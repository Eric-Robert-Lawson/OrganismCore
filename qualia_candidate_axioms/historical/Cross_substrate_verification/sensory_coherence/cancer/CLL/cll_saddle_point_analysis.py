"""
CLL FALSE ATTRACTOR ANALYSIS
OrganismCore — Document 80
False Attractor Framework — Cancer Validation #8
Session 2 — Lymphoid

CLL BIOLOGY:
  Chronic Lymphocytic Leukemia
  Mature-appearing CD5+ B cells
  that accumulate because they
  FAIL TO DIE not because they
  fail to differentiate.

  The false attractor in CLL is
  a SURVIVAL ATTRACTOR:
  Cells appear mature but lack
  the final apoptotic signal.
  They are stuck in a state that
  resembles completion but is not.

DESIGN:
  CLL cells:   GSE111014 day 0
               4 patients untreated
               15,007 cells
  Normal B:    GSE132509 PBMMC
               3 normal donors
               3,814 cells
  Cross-dataset: both 10X Chromium
                 same 33,694 gene panel

SWITCH GENE PREDICTIONS:
  IGHD   — naive mature B cell marker
  BTG1   — anti-proliferative
  FCRL5  — Fc receptor-like 5
  PRDM1  — Blimp1 — plasma cell fate

SCAFFOLD (should be ELEVATED in CLL):
  BCL2   — anti-apoptotic
           THE hallmark of CLL
           venetoclax targets this

INTERNAL CROSS-CHECK:
  IGKC   — confirmed B-ALL switch 83.7%
           in CLL should be EXPRESSED
           CLL cells are mature B cells

CONTROLS:
  CEBPA  — myeloid — should be flat
  SFTPC  — lung — zero
  CDX2   — colon — zero
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.io import mmread
from scipy import stats
import os
import gzip
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# CONFIGURATION
# ============================================================

CLL_DIR     = "/Users/ericlawson/cancer/CLL/"
ALL_CACHE   = "/Users/ericlawson/cancer/CLL/cll_saddle_results/normal_b_cache.pkl"
RESULTS_DIR = "/Users/ericlawson/cancer/CLL/cll_saddle_results/"
os.makedirs(RESULTS_DIR, exist_ok=True)
LOG_FILE    = RESULTS_DIR + "analysis_log.txt"

with open(LOG_FILE, "w") as f:
    f.write("")

def log(msg=""):
    print(msg)
    with open(LOG_FILE, "a") as f:
        f.write(str(msg) + "\n")

# Switch genes — survival attractor
CLL_SWITCH  = ["IGHD", "BTG1", "FCRL5", "PRDM1"]

# Scaffold — should be ELEVATED in CLL
SCAFFOLD    = ["BCL2", "MKI67", "CD19",
               "PAX5", "RAG1", "RAG2"]

# Internal cross-check
CROSS_CHECK = ["IGKC", "IGHM", "CD27"]

# Controls
CONTROLS    = ["CEBPA", "SFTPC", "CDX2"]

ALL_TARGET  = (CLL_SWITCH + SCAFFOLD +
               CROSS_CHECK + CONTROLS)

# Day 0 CLL samples
D0_SUFFIXES = ["CLL1_d0", "CLL5_d0",
               "CLL6_d0", "CLL8_d0"]

# ============================================================
# STEP 1: LOAD CLL DATA (GSE111014 day 0)
# ============================================================

def load_cll_data():
    log("=" * 56)
    log("STEP 1: LOADING CLL DATA (GSE111014)")
    log("=" * 56)

    cache = RESULTS_DIR + "cll_expr_cache.pkl"
    if os.path.exists(cache):
        log("Loading CLL from cache...")
        df = pd.read_pickle(cache)
        log(f"Cached shape: {df.shape}")
        return df

    log("Loading barcodes...")
    with gzip.open(CLL_DIR +
                   "GSE111014_barcodes.tsv.gz",
                   'rt') as f:
        barcodes = [line.strip() for line in f]
    log(f"Total barcodes: {len(barcodes)}")

    log("Loading genes...")
    gene_df = pd.read_csv(
        CLL_DIR + "GSE111014_genes.tsv.gz",
        sep="\t", header=None,
        compression='gzip',
        names=["ensembl", "symbol"])
    gene_list = gene_df["symbol"].tolist()
    log(f"Total genes: {len(gene_list)}")

    log("Loading matrix...")
    with gzip.open(CLL_DIR +
                   "GSE111014_matrix.mtx.gz",
                   'rb') as f:
        mat = mmread(f).tocsc()
    log(f"Matrix shape: {mat.shape}")

    if mat.shape[1] == len(gene_list):
        mat = mat.T.tocsc()

    # Filter to day 0 cells only
    d0_idx = [
        i for i, b in enumerate(barcodes)
        if any(b.endswith(s) for s in D0_SUFFIXES)
    ]
    log(f"Day 0 cells: {len(d0_idx)}")

    d0_barcodes = [barcodes[i] for i in d0_idx]

    # Extract patient labels
    patient_labels = []
    for b in d0_barcodes:
        parts = b.split("-scRNA-seq_")
        if len(parts) == 2:
            patient_labels.append(
                parts[1].split("_d")[0])
        else:
            patient_labels.append("unknown")

    # Find target gene indices
    target_idx   = []
    target_names = []
    for g in ALL_TARGET:
        if g in gene_list:
            idx = gene_list.index(g)
            target_idx.append(idx)
            target_names.append(g)

    log(f"Target genes found: "
        f"{len(target_names)}/{len(ALL_TARGET)}")
    missing = set(ALL_TARGET) - set(target_names)
    if missing:
        log(f"Missing: {missing}")

    # Extract submatrix
    sub = mat[target_idx, :][:, d0_idx].toarray().T
    df  = pd.DataFrame(sub,
                       index=d0_barcodes,
                       columns=target_names)
    df  = np.log1p(df)
    df["patient"]  = patient_labels
    df["sample"]   = "CLL_d0"
    df["celltype"] = "CLL"

    log(f"CLL data shape: {df.shape}")
    log("Patient distribution:")
    log(str(df["patient"].value_counts()))

    df.to_pickle(cache)
    log(f"Cached: {cache}")

    return df

# ============================================================
# STEP 2: LOAD NORMAL B CELLS (GSE132509 PBMMC)
# ============================================================

def load_normal_b():
    log("=" * 56)
    log("STEP 2: LOADING NORMAL B CELLS")
    log("(GSE132509 PBMMC — ALL dataset cache)")
    log("=" * 56)

    if not os.path.exists(ALL_CACHE):
        log("ERROR: ALL cache not found")
        log(f"Expected: {ALL_CACHE}")
        log("Run ALL analysis first")
        return pd.DataFrame()

    log("Loading ALL cache...")
    all_data = pd.read_pickle(ALL_CACHE)
    log(f"ALL cache shape: {all_data.shape}")

    normal_b = all_data[
        all_data["celltype"] == "B cells + Mono"
    ].copy()
    log(f"Normal B cells: {len(normal_b)}")

    if len(normal_b) == 0:
        log("WARNING: 'B cells + Mono' not found")
        log("Available celltypes:")
        log(str(all_data["celltype"].unique()))
        return pd.DataFrame()

    avail = [g for g in ALL_TARGET
             if g in normal_b.columns]
    missing = set(ALL_TARGET) - set(avail)
    log(f"Target genes in normal B: "
        f"{len(avail)}/{len(ALL_TARGET)}")
    if missing:
        log(f"Missing from normal B: {missing}")

    return normal_b

# ============================================================
# STEP 3: ALIGN GENE PANELS
# ============================================================

def align_panels(cll_df, normal_b):
    log("=" * 56)
    log("STEP 3: ALIGNING GENE PANELS")
    log("=" * 56)

    cll_genes    = set(cll_df.columns) - {
        "patient", "sample", "celltype"}
    normal_genes = set(normal_b.columns) - {
        "celltype", "sample"}

    shared = cll_genes & normal_genes
    log(f"CLL genes:    {len(cll_genes)}")
    log(f"Normal genes: {len(normal_genes)}")
    log(f"Shared:       {len(shared)}")

    shared_target = [g for g in ALL_TARGET
                     if g in shared]
    log(f"Shared target genes: {len(shared_target)}")
    log(f"Shared target list:  {shared_target}")

    return shared_target

# ============================================================
# STEP 4: COMPUTE SIGNATURE
# ============================================================

def compute_signature(cll_df, normal_b,
                      shared_genes):
    log("=" * 56)
    log("STEP 4: CLL FALSE ATTRACTOR ANALYSIS")
    log("=" * 56)
    log(f"CLL cells:    {len(cll_df)}")
    log(f"Normal B:     {len(normal_b)}")
    log()
    log("Switch genes:  should be LOW in CLL, HIGH in normal B")
    log("BCL2 scaffold: should be HIGH in CLL")
    log("IGKC cross:    should be HIGH in CLL (mature B cells)")
    log()

    def fmt_p(p):
        if np.isnan(p):  return "N/A      "
        if p < 0.001:    return f"{p:.2e} ***"
        if p < 0.01:     return f"{p:.4f} ** "
        if p < 0.05:     return f"{p:.4f} *  "
        return            f"{p:.4f}    "

    results = []

    for gene in shared_genes:
        cll_vals    = cll_df[gene].dropna()
        normal_vals = normal_b[gene].dropna()

        if len(cll_vals) < 5 or len(normal_vals) < 5:
            continue

        cll_mean    = cll_vals.mean()
        normal_mean = normal_vals.mean()

        suppression_pct = (
            (normal_mean - cll_mean) /
            (normal_mean + 1e-6) * 100
        )
        elevation_pct = (
            (cll_mean - normal_mean) /
            (normal_mean + 1e-6) * 100
        )

        _, pval_supp = stats.mannwhitneyu(
            normal_vals, cll_vals,
            alternative='greater')
        _, pval_elev = stats.mannwhitneyu(
            cll_vals, normal_vals,
            alternative='greater')

        is_switch   = gene in CLL_SWITCH
        is_scaffold = gene in SCAFFOLD
        is_cross    = gene in CROSS_CHECK
        is_control  = gene in CONTROLS

        role = ('SWITCH'   if is_switch   else
                'SCAFFOLD' if is_scaffold else
                'CROSS'    if is_cross    else
                'CONTROL')

        if is_switch:
            if suppression_pct > 30 and pval_supp < 0.05:
                result = "CONFIRMED"
            elif suppression_pct > 15:
                result = "PARTIAL"
            elif suppression_pct < -20:
                result = "INVERTED"
            else:
                result = "NOT CONFIRMED"

        elif is_scaffold:
            if gene == "BCL2":
                if elevation_pct > 20 and pval_elev < 0.05:
                    result = "SCAFFOLD CONFIRMED"
                elif elevation_pct > 0:
                    result = "SCAFFOLD ELEVATED"
                else:
                    result = "SCAFFOLD FLAT"
            else:
                result = ("SCAFFOLD HIGH"
                          if elevation_pct > 0
                          else "SCAFFOLD LOW")

        elif is_cross:
            if elevation_pct > 0:
                result = "CROSS: CLL > normal"
            elif suppression_pct > 30:
                result = "CROSS: suppressed"
            else:
                result = "CROSS: flat"

        else:
            result = ("CONTROL OK"
                      if abs(suppression_pct) < 30
                      else "CONTROL UNEXPECTED")

        results.append({
            'gene':            gene,
            'role':            role,
            'cll_expr':        round(cll_mean, 4),
            'normal_expr':     round(normal_mean, 4),
            'suppression_pct': round(suppression_pct, 1),
            'elevation_pct':   round(elevation_pct, 1),
            'pval_supp':       pval_supp,
            'pval_elev':       pval_elev,
            'result':          result
        })

        if suppression_pct > 0:
            direction = f"suppressed {suppression_pct:+.1f}%"
        else:
            direction = f"elevated   {elevation_pct:+.1f}%"

        flag = (
            "✓ CONFIRMED"     if result == "CONFIRMED"
            else "~ PARTIAL"  if result == "PARTIAL"
            else "✓ BCL2↑"    if result == "SCAFFOLD CONFIRMED"
            else "↑ SCAFFOLD" if "SCAFFOLD" in result
            else "↑ CLL>norm" if "CLL >" in result
            else "✓ CTRL OK"  if result == "CONTROL OK"
            else "✗ " + result
        )

        log(f"{gene:8} [{role:8}] | "
            f"CLL={cll_mean:.4f} "
            f"Normal={normal_mean:.4f} | "
            f"{direction:30} | "
            f"p_supp={fmt_p(pval_supp)} | "
            f"{flag}")

    results_df = pd.DataFrame(results)

    if len(results_df) == 0:
        log("WARNING: no results computed")
        return results_df

    sw     = results_df[results_df['role'] == 'SWITCH']
    n_sw_c = (sw['result'] == 'CONFIRMED').sum()
    n_sw_p = (sw['result'] == 'PARTIAL').sum()
    n_sw   = len(sw)

    log()
    log(f"Switch genes confirmed: {n_sw_c}/{n_sw}")
    log(f"Switch genes partial:   {n_sw_p}/{n_sw}")

    if n_sw_c >= 3:
        log("*** CLL FALSE ATTRACTOR CONFIRMED ***")
    elif n_sw_c + n_sw_p >= 2:
        log("** PARTIAL CLL CONFIRMATION **")
    else:
        log("--- CLL: insufficient confirmation")

    bcl2_row = results_df[results_df['gene'] == 'BCL2']
    if len(bcl2_row) > 0:
        log()
        log("BCL2 SCAFFOLD:")
        log(str(bcl2_row[['gene', 'cll_expr',
                           'normal_expr',
                           'elevation_pct',
                           'result']]))

    igkc_row = results_df[results_df['gene'] == 'IGKC']
    if len(igkc_row) > 0:
        log()
        log("IGKC CROSS-CHECK:")
        log("(Should be HIGH in CLL — mature B cells)")
        log(str(igkc_row[['gene', 'cll_expr',
                           'normal_expr',
                           'elevation_pct',
                           'result']]))

    return results_df

# ============================================================
# STEP 5: IBRUTINIB RESPONSE
# ============================================================

def ibrutinib_response(shared_genes=None):
    log()
    log("=" * 56)
    log("STEP 5: IBRUTINIB RESPONSE")
    log("Day 0 vs Day 120+ — does treatment")
    log("push cells toward normal B identity?")
    log("=" * 56)

    cache = RESULTS_DIR + "cll_full_cache.pkl"
    if os.path.exists(cache):
        log("Loading full CLL from cache...")
        full_df = pd.read_pickle(cache)
    else:
        log("Loading full matrix for all timepoints...")
        with gzip.open(
                CLL_DIR + "GSE111014_barcodes.tsv.gz",
                'rt') as f:
            barcodes = [line.strip() for line in f]

        gene_df = pd.read_csv(
            CLL_DIR + "GSE111014_genes.tsv.gz",
            sep="\t", header=None,
            compression='gzip',
            names=["ensembl", "symbol"])
        gene_list = gene_df["symbol"].tolist()

        with gzip.open(
                CLL_DIR + "GSE111014_matrix.mtx.gz",
                'rb') as f:
            mat = mmread(f).tocsc()

        if mat.shape[1] == len(gene_list):
            mat = mat.T.tocsc()

        target_idx   = []
        target_names = []
        for g in shared_genes:
            if g in gene_list:
                idx = gene_list.index(g)
                target_idx.append(idx)
                target_names.append(g)

        sub = mat[target_idx, :].toarray().T
        full_df = pd.DataFrame(
            sub, index=barcodes,
            columns=target_names)
        full_df = np.log1p(full_df)

        timepoints = []
        patients   = []
        for b in barcodes:
            parts = b.split("-scRNA-seq_")
            if len(parts) == 2:
                pt_time = parts[1]
                if "_d" in pt_time:
                    pt, t = pt_time.rsplit("_d", 1)
                    patients.append(pt)
                    timepoints.append(int(t))
                else:
                    patients.append("unknown")
                    timepoints.append(-1)
            else:
                patients.append("unknown")
                timepoints.append(-1)

        full_df["patient"]   = patients
        full_df["timepoint"] = timepoints
        full_df.to_pickle(cache)

    log("Timepoint distribution:")
    log(str(full_df["timepoint"].value_counts()
            .sort_index()))
    log()

    switch_avail = [g for g in CLL_SWITCH
                    if g in full_df.columns]
    if not switch_avail:
        log("No switch genes in full df")
        return

    log("Switch gene expression by timepoint:")
    log("(Does ibrutinib restore normal B identity?)")
    log()

    tp_groups = full_df.groupby("timepoint")
    for gene in switch_avail + ["BCL2"]:
        if gene not in full_df.columns:
            continue
        row = f"{gene:8}: "
        for tp, grp in tp_groups:
            mean = grp[gene].mean()
            row += f"d{tp}={mean:.3f}  "
        log(row)

# ============================================================
# STEP 6: FIGURE
# ============================================================

def generate_figure(results_df, cll_df, normal_b):
    log()
    log("=" * 56)
    log("STEP 6: GENERATING FIGURE")
    log("=" * 56)

    fig = plt.figure(figsize=(22, 14))
    gs  = gridspec.GridSpec(2, 3, figure=fig,
                            hspace=0.5, wspace=0.4)

    # Panel A: switch genes
    ax_a = fig.add_subplot(gs[0, :2])
    avail_sw = [g for g in CLL_SWITCH
                if (g in cll_df.columns and
                    g in normal_b.columns)]
    if avail_sw:
        x     = np.arange(len(avail_sw))
        width = 0.35
        c_means = [cll_df[g].mean()   for g in avail_sw]
        n_means = [normal_b[g].mean() for g in avail_sw]
        c_sems  = [cll_df[g].sem()    for g in avail_sw]
        n_sems  = [normal_b[g].sem()  for g in avail_sw]

        ax_a.bar(x - width/2, c_means, width,
                 yerr=c_sems, capsize=3,
                 label='CLL (day 0)',
                 color='darkred', alpha=0.85)
        ax_a.bar(x + width/2, n_means, width,
                 yerr=n_sems, capsize=3,
                 label='Normal B cells',
                 color='steelblue', alpha=0.85)
        ax_a.set_xticks(x)
        ax_a.set_xticklabels(avail_sw, fontsize=11)
        ax_a.set_ylabel("Mean log1p(UMI)", fontsize=10)
        ax_a.legend(fontsize=9)

        if len(results_df) > 0:
            for i, gene in enumerate(avail_sw):
                row = results_df[
                    results_df['gene'] == gene]
                if len(row) == 0:
                    continue
                row   = row.iloc[0]
                pct   = row['suppression_pct']
                color = ('darkgreen'
                         if row['result'] == 'CONFIRMED'
                         else 'gray')
                label = (f"{pct:.0f}%↓"
                         if pct > 0
                         else f"{abs(pct):.0f}%↑")
                ax_a.annotate(
                    label,
                    xy=(i,
                        max(c_means[i],
                            n_means[i]) + 0.005),
                    ha='center', fontsize=9,
                    color=color, fontweight='bold')

    ax_a.set_title(
        "A. CLL False Attractor — Switch Genes\n"
        "IGHD  BTG1  FCRL5  PRDM1\n"
        "Should be LOW in CLL, HIGH in normal B",
        fontsize=10, fontweight='bold')

    # Panel B: BCL2 scaffold + cross-check
    ax_b = fig.add_subplot(gs[1, :2])
    check_genes = (["BCL2"] +
                   [g for g in CROSS_CHECK
                    if (g in cll_df.columns and
                        g in normal_b.columns)])
    if check_genes:
        x     = np.arange(len(check_genes))
        width = 0.35
        c_means = [cll_df[g].mean()
                   if g in cll_df.columns else 0
                   for g in check_genes]
        n_means = [normal_b[g].mean()
                   if g in normal_b.columns else 0
                   for g in check_genes]

        ax_b.bar(x - width/2, c_means, width,
                 label='CLL (day 0)',
                 color='darkred', alpha=0.85)
        ax_b.bar(x + width/2, n_means, width,
                 label='Normal B cells',
                 color='steelblue', alpha=0.85)
        ax_b.set_xticks(x)
        ax_b.set_xticklabels(check_genes, fontsize=11)
        ax_b.set_ylabel("Mean log1p(UMI)", fontsize=10)
        ax_b.legend(fontsize=9)
        ax_b.axvline(x=0.5, color='gray',
                     linestyle='--', alpha=0.5)

    ax_b.set_title(
        "B. BCL2 Scaffold + IGKC Cross-Check\n"
        "BCL2 should be HIGH in CLL (survival attractor)\n"
        "IGKC should be HIGH in CLL "
        "(mature B cells — V(D)J complete)",
        fontsize=10, fontweight='bold')

    # Panel C: results table
    ax_c = fig.add_subplot(gs[0, 2])
    ax_c.axis('off')
    ax_c.set_title("C. CLL Results Summary",
                   fontsize=10,
                   fontweight='bold', pad=15)
    if len(results_df) > 0:
        sw = results_df[
            results_df['role'].isin(
                ['SWITCH', 'SCAFFOLD'])
        ][['gene', 'role',
           'suppression_pct',
           'result']].copy()
        if len(sw) > 0:
            sw.columns = ['Gene', 'Role',
                          'Supp%', 'Result']
            table = ax_c.table(
                cellText=sw.values,
                colLabels=sw.columns,
                loc='center',
                cellLoc='center')
            table.auto_set_font_size(False)
            table.set_fontsize(8)
            table.scale(1.1, 1.6)
            for i, (_, row) in enumerate(
                    sw.iterrows()):
                c = ('#c8e6c9'
                     if row['Result'] in
                     ['CONFIRMED',
                      'SCAFFOLD CONFIRMED']
                     else '#fff9c4')
                for j in range(len(sw.columns)):
                    table[i+1, j].set_facecolor(c)

    # Panel D: suppression bar chart
    ax_d = fig.add_subplot(gs[1, 2])
    if len(results_df) > 0:
        sw = results_df[
            results_df['role'] == 'SWITCH'
        ].sort_values('suppression_pct',
                      ascending=False)
        if len(sw) > 0:
            colors = [
                'darkgreen' if r == 'CONFIRMED'
                else 'orange' if r == 'PARTIAL'
                else 'gray'
                for r in sw['result']
            ]
            ax_d.barh(sw['gene'],
                      sw['suppression_pct'],
                      color=colors, alpha=0.85)
            ax_d.axvline(x=30, color='darkred',
                         linestyle='--', lw=1.5,
                         label='30% threshold')
            ax_d.axvline(x=0, color='black',
                         linewidth=0.8, alpha=0.5)
            ax_d.set_xlabel("Suppression (%)",
                            fontsize=9)
            ax_d.legend(fontsize=8)

    ax_d.set_title(
        "D. Switch Gene Suppression\n"
        "Green=confirmed  Orange=partial",
        fontsize=9, fontweight='bold')

    fig.suptitle(
        "CLL False Attractor — Survival Attractor\n"
        "GSE111014 (Rendeiro et al. 2020)  |  "
        "OrganismCore  |  Document 80\n"
        "15,007 CLL cells (day 0)  |  "
        "3,814 normal B cells (GSE132509)  |  "
        "4 CLL patients",
        fontsize=11, fontweight='bold')

    outpath = RESULTS_DIR + "cll_saddle_figure.png"
    plt.savefig(outpath, dpi=180,
                bbox_inches='tight')
    plt.close()
    log(f"Figure saved: {outpath}")

# ============================================================
# MAIN
# ============================================================

def main():
    log("=" * 56)
    log("CLL FALSE ATTRACTOR ANALYSIS")
    log("OrganismCore — False Attractor Framework")
    log("Cancer Validation #8 — Document 80")
    log("Survival attractor — mature B cells")
    log("that fail to undergo apoptosis")
    log("=" * 56)

    cll_df   = load_cll_data()
    normal_b = load_normal_b()

    if len(normal_b) == 0:
        log("ERROR: no normal B cells loaded")
        log("Run ALL analysis first to populate")
        log("GSE132509 cache")
        return

    shared_genes = align_panels(cll_df, normal_b)

    results_df = compute_signature(
        cll_df, normal_b, shared_genes)

    ibrutinib_response(ALL_TARGET)

    generate_figure(results_df, cll_df, normal_b)

    if len(results_df) > 0:
        results_df.to_csv(
            RESULTS_DIR + "cll_saddle_results.csv",
            index=False)

    log()
    log("=" * 56)
    log("CLL ANALYSIS COMPLETE")
    log(f"Results: {RESULTS_DIR}")
    log("=" * 56)


if __name__ == "__main__":
    main()
