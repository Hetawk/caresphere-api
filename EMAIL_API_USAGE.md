# EKDSend Transactional Email API - Complete Usage Guide

> Professional transactional email delivery via REST API with SMTP relay, rate limiting, templates, and real-time tracking.

This guide covers **transactional email** functionality in EKDSend. For SMS and Voice, see the respective documentation sections.

---

## 1. Quick Start

**Base URL**

```text
https://es.ekddigital.com/api/v1
```

**Authentication:** Bearer token (API Key)

```bash
curl -X POST https://es.ekddigital.com/api/v1/send \
  -H "Authorization: Bearer ek_live_your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "email",
    "to": "recipient@example.com",
    "subject": "Hello from EKDSend",
    "body": "<h1>Welcome!</h1><p>This is a test email sent via the EKDSend API.</p>"
  }'
```

On success, the API responds with:

```json
{
  "success": true,
  "messageId": "clxyz123abc456",
  "type": "email",
  "queuedAt": "2026-01-02T14:30:00.000Z"
}
```

### Alternative Endpoint

You can also use the dedicated `/emails` endpoint:

```bash
curl -X POST https://es.ekddigital.com/api/v1/emails \
  -H "Authorization: Bearer ek_live_your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "recipient@example.com",
    "subject": "Hello from EKDSend",
    "html": "<h1>Welcome!</h1><p>Thanks for signing up.</p>",
    "text": "Welcome! Thanks for signing up."
  }'
```

Response:

```json
{
  "id": "clxyz123abc456",
  "status": "QUEUED",
  "from": "noreply@mail.ekdsend.com",
  "to": ["recipient@example.com"],
  "subject": "Hello from EKDSend",
  "createdAt": "2026-01-02T14:30:00.000Z",
  "sandbox": false
}
```

---

## 2. Authentication & API Keys

Every request must include a valid API key with the appropriate scopes.

**Header format:**

```http
Authorization: Bearer ek_live_your_api_key_here
```

### 2.1 Creating API Keys

```bash
curl -X POST https://es.ekddigital.com/api/v1/api-keys \
  -H "Authorization: Bearer your_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Production Email Key",
    "scopes": ["send:email"],
    "expiresInDays": 365
  }'
```

**Response:**

```json
{
  "message": "API key created successfully",
  "apiKey": {
    "id": "key_abc123",
    "name": "Production Email Key",
    "keyPrefix": "ek_live",
    "key": "ek_live_abc123xyz789...",
    "scopes": ["send:email"],
    "createdAt": "2026-01-02T10:00:00.000Z",
    "expiresAt": "2027-01-02T10:00:00.000Z"
  },
  "warning": "⚠️ Save this key securely. It will not be shown again for security reasons."
}
```

### 2.2 Required Scopes for Transactional Email

| Feature              | Scope          | Description                |
| -------------------- | -------------- | -------------------------- |
| Send Email           | `send:email`   | Send transactional emails  |
| List/Search Messages | `admin:view`   | View email history & stats |
| Manage Domains       | `admin:manage` | Add/verify sending domains |
| Manage Webhooks      | `admin:manage` | Configure event webhooks   |

### 2.3 List API Keys

```bash
curl -X GET https://es.ekddigital.com/api/v1/api-keys \
  -H "Authorization: Bearer your_jwt_token"
```

### 2.4 Revoke API Key

```bash
curl -X DELETE https://es.ekddigital.com/api/v1/api-keys/key_abc123 \
  -H "Authorization: Bearer your_jwt_token"
```

If the scope for sending email is missing, the API returns `403 FORBIDDEN`.

> The authentication logic lives in `src/lib/auth/middleware.ts` and `src/lib/auth/apiKey.ts`.

---

## 3. Sending Transactional Emails

### 3.1 Using the Unified `/send` Endpoint

**Endpoint:**

```http
POST /api/v1/send
```

This endpoint supports email, SMS, and voice. For transactional email, use `type: "email"`.

### 3.2 Request Schema (TypeScript)

```ts
interface SendEmailRequest {
  type: "email";
  to: string | string[]; // Up to 50 recipients
  from?: string; // Defaults to ES_DEFAULT_FROM
  subject: string; // Required, max 998 chars
  body?: string; // HTML or text body
  template?: string; // Built-in template key
  templateData?: Record<string, unknown>;
  cc?: string[]; // Max 50 addresses
  bcc?: string[]; // Max 50 addresses
  replyTo?: string;
}
```

### 3.3 Using the `/emails` Endpoint (Full Featured)

**Endpoint:**

```http
POST /api/v1/emails
```

This endpoint provides more features including attachments and scheduling:

```ts
interface SendEmailSchemaRequest {
  to: string | string[]; // Up to 50 recipients
  from?: string; // Optional sender address
  subject: string; // Required, max 998 chars
  html?: string; // HTML body (max 5MB)
  text?: string; // Plain text body (max 1MB)
  template?: string; // Template ID (max 100 chars)
  data?: Record<string, unknown>; // Template variables
  cc?: string[]; // Max 50 addresses
  bcc?: string[]; // Max 50 addresses
  replyTo?: string;
  attachments?: EmailAttachment[]; // Max 10 attachments
  headers?: Record<string, string>; // Custom headers
  tags?: string[]; // Max 10 tags for tracking
  scheduledAt?: Date; // Schedule for later
  idempotencyKey?: string; // Prevent duplicates
}

interface EmailAttachment {
  filename: string; // Required, max 255 chars
  content: string; // Base64 encoded content
  contentType?: string; // MIME type, defaults to application/octet-stream
}
```

