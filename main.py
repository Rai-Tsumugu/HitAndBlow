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

def main():
    # 設定
    DIGITS = 4
    
    print(f"=== Hit and Blow ===")
    print("モードを選択してください:")
    print("1: PvP (人間 vs 人間) - 共通の正解を奪い合う")
    print("2: PvAI (人間 vs AI) - 共通の正解を奪い合う")
    
    mode = input("選択 > ")
    while mode not in ["1", "2"]:
        mode = input("1 か 2 を入力してください > ")
    
    is_vs_ai = (mode == "2")
    
    # 判定機能のインスタンス化
    logic = HitAndBlowLogic(digits=DIGITS)
    # AIのインスタンス化 (PvAIの場合)
    ai_solver = HitAndBlowSolver(digits=DIGITS) if is_vs_ai else None

    print("\n---------------------------------")
    print(f"ゲーム開始！ 共通の正解（{DIGITS}桁）を先に当てた方が勝ちです。")
    print("---------------------------------")

    players = ["Player 1", "Player 2 (AI)" if is_vs_ai else "Player 2"]
    turn_count = 1
    game_over = False
    
    # メインゲームループ
    while not game_over:
        current_player_idx = (turn_count - 1) % 2
        current_player_name = players[current_player_idx]
        
        print(f"\n--- Turn {turn_count} ({current_player_name}) ---")
        
        guess = []
        
        # --- AIのターン ---
        if is_vs_ai and current_player_idx == 1:
            print("AI思考中...", end="", flush=True)
            start_time = time.time()
            guess = ai_solver.suggest_move()
            elapsed = time.time() - start_time
            print(f" 完了 ({elapsed:.2f}s)")
            
            guess_str = ''.join(map(str, guess))
            print(f"[{current_player_name}] 予想: {guess_str}")

        # --- 人間のターン ---
        else:
            guess = get_player_input(current_player_name, logic)
        
        # 判定
        hit, blow = logic.judge(guess)
        guess_str = ''.join(map(str, guess))
        
        print(f"判定結果: {guess_str} -> [ Hit: {hit}, Blow: {blow} ]")
        
        # AIに情報を共有する (自分自身のターンも含めて、場の情報は全て学習する)
        if is_vs_ai:
            ai_solver.update(guess, hit, blow)
            if current_player_idx == 0:
                print(f"  (AIもこの結果を見て候補を絞り込みました)")

        # 勝利判定
        if hit == DIGITS:
            print("\n" + "="*40)
            print(f"勝者: {current_player_name} !!")
            print(f"正解: {logic.get_secret_str()}")
            print("="*40)
            game_over = True
        
        turn_count += 1

if __name__ == "__main__":
    main()
