"""
Slack webhook notification module.
"""

import requests
from config.settings import settings

def notify_slack(message: str, is_error: bool = False):
    """Send a notification to Slack."""
    webhook_url = settings.slack_webhook_url
    if not webhook_url:
        print(f"SLACK NOTIFICATION (not sent, no webhook): {message}")
        return
        
    emoji = "🚨" if is_error else "✅"
    payload = {
        "text": f"{emoji} {message}"
    }
    
    try:
        requests.post(webhook_url, json=payload, timeout=10)
    except Exception as e:
        print(f"Failed to send Slack notification: {e}")
