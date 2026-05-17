"""
Live Challenges API Module
Handles creation, participation, and leaderboard management for wellness challenges.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
import uuid

router = APIRouter(prefix="/api/v1/challenges", tags=["Challenges"])

# --- Enums ---

class ChallengeType(str, Enum):
    STEPS = "steps"
    WORKOUT_MINUTES = "workout_minutes"
    WATER_INTAKE = "water_intake"
    HABIT_STREAK = "habit_streak"
    WEIGHT_LOSS = "weight_loss"  # Percentage based for privacy
    MEDITATION_MINUTES = "meditation_minutes"
    SUGAR_FREE = "sugar_free_days"
    CUSTOM = "custom"

class ChallengeVisibility(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    FRIENDS_ONLY = "friends_only"

class ChallengeStatus(str, Enum):
    UPCOMING = "upcoming"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

# --- Models ---

class ChallengeCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., max_length=500)
    challenge_type: ChallengeType
    goal_value: int = Field(..., gt=0, description="Target value (e.g., 10000 steps)")
    start_date: datetime
    end_date: datetime
    visibility: ChallengeVisibility = ChallengeVisibility.PUBLIC
    max_participants: Optional[int] = None
    team_based: bool = False
    entry_fee: float = 0.0
    prize_pool: float = 0.0
    sponsor_id: Optional[str] = None

class ChallengeUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    goal_value: Optional[int] = None
    visibility: Optional[ChallengeVisibility] = None
    status: Optional[ChallengeStatus] = None

class ChallengeParticipant(BaseModel):
    user_id: str
    joined_at: datetime
    current_progress: float = 0.0
    completion_percentage: float = 0.0
    rank: Optional[int] = None
    team_id: Optional[str] = None
    check_ins: int = 0
    last_activity: datetime

class ChallengeResponse(BaseModel):
    id: str
    title: str
    description: str
    challenge_type: ChallengeType
    goal_value: int
    start_date: datetime
    end_date: datetime
    visibility: ChallengeVisibility
    status: ChallengeStatus
    participant_count: int
    team_based: bool
    creator_id: str
    created_at: datetime
    top_participants: List[Dict[str, Any]] = []

# --- Mock Database ---

challenges_db: Dict[str, Dict[str, Any]] = {}
participants_db: Dict[str, List[Dict[str, Any]]] = {}  # challenge_id -> list of participants

# --- Helper Functions ---

def calculate_status(start: datetime, end: datetime) -> ChallengeStatus:
    now = datetime.utcnow()
    if now < start:
        return ChallengeStatus.UPCOMING
    elif now > end:
        return ChallengeStatus.COMPLETED
    return ChallengeStatus.ACTIVE

def update_leaderboard(challenge_id: str):
    """Recalculates ranks for a challenge."""
    if challenge_id not in participants_db:
        return
    
    # Sort by progress descending
    sorted_participants = sorted(
        participants_db[challenge_id],
        key=lambda x: x['current_progress'],
        reverse=True
    )
    
    for rank, participant in enumerate(sorted_participants, 1):
        participant['rank'] = rank

# --- Endpoints ---

@router.post("/", response_model=ChallengeResponse, status_code=201)
async def create_challenge(challenge: ChallengeCreate, user_id: str = "current_user"):
    """Create a new wellness challenge."""
    
    if challenge.start_date >= challenge.end_date:
        raise HTTPException(status_code=400, detail="Start date must be before end date")
    
    challenge_id = str(uuid.uuid4())
    
    challenge_data = {
        "id": challenge_id,
        **challenge.dict(),
        "creator_id": user_id,
        "created_at": datetime.utcnow(),
        "status": calculate_status(challenge.start_date, challenge.end_date),
        "participant_count": 0
    }
    
    challenges_db[challenge_id] = challenge_data
    participants_db[challenge_id] = []
    
    return ChallengeResponse(
        **challenge_data,
        top_participants=[]
    )

@router.get("/", response_model=List[ChallengeResponse])
async def list_challenges(
    status: Optional[ChallengeStatus] = None,
    challenge_type: Optional[ChallengeType] = None,
    visibility: Optional[ChallengeVisibility] = ChallengeVisibility.PUBLIC,
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0)
):
    """List challenges with filtering."""
    
    results = []
    for ch_id, ch_data in challenges_db.items():
        # Filter by status (dynamic)
        current_status = calculate_status(ch_data['start_date'], ch_data['end_date'])
        if status and current_status != status:
            continue
        
        # Filter by type
        if challenge_type and ch_data['challenge_type'] != challenge_type.value:
            continue
            
        # Filter by visibility
        if visibility and ch_data['visibility'] != visibility.value:
            continue
            
        # Get top 3 participants
        top_participants = []
        if ch_id in participants_db:
            sorted_parts = sorted(
                participants_db[ch_id],
                key=lambda x: x['current_progress'],
                reverse=True
            )[:3]
            top_participants = [
                {"user_id": p['user_id'], "progress": p['current_progress'], "rank": p['rank']}
                for p in sorted_parts
            ]
        
        results.append(ChallengeResponse(
            **ch_data,
            status=current_status,
            top_participants=top_participants
        ))
    
    # Apply pagination
    paginated = results[offset:offset+limit]
    return paginated

@router.get("/{challenge_id}", response_model=ChallengeResponse)
async def get_challenge(challenge_id: str):
    """Get details of a specific challenge."""
    
    if challenge_id not in challenges_db:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    ch_data = challenges_db[challenge_id]
    current_status = calculate_status(ch_data['start_date'], ch_data['end_date'])
    
    # Get top participants
    top_participants = []
    if challenge_id in participants_db:
        sorted_parts = sorted(
            participants_db[challenge_id],
            key=lambda x: x['current_progress'],
            reverse=True
        )[:10]
        top_participants = [
            {"user_id": p['user_id'], "progress": p['current_progress'], "rank": p['rank']}
            for p in sorted_parts
        ]
    
    return ChallengeResponse(
        **ch_data,
        status=current_status,
        top_participants=top_participants
    )

@router.post("/{challenge_id}/join")
async def join_challenge(challenge_id: str, user_id: str = "current_user"):
    """Join a challenge."""
    
    if challenge_id not in challenges_db:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    ch_data = challenges_db[challenge_id]
    
    # Check status
    current_status = calculate_status(ch_data['start_date'], ch_data['end_date'])
    if current_status != ChallengeStatus.ACTIVE and current_status != ChallengeStatus.UPCOMING:
        raise HTTPException(status_code=400, detail="Cannot join this challenge")
    
    # Check capacity
    if ch_data.get('max_participants') and len(participants_db.get(challenge_id, [])) >= ch_data['max_participants']:
        raise HTTPException(status_code=400, detail="Challenge is full")
    
    # Check if already joined
    for participant in participants_db.get(challenge_id, []):
        if participant['user_id'] == user_id:
            raise HTTPException(status_code=400, detail="Already joined this challenge")
    
    # Add participant
    new_participant = {
        "user_id": user_id,
        "joined_at": datetime.utcnow(),
        "current_progress": 0.0,
        "completion_percentage": 0.0,
        "rank": None,
        "team_id": None,
        "check_ins": 0,
        "last_activity": datetime.utcnow()
    }
    
    if challenge_id not in participants_db:
        participants_db[challenge_id] = []
    
    participants_db[challenge_id].append(new_participant)
    challenges_db[challenge_id]['participant_count'] = len(participants_db[challenge_id])
    
    update_leaderboard(challenge_id)
    
    return {"message": "Successfully joined challenge", "challenge_id": challenge_id}

@router.post("/{challenge_id}/progress")
async def submit_progress(
    challenge_id: str,
    value: float = Field(..., gt=0),
    user_id: str = "current_user"
):
    """Submit progress for a challenge (e.g., steps today)."""
    
    if challenge_id not in challenges_db:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    # Find participant
    participant = None
    for p in participants_db.get(challenge_id, []):
        if p['user_id'] == user_id:
            participant = p
            break
    
    if not participant:
        raise HTTPException(status_code=404, detail="Not a participant of this challenge")
    
    # Update progress (logic depends on challenge type)
    ch_data = challenges_db[challenge_id]
    
    # For simplicity, we're adding to cumulative progress
    # In real app, you'd have logic for daily vs cumulative
    participant['current_progress'] += value
    participant['check_ins'] += 1
    participant['last_activity'] = datetime.utcnow()
    
    # Calculate percentage
    goal = ch_data['goal_value']
    participant['completion_percentage'] = min(100.0, (participant['current_progress'] / goal) * 100)
    
    update_leaderboard(challenge_id)
    
    return {
        "message": "Progress updated",
        "current_progress": participant['current_progress'],
        "completion_percentage": participant['completion_percentage'],
        "rank": participant['rank']
    }

@router.get("/{challenge_id}/leaderboard")
async def get_leaderboard(
    challenge_id: str,
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0)
):
    """Get challenge leaderboard."""
    
    if challenge_id not in challenges_db:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    if challenge_id not in participants_db:
        return {"participants": [], "total": 0}
    
    # Ensure leaderboard is up to date
    update_leaderboard(challenge_id)
    
    sorted_participants = sorted(
        participants_db[challenge_id],
        key=lambda x: x['current_progress'],
        reverse=True
    )
    
    paginated = sorted_participants[offset:offset+limit]
    
    return {
        "challenge_id": challenge_id,
        "total_participants": len(participants_db[challenge_id]),
        "participants": paginated
    }

@router.delete("/{challenge_id}")
async def delete_challenge(challenge_id: str, user_id: str = "current_user"):
    """Delete a challenge (creator or admin only)."""
    
    if challenge_id not in challenges_db:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    ch_data = challenges_db[challenge_id]
    if ch_data['creator_id'] != user_id:
        raise HTTPException(status_code=403, detail="Only creator can delete challenge")
    
    del challenges_db[challenge_id]
    if challenge_id in participants_db:
        del participants_db[challenge_id]
    
    return {"message": "Challenge deleted successfully"}

@router.get("/my-challenges")
async def get_my_challenges(user_id: str = "current_user"):
    """Get all challenges a user is participating in."""
    
    my_challenges = []
    
    for ch_id, participants in participants_db.items():
        for p in participants:
            if p['user_id'] == user_id:
                ch_data = challenges_db.get(ch_id)
                if ch_data:
                    current_status = calculate_status(ch_data['start_date'], ch_data['end_date'])
                    my_challenges.append({
                        "challenge": ChallengeResponse(
                            **ch_data,
                            status=current_status,
                            top_participants=[]
                        ),
                        "my_progress": p['current_progress'],
                        "my_rank": p['rank'],
                        "completion_percentage": p['completion_percentage']
                    })
    
    return my_challenges
