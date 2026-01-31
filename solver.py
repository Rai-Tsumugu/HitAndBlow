import itertools
import math
from game_logic import HitAndBlowLogic

class HitAndBlowSolver:
    def __init__(self, digits=4):
        self.digits = digits
        self.logic = HitAndBlowLogic(digits)
        # 全候補の生成 (例: 4桁なら 5040通り)
        self.all_permutations = list(itertools.permutations(range(10), digits))
        self.all_permutations = [list(p) for p in self.all_permutations]
        
        # 現在の候補リスト（初期状態は全候補）
        self.candidates = self.all_permutations.copy()
        
        # 初手の計算は重いので、キャッシュしておく (4桁の場合)
        # 計算結果に基づく最強の初手のひとつ (0, 1, 2, 3)
        self.first_guess = [0, 1, 2, 3]

    def reset(self):
        """ゲームごとにリセット"""
        self.candidates = self.all_permutations.copy()

    def update(self, guess, hit, blow):
        """
        前回の推測(guess)と結果(hit, blow)を受け取り、
        候補リストを絞り込む
        """
        new_candidates = []
        for c in self.candidates:
            # もしこの候補 c が正解だった場合、
            # guess に対する判定は (hit, blow) になるはずである
            # ならないものは候補から外す
            h, b = self.logic.judge_with_secret(guess, c)
            if h == hit and b == blow:
                new_candidates.append(c)
        
        self.candidates = new_candidates
        # print(f"  [AI] 候補数: {len(self.candidates)}")

    def suggest_move(self, on_progress=None):
        """
        現在の候補数に応じて戦略を切り替える
        - 候補が多いとき: エントロピー最大化（情報収集優先）
        - 候補が少ないとき: 勝率最大化（Minimax / 相手へのアシスト回避）
        """
        N = len(self.candidates)
        
        # 1. 確定しているならそれを答える
        if N == 1:
            return self.candidates[0]
        
        # 2. 初手固定
        if N == len(self.all_permutations):
            return self.first_guess

        # 3. 戦略の切り替え
        # 候補数が50以下なら、厳密な勝率計算を行う (Minimax)
        if N <= 50:
            return self.suggest_move_minimax(N, on_progress)
        else:
            return self.suggest_move_entropy(N, on_progress)

    def suggest_move_entropy(self, N, on_progress=None):
        """エントロピー最大化戦略 (従来のロジック)"""
        best_guess = None
        max_entropy = -1.0
        
        # 候補が多いときは検索空間を間引くなどの最適化が可能だが、
        # ここでは候補が十分減っている(<=200)なら全探索、そうでなければ候補内探索とする
        search_space = self.all_permutations if len(self.candidates) <= 200 else self.candidates
        total_steps = len(search_space)
        
        # judgeロジックをローカル変数に展開して高速化
        candidates = self.candidates
        
        for i, guess in enumerate(search_space):
            if on_progress and i % 100 == 0:
                on_progress(i, total_steps)

            outcome_counts = {}
            for secret_candidate in candidates:
                # judge_with_secret のインライン化
                hit = 0
                blow = 0
                for j in range(self.digits):
                    g = guess[j]
                    if g == secret_candidate[j]:
                        hit += 1
                    elif g in secret_candidate:
                        blow += 1
                
                outcome = (hit, blow)
                if outcome in outcome_counts:
                    outcome_counts[outcome] += 1
                else:
                    outcome_counts[outcome] = 1
            
            entropy = 0.0
            for count in outcome_counts.values():
                p = count / N
                entropy -= p * math.log2(p)
            
            if entropy > max_entropy:
                max_entropy = entropy
                best_guess = guess
            elif entropy == max_entropy:
                if best_guess not in self.candidates and guess in self.candidates:
                    best_guess = guess
        
        return best_guess

    def suggest_move_minimax(self, N, on_progress=None):
        """勝率最大化戦略 (Minimax) - 高速化版"""
        best_guess = None
        max_score = -1.0
        
        search_space = self.all_permutations
        total_steps = len(search_space)
        candidates = self.candidates
        
        for i, guess in enumerate(search_space):
            if on_progress and i % 50 == 0:
                on_progress(i, total_steps)

            outcome_counts = {}
            # インライン化したジャッジロジック
            for secret_candidate in candidates:
                hit = 0
                blow = 0
                for j in range(self.digits):
                    g = guess[j]
                    if g == secret_candidate[j]:
                        hit += 1
                    elif g in secret_candidate:
                        blow += 1
                        
                outcome = (hit, blow)
                if outcome in outcome_counts:
                    outcome_counts[outcome] += 1
                else:
                    outcome_counts[outcome] = 1
            
            # スコア計算
            p_immediate_win = (1.0 / N) if guess in self.candidates else 0.0
            p_survive_next = 0.0
            
            for count in outcome_counts.values():
                prob_outcome = count / N
                # _estimate_win_rate のインライン展開 (呼び出しコスト削減)
                # k = count
                if count > 0:
                    opponent_win_rate = ((count + 1) // 2) / count
                else:
                    opponent_win_rate = 0
                
                p_survive_next += prob_outcome * (1.0 - opponent_win_rate)
            
            total_score = p_immediate_win + p_survive_next
            
            if total_score > max_score:
                max_score = total_score
                best_guess = guess
            elif total_score == max_score:
                if best_guess not in self.candidates and guess in self.candidates:
                    best_guess = guess
                    
        return best_guess

    def _estimate_win_rate(self, k):
        """
        残り候補数 k のときの、手番プレイヤーの勝率（概算）
        k=1 -> 1.0 (必勝)
        k=2 -> 0.5 (1/2で当たり、外れたら相手必勝)
        k=3 -> 0.66 (1/3で当たり、2/3で相手が残り2(0.5)→自分は0.5勝てる) 
           -> 1/3 + 2/3 * 0.5 = 2/3
        一般項: int((k+1)/2) / k
           k=odd(2m+1) -> (m+1)/(2m+1) ~ 0.5
           k=even(2m)  -> m/2m = 0.5
        """
        if k <= 0: return 0
        return math.floor((k + 1) / 2) / k

