# AI HR Platform

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A professional, modular Python platform for AI-powered resume analysis and optimization. Built with modern Python practices and designed for extensibility.

## Features
- **Resume Analysis**: Get professional feedback on your resume with AI-powered insights
- **Resume Optimization**: Improve your resume for better ATS compatibility and impact
- **Web Interface**: Beautiful Gradio-based web UI for easy interaction
- **Telegram Bot**: Full-featured bot with async support and rich interactions
- **CLI Tool**: Professional command-line interface for automation
- **Modular Architecture**: Clean, maintainable codebase following Python best practices
- **Comprehensive Testing**: Full test suite with pytest and coverage reporting
- **Rich Documentation**: Extensive documentation and API reference

## Quick Start

### Prerequisites

- Python 3.9 or higher
- OpenAI API key
- (Optional) Telegram bot token for bot functionality

### Installation

---

### 📦 1. Clone the Repository

```bash
git clone https://github.com/DovudAsadov/ai-hr-platform.git
cd ai-hr-platform
````

---

### ⚙️ 2. Install [`uv`](https://github.com/astral-sh/uv) (Python package & environment manager)

If you haven’t installed `uv` yet:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

### 🧪 3. Set Up Python Environment

```bash
uv venv
source .venv/bin/activate
uv sync
```

---

### Configuration

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your-openai-api-key-here
TELEGRAM_BOT_TOKEN=your-telegram-bot-token-here  # Optional
```

### Usage Examples

#### Web Interface
```bash
ai-hr web --port 8080
```
Then open http://localhost:8080 in your browser.

#### Command Line
```bash
# Analyze a resume
ai-hr analyze resume.pdf

# Optimize resume text
ai-hr optimize --text "Your resume text here..."

# Save results to file
ai-hr analyze resume.pdf --output analysis.txt
```

#### Telegram Bot
```bash
ai-hr telegram --token YOUR_BOT_TOKEN
```

#### Python API
```python
from ai_hr_platform import ResumeAnalyzer, Config

# Initialize
config = Config()
analyzer = ResumeAnalyzer(config.to_dict())

# Analyze resume
result = analyzer.process("Your resume text here...")
print(result['analysis'])
```

### Core Classes

#### ResumeAnalyzer
Analyzes resumes and provides professional feedback.

```python
from ai_hr_platform.core import ResumeAnalyzer

analyzer = ResumeAnalyzer({'openai_api_key': 'your-key'})
result = analyzer.process("Resume text...")
```

#### ResumeOptimizer
Optimizes resumes for better impact and ATS compatibility.

```python
from ai_hr_platform.core import ResumeOptimizer

optimizer = ResumeOptimizer({'openai_api_key': 'your-key'})
result = optimizer.process("Resume text...")
```

#### Configuration
Centralized configuration management with environment variable support.

```python
from ai_hr_platform.config import Config

config = Config()
config.set('openai_api_key', 'your-key')
config.save()  # Saves to ~/.aihr/config.json
```

### CLI Commands

```bash
# Show help
ai-hr --help

# Analyze resume
ai-hr analyze <file.pdf>
ai-hr analyze --text "Resume text here"

# Optimize resume
ai-hr optimize <file.pdf>
ai-hr optimize --text "Resume text here"

# Launch web interface
ai-hr web [--port 8080] [--host 0.0.0.0] [--share]

# Run Telegram bot
ai-hr telegram [--token TOKEN]
```


### Code Quality

```bash
# Format code
black ai_hr_platform/
isort ai_hr_platform/

# Lint code
flake8 ai_hr_platform/
mypy ai_hr_platform/

# Security scan
bandit -r ai_hr_platform/

# Run all checks
make check
```

### Make Commands

```bash
make help          # Show all available commands
make test          # Run tests
make lint          # Run linting
make format        # Format code
make clean         # Clean build artifacts
make build         # Build package
make install       # Install package
make dev           # Install in development mode
```

## =' Configuration

### Environment Variables

- `OPENAI_API_KEY`: OpenAI API key (required)
- `TELEGRAM_BOT_TOKEN`: Telegram bot token (optional)
- `ANTHROPIC_API_KEY`: Anthropic API key (optional)
- `GROQ_API_KEY`: Groq API key (optional)

### Config File

The platform supports JSON configuration files at `~/.aihr/config.json`:

```json
{
  "openai_api_key": "your-key-here",
  "telegram_bot_token": "your-token-here"
}
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run the test suite (`pytest`)
6. Run code quality checks (`make check`)
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

### Code Style

- Follow PEP 8
- Use type hints
- Write docstrings for all public functions
- Add tests for new features
- Keep functions focused and small

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- OpenAI for providing the AI capabilities
- Gradio for the web interface framework
- python-telegram-bot for Telegram integration
- All contributors and users of this project
