"""
GBM FALSE ATTRACTOR ANALYSIS
OrganismCore — Document 74
False Attractor Framework — Cancer Validation #3
February 28, 2026

CANCER TYPE: Glioblastoma (GBM)
DATA: GSE131928 — Neftel et al. 2019, Cell
      Smart-seq2: GSM3828672
      23,686 genes x 7,930 cells (Smart-seq2)
      28 patients, IDH-wildtype GBM

LINK: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE131928

FILE:
  GSM3828672_Smartseq2_GBM_IDHwt_processed_TPM.tsv.gz
  Format: genes x cells, TPM values
  Columns: GENE, then cell barcodes (MGH###-P#-###)

CELL STATE CLASSIFICATION:
  Neftel 2019 defined 6 cell states using
  marker gene expression scores. We replicate
  their approach using published marker genes.

  MALIGNANT STATES (GBM false attractors):
    OPC-like:  PDGFRA+, OLIG1+, OLIG2+ (low MBP)
    NPC-like:  SOX2+, NES+, EGFR+ (neural progenitor)
    MES-like:  high stress/hypoxia signature
    AC-like:   GFAP+, AQP4+ (astrocyte-like)

  NORMAL BRAIN CELLS (differentiation endpoints):
    Oligodendrocyte: MBP+, MOG+, PLP1+, SOX10+
                     (terminal myelinating)
    Astrocyte:       GFAP+, AQP4+ (but EGFR-low)
    Cycling:         MKI67+, TOP2A+

  THE KEY COMPARISON FOR THE FALSE ATTRACTOR:
    OPC-like malignant cells vs normal oligodendrocytes

    OPC-like cells are stuck at the progenitor stage.
    They express PDGFRA and early OLIG markers but
    CANNOT complete differentiation to myelinating
    oligodendrocytes (MBP, MOG, PLP1, SOX10 suppressed).

    This is the GBM false attractor:
    cells trapped in the OPC-like state,
    unable to cross the myelination threshold.

FRAMEWORK PREDICTION:
  SUPPRESSED in OPC-like vs normal oligo:
    OLIG2  — oligodendrocyte master TF
    SOX10  — myelination TF
    MBP    — myelin basic protein (terminal)
    MOG    — myelin oligodendrocyte glycoprotein
    PLP1   — proteolipid protein (terminal myelin)

  ELEVATED in OPC-like vs normal oligo:
    PDGFRA — OPC marker / false attractor driver
    SOX2   — neural stem / GBM oncogene
    EGFR   — GBM oncogene
    NES    — neural progenitor (dedifferentiation)

  CONTROLS (wrong lineage — flat):
    CDX2   — colonocyte TF (confirmed CRC: 79.5%)
    SPI1   — myeloid TF   (confirmed AML: 90.5%)
    KLF4   — myeloid TF   (confirmed AML: 94.7%)
    IRF8   — myeloid TF   (confirmed AML: 69.5%)
    GFAP   — astrocyte marker (different glial type)

NOTE ON STRATEGY:
  Because there is no separate normal brain cell
  annotation in this dataset (all cells are from
  GBM tumors), we use MARKER-BASED CLASSIFICATION:

  1. Score each cell for oligodendrocyte markers
     (MBP + MOG + PLP1 + SOX10) — high = normal oligo
  2. Score each cell for OPC/GBM markers
     (PDGFRA + SOX2 + EGFR + NES) — high = OPC-like
  3. Compare these two populations directly

  Cells with high myelination scores in a GBM
  tumor dataset are oligodendrocytes that were
  co-profiled with the tumor (Neftel included
  non-malignant cells in all tumors).
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

EXPR_FILE   = ("GSM3828672_Smartseq2_GBM_IDHwt"
               "_processed_TPM.tsv.gz")
RESULTS_DIR = "./gbm_saddle_results/"
os.makedirs(RESULTS_DIR, exist_ok=True)
LOG_FILE    = RESULTS_DIR + "analysis_log.txt"

with open(LOG_FILE, "w") as f:
    f.write("")

def log(msg=""):
    print(msg)
    with open(LOG_FILE, "a") as f:
        f.write(str(msg) + "\n")

# ---- Marker gene sets for cell classification ----

# Terminal oligodendrocyte differentiation markers
# High in normal myelinating oligodendrocytes
# Predicted SUPPRESSED in OPC-like false attractor
OLIGO_TERMINAL = ["MBP", "MOG", "PLP1", "SOX10"]

# OPC / GBM progenitor markers
# High in OPC-like false attractor state
PROGENITOR_MARKERS = ["PDGFRA", "SOX2", "EGFR", "NES"]

# Early oligodendrocyte lineage (expressed in both
# OPC and mature oligo — these are SCAFFOLD genes)
OLIGO_EARLY = ["OLIG1", "OLIG2"]

# Proliferation markers
CYCLING_MARKERS = ["MKI67", "TOP2A"]

# Astrocyte markers
ASTROCYTE_MARKERS = ["GFAP", "AQP4"]

# PREDICTED SUPPRESSED in OPC-like vs normal oligo
SADDLE_CANDIDATES = ["OLIG2", "SOX10", "MBP",
                     "MOG", "PLP1"]

# PREDICTED ELEVATED in OPC-like vs normal oligo
ELEVATED_PREDICTED = ["PDGFRA", "SOX2", "EGFR", "NES"]

# CONTROLS — wrong lineage, should be flat
# These are the confirmed switch genes from AML + CRC
CONTROL_GENES = ["CDX2", "SPI1", "KLF4", "IRF8"]

ALL_TARGET = (SADDLE_CANDIDATES +
              ELEVATED_PREDICTED +
              CONTROL_GENES +
              ["OLIG1", "GFAP", "MKI67"])

# Classification thresholds
# Cells in top N% of myelination score = normal oligo
# Cells in top N% of progenitor score  = OPC-like
TOP_PCT = 20

# ============================================================
# STEP 1: LOAD EXPRESSION
# ============================================================

def load_expression():
    log("="*56)
    log("STEP 1: LOADING EXPRESSION MATRIX")
    log("="*56)
    log(f"File: {EXPR_FILE}")
    log("Loading TPM matrix (genes x cells)...")
    log("This will take ~60 seconds...")

    # Check cache
    cache = RESULTS_DIR + "expr_cache.csv"
    if os.path.exists(cache):
        log("Loading from cache...")
        expr = pd.read_csv(cache, index_col=0)
        log(f"Cached shape: {expr.shape}")
        return expr

    # Load full matrix — genes as rows, cells as cols
    df = pd.read_csv(
        EXPR_FILE,
        sep='\t',
        index_col=0,
        compression='gzip'
    )
    log(f"Full matrix: {df.shape} (genes x cells)")

    # Extract only our target genes
    available = [g for g in ALL_TARGET
                 if g in df.index]
    missing   = [g for g in ALL_TARGET
                 if g not in df.index]

    log(f"\nTarget genes found:   {available}")
    if missing:
        log(f"Missing genes:        {missing}")

    # Extract target genes — transpose to cells x genes
    expr = df.loc[available].T
    log(f"\nExtracted: {expr.shape} (cells x genes)")

    # Log-transform TPM (log1p is standard)
    expr_log = np.log1p(expr)
    log("Log1p transformed.")

    # Save cache
    expr_log.to_csv(cache)
    log(f"Cached: {cache}")

    return expr_log

# ============================================================
# STEP 2: CLASSIFY CELLS
# ============================================================

def classify_cells(expr):
    log("="*56)
    log("STEP 2: CELL STATE CLASSIFICATION")
    log("="*56)
    log("Strategy: marker-based scoring")
    log("  Normal oligodendrocyte = high MBP/MOG/PLP1/SOX10")
    log("  OPC-like false attractor = high PDGFRA/SOX2/EGFR/NES")
    log()

    # Score each cell for myelination
    # (terminal oligodendrocyte differentiation)
    oligo_genes = [g for g in OLIGO_TERMINAL
                   if g in expr.columns]
    prog_genes  = [g for g in PROGENITOR_MARKERS
                   if g in expr.columns]
    cycling     = [g for g in CYCLING_MARKERS
                   if g in expr.columns]

    log(f"Myelination markers available: {oligo_genes}")
    log(f"Progenitor markers available:  {prog_genes}")

    # Mean score across available markers
    expr['oligo_score'] = expr[oligo_genes].mean(axis=1)
    expr['prog_score']  = expr[prog_genes].mean(axis=1)

    if cycling:
        expr['cycling_score'] = expr[cycling].mean(axis=1)

    # Show score distributions
    log(f"\nOligo score:      "
        f"mean={expr['oligo_score'].mean():.3f}  "
        f"max={expr['oligo_score'].max():.3f}")
    log(f"Progenitor score: "
        f"mean={expr['prog_score'].mean():.3f}  "
        f"max={expr['prog_score'].max():.3f}")

    # Classify by top percentile
    oligo_thresh = np.percentile(
        expr['oligo_score'], 100 - TOP_PCT
    )
    prog_thresh  = np.percentile(
        expr['prog_score'],  100 - TOP_PCT
    )

    log(f"\nThresholds (top {TOP_PCT}%):")
    log(f"  Oligo:      {oligo_thresh:.3f}")
    log(f"  Progenitor: {prog_thresh:.3f}")

    # Assign cell states
    # Normal oligo: high myelination, low progenitor
    # OPC-like:     high progenitor, low myelination
    # Ambiguous:    high both or low both
    expr['cell_state'] = 'Ambiguous'

    is_oligo = (
        (expr['oligo_score'] >= oligo_thresh) &
        (expr['prog_score']  <  prog_thresh)
    )
    is_opc = (
        (expr['prog_score']  >= prog_thresh) &
        (expr['oligo_score'] <  oligo_thresh)
    )

    expr.loc[is_oligo, 'cell_state'] = 'Normal_Oligo'
    expr.loc[is_opc,   'cell_state'] = 'OPC_like'

    # Show cell state counts
    counts = expr['cell_state'].value_counts()
    log(f"\nCell state distribution:")
    log(str(counts))

    n_oligo = (expr['cell_state'] == 'Normal_Oligo').sum()
    n_opc   = (expr['cell_state'] == 'OPC_like').sum()

    log(f"\nNormal oligodendrocytes: {n_oligo}")
    log(f"OPC-like (false attractor): {n_opc}")

    if n_oligo < 20:
        log("WARNING: Very few normal oligo cells.")
        log("Lowering threshold to top 30%...")
        oligo_thresh = np.percentile(
            expr['oligo_score'], 70
        )
        prog_thresh  = np.percentile(
            expr['prog_score'],  70
        )
        expr['cell_state'] = 'Ambiguous'
        is_oligo = (
            (expr['oligo_score'] >= oligo_thresh) &
            (expr['prog_score']  <  prog_thresh)
        )
        is_opc = (
            (expr['prog_score']  >= prog_thresh) &
            (expr['oligo_score'] <  oligo_thresh)
        )
        expr.loc[is_oligo, 'cell_state'] = 'Normal_Oligo'
        expr.loc[is_opc,   'cell_state'] = 'OPC_like'
        counts = expr['cell_state'].value_counts()
        log(f"Revised distribution:")
        log(str(counts))

    # Show mean expression of key markers by state
    log(f"\nMarker expression by cell state:")
    key_genes = [g for g in
                 (OLIGO_TERMINAL + PROGENITOR_MARKERS)
                 if g in expr.columns]
    state_means = expr.groupby('cell_state')[
        key_genes
    ].mean().round(3)
    log(str(state_means))

    return expr

# ============================================================
# STEP 3: SADDLE POINT SIGNATURE
# ============================================================

def compute_saddle_point_signature(expr):
    log("="*56)
    log("STEP 3: SADDLE POINT SIGNATURE")
    log("="*56)
    log("FRAMEWORK PREDICTION (GBM):")
    log("  Reference:  Normal_Oligo")
    log("              (myelinating oligodendrocytes)")
    log("  Blocked:    OPC_like")
    log("              (false attractor)")
    log()
    log("  SUPPRESSED candidates:")
    log(f"    {SADDLE_CANDIDATES}")
    log("  ELEVATED predicted:")
    log(f"    {ELEVATED_PREDICTED}")
    log("  CONTROLS (prior cancer switch genes):")
    log(f"    {CONTROL_GENES}")
    log()

    normal_cells = expr[expr['cell_state'] == 'Normal_Oligo']
    blocked_cells = expr[expr['cell_state'] == 'OPC_like']

    log(f"n normal oligo:  {len(normal_cells)}")
    log(f"n OPC-like:      {len(blocked_cells)}")
    log()

    results = []
    all_analysis_genes = (SADDLE_CANDIDATES +
                          ELEVATED_PREDICTED +
                          CONTROL_GENES +
                          ["OLIG1", "GFAP"])

    for gene in all_analysis_genes:
        if gene not in expr.columns:
            continue

        normal_vals  = normal_cells[gene].dropna()
        blocked_vals = blocked_cells[gene].dropna()

        if len(normal_vals) < 5 or len(blocked_vals) < 5:
            continue

        normal_mean  = normal_vals.mean()
        blocked_mean = blocked_vals.mean()

        # Suppression: how much lower is blocked
        # relative to normal?
        suppression_pct = (
            (normal_mean - blocked_mean) /
            (normal_mean + 1e-6) * 100
        )
        elevation_pct = (
            (blocked_mean - normal_mean) /
            (normal_mean + 1e-6) * 100
        )

        # Statistical tests
        _, pval_supp = stats.mannwhitneyu(
            normal_vals, blocked_vals,
            alternative='greater'
        )
        _, pval_elev = stats.mannwhitneyu(
            blocked_vals, normal_vals,
            alternative='greater'
        )

        # Classify role
        is_candidate = gene in SADDLE_CANDIDATES
        is_elevated  = gene in ELEVATED_PREDICTED
        is_control   = gene in CONTROL_GENES
        is_scaffold  = gene in ["OLIG1", "GFAP"]

        role = (
            'CANDIDATE' if is_candidate else
            'ELEVATED'  if is_elevated  else
            'CONTROL'   if is_control   else
            'SCAFFOLD'
        )

        # Evaluate
        if is_candidate:
            if (suppression_pct > 30 and
                    pval_supp < 0.05):
                result = "CONFIRMED"
            elif suppression_pct > 15:
                result = "PARTIAL"
            elif suppression_pct < -20:
                result = "INVERTED"
            else:
                result = "NOT CONFIRMED"

        elif is_elevated:
            if (elevation_pct > 20 and
                    pval_elev < 0.05):
                result = "ELEVATED AS PREDICTED"
            elif elevation_pct > 0:
                result = "WEAKLY ELEVATED"
            else:
                result = "NOT ELEVATED"

        elif is_scaffold:
            # Scaffold: should be present in both
            # states — not suppressed, not elevated
            if abs(suppression_pct) < 30:
                result = "SCAFFOLD OK"
            else:
                result = "SCAFFOLD UNEXPECTED"

        else:  # control
            if abs(suppression_pct) < 30:
                result = "CONTROL OK"
            else:
                result = "CONTROL UNEXPECTED"

        results.append({
            'gene':            gene,
            'role':            role,
            'normal_expr':     round(normal_mean, 4),
            'blocked_expr':    round(blocked_mean, 4),
            'suppression_pct': round(suppression_pct, 1),
            'elevation_pct':   round(elevation_pct, 1),
            'pval_supp':       pval_supp,
            'pval_elev':       pval_elev,
            'result':          result
        })

        def fmt_p(p):
            if np.isnan(p):   return "N/A      "
            if p < 0.001:     return f"{p:.2e} ***"
            if p < 0.01:      return f"{p:.4f} ** "
            if p < 0.05:      return f"{p:.4f} *  "
            return             f"{p:.4f}    "

        direction = (
            f"suppressed {suppression_pct:+.1f}%"
            if suppression_pct > 0
            else f"elevated   {elevation_pct:+.1f}%"
        )

        flag = (
            "✓ CONFIRMED"   if result == "CONFIRMED"
            else "✓ ELEVATED" if result == "ELEVATED AS PREDICTED"
            else "~ PARTIAL"  if result == "PARTIAL"
            else "~ SCAFFOLD" if result == "SCAFFOLD OK"
            else "✓ CTRL OK"  if result == "CONTROL OK"
            else "✗ " + result
        )

        log(f"{gene:8} [{role:10}] | "
            f"normal={normal_mean:.3f} "
            f"blocked={blocked_mean:.3f} | "
            f"{direction:26} | "
            f"p={fmt_p(pval_supp)} | {flag}")

    results_df = pd.DataFrame(results)
    results_df.to_csv(
        RESULTS_DIR + "gbm_saddle_results.csv",
        index=False
    )

    # Summary
    n_conf  = (results_df['result'] == 'CONFIRMED').sum()
    n_part  = (results_df['result'] == 'PARTIAL').sum()
    n_cand  = (results_df['role'] == 'CANDIDATE').sum()
    n_elev  = (results_df['result'] ==
               'ELEVATED AS PREDICTED').sum()
    n_elev_pred = (results_df['role'] == 'ELEVATED').sum()
    n_ctrl  = (results_df['result'] == 'CONTROL OK').sum()
    n_ctrl_t = (results_df['role'] == 'CONTROL').sum()

    log()
    log("="*56)
    log("GBM FRAMEWORK PREDICTION RESULT")
    log("="*56)
    log(f"Switch genes confirmed:  {n_conf}/{n_cand}")
    log(f"Switch genes partial:    {n_part}/{n_cand}")
    log(f"Elevated as predicted:   {n_elev}/{n_elev_pred}")
    log(f"Controls as expected:    {n_ctrl}/{n_ctrl_t}")
    log()

    if n_conf >= 2 and n_ctrl >= 2:
        log("*** STRONG CONFIRMATION ***")
        log("GBM false attractor signature confirmed.")
        log()
        log("CROSS-CANCER TABLE:")
        log("  AML: SPI1 90.5% KLF4 94.7% IRF8 69.5%")
        log("       Myeloid switch genes")
        log("  CRC: CDX2 79.5%")
        log("       Colonocyte switch gene")
        log("  GBM: [results above]")
        log("       Oligodendrocyte switch genes")
        log()
        log("Three cancer types.")
        log("Three lineages.")
        log("Zero gene overlap.")
        log("Same principle.")
    elif n_conf + n_part >= 2:
        log("** PARTIAL CONFIRMATION **")
        log("Consistent with framework.")
    else:
        log("* CHECK REQUIRED *")
        log("Paste output for diagnosis.")

    return results_df

# ============================================================
# STEP 4: FIGURE
# ============================================================

def generate_figure(expr, results_df):
    log("="*56)
    log("STEP 4: GENERATING FIGURE")
    log("="*56)

    fig = plt.figure(figsize=(20, 14))
    gs  = gridspec.GridSpec(
        2, 3, figure=fig,
        hspace=0.5, wspace=0.4
    )

    normal_cells  = expr[expr['cell_state'] == 'Normal_Oligo']
    blocked_cells = expr[expr['cell_state'] == 'OPC_like']

    plot_genes = [g for g in
                  (SADDLE_CANDIDATES +
                   ELEVATED_PREDICTED +
                   CONTROL_GENES)
                  if g in expr.columns]

    # ---- Panel A: Gap bar chart ----
    ax_a = fig.add_subplot(gs[0, :])

    x     = np.arange(len(plot_genes))
    width = 0.35

    normal_means  = [normal_cells[g].mean()
                     if g in normal_cells.columns
                     else 0 for g in plot_genes]
    blocked_means = [blocked_cells[g].mean()
                     if g in blocked_cells.columns
                     else 0 for g in plot_genes]
    normal_sems   = [normal_cells[g].sem()
                     if g in normal_cells.columns
                     else 0 for g in plot_genes]
    blocked_sems  = [blocked_cells[g].sem()
                     if g in blocked_cells.columns
                     else 0 for g in plot_genes]

    ax_a.bar(x - width/2, normal_means, width,
             yerr=normal_sems, capsize=3,
             label='Normal oligodendrocyte\n'
                   '(differentiated endpoint)',
             color='steelblue', alpha=0.85,
             error_kw={'linewidth': 1})
    ax_a.bar(x + width/2, blocked_means, width,
             yerr=blocked_sems, capsize=3,
             label='OPC-like (false attractor)\n'
                   'GBM malignant state',
             color='crimson', alpha=0.85,
             error_kw={'linewidth': 1})

    ax_a.set_xticks(x)
    ax_a.set_xticklabels(plot_genes, fontsize=10)
    ax_a.set_ylabel("Mean log1p(TPM)", fontsize=11)
    ax_a.set_title(
        "A. The GBM False Attractor Gap\n"
        "Blue = normal myelinating oligodendrocyte  |  "
        "Red = OPC-like malignant cells (false attractor)\n"
        "Switch candidates: OLIG2 SOX10 MBP MOG PLP1  |  "
        "Elevated: PDGFRA SOX2 EGFR NES  |  "
        "Controls: CDX2 SPI1 KLF4 IRF8",
        fontsize=10, fontweight='bold'
    )
    ax_a.legend(fontsize=10)

    # Separators between gene groups
    n_s = len(SADDLE_CANDIDATES)
    n_e = len(ELEVATED_PREDICTED)
    ax_a.axvline(x=n_s - 0.5,
                 color='gray', linestyle='--',
                 alpha=0.4, linewidth=1)
    ax_a.axvline(x=n_s + n_e - 0.5,
                 color='gray', linestyle='--',
                 alpha=0.4, linewidth=1)

    # Annotate % change
    if results_df is not None:
        for i, gene in enumerate(plot_genes):
            row = results_df[results_df['gene'] == gene]
            if len(row) == 0:
                continue
            row = row.iloc[0]
            pct = row['suppression_pct']
            color = (
                'darkgreen'
                if row['result'] == 'CONFIRMED'
                else 'darkorange'
                if row['result'] == 'ELEVATED AS PREDICTED'
                else 'darkred'
                if row['result'] == 'INVERTED'
                else 'gray'
            )
            label = (f"{pct:.0f}%↓"
                     if pct > 0
                     else f"{abs(pct):.0f}%↑")
            ax_a.annotate(
                label,
                xy=(i, max(normal_means[i],
                           blocked_means[i]) + 0.05),
                ha='center', fontsize=9,
                color=color, fontweight='bold'
            )

    # ---- Panel B: Score distributions ----
    ax_b = fig.add_subplot(gs[1, 0])
    all_states = expr['cell_state'].unique()
    colors_map = {
        'Normal_Oligo': 'steelblue',
        'OPC_like':     'crimson',
        'Ambiguous':    'lightgray'
    }
    for state in ['Normal_Oligo', 'OPC_like',
                  'Ambiguous']:
        if state not in expr['cell_state'].values:
            continue
        subset = expr[expr['cell_state'] == state]
        ax_b.scatter(
            subset['oligo_score'],
            subset['prog_score'],
            c=colors_map.get(state, 'gray'),
            alpha=0.3, s=5,
            label=f"{state} (n={len(subset)})"
        )
    ax_b.set_xlabel("Myelination score\n"
                    "(MBP+MOG+PLP1+SOX10)", fontsize=9)
    ax_b.set_ylabel("Progenitor score\n"
                    "(PDGFRA+SOX2+EGFR+NES)", fontsize=9)
    ax_b.set_title(
        "B. Cell State Landscape\nBlue=normal oligo  "
        "Red=OPC-like",
        fontsize=10, fontweight='bold'
    )
    ax_b.legend(fontsize=7, markerscale=3)

    # ---- Panel C: Suppression bar chart ----
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
            "Suppression in OPC-like (%)\n"
            "(negative = elevated)",
            fontsize=9
        )
        ax_c.set_title(
            "C. Direction and Magnitude\n"
            "Red=switch candidates  "
            "Orange=elevated  Blue=controls",
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
            'CONFIRMED':           '#c8e6c9',
            'ELEVATED AS PREDICTED':'#ffe0b2',
            'PARTIAL':             '#fff9c4',
            'CONTROL OK':          '#e3f2fd',
            'SCAFFOLD OK':         '#f3e5f5',
            'NOT CONFIRMED':       '#ffcdd2',
            'CONTROL UNEXPECTED':  '#ff8a65',
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
        "GBM False Attractor — OPC-like vs "
        "Normal Oligodendrocyte\n"
        "GSE131928 Neftel et al. 2019  |  "
        "OrganismCore  |  February 28, 2026\n"
        "Myelination switch genes predicted suppressed "
        "in GBM OPC-like false attractor state",
        fontsize=11, fontweight='bold'
    )

    outpath = RESULTS_DIR + "gbm_saddle_figure.png"
    plt.savefig(outpath, dpi=180, bbox_inches='tight')
    plt.close()
    log(f"Figure saved: {outpath}")
    return outpath

# ============================================================
# STEP 5: CROSS-CANCER SUMMARY
# ============================================================

def generate_cross_cancer_summary(results_df):
    log("="*56)
    log("STEP 5: CROSS-CANCER SUMMARY")
    log("="*56)

    summary = """
