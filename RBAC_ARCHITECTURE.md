# Role-Based Access Control (RBAC) Architecture

## Overview

CareSphere implements a flexible Role-Based Access Control (RBAC) system that supports:
- **Multi-tenancy**: Multiple organizations (churches, mosques, nonprofits)
- **Custom Roles**: Super admins can create organization-specific roles
- **Granular Permissions**: Fine-grained access control
- **User Invitations**: Email-based user onboarding
- **Flexible Role Management**: Create, edit, delete roles and assign permissions

## Database Schema

### Core Tables

#### `organizations`
- Primary tenant/organization entity
- Each organization is isolated (data segregation)
- Contains name, slug, domain, settings

#### `users`
- Global user accounts
- Can belong to multiple organizations
- Has legacy `organization_id` for backward compatibility

#### `permissions`
- Granular access rights (e.g., "manage_members", "send_messages")
- System permissions cannot be deleted
- Grouped by category (members, messages, automation, etc.)

#### `roles`
- Organization-specific roles
- Links to multiple permissions via `role_permissions`
- System roles (super_admin, admin, etc.) cannot be deleted
- Custom roles can be created/modified by super admins

#### `organization_users` (Many-to-Many)
- Links users to organizations with specific roles
- Supports:
  - `is_owner`: Organization creator/owner
  - `is_active`: Active membership status
  - `invited_by`: Who invited this user
  - `joined_at`: When user accepted invitation

#### `user_invitations`
- Pending invitations to join organizations
- Contains:
  - Email, role assignment
  - Invitation token and expiry
  - Custom invitation message
  - Acceptance tracking

### Permission Categories

1. **Members**
   - view_members, manage_members
   - import_members, export_members

2. **Messages**
   - view_messages, send_messages
   - manage_templates, delete_messages

3. **Automation**
   - view_automation, manage_automation
   - execute_automation

4. **Analytics**
   - view_analytics, export_reports

5. **Organization**
   - manage_organization, invite_users
   - manage_users, remove_users

6. **Roles**
   - view_roles, manage_roles
   - assign_roles

7. **Settings**
   - view_settings, manage_settings
   - manage_integrations

## System Roles

### Super Admin
- **Color**: Red (#DC2626)
- **Permissions**: ALL
- **Capabilities**:
  - Full access to everything
  - Create/edit/delete custom roles
  - Invite users with any role
  - Manage organization settings
  - Cannot be deleted (system role)

### Administrator
- **Color**: Orange (#EA580C)
- **Permissions**: Most permissions except role management
- **Capabilities**:
  - Manage members, messages, automation
  - View analytics and reports
  - Assign roles (but not create/edit roles)
  - Cannot manage organization settings

### Ministry Leader
- **Color**: Cyan (#0891B2)
- **Permissions**: Member management, messaging
- **Capabilities**:
  - Manage members within ministry
  - Send messages and create templates
  - View analytics
  - Cannot manage automation or organization

### Volunteer
- **Color**: Green (#059669)
- **Permissions**: View members, send messages
- **Capabilities**:
  - View member list
  - Send messages
  - View analytics
  - Cannot modify members or create templates

### Member
- **Color**: Gray (#6B7280)
- **Permissions**: View-only access
- **Capabilities**:
  - View members
  - View messages
  - No modification rights

## Workflows

### 1. Organization Creation
```
1. User registers → Creates account
2. Super admin creates organization → Becomes owner
3. System creates default roles for organization
4. Owner is assigned super_admin role
```

### 2. User Invitation
```
1. Super admin enters email + assigns role
2. System creates invitation with token
3. Email sent with invitation link
4. User clicks link → Accepts invitation
5. OrganizationUser record created
6. User gains access to organization
```

### 3. Custom Role Creation
```
1. Super admin navigates to Roles
2. Creates new role (e.g., "Youth Leader")
3. Selects permissions from available list
4. Saves role with custom name, description, color
5. Role available for assignment to users
```

### 4. Role Assignment
```
1. Admin views organization users
2. Selects user → Changes role
3. User's OrganizationUser.role_id updated
4. Permissions immediately reflect in user's access
```

### 5. Member Import
```
1. Admin uploads CSV file
2. System validates CSV format
3. Members created with organization_id
4. Only users with same organization_id can view
```

## API Endpoints (To Be Created)

### Organizations
- `POST /organizations` - Create organization
- `GET /organizations/{id}` - Get organization details
- `PATCH /organizations/{id}` - Update organization
- `DELETE /organizations/{id}` - Delete organization

### Roles
- `GET /organizations/{org_id}/roles` - List org roles
- `POST /organizations/{org_id}/roles` - Create custom role
- `PATCH /roles/{id}` - Update role
- `DELETE /roles/{id}` - Delete role (custom only)

### Permissions
- `GET /permissions` - List all permissions
- `GET /permissions/categories` - List by category

### User Invitations
- `POST /organizations/{org_id}/invitations` - Invite user
- `GET /organizations/{org_id}/invitations` - List pending invitations
- `POST /invitations/{token}/accept` - Accept invitation
- `DELETE /invitations/{id}` - Cancel invitation

### Organization Users
- `GET /organizations/{org_id}/users` - List org users
- `PATCH /organizations/{org_id}/users/{user_id}` - Update user role
- `DELETE /organizations/{org_id}/users/{user_id}` - Remove user

## Security Considerations

1. **Data Isolation**
   - All queries must filter by `organization_id`
   - Users can only access data from their organizations

2. **Permission Checks**
   - Every endpoint must verify user permissions
   - Use decorators/dependencies for permission enforcement

3. **Role Hierarchy**
   - Super admin can do anything
   - System roles cannot be deleted
   - Custom roles inherit from permission grants

4. **Invitation Security**
   - Tokens expire after 7 days
   - One-time use tokens
   - Email verification required

## Migration Plan

1. **Run RBAC Migration**
   ```bash
   alembic upgrade head
   ```

2. **Seed Permissions**
   ```bash
   python scripts/seed_rbac_permissions.py
   ```

3. **Setup JICF Organization**
   ```bash
   python scripts/setup_jicf_complete.py
   ```

4. **Update API Endpoints**
   - Add organization management
   - Add role management
   - Add invitation system
   - Update all queries to filter by organization

5. **Update Frontend**
   - Add organization selector
   - Add role management UI
   - Add user invitation flow
   - Add custom role creation

## Benefits

✅ **Flexible**: Create unlimited custom roles per organization
✅ **Scalable**: Supports multiple organizations on same platform
✅ **Secure**: Granular permissions with data isolation
✅ **User-friendly**: Email-based invitations with role assignment
✅ **Extensible**: Easy to add new permissions/categories

## Example Use Cases

### Church Organization (JICF)
- Roles: Pastor, Elder, Deacon, Youth Leader, Member
- Permissions: Manage members, send announcements, view reports

### Nonprofit Organization
- Roles: Executive Director, Program Manager, Volunteer Coordinator
- Permissions: Manage beneficiaries, track donations, send communications

### Mosque Community
- Roles: Imam, Board Member, Committee Leader, Community Member
- Permissions: Manage community, schedule events, send notifications
