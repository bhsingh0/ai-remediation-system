#!/usr/bin/env python3
"""
AI-powered bug fixer for CI failures.
 
Workflow:
1. Collect: git diff, test output, impacted files
2. Claude: generate minimal patch + regression tests
3. Apply: write changes to disk
4. Validate: run tests locally
5. Output: summary for GitHub Actions
 
Usage: python ai/fix_bug.py
Requires: ANTHROPIC_API_KEY environment variable
"""
 
import os
import sys
import subprocess
import re
from pathlib import Path
from typing import Optional
 
import anthropic
 
 
class CIFailureCollector:
    """Collect context about the CI failure."""
 
    @staticmethod
    def get_git_diff() -> str:
        """Get the diff of changes since last commit."""
        try:
            result = subprocess.run(
                ["git", "diff", "HEAD"],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout or "No changes detected"
        except subprocess.CalledProcessError as e:
            return f"Error getting diff: {e.stderr}"
 
    @staticmethod
    def get_failing_tests() -> str:
        """Run tests and capture output."""
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "-v", "--tb=short"],
                capture_output=True,
                text=True,
            )
            return result.stdout + result.stderr
        except subprocess.CalledProcessError as e:
            return f"pytest error:\n{e.stdout}\n{e.stderr}"
        except FileNotFoundError:
            return "pytest not found - skipping test run"
 
    @staticmethod
    def get_impacted_files() -> list[str]:
        """Get list of files changed in current diff."""
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD"],
                capture_output=True,
                text=True,
                check=True,
            )
            files = [f for f in result.stdout.strip().split("\n") if f]
            return files
        except subprocess.CalledProcessError:
            return []
 
    @staticmethod
    def get_file_content(filepath: str) -> Optional[str]:
        """Read file content if it exists."""
        path = Path(filepath)
        if path.exists() and path.is_file():
            try:
                return path.read_text()
            except Exception as e:
                return f"Error reading {filepath}: {e}"
        return None
 
    @classmethod
    def collect_all(cls) -> dict:
        """Collect all diagnostic information."""
        print("📊 Collecting diagnostic information...")
 
        impacted_files = cls.get_impacted_files()
        file_contents = {}
 
        for filepath in impacted_files:
            content = cls.get_file_content(filepath)
            if content:
                file_contents[filepath] = content
 
        test_output = cls.get_failing_tests()
        git_diff = cls.get_git_diff()
 
        diagnostics = {
            "git_diff": git_diff,
            "test_output": test_output,
            "impacted_files": impacted_files,
            "file_contents": file_contents,
        }
 
        print(f"✓ Found {len(impacted_files)} impacted files")
        print(f"✓ Collected test output ({len(test_output)} chars)")
 
        return diagnostics
 
 
class ClaudeFixer:
    """Use Claude to generate fixes."""
 
    def __init__(self, api_key: Optional[str] = None):
        self.client = anthropic.Anthropic(api_key=api_key)
 
    def generate_fix(self, diagnostics: dict) -> dict:
        """Call Claude to generate a fix and tests."""
        print("\n🤖 Calling Claude to generate fix...")
 
        prompt = self._build_prompt(diagnostics)
 
        message = self.client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
 
        response_text = message.content[0].text
        fix_data = self._parse_response(response_text, diagnostics)
 
        print("✓ Claude generated fix and tests")
        return fix_data
 
    @staticmethod
    def _build_prompt(diagnostics: dict) -> str:
        """Build the prompt for Claude."""
        file_contents_section = ""
        if diagnostics["file_contents"]:
            file_contents_section = "## Current file contents:\n"
            for filepath, content in diagnostics["file_contents"].items():
                file_contents_section += f"\n### {filepath}\n```python\n{content}\n```\n"
 
        prompt = f"""You are an expert Python developer fixing failing CI tests.
 
READ THE TEST OUTPUT VERY CAREFULLY to understand:
1. What exceptions the tests expect (ValueError, ZeroDivisionError, etc.)
2. What error messages are expected
3. All edge cases being tested
 
## Test failure output (READ THIS CAREFULLY):
```
{diagnostics['test_output']}
```
 
## Git diff (what changed):
```
{diagnostics['git_diff']}
```
 
{file_contents_section}
 
## CRITICAL RULES FOR YOUR FIX:
 
1. **LOOK FOR pytest.raises() IN TEST OUTPUT**
   - If you see: pytest.raises(ValueError) → you MUST raise ValueError
   - If you see: pytest.raises(ZeroDivisionError) → you MUST raise ZeroDivisionError
   - If you see: match="message" → use EXACTLY that message
 
2. **HANDLE ALL EDGE CASES SHOWN IN TESTS**
   - If tests check divide by zero: add `if b == 0: raise ValueError("Cannot divide by zero")`
   - If tests check negative numbers: make sure they work
   - Check ALL test names to understand ALL requirements
 
3. **MATCH ERROR TYPES AND MESSAGES EXACTLY**
   - Don't use different exception types
   - Don't use different error messages
   - Use EXACTLY what the test expects
 
4. **MAKE ALL TESTS PASS**
   - Your fix must make ALL failing tests pass
   - Don't just fix obvious bugs - look for edge case handling
 
## Response format:
 
### DIAGNOSIS
Explain:
- Root cause of the bug
- What error handling is missing
- How you'll fix it
 
### FIXED FILES
List format: `filename.py`
 
### PATCH
For each file, provide complete corrected content:
 
```python
# filename.py
<complete file content with all error handling>
```
 
EXAMPLE: If test expects ValueError for divide by zero:
```python
# app/app.py
def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
```
 
CRITICAL CHECKLIST:
✓ Read test output for pytest.raises() calls
✓ Use correct exception type (ValueError vs ZeroDivisionError)
✓ Use correct error message from test
✓ Include ALL error handling needed
✓ Make sure ALL tests will pass"""
 
        return prompt
 
    @staticmethod
    def _parse_response(response_text: str, diagnostics: dict) -> dict:
        """Parse Claude's response into structured data."""
        result = {
            "diagnosis": "",
            "fixed_files": {},
            "tests": {},
            "raw_response": response_text,
        }
 
        # Extract DIAGNOSIS (handle both # and ###)
        diagnosis_match = re.search(
            r"#+\s*DIAGNOSIS\n(.*?)(?=#+\s*FIXED FILES|#+\s*PATCH|#+\s*TESTS|\Z)", response_text, re.DOTALL | re.IGNORECASE
        )
        if diagnosis_match:
            result["diagnosis"] = diagnosis_match.group(1).strip()
 
        # Extract PATCH section and parse code blocks (handle both # and ###)
        patch_match = re.search(
            r"#+\s*PATCH\n(.*?)(?=#+\s*TESTS|#+\s*FIXED FILES|\Z)", response_text, re.DOTALL | re.IGNORECASE
        )
        if patch_match:
            patch_text = patch_match.group(1)
            # Find all markdown code blocks with filename comments
            code_blocks = re.findall(
                r"```python\n# ([\w/.]+\.py)\n(.*?)```", patch_text, re.DOTALL
            )
            for filename, code in code_blocks:
                result["fixed_files"][filename] = code.strip()
 
        # Extract TESTS section if present (handle both # and ###)
        tests_match = re.search(
            r"#+\s*TESTS\n(.*?)(?=#+|\Z)", response_text, re.DOTALL | re.IGNORECASE
        )
        if tests_match:
            tests_text = tests_match.group(1)
            # Find all code blocks with filename comments
            code_blocks = re.findall(
                r"```python\n# ([\w/.]+\.py)\n(.*?)```", tests_text, re.DOTALL
            )
            for filename, code in code_blocks:
                result["tests"][filename] = code.strip()
 
        return result
 
 
