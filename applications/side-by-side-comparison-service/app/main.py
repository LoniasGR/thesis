import logging
import random
import sys
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


def loop():
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
        llm_suggestion = client.get_generated_suggestion(dialogue)
        popularity_suggestion = random.choice(
            intent_to_suggestion_popularity_baseline[
                actions_data["previous_intents"][-1]
            ]
        )
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
            # "llm": {
                # "utt": functionality_proposal[llm_suggestion["suggestion"]],
                # "intent": llm_suggestion["suggestion"],
            # },
            "popularity": {
                "utt": (
                    random.choice(functionality_proposal[popularity_suggestion])
                    if "no_action" == popularity_suggestion
                    else functionality_proposal[popularity_suggestion]
                ),
                "intent": popularity_suggestion,
            },
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
                    # llm_suggestion=llm_suggestion["suggestion"],
                    choice=assessed_suggestion["picked"],
                    choice_reason=assessed_suggestion["reasoning"],
                )
            )
        session.commit()


if __name__ == "__main__":
    from tqdm import tqdm

    for i in tqdm(range(int(sys.argv[1]))):
        loop()
