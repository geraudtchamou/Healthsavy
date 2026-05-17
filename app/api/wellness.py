from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.core.database import get_db
from app.models.meal import MealPlan, FoodItem
from app.models.workout import WorkoutPlan, Exercise, WorkoutLog
from app.models.user import User
from app.schemas.wellness import (
    MealPlanCreate,
    MealPlanUpdate,
    MealPlanResponse,
    FoodItemCreate,
    FoodItemUpdate,
    FoodItemResponse,
    WorkoutPlanCreate,
    WorkoutPlanUpdate,
    WorkoutPlanResponse,
    ExerciseCreate,
    ExerciseUpdate,
    ExerciseResponse,
    WorkoutLogCreate,
    WorkoutLogResponse,
)

router = APIRouter(prefix="/wellness", tags=["Wellness"])


# ==================== MEAL PLANS ====================

@router.get("/meal-plans", response_model=List[MealPlanResponse])
async def get_meal_plans(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    is_public: Optional[bool] = None,
    creator_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get meal plans with optional filtering."""
    query = select(MealPlan)
    
    if category:
        query = query.where(MealPlan.category == category)
    
    if is_public is not None:
        query = query.where(MealPlan.is_public == is_public)
    
    if creator_id:
        query = query.where(MealPlan.creator_id == creator_id)
    
    query = query.order_by(MealPlan.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    meal_plans = result.scalars().all()
    
    return meal_plans


@router.post("/meal-plans", response_model=MealPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_meal_plan(
    meal_plan_data: MealPlanCreate,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Create a new meal plan."""
    new_meal_plan = MealPlan(
        name=meal_plan_data.name,
        description=meal_plan_data.description,
        category=meal_plan_data.category,
        total_calories=meal_plan_data.total_calories,
        total_protein=meal_plan_data.total_protein,
        total_carbs=meal_plan_data.total_carbs,
        total_fats=meal_plan_data.total_fats,
        meals=meal_plan_data.meals,
        grocery_list=meal_plan_data.grocery_list,
        creator_id=user_id,
        is_public=meal_plan_data.is_public,
        is_premium=meal_plan_data.is_premium,
    )
    
    db.add(new_meal_plan)
    await db.commit()
    await db.refresh(new_meal_plan)
    
    return new_meal_plan


@router.get("/meal-plans/{plan_id}", response_model=MealPlanResponse)
async def get_meal_plan(plan_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific meal plan by ID."""
    result = await db.execute(select(MealPlan).where(MealPlan.id == plan_id))
    meal_plan = result.scalar_one_or_none()
    
    if not meal_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan not found"
        )
    
    return meal_plan


@router.put("/meal-plans/{plan_id}", response_model=MealPlanResponse)
async def update_meal_plan(
    plan_id: int,
    meal_plan_data: MealPlanUpdate,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Update a meal plan."""
    result = await db.execute(select(MealPlan).where(MealPlan.id == plan_id))
    meal_plan = result.scalar_one_or_none()
    
    if not meal_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan not found"
        )
    
    if meal_plan.creator_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this meal plan"
        )
    
    update_data = meal_plan_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(meal_plan, field, value)
    
    await db.commit()
    await db.refresh(meal_plan)
    
    return meal_plan


