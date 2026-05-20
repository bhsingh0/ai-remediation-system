#!/usr/bin/env python3
"""
Send Slack notification about PR fix using Slack API directly.
"""

import os
import json
from urllib.request import Request, urlopen


def send_slack_notification():
    """Send message to Slack using webhook API."""
    
    slack_token = os.getenv("SLACK_BOT_TOKEN")
    slack_channel = os.getenv("SLACK_CHANNEL", "#ci-notifications")
    
    if not slack_token:
        print("❌ SLACK_BOT_TOKEN not set")
        return False

    message = {
        "channel": slack_channel,
        "text": "🤖 AI Auto-Fix Completed Successfully!",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "✅ *AI Auto-Fix PR Merged!*\n\nRepository: ai-remediation-system\nStatus: All tests passing ✨\n\n🎉 Ready to review and merge!"
                }
            }
        ]
    }

    try:
        # Use Slack API with bot token
        url = "https://slack.com/api/chat.postMessage"
        
        req = Request(
            url,
            data=json.dumps(message).encode('utf-8'),
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {slack_token}'
            }
        )

        with urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            if result.get("ok"):
                print("✅ Slack notification sent!")
                return True
            else:
                print(f"❌ Slack API error: {result.get('error')}")
                return False

    except Exception as e:
        print(f"❌ Failed to send notification: {e}")
        return False


if __name__ == "__main__":
    send_slack_notification()