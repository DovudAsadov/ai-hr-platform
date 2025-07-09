"""User interfaces for AI HR Platform."""

from .web_interface import WebInterface
from .telegram_bot import TelegramBot
from .cli_interface import CLIInterface

__all__ = [
    "WebInterface",
    "TelegramBot", 
    "CLIInterface",
]