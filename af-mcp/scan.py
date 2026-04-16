#!/usr/bin/env python3
"""Platsbanken-scanner — söker nya jobb och uppdaterar pipeline-filer.

Användning:
    python af-mcp/scan.py              # senaste 7 dagarna
    python af-mcp/scan.py --days 14    # senaste 14 dagarna
    python af-mcp/scan.py --dry-run    # visa resultat utan att skriva filer
    python af-mcp/scan.py --no-filter  # skippa titelfiltrering (debugging)
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import re
import sys
from datetime import date
from pathlib import Path

import httpx
import yaml

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
JOBSEARCH_BASE = "https://jobsearch.api.jobtechdev.se"
GÖTEBORG_MUNICIPALITY = "1480"
TODAY = date.today().isoformat()

SCRIPT_DIR = Path(__file__).parent
ROOT = SCRIPT_DIR.parent
CAREER_OPS = ROOT / "career-ops"
SCAN_HISTORY = CAREER_OPS / "data" / "scan-history.tsv"
PIPELINE_MD = CAREER_OPS / "data" / "pipeline.md"
PIPELINE_HTML = ROOT / "pipeline.html"
PORTALS_YML = CAREER_OPS / "portals.yml"

# Sökningar att köra: (q, municipality, remote)
# municipality="" = Sverige-brett
SEARCHES: list[tuple[str, str, bool | None]] = [
    ("IT-support", GÖTEBORG_MUNICIPALITY, None),
    ("supporttekniker", GÖTEBORG_MUNICIPALITY, None),
    ("helpdesk", GÖTEBORG_MUNICIPALITY, None),
    ("servicedesk", GÖTEBORG_MUNICIPALITY, None),
    ("IT-tekniker", GÖTEBORG_MUNICIPALITY, None),
    ("2nd line", GÖTEBORG_MUNICIPALITY, None),
    ("applikationssupport", GÖTEBORG_MUNICIPALITY, None),
    ("Python developer", GÖTEBORG_MUNICIPALITY, None),
    ("kommunikatör", GÖTEBORG_MUNICIPALITY, None),
    ("webbredaktör", GÖTEBORG_MUNICIPALITY, None),
    ("technical support", GÖTEBORG_MUNICIPALITY, None),
    ("technical support specialist", "", True),
    ("support engineer", "", True),
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _tags_for_query(q: str, remote: bool | None) -> tuple[str, str]:
    """Returnerar (data-tags sträng, kategori-label) baserat på sökning."""
    q_low = q.lower()
    if any(w in q_low for w in ("kommunikatör", "webbredaktör", "kommunik", "redaktör")):
        tags, cat = "komm gbg new", "Kommunikation"
    elif "python" in q_low:
        tags, cat = "tech gbg new", "Python"
    else:
        tags, cat = "tech gbg new", "IT Support"

    if remote:
        tags = tags.replace("gbg", "remote")
    return tags, cat


async def _fetch(path: str, params: dict) -> dict:
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(
            f"{JOBSEARCH_BASE}{path}",
            params=params,
            headers={"Accept": "application/json"},
        )
        r.raise_for_status()
        return r.json()


def _load_title_filters() -> tuple[list[re.Pattern], list[re.Pattern]]:
    """Laddar positiva och negativa titelfilter från portals.yml som regex-mönster."""
    if not PORTALS_YML.exists():
        return [], []
    with open(PORTALS_YML, encoding="utf-8") as f:
        config = yaml.safe_load(f)
    tf = config.get("title_filter", {})

    def _compile(terms: list[str]) -> list[re.Pattern]:
        patterns = []
        for term in terms:
            t = term.strip()
            # Word boundaries förhindrar att "PR" matchar "primärvården", "AI" matchar "mail" etc.
            patterns.append(re.compile(r"\b" + re.escape(t) + r"\b", re.IGNORECASE))
        return patterns

    return _compile(tf.get("positive", [])), _compile(tf.get("negative", []))


def _passes_title_filter(
    headline: str,
    positive: list[re.Pattern],
    negative: list[re.Pattern],
) -> bool:
    """True om headline matchar minst ett positivt mönster och inget negativt."""
    if not positive and not negative:
        return True
    if positive and not any(p.search(headline) for p in positive):
        return False
    if any(n.search(headline) for n in negative):
        return False
    return True


def _load_known_ids() -> set[str]:
    """Laddar alla Platsbanken-IDs som redan finns i scan-history och pipeline.html."""
    known: set[str] = set()

    if SCAN_HISTORY.exists():
        with open(SCAN_HISTORY, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                m = re.search(r"/annonser/(\d+)", row.get("url", ""))
                if m:
                    known.add(m.group(1))

    if PIPELINE_HTML.exists():
        for m in re.finditer(r"/platsbanken/annonser/(\d+)", PIPELINE_HTML.read_text(encoding="utf-8")):
            known.add(m.group(1))

    return known


async def _search(q: str, municipality: str, remote: bool | None, published_after: str, limit: int = 50) -> list[dict]:
    params: dict = {
        "q": q,
        "limit": limit,
        "sort": "pubdate-desc",
        "published-after": published_after,
    }
    if municipality:
        params["municipality"] = municipality
    if remote:
        params["remote"] = "true"

    try:
        data = await _fetch("/search", params)
        return data.get("hits", [])
    except Exception as e:
        print(f"  ⚠️  Sökning '{q}' misslyckades: {e}", file=sys.stderr)
        return []


# ---------------------------------------------------------------------------
# HTML-generering
# ---------------------------------------------------------------------------
def _html_entry(ad: dict, data_tags: str, cat_label: str) -> str:
    headline = ad.get("headline", "Utan rubrik")
    employer = ad.get("employer", {}).get("name", "Okänd")
    wp = ad.get("workplace_address", {}) or {}
    city = wp.get("city", "") or wp.get("municipality", "")
    ad_id = ad.get("id", "")
    url = f"https://arbetsformedlingen.se/platsbanken/annonser/{ad_id}"

    deadline = ad.get("application_deadline", "")
    if deadline and "T" in deadline:
        deadline = deadline.split("T")[0]

    deadline_html = ""
    if deadline:
        try:
            dl = date.fromisoformat(deadline)
            days_left = (dl - date.today()).days
            if days_left <= 14:
                deadline_html = (
                    f' <span style="color:#f87171;font-size:0.75rem;margin-left:0.5rem">'
                    f'⚠️ Deadline {deadline}</span>'
                )
        except ValueError:
            pass

    is_remote = "remote" in data_tags
    loc_tag = (
        '<span class="tag tag-remote">Remote</span>'
        if is_remote
        else '<span class="tag tag-gbg">Göteborg</span>'
    )
    cat_class = "tag-komm" if "komm" in data_tags else "tag-tech"
    description = f"{employer} — {city}" if city else employer

    return (
        f'  <a href="{url}" target="_blank" class="job" data-tags="{data_tags}">\n'
        f'    <div class="job-info">\n'
        f'      <div class="job-title">{headline}{deadline_html}</div>\n'
        f'      <div class="job-company">{description}</div>\n'
        f'    </div>\n'
        f'    <div class="tags">\n'
        f'      <span class="tag tag-new">NY</span>\n'
        f'      <span class="tag {cat_class}">{cat_label}</span>\n'
        f'      {loc_tag}\n'
        f'    </div>\n'
        f'    <span class="arrow">→</span>\n'
        f'  </a>\n'
    )


def _pipeline_md_entry(ad: dict) -> str:
    headline = ad.get("headline", "Utan rubrik")
    employer = ad.get("employer", {}).get("name", "Okänd")
    wp = ad.get("workplace_address", {}) or {}
    city = wp.get("city", "") or wp.get("municipality", "Göteborg")
    ad_id = ad.get("id", "")
    url = f"https://arbetsformedlingen.se/platsbanken/annonser/{ad_id}"
    return f"- [ ] {url} | {employer} | {headline} ({city})"


# ---------------------------------------------------------------------------
# Pipeline HTML update
# ---------------------------------------------------------------------------
def _update_pipeline_html(html: str, new_entries_html: str, n_new: int) -> str:
    section_comment = f"<!-- NYA JOBB {TODAY}"

    # Om en sektion för idag redan finns — lägg till i den
    idx = html.find(section_comment)
    if idx != -1:
        ul_start = html.find('<ul class="job-list">', idx)
        if ul_start != -1:
            ul_end = html.find("</ul>", ul_start)
            if ul_end != -1:
                return html[:ul_end] + new_entries_html + html[ul_end:]

    # Annars: skapa ny sektion, infoga före första NYA/HITTADE-sektionen
    new_section = (
        f"\n{section_comment} — Platsbanken-scan, {n_new} nya -->\n"
        f'<div class="section-label">🔍 Platsbanken-scan — {TODAY} ({n_new} nya)</div>\n'
        f'<ul class="job-list">\n'
        f"{new_entries_html}"
        f"</ul>\n"
    )

    m = re.search(r"\n<!-- (NYA JOBB|HITTADE)", html)
    if m:
        return html[: m.start()] + new_section + html[m.start() :]

    # Fallback: före </body>
    return html.replace("</body>", new_section + "</body>")


def _update_senast_skannad(html: str) -> str:
    return re.sub(r"Senast skannad \d{4}-\d{2}-\d{2}", f"Senast skannad {TODAY}", html)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
async def main(days: int, dry_run: bool, no_filter: bool) -> None:
    from datetime import timedelta
    since = date.today() - timedelta(days=days)
    published_after = f"{since.isoformat()}T00:00:00"

    print(f"🔍 Platsbanken-scan — {TODAY} (senaste {days} dagarna)")
    if dry_run:
        print("  [DRY RUN — skriver inga filer]")

    # Ladda titelfilter
    if no_filter:
        positive_filters: list[re.Pattern] = []
        negative_filters: list[re.Pattern] = []
        print("  [--no-filter: titelfiltrering avstängd]")
    else:
        positive_filters, negative_filters = _load_title_filters()
        if positive_filters:
            print(f"  Titelfilter: {len(positive_filters)} positiva, {len(negative_filters)} negativa termer")
    print()

    known_ids = _load_known_ids()
    print(f"  Kända Platsbanken-annonser: {len(known_ids)}\n")

    # Kör alla sökningar
    all_hits: dict[str, dict] = {}          # ad_id -> ad
    id_to_search: dict[str, tuple[str, bool | None]] = {}

    for q, municipality, remote in SEARCHES:
        label_loc = " (remote)" if remote else " (Gbg)" if municipality else " (Sverige)"
        print(f"  🔎 '{q}'{label_loc}...")
        hits = await _search(q, municipality, remote, published_after)
        new_here = 0
        filtered_out = 0
        for ad in hits:
            ad_id = str(ad.get("id", ""))
            if not ad_id or ad_id in known_ids or ad_id in all_hits:
                continue
            headline = ad.get("headline", "")
            if not _passes_title_filter(headline, positive_filters, negative_filters):
                filtered_out += 1
                continue
            all_hits[ad_id] = ad
            id_to_search[ad_id] = (q, remote)
            new_here += 1
        filter_note = f", {filtered_out} filtrerade" if filtered_out else ""
        print(f"    → {len(hits)} träffar, {new_here} nya{filter_note}")

    if not all_hits:
        print("\n✅ Inga nya jobb hittades.")
        return

    n = len(all_hits)
    print(f"\n🆕 {n} nya jobb:\n")

    for ad_id, ad in all_hits.items():
        headline = ad.get("headline", "")
        employer = ad.get("employer", {}).get("name", "")
        wp = ad.get("workplace_address", {}) or {}
        city = wp.get("city", "") or wp.get("municipality", "")
        deadline = ad.get("application_deadline", "")
        if deadline and "T" in deadline:
            deadline = deadline.split("T")[0]
        print(f"  • {headline}")
        print(f"    {employer} — {city}  |  Deadline: {deadline or '—'}")
        print(f"    https://arbetsformedlingen.se/platsbanken/annonser/{ad_id}")
        print()

    if dry_run:
        return

    # --- Uppdatera scan-history.tsv ---
    with open(SCAN_HISTORY, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["url", "first_seen", "portal", "title", "company", "status"],
            delimiter="\t",
        )
        for ad_id, ad in all_hits.items():
            writer.writerow({
                "url": f"https://arbetsformedlingen.se/platsbanken/annonser/{ad_id}",
                "first_seen": TODAY,
                "portal": "Platsbanken",
                "title": ad.get("headline", ""),
                "company": ad.get("employer", {}).get("name", ""),
                "status": "added",
            })
    print(f"✅ scan-history.tsv — {n} rader tillagda")

    # --- Uppdatera pipeline.md ---
    md_lines = [_pipeline_md_entry(ad) for ad in all_hits.values()]
    md = PIPELINE_MD.read_text(encoding="utf-8")
    marker = "## Pendientes\n"
    idx = md.find(marker)
    if idx != -1:
        pos = idx + len(marker)
        md = md[:pos] + "\n".join(md_lines) + "\n" + md[pos:]
    else:
        md += "\n" + "\n".join(md_lines) + "\n"
    PIPELINE_MD.write_text(md, encoding="utf-8")
    print(f"✅ pipeline.md — {n} jobb tillagda")

    # --- Uppdatera pipeline.html ---
    html_entries = "".join(
        _html_entry(ad, *_tags_for_query(*id_to_search[ad_id]))
        for ad_id, ad in all_hits.items()
    )
    html = PIPELINE_HTML.read_text(encoding="utf-8")
    html = _update_pipeline_html(html, html_entries, n)
    html = _update_senast_skannad(html)
    PIPELINE_HTML.write_text(html, encoding="utf-8")
    print(f"✅ pipeline.html — ny sektion tillagd")

    print(f"\n🎯 Kör karriärpipelinen: /career-ops pipeline  för att utvärdera jobben")


if __name__ == "__main__":
    # Sätt UTF-8 på stdout/stderr för att hantera svenska tecken i Windows-terminal
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="Scanna Platsbanken för nya jobb")
    parser.add_argument("--days", type=int, default=7, help="Sök jobb publicerade de senaste N dagarna (default: 7)")
    parser.add_argument("--dry-run", action="store_true", help="Visa resultat utan att skriva filer")
    parser.add_argument("--no-filter", action="store_true", help="Skippa titelfiltrering (debugging)")
    args = parser.parse_args()
    asyncio.run(main(args.days, args.dry_run, args.no_filter))
