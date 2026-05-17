"""
Engagement Models
Defines database schemas for Likes, Stars, Comments, Votes, and Shares.
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class VoteType(str, enum.Enum):
    UPVOTE = "upvote"
    DOWNVOTE = "downvote"


class Engagement(Base):
    """
    Unified table for Likes, Stars, and Votes to reduce table sprawl.
    Differentiates by 'action_type'.
    """
    __tablename__ = "engagements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    # Target identification (Polymorphic)
    target_type = Column(String, nullable=False, index=True)  # 'post', 'comment', 'meal_plan', 'workout'
    target_id = Column(String, nullable=False, index=True)    # The ID of the target
    
    # Action Type
    action_type = Column(String, nullable=False, index=True)  # 'like', 'star', 'upvote', 'downvote'
    
    # For votes, we might store value, but action_type usually suffices
    # Extra metadata if needed
    metadata = Column(String, nullable=True) 
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="engagements")


class Comment(Base):
    """
    Nested comments system for posts and other content.
    """
    __tablename__ = "comments"

    id = Column(String, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    # Target Content
    target_type = Column(String, nullable=False, index=True) # 'post', 'meal_plan', etc.
    target_id = Column(String, nullable=False, index=True)
    
    # Threading
    parent_id = Column(String, ForeignKey("comments.id"), nullable=True, index=True)
    level = Column(Integer, default=0) # Depth of nesting
    
    # Stats (Cached for performance)
    likes_count = Column(Integer, default=0)
    upvotes_count = Column(Integer, default=0)
    downvotes_count = Column(Integer, default=0)
    
    is_edited = Column(Boolean, default=False)
    is_hidden = Column(Boolean, default=False) # Moderation
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="comments")
    replies = relationship("Comment", backref="parent", remote_side=[id])
    

class Share(Base):
    """
    Tracks sharing activity for analytics and feed distribution.
    """
    __tablename__ = "shares"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    target_type = Column(String, nullable=False, index=True)
    target_id = Column(String, nullable=False, index=True)
    
    share_method = Column(String, nullable=True) # 'copy_link', 'whatsapp', 'twitter', 'internal_dm'
    shared_to_user_id = Column(String, ForeignKey("users.id"), nullable=True) # If shared internally
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="shares")


# Update User model relationship placeholder
# (In a real app, this would be merged into the main user model file)
class UserEngagementMixin:
    engagements = relationship("Engagement", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")
    shares = relationship("Share", back_populates="user", cascade="all, delete-orphan")
