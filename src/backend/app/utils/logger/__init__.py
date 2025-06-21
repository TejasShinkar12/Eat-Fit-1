"""Logging module for the application."""

import logging
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

class JsonFormatter(logging.Formatter):
    """Custom JSON formatter for logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format the log record as JSON"""
        # Get the message first
        message = record.getMessage()
        
        # Create the base log entry
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            "level": record.levelname,
            "message": message,
            "module_name": record.name,
            "function_name": record.funcName,
            "line_number": record.lineno,
            "process_id": record.process,
            "thread_id": record.thread
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["traceback"] = self.formatException(record.exc_info)
            
        # Add extra fields if present
        if hasattr(record, "extra"):
            log_entry["extra"] = record.extra
            
        try:
            return json.dumps(log_entry)
        except Exception as e:
            # Fallback for any JSON serialization errors
            return json.dumps({
                "timestamp": datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                "level": "ERROR",
                "message": "Error serializing log entry",
                "error": str(e),
                "original_message": message
            })

def wrap_logging_method(logger: logging.Logger, method_name: str):
    """Wrap a logging method to handle extra fields"""
    original_method = getattr(logger, method_name)
    
    def wrapped(msg, *args, **kwargs):
        if "extra" in kwargs:
            # Get the extra fields
            extra = kwargs.copy()
            # Create a new record
            record = logging.LogRecord(
                name=logger.name,
                level=getattr(logging, method_name.upper()),
                pathname=sys._getframe(1).f_code.co_filename,
                lineno=sys._getframe(1).f_lineno,
                msg=msg,
                args=args,
                exc_info=kwargs.get("exc_info"),
                func=sys._getframe(1).f_code.co_name
            )
            # Add extra fields
            record.extra = extra["extra"]
            
            # Format and emit
            for handler in logger.handlers:
                if handler:
                    handler.handle(record)
        else:
            original_method(msg, *args, **kwargs)
    
    return wrapped

def setup_logger(
    log_dir: Path,
    env: str,
    level: int = logging.INFO,
) -> logging.Logger:
    """Set up the application logger"""
    # Create log directory if it doesn't exist
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create root logger
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Create formatters
    json_formatter = JsonFormatter()
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(json_formatter)
    logger.addHandler(console_handler)
    
    # Create file handler
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = log_dir / f"app-{env}-{today}.log"
    file_handler = logging.FileHandler(str(log_file), mode='a', encoding='utf-8')
    file_handler.setFormatter(json_formatter)
    logger.addHandler(file_handler)
    
    # Wrap logging methods
    logger.debug = wrap_logging_method(logger, "debug")
    logger.info = wrap_logging_method(logger, "info")
    logger.warning = wrap_logging_method(logger, "warning")
    logger.error = wrap_logging_method(logger, "error")
    logger.critical = wrap_logging_method(logger, "critical")
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name"""
    logger = logging.getLogger(name)
    
    # Wrap logging methods
    logger.debug = wrap_logging_method(logger, "debug")
    logger.info = wrap_logging_method(logger, "info")
    logger.warning = wrap_logging_method(logger, "warning")
    logger.error = wrap_logging_method(logger, "error")
    logger.critical = wrap_logging_method(logger, "critical")
    
    return logger 