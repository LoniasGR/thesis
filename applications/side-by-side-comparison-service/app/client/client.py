import uuid

from sqlalchemy.orm import Session
import httpx

from logger.logger import CustomLogger
import utils.utils as utils
import db.crud as crud
import db.models as models
import models.schemas as schemas
from common.helpers import (
    generate_remaining_suggestions,
    get_functionalities_from_intents,
    get_functionality_proposal_from_intent,
)

logger: CustomLogger = CustomLogger(__name__)


MOCK_DIALOGUES_URL = utils.envOrDefault("MOCK_DIALOGUES_URL", "http://localhost:8123")
SMART_SUGGEST_MICROSERVICE_URL = utils.envOrDefault(
    "SMART_SUGGEST_MICROSERVICE_URL", "http://localhost:8005"
)


def get_random_dialogues(length=1) -> list[dict]:
    params = {"dialogues": length}
    headers = {"x-forwarded-for": "127.0.0.1"}
    url = f"{MOCK_DIALOGUES_URL}/generate"
    logger.debug(f"Requesting mock dialogues from {url}")
    r = httpx.get(url, params=params, headers=headers)

    logger.debug(f"Response is {r}")

    return r.json()


def clean_up_dialogue(
    db: Session, dialogue
) -> tuple[list[models.UserDialogueDB], list[str]]:
    user_utts = []
    intents = []
    for d in dialogue[0]["user"]:
        intents.append(d["intent"])
        utt = schemas.UserUtterance(**d)
        user_utts.append(crud.create_or_get_user_dialogue(db, utt))
    return user_utts, intents


def get_random_suggestion(dialogue) -> tuple[str, str]:
    return dialogue[0]["suggestion"], dialogue[0]["suggestion_utterance"]


def get_smart_suggestion(previous_intents) -> str:
    url = f"{SMART_SUGGEST_MICROSERVICE_URL}/suggest"
    functionalities = get_functionalities_from_intents(previous_intents)
    remaining_suggesstions = generate_remaining_suggestions(functionalities)
    data = {
        "uid": f"{uuid.uuid4()}",
        "previous_intents": previous_intents,
        "previous_suggestions": [],
        "remaining_suggestions": remaining_suggesstions,
        "intent": previous_intents[-1],
    }
    r = httpx.post(url=url, json=data)
    body = r.json()
    if body["error"] is None:
        return remaining_suggesstions[body["action"]]
    raise Exception(body["error"])


def create_side_by_side(db: Session):
    dialogue = get_random_dialogues()
    user_utts, intents = clean_up_dialogue(db, dialogue)
    (random_suggestion, random_suggestion_utterance) = get_random_suggestion(dialogue)
    smart_suggestion: str = get_smart_suggestion(intents)

    suggestion = schemas.ComparisonSuggestion(
        uuid=str(uuid.uuid4()),
        user=user_utts,
        response=None,
        random_intent=random_suggestion,
        random_utterance=random_suggestion_utterance,
        smart_intent=smart_suggestion,
        smart_utterance=get_functionality_proposal_from_intent(smart_suggestion),
    )
    return suggestion
