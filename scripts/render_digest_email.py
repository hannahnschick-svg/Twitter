#!/usr/bin/env python3
"""Render drafts.json into a readable plain-text email body.

    python3 scripts/render_digest_email.py digests/2026-08-05/drafts.json
    python3 scripts/render_digest_email.py digests/2026-08-05/drafts.json -o body.txt

Produces UTF-8 plain text that:
  - separates every draft and topic clearly
  - includes the original X post link for quote-tweets
  - includes paper / DOI / reference links
  - omits raw internal X transcripts, so only the drafts and their
    sources appear -- not the scraped post bodies

Reads the optional "topic" and "source_url" fields when present, and
groups by topic in the order topics first appear.
"""
import argparse
import json
import sys
from collections import OrderedDict
from pathlib import Path

RULE = "=" * 62
THIN = "-" * 62


def wrap_block(text, indent="  "):
    """Indent a draft body without reflowing it -- line breaks are authored."""
    return "\n".join(indent + line if line else "" for line in text.split("\n"))


def render_standalone(d, n):
    out = [f"[{n}] STANDALONE", ""]
    out.append(wrap_block(d["text"]))
    if d.get("source_url"):
        out += ["", f"  Source: {d['source_url']}"]
    return "\n".join(out)


def render_quote(d, n):
    out = [f"[{n}] QUOTE-TWEET", ""]
    out.append(wrap_block(d["text"]))
    out += ["", f"  Quoting: {d['quote_of']}"]
    return "\n".join(out)


def render_thread(d, n):
    tweets = d["tweets"]
    out = [f"[{n}] THREAD ({len(tweets)} posts)", ""]
    for i, t in enumerate(tweets, 1):
        out.append(f"  --- {i}/{len(tweets)} ---")
        out.append(wrap_block(t))
        out.append("")
    if d.get("paper_link"):
        out.append(f"  Primary paper (appended to each post): {d['paper_link']}")
    for src in d.get("sources", []):
        if isinstance(src, dict):
            bits = [src.get("title"), src.get("journal"), src.get("link") or src.get("doi")]
            out.append("  Source: " + " -- ".join(b for b in bits if b))
        else:
            out.append(f"  Source: {src}")
    return "\n".join(out)


RENDERERS = {
    "standalone": render_standalone,
    "quote": render_quote,
    "thread": render_thread,
}


def render(drafts, date=None):
    counts = {}
    for d in drafts:
        counts[d["type"]] = counts.get(d["type"], 0) + 1
    summary = ", ".join(f"{v} {k}" for k, v in sorted(counts.items()))

    lines = [RULE, f"TWEETS ARE READY{f' -- {date}' if date else ''}", RULE, ""]
    lines.append(f"{len(drafts)} drafts: {summary}")
    lines += ["", "Review below, then post from X. Nothing has been published.", ""]

    by_topic = OrderedDict()
    for d in drafts:
        by_topic.setdefault(d.get("topic") or "Drafts", []).append(d)

    n = 0
    for topic, items in by_topic.items():
        lines += ["", RULE, topic.upper(), RULE, ""]
        for d in items:
            n += 1
            kind = d.get("type")
            if kind not in RENDERERS:
                lines += [f"[{n}] UNKNOWN TYPE {kind!r} -- skipped", ""]
                continue
            lines.append(RENDERERS[kind](d, n))
            lines += ["", THIN, ""]

    return "\n".join(lines).rstrip() + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("drafts", help="Path to drafts.json")
    parser.add_argument("-o", "--output", help="Write here instead of stdout")
    parser.add_argument("--date", help="Date shown in the header")
    args = parser.parse_args()

    path = Path(args.drafts)
    drafts = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(drafts, list):
        print("ERROR: drafts file must be a JSON array.", file=sys.stderr)
        sys.exit(1)

    date = args.date or path.parent.name
    body = render(drafts, date)

    if args.output:
        Path(args.output).write_text(body, encoding="utf-8")
        print(f"Wrote {args.output} ({len(body)} chars)")
    else:
        sys.stdout.write(body)


if __name__ == "__main__":
    main()
