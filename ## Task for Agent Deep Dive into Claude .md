 ## Task for Agent Deep Dive into Claude Code SDK Capabilities

  ### Recommended Configuration
  
  - **Thinking Mode**: Think Hard

  ### Task Description

  **Objective**: Investigate the actual capabilities and limitations of the Claude Code SDK to determine which
  features from the official Anthropic API are supported and which are not.

## REQUIRED READING
https://github.com/anthropics/claude-code-sdk-python
https://github.com/BerriAI/litellm/blob/main/docs/my-website/docs/providers/anthropic.md
https://docs.anthropic.com/en/docs/claude-code/sdk
providers/claude_code_provider.py


  ### Investigation Areas

  1. **STREAMING IMPLEMENTATION**
     - We have this implemented, but improvement is CRITICAL
     - Examine Anthropics' LiteLLM Implementation
     - Examine Claude Code SDK Python implementation
     - Examine our implementation in providers/claude_code_provider.py

  1. **SDK Source Code Analysis**
     - Examine the Claude Code SDK Python implementation
     - Start with: `pip show claude-code-sdk` to find installation location
     - Review the SDK's class definitions and method signatures
     - Look for supported parameters in `ClaudeCodeOptions` or similar classes

  2. **Feature Compatibility Matrix**
     Create a detailed comparison table:
     - Parameter support (temperature, max_tokens, stop_sequences, etc.)
     - System message handling
     - Streaming capabilities and format
     - Tool/function calling support
     - Vision/image support
     - Web search integration
     - MCP (Model Context Protocol) support
     - Response format options
     - Token counting/usage reporting

  3. **SDK Documentation Review**
     - Check official Claude Code SDK documentation
     - Look for API reference or parameter guides
     - Note any mentioned limitations or unsupported features

  4. **Practical Testing**
     - Write small test scripts to verify:
       - Which parameters are actually accepted
       - How the SDK handles unsupported parameters
       - What happens when you try to use advanced features
     - Test the SDK's error messages for clues about capabilities

  5. **SDK vs API Comparison**
     - Compare Claude Code SDK methods with Anthropic's direct API
     - Identify the abstraction layer differences
     - Determine if SDK is a thin wrapper or has significant limitations

  ### Specific Questions to Answer

  1. **Parameter Support**
     - Does `ClaudeCodeOptions` accept temperature, max_tokens, stop_sequences?
     - How does it handle system messages?
     - Can it process tool definitions?

  2. **Response Format**
     - What's the actual response structure from the SDK?
     - Does it include token usage information?
     - How does streaming work (if at all)?

  3. **Authentication Differences**
     - How does OAuth affect available features vs API key auth?
     - Are there tier-based limitations?

  4. **Advanced Features**
     - Is tool/function calling possible through the SDK?
     - Can it handle vision requests?
     - Is web search available?
     - What about thinking/reasoning tokens?

  ### Deliverables

  1. **Capability Matrix**: Clear table showing Supported/Unsupported/Unknown for each feature
  2. **Code Examples**: Working examples of what IS supported
  3. **Limitation Report**: Detailed explanation of what can't be done and why
  4. **Recommendations**:
     - Which parameters we should immediately add to our provider
     - Which features we should document as unsupported
     - Potential workarounds for missing features
  5. **Documentation**: Output markdown containing all findings to agent-output/
  6. **Testing**: Output testing prodecure, scripts and findings to agent-output/

  ### Investigation Methodology

  1. Start with Claude Code SDK source code inspection
  2. Supplement with LiteLLM Anthropic Provider source code inspection  
  3. Cross-reference with any available documentation
  4. Use Context7 tool to search for other relevant documentation 
  5. Scrutinize our implementation
  6. Write test scripts to verify findings
  7. Document everything with code examples
  8. Provide clear recommendations based on findings

  This investigation will help us understand exactly what we can and cannot implement in our provider, avoiding
  wasted effort on unsupported features.