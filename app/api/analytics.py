"""Analytics routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.config import settings
from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.analytics import DashboardAnalytics
from app.services import analytics_service
from app.utils import responses

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard(
    db: Session = Depends(get_db),
    _: User = Depends(deps.require_roles(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
):
    if not settings.ENABLE_ANALYTICS:
        raise HTTPException(status_code=403, detail="Analytics is disabled")
    data = analytics_service.get_dashboard_metrics(db)
    payload = DashboardAnalytics.model_validate(data).model_dump(by_alias=True)
    return responses.success_response(payload)
