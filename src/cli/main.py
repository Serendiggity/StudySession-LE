#!/usr/bin/env python3
"""
Main CLI entry point for the Insolvency Study Assistant.

This module provides the command-line interface for all functionality including:
- Document extraction
- Quiz generation
- Knowledge base querying
- Deadline calculations
"""

import click
from rich.console import Console
from rich.panel import Panel
import sys
import os
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logging_config import setup_logging, get_logger


console = Console()


@click.group()
@click.version_option(version="0.1.0", prog_name="Insolvency Study Assistant")
@click.option('--debug', is_flag=True, help='Enable debug logging')
def cli(debug):
    """
    Insolvency Study Assistant - AI-powered knowledge extraction and quiz generation.

    Extract structured knowledge from legal study materials and generate
    exam-realistic quizzes based on learned question patterns.
    """
    # Set up logging
    log_level = "DEBUG" if debug else os.getenv("LOG_LEVEL", "INFO")
    setup_logging(log_level=log_level)


@cli.command()
def test():
    """Test that the CLI is working correctly."""
    logger = get_logger(__name__)
    logger.info("CLI test command executed")

    console.print(Panel.fit(
        "[bold green]✓ CLI is working![/bold green]\n\n"
        "[cyan]System Status:[/cyan]\n"
        "• Python environment: OK\n"
        "• CLI framework: OK\n"
        "• Logging: OK\n"
        "• Rich formatting: OK\n\n"
        "[yellow]Next steps:[/yellow]\n"
        "1. Set up your API key in .env file\n"
        "2. Run: insolvency-study api-test\n"
        "3. Extract text from your PDF",
        title="✨ Insolvency Study Assistant",
        border_style="green"
    ))


@cli.command()
def info():
    """Display system information and configuration."""
    logger = get_logger(__name__)
    logger.info("Displaying system information")

    # Check for .env file
    env_exists = Path(".env").exists()
    api_key_set = bool(os.getenv("GEMINI_API_KEY"))

    # Check for PDF
    pdf_path = Path("Materials/Insolvency Administration - July 2020.pdf")
    pdf_exists = pdf_path.exists()

    console.print("\n[bold]Insolvency Study Assistant - System Information[/bold]\n")

    console.print("[cyan]Configuration:[/cyan]")
    console.print(f"  • .env file: {'✓ Found' if env_exists else '✗ Not found (copy .env.example)'}")
    console.print(f"  • API key: {'✓ Set' if api_key_set else '✗ Not set'}")
    console.print(f"  • Log level: {os.getenv('LOG_LEVEL', 'INFO')}")
    console.print(f"  • Database: {os.getenv('DATABASE_PATH', 'data/database/knowledge_base.db')}")

    console.print("\n[cyan]Project Structure:[/cyan]")
    console.print(f"  • Source PDF: {'✓ Found' if pdf_exists else '✗ Not found'}")
    console.print(f"  • Input dir: data/input/")
    console.print(f"  • Output dir: data/output/")
    console.print(f"  • Examples dir: data/examples/")

    console.print("\n[cyan]Version:[/cyan]")
    console.print("  • Version: 0.1.0")
    console.print("  • Phase: 1 (Setup)")

    if not env_exists or not api_key_set:
        console.print("\n[yellow]⚠ Action Required:[/yellow]")
        console.print("  1. Copy .env.example to .env")
        console.print("  2. Add your Gemini API key to .env")
        console.print("  3. Get API key from: https://aistudio.google.com/apikey")


@cli.command()
@click.option('--input', 'input_path', type=click.Path(exists=True),
              help='Path to PDF file')
def extract_text(input_path):
    """Extract text from a PDF file (Phase 2 functionality)."""
    console.print("[yellow]⚠ This command will be implemented in Phase 2[/yellow]")
    console.print("For now, focus on completing Phase 1 setup.")


# Placeholder commands for future phases
@cli.command()
def extract():
    """Extract knowledge from study materials (Phase 4+)."""
    console.print("[yellow]⚠ This command will be implemented in Phase 4[/yellow]")


@cli.command()
def generate_quiz():
    """Generate practice quizzes (Phase 8+)."""
    console.print("[yellow]⚠ This command will be implemented in Phase 8[/yellow]")


@cli.command()
def query():
    """Search the knowledge base (Phase 10+)."""
    console.print("[yellow]⚠ This command will be implemented in Phase 10[/yellow]")


if __name__ == '__main__':
    cli()
