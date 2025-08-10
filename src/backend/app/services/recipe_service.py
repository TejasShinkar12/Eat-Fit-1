import re
from sqlalchemy.orm import Session
from app.services.ml_services.recipe_generation.gemini_recipe_generator import (
    GeminiRecipeGenerator,
)
from app.models.inventory import Inventory
from app.models.user import User
from app.models.generated_recipe import GeneratedRecipe
from fastapi import HTTPException
import uuid


class RecipeService:
    def __init__(self):
        try:
            self.recipe_generator = GeminiRecipeGenerator()
        except RuntimeError as e:
            raise HTTPException(status_code=500, detail=str(e))

    def _clean_repetitive_text(self, text: str) -> str:
        """
        Remove repetitive words or phrases from text.
        This is a simple heuristic that removes repeated consecutive words.
        """
        # Remove consecutive duplicate words
        text = re.sub(r"\b(\w+)\s+\1\b", r"\1", text, flags=re.IGNORECASE)

        # Handle cases where a word is repeated many times
        words = text.split()
        if len(words) > 10:  # Only apply to longer texts
            # Check if the first few words are repeated many times
            unique_words = []
            for word in words:
                word_lower = word.lower()
                # Only add if it's not a duplicate of the last few words
                if len(unique_words) < 3 or word_lower not in [
                    w.lower() for w in unique_words[-3:]
                ]:
                    unique_words.append(word)
            text = " ".join(unique_words)

        return text.strip()

    def _match_ingredients(
        self, generated_ingredients: list[str], inventory_ingredients: list[str]
    ) -> list[str]:
        """
        Match generated ingredients with inventory ingredients to ensure exact names.
        This function tries to find the closest match from inventory ingredients
        for each generated ingredient.
        """
        matched_ingredients = []

        # Convert inventory ingredients to lowercase for comparison
        inventory_lower = [item.lower() for item in inventory_ingredients]

        for gen_ing in generated_ingredients:
            # Clean the generated ingredient
            gen_ing_clean = re.sub(r"^\s*[\d\.\)\-\*]+\s*", "", gen_ing).strip()
            # Remove common measurements and descriptors
            gen_ing_clean = re.sub(
                r"\d+\s*(grams?|cups?|tbsp|tsp|ounces?|oz|lbs?|pounds?|slices?|pieces?|cloves?|inch(es)?|cubes?|chunks?)",
                "",
                gen_ing_clean,
                flags=re.IGNORECASE,
            )
            gen_ing_clean = re.sub(
                r"\(.*?\)", "", gen_ing_clean
            )  # Remove anything in parentheses
            gen_ing_clean = gen_ing_clean.strip()

            # Convert to lowercase for comparison
            gen_ing_lower = gen_ing_clean.lower()

            # Try to find an exact match first
            matched = False
            for i, inv_ing in enumerate(inventory_lower):
                if inv_ing in gen_ing_lower or gen_ing_lower in inv_ing:
                    matched_ingredients.append(inventory_ingredients[i])
                    matched = True
                    break

            # If no exact match, add the cleaned ingredient
            if not matched:
                # Try to find a partial match
                for i, inv_ing in enumerate(inventory_lower):
                    if inv_ing in gen_ing_lower or gen_ing_lower in inv_ing:
                        matched_ingredients.append(inventory_ingredients[i])
                        matched = True
                        break

                # If still no match, add the original generated ingredient
                if not matched:
                    matched_ingredients.append(gen_ing_clean)

        # Remove duplicates while preserving order
        seen = set()
        unique_ingredients = []
        for item in matched_ingredients:
            if item not in seen:
                seen.add(item)
                unique_ingredients.append(item)

        return unique_ingredients

    def get_recipes_by_ingredients(
        self,
        ingredients: list[str],
        fitness_goal: str = "maintain",
        inventory_items: list[Inventory] = None,
    ) -> dict:
        try:
            recipe_data = self.recipe_generator.generate_recipe(
                ingredients, fitness_goal, inventory_items
            )
        except RuntimeError as e:
            raise HTTPException(status_code=500, detail=str(e))

        # Extract data from the dictionary
        title = recipe_data["title"]
        calories = recipe_data["calories"]
        protein = recipe_data["protein"]
        carbs = recipe_data["carbs"]
        fats = recipe_data["fats"]
        generated_ingredients = recipe_data["ingredients"]
        directions = recipe_data["directions"]

        # Clean repetitive text in title
        title = self._clean_repetitive_text(title)

        # Match generated ingredients with inventory ingredients
        matched_ingredients = self._match_ingredients(
            generated_ingredients, ingredients
        )

        return {
            "title": title,
            "calories": calories,
            "protein": protein,
            "carbs": carbs,
            "fats": fats,
            "ingredients": matched_ingredients,
            "directions": directions,
        }

    def generate_recipe_from_inventory(self, db: Session, user_id: uuid.UUID) -> dict:
        # Fetch inventory items for the user
        inventory_items = db.query(Inventory).filter(Inventory.user_id == user_id).all()
        ingredients = [item.name for item in inventory_items if item.quantity > 0]

        if not ingredients:
            raise HTTPException(
                status_code=400, detail="No ingredients available in inventory"
            )

        # Fetch user's fitness goal
        user = db.query(User).filter(User.id == user_id).first()
        fitness_goal = (
            user.fitness_goal.value if user and user.fitness_goal else "maintain"
        )

        # Generate recipe using the existing method
        recipe_data = self.get_recipes_by_ingredients(
            ingredients, fitness_goal, inventory_items
        )

        # Save the generated recipe to the database
        generated_recipe = GeneratedRecipe(
            user_id=user_id,
            title=recipe_data["title"],
            ingredients=recipe_data["ingredients"],
            directions=recipe_data["directions"],
        )
        db.add(generated_recipe)
        db.commit()
        db.refresh(generated_recipe)

        return recipe_data

    def get_generated_recipes(
        self, db: Session, user_id: uuid.UUID
    ) -> list[GeneratedRecipe]:
        return (
            db.query(GeneratedRecipe).filter(GeneratedRecipe.user_id == user_id).all()
        )
