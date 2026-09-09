#!/usr/bin/env python3
"""Bootstrap för en ny installation — skapar de filer som behövs innan
af-mcp/scan.py, verify.py och /career-ops kan köras.

Idempotent: rör ALDRIG en fil som redan finns. Kör om det så ofta du vill.

Användning:
    python af-mcp/init.py            # skapar saknade filer
    python af-mcp/init.py --check    # visar bara vad som saknas/finns, skriver inget

Se ONBOARDING.md för hela flödet (det här skriptet är ett steg i det,
inte hela onboardingen — det fyller inga personuppgifter).
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from datetime import date
from pathlib import Path

# Windows cp1252-konsolen kraschar annars på ✅/📋/🔍-tecken (samma fix som
# behövs i scan.py/verify.py/rebuild.py).
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

SCRIPT_DIR = Path(__file__).parent
ROOT = SCRIPT_DIR.parent
CAREER_OPS = ROOT / "career-ops"

sys.path.insert(0, str(SCRIPT_DIR))
from pipeline_lib import SECTION_MARKERS, stamp_updated, sync_counters  # noqa: E402

TODAY = date.today().isoformat()


# ---------------------------------------------------------------------------
# pipeline.html — byggs ur pipeline.example.html, tömd på jobbkort
# ---------------------------------------------------------------------------
def _build_pipeline_html() -> str:
    example = ROOT / "pipeline.example.html"
    html = example.read_text(encoding="utf-8")

    html = html.replace(
        "<title>Jobbpipeline - Exempel</title>",
        "<title>Jobbpipeline</title>",
    )
    html = html.replace(
        '<div class="subtitle">Exempeldata - visar formatet, inte en riktig jobbsökning</div>',
        f'<div class="subtitle">Din pipeline - Senast uppdaterad {TODAY}</div>',
    )
    # Bort med demo-bannern (den pratar om pipeline.example.html specifikt).
    html = re.sub(r'\s*<div class="banner">.*?</div>\n', "\n", html, flags=re.DOTALL)

    # Töm varje sektions <ul class="job-list">...</ul> på jobbkort.
    html = re.sub(
        r'(<ul class="job-list">)(.*?)(</ul>)',
        lambda m: m.group(1) + "\n" + m.group(3),
        html,
        flags=re.DOTALL,
    )

    # Töm "Att söka NU"-tabellens rader (behåll <thead>).
    html = re.sub(r"(<tbody>)(.*?)(</tbody>)", r"\1\3", html, flags=re.DOTALL)

    # Footer: byt "Exempeldata." mot produktionsformatet så att
    # pipeline_lib.stamp_updated() känner igen och uppdaterar den i framtida körningar.
    html = html.replace(
        "career-ops pipeline - Exempeldata.",
        f"career-ops pipeline - Uppdaterad {TODAY}.",
    )

    html = sync_counters(html)  # räknar om till 0 överallt (0 jobbkort kvar)
    html = stamp_updated(html)
    return html


def _atomic_write_new(path: Path, html: str) -> None:
    """Skriver en HELT NY fil atomiskt.

    Använder INTE pipeline_lib.safe_write() här, med flit: safe_write()
    vägrar skriva om jobbantalet är 0 (skydd mot att av misstag tömma en
    befintlig pipeline — se INCIDENT_2026-07-09_pipeline_corruption.md).
    Det skyddet ska INTE gälla här: en helt ny pipeline.html HAR 0 kort,
    det är hela poängen. Vi gör ändå motsvarande strukturkoll minus
    nollkravet, plus samma tempfil->atomisk-ersättning-mönster.
    """
    if not html.rstrip().endswith("</html>"):
        raise RuntimeError("Bygget av pipeline.html gick fel: slutar inte med </html>")
    for marker in SECTION_MARKERS:
        if html.count(marker) != 1:
            raise RuntimeError(
                f"Bygget av pipeline.html gick fel: {marker} saknas eller finns flera gånger"
            )
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(html, encoding="utf-8")
    if tmp.read_text(encoding="utf-8") != html:
        tmp.unlink()
        raise RuntimeError("Tempfilen matchade inte innehållet i minnet — avbryter.")
    os.replace(tmp, path)


PIPELINE_MD_TEMPLATE = """# Pipeline

## Pendientes

## Procesadas
"""

APPLICATIONS_MD_TEMPLATE = """# Applications Tracker

| # | Date | Company | Role | Score | Status | PDF | Report | Notes |
|---|------|---------|------|-------|--------|-----|--------|-------|
"""

SCAN_HISTORY_HEADER = "url\tfirst_seen\tportal\ttitle\tcompany\tstatus\n"

CLAUDE_LOCAL_TEMPLATE = """# CLAUDE.local.md - LOKAL FIL, ALDRIG TILL GIT

Denna fil är gitignorerad och får ALDRIG committas, pushas eller citeras i
publika dokument. Kolla `git status` innan du committar om du är osäker.

## Sekretess kring nuvarande/tidigare uppdragsgivare

[ANPASSA] Har du bindande sekretessregler (NDA, interna förhållanden som
aldrig får nämnas i ansökningar)? Skriv dem här, t.ex.:

- Vad får ALDRIG nämnas (kundnamn, projekt, interna beslut)?
- Vilken säker formulering använder du istället i CV/brev?
- Vad svarar du om du får frågan direkt i en intervju?

