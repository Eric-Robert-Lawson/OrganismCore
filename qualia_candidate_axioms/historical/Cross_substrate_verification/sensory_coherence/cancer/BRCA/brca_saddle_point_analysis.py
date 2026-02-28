"""
BRCA FALSE ATTRACTOR ANALYSIS
OrganismCore — Document 75
False Attractor Framework — Cancer Validation #4
February 28, 2026

CANCER TYPE: Breast Cancer (BRCA)
DATA: GSE176078 — Wu et al. 2021, Nature Genetics
      PMID: 34493872
      100,064 cells — 26 primary tumors
      ER+, HER2+, TNBC subtypes
      10X Chromium scRNA-seq

FILE STRUCTURE:
  Wu_etal_2021_BRCA_scRNASeq/
    count_matrix_sparse.mtx   — genes x cells
    count_matrix_genes.tsv    — gene names
    count_matrix_barcodes.tsv — cell barcodes
    metadata.csv              — cell annotations

KEY METADATA COLUMNS:
  celltype_major:  9 major types
  celltype_minor:  29 subtypes
  celltype_subset: 49 fine-grained types
  subtype:         ER+, HER2+, TNBC

KEY POPULATIONS:
  Normal endpoint:
    Mature Luminal         1,265 cells
    (terminal luminal differentiation)
  Progenitor (scaffold):
    Luminal Progenitors    1,992 cells
  False attractor candidates:
    Cancer Basal SC        4,312 cells
    (dedifferentiated TNBC-like)
    Cancer LumA SC         7,742 cells
    Cancer Cycling         5,359 cells

FRAMEWORK PREDICTION:
  The false attractor in BRCA is the
  basal/stem-like state. These cells
  have lost luminal identity and are
  stuck in a dedifferentiated progenitor
  state — unable to complete the
  transition to mature luminal epithelium.

  PRIMARY COMPARISON:
    Cancer Basal SC vs Mature Luminal

  PREDICTED SUPPRESSED (switch genes):
    FOXA1  — luminal pioneer TF
             opens chromatin for ESR1
    GATA3  — luminal identity master TF
             most mutated gene in ER+ BRCA
    ESR1   — estrogen receptor
             terminal luminal marker

  PREDICTED ELEVATED (false attractor
  drivers):
    SOX2   — confirmed elevated in GBM
    MYC    — BRCA proliferation driver
    EGFR   — confirmed GBM, TNBC driver
    KRT5   — basal keratin (alternative
             identity marker)

  CONTROLS (confirmed switch genes from
  all three prior cancers):
    SOX10  — GBM: 88.6% suppressed
    MBP    — GBM: 89.6% suppressed
    CDX2   — CRC: 79.5% suppressed
    SPI1   — AML: 90.5% suppressed

  SCAFFOLD GENES (should be present
  in both luminal and basal — lineage
  identity throughout hierarchy):
    KRT8   — epithelial marker
             (present in both luminal
             and basal epithelium)
    MKI67  — cycling marker

  SECONDARY COMPARISON:
    Cancer Basal SC vs Luminal Progenitors
    Tests whether basal cells are below
    even the progenitor state — or
    whether they are a parallel branch.
"""

import pandas as pd
import numpy as np
import scipy.io
import scipy.sparse
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

DATA_DIR    = "Wu_etal_2021_BRCA_scRNASeq/"
MTX_FILE    = DATA_DIR + "count_matrix_sparse.mtx"
GENES_FILE  = DATA_DIR + "count_matrix_genes.tsv"
BARCODES_FILE = DATA_DIR + "count_matrix_barcodes.tsv"
META_FILE   = DATA_DIR + "metadata.csv"
RESULTS_DIR = "./brca_saddle_results/"
os.makedirs(RESULTS_DIR, exist_ok=True)
LOG_FILE    = RESULTS_DIR + "analysis_log.txt"

with open(LOG_FILE, "w") as f:
    f.write("")

def log(msg=""):
    print(msg)
    with open(LOG_FILE, "a") as f:
        f.write(str(msg) + "\n")

