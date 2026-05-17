"""
Recommendations API Endpoints

Personalized recommendations for content, habits, meal plans, workouts, groups, and challenges.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel

# Import services
import sys
sys.path.append('/workspace')
from app.services.recommendations import recommendations_service, Recommendation
from app.services.advanced_analytics import advanced_analytics_service


router = APIRouter(prefix="/api/v1/recommendations", tags=["Recommendations"])


class RecommendationsResponse(BaseModel):
    """Response wrapper for recommendations"""
    success: bool
    data: List[Recommendation]
    count: int
    user_id: str


class MixedRecommendationsResponse(BaseModel):
    """Mixed recommendations from multiple categories"""
    content: List[Recommendation]
    habits: List[Recommendation]
    meal_plans: List[Recommendation]
    workouts: List[Recommendation]
    groups: List[Recommendation]
    challenges: List[Recommendation]
    users_to_follow: List[Recommendation]


# ==================== CONTENT RECOMMENDATIONS ====================

@router.get("/content", response_model=RecommendationsResponse)
async def get_content_recommendations(
    user_id: str,
    limit: int = Query(default=10, ge=1, le=50),
    category: Optional[str] = None
):
    """
    Get personalized content recommendations
    
    - **user_id**: User to get recommendations for
    - **limit**: Number of recommendations (1-50)
    - **category**: Optional filter by category
    """
    try:
        recommendations = recommendations_service.recommend_content(user_id, limit)
        
        # Filter by category if provided
        if category:
            recommendations = [
                r for r in recommendations 
                if r.metadata.get("category") == category
            ]
        
        # Track event
        advanced_analytics_service.track_event(
            event_type="recommendations_viewed",
            user_id=user_id,
            properties={
                "recommendation_type": "content",
                "count": len(recommendations),
                "category": category
            }
        )
        
        return RecommendationsResponse(
            success=True,
            data=recommendations,
            count=len(recommendations),
            user_id=user_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== HABIT RECOMMENDATIONS ====================

@router.get("/habits", response_model=RecommendationsResponse)
async def get_habit_recommendations(
    user_id: str,
    limit: int = Query(default=5, ge=1, le=20)
):
    """
    Get personalized habit recommendations
    
    Based on user goals, current habits, and success patterns.
    """
    try:
        recommendations = recommendations_service.recommend_habits(user_id, limit)
        
        advanced_analytics_service.track_event(
            event_type="recommendations_viewed",
            user_id=user_id,
            properties={
                "recommendation_type": "habits",
                "count": len(recommendations)
            }
        )
        
        return RecommendationsResponse(
            success=True,
            data=recommendations,
            count=len(recommendations),
            user_id=user_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== MEAL PLAN RECOMMENDATIONS ====================

@router.get("/meal-plans", response_model=RecommendationsResponse)
async def get_meal_plan_recommendations(
    user_id: str,
    limit: int = Query(default=5, ge=1, le=20),
    dietary_preference: Optional[str] = None
):
    """
    Get personalized meal plan recommendations
    
    - **dietary_preference**: Optional filter (vegan, keto, etc.)
    """
    try:
        recommendations = recommendations_service.recommend_meal_plans(user_id, limit)
        
        if dietary_preference:
            recommendations = [
                r for r in recommendations
                if dietary_preference.lower() in r.title.lower() or
                   dietary_preference.lower() in r.description.lower()
            ]
        
        advanced_analytics_service.track_event(
            event_type="recommendations_viewed",
            user_id=user_id,
            properties={
                "recommendation_type": "meal_plans",
                "count": len(recommendations),
                "dietary_preference": dietary_preference
            }
        )
        
        return RecommendationsResponse(
            success=True,
            data=recommendations,
            count=len(recommendations),
            user_id=user_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== WORKOUT RECOMMENDATIONS ====================

@router.get("/workouts", response_model=RecommendationsResponse)
async def get_workout_recommendations(
    user_id: str,
    limit: int = Query(default=5, ge=1, le=20),
    difficulty: Optional[str] = None,
    duration_max: Optional[int] = None
):
    """
    Get personalized workout recommendations
    
    - **difficulty**: Filter by difficulty level
    - **duration_max**: Maximum workout duration in minutes
    """
    try:
        recommendations = recommendations_service.recommend_workouts(user_id, limit)
        
        if difficulty:
            recommendations = [
                r for r in recommendations
                if r.metadata.get("difficulty") == difficulty
            ]
        
        if duration_max:
            recommendations = [
                r for r in recommendations
                if r.metadata.get("duration_minutes", 999) <= duration_max
            ]
        
        advanced_analytics_service.track_event(
            event_type="recommendations_viewed",
            user_id=user_id,
            properties={
                "recommendation_type": "workouts",
                "count": len(recommendations),
                "filters": {"difficulty": difficulty, "duration_max": duration_max}
            }
        )
        
        return RecommendationsResponse(
            success=True,
            data=recommendations,
            count=len(recommendations),
            user_id=user_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== GROUP RECOMMENDATIONS ====================

@router.get("/groups", response_model=RecommendationsResponse)
async def get_group_recommendations(
    user_id: str,
    limit: int = Query(default=5, ge=1, le=20)
):
    """
    Get community group recommendations
    
    Based on user interests, goals, and location.
    """
    try:
        recommendations = recommendations_service.recommend_groups(user_id, limit)
        
        advanced_analytics_service.track_event(
            event_type="recommendations_viewed",
            user_id=user_id,
            properties={
                "recommendation_type": "groups",
                "count": len(recommendations)
            }
        )
        
        return RecommendationsResponse(
            success=True,
            data=recommendations,
            count=len(recommendations),
            user_id=user_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== CHALLENGE RECOMMENDATIONS ====================

@router.get("/challenges", response_model=RecommendationsResponse)
async def get_challenge_recommendations(
    user_id: str,
    limit: int = Query(default=3, ge=1, le=10),
    difficulty: Optional[str] = None
):
    """
    Get wellness challenge recommendations
    
    Matched to user's consistency level and social connections.
    """
    try:
        recommendations = recommendations_service.recommend_challenges(user_id, limit)
        
        if difficulty:
            recommendations = [
                r for r in recommendations
                if r.metadata.get("difficulty") == difficulty
            ]
        
        advanced_analytics_service.track_event(
            event_type="recommendations_viewed",
            user_id=user_id,
            properties={
                "recommendation_type": "challenges",
                "count": len(recommendations)
            }
        )
        
        return RecommendationsResponse(
            success=True,
            data=recommendations,
            count=len(recommendations),
            user_id=user_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== USER RECOMMENDATIONS ====================

@router.get("/users-to-follow", response_model=RecommendationsResponse)
async def get_users_to_follow(
    user_id: str,
    limit: int = Query(default=5, ge=1, le=20)
):
    """
    Get user recommendations to follow
    
    Includes creators, peers, and local influencers.
    """
    try:
        recommendations = recommendations_service.recommend_users_to_follow(user_id, limit)
        
        advanced_analytics_service.track_event(
            event_type="recommendations_viewed",
            user_id=user_id,
            properties={
                "recommendation_type": "users_to_follow",
                "count": len(recommendations)
            }
        )
        
        return RecommendationsResponse(
            success=True,
            data=recommendations,
            count=len(recommendations),
            user_id=user_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== MIXED RECOMMENDATIONS ====================

@router.get("/mixed", response_model=MixedRecommendationsResponse)
async def get_mixed_recommendations(
    user_id: str,
    content_limit: int = 5,
    habits_limit: int = 3,
    meal_plans_limit: int = 3,
    workouts_limit: int = 3,
    groups_limit: int = 3,
    challenges_limit: int = 2,
    users_limit: int = 3
):
    """
    Get mixed recommendations across all categories
    
    Perfect for home page "For You" feed.
    """
    try:
        mixed = MixedRecommendationsResponse(
            content=recommendations_service.recommend_content(user_id, content_limit),
            habits=recommendations_service.recommend_habits(user_id, habits_limit),
            meal_plans=recommendations_service.recommend_meal_plans(user_id, meal_plans_limit),
            workouts=recommendations_service.recommend_workouts(user_id, workouts_limit),
            groups=recommendations_service.recommend_groups(user_id, groups_limit),
            challenges=recommendations_service.recommend_challenges(user_id, challenges_limit),
            users_to_follow=recommendations_service.recommend_users_to_follow(user_id, users_limit)
        )
        
        advanced_analytics_service.track_event(
            event_type="recommendations_viewed",
            user_id=user_id,
            properties={
                "recommendation_type": "mixed",
                "total_count": sum([
                    len(mixed.content),
                    len(mixed.habits),
                    len(mixed.meal_plans),
                    len(mixed.workouts),
                    len(mixed.groups),
                    len(mixed.challenges),
                    len(mixed.users_to_follow)
                ])
            }
        )
        
        return mixed
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== RECOMMENDATION FEEDBACK ====================

@router.post("/feedback")
async def submit_recommendation_feedback(
    user_id: str,
    recommendation_id: str,
    action: str,  # clicked, dismissed, saved, shared
    dwell_time_seconds: Optional[int] = None
):
    """
    Submit feedback on a recommendation
    
    Used to improve recommendation algorithm.
    """
    try:
        advanced_analytics_service.track_event(
            event_type="recommendation_feedback",
            user_id=user_id,
            properties={
                "recommendation_id": recommendation_id,
                "action": action,
                "dwell_time_seconds": dwell_time_seconds
            }
        )
        
        return {
            "success": True,
            "message": "Feedback recorded",
            "data": {
                "recommendation_id": recommendation_id,
                "action": action
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== RECOMMENDATION ANALYTICS ====================

@router.get("/analytics/performance")
async def get_recommendation_performance(
    days: int = Query(default=7, ge=1, le=90)
):
    """
    Get recommendation system performance metrics
    
    - CTR by category
    - Conversion rates
    - User satisfaction scores
    """
    try:
        # Simulated analytics (replace with real queries)
        performance = {
            "period_days": days,
            "total_impressions": 145230,
            "total_clicks": 18456,
            "overall_ctr": 0.127,
            "by_category": {
                "content": {"impressions": 52000, "clicks": 7800, "ctr": 0.15},
                "habits": {"impressions": 28000, "clicks": 4200, "ctr": 0.15},
                "meal_plans": {"impressions": 25000, "clicks": 3000, "ctr": 0.12},
                "workouts": {"impressions": 22000, "clicks": 2640, "ctr": 0.12},
                "groups": {"impressions": 12000, "clicks": 600, "ctr": 0.05},
                "challenges": {"impressions": 6230, "clicks": 216, "ctr": 0.035}
            },
            "conversion_metrics": {
                "habit_adoption_rate": 0.34,
                "meal_plan_start_rate": 0.28,
                "workout_start_rate": 0.31,
                "group_join_rate": 0.42,
                "challenge_join_rate": 0.25
            }
        }
        
        return {
            "success": True,
            "data": performance
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
