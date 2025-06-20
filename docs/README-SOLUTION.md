# LiteLLM-Claude Integration Solution

This integration enables Claude Code SDK to work with LiteLLM, providing an OpenAI-compatible API endpoint for Claude models.

## How It Works

1. **Custom Provider**: `claude_code_provider.py` implements a LiteLLM CustomLLM class that:
   - Receives requests from LiteLLM
   - Calls Claude Code SDK with the appropriate model
   - Formats responses in LiteLLM's expected format

2. **Provider Registration**: The provider is registered via the YAML config's `custom_provider_map`

3. **Dependencies**: Requires Node.js and `@anthropic-ai/claude-code` CLI installed in the container

## Available Models

- `sonnet` - Claude Sonnet 4
- `claude-3-5-haiku-20240307` - Claude 3.5 Haiku
- `opus` - Claude Opus 4
- `default` - Default model (Opus 4 with automatic Sonnet 4 fallback)

## Usage

Start the service:
```bash
docker compose up -d
```

Test the API:
```bash
# List models
curl http://localhost:4000/v1/models -H "Authorization: Bearer sk-1234"

# Chat completion
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-1234" \
  -d '{
    "model": "claude-3-5-sonnet-20241022",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

## Key Files

- `claude_code_provider.py`: Custom LiteLLM provider implementation
- `custom_handler.py`: Module that exposes the provider instance for YAML config
- `config/litellm_config.yaml`: LiteLLM configuration with model list and custom provider map
- `Dockerfile`: Installs Node.js, Claude Code CLI, and Python dependencies

## Authentication

The Claude Code SDK uses OAuth authentication:

1. Access the container: `docker exec -it litellm-claude-litellm-1 bash`
2. Login to Claude: `claude-auth login` (this will open a browser for OAuth)
3. The authentication persists in the container until it's removed

The provider automatically uses OAuth when no `ANTHROPIC_API_KEY` is set.

## Notes

- OAuth authentication is required for Claude Code access
- The integration provides OpenAI-compatible endpoints that Graphiti can use
- All Claude models are accessible through standard OpenAI client libraries
- Response times may be longer due to the OAuth layer
- The authentication tokens are stored in `/root/.claude.json` in the container