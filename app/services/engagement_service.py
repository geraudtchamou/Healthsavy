"""
Engagement Service
Business logic for Likes, Stars, Comments, Votes, and Shares.
Handles counting, validation, and feed scoring.
"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from app.models.engagement import Engagement, Comment, Share, VoteType
from app.models.user import User
from app.schemas.engagement import EngagementCreate, CommentCreate, ShareCreate, ActionType
from app.services.analytics_service import AnalyticsService


class EngagementService:
    def __init__(self, db: Session):
        self.db = db
        self.analytics = AnalyticsService(db)

    # --- ENGAGEMENT (Likes, Stars, Votes) ---

    def toggle_engagement(self, user_id: str, data: EngagementCreate) -> Dict[str, Any]:
        """
        Toggle a like, star, or vote. 
        If exists -> remove (unlike). If not exists -> create.
        Handles switching vote types (upvote <-> downvote).
        """
        existing = self.db.query(Engagement).filter(
            Engagement.user_id == user_id,
            Engagement.target_type == data.target_type.value,
            Engagement.target_id == data.target_id,
            Engagement.action_type == data.action_type.value
        ).first()

        target_model = self._get_target_model(data.target_type.value)
        
        if existing:
            # Remove engagement (Toggle off)
            self.db.delete(existing)
            self._update_counts(data.target_type.value, data.target_id, data.action_type.value, delta=-1)
            action = "removed"
        else:
            # If voting, remove opposite vote first
            if data.action_type in [ActionType.UPVOTE, ActionType.DOWNVOTE]:
                opposite = ActionType.DOWNVOTE if data.action_type == ActionType.UPVOTE else ActionType.UPVOTE
                opposite_engagement = self.db.query(Engagement).filter(
                    Engagement.user_id == user_id,
                    Engagement.target_type == data.target_type.value,
                    Engagement.target_id == data.target_id,
                    Engagement.action_type == opposite.value
                ).first()
                
                if opposite_engagement:
                    self.db.delete(opposite_engagement)
                    self._update_counts(data.target_type.value, data.target_id, opposite.value, delta=-1)

            # Create new engagement
            new_engagement = Engagement(
                user_id=user_id,
                target_type=data.target_type.value,
                target_id=data.target_id,
                action_type=data.action_type.value
            )
            self.db.add(new_engagement)
            self._update_counts(data.target_type.value, data.target_id, data.action_type.value, delta=1)
            
            # Track analytics
            self.analytics.track_event(
                user_id=user_id,
                event_type=f"content_{data.action_type.value}",
                properties={
                    "target_type": data.target_type.value,
                    "target_id": data.target_id
                }
            )
            action = "added"

        self.db.commit()
        
        # Refresh counts
        stats = self.get_engagement_stats(data.target_type.value, data.target_id)
        return {"action": action, "stats": stats}

    def _update_counts(self, target_type: str, target_id: str, action_type: str, delta: int):
        """
        Updates cached counts on the target model (e.g., Post.likes_count).
        Note: In a real app, this would use a generic update or specific model handlers.
        Here we assume the target has these columns or we rely on real-time counting.
        For this implementation, we'll rely on real-time counting in get_engagement_stats
        to avoid complex polymorphic updates, but this is where you'd increment/decrement.
        """
        pass 

    def get_engagement_stats(self, target_type: str, target_id: str) -> Dict[str, int]:
        """Calculate real-time engagement statistics."""
        likes = self.db.query(Engagement).filter(
            Engagement.target_type == target_type,
            Engagement.target_id == target_id,
            Engagement.action_type == ActionType.LIKE.value
        ).count()

        stars = self.db.query(Engagement).filter(
            Engagement.target_type == target_type,
            Engagement.target_id == target_id,
            Engagement.action_type == ActionType.STAR.value
        ).count()

        upvotes = self.db.query(Engagement).filter(
            Engagement.target_type == target_type,
            Engagement.target_id == target_id,
            Engagement.action_type == ActionType.UPVOTE.value
        ).count()

        downvotes = self.db.query(Engagement).filter(
            Engagement.target_type == target_type,
            Engagement.target_id == target_id,
            Engagement.action_type == ActionType.DOWNVOTE.value
        ).count()

        shares = self.db.query(Share).filter(
            Share.target_type == target_type,
            Share.target_id == target_id
        ).count()

        # Calculate weighted score (Reddit-style hot ranking base)
        score = (likes * 1) + (stars * 2) + (upvotes * 1) - (downvotes * 1)

        return {
            "likes_count": likes,
            "stars_count": stars,
            "upvotes_count": upvotes,
            "downvotes_count": downvotes,
            "shares_count": shares,
            "score": score
        }

    def get_user_engagements(self, user_id: str, target_type: str, target_ids: List[str]) -> Dict[str, List[str]]:
        """
        Bulk fetch user engagements for a list of targets.
        Returns dict mapping target_id -> list of action_types.
        """
        engagements = self.db.query(Engagement).filter(
            Engagement.user_id == user_id,
            Engagement.target_type == target_type,
            Engagement.target_id.in_(target_ids)
        ).all()

        result = {}
        for eng in engagements:
            if eng.target_id not in result:
                result[eng.target_id] = []
            result[eng.target_id].append(eng.action_type)
        
        return result

    def _get_target_model(self, target_type: str):
        """Helper to get SQLAlchemy model class by string name."""
        from app.models.post import Post
        from app.models.meal_plan import MealPlan
        # Add imports as needed
        mapping = {
            "post": Post,
            "meal_plan": MealPlan,
            # "workout_plan": WorkoutPlan
        }
        return mapping.get(target_type)

    # --- COMMENTS ---

    def create_comment(self, user_id: str, data: CommentCreate) -> Comment:
        comment_id = f"comment_{uuid.uuid4().hex[:12]}"
        
        # Determine level for threading
        level = 0
        if data.parent_id:
            parent = self.db.query(Comment).filter(Comment.id == data.parent_id).first()
            if parent:
                level = parent.level + 1
        
        new_comment = Comment(
            id=comment_id,
            content=data.content,
            user_id=user_id,
            target_type=data.target_type.value,
            target_id=data.target_id,
            parent_id=data.parent_id,
            level=level
        )
        
        self.db.add(new_comment)
        self.db.commit()
        self.db.refresh(new_comment)
        
        # Analytics
        self.analytics.track_event(
            user_id=user_id,
            event_type="comment_created",
            properties={"target_type": data.target_type.value, "target_id": data.target_id}
        )
        
        return new_comment

    def get_comments(self, target_type: str, target_id: str, limit: int = 50) -> List[Comment]:
        """Fetch top-level comments for a target."""
        return self.db.query(Comment).filter(
            Comment.target_type == target_type,
            Comment.target_id == target_id,
            Comment.parent_id == None,
            Comment.is_hidden == False
        ).order_by(Comment.created_at.desc()).limit(limit).all()

    def get_comment_replies(self, comment_id: str) -> List[Comment]:
        """Fetch replies for a specific comment."""
        return self.db.query(Comment).filter(
            Comment.parent_id == comment_id,
            Comment.is_hidden == False
        ).order_by(Comment.created_at.asc()).all()

    def update_comment(self, comment_id: str, user_id: str, content: str) -> Comment:
        comment = self.db.query(Comment).filter(
            Comment.id == comment_id,
            Comment.user_id == user_id
        ).first()
        
        if not comment:
            raise ValueError("Comment not found or unauthorized")
            
        comment.content = content
        comment.is_edited = True
        self.db.commit()
        self.db.refresh(comment)
        return comment

    def delete_comment(self, comment_id: str, user_id: str, is_moderator: bool = False) -> bool:
        query = self.db.query(Comment).filter(Comment.id == comment_id)
        if not is_moderator:
            query = query.filter(Comment.user_id == user_id)
            
        comment = query.first()
        if not comment:
            raise ValueError("Comment not found or unauthorized")
            
        # Soft delete for moderation, hard delete for user
        if is_moderator:
            comment.is_hidden = True
            comment.content = "[Removed by Moderator]"
            self.db.commit()
        else:
            self.db.delete(comment)
            self.db.commit()
            
        return True

    # --- SHARES ---

    def create_share(self, user_id: str, data: ShareCreate) -> Share:
        new_share = Share(
            user_id=user_id,
            target_type=data.target_type.value,
            target_id=data.target_id,
            share_method=data.share_method,
            shared_to_user_id=data.shared_to_user_id
        )
        
        self.db.add(new_share)
        self.db.commit()
        self.db.refresh(new_share)
        
        # Analytics
        self.analytics.track_event(
            user_id=user_id,
            event_type="content_shared",
            properties={
                "target_type": data.target_type.value,
                "target_id": data.target_id,
                "method": data.share_method
            }
        )
        
        return new_share

    def get_share_count(self, target_type: str, target_id: str) -> int:
        return self.db.query(Share).filter(
            Share.target_type == target_type,
            Share.target_id == target_id
        ).count()
