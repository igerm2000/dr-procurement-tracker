"""
Fetches the live contract-notice list from comprasdominicana.gob.do and
parses it into structured rows.

The portal renders this page server-side as plain HTML (confirmed by
inspecting a live fetch on 2026-08-21) -- no JavaScript rendering is
required, so a plain HTTP request + BeautifulSoup parse is enough.
No browser automation (Playwright/Selenium) needed, which keeps the
GitHub Actions runner fast and avoids the flakiness that comes with
headless browsers.
"""
import re
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


def fetch_html(url):
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.text


def parse_rows(html):
    """
    Parses the contract-notice table into a list of dicts.

    Column order on the portal (confirmed 2026-08-21):
    Pais | Unidad de Compras | Referencia | Descripcion | Fase actual |
    Fecha de publicacion | Fecha de presentacion de ofertas |
    Total estimado | Estado | Detalle

    Parsing is defensive: rows with an unexpected number of cells are
    skipped rather than crashing the whole run, since a portal layout
    tweak should degrade gracefully (fewer alerts) rather than break
    the scheduled job entirely.
    """
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    for tr in soup.find_all("tr"):
        cells = tr.find_all("td")
        if len(cells) < 9:
            continue
        texts = [c.get_text(strip=True) for c in cells]
        # First real data column should be the country code "DO"
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
