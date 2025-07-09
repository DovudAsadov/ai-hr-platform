"""Tests for core functionality."""

import pytest
from unittest.mock import Mock, patch
from ai_hr_platform.core import ResumeAnalyzer, ResumeOptimizer, BaseProcessor


class TestBaseProcessor:
    """Test base processor functionality."""
    
    def test_base_processor_initialization(self):
        """Test base processor initialization."""
        # Cannot instantiate abstract class directly
        with pytest.raises(TypeError):
            BaseProcessor()
    
    def test_base_processor_with_config(self):
        """Test base processor with configuration."""
        class TestProcessor(BaseProcessor):
            def process(self, input_data):
                return input_data
        
        config = {'test_key': 'test_value'}
        processor = TestProcessor(config)
        
        assert processor.config == config
        assert processor.process('test') == 'test'


class TestResumeAnalyzer:
    """Test resume analyzer functionality."""
    
    def test_analyzer_initialization(self):
        """Test analyzer initialization."""
        analyzer = ResumeAnalyzer()
        assert analyzer.config == {}
        assert analyzer.openai_client is None
    
    def test_analyzer_with_config(self):
        """Test analyzer with configuration."""
        config = {'openai_api_key': 'test_key'}
        
        with patch('ai_hr_platform.core.resume_analyzer.openai.OpenAI') as mock_openai:
            analyzer = ResumeAnalyzer(config)
            assert analyzer.config == config
            mock_openai.assert_called_once_with(api_key='test_key')
    
    def test_analyzer_process_invalid_input(self):
        """Test analyzer with invalid input."""
        analyzer = ResumeAnalyzer()
        
        with pytest.raises(ValueError):
            analyzer.process("")
    
    def test_analyzer_process_no_client(self):
        """Test analyzer without OpenAI client."""
        analyzer = ResumeAnalyzer()
        result = analyzer.process("Sample resume text")
        
        assert result['error'] == "OpenAI client not configured"
    
    @patch('ai_hr_platform.core.resume_analyzer.openai.OpenAI')
    def test_analyzer_process_success(self, mock_openai_class):
        """Test successful resume analysis."""
        # Mock OpenAI client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Analysis result"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        config = {'openai_api_key': 'test_key'}
        analyzer = ResumeAnalyzer(config)
        
        result = analyzer.process("Sample resume text")
        
        assert result['status'] == 'success'
        assert result['analysis'] == "Analysis result"
    
    def test_get_analysis_prompt(self):
        """Test analysis prompt generation."""
        analyzer = ResumeAnalyzer()
        prompt = analyzer._get_analysis_prompt()
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "resume" in prompt.lower()


class TestResumeOptimizer:
    """Test resume optimizer functionality."""
    
    def test_optimizer_initialization(self):
        """Test optimizer initialization."""
        optimizer = ResumeOptimizer()
        assert optimizer.config == {}
        assert optimizer.openai_client is None
    
    def test_optimizer_with_config(self):
        """Test optimizer with configuration."""
        config = {'openai_api_key': 'test_key'}
        
        with patch('ai_hr_platform.core.resume_optimizer.openai.OpenAI') as mock_openai:
            optimizer = ResumeOptimizer(config)
            assert optimizer.config == config
            mock_openai.assert_called_once_with(api_key='test_key')
    
    def test_optimizer_process_invalid_input(self):
        """Test optimizer with invalid input."""
        optimizer = ResumeOptimizer()
        
        with pytest.raises(ValueError):
            optimizer.process("")
    
    def test_optimizer_process_no_client(self):
        """Test optimizer without OpenAI client."""
        optimizer = ResumeOptimizer()
        result = optimizer.process("Sample resume text")
        
        assert result['error'] == "OpenAI client not configured"
    
    @patch('ai_hr_platform.core.resume_optimizer.openai.OpenAI')
    def test_optimizer_process_success(self, mock_openai_class):
        """Test successful resume optimization."""
        # Mock OpenAI client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Optimized resume"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        config = {'openai_api_key': 'test_key'}
        optimizer = ResumeOptimizer(config)
        
        result = optimizer.process("Sample resume text")
        
        assert result['status'] == 'success'
        assert result['optimized_resume'] == "Optimized resume"
    
    def test_get_optimization_prompt(self):
        """Test optimization prompt generation."""
        optimizer = ResumeOptimizer()
        prompt = optimizer._get_optimization_prompt()
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "optimize" in prompt.lower()
    
    def test_generate_latex_resume(self):
        """Test LaTeX resume generation."""
        optimizer = ResumeOptimizer()
        latex_output = optimizer.generate_latex_resume({})
        
        assert isinstance(latex_output, str)
        assert "LaTeX" in latex_output