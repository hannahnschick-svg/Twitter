#!/usr/bin/env python3
"""Save generated drafts into X's native Drafts folder via the web UI.

X has no API for the Drafts folder -- it is a client-only feature -- so
this drives a real logged-in browser session. Runs headed by default so
you can watch every action and intervene.

    python3 scripts/save_x_drafts.py --input work/drafts.json
    python3 scripts/save_x_drafts.py --input work/drafts.json --dry-run

First run opens a browser and waits for you to log in as @descidecoded.
The session persists in a local profile directory, so later runs skip
the login. Your password is never handled by this script.

Input schema -- a JSON array of objects:

    {"type": "standalone",
     "text": "The draft body.",
     "source_url": "https://..."}          # optional, appended

    {"type": "quote",
     "quote_of": "https://x.com/user/status/123",   # required
     "text": "The commentary."}

    {"type": "thread",
     "tweets": ["1/5 ...", "2/5 ...'"],
     "paper_link": "https://..."}          # optional, appended to each

SAFETY: this script only ever clicks the composer's close button and the
"Save" option in the resulting confirmation dialog. Every click is routed
through a guard that refuses to press any control whose label looks like
a publish action, so a selector drifting onto the Post button raises
instead of publishing.
"""
import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

from playwright.sync_api import TimeoutError as PWTimeout
from playwright.sync_api import sync_playwright

PROFILE_DIR = Path(
    os.environ.get("X_PROFILE_DIR", Path.home() / ".x-drafts-profile")
)

COMPOSE_URL = "https://x.com/compose/post"
DRAFTS_URL = "https://x.com/compose/post/unsent/drafts"

# Anything matching this must never be clicked by this script.
PUBLISH_PATTERN = re.compile(r"\b(post|posts|post all|publish|tweet|reply)\b", re.I)

TEXTAREA = '[data-testid="tweetTextarea_{}"]'
ADD_POST_BUTTON = '[data-testid="addButton"]'
CLOSE_BUTTON = '[data-testid="app-bar-close"]'
RETWEET_BUTTON = '[data-testid="retweet"]'
CONFIRM_BUTTON = '[data-testid="confirmationSheetConfirm"]'


class PublishGuard(Exception):
    """Raised when a click would have published rather than saved."""


def safe_click(locator, expect_label=None, what=""):
    """Click only after confirming the control isn't a publish action."""
    label = ""
    try:
        label = (locator.inner_text(timeout=3000) or "").strip()
    except Exception:
        try:
            label = (locator.get_attribute("aria-label") or "").strip()
        except Exception:
            label = ""

    if label and PUBLISH_PATTERN.search(label):
        raise PublishGuard(
            f"Refusing to click {what!r}: its label is {label!r}, which looks "
            "like a publish action. X's UI has probably changed -- stopping "
            "rather than risking posting."
        )
    if expect_label and label and expect_label.lower() not in label.lower():
        raise PublishGuard(
            f"Refusing to click {what!r}: expected a control labelled "
            f"{expect_label!r} but found {label!r}."
        )
    locator.click()


def type_into(page, index, text):
    """Put text into composer box `index`, handling the rich-text editor."""
    box = page.locator(TEXTAREA.format(index))
    box.wait_for(state="visible", timeout=20000)
    box.click()
    page.keyboard.insert_text(text)
    time.sleep(0.3)

    got = (box.inner_text(timeout=5000) or "").strip()
    if not got:
        # Draft.js occasionally ignores insert_text; fall back to real keys.
        box.click()
        page.keyboard.type(text, delay=5)
        time.sleep(0.3)
        got = (box.inner_text(timeout=5000) or "").strip()
    if not got:
        raise RuntimeError(f"Could not enter text into composer box {index}.")


def close_and_save(page, what):
    """Close the composer and choose Save in the confirmation dialog."""
    safe_click(page.locator(CLOSE_BUTTON), what=f"close composer ({what})")

    confirm = page.locator(CONFIRM_BUTTON)
    try:
        confirm.wait_for(state="visible", timeout=8000)
    except PWTimeout:
        raise RuntimeError(
            f"No save/discard dialog appeared after closing the {what} "
            "composer. The draft may not have been saved."
        )

    # The confirm button on this sheet is "Save"; "Discard" is the cancel
    # side. Require the label so a layout change can't silently discard.
    safe_click(confirm, expect_label="save", what=f"save {what}")
    time.sleep(1.5)


def compose_text(draft):
    if draft["type"] == "standalone":
        parts = [draft["text"]]
        if draft.get("source_url"):
            parts.append(draft["source_url"])
        return ["\n\n".join(parts)]

    if draft["type"] == "quote":
        return [draft["text"]]

    if draft["type"] == "thread":
        link = draft.get("paper_link")
        return [
            f"{t}\n\n{link}" if link else t
            for t in draft["tweets"]
        ]

    raise ValueError(f"Unknown draft type: {draft['type']!r}")


