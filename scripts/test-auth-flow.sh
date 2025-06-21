#!/bin/bash
# Test script to verify authentication flow

echo "Testing LiteLLM Claude Authentication Flow"
echo "=========================================="
echo ""

# Check current auth status
echo "1. Checking authentication status..."
AUTH_STATUS=$(curl -s http://localhost:4000/auth/status | jq -r '.authenticated')
echo "   Authenticated: $AUTH_STATUS"
echo ""

# Test API call
echo "2. Testing API call..."
RESPONSE=$(curl -s -X POST http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-1234" \
  -d '{"model": "sonnet", "messages": [{"role": "user", "content": "Say hello"}]}')

if echo "$RESPONSE" | jq -e '.choices[0].message.content' > /dev/null 2>&1; then
    echo "   Success! Response: $(echo "$RESPONSE" | jq -r '.choices[0].message.content')"
else
    echo "   Failed. Error: $(echo "$RESPONSE" | jq -r '.error.message // .error // "Unknown error"')"
fi
echo ""

# Show auth URL
echo "3. Authentication URL: http://localhost:4000/auth"
echo ""
echo "4. API Documentation: http://localhost:4000/docs"
echo ""

echo "Test complete!"