# ---- Target genes ----

# PREDICTED SUPPRESSED in basal vs mature luminal
SADDLE_CANDIDATES = ["FOXA1", "GATA3", "ESR1"]

# PREDICTED ELEVATED in basal (false attractor)
ELEVATED_PREDICTED = ["SOX2", "MYC", "EGFR", "KRT5"]

# CONTROLS — confirmed switch genes from prior cancers
# Should be flat/absent in breast tissue
CONTROL_GENES = ["SOX10", "MBP", "CDX2", "SPI1"]

# SCAFFOLD — epithelial identity, both populations
SCAFFOLD_GENES = ["KRT8", "MKI67", "AR", "ERBB2"]

ALL_TARGET = (SADDLE_CANDIDATES +
              ELEVATED_PREDICTED +
              CONTROL_GENES +
              SCAFFOLD_GENES)

# Cell populations
MATURE_LUMINAL  = "Mature Luminal"
CANCER_BASAL    = "Cancer Basal SC"
LUMINAL_PROG    = "Luminal Progenitors"
CANCER_LUMA     = "Cancer LumA SC"
CANCER_CYCLING  = "Cancer Cycling"
CT_COL          = "celltype_subset"

# ============================================================
# STEP 1: LOAD METADATA
# ============================================================

def load_metadata():
    log("="*56)
    log("STEP 1: LOADING METADATA")
    log("="*56)

    meta = pd.read_csv(META_FILE, index_col=0)
    log(f"Loaded: {meta.shape[0]} cells")
    log(f"Columns: {meta.columns.tolist()}")

    log(f"\ncelltype_subset distribution:")
    log(str(meta[CT_COL].value_counts()))

    log(f"\nSubtype distribution:")
    log(str(meta['subtype'].value_counts()))

    # Tag our populations
    meta['is_mature_luminal'] = (
        meta[CT_COL] == MATURE_LUMINAL
    )
    meta['is_cancer_basal'] = (
        meta[CT_COL] == CANCER_BASAL
    )
    meta['is_luminal_prog'] = (
        meta[CT_COL] == LUMINAL_PROG
    )
    meta['is_cancer_luma'] = (
        meta[CT_COL] == CANCER_LUMA
    )

    log(f"\nMature Luminal:      "
        f"{meta['is_mature_luminal'].sum()}")
    log(f"Cancer Basal SC:     "
        f"{meta['is_cancer_basal'].sum()}")
    log(f"Luminal Progenitors: "
        f"{meta['is_luminal_prog'].sum()}")
    log(f"Cancer LumA SC:      "
        f"{meta['is_cancer_luma'].sum()}")

    return meta

# ============================================================
# STEP 2: LOAD MTX EXPRESSION
# ============================================================

def load_mtx_expression(meta):
    log("="*56)
    log("STEP 2: LOADING MTX EXPRESSION")
    log("="*56)

    cache = RESULTS_DIR + "expr_cache.csv"
    if os.path.exists(cache):
        log("Loading from cache...")
        expr = pd.read_csv(cache, index_col=0)
        log(f"Cached: {expr.shape}")
        return expr

    # Load genes
    genes_df = pd.read_csv(
        GENES_FILE, header=None, sep='\t'
    )
    # Handle 1 or 2 column gene files
    if genes_df.shape[1] >= 2:
        genes = genes_df.iloc[:, 1].tolist()
    else:
        genes = genes_df.iloc[:, 0].tolist()
    log(f"Genes: {len(genes)}")
    log(f"Sample: {genes[:5]}")

    # Load barcodes
    barcodes_df = pd.read_csv(
        BARCODES_FILE, header=None, sep='\t'
    )
    barcodes = barcodes_df.iloc[:, 0].tolist()
    log(f"Barcodes: {len(barcodes)}")
    log(f"Sample: {barcodes[:3]}")

    # Check target genes
    found   = [g for g in ALL_TARGET if g in genes]
    missing = [g for g in ALL_TARGET if g not in genes]
    log(f"\nTarget genes found: {found}")
    if missing:
        log(f"Missing: {missing}")

    if not found:
        log("ERROR: No target genes found.")
        return None

    # Load sparse matrix
    log(f"\nLoading MTX matrix...")
    mat = scipy.io.mmread(MTX_FILE)
    mat = scipy.sparse.csr_matrix(mat)
    log(f"Matrix shape: {mat.shape} (genes x cells)")

    # Extract target genes
    log(f"Extracting {len(found)} target genes...")
    gene_to_idx = {g: i for i, g in enumerate(genes)}

    expr_dict = {}
    for gene in found:
        idx = gene_to_idx[gene]
        row = mat[idx, :].toarray().flatten()
        # Log-normalize
        row_log = np.log1p(row)
        expr_dict[gene] = row_log
        log(f"  {gene}: "
            f"mean={row_log.mean():.4f} "
            f"max={row_log.max():.4f} "
            f"nonzero={np.count_nonzero(row)}")

    expr = pd.DataFrame(expr_dict, index=barcodes)
    log(f"\nExpression: {expr.shape}")

    expr.to_csv(cache)
    log(f"Cached: {cache}")

    return expr

