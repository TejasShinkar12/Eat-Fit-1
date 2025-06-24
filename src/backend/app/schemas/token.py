from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class Token(BaseModel):
    access_token: str = Field(..., description="JWT access token string", example="eyJhbGciOiJIUzI1NiIsInR5cCI6...")
    token_type: str = Field(..., description="Type of the token", example="bearer")
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6...",
                "token_type": "bearer"
            }
        }
    )


class TokenData(BaseModel):
    username: str | None = Field(None, description="Username associated with the token", example="user@example.com")
    model_config = ConfigDict(from_attributes=True)


class TokenPayload(BaseModel):
    sub: Optional[str] = Field(None, description="Subject (usually user identifier)", example="user@example.com")
    exp: Optional[int] = Field(None, description="Expiration time as UNIX timestamp", example=1718000000)

    class Config:
        extra = "allow" 