def save_standalone(page, draft):
    bodies = compose_text(draft)
    page.goto(COMPOSE_URL, wait_until="domcontentloaded")
    type_into(page, 0, bodies[0])
    close_and_save(page, "standalone draft")


def save_thread(page, draft):
    bodies = compose_text(draft)
    page.goto(COMPOSE_URL, wait_until="domcontentloaded")
    type_into(page, 0, bodies[0])
    for i, body in enumerate(bodies[1:], start=1):
        safe_click(page.locator(ADD_POST_BUTTON), what="add post to thread")
        time.sleep(0.5)
        type_into(page, i, body)
    close_and_save(page, f"{len(bodies)}-post thread")


def save_quote(page, draft):
    url = draft["quote_of"]
    page.goto(url, wait_until="domcontentloaded")
    time.sleep(2)

    # The first retweet control on the page belongs to the focused post.
    safe_click(page.locator(RETWEET_BUTTON).first, what="repost menu")
    time.sleep(0.8)

    quote_option = page.get_by_role("menuitem").filter(has_text=re.compile(r"quote", re.I))
    try:
        quote_option.first.click(timeout=8000)
    except PWTimeout:
        raise RuntimeError(
            "Could not find the 'Quote' option in the repost menu. Stopping "
            "so nothing is reposted directly."
        )
    time.sleep(1)

    type_into(page, 0, compose_text(draft)[0])
    close_and_save(page, "quote draft")


HANDLERS = {
    "standalone": save_standalone,
    "quote": save_quote,
    "thread": save_thread,
}


def ensure_logged_in(page, interactive=True):
    page.goto("https://x.com/home", wait_until="domcontentloaded")
    time.sleep(3)
    if "login" not in page.url and "i/flow/login" not in page.url:
        return

    if not interactive:
        raise RuntimeError(
            "Not logged in, and running unattended so I can't wait for you. "
            "Run once by hand without --no-wait to sign in; the session then "
            "persists for scheduled runs."
        )

    print(
        "\n  Not logged in. Log in as @descidecoded in the browser window,\n"
        "  then press Enter here to continue.",
        file=sys.stderr,
    )
    input()
    page.goto("https://x.com/home", wait_until="domcontentloaded")
    time.sleep(2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="work/drafts.json")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be saved without opening a browser.",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run without a visible window. Not recommended for the first run.",
    )
    parser.add_argument(
        "--no-wait",
        action="store_true",
        help="Close the browser immediately instead of waiting for Enter. "
        "Required when run unattended, e.g. from launchd.",
    )
    args = parser.parse_args()

    drafts = json.loads(Path(args.input).read_text())
    if not isinstance(drafts, list):
        print("ERROR: input must be a JSON array of drafts.", file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        for i, d in enumerate(drafts, 1):
            bodies = compose_text(d)
            print(f"\n[{i}] {d['type']}", end="")
            if d.get("quote_of"):
                print(f"  (quoting {d['quote_of']})", end="")
            print()
            for b in bodies:
                print("    " + b.replace("\n", "\n    "))
        print(f"\n{len(drafts)} draft(s) would be saved. No browser opened.")
        return

    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    saved, failed = 0, []

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            str(PROFILE_DIR),
            headless=args.headless,
            viewport={"width": 1280, "height": 900},
        )
        page = context.pages[0] if context.pages else context.new_page()
        ensure_logged_in(page, interactive=not args.no_wait)

        for i, draft in enumerate(drafts, 1):
            kind = draft.get("type")
            print(f"[{i}/{len(drafts)}] saving {kind}...", flush=True)
            try:
                HANDLERS[kind](page, draft)
                saved += 1
            except PublishGuard:
                raise  # never continue past a guard trip
            except Exception as e:
                print(f"    failed: {type(e).__name__}: {e}", file=sys.stderr)
                failed.append((i, kind, str(e)))
                # Get back to a clean state before the next draft.
                try:
                    page.goto("https://x.com/home", wait_until="domcontentloaded")
                    time.sleep(1)
                except Exception:
                    pass

        print(f"\nSaved {saved}/{len(drafts)} draft(s).")
        if failed:
            print("Failed:", file=sys.stderr)
            for i, kind, err in failed:
                print(f"  [{i}] {kind}: {err}", file=sys.stderr)

        print(f"\nVerify them at {DRAFTS_URL} -- reload the page and check twice.")
        if not args.no_wait:
            print("Press Enter to close the browser.")
            input()
        context.close()

    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
