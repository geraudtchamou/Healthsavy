from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.enums import PostCategory


class PostBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)
    category: PostCategory
    tags: Optional[List[str]] = None


class PostCreate(PostBase):
    images: Optional[List[str]] = None
    videos: Optional[List[str]] = None


class PostUpdate(BaseModel):
    content: Optional[str] = None
    category: Optional[PostCategory] = None
    tags: Optional[List[str]] = None
    is_pinned: Optional[bool] = None


class PostResponse(PostBase):
    id: int
    author_id: int
    images: Optional[List[str]] = None
    videos: Optional[List[str]] = None
    likes_count: int
    comments_count: int
    reposts_count: int
    saves_count: int
    mentions: Optional[List[str]] = None
    is_pinned: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CommentBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)


class CommentCreate(CommentBase):
    post_id: int
    parent_id: Optional[int] = None


class CommentResponse(CommentBase):
    id: int
    author_id: int
    post_id: int
    parent_id: Optional[int] = None
    likes_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class LikeResponse(BaseModel):
    id: int
    user_id: int
    post_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class SavedPostCreate(BaseModel):
    post_id: int
    collection_name: Optional[str] = None


class SavedPostResponse(BaseModel):
    id: int
    user_id: int
    post_id: int
    collection_name: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class FollowCreate(BaseModel):
    followed_id: int


class FollowResponse(BaseModel):
    id: int
    follower_id: int
    followed_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
