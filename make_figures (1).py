"""Regenerate Figures 2 and 3 from the GRID agent-based model.

Run from the repository root alongside grid_abm.py:
    python3 make_figures.py

Outputs 600 dpi TIF (LZW) and PNG for each figure, sized to Springer's
174 mm double-column width.
"""

import math
import statistics as st

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

import grid_abm as g

N_REPS = 100
BASE_SEED = 1000
CONDITIONS = [("baseline", "Standard Baseline"),
              ("naive", "Naive AI"),
              ("grid", "GRID")]

# Semantic palette. Green (#D9EAD3 family) matches the paper's table headers and
# marks the condition that protects. Baseline is neutral grey, Naive AI charcoal.
# Red is reserved for the crisis threshold and used nowhere else.
COLOURS = {"baseline": "#8A8A90", "naive": "#2B2B2E", "grid": "#4E7A46"}
CRISIS_RED = "#B3261E"

MM = 1 / 25.4
WIDTH = 174 * MM

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 8,
    "axes.linewidth": 0.6,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
})


def trajectories(condition):
    """Per-tick stress for N_REPS replications, using the model's own seeding."""
    runs = []
    for i in range(N_REPS):
        sim = g.SimState(condition=condition)
        rng = g.make_rng(BASE_SEED + i)
        series = []
        for _ in range(g.TOTAL_TICKS):
            g.step_sim(sim, g.DEFAULT_PARAMS, rng)
            series.append(sim.stress)
        runs.append(series)
    return runs


def mean_and_ci(runs):
    mean, lo, hi = [], [], []
    for t in range(len(runs[0])):
        col = [r[t] for r in runs]
        m = st.mean(col)
        h = 1.96 * st.stdev(col) / math.sqrt(len(col))
        mean.append(m)
        lo.append(m - h)
        hi.append(m + h)
    return mean, lo, hi


def save(fig, stem):
    for ext, kw in (("tif", {"pil_kwargs": {"compression": "tiff_lzw"}}),
                    ("png", {})):
        fig.savefig(f"{stem}.{ext}", dpi=600, bbox_inches="tight", **kw)
    plt.close(fig)


def figure_two():
    fig, ax = plt.subplots(figsize=(WIDTH, WIDTH * 0.42))
    for cond, label in CONDITIONS:
        mean, lo, hi = mean_and_ci(trajectories(cond))
        ticks = range(len(mean))
        ax.fill_between(ticks, lo, hi, color=COLOURS[cond], alpha=0.18, linewidth=0)
        ax.plot(ticks, mean, color=COLOURS[cond], linewidth=1.1, label=label)

    ax.axhline(g.CRISIS_THRESHOLD, color=CRISIS_RED, linewidth=0.9,
               linestyle=(0, (4, 3)), zorder=1)
    ax.text(g.TOTAL_TICKS - 4, g.CRISIS_THRESHOLD + 0.018, "Crisis threshold",
            fontsize=7, color=CRISIS_RED, ha="right")

    for boundary in (72, 144, 216, 288):
        ax.axvline(boundary, color="#C8C8CC", linewidth=0.5, zorder=0)
    ax.set_xticks([36, 108, 180, 252, 324])
    ax.set_xticklabels(["Mon", "Tue", "Wed", "Thu", "Fri"])
    ax.set_xlim(0, g.TOTAL_TICKS)
    ax.set_ylim(0, 0.95)
    ax.yaxis.set_major_locator(MultipleLocator(0.2))
    ax.set_ylabel("Focal student stress")
    ax.legend(frameon=False, loc="upper left", handlelength=1.6)
    save(fig, "figure2_stress_trajectory")


def figure_three():
    results = {c: g.run_monte_carlo(c, g.DEFAULT_PARAMS, N_REPS, BASE_SEED)
               for c, _ in CONDITIONS}

    panels = [
        ("Crisis rate (%)", lambda r: 100 * sum(x["crisis"] for x in r) / len(r), None),
        ("Governance Health", lambda r: st.mean(x["governance_health"] for x in r),
         "governance_health"),
        ("Logs per week", lambda r: st.mean(x["total_logs"] for x in r), "total_logs"),
        ("Classified signals", lambda r: st.mean(x["classified_signals"] for x in r),
         "classified_signals"),
    ]

    fig, axes = plt.subplots(1, 4, figsize=(WIDTH, WIDTH * 0.30))
    for ax, (title, fn, key) in zip(axes, panels):
        for i, (cond, label) in enumerate(CONDITIONS):
            r = results[cond]
            value = fn(r)
            err = None
            if key:
                col = [x[key] for x in r]
                err = 1.96 * st.stdev(col) / math.sqrt(len(col))
            ax.bar(i, value, color=COLOURS[cond], width=0.62,
                   yerr=err, capsize=2,
                   error_kw={"linewidth": 0.6, "capthick": 0.6})
        ax.set_title(title, fontsize=8, pad=6)
        ax.set_xticks(range(len(CONDITIONS)))
        ax.set_xticklabels([l for _, l in CONDITIONS], rotation=35,
                           ha="right", fontsize=7)
        ax.tick_params(axis="x", length=0)
    save(fig, "figure3_governance_outcomes")


