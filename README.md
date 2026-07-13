# frc4265-shoptime-bot

Announces the coming week's shop sessions in the FRC 4265 `#shoptime` Slack
channel.

Every **Friday at 8:30am Eastern**, it posts the upcoming Tuesday and Thursday
as two separate messages:

```
Tuesday, July 21, 6-9PM
Thursday, July 23, 6-9PM
```

They're posted separately on purpose. The team reacts to each one with 👍 / 👎
to signal whether they're coming, so each session needs its own message to
collect its own reactions. Posting on Friday gives everyone the weekend to
respond.

Before posting, the bot reads the recent channel history and skips any session
it already announced, so an accidental double run won't produce duplicates.

## Setup

You only need to do this once.

### 1. Create the Slack app

1. Go to https://api.slack.com/apps and click **Create New App** > **From scratch**.
2. Name it `Shop Time Bot` and pick the **FRC 4265** workspace.
3. In the sidebar, open **OAuth & Permissions**.
4. Scroll to **Bot Token Scopes** and add these two:
   - `chat:write` — lets it post
   - `channels:history` — lets it read recent messages to check for duplicates
5. Scroll back up and click **Install to Workspace**, then **Allow**.
6. Copy the **Bot User OAuth Token**. It starts with `xoxb-`.

If you add the scopes *after* installing, click **Reinstall to Workspace** or
the bot user won't actually appear in Slack.

### 2. Invite the bot to the channel

In Slack, open `#shoptime`, click the channel name at the top, go to the
**Integrations** tab, and choose **Add an App** > `Shop Time Bot`.

The bot cannot post to a channel it hasn't been invited to.

### 3. Give the token to GitHub

1. Go to the repo on GitHub > **Settings** > **Secrets and variables** > **Actions**.
2. Click **New repository secret**.
3. Name it exactly `SLACK_BOT_TOKEN` and paste the `xoxb-...` token as the secret.

## Testing it

Go to the **Actions** tab (the one in the top row of the repo, not the one in
Settings) > **Post shop time to Slack** > **Run workflow**.

Leave **dry run** checked and it will print the exact messages it *would* post,
without posting them. Uncheck it to post for real.

## Changing the schedule

Edit the `cron` line in `.github/workflows/shoptime.yml`. The `5` at the end
means Friday (Sunday is 0). It's listed twice — `12,13` — so that one run always
lands on 8:30am Eastern whether or not daylight saving is in effect; the script
ignores the other. GitHub's scheduler can run a few minutes late when it's busy,
which is normal.
