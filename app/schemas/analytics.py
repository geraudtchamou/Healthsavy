from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class EventCategory(str, Enum):
    """Event categories for grouping"""
    AUTH = "auth"
    PROFILE = "profile"
    CONTENT = "content"
    HABIT = "habit"
    MEAL = "meal"
    WORKOUT = "workout"
    FASTING = "fasting"
    GROUP = "group"
    MESSAGE = "message"
    DISCOVERY = "discovery"
    NOTIFICATION = "notification"
    GAMIFICATION = "gamification"
    PWA = "pwa"
    ADMIN = "admin"


# Event Type Mapping
EVENT_TYPE_MAPPING = {
    # Auth
    "user_login": EventCategory.AUTH,
    "user_logout": EventCategory.AUTH,
    "user_register": EventCategory.AUTH,
    "password_reset": EventCategory.AUTH,
    
    # Profile
    "profile_view": EventCategory.PROFILE,
    "profile_update": EventCategory.PROFILE,
    "profile_picture_upload": EventCategory.PROFILE,
    
    # Content
    "post_create": EventCategory.CONTENT,
    "post_view": EventCategory.CONTENT,
    "post_like": EventCategory.CONTENT,
    "post_unlike": EventCategory.CONTENT,
    "post_comment": EventCategory.CONTENT,
    "post_share": EventCategory.CONTENT,
    "post_save": EventCategory.CONTENT,
    "post_delete": EventCategory.CONTENT,
    
    # Habits
    "habit_create": EventCategory.HABIT,
    "habit_track": EventCategory.HABIT,
    "habit_complete": EventCategory.HABIT,
    "habit_delete": EventCategory.HABIT,
    "streak_milestone": EventCategory.HABIT,
    
    # Meals
    "meal_plan_create": EventCategory.MEAL,
    "meal_plan_view": EventCategory.MEAL,
    "meal_log": EventCategory.MEAL,
    "recipe_save": EventCategory.MEAL,
    "recipe_view": EventCategory.MEAL,
    "grocery_list_create": EventCategory.MEAL,
    
    # Workouts
    "workout_plan_create": EventCategory.WORKOUT,
    "workout_plan_view": EventCategory.WORKOUT,
    "workout_start": EventCategory.WORKOUT,
    "workout_complete": EventCategory.WORKOUT,
    "exercise_log": EventCategory.WORKOUT,
    
    # Fasting
    "fasting_start": EventCategory.FASTING,
    "fasting_end": EventCategory.FASTING,
    "fasting_log": EventCategory.FASTING,
    
    # Groups
    "group_create": EventCategory.GROUP,
    "group_join": EventCategory.GROUP,
    "group_leave": EventCategory.GROUP,
    "group_post_create": EventCategory.GROUP,
    "group_event_create": EventCategory.GROUP,
    "group_event_join": EventCategory.GROUP,
    
    # Messages
    "message_send": EventCategory.MESSAGE,
    "message_read": EventCategory.MESSAGE,
    "chat_open": EventCategory.MESSAGE,
    
    # Discovery
    "search_perform": EventCategory.DISCOVERY,
    "content_discover": EventCategory.DISCOVERY,
    "user_follow": EventCategory.DISCOVERY,
    "user_unfollow": EventCategory.DISCOVERY,
    
    # Notifications
    "notification_view": EventCategory.NOTIFICATION,
    "notification_click": EventCategory.NOTIFICATION,
    
    # Gamification
    "badge_earned": EventCategory.GAMIFICATION,
    "xp_gained": EventCategory.GAMIFICATION,
    "leaderboard_view": EventCategory.GAMIFICATION,
    "challenge_join": EventCategory.GAMIFICATION,
    "challenge_complete": EventCategory.GAMIFICATION,
    
    # PWA
    "app_install": EventCategory.PWA,
    "offline_mode": EventCategory.PWA,
    "push_notification_enable": EventCategory.PWA,
    "page_view": EventCategory.PWA,
    "screen_view": EventCategory.PWA,
    "feature_access": EventCategory.PWA,
    
    # Admin
    "content_report": EventCategory.ADMIN,
    "content_moderate": EventCategory.ADMIN,
    "user_ban": EventCategory.ADMIN,
    "user_unban": EventCategory.ADMIN,
}


