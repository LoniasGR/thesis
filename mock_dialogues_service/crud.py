import uuid
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import select

import models, schemas


def get_all(clazz: type, db: Session, skip: int = 0, limit: int = 100):
    return db.execute(select(clazz).offset(skip).limit(100)).all()


def get_user_dialogue_by_intent(db: Session, intent: str):
    return db.scalars(
        select(models.UserDialogueDB).where(models.UserDialogueDB.intent == intent)
    ).first()


def get_client_by_host(db: Session, host: str):
    return db.scalars(
        select(models.ClientDB).where(models.ClientDB.host == host)
    ).first()


def get_user_dialogues_by_intent_list(db: Session, intents: list[str]):
    return db.execute(
        select(models.UserDialogueDB).where(models.UserDialogueDB.intent.in_(intents))
    ).all()


def create_evaluation(db: Session, ev: schemas.Evaluation):
    prompts = list()
    for pr in ev.user:
        prompts.append(get_user_dialogue_by_intent(db, pr.intent))

    db_evaluation = models.EvaluationDB(
        uuid=ev.uuid,
        suggestion=ev.suggestion,
        client_id=ev.client.id,
        user_prompts=prompts,
    )

    db.add(db_evaluation)

    db.commit()
    db.refresh(db_evaluation)
    return db_evaluation


def create_user_dialogue(db: Session, usr: schemas.UserUtterance):
    db_user_dialogue = models.UserDialogueDB(
        description=usr.description, intent=usr.intent
    )
    db.add(db_user_dialogue)
    db.commit()
    db.refresh(db_user_dialogue)
    return db_user_dialogue


def create_client(db: Session, host: str):
    db_client = models.ClientDB(host=host)
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client


def create_or_get_user_dialogue(db: Session, usr: schemas.UserUtterance):
    existing = get_user_dialogue_by_intent(db, usr.intent)
    if existing != None:
        return existing
    return create_user_dialogue(db, usr)


def create_or_get_client(db: Session, host: str):
    existing = get_client_by_host(db, host)
    if existing != None:
        return existing
    return create_client(db, host)
