import uuid
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field, ConfigDict
from app.enums import ImageUploadStatus


class ImageUploadBase(BaseModel):
    file_path: str = Field(..., description="Relative file path to the uploaded image")
    status: ImageUploadStatus = Field(..., description="Status of the image upload")
    error_message: Optional[str] = Field(
        None, description="Error message if upload or detection failed"
    )


class ImageUploadCreate(ImageUploadBase):
    user_id: uuid.UUID = Field(..., description="ID of the user who uploaded the image")


class ImageUploadReviewObject(BaseModel):
    object_name: str = Field(..., description="Reviewed object name")
    quantity: int = Field(1, description="Quantity detected or reviewed")
    confidence: float = Field(..., description="Detection confidence score")
    bbox: List[float] = Field(..., description="Bounding box [x1, y1, x2, y2]")


class ImageUploadReview(BaseModel):
    reviewed_results: List[ImageUploadReviewObject] = Field(
        ..., description="List of reviewed/edited detection results"
    )


class ImageUploadRead(ImageUploadBase):
    id: uuid.UUID = Field(..., description="Image upload record ID")
    user_id: uuid.UUID = Field(..., description="ID of the user who uploaded the image")
    created_at: datetime = Field(..., description="Upload creation timestamp")
    updated_at: datetime = Field(..., description="Upload update timestamp")
    detection_results_json: Optional[List[Any]] = Field(
        None, description="Detection results as JSON"
    )
    reviewed_results: Optional[List[Any]] = Field(
        None, description="List of reviewed/edited detection results"
    )
    model_config = ConfigDict(from_attributes=True)


class InventoryFromDetectionObject(BaseModel):
    name: str = Field(..., description="Name of the inventory item")
    quantity: float = Field(
        ..., description="Quantity of the item (number of servings)"
    )
    calories_per_serving: float = Field(..., description="Calories per serving")
    protein_g_per_serving: float = Field(..., description="Protein per serving (g)")
    carbs_g_per_serving: float = Field(..., description="Carbs per serving (g)")
    fats_g_per_serving: float = Field(..., description="Fats per serving (g)")
    serving_size_unit: str = Field(
        ..., description="Unit for serving size (e.g., g, ml, piece)"
    )
    expiry_date: Optional[str] = Field(None, description="Expiry date (YYYY-MM-DD)")
    source: str = Field("image", description="Source of the item (default: image)")


class InventoryFromDetectionPayload(BaseModel):
    items: List[InventoryFromDetectionObject] = Field(
        ..., description="List of inventory items to create from detections"
    )
