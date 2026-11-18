import os

from sqlalchemy import create_engine

SQLALCHEMY_DATABASE_URL = os.getenv("DB_URL", "sqlite:///./sql_app.db")
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    pool_size=10,
    max_overflow=20,
)
