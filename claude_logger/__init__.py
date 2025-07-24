"""
Claude Code Dev Logger - Conversation logging and analysis for Claude Code CLI

A Python package for comprehensive logging and analysis of Claude Code CLI conversations,
with methodology tracking, creative energy measurement, and statistical comparison.
"""

__version__ = "1.0.0"
__author__ = "Benjamin Rood"
__email__ = "10102132+benjamin-rood@users.noreply.github.com"

from .logger import ClaudeLogger
from .analyzer import SessionAnalyzer

__all__ = ["ClaudeLogger", "SessionAnalyzer"]