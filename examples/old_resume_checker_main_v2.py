import os
import gradio as gr
from openai import OpenAI
from dotenv import load_dotenv
import time
import PyPDF2
import io
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables from .env file
load_dotenv()

# Configure OpenAI API
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    logging.warning("OpenAI API key not found. Please set OPENAI_API_KEY in your .env file.")

# Import system prompt if available, otherwise define a default
try:
    from sys_prompt import RESUME_ANALYSIS_PROMPT
except ImportError:
    logging.warning("sys_prompt.py not found. Using default system prompt.")
    RESUME_ANALYSIS_PROMPT = """
    You are an expert resume analyzer. Analyze the provided resume against the job description.
    Provide a detailed analysis including:
    
    1. Match Score: Give a score from 0-100 based on how well the candidate matches the job.
    2. Skills Assessment: Evaluate how well the candidate's skills match the requirements.
    3. Experience Relevance: Assess how relevant the candidate's experience is.
    4. Key Strengths: Identify the candidate's strongest qualifications for this position.
    5. Improvement Areas: Suggest areas where the candidate could improve their resume.
    6. Recommendation: Provide a final recommendation on whether to interview the candidate.
    
    Format your response in Markdown for better readability.
    """

def extract_text_from_pdf(file_obj):
    """Extract text from a PDF file object"""
    try:
        if hasattr(file_obj, 'name'):  # If it's a file path
            with open(file_obj.name, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() or ""
        else:  # If it's a file-like object
            pdf_reader = PyPDF2.PdfReader(file_obj)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() or ""
        return text
    except Exception as e:
        logging.error(f"Error extracting text from PDF: {str(e)}")
        return f"Error extracting text: {str(e)}"

def read_file_content(file):
    """Read content from uploaded file (text or PDF)"""
    if file is None:
        return ""
    
    try:
        if isinstance(file, str):  # If it's already text
            return file
            
        file_type = file.name.split('.')[-1].lower() if hasattr(file, 'name') else ""
        
        if file_type == 'pdf':
            return extract_text_from_pdf(file)
        else:  # Assume text file
            if hasattr(file, 'name'):
                with open(file.name, 'r', encoding='utf-8', errors='replace') as f:
                    return f.read()
            else:
                content = file.read()
                if isinstance(content, bytes):
                    return content.decode('utf-8', errors='replace')
                return content
    except Exception as e:
        logging.error(f"Error reading file: {str(e)}")
        return f"Error reading file: {str(e)}"

def analyze_resume(job_description, resume, model="gpt-4o-mini"):
    """
    Analyze a resume against a job description using OpenAI API
    """
    try:
        if not job_description.strip() or not resume.strip():
            return "Please provide both a job description and resume."
        
        logging.info("Starting resume analysis")
        
        user_query = """
        ## Job Description:
        {job_description}

        ## Candidate Resume:
        {resume}"""
        
        # Format the prompt with job description and resume
        formatted_prompt = user_query.format(
            job_description=job_description,
            resume=resume
        )

        client = OpenAI(api_key=API_KEY)
        
        # Call OpenAI API
        logging.info(f"Calling OpenAI API with model: {model}")
        start_time = time.time()
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": RESUME_ANALYSIS_PROMPT},
                {"role": "user", "content": formatted_prompt}
            ],
            temperature=0.2,  # Setting a lower temperature for more consistent results
            max_tokens=4000
        )
        
        elapsed_time = time.time() - start_time
        logging.info(f"API call completed in {elapsed_time:.2f} seconds")
        
        # Extract and display the response
        analysis = response.choices[0].message.content
        return analysis

    except Exception as e:
        logging.error(f"Error in analyze_resume: {str(e)}")
        return f"An error occurred: {str(e)}"

def analyze_with_progress(job_description, resume, progress=gr.Progress()):
    """Handle analysis with progress updates"""
    progress(0, desc="Starting analysis...")
    
    # Process file uploads if needed
    if hasattr(job_description, 'name'):
        progress(0.2, desc="Processing job description file...")
        job_description = read_file_content(job_description)
    
    if hasattr(resume, 'name'):
        progress(0.4, desc="Processing resume file...")
        resume = read_file_content(resume)
    
    progress(0.6, desc="Analyzing resume against job description...")
    result = analyze_resume(job_description, resume)
    
    progress(1.0, desc="Analysis complete!")
    return result

def update_job_description(file):
    """Process uploaded job description file and return its content"""
    if file is None:
        return ""
    return read_file_content(file)

def update_resume(file):
    """Process uploaded resume file and return its content"""
    if file is None:
        return ""
    return read_file_content(file)

def create_interface():
    """Create the Gradio interface"""
    # Define custom theme
    theme = gr.themes.Default(
        # primary_hue="blue",
        # secondary_hue="indigo",
    )
    
    # Define interface
    with gr.Blocks(theme=theme, title="Resume Analyzer", css="""
        .gradio-container {max-width: 1200px; margin: auto;}
        .file-upload {margin-bottom: 10px;}
    """) as app:
        gr.Markdown("""
        # 📄 Resume Analyzer
        
        Upload a job description and resume to get an AI-powered analysis of how well the candidate matches the position.
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                # Job Description Section
                gr.Markdown("### Job Description")
                job_description_text = gr.Textbox(
                    placeholder="Paste the job description here or upload a file...",
                    lines=10,
                    label="Job Description"
                )
                job_file_upload = gr.File(
                    label="Or upload job description (TXT, PDF)",
                    file_types=[".txt", ".pdf"]
                )
                
                # Resume Section
                gr.Markdown("### Resume")
                resume_text = gr.Textbox(
                    placeholder="Paste the candidate's resume here or upload a file...",
                    lines=10,
                    label="Resume"
                )
                resume_file_upload = gr.File(
                    label="Or upload resume (TXT, PDF)",
                    file_types=[".txt", ".pdf"]
                )
                
                # model_choice = gr.Dropdown(
                #     choices=["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
                #     value="gpt-4o-mini",
                #     label="Select AI Model"
                # )
                
                analyze_button = gr.Button("Analyze Resume", variant="primary", size="lg")
            
            with gr.Column(scale=1):
                output = gr.Markdown(label="Analysis Results")
        
        # Handle file uploads
        job_file_upload.change(
            update_job_description,
            inputs=[job_file_upload],
            outputs=[job_description_text]
        )
        
        resume_file_upload.change(
            update_resume,
            inputs=[resume_file_upload],
            outputs=[resume_text]
        )
        
        # Handle analysis button
        analyze_button.click(
            analyze_with_progress,
            inputs=[job_description_text, resume_text],
            outputs=output
        )
    
        gr.Markdown("""
        ## How It Works
        
        1. Paste the job description and candidate's resume in the text fields OR upload files containing this information
        2. Select the AI model you want to use
        3. Click "Analyze Resume" to get a detailed analysis
        
        The analysis includes a detailed evaluation of the candidate's fit for the position, including skills match, 
        experience relevance, key strengths, areas for improvement, and an overall recommendation.
        """)
    
    return app

# Create and launch the app
if __name__ == "__main__":
    try:
        app = create_interface()
        app.launch(
            share=True, 
            server_name="0.0.0.0",  # Bind to all interfaces
            server_port=7860,       # Default Gradio port
            debug=False,            # Disable debug mode for production\
        )
    except Exception as e:
        logging.error(f"Error launching app: {str(e)}")
        print(f"Error launching app: {str(e)}")