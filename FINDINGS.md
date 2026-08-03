# Progress Notes: Component-Level Dependency Analysis of Turkish Defence Platforms

**Status: ongoing PhD dissertation fieldwork (2026–present). This is a working note on methodology and interim findings, not a finished paper — it will be updated as the verification work continues.**

## Research question

SIPRI's Arms Transfers Database records platform-level transfers and flags "local production," but it does not link a locally-produced platform to the specific foreign subsystems (engines, sensors, naval weapons, etc.) it depends on. This project asks: for Turkey's major defence platforms, which foreign components/suppliers is "local production" actually built on, and how has that dependency structure changed over time?

## Method

Dependency claims are cross-validated across three independent source types rather than relying on any single one:

1. **SIPRI Arms Transfers Database** — used both for its "local production" flag and, experimentally, for temporal co-occurrence between a platform's delivery years and other imports in the same period.
2. **Official export-control records** (US DSCA Major Arms Sales notifications, German *Rüstungsexportbericht*) — used where SIPRI coverage is thin or below its reporting threshold.
3. **Secondary/open-source literature** — principally Egeli, Güvenç, Kurç & Mevlütoğlu (2024), *"From Client to Competitor: The Rise of Türkiye's Defence Industry,"* IISS/CFPPR, and manufacturer/press reporting (company press releases, Naval News, Defence Turkey, Jamestown Foundation, etc.).

**A methodological result worth flagging on its own:** an early version of this project tried to establish supplier links purely statistically — matching a platform's delivery year against other imports arriving in the same window. Run end-to-end against the 36 SIPRI-flagged "local production" designs (script and full write-up in [`criticality_matrix/README.md`](criticality_matrix/README.md)), this heuristic returns a candidate subsystem match for 36 of 36 (100%) — i.e., it fails to discriminate at all. That negative result is treated as a finding in its own right: temporal co-occurrence alone is not usable evidence for platform–subsystem linkage in this dataset, and every dependency claim in the underlying dataset is now instead confirmed through the multi-source process above, with unconfirmed cases explicitly labelled as such rather than silently dropped or asserted.

## Current coverage (interim)

Across 141 locally-produced/procured designs identified so far (from SIPRI's local-production flag, 1950–2025, combined with IISS/CFPPR's 1982–2022 procurement tables):

- **131 (93%)** are corroborated by two or more independent sources.
- **2 (1%)** currently rest on a single secondary source (IISS/CFPPR) alone and remain unresolved despite active search (Bell 412EP, MIM-23 HAWK).
- **8 (6%)** are partially confirmed or still pending further corroboration.

## Illustrative findings

- **Ada-class corvette (MİLGEM):** component-level sourcing spans six different countries — the US (anti-ship missile, gas turbines), Germany (diesel engines, air-defence missile system), Italy (main gun), France (ESM/ECM), the Netherlands (radar/EO), and the UK (torpedo defence) — a concrete illustration of how "local production" can still carry a wide multinational dependency footprint.
- **Bayraktar Akıncı:** three-country component sourcing (South Africa, Ukraine, Canada) for EO payloads and engines.
- **M-52T self-propelled howitzer:** a 1950s US-supplied chassis re-armed in 1995–98 with a German (Rheinmetall) turret and 155mm/L39 gun — a two-stage, two-country dependency chain across four decades.
- **Dependency trajectories over time**, not just snapshots: e.g. the S-70A Black Hawk moved from an off-the-shelf US purchase (1992) to Turkish licensed production (T-70, 2014) with the same supplier; conversely, the Anka UAV's 2004 baseline listed no foreign supplier, while the upgraded Anka-3 (2022) shows a new engine dependency (Ukraine) — a reminder that dependency reduction is not a one-directional trend.

## Data note

The full working dataset (spreadsheet-level dependency table, per-row source citations, and rows still pending verification) is kept private while verification is in progress, since it mixes confirmed and unconfirmed claims. This document summarizes the method and the findings that already meet the two-source bar above. Code for the SIPRI temporal-matching script, the DSCA/German export scrapers, and the news-scraping/deduplication pipeline is in this repository (see `README.md`). Dated, granular notes on each verification pass are in [`research-log.md`](research-log.md).

## Next steps

- Re-check the 2 remaining unresolved cases (Bell 412EP, MIM-23 HAWK) against additional specialist sources (Jane's, SSB statements).
- Resolve the 8 partially-confirmed/pending rows.
- Extend the two-stage/multi-stage dependency-evolution mapping (illustrated above for a handful of platforms) systematically across the full dataset — recent additions to this pattern include Atmaca and SOM (French→domestic engine), T625 Gökbey (foreign prototype engine→domestic TEI production engine), and Barbaros MLU (foreign→domestic combat management system).
- Build out the criticality-scoring layer (functional necessity × export restriction × substitution availability) as a distinct next phase, once the underlying dependency mapping above is more complete.
