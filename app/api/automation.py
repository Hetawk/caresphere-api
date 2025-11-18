"""Automation routes."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api import deps
from app.config import settings
from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.automation import (
    AutomationExecutePayload,
    AutomationLogPublic,
    AutomationRuleCreate,
    AutomationRulePublic,
    AutomationRuleUpdate,
)
from app.services import automation_service
from app.utils import pagination, responses

router = APIRouter()

MANAGER_ROLES = (
    UserRole.SUPER_ADMIN,
    UserRole.ADMIN,
    UserRole.MINISTRY_LEADER,
)


@router.get("/")
async def list_rules(
    page: int = Query(settings.PAGE_DEF, ge=1),
    limit: int = Query(settings.PAGE_SIZE_DEF, ge=1, le=settings.PAGE_SIZE_MAX),
    is_active: bool | None = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(deps.require_roles(*MANAGER_ROLES)),
):
    items, total = automation_service.list_rules(db, page=page, limit=limit, is_active=is_active)
    pagination_meta = pagination.paginate_metadata(total=total, page=page, limit=limit)
    data = {
        "rules": [AutomationRulePublic.model_validate(rule).model_dump(by_alias=True) for rule in items],
        "pagination": pagination_meta,
    }
    return responses.success_response(data, metadata={"pagination": pagination_meta})


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_rule(
    payload: AutomationRuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.require_roles(*MANAGER_ROLES)),
):
    rule = automation_service.create_rule(db, payload, current_user=current_user)
    body = AutomationRulePublic.model_validate(rule).model_dump(by_alias=True)
    return responses.success_response(body, status_code=status.HTTP_201_CREATED)


@router.get("/logs")
async def list_logs(
    rule_id: str | None = Query(None, alias="ruleId"),
    limit: int = Query(settings.LOG_LIMIT_DEF, ge=1, le=settings.LOG_LIMIT_MAX),
    db: Session = Depends(get_db),
    _: User = Depends(deps.require_roles(*MANAGER_ROLES)),
):
    logs = automation_service.list_logs(db, rule_id=rule_id, limit=limit)
    data = [AutomationLogPublic.model_validate(log).model_dump(by_alias=True) for log in logs]
    return responses.success_response({"logs": data})


@router.get("/{rule_id}")
async def get_rule(
    rule_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(deps.require_roles(*MANAGER_ROLES)),
):
    rule = automation_service.get_rule(db, rule_id)
    return responses.success_response(AutomationRulePublic.model_validate(rule).model_dump(by_alias=True))


@router.put("/{rule_id}")
async def update_rule(
    rule_id: str,
    payload: AutomationRuleUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(deps.require_roles(*MANAGER_ROLES)),
):
    rule = automation_service.update_rule(db, rule_id, payload)
    return responses.success_response(AutomationRulePublic.model_validate(rule).model_dump(by_alias=True))


@router.delete("/{rule_id}")
async def delete_rule(
    rule_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(deps.require_roles(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
):
    automation_service.delete_rule(db, rule_id)
    return responses.success_response({"message": "Automation rule deleted successfully"})


@router.post("/{rule_id}/execute")
async def execute_rule(
    rule_id: str,
    payload: AutomationExecutePayload | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(deps.require_roles(*MANAGER_ROLES)),
):
    log = automation_service.execute_rule(db, rule_id, trigger_data=payload.triggerData if payload else None)
    body = AutomationLogPublic.model_validate(log).model_dump(by_alias=True)
    return responses.success_response(body)
