from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, BigInteger, Text, JSON, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class EventType(enum.Enum):
    """Types of events that can be tracked"""
    # Authentication
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_REGISTER = "user_register"
    PASSWORD_RESET = "password_reset"
    
    # User Profile
    PROFILE_VIEW = "profile_view"
    PROFILE_UPDATE = "profile_update"
    PROFILE_PICTURE_UPLOAD = "profile_picture_upload"
    
    # Posts & Content
    POST_CREATE = "post_create"
    POST_VIEW = "post_view"
    POST_LIKE = "post_like"
    POST_UNLIKE = "post_unlike"
    POST_COMMENT = "post_comment"
    POST_SHARE = "post_share"
    POST_SAVE = "post_save"
    POST_DELETE = "post_delete"
    
    # Habits
    HABIT_CREATE = "habit_create"
    HABIT_TRACK = "habit_track"
    HABIT_COMPLETE = "habit_complete"
    HABIT_DELETE = "habit_delete"
    STREAK_MILESTONE = "streak_milestone"
    
    # Meal Planning
    MEAL_PLAN_CREATE = "meal_plan_create"
    MEAL_PLAN_VIEW = "meal_plan_view"
    MEAL_LOG = "meal_log"
    RECIPE_SAVE = "recipe_save"
    RECIPE_VIEW = "recipe_view"
    GROCERY_LIST_CREATE = "grocery_list_create"
    
    # Workout
    WORKOUT_PLAN_CREATE = "workout_plan_create"
    WORKOUT_PLAN_VIEW = "workout_plan_view"
    WORKOUT_START = "workout_start"
    WORKOUT_COMPLETE = "workout_complete"
    EXERCISE_LOG = "exercise_log"
    
    # Fasting
    FASTING_START = "fasting_start"
    FASTING_END = "fasting_end"
    FASTING_LOG = "fasting_log"
    
    # Groups & Community
    GROUP_CREATE = "group_create"
    GROUP_JOIN = "group_join"
    GROUP_LEAVE = "group_leave"
    GROUP_POST_CREATE = "group_post_create"
    GROUP_EVENT_CREATE = "group_event_create"
    GROUP_EVENT_JOIN = "group_event_join"
    
    # Messaging
    MESSAGE_SEND = "message_send"
    MESSAGE_READ = "message_read"
    CHAT_OPEN = "chat_open"
    
    # Discovery & Search
    SEARCH_PERFORM = "search_perform"
    CONTENT_DISCOVER = "content_discover"
    USER_FOLLOW = "user_follow"
    USER_UNFOLLOW = "user_unfollow"
    
    # Notifications
    NOTIFICATION_VIEW = "notification_view"
    NOTIFICATION_CLICK = "notification_click"
    
    # Gamification
    BADGE_EARNED = "badge_earned"
    XP_GAINED = "xp_gained"
    LEADERBOARD_VIEW = "leaderboard_view"
    CHALLENGE_JOIN = "challenge_join"
    CHALLENGE_COMPLETE = "challenge_complete"
    
    # PWA & Technical
    APP_INSTALL = "app_install"
    OFFLINE_MODE = "offline_mode"
    PUSH_NOTIFICATION_ENABLE = "push_notification_enable"
    PAGE_VIEW = "page_view"
    SCREEN_VIEW = "screen_view"
    FEATURE_ACCESS = "feature_access"
    
    # Admin & Moderation
    CONTENT_REPORT = "content_report"
    CONTENT_MODERATE = "content_moderate"
    USER_BAN = "user_ban"
    USER_UNBAN = "user_unban"


class DeviceType(enum.Enum):
    """Device types for tracking"""
    WEB = "web"
    MOBILE_WEB = "mobile_web"
    ANDROID_PWA = "android_pwa"
    IOS_PWA = "ios_pwa"
    DESKTOP_PWA = "desktop_pwa"


