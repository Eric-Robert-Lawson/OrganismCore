"""
EUMODIC ELF-Thigmotaxis Correlation
=====================================
Computes center-level median periphery
permanence time (thigmotaxis measure)
for C57BL/6N wildtype controls and runs
Spearman correlation against ELF scores.

Also runs:
  - Leave-one-out sensitivity analysis
  - Within-center DR23 comparison
    (HMGU, ICS, MRC Harwell)
  - Observed vs predicted rank comparison
  - Secondary outcome: centre permanence
    time (inverse consistency check)

Reads:
  eumodic_raw.csv
  eumodic_elf_scores.csv
  eumodic_strain_decision.csv

Writes:
  eumodic_correlation_results.txt
  eumodic_center_summary.csv
  eumodic_correlation.png

OrganismCore — IMPC Series
EUMODIC Replication Analysis
February 2026
"""

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────

IN_RAW      = "eumodic_raw.csv"
IN_ELF      = "eumodic_elf_scores.csv"
IN_DEC      = "eumodic_strain_decision.csv"
OUT_TXT     = "eumodic_correlation_results.txt"
OUT_CSV     = "eumodic_center_summary.csv"
OUT_FIG     = "eumodic_correlation.png"

PERIPHERY_PARAM = "Periphery permanence time"
CENTRE_PARAM    = "Centre permanence time"

# DR23 results for within-center
# comparison — median periphery time
# (seconds) per center from DR23
# primary analysis
DR23_MEDIANS = {
    "HMGU":        1842.6,
    "ICS":          987.3,
    "MRC Harwell": 1243.1,
}

# DR23 primary correlation result
# for reference
DR23_SPEARMAN_R = -0.775
DR23_SPEARMAN_P =  0.0408
DR23_N_CENTERS  =  7

# C57BL/6N strain strings
B6N_STRINGS = [
    "C57BL/6N",
    "C57BL/6NTac",
    "C57BL/6NTacDen",
    "C57BL/6NTac-ICS-Denmark(ImportedLive)",
    "C57BL/6NTac-ICS-USA(ImportedLive)",
    "C57BL/6NCrl",
    "C57BL/6NJ",
]

# Pre-registered predicted rank order
# 1 = highest thigmotaxis
PREDICTED_RANKS = {
    "CMHD":        1,
    "HMGU":        2,
    "MRC Harwell": 3,
    "ICS":         4,
    "WTSI":        5,
}

results = []

def log(s=""):
    results.append(s)
    print(s)

# ─────────────────────────────────────────
# LOAD
# ────────────────────���────────────────────

log("=" * 56)
log("EUMODIC ELF-THIGMOTAXIS CORRELATION")
log("=" * 56)
log()

df  = pd.read_csv(IN_RAW,  low_memory=False)
elf = pd.read_csv(IN_ELF)
dec = pd.read_csv(IN_DEC)

log(f"Raw records loaded:    {len(df):,}")
log(f"ELF centers:           {len(elf)}")
log()

# ─────────────────────────────────────────
# FILTER: C57BL/6N STRICT PER CENTER
# Uses strain_rule from decision file
# ─────────────────────────────────────────

strict_centers = dec[
    dec["strain_rule"] == "STRICT_B6N"
]["center"].tolist()

log(
    f"Centers using STRICT_B6N rule: "
    f"{len(strict_centers)}"
)
for c in strict_centers:
    log(f"  {c}")
log()

# Filter to strict B6N for strict centers
b6n_mask = df["strain_name"].isin(
    B6N_STRINGS
)
center_mask = df[
    "phenotyping_center"
].isin(strict_centers)

df_strict = df[
    b6n_mask & center_mask
].copy()

log(
    f"Records after B6N strict filter: "
    f"{len(df_strict):,}"
)
log()

# ─────────────────────────────────────────
# SPLIT BY PARAMETER
# ─────────────────────────────────────────

df_periphery = df_strict[
    df_strict["parameter_name"]
    == PERIPHERY_PARAM
].copy()