### 3.4 Basic Email

```bash
curl -X POST https://es.ekddigital.com/api/v1/send \
  -H "Authorization: Bearer ek_live_your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "email",
    "to": "user@example.com",
    "subject": "Welcome to Our Service",
    "body": "<h1>Welcome!</h1><p>Thanks for signing up.</p>"
  }'
```

**Notes (from implementation):**

- `to` can be a string or an array of strings (max 50 recipients)
- `from` defaults to `process.env.ES_DEFAULT_FROM` if omitted
- Either `body` **or** `template` must be provided

### 3.5 Email with CC/BCC/Reply-To

```bash
curl -X POST https://es.ekddigital.com/api/v1/send \
  -H "Authorization: Bearer ek_live_your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "email",
    "to": "main@example.com",
    "cc": ["manager@example.com"],
    "bcc": ["archive@example.com"],
    "replyTo": "support@yourcompany.com",
    "subject": "Important Announcement",
    "body": "<p>Please see the attached report...</p>"
  }'
```

If any address in `to`, `cc`, `bcc`, or `replyTo` is invalid, the API returns `400 VALIDATION_ERROR`.

### 3.6 Multiple Recipients

```bash
curl -X POST https://es.ekddigital.com/api/v1/send \
  -H "Authorization: Bearer ek_live_your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "email",
    "to": ["user1@example.com", "user2@example.com", "user3@example.com"],
    "subject": "Team Update",
    "body": "<p>Hello team, here is the weekly update...</p>"
  }'
```

Quotas are enforced **per recipient** via `enforceQuota(customerId, "EMAIL", recipients.length)`.

### 3.7 Email with Attachments (via /emails endpoint)

```bash
curl -X POST https://es.ekddigital.com/api/v1/emails \
  -H "Authorization: Bearer ek_live_your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "user@example.com",
    "subject": "Invoice Attached",
    "html": "<p>Please find your invoice attached.</p>",
    "text": "Please find your invoice attached.",
    "attachments": [
      {
        "filename": "invoice-2026-001.pdf",
        "content": "JVBERi0xLjcKJeLjz9MK...",
        "contentType": "application/pdf"
      }
    ]
  }'
```

### 3.8 Email with Custom Headers

```bash
curl -X POST https://es.ekddigital.com/api/v1/emails \
  -H "Authorization: Bearer ek_live_your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "user@example.com",
    "subject": "Order Confirmation",
    "html": "<h1>Order #12345</h1><p>Your order has been confirmed.</p>",
    "headers": {
      "X-Order-ID": "12345",
      "X-Customer-ID": "cust_789"
    },
    "tags": ["order-confirmation", "e-commerce"]
  }'
```

---

## 4. Built-in Email Templates

EKDSend includes pre-built templates for common transactional email use cases.

### 4.1 Available Templates

| Template Key      | Use Case                      | Variables                                                                           |
| ----------------- | ----------------------------- | ----------------------------------------------------------------------------------- |
| `welcome`         | New user welcome email        | `firstName`, `serviceName`, `dashboardUrl`                                          |
| `verification`    | Email verification            | `name`, `verificationLink`, `expiryHours`, `serviceName`                            |
| `passwordReset`   | Password reset request        | `name`, `resetLink`, `expiryHours`, `serviceName`                                   |
| `apiKeyCreated`   | API key creation notification | `name`, `keyName`, `scopes`, `createdAt`, `serviceName`                             |
| `quotaWarning`    | Usage quota warning           | `name`, `usagePercent`, `resourceType`, `currentUsage`, `quotaLimit`, `serviceName` |
| `deliveryFailure` | Message delivery failed       | `name`, `messageId`, `messageType`, `recipient`, `failureReason`, `serviceName`     |

### 4.2 Using Built-in Templates

```bash
curl -X POST https://es.ekddigital.com/api/v1/send \
  -H "Authorization: Bearer ek_live_your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "email",
    "to": "user@example.com",
    "template": "welcome",
    "templateData": {
      "firstName": "John",
      "serviceName": "EKDSend",
      "dashboardUrl": "https://es.ekddigital.com/dashboard"
    }
  }'
```

### 4.3 Verification Email Template

```bash
curl -X POST https://es.ekddigital.com/api/v1/send \
  -H "Authorization: Bearer ek_live_your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "email",
    "to": "newuser@example.com",
    "template": "verification",
    "templateData": {
      "name": "Jane Doe",
      "verificationLink": "https://yourapp.com/verify?token=abc123",
      "expiryHours": "24",
      "serviceName": "YourApp"
    }
  }'
```

### 4.4 Password Reset Template

```bash
curl -X POST https://es.ekddigital.com/api/v1/send \
  -H "Authorization: Bearer ek_live_your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "email",
    "to": "user@example.com",
    "template": "passwordReset",
    "templateData": {
      "name": "John Smith",
      "resetLink": "https://yourapp.com/reset?token=xyz789",
      "expiryHours": "2",
      "serviceName": "YourApp"
    }
  }'
```

