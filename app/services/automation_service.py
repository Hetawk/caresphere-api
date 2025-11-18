"""Automation service layer."""

from __future__ import annotations

from datetime import datetime
from typing import List, Tuple

from sqlalchemy.orm import Session

from app.config import settings
from app.models.automation import AutomationLog, AutomationRule
from app.models.user import User
from app.schemas.automation import AutomationRuleCreate, AutomationRuleUpdate
from app.utils.exceptions import NotFoundError


def list_rules(db: Session, *, page: int, limit: int, is_active: bool | None = None) -> Tuple[List[AutomationRule], int]:
    query = db.query(AutomationRule)
    if is_active is not None:
        query = query.filter(AutomationRule.is_active.is_(is_active))
    total = query.count()
    items = (
        query.order_by(AutomationRule.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )
    return items, total


def create_rule(db: Session, payload: AutomationRuleCreate, *, current_user: User) -> AutomationRule:
    rule = AutomationRule(
        name=payload.name,
        description=payload.description,
        trigger_type=payload.triggerType,
        trigger_config=payload.triggerConfig,
        action_type=payload.actionType,
        action_config=payload.actionConfig,
        conditions=payload.conditions,
        is_active=payload.isActive,
        created_by=current_user.id,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


def get_rule(db: Session, rule_id: str) -> AutomationRule:
    rule = db.get(AutomationRule, rule_id)
    if not rule:
        raise NotFoundError("Automation rule", rule_id)
    return rule


def update_rule(db: Session, rule_id: str, payload: AutomationRuleUpdate) -> AutomationRule:
    rule = get_rule(db, rule_id)
    update_data = payload.model_dump(exclude_unset=True, by_alias=True)
    for key, value in update_data.items():
        setattr(rule, key, value)
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


def delete_rule(db: Session, rule_id: str) -> None:
    rule = get_rule(db, rule_id)
    db.delete(rule)
    db.commit()


def execute_rule(db: Session, rule_id: str, *, trigger_data: dict | None = None) -> AutomationLog:
    rule = get_rule(db, rule_id)
    rule.run_count += 1
    log = AutomationLog(
        rule_id=rule_id,
        status="success",
        trigger_data=trigger_data or {},
        action_result={"message": "Execution queued"},
        executed_at=datetime.utcnow(),
        execution_time_ms=10,
    )
    rule.last_run_at = log.executed_at
    rule.success_count += 1
    db.add_all([rule, log])
    db.commit()
    db.refresh(log)
    return log


def list_logs(
    db: Session,
    *,
    rule_id: str | None = None,
    limit: int = settings.LOG_LIMIT_DEF,
) -> List[AutomationLog]:
    query = db.query(AutomationLog)
    if rule_id:
        query = query.filter(AutomationLog.rule_id == rule_id)
    return query.order_by(AutomationLog.created_at.desc()).limit(limit).all()
