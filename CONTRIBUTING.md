# Contributing to Coming Attractions

**Navigation**: [Home](README.md) > Contributing

Thank you for your interest in contributing to Coming Attractions! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)

## Code of Conduct

This project follows a code of conduct that all contributors are expected to uphold. Please be respectful and professional in all interactions.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/coming-attractions.git
   cd coming-attractions
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/robertsinfosec/coming-attractions.git
   ```

## Development Setup

This project uses **VS Code Dev Containers** for a consistent development environment.

### Quick Start

Steps to get started:

1. Install [VS Code](https://code.visualstudio.com/) and [Docker Desktop](https://www.docker.com/products/docker-desktop/)
2. Install the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
3. Clone and open the repository in VS Code
4. Click **Reopen in Container** when prompted
5. Wait for setup to complete (2-5 minutes first time)

**For detailed setup instructions**, including manual setup without Dev Containers, see **[Developer Setup Guide](docs/dev/SETUP.md)**.

## Making Changes

### Branch Naming

Create a descriptive branch for your changes:

```bash
git checkout -b feature/add-new-filter
git checkout -b fix/pruner-crash
git checkout -b docs/update-readme
```

### Commit Messages

Write clear, descriptive commit messages:

```
type: Short description (50 chars or less)

More detailed explanation if needed. Wrap at 72 characters.

- Bullet points are okay
- Use present tense ("Add feature" not "Added feature")
- Reference issues: "Fixes #123" or "Related to #456"
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `style`, `chore`

Examples:
```
feat: Add --exclude-genres option to fetch command

fix: Handle missing release dates in pruner

docs: Update Docker deployment instructions
```

## Testing

All code changes require tests with 80%+ coverage.

**Run tests:**

```bash
cd src/
pytest
pytest --cov=coming_attractions --cov-report=term-missing
```

**For detailed testing guidelines**, see **[Testing Guide](docs/dev/TESTING.md)**.

## Pull Request Process

### Before Submitting

Steps to take before creating a pull request:

1. **Update your branch** with latest upstream:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run tests** and ensure they pass:
   ```bash
   make test
   ```

3. **Check code quality** (if tools installed):
   ```bash
   make lint
   make format
   ```

4. **Update documentation** if you changed:
   - CLI commands or options
   - Configuration options
   - API or behavior

### Submitting

1. **Push to your fork**:
   ```bash
   git push origin feature/your-branch
   ```

2. **Create Pull Request** on GitHub
3. **Fill out PR template** completely
4. **Link related issues**: "Fixes #123"

### PR Review Process

What happens after you submit:

- Maintainers will review your PR
- Address any requested changes
- Once approved, a maintainer will merge

## Coding Standards

Follow these standards strictly:

- **PEP 8** compliance (line length: 100 characters)
- **Type hints** required for all function signatures
- **Docstrings** required (Google style)
- **No technical debt** - refactor as you go

**For complete coding standards**, see **[Style Guide](STYLE_GUIDE.md)** and **[Architecture Guide](docs/dev/ARCHITECTURE.md)**.

## Getting Help

- 📖 **[Developer Setup Guide](docs/dev/SETUP.md)** - Environment setup
- 🧪 **[Testing Guide](docs/dev/TESTING.md)** - Writing and running tests
- 🏗️ **[Architecture Guide](docs/dev/ARCHITECTURE.md)** - Project structure
- 📝 **[Style Guide](STYLE_GUIDE.md)** - Code quality standards
- 🐛 **[Issues](https://github.com/robertsinfosec/coming-attractions/issues)** - Bug reports
- 💬 **[Discussions](https://github.com/robertsinfosec/coming-attractions/discussions)** - Questions

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.
