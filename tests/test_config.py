"""Tests for configuration management."""

import pytest
import tempfile
import json
from pathlib import Path

from ai_hr_platform.config import Config


class TestConfig:
    """Test configuration management."""
    
    def test_config_initialization(self):
        """Test configuration initialization."""
        config = Config()
        assert isinstance(config.to_dict(), dict)
    
    def test_config_get_set(self):
        """Test getting and setting configuration values."""
        config = Config()
        
        # Test setting and getting
        config.set('test_key', 'test_value')
        assert config.get('test_key') == 'test_value'
        
        # Test default value
        assert config.get('nonexistent_key', 'default') == 'default'
    
    def test_config_from_dict(self):
        """Test creating configuration from dictionary."""
        config_dict = {'openai_api_key': 'test_key'}
        config = Config.from_dict(config_dict)
        
        assert config.get('openai_api_key') == 'test_key'
    
    def test_config_file_operations(self):
        """Test saving and loading configuration files."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_file = Path(tmp_dir) / "test_config.json"
            
            # Create config with custom file
            config = Config(config_file=config_file)
            config.set('test_key', 'test_value')
            config.save()
            
            # Verify file was created
            assert config_file.exists()
            
            # Load config from file
            new_config = Config(config_file=config_file)
            assert new_config.get('test_key') == 'test_value'
    
    def test_config_validation(self):
        """Test configuration validation."""
        config = Config()
        
        # Should fail without required keys
        assert not config.validate()
        
        # Should pass with required keys
        config.set('openai_api_key', 'test_key')
        assert config.validate()
    
    def test_config_repr(self):
        """Test configuration string representation."""
        config = Config()
        config.set('openai_api_key', 'secret_key')
        config.set('regular_setting', 'value')
        
        repr_str = repr(config)
        
        # Sensitive data should be hidden
        assert 'secret_key' not in repr_str
        assert '***' in repr_str
        
        # Regular settings should be visible
        assert 'regular_setting' in repr_str
        assert 'value' in repr_str