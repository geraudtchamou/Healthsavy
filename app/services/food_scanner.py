"""
Barcode Scanner & Food Recognition Service
Handles barcode lookups and image-based food identification.
"""
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
import hashlib
import random

class BarcodeResult(BaseModel):
    barcode: str
    product_name: str
    brand: str
    category: str
    calories_per_100g: float
    macros: Dict[str, float]
    ingredients: List[str]
    allergens: List[str]
    health_score: int  # 0-100 (Nutri-Score style)
    verified: bool

class ImageFoodResult(BaseModel):
    food_name: str
    confidence: float
    estimated_calories: float
    estimated_macros: Dict[str, float]
    portion_size: str
    suggestions: List[str]

class BarcodeService:
    def __init__(self):
        # Mock database of common barcodes
        self.barcode_db = self._load_mock_db()
    
    def _load_mock_db(self) -> Dict[str, Dict]:
        """Load mock barcode database"""
        return {
            "5449000000996": {
                "product_name": "Coca-Cola Classic",
                "brand": "Coca-Cola",
                "category": "Beverages",
                "calories_per_100g": 42,
                "macros": {"protein": 0, "carbs": 10.6, "fat": 0, "sugar": 10.6},
                "ingredients": ["Carbonated Water", "Sugar", "Caramel Color", "Phosphoric Acid"],
                "allergens": [],
                "health_score": 15,
                "verified": True
            },
            "5000159484322": {
                "product_name": "Greek Yogurt Natural",
                "brand": "Fage",
                "category": "Dairy",
                "calories_per_100g": 97,
                "macros": {"protein": 9.0, "carbs": 3.4, "fat": 5.0, "sugar": 3.4},
                "ingredients": ["Pasteurized Milk", "Live Cultures"],
                "allergens": ["Milk"],
                "health_score": 78,
                "verified": True
            },
            "7622210100541": {
                "product_name": "Dark Chocolate 70%",
                "brand": "Lindt",
                "category": "Snacks",
                "calories_per_100g": 560,
                "macros": {"protein": 8.0, "carbs": 45.0, "fat": 38.0, "sugar": 24.0},
                "ingredients": ["Cocoa Mass", "Sugar", "Cocoa Butter", "Vanilla"],
                "allergens": ["May contain milk", "May contain nuts"],
                "health_score": 45,
                "verified": True
            }
        }

    def lookup_barcode(self, barcode: str) -> Optional[BarcodeResult]:
        """Lookup product by barcode"""
        # Normalize barcode (remove spaces/dashes)
        clean_barcode = barcode.replace("-", "").replace(" ", "")
        
        if clean_barcode in self.barcode_db:
            data = self.barcode_db[clean_barcode]
            return BarcodeResult(barcode=clean_barcode, **data)
        
        # Simulate external API call for unknown barcodes
        # In production, this would call OpenFoodFacts or similar
        return self._generate_mock_result(clean_barcode)

    def _generate_mock_result(self, barcode: str) -> BarcodeResult:
        """Generate a mock result for unknown barcodes (simulation)"""
        return BarcodeResult(
            barcode=barcode,
            product_name=f"Product {barcode[-4:]}",
            brand="Unknown Brand",
            category="General",
            calories_per_100g=random.randint(50, 300),
            macros={"protein": random.uniform(2, 15), "carbs": random.uniform(10, 40), "fat": random.uniform(1, 20)},
            ingredients=["Ingredient A", "Ingredient B"],
            allergens=[],
            health_score=random.randint(30, 70),
            verified=False
        )

    def search_product(self, query: str) -> List[BarcodeResult]:
        """Search products by name"""
        results = []
        query_lower = query.lower()
        
        for code, data in self.barcode_db.items():
            if query_lower in data["product_name"].lower() or query_lower in data["brand"].lower():
                results.append(BarcodeResult(barcode=code, **data))
        
        return results

class ImageRecognitionService:
    def __init__(self):
        self.food_models = ["CNN-Food-v2", "ResNet-Food", "MobileNet-Food"]
        
    def identify_food_from_image(self, image_data: bytes, user_context: Optional[Dict] = None) -> List[ImageFoodResult]:
        """
        Identify food from image bytes.
        In production, this calls a computer vision model or API (Google Vision, Clarifai, custom model).
        """
        # Simulate image analysis
        # In reality, you'd process the image tensor through a model
        
        # Mock results based on common foods
        mock_foods = [
            {
                "food_name": "Grilled Chicken Salad",
                "confidence": 0.92,
                "estimated_calories": 350,
                "estimated_macros": {"protein": 35, "carbs": 12, "fat": 18},
                "portion_size": "Medium Bowl (300g)",
                "suggestions": ["Add more leafy greens", "Use light dressing"]
            },
            {
                "food_name": "Avocado Toast",
                "confidence": 0.88,
                "estimated_calories": 280,
                "estimated_macros": {"protein": 8, "carbs": 25, "fat": 18},
                "portion_size": "2 Slices",
                "suggestions": ["Use whole grain bread", "Add poached egg for protein"]
            },
            {
                "food_name": "Smoothie Bowl",
                "confidence": 0.85,
                "estimated_calories": 420,
                "estimated_macros": {"protein": 12, "carbs": 65, "fat": 14},
                "portion_size": "Large Bowl (400g)",
                "suggestions": ["Reduce banana content", "Add chia seeds"]
            }
        ]
        
        # Return top 3 predictions
        return [ImageFoodResult(**food) for food in mock_foods[:3]]

    def estimate_portion(self, image_data: bytes, food_name: str) -> Dict[str, Any]:
        """Estimate portion size from image"""
        # Simulate depth/volume estimation
        return {
            "food_name": food_name,
            "estimated_weight_g": random.randint(200, 500),
            "volume_ml": random.randint(200, 600),
            "confidence": 0.75,
            "reference_object": "Standard plate detected"
        }

# Singleton instances
barcode_service = BarcodeService()
image_service = ImageRecognitionService()
