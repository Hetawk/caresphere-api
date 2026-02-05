# Organization Onboarding Enhancement

## Overview
Enhanced user registration and organization management flow allowing users to either create or join organizations during or after signup.

## User Flows

### Flow 1: Create Organization During Signup
1. User signs up with email/password
2. **Option presented**: "Create a new organization" or "Join existing organization" or "Skip for now"
3. If "Create new organization":
   - User provides organization name
   - System auto-generates unique 7-9 digit organization code
   - User becomes **Super Admin** of the organization
   - Organization is activated immediately

### Flow 2: Join Organization During Signup
1. User signs up with email/password
2. Selects "Join existing organization"
3. User enters 7-9 digit organization code
4. System validates code and links user to organization
5. User becomes **Member** of that organization (default role)
6. Organization owner/admin can later adjust their role

### Flow 3: Skip During Signup (Setup Later)
1. User signs up with email/password
2. Selects "Skip for now"
3. User account created without organization link
4. **In-app prompt**: User can create or join organization anytime from settings/profile
5. Until linked to organization, user has limited access

### Flow 4: Join Organization While In-App
1. User already registered but not linked to organization
2. Navigate to Settings → Organization
3. Options available:
   - "Create New Organization"
   - "Join Organization" (enter code)
4. Same flows as signup apply

## Technical Implementation

### Database Changes

#### Organizations Table
```sql
ALTER TABLE organizations 
ADD COLUMN organization_code VARCHAR(9) UNIQUE NOT NULL;

-- Index for fast lookups
CREATE INDEX idx_organization_code ON organizations(organization_code);
```

#### Organization Code Generator
- Format: 7-9 digit numeric code (e.g., `12345678` or `123456789`)
- Must be unique across all organizations
- Easy to type and share
- Auto-generated using secure random number generation

### API Endpoints

#### 1. POST /auth/register-with-organization
```json
{
  "email": "user@example.com",
  "password": "securePassword123",
  "firstName": "John",
  "lastName": "Doe",
  "organization": {
    "action": "create|join|skip",
    "name": "My Church",  // if action=create
    "code": "12345678"    // if action=join
  }
}
```

Response:
```json
{
  "success": true,
  "data": {
    "user": {...},
    "organization": {
      "id": "...",
      "name": "My Church",
      "code": "12345678",
      "role": "super_admin"  // or "member"
    },
    "token": "jwt_token_here"
  }
}
```

#### 2. POST /organizations/create
Create organization for existing user:
```json
{
  "name": "My Church",
  "slug": "my-church",
  "domain": "mychurch.com"  // optional
}
```

Response includes generated `organization_code`.

#### 3. POST /organizations/join
Join organization by code:
```json
{
  "code": "12345678"
}
```

#### 4. GET /organizations/my-organization
Get current user's organization details including the code (visible to admins only).

#### 5. POST /organizations/regenerate-code
Regenerate organization code (Super Admin only):
```json
{
  "reason": "Security - code was shared publicly"
}
```

### Security Considerations

1. **Code Visibility**
   - Organization code visible only to organization admins
   - Regular members cannot see the code
   - Prevents unauthorized sharing

2. **Code Regeneration**
   - Super Admin can regenerate code if compromised
   - Old code immediately invalidated
   - Audit log entry created

3. **Join Validation**
   - Verify organization is active (`is_active=true`)
   - Check if organization has reached member limit (if applicable)
   - Log all join attempts for security monitoring

4. **Rate Limiting**
   - Limit failed code entry attempts (5 per hour per IP)
   - Prevent brute force attacks on organization codes

### User Experience

#### Mobile App (Swift)
```swift
// Registration screen enhancement
struct RegistrationView: View {
    @State private var email = ""
    @State private var password = ""
    @State private var organizationOption: OrgOption = .skip
    @State private var organizationCode = ""
    @State private var organizationName = ""
    
    enum OrgOption {
        case create, join, skip
    }
    
    var body: some View {
        VStack {
            // ... email and password fields ...
            
            Picker("Organization", selection: $organizationOption) {
                Text("Skip for now").tag(OrgOption.skip)
                Text("Create organization").tag(OrgOption.create)
                Text("Join organization").tag(OrgOption.join)
            }
            
            if organizationOption == .create {
                TextField("Organization Name", text: $organizationName)
            } else if organizationOption == .join {
                TextField("Organization Code", text: $organizationCode)
                    .keyboardType(.numberPad)
            }
            
            Button("Sign Up") {
                registerWithOrganization()
            }
        }
    }
}
```

#### Web Dashboard
- Similar flow with clearer explanations
- Visual code display with copy button for admins
- QR code generation option (for easy mobile joining)

### Onboarding Experience

#### For Organization Creators
1. Welcome message: "You're now the administrator of [Organization Name]"
2. Quick setup wizard:
   - Invite team members
   - Customize organization settings
   - Set up roles and permissions
3. Display organization code prominently: "Share this code: **12345678**"

#### For Organization Joiners
1. Confirmation message: "You've joined [Organization Name]"
2. Pending approval state (optional feature):
   - Admin must approve new members
   - User has limited access until approved
3. Introduction to organization features

#### For Skip Users
1. Limited dashboard access
2. Prominent banner: "Complete your setup by creating or joining an organization"
3. CTA button always visible in navigation

## Migration Plan

### Phase 1: Database Schema
1. Add `organization_code` column to organizations table
2. Generate codes for existing organizations
3. Create audit log table for organization joins

### Phase 2: Backend API
1. Implement code generation utility
2. Create new registration endpoint
3. Update organization service with join/create methods
4. Add role assignment logic

### Phase 3: Frontend Integration
1. Update mobile app registration flow
2. Update web dashboard registration
3. Add organization management screen
4. Add code sharing features

### Phase 4: Testing & Rollout
1. Unit tests for code generation and validation
2. Integration tests for registration flows
3. Beta testing with select users
4. Gradual rollout with feature flag

## Benefits

1. **Simplified Onboarding**: Users can get started quickly
2. **Flexible**: Create or join - user chooses
3. **Secure**: Code-based joining with admin controls
4. **Scalable**: Easy for organizations to grow membership
5. **User-Friendly**: Simple numeric codes easy to share

## Future Enhancements

1. **Invitation Links**: Generate shareable links instead of just codes
2. **QR Codes**: Scan to join organizations
3. **Email Invitations**: Admin sends email invites with embedded codes
4. **Multi-Organization Support**: Users can belong to multiple organizations
5. **Organization Discovery**: Public directory of organizations (opt-in)

## Implementation Priority

**High Priority:**
- [x] Database schema for RBAC (completed)
- [ ] Organization code generation
- [ ] Enhanced registration endpoint
- [ ] Join organization endpoint

**Medium Priority:**
- [ ] Mobile app UI updates
- [ ] Web dashboard updates
- [ ] Admin code visibility controls

**Low Priority:**
- [ ] QR code generation
- [ ] Invitation links
- [ ] Multi-organization support

---

**Status**: Documented
**Date**: February 5, 2026
**Author**: EKD Digital Team
