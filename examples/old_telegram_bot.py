import os
import logging
import time
import PyPDF2
import io
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, CallbackQueryHandler
from openai import OpenAI
from dotenv import load_dotenv
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from sys_prompt import RESUME_ANALYSIS_PROMPT_V1, RESUME_ANALYSIS_PROMPT_V2

RESUME_ANALYSIS_PROMPT = RESUME_ANALYSIS_PROMPT_V2
# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Configure API keys
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Check if keys are available
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN not found in .env file")
if not OPENAI_API_KEY:
    logger.warning("OpenAI API key not found. Please set OPENAI_API_KEY in your .env file.")


# States for conversation
CHOOSING_ACTION, AWAITING_JOB_DESCRIPTION, AWAITING_RESUME, AWAITING_MODEL_CHOICE, PROCESSING = range(5)

# User session data storage
user_data = {}

# Available models
AVAILABLE_MODELS = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send a welcome message when the command /start is issued."""
    user = update.effective_user
    user_id = user.id
    
    # Initialize user data if not exists
    if user_id not in user_data:
        user_data[user_id] = {
            "job_description": None,
            "resume": None,
            "model": "gpt-4o-mini"
        }
    
    await update.message.reply_text(
        f"👋 Hello {user.first_name}! I'm your Resume Analyzer Bot.\n\n"
        "I can help you analyze how well a resume matches a job description.\n\n"
        "Let's get started! Please choose an action:",
        reply_markup=get_main_menu_keyboard()
    )
    
    return CHOOSING_ACTION

def get_main_menu_keyboard():
    """Create main menu keyboard"""
    keyboard = [
        [InlineKeyboardButton("Submit Job Description", callback_data="submit_job")],
        [InlineKeyboardButton("Submit Resume", callback_data="submit_resume")],
        [InlineKeyboardButton("Select AI Model", callback_data="select_model")],
        [InlineKeyboardButton("Start Analysis", callback_data="analyze")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_model_selection_keyboard():
    """Create model selection keyboard"""
    keyboard = []
    for model in AVAILABLE_MODELS:
        keyboard.append([InlineKeyboardButton(model, callback_data=f"model_{model}")])
    keyboard.append([InlineKeyboardButton("Back to Main Menu", callback_data="back_to_menu")])
    return InlineKeyboardMarkup(keyboard)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle button clicks"""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    if query.data == "submit_job":
        await query.edit_message_text(
            "📝 Please send me the job description as text, link or upload a PDF/TXT file."
        )
        return AWAITING_JOB_DESCRIPTION
    
    elif query.data == "submit_resume":
        await query.edit_message_text(
            "📄 Please send me the resume as text or upload a PDF/TXT file."
        )
        return AWAITING_RESUME
    
    elif query.data == "select_model":
        await query.edit_message_text(
            "🤖 Please select the AI model for analysis:",
            reply_markup=get_model_selection_keyboard()
        )
        return AWAITING_MODEL_CHOICE
    
    elif query.data.startswith("model_"):
        model = query.data.replace("model_", "")
        user_data[user_id]["model"] = model
        await query.edit_message_text(
            f"✅ AI model selected: {model}\n\nWhat would you like to do next?",
            reply_markup=get_main_menu_keyboard()
        )
        return CHOOSING_ACTION
    
    elif query.data == "back_to_menu":
        await query.edit_message_text(
            "Please choose an action:",
            reply_markup=get_main_menu_keyboard()
        )
        return CHOOSING_ACTION
    
    elif query.data == "analyze":
        # Check if both job description and resume are provided
        if not user_data[user_id]["job_description"]:
            await query.edit_message_text(
                "❌ Job description is missing. Please submit job description first.",
                reply_markup=get_main_menu_keyboard()
            )
            return CHOOSING_ACTION
        
        if not user_data[user_id]["resume"]:
            await query.edit_message_text(
                "❌ Resume is missing. Please submit resume first.",
                reply_markup=get_main_menu_keyboard()
            )
            return CHOOSING_ACTION
        
        # Start analysis
        await query.edit_message_text("🔄 Processing your request. This may take a moment...")
        
        # Get the analysis result
        job_description = user_data[user_id]["job_description"]
        resume = user_data[user_id]["resume"]
        model = user_data[user_id]["model"]
        
        # Process in the background to avoid blocking
        context.application.create_task(
            process_analysis(update, context, user_id, job_description, resume, model)
        )
        
        return PROCESSING

