# GRID Observatory

Computational governance framework for AI deployment in specialist SEND (Special Educational Needs and Disabilities) schools, stress-tested via agent-based simulation.

GRID (Governance Risk and Infrastructure Diagnostics) addresses a structural safeguarding gap: non-verbal autistic learners cannot self-report distress, so their safety depends entirely on whether trained staff observe, record, and escalate behavioural signals before a crisis occurs. This repository contains two faithful implementations of the same underlying model, built for two different purposes, together with the scripts that produce the reported statistics and figures.

## What's in this repository

**`grid_abm.py`** — the headless Python implementation. It runs 100 Monte Carlo replications per governance condition and produces every quantitative claim in the accompanying paper. Replications are seeded deterministically as `base_seed + i` with `base_seed = 1000`, so any reported run can be reproduced exactly.

**`index.html`** — an interactive, browser-based visualisation implementing the same per-tick step logic, built for non-technical stakeholders to explore how the three governance architectures behave under adjustable operational conditions. Each play-through is a single deterministic run, not a statistical study. A "Show 100-replication results" panel reads and displays the output of `grid_abm.py` alongside the live run, so the numbers reported in the paper are visible in the dashboard. Live at [grid-simulation.netlify.app](https://grid-simulation.netlify.app).

**`grid_sensitivity.py`** and **`grid_sensitivity.csv`** — a one-at-a-time sweep of each operational variable, holding the others at default, across all three conditions.

**`make_figures.py`** — regenerates all three figures in the paper directly from the model. Requires matplotlib.

**`full_stats.json`** and **`grid_summary.csv`** — output of the most recent 100-replication run: summary statistics with 95% confidence intervals, and per-replication raw results.

## The three governance conditions modelled

- **Standard Baseline** — narrative-only reporting, no computational support. Recording probability falls steeply with behavioural stage, leaving the institutional record sparse before any precipitating event.
- **Naive AI** — automated pattern-detection that broadcasts a room-wide threat alert once unclassified concerns cross a threshold. This elevates staff defensive posture, which transmits to the focal student and can independently produce the crisis it was deployed to prevent.
- **GRID** — structured, CPI-aligned observation capture that lowers documentation friction and routes classified signals to the Behavioural Lead and the Designated Safeguarding Lead before a crisis threshold is crossed.

## Running the simulation

```bash
python3 grid_abm.py          # 100 replications per condition; writes full_stats.json and grid_summary.csv
python3 grid_sensitivity.py  # one-at-a-time sweep; writes grid_sensitivity.csv
python3 make_figures.py      # regenerates Figures 1-3 as TIF and PNG
```

`grid_abm.py` and `grid_sensitivity.py` require Python 3.8+ with no external dependencies. `make_figures.py` additionally requires matplotlib.

## Model parameters

The stress decay parameter is 0.85. An initial value of 0.93 was rejected during verification because it produced a steady-state stress above the crisis threshold under default conditions, independent of governance condition. Any deposit or output generated before that correction is superseded by the current code.

## Relationship to the paper

Statistical results in the paper's Results section are generated exclusively by `grid_abm.py`. The dashboard implements the same step logic for live demonstration and separately displays, but does not compute, the pre-generated results. All simulation inputs and outputs are synthetic; no real student, staff, or school data is used or stored in any artefact in this repository.
