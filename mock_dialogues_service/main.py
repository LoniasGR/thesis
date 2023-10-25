import uuid
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
from helpers import get_all_intents

from schemas import Evaluation
from generate_dialogues import (
    generate_dialogue,
    create_user_utterances,
    generate_suggestion,
    present_suggestion,
    record_feedback,
)
from database import SessionLocal, engine
import crud, models, schemas
from logger import CustomLogger


models.Base.metadata.create_all(bind=engine)
logger: CustomLogger = CustomLogger(__name__)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Here we do stuff when the app starts-up
    intents = get_all_intents()
    utts = create_user_utterances(intents)
    for dial, utt in zip(intents, utts):
        crud.create_or_get_user_dialogue(
            next(get_db()), schemas.UserUtterance(intent=dial, description=utt)
        )
    yield
    # Here we do stuff when the app shuts-down


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SPAStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        try:
            return await super().get_response(path, scope)
        except HTTPException as ex:
            if ex.status_code == 404:
                return await super().get_response("index.html", scope)
            else:
                raise ex


@app.get("/generate")
def generate(request: Request, dialogues: int = 3, db: Session = Depends(get_db)):
    client = crud.create_or_get_client(db, host=request.client.host)

    ret_data = list()
    for d in range(dialogues):
        user = generate_dialogue()
        uttsDB = crud.get_user_dialogues_by_intent_list(db, user)
        suggestion = generate_suggestion(user)

        eval = schemas.Evaluation(
            client=client,
            user=uttsDB,
            suggestion=suggestion,
            uuid=str(uuid.uuid4()),
            answer=None,
        )
        eval_db = crud.create_evaluation(db, eval)

        d_data = {
            "uuid": eval_db.uuid,
            "user": [p.user_dialogue.description for p in eval_db.user_prompts],
            "user_intents": [p.user_dialogue.intent for p in eval_db.user_prompts],
            "suggestions": present_suggestion(eval_db.suggestion),
            "suggestion_intent": eval_db.suggestion,
        }
        ret_data.append(d_data)
    return ret_data


@app.post("/evaluate")
def evaluate(ev: schemas.EvaluationBase, db: Session = Depends(get_db)):
    new_ev = crud.update_evaluation_answer(db, ev.uuid, ev.answer)
    if new_ev == None:
        raise HTTPException(status_code=400, detail="Wrong evaluation id")
    return new_ev


app.mount("/", SPAStaticFiles(directory="frontend/build", html=True), name="app")