async def process_analysis(update, context, user_id, job_description, resume, model):
    """Process analysis in the background"""
    try:
        result = analyze_resume(job_description, resume, model)
        # Split result if too long for a single message
        if len(result) > 4000:
            parts = [result[i:i+4000] for i in range(0, len(result), 4000)]
            for i, part in enumerate(parts):
                if i == 0:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=f"Analysis Results (Part {i+1}/{len(parts)}):\n\n{part}",
                        parse_mode="Markdown"
                    )
                else:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=f"Analysis Results (Part {i+1}/{len(parts)}):\n\n{part}",
                        parse_mode="Markdown"
                    )
        else:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"Analysis Results:\n\n{result}",
                parse_mode="Markdown"
            )
    except Exception as e:
        logger.error(f"Error in analysis: {str(e)}")
        await context.bot.send_message(
            chat_id=user_id,
            text=f"❌ An error occurred during analysis: {str(e)}"
        )
    
    # Return to main menu
    await context.bot.send_message(
        chat_id=user_id,
        text="What would you like to do next?",
        reply_markup=get_main_menu_keyboard()
    )

# async def receive_job_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Handle receiving job description"""
#     user_id = update.effective_user.id
    
#     # Check if it's a document or text
#     if update.message.document:
#         # It's a file
#         file = await update.message.document.get_file()
#         file_name = update.message.document.file_name
        
#         if file_name.lower().endswith(('.pdf', '.txt')):
#             try:
#                 # Download the file
#                 file_bytes = await file.download_as_bytearray()
#                 file_io = io.BytesIO(file_bytes)
                
#                 # Process based on file type
#                 if file_name.lower().endswith('.pdf'):
#                     text = extract_text_from_pdf(file_io)
#                 else:  # txt
#                     text = file_io.getvalue().decode('utf-8', errors='replace')
                
#                 user_data[user_id]["job_description"] = text
#                 await update.message.reply_text(
#                     "✅ Job description file received and processed successfully!\n\n"
#                     f"Length: {len(text)} characters\n\n"
#                     "What would you like to do next?",
#                     reply_markup=get_main_menu_keyboard()
#                 )
#             except Exception as e:
#                 logger.error(f"Error processing file: {str(e)}")
#                 await update.message.reply_text(
#                     f"❌ Error processing your file: {str(e)}\n\n"
#                     "Please try again or send the job description as text.",
#                     reply_markup=get_main_menu_keyboard()
#                 )
#         else:
#             await update.message.reply_text(
#                 "❌ Unsupported file format. Please upload a PDF or TXT file, or send the job description as text.",
#                 reply_markup=get_main_menu_keyboard()
#             )
#     else:
#         # It's text
#         text = update.message.text
#         user_data[user_id]["job_description"] = text
#         await update.message.reply_text(
#             "✅ Job description received!\n\n"
#             f"Length: {len(text)} characters\n\n"
#             "What would you like to do next?",
#             reply_markup=get_main_menu_keyboard()
#         )
    
#     return CHOOSING_ACTION


