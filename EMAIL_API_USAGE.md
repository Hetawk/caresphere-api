# EKDSend Email API - Usage Guide

> Send emails, SMS, and voice messages via a simple REST API. Built for developers.

## Quick Start

**Base URL:** `https://es.ekddigital.com/api/v1`

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

---

## 1. Getting Your API Key

### Option A: Via Dashboard

1. Login to [es.ekddigital.com](https://es.ekddigital.com)
2. Go to **Settings** → **API Keys**
3. Click **Create New Key**
4. Choose scopes: `send:email`, `send:sms`, `send:voice`
5. **Save the key immediately** - it's only shown once!

### Option B: Via API (if you already have a key)

```bash
# Create a new API key
curl -X POST https://es.ekddigital.com/api/v1/api-keys \
  -H "Authorization: Bearer ek_live_existing_key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Production Email Key",
    "scopes": ["send:email", "send:sms"],
    "expiresInDays": 365
  }'
```

**Response:**

```json
{
  "message": "API key created successfully",
  "apiKey": {
    "id": "clxyz123",
    "name": "Production Email Key",
    "key": "ek_live_abc123xyz789...",
    "scopes": ["send:email", "send:sms"],
    "expiresAt": "2026-11-26T00:00:00.000Z"
  },
  "warning": "⚠️ Save this key securely. It will not be shown again."
}
```

---

## 2. Send Email

### Basic Email

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

### Multiple Recipients

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

### With CC, BCC, and Reply-To

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

### Custom From Address

```bash
curl -X POST https://es.ekddigital.com/api/v1/send \
  -H "Authorization: Bearer ek_live_your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "email",
    "to": "customer@example.com",
    "from": "sales@yourdomain.com",
    "subject": "Your Quote Request",
    "body": "Thank you for your interest..."
  }'
```

> **Note:** Custom `from` addresses require a verified domain.

---

## 3. Send SMS

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

### Multiple SMS Recipients

```bash
curl -X POST https://es.ekddigital.com/api/v1/send \
  -H "Authorization: Bearer ek_live_your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "sms",
    "to": ["+1234567890", "+0987654321"],
    "body": "Flash sale! 50% off all items today only."
  }'
```

---

## 4. Send Voice Call

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

---

## 5. Using Templates

### Built-in Templates

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

### Available Built-in Templates

| Template Name    | Description          | Variables                            |
| ---------------- | -------------------- | ------------------------------------ |
| `welcome`        | Welcome email        | `name`, `company`                    |
| `verification`   | Email verification   | `name`, `verificationUrl`            |
| `password-reset` | Password reset       | `name`, `resetUrl`                   |
| `invoice`        | Invoice notification | `invoiceNumber`, `amount`, `dueDate` |

---

## 6. Response Format

### Success Response (202 Accepted)

```json
{
  "success": true,
  "messageId": "clxyz123abc456",
  "type": "email",
  "queuedAt": "2025-11-26T14:30:00.000Z"
}
```

### Error Response

```json
{
  "error": {
    "message": "Invalid email address: bad-email",
    "code": "VALIDATION_ERROR"
  }
}
```

### Common Error Codes

| Code               | HTTP Status | Description                |
| ------------------ | ----------- | -------------------------- |
| `VALIDATION_ERROR` | 400         | Invalid request data       |
| `UNAUTHORIZED`     | 401         | Invalid or missing API key |
| `FORBIDDEN`        | 403         | Insufficient scopes        |
| `RATE_LIMITED`     | 429         | Too many requests          |
| `QUOTA_EXCEEDED`   | 402         | Monthly quota exceeded     |
| `INTERNAL_ERROR`   | 500         | Server error               |

---

## 7. Rate Limits

| Plan       | Requests/min | Emails/month |
| ---------- | ------------ | ------------ |
| Starter    | 60           | 10,000       |
| Pro        | 300          | 100,000      |
| Enterprise | 1000         | Unlimited    |

Rate limit headers are included in every response:

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1732631400
```

---

## 8. Code Examples

### JavaScript/TypeScript (Node.js)

```typescript
const sendEmail = async () => {
  const response = await fetch("https://es.ekddigital.com/api/v1/send", {
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

  const result = await response.json();

  if (result.success) {
    console.log("Email queued:", result.messageId);
  } else {
    console.error("Failed:", result.error.message);
  }
};
```

### Python

```python
import requests
import os

def send_email(to, subject, body):
    response = requests.post(
        'https://es.ekddigital.com/api/v1/send',
        headers={
            'Authorization': f'Bearer {os.environ["EKDSEND_API_KEY"]}',
            'Content-Type': 'application/json',
        },
        json={
            'type': 'email',
            'to': to,
            'subject': subject,
            'body': body,
        }
    )

    result = response.json()

    if result.get('success'):
        print(f'Email queued: {result["messageId"]}')
        return result['messageId']
    else:
        raise Exception(result['error']['message'])

# Usage
send_email('user@example.com', 'Hello from Python', '<h1>It works!</h1>')
```

### PHP

```php
<?php

function sendEmail($to, $subject, $body) {
    $apiKey = getenv('EKDSEND_API_KEY');

    $ch = curl_init('https://es.ekddigital.com/api/v1/send');

    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_POST => true,
        CURLOPT_HTTPHEADER => [
            'Authorization: Bearer ' . $apiKey,
            'Content-Type: application/json',
        ],
        CURLOPT_POSTFIELDS => json_encode([
            'type' => 'email',
            'to' => $to,
            'subject' => $subject,
            'body' => $body,
        ]),
    ]);

    $response = curl_exec($ch);
    $result = json_decode($response, true);

    curl_close($ch);

    if ($result['success']) {
        echo "Email queued: " . $result['messageId'];
        return $result['messageId'];
    } else {
        throw new Exception($result['error']['message']);
    }
}

// Usage
sendEmail('user@example.com', 'Hello from PHP', '<h1>It works!</h1>');
```

### Go

```go
package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "net/http"
    "os"
)

type SendRequest struct {
    Type    string `json:"type"`
    To      string `json:"to"`
    Subject string `json:"subject"`
    Body    string `json:"body"`
}

type SendResponse struct {
    Success   bool   `json:"success"`
    MessageID string `json:"messageId"`
    Error     struct {
        Message string `json:"message"`
    } `json:"error"`
}

func sendEmail(to, subject, body string) (string, error) {
    apiKey := os.Getenv("EKDSEND_API_KEY")

    payload := SendRequest{
        Type:    "email",
        To:      to,
        Subject: subject,
        Body:    body,
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
```

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
```

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