# ============================================================
# STEP 3: MERGE AND COMPUTE PROFILES
# ============================================================

def compute_profiles(expr, meta):
    log("="*56)
    log("STEP 3: EXPRESSION PROFILES")
    log("="*56)

    common = expr.index.intersection(meta.index)
    log(f"Common cells: {len(common)}")

    if len(common) == 0:
        log("Index mismatch. Trying barcode trimming...")
        # Sometimes barcodes have sample prefix
        expr_idx   = pd.Series(expr.index)
        meta_idx   = pd.Series(meta.index)
        # Try matching on suffix
        expr.index = expr.index.str.split('_').str[-1]
        meta.index = meta.index.str.split('_').str[-1]
        common = expr.index.intersection(meta.index)
        log(f"After trim: {len(common)}")

    if len(common) < 10:
        log("ERROR: Cannot align.")
        return None, None, None

    expr_a = expr.loc[common]
    meta_a = meta.loc[common]

    combined = expr_a.copy()
    combined[CT_COL]             = meta_a[CT_COL].values
    combined['subtype']          = meta_a['subtype'].values
    combined['is_mature_luminal']= (
        meta_a['is_mature_luminal'].values
    )
    combined['is_cancer_basal']  = (
        meta_a['is_cancer_basal'].values
    )
    combined['is_luminal_prog']  = (
        meta_a['is_luminal_prog'].values
    )
    combined['is_cancer_luma']   = (
        meta_a['is_cancer_luma'].values
    )

    available_genes = [g for g in ALL_TARGET
                       if g in combined.columns]
    log(f"Genes available: {available_genes}")

    # Primary comparison populations
    primary = combined[
        combined[CT_COL].isin(
            [MATURE_LUMINAL, CANCER_BASAL]
        )
    ].copy()

    log(f"\nPrimary comparison cells:")
    log(str(primary[CT_COL].value_counts()))

    grouped   = primary.groupby(CT_COL)[available_genes]
    traj_mean = grouped.mean()
    traj_sem  = grouped.sem()

    log(f"\nMean expression — Mature Luminal vs "
        f"Cancer Basal:")
    log(str(traj_mean.round(4)))

    return combined, {
        'mean': traj_mean,
        'sem':  traj_sem
    }, available_genes

# ============================================================
# STEP 4: SADDLE POINT SIGNATURE
# ============================================================

