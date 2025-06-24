import uuid
from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
from enum import Enum
from app.enums import SexEnum, ActivityLevelEnum, FitnessGoalEnum


# Shared properties
class UserBase(BaseModel):
    email: EmailStr
    height: Optional[float] = None
    weight: Optional[float] = None
    age: Optional[int] = None
    sex: Optional[SexEnum] = None
    activity_level: Optional[ActivityLevelEnum] = None
    fitness_goal: Optional[FitnessGoalEnum] = None


# Properties to receive on user creation
class UserCreate(UserBase):
    password: str


# Properties to receive on user update
class UserUpdate(UserBase):
    password: Optional[str] = None


# Properties shared by models stored in DB
class UserInDBBase(UserBase):
    id: uuid.UUID
    hashed_password: str

    class Config:
        from_attributes = True


# Properties to return to client
class User(UserBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Properties stored in DB
class UserInDB(UserInDBBase):
    pass 