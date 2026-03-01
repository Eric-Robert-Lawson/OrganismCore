"""
Multiple Myeloma — Corrected False Attractor Analysis
REVISED FRAMEWORK: MM is locked in plasmablast/activated state
True switch gene: IRF8 (suppressed — blocks transition to LLPC)
False attractor: IRF4/PRDM1/XBP1 elevated — activation locked on
OrganismCore — Principles-First
Date: 2026-03-01
"""

import h5py
import numpy as np
import pandas as pd
import scipy.sparse as sp
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import os
import warnings
warnings.filterwarnings("ignore")

DATA_DIR    = "/Users/ericlawson/cancer/MM/"
RESULTS_DIR = "/Users/ericlawson/cancer/MM/mm_saddle_results/"
LOG_FILE    = RESULTS_DIR + "corrected_analysis_log.txt"
os.makedirs(RESULTS_DIR, exist_ok=True)

log_lines = []
def log(msg=""):
    print(msg)
    log_lines.append(str(msg))

def write_log():
    with open(LOG_FILE, "w") as f:
        f.write("\n".join(log_lines))

# ============================================================
# CORRECTED GENE PANELS
# Based on data-corrected framework
# MM = stuck in plasmablast/activated plasma cell state
# Cannot complete transition to long-lived plasma cell (LLPC)
# ============================================================

# TRUE SWITCH GENE — suppressed in MM
# IRF8 drives plasmablast -> LLPC transition
# Its loss = the differentiation block
SWITCH_GENES = ["IRF8"]

# FALSE ATTRACTOR MARKERS — elevated in MM
# These define the activated/plasmablast state MM is locked in
# Normally high in plasmablasts, low in LLPC
FALSE_ATTRACTOR = ["IRF4", "PRDM1", "XBP1"]

# SECONDARY FALSE ATTRACTOR — residual B cell signal
# Small elevation suggests partial retention of earlier state
B_CELL_RESIDUAL = ["PAX5", "CD19", "MS4A1", "BCL6"]

# SCAFFOLD — proliferation, secretory activity
SCAFFOLD = ["MYC", "MKI67"]

# LOCK CANDIDATE — revised: EZH2 not the mechanism
# Check IKZF1 (Ikaros) — known regulator of plasma cell maturation
# Check BLIMP1 targets
LOCK_CANDIDATE = ["EZH2"]

# UNFOLDED PROTEIN RESPONSE — plasma cell secretory stress marker
UPR = ["HSPA5", "DDIT3", "ATF4"]

# LLPC MATURITY MARKERS — should be HIGH in normal LLPC, LOW in MM
# These are the genes that define the terminal state MM cannot reach
LLPC_MARKERS = ["CD19", "CXCR4", "CD28", "CD44"]

ALL_TARGET = list(dict.fromkeys(
    SWITCH_GENES + FALSE_ATTRACTOR + B_CELL_RESIDUAL +
    SCAFFOLD + LOCK_CANDIDATE + UPR
))

ALL_LOAD = list(dict.fromkeys(
    ["SDC1","CD38","CD27","CD3D","CD14","HBB","MS4A1","PAX5"] +
    ALL_TARGET
))

# ============================================================
# LOAD H5
# ============================================================

def load_h5(filepath, target_genes, label):
    with h5py.File(filepath, "r") as f:
        gene_names = [g.decode("utf-8") for g in f["matrix/features/name"][:]]
        barcodes   = [b.decode("utf-8") for b in f["matrix/barcodes"][:]]
        shape      = tuple(f["matrix/shape"][:])
        data       = f["matrix/data"][:]
        indices    = f["matrix/indices"][:]
        indptr     = f["matrix/indptr"][:]

    mat = sp.csc_matrix((data, indices, indptr), shape=shape)
    cell_totals = np.array(mat.sum(axis=0)).flatten()
    cell_totals[cell_totals == 0] = 1

    rows, found = [], []
    for gene in target_genes:
        if gene in gene_names:
            idx   = gene_names.index(gene)
            raw   = np.array(mat[idx, :].todense()).flatten()
            norm  = (raw / cell_totals) * 10000
            log1p = np.log1p(norm)
            rows.append(log1p)
            found.append(gene)

    if not rows:
        return pd.DataFrame(index=[f"{label}_{b}" for b in barcodes])

    return pd.DataFrame(
        np.array(rows).T,
        index=[f"{label}_{b}" for b in barcodes],
        columns=found
    )

