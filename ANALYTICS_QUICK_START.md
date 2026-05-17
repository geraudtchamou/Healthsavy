# Analytics Module - Quick Start Guide

## Files Created

### Models (`app/models/analytics.py`)
- `AnalyticsEvent` - Core event tracking table
- `DailyMetrics` - Daily aggregated metrics
- `WeeklyMetrics` - Weekly aggregated metrics
- `MonthlyMetrics` - Monthly trends and retention
- `UserFunnel` - Funnel progression tracking
- `CohortAnalysis` - Cohort retention analysis
- `PerformanceMetrics` - Technical performance
- `KPISnapshot` - KPI snapshots

### Schemas (`app/schemas/analytics.py`)
- `AnalyticsEventCreate` - Event creation schema
- `AnalyticsEventResponse` - Event response schema
- `DailyMetricsResponse` - Daily metrics schema
- `WeeklyMetricsResponse` - Weekly metrics schema
- `MonthlyMetricsResponse` - Monthly metrics schema
- `KPISnapshotResponse` - KPI snapshot schema
- `DashboardSummaryResponse` - Dashboard summary
- `FunnelAnalysisResponse` - Funnel analysis
- `RetentionCohortResponse` - Retention cohort
- `EventTrendResponse` - Event trends
- `CategoryMetricsResponse` - Category metrics

### Service (`app/services/analytics_service.py`)
- `AnalyticsService` class with 30+ methods for:
  - Event tracking (single & bulk)
  - User metrics (DAU, WAU, MAU, retention)
  - Engagement metrics (sessions, duration, bounce rate)
  - Content metrics (posts, likes, comments, shares)
  - Habit & wellness metrics
  - Social metrics
  - PWA metrics
  - Aggregation functions

### API (`app/api/analytics.py`)
25+ REST endpoints organized by category:
- Event tracking endpoints
- Dashboard & summary endpoints
- User metrics endpoints
- Engagement metrics endpoints
- Content metrics endpoints
- Habit & wellness endpoints
- Social metrics endpoints
- PWA metrics endpoints
- Admin aggregation endpoints

## Usage Examples

### Track an Event

```python
# Python client
import requests

response = requests.post(
    "http://localhost:8000/api/v1/analytics/events",
    headers={"Authorization": "Bearer YOUR_TOKEN"},
    json={
        "event_type": "habit_complete",
        "entity_type": "habit",
        "entity_id": 123,
        "properties": {"streak_days": 7},
        "value": 1
    }
)
```

### Get Dashboard Summary

```python
# Admin dashboard data
response = requests.get(
    "http://localhost:8000/api/v1/analytics/dashboard",
    headers={"Authorization": "Bearer ADMIN_TOKEN"}
)

# Returns:
{
    "dau": 1250,
    "wau": 5430,
    "mau": 18500,
    "new_users_today": 87,
    "avg_session_duration_minutes": 8.5,
    "day_1_retention": 45.2,
    "day_7_retention": 28.7,
    ...
}
```

### Get Daily Metrics

```python
response = requests.get(
    "http://localhost:8000/api/v1/analytics/metrics/daily/2024-01-15",
    headers={"Authorization": "Bearer ADMIN_TOKEN"}
)
```

### Get Event Trends

```python
# Last 30 days of trends
response = requests.get(
    "http://localhost:8000/api/v1/analytics/metrics/trends?days=30",
    headers={"Authorization": "Bearer ADMIN_TOKEN"}
)
```

## Key KPIs to Monitor

### Growth
- **DAU/WAU/MAU** - Active user counts
- **Stickiness Ratio** - DAU/WAU (target > 20%)

### Engagement
- **Avg Session Duration** - Time spent in app (target > 5 min)
- **Sessions per User** - Frequency (target > 2)
- **Bounce Rate** - Single-page sessions (target < 40%)

### Retention
- **Day 1 Retention** - Next day return (target > 40%)
- **Day 7 Retention** - Week return (target > 20%)
- **Day 30 Retention** - Month return (target > 10%)

### Health & Wellness
- **Habit Completion Rate** - (target > 60%)
- **Avg Streak Length** - (target > 7 days)
- **Workout Completion Rate** - (target > 70%)

## Database Migration

After adding the models, run migrations:

```bash
# The models will be auto-created on next app startup
# Or manually create tables using Alembic if configured
```

## Testing the Module

```bash
# Test imports
python -c "from app.models.analytics import AnalyticsEvent; print('✓ Models OK')"
python -c "from app.schemas.analytics import AnalyticsEventCreate; print('✓ Schemas OK')"
python -c "from app.services.analytics_service import AnalyticsService; print('✓ Service OK')"
python -c "from app.api.analytics import router; print('✓ API OK')"

# Start server and test endpoint
uvicorn app.main:app --reload
# Visit http://localhost:8000/docs for interactive API docs
```

## Next Steps

1. **Integrate event tracking** into all existing API endpoints
2. **Set up scheduled jobs** for daily metric aggregation
3. **Build admin dashboard** UI using the API endpoints
4. **Configure alerts** for key metric thresholds
5. **Add frontend tracking** for page views and user interactions
