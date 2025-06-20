# Auto-import to register provider
from .claude_code_provider import register_provider
# Import wrapper to patch get_llm_provider
from . import claude_code_wrapper