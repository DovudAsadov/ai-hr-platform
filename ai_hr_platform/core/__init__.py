"""Core functionality for AI HR Platform."""

from .resume_analyzer import ResumeAnalyzer
from .resume_optimizer import ResumeOptimizer
from .base import BaseProcessor

__all__ = [
    "ResumeAnalyzer",
    "ResumeOptimizer",
    "BaseProcessor",
]