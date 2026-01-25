# Developer Setup Guide

> **Navigation:** [Home](../../README.md) | [Contributing](../../CONTRIBUTING.md) | [Testing](TESTING.md) | [Architecture](ARCHITECTURE.md) | [Style Guide](../../STYLE_GUIDE.md)

Complete setup guide for developers working on Coming Attractions.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start (Dev Container)](#quick-start-dev-container)
- [Manual Setup](#manual-setup)
- [Verifying Installation](#verifying-installation)
- [Running the Application](#running-the-application)
- [Development Workflow](#development-workflow)
- [Troubleshooting](#troubleshooting)


## Prerequisites

### Required

- **Python 3.11+** (check: `python --version`)
- **Git** (check: `git --version`)
- **pip** (check: `pip --version`)

### Optional but Recommended

- **VS Code** with Dev Containers extension
- **Docker** (for Dev Container or local testing)
- **make** (for Makefile commands)


## Quick Start (Dev Container)

**Recommended approach** - Provides a consistent, isolated development environment.

### What is a Dev Container?

Instead of installing all dependencies on your workstation, VS Code opens this project in a Docker container with everything pre-configured. Your code stays on your machine, but executes in the container.

### Setup Steps

1. **Install prerequisites:**
   - [VS Code](https://code.visualstudio.com/)
   - [Docker Desktop](https://www.docker.com/products/docker-desktop/)
   - [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

2. **Clone the repository:**
   ```bash
   git clone https://github.com/robertsinfosec/coming-attractions.git
   cd coming-attractions
   ```

3. **Open in VS Code:**
   ```bash
   code .
   ```

4. **Reopen in Container:**
   - VS Code will detect `.devcontainer/devcontainer.json`
   - Click **Reopen in Container** when prompted
   - Or: **Command Palette** (Ctrl+Shift+P) → **Dev Containers: Reopen in Container**

5. **Wait for setup:**
   - First time takes 2-5 minutes (downloads base image, installs dependencies)
   - Subsequent opens are much faster

6. **Verify:**
   ```bash
   # Inside the container terminal
   python --version       # Should show 3.11+
   coming-attractions --help
   pytest --version
   ```

### Dev Container Features

- ✅ Python 3.11+ pre-installed
- ✅ All dependencies installed
- ✅ Git configured
- ✅ Extensions pre-installed (Python, Pylance, etc.)
- ✅ Isolated from your host system
- ✅ Consistent across all developers


## Manual Setup

If you prefer not to use Dev Containers:

### 1. Clone Repository

```bash
git clone https://github.com/robertsinfosec/coming-attractions.git
cd coming-attractions
```

### 2. Create Virtual Environment

```bash
# Create venv
python -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### 3. Install Package in Development Mode

```bash
# Navigate to src directory
cd src/

# Install with development dependencies
pip install -e ".[dev]"

# Or without dev dependencies (minimal)
pip install -e .
```

This installs the package in "editable" mode, meaning changes to source code immediately reflect without reinstalling.

### 4. Verify Installation

```bash
coming-attractions --version
coming-attractions --help
pytest --version
```


## Verifying Installation

### Check Package Installation

```bash
pip list | grep coming-attractions
# Output: coming-attractions    1.0.0    /path/to/src
```

### Check Dependencies

```bash
cd src/
pip check
# Output: No broken requirements found.
```

### Run Basic Command

```bash
coming-attractions --help
```

Should show:

```
Usage: coming-attractions [OPTIONS] COMMAND [ARGS]...

Commands:
  daemon      Run complete workflow on interval
  fetch       Fetch trailers from TMDb
  fix-titles  Add "Trailer - " prefix to NFO files
  prune       Remove old trailers
```


## Running the Application

### From Source (Development Mode)

```bash
# Using installed command
coming-attractions fetch --help

# Or as Python module
python -m coming_attractions fetch --help

# Or directly from source (if not installed)
python src/coming_attractions/cli.py fetch --help
```

### Quick Test (Dry Run)

```bash
# Test fetch (doesn't actually download)
coming-attractions fetch \
  --api-key YOUR_KEY \
  --mode theatrical \
  --dry-run \
  --debug

# Test prune (doesn't actually delete)
coming-attractions prune \
  --retention-years 2 \
  --dry-run
```

### Set Up Test Environment

Create a `.env` file in project root:

```env
# For local testing
TMDB_API_KEY=your_test_api_key_here
OUT_DIR=./test_trailers
THEATRICAL_DIR=./test_trailers/theatrical
STREAMING_DIR=./test_trailers/streaming
RETENTION_YEARS=2
DEBUG=1
```

Then run:

```bash
coming-attractions fetch
```


## Development Workflow

### Typical Day-to-Day Flow

1. **Pull latest changes:**
   ```bash
   git pull origin main
   ```

2. **Create feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make changes to code:**
   ```bash
   # Edit files in src/coming_attractions/
   code src/coming_attractions/fetcher.py
   ```

4. **Test changes:**
   ```bash
   # Run tests
   cd src/
   pytest
   
   # Test specific file
   pytest tests/test_fetcher.py
   
   # Test with coverage
   pytest --cov=coming_attractions
   ```

5. **Run the application:**
   ```bash
   # Your changes are immediately available
   coming-attractions fetch --dry-run --debug
   ```

6. **Lint and format (if using Make):**
   ```bash
   cd src/
   make lint
   make format
   ```

7. **Commit changes:**
   ```bash
   git add .
   git commit -m "feat: Add new feature description"
   ```

8. **Push and create PR:**
   ```bash
   git push origin feature/your-feature-name
   # Open PR on GitHub
   ```

### Using Makefile

If `make` is available, use these shortcuts:

```bash
cd src/

# Install dependencies
make install-dev

# Run tests
make test

# Run tests with coverage
make test-cov

# Lint code
make lint

# Format code
make format

# Clean build artifacts
make clean

# Build Docker image
make docker-build
```

See [`src/Makefile`](../../src/Makefile) for all available commands.


## Troubleshooting

### "Command not found: coming-attractions"

**Problem:** Can't run `coming-attractions` command.

**Solutions:**

1. **Ensure package is installed:**
   ```bash
   cd src/
   pip install -e .
   ```

2. **Check if it's in your PATH:**
   ```bash
   which coming-attractions
   ```

3. **Use Python module invocation instead:**
   ```bash
   python -m coming_attractions --help
   ```

4. **Reinstall:**
   ```bash
   pip uninstall coming-attractions
   cd src/
   pip install -e .
   ```


### Import Errors

**Problem:** `ModuleNotFoundError` or import errors.

**Solutions:**

1. **Verify Python version (3.11+ required):**
   ```bash
   python --version
   ```

2. **Reinstall dependencies:**
   ```bash
   cd src/
   pip install -e ".[dev]"
   ```

3. **Check virtual environment is activated:**
   ```bash
   which python
   # Should show: /path/to/venv/bin/python
   ```

4. **Clear Python cache:**
   ```bash
   find . -type d -name __pycache__ -exec rm -rf {} +
   find . -type f -name "*.pyc" -delete
   ```


### Tests Failing

**Problem:** `pytest` fails with import or setup errors.

**Solutions:**

1. **Run tests from src/ directory:**
   ```bash
   cd src/
   pytest
   ```

2. **Reinstall in editable mode:**
   ```bash
   cd src/
   pip install -e .
   ```

3. **Check pytest is installed:**
   ```bash
   pip install pytest pytest-cov
   ```

4. **Run with verbose output:**
   ```bash
   cd src/
   pytest -v
   ```

See [Testing Guide](TESTING.md) for detailed testing information.


### Dev Container Issues

**Problem:** Dev Container won't build or start.

**Solutions:**

1. **Rebuild container:**
   - **Command Palette** → **Dev Containers: Rebuild Container**

2. **Check Docker is running:**
   ```bash
   docker ps
   ```

3. **Check Docker resources:**
   - Docker Desktop → Settings → Resources
   - Increase memory to 4GB+ if needed

4. **Clear Docker cache:**
   ```bash
   docker system prune -a
   ```

5. **Check .devcontainer/devcontainer.json:**
   - Ensure no syntax errors


### Permission Errors (Linux)

**Problem:** Can't write to directories or permission denied.

**Solutions:**

1. **Check ownership:**
   ```bash
   ls -la
   ```

2. **Fix ownership:**
   ```bash
   sudo chown -R $USER:$USER .
   ```

3. **For test directories:**
   ```bash
   mkdir -p test_trailers
   chmod -R 755 test_trailers
   ```


### "Python.h: No such file or directory"

**Problem:** Error when installing dependencies (missing Python headers).

**Solutions:**

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install python3-dev
```

**Fedora/CentOS:**
```bash
sudo dnf install python3-devel
```

**macOS:**
```bash
# Install Xcode Command Line Tools
xcode-select --install
```

Then reinstall:
```bash
cd src/
pip install -e ".[dev]"
```


### Virtual Environment Issues

**Problem:** Packages not found or wrong Python version.

**Solutions:**

1. **Deactivate and recreate:**
   ```bash
   deactivate
   rm -rf venv
   python3.11 -m venv venv
   source venv/bin/activate
   cd src/
   pip install -e ".[dev]"
   ```

2. **Ensure using correct Python:**
   ```bash
   which python
   python --version
   ```


### Getting Help

For setup issues:

1. Check [Contributing Guide](../../CONTRIBUTING.md)
2. Check [Testing Guide](TESTING.md) if test-related
3. Check [Architecture Guide](ARCHITECTURE.md) for code structure
4. 🐛 [Report bugs](https://github.com/robertsinfosec/coming-attractions/issues)
5. 💬 [Ask in Discussions](https://github.com/robertsinfosec/coming-attractions/discussions)


> **Navigation:** [Home](../../README.md) | [Contributing](../../CONTRIBUTING.md) | [Testing](TESTING.md) | [Architecture](ARCHITECTURE.md) | [Style Guide](../../STYLE_GUIDE.md)