### 4.5 Template Variable Syntax

Templates use Mustache-style `{{variableName}}` syntax:

```
Hello {{firstName}},

Welcome to {{serviceName}}! Click below to access your dashboard:

{{dashboardUrl}}
```

If `template` is provided but unknown, the API returns `400 VALIDATION_ERROR`.

> Template definitions are in `src/lib/utils/templates/builtins.ts`

---

## 5. Domain Configuration

For better deliverability, configure your sending domain with proper DNS records.

### 5.1 Add a Domain

```bash
curl -X POST https://es.ekddigital.com/api/v1/domains \
  -H "Authorization: Bearer ek_live_your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "example.com"
  }'
```

**Response:**

```json
{
  "id": "dom_abc123",
  "domain": "example.com",
  "status": "PENDING",
  "dnsRecords": {
    "spf": {
      "type": "TXT",
      "host": "@",
      "value": "v=spf1 include:mail.ekdsend.com ~all"
    },
    "dkim": {
      "type": "TXT",
      "host": "ekd._domainkey",
      "selector": "ekd",
      "record": "v=DKIM1; k=rsa; p=MIIBIjANBg..."
    },
    "dmarc": {
      "type": "TXT",
      "host": "_dmarc",
      "value": "v=DMARC1; p=quarantine; rua=mailto:dmarc@ekddigital.com"
    }
  }
}
```

### 5.2 List Domains

```bash
curl -X GET https://es.ekddigital.com/api/v1/domains \
  -H "Authorization: Bearer ek_live_your_api_key"
```

### 5.3 Verify Domain DNS

```bash
curl -X POST https://es.ekddigital.com/api/v1/domains/dom_abc123/verify \
  -H "Authorization: Bearer ek_live_your_api_key"
```

### 5.4 Domain Statuses

| Status     | Description                             |
| ---------- | --------------------------------------- |
| `PENDING`  | Domain added, awaiting DNS verification |
| `VERIFIED` | DNS records verified, ready for sending |
| `FAILED`   | DNS verification failed                 |

---

## 6. Email Message History

The Messages API gives you a unified view of all email activity.

### 6.1 List Emails

**Endpoint:**

```http
GET /api/v1/emails
```

**Query Parameters (all optional):**

| Name        | Type     | Description                                                             |
| ----------- | -------- | ----------------------------------------------------------------------- |
| `status`    | string   | `queued` \| `sending` \| `sent` \| `delivered` \| `failed` \| `bounced` |
| `direction` | string   | `inbound` \| `outbound`                                                 |
| `from`      | string   | Partial match on sender                                                 |
| `to`        | string   | Exact match in recipient array                                          |
| `start`     | ISO date | Filter `createdAt >=`                                                   |
| `end`       | ISO date | Filter `createdAt <=`                                                   |
| `page`      | number   | Default `1`                                                             |
| `limit`     | number   | Default `25`, max `100`                                                 |

**Example:**

```bash
curl -X GET 'https://es.ekddigital.com/api/v1/emails?status=delivered&page=1&limit=20' \
  -H "Authorization: Bearer ek_live_your_api_key"
```

**Response:**

```json
{
  "data": [
    {
      "id": "clxyz123abc456",
      "status": "DELIVERED",
      "from": "no-reply@yourapp.com",
      "to": ["user@example.com"],
      "subject": "Welcome",
      "createdAt": "2026-01-02T14:29:59.000Z",
      "sentAt": "2026-01-02T14:30:02.000Z",
      "deliveredAt": "2026-01-02T14:30:03.000Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 1,
    "totalPages": 1,
    "hasMore": false
  }
}
```

### 6.2 Get a Single Email

**Endpoint:**

```http
GET /api/v1/emails/{id}
```

```bash
curl -X GET https://es.ekddigital.com/api/v1/emails/clxyz123abc456 \
  -H "Authorization: Bearer ek_live_your_api_key"
```

### 6.3 Using the Messages Endpoint

For a unified view across email, SMS, and voice:

```bash
curl -X GET 'https://es.ekddigital.com/api/v1/messages?channel=email&status=delivered' \
  -H "Authorization: Bearer ek_live_your_api_key"
```

**Response:**

```json
{
  "success": true,
  "data": {
    "messages": [
      {
        "id": "clxyz123abc456",
        "channel": "email",
        "direction": "outbound",
        "status": "DELIVERED",
        "from": "no-reply@yourapp.com",
        "to": ["user@example.com"],
        "subject": "Welcome",
        "preview": "Welcome to our platform...",
        "queuedAt": "2026-01-02T14:30:00.000Z",
        "sentAt": "2026-01-02T14:30:02.000Z",
        "deliveredAt": "2026-01-02T14:30:03.000Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 1,
      "totalPages": 1,
      "hasMore": false
    }
  }
}
```

---

## 7. Sandbox Mode

The sandbox endpoints allow you to test email flows **without sending real emails**.

### 7.1 How Sandbox Mode Works

When your tenant is in sandbox mode:

- Emails are stored in a sandbox "mailbox" instead of being sent
- No actual SMTP delivery occurs
- Perfect for development and testing

### 7.2 List Sandbox Emails

