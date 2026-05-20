#!/usr/bin/env python3
"""
Simple script to notify Slack about PR fixes using Claude with MCP.
"""

import os
import sys
import anthropic


def notify_slack_about_pr(pr_title: str, pr_url: str, fixed_files: list):
    """Send Slack notification about PR using Claude MCP."""
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    slack_token = os.getenv("SLACK_BOT_TOKEN")
    slack_channel = os.getenv("SLACK_CHANNEL", "#ci-notifications")
    
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not set")
        return False
    
    if not slack_token:
        print("❌ SLACK_BOT_TOKEN not set")
        return False

    prompt = f"""Send a message to Slack channel {slack_channel}.

Message:
🎉 **AI Auto-Fix PR Merged Successfully!**

Repository: {os.getenv('GITHUB_REPOSITORY', 'ai-remediation-system')}
PR Title: {pr_title}
PR Link: {pr_url}

Fixed Files:
{chr(10).join([f'  ✅ {f}' for f in fixed_files])}

All tests passing! ✨"""

    try:
        client = anthropic.Anthropic(api_key=api_key)
        
        message = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
        )

        print("✅ Slack notification sent!")
        return True

    except Exception as e:
        print(f"❌ Failed to send notification: {e}")
        return False


if __name__ == "__main__":
    pr_title = os.getenv("PR_TITLE", "🤖 AI: auto fix for CI failure")
    pr_url = os.getenv("PR_URL", "https://github.com/bhsingh0/ai-remediation-system")
    fixed_files = os.getenv("FIXED_FILES", "app/app.py,tests/test_app.py").split(",")
    
    notify_slack_about_pr(pr_title, pr_url, fixed_files)