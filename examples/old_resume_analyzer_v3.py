import os
import streamlit as st
import openai
from dotenv import load_dotenv
import PyPDF2
import logging
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re

# Load environment variables
load_dotenv()

# Configure logging
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
        self.similarity_model = None
        
    @st.cache_resource
    def load_similarity_model(_self):
        try:
            return SentenceTransformer("all-MiniLM-L6-v2")
        except Exception as e:
            logger.error(f"Failed to load similarity model: {e}")
            return None
    
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
            
            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
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
    
    def compute_similarity_score(self, resume_text, job_text):
        try:
            if not self.similarity_model:
                self.similarity_model = self.load_similarity_model()
            
            if not self.similarity_model:
                return 0
            
            resume_embedding = self.similarity_model.encode([resume_text])[0]
            job_embedding = self.similarity_model.encode([job_text])[0]
            similarity = cosine_similarity([resume_embedding], [job_embedding])[0][0]
            return similarity * 100
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
    
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []
    
    st.title("🎯 AI Resume Analyzer & Job Matcher")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        api_key = st.text_input("OpenAI API Key", type="password", 
                               value=os.getenv("OPENAI_API_KEY", ""))
        
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
        
        model_choice = st.selectbox(
            "AI Model",
            ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]
        )
        
        include_similarity = st.checkbox("Semantic Similarity Score", value=True)
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
                    placeholder="Paste job description here..."
                )
            else:
                job_file = st.file_uploader("Upload job file", type=['txt', 'pdf'], key="job_file")
                job_description = analyzer.read_file_content(job_file)
                if job_description:
                    st.text_area("Extracted:", job_description, height=200, disabled=True)
        
        with col2:
            st.subheader("👤 Resume")
            resume_method = st.radio("Input Method:", ["Text", "File"], key="resume_method")
            
            if resume_method == "Text":
                resume_text = st.text_area(
                    "Resume:",
                    height=300,
                    placeholder="Paste resume here..."
                )
            else:
                resume_file = st.file_uploader("Upload resume", type=['txt', 'pdf'], key="resume_file")
                resume_text = analyzer.read_file_content(resume_file)
                if resume_text:
                    st.text_area("Extracted:", resume_text, height=200, disabled=True)
        
        # Analysis
        st.markdown("---")
        if st.button("🚀 Analyze Resume", type="primary", use_container_width=True):
            if not job_description.strip() or not resume_text.strip():
                st.error("Please provide both job description and resume.")
            else:
                with st.spinner("Analyzing..."):
                    analysis_result = analyzer.analyze_with_openai(job_description, resume_text, model_choice)
                    
                    similarity_score = None
                    if include_similarity:
                        similarity_score = analyzer.compute_similarity_score(resume_text, job_description)
                    
                    overall_score = analyzer.extract_score(analysis_result)
                    
                    # Store results
                    analysis_data = {
                        'timestamp': datetime.now(),
                        'job_preview': job_description[:100] + "...",
                        'resume_preview': resume_text[:100] + "...",
                        'analysis': analysis_result,
                        'overall_score': overall_score,
                        'similarity_score': similarity_score,
                        'model_used': model_choice
                    }
                    st.session_state.analysis_history.append(analysis_data)
                
                # Display results
                st.markdown("---")
                st.subheader("📊 Results")
                
                if include_visualization and overall_score:
                    col1, col2 = st.columns(2)
                    with col1:
                        fig = analyzer.create_gauge_chart(overall_score, "AI Analysis Score")
                        st.plotly_chart(fig, use_container_width=True)
                    
                    if similarity_score:
                        with col2:
                            fig_sim = analyzer.create_gauge_chart(similarity_score, "Similarity Score")
                            st.plotly_chart(fig_sim, use_container_width=True)
                
                # Metrics
                if overall_score or similarity_score:
                    col1, col2, col3 = st.columns(3)
                    if overall_score:
                        col1.metric("AI Score", f"{overall_score}/100")
                    if similarity_score:
                        col2.metric("Similarity", f"{similarity_score:.1f}/100")
                    if overall_score and similarity_score:
                        avg = (overall_score + similarity_score) / 2
                        col3.metric("Average", f"{avg:.1f}/100")
                
                st.markdown("### 📋 Analysis Details")
                st.markdown(analysis_result)
                
                # Download
                report_data = f"""RESUME ANALYSIS REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Model: {model_choice}

JOB DESCRIPTION:
{job_description}

RESUME:
{resume_text}

ANALYSIS:
{analysis_result}

SCORES:
AI Score: {overall_score}/100
Similarity: {similarity_score:.1f}/100 if similarity_score else 'N/A'
"""
                st.download_button(
                    "📥 Download Report",
                    report_data,
                    file_name=f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
    
    with tab2:
        st.subheader("📈 Analytics Dashboard")
        
        if st.session_state.analysis_history:
            history_df = pd.DataFrame([
                {
                    'timestamp': item['timestamp'],
                    'overall_score': item.get('overall_score', 0),
                    'similarity_score': item.get('similarity_score', 0),
                    'model_used': item.get('model_used', 'Unknown')
                }
                for item in st.session_state.analysis_history
                if item.get('overall_score') is not None
            ])
            
            if not history_df.empty:
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total", len(history_df))
                col2.metric("Avg Score", f"{history_df['overall_score'].mean():.1f}")
                col3.metric("Max Score", f"{history_df['overall_score'].max()}")
                col4.metric("Min Score", f"{history_df['overall_score'].min()}")
                
                st.subheader("Recent Analyses")
                recent_df = history_df.tail(10).copy()
                recent_df['timestamp'] = recent_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
                st.dataframe(recent_df, use_container_width=True)
            else:
                st.info("No data for visualization.")
        else:
            st.info("No analyses yet. Start analyzing to see stats!")
    
    with tab3:
        st.subheader("ℹ️ About")
        
        st.markdown("""
        ## AI Resume Analyzer
        
        This tool uses advanced AI to evaluate resume-job fit across 7 key criteria:
        
        **Scoring System (100 points total):**
        - Skills Match (25 pts) - Technical and soft skills alignment
        - Experience Relevance (25 pts) - Work history relevance  
        - Achievement Quality (15 pts) - Quantifiable accomplishments
        - Education & Certifications (10 pts) - Academic qualifications
        - Career Progression (10 pts) - Growth trajectory
        - Keyword Match (10 pts) - Industry terminology
        - Resume Quality (5 pts) - Presentation and organization
        
        **Features:**
        - AI-powered comprehensive analysis
        - Semantic similarity scoring
        - PDF and text file support
        - Interactive score visualizations
        - Analysis history tracking
        - Downloadable reports
        
        **Getting Started:**
        1. Add your OpenAI API key in the sidebar
        2. Input or upload job description and resume
        3. Click "Analyze Resume" for results
        
        **Tips:**
        - Use complete, detailed job descriptions
        - Include full resume content
        - Compare multiple candidates for best results
        """)

if __name__ == "__main__":
    main()