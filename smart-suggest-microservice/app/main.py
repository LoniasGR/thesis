from typing import Generator

from fastapi import Depends, FastAPI, Response, status
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from vw.vw_utils import create_suggestion, vw_learn, init_model
from db import db_models, crud
from db.database import SessionLocal, engine
from data_models.classes import (
    Suggestion,
    UserData,
    SuggestionRequestData,
    UserIntentRequestData,
)
from logger.logger import CustomLogger
from decorators.tasks import repeat_every
from jobs.jobs import clear_up_old_users

db_models.Base.metadata.create_all(bind=engine)

app: FastAPI = FastAPI()

logger: CustomLogger = CustomLogger(__name__)

load_dotenv()
init_model()

# Dependency
def get_db() -> Generator[Session, None, None]:
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/suggest", response_model=Suggestion, status_code=status.HTTP_200_OK)
def suggest(
    data: SuggestionRequestData, response: Response, db: Session = Depends(get_db)
):
    logger.debug("/suggest was called")
    if crud.user_exists(db, data.uid):
        user = crud.get_user_data(db, data.uid)
    else:
        response.status_code = status.HTTP_201_CREATED
        user: UserData = UserData(
            uid=data.uid,
            intent="",
            previous_intents=[],
            previous_suggestions=[],
            remaining_suggestions=[],
            recommendation="",
            recommendation_probability=0,
            recommendation_cost=0,
            awaits_results=False,
            awaits_intent=False,
            created_at=None,
            updated_at=None,
        )
    logger.debug(f"Data:")
    data.log(logger)

    user.set_historic_data(data)
    user.awaits_results = True
    user.awaits_intent = True

    suggestion = create_suggestion(user)

    logger.debug(f"Suggestion: {suggestion}")
    crud.set_user_data(db, user)

    logger.debug(f"User:")
    user.log(logger)

    return {"action": suggestion}


@app.post("/intent", status_code=status.HTTP_200_OK)
def intent(data: UserIntentRequestData, db: Session = Depends(get_db)):
    logger.debug("/intent was called")
    logger.debug("Data:")
    data.log(logger)

    if crud.user_exists(db, data.uid):
        user: UserData = crud.get_user_data(db, data.uid)
    else:
        user = UserData(
            uid=data.uid,
            intent="",
            previous_intents=[],
            previous_suggestions=[],
            remaining_suggestions=[],
            recommendation="",
            recommendation_probability=0,
            recommendation_cost=0,
            awaits_results=False,
            awaits_intent=False,
            created_at=None,
            updated_at=None,
        )

    if not user.awaits_intent and not user.awaits_results:
        if user.recommendation != "":
            # vw_learn(user, data.intent)
            print("TODO")
    elif not user.awaits_intent and user.awaits_results:
        # Here we learn what the user selected.
        vw_learn(user, data.intent)
        user.awaits_results = False
        user.recommendation = ""

    elif user.awaits_intent:
        if user.intent != data.intent:
            logger.error(
                f"Different user intent ({user.intent}) and data intent ({data.intent})"
            )
            data.intent = user.intent
        user.awaits_intent = False

    user.intent = data.intent



    logger.debug("User")
    user.log(logger)
    crud.set_user_data(db, user)


@app.on_event("startup")
@repeat_every(seconds=60, logger=logger)
async def cuou() -> None:
    clear_up_old_users(next(get_db()), logger)