async def receive_job_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle receiving job description"""
    user_id = update.effective_user.id
    
    # Check if it's a document or text
    if update.message.document:
        # It's a file
        file = await update.message.document.get_file()
        file_name = update.message.document.file_name
        
        if file_name.lower().endswith(('.pdf', '.txt')):
            try:
                # Download the file
                file_bytes = await file.download_as_bytearray()
                file_io = io.BytesIO(file_bytes)
                
                # Process based on file type
                if file_name.lower().endswith('.pdf'):
                    text = extract_text_from_pdf(file_io)
                else:  # txt
                    text = file_io.getvalue().decode('utf-8', errors='replace')
                
                user_data[user_id]["job_description"] = text
                await update.message.reply_text(
                    "✅ Job description file received and processed successfully!\n\n"
                    f"Length: {len(text)} characters\n\n"
                    "What would you like to do next?",
                    reply_markup=get_main_menu_keyboard()
                )
            except Exception as e:
                logger.error(f"Error processing file: {str(e)}")
                await update.message.reply_text(
                    f"❌ Error processing your file: {str(e)}\n\n"
                    "Please try again or send the job description as text.",
                    reply_markup=get_main_menu_keyboard()
                )
        else:
            await update.message.reply_text(
                "❌ Unsupported file format. Please upload a PDF or TXT file, or send the job description as text.",
                reply_markup=get_main_menu_keyboard()
            )
    else:
        # It's text
        text = update.message.text
        
        # Check if it's a URL
        url_pattern = re.compile(r'https?://\S+')
        if url_pattern.match(text.strip()):
            try:
                await update.message.reply_text(
                    "🔍 Detecting a URL. Attempting to scrape the job description...",
                    reply_markup=get_main_menu_keyboard()
                )
                
                # Extract job description from the URL
                text = await scrape_job_description(text.strip())
                
                user_data[user_id]["job_description"] = text
                await update.message.reply_text(
                    "✅ Job description successfully scraped from the provided URL!\n\n"
                    f"Length: {len(text)} characters\n\n"
                    "What would you like to do next?",
                    reply_markup=get_main_menu_keyboard()
                )
            except Exception as e:
                logger.error(f"Error scraping URL: {str(e)}")
                await update.message.reply_text(
                    f"❌ Error scraping the URL: {str(e)}\n\n"
                    "Please try again with a different URL or send the job description directly.",
                    reply_markup=get_main_menu_keyboard()
                )
        else:
            # Regular text input
            user_data[user_id]["job_description"] = text
            await update.message.reply_text(
                "✅ Job description received!\n\n"
                f"Length: {len(text)} characters\n\n"
                "What would you like to do next?",
                reply_markup=get_main_menu_keyboard()
            )
    
    return CHOOSING_ACTION

async def scrape_job_description(url):
    """Scrape job description from URL"""
    # Add headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Get the domain to handle site-specific scraping
    domain = urlparse(url).netloc
    
    # Make the request
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an exception for bad status codes
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Site-specific scraping logic
    if 'linkedin.com' in domain:
        # LinkedIn job posts typically have job descriptions in elements with these classes
        job_description = soup.find('div', {'class': 'description__text'})
        if job_description:
            return job_description.get_text(separator='\n', strip=True)
    elif 'indeed.com' in domain:
        # Indeed job posts
        job_description = soup.find('div', {'id': 'jobDescriptionText'})
        if job_description:
            return job_description.get_text(separator='\n', strip=True)
    elif 'glassdoor.com' in domain:
        # Glassdoor job posts
        job_description = soup.find('div', {'class': 'jobDescriptionContent'})
        if job_description:
            return job_description.get_text(separator='\n', strip=True)
    
    # Generic approach - look for common job description containers
    # Try to find content in article tags
    article = soup.find('article')
    if article:
        return article.get_text(separator='\n', strip=True)
    
    # Try to find content in main tag
    main_content = soup.find('main')
    if main_content:
        return main_content.get_text(separator='\n', strip=True)
    
    # Look for sections with keywords that might indicate job descriptions
    potential_containers = soup.find_all(['div', 'section'], string=re.compile(r'job description|responsibilities|requirements', re.I))
    if potential_containers:
        # Get the largest text block, which is likely the job description
        return max([container.get_text(separator='\n', strip=True) for container in potential_containers], key=len)
    
    # If all else fails, extract all the text from the body
    body = soup.find('body')
    if body:
        # Clean up the text - remove scripts, styles, etc.
        for script in body(['script', 'style', 'nav', 'header', 'footer']):
            script.extract()
        
        text = body.get_text(separator='\n', strip=True)
        # Return a reasonable chunk of the page that might contain the job description
        return text[:50000]  # Limit to a reasonable size
    
    raise ValueError("Could not extract job description content from the provided URL")

async def receive_resume(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle receiving resume"""
    user_id = update.effective_user.id
    
    # Check if it's a document or text
    if update.message.document:
        # It's a file
        file = await update.message.document.get_file()
        file_name = update.message.document.file_name
        
        if file_name.lower().endswith(('.pdf', '.txt')):
            try:
                # Download the file
                file_bytes = await file.download_as_bytearray()
                file_io = io.BytesIO(file_bytes)
                
                # Process based on file type
                if file_name.lower().endswith('.pdf'):
                    text = extract_text_from_pdf(file_io)
                else:  # txt
                    text = file_io.getvalue().decode('utf-8', errors='replace')
                
                user_data[user_id]["resume"] = text
                await update.message.reply_text(
                    "✅ Resume file received and processed successfully!\n\n"
                    f"Length: {len(text)} characters\n\n"
                    "What would you like to do next?",
                    reply_markup=get_main_menu_keyboard()
                )
            except Exception as e:
                logger.error(f"Error processing file: {str(e)}")
                await update.message.reply_text(
                    f"❌ Error processing your file: {str(e)}\n\n"
                    "Please try again or send the resume as text.",
                    reply_markup=get_main_menu_keyboard()
                )
        else:
            await update.message.reply_text(
                "❌ Unsupported file format. Please upload a PDF or TXT file, or send the resume as text.",
                reply_markup=get_main_menu_keyboard()
            )
    else:
        # It's text
        text = update.message.text
        user_data[user_id]["resume"] = text
        await update.message.reply_text(
            "✅ Resume received!\n\n"
            f"Length: {len(text)} characters\n\n"
            "What would you like to do next?",
            reply_markup=get_main_menu_keyboard()
        )
    
    return CHOOSING_ACTION

