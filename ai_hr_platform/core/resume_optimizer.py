"""Resume optimization core functionality."""

from typing import Dict, Any, Optional
from .base import BaseProcessor


class ResumeOptimizer(BaseProcessor):
    """Core resume optimization functionality."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the resume optimizer."""
        super().__init__(config)
        self.openai_client = None
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
        """Optimize resume and return enhanced version."""
        if not self.validate_input(resume_data):
            raise ValueError("Invalid resume data provided")
        
        processed_data = self.preprocess(resume_data)
        
        # Main optimization logic
        optimization_result = self._optimize_resume(processed_data)
        
        return self.postprocess(optimization_result)
    
    def _optimize_resume(self, resume_text: str) -> Dict[str, Any]:
        """Perform the actual resume optimization."""
        if not self.openai_client:
            return {"error": "OpenAI client not configured"}
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self._get_optimization_prompt()},
                    {"role": "user", "content": f"Please optimize this resume:\n\n{resume_text}"}
                ],
                max_tokens=3000,
                temperature=0.5
            )
            
            return {
                "optimized_resume": response.choices[0].message.content,
                "status": "success"
            }
        except Exception as e:
            self.logger.error(f"Optimization failed: {str(e)}")
            return {"error": str(e), "status": "failed"}
    
    def _get_optimization_prompt(self) -> str:
        """Get the system prompt for resume optimization."""
        return """You are an expert resume writer and career coach. 
        Optimize the provided resume to make it more compelling and effective.
        
        Focus on:
        1. Improving language and impact statements
        2. Enhancing formatting and structure
        3. Optimizing for ATS systems
        4. Strengthening achievements with metrics
        5. Ensuring consistency and professional presentation
        
        Return the optimized resume in a well-formatted structure."""
    
    def generate_latex_resume(self, resume_data: Dict[str, Any]) -> str:
        """Generate LaTeX formatted resume."""
        # This would contain LaTeX template generation logic
        # For now, return a placeholder
        return "% LaTeX resume template would be generated here"