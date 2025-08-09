from sqlalchemy import Column, String, ForeignKey, DateTime, Enum as SAEnum, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from app.db import Base
from app.enums import ImageUploadStatus


class ImageUpload(Base):
    __tablename__ = "image_upload"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    file_path = Column(String, nullable=False)
    detection_results_json = Column(JSONB, nullable=True)
    status = Column(
        SAEnum(ImageUploadStatus, name="image_upload_status_enum"),
        nullable=False,
        default=ImageUploadStatus.pending,
    )
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
        nullable=False,
    )

    user = relationship("User")
    detection_results = relationship("DetectionResult", back_populates="image_upload")
