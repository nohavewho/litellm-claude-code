#!/usr/bin/env python3
"""
Test script showing how to use LiteLLM-Claude as an OpenAI API replacement
"""

from openai import OpenAI
import json

# Create OpenAI client pointing to LiteLLM
client = OpenAI(
    base_url="http://localhost:4000/v1",
    api_key="sk-1234"
)

print("Testing LiteLLM-Claude as OpenAI API...\n")

# List available models
print("Available models:")
models = client.models.list()
for model in models.data:
    print(f"  - {model.id}")

print("\n" + "="*50 + "\n")

# Test each model
test_models = ["sonnet", "opus", "claude-3-5-haiku-20240307"]

for model_name in test_models:
    print(f"Testing model: {model_name}")
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "user", "content": "Say hello and tell me what model you are in one sentence."}
            ],
            temperature=0.7,
            max_tokens=100
        )
        
        print(f"Response: {response.choices[0].message.content}")
        print(f"Usage: {response.usage}")
        print("\n" + "-"*50 + "\n")
        
    except Exception as e:
        print(f"Error: {e}")
        print("\n" + "-"*50 + "\n")

# Example with streaming
print("Testing streaming with sonnet model:")
stream = client.chat.completions.create(
    model="sonnet",
    messages=[{"role": "user", "content": "Count to 5"}],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
print("\n")