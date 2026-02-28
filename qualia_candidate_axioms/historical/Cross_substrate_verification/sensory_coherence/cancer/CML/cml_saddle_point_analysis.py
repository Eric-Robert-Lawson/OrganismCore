"""
CML FALSE ATTRACTOR ANALYSIS
OrganismCore — Document 78
False Attractor Framework — Cancer Validation #6
Session 2 — Hematopoietic

CANCER TYPE: Chronic Myeloid Leukemia (CML)
DATA: GSE236233 — Warfvinge et al. 2024, eLife
      PMID: 38809238
      20,395 cells — 9 CML patients
      CD34+ enriched — stem and progenitor
      fractions (34p and 38n)
      10X Chromium scRNA-seq
      33,538 genes

COMPARISON:
  CML Primitive cells (3,910 cells)
      vs
  My cells (1,327 cells)
  (most myeloid-committed population
   available in CD34+ enriched dataset)

NOTE ON CONSERVATIVE NATURE:
  My cells are committed myeloid
  progenitors — NOT terminal
  mature neutrophils/granulocytes.
  True terminal granulocytes are
  CD34-negative and were excluded
  by the sorting protocol.
  Switch gene suppression in Primitive
  vs My will be UNDERESTIMATED
  relative to true mature granulocytes.
  Any confirmation here is conservative.
  The true signal against mature
  neutrophils would be larger.
  Follow-up: GSE173076 normal bone
  marrow with mature granulocytes.

FRAMEWORK PREDICTION:
  CML Primitive cells are the false
  attractor population — stuck below
  the granulocyte completion threshold.
  My cells are further along the path
  but still progenitors.

  PREDICTED SUPPRESSED (switch genes):
    CEBPA  — granulocyte master TF
             pioneer factor for myeloid
             terminal differentiation
    CEBPE  — late granulocyte maturation
             expressed at terminal
             neutrophil completion
    ELANE  — neutrophil elastase
             terminal granule protein
    CAMP   — cathelicidin antimicrobial
             peptide — terminal neutrophil
    LTF    — lactoferrin — terminal
             neutrophil secretory protein

  PREDICTED SCAFFOLD:
    CD34   — confirmed scaffold AML
             hematopoietic stem marker
             elevated in Primitive
    MPO    — myeloperoxidase
             GMP/progenitor marker
             expressed before terminal
             may be scaffold here

  CRITICAL TEST — AML SWITCH GENES:
    SPI1   — confirmed AML 90.5%
    KLF4   — confirmed AML 94.7%
    IRF8   — confirmed AML 69.5%
    If suppressed in CML Primitive
    vs My — same switch genes in two
    independent myeloid cancers.
    The switch genes are a property
    of the myeloid lineage.
    Not of the specific malignancy.
    First deliberate cross-cancer
    confirmation of the same switch
    gene set.

  CONTROLS (Session 1 confirmed):
    CDX2   — CRC 79.5%  — zero in blood
    MKI67  — proliferation scaffold
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
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# CONFIGURATION
# ============================================================

DATA_DIR    = "GEO/"
RESULTS_DIR = "./cml_saddle_results/"
os.makedirs(RESULTS_DIR, exist_ok=True)
LOG_FILE    = RESULTS_DIR + "analysis_log.txt"

with open(LOG_FILE, "w") as f:
    f.write("")

def log(msg=""):
    print(msg)
    with open(LOG_FILE, "a") as f:
        f.write(str(msg) + "\n")

SWITCH_CANDIDATES = ["CEBPA", "CEBPE", "ELANE", "CAMP", "LTF"]
AML_SWITCH_GENES  = ["SPI1", "KLF4", "IRF8"]
SCAFFOLD_GENES    = ["CD34", "MPO", "MKI67"]
CONTROL_GENES     = ["CDX2", "CSF3R"]

ALL_TARGET = (SWITCH_CANDIDATES +
              AML_SWITCH_GENES +
              SCAFFOLD_GENES +
              CONTROL_GENES)

PRIMITIVE_LABEL = "Primitive"
MY_LABEL        = "My"
LABEL_COL       = "transferred_labels"

# ============================================================
# STEP 1: LOAD ALL SAMPLES
# ============================================================

def load_all_samples():
    log("=" * 56)
    log("STEP 1: LOADING ALL SAMPLES")
    log("=" * 56)

    cache = RESULTS_DIR + "expr_cache.parquet"
    if os.path.exists(cache):
        log("Loading from cache...")
        expr = pd.read_parquet(cache)
        log(f"Cached shape: {expr.shape}")
        return expr

    samples = []
    for f in sorted(os.listdir(DATA_DIR)):
        if not f.endswith("_metadata.txt"):
            continue
        sample_name = f.replace("_metadata.txt", "")
        meta_path  = DATA_DIR + f
        cells_path = DATA_DIR + sample_name + "_cells.txt"
        genes_path = DATA_DIR + sample_name + "_genes.txt"
        mtx_path   = DATA_DIR + sample_name + "_counts.mtx"

        if not all(os.path.exists(p) for p in
                   [cells_path, genes_path, mtx_path]):
            log(f"Skipping {sample_name} — missing files")
            continue

        log(f"Loading {sample_name}...")

        meta  = pd.read_csv(meta_path)
        cells = pd.read_csv(cells_path, header=None,
                            names=["barcode"])
        genes = pd.read_csv(genes_path, header=None,
                            names=["gene"])

        n_genes = len(genes)
        n_cells = len(cells)

        mat = mmread(mtx_path)
        mat_csc = mat.tocsc()

        if mat_csc.shape[0] == n_genes:
            orientation = "genes_x_cells"
        elif mat_csc.shape[1] == n_genes:
            orientation = "cells_x_genes"
            mat_csc = mat_csc.T.tocsc()
        else:
            log(f"  WARNING: shape {mat_csc.shape} "
                f"vs {n_genes} genes {n_cells} cells")
            orientation = "unknown"

        log(f"  Orientation: {orientation} "
            f"shape: {mat_csc.shape}")

        cell_ids = [f"{sample_name}_{b}"
                    for b in cells["barcode"]]

        gene_list    = genes["gene"].tolist()
        target_idx   = []
        target_names = []
        for g in ALL_TARGET:
            if g in gene_list:
                idx = gene_list.index(g)
                target_idx.append(idx)
                target_names.append(g)

        sub = mat_csc[target_idx, :].toarray().T
        df  = pd.DataFrame(sub,
                           index=cell_ids,
                           columns=target_names)

        df = np.log1p(df)

        meta.index = cell_ids
        df[LABEL_COL] = meta[LABEL_COL].values
        df["sample"]  = sample_name

        samples.append(df)
        log(f"  {sample_name}: {df.shape[0]} cells")

    combined = pd.concat(samples, ignore_index=False)
    log(f"\nTotal cells loaded: {len(combined)}")

    combined.to_parquet(cache)
    log(f"Cached: {cache}")

    return combined

# ============================================================
# STEP 2: CLASSIFY AND SUMMARIZE
# ============================================================

def classify(combined):
    log("=" * 56)
    log("STEP 2: CLASSIFY AND SUMMARIZE")
    log("=" * 56)

    log("Cell type distribution:")
    log(str(combined[LABEL_COL].value_counts()))
    log()

    prim = combined[combined[LABEL_COL] == PRIMITIVE_LABEL]
    my   = combined[combined[LABEL_COL] == MY_LABEL]

    log(f"Primitive cells: {len(prim)}")
    log(f"My cells:        {len(my)}")

    avail = [g for g in ALL_TARGET if g in combined.columns]
    log(f"\nAvailable target genes: {avail}")

    log("\nMean expression — Primitive vs My:")
    means = combined[
        combined[LABEL_COL].isin([PRIMITIVE_LABEL, MY_LABEL])
    ].groupby(LABEL_COL)[avail].mean()
    log(str(means.round(4)))

    return prim, my, avail

# ============================================================
# STEP 3: SADDLE POINT SIGNATURE
# ============================================================

def compute_signature(combined, prim, my, avail):
    log("=" * 56)
    log("STEP 3: SADDLE POINT SIGNATURE")
    log("=" * 56)
    log(f"Reference (further differentiated): {MY_LABEL}")
    log(f"Blocked (false attractor):          {PRIMITIVE_LABEL}")
    log()
    log("CONSERVATIVE NOTE:")
    log("  My cells are NOT terminal granulocytes.")
    log("  Any suppression seen here is a lower bound.")
    log("  True signal vs mature neutrophils is larger.")
    log()
    log("CRITICAL TEST:")
    log("  SPI1, KLF4, IRF8 — confirmed AML switches.")
    log("  If confirmed here — same switch genes in two")
    log("  independent myeloid cancers.")
    log()

    results = []
    analysis_genes = (SWITCH_CANDIDATES +
                      AML_SWITCH_GENES +
                      SCAFFOLD_GENES +
                      CONTROL_GENES)

    def fmt_p(p):
        if np.isnan(p):   return "N/A      "
        if p < 0.001:     return f"{p:.2e} ***"
        if p < 0.01:      return f"{p:.4f} ** "
        if p < 0.05:      return f"{p:.4f} *  "
        return             f"{p:.4f}    "

    for gene in analysis_genes:
        if gene not in combined.columns:
            continue

        prim_vals = prim[gene].dropna()
        my_vals   = my[gene].dropna()

        if len(prim_vals) < 5 or len(my_vals) < 5:
            continue

        prim_mean = prim_vals.mean()
        my_mean   = my_vals.mean()

        suppression_pct = (my_mean - prim_mean) / (my_mean + 1e-6) * 100
        elevation_pct   = (prim_mean - my_mean) / (my_mean + 1e-6) * 100

        _, pval_supp = stats.mannwhitneyu(
            my_vals, prim_vals, alternative='greater')
        _, pval_elev = stats.mannwhitneyu(
            prim_vals, my_vals, alternative='greater')

        is_switch   = gene in SWITCH_CANDIDATES
        is_aml      = gene in AML_SWITCH_GENES
        is_scaffold = gene in SCAFFOLD_GENES
        is_control  = gene in CONTROL_GENES

        role = ('SWITCH'   if is_switch   else
                'AML_GENE' if is_aml      else
                'SCAFFOLD' if is_scaffold else
                'CONTROL')

        if is_switch or is_aml:
            if suppression_pct > 30 and pval_supp < 0.05:
                result = "CONFIRMED"
            elif suppression_pct > 15:
                result = "PARTIAL"
            elif suppression_pct < -20:
                result = "INVERTED"
            else:
                result = "NOT CONFIRMED"
        elif is_scaffold:
            if suppression_pct < 20:
                result = "SCAFFOLD OK"
            else:
                result = "SCAFFOLD UNEXPECTED"
        else:
            if abs(suppression_pct) < 30:
                result = "CONTROL OK"
            else:
                result = "CONTROL UNEXPECTED"

        results.append({
            'gene':            gene,
            'role':            role,
            'prim_expr':       round(prim_mean, 4),
            'my_expr':         round(my_mean, 4),
            'suppression_pct': round(suppression_pct, 1),
            'pval_supp':       pval_supp,
            'result':          result
        })

        direction = (
            f"suppressed {suppression_pct:+.1f}%"
            if suppression_pct > 0
            else f"elevated   {elevation_pct:+.1f}%"
        )

        flag = (
            "✓ CONFIRMED" if result == "CONFIRMED"   else
            "~ PARTIAL"   if result == "PARTIAL"      else
            "✓ SCAFFOLD"  if result == "SCAFFOLD OK"  else
            "✓ CTRL"      if result == "CONTROL OK"   else
            "✗ " + result
        )

        aml_marker = (
            "  ← AML cross-cancer test"
            if is_aml else ""
        )

        log(f"{gene:8} [{role:10}] | "
            f"Prim={prim_mean:.4f} "
            f"My={my_mean:.4f} | "
            f"{direction:30} | "
            f"p={fmt_p(pval_supp)} | "
            f"{flag}{aml_marker}")

    results_df = pd.DataFrame(results)
    results_df.to_csv(
        RESULTS_DIR + "cml_saddle_results.csv", index=False)

    n_sw_c = (results_df[results_df['role'] == 'SWITCH']
              ['result'] == 'CONFIRMED').sum()
    n_sw_p = (results_df[results_df['role'] == 'SWITCH']
              ['result'] == 'PARTIAL').sum()
    n_sw   = len(results_df[results_df['role'] == 'SWITCH'])

    n_aml_c = (results_df[results_df['role'] == 'AML_GENE']
               ['result'] == 'CONFIRMED').sum()
    n_aml   = len(results_df[results_df['role'] == 'AML_GENE'])

    log()
    log("=" * 56)
    log("CML FRAMEWORK PREDICTION RESULT")
    log("=" * 56)
    log(f"CML switch genes confirmed: {n_sw_c}/{n_sw}")
    log(f"CML switch genes partial:   {n_sw_p}/{n_sw}")
    log(f"AML genes in CML:           {n_aml_c}/{n_aml}")
    log()
    log("CRITICAL TEST — AML SWITCH GENES IN CML:")
    for _, row in results_df[
        results_df['role'] == 'AML_GENE'
    ].iterrows():
        log(f"  {row['gene']:6}: "
            f"{row['suppression_pct']:+.1f}% "
            f"[{row['result']}]")

    if n_aml_c == n_aml and n_aml > 0:
        log()
        log("*** CROSS-CANCER MYELOID CONFIRMATION ***")
        log("AML switch genes confirmed in CML.")
        log("Same switch genes. Two myeloid cancers.")
        log("Switch genes are a property of the")
        log("myeloid lineage. Not the malignancy.")
        log("The invariant deepens.")
    elif n_aml_c > 0:
        log()
        log("** PARTIAL CROSS-CANCER CONFIRMATION **")

    log()
    if n_sw_c >= 2:
        log("*** CML FALSE ATTRACTOR CONFIRMED ***")
    elif n_sw_c + n_sw_p >= 2:
        log("** PARTIAL CML CONFIRMATION **")
        log("Conservative comparison — My cells are")
        log("not terminal granulocytes.")
        log("True signal vs mature neutrophils larger.")

    return results_df

# ============================================================
# STEP 4: DEPTH ANALYSIS
# ============================================================

def depth_analysis(combined, avail):
    log("=" * 56)
    log("STEP 4: FALSE ATTRACTOR DEPTH ANALYSIS")
    log("=" * 56)
    log("Testing: switch gene expression along")
    log("differentiation hierarchy.")
    log("Primitive → MPP2 → MPP1 → My/Ly → My")
    log()

    hierarchy    = ["Primitive", "MPP2", "MPP1", "My/Ly", "My"]
    switch_genes = [g for g in
                    (SWITCH_CANDIDATES + AML_SWITCH_GENES)
                    if g in combined.columns]

    log(f"{'Stage':12} | " +
        " | ".join(f"{g:8}" for g in switch_genes))
    log("-" * (14 + 11 * len(switch_genes)))

    for stage in hierarchy:
        cells = combined[combined[LABEL_COL] == stage]
        if len(cells) < 10:
            continue
        means = [
            f"{cells[g].mean():.4f}"
            if g in cells.columns else "  N/A  "
            for g in switch_genes
        ]
        log(f"{stage:12} | " +
            " | ".join(f"{m:8}" for m in means))

    log()
    log("If values increase Primitive → My:")
    log("False attractor depth is real.")
    log("More primitive = more suppressed.")
    log("Waddington geometry directly observed.")

# ============================================================
# STEP 5: FIGURE
# ============================================================

def generate_figure(combined, results_df, avail):
    log("=" * 56)
    log("STEP 5: GENERATING FIGURE")
    log("=" * 56)

    prim = combined[combined[LABEL_COL] == PRIMITIVE_LABEL]
    my   = combined[combined[LABEL_COL] == MY_LABEL]

    plot_genes = [g for g in
                  (SWITCH_CANDIDATES +
                   AML_SWITCH_GENES +
                   SCAFFOLD_GENES)
                  if g in combined.columns]

    fig = plt.figure(figsize=(20, 12))
    gs  = gridspec.GridSpec(2, 3, figure=fig,
                            hspace=0.5, wspace=0.4)

    # ---- Panel A: Bar chart ----
    ax_a = fig.add_subplot(gs[0, :])
    x     = np.arange(len(plot_genes))
    width = 0.35

    prim_means = [prim[g].mean() if g in prim.columns else 0
                  for g in plot_genes]
    my_means   = [my[g].mean()   if g in my.columns   else 0
                  for g in plot_genes]
    prim_sems  = [prim[g].sem()  if g in prim.columns else 0
                  for g in plot_genes]
    my_sems    = [my[g].sem()    if g in my.columns   else 0
                  for g in plot_genes]

    ax_a.bar(x - width/2, prim_means, width,
             yerr=prim_sems, capsize=3,
             label='Primitive CML (false attractor)',
             color='crimson', alpha=0.85)
    ax_a.bar(x + width/2, my_means, width,
             yerr=my_sems, capsize=3,
             label='My (myeloid committed)',
             color='steelblue', alpha=0.85)

    ax_a.set_xticks(x)
    ax_a.set_xticklabels(plot_genes, fontsize=9,
                          rotation=15)
    ax_a.set_ylabel("Mean log1p(UMI)", fontsize=11)
    ax_a.set_title(
        "A. CML False Attractor Gap\n"
        "Red = Primitive CML  |  Blue = My (myeloid committed)\n"
        "Switch: CEBPA CEBPE ELANE CAMP LTF  |  "
        "AML cross-cancer: SPI1 KLF4 IRF8  |  "
        "Scaffold: CD34 MPO MKI67",
        fontsize=10, fontweight='bold')
    ax_a.legend(fontsize=10)

    n_s = len(SWITCH_CANDIDATES)
    n_a = len(AML_SWITCH_GENES)
    ax_a.axvline(x=n_s - 0.5, color='gray',
                 linestyle='--', alpha=0.4)
    ax_a.axvline(x=n_s + n_a - 0.5, color='gray',
                 linestyle='--', alpha=0.4)

    if results_df is not None:
        for i, gene in enumerate(plot_genes):
            row = results_df[results_df['gene'] == gene]
            if len(row) == 0:
                continue
            row   = row.iloc[0]
            pct   = row['suppression_pct']
            color = ('darkgreen'   if row['result'] == 'CONFIRMED'
                     else 'darkorange' if 'SCAFFOLD' in row['result']
                     else 'gray')
            label = (f"{pct:.0f}%↓" if pct > 0
                     else f"{abs(pct):.0f}%↑")
            ax_a.annotate(
                label,
                xy=(i, max(prim_means[i],
                           my_means[i]) + 0.01),
                ha='center', fontsize=8,
                color=color, fontweight='bold')

    # ---- Panel B: Differentiation depth ----
    ax_b = fig.add_subplot(gs[1, 0])
    hierarchy   = ["Primitive", "MPP2", "MPP1", "My/Ly", "My"]
    depth_genes = [g for g in
                   (SWITCH_CANDIDATES[:2] +
                    AML_SWITCH_GENES[:2])
                   if g in combined.columns]

    for gene in depth_genes:
        stage_means  = []
        stage_labels = []
        for stage in hierarchy:
            cells = combined[combined[LABEL_COL] == stage]
            if len(cells) >= 10 and gene in cells.columns:
                stage_means.append(cells[gene].mean())
                stage_labels.append(stage)
        if stage_means:
            ax_b.plot(stage_labels, stage_means,
                      '-o', linewidth=2,
                      markersize=7, label=gene)

    ax_b.set_ylabel("Mean log1p(UMI)", fontsize=9)
    ax_b.set_xticklabels(ax_b.get_xticklabels(),
                          rotation=20, fontsize=8)
    ax_b.set_title(
        "B. Switch Gene Expression\n"
        "Along Differentiation Hierarchy\n"
        "Primitive → My",
        fontsize=9, fontweight='bold')
    ax_b.legend(fontsize=8)

    # ---- Panel C: Suppression bar ----
    ax_c = fig.add_subplot(gs[1, 1])
    if results_df is not None:
        plot_df = results_df[
            results_df['gene'].isin(plot_genes)
        ].sort_values('suppression_pct',
                      ascending=False).copy()

        bar_colors = []
        for _, row in plot_df.iterrows():
            if row['role'] == 'SWITCH':
                bar_colors.append('crimson')
            elif row['role'] == 'AML_GENE':
                bar_colors.append('darkorange')
            else:
                bar_colors.append('steelblue')

        ax_c.barh(plot_df['gene'],
                  plot_df['suppression_pct'],
                  color=bar_colors, alpha=0.82,
                  edgecolor='white')
        ax_c.axvline(x=30, color='darkred',
                     linestyle='--', lw=1.5,
                     label='30% threshold')
        ax_c.axvline(x=0, color='black',
                     linewidth=0.8, alpha=0.5)
        ax_c.set_xlabel(
            "Suppression in Primitive (%)",
            fontsize=9)
        ax_c.set_title(
            "C. Direction and Magnitude\n"
            "Red=CML switch  "
            "Orange=AML cross-cancer  "
            "Blue=scaffold",
            fontsize=9, fontweight='bold')
        ax_c.legend(fontsize=9)

    # ---- Panel D: Results table ----
    ax_d = fig.add_subplot(gs[1, 2])
    ax_d.axis('off')
    if results_df is not None:
        tbl = results_df[[
            'gene', 'role', 'suppression_pct', 'result'
        ]].copy()
        tbl['pval'] = results_df['pval_supp'].apply(
            lambda p: f"{p:.2e}"
            if not np.isnan(p) else "N/A")
        tbl = tbl[['gene', 'role',
                   'suppression_pct', 'pval', 'result']]
        tbl.columns = ['Gene', 'Role', 'Supp%',
                       'p-val', 'Result']

        table = ax_d.table(
            cellText=tbl.values,
            colLabels=tbl.columns,
            loc='center', cellLoc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(7)
        table.scale(1.0, 1.5)

        colors = {
            'CONFIRMED':   '#c8e6c9',
            'PARTIAL':     '#fff9c4',
            'SCAFFOLD OK': '#e3f2fd',
            'CONTROL OK':  '#f3e5f5',
        }
        for i, (_, row) in enumerate(tbl.iterrows()):
            c = colors.get(str(row['Result']), 'white')
            for j in range(len(tbl.columns)):
                table[i + 1, j].set_facecolor(c)

    ax_d.set_title("D. Full Results Table",
                   fontsize=10, fontweight='bold',
                   pad=20)

    fig.suptitle(
        "CML False Attractor — Primitive vs Myeloid Committed\n"
        "GSE236233 Warfvinge et al. 2024  |  "
        "OrganismCore  |  Document 78\n"
        "Conservative: My cells are progenitors, "
        "not terminal granulocytes",
        fontsize=11, fontweight='bold')

    outpath = RESULTS_DIR + "cml_saddle_figure.png"
    plt.savefig(outpath, dpi=180, bbox_inches='tight')
    plt.close()
    log(f"Figure saved: {outpath}")

# ============================================================
# MAIN
# ============================================================

def main():
    log("=" * 56)
    log("CML FALSE ATTRACTOR ANALYSIS")
    log("OrganismCore — False Attractor Framework")
    log("Cancer Validation #6 — Document 78")
    log("Session 2 — Hematopoietic")
    log("=" * 56)

    combined = load_all_samples()

    prim, my, avail = classify(combined)

    results_df = compute_signature(
        combined, prim, my, avail)

    depth_analysis(combined, avail)

    generate_figure(combined, results_df, avail)

    log()
    log("=" * 56)
    log("CML ANALYSIS COMPLETE")
    log(f"Results: {RESULTS_DIR}")
    log("=" * 56)


if __name__ == "__main__":
    main()
