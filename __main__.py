import argparse
import sys
import os
from . import words as words_module
from . import stats as stats_module
from .game import Game
from .display import render_grid, render_keyboard, render_share


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


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
            print(f"{err}\n")
            continue
        game.submit(raw)

    print(render_grid(game))
    if game.guesses:
        print()
        print(render_keyboard(game))
    print()

    if game.is_won:
        print(f"Победа! Слово: {game.secret.upper()}")
    else:
        print(f"Поражение. Слово было: {game.secret.upper()}")
    print()
    print(render_share(game))
    return game


def main(argv=None):
    parser = argparse.ArgumentParser(prog="wordle", description="Wordle в терминале")
    parser.add_argument("--daily", action="store_true", help="Слово дня")
    parser.add_argument("--random", action="store_true", help="Случайное слово (по умолчанию)")
    parser.add_argument("--stats", action="store_true", help="Показать статистику и выйти")
    parser.add_argument("--word", help="Задать слово вручную (для тестов)")
    args = parser.parse_args(argv)

    all_words = words_module.load_words()

    if args.stats:
        print(stats_module.render_stats(stats_module.load_stats()))
        return 0

    if args.word:
        secret = args.word.lower()
        if len(secret) != 5:
            print("Слово должно быть из 5 букв", file=sys.stderr)
            return 1
    elif args.daily:
        secret = words_module.get_daily_word(all_words)
    else:
        secret = words_module.get_random_word(all_words)

    game = Game(secret)
    result = play_game(game)

    if result is None:
        print("Игра прервана.")
        return 0

    stats_module.record_game(game)
    print()
    print(stats_module.render_stats(stats_module.load_stats()))
    return 0 if game.is_won else 1


if __name__ == "__main__":
    sys.exit(main())