df_centre = df_strict[
    df_strict["parameter_name"]
    == CENTRE_PARAM
].copy()

log(
    f"Periphery permanence records: "
    f"{len(df_periphery):,}"
)
log(
    f"Centre permanence records:    "
    f"{len(df_centre):,}"
)
log()

# ─────────────────────────────────────────
# NUMERIC CONVERSION
# ─────────────────────────────────────────

for df_tmp in [df_periphery, df_centre]:
    df_tmp["value"] = pd.to_numeric(
        df_tmp["data_point"],
        errors="coerce"
    )

# ─────────────────────────────────────────
# CENTER-LEVEL MEDIANS
# ─────────────────────────────────────────

log("=" * 56)
log("CENTER-LEVEL MEDIANS")
log("=" * 56)
log()

peri_medians = (
    df_periphery
    .groupby("phenotyping_center")["value"]
    .agg(["median", "mean", "std", "count"])
    .reset_index()
    .rename(columns={
        "phenotyping_center": "center",
        "median": "peri_median",
        "mean":   "peri_mean",
        "std":    "peri_std",
        "count":  "peri_n",
    })
)

ctr_medians = (
    df_centre
    .groupby("phenotyping_center")["value"]
    .agg(["median", "count"])
    .reset_index()
    .rename(columns={
        "phenotyping_center": "center",
        "median": "ctr_median",
        "count":  "ctr_n",
    })
)

# Merge with ELF scores
summary = peri_medians.merge(
    ctr_medians, on="center", how="left"
)
summary = summary.merge(
    elf[["center", "elf_score", "source"]],
    on="center"
)
summary = summary.sort_values(
    "elf_score", ascending=False
).reset_index(drop=True)

# Add predicted rank
summary["predicted_rank"] = summary[
    "center"
].map(PREDICTED_RANKS)

# Add observed rank
summary["observed_rank"] = summary[
    "peri_median"
].rank(ascending=False).astype(int)

log(
    f"{'Center':<14} "
    f"{'ELF':>5} "
    f"{'Peri_med':>9} "
    f"{'Peri_n':>7} "
    f"{'Ctr_med':>8} "
    f"{'Pred_rank':>10} "
    f"{'Obs_rank':>9}"
)
log("-" * 70)

for _, row in summary.iterrows():
    ctr_med = (
        f"{row['ctr_median']:>8.1f}"
        if pd.notna(row.get("ctr_median"))
        else "     N/A"
    )
    log(
        f"{row['center']:<14} "
        f"{row['elf_score']:>5.0f} "
        f"{row['peri_median']:>9.1f} "
        f"{int(row['peri_n']):>7,} "
        f"{ctr_med} "
        f"{int(row['predicted_rank']):>10} "
        f"{int(row['observed_rank']):>9}"
    )

log()

# ─────────────────────────────────────────
# PRIMARY SPEARMAN CORRELATION
# ELF score vs median periphery time
# ─────────────────────────────────────────

log("=" * 56)
log("PRIMARY SPEARMAN CORRELATION")
log("ELF score vs periphery permanence")
log("time — C57BL/6N strict")
log("=" * 56)
log()

elf_vals  = summary["elf_score"].values
peri_vals = summary["peri_median"].values

r, p = stats.spearmanr(elf_vals, peri_vals)
n = len(summary)

log(f"N centers:     {n}")
log(f"Spearman r:    {r:+.4f}")
log(f"p-value:       {p:.4f}")
log()

if p < 0.001:
    sig = "p < 0.001 — HIGHLY SIGNIFICANT"
elif p < 0.01:
    sig = "p < 0.01  — SIGNIFICANT"
elif p < 0.05:
    sig = "p < 0.05  — SIGNIFICANT"
elif p < 0.10:
    sig = "p < 0.10  — TREND"
else:
    sig = "p >= 0.10 — NOT SIGNIFICANT"

log(f"Result: {sig}")
log()

if r < 0:
    direction = (
        "CONSISTENT with coherence "
        "hypothesis: higher ELF -> "
        "higher thigmotaxis."
    )
