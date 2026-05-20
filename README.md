# ai-remediation-system

🤖 AI-powered automatic CI failure remediation using Claude, GitHub Actions, and MCP. When tests fail, this system analyzes the failure, generates a fix, validates it, and creates a pull request—all automatically.

## Features

- **Automatic Test Analysis**: Collects test output, git diffs, and source files to understand failures
- **Claude-Powered Fixes**: Uses Claude API to generate code fixes based on test specifications
- **Test-Driven**: Reads test files as the source of truth for expected behavior
- **Validation Pipeline**: Automatically validates fixes by re-running tests before PR creation
- **GitHub Integration**: Creates pull requests with the generated fixes
- **Slack Notifications**: Sends notifications when fixes are successfully generated
- **MCP Support**: Integrates with Model Context Protocol for extensible tools

## Quick Start

### Prerequisites
- Python 3.10+
- [uv](https://github.com/astral-sh/uv) package manager
- ANTHROPIC_API_KEY for Claude API access

### Local Development

```bash
# Install dependencies
uv sync

# Run tests to see if any are failing
uv run pytest tests/

# (Optional) Manually trigger the AI fixer
ANTHROPIC_API_KEY=sk-... uv run python ai/fix_bug.py

# Run a single test
uv run pytest tests/test_app.py::TestDivide::test_divide_normal -v
```

## How It Works

```
Push to main/fix/*
       ↓
GitHub Actions detects test failure
       ↓
CIFailureCollector gathers diagnostics
  • Test output
  • Git diff
  • Source files
  • Test file (THE SPEC)
       ↓
ClaudeFixer calls Claude API
  • Analyzes test expectations
  • Generates code fixes
  • Parses response for code blocks
       ↓
PatchApplier writes fixes to disk
       ↓
TestValidator runs pytest
       ↓
If tests pass → Create PR
If tests fail → Workflow fails, no PR created
```

## Project Structure

```
.
├── app/
│   └── app.py              # Example application (with intentional bugs)
├── ai/
│   └── fix_bug.py          # Main AI remediation logic
├── tests/
│   └── test_app.py         # Test specifications
├── scripts/
│   └── notify_slack.py     # Slack notification script
├── .github/workflows/
│   ├── ai-remediation.yml  # Main fix pipeline
│   └── ci.yml              # Standard CI tests
└── settings/
    └── mcp.json            # MCP server configuration
```

## Configuration

### GitHub Secrets Required
- `ANTHROPIC_API_KEY`: Your Claude API key (for AI fixer)
- `SLACK_BOT_TOKEN`: Slack bot token (optional, for notifications)

### Environment Variables
- `SLACK_CHANNEL`: Slack channel for notifications (default: `#ci-notifications`)

## Example Usage

### Adding a Bug to Test

1. **Break the code** in `app/app.py`:
   ```python
   def divide(a, b):
       return a / 0  # BUG: should be a / b
   ```

2. **Add test expectations** in `tests/test_app.py`:
   ```python
   def test_divide_normal(self):
       assert divide(10, 2) == 5.0
   ```

3. **Push** to a `fix/*` branch to trigger the workflow

4. **AI fixes it** automatically and creates a PR

## Key Concepts

### Test File as Spec
The test file (`tests/test_app.py`) is explicitly read and passed to Claude with the label "THIS IS THE SPEC". Claude uses tests to understand exactly what behavior is expected.

### Exception Type Matching
If a test expects `ValueError`, the fix must raise `ValueError`—not `ZeroDivisionError` or any other exception type. The prompt emphasizes this explicitly.

### Multi-Step Validation
Fixes are validated before PR creation:
1. Generate fix with Claude
2. Apply to disk
3. Run pytest
4. Only create PR if tests pass

## Development

For detailed development guidance, architecture deep-dives, and debugging tips, see [CLAUDE.md](./CLAUDE.md).

### Common Commands

```bash
# Run all tests
uv run pytest tests/

# Run tests with verbose output
uv run pytest tests/ -v

# Run a specific test class
uv run pytest tests/test_app.py::TestDivide -v

# Run with short tracebacks
uv run pytest tests/ --tb=short

# Run the AI fixer locally
ANTHROPIC_API_KEY=sk-... uv run python ai/fix_bug.py
```

## Architecture

The system consists of four main components:

1. **CIFailureCollector** (`ai/fix_bug.py`): Gathers test output, diffs, file contents, and test specifications
2. **ClaudeFixer** (`ai/fix_bug.py`): Calls Claude API with diagnostics and parses the response
3. **PatchApplier** (`ai/fix_bug.py`): Writes generated fixes to disk
4. **TestValidator** (`ai/fix_bug.py`): Runs pytest to confirm fixes work

See [CLAUDE.md](./CLAUDE.md) for the detailed architecture diagram and design patterns.

## Troubleshooting

**Tests still failing after AI fix?**
- Run `uv run pytest tests/ -v` locally to see detailed errors
- Check the test expectations in `tests/test_app.py`
- Run the fixer manually: `ANTHROPIC_API_KEY=... uv run python ai/fix_bug.py`

**PR not created?**
- Check GitHub Actions logs in the workflow run
- Verify `ANTHROPIC_API_KEY` is set in GitHub Secrets
- Ensure the test validation step passed

**Slack notifications not working?**
- Set `SLACK_BOT_TOKEN` in GitHub Secrets
- Confirm bot has permission to post to the target channel

## Contributing

This is an experimental system for exploring AI-powered CI remediation. For development guidelines, see [CLAUDE.md](./CLAUDE.md).

## License

Open source, experimental project.