@router.delete("/meal-plans/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_meal_plan(
    plan_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a meal plan."""
    result = await db.execute(select(MealPlan).where(MealPlan.id == plan_id))
    meal_plan = result.scalar_one_or_none()
    
    if not meal_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan not found"
        )
    
    if meal_plan.creator_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this meal plan"
        )
    
    await db.delete(meal_plan)
    await db.commit()


# ==================== FOOD ITEMS ====================

@router.get("/food-items", response_model=List[FoodItemResponse])
async def get_food_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = None,
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get food items from the database."""
    query = select(FoodItem)
    
    if search:
        query = query.where(FoodItem.name.ilike(f"%{search}%"))
    
    query = query.order_by(FoodItem.name).offset(skip).limit(limit)
    result = await db.execute(query)
    food_items = result.scalars().all()
    
    return food_items


@router.post("/food-items", response_model=FoodItemResponse, status_code=status.HTTP_201_CREATED)
async def create_food_item(
    food_data: FoodItemCreate,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Add a new food item to the database."""
    new_food = FoodItem(
        name=food_data.name,
        description=food_data.description,
        calories=food_data.calories,
        protein=food_data.protein,
        carbs=food_data.carbs,
        fats=food_data.fats,
        fiber=food_data.fiber,
        sugar=food_data.sugar,
        sodium=food_data.sodium,
        vitamins=food_data.vitamins,
        minerals=food_data.minerals,
        serving_size=food_data.serving_size,
        allergens=food_data.allergens,
        tags=food_data.tags,
        created_by=user_id,
    )
    
    db.add(new_food)
    await db.commit()
    await db.refresh(new_food)
    
    return new_food


# ==================== WORKOUT PLANS ====================

@router.get("/workout-plans", response_model=List[WorkoutPlanResponse])
async def get_workout_plans(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    level: Optional[str] = None,
    is_public: Optional[bool] = None,
    creator_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get workout plans with optional filtering."""
    query = select(WorkoutPlan)
    
    if level:
        query = query.where(WorkoutPlan.level == level)
    
    if is_public is not None:
        query = query.where(WorkoutPlan.is_public == is_public)
    
    if creator_id:
        query = query.where(WorkoutPlan.creator_id == creator_id)
    
    query = query.order_by(WorkoutPlan.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    workout_plans = result.scalars().all()
    
    return workout_plans


@router.post("/workout-plans", response_model=WorkoutPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_workout_plan(
    workout_data: WorkoutPlanCreate,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Create a new workout plan."""
    new_workout = WorkoutPlan(
        name=workout_data.name,
        description=workout_data.description,
        level=workout_data.level,
        duration_minutes=workout_data.duration_minutes,
        calories_burned=workout_data.calories_burned,
        equipment_needed=workout_data.equipment_needed,
        exercises=workout_data.exercises,
        creator_id=user_id,
        is_public=workout_data.is_public,
        is_premium=workout_data.is_premium,
    )
    
    db.add(new_workout)
    await db.commit()
    await db.refresh(new_workout)
    
    return new_workout


@router.get("/workout-plans/{plan_id}", response_model=WorkoutPlanResponse)
async def get_workout_plan(plan_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific workout plan by ID."""
    result = await db.execute(select(WorkoutPlan).where(WorkoutPlan.id == plan_id))
    workout_plan = result.scalar_one_or_none()
    
    if not workout_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout plan not found"
        )
    
    return workout_plan


@router.put("/workout-plans/{plan_id}", response_model=WorkoutPlanResponse)
async def update_workout_plan(
    plan_id: int,
    workout_data: WorkoutPlanUpdate,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Update a workout plan."""
    result = await db.execute(select(WorkoutPlan).where(WorkoutPlan.id == plan_id))
    workout_plan = result.scalar_one_or_none()
    
    if not workout_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout plan not found"
        )
    
    if workout_plan.creator_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this workout plan"
        )
    
    update_data = workout_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(workout_plan, field, value)
    
    await db.commit()
    await db.refresh(workout_plan)
    
    return workout_plan


@router.delete("/workout-plans/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workout_plan(
    plan_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a workout plan."""
    result = await db.execute(select(WorkoutPlan).where(WorkoutPlan.id == plan_id))
    workout_plan = result.scalar_one_or_none()
    
    if not workout_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout plan not found"
        )
    
    if workout_plan.creator_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this workout plan"
        )
    
    await db.delete(workout_plan)
    await db.commit()


# ==================== EXERCISES ====================

@router.get("/exercises", response_model=List[ExerciseResponse])
async def get_exercises(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get exercises from the library."""
    query = select(Exercise)
    
    if category:
        query = query.where(Exercise.category == category)
    
    if difficulty:
        query = query.where(Exercise.difficulty == difficulty)
    
    query = query.order_by(Exercise.name).offset(skip).limit(limit)
    result = await db.execute(query)
    exercises = result.scalars().all()
    
    return exercises


@router.post("/exercises", response_model=ExerciseResponse, status_code=status.HTTP_201_CREATED)
async def create_exercise(
    exercise_data: ExerciseCreate,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Add a new exercise to the library."""
    new_exercise = Exercise(
        name=exercise_data.name,
        description=exercise_data.description,
        category=exercise_data.category,
        difficulty=exercise_data.difficulty,
        equipment_needed=exercise_data.equipment_needed,
        muscle_groups=exercise_data.muscle_groups,
        instructions=exercise_data.instructions,
        video_url=exercise_data.video_url,
        image_url=exercise_data.image_url,
        default_sets=exercise_data.default_sets,
        default_reps=exercise_data.default_reps,
        default_duration_seconds=exercise_data.default_duration_seconds,
        default_rest_seconds=exercise_data.default_rest_seconds,
        created_by=user_id,
    )
    
    db.add(new_exercise)
    await db.commit()
    await db.refresh(new_exercise)
    
    return new_exercise


# ==================== WORKOUT LOGS ====================

@router.post("/workout-logs", response_model=WorkoutLogResponse, status_code=status.HTTP_201_CREATED)
async def log_workout(
    workout_log_data: WorkoutLogCreate,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Log a completed workout."""
    new_log = WorkoutLog(
        user_id=user_id,
        workout_plan_id=workout_log_data.workout_plan_id,
        date=workout_log_data.date,
        duration_minutes=workout_log_data.duration_minutes,
        calories_burned=workout_log_data.calories_burned,
        exercises_completed=workout_log_data.exercises_completed,
        difficulty_rating=workout_log_data.difficulty_rating,
        notes=workout_log_data.notes,
    )
    
    db.add(new_log)
    await db.commit()
    await db.refresh(new_log)
    
    return new_log


@router.get("/workout-logs", response_model=List[WorkoutLogResponse])
async def get_workout_logs(
    user_id: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get workout logs for a user."""
    from datetime import datetime
    
    query = select(WorkoutLog).where(WorkoutLog.user_id == user_id)
    
    if start_date:
        query = query.where(WorkoutLog.date >= datetime.fromisoformat(start_date))
    
    if end_date:
        query = query.where(WorkoutLog.date <= datetime.fromisoformat(end_date))
    
    query = query.order_by(WorkoutLog.date.desc())
    result = await db.execute(query)
    logs = result.scalars().all()
    
    return logs
