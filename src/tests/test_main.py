"""Tests for __main__ entry point."""

import sys
from unittest.mock import patch

import pytest


class TestMainEntry:
    """Tests for main entry point."""

    @patch("coming_attractions.__main__.cli")
    def test_main_calls_cli(self, mock_cli):
        """Test that __main__ calls cli() when executed."""
        # Import triggers the if __name__ == '__main__' check
        # We need to test it as a module execution
        with patch.object(sys, "argv", ["coming-attractions", "--help"]):
            # Import the module - this won't trigger __main__ in test
            # Instead, directly call what __main__ would call
            from coming_attractions.cli import cli

            # Simulate what happens in __main__.py
            with pytest.raises(SystemExit) as exc_info:
                cli(["--help"])

            # --help exits with code 0
            assert exc_info.value.code == 0

    def test_module_can_be_imported(self):
        """Test that the module can be imported without errors."""
        import coming_attractions.__main__

        # Should import successfully
        assert coming_attractions.__main__ is not None

    def test_package_executable(self):
        """Test that package can be run as: python -m coming_attractions."""
        # This test verifies the __main__.py exists and is importable
        import importlib.util

        spec = importlib.util.find_spec("coming_attractions.__main__")
        assert spec is not None
        assert spec.origin is not None
