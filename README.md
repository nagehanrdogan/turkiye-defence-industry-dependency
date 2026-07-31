# Türkiye Defence Industry: Component-Level Dependency Analysis

**Ongoing PhD dissertation fieldwork · NLP / text-as-data**

This repository is the empirical work behind one strand of a broader research programme on defence-industry development in late-industrialising states, using Türkiye as the case. The specific question here: SIPRI's Arms Transfers Database flags a platform as "local production," but doesn't say which foreign subsystems (engines, sensors, naval weapons, etc.) that local production actually depends on. This project maps that dependency, across four core platforms (Altay tank, T129 ATAK, Hisar air-defence, TAI KAAN) and a wider set of historical Turkish procurement, and is building toward a criticality matrix (functional necessity × export restriction × substitution availability) over that mapping.

**This is active fieldwork, not a finished dataset.** See [`FINDINGS.md`](FINDINGS.md) for current interim results and [`research-log.md`](research-log.md) for a dated, granular log of each verification pass.

## What's here

**`news_pipeline/`** — an automated Turkish-language news scraping and deduplication pipeline (530+ articles across the four platforms), with BERTopic topic modelling used to surface which platforms/themes (embargo mentions, indigenous-substitute development, supplier-agreement news) are most prominent in press coverage. Includes both the production scripts and the original pilot/multi-platform notebooks.

**`criticality_matrix/`** — the core dependency-mapping work: an initial purely-statistical approach (SIPRI temporal co-occurrence matching) that was tested, found to have no discriminating power, and documented as a negative result; and the multi-source triangulation method that replaced it. See [`criticality_matrix/README.md`](criticality_matrix/README.md) for the full writeup, including the code and the reproducible negative-result numbers. Nested subsystem chains (a platform depending on several foreign suppliers at once) and platform-evolution-over-time (e.g. off-the-shelf → licensed production) are the current active threads.

**`external_validation/`** — scrapers for US DSCA Major Arms Sales notifications and German *Rüstungsexportbericht* (2014–2024), used to independently corroborate dependency claims that fall outside or below SIPRI's coverage.

**`budget_crossvalidation/`** — a secondary, largely-complete piece of work: Turkish official defence-budget-law figures merged with Muhasebat (Treasury) realised-expenditure statistics into one tidy dataset, for cross-validation against SIPRI's Military Expenditure Database.

## Method summary

Every dependency claim is checked against independent, named sources rather than accepted from any single one — see [`criticality_matrix/README.md`](criticality_matrix/README.md) for the full method and [`FINDINGS.md`](FINDINGS.md) for what's confirmed so far. In short: SIPRI's own data plus its Supplier/Recipient re-export matching, US/German official export-control records, IISS/CFPPR's compiled procurement history, and manufacturer/press reporting, each explicitly labelled by which of these established it — including cases that were checked and remain unconfirmed.

## Data note

Raw and processed data files (`.csv`, `.xlsx`, `.pdf`) are intentionally excluded from this repository via `.gitignore` — only code, notebooks, and methodology are shared here, since the underlying working dataset mixes confirmed and unconfirmed claims. Data files stay local. See [`FINDINGS.md`](FINDINGS.md) for the subset of findings that are already sourced well enough to share.

## Setup

Each script's docstring documents its own `pip install` requirements (e.g. `pip install bertopic sentence-transformers umap-learn hdbscan` for the topic-modelling scripts, `pip install selenium webdriver-manager pdfplumber` for the DSCA scraper). Scripts are designed to be run from within their own folder (input/output paths are relative to that folder).
