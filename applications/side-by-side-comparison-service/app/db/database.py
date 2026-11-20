import os

from sqlalchemy import create_engine

SQLALCHEMY_DATABASE_URL = os.getenv("DB_URL", "sqlite:///./sql_app.db")
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    pool_size=10,
    max_overflow=20,
)

HUMAN_EVALUATION_DATABASE_URL = os.getenv(
    "HUMAN_EVALUATION_DB_URL", "sqlite:///./human_evaluation.db"
)
human_evaluation_engine = create_engine(
    HUMAN_EVALUATION_DATABASE_URL,
    connect_args={"check_same_thread": False},
    pool_size=10,
    max_overflow=20,
)
