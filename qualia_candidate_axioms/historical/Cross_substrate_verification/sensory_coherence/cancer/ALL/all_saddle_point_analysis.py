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

B_SWITCH  = ["PAX5", "EBF1", "IKZF1", "CD19", "MS4A1"]
T_SWITCH  = ["GATA3", "BCL11B", "TCF7", "CD3E", "TRBC1"]
SCAFFOLD  = ["CD34", "MKI67"]
CONTROLS  = ["CEBPA", "SFTPC", "CDX2"]

ALL_TARGET = B_SWITCH + T_SWITCH + SCAFFOLD + CONTROLS

B_BLAST_LABELS  = ["ETV6.RUNX1.1", "ETV6.RUNX1.2",
                   "ETV6.RUNX1.3", "ETV6.RUNX1.4",
                   "HHD.1", "HHD.2"]
T_BLAST_LABELS  = ["PRE-T.1", "PRE-T.2"]
NORMAL_B_LABELS = ["B cells + Mono"]
NORMAL_T_LABELS = ["T cells + NK"]
LABEL_COL       = "celltype"

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
    log()
    log("Sample annotation IDs (first 3 per sample):")
    for prefix in set(
        i.split("_")[0] for i in ann.index
    ):
        examples = [i for i in ann.index
                    if i.startswith(prefix)][:3]
        log(f"  {prefix}: {examples}")

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
        log("Label distribution in cache:")
        log(str(expr[LABEL_COL].value_counts()))
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

        log(f"Loading {ann_prefix} ({gsm_prefix})...")

        # Load barcodes
        with gzip.open(barcodes_file, 'rt') as f:
            barcodes = [line.strip() for line in f]

        # Load genes
        gene_df = pd.read_csv(
            genes_file, sep="\t",
            header=None, compression='gzip',
            names=["ensembl", "symbol"])
        gene_list = gene_df["symbol"].tolist()

        # Load matrix
        with gzip.open(matrix_file, 'rb') as f:
            mat = mmread(f).tocsc()

        n_genes = len(gene_list)

        if mat.shape[0] == n_genes:
            pass  # genes x cells
        elif mat.shape[1] == n_genes:
            mat = mat.T.tocsc()
        else:
            log(f"  WARNING: shape mismatch "
                f"{mat.shape} vs {n_genes} genes")

        # Build cell IDs
        # annotation format: ETV6.RUNX1.1_AAACCTGAGACTTTCG
        # barcodes format:   AAACCTGAGACTTTCG (no suffix)
        #                 or AAACCTGAGACTTTCG-1 (with suffix)
        # Check annotation to determine which format
        ann_ids = ann.index.tolist()
        sample_ann_ids = [
            i for i in ann_ids
            if i.startswith(ann_prefix + "_")
        ]

        if len(sample_ann_ids) == 0:
            log(f"  WARNING: no annotation IDs found "
                f"for prefix '{ann_prefix}'")
            log(f"  Sample ann IDs: "
                f"{ann_ids[:5]}")
            continue

        # Get barcode portion from annotation
        ann_barcodes = [
            i.split("_", 1)[1]
            for i in sample_ann_ids
        ]

        log(f"  Annotation barcodes sample: "
            f"{ann_barcodes[:3]}")
        log(f"  File barcodes sample: "
            f"{barcodes[:3]}")

        # Build cell_id -> annotation lookup
        ann_barcode_set = set(ann_barcodes)
        file_barcode_set = set(barcodes)

        # Check direct match
        direct_match = len(
            ann_barcode_set & file_barcode_set)
        log(f"  Direct barcode match: {direct_match}")

        # If no direct match try stripping -1/-2 suffix
        if direct_match == 0:
            stripped = {
                b.rsplit("-", 1)[0]: b
                for b in barcodes
            }
            strip_match = len(
                ann_barcode_set &
                set(stripped.keys()))
            log(f"  Stripped suffix match: {strip_match}")

        # Build cell IDs using annotation barcode format
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

        log(f"  Target genes found: {target_names}")

        if not target_idx:
            log(f"  WARNING: no target genes found")
            continue

        sub = mat[target_idx, :].toarray().T
        df  = pd.DataFrame(sub,
                           index=cell_ids,
                           columns=target_names)
        df  = np.log1p(df)

        # Match labels from annotation
        df[LABEL_COL] = ann[LABEL_COL].reindex(
            df.index).values
        df["sample"] = ann_prefix

        n_matched = df[LABEL_COL].notna().sum()
        log(f"  {ann_prefix}: {len(df)} cells, "
            f"{n_matched} matched to annotations")

        if n_matched == 0:
            log(f"  DEBUG: first 3 cell IDs built: "
                f"{cell_ids[:3]}")
            log(f"  DEBUG: first 3 ann IDs for this "
                f"sample: {sample_ann_ids[:3]}")

        samples.append(df)

    combined = pd.concat(samples, ignore_index=False)
    log(f"\nTotal cells loaded: {len(combined)}")
    log(f"Cells with annotations: "
        f"{combined[LABEL_COL].notna().sum()}")
    log("Label distribution:")
    log(str(combined[LABEL_COL].value_counts()))

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

    log(f"B-ALL blasts:   {len(b_blast):6} cells")
    log(f"T-ALL blasts:   {len(t_blast):6} cells")
    log(f"Normal B cells: {len(normal_b):6} cells")
    log(f"Normal T cells: {len(normal_t):6} cells")

    if len(t_blast) == 0:
        log()
        log("WARNING: T-ALL blasts = 0 cells")
        log("Checking PRE-T label variants...")
        labels = combined[LABEL_COL].dropna().unique()
        pre_t = [l for l in labels
                 if 'PRE' in str(l).upper()
                 or 'T' in str(l).upper()]
        log(f"T-related labels found: {pre_t}")

    return b_blast, t_blast, normal_b, normal_t

