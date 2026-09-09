---
name: starta-jobbsok
description: Startar första körningen — intervjuar en ny användare och skräddarsyr jobbsöksprojektet åt hen
user_invocable: true
---

# starta-jobbsok

Läs `ONBOARDING.md` i repo-roten och följ det till punkt och pricka: kolla
vilka konfigfiler som saknas, ställ de nio frågeblocken i onboardingen,
skriv svaren till rätt filer, kör `python af-mcp/init.py` samt
`python af-mcp/verify.py` och `python af-mcp/scan.py --dry-run --days 14`
när intervjun är klar.

Om alla filer som `ONBOARDING.md` listar under "Detektering" redan finns:
säg det till användaren och fråga om de ändå vill gå igenom intervjun igen
(t.ex. för att uppdatera målroller) — kör inte om den i onödan.
