# Health & Wellness PWA - Analytics & KPI Implementation Guide

## Overview

This document provides a comprehensive guide to the analytics module implementation, including all tracked events, KPIs, metrics, and how to use the analytics API.

---

## 1. Event Tracking System

### Event Categories

The system tracks events across **10 major categories**:

1. **User Events** - Authentication, profile management
2. **Content Events** - Posts, comments, likes, shares
3. **Habit Events** - Habit creation, tracking, completion
4. **Wellness Events** - Meals, workouts, fasting
5. **Social Events** - Follows, groups, messages
6. **Discovery Events** - Search, browse, explore
7. **PWA Events** - Installs, offline usage, push notifications
8. **Performance Events** - Page load, Core Web Vitals
9. **Commerce Events** - Subscriptions, purchases (future)
10. **System Events** - Errors, crashes, technical issues

### Complete Event List (80+ Events)

#### User Events (10)
- `USER_SIGNUP` - User registration
- `USER_LOGIN` - User login
- `USER_LOGOUT` - User logout
- `USER_PROFILE_UPDATE` - Profile information updated
- `USER_SETTINGS_UPDATE` - Settings changed
- `USER_GOAL_SET` - Health goal created
- `USER_GOAL_UPDATE` - Health goal modified
- `USER_AVATAR_UPLOAD` - Profile picture uploaded
- `USER_EMAIL_VERIFY` - Email verification completed
- `USER_PASSWORD_RESET` - Password reset requested

#### Content Events (15)
- `POST_CREATE` - New post created
- `POST_VIEW` - Post viewed
- `POST_LIKE` - Post liked
- `POST_UNLIKE` - Post like removed
- `POST_COMMENT` - Comment added
- `POST_COMMENT_REPLY` - Reply to comment
- `POST_SHARE` - Post shared
- `POST_SAVE` - Post bookmarked
- `POST_UNSAVE` - Bookmark removed
- `POST_REPORT` - Post reported
- `POST_DELETE` - Post deleted
- `POST_EDIT` - Post edited
- `POST_POLL_VOTE` - Poll voted
- `POST_TAG_ADD` - Tag added to post
- `POST_MENTION` - User mentioned in post

#### Habit Events (12)
- `HABIT_CREATE` - New habit created
- `HABIT_UPDATE` - Habit modified
- `HABIT_DELETE` - Habit deleted
- `HABIT_TRACK` - Habit logged for a day
- `HABIT_COMPLETE` - Habit marked complete
- `HABIT_SKIP` - Habit skipped
- `HABIT_STREAK_START` - Streak started
- `HABIT_STREAK_MILESTONE` - Streak milestone reached
- `HABIT_REMINDER_SET` - Reminder configured
- `HABIT_REMINDER_TRIGGER` - Reminder fired
- `HABIT_GOAL_SET` - Habit goal defined
- `HABIT_STATS_VIEW` - Habit statistics viewed

#### Wellness Events (15)
- `MEAL_LOG` - Meal logged
- `MEAL_CREATE` - Custom meal created
- `MEAL_PLAN_CREATE` - Meal plan created
- `MEAL_PLAN_VIEW` - Meal plan viewed
- `RECIPE_SAVE` - Recipe saved
- `RECIPE_VIEW` - Recipe viewed
- `WORKOUT_START` - Workout session started
- `WORKOUT_COMPLETE` - Workout finished
- `WORKOUT_PAUSE` - Workout paused
- `WORKOUT_CANCEL` - Workout cancelled
- `EXERCISE_LOG` - Exercise logged
- `FASTING_START` - Fasting session started
- `FASTING_END` - Fasting session ended
- `FASTING_BREAK` - Fast broken
- `WATER_INTAKE_LOG` - Water intake logged

#### Social Events (10)
- `USER_FOLLOW` - Started following user
- `USER_UNFOLLOW` - Unfollowed user
- `GROUP_CREATE` - Group created
- `GROUP_JOIN` - Joined group
- `GROUP_LEAVE` - Left group
- `GROUP_POST_CREATE` - Post in group
- `GROUP_EVENT_CREATE` - Group event created
- `GROUP_EVENT_JOIN` - Joined group event
- `CHALLENGE_JOIN` - Joined challenge
- `CHALLENGE_COMPLETE` - Challenge completed

