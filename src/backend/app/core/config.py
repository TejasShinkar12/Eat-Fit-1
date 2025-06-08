from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, field_validator, constr, Field, model_validator
from pydantic.networks import AnyHttpUrl

class Settings(BaseSettings):
    # API Settings
    PROJECT_NAME: str = "PantryFit"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True

    # Database
    DATABASE_URL: PostgresDsn

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if not str(v).endswith("/"):  # Ensure URL doesn't end with slash
            parts = str(v).split("/")
            if len(parts) < 4 or not parts[-1]:  # Check if database name is present
                raise ValueError("Database URL must include a database name")
        return v

    # Security
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = Field("HS256", pattern="^(HS256|HS384|HS512|RS256|RS384|RS512)$")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, gt=0)

    # Password Settings
    PASSWORD_MIN_LENGTH: int = Field(6, gt=0)
    PASSWORD_MAX_LENGTH: int = Field(18, gt=0)

    @model_validator(mode='after')
    def validate_password_lengths(self) -> 'Settings':
        if self.PASSWORD_MIN_LENGTH > self.PASSWORD_MAX_LENGTH:
            raise ValueError("minimum password length cannot be greater than maximum length")
        return self

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(5, gt=0)

    @field_validator("RATE_LIMIT_PER_MINUTE")
    @classmethod
    def validate_rate_limit(cls, v: int) -> int:
        if v < 1:
            raise ValueError("rate limit must be positive")
        return v

    # CORS Settings
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env"
    ) 