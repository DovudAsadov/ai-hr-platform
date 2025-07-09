"""Test configuration and fixtures."""

import pytest
import tempfile
from pathlib import Path

from ai_hr_platform.config import Config


@pytest.fixture
def temp_config_file():
    """Create a temporary config file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config_file = Path(f.name)
    
    yield config_file
    
    # Cleanup
    if config_file.exists():
        config_file.unlink()


@pytest.fixture
def test_config():
    """Create a test configuration."""
    return Config.from_dict({
        'openai_api_key': 'test_openai_key',
        'telegram_bot_token': 'test_telegram_token'
    })


@pytest.fixture
def sample_resume_text():
    """Sample resume text for testing."""
    return """
    John Doe
    Software Engineer
    
    Experience:
    - Software Engineer at Tech Corp (2020-2023)
    - Developed web applications using Python and JavaScript
    - Led team of 5 developers
    
    Education:
    - Bachelor's in Computer Science, University of Tech (2020)
    
    Skills:
    - Python, JavaScript, React, Node.js
    - Database: PostgreSQL, MongoDB
    - Cloud: AWS, Docker
    """


@pytest.fixture
def sample_pdf_path():
    """Create a sample PDF file for testing."""
    # This would need a real PDF file for full testing
    # For now, return a placeholder path
    return Path("/tmp/sample_resume.pdf")