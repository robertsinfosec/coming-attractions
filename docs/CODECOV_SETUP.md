# Codecov Setup Guide

This guide shows you how to integrate Codecov with your Coming Attractions project.

## Prerequisites

- GitHub repository at `robertsinfosec/coming-attractions`
- Codecov account (sign up at https://codecov.io with your GitHub account)
- Repository already has coverage reports generated (`coverage.xml`)

## Setup Steps

### 1. Connect Repository to Codecov

1. Go to https://codecov.io
2. Sign in with GitHub
3. Click "Add new repository"
4. Find `robertsinfosec/coming-attractions`
5. Copy the repository upload token

### 2. Add Codecov Token to GitHub Secrets

1. Go to your GitHub repository: `https://github.com/robertsinfosec/coming-attractions`
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `CODECOV_TOKEN`
5. Value: Paste the token from step 1
6. Click **Add secret**

### 3. Verify CI/CD Configuration

Your `.github/workflows/ci.yml` is already configured:

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

### 4. Test the Integration

Trigger a test run:

```bash
# Option 1: Push a commit
git commit --allow-empty -m "test: Trigger CI for Codecov"
git push

# Option 2: Manually trigger workflow
# Go to Actions tab → CI workflow → Run workflow
```

### 5. Verify Upload

1. Check GitHub Actions run completes successfully
2. Look for "Upload coverage to Codecov" step
3. Visit https://codecov.io/gh/robertsinfosec/coming-attractions
4. Confirm coverage data appears

---

## Configuration

### Optional: codecov.yml

Create `.github/codecov.yml` for custom configuration:

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

### Badge Configuration

Your README already has the badge:

```markdown
[![coverage](https://codecov.io/gh/robertsinfosec/coming-attractions/branch/main/graph/badge.svg)](https://codecov.io/gh/robertsinfosec/coming-attractions)
```

This will show the current coverage percentage once data is uploaded.

---

## Understanding Coverage Reports

### On Codecov Dashboard

You'll see:
- **Overall coverage percentage** (currently ~58%)
- **Coverage by file** (click to see line-by-line)
- **Coverage trends** (graph over time)
- **Pull request diffs** (coverage impact of PRs)

### Interpreting Colors

- 🟢 **Green (80-100%)**: Well-covered, good!
- 🟡 **Yellow (60-79%)**: Partial coverage, needs improvement
- 🔴 **Red (0-59%)**: Poor coverage, priority for improvement

### PR Comments

Codecov will comment on PRs with:
- Coverage change (+2.5%, -1.2%, etc.)
- Diff coverage (coverage of changed lines)
- Link to detailed report

---

## Local Coverage Workflow

### Generate Coverage Locally

```bash
cd /workspaces/coming-attractions/src

# Run tests with coverage
pytest --cov=coming_attractions --cov-report=term-missing --cov-report=html

# View in terminal
pytest --cov=coming_attractions --cov-report=term-missing

# View in browser
python -m http.server 8000 --directory htmlcov
# Open http://localhost:8000
```

### Coverage Report Formats

```bash
# Terminal summary
--cov-report=term

# Terminal with missing line numbers
--cov-report=term-missing

# HTML (most detailed, interactive)
--cov-report=html

# XML (for CI/CD tools like Codecov)
--cov-report=xml

# JSON (for custom tooling)
--cov-report=json
```

### Coverage Commands

```bash
# Quick check
make test-cov

# Detailed HTML report
pytest --cov=coming_attractions --cov-report=html
open htmlcov/index.html

# See only uncovered lines
pytest --cov=coming_attractions --cov-report=term-missing | grep "MISS"

# Coverage for specific file
pytest --cov=coming_attractions.fetcher --cov-report=term-missing

# Branch coverage (more strict)
pytest --cov=coming_attractions --cov-branch
```

---

## CI/CD Integration

### Automatic Upload on Push

Every push to `main` or PR will:
1. Run tests on Python 3.11 and 3.12
2. Generate coverage reports
3. Upload to Codecov
4. Comment on PR with results

### Workflow Configuration

The CI workflow runs coverage in parallel across Python versions:

```yaml
strategy:
  matrix:
    python-version: ["3.11", "3.12"]
```

Results are combined on Codecov dashboard.

### Viewing Results

**GitHub Actions**:
- Go to **Actions** tab
- Click on a workflow run
- Expand "Run tests with coverage" step
- See terminal coverage report

**Codecov Dashboard**:
- https://codecov.io/gh/robertsinfosec/coming-attractions
- Click on specific commit/PR
- View detailed file-by-file breakdown

---

## Coverage Goals

### Current Status
- **Overall**: 58%
- **Target**: 80% (per PRD requirement)
- **Gap**: Need +22%

### Priority Areas

**Critical** (9% coverage):
- `fetcher.py` - Main business logic

**High** (0% coverage):
- `__main__.py` - Entry point

**Medium** (51-68% coverage):
- `cli.py`
- `pruner.py`
- `logger.py`
- `youtube_downloader.py`

### Tracking Progress

Add this to your PR checklist:

```markdown
### Coverage Checklist
- [ ] Coverage did not decrease
- [ ] New code is ≥80% covered
- [ ] Overall coverage is improving
- [ ] CI coverage check passes
```

---

## Best Practices

### 1. Write Tests First

```bash
# See what's uncovered
pytest --cov=coming_attractions --cov-report=html
open htmlcov/index.html

# Focus on red/yellow files
# Write tests for uncovered code
# Re-run to verify
```

### 2. Don't Game Coverage

❌ **Bad**: Adding tests that run code but don't assert anything
```python
def test_something():
    do_something()  # No assertions!
```

✅ **Good**: Meaningful tests with assertions
```python
def test_something():
    result = do_something()
    assert result == expected_value
    assert some_side_effect_occurred()
```

### 3. Focus on Critical Code

Priority order:
1. **Business logic** (fetcher, pruner, etc.)
2. **Error handling** (exception paths)
3. **Edge cases** (empty inputs, malformed data)
4. **Integration** (end-to-end workflows)

### 4. Use Coverage to Find Bugs

Coverage reports often reveal:
- Unreachable code
- Missing error handling
- Forgotten edge cases
- Dead code to remove

---

## Troubleshooting

### Issue: Coverage Not Uploading

**Check**:
1. `CODECOV_TOKEN` secret is set correctly
2. `coverage.xml` exists in `src/` after tests
3. GitHub Actions has internet access
4. Codecov service is operational

**Debug**:
```yaml
- name: Debug coverage
  run: |
    ls -la src/coverage.xml
    head -20 src/coverage.xml
```

### Issue: Coverage Seems Wrong

**Check**:
1. All source files are being discovered
2. Test files aren't counted (should be excluded)
3. Virtual environment files excluded
4. pytest.ini `testpaths` is correct

**Debug**:
```bash
# See what pytest discovers
pytest --collect-only

# See what coverage measures
coverage report
```

### Issue: PR Comment Not Appearing

**Causes**:
- First-time setup (may take 1-2 PRs)
- Token permissions
- Codecov integration not enabled

**Solution**:
- Check https://github.com/apps/codecov
- Ensure app is installed for your repo

---

## Additional Resources

- **Codecov Docs**: https://docs.codecov.com/
- **pytest-cov Docs**: https://pytest-cov.readthedocs.io/
- **Coverage.py Docs**: https://coverage.readthedocs.io/
- **GitHub Actions**: https://docs.github.com/en/actions

## Example: Your Org's freebusy-api

Your organization already uses Codecov successfully. See:
- Workflow: https://github.com/robertsinfosec/freebusy-api/blob/main/.github/workflows/ci.yml
- Badge: [![coverage](https://codecov.io/gh/robertsinfosec/freebusy-api/branch/main/graph/badge.svg)](https://codecov.io/gh/robertsinfosec/freebusy-api)

The setup is nearly identical - just different paths and test commands for Node.js vs Python.

---

## Next Steps

1. ✅ Add `CODECOV_TOKEN` to GitHub secrets
2. ✅ Push a commit to trigger CI
3. ✅ Verify upload on Codecov dashboard
4. ✅ Start improving coverage (target: 80%)
5. ✅ Monitor trends and celebrate improvements! 🎉

**Goal**: Get from 58% → 80% coverage before v1.0 release.
