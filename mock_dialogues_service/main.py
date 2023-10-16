import uuid
import uvicorn
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session

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

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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
        utts = create_user_utterances(user)

        uttsDB = list()
        # Save the utterance if it doesn't exist already
        for dial, utt in zip(user, utts):
            uttsDB.append(
                crud.create_or_get_user_dialogue(
                    db, schemas.UserUtterance(intent=dial, description=utt)
                )
            )

        suggestion = generate_suggestion(user)
        sugg_utt = present_suggestion(suggestion)

        eval = schemas.Evaluation(
            client=client,
            user=uttsDB,
            suggestion=suggestion,
            uuid=str(uuid.uuid4()),
            answer=None,
        )
        crud.create_evaluation(db, eval)

        d_data = {
            "uid": uuid.uuid4(),
            "user": utts,
            "user_intents": user,
            "suggestions": sugg_utt,
            "suggestion_intent": suggestion,
        }
        ret_data.append(d_data)
    return ret_data


@app.post("/evaluate")
def evaluate(ev: Evaluation, request: Request, db: Session = Depends(get_db)):
    client = crud.create_or_get_client(db, schemas.Client(host=request.client.host))
    intents = crud.get_user_dialogues_by_intent_list(db, ev.user)

    db_ev = models.EvaluationDB()

    record_feedback(ev.user, ev.suggestion, ev.answer)


app.mount("/", SPAStaticFiles(directory="frontend/build", html=True), name="app")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
