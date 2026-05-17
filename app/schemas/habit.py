from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.enums import HabitType


class HabitBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    habit_type: HabitType
    description: Optional[str] = None
    target_value: Optional[float] = None
    target_unit: Optional[str] = None
    frequency: Optional[str] = "daily"
    reminder_times: Optional[List[str]] = None


class HabitCreate(HabitBase):
    pass


class HabitUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    target_value: Optional[float] = None
    target_unit: Optional[str] = None
    frequency: Optional[str] = None
    reminder_times: Optional[List[str]] = None
    is_active: Optional[bool] = None


class HabitResponse(HabitBase):
    id: int
    user_id: int
    is_active: bool
    current_streak: int
    longest_streak: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class HabitTrackingLogBase(BaseModel):
    date: datetime
    completed: bool = False
    value: Optional[float] = None
    notes: Optional[str] = None


class HabitTrackingLogCreate(HabitTrackingLogBase):
    habit_id: int


class HabitTrackingLogResponse(HabitTrackingLogBase):
    id: int
    habit_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
