"""Base classes for AI HR Platform processors."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class BaseProcessor(ABC):
    """Base class for all AI HR Platform processors."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the processor with configuration."""
        self.config = config or {}
        self.logger = logger
    
    @abstractmethod
    def process(self, input_data: Any) -> Any:
        """Process input data and return results."""
        pass
    
    def validate_input(self, input_data: Any) -> bool:
        """Validate input data before processing."""
        return True
    
    def preprocess(self, input_data: Any) -> Any:
        """Preprocess input data before main processing."""
        return input_data
    
    def postprocess(self, output_data: Any) -> Any:
        """Postprocess output data after main processing."""
        return output_data