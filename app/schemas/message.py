from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class MessageBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)
    message_type: str = "text"
    media_url: Optional[str] = None


class MessageCreate(MessageBase):
    receiver_id: int


class MessageResponse(MessageBase):
    id: int
    sender_id: int
    receiver_id: int
    is_read: bool
    read_at: Optional[datetime] = None
    reactions: Optional[dict] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class GroupChatMessageBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)
    message_type: str = "text"
    media_url: Optional[str] = None


class GroupChatMessageCreate(GroupChatMessageBase):
    chat_id: int


class GroupChatMessageResponse(GroupChatMessageBase):
    id: int
    sender_id: int
    chat_id: int
    is_edited: bool
    reactions: Optional[dict] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