elif r > 0:
    direction = (
        "INCONSISTENT with coherence "
        "hypothesis: higher ELF -> "
        "lower thigmotaxis."
    )
else:
    direction = "No association detected."

log(f"Direction: {direction}")
log()

# DR23 comparison
log("DR23 primary result (reference):")
log(f"  r = {DR23_SPEARMAN_R:+.3f}")
log(f"  p = {DR23_SPEARMAN_P:.4f}")
log(f"  N = {DR23_N_CENTERS} centers")
log()

# ─────────────────────────────────────────
# PREDICTED VS OBSERVED RANK COMPARISON
# ─────────────────────────────────────────

log("=" * 56)
log("PREDICTED VS OBSERVED RANK")
log("=" * 56)
log()
log(
    f"{'Center':<14} "
    f"{'Predicted':>10} "
    f"{'Observed':>9} "
    f"{'Match':>6}"
)
log("-" * 44)

rank_matches = 0
for _, row in summary.sort_values(
    "predicted_rank"
).iterrows():
    pred = int(row["predicted_rank"])
    obs  = int(row["observed_rank"])
    match = "YES" if pred == obs else "NO"
    if pred == obs:
        rank_matches += 1
    log(
        f"{row['center']:<14} "
        f"{pred:>10} "
        f"{obs:>9} "
        f"{match:>6}"
    )

log()
log(
    f"Exact rank matches: "
    f"{rank_matches} / {n}"
)

# Rank correlation
r_rank, p_rank = stats.spearmanr(
    summary["predicted_rank"].values,
    summary["observed_rank"].values
)
log(
    f"Predicted/observed rank "
    f"correlation: r = {r_rank:+.4f}, "
    f"p = {p_rank:.4f}"
)
log()

# ─────────────────────────────────────────
# LEAVE-ONE-OUT SENSITIVITY
# ─────────────────────────────────────────

log("=" * 56)
log("LEAVE-ONE-OUT SENSITIVITY")
log("=" * 56)
log()
log(
    f"{'Left out':<14} "
    f"{'r':>8} "
    f"{'p':>8} "
    f"{'N':>4} "
    f"Sig"
)
log("-" * 50)

loo_rows = []
for i, row in summary.iterrows():
    left_out = row["center"]
    sub = summary[
        summary["center"] != left_out
    ]
    if len(sub) < 3:
        continue
    r_l, p_l = stats.spearmanr(
        sub["elf_score"].values,
        sub["peri_median"].values
    )
    if p_l < 0.05:
        s = "*"
    elif p_l < 0.10:
        s = "."
    else:
        s = "ns"
    log(
        f"{left_out:<14} "
        f"{r_l:>+8.4f} "
        f"{p_l:>8.4f} "
        f"{len(sub):>4} "
        f"{s}"
    )
    loo_rows.append({
        "left_out": left_out,
        "r": r_l,
        "p": p_l,
        "n": len(sub),
        "sig": s,
    })

log()
n_sig_loo = sum(
    1 for x in loo_rows
    if x["sig"] != "ns"
)
log(
    f"LOO results remaining significant "
    f"or trend: {n_sig_loo} / {len(loo_rows)}"
)
log()

# ─────────────────────────────────────────
# WITHIN-CENTER DR23 COMPARISON
# ─────────────────────────────────────────

log("=" * 56)
log("WITHIN-CENTER DR23 COMPARISON")
log("Overlapping centers: HMGU, ICS,")
log("MRC Harwell")
log("=" * 56)
log()
log(
    f"{'Center':<14} "
    f"{'DR23_med':>9} "
    f"{'EUMOD_med':>10} "
    f"{'Diff':>8} "
    f"{'DR23_rank':>10} "
    f"{'EUMOD_rank':>11}"
)
log("-" * 68)

# DR23 ranks among the 3 overlapping
# centers only
dr23_overlap = {
    c: v for c, v in DR23_MEDIANS.items()
}
dr23_rank = {
    c: r+1 for r, (c, v) in enumerate(
        sorted(
            dr23_overlap.items(),
            key=lambda x: x[1],
            reverse=True
        )
    )
}

