from sqlalchemy.orm import Session

from . import db_models
from data_models.classes import UserData
from logger.logger import CustomLogger

logger: CustomLogger = CustomLogger(__name__)


def get_db_content(db_user: db_models.User):
    def _empty_or_result(value: None | str, fn=None) -> None | list[str]:
        if value is None or value == "[]":
            return []
        if fn is None:
            return value
        return fn(value)

    def recreate_arr(v: str):
        return v.strip("[]").split(", ")

    return {
        "uid": db_user.uid,
        "intent": db_user.intent,
        "previous_intents": _empty_or_result(db_user.previous_intents, recreate_arr),
        "previous_suggestions": _empty_or_result(
            db_user.previous_suggestions, recreate_arr
        ),
        "remaining_suggestions": _empty_or_result(
            db_user.remaining_suggestions, recreate_arr
        ),
        "recommendation": db_user.recommendation,
        "recommendation_probability": db_user.recommendation_probability,
        "recommendation_cost": db_user.recommendation_cost,
        "awaits_results": db_user.awaits_results,
        "awaits_intent": db_user.awaits_intent,
        "created_at": db_user.created_at,
        "updated_at": db_user.updated_at,
    }


def get_user_data(db: Session, uid: str) -> UserData:
    db_user = get_user(db, uid)

    return UserData(**get_db_content(db_user))


def user_exists(db: Session, uid: str) -> bool:
    if get_user(db, uid) is not None:
        return True
    return False


def get_user(db: Session, uid: str) -> db_models.User:
    return db.query(db_models.User).filter(db_models.User.uid == uid).first()


def get_all_users(db: Session) -> list[db_models.User]:
    return db.query(db_models.User).all()

def delete_user(db:Session, uid:str) -> None:
    db.query(db_models.User).filter(db_models.User.uid == uid).delete()
    db.commit()

def create_user(db: Session, user: UserData) -> db_models.User:
    def empty_or_array_string(arr: list[str] | None) -> str:
        if arr is [] or arr is None:
            return "[]"
        else:
            return f"[{', '.join(arr)}]"

    db_user = db_models.User(
        uid=user.uid,
        intent=user.intent,
        previous_intents=empty_or_array_string(user.previous_intents),
        previous_suggestions=empty_or_array_string(user.previous_suggestions),
        remaining_suggestions=empty_or_array_string(user.remaining_suggestions),
        recommendation=user.recommendation,
        recommendation_probability=user.recommendation_probability,
        recommendation_cost=user.recommendation_cost,
        awaits_results=user.awaits_results,
        awaits_intent=user.awaits_intent,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user: UserData) -> db_models.User:
    db_user = get_user(db, user.uid)

    db_user.intent = user.intent
    db_user.previous_intents = f"[{', '.join(user.previous_intents)}]"
    db_user.previous_suggestions = f"[{', '.join(user.previous_suggestions)}]"
    db_user.remaining_suggestions = f"[{', '.join(user.remaining_suggestions)}]"
    db_user.recommendation = user.recommendation
    db_user.recommendation_probability = user.recommendation_probability
    db_user.recommendation_cost = user.recommendation_cost
    db_user.awaits_results = user.awaits_results
    db_user.awaits_intent = user.awaits_intent

    db.commit()
    db.refresh(db_user)
    return db_user


def set_user_data(db: Session, user: UserData) -> None:

    if not user_exists(db, user.uid):
        create_user(db, user)
    else:
        update_user(db, user)
