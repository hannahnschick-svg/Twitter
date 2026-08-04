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
5. The full digest is emailed via `scripts/send_email.py` (Resend HTTPS
   API -- see setup below), and a short push notification points to it.

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

Add it as an environment variable named `X_BEARER_TOKEN` in the cloud
environment's configuration (not in chat, not committed to the repo).

### 3. Set up email delivery

Delivery uses the **Resend** HTTPS API rather than SMTP. This is not a
preference -- the cloud sandbox has no direct network egress, so a raw
socket to `smtp.gmail.com:465` fails at the network layer no matter what
is allowlisted. Only HTTPS-through-the-proxy works, which rules out
`smtplib` entirely.

1. Sign up at resend.com and create an API key (the free tier is far
   more than one email a day needs).
2. Add these environment variables alongside `X_BEARER_TOKEN`:
   - `RESEND_API_KEY` -- the key from step 1
   - `EMAIL_TO` -- where the digest should land
   - `EMAIL_FROM` -- optional. Defaults to `onboarding@resend.dev`,
     which Resend permits only for sending to your own account address.
     To send anywhere else, verify a domain in Resend and use an address
     on it.

### 4. Allow the required domains

The environment's network access defaults to a **Trusted** allowlist that
excludes both of the hosts this project calls. Open the environment
settings, set **Network access** to **Custom**, tick *"Also include
default list of common package managers"*, and add:

```
api.twitter.com
api.resend.com
```

Add `api.x.com` too if you switch `config.API_HOST` (see Customizing).
Anything missing here fails with `403` on the proxy's CONNECT tunnel,
which looks like an auth error but isn't -- verify with:

```bash
curl -sS -o /dev/null https://api.twitter.com/2/tweets/search/recent
```

A `401` means the host is reachable (good). `CONNECT tunnel failed,
response 403` means it isn't allowlisted.

### 5. Test manually

```bash
pip install -r requirements.txt
python3 scripts/x_longevity_search.py > work/x-posts-test.json
python3 -m json.tool work/x-posts-test.json > /dev/null && echo "valid JSON"
```

This writes a JSON array of matched posts. If `X_BEARER_TOKEN` is
missing, it exits with an error explaining what's needed.

### 6. Enable the daily routine

A Routine named **"Daily longevity digest"** fires at 8am ET
(12:00 UTC) daily. Its prompt lives in the Routines UI, not this repo.

**DST note:** 12:00 UTC is 8am during Eastern Daylight Time (roughly
March-November). When clocks fall back to EST in November, this fires at
7am ET until the cron is changed to 13:00 UTC.

## Customizing

Edit `config.py`:

- `KEYWORDS` -- phrases searched for anywhere in a post.
- `ACCOUNTS` -- handles (no `@`) whose posts are always pulled in,
  regardless of keyword match. **Verify these are correct/current** --
  they're a starting point, not verified handles.
- `LOOKBACK_HOURS` -- how far back each run searches (default 24).
- `MAX_RESULTS_PER_CALL` -- API page size (10-100).
- `MAX_PAGES_PER_QUERY` -- pages followed per query before stopping.
  Each page is another billed call against the monthly post-read cap.
- `API_HOST` -- `api.twitter.com` (default) or `api.x.com`. Both serve
  the same v2 endpoints, but each must be allowlisted separately, and
  only `api.twitter.com` is allowlisted today.
- `EXTRA_FILTERS` -- currently English only, no retweets, no replies.

### Long-form posts

The search requests the `note_tweet` field and prefers it over the
top-level `text`, because X truncates `text` for long-form posts. Without
this the agent would draft from partial content without any sign it was
truncated.

## Cost/rate-limit notes

Each run issues a handful of API calls (one per chunk of keywords/
accounts that fits under the query-length limit, times up to
`MAX_PAGES_PER_QUERY` pages). Recent-search tiers have a monthly
post-read cap -- keep an eye on usage in the developer portal,
especially if you widen `KEYWORDS`/`ACCOUNTS` or raise the page cap.

## Saving drafts back to X

The digest delivers drafts as text for you to review and post yourself.
There is no API for X's native Drafts folder -- it's a client-only
feature -- so the only way to populate it automatically is to drive a
logged-in browser session, which this cloud environment cannot do (no
signed-in session, and X actively detects automation, which risks
security challenges on the account). Copy-pasting from the email is the
supported path.
