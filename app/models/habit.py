from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Text, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.models.enums import HabitType


class Habit(Base):
    __tablename__ = "habits"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    habit_type = Column(Enum(HabitType), nullable=False)
    description = Column(Text, nullable=True)
    
    # Tracking settings
    target_value = Column(Float, nullable=True)  # e.g., 8 glasses of water
    target_unit = Column(String(50), nullable=True)  # e.g., "glasses", "minutes", "km"
    frequency = Column(String(50), default="daily")  # daily, weekly, monthly
    reminder_times = Column(JSON, nullable=True)  # List of times for reminders
    
    # User
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User", back_populates="habits")
    
    # Status
    is_active = Column(Boolean, default=True)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    tracking_logs = relationship("HabitTrackingLog", back_populates="habit", cascade="all, delete-orphan")


class HabitTrackingLog(Base):
    __tablename__ = "habit_tracking_logs"

    id = Column(Integer, primary_key=True, index=True)
    habit_id = Column(Integer, ForeignKey("habits.id", ondelete="CASCADE"), nullable=False)
    habit = relationship("Habit", back_populates="tracking_logs")
    
    # Tracking data
    date = Column(DateTime(timezone=True), nullable=False)
    completed = Column(Boolean, default=False)
    value = Column(Float, nullable=True)  # Actual value achieved
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
