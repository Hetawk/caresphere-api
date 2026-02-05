"""HTML templates for dashboard and monitoring pages."""

from datetime import datetime
from typing import Dict, Any


def get_dashboard_html() -> str:
    """Generate the main dashboard HTML with sidebar navigation."""
    current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>CareSphere API Dashboard</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: #F7F6F4;
                min-height: 100vh;
            }}
            .dashboard {{
                display: flex;
                min-height: 100vh;
            }}
            .sidebar {{
                width: 250px;
                background: linear-gradient(135deg, #E8C589 0%, #D4AF6A 50%, #C8A061 100%);
                color: #14120F;
                padding: 20px;
                position: fixed;
                height: 100vh;
                overflow-y: auto;
                box-shadow: 2px 0 12px rgba(200, 160, 97, 0.15);
            }}
            .sidebar h1 {{
                font-size: 1.5em;
                margin-bottom: 30px;
                padding-bottom: 15px;
                border-bottom: 2px solid rgba(20, 18, 15, 0.2);
                font-weight: 700;
                color: #14120F;
            }}
            .nav-section {{
                margin-bottom: 25px;
            }}
            .nav-section h3 {{
                font-size: 0.9em;
                text-transform: uppercase;
                opacity: 0.75;
                margin-bottom: 10px;
                letter-spacing: 1px;
                color: #14120F;
                font-weight: 600;
            }}
            .nav-link {{
                display: block;
                color: #14120F;
                text-decoration: none;
                padding: 10px 15px;
                border-radius: 6px;
                margin-bottom: 5px;
                transition: all 0.3s;
                font-weight: 500;
            }}
            .nav-link:hover {{
                background: rgba(20, 18, 15, 0.15);
                transform: translateX(5px);
            }}
            .nav-link.active {{
                background: rgba(20, 18, 15, 0.2);
                font-weight: 600;
            }}
            .main-content {{
                margin-left: 250px;
                flex: 1;
                padding: 30px;
            }}
            .header {{
                background: white;
                padding: 30px;
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                margin-bottom: 30px;
            }}
            .header h2 {{
                color: #333;
                font-size: 2em;
                margin-bottom: 10px;
            }}
            .status-badge {{
                display: inline-block;
                padding: 6px 12px;
                background: linear-gradient(135deg, #C8A061 0%, #D4AF6A 100%);
                color: #14120F;
                border-radius: 20px;
                font-weight: bold;
                font-size: 0.9em;
                box-shadow: 0 2px 4px rgba(200, 160, 97, 0.3);
            }}
            .section {{
                background: white;
                padding: 25px;
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }}
            .section h3 {{
                color: #C8A061;
                font-size: 1.4em;
                margin-bottom: 15px;
                padding-bottom: 10px;
                border-bottom: 2px solid #E8C589;
                font-weight: 600;
            }}
            .endpoint-card {{
                background: #F7F6F4;
                border-left: 4px solid #C8A061;
                padding: 15px;
                margin-bottom: 12px;
                border-radius: 6px;
                transition: all 0.3s;
                border: 1px solid #E8C589;
            }}
            .endpoint-card:hover {{
                box-shadow: 0 4px 12px rgba(200, 160, 97, 0.2);
                transform: translateX(5px);
                border-left-width: 6px;
            }}
            .method {{
                display: inline-block;
                padding: 4px 10px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 0.8em;
                margin-right: 10px;
                min-width: 55px;
                text-align: center;
            }}
            .method.get {{ background: #28a745; color: white; }}
            .method.post {{ background: #007bff; color: white; }}
            .method.patch {{ background: #17a2b8; color: white; }}
            .method.delete {{ background: #dc3545; color: white; }}
            .endpoint-path {{
                font-family: 'Courier New', monospace;
                color: #495057;
                font-weight: 600;
            }}
            .endpoint-desc {{
                color: #6c757d;
                margin-top: 8px;
                font-size: 0.95em;
            }}
            .auth-badge {{
                display: inline-block;
                padding: 3px 8px;
                background: #dc3545;
                color: white;
                border-radius: 4px;
                font-size: 0.75em;
                margin-top: 5px;
            }}
            .auth-badge.public {{
                background: #28a745;
            }}
            @media (max-width: 768px) {{
                .sidebar {{
                    width: 100%;
                    height: auto;
                    position: relative;
                }}
                .main-content {{
                    margin-left: 0;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="dashboard">
            <aside class="sidebar">
                <h1>🏥 CareSphere</h1>
                
                <div class="nav-section">
                    <h3>Main</h3>
                    <a href="/dashboard" class="nav-link active">📊 Dashboard</a>
                    <a href="/docs" class="nav-link">📚 API Docs</a>
                    <a href="/redoc" class="nav-link">📖 ReDoc</a>
                </div>
                
                <div class="nav-section">
                    <h3>Monitoring</h3>
                    <a href="/monitoring/health" class="nav-link">❤️ Health Check</a>
                    <a href="/monitoring/stats" class="nav-link">📊 Statistics</a>
                    <a href="/monitoring/recent" class="nav-link">📧 Recent Messages</a>
                </div>
                
                <div class="nav-section">
                    <h3>Resources</h3>
                    <a href="/auth/register" class="nav-link">🔐 Register</a>
                    <a href="/auth/login" class="nav-link">🔑 Login</a>
                </div>
            </aside>
            
            <main class="main-content">
                <div class="header">
                    <h2>API Dashboard</h2>
                    <p>
                        <span class="status-badge">✓ ONLINE</span>
                        <span style="margin-left: 15px; color: #6c757d;">
                            Version 1.0.0 • {current_time}
                        </span>
                    </p>
                </div>
                
                <div class="section">
                    <h3>🔐 Authentication</h3>
                    {_get_endpoints_html([
        ("POST", "/auth/register", "Register a new user account", "public"),
        ("POST", "/auth/login",
         "Login with credentials to get JWT token", "public"),
        ("POST", "/auth/refresh", "Refresh access token", "public"),
    ])}
                </div>
                
                <div class="section">
                    <h3>👥 Members Management</h3>
                    {_get_endpoints_html([
        ("GET", "/members", "List all members with pagination", "auth"),
        ("POST", "/members", "Create a new member profile", "auth"),
        ("GET", "/members/{{id}}",
         "Get member details by ID", "auth"),
        ("PATCH", "/members/{{id}}",
         "Update member information", "auth"),
        ("DELETE", "/members/{{id}}",
         "Delete a member", "auth"),
    ])}
                </div>
                
                <div class="section">
                    <h3>📧 Messaging</h3>
                    {_get_endpoints_html([
        ("POST", "/messages/send",
         "Send email, SMS, or voice messages", "auth"),
        ("GET", "/messages",
         "List message history with filters", "auth"),
        ("GET", "/messages/{{id}}",
         "Get message details and status", "auth"),
    ])}
                </div>
                
                <div class="section">
                    <h3>📝 Templates</h3>
                    {_get_endpoints_html([
        ("GET", "/templates", "List all message templates", "auth"),
        ("POST", "/templates", "Create new message template", "auth"),
        ("PATCH", "/templates/{{id}}",
         "Update existing template", "auth"),
    ])}
                </div>
                
                <div class="section">
                    <h3>⚙️ Automation</h3>
                    {_get_endpoints_html([
        ("GET", "/automation/rules",
                     "List automation rules", "auth"),
        ("POST", "/automation/rules",
         "Create automation rule", "auth"),
    ])}
                </div>
                
                <div class="section">
                    <h3>📊 Analytics</h3>
                    {_get_endpoints_html([
        ("GET", "/analytics/overview",
                     "Get member and message statistics", "auth"),
        ("GET", "/analytics/messages",
         "Detailed message analytics", "auth"),
    ])}
                </div>
                
                <div class="section">
                    <h3>⚙️ Settings</h3>
                    {_get_endpoints_html([
        ("GET", "/settings/sender", "Get sender settings", "auth"),
        ("POST", "/settings/sender",
         "Configure sender information", "auth"),
    ])}
                </div>
                
                <div class="section">
                    <h3>🔍 Monitoring</h3>
                    {_get_endpoints_html([
        ("GET", "/monitoring/health",
                     "API health check", "public"),
        ("GET", "/monitoring/stats", "Email statistics", "auth"),
        ("GET", "/monitoring/recent",
         "Recent messages list", "auth"),
    ])}
                </div>
            </main>
        </div>
    </body>
    </html>
    """


def _get_endpoints_html(endpoints: list) -> str:
    """Generate HTML for a list of endpoints."""
    html = ""
    for method, path, description, auth_type in endpoints:
        auth_class = "public" if auth_type == "public" else ""
        auth_text = "Public" if auth_type == "public" else "Requires Auth"

        html += f"""
        <div class="endpoint-card">
            <div>
                <span class="method {method.lower()}">{method}</span>
                <span class="endpoint-path">{path}</span>
            </div>
            <div class="endpoint-desc">{description}</div>
            <span class="auth-badge {auth_class}">{auth_text}</span>
        </div>
        """
    return html


def get_health_check_response(version: str = "1.0.0") -> Dict[str, Any]:
    """Generate health check response."""
    return {
        "success": True,
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": version
    }
