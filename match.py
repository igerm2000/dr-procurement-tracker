"""
Keyword matching + status/noise filtering.
This is the exact logic validated against real live portal data in
the proof-of-concept step (it correctly caught a real sham-published
process during testing on 2026-08-21).
"""
import unicodedata
from datetime import timedelta


def strip_accents(s):
    return "".join(
        c for c in unicodedata.normalize("NFD", s)
        if unicodedata.category(c) != "Mn"
    )


def normalize(s):
    return strip_accents(s).lower()


def match_keywords(text, keywords):
    """Returns the first matching keyword, or None. OR logic, exact
    phrase match (not loose word scatter), case/accent-insensitive."""
    norm_text = normalize(text)
    for kw in keywords:
        if normalize(kw) in norm_text:
            return kw
    return None


def passes_status_filter(process, required_status):
    return process["estado"] == required_status


def passes_noise_filter(process, min_hours):
    window = process["fecha_oferta"] - process["fecha_publicacion"]
    return window >= timedelta(hours=min_hours), window


def evaluate(processes, keywords, required_status, min_hours):
    """Returns processes that matched a keyword, tagged with whether
    they qualify for an alert (both filters passed)."""
    results = []
    for p in processes:
        kw = match_keywords(p["descripcion"], keywords)
        if not kw:
            continue
        status_ok = passes_status_filter(p, required_status)
        noise_ok, window = passes_noise_filter(p, min_hours)
        results.append({
            **p,
            "matched_keyword": kw,
            "status_ok": status_ok,
            "noise_ok": noise_ok,
            "window": window,
            "qualifies": status_ok and noise_ok,
        })
    return results