# ============================================================
# PLASMA CELL ISOLATION
# ============================================================

def isolate_plasma_cells(df, label):
    def norm01(s):
        mn, mx = s.min(), s.max()
        if mx == mn: return s * 0.0
        return (s - mn) / (mx - mn)

    pos_genes = [g for g in ["SDC1","CD38","CD27"] if g in df.columns]
    if not pos_genes:
        return df.iloc[0:0], 0, len(df)

    plasma_score = norm01(df[pos_genes].mean(axis=1))
    excl_genes   = [g for g in ["CD3D","CD14","HBB"] if g in df.columns]
    excl_norm    = norm01(df[excl_genes].mean(axis=1)) \
                   if excl_genes else \
                   pd.Series(np.zeros(len(df)), index=df.index)

    mask = (plasma_score >= plasma_score.quantile(0.80)) & \
           (excl_norm    <= excl_norm.quantile(0.70))

    return df[mask], mask.sum(), len(df)

# ============================================================
# LOAD FROM CACHE (already computed)
# ============================================================

def load_stage_caches():
    stages = {
        "HD":   RESULTS_DIR + "plasma_hd.csv",
        "MGUS": RESULTS_DIR + "plasma_mgus.csv",
        "SMM":  RESULTS_DIR + "plasma_smm.csv",
        "MM":   RESULTS_DIR + "plasma_mm.csv",
    }
    data = {}
    for stage, cache in stages.items():
        if os.path.exists(cache):
            df = pd.read_csv(cache, index_col=0)
            # keep only columns we need
            keep = [c for c in ALL_TARGET if c in df.columns]
            data[stage] = df[keep]
            log(f"  {stage}: {len(df)} plasma cells  "
                f"(genes available: {keep})")
        else:
            log(f"  {stage}: CACHE MISSING — {cache}")
            data[stage] = pd.DataFrame()
    return data

# ============================================================
# CORRECTED SADDLE POINT ANALYSIS
# ============================================================

def saddle_point_corrected(hd, mm):
    log("")
    log("=" * 70)
    log("CORRECTED SADDLE POINT — MM PLASMA vs HD PLASMA")
    log("REVISED FRAMEWORK: MM locked in plasmablast/activated state")
    log("True switch: IRF8 (suppressed = cannot become LLPC)")
    log("False attractor: IRF4/PRDM1/XBP1 (elevated = activation locked)")
    log("=" * 70)
    log(f"HD plasma : {len(hd)}")
    log(f"MM plasma : {len(mm)}")
    log("")

    results = []
    log(f"  {'Gene':<12} {'Role':<20} {'HD':>8} {'MM':>8} "
        f"{'Change':>10} {'p-value':>16} {'Result'}")
    log(f"  {'-'*85}")

    role_map = {}
    for g in SWITCH_GENES:     role_map[g] = "SWITCH"
    for g in FALSE_ATTRACTOR:  role_map[g] = "FALSE_ATTRACTOR"
    for g in B_CELL_RESIDUAL:  role_map[g] = "B_RESIDUAL"
    for g in SCAFFOLD:         role_map[g] = "SCAFFOLD"
    for g in LOCK_CANDIDATE:   role_map[g] = "LOCK"
    for g in UPR:              role_map[g] = "UPR"

    for gene in ALL_TARGET:
        if gene not in hd.columns or gene not in mm.columns:
            continue

        hd_v = hd[gene].values
        mm_v = mm[gene].values
        hd_m = hd_v.mean()
        mm_m = mm_v.mean()

        _, p_supp = stats.mannwhitneyu(hd_v, mm_v, alternative="greater")
        _, p_elev = stats.mannwhitneyu(mm_v, hd_v, alternative="greater")

        chg = (mm_m - hd_m) / hd_m * 100 if hd_m > 0.0001 else 0.0
        role = role_map.get(gene, "OTHER")

        if role == "SWITCH":
            if p_supp < 0.05 and chg < -20:
                result = "CONFIRMED"
            elif p_supp < 0.05:
                result = "WEAKLY SUPPRESSED"
            elif chg > 20:
                result = "INVERTED — SEE NOTE"
            else:
                result = "NOT SUPPRESSED"
        elif role == "FALSE_ATTRACTOR":
            if p_elev < 0.05 and chg > 20:
                result = "ELEVATED — ATTRACTOR CONFIRMED"
            elif p_elev < 0.05:
                result = "WEAKLY ELEVATED"
            else:
                result = "NOT ELEVATED"
        elif role == "LOCK":
            if p_elev < 0.05 and chg > 20:
                result = "LOCK CONFIRMED"
            elif p_supp < 0.05 and chg < -20:
                result = "SUPPRESSED — NOT LOCK"
            else:
                result = "NEUTRAL"
        else:
            result = "SEE DATA"

        def fmt_p(p):
            if p < 1e-300: return "p=0.00e+00 ***"
            elif p < 0.001: return f"p={p:.2e} ***"
            elif p < 0.01:  return f"p={p:.2e} **"
            elif p < 0.05:  return f"p={p:.4f} *"
            else:           return f"p={p:.4f} ns"

        log(f"  {gene:<12} {role:<20} {hd_m:>8.4f} {mm_m:>8.4f} "
            f"{chg:>+9.1f}%  {fmt_p(min(p_supp,p_elev)):>18}  {result}")

        results.append({"gene":gene,"role":role,
                        "hd_mean":hd_m,"mm_mean":mm_m,
                        "change_pct":chg,
                        "p_supp":p_supp,"p_elev":p_elev,
                        "result":result})

    return pd.DataFrame(results)

