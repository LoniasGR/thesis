from sqlalchemy.orm import Session

import models, schemas

def get_all(clazz: type, db: Session, skip: int = 0, limit: int = 100):
    return db.query(clazz).offset(skip).limit(100).all()

def get_one(clazz: type, db: Session, id: int):
    return db.query(clazz).filter(clazz.id == id).first()

def get_user_dialogue_by_intent(db: Session, intent: str):
    return db.query(models.UserDialogueDB).filter(models.UserDialogueDB.intent == intent).first()

def create_evaluation(db: Session, ev: schemas.Evaluation):
    db_evaluation = models.EvaluationDB()
    # TODO

def create_user_dialogue(db: Session, usr: schemas.UserUtterance):
    db_user_dialogue = models.UserDialogueDB(description=usr.description, intent=usr.intent)
    db.add(db_user_dialogue)
    db.commit()
    db.refresh(db_user_dialogue)
    return db_user_dialogue

def create_or_get_user_dialogue(db: Session, usr: schemas.UserUtterance):
    existing = get_user_dialogue_by_intent(db, usr.intent)
    if existing != None:
        return existing
    return create_user_dialogue(db, usr)