overlap_centers = [
    "HMGU", "ICS", "MRC Harwell"
]
within_rows = []

for center in overlap_centers:
    dr23_med = DR23_MEDIANS.get(center)
    row = summary[
        summary["center"] == center
    ]
    if row.empty or dr23_med is None:
        continue
    eumod_med = row["peri_median"].iloc[0]
    diff = eumod_med - dr23_med
    dr23_r = dr23_rank.get(center, "?")

    # EUMODIC rank among overlap only
    eumod_overlap = summary[
        summary["center"].isin(
            overlap_centers
        )
    ].copy()
    eumod_overlap["overlap_rank"] = (
        eumod_overlap["peri_median"]
        .rank(ascending=False)
        .astype(int)
    )
    eumod_r = eumod_overlap[
        eumod_overlap["center"] == center
    ]["overlap_rank"].iloc[0]

    log(
        f"{center:<14} "
        f"{dr23_med:>9.1f} "
        f"{eumod_med:>10.1f} "
        f"{diff:>+8.1f} "
        f"{dr23_r:>10} "
        f"{int(eumod_r):>11}"
    )
    within_rows.append({
        "center":    center,
        "dr23_med":  dr23_med,
        "eumod_med": eumod_med,
        "diff":      diff,
        "dr23_rank": dr23_r,
        "eumod_rank": int(eumod_r),
        "rank_preserved": (
            dr23_r == int(eumod_r)
        ),
    })

log()
within_df = pd.DataFrame(within_rows)
if len(within_df):
    n_rank_preserved = within_df[
        "rank_preserved"
    ].sum()
    log(
        f"Rank order preserved: "
        f"{n_rank_preserved} / "
        f"{len(within_df)} centers"
    )
log()

# ─────────────────────────────────────────
# SECONDARY OUTCOME
# Centre permanence time
# Expect inverse of periphery
# ─────────────────────────────────────────

log("=" * 56)
log("SECONDARY OUTCOME")
log("Centre permanence time")
log("(expect inverse of periphery)")
log("=" * 56)
log()

ctr_vals = summary["ctr_median"].values
if not all(pd.isna(ctr_vals)):
    r_ctr, p_ctr = stats.spearmanr(
        elf_vals, ctr_vals
    )
    log(f"ELF vs centre time:")
    log(f"  Spearman r: {r_ctr:+.4f}")
    log(f"  p-value:    {p_ctr:.4f}")
    log()
    if r_ctr < 0 and r > 0:
        log(
            "Internal consistency: "
            "periphery and centre move "
            "in opposite directions "
            "as expected."
        )
    elif r_ctr > 0 and r < 0:
        log(
            "Internal consistency: "
            "periphery and centre move "
            "in opposite directions "
            "as expected."
        )
    else:
        log(
            "Note: periphery and centre "
            "do not show expected "
            "inverse relationship."
        )
    log()

# ─────────────────────────────────────────
# HONEST ASSESSMENT
# ─────────────────────────────────────────

log("=" * 56)
log("HONEST ASSESSMENT")
log("=" * 56)
log()
log("What this result establishes:")
log()

if p < 0.05 and r < 0:
    log(
        "  REPLICATION SUPPORTED."
    )
    log(
        "  The ELF-thigmotaxis correlation"
    )
    log(
        "  observed in DR23 (r=-0.775,"
    )
    log(
        "  p=0.04) replicates in an"
    )
    log(
        "  independent dataset collected"
    )
    log(
        "  under a different program,"
    )
    log(
        "  different procedure ID, and"
    )
    log(
        "  partially overlapping centers."
    )
elif p < 0.10 and r < 0:
    log(
        "  TREND TOWARD REPLICATION."
    )
    log(
        "  Direction consistent with DR23"
    )
    log(
        "  but does not reach p<0.05"
    )
    log(
        "  with N=5 centers."
    )
elif r > 0:
    log(
        "  REPLICATION NOT SUPPORTED."
    )
    log(
        "  Direction inconsistent with"
    )
    log(
        "  DR23 result and coherence"
    )
    log(
        "  hypothesis."
    )
