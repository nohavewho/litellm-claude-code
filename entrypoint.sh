#!/bin/bash

# Set up Python path
export PYTHONPATH="/app:$PYTHONPATH"

# If Claude auth file is mounted, copy it to writable location
if [ -f "/root/.claude.json" ]; then
    # Create a copy in a temp location that Claude CLI can write to
    cp /root/.claude.json /tmp/.claude.json.bak
    rm -f /root/.claude.json
    cp /tmp/.claude.json.bak /root/.claude.json
    chmod 644 /root/.claude.json
    echo "Claude auth file copied to writable location"
fi

# Use our custom startup script that registers the provider first
exec python /app/startup.py