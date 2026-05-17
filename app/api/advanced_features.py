"""
Unified API for Advanced Features
Combines Recipe Generator, Food Scanner, Wearable Integration into REST endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

# Import services
from app.services.recipe_generator import recipe_service, RecipeRequest, DietType, MealType
from app.services.food_scanner import barcode_service, image_service
from app.services.wearable_integration import wearable_service, WearableProvider

router = APIRouter(prefix="/api/v1/advanced", tags=["Advanced Features"])

# ==================== RECIPE GENERATOR ENDPOINTS ====================

class GenerateRecipeRequest(BaseModel):
    diet_type: str
    meal_type: str
    available_ingredients: List[str] = []
    excluded_ingredients: List[str] = []
    max_calories: Optional[int] = None
    max_prep_time: Optional[int] = None
    servings: int = 1

@router.post("/recipes/generate")
async def generate_recipe(request: GenerateRecipeRequest, user_id: str = "user_123"):
    """
    Generate a personalized recipe based on diet, ingredients, and goals.
    """
    try:
        recipe_request = RecipeRequest(
            user_id=user_id,
            diet_type=DietType(request.diet_type),
            meal_type=MealType(request.meal_type),
            available_ingredients=request.available_ingredients,
            excluded_ingredients=request.excluded_ingredients,
            max_calories=request.max_calories,
            max_prep_time=request.max_prep_time,
            servings=request.servings
        )
        
        recipe = recipe_service.generate_recipe(recipe_request)
        
        return {
            "success": True,
            "data": recipe.dict(),
            "message": f"Generated {recipe.title} successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/recipes/substitutions/{ingredient}")
async def get_substitutions(ingredient: str, diet_type: str = "mediterranean"):
    """Get healthy substitutions for an ingredient"""
    try:
        subs = recipe_service.suggest_substitutions(ingredient, DietType(diet_type))
        return {
            "success": True,
            "ingredient": ingredient,
            "diet": diet_type,
            "substitutions": subs
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ==================== BARCODE SCANNER ENDPOINTS ====================

@router.get("/food/barcode/{barcode}")
async def lookup_barcode(barcode: str):
    """Lookup product information by barcode"""
    result = barcode_service.lookup_barcode(barcode)
    
    if not result:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {
        "success": True,
        "data": result.dict()
    }

@router.get("/food/search")
async def search_food(q: str):
    """Search food products by name"""
    results = barcode_service.search_product(q)
    return {
        "success": True,
        "count": len(results),
        "data": [r.dict() for r in results]
    }

@router.post("/food/scan-image")
async def scan_food_image(file: UploadFile = File(...)):
    """
    Identify food from uploaded image.
    Accepts image files (jpg, png).
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # Read image bytes
        image_data = await file.read()
        
        # Analyze image
        results = image_service.identify_food_from_image(image_data)
        
        return {
            "success": True,
            "count": len(results),
            "data": [r.dict() for r in results],
            "message": f"Identified {len(results)} food items"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image analysis failed: {str(e)}")

# ==================== WEARABLE INTEGRATION ENDPOINTS ====================

@router.post("/wearables/connect/{provider}")
async def connect_wearable(provider: str, auth_token: str = Form(...), user_id: str = "user_123"):
    """Connect a wearable device to user account"""
    try:
        provider_enum = WearableProvider(provider)
        success = wearable_service.connect_device(user_id, provider_enum, auth_token)
        
        if success:
            return {
                "success": True,
                "message": f"{provider} connected successfully",
                "provider": provider
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to connect device")
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid provider. Choose from: {[p.value for p in WearableProvider]}")

@router.delete("/wearables/disconnect")
async def disconnect_wearable(user_id: str = "user_123"):
    """Disconnect wearable device"""
    success = wearable_service.disconnect_device(user_id)
    
    if success:
        return {"success": True, "message": "Device disconnected"}
    else:
        raise HTTPException(status_code=404, detail="No device connected")

@router.get("/wearables/status")
async def wearable_status(user_id: str = "user_123"):
    """Check wearable connection status"""
    is_connected = wearable_service.is_connected(user_id)
    provider = wearable_service.get_provider(user_id)
    
    return {
        "success": True,
        "connected": is_connected,
        "provider": provider.value if provider else None
    }

@router.get("/wearables/sync")
async def sync_wearable_data(
    days: int = 1,
    user_id: str = "user_123"
):
    """Sync data from connected wearable"""
    from datetime import timedelta
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    result = wearable_service.sync_data(user_id, start_date, end_date)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {
        "success": True,
        "data": result
    }

@router.get("/wearables/heart-rate")
async def get_heart_rate(user_id: str = "user_123"):
    """Get real-time heart rate"""
    hr = wearable_service.get_real_time_heart_rate(user_id)
    
    if hr is None:
        raise HTTPException(status_code=400, detail="No device connected or heart rate unavailable")
    
    return {
        "success": True,
        "heart_rate": hr,
        "unit": "bpm",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/wearables/goals/progress")
async def get_goals_progress(goal_steps: int = 10000, user_id: str = "user_123"):
    """Get progress towards daily activity goals"""
    result = wearable_service.calculate_activity_goals_progress(user_id, goal_steps)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {
        "success": True,
        "data": result
    }

# ==================== COMBINED HEALTH INSIGHTS ====================

@router.get("/insights/daily-summary")
async def get_daily_health_summary(user_id: str = "user_123"):
    """
    Get comprehensive daily health summary combining:
    - Wearable data (if connected)
    - Generated meal suggestions
    - Activity recommendations
    """
    summary = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "wearable_data": None,
        "meal_suggestions": [],
        "recommendations": []
    }
    
    # Get wearable data if connected
    if wearable_service.is_connected(user_id):
        today = datetime.now()
        wearable_data = wearable_service.sync_data(user_id, today, today)
        if "error" not in wearable_data:
            summary["wearable_data"] = wearable_data["summary"]
            
            # Add recommendations based on data
            steps = wearable_data["summary"].get("steps", 0)
            if steps < 5000:
                summary["recommendations"].append("🚶 Try to walk more today! Aim for 10k steps.")
            if wearable_data["summary"].get("sleep_hours", 8) < 7:
                summary["recommendations"].append("😴 Consider getting more sleep tonight.")
    
    # Generate meal suggestion
    try:
        from app.services.recipe_generator import MealType, DietType
        recipe_req = RecipeRequest(
            user_id=user_id,
            diet_type=DietType.MEDITERRANEAN,
            meal_type=MealType.DINNER,
            servings=1
        )
        recipe = recipe_service.generate_recipe(recipe_req)
        summary["meal_suggestions"].append({
            "meal": "Dinner",
            "recipe": recipe.title,
            "calories": recipe.calories
        })
    except:
        pass
    
    return {
        "success": True,
        "data": summary
    }
