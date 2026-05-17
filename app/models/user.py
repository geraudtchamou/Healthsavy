from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Text, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.models.enums import UserRole, EatingStyle, FitnessInterest, FastingPreference


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # Profile information
    full_name = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    
    # Health profile
    health_goals = Column(JSON, nullable=True)  # List of goals
    eating_style = Column(Enum(EatingStyle), default=EatingStyle.OMNIVORE)
    fitness_interests = Column(JSON, nullable=True)  # List of interests
    fasting_preferences = Column(Enum(FastingPreference), default=FastingPreference.NONE)
    
    # Account settings
    role = Column(Enum(UserRole), default=UserRole.STANDARD)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    privacy_settings = Column(JSON, nullable=True)
    notification_settings = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    habits = relationship("Habit", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="author", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="user", cascade="all, delete-orphan")
    saved_posts = relationship("SavedPost", back_populates="user", cascade="all, delete-orphan")
    followers = relationship(
        "Follow",
        foreign_keys="Follow.followed_id",
        back_populates="followed",
        cascade="all, delete-orphan"
    )
    following = relationship(
        "Follow",
        foreign_keys="Follow.follower_id",
        back_populates="follower",
        cascade="all, delete-orphan"
    )
    group_memberships = relationship("GroupMember", back_populates="user", cascade="all, delete-orphan")
    messages_sent = relationship("Message", foreign_keys="Message.sender_id", back_populates="sender", cascade="all, delete-orphan")
    messages_received = relationship("Message", foreign_keys="Message.receiver_id", back_populates="receiver", cascade="all, delete-orphan")
    meal_plans = relationship("MealPlan", back_populates="creator", cascade="all, delete-orphan")
    workout_plans = relationship("WorkoutPlan", back_populates="creator", cascade="all, delete-orphan")
    achievements = relationship("Achievement", back_populates="user", cascade="all, delete-orphan")
