from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List

from app.core.database import get_db
from app.models.user import User
from app.models.post import Post, Comment, Like, SavedPost, Follow
from app.schemas.post import (
    PostCreate,
    PostUpdate,
    PostResponse,
    CommentCreate,
    CommentResponse,
    SavedPostCreate,
    SavedPostResponse,
    FollowCreate,
    FollowResponse,
)

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.get("/", response_model=List[PostResponse])
async def get_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get posts with optional filtering by category."""
    query = select(Post).order_by(Post.created_at.desc())
    
    if category:
        query = query.where(Post.category == category)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    posts = result.scalars().all()
    
    return posts


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: PostCreate,
    user_id: int,  # This would come from auth dependency in real app
    db: AsyncSession = Depends(get_db)
):
    """Create a new post."""
    new_post = Post(
        content=post_data.content,
        category=post_data.category,
        images=post_data.images,
        videos=post_data.videos,
        tags=post_data.tags,
        author_id=user_id,
    )
    
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)
    
    return new_post


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific post by ID."""
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    return post


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    post_data: PostUpdate,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Update a post."""
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    if post.author_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this post"
        )
    
    update_data = post_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(post, field, value)
    
    await db.commit()
    await db.refresh(post)
    
    return post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a post."""
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    if post.author_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this post"
        )
    
    await db.delete(post)
    await db.commit()


@router.post("/{post_id}/comments", response_model=CommentResponse)
async def create_comment(
    post_id: int,
    comment_data: CommentCreate,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Create a comment on a post."""
    # Verify post exists
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    new_comment = Comment(
        content=comment_data.content,
        author_id=user_id,
        post_id=post_id,
        parent_id=comment_data.parent_id,
    )
    
    db.add(new_comment)
    
    # Update post comment count
    post.comments_count += 1
    
    await db.commit()
    await db.refresh(new_comment)
    
    return new_comment


@router.post("/{post_id}/like")
async def like_post(
    post_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Like a post."""
    # Check if already liked
    result = await db.execute(
        select(Like).where(Like.post_id == post_id, Like.user_id == user_id)
    )
    existing_like = result.scalar_one_or_none()
    
    if existing_like:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already liked this post"
        )
    
    new_like = Like(user_id=user_id, post_id=post_id)
    db.add(new_like)
    
    # Update post likes count
    post_result = await db.execute(select(Post).where(Post.id == post_id))
    post = post_result.scalar_one_or_none()
    if post:
        post.likes_count += 1
    
    await db.commit()
    
    return {"message": "Post liked successfully"}


@router.post("/{post_id}/save", response_model=SavedPostResponse)
async def save_post(
    post_id: int,
    save_data: Optional[SavedPostCreate] = None,
    user_id: int = None,
    db: AsyncSession = Depends(get_db)
):
    """Save/bookmark a post."""
    collection_name = save_data.collection_name if save_data else None
    
    new_saved = SavedPost(
        user_id=user_id,
        post_id=post_id,
        collection_name=collection_name,
    )
    
    db.add(new_saved)
    
    # Update post saves count
    post_result = await db.execute(select(Post).where(Post.id == post_id))
    post = post_result.scalar_one_or_none()
    if post:
        post.saves_count += 1
    
    await db.commit()
    await db.refresh(new_saved)
    
    return new_saved


@router.post("/follow", response_model=FollowResponse)
async def follow_user(
    follow_data: FollowCreate,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Follow another user."""
    if user_id == follow_data.followed_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot follow yourself"
        )
    
    # Check if already following
    result = await db.execute(
        select(Follow).where(
            Follow.follower_id == user_id,
            Follow.followed_id == follow_data.followed_id
        )
    )
    existing_follow = result.scalar_one_or_none()
    
    if existing_follow:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already following this user"
        )
    
    new_follow = Follow(follower_id=user_id, followed_id=follow_data.followed_id)
    db.add(new_follow)
    
    await db.commit()
    await db.refresh(new_follow)
    
    return new_follow
