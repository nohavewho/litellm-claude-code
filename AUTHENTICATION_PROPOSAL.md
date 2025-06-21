# Authentication Integration Proposal

## Current Situation
- LiteLLM uses FastAPI with Swagger UI at http://localhost:4000
- Claude CLI requires interactive OAuth authentication
- We have persistent auth storage via Docker volume `claude-auth`

## Proposed Solution: Authentication Sidecar

Create a lightweight FastAPI service that:

1. **Serves Authentication UI** (port 4001)
   - Simple web page matching LiteLLM's style
   - Shows current auth status
   - Provides "Authenticate" button

2. **Handles OAuth Flow**
   - Uses WebSockets to relay CLI output to browser
   - Captures OAuth URL from CLI output
   - Opens in iframe or new window
   - Monitors for completion

3. **Integration Options**

### Option A: Reverse Proxy Integration
```
nginx/traefik -> 
  /auth/* -> :4001 (auth service)
  /*      -> :4000 (litellm)
```

### Option B: Standalone Service
- Run alongside LiteLLM
- Link from LiteLLM's Swagger UI description
- Check auth status via health endpoint

### Option C: Custom Middleware
- Inject auth check into LiteLLM startup
- Redirect to auth service if not authenticated
- More invasive but better UX

## Technical Implementation

### 1. Auth Service (`auth_service.py`)
```python
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import asyncio
import pty
import os

app = FastAPI()

@app.get("/")
async def auth_page():
    return HTMLResponse(auth_html)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Handle interactive CLI auth via WebSocket
    pass

@app.get("/status")
async def auth_status():
    # Check if .credentials.json exists
    pass
```

### 2. Frontend (`auth.html`)
- Material UI or Bootstrap for consistency
- WebSocket connection for real-time CLI output
- OAuth URL detection and handling
- Success/failure feedback

### 3. Docker Integration
- Add auth service to docker-compose.yml
- Share `claude-auth` volume
- Expose port 4001

## Benefits
- Consistent UX with LiteLLM
- No modifications to core LiteLLM code
- Handles interactive auth gracefully
- One-time setup for users

## Next Steps
1. Create basic auth service
2. Implement WebSocket CLI relay
3. Design matching UI
4. Test OAuth flow
5. Integrate with docker-compose