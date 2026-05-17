"""
Engagement Schemas
Pydantic models for request/response validation.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Literal
from datetime import datetime
from enum import Enum


class ActionType(str, Enum):
    LIKE = "like"
    STAR = "star"
    UPVOTE = "upvote"
    DOWNVOTE = "downvote"


class TargetType(str, Enum):
    POST = "post"
    COMMENT = "comment"
    MEAL_PLAN = "meal_plan"
    WORKOUT_PLAN = "workout_plan"
    HABIT = "habit"
    GROUP = "group"


# --- Request Schemas ---

class EngagementCreate(BaseModel):
    target_type: TargetType
    target_id: str
    action_type: ActionType
    
    class Config:
        schema_extra = {
            "example": {
                "target_type": "post",
                "target_id": "post_123",
                "action_type": "like"
            }
        }


class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)
    target_type: TargetType
    target_id: str
    parent_id: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "content": "Great tip! I'll try this tomorrow.",
                "target_type": "post",
                "target_id": "post_123",
                "parent_id": None
            }
        }


class CommentUpdate(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)


class ShareCreate(BaseModel):
    target_type: TargetType
    target_id: str
    share_method: Optional[str] = "copy_link"  # copy_link, whatsapp, twitter, internal_dm
    shared_to_user_id: Optional[str] = None


# --- Response Schemas ---

class UserSummary(BaseModel):
    id: str
    name: str
    avatar: Optional[str] = None
    
    class Config:
        from_attributes = True


class CommentResponse(BaseModel):
    id: str
    content: str
    user: UserSummary
    target_type: str
    target_id: str
    parent_id: Optional[str] = None
    level: int = 0
    
    # Counts
    likes_count: int = 0
    upvotes_count: int = 0
    downvotes_count: int = 0
    
    # State
    is_edited: bool = False
    is_hidden: bool = False
    
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Nested replies
    replies: List['CommentResponse'] = []
    
    # Current user interaction (injected by API)
    user_has_liked: bool = False
    user_has_upvoted: bool = False
    user_has_downvoted: bool = False
    
    class Config:
        from_attributes = True


class EngagementStats(BaseModel):
    likes_count: int = 0
    stars_count: int = 0
    upvotes_count: int = 0
    downvotes_count: int = 0
    shares_count: int = 0
    
    # Calculated
    score: int = 0  # Weighted score for ranking
    engagement_rate: float = 0.0


class EngagementResponse(BaseModel):
    id: int
    user_id: str
    target_type: str
    target_id: str
    action_type: str
    created_at: datetime
    
    user: Optional[UserSummary] = None
    
    class Config:
        from_attributes = True


class ShareResponse(BaseModel):
    id: int
    user_id: str
    target_type: str
    target_id: str
    share_method: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Update forward refs
CommentResponse.update_forward_refs()
