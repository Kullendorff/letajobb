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
Alla rapporter och vyer genereras som HTML i hittajobb-roten (`C:\AI\hittajobb\`):
- `pipeline.html` — jobbpipeline med filter, statusmarkeringar och rapportlänkar. **Johans startsida i Chrome.**
- `{NNN}-{företag}.html` (t.ex. `001-lansstyrelsen-vgr.html`) — utvärderingsrapporter per jobb
- Markdown-versioner sparas även i `career-ops/reports/` för career-ops-systemet
- **Efter varje utvärdering:** uppdatera pipeline.html med status "UTVÄRDERAD" + länk till HTML-rapport
- **Efter varje scan:** uppdatera pipeline.html med nya jobb
- **Använd ALLTID å ä ö** — aldrig ASCII-ersättningar i svenska texter
- Rapporternas HTML har mörkt tema, scorecard, STAR-historier, personligt brev, ATS-keywords
- Rapporter länkas tillbaka till pipeline.html via footer

## Principer
- Ärlig, konkret ton — inget corporatespeak
- Anpassa CV-variant efter roll (3 befintliga + career-ops PDF-generering)
- Johan är i akut jobbsökarläge — bred sökning, inte bara drömroller
