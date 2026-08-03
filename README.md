# X Longevity Daily Digest

An automated agent that searches X (Twitter) every night for
longevity-related/adjacent posts and emails a digest every morning at
8am ET: links + takeaways grouped by topic, in-voice tweet drafts for
each post, a citation-checked deep-dive thread every 4th post, and a
standalone thought-leadership take -- plus a short push notification.

## How it works

1. A scheduled Routine ("Daily longevity digest") fires daily at 8am ET
   in a fresh session. Its prompt is managed in the Routines UI
   (`claude.ai/code/routines`), not in this repo, since trigger-editing
   tools aren't reliably callable from within a session -- see the
   "Editing the routine" note below.
2. That session runs `scripts/x_longevity_search.py`, which calls the X
   API v2 recent-search endpoint for:
   - a set of longevity keywords/phrases (`config.py: KEYWORDS`)
   - posts from a curated list of longevity-focused accounts (`config.py: ACCOUNTS`)
   - restricted to the last 24 hours, English, no retweets
3. Claude reads the raw results, drops anything not actually
   longevity-related, and groups the rest into topics.
4. Per `tone_guide.md` (the @descidecoded voice brief), it drafts:
   - 1-2 short tweet drafts (organic and/or quote-tweet) for 3 of every
     4 posts
   - a 4-8 tweet deep-dive thread for every 4th post, citing real
     peer-reviewed papers found via web search and independently
     re-verified before inclusion
   - one standalone "thought leadership" take per digest, not tied to
     any single post
5. The full digest is emailed to `hannahschick01@gmail.com` via
   `scripts/send_email.py` (Gmail SMTP with an App Password -- see
   setup below), and a short push notification points to it.

### Editing the routine

`create_trigger`/`update_trigger`/`fire_trigger` calls from within a
chat session have intermittently required approval that doesn't
surface properly, so the reliable way to change the routine's prompt is
directly in the UI: `claude.ai/code/routines` -> the routine -> pencil
icon -> edit **Instructions** -> **Save**. Ask Claude for the current
full prompt text to paste in if you're changing it.

## Setup

### 1. Get X API access with search permission

You need a developer account and app at the X Developer Portal with a
tier that includes the **recent search** endpoint
(`GET /2/tweets/search/recent`). The free tier does not include search
over other users' posts -- you need at least the paid **Basic** tier (or
higher). Steps:

1. Go to the X Developer Portal and create a Project + App (or use an
   existing one).
2. Subscribe to a tier that includes recent search (check current
   pricing/limits on the portal -- these change over time).
3. In the app's "Keys and tokens" tab, generate a **Bearer Token**.

### 2. Set the token

Add it as an environment variable named `X_BEARER_TOKEN` in this
environment's configuration (not in chat, not committed to the repo).

### 3. Test manually

```bash
pip install -r requirements.txt
export X_BEARER_TOKEN=xxxx   # or rely on the environment-level var
python3 scripts/x_longevity_search.py
```

This prints a JSON array of matched posts to stdout. If `X_BEARER_TOKEN`
is missing, it exits with an error explaining what's needed.

### 4. Enable the daily routine

A Routine named **"Daily longevity digest"** has already been created,
firing at 8am ET (12:00 UTC) every day, but it's disabled until the
token is set up. Once `X_BEARER_TOKEN` is in place, ask Claude to enable
it, or use the trigger tools directly.

**DST note:** 12:00 UTC is 8am during Eastern Daylight Time (roughly
March-November). When clocks fall back to EST in November, this will
fire at 7am ET instead until the cron is adjusted to 13:00 UTC. Ask
Claude to flip it around the DST changeover, or set a reminder.

## Customizing

Edit `config.py`:

- `KEYWORDS` -- phrases searched for anywhere in a post.
- `ACCOUNTS` -- handles (no `@`) whose posts are always pulled in,
  regardless of keyword match. **Verify these are correct/current** --
  they're a starting point, not verified handles.
- `LOOKBACK_HOURS` -- how far back each run searches (default 24).
- `MAX_RESULTS_PER_CALL` -- API page size (10-100).

## Cost/rate-limit notes

Each run issues a handful of API calls (one per chunk of keywords/
accounts that fits under the query-length limit). Recent-search tiers
have a monthly post-read cap -- keep an eye on usage in the developer
portal, especially if you widen `KEYWORDS`/`ACCOUNTS` significantly.