class Platform(enum.Enum):
    """Platform information"""
    CHROME = "chrome"
    FIREFOX = "firefox"
    SAFARI = "safari"
    EDGE = "edge"
    ANDROID = "android"
    IOS = "ios"
    WINDOWS = "windows"
    MACOS = "macos"
    LINUX = "linux"


class AnalyticsEvent(Base):
    """Core table for tracking all user activities"""
    __tablename__ = "analytics_events"

    id = Column(BigInteger, primary_key=True, index=True)
    
    # Event identification
    event_type = Column(Enum(EventType), nullable=False, index=True)
    event_category = Column(String(100), nullable=False, index=True)  # auth, content, habit, etc.
    event_name = Column(String(255), nullable=False)
    
    # User context
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    session_id = Column(String(255), nullable=True, index=True)
    
    # Entity context (what was interacted with)
    entity_type = Column(String(50), nullable=True)  # post, habit, meal_plan, etc.
    entity_id = Column(Integer, nullable=True)
    related_entity_type = Column(String(50), nullable=True)
    related_entity_id = Column(Integer, nullable=True)
    
    # Device & Platform context
    device_type = Column(Enum(DeviceType), nullable=True)
    platform = Column(Enum(Platform), nullable=True)
    browser = Column(String(100), nullable=True)
    os = Column(String(100), nullable=True)
    screen_resolution = Column(String(50), nullable=True)
    
    # Location context
    country = Column(String(100), nullable=True)
    region = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    timezone = Column(String(50), nullable=True)
    
    # Event metadata
    properties = Column(JSON, nullable=True)  # Additional event-specific data
    value = Column(Float, nullable=True)  # Numeric value associated with event
    duration_ms = Column(BigInteger, nullable=True)  # Duration in milliseconds if applicable
    
    # Referral & Navigation
    referrer_url = Column(Text, nullable=True)
    page_url = Column(Text, nullable=True)
    previous_page_url = Column(Text, nullable=True)
    
    # Timestamps
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Indexes for common queries
    __table_args__ = (
        # Composite indexes for efficient querying
        {'extend_existing': True}
    )


