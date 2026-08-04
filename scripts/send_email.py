#!/usr/bin/env python3
"""Email the digest via an HTTPS email API (Resend).

Usage:
    python3 scripts/send_email.py --subject "Some subject" < body.txt

Reads the email body from stdin.

Why HTTP and not SMTP: the cloud environment has no direct network
egress -- all traffic is tunneled through an HTTPS CONNECT proxy. A raw
socket to smtp.gmail.com:465 fails at the network layer regardless of
domain allowlisting, so smtplib cannot work here. An HTTPS API call can.

Required environment variables:
    RESEND_API_KEY -- API key from https://resend.com (free tier is
                      ample for one email a day)
    EMAIL_TO       -- recipient address
    EMAIL_FROM     -- sender address. Until you verify your own domain in
                      Resend, use "onboarding@resend.dev", which Resend
                      allows only for sending to your own account address.

The environment must also allow outbound HTTPS to api.resend.com.
"""
import argparse
import json
import os
import sys

import requests

SEND_URL = "https://api.resend.com/emails"
DEFAULT_FROM = "onboarding@resend.dev"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--subject", required=True)
    args = parser.parse_args()

    api_key = os.environ.get("RESEND_API_KEY")
    recipient = os.environ.get("EMAIL_TO")
    if not api_key or not recipient:
        print(
            "ERROR: RESEND_API_KEY and/or EMAIL_TO is not set. See README.md "
            "for how to configure email delivery.",
            file=sys.stderr,
        )
        sys.exit(1)

    body = sys.stdin.read()
    if not body.strip():
        print("ERROR: refusing to send an empty digest.", file=sys.stderr)
        sys.exit(1)

    payload = {
        "from": os.environ.get("EMAIL_FROM", DEFAULT_FROM),
        "to": [recipient],
        "subject": args.subject,
        "text": body,
    }
    resp = requests.post(
        SEND_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        data=json.dumps(payload),
        timeout=30,
    )

    if resp.status_code >= 400:
        print(
            f"ERROR: send failed ({resp.status_code}): {resp.text}",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"Sent to {recipient}: {args.subject}")


if __name__ == "__main__":
    main()
