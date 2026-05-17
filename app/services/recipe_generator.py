"""
Smart Recipe Generator Service
Generates personalized recipes based on user profile, goals, and available ingredients.
"""
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum
import random
import math

class DietType(str, Enum):
    VEGAN = "vegan"
    KETO = "keto"
    PALEO = "paleo"
    MEDITERRANEAN = "mediterranean"
    DIABETIC_FRIENDLY = "diabetic_friendly"
    HIGH_PROTEIN = "high_protein"
    GLUTEN_FREE = "gluten_free"

class MealType(str, Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"

class Ingredient(BaseModel):
    name: str
    quantity: float
    unit: str
    calories: float
    protein: float
    carbs: float
    fat: float

class RecipeRequest(BaseModel):
    user_id: str
    diet_type: DietType
    meal_type: MealType
    available_ingredients: List[str] = []
    excluded_ingredients: List[str] = []
    max_calories: Optional[int] = None
    max_prep_time: Optional[int] = None  # minutes
    servings: int = 1

class RecipeResponse(BaseModel):
    id: str
    title: str
    description: str
    prep_time: int
    cook_time: int
    servings: int
    calories: float
    macros: Dict[str, float]  # protein, carbs, fat
    ingredients: List[Dict[str, Any]]
    instructions: List[str]
    tags: List[str]
    match_score: float  # How well it matches user prefs (0-1)
    source: str  # "generated", "database", "community"

class SmartRecipeService:
    def __init__(self):
        # Mock database of base recipes/templates
        self.recipe_templates = self._load_templates()
        
    def _load_templates(self) -> Dict:
        """Load base recipe templates for generation logic"""
        return {
            "keto": {
                "breakfast": ["Avocado Egg Boats", "Keto Smoothie Bowl", "Bacon & Spinach Frittata"],
                "lunch": ["Cobb Salad with Chicken", "Zucchini Noodle Carbonara", "Tuna Stuffed Avocado"],
                "dinner": ["Salmon with Asparagus", "Steak with Cauliflower Mash", "Chicken Thighs with Broccoli"],
                "snack": ["Cheese Crisps", "Macadamia Nuts", "Celery with Almond Butter"]
            },
            "vegan": {
                "breakfast": ["Tofu Scramble", "Oatmeal with Berries", "Green Smoothie"],
                "lunch": ["Quinoa Buddha Bowl", "Lentil Soup", "Chickpea Salad Wrap"],
                "dinner": ["Stir-Fry Tofu with Veggies", "Sweet Potato Curry", "Mushroom Risotto"],
                "snack": ["Hummus with Carrots", "Apple Slices with Peanut Butter", "Energy Balls"]
            },
            "high_protein": {
                "breakfast": ["Greek Yogurt Parfait", "Protein Pancakes", "Egg White Omelet"],
                "lunch": ["Grilled Chicken Salad", "Turkey Burger Bowl", "Shrimp Quinoa Bowl"],
                "dinner": ["Lean Beef Stir-Fry", "Baked Cod with Rice", "Chicken Breast with Sweet Potato"],
                "snack": ["Protein Shake", "Hard Boiled Eggs", "Cottage Cheese"]
            }
            # Add more diet types as needed
        }

    def generate_recipe(self, request: RecipeRequest) -> RecipeResponse:
        """
        Main method to generate a recipe based on constraints.
        In production, this would call an LLM or complex algorithm.
        Here we use heuristic generation + template selection.
        """
        # 1. Select base template
        diet_recipes = self.recipe_templates.get(request.diet_type.value, self.recipe_templates["mediterranean"])
        meal_options = diet_recipes.get(request.meal_type.value, diet_recipes["dinner"])
        
        base_title = random.choice(meal_options)
        
        # 2. Customize based on available ingredients
        matched_ingredients = []
        match_score = 0.5 # Base score
        
        if request.available_ingredients:
            # Simulate matching logic
            for ing in request.available_ingredients:
                if ing.lower() in base_title.lower() or ing.lower() in ["egg", "chicken", "tofu", "avocado"]:
                    matched_ingredients.append(ing)
                    match_score += 0.1
            
            if len(matched_ingredients) >= 2:
                match_score += 0.2
                base_title = f"{request.available_ingredients[0].title()} {base_title}"

        # 3. Calculate Macros based on diet type
        macros = self._calculate_macros(request.diet_type, request.max_calories or 500)
        
        # 4. Generate Instructions
        instructions = self._generate_instructions(base_title, request.servings)
        
        # 5. Construct Response
        return RecipeResponse(
            id=f"rec_{random.randint(10000, 99999)}",
            title=base_title,
            description=f"A delicious {request.diet_type.value} {request.meal_type.value} optimized for your goals.",
            prep_time=random.randint(10, 20),
            cook_time=random.randint(15, 30),
            servings=request.servings,
            calories=macros["calories"],
            macros={
                "protein": macros["protein"],
                "carbs": macros["carbs"],
                "fat": macros["fat"]
            },
            ingredients=self._generate_ingredients(base_title, request.servings, matched_ingredients),
            instructions=instructions,
            tags=[request.diet_type.value, request.meal_type.value, "healthy", "homemade"],
            match_score=min(match_score, 1.0),
            source="generated"
        )

    def _calculate_macros(self, diet: DietType, target_calories: int) -> Dict[str, float]:
        """Calculate macro split based on diet type"""
        ratios = {
            DietType.KETO: {"protein": 0.25, "carbs": 0.05, "fat": 0.70},
            DietType.VEGAN: {"protein": 0.20, "carbs": 0.50, "fat": 0.30},
            DietType.HIGH_PROTEIN: {"protein": 0.40, "carbs": 0.30, "fat": 0.30},
            DietType.MEDITERRANEAN: {"protein": 0.25, "carbs": 0.45, "fat": 0.30}
        }
        
        r = ratios.get(diet, ratios[DietType.MEDITERRANEAN])
        
        # Calorie per gram: Protein=4, Carbs=4, Fat=9
        protein_g = (target_calories * r["protein"]) / 4
        carbs_g = (target_calories * r["carbs"]) / 4
        fat_g = (target_calories * r["fat"]) / 9
        
        return {
            "calories": target_calories,
            "protein": round(protein_g, 1),
            "carbs": round(carbs_g, 1),
            "fat": round(fat_g, 1)
        }

    def _generate_instructions(self, title: str, servings: int) -> List[str]:
        """Generate generic cooking steps"""
        return [
            f"Gather all ingredients for {title}.",
            "Prepare vegetables by washing and chopping them into bite-sized pieces.",
            "Heat a pan or pot over medium heat with a small amount of healthy oil.",
            f"Cook primary protein until fully done (internal temp 165°F for poultry).",
            "Combine all ingredients and season with salt, pepper, and herbs to taste.",
            f"Divide into {servings} servings and garnish if desired.",
            "Serve immediately and enjoy your healthy meal!"
        ]

    def _generate_ingredients(self, title: str, servings: int, matched: List[str]) -> List[Dict]:
        """Generate ingredient list"""
        base_ingredients = [
            {"name": "Olive Oil", "qty": 1, "unit": "tbsp", "cal": 120, "prot": 0, "carb": 0, "fat": 14},
            {"name": "Sea Salt", "qty": 0.5, "unit": "tsp", "cal": 0, "prot": 0, "carb": 0, "fat": 0},
            {"name": "Black Pepper", "qty": 0.25, "unit": "tsp", "cal": 2, "prot": 0, "carb": 0.5, "fat": 0},
            {"name": "Fresh Herbs", "qty": 1, "unit": "tbsp", "cal": 5, "prot": 0.2, "carb": 1, "fat": 0.1}
        ]
        
        # Add matched ingredients
        for m in matched:
            base_ingredients.append({"name": m.title(), "qty": 100 * servings, "unit": "g", "cal": 150, "prot": 20, "carb": 5, "fat": 5})
            
        # Fillers if not enough ingredients
        if len(base_ingredients) < 5:
            base_ingredients.append({"name": "Mixed Vegetables", "qty": 150 * servings, "unit": "g", "cal": 50, "prot": 2, "carb": 10, "fat": 0})
            
        return base_ingredients

    def suggest_substitutions(self, ingredient: str, diet: DietType) -> List[str]:
        """Suggest healthy substitutions for ingredients"""
        subs = {
            "rice": ["cauliflower rice", "quinoa", "broccoli rice"],
            "pasta": ["zucchini noodles", "shirataki noodles", "lentil pasta"],
            "sugar": ["stevia", "monk fruit", "erythritol"],
            "milk": ["almond milk", "oat milk", "coconut milk"],
            "beef": ["lean turkey", "tofu", "tempeh"]
        }
        return subs.get(ingredient.lower(), ["organic version", "fresh alternative"])

# Singleton instance
recipe_service = SmartRecipeService()