else:
    log(
        "  NULL RESULT."
    )
    log(
        "  No significant association"
    )
    log(
        "  detected in EUMODIC dataset."
    )

log()
log("What this result does not establish:")
log()
log(
    "  Causation — observational data"
    " only."
)
log(
    "  Mechanism — ELF score is a"
    " proxy."
)
log(
    "  Generalizability beyond these"
    " centers."
)
log()
log(
    "Next step regardless of result:"
)
log(
    "  Faraday cage pre-registered"
    " experiment."
)
log()

# ─────────────────────────────────────────
# SAVE CSV
# ─────────────────────────────────────────

summary.to_csv(OUT_CSV, index=False)
log(f"Saved: {OUT_CSV}")
log()

# ─────────────────────────────────────────
# FIGURE
# ─────────────────────────────────────────

fig = plt.figure(
    figsize=(16, 10), dpi=120
)
fig.patch.set_facecolor("white")
gs = gridspec.GridSpec(
    2, 3, figure=fig,
    hspace=0.44, wspace=0.38
)

COLORS = {
    "CMHD":        "#d7191c",
    "HMGU":        "#f4a582",
    "MRC Harwell": "#878787",
    "ICS":         "#92c5de",
    "WTSI":        "#2166ac",
}

# ── Panel 1: Primary scatter ──────────
ax1 = fig.add_subplot(gs[0, :2])

for _, row in summary.iterrows():
    c = row["center"]
    ax1.scatter(
        row["elf_score"],
        row["peri_median"],
        color=COLORS.get(c, "#888888"),
        s=120, zorder=3,
        label=c
    )
    ax1.annotate(
        c,
        (row["elf_score"],
         row["peri_median"]),
        textcoords="offset points",
        xytext=(6, 4),
        fontsize=9
    )

# Trend line
z = np.polyfit(elf_vals, peri_vals, 1)
xf = np.linspace(
    min(elf_vals) - 5,
    max(elf_vals) + 5, 100
)
ax1.plot(
    xf, np.polyval(z, xf),
    "k--", alpha=0.4, lw=1.5
)

ax1.set_xlabel(
    "ELF Score (facility-level)",
    fontsize=10
)
ax1.set_ylabel(
    "Median Periphery Permanence Time (s)",
    fontsize=10
)
ax1.set_title(
    f"EUMODIC: ELF vs Thigmotaxis\n"
    f"Spearman r={r:+.3f}, p={p:.4f}, "
    f"N={n}",
    fontsize=11
)
ax1.grid(True, alpha=0.3)

# ── Panel 2: Predicted vs observed ───
ax2 = fig.add_subplot(gs[0, 2])

pred_ranks = summary[
    "predicted_rank"
].values
obs_ranks  = summary[
    "observed_rank"
].values

for i, row in summary.iterrows():
    c = row["center"]
    ax2.scatter(
        row["predicted_rank"],
        row["observed_rank"],
        color=COLORS.get(c, "#888888"),
        s=100, zorder=3
    )
    ax2.annotate(
        c,
        (row["predicted_rank"],
         row["observed_rank"]),
        textcoords="offset points",
        xytext=(4, 3),
        fontsize=8
    )

ax2.plot(
    [1, n], [1, n],
    "k--", alpha=0.4, lw=1.5,
    label="Perfect prediction"
)
ax2.set_xlabel(
    "Predicted rank", fontsize=10
)
ax2.set_ylabel(
    "Observed rank", fontsize=10
)
ax2.set_title(
    f"Predicted vs Observed Rank\n"
    f"r={r_rank:+.3f}, p={p_rank:.4f}",
    fontsize=11
)
ax2.set_xticks(range(1, n+1))
ax2.set_yticks(range(1, n+1))
ax2.grid(True, alpha=0.3)

# ── Panel 3: LOO sensitivity ──────────
ax3 = fig.add_subplot(gs[1, 0])

