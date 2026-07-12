# frc4265-shoptime-bot

Posts the upcoming shop session to the FRC 4265 `#shoptime` Slack channel.

Every Tuesday and Thursday at 8:30am Eastern, it announces the session one week
out, in the team's usual format:

```
Tuesday, July 21, 6-9PM
```

Before posting it reads the last 10 messages in the channel, so if it somehow
runs twice it won't post a duplicate.

## Setup

You only need to do this once.

### 1. Create the Slack app

1. Go to https://api.slack.com/apps and click **Create New App** > **From scratch**.
2. Name it `Shop Time Bot` and pick the **FRC 4265** workspace.
3. In the sidebar, open **OAuth & Permissions**.
4. Scroll to **Bot Token Scopes** and add these two:
   - `chat:write` — lets it post
   - `channels:history` — lets it read the last 10 messages to check for duplicates
5. Scroll back up and click **Install to Workspace**, then **Allow**.
6. Copy the **Bot User OAuth Token**. It starts with `xoxb-`.

### 2. Invite the bot to the channel

In Slack, go to `#shoptime` and send:

```
/invite @Shop Time Bot
```

The bot cannot post to a channel it hasn't been invited to.

### 3. Give the token to GitHub

1. Go to this repo on GitHub > **Settings** > **Secrets and variables** > **Actions**.
2. Click **New repository secret**.
3. Name it exactly `SLACK_BOT_TOKEN` and paste the `xoxb-...` token as the value.

## Testing it

Go to the **Actions** tab > **Post shop time to Slack** > **Run workflow**.

Leave **dry run** checked and it will show you the exact message it *would*
post, without posting. Uncheck it to post for real.

## Changing the schedule

Edit the `cron` line in `.github/workflows/shoptime.yml`. The `2,4` at the end
means Tuesday and Thursday. Note that GitHub's scheduler can run a few minutes
late when it's busy; that's normal and doesn't affect the message.
