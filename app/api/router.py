"""Central API router that wires all domain modules."""

from fastapi import APIRouter

from app.api import analytics, auth, automation, fields, members, messages, settings, templates, monitoring

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(members.router, prefix="/members", tags=["Members"])
api_router.include_router(
    messages.router, prefix="/messages", tags=["Messages"])
api_router.include_router(
    settings.router, prefix="/settings", tags=["Settings"])
api_router.include_router(
    templates.router, prefix="/templates", tags=["Templates"])
api_router.include_router(
    automation.router, prefix="/automation", tags=["Automation"])
api_router.include_router(
    analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(
    fields.router, prefix="/fields", tags=["Field Configuration"])
api_router.include_router(
    monitoring.router, tags=["Monitoring & Statistics"])
