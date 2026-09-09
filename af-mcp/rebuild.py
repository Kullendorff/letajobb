#!/usr/bin/env python3
"""Engångsmigration + reparation efter incidenten 2026-07-09.

pipeline.html innehåller trasiga kort (saknade </a>, pilar, taggblock) från
recovery-skriptet, plus 15 lösa scan-sektioner. Detta skript:
1. Hittar alla jobbkort oavsett skick, extraherar fälten
2. Genererar om varje kort enligt kortmallen i CLAUDE.md
3. Placerar korten i rätt sektion utifrån klass
4. Tar bort scan-sektionerna, synkar räknarna, verifierar, skriver säkert

Kör med --dry-run först.
"""

import re
import sys
from pathlib import Path

# Windows cp1252-konsolen kraschar annars på ✅/⚠️-tecken.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).parent))
from pipeline_lib import backup_pipeline, count_jobs, safe_write, sync_counters, verify_pipeline

ROOT = Path(__file__).parent.parent
PIPELINE = ROOT / "pipeline.html"
PORTALS_YML = ROOT / "career-ops" / "portals.yml"


def _default_city() -> str:
    """Ort att sätta på 'gbg'-taggade kort som saknar text (läses från portals.yml)."""
    if PORTALS_YML.exists():
        try:
            import yaml
            config = yaml.safe_load(PORTALS_YML.read_text(encoding="utf-8")) or {}
            city = (config.get("platsbanken") or {}).get("default_city")
            if city:
                return city
        except Exception:
            pass
    return "Göteborg"


CARD_START = re.compile(r'<a href="([^"]+)" target="_blank" class="(job[^"]*)"\s+data-tags="([^"]*)"')
BOUNDARIES = ["</ul>", "<!-- ", '<div class="section-label"', "<footer", "<script", "</body>"]

TAG_LABELS = {
    "tech": ("tag-tech", "Tech"), "komm": ("tag-komm", "Komm"),
    "gbg": ("tag-gbg", _default_city()), "remote": ("tag-remote", "Remote"),
    "new": ("tag-new", "NY"),
}


def extract_cards(html: str) -> list[dict]:
    starts = list(CARD_START.finditer(html))
    cards = []
    for i, m in enumerate(starts):
        end = starts[i + 1].start() if i + 1 < len(starts) else len(html)
        seg = html[m.start():end]
        # klipp vid närmaste strukturgräns
        cut = min((p for p in (seg.find(b, 1) for b in BOUNDARIES) if p != -1), default=len(seg))
        seg = seg[:cut]

        title = re.search(r'<div class="job-title">(.*?)</div>', seg, re.DOTALL)
        company = re.search(r'<div class="job-company">(.*?)</div>', seg, re.DOTALL)
        report = re.search(r'<a href="(reports/[^"]+)"', seg)
        tags = re.findall(r'<span class="tag [^"]*">[^<]*</span>', seg)
        cards.append({
            "href": m.group(1), "cls": m.group(2), "data_tags": m.group(3).strip(),
            "title": title.group(1).strip() if title else "OKÄND TITEL",
            "company": company.group(1).strip() if company else "",
            "report": report.group(1) if report else None,
            "tags": tags,
        })
    return cards


def synth_tags(card: dict) -> list[str]:
    """Bygger taggblock från data-tags om kortet saknar ett."""
    tags = []
    cls = card["cls"]
    if cls == "job applied":
        tags.append('<span class="tag tag-applied">ANSÖKT ✓</span>')
    elif cls == "job done":
        tags.append('<span class="tag tag-done">UTVÄRDERAD</span>')
    elif cls == "job ej":
        tags.append('<span class="tag tag-ej">EJ AKTUELL</span>')
    dt = card["data_tags"].split()
    for key in ("tech", "komm", "gbg", "remote"):
        if key in dt:
            c, label = TAG_LABELS[key]
            tags.append(f'<span class="tag {c}">{label}</span>')
    if cls == "job" and "new" in dt:
        c, label = TAG_LABELS["new"]
        tags.insert(0, f'<span class="tag {c}">{label}</span>')
    return tags


