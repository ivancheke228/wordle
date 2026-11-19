import json
from datetime import date, timedelta
from pathlib import Path

STATS_FILE = Path(__file__).parent / "wordle_stats.json"


def _empty():
    return {
        "played": 0,
        "wins": 0,
        "current_streak": 0,
        "max_streak": 0,
        "last_won_date": None,
        "distribution": {str(i): 0 for i in range(1, 7)},
    }


def load_stats():
    if not STATS_FILE.exists():
        return _empty()
    try:
        with open(STATS_FILE, encoding="utf-8") as f:
            data = json.load(f)
        base = _empty()
        base.update(data)
        return base
    except (json.JSONDecodeError, OSError):
        return _empty()


def save_stats(stats):
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)


def record_game(game):
    stats = load_stats()
    stats["played"] += 1

    if game.is_won:
        stats["wins"] += 1
        attempts = len(game.guesses)
        stats["distribution"][str(attempts)] = (
            stats["distribution"].get(str(attempts), 0) + 1
        )

        today = str(date.today())
        if stats["last_won_date"] == today:
            pass
        else:
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
