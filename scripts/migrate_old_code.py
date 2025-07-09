#!/usr/bin/env python3
"""Script to migrate old code to new structure."""

import shutil
import os
from pathlib import Path


def migrate_code():
    """Migrate existing code to new structure."""
    print("🔄 Migrating old code to new structure...")
    
    # Create examples directory
    examples_dir = Path("examples")
    examples_dir.mkdir(exist_ok=True)
    
    # Migration mappings
    migrations = [
        # Resume checker files
        ("resume_checker/main.py", "examples/old_resume_checker_main.py"),
        ("resume_checker/main_v2.py", "examples/old_resume_checker_main_v2.py"),
        ("resume_checker/sys_prompt.py", "examples/old_resume_checker_prompts.py"),
        
        # Resume analyzer files
        ("resume_analyzer/main_v4.py", "examples/old_resume_analyzer_main.py"),
        ("resume_analyzer/additional functions/main_v3.py", "examples/old_resume_analyzer_v3.py"),
        
        # Telegram bot files
        ("telegram_bot/resume_checker.py", "examples/old_telegram_bot.py"),
        ("telegram_bot/sys_prompt.py", "examples/old_telegram_prompts.py"),
    ]
    
    migrated_count = 0
    
    for old_path, new_path in migrations:
        old_file = Path(old_path)
        new_file = Path(new_path)
        
        if old_file.exists():
            try:
                # Copy file to examples
                shutil.copy2(old_file, new_file)
                print(f"✅ Migrated {old_path} -> {new_path}")
                migrated_count += 1
            except Exception as e:
                print(f"❌ Failed to migrate {old_path}: {e}")
    
    print(f"\n📊 Migration complete: {migrated_count} files migrated")
    
    # Create a migration guide
    guide_content = """# Migration Guide

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
"""
    
    with open(examples_dir / "MIGRATION_GUIDE.md", "w") as f:
        f.write(guide_content)
    
    print("📝 Created migration guide at examples/MIGRATION_GUIDE.md")


if __name__ == "__main__":
    migrate_code()