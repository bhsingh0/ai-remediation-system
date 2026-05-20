# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**ai-remediation-system**: An AI-powered automatic CI failure remediation pipeline that uses Claude to detect failing tests, analyze the failures, generate fixes, validate them, and create pull requests with Slack notifications.

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    GitHub Actions Workflow                   │
│                    (ai-remediation.yml)                      │
└──────────────────────────────────────────────────────────────┘
                              │
                              ↓
        ┌─────────────────────────────────────┐
        │    CI Failure Detection & Trigger    │
        │  (Run pytest, detect failures)       │
        └─────────────────────────────────────┘
                              │
                              ↓
        ┌─────────────────────────────────────────────────────┐
        │ CIFailureCollector (ai/fix_bug.py)                  │
        │ • Collects test output                              │
        │ • Gets git diff                                     │
        │ • Reads test file for spec (CRITICAL!)              │
        │ • Reads source files being changed                  │
        └─────────────────────────────────────────────────────┘
                              │
                              ↓
        ┌─────────────────────────────────────────────────────┐
        │ ClaudeFixer (ai/fix_bug.py)                         │
        │ • Builds prompt with diagnostics                    │
        │ • Calls Claude API (haiku-4-5)                      │
        │ • Parses response for fixes & code blocks           │
        │ • Extracts filenames from code blocks               │
        └─────────────────────────────────────────────────────┘
                              │
                              ↓
        ┌─────────────────────────────────────────────────────┐
        │ PatchApplier (ai/fix_bug.py)                        │
        │ • Writes fixed files to disk                        │
        │ • Updates test files if provided by Claude          │
        └─────────────────────────────────────────────────────┘
                              │
                              ↓
        ┌─────────────────────────────────────────────────────┐
        │ TestValidator (ai/fix_bug.py)                       │
        │ • Runs pytest to validate fix                       │
        │ • Returns test results                              │
        └─────────────────────────────────────────────────────┘
                              │
                              ↓
        ┌─────────────────────────────────────────────────────┐
        │ Create Pull Request (GitHub Actions)                │
        │ • Creates branch: ai/fix-${{ github.run_id }}       │
        │ • Commits changes with AI-remediation message       │
        └─────────────────────────────────────────────────────┘
                              │
                              ↓
        ┌─────────────────────────────────────────────────────┐
        │ Slack Notification (scripts/notify_slack.py)        │
        │ • Notifies via SLACK_BOT_TOKEN                      │
        │ • Sends to SLACK_CHANNEL env var                    │
        └─────────────────────────────────────────────────────┘
```

### Key Flow Details

1. **Test File is the Spec**: The test file (`tests/test_app.py`) is explicitly read and included in the Claude prompt with a "READ THIS!" header. Tests define what the expected behavior should be—Claude uses this as the source of truth.

2. **Prompt Parsing**: Claude response is parsed to extract:
   - `### DIAGNOSIS` section (what's wrong and how to fix)
   - Code blocks with optional `# filename.py` comments
   - Filenames are inferred if not provided (based on keywords like `def divide` → `app/app.py`)

3. **Exception Type Matching**: The prompt explicitly instructs Claude to match exception types exactly as shown in test files (e.g., if test expects `ValueError`, code must raise `ValueError`, not `ZeroDivisionError`).

### Key Files

