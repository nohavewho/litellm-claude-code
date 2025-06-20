#!/usr/bin/env python3
"""Check authentication status on container startup"""

import subprocess
import sys
import os
from pathlib import Path

def check_auth_status():
    """Check if we're authenticated with Claude SDK"""
    try:
        result = subprocess.run(
            ["claude-auth", "status"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except Exception:
        return False

def check_host_tokens():
    """Check if host tokens are available as fallback"""
    host_sdk_tokens = Path("/root/.claude_code_host/tokens.json")
    host_cli_tokens = Path("/root/.claude.json_host")
    
    if host_sdk_tokens.exists():
        print("Found host SDK tokens at /root/.claude_code_host/tokens.json")
        # Try to copy them if our volume is empty
        our_tokens = Path("/root/.claude_code/tokens.json")
        if not our_tokens.exists():
            try:
                our_tokens.parent.mkdir(parents=True, exist_ok=True)
                import shutil
                shutil.copy2(host_sdk_tokens, our_tokens)
                print("Copied host SDK tokens to container")
                return True
            except Exception as e:
                print(f"Could not copy host tokens: {e}")
    
    return False

def main():
    print("=== Claude Authentication Check ===")
    
    # Check if we're already authenticated
    if check_auth_status():
        print("✓ Claude SDK authentication is active")
        return 0
    
    print("✗ Not authenticated with Claude SDK")
    
    # Try to use host tokens
    if check_host_tokens() and check_auth_status():
        print("✓ Successfully used host authentication")
        return 0
    
    print("\nTo authenticate this container, run:")
    print("  ./scripts/auth-container.sh")
    print("\nOr from inside the container:")
    print("  claude-auth login")
    
    # Don't fail - just warn
    return 0

if __name__ == "__main__":
    sys.exit(main())