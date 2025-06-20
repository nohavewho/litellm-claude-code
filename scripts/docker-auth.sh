#!/bin/bash

# Script to authenticate Claude inside the Docker container

echo "Authenticating Claude Code CLI in Docker container..."
echo "This will open a browser window for OAuth authentication."
echo ""

# Run the login command inside the container
docker exec -it litellm-claude-litellm-1 claude-code login

echo ""
echo "Authentication complete!"
echo "The credentials are stored in the container volume and will persist."