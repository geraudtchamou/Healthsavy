from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models.habit import Habit, HabitTrackingLog
from app.schemas.habit import (
    HabitCreate,
    HabitUpdate,
    HabitResponse,
    HabitTrackingLogCreate,
    HabitTrackingLogResponse,
)

router = APIRouter(prefix="/habits", tags=["Habits"])


@router.get("/", response_model=List[HabitResponse])
async def get_habits(
    user_id: int,
    is_active: Optional[bool] = None,
    habit_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get all habits for a user."""
    query = select(Habit).where(Habit.user_id == user_id)
    
    if is_active is not None:
        query = query.where(Habit.is_active == is_active)
    
    if habit_type:
        query = query.where(Habit.habit_type == habit_type)
    
    query = query.order_by(Habit.created_at.desc())
    result = await db.execute(query)
    habits = result.scalars().all()
    
    return habits


@router.post("/", response_model=HabitResponse, status_code=status.HTTP_201_CREATED)
async def create_habit(
    habit_data: HabitCreate,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Create a new habit."""
    new_habit = Habit(
        name=habit_data.name,
        habit_type=habit_data.habit_type,
        description=habit_data.description,
        target_value=habit_data.target_value,
        target_unit=habit_data.target_unit,
        frequency=habit_data.frequency,
        reminder_times=habit_data.reminder_times,
        user_id=user_id,
    )
    
    db.add(new_habit)
    await db.commit()
    await db.refresh(new_habit)
    
    return new_habit


@router.put("/{habit_id}", response_model=HabitResponse)
async def update_habit(
    habit_id: int,
    habit_data: HabitUpdate,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Update a habit."""
    result = await db.execute(select(Habit).where(Habit.id == habit_id))
    habit = result.scalar_one_or_none()
    
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found"
        )
    
    if habit.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this habit"
        )
    
    update_data = habit_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(habit, field, value)
    
    await db.commit()
    await db.refresh(habit)
    
    return habit


@router.delete("/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_habit(
    habit_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a habit."""
    result = await db.execute(select(Habit).where(Habit.id == habit_id))
    habit = result.scalar_one_or_none()
    
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found"
        )
    
    if habit.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this habit"
        )
    
    await db.delete(habit)
    await db.commit()


@router.post("/{habit_id}/track", response_model=HabitTrackingLogResponse)
async def track_habit(
    habit_id: int,
    tracking_data: HabitTrackingLogCreate,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Track a habit completion."""
    # Verify habit exists and belongs to user
    result = await db.execute(select(Habit).where(Habit.id == habit_id))
    habit = result.scalar_one_or_none()
    
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found"
        )
    
    if habit.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to track this habit"
        )
    
    # Create tracking log
    new_log = HabitTrackingLog(
        habit_id=habit_id,
        date=tracking_data.date,
        completed=tracking_data.completed,
        value=tracking_data.value,
        notes=tracking_data.notes,
    )
    
    db.add(new_log)
    
    # Update streak if completed today
    if tracking_data.completed:
        today = datetime.utcnow().date()
        if tracking_data.date.date() == today:
            habit.current_streak += 1
            if habit.current_streak > habit.longest_streak:
                habit.longest_streak = habit.current_streak
    
    await db.commit()
    await db.refresh(new_log)
    
    return new_log


@router.get("/{habit_id}/logs", response_model=List[HabitTrackingLogResponse])
async def get_habit_logs(
    habit_id: int,
    user_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get tracking logs for a habit."""
    query = select(HabitTrackingLog).where(HabitTrackingLog.habit_id == habit_id)
    
    if start_date:
        query = query.where(HabitTrackingLog.date >= start_date)
    
    if end_date:
        query = query.where(HabitTrackingLog.date <= end_date)
    
    query = query.order_by(HabitTrackingLog.date.desc())
    result = await db.execute(query)
    logs = result.scalars().all()
    
    return logs
