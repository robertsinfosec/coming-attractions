"""Centralized logging with color support and configurable output."""

import sys
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, TextIO


class LogLevel(Enum):
    """Log levels with corresponding color codes and prefixes."""

    INFO = ("INFO", "[*]", "\033[36m")  # Cyan
    SUCCESS = ("SUCCESS", "[+]", "\033[32m")  # Green
    ERROR = ("ERROR", "[-]", "\033[31m")  # Red
    WARNING = ("WARNING", "[!]", "\033[33m")  # Yellow/Amber
    DEBUG = ("DEBUG", "[D]", "\033[90m")  # Gray


class Logger:
    """
    Centralized logger with color support, timestamps, and file output.

    Features:
    - Color-coded console output with standardized prefixes
    - Optional timestamps (HH:MM:SS or full datetime)
    - File logging with automatic timestamps
    - Debug mode toggle
    - Indentation support for hierarchical output
    - Immediate flush for real-time output
    """

    C_RESET = "\033[0m"

    def __init__(
        self,
        timestamps: bool = False,
        debug: bool = False,
        log_file: Optional[Path] = None,
    ):
        """
        Initialize logger.

        Args:
            timestamps: Add HH:MM:SS timestamps to console output
            debug: Enable debug-level logging
            log_file: Optional file path for logging (with full timestamps)
        """
        self.timestamps = timestamps
        self.debug_enabled = debug
        self.log_file = log_file
        self._file_handle: Optional[TextIO] = None

        # Open log file if specified
        if self.log_file:
            try:
                self._file_handle = open(self.log_file, "a", encoding="utf-8")
            except (OSError, PermissionError) as e:
                # Warn but continue - don't fail if log file can't be opened
                print(
                    f"{LogLevel.ERROR.value[2]}[-] WARNING: Could not open log file "
                    f"{self.log_file}: {e}{self.C_RESET}",
                    file=sys.stderr,
                    flush=True,
                )
                self._file_handle = None

    def _format_timestamp(self) -> str:
        """Generate timestamp for console output (HH:MM:SS)."""
        if self.timestamps:
            return f"{datetime.now().strftime('%H:%M:%S')} "
        return ""

    def _log_to_file(self, level: str, message: str) -> None:
        """Write log entry to file with full timestamp."""
        if self._file_handle:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            try:
                self._file_handle.write(f"[{timestamp}] {level} {message}\n")
                self._file_handle.flush()
            except (OSError, IOError):
                # Silently ignore file write errors to avoid disrupting execution
                pass

    def log(
        self,
        message: str,
        level: LogLevel = LogLevel.INFO,
        indent: int = 0,
    ) -> None:
        """
        Log a message with specified level and optional indentation.

        Args:
            message: Message to log
            level: Log level (determines color and prefix)
            indent: Number of spaces to indent (for hierarchical output)
        """
        # Skip debug messages if debug mode is disabled
        if level == LogLevel.DEBUG and not self.debug_enabled:
            return

        _, prefix, color = level.value
        timestamp = self._format_timestamp()
        indent_str = " " * indent

        # Format and print to console
        formatted = f"{color}{prefix} {timestamp}{indent_str}{message}{self.C_RESET}"
        print(formatted, flush=True)

        # Write to file (without color codes)
        self._log_to_file(level.value[0], f"{indent_str}{message}")

    def info(self, message: str, indent: int = 0) -> None:
        """Log informational message."""
        self.log(message, LogLevel.INFO, indent)

    def success(self, message: str, indent: int = 0) -> None:
        """Log success message."""
        self.log(message, LogLevel.SUCCESS, indent)

    def error(self, message: str, indent: int = 0) -> None:
        """Log error message."""
        self.log(message, LogLevel.ERROR, indent)

    def warning(self, message: str, indent: int = 0) -> None:
        """Log warning message."""
        self.log(message, LogLevel.WARNING, indent)

    def debug(self, message: str, indent: int = 0) -> None:
        """Log debug message (only if debug mode enabled)."""
        self.log(message, LogLevel.DEBUG, indent)

    def separator(self, char: str = "─", length: int = 64) -> None:
        """Print a visual separator line."""
        self.info(char * length)

    def close(self) -> None:
        """Close log file handle if open."""
        if self._file_handle:
            try:
                self._file_handle.close()
            except (OSError, IOError):
                pass
            self._file_handle = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close file handle."""
        self.close()
        return False
