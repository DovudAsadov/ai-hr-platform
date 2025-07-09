"""Configuration management for AI HR Platform."""

import os
from typing import Dict, Any, Optional
from pathlib import Path
import json
from dotenv import load_dotenv


class Config:
    """Configuration manager for AI HR Platform."""
    
    def __init__(self, config_file: Optional[Path] = None):
        """Initialize configuration."""
        self.config_file = config_file or Path.home() / ".aihr" / "config.json"
        self.config_dir = self.config_file.parent
        self._config = {}
        
        # Load environment variables
        load_dotenv()
        
        # Load configuration
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file and environment."""
        # Load from file if exists
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self._config = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")
        
        # Override with environment variables
        env_mappings = {
            'OPENAI_API_KEY': 'openai_api_key',
            'TELEGRAM_BOT_TOKEN': 'telegram_bot_token',
            'ANTHROPIC_API_KEY': 'anthropic_api_key',
            'GROQ_API_KEY': 'groq_api_key',
        }
        
        for env_var, config_key in env_mappings.items():
            if env_var in os.environ:
                self._config[config_key] = os.environ[env_var]
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value."""
        self._config[key] = value
    
    def save(self):
        """Save configuration to file."""
        try:
            # Create config directory if it doesn't exist
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            # Save configuration
            with open(self.config_file, 'w') as f:
                json.dump(self._config, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save config file: {e}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Return configuration as dictionary."""
        return self._config.copy()
    
    def validate(self) -> bool:
        """Validate configuration."""
        required_keys = ['openai_api_key']
        
        for key in required_keys:
            if not self.get(key):
                print(f"Warning: Missing required configuration: {key}")
                return False
        
        return True
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'Config':
        """Create configuration from dictionary."""
        config = cls()
        config._config = config_dict.copy()
        return config
    
    def __repr__(self):
        """String representation of configuration."""
        # Hide sensitive information
        safe_config = {}
        for key, value in self._config.items():
            if 'api_key' in key.lower() or 'token' in key.lower():
                safe_config[key] = '***' if value else None
            else:
                safe_config[key] = value
        
        return f"Config({safe_config})"