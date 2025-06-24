import uuid
from typing import Optional
from datetime import datetime, date
from pydantic import BaseModel, Field, field_validator, ConfigDict

class InventoryBase(BaseModel):
    """Shared fields for Inventory (not exposed directly)."""
    name: str = Field(..., description="Name of the inventory item", json_schema_extra={"example": "Greek Yogurt"})
    quantity: float = Field(..., description="Quantity of the item (number of servings)", json_schema_extra={"example": 2.0})
    calories_per_serving: Optional[float] = Field(None, description="Calories per serving", json_schema_extra={"example": 120.0})
    protein_g_per_serving: Optional[float] = Field(None, description="Protein per serving (g)", json_schema_extra={"example": 10.0})
    carbs_g_per_serving: Optional[float] = Field(None, description="Carbs per serving (g)", json_schema_extra={"example": 15.0})
    fats_g_per_serving: Optional[float] = Field(None, description="Fats per serving (g)", json_schema_extra={"example": 2.0})
    serving_size_unit: Optional[str] = Field(None, description="Unit for serving size (e.g., g, ml, piece)", json_schema_extra={"example": "g"})
    expiry_date: Optional[date] = Field(None, description="Expiry date (YYYY-MM-DD)", json_schema_extra={"example": "2024-12-31"})
    source: Optional[str] = Field(None, description="Source of the item (e.g., manual, image)", json_schema_extra={"example": "manual"})

    @field_validator('quantity')
    @classmethod
    def quantity_non_negative(cls, v):
        if v < 0:
            raise ValueError('Quantity must be non-negative')
        return v

    @field_validator('expiry_date')
    @classmethod
    def expiry_date_in_future(cls, v):
        if v is not None and v < date.today():
            raise ValueError('Expiry date must be today or in the future')
        return v

class InventoryCreate(InventoryBase):
    """Fields required for creating an inventory item."""
    pass

class InventoryUpdate(BaseModel):
    """Fields for updating an inventory item (all optional)."""
    name: Optional[str] = Field(None, json_schema_extra={"example": "Greek Yogurt"})
    quantity: Optional[float] = Field(None, json_schema_extra={"example": 2.0})
    calories_per_serving: Optional[float] = Field(None, json_schema_extra={"example": 120.0})
    protein_g_per_serving: Optional[float] = Field(None, json_schema_extra={"example": 10.0})
    carbs_g_per_serving: Optional[float] = Field(None, json_schema_extra={"example": 15.0})
    fats_g_per_serving: Optional[float] = Field(None, json_schema_extra={"example": 2.0})
    serving_size_unit: Optional[str] = Field(None, json_schema_extra={"example": "g"})
    expiry_date: Optional[date] = Field(None, json_schema_extra={"example": "2024-12-31"})
    source: Optional[str] = Field(None, json_schema_extra={"example": "manual"})

    @field_validator('quantity')
    @classmethod
    def quantity_non_negative(cls, v):
        if v is not None and v < 0:
            raise ValueError('Quantity must be non-negative')
        return v

    @field_validator('expiry_date')
    @classmethod
    def expiry_date_in_future(cls, v):
        if v is not None and v < date.today():
            raise ValueError('Expiry date must be today or in the future')
        return v

class InventoryRead(InventoryBase):
    """Fields returned in API responses for inventory items."""
    id: uuid.UUID = Field(..., json_schema_extra={"example": "b3b7c7e2-8c2a-4e2a-9e2a-123456789abc"})
    added_at: datetime = Field(..., json_schema_extra={"example": "2024-06-01T12:00:00Z"})
    updated_at: datetime = Field(..., json_schema_extra={"example": "2024-06-01T12:00:00Z"})

    model_config = ConfigDict(from_attributes=True)

class InventoryInDB(InventoryRead):
    """Internal schema for inventory (includes user_id)."""
    user_id: uuid.UUID = Field(..., json_schema_extra={"example": "b3b7c7e2-8c2a-4e2a-9e2a-123456789abc"})
    model_config = ConfigDict(from_attributes=True) 