#### Messaging Events (8)
- `MESSAGE_SEND` - Message sent
- `MESSAGE_RECEIVE` - Message received
- `MESSAGE_READ` - Message read receipt
- `MESSAGE_DELETE` - Message deleted
- `MESSAGE_REACTION` - Reaction added to message
- `VOICE_NOTE_SEND` - Voice note sent
- `IMAGE_SEND` - Image sent in chat
- `VIDEO_SEND` - Video sent in chat

#### Discovery Events (8)
- `SEARCH_QUERY` - Search performed
- `SEARCH_RESULT_CLICK` - Search result clicked
- `CATEGORY_BROWSE` - Category browsed
- `USER_DISCOVER` - User discovered
- `CONTENT_EXPLORE` - Content explored
- `TRENDING_VIEW` - Trending content viewed
- `RECOMMENDATION_CLICK` - Recommendation clicked
- `HASHTAG_FOLLOW` - Hashtag followed

#### PWA Events (7)
- `PWA_INSTALL` - App installed
- `PWA_OFFLINE_MODE` - Offline mode activated
- `PWA_ONLINE_MODE` - Back online
- `PUSH_NOTIFICATION_PERMISSION` - Permission granted/denied
- `PUSH_NOTIFICATION_RECEIVED` - Notification received
- `PUSH_NOTIFICATION_CLICK` - Notification clicked
- `CACHE_UPDATE` - Service worker cache updated

#### Performance Events (5)
- `PAGE_LOAD` - Page loaded
- `PAGE_VIEW` - Page view tracked
- `NAVIGATION` - Navigation event
- `PERFORMANCE_METRIC` - Core Web Vitals captured
- `API_REQUEST` - API call made

#### System Events (5)
- `ERROR_OCCURRED` - Error encountered
- `CRASH_REPORT` - App crash reported
- `API_ERROR` - API request failed
- `RATE_LIMIT_HIT` - Rate limit exceeded
- `FEATURE_FLAG_CHECK` - Feature flag evaluated

---

## 2. Key Performance Indicators (KPIs)

### Growth Metrics

| KPI | Description | Target | Calculation |
|-----|-------------|--------|-------------|
| **DAU** | Daily Active Users | +10% WoW | Unique users with ≥1 event/day |
| **WAU** | Weekly Active Users | +8% WoW | Unique users with ≥1 event/week |
| **MAU** | Monthly Active Users | +5% MoM | Unique users with ≥1 event/month |
| **New Users** | New signups per day | 100+/day | Users created in period |
| **Activation Rate** | % completing first action | >60% | (Users with 1st action / Signups) × 100 |
| **Growth Rate** | User base growth | 15%/month | ((End - Start) / Start) × 100 |

### Engagement Metrics

| KPI | Description | Target | Calculation |
|-----|-------------|--------|-------------|
| **Sessions per DAU** | Avg sessions per user | 3-5 | Total sessions / DAU |
| **Session Duration** | Avg time in app | >5 min | Sum(duration) / Sessions |
| **Bounce Rate** | Single-page sessions | <30% | (1-event sessions / Total) × 100 |
| **Stickiness** | DAU/MAU ratio | >20% | (DAU / MAU) × 100 |
| **Engagement Rate** | Active engagement | >40% | (Engaged users / DAU) × 100 |
| **Feature Adoption** | Using key features | >50% | (Users using feature / MAU) × 100 |

### Retention Metrics

| KPI | Description | Target | Calculation |
|-----|-------------|--------|-------------|
| **D1 Retention** | Return after 1 day | >40% | (Day 1 active / Cohort) × 100 |
| **D7 Retention** | Return after 7 days | >25% | (Day 7 active / Cohort) × 100 |
| **D30 Retention** | Return after 30 days | >15% | (Day 30 active / Cohort) × 100 |
| **Churn Rate** | Users lost | <5%/month | (Lost users / Start users) × 100 |
| **Resurrection Rate** | Returned churned users | >10% | (Returned / Churned) × 100 |

### Content Metrics

