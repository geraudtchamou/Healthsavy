from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, distinct, extract, cast, Date, Integer, text
from sqlalchemy.sql import literal_column
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from functools import lru_cache
import hashlib
from app.models.analytics import (
    AnalyticsEvent, DailyMetrics, WeeklyMetrics, MonthlyMetrics,
    UserFunnel, CohortAnalysis, PerformanceMetrics, KPISnapshot,
    EventType, DeviceType, Platform
)
from app.models.user import User
from app.models.post import Post
from app.models.habit import Habit
from app.models.group import Group
from app.models.message import Message


class AnalyticsService:
    """Service for analytics tracking and reporting with performance optimizations"""
    
    # Cache for event type mapping to avoid repeated imports
    _event_type_mapping = None
    
    def __init__(self, db: Session):
        self.db = db
        self._query_cache = {}
        self._cache_ttl = {}
        self.CACHE_TTL_SECONDS = 300  # 5 minutes cache
    
    def _get_event_type_mapping(self):
        """Lazy load event type mapping"""
        if self._event_type_mapping is None:
            from app.schemas.analytics import EVENT_TYPE_MAPPING
            self._event_type_mapping = EVENT_TYPE_MAPPING
        return self._event_type_mapping
    
    def _get_date_range(self, date: Optional[datetime] = None) -> Tuple[datetime, datetime]:
        """Calculate date range once and reuse"""
        if date is None:
            date = datetime.now()
        date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        date_end = date_start + timedelta(days=1)
        return date_start, date_end
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached result is still valid"""
        if key not in self._cache_ttl:
            return False
        return (datetime.now() - self._cache_ttl[key]).total_seconds() < self.CACHE_TTL_SECONDS
    
    def _get_cached(self, key: str) -> Optional[Any]:
        """Get cached result if valid"""
        if self._is_cache_valid(key):
            return self._query_cache.get(key)
        return None
    
    def _set_cached(self, key: str, value: Any):
        """Cache a result"""
        self._query_cache[key] = value
        self._cache_ttl[key] = datetime.now()
    
    def _clear_cache(self):
        """Clear all cached results"""
        self._query_cache.clear()
        self._cache_ttl.clear()
    
    # ==================== Event Tracking ====================
    
    def track_event(self, event_data: Dict[str, Any]) -> AnalyticsEvent:
        """Track a single analytics event"""
        event_type_mapping = self._get_event_type_mapping()
        
        event_type_str = event_data.get("event_type")
        
        # Determine event category
        event_category = event_type_mapping.get(event_type_str, "other")
        
        # Create event
        event = AnalyticsEvent(
            event_type=EventType(event_type_str),
            event_category=event_category.value,
            event_name=event_data.get("event_name", event_type_str),
            user_id=event_data.get("user_id"),
            session_id=event_data.get("session_id"),
            entity_type=event_data.get("entity_type"),
            entity_id=event_data.get("entity_id"),
            related_entity_type=event_data.get("related_entity_type"),
            related_entity_id=event_data.get("related_entity_id"),
            device_type=event_data.get("device_type"),
            platform=event_data.get("platform"),
            browser=event_data.get("browser"),
            os=event_data.get("os"),
            screen_resolution=event_data.get("screen_resolution"),
            country=event_data.get("country"),
            region=event_data.get("region"),
            city=event_data.get("city"),
            timezone=event_data.get("timezone"),
            properties=event_data.get("properties"),
            value=event_data.get("value"),
            duration_ms=event_data.get("duration_ms"),
            referrer_url=event_data.get("referrer_url"),
            page_url=event_data.get("page_url"),
            previous_page_url=event_data.get("previous_page_url"),
        )
        
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        
        return event
    
    def track_bulk_events(self, events_data: List[Dict[str, Any]], batch_size: int = 1000) -> int:
        """Track multiple events in bulk with optimized batching"""
        event_type_mapping = self._get_event_type_mapping()
        
        events = []
        for i, event_data in enumerate(events_data):
            event_type_str = event_data.get("event_type")
            event_category = event_type_mapping.get(event_type_str, "other")
            
            event = AnalyticsEvent(
                event_type=EventType(event_type_str),
                event_category=event_category.value,
                event_name=event_data.get("event_name", event_type_str),
                user_id=event_data.get("user_id"),
                session_id=event_data.get("session_id"),
                entity_type=event_data.get("entity_type"),
                entity_id=event_data.get("entity_id"),
                **{k: v for k, v in event_data.items() 
                   if k not in ["event_type", "event_name"]}
            )
            events.append(event)
            
            # Batch commit for better performance
            if len(events) >= batch_size:
                self.db.bulk_save_objects(events, return_defaults=False)
                self.db.commit()
                events = []
        
        # Commit remaining events
        if events:
            self.db.bulk_save_objects(events, return_defaults=False)
            self.db.commit()
        
        return len(events_data)
    
    # ==================== User Metrics ====================
    
    def get_dau(self, date: Optional[datetime] = None) -> int:
        """Get Daily Active Users with caching"""
        cache_key = f"dau_{date.isoformat() if date else 'today'}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached
        
        date_start, date_end = self._get_date_range(date)
        
        count = self.db.query(func.count(distinct(AnalyticsEvent.user_id))).filter(
            AnalyticsEvent.timestamp >= date_start,
            AnalyticsEvent.timestamp < date_end,
            AnalyticsEvent.user_id.isnot(None)
        ).scalar()
        
        result = count or 0
        self._set_cached(cache_key, result)
        return result
    
    def get_wau(self, end_date: Optional[datetime] = None) -> int:
        """Get Weekly Active Users with caching"""
        cache_key = f"wau_{end_date.isoformat() if end_date else 'now'}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached
        
        start_date = (end_date or datetime.now()) - timedelta(days=7)
        
        count = self.db.query(func.count(distinct(AnalyticsEvent.user_id))).filter(
            AnalyticsEvent.timestamp >= start_date,
            AnalyticsEvent.timestamp <= (end_date or datetime.now()),
            AnalyticsEvent.user_id.isnot(None)
        ).scalar()
        
        result = count or 0
        self._set_cached(cache_key, result)
        return result
    
    def get_mau(self, end_date: Optional[datetime] = None) -> int:
        """Get Monthly Active Users with caching"""
        cache_key = f"mau_{end_date.isoformat() if end_date else 'now'}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached
        
        start_date = (end_date or datetime.now()) - timedelta(days=30)
        
        count = self.db.query(func.count(distinct(AnalyticsEvent.user_id))).filter(
            AnalyticsEvent.timestamp >= start_date,
            AnalyticsEvent.timestamp <= (end_date or datetime.now()),
            AnalyticsEvent.user_id.isnot(None)
        ).scalar()
        
        result = count or 0
        self._set_cached(cache_key, result)
        return result
    
    def get_new_users_count(self, days: int = 1) -> int:
        """Get count of new users in the last N days with caching"""
        cache_key = f"new_users_{days}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        count = self.db.query(func.count(User.id)).filter(
            User.created_at >= cutoff_date
        ).scalar()
        
        result = count or 0
        self._set_cached(cache_key, result)
        return result
    
    def get_retention_rate(self, cohort_date: datetime, days: int) -> float:
        """Calculate retention rate for a cohort after N days - optimized with single query"""
        cache_key = f"retention_{cohort_date.isoformat()}_{days}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached
        
        # Get cohort size
        cohort_start = cohort_date.replace(hour=0, minute=0, second=0, microsecond=0)
        cohort_end = cohort_start + timedelta(days=1)
        
        # Use a single correlated query instead of loading all user IDs
        target_date = cohort_start + timedelta(days=days)
        target_end = target_date + timedelta(days=1)
        
        # Optimized query using EXISTS subquery
        retained_count = self.db.query(func.count(distinct(AnalyticsEvent.user_id))).filter(
            AnalyticsEvent.timestamp >= target_date,
            AnalyticsEvent.timestamp < target_end,
            AnalyticsEvent.user_id.in_(
                self.db.query(User.id).filter(
                    User.created_at >= cohort_start,
                    User.created_at < cohort_end
                )
            )
        ).scalar() or 0
        
        cohort_size = self.db.query(func.count(User.id)).filter(
            User.created_at >= cohort_start,
            User.created_at < cohort_end
        ).scalar() or 0
        
        result = (retained_count / cohort_size) * 100 if cohort_size > 0 else 0.0
        self._set_cached(cache_key, result)
        return result
    
    # ==================== Engagement Metrics ====================
    
    def get_avg_session_duration(self, date: Optional[datetime] = None) -> float:
        """Get average session duration in seconds with caching"""
        cache_key = f"avg_session_{date.isoformat() if date else 'today'}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached
        
        date_start, date_end = self._get_date_range(date)
        
        result = self.db.query(func.avg(AnalyticsEvent.duration_ms)).filter(
            AnalyticsEvent.timestamp >= date_start,
            AnalyticsEvent.timestamp < date_end,
            AnalyticsEvent.duration_ms.isnot(None)
        ).scalar()
        
        calculated = (result / 1000) if result else 0.0
        self._set_cached(cache_key, calculated)
        return calculated
    
    def get_total_sessions(self, date: Optional[datetime] = None) -> int:
        """Get total number of sessions with caching"""
        cache_key = f"sessions_{date.isoformat() if date else 'today'}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached
        
        date_start, date_end = self._get_date_range(date)
        
        count = self.db.query(func.count(distinct(AnalyticsEvent.session_id))).filter(
            AnalyticsEvent.timestamp >= date_start,
            AnalyticsEvent.timestamp < date_end,
            AnalyticsEvent.session_id.isnot(None)
        ).scalar()
        
        result = count or 0
        self._set_cached(cache_key, result)
        return result
    
    def get_bounce_rate(self, date: Optional[datetime] = None) -> float:
        """Calculate bounce rate (single-page sessions) with caching"""
        cache_key = f"bounce_{date.isoformat() if date else 'today'}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached
        
        date_start, date_end = self._get_date_range(date)
        
        # Optimized: Use a single query with subquery instead of loading all sessions
        single_session_count = self.db.query(
            func.count(distinct(AnalyticsEvent.session_id))
        ).filter(
            AnalyticsEvent.timestamp >= date_start,
            AnalyticsEvent.timestamp < date_end,
            AnalyticsEvent.session_id.isnot(None),
            AnalyticsEvent.event_type == EventType.PAGE_VIEW,
            AnalyticsEvent.session_id.in_(
                self.db.query(AnalyticsEvent.session_id).filter(
                    AnalyticsEvent.timestamp >= date_start,
                    AnalyticsEvent.timestamp < date_end,
                    AnalyticsEvent.session_id.isnot(None),
                    AnalyticsEvent.event_type == EventType.PAGE_VIEW
                ).group_by(AnalyticsEvent.session_id).having(
                    func.count(AnalyticsEvent.id) == 1
                )
            )
        ).scalar() or 0
        
        total_sessions = self.get_total_sessions(date)
        
        result = (single_session_count / total_sessions) * 100 if total_sessions > 0 else 0.0
        self._set_cached(cache_key, result)
        return result
    
    # ==================== Content Metrics ====================
    
    def get_content_metrics(self, date: Optional[datetime] = None) -> Dict[str, int]:
        """Get content-related metrics for a given date"""
        if date is None:
            date = datetime.now()
        
        date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        date_end = date_start + timedelta(days=1)
        
        metrics = {}
        
        # Posts created
        metrics['posts_created'] = self.db.query(func.count(Post.id)).filter(
            Post.created_at >= date_start,
            Post.created_at < date_end
        ).scalar() or 0
        
        # Post views
        metrics['posts_viewed'] = self.db.query(func.count(AnalyticsEvent.id)).filter(
            AnalyticsEvent.timestamp >= date_start,
            AnalyticsEvent.timestamp < date_end,
            AnalyticsEvent.event_type == EventType.POST_VIEW
        ).scalar() or 0
        
        # Likes
        metrics['total_likes'] = self.db.query(func.count(AnalyticsEvent.id)).filter(
            AnalyticsEvent.timestamp >= date_start,
            AnalyticsEvent.timestamp < date_end,
            AnalyticsEvent.event_type.in_([EventType.POST_LIKE])
        ).scalar() or 0
        
        # Comments
        metrics['total_comments'] = self.db.query(func.count(AnalyticsEvent.id)).filter(
            AnalyticsEvent.timestamp >= date_start,
            AnalyticsEvent.timestamp < date_end,
            AnalyticsEvent.event_type == EventType.POST_COMMENT
        ).scalar() or 0
        
        # Shares
        metrics['total_shares'] = self.db.query(func.count(AnalyticsEvent.id)).filter(
            AnalyticsEvent.timestamp >= date_start,
            AnalyticsEvent.timestamp < date_end,
            AnalyticsEvent.event_type == EventType.POST_SHARE
        ).scalar() or 0
        
        # Saves
        metrics['total_saves'] = self.db.query(func.count(AnalyticsEvent.id)).filter(
            AnalyticsEvent.timestamp >= date_start,
            AnalyticsEvent.timestamp < date_end,
            AnalyticsEvent.event_type == EventType.POST_SAVE
        ).scalar() or 0
        
        return metrics
    
    # ==================== Habit & Wellness Metrics ====================
    
    def get_habit_metrics(self, date: Optional[datetime] = None) -> Dict[str, int]:
        """Get habit tracking metrics"""
        if date is None:
            date = datetime.now()
        
        date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        date_end = date_start + timedelta(days=1)
        
        metrics = {}
        
        # Habits tracked
        metrics['habits_tracked'] = self.db.query(func.count(AnalyticsEvent.id)).filter(
            AnalyticsEvent.timestamp >= date_start,
            AnalyticsEvent.timestamp < date_end,
            AnalyticsEvent.event_type.in_([EventType.HABIT_TRACK, EventType.HABIT_COMPLETE])
        ).scalar() or 0
        
        # Habits completed
        metrics['habits_completed'] = self.db.query(func.count(AnalyticsEvent.id)).filter(
            AnalyticsEvent.timestamp >= date_start,
            AnalyticsEvent.timestamp < date_end,
            AnalyticsEvent.event_type == EventType.HABIT_COMPLETE
        ).scalar() or 0
        
        # Streak milestones
        metrics['streaks_maintained'] = self.db.query(func.count(AnalyticsEvent.id)).filter(
            AnalyticsEvent.timestamp >= date_start,
            AnalyticsEvent.timestamp < date_end,
            AnalyticsEvent.event_type == EventType.STREAK_MILESTONE
        ).scalar() or 0
        
        return metrics
    
    def get_wellness_metrics(self, date: Optional[datetime] = None) -> Dict[str, int]:
        """Get wellness-related metrics"""
        if date is None:
            date = datetime.now()
        
        date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        date_end = date_start + timedelta(days=1)
        
        metrics = {}
        
        # Meals logged
        metrics['meals_logged'] = self.db.query(func.count(AnalyticsEvent.id)).filter(
            AnalyticsEvent.timestamp >= date_start,
            AnalyticsEvent.timestamp < date_end,
            AnalyticsEvent.event_type == EventType.MEAL_LOG
        ).scalar() or 0
        
        # Workouts completed
        metrics['workouts_completed'] = self.db.query(func.count(AnalyticsEvent.id)).filter(
            AnalyticsEvent.timestamp >= date_start,
            AnalyticsEvent.timestamp < date_end,
            AnalyticsEvent.event_type == EventType.WORKOUT_COMPLETE
        ).scalar() or 0
        
        # Fasting sessions
        metrics['fasting_sessions'] = self.db.query(func.count(AnalyticsEvent.id)).filter(
            AnalyticsEvent.timestamp >= date_start,
            AnalyticsEvent.timestamp < date_end,
            AnalyticsEvent.event_type == EventType.FASTING_END
        ).scalar() or 0
        
        return metrics
    
    # ==================== Social Metrics ====================
    
    def get_social_metrics(self, date: Optional[datetime] = None) -> Dict[str, int]:
        """Get social interaction metrics"""
        if date is None:
            date = datetime.now()
        
        date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        date_end = date_start + timedelta(days=1)
        
        metrics = {}
        
        # New follows
        metrics['new_follows'] = self.db.query(func.count(AnalyticsEvent.id)).filter(
            AnalyticsEvent.timestamp >= date_start,
            AnalyticsEvent.timestamp < date_end,
            AnalyticsEvent.event_type == EventType.USER_FOLLOW
        ).scalar() or 0
        
        # Groups created
        metrics['groups_created'] = self.db.query(func.count(AnalyticsEvent.id)).filter(
            AnalyticsEvent.timestamp >= date_start,
            AnalyticsEvent.timestamp < date_end,
            AnalyticsEvent.event_type == EventType.GROUP_CREATE
        ).scalar() or 0
        
        # Groups joined
        metrics['groups_joined'] = self.db.query(func.count(AnalyticsEvent.id)).filter(
            AnalyticsEvent.timestamp >= date_start,
            AnalyticsEvent.timestamp < date_end,
            AnalyticsEvent.event_type == EventType.GROUP_JOIN
        ).scalar() or 0
        
        # Messages sent
        metrics['messages_sent'] = self.db.query(func.count(AnalyticsEvent.id)).filter(
            AnalyticsEvent.timestamp >= date_start,
            AnalyticsEvent.timestamp < date_end,
            AnalyticsEvent.event_type == EventType.MESSAGE_SEND
        ).scalar() or 0
        
        return metrics
    
    # ==================== PWA Metrics ====================
    
    def get_pwa_metrics(self, date: Optional[datetime] = None) -> Dict[str, int]:
        """Get PWA-specific metrics"""
        if date is None:
            date = datetime.now()
        
        date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        date_end = date_start + timedelta(days=1)
        
        metrics = {}
        
        # PWA installs
        metrics['pwa_installs'] = self.db.query(func.count(AnalyticsEvent.id)).filter(
            AnalyticsEvent.timestamp >= date_start,
            AnalyticsEvent.timestamp < date_end,
            AnalyticsEvent.event_type == EventType.APP_INSTALL
        ).scalar() or 0
        
        # Offline sessions
        metrics['offline_sessions'] = self.db.query(func.count(AnalyticsEvent.id)).filter(
            AnalyticsEvent.timestamp >= date_start,
            AnalyticsEvent.timestamp < date_end,
            AnalyticsEvent.event_type == EventType.OFFLINE_MODE
        ).scalar() or 0
        
        # Push notifications enabled
        metrics['push_notifications_enabled'] = self.db.query(func.count(AnalyticsEvent.id)).filter(
            AnalyticsEvent.timestamp >= date_start,
            AnalyticsEvent.timestamp < date_end,
            AnalyticsEvent.event_type == EventType.PUSH_NOTIFICATION_ENABLE
        ).scalar() or 0
        
        return metrics
    
    # ==================== Aggregation ====================
    
    def aggregate_daily_metrics(self, date: Optional[datetime] = None) -> DailyMetrics:
        """Aggregate all daily metrics and store in DailyMetrics table"""
        if date is None:
            date = datetime.now()
        
        date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Check if already exists
        existing = self.db.query(DailyMetrics).filter(
            DailyMetrics.date == date_start
        ).first()
        
        if existing:
            return existing
        
        # Gather all metrics
        content_metrics = self.get_content_metrics(date)
        habit_metrics = self.get_habit_metrics(date)
        wellness_metrics = self.get_wellness_metrics(date)
        social_metrics = self.get_social_metrics(date)
        pwa_metrics = self.get_pwa_metrics(date)
        
        daily = DailyMetrics(
            date=date_start,
            total_users=self.db.query(func.count(User.id)).scalar() or 0,
            new_users=self.get_new_users_count(1),
            active_users=self.get_dau(date),
            returning_users=self.get_dau(date) - self.get_new_users_count(1),
            total_sessions=self.get_total_sessions(date),
            avg_session_duration_seconds=self.get_avg_session_duration(date),
            bounce_rate=self.get_bounce_rate(date),
            **content_metrics,
            **habit_metrics,
            **wellness_metrics,
            **social_metrics,
            **pwa_metrics,
        )
        
        self.db.add(daily)
        self.db.commit()
        self.db.refresh(daily)
        
        return daily
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get comprehensive dashboard summary"""
        today = datetime.now()
        
        return {
            # Current period metrics
            "dau": self.get_dau(today),
            "wau": self.get_wau(today),
            "mau": self.get_mau(today),
            "new_users_today": self.get_new_users_count(1),
            "new_users_this_week": self.get_new_users_count(7),
            "new_users_this_month": self.get_new_users_count(30),
            
            # Engagement
            "avg_session_duration_minutes": self.get_avg_session_duration(today) / 60,
            "total_posts_today": self.get_content_metrics(today)['posts_created'],
            "total_habits_tracked_today": self.get_habit_metrics(today)['habits_tracked'],
            "total_workouts_today": self.get_wellness_metrics(today)['workouts_completed'],
            
            # Retention
            "day_1_retention": self.get_retention_rate(today - timedelta(days=1), 1),
            "day_7_retention": self.get_retention_rate(today - timedelta(days=7), 7),
            "day_30_retention": self.get_retention_rate(today - timedelta(days=30), 30),
            
            # Growth trends (simplified)
            "user_growth_rate": self._calculate_user_growth_rate(),
            "engagement_growth_rate": self._calculate_engagement_growth_rate(),
            
            # Top content categories
            "top_categories": self._get_top_content_categories(),
            
            # Recent activity
            "recent_events_count": self._get_recent_events_count(),
        }
    
    def _calculate_user_growth_rate(self) -> float:
        """Calculate user growth rate (week over week)"""
        today = datetime.now()
        current_week_users = self.get_new_users_count(7)
        previous_week_users = self.get_new_users_count(14) - current_week_users
        
        if previous_week_users == 0:
            return 100.0 if current_week_users > 0 else 0.0
        
        return ((current_week_users - previous_week_users) / previous_week_users) * 100
    
    def _calculate_engagement_growth_rate(self) -> float:
        """Calculate engagement growth rate"""
        today = datetime.now()
        current_dau = self.get_dau(today)
        previous_dau = self.get_dau(today - timedelta(days=7))
        
        if previous_dau == 0:
            return 100.0 if current_dau > 0 else 0.0
        
        return ((current_dau - previous_dau) / previous_dau) * 100
    
    def _get_top_content_categories(self) -> List[Dict[str, Any]]:
        """Get top content categories by engagement"""
        results = self.db.query(
            AnalyticsEvent.entity_type,
            func.count(AnalyticsEvent.id).label('count')
        ).filter(
            AnalyticsEvent.event_type.in_([
                EventType.POST_VIEW, EventType.POST_LIKE, EventType.POST_COMMENT
            ]),
            AnalyticsEvent.entity_type.isnot(None)
        ).group_by(AnalyticsEvent.entity_type).order_by(
            func.count(AnalyticsEvent.id).desc()
        ).limit(5).all()
        
        return [{"category": r.entity_type, "count": r.count} for r in results]
    
    def _get_recent_events_count(self) -> int:
        """Get count of recent events (last 24 hours)"""
        cutoff = datetime.now() - timedelta(hours=24)
        
        count = self.db.query(func.count(AnalyticsEvent.id)).filter(
            AnalyticsEvent.timestamp >= cutoff
        ).scalar()
        
        return count or 0
    
    def get_event_trends(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get event trends over time"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        results = self.db.query(
            cast(AnalyticsEvent.timestamp, Date).label('date'),
            AnalyticsEvent.event_type,
            func.count(AnalyticsEvent.id).label('count'),
            func.count(distinct(AnalyticsEvent.user_id)).label('unique_users')
        ).filter(
            AnalyticsEvent.timestamp >= start_date,
            AnalyticsEvent.timestamp <= end_date
        ).group_by(
            cast(AnalyticsEvent.timestamp, Date),
            AnalyticsEvent.event_type
        ).order_by(
            cast(AnalyticsEvent.timestamp, Date).desc(),
            func.count(AnalyticsEvent.id).desc()
        ).all()
        
        return [
            {
                "date": r.date.isoformat(),
                "event_type": r.event_type.value,
                "count": r.count,
                "unique_users": r.unique_users
            }
            for r in results
        ]
    
    def get_category_metrics(self) -> List[Dict[str, Any]]:
        """Get metrics grouped by event category"""
        results = self.db.query(
            AnalyticsEvent.event_category,
            func.count(AnalyticsEvent.id).label('total_events'),
            func.count(distinct(AnalyticsEvent.user_id)).label('unique_users')
        ).filter(
            AnalyticsEvent.timestamp >= datetime.now() - timedelta(days=30)
        ).group_by(
            AnalyticsEvent.event_category
        ).order_by(
            func.count(AnalyticsEvent.id).desc()
        ).all()
        
        return [
            {
                "category": r.event_category,
                "total_events": r.total_events,
                "unique_users": r.unique_users,
                "top_events": []  # Would need additional query
            }
            for r in results
        ]
