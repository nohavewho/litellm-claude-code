#!/bin/bash

# Set up Python path
export PYTHONPATH="/app:$PYTHONPATH"

# Use our custom startup script that registers the provider first
exec python /app/startup.py