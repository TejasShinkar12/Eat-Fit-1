from sqlalchemy import Column, String, ForeignKey, DateTime, Float, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from app.db import Base
from .image_upload import ImageUpload


class DetectionResult(Base):
    __tablename__ = "detection_result"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    image_upload_id = Column(
        UUID(as_uuid=True), ForeignKey("image_upload.id"), nullable=False
    )
    object_name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    confidence = Column(Float, nullable=False)
    bbox = Column(JSONB, nullable=False)  # [x1, y1, x2, y2]
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)

    image_upload = relationship("ImageUpload", back_populates="detection_results")
