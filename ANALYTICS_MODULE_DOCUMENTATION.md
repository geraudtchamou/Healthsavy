# Analytics Module Implementation - Health & Wellness Social PWA

## Overview

This document describes the comprehensive analytics module implemented for tracking all user activities and measuring key performance indicators (KPIs) across the Health & Wellness Social PWA platform.

---

## 1. Database Models

### Core Event Tracking

#### `AnalyticsEvent`
Tracks every user interaction in the application.

**Fields:**
- `event_type`: Type of event (80+ event types defined)
- `event_category`: Category grouping (auth, content, habit, meal, workout, etc.)
- `user_id`: User who performed the action
- `session_id`: Session identifier for session-based analysis
- `entity_type/id`: What was interacted with (post, habit, meal_plan, etc.)
- `device_type`: Web, Mobile Web, Android PWA, iOS PWA, Desktop PWA
- `platform`: Browser/OS information
- `location`: Country, region, city, timezone
- `properties`: JSON metadata for event-specific data
- `duration_ms`: Duration for timed events
- `page_url`, `referrer_url`: Navigation context
- `timestamp`: When the event occurred

**Supported Event Types (80+):**
- **Authentication**: login, logout, register, password_reset
- **Profile**: view, update, picture_upload
- **Content**: post_create/view/like/comment/share/save/delete
- **Habits**: create, track, complete, delete, streak_milestone
- **Meals**: plan_create/view, meal_log, recipe_save/view, grocery_list_create
- **Workouts**: plan_create/view, start, complete, exercise_log
- **Fasting**: start, end, log
- **Groups**: create, join, leave, post_create, event_create/join
- **Messages**: send, read, chat_open
- **Discovery**: search, content_discover, follow/unfollow
- **Notifications**: view, click
- **Gamification**: badge_earned, xp_gained, leaderboard_view, challenge_join/complete
- **PWA**: app_install, offline_mode, push_notification_enable, page/screen_view
- **Admin**: content_report, moderate, user_ban/unban

### Aggregated Metrics Tables

#### `DailyMetrics`
Pre-aggregated daily metrics for fast dashboard queries.

**Metrics Tracked:**
- User metrics: total_users, new_users, active_users (DAU), returning_users
- Engagement: sessions, avg_duration, page_views, bounce_rate
- Content: posts_created/viewed, likes, comments, shares, saves
- Habits: tracked, completed, streaks_maintained
- Wellness: meals_logged, workouts_completed, fasting_sessions
- Social: new_follows, groups_created/joined, messages_sent
- PWA: installs, offline_sessions, push_notifications_enabled

#### `WeeklyMetrics`
Weekly aggregated metrics with retention rates.

#### `MonthlyMetrics`
Monthly trends with long-term retention and health outcomes.

**Additional Fields:**
- Revenue metrics (for future monetization)
- Retention rates: day_1, day_7, day_30
- Health outcomes: avg_streak_length, avg_workouts_per_user

#### `KPISnapshot`
Snapshot of key KPIs at regular intervals.

**KPI Categories:**
1. **Growth KPIs**: DAU, WAU, MAU, stickiness ratios
2. **Acquisition KPIs**: new_users, signup_conversion_rate
3. **Engagement KPIs**: session_duration, sessions_per_user, bounce_rate
4. **Retention KPIs**: day_1/7/30 retention, churn_rate
5. **Content KPIs**: posts_per_dau, engagement_rate, viral_coefficient
6. **Habit KPIs**: completion_rate, avg_streak_length, active_habitors
7. **Wellness KPIs**: workouts, meals, fasting_hours
8. **Social KPIs**: messages/groups/follows_per_user
9. **PWA KPIs**: installs, offline_usage, push_notification_ctr
10. **Health Impact KPIs**: improved_streaks, health_score_improvement

### Analysis Tables

#### `UserFunnel`
Track user progression through key funnels:
- Onboarding funnel
- First habit creation
- First post
- First workout
- Premium conversion

#### `CohortAnalysis`
Cohort-based retention analysis by signup date or feature adoption.

#### `PerformanceMetrics`
Technical performance monitoring:
- API response times (avg, p95, p99)
- Error rates
- Throughput (requests/minute)

---

## 2. API Endpoints

### Event Tracking

| Endpoint | Method | Description | Access |
|----------|--------|-------------|--------|
| `/api/v1/analytics/events` | POST | Track single event | Authenticated |
| `/api/v1/analytics/events/bulk` | POST | Track multiple events | Authenticated |

### Dashboard & Summary

| Endpoint | Method | Description | Access |
|----------|--------|-------------|--------|
| `/api/v1/analytics/dashboard` | GET | Comprehensive dashboard summary | Admin/Moderator |
| `/api/v1/analytics/metrics/daily/{date}` | GET | Daily metrics for specific date | Admin/Moderator |
| `/api/v1/analytics/metrics/trends` | GET | Event trends over time (7-90 days) | Admin/Moderator |
| `/api/v1/analytics/metrics/categories` | GET | Metrics by event category | Admin/Moderator |

### User Metrics

