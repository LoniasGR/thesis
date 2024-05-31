from database import SessionLocal
from crud import get_all_answered_evaluations
from helpers import (
    get_unique_functionalities,
    remove_useless_intents,
    generate_remaining_suggestions,
)
from mappings import intent_to_functionality_dict


def main():
    db = SessionLocal()
    answered_evaluations = get_all_answered_evaluations(db)
    with open("new_data.dat", "w") as outfile:
        for answer in answered_evaluations:
            intents = [up.user_dialogue.intent for up in answer.user_prompts]
            create_vw_line(intents, answer.answer, answer.suggestion, outfile)


def create_vw_line(context: list[str], response: bool, suggestion: str, file):
    unique_actions = get_unique_functionalities()
    functionalities = [intent_to_functionality_dict[x] for x in context]
    remaining_suggestions = generate_remaining_suggestions(functionalities)
    intents = remove_useless_intents(context)

    result = int(response)

    probability = 1.0 / (len(remaining_suggestions) + 1)

    file.write(f"shared |{' '.join(map(str, context))}\n")
    file.write(
        f"{unique_actions.index(suggestion)}:{float(result)}:{probability} |{suggestion}\n"
    )

    for sug in remaining_suggestions:
        if sug != suggestion:
            file.write(f"|{sug}\n")
    file.write("\n")


if __name__ == "__main__":
    main()
