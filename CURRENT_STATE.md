# Hittajobb - Current State (2026-04-16)

## Vad vi gjort

### Career-ops (jobbsökningspipeline)
- Klonat och anpassat santifer/career-ops för Johan
- Alla config-filer skapade: profile.yml, cv.md, _profile.md, portals.yml
- Playwright + npm installerat, `npm run doctor` grön
- Pipeline.html skapad i hittajobb-roten (Johans Chrome-startsida)
- Senaste scan: 55 jobb i pipeline, 1 ansökt, 8 utvärderade, 4 utgångna

### Platsbanken-scanner (af-mcp)
- `af-mcp/server.py` — MCP-server mot JobTech API (4 verktyg: sok_jobb, hamta_annons, sok_taxonomy, autocomplete)
- `af-mcp/scan.py` — batch-scanner med titelfiltrering från portals.yml (40 → 10 relevanta träffar/scan)
- Konfigurerad i `~/.mcp.json` för Claude Code

### Utvärderade jobb (9 st)
| # | Jobb | Score | Status |
|---|------|-------|--------|
| 001 | Länsstyrelsen VGR - Strategisk kommunikatör | 3.8/5 | Ej ansökt (deadline 20 apr) |
| 002 | Experis/Trafikverket - IT-tekniker | 4.2/5 | Utvärderad |
| 003 | Länsstyrelsen VGR - Webbredaktör/Språkvårdare | 4.1/5 | Utvärderad |
| 004 | AFRY - Teknikinformatör | 4.5/5 | **ANSÖKT 2026-04-16** |
| 005 | CarbonCloud - Customer Support Specialist | 4.3/5 | Utvärderad |
| 006 | Linden-IT - Operativ Team Lead IT Service Desk | 3.5/5 | Utvärderad |
| 007 | Experis - Servicedesk-tekniker inom IT | 3.8/5 | Utvärderad |
| 008 | Akkodis - IT-Support i Göteborg | 3.7/5 | Utvärderad (deadline 28 apr) |
| 009 | Frico AB - Marknadskommunikatör | okänd | Utvärderad |

Rapporter: `reports/` (HTML, gitignored) + `career-ops/reports/` (markdown)
Tracker: `career-ops/data/applications.md`
Pipeline: `career-ops/data/pipeline.md` + `pipeline.html`

### GitHub-profil städad
- Ny bio: "Technical Advisor | Python, Flask, AI APIs | Journalist background. Building tools with LLMs. Gothenburg, Sweden."
- 6 pinnade repos: compareai, debateAI, drivebot, rpgbot, transkribering_svensk, systembolaget
- README:s fixade: compareai (omskriven), trip19, densomsover, arsenia, gravensarv (alla nya)
- .gitignore fixad: trip19 + densomsover (lade till .env*)
- Exponerade API-nycklar: revokerade av Johan (GitHub-token + OpenAI)
- Allt pushat till GitHub

### thisisme — Portfolio-sida (KLAR)
- **5 POC-koncept** skapade och utvärderade (The Pitch, Show Don't Tell, The Arc, The Signal, The Conversation)
- **2 fullversioner** byggda och deployade:
  - `index.html` — **The Pitch**: Billboard-hero + projekt, erfarenhet, kompetens under folden. Burnt orange accent.
  - `arc/index.html` — **The Arc**: Scrollytelling i tre akter (Berättaren → Felsökaren → Byggaren). Progress-nav, projektkort, cinematiska transitions.
- Repo rensat: 15 varianter + POC:er borttagna, bara produktionsklara filer kvar
- Pushat till GitHub: `kullendorff.github.io/thisisme/`
- LLM-easter-egg i båda (subtil, inte huvudfeature)
- "Se min historia →" länk i Pitch-footern till Arc-versionen

### LinkedIn-profil kurerad (KLAR)
Komplett genomgång och uppdatering:
- **URL**: `johan-kullendorff-0512b43b` → `johankullendorff`
- **Headline**: "Senior Technical Advisor | Journalist & Editor | Python Developer"
- **Företag**: Webhelp → Concentrix
- **Titel**: Senior Technical Support Specialist → Senior Technical Advisor
- **Industry**: Media Production → IT Services and IT Consulting
- **About**: Omskriven till punchy engelska — "I debug things, explain things, and build things."
- **Språk**: Borttagen "Computer Jargon", tillagd Swedish (Native), behållt English (Full professional)
- **Experience**: Alla beskrivningar översatta till engelska (Concentrix, AmiNTe, Hall Media, Hallpressen)
- **Föreläsare-rollen**: Borttagen (distraherade från tech-profilen)
- **Projekt**: 4 st — alla fixade från trasig markdown/svenska till ren engelska (Systembolaget, Diceroller, CompareAI, DriveBot)
- Profilen nu konsekvent engelska genomgående

### Regler (sparade i memory)
- **NDA:** Concentrix KPI-reform nämns ALDRIG i ansökningar
- **HTML-output:** Rapporter i `reports/` (HTML) + `career-ops/reports/` (md). Backlinks via `../pipeline.html`
- **Skrivstil:** Läs writing_style_analysis.json, undvik AI-mönster (se feedback_writing_style.md)
- **Svenska tecken:** Alltid å ä ö, aldrig ASCII-ersättningar
- **Pipeline.html:** Johans Chrome-startsida, uppdateras efter varje scan/utvärdering

## Nästa steg

### Jobbansökningar
- Akkodis IT-Support (deadline 28 april) — score 3.7/5
- Länsstyrelsen strategisk kommunikatör (deadline 20 april) — score 3.8/5
- ~45 oevaluerade jobb kvar i pipeline

### Verktyg
- Kör `python af-mcp/scan.py` för att hämta nya Platsbanken-jobb
- Kör `/career-ops pipeline` för att utvärdera jobb i pipeline.md

### Övrigt
- LinkedIn: Överväg att rensa bland 42 skills (behåll 15-20 relevanta)

## Filstruktur

```
C:\AI\hittajobb\
├── CLAUDE.md                           # Projektinstruktioner
├── CURRENT_STATE.md                    # Denna fil
├── pipeline.html                       # Chrome-startsida, jobbpipeline
├── reports/                            # HTML-utvärderingsrapporter (gitignored)
│   ├── 001-lansstyrelsen-vgr.html
│   ├── 002-experis-trafikverket.html
│   ├── 003-lansstyrelsen-webbredaktor.html
│   ├── 004-afry-teknikinformator.html
│   ├── 005-carboncloud.html
│   ├── 006-linden-it.html
│   ├── 007-experis-servicedesk.html
│   ├── 008-akkodis.html
│   └── 009-frico.html
├── af-mcp/                             # Platsbanken-scanner + MCP-server
│   ├── server.py                       # MCP-server (4 verktyg: sok_jobb, hamta_annons, ...)
│   ├── scan.py                         # Batch-scanner med titelfiltrering
│   └── requirements.txt
├── Johan_Kullendorff_CV_Avinode.pdf    # CV (EN)
├── Johan_Kullendorff_CV_Friday_Mac.pdf # CV (SV, IT-support)
├── Johan_Kullendorff_CV_Sway.pdf       # CV (SV, incident mgmt)
└── career-ops/                         # Jobbsökningspipeline

C:\AI\thisisme\
├── index.html                          # The Pitch (landningssida)
├── arc/index.html                      # The Arc (scrollytelling)
└── README.md
```
