# Progress Notes: Component-Level Dependency Analysis of Turkish Defence Platforms

**Status: ongoing PhD dissertation fieldwork (2026–present). This is a working note on methodology and interim findings, not a finished paper — it will be updated as the verification work continues.**

## Research question

SIPRI's Arms Transfers Database records platform-level transfers and flags "local production," but it does not link a locally-produced platform to the specific foreign subsystems (engines, sensors, naval weapons, etc.) it depends on. This project asks: for Turkiye's major defence platforms, which foreign components/suppliers is "local production" actually built on, and how has that dependency structure changed over time?

## Method

Dependency claims are cross-validated across three independent source types rather than relying on any single one:

1. **SIPRI Arms Transfers Database** — used both for its "local production" flag and, experimentally, for temporal co-occurrence between a platform's delivery years and other imports in the same period.
2. **Official export-control records** (US DSCA Major Arms Sales notifications, German *Rüstungsexportbericht*) — used where SIPRI coverage is thin or below its reporting threshold.
3. **Secondary/open-source literature** — principally Egeli, Güvenç, Kurç & Mevlütoğlu (2024), *"From Client to Competitor: The Rise of Türkiye's Defence Industry,"* IISS/CFPPR, and manufacturer/press reporting (company press releases, Naval News, Defence Turkey, Jamestown Foundation, etc.).

**A conceptual distinction worth stating explicitly:** this dataset tracks *component/subsystem dependency* — which foreign part or supplier a platform currently sources from. A separate, related form of dependency is not separately coded: *platform-origin export-control dependency*, the veto power an origin country retains over a platform's use, transfer, or modification by virtue of having supplied the base design, type certificate, or a component subject to its own export-control regime, independent of how much local production value has since been added. Germany's 2016–2021 arms embargo cutting off the Altay tank's original MTU/RENK powerpack, and the persistent US export-control interest implicit in third-country F-4E modernization programmes, both illustrate this second, distinct form of dependency.

**A methodological result worth flagging on its own:** an early version of this project tried to establish supplier links purely statistically — matching a platform's delivery year against other imports arriving in the same window. Run end-to-end against the 36 SIPRI-flagged "local production" designs (script and full write-up in [`criticality_matrix/README.md`](criticality_matrix/README.md)), this heuristic returns a candidate subsystem match for 36 of 36 (100%) — i.e., it fails to discriminate at all. That negative result is treated as a finding in its own right: temporal co-occurrence alone is not usable evidence for platform–subsystem linkage in this dataset, and every dependency claim in the underlying dataset is now instead confirmed through the multi-source process above, with unconfirmed cases explicitly labelled as such rather than silently dropped or asserted.

## Current coverage (interim)

Across 141 locally-produced/procured designs identified so far (from SIPRI's local-production flag, 1950–2025, combined with IISS/CFPPR's 1982–2022 procurement tables):

- **141 (100%)** are corroborated by two or more independent, named sources.

## Data note

The full working dataset (spreadsheet-level dependency table, per-row source citations, illustrative findings, and rows still pending verification) is kept private while the research is ongoing, since it mixes confirmed and unconfirmed claims and represents unpublished analysis. This document summarizes the method and headline coverage only. Code for the SIPRI temporal-matching script, the DSCA/German export scrapers, and the news-scraping/deduplication pipeline is in this repository (see `README.md`).

## Next steps

- Two-source verification is now complete across the dataset; remaining work shifts to depth rather than coverage.
- Extend the dependency-evolution mapping (off-the-shelf → licensed production → indigenous, and cases where dependency reappears at a later stage) systematically across the full dataset.
- Build out the criticality-scoring layer (functional necessity × export restriction × substitution availability) as a distinct next phase, now that the underlying dependency mapping is complete.
