"""
Wearable Integration Service
Syncs data from Fitbit, Apple Health, Google Fit, Garmin, and Oura.
"""
from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from enum import Enum
import random

class WearableProvider(str, Enum):
    FITBIT = "fitbit"
    APPLE_HEALTH = "apple_health"
    GOOGLE_FIT = "google_fit"
    GARMIN = "garmin"
    OURA = "oura"

class ActivityType(str, Enum):
    WALKING = "walking"
    RUNNING = "running"
    CYCLING = "cycling"
    SWIMMING = "swimming"
    YOGA = "yoga"
    STRENGTH_TRAINING = "strength_training"
    SLEEP = "sleep"
    HEART_RATE = "heart_rate"

class WearableDataPoint(BaseModel):
    timestamp: datetime
    value: float
    unit: str
    source: WearableProvider
    activity_type: Optional[ActivityType] = None

class DailySummary(BaseModel):
    date: str
    steps: int
    distance_km: float
    active_minutes: int
    calories_burned: int
    heart_rate_avg: float
    heart_rate_max: float
    sleep_hours: float
    sleep_quality_score: Optional[int]  # 0-100
    floors_climbed: int
    provider: WearableProvider

class WearableIntegrationService:
    def __init__(self):
        self.connected_devices: Dict[str, Dict] = {}  # user_id -> device_info
        
    def connect_device(self, user_id: str, provider: WearableProvider, auth_token: str) -> bool:
        """
        Connect a wearable device to user account.
        In production, this handles OAuth flow with the provider.
        """
        # Simulate successful connection
        self.connected_devices[user_id] = {
            "provider": provider,
            "connected_at": datetime.now(),
            "status": "active",
            "last_sync": None
        }
        return True
    
    def disconnect_device(self, user_id: str) -> bool:
        """Disconnect wearable device"""
        if user_id in self.connected_devices:
            del self.connected_devices[user_id]
            return True
        return False
    
    def is_connected(self, user_id: str) -> bool:
        """Check if user has connected wearable"""
        return user_id in self.connected_devices
    
    def get_provider(self, user_id: str) -> Optional[WearableProvider]:
        """Get connected provider for user"""
        if user_id in self.connected_devices:
            return self.connected_devices[user_id]["provider"]
        return None

    def sync_data(self, user_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Sync data from connected wearable.
        In production, calls provider APIs (Fitbit API, HealthKit, etc.)
        """
        if user_id not in self.connected_devices:
            return {"error": "No device connected"}
        
        provider = self.connected_devices[user_id]["provider"]
        
        # Simulate fetching data based on provider
        if provider == WearableProvider.FITBIT:
            return self._fetch_fitbit_data(start_date, end_date)
        elif provider == WearableProvider.APPLE_HEALTH:
            return self._fetch_apple_health_data(start_date, end_date)
        elif provider == WearableProvider.GARMIN:
            return self._fetch_garmin_data(start_date, end_date)
        else:
            return self._fetch_generic_data(provider, start_date, end_date)

    def _fetch_fitbit_data(self, start: datetime, end: datetime) -> Dict[str, Any]:
        """Simulate Fitbit API response"""
        return {
            "provider": "fitbit",
            "summary": {
                "steps": random.randint(5000, 15000),
                "distance_km": round(random.uniform(3, 12), 2),
                "active_minutes": random.randint(30, 90),
                "calories_burned": random.randint(1800, 2800),
                "heart_rate_avg": random.randint(60, 80),
                "heart_rate_max": random.randint(140, 170),
                "sleep_hours": round(random.uniform(6, 8.5), 2),
                "sleep_quality_score": random.randint(60, 95),
                "floors_climbed": random.randint(2, 15)
            },
            "activities": [
                {"type": "walking", "duration_min": 30, "calories": 150},
                {"type": "strength_training", "duration_min": 45, "calories": 280}
            ],
            "synced_at": datetime.now().isoformat()
        }

    def _fetch_apple_health_data(self, start: datetime, end: datetime) -> Dict[str, Any]:
        """Simulate Apple HealthKit response"""
        return {
            "provider": "apple_health",
            "summary": {
                "steps": random.randint(6000, 16000),
                "distance_km": round(random.uniform(4, 13), 2),
                "active_minutes": random.randint(40, 100),
                "calories_burned": random.randint(1900, 2900),
                "heart_rate_avg": random.randint(58, 78),
                "heart_rate_max": random.randint(145, 175),
                "sleep_hours": round(random.uniform(6.5, 9), 2),
                "sleep_quality_score": None,  # Apple Health doesn't provide single score
                "floors_climbed": random.randint(3, 18)
            },
            "activities": [
                {"type": "running", "duration_min": 25, "calories": 280},
                {"type": "yoga", "duration_min": 30, "calories": 120}
            ],
            "synced_at": datetime.now().isoformat()
        }

    def _fetch_garmin_data(self, start: datetime, end: datetime) -> Dict[str, Any]:
        """Simulate Garmin Connect response"""
        return {
            "provider": "garmin",
            "summary": {
                "steps": random.randint(7000, 18000),
                "distance_km": round(random.uniform(5, 15), 2),
                "active_minutes": random.randint(50, 120),
                "calories_burned": random.randint(2000, 3200),
                "heart_rate_avg": random.randint(55, 75),
                "heart_rate_max": random.randint(150, 180),
                "sleep_hours": round(random.uniform(6, 8), 2),
                "sleep_quality_score": random.randint(70, 98),
                "floors_climbed": random.randint(5, 20),
                "body_battery": random.randint(40, 100)  # Garmin specific
            },
            "activities": [
                {"type": "cycling", "duration_min": 60, "calories": 450},
                {"type": "swimming", "duration_min": 30, "calories": 250}
            ],
            "synced_at": datetime.now().isoformat()
        }

    def _fetch_generic_data(self, provider: WearableProvider, start: datetime, end: datetime) -> Dict[str, Any]:
        """Generic fallback data"""
        return {
            "provider": provider.value,
            "summary": {
                "steps": random.randint(5000, 12000),
                "distance_km": round(random.uniform(3, 10), 2),
                "active_minutes": random.randint(30, 80),
                "calories_burned": random.randint(1800, 2500),
                "heart_rate_avg": random.randint(60, 80),
                "heart_rate_max": random.randint(140, 165),
                "sleep_hours": round(random.uniform(6, 8), 2),
                "sleep_quality_score": random.randint(60, 90),
                "floors_climbed": random.randint(2, 12)
            },
            "activities": [],
            "synced_at": datetime.now().isoformat()
        }

    def get_real_time_heart_rate(self, user_id: str) -> Optional[float]:
        """Get current heart rate if available"""
        if not self.is_connected(user_id):
            return None
        # Simulate real-time reading
        return random.uniform(60, 100)

    def calculate_activity_goals_progress(self, user_id: str, daily_goal_steps: int = 10000) -> Dict[str, Any]:
        """Calculate progress towards daily goals"""
        if not self.is_connected(user_id):
            return {"error": "No device connected"}
        
        # Get today's data
        today = datetime.now()
        data = self.sync_data(user_id, today, today)
        
        if "error" in data:
            return data
            
        summary = data["summary"]
        steps = summary.get("steps", 0)
        
        return {
            "steps_current": steps,
            "steps_goal": daily_goal_steps,
            "progress_percent": min((steps / daily_goal_steps) * 100, 100),
            "remaining_steps": max(daily_goal_steps - steps, 0),
            "on_track": steps >= (daily_goal_steps * 0.5)  # Assuming mid-day check
        }

# Singleton instance
wearable_service = WearableIntegrationService()
