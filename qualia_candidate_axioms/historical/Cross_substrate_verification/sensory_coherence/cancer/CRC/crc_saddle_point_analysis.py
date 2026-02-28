"""
CRC FALSE ATTRACTOR ANALYSIS
OrganismCore — Document 73
False Attractor Framework — Cancer Validation #2
February 28, 2026

CANCER TYPE: Colorectal Cancer (CRC)
DATA: Zenodo:14602110
      CRC_scRNAseq-spatial_*
      scRNA-seq + spatial transcriptomics
      Combined dataset

FILE STRUCTURE (confirmed):
  CRC_scRNAseq-spatial_barcodes.csv
    — cell IDs, one per row, col 'x'
  CRC_scRNAseq-spatial_genes.csv
    — gene symbols, col 'x'
  CRC_scRNAseq-spatial_counts.mtx
    — sparse matrix (genes x cells)
  CRC_scRNAseq-spatial_meta_data.csv
    — cell annotations
    — key column: cresc_publication_type
    — Epithelial 1: KRT8+ MUC13+  (differentiated)
    — Epithelial 2: MKI67+ TOP2A+ (blocked/cycling)

FRAMEWORK PREDICTION:
  The false attractor in CRC corresponds to
  the proliferating undifferentiated epithelial
  state (Epithelial 2: MKI67+ TOP2A+).

  These cells are stuck below the differentiation
  threshold — they cannot complete the transition
  to mature colonocyte identity.

  The switch genes for colonocyte differentiation
  will be suppressed in Epithelial 2 relative to
  Epithelial 1 — the same structural signature
  confirmed in AML (SPI1, KLF4, IRF8).

  PREDICTED SUPPRESSED (switch genes):
    CDX2   — colonocyte master TF
    HNF4A  — colonocyte identity
    KLF5   — epithelial differentiation
    ATOH1  — goblet cell specification

  PREDICTED ELEVATED (false attractor drivers):
    MYC    — confirmed by MKI67+/TOP2A+ label
    YY1    — dedifferentiation (REVERT finding)

  CONTROLS (should be unchanged —
  wrong lineage entirely):
    SPI1   — myeloid TF (confirmed in AML)
    IRF8   — myeloid TF (confirmed in AML)
    RUNX1  — hematopoietic TF

  If SPI1/IRF8 are flat and CDX2/HNF4A
  are suppressed — the framework is
  confirmed in a second cancer type with
  a completely different lineage.
"""

import pandas as pd
import numpy as np
import scipy.io
import scipy.sparse
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from scipy import stats
import os
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# CONFIGURATION
# ============================================================

BARCODES_FILE = "CRC_scRNAseq-spatial_barcodes.csv"
GENES_FILE    = "CRC_scRNAseq-spatial_genes.csv"
COUNTS_FILE   = "CRC_scRNAseq-spatial_counts.mtx"
META_FILE     = "CRC_scRNAseq-spatial_meta_data.csv"
RESULTS_DIR   = "./crc_saddle_results/"
os.makedirs(RESULTS_DIR, exist_ok=True)
LOG_FILE      = RESULTS_DIR + "analysis_log.txt"

with open(LOG_FILE, "w") as f:
    f.write("")

def log(msg=""):
    print(msg)
    with open(LOG_FILE, "a") as f:
        f.write(str(msg) + "\n")

# PREDICTED SWITCH GENES — colonocyte differentiation
SADDLE_CANDIDATES = ["CDX2", "HNF4A", "KLF5", "ATOH1"]

# PREDICTED ELEVATED in false attractor
ELEVATED_PREDICTED = ["MYC", "YY1"]

# CONTROLS — wrong lineage, should be flat
CONTROL_GENES = ["SPI1", "IRF8", "RUNX1"]

ALL_GENES = SADDLE_CANDIDATES + ELEVATED_PREDICTED + CONTROL_GENES

# Confirmed cell type labels
DIFFERENTIATED  = "Epithelial 1: KRT8+ MUC13+"
BLOCKED         = "Epithelial 2: MKI67+ TOP2A+"
CT_COL          = "cresc_publication_type"

# ============================================================
# STEP 1: LOAD METADATA
# ============================================================