def compute_saddle_point_signature(
        combined, traj_stats, available_genes):
    log("="*56)
    log("STEP 4: SADDLE POINT SIGNATURE")
    log("="*56)
    log("FRAMEWORK PREDICTION (BRCA):")
    log(f"  Reference: {MATURE_LUMINAL}")
    log(f"  Blocked:   {CANCER_BASAL}")
    log()
    log(f"  SUPPRESSED: {SADDLE_CANDIDATES}")
    log(f"  ELEVATED:   {ELEVATED_PREDICTED}")
    log(f"  CONTROLS:   {CONTROL_GENES}")
    log()

    luminal_cells = combined[
        combined[CT_COL] == MATURE_LUMINAL
    ]
    basal_cells   = combined[
        combined[CT_COL] == CANCER_BASAL
    ]

    log(f"n mature luminal: {len(luminal_cells)}")
    log(f"n cancer basal:   {len(basal_cells)}")
    log()

    results = []
    analysis_genes = (SADDLE_CANDIDATES +
                      ELEVATED_PREDICTED +
                      CONTROL_GENES +
                      SCAFFOLD_GENES)

    for gene in analysis_genes:
        if gene not in combined.columns:
            continue

        lum_vals   = luminal_cells[gene].dropna()
        basal_vals = basal_cells[gene].dropna()

        if len(lum_vals) < 5 or len(basal_vals) < 5:
            continue

        lum_mean   = lum_vals.mean()
        basal_mean = basal_vals.mean()

        suppression_pct = (
            (lum_mean - basal_mean) /
            (lum_mean + 1e-6) * 100
        )
        elevation_pct = (
            (basal_mean - lum_mean) /
            (lum_mean + 1e-6) * 100
        )

        _, pval_supp = stats.mannwhitneyu(
            lum_vals, basal_vals,
            alternative='greater'
        )
        _, pval_elev = stats.mannwhitneyu(
            basal_vals, lum_vals,
            alternative='greater'
        )

        is_candidate = gene in SADDLE_CANDIDATES
        is_elevated  = gene in ELEVATED_PREDICTED
        is_control   = gene in CONTROL_GENES
        is_scaffold  = gene in SCAFFOLD_GENES

        role = (
            'CANDIDATE' if is_candidate else
            'ELEVATED'  if is_elevated  else
            'CONTROL'   if is_control   else
            'SCAFFOLD'
        )

        if is_candidate:
            if suppression_pct > 30 and pval_supp < 0.05:
                result = "CONFIRMED"
            elif suppression_pct > 15:
                result = "PARTIAL"
            elif suppression_pct < -20:
                result = "INVERTED"
            else:
                result = "NOT CONFIRMED"

        elif is_elevated:
            if elevation_pct > 20 and pval_elev < 0.05:
                result = "ELEVATED AS PREDICTED"
            elif elevation_pct > 0:
                result = "WEAKLY ELEVATED"
            else:
                result = "NOT ELEVATED"

        elif is_scaffold:
            if abs(suppression_pct) < 30:
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
            'luminal_expr':    round(lum_mean, 4),
            'basal_expr':      round(basal_mean, 4),
            'suppression_pct': round(suppression_pct, 1),
            'elevation_pct':   round(elevation_pct, 1),
            'pval_supp':       pval_supp,
            'pval_elev':       pval_elev,
            'result':          result
        })

        def fmt_p(p):
            if np.isnan(p):  return "N/A      "
            if p < 0.001:    return f"{p:.2e} ***"
            if p < 0.01:     return f"{p:.4f} ** "
            if p < 0.05:     return f"{p:.4f} *  "
            return            f"{p:.4f}    "

        direction = (
            f"suppressed {suppression_pct:+.1f}%"
            if suppression_pct > 0
            else f"elevated   {elevation_pct:+.1f}%"
        )

        flag = (
            "✓ CONFIRMED"  if result == "CONFIRMED"
            else "✓ ELEVATED" if result == "ELEVATED AS PREDICTED"
            else "~ PARTIAL"  if result == "PARTIAL"
            else "~ SCAFFOLD" if result == "SCAFFOLD OK"
            else "✓ CTRL OK"  if result == "CONTROL OK"
            else "✗ " + result
        )

        log(f"{gene:8} [{role:10}] | "
            f"lum={lum_mean:.4f} "
            f"basal={basal_mean:.4f} | "
            f"{direction:26} | "
            f"p={fmt_p(pval_supp)} | {flag}")

    results_df = pd.DataFrame(results)
    results_df.to_csv(
        RESULTS_DIR + "brca_saddle_results.csv",
        index=False
    )

    n_conf  = (results_df['result'] == 'CONFIRMED').sum()
    n_part  = (results_df['result'] == 'PARTIAL').sum()
    n_cand  = (results_df['role'] == 'CANDIDATE').sum()
    n_elev  = (results_df['result'] ==
               'ELEVATED AS PREDICTED').sum()
    n_elev_p = (results_df['role'] == 'ELEVATED').sum()
    n_ctrl  = (results_df['result'] == 'CONTROL OK').sum()
    n_ctrl_t = (results_df['role'] == 'CONTROL').sum()

    log()
    log("="*56)
    log("BRCA FRAMEWORK PREDICTION RESULT")
    log("="*56)
    log(f"Switch genes confirmed:  {n_conf}/{n_cand}")
    log(f"Switch genes partial:    {n_part}/{n_cand}")
    log(f"Elevated as predicted:   {n_elev}/{n_elev_p}")
    log(f"Controls as expected:    {n_ctrl}/{n_ctrl_t}")
    log()

    if n_conf >= 2 and n_ctrl >= 1:
        log("*** STRONG CONFIRMATION ***")
        log("BRCA false attractor confirmed.")
        log()
        log("CROSS-CANCER TABLE:")
        log("  AML:  SPI1 90.5% KLF4 94.7% IRF8 69.5%")
        log("  CRC:  CDX2 79.5%")
        log("  GBM:  SOX10 88.6% MBP 89.6%"
            " MOG 56.9% PLP1 83.4%")
        log("  BRCA: [results above]")
        log()
        log("Four cancer types.")
        log("Four lineages.")
        log("Zero gene overlap.")
        log("Same principle.")
    elif n_conf + n_part >= 2:
        log("** PARTIAL CONFIRMATION **")
    else:
        log("* CHECK REQUIRED *")
        log("Paste output for diagnosis.")

    return results_df

