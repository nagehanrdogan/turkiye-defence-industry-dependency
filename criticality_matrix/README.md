# Criticality matrix: platform–component dependency

This folder holds the SIPRI-side analysis for the broader dependency-mapping project (see the [repo README](../README.md)). It documents both a method that was tried and rejected, and the method that replaced it — the negative result is treated as a finding in its own right, not hidden.

## Step 1: a purely statistical test (and why it doesn't work)

[`platform_component_dependency.py`](platform_component_dependency.py) implements a simple hypothesis: if a locally-produced platform ("Local production: Yes" in SIPRI) is delivered around the same time as a subsystem import (engines, sensors, naval weapons, etc.) from a *different* supplier country, treat that as a **candidate** dependency link.

Running it against Turkiye's SIPRI Trade Register data (±2-year matching window):

```
Local-production platform deliveries: 172 (36 unique designs)
Subsystem imports (Engines/Sensors/Naval weapons/Other): 255
Candidate matches produced: 6,380
Unique designs with ≥1 candidate match: 36 / 36 (100%)
```

Every single locally-produced design matched to at least one subsystem import within the window. That is not a finding about Turkish supply chains — it is a finding about the test: at this match rate, temporal co-occurrence has no discriminating power. SIPRI's transfer records don't contain an explicit "this engine went into this platform" field, so proximity in time is all a purely statistical approach has to work with, and in a dataset with hundreds of transfers per country per decade, almost everything is "close in time" to almost everything else.

This is why the script's own output flags every match as unverified (`Match_Confidence`: "Orta (kategori uyumlu)" at best, based only on a plausible-category heuristic — e.g. Aircraft↔Engines — never as confirmed), and ships a blank `To_Verify_External` template rather than presenting any match as established.

## Step 2: what replaced it — multi-source triangulation

Instead of relying on statistical proximity, each dependency claim is now checked against independent, named sources:

1. **SIPRI's own "Local production" flag** — which designs to look at, and (via its Supplier/Recipient row-matching, used differently from the temporal test above) confirmed re-export chains.
2. **Official export-control records** — US DSCA Major Arms Sales notifications, German *Rüstungsexportbericht* (2014–2024) — for chains below SIPRI's reporting threshold or outside its scope.
3. **IISS/CFPPR** (Egeli, Güvenç, Kurç & Mevlütoğlu, 2024, *"From Client to Competitor: The Rise of Türkiye's Defence Industry"*) — for platforms retained entirely for domestic use, which by definition never show up in an international-transfer database.
4. **Manufacturer and specialist-press reporting** (company statements, Naval News, Defence Turkey, Jane's-type sources) — used to confirm or reject specific claims.

Each dependency claim is labelled by how it was established, rather than presented uniformly:
- confirmed by 2+ independent sources,
- sourced from a single secondary report only (expected for domestic-only systems, not a data error — see below),
- or explicitly flagged as researched but inconclusive, rather than guessed at.

**Why single-sourcing happens structurally, not by omission:** a platform built solely for the Turkish military and never exported will not appear in SIPRI's international transfer records — that's the database's scope, not a gap in this project's search. For those cases, IISS/CFPPR is currently the only available compiled secondary source, and is cited as such rather than treated as independently corroborated.

## Current state

The working dependency table (verification status, per-claim sourcing, subsystem-chain detail) is kept private while still in progress — see [`../FINDINGS.md`](../FINDINGS.md) for the aggregate numbers and a handful of fully-sourced illustrative cases that are shareable now.

## Active / next

- **Subsystem chains (nested dependency):** several platforms map to *multiple* foreign component suppliers at once rather than one (e.g. a naval platform sourcing its gun, radar, engines and defensive systems from four different countries) — mapping this nested structure systematically, not just per-platform, is the current focus.
- **Platform evolution over time:** several platforms shift acquisition mode over their lifecycle — e.g. an off-the-shelf purchase later replaced by licensed local production of the same design, or the reverse (a system initially recorded with no foreign supplier later acquiring one at an upgrade stage). Mapping these trajectories, not just point-in-time snapshots, is the other active thread.
- Extending verification coverage further back in time (SIPRI's transfer data goes back to 1950; this project's pull initially covered only 1995–2025 and has since been extended to close that gap).