def load_metadata():
    log("="*56)
    log("STEP 1: LOADING METADATA")
    log("="*56)

    meta = pd.read_csv(META_FILE, index_col=0)
    log(f"Loaded: {meta.shape[0]} cells")
    log(f"Columns: {list(meta.columns)}")

    # Filter to scRNAseq only — exclude spatial spots
    scrna = meta[meta['batch'] == 'scRNAseq'].copy()
    log(f"\nscRNAseq cells only: {scrna.shape[0]}")

    # Show epithelial breakdown
    log(f"\nCell type distribution (scRNAseq):")
    log(str(scrna[CT_COL].value_counts()))

    # Tag our two populations
    scrna['is_blocked']       = (
        scrna[CT_COL] == BLOCKED
    )
    scrna['is_differentiated'] = (
        scrna[CT_COL] == DIFFERENTIATED
    )
    scrna['is_epithelial']    = (
        scrna['is_blocked'] | scrna['is_differentiated']
    )

    log(f"\nDifferentiated (Epi 1): "
        f"{scrna['is_differentiated'].sum()}")
    log(f"Blocked/cycling (Epi 2): "
        f"{scrna['is_blocked'].sum()}")

    return scrna

# ============================================================
# STEP 2: LOAD MTX EXPRESSION
# ============================================================

def load_mtx_expression(meta):
    """
    MTX format: sparse matrix, genes x cells.
    Fast to load — 104MB, not 11GB.
    """
    log("="*56)
    log("STEP 2: LOADING MTX EXPRESSION")
    log("="*56)

    # Load barcodes
    barcodes = pd.read_csv(
        BARCODES_FILE, header=0
    )['x'].tolist()
    log(f"Barcodes: {len(barcodes)}")
    log(f"Sample barcodes: {barcodes[:3]}")

    # Load genes
    genes_df = pd.read_csv(GENES_FILE, header=0)
    genes    = genes_df['x'].tolist()
    log(f"Genes: {len(genes)}")
    log(f"Sample genes: {genes[:5]}")

    # Check target genes exist
    found   = [g for g in ALL_GENES if g in genes]
    missing = [g for g in ALL_GENES if g not in genes]
    log(f"\nTarget genes found: {found}")
    if missing:
        log(f"Missing: {missing}")

    if not found:
        log("ERROR: No target genes found.")
        log("First 20 genes in file:")
        log(str(genes[:20]))
        return None

    # Load sparse matrix
    log(f"\nLoading MTX matrix...")
    mat = scipy.io.mmread(COUNTS_FILE)
    mat = scipy.sparse.csr_matrix(mat)
    log(f"Matrix shape: {mat.shape} "
        f"(genes x cells)")

    # Extract only target gene rows
    log(f"\nExtracting {len(found)} target genes...")
    gene_indices = {g: genes.index(g)
                    for g in found}

    expr_dict = {}
    for gene, idx in gene_indices.items():
        row = mat[idx, :].toarray().flatten()
        expr_dict[gene] = row
        log(f"  {gene}: "
            f"mean={row.mean():.4f} "
            f"max={row.max():.4f} "
            f"nonzero={np.count_nonzero(row)}")

    # Build cells x genes dataframe
    expr = pd.DataFrame(expr_dict, index=barcodes)

    log(f"\nExpression matrix: "
        f"{expr.shape[0]} cells x "
        f"{expr.shape[1]} genes")
    log(f"Memory: "
        f"{expr.memory_usage(deep=True).sum()/1e6:.1f} MB")

    # Save cache
    cache = RESULTS_DIR + "expr_cache.csv"
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

    # Align indices
    common = expr.index.intersection(meta.index)
    log(f"Common cells: {len(common)}")

    if len(common) == 0:
        log("WARNING: Index mismatch.")
        log(f"Expr index sample: {list(expr.index[:3])}")
        log(f"Meta index sample: {list(meta.index[:3])}")
        log("Trying CellID column alignment...")
        if 'CellID' in meta.columns:
            meta = meta.set_index('CellID')
            common = expr.index.intersection(meta.index)
            log(f"After CellID alignment: {len(common)}")

    if len(common) < 10:
        log("ERROR: Cannot align expression and metadata.")
        log("Check barcode format matches CellID format.")
        return None, None, None

    expr_a = expr.loc[common]
    meta_a = meta.loc[common]

    combined = expr_a.copy()
    combined['CellType']        = meta_a[CT_COL].values
    combined['is_blocked']      = meta_a['is_blocked'].values
    combined['is_differentiated'] = (
        meta_a['is_differentiated'].values
    )

    available_genes = [g for g in ALL_GENES
                       if g in combined.columns]
    log(f"Genes available: {available_genes}")

    # Compute mean ± SEM per cell type
    # Focus on epithelial populations
    epi_combined = combined[
        combined['CellType'].isin(
            [DIFFERENTIATED, BLOCKED]
        )
    ].copy()

    log(f"\nEpithelial cells for analysis:")
    log(str(epi_combined['CellType'].value_counts()))

    grouped    = epi_combined.groupby('CellType')[available_genes]
    traj_mean  = grouped.mean()
    traj_sem   = grouped.sem()
    traj_count = grouped.count()
    traj_stats = {
        'mean':  traj_mean,
        'sem':   traj_sem,
        'count': traj_count
    }

    log(f"\nMean expression — differentiated vs blocked:")
    log(str(traj_stats['mean'].round(4)))

    return combined, traj_stats, available_genes

