from game_logic import HitAndBlowLogic
from solver import HitAndBlowSolver
import time

def get_player_input(player_name, logic):
    """
    プレイヤーからの入力を受け付け、バリデーションを行う関数
    """
    while True:
        try:
            user_input = input(f"[{player_name}] 予想を入力してください (例: 0123) > ")
            
            # ロジッククラスを使ってバリデーション
            is_valid, error_msg, guess_list = logic.validate_guess(user_input)
            
            if is_valid:
                return guess_list
            else:
                print(f"エラー: {error_msg}")
        except KeyboardInterrupt:
            print("\nゲームを中断します。")
            exit()
        except Exception as e:
            print(f"予期せぬエラーが発生しました: {e}")

def play_match(p1_is_ai, p2_is_ai, digits=4, verbose=True):
    """
    1試合を行う関数
    Returns: winner_index (0 for P1, 1 for P2), turns_taken
    """
    logic = HitAndBlowLogic(digits=digits)
    
    # ソルバーの初期化
    solvers = [None, None]
    if p1_is_ai:
        solvers[0] = HitAndBlowSolver(digits=digits)
    if p2_is_ai:
        solvers[1] = HitAndBlowSolver(digits=digits)

    players = ["Player 1" + (" (AI)" if p1_is_ai else ""), 
               "Player 2" + (" (AI)" if p2_is_ai else "")]
    
    turn_count = 1
    game_over = False
    
    if verbose:
        print("\n---------------------------------")
        print(f"ゲーム開始！ 共通の正解（{digits}桁）を先に当てた方が勝ちです。")
        print("---------------------------------")

    history = []

    while not game_over:
        current_player_idx = (turn_count - 1) % 2
        current_player_name = players[current_player_idx]
        is_ai_turn = (current_player_idx == 0 and p1_is_ai) or (current_player_idx == 1 and p2_is_ai)
        
        if verbose:
            print(f"\n--- Turn {turn_count} ({current_player_name}) ---")
            # 履歴の表示
            if history:
                print("HISTORY:")
                for entry in history:
                    print(entry)
                print("-" * 20)
        
        guess = []
        
        # --- AIのターン ---
        if is_ai_turn:
            solver = solvers[current_player_idx]
            if verbose: print(f"AI思考中...", end="", flush=True)
            
            # 進捗表示用のコールバック
            def progress_reporter(current, total):
                if verbose:
                    # \r で行頭に戻って上書き
                    print(f"\rAI思考中... {current}/{total}", end="", flush=True)

            guess = solver.suggest_move(on_progress=progress_reporter)
            
            if verbose: print(f"\rAI思考中... 完了           ") # 行をクリア
            
            if verbose:
                guess_str = ''.join(map(str, guess))
                print(f"[{current_player_name}] 予想: {guess_str}")

        # --- 人間のターン ---
        else:
            guess = get_player_input(current_player_name, logic)
        
        # 判定
        hit, blow = logic.judge(guess)
        
        guess_str = ''.join(map(str, guess))
        result_str = f"[{guess_str} Hit: {hit}, Blow: {blow}]"
        history.append(result_str)
        
        if verbose:
            print(f"判定結果: {result_str}")
        
        # 全員（AI含む）に情報を共有
        if solvers[0]: solvers[0].update(guess, hit, blow)
        if solvers[1]: solvers[1].update(guess, hit, blow)

        # 勝利判定
        if hit == digits:
            if verbose:
                print("\n" + "="*40)
                print(f"勝者: {current_player_name} !!")
                print(f"正解: {logic.get_secret_str()}")
                print("="*40)
            return current_player_idx, turn_count
        
        turn_count += 1

def main():
    # 設定
    DIGITS = 4
    
    print(f"=== Hit and Blow ===")
    print("モードを選択してください:")
    print("1: PvP (人間 vs 人間)")
    print("2: PvAI (人間 vs AI)")
    print("3: AI vs AI (Battle Mode - 指定回数対戦)")
    
    mode = input("選択 > ")
    while mode not in ["1", "2", "3"]:
        mode = input("1, 2, 3 のいずれかを入力してください > ")
    
    if mode == "1":
        play_match(p1_is_ai=False, p2_is_ai=False, digits=DIGITS)
    elif mode == "2":
        play_match(p1_is_ai=False, p2_is_ai=True, digits=DIGITS)
    elif mode == "3":
        try:
            games_str = input("対戦回数を入力してください (Default: 100) > ")
            games = int(games_str) if games_str.strip() else 100
        except ValueError:
            games = 100
            print("数値を認識できなかったため、100回行います。")

        print(f"\nAI vs AI Battle Start! ({games} games)")
        
        p1_wins = 0
        p2_wins = 0
        total_turns = 0
        
        start_time = time.time()
        
        for i in range(games):
            winner, turns = play_match(p1_is_ai=True, p2_is_ai=True, digits=DIGITS, verbose=False)
            if winner == 0:
                p1_wins += 1
            else:
                p2_wins += 1
            total_turns += turns
            
            print(".", end="", flush=True)
            if (i+1) % 50 == 0:
                print(f" {i+1}/{games}")
                
        elapsed = time.time() - start_time
        
        print("\n=== Battle Results ===")
        print(f"Total Games: {games}")
        print(f"Player 1 (AI) Wins: {p1_wins} ({p1_wins/games*100:.1f}%)")
        print(f"Player 2 (AI) Wins: {p2_wins} ({p2_wins/games*100:.1f}%)")
        print(f"Average Turns: {total_turns/games:.2f}")
        print(f"Time Taken: {elapsed:.2f}s")

if __name__ == "__main__":
    main()