**Endpoint:**

```http
GET /api/v1/sandbox/emails
```

```bash
curl -X GET 'https://es.ekddigital.com/api/v1/sandbox/emails?limit=20' \
  -H "Authorization: Bearer ek_live_your_api_key"
```

**Response:**

```json
{
  "emails": [
    {
      "id": "sbx_123",
      "to": ["user@example.com"],
      "from": "no-reply@yourapp.com",
      "subject": "Welcome",
      "html": "<h1>Welcome</h1>",
      "text": "Welcome",
      "createdAt": "2026-01-02T14:30:00.000Z"
    }
  ],
  "count": 1,
  "sandbox": true
}
```

### 7.3 Clear Sandbox Emails

```bash
curl -X DELETE https://es.ekddigital.com/api/v1/sandbox/emails \
  -H "Authorization: Bearer ek_live_your_api_key"
```

**Response:**

```json
{
  "success": true,
  "deleted": 42
}
```

---

## 8. Rate Limiting & Quotas

The email API applies both **rate limits** and **monthly/plan quotas**.

### 8.1 Rate Limits

Rate limits are enforced per API key based on your plan:

| Plan         | Email Send/hr | Burst/min | Daily Cap |
| ------------ | ------------- | --------- | --------- |
| Free         | 500           | 20        | 5,000     |
| Starter (5x) | 2,500         | 100       | 25,000    |
| Pro (20x)    | 10,000        | 400       | 100,000   |
| Enterprise   | 50,000        | 2,000     | 500,000   |

On every response, rate limit headers are included:

```http
X-RateLimit-Limit: 500
X-RateLimit-Remaining: 450
X-RateLimit-Reset: 1735830600
```

If you exceed the limit:

```json
{
  "error": "Rate limit exceeded",
  "code": "rate_limit_exceeded",
  "retryAfter": 60
}
```

**Response Status:** `429 Too Many Requests`

### 8.2 Monthly Quotas

Quotas are enforced per customer by plan:

| Plan       | Emails/Month |
| ---------- | ------------ |
| Free       | 100          |
| Starter    | 10,000       |
| Pro        | 100,000      |
| Enterprise | Unlimited    |

If a quota is exceeded:

```json
{
  "error": {
    "message": "Monthly email quota exceeded",
    "code": "QUOTA_EXCEEDED"
  }
}
```

### 8.3 Checking Quota Usage

```bash
curl -X GET https://es.ekddigital.com/api/v1/usage \
  -H "Authorization: Bearer ek_live_your_api_key"
```

---

## 9. Webhooks

Configure webhooks to receive real-time email delivery status updates.

### 9.1 Create a Webhook

```bash
curl -X POST https://es.ekddigital.com/api/v1/webhooks \
  -H "Authorization: Bearer ek_live_your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://yourapp.com/webhooks/email",
    "events": ["email.sent", "email.delivered", "email.bounced", "email.failed"]
  }'
```

**Response:**

```json
{
  "id": "wh_abc123",
  "url": "https://yourapp.com/webhooks/email",
  "events": ["email.sent", "email.delivered", "email.bounced", "email.failed"],
  "secret": "whsec_abc123xyz789...",
  "status": "ACTIVE"
}
```

### 9.2 Webhook Events

| Event             | Description                        |
| ----------------- | ---------------------------------- |
| `email.queued`    | Email added to send queue          |
| `email.sent`      | Email sent to SMTP server          |
| `email.delivered` | Email delivered to recipient inbox |
| `email.bounced`   | Email bounced (hard/soft)          |
| `email.failed`    | Email delivery failed              |
| `email.opened`    | Email opened (if tracking enabled) |
| `email.clicked`   | Link clicked (if tracking enabled) |

### 9.3 Webhook Payload

```json
{
  "event": "email.delivered",
  "messageId": "clxyz123abc456",
  "timestamp": "2026-01-02T14:30:05.000Z",
  "data": {
    "from": "no-reply@yourapp.com",
    "to": ["user@example.com"],
    "subject": "Welcome",
    "status": "delivered"
  }
}
```

### 9.4 Verifying Webhook Signatures

Webhooks include an `X-EKDSend-Signature` header. Verify using HMAC-SHA256:

```javascript
const crypto = require("crypto");

function verifyWebhook(payload, signature, secret) {
  const expected = crypto
    .createHmac("sha256", secret)
    .update(payload)
    .digest("hex");
  return crypto.timingSafeEqual(Buffer.from(signature), Buffer.from(expected));
}
```

### 9.5 List Webhooks

```bash
curl -X GET https://es.ekddigital.com/api/v1/webhooks \
  -H "Authorization: Bearer ek_live_your_api_key"
```

---

## 10. Error Handling

All errors follow a consistent format.

### 10.1 Validation Errors

```json
{
  "error": {
    "message": "Invalid email address: bad-email",
    "code": "VALIDATION_ERROR",
    "details": {
      "field": "to"
    }
  }
}
```

**Status:** `400 Bad Request`

### 10.2 Authentication Errors

```json
{
  "error": {
    "message": "Invalid or missing API key",
    "code": "UNAUTHORIZED"
  }
}
```

**Status:** `401 Unauthorized`

### 10.3 Permission Errors

