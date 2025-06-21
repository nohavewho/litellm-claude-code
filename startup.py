#!/usr/bin/env python3
"""
Startup script that generates Prisma client and starts LiteLLM
"""
import sys
import os
import subprocess

# Add paths for custom providers
sys.path.append('/app')

# The custom provider will be loaded via the YAML config
print("Starting LiteLLM with custom provider configuration...")

# Generate Prisma client first
print("Generating Prisma client...")
try:
    result = subprocess.run(['prisma', 'generate'], capture_output=True, text=True, cwd='/usr/local/lib/python3.11/site-packages/litellm/proxy')
    print(f"Prisma generate result: {result.returncode}")
    if result.stdout:
        print(f"Stdout: {result.stdout}")
    if result.stderr:
        print(f"Stderr: {result.stderr}")
except Exception as e:
    print(f"Prisma generate failed: {e}")

print("Starting LiteLLM proxy with YAML config...")

if __name__ == "__main__":
    os.environ['CONFIG_FILE_PATH'] = '/app/config/litellm_config.yaml'
    
    # Set default development master key if not provided
    if not os.environ.get('LITELLM_MASTER_KEY'):
        print("[STARTUP] WARNING: No LITELLM_MASTER_KEY set, using development default 'sk-development-only'")
        print("[STARTUP] For production, set a secure key using: openssl rand -hex 32")
        os.environ['LITELLM_MASTER_KEY'] = 'sk-development-only'
    
    # Import litellm and ensure custom provider is registered
    import litellm
    
    # Double-check provider registration
    if hasattr(litellm, 'custom_provider_map'):
        print(f"[STARTUP] Custom providers registered: {litellm.custom_provider_map}")
        print(f"[STARTUP] Number of providers: {len(litellm.custom_provider_map)}")
        for i, provider in enumerate(litellm.custom_provider_map):
            print(f"[STARTUP] Provider {i}: {provider.get('provider')}")
    else:
        print("[STARTUP] Warning: No custom_provider_map found")
    
    # Also check if our wrapper patch is applied
    print(f"[STARTUP] get_llm_provider function: {litellm.get_llm_provider}")
    
    import uvicorn
    from litellm.proxy.proxy_server import app
    
    # Add authentication routes
    from auth_integration import add_auth_routes
    app = add_auth_routes(app)
    print("[STARTUP] Added authentication routes to LiteLLM")
    
    # Start the server
    uvicorn.run(app, host="0.0.0.0", port=4000)