# ============================================================
# STEP 5: SECONDARY COMPARISON
# LumA SC vs Mature Luminal — is the luminal
# malignant state also blocked?
# ============================================================

def secondary_comparison(combined, available_genes):
    log("="*56)
    log("STEP 5: SECONDARY COMPARISON")
    log("LumA Cancer vs Mature Luminal")
    log("="*56)
    log("Testing whether luminal cancer cells")
    log("show the same switch gene suppression")
    log("as basal cancer cells, or a weaker form.")
    log()

    lum_cells  = combined[
        combined[CT_COL] == MATURE_LUMINAL
    ]
    luma_cells = combined[
        combined[CT_COL] == CANCER_LUMA
    ]

    log(f"n mature luminal:  {len(lum_cells)}")
    log(f"n cancer LumA SC:  {len(luma_cells)}")
    log()

    for gene in SADDLE_CANDIDATES:
        if gene not in combined.columns:
            continue
        lum_vals  = lum_cells[gene].dropna()
        luma_vals = luma_cells[gene].dropna()
        if len(lum_vals) < 5 or len(luma_vals) < 5:
            continue

        lum_mean  = lum_vals.mean()
        luma_mean = luma_vals.mean()
        supp = (lum_mean - luma_mean) / (
            lum_mean + 1e-6
        ) * 100

        _, pval = stats.mannwhitneyu(
            lum_vals, luma_vals,
            alternative='greater'
        )

        log(f"  {gene:8}: "
            f"luminal={lum_mean:.4f} "
            f"LumA={luma_mean:.4f} "
            f"suppressed={supp:.1f}% "
            f"p={pval:.2e}")

    log()
    log("INTERPRETATION:")
    log("  If LumA shows partial suppression of")
    log("  FOXA1/GATA3/ESR1 relative to Mature")
    log("  Luminal, the false attractor gradient")
    log("  runs: Mature Luminal > LumA SC > Basal SC")
    log("  — a continuous suppression landscape")
    log("  tracking differentiation state.")

# ============================================================
# STEP 6: FIGURE
# ============================================================

