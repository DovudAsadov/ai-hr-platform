import os
import streamlit as st
import openai
from dotenv import load_dotenv
import PyPDF2
import logging
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import re

# Load environment variables
load_dotenv()

# Configure minimal logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Constants
SYSTEM_PROMPT = """You are an expert HR analyst and resume reviewer. Analyze the provided resume against the job description and provide a comprehensive evaluation.

Scoring Criteria (Total: 100 points):
1. Skills Match (25 points) - Alignment with required skills
2. Experience Relevance (25 points) - Relevant work experience depth
3. Achievement Quality (15 points) - Quantifiable accomplishments
4. Education & Certifications (10 points) - Educational background
5. Career Progression (10 points) - Career growth trajectory
6. Keyword Match (10 points) - Industry terminology usage
7. Resume Quality (5 points) - Organization and presentation

Provide:
- Overall Score: X/100
- Detailed breakdown for each criteria
- Strengths and improvement areas
- Hiring recommendation with reasoning"""

class ResumeAnalyzer:
    def __init__(self):
        pass
        
    def extract_pdf_text(self, file_obj):
        try:
            pdf_reader = PyPDF2.PdfReader(file_obj)
            return "".join(page.extract_text() or "" for page in pdf_reader.pages)
        except Exception as e:
            st.error(f"PDF extraction error: {str(e)}")
            return ""
    
    def read_file_content(self, uploaded_file):
        if not uploaded_file:
            return ""
        
        try:
            if uploaded_file.type == "application/pdf":
                return self.extract_pdf_text(uploaded_file)
            else:
                return str(uploaded_file.read(), "utf-8")
        except Exception as e:
            st.error(f"File reading error: {str(e)}")
            return ""
    
    def analyze_with_openai(self, job_description, resume, model="gpt-4o-mini"):
        try:
            if not job_description.strip() or not resume.strip():
                return "Please provide both job description and resume."
            
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                return "OpenAI API key not found. Please add it in the sidebar."
            
            client = openai.OpenAI(api_key=api_key)
            
            user_query = f"""Job Description:\n{job_description}\n\nCandidate Resume:\n{resume}"""
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_query}
                ],
                temperature=0.2,
                max_tokens=4000
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"Analysis error: {str(e)}"
    
    def compute_basic_similarity(self, resume_text, job_text):
        """Basic keyword-based similarity without heavy ML dependencies"""
        try:
            # Convert to lowercase and split into words
            resume_words = set(re.findall(r'\b\w+\b', resume_text.lower()))
            job_words = set(re.findall(r'\b\w+\b', job_text.lower()))
            
            # Calculate Jaccard similarity
            intersection = len(resume_words & job_words)
            union = len(resume_words | job_words)
            
            if union == 0:
                return 0
            
            similarity = (intersection / union) * 100
            return min(similarity, 100)
        except Exception as e:
            logger.error(f"Similarity computation error: {e}")
            return 0
    
    def extract_score(self, analysis_text):
        score_patterns = [
            r"Overall Score.*?(\d+)",
            r"Score.*?(\d+)",
            r"(\d+)/100",
            r"(\d+)%"
        ]
        
        for pattern in score_patterns:
            match = re.search(pattern, analysis_text, re.IGNORECASE)
            if match:
                return min(int(match.group(1)), 100)
        return None
    
    def create_gauge_chart(self, score, title="Resume Score"):
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': title},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 85], 'color': "gray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        fig.update_layout(height=300)
        return fig

