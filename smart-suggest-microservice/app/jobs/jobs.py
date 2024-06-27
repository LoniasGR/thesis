from datetime import datetime, timedelta
from logging import Logger
from sqlalchemy.orm import Session

from data_models.classes import UserData
from db.crud import get_all_users, get_db_content, delete_user
from vw.vw_utils import vw_learn


def clear_up_old_users(db: Session, logger: Logger):
    logger.info("Starting cleanup")
    users = get_all_users(db)
    now = datetime.now()
    for user in users:
        if user.updated_at + timedelta(minutes=1) < now:
            # The user is pretty old and we can delete it
            user_data = UserData(**get_db_content(user))
            vw_learn(user_data, "")
            logger.info(f"Deleting user {user_data.uid}")
            delete_user(db, user_data.uid)
    logger.info("Finishing cleanup")

