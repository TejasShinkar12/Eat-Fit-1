from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.services.recipe_service import RecipeService
from typing import List
from app.api import deps
from app.models.user import User
from app.schemas.generated_recipe import GeneratedRecipeRead

router = APIRouter()


@router.post("/generate-from-inventory", status_code=200)
def generate_recipes_from_inventory(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Generate recipes from the user's inventory.
    """
    recipe_service = RecipeService()
    recipe = recipe_service.generate_recipe_from_inventory(db, current_user.id)
    return recipe


@router.get("/user-recipes", response_model=List[GeneratedRecipeRead])
def get_user_recipes(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Get all recipes generated for the current user.
    """
    recipe_service = RecipeService()
    recipes = recipe_service.get_generated_recipes(db, current_user.id)
    return recipes