FILLS = {"baseline": "#EFEFF1", "naive": "#E3E3E5", "grid": "#D9EAD3"}

PATHWAY = {
    "baseline": [
        "Narrative report.\nRecording probability falls\nsteeply with behavioural stage",
        "Classification depends on the\nindividual observer's\nCPI training",
        "Sparse, largely unclassified\nsignal reaches the DSL.\nNo pattern above classroom level",
        "Crisis in 100 of 100\nFriday trigger, tick 308",
    ],
    "naive": [
        "Narrative report.\nMarginally higher recording\nof low-stage events",
        "Observed anxiety and defensive\nstates counted as unclassified\nconcerns, recorded or not",
        "Room-wide threat alert at 8\nconcerns. Staff defensive\nstance held at 0.85",
        "Crisis in 100 of 100\nmedian tick 68",
    ],
    "grid": [
        "Structured selection.\nRecording floor 0.5 + 0.5d,\nindependent of staff load",
        "Classification by behavioural\nstage, independent of the\nobserver's training",
        "Behavioural Lead at 4 classified\nsignals. DSL and low-arousal\nprotocol at 8",
        "Crisis in 0 of 100\nFriday event neutralised",
    ],
}

ROW_LABELS = ["Record", "Classify", "Route", "Outcome"]
ROW_Y = [(59, 72), (44, 56), (27, 41), (11, 23)]


def box(ax, x0, x1, y0, y1, text, edge, fill, weight="normal", size=6.2):
    ax.add_patch(plt.Rectangle((x0, y0), x1 - x0, y1 - y0, facecolor=fill,
                               edgecolor=edge, linewidth=0.7, zorder=2))
    ax.text((x0 + x1) / 2, (y0 + y1) / 2, text, ha="center", va="center",
            fontsize=size, color="#1A1A1A", fontweight=weight,
            linespacing=1.45, zorder=3)


def arrow(ax, x_from, y_from, x_to, y_to, colour):
    ax.annotate("", xy=(x_to, y_to), xytext=(x_from, y_from),
                arrowprops=dict(arrowstyle="-|>", color=colour, linewidth=0.7,
                                shrinkA=0, shrinkB=0, mutation_scale=7))


def figure_one():
    fig, ax = plt.subplots(figsize=(WIDTH, WIDTH * 0.70))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    cols = {"baseline": (2, 31), "naive": (35.5, 64.5), "grid": (69, 98)}

    box(ax, 2, 98, 90, 98,
        "Safeguarding event\nthe behaviour  ·  the physical intervention it requires  ·  "
        "the practitioner's reading of why",
        "#1A1A1A", "#FFFFFF", size=6.8)

    box(ax, 2, 98, 79, 87,
        "Observation by staff\nP(observe) = (1 \u2212 0.65w)(0.7a + 0.3)\u03bb, "
        "identical across all three conditions",
        "#1A1A1A", "#FFFFFF", size=6.8)

    arrow(ax, 50, 90, 50, 87, "#1A1A1A")

    for cond, label in CONDITIONS:
        x0, x1 = cols[cond]
        centre = (x0 + x1) / 2
        colour, fill = COLOURS[cond], FILLS[cond]

        ax.text(centre, 75.5, label, ha="center", va="center", fontsize=7.6,
                fontweight="bold", color=colour)
        arrow(ax, centre, 79, centre, 73.4, colour)

        for i, ((y0, y1), text) in enumerate(zip(ROW_Y, PATHWAY[cond])):
            last = i == len(ROW_Y) - 1
            box(ax, x0, x1, y0, y1, text, colour,
                "#F3F7F0" if (last and cond == "grid") else fill,
                weight="bold" if last else "normal",
                size=6.4 if last else 6.2)
            if i:
                arrow(ax, centre, ROW_Y[i - 1][0], centre, y1, colour)

    for (y0, y1), label in zip(ROW_Y, ROW_LABELS):
        ax.text(0.4, (y0 + y1) / 2, label, ha="left", va="center", fontsize=6.4,
                color="#6E6E73", rotation=90)

    save(fig, "figure1_signal_pathway")


if __name__ == "__main__":
    figure_one()
    figure_two()
    figure_three()
    print("Figures written.")
