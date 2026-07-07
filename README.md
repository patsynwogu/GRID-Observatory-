# GRID Observatory

Computational governance framework for AI deployment in specialist SEND (Special Educational Needs and Disabilities) schools, stress-tested via agent-based simulation.

GRID (Governance Risk and Infrastructure Diagnostics) addresses a structural safeguarding gap: non-verbal autistic learners cannot self-report distress, so their safety depends entirely on whether trained staff observe, record, and escalate behavioural signals before a crisis occurs. This repository contains two faithful implementations of the same underlying model, built for two different purposes.

## What's in this repository

**`index.html`** — an interactive, browser-based visualisation of the model. Built for non-technical stakeholders (head teachers, Designated Safeguarding Leads, Behavioural Leads) to directly explore how three governance architectures behave under adjustable operational conditions, in real time, without needing to read code or statistics first. Each play-through is a single deterministic run, not a statistical study in itself; a "Show 100-replication results" panel reads and displays the real output of `grid_abm.py` (below) alongside the live run, so the same numbers reported in the paper are visible directly in the dashboard. Live at [grid-simulation.netlify.app](https://grid-simulation.netlify.app).

**`grid_abm.py`** — a headless Python implementation of the same per-tick step logic, designed to run real Monte Carlo batches (100 replications per condition) and produce the statistical results reported in the accompanying paper, *The Mathematics of Safeguarding: An Agent-Based Simulation of AI Governance Compliance in Specialist SEND Schools*. This file, not the interactive dashboard, is the source of all quantitative claims in that paper.

**`full_stats.json`** and **`grid_summary.csv`** — output of the most recent 100-replication run of `grid_abm.py`: summary statistics with 95% confidence intervals, and per-replication raw results, respectively.

## The three governance conditions modelled

- **Standard Baseline** — narrative-only reporting, no computational support. Documentation is suppressed under workload pressure, leaving the institutional record sparse before any precipitating event.
- **Naive AI** — automated pattern-detection that broadcasts a room-wide threat alert once unclassified concerns cross a threshold. This elevates staff defensive posture, which transmits to the focal student and can independently produce the crisis it was deployed to prevent.
- **GRID** — structured, CPI-aligned observation capture that lowers documentation friction and routes targeted, classified signals to the Designated Safeguarding Lead or Behavioural Lead before a crisis threshold is crossed.

## Running the simulation

```bash
python3 grid_abm.py
```

Requires Python 3.8+, no external dependencies. Running the script executes 100 Monte Carlo replications per condition and regenerates `full_stats.json` and `grid_summary.csv`.

 grid_sensitivity.py sweeps each operational variable while holding the others at default, for all three conditions, and reproduces the CPI-coverage result in Section 3.2 (GRID: 29/100 crises at coverage 0.1, 4/100 at 0.3, 0/100 at 0.5 and above)

## Relationship to the published paper

Statistical results reported in the paper's Results section are generated exclusively by `grid_abm.py`. The interactive dashboard (`index.html`) implements the same step logic for live demonstration, and separately displays — but does not compute — the pre-generated results from `full_stats.json` via its "Show 100-replication results" panel. The dashboard is a viewer of those results, not their source. All simulation inputs and outputs are synthetic; no real student, staff, or school data is used or stored in any artefact in this repository.

## Author

Patsy Nwogu — Independent Researcher, Computational Governance and AI Policy.
