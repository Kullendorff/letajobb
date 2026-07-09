#!/usr/bin/env python3
"""Verifiera (och valfritt synka räknarna i) pipeline.html.

    python af-mcp/verify.py          # bara kontroll, exit 1 vid fel
    python af-mcp/verify.py --sync   # synka räknarna om de diffar (tar backup först)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from pipeline_lib import backup_pipeline, count_jobs, safe_write, sync_counters, verify_pipeline

PIPELINE = Path(__file__).parent.parent / "pipeline.html"


def main() -> None:
    html = PIPELINE.read_text(encoding="utf-8")
    c = count_jobs(html)
    print(f"Jobb: {c['total']} totalt — {c['applied']} ansökta, {c['done']} utvärderade, "
          f"{c['nya']} ovärderade, {c['ej']} ej aktuella")

    errors = verify_pipeline(html)
    synced = sync_counters(html)
    if synced != html:
        errors.append("räknarna är ur synk med korten (kör --sync för att rätta)")

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
