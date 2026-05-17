from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Text, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.models.enums import GroupPrivacy


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    privacy = Column(Enum(GroupPrivacy), default=GroupPrivacy.PUBLIC)
    
    # Category
    category = Column(String(100), nullable=True)  # e.g., "weight_loss", "vegan", "fitness"
    tags = Column(JSON, nullable=True)  # List of tags
    
    # Cover and branding
    cover_image_url = Column(String(500), nullable=True)
    
    # Creator/Owner
    creator_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Member counts
    member_count = Column(Integer, default=1)
    
    # Settings
    is_active = Column(Boolean, default=True)
    requires_approval = Column(Boolean, default=False)
    rules = Column(JSON, nullable=True)  # List of group rules
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    members = relationship("GroupMember", back_populates="group", cascade="all, delete-orphan")
    posts = relationship("GroupPost", back_populates="group", cascade="all, delete-orphan")
    events = relationship("GroupEvent", back_populates="group", cascade="all, delete-orphan")
    chats = relationship("GroupChat", back_populates="group", cascade="all, delete-orphan")


class GroupMember(Base):
    __tablename__ = "group_members"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User", back_populates="group_memberships")
    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)
    group = relationship("Group", back_populates="members")
    
    # Role in group
    role = Column(String(50), default="member")  # owner, admin, moderator, member
    is_banned = Column(Boolean, default=False)
    
    # Join info
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        # Unique constraint for user-group pair
    )


class GroupPost(Base):
    __tablename__ = "group_posts"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    images = Column(JSON, nullable=True)
    videos = Column(JSON, nullable=True)
    
    # Author and group
    author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)
    group = relationship("Group", back_populates="posts")
    
    # Engagement
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    
    # Type
    is_announcement = Column(Boolean, default=False)
    is_pinned = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class GroupEvent(Base):
    __tablename__ = "group_events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Event details
    event_type = Column(String(50), nullable=True)  # live_discussion, challenge, meetup, etc.
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=True)
    location = Column(String(255), nullable=True)  # Can be virtual or physical
    meeting_link = Column(String(500), nullable=True)
    
    # Group and organizer
    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)
    group = relationship("Group", back_populates="events")
    organizer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Attendance
    attendee_count = Column(Integer, default=0)
    max_attendees = Column(Integer, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class GroupChat(Base):
    __tablename__ = "group_chats"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)
    group = relationship("Group", back_populates="chats")
    
    # Chat metadata
    name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    messages = relationship("GroupChatMessage", back_populates="chat", cascade="all, delete-orphan")
