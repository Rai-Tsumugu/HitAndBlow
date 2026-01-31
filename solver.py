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
        print(f"  [AI] 候補数: {len(self.candidates)}")

    def suggest_move(self):
        """
        期待情報量（エントロピー）が最大になる手を提案する
        """
        # 1. 候補が1つならそれを答える
        if len(self.candidates) == 1:
            return self.candidates[0]
        
        # 2. 初手は計算コスト削減のため固定
        if len(self.candidates) == len(self.all_permutations):
            return self.first_guess

        best_guess = None
        max_entropy = -1.0
        
        # 3. 全通りの推測パターンについてシミュレーションを行う
        #    (通常、残りの候補から選ぶより、全順列から選んだほうが情報量が高い場合があるが、
        #     計算量削減のため候補数が多いときは「候補集合」から、
        #     少なくなってきたら「全集合」から選ぶなりの工夫が可能。
        #     ここでは最強を目指すため、常に「全集合」から探索するが、
        #     速度が遅すぎる場合は候補集合のみにする)
        
        # 探索範囲の設定
        # 候補が多いときは処理時間を短縮するために候補内から選ぶ (ヒューリスティック)
        # 厳密な最強ではないが、実用的な速度を重視
        search_space = self.all_permutations if len(self.candidates) <= 200 else self.candidates
        
        for guess in search_space:
            # このguessをした時の、結果の分布を調べる
            outcome_counts = {}
            for secret_candidate in self.candidates:
                h, b = self.logic.judge_with_secret(guess, secret_candidate)
                outcome = (h, b)
                outcome_counts[outcome] = outcome_counts.get(outcome, 0) + 1
            
            # エントロピー計算
            # E = - sum( p * log2(p) )
            entropy = 0.0
            total = len(self.candidates)
            for count in outcome_counts.values():
                p = count / total
                entropy -= p * math.log2(p)
            
            # 最大エントロピーを更新
            # エントロピーが同じなら、それが候補に含まれている手（自分自身が正解の可能性がある手）を優先する
            if entropy > max_entropy:
                max_entropy = entropy
                best_guess = guess
            elif entropy == max_entropy:
                if best_guess not in self.candidates and guess in self.candidates:
                    best_guess = guess
        
        return best_guess

