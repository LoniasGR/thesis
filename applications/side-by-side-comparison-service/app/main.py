import argparse
import logging
import random
import uuid

from client import client
from common.helpers import get_actions
from common.mappings import (
    functionality_proposal,
    intent_to_suggestion_popularity_baseline,
)
from db import models
from db.database import engine
from sqlalchemy.orm import Session
from utils.utils import shouldPrint

models.Base.metadata.create_all(bind=engine)
logger: logging.Logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

output = shouldPrint(True)


def loop(include_llm: bool) -> None:
    client.initialize_genai_chat()
    result = client.get_random_dialogues()
    state = result["state"]
    dialogue = result["dialogue"]
    actions_data = get_actions(state["events"])
    if result["suggest"]:
        print("Previous slot value:", actions_data["previous_slot_values"])
        print("Previous intents:", actions_data["previous_intents"])
        smart_suggestion = actions_data["previous_slot_values"][-1]
        actions_data["remaining_suggestions"].append(
            actions_data["previous_slot_values"][-1]
        )
        actions_data["previous_slot_values"].pop(-1)
        random_suggestion = random.choice(actions_data["remaining_suggestions"])
        latest_intent = actions_data["previous_intents"][-1]
        popularity_candidates = intent_to_suggestion_popularity_baseline.get(
            latest_intent
        )
        if popularity_candidates is None:
            popularity_candidates = next(
                (
                    intent_to_suggestion_popularity_baseline[intent]
                    for intent in reversed(latest_intent.split("+"))
                    if intent in intent_to_suggestion_popularity_baseline
                ),
                ["no_action"],
            )
        popularity_suggestion = random.choice(popularity_candidates)
        suggestions = {
            "random": {
                "utt": (
                    random.choice(functionality_proposal[random_suggestion])
                    if "no_action" == random_suggestion
                    else functionality_proposal[random_suggestion]
                ),
                "intent": random_suggestion,
            },
            "smart": {
                "utt": (
                    random.choice(functionality_proposal[smart_suggestion])
                    if "no_action" == smart_suggestion
                    else functionality_proposal[smart_suggestion]
                ),
                "intent": smart_suggestion,
            },
            "popularity": {
                "utt": (
                    random.choice(functionality_proposal[popularity_suggestion])
                    if "no_action" == popularity_suggestion
                    else functionality_proposal[popularity_suggestion]
                ),
                "intent": popularity_suggestion,
            },
        }
        llm_suggestion = None
        if include_llm:
            llm_suggestion = client.get_generated_suggestion(dialogue)
            suggestions["llm"] = {
                "utt": functionality_proposal[llm_suggestion["suggestion"]],
                "intent": llm_suggestion["suggestion"],
            }
        output(f"Suggestions: {suggestions}")
        assessed_suggestion = client.assess_suggestions(dialogue, suggestions)
        output(f"Assessed suggestion: {assessed_suggestion}")
    with Session(engine) as session:

        if result["suggest"] == False:
            session.add(
                models.DialogueDB(
                    uuid=str(uuid.uuid4()),
                    dialogue="\n".join(dialogue),
                    goal="\n".join(result["goal"]),
                )
            )
        else:
            session.add(
                models.DialogueDB(
                    uuid=str(uuid.uuid4()),
                    dialogue="\n".join(dialogue),
                    goal="\n".join(result["goal"]),
                    smart_suggestion=smart_suggestion,
                    random_suggestion=random_suggestion,
                    popularity_suggestion=popularity_suggestion,
                    llm_suggestion=(
                        llm_suggestion["suggestion"] if llm_suggestion else None
                    ),
                    choice=assessed_suggestion["picked"],
                    choice_reason=assessed_suggestion["reasoning"],
                )
            )
        session.commit()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run side-by-side suggestion evaluations."
    )
    parser.add_argument("rounds", type=int, help="number of dialogue runs")
    llm_mode = parser.add_mutually_exclusive_group()
    llm_mode.add_argument(
        "--with-llm",
        action="store_true",
        help="include the LLM recommendation as option 4",
    )
    llm_mode.add_argument(
        "--without-llm",
        action="store_true",
        help="compare random, smart, and popularity recommendations only",
    )
    return parser.parse_args()


if __name__ == "__main__":
    from tqdm import tqdm

    args = parse_args()
    include_llm = args.with_llm or not args.without_llm
    for i in tqdm(range(args.rounds)):
        loop(include_llm)
