"""
Smart Recommendations Engine

Personalized recommendations for:
- Content (posts, articles, videos)
- Habits to track
- Meal plans
- Workout programs
- Groups to join
- Users to follow
- Wellness challenges
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class Recommendation(BaseModel):
    """Generic recommendation item"""
    id: str
    type: str  # content, habit, meal_plan, workout, group, user, challenge
    title: str
    description: str
    relevance_score: float  # 0-100
    reason: str
    metadata: Dict[str, Any] = {}
    image_url: Optional[str] = None


class PersonalizedRecommendationsService:
    """
    AI-powered personalized recommendations engine
    
    Uses collaborative filtering, content-based filtering,
    and contextual bandits for optimal recommendations.
    """
    
    def __init__(self, db_session=None):
        self.db = db_session
    
    # ==================== CONTENT RECOMMENDATIONS ====================
    
    def recommend_content(self, user_id: str, limit: int = 10) -> List[Recommendation]:
        """
        Recommend posts, articles, and videos based on:
        - User's past engagement
        - Followed topics/categories
        - Similar users' preferences
        - Trending content in user's network
        """
        recommendations = []
        
        # Get user profile and preferences (simulated)
        user_interests = self._get_user_interests(user_id)
        followed_categories = self._get_followed_categories(user_id)
        
        # Content-based recommendations
        content_recs = self._content_based_recommendations(user_interests, limit // 2)
        recommendations.extend(content_recs)
        
        # Collaborative filtering (similar users)
        collab_recs = self._collaborative_filtering(user_id, limit // 2)
        recommendations.extend(collab_recs)
        
        # Trending in network
        trending_recs = self._trending_in_network(user_id, limit // 3)
        recommendations.extend(trending_recs)
        
        # Sort by relevance
        recommendations = sorted(recommendations, key=lambda x: x.relevance_score, reverse=True)
        
        return recommendations[:limit]
    
    # ==================== HABIT RECOMMENDATIONS ====================
    
    def recommend_habits(self, user_id: str, limit: int = 5) -> List[Recommendation]:
        """
        Recommend new habits to track based on:
        - User's health goals
        - Current habit success rate
        - Popular habits among similar users
        - Seasonal/trending habits
        """
        recommendations = []
        
        user_goals = self._get_user_goals(user_id)
        current_habits = self._get_current_habits(user_id)
        
        # Goal-based recommendations
        if "weight_loss" in user_goals:
            recommendations.append(Recommendation(
                id="habit_water",
                type="habit",
                title="Track Water Intake",
                description="Staying hydrated boosts metabolism and reduces cravings",
                relevance_score=92,
                reason="Aligns with your weight loss goal",
                metadata={"category": "nutrition", "difficulty": "easy", "avg_completion_rate": 0.78}
            ))
        
        if "fitness" in user_goals or "muscle_gain" in user_goals:
            recommendations.append(Recommendation(
                id="habit_protein",
                type="habit",
                title="Track Protein Intake",
                description="Ensure adequate protein for muscle recovery and growth",
                relevance_score=89,
                reason="Supports your fitness goals",
                metadata={"category": "nutrition", "difficulty": "medium", "avg_completion_rate": 0.65}
            ))
        
        if "stress_management" in user_goals or "mental_wellness" in user_goals:
            recommendations.append(Recommendation(
                id="habit_meditation",
                type="habit",
                title="Daily Meditation",
                description="10 minutes of mindfulness to reduce stress and improve focus",
                relevance_score=94,
                reason="Perfect for your mental wellness journey",
                metadata={"category": "mental_health", "difficulty": "easy", "avg_completion_rate": 0.71}
            ))
        
        # Based on habit success patterns
        if self._is_user_consistent(user_id):
            recommendations.append(Recommendation(
                id="habit_advanced",
                type="habit",
                title="Advanced Morning Routine",
                description="Combine meditation, exercise, and healthy breakfast",
                relevance_score=85,
                reason="You're ready for an advanced challenge!",
                metadata={"category": "routine", "difficulty": "hard", "avg_completion_rate": 0.52}
            ))
        else:
            recommendations.append(Recommendation(
                id="habit_simple",
                type="habit",
                title="One Glass of Water",
                description="Start small: drink one glass of water every morning",
                relevance_score=88,
                reason="Build consistency with this easy habit",
                metadata={"category": "nutrition", "difficulty": "very_easy", "avg_completion_rate": 0.91}
            ))
        
        # Popular among similar users
        recommendations.append(Recommendation(
            id="habit_sleep",
            type="habit",
            title="Sleep Schedule",
            description="Track sleep quality and maintain consistent bedtime",
            relevance_score=82,
            reason="85% of users with similar goals track this",
            metadata={"category": "sleep", "difficulty": "medium", "avg_completion_rate": 0.68}
        ))
        
        return sorted(recommendations, key=lambda x: x.relevance_score, reverse=True)[:limit]
    
    # ==================== MEAL PLAN RECOMMENDATIONS ====================
    
    def recommend_meal_plans(self, user_id: str, limit: int = 5) -> List[Recommendation]:
        """
        Recommend meal plans based on:
        - Dietary preferences and restrictions
        - Health goals
        - Past meal plan success
        - Seasonal ingredients
        """
        recommendations = []
        
        dietary_prefs = self._get_dietary_preferences(user_id)
        health_goals = self._get_user_goals(user_id)
        
        # Weight loss plans
        if "weight_loss" in health_goals:
            if "low_carb" in dietary_prefs:
                recommendations.append(Recommendation(
                    id="meal_keto",
                    type="meal_plan",
                    title="Keto Weight Loss Plan",
                    description="Low-carb, high-fat meals designed for sustainable weight loss",
                    relevance_score=93,
                    reason="Matches your low-carb preference and weight loss goal",
                    metadata={
                        "calories_per_day": 1500,
                        "macros": {"protein": "30%", "carbs": "10%", "fat": "60%"},
                        "duration_days": 28,
                        "difficulty": "medium",
                        "success_rate": 0.76
                    }
                ))
            
            recommendations.append(Recommendation(
                id="meal_mediterranean",
                type="meal_plan",
                title="Mediterranean Slim",
                description="Heart-healthy Mediterranean diet for gradual weight loss",
                relevance_score=88,
                reason="Balanced approach with proven long-term results",
                metadata={
                    "calories_per_day": 1600,
                    "macros": {"protein": "25%", "carbs": "45%", "fat": "30%"},
                    "duration_days": 30,
                    "difficulty": "easy",
                    "success_rate": 0.82
                }
            ))
        
        # Muscle gain plans
        if "muscle_gain" in health_goals or "fitness" in health_goals:
            recommendations.append(Recommendation(
                id="meal_high_protein",
                type="meal_plan",
                title="High Protein Muscle Builder",
                description="Protein-rich meals to support muscle growth and recovery",
                relevance_score=91,
                reason="Optimized for your muscle building goals",
                metadata={
                    "calories_per_day": 2400,
                    "macros": {"protein": "40%", "carbs": "35%", "fat": "25%"},
                    "duration_days": 42,
                    "difficulty": "medium",
                    "success_rate": 0.79
                }
            ))
        
        # Vegan options
        if "vegan" in dietary_prefs:
            recommendations.append(Recommendation(
                id="meal_vegan",
                type="meal_plan",
                title="Complete Vegan Nutrition",
                description="Plant-based meals with all essential nutrients",
                relevance_score=95,
                reason="100% plant-based, perfectly aligned with your values",
                metadata={
                    "calories_per_day": 1800,
                    "macros": {"protein": "20%", "carbs": "55%", "fat": "25%"},
                    "duration_days": 28,
                    "difficulty": "medium",
                    "success_rate": 0.74
                }
            ))
        
        # Quick & easy
        recommendations.append(Recommendation(
            id="meal_quick",
            type="meal_plan",
            title="15-Minute Healthy Meals",
            description="Nutritious recipes ready in 15 minutes or less",
            relevance_score=79,
            reason="Perfect for busy schedules",
            metadata={
                "calories_per_day": 1700,
                "prep_time_minutes": 15,
                "duration_days": 14,
                "difficulty": "easy",
                "success_rate": 0.88
            }
        ))
        
        return sorted(recommendations, key=lambda x: x.relevance_score, reverse=True)[:limit]
    
    # ==================== WORKOUT RECOMMENDATIONS ====================
    
    def recommend_workouts(self, user_id: str, limit: int = 5) -> List[Recommendation]:
        """
        Recommend workout programs based on:
        - Fitness level
        - Available equipment
        - Time availability
        - Goals (strength, cardio, flexibility)
        """
        recommendations = []
        
        fitness_level = self._get_fitness_level(user_id)
        available_equipment = self._get_available_equipment(user_id)
        time_available = self._get_available_time(user_id)
        goals = self._get_user_goals(user_id)
        
        # Beginner home workouts
        if fitness_level == "beginner" or "home" in available_equipment:
            recommendations.append(Recommendation(
                id="workout_beginner_home",
                type="workout",
                title="Beginner Home Workout",
                description="No-equipment full-body workout perfect for beginners",
                relevance_score=94,
                reason="Start your fitness journey safely at home",
                metadata={
                    "duration_minutes": 20,
                    "difficulty": "beginner",
                    "equipment": "none",
                    "focus": ["full_body", "cardio"],
                    "calories_burned": 150
                }
            ))
        
        # HIIT for weight loss
        if "weight_loss" in goals and time_available < 30:
            recommendations.append(Recommendation(
                id="workout_hiit",
                type="workout",
                title="Quick HIIT Blast",
                description="High-intensity interval training for maximum calorie burn",
                relevance_score=91,
                reason="Efficient fat burning in minimal time",
                metadata={
                    "duration_minutes": 15,
                    "difficulty": "intermediate",
                    "equipment": "none",
                    "focus": ["cardio", "fat_burn"],
                    "calories_burned": 200
                }
            ))
        
        # Strength training
        if "muscle_gain" in goals or "strength" in goals:
            if "gym" in available_equipment or "weights" in available_equipment:
                recommendations.append(Recommendation(
                    id="workout_strength",
                    type="workout",
                    title="Progressive Strength Program",
                    description="Build muscle with compound movements and progressive overload",
                    relevance_score=93,
                    reason="Scientifically designed for muscle growth",
                    metadata={
                        "duration_minutes": 45,
                        "difficulty": "intermediate",
                        "equipment": ["weights", "bench"],
                        "focus": ["strength", "muscle"],
                        "program_weeks": 8
                    }
                ))
        
        # Yoga for flexibility
        if "flexibility" in goals or "stress_management" in goals:
            recommendations.append(Recommendation(
                id="workout_yoga",
                type="workout",
                title="Morning Yoga Flow",
                description="Gentle yoga sequence to improve flexibility and reduce stress",
                relevance_score=87,
                reason="Perfect for recovery and mental clarity",
                metadata={
                    "duration_minutes": 30,
                    "difficulty": "all_levels",
                    "equipment": "yoga_mat",
                    "focus": ["flexibility", "mindfulness"],
                    "calories_burned": 90
                }
            ))
        
        # Advanced challenge
        if fitness_level == "advanced":
            recommendations.append(Recommendation(
                id="workout_advanced",
                type="workout",
                title="Elite Athlete Challenge",
                description="Intense full-body conditioning for advanced athletes",
                relevance_score=85,
                reason="Push your limits with this elite program",
                metadata={
                    "duration_minutes": 60,
                    "difficulty": "advanced",
                    "equipment": ["pull_up_bar", "weights", "box"],
                    "focus": ["strength", "endurance", "power"],
                    "calories_burned": 500
                }
            ))
        
        return sorted(recommendations, key=lambda x: x.relevance_score, reverse=True)[:limit]
    
    # ==================== GROUP RECOMMENDATIONS ====================
    
    def recommend_groups(self, user_id: str, limit: int = 5) -> List[Recommendation]:
        """
        Recommend communities to join based on:
        - User interests and goals
        - Activity level
        - Group engagement rates
        - Geographic location (for local groups)
        """
        recommendations = []
        
        interests = self._get_user_interests(user_id)
        goals = self._get_user_goals(user_id)
        
        # Weight loss support
        if "weight_loss" in goals:
            recommendations.append(Recommendation(
                id="group_weight_loss",
                type="group",
                title="Weight Loss Warriors",
                description="Supportive community sharing tips, progress, and motivation",
                relevance_score=96,
                reason="Join 15k+ members on similar journeys",
                metadata={
                    "members": 15234,
                    "activity_level": "very_high",
                    "posts_per_day": 150,
                    "support_rating": 4.8
                }
            ))
        
        # Vegan community
        if "vegan" in interests:
            recommendations.append(Recommendation(
                id="group_vegan",
                type="group",
                title="Plant-Based Living",
                description="Recipes, tips, and support for vegan lifestyle",
                relevance_score=93,
                reason="Connect with fellow plant-based enthusiasts",
                metadata={
                    "members": 8921,
                    "activity_level": "high",
                    "posts_per_day": 85,
                    "support_rating": 4.7
                }
            ))
        
        # Fitness motivation
        if "fitness" in goals or "muscle_gain" in goals:
            recommendations.append(Recommendation(
                id="group_fitness",
                type="group",
                title="Fitness Motivation Hub",
                description="Daily workout inspiration, form checks, and progress sharing",
                relevance_score=89,
                reason="Stay accountable with workout buddies",
                metadata={
                    "members": 22156,
                    "activity_level": "very_high",
                    "posts_per_day": 200,
                    "support_rating": 4.6
                }
            ))
        
        # Mental wellness
        if "stress_management" in goals or "mental_wellness" in goals:
            recommendations.append(Recommendation(
                id="group_wellness",
                type="group",
                title="Mindful Living Community",
                description="Meditation, mindfulness, and mental health support",
                relevance_score=91,
                reason="Find peace and support in this calming space",
                metadata={
                    "members": 6543,
                    "activity_level": "medium",
                    "posts_per_day": 45,
                    "support_rating": 4.9
                }
            ))
        
        # Local/nearby
        recommendations.append(Recommendation(
            id="group_local",
            type="group",
            title="Local Running Club",
            description="Weekly group runs and running events in your area",
            relevance_score=82,
            reason="Meet active people near you",
            metadata={
                "members": 342,
                "activity_level": "medium",
                "location_based": True,
                "events_per_month": 8,
                "support_rating": 4.5
            }
        ))
        
        return sorted(recommendations, key=lambda x: x.relevance_score, reverse=True)[:limit]
    
    # ==================== CHALLENGE RECOMMENDATIONS ====================
    
    def recommend_challenges(self, user_id: str, limit: int = 3) -> List[Recommendation]:
        """
        Recommend wellness challenges based on:
        - User's current streak and consistency
        - Past challenge completions
        - Seasonal campaigns
        - Social proof (friends participating)
        """
        recommendations = []
        
        consistency_score = self._get_user_consistency_score(user_id)
        friends_participating = self._get_friends_challenges(user_id)
        
        # Easy challenge for beginners
        if consistency_score < 0.5:
            recommendations.append(Recommendation(
                id="challenge_7day_water",
                type="challenge",
                title="7-Day Hydration Challenge",
                description="Drink 8 glasses of water daily for a week",
                relevance_score=92,
                reason="Build momentum with this achievable challenge",
                metadata={
                    "duration_days": 7,
                    "difficulty": "easy",
                    "participants": 3421,
                    "completion_rate": 0.84,
                    "badge_reward": "Hydration Hero"
                }
            ))
        
        # Medium challenge
        if 0.5 <= consistency_score < 0.8:
            recommendations.append(Recommendation(
                id="challenge_21day_habit",
                type="challenge",
                title="21-Day Habit Builder",
                description="Establish a new healthy habit in 3 weeks",
                relevance_score=88,
                reason="You're ready for a medium-term commitment",
                metadata={
                    "duration_days": 21,
                    "difficulty": "medium",
                    "participants": 1876,
                    "completion_rate": 0.67,
                    "badge_reward": "Habit Master"
                }
            ))
        
        # Advanced challenge
        if consistency_score >= 0.8:
            recommendations.append(Recommendation(
                id="challenge_30day_transformation",
                type="challenge",
                title="30-Day Total Transformation",
                description="Complete wellness overhaul: diet, exercise, and mindfulness",
                relevance_score=85,
                reason="Ready for the ultimate challenge?",
                metadata={
                    "duration_days": 30,
                    "difficulty": "hard",
                    "participants": 892,
                    "completion_rate": 0.52,
                    "badge_reward": "Transformation Champion"
                }
            ))
        
        # Social challenge
        if friends_participating:
            recommendations.append(Recommendation(
                id="challenge_social",
                type="challenge",
                title="Step Challenge with Friends",
                description="Compete with friends to reach 10k steps daily",
                relevance_score=94,
                reason=f"{len(friends_participating)} of your friends are participating!",
                metadata={
                    "duration_days": 14,
                    "difficulty": "medium",
                    "participants": 5234,
                    "social": True,
                    "friends_count": len(friends_participating),
                    "badge_reward": "Social Stepper"
                }
            ))
        
        # Seasonal challenge
        recommendations.append(Recommendation(
            id="challenge_seasonal",
            type="challenge",
            title="New Year Reset Challenge",
            description="Start fresh with holistic wellness practices",
            relevance_score=79,
            reason="Limited time seasonal challenge",
            metadata={
                "duration_days": 14,
                "difficulty": "medium",
                "participants": 8921,
                "seasonal": True,
                "ends_at": (datetime.utcnow() + timedelta(days=10)).isoformat(),
                "badge_reward": "Fresh Starter"
            }
        ))
        
        return sorted(recommendations, key=lambda x: x.relevance_score, reverse=True)[:limit]
    
    # ==================== PEOPLE TO FOLLOW ====================
    
    def recommend_users_to_follow(self, user_id: str, limit: int = 5) -> List[Recommendation]:
        """
        Recommend users to follow based on:
        - Shared interests
        - Similar goals
        - Content quality
        - Engagement patterns
        """
        recommendations = []
        
        user_interests = self._get_user_interests(user_id)
        
        # Wellness creators
        recommendations.append(Recommendation(
            id="user_creator_1",
            type="user",
            title="Sarah Johnson - Nutritionist",
            description="Certified nutritionist sharing evidence-based meal plans",
            relevance_score=94,
            reason="Creates content about your interests: nutrition, weight loss",
            metadata={
                "followers": 45200,
                "posts": 342,
                "engagement_rate": 0.08,
                "verified": True,
                "specialties": ["nutrition", "meal_planning"]
            },
            image_url="/avatars/sarah_j.jpg"
        ))
        
        recommendations.append(Recommendation(
            id="user_creator_2",
            type="user",
            title="Mike Chen - Fitness Coach",
            description="Home workout specialist, no gym required",
            relevance_score=91,
            reason="Perfect for your home workout interest",
            metadata={
                "followers": 78900,
                "posts": 521,
                "engagement_rate": 0.12,
                "verified": True,
                "specialties": ["home_workouts", "bodyweight"]
            },
            image_url="/avatars/mike_c.jpg"
        ))
        
        # Similar users (peer recommendations)
        recommendations.append(Recommendation(
            id="user_peer_1",
            type="user",
            title="Emma Williams",
            description="On a similar wellness journey, great progress!",
            relevance_score=87,
            reason="Similar goals and 85% habit completion rate",
            metadata={
                "followers": 234,
                "posts": 89,
                "mutual_friends": 5,
                "similar_goal_match": 0.85,
                "verified": False
            },
            image_url="/avatars/emma_w.jpg"
        ))
        
        # Local influencers
        recommendations.append(Recommendation(
            id="user_local",
            type="user",
            title="David Park - Yoga Instructor",
            description="Local yoga teacher offering online classes",
            relevance_score=83,
            reason="Based in your area, teaches mindfulness",
            metadata={
                "followers": 3400,
                "posts": 156,
                "location": "Your City",
                "verified": True,
                "specialties": ["yoga", "meditation"]
            },
            image_url="/avatars/david_p.jpg"
        ))
        
        # Rising stars
        recommendations.append(Recommendation(
            id="user_rising",
            type="user",
            title="Alex Rivera",
            description="Rising wellness creator with authentic content",
            relevance_score=79,
            reason="Fast-growing creator in your interest areas",
            metadata={
                "followers": 892,
                "posts": 67,
                "growth_rate": 0.45,
                "engagement_rate": 0.15,
                "verified": False
            },
            image_url="/avatars/alex_r.jpg"
        ))
        
        return sorted(recommendations, key=lambda x: x.relevance_score, reverse=True)[:limit]
    
    # ==================== HELPER METHODS (Simulated) ====================
    
    def _get_user_interests(self, user_id: str) -> List[str]:
        """Get user's interests"""
        return ["nutrition", "fitness", "mental_wellness", "weight_loss"]
    
    def _get_followed_categories(self, user_id: str) -> List[str]:
        """Get categories user follows"""
        return ["healthy_eating", "home_workouts", "meditation"]
    
    def _get_user_goals(self, user_id: str) -> List[str]:
        """Get user's health goals"""
        return ["weight_loss", "fitness", "stress_management"]
    
    def _get_current_habits(self, user_id: str) -> List[str]:
        """Get user's current habits"""
        return ["water_intake", "daily_steps"]
    
    def _is_user_consistent(self, user_id: str) -> bool:
        """Check if user is consistent with habits"""
        import random
        return random.random() > 0.5
    
    def _get_dietary_preferences(self, user_id: str) -> List[str]:
        """Get dietary preferences"""
        import random
        return random.choice([["low_carb"], ["vegan"], [], ["vegetarian"]])
    
    def _get_fitness_level(self, user_id: str) -> str:
        """Get user's fitness level"""
        import random
        return random.choice(["beginner", "intermediate", "advanced"])
    
    def _get_available_equipment(self, user_id: str) -> List[str]:
        """Get available workout equipment"""
        import random
        return random.choice([["home"], ["gym", "weights"], ["yoga_mat"], []])
    
    def _get_available_time(self, user_id: str) -> int:
        """Get available workout time in minutes"""
        import random
        return random.randint(15, 60)
    
    def _get_user_consistency_score(self, user_id: str) -> float:
        """Get user's habit consistency score"""
        import random
        return random.uniform(0.3, 0.95)
    
    def _get_friends_challenges(self, user_id: str) -> List[str]:
        """Get challenges friends are participating in"""
        import random
        if random.random() > 0.5:
            return ["step_challenge", "hydration_challenge"]
        return []
    
    def _content_based_recommendations(self, interests: List[str], limit: int) -> List[Recommendation]:
        """Generate content-based recommendations"""
        recs = []
        for i, interest in enumerate(interests[:limit]):
            recs.append(Recommendation(
                id=f"content_{interest}_{i}",
                type="content",
                title=f"Top {interest.replace('_', ' ').title()} Tips",
                description=f"Expert advice on {interest.replace('_', ' ')}",
                relevance_score=90 - i*5,
                reason=f"Based on your interest in {interest}",
                metadata={"category": interest, "views": 15000 - i*1000}
            ))
        return recs
    
    def _collaborative_filtering(self, user_id: str, limit: int) -> List[Recommendation]:
        """Generate collaborative filtering recommendations"""
        return [
            Recommendation(
                id="content_collab_1",
                type="content",
                title="Users Like You Also Read",
                description="Popular among users with similar profiles",
                relevance_score=85,
                reason="85% match with users similar to you",
                metadata={"similarity_score": 0.85, "users_liked": 2341}
            )
        ]
    
    def _trending_in_network(self, user_id: str, limit: int) -> List[Recommendation]:
        """Get trending content in user's network"""
        return [
            Recommendation(
                id="content_trending_1",
                type="content",
                title="Trending in Your Network",
                description="What your friends and followed creators are discussing",
                relevance_score=82,
                reason="Viral in your network right now",
                metadata={"shares": 456, "network_engagement": 0.23}
            )
        ]


# Singleton instance
recommendations_service = PersonalizedRecommendationsService()
