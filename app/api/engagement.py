"""
Engagement API
Endpoints for Likes, Stars, Comments, Votes, and Shares.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.engagement import (
    EngagementCreate, 
    CommentCreate, 
    CommentUpdate, 
    ShareCreate,
    CommentResponse, 
    EngagementStats, 
    ShareResponse,
    TargetType,
    ActionType
)
from app.services.engagement_service import EngagementService

router = APIRouter(prefix="/api/v1/engagement", tags=["Engagement"])


# --- ENGAGEMENT ACTIONS (Like, Star, Vote) ---

@router.post("/action", response_model=EngagementStats)
def toggle_engagement(
    data: EngagementCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Toggle a like, star, upvote, or downvote on any content.
    - Send same request again to undo (toggle off).
    - Switching from Upvote to Downvote automatically removes Upvote.
    """
    service = EngagementService(db)
    try:
        result = service.toggle_engagement(user_id=current_user.id, data=data)
        return result["stats"]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/stats/{target_type}/{target_id}", response_model=EngagementStats)
def get_engagement_stats(
    target_type: str,
    target_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Get engagement statistics for a specific item.
    Returns counts for likes, stars, upvotes, downvotes, shares, and total score.
    """
    service = EngagementService(db)
    stats = service.get_engagement_stats(target_type, target_id)
    
    # Validate target type
    valid_types = [t.value for t in TargetType]
    if target_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid target type. Must be one of: {valid_types}")
        
    return stats


# --- COMMENTS ---

@router.post("/comments", response_model=CommentResponse)
def create_comment(
    data: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new comment or reply.
    - Set `parent_id` to reply to an existing comment.
    - Supports nested threading.
    """
    service = EngagementService(db)
    
    # Validate parent if provided
    if data.parent_id:
        parent = db.query(service.db.query(Comment).filter(Comment.id == data.parent_id).first())
        # Simplified validation for brevity
        
    comment = service.create_comment(user_id=current_user.id, data=data)
    
    # Build response with user info
    return CommentResponse(
        id=comment.id,
        content=comment.content,
        user=comment.user,
        target_type=comment.target_type,
        target_id=comment.target_id,
        parent_id=comment.parent_id,
        level=comment.level,
        likes_count=comment.likes_count,
        upvotes_count=comment.upvotes_count,
        downvotes_count=comment.downvotes_count,
        is_edited=comment.is_edited,
        is_hidden=comment.is_hidden,
        created_at=comment.created_at,
        updated_at=comment.updated_at
    )


@router.get("/comments/{target_type}/{target_id}", response_model=List[CommentResponse])
def get_comments(
    target_type: str,
    target_id: str,
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Get all top-level comments for a specific item.
    Replies are not included by default to save bandwidth (fetch separately).
    """
    service = EngagementService(db)
    comments = service.get_comments(target_type, target_id, limit=limit)
    
    # Enrich with current user interactions
    # In a real app, you'd batch fetch engagements for all comments here
    
    return [
        CommentResponse(
            id=c.id,
            content=c.content,
            user=c.user,
            target_type=c.target_type,
            target_id=c.target_id,
            parent_id=c.parent_id,
            level=c.level,
            likes_count=c.likes_count,
            upvotes_count=c.upvotes_count,
            downvotes_count=c.downvotes_count,
            is_edited=c.is_edited,
            is_hidden=c.is_hidden,
            created_at=c.created_at,
            updated_at=c.updated_at,
            replies=[]  # Fetch separately via /comments/{id}/replies
        )
        for c in comments
    ]


@router.get("/comments/{comment_id}/replies", response_model=List[CommentResponse])
def get_comment_replies(
    comment_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Get nested replies for a specific comment."""
    service = EngagementService(db)
    replies = service.get_comment_replies(comment_id)
    
    return [
        CommentResponse(
            id=r.id,
            content=r.content,
            user=r.user,
            target_type=r.target_type,
            target_id=r.target_id,
            parent_id=r.parent_id,
            level=r.level,
            likes_count=r.likes_count,
            upvotes_count=r.upvotes_count,
            downvotes_count=r.downvotes_count,
            is_edited=r.is_edited,
            is_hidden=r.is_hidden,
            created_at=r.created_at,
            updated_at=r.updated_at
        )
        for r in replies
    ]


@router.put("/comments/{comment_id}")
def update_comment(
    comment_id: str,
    data: CommentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update your own comment."""
    service = EngagementService(db)
    try:
        comment = service.update_comment(
            comment_id=comment_id,
            user_id=current_user.id,
            content=data.content
        )
        return {"message": "Comment updated", "edited": comment.is_edited}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/comments/{comment_id}")
def delete_comment(
    comment_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete your own comment. Moderators can delete any."""
    service = EngagementService(db)
    is_moderator = current_user.role in ["moderator", "admin"]
    
    try:
        service.delete_comment(
            comment_id=comment_id,
            user_id=current_user.id,
            is_moderator=is_moderator
        )
        return {"message": "Comment deleted"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# --- SHARES ---

@router.post("/share", response_model=ShareResponse)
def share_content(
    data: ShareCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Record a share action.
    Methods: 'copy_link', 'whatsapp', 'twitter', 'internal_dm'
    If internal_dm, provide `shared_to_user_id`.
    """
    service = EngagementService(db)
    share = service.create_share(user_id=current_user.id, data=data)
    
    return ShareResponse(
        id=share.id,
        user_id=share.user_id,
        target_type=share.target_type,
        target_id=share.target_id,
        share_method=share.share_method,
        created_at=share.created_at
    )


@router.get("/shares/{target_type}/{target_id}")
def get_share_count(
    target_type: str,
    target_id: str,
    db: Session = Depends(get_db)
):
    """Get total share count for an item."""
    service = EngagementService(db)
    count = service.get_share_count(target_type, target_id)
    return {"target_type": target_type, "target_id": target_id, "shares_count": count}


# --- BULK ENGAGEMENT CHECK ---

@router.get("/my-actions/{target_type}")
def get_my_engagements(
    target_type: str,
    target_ids: str = Query(..., description="Comma-separated list of IDs"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Bulk check which actions (like, star, vote) the current user has taken
    on a list of items. Essential for rendering feed UI correctly.
    
    Example: ?target_ids=post_1,post_2,post_3
    """
    service = EngagementService(db)
    ids_list = target_ids.split(",")
    engagements = service.get_user_engagements(current_user.id, target_type, ids_list)
    
    # Format for easy frontend consumption
    result = []
    for tid, actions in engagements.items():
        result.append({
            "target_id": tid,
            "has_liked": "like" in actions,
            "has_starred": "star" in actions,
            "has_upvoted": "upvote" in actions,
            "has_downvoted": "downvote" in actions
        })
    
    return result
