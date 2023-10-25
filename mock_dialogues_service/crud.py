from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import select
import sqlalchemy.sql.functions as func

import models, schemas


def get_all(clazz: type, db: Session, skip: int = 0, limit: int = 100):
    return db.scalars(select(clazz).offset(skip).limit(100)).all()


def get_user_dialogue_by_intent(db: Session, intent: str):
    return db.scalar(
        select(models.UserDialogueDB).where(models.UserDialogueDB.intent == intent)
    )


def get_client_by_host(db: Session, host: str):
    return db.scalar(select(models.ClientDB).where(models.ClientDB.host == host))


def get_user_dialogues_by_intent_list(db: Session, intents: list[str]):
    return db.scalars(
        select(models.UserDialogueDB).where(models.UserDialogueDB.intent.in_(intents))
    ).all()


def get_evaluation_by_uuid(db: Session, uuid: str) -> models.EvaluationDB | None:
    return db.scalar(
        select(models.EvaluationDB).where(models.EvaluationDB.uuid == uuid)
    )


def update_evaluation_answer(db: Session, uuid: str, answer: bool):
    db_ev = get_evaluation_by_uuid(db, uuid)
    if db_ev == None:
        return None

    db_ev.answer = answer
    db_ev.date_answered = func.now()

    db.commit()
    db.refresh(db_ev)
    return db_ev


def create_evaluation(db: Session, ev: schemas.Evaluation):
    for pr in ev.user:
        r = models.EvaluationDialoguesDB()

    db_evaluation = models.EvaluationDB(
        uuid=ev.uuid,
        suggestion=ev.suggestion,
        client_id=ev.client.id,
    )

    for idx, pr in enumerate(ev.user):
        r = models.EvaluationDialoguesDB(
            order=idx,
            user_dialogue=get_user_dialogue_by_intent(db, pr.intent),
        )
        db_evaluation.user_prompts.append(r)

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
