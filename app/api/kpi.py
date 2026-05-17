from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import csv
import io

from app.core.database import get_db
from app.schemas.analytics import (
    KPISnapshotResponse, DashboardSummaryResponse,
    RetentionCohortResponse, FunnelAnalysisResponse,
    PerformanceMetricsResponse
)
from app.services.analytics_service import AnalyticsService
from app.models.user import User
from app.core.security import get_current_user

router = APIRouter(prefix="/analytics/kpi", tags=["KPI & Reports"])


# ==================== KPI Dashboard Endpoints ====================

@router.get("/dashboard/summary", response_model=DashboardSummaryResponse)
def get_kpi_dashboard(
    period: str = Query(default="7d", regex="^(1d|7d|30d|90d)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive KPI dashboard summary.
    
    Period options:
    - 1d: Last 24 hours
    - 7d: Last 7 days
    - 30d: Last 30 days
    - 90d: Last 90 days
    """
    if current_user.role.value not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    service = AnalyticsService(db)
    
    # Parse period
    days_map = {"1d": 1, "7d": 7, "30d": 30, "90d": 90}
    days = days_map.get(period, 7)
    
    summary = service.get_dashboard_summary()
    
    # Add period-specific calculations
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Calculate growth rates for the period
    previous_start = start_date - timedelta(days=days)
    
    # DAU comparison
    current_dau = service.get_dau(end_date)
    previous_dau = service.get_dau(previous_start)
    dau_growth = ((current_dau - previous_dau) / previous_dau * 100) if previous_dau > 0 else 0
    
    # Engagement comparison
    current_sessions = service.get_total_sessions(end_date)
    previous_sessions = service.get_total_sessions(previous_start)
    sessions_growth = ((current_sessions - previous_sessions) / previous_sessions * 100) if previous_sessions > 0 else 0
    
    summary["period"] = period
    summary["period_days"] = days
    summary["start_date"] = start_date.strftime("%Y-%m-%d")
    summary["end_date"] = end_date.strftime("%Y-%m-%d")
    summary["dau_growth_rate"] = round(dau_growth, 2)
    summary["sessions_growth_rate"] = round(sessions_growth, 2)
    
    return summary


@router.get("/snapshot", response_model=KPISnapshotResponse)
def get_kpi_snapshot(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current KPI snapshot with real-time metrics.
    
    Returns the most recent KPI values for quick monitoring.
    """
    if current_user.role.value not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    service = AnalyticsService(db)
    today = datetime.now()
    
    # Get today's metrics
    dau = service.get_dau(today)
    total_sessions = service.get_total_sessions(today)
    avg_session_duration = service.get_avg_session_duration(today)
    bounce_rate = service.get_bounce_rate(today)
    
    # Get content metrics
    content_metrics = service.get_content_metrics(today)
    
    # Get habit metrics
    habit_metrics = service.get_habit_metrics(today)
    
    # Get wellness metrics
    wellness_metrics = service.get_wellness_metrics(today)
    
    # Get social metrics
    social_metrics = service.get_social_metrics(today)
    
    snapshot = {
        "timestamp": datetime.now().isoformat(),
        "dau": dau,
        "wau": service.get_wau(today),
        "mau": service.get_mau(today),
        "total_sessions": total_sessions,
        "avg_session_duration_seconds": avg_session_duration,
        "bounce_rate_percentage": round(bounce_rate, 2),
        "posts_created_today": content_metrics.get("posts_created", 0),
        "total_engagements_today": (
            content_metrics.get("total_likes", 0) +
            content_metrics.get("total_comments", 0) +
            content_metrics.get("total_shares", 0) +
            content_metrics.get("total_saves", 0)
        ),
        "habits_tracked_today": habit_metrics.get("habits_tracked", 0),
        "habits_completed_today": habit_metrics.get("habits_completed", 0),
        "meals_logged_today": wellness_metrics.get("meals_logged", 0),
        "workouts_completed_today": wellness_metrics.get("workouts_completed", 0),
        "new_follows_today": social_metrics.get("new_follows", 0),
        "messages_sent_today": social_metrics.get("messages_sent", 0),
        "groups_joined_today": social_metrics.get("groups_joined", 0)
    }
    
    return snapshot


# ==================== Retention Analysis Endpoints ====================

@router.get("/retention/cohort", response_model=List[RetentionCohortResponse])
def get_retention_cohorts(
    weeks: int = Query(default=8, ge=1, le=12),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get retention cohort analysis.
    
    Shows how well you retain users from different signup weeks.
    """
    if current_user.role.value not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    service = AnalyticsService(db)
    
    cohorts = []
    today = datetime.now()
    
    # Generate cohorts for the last N weeks
    for week_offset in range(weeks):
        cohort_date = today - timedelta(weeks=week_offset)
        # Round to start of week (Monday)
        cohort_date = cohort_date - timedelta(days=cohort_date.weekday())
        
        cohort_data = {
            "cohort_week": cohort_date.strftime("%Y-%m-%d"),
            "cohort_size": 0,
            "retention_rates": {}
        }
        
        # Get cohort size (users who signed up this week)
        week_end = cohort_date + timedelta(days=7)
        cohort_users = db.query(User.id).filter(
            User.created_at >= cohort_date,
            User.created_at < week_end
        ).all()
        
        cohort_data["cohort_size"] = len(cohort_users)
        
        if cohort_data["cohort_size"] > 0:
            # Calculate retention for each week after signup
            for retention_week in range(1, min(weeks, 13)):
                retention_date = cohort_date + timedelta(weeks=retention_week)
                retention_end = retention_date + timedelta(days=7)
                
                if retention_end > today:
                    continue
                
                retained = db.query(func.count(distinct(AnalyticsEvent.user_id))).filter(
                    AnalyticsEvent.user_id.in_([u.id for u in cohort_users]),
                    AnalyticsEvent.timestamp >= retention_date,
                    AnalyticsEvent.timestamp < retention_end
                ).scalar() or 0
                
                retention_rate = (retained / cohort_data["cohort_size"]) * 100
                cohort_data["retention_rates"][f"week_{retention_week}"] = round(retention_rate, 2)
        
        cohorts.append(cohort_data)
    
    return cohorts


@router.get("/retention/daily", response_model=Dict[str, float])
def get_daily_retention(
    cohort_date: str,
    days: int = Query(default=30, ge=1, le=90),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get daily retention rates for a specific cohort.
    
    Cohort date format: YYYY-MM-DD
    """
    if current_user.role.value not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        cohort_date_obj = datetime.strptime(cohort_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")
    
    service = AnalyticsService(db)
    
    retention_rates = {}
    
    for day in range(1, days + 1):
        rate = service.get_retention_rate(cohort_date_obj, day)
        retention_rates[f"day_{day}"] = round(rate, 2)
    
    return retention_rates


# ==================== Funnel Analysis Endpoints ====================

@router.get("/funnel/acquisition", response_model=FunnelAnalysisResponse)
def get_acquisition_funnel(
    days: int = Query(default=7, ge=1, le=30),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get user acquisition funnel analysis.
    
    Tracks: Page View -> Sign Up -> Profile Complete -> First Action
    """
    if current_user.role.value not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    service = AnalyticsService(db)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    from app.models.analytics import AnalyticsEvent, EventType
    
    funnel = {
        "period_days": days,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "steps": []
    }
    
    # Step 1: Page Views
    page_views = db.query(func.count(AnalyticsEvent.id)).filter(
        AnalyticsEvent.timestamp >= start_date,
        AnalyticsEvent.timestamp <= end_date,
        AnalyticsEvent.event_type == EventType.PAGE_VIEW
    ).scalar() or 0
    
    funnel["steps"].append({
        "step": 1,
        "name": "Page Views",
        "count": page_views,
        "conversion_rate": 100.0
    })
    
    # Step 2: Sign Ups
    signups = db.query(func.count(User.id)).filter(
        User.created_at >= start_date,
        User.created_at <= end_date
    ).scalar() or 0
    
    conversion_2 = (signups / page_views * 100) if page_views > 0 else 0
    funnel["steps"].append({
        "step": 2,
        "name": "Sign Ups",
        "count": signups,
        "conversion_rate": round(conversion_2, 2)
    })
    
    # Step 3: Profile Complete (users who updated profile)
    # This would need a profile_updated_at field in User model
    # For now, estimate as 80% of signups
    profile_complete = int(signups * 0.8)
    conversion_3 = (profile_complete / signups * 100) if signups > 0 else 0
    funnel["steps"].append({
        "step": 3,
        "name": "Profile Completed",
        "count": profile_complete,
        "conversion_rate": round(conversion_3, 2)
    })
    
    # Step 4: First Action (any event after signup)
    new_user_ids = db.query(User.id).filter(
        User.created_at >= start_date,
        User.created_at <= end_date
    ).all()
    
    first_action = db.query(func.count(distinct(AnalyticsEvent.user_id))).filter(
        AnalyticsEvent.user_id.in_([u.id for u in new_user_ids]),
        AnalyticsEvent.timestamp >= start_date,
        AnalyticsEvent.timestamp <= end_date
    ).scalar() or 0
    
    conversion_4 = (first_action / profile_complete * 100) if profile_complete > 0 else 0
    funnel["steps"].append({
        "step": 4,
        "name": "First Action",
        "count": first_action,
        "conversion_rate": round(conversion_4, 2)
    })
    
    return funnel


@router.get("/funnel/activation", response_model=FunnelAnalysisResponse)
def get_activation_funnel(
    days: int = Query(default=7, ge=1, le=30),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get user activation funnel.
    
    Tracks: Sign Up -> First Post/Habit/Meal -> Regular Usage
    """
    if current_user.role.value not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    from app.models.analytics import AnalyticsEvent, EventType
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    funnel = {
        "period_days": days,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "steps": []
    }
    
    # New users in period
    new_users = db.query(User.id).filter(
        User.created_at >= start_date,
        User.created_at <= end_date
    ).all()
    
    total_new = len(new_users)
    
    funnel["steps"].append({
        "step": 1,
        "name": "New Users",
        "count": total_new,
        "conversion_rate": 100.0
    })
    
    # Users who created first content
    active_users = db.query(func.count(distinct(AnalyticsEvent.user_id))).filter(
        AnalyticsEvent.user_id.in_([u.id for u in new_users]),
        AnalyticsEvent.timestamp >= start_date,
        AnalyticsEvent.timestamp <= end_date,
        AnalyticsEvent.event_type.in_([
            EventType.POST_CREATE,
            EventType.HABIT_CREATE,
            EventType.MEAL_LOG,
            EventType.WORKOUT_START
        ])
    ).scalar() or 0
    
    conversion_2 = (active_users / total_new * 100) if total_new > 0 else 0
    funnel["steps"].append({
        "step": 2,
        "name": "Created First Content",
        "count": active_users,
        "conversion_rate": round(conversion_2, 2)
    })
    
    # Users with 3+ sessions (regular usage)
    # Simplified: count users with multiple events
    regular_users = db.query(AnalyticsEvent.user_id).filter(
        AnalyticsEvent.user_id.in_([u.id for u in new_users]),
        AnalyticsEvent.timestamp >= start_date,
        AnalyticsEvent.timestamp <= end_date
    ).group_by(AnalyticsEvent.user_id).having(
        func.count(AnalyticsEvent.id) >= 3
    ).all()
    
    regular_count = len(regular_users)
    conversion_3 = (regular_count / total_new * 100) if total_new > 0 else 0
    funnel["steps"].append({
        "step": 3,
        "name": "Regular Usage (3+ sessions)",
        "count": regular_count,
        "conversion_rate": round(conversion_3, 2)
    })
    
    return funnel


# ==================== Performance Metrics Endpoints ====================

@router.get("/performance/api", response_model=PerformanceMetricsResponse)
def get_api_performance(
    days: int = Query(default=7, ge=1, le=30),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get API performance metrics.
    
    Note: Requires API logging middleware to be implemented.
    """
    if current_user.role.value not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Placeholder - would need actual API request logging
    # This is where you'd integrate with your APM tool (e.g., New Relic, DataDog)
    
    return {
        "period_days": days,
        "avg_response_time_ms": 150,  # Placeholder
        "p95_response_time_ms": 300,  # Placeholder
        "p99_response_time_ms": 500,  # Placeholder
        "error_rate_percentage": 0.5,  # Placeholder
        "requests_per_second": 100,  # Placeholder
        "slowest_endpoints": [
            {"endpoint": "/api/analytics/dashboard", "avg_ms": 450},
            {"endpoint": "/api/posts/feed", "avg_ms": 320},
            {"endpoint": "/api/users/search", "avg_ms": 280}
        ]
    }


@router.get("/performance/pwa")
def get_pwa_performance(
    days: int = Query(default=7, ge=1, le=30),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get PWA performance metrics (Core Web Vitals).
    
    Tracks: LCP, FID, CLS, TTFB
    """
    if current_user.role.value not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    from app.models.analytics import AnalyticsEvent, EventType
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Get web vitals from events
    vitals_events = db.query(AnalyticsEvent.properties).filter(
        AnalyticsEvent.timestamp >= start_date,
        AnalyticsEvent.timestamp <= end_date,
        AnalyticsEvent.event_type == EventType.PERFORMANCE_METRIC,
        AnalyticsEvent.properties.isnot(None)
    ).all()
    
    # Extract metrics from properties (stored as JSON)
    lcp_values = []
    fid_values = []
    cls_values = []
    
    for event in vitals_events:
        props = event.properties if isinstance(event.properties, dict) else {}
        if "lcp" in props:
            lcp_values.append(props["lcp"])
        if "fid" in props:
            fid_values.append(props["fid"])
        if "cls" in props:
            cls_values.append(props["cls"])
    
    def avg(lst):
        return sum(lst) / len(lst) if lst else 0
    
    return {
        "period_days": days,
        "core_web_vitals": {
            "lcp_seconds": round(avg(lcp_values), 2) if lcp_values else 2.5,
            "fid_ms": round(avg(fid_values), 0) if fid_values else 100,
            "cls_score": round(avg(cls_values), 3) if cls_values else 0.1
        },
        "performance_grade": "A" if (avg(lcp_values) < 2.5 if lcp_values else True) else "B",
        "sample_size": len(vitals_events)
    }


# ==================== Report Generation Endpoints ====================

@router.get("/reports/daily/csv")
def generate_daily_report_csv(
    date: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate daily metrics report as CSV.
    
    Date format: YYYY-MM-DD. Defaults to yesterday.
    """
    if current_user.role.value not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    service = AnalyticsService(db)
    
    if date:
        try:
            report_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format")
    else:
        report_date = datetime.now() - timedelta(days=1)
    
    # Gather all metrics
    dau = service.get_dau(report_date)
    wau = service.get_wau(report_date)
    sessions = service.get_total_sessions(report_date)
    avg_duration = service.get_avg_session_duration(report_date)
    bounce_rate = service.get_bounce_rate(report_date)
    content = service.get_content_metrics(report_date)
    habits = service.get_habit_metrics(report_date)
    wellness = service.get_wellness_metrics(report_date)
    social = service.get_social_metrics(report_date)
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(["Health & Wellness PWA - Daily Report"])
    writer.writerow(["Date", report_date.strftime("%Y-%m-%d")])
    writer.writerow([])
    
    # User Metrics
    writer.writerow(["USER METRICS"])
    writer.writerow(["Metric", "Value"])
    writer.writerow(["Daily Active Users", dau])
    writer.writerow(["Weekly Active Users", wau])
    writer.writerow(["Total Sessions", sessions])
    writer.writerow(["Avg Session Duration (seconds)", round(avg_duration, 2)])
    writer.writerow(["Bounce Rate (%)", round(bounce_rate, 2)])
    writer.writerow([])
    
    # Content Metrics
    writer.writerow(["CONTENT METRICS"])
    writer.writerow(["Posts Created", content.get("posts_created", 0)])
    writer.writerow(["Posts Viewed", content.get("posts_viewed", 0)])
    writer.writerow(["Total Likes", content.get("total_likes", 0)])
    writer.writerow(["Total Comments", content.get("total_comments", 0)])
    writer.writerow(["Total Shares", content.get("total_shares", 0)])
    writer.writerow(["Total Saves", content.get("total_saves", 0)])
    writer.writerow([])
    
    # Habit Metrics
    writer.writerow(["HABIT TRACKING"])
    writer.writerow(["Habits Tracked", habits.get("habits_tracked", 0)])
    writer.writerow(["Habits Completed", habits.get("habits_completed", 0)])
    writer.writerow(["Streak Milestones", habits.get("streaks_maintained", 0)])
    writer.writerow([])
    
    # Wellness Metrics
    writer.writerow(["WELLNESS ACTIVITIES"])
    writer.writerow(["Meals Logged", wellness.get("meals_logged", 0)])
    writer.writerow(["Workouts Completed", wellness.get("workouts_completed", 0)])
    writer.writerow(["Fasting Sessions", wellness.get("fasting_sessions", 0)])
    writer.writerow([])
    
    # Social Metrics
    writer.writerow(["SOCIAL INTERACTIONS"])
    writer.writerow(["New Follows", social.get("new_follows", 0)])
    writer.writerow(["Groups Created", social.get("groups_created", 0)])
    writer.writerow(["Groups Joined", social.get("groups_joined", 0)])
    writer.writerow(["Messages Sent", social.get("messages_sent", 0)])
    
    # Return as file download
    from fastapi.responses import StreamingResponse
    
    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=daily_report_{report_date.strftime('%Y%m%d')}.csv"}
    )


@router.get("/reports/weekly/summary")
def generate_weekly_summary(
    week_offset: int = Query(default=0, ge=0, le=12),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate weekly summary report.
    
    Week 0 = current week, Week 1 = last week, etc.
    """
    if current_user.role.value not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    service = AnalyticsService(db)
    today = datetime.now()
    
    # Calculate week boundaries
    days_since_monday = today.weekday()
    week_start = today - timedelta(days=days_since_monday + (week_offset * 7))
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    week_end = week_start + timedelta(days=7)
    
    # Don't include future dates
    if week_end > today:
        week_end = today
    
    # Aggregate metrics for the week
    total_dau = 0
    for day in range((week_end - week_start).days + 1):
        current_day = week_start + timedelta(days=day)
        total_dau += service.get_dau(current_day)
    
    avg_dau = total_dau / max((week_end - week_start).days + 1, 1)
    
    return {
        "report_type": "weekly_summary",
        "week_number": week_start.isocalendar()[1],
        "year": week_start.year,
        "period": {
            "start": week_start.strftime("%Y-%m-%d"),
            "end": week_end.strftime("%Y-%m-%d")
        },
        "highlights": {
            "average_dau": round(avg_dau, 0),
            "total_new_users": service.get_new_users_count(7),
            "total_posts": "N/A",  # Would need date range query on posts
            "engagement_trend": "stable"  # Would need comparison logic
        },
        "generated_at": datetime.now().isoformat()
    }


# ==================== Alerts & Thresholds ====================

@router.get("/alerts/check")
def check_kpi_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Check KPIs against thresholds and return alerts.
    
    Monitors for unusual drops or spikes in key metrics.
    """
    if current_user.role.value not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    service = AnalyticsService(db)
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    
    alerts = []
    
    # Define thresholds
    thresholds = {
        "dau_drop_percentage": 20,  # Alert if DAU drops more than 20%
        "error_rate_threshold": 5,  # Alert if error rate exceeds 5%
        "session_duration_drop": 30,  # Alert if avg session drops 30%
        "bounce_rate_increase": 25  # Alert if bounce rate increases 25%
    }
    
    # Check DAU
    today_dau = service.get_dau(today)
    yesterday_dau = service.get_dau(yesterday)
    
    if yesterday_dau > 0:
        dau_change = ((today_dau - yesterday_dau) / yesterday_dau) * 100
        if dau_change < -thresholds["dau_drop_percentage"]:
            alerts.append({
                "severity": "high",
                "metric": "DAU",
                "message": f"DAU dropped by {abs(dau_change):.1f}% (from {yesterday_dau} to {today_dau})",
                "threshold": thresholds["dau_drop_percentage"]
            })
    
    # Check session duration
    today_duration = service.get_avg_session_duration(today)
    yesterday_duration = service.get_avg_session_duration(yesterday)
    
    if yesterday_duration > 0:
        duration_change = ((today_duration - yesterday_duration) / yesterday_duration) * 100
        if duration_change < -thresholds["session_duration_drop"]:
            alerts.append({
                "severity": "medium",
                "metric": "Session Duration",
                "message": f"Avg session duration dropped by {abs(duration_change):.1f}%",
                "threshold": thresholds["session_duration_drop"]
            })
    
    # Check bounce rate
    today_bounce = service.get_bounce_rate(today)
    yesterday_bounce = service.get_bounce_rate(yesterday)
    
    if yesterday_bounce > 0:
        bounce_change = ((today_bounce - yesterday_bounce) / yesterday_bounce) * 100
        if bounce_change > thresholds["bounce_rate_increase"]:
            alerts.append({
                "severity": "medium",
                "metric": "Bounce Rate",
                "message": f"Bounce rate increased by {bounce_change:.1f}%",
                "threshold": thresholds["bounce_rate_increase"]
            })
    
    return {
        "check_time": datetime.now().isoformat(),
        "alerts_count": len(alerts),
        "alerts": alerts,
        "status": "critical" if any(a["severity"] == "high" for a in alerts) else "normal"
    }


# Import required SQLAlchemy functions
from sqlalchemy import func, distinct
