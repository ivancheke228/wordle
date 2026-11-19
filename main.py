import os
import sys
import json
import random
import argparse
from datetime import date, timedelta
from pathlib import Path

# ==========================================
# 1. ЦВЕТА И ОТРИСОВКА
# ==========================================
if os.name == "nt":
    os.system("")  # Включаем ANSI-цвета для Windows

GREEN = "\033[42m\033[30m"
YELLOW = "\033[43m\033[30m"
GREY = "\033[100m\033[97m"
RESET = "\033[0m"

STATUS_COLOR = {"correct": GREEN, "present": YELLOW, "absent": GREY}
PRIORITY = {"absent": 0, "present": 1, "correct": 2}
KEYBOARD_ROWS = ["йцукенгшщзхъ", "фывапролджэ", "ячсмитьбю"]

CORRECT = "correct"
PRESENT = "present"
ABSENT = "absent"


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def render_cell(letter, status):
    if status is None:
        return "|   |"
    color = STATUS_COLOR[status]
    return f"|{color}\u00A0{letter.upper()}\u00A0{RESET}|"


def render_grid(game):
    lines = []
    for i in range(game.max_attempts):
        if i < len(game.guesses):
            word, statuses = game.guesses[i]
            cells = [render_cell(c, s) for c, s in zip(word, statuses)]
        else:
            cells = ["|   |"] * 5
        lines.append("".join(cells))
    return "\n".join(lines)


def render_keyboard(game):
    letter_status = {}
    for word, statuses in game.guesses:
        for letter, status in zip(word, statuses):
            cur = letter_status.get(letter)
            if cur is None or PRIORITY[status] > PRIORITY[cur]:
                letter_status[letter] = status

    lines = []
    for row in KEYBOARD_ROWS:
        parts = []
        for letter in row:
            status = letter_status.get(letter)
            if status is None:
                parts.append(f"{letter.upper()}\u00A0")
            else:
                parts.append(f"{STATUS_COLOR[status]}{letter.upper()}{RESET}\u00A0")
        lines.append("".join(parts))
    return "\n".join(lines)


def render_share(game):
    lines = [f"Wordle {len(game.guesses)}/{game.max_attempts}"]
    emoji = {"correct": "🟩", "present": "🟨", "absent": "⬛"}
    for _, statuses in game.guesses:
        lines.append("".join(emoji[s] for s in statuses))
    return "\n".join(lines)


# ==========================================
# 2. ЛОГИКА ИГРЫ
# ==========================================
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


# ==========================================
# 3. СТАТИСТИКА
# ==========================================
STATS_FILE = Path(__file__).parent / "wordle_stats.json"


def _empty_stats():
    return {
        "played": 0, "wins": 0, "current_streak": 0,
        "max_streak": 0, "last_won_date": None,
        "distribution": {str(i): 0 for i in range(1, 7)},
    }


def load_stats():
    if not STATS_FILE.exists():
        return _empty_stats()
    try:
        with open(STATS_FILE, encoding="utf-8") as f:
            data = json.load(f)
        base = _empty_stats()
        base.update(data)
        return base
    except (json.JSONDecodeError, OSError):
        return _empty_stats()


def save_stats(stats):
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)


def record_game(game):
    stats = load_stats()
    stats["played"] += 1

    if game.is_won:
        stats["wins"] += 1
        attempts = len(game.guesses)
        stats["distribution"][str(attempts)] = stats["distribution"].get(str(attempts), 0) + 1

        today = str(date.today())
        if stats["last_won_date"] != today:
            yesterday = str(date.today() - timedelta(days=1))
            if stats["last_won_date"] == yesterday:
                stats["current_streak"] += 1
            else:
                stats["current_streak"] = 1
            stats["last_won_date"] = today
            stats["max_streak"] = max(stats["max_streak"], stats["current_streak"])
    else:
        stats["current_streak"] = 0

    save_stats(stats)
    return stats


def render_stats(stats):
    lines = [
        f"Сыграно:        {stats['played']}",
        f"Побед:          {stats['wins']}",
    ]
    if stats["played"]:
        pct = stats["wins"] / stats["played"] * 100
        lines.append(f"Процент побед:  {pct:.1f}%")
    lines.append(f"Текущая серия:  {stats['current_streak']}")
    lines.append(f"Лучшая серия:   {stats['max_streak']}")
    lines.append("")
    lines.append("Распределение попыток:")
    for i in range(1, 7):
        count = stats["distribution"].get(str(i), 0)
        bar = "█" * count
        lines.append(f"  {i}: {bar} {count}")
    return "\n".join(lines)


# ==========================================
# 4. ГЛАВНЫЙ ЦИКЛ И CLI
# ==========================================
def show_banner():
    print("=" * 44)
    print("   W O R D L E   —   угадай слово из 5 букв")
    print("=" * 44)
    print("Зелёный — буква на месте")
    print("Жёлтый  — буква есть, но не там")
    print("Серый   — буквы нет в слове")
    print("Введи 'выход' чтобы сдаться.")
    print()


def play_game(game):
    clear_screen()
    show_banner()
    while not game.is_over:
        print(render_grid(game))
        if game.guesses:
            print()
            print(render_keyboard(game))
        print()
        try:
            raw = input("> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return None
        if raw in ("выход", "exit", "quit", "q"):
            return None

        ok, err = game.is_valid_guess(raw)
        clear_screen()
        if not ok:
            print(f"⚠ {err}\n")
            continue
        game.submit(raw)

    print(render_grid(game))
    if game.guesses:
        print()
        print(render_keyboard(game))
    print()

    if game.is_won:
        print(f"🎉 Победа! Слово: {game.secret.upper()}")
    else:
        print(f"💀 Поражение. Слово было: {game.secret.upper()}")
    print()
    print(render_share(game))
    return game


def main():
    parser = argparse.ArgumentParser(prog="wordle", description="Wordle в терминале")
    parser.add_argument("--daily", action="store_true", help="Слово дня")
    parser.add_argument("--stats", action="store_true", help="Показать статистику и выйти")
    parser.add_argument("--word", help="Задать слово вручную (для тестов)")
    args = parser.parse_args()

    WORDS_FILE = Path(__file__).parent / "words.txt"
    
    if args.stats:
        print(render_stats(load_stats()))
        return 0

    if not WORDS_FILE.exists():
        print(f"Ошибка: не найден файл {WORDS_FILE}")
        return 1
        
    with open(WORDS_FILE, encoding="utf-8") as f:
        all_words = [w.strip().lower() for w in f if len(w.strip()) == 5]

    if not all_words:
        print("Ошибка: словарь пуст или в нем нет слов из 5 букв!")
        return 1

    if args.word:
        secret = args.word.lower()
    elif args.daily:
        delta = (date.today() - date(2024, 1, 1)).days
        secret = all_words[delta % len(all_words)]
    else:
        secret = random.choice(all_words)

    game = Game(secret)
    result = play_game(game)

    if result is None:
        print("Игра прервана.")
        return 0

    record_game(game)
    print()
    print(render_stats(load_stats()))
    return 0 if game.is_won else 1


if __name__ == "__main__":
    sys.exit(main())