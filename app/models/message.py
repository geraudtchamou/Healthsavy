from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    
    # Message type and media
    message_type = Column(String(50), default="text")  # text, image, video, voice_note
    media_url = Column(String(500), nullable=True)
    
    # Sender and receiver
    sender_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    sender = relationship("User", foreign_keys=[sender_id], back_populates="messages_sent")
    receiver_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="messages_received")
    
    # Status
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    # Reactions
    reactions = Column(JSON, nullable=True)  # {emoji: count}
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class GroupChatMessage(Base):
    __tablename__ = "group_chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    
    # Message type and media
    message_type = Column(String(50), default="text")  # text, image, video, voice_note
    media_url = Column(String(500), nullable=True)
    
    # Sender and chat
    sender_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    chat_id = Column(Integer, ForeignKey("group_chats.id", ondelete="CASCADE"), nullable=False)
    chat = relationship("GroupChat", back_populates="messages")
    
    # Status
    is_edited = Column(Boolean, default=False)
    
    # Reactions
    reactions = Column(JSON, nullable=True)  # {emoji: count}
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
