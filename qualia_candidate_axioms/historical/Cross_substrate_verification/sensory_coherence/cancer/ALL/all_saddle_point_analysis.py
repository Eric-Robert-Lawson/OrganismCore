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

"""
ALL FALSE ATTRACTOR ANALYSIS
OrganismCore — Document 79
False Attractor Framework — Cancer Validation #7
Session 2 — Lymphoid

REVISED GENE LIST — v2

LESSON FROM v1:
  B-ALL and T-ALL blasts are NOT
  blocked before lineage identity
  activates. They ARE the lineage —
  PAX5, EBF1, CD19, TCF7, CD3E
  are ON in blasts.
  The block is AFTER lineage identity
  but BEFORE terminal completion.

  The switch genes for ALL are the
  TERMINAL COMPLETION genes —
  the last step the blasts cannot take.

B-ALL terminal completion (new):
  IGHM   — IgM heavy chain
           expressed only in mature
           naive B cells
           NOT in B-cell progenitors
           NOT in blasts
  IGKC   — Ig kappa light chain
           terminal B cell product
  PRDM1  — Blimp1 — plasma cell
           master TF — drives terminal
           B cell differentiation
           into antibody-secreting
           plasma cells
  CD27   — memory/mature B cell marker

T-ALL terminal completion (new):
  SELL   — CD62L — lymph node homing
           expressed on mature naive
           T cells — NOT on blasts
  CCR7   — chemokine receptor
           mature naive T cell
  IL7R   — IL-7 receptor
           mature T cell survival
           signal receptor
  PTPRC  — CD45 — pan-lymphocyte
           marker — high on mature
           T cells

SCAFFOLD (blasts should be HIGH):
  RAG1   — recombination activating
           gene — active in immature
           B and T cells
           HIGH in blasts
           LOW in mature cells
           This is the scaffold —
           confirms blasts are
           immature lymphoid cells
  RAG2   — same — scaffold
  PAX5   — B-cell identity gene
           ON in blasts — scaffold
           for B-ALL comparison
  CD3E   — T-cell identity gene
           ON in blasts — scaffold
           for T-ALL comparison

CONTROLS:
  CEBPA  — myeloid switch — flat
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
# CONFIGURATION — v2 REVISED GENE LIST
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

# REVISED: terminal completion genes
B_SWITCH  = ["IGHM", "IGKC", "PRDM1", "CD27"]
T_SWITCH  = ["SELL", "CCR7", "IL7R", "PTPRC"]

# Scaffolds — should be HIGH in blasts
# RAG1/2 active in immature lymphoid
# PAX5/CD3E = lineage identity (on in blasts)
SCAFFOLD  = ["RAG1", "RAG2", "PAX5", "CD3E",
             "CD34", "MKI67"]

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

    ann_index = ann[LABEL_COL].to_dict()
    samples   = []

    for gsm_prefix, ann_prefix in SAMPLE_MAP.items():
        barcodes_file = DATA_DIR + gsm_prefix + ".barcodes.tsv.gz"
        genes_file    = DATA_DIR + gsm_prefix + ".genes.tsv.gz"
        matrix_file   = DATA_DIR + gsm_prefix + ".matrix.mtx.gz"

        if not all(os.path.exists(f) for f in
                   [barcodes_file, genes_file,
                    matrix_file]):
            log(f"Skipping {gsm_prefix} — "
                f"missing files")
            continue

        log(f"Loading {ann_prefix}...")

        with gzip.open(barcodes_file, 'rt') as f:
            barcodes = [line.strip() for line in f]

        gene_df = pd.read_csv(
            genes_file, sep="\t",
            header=None, compression='gzip',
            names=["ensembl", "symbol"])
        gene_list = gene_df["symbol"].tolist()

        with gzip.open(matrix_file, 'rb') as f:
            mat = mmread(f).tocsc()

        n_genes = len(gene_list)
        if mat.shape[0] == n_genes:
            pass
        elif mat.shape[1] == n_genes:
            mat = mat.T.tocsc()

        sample_ann_ids = [
            i for i in ann_index.keys()
            if i.startswith(ann_prefix + "_")
        ]

        if len(sample_ann_ids) == 0:
            log(f"  WARNING: no annotation IDs "
                f"for {ann_prefix} — skipping")
            continue

        ann_barcodes_sample = set(
            i.split("_", 1)[1]
            for i in sample_ann_ids)

        file_barcode_sample = set(barcodes[:100])
        direct_match = len(
            ann_barcodes_sample &
            file_barcode_sample)

        if direct_match > 0:
            cell_ids = [f"{ann_prefix}_{b}"
                        for b in barcodes]
        else:
            cell_ids = [
                f"{ann_prefix}_{b.rsplit('-', 1)[0]}"
                for b in barcodes
            ]

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

        sub = mat[target_idx, :].toarray().T
        df  = pd.DataFrame(sub,
                           index=cell_ids,
                           columns=target_names)
        df  = np.log1p(df)

        df[LABEL_COL] = [
            ann_index.get(cid, np.nan)
            for cid in df.index
        ]
        df["sample"] = ann_prefix

        n_matched = df[LABEL_COL].notna().sum()
        log(f"  {ann_prefix}: {len(df)} cells, "
            f"{n_matched} matched")

        samples.append(df)

    combined = pd.concat(samples, ignore_index=False)
    log(f"\nTotal cells loaded: {len(combined)}")
    log(f"Annotations matched: "
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
    log()
    log("Testing TERMINAL COMPLETION genes.")
    log("These should be HIGH in normal,")
    log("LOW/absent in blasts.")
    log()

    if len(blast) == 0 or len(normal) == 0:
        log("WARNING: insufficient cells — skipping")
        return pd.DataFrame(columns=[
            'gene', 'cancer', 'role',
            'blast_expr', 'normal_expr',
            'suppression_pct', 'pval_supp',
            'result'
        ])

    def fmt_p(p):
        if np.isnan(p):  return "N/A      "
        if p < 0.001:    return f"{p:.2e} ***"
        if p < 0.01:     return f"{p:.4f} ** "
        if p < 0.05:     return f"{p:.4f} *  "
        return            f"{p:.4f}    "

    results    = []
    all_genes  = switch_genes + SCAFFOLD + CONTROLS

    for gene in all_genes:
        if (gene not in blast.columns or
                gene not in normal.columns):
            continue

        blast_vals  = blast[gene].dropna()
        normal_vals = normal[gene].dropna()

        if (len(blast_vals) < 5 or
                len(normal_vals) < 5):
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
            # Scaffolds expected HIGH in blasts
            if elevation_pct > 0:
                result = "SCAFFOLD HIGH (expected)"
            else:
                result = "SCAFFOLD LOW (unexpected)"
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
            else
            f"elevated   {elevation_pct:+.1f}%"
        )

        flag = (
            "✓ CONFIRMED" if result == "CONFIRMED"
            else "~ PARTIAL" if result == "PARTIAL"
            else "✓ SCAFFOLD↑" if "HIGH" in result
            else "✗ SCAFFOLD↓" if "LOW"  in result
            else "✓ CTRL OK"   if result == "CONTROL OK"
            else "✗ " + result
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

    sw     = results_df[results_df['role'] == 'SWITCH']
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
    else:
        log(f"--- {cancer_name}: insufficient "
            f"confirmation")

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
    log("CEBPA — myeloid switch (AML 94.7% CML 90.3%)")
    log("Prediction: FLAT in ALL lymphoid populations")
    log()

    for gene in ["CEBPA", "SFTPC", "CDX2"]:
        vals = {}
        for name, grp in [
            ("B-blast",  b_blast),
            ("T-blast",  t_blast),
            ("Normal-B", normal_b),
            ("Normal-T", normal_t),
        ]:
            vals[name] = (
                grp[gene].mean()
                if gene in grp.columns
                and len(grp) > 0
                else 0.0
            )
        log(f"{gene:8}: " +
            "  ".join(f"{k}={v:.4f}"
                      for k, v in vals.items()))
        if gene == "CEBPA":
            mx = max(vals.values())
            if mx < 0.2:
                log(f"  → LINEAGE SPECIFICITY CONFIRMED "
                    f"(max={mx:.4f})")
            else:
                log(f"  → Unexpected CEBPA "
                    f"(max={mx:.4f})")

    log()
    log("RAG1/RAG2 scaffold test:")
    log("Should be HIGH in blasts (immature lymphoid)")
    log("LOW in mature normal B and T cells")
    for gene in ["RAG1", "RAG2"]:
        for name, grp in [
            ("B-blast",  b_blast),
            ("T-blast",  t_blast),
            ("Normal-B", normal_b),
            ("Normal-T", normal_t),
        ]:
            if gene in grp.columns and len(grp) > 0:
                val = grp[gene].mean()
                log(f"  {gene} {name}: {val:.4f}")

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
                    "Insufficient data",
                    ha='center', va='center',
                    transform=ax.transAxes,
                    fontsize=12)
            ax.set_title(title, fontsize=9,
                         fontweight='bold')
            return

        avail = [g for g in genes
                 if g in blast.columns
                 and g in normal.columns]
        if not avail:
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
                row   = row.iloc[0]
                pct   = row['suppression_pct']
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
        "A. B-ALL False Attractor — Terminal "
        "Completion Genes\n"
        "IGHM  IGKC  PRDM1  CD27\n"
        "These should be HIGH in normal, "
        "LOW in blasts",
        b_results)

    ax_b = fig.add_subplot(gs[1, :2])
    make_bar_panel(
        ax_b, t_blast, normal_t, T_SWITCH,
        'T-ALL blasts', 'Normal T cells',
        "B. T-ALL False Attractor — Terminal "
        "Completion Genes\n"
        "SELL  CCR7  IL7R  PTPRC\n"
        "These should be HIGH in normal, "
        "LOW in blasts",
        t_results)

    ax_c = fig.add_subplot(gs[2, :2])
    ctrl_genes = [g for g in
                  ["CEBPA", "RAG1", "RAG2", "CDX2"]
                  if g in b_blast.columns]
    if ctrl_genes and len(b_blast) > 0:
        x     = np.arange(len(ctrl_genes))
        width = 0.2
        for grp, label, color, offset in [
            (b_blast,  'B-ALL',    'crimson',    -1.5),
            (t_blast,  'T-ALL',    'darkorange',  -0.5),
            (normal_b, 'Normal B', 'steelblue',    0.5),
            (normal_t, 'Normal T', 'navy',          1.5),
        ]:
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
        "C. Controls + Scaffolds\n"
        "CEBPA flat = lineage specificity confirmed  |  "
        "RAG1/2 high in blasts = immaturity confirmed",
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
                'crimson'
                if 'B-ALL' in str(r['cancer'])
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
        "OrganismCore  |  Document 79  v2\n"
        "Terminal completion genes — "
        "38,922 cells  |  8 ALL patients",
        fontsize=11, fontweight='bold')

    outpath = RESULTS_DIR + "all_saddle_figure_v2.png"
    plt.savefig(outpath, dpi=180,
                bbox_inches='tight')
    plt.close()
    log(f"Figure saved: {outpath}")

# ============================================================
# MAIN
# ============================================================

def main():
    log("=" * 56)
    log("ALL FALSE ATTRACTOR ANALYSIS v2")
    log("OrganismCore — False Attractor Framework")
    log("Cancer Validation #7 — Document 79")
    log("REVISED: Terminal completion gene list")
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
            RESULTS_DIR + "all_saddle_results_v2.csv",
            index=False)

    log()
    log("=" * 56)
    log("ALL ANALYSIS v2 COMPLETE")
    log(f"Results: {RESULTS_DIR}")
    log("=" * 56)


if __name__ == "__main__":
    main()