def generate_figure(combined, results_df,
                    available_genes):
    log("="*56)
    log("STEP 6: GENERATING FIGURE")
    log("="*56)

    fig = plt.figure(figsize=(20, 14))
    gs  = gridspec.GridSpec(
        2, 3, figure=fig,
        hspace=0.5, wspace=0.4
    )

    lum_cells   = combined[
        combined[CT_COL] == MATURE_LUMINAL
    ]
    basal_cells = combined[
        combined[CT_COL] == CANCER_BASAL
    ]
    prog_cells  = combined[
        combined[CT_COL] == LUMINAL_PROG
    ]
    luma_cells  = combined[
        combined[CT_COL] == CANCER_LUMA
    ]

    plot_genes = [g for g in
                  (SADDLE_CANDIDATES +
                   ELEVATED_PREDICTED +
                   CONTROL_GENES)
                  if g in combined.columns]

    # ---- Panel A: Gap bar chart ----
    ax_a = fig.add_subplot(gs[0, :])
    x     = np.arange(len(plot_genes))
    width = 0.35

    lum_means   = [lum_cells[g].mean()
                   if g in lum_cells.columns else 0
                   for g in plot_genes]
    basal_means = [basal_cells[g].mean()
                   if g in basal_cells.columns else 0
                   for g in plot_genes]
    lum_sems    = [lum_cells[g].sem()
                   if g in lum_cells.columns else 0
                   for g in plot_genes]
    basal_sems  = [basal_cells[g].sem()
                   if g in basal_cells.columns else 0
                   for g in plot_genes]

    ax_a.bar(x - width/2, lum_means, width,
             yerr=lum_sems, capsize=3,
             label='Mature Luminal\n'
                   '(differentiated endpoint)',
             color='steelblue', alpha=0.85,
             error_kw={'linewidth': 1})
    ax_a.bar(x + width/2, basal_means, width,
             yerr=basal_sems, capsize=3,
             label='Cancer Basal SC\n'
                   '(false attractor)',
             color='crimson', alpha=0.85,
             error_kw={'linewidth': 1})

    ax_a.set_xticks(x)
    ax_a.set_xticklabels(plot_genes, fontsize=10)
    ax_a.set_ylabel("Mean log1p(counts)", fontsize=11)
    ax_a.set_title(
        "A. The BRCA False Attractor Gap\n"
        "Blue = Mature Luminal (normal endpoint)  |  "
        "Red = Cancer Basal SC (false attractor)\n"
        "Switch: FOXA1 GATA3 ESR1  |  "
        "Elevated: SOX2 MYC EGFR KRT5  |  "
        "Controls: SOX10 MBP CDX2 SPI1",
        fontsize=10, fontweight='bold'
    )
    ax_a.legend(fontsize=10)

    n_s = len(SADDLE_CANDIDATES)
    n_e = len(ELEVATED_PREDICTED)
    ax_a.axvline(x=n_s - 0.5,
                 color='gray', linestyle='--',
                 alpha=0.4, linewidth=1)
    ax_a.axvline(x=n_s + n_e - 0.5,
                 color='gray', linestyle='--',
                 alpha=0.4, linewidth=1)

    if results_df is not None:
        for i, gene in enumerate(plot_genes):
            row = results_df[
                results_df['gene'] == gene
            ]
            if len(row) == 0:
                continue
            row   = row.iloc[0]
            pct   = row['suppression_pct']
            color = (
                'darkgreen'
                if row['result'] == 'CONFIRMED'
                else 'darkorange'
                if row['result'] == 'ELEVATED AS PREDICTED'
                else 'darkred'
                if row['result'] == 'INVERTED'
                else 'gray'
            )
            label = (f"{pct:.0f}%↓" if pct > 0
                     else f"{abs(pct):.0f}%↑")
            ax_a.annotate(
                label,
                xy=(i, max(lum_means[i],
                           basal_means[i]) + 0.02),
                ha='center', fontsize=9,
                color=color, fontweight='bold'
            )

    # ---- Panel B: Gradient across states ----
    ax_b = fig.add_subplot(gs[1, 0])

    states = [MATURE_LUMINAL, LUMINAL_PROG,
              CANCER_LUMA, CANCER_BASAL]
    state_labels = ['Mature\nLuminal',
                    'Luminal\nProg',
                    'Cancer\nLumA',
                    'Cancer\nBasal']
    colors_grad = ['steelblue', 'cornflowerblue',
                   'salmon', 'crimson']

    for gene in SADDLE_CANDIDATES:
        if gene not in combined.columns:
            continue
        means = []
        sems  = []
        for state in states:
            cells = combined[
                combined[CT_COL] == state
            ][gene]
            means.append(cells.mean())
            sems.append(cells.sem())
        ax_b.plot(state_labels, means,
                  marker='o', linewidth=2,
                  label=gene, alpha=0.85)
        ax_b.fill_between(
            state_labels,
            [m - s for m, s in zip(means, sems)],
            [m + s for m, s in zip(means, sems)],
            alpha=0.1
        )

    ax_b.set_ylabel("Mean log1p(counts)", fontsize=9)
    ax_b.set_title(
        "B. Suppression Gradient\n"
        "Normal → Progenitor → LumA → Basal",
        fontsize=10, fontweight='bold'
    )
    ax_b.legend(fontsize=9)

    # ---- Panel C: Suppression bar ----
    ax_c = fig.add_subplot(gs[1, 1])
    if results_df is not None:
        plot_df = results_df[
            results_df['gene'].isin(plot_genes)
        ].sort_values('suppression_pct',
                      ascending=False).copy()
        bar_colors = []
        for _, row in plot_df.iterrows():
            if row['role'] == 'CANDIDATE':
                bar_colors.append('crimson')
            elif row['role'] == 'ELEVATED':
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
            "Suppression in Basal SC (%)\n"
            "(negative = elevated)",
            fontsize=9
        )
        ax_c.set_title(
            "C. Direction and Magnitude\n"
            "Red=switch  Orange=elevated  "
            "Blue=controls",
            fontsize=10, fontweight='bold'
        )
        ax_c.legend(fontsize=9)

    # ---- Panel D: Results table ----
    ax_d = fig.add_subplot(gs[1, 2])
    ax_d.axis('off')
    if results_df is not None:
        tbl = results_df[[
            'gene', 'role',
            'suppression_pct', 'result'
        ]].copy()
        tbl['pval'] = results_df['pval_supp'].apply(
            lambda p: f"{p:.2e}"
            if not np.isnan(p) else "N/A"
        )
        tbl = tbl[[
            'gene', 'role',
            'suppression_pct', 'pval', 'result'
        ]]
        tbl.columns = [
            'Gene', 'Role', 'Supp%', 'p-val', 'Result'
        ]
        table = ax_d.table(
            cellText=tbl.values,
            colLabels=tbl.columns,
            loc='center', cellLoc='center'
        )
        table.auto_set_font_size(False)
        table.set_fontsize(7)
        table.scale(1.0, 1.6)

        row_colors = {
            'CONFIRMED':            '#c8e6c9',
            'ELEVATED AS PREDICTED':'#ffe0b2',
            'PARTIAL':              '#fff9c4',
            'CONTROL OK':           '#e3f2fd',
            'SCAFFOLD OK':          '#f3e5f5',
            'NOT CONFIRMED':        '#ffcdd2',
            'CONTROL UNEXPECTED':   '#ff8a65',
        }
        for i, (_, row) in enumerate(tbl.iterrows()):
            color = row_colors.get(
                str(row['Result']), 'white'
            )
            for j in range(len(tbl.columns)):
                table[i+1, j].set_facecolor(color)

    ax_d.set_title(
        "D. Full Results Table",
        fontsize=10, fontweight='bold', pad=20
    )

    fig.suptitle(
        "BRCA False Attractor — "
        "Cancer Basal SC vs Mature Luminal\n"
        "GSE176078 Wu et al. 2021  |  "
        "OrganismCore  |  February 28, 2026\n"
        "Luminal switch genes predicted suppressed "
        "in BRCA basal false attractor state",
        fontsize=11, fontweight='bold'
    )

    outpath = RESULTS_DIR + "brca_saddle_figure.png"
    plt.savefig(outpath, dpi=180,
                bbox_inches='tight')
    plt.close()
    log(f"Figure saved: {outpath}")

