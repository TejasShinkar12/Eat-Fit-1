import uuid
from typing import List, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class DetectionResultBase(BaseModel):
    object_name: str = Field(..., description="Detected object name")
    quantity: int = Field(1, description="Quantity detected")
    confidence: float = Field(..., description="Detection confidence score")
    bbox: List[float] = Field(..., description="Bounding box [x1, y1, x2, y2]")


class DetectionResultCreate(DetectionResultBase):
    image_upload_id: uuid.UUID = Field(..., description="Related image upload ID")


class DetectionResultRead(DetectionResultBase):
    id: uuid.UUID = Field(..., description="Detection result ID")
    image_upload_id: uuid.UUID = Field(..., description="Related image upload ID")
    created_at: datetime = Field(..., description="Detection creation timestamp")
    model_config = ConfigDict(from_attributes=True)
