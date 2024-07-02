from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import select

from . import models
import models.schemas as schemas


def get_user_dialogue_by_intent(db: Session, intent: str):
    return db.scalar(
        select(models.UserDialogueDB).where(models.UserDialogueDB.intent == intent)
    )


def create_user_dialogue(db: Session, usr: schemas.UserUtterance):
    db_user_dialogue = models.UserDialogueDB(
        description=usr.description, intent=usr.intent, response=usr.response
    )
    db.add(db_user_dialogue)
    db.commit()
    db.refresh(db_user_dialogue)
    return db_user_dialogue


def create_or_get_user_dialogue(db: Session, usr: schemas.UserUtterance):
    existing = get_user_dialogue_by_intent(db, usr.intent)
    if existing != None:
        return existing
    return create_user_dialogue(db, usr)


def create_suggestion(
    db: Session, suggestion: schemas.ComparisonSuggestion, client=models.ClientDB
):
    db_suggestion = models.ComparisonsDB(
        uuid=suggestion.uuid,
        random_intent=suggestion.random_intent,
        smart_intent=suggestion.smart_intent,
        client=client,
    )

    for idx, pr in enumerate(suggestion.user):
        r = models.ComparisonDialoguesDB(
            order=idx,
            user_dialogue=get_user_dialogue_by_intent(db, pr.intent),
        )

    db.add(db_suggestion)

    db.commit()
    db.refresh(db_suggestion)
    return db_suggestion


def create_client(db: Session, host: str):
    db_client = models.ClientDB(host=host)
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client


def get_client_by_host(db: Session, host: str):
    return db.scalar(select(models.ClientDB).where(models.ClientDB.host == host))


def create_or_get_client(db: Session, host: str):
    existing = get_client_by_host(db, host)
    if existing != None:
        return existing
    return create_client(db, host)