Om du inte har några sekretessregler kan den här sektionen lämnas tom eller
tas bort helt — filen behöver bara finnas om du faktiskt har något att skydda.

## Historik

- {today}: Skapad av af-mcp/init.py.
""".format(today=TODAY)


def _copy_if_missing(src: Path, dst: Path) -> str:
    if not src.exists():
        return f"HOPPAR ÖVER {dst.relative_to(ROOT)}: källan {src.relative_to(ROOT)} finns inte"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    return f"skapad (kopia av {src.relative_to(ROOT)})"


def _write_if_missing(dst: Path, content: str) -> str:
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(content, encoding="utf-8")
    return "skapad"


# ---------------------------------------------------------------------------
# Alla poster: (beskrivning, målsökväg, byggfunktion() -> None, skapar filen)
# ---------------------------------------------------------------------------
def _pipeline_html_action() -> str:
    example = ROOT / "pipeline.example.html"
    if not example.exists():
        return "HOPPAR ÖVER pipeline.html: pipeline.example.html saknas"
    _atomic_write_new(ROOT / "pipeline.html", _build_pipeline_html())
    return "skapad (tom, byggd ur pipeline.example.html)"


ITEMS: list[tuple[str, Path, "callable"]] = [
    ("pipeline.html", ROOT / "pipeline.html", _pipeline_html_action),
    (
        "career-ops/data/pipeline.md",
        CAREER_OPS / "data" / "pipeline.md",
        lambda: _write_if_missing(CAREER_OPS / "data" / "pipeline.md", PIPELINE_MD_TEMPLATE),
    ),
    (
        "career-ops/data/applications.md",
        CAREER_OPS / "data" / "applications.md",
        lambda: _write_if_missing(
            CAREER_OPS / "data" / "applications.md", APPLICATIONS_MD_TEMPLATE
        ),
    ),
    (
        "career-ops/data/scan-history.tsv",
        CAREER_OPS / "data" / "scan-history.tsv",
        lambda: _write_if_missing(
            CAREER_OPS / "data" / "scan-history.tsv", SCAN_HISTORY_HEADER
        ),
    ),
    (
        "career-ops/config/profile.yml",
        CAREER_OPS / "config" / "profile.yml",
        lambda: _copy_if_missing(
            CAREER_OPS / "config" / "profile.example.yml",
            CAREER_OPS / "config" / "profile.yml",
        ),
    ),
    (
        "career-ops/portals.yml",
        CAREER_OPS / "portals.yml",
        lambda: _copy_if_missing(
            CAREER_OPS / "templates" / "portals.svenska.example.yml",
            CAREER_OPS / "portals.yml",
        ),
    ),
    (
        "career-ops/modes/_profile.md",
        CAREER_OPS / "modes" / "_profile.md",
        lambda: _copy_if_missing(
            CAREER_OPS / "modes" / "_profile.template.md",
            CAREER_OPS / "modes" / "_profile.md",
        ),
    ),
    (
        "CLAUDE.local.md",
        ROOT / "CLAUDE.local.md",
        lambda: _write_if_missing(ROOT / "CLAUDE.local.md", CLAUDE_LOCAL_TEMPLATE),
    ),
]

DIRS = [ROOT / "reports", CAREER_OPS / "output", CAREER_OPS / "reports", CAREER_OPS / "jds"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="Visa bara vad som saknas/finns, skriv inget"
    )
    args = parser.parse_args()

    print("🔎 Kollar installationen...\n" if not args.check else "🔎 Statuskoll (--check, skriver inget)...\n")

    missing_after = []
    for label, path, action in ITEMS:
        if path.exists():
            print(f"  ✅ {label} — finns redan, rörs inte")
            continue
        if args.check:
            print(f"  ⬜ {label} — saknas")
            missing_after.append(label)
            continue
        try:
            result = action()
        except Exception as exc:  # noqa: BLE001 — vi vill rapportera, inte krascha halvvägs
            print(f"  ❌ {label} — FEL: {exc}")
            missing_after.append(label)
            continue
        print(f"  🆕 {label} — {result}")

    for d in DIRS:
        if d.exists():
            continue
        if args.check:
            print(f"  ⬜ {d.relative_to(ROOT)}/ — saknas")
            missing_after.append(str(d.relative_to(ROOT)))
            continue
        d.mkdir(parents=True, exist_ok=True)
        print(f"  🆕 {d.relative_to(ROOT)}/ — skapad")

    print()
    if args.check:
        if missing_after:
            print(f"❌ {len(missing_after)} saknas. Kör 'python af-mcp/init.py' utan --check för att skapa dem.")
            sys.exit(1)
        print("✅ Allt finns redan.")
        return

    if missing_after:
        print(f"⚠️  {len(missing_after)} poster kunde inte skapas, se FEL ovan.")
        sys.exit(1)

    print("✅ Klart. Nästa steg: låt AI:n läsa ONBOARDING.md och intervjua dig,")
    print("   eller fyll i career-ops/config/profile.yml, career-ops/portals.yml och")
    print("   career-ops/modes/_profile.md för hand.")
    print("   Testa sedan: python af-mcp/scan.py --dry-run --days 14")


if __name__ == "__main__":
    main()
