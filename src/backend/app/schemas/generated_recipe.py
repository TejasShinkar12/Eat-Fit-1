import uuid
from pydantic import BaseModel
from typing import List

class GeneratedRecipeBase(BaseModel):
    title: str
    ingredients: List[str]
    directions: str

class GeneratedRecipeCreate(GeneratedRecipeBase):
    pass

class GeneratedRecipeRead(GeneratedRecipeBase):
    id: uuid.UUID

    class Config:
        from_attributes = True
