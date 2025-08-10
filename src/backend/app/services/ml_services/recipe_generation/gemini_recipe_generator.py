from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from pydantic import BaseModel, Field
from app.core.config import settings
from typing import List, Optional
from app.models.inventory import Inventory
import json


class RecipeSchema(BaseModel):
    title: str = Field(description="Recipe title")
    calories: int = Field(description="Calories per serving")
    protein: float = Field(description="Protein per serving")
    carbs: float = Field(description="Carbs per serving")
    fats: float = Field(description="Fats per serving")
    ingredients: List[str] = Field(description="List of ingredients")
    directions: str = Field(description="Step-by-step cooking instructions")


class GeminiRecipeGenerator:
    def __init__(self):
        """
        Initialize the GEMINI recipe generator with LangChain integration.
        """
        try:
            # Initialize the GEMINI model through LangChain with structured output
            self.model = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash-lite",
                google_api_key=settings.GEMINI_API_KEY,
                temperature=0.7,
                max_tokens=1024,
            ).with_structured_output(RecipeSchema)

            # Create prompt template for recipe generation
            self.prompt_template = PromptTemplate(
                input_variables=["ingredients", "fitness_goal", "inventory_details"],
                template="""You are a professional chef and nutritionist. Generate a healthy recipe using the following ingredients: {ingredients}.

The recipe should be appropriate for someone with the fitness goal: {fitness_goal}.

Available ingredients with their nutritional information:
{inventory_details}

Make sure to:
1. Use only the provided ingredients when possible
2. Provide clear, concise cooking instructions
3. Keep the recipe healthy and aligned with the fitness goal
4. Consider the nutritional values and quantities when creating the recipe""",
            )

            # Create the chain
            self.chain = self.prompt_template | self.model
        except Exception as e:
            raise RuntimeError(f"Failed to initialize GEMINI recipe generator: {e}")

    def generate_recipe(
        self,
        ingredients: List[str],
        fitness_goal: str = "maintain",
        inventory_items: Optional[List[Inventory]] = None,
    ) -> dict:
        """
        Generate a recipe using GEMINI based on provided ingredients and fitness goal.

        Args:
            ingredients: List of ingredient names
            fitness_goal: User's fitness goal (gain, lose, maintain)
            inventory_items: List of inventory items with nutritional details

        Returns:
            Dictionary with recipe data (title, ingredients, directions)
        """
        try:
            # Format ingredients as a comma-separated string
            ingredients_str = ", ".join(ingredients)

            # Format inventory details with nutritional information
            inventory_details = "No detailed inventory information available"
            if inventory_items:
                inventory_details_lines = []
                for item in inventory_items:
                    if item.quantity > 0:  # Only include items with available quantity
                        details = f"- {item.name}: {item.quantity} {item.serving_size_unit or 'units'}"
                        if item.calories_per_serving is not None:
                            details += (
                                f", {item.calories_per_serving} calories per serving"
                            )
                        if item.protein_g_per_serving is not None:
                            details += f", {item.protein_g_per_serving}g protein"
                        if item.carbs_g_per_serving is not None:
                            details += f", {item.carbs_g_per_serving}g carbs"
                        if item.fats_g_per_serving is not None:
                            details += f", {item.fats_g_per_serving}g fats"
                        inventory_details_lines.append(details)
                if inventory_details_lines:
                    inventory_details = "\n".join(inventory_details_lines)

            # Generate recipe using the chain
            recipe_data = self.chain.invoke(
                {
                    "ingredients": ingredients_str,
                    "fitness_goal": fitness_goal,
                    "inventory_details": inventory_details,
                }
            )

            # Convert to dictionary
            return {
                "title": recipe_data.title,
                "calories": recipe_data.calories,
                "protein": recipe_data.protein,
                "carbs": recipe_data.carbs,
                "fats": recipe_data.fats,
                "ingredients": recipe_data.ingredients,
                "directions": recipe_data.directions,
            }
        except Exception as e:
            raise RuntimeError(f"Failed to generate recipe with GEMINI: {e}")
