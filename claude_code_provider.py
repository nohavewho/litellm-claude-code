import asyncio
from typing import Dict, List
import litellm
from litellm import CustomLLM, ModelResponse, Usage
from litellm.types.utils import Choices, Message as LiteLLMMessage, GenericStreamingChunk
from typing import Iterator, AsyncIterator

from claude_code_sdk import query, query_with_oauth, ClaudeCodeOptions
from claude_code_sdk.types import AssistantMessage, TextBlock
import os

class ClaudeCodeSDKProvider(CustomLLM):
    """LiteLLM provider for Claude Code SDK with proper model selection."""
    
    def __init__(self):
        super().__init__()
        print("ClaudeCodeSDKProvider initialized")
    
    def format_messages_to_prompt(self, messages: List[Dict]) -> str:
        """Convert LiteLLM messages to Claude prompt."""
        prompt_parts = []
        for message in messages:
            role = message.get('role', 'user')
            content = message.get('content', '')
            
            if role == 'system':
                prompt_parts.append(f"System: {content}")
            elif role == 'user':
                prompt_parts.append(f"Human: {content}")
            elif role == 'assistant':
                prompt_parts.append(f"Assistant: {content}")
        
        return "\n\n".join(prompt_parts)
    
    def extract_claude_model(self, model: str) -> str:
        """Extract Claude model name from LiteLLM model parameter."""
        # Handle "claude-code-sdk/claude-3-5-sonnet" -> "claude-3-5-sonnet"
        # Or just "claude-3-5-sonnet" -> "claude-3-5-sonnet"
        return model.split('/')[-1] if '/' in model else model
    
    def create_litellm_response(self, content: str, model: str) -> ModelResponse:
        """Convert Claude response to LiteLLM format."""
        import uuid
        from datetime import datetime
        
        message = LiteLLMMessage(content=content, role="assistant")
        choice = Choices(finish_reason="stop", index=0, message=message)
        usage = Usage(prompt_tokens=100, completion_tokens=50, total_tokens=150)
        
        response = ModelResponse()
        response.id = f"chatcmpl-{uuid.uuid4().hex}"
        response.object = "chat.completion"
        response.created = int(datetime.now().timestamp())
        response.model = model
        response.choices = [choice]
        response.usage = usage
        
        return response
    
    def completion(self, model: str, messages: List[Dict], **kwargs) -> ModelResponse:
        """Sync completion wrapper."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.acompletion(model, messages, **kwargs))
        finally:
            loop.close()
    
    async def acompletion(self, model: str, messages: List[Dict], **kwargs) -> ModelResponse:
        """Async completion using Claude Code SDK with model selection."""
        prompt = self.format_messages_to_prompt(messages)
        claude_model = self.extract_claude_model(model)
        
        # Create options with proper model selection
        options = ClaudeCodeOptions(model=claude_model)
        
        response_content = ""
        
        # Get the appropriate query function (they return AsyncIterators directly)
        if not os.environ.get('ANTHROPIC_API_KEY'):
            # Use OAuth authentication
            message_iterator = query_with_oauth(prompt=prompt, options=options)
        else:
            # Use API key authentication
            message_iterator = query(prompt=prompt, options=options)
        
        # Iterate through messages
        async for message in message_iterator:
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        response_content += block.text
        
        return self.create_litellm_response(response_content, model)
    
    def streaming(self, model: str, messages: List[Dict], **kwargs) -> Iterator[GenericStreamingChunk]:
        """Sync streaming wrapper - converts async to sync."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Create an async generator and convert to sync
            async_gen = self.astreaming(model, messages, **kwargs)
            while True:
                try:
                    chunk = loop.run_until_complete(async_gen.__anext__())
                    yield chunk
                except StopAsyncIteration:
                    break
        finally:
            loop.close()
    
    async def astreaming(self, model: str, messages: List[Dict], **kwargs) -> AsyncIterator[GenericStreamingChunk]:
        """Async streaming using Claude Code SDK."""
        prompt = self.format_messages_to_prompt(messages)
        claude_model = self.extract_claude_model(model)
        
        # Create options with proper model selection
        options = ClaudeCodeOptions(model=claude_model)
        
        accumulated_content = ""
        
        # Get the appropriate query function (they return AsyncIterators directly)
        if not os.environ.get('ANTHROPIC_API_KEY'):
            # Use OAuth authentication
            message_iterator = query_with_oauth(prompt=prompt, options=options)
        else:
            # Use API key authentication
            message_iterator = query(prompt=prompt, options=options)
        
        # Iterate through messages
        async for message in message_iterator:
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        # Yield each piece of text as it comes
                        chunk_text = block.text[len(accumulated_content):]
                        if chunk_text:
                            accumulated_content = block.text
                            yield GenericStreamingChunk(
                                text=chunk_text,
                                is_finished=False,
                                finish_reason=None,
                                usage=None,
                                index=0,
                                tool_use=None
                            )
        
        # Final chunk to indicate completion
        yield GenericStreamingChunk(
            text="",
            is_finished=True,
            finish_reason="stop",
            usage={"completion_tokens": 50, "prompt_tokens": 100, "total_tokens": 150},
            index=0,
            tool_use=None
        )

# Don't register here - let the YAML config handle it
# This avoids duplicate registrations