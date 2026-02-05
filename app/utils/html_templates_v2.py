"""Enhanced HTML templates with user management functionality."""

from datetime import datetime
from typing import Dict, Any


def get_dashboard_html() -> str:
    """Generate the main dashboard HTML with user management."""
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
                cursor: pointer;
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
                display: none;
            }}
            .section.active {{
                display: block;
            }}
            .section h3 {{
                color: #C8A061;
                font-size: 1.4em;
                margin-bottom: 15px;
                padding-bottom: 10px;
                border-bottom: 2px solid #E8C589;
                font-weight: 600;
            }}
            .btn {{
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s;
                font-size: 0.95em;
            }}
            .btn-primary {{
                background: linear-gradient(135deg, #C8A061 0%, #D4AF6A 100%);
                color: #14120F;
            }}
            .btn-primary:hover {{
                box-shadow: 0 4px 12px rgba(200, 160, 97, 0.4);
                transform: translateY(-2px);
            }}
            .btn-danger {{
                background: #dc3545;
                color: white;
            }}
            .btn-danger:hover {{
                background: #c82333;
            }}
            .btn-secondary {{
                background: #6c757d;
                color: white;
            }}
            .btn-secondary:hover {{
                background: #5a6268;
            }}
            .table-container {{
                overflow-x: auto;
                margin-top: 20px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
            }}
            th, td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #E8C589;
            }}
            th {{
                background: #F7F6F4;
                font-weight: 600;
                color: #C8A061;
            }}
            tr:hover {{
                background: #F7F6F4;
            }}
            .role-badge {{
                display: inline-block;
                padding: 4px 10px;
                border-radius: 12px;
                font-size: 0.85em;
                font-weight: 600;
            }}
            .role-super_admin {{ background: #dc3545; color: white; }}
            .role-admin {{ background: #ffc107; color: #14120F; }}
            .role-ministry_leader {{ background: #007bff; color: white; }}
            .role-volunteer {{ background: #28a745; color: white; }}
            .role-member {{ background: #6c757d; color: white; }}
            .status-badge-inline {{
                display: inline-block;
                padding: 4px 10px;
                border-radius: 12px;
                font-size: 0.85em;
                font-weight: 600;
            }}
            .status-active {{ background: #28a745; color: white; }}
            .status-inactive {{ background: #ffc107; color: #14120F; }}
            .status-suspended {{ background: #dc3545; color: white; }}
            .modal {{
                display: none;
                position: fixed;
                z-index: 1000;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.5);
                align-items: center;
                justify-content: center;
            }}
            .modal.active {{
                display: flex;
            }}
            .modal-content {{
                background: white;
                padding: 30px;
                border-radius: 12px;
                max-width: 500px;
                width: 90%;
                max-height: 90vh;
                overflow-y: auto;
            }}
            .modal-content h3 {{
                color: #C8A061;
                margin-bottom: 20px;
            }}
            .form-group {{
                margin-bottom: 20px;
            }}
            .form-group label {{
                display: block;
                margin-bottom: 5px;
                font-weight: 600;
                color: #333;
            }}
            .form-group input, .form-group select {{
                width: 100%;
                padding: 10px;
                border: 1px solid #E8C589;
                border-radius: 6px;
                font-size: 1em;
            }}
            .form-group input:focus, .form-group select:focus {{
                outline: none;
                border-color: #C8A061;
                box-shadow: 0 0 0 3px rgba(200, 160, 97, 0.1);
            }}
            .action-buttons {{
                display: flex;
                gap: 10px;
                margin-top: 20px;
            }}
            .toast {{
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 15px 20px;
                border-radius: 6px;
                color: white;
                font-weight: 600;
                z-index: 2000;
                animation: slideIn 0.3s ease-out;
                display: none;
                max-width: 400px;
                word-wrap: break-word;
            }}
            .toast.success {{ background: #28a745; }}
            .toast.error {{ background: #dc3545; }}
            .toast.active {{ display: block; }}
            @keyframes slideIn {{
                from {{ transform: translateX(400px); opacity: 0; }}
                to {{ transform: translateX(0); opacity: 1; }}
            }}
            .loading {{
                text-align: center;
                padding: 40px;
                color: #6c757d;
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
                    <a class="nav-link" onclick="showSection('dashboard')">📊 Dashboard</a>
                    <a class="nav-link active" onclick="showSection('users')">👤 User Management</a>
                    <a href="/docs" class="nav-link">📚 API Docs</a>
                    <a href="/redoc" class="nav-link">📖 ReDoc</a>
                </div>
                
                <div class="nav-section">
                    <h3>Monitoring</h3>
                    <a href="/monitoring/health" class="nav-link">❤️ Health Check</a>
                    <a href="/monitoring/stats" class="nav-link">📊 Statistics</a>
                    <a href="/monitoring/recent" class="nav-link">📧 Recent Messages</a>
                </div>
            </aside>
            
            <main class="main-content">
                <div class="header">
                    <h2>API Dashboard</h2>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <p style="margin: 0;">
                            <span class="status-badge">✓ ONLINE</span>
                            <span style="margin-left: 15px; color: #6c757d;">
                                Version 1.0.0 • {current_time}
                            </span>
                        </p>
                        <div id="auth-controls">
                            <div id="login-section" style="display: flex; gap: 10px;">
                                <input type="email" id="login-email" placeholder="Email" style="padding: 8px; border-radius: 6px; border: 1px solid #E8C589;">
                                <input type="password" id="login-password" placeholder="Password" style="padding: 8px; border-radius: 6px; border: 1px solid #E8C589;">
                                <button class="btn btn-primary" onclick="login()" style="padding: 8px 16px;">Login</button>
                            </div>
                            <div id="logged-in-section" style="display: none;">
                                <span id="user-email" style="color: #6c757d; margin-right: 10px;"></span>
                                <button class="btn btn-secondary" onclick="logout()" style="padding: 8px 16px;">Logout</button>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- User Management Section -->
                <div id="users-section" class="section active">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                        <h3>👤 User Management</h3>
                        <button class="btn btn-primary" onclick="showCreateModal()">+ Create User</button>
                    </div>
                    
                    <div class="table-container">
                        <div id="users-loading" class="loading">Loading users...</div>
                        <table id="users-table" style="display: none;">
                            <thead>
                                <tr>
                                    <th>Email</th>
                                    <th>Full Name</th>
                                    <th>Role</th>
                                    <th>Status</th>
                                    <th>Verified</th>
                                    <th>Created</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody id="users-tbody">
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Dashboard Section (hidden by default) -->
                <div id="dashboard-section" class="section">
                    <h3>📊 API Endpoints</h3>
                    <p style="color: #6c757d; margin-bottom: 20px;">
                        Browse available API endpoints. Full documentation available at 
                        <a href="/docs" style="color: #C8A061;">/docs</a>.
                    </p>
                </div>
            </main>
        </div>
        
        <!-- Create/Edit User Modal -->
        <div id="user-modal" class="modal">
            <div class="modal-content">
                <h3 id="modal-title">Create New User</h3>
                <form id="user-form" onsubmit="saveUser(event)">
                    <input type="hidden" id="user-id">
                    
                    <div class="form-group">
                        <label for="email">Email *</label>
                        <input type="email" id="email" required>
                    </div>
                    
                    <div class="form-group" id="password-group">
                        <label for="password">Password *</label>
                        <input type="password" id="password" minlength="8" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="fullName">Full Name *</label>
                        <input type="text" id="fullName" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="displayName">Display Name</label>
                        <input type="text" id="displayName">
                    </div>
                    
                    <div class="form-group">
                        <label for="avatarUrl">Avatar URL</label>
                        <input type="url" id="avatarUrl" placeholder="https://...">
                    </div>
                    
                    <div class="form-group" id="password-change-group">
                        <label for="newPassword">New Password (leave blank to keep current)</label>
                        <input type="password" id="newPassword" minlength="8">
                        <small style="color: #6c757d; font-size: 0.85em;">Minimum 8 characters</small>
                    </div>
                    
                    <div class="form-group">
                        <label for="role">Role *</label>
                        <select id="role" required>
                            <option value="super_admin">Super Admin</option>
                            <option value="admin" selected>Admin</option>
                            <option value="ministry_leader">Ministry Leader</option>
                            <option value="volunteer">Volunteer</option>
                            <option value="member">Member</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="status">Status *</label>
                        <select id="status" required>
                            <option value="active" selected>Active</option>
                            <option value="inactive">Inactive</option>
                            <option value="suspended">Suspended</option>
                        </select>
                    </div>
                    
                    <div class="form-group" id="email-verified-group" style="display: none;">
                        <label style="display: flex; align-items: center; cursor: pointer;">
                            <input type="checkbox" id="emailVerified" style="width: auto; margin-right: 10px;">
                            <span>Email Verified</span>
                        </label>
                        <small style="color: #6c757d; font-size: 0.85em;">Check if user's email is verified</small>
                    </div>
                    
                    <div class="action-buttons">
                        <button type="submit" class="btn btn-primary">Save User</button>
                        <button type="button" class="btn btn-secondary" onclick="closeModal()">Cancel</button>
                    </div>
                </form>
            </div>
        </div>
        
        <!-- Toast Notification -->
        <div id="toast" class="toast"></div>
        
        <script>
            let users = [];
            let editingUserId = null;
            let currentUserEmail = null;
            
            // Load users on page load
            window.onload = function() {{
                checkAuth();
                loadUsers();
            }};
            
            function checkAuth() {{
                const token = localStorage.getItem('token');
                const userEmail = localStorage.getItem('userEmail');
                
                if (token && userEmail) {{
                    currentUserEmail = userEmail;
                    document.getElementById('login-section').style.display = 'none';
                    document.getElementById('logged-in-section').style.display = 'block';
                    document.getElementById('user-email').textContent = userEmail;
                }} else {{
                    document.getElementById('login-section').style.display = 'flex';
                    document.getElementById('logged-in-section').style.display = 'none';
                }}
            }}
            
            async function login() {{
                const email = document.getElementById('login-email').value;
                const password = document.getElementById('login-password').value;
                
                if (!email || !password) {{
                    showToast('Please enter email and password', 'error');
                    return;
                }}
                
                try {{
                    const response = await fetch('/auth/login', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json'
                        }},
                        body: JSON.stringify({{ email, password }})
                    }});
                    
                    if (response.ok) {{
                        const result = await response.json();
                        const data = result.data;
                        localStorage.setItem('token', data.accessToken);
                        localStorage.setItem('userEmail', data.user.email);
                        currentUserEmail = data.user.email;
                        
                        showToast('Login successful!', 'success');
                        checkAuth();
                        loadUsers();
                    }} else {{
                        const error = await response.json();
                        showToast(`Login failed: ${{error.detail || error.message || 'Invalid credentials'}}`, 'error');
                    }}
                }} catch (error) {{
                    console.error('Login error:', error);
                    showToast('Login failed: ' + error.message, 'error');
                }}
            }}
            
            function logout() {{
                localStorage.removeItem('token');
                localStorage.removeItem('userEmail');
                currentUserEmail = null;
                checkAuth();
                showToast('Logged out successfully', 'success');
            }}
            
            function showSection(sectionName) {{
                // Update nav links
                document.querySelectorAll('.nav-link').forEach(link => {{
                    link.classList.remove('active');
                }});
                event.target.classList.add('active');
                
                // Show section
                document.querySelectorAll('.section').forEach(section => {{
                    section.classList.remove('active');
                }});
                document.getElementById(sectionName + '-section').classList.add('active');
            }}
            
            async function loadUsers() {{
                try {{
                    const token = localStorage.getItem('token');
                    
                    if (!token) {{
                        console.warn('No token available, showing login prompt');
                        document.getElementById('users-loading').textContent = 'Please login to view users';
                        document.getElementById('users-loading').style.display = 'block';
                        document.getElementById('users-table').style.display = 'none';
                        return;
                    }}
                    
                    const response = await fetch('/admin/users', {{
                        headers: {{
                            'Authorization': `Bearer ${{token}}`
                        }}
                    }});
                    
                    if (response.ok) {{
                        const result = await response.json();
                        console.log('API Response:', result);
                        
                        // Handle both formats: direct array or nested in data
                        if (result.data && result.data.users) {{
                            users = result.data.users;
                        }} else if (result.users) {{
                            users = result.users;
                        }} else if (Array.isArray(result.data)) {{
                            users = result.data;
                        }} else {{
                            console.error('Unexpected response format:', result);
                            users = [];
                        }}
                        
                        console.log('Loaded users:', users);
                        renderUsers();
                    }} else {{
                        const errorText = await response.text();
                        console.error('Failed to load users:', response.status, errorText);
                        document.getElementById('users-loading').textContent = `Failed to load users: ${{response.status}}. Please login again.`;
                        users = [];
                    }}
                }} catch (error) {{
                    console.error('Error loading users:', error);
                    document.getElementById('users-loading').textContent = 'Error loading users: ' + error.message;
                    users = [];
                }}
                
                document.getElementById('users-loading').style.display = users.length === 0 ? 'block' : 'none';
                document.getElementById('users-table').style.display = users.length > 0 ? 'table' : 'none';
            }}
            
            function renderUsers() {{
                const tbody = document.getElementById('users-tbody');
                tbody.innerHTML = '';
                
                users.forEach(user => {{
                    const row = document.createElement('tr');
                    const verifiedIcon = user.emailVerified || user.email_verified ? '✓' : '✗';
                    const verifiedColor = user.emailVerified || user.email_verified ? '#28a745' : '#dc3545';
                    row.innerHTML = `
                        <td>${{user.email}}</td>
                        <td>${{user.fullName || user.full_name || 'N/A'}}</td>
                        <td><span class="role-badge role-${{user.role}}">${{formatRole(user.role)}}</span></td>
                        <td><span class="status-badge-inline status-${{user.status}}">${{user.status}}</span></td>
                        <td><span style="color: ${{verifiedColor}}; font-weight: bold;">${{verifiedIcon}}</span></td>
                        <td>${{formatDate(user.createdAt || user.created_at)}}</td>
                        <td>
                            <button class="btn btn-secondary" style="padding: 5px 10px; font-size: 0.85em; margin-right: 5px;" onclick="editUser('${{user.id}}')">✏️ Edit</button>
                            <button class="btn btn-primary" style="padding: 5px 10px; font-size: 0.85em; margin-right: 5px;" onclick="resetPassword('${{user.id}}', '${{user.email}}')">🔑 Reset PWD</button>
                            <button class="btn btn-danger" style="padding: 5px 10px; font-size: 0.85em;" onclick="deleteUser('${{user.id}}', '${{user.email}}')">🗑️ Delete</button>
                        </td>
                    `;
                    tbody.appendChild(row);
                }});
            }}
            
            function formatRole(role) {{
                return role.replace(/_/g, ' ').replace(/\\b\\w/g, l => l.toUpperCase());
            }}
            
            function formatDate(dateString) {{
                if (!dateString) return 'N/A';
                const date = new Date(dateString);
                return date.toLocaleDateString('en-US', {{ year: 'numeric', month: 'short', day: 'numeric' }});
            }}
            
            function showCreateModal() {{
                editingUserId = null;
                document.getElementById('modal-title').textContent = 'Create New User';
                document.getElementById('user-form').reset();
                document.getElementById('user-id').value = '';
                document.getElementById('password-group').style.display = 'block';
                document.getElementById('password').required = true;
                document.getElementById('password-change-group').style.display = 'none';
                document.getElementById('email-verified-group').style.display = 'none';
                document.getElementById('user-modal').classList.add('active');
            }}
            
            function editUser(userId) {{
                const user = users.find(u => u.id === userId);
                if (!user) return;
                
                editingUserId = userId;
                document.getElementById('modal-title').textContent = 'Edit User';
                document.getElementById('user-id').value = user.id;
                document.getElementById('email').value = user.email;
                document.getElementById('fullName').value = user.fullName || user.full_name || '';
                document.getElementById('displayName').value = user.displayName || user.display_name || '';
                document.getElementById('avatarUrl').value = user.avatarUrl || user.avatar_url || '';
                document.getElementById('role').value = user.role;
                document.getElementById('status').value = user.status;
                document.getElementById('emailVerified').checked = user.emailVerified || user.email_verified || false;
                document.getElementById('password-group').style.display = 'none';
                document.getElementById('password').required = false;
                document.getElementById('password-change-group').style.display = 'block';
                document.getElementById('email-verified-group').style.display = 'block';
                
                document.getElementById('user-modal').classList.add('active');
            }}
            
            function closeModal() {{
                document.getElementById('user-modal').classList.remove('active');
                document.getElementById('user-form').reset();
                editingUserId = null;
            }}
            
            async function saveUser(event) {{
                event.preventDefault();
                
                const formData = {{
                    email: document.getElementById('email').value,
                    fullName: document.getElementById('fullName').value,
                    displayName: document.getElementById('displayName').value || null,
                    avatarUrl: document.getElementById('avatarUrl').value || null,
                    role: document.getElementById('role').value,
                    status: document.getElementById('status').value
                }};
                
                if (!editingUserId) {{
                    formData.password = document.getElementById('password').value;
                }} else {{
                    // Include password only if changed
                    const newPassword = document.getElementById('newPassword').value;
                    if (newPassword) {{
                        formData.password = newPassword;
                    }}
                    formData.emailVerified = document.getElementById('emailVerified').checked;
                }}
                
                console.log('Saving user with data:', formData);
                console.log('URL:', editingUserId ? `/admin/users/${{editingUserId}}` : '/auth/register');
                
                try {{
                    const url = editingUserId ? `/admin/users/${{editingUserId}}` : '/auth/register';
                    const method = editingUserId ? 'PATCH' : 'POST';
                    
                    const headers = {{
                        'Content-Type': 'application/json'
                    }};
                    
                    // Add auth token only for update operations
                    if (editingUserId) {{
                        const token = localStorage.getItem('token') || '';
                        if (token) {{
                            headers['Authorization'] = `Bearer ${{token}}`;
                        }}
                        console.log('Using token:', token ? 'Yes' : 'No');
                    }}
                    
                    const response = await fetch(url, {{
                        method,
                        headers,
                        body: JSON.stringify(formData)
                    }});
                    
                    console.log('Response status:', response.status);
                    
                    if (response.ok) {{
                        showToast(editingUserId ? 'User updated successfully!' : 'User created successfully!', 'success');
                        closeModal();
                        setTimeout(() => loadUsers(), 500);
                    }} else {{
                        const errorText = await response.text();
                        console.error('Error response:', errorText);
                        let errorMsg;
                        try {{
                            const error = JSON.parse(errorText);
                            errorMsg = error.detail || error.message || JSON.stringify(error);
                        }} catch {{
                            errorMsg = errorText || 'Unknown error';
                        }}
                        showToast(`Failed to save user: ${{errorMsg}}`, 'error');
                    }}
                }} catch (error) {{
                    console.error('Error saving user:', error);
                    showToast(`Failed to save user: ${{error.message}}`, 'error');
                }}
            }}
            
            async function resetPassword(userId, userEmail) {{
                const newPassword = prompt(`Enter new password for ${{userEmail}}:\\n(Minimum 8 characters)`);
                
                if (!newPassword) return;
                
                if (newPassword.length < 8) {{
                    showToast('Password must be at least 8 characters', 'error');
                    return;
                }}
                
                try {{
                    const response = await fetch(`/admin/users/${{userId}}`, {{
                        method: 'PATCH',
                        headers: {{
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${{localStorage.getItem('token') || ''}}`
                        }},
                        body: JSON.stringify({{ password: newPassword }})
                    }});
                    
                    if (response.ok) {{
                        showToast('Password reset successfully!', 'success');
                    }} else {{
                        showToast('Failed to reset password', 'error');
                    }}
                }} catch (error) {{
                    console.error('Error resetting password:', error);
                    showToast('Failed to reset password', 'error');
                }}
            }}
            
            async function deleteUser(userId, userEmail) {{
                if (!confirm(`Are you sure you want to delete user ${{userEmail}}?`)) {{
                    return;
                }}
                
                try {{
                    const response = await fetch(`/admin/users/${{userId}}`, {{
                        method: 'DELETE',
                        headers: {{
                            'Authorization': `Bearer ${{localStorage.getItem('token') || ''}}`
                        }}
                    }});
                    
                    if (response.ok) {{
                        showToast('User deleted successfully!', 'success');
                        setTimeout(() => loadUsers(), 500);
                    }} else {{
                        showToast('Failed to delete user', 'error');
                    }}
                }} catch (error) {{
                    console.error('Error deleting user:', error);
                    showToast('Failed to delete user', 'error');
                }}
            }}
            
            function showToast(message, type) {{
                const toast = document.getElementById('toast');
                toast.textContent = message;
                toast.className = `toast ${{type}} active`;
                
                setTimeout(() => {{
                    toast.classList.remove('active');
                }}, 5000);  // Show for 5 seconds to read error messages
            }}
        </script>
    </body>
    </html>
    """


def get_health_check_response(version: str = "1.0.0") -> Dict[str, Any]:
    """Generate health check response."""
    return {
        "success": True,
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": version
    }