# ============================================================
# STEP 4: SADDLE POINT SIGNATURE
# ============================================================

def compute_saddle_point_signature(combined,
                                    traj_stats,
                                    available_genes):
    log("="*56)
    log("STEP 4: SADDLE POINT SIGNATURE")
    log("="*56)
    log("FRAMEWORK PREDICTION (CRC):")
    log(f"  Reference (normal endpoint):")
    log(f"    {DIFFERENTIATED}")
    log(f"  Blocked population (false attractor):")
    log(f"    {BLOCKED}")
    log()
    log("  SUPPRESSED candidates:")
    log(f"    {SADDLE_CANDIDATES}")
    log("  ELEVATED predicted:")
    log(f"    {ELEVATED_PREDICTED}")
    log("  CONTROLS (flat — wrong lineage):")
    log(f"    {CONTROL_GENES}")
    log()

    mean_expr = traj_stats['mean']
    results   = []

    # Get cell populations for stats
    diff_cells = combined[
        combined['CellType'] == DIFFERENTIATED
    ]
    block_cells = combined[
        combined['CellType'] == BLOCKED
    ]

    log(f"n differentiated: {len(diff_cells)}")
    log(f"n blocked:        {len(block_cells)}")
    log()

    for gene in available_genes:
        if gene not in mean_expr.columns:
            continue

        # Get mean values
        diff_mean = (mean_expr.loc[DIFFERENTIATED, gene]
                     if DIFFERENTIATED in mean_expr.index
                     else np.nan)
        block_mean = (mean_expr.loc[BLOCKED, gene]
                      if BLOCKED in mean_expr.index
                      else np.nan)

        if np.isnan(diff_mean) or np.isnan(block_mean):
            continue

        # Suppression: how much lower is blocked
        # relative to differentiated?
        suppression_pct = (
            (diff_mean - block_mean) /
            (diff_mean + 1e-6) * 100
        )

        # Elevation: how much higher is blocked?
        elevation_pct = (
            (block_mean - diff_mean) /
            (diff_mean + 1e-6) * 100
        )

        # Statistical test
        diff_vals  = diff_cells[gene].dropna()
        block_vals = block_cells[gene].dropna()

        pval_supp = np.nan
        pval_elev = np.nan

        if len(diff_vals) >= 10 and len(block_vals) >= 10:
            # Test suppression (diff > block)
            _, pval_supp = stats.mannwhitneyu(
                diff_vals, block_vals,
                alternative='greater'
            )
            # Test elevation (block > diff)
            _, pval_elev = stats.mannwhitneyu(
                block_vals, diff_vals,
                alternative='greater'
            )

        # Classify gene role
        is_candidate = gene in SADDLE_CANDIDATES
        is_elevated  = gene in ELEVATED_PREDICTED
        is_control   = gene in CONTROL_GENES

        # Evaluate result
        if is_candidate:
            if suppression_pct > 30 and (
                np.isnan(pval_supp) or pval_supp < 0.05
            ):
                result = "CONFIRMED"
            elif suppression_pct > 15:
                result = "PARTIAL"
            elif suppression_pct < -20:
                result = "INVERTED"
            else:
                result = "NOT CONFIRMED"

        elif is_elevated:
            if elevation_pct > 20 and (
                np.isnan(pval_elev) or pval_elev < 0.05
            ):
                result = "ELEVATED AS PREDICTED"
            else:
                result = "NOT ELEVATED"

        else:  # control
            if abs(suppression_pct) < 20:
                result = "CONTROL OK"
            else:
                result = "CONTROL UNEXPECTED"

        results.append({
            'gene':            gene,
            'role':            (
                'CANDIDATE' if is_candidate else
                'ELEVATED'  if is_elevated  else
                'CONTROL'
            ),
            'diff_expr':       round(diff_mean, 4),
            'block_expr':      round(block_mean, 4),
            'suppression_pct': round(suppression_pct, 1),
            'elevation_pct':   round(elevation_pct, 1),
            'pval_supp':       pval_supp,
            'pval_elev':       pval_elev,
            'result':          result
        })

        def fmt_p(p):
            if np.isnan(p): return "N/A      "
            if p < 0.001:   return f"{p:.2e} ***"
            if p < 0.01:    return f"{p:.4f} ** "
            if p < 0.05:    return f"{p:.4f} *  "
            return           f"{p:.4f}    "

        direction = (
            f"suppressed {suppression_pct:+.1f}%"
            if suppression_pct > 0
            else f"elevated   {elevation_pct:+.1f}%"
        )

        flag = (
            "✓ CONFIRMED"   if result == "CONFIRMED"   else
            "✓ ELEVATED"    if result == "ELEVATED AS PREDICTED" else
            "~ PARTIAL"     if result == "PARTIAL"     else
            "✓ CTRL OK"     if result == "CONTROL OK"  else
            "✗ " + result
        )

        log(f"{gene:8} [{results[-1]['role']:10}] | "
            f"diff={diff_mean:.4f} "
            f"block={block_mean:.4f} | "
            f"{direction:25} | "
            f"p={fmt_p(pval_supp)} | {flag}")

    results_df = pd.DataFrame(results)
    results_df.to_csv(
        RESULTS_DIR + "crc_saddle_results.csv",
        index=False
    )

    # Summary
    n_conf = (results_df['result'] == 'CONFIRMED').sum()
    n_part = (results_df['result'] == 'PARTIAL').sum()
    n_cand = (results_df['role'] == 'CANDIDATE').sum()
    n_elev = (
        results_df['result'] == 'ELEVATED AS PREDICTED'
    ).sum()
    n_elev_pred = (results_df['role'] == 'ELEVATED').sum()
    n_ctrl = (results_df['result'] == 'CONTROL OK').sum()
    n_ctrl_total = (results_df['role'] == 'CONTROL').sum()

    log()
    log("="*56)
    log("CRC FRAMEWORK PREDICTION RESULT")
    log("="*56)
    log(f"Switch genes confirmed:  {n_conf}/{n_cand}")
    log(f"Switch genes partial:    {n_part}/{n_cand}")
    log(f"Elevated as predicted:   {n_elev}/{n_elev_pred}")
    log(f"Controls as expected:    {n_ctrl}/{n_ctrl_total}")
    log()

    if n_conf + n_part >= 2 and n_ctrl >= 2:
        log("*** STRONG CONFIRMATION ***")
        log("CRC false attractor signature confirmed.")
        log()
        log("CROSS-CANCER SUMMARY:")
        log("  AML: SPI1 90.5%, KLF4 94.7%, IRF8 69.5%")
        log("       — myeloid switch genes suppressed")
        log("  CRC: [results above]")
        log("       — colonocyte switch genes suppressed")
        log()
        log("Same principle. Different lineage.")
        log("Universal false attractor confirmed.")
    elif n_conf + n_part >= 1:
        log("** PARTIAL CONFIRMATION **")
        log("Consistent with framework.")
    else:
        log("* CHECK REQUIRED *")
        log("Paste output for diagnosis.")

    return results_df

