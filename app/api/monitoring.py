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

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Public health check endpoint.
    Returns API status and version.
    """
    return {
        "success": True,
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


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


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard() -> str:
    """
    Visual dashboard showing all available API endpoints.
    Public endpoint - no authentication required.
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>CareSphere API Dashboard</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 12px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                overflow: hidden;
            }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 40px;
                text-align: center;
            }
            .header h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
            }
            .header p {
                font-size: 1.2em;
                opacity: 0.9;
            }
            .status {
                background: #f8f9fa;
                padding: 20px 40px;
                border-bottom: 1px solid #e9ecef;
            }
            .status-badge {
                display: inline-block;
                padding: 8px 16px;
                background: #28a745;
                color: white;
                border-radius: 20px;
                font-weight: bold;
                margin-right: 20px;
            }
            .quick-links {
                background: #fff3cd;
                padding: 20px 40px;
                border-bottom: 1px solid #ffc107;
            }
            .quick-links h3 {
                color: #856404;
                margin-bottom: 10px;
            }
            .quick-links a {
                display: inline-block;
                margin: 5px 10px 5px 0;
                padding: 8px 16px;
                background: #ffc107;
                color: #212529;
                text-decoration: none;
                border-radius: 6px;
                font-weight: 500;
                transition: background 0.3s;
            }
            .quick-links a:hover {
                background: #e0a800;
            }
            .content {
                padding: 40px;
            }
            .section {
                margin-bottom: 40px;
            }
            .section h2 {
                color: #667eea;
                font-size: 1.8em;
                margin-bottom: 20px;
                padding-bottom: 10px;
                border-bottom: 2px solid #667eea;
            }
            .endpoint-card {
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 15px;
                transition: all 0.3s;
            }
            .endpoint-card:hover {
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                transform: translateY(-2px);
            }
            .endpoint-header {
                display: flex;
                align-items: center;
                margin-bottom: 10px;
            }
            .method {
                display: inline-block;
                padding: 4px 12px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 0.85em;
                margin-right: 15px;
                min-width: 60px;
                text-align: center;
            }
            .method.get { background: #28a745; color: white; }
            .method.post { background: #007bff; color: white; }
            .method.put { background: #ffc107; color: #212529; }
            .method.patch { background: #17a2b8; color: white; }
            .method.delete { background: #dc3545; color: white; }
            .endpoint-path {
                font-family: 'Courier New', monospace;
                font-size: 1.1em;
                color: #495057;
                font-weight: 600;
            }
            .endpoint-description {
                color: #6c757d;
                line-height: 1.6;
                margin-bottom: 10px;
            }
            .auth-badge {
                display: inline-block;
                padding: 4px 10px;
                background: #dc3545;
                color: white;
                border-radius: 4px;
                font-size: 0.8em;
                margin-top: 8px;
            }
            .auth-badge.public {
                background: #28a745;
            }
            .footer {
                background: #f8f9fa;
                padding: 20px 40px;
                text-align: center;
                color: #6c757d;
                border-top: 1px solid #dee2e6;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏥 CareSphere API</h1>
                <p>Church & Community Management Platform</p>
            </div>
            
            <div class="status">
                <span class="status-badge">✓ ONLINE</span>
                <span>Version 1.0.0 • Updated: """ + datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC") + """</span>
            </div>
            
            <div class="quick-links">
                <h3>📚 Quick Access</h3>
                <a href="/docs" target="_blank">Interactive API Docs (Swagger)</a>
                <a href="/redoc" target="_blank">API Documentation (ReDoc)</a>
                <a href="/monitoring/health" target="_blank">Health Check</a>
            </div>
            
            <div class="content">
                <!-- Authentication -->
                <div class="section">
                    <h2>🔐 Authentication</h2>
                    <div class="endpoint-card">
                        <div class="endpoint-header">
                            <span class="method post">POST</span>
                            <span class="endpoint-path">/auth/register</span>
                        </div>
                        <div class="endpoint-description">
                            Register a new user account with email verification
                        </div>
                        <span class="auth-badge public">Public</span>
                    </div>
                    
                    <div class="endpoint-card">
                        <div class="endpoint-header">
                            <span class="method post">POST</span>
                            <span class="endpoint-path">/auth/login</span>
                        </div>
                        <div class="endpoint-description">
                            Login with email and password to receive JWT token
                        </div>
                        <span class="auth-badge public">Public</span>
                    </div>
                    
                    <div class="endpoint-card">
                        <div class="endpoint-header">
                            <span class="method post">POST</span>
                            <span class="endpoint-path">/auth/refresh</span>
                        </div>
                        <div class="endpoint-description">
                            Refresh access token using refresh token
                        </div>
                        <span class="auth-badge public">Public</span>
                    </div>
                </div>
                
                <!-- Members -->
                <div class="section">
                    <h2>👥 Members Management</h2>
                    <div class="endpoint-card">
                        <div class="endpoint-header">
                            <span class="method get">GET</span>
                            <span class="endpoint-path">/members</span>
                        </div>
                        <div class="endpoint-description">
                            List all members with pagination and filtering options
                        </div>
                        <span class="auth-badge">Requires Auth</span>
                    </div>
                    
                    <div class="endpoint-card">
                        <div class="endpoint-header">
                            <span class="method post">POST</span>
                            <span class="endpoint-path">/members</span>
                        </div>
                        <div class="endpoint-description">
                            Create a new member profile with contact information
                        </div>
                        <span class="auth-badge">Requires Auth</span>
                    </div>
                    
                    <div class="endpoint-card">
                        <div class="endpoint-header">
                            <span class="method get">GET</span>
                            <span class="endpoint-path">/members/{id}</span>
                        </div>
                        <div class="endpoint-description">
                            Get detailed information about a specific member
                        </div>
                        <span class="auth-badge">Requires Auth</span>
                    </div>
                    
                    <div class="endpoint-card">
                        <div class="endpoint-header">
                            <span class="method patch">PATCH</span>
                            <span class="endpoint-path">/members/{id}</span>
                        </div>
                        <div class="endpoint-description">
                            Update member information and preferences
                        </div>
                        <span class="auth-badge">Requires Auth</span>
                    </div>
                    
                    <div class="endpoint-card">
                        <div class="endpoint-header">
                            <span class="method delete">DELETE</span>
                            <span class="endpoint-path">/members/{id}</span>
                        </div>
                        <div class="endpoint-description">
                            Delete a member from the system
                        </div>
                        <span class="auth-badge">Requires Auth</span>
                    </div>
                </div>
                
                <!-- Messages -->
                <div class="section">
                    <h2>📧 Messaging</h2>
                    <div class="endpoint-card">
                        <div class="endpoint-header">
                            <span class="method post">POST</span>
                            <span class="endpoint-path">/messages/send</span>
                        </div>
                        <div class="endpoint-description">
                            Send email, SMS, or voice messages to members
                        </div>
                        <span class="auth-badge">Requires Auth</span>
                    </div>
                    
                    <div class="endpoint-card">
                        <div class="endpoint-header">
                            <span class="method get">GET</span>
                            <span class="endpoint-path">/messages</span>
                        </div>
                        <div class="endpoint-description">
                            List message history with filtering by status and type
                        </div>
                        <span class="auth-badge">Requires Auth</span>
                    </div>
                    
                    <div class="endpoint-card">
                        <div class="endpoint-header">
                            <span class="method get">GET</span>
                            <span class="endpoint-path">/messages/{id}</span>
                        </div>
                        <div class="endpoint-description">
                            Get details of a specific message including delivery status
                        </div>
                        <span class="auth-badge">Requires Auth</span>
                    </div>
                </div>
                
                <!-- Templates -->
                <div class="section">
                    <h2>📝 Message Templates</h2>
                    <div class="endpoint-card">
                        <div class="endpoint-header">
                            <span class="method get">GET</span>
                            <span class="endpoint-path">/templates</span>
                        </div>
                        <div class="endpoint-description">
                            List all message templates for emails, SMS, and voice
                        </div>
                        <span class="auth-badge">Requires Auth</span>
                    </div>
                    
                    <div class="endpoint-card">
                        <div class="endpoint-header">
                            <span class="method post">POST</span>
                            <span class="endpoint-path">/templates</span>
                        </div>
                        <div class="endpoint-description">
                            Create a new message template with variables
                        </div>
                        <span class="auth-badge">Requires Auth</span>
                    </div>
                    
                    <div class="endpoint-card">
                        <div class="endpoint-header">
                            <span class="method patch">PATCH</span>
                            <span class="endpoint-path">/templates/{id}</span>
                        </div>
                        <div class="endpoint-description">
                            Update an existing template
                        </div>
                        <span class="auth-badge">Requires Auth</span>
                    </div>
                </div>
                
                <!-- Automation -->
                <div class="section">
                    <h2>⚙️ Automation</h2>
                    <div class="endpoint-card">
                        <div class="endpoint-header">
                            <span class="method get">GET</span>
                            <span class="endpoint-path">/automation/rules</span>
                        </div>
                        <div class="endpoint-description">
                            List all automation rules and their status
                        </div>
                        <span class="auth-badge">Requires Auth</span>
                    </div>
                    
                    <div class="endpoint-card">
                        <div class="endpoint-header">
                            <span class="method post">POST</span>
                            <span class="endpoint-path">/automation/rules</span>
                        </div>
                        <div class="endpoint-description">
                            Create automated message rules based on triggers
                        </div>
                        <span class="auth-badge">Requires Auth</span>
                    </div>
                </div>
                
                <!-- Analytics -->
                <div class="section">
                    <h2>📊 Analytics</h2>
                    <div class="endpoint-card">
                        <div class="endpoint-header">
                            <span class="method get">GET</span>
                            <span class="endpoint-path">/analytics/overview</span>
                        </div>
                        <div class="endpoint-description">
                            Get overview of member counts, message statistics, and trends
                        </div>
                        <span class="auth-badge">Requires Auth</span>
                    </div>
                    
                    <div class="endpoint-card">
                        <div class="endpoint-header">
                            <span class="method get">GET</span>
                            <span class="endpoint-path">/analytics/messages</span>
                        </div>
                        <div class="endpoint-description">
                            Detailed message delivery analytics and engagement metrics
                        </div>
                        <span class="auth-badge">Requires Auth</span>
                    </div>
                </div>
                
                <!-- Settings -->
                <div class="section">
                    <h2>⚙️ Settings</h2>
                    <div class="endpoint-card">
                        <div class="endpoint-header">
                            <span class="method get">GET</span>
                            <span class="endpoint-path">/settings/sender</span>
                        </div>
                        <div class="endpoint-description">
                            Get sender settings for email and SMS
                        </div>
                        <span class="auth-badge">Requires Auth</span>
                    </div>
                    
                    <div class="endpoint-card">
                        <div class="endpoint-header">
                            <span class="method post">POST</span>
                            <span class="endpoint-path">/settings/sender</span>
                        </div>
                        <div class="endpoint-description">
                            Configure sender information and preferences
                        </div>
                        <span class="auth-badge">Requires Auth</span>
                    </div>
                </div>
                
                <!-- Monitoring -->
                <div class="section">
                    <h2>🔍 Monitoring & Health</h2>
                    <div class="endpoint-card">
                        <div class="endpoint-header">
                            <span class="method get">GET</span>
                            <span class="endpoint-path">/monitoring/health</span>
                        </div>
                        <div class="endpoint-description">
                            Check API health status and uptime
                        </div>
                        <span class="auth-badge public">Public</span>
                    </div>
                    
                    <div class="endpoint-card">
                        <div class="endpoint-header">
                            <span class="method get">GET</span>
                            <span class="endpoint-path">/monitoring/stats</span>
                        </div>
                        <div class="endpoint-description">
                            Get email statistics: sent, failed, success rate
                        </div>
                        <span class="auth-badge">Requires Auth</span>
                    </div>
                    
                    <div class="endpoint-card">
                        <div class="endpoint-header">
                            <span class="method get">GET</span>
                            <span class="endpoint-path">/monitoring/recent</span>
                        </div>
                        <div class="endpoint-description">
                            View recent messages with status and timestamps
                        </div>
                        <span class="auth-badge">Requires Auth</span>
                    </div>
                    
                    <div class="endpoint-card">
                        <div class="endpoint-header">
                            <span class="method get">GET</span>
                            <span class="endpoint-path">/monitoring/dashboard</span>
                        </div>
                        <div class="endpoint-description">
                            This page - Visual overview of all API endpoints
                        </div>
                        <span class="auth-badge public">Public</span>
                    </div>
                </div>
            </div>
            
            <div class="footer">
                <p>CareSphere API v1.0.0</p>
                <p>For technical support or questions, please refer to the <a href="/docs">API documentation</a></p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content
