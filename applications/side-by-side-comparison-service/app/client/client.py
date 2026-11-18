import json
import logging
import random
import uuid
from typing import Any

import httpx2
import numpy as np
from client import rasa_client
from common.helpers import (
    generate_remaining_suggestions,
    get_functionalities_from_intents,
    get_functionality_proposal_from_intent,
)
from common.mappings import (
    functionality_proposal,
    limited_intent_to_dialogue_dict,
    useful_intents,
)
from db import models
from main import output
from models import schemas
from openai import BaseModel, OpenAI
from sqlalchemy.orm import Session
from utils import utils

logger: logging.Logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

rng = np.random.default_rng()


MOCK_DIALOGUES_URL = utils.envOrDefault("MOCK_DIALOGUES_URL", "http://localhost:8123")
SMART_SUGGEST_MICROSERVICE_URL = utils.envOrDefault(
    "SMART_SUGGEST_MICROSERVICE_URL", "http://localhost:8005"
)

client = None
evaluation_model = utils.envOrDefault("LLM_MODEL", "gemini/gemini-3.5-flash-lite")
# evaluation_model = "gpt-6-luna"
conversation_model = "gpt-6-luna"
rasa = rasa_client.RasaClient()
apiKey = utils.envOrDefault("LLM_API_KEY", "sk-_grQ-NZgU07zilTCwlzJkQ")


def initialize_genai_chat():
    if not apiKey:
        return
    global client
    client = OpenAI(
        base_url="http://localhost:4000",
        api_key=apiKey,
    )


def theano_said(dialogue: str) -> None:
    output(f"> ΘΕΑΝΩ: {dialogue}")


def user_said(dialogue: str) -> None:
    output(f"> ΧΡΗΣΤΗΣ: {dialogue}")


def get_random_dialogues() -> dict:
    rasa = rasa_client.RasaClient()
    if not client:
        return {}
    response = rasa.converse("Ναί")
    willingness = rng.random()
    goals = rng.choice(
        [limited_intent_to_dialogue_dict[intent] for intent in useful_intents],
        rng.integers(1, 4),
        replace=False,
    )
    rounds = int(np.round(rng.normal(6.67, 2.28)))
    rounds_counter = 0
    suggestions = int(np.round(rng.normal(2.22, 4.32)))
    suggestions = max(suggestions, 1)
    suggestions_counter = 0
    dialogue = []
    output(f"goals: {goals}, suggestions = {suggestions} uid = {rasa.uuid}")
    instructions = f"""
        Είσαι Έλληνας χρήστης που θέλει να μάθει περισσότερα για τον COVID-19. Βρίσκεσαι στην Ελλάδα και το έτος είναι 2021. 
        Μιλάς με ένα chatbot για τον COVID-19.

        ΡΟΛΟΣ
        - Μίλα πάντα στα ελληνικά, σαν πραγματικός άνθρωπος. Μην αποκαλύψεις ποτέ ότι είσαι AI και μην βγεις ποτέ από τον ρόλο σου.
        - Ο ρόλος σου είναι να ρωτάς, όχι να απαντάς. Μιλάς με bot, οπότε μην ρωτάς για την υγεία του και μην κάνεις small talk μαζί του.
        - Έγραφε σύντομα και φυσικά, όπως σε chat: μία ή δύο προτάσεις, καθημερινή γλώσσα, χωρίς markdown, λίστες ή μορφοποίηση.
        - Χαιρέτησε μόνο στο πρώτο μήνυμα. Μην χαιρετάς ξανά.
        - Αν παρατηρήσεις ότι το bot δεν καταλαβαίνει, δεν απαντά σωστά ή λέει ότι δεν γνωρίζει σχετικά με το θέμα, μην επιμένεις πολύ,
          συνέχισε στον επόμενο στόχο σου.
        - Αν το chatbot σου δώσει μια ημερομηνία του 2026, αποδέξου την σαν να ήταν ημερομηνία του 2021. Μην του ζητήσεις να σου δώσει στοιχεία 
          για το 2021.
    

        ΣΤΟΧΟΣ
        - Θέλεις να πάρεις πληροφορίες με βάση τις παρακάτω ερωτήσεις/στόχους - παράφρασε αν χρειάζεται: {', '.join(goals)}
        - Μην την αντιγράψεις αυτούσια. Διατύπωσέ την με δικά σου λόγια και, αν χρειαστεί, προσέγγισέ την σταδιακά με συμπληρωματικές ερωτήσεις.
        - Αν ο bot δεν καταλάβει, ξαναδιατύπωσε την ερώτηση διαφορετικά.

        ΠΟΤΕ ΝΑ ΤΕΛΕΙΩΣΕΙΣ
        Γράψε ΜΟΝΟ [END_CONVERSATION], χωρίς τίποτα άλλο, όταν συμβεί ένα από τα παρακάτω:
        1. Πήρες ικανοποιητική απάντηση για τον στόχο σου.
        2. Ο bot σου έχει κάνει περισσότερες από {suggestions} προτάσεις (π.χ. σου προτείνει άλλα θέματα ή επόμενες ερωτήσεις αντί να απαντά).
        3. Μετά από αρκετές προσπάθειες δεν παίρνεις απάντηση.
        ΣΤΑΣΗ
        {'Δεν είσαι πολύ πρόθυμος να επιμείνεις. Αν ο bot δεν σε καταλαβαίνει ή κάτι πάει στραβά, τα παρατάς σύντομα.'
        if willingness > 0.17 else 'Είσαι υπομονετικός. Αν ο bot δεν σε καταλάβει, επανέλαβε ή ξαναδιατύπωσε την ερώτησή σου όσες φορές χρειαστεί.'} 

        Παραδείγματα ερωτημάτων:
        - "πόσα κρούσματα ανακοινώθηκαν σήμερα"
        - "πότε ξεκίνησε η πανδημία"
        - "αν οι δυο δοσεις του εμβολιου ηταν moderna τι θα είναι η τριτη"
        - πως ξεχωρίζει κανεις τον covid από τη γρίπη;
                """
    greeting = [{"role": "user", "content": response}]
    theano_said(response)
    dialogue.append(f"assistant: {response}")
    previous_response_id = None
    r = client.responses.create(
        model=conversation_model,
        input=f"{greeting}",
        instructions=instructions,
    )
    user_said(r.output_text)
    dialogue.append(f"user: {r.output_text}")
    previous_response_id = r.id

    while True:
        if "[END_CONVERSATION]" in r.output_text or rounds_counter > rounds:
            state = rasa.get_state()
            return {
                "state": state,
                "dialogue": dialogue,
                "goal": goals,
                "suggest": False,
            }

        response = rasa.converse(r.output_text)

        if "[SUGGESTION_REQUIRED]" in response:
            suggestions_counter += 1
            if suggestions_counter < suggestions:
                response = " ".join(response.split("[SUGGESTION_REQUIRED]"))
            else:
                theano_said(response)
                dialogue.append(
                    f"assistant: {response.split("[SUGGESTION_REQUIRED]")[0].strip()}"
                )
                state = rasa.get_state()
                return {
                    "state": state,
                    "dialogue": dialogue,
                    "goal": goals,
                    "suggest": True,
                }

        theano_said(response)
        dialogue.append(f"assistant: {response}")
        r = client.responses.create(
            model=conversation_model,
            instructions=instructions,
            input=f"{[{"role": "user", "content": response}]}",
            previous_response_id=previous_response_id,
        )
        user_said(r.output_text)
        dialogue.append(f"user: {r.output_text}")
        previous_response_id = r.id
        rounds_counter += 1


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


