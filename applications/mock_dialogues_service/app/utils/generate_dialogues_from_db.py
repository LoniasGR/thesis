from io import TextIOWrapper
import os

os.environ["DB_URL"] = "sqlite:///./production.db"

from db.database import SessionLocal
from db.crud import get_all_answered_evaluations
from helpers import (
    remove_useless_intents,
    generate_remaining_suggestions,
)
from .mappings import intent_to_functionality_dict


def main():
    db = SessionLocal()
    answered_evaluations = get_all_answered_evaluations(db)
    with open("new_data.dat", "w") as outfile:
        for answer in answered_evaluations:
            intents = [up.user_dialogue.intent for up in answer.user_prompts]
            create_vw_line(intents, answer.answer, answer.suggestion, outfile)


def create_vw_line(
    context: list[str], response: bool, suggestion: str, file: TextIOWrapper
):
    functionalities = [intent_to_functionality_dict[x] for x in context]
    remaining_suggestions = generate_remaining_suggestions(functionalities)
    intents = remove_useless_intents(context)

    result = -(int(response) - 1)

    probability = 1.0 / len(remaining_suggestions)

    file.write(f"shared |S {' '.join(map(str, intents))}\n")
    file.write(
        f"0:{float(result)}:{probability} |A action={suggestion}\n"
    )

    for sug in remaining_suggestions:
        if sug != suggestion:
            file.write(f"|A action={sug}\n")
    file.write("\n")


if __name__ == "__main__":
    main()
