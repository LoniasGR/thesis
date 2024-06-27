from sqlalchemy import Boolean, Column, String, Float, DateTime
from datetime import datetime

from .database import Base


class User(Base):
    __tablename__ = "users"

    uid = Column(String, primary_key=True, index=True)
    intent = Column(String)
    previous_intents = Column(String)
    previous_suggestions = Column(String)
    remaining_suggestions = Column(String)
    # These are saved so we remember what we suggested
    recommendation = Column(String)
    recommendation_probability = Column(Float)
    recommendation_cost = Column(Float)
    # This to check if we are waiting to get the results of a recommendation
    awaits_results = Column(Boolean)
    # This is to check if we need to run learning on the current intent or the next
    awaits_intent = Column(Boolean)
    # Keep creation and update time
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
