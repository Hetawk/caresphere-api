# EKDSend Email API - Complete Usage Guide

> Unified email, SMS, and voice messaging over a single `/send` endpoint, with message search, sandbox inbox, and quotas built-in.

This guide is modeled after `XTERM_API_USAGE.md` and `ASSETS_API_USAGE.md` and reflects the **actual implementation** under `src/app/api/v1`.

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
    "body": "This is a test email sent via the EKDSend API."
  }'
```

On success, the API responds with:

```json
{
  "success": true,
  "messageId": "msg_1234567890",
  "type": "email",
  "queuedAt": "2025-11-26T14:30:00.000Z"
}
```

---

## 2. Authentication & Scopes

Every request to `/api/v1/send` and the messages/sandbox endpoints must include a valid API key with the right scopes.

**Header format:**

```http
Authorization: Bearer ek_live_your_api_key_here
```

### Required Scopes

| Feature              | Scope                                                    |
| -------------------- | -------------------------------------------------------- |
| Send Email           | `send:email`                                             |
| Send SMS             | `send:sms`                                               |
| Send Voice           | `send:voice`                                             |
| List/Search Messages | `messages:read` (configured in backend)                  |
| Sandbox Inbox        | `sandbox:read` / `sandbox:write` (configured in backend) |

If the scope for the selected `type` is missing, the API returns `403 FORBIDDEN`.

> The `authenticate` + `checkScope` logic lives in `src/lib/auth/middleware.ts` and `src/lib/auth/apiKey.ts`.

---

## 3. The `/send` Endpoint

**Endpoint:**

```http
POST /api/v1/send
```

This is a **unified** endpoint for:

- Email (`type: "email"`)
- SMS (`type: "sms"`)
- Voice (`type: "voice"`)

Behind the scenes, the handler:

- Authenticates the API key
- Enforces rate limits (`RATE_LIMITS["send:basic"]`)
- Enforces quotas per customer (`enforceQuota`)
- Validates and normalizes the payload
- Stores a `message` record in the database (`prisma.message.create`)
- Queues work to the appropriate worker (`queueEmail`, `queueSms`, `queueVoice`)

### 3.1 Request Shape (Typed)

```ts
// Email
interface SendEmailRequest {
  type: "email";
  to: string | string[];
  from?: string;
  subject: string;
  body?: string; // direct HTML/text body
  template?: string; // builtin template key
  templateData?: Record<string, unknown>;
  cc?: string[];
  bcc?: string[];
  replyTo?: string;
}

// SMS
interface SendSmsRequest {
  type: "sms";
  to: string | string[];
  from?: string;
  body?: string; // direct SMS text
  template?: string;
  templateData?: Record<string, unknown>;
}

// Voice
interface SendVoiceRequest {
  type: "voice";
  to: string;
  from?: string;
  body?: string; // TTS text or script
  template?: string;
  templateData?: Record<string, unknown>;
}
```

### 3.2 Send Email (Basic)

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

- `to` can be a string or an array of strings. Every address is validated with `validateEmail`.
- `from` defaults to `process.env.ES_DEFAULT_FROM` if omitted.
- Either `body` **or** `template` must be provided.

### 3.3 Email with CC/BCC/Reply-To

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
    "body": "Please see the attached report..."
  }'
```

If any address in `to`, `cc`, `bcc`, or `replyTo` is invalid, the API returns `400 VALIDATION_ERROR`.

### 3.4 Multiple Recipients

```bash
curl -X POST https://es.ekddigital.com/api/v1/send \
  -H "Authorization: Bearer ek_live_your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "email",
    "to": ["user1@example.com", "user2@example.com"],
    "subject": "Team Update",
    "body": "Hello team, here is the weekly update..."
  }'
```

Quotas are enforced **per recipient** via `enforceQuota(customerId, "EMAIL", recipients.length)`.

### 3.5 Using Built-in Templates

Email templates are resolved through `getEmailTemplate(templateKey)` and rendered with `renderTemplate`.

```bash
curl -X POST https://es.ekddigital.com/api/v1/send \
  -H "Authorization: Bearer ek_live_your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "email",
    "to": "user@example.com",
    "template": "welcome",
    "templateData": {
      "name": "John Doe",
      "company": "ACME Inc"
    }
  }'
```

If `template` is provided but unknown, the API returns `400 VALIDATION_ERROR`.

> The available template keys and shapes live in `src/lib/utils/templates/builtins.ts`.

### 3.6 Send SMS

```bash
curl -X POST https://es.ekddigital.com/api/v1/send \
  -H "Authorization: Bearer ek_live_your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "sms",
    "to": "+1234567890",
    "body": "Your verification code is: 123456"
  }'
```