# ============================================================
# STEP 7: CROSS-CANCER SUMMARY
# ============================================================

def generate_cross_cancer_summary(results_df):
    log("="*56)
    log("STEP 7: FOUR-CANCER SUMMARY")
    log("="*56)

    summary = """
CROSS-CANCER FALSE ATTRACTOR ANALYSIS
OrganismCore — February 28, 2026
============================================================

CANCER 1: AML — Myeloid
  SPI1: 90.5%  KLF4: 94.7%  IRF8: 69.5%

CANCER 2: CRC — Epithelial/Colonocyte
  CDX2: 79.5%

CANCER 3: GBM — Oligodendrocyte/Neural
  SOX10: 88.6%  MBP: 89.6%
  MOG:   56.9%  PLP1: 83.4%

CANCER 4: BRCA — Luminal Epithelial
"""

    if results_df is not None:
        for _, row in results_df[
            results_df['role'] == 'CANDIDATE'
        ].iterrows():
            p_str  = f"{row['pval_supp']:.2e}"
            marker = (
                "***" if row['pval_supp'] < 0.001
                else "**" if row['pval_supp'] < 0.01
                else "*"  if row['pval_supp'] < 0.05
                else ""
            )
            summary += (
                f"  {row['gene']:8}: "
                f"{row['suppression_pct']:5.1f}% "
                f"suppressed  p={p_str} {marker}  "
                f"[{row['result']}]\n"
            )

        summary += "\n  Elevated:\n"
        for _, row in results_df[
            results_df['role'] == 'ELEVATED'
        ].iterrows():
            summary += (
                f"  {row['gene']:8}: "
                f"{row['elevation_pct']:5.1f}% "
                f"elevated  [{row['result']}]\n"
            )

    summary += """
GENE OVERLAP ACROSS ALL FOUR CANCERS:
  AML:  SPI1, KLF4, IRF8
  CRC:  CDX2
  GBM:  SOX10, MBP, MOG, PLP1
  BRCA: FOXA1, GATA3, ESR1

  Zero overlap.
  Four cancers.
  Four lineages.
  Four completely different switch gene sets.
  One principle.

============================================================
Eric Robert Lawson — OrganismCore
February 28, 2026
"""

    path = RESULTS_DIR + "cross_cancer_summary.txt"
    with open(path, "w") as f:
        f.write(summary)
    log(summary)
    log(f"Saved: {path}")