```json
{
  "error": {
    "message": "API key does not have required scope: send:email",
    "code": "FORBIDDEN"
  }
}
```

**Status:** `403 Forbidden`

### 10.4 Rate Limit Errors

```json
{
  "error": "Rate limit exceeded",
  "code": "rate_limit_exceeded",
  "retryAfter": 60
}
```

**Status:** `429 Too Many Requests`

### 10.5 Server Errors

```json
{
  "error": {
    "message": "Internal server error",
    "code": "INTERNAL_ERROR"
  }
}
```

**Status:** `500 Internal Server Error`

---

## 11. SDK & Language Examples

### 11.1 Node.js (using fetch)

```javascript
const EKDSEND_API_KEY = process.env.EKDSEND_API_KEY;
const BASE_URL = "https://es.ekddigital.com/api/v1";

async function sendTransactionalEmail(options) {
  const response = await fetch(`${BASE_URL}/send`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${EKDSEND_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      type: "email",
      to: options.to,
      subject: options.subject,
      body: options.html || options.text,
      cc: options.cc,
      bcc: options.bcc,
      replyTo: options.replyTo,
    }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error?.message || "Failed to send email");
  }

  return data;
}

// Usage
async function main() {
  try {
    const result = await sendTransactionalEmail({
      to: "user@example.com",
      subject: "Order Confirmation #12345",
      html: "<h1>Thank you for your order!</h1><p>Your order has been confirmed.</p>",
    });
    console.log("Email queued:", result.messageId);
  } catch (error) {
    console.error("Error:", error.message);
  }
}
```

### 11.2 Node.js (using EKDSend Client)

```javascript
// Using the built-in client from src/lib/utils/email/client.ts
import { sendEmailViaAPI } from "@/lib/utils/email/client";

// Send a basic email
const result = await sendEmailViaAPI({
  to: "user@example.com",
  subject: "Welcome!",
  html: "<h1>Welcome to our service!</h1>",
  text: "Welcome to our service!",
});

if (result.success) {
  console.log("Sent:", result.messageId);
} else {
  console.error("Error:", result.error);
}
```

### 11.3 Python (requests)

```python
import os
import requests
from typing import Optional, List

EKDSEND_API_KEY = os.environ.get('EKDSEND_API_KEY')
BASE_URL = 'https://es.ekddigital.com/api/v1'


def send_transactional_email(
    to: str | List[str],
    subject: str,
    html: Optional[str] = None,
    text: Optional[str] = None,
    cc: Optional[List[str]] = None,
    bcc: Optional[List[str]] = None,
    reply_to: Optional[str] = None,
) -> dict:
    """Send a transactional email via EKDSend API."""

    payload = {
        'type': 'email',
        'to': to,
        'subject': subject,
        'body': html or text,
    }

    if cc:
        payload['cc'] = cc
    if bcc:
        payload['bcc'] = bcc
    if reply_to:
        payload['replyTo'] = reply_to

    response = requests.post(
        f'{BASE_URL}/send',
        headers={
            'Authorization': f'Bearer {EKDSEND_API_KEY}',
            'Content-Type': 'application/json',
        },
        json=payload,
        timeout=30,
    )

    data = response.json()

    if not response.ok:
        error_msg = data.get('error', {}).get('message', 'Unknown error')
        raise RuntimeError(f'Failed to send email: {error_msg}')

    return data


# Usage
if __name__ == '__main__':
    result = send_transactional_email(
        to='user@example.com',
        subject='Password Reset Request',
        html='<p>Click <a href="https://app.example.com/reset?token=abc123">here</a> to reset your password.</p>',
        text='Visit https://app.example.com/reset?token=abc123 to reset your password.',
    )
    print(f'Email queued: {result["messageId"]}')
```

### 11.4 Go

```go
package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "net/http"
    "os"
)

type SendEmailRequest struct {
    Type    string   `json:"type"`
    To      []string `json:"to"`
    Subject string   `json:"subject"`
    Body    string   `json:"body"`
    CC      []string `json:"cc,omitempty"`
    BCC     []string `json:"bcc,omitempty"`
    ReplyTo string   `json:"replyTo,omitempty"`
}

type SendEmailResponse struct {
    Success   bool   `json:"success"`
    MessageID string `json:"messageId"`
    QueuedAt  string `json:"queuedAt"`
    Error     struct {
        Message string `json:"message"`
        Code    string `json:"code"`
    } `json:"error"`
}

func sendTransactionalEmail(to []string, subject, body string) (*SendEmailResponse, error) {
    apiKey := os.Getenv("EKDSEND_API_KEY")

    payload := SendEmailRequest{
        Type:    "email",
        To:      to,
        Subject: subject,
        Body:    body,
    }

    jsonData, err := json.Marshal(payload)
    if err != nil {
        return nil, err
    }

    req, err := http.NewRequest("POST", "https://es.ekddigital.com/api/v1/send", bytes.NewBuffer(jsonData))
    if err != nil {
        return nil, err
    }

    req.Header.Set("Authorization", "Bearer "+apiKey)
    req.Header.Set("Content-Type", "application/json")

    client := &http.Client{}
    resp, err := client.Do(req)
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()

    var result SendEmailResponse
    if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
        return nil, err
    }

    if !result.Success {
        return nil, fmt.Errorf("failed to send email: %s", result.Error.Message)
    }

    return &result, nil
}

func main() {
    result, err := sendTransactionalEmail(
        []string{"user@example.com"},
        "Welcome to Our App",
        "<h1>Welcome!</h1><p>Thanks for signing up.</p>",
    )
    if err != nil {
        fmt.Println("Error:", err)
        return
    }
    fmt.Printf("Email queued: %s\n", result.MessageID)
}
```

