from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime
from app.models.enums import UserRole, EatingStyle, FitnessInterest, FastingPreference


class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    eating_style: Optional[EatingStyle] = EatingStyle.OMNIVORE
    fasting_preferences: Optional[FastingPreference] = FastingPreference.NONE


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    health_goals: Optional[List[str]] = None
    eating_style: Optional[EatingStyle] = None
    fitness_interests: Optional[List[FitnessInterest]] = None
    fasting_preferences: Optional[FastingPreference] = None
    privacy_settings: Optional[dict] = None
    notification_settings: Optional[dict] = None


class UserResponse(UserBase):
    id: int
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    role: UserRole
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None
