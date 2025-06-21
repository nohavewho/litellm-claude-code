"""
Authentication integration for LiteLLM proxy server.
Adds Claude CLI authentication UI directly to the LiteLLM interface.
"""

import os
import asyncio
import subprocess
import json
from pathlib import Path
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
import aiofiles

# HTML template for authentication page
AUTH_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Claude Authentication - LiteLLM</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
            background: #f5f5f5;
        }
        .container {
            background: white;
            border-radius: 8px;
            padding: 2rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            margin-bottom: 1rem;
        }
        .status {
            padding: 1rem;
            border-radius: 4px;
            margin-bottom: 1rem;
        }
        .status.authenticated {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .status.unauthenticated {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .terminal {
            background: #1e1e1e;
            color: #d4d4d4;
            padding: 1rem;
            border-radius: 4px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 14px;
            height: 400px;
            overflow-y: auto;
            display: none;
        }
        .terminal.active {
            display: block;
        }
        button {
            background: #007bff;
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 4px;
            font-size: 16px;
            cursor: pointer;
            margin-right: 1rem;
        }
        button:hover {
            background: #0056b3;
        }
        button:disabled {
            background: #6c757d;
            cursor: not-allowed;
        }
        .oauth-link {
            display: none;
            padding: 1rem;
            background: #e7f3ff;
            border: 1px solid #b3d9ff;
            border-radius: 4px;
            margin: 1rem 0;
        }
        .oauth-link a {
            color: #004085;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Claude Authentication</h1>
        
        <div id="status" class="status">
            Checking authentication status...
        </div>
        
        <div id="oauth-link" class="oauth-link">
            <p>Please visit the following URL to authenticate:</p>
            <a id="oauth-url" href="#" target="_blank"></a>
        </div>
        
        <button id="auth-btn" onclick="startAuth()" disabled>
            Start Authentication
        </button>
        
        <button onclick="window.location='/docs'">
            Back to API Documentation
        </button>
        
        <div id="terminal" class="terminal"></div>
    </div>
    
    <script>
        let ws = null;
        let isAuthenticating = false;
        
        async function checkAuthStatus() {
            try {
                const response = await fetch('/auth/status');
                const data = await response.json();
                updateStatus(data.authenticated);
                return data.authenticated;
            } catch (e) {
                console.error('Failed to check auth status:', e);
                return false;
            }
        }
        
        function updateStatus(authenticated) {
            const statusEl = document.getElementById('status');
            const authBtn = document.getElementById('auth-btn');
            
            if (authenticated) {
                statusEl.className = 'status authenticated';
                statusEl.textContent = 'Authenticated successfully! You can now use the API.';
                authBtn.disabled = true;
                authBtn.textContent = 'Already Authenticated';
            } else {
                statusEl.className = 'status unauthenticated';
                statusEl.textContent = 'Not authenticated. Please click the button below to authenticate.';
                authBtn.disabled = false;
                authBtn.textContent = 'Start Authentication';
            }
        }
        
        function addTerminalLine(text) {
            const terminal = document.getElementById('terminal');
            const line = document.createElement('div');
            line.textContent = text;
            terminal.appendChild(line);
            terminal.scrollTop = terminal.scrollHeight;
        }
        
        function startAuth() {
            if (isAuthenticating) return;
            
            isAuthenticating = true;
            const terminal = document.getElementById('terminal');
            const authBtn = document.getElementById('auth-btn');
            
            terminal.className = 'terminal active';
            terminal.innerHTML = '';
            authBtn.disabled = true;
            authBtn.textContent = 'Authenticating...';
            
            // Connect WebSocket
            ws = new WebSocket(`ws://${window.location.host}/auth/ws`);
            
            ws.onopen = () => {
                addTerminalLine('Starting Claude authentication...');
                ws.send(JSON.stringify({action: 'start'}));
            };
            
            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                
                if (data.type === 'output') {
                    addTerminalLine(data.text);
                    
                    // Check for OAuth URL
                    const urlMatch = data.text.match(/https:\/\/[^\s]+/);
                    if (urlMatch && data.text.includes('authenticate')) {
                        const oauthLink = document.getElementById('oauth-link');
                        const oauthUrl = document.getElementById('oauth-url');
                        oauthLink.style.display = 'block';
                        oauthUrl.href = urlMatch[0];
                        oauthUrl.textContent = urlMatch[0];
                    }
                } else if (data.type === 'complete') {
                    addTerminalLine('\\nAuthentication complete!');
                    isAuthenticating = false;
                    setTimeout(() => checkAuthStatus(), 1000);
                } else if (data.type === 'error') {
                    addTerminalLine(`\\nError: ${data.message}`);
                    isAuthenticating = false;
                    authBtn.disabled = false;
                    authBtn.textContent = 'Retry Authentication';
                }
            };
            
            ws.onclose = () => {
                if (isAuthenticating) {
                    addTerminalLine('\\nConnection closed unexpectedly.');
                    isAuthenticating = false;
                    authBtn.disabled = false;
                    authBtn.textContent = 'Retry Authentication';
                }
            };
        }
        
        // Check auth status on load
        checkAuthStatus();
    </script>
</body>
</html>
"""

def add_auth_routes(app):
    """Add authentication routes to the LiteLLM FastAPI app."""
    
    @app.get("/auth")
    async def auth_page():
        """Serve the authentication UI."""
        return HTMLResponse(content=AUTH_HTML)
    
    @app.get("/auth/status")
    async def auth_status():
        """Check if Claude CLI is authenticated."""
        creds_path = Path("/root/.claude/.credentials.json")
        authenticated = creds_path.exists() and creds_path.stat().st_size > 0
        return JSONResponse({"authenticated": authenticated})
    
    @app.websocket("/auth/ws")
    async def websocket_endpoint(websocket: WebSocket):
        """Handle interactive Claude CLI authentication via WebSocket."""
        await websocket.accept()
        
        try:
            # Wait for start signal
            data = await websocket.receive_json()
            if data.get("action") != "start":
                return
            
            # Start Claude CLI in interactive mode
            process = await asyncio.create_subprocess_exec(
                "claude",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                env={**os.environ, "TERM": "xterm"}
            )
            
            # Read output in real-time
            while True:
                # Check if process has output
                try:
                    line = await asyncio.wait_for(
                        process.stdout.readline(), 
                        timeout=0.1
                    )
                    if line:
                        text = line.decode('utf-8', errors='replace')
                        await websocket.send_json({
                            "type": "output",
                            "text": text.rstrip()
                        })
                        
                        # Check for completion
                        if "success" in text.lower() or "authenticated" in text.lower():
                            await asyncio.sleep(2)  # Let it finish
                            await websocket.send_json({"type": "complete"})
                            break
                except asyncio.TimeoutError:
                    pass
                
                # Check if process ended
                if process.returncode is not None:
                    if process.returncode == 0:
                        await websocket.send_json({"type": "complete"})
                    else:
                        await websocket.send_json({
                            "type": "error",
                            "message": f"Process exited with code {process.returncode}"
                        })
                    break
                
        except WebSocketDisconnect:
            pass
        except Exception as e:
            await websocket.send_json({
                "type": "error",
                "message": str(e)
            })
        finally:
            if process and process.returncode is None:
                process.terminate()
                await process.wait()
    
    # Add a note in the main docs
    original_description = app.description or ""
    app.description = f"""
{original_description}

### Authentication Required

This LiteLLM instance uses Claude Code which requires authentication.

**First-time setup:**
1. Visit [/auth](/auth) to authenticate with Claude
2. Follow the OAuth flow in your browser
3. Once authenticated, you can use all API endpoints

**Note:** Authentication persists across container restarts.
"""
    
    return app