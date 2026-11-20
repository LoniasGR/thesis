"""Create a separate human-evaluation database from completed LLM comparisons.

Usage:
    python create_human_sample.py with_llm.db --limit 100
"""

import argparse
import random
import sqlite3
from pathlib import Path

from sqlalchemy import delete
from sqlalchemy.orm import Session

from db.database import human_evaluation_engine
from db.models import Base, HumanDialogueSampleDB


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="completed with-LLM SQLite database")
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--include-no-action",
        action="store_true",
        help="keep examples where the LLM selected no_action",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with sqlite3.connect(args.source) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            """
            SELECT
                uuid, dialogue, random_suggestion, smart_suggestion,
                popularity_suggestion, llm_suggestion, choice, choice_reason
            FROM dialogues
            WHERE choice IS NOT NULL
              AND choice != ''
              AND llm_suggestion IS NOT NULL
            """
        ).fetchall()

    columns = {
        "1": "random_suggestion",
        "2": "smart_suggestion",
        "3": "popularity_suggestion",
        "4": "llm_suggestion",
    }
    candidates = []
    for row in rows:
        chosen_column = columns.get(str(row["choice"]))
        if chosen_column is None:
            continue
        if not args.include_no_action and row[chosen_column] == "no_action":
            continue
        candidates.append(row)

    random.Random(args.seed).shuffle(candidates)
    selected = candidates[: args.limit]
    Base.metadata.create_all(human_evaluation_engine)
    with Session(human_evaluation_engine) as session:
        session.execute(delete(HumanDialogueSampleDB))
        session.add_all(
            HumanDialogueSampleDB(
                dialogue_uuid=row["uuid"],
                source_database=args.source.name,
                dialogue=row["dialogue"],
                random_suggestion=row["random_suggestion"],
                smart_suggestion=row["smart_suggestion"],
                popularity_suggestion=row["popularity_suggestion"],
                llm_suggestion=row["llm_suggestion"],
                llm_choice=row["choice"],
                llm_choice_reason=row["choice_reason"],
            )
            for row in selected
        )
        session.commit()

    print(
        f"Selected {len(selected)} of {len(candidates)} eligible "
        f"dialogues into human_evaluation.db"
    )


if __name__ == "__main__":
    main()
