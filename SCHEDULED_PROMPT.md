# Scheduled prompt

The instruction the agent runs each morning. Used two ways:

- **Locally**: `claude "$(cat SCHEDULED_PROMPT.md)"` from the project root.
- **Cloud**: pasted into the Routine's Instructions field at
  claude.ai/code/routines.

Never put the bearer token in this file.

---

You are running the daily longevity digest. Work from the project root.

## 1. Fetch

```bash
mkdir -p work
python3 scripts/x_longevity_search.py > work/posts.json
python3 -m json.tool work/posts.json > /dev/null
```

If the fetch fails, read the error and report the specific cause, then stop.
These look similar but have different fixes:

- `CONNECT tunnel failed, response 403` — the host isn't on the cloud
  environment's network allowlist. Only happens in the cloud sandbox.
- HTTP 401 — `X_BEARER_TOKEN` is missing or invalid.
- HTTP 403 from X — the API tier doesn't include recent search.
- HTTP 429 — rate limited.

## 2. Filter and cluster

Read `work/posts.json`. Each entry has `id`, `url`, `author`, `author_name`,
`text`, `created_at`, `matched`. The `text` field is already the full
long-form body wherever one exists, so use it as-is.

- Drop anything not genuinely longevity-related or adjacent. The keyword
  and account matching is a starting filter, not proof of relevance.
- Group survivors into 2-6 topic clusters based on what's actually in
  this batch. Don't force a fixed taxonomy.
- Number the survivors in one continuous sequence in the order you'll
  present them, not restarting per cluster. This drives the rotation below.

## 3. Draft

Read `tone_guide.md` in full first — it is the voice brief for
@descidecoded, and every draft must pass its Pre-post checklist. Zero
emoji, ever. At most one hashtag, and only a real community tag.
American spelling. Short drafts stay under ~280 characters.

Rotate across the numbered sequence:

**Posts 1-3 of every group of 4** — one or two short drafts each:

- *organic*: a standalone tweet inspired by the post or what it links to.
  A genuine idea or hook in-voice, not a restatement of the original.
- *quote*: commentary to accompany quote-tweeting that specific post.
  A distinct angle or reaction, not a summary.

**Every 4th post** — instead of short drafts, one deep-dive thread on that
post's topic. 4-8 tweets, numbered `1/n`. Open on the payoff, one idea per
tweet, close on a clean landing.

- Cite real peer-reviewed literature. Use web search to find actual papers
  supporting your specific claims, and name the paper and journal inline.
- **Verification pass — mandatory, and separate from the search above.**
  After drafting, independently re-verify every citation: re-search each
  paper by title and authors to confirm it exists, and read enough of the
  actual abstract to confirm it supports the specific claim or number you
  attributed to it — not merely that a paper on a similar topic exists.
  If a citation fails either check, find a genuine alternative, soften the
  claim to what you can verify, or cut the point entirely.

  Never leave an unverified or invented citation in a final draft. This is
  the most important instruction here: a fabricated citation on a science
  account is worse than publishing no thread at all.

**One thought-leadership take per run**, not tied to any single post. Look
across the themes in today's whole batch and write an original opinion,
prediction, or perspective on the longevity space itself. Opinion and
analysis, not a literature review — no citation required, but don't assert
a statistic you aren't confident is accurate. Single tweet by default; a
2-3 tweet thread only if the take genuinely needs the room.

## 4. Write both outputs

**`work/digest.md`** — human-readable review copy. Thought-leadership take
first, then each cluster with a short header, and under it every post's
link, a one-line factual takeaway, and its labeled drafts. Threads list
`Verified sources:` (title, journal, link/DOI) beneath them, not inside
any tweet.

**`work/drafts.json`** — machine-readable, for the draft saver. A JSON
array using exactly these shapes:

```json
[
  {"type": "standalone", "text": "...", "source_url": "https://..."},
  {"type": "quote", "quote_of": "https://x.com/user/status/123", "text": "..."},
  {"type": "thread", "tweets": ["1/3 ...", "2/3 ...", "3/3 ..."],
   "paper_link": "https://doi.org/..."}
]
```

- `quote_of` must be the exact `url` of the post being quoted, so the
  composer attaches the right source.
- `paper_link` is appended to every post in a thread — omit the field if
  there's no single primary paper.
- Don't put the source link inside `text`; use `source_url` so it's
  appended consistently.

## 5. Report

Summarize what you produced: counts by type, which clusters, and any
citation you had to cut or soften during verification. Say so explicitly
if a thread ended up thinner than intended because sources didn't hold up.

Keep your own framing factual and free of filler. This is a scan report
with drafts attached, not an essay. The drafts are the only place the
in-voice writing happens.

## 6. Saving to X (separate, manual step)

Do not run the draft saver yourself. Once the drafts are reviewed:

```bash
python3 scripts/save_x_drafts.py --input work/drafts.json --dry-run
python3 scripts/save_x_drafts.py --input work/drafts.json
```

It opens a visible browser, saves each draft, and never posts.
