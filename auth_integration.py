"""
Authentication integration for LiteLLM proxy server.
Adds Claude CLI authentication UI directly to the LiteLLM interface.
"""

import os
import asyncio
import subprocess
import json
import pty
import select
import fcntl
from pathlib import Path
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
import aiofiles

# HTML template for authentication page with xterm.js
AUTH_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Claude Authentication - LiteLLM</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/xterm@5.3.0/css/xterm.css" />
    <script src="https://cdn.jsdelivr.net/npm/xterm@5.3.0/lib/xterm.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/xterm-addon-fit@0.8.0/lib/xterm-addon-fit.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/xterm-addon-web-links@0.9.0/lib/xterm-addon-web-links.js"></script>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            max-width: 900px;
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
        #terminal-container {
            padding: 1rem;
            background: #000;
            border-radius: 4px;
            display: none;
            margin-top: 1rem;
        }
        #terminal-container.active {
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
    </style>
</head>
<body>
    <div class="container">
        <h1>Claude Authentication</h1>
        
        <div id="status" class="status">
            Checking authentication status...
        </div>
        
        <button id="auth-btn" onclick="startAuth()" disabled>
            Start Authentication
        </button>
        
        <button onclick="window.location='/docs'">
            Back to API Documentation
        </button>
        
        <div id="terminal-container">
            <div id="terminal"></div>
        </div>
    </div>
    
    <script>
        let ws = null;
        let term = null;
        let fitAddon = null;
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
        
        function startAuth() {
            if (isAuthenticating) return;
            
            isAuthenticating = true;
            const terminalContainer = document.getElementById('terminal-container');
            const authBtn = document.getElementById('auth-btn');
            
            terminalContainer.className = 'active';
            authBtn.disabled = true;
            authBtn.textContent = 'Authenticating...';
            
            // Initialize xterm.js
            if (!term) {
                term = new Terminal({
                    cursorBlink: true,
                    fontSize: 14,
                    fontFamily: 'Consolas, "Liberation Mono", Menlo, Courier, monospace',
                    theme: {
                        background: '#1e1e1e',
                        foreground: '#d4d4d4'
                    }
                });
                
                fitAddon = new FitAddon.FitAddon();
                const webLinksAddon = new WebLinksAddon.WebLinksAddon();
                
                term.loadAddon(fitAddon);
                term.loadAddon(webLinksAddon);
                
                term.open(document.getElementById('terminal'));
                fitAddon.fit();
                
                // Handle window resize
                window.addEventListener('resize', () => {
                    fitAddon.fit();
                });
            }
            
            term.clear();
            term.writeln('Starting Claude authentication...');
            
            // Connect WebSocket - use wss:// for HTTPS, ws:// for HTTP
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(`${protocol}//${window.location.host}/auth/ws`);
            
            ws.onopen = () => {
                ws.send(JSON.stringify({action: 'start'}));
                
                // Handle terminal input
                term.onData(data => {
                    if (ws && ws.readyState === WebSocket.OPEN) {
                        ws.send(JSON.stringify({
                            type: 'input',
                            text: data
                        }));
                    }
                });
            };
            
            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                
                if (data.type === 'output') {
                    term.write(data.text);
                } else if (data.type === 'complete') {
                    term.writeln('\\r\\nAuthentication complete!');
                    isAuthenticating = false;
                    setTimeout(() => checkAuthStatus(), 1000);
                } else if (data.type === 'error') {
                    term.writeln(`\\r\\nError: ${data.message}`);
                    isAuthenticating = false;
                    authBtn.disabled = false;
                    authBtn.textContent = 'Retry Authentication';
                }
            };
            
            ws.onclose = () => {
                if (isAuthenticating) {
                    term.writeln('\\r\\nConnection closed unexpectedly.');
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
        
        master_fd = None
        slave_fd = None
        
        try:
            # Wait for start signal
            data = await websocket.receive_json()
            if data.get("action") != "start":
                return
            
            # Create a pseudo-terminal
            master_fd, slave_fd = pty.openpty()
            
            # Set terminal to non-blocking mode
            flags = fcntl.fcntl(master_fd, fcntl.F_GETFL)
            fcntl.fcntl(master_fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
            
            # Start Claude CLI with the PTY
            process = await asyncio.create_subprocess_exec(
                "claude",
                stdin=slave_fd,
                stdout=slave_fd,
                stderr=slave_fd,
                env={**os.environ, "TERM": "xterm-256color"}
            )
            
            # Close slave_fd in parent process
            os.close(slave_fd)
            slave_fd = None
            
            # Main loop to handle output and input
            while True:
                # Check for output from PTY
                try:
                    output = os.read(master_fd, 4096)
                    if output:
                        await websocket.send_json({
                            "type": "output",
                            "text": output.decode('utf-8', errors='replace')
                        })
                        
                        # Check for completion
                        if b"authenticated" in output.lower() or b"success" in output.lower():
                            await websocket.send_json({"type": "complete"})
                            break
                except OSError:
                    await asyncio.sleep(0.01)
                
                # Check for input from WebSocket
                try:
                    data = await asyncio.wait_for(websocket.receive_json(), timeout=0.01)
                    if data.get("type") == "input":
                        input_text = data.get("text", "")
                        if input_text:
                            os.write(master_fd, input_text.encode())
                except asyncio.TimeoutError:
                    pass
                except WebSocketDisconnect:
                    break
                
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
            # Cleanup
            if master_fd is not None:
                try:
                    os.close(master_fd)
                except:
                    pass
            if slave_fd is not None:
                try:
                    os.close(slave_fd)
                except:
                    pass
            if process and process.returncode is None:
                try:
                    process.terminate()
                    await process.wait()
                except:
                    pass
    
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