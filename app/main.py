"""
CareSphere API - Main Application Entry Point
FastAPI application with all routes, middleware, and configuration
"""

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.api import api_router
from app.middleware.error_handler import init_exception_handlers
import logging

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend API for CareSphere Church/Community Management Platform",
    debug=settings.DEBUG,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory for serving images (like logo)
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
    logger.info(f"Static files mounted at /static from {static_path}")

# Register routers and exception handlers
app.include_router(api_router)
init_exception_handlers(app)


@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "success": True,
        "data": {
            "message": "Welcome to CareSphere API",
            "version": settings.APP_VERSION,
            "status": "running"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "success": True,
        "data": {
            "status": "healthy",
            "version": settings.APP_VERSION,
            "email_configured": bool(settings.EKDSEND_API_KEY),
            "api_base_url": settings.API_BASE_URL,
        }
    }


# TODO: Import and include routers here
# from app.api import auth, members, messages, templates, automation, analytics
# app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
# app.include_router(members.router, prefix="/members", tags=["Members"])
# app.include_router(messages.router, prefix="/messages", tags=["Messages"])
# app.include_router(templates.router, prefix="/templates", tags=["Templates"])
# app.include_router(automation.router, prefix="/automation", tags=["Automation"])
# app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.RELOAD
    )
