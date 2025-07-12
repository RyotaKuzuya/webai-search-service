# WebAI API Endpoints for GitHub Actions

The WebAI API is now exposed through NGINX with HTTPS support. Below are the available endpoints:

## Base URL
`https://your-domain.com`

## Available API Endpoints

### 1. Simple API (Recommended for GitHub Actions)
Base path: `/api/simple/`

#### Health Check
- **GET** `/api/simple/health`
- Returns: `{"status": "healthy", "service": "simple-claude-api"}`

#### Chat
- **POST** `/api/simple/chat`
- Headers: `Content-Type: application/json`
- Body:
  ```json
  {
    "message": "Your message here",
    "model": "opus"  // optional, defaults to "opus"
  }
  ```
- Response:
  ```json
  {
    "id": "uuid",
    "message": "Response from Claude"
  }
  ```

#### Streaming Chat
- **POST** `/api/simple/chat/stream`
- Headers: `Content-Type: application/json`
- Body: Same as chat endpoint
- Response: Server-Sent Events stream

### 2. Session API (For Persistent Conversations)
Base path: `/api/session/`

#### Health Check
- **GET** `/api/session/health`
- Returns session information

#### Create Session
- **POST** `/api/session/create`
- Body:
  ```json
  {
    "model": "opus"  // optional
  }
  ```

#### Send Message
- **POST** `/api/session/chat`
- Body:
  ```json
  {
    "session_id": "your-session-id",
    "message": "Your message"
  }
  ```

### 3. Bridge API
Base path: `/api/bridge/`
- Used for WebSocket connections and advanced integrations

## GitHub Actions Example

```yaml
name: Claude Chat Example

on:
  workflow_dispatch:
    inputs:
      message:
        description: 'Message to send to Claude'
        required: true
        default: 'Hello, Claude!'

jobs:
  chat:
    runs-on: ubuntu-latest
    steps:
      - name: Send message to Claude
        run: |
          response=$(curl -X POST https://your-domain.com/api/simple/chat \
            -H "Content-Type: application/json" \
            -d "{\"message\": \"${{ github.event.inputs.message }}\"}" \
            -s)
          echo "Response: $response"
          echo "$response" | jq -r '.message'
```

## Configuration Details

- All endpoints support CORS for cross-origin requests
- Timeout is set to 30 minutes for long-running requests
- SSL/TLS is enforced with modern protocols (TLS 1.2+)
- The API automatically includes safety prompts to prevent server manipulation

## Security Notes

- The API is publicly accessible but includes safety measures
- All responses are in Japanese by default
- File system operations are blocked at the API level