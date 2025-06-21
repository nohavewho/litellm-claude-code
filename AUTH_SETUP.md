# Authentication Setup for LiteLLM Claude Code Provider

This guide explains how to authenticate the Claude CLI within the Docker container.

## Overview

The LiteLLM Claude Code Provider requires Claude CLI authentication to work. We've integrated the authentication flow directly into the LiteLLM web interface for a seamless experience.

## First-Time Setup

### 1. Start the Container

```bash
docker-compose up -d
```

### 2. Access the Authentication Page

Open your browser and navigate to:
```
http://localhost:4000/auth
```

### 3. Check Authentication Status

The page will show whether you're currently authenticated. If not authenticated, you'll see:
- A red status box indicating "Not authenticated"
- A "Start Authentication" button

### 4. Start Authentication

Click the "Start Authentication" button. This will:
- Start the Claude CLI authentication process
- Show a terminal window with the CLI output
- Display the OAuth URL when it appears

### 5. Complete OAuth Flow

1. Click the OAuth URL that appears (or copy and paste it into a new tab)
2. Sign in to your Claude account
3. Authorize the application
4. The browser will redirect to a callback URL (this may show an error page - that's normal)
5. Return to the authentication page

### 6. Verify Success

Once authentication is complete:
- The status will turn green showing "Authenticated successfully!"
- You can now use all API endpoints
- Authentication persists across container restarts

## Using the API

After authentication, you can:

1. **Access API Documentation**: http://localhost:4000/docs
2. **Make API Calls**:
   ```bash
   curl -X POST http://localhost:4000/v1/chat/completions \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer sk-1234" \
     -d '{
       "model": "sonnet",
       "messages": [{"role": "user", "content": "Hello Claude!"}]
     }'
   ```

## Persistence

- Authentication credentials are stored in a Docker volume named `claude-auth`
- Credentials persist across container restarts
- To reset authentication, remove the volume: `docker volume rm litellm-claude_claude-auth`

## Troubleshooting

### WebSocket Connection Failed
- Ensure you're accessing the page via HTTP (not HTTPS)
- Check that port 4000 is accessible
- Try refreshing the page

### Authentication Stuck
- The Claude CLI may be waiting for input
- Try restarting the container and retrying
- Check container logs: `docker-compose logs litellm`

### OAuth Page Shows Error
- This is normal - the CLI handles the callback internally
- Return to the authentication page to check status

## Security Notes

- Never expose port 4000 to the public internet without proper security
- The Bearer token (sk-1234) is for local development only
- For production, implement proper API key management in LiteLLM

## Available Models

Once authenticated, you can use:
- `sonnet` - Claude Sonnet (latest)
- `opus` - Claude Opus (latest)
- `default` - Default model

Note: Haiku model is currently disabled upstream in Claude Code.