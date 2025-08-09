from transformers import T5ForConditionalGeneration, AutoTokenizer
from app.core.config import settings

class RecipeGenerator:
    def __init__(self):
        try:
            self.model = T5ForConditionalGeneration.from_pretrained(settings.RECIPE_MODEL_PATH)
            self.tokenizer = AutoTokenizer.from_pretrained(settings.RECIPE_MODEL_PATH)
            # Special tokens and mapping as per the official implementation
            self.special_tokens = self.tokenizer.all_special_tokens
            self.tokens_map = {
                "<sep>": "--",
                "<section>": "\n"
            }
        except Exception as e:
            raise RuntimeError(f"Failed to load recipe generation model: {e}")

    def _skip_special_tokens(self, text):
        """Remove special tokens from text"""
        for token in self.special_tokens:
            text = text.replace(token, "")
        return text

    def _postprocess_recipe(self, text):
        """Postprocess the generated recipe text according to official implementation"""
        # Remove special tokens
        text = self._skip_special_tokens(text)
        
        # Apply token mappings
        for k, v in self.tokens_map.items():
            text = text.replace(k, v)
            
        return text

    def generate_recipe(self, ingredients: list[str]) -> str:
        # Using the official prefix and generation parameters
        prefix = "items: "
        generation_kwargs = {
            "max_length": 512,
            "min_length": 64,
            "no_repeat_ngram_size": 3,
            "do_sample": True,
            "top_k": 60,
            "top_p": 0.95
        }
        
        # Format ingredients as a comma-separated string
        ingredients_str = ", ".join(ingredients)
        prompt = f"{prefix}{ingredients_str}"
        
        try:
            inputs = self.tokenizer(
                prompt, 
                max_length=256, 
                padding="max_length", 
                truncation=True, 
                return_tensors="pt"
            )
            
            output = self.model.generate(
                input_ids=inputs.input_ids, 
                attention_mask=inputs.attention_mask,
                **generation_kwargs
            )
            
            # Decode and postprocess the output
            recipe = self.tokenizer.decode(output[0], skip_special_tokens=False)
            recipe = self._postprocess_recipe(recipe)
            
            return recipe
        except Exception as e:
            raise RuntimeError(f"Failed to generate recipe: {e}")

