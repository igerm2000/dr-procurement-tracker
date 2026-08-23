"""
Entry point run once daily by GitHub Actions (end of business day).
Sends the digest summarizing everything alerted on today, then clears
the pending list for tomorrow.
"""
from state import load_state, save_state
from emails import digest_email
from mailer import send_email


def main():
    state = load_state()
    pending = state.get("digest_pending", [])
    excluded_count = state.get("excluded_count_today", 0)

    subject, html = digest_email(pending, excluded_count)
    send_email(subject, html)
    print(f"Sent digest with {len(pending)} item(s).")

    state["digest_pending"] = []
    state["excluded_count_today"] = 0
    save_state(state)


if __name__ == "__main__":
    main()
