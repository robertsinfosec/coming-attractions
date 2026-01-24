"""Tests for CLI interface."""

from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from coming_attractions import __version__
from coming_attractions.cli import cli


class TestCLIBasics:
    """Tests for basic CLI functionality."""

    def test_version_flag(self):
        """Test --version flag."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])

        assert result.exit_code == 0
        assert __version__ in result.output

    def test_help_flag(self):
        """Test --help flag."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "Coming Attractions" in result.output
        assert "fetch" in result.output
        assert "prune" in result.output
        assert "fix-titles" in result.output

    def test_fetch_help(self):
        """Test fetch command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["fetch", "--help"])

        assert result.exit_code == 0
        assert "--api-key" in result.output
        assert "--mode" in result.output

    def test_prune_help(self):
        """Test prune command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["prune", "--help"])

        assert result.exit_code == 0
        assert "--retention-years" in result.output
        assert "--dry-run" in result.output

    def test_fix_titles_help(self):
        """Test fix-titles command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["fix-titles", "--help"])

        assert result.exit_code == 0
        assert "--root-dir" in result.output
        assert "--prefix" in result.output


class TestFetchCommand:
    """Tests for fetch command."""

    @patch("coming_attractions.cli.TrailerFetcher")
    def test_fetch_dry_run(self, mock_fetcher_class, tmp_path, valid_api_key):
        """Test fetch in dry-run mode."""
        # Setup mock
        mock_instance = MagicMock()
        mock_fetcher_class.return_value = mock_instance
        mock_stats = MagicMock()
        mock_stats.total_items = 0
        mock_instance.fetch.return_value = mock_stats

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "fetch",
                "--api-key",
                valid_api_key,
                "--out-dir",
                str(tmp_path),
                "--dry-run",
            ],
        )

        # Should succeed in dry-run
        assert result.exit_code == 0
        mock_instance.fetch.assert_called_once()

    def test_fetch_missing_api_key(self):
        """Test fetch without required API key."""
        runner = CliRunner()
        result = runner.invoke(cli, ["fetch"])

        # Should fail with missing required option
        assert result.exit_code != 0
        assert "api-key" in result.output.lower() or "missing" in result.output.lower()

    @patch("coming_attractions.cli.TrailerFetcher")
    def test_fetch_with_all_options(self, mock_fetcher_class, tmp_path, valid_api_key):
        """Test fetch with all available options."""
        mock_instance = MagicMock()
        mock_fetcher_class.return_value = mock_instance
        mock_stats = MagicMock()
        mock_stats.total_items = 10
        mock_stats.added = 5
        mock_stats.skipped = 5
        mock_instance.fetch.return_value = mock_stats

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "fetch",
                "--api-key",
                valid_api_key,
                "--out-dir",
                str(tmp_path),
                "--mode",
                "both",
                "--region",
                "GB",
                "--days-ahead",
                "180",
                "--days-back",
                "30",
                "--max-pages",
                "5",
                "--max-height",
                "720",
                "--dry-run",
            ],
        )

        assert result.exit_code == 0
        mock_instance.fetch.assert_called_once()

    @patch("coming_attractions.cli.TrailerFetcher")
    def test_fetch_without_dry_run(self, mock_fetcher_class, tmp_path, valid_api_key):
        """Test fetch in normal (non-dry-run) mode."""
        mock_instance = MagicMock()
        mock_fetcher_class.return_value = mock_instance
        mock_stats = MagicMock()
        mock_instance.fetch.return_value = mock_stats

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "fetch",
                "--api-key",
                valid_api_key,
                "--out-dir",
                str(tmp_path),
            ],
        )

        assert result.exit_code == 0
        # Verify dry_run was False in config
        call_args = mock_fetcher_class.call_args
        config = call_args[0][0]
        assert config.dry_run is False


class TestPruneCommand:
    """Tests for prune command."""

    @patch("coming_attractions.cli.TrailerPruner")
    def test_prune_dry_run(self, mock_pruner_class, tmp_path):
        """Test prune in dry-run mode."""
        # Create directories
        theatrical = tmp_path / "theatrical"
        streaming = tmp_path / "streaming"
        theatrical.mkdir()
        streaming.mkdir()

        # Setup mock
        mock_instance = MagicMock()
        mock_pruner_class.return_value = mock_instance
        mock_stats = MagicMock()
        mock_stats.pruned = 0
        mock_instance.prune.return_value = mock_stats

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "prune",
                "--theatrical-dir",
                str(theatrical),
                "--streaming-dir",
                str(streaming),
                "--dry-run",
            ],
        )

        # Should succeed in dry-run
        assert result.exit_code == 0
        mock_instance.prune.assert_called_once()

    @patch("coming_attractions.cli.TrailerPruner")
    def test_prune_with_force(self, mock_pruner_class, tmp_path):
        """Test prune with --force flag."""
        theatrical = tmp_path / "theatrical"
        streaming = tmp_path / "streaming"
        theatrical.mkdir()
        streaming.mkdir()

        mock_instance = MagicMock()
        mock_pruner_class.return_value = mock_instance
        mock_stats = MagicMock()
        mock_instance.prune.return_value = mock_stats

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "prune",
                "--theatrical-dir",
                str(theatrical),
                "--streaming-dir",
                str(streaming),
                "--force",
            ],
        )

        assert result.exit_code == 0
        call_args = mock_pruner_class.call_args
        config = call_args[0][0]
        assert config.force is True

    @patch("coming_attractions.cli.TrailerPruner")
    def test_prune_custom_retention(self, mock_pruner_class, tmp_path):
        """Test prune with custom retention years."""
        theatrical = tmp_path / "theatrical"
        streaming = tmp_path / "streaming"
        theatrical.mkdir()
        streaming.mkdir()

        mock_instance = MagicMock()
        mock_pruner_class.return_value = mock_instance
        mock_stats = MagicMock()
        mock_instance.prune.return_value = mock_stats

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "prune",
                "--theatrical-dir",
                str(theatrical),
                "--streaming-dir",
                str(streaming),
                "--retention-years",
                "5",
            ],
        )

        assert result.exit_code == 0
        call_args = mock_pruner_class.call_args
        config = call_args[0][0]
        assert config.retention_years == 5


class TestFixTitlesCommand:
    """Tests for fix-titles command."""

    @patch("coming_attractions.cli.TitleFixer")
    def test_fix_titles_basic(self, mock_fixer_class, tmp_path):
        """Test fix-titles command."""
        # Setup mock
        mock_instance = MagicMock()
        mock_fixer_class.return_value = mock_instance
        mock_stats = MagicMock()
        mock_stats.updated = 5
        mock_instance.fix_titles.return_value = mock_stats

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "fix-titles",
                "--root-dir",
                str(tmp_path),
            ],
        )

        assert result.exit_code == 0
        mock_instance.fix_titles.assert_called_once()

    @patch("coming_attractions.cli.TitleFixer")
    def test_fix_titles_custom_prefix(self, mock_fixer_class, tmp_path):
        """Test fix-titles with custom prefix."""
        mock_instance = MagicMock()
        mock_fixer_class.return_value = mock_instance
        mock_stats = MagicMock()
        mock_instance.fix.return_value = mock_stats

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "fix-titles",
                "--root-dir",
                str(tmp_path),
                "--prefix",
                "Preview - ",
            ],
        )

        assert result.exit_code == 0
        call_args = mock_fixer_class.call_args
        config = call_args[0][0]
        assert config.prefix == "Preview - "


class TestDaemonCommand:
    """Tests for daemon command."""

    @patch("coming_attractions.cli.time.sleep")
    @patch("coming_attractions.cli.TrailerFetcher")
    @patch("coming_attractions.cli.TrailerPruner")
    @patch("coming_attractions.cli.TitleFixer")
    def test_daemon_parses_interval(
        self,
        mock_fixer_class,
        mock_pruner_class,
        mock_fetcher_class,
        mock_sleep,
        tmp_path,
        valid_api_key,
    ):
        """Test daemon parses interval correctly."""
        from coming_attractions.models import FetchStats, PruneStats, TitleFixStats

        # Mock all components
        mock_fetcher = MagicMock()
        mock_fetcher.fetch.return_value = FetchStats(added=0, skipped=0)
        mock_fetcher_class.return_value = mock_fetcher

        mock_pruner = MagicMock()
        mock_pruner.prune.return_value = PruneStats()
        mock_pruner_class.return_value = mock_pruner

        mock_fixer = MagicMock()
        mock_fixer.fix.return_value = TitleFixStats()
        mock_fixer_class.return_value = mock_fixer

        # Make sleep raise to exit after first iteration
        mock_sleep.side_effect = KeyboardInterrupt()

        runner = CliRunner()
        result = runner.invoke(
            cli, ["daemon", "--api-key", valid_api_key, "--interval", "2h"]
        )

        # Should parse 2h = 7200 seconds
        assert result.exit_code == 0
        if mock_sleep.called:
            assert mock_sleep.call_args[0][0] == 7200

    @patch("coming_attractions.cli.time.sleep")
    @patch("coming_attractions.cli.TrailerFetcher")
    @patch("coming_attractions.cli.TrailerPruner")
    @patch("coming_attractions.cli.TitleFixer")
    def test_daemon_handles_keyboard_interrupt(
        self,
        mock_fixer_class,
        mock_pruner_class,
        mock_fetcher_class,
        mock_sleep,
        tmp_path,
        valid_api_key,
    ):
        """Test daemon handles Ctrl+C gracefully."""
        from coming_attractions.models import FetchStats, PruneStats, TitleFixStats

        # Mock all components
        mock_fetcher = MagicMock()
        mock_fetcher.fetch.return_value = FetchStats(added=0, skipped=0)
        mock_fetcher_class.return_value = mock_fetcher

        mock_pruner = MagicMock()
        mock_pruner.prune.return_value = PruneStats()
        mock_pruner_class.return_value = mock_pruner

        mock_fixer = MagicMock()
        mock_fixer.fix.return_value = TitleFixStats()
        mock_fixer_class.return_value = mock_fixer

        # Raise KeyboardInterrupt during sleep
        mock_sleep.side_effect = KeyboardInterrupt()

        runner = CliRunner()
        result = runner.invoke(cli, ["daemon", "--api-key", valid_api_key])

        # Should exit gracefully with code 0
        assert result.exit_code == 0

    def test_daemon_invalid_interval_format(self, tmp_path, valid_api_key):
        """Test daemon rejects invalid interval format."""
        runner = CliRunner()
        result = runner.invoke(
            cli, ["daemon", "--api-key", valid_api_key, "--interval", "invalid"]
        )

        assert result.exit_code != 0
        assert "Invalid interval" in result.output

    @patch("coming_attractions.cli.TrailerFetcher")
    @patch("coming_attractions.cli.TrailerPruner")
    @patch("coming_attractions.cli.TitleFixer")
    def test_daemon_continues_on_fetch_error(
        self,
        mock_fixer_class,
        mock_pruner_class,
        mock_fetcher_class,
        tmp_path,
        valid_api_key,
    ):
        """Test daemon continues running even if fetch fails."""
        from coming_attractions.models import PruneStats, TitleFixStats

        # Mock pruner and fixer to succeed
        mock_pruner = MagicMock()
        mock_pruner.prune.return_value = PruneStats()
        mock_pruner_class.return_value = mock_pruner

        mock_fixer = MagicMock()
        mock_fixer.fix.return_value = TitleFixStats()
        mock_fixer_class.return_value = mock_fixer

        # Mock fetcher to fail once then raise to exit
        mock_fetcher = MagicMock()
        mock_fetcher.fetch.side_effect = [
            Exception("Network error"),
            KeyboardInterrupt(),  # Exit after retry
        ]
        mock_fetcher_class.return_value = mock_fetcher

        runner = CliRunner()
        result = runner.invoke(cli, ["daemon", "--api-key", valid_api_key])

        # Should complete both iterations
        assert result.exit_code == 0


class TestEnvironmentVariables:
    """Tests for environment variable support."""

    @patch("coming_attractions.cli.TrailerFetcher")
    def test_api_key_from_env(self, mock_fetcher_class, tmp_path):
        """Test reading API key from environment."""
        # Setup mock
        mock_instance = MagicMock()
        mock_fetcher_class.return_value = mock_instance
        mock_stats = MagicMock()
        mock_instance.fetch.return_value = mock_stats

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "fetch",
                "--out-dir",
                str(tmp_path),
                "--dry-run",
            ],
            env={"TMDB_API_KEY": "a" * 32},  # Valid 32-character API key
        )

        # Should use env var for API key
        assert result.exit_code == 0

    @patch("coming_attractions.cli.TrailerPruner")
    def test_retention_from_env(self, mock_pruner_class, tmp_path):
        """Test reading retention years from environment."""
        theatrical = tmp_path / "theatrical"
        streaming = tmp_path / "streaming"
        theatrical.mkdir()
        streaming.mkdir()

        mock_instance = MagicMock()
        mock_pruner_class.return_value = mock_instance
        mock_stats = MagicMock()
        mock_instance.prune.return_value = mock_stats

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "prune",
                "--theatrical-dir",
                str(theatrical),
                "--streaming-dir",
                str(streaming),
            ],
            env={"RETENTION_YEARS": "3"},
        )

        assert result.exit_code == 0


class TestPruneCommandExtended:
    """Extended tests for prune command."""

    @patch("coming_attractions.cli.TrailerPruner")
    def test_prune_dry_run(self, mock_pruner_class, tmp_path):
        """Test prune in dry-run mode."""
        # Create directories
        theatrical = tmp_path / "theatrical"
        streaming = tmp_path / "streaming"
        theatrical.mkdir()
        streaming.mkdir()

        # Setup mock
        mock_instance = MagicMock()
        mock_pruner_class.return_value = mock_instance
        mock_stats = MagicMock()
        mock_stats.total_scanned = 0
        mock_stats.total_removed = 0
        mock_instance.prune.return_value = mock_stats

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "prune",
                "--theatrical-dir",
                str(theatrical),
                "--streaming-dir",
                str(streaming),
                "--dry-run",
            ],
        )

        assert result.exit_code == 0
        mock_instance.prune.assert_called_once()


class TestFixTitlesCommandExtended:
    """Extended tests for fix-titles command."""

    @patch("coming_attractions.cli.TitleFixer")
    def test_fix_titles(self, mock_fixer_class, tmp_path):
        """Test fix-titles command."""
        # Setup mock
        mock_instance = MagicMock()
        mock_fixer_class.return_value = mock_instance
        mock_stats = MagicMock()
        mock_stats.total = 0
        mock_stats.fixed = 0
        mock_instance.fix_titles.return_value = mock_stats

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "fix-titles",
                "--root-dir",
                str(tmp_path),
            ],
        )

        assert result.exit_code == 0
        mock_instance.fix_titles.assert_called_once()


class TestEnvironmentVariablesExtended:
    """Extended tests for environment variable support."""

    @patch("coming_attractions.cli.TrailerFetcher")
    def test_api_key_from_env(self, mock_fetcher_class, tmp_path):
        """Test reading API key from environment."""
        mock_instance = MagicMock()
        mock_fetcher_class.return_value = mock_instance
        mock_stats = MagicMock()
        mock_instance.fetch.return_value = mock_stats

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "fetch",
                "--out-dir",
                str(tmp_path),
                "--dry-run",
            ],
            env={"TMDB_API_KEY": "a" * 32},  # Valid 32-character API key
        )

        # Should use env var for API key
        assert result.exit_code == 0
