from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Text, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.models.enums import WorkoutLevel, ExerciseCategory


class WorkoutPlan(Base):
    __tablename__ = "workout_plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    level = Column(Enum(WorkoutLevel), nullable=False)
    
    # Workout info
    duration_minutes = Column(Integer, nullable=True)
    calories_burned = Column(Integer, nullable=True)
    equipment_needed = Column(JSON, nullable=True)  # List of equipment
    
    # Exercises structure
    exercises = Column(JSON, nullable=False)  # [{name, sets, reps, duration, rest_time, video_url}]
    
    # Creator
    creator_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    creator = relationship("User", back_populates="workout_plans")
    
    # Visibility
    is_public = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    
    # Engagement
    saves_count = Column(Integer, default=0)
    rating = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(Enum(ExerciseCategory), nullable=False)
    
    # Exercise details
    difficulty = Column(Enum(WorkoutLevel), nullable=False)
    equipment_needed = Column(JSON, nullable=True)  # List of equipment
    muscle_groups = Column(JSON, nullable=True)  # List of targeted muscle groups
    
    # Instructions
    instructions = Column(JSON, nullable=True)  # Step-by-step instructions
    video_url = Column(String(500), nullable=True)
    image_url = Column(String(500), nullable=True)
    
    # Metrics
    default_sets = Column(Integer, nullable=True)
    default_reps = Column(Integer, nullable=True)
    default_duration_seconds = Column(Integer, nullable=True)
    default_rest_seconds = Column(Integer, nullable=True)
    
    # Metadata
    is_verified = Column(Boolean, default=False)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class WorkoutLog(Base):
    __tablename__ = "workout_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    workout_plan_id = Column(Integer, ForeignKey("workout_plans.id", ondelete="SET NULL"), nullable=True)
    
    # Workout data
    date = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer, nullable=True)
    calories_burned = Column(Integer, nullable=True)
    exercises_completed = Column(JSON, nullable=True)  # [{exercise_name, sets, reps, weight}]
    
    # User feedback
    difficulty_rating = Column(Integer, nullable=True)  # 1-10 scale
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