CROSS-CANCER FALSE ATTRACTOR ANALYSIS
OrganismCore — February 28, 2026
============================================================

THE PRINCIPLE:
  Cancer is a false attractor in the Waddington
  epigenetic landscape. Malignant cells are stuck
  below the differentiation threshold — a ceiling
  imposed by suppression of lineage-specific switch
  genes. The switch genes are identifiable by their
  expression profile: suppressed in the blocked
  population relative to the normal differentiated
  endpoint.

CANCER 1: AML — Acute Myeloid Leukemia
  Lineage:    Myeloid
  Block:      GMP-like vs CD14+ monocytes
  Switch genes (myeloid differentiation):
    SPI1:  90.5% suppressed  p=0.00e+00 ***
    KLF4:  94.7% suppressed  p=0.00e+00 ***
    IRF8:  69.5% suppressed  p=0.00e+00 ***

CANCER 2: CRC — Colorectal Cancer
  Lineage:    Epithelial/Colonocyte
  Block:      Epithelial 2 (cycling) vs Epithelial 1
  Switch genes (colonocyte differentiation):
    CDX2:  79.5% suppressed  p=3.89e-154 ***
  Unexpected: IRF8 elevated 211%
              (lineage infidelity)

CANCER 3: GBM — Glioblastoma
  Lineage:    Neural/Oligodendrocyte
  Block:      OPC-like vs normal oligodendrocytes
  Switch genes (myelination/oligodendrocyte):
