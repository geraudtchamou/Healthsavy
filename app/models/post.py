from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Text, Float, JSON, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.models.enums import PostCategory


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    category = Column(Enum(PostCategory), nullable=False)
    
    # Media
    images = Column(JSON, nullable=True)  # List of image URLs
    videos = Column(JSON, nullable=True)  # List of video URLs
    
    # Author
    author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    author = relationship("User", back_populates="posts")
    
    # Engagement
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    reposts_count = Column(Integer, default=0)
    saves_count = Column(Integer, default=0)
    
    # Metadata
    tags = Column(JSON, nullable=True)  # List of tags
    mentions = Column(JSON, nullable=True)  # List of mentions
    is_pinned = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="post", cascade="all, delete-orphan")
    saved_by = relationship("SavedPost", back_populates="post", cascade="all, delete-orphan")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    
    # Author and post
    author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    author = relationship("User", back_populates="comments")
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    post = relationship("Post", back_populates="comments")
    
    # Parent comment (for nested comments)
    parent_id = Column(Integer, ForeignKey("comments.id", ondelete="CASCADE"), nullable=True)
    parent = relationship("Comment", remote_side=[id], backref="replies")
    
    # Engagement
    likes_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User", back_populates="likes")
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    post = relationship("Post", back_populates="likes")
    
    # Ensure one like per user per post
    __table_args__ = (
        # Unique constraint would be added in migration
    )
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SavedPost(Base):
    __tablename__ = "saved_posts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User", back_populates="saved_posts")
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    post = relationship("Post", back_populates="saved_by")
    
    collection_name = Column(String(100), nullable=True)  # For organizing saved posts
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        # Unique constraint for user-post pair
    )


class Follow(Base):
    __tablename__ = "follows"

    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    follower = relationship("User", foreign_keys=[follower_id], back_populates="following")
    followed_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    followed = relationship("User", foreign_keys=[followed_id], back_populates="followers")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        # Unique constraint for follower-followed pair
    )
