# API Reference

Complete API reference for AI HR Platform.

## Table of Contents

- [Core Classes](#core-classes)
- [Configuration](#configuration)
- [Interfaces](#interfaces)
- [Utilities](#utilities)
- [Error Handling](#error-handling)

## Core Classes

### BaseProcessor

Abstract base class for all processors in the AI HR Platform.

```python
from ai_hr_platform.core.base import BaseProcessor
```

#### Methods

##### `__init__(config: Optional[Dict[str, Any]] = None)`

Initialize the processor with optional configuration.

**Parameters:**
- `config` (Optional[Dict[str, Any]]): Configuration dictionary

##### `process(input_data: Any) -> Any` (Abstract)

Process input data and return results. Must be implemented by subclasses.

**Parameters:**
- `input_data` (Any): Data to process

**Returns:**
- Any: Processed results

##### `validate_input(input_data: Any) -> bool`

Validate input data before processing.

**Parameters:**
- `input_data` (Any): Data to validate

**Returns:**
- bool: True if valid, False otherwise

##### `preprocess(input_data: Any) -> Any`

Preprocess input data before main processing.

**Parameters:**
- `input_data` (Any): Data to preprocess

**Returns:**
- Any: Preprocessed data

##### `postprocess(output_data: Any) -> Any`

Postprocess output data after main processing.

**Parameters:**
- `output_data` (Any): Data to postprocess

**Returns:**
- Any: Postprocessed data

---

### ResumeAnalyzer

Core resume analysis functionality.

```python
from ai_hr_platform.core import ResumeAnalyzer
```

#### Methods

##### `__init__(config: Optional[Dict[str, Any]] = None)`

Initialize the resume analyzer.

**Parameters:**
- `config` (Optional[Dict[str, Any]]): Configuration including OpenAI API key

**Example:**
```python
config = {'openai_api_key': 'your-key-here'}
analyzer = ResumeAnalyzer(config)
```

##### `process(resume_data: Any) -> Dict[str, Any]`

Analyze resume and return structured feedback.

**Parameters:**
- `resume_data` (Any): Resume text or data to analyze

**Returns:**
- Dict[str, Any]: Analysis results with structure:
  ```python
  {
      "status": "success|failed",
      "analysis": "Detailed analysis text",
      "error": "Error message if failed"
  }
  ```

**Raises:**
- `ValueError`: If resume_data is invalid

**Example:**
```python
result = analyzer.process("Resume text here...")
if result["status"] == "success":
    print(result["analysis"])
```

##### `extract_text_from_pdf(pdf_path: Path) -> str`

Extract text from PDF resume.

**Parameters:**
- `pdf_path` (Path): Path to PDF file

**Returns:**
- str: Extracted text content

**Example:**
```python
from pathlib import Path
text = analyzer.extract_text_from_pdf(Path("resume.pdf"))
```

---

### ResumeOptimizer

Core resume optimization functionality.

```python
from ai_hr_platform.core import ResumeOptimizer
```

#### Methods

##### `__init__(config: Optional[Dict[str, Any]] = None)`

Initialize the resume optimizer.

**Parameters:**
- `config` (Optional[Dict[str, Any]]): Configuration including OpenAI API key

##### `process(resume_data: Any) -> Dict[str, Any]`

Optimize resume and return enhanced version.

**Parameters:**
- `resume_data` (Any): Resume text or data to optimize

**Returns:**
- Dict[str, Any]: Optimization results with structure:
  ```python
  {
      "status": "success|failed",
      "optimized_resume": "Optimized resume text",
      "error": "Error message if failed"
  }
  ```

**Example:**
```python
optimizer = ResumeOptimizer(config)
result = optimizer.process("Resume text here...")
if result["status"] == "success":
    print(result["optimized_resume"])
```

##### `generate_latex_resume(resume_data: Dict[str, Any]) -> str`

Generate LaTeX formatted resume.

**Parameters:**
- `resume_data` (Dict[str, Any]): Structured resume data

**Returns:**
- str: LaTeX formatted resume

---

## Configuration

### Config

Configuration management for AI HR Platform.

```python
from ai_hr_platform.config import Config
```

#### Methods

##### `__init__(config_file: Optional[Path] = None)`

Initialize configuration manager.

**Parameters:**
- `config_file` (Optional[Path]): Custom config file path (default: ~/.aihr/config.json)

##### `get(key: str, default: Any = None) -> Any`

Get configuration value.

**Parameters:**
- `key` (str): Configuration key
- `default` (Any): Default value if key not found

**Returns:**
- Any: Configuration value

**Example:**
```python
config = Config()
api_key = config.get('openai_api_key')
port = config.get('web_port', 8080)
```

##### `set(key: str, value: Any)`

Set configuration value.

**Parameters:**
- `key` (str): Configuration key
- `value` (Any): Value to set

**Example:**
```python
config.set('openai_api_key', 'your-key-here')
config.set('telegram_bot_token', 'your-token')
```

##### `save()`

Save configuration to file.

**Example:**
```python
config.set('openai_api_key', 'new-key')
config.save()  # Saves to ~/.aihr/config.json
```

##### `to_dict() -> Dict[str, Any]`

Return configuration as dictionary.

**Returns:**
- Dict[str, Any]: Configuration dictionary

##### `validate() -> bool`

Validate configuration for required keys.

**Returns:**
- bool: True if valid, False otherwise

##### `from_dict(cls, config_dict: Dict[str, Any]) -> 'Config'` (Class Method)

Create configuration from dictionary.

**Parameters:**
- `config_dict` (Dict[str, Any]): Configuration dictionary

**Returns:**
- Config: New configuration instance

**Example:**
```python
config = Config.from_dict({
    'openai_api_key': 'your-key',
    'telegram_bot_token': 'your-token'
})
```

---

## Interfaces

### WebInterface

Gradio-based web interface.

```python
from ai_hr_platform.interfaces import WebInterface
```

#### Methods

##### `__init__(config: Optional[Config] = None)`

Initialize web interface.

**Parameters:**
- `config` (Optional[Config]): Configuration instance

##### `launch(**kwargs)`

Launch the Gradio interface.

**Parameters:**
- `**kwargs`: Gradio launch parameters (port, share, etc.)

**Example:**
```python
interface = WebInterface(config)
interface.launch(port=8080, share=True)
```

---

### TelegramBot

Telegram bot interface.

```python
from ai_hr_platform.interfaces import TelegramBot
```

#### Methods

##### `__init__(config: Optional[Config] = None)`

Initialize Telegram bot.

**Parameters:**
- `config` (Optional[Config]): Configuration with bot token

##### `run()`

Run the Telegram bot.

**Example:**
```python
bot = TelegramBot(config)
bot.run()  # Starts polling for messages
```

---

### CLIInterface

Command-line interface.

```python
from ai_hr_platform.interfaces import CLIInterface
```

#### Methods

##### `__init__(config: Optional[Config] = None)`

Initialize CLI interface.

##### `run(args: Optional[list] = None)`

Run the CLI with given arguments.

**Parameters:**
- `args` (Optional[list]): Command line arguments (default: sys.argv[1:])

**Example:**
```python
cli = CLIInterface(config)
cli.run(['analyze', 'resume.pdf'])
```

---

## Utilities

### Environment Variables

The platform recognizes these environment variables:

- `OPENAI_API_KEY`: OpenAI API key (required)
- `TELEGRAM_BOT_TOKEN`: Telegram bot token
- `ANTHROPIC_API_KEY`: Anthropic API key
- `GROQ_API_KEY`: Groq API key

### File Paths

- Config file: `~/.aihr/config.json`
- Log files: `~/.aihr/logs/`
- Cache: `~/.aihr/cache/`

---

## Error Handling

### Standard Response Format

All processors return responses in this format:

```python
{
    "status": "success" | "failed",
    "data": "...",  # Varies by processor
    "error": "Error message if failed"
}
```

### Common Exceptions

#### `ValueError`
Raised when input data is invalid or malformed.

#### `ConfigurationError`
Raised when required configuration is missing.

#### `APIError`
Raised when AI service API calls fail.

### Error Examples

```python
try:
    result = analyzer.process("")
except ValueError as e:
    print(f"Invalid input: {e}")

# Or check status
result = analyzer.process("resume text")
if result["status"] == "failed":
    print(f"Analysis failed: {result['error']}")
```

---

## Examples

### Complete Analysis Workflow

```python
from ai_hr_platform import ResumeAnalyzer, Config
from pathlib import Path

# Setup
config = Config()
config.set('openai_api_key', 'your-key-here')
analyzer = ResumeAnalyzer(config.to_dict())

# Extract text from PDF
pdf_path = Path("resume.pdf")
resume_text = analyzer.extract_text_from_pdf(pdf_path)

# Analyze
result = analyzer.process(resume_text)

if result["status"] == "success":
    print("Analysis Results:")
    print(result["analysis"])
else:
    print(f"Analysis failed: {result['error']}")
```

### Multi-Interface Setup

```python
from ai_hr_platform.config import Config
from ai_hr_platform.interfaces import WebInterface, TelegramBot

# Shared configuration
config = Config()
config.set('openai_api_key', 'your-key')
config.set('telegram_bot_token', 'your-token')

# Launch web interface in one process
web = WebInterface(config)
web.launch(port=8080)

# Run Telegram bot in another process
bot = TelegramBot(config)
bot.run()
```

---

For more examples, see the [examples/](../examples/) directory.