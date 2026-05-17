from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from app.core.database import get_db
from app.schemas.analytics import (
    AnalyticsEventCreate, AnalyticsEventResponse,
    DailyMetricsResponse, WeeklyMetricsResponse, MonthlyMetricsResponse,
    KPISnapshotResponse, DashboardSummaryResponse,
    FunnelAnalysisResponse, RetentionCohortResponse,
    EventTrendResponse, CategoryMetricsResponse,
    PerformanceMetricsResponse, UserFunnelResponse, CohortAnalysisResponse
)
from app.services.analytics_service import AnalyticsService
from app.models.user import User
from app.core.security import get_current_user

router = APIRouter(prefix="/analytics", tags=["Analytics"])


# ==================== Event Tracking Endpoints ====================

@router.post("/events", response_model=AnalyticsEventResponse)
def track_event(
    event: AnalyticsEventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Track a single analytics event.
    
    This endpoint is called whenever a user performs an action in the app.
    Events are used for analytics, personalization, and improving user experience.
    """
    service = AnalyticsService(db)
    
    event_data = event.model_dump()
    
    # Override user_id if not provided but user is authenticated
    if event_data.get("user_id") is None and current_user:
        event_data["user_id"] = current_user.id
    
    tracked_event = service.track_event(event_data)
    
    return tracked_event


@router.post("/events/bulk")
def track_bulk_events(
    events: List[AnalyticsEventCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Track multiple analytics events in bulk.
    
    Useful for batching events from client-side to reduce API calls.
    """
    service = AnalyticsService(db)
    
    events_data = [event.model_dump() for event in events]
    
    # Set user_id for all events if not provided
    for event_data in events_data:
        if event_data.get("user_id") is None and current_user:
            event_data["user_id"] = current_user.id
    
    count = service.track_bulk_events(events_data)
    
    return {"message": f"Successfully tracked {count} events", "count": count}


# ==================== Dashboard & Summary Endpoints ====================

@router.get("/dashboard", response_model=DashboardSummaryResponse)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive dashboard summary with key metrics.
    
    Returns a snapshot of the most important KPIs including:
    - User growth (DAU, WAU, MAU)
    - Engagement metrics
    - Retention rates
    - Content performance
    - Recent activity
    """
    # Check if user has admin or moderator role
    if current_user.role.value not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    service = AnalyticsService(db)
    summary = service.get_dashboard_summary()
    
    return summary


@router.get("/metrics/daily/{date}", response_model=DailyMetricsResponse)
def get_daily_metrics(
    date: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get aggregated daily metrics for a specific date.
    
    Date format: YYYY-MM-DD
    """
    if current_user.role.value not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    service = AnalyticsService(db)
    
    # Aggregate metrics if they don't exist
    metrics = service.aggregate_daily_metrics(date_obj)
    
    return metrics


@router.get("/metrics/trends")
def get_event_trends(
    days: int = Query(default=7, ge=1, le=90),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get event trends over time.
    
    Returns event counts and unique users per day for the specified period.
    """
    if current_user.role.value not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    service = AnalyticsService(db)
    trends = service.get_event_trends(days=days)
    
    return {"trends": trends, "period_days": days}


@router.get("/metrics/categories", response_model=List[CategoryMetricsResponse])
def get_category_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get metrics grouped by event category.
    
    Shows which areas of the app are most active.
    """
    if current_user.role.value not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    service = AnalyticsService(db)
    categories = service.get_category_metrics()
    
    return categories


# ==================== User Metrics Endpoints ====================

@router.get("/users/dau")
def get_dau(
    date: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get Daily Active Users count.
    
    Optional date parameter in YYYY-MM-DD format. Defaults to today.
    """
    if current_user.role.value not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    service = AnalyticsService(db)
    
    date_obj = None
    if date:
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format")
    
    dau = service.get_dau(date_obj)
    
    return {"dau": dau, "date": date or datetime.now().strftime("%Y-%m-%d")}


@router.get("/users/wau")
def get_wau(
    end_date: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get Weekly Active Users count."""
    if current_user.role.value not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    service = AnalyticsService(db)
    
    date_obj = None
    if end_date:
        try:
            date_obj = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format")
    
    wau = service.get_wau(date_obj)
    
    return {"wau": wau}


@router.get("/users/mau")
def get_mau(
    end_date: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get Monthly Active Users count."""
    if current_user.role.value not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    service = AnalyticsService(db)
    
    date_obj = None
    if end_date:
        try:
            date_obj = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format")
    
    mau = service.get_mau(date_obj)
    
    return {"mau": mau}


@router.get("/users/retention")
def get_retention_rate(
    cohort_date: str,
    days: int = Query(default=7, ge=1, le=30),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get retention rate for a specific cohort after N days.
    
    Cohort date format: YYYY-MM-DD
    """
    if current_user.role.value not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        cohort_date_obj = datetime.strptime(cohort_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")
    
    service = AnalyticsService(db)
    retention = service.get_retention_rate(cohort_date_obj, days)
    
    return {
        "cohort_date": cohort_date,
        "days_after": days,
        "retention_rate": retention,
        "retained_percentage": f"{retention:.2f}%"
    }


# ==================== Engagement Metrics Endpoints ====================

@router.get("/engagement/session-duration")
def get_avg_session_duration(
    date: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get average session duration in seconds."""
    if current_user.role.value not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    service = AnalyticsService(db)
    
    date_obj = None
    if date:
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format")
    
    duration = service.get_avg_session_duration(date_obj)
    
    return {
        "avg_session_duration_seconds": duration,
        "avg_session_duration_minutes": duration / 60,
        "date": date or datetime.now().strftime("%Y-%m-%d")
    }


@router.get("/engagement/sessions")
def get_total_sessions(
    date: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get total number of sessions for a date."""
    if current_user.role.value not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    service = AnalyticsService(db)
    
    date_obj = None
    if date:
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format")
    
    sessions = service.get_total_sessions(date_obj)
    
    return {"total_sessions": sessions, "date": date or datetime.now().strftime("%Y-%m-%d")}


@router.get("/engagement/bounce-rate")
def get_bounce_rate(
    date: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get bounce rate (percentage of single-page sessions)."""
    if current_user.role.value not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    service = AnalyticsService(db)
    
    date_obj = None
    if date:
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format")
    
    bounce_rate = service.get_bounce_rate(date_obj)
    
    return {
        "bounce_rate": bounce_rate,
        "bounce_rate_percentage": f"{bounce_rate:.2f}%",
        "date": date or datetime.now().strftime("%Y-%m-%d")
    }


# ==================== Content Metrics Endpoints ====================

@router.get("/content/metrics")
def get_content_metrics(
    date: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get content-related metrics (posts, likes, comments, shares, saves)."""
    if current_user.role.value not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    service = AnalyticsService(db)
    
    date_obj = None
    if date:
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format")
    
    metrics = service.get_content_metrics(date_obj)
    
    return {**metrics, "date": date or datetime.now().strftime("%Y-%m-%d")}


# ==================== Habit & Wellness Metrics Endpoints ====================

@router.get("/habits/metrics")
def get_habit_metrics(
    date: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get habit tracking metrics."""
    if current_user.role.value not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    service = AnalyticsService(db)
    
    date_obj = None
    if date:
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format")
    
    metrics = service.get_habit_metrics(date_obj)
    
    return {**metrics, "date": date or datetime.now().strftime("%Y-%m-%d")}


@router.get("/wellness/metrics")
def get_wellness_metrics(
    date: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get wellness metrics (meals, workouts, fasting)."""
    if current_user.role.value not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    service = AnalyticsService(db)
    
    date_obj = None
    if date:
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format")
    
    metrics = service.get_wellness_metrics(date_obj)
    
    return {**metrics, "date": date or datetime.now().strftime("%Y-%m-%d")}


# ==================== Social Metrics Endpoints ====================

@router.get("/social/metrics")
def get_social_metrics(
    date: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get social interaction metrics (follows, groups, messages)."""
    if current_user.role.value not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    service = AnalyticsService(db)
    
    date_obj = None
    if date:
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format")
    
    metrics = service.get_social_metrics(date_obj)
    
    return {**metrics, "date": date or datetime.now().strftime("%Y-%m-%d")}


# ==================== PWA Metrics Endpoints ====================

@router.get("/pwa/metrics")
def get_pwa_metrics(
    date: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get PWA-specific metrics (installs, offline usage, push notifications)."""
    if current_user.role.value not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    service = AnalyticsService(db)
    
    date_obj = None
    if date:
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format")
    
    metrics = service.get_pwa_metrics(date_obj)
    
    return {**metrics, "date": date or datetime.now().strftime("%Y-%m-%d")}


# ==================== Admin Aggregation Endpoints ====================

@router.post("/aggregate/daily")
def aggregate_daily_metrics(
    date: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Manually trigger daily metrics aggregation.
    
    This is typically run automatically, but can be triggered manually for backfilling.
    """
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    service = AnalyticsService(db)
    
    date_obj = None
    if date:
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format")
    
    metrics = service.aggregate_daily_metrics(date_obj)
    
    return {"message": "Daily metrics aggregated successfully", "date": metrics.date.isoformat()}


# ==================== KPI Snapshots ====================

@router.get("/kpi/snapshots/latest")
def get_latest_kpi_snapshot(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the latest KPI snapshot."""
    from app.models.analytics import KPISnapshot
    
    if current_user.role.value not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    snapshot = db.query(KPISnapshot).order_by(KPISnapshot.snapshot_date.desc()).first()
    
    if not snapshot:
        raise HTTPException(status_code=404, detail="No KPI snapshots available")
    
    return KPISnapshotResponse.model_validate(snapshot)


@router.get("/kpi/snapshots")
def get_kpi_snapshots(
    limit: int = Query(default=30, ge=1, le=365),
    snapshot_type: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get historical KPI snapshots."""
    from app.models.analytics import KPISnapshot
    
    if current_user.role.value not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    query = db.query(KPISnapshot).order_by(KPISnapshot.snapshot_date.desc())
    
    if snapshot_type:
        query = query.filter(KPISnapshot.snapshot_type == snapshot_type)
    
    snapshots = query.limit(limit).all()
    
    return {
        "snapshots": [KPISnapshotResponse.model_validate(s) for s in snapshots],
        "count": len(snapshots)
    }
