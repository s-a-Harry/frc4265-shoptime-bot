#!/usr/bin/env python3
"""Announce the coming week's FRC 4265 shop sessions in #shoptime.

Runs from GitHub Actions on Friday mornings and posts the upcoming Tuesday and
Thursday as two separate messages, e.g.

    Tuesday, July 21, 6-9PM
    Thursday, July 23, 6-9PM

They are posted separately on purpose: the team reacts to each one with a
thumbs up or down to signal attendance, so each session needs its own message
to collect its own reactions.
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

MONDAY, TUESDAY, THURSDAY, FRIDAY = 0, 1, 3, 4

# Enough history to see both of last week's announcements plus normal chatter.
HISTORY_LIMIT = 20


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


def next_weekday(start, weekday):
    """The next given weekday strictly after `start`."""
    days = (weekday - start.weekday()) % 7 or 7
    return start + timedelta(days=days)


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
        if now.weekday() != FRIDAY:
            print(f"Today is {now:%A}, not announcement day. Exiting.")
            return

    sessions = [next_weekday(now, TUESDAY), next_weekday(now, THURSDAY)]
    messages = [f"{d:%A}, {d:%B} {d.day}, 6-9PM" for d in sessions]

    history = slack_get(
        "conversations.history", token, {"channel": CHANNEL_ID, "limit": HISTORY_LIMIT}
    )
    if not history.get("ok"):
        sys.exit(f"Could not read #shoptime: {history.get('error')}")

    already_posted = {m.get("text", "").strip() for m in history.get("messages", [])}

    for message in messages:
        if message in already_posted:
            print(f"Already announced, skipping: {message}")
            continue

        if dry_run:
            print(f"Would post: {message}")
            continue

        result = slack_post(
            "chat.postMessage", token, {"channel": CHANNEL_ID, "text": message}
        )
        if not result.get("ok"):
            sys.exit(f"Failed to post '{message}': {result.get('error')}")
        print(f"Posted: {message}")


if __name__ == "__main__":
    main()
