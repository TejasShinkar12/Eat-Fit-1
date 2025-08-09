from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, inventory, recipe

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["inventory"])
api_router.include_router(recipe.router, prefix="/recipe", tags=["recipe"])
