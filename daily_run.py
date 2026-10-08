"""
Runs every 15 minutes to keep up with the portal, but only SENDS an
email once a day, at the first run after 6:00 PM Santo Domingo time
(UTC-4 fixed, no DST). All other runs just accumulate.

15 minutes is a large safety margin under how much activity the
portal's first results page actually holds (confirmed ~2.5 hours of
national activity per page via a live fetch on 2026-08-31) -- so
checking that often keeps results from scrolling off unseen without
needing to page through the full site.

Still one workflow/script, not two -- avoids the git-push races that
caused the original missed-alert problem.
"""
import sys
import traceback
from datetime import datetime, timezone
import yaml
from zoneinfo import ZoneInfo

from scraper import get_current_processes
from match import evaluate
from state import load_state, save_state, filter_new
from emails import digest_email
from mailer import send_email

LOCAL_TZ = ZoneInfo("America/Santo_Domingo")
DIGEST_HOUR_LOCAL = 18


def format_dt(dt):
    return dt.strftime("%d/%m %H:%M")


def is_digest_run(now_utc):
    # Any run at/after 6:00 PM Santo Domingo time may send. The
    # already-sent-today flag guarantees only one does, so a delayed or
    # dropped GitHub trigger still delivers the digest that evening.
    return now_utc.astimezone(LOCAL_TZ).hour >= DIGEST_HOUR_LOCAL


def run():
    with open("config.yaml", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    try:
        processes = get_current_processes(cfg["source_url"])
    except Exception as e:
        # Portal down/blocked this run: don't lose the day. Carry on with
        # nothing new so a digest-eligible run still sends what's pending.
        print(f"WARNING: portal fetch failed ({e.__class__.__name__}: {e}); continuing with 0 processes.")
        processes = []
    print(f"Fetched {len(processes)} processes from the portal.")

    matches = evaluate(
        processes,
        keywords=cfg["keywords"],
        required_status=cfg["required_status"],
        min_hours=cfg["min_hours_window"],
    )
    qualifying = [m for m in matches if m["qualifies"]]
    excluded_now = len(matches) - len(qualifying)
    print(f"{len(matches)} matched keywords, {len(qualifying)} passed all filters.")

    state = load_state()
    new_matches = filter_new(qualifying, state)
    print(f"{len(new_matches)} are new since the last run.")

    seen = set(state.get("alerted_refs", []))
    pending = state.get("pending", [])
    excluded_today = state.get("excluded_today", 0) + excluded_now
    for p in new_matches:
        seen.add(p["referencia"])
        pending.append({
            "referencia": p["referencia"],
            "descripcion": p["descripcion"],
            "institucion": p["institucion"],
            "matched_keyword": p["matched_keyword"],
            "fecha_oferta": format_dt(p["fecha_oferta"]),
            "total_estimado": p["total_estimado"],
        })
    state["alerted_refs"] = list(seen)[-5000:]
    state["pending"] = pending
    state["excluded_today"] = excluded_today

    now_utc = datetime.now(timezone.utc)
    today_local = now_utc.astimezone(LOCAL_TZ).strftime("%Y-%m-%d")
    already_sent_today = state.get("last_digest_date") == today_local

    if is_digest_run(now_utc) and not already_sent_today:
        subject, html = digest_email(pending, excluded_today)
        send_email(subject, html)
        print(f"Sent daily digest: {subject}")
        state["pending"] = []
        state["excluded_today"] = 0
        state["last_digest_date"] = today_local
    else:
        print("Not the digest run (or already sent today) -- accumulating only.")

    save_state(state)


def _sent_today(now_utc):
    try:
        return load_state().get("last_digest_date") == now_utc.astimezone(LOCAL_TZ).strftime("%Y-%m-%d")
    except Exception:
        return False


def main():
    try:
        run()
    except Exception:
        print("Run failed:", file=sys.stderr)
        traceback.print_exc()
        now_utc = datetime.now(timezone.utc)
        if is_digest_run(now_utc) and not _sent_today(now_utc):
            try:
                send_email(
                    "Tracker: fallo en la revisión de hoy",
                    "<p>La revisión de hoy no pudo completarse a tiempo para "
                    "el resumen diario. Revisa el log de GitHub Actions para "
                    "más detalle.</p>",
                )
                print("Sent failure-notice email.")
            except Exception:
                print("Also failed to send the failure-notice email.", file=sys.stderr)
        raise


if __name__ == "__main__":
    main()
