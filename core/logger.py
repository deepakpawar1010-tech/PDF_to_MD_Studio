"""
PDF_to_MD_Studio v1.0 - Logging System
=======================================
Centralized logging with file rotation, console output,
and session-aware log management.
"""

import logging
import logging.handlers
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from core.constants import (
    LOG_DATE_FORMAT,
    LOG_FILE_BACKUP_COUNT,
    LOG_FILE_MAX_BYTES,
    LOG_FORMAT,
    LOG_LEVEL,
    LOGS_DIR,
)
from core.config import get_config


class ColoredFormatter(logging.Formatter):
    """
    Custom formatter that adds ANSI color codes to console output.
    """
    
    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",      # Cyan
        "INFO": "\033[32m",       # Green
        "WARNING": "\033[33m",    # Yellow
        "ERROR": "\033[31m",      # Red
        "CRITICAL": "\033[35m",   # Magenta
    }
    RESET = "\033[0m"
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with color codes."""
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


class LoggerManager:
    """
    Manages application logging with file rotation and console output.
    """
    
    _loggers: dict = {}
    _initialized: bool = False
    
    @classmethod
    def initialize(cls, log_level: Optional[str] = None) -> None:
        """
        Initialize the logging system.
        
        Args:
            log_level: Optional override for log level
        """
        if cls._initialized:
            return
        
        level = log_level or get_config().get("log_level", LOG_LEVEL)
        numeric_level = getattr(logging, level.upper(), logging.INFO)
        
        # Create logs directory
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        
        # Generate log filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d")
        log_file = LOGS_DIR / f"app_{timestamp}.log"
        
        # Root logger configuration
        root_logger = logging.getLogger()
        root_logger.setLevel(numeric_level)
        
        # Remove existing handlers to avoid duplicates
        root_logger.handlers.clear()
        
        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_file,
            maxBytes=LOG_FILE_MAX_BYTES,
            backupCount=LOG_FILE_BACKUP_COUNT,
            encoding="utf-8",
        )
        file_handler.setLevel(numeric_level)
        file_formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
        
        # Console handler with colors
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        console_formatter = ColoredFormatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
        
        cls._initialized = True
        
        # Log initialization
        app_logger = cls.get_logger("LoggerManager")
        app_logger.info(f"Logging initialized at level {level}")
        app_logger.info(f"Log file: {log_file}")
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        Get or create a named logger.
        
        Args:
            name: Logger name (typically module name)
            
        Returns:
            Configured logger instance
        """
        if not cls._initialized:
            cls.initialize()
        
        if name not in cls._loggers:
            logger = logging.getLogger(name)
            cls._loggers[name] = logger
        
        return cls._loggers[name]
    
    @classmethod
    def set_level(cls, level: str) -> None:
        """
        Change logging level at runtime.
        
        Args:
            level: New log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        numeric_level = getattr(logging, level.upper(), logging.INFO)
        root_logger = logging.getLogger()
        root_logger.setLevel(numeric_level)
        
        for handler in root_logger.handlers:
            handler.setLevel(numeric_level)
        
        app_logger = cls.get_logger("LoggerManager")
        app_logger.info(f"Log level changed to {level}")
    
    @classmethod
    def get_recent_logs(cls, lines: int = 100) -> str:
        """
        Get recent log entries as a string.
        
        Args:
            lines: Number of recent lines to retrieve
            
        Returns:
            Recent log content
        """
        # Find the most recent log file
        log_files = sorted(LOGS_DIR.glob("app_*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
        
        if not log_files:
            return "No log files found."
        
        try:
            with open(log_files[0], "r", encoding="utf-8") as f:
                all_lines = f.readlines()
                return "".join(all_lines[-lines:])
        except (IOError, OSError) as e:
            return f"Error reading logs: {e}"
    
    @classmethod
    def cleanup_old_logs(cls, keep_days: int = 7) -> int:
        """
        Remove log files older than specified days.
        
        Args:
            keep_days: Number of days to keep
            
        Returns:
            Number of files removed
        """
        if not LOGS_DIR.exists():
            return 0
        
        cutoff = datetime.now().timestamp() - (keep_days * 86400)
        removed = 0
        
        for log_file in LOGS_DIR.glob("app_*.log*"):
            try:
                if log_file.stat().st_mtime < cutoff:
                    log_file.unlink()
                    removed += 1
            except (OSError, PermissionError):
                continue
        
        app_logger = cls.get_logger("LoggerManager")
        app_logger.info(f"Cleaned up {removed} old log files")
        
        return removed


def get_logger(name: str) -> logging.Logger:
    """
    Convenience function to get a logger instance.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured logger
    """
    return LoggerManager.get_logger(name)