### 11.5 Ruby

```ruby
require 'net/http'
require 'json'
require 'uri'

class EKDSendClient
  BASE_URL = 'https://es.ekddigital.com/api/v1'.freeze

  def initialize(api_key = ENV['EKDSEND_API_KEY'])
    @api_key = api_key
  end

  def send_email(to:, subject:, html: nil, text: nil, cc: nil, bcc: nil, reply_to: nil)
    uri = URI("#{BASE_URL}/send")

    http = Net::HTTP.new(uri.host, uri.port)
    http.use_ssl = true

    request = Net::HTTP::Post.new(uri.path)
    request['Authorization'] = "Bearer #{@api_key}"
    request['Content-Type'] = 'application/json'

    payload = {
      type: 'email',
      to: to,
      subject: subject,
      body: html || text
    }
    payload[:cc] = cc if cc
    payload[:bcc] = bcc if bcc
    payload[:replyTo] = reply_to if reply_to

    request.body = payload.to_json

    response = http.request(request)
    result = JSON.parse(response.body)

    unless result['success']
      raise StandardError, result.dig('error', 'message') || 'Unknown error'
    end

    result
  end
end

# Usage
client = EKDSendClient.new
result = client.send_email(
  to: 'user@example.com',
  subject: 'Invoice #12345',
  html: '<h1>Invoice</h1><p>Please find your invoice attached.</p>'
)
puts "Email queued: #{result['messageId']}"
```

### 11.6 PHP

```php
<?php

class EKDSendClient {
    private const BASE_URL = 'https://es.ekddigital.com/api/v1';
    private string $apiKey;

    public function __construct(?string $apiKey = null) {
        $this->apiKey = $apiKey ?? getenv('EKDSEND_API_KEY');
    }

    public function sendEmail(
        string|array $to,
        string $subject,
        ?string $html = null,
        ?string $text = null,
        ?array $cc = null,
        ?array $bcc = null,
        ?string $replyTo = null
    ): array {
        $payload = [
            'type' => 'email',
            'to' => $to,
            'subject' => $subject,
            'body' => $html ?? $text,
        ];

        if ($cc) $payload['cc'] = $cc;
        if ($bcc) $payload['bcc'] = $bcc;
        if ($replyTo) $payload['replyTo'] = $replyTo;

        $ch = curl_init(self::BASE_URL . '/send');
        curl_setopt_array($ch, [
            CURLOPT_POST => true,
            CURLOPT_POSTFIELDS => json_encode($payload),
            CURLOPT_HTTPHEADER => [
                'Authorization: Bearer ' . $this->apiKey,
                'Content-Type: application/json',
            ],
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_TIMEOUT => 30,
        ]);

        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);

        $result = json_decode($response, true);

        if ($httpCode >= 400 || !$result['success']) {
            throw new Exception($result['error']['message'] ?? 'Unknown error');
        }

        return $result;
    }
}

// Usage
$client = new EKDSendClient();
$result = $client->sendEmail(
    to: 'user@example.com',
    subject: 'Account Verification',
    html: '<p>Click <a href="https://app.example.com/verify">here</a> to verify your account.</p>'
);
echo "Email queued: " . $result['messageId'] . "\n";
```

---

## 12. Email Deliverability Best Practices

### 12.1 Domain Authentication (SPF, DKIM, DMARC)

Configure these DNS records for maximum deliverability:

**SPF Record:**

```
Type: TXT
Host: @
Value: v=spf1 include:mail.ekdsend.com ~all
```

**DKIM Record:**

```
Type: TXT
Host: ekd._domainkey
Value: v=DKIM1; k=rsa; p=<your-public-key>
```

**DMARC Record:**

```
Type: TXT
Host: _dmarc
Value: v=DMARC1; p=quarantine; rua=mailto:dmarc@yourdomain.com
```

### 12.2 Email Headers Added Automatically

EKDSend adds these headers for better deliverability:

```
X-Mailer: EKDSend/1.0
X-Platform: EKDSend Email Service
X-Entity-Type: transactional
Message-ID: <messageId.timestamp@mail.es.ekddigital.com>
```

### 12.3 Best Practices Checklist

✅ **DO:**

- Verify your sending domain before production use
- Use a consistent "From" address
- Include both HTML and plain text versions
- Use templates for consistent branding
- Monitor bounce rates and handle unsubscribes
- Set meaningful subject lines
- Include a Reply-To address for support emails
- Store API keys securely - Use environment variables, never commit to git
- Handle rate limits - Check `X-RateLimit-Remaining` header

❌ **DON'T:**

- Send to purchased email lists
- Use generic or misleading subject lines
- Ignore bounce notifications
- Send without domain verification
- Use localhost URLs in email content
- Expose API keys - Never put API keys in frontend code
- Ignore errors - Always check response status
- Send spam - Follow anti-spam laws (CAN-SPAM, GDPR)

