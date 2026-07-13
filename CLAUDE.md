# CLAUDE.md

Guidance for Claude Code when working in this repo.

## What this is

A single-purpose bot that announces FRC 4265's shop sessions in the team's
Slack channel `#shoptime` (`C04HZNFFFJQ`). It is deliberately small: one Python
script and one GitHub Actions workflow, no dependencies beyond the standard
library.

- `post_shoptime.py` — computes the dates, checks for duplicates, posts.
- `.github/workflows/shoptime.yml` — the Friday 8:30am ET cron.

The owner is not a developer. Prefer clear, boring code and explain changes in
plain language rather than jargon.

## Things that will bite you

**The two messages must stay separate.** The bot posts the coming Tuesday and
the coming Thursday as two individual messages. The team reacts to each one with
👍 / 👎 to signal attendance — the reactions *are* the attendance poll. Combining
them into one message would destroy that. This is the whole point of the tool.

**The message format is copied from what the team already does by hand:**
`Tuesday, July 21, 6-9PM`. Match it exactly. The duplicate check compares
message text literally, so any drift in the format silently breaks it.

**The cron is listed twice on purpose** (`30 12,13 * * 5`). GitHub cron is
UTC-only, so a single entry would drift by an hour when daylight saving ends.
Firing at both 12:30 and 13:30 UTC means one of them is always 8:30am Eastern;
the script checks the local hour and exits from the wrong one.

**That time guard only applies to scheduled runs** (`IS_SCHEDULED`). Manual runs
via *Run workflow* deliberately bypass it — if a human pressed the button, they
meant it. Don't "fix" this by applying the guard everywhere; it was a real bug
that blocked intentional manual posts.

**Do not try to make this a Claude cloud routine.** `/schedule` plus the Slack
MCP connector does not work — see the two upstream bugs noted in the project
memory. GitHub Actions is the working path.

## Testing

There's no test suite. Verify changes with **Actions → Post shop time to Slack →
Run workflow** with *dry run* checked: it prints the exact messages it would
post without touching Slack. Dry run also bypasses the day/hour guard, so it
works any day of the week.

## Secrets

`SLACK_BOT_TOKEN` (a Slack bot token, `xoxb-...`) lives in the repo's Actions
secrets. Scopes: `chat:write` and `channels:history`. The bot must also be
invited to `#shoptime` or posting fails with `not_in_channel`.
