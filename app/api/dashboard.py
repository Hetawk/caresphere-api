"""Main dashboard endpoint for CareSphere API."""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from app.utils.html_templates_v2 import get_dashboard_html

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard() -> str:
    """
    Visual dashboard with user management interface.
    Public endpoint - no authentication required for viewing.
    """
    return get_dashboard_html()
