# X Longevity Daily Digest

Scans X for longevity-related and adjacent posts from the last 24 hours,
drafts tweets about them in the @descidecoded voice, and saves those
drafts straight into X's Drafts folder for review. Nothing is ever posted
automatically.

Each run produces:

- short drafts (organic or quote-tweet) for three of every four posts
- a deep-dive thread for every fourth post, citing peer-reviewed papers
  that are independently re-verified before they make the cut
- one thought-leadership take per run, not tied to any single post

## Pipeline

```
scripts/x_longevity_search.py   ->  work/posts.json
        (X API v2 recent search)

agent, per SCHEDULED_PROMPT.md  ->  digests/<date>/digest.md    (review)
        + tone_guide.md             digests/<date>/drafts.json  (machine)

scripts/send_email.py           ->  inbox
scripts/save_x_drafts.py        ->  X Drafts folder
        (headed browser, save-only)
```

`digests/` is committed; `work/` is scratch and ignored.

## Cloud and laptop, split by what each can do

The cloud sandbox has no signed-in browser, so it cannot save into X's
Drafts folder — that step needs your machine. But the scheduled work
shouldn't depend on your laptop being open. So the two split:

- **Cloud, 8am daily, laptop closed or not.** Search, filter, draft,
  verify citations, commit `digests/<date>/` to the branch, email the
  digest.
- **Laptop, whenever you next open it.** Pull and push the drafts into X.

```bash
git pull
python3 scripts/save_x_drafts.py --input digests/<date>/drafts.json --dry-run
python3 scripts/save_x_drafts.py --input digests/<date>/drafts.json
```

If you never get to it, nothing is lost — the digest is in your inbox and
committed to the repo.

## Local setup

```bash
cd /path/to/this/repo
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m playwright install chromium
```

### Bearer token

The X Developer Console app has an app **Bearer Token**. It is read only
from the environment — never put it in source, a prompt, git, this file,
or `SCHEDULED_PROMPT.md`.

In zsh, enter it without echoing it to the terminal:

```zsh
read -s "X_BEARER_TOKEN?Paste X bearer token: "
export X_BEARER_TOKEN
```

The token needs an API tier that includes `GET /2/tweets/search/recent`.
The free tier does not include searching other users' posts, so this
needs at least the paid Basic tier.

### Test retrieval

```bash
mkdir -p work
python3 scripts/x_longevity_search.py > work/x-posts-test.json
python3 -m json.tool work/x-posts-test.json > /dev/null && echo "valid JSON"
```

Each entry has `id`, `url`, `author`, `author_name`, `text`, `created_at`,
and `matched`.

### Run a digest

```bash
claude "$(cat SCHEDULED_PROMPT.md)"
```

Then review `work/digest.md` before saving anything.

## Saving drafts to X

X has no API for the Drafts folder — it's a client-only feature — so
`save_x_drafts.py` drives a real logged-in browser.

```bash
python3 scripts/save_x_drafts.py --input work/drafts.json --dry-run  # inspect
python3 scripts/save_x_drafts.py --input work/drafts.json            # save
```

The first run opens a browser and waits for you to log in as
@descidecoded. The session persists in `~/.x-drafts-profile` (override
with `X_PROFILE_DIR`), so later runs skip the login. The script never
handles your password.

How each type is saved, matching X's own flow:

- **standalone and thought-leadership** — open the composer, enter the
  draft and its source link, close, Save.
- **quote-tweet** — open the exact original post, Repost → Quote, enter
  the commentary, close, Save. Going through the real post is what
  preserves the source attachment.
- **thread** — build every post in one composer, with the primary-paper
  link in each, then close and save the whole thread.

Afterwards open Drafts → Unsent posts, verify every draft, reload, and
verify again.

### Safety

The script only ever clicks the composer's close button and **Save** in
the confirmation dialog. Every click passes through a guard that refuses
any control labelled `Post`, `Post all`, `Publish`, or `Reply`, and that
refuses to press `Discard` where it expects `Save`. If X changes its UI
and a selector drifts onto a publish control, the run aborts instead of
posting.

### Account risk

X actively detects browser automation. Driving a logged-in session can
trigger a security challenge or a temporary lock on the account, and that
risk exists regardless of the save-only guarantee above. Running headed
and watching the first few runs is the mitigation. Copy-pasting from
`work/digest.md` avoids the risk entirely if you'd rather not automate it.

## Configuration

Edit `config.py`:

- `KEYWORDS` — phrases searched for anywhere in a post.
- `ACCOUNTS` — handles (no `@`) always pulled in regardless of keyword
  match. **Verify these are current** — they're a starting point, not
  checked handles.
- `LOOKBACK_HOURS` — how far back each run searches. Default 24.
- `MAX_RESULTS_PER_CALL` — API page size, 10-100.
- `MAX_PAGES_PER_QUERY` — pages followed per query. Each page is another
  billed call against the monthly post-read cap.
- `EXTRA_FILTERS` — English only, no retweets, no replies.
- `API_HOST` — defaults to `api.x.com`, overridable with the `X_API_HOST`
  environment variable. See the cloud note below.

### Long-form posts

The search requests `note_tweet` and prefers it over the top-level `text`,
because X truncates `text` for long-form posts. Without this the agent
would draft from partial content with no sign it was truncated.

## Optional: cloud runs

The same pipeline runs as a Routine at claude.ai/code/routines, which
fires on schedule without your laptop open. Two things differ there:

**Network allowlist.** The sandbox only reaches hosts on the environment's
allowlist, and `api.x.com` is not on it by default — either add it, or set
`X_API_HOST=api.twitter.com`, which is allowlisted and serves the same v2
endpoints. Verify with:

```bash
curl -sS -o /dev/null https://api.x.com/2/tweets/search/recent
```

`401` means reachable. `CONNECT tunnel failed, response 403` means it
isn't allowlisted.

**Email instead of browser drafts.** The sandbox has no signed-in browser,
so `save_x_drafts.py` can't run there. `scripts/send_email.py` mails the
digest instead, using the Resend HTTPS API — not SMTP, because the sandbox
has no direct network egress and a raw socket to port 465 fails at the
network layer regardless of allowlisting. Set `RESEND_API_KEY` and
`EMAIL_TO`, and allowlist `api.resend.com`.

## Cost notes

Each run issues a few API calls per query chunk, times up to
`MAX_PAGES_PER_QUERY` pages. Recent-search tiers have a monthly
post-read cap — watch usage in the developer portal if you widen
`KEYWORDS`, `ACCOUNTS`, or the page cap.
