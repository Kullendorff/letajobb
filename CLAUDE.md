# Hittajobb — Johans jobbsökningsprojekt

## Syfte
AI-assisterad jobbsökning med career-ops som pipeline-motor.

## Struktur
- `career-ops/` — Klonad från santifer/career-ops, anpassad för Johan
- `Johan_Kullendorff_CV_Avinode.pdf` — CV (EN), Technical Support + API & Documentation
- `Johan_Kullendorff_CV_Friday_Mac.pdf` — CV (SV), IT-Supporttekniker, Mac & Windows
- `Johan_Kullendorff_CV_Sway.pdf` — CV (SV), Application Support, Incident Management
- `johan_kontext_claude_code.md` — Johans fullständiga kontextfil

## Kandidatprofil (snabbref)
- **Johan Kullendorff**, Göteborg, 49 år
- Senior Technical Advisor (Concentrix/Apple), 2020–nu
- Journalist/redigerare-bakgrund (6+ år)
- Självlärd Python/Flask/API-utvecklare
- Söker BRETT: support, IT, Python dev, automation, kommunikatör, hybrid tech+komm
- Göteborg primärt, remote/hybrid öppet

## Career-ops
Kör `/career-ops` i career-ops-mappen för alla kommandon.
Alla personliga anpassningar: `career-ops/config/profile.yml` + `career-ops/modes/_profile.md`

## HTML-output (VIKTIGT)
- `pipeline.html` — jobbpipeline med filter, statusmarkeringar och rapportlänkar. **Johans startsida i Chrome.** Ligger i hittajobb-roten.
- `reports/{NNN}-{företag}.html` (t.ex. `reports/001-lansstyrelsen-vgr.html`) — utvärderingsrapporter per jobb, i undermappen `reports/`
- Markdown-versioner sparas även i `career-ops/reports/` för career-ops-systemet
- **Efter varje utvärdering:** spara HTML-rapporten i `reports/`, uppdatera pipeline.html med status "UTVÄRDERAD" + länk `reports/NNN-slug.html`
- **Efter varje scan:** uppdatera pipeline.html med nya jobb
- **Använd ALLTID å ä ö** — aldrig ASCII-ersättningar i svenska texter
- Rapporternas HTML har mörkt tema, scorecard, STAR-historier, personligt brev, ATS-keywords
- Rapporter länkas tillbaka till pipeline.html via footer med `../pipeline.html` (ett steg upp från reports/)

## Platsbanken-scanner
`af-mcp/scan.py` söker Platsbanken (Arbetsförmedlingens API) och uppdaterar pipeline-filerna.

```
python af-mcp/scan.py              # senaste 7 dagarna
python af-mcp/scan.py --days 14    # senaste 14 dagarna
python af-mcp/scan.py --dry-run    # visa resultat utan att skriva filer
python af-mcp/scan.py --no-filter  # skippa titelfiltrering (debugging)
```

Scannern filtrerar träffar mot titelfiltret i `career-ops/portals.yml` (81 positiva, 26 negativa termer).
Uppdaterar: `pipeline.html`, `career-ops/data/pipeline.md`, `career-ops/data/scan-history.tsv`

## Principer
- Ärlig, konkret ton — inget corporatespeak
- Anpassa CV-variant efter roll (3 befintliga + career-ops PDF-generering)
- Johan är i akut jobbsökarläge — bred sökning, inte bara drömroller
