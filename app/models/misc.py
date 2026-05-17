from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    badge_url = Column(String(500), nullable=True)
    
    # Achievement criteria
    category = Column(String(100), nullable=True)  # streak, milestone, community, etc.
    points = Column(Integer, default=10)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user_achievements = relationship("UserAchievement", back_populates="achievement", cascade="all, delete-orphan")


class UserAchievement(Base):
    __tablename__ = "user_achievements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User", back_populates="achievements")
    achievement_id = Column(Integer, ForeignKey("achievements.id", ondelete="CASCADE"), nullable=False)
    achievement = relationship("Achievement", back_populates="user_achievements")
    
    # Progress tracking
    progress = Column(Integer, default=0)
    target = Column(Integer, default=1)
    is_completed = Column(Boolean, default=False)
    
    # Timestamps
    earned_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Notification content
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False)  # like, comment, follow, message, reminder, etc.
    
    # Related entities
    related_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    related_post_id = Column(Integer, ForeignKey("posts.id", ondelete="SET NULL"), nullable=True)
    related_group_id = Column(Integer, ForeignKey("groups.id", ondelete="SET NULL"), nullable=True)
    
    # Status
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    # Delivery
    is_push_sent = Column(Boolean, default=False)
    is_email_sent = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    
    # Report details
    report_type = Column(String(50), nullable=False)  # post, comment, user, group
    reason = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Reporter and reported
    reporter_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    reported_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    reported_post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=True)
    reported_comment_id = Column(Integer, ForeignKey("comments.id", ondelete="CASCADE"), nullable=True)
    reported_group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=True)
    
    # Status
    status = Column(String(50), default="pending")  # pending, reviewed, resolved, dismissed
    moderator_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