- **ai/fix_bug.py**: Main entry point; contains all four classes (CIFailureCollector, ClaudeFixer, PatchApplier, TestValidator)
- **app/app.py**: Example buggy application with intentional bugs in `divide()` and `add()` functions
- **tests/test_app.py**: Test spec that defines expected behavior; Claude reads this to understand requirements
- **.github/workflows/ai-remediation.yml**: Main workflow triggered on push to main or fix/* branches; orchestrates the fix pipeline
- **.github/workflows/ci.yml**: Standard CI workflow that just runs pytest
- **scripts/notify_slack.py**: Posts success notifications to Slack using bot token

## Development Setup

### Prerequisites
- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (package manager and virtualenv tool)

### Install & Run Locally

```bash
# Install dependencies
uv sync

# Run tests (shows failures if any)
uv run pytest tests/

# Run the AI fixer manually
ANTHROPIC_API_KEY=sk-... uv run python ai/fix_bug.py

# Run a single test
uv run pytest tests/test_app.py::TestDivide::test_divide_normal -v
```

### Development Workflow

1. **Make a change to `app/app.py`** that breaks tests
2. **Run tests** locally to confirm they fail: `uv run pytest`
3. **Run the fixer**: `ANTHROPIC_API_KEY=... uv run python ai/fix_bug.py`
4. **Verify tests pass**: `uv run pytest`

## Testing

### Run All Tests
```bash
uv run pytest tests/
```

### Run Specific Test Class
```bash
uv run pytest tests/test_app.py::TestDivide -v
```

### Run Single Test with Output
```bash
uv run pytest tests/test_app.py::TestAdd::test_add_normal -v -s
```

### View Test Summary
```bash
uv run pytest tests/ --tb=short
```

## Important Design Patterns

### 1. Prompt Engineering for Test-Driven Fixes
- The test file is read in full and passed to Claude with "READ THIS!" and "THIS IS THE SPEC" markers
- The prompt explicitly shows example output format with code blocks prefixed by `# filename.py`
- Claude is shown a KEY RULE example: what exception type it MUST raise based on the test

### 2. Code Block Parsing
- Claude wraps fixes in ` ```python code blocks
- Optional `# filename.py` comment inside code block identifies the target file
- Fallback logic: if no filename, infer from code content (e.g., `def divide` → `app/app.py`, `def test_` → `tests/test_app.py`)

### 3. Exception Handling Emphasis
- The prompt repeatedly emphasizes matching exception types exactly
- Shows what NOT to do (e.g., `ZeroDivisionError` vs required `ValueError`)
- This prevents the common mistake of using Python's built-in exceptions when tests expect custom ones

### 4. Multi-Step Validation
- Fix is generated → applied to disk → immediately validated with pytest
- If tests still fail, exit with error (don't create PR)
- Only GitHub Actions creates PR if fix is successful

## GitHub Actions Workflows

### ai-remediation.yml (Main Fix Pipeline)
- **Trigger**: push to `main` or `fix/*` branches
- **Permissions**: write access to contents and pull-requests
- **Jobs**:
  - `fix`: Runs pytest, detects failures, runs AI fixer, applies patch, creates PR
  - `notify`: Sends Slack notification if workflow succeeds

### ci.yml (Standard CI)
- **Trigger**: push to main/fix/* or any pull request
- **Job**: Runs pytest only (no remediation)

### Secrets Required (GitHub)
- `ANTHROPIC_API_KEY`: Claude API key for ai/fix_bug.py
- `SLACK_BOT_TOKEN`: Slack bot token for notifications (only used in notify job)

## Environment Variables

| Variable | Purpose | Required | Example |
|----------|---------|----------|---------|
| `ANTHROPIC_API_KEY` | Claude API authentication | Yes (for AI fixer) | `sk-...` |
| `SLACK_BOT_TOKEN` | Slack bot auth for notifications | No (only notify job) | `xoxb-...` |
| `SLACK_CHANNEL` | Slack channel for notifications | No | `#ci-notifications` |

## Extending the System

### Adding a New Bug for Testing
1. Add buggy code to `app/app.py`
2. Add test(s) to `tests/test_app.py` that verify the expected behavior
3. Push to a fix/* branch to trigger AI remediation
4. Claude will analyze the test failure and generate a fix

### Customizing Claude Behavior
Edit the `_build_prompt()` method in `ai/fix_bug.py`:
- Change model: update `model=` parameter in `client.messages.create()`
- Change instructions: modify the prompt string (ensure the KEY RULE section is preserved)
- Change response format: update the `### Response format:` section and corresponding parse logic

### Adding More Validation Steps
Extend `TestValidator.run_tests()` to:
- Run additional linters (ruff, black, mypy)
- Check test coverage
- Run integration tests

## Key Gotchas

1. **Test File Must Exist**: If `tests/test_app.py` doesn't exist, the fixer still runs but Claude has no spec to work from.
2. **File Path Inference**: Code block filename comments are critical. If missing, the fallback logic must match keywords in the code. Edge cases may need explicit filename in prompt.
3. **Exception Types**: Tests using `pytest.raises(ValueError)` must be fixed with `raise ValueError(...)`. The prompt emphasizes this, but Claude can still make mistakes if the prompt isn't clear.
4. **Git Config**: The workflow sets git user/email globally before commits. If running locally, ensure your git is configured.
5. **Slack Optional**: Slack token is only needed for the notify job. The fix job works fine without it.

## Debugging

### Claude Generated Wrong Fix
1. Check `fix_data["raw_response"]` printed to stdout
2. Check if test file was included in the prompt (should be in the output)
3. Review the test file for clarity—add comments if expected behavior is ambiguous
4. Update prompt's KEY RULE section with more explicit examples

### Tests Still Failing After Fix
1. Run tests locally: `uv run pytest tests/ -v`
2. Check the actual error message (not just "test failed")
3. Run `uv run python ai/fix_bug.py` locally with `ANTHROPIC_API_KEY` set
4. Look at `raw_response` to see what Claude generated

### PR Not Created
1. Check GitHub Actions logs: workflow → fix job → "Create Pull Request" step
2. Confirm token has `pull-requests: write` permission
3. Verify fix job completed successfully (tests validated)

## References

- **Anthropic SDK**: https://github.com/anthropic-ai/anthropic-sdk-python
- **pytest**: https://docs.pytest.org/
- **GitHub Actions**: https://docs.github.com/en/actions
