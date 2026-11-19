import os
import sys

if os.name == "nt":
    os.system("")

GREEN = "\033[42m\033[30m"
YELLOW = "\033[43m\033[30m"
GREY = "\033[100m\033[97m"
RESET = "\033[0m"

STATUS_COLOR = {"correct": GREEN, "present": YELLOW, "absent": GREY}
PRIORITY = {"absent": 0, "present": 1, "correct": 2}

KEYBOARD_ROWS = ["йцукенгшщзхъ", "фывапролджэ", "ячсмитьбю"]


def render_cell(letter, status):
    if status is None:
        return "|   |"
    color = STATUS_COLOR[status]
    return f"|{color}\u00A0{letter.upper()}\u00A0{RESET}|"

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

def render_share(game):
    lines = [f"Wordle {len(game.guesses)}/{game.max_attempts}"]
    emoji = {"correct": "G", "present": "Y", "absent": "B"}
    for _, statuses in game.guesses:
        lines.append("".join(emoji[s] for s in statuses))
    return "\n".join(lines)
