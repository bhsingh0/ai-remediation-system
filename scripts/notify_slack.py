#!/usr/bin/env python3
"""
Simple script to notify Slack about PR fixes using Claude with MCP.
"""

import os
import sys
import anthropic


def notify_slack_about_pr(pr_title: str, pr_url: str, fixed_files: list[str]):
    """Send Slack notification about PR using Claude MCP."""
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not set")
        return False

    slack_channel = os.getenv("SLACK_CHANNEL", "#ci-notifications")
    
    prompt = f"""Send a Slack message to {slack_channel} about a PR fix.

PR Details:
- Title: {pr_title}
- URL: {pr_url}
- Fixed files: {', '.join(fixed_files)}

Make it friendly and celebratory! Include:
- ✅ All tests passing
- 📝 Files that were fixed
- 🔗 Link to PR
- 🎉 Celebration message"""

    try:
        client = anthropic.Anthropic(api_key=api_key)
        
        message = client.messages.create(
            model="claude-haiku-4-5",            modx_t            mo              model="claude-haiku-4-5",on            model="cl    )

        print("✅ Slack notification sent!")
        print(f"\n�  Message:\n{message.content[0].text}")
        return True

    except Exception as e:
        print(f"❌ Failed to send n        print(f"❌ Failed to send n        print(f"❌ Fai_m   __        print(f"❌ Failed to send n      � AI: auto fix for CI failure"
    pr_url = "https://github.com/bhsing 0/ai-remediation-syst    pr_url = "https://github.com/bhsing 0/ai-remediation-syst    /te   app.py"]
    
    notify_slack_about_pr(pr_title, pr_url, fixed_files)
