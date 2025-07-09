"""Web interface using Gradio for AI HR Platform."""

import gradio as gr
from typing import Optional, Tuple
from pathlib import Path
import tempfile
import os

from ..core import ResumeAnalyzer, ResumeOptimizer
from ..config import Config


class WebInterface:
    """Gradio-based web interface for the AI HR Platform."""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize the web interface."""
        self.config = config or Config()
        self.analyzer = ResumeAnalyzer(self.config.to_dict())
        self.optimizer = ResumeOptimizer(self.config.to_dict())
        self.interface = None
        self._setup_interface()
    
    def _setup_interface(self):
        """Set up the Gradio interface."""
        with gr.Blocks(title="AI HR Platform", theme=gr.themes.Soft()) as interface:
            gr.Markdown("# AI HR Platform")
            gr.Markdown("Professional Resume Analysis and Optimization")
            
            with gr.Tabs():
                with gr.TabItem("Resume Analysis"):
                    self._setup_analysis_tab()
                
                with gr.TabItem("Resume Optimization"):
                    self._setup_optimization_tab()
                
                with gr.TabItem("Settings"):
                    self._setup_settings_tab()
        
        self.interface = interface
    
    def _setup_analysis_tab(self):
        """Set up the resume analysis tab."""
        gr.Markdown("## Resume Analysis")
        gr.Markdown("Upload your resume for professional analysis and feedback.")
        
        with gr.Row():
            with gr.Column():
                file_input = gr.File(
                    label="Upload Resume (PDF)",
                    file_types=[".pdf"],
                    type="filepath"
                )
                text_input = gr.Textbox(
                    label="Or paste resume text here",
                    placeholder="Paste your resume text...",
                    lines=10
                )
                analyze_btn = gr.Button("Analyze Resume", variant="primary")
            
            with gr.Column():
                analysis_output = gr.Textbox(
                    label="Analysis Results",
                    lines=20,
                    interactive=False
                )
        
        analyze_btn.click(
            fn=self._analyze_resume,
            inputs=[file_input, text_input],
            outputs=[analysis_output]
        )
    
    def _setup_optimization_tab(self):
        """Set up the resume optimization tab."""
        gr.Markdown("## Resume Optimization")
        gr.Markdown("Optimize your resume for better impact and ATS compatibility.")
        
        with gr.Row():
            with gr.Column():
                file_input = gr.File(
                    label="Upload Resume (PDF)",
                    file_types=[".pdf"],
                    type="filepath"
                )
                text_input = gr.Textbox(
                    label="Or paste resume text here",
                    placeholder="Paste your resume text...",
                    lines=10
                )
                optimize_btn = gr.Button("Optimize Resume", variant="primary")
            
            with gr.Column():
                optimization_output = gr.Textbox(
                    label="Optimized Resume",
                    lines=20,
                    interactive=False
                )
        
        optimize_btn.click(
            fn=self._optimize_resume,
            inputs=[file_input, text_input],
            outputs=[optimization_output]
        )
    
    def _setup_settings_tab(self):
        """Set up the settings tab."""
        gr.Markdown("## Settings")
        gr.Markdown("Configure your AI HR Platform settings.")
        
        api_key_input = gr.Textbox(
            label="OpenAI API Key",
            type="password",
            placeholder="Enter your OpenAI API key..."
        )
        
        save_btn = gr.Button("Save Settings", variant="primary")
        status_output = gr.Textbox(label="Status", interactive=False)
        
        save_btn.click(
            fn=self._save_settings,
            inputs=[api_key_input],
            outputs=[status_output]
        )
    
    def _analyze_resume(self, file_path: Optional[str], text_input: str) -> str:
        """Analyze resume from file or text input."""
        try:
            resume_text = ""
            
            if file_path:
                resume_text = self.analyzer.extract_text_from_pdf(Path(file_path))
            elif text_input.strip():
                resume_text = text_input.strip()
            else:
                return "Please upload a resume file or enter text to analyze."
            
            if not resume_text:
                return "Could not extract text from the resume. Please try again."
            
            result = self.analyzer.process(resume_text)
            
            if result.get("status") == "success":
                return result["analysis"]
            else:
                return f"Analysis failed: {result.get('error', 'Unknown error')}"
        
        except Exception as e:
            return f"Error analyzing resume: {str(e)}"
    
    def _optimize_resume(self, file_path: Optional[str], text_input: str) -> str:
        """Optimize resume from file or text input."""
        try:
            resume_text = ""
            
            if file_path:
                resume_text = self.analyzer.extract_text_from_pdf(Path(file_path))
            elif text_input.strip():
                resume_text = text_input.strip()
            else:
                return "Please upload a resume file or enter text to optimize."
            
            if not resume_text:
                return "Could not extract text from the resume. Please try again."
            
            result = self.optimizer.process(resume_text)
            
            if result.get("status") == "success":
                return result["optimized_resume"]
            else:
                return f"Optimization failed: {result.get('error', 'Unknown error')}"
        
        except Exception as e:
            return f"Error optimizing resume: {str(e)}"
    
    def _save_settings(self, api_key: str) -> str:
        """Save settings."""
        try:
            if api_key.strip():
                # In a real implementation, you'd save this securely
                os.environ["OPENAI_API_KEY"] = api_key.strip()
                return "Settings saved successfully!"
            else:
                return "Please enter a valid API key."
        except Exception as e:
            return f"Error saving settings: {str(e)}"
    
    def launch(self, **kwargs):
        """Launch the Gradio interface."""
        if self.interface:
            return self.interface.launch(**kwargs)
        else:
            raise RuntimeError("Interface not initialized")