# ============================================================
# STEP 4: COMPUTE SIGNATURE
# ============================================================

def compute_signature(blast, normal,
                      switch_genes,
                      cancer_name, normal_name):
    log()
    log("=" * 56)
    log(f"COMPARISON: {cancer_name} vs {normal_name}")
    log("=" * 56)
    log(f"Blast cells:  {len(blast)}")
    log(f"Normal cells: {len(normal)}")

    if len(blast) == 0:
        log(f"WARNING: no {cancer_name} blast cells — "
            f"skipping comparison")
        return pd.DataFrame(columns=[
            'gene', 'cancer', 'role',
            'blast_expr', 'normal_expr',
            'suppression_pct', 'pval_supp', 'result'
        ])

    if len(normal) == 0:
        log(f"WARNING: no {normal_name} cells — "
            f"skipping comparison")
        return pd.DataFrame(columns=[
            'gene', 'cancer', 'role',
            'blast_expr', 'normal_expr',
            'suppression_pct', 'pval_supp', 'result'
        ])

    log()

    def fmt_p(p):
        if np.isnan(p):  return "N/A      "
        if p < 0.001:    return f"{p:.2e} ***"
        if p < 0.01:     return f"{p:.4f} ** "
        if p < 0.05:     return f"{p:.4f} *  "
        return            f"{p:.4f}    "

    results = []
    all_genes = switch_genes + SCAFFOLD + CONTROLS

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

        is_switch   = gene in switch_genes
        is_scaffold = gene in SCAFFOLD
        is_control  = gene in CONTROLS

        role = ('SWITCH'   if is_switch   else
                'SCAFFOLD' if is_scaffold else
                'CONTROL')

        if is_switch:
            if (suppression_pct > 30 and
                    pval_supp < 0.05):
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

    if len(results_df) == 0:
        log("WARNING: no results computed")
        return results_df

    sw = results_df[results_df['role'] == 'SWITCH']
    n_sw_c = (sw['result'] == 'CONFIRMED').sum()
    n_sw_p = (sw['result'] == 'PARTIAL').sum()
    n_sw   = len(sw)

    log()
    log(f"Switch genes confirmed: {n_sw_c}/{n_sw}")
    log(f"Switch genes partial:   {n_sw_p}/{n_sw}")

    if n_sw_c >= 3:
        log(f"*** {cancer_name} FALSE ATTRACTOR "
            f"CONFIRMED ***")
    elif n_sw_c + n_sw_p >= 2:
        log(f"** PARTIAL {cancer_name} "
            f"CONFIRMATION **")

    return results_df

# ============================================================
# STEP 5: LINEAGE SPECIFICITY TEST
# ============================================================

