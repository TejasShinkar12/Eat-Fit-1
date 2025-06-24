from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    Float,
    Enum,
    DateTime,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.orm import relationship
from datetime import datetime
from app.enums import SexEnum, ActivityLevelEnum, FitnessGoalEnum
from sqlalchemy import Enum as SAEnum

from app.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    height = Column(Float, nullable=True)
    weight = Column(Float, nullable=True)
    age = Column(Integer, nullable=True)
    sex = Column(SAEnum(SexEnum, name="sex_enum"), nullable=True)
    activity_level = Column(SAEnum(ActivityLevelEnum, name="activity_level_enum"), nullable=True)
    fitness_goal = Column(SAEnum(FitnessGoalEnum, name="fitness_goal_enum"), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    inventory_items = relationship("Inventory", back_populates="owner") 