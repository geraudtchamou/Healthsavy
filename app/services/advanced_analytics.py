"""
Advanced Analytics Service with AI Insights & Predictive Modeling

This module provides:
- Predictive churn modeling
- User segmentation (RFM + Behavioral)
- Anomaly detection
- Personalized recommendations
- Automated insights generation
- Trend forecasting
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel
import math


class UserSegment(BaseModel):
    """User segment definition"""
    name: str
    criteria: Dict[str, Any]
    size: int = 0
    growth_rate: float = 0.0
    engagement_score: float = 0.0


class ChurnPrediction(BaseModel):
    """Churn prediction result"""
    user_id: str
    churn_probability: float
    risk_level: str  # low, medium, high, critical
    risk_factors: List[str]
    recommended_actions: List[str]
    predicted_churn_date: Optional[datetime] = None


class AnomalyAlert(BaseModel):
    """Anomaly detection alert"""
    metric_name: str
    current_value: float
    expected_value: float
    deviation_percentage: float
    severity: str  # low, medium, high, critical
    detected_at: datetime
    description: str
    recommended_actions: List[str]


class Insight(BaseModel):
    """Automated insight"""
    id: str
    title: str
    description: str
    category: str  # growth, engagement, retention, content, wellness
    impact_score: float  # 0-100
    data_points: Dict[str, Any]
    trend: str  # positive, negative, neutral
    created_at: datetime


class ForecastPoint(BaseModel):
    """Forecast data point"""
    date: datetime
    predicted_value: float
    confidence_interval_lower: float
    confidence_interval_upper: float
    actual_value: Optional[float] = None


class AdvancedAnalyticsService:
    """
    Advanced analytics service with AI-powered insights
    """
    
    def __init__(self, db_session=None):
        self.db = db_session
    
    # ==================== PREDICTIVE ANALYTICS ====================
    
    def predict_user_churn(self, user_id: str, lookback_days: int = 30) -> ChurnPrediction:
        """
        Predict user churn probability using behavioral signals
        
        Risk Factors:
        - Declining activity
        - Missed habit streaks
        - Reduced social interactions
        - Increased session gaps
        - Negative sentiment (if available)
        """
        # Simulated churn model (replace with ML model in production)
        risk_factors = []
        churn_score = 0.0
        
        # Get user activity data (simulated)
        # In production, query from database
        days_since_last_login = self._get_days_since_last_activity(user_id)
        habit_streak_broken = self._check_habit_streak_broken(user_id)
        social_interaction_decline = self._check_social_decline(user_id, lookback_days)
        session_duration_decline = self._check_session_decline(user_id, lookback_days)
        
        # Calculate risk score
        if days_since_last_login > 7:
            churn_score += 0.25
            risk_factors.append(f"No activity for {days_since_last_login} days")
        
        if days_since_last_login > 14:
            churn_score += 0.20
            risk_factors.append("Extended inactivity period")
        
        if habit_streak_broken:
            churn_score += 0.20
            risk_factors.append("Habit streak broken")
        
        if social_interaction_decline > 0.5:
            churn_score += 0.15
            risk_factors.append(f"Social interactions down {social_interaction_decline*100:.0f}%")
        
        if session_duration_decline > 0.3:
            churn_score += 0.10
            risk_factors.append(f"Session duration down {session_duration_decline*100:.0f}%")
        
        # Cap at 1.0
        churn_probability = min(churn_score, 1.0)
        
        # Determine risk level
        if churn_probability >= 0.7:
            risk_level = "critical"
        elif churn_probability >= 0.5:
            risk_level = "high"
        elif churn_probability >= 0.3:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        # Generate recommended actions
        recommended_actions = self._generate_retention_actions(risk_factors, churn_probability)
        
        # Predict churn date
        predicted_churn_date = None
        if churn_probability > 0.5:
            days_to_churn = max(1, int((1 - churn_probability) * 30))
            predicted_churn_date = datetime.utcnow() + timedelta(days=days_to_churn)
        
        return ChurnPrediction(
            user_id=user_id,
            churn_probability=churn_probability,
            risk_level=risk_level,
            risk_factors=risk_factors,
            recommended_actions=recommended_actions,
            predicted_churn_date=predicted_churn_date
        )
    
    def get_churn_risk_users(self, limit: int = 100) -> List[ChurnPrediction]:
        """Get list of users at risk of churning"""
        # In production, batch process all active users
        # This is a simplified version
        high_risk_users = []
        
        # Simulate checking top active users
        for i in range(limit):
            user_id = f"user_{i}"
            prediction = self.predict_user_churn(user_id)
            if prediction.risk_level in ["high", "critical"]:
                high_risk_users.append(prediction)
        
        return sorted(high_risk_users, key=lambda x: x.churn_probability, reverse=True)
    
    # ==================== USER SEGMENTATION ====================
    
    def segment_users_rfm(self) -> List[UserSegment]:
        """
        RFM Segmentation (Recency, Frequency, Monetary)
        
        Segments:
        - Champions: Recent, frequent, high value
        - Loyal Customers: Frequent, good value
        - Potential Loyalists: Recent, moderate frequency
        - At Risk: Were frequent, now inactive
        - Hibernating: Low recency, low frequency
        - Lost: Very low across all dimensions
        """
        segments = []
        
        # Champions
        segments.append(UserSegment(
            name="Champions",
            criteria={
                "recency_days": "<=7",
                "frequency_per_month": ">=15",
                "engagement_score": ">=80"
            },
            size=self._count_users_in_segment("champions"),
            engagement_score=92.5
        ))
        
        # Loyal Customers
        segments.append(UserSegment(
            name="Loyal Customers",
            criteria={
                "recency_days": "<=14",
                "frequency_per_month": ">=10",
                "engagement_score": ">=60"
            },
            size=self._count_users_in_segment("loyal"),
            engagement_score=75.3
        ))
        
        # Potential Loyalists
        segments.append(UserSegment(
            name="Potential Loyalists",
            criteria={
                "recency_days": "<=7",
                "frequency_per_month": ">=5",
                "engagement_score": ">=40"
            },
            size=self._count_users_in_segment("potential"),
            engagement_score=58.7
        ))
        
        # At Risk
        segments.append(UserSegment(
            name="At Risk",
            criteria={
                "recency_days": ">14",
                "frequency_per_month": ">=10",
                "engagement_score": ">=50"
            },
            size=self._count_users_in_segment("at_risk"),
            engagement_score=45.2
        ))
        
        # Hibernating
        segments.append(UserSegment(
            name="Hibernating",
            criteria={
                "recency_days": ">30",
                "frequency_per_month": "<5",
                "engagement_score": "<40"
            },
            size=self._count_users_in_segment("hibernating"),
            engagement_score=22.1
        ))
        
        return segments
    
    def segment_by_behavior(self) -> List[UserSegment]:
        """
        Behavioral segmentation based on app usage patterns
        
        Segments:
        - Social Butterflies: High social activity
        - Habit Masters: Consistent habit tracking
        - Content Creators: High content creation
        - Learners: High content consumption
        - Wellness Warriors: High wellness program usage
        - Casual Users: Low across all dimensions
        """
        segments = []
        
        segments.append(UserSegment(
            name="Social Butterflies",
            criteria={"social_score": ">=70"},
            size=self._count_behavioral_segment("social"),
            engagement_score=85.4
        ))
        
        segments.append(UserSegment(
            name="Habit Masters",
            criteria={"habit_completion_rate": ">=80"},
            size=self._count_behavioral_segment("habit"),
            engagement_score=88.9
        ))
        
        segments.append(UserSegment(
            name="Content Creators",
            criteria={"posts_per_month": ">=10"},
            size=self._count_behavioral_segment("creator"),
            engagement_score=79.2
        ))
        
        segments.append(UserSegment(
            name="Wellness Warriors",
            criteria={"wellness_programs_active": ">=3"},
            size=self._count_behavioral_segment("wellness"),
            engagement_score=91.3
        ))
        
        return segments
    
    # ==================== ANOMALY DETECTION ====================
    
    def detect_anomalies(self, metric_name: str, time_window_hours: int = 24) -> List[AnomalyAlert]:
        """
        Detect anomalies in metrics using statistical methods
        
        Methods:
        - Z-score detection (>3 standard deviations)
        - Moving average deviation
        - Seasonal adjustment
        """
        alerts = []
        
        # Get current and historical values
        current_value = self._get_current_metric_value(metric_name)
        historical_mean, historical_std = self._get_historical_stats(metric_name, time_window_hours)
        
        if historical_std == 0:
            return alerts
        
        # Calculate Z-score
        z_score = abs(current_value - historical_mean) / historical_std
        
        if z_score > 3:  # Significant anomaly
            deviation_pct = ((current_value - historical_mean) / historical_mean) * 100 if historical_mean != 0 else 0
            
            severity = "critical" if z_score > 4 else "high" if z_score > 3.5 else "medium"
            
            direction = "spike" if current_value > historical_mean else "drop"
            
            alerts.append(AnomalyAlert(
                metric_name=metric_name,
                current_value=current_value,
                expected_value=historical_mean,
                deviation_percentage=deviation_pct,
                severity=severity,
                detected_at=datetime.utcnow(),
                description=f"{direction.capitalize()} detected in {metric_name}: {deviation_pct:+.1f}% from normal",
                recommended_actions=self._get_anomaly_actions(metric_name, direction, severity)
            ))
        
        return alerts
    
    def monitor_all_critical_metrics(self) -> List[AnomalyAlert]:
        """Monitor all critical metrics for anomalies"""
        critical_metrics = [
            "daily_active_users",
            "new_registrations",
            "habit_completion_rate",
            "api_error_rate",
            "average_session_duration",
            "chat_messages_sent",
            "posts_created"
        ]
        
        all_alerts = []
        for metric in critical_metrics:
            alerts = self.detect_anomalies(metric)
            all_alerts.extend(alerts)
        
        return sorted(all_alerts, key=lambda x: {"critical": 0, "high": 1, "medium": 2, "low": 3}[x.severity])
    
    # ==================== AUTOMATED INSIGHTS ====================
    
    def generate_insights(self, time_period: str = "7d") -> List[Insight]:
        """
        Automatically generate actionable insights from data
        
        Categories:
        - Growth opportunities
        - Engagement improvements
        - Retention risks
        - Content performance
        - Wellness trends
        """
        insights = []
        
        # Growth Insight
        new_user_growth = self._calculate_metric_growth("new_registrations", time_period)
        if new_user_growth > 0.15:
            insights.append(Insight(
                id="insight_growth_001",
                title="Strong User Growth",
                description=f"New registrations increased by {new_user_growth*100:.1f}% compared to previous period. Consider scaling acquisition efforts.",
                category="growth",
                impact_score=min(95, 60 + new_user_growth * 100),
                data_points={"growth_rate": new_user_growth, "period": time_period},
                trend="positive",
                created_at=datetime.utcnow()
            ))
        
        # Engagement Insight
        session_duration_change = self._calculate_metric_growth("avg_session_duration", time_period)
        if session_duration_change < -0.1:
            insights.append(Insight(
                id="insight_engagement_001",
                title="Declining Session Duration",
                description=f"Average session duration decreased by {abs(session_duration_change)*100:.1f}%. Review content quality and UX.",
                category="engagement",
                impact_score=min(90, 70 + abs(session_duration_change) * 200),
                data_points={"change_rate": session_duration_change, "period": time_period},
                trend="negative",
                created_at=datetime.utcnow()
            ))
        
        # Habit Completion Insight
        habit_completion = self._get_metric_value("habit_completion_rate")
        if habit_completion > 0.75:
            insights.append(Insight(
                id="insight_wellness_001",
                title="High Habit Success Rate",
                description=f"Users are completing {habit_completion*100:.1f}% of tracked habits. Consider introducing more advanced challenges.",
                category="wellness",
                impact_score=75,
                data_points={"completion_rate": habit_completion},
                trend="positive",
                created_at=datetime.utcnow()
            ))
        
        # Social Engagement Insight
        social_rate = self._get_metric_value("social_interaction_rate")
        if social_rate < 0.3:
            insights.append(Insight(
                id="insight_social_001",
                title="Low Social Engagement",
                description=f"Only {social_rate*100:.1f}% of users engage socially. Consider gamification or community features.",
                category="engagement",
                impact_score=80,
                data_points={"social_rate": social_rate},
                trend="negative",
                created_at=datetime.utcnow()
            ))
        
        # Content Viral Insight
        viral_coefficient = self._get_metric_value("viral_coefficient")
        if viral_coefficient > 1.0:
            insights.append(Insight(
                id="insight_viral_001",
                title="Viral Growth Detected",
                description=f"Viral coefficient is {viral_coefficient:.2f}. Each user brings more than 1 new user organically.",
                category="growth",
                impact_score=95,
                data_points={"viral_coefficient": viral_coefficient},
                trend="positive",
                created_at=datetime.utcnow()
            ))
        
        return sorted(insights, key=lambda x: x.impact_score, reverse=True)
    
    # ==================== FORECASTING ====================
    
    def forecast_metric(self, metric_name: str, days_ahead: int = 30) -> List[ForecastPoint]:
        """
        Forecast future metric values using time series analysis
        
        Methods:
        - Linear regression trend
        - Seasonal adjustment
        - Moving average smoothing
        """
        forecasts = []
        
        # Get historical data (simulated)
        historical_data = self._get_historical_data(metric_name, days=60)
        
        if not historical_data:
            return []
        
        # Simple linear regression forecast (replace with Prophet/ARIMA in production)
        trend_slope = self._calculate_trend(historical_data)
        last_value = historical_data[-1]["value"] if historical_data else 0
        last_date = historical_data[-1]["date"] if historical_data else datetime.utcnow()
        
        for i in range(days_ahead):
            forecast_date = last_date + timedelta(days=i+1)
            
            # Base forecast with trend
            predicted_value = last_value + (trend_slope * (i + 1))
            
            # Add seasonality (weekly pattern)
            day_of_week = forecast_date.weekday()
            seasonal_factor = 1.0 + 0.1 * math.sin(2 * math.pi * day_of_week / 7)
            predicted_value *= seasonal_factor
            
            # Confidence interval (widens over time)
            uncertainty = 0.05 * (i + 1)
            ci_lower = predicted_value * (1 - uncertainty)
            ci_upper = predicted_value * (1 + uncertainty)
            
            forecasts.append(ForecastPoint(
                date=forecast_date,
                predicted_value=max(0, predicted_value),
                confidence_interval_lower=max(0, ci_lower),
                confidence_interval_upper=ci_upper
            ))
        
        return forecasts
    
    def forecast_dau(self, days_ahead: int = 30) -> Dict[str, Any]:
        """Forecast Daily Active Users with summary"""
        forecasts = self.forecast_metric("daily_active_users", days_ahead)
        
        if not forecasts:
            return {"error": "No forecast available"}
        
        current_dau = self._get_current_metric_value("daily_active_users")
        final_forecast = forecasts[-1].predicted_value
        growth_projection = ((final_forecast - current_dau) / current_dau) * 100 if current_dau != 0 else 0
        
        return {
            "current_dau": current_dau,
            "forecast_30d": final_forecast,
            "projected_growth_percent": growth_projection,
            "confidence_range": {
                "lower": forecasts[-1].confidence_interval_lower,
                "upper": forecasts[-1].confidence_interval_upper
            },
            "daily_forecasts": forecasts
        }
    
    # ==================== HELPER METHODS (Simulated) ====================
    
    def _get_days_since_last_activity(self, user_id: str) -> int:
        """Get days since user's last activity"""
        # In production: query database
        import random
        return random.randint(0, 45)
    
    def _check_habit_streak_broken(self, user_id: str) -> bool:
        """Check if user broke their habit streak"""
        import random
        return random.random() < 0.3
    
    def _check_social_decline(self, user_id: str, lookback_days: int) -> float:
        """Check decline in social interactions"""
        import random
        return random.uniform(0, 0.7)
    
    def _check_session_decline(self, user_id: str, lookback_days: int) -> float:
        """Check decline in session duration"""
        import random
        return random.uniform(0, 0.5)
    
    def _generate_retention_actions(self, risk_factors: List[str], churn_prob: float) -> List[str]:
        """Generate personalized retention actions"""
        actions = []
        
        if "No activity" in str(risk_factors):
            actions.append("Send re-engagement email with personalized content")
            actions.append("Push notification about missed habit streak")
        
        if "Habit streak" in str(risk_factors):
            actions.append("Offer habit recovery challenge")
            actions.append("Show success stories from similar users")
        
        if "Social" in str(risk_factors):
            actions.append("Invite to active group discussions")
            actions.append("Notify about friend activities")
        
        if churn_prob > 0.7:
            actions.append("Offer premium feature trial")
            actions.append("Personal check-in from wellness coach")
        
        return actions if actions else ["Monitor user activity", "A/B test engagement strategies"]
    
    def _count_users_in_segment(self, segment_type: str) -> int:
        """Count users in RFM segment"""
        import random
        segment_sizes = {
            "champions": 450,
            "loyal": 1200,
            "potential": 2300,
            "at_risk": 890,
            "hibernating": 1560
        }
        return segment_sizes.get(segment_type, random.randint(100, 3000))
    
    def _count_behavioral_segment(self, segment_type: str) -> int:
        """Count users in behavioral segment"""
        import random
        segment_sizes = {
            "social": 1800,
            "habit": 2400,
            "creator": 650,
            "wellness": 1950
        }
        return segment_sizes.get(segment_type, random.randint(500, 3000))
    
    def _get_current_metric_value(self, metric_name: str) -> float:
        """Get current value of a metric"""
        import random
        base_values = {
            "daily_active_users": 5000,
            "new_registrations": 250,
            "habit_completion_rate": 0.72,
            "api_error_rate": 0.02,
            "average_session_duration": 420,
            "chat_messages_sent": 8500,
            "posts_created": 1200,
            "social_interaction_rate": 0.35,
            "viral_coefficient": 0.8
        }
        base = base_values.get(metric_name, 1000)
        return base * random.uniform(0.8, 1.2)
    
    def _get_historical_stats(self, metric_name: str, hours: int) -> Tuple[float, float]:
        """Get historical mean and std deviation"""
        import random
        base_values = {
            "daily_active_users": (5000, 500),
            "new_registrations": (250, 50),
            "habit_completion_rate": (0.72, 0.08),
            "api_error_rate": (0.02, 0.005),
            "average_session_duration": (420, 60),
            "chat_messages_sent": (8500, 1200),
            "posts_created": (1200, 200)
        }
        return base_values.get(metric_name, (1000, 100))
    
    def _get_anomaly_actions(self, metric_name: str, direction: str, severity: str) -> List[str]:
        """Get recommended actions for anomaly"""
        actions = []
        
        if direction == "drop":
            if "users" in metric_name or "registrations" in metric_name:
                actions.append("Check marketing campaigns and acquisition channels")
                actions.append("Review recent product changes or bugs")
            elif "completion" in metric_name or "engagement" in metric_name:
                actions.append("Analyze content quality and relevance")
                actions.append("Survey users for feedback")
            elif "error" in metric_name:
                actions.append("Investigate server logs immediately")
                actions.append("Check recent deployments")
        else:  # spike
            if "error" in metric_name:
                actions.append("Immediate incident response required")
                actions.append("Scale infrastructure if needed")
            elif "users" in metric_name:
                actions.append("Ensure infrastructure can handle load")
                actions.append("Prepare for increased support requests")
        
        if severity == "critical":
            actions.append("Escalate to leadership team")
            actions.append("Prepare incident report")
        
        return actions if actions else ["Investigate root cause", "Monitor closely"]
    
    def _calculate_metric_growth(self, metric_name: str, period: str) -> float:
        """Calculate growth rate for a metric"""
        import random
        return random.uniform(-0.2, 0.3)
    
    def _get_metric_value(self, metric_name: str) -> float:
        """Get single metric value"""
        return self._get_current_metric_value(metric_name)
    
    def _get_historical_data(self, metric_name: str, days: int = 60) -> List[Dict]:
        """Get historical time series data"""
        import random
        data = []
        base_value = self._get_current_metric_value(metric_name)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        for i in range(days):
            date = start_date + timedelta(days=i)
            value = base_value * random.uniform(0.8, 1.2)
            data.append({"date": date, "value": value})
        
        return data
    
    def _calculate_trend(self, data: List[Dict]) -> float:
        """Calculate trend slope from historical data"""
        if len(data) < 2:
            return 0.0
        
        # Simple linear regression
        n = len(data)
        sum_x = sum(range(n))
        sum_y = sum(d["value"] for d in data)
        sum_xy = sum(i * d["value"] for i, d in enumerate(data))
        sum_x2 = sum(i**2 for i in range(n))
        
        denominator = n * sum_x2 - sum_x**2
        if denominator == 0:
            return 0.0
        
        slope = (n * sum_xy - sum_x * sum_y) / denominator
        return slope / 100  # Normalize


# Singleton instance
advanced_analytics_service = AdvancedAnalyticsService()
