from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.core.database import get_db
from app.models.message import Message, GroupChatMessage
from app.models.user import User
from app.schemas.message import MessageResponse

router = APIRouter(prefix="/messages", tags=["Messages"])


@router.get("/conversations", response_model=List[dict])
async def get_conversations(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get list of all conversations for a user."""
    # Get messages sent by user
    sent_result = await db.execute(
        select(Message.receiver_id).where(Message.sender_id == user_id)
    )
    sent_to = set([row[0] for row in sent_result.fetchall()])
    
    # Get messages received by user
    received_result = await db.execute(
        select(Message.sender_id).where(Message.receiver_id == user_id)
    )
    received_from = set([row[0] for row in received_result.fetchall()])
    
    # Combine unique conversation partners
    conversation_partners = sent_to.union(received_from)
    
    conversations = []
    for partner_id in conversation_partners:
        # Get latest message with this partner
        result = await db.execute(
            select(Message)
            .where(
                ((Message.sender_id == user_id) & (Message.receiver_id == partner_id)) |
                ((Message.sender_id == partner_id) & (Message.receiver_id == user_id))
            )
            .order_by(Message.created_at.desc())
            .limit(1)
        )
        latest_message = result.scalar_one_or_none()
        
        if latest_message:
            conversations.append({
                "partner_id": partner_id,
                "latest_message": latest_message,
                "unread_count": 0  # Would need to calculate
            })
    
    return conversations


@router.get("/{partner_id}", response_model=List[MessageResponse])
async def get_messages_with_user(
    partner_id: int,
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    """Get messages between current user and a specific partner."""
    query = select(Message).where(
        ((Message.sender_id == user_id) & (Message.receiver_id == partner_id)) |
        ((Message.sender_id == partner_id) & (Message.receiver_id == user_id))
    ).order_by(Message.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    messages = result.scalars().all()
    
    return list(messages)


@router.post("/", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    receiver_id: int,
    content: str,
    message_type: str = "text",
    media_url: Optional[str] = None,
    user_id: int = None,
    db: AsyncSession = Depends(get_db)
):
    """Send a direct message to another user."""
    # Verify sender exists
    sender_result = await db.execute(select(User).where(User.id == user_id))
    sender = sender_result.scalar_one_or_none()
    
    if not sender:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sender not found"
        )
    
    # Verify receiver exists
    receiver_result = await db.execute(select(User).where(User.id == receiver_id))
    receiver = receiver_result.scalar_one_or_none()
    
    if not receiver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receiver not found"
        )
    
    if user_id == receiver_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot send message to yourself"
        )
    
    new_message = Message(
        content=content,
        message_type=message_type,
        media_url=media_url,
        sender_id=user_id,
        receiver_id=receiver_id,
    )
    
    db.add(new_message)
    await db.commit()
    await db.refresh(new_message)
    
    return new_message


@router.put("/{message_id}/read")
async def mark_message_as_read(
    message_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Mark a message as read."""
    result = await db.execute(select(Message).where(Message.id == message_id))
    message = result.scalar_one_or_none()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    if message.receiver_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to mark this message as read"
        )
    
    from datetime import datetime
    message.is_read = True
    message.read_at = datetime.utcnow()
    
    await db.commit()
    
    return {"message": "Message marked as read"}


@router.post("/{message_id}/reaction")
async def add_reaction(
    message_id: int,
    emoji: str,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Add a reaction to a message."""
    result = await db.execute(select(Message).where(Message.id == message_id))
    message = result.scalar_one_or_none()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Initialize reactions if None
    if message.reactions is None:
        message.reactions = {}
    
    # Add or increment reaction
    if emoji in message.reactions:
        message.reactions[emoji] += 1
    else:
        message.reactions[emoji] = 1
    
    await db.commit()
    
    return {"message": "Reaction added", "reactions": message.reactions}


from app.schemas.message import MessageResponse, GroupChatMessageResponse

# Group Chat Endpoints

@router.get("/group/{chat_id}", response_model=List[GroupChatMessageResponse])
async def get_group_chat_messages(
    chat_id: int,
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    """Get messages from a group chat."""
    # Verify user is member of the group chat
    from app.models.group import GroupChat, GroupMember
    chat_result = await db.execute(select(GroupChat).where(GroupChat.id == chat_id))
    chat = chat_result.scalar_one_or_none()
    
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group chat not found"
        )
    
    # Check membership
    member_result = await db.execute(
        select(GroupMember).where(
            GroupMember.group_id == chat.group_id,
            GroupMember.user_id == user_id
        )
    )
    member = member_result.scalar_one_or_none()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this group"
        )
    
    query = select(GroupChatMessage).where(
        GroupChatMessage.chat_id == chat_id
    ).order_by(GroupChatMessage.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    messages = result.scalars().all()
    
    return list(messages)


@router.post("/group/{chat_id}", response_model=GroupChatMessageResponse, status_code=status.HTTP_201_CREATED)
async def send_group_chat_message(
    chat_id: int,
    content: str,
    message_type: str = "text",
    media_url: Optional[str] = None,
    user_id: int = None,
    db: AsyncSession = Depends(get_db)
):
    """Send a message to a group chat."""
    from app.models.group import GroupChat, GroupMember
    
    # Verify chat exists
    chat_result = await db.execute(select(GroupChat).where(GroupChat.id == chat_id))
    chat = chat_result.scalar_one_or_none()
    
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group chat not found"
        )
    
    # Verify membership
    member_result = await db.execute(
        select(GroupMember).where(
            GroupMember.group_id == chat.group_id,
            GroupMember.user_id == user_id
        )
    )
    member = member_result.scalar_one_or_none()
    
    if not member or member.is_banned:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this group or banned"
        )
    
    new_message = GroupChatMessage(
        content=content,
        message_type=message_type,
        media_url=media_url,
        sender_id=user_id,
        chat_id=chat_id,
    )
    
    db.add(new_message)
    await db.commit()
    await db.refresh(new_message)
    
    return new_message
