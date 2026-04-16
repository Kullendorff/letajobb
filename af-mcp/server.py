"""Platsbanken MCP-server — söker jobb via Arbetsförmedlingens öppna JobTech API."""

from __future__ import annotations

import httpx
from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
JOBSEARCH_BASE = "https://jobsearch.api.jobtechdev.se"
TAXONOMY_BASE = "https://taxonomy.api.jobtechdev.se"
DEFAULT_TIMEOUT = 15.0
GÖTEBORG_MUNICIPALITY = "1480"
VGR_REGION = "14"

server = FastMCP(
    name="platsbanken",
    instructions=(
        "MCP-server för att söka jobb på Platsbanken (Arbetsförmedlingen). "
        "Använd sok_taxonomy för att slå upp concept IDs för yrken, kommuner "
        "och kompetenser innan du filtrerar med sok_jobb."
    ),
)


# ---------------------------------------------------------------------------
# HTTP helper
# ---------------------------------------------------------------------------
async def _get(base: str, path: str, params: dict | None = None) -> dict | list:
    """GET request with timeout and basic error handling."""
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        resp = await client.get(
            f"{base}{path}",
            params=params,
            headers={"Accept": "application/json"},
        )
        resp.raise_for_status()
        return resp.json()


# ---------------------------------------------------------------------------
# Tool 1: sok_jobb
# ---------------------------------------------------------------------------
@server.tool()
async def sok_jobb(
    q: str = "",
    municipality: str = "",
    region: str = "",
    remote: bool | None = None,
    occupation_field: str = "",
    occupation_group: str = "",
    occupation_name: str = "",
    skill: list[str] | None = None,
    employment_type: str = "",
    sort: str = "pubdate-desc",
    published_after: str = "",
    experience: bool | None = None,
    limit: int = 25,
    offset: int = 0,
) -> str:
    """Sök jobb på Platsbanken.

    Parametrar:
    - q: Fritext (t.ex. "python developer", "IT-support")
    - municipality: Kommun-kod (t.ex. "1480" för Göteborg). Använd sok_taxonomy för att slå upp.
    - region: Region-kod (t.ex. "14" för Västra Götaland)
    - remote: true = bara distansjobb
    - occupation_field/group/name: Concept IDs från taxonomy (använd sok_taxonomy)
    - skill: Lista med skill concept IDs
    - employment_type: Concept ID (t.ex. PFZr_Syz_cUq = Vanlig anställning)
    - sort: pubdate-desc (nyast först, default), pubdate-asc, relevance, applydate-asc, updated
    - published_after: Visa bara jobb publicerade efter detta datum (ISO 8601 eller t.ex. "PT7D" för senaste 7 dagarna)
    - experience: false = jobb utan erfarenhetskrav
    - limit: Antal resultat (1-100, default 25)
    - offset: Sidförskjutning (0-2000)
    """
    params: dict = {"limit": min(max(limit, 1), 100), "offset": min(max(offset, 0), 2000)}

    if q:
        params["q"] = q
    if municipality:
        params["municipality"] = municipality
    if region:
        params["region"] = region
    if remote is not None:
        params["remote"] = str(remote).lower()
    if occupation_field:
        params["occupation-field"] = occupation_field
    if occupation_group:
        params["occupation-group"] = occupation_group
    if occupation_name:
        params["occupation-name"] = occupation_name
    if skill:
        params["skill"] = skill
    if employment_type:
        params["employment-type"] = employment_type
    if sort:
        params["sort"] = sort
    if published_after:
        params["published-after"] = published_after
    if experience is not None:
        params["experience"] = str(experience).lower()

    data = await _get(JOBSEARCH_BASE, "/search", params)

    total = data.get("total", {}).get("value", 0)
    hits = data.get("hits", [])

    lines = [f"## Sökresultat: {total} jobb totalt (visar {offset + 1}–{offset + len(hits)})\n"]

    for ad in hits:
        headline = ad.get("headline", "Utan rubrik")
        employer = ad.get("employer", {}).get("name", "Okänd arbetsgivare")
        city = ad.get("workplace_address", {}).get("city", "")
        municipality_name = ad.get("workplace_address", {}).get("municipality", "")
        location = city or municipality_name or "Ej angiven"
        deadline = ad.get("application_deadline", "Ej angiven")
        if deadline and "T" in deadline:
            deadline = deadline.split("T")[0]
        ad_id = ad.get("id", "")
        webpage = ad.get("webpage_url", "")
        remote_flag = ""
        if ad.get("workplace_address", {}).get("country") and not ad.get("workplace_address", {}).get("municipality"):
            remote_flag = " 🌐 Remote"

        # Employment type
        emp_type = ad.get("employment_type", {})
        emp_label = emp_type.get("label", "") if emp_type else ""

        # Occupation
        occ = ad.get("occupation", {})
        occ_label = occ.get("label", "") if occ else ""

        # Application URL
        app_details = ad.get("application_details", {})
        apply_url = app_details.get("url", "") if app_details else ""

        lines.append(f"### {headline}")
        lines.append(f"**Arbetsgivare:** {employer}")
        lines.append(f"**Plats:** {location}{remote_flag}")
        if occ_label:
            lines.append(f"**Yrke:** {occ_label}")
        if emp_label:
            lines.append(f"**Anställning:** {emp_label}")
        lines.append(f"**Sista ansökningsdag:** {deadline}")
        lines.append(f"**ID:** {ad_id}")
        if apply_url:
            lines.append(f"**Ansök:** {apply_url}")
        if webpage:
            lines.append(f"**Platsbanken:** {webpage}")
        lines.append("")

    if not hits:
        lines.append("Inga jobb hittades. Prova bredare söktermer eller andra filter.")

    if total > offset + len(hits):
        lines.append(f"---\n*Fler resultat finns. Använd offset={offset + limit} för nästa sida.*")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Tool 2: hamta_annons
