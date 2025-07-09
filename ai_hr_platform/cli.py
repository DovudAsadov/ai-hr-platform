"""Command-line entry point for AI HR Platform."""

import sys
from .interfaces.cli_interface import CLIInterface
from .config import Config


def main():
    """Main entry point for the CLI."""
    try:
        config = Config()
        cli = CLIInterface(config)
        cli.run()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()