from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.enums import MealCategory, WorkoutLevel, ExerciseCategory


class MealPlanBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category: MealCategory
    total_calories: Optional[int] = None
    total_protein: Optional[float] = None
    total_carbs: Optional[float] = None
    total_fats: Optional[float] = None
    meals: dict  # [{name, time, foods: [{name, calories, protein, carbs, fats}]}]
    grocery_list: Optional[List[str]] = None
    is_public: bool = False
    is_premium: bool = False


class MealPlanCreate(MealPlanBase):
    pass


class MealPlanUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    meals: Optional[dict] = None
    grocery_list: Optional[List[str]] = None
    is_public: Optional[bool] = None
    is_premium: Optional[bool] = None


class MealPlanResponse(MealPlanBase):
    id: int
    creator_id: int
    saves_count: int
    rating: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class FoodItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    calories: Optional[float] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fats: Optional[float] = None
    fiber: Optional[float] = None
    sugar: Optional[float] = None
    sodium: Optional[float] = None
    vitamins: Optional[dict] = None
    minerals: Optional[dict] = None
    serving_size: Optional[str] = None
    allergens: Optional[List[str]] = None
    tags: Optional[List[str]] = None


class FoodItemCreate(FoodItemBase):
    pass


class FoodItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    calories: Optional[float] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fats: Optional[float] = None
    vitamins: Optional[dict] = None
    minerals: Optional[dict] = None
    allergens: Optional[List[str]] = None
    tags: Optional[List[str]] = None


class FoodItemResponse(FoodItemBase):
    id: int
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class WorkoutPlanBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    level: WorkoutLevel
    duration_minutes: Optional[int] = None
    calories_burned: Optional[int] = None
    equipment_needed: Optional[List[str]] = None
    exercises: dict  # [{name, sets, reps, duration, rest_time, video_url}]
    is_public: bool = False
    is_premium: bool = False


class WorkoutPlanCreate(WorkoutPlanBase):
    pass


class WorkoutPlanUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    exercises: Optional[dict] = None
    is_public: Optional[bool] = None
    is_premium: Optional[bool] = None


class WorkoutPlanResponse(WorkoutPlanBase):
    id: int
    creator_id: int
    saves_count: int
    rating: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ExerciseBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category: ExerciseCategory
    difficulty: WorkoutLevel
    equipment_needed: Optional[List[str]] = None
    muscle_groups: Optional[List[str]] = None
    instructions: Optional[dict] = None
    video_url: Optional[str] = None
    image_url: Optional[str] = None
    default_sets: Optional[int] = None
    default_reps: Optional[int] = None
    default_duration_seconds: Optional[int] = None
    default_rest_seconds: Optional[int] = None


class ExerciseCreate(ExerciseBase):
    pass


class ExerciseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    instructions: Optional[dict] = None
    video_url: Optional[str] = None
    image_url: Optional[str] = None
    default_sets: Optional[int] = None
    default_reps: Optional[int] = None


class ExerciseResponse(ExerciseBase):
    id: int
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class WorkoutLogCreate(BaseModel):
    workout_plan_id: Optional[int] = None
    duration_minutes: Optional[int] = None
    calories_burned: Optional[int] = None
    exercises_completed: Optional[dict] = None
    difficulty_rating: Optional[int] = None
    notes: Optional[str] = None


class WorkoutLogResponse(BaseModel):
    id: int
    user_id: int
    workout_plan_id: Optional[int] = None
    date: datetime
    duration_minutes: Optional[int] = None
    calories_burned: Optional[int] = None
    exercises_completed: Optional[dict] = None
    difficulty_rating: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