---

## 13. SMTP Relay Configuration

For applications that need direct SMTP access:

### 13.1 SMTP Settings

```
Host: mail.es.ekddigital.com
Port: 587 (STARTTLS) or 465 (SSL)
Username: Your API Key
Password: Your API Key
Encryption: STARTTLS (recommended)
```

### 13.2 Nodemailer Configuration

```javascript
const nodemailer = require("nodemailer");

const transporter = nodemailer.createTransport({
  host: "mail.es.ekddigital.com",
  port: 587,
  secure: false, // STARTTLS
  auth: {
    user: process.env.EKDSEND_API_KEY,
    pass: process.env.EKDSEND_API_KEY,
  },
});

await transporter.sendMail({
  from: "no-reply@yourdomain.com",
  to: "user@example.com",
  subject: "Test Email",
  html: "<h1>Hello!</h1>",
});
```

### 13.3 Python smtplib Configuration

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

smtp_host = 'mail.es.ekddigital.com'
smtp_port = 587
api_key = os.environ['EKDSEND_API_KEY']

msg = MIMEMultipart('alternative')
msg['Subject'] = 'Test Email'
msg['From'] = 'no-reply@yourdomain.com'
msg['To'] = 'user@example.com'

text = 'Hello from Python!'
html = '<h1>Hello from Python!</h1>'

msg.attach(MIMEText(text, 'plain'))
msg.attach(MIMEText(html, 'html'))

with smtplib.SMTP(smtp_host, smtp_port) as server:
    server.starttls()
    server.login(api_key, api_key)
    server.sendmail(msg['From'], msg['To'], msg.as_string())
```

---

## 14. Transactional Email Use Cases

### 14.1 User Authentication Emails

```javascript
// Email verification
await sendTransactionalEmail({
  to: user.email,
  subject: "Verify your email address",
  template: "verification",
  templateData: {
    name: user.name,
    verificationLink: `${APP_URL}/verify?token=${token}`,
    expiryHours: "24",
    serviceName: "YourApp",
  },
});

// Password reset
await sendTransactionalEmail({
  to: user.email,
  subject: "Reset your password",
  template: "passwordReset",
  templateData: {
    name: user.name,
    resetLink: `${APP_URL}/reset?token=${token}`,
    expiryHours: "2",
    serviceName: "YourApp",
  },
});
```

### 14.2 Order & Invoice Emails

```javascript
await sendTransactionalEmail({
  to: customer.email,
  subject: `Order Confirmation #${order.id}`,
  html: `
    <h1>Thank you for your order!</h1>
    <p>Order #${order.id} has been confirmed.</p>
    <table>
      ${order.items
        .map(
          (item) => `
        <tr>
          <td>${item.name}</td>
          <td>${item.quantity}</td>
          <td>$${item.price}</td>
        </tr>
      `
        )
        .join("")}
    </table>
    <p><strong>Total: $${order.total}</strong></p>
  `,
  headers: {
    "X-Order-ID": order.id,
  },
  tags: ["order-confirmation"],
});
```

### 14.3 Notification Emails

```javascript
// Activity notification
await sendTransactionalEmail({
  to: user.email,
  subject: "New comment on your post",
  html: `
    <p>Hi ${user.name},</p>
    <p>${commenter.name} commented on your post "${post.title}":</p>
    <blockquote>${comment.text}</blockquote>
    <p><a href="${postUrl}">View comment</a></p>
  `,
  replyTo: "notifications@yourapp.com",
});
```

---

## 15. Environment Variables

```bash
# Required - API Key for authentication
EKDSEND_API_KEY="ek_live_your_api_key_here"

# Optional - Override default API URL
ES_API_URL="https://es.ekddigital.com"

# Optional - Default sender address
ES_DEFAULT_FROM="noreply@mail.ekdsend.com"

# Optional - App URL for links in emails
ES_APP_URL="https://yourapp.com"