**Implementation details:**

- `to` can be a single E.164 number or an array.
- Each number is validated with `validatePhone`.
- Quotas are enforced with `enforceQuota(customerId, "SMS", recipients.length)`.

### 3.7 Send Voice

```bash
curl -X POST https://es.ekddigital.com/api/v1/send \
  -H "Authorization: Bearer ek_live_your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "voice",
    "to": "+1234567890",
    "body": "Hello, this is an automated call from ACME Corp. Your appointment is confirmed for tomorrow at 3 PM."
  }'
```

Voice messages are queued via `queueVoice` and stored with `channel: "VOICE"` in the `message` table. Extra call details (duration, callerId, audioUrl) are stored in `headers` and exposed in the `/messages/[id]` endpoint.

---

## 4. Message Search & History

The Messages API gives you a unified view of all email/SMS/voice activity.

### 4.1 List Messages

**Endpoint:**

```http
GET /api/v1/messages
```

**Query Parameters (all optional):**

| Name        | Type     | Description                                                             |
| ----------- | -------- | ----------------------------------------------------------------------- |
| `channel`   | string   | `email` \| `sms` \| `voice`                                             |
| `direction` | string   | `inbound` \| `outbound`                                                 |
| `status`    | string   | `queued` \| `sending` \| `sent` \| `delivered` \| `failed` \| `bounced` |
| `from`      | string   | Partial match on sender                                                 |
| `to`        | string   | Exact match in recipient array                                          |
| `startDate` | ISO date | Filter `createdAt >=`                                                   |
| `endDate`   | ISO date | Filter `createdAt <=`                                                   |
| `search`    | string   | Searches subject, text body, and from                                   |
| `page`      | number   | Default `1`                                                             |
| `limit`     | number   | Default `50`, max `100`                                                 |
| `sortBy`    | string   | One of: `createdAt`, `queuedAt`, `sentAt`, `deliveredAt`                |
| `sortOrder` | string   | `asc` or `desc` (default)                                               |

**Example:**

```bash
curl -X GET 'https://es.ekddigital.com/api/v1/messages?channel=email&status=delivered&page=1&limit=20' \
  -H "Authorization: Bearer ek_live_your_api_key"
```

**Response Shape (simplified):**

```json
{
  "success": true,
  "data": {
    "messages": [
      {
        "id": "msg_123",
        "channel": "email",
        "direction": "outbound",
        "status": "DELIVERED",
        "from": "no-reply@yourapp.com",
        "to": ["user@example.com"],
        "subject": "Welcome",
        "preview": "Welcome to our platform...",
        "queuedAt": "2025-11-26T14:30:00.000Z",
        "sentAt": "2025-11-26T14:30:02.000Z",
        "deliveredAt": "2025-11-26T14:30:03.000Z",
        "error": null,
        "providerId": "ses-123456",
        "createdAt": "2025-11-26T14:29:59.000Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 1,
      "totalPages": 1,
      "hasMore": false
    },
    "stats": {
      "email": { "sent": 10, "delivered": 9, "failed": 1, "total": 10 },
      "sms": { "sent": 5, "delivered": 5, "failed": 0, "total": 5 },
      "voice": { "sent": 2, "delivered": 2, "failed": 0, "total": 2 }
    },
    "filters": {
      "applied": { "channel": "EMAIL", "status": "DELIVERED" },
      "available": {
        "channels": ["email", "sms", "voice"],
        "directions": ["inbound", "outbound"],
        "statuses": [
          "queued",
          "sending",
          "sent",
          "delivered",
          "failed",
          "bounced"
        ]
      }
    }
  }
}
```

### 4.2 Get a Single Message

**Endpoint:**

```http
GET /api/v1/messages/{id}
```

```bash
curl -X GET https://es.ekddigital.com/api/v1/messages/msg_123 \
  -H "Authorization: Bearer ek_live_your_api_key"
```

**Response (simplified):**

```json
{
  "success": true,
  "data": {
    "id": "msg_123",
    "channel": "email",
    "direction": "outbound",
    "status": "DELIVERED",
    "from": "no-reply@yourapp.com",
    "to": ["user@example.com"],
    "subject": "Welcome",
    "textBody": "Welcome to our platform...",
    "htmlBody": "<h1>Welcome</h1>...",
    "headers": { "x-provider-message-id": "ses-123456" },
    "templateVars": { "name": "John" },
    "template": { "id": "tpl_welcome", "name": "Welcome", "channel": "EMAIL" },
    "providerId": "ses-123456",
    "providerResponse": "...raw provider payload...",
    "error": null,
    "timestamps": {
      "created": "2025-11-26T14:29:59.000Z",
      "queued": "2025-11-26T14:30:00.000Z",
      "sent": "2025-11-26T14:30:02.000Z",
      "delivered": "2025-11-26T14:30:03.000Z",
      "bounced": null,
      "complained": null
    },
    "callDetails": null,
    "smsDetails": null
  }
}
```

