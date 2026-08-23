"""
Entry point run every few hours by GitHub Actions.
Fetches current processes, matches/filters them, sends an instant
email for each NEW qualifying process, and records them for later
inclusion in the daily digest.
"""
import sys
import yaml

from scraper import get_current_processes
from match import evaluate
from state import load_state, save_state, filter_new, record_alerted
from emails import instant_email
from mailer import send_email


def main():
    with open("config.yaml", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    processes = get_current_processes(cfg["source_url"])
    print(f"Fetched {len(processes)} processes from the portal.")

    matches = evaluate(
        processes,
        keywords=cfg["keywords"],
        required_status=cfg["required_status"],
        min_hours=cfg["min_hours_window"],
    )
    qualifying = [m for m in matches if m["qualifies"]]
    print(f"{len(matches)} matched keywords, {len(qualifying)} passed all filters.")

    state = load_state()
    new_matches = filter_new(qualifying, state)
    print(f"{len(new_matches)} are new (not previously alerted).")

    for p in new_matches:
        p["source_url"] = cfg["source_url"]
        subject, html = instant_email(p)
        try:
            send_email(subject, html)
            print(f"Sent alert: {p['referencia']}")
        except Exception as e:
            print(f"FAILED to send alert for {p['referencia']}: {e}", file=sys.stderr)
            continue  # don't mark as alerted if the send failed

    excluded_today = len(matches) - len(qualifying)
    state = record_alerted(new_matches, state, excluded_today=excluded_today)
    save_state(state)


if __name__ == "__main__":
    main()
