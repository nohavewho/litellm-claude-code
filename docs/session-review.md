# Session Review: LiteLLM Claude Provider Streaming Debug

## BE SKEPTICAL OF THESE CLAIMS

### These are notes from an incomplete and untested debug session. View all of this as points of exploration, not authoritative discoveries

## Initial Problems

1. **Streaming Error**: `'coroutine' object is not an iterator` - The streaming functionality was throwing an error when trying to handle async streaming responses.

2. **Duplicate Files**: Multiple copies of `claude_code_provider.py` existed in different directories (root, `/config/`, `/providers/`), unclear which were necessary.

3. **Image Support**: Untested/unknown if image handling works.

## Current State

### Authentication Issue
- OAuth authentication via `claude` CLI is successful and stored in `/root/.claude/.credentials.json`
- However, the Claude Code SDK expects tokens in `/root/.claude_code/tokens.json` format
- When SDK doesn't find its expected auth format, it tries to start OAuth flow on port 54545
- This causes "port already in use" errors because multiple requests trigger simultaneous OAuth attempts

### Key Theory
- `claude` (CLI) and `claude-auth` (SDK) use different authentication storage formats
- CLI stores credentials at `/root/.claude/.credentials.json` with key `claudeAiOauth`
- SDK expects tokens at `/root/.claude_code/tokens.json`
- The SDK's `query_with_oauth` function doesn't recognize CLI authentication

## Files Modified

### 1. `/providers/claude_code_provider.py` (and copies)
**Location**: Also copied to `/claude_code_provider.py` and `/config/claude_code_provider.py`

**Original Issues**:
- Missing streaming implementation
- Only had basic completion methods

**Changes Made**:
- Added `streaming()` and `astreaming()` methods
- Added imports: `GenericStreamingChunk`, `Iterator`, `AsyncIterator`
- Implemented streaming logic that converts async to sync
- Initially removed OAuth logic (replaced `query_with_oauth` with `query`) - this was a mistake
- Restored OAuth logic to use `query_with_oauth` when no API key present

**Current Implementation**:
```python
# Uses appropriate query function based on auth
if not os.environ.get('ANTHROPIC_API_KEY'):
    message_iterator = query_with_oauth(prompt=prompt, options=options)
else:
    message_iterator = query(prompt=prompt, options=options)
```

### 2. `docker-compose.yml`
**Changes**:
- Added persistent volume `claude_auth:/root/.claude_code` for SDK auth
- Temporarily added port 54545 mapping (removed later)
- Added host auth mounts as fallback (removed later for simplicity)
- Final state: Clean setup with just persistent volume

### 3. `Dockerfile`
**Changes**:
- Added `check_auth.py` copy (later removed)
- Final state: Back to original simple setup

### 4. `entrypoint.sh`
**Changes**:
- Added auth checking call (later removed)
- Final state: Simple Python path setup and startup.py execution

### 5. `config/litellm_config.yaml`
**Changes**:
- Changed `master_key: sk-1234` to `master_key: os.environ/LITELLM_MASTER_KEY`
- Made auth key configurable via environment variable

### 6. `.env`
- Already had `LITELLM_MASTER_KEY=sk-1234`
- No changes needed

### 7. New Files Created
- `.env.example` - Template without sensitive values
- `scripts/auth-container.sh` - Interactive auth script for container
- `CLAUDE.md` - Documentation for future Claude Code instances

### 8. Files Created Then Removed
- `check_auth.py` - Auth status checker (removed for simplicity)
- `oauth_manager.py` - Singleton OAuth manager (removed as overcomplicated)
- `scripts/docker-auth.sh` - Duplicate auth script

## Git Status
- Created private GitHub repo: https://github.com/cabinlab/litellm-claude
- Main branch has streaming implementation with OAuth
- Backup branch `backup-original-files` has original files without streaming

## Key Technical Issues

### 1. Authentication Mismatch
- Container has successful `claude` CLI authentication
- SDK doesn't recognize CLI auth format
- SDK tries to start new OAuth flow, causing port conflicts

### 2. Port 54545 Conflict
- OAuth callback server tries to bind to port 54545
- Multiple concurrent requests each try to start OAuth
- Results in "address already in use" errors

### 3. Streaming Implementation
- The streaming code itself appears correct
- It's blocked by authentication issues
- Once auth works, streaming should function

## Next Steps for Fresh Session

1. **Solve Authentication Format Issue**:
   - Option A: Find way to make SDK recognize CLI auth
   - Option B: Create converter from CLI format to SDK format
   - Option C: Use SDK's own `claude-auth login` command
   - Option D: Use API key authentication instead of OAuth

2. **Test Streaming**:
   - Once auth works, test streaming with curl
   - Verify chunk-by-chunk delivery
   - Test error handling

3. **Handle Multiple Requests**:
   - Implement singleton pattern for OAuth
   - Or use proper auth that doesn't require port binding

## Commands to Reproduce Current State

```bash
# Check auth status
docker exec litellm-claude-litellm-1 claude-auth status

# See auth files
docker exec litellm-claude-litellm-1 ls -la /root/.claude*

# Test streaming (currently fails with port error)
curl -N -X POST http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-1234" \
  -d '{"model": "sonnet", "messages": [{"role": "user", "content": "Hi"}], "stream": true}'
```

## Environment Details
- Docker container with Python 3.11, Node.js LTS
- Claude Code CLI installed via npm
- Claude Code SDK installed from GitHub
- PostgreSQL for LiteLLM state
- OAuth credentials stored in Docker volume `claude_auth`