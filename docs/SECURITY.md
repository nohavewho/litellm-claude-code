# Security Best Practices

## Critical Security Requirement

**The LITELLM_MASTER_KEY is REQUIRED and protects access to your authenticated Claude instance.** Since the Claude OAuth provides real API access, anyone with the master key can use your Claude authentication. There is no default key - you must set one.

## Master Key Configuration

### Why It's Required

The LiteLLM master key serves as the authentication barrier between the public API and your private Claude OAuth credentials. Without it, anyone could access your authenticated Claude instance.

### Setting Up Your Key

1. **Generate a secure key:**
   ```bash
   # Using OpenSSL (recommended)
   openssl rand -hex 32
   
   # Using Python
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

2. **Configuration methods:**
   
   **For Production** (Environment Variable - Recommended)
   ```bash
   LITELLM_MASTER_KEY="your-secure-key-here" docker-compose up -d
   ```
   
   **For Development** (.env File)
   ```bash
   cp .env.example .env
   # Edit .env and replace 'your-secret-key-here' with your actual key
   docker-compose up -d
   ```

3. **The system will not start without a key**
   - No fallback or default keys are provided
   - This is intentional for security

## Best Practices

1. **Never commit secrets** - Always use `.env.example` as a template
2. **Use strong keys** - At least 32 bytes of randomness
3. **Rotate keys regularly** - Especially if exposed
4. **Use HTTPS in production** - Protect the API key in transit
5. **Limit access** - Use firewall rules to restrict who can access the API

## Authentication Flow

This system uses OAuth for Claude authentication (stored in Docker volume) and API keys for LiteLLM access. The two are separate:

- **Claude OAuth**: Handled via `claude-auth` Docker volume, persists across restarts
- **LiteLLM API Key**: Set via `LITELLM_MASTER_KEY`, used in `Authorization: Bearer <key>` headers

## Checking Current Configuration

To verify your security setup:

```bash
# Check if custom key is set (should not show default)
docker-compose exec litellm env | grep LITELLM_MASTER_KEY

# Check startup logs for warnings
docker-compose logs litellm | grep "WARNING"
```