#!/usr/bin/env python3
"""Development setup script for AI HR Platform."""

import os
import sys
import subprocess
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False


def main():
    """Set up development environment."""
    print("🚀 Setting up AI HR Platform development environment...")
    
    # Check if we're in the right directory
    if not (Path.cwd() / "ai_hr_platform").exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Install dependencies
    if not run_command("uv pip install -e .", "Installing package in development mode"):
        sys.exit(1)
    
    # Install development dependencies
    dev_deps = [
        "pytest",
        "pytest-cov",
        "pytest-asyncio",
        "black",
        "isort",
        "flake8",
        "mypy",
        "bandit",
        "pre-commit",
        "safety"
    ]
    
    cmd = f"uv pip install {' '.join(dev_deps)}"
    if not run_command(cmd, "Installing development dependencies"):
        sys.exit(1)
    
    # Set up pre-commit hooks
    if not run_command("pre-commit install", "Setting up pre-commit hooks"):
        print("⚠️  Pre-commit setup failed, continuing...")
    
    # Create .env file if it doesn't exist
    env_file = Path(".env")
    if not env_file.exists():
        env_content = """# AI HR Platform Environment Variables
OPENAI_API_KEY=your-openai-api-key-here
TELEGRAM_BOT_TOKEN=your-telegram-bot-token-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here
GROQ_API_KEY=your-groq-api-key-here
"""
        env_file.write_text(env_content)
        print("✅ Created .env file template")
    
    # Run tests to make sure everything works
    if not run_command("pytest tests/ -v", "Running tests"):
        print("⚠️  Some tests failed, but setup is complete")
    
    print("\n🎉 Development environment setup complete!")
    print("\nNext steps:")
    print("1. Edit .env file with your API keys")
    print("2. Run tests: pytest tests/")
    print("3. Start coding!")
    print("\nUseful commands:")
    print("  make test      # Run tests")
    print("  make lint      # Run linting")
    print("  make format    # Format code")
    print("  make help      # Show all commands")


if __name__ == "__main__":
    main()