class DeviceType(str, Enum):
    WEB = "web"
    MOBILE_WEB = "mobile_web"
    ANDROID_PWA = "android_pwa"
    IOS_PWA = "ios_pwa"
    DESKTOP_PWA = "desktop_pwa"


class Platform(str, Enum):
    CHROME = "chrome"
    FIREFOX = "firefox"
    SAFARI = "safari"
    EDGE = "edge"
    ANDROID = "android"
    IOS = "ios"
    WINDOWS = "windows"
    MACOS = "macos"
    LINUX = "linux"


class AnalyticsEventCreate(BaseModel):
    """Schema for creating an analytics event"""
    event_type: str
    event_name: Optional[str] = None
    user_id: Optional[int] = None
    session_id: Optional[str] = None
    
    # Entity context
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[int] = None
    
    # Device & Platform
    device_type: Optional[DeviceType] = None
    platform: Optional[Platform] = None
    browser: Optional[str] = None
    os: Optional[str] = None
    screen_resolution: Optional[str] = None
    
    # Location
    country: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    timezone: Optional[str] = None
    
    # Metadata
    properties: Optional[Dict[str, Any]] = None
    value: Optional[float] = None
    duration_ms: Optional[int] = None
    
    # Navigation
    referrer_url: Optional[str] = None
    page_url: Optional[str] = None
    previous_page_url: Optional[str] = None


class AnalyticsEventResponse(BaseModel):
    """Schema for analytics event response"""
    id: int
    event_type: str
    event_category: str
    event_name: str
    user_id: Optional[int]
    session_id: Optional[str]
    timestamp: datetime
    
    class Config:
        from_attributes = True


class DailyMetricsResponse(BaseModel):
    """Schema for daily metrics response"""
    id: int
    date: datetime
    total_users: int
    new_users: int
    active_users: int
    returning_users: int
    total_sessions: int
    avg_session_duration_seconds: float
    total_page_views: int
    bounce_rate: float
    posts_created: int
    posts_viewed: int
    total_likes: int
    total_comments: int
    total_shares: int
    total_saves: int
    habits_tracked: int
    habits_completed: int
    streaks_maintained: int
    meals_logged: int
    workouts_completed: int
    fasting_sessions: int
    new_follows: int
    groups_created: int
    groups_joined: int
    messages_sent: int
    pwa_installs: int
    offline_sessions: int
    
    class Config:
        from_attributes = True


class WeeklyMetricsResponse(BaseModel):
    """Schema for weekly metrics response"""
    id: int
    week_start_date: datetime
    week_end_date: datetime
    total_users: int
    new_users: int
    weekly_active_users: int
    returning_users: int
    total_sessions: int
    avg_session_duration_seconds: float
    total_page_views: int
    posts_created: int
    total_likes: int
    total_comments: int
    habits_tracked: int
    habits_completed: int
    workouts_completed: int
    meals_logged: int
    new_follows: int
    messages_sent: int
    retention_rate: float
    
    class Config:
        from_attributes = True


class MonthlyMetricsResponse(BaseModel):
    """Schema for monthly metrics response"""
    id: int
    month: int
    year: int
    unique_constraint: str
    total_users: int
    new_users: int
    monthly_active_users: int
    churned_users: int
    total_sessions: int
    avg_session_duration_seconds: float
    total_page_views: int
    posts_created: int
    total_likes: int
    total_comments: int
    total_shares: int
    habits_tracked: int
    habits_completed: int
    workouts_completed: int
    meals_logged: int
    fasting_sessions: int
    new_follows: int
    groups_created: int
    messages_sent: int
    premium_subscriptions: int
    revenue: float
    day_1_retention: float
    day_7_retention: float
    day_30_retention: float
    avg_streak_length: float
    avg_workouts_per_user: float
    avg_meals_logged_per_user: float
    
    class Config:
        from_attributes = True


class UserFunnelResponse(BaseModel):
    """Schema for user funnel response"""
    id: int
    user_id: int
    funnel_name: str
    funnel_stage: str
    is_completed: bool
    completed_at: Optional[datetime]
    time_to_complete_seconds: Optional[int]
    dropped_off: bool
    drop_off_reason: Optional[str]
    started_at: datetime
    
    class Config:
        from_attributes = True