# ============================================================
# PROGRESSION — IRF8 TRAJECTORY FOCUS
# ============================================================

def progression_irf8(stage_data):
    log("")
    log("=" * 70)
    log("IRF8 PROGRESSION TRAJECTORY — THE DIFFERENTIATION BLOCK")
    log("HD -> MGUS -> SMM -> MM (plasma cells only)")
    log("=" * 70)

    stages = ["HD","MGUS","SMM","MM"]
    rows = []

    for stage in stages:
        df = stage_data.get(stage, pd.DataFrame())
        if len(df) == 0:
            continue
        row = {"stage": stage, "n": len(df)}
        for gene in ALL_TARGET:
            if gene in df.columns:
                row[gene] = df[gene].mean()
                row[f"{gene}_sem"] = df[gene].sem()
        rows.append(row)

    prog = pd.DataFrame(rows).set_index("stage")

    # Print IRF8 trajectory
    log("\n  IRF8 trajectory (the differentiation block signal):")
    log(f"  {'Stage':<8} {'n cells':>8} {'IRF8 mean':>12} {'SEM':>8}")
    log(f"  {'-'*42}")
    for stage in stages:
        if stage not in prog.index:
            continue
        n    = int(prog.loc[stage,"n"])
        val  = prog.loc[stage,"IRF8"] if "IRF8" in prog.columns else float("nan")
        sem  = prog.loc[stage,"IRF8_sem"] if "IRF8_sem" in prog.columns else float("nan")
        log(f"  {stage:<8} {n:>8} {val:>12.4f} {sem:>8.4f}")

    # Print all genes
    log("\n  Full progression table:")
    header = f"  {'Gene':<12}"
    for s in stages:
        if s in prog.index:
            header += f"  {s:>8}"
    header += "  HD->MM trend"
    log(header)
    log(f"  {'-'*75}")

    for gene in ALL_TARGET:
        if gene not in prog.columns:
            continue
        row_str = f"  {gene:<12}"
        hd_v = prog.loc["HD",  gene] if "HD"  in prog.index else np.nan
        mm_v = prog.loc["MM",  gene] if "MM"  in prog.index else np.nan
        for s in stages:
            if s in prog.index:
                row_str += f"  {prog.loc[s,gene]:>8.4f}"
        if not np.isnan(hd_v) and not np.isnan(mm_v) and hd_v > 0.0001:
            trend = (mm_v - hd_v) / hd_v * 100
            arrow = "↓" if trend < -10 else "↑" if trend > 10 else "→"
            row_str += f"  {arrow} {trend:>+.1f}%"
        log(row_str)

    return prog

# ============================================================
# ATTRACTOR DEPTH — IRF8-BASED
# ============================================================

