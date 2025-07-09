"""Command-line interface for AI HR Platform."""

import argparse
import sys
from pathlib import Path
from typing import Optional

from ..core import ResumeAnalyzer, ResumeOptimizer
from ..config import Config


class CLIInterface:
    """Command-line interface for the AI HR Platform."""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize the CLI interface."""
        self.config = config or Config()
        self.analyzer = ResumeAnalyzer(self.config.to_dict())
        self.optimizer = ResumeOptimizer(self.config.to_dict())
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Create the argument parser."""
        parser = argparse.ArgumentParser(
            description="AI HR Platform - Professional Resume Analysis and Optimization",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  ai-hr analyze resume.pdf
  ai-hr optimize --text "Resume text here"
  ai-hr web --port 8080
  ai-hr telegram --token YOUR_BOT_TOKEN
            """
        )
        
        parser.add_argument(
            "--version",
            action="version",
            version="AI HR Platform 0.1.0"
        )
        
        subparsers = parser.add_subparsers(dest="command", help="Available commands")
        
        # Analyze command
        analyze_parser = subparsers.add_parser("analyze", help="Analyze a resume")
        analyze_parser.add_argument(
            "file",
            nargs="?",
            help="Resume file to analyze (PDF format)"
        )
        analyze_parser.add_argument(
            "--text",
            help="Resume text to analyze (instead of file)"
        )
        analyze_parser.add_argument(
            "--output",
            help="Output file for analysis results"
        )
        
        # Optimize command
        optimize_parser = subparsers.add_parser("optimize", help="Optimize a resume")
        optimize_parser.add_argument(
            "file",
            nargs="?",
            help="Resume file to optimize (PDF format)"
        )
        optimize_parser.add_argument(
            "--text",
            help="Resume text to optimize (instead of file)"
        )
        optimize_parser.add_argument(
            "--output",
            help="Output file for optimized resume"
        )
        
        # Web interface command
        web_parser = subparsers.add_parser("web", help="Launch web interface")
        web_parser.add_argument(
            "--port",
            type=int,
            default=7860,
            help="Port for web interface (default: 7860)"
        )
        web_parser.add_argument(
            "--host",
            default="127.0.0.1",
            help="Host for web interface (default: 127.0.0.1)"
        )
        web_parser.add_argument(
            "--share",
            action="store_true",
            help="Create shareable link"
        )
        
        # Telegram bot command
        telegram_parser = subparsers.add_parser("telegram", help="Launch Telegram bot")
        telegram_parser.add_argument(
            "--token",
            help="Telegram bot token"
        )
        
        return parser
    
    def run(self, args: Optional[list] = None):
        """Run the CLI interface."""
        parser = self.create_parser()
        
        if args is None:
            args = sys.argv[1:]
        
        parsed_args = parser.parse_args(args)
        
        if not parsed_args.command:
            parser.print_help()
            return
        
        try:
            if parsed_args.command == "analyze":
                self._handle_analyze(parsed_args)
            elif parsed_args.command == "optimize":
                self._handle_optimize(parsed_args)
            elif parsed_args.command == "web":
                self._handle_web(parsed_args)
            elif parsed_args.command == "telegram":
                self._handle_telegram(parsed_args)
        
        except Exception as e:
            print(f"Error: {str(e)}", file=sys.stderr)
            sys.exit(1)
    
    def _handle_analyze(self, args):
        """Handle the analyze command."""
        resume_text = self._get_resume_text(args.file, args.text)
        
        if not resume_text:
            print("Error: No resume provided. Use --file or --text option.", file=sys.stderr)
            return
        
        print("🔄 Analyzing resume...")
        result = self.analyzer.process(resume_text)
        
        if result.get("status") == "success":
            analysis = result["analysis"]
            
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(analysis)
                print(f"✅ Analysis saved to {args.output}")
            else:
                print("\n📄 Resume Analysis Results:")
                print("=" * 50)
                print(analysis)
        else:
            print(f"❌ Analysis failed: {result.get('error', 'Unknown error')}", file=sys.stderr)
    
    def _handle_optimize(self, args):
        """Handle the optimize command."""
        resume_text = self._get_resume_text(args.file, args.text)
        
        if not resume_text:
            print("Error: No resume provided. Use --file or --text option.", file=sys.stderr)
            return
        
        print("🔄 Optimizing resume...")
        result = self.optimizer.process(resume_text)
        
        if result.get("status") == "success":
            optimized = result["optimized_resume"]
            
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(optimized)
                print(f"✅ Optimized resume saved to {args.output}")
            else:
                print("\n✨ Optimized Resume:")
                print("=" * 50)
                print(optimized)
        else:
            print(f"❌ Optimization failed: {result.get('error', 'Unknown error')}", file=sys.stderr)
    
    def _handle_web(self, args):
        """Handle the web command."""
        try:
            from ..interfaces.web_interface import WebInterface
            
            print(f"🌐 Starting web interface on {args.host}:{args.port}")
            web_interface = WebInterface(self.config)
            web_interface.launch(
                server_name=args.host,
                server_port=args.port,
                share=args.share
            )
        except ImportError:
            print("Error: Gradio not installed. Install with: pip install gradio", file=sys.stderr)
    
    def _handle_telegram(self, args):
        """Handle the telegram command."""
        try:
            from ..interfaces.telegram_bot import TelegramBot
            
            if args.token:
                self.config.set('telegram_bot_token', args.token)
            
            bot = TelegramBot(self.config)
            bot.run()
        except ImportError:
            print("Error: python-telegram-bot not installed. Install with: pip install python-telegram-bot", file=sys.stderr)
    
    def _get_resume_text(self, file_path: Optional[str], text: Optional[str]) -> Optional[str]:
        """Get resume text from file or direct input."""
        if file_path:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            if path.suffix.lower() == '.pdf':
                return self.analyzer.extract_text_from_pdf(path)
            else:
                return path.read_text()
        elif text:
            return text
        else:
            return None