class PatchApplier:
    """Apply the generated patch to the repository."""
 
    @staticmethod
    def apply(fix_data: dict) -> bool:
        """Write the fixed files and tests to disk."""
        print("\n📝 Applying patch...")
 
        success = True
 
        # Apply fixed files
        for filepath, content in fix_data["fixed_files"].items():
            try:
                path = Path(filepath)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content + "\n")
                print(f"  ✓ Updated {filepath}")
            except Exception as e:
                print(f"  ✗ Error writing {filepath}: {e}")
                success = False
 
        # Apply tests
        for filepath, content in fix_data["tests"].items():
            try:
                path = Path(filepath)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content + "\n")
                print(f"  ✓ Created {filepath}")
            except Exception as e:
                print(f"  ✗ Error writing {filepath}: {e}")
                success = False
 
        return success
 
 
class TestValidator:
    """Validate that the patch actually fixes the tests."""
 
    @staticmethod
    def run_tests() -> tuple[bool, str]:
        """Run tests and return success status and output."""
        print("\n🧪 Validating patch with tests...")
 
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "-v"],
                capture_output=True,
                text=True,
                timeout=60,
            )
 
            output = result.stdout + result.stderr
            passed = result.returncode == 0
 
            if passed:
                print("✓ All tests passing")
            else:
                print(f"✗ Tests still failing:\n{output}")
 
            return passed, output
 
        except subprocess.TimeoutExpired:
            return False, "Tests timed out"
        except Exception as e:
            return False, f"Error running tests: {e}"
 
 
def main():
    """Main entry point."""
    print("🚀 AI Remediation for CI Failures\n")
 
    # Step 1: Collect diagnostics
    collector = CIFailureCollector()
    diagnostics = collector.collect_all()
 
    # Step 2: Generate fix with Claude
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not set")
        sys.exit(1)
 
    fixer = ClaudeFixer(api_key=api_key)
    try:
        fix_data = fixer.generate_fix(diagnostics)
    except anthropic.APIError as e:
        print(f"❌ Claude API error: {e}")
        sys.exit(1)
 
    # Show diagnosis
    if fix_data["diagnosis"]:
        print(f"\n📋 Diagnosis:\n{fix_data['diagnosis']}")
 
    # Step 3: Validate we have fixes
    if not fix_data["fixed_files"]:
        print("❌ No fixes were generated")
        print("\nRaw response from Claude:")
        print(fix_data["raw_response"])
        sys.exit(1)
 
    # Step 4: Apply patch
    if not PatchApplier.apply(fix_data):
        print("❌ Failed to apply patch")
        sys.exit(1)
 
    # Step 5: Validate with tests
    tests_pass, test_output = TestValidator.run_tests()
 
    if not tests_pass:
        print("\n⚠️  Patch applied but tests still failing:")
        print(test_output)
        sys.exit(1)
 
    # Success!
    print("\n✅ Fix applied and validated successfully!")
    print("\nSummary:")
    print(f"  • Fixed files: {len(fix_data['fixed_files'])}")
    print(f"  • Test files: {len(fix_data['tests'])}")
    for filepath in fix_data["fixed_files"]:
        print(f"    - {filepath}")
 
    sys.exit(0)
 
 
if __name__ == "__main__":
    main()
 