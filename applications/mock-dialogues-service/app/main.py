import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import HTTPException
from sqlalchemy import null
from sqlalchemy.orm import Session

from utils.helpers import get_all_intents
from utils.generate_dialogues import (
    generate_dialogue,
    create_user_utterances,
    generate_suggestion,
    present_suggestion,
    create_bot_responses,
)
from db.database import SessionLocal, engine
import db.crud as crud, db.models as models
import models.schemas as schemas
from logger.logger import CustomLogger


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
    responses = create_bot_responses(intents)
    for dial, utt, resp in zip(intents, utts, responses):
        crud.create_or_get_user_dialogue(
            next(get_db()),
            schemas.UserUtterance(intent=dial, description=utt, response=resp),
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


@app.get("/generate", response_model=list[schemas.Suggestion])
def generate(request: Request, dialogues: int = 3, db: Session = Depends(get_db)):
    host = request.headers["Host"]
    if "x-forwared-for" in request.headers:
        host = request.headers["x-forwared-for"]

    client = crud.create_or_get_client(db, host=host)

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
        ret_data.append(
            schemas.Suggestion(
                uuid=eval_db.uuid,
                suggestion=eval_db.suggestion,
                suggestion_utterance=present_suggestion(eval_db.suggestion),
                user=[
                    schemas.UserUtterance(**u.user_dialogue.__dict__)
                    for u in eval_db.user_prompts
                ],
                answer=None,
            )
        )
    return ret_data


@app.post("/evaluate")
def evaluate(ev: schemas.EvaluationBase, db: Session = Depends(get_db)):
    new_ev = crud.update_evaluation_answer(db, ev.uuid, ev.answer)
    if new_ev == None:
        raise HTTPException(status_code=400, detail="Wrong evaluation id")
    return new_ev


@app.get(
    "/health",
    tags=["healthcheck"],
    summary="Perform a Health Check",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=schemas.HealthCheck,
)
def get_health() -> schemas.HealthCheck:
    """
    ## Perform a Health Check
    Endpoint to perform a healthcheck on. This endpoint can primarily be used Docker
    to ensure a robust container orchestration and management is in place. Other
    services which rely on proper functioning of the API service will not deploy if this
    endpoint returns any other HTTP status code except 200 (OK).
    Returns:
        HealthCheck: Returns a JSON response with the health status
    """
    return schemas.HealthCheck(status="OK")


app.mount("/", SPAStaticFiles(directory="frontend/dist", html=True), name="app")
