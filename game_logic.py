import random

class HitAndBlowLogic:
    def __init__(self, digits=4):
        self.digits = digits
        self.secret = self._generate_secret()

    def _generate_secret(self):
        """0-9の数字から重複なしで digits 個選んで正解リストを作成する"""
        numbers = list(range(10))
        return random.sample(numbers, self.digits)

    def judge(self, guess_list):
        """
        予想を受け取り、HitとBlowを判定して返す (自身のsecretを使用)
        """
        return self.judge_with_secret(guess_list, self.secret)

    def judge_with_secret(self, guess_list, secret_list):
        """
        指定された正解(secret_list)に対する判定(Hit, Blow)を返す
        """
        hit = 0
        blow = 0
        
        for i, g in enumerate(guess_list):
            if g == secret_list[i]:
                hit += 1
            elif g in secret_list:
                blow += 1
        return hit, blow

    def validate_guess(self, guess_str):
        """
        入力文字列を検証する
        returns: (is_valid, error_message, parsed_list)
        """
        # 数字チェック
        if not guess_str.isdigit():
            return False, "数字のみを入力してください。", []
        
        # 桁数チェック
        if len(guess_str) != self.digits:
            return False, f"{self.digits}桁の数字を入力してください。", []
        
        # リストに変換
        guess_list = [int(x) for x in guess_str]
        
        # 重複チェック
        if len(set(guess_list)) != len(guess_list):
            return False, "同じ数字を複数回使用することはできません。", []
            
        return True, "", guess_list

    def get_secret_str(self):
        """正解を文字列で返す（デバッグや終了時用）"""
        return ''.join(map(str, self.secret))
