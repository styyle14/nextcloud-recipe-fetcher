"""Logging configuration."""

import logging
import sys

from rich.console import Console
from rich.logging import RichHandler

# Create console for rich output
console = Console()

# Configure logging with Rich handler
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=console, rich_tracebacks=True)],
)

# Get logger instance
logger = logging.getLogger("recipito")
