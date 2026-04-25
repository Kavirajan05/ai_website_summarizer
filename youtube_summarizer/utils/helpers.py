import logging

# Basic logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_logger():
    """
    Returns the basic logger instance.
    """
    return logger

def format_error(error: Exception) -> str:
    """
    Simple helper to format exceptions for logging.
    """
    return f"Error occurred: {str(error)}"
