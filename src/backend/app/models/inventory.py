from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    DateTime,
    Enum as SAEnum,
    Float,
    Date,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.db import Base


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    quantity = Column(Float, default=1.0, nullable=False)
    calories_per_serving = Column(Float, nullable=True)
    protein_g_per_serving = Column(Float, nullable=True)
    carbs_g_per_serving = Column(Float, nullable=True)
    fats_g_per_serving = Column(Float, nullable=True)
    serving_size_unit = Column(String, nullable=True)
    expiry_date = Column(Date, nullable=True)
    source = Column(String, nullable=True, default="manual")  # e.g., 'image', 'manual'
    added_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    owner = relationship("User", back_populates="inventory_items") 