#!/usr/bin/env python3
"""
Fail-open notification utility for SER Framework.

Sends webhook notifications for long-running autonomous operations
(experiment completion, overnight pipeline results, etc.).

Fail-open: notification failure never blocks the calling process.

Usage:
    python notify.py "Experiment exp-001 completed" --level info
    python notify.py "GPU OOM on remote-5" --level error

Environment:
    SER_NOTIFY_WEBHOOK_URL — Webhook URL (Slack, Feishu, Discord, etc.)
    SER_NOTIFY_ENABLED     — Set to "false" to disable (default: true)
"""

import argparse
import json
import os
import sys
import urllib.request
from datetime import datetime

WEBHOOK_URL = os.environ.get("SER_NOTIFY_WEBHOOK_URL", "")
ENABLED = os.environ.get("SER_NOTIFY_ENABLED", "true").lower() != "false"


def notify(message: str, level: str = "info", context: dict | None = None) -> bool:
    """
    Send a notification via webhook. Returns True on success, False on failure.
    Never raises exceptions (fail-open).
    """
    if not ENABLED or not WEBHOOK_URL:
        return False

    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        icon = {"info": "ℹ️", "warning": "⚠️", "error": "🔴", "success": "✅"}.get(level, "📌")

        payload = {
            "text": f"{icon} *[SER]* [{level.upper()}] {timestamp}\n{message}",
        }

        if context:
            details = "\n".join(f"  • {k}: {v}" for k, v in context.items())
            payload["text"] += f"\n{details}"

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            WEBHOOK_URL,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10):
            pass
        return True
    except Exception as e:
        print(f"[notify] Failed (non-blocking): {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="SER notification utility")
    parser.add_argument("message", help="Notification message")
    parser.add_argument("--level", "-l", default="info", choices=["info", "warning", "error", "success"])
    args = parser.parse_args()

    success = notify(args.message, args.level)
    if not success:
        if not WEBHOOK_URL:
            print("[notify] No webhook URL configured (SER_NOTIFY_WEBHOOK_URL)", file=sys.stderr)
        print("[notify] Notification not sent (non-blocking)", file=sys.stderr)


if __name__ == "__main__":
    main()
