"""Analytics service providing dashboard level metrics."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.automation import AutomationRule
from app.models.member import Member, MemberActivity, MemberStatus
from app.models.message import Message, MessageStatus


def get_dashboard_metrics(db: Session) -> dict:
    now = datetime.now(timezone.utc)
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    total_members = db.query(func.count(Member.id)).scalar() or 0
    active_members = (
        db.query(func.count(Member.id))
        .filter(Member.member_status == MemberStatus.ACTIVE)
        .scalar()
        or 0
    )
    new_members = (
        db.query(func.count(Member.id))
        .filter(Member.created_at >= start_of_month)
        .scalar()
        or 0
    )

    messages_sent = (
        db.query(func.count(Message.id))
        .filter(
            Message.status == MessageStatus.SENT,
            Message.sent_at >= start_of_month,
        )
        .scalar()
        or 0
    )

    totals = (
        db.query(
            func.coalesce(func.sum(Message.opened_count), 0),
            func.coalesce(func.sum(Message.clicked_count), 0),
            func.coalesce(func.sum(Message.recipient_count), 0),
        )
        .filter(Message.recipient_count > 0)
        .one()
    )
    opened_sum, clicked_sum, recipient_sum = totals
    average_open_rate = (opened_sum / recipient_sum * 100) if recipient_sum else 0
    average_click_rate = (clicked_sum / recipient_sum * 100) if recipient_sum else 0

    automation_rules_active = (
        db.query(func.count(AutomationRule.id))
        .filter(AutomationRule.is_active.is_(True))
        .scalar()
        or 0
    )

    activity_rows = (
        db.query(MemberActivity.activity_type, func.count(MemberActivity.id))
        .group_by(MemberActivity.activity_type)
        .order_by(func.count(MemberActivity.id).desc())
        .limit(5)
        .all()
    )
    recent_activities = [
        {"label": activity_type or "unknown", "value": count}
        for activity_type, count in activity_rows
    ]

    return {
        "totalMembers": total_members,
        "activeMembers": active_members,
        "newMembersThisMonth": new_members,
        "messagesSentThisMonth": messages_sent,
        "averageOpenRate": round(average_open_rate, 2),
        "averageClickRate": round(average_click_rate, 2),
        "automationRulesActive": automation_rules_active,
        "recentActivities": recent_activities,
        "generatedAt": now,
    }
