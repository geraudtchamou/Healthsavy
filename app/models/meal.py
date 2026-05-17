from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Text, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.models.enums import MealCategory


class MealPlan(Base):
    __tablename__ = "meal_plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(Enum(MealCategory), nullable=False)
    
    # Nutritional info
    total_calories = Column(Integer, nullable=True)
    total_protein = Column(Float, nullable=True)
    total_carbs = Column(Float, nullable=True)
    total_fats = Column(Float, nullable=True)
    
    # Meals structure
    meals = Column(JSON, nullable=False)  # [{name, time, foods: [{name, calories, protein, carbs, fats}]}]
    grocery_list = Column(JSON, nullable=True)  # List of ingredients
    
    # Creator
    creator_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    creator = relationship("User", back_populates="meal_plans")
    
    # Visibility
    is_public = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    
    # Engagement
    saves_count = Column(Integer, default=0)
    rating = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FoodItem(Base):
    __tablename__ = "food_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Nutritional information (per 100g or per serving)
    calories = Column(Float, nullable=True)
    protein = Column(Float, nullable=True)  # grams
    carbs = Column(Float, nullable=True)  # grams
    fats = Column(Float, nullable=True)  # grams
    fiber = Column(Float, nullable=True)  # grams
    sugar = Column(Float, nullable=True)  # grams
    sodium = Column(Float, nullable=True)  # mg
    
    # Vitamins and minerals
    vitamins = Column(JSON, nullable=True)  # {vitamin_a, vitamin_c, vitamin_d, etc.}
    minerals = Column(JSON, nullable=True)  # {iron, calcium, magnesium, etc.}
    
    # Metadata
    serving_size = Column(String(50), nullable=True)  # e.g., "100g", "1 cup"
    allergens = Column(JSON, nullable=True)  # List of allergens
    tags = Column(JSON, nullable=True)  # List of tags
    
    # Source
    is_verified = Column(Boolean, default=False)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