| KPI | Description | Target | Calculation |
|-----|-------------|--------|-------------|
| **Posts per DAU** | Content creation rate | >0.3 | Posts created / DAU |
| **Engagement per Post** | Interactions per post | >5 | (Likes+Comments+Shares) / Posts |
| **Viral Coefficient** | Shares per post | >0.5 | Shares / Posts |
| **Save Rate** | Content saved | >10% | Saves / Views × 100 |
| **Comment Rate** | Discussion generated | >5% | Comments / Views × 100 |

### Habit & Wellness Metrics

| KPI | Description | Target | Calculation |
|-----|-------------|--------|-------------|
| **Habit Completion Rate** | Habits completed | >70% | Completed / Tracked × 100 |
| **Avg Streak Length** | Habit consistency | >7 days | Sum(streaks) / Active habits |
| **Meals Logged per DAU** | Nutrition tracking | >1.5 | Meals logged / DAU |
| **Workout Completion** | Fitness adherence | >60% | Completed workouts / Started |
| **Fasting Adherence** | Fasting plan follow-through | >50% | Completed fasts / Started |

### Social Metrics

| KPI | Description | Target | Calculation |
|-----|-------------|--------|-------------|
| **Follow Rate** | Social connections | >2/user | Follows / DAU |
| **Group Participation** | Community engagement | >30% | Group actives / MAU |
| **Messages per DAU** | Communication volume | >5 | Messages sent / DAU |
| **Group Creation Rate** | Community formation | >10/day | Groups created / day |

### PWA Metrics

| KPI | Description | Target | Calculation |
|-----|-------------|--------|-------------|
| **Install Rate** | PWA installations | >20% | Installs / Visitors × 100 |
| **Offline Usage** | Using offline mode | >15% | Offline sessions / Total |
| **Push Opt-in Rate** | Notification permission | >40% | Granted / Requests × 100 |
| **Push CTR** | Notification engagement | >20% | Clicks / Sent × 100 |

### Performance Metrics

| KPI | Description | Target | Measurement |
|-----|-------------|--------|-------------|
| **LCP** | Largest Contentful Paint | <2.5s | Core Web Vital |
| **FID** | First Input Delay | <100ms | Core Web Vital |
| **CLS** | Cumulative Layout Shift | <0.1 | Core Web Vital |
| **API Response Time** | Backend performance | <200ms | Avg response time |
| **Error Rate** | Request failures | <1% | Errors / Requests × 100 |

---

## 3. API Endpoints Reference

### Event Tracking

```bash
# Track single event
POST /api/v1/analytics/events
{
  "event_type": "POST_CREATE",
  "event_name": "Create Post",
  "entity_type": "post",
  "entity_id": "123",
  "properties": {"category": "nutrition"}
}

# Track bulk events
POST /api/v1/analytics/events/bulk
[
  {"event_type": "PAGE_VIEW", ...},
  {"event_type": "POST_CREATE", ...}
]
```

### Dashboard & Metrics

```bash
# Get dashboard summary
GET /api/v1/analytics/dashboard

# Get daily metrics
GET /api/v1/analytics/metrics/daily/2024-01-15

# Get event trends
GET /api/v1/analytics/metrics/trends?days=7

# Get category metrics
GET /api/v1/analytics/metrics/categories
```

### User Metrics

```bash
# Daily Active Users
GET /api/v1/analytics/users/dau?date=2024-01-15

# Weekly Active Users
GET /api/v1/analytics/users/wau

# Monthly Active Users
GET /api/v1/analytics/users/mau

# Retention rate
GET /api/v1/analytics/users/retention?cohort_date=2024-01-01&days=7
```

### Engagement Metrics

```bash
# Average session duration
GET /api/v1/analytics/engagement/session-duration

# Total sessions
GET /api/v1/analytics/engagement/sessions

# Bounce rate
GET /api/v1/analytics/engagement/bounce-rate
```

### Content, Habit, Wellness Metrics

```bash
# Content metrics
GET /api/v1/analytics/content/metrics

# Habit metrics
GET /api/v1/analytics/habits/metrics

# Wellness metrics
GET /api/v1/analytics/wellness/metrics

# Social metrics
GET /api/v1/analytics/social/metrics

# PWA metrics
GET /api/v1/analytics/pwa/metrics
```

