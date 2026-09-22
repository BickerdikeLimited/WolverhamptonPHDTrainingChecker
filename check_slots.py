import os
import smtplib
import sys
from email.mime.text import MIMEText

import requests

URL = "https://capublic.worcestershire.gov.uk/LearnTaxi/AllSlotsBooked.aspx"
NO_SLOTS_TEXT = "no available sessions"

SMTP_HOST = os.environ["SMTP_HOST"]
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ["SMTP_USER"]
SMTP_PASS = os.environ["SMTP_PASS"]
NOTIFY_TO = os.environ["NOTIFY_TO"]


def slots_available() -> bool:
    resp = requests.get(URL, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    page_text = resp.text.lower()
    # Page says "no available sessions" when full. If that phrase is gone,
    # something has changed - most likely slots have appeared.
    return NO_SLOTS_TEXT not in page_text


def send_email():
    msg = MIMEText(
        f"Slots may now be available (or the page changed):\n\n{URL}"
    )
    msg["Subject"] = "Taxi course: slots may be available!"
    msg["From"] = SMTP_USER
    msg["To"] = NOTIFY_TO

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, [NOTIFY_TO], msg.as_string())


def main():
    try:
        available = slots_available()
    except Exception as e:
        print(f"Check failed: {e}", file=sys.stderr)
        sys.exit(1)

    if available:
        print("Slots available (or page changed) - sending email.")
        send_email()
    else:
        print("Still fully booked. No email sent.")


if __name__ == "__main__":
    main()
