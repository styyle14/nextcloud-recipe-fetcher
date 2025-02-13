"""Logging configuration."""

import logging
import sys

from rich.console import Console
from rich.logging import RichHandler

# Create console for rich output with markup enabled
console = Console(markup=True)

# Configure logging with Rich handler
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[
        RichHandler(
            console=console,
            rich_tracebacks=True,
            markup=True,  # Enable markup in log messages
            show_time=True,
            show_path=False,  # Hide file paths for cleaner output
        )
    ],
)

# Get logger instance
logger = logging.getLogger("recipito")