class DailyMetrics(Base):
    """Aggregated daily metrics for fast dashboard queries"""
    __tablename__ = "daily_metrics"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime(timezone=True), nullable=False, unique=True, index=True)
    
    # User metrics
    total_users = Column(Integer, default=0)
    new_users = Column(Integer, default=0)
    active_users = Column(Integer, default=0)  # DAU
    returning_users = Column(Integer, default=0)
    
    # Engagement metrics
    total_sessions = Column(Integer, default=0)
    avg_session_duration_seconds = Column(Float, default=0.0)
    total_page_views = Column(Integer, default=0)
    bounce_rate = Column(Float, default=0.0)
    
    # Content metrics
    posts_created = Column(Integer, default=0)
    posts_viewed = Column(Integer, default=0)
    total_likes = Column(Integer, default=0)
    total_comments = Column(Integer, default=0)
    total_shares = Column(Integer, default=0)
    total_saves = Column(Integer, default=0)
    
    # Habit tracking metrics
    habits_tracked = Column(Integer, default=0)
    habits_completed = Column(Integer, default=0)
    streaks_maintained = Column(Integer, default=0)
    
    # Wellness metrics
    meals_logged = Column(Integer, default=0)
    workouts_completed = Column(Integer, default=0)
    fasting_sessions = Column(Integer, default=0)
    
    # Social metrics
    new_follows = Column(Integer, default=0)
    groups_created = Column(Integer, default=0)
    groups_joined = Column(Integer, default=0)
    messages_sent = Column(Integer, default=0)
    
    # PWA metrics
    pwa_installs = Column(Integer, default=0)
    offline_sessions = Column(Integer, default=0)
    push_notifications_enabled = Column(Integer, default=0)
    
    # Retention cohorts (stored as JSON for flexibility)
    retention_data = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class WeeklyMetrics(Base):
    """Aggregated weekly metrics"""
    __tablename__ = "weekly_metrics"

    id = Column(Integer, primary_key=True, index=True)
    week_start_date = Column(DateTime(timezone=True), nullable=False, unique=True, index=True)
    week_end_date = Column(DateTime(timezone=True), nullable=False)
    
    # User metrics
    total_users = Column(Integer, default=0)
    new_users = Column(Integer, default=0)
    weekly_active_users = Column(Integer, default=0)  # WAU
    returning_users = Column(Integer, default=0)
    
    # Engagement metrics
    total_sessions = Column(Integer, default=0)
    avg_session_duration_seconds = Column(Float, default=0.0)
    total_page_views = Column(Integer, default=0)
    
    # Content metrics
    posts_created = Column(Integer, default=0)
    total_likes = Column(Integer, default=0)
    total_comments = Column(Integer, default=0)
    
    # Habit & Wellness metrics
    habits_tracked = Column(Integer, default=0)
    habits_completed = Column(Integer, default=0)
    workouts_completed = Column(Integer, default=0)
    meals_logged = Column(Integer, default=0)
    
    # Social metrics
    new_follows = Column(Integer, default=0)
    messages_sent = Column(Integer, default=0)
    
    # Retention rate
    retention_rate = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class MonthlyMetrics(Base):
    """Aggregated monthly metrics for long-term trends"""
    __tablename__ = "monthly_metrics"

    id = Column(Integer, primary_key=True, index=True)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    unique_constraint = Column(String(20), unique=True, index=True)  # Format: YYYY-MM
    
    # User metrics
    total_users = Column(Integer, default=0)
    new_users = Column(Integer, default=0)
    monthly_active_users = Column(Integer, default=0)  # MAU
    churned_users = Column(Integer, default=0)
    
    # Engagement metrics
    total_sessions = Column(Integer, default=0)
    avg_session_duration_seconds = Column(Float, default=0.0)
    total_page_views = Column(Integer, default=0)
    
    # Content metrics
    posts_created = Column(Integer, default=0)
    total_likes = Column(Integer, default=0)
    total_comments = Column(Integer, default=0)
    total_shares = Column(Integer, default=0)
    
    # Habit & Wellness metrics
    habits_tracked = Column(Integer, default=0)
    habits_completed = Column(Integer, default=0)
    workouts_completed = Column(Integer, default=0)
    meals_logged = Column(Integer, default=0)
    fasting_sessions = Column(Integer, default=0)
    
    # Social metrics
    new_follows = Column(Integer, default=0)
    groups_created = Column(Integer, default=0)
    messages_sent = Column(Integer, default=0)
    
    # Revenue metrics (for future monetization)
    premium_subscriptions = Column(Integer, default=0)
    revenue = Column(Float, default=0.0)
    
    # Retention rates
    day_1_retention = Column(Float, default=0.0)
    day_7_retention = Column(Float, default=0.0)
    day_30_retention = Column(Float, default=0.0)
    
    # Health outcomes (aggregated, anonymized)
    avg_streak_length = Column(Float, default=0.0)
    avg_workouts_per_user = Column(Float, default=0.0)
    avg_meals_logged_per_user = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class UserFunnel(Base):
    """Track user progression through key funnels"""
    __tablename__ = "user_funnels"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Funnel type
    funnel_name = Column(String(100), nullable=False, index=True)  # onboarding, first_habit, first_post, etc.
    funnel_stage = Column(String(100), nullable=False)
    
    # Stage completion
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Time metrics
    time_to_complete_seconds = Column(BigInteger, nullable=True)
    
    # Drop-off tracking
    dropped_off = Column(Boolean, default=False)
    drop_off_reason = Column(String(255), nullable=True)
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CohortAnalysis(Base):
    """Cohort-based retention analysis"""
    __tablename__ = "cohort_analysis"

    id = Column(Integer, primary_key=True, index=True)
    
    # Cohort definition
    cohort_type = Column(String(50), nullable=False)  # signup_date, feature_adoption, etc.
    cohort_period = Column(String(20), nullable=False, index=True)  # YYYY-MM or YYYY-Www
    cohort_size = Column(Integer, nullable=False)
    
    # Retention by period
    period_0_retention = Column(Float, default=100.0)  # Initial period
    period_1_retention = Column(Float, default=0.0)   # Day 1 / Week 1
    period_7_retention = Column(Float, default=0.0)   # Day 7 / Week 2
    period_14_retention = Column(Float, default=0.0)  # Day 14 / Week 3
    period_30_retention = Column(Float, default=0.0)  # Day 30 / Month 1
    
    # Activity metrics per cohort
    avg_sessions_per_user = Column(Float, default=0.0)
    avg_actions_per_user = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PerformanceMetrics(Base):
    """Technical performance metrics"""
    __tablename__ = "performance_metrics"

    id = Column(Integer, primary_key=True, index=True)
    
    # Metric type
    metric_type = Column(String(100), nullable=False, index=True)  # page_load, api_response, error_rate, etc.
    endpoint = Column(String(255), nullable=True, index=True)
    
    # Performance values
    avg_response_time_ms = Column(Float, default=0.0)
    p95_response_time_ms = Column(Float, default=0.0)
    p99_response_time_ms = Column(Float, default=0.0)
    
    # Error tracking
    error_count = Column(Integer, default=0)
    error_rate = Column(Float, default=0.0)
    
    # Throughput
    requests_per_minute = Column(Float, default=0.0)
    
    # Period
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class KPISnapshot(Base):
    """Snapshot of key KPIs at regular intervals"""
    __tablename__ = "kpi_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    snapshot_date = Column(DateTime(timezone=True), nullable=False, index=True)
    snapshot_type = Column(String(50), nullable=False)  # daily, weekly, monthly
    
    # Growth KPIs
    dau = Column(Integer, default=0)  # Daily Active Users
    wau = Column(Integer, default=0)  # Weekly Active Users
    mau = Column(Integer, default=0)  # Monthly Active Users
    dau_wau_ratio = Column(Float, default=0.0)  # Stickiness
    wau_mau_ratio = Column(Float, default=0.0)
    
    # Acquisition KPIs
    new_users_today = Column(Integer, default=0)
    signup_conversion_rate = Column(Float, default=0.0)
    
    # Engagement KPIs
    avg_session_duration_minutes = Column(Float, default=0.0)
    sessions_per_user = Column(Float, default=0.0)
    page_views_per_session = Column(Float, default=0.0)
    bounce_rate = Column(Float, default=0.0)
    
    # Retention KPIs
    day_1_retention = Column(Float, default=0.0)
    day_7_retention = Column(Float, default=0.0)
    day_30_retention = Column(Float, default=0.0)
    churn_rate = Column(Float, default=0.0)
    
    # Content KPIs
    posts_per_dau = Column(Float, default=0.0)
    engagement_rate = Column(Float, default=0.0)  # (likes+comments+shares)/views
    viral_coefficient = Column(Float, default=0.0)
    
    # Habit KPIs
    habit_completion_rate = Column(Float, default=0.0)
    avg_streak_length = Column(Float, default=0.0)
    active_habitors = Column(Integer, default=0)
    
    # Wellness KPIs
    workouts_completed = Column(Integer, default=0)
    meals_logged = Column(Integer, default=0)
    fasting_hours_total = Column(Float, default=0.0)
    
    # Social KPIs
    messages_per_user = Column(Float, default=0.0)
    groups_per_user = Column(Float, default=0.0)
    follows_per_user = Column(Float, default=0.0)
    
    # PWA KPIs
    pwa_installs_total = Column(Integer, default=0)
    offline_usage_rate = Column(Float, default=0.0)
    push_notification_ctr = Column(Float, default=0.0)
    
    # Health Impact KPIs (aggregated, anonymized)
    users_with_improved_streaks = Column(Integer, default=0)
    avg_health_score_improvement = Column(Float, default=0.0)
    
    # Additional data
    additional_data = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
