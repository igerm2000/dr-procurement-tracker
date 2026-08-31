"""
Tracks:
- alerted_refs: every process reference ever reported (prevents the
  same still-open process being caught again on a later run)
- pending: processes found since the last digest email was sent, not
  yet emailed
- excluded_today: running count of matched-but-filtered processes
  since the last digest, for the footer note

Plain JSON file (seen.json), committed back to the repo after every
run by the single workflow.
"""
import json
import os

STATE_FILE = "seen.json"


def load_state():
    if not os.path.exists(STATE_FILE):
        return {"alerted_refs": [], "pending": [], "excluded_today": 0}
    with open(STATE_FILE, encoding="utf-8") as f:
        state = json.load(f)
    state.setdefault("alerted_refs", [])
    state.setdefault("pending", [])
    state.setdefault("excluded_today", 0)
    return state


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def filter_new(qualifying, state):
    """Returns only the processes not already reported in a previous run."""
    seen = set(state.get("alerted_refs", []))
    return [p for p in qualifying if p["referencia"] not in seen]