class GeneratedSuggestion(BaseModel):
    suggestion: str
    reasoning: str


def get_generated_suggestion(dialogue) -> Any:
    if not client:
        return None
    response = client.responses.parse(
        model=evaluation_model,
        instructions=f"""
        You are a recommendation agent that proposes next topics of discussion 
        based on the previous conversation context. The conversation pool is 
        limited to the intents defined below and your job is to suggest
        the next relevant topic of discussion based on the dialogue present. 
        Please provide a JSON response with two fields 
        "suggestion" and "reasoning": {{"suggestion": "<next_topic>", "reasoning": "<reasoning>"}}.
        Do not repeat an intent that has already been discussed.
        Available intents are: {functionality_proposal}
        """,
        input="\n".join(dialogue),
        text_format=GeneratedSuggestion,
    )
    return json.loads(response.output_text)


class AssessedSuggestion(BaseModel):
    picked: int
    reasoning: str


def assess_suggestions(dialogue, suggestions):
    if not client:
        return None
    response = client.responses.parse(
        model=evaluation_model,
        instructions="""
        You are responsible for evaluating the output of a
        There are 4 options A/B/C/D tested currently
        and your job is to pick the one that seems the most appropriate based on the 
        dialogue provided. Please provide your response in a JSON format with a
        field "picked" indicating the suggestion number you consider the most appropriate, together
        with a brief explanation in a field "reasoning" describing why you picked that suggestion.
        """,
        input=f"""
        Dialogue: {'\n'.join(dialogue)}
        Suggestion 1: {suggestions["random"]}
        Suggestion 2: {suggestions["smart"]}
        Suggestion 3: {suggestions["popularity"]}
        """,
        text_format=AssessedSuggestion,
    )
    return json.loads(response.output_text)


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
    r = httpx2.post(url=url, json=data)
    body = r.json()
    if body["error"] is None:
        return remaining_suggesstions[body["action"]]
    raise Exception(body["error"])


def create_side_by_side(db: Session):
    dialogue = get_random_dialogues()
    user_utts, intents = clean_up_dialogue(db, dialogue)
    random_suggestion, random_suggestion_utterance = get_random_suggestion(dialogue)
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