### KPI & Reports (NEW)

```bash
# KPI Dashboard Summary
GET /api/v1/analytics/kpi/dashboard/summary?period=7d

# Real-time KPI Snapshot
GET /api/v1/analytics/kpi/snapshot

# Retention Cohort Analysis
GET /api/v1/analytics/kpi/retention/cohort?weeks=8

# Daily Retention Rates
GET /api/v1/analytics/kpi/retention/daily?cohort_date=2024-01-01&days=30

# Acquisition Funnel
GET /api/v1/analytics/kpi/funnel/acquisition?days=7

# Activation Funnel
GET /api/v1/analytics/kpi/funnel/activation?days=7

# API Performance
GET /api/v1/analytics/kpi/performance/api?days=7

# PWA Performance (Core Web Vitals)
GET /api/v1/analytics/kpi/performance/pwa?days=7

# Generate Daily CSV Report
GET /api/v1/analytics/kpi/reports/daily/csv?date=2024-01-15

# Weekly Summary Report
GET /api/v1/analytics/kpi/reports/weekly/summary?week_offset=0

# Check KPI Alerts
GET /api/v1/analytics/kpi/alerts/check
```

---

## 4. Implementation Examples

### Frontend Event Tracking (JavaScript/TypeScript)

```typescript
// Track page view
async function trackPageView(pageName: string) {
  await fetch('/api/v1/analytics/events', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      event_type: 'PAGE_VIEW',
      event_name: pageName,
      page_url: window.location.href,
      referrer_url: document.referrer,
      platform: 'web',
      device_type: 'desktop'
    })
  });
}

// Track user action
async function trackEvent(eventType: string, properties: any = {}) {
  await fetch('/api/v1/analytics/events', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      event_type: eventType,
      event_name: eventType.replace('_', ' '),
      ...properties,
      platform: 'web',
      timestamp: new Date().toISOString()
    })
  });
}

// Example usage
trackEvent('POST_CREATE', { 
  entity_type: 'post',
  entity_id: postId,
  properties: { category: 'nutrition', has_image: true }
});

// Batch events for efficiency
async function batchTrackEvents(events: Array<any>) {
  await fetch('/api/v1/analytics/events/bulk', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(events)
  });
}
```

### React Hook for Analytics

```typescript
// hooks/useAnalytics.ts
import { useCallback } from 'react';

export function useAnalytics(userId?: string) {
  const trackEvent = useCallback(async (
    eventType: string,
    properties: Record<string, any> = {}
  ) => {
    try {
      await fetch('/api/v1/analytics/events', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          event_type: eventType,
          user_id: userId,
          session_id: getSessionId(),
          timestamp: new Date().toISOString(),
          ...properties
        })
      });
    } catch (error) {
      console.error('Analytics tracking failed:', error);
    }
  }, [userId]);

  const trackPageView = useCallback((pageName: string) => {
    return trackEvent('PAGE_VIEW', {
      page_name: pageName,
      page_url: window.location.href
    });
  }, [trackEvent]);

  return { trackEvent, trackPageView };
}
```

### Automatic Event Tracking

```typescript
// Auto-track clicks on elements with data-analytics attribute
document.querySelectorAll('[data-analytics]').forEach(element => {
  element.addEventListener('click', (e) => {
    const eventType = element.getAttribute('data-analytics');
    const eventData = JSON.parse(
      element.getAttribute('data-analytics-data') || '{}'
    );
    trackEvent(eventType, eventData);
  });
});

// Usage in HTML
<button 
  data-analytics="HABIT_COMPLETE"
  data-analytics-data='{"habit_id": 123, "habit_type": "water_intake"}'
>
  Log Water Intake
</button>
```

---

## 5. Data Aggregation Strategy

### Pre-aggregated Metrics

To optimize query performance, metrics are pre-aggregated at three levels:

1. **Daily Metrics** (`daily_metrics` table)
   - Aggregated every 24 hours
   - Includes: DAU, sessions, events by category, conversions
   
