"""
GRID Observatory - one-at-a-time sensitivity analysis

Sweeps each of the five operational variables across its range while holding
the others at their default values, for all three governance conditions, and
reports crisis rate, Governance Health, total logs, and classified signals at
each point.

This script imports grid_abm.py unchanged and calls its Monte Carlo harness.
It assumes nothing in advance. Whatever it prints is what should be reported.
If a draft claim does not match this output, the draft is wrong.

The sweep that Section 3.2 of the paper cites is the CPI-coverage sweep under
the GRID condition. It shows that GRID's crisis elimination is conditional on
training coverage clearing a floor: at the modelled coverage GRID produces
0 crises in 100 replications, and as coverage falls the crisis count rises,
which is the multiplicative structure (a low A term dragging the product down)
made visible inside the simulation.

Usage:
    python grid_sensitivity.py

Outputs:
    - a table printed to stdout
    - grid_sensitivity.csv written next to this script
"""

import csv
import os

from grid_abm import (
    run_monte_carlo,
    summarize,
    DEFAULT_PARAMS,
)

N_REPLICATIONS = 100
BASE_SEED = 1000
CONDITIONS = ["baseline", "naive", "grid"]

# The five operational variables and the values each is swept across.
# workload, cpi, doc, env are the four sliders in DEFAULT_PARAMS. The fifth
# operational variable in the paper's framing is the structured observational
# recording rate, which is an outcome of the condition rather than an input
# slider, so it is not swept here; it is reported as total logs at each point.
SWEEPS = {
    "workload": [0.30, 0.50, 0.75, 0.95],
    "cpi": [0.10, 0.30, 0.50, 0.70, 0.90],
    "doc": [0.10, 0.25, 0.50, 0.90],
    "env": [0.20, 0.45, 0.70, 0.90],
}


def run_point(condition, variable, value):
    """Run one Monte Carlo batch with a single variable overridden."""
    params = dict(DEFAULT_PARAMS)
    params[variable] = value
    results = run_monte_carlo(
        condition, params, N_REPLICATIONS, base_seed=BASE_SEED
    )
    summary = summarize(results, f"{condition}:{variable}={value}")
    return {
        "condition": condition,
        "variable": variable,
        "value": value,
        "crisis_count": summary["crisis_count"],
        "crisis_rate": summary["crisis_rate"],
        "governance_health": summary["governance_health_mean"],
        "total_logs": summary["total_logs_mean"],
        "classified_signals": summary["classified_signals_mean"],
        "final_stress": summary["final_stress_mean"],
    }


def main():
    rows = []
    for variable, values in SWEEPS.items():
        for condition in CONDITIONS:
            for value in values:
                rows.append(run_point(condition, variable, value))

    # Print a readable table, grouped by variable then condition.
    header = (
        f"{'Variable':<10} {'Condition':<10} {'Value':<7} "
        f"{'Crisis':<9} {'Gov.Health':<11} {'Logs':<7} {'Classified':<11} {'Final stress'}"
    )
    print(header)
    print("-" * len(header))
    current_variable = None
    for row in rows:
        if row["variable"] != current_variable:
            if current_variable is not None:
                print()
            current_variable = row["variable"]
        print(
            f"{row['variable']:<10} {row['condition']:<10} {row['value']:<7} "
            f"{row['crisis_count']}/{N_REPLICATIONS:<5} "
            f"{row['governance_health']:<11.1f} "
            f"{row['total_logs']:<7.1f} "
            f"{row['classified_signals']:<11.1f} "
            f"{row['final_stress']:.3f}"
        )

    # Highlight the sweep Section 3.2 cites.
    print()
    print("=" * len(header))
    print("Section 3.2 reference sweep: CPI coverage under GRID")
    print("=" * len(header))
    print(f"{'CPI coverage':<14} {'Crisis rate':<14} {'Classified signals'}")
    for row in rows:
        if row["variable"] == "cpi" and row["condition"] == "grid":
            print(
                f"{row['value']:<14} "
                f"{row['crisis_count']}/{N_REPLICATIONS} "
                f"({row['crisis_rate']*100:.0f}%)".ljust(14)
                + f" {row['classified_signals']:.1f}"
            )

    # Write CSV next to this script.
    out_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(out_dir, "grid_sensitivity.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "variable",
                "condition",
                "value",
                "crisis_count",
                "crisis_rate",
                "governance_health_mean",
                "total_logs_mean",
                "classified_signals_mean",
                "final_stress_mean",
            ]
        )
        for row in rows:
            writer.writerow(
                [
                    row["variable"],
                    row["condition"],
                    row["value"],
                    row["crisis_count"],
                    f"{row['crisis_rate']:.4f}",
                    f"{row['governance_health']:.2f}",
                    f"{row['total_logs']:.2f}",
                    f"{row['classified_signals']:.2f}",
                    f"{row['final_stress']:.4f}",
                ]
            )

    print()
    print(f"Wrote {csv_path}")


if __name__ == "__main__":
    main()
