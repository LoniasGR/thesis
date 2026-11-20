"""Generate VW ADF data from the human-feedback SQLite database.

Usage:
    python format_human_feedback.py

Full example:
    python format_human_feedback.py \
        --database production.db \
        --output applications/mock_dialogues_service/new_data.dat

Each answered evaluation becomes one uniformly sampled contextual-bandit
example. Human feedback is formatted for independent evaluation; it is not
added to historical production training data.
"""

import argparse
import json
import sqlite3
from pathlib import Path

from applications.mock_dialogues_service.app.common.helpers import (
    generate_remaining_suggestions,
    remove_useless_intents,
)
from applications.mock_dialogues_service.app.common.mappings import (
    intent_to_functionality_dict,
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Convert answered synthetic-dialogue feedback to VW ADF data."
    )
    parser.add_argument(
        "--database",
        type=Path,
        default=Path("production.db"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("applications/mock_dialogues_service/new_data.dat"),
    )
    return parser.parse_args()


def load_answered_evaluations(database: Path):
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    try:
        rows = connection.execute(
            """
            SELECT
                e.uuid,
                e.suggestion,
                e.answer,
                u.intent,
                eu."order"
            FROM evaluations AS e
            JOIN evaluation_user_dialogue_table AS eu
              ON eu.evaluation_id = e.uuid
            JOIN user_dialogues AS u
              ON u.id = eu.user_dialogue_id
            WHERE e.answer IS NOT NULL
            ORDER BY e.uuid, eu."order"
            """
        ).fetchall()
    finally:
        connection.close()

    evaluations = {}
    for row in rows:
        evaluation = evaluations.setdefault(
            row["uuid"],
            {
                "uuid": row["uuid"],
                "suggestion": row["suggestion"],
                "answer": bool(row["answer"]),
                "intents": [],
            },
        )
        evaluation["intents"].append(row["intent"])
    return list(evaluations.values())


def format_evaluation(evaluation: dict) -> str:
    intents = evaluation["intents"]
    functionalities = [
        intent_to_functionality_dict[intent] for intent in intents
    ]
    remaining_suggestions = generate_remaining_suggestions(functionalities)
    suggestion = evaluation["suggestion"]
    if suggestion not in remaining_suggestions:
        raise ValueError(
            f"Evaluation {evaluation['uuid']}: suggested action "
            f"{suggestion!r} is outside the reconstructed candidate set"
        )

    actions = [suggestion] + [
        action for action in remaining_suggestions if action != suggestion
    ]
    probability = 1.0 / len(actions)
    cost = 0.0 if evaluation["answer"] else 1.0
    context = remove_useless_intents(intents)
    lines = [
        f"shared |S {' '.join(context)}",
        f"0:{cost}:{probability} |A action={suggestion}",
        *(f"|A action={action}" for action in actions[1:]),
    ]
    return "\n".join(lines) + "\n"


def main():
    args = parse_args()
    evaluations = load_answered_evaluations(args.database)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "\n".join(format_evaluation(evaluation) for evaluation in evaluations)
    )
    print(
        json.dumps(
            {
                "database": str(args.database),
                "output": str(args.output),
                "answered_evaluations": len(evaluations),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
