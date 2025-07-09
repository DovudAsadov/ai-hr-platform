# Migration Guide

This directory contains the old code files that have been migrated to the new structure.

## New Structure

The new AI HR Platform has been restructured as follows:

### Core Components
- `ai_hr_platform/core/resume_analyzer.py` - Resume analysis logic
- `ai_hr_platform/core/resume_optimizer.py` - Resume optimization logic
- `ai_hr_platform/config.py` - Configuration management

### Interfaces
- `ai_hr_platform/interfaces/web_interface.py` - Web UI (Gradio)
- `ai_hr_platform/interfaces/telegram_bot.py` - Telegram bot
- `ai_hr_platform/interfaces/cli_interface.py` - Command line interface

### Usage

```python
# New way to use the platform
from ai_hr_platform.core import ResumeAnalyzer
from ai_hr_platform.config import Config

config = Config()
analyzer = ResumeAnalyzer(config.to_dict())
result = analyzer.process("resume text here")
```

## Migration Notes

1. **System prompts**: Old prompt files have been integrated into the core classes
2. **Configuration**: Now uses a centralized Config class
3. **Interfaces**: Separated into different modules for better maintainability
4. **Error handling**: Standardized error handling across all components
5. **Testing**: Added comprehensive test suite

## Files Migrated

- `old_resume_checker_main.py` - Original resume checker main
- `old_resume_checker_main_v2.py` - Resume checker version 2
- `old_resume_checker_prompts.py` - Original system prompts
- `old_resume_analyzer_main.py` - Original resume analyzer
- `old_telegram_bot.py` - Original Telegram bot
- `old_telegram_prompts.py` - Telegram bot prompts

These files are kept for reference but should not be used in the new structure.