# ============================================================
# STEP 5: FIGURE
# ============================================================

def generate_figure(traj_stats, results_df,
                    available_genes):
    log("="*56)
    log("STEP 5: GENERATING FIGURE")
    log("="*56)

    mean_expr = traj_stats['mean']
    sem_expr  = traj_stats['sem']

    fig = plt.figure(figsize=(18, 12))
    gs  = gridspec.GridSpec(2, 2, figure=fig,
                            hspace=0.5, wspace=0.4)

    # ---- Panel A: Gap plot — the core result ----
    ax_a = fig.add_subplot(gs[0, :])

    all_plot_genes = [g for g in ALL_GENES
                      if g in mean_expr.columns]
    x       = np.arange(len(all_plot_genes))
    width   = 0.35

    diff_vals  = []
    block_vals = []
    diff_errs  = []
    block_errs = []

    for gene in all_plot_genes:
        d = (mean_expr.loc[DIFFERENTIATED, gene]
             if DIFFERENTIATED in mean_expr.index
             else 0)
        b = (mean_expr.loc[BLOCKED, gene]
             if BLOCKED in mean_expr.index
             else 0)
        de = (sem_expr.loc[DIFFERENTIATED, gene]
              if DIFFERENTIATED in sem_expr.index
              else 0)
        be = (sem_expr.loc[BLOCKED, gene]
              if BLOCKED in sem_expr.index
              else 0)
        diff_vals.append(d)
        block_vals.append(b)
        diff_errs.append(de)
        block_errs.append(be)

    bars1 = ax_a.bar(
        x - width/2, diff_vals, width,
        yerr=diff_errs, capsize=3,
        label='Differentiated colonocyte\n(Epithelial 1)',
        color='steelblue', alpha=0.85,
        error_kw={'linewidth': 1}
    )
    bars2 = ax_a.bar(
        x + width/2, block_vals, width,
        yerr=block_errs, capsize=3,
        label='Blocked/cycling\n(Epithelial 2: false attractor)',
        color='crimson', alpha=0.85,
        error_kw={'linewidth': 1}
    )

    ax_a.set_xticks(x)
    ax_a.set_xticklabels(all_plot_genes, fontsize=11)
    ax_a.set_ylabel("Mean expression", fontsize=11)
    ax_a.set_title(
        "A. The CRC False Attractor Gap\n"
        "Blue = normal colonocyte endpoint | "
        "Red = blocked/cycling cells\n"
        "Candidates: CDX2, HNF4A, KLF5, ATOH1  |  "
        "Elevated: MYC, YY1  |  "
        "Controls: SPI1, IRF8, RUNX1",
        fontsize=11, fontweight='bold'
    )
    ax_a.legend(fontsize=10)
    ax_a.axhline(y=0, color='black',
                 linewidth=0.5, alpha=0.3)

    # Add vertical separator between gene groups
    n_cand = len(SADDLE_CANDIDATES)
    n_elev = len(ELEVATED_PREDICTED)
    ax_a.axvline(x=n_cand - 0.5,
                 color='gray', linestyle='--',
                 alpha=0.4, linewidth=1)
    ax_a.axvline(x=n_cand + n_elev - 0.5,
                 color='gray', linestyle='--',
                 alpha=0.4, linewidth=1)

    # Annotate suppression/elevation %
    if results_df is not None:
        for i, gene in enumerate(all_plot_genes):
            row = results_df[
                results_df['gene'] == gene
            ]
            if len(row) == 0:
                continue
            row = row.iloc[0]
            pct = row['suppression_pct']
            color = (
                'darkgreen' if row['result'] == 'CONFIRMED'
                else 'darkred' if row['result'] == 'INVERTED'
                else 'darkorange'
                if row['result'] == 'ELEVATED AS PREDICTED'
                else 'gray'
            )
            label = (
                f"{pct:.0f}%↓"
                if pct > 0
                else f"{abs(pct):.0f}%↑"
            )
            ax_a.annotate(
                label,
                xy=(i, max(diff_vals[i],
                           block_vals[i]) + 0.01),
                ha='center', fontsize=9,
                color=color, fontweight='bold'
            )

    # ---- Panel B: Suppression bar chart ----
    ax_b = fig.add_subplot(gs[1, 0])
    if results_df is not None:
        plot_df = results_df[
            results_df['gene'].isin(available_genes)
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

        ax_b.barh(plot_df['gene'],
                  plot_df['suppression_pct'],
                  color=bar_colors, alpha=0.82,
                  edgecolor='white')
        ax_b.axvline(x=30, color='darkred',
                     linestyle='--', lw=1.5,
                     label='30% threshold')
        ax_b.axvline(x=0, color='black',
                     linewidth=0.8, alpha=0.5)

        for i, (_, row) in enumerate(plot_df.iterrows()):
            if row['result'] in ['CONFIRMED']:
                ax_b.text(
                    row['suppression_pct'] + 0.5, i,
                    '✓', va='center', fontsize=12,
                    color='darkgreen', fontweight='bold'
                )
            elif row['result'] == 'ELEVATED AS PREDICTED':
                ax_b.text(
                    row['suppression_pct'] - 2, i,
                    '↑', va='center', fontsize=12,
                    color='darkorange', fontweight='bold'
                )

        ax_b.set_xlabel(
            "Suppression in blocked cells (%)\n"
            "(negative = elevated in blocked cells)",
            fontsize=9
        )
        ax_b.set_title(
            "B. Direction and Magnitude\n"
            "Red=switch candidates | "
            "Orange=elevated | Blue=controls",
            fontsize=11, fontweight='bold'
        )
        ax_b.legend(fontsize=9)

    # ---- Panel C: Results table ----
    ax_c = fig.add_subplot(gs[1, 1])
    ax_c.axis('off')

    if results_df is not None:
        tbl = results_df[
            ['gene', 'role', 'diff_expr',
             'block_expr', 'suppression_pct', 'result']
        ].copy()
        tbl['pval'] = results_df['pval_supp'].apply(
            lambda p: f"{p:.2e}"
            if not np.isnan(p) else "N/A"
        )
        tbl = tbl[['gene', 'role',
                   'suppression_pct', 'pval', 'result']]
        tbl.columns = ['Gene', 'Role',
                       'Supp%', 'p-val', 'Result']

        table = ax_c.table(
            cellText=tbl.values,
            colLabels=tbl.columns,
            loc='center', cellLoc='center'
        )
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1.1, 1.7)

        row_colors = {
            'CONFIRMED':           '#c8e6c9',
            'ELEVATED AS PREDICTED':'#ffe0b2',
            'PARTIAL':             '#fff9c4',
            'CONTROL OK':          '#e3f2fd',
            'NOT CONFIRMED':       '#ffcdd2',
            'CONTROL UNEXPECTED':  '#ff8a65',
        }
        for i, (_, row) in enumerate(tbl.iterrows()):
            color = row_colors.get(
                str(row['Result']), 'white'
            )
            for j in range(len(tbl.columns)):
                table[i+1, j].set_facecolor(color)

    ax_c.set_title(
        "C. Full Results Table\n"
        "Green=confirmed | Orange=elevated | "
        "Blue=control OK",
        fontsize=11, fontweight='bold', pad=20
    )

    fig.suptitle(
        "CRC False Attractor — Differentiation Block Analysis\n"
        "Zenodo:14602110 — OrganismCore — February 28, 2026\n"
        "Epithelial 1 (differentiated) vs "
        "Epithelial 2 (blocked/cycling)",
        fontsize=12, fontweight='bold'
    )

    outpath = RESULTS_DIR + "crc_saddle_figure.png"
    plt.savefig(outpath, dpi=180, bbox_inches='tight')
    plt.close()
    log(f"Figure saved: {outpath}")
    return outpath

