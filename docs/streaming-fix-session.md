# Streaming Fix Session - 2025-06-21

## Context
This session focused on fixing a streaming error in the LiteLLM Claude Code Provider and debugging authentication issues.

## Streaming Error Fix

### Original Error
```
Error fetching response:Error: 500 data: {"error": {"message": "litellm.APIConnectionError: 'coroutine' object is not an iterator\nTraceback (most recent call last):\n  File "/usr/local/lib/python3.11/site-packages/litellm/litellm_core_utils/streaming_handler.py", line 1715, in anext\n    chunk = next(self.completion_stream)\n            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^\nTypeError: 'coroutine' object is not an iterator\n", "type": null, "param": null, "code": "500"}}
```

Later evolved to:
```
litellm.APIConnectionError: 'text'
KeyError: 'text'
```

### Root Cause
The ClaudeCodeSDKProvider class was missing streaming methods (`streaming` and `astreaming`). When LiteLLM tried to handle streaming requests, it expected an iterator but got a coroutine instead.

### Solution Implemented
Added streaming support to `claude_code_provider.py`:

1. Added imports:
   ```python
   from typing import Dict, List, Iterator, AsyncIterator, Any
   from litellm.types.utils import Choices, Message as LiteLLMMessage, GenericStreamingChunk, Delta
   ```

2. Implemented `streaming` method (raises NotImplementedError for sync streaming)

3. Implemented `astreaming` method that:
   - Yields chunks in the GenericStreamingChunk format expected by LiteLLM
   - Each chunk contains: `text`, `is_finished`, `finish_reason`, `index`, `tool_use`, `usage`
   - Sends a final chunk with `is_finished=True` and usage statistics

### Key Learning
LiteLLM expects streaming chunks in a specific format (GenericStreamingChunk) rather than the OpenAI-style format we initially tried.

## Authentication Issue

### Problem
After rebuilding the container for the streaming fix, authentication was lost despite having a persistent Docker volume.

### Investigation
1. Checked volume mount: `claude-auth:/root/.claude` - correctly configured
2. Found `/root/.claude/` directory exists but `/root/.claude/.credentials.json` is missing
3. The auth check in `auth_integration.py` looks for this specific file

### Root Cause
The credentials were not persisted in the volume. When the container was rebuilt, the authentication state was lost.

### Current State
- Volume is properly mounted
- Directory structure exists
- But credentials file is missing
- Need to re-authenticate using `docker exec -it litellm-claude-litellm-1 bash` then `claude`

## Web Authentication UI Status

### What Works
- Authentication status endpoint (`/auth/status`) correctly reports authentication state
- Web UI at `/auth` displays properly

### What Doesn't Work
- Interactive authentication flow through web UI hangs
- Issue with PTY handling for interactive OAuth flow
- Documented in AUTH_SETUP.md to use CLI method instead

## Branch Information
- Working on `stream-fix` branch
- Contains all commits from main including OAuth Docker fixes
- Need to merge streaming fix back to main once authentication is restored and streaming is tested

## Next Steps
1. Re-authenticate in the container
2. Test streaming functionality
3. Ensure both streaming and non-streaming requests work
4. Merge `stream-fix` branch to main
5. Consider improving web auth UI (lower priority)

## Files Modified
- `/home/andrew/litellm-claude/claude_code_provider.py` - Added streaming implementation
- `/home/andrew/litellm-claude/AUTH_SETUP.md` - Updated with web auth limitations