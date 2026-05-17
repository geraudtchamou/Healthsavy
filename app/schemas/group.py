from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.enums import GroupPrivacy


class GroupBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    privacy: GroupPrivacy = GroupPrivacy.PUBLIC
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    requires_approval: bool = False
    rules: Optional[List[str]] = None


class GroupCreate(GroupBase):
    cover_image_url: Optional[str] = None


class GroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    privacy: Optional[GroupPrivacy] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    cover_image_url: Optional[str] = None
    requires_approval: Optional[bool] = None
    rules: Optional[List[str]] = None
    is_active: Optional[bool] = None


class GroupResponse(GroupBase):
    id: int
    creator_id: int
    cover_image_url: Optional[str] = None
    member_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class GroupMemberResponse(BaseModel):
    id: int
    user_id: int
    group_id: int
    role: str
    is_banned: bool
    joined_at: datetime
    
    class Config:
        from_attributes = True


class GroupPostBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)
    images: Optional[List[str]] = None
    videos: Optional[List[str]] = None
    is_announcement: bool = False


class GroupPostCreate(GroupPostBase):
    group_id: int


class GroupPostResponse(GroupPostBase):
    id: int
    author_id: int
    group_id: int
    likes_count: int
    comments_count: int
    is_pinned: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class GroupEventBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    event_type: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    meeting_link: Optional[str] = None
    max_attendees: Optional[int] = None


class GroupEventCreate(GroupEventBase):
    group_id: int


class GroupEventResponse(GroupEventBase):
    id: int
    group_id: int
    organizer_id: int
    attendee_count: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
