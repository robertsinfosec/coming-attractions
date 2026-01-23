"""Shared utility functions for trailer management."""

import os
import re
import unicodedata
from datetime import date, datetime
from pathlib import Path
from typing import Optional, Set


def sanitize_folder_name(name: str, max_length: int = 200) -> str:
    """
    Sanitize string for use as folder name.
    
    Handles:
    - Unicode normalization
    - Control characters
    - Invalid filesystem chars (: * ? " < > | /)
    - Leading/trailing dots and spaces
    - Length limits (with UTF-8 awareness)
    - Empty result fallback
    
    Args:
        name: String to sanitize
        max_length: Maximum length in characters (default: 200)
    
    Returns:
        Sanitized folder name safe for filesystem use
    
    Examples:
        >>> sanitize_folder_name("Movie: The Sequel (2026)")
        'Movie The Sequel (2026)'
        >>> sanitize_folder_name("  ...Invalid...  ")
        'Invalid'
    """
    if not name:
        return "Unknown"
    
    # Normalize Unicode (NFKC - compatibility decomposition + canonical composition)
    name = unicodedata.normalize("NFKC", name)
    
    # Collapse multiple whitespace to single space
    name = re.sub(r"\s+", " ", name, flags=re.UNICODE).strip()
    
    # Remove illegal filesystem characters
    # Windows: < > : " / \ | ? *
    # Unix: /
    # We'll be conservative and remove all of the above
    name = re.sub(r'[\/:*?"<>|]', "", name)
    
    # Remove control characters and other problematic Unicode
    name = "".join(ch for ch in name if unicodedata.category(ch)[0] != "C")
    
    # Remove leading/trailing dots and spaces (Windows compatibility)
    name = name.strip(". ")
    
    # Prevent empty result
    if not name:
        return "Unknown"
    
    # Limit length to prevent filesystem issues
    # Most filesystems support 255 bytes per component
    # Leave room for extensions and year suffix
    if len(name.encode("utf-8")) > max_length:
        # Truncate by characters first
        name = name[:max_length]
        # Ensure we didn't cut in middle of a multi-byte UTF-8 character
        name = name.encode("utf-8", "ignore").decode("utf-8", "ignore").strip()
        # Re-strip trailing dots/spaces after truncation
        name = name.strip(". ")
    
    # Final fallback if truncation resulted in empty string
    if not name:
        return "Unknown"
    
    return name


def parse_release_date(date_str: str) -> date:
    """
    Parse and validate ISO 8601 date string (YYYY-MM-DD).
    
    Args:
        date_str: Date string to parse
    
    Returns:
        date object
    
    Raises:
        ValueError: If date string is invalid or malformed
    
    Examples:
        >>> parse_release_date("2026-12-25")
        datetime.date(2026, 12, 25)
        >>> parse_release_date("invalid")
        Traceback (most recent call last):
            ...
        ValueError: Invalid date format: invalid
    """
    if not date_str or not isinstance(date_str, str):
        raise ValueError("Date string is empty or not a string")
    
    # Validate format with regex
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
        raise ValueError(f"Invalid date format: {date_str}")
    
    try:
        year, month, day = map(int, date_str.split("-"))
        return date(year, month, day)
    except ValueError as e:
        raise ValueError(f"Invalid date values in {date_str}: {e}") from e


def load_removed_trailers(removed_file: Path) -> Set[str]:
    """
    Load set of folder names from .trailer-removed.txt.
    
    Args:
        removed_file: Path to removed trailers file
    
    Returns:
        Set of folder names that were previously removed
    """
    removed_folders = set()
    
    if not removed_file.exists():
        return removed_folders
    
    try:
        with open(removed_file, "r", encoding="utf-8") as f:
            removed_folders = {line.strip() for line in f if line.strip()}
    except (OSError, IOError):
        # Silently ignore errors - assume no removed trailers
        pass
    
    return removed_folders


def add_to_removed_trailers(removed_file: Path, folder_name: str) -> bool:
    """
    Add folder name to .trailer-removed.txt atomically.
    
    Uses atomic write pattern: write to temp file, then rename.
    Deduplicates and sorts the file.
    
    Args:
        removed_file: Path to removed trailers file
        folder_name: Folder name to add
    
    Returns:
        True if successfully added, False on error
    """
    try:
        # Create directory if it doesn't exist
        removed_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing entries
        existing = load_removed_trailers(removed_file)
        
        # Add new entry
        existing.add(folder_name)
        
        # Write atomically
        temp_file = removed_file.with_suffix(f".tmp.{os.getpid()}")
        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                for name in sorted(existing):
                    f.write(f"{name}\n")
            
            # Atomic rename
            temp_file.replace(removed_file)
            return True
        finally:
            # Clean up temp file if it still exists
            if temp_file.exists():
                temp_file.unlink(missing_ok=True)
    
    except (OSError, IOError):
        return False


def deduplicate_removed_trailers(removed_file: Path) -> bool:
    """
    Sort and deduplicate .trailer-removed.txt file atomically.
    
    Args:
        removed_file: Path to removed trailers file
    
    Returns:
        True if successful, False on error
    """
    if not removed_file.exists():
        return True
    
    try:
        # Load and deduplicate
        existing = load_removed_trailers(removed_file)
        
        # Write atomically
        temp_file = removed_file.with_suffix(f".tmp.{os.getpid()}")
        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                for name in sorted(existing):
                    f.write(f"{name}\n")
            
            # Atomic rename
            temp_file.replace(removed_file)
            return True
        finally:
            # Clean up temp file if it still exists
            if temp_file.exists():
                temp_file.unlink(missing_ok=True)
    
    except (OSError, IOError):
        return False


def validate_directory_writable(directory: Path) -> None:
    """
    Validate that directory exists and is writable.
    
    Args:
        directory: Directory to validate
    
    Raises:
        ValueError: If directory is not writable
    """
    try:
        directory.mkdir(parents=True, exist_ok=True)
        
        # Test write permissions
        test_file = directory / ".write_test"
        test_file.write_text("test")
        test_file.unlink()
    except (OSError, PermissionError) as e:
        raise ValueError(
            f"Directory is not writable: {directory}\nError: {e}"
        ) from e


def format_duration(seconds: int) -> str:
    """
    Format seconds into human-readable duration.
    
    Args:
        seconds: Duration in seconds
    
    Returns:
        Formatted string (e.g., "2h 30m 15s", "45m 30s", "15s")
    
    Examples:
        >>> format_duration(9015)
        '2h 30m 15s'
        >>> format_duration(90)
        '1m 30s'
        >>> format_duration(45)
        '45s'
    """
    if seconds < 60:
        return f"{seconds}s"
    
    minutes = seconds // 60
    seconds = seconds % 60
    
    if minutes < 60:
        if seconds > 0:
            return f"{minutes}m {seconds}s"
        return f"{minutes}m"
    
    hours = minutes // 60
    minutes = minutes % 60
    
    parts = [f"{hours}h"]
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0:
        parts.append(f"{seconds}s")
    
    return " ".join(parts)
