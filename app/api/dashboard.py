"""Main dashboard endpoint for CareSphere API."""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from app.utils.html_templates import get_dashboard_html

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard() -> str:
    """
    Visual dashboard showing all available API endpoints with sidebar navigation.
    Public endpoint - no authentication required.
    """
    return get_dashboard_html()
