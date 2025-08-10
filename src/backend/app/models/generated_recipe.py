import uuid
from sqlalchemy import Column, ForeignKey, String, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db import Base


class GeneratedRecipe(Base):
    __tablename__ = "generated_recipes"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    ingredients = Column(JSON, nullable=False)
    directions = Column(String, nullable=False)

    user = relationship("User")
