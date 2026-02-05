"""Central API router that wires all domain modules."""

from fastapi import APIRouter

from app.api import admin, analytics, auth, automation, bulk, fields, members, messages, settings, templates, monitoring, dashboard, organizations

api_router = APIRouter()

# Dashboard (no prefix - directly at /dashboard)
api_router.include_router(dashboard.router)

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["Organizations"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_router.include_router(bulk.router, prefix="/bulk",
                          tags=["Bulk Operations"])
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
