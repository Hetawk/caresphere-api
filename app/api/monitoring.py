"""Monitoring and statistics endpoints for CareSphere API."""

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from typing import Dict, Any

from app.database import get_db
from app.models.message import Message
from app.models.user import User
from app.api.deps import get_current_user
from app.utils.html_templates import get_health_check_response

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Public health check endpoint.
    Returns API status and version.
    """
    return get_health_check_response(version="1.0.0")


@router.get("/stats")
async def get_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get email sending statistics.
    Requires authentication.

    Returns:
        - Total messages sent
        - Success/failure counts
        - Recent activity summary
    """
    # Calculate date ranges
    today = datetime.utcnow().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    # Total messages
    total_result = await db.execute(
        select(func.count(Message.id))
    )
    total_messages = total_result.scalar() or 0

    # Messages today
    today_result = await db.execute(
        select(func.count(Message.id))
        .where(func.date(Message.created_at) == today)
    )
    messages_today = today_result.scalar() or 0

    # Messages this week
    week_result = await db.execute(
        select(func.count(Message.id))
        .where(func.date(Message.created_at) >= week_ago)
    )
    messages_this_week = week_result.scalar() or 0

    # Messages this month
    month_result = await db.execute(
        select(func.count(Message.id))
        .where(func.date(Message.created_at) >= month_ago)
    )
    messages_this_month = month_result.scalar() or 0

    # Failed messages today
    failed_today_result = await db.execute(
        select(func.count(Message.id))
        .where(
            func.date(Message.created_at) == today,
            Message.status.in_(['failed', 'bounced'])
        )
    )
    failed_today = failed_today_result.scalar() or 0

    # Calculate success rate
    success_rate = (
        ((messages_today - failed_today) / messages_today * 100)
        if messages_today > 0 else 100.0
    )

    return {
        "success": True,
        "data": {
            "overview": {
                "total_messages": total_messages,
                "messages_today": messages_today,
                "messages_this_week": messages_this_week,
                "messages_this_month": messages_this_month,
            },
            "today": {
                "sent": messages_today,
                "failed": failed_today,
                "success_rate": round(success_rate, 2),
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    }


@router.get("/recent")
async def get_recent_messages(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get recent messages.
    Requires authentication.

    Args:
        limit: Number of recent messages to return (default: 10, max: 50)

    Returns:
        List of recent messages with status
    """
    # Limit maximum to 50
    limit = min(limit, 50)

    # Fetch recent messages
    result = await db.execute(
        select(Message)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    messages = result.scalars().all()

    return {
        "success": True,
        "data": [
            {
                "id": msg.id,
                "type": msg.type,
                "recipient": msg.recipient,
                "subject": msg.subject,
                "status": msg.status,
                "created_at": msg.created_at.isoformat() if msg.created_at else None,
            }
            for msg in messages
        ],
        "count": len(messages),
    }