For `channel === "VOICE"`, `callDetails` is populated from message headers:

```json
"callDetails": {
  "duration": 35,
  "callerId": "+15551230000",
  "audioUrl": "https://.../recording.mp3"
}
```

For `channel === "SMS"`, `smsDetails.segments` estimates the number of SMS segments.

If the message does not belong to the authenticated customer or does not exist, the API returns `404 Message not found`.

---

## 5. Sandbox Email Inbox

The sandbox endpoints allow you to test email flows **without sending real email**.

These endpoints are backed by `mailSink` in `src/lib/utils/sandbox/mailSink.ts` and are only available for authenticated customers.

### 5.1 List Sandbox Emails

**Endpoint:**

```http
GET /api/v1/sandbox/emails
```

**Query Parameters:**

| Name    | Type   | Description                        |
| ------- | ------ | ---------------------------------- |
| `limit` | number | Max emails to return (default: 50) |

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
      "createdAt": "2025-11-26T14:30:00.000Z"
    }
  ],
  "count": 1,
  "sandbox": true
}
```

### 5.2 Clear Sandbox Emails

**Endpoint:**

```http
DELETE /api/v1/sandbox/emails
```

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

## 6. Rate Limiting & Quotas

The `/send` endpoint applies both **rate limits** and **monthly/plan quotas**.

### 6.1 Rate Limits

Configured via `RATE_LIMITS["send:basic"]` and enforced per API key using `checkRateLimit`.

On every `/send` response, rate limit headers are added:

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1732631400
```

If you exceed the limit, you get a `429` with a `RATE_LIMITED` error.

### 6.2 Quotas

Quotas are enforced per customer and per channel via `enforceQuota(customerId, channel, count)`.

Typical channels:

- `"EMAIL"`
- `"SMS"`
- `"VOICE"`

If a quota is exceeded, the API returns an error similar to:

```json
{
  "error": {
    "message": "Monthly email quota exceeded",
    "code": "QUOTA_EXCEEDED"
  }
}
```

---

## 7. Error Model

All errors are normalized via `handleApiError` in `src/lib/utils/api/errors.ts`.

### 7.1 Validation Errors

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

### 7.2 Authentication & Scope Errors

```json
{
  "error": {
    "message": "Invalid or missing API key",
    "code": "UNAUTHORIZED"
  }
}
```

```json
{
  "error": {
    "message": "API key does not have required scope: send:email",
    "code": "FORBIDDEN"
  }
}
```

### 7.3 Rate Limit Errors

```json
{
  "error": {
    "message": "Rate limit exceeded. Try again later.",
    "code": "RATE_LIMITED"
  }
}
```

### 7.4 Generic Server Errors

```json
{
  "error": {
    "message": "Internal server error",
    "code": "INTERNAL_ERROR"
  }
}
```

---

## 8. Language Examples

The payloads shown above can be used from any HTTP client. Here are short examples for Node.js and Python.

### 8.1 Node.js (fetch)

```ts
async function sendEmail() {
  const res = await fetch("https://es.ekddigital.com/api/v1/send", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${process.env.EKDSEND_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      type: "email",
      to: "user@example.com",
      subject: "Hello from Node.js",
      body: "<h1>It works!</h1>",
    }),
  });

  const data = await res.json();
  if (data.success) {
    console.log("Queued message:", data.messageId);
  } else {
    console.error("Error:", data.error?.message || data.error);
  }
}
```

### 8.2 Python (requests)

```python
import os
import requests


def send_email(to: str, subject: str, body: str) -> str:
    resp = requests.post(
        "https://es.ekddigital.com/api/v1/send",
        headers={
            "Authorization": f"Bearer {os.environ['EKDSEND_API_KEY']}",
            "Content-Type": "application/json",
        },
        json={
            "type": "email",
            "to": to,
            "subject": subject,
            "body": body,
        },
        timeout=10,
    )

    data = resp.json()
    if data.get("success"):
        return data["messageId"]
    raise RuntimeError(data.get("error", {}).get("message", "Unknown error"))
```

---

## 9. Summary

- Use **`POST /api/v1/send`** for all outbound channels (email, SMS, voice).
- Use **`GET /api/v1/messages`** and **`GET /api/v1/messages/{id}`** to search and inspect activity.
- Use **sandbox endpoints** to safely test email flows.
- Respect **scopes, rate limits, and quotas** to keep your integration reliable.

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
