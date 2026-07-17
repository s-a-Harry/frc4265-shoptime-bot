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

TUESDAY, THURSDAY, FRIDAY = 1, 3, 4

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


def skip_reason(now, scheduled):
    """Why a run at local time `now` should NOT post — or None to go ahead.

    Manual runs (`scheduled` is False) always post: if a human pressed the
    button, they meant it, whatever day and hour it is.

    Scheduled runs post only on Fridays, and only once we've reached 8am
    Eastern. We accept *any* time from 8am onward, not 8:30 exactly, because
    GitHub Actions runs scheduled jobs late — usually by a few minutes, but
    occasionally by over an hour. (This bot silently missed a week when GitHub
    fired the Friday job at 10:11 instead of 8:30 and the old exact-8am check
    threw it away.) Posting a little late is fine; posting nothing is not.

    We still refuse to post *before* 8am, which is what drops the wrong half of
    the two daylight-saving cron runs (see the workflow). The duplicate check
    back in main() is what keeps a late — or repeated — run from announcing the
    same session twice.
    """
    if not scheduled:
        return None
    if now.weekday() != FRIDAY:
        return f"Today is {now:%A}, not announcement day."
    if now.hour < 8:
        return f"It's {now:%H:%M} Eastern, before the 8am announcement window."
    return None


def main():
    token = os.environ.get("SLACK_BOT_TOKEN")
    if not token:
        sys.exit("SLACK_BOT_TOKEN is not set. Add it under Settings > Secrets.")

    dry_run = os.environ.get("DRY_RUN", "").lower() == "true"
    scheduled = os.environ.get("IS_SCHEDULED", "").lower() == "true"
    now = datetime.now(TEAM_TZ)

    reason = skip_reason(now, scheduled)
    if reason:
        print(reason + " Exiting.")
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
