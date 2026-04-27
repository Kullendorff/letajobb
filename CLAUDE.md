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
- Senior Technical Advisor på Concentrix med specialisering inom Apples ekosystem, 2020–nu
- Journalist/redigerare-bakgrund (6+ år)
- Självlärd Python/Flask/API-utvecklare
- Söker BRETT: support, IT, Python dev, automation, kommunikatör, kundsuccess SaaS, hybrid tech+komm
- Göteborg primärt, remote/hybrid öppet

## NDA - Apple/Concentrix (KRITISKT)
Johan har skrivit NDA med Concentrix för Apple-uppdraget. NDA:t täcker explicit "Supplier's relationship to the Apple account". Det innebär:
- **Skriv ALDRIG "Apple via Concentrix" eller "anställd hos Apple"** i CV, brev eller publika dokument
- **Använd istället variant 1 (NDA-säker):** "Senior Technical Advisor på Concentrix med specialisering inom Apples ekosystem"
- I CV experience-sektion: `"Concentrix (specialisering: Apple-ekosystemet - macOS, iOS, iCloud)"`
- Bullet-text OK: "Andra linjens support för Apple-produkter (macOS, iOS, iCloud)" är försvarbart eftersom det är personlig kompetens, inte kundrelation
- Risk att skydda mot är inte stämning utan **Concentrix HR-konsekvens** om någon rekryterare rapporterar tillbaka. Branschen är liten.
- Om Johan får frågan i intervju: "uppdragsgivare omfattas av sekretess, jag namnger inte slutkund" räcker som svar

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

## Pipeline.html design (VIKTIGT)
- **"Att söka NU"-tabell** högst upp efter ANSÖKTA-sektionen, listar alla utvärderade-icke-ansökta-icke-EJ-AKTUELLA jobb
- Tabellen är **sorterbar** - klick på kolumnrubrik (Score / Deadline / Lokation / Företag) togglar sortering
- Default-sortering: Score DESC
- Varje rad har **två knappar**: 🔗 Ansök (direktlänk till annonsen) + 📋 [nr] (länk till rapporten)
- Deadline-celler färgkodade: röd (`deadline-urgent`) ≤ 7 dagar, orange (`deadline-warn`) ≤ 21 dagar, grön (`deadline-ok`) > 21 dagar
- Stats i headern: jobb totalt / ansökta / utvärderade / nya / ej aktuella
- Filter-knappar: Alla / Ansökta / Utvärderade / Nya / Göteborg / Remote / Komm / Tech / Ej aktuella

## Verifiera deadlines och status (VIKTIGT)
- Innan utvärdering eller "Att söka NU"-listning: **kolla att jobbet är öppet**
- Platsbanken-jobb (`arbetsformedlingen.se/platsbanken/annonser/{id}`): hämta via API `https://jobsearch.api.jobtechdev.se/ad/{id}` - returnerar deadline + apply URL
- Indeed-länkar (`to.indeed.com/...`): kan vara expired - öppna i Chrome och leta efter "jobbet har gått ut"
- Annars-länkar (Greenhouse, Ashby, Teamtailor, Workable): kan vara JS-renderade - använd företagets job-board API om sådan finns, annars Chrome MCP
- **Om jobb visat sig stängt:** markera som EJ AKTUELL i pipelinen med text "tjänsten har gått ut (verifierad YYYY-MM-DD)"
- **Om deadline okänd eller "verifiera":** lös detta innan jobbet hamnar i "Att söka NU"-tabellen
- Äldre Indeed-jobb (>7 dagar): verifiera proaktivt om de fortfarande är värda att rekommendera

## EJ AKTUELL-flow (VIKTIGT)
Jobb som är "EJ AKTUELL" SKA stanna i pipeline.html (med `class="job ej"` + `tag tag-ej`) eftersom:
- Scannern (`af-mcp/scan.py`) läser pipeline.html för kända IDs och hoppar över dem nästa scan
- Visuellt nedtonade (CSS `opacity: 0.4`) men sökbara via filter "Ej aktuella"
- Plus extra dubbel-spårning: lägg till rad i `career-ops/data/scan-history.tsv` med status `skipped-not-actual`

Vanliga EJ AKTUELL-orsaker att flagga tydligt i note-text:
- **Geografi-mismatch:** "tjänsten är i Norrköping/Stockholm/Linköping (inte Göteborg)"
- **Mandatory-krav saknas:** "kräver 5+ års X" / "PhD i Y" / "PLC-programmering" / "10 års strategisk kommunikation"
- **3-skift / visstid / villkor:** "3-skift rullande schema + visstid - dåligt fit"
- **Tjänsten tillsatt:** "verifierad expired YYYY-MM-DD"

