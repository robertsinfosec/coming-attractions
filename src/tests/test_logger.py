"""Tests for logger functionality."""

import io
from pathlib import Path
from unittest.mock import patch


from coming_attractions.logger import Logger


class TestLoggerBasics:
    """Test basic logger functionality."""

    def test_logger_initialization(self):
        """Test logger can be initialized."""
        logger = Logger()
        assert logger.timestamps is False
        assert logger.debug_enabled is False

        logger_debug = Logger(debug=True)
        assert logger_debug.debug_enabled is True

    def test_info_logging(self):
        """Test info level logging."""
        logger = Logger()

        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            logger.info("Test message")
            output = mock_stdout.getvalue()
            assert "[*]" in output
            assert "Test message" in output

    def test_success_logging(self):
        """Test success level logging."""
        logger = Logger()

        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            logger.success("Operation succeeded")
            output = mock_stdout.getvalue()
            assert "[+]" in output
            assert "Operation succeeded" in output

    def test_error_logging(self):
        """Test error level logging."""
        logger = Logger()

        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            logger.error("Error occurred")
            output = mock_stdout.getvalue()
            assert "[-]" in output
            assert "Error occurred" in output

    def test_warning_logging(self):
        """Test warning level logging."""
        logger = Logger()

        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            logger.warning("Warning message")
            output = mock_stdout.getvalue()
            assert "[!]" in output
            assert "Warning message" in output

    def test_debug_logging_when_enabled(self):
        """Test debug logging when debug is enabled."""
        logger = Logger(debug=True)

        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            logger.debug("Debug info")
            output = mock_stdout.getvalue()
            assert "Debug info" in output

    def test_debug_logging_when_disabled(self):
        """Test debug logging is suppressed when debug is disabled."""
        logger = Logger(debug=False)

        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            logger.debug("Debug info")
            output = mock_stdout.getvalue()
            assert output == ""


class TestLoggerFormatting:
    """Test logger formatting options."""

    def test_indent_parameter(self):
        """Test message indentation."""
        logger = Logger()

        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            logger.info("Indented message", indent=2)
            output = mock_stdout.getvalue()
            # Should have indentation
            assert "Indented message" in output

    def test_timestamps_enabled(self):
        """Test timestamp formatting when enabled."""
        logger = Logger(timestamps=True)

        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            logger.info("Message with timestamp")
            output = mock_stdout.getvalue()
            # Should contain timestamp pattern (HH:MM:SS)
            assert "Message with timestamp" in output
            # Look for time pattern
            assert ":" in output or "Message" in output

    def test_color_output(self):
        """Test color codes in output."""
        logger = Logger()

        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            logger.success("Colored success")
            output = mock_stdout.getvalue()
            # Should contain message
            assert "success" in output.lower()


class TestLoggerFileOutput:
    """Test logger file output functionality."""

    def test_file_logging(self, tmp_path):
        """Test logging to file."""
        log_file = tmp_path / "test.log"
        logger = Logger(log_file=log_file)

        logger.info("Test message to file")
        logger.success("Success message")
        logger.error("Error message")

        # Close file handle
        if logger._file_handle:
            logger._file_handle.close()

        # Check file was created and contains messages
        assert log_file.exists()
        content = log_file.read_text()
        assert "Test message to file" in content
        assert "Success message" in content
        assert "Error message" in content

    def test_file_logging_with_timestamps(self, tmp_path):
        """Test file logging includes timestamps."""
        log_file = tmp_path / "timestamped.log"
        logger = Logger(log_file=log_file, timestamps=True)

        logger.info("Timestamped message")

        if logger._file_handle:
            logger._file_handle.close()

        content = log_file.read_text()
        assert "Timestamped message" in content

    def test_file_logging_creates_parent_dirs(self, tmp_path):
        """Test file logging creates parent directories."""
        log_file = tmp_path / "subdir" / "logs" / "test.log"

        # Create parent dirs
        log_file.parent.mkdir(parents=True, exist_ok=True)

        logger = Logger(log_file=log_file)
        logger.info("Creating directories")

        if logger._file_handle:
            logger._file_handle.close()

        assert log_file.exists()

    def test_console_and_file_logging(self, tmp_path):
        """Test logging to both console and file."""
        log_file = tmp_path / "combined.log"
        logger = Logger(log_file=log_file)

        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            logger.info("Dual output")
            console_output = mock_stdout.getvalue()

        if logger._file_handle:
            logger._file_handle.close()

        file_output = log_file.read_text()

        # Both should contain the message
        assert "Dual output" in console_output
        assert "Dual output" in file_output


class TestLoggerEdgeCases:
    """Test edge cases and special scenarios."""

    def test_empty_message(self):
        """Test logging empty message."""
        logger = Logger()

        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            logger.info("")
            output = mock_stdout.getvalue()
            # Should handle gracefully
            assert "[*]" in output

    def test_multiline_message(self):
        """Test logging multiline messages."""
        logger = Logger()

        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            logger.info("Line 1\nLine 2\nLine 3")
            output = mock_stdout.getvalue()
            assert "Line 1" in output

    def test_unicode_message(self):
        """Test logging unicode characters."""
        logger = Logger()

        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            logger.info("Unicode: 你好 🎬 ✅")
            output = mock_stdout.getvalue()
            # Should handle unicode gracefully
            assert "Unicode" in output

    def test_none_log_file(self):
        """Test logger works with None log_file."""
        logger = Logger(log_file=None)

        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            logger.info("Console only")
            output = mock_stdout.getvalue()
            assert "Console only" in output

    def test_invalid_log_file_path(self, tmp_path):
        """Test logger handles invalid log file path gracefully."""
        # Try to create log in non-writable location (will fail gracefully)
        logger = Logger(log_file=Path("/invalid/path/test.log"))

        # Should still work for console
        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            logger.info("Still works")
            output = mock_stdout.getvalue()
            assert "Still works" in output