def render_card(card: dict) -> str:
    tags = card["tags"] or synth_tags(card)
    tags_html = "\n".join(f"      {t}" for t in tags)
    report_html = (
        f'\n    <a href="{card["report"]}" class="report-link" '
        f'onclick="event.stopPropagation()">📋 Rapport</a>'
        if card["report"] else ""
    )
    return (
        f'<a href="{card["href"]}" target="_blank" class="{card["cls"]}" data-tags="{card["data_tags"]}">\n'
        f'    <div class="job-info">\n'
        f'      <div class="job-title">{card["title"]}</div>\n'
        f'      <div class="job-company">{card["company"]}</div>\n'
        f'    </div>\n'
        f'    <div class="tags">\n'
        f'{tags_html}\n'
        f'    </div>{report_html}\n'
        f'    <span class="arrow">→</span>\n'
        f'  </a>'
    )


def replace_ul(html: str, marker: str, rendered: list[str]) -> str:
    idx = html.find(marker)
    if idx == -1:
        raise RuntimeError(f"Marker saknas: {marker}")
    ul_start = html.find('<ul class="job-list">', idx)
    ul_end = html.find("</ul>", ul_start)
    if ul_start == -1 or ul_end == -1:
        raise RuntimeError(f"Hittar inte <ul> efter {marker}")
    ul_open_end = ul_start + len('<ul class="job-list">')
    body = "\n" + "\n".join("  " + c for c in rendered) + "\n"
    return html[:ul_open_end] + body + html[ul_end:]


def main(dry_run: bool) -> None:
    html = PIPELINE.read_text(encoding="utf-8")
    print(f"Före: {count_jobs(html)}")

    cards, seen = [], set()
    for card in extract_cards(html):
        if card["href"] in seen:
            print(f"  dubblett hoppas över: {card['href']}")
            continue
        seen.add(card["href"])
        cards.append(card)

    by_class = {"job applied": [], "job done": [], "job ej": [], "job": []}
    for card in cards:
        by_class[card["cls"]].append(render_card(card))
    print(f"Insamlat: {len(cards)} kort — {len(by_class['job applied'])} ansökta, "
          f"{len(by_class['job done'])} utvärderade, {len(by_class['job'])} ovärderade, "
          f"{len(by_class['job ej'])} ej aktuella")
    missing_title = [c["href"] for c in cards if c["title"] == "OKÄND TITEL"]
    if missing_title:
        print(f"  ⚠️ {len(missing_title)} kort utan titel: {missing_title[:5]}")

    # Klipp bort scan-sektionerna (korten är redan insamlade)
    first_scan = html.find("<!-- NYA JOBB")
    if first_scan != -1:
        body_end = html.find("</body>", first_scan)
        if body_end == -1:
            raise RuntimeError("</body> saknas efter scan-sektionerna — avbryter.")
        html = html[:first_scan].rstrip() + "\n\n" + html[body_end:]

    html = replace_ul(html, "<!-- ANSÖKTA -->", by_class["job applied"])
    html = replace_ul(html, "<!-- UTVÄRDERADE -->", by_class["job done"])
    html = replace_ul(html, "<!-- OVÄRDERADE -->", by_class["job"])
    html = replace_ul(html, "<!-- EJ AKTUELLA -->", by_class["job ej"])

    html = sync_counters(html)
    after = count_jobs(html)
    print(f"Efter: {after}")
    errors = verify_pipeline(html, expect_total=len(cards))
    if after["total"] != len(cards):
        errors.append(f"kort tappades: {after['total']} != {len(cards)}")
    if "<!-- NYA JOBB" in html:
        errors.append("scan-sektioner finns kvar")
    if errors:
        print("FEL — skriver inte:\n  - " + "\n  - ".join(errors))
        sys.exit(1)

    if dry_run:
        print("[dry-run] Allt OK — inget skrivet.")
        return

    bak = backup_pipeline(PIPELINE)
    print(f"Backup: {bak.name}")
    safe_write(PIPELINE, html, expect_total=len(cards))
    print(f"✅ pipeline.html ombyggd och reparerad: {after['total']} jobb, 0 scan-sektioner")


if __name__ == "__main__":
    main("--dry-run" in sys.argv)
