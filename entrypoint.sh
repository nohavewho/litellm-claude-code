#!/bin/bash

# Set up Python path
export PYTHONPATH="/app:$PYTHONPATH"

# Check authentication status
python /app/check_auth.py

# Use our custom startup script that registers the provider first
exec python /app/startup.py