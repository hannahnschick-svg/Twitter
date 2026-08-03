#!/usr/bin/env python3
"""Send a plain-text email via Gmail SMTP using an App Password.

Usage:
    python3 scripts/send_email.py --subject "Some subject" < body.txt

Reads the email body from stdin. Requires these environment variables:
    GMAIL_ADDRESS      -- the Gmail address to send from (and log in as)
    GMAIL_APP_PASSWORD -- a Google App Password for that account
                          (Google Account -> Security -> 2-Step Verification
                          -> App Passwords; requires 2-Step Verification on)
    EMAIL_TO           -- optional recipient; defaults to GMAIL_ADDRESS
"""
import argparse
import os
import smtplib
import sys
from email.mime.text import MIMEText


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--subject", required=True)
    args = parser.parse_args()

    sender = os.environ.get("GMAIL_ADDRESS")
    app_password = os.environ.get("GMAIL_APP_PASSWORD")
    if not sender or not app_password:
        print(
            "ERROR: GMAIL_ADDRESS and/or GMAIL_APP_PASSWORD is not set. "
            "See README.md for how to generate a Google App Password and "
            "configure it.",
            file=sys.stderr,
        )
        sys.exit(1)

    recipient = os.environ.get("EMAIL_TO", sender)
    body = sys.stdin.read()

    msg = MIMEText(body, "plain")
    msg["Subject"] = args.subject
    msg["From"] = sender
    msg["To"] = recipient

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, app_password)
        server.sendmail(sender, [recipient], msg.as_string())

    print(f"Sent to {recipient}: {args.subject}")


if __name__ == "__main__":
    main()