| Endpoint | Method | Description | Access |
|----------|--------|-------------|--------|
| `/api/v1/analytics/users/dau` | GET | Daily Active Users | Admin/Moderator |
| `/api/v1/analytics/users/wau` | GET | Weekly Active Users | Admin/Moderator |
| `/api/v1/analytics/users/mau` | GET | Monthly Active Users | Admin/Moderator |
| `/api/v1/analytics/users/retention` | GET | Retention rate for cohort | Admin/Moderator |

### Engagement Metrics

| Endpoint | Method | Description | Access |
|----------|--------|-------------|--------|
| `/api/v1/analytics/engagement/session-duration` | GET | Average session duration | Admin/Moderator |
| `/api/v1/analytics/engagement/sessions` | GET | Total sessions count | Admin/Moderator |
| `/api/v1/analytics/engagement/bounce-rate` | GET | Bounce rate percentage | Admin/Moderator |

### Content Metrics

| Endpoint | Method | Description | Access |
|----------|--------|-------------|--------|
| `/api/v1/analytics/content/metrics` | GET | Posts, likes, comments, shares, saves | Admin/Moderator |

### Habit & Wellness Metrics

| Endpoint | Method | Description | Access |
|----------|--------|-------------|--------|
| `/api/v1/analytics/habits/metrics` | GET | Habit tracking metrics | Admin/Moderator |
| `/api/v1/analytics/wellness/metrics` | GET | Meals, workouts, fasting metrics | Admin/Moderator |

### Social Metrics

| Endpoint | Method | Description | Access |
|----------|--------|-------------|--------|
| `/api/v1/analytics/social/metrics` | GET | Follows, groups, messages | Admin/Moderator |

### PWA Metrics

| Endpoint | Method | Description | Access |
|----------|--------|-------------|--------|
| `/api/v1/analytics/pwa/metrics` | GET | Installs, offline usage, push notifications | Admin/Moderator |

### Admin Operations

| Endpoint | Method | Description | Access |
|----------|--------|-------------|--------|
| `/api/v1/analytics/aggregate/daily` | POST | Trigger daily aggregation | Admin |
| `/api/v1/analytics/kpi/snapshots/latest` | GET | Latest KPI snapshot | Admin/Moderator |
| `/api/v1/analytics/kpi/snapshots` | GET | Historical KPI snapshots | Admin/Moderator |

---

## 3. Key Performance Indicators (KPIs)

### Growth Metrics

| KPI | Formula | Target |
|-----|---------|--------|
| **DAU** (Daily Active Users) | Unique users with events today | - |
| **WAU** (Weekly Active Users) | Unique users with events in 7 days | - |
| **MAU** (Monthly Active Users) | Unique users with events in 30 days | - |
| **Stickiness Ratio** | DAU / WAU | > 20% |
| **WAU/MAU Ratio** | WAU / MAU | > 40% |
| **User Growth Rate** | (Current week users - Previous week) / Previous week * 100 | > 10% weekly |

### Engagement Metrics

| KPI | Formula | Target |
|-----|---------|--------|
| **Avg Session Duration** | Total time / Total sessions | > 5 minutes |
| **Sessions per User** | Total sessions / DAU | > 2 |
| **Page Views per Session** | Total page views / Total sessions | > 3 |
| **Bounce Rate** | Single-page sessions / Total sessions * 100 | < 40% |
| **Engagement Rate** | (Likes + Comments + Shares) / Post Views * 100 | > 5% |

### Retention Metrics

| KPI | Formula | Target |
|-----|---------|--------|
| **Day 1 Retention** | Users active day after signup / Signups * 100 | > 40% |
| **Day 7 Retention** | Users active 7 days after signup / Signups * 100 | > 20% |
| **Day 30 Retention** | Users active 30 days after signup / Signups * 100 | > 10% |
| **Churn Rate** | Inactive users / Total users * 100 | < 5% monthly |

### Content Metrics

| KPI | Formula | Target |
|-----|---------|--------|
| **Posts per DAU** | Total posts / DAU | > 0.1 |
| **Viral Coefficient** | Invites sent * Conversion rate | > 1.0 |

### Habit & Wellness Metrics

| KPI | Formula | Target |
|-----|---------|--------|
| **Habit Completion Rate** | Completed habits / Tracked habits * 100 | > 60% |
| **Avg Streak Length** | Total streak days / Active habitors | > 7 days |
| **Active Habitors** | Users tracking habits today | - |
| **Workout Completion Rate** | Completed workouts / Started workouts * 100 | > 70% |
| **Meals Logged per User** | Total meals logged / Active users | > 2 |

### Social Metrics

| KPI | Formula | Target |
|-----|---------|--------|
| **Messages per User** | Total messages / DAU | > 5 |
| **Groups per User** | Total group memberships / Users | > 2 |
| **Follows per User** | Total follows / Users | > 5 |

### PWA Metrics

| KPI | Formula | Target |
|-----|---------|--------|
| **PWA Install Rate** | Installs / Visitors * 100 | > 30% |
| **Offline Usage Rate** | Offline sessions / Total sessions * 100 | > 20% |
| **Push Notification CTR** | Clicks / Sent * 100 | > 15% |

