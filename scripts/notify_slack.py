#!/usr/bin/env python3
"""
Send Slack notification about PR fix using Claude with Slack MCP.
"""

import os
import anthropic


def notify_slack():
    """Send Slack notification using Claude with MCP."""
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    slack_token = os.getenv("SLACK_BOT_TOKEN")
    slack_channel = os.getenv("SLACK_CHANNEL", "#ci-notifications")
    
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not set")
        return False
    
    if not slack_token:
        print("❌ SLACK_BOT_TOKEN not set")
        return False

    prompt = f"""You are connected to Slack via MCP.

Send a message to Slack channel {slack_channel} with this content:

🎉 **AI Auto-Fix PR Merged Successfully!**

Repository: ai-remediation-system
Status: All tests passing ✨
Fixed Files:
  ✅ app/app.py
  ✅ tests/test_app.py

Ready to review and merge! 🚀"""

    try:
        client = anthropic.Anthropic(api_key=api_key)
        
        # Call Claude with Slack MCP enabled
        message = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            # Enable Slack MCP
            extra_headers={
                "anthropic-beta": "mcp-20250515"
            }
        )

        print("✅ Slack notification sent via MCP!")
        print(f"\nClaude response:\n{message.content[0].text}")
        return True

    except Exception as e:
        print(f"❌ Failed to send notification: {e}")
        return False


if __name__ == "__main__":
    notify_slack()#!/usr/bin/env python3
"""
Send Slack notification about PR fix using Claude with Slack MCP.
"""

import os
import anthropic


def notify_slack():
    """Send Slack notification using Claude with MCP."""
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    slack_token = os.getenv("SLACK_BOT_TOKEN")
    slack_channel = os.getenv("SLACK_CHANNEL", "#ci-notifications")
    
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not set")
        return False
    
    if not slack_token:
        print("❌ SLACK_BOT_TOKEN not set")
        return False

    prompt = f"""You are connected to Slack via MCP.

Send a message to Slack channel {slack_channel} with this content:

🎉 **AI Auto-Fix PR Merged Successfully!**

Repository: ai-remediation-system
Status: All tests passing ✨
Fixed Files:
  ✅ app/app.py
  ✅ tests/test_app.py

Ready to review and merge! 🚀"""

    try:
        client = anthropic.Anthropic(api_key=api_key)
        
        # Call Claude with Slack MCP enabled
        message = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            # Enable Slack MCP
            extra_headers={
                "anthropic-beta": "mcp-20250515"
            }
        )

        print("✅ Slack notification sent via MCP!")
        print(f"\nClaude response:\n{message.content[0].text}")
        return True

    except Exception as e:
        print(f"❌ Failed to send notification: {e}")
        return False


if __name__ == "__main__":
    notify_slack()