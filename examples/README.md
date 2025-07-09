# Examples and Legacy Code

This directory contains usage examples and migrated legacy code for reference.

## Usage Examples

### Basic Analysis Example

```python
from ai_hr_platform import ResumeAnalyzer, Config

# Setup configuration
config = Config()
config.set('openai_api_key', 'your-api-key-here')

# Initialize analyzer
analyzer = ResumeAnalyzer(config.to_dict())

# Analyze resume text
resume_text = """
John Doe
Software Engineer

Experience:
- Software Engineer at Tech Corp (2020-2023)
- Developed web applications using Python and JavaScript
"""

result = analyzer.process(resume_text)
print(result['analysis'])
```

### PDF Processing Example

```python
from ai_hr_platform.core import ResumeAnalyzer
from pathlib import Path

analyzer = ResumeAnalyzer({'openai_api_key': 'your-key'})

# Extract text from PDF
pdf_path = Path("resume.pdf")
text = analyzer.extract_text_from_pdf(pdf_path)

# Analyze extracted text
result = analyzer.process(text)
print(result['analysis'])
```

### Web Interface Example

```python
from ai_hr_platform.interfaces import WebInterface
from ai_hr_platform.config import Config

config = Config()
interface = WebInterface(config)

# Launch web interface
interface.launch(
    port=8080,
    share=True,  # Create shareable link
    server_name="0.0.0.0"  # Allow external connections
)
```

### Telegram Bot Example

```python
from ai_hr_platform.interfaces import TelegramBot
from ai_hr_platform.config import Config

config = Config()
config.set('telegram_bot_token', 'your-bot-token')

bot = TelegramBot(config)
bot.run()  # Start the bot
```

### CLI Examples

```bash
# Analyze a PDF resume
ai-hr analyze resume.pdf

# Analyze text input
ai-hr analyze --text "Resume content here..."

# Optimize a resume
ai-hr optimize resume.pdf --output optimized.txt

# Launch web interface
ai-hr web --port 8080 --share

# Run Telegram bot
ai-hr telegram --token YOUR_BOT_TOKEN
```

### Configuration Examples

#### Using Environment Variables

```bash
export OPENAI_API_KEY="your-key-here"
export TELEGRAM_BOT_TOKEN="your-token-here"

# Now you can use the CLI without additional setup
ai-hr analyze resume.pdf
```

#### Using Config File

```python
from ai_hr_platform.config import Config

# Create config from dictionary
config = Config.from_dict({
    'openai_api_key': 'your-key',
    'telegram_bot_token': 'your-token'
})

# Save to file
config.save()  # Saves to ~/.aihr/config.json

# Later, load from file
config = Config()  # Automatically loads from file
```

### Error Handling Examples

```python
from ai_hr_platform.core import ResumeAnalyzer

analyzer = ResumeAnalyzer({'openai_api_key': 'your-key'})

try:
    result = analyzer.process("resume text")
    
    if result['status'] == 'success':
        print("Analysis:", result['analysis'])
    else:
        print("Error:", result['error'])
        
except ValueError as e:
    print(f"Invalid input: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Batch Processing Example

```python
from ai_hr_platform.core import ResumeAnalyzer
from pathlib import Path
import json

analyzer = ResumeAnalyzer({'openai_api_key': 'your-key'})

# Process multiple resumes
resume_dir = Path("resumes/")
results = {}

for pdf_file in resume_dir.glob("*.pdf"):
    print(f"Processing {pdf_file.name}...")
    
    # Extract text
    text = analyzer.extract_text_from_pdf(pdf_file)
    
    # Analyze
    result = analyzer.process(text)
    results[pdf_file.name] = result

# Save results
with open("batch_results.json", "w") as f:
    json.dump(results, f, indent=2)
```

### Custom Processor Example

```python
from ai_hr_platform.core.base import BaseProcessor
from typing import Dict, Any

class CustomResumeProcessor(BaseProcessor):
    """Custom processor that adds specific analysis."""
    
    def process(self, input_data: str) -> Dict[str, Any]:
        # Validate input
        if not self.validate_input(input_data):
            return {"status": "failed", "error": "Invalid input"}
        
        # Preprocess
        processed_data = self.preprocess(input_data)
        
        # Custom processing logic
        word_count = len(processed_data.split())
        has_contact = "@" in processed_data
        
        analysis = {
            "word_count": word_count,
            "has_contact_info": has_contact,
            "status": "success"
        }
        
        # Postprocess
        return self.postprocess(analysis)
    
    def validate_input(self, input_data: str) -> bool:
        return isinstance(input_data, str) and len(input_data.strip()) > 0

# Usage
processor = CustomResumeProcessor()
result = processor.process("John Doe john@example.com Software Engineer...")
print(result)
```

## Legacy Code Files

The following files contain the original code that has been migrated to the new structure:

- `old_resume_checker_main.py` - Original resume checker main script
- `old_resume_checker_main_v2.py` - Resume checker version 2
- `old_resume_checker_prompts.py` - Original system prompts
- `old_resume_analyzer_main.py` - Original resume analyzer
- `old_resume_analyzer_v3.py` - Resume analyzer version 3
- `old_telegram_bot.py` - Original Telegram bot implementation
- `old_telegram_prompts.py` - Telegram bot prompts

These files are kept for reference but should not be used in the new structure. See `MIGRATION_GUIDE.md` for details on how the code has been restructured.

## Testing Examples

```python
import pytest
from ai_hr_platform.core import ResumeAnalyzer

def test_resume_analysis():
    """Test basic resume analysis."""
    analyzer = ResumeAnalyzer({'openai_api_key': 'test-key'})
    
    # Mock the OpenAI client for testing
    with patch.object(analyzer, 'openai_client') as mock_client:
        mock_response = Mock()
        mock_response.choices[0].message.content = "Great resume!"
        mock_client.chat.completions.create.return_value = mock_response
        
        result = analyzer.process("Sample resume text")
        assert result['status'] == 'success'
        assert 'Great resume!' in result['analysis']

# Run with: pytest examples/test_examples.py
```

## Contributing Examples

If you want to contribute new examples:

1. Create a new Python file in this directory
2. Include clear comments and docstrings
3. Test your examples thoroughly
4. Update this README with a description
5. Submit a pull request

For more information, see [CONTRIBUTING.md](../CONTRIBUTING.md).