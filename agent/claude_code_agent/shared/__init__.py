"""
Shared components for Claude Code trading agents.

This module provides common infrastructure used by all strategy agents:
- ClaudeCodeAgent base class
- BaseStrategy interface
- Shared CLAUDE.md instruction sections
- Utilities for building agent-specific instructions
"""

from .claude_core import ClaudeCodeAgent
from .base_strategy import BaseStrategy

__all__ = [
    'ClaudeCodeAgent',
    'BaseStrategy',
]

__version__ = '3.1.0'  # Separate agent directories
