from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models.group import Group, GroupMember, GroupPost, GroupEvent, GroupChat
from app.models.user import User
from app.schemas.group import (
    GroupCreate,
    GroupUpdate,
    GroupResponse,
    GroupMemberResponse,
    GroupPostCreate,
    GroupPostResponse,
    GroupEventCreate,
    GroupEventResponse,
)

router = APIRouter(prefix="/groups", tags=["Groups"])


@router.get("/", response_model=List[GroupResponse])
async def get_groups(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    privacy: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get all groups with optional filtering."""
    query = select(Group).where(Group.is_active == True).order_by(Group.created_at.desc())
    
    if category:
        query = query.where(Group.category == category)
    
    if privacy:
        query = query.where(Group.privacy == privacy)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    groups = result.scalars().all()
    
    return groups


@router.post("/", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
async def create_group(
    group_data: GroupCreate,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Create a new group."""
    # Verify user exists
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    new_group = Group(
        name=group_data.name,
        description=group_data.description,
        privacy=group_data.privacy,
        category=group_data.category,
        tags=group_data.tags,
        cover_image_url=group_data.cover_image_url,
        creator_id=user_id,
        requires_approval=group_data.requires_approval,
        rules=group_data.rules,
    )
    
    db.add(new_group)
    await db.flush()  # Get the group ID
    
    # Add creator as owner member
    owner_member = GroupMember(
        user_id=user_id,
        group_id=new_group.id,
        role="owner",
    )
    db.add(owner_member)
    
    await db.commit()
    await db.refresh(new_group)
    
    return new_group


@router.get("/{group_id}", response_model=GroupResponse)
async def get_group(group_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific group by ID."""
    result = await db.execute(select(Group).where(Group.id == group_id))
    group = result.scalar_one_or_none()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    return group


@router.put("/{group_id}", response_model=GroupResponse)
async def update_group(
    group_id: int,
    group_data: GroupUpdate,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Update a group (owner or admin only)."""
    result = await db.execute(select(Group).where(Group.id == group_id))
    group = result.scalar_one_or_none()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    # Check if user is owner or admin
    member_result = await db.execute(
        select(GroupMember).where(
            GroupMember.group_id == group_id,
            GroupMember.user_id == user_id
        )
    )
    member = member_result.scalar_one_or_none()
    
    if not member or member.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this group"
        )
    
    update_data = group_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(group, field, value)
    
    await db.commit()
    await db.refresh(group)
    
    return group


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(
    group_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a group (owner only)."""
    result = await db.execute(select(Group).where(Group.id == group_id))
    group = result.scalar_one_or_none()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    # Check if user is owner
    member_result = await db.execute(
        select(GroupMember).where(
            GroupMember.group_id == group_id,
            GroupMember.user_id == user_id
        )
    )
    member = member_result.scalar_one_or_none()
    
    if not member or member.role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can delete this group"
        )
    
    await db.delete(group)
    await db.commit()


@router.post("/{group_id}/join", response_model=GroupMemberResponse)
async def join_group(
    group_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Join a group."""
    # Verify group exists
    group_result = await db.execute(select(Group).where(Group.id == group_id))
    group = group_result.scalar_one_or_none()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    # Check if already a member
    existing_result = await db.execute(
        select(GroupMember).where(
            GroupMember.group_id == group_id,
            GroupMember.user_id == user_id
        )
    )
    existing = existing_result.scalar_one_or_none()
    
    if existing:
        if existing.is_banned:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are banned from this group"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already a member of this group"
        )
    
    # Create membership
    role = "member" if not group.requires_approval else "pending"
    new_member = GroupMember(
        user_id=user_id,
        group_id=group_id,
        role=role,
    )
    
    db.add(new_member)
    
    # Update member count if approved immediately
    if not group.requires_approval:
        group.member_count += 1
    
    await db.commit()
    await db.refresh(new_member)
    
    return new_member


@router.post("/{group_id}/leave", status_code=status.HTTP_204_NO_CONTENT)
async def leave_group(
    group_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Leave a group."""
    result = await db.execute(
        select(GroupMember).where(
            GroupMember.group_id == group_id,
            GroupMember.user_id == user_id
        )
    )
    member = result.scalar_one_or_none()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not a member of this group"
        )
    
    if member.role == "owner":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Owner cannot leave. Transfer ownership or delete the group."
        )
    
    await db.delete(member)
    
    # Update member count
    group_result = await db.execute(select(Group).where(Group.id == group_id))
    group = group_result.scalar_one_or_none()
    if group and group.member_count > 0:
        group.member_count -= 1
        await db.flush()
    
    await db.commit()


@router.get("/{group_id}/members", response_model=List[GroupMemberResponse])
async def get_group_members(
    group_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    """Get all members of a group."""
    query = select(GroupMember).where(
        GroupMember.group_id == group_id,
        GroupMember.is_banned == False
    ).offset(skip).limit(limit)
    
    result = await db.execute(query)
    members = result.scalars().all()
    
    return members


@router.post("/{group_id}/posts", response_model=GroupPostResponse, status_code=status.HTTP_201_CREATED)
async def create_group_post(
    group_id: int,
    post_data: GroupPostCreate,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Create a post in a group."""
    # Verify membership
    member_result = await db.execute(
        select(GroupMember).where(
            GroupMember.group_id == group_id,
            GroupMember.user_id == user_id,
            GroupMember.is_banned == False
        )
    )
    member = member_result.scalar_one_or_none()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this group or banned"
        )
    
    new_post = GroupPost(
        content=post_data.content,
        images=post_data.images,
        videos=post_data.videos,
        author_id=user_id,
        group_id=group_id,
        is_announcement=post_data.is_announcement,
        is_pinned=post_data.is_pinned,
    )
    
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)
    
    return new_post


@router.post("/{group_id}/events", response_model=GroupEventResponse, status_code=status.HTTP_201_CREATED)
async def create_group_event(
    group_id: int,
    event_data: GroupEventCreate,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Create an event in a group."""
    # Verify user is organizer (owner, admin, or moderator)
    member_result = await db.execute(
        select(GroupMember).where(
            GroupMember.group_id == group_id,
            GroupMember.user_id == user_id,
            GroupMember.is_banned == False
        )
    )
    member = member_result.scalar_one_or_none()
    
    if not member or member.role not in ["owner", "admin", "moderator"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create events"
        )
    
    new_event = GroupEvent(
        title=event_data.title,
        description=event_data.description,
        event_type=event_data.event_type,
        start_time=event_data.start_time,
        end_time=event_data.end_time,
        location=event_data.location,
        meeting_link=event_data.meeting_link,
        group_id=group_id,
        organizer_id=user_id,
        max_attendees=event_data.max_attendees,
    )
    
    db.add(new_event)
    await db.commit()
    await db.refresh(new_event)
    
    return new_event


@router.get("/{group_id}/events", response_model=List[GroupEventResponse])
async def get_group_events(
    group_id: int,
    upcoming: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get events for a group."""
    query = select(GroupEvent).where(
        GroupEvent.group_id == group_id,
        GroupEvent.is_active == True
    ).order_by(GroupEvent.start_time.asc())
    
    if upcoming:
        query = query.where(GroupEvent.start_time >= datetime.utcnow())
    
    result = await db.execute(query)
    events = result.scalars().all()
    
    return events
