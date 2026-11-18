"""Count how many times each suggestion strategy was accepted.

The final choice (1=random, 2=smart, 3=popularity, 4=llm) is credited to the chosen
suggestion and to every other suggestion that proposed the same value.
"""

import argparse
import sqlite3
from pathlib import Path

# When True, dialogues whose chosen suggestion is "no_action" are ignored.
SKIP_NO_ACTION = True
NO_ACTION = "no_action"

COLUMNS = {
    1: "random_suggestion",
    2: "smart_suggestion",
    3: "popularity_suggestion",
    4: "llm_suggestion",
}


def count_acceptances(db_path: Path) -> tuple[dict[str, int], int]:
    scores = {name: 0 for name in COLUMNS.values()}
    answered = 0
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            f"SELECT {', '.join(COLUMNS.values())}, choice "
            "FROM dialogues WHERE choice IS NOT NULL AND choice != ''"
        ).fetchall()
    for row in rows:
        try:
            chosen = COLUMNS[int(row["choice"])]
        except (ValueError, KeyError):
            continue
        # The LLM only takes part when it produced a suggestion for this dialogue.
        by_name = {n: row[n] for n in COLUMNS.values() if row[n] is not None}
        if chosen not in by_name:
            continue
        if SKIP_NO_ACTION and by_name[chosen] == NO_ACTION:
            continue
        answered += 1
        for name, value in by_name.items():
            if value == by_name[chosen]:
                scores[name] += 1
    return scores, answered


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("db", type=Path, help="path to the SQLite database")
    args = parser.parse_args()

    scores, answered = count_acceptances(args.db)
    print(f"Dialogues with a choice: {answered}")
    for name, score in scores.items():
        if name == "llm_suggestion" and not score:
            continue
        pct = 100 * score / answered if answered else 0
        print(f"{name:<22} {score:>5}  ({pct:.1f}%)")


if __name__ == "__main__":
    main()