# ============================================================
# MAIN
# ============================================================

def main():
    log("="*56)
    log("BRCA FALSE ATTRACTOR ANALYSIS")
    log("OrganismCore — False Attractor Framework")
    log("Cancer Validation #4")
    log("February 28, 2026")
    log("="*56)

    for f in [MTX_FILE, GENES_FILE,
              BARCODES_FILE, META_FILE]:
        if not os.path.exists(f):
            log(f"ERROR: {f} not found.")
            log(f"Contents: {os.listdir('.')}")
            return

    log("All files found.")

    meta = load_metadata()

    cache = RESULTS_DIR + "expr_cache.csv"
    if os.path.exists(cache):
        log("\nLoading expression from cache...")
        expr = pd.read_csv(cache, index_col=0)
        log(f"Cached: {expr.shape}")
    else:
        expr = load_mtx_expression(meta)

    if expr is None:
        log("Expression loading failed.")
        return

    combined, traj_stats, available_genes = \
        compute_profiles(expr, meta)

    if combined is None:
        log("Profile computation failed.")
        return

    results_df = compute_saddle_point_signature(
        combined, traj_stats, available_genes
    )

    secondary_comparison(combined, available_genes)

    generate_figure(
        combined, results_df, available_genes
    )

    generate_cross_cancer_summary(results_df)

    log()
    log("="*56)
    log("COMPLETE")
    log(f"Results: {RESULTS_DIR}")
    log("="*56)


if __name__ == "__main__":
    main()
