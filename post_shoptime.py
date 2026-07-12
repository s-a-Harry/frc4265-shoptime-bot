#!/usr/bin/env python3
"""Announce the next FRC 4265 shop session in #shoptime.

Runs from GitHub Actions on Tuesdays and Thursdays and posts the session one
week out, e.g. "Tuesday, July 21, 6-9PM".
"""

import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

TEAM_TZ = ZoneInfo("America/New_York")
CHANNEL_ID = "C04HZNFFFJQ"  # #shoptime
SLACK_API = "https://slack.com/api"

TUESDAY, THURSDAY = 1, 3


def slack_get(method, token, params):
    url = f"{SLACK_API}/{method}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def slack_post(method, token, payload):
    req = urllib.request.Request(
        f"{SLACK_API}/{method}",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
        },
    )
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def main():
    token = os.environ.get("SLACK_BOT_TOKEN")
    if not token:
        sys.exit("SLACK_BOT_TOKEN is not set. Add it under Settings > Secrets.")

    dry_run = os.environ.get("DRY_RUN", "").lower() == "true"
    now = datetime.now(TEAM_TZ)

    # The workflow fires at 12:30 and 13:30 UTC so that one of the two is always
    # 8:30am in New York, whether or not daylight saving is in effect. Whichever
    # run is the wrong one lands outside the 8am hour and stops here.
    if not dry_run:
        if now.hour != 8:
            print(f"Local time is {now:%H:%M} Eastern, not the 8am run. Exiting.")
            return
        if now.weekday() not in (TUESDAY, THURSDAY):
            print(f"Today is {now:%A}, not a shop day. Exiting.")
            return

    session = now + timedelta(days=7)
    message = f"{session:%A}, {session:%B} {session.day}, 6-9PM"
    print(f"Message to post: {message}")

    history = slack_get(
        "conversations.history", token, {"channel": CHANNEL_ID, "limit": 10}
    )
    if not history.get("ok"):
        sys.exit(f"Could not read #shoptime: {history.get('error')}")

    for msg in history.get("messages", []):
        if msg.get("text", "").strip() == message:
            print("This session was already announced. Nothing to do.")
            return

    if dry_run:
        print("Dry run: not posting to Slack.")
        return

    result = slack_post(
        "chat.postMessage", token, {"channel": CHANNEL_ID, "text": message}
    )
    if not result.get("ok"):
        sys.exit(f"Failed to post: {result.get('error')}")

    print("Posted to #shoptime.")


if __name__ == "__main__":
    main()
