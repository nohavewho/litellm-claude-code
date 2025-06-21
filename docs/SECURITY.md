# Security Best Practices

## Master Key Configuration

The LiteLLM master key is used to authenticate API requests. Here's how to handle it securely:

### Development
For local development, the system will use a default key `sk-development-only` if no key is provided. This is logged as a warning on startup.

### Production

1. **Generate a secure key:**
   ```bash
   # Using OpenSSL
   openssl rand -hex 32
   
   # Using Python
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

2. **Set the key via environment variable:**
   - Never commit the actual key to version control
   - Use `.env` file (which is gitignored) for local development
   - Use environment variables or secret management systems in production

3. **Configuration methods (in order of preference):**
   
   a. **Environment Variable** (Recommended for production)
   ```bash
   export LITELLM_MASTER_KEY="your-secure-key-here"
   docker-compose up -d
   ```
   
   b. **Docker Compose Override** (For local development)
   Create `docker-compose.override.yml` (gitignored):
   ```yaml
   services:
     litellm:
       environment:
         - LITELLM_MASTER_KEY=your-secure-key-here
   ```
   
   c. **.env File** (For local development)
   ```bash
   cp .env.example .env
   # Edit .env and set LITELLM_MASTER_KEY
   ```

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