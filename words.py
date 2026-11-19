import random
from datetime import date
from pathlib import Path

WORDS_FILE = Path(__file__).parent / "words.txt"
_LAUNCH_DATE = date(2024, 1, 1)


def load_words():
    if not WORDS_FILE.exists():
        raise FileNotFoundError(f"Не найден словарь: {WORDS_FILE}")
    with open(WORDS_FILE, encoding="utf-8") as f:
        words = [line.strip().lower() for line in f if line.strip()]
    return [w for w in words if len(w) == 5]


def get_random_word(words):
    return random.choice(words)


def get_daily_word(words):
    today = date.today()
    delta = (today - _LAUNCH_DATE).days
    return words[delta % len(words)]
