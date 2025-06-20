#!/usr/bin/env python3
"""Test script to verify custom provider works"""
import sys
sys.path.append('/app')
sys.path.append('/app/providers')

# Import litellm and our provider
import litellm
from litellm import completion

# Import to register the provider
import claude_code_provider

print("Testing Claude Code SDK Provider")
print(f"Custom provider map: {litellm.custom_provider_map}")

try:
    # Test a direct completion call
    response = completion(
        model="claude-code-sdk/claude-3-5-sonnet-20241022",
        messages=[{"role": "user", "content": "Say 'Hello from Claude Code SDK'"}],
        custom_llm_provider="claude-code-sdk"
    )
    print(f"Success! Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()