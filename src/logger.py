"""
Logging configuration for Bodega App
"""
import logging
import sys
from datetime import datetime
import os
from pathlib import Path


def setup_logger(name: str = "BodegaApp", log_level: str = "INFO") -> logging.Logger:
    """
    Sets up a logger with file and console handlers
    
    Args:
        name: Logger name
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    
    # Set log level
    level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(level)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # File handler (detailed logs)
    log_file = log_dir / f"bodega_{datetime.now().strftime('%Y%m')}.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    
    # Console handler (simple output)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(simple_formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


# Global logger instance
logger = setup_logger()


def log_function_call(func):
    """Decorator to log function calls"""
    def wrapper(*args, **kwargs):
        logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} returned: {result}")
            return result
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
            raise
    
    return wrapper


class DatabaseLogger:
    """Logger specifically for database operations"""
    
    def __init__(self, component: str = "Database"):
        self.logger = logging.getLogger(f"BodegaApp.{component}")
    
    def log_query(self, query: str, params: tuple = None):
        """Logs database queries (DEBUG level)"""
        if params:
            self.logger.debug(f"Query: {query} | Params: {params}")
        else:
            self.logger.debug(f"Query: {query}")
    
    def log_success(self, operation: str, details: str = ""):
        """Logs successful database operations"""
        self.logger.info(f"DB {operation} successful. {details}")
    
    def log_error(self, operation: str, error: str):
        """Logs database errors"""
        self.logger.error(f"DB {operation} failed: {error}")
    
    def log_warning(self, operation: str, warning: str):
        """Logs database warnings"""
        self.logger.warning(f"DB {operation} warning: {warning}")