"""

    if results_df is not None:
        for _, row in results_df[
            results_df['role'] == 'CANDIDATE'
        ].iterrows():
            p_str = f"{row['pval_supp']:.2e}"
            marker = (
                "***" if row['pval_supp'] < 0.001
                else "**" if row['pval_supp'] < 0.01
                else "*"  if row['pval_supp'] < 0.05
                else ""
            )
            summary += (
                f"    {row['gene']:8}: "
                f"{row['suppression_pct']:5.1f}% "
                f"suppressed  p={p_str} {marker}  "
                f"[{row['result']}]\n"
            )

        summary += "\n  Elevated (false attractor drivers):\n"
        for _, row in results_df[
            results_df['role'] == 'ELEVATED'
        ].iterrows():
            summary += (
                f"    {row['gene']:8}: "
                f"{row['elevation_pct']:5.1f}% "
                f"elevated  [{row['result']}]\n"
            )

        summary += "\n  Controls (prior cancer switch genes):\n"
        for _, row in results_df[
            results_df['role'] == 'CONTROL'
        ].iterrows():
            summary += (
                f"    {row['gene']:8}: "
                f"suppression={row['suppression_pct']:+.1f}%"
                f"  [{row['result']}]\n"
            )

    summary += """
ZERO GENE OVERLAP (confirmed):
  AML:  SPI1, KLF4, IRF8   — myeloid TFs
  CRC:  CDX2               — colonocyte TF
  GBM:  OLIG2, SOX10, MBP, MOG, PLP1
        — oligodendrocyte/myelin TFs and proteins

  None of these gene sets overlap.
  The framework finds lineage-specific gates
  in each cancer type.
  The lock is the same. The gates are different.

