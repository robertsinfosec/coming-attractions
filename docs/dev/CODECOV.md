# Codecov Setup and Usage Guide

> **Navigation:** [Home](../../README.md) | [Contributing](../../CONTRIBUTING.md) | [Testing](TESTING.md) | [Setup](SETUP.md) | [Architecture](ARCHITECTURE.md)

Complete guide for setting up and using Codecov for code coverage tracking.

## Table of Contents

- [What is Codecov?](#what-is-codecov)
- [Setup Steps](#setup-steps)
- [Viewing Coverage](#viewing-coverage)
- [Configuration](#configuration)
- [Local Workflow](#local-workflow)
- [CI/CD Integration](#cicd-integration)
- [Understanding Reports](#understanding-reports)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)


## What is Codecov?

**Codecov** is a code coverage reporting service that integrates with GitHub to track test coverage over time.

**What it provides:**
- 📊 **Coverage trends** - See coverage change over time
- 🎯 **PR comments** - Automatic coverage reports on pull requests
- 📈 **Visual reports** - Line-by-line coverage visualization
- 🏅 **Badges** - Show coverage status in README

**Why use it:**
- Track coverage progress toward 80% goal
- Prevent coverage regressions in PRs
- Identify untested code
- Visualize coverage by file/module


## Setup Steps

### Prerequisites

- GitHub repository
- Codecov account (free for open source)
- Existing test suite with coverage reports

### 1. Connect Repository to Codecov

1. **Sign in to Codecov:**
   - Go to https://codecov.io
   - Click **Sign in with GitHub**
   - Authorize Codecov

2. **Add repository:**
   - Click **Add new repository**
   - Find `robertsinfosec/coming-attractions`
   - Click to enable

3. **Copy upload token:**
   - Codecov will show your repository upload token
   - Copy this token (format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)

### 2. Add Token to GitHub Secrets

1. **Go to repository settings:**
   ```
   https://github.com/robertsinfosec/coming-attractions/settings/secrets/actions
   ```

2. **Create new secret:**
   - Click **New repository secret**
   - **Name:** `CODECOV_TOKEN`
   - **Value:** Paste the token from step 1
   - Click **Add secret**

### 3. Verify CI/CD Configuration

Your `.github/workflows/ci-cd.yml` should include:

```yaml
- name: Run tests with coverage
  run: |
    cd src
    pytest --cov=coming_attractions --cov-report=xml --cov-report=term -v

- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v4
  with:
    file: src/coverage.xml
    flags: unittests
    name: python-${{ matrix.python-version }}
    fail_ci_if_error: false
    token: ${{ secrets.CODECOV_TOKEN }}
```

### 4. Trigger First Upload

Push a commit to trigger CI:

```bash
git commit --allow-empty -m "test: Trigger CI for Codecov"
git push
```

Or manually trigger the workflow:
- Go to **Actions** tab
- Select "CI/CD" workflow
- Click **Run workflow**

### 5. Verify Upload

1. **Check GitHub Actions:**
   - Go to **Actions** tab
   - Click on the workflow run
   - Expand "Upload coverage to Codecov" step
   - Should show "Success!"

2. **Check Codecov Dashboard:**
   - Visit https://codecov.io/gh/robertsinfosec/coming-attractions
   - Should see coverage data


## Viewing Coverage

### Codecov Dashboard

**URL:** https://codecov.io/gh/robertsinfosec/coming-attractions

**What you see:**
- **Overall coverage percentage** (top of page)
- **Coverage graph** (trends over time)
- **File browser** (click to see line-by-line coverage)
- **Recent commits** (coverage for each commit)

### README Badge

The README includes a live coverage badge:

```markdown
[![codecov](https://codecov.io/gh/robertsinfosec/coming-attractions/branch/main/graph/badge.svg)](https://codecov.io/gh/robertsinfosec/coming-attractions)
```

This shows current coverage percentage and links to full report.

### PR Comments

Codecov automatically comments on pull requests with:

```
## Codecov Report
Coverage: 62.5% (+2.3%)
Diff Coverage: 85.7%

Files changed:
- coming_attractions/fetcher.py: 45% → 52% (+7%)
- coming_attractions/utils.py: 87% → 89% (+2%)
```


## Configuration

### Optional: codecov.yml

Create `.github/codecov.yml` for custom settings:

```yaml
# Codecov configuration
# https://docs.codecov.com/docs/codecov-yaml

coverage:
  precision: 2
  round: down
  range: "70...100"
  
  status:
    project:
      default:
        target: 80%           # Target overall coverage
        threshold: 2%         # Allow 2% drop
        if_ci_failed: error
    
    patch:
      default:
        target: 80%           # New code must be 80%+ covered
        threshold: 5%

comment:
  layout: "header, diff, files, footer"
  behavior: default
  require_changes: false

ignore:
  - "tests/"                  # Don't count test files
  - "**/__pycache__"
  - "**/conftest.py"

flags:
  unittests:
    paths:
      - coming_attractions/
```

### Badge Customization

**Default badge:**
```markdown
[![codecov](https://codecov.io/gh/USER/REPO/branch/main/graph/badge.svg)](https://codecov.io/gh/USER/REPO)
```

**Custom colors/styles:**
```markdown
[![codecov](https://codecov.io/gh/USER/REPO/branch/main/graph/badge.svg?token=YOUR_TOKEN)](https://codecov.io/gh/USER/REPO)
```

See https://docs.codecov.com/docs/status-badges for options.


## Local Workflow

### Generate Coverage Locally

```bash
cd src/

# Run tests with coverage
pytest --cov=coming_attractions --cov-report=html --cov-report=term-missing

# View HTML report
open htmlcov/index.html
```

### Coverage Report Formats

```bash
# Terminal summary
pytest --cov=coming_attractions --cov-report=term

# Terminal with missing lines
pytest --cov=coming_attractions --cov-report=term-missing

# HTML (interactive, browse files)
pytest --cov=coming_attractions --cov-report=html

# XML (for Codecov)
pytest --cov=coming_attractions --cov-report=xml

# JSON (for custom tools)
pytest --cov=coming_attractions --cov-report=json
```

### Check Coverage Before Push

```bash
cd src/

# Run tests with coverage
pytest --cov=coming_attractions --cov-report=term-missing

# Look for files with low coverage
# Add tests for those files
# Re-run to verify improvement
```


## CI/CD Integration

### Workflow Overview

On every push or PR:

1. **Run tests** on Python 3.11 and 3.12
2. **Generate coverage** (XML format)
3. **Upload to Codecov** (using token)
4. **Codecov processes** and updates dashboard
5. **Codecov comments** on PR (if applicable)

### Viewing CI Coverage

**In GitHub Actions:**
- Go to **Actions** tab
- Click workflow run
- Expand "Run tests with coverage"
- See terminal coverage report

**On Codecov:**
- Visit dashboard
- Click commit or PR
- See detailed file-by-file coverage

### Multi-Python Version Support

Coverage is collected from Python 3.11 and 3.12:

```yaml
strategy:
  matrix:
    python-version: ["3.11", "3.12"]
```

Codecov merges reports from both versions.


## Understanding Reports

### Coverage Metrics

**Overall coverage:**
- Percentage of lines executed during tests
- **Goal:** 80%+ for this project

**Diff coverage:**
- Coverage of lines changed in a PR
- **Goal:** 80%+ for new code

**File coverage:**
- Coverage per file
- 🟢 Green (80-100%) = good
- 🟡 Yellow (60-79%) = needs improvement  
- 🔴 Red (0-59%) = priority

### Interpreting Colors

**In HTML report:**
- 🟢 **Green line** = Covered by tests
- 🔴 **Red line** = Not covered
- ⚪ **Gray line** = Not executable (comments, blank)

**In Codecov dashboard:**
- 🟢 **Green file** = 80-100% covered
- 🟡 **Yellow file** = 60-79% covered
- 🔴 **Red file** = 0-59% covered

### Finding Uncovered Code

**Locally:**
```bash
pytest --cov=coming_attractions --cov-report=html
open htmlcov/index.html
```

Click on a file → red lines are uncovered.

**On Codecov:**
- Visit https://codecov.io/gh/robertsinfosec/coming-attractions
- Click **Files** tab
- Click on a file
- Red lines are uncovered


## Best Practices

### 1. Check Coverage Before PR

```bash
# Before creating PR, run:
cd src/
pytest --cov=coming_attractions --cov-report=term-missing

# Ensure coverage didn't decrease
# Add tests for new code
```

### 2. Target 80% Minimum

Per PRD requirement:
- **Overall:** 80%+ coverage
- **New code:** 80%+ coverage (diff coverage)
- **No regressions:** Coverage should not decrease

### 3. Focus on Critical Code

Priority order:
1. Business logic (fetcher, pruner)
2. Error handling
3. Edge cases
4. Integration points

### 4. Don't Game Coverage

❌ **Bad:** Tests without assertions
```python
def test_something():
    do_something()  # Runs code but doesn't verify
```

✅ **Good:** Meaningful tests
```python
def test_something():
    result = do_something()
    assert result == expected
```

### 5. Use Coverage to Find Bugs

Coverage often reveals:
- Unreachable code
- Missing error handlers
- Forgotten edge cases
- Dead code to remove

### 6. Track Progress

**Check coverage badge regularly:**

[![codecov](https://codecov.io/gh/robertsinfosec/coming-attractions/branch/main/graph/badge.svg)](https://codecov.io/gh/robertsinfosec/coming-attractions)

**Monitor trends:**
- Visit Codecov dashboard weekly
- Celebrate improvements!
- Address declining coverage


## Troubleshooting

### Coverage Not Uploading

**Check:**
1. `CODECOV_TOKEN` is set in GitHub secrets
2. `coverage.xml` exists after tests
3. Upload step in workflow completed
4. Codecov service is operational

**Debug:**
```yaml
- name: Debug coverage file
  run: |
    ls -la src/coverage.xml
    head -20 src/coverage.xml
```

### Coverage Seems Wrong

**Check:**
1. All source files discovered
2. Test files excluded (`tests/`)
3. Virtual envs excluded
4. `pytest.ini` `testpaths` correct

**Debug:**
```bash
# See what pytest discovers
pytest --collect-only

# See what coverage measures
cd src/
coverage report
```

### PR Comments Not Appearing

**Causes:**
- First-time setup (wait 1-2 PRs)
- Token permissions issue
- Codecov app not installed

**Solution:**
- Visit https://github.com/apps/codecov
- Ensure app installed for your repo
- Check token is valid

### "Coverage increased" but Badge Shows Decrease

**Cause:** Badge may cache for a few minutes.

**Solution:**
- Wait 5-10 minutes
- Hard refresh (Ctrl+Shift+R)
- Check actual Codecov dashboard for truth


## Additional Resources

- **Codecov Docs:** https://docs.codecov.com/
- **pytest-cov Docs:** https://pytest-cov.readthedocs.io/
- **Coverage.py Docs:** https://coverage.readthedocs.io/
- **Testing Guide:** [TESTING.md](TESTING.md)
- **GitHub Actions:** https://docs.github.com/en/actions


## Current Coverage

**Always check live sources for current coverage:**

- **README Badge:** [![codecov](https://codecov.io/gh/robertsinfosec/coming-attractions/branch/main/graph/badge.svg)](https://codecov.io/gh/robertsinfosec/coming-attractions)
- **Codecov Dashboard:** https://codecov.io/gh/robertsinfosec/coming-attractions

**Never rely on hardcoded numbers in documentation** - they become stale immediately!


> **Navigation:** [Home](../../README.md) | [Contributing](../../CONTRIBUTING.md) | [Testing](TESTING.md) | [Setup](SETUP.md) | [Architecture](ARCHITECTURE.md)
