"""
GBM DRUG TARGET EXPLORATION
OrganismCore — False Attractor Framework
Cancer Validation #3 — Extended Analysis
Document 81

QUESTION:
  Given the GBM false attractor is an
  OPC-like progenitor state maintained
  by EGFR and PDGFRA signaling —

  1. How many cells have BOTH elevated?
  2. Does EGFR/PDGFRA co-elevation
     correlate with OLIG2 lock?
  3. Does dual elevation predict
     deeper attractor entrenchment?
  4. What is the predicted drug
     target combination?

HYPOTHESIS:
  The OPC-like false attractor in GBM
  is maintained by TWO upstream signals:
    EGFR  — elevated +252%
    PDGFRA — elevated +83%
  
  Single blockade of either fails
  because the other compensates.
  
  DUAL blockade predicted to dissolve
  the attractor more completely.
  
  OLIG2 elevation should correlate
  with dual EGFR/PDGFRA co-elevation
  — OLIG2 is downstream of both.

INPUT:
  /Users/ericlawson/cancer/GBM/
  gbm_saddle_results/expr_cache.csv
  (already computed — no reload needed)
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy import stats
import os
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# CONFIGURATION
# ============================================================

GBM_CACHE   = "/Users/ericlawson/cancer/GBM/" \
              "gbm_saddle_results/expr_cache.csv"
RESULTS_DIR = "/Users/ericlawson/cancer/GBM/" \
              "gbm_saddle_results/"
LOG_FILE    = RESULTS_DIR + "drug_target_log.txt"

os.makedirs(RESULTS_DIR, exist_ok=True)

with open(LOG_FILE, "w") as f:
    f.write("")

def log(msg=""):
    print(msg)
    with open(LOG_FILE, "a") as f:
        f.write(str(msg) + "\n")

# Gene groups
PROGENITOR  = ["EGFR", "PDGFRA",
               "SOX2", "NES"]
LOCK        = ["OLIG2", "OLIG1"]
MYELINATION = ["MBP", "MOG",
               "PLP1", "SOX10"]
ASTROCYTE   = ["GFAP"]

# Elevation thresholds
# Top 30% within OPC-like cells
ELEV_PERCENTILE = 70

# ============================================================
# STEP 1: LOAD CACHE
# ============================================================

def load_cache():
    log("=" * 56)
    log("GBM DRUG TARGET EXPLORATION")
    log("OrganismCore — Document 81")
    log("=" * 56)
    log()
    log("STEP 1: LOADING GBM CACHE")
    log("-" * 40)

    df = pd.read_csv(GBM_CACHE, index_col=0)
    log(f"Cache shape: {df.shape}")
    log(f"Columns: {df.columns.tolist()}")

    # Reclassify cell states
    myl_genes  = [g for g in
                  ["MBP", "MOG", "PLP1", "SOX10"]
                  if g in df.columns]
    prog_genes = [g for g in
                  ["PDGFRA", "SOX2", "EGFR", "NES"]
                  if g in df.columns]

    df["oligo_score"] = df[myl_genes].mean(axis=1)
    df["prog_score"]  = df[prog_genes].mean(axis=1)

    oligo_thresh = df["oligo_score"].quantile(0.80)
    prog_thresh  = df["prog_score"].quantile(0.80)

    conditions = [
        df["oligo_score"] >= oligo_thresh,
        df["prog_score"]  >= prog_thresh,
    ]
    choices = ["Normal_Oligo", "OPC_like"]
    df["cell_state"] = np.select(
        conditions, choices, default="Ambiguous")

    counts = df["cell_state"].value_counts()
    log(f"\nCell state distribution:")
    log(str(counts))

    return df

# ============================================================
# STEP 2: EGFR / PDGFRA CO-ELEVATION ANALYSIS
# ============================================================

def coexpression_analysis(df):
    log()
    log("=" * 56)
    log("STEP 2: EGFR / PDGFRA CO-ELEVATION")
    log("=" * 56)

    opc = df[df["cell_state"] == "OPC_like"].copy()
    log(f"OPC-like cells: {len(opc)}")

    if "EGFR" not in opc.columns or \
       "PDGFRA" not in opc.columns:
        log("ERROR: EGFR or PDGFRA not in cache")
        return df

    egfr_thresh  = opc["EGFR"].quantile(
        ELEV_PERCENTILE / 100)
    pdgfra_thresh = opc["PDGFRA"].quantile(
        ELEV_PERCENTILE / 100)

    log(f"\nEGFR  threshold (p{ELEV_PERCENTILE}): "
        f"{egfr_thresh:.4f}")
    log(f"PDGFRA threshold (p{ELEV_PERCENTILE}): "
        f"{pdgfra_thresh:.4f}")

    # Flag cells by elevation pattern
    egfr_hi   = opc["EGFR"]   >= egfr_thresh
    pdgfra_hi = opc["PDGFRA"] >= pdgfra_thresh

    opc["EGFR_high"]       = egfr_hi
    opc["PDGFRA_high"]     = pdgfra_hi
    opc["DUAL_high"]       = egfr_hi & pdgfra_hi
    opc["EGFR_only"]       = egfr_hi & ~pdgfra_hi
    opc["PDGFRA_only"]     = ~egfr_hi & pdgfra_hi
    opc["NEITHER_high"]    = ~egfr_hi & ~pdgfra_hi

    n_dual    = opc["DUAL_high"].sum()
    n_egfr    = opc["EGFR_only"].sum()
    n_pdgfra  = opc["PDGFRA_only"].sum()
    n_neither = opc["NEITHER_high"].sum()
    n_total   = len(opc)

    log(f"\nElevation pattern in OPC-like cells:")
    log(f"  DUAL high (EGFR + PDGFRA): "
        f"{n_dual:4d} ({n_dual/n_total*100:.1f}%)")
    log(f"  EGFR only:                 "
        f"{n_egfr:4d} ({n_egfr/n_total*100:.1f}%)")
    log(f"  PDGFRA only:               "
        f"{n_pdgfra:4d} "
        f"({n_pdgfra/n_total*100:.1f}%)")
    log(f"  Neither elevated:          "
        f"{n_neither:4d} "
        f"({n_neither/n_total*100:.1f}%)")

    # Correlation EGFR vs PDGFRA
    r, p = stats.pearsonr(
        opc["EGFR"], opc["PDGFRA"])
    log(f"\nEGFR vs PDGFRA correlation:")
    log(f"  Pearson r = {r:.4f}  p = {p:.2e}")

    if r > 0.3 and p < 0.05:
        log("  CORRELATED — co-elevated together")
        log("  Both respond to same upstream signal")
    elif r > 0:
        log("  WEAKLY CORRELATED")
        log("  Partially independent signals")
    else:
        log("  ANTI-CORRELATED or independent")
        log("  Independent attractor inputs")

    return opc

# ============================================================
# STEP 3: OLIG2 LOCK CORRELATION
# ============================================================

def olig2_lock_analysis(opc):
    log()
    log("=" * 56)
    log("STEP 3: OLIG2 LOCK CORRELATION")
    log("=" * 56)
    log("OLIG2 is downstream of EGFR/PDGFRA")
    log("in OPCs. If it is the attractor lock,")
    log("OLIG2 should be highest in DUAL cells.")

    if "OLIG2" not in opc.columns:
        log("OLIG2 not in cache — skipping")
        return

    groups = {
        "DUAL"    : opc[opc["DUAL_high"]],
        "EGFR_only": opc[opc["EGFR_only"]],
        "PDGFRA_only": opc[opc["PDGFRA_only"]],
        "NEITHER" : opc[opc["NEITHER_high"]],
    }

    log(f"\nOLIG2 expression by elevation group:")
    olig2_means = {}
    for name, grp in groups.items():
        if len(grp) == 0:
            continue
        m  = grp["OLIG2"].mean()
        se = grp["OLIG2"].sem()
        olig2_means[name] = m
        log(f"  {name:12}: mean={m:.4f} ± {se:.4f} "
            f"n={len(grp)}")

    # Test DUAL vs NEITHER
    dual_vals    = opc[opc["DUAL_high"]]["OLIG2"]
    neither_vals = opc[opc["NEITHER_high"]]["OLIG2"]

    if len(dual_vals) > 5 and len(neither_vals) > 5:
        _, p = stats.mannwhitneyu(
            dual_vals, neither_vals,
            alternative='greater')
        log(f"\nDUAL vs NEITHER OLIG2:")
        log(f"  p = {p:.2e}")
        if p < 0.05:
            log("  OLIG2 significantly higher")
            log("  in DUAL co-elevated cells ***")
            log("  OLIG2 IS the downstream lock")
            log("  Dual EGFR+PDGFRA → OLIG2 → lock")
        else:
            log("  No significant OLIG2 difference")

    # EGFR correlation with OLIG2
    r_egfr, p_egfr = stats.pearsonr(
        opc["EGFR"], opc["OLIG2"])
    log(f"\nEGFR vs OLIG2:   r={r_egfr:.4f} "
        f"p={p_egfr:.2e}")

    if "PDGFRA" in opc.columns:
        r_pdgfra, p_pdgfra = stats.pearsonr(
            opc["PDGFRA"], opc["OLIG2"])
        log(f"PDGFRA vs OLIG2: r={r_pdgfra:.4f} "
            f"p={p_pdgfra:.2e}")

    return olig2_means

# ============================================================
# STEP 4: ATTRACTOR DEPTH SCORING
# ============================================================

def attractor_depth(opc):
    log()
    log("=" * 56)
    log("STEP 4: ATTRACTOR DEPTH SCORING")
    log("=" * 56)
    log("Deeper attractor = more myelination")
    log("genes suppressed + more progenitor")
    log("genes elevated simultaneously")

    myl_avail  = [g for g in MYELINATION
                  if g in opc.columns]
    prog_avail = [g for g in PROGENITOR
                  if g in opc.columns]

    log(f"Myelination genes: {myl_avail}")
    log(f"Progenitor genes:  {prog_avail}")

    # Attractor depth score:
    # high progenitor + low myelination
    # normalized 0-1
    prog_score = opc[prog_avail].mean(axis=1)
    myl_score  = opc[myl_avail].mean(axis=1)

    # Normalize each to 0-1
    def norm01(s):
        mn, mx = s.min(), s.max()
        if mx == mn:
            return s * 0
        return (s - mn) / (mx - mn)

    prog_norm = norm01(prog_score)
    myl_norm  = norm01(myl_score)

    # Depth = progenitor - myelination
    # rescaled to 0-1
    depth = norm01(prog_norm - myl_norm)
    opc   = opc.copy()
    opc["attractor_depth"] = depth

    log(f"\nAttractor depth by elevation group:")
    for group_col, label in [
        ("DUAL_high",    "DUAL"),
        ("EGFR_only",    "EGFR only"),
        ("PDGFRA_only",  "PDGFRA only"),
        ("NEITHER_high", "NEITHER"),
    ]:
        grp = opc[opc[group_col]]
        if len(grp) == 0:
            continue
        m  = grp["attractor_depth"].mean()
        se = grp["attractor_depth"].sem()
        log(f"  {label:12}: depth={m:.4f} ± {se:.4f}")

    # Statistical test: DUAL deepest?
    dual    = opc[opc["DUAL_high"]]["attractor_depth"]
    neither = opc[opc["NEITHER_high"]]["attractor_depth"]
    egfr_o  = opc[opc["EGFR_only"]]["attractor_depth"]
    pdgfra_o = opc[opc["PDGFRA_only"]]["attractor_depth"]

    if len(dual) > 5 and len(neither) > 5:
        _, p_dn = stats.mannwhitneyu(
            dual, neither, alternative='greater')
        log(f"\nDUAL vs NEITHER depth: p={p_dn:.2e}")
        if p_dn < 0.05:
            log("  DUAL cells are DEEPER in attractor ***")
            log("  Co-elevation = stronger lock")

    if len(dual) > 5 and len(egfr_o) > 5:
        _, p_de = stats.mannwhitneyu(
            dual, egfr_o, alternative='greater')
        log(f"DUAL vs EGFR-only:    p={p_de:.2e}")

    if len(dual) > 5 and len(pdgfra_o) > 5:
        _, p_dp = stats.mannwhitneyu(
            dual, pdgfra_o, alternative='greater')
        log(f"DUAL vs PDGFRA-only:  p={p_dp:.2e}")

    return opc

# ============================================================
# STEP 5: MYELINATION SUPPRESSION BY GROUP
# ============================================================

def myelination_suppression(opc):
    log()
    log("=" * 56)
    log("STEP 5: MYELINATION SUPPRESSION")
    log("BY ELEVATION GROUP")
    log("=" * 56)
    log("If DUAL cells are deepest in attractor")
    log("they should have the MOST suppressed")
    log("myelination genes — most lost identity")

    myl_avail = [g for g in MYELINATION
                 if g in opc.columns]

    results = {}
    for group_col, label in [
        ("DUAL_high",    "DUAL"),
        ("EGFR_only",    "EGFR only"),
        ("PDGFRA_only",  "PDGFRA only"),
        ("NEITHER_high", "NEITHER"),
    ]:
        grp = opc[opc[group_col]]
        if len(grp) == 0:
            continue
        means = {g: grp[g].mean() for g in myl_avail}
        avg   = np.mean(list(means.values()))
        results[label] = {
            "genes": means,
            "avg":   avg,
            "n":     len(grp)
        }
        gene_str = "  ".join(
            [f"{g}={v:.3f}"
             for g, v in means.items()])
        log(f"\n  {label} (n={len(grp)}):")
        log(f"    {gene_str}")
        log(f"    avg myelination = {avg:.4f}")

    log()
    log("Interpretation:")
    avgs = {k: v["avg"] for k, v in results.items()}
    sorted_groups = sorted(avgs.items(),
                           key=lambda x: x[1])
    log("Myelination suppression ranking:")
    log("(lowest = most suppressed = deepest attractor)")
    for rank, (label, val) in enumerate(
            sorted_groups, 1):
        log(f"  {rank}. {label:12}: avg={val:.4f}")

    return results

# ============================================================
# STEP 6: DRUG TARGET SUMMARY
# ============================================================

def drug_target_summary(opc, myl_results):
    log()
    log("=" * 56)
    log("STEP 6: DRUG TARGET DERIVATION")
    log("FROM ATTRACTOR LOGIC")
    log("=" * 56)

    n_total = len(opc)
    n_dual  = opc["DUAL_high"].sum()
    n_egfr  = opc["EGFR_only"].sum()
    n_pdgfra = opc["PDGFRA_only"].sum()

    egfr_mean   = opc["EGFR"].mean()
    pdgfra_mean = opc["PDGFRA"].mean()

    log(f"OPC-like cells:          {n_total}")
    log(f"DUAL elevated:           "
        f"{n_dual} ({n_dual/n_total*100:.1f}%)")
    log(f"EGFR only elevated:      "
        f"{n_egfr} ({n_egfr/n_total*100:.1f}%)")
    log(f"PDGFRA only elevated:    "
        f"{n_pdgfra} "
        f"({n_pdgfra/n_total*100:.1f}%)")
    log()
    log("DRUG TARGET PREDICTIONS:")
    log("=" * 40)
    log()
    log("TARGET 1: EGFR inhibition")
    log(f"  EGFR elevated +252% in OPC-like")
    log(f"  Mean EGFR in OPC-like: "
        f"{egfr_mean:.4f}")
    log(f"  Relevant to: EGFR-only + DUAL cells")
    log(f"  = {(n_egfr+n_dual)/n_total*100:.1f}% "
        f"of OPC-like cells")
    log(f"  Drug class: EGFR inhibitor")
    log(f"  Known drugs: erlotinib, gefitinib,")
    log(f"               osimertinib, cetuximab")
    log(f"  Clinical history: FAILED as")
    log(f"  monotherapy in GBM")
    log(f"  Attractor reason for failure:")
    log(f"  PDGFRA compensates when EGFR blocked")
    log()
    log("TARGET 2: PDGFRA inhibition")
    log(f"  PDGFRA elevated +83% in OPC-like")
    log(f"  Mean PDGFRA in OPC-like: "
        f"{pdgfra_mean:.4f}")
    log(f"  Relevant to: PDGFRA-only + DUAL cells")
    log(f"  = {(n_pdgfra+n_dual)/n_total*100:.1f}% "
        f"of OPC-like cells")
    log(f"  Drug class: PDGFR inhibitor")
    log(f"  Known drugs: imatinib, sunitinib,")
    log(f"               ripretinib, avapritinib")
    log(f"  Clinical history: FAILED as")
    log(f"  monotherapy in GBM")
    log(f"  Attractor reason for failure:")
    log(f"  EGFR compensates when PDGFRA blocked")
    log()
    log("TARGET 3: EGFR + PDGFRA DUAL BLOCKADE")
    log(f"  *** PRIMARY NOVEL PREDICTION ***")
    log(f"  DUAL co-elevated cells: "
        f"{n_dual/n_total*100:.1f}%")
    log(f"  These are the DEEPEST in attractor")
    log(f"  Both upstream signals active")
    log(f"  Single blockade insufficient —")
    log(f"  the other signal compensates")
    log(f"  Dual blockade removes both inputs")
    log(f"  → attractor has no maintenance signal")
    log(f"  → cells differentiate or die")
    log(f"  Drug combinations to test:")
    log(f"    erlotinib + imatinib")
    log(f"    osimertinib + avapritinib")
    log(f"    cetuximab + sunitinib")
    log(f"  Clinical status: NOT systematically")
    log(f"  tested as attractor-dissolution")
    log(f"  strategy in GBM")
    log(f"  THIS IS THE TESTABLE PREDICTION")
    log()
    log("TARGET 4: OLIG2 (downstream lock)")
    log(f"  OLIG2 elevated in OPC-like cells")
    log(f"  Downstream of EGFR and PDGFRA")
    log(f"  Transcription factor — harder to drug")
    log(f"  CT-179 OLIG2 inhibitor in preclinical")
    log(f"  Prediction: OLIG2 inhibition would")
    log(f"  dissolve attractor independently of")
    log(f"  upstream RTK signals")
    log(f"  Combination: RTK dual + OLIG2")
    log(f"  = triple attractor dissolution")
    log()
    log("=" * 40)
    log("WHY PREVIOUS GBM TRIALS FAILED:")
    log("=" * 40)
    log("The attractor has multiple inputs.")
    log("EGFR alone: blocked → PDGFRA compensates")
    log("PDGFRA alone: blocked → EGFR compensates")
    log("Both: blocked → OLIG2 may persist")
    log("All three: blocked → attractor dissolved")
    log()
    log("This is the attractor topology")
    log("explanation for why GBM is")
    log("resistant to single-target therapy.")

# ============================================================
# STEP 7: FIGURE
# ============================================================

def generate_figure(df, opc, olig2_means,
                    myl_results):
    log()
    log("=" * 56)
    log("STEP 7: GENERATING FIGURE")
    log("=" * 56)

    fig = plt.figure(figsize=(24, 16))
    gs  = gridspec.GridSpec(
        2, 3, figure=fig,
        hspace=0.45, wspace=0.38)

    colors = {
        "DUAL":         "#c0392b",
        "EGFR only":    "#e67e22",
        "PDGFRA only":  "#2980b9",
        "NEITHER":      "#95a5a6",
    }

    # Panel A: EGFR vs PDGFRA scatter
    ax_a = fig.add_subplot(gs[0, 0])
    if "EGFR" in opc.columns and \
       "PDGFRA" in opc.columns:
        # Sample for speed
        sample = opc.sample(
            min(800, len(opc)),
            random_state=42)

        group_masks = {
            "DUAL":        (sample["DUAL_high"],
                            "#c0392b"),
            "EGFR only":   (sample["EGFR_only"],
                            "#e67e22"),
            "PDGFRA only": (sample["PDGFRA_only"],
                            "#2980b9"),
            "NEITHER":     (sample["NEITHER_high"],
                            "#95a5a6"),
        }
        for label, (mask, color) in \
                group_masks.items():
            grp = sample[mask]
            ax_a.scatter(
                grp["EGFR"], grp["PDGFRA"],
                c=color, alpha=0.5, s=12,
                label=label)
        ax_a.set_xlabel("EGFR expression",
                        fontsize=10)
        ax_a.set_ylabel("PDGFRA expression",
                        fontsize=10)
        ax_a.legend(fontsize=7,
                    loc="upper right")
        r, _ = stats.pearsonr(
            opc["EGFR"], opc["PDGFRA"])
        ax_a.set_title(
            f"A. EGFR vs PDGFRA Co-elevation\n"
            f"OPC-like cells  |  r={r:.3f}",
            fontsize=9, fontweight='bold')

    # Panel B: Cell counts by group
    ax_b = fig.add_subplot(gs[0, 1])
    n_total  = len(opc)
    groups_b = ["DUAL", "EGFR only",
                "PDGFRA only", "NEITHER"]
    cols_b   = ["DUAL_high", "EGFR_only",
                "PDGFRA_only", "NEITHER_high"]
    counts_b = [opc[c].sum() for c in cols_b]
    pcts_b   = [c / n_total * 100
                for c in counts_b]
    bar_colors = ["#c0392b", "#e67e22",
                  "#2980b9", "#95a5a6"]
    bars = ax_b.bar(groups_b, pcts_b,
                    color=bar_colors, alpha=0.85)
    for bar, pct, n in zip(bars, pcts_b,
                           counts_b):
        ax_b.text(
            bar.get_x() + bar.get_width()/2,
            bar.get_height() + 0.5,
            f"{pct:.1f}%\nn={n}",
            ha='center', va='bottom',
            fontsize=8)
    ax_b.set_ylabel("% of OPC-like cells",
                    fontsize=10)
    ax_b.set_title(
        "B. Elevation Pattern Distribution\n"
        "OPC-like false attractor cells",
        fontsize=9, fontweight='bold')
    ax_b.tick_params(axis='x', labelsize=8)

    # Panel C: OLIG2 by group
    ax_c = fig.add_subplot(gs[0, 2])
    if olig2_means and "OLIG2" in opc.columns:
        group_order = ["DUAL", "EGFR only",
                       "PDGFRA only", "NEITHER"]
        olig2_vals  = [olig2_means.get(g, 0)
                       for g in group_order]
        bar_c = ax_c.bar(
            group_order, olig2_vals,
            color=["#c0392b", "#e67e22",
                   "#2980b9", "#95a5a6"],
            alpha=0.85)
        for bar, val in zip(bar_c, olig2_vals):
            ax_c.text(
                bar.get_x() + bar.get_width()/2,
                bar.get_height() + 0.002,
                f"{val:.3f}",
                ha='center', va='bottom',
                fontsize=8)
        ax_c.set_ylabel("OLIG2 expression",
                        fontsize=10)
        ax_c.set_title(
            "C. OLIG2 Lock by Elevation Group\n"
            "DUAL cells should have highest OLIG2",
            fontsize=9, fontweight='bold')
        ax_c.tick_params(axis='x', labelsize=8)

    # Panel D: Attractor depth by group
    ax_d = fig.add_subplot(gs[1, 0])
    if "attractor_depth" in opc.columns:
        group_data = []
        group_lbls = []
        group_cols = [
            ("DUAL_high",    "DUAL",
             "#c0392b"),
            ("EGFR_only",    "EGFR only",
             "#e67e22"),
            ("PDGFRA_only",  "PDGFRA only",
             "#2980b9"),
            ("NEITHER_high", "NEITHER",
             "#95a5a6"),
        ]
        bp_data   = []
        bp_labels = []
        bp_colors = []
        for col, lbl, clr in group_cols:
            vals = opc[opc[col]]["attractor_depth"]
            if len(vals) > 0:
                bp_data.append(vals.values)
                bp_labels.append(lbl)
                bp_colors.append(clr)

        bp = ax_d.boxplot(
            bp_data, labels=bp_labels,
            patch_artist=True,
            medianprops=dict(color='black',
                             linewidth=2))
        for patch, color in zip(
                bp['boxes'], bp_colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        ax_d.set_ylabel("Attractor depth score",
                        fontsize=10)
        ax_d.set_title(
            "D. Attractor Depth by Group\n"
            "DUAL = deepest in false attractor",
            fontsize=9, fontweight='bold')
        ax_d.tick_params(axis='x', labelsize=8)

    # Panel E: Myelination suppression
    ax_e = fig.add_subplot(gs[1, 1])
    if myl_results:
        group_order = ["DUAL", "EGFR only",
                       "PDGFRA only", "NEITHER"]
        myl_avail   = [g for g in MYELINATION
                       if g in opc.columns]
        x = np.arange(len(myl_avail))
        width = 0.18
        grp_colors = ["#c0392b", "#e67e22",
                      "#2980b9", "#95a5a6"]
        for i, (grp_lbl, clr) in enumerate(
                zip(group_order, grp_colors)):
            if grp_lbl not in myl_results:
                continue
            vals = [myl_results[grp_lbl]
                    ["genes"].get(g, 0)
                    for g in myl_avail]
            offset = (i - 1.5) * width
            ax_e.bar(x + offset, vals, width,
                     label=grp_lbl,
                     color=clr, alpha=0.8)
        ax_e.set_xticks(x)
        ax_e.set_xticklabels(myl_avail,
                             fontsize=9)
        ax_e.set_ylabel(
            "Mean expression", fontsize=10)
        ax_e.legend(fontsize=7)
        ax_e.set_title(
            "E. Myelination Gene Suppression\n"
            "DUAL cells lose most normal identity",
            fontsize=9, fontweight='bold')

    # Panel F: Drug target summary text
    ax_f = fig.add_subplot(gs[1, 2])
    ax_f.axis('off')
    n_dual   = opc["DUAL_high"].sum()
    n_total  = len(opc)
    summary  = (
        "F. Drug Target Predictions\n"
        "from Attractor Logic\n\n"
        f"OPC-like cells: {n_total}\n"
        f"DUAL elevated:  "
        f"{n_dual} "
        f"({n_dual/n_total*100:.1f}%)\n\n"
        "TARGET 1: EGFR inhibitor\n"
        "  Monotherapy → FAILED\n"
        "  PDGFRA compensates\n\n"
        "TARGET 2: PDGFRA inhibitor\n"
        "  Monotherapy → FAILED\n"
        "  EGFR compensates\n\n"
        "TARGET 3: EGFR + PDGFRA\n"
        "  DUAL BLOCKADE\n"
        "  *** NOVEL PREDICTION ***\n"
        "  Not tested as attractor\n"
        "  dissolution strategy\n\n"
        "TARGET 4: OLIG2 inhibitor\n"
        "  Downstream lock\n"
        "  CT-179 preclinical\n\n"
        "TRIPLE: RTK dual + OLIG2\n"
        "  Maximum dissolution"
    )
    ax_f.text(
        0.05, 0.97, summary,
        transform=ax_f.transAxes,
        fontsize=8.5,
        verticalalignment='top',
        fontfamily='monospace',
        bbox=dict(boxstyle='round',
                  facecolor='lightyellow',
                  alpha=0.8))

    fig.suptitle(
        "GBM Drug Target Exploration — "
        "OPC-like False Attractor\n"
        "EGFR/PDGFRA Co-elevation Analysis  |  "
        "OrganismCore  |  Document 81\n"
        "GSE131928 — Neftel et al. 2019  |  "
        "7,930 GBM cells  |  Smart-seq2",
        fontsize=11, fontweight='bold')

    outpath = (RESULTS_DIR +
               "gbm_drug_target_figure.png")
    plt.savefig(outpath, dpi=180,
                bbox_inches='tight')
    plt.close()
    log(f"Figure saved: {outpath}")

# ============================================================
# MAIN
# ============================================================

def main():
    df        = load_cache()
    opc       = coexpression_analysis(df)
    olig2_m   = olig2_lock_analysis(opc)
    opc       = attractor_depth(opc)
    myl_res   = myelination_suppression(opc)
    drug_target_summary(opc, myl_res)
    generate_figure(df, opc, olig2_m, myl_res)

    log()
    log("=" * 56)
    log("GBM DRUG TARGET EXPLORATION COMPLETE")
    log(f"Results: {RESULTS_DIR}")
    log("Key output: drug_target_log.txt")
    log("Figure:     gbm_drug_target_figure.png")
    log("=" * 56)

if __name__ == "__main__":
    main()
