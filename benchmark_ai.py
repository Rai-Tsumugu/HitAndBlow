from game_logic import HitAndBlowLogic
from solver import HitAndBlowSolver
import time
import random

def run_benchmark(iterations=10):
    print(f"Running benchmark with {iterations} games...")
    print("AI Strategy: Entropy Maximization (Strongest)")

    total_turns = 0
    max_turns = 0
    
    # 統計情報: ターンごとの平均残候補数
    # remaining_counts[turn_index] = list of remaining candidate counts
    remaining_counts_history = {} 

    digits = 4
    
    start_time = time.time()
    
    for i in range(iterations):
        # 毎回新しいゲーム
        logic = HitAndBlowLogic(digits=digits)
        solver = HitAndBlowSolver(digits=digits)
        secret = logic.secret
        
        turn = 1
        solved = False
        
        # print(f"Game {i+1}: Secret = {secret}")
        
        while not solved:
            # AIの手
            guess = solver.suggest_move()
            
            # 判定
            hit, blow = logic.judge_with_secret(guess, secret)
            
            # AI更新
            solver.update(guess, hit, blow)
            remaining = len(solver.candidates)
            
            # 統計記録
            if turn not in remaining_counts_history:
                remaining_counts_history[turn] = []
            remaining_counts_history[turn].append(remaining)
            
            if hit == digits:
                solved = True
                total_turns += turn
                if turn > max_turns:
                    max_turns = turn
                # print(f"  Solved in {turn} turns")
            else:
                turn += 1
        
        # 進捗表示
        if (i+1) % 10 == 0:
            print(f"  Processed {i+1}/{iterations} games...")

    elapsed = time.time() - start_time
    avg_turns = total_turns / iterations
    
    print("\n=== Benchmark Results ===")
    print(f"Games Played: {iterations}")
    print(f"Average Turns: {avg_turns:.2f}")
    print(f"Max Turns: {max_turns}")
    print(f"Total Time: {elapsed:.2f}s ({elapsed/iterations:.2f}s/game)")
    
    print("\n--- Candidate Reduction Stats ---")
    print(f"Avg Candidates after each turn:")
    sorted_turns = sorted(remaining_counts_history.keys())
    for t in sorted_turns:
        counts = remaining_counts_history[t]
        avg_rem = sum(counts) / len(counts)
        print(f"  Turn {t}: {avg_rem:.1f} candidates remaining")

if __name__ == "__main__":
    # 実際の全探索は重いので、ベンチマークは10〜20回程度で行う
    run_benchmark(iterations=20)