# For SMTP relay (if using direct SMTP)
ES_SMTP_HOST="mail.es.ekddigital.com"
ES_SMTP_PORT="587"
ES_SMTP_USER="your_api_key"
ES_SMTP_PASS="your_api_key"
```

---

## 16. API Endpoint Reference

| Endpoint                       | Method | Description                   |
| ------------------------------ | ------ | ----------------------------- |
| `/api/v1/send`                 | POST   | Send email (unified endpoint) |
| `/api/v1/emails`               | POST   | Send email (full featured)    |
| `/api/v1/emails`               | GET    | List emails                   |
| `/api/v1/emails/:id`           | GET    | Get email details             |
| `/api/v1/messages`             | GET    | List all messages             |
| `/api/v1/messages/:id`         | GET    | Get message details           |
| `/api/v1/api-keys`             | POST   | Create API key                |
| `/api/v1/api-keys`             | GET    | List API keys                 |
| `/api/v1/api-keys/:id`         | DELETE | Revoke API key                |
| `/api/v1/domains`              | POST   | Add sending domain            |
| `/api/v1/domains`              | GET    | List domains                  |
| `/api/v1/domains/:id`          | GET    | Get domain details            |
| `/api/v1/domains/:id/verify`   | POST   | Verify domain DNS             |
| `/api/v1/webhooks`             | POST   | Create webhook                |
| `/api/v1/webhooks`             | GET    | List webhooks                 |
| `/api/v1/sandbox/emails`       | GET    | List sandbox emails           |
| `/api/v1/sandbox/emails/clear` | DELETE | Clear sandbox emails          |
| `/api/v1/usage`                | GET    | Get usage statistics          |

---

## 17. Support & Resources

- **API Documentation:** [es.ekddigital.com/docs](https://es.ekddigital.com/docs)
- **Dashboard:** [es.ekddigital.com/dashboard](https://es.ekddigital.com/dashboard)
- **Email Support:** support@ekddigital.com
- **Status Page:** [status.ekddigital.com](https://status.ekddigital.com)

---

**Happy Sending! 🚀**

_EKDSend - Professional Transactional Email Delivery_

_Powered by [EKD Digital](https://ekddigital.com)_

If anything in this guide doesn’t match what you see from the live API, we can adjust the implementation or this document so they stay perfectly aligned.
}

    jsonData, _ := json.Marshal(payload)

    req, _ := http.NewRequest("POST", "https://es.ekddigital.com/api/v1/send", bytes.NewBuffer(jsonData))
    req.Header.Set("Authorization", "Bearer "+apiKey)
    req.Header.Set("Content-Type", "application/json")

    client := &http.Client{}
    resp, err := client.Do(req)
    if err != nil {
        return "", err
    }
    defer resp.Body.Close()

    var result SendResponse
    json.NewDecoder(resp.Body).Decode(&result)

    if result.Success {
        return result.MessageID, nil
    }
    return "", fmt.Errorf(result.Error.Message)

}

func main() {
msgID, err := sendEmail("user@example.com", "Hello from Go", "<h1>It works!</h1>")
if err != nil {
fmt.Println("Error:", err)
return
}
fmt.Println("Email queued:", msgID)
}

````

### Ruby

```ruby
require 'net/http'
require 'json'
require 'uri'

def send_email(to, subject, body)
  uri = URI('https://es.ekddigital.com/api/v1/send')
  api_key = ENV['EKDSEND_API_KEY']

  http = Net::HTTP.new(uri.host, uri.port)
  http.use_ssl = true

  request = Net::HTTP::Post.new(uri.path)
  request['Authorization'] = "Bearer #{api_key}"
  request['Content-Type'] = 'application/json'
  request.body = {
    type: 'email',
    to: to,
    subject: subject,
    body: body
  }.to_json

  response = http.request(request)
  result = JSON.parse(response.body)

  if result['success']
    puts "Email queued: #{result['messageId']}"
    result['messageId']
  else
    raise result['error']['message']
  end
end

# Usage
send_email('user@example.com', 'Hello from Ruby', '<h1>It works!</h1>')
````

---

## 9. API Key Scopes

| Scope          | Permission              |
| -------------- | ----------------------- |
| `send:email`   | Send email messages     |
| `send:sms`     | Send SMS messages       |
| `send:voice`   | Make voice calls        |
| `admin:view`   | View account settings   |
| `admin:manage` | Manage account settings |

---

## 10. Webhooks (Coming Soon)

Configure webhooks to receive real-time delivery status updates:

```json
{
  "event": "email.delivered",
  "messageId": "clxyz123abc456",
  "timestamp": "2025-11-26T14:30:05.000Z",
  "recipient": "user@example.com",
  "status": "delivered"
}
```

---

## 11. Best Practices

### ✅ DO

- **Store API keys securely** - Use environment variables, never commit to git
- **Use HTTPS only** - All API calls must be over HTTPS
- **Handle rate limits** - Check `X-RateLimit-Remaining` header
- **Validate emails** - Validate recipient addresses before sending
- **Use templates** - For consistent, maintainable email content
- **Set meaningful `from`** - Use `noreply@` or `support@` addresses

### ❌ DON'T

- **Don't expose keys** - Never put API keys in frontend code
- **Don't ignore errors** - Always check response status
- **Don't send spam** - Follow anti-spam laws (CAN-SPAM, GDPR)
- **Don't hardcode recipients** - Use variables for recipient addresses

---

## 12. Environment Variables

```bash
# Required
EKDSEND_API_KEY="ek_live_your_api_key_here"

# Optional (for local development)
EKDSEND_API_URL="https://es.ekddigital.com/api/v1"
```

---

## 13. Support

- **Documentation:** [es.ekddigital.com/docs](https://es.ekddigital.com/docs)
- **Email:** support@ekddigital.com
- **Status Page:** [status.ekddigital.com](https://status.ekddigital.com)

---

## Quick Reference

| Endpoint                     | Method | Description          |
| ---------------------------- | ------ | -------------------- |
| `/api/v1/send`               | POST   | Send email/SMS/voice |
| `/api/v1/api-keys`           | POST   | Create API key       |
| `/api/v1/api-keys`           | GET    | List API keys        |
| `/api/v1/api-keys/:id`       | DELETE | Revoke API key       |
| `/api/v1/domains`            | GET    | List domains         |
| `/api/v1/domains/:id/verify` | POST   | Verify domain DNS    |

---

**Happy Sending! 🚀**

_Powered by [EKD Digital](https://ekddigital.com)_
