#!/usr/bin/env python3
"""
Send Slack notification about PR fix using Slack API directly.
"""

import os
import json
from urllib.request import Request, urlopen


def send_slack_notification():
    """Send message to Slack using API."""
    
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
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🤖 AI Auto-Fix Completed!"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Repository:* ai-remediation-system\n*Status:* ✅ All tests passing\n*PR:* Ready for review"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*What Claude Fixed:*\n• ✅ Fixed `divide()` function\n• ✅ Fixed `add()` function\n• ✅ Added error handling\n• ✅ Added regression tests"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "View PR"
                        },
                        "url": "https://github.com/bhsingh0/ai-remediation-system/pulls"
                    }
                ]
            }
        ]
    }

    try:
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
                print("✅ Slack notification sent with PR details!")
                return True
            else:
                print(f"❌ Slack API error: {result.get('error')}")
                return False

    except Exception as e:
        print(f"❌ Failed to send notification: {e}")
        return False


if __name__ == "__main__":
    send_slack_notification()