2. **Weekly Metrics** (`weekly_metrics` table)
   - Aggregated every week (Monday-Sunday)
   - Includes: WAU, weekly totals, retention rates, growth metrics
   
3. **Monthly Metrics** (`monthly_metrics` table)
   - Aggregated monthly
   - Includes: MAU, monthly trends, cohort analysis, KPI snapshots

### Aggregation Schedule

```python
# Recommended cron schedule
0 1 * * *    # Daily aggregation at 1 AM
0 2 * * 1    # Weekly aggregation on Monday at 2 AM
0 3 1 * *    # Monthly aggregation on 1st at 3 AM
```

### Manual Aggregation

```bash
# Trigger daily aggregation
POST /api/v1/analytics/aggregate/daily?date=2024-01-15

# Trigger weekly aggregation
POST /api/v1/analytics/aggregate/weekly?year=2024&week=3

# Trigger monthly aggregation
POST /api/v1/analytics/aggregate/monthly?year=2024&month=1
```

---

## 6. Alert Thresholds

The system monitors these thresholds and triggers alerts:

| Metric | Alert Condition | Severity |
|--------|----------------|----------|
| DAU | Drop >20% vs previous day | HIGH |
| Session Duration | Drop >30% vs previous day | MEDIUM |
| Bounce Rate | Increase >25% vs previous day | MEDIUM |
| Error Rate | Exceeds 5% | HIGH |
| API Response Time | P95 >1000ms | MEDIUM |
| New Signups | Drop >40% vs 7-day avg | HIGH |
| Habit Completion | Drop >25% vs 7-day avg | LOW |

---

## 7. Privacy & Compliance

### Data Anonymization

- IP addresses are hashed before storage
- User agents are truncated to browser/OS only
- Geolocation is stored at city level only
- Session IDs are rotated every 24 hours

### GDPR Compliance

- Users can request data export via `/api/v1/users/data-export`
- Users can request data deletion via `/api/v1/users/delete-account`
- Analytics tracking respects Do Not Track (DNT) header
- Cookie consent required for non-essential tracking

### Data Retention

- Raw events: 90 days
- Daily aggregates: 2 years
- Weekly aggregates: 5 years
- Monthly aggregates: Indefinite

---

## 8. Best Practices

### For Developers

1. **Track meaningful events only** - Don't track every click
2. **Use consistent naming** - Follow the EVENT_TYPE_MAPPING
3. **Include relevant context** - Add entity_type, entity_id when applicable
4. **Batch events** - Use bulk endpoint for multiple events
5. **Handle failures gracefully** - Don't block UX if tracking fails
6. **Test in staging** - Verify events before production deployment

### For Analysts

1. **Use pre-aggregated tables** - Faster queries on daily/weekly/monthly
2. **Segment by user type** - Compare free vs premium behavior
3. **Monitor funnels regularly** - Identify drop-off points
4. **Set up custom alerts** - Get notified of anomalies
5. **Export reports** - Use CSV endpoints for external analysis

### For Product Managers

1. **Define success metrics** - What does "good" look like?
2. **Track feature adoption** - Are users using new features?
3. **Monitor retention cohorts** - Which signup periods perform best?
4. **A/B test with analytics** - Measure impact of changes
5. **Review dashboards daily** - Stay informed of trends

---

## 9. Future Enhancements

### Planned Features

- [ ] Real-time event streaming with Kafka
- [ ] Advanced segmentation builder
- [ ] Custom event definitions (no-code)
- [ ] Predictive analytics (churn prediction)
- [ ] Attribution modeling
- [ ] Revenue tracking integration
- [ ] A/B testing framework
- [ ] Automated insights generation
- [ ] Integration with external tools (Mixpanel, Amplitude)
- [ ] Machine learning anomaly detection

### AI-Powered Insights

Future AI features will provide:
- Automatic anomaly detection
- Trend predictions
- Personalized recommendations for users
- Content performance predictions
- Optimal posting time suggestions

---

## 10. Support & Documentation

- **API Documentation**: http://localhost:8000/docs
- **Event Schema**: See `app/schemas/analytics.py`
- **Service Layer**: See `app/services/analytics_service.py`
- **Models**: See `app/models/analytics.py`

For questions or issues, contact the development team.
