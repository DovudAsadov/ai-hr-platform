# Installation Guide

This guide will help you install and set up AI HR Platform on your system.

## Requirements

### System Requirements
- **Operating System**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Python**: 3.9 or higher
- **Memory**: Minimum 4GB RAM, 8GB recommended
- **Storage**: At least 1GB free space

### Prerequisites
- Python 3.9+ installed on your system
- pip (Python package installer)
- Git (for cloning the repository)
- OpenAI API key (required for AI functionality)

## Installation Methods

### Method 1: Quick Install (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-hr-platform.git
cd ai-hr-platform

# Install the package
pip install -e .
```

### Method 2: Development Install

For developers or contributors:

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-hr-platform.git
cd ai-hr-platform

# Install with development dependencies
pip install -e ".[dev]"

# Set up development environment
python scripts/setup_dev.py
```

### Method 3: Using uv (Faster)

If you have [uv](https://github.com/astral-sh/uv) installed:

```bash
# Clone and install
git clone https://github.com/yourusername/ai-hr-platform.git
cd ai-hr-platform

# Install with uv
uv pip install -e .
```

## Configuration

### 1. Environment Variables

Create a `.env` file in the project root:

```bash
# Copy the example file
cp .env.example .env

# Edit the file with your configuration
nano .env
```

Add your API keys:

```env
# Required
OPENAI_API_KEY=your-openai-api-key-here

# Optional
TELEGRAM_BOT_TOKEN=your-telegram-bot-token-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here
GROQ_API_KEY=your-groq-api-key-here
```

### 2. Getting API Keys

#### OpenAI API Key (Required)
1. Go to [OpenAI Platform](https://platform.openai.com)
2. Sign up or log in to your account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key to your `.env` file

#### Telegram Bot Token (Optional)
1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Copy the bot token to your `.env` file

### 3. Verify Installation

```bash
# Check if the CLI is working
ai-hr --help

# Run a quick test
ai-hr analyze --text "Sample resume text for testing"
```

## Platform-Specific Instructions

### Windows

```powershell
# Using PowerShell
git clone https://github.com/yourusername/ai-hr-platform.git
cd ai-hr-platform
pip install -e .

# Create .env file
New-Item -Path .env -ItemType File
# Edit .env with Notepad or your preferred editor
```

### macOS

```bash
# Install Python if not already installed
brew install python

# Clone and install
git clone https://github.com/yourusername/ai-hr-platform.git
cd ai-hr-platform
pip3 install -e .
```

### Linux (Ubuntu/Debian)

```bash
# Install Python and pip if not already installed
sudo apt update
sudo apt install python3 python3-pip git

# Clone and install
git clone https://github.com/yourusername/ai-hr-platform.git
cd ai-hr-platform
pip3 install -e .
```

### Linux (CentOS/RHEL/Fedora)

```bash
# Install Python and pip if not already installed
sudo dnf install python3 python3-pip git  # Fedora
# or
sudo yum install python3 python3-pip git  # CentOS/RHEL

# Clone and install
git clone https://github.com/yourusername/ai-hr-platform.git
cd ai-hr-platform
pip3 install -e .
```

## Docker Installation (Alternative)

If you prefer using Docker:

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-hr-platform.git
cd ai-hr-platform

# Build the Docker image
docker build -t ai-hr-platform .

# Run the container
docker run -it --rm -v $(pwd):/app ai-hr-platform
```

## Troubleshooting

### Common Issues

#### Permission Errors
```bash
# If you get permission errors on Linux/macOS
pip install --user -e .
```

#### Python Version Issues
```bash
# Check your Python version
python --version

# If using Python 3.x specifically
python3 -m pip install -e .
```

#### Module Not Found
```bash
# Make sure you're in the right directory
pwd
ls -la  # Should see pyproject.toml

# Try reinstalling
pip uninstall ai-hr-platform
pip install -e .
```

#### API Key Issues
- Make sure your `.env` file is in the project root
- Check that your API key is valid and has sufficient credits
- Ensure there are no extra spaces in your `.env` file

### Getting Help

If you encounter issues:

1. **Check the Logs**: Look for error messages in the terminal
2. **GitHub Issues**: Search [existing issues](https://github.com/yourusername/ai-hr-platform/issues)
3. **Documentation**: Review the [full documentation](README.md)
4. **Community**: Ask in [GitHub Discussions](https://github.com/yourusername/ai-hr-platform/discussions)

## Updating

To update to the latest version:

```bash
# Pull latest changes
git pull origin main

# Reinstall dependencies
pip install -e .

# Run any migration scripts if needed
python scripts/migrate.py
```

## Uninstallation

To completely remove AI HR Platform:

```bash
# Uninstall the package
pip uninstall ai-hr-platform

# Remove the directory
rm -rf ai-hr-platform

# Remove configuration (optional)
rm -rf ~/.aihr
```

## Next Steps

After installation, you can:

1. **Try the Web Interface**: `ai-hr web`
2. **Use the CLI**: `ai-hr analyze resume.pdf`
3. **Read the Documentation**: Check out the [README](README.md)
4. **Join the Community**: Visit our [GitHub Discussions](https://github.com/yourusername/ai-hr-platform/discussions)

Happy analyzing! 🚀