def lineage_specificity_test(b_blast, t_blast,
                              normal_b, normal_t):
    log()
    log("=" * 56)
    log("STEP 5: LINEAGE SPECIFICITY TEST")
    log("=" * 56)
    log("CEBPA — confirmed myeloid switch")
    log("AML: 94.7%  CML: 90.3%  both p≈0")
    log("Prediction: FLAT in ALL (lymphoid)")
    log()

    for gene in ["CEBPA", "SFTPC", "CDX2"]:
        vals = {}
        for name, grp in [
            ("B-blast",  b_blast),
            ("T-blast",  t_blast),
            ("Normal-B", normal_b),
            ("Normal-T", normal_t),
        ]:
            if gene in grp.columns and len(grp) > 0:
                vals[name] = grp[gene].mean()
            else:
                vals[name] = 0.0

        log(f"{gene:8}: " +
            "  ".join(f"{k}={v:.4f}"
                      for k, v in vals.items()))

        if gene == "CEBPA":
            mx = max(vals.values())
            if mx < 0.2:
                log(f"  → CEBPA flat (max={mx:.4f}) — "
                    f"LINEAGE SPECIFICITY CONFIRMED")
                log(f"  → Myeloid switch genes do not")
                log(f"     apply to lymphoid cancers")
            else:
                log(f"  → CEBPA expressed (max={mx:.4f})")

    log()
    log("GATA3 cross-cancer test:")
    log("BRCA confirmed luminal switch 53.4%")
    log("T-ALL: testing in T-cell context")
    if ("GATA3" in t_blast.columns and
            len(t_blast) > 0 and
            len(normal_t) > 0):
        tb  = t_blast["GATA3"].mean()
        nt  = normal_t["GATA3"].mean()
        sup = (nt - tb) / (nt + 1e-6) * 100
        log(f"  T-blast GATA3:  {tb:.4f}")
        log(f"  Normal-T GATA3: {nt:.4f}")
        log(f"  Suppression:    {sup:.1f}%")
        if sup > 30:
            log("  → GATA3 confirmed in T-ALL")
            log("  → BRCA (luminal) + T-ALL confirmed")
            log("  → Gene reused across lineages")
        else:
            log("  → GATA3 not suppressed in T-ALL")
    else:
        log("  GATA3 test skipped — "
            "insufficient cells")

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
        if len(blast) == 0 or len(normal) == 0:
            ax.text(0.5, 0.5,
                    f"No data\n{blast_label}",
                    ha='center', va='center',
                    transform=ax.transAxes)
            ax.set_title(title, fontsize=9,
                         fontweight='bold')
            return

        avail = [g for g in genes
                 if g in blast.columns
                 and g in normal.columns]
        if not avail:
            ax.text(0.5, 0.5, "No genes available",
                    ha='center', va='center',
                    transform=ax.transAxes)
            return

        x     = np.arange(len(avail))
        width = 0.35

        b_means = [blast[g].mean()  for g in avail]
        n_means = [normal[g].mean() for g in avail]
        b_sems  = [blast[g].sem()   for g in avail]
        n_sems  = [normal[g].sem()  for g in avail]

        ax.bar(x - width/2, b_means, width,
               yerr=b_sems, capsize=3,
               label=blast_label,
               color='crimson', alpha=0.85)
        ax.bar(x + width/2, n_means, width,
               yerr=n_sems, capsize=3,
               label=normal_label,
               color='steelblue', alpha=0.85)

        ax.set_xticks(x)
        ax.set_xticklabels(avail, fontsize=9,
                            rotation=15)
        ax.set_ylabel("Mean log1p(UMI)", fontsize=9)
        ax.set_title(title, fontsize=9,
                     fontweight='bold')
        ax.legend(fontsize=8)

        if (results_df is not None and
                len(results_df) > 0 and
                'gene' in results_df.columns):
            for i, gene in enumerate(avail):
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

    ax_a = fig.add_subplot(gs[0, :2])
    make_bar_panel(
        ax_a, b_blast, normal_b, B_SWITCH,
        'B-ALL blasts', 'Normal B cells',
        "A. B-ALL False Attractor — "
        "PAX5 EBF1 IKZF1 CD19 MS4A1",
        b_results)

    ax_b = fig.add_subplot(gs[1, :2])
    make_bar_panel(
        ax_b, t_blast, normal_t, T_SWITCH,
        'T-ALL blasts', 'Normal T cells',
        "B. T-ALL False Attractor — "
        "GATA3 BCL11B TCF7 CD3E TRBC1",
        t_results)

    ax_c = fig.add_subplot(gs[2, :2])
    ctrl_genes = [g for g in
                  ["CEBPA", "CDX2", "SFTPC"]
                  if g in b_blast.columns]
    if ctrl_genes:
        x     = np.arange(len(ctrl_genes))
        width = 0.2
        groups = [
            (b_blast,  'B-ALL',    'crimson',    -1.5),
            (t_blast,  'T-ALL',    'darkorange',  -0.5),
            (normal_b, 'Normal B', 'steelblue',    0.5),
            (normal_t, 'Normal T', 'navy',          1.5),
        ]
        for grp, label, color, offset in groups:
            if len(grp) == 0:
                continue
            means = [grp[g].mean()
                     if g in grp.columns else 0
                     for g in ctrl_genes]
            ax_c.bar(x + offset * width, means,
                     width, label=label,
                     color=color, alpha=0.8)
        ax_c.set_xticks(x)
        ax_c.set_xticklabels(ctrl_genes, fontsize=9)
        ax_c.set_ylabel("Mean log1p(UMI)", fontsize=9)
        ax_c.legend(fontsize=7)
    ax_c.set_title(
        "C. Lineage Specificity — CEBPA (myeloid) "
        "should be flat in ALL lymphoid populations",
        fontsize=9, fontweight='bold')

    def make_table(ax, results_df, title):
        ax.axis('off')
        ax.set_title(title, fontsize=9,
                     fontweight='bold', pad=15)
        if (results_df is None or
                len(results_df) == 0 or
                'role' not in results_df.columns):
            ax.text(0.5, 0.5, "No data",
                    ha='center', va='center',
                    transform=ax.transAxes)
            return
        sw = results_df[
            results_df['role'] == 'SWITCH'
        ][['gene', 'suppression_pct',
           'pval_supp', 'result']].copy()
        if len(sw) == 0:
            ax.text(0.5, 0.5, "No switch genes",
                    ha='center', va='center',
                    transform=ax.transAxes)
            return
        sw['pval_supp'] = sw['pval_supp'].apply(
            lambda p: f"{p:.2e}"
            if not np.isnan(p) else "N/A")
        sw.columns = ['Gene', 'Supp%',
                      'p-val', 'Result']
        table = ax.table(
            cellText=sw.values,
            colLabels=sw.columns,
            loc='center', cellLoc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1.1, 1.8)
        for i, (_, row) in enumerate(sw.iterrows()):
            c = ('#c8e6c9'
                 if row['Result'] == 'CONFIRMED'
                 else '#fff9c4')
            for j in range(len(sw.columns)):
                table[i+1, j].set_facecolor(c)

    make_table(fig.add_subplot(gs[0, 2]),
               b_results, "D. B-ALL Results")
    make_table(fig.add_subplot(gs[1, 2]),
               t_results, "E. T-ALL Results")

    ax_f = fig.add_subplot(gs[2, 2])
    all_r = pd.concat(
        [r for r in [b_results, t_results]
         if r is not None and
         len(r) > 0 and
         'role' in r.columns],
        ignore_index=True)
    if len(all_r) > 0:
        sw = all_r[
            all_r['role'] == 'SWITCH'
        ].sort_values('suppression_pct',
                      ascending=False)
        if len(sw) > 0:
            bar_colors = [
                'crimson' if 'B-ALL' in str(r['cancer'])
                else 'darkorange'
                for _, r in sw.iterrows()
            ]
            ax_f.barh(
                sw['gene'] + ' (' +
                sw['cancer'] + ')',
                sw['suppression_pct'],
                color=bar_colors, alpha=0.82)
            ax_f.axvline(x=30, color='darkred',
                         linestyle='--', lw=1.5,
                         label='30% threshold')
            ax_f.axvline(x=0, color='black',
                         linewidth=0.8, alpha=0.5)
            ax_f.set_xlabel("Suppression (%)",
                            fontsize=8)
            ax_f.legend(fontsize=8)
    ax_f.set_title(
        "F. All Switch Genes\n"
        "Red=B-ALL  Orange=T-ALL",
        fontsize=9, fontweight='bold')

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
        b_blast, t_blast,
        normal_b, normal_t)

    generate_figure(
        b_results, t_results,
        b_blast, t_blast,
        normal_b, normal_t)

    all_results = pd.concat(
        [r for r in [b_results, t_results]
         if len(r) > 0],
        ignore_index=True)
    if len(all_results) > 0:
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
