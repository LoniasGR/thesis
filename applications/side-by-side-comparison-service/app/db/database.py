import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from logger.logger import CustomLogger

logger: CustomLogger = CustomLogger(__name__)

SQLALCHEMY_DATABASE_URL = os.getenv("DB_URL", "sqlite:///./sql_app.db")
logger.debug(f"Database: {SQLALCHEMY_DATABASE_URL}")
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    pool_size=10,
    max_overflow=20,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