## AI-marker scan (OBLIGATORISKT före leverans)
Efter att CV och brev skapats, kör regex-scan PLUS manuell läsning för att fånga AI-trigger-formuleringar:

Regex-flaggor (i ordning):
```
em-dash:          — eller –
"spännande":      \bspännande\b
"genuint intresse": \bgenuint intresse\b
"lösningsorienterad", "resultatdriven", "passionerad", "brinner för", "min passion"
"perfekt blandning", "naturlig fortsättning", "i en alltmer", "i en värld där"
"säkerställa att", "värt att notera", "världsledande"
"I'm thrilled", "passionate about", "leverage", "synergy", "spearhead"
```

Manuell trippelkoll (efter regex):
- Repetitiva meningsstartar
- Triadiska adjektivlistor ("kompetens, engagemang och driv")
- "Inte bara X utan också Y"-konstruktioner
- För perfekt struktur (varje stycke exakt 3 meningar)
- Kliché-formuleringar som inte säger något konkret ("matchar min utvecklingsriktning")
- Hyperlativer utan konkret backup

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

## CV per jobb (OBLIGATORISKT)
- **Skapa ALLTID ett dedikerat CV för varje jobb Johan söker**, även om det är 99% återanvändning av ett befintligt CV
- Spara som `Johan_Kullendorff_CV_{företag}.pdf` (eller .docx) via career-ops PDF-generering
- Justera minst: titel, profil-stycke, och 2-3 rader i kompetenser/erfarenhet så de speglar annonsens ord
- Detta gäller även snabba ansökningar - inget mer "återanvänder Friday_Mac som den är"
- Logga vilket CV som skickades i pipeline.html-noten (t.ex. "Ansökt 2026-04-22, CV: Akkodis-variant")

## Generera CV och brev (workflow)
- Pipeline finns i `outputs/generate_apps.py` (eller `generate_round2.py` för senare rundor) - Python-skript som tar profilen + variant-specifik info och bygger .docx via python-docx
- Skapas: `Johan_Kullendorff_CV_{key}.docx` och `Johan_Kullendorff_Brev_{key}.docx` i hittajobb-roten
- Konvertera till PDF via `libreoffice --headless --convert-to pdf {fil}.docx --outdir .`
- **Båda format levereras** - .docx för redigering, .pdf för uppladdning
- Dela ut via `computer://C:\AI\hittajobb\{filnamn}.pdf`-länkar
- Edit-tool och bash-tool ser olika filsystem-paths (Windows fil vs Linux mount). Om syntaxfel uppstår vid bash-körning: skriv om hela filen via `cat > /sessions/.../mnt/outputs/script.py << 'PYEOF' ... PYEOF`

## Chrome-flöde för ansökningar
- Öppna annonsen i Chrome MCP, identifiera ansökningssättet:
  - **Mail (info@xxx.se):** öppna Gmail-utkast med to+subject+body pre-fyllt via URL-params (`https://mail.google.com/mail/u/0/?fs=1&tf=cm&to=...&su=...&body=...`)
  - **Webbformulär:** scrolla, identifiera fält via `find`, fyll i namn/mejl/telefon, klistra in brev i cover letter-textbox där sådan finns
  - **Eccera/Akkodis (Zerolime/recman):** Johan har redan konton, lösenord-baserad inloggning kräver att Johan själv loggar in (säkerhetsregel)
- **File upload (CV/brev) blockeras av Chrome MCP säkerhetsregler** - Johan måste själv klicka 📎 paperclip eller 'upload'-knappen och välja PDF:erna
- Stanna ALLTID innan submit/send. Per `feedback_jobbsok_workflow.md`: aldrig tryck "skicka"
- Cookie-banners: välj alltid "Avvisa alla" / mest privacy-bevarande automatiskt

## Principer
- Ärlig, konkret ton, inget corporatespeak
- Anpassa CV-variant efter roll (3 befintliga + career-ops PDF-generering + nya per-jobb-varianter)
- Johan är i akut jobbsökarläge, bred sökning, inte bara drömroller
- Aldrig em-dash (—) eller en-dash (–) i svensk text. Bara vanligt bindestreck (-) om streck behövs
- **Inga rapporter för ohjälpliga jobb** - om mandatory-krav saknas, markera EJ AKTUELL direkt och gå vidare
