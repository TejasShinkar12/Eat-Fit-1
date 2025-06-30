import uuid
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict, Field
from datetime import datetime
from enum import Enum
from app.enums import SexEnum, ActivityLevelEnum, FitnessGoalEnum


# Shared properties
class UserBase(BaseModel):
    email: EmailStr = Field(
        ...,
        description="User's email address",
        json_schema_extra={"example": "user@example.com"},
    )
    height: Optional[float] = Field(
        None,
        description="User's height in centimeters",
        json_schema_extra={"example": 175.0},
    )
    weight: Optional[float] = Field(
        None,
        description="User's weight in kilograms",
        json_schema_extra={"example": 70.5},
    )
    age: Optional[int] = Field(
        None, description="User's age in years", json_schema_extra={"example": 30}
    )
    sex: Optional[SexEnum] = Field(
        None, description="User's biological sex", json_schema_extra={"example": "male"}
    )
    activity_level: Optional[ActivityLevelEnum] = Field(
        None,
        description="User's activity level",
        json_schema_extra={"example": "moderate"},
    )
    fitness_goal: Optional[FitnessGoalEnum] = Field(
        None,
        description="User's fitness goal",
        json_schema_extra={"example": "lose"},
    )


# Properties to receive on user creation
class UserCreate(UserBase):
    password: str = Field(
        ...,
        min_length=6,
        max_length=18,
        description="User password (plain text)",
        json_schema_extra={"example": "strongpassword123"},
    )


# Properties to receive on user update
class UserUpdate(UserBase):
    password: Optional[str] = Field(
        None,
        min_length=6,
        max_length=18,
        description="User password (plain text)",
        json_schema_extra={"example": "strongpassword123"},
    )


# Properties shared by models stored in DB
class UserInDBBase(UserBase):
    id: uuid.UUID = Field(
        ...,
        description="User ID",
        json_schema_extra={"example": "b3b7c7e2-8c2a-4e2a-9e2a-123456789abc"},
    )
    hashed_password: str = Field(
        ..., description="Hashed password", json_schema_extra={"example": "$2b$12$..."}
    )
    model_config = ConfigDict(from_attributes=True)


# Properties to return to client
class User(UserBase):
    id: uuid.UUID = Field(
        ...,
        description="User ID",
        json_schema_extra={"example": "b3b7c7e2-8c2a-4e2a-9e2a-123456789abc"},
    )
    created_at: datetime = Field(
        ...,
        description="User creation timestamp",
        json_schema_extra={"example": "2024-06-01T12:00:00Z"},
    )
    updated_at: datetime = Field(
        ...,
        description="User update timestamp",
        json_schema_extra={"example": "2024-06-01T12:00:00Z"},
    )
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "b3b7c7e2-8c2a-4e2a-9e2a-123456789abc",
                "email": "user@example.com",
                "height": 175.0,
                "weight": 70.5,
                "age": 30,
                "sex": "male",
                "activity_level": "moderate",
                "fitness_goal": "lose",
                "created_at": "2024-06-01T12:00:00Z",
                "updated_at": "2024-06-01T12:00:00Z",
            }
        },
    )


# Properties stored in DB
class UserInDB(UserInDBBase):
    pass
