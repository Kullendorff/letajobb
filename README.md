# letajobb

AI-assisterad jobbsökning med pipeline-tänk. Byggt för att hålla koll på ett brett jobbsök utan att tappa bort sig i ett kaos av flikar och bokmärken.

## Vad det här är

En jobbsökningspipeline som skannar svenska och internationella jobbportaler, utvärderar roller mot min profil, och samlar allt i en filtrerad HTML-vy. Tänk CRM, fast för den som *söker* jobbet istället för den som säljer.

Bygger på [career-ops](https://github.com/santifer/career-ops) av [@santifer](https://github.com/santifer), som skapades för en helt annan jobbmarknad och rolltyp. Det här är en svensk fork, omskriven för svenska jobbportaler (Platsbanken, Indeed Sverige, Teamtailor m.fl.), svensk arbetsmarknad, och en bredare profil som spänner från teknisk support till kommunikatörsroller. Pipeline-vyn, utvärderingssystemet och portalskonfigurationen är egna tillägg.

## Hur det fungerar

**Skanning:** Söker igenom LinkedIn, Platsbanken, Indeed, Greenhouse, Ashby, Lever, Teamtailor och Workable efter roller som matchar. Portaler och sökfrågor är konfigurerade för den svenska marknaden plus remote/EMEA-roller hos internationella tech-bolag. Allt i `portals.yml`.

**Pipeline:** Alla hittade jobb hamnar i `pipeline.html` — en dark-mode dashboard med filter för kategori, plats, status och urgency. Varje jobb taggas (tech/komm, Göteborg/remote, ny/utvärderad/utgången) och kan klickas igenom till originalannonsen.

**Utvärdering:** Intressanta jobb utvärderas mot kandidatprofilen och får en rapport med scorecard, gap-analys, STAR-historier, personligt brev-utkast och ATS-keywords. Rapporterna genereras som HTML med mörkt tema och länkas direkt från pipeline-vyn.

## Struktur

```
letajobb/
├── pipeline.html                  # Startsida — jobbpipeline med filter
├── 001-lansstyrelsen-vgr.html     # Utvärderingsrapport
├── 002-experis-trafikverket.html
├── 003-lansstyrelsen-webbredaktor.html
├── 004-afry-teknikinformator.html
├── CURRENT_STATE.md               # Nuläge och historik
├── CLAUDE.md                      # AI-instruktioner för projektet
├── .gitignore
└── career-ops/                    # Pipeline-motor (fork av santifer/career-ops)
    ├── config/
    │   ├── profile.yml            # Kandidatprofil (gitignored — persondata)
    │   └── profile.example.yml    # Exempelprofil
    ├── portals.yml                # Sökfrågor och bevakade företag
    ├── data/
    │   ├── pipeline.md            # Alla jobb i markdown-format
    │   └── applications.md        # Ansökningsstatus
    ├── reports/                   # Utvärderingsrapporter (markdown)
    ├── modes/                     # career-ops lägen och profil
    └── ...
```

## Vad som skiljer den här forken

Originalet (career-ops) är riktat mot en specifik internationell marknad. Den här varianten är anpassad för:

- **Svenska jobbportaler** — Platsbanken, Indeed Sverige, Teamtailor-baserade karriärsidor, Varbi (offentlig sektor)
- **Bred rollprofil** — söker parallellt inom IT-support, Python-utveckling, kommunikation, teknikinformation och hybridroller
- **HTML-pipeline** — egen dark-mode dashboard (`pipeline.html`) med filter, taggar och rapportlänkar som ersätter career-ops standardvy
- **Utvärderingsrapporter** — scorecard, gap-analys, STAR-historier och personligt brev-utkast, genererade som statisk HTML
- **Svensk + EMEA-remote** — skannar både lokalt (Göteborg) och internationella remote-roller hos bolag som GitLab, Zapier, n8n, Camunda m.fl.

## Teknik

Ingen fancy stack. HTML + vanilla JS för pipeline-vyn. career-ops körs med Node.js + Playwright för portalskanning. Rapporter genereras som statisk HTML. Hela grejjen orkestreras via Claude som AI-assistent för skanning, utvärdering och rapportskrivning.

## Status

Aktivt projekt. Pipeline skannas regelbundet och utökas med nya portaler vid behov. Just nu 35 jobb i pipeline, varav 4 utvärderade.

## Personligt

Det här är mitt faktiska jobbsök — inte ett demo eller proof-of-concept. Jag är Senior Technical Advisor med journalistbakgrund och självlärd Python-utvecklare i Göteborg som söker brett: support, IT, utveckling, kommunikation, och hybrider däremellan.

Portfolion finns på [kullendorff.github.io/thisisme](https://kullendorff.github.io/thisisme/).

---

*Känslig persondata (CV:n, personnummer, kontaktuppgifter, löneanspråk) är exkluderade via `.gitignore`.*
