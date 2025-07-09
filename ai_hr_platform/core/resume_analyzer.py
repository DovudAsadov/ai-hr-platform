"""Resume analysis core functionality."""

from typing import Dict, Any, Optional
from pathlib import Path
import PyPDF2
from .base import BaseProcessor


class ResumeAnalyzer(BaseProcessor):
    """Core resume analysis functionality."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the resume analyzer."""
        super().__init__(config)
        self.openai_client = None
        self.analysis_prompt = None
        self._setup_ai_client()
    
    def _setup_ai_client(self):
        """Set up OpenAI client."""
        try:
            import openai
            api_key = self.config.get('openai_api_key')
            if api_key:
                self.openai_client = openai.OpenAI(api_key=api_key)
        except ImportError:
            self.logger.warning("OpenAI package not installed")
    
    def process(self, resume_data: Any) -> Dict[str, Any]:
        """Analyze resume and return structured feedback."""
        if not self.validate_input(resume_data):
            raise ValueError("Invalid resume data provided")
        
        processed_data = self.preprocess(resume_data)
        
        # Main analysis logic
        analysis_result = self._analyze_resume(processed_data)
        
        return self.postprocess(analysis_result)
    
    def _analyze_resume(self, resume_text: str) -> Dict[str, Any]:
        """Perform the actual resume analysis."""
        if not self.openai_client:
            return {"error": "OpenAI client not configured"}
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self._get_analysis_prompt()},
                    {"role": "user", "content": f"Please analyze this resume:\n\n{resume_text}"}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            return {
                "analysis": response.choices[0].message.content,
                "status": "success"
            }
        except Exception as e:
            self.logger.error(f"Analysis failed: {str(e)}")
            return {"error": str(e), "status": "failed"}
    
    def _get_analysis_prompt(self) -> str:
        """Get the system prompt for resume analysis."""
        return """You are an expert HR professional and resume reviewer. 
        Analyze the provided resume and provide structured feedback on:
        1. Overall impression and strengths
        2. Areas for improvement
        3. Formatting and presentation
        4. Content relevance and impact
        5. Specific recommendations for enhancement
        
        Provide your analysis in a structured, professional format."""
    
    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """Extract text from PDF resume."""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return text
        except Exception as e:
            self.logger.error(f"PDF extraction failed: {str(e)}")
            return ""