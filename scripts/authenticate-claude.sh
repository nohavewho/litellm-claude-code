#!/bin/bash
# Script to authenticate Claude Code CLI in the container

echo "Authenticating Claude Code CLI..."
echo "This will open a browser window for OAuth authentication."
echo ""

# Run the login command in the container
docker exec -it litellm-claude-litellm-1 claude-code login

echo ""
echo "Authentication complete!"
echo "The credentials are stored in the container and will persist until the container is removed."