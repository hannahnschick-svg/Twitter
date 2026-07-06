# X Longevity Daily Digest

An automated agent that searches X (Twitter) every night for
longevity-related/adjacent posts and delivers a digest (links + tweet
summaries, grouped by topic) every morning at 8am ET, with a short push
notification pointing to it.

## How it works

1. A scheduled Routine fires daily at 8am ET in a fresh session.
2. That session runs `scripts/x_longevity_search.py`, which calls the X
   API v2 recent-search endpoint for:
   - a set of longevity keywords/phrases (`config.py: KEYWORDS`)
   - posts from a curated list of longevity-focused accounts (`config.py: ACCOUNTS`)
   - restricted to the last 24 hours, English, no retweets
3. Claude reads the raw results, drops anything not actually
   longevity-related, groups the rest into topics, and writes a digest
   (topic headers, each post's link + a one-line takeaway) as its reply
   in that session.
4. Claude sends a short push notification (e.g. "Longevity digest:
   14 posts across 3 topics (senolytics, NAD+, VO2 max)") so you know
   it's ready without needing the full text pushed to your phone.

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
