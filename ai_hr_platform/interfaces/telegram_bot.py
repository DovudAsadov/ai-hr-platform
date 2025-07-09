"""Telegram bot interface for AI HR Platform."""

import asyncio
import logging
from typing import Optional
from pathlib import Path
import tempfile
import os

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler,
    ContextTypes,
    filters
)

from ..core import ResumeAnalyzer, ResumeOptimizer
from ..config import Config


class TelegramBot:
    """Telegram bot interface for the AI HR Platform."""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize the Telegram bot."""
        self.config = config or Config()
        self.analyzer = ResumeAnalyzer(self.config.to_dict())
        self.optimizer = ResumeOptimizer(self.config.to_dict())
        self.application = None
        self.logger = logging.getLogger(__name__)
        self._setup_bot()
    
    def _setup_bot(self):
        """Set up the Telegram bot application."""
        token = self.config.get('telegram_bot_token')
        if not token:
            raise ValueError("Telegram bot token not configured")
        
        # Create application
        self.application = Application.builder().token(token).build()
        
        # Add handlers
        self.application.add_handler(CommandHandler("start", self._start_command))
        self.application.add_handler(CommandHandler("help", self._help_command))
        self.application.add_handler(CommandHandler("analyze", self._analyze_command))
        self.application.add_handler(CommandHandler("optimize", self._optimize_command))
        
        # Message handlers
        self.application.add_handler(
            MessageHandler(filters.Document.PDF, self._handle_pdf_document)
        )
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_text_message)
        )
        
        # Callback query handler
        self.application.add_handler(CallbackQueryHandler(self._handle_callback_query))
    
    async def _start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /start command."""
        welcome_message = """
🤖 Welcome to AI HR Platform Bot!

I can help you with:
📄 Resume Analysis - Get professional feedback on your resume
✨ Resume Optimization - Improve your resume for better results

Commands:
/analyze - Analyze your resume
/optimize - Optimize your resume
/help - Show this help message

Just send me your resume as a PDF file or paste the text!
        """
        
        keyboard = [
            [
                InlineKeyboardButton("📄 Analyze Resume", callback_data="analyze"),
                InlineKeyboardButton("✨ Optimize Resume", callback_data="optimize")
            ],
            [InlineKeyboardButton("❓ Help", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_message, reply_markup=reply_markup)
    
    async def _help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /help command."""
        help_message = """
🤖 AI HR Platform Bot Help

📄 **Resume Analysis**:
- Upload a PDF resume file
- Or use /analyze command and paste your resume text
- Get detailed professional feedback

✨ **Resume Optimization**:
- Upload a PDF resume file  
- Or use /optimize command and paste your resume text
- Get an improved version of your resume

💡 **Tips**:
- PDF files work best for analysis
- Make sure your resume text is clear and complete
- The bot uses AI to provide professional HR insights

Commands:
/start - Start the bot
/analyze - Analyze your resume
/optimize - Optimize your resume
/help - Show this help
        """
        
        await update.message.reply_text(help_message)
    
    async def _analyze_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /analyze command."""
        await update.message.reply_text(
            "📄 **Resume Analysis Mode**\n\n"
            "Please send me your resume as:\n"
            "• PDF file (recommended)\n"
            "• Or paste your resume text in the next message"
        )
        
        # Set user state for analysis
        context.user_data['mode'] = 'analyze'
    
    async def _optimize_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /optimize command."""
        await update.message.reply_text(
            "✨ **Resume Optimization Mode**\n\n"
            "Please send me your resume as:\n"
            "• PDF file (recommended)\n"
            "• Or paste your resume text in the next message"
        )
        
        # Set user state for optimization
        context.user_data['mode'] = 'optimize'
    
    async def _handle_pdf_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle PDF document uploads."""
        try:
            # Get the file
            file = await update.message.document.get_file()
            
            # Download to temporary file
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                await file.download_to_drive(tmp_file.name)
                pdf_path = Path(tmp_file.name)
            
            # Extract text
            resume_text = self.analyzer.extract_text_from_pdf(pdf_path)
            
            # Clean up
            os.unlink(pdf_path)
            
            if not resume_text:
                await update.message.reply_text(
                    "❌ Could not extract text from the PDF. Please try again with a different file."
                )
                return
            
            # Determine mode and process
            mode = context.user_data.get('mode', 'analyze')
            await self._process_resume(update, context, resume_text, mode)
            
        except Exception as e:
            self.logger.error(f"Error processing PDF: {str(e)}")
            await update.message.reply_text(
                "❌ Error processing the PDF file. Please try again."
            )
    
    async def _handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages."""
        text = update.message.text.strip()
        
        if len(text) < 100:
            await update.message.reply_text(
                "📝 The text seems too short for a resume. Please provide more detailed resume content."
            )
            return
        
        # Determine mode and process
        mode = context.user_data.get('mode', 'analyze')
        await self._process_resume(update, context, text, mode)
    
    async def _process_resume(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                             resume_text: str, mode: str):
        """Process resume text based on mode."""
        try:
            # Show processing message
            processing_msg = await update.message.reply_text("🔄 Processing your resume...")
            
            if mode == 'optimize':
                result = self.optimizer.process(resume_text)
                if result.get("status") == "success":
                    response = f"✨ **Optimized Resume**\n\n{result['optimized_resume']}"
                else:
                    response = f"❌ Optimization failed: {result.get('error', 'Unknown error')}"
            else:  # analyze
                result = self.analyzer.process(resume_text)
                if result.get("status") == "success":
                    response = f"📄 **Resume Analysis**\n\n{result['analysis']}"
                else:
                    response = f"❌ Analysis failed: {result.get('error', 'Unknown error')}"
            
            # Delete processing message
            await processing_msg.delete()
            
            # Send result (split if too long)
            if len(response) > 4000:
                # Split into chunks
                chunks = [response[i:i+4000] for i in range(0, len(response), 4000)]
                for chunk in chunks:
                    await update.message.reply_text(chunk)
            else:
                await update.message.reply_text(response)
            
            # Reset user mode
            context.user_data.pop('mode', None)
            
        except Exception as e:
            self.logger.error(f"Error processing resume: {str(e)}")
            await update.message.reply_text(
                "❌ Error processing your resume. Please try again."
            )
    
    async def _handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries from inline buttons."""
        query = update.callback_query
        await query.answer()
        
        if query.data == "analyze":
            await self._analyze_command(update, context)
        elif query.data == "optimize":
            await self._optimize_command(update, context)
        elif query.data == "help":
            await self._help_command(update, context)
    
    def run(self):
        """Run the Telegram bot."""
        if not self.application:
            raise RuntimeError("Bot not initialized")
        
        print("🤖 Starting Telegram bot...")
        self.application.run_polling()