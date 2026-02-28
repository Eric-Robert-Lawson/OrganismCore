"""
ALL FALSE ATTRACTOR ANALYSIS
OrganismCore — Document 79
False Attractor Framework — Cancer Validation #7
Session 2 — Lymphoid

CANCER TYPE: Acute Lymphoblastic Leukemia (ALL)
  B-ALL: ETV6-RUNX1 (4 patients)
         HHD — High Hyperdiploid (2 patients)
  T-ALL: PRE-T (2 patients)

DATA: GSE132509 — Caron et al. 2020
      38,922 cells — 8 ALL patients
      3 normal PBMMC donors
      10X Chromium scRNA-seq

TWO COMPARISONS:
  1. B-ALL blasts vs normal B cells
     Tests: PAX5, EBF1, IKZF1,
            CD19, MS4A1
  2. T-ALL blasts vs normal T cells
     Tests: GATA3, BCL11B, TCF7,
            CD3E, TRBC1

CRITICAL LINEAGE SPECIFICITY TEST:
  CEBPA — confirmed myeloid switch
  (AML 94.7%, CML 90.3%)
  Predicted: FLAT in ALL
  (not a lymphoid switch gene)
  If CEBPA is flat in ALL —
  confirms switch genes are
  lineage-specific, not pan-cancer.

CROSS-CANCER TEST:
  GATA3 confirmed BRCA switch gene
  (luminal epithelial context)
  Now testing in T-ALL
  (T-cell context)
  If GATA3 is suppressed in T-ALL:
  same gene, different lineage,
  different cancer — but both
  use GATA3 as a lineage switch.
  The gene is reused across lineages
  for lineage-specific purposes.
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

DATA_DIR    = "./"
RESULTS_DIR = "./all_saddle_results/"
os.makedirs(RESULTS_DIR, exist_ok=True)
LOG_FILE    = RESULTS_DIR + "analysis_log.txt"

with open(LOG_FILE, "w") as f:
    f.write("")

def log(msg=""):
    print(msg)
    with open(LOG_FILE, "a") as f:
        f.write(str(msg) + "\n")

# Target genes
B_SWITCH    = ["PAX5", "EBF1", "IKZF1", "CD19", "MS4A1"]
T_SWITCH    = ["GATA3", "BCL11B", "TCF7", "CD3E", "TRBC1"]
SCAFFOLD    = ["CD34", "MKI67"]
CONTROLS    = ["CEBPA", "SFTPC", "CDX2"]

ALL_TARGET  = B_SWITCH + T_SWITCH + SCAFFOLD + CONTROLS

# Cell type labels from annotation file
B_BLAST_LABELS  = ["ETV6.RUNX1.1", "ETV6.RUNX1.2",
                   "ETV6.RUNX1.3", "ETV6.RUNX1.4",
                   "HHD.1", "HHD.2"]
T_BLAST_LABELS  = ["PRE-T.1", "PRE-T.2"]
NORMAL_B_LABELS = ["B cells + Mono"]
NORMAL_T_LABELS = ["T cells + NK"]
LABEL_COL       = "celltype"

# Sample name mapping:
# filename prefix → annotation prefix
SAMPLE_MAP = {
    "GSM3872434_ETV6-RUNX1_1": "ETV6.RUNX1.1",
    "GSM3872435_ETV6-RUNX1_2": "ETV6.RUNX1.2",
    "GSM3872436_ETV6-RUNX1_3": "ETV6.RUNX1.3",
    "GSM3872437_ETV6-RUNX1_4": "ETV6.RUNX1.4",
    "GSM3872438_HHD_1":         "HHD.1",
    "GSM3872439_HHD_2":         "HHD.2",
    "GSM3872440_PRE-T_1":       "PRE-T.1",
    "GSM3872441_PRE-T_2":       "PRE-T.2",
    "GSM3872442_PBMMC_1":       "PBMMC.1",
    "GSM3872443_PBMMC_2":       "PBMMC.2",
    "GSM3872444_PBMMC_3":       "PBMMC.3",
}

# ============================================================
# STEP 1: LOAD ANNOTATIONS
# ============================================================

def load_annotations():
    log("=" * 56)
    log("STEP 1: LOADING ANNOTATIONS")
    log("=" * 56)

    ann = pd.read_csv(
        DATA_DIR + "GSE132509_cell_annotations.tsv",
        sep="\t", index_col=0)

    log(f"Total annotated cells: {len(ann)}")
    log("Cell type distribution:")
    log(str(ann[LABEL_COL].value_counts()))

    return ann

# ============================================================
# STEP 2: LOAD ALL SAMPLES
# ============================================================

def load_all_samples(ann):
    log("=" * 56)
    log("STEP 2: LOADING EXPRESSION DATA")
    log("=" * 56)

    cache = RESULTS_DIR + "expr_cache.pkl"
    if os.path.exists(cache):
        log("Loading from cache...")
        expr = pd.read_pickle(cache)
        log(f"Cached shape: {expr.shape}")
        return expr

    samples = []

    for gsm_prefix, ann_prefix in SAMPLE_MAP.items():
        barcodes_file = DATA_DIR + gsm_prefix + ".barcodes.tsv.gz"
        genes_file    = DATA_DIR + gsm_prefix + ".genes.tsv.gz"
        matrix_file   = DATA_DIR + gsm_prefix + ".matrix.mtx.gz"

        if not all(os.path.exists(f) for f in
                   [barcodes_file, genes_file, matrix_file]):
            log(f"Skipping {gsm_prefix} — missing files")
            continue

        log(f"Loading {ann_prefix}...")

        # Load barcodes
        with gzip.open(barcodes_file, 'rt') as f:
            barcodes = [line.strip() for line in f]

        # Load genes — two columns: Ensembl + symbol
        gene_df = pd.read_csv(
            genes_file, sep="\t",
            header=None, compression='gzip',
            names=["ensembl", "symbol"])
        gene_list = gene_df["symbol"].tolist()

        # Load matrix
        with gzip.open(matrix_file, 'rb') as f:
            mat = mmread(f).tocsc()

        log(f"  Matrix shape: {mat.shape} "
            f"({len(gene_list)} genes x "
            f"{len(barcodes)} cells)")

        # Detect orientation
        n_genes = len(gene_list)
        n_cells = len(barcodes)

        if mat.shape[0] == n_genes:
            pass  # genes x cells — standard
        elif mat.shape[1] == n_genes:
            mat = mat.T.tocsc()
        else:
            log(f"  WARNING: shape mismatch "
                f"{mat.shape} vs {n_genes} genes")

        # Build cell IDs matching annotation format
        # annotation: PBMMC.1_AAACCTGCAGACGCAA-1
        # barcode:    AAACCTGCAGACGCAA-1
        cell_ids = [f"{ann_prefix}_{b}"
                    for b in barcodes]

        # Find target gene indices
        target_idx   = []
        target_names = []
        for g in ALL_TARGET:
            if g in gene_list:
                idx = gene_list.index(g)
                target_idx.append(idx)
                target_names.append(g)

        if not target_idx:
            log(f"  WARNING: no target genes found")
            continue

        # Extract target genes
        sub = mat[target_idx, :].toarray().T
        df  = pd.DataFrame(sub,
                           index=cell_ids,
                           columns=target_names)

        # log1p normalize
        df = np.log1p(df)

        # Add cell type labels from annotation
        df[LABEL_COL] = ann[LABEL_COL].reindex(
            df.index).values
        df["sample"] = ann_prefix

        n_matched = df[LABEL_COL].notna().sum()
        log(f"  {ann_prefix}: {len(df)} cells "
            f"({n_matched} matched to annotations)")

        samples.append(df)

    combined = pd.concat(samples, ignore_index=False)
    log(f"\nTotal cells loaded: {len(combined)}")
    log(f"Cells with annotations: "
        f"{combined[LABEL_COL].notna().sum()}")

    combined.to_pickle(cache)
    log(f"Cached: {cache}")

    return combined

# ============================================================
# STEP 3: DEFINE COMPARISON GROUPS
# ============================================================

def define_groups(combined):
    log("=" * 56)
    log("STEP 3: DEFINE COMPARISON GROUPS")
    log("=" * 56)

    b_blast  = combined[
        combined[LABEL_COL].isin(B_BLAST_LABELS)]
    t_blast  = combined[
        combined[LABEL_COL].isin(T_BLAST_LABELS)]
    normal_b = combined[
        combined[LABEL_COL].isin(NORMAL_B_LABELS)]
    normal_t = combined[
        combined[LABEL_COL].isin(NORMAL_T_LABELS)]

    log(f"B-ALL blasts:   {len(b_blast):6} cells "
        f"(ETV6-RUNX1 + HHD)")
    log(f"T-ALL blasts:   {len(t_blast):6} cells "
        f"(PRE-T)")
    log(f"Normal B cells: {len(normal_b):6} cells")
    log(f"Normal T cells: {len(normal_t):6} cells")

    return b_blast, t_blast, normal_b, normal_t

# ============================================================
# STEP 4: COMPUTE SIGNATURE
# ============================================================

def compute_signature(blast, normal,
                      switch_genes, cancer_name,
                      normal_name):
    log()
    log("=" * 56)
    log(f"COMPARISON: {cancer_name} vs {normal_name}")
    log("=" * 56)
    log(f"Blast cells:  {len(blast)}")
    log(f"Normal cells: {len(normal)}")
    log()

    def fmt_p(p):
        if np.isnan(p):  return "N/A      "
        if p < 0.001:    return f"{p:.2e} ***"
        if p < 0.01:     return f"{p:.4f} ** "
        if p < 0.05:     return f"{p:.4f} *  "
        return            f"{p:.4f}    "

    results = []
    all_genes = (switch_genes + SCAFFOLD + CONTROLS)

    for gene in all_genes:
        if gene not in blast.columns:
            continue
        if gene not in normal.columns:
            continue

        blast_vals  = blast[gene].dropna()
        normal_vals = normal[gene].dropna()

        if len(blast_vals) < 5 or len(normal_vals) < 5:
            continue

        blast_mean  = blast_vals.mean()
        normal_mean = normal_vals.mean()

        suppression_pct = (
            (normal_mean - blast_mean) /
            (normal_mean + 1e-6) * 100
        )
        elevation_pct = (
            (blast_mean - normal_mean) /
            (normal_mean + 1e-6) * 100
        )

        _, pval_supp = stats.mannwhitneyu(
            normal_vals, blast_vals,
            alternative='greater')
        _, pval_elev = stats.mannwhitneyu(
            blast_vals, normal_vals,
            alternative='greater')

        is_switch   = gene in switch_genes
        is_scaffold = gene in SCAFFOLD
        is_control  = gene in CONTROLS

        role = ('SWITCH'   if is_switch   else
                'SCAFFOLD' if is_scaffold else
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
            result = "SCAFFOLD"
        else:
            # Controls — CEBPA should be flat
            if abs(suppression_pct) < 30:
                result = "CONTROL OK"
            else:
                result = "CONTROL UNEXPECTED"

        results.append({
            'gene':            gene,
            'cancer':          cancer_name,
            'role':            role,
            'blast_expr':      round(blast_mean, 4),
            'normal_expr':     round(normal_mean, 4),
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
            "SCAFFOLD"    if result == "SCAFFOLD"     else
            "✓ CTRL OK"   if result == "CONTROL OK"   else
            "✗ " + result
        )

        log(f"{gene:8} [{role:8}] | "
            f"Blast={blast_mean:.4f} "
            f"Normal={normal_mean:.4f} | "
            f"{direction:32} | "
            f"p={fmt_p(pval_supp)} | "
            f"{flag}")

    results_df = pd.DataFrame(results)

    n_sw_c = (results_df[
        results_df['role'] == 'SWITCH'
    ]['result'] == 'CONFIRMED').sum()
    n_sw_p = (results_df[
        results_df['role'] == 'SWITCH'
    ]['result'] == 'PARTIAL').sum()
    n_sw   = len(results_df[
        results_df['role'] == 'SWITCH'])

    log()
    log(f"Switch genes confirmed: {n_sw_c}/{n_sw}")
    log(f"Switch genes partial:   {n_sw_p}/{n_sw}")

    if n_sw_c >= 3:
        log(f"*** {cancer_name} FALSE ATTRACTOR "
            f"CONFIRMED ***")
    elif n_sw_c + n_sw_p >= 2:
        log(f"** PARTIAL {cancer_name} CONFIRMATION **")

    return results_df

# ============================================================
# STEP 5: LINEAGE SPECIFICITY TEST
# ============================================================

def lineage_specificity_test(combined,
                              b_blast, t_blast,
                              normal_b, normal_t):
    log()
    log("=" * 56)
    log("STEP 5: LINEAGE SPECIFICITY TEST")
    log("=" * 56)
    log("CEBPA — confirmed myeloid switch gene")
    log("AML: 94.7%  CML: 90.3%  both p≈0")
    log("Prediction: FLAT in ALL (lymphoid)")
    log("If flat — switch genes are lineage-")
    log("specific. The invariant holds.")
    log()

    for gene in ["CEBPA", "SFTPC", "CDX2"]:
        if gene not in combined.columns:
            log(f"{gene}: not in dataset")
            continue

        bb = b_blast[gene].mean()  if gene in b_blast.columns  else 0
        tb = t_blast[gene].mean()  if gene in t_blast.columns  else 0
        nb = normal_b[gene].mean() if gene in normal_b.columns else 0
        nt = normal_t[gene].mean() if gene in normal_t.columns else 0

        log(f"{gene:8}: B-blast={bb:.4f}  "
            f"T-blast={tb:.4f}  "
            f"Normal-B={nb:.4f}  "
            f"Normal-T={nt:.4f}")

        if gene == "CEBPA":
            all_vals = [bb, tb, nb, nt]
            if max(all_vals) < 0.2:
                log(f"  → CEBPA flat across ALL "
                    f"populations: max={max(all_vals):.4f}")
                log(f"  → LINEAGE SPECIFICITY CONFIRMED")
                log(f"  → Myeloid switch genes do not")
                log(f"     apply to lymphoid cancers.")
            else:
                log(f"  → CEBPA unexpectedly expressed: "
                    f"max={max(all_vals):.4f}")

    log()
    log("GATA3 cross-cancer test:")
    log("BRCA: confirmed luminal switch 53.4%")
    log("T-ALL: testing now in T-cell context")
    if "GATA3" in t_blast.columns:
        tb_gata3 = t_blast["GATA3"].mean()
        nt_gata3 = normal_t["GATA3"].mean()
        supp = (nt_gata3 - tb_gata3) / (nt_gata3 + 1e-6) * 100
        log(f"  T-blast GATA3:  {tb_gata3:.4f}")
        log(f"  Normal-T GATA3: {nt_gata3:.4f}")
        log(f"  Suppression:    {supp:.1f}%")
        if supp > 30:
            log(f"  → GATA3 confirmed in T-ALL")
            log(f"  → Same gene. BRCA (luminal) + T-ALL")
            log(f"  → Gene reused across lineages")
            log(f"  → as lineage-specific switch")
        else:
            log(f"  → GATA3 not suppressed in T-ALL")
            log(f"  → GATA3 may be BRCA-specific")

# ============================================================
# STEP 6: FIGURE
# ============================================================

def generate_figure(b_results, t_results,
                    b_blast, t_blast,
                    normal_b, normal_t):
    log()
    log("=" * 56)
    log("STEP 6: GENERATING FIGURE")
    log("=" * 56)

    fig = plt.figure(figsize=(22, 14))
    gs  = gridspec.GridSpec(3, 3, figure=fig,
                            hspace=0.55, wspace=0.4)

    def make_bar_panel(ax, blast, normal,
                       genes, blast_label,
                       normal_label, title,
                       results_df):
        x     = np.arange(len(genes))
        width = 0.35

        b_means = [blast[g].mean()
                   if g in blast.columns else 0
                   for g in genes]
        n_means = [normal[g].mean()
                   if g in normal.columns else 0
                   for g in genes]
        b_sems  = [blast[g].sem()
                   if g in blast.columns else 0
                   for g in genes]
        n_sems  = [normal[g].sem()
                   if g in normal.columns else 0
                   for g in genes]

        ax.bar(x - width/2, b_means, width,
               yerr=b_sems, capsize=3,
               label=blast_label,
               color='crimson', alpha=0.85)
        ax.bar(x + width/2, n_means, width,
               yerr=n_sems, capsize=3,
               label=normal_label,
               color='steelblue', alpha=0.85)

        ax.set_xticks(x)
        ax.set_xticklabels(genes, fontsize=9,
                            rotation=15)
        ax.set_ylabel("Mean log1p(UMI)", fontsize=9)
        ax.set_title(title, fontsize=9,
                     fontweight='bold')
        ax.legend(fontsize=8)

        if results_df is not None:
            for i, gene in enumerate(genes):
                row = results_df[
                    results_df['gene'] == gene]
                if len(row) == 0:
                    continue
                row = row.iloc[0]
                pct = row['suppression_pct']
                color = ('darkgreen'
                         if row['result'] == 'CONFIRMED'
                         else 'gray')
                label = (f"{pct:.0f}%↓"
                         if pct > 0
                         else f"{abs(pct):.0f}%↑")
                ax.annotate(
                    label,
                    xy=(i, max(b_means[i],
                               n_means[i]) + 0.005),
                    ha='center', fontsize=8,
                    color=color,
                    fontweight='bold')

    # Panel A — B-ALL switch genes
    ax_a = fig.add_subplot(gs[0, :2])
    make_bar_panel(
        ax_a, b_blast, normal_b, B_SWITCH,
        'B-ALL blasts', 'Normal B cells',
        "A. B-ALL False Attractor\n"
        "PAX5 EBF1 IKZF1 CD19 MS4A1\n"
        "Red=B-ALL blasts  Blue=Normal B cells",
        b_results)

    # Panel B — T-ALL switch genes
    ax_b = fig.add_subplot(gs[1, :2])
    make_bar_panel(
        ax_b, t_blast, normal_t, T_SWITCH,
        'T-ALL blasts', 'Normal T cells',
        "B. T-ALL False Attractor\n"
        "GATA3 BCL11B TCF7 CD3E TRBC1\n"
        "Red=T-ALL blasts  Blue=Normal T cells",
        t_results)

    # Panel C — Lineage specificity
    ax_c = fig.add_subplot(gs[2, :2])
    control_genes = ["CEBPA", "CDX2", "SFTPC"]
    avail_ctrl = [g for g in control_genes
                  if g in b_blast.columns]

    x     = np.arange(len(avail_ctrl))
    width = 0.2
    groups = [
        (b_blast,  'B-ALL blast',   'crimson',  -1.5),
        (t_blast,  'T-ALL blast',   'darkorange', -0.5),
        (normal_b, 'Normal B',      'steelblue',  0.5),
        (normal_t, 'Normal T',      'navy',        1.5),
    ]
    for grp, label, color, offset in groups:
        means = [grp[g].mean()
                 if g in grp.columns else 0
                 for g in avail_ctrl]
        ax_c.bar(x + offset * width, means, width,
                 label=label, color=color, alpha=0.8)

    ax_c.set_xticks(x)
    ax_c.set_xticklabels(avail_ctrl, fontsize=9)
    ax_c.set_ylabel("Mean log1p(UMI)", fontsize=9)
    ax_c.set_title(
        "C. Lineage Specificity Test\n"
        "CEBPA (myeloid switch) should be FLAT "
        "in ALL lymphoid populations\n"
        "CDX2 (CRC switch) and SFTPC (lung switch) "
        "should be zero everywhere",
        fontsize=9, fontweight='bold')
    ax_c.legend(fontsize=7)

    # Panel D — B-ALL results table
    ax_d = fig.add_subplot(gs[0, 2])
    ax_d.axis('off')
    if b_results is not None and len(b_results) > 0:
        tbl = b_results[
            b_results['role'] == 'SWITCH'
        ][['gene', 'suppression_pct',
           'pval_supp', 'result']].copy()
        tbl['pval_supp'] = tbl['pval_supp'].apply(
            lambda p: f"{p:.2e}"
            if not np.isnan(p) else "N/A")
        tbl.columns = ['Gene', 'Supp%',
                       'p-val', 'Result']
        table = ax_d.table(
            cellText=tbl.values,
            colLabels=tbl.columns,
            loc='center', cellLoc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1.1, 1.8)
        for i, (_, row) in enumerate(tbl.iterrows()):
            c = ('#c8e6c9'
                 if row['Result'] == 'CONFIRMED'
                 else '#fff9c4')
            for j in range(len(tbl.columns)):
                table[i+1, j].set_facecolor(c)
    ax_d.set_title("D. B-ALL Results",
                   fontsize=9, fontweight='bold',
                   pad=15)

    # Panel E — T-ALL results table
    ax_e = fig.add_subplot(gs[1, 2])
    ax_e.axis('off')
    if t_results is not None and len(t_results) > 0:
        tbl = t_results[
            t_results['role'] == 'SWITCH'
        ][['gene', 'suppression_pct',
           'pval_supp', 'result']].copy()
        tbl['pval_supp'] = tbl['pval_supp'].apply(
            lambda p: f"{p:.2e}"
            if not np.isnan(p) else "N/A")
        tbl.columns = ['Gene', 'Supp%',
                       'p-val', 'Result']
        table = ax_e.table(
            cellText=tbl.values,
            colLabels=tbl.columns,
            loc='center', cellLoc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1.1, 1.8)
        for i, (_, row) in enumerate(tbl.iterrows()):
            c = ('#c8e6c9'
                 if row['Result'] == 'CONFIRMED'
                 else '#fff9c4')
            for j in range(len(tbl.columns)):
                table[i+1, j].set_facecolor(c)
    ax_e.set_title("E. T-ALL Results",
                   fontsize=9, fontweight='bold',
                   pad=15)

    # Panel F — suppression comparison
    ax_f = fig.add_subplot(gs[2, 2])
    all_results = pd.concat(
        [r for r in [b_results, t_results]
         if r is not None and len(r) > 0],
        ignore_index=True)
    if len(all_results) > 0:
        sw = all_results[
            all_results['role'] == 'SWITCH'
        ].sort_values('suppression_pct',
                      ascending=False)
        colors = ['crimson'
                  if 'ALL' in str(r['cancer'])
                     and 'B' in str(r['cancer'])
                  else 'darkorange'
                  for _, r in sw.iterrows()]
        ax_f.barh(
            sw['gene'] + ' (' + sw['cancer'] + ')',
            sw['suppression_pct'],
            color=colors, alpha=0.82)
        ax_f.axvline(x=30, color='darkred',
                     linestyle='--', lw=1.5,
                     label='30% threshold')
        ax_f.axvline(x=0, color='black',
                     linewidth=0.8, alpha=0.5)
        ax_f.set_xlabel("Suppression (%)",
                        fontsize=8)
        ax_f.set_title(
            "F. All Switch Genes\n"
            "Red=B-ALL  Orange=T-ALL",
            fontsize=9, fontweight='bold')
        ax_f.legend(fontsize=8)

    fig.suptitle(
        "ALL False Attractor — B-ALL and T-ALL\n"
        "GSE132509 Caron et al. 2020  |  "
        "OrganismCore  |  Document 79\n"
        "38,922 cells  |  8 ALL patients  |  "
        "3 normal donors",
        fontsize=11, fontweight='bold')

    outpath = RESULTS_DIR + "all_saddle_figure.png"
    plt.savefig(outpath, dpi=180,
                bbox_inches='tight')
    plt.close()
    log(f"Figure saved: {outpath}")

# ============================================================
# MAIN
# ============================================================

def main():
    log("=" * 56)
    log("ALL FALSE ATTRACTOR ANALYSIS")
    log("OrganismCore — False Attractor Framework")
    log("Cancer Validation #7 — Document 79")
    log("Session 2 — Lymphoid")
    log("=" * 56)

    ann = load_annotations()

    combined = load_all_samples(ann)

    b_blast, t_blast, normal_b, normal_t = \
        define_groups(combined)

    b_results = compute_signature(
        b_blast, normal_b,
        B_SWITCH, "B-ALL", "Normal B cells")

    t_results = compute_signature(
        t_blast, normal_t,
        T_SWITCH, "T-ALL", "Normal T cells")

    lineage_specificity_test(
        combined,
        b_blast, t_blast,
        normal_b, normal_t)

    generate_figure(
        b_results, t_results,
        b_blast, t_blast,
        normal_b, normal_t)

    # Save combined results
    all_results = pd.concat(
        [b_results, t_results],
        ignore_index=True)
    all_results.to_csv(
        RESULTS_DIR + "all_saddle_results.csv",
        index=False)

    log()
    log("=" * 56)
    log("ALL ANALYSIS COMPLETE")
    log(f"Results: {RESULTS_DIR}")
    log("=" * 56)


if __name__ == "__main__":
    main()