# ---------------------------------------------------------------------------
@server.tool()
async def hamta_annons(annons_id: str) -> str:
    """Hämta fullständig jobbannons från Platsbanken.

    Parametrar:
    - annons_id: Annonsens ID (från sökresultat eller Platsbanken-URL)
    """
    ad = await _get(JOBSEARCH_BASE, f"/ad/{annons_id}")

    headline = ad.get("headline", "Utan rubrik")
    employer = ad.get("employer", {})
    employer_name = employer.get("name", "Okänd")
    employer_url = employer.get("url", "")
    employer_org = employer.get("organization_number", "")

    wp = ad.get("workplace_address", {}) or {}
    city = wp.get("city", "")
    municipality_name = wp.get("municipality", "")
    region_name = wp.get("region", "")
    location_parts = [p for p in [city, municipality_name, region_name] if p]
    location = ", ".join(location_parts) or "Ej angiven"

    desc = ad.get("description", {}) or {}
    description_text = desc.get("text", "Ingen beskrivning tillgänglig.")

    emp_type = ad.get("employment_type", {})
    emp_label = emp_type.get("label", "") if emp_type else ""
    duration = ad.get("duration", {})
    duration_label = duration.get("label", "") if duration else ""
    working_hours = ad.get("working_hours_type", {})
    hours_label = working_hours.get("label", "") if working_hours else ""
    scope = ad.get("scope_of_work", {})
    scope_min = scope.get("min", "") if scope else ""
    scope_max = scope.get("max", "") if scope else ""

    deadline = ad.get("application_deadline", "Ej angiven")
    if deadline and "T" in deadline:
        deadline = deadline.split("T")[0]
    pub_date = ad.get("publication_date", "")
    if pub_date and "T" in pub_date:
        pub_date = pub_date.split("T")[0]

    webpage = ad.get("webpage_url", "")
    app_details = ad.get("application_details", {}) or {}
    apply_url = app_details.get("url", "")
    apply_email = app_details.get("email", "")
    apply_ref = app_details.get("reference", "")

    # Must have / Nice to have
    must_have = ad.get("must_have", {}) or {}
    nice_to_have = ad.get("nice_to_have", {}) or {}

    def _format_requirements(reqs: dict) -> list[str]:
        parts = []
        for key in ["skills", "languages", "work_experiences", "education", "education_level"]:
            items = reqs.get(key, [])
            if items:
                labels = [item.get("label", "?") for item in items]
                parts.append(f"  - **{key.replace('_', ' ').title()}:** {', '.join(labels)}")
        return parts

    # Build output
    lines = [f"# {headline}\n"]
    lines.append(f"**Arbetsgivare:** {employer_name}")
    if employer_org:
        lines.append(f"**Org.nr:** {employer_org}")
    if employer_url:
        lines.append(f"**Webb:** {employer_url}")
    lines.append(f"**Plats:** {location}")
    lines.append("")

    # Employment details
    details = []
    if emp_label:
        details.append(f"**Anställningstyp:** {emp_label}")
    if duration_label:
        details.append(f"**Varaktighet:** {duration_label}")
    if hours_label:
        details.append(f"**Arbetstid:** {hours_label}")
    if scope_min and scope_max:
        details.append(f"**Omfattning:** {scope_min}–{scope_max}%")
    if details:
        lines.extend(details)
        lines.append("")

    # Dates
    lines.append(f"**Publicerad:** {pub_date}")
    lines.append(f"**Sista ansökningsdag:** {deadline}")
    lines.append("")

    # Requirements
    must_lines = _format_requirements(must_have)
    if must_lines:
        lines.append("## Krav")
        lines.extend(must_lines)
        lines.append("")

    nice_lines = _format_requirements(nice_to_have)
    if nice_lines:
        lines.append("## Meriterande")
        lines.extend(nice_lines)
        lines.append("")

    # Description
    lines.append("## Beskrivning")
    if len(description_text) > 4000:
        lines.append(description_text[:4000] + "\n\n*[Beskrivningen trunkerad — se fullständig annons via länken nedan]*")
    else:
        lines.append(description_text)
    lines.append("")

    # Application
    lines.append("## Ansökan")
    if apply_url:
        lines.append(f"**Ansök här:** {apply_url}")
    if apply_email:
        lines.append(f"**E-post:** {apply_email}")
    if apply_ref:
        lines.append(f"**Referens:** {apply_ref}")
    if webpage:
        lines.append(f"**Platsbanken:** {webpage}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Tool 3: sok_taxonomy
# ---------------------------------------------------------------------------
@server.tool()
async def sok_taxonomy(
    query: str,
    typ: str = "municipality",
) -> str:
    """Slå upp concept IDs i Arbetsförmedlingens taxonomy.

    Använd detta verktyg INNAN sok_jobb för att översätta namn till concept IDs.

    Parametrar:
    - query: Sökterm (t.ex. "Göteborg", "Python", "Data/IT")
    - typ: Typ att söka bland. Möjliga värden:
      - municipality (kommun, default)
      - region
      - occupation-name (specifikt yrke)
      - occupation-group (yrkesgrupp)
      - occupation-field (yrkesområde, t.ex. "Data/IT")
      - skill (kompetens)
      - language
      - employment-type

    Vanliga concept IDs:
    - Göteborg (municipality): PVZL_BQT_XtL
    - Västra Götalands län (region): EVvN_pUR_uqL
    - Data/IT (occupation-field): apaJ_2ja_LuF
    """
    import urllib.parse

    # Use the Taxonomy GraphQL API
    gql_query = (
        f'{{concepts(type:"{typ}",'
        f'preferred_label_contains:"{query}",'
        f'limit:15)'
        f'{{id,preferred_label,type}}}}'
    )
    url = f"{TAXONOMY_BASE}/v1/taxonomy/graphql?query={urllib.parse.quote(gql_query)}"

    try:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            resp = await client.get(url, headers={"Accept": "application/json"})
            resp.raise_for_status()
            data = resp.json()

        concepts = data.get("data", {}).get("concepts", [])

        if not concepts:
            return f"Inga resultat för \"{query}\" (typ: {typ}). Prova en annan sökterm eller typ."

        lines = [f"## Taxonomy-resultat för \"{query}\" (typ: {typ})\n"]
        lines.append("| Concept ID | Namn |")
        lines.append("|------------|------|")
        for item in concepts:
            lines.append(f"| `{item['id']}` | {item['preferred_label']} |")

        lines.append(f"\n*Använd concept ID i sok_jobb-parametrar (t.ex. municipality=\"{concepts[0]['id']}\")*")
        return "\n".join(lines)

    except Exception as e:
        return f"Fel vid taxonomy-sökning: {e}"


# ---------------------------------------------------------------------------
# Tool 4: autocomplete
# ---------------------------------------------------------------------------
@server.tool()
async def autocomplete(q: str) -> str:
    """Autocomplete/typeahead för Platsbanken-sökningar.

    Parametrar:
    - q: Början på en sökterm (minst 2 tecken)
    """
    if len(q) < 2:
        return "Ange minst 2 tecken för autocomplete."

    data = await _get(JOBSEARCH_BASE, "/complete", {"q": q})
    suggestions = data.get("typeahead", []) if isinstance(data, dict) else data

    if not suggestions:
        return f"Inga förslag för \"{q}\"."

    lines = [f"## Förslag för \"{q}\"\n"]
    for item in suggestions[:20]:
        if isinstance(item, str):
            lines.append(f"- {item}")
        elif isinstance(item, dict):
            label = item.get("value", item.get("label", item.get("name", str(item))))
            typ = item.get("type", "")
            type_hint = f" *({typ})*" if typ else ""
            lines.append(f"- {label}{type_hint}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    server.run(transport="stdio")
