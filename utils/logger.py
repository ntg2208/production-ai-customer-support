"""
Centralized Logging Module for UKConnect Customer Support System

Provides structured logging with consistent formatting across all modules.
Supports different log levels, colored console output, and file logging.

Usage:
    from utils.logger import get_logger

    logger = get_logger(__name__)
    logger.info("Processing request")
    logger.error("Database connection failed", exc_info=True)
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Formatter that adds colors to console output based on log level"""

    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'
    BOLD = '\033[1m'

    def format(self, record: logging.LogRecord) -> str:
        # Get the color for this log level
        color = self.COLORS.get(record.levelname, '')

        # Format the message
        formatted = super().format(record)

        # Add color if we have one
        if color:
            return f"{color}{formatted}{self.RESET}"
        return formatted


class UKConnectLogger:
    """
    Centralized logger for UKConnect system.

    Features:
    - Colored console output
    - Optional file logging
    - Structured format with timestamps
    - Per-module logger instances
    """

    _loggers: dict = {}
    _file_handler: Optional[logging.FileHandler] = None
    _initialized: bool = False
    _log_level: int = logging.INFO

    @classmethod
    def configure(
        cls,
        log_level: int = logging.INFO,
        log_file: Optional[str] = None,
        enable_colors: bool = True
    ) -> None:
        """
        Configure global logging settings.

        Args:
            log_level: Minimum log level to display (default: INFO)
            log_file: Optional path to log file
            enable_colors: Whether to use colored console output
        """
        cls._log_level = log_level
        cls._initialized = True

        # Create root logger
        root_logger = logging.getLogger("ukconnect")
        root_logger.setLevel(log_level)

        # Remove existing handlers to avoid duplicates
        root_logger.handlers.clear()

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)

        if enable_colors and sys.stdout.isatty():
            console_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
            console_handler.setFormatter(ColoredFormatter(console_format, datefmt="%H:%M:%S"))
        else:
            console_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
            console_handler.setFormatter(logging.Formatter(console_format, datefmt="%H:%M:%S"))

        root_logger.addHandler(console_handler)

        # File handler (optional)
        if log_file:
            cls._setup_file_handler(root_logger, log_file)

    @classmethod
    def _setup_file_handler(cls, logger: logging.Logger, log_file: str) -> None:
        """Setup file handler for persistent logging"""
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setLevel(cls._log_level)

        file_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s"
        file_handler.setFormatter(logging.Formatter(file_format))

        logger.addHandler(file_handler)
        cls._file_handler = file_handler

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        Get or create a logger instance for the given module name.

        Args:
            name: Module name (typically __name__)

        Returns:
            Configured logger instance
        """
        # Auto-initialize with defaults if not configured
        if not cls._initialized:
            cls.configure()

        # Normalize name to be under ukconnect namespace
        if not name.startswith("ukconnect"):
            name = f"ukconnect.{name}"

        if name not in cls._loggers:
            logger = logging.getLogger(name)
            cls._loggers[name] = logger

        return cls._loggers[name]


# Convenience function for easy imports
def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for the given module.

    Usage:
        from utils.logger import get_logger
        logger = get_logger(__name__)
        logger.info("Hello world")
    """
    return UKConnectLogger.get_logger(name)


def configure_logging(
    log_level: int = logging.INFO,
    log_file: Optional[str] = None,
    enable_colors: bool = True
) -> None:
    """
    Configure global logging settings.

    Args:
        log_level: Minimum log level (logging.DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file for persistent logging
        enable_colors: Whether to use colored output in console
    """
    UKConnectLogger.configure(log_level, log_file, enable_colors)


# Module-level logger for this file
_logger = get_logger(__name__)


def log_agent_event(
    event_type: str,
    agent_name: str,
    message: str,
    details: Optional[dict] = None
) -> None:
    """
    Log an agent-related event with structured format.

    Args:
        event_type: Type of event (e.g., 'tool_call', 'response', 'delegation')
        agent_name: Name of the agent
        message: Event message
        details: Optional additional details
    """
    logger = get_logger("agent.events")
    log_msg = f"[{event_type.upper()}] {agent_name}: {message}"
    if details:
        log_msg += f" | {details}"
    logger.info(log_msg)


def log_database_event(
    operation: str,
    table: Optional[str] = None,
    success: bool = True,
    details: Optional[str] = None
) -> None:
    """
    Log a database operation.

    Args:
        operation: Type of operation (query, insert, update, delete)
        table: Table name if applicable
        success: Whether the operation succeeded
        details: Optional additional details
    """
    logger = get_logger("database")
    level = logging.INFO if success else logging.ERROR
    msg = f"[{operation.upper()}]"
    if table:
        msg += f" {table}"
    if details:
        msg += f" | {details}"
    logger.log(level, msg)


def log_tool_call(
    tool_name: str,
    args: Optional[dict] = None,
    result: Optional[str] = None,
    error: Optional[str] = None
) -> None:
    """
    Log a tool invocation.

    Args:
        tool_name: Name of the tool
        args: Tool arguments
        result: Result summary (truncated)
        error: Error message if failed
    """
    logger = get_logger("tools")
    if error:
        logger.error(f"Tool '{tool_name}' failed: {error}")
    else:
        msg = f"Tool '{tool_name}' called"
        if args:
            # Truncate long arguments
            args_str = str(args)
            if len(args_str) > 100:
                args_str = args_str[:100] + "..."
            msg += f" with {args_str}"
        if result:
            result_str = str(result)
            if len(result_str) > 100:
                result_str = result_str[:100] + "..."
            msg += f" -> {result_str}"
        logger.info(msg)