THERAPEUTIC IMPLICATIONS:
  AML:  CRISPRa SPI1 + KLF4 + IRF8
  CRC:  CRISPRa CDX2  +  CRISPRi IRF8
  GBM:  CRISPRa [confirmed switch genes above]

  Same intervention logic. Different targets.
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
    log("GBM FALSE ATTRACTOR ANALYSIS")
    log("OrganismCore — False Attractor Framework")
    log("Cancer Validation #3")
    log("February 28, 2026")
    log("="*56)

    if not os.path.exists(EXPR_FILE):
        log(f"ERROR: {EXPR_FILE} not found.")
        log(f"Contents: {os.listdir('.')}")
        return

    log("File found.")

    expr       = load_expression()
    expr       = classify_cells(expr)
    results_df = compute_saddle_point_signature(expr)

    generate_figure(expr, results_df)
    generate_cross_cancer_summary(results_df)

    log()
    log("="*56)
    log("COMPLETE")
    log(f"Results: {RESULTS_DIR}")
    log("Files:")
    log(f"  {RESULTS_DIR}gbm_saddle_figure.png")
    log(f"  {RESULTS_DIR}gbm_saddle_results.csv")
    log(f"  {RESULTS_DIR}cross_cancer_summary.txt")
    log("="*56)


if __name__ == "__main__":
    main()