loo_df = pd.DataFrame(loo_rows)
colors_loo = [
    COLORS.get(c, "#888888")
    for c in loo_df["left_out"]
]
bars = ax3.bar(
    range(len(loo_df)),
    loo_df["r"].values,
    color=colors_loo,
    edgecolor="white"
)
ax3.axhline(
    0, color="black",
    linewidth=0.8, linestyle="-"
)
ax3.axhline(
    r, color="black",
    linewidth=1.2, linestyle="--",
    alpha=0.5, label=f"Full r={r:+.3f}"
)
ax3.set_xticks(range(len(loo_df)))
ax3.set_xticklabels(
    loo_df["left_out"].tolist(),
    rotation=30, ha="right",
    fontsize=8
)
ax3.set_ylabel("Spearman r", fontsize=10)
ax3.set_title(
    "Leave-One-Out Sensitivity",
    fontsize=11
)
ax3.legend(fontsize=8)
ax3.grid(True, alpha=0.3, axis="y")

# ── Panel 4: Within-center DR23 ───────
ax4 = fig.add_subplot(gs[1, 1])

if len(within_rows):
    wd = pd.DataFrame(within_rows)
    x  = np.arange(len(wd))
    w  = 0.35
    c_colors = [
        COLORS.get(c, "#888888")
        for c in wd["center"]
    ]
    ax4.bar(
        x - w/2,
        wd["dr23_med"].values,
        w, label="DR23",
        color=[
            plt.matplotlib.colors
            .to_rgba(c, 0.5)
            for c in c_colors
        ],
        edgecolor="white"
    )
    ax4.bar(
        x + w/2,
        wd["eumod_med"].values,
        w, label="EUMODIC",
        color=c_colors,
        edgecolor="white"
    )
    ax4.set_xticks(x)
    ax4.set_xticklabels(
        wd["center"].tolist(),
        rotation=20, ha="right",
        fontsize=9
    )
    ax4.set_ylabel(
        "Median Periphery Time (s)",
        fontsize=10
    )
    ax4.set_title(
        "Within-Center: DR23 vs EUMODIC",
        fontsize=11
    )
    ax4.legend(fontsize=9)
    ax4.grid(True, alpha=0.3, axis="y")

# ── Panel 5: Summary text ─────────────
ax5 = fig.add_subplot(gs[1, 2])
ax5.axis("off")

sum_lines = [
    "EUMODIC REPLICATION SUMMARY",
    "",
    f"Primary result:",
    f"  Spearman r = {r:+.4f}",
    f"  p = {p:.4f}  N = {n}",
    f"  {sig}",
    "",
    f"Direction: {'consistent' if r < 0 else 'inconsistent'}",
    f"with coherence hypothesis",
    "",
    f"DR23 reference:",
    f"  r = {DR23_SPEARMAN_R:+.3f}",
    f"  p = {DR23_SPEARMAN_P:.4f}",
    f"  N = {DR23_N_CENTERS}",
    "",
    f"Rank matches: {rank_matches}/{n}",
    f"Rank r = {r_rank:+.3f}",
    "",
    "LOO significant or trend:",
    f"  {n_sig_loo}/{len(loo_rows)}",
]

ax5.text(
    0.05, 0.95,
    "\n".join(sum_lines),
    transform=ax5.transAxes,
    fontsize=9,
    verticalalignment="top",
    fontfamily="monospace",
    bbox=dict(
        boxstyle="round",
        facecolor="lightyellow",
        alpha=0.8
    )
)

plt.suptitle(
    "EUMODIC ELF-Thigmotaxis "
    "Replication Analysis\n"
    "OrganismCore — February 2026",
    fontsize=12, y=1.01
)

plt.savefig(
    OUT_FIG,
    bbox_inches="tight",
    dpi=120
)
log(f"Saved: {OUT_FIG}")
log()

# ─────────────────────────────────────────
# SAVE LOG
# ─────────────────────────────────────────

with open(OUT_TXT, "w") as f:
    f.write("\n".join(results))
log(f"Saved: {OUT_TXT}")
log()

log("=" * 56)
log("ANALYSIS COMPLETE")
log("=" * 56)