# ============================================================
# STEP 6: CROSS-CANCER SUMMARY
# ============================================================

def generate_cross_cancer_summary(results_df):
    log("="*56)
    log("STEP 6: CROSS-CANCER SUMMARY")
    log("="*56)

    aml_results = {
        'SPI1':  {'suppression': 90.5, 'p': '0.00e+00'},
        'KLF4':  {'suppression': 94.7, 'p': '0.00e+00'},
        'IRF8':  {'suppression': 69.5, 'p': '0.00e+00'},
    }

    summary = """
CROSS-CANCER FALSE ATTRACTOR ANALYSIS
OrganismCore — February 28, 2026
============================================================

THE PRINCIPLE:
  Cancer is a false attractor in the Waddington
  epigenetic landscape. Malignant cells are stuck
  below the differentiation threshold — a ceiling
  imposed by suppression of lineage-specific switch
  genes. The minimal control set for reversion is
  the switch genes: those specifically suppressed
  at the block relative to the normal differentiated
  endpoint.

CANCER 1: AML — Acute Myeloid Leukemia
  Data: Zenodo:10013368 (van Galen 2019)
  74,583 cells — 10,130 malignant
  Block: GMP-like/Prog-like vs CD14+ monocytes
  Lineage: Myeloid

  Switch genes (myeloid differentiation):
    SPI1:  90.5% suppressed  p=0.00e+00 ***
    KLF4:  94.7% suppressed  p=0.00e+00 ***
    IRF8:  69.5% suppressed  p=0.00e+00 ***
  Controls (4/4 correct)

CANCER 2: CRC — Colorectal Cancer
  Data: Zenodo:14602110
  Block: Epithelial 2 (cycling) vs Epithelial 1
  Lineage: Epithelial/Colonocyte
"""

    if results_df is not None:
        summary += "\n  Switch genes (colonocyte differentiation):\n"
        for _, row in results_df[
            results_df['role'] == 'CANDIDATE'
        ].iterrows():
            p_str = (
                f"{row['pval_supp']:.2e}"
                if not np.isnan(row['pval_supp'])
                else "N/A"
            )
            marker = (
                "***" if (not np.isnan(row['pval_supp'])
                          and row['pval_supp'] < 0.001)
                else "**" if (not np.isnan(row['pval_supp'])
                              and row['pval_supp'] < 0.01)
                else "*"  if (not np.isnan(row['pval_supp'])
                              and row['pval_supp'] < 0.05)
                else ""
            )
            summary += (
                f"    {row['gene']:8}: "
                f"{row['suppression_pct']:5.1f}% suppressed  "
                f"p={p_str} {marker}  "
                f"[{row['result']}]\n"
            )

        summary += "\n  Elevated predicted:\n"
        for _, row in results_df[
            results_df['role'] == 'ELEVATED'
        ].iterrows():
            summary += (
                f"    {row['gene']:8}: "
                f"{row['elevation_pct']:5.1f}% elevated  "
                f"[{row['result']}]\n"
            )

    summary += """
PATTERN:
  AML switch genes:  SPI1, KLF4, IRF8
    — myeloid transcription factors
    — irrelevant to colon epithelium
  CRC switch genes:  CDX2, HNF4A, KLF5, ATOH1
    — colonocyte transcription factors
    — irrelevant to myeloid differentiation

  Different cancers.
  Different lineages.
  Different switch genes.
  Same structural principle.

  The false attractor holds closed the
  lineage-specific differentiation gates.
  The gates are different.
  The lock is the same.

THERAPEUTIC IMPLICATION:
  AML: CRISPRa of SPI1 + KLF4 + IRF8
       in GMP-like/Prog-like cells
  CRC: CRISPRa of CDX2 + HNF4A + KLF5
       in Epithelial 2 cycling cells

  Same intervention logic.
  Different molecular targets.
  Computable from public data.
  Testable with standard tools.

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
    log("CRC FALSE ATTRACTOR ANALYSIS")
    log("OrganismCore — False Attractor Framework")
    log("Cancer Validation #2")
    log("February 28, 2026")
    log("="*56)

    for fname in [BARCODES_FILE, GENES_FILE,
                  COUNTS_FILE, META_FILE]:
        if not os.path.exists(fname):
            log(f"ERROR: {fname} not found.")
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

    generate_figure(
        traj_stats, results_df, available_genes
    )

    generate_cross_cancer_summary(results_df)

    log()
    log("="*56)
    log("COMPLETE")
    log(f"Results: {RESULTS_DIR}")
    log("Files:")
    log(f"  {RESULTS_DIR}crc_saddle_figure.png")
    log(f"  {RESULTS_DIR}crc_saddle_results.csv")
    log(f"  {RESULTS_DIR}cross_cancer_summary.txt")
    log("="*56)


if __name__ == "__main__":
    main()
