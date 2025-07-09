"""AI HR Platform - Professional Resume Analysis and Optimization Suite."""

__version__ = "0.1.0"
__author__ = "AI HR Platform Team"
__email__ = "contact@aihrplatform.com"

from .core import ResumeAnalyzer, ResumeOptimizer
from .config import Config

__all__ = [
    "ResumeAnalyzer",
    "ResumeOptimizer", 
    "Config",
]