def extract_text_from_pdf(file_obj):
    """Extract text from a PDF file object"""
    try:
        pdf_reader = PyPDF2.PdfReader(file_obj)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise Exception(f"Error extracting text from PDF: {str(e)}")

def analyze_resume(job_description, resume, model="gpt-4o-mini"):
    """
    Analyze a resume against a job description using OpenAI API
    """
    try:
        if not job_description.strip() or not resume.strip():
            return "Please provide both a job description and resume."
        
        logger.info("Starting resume analysis")
        
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

        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Call OpenAI API
        logger.info(f"Calling OpenAI API with model: {model}")
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
        logger.info(f"API call completed in {elapsed_time:.2f} seconds")
        
        # Extract and display the response
        analysis = response.choices[0].message.content
        return analysis

    except Exception as e:
        logger.error(f"Error in analyze_resume: {str(e)}")
        return f"An error occurred: {str(e)}"

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = (
        "🤖 *Resume Analyzer Bot Help*\n\n"
        "This bot helps you analyze how well a resume matches a job description.\n\n"
        "*Commands:*\n"
        "/start - Start the bot and show main menu\n"
        "/help - Show this help message\n"
        "/status - Check your current submission status\n"
        "/reset - Reset your data and start over\n\n"
        "*How to use:*\n"
        "1. Submit a job description (text or PDF/TXT file)\n"
        "2. Submit a resume (text or PDF/TXT file)\n"
        "3. Optionally select an AI model\n"
        "4. Start the analysis\n\n"
        "The analysis will provide a match score and detailed feedback on how well the resume fits the job requirements."
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show current status of user submissions."""
    user_id = update.effective_user.id
    
    if user_id not in user_data:
        user_data[user_id] = {
            "job_description": None,
            "resume": None,
            "model": "gpt-4o-mini"
        }
    
    job_status = "✅ Submitted" if user_data[user_id]["job_description"] else "❌ Not submitted"
    resume_status = "✅ Submitted" if user_data[user_id]["resume"] else "❌ Not submitted"
    model = user_data[user_id]["model"]
    
    status_text = (
        "📊 *Current Status*\n\n"
        f"Job Description: {job_status}\n"
        f"Resume: {resume_status}\n"
        f"Selected Model: {model}\n\n"
    )
    
    if user_data[user_id]["job_description"] and user_data[user_id]["resume"]:
        status_text += "You're ready to start the analysis! 🚀"
    else:
        status_text += "Please submit the missing items before starting analysis."
    
    await update.message.reply_text(
        status_text, 
        parse_mode="Markdown",
        reply_markup=get_main_menu_keyboard()
    )
    
    return CHOOSING_ACTION

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Reset user data and start over."""
    user_id = update.effective_user.id
    
    # Reset user data
    user_data[user_id] = {
        "job_description": None,
        "resume": None,
        "model": "gpt-4o-mini"
    }
    
    await update.message.reply_text(
        "🔄 All your data has been reset. You can start fresh now!",
        reply_markup=get_main_menu_keyboard()
    )
    
    return CHOOSING_ACTION

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the conversation."""
    await update.message.reply_text(
        "Operation cancelled. What would you like to do?",
        reply_markup=get_main_menu_keyboard()
    )
    return CHOOSING_ACTION

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Setup conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING_ACTION: [
                CallbackQueryHandler(button_handler),
                CommandHandler("status", status_command),
                CommandHandler("reset", reset_command),
            ],
            AWAITING_JOB_DESCRIPTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_job_description),
                MessageHandler(filters.Document.ALL, receive_job_description),
                CommandHandler("cancel", cancel),
            ],
            AWAITING_RESUME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_resume),
                MessageHandler(filters.Document.ALL, receive_resume),
                CommandHandler("cancel", cancel),
            ],
            AWAITING_MODEL_CHOICE: [
                CallbackQueryHandler(button_handler),
                CommandHandler("cancel", cancel),
            ],
            PROCESSING: [
                CallbackQueryHandler(button_handler),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", help_command))

    # Start the Bot
    logger.info("Starting bot...")
    application.run_polling()

if __name__ == "__main__":
    main()