#!/usr/bin/env python3
"""Verifiera (och valfritt synka räknarna i) pipeline.html.

    python af-mcp/verify.py          # bara kontroll, exit 1 vid fel
    python af-mcp/verify.py --sync   # synka räknarna om de diffar (tar backup först)
"""

import sys
from pathlib import Path

# Windows cp1252-konsolen kraschar annars på ✅/❌-tecken.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).parent))
from pipeline_lib import backup_pipeline, count_jobs, safe_write, sync_counters, verify_pipeline

ROOT = Path(__file__).parent.parent
PIPELINE = ROOT / "pipeline.html"


def main() -> None:
    if not PIPELINE.exists():
        print(f"❌ {PIPELINE.relative_to(ROOT)} saknas. Kör: python af-mcp/init.py", file=sys.stderr)
        sys.exit(1)
    html = PIPELINE.read_text(encoding="utf-8")
    c = count_jobs(html)
    print(f"Jobb: {c['total']} totalt — {c['applied']} ansökta, {c['done']} utvärderade, "
          f"{c['nya']} ovärderade, {c['ej']} ej aktuella")

    errors = verify_pipeline(html)
    synced = sync_counters(html)
    if synced != html:
        errors.append("räknarna är ur synk med korten (kör --sync för att rätta)")

    # 0 jobbkort är ett hårt fel i verify_pipeline() (skyddar safe_write mot att
    # av misstag tömma en befintlig pipeline) — men i verify.py, som bara
    # rapporterar till en människa, är en helt ny, tom pipeline.html (precis
    # byggd av af-mcp/init.py) inte ett fel. Nedgradera just det specialfallet.
    if errors == ["0 jobbkort hittades"]:
        print("ℹ️  pipeline.html är tom — inga jobb tillagda än. Kör af-mcp/scan.py för att fylla den.")
        return

    if not errors:
        print("✅ pipeline.html OK")
        return
    if "--sync" in sys.argv and errors == ["räknarna är ur synk med korten (kör --sync för att rätta)"]:
        bak = backup_pipeline(PIPELINE)
        print(f"🔒 Backup: {bak.name}")
        safe_write(PIPELINE, synced)
        print("✅ räknare synkade")
        return
    print("❌ FEL:\n  - " + "\n  - ".join(errors))
    sys.exit(1)


if __name__ == "__main__":
    main()