def main():
    st.set_page_config(
        page_title="AI Resume Analyzer",
        page_icon="📄",
        layout="wide"
    )
    
    analyzer = ResumeAnalyzer()
    
    # Initialize session state
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []
    
    st.title("🎯 AI Resume Analyzer & Job Matcher")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        api_key = st.text_input(
            "OpenAI API Key", 
            type="password", 
            value=os.getenv("OPENAI_API_KEY", ""),
            help="Enter your OpenAI API key"
        )
        
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
        
        model_choice = st.selectbox(
            "AI Model",
            ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
            help="Choose the OpenAI model for analysis"
        )
        
        include_similarity = st.checkbox("Keyword Similarity Score", value=True)
        include_visualization = st.checkbox("Score Visualization", value=True)
        
        st.markdown("---")
        st.subheader("📊 History")
        st.write(f"Total Analyses: {len(st.session_state.analysis_history)}")
        if st.button("Clear History") and st.session_state.analysis_history:
            st.session_state.analysis_history = []
            st.rerun()
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["📄 Analysis", "📊 Analytics", "ℹ️ About"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📋 Job Description")
            job_method = st.radio("Input Method:", ["Text", "File"], key="job_method")
            
            if job_method == "Text":
                job_description = st.text_area(
                    "Job description:",
                    height=300,
                    placeholder="Paste the complete job description here...",
                    key="job_text_input"
                )
            else:
                job_file = st.file_uploader(
                    "Upload job file", 
                    type=['txt', 'pdf'], 
                    key="job_file",
                    help="Upload a text or PDF file containing the job description"
                )
                job_description = analyzer.read_file_content(job_file) if job_file else ""
                if job_description:
                    st.text_area("Extracted content:", job_description, height=200, disabled=True)
        
        with col2:
            st.subheader("👤 Resume")
            resume_method = st.radio("Input Method:", ["Text", "File"], key="resume_method")
            
            if resume_method == "Text":
                resume_text = st.text_area(
                    "Resume:",
                    height=300,
                    placeholder="Paste the complete resume here...",
                    key="resume_text_input"
                )
            else:
                resume_file = st.file_uploader(
                    "Upload resume", 
                    type=['txt', 'pdf'], 
                    key="resume_file",
                    help="Upload a text or PDF file containing the resume"
                )
                resume_text = analyzer.read_file_content(resume_file) if resume_file else ""
                if resume_text:
                    st.text_area("Extracted content:", resume_text, height=200, disabled=True)
        
        # Analysis button
        st.markdown("---")
        if st.button("🚀 Analyze Resume", type="primary", use_container_width=True):
            if not job_description.strip():
                st.error("Please provide a job description.")
            elif not resume_text.strip():
                st.error("Please provide a resume.")
            elif not os.getenv("OPENAI_API_KEY"):
                st.error("Please add your OpenAI API key in the sidebar.")
            else:
                with st.spinner("Analyzing resume... This may take a moment."):
                    # Perform analysis
                    analysis_result = analyzer.analyze_with_openai(job_description, resume_text, model_choice)
                    
                    # Compute similarity if enabled
                    similarity_score = None
                    if include_similarity:
                        similarity_score = analyzer.compute_basic_similarity(resume_text, job_description)
                    
                    # Extract overall score
                    overall_score = analyzer.extract_score(analysis_result)
                    
                    # Store results
                    analysis_data = {
                        'timestamp': datetime.now(),
                        'job_preview': job_description[:100] + "..." if len(job_description) > 100 else job_description,
                        'resume_preview': resume_text[:100] + "..." if len(resume_text) > 100 else resume_text,
                        'analysis': analysis_result,
                        'overall_score': overall_score,
                        'similarity_score': similarity_score,
                        'model_used': model_choice
                    }
                    st.session_state.analysis_history.append(analysis_data)
                
                # Display results
                st.markdown("---")
                st.subheader("📊 Analysis Results")
                
                # Visualizations
                if include_visualization and overall_score:
                    if similarity_score:
                        col1, col2 = st.columns(2)
                        with col1:
                            fig = analyzer.create_gauge_chart(overall_score, "AI Analysis Score")
                            st.plotly_chart(fig, use_container_width=True)
                        with col2:
                            fig_sim = analyzer.create_gauge_chart(similarity_score, "Keyword Similarity")
                            st.plotly_chart(fig_sim, use_container_width=True)
                    else:
                        fig = analyzer.create_gauge_chart(overall_score, "AI Analysis Score")
                        st.plotly_chart(fig, use_container_width=True)
                
                # Score metrics
                if overall_score or similarity_score:
                    cols = st.columns(3)
                    if overall_score:
                        cols[0].metric("AI Analysis Score", f"{overall_score}/100")
                    if similarity_score:
                        cols[1].metric("Keyword Similarity", f"{similarity_score:.1f}/100")
                    if overall_score and similarity_score:
                        avg_score = (overall_score + similarity_score) / 2
                        cols[2].metric("Average Score", f"{avg_score:.1f}/100")
                
                # Detailed analysis
                st.markdown("### 📋 Detailed Analysis")
                st.markdown(analysis_result)
                
                # Download report
                st.markdown("---")
                report_content = f"""RESUME ANALYSIS REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Model Used: {model_choice}

JOB DESCRIPTION:
{job_description}

CANDIDATE RESUME:
{resume_text}

ANALYSIS RESULTS:
{analysis_result}

SCORES:
AI Analysis Score: {overall_score}/100 if overall_score else 'Not extracted'
Keyword Similarity: {similarity_score:.1f}/100 if similarity_score else 'Not computed'
"""
                
                st.download_button(
                    label="📥 Download Analysis Report",
                    data=report_content,
                    file_name=f"resume_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
    
    with tab2:
        st.subheader("📈 Analytics Dashboard")
        
        if st.session_state.analysis_history:
            # Create analytics dataframe
            history_data = []
            for item in st.session_state.analysis_history:
                if item.get('overall_score') is not None:
                    history_data.append({
                        'timestamp': item['timestamp'],
                        'overall_score': item['overall_score'],
                        'similarity_score': item.get('similarity_score', 0),
                        'model_used': item.get('model_used', 'Unknown')
                    })
            
            if history_data:
                history_df = pd.DataFrame(history_data)
                
                # Summary metrics
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Analyses", len(history_df))
                col2.metric("Average AI Score", f"{history_df['overall_score'].mean():.1f}")
                col3.metric("Highest Score", f"{history_df['overall_score'].max()}")
                col4.metric("Lowest Score", f"{history_df['overall_score'].min()}")
                
                # Recent analyses table
                st.subheader("Recent Analyses")
                display_df = history_df.tail(10).copy()
                display_df['timestamp'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
                st.dataframe(display_df, use_container_width=True)
            else:
                st.info("No scored analyses available for visualization.")
        else:
            st.info("No analyses performed yet. Start analyzing resumes to see analytics!")
    
    with tab3:
        st.subheader("ℹ️ About AI Resume Analyzer")
        
        st.markdown("""
        ## Overview
        
        This AI-powered tool evaluates how well a candidate's resume matches a specific job description using advanced natural language processing.
        
        ## Scoring System (100 Points Total)
        
        - **Skills Match (25 points)** - Alignment between candidate skills and job requirements
        - **Experience Relevance (25 points)** - Depth and relevance of work experience
        - **Achievement Quality (15 points)** - Quantifiable accomplishments and impact
        - **Education & Certifications (10 points)** - Academic background and certifications
        - **Career Progression (10 points)** - Career growth and advancement trajectory
        - **Keyword Match (10 points)** - Industry-specific terminology usage
        - **Resume Quality (5 points)** - Organization, clarity, and presentation
        
        ## Features
        
        - **AI-Powered Analysis**: Uses OpenAI's language models for comprehensive evaluation
        - **Keyword Similarity**: Basic similarity scoring based on shared terminology
        - **File Support**: Accepts both text and PDF files for input
        - **Interactive Visualizations**: Score gauges and breakdown charts
        - **Analysis History**: Track and compare multiple analyses over time
        - **Export Functionality**: Download detailed analysis reports
        
        ## Getting Started
        
        1. **API Setup**: Enter your OpenAI API key in the sidebar configuration
        2. **Input Data**: Paste or upload both job description and resume
        3. **Select Model**: Choose from available OpenAI models
        4. **Analyze**: Click the analyze button to generate results
        
        ## Tips for Best Results
        
        - Provide complete, detailed job descriptions
        - Include comprehensive resume content with all relevant sections
        - Use clear, well-formatted text for better analysis
        - Compare multiple candidates for the same position
        
        ## Privacy & Security
        
        - Analysis is performed securely through OpenAI's API
        - No permanent data storage - all data is session-based
        - API keys are handled securely and not stored
        - Use the "Clear History" option to remove session data
        
        ---
        
        **Version**: 3.0  
        **Last Updated**: May 2025  
        **Built with**: Streamlit, OpenAI API, Plotly
        """)

if __name__ == "__main__":
    main()