class CohortAnalysisResponse(BaseModel):
    """Schema for cohort analysis response"""
    id: int
    cohort_type: str
    cohort_period: str
    cohort_size: int
    period_0_retention: float
    period_1_retention: float
    period_7_retention: float
    period_14_retention: float
    period_30_retention: float
    avg_sessions_per_user: float
    avg_actions_per_user: float
    
    class Config:
        from_attributes = True


class PerformanceMetricsResponse(BaseModel):
    """Schema for performance metrics response"""
    id: int
    metric_type: str
    endpoint: Optional[str]
    avg_response_time_ms: float
    p95_response_time_ms: float
    p99_response_time_ms: float
    error_count: int
    error_rate: float
    requests_per_minute: float
    period_start: datetime
    period_end: datetime
    
    class Config:
        from_attributes = True


class KPISnapshotResponse(BaseModel):
    """Schema for KPI snapshot response"""
    id: int
    snapshot_date: datetime
    snapshot_type: str
    
    # Growth KPIs
    dau: int
    wau: int
    mau: int
    dau_wau_ratio: float
    wau_mau_ratio: float
    
    # Acquisition KPIs
    new_users_today: int
    signup_conversion_rate: float
    
    # Engagement KPIs
    avg_session_duration_minutes: float
    sessions_per_user: float
    page_views_per_session: float
    bounce_rate: float
    
    # Retention KPIs
    day_1_retention: float
    day_7_retention: float
    day_30_retention: float
    churn_rate: float
    
    # Content KPIs
    posts_per_dau: float
    engagement_rate: float
    viral_coefficient: float
    
    # Habit KPIs
    habit_completion_rate: float
    avg_streak_length: float
    active_habitors: int
    
    # Wellness KPIs
    workouts_completed: int
    meals_logged: int
    fasting_hours_total: float
    
    # Social KPIs
    messages_per_user: float
    groups_per_user: float
    follows_per_user: float
    
    # PWA KPIs
    pwa_installs_total: int
    offline_usage_rate: float
    push_notification_ctr: float
    
    # Health Impact KPIs
    users_with_improved_streaks: int
    avg_health_score_improvement: float
    
    class Config:
        from_attributes = True


class DashboardSummaryResponse(BaseModel):
    """Summary dashboard response with key metrics"""
    # Current period metrics
    dau: int
    wau: int
    mau: int
    new_users_today: int
    new_users_this_week: int
    new_users_this_month: int
    
    # Engagement
    avg_session_duration_minutes: float
    total_posts_today: int
    total_habits_tracked_today: int
    total_workouts_today: int
    
    # Retention
    day_1_retention: float
    day_7_retention: float
    day_30_retention: float
    
    # Growth trends
    user_growth_rate: float
    engagement_growth_rate: float
    
    # Top content categories
    top_categories: List[Dict[str, Any]]
    
    # Recent activity summary
    recent_events_count: int
    
    class Config:
        from_attributes = True


class FunnelAnalysisResponse(BaseModel):
    """Funnel analysis response"""
    funnel_name: str
    total_users_started: int
    stage_data: List[Dict[str, Any]]  # [{stage, count, conversion_rate}, ...]
    overall_conversion_rate: float
    avg_time_to_complete_seconds: float
    drop_off_points: List[Dict[str, Any]]
    
    class Config:
        from_attributes = True


class RetentionCohortResponse(BaseModel):
    """Retention cohort analysis response"""
    cohort_period: str
    cohort_size: int
    retention_by_day: Dict[int, float]  # {day_number: retention_percentage}
    avg_sessions_per_user: float
    avg_actions_per_user: float
    
    class Config:
        from_attributes = True


class EventTrendResponse(BaseModel):
    """Event trend over time"""
    date: str
    event_type: str
    count: int
    unique_users: int
    
    class Config:
        from_attributes = True


class CategoryMetricsResponse(BaseModel):
    """Metrics by category"""
    category: str
    total_events: int
    unique_users: int
    top_events: List[Dict[str, Any]]
    
    class Config:
        from_attributes = True
