from sqlalchemy import Column, String, Float, Integer, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from ..db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    height = Column(Float)
    weight = Column(Float)
    age = Column(Integer)
    sex = Column(Enum('male', 'female', 'other', name='sex_enum'))
    activity_level = Column(Enum('sedentary', 'light', 'moderate', 'active', 'very_active', name='activity_level_enum'))
    fitness_goal = Column(Enum('lose', 'maintain', 'gain', name='fitness_goal_enum'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 