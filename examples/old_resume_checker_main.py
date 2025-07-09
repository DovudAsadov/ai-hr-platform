import os
import gradio as gr
from openai import OpenAI
from dotenv import load_dotenv
import time
from sys_prompt import RESUME_ANALYSIS_PROMPT

# Load environment variables from .env file
load_dotenv()

# Configure OpenAI API
API_KEY = os.getenv("OPENAI_API_KEY")

def analyze_resume(job_description, resume, model="gpt-4o-mini"):
    """
    Analyze a resume against a job description using OpenAI API
    """
    try:
        if not job_description.strip() or not resume.strip():
            return "Please provide both a job description and resume."
        

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
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": RESUME_ANALYSIS_PROMPT},
                {"role": "user", "content": formatted_prompt}
            ],
            temperature=0.2,  # Setting a lower temperature for more consistent results
            max_tokens=4000
        )
        
        # Extract and display the response
        analysis = response.choices[0].message.content
        return analysis

    except Exception as e:
        return f"An error occurred: {str(e)}"
    

# Function to handle API selection
def analyze_with_selected_api(job_description, resume, progress=gr.Progress()):
    # Update progress
    # progress(0, desc="Starting analysis...")

    # Simulate API processing with progress updates
    # progress(0.3, desc="Processing job description...")
    # time.sleep(1)  # Simulate processing time
    # progress(0.5, desc="Analyzing resume...")
    # time.sleep(1)  # Simulate processing time
    # progress(0.7, desc="Calling OpenAI API...")
    result = analyze_resume(job_description, resume)
    
    # progress(1.0, desc="Analysis complete!")
    return result

# Create Gradio interface
def create_interface():
    # Define theme
    theme = gr.themes.Default()
    
    # Define interface
    with gr.Blocks(theme=theme, title="Resume Analyzer") as app:
        gr.Markdown("""
        # Resume Analyzer
        
        Upload a job description and resume to get an AI-powered analysis of how well the candidate matches the position.
        """)
        
        with gr.Row():
            with gr.Column():
                
                # File upload options
                with gr.Tab("Text Input"):
                    job_description = gr.Textbox(
                        label="Job Description",
                        placeholder="Paste the job description here...",
                        lines=10
                    )
                    resume = gr.Textbox(
                        label="Resume",
                        placeholder="Paste the candidate's resume here...",
                        lines=10
                    )
                
                with gr.Tab("File Upload"):
                    job_file = gr.File(label="Upload Job Description (TXT, PDF)")
                    resume_file = gr.File(label="Upload Resume (TXT, PDF)")
                    file_upload_button = gr.Button("Load Files")
                
                analyze_button = gr.Button("Analyze Resume", variant="primary")
            
            with gr.Column():
                output = gr.Markdown(label="Analysis Results")
                
        # Handle file uploads
        def process_files(job_file, resume_file):
            job_text = ""
            resume_text = ""
            
            try:
                # Process job description file
                if job_file is not None:
                    file_path = job_file.name
                    if file_path.endswith('.pdf'):
                        # For PDF files
                        import PyPDF2
                        with open(file_path, 'rb') as f:
                            pdf_reader = PyPDF2.PdfReader(f)
                            for page in pdf_reader.pages:
                                job_text += page.extract_text()
                    else:
                        # For text files
                        with open(file_path, 'r', encoding='utf-8') as f:
                            job_text = f.read()
                
                # Process resume file
                if resume_file is not None:
                    file_path = resume_file.name
                    if file_path.endswith('.pdf'):
                        # For PDF files
                        import PyPDF2
                        with open(file_path, 'rb') as f:
                            pdf_reader = PyPDF2.PdfReader(f)
                            for page in pdf_reader.pages:
                                resume_text += page.extract_text()
                    else:
                        # For text files
                        with open(file_path, 'r', encoding='utf-8') as f:
                            resume_text = f.read()
                
                return job_text, resume_text
            
            except Exception as e:
                return f"Error processing files: {str(e)}", ""
        
        file_upload_button.click(
            process_files,
            inputs=[job_file, resume_file],
            outputs=[job_description, resume]
        )
        
        # Handle analysis button
        analyze_button.click(
            analyze_with_selected_api,
            inputs=[job_description, resume],
            outputs=output
        )
    
        
        gr.Markdown("""
        ## How It Works
        
        1. Paste the job description and candidate's resume in the respective fields
        2. Or upload text/PDF files containing this information
        3. Select the AI provider you want to use
        4. Click "Analyze Resume" to get a detailed analysis
        
        The analysis includes a 0-100 score based on skills match, experience relevance, achievements, education, career progression, keyword match, and resume quality.
        
        **Note:** You need to set up your API keys in a `.env` file:
        ```
        OPENAI_API_KEY=your_openai_key_here
        ANTHROPIC_API_KEY=your_anthropic_key_here
        ```
        """)
    
    return app

# Create and launch the app
if __name__ == "__main__":
    app = create_interface()
    app.launch(share=True)