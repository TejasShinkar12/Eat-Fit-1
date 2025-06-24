import uuid
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict, Field
from datetime import datetime
from enum import Enum
from app.enums import SexEnum, ActivityLevelEnum, FitnessGoalEnum


# Shared properties
class UserBase(BaseModel):
    email: EmailStr = Field(..., description="User's email address", example="user@example.com")
    height: Optional[float] = Field(None, description="User's height in centimeters", example=175.0)
    weight: Optional[float] = Field(None, description="User's weight in kilograms", example=70.5)
    age: Optional[int] = Field(None, description="User's age in years", example=30)
    sex: Optional[SexEnum] = Field(None, description="User's biological sex", example="male")
    activity_level: Optional[ActivityLevelEnum] = Field(None, description="User's activity level", example="moderate")
    fitness_goal: Optional[FitnessGoalEnum] = Field(None, description="User's fitness goal", example="weight_loss")


# Properties to receive on user creation
class UserCreate(UserBase):
    password: str = Field(..., description="User's password", example="strongpassword123")


# Properties to receive on user update
class UserUpdate(UserBase):
    password: Optional[str] = Field(None, description="User's password", example="newpassword456")


# Properties shared by models stored in DB
class UserInDBBase(UserBase):
    id: uuid.UUID = Field(..., description="User's unique identifier", example="b3b7c7e2-8c2a-4e2a-9e2a-123456789abc")
    hashed_password: str = Field(..., description="Hashed user password", example="hashedpassword...")
    model_config = ConfigDict(from_attributes=True)


# Properties to return to client
class User(UserBase):
    id: uuid.UUID = Field(..., description="User's unique identifier", example="b3b7c7e2-8c2a-4e2a-9e2a-123456789abc")
    created_at: datetime = Field(..., description="User creation timestamp", example="2024-06-01T12:00:00Z")
    updated_at: datetime = Field(..., description="User last update timestamp", example="2024-06-01T12:00:00Z")
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
                "fitness_goal": "weight_loss",
                "created_at": "2024-06-01T12:00:00Z",
                "updated_at": "2024-06-01T12:00:00Z"
            }
        }
    )


# Properties stored in DB
class UserInDB(UserInDBBase):
    pass 