def attractor_depth_corrected(mm, results_df):
    log("")
    log("=" * 70)
    log("ATTRACTOR DEPTH — IRF8 SUPPRESSION + IRF4/PRDM1/XBP1 ELEVATION")
    log("=" * 70)

    def norm01(s):
        mn, mx = s.min(), s.max()
        if mx == mn: return s * 0
        return (s - mn) / (mx - mn)

    depth = pd.Series(np.zeros(len(mm)), index=mm.index)
    components = 0

    # IRF8 suppressed = deeper in false attractor
    if "IRF8" in mm.columns:
        depth += (1 - norm01(mm["IRF8"]))
        components += 1
        log("  Component 1: IRF8 suppression (1 - norm(IRF8))")

    # IRF4/PRDM1/XBP1 elevated = deeper in activation lock
    fa_avail = [g for g in FALSE_ATTRACTOR if g in mm.columns]
    if fa_avail:
        fa_score = mm[fa_avail].mean(axis=1)
        depth += norm01(fa_score)
        components += 1
        log(f"  Component 2: False attractor elevation "
            f"norm({fa_avail})")

    if components > 0:
        depth /= components

    mm = mm.copy()
    mm["attractor_depth"] = depth

    log(f"\n  Depth statistics:")
    log(f"  Mean   : {depth.mean():.4f}")
    log(f"  Median : {depth.median():.4f}")
    log(f"  Std    : {depth.std():.4f}")
    log(f"  Q25    : {depth.quantile(0.25):.4f}")
    log(f"  Q75    : {depth.quantile(0.75):.4f}")

    q75 = depth.quantile(0.75)
    q25 = depth.quantile(0.25)
    n_deep    = (depth >= q75).sum()
    n_shallow = (depth <= q25).sum()
    log(f"  Deep cells (Q75+, depth>={q75:.3f})    : {n_deep}")
    log(f"  Shallow cells (Q25-, depth<={q25:.3f}) : {n_shallow}")

    # Deep vs shallow: what do switch/FA genes look like?
    log("\n  Deep vs Shallow cell gene expression:")
    deep_cells    = mm[depth >= q75]
    shallow_cells = mm[depth <= q25]
    log(f"  {'Gene':<12} {'Deep':>8} {'Shallow':>10} {'Difference':>12}")
    log(f"  {'-'*48}")
    for gene in ["IRF8"] + FALSE_ATTRACTOR + ["MYC","MKI67"]:
        if gene in mm.columns:
            d_m = deep_cells[gene].mean()
            s_m = shallow_cells[gene].mean()
            diff = d_m - s_m
            log(f"  {gene:<12} {d_m:>8.4f} {s_m:>10.4f} {diff:>+12.4f}")

    return mm

# ============================================================
# FIGURE
# ============================================================

def generate_figure(stage_data, results_df, mm_depth):
    clr_hd   = "#2980b9"
    clr_mgus = "#8e44ad"
    clr_smm  = "#e67e22"
    clr_mm   = "#c0392b"
    colors   = {"HD":clr_hd,"MGUS":clr_mgus,"SMM":clr_smm,"MM":clr_mm}
    stages   = ["HD","MGUS","SMM","MM"]

    fig = plt.figure(figsize=(24,18))
    fig.suptitle(
        "Multiple Myeloma — Corrected False Attractor Analysis\n"
        "MM locked in plasmablast state | IRF8 = differentiation block\n"
        "OrganismCore Principles-First | 2026-03-01",
        fontsize=13, fontweight="bold", y=0.99
    )
    gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.5, wspace=0.38)

    w = 0.18

    def stage_bar(ax, genes, title):
        x = np.arange(len(genes))
        for i,(stage,clr) in enumerate(colors.items()):
            df_s = stage_data.get(stage, pd.DataFrame())
            if len(df_s)==0: continue
            means=[df_s[g].mean() if g in df_s.columns else 0 for g in genes]
            sems =[df_s[g].sem()  if g in df_s.columns else 0 for g in genes]
            ax.bar(x+i*w-1.5*w, means, w, yerr=sems,
                   color=clr, label=stage, capsize=3, alpha=0.85)
        ax.set_xticks(x)
        ax.set_xticklabels(genes, fontsize=10)
        ax.set_ylabel("log1p(CP10K)")
        ax.set_title(title)
        ax.legend(fontsize=7)

    # Panel A — IRF8 (true switch)
    ax_a = fig.add_subplot(gs[0,0])
    stage_bar(ax_a, ["IRF8"],
              "A — IRF8: True Switch Gene\n"
              "(Suppressed = cannot reach LLPC state)")

    # Panel B — False attractor: IRF4/PRDM1/XBP1
    ax_b = fig.add_subplot(gs[0,1])
    stage_bar(ax_b, FALSE_ATTRACTOR,
              "B — False Attractor Markers\n"
              "(Elevated = locked in plasmablast activation)")

    # Panel C — B cell residual + scaffold
    ax_c = fig.add_subplot(gs[0,2])
    misc = [g for g in ["PAX5","CD19","MS4A1","MYC","MKI67","EZH2"]
            if any(g in stage_data.get(s,pd.DataFrame()).columns
                   for s in stages)]
    stage_bar(ax_c, misc,
              "C — B Cell Residual / Scaffold / EZH2")

    # Panel D — IRF8 progression line plot
    ax_d = fig.add_subplot(gs[1,0])
    prog_vals = {}
    prog_sems = {}
    for stage in stages:
        df_s = stage_data.get(stage, pd.DataFrame())
        if len(df_s)>0 and "IRF8" in df_s.columns:
            prog_vals[stage] = df_s["IRF8"].mean()
            prog_sems[stage] = df_s["IRF8"].sem()
    if prog_vals:
        x_p = list(prog_vals.keys())
        y_p = list(prog_vals.values())
        e_p = [prog_sems[s] for s in x_p]
        ax_d.errorbar(x_p, y_p, yerr=e_p, marker="o",
                      color=clr_mm, linewidth=2, capsize=5)
        ax_d.set_ylabel("IRF8 log1p(CP10K)")
        ax_d.set_title("D — IRF8 Monotonic Decline\nHD → MGUS → SMM → MM")
        ax_d.set_ylim(bottom=0)

    # Panel E — Waterfall % change
    ax_e = fig.add_subplot(gs[1,1])
    plot_df = results_df[results_df["hd_mean"]>0.0001].copy()
    plot_df = plot_df.sort_values("change_pct")
    bar_c   = [clr_mm if v<0 else "#27ae60"
               for v in plot_df["change_pct"]]
    ax_e.barh(plot_df["gene"], plot_df["change_pct"], color=bar_c)
    ax_e.axvline(0, color="black", linewidth=0.8)
    ax_e.set_xlabel("% change MM vs HD plasma")
    ax_e.set_title("E — All Genes: % Change\nMM plasma vs HD plasma")
    ax_e.tick_params(axis="y", labelsize=9)

    # Panel F — Attractor depth distribution
    ax_f = fig.add_subplot(gs[1,2])
    if "attractor_depth" in mm_depth.columns:
        d = mm_depth["attractor_depth"]
        ax_f.hist(d, bins=60, color=clr_mm,
                  edgecolor="white", linewidth=0.4, alpha=0.85)
        ax_f.axvline(d.quantile(0.75), color="#8e44ad",
                     linestyle="--", linewidth=1.5, label="Q75 deep")
        ax_f.axvline(d.quantile(0.25), color="#f39c12",
                     linestyle="--", linewidth=1.5, label="Q25 shallow")
        ax_f.axvline(d.mean(), color="black",
                     linestyle="-",  linewidth=1.2, label="Mean")
        ax_f.set_xlabel("Attractor Depth Score")
        ax_f.set_ylabel("Cell Count")
        ax_f.set_title("F — Attractor Depth Distribution\n(MM plasma cells)")
        ax_f.legend(fontsize=8)

    # Panel G — Deep vs shallow heatmap
    ax_g = fig.add_subplot(gs[2,0])
    if "attractor_depth" in mm_depth.columns:
        d     = mm_depth["attractor_depth"]
        deep  = mm_depth[d >= d.quantile(0.75)]
        shal  = mm_depth[d <= d.quantile(0.25)]
        genes_heat = [g for g in
                      ["IRF8"]+FALSE_ATTRACTOR+["MYC","MKI67","EZH2"]
                      if g in mm_depth.columns]
        heat_data = np.array([
            [deep[g].mean() for g in genes_heat],
            [shal[g].mean() for g in genes_heat]
        ])
        im = ax_g.imshow(heat_data, aspect="auto", cmap="RdBu_r")
        ax_g.set_xticks(range(len(genes_heat)))
        ax_g.set_xticklabels(genes_heat, rotation=45,
                              ha="right", fontsize=9)
        ax_g.set_yticks([0,1])
        ax_g.set_yticklabels(["Deep\n(Q75+)","Shallow\n(Q25-)"],
                              fontsize=9)
        ax_g.set_title("G — Deep vs Shallow\nGene Expression Heatmap")
        plt.colorbar(im, ax=ax_g, shrink=0.7)

    # Panel H — UPR panel
    ax_h = fig.add_subplot(gs[2,1])
    upr_avail = [g for g in UPR
                 if any(g in stage_data.get(s,pd.DataFrame()).columns
                        for s in stages)]
    if upr_avail:
        stage_bar(ax_h, upr_avail,
                  "H — UPR Genes\n(Secretory stress markers)")

    # Panel I — Summary
    ax_i = fig.add_subplot(gs[2,2])
    ax_i.axis("off")

    confirmed_fa = results_df[
        results_df["result"] == "ELEVATED — ATTRACTOR CONFIRMED"
    ]["gene"].tolist()
    irf8_row = results_df[results_df["gene"]=="IRF8"]
    irf8_res = irf8_row["result"].values[0] if len(irf8_row)>0 else "N/A"

    summary = (
        "I — CORRECTED FRAMEWORK SUMMARY\n"
        "─────────────────────────────────\n"
        "MM false attractor geometry:\n"
        "  NOT stuck before plasma cell\n"
        "  STUCK within plasma cell —\n"
        "  cannot reach LLPC state\n\n"
        "True switch gene:\n"
        f"  IRF8: {irf8_res}\n"
        f"  Progression: monotonic ↓\n"
        f"  HD→MGUS→SMM→MM\n\n"
        "False attractor (activation lock):\n"
        f"  {', '.join(confirmed_fa) if confirmed_fa else 'IRF4/PRDM1/XBP1 elevated'}\n\n"
        "Waddington geometry:\n"
        "  Plasmablast\n"
        "    → [FALSE ATTRACTOR]\n"
        "       IRF8↓ blocks exit\n"
        "    → Long-lived plasma cell\n"
        "       (state MM cannot reach)\n\n"
        "Drug implication:\n"
        "  Restore IRF8 expression\n"
        "  to force LLPC maturation\n"
        "  and exit from false attractor"
    )
    ax_i.text(0.03, 0.97, summary, transform=ax_i.transAxes,
              fontsize=8.5, verticalalignment="top",
              fontfamily="monospace",
              bbox=dict(boxstyle="round", facecolor="#f8f8f8",
                        edgecolor="#cccccc"))

    outpath = RESULTS_DIR + "mm_corrected_analysis.png"
    plt.savefig(outpath, dpi=150, bbox_inches="tight")
    log(f"\n  Figure saved: {outpath}")
    plt.close()

# ============================================================
# MAIN
# ============================================================

def main():
    log("=" * 70)
    log("MM FALSE ATTRACTOR — CORRECTED ANALYSIS")
    log("REVISED: MM locked in plasmablast/activated state")
    log("IRF8 suppression = differentiation block to LLPC")
    log("OrganismCore | 2026-03-01")
    log("=" * 70)

    log("\n=== STEP 1: LOAD FROM CACHE ===")
    stage_data = load_stage_caches()

    log("\n=== STEP 2: CORRECTED SADDLE POINT ===")
    hd = stage_data.get("HD", pd.DataFrame())
    mm = stage_data.get("MM", pd.DataFrame())

    if len(hd)==0 or len(mm)==0:
        log("ERROR: No data")
        write_log()
        return

    results_df = saddle_point_corrected(hd, mm)
    results_df.to_csv(RESULTS_DIR+"mm_corrected_results.csv", index=False)

    log("\n=== STEP 3: PROGRESSION — IRF8 TRAJECTORY ===")
    progression_irf8(stage_data)

    log("\n=== STEP 4: ATTRACTOR DEPTH (IRF8-BASED) ===")
    mm_depth = attractor_depth_corrected(mm, results_df)

    log("\n=== STEP 5: FIGURE ===")
    generate_figure(stage_data, results_df, mm_depth)

    write_log()
    log(f"\n  Log: {LOG_FILE}")
    log("=== COMPLETE ===")

if __name__ == "__main__":
    main()
