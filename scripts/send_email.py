#!/usr/bin/env python3
"""Send the digest as a real email. Picks a transport automatically.

    python3 scripts/render_digest_email.py digests/<date>/drafts.json \
      | python3 scripts/send_email.py --subject "Tweets are ready"

Two transports, tried in this order:

1. SMTP (Gmail app password) -- used when GMAIL_ADDRESS and
   GMAIL_APP_PASSWORD are set. Works on a normal machine such as a Mac.
   Does NOT work in the Claude Code cloud sandbox: that environment has
   no direct network egress, only an HTTPS CONNECT proxy, so a raw
   socket to port 465 fails at the network layer no matter what is
   allowlisted.

2. Resend HTTPS API -- used when RESEND_API_KEY and EMAIL_TO are set.
   Works everywhere, including the sandbox, because it is plain HTTPS.
   Requires api.resend.com on the environment's network allowlist.

Environment variables:
    GMAIL_ADDRESS       sender address, also the SMTP login
    GMAIL_APP_PASSWORD  Google app password (needs 2-Step Verification)
    RESEND_API_KEY      Resend API key
    EMAIL_FROM          sender for Resend; defaults to onboarding@resend.dev
    EMAIL_TO            recipient; defaults to GMAIL_ADDRESS when set

Note: the Gmail MCP connector is not a transport here. It exposes only
create_draft/update_draft and no send operation, so it cannot deliver
mail to an inbox.
"""
import argparse
import json
import os
import smtplib
import sys
from email.mime.text import MIMEText
from email.utils import formatdate

import requests

RESEND_URL = "https://api.resend.com/emails"
DEFAULT_RESEND_FROM = "onboarding@resend.dev"


def send_smtp(subject, body, sender, password, recipient):
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient
    msg["Date"] = formatdate(localtime=True)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as server:
        server.login(sender, password)
        server.sendmail(sender, [recipient], msg.as_string())
    return f"Sent via Gmail SMTP as {sender}"


def send_resend(subject, body, api_key, recipient):
    payload = {
        "from": os.environ.get("EMAIL_FROM", DEFAULT_RESEND_FROM),
        "to": [recipient],
        "subject": subject,
        "text": body,
    }
    resp = requests.post(
        RESEND_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        data=json.dumps(payload).encode("utf-8"),
        timeout=30,
    )
    if resp.status_code >= 400:
        raise RuntimeError(f"Resend returned {resp.status_code}: {resp.text}")
    return f"Sent via Resend from {payload['from']}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--subject", required=True)
    parser.add_argument(
        "--input", help="Read body from this file instead of stdin."
    )
    args = parser.parse_args()

    body = (
        open(args.input, encoding="utf-8").read()
        if args.input
        else sys.stdin.read()
    )
    if not body.strip():
        print("ERROR: refusing to send an empty digest.", file=sys.stderr)
        sys.exit(1)

    gmail_addr = os.environ.get("GMAIL_ADDRESS")
    gmail_pw = os.environ.get("GMAIL_APP_PASSWORD")
    resend_key = os.environ.get("RESEND_API_KEY")
    recipient = os.environ.get("EMAIL_TO") or gmail_addr

    if not recipient:
        print(
            "ERROR: no recipient. Set EMAIL_TO (or GMAIL_ADDRESS).",
            file=sys.stderr,
        )
        sys.exit(1)

    attempts = []

    if gmail_addr and gmail_pw:
        try:
            print(send_smtp(args.subject, body, gmail_addr, gmail_pw, recipient))
            print(f"  to: {recipient}\n  subject: {args.subject}")
            return
        except Exception as e:
            attempts.append(f"SMTP failed: {type(e).__name__}: {e}")
    else:
        attempts.append("SMTP skipped: GMAIL_ADDRESS/GMAIL_APP_PASSWORD unset")

    if resend_key:
        try:
            print(send_resend(args.subject, body, resend_key, recipient))
            print(f"  to: {recipient}\n  subject: {args.subject}")
            return
        except Exception as e:
            attempts.append(f"Resend failed: {type(e).__name__}: {e}")
    else:
        attempts.append("Resend skipped: RESEND_API_KEY unset")

    print("ERROR: could not send. Transports tried:", file=sys.stderr)
    for a in attempts:
        print(f"  - {a}", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
