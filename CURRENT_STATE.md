# Hittajobb - Current State (2026-04-11)

## Vad vi gjort

### Career-ops (jobbsökningspipeline)
- Klonat och anpassat santifer/career-ops för Johan
- Alla config-filer skapade: profile.yml, cv.md, _profile.md, portals.yml
- Playwright + npm installerat, `npm run doctor` grön
- Skannat portaler: 35 jobb i pipeline (27 tech + 8 kommunikatör, varav 2 utgångna)
- Pipeline.html skapad i hittajobb-roten (Johans Chrome-startsida)
- Scan 2026-04-11: +8 nya jobb (Camunda, GitLab x2, Nexer x2, Akkodis, Jobandtalent, Frontendutvecklare), 2 utgångna (GöteborgsOperan, Göteborgs Stad)

### Utvärderade jobb (4 st)
| # | Jobb | Score | Filer |
|---|------|-------|-------|
| 001 | Länsstyrelsen VGR - Strategisk kommunikatör | 3.8/5 | rapport + HTML + CV-PDF |
| 002 | Experis/Trafikverket - IT-tekniker | 4.2/5 | rapport + HTML |
| 003 | Länsstyrelsen VGR - Webbredaktör/Språkvårdare | 4.1/5 | rapport + HTML |
| 004 | AFRY - Teknikinformatör | 4.5/5 | rapport + HTML |

Alla rapporter i: career-ops/reports/ (markdown) + hittajobb-roten (HTML)
Tracker: career-ops/data/applications.md
Pipeline: career-ops/data/pipeline.md + hittajobb/pipeline.html

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
- **HTML-output:** Alla rapporter som HTML i hittajobb-roten + md i career-ops/reports/
- **Skrivstil:** Läs writing_style_analysis.json, undvik AI-mönster (se feedback_writing_style.md)
- **Svenska tecken:** Alltid å ä ö, aldrig ASCII-ersättningar
- **Pipeline.html:** Johans Chrome-startsida, uppdateras efter varje scan/utvärdering

## Nästa steg

### Jobbansökningar att skicka
- Länsstyrelsen strategisk kommunikatör (deadline 20 april)
- AFRY teknikinformatör (4.5/5, högsta score)
- 23 oevaluerade jobb kvar i pipeline

### Övrigt
- thisisme: Aktivera GitHub Pages om inte redan gjort
- LinkedIn: Överväg att rensa bland 42 skills (behåll 15-20 relevanta)
- LinkedIn: Projektbeskrivningar saknar CompareAI och DebateAI på GitHub-länknivå

## Filstruktur

```
C:\AI\hittajobb\
├── CLAUDE.md                           # Projektinstruktioner
├── CURRENT_STATE.md                    # Denna fil
├── pipeline.html                       # Chrome-startsida, jobbpipeline
├── 001-lansstyrelsen-vgr.html          # Rapport: strategisk kommunikatör
├── 002-experis-trafikverket.html       # Rapport: IT-tekniker
├── 003-lansstyrelsen-webbredaktor.html # Rapport: webbredaktör
├── 004-afry-teknikinformator.html      # Rapport: teknikinformatör
├── Johan_Kullendorff_CV_Avinode.pdf    # CV (EN)
├── Johan_Kullendorff_CV_Friday_Mac.pdf # CV (SV, IT-support)
├── Johan_Kullendorff_CV_Sway.pdf       # CV (SV, incident mgmt)
└── career-ops/                         # Jobbsökningspipeline

C:\AI\thisisme\
├── index.html                          # The Pitch (landningssida)
├── arc/index.html                      # The Arc (scrollytelling)
└── README.md
```
