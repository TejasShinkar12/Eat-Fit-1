from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    DateTime,
    Float,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.db import Base


class ConsumptionLog(Base):
    __tablename__ = "consumption_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    inventory_item_id = Column(
        UUID(as_uuid=True), ForeignKey("inventory.id"), nullable=True
    )
    item_name = Column(String, nullable=False)
    quantity_consumed = Column(Float, nullable=False)
    calories_consumed = Column(Float, nullable=False)
    protein_consumed_g = Column(Float, nullable=False)
    carbs_consumed_g = Column(Float, nullable=False)
    fats_consumed_g = Column(Float, nullable=False)
    consumed_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User")
    inventory_item = relationship("Inventory") 