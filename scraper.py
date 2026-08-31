"""
Fetches the live contract-notice list from comprasdominicana.gob.do and
parses it into structured rows.

The portal renders this page server-side as plain HTML -- no JavaScript
rendering required, so a plain HTTP request + BeautifulSoup parse is
enough. Checked every 15 minutes (see daily_run.py / workflow), which
is a large safety margin under the ~2.5 hours of activity one page
actually holds -- confirmed by comparing timestamps on a live fetch.
"""
import re
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/124.0 Safari/537.36"
}


def parse_dt(raw):
    """'21/08/2026 15:35 (UTC -4 horas)' -> datetime"""
    m = re.match(r"(\d{2})/(\d{2})/(\d{4})\s+(\d{2}):(\d{2})", raw.strip())
    if not m:
        return None
    day, month, year, hour, minute = map(int, m.groups())
    return datetime(year, month, day, hour, minute)


def fetch_html(url, attempts=3, backoff_seconds=15):
    """Retries a few times on timeout/connection errors before giving
    up, so one slow moment from the portal doesn't fail the run."""
    last_error = None
    for attempt in range(1, attempts + 1):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            return resp.text
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            last_error = e
            print(f"Attempt {attempt}/{attempts} failed ({e.__class__.__name__}); "
                  f"{'retrying' if attempt < attempts else 'giving up'}...")
            if attempt < attempts:
                time.sleep(backoff_seconds)
    raise last_error


def parse_rows(html):
    """
    Parses the contract-notice table into a list of dicts.

    Column order on the portal: Pais | Unidad de Compras | Referencia |
    Descripcion | Fase actual | Fecha de publicacion | Fecha de
    presentacion de ofertas | Total estimado | Estado | Detalle

    Parsing is defensive: rows with an unexpected number of cells, or
    unparseable dates, are skipped rather than crashing the whole run.
    """
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    for tr in soup.find_all("tr"):
        cells = tr.find_all("td")
        if len(cells) < 9:
            continue
        texts = [c.get_text(strip=True) for c in cells]
        if texts[0] != "DO":
            continue
        fecha_pub = parse_dt(texts[5])
        fecha_oferta = parse_dt(texts[6])
        if not fecha_pub or not fecha_oferta:
            continue
        rows.append({
            "institucion": texts[1],
            "referencia": texts[2],
            "descripcion": texts[3],
            "fase": texts[4],
            "fecha_publicacion": fecha_pub,
            "fecha_oferta": fecha_oferta,
            "total_estimado": texts[7],
            "estado": texts[8],
        })
    return rows


def get_current_processes(url):
    html = fetch_html(url)
    return parse_rows(html)


if __name__ == "__main__":
    import yaml
    with open("config.yaml", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    processes = get_current_processes(cfg["source_url"])
    print(f"Fetched {len(processes)} processes from the live portal.")
    for p in processes[:5]:
        print(f"- {p['referencia']}: {p['descripcion'][:60]}")