### Health Impact Metrics

| KPI | Description | Target |
|-----|-------------|--------|
| **Users with Improved Streaks** | Users with increasing streak lengths | - |
| **Avg Health Score Improvement** | Aggregate improvement in health metrics | Positive trend |

---

## 4. Service Layer Functions

### AnalyticsService Class

**Event Tracking:**
- `track_event(event_data)` - Track single event
- `track_bulk_events(events_data)` - Batch track events

**User Metrics:**
- `get_dau(date)` - Daily Active Users
- `get_wau(end_date)` - Weekly Active Users
- `get_mau(end_date)` - Monthly Active Users
- `get_new_users_count(days)` - New users in period
- `get_retention_rate(cohort_date, days)` - Cohort retention

**Engagement Metrics:**
- `get_avg_session_duration(date)` - Average session length
- `get_total_sessions(date)` - Session count
- `get_bounce_rate(date)` - Bounce rate calculation

**Content Metrics:**
- `get_content_metrics(date)` - All content-related metrics

**Habit & Wellness:**
- `get_habit_metrics(date)` - Habit tracking stats
- `get_wellness_metrics(date)` - Meals, workouts, fasting

**Social:**
- `get_social_metrics(date)` - Social interaction stats

**PWA:**
- `get_pwa_metrics(date)` - PWA-specific metrics

**Aggregation:**
- `aggregate_daily_metrics(date)` - Create daily aggregate record
- `get_dashboard_summary()` - Complete dashboard data
- `get_event_trends(days)` - Trend analysis
- `get_category_metrics()` - Category breakdown

---

## 5. Integration Points

### Frontend Integration

```javascript
// Example: Track a habit completion
async function trackHabitComplete(habitId) {
  await fetch('/api/v1/analytics/events', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      event_type: 'habit_complete',
      entity_type: 'habit',
      entity_id: habitId,
      properties: {
        habit_name: 'Morning Meditation',
        streak_days: 7
      },
      value: 1
    })
  });
}

// Example: Batch tracking for performance
async function trackBulkEvents(events) {
  await fetch('/api/v1/analytics/events/bulk', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(events)
  });
}
```

### Automatic Tracking Middleware

Recommended frontend implementation:
- Page view tracking on route changes
- Session duration tracking
- Error tracking
- Performance metrics (page load time)

### Backend Integration

All existing API endpoints should emit analytics events:
- Auth endpoints → login/register events
- Post endpoints → create/view/like/comment events
- Habit endpoints → track/complete events
- etc.

---

## 6. Data Privacy & Compliance

### GDPR Considerations
- User consent required for analytics tracking
- Right to deletion includes analytics data
- Anonymization options available
- Data export functionality

### Data Retention
- Raw events: 90 days (configurable)
- Daily aggregates: 2 years
- Weekly/monthly aggregates: 5 years
- KPI snapshots: Indefinite

### Anonymization
- Health outcome metrics are aggregated
- No personally identifiable information in reports
- IP addresses not stored

---

## 7. Performance Optimization

### Database Indexes
- `timestamp` on AnalyticsEvent for time-range queries
- `event_type` for filtering
- `user_id` for user-specific queries
- `session_id` for session analysis
- Composite indexes for common query patterns

### Aggregation Strategy
- Real-time event tracking
- Hourly incremental aggregation (recommended cron job)
- Daily full aggregation
- Pre-computed KPI snapshots

### Query Optimization
- Use materialized views for complex queries
- Cache frequently accessed metrics
- Partition AnalyticsEvent table by month for large datasets

---

## 8. Monitoring & Alerts

### Recommended Alerts
- DAU drop > 20% day-over-day
- Error rate > 5%
- API response time p95 > 500ms
- Retention rate below target

### Dashboard Refresh
- Real-time: Last hour metrics
- Hourly: Current day metrics
- Daily: Full aggregation at midnight UTC

---

## 9. Future Enhancements

### AI-Powered Insights
- Anomaly detection in metrics
- Predictive retention modeling
- User churn prediction
- Personalized engagement recommendations

### Advanced Analytics
- Funnel visualization
- Cohort heatmaps
- User journey mapping
- A/B testing framework

### Integrations
- Google Analytics export
- Mixpanel/Amplitude integration
- Data warehouse sync (BigQuery, Snowflake)
- BI tool connectors (Tableau, Looker)

---

## 10. Testing Strategy

### Unit Tests
- Event tracking accuracy
- Metric calculations
- Aggregation logic
- KPI formulas

### Integration Tests
- API endpoint responses
- Database writes
- Bulk event processing

### Load Tests
- High-volume event tracking
- Concurrent aggregations
- Query performance under load

---

## Summary

The analytics module provides comprehensive tracking and measurement capabilities for the Health & Wellness Social PWA platform. With 80+ event types, 10 KPI categories, and real-time aggregation, it enables data-driven decision making for product improvements, user engagement optimization, and business growth.

**Total Implementation:**
- 8 database models
- 25+ API endpoints
- 30+ service methods
- 50+ KPIs and metrics
- Full admin dashboard support
