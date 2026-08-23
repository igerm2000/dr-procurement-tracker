"""
Tracks which qualifying process references have already triggered an
instant email, and which ones are pending inclusion in today's digest.
Stored as a plain JSON file (seen.json) committed back into the repo
by the GitHub Actions workflow -- no database needed, and it's
human-readable if you ever want to peek at it.
"""
import json
import os
from datetime import date

STATE_FILE = "seen.json"


def load_state():
    if not os.path.exists(STATE_FILE):
        return {"alerted_refs": [], "digest_pending": [], "digest_date": None}
    with open(STATE_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2, default=str)


def filter_new(qualifying, state):
    """Returns only the processes not already alerted on."""
    seen = set(state["alerted_refs"])
    return [p for p in qualifying if p["referencia"] not in seen]


def record_alerted(new_matches, state, excluded_today=0):
    today = str(date.today())
    if state.get("digest_date") != today:
        # New day -- digest.py will have already flushed pending items
        # before this runs, but reset defensively.
        state["digest_date"] = today
        state["excluded_count_today"] = 0
    state["excluded_count_today"] = state.get("excluded_count_today", 0) + excluded_today
    for p in new_matches:
        state["alerted_refs"].append(p["referencia"])
        state["digest_pending"].append({
            "referencia": p["referencia"],  # kept for traceability in the digest
            "descripcion": p["descripcion"],
            "institucion": p["institucion"],
            "matched_keyword": p["matched_keyword"],
            "fecha_oferta": str(p["fecha_oferta"]),
        })
    # Keep alerted_refs from growing forever -- 90 days is plenty
    # since the portal itself won't show anything nearly that old.
    state["alerted_refs"] = state["alerted_refs"][-5000:]
    return state
