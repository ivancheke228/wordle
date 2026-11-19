CORRECT = "correct"
PRESENT = "present"
ABSENT = "absent"


class Game:
    def __init__(self, secret, max_attempts=6):
        self.secret = secret.lower()
        self.max_attempts = max_attempts
        self.guesses = []

    def is_valid_guess(self, guess):
        if len(guess) != 5:
            return False, "Слово должно быть из 5 букв"
        if not all("а" <= c <= "я" or c == "ё" for c in guess):
            return False, "Только русские буквы"
        return True, ""

    def submit(self, guess):
        guess = guess.lower()
        statuses = self._check(guess)
        self.guesses.append((guess, statuses))
        return statuses

    def _check(self, guess):
        statuses = [ABSENT] * 5
        remaining = list(self.secret)

        for i in range(5):
            if guess[i] == remaining[i]:
                statuses[i] = CORRECT
                remaining[i] = None

        for i in range(5):
            if statuses[i] == CORRECT:
                continue
            if guess[i] in remaining:
                statuses[i] = PRESENT
                remaining[remaining.index(guess[i])] = None

        return statuses

    @property
    def is_won(self):
        return bool(self.guesses) and self.guesses[-1][0] == self.secret

    @property
    def is_lost(self):
        return len(self.guesses) >= self.max_attempts and not self.is_won

    @property
    def is_over(self):
        return self.is_won or self.is_lost
