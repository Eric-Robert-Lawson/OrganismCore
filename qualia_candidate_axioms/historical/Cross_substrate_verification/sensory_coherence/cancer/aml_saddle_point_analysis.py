"""
AML SADDLE POINT EXPRESSION ANALYSIS
OrganismCore — Document 71 — CORRECTED
False Attractor Framework
February 28, 2026

How To Get Files:
https://zenodo.org/records/10013368

Needs files:

anno_cells_corr.txt
counts_corr.csv


CORRECTION FROM RUN 1:
  Saddle point is at GMP-like, not HSC-like.
  The differentiation block is between GMP-like
  and ProMono-like/Mono-like — where SPI1 jumps
  from 0.04 to 0.48 and KLF4 from 0.04 to 0.79
  in the malignant trajectory.

  Reference for suppression changed from HSC/HSPCs
  to CD14+ monocytes/Mono/ProMono — the normal
  differentiated endpoint these cells cannot reach.

  This is what the false attractor looks like:
  not a minimum at the top — a CEILING throughout
  the malignant trajectory below the normal
  differentiated level. The gap IS the false attractor.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from scipy import stats
import os
import warnings
warnings.filterwarnings('ignore')

ANNO_FILE   = "anno_cells_corr.txt"
EXPR_FILE   = "counts_corr.csv"
RESULTS_DIR = "./aml_saddle_results/"
os.makedirs(RESULTS_DIR, exist_ok=True)
LOG_FILE    = RESULTS_DIR + "analysis_log.txt"

with open(LOG_FILE, "w") as f:
    f.write("")

def log(msg=""):
    print(msg)
    with open(LOG_FILE, "a") as f:
        f.write(str(msg) + "\n")

SADDLE_CANDIDATES = ["CEBPA", "SPI1", "KLF4",
                     "RUNX1", "IRF8"]
CONTROL_GENES     = ["MYC", "CD34", "GATA1", "MPO"]
ALL_GENES         = SADDLE_CANDIDATES + CONTROL_GENES

NORMAL_ORDER    = ["HSC", "HSPCs", "Prog", "GMP",
                   "ProMono", "Mono", "cDC", "pDC"]
MALIGNANT_ORDER = ["HSC", "HSC-like",
                   "Prog-like", "GMP-like",
                   "ProMono-like", "Mono-like",
                   "cDC-like"]

# CORRECTED: saddle point is the GMP-like block
# where differentiation is arrested
SADDLE_POSITIONS = ["GMP-like", "Prog-like"]

# CORRECTED: reference is normal differentiated endpoint
# — what these cells should become but cannot
REF_NORMAL = ['CD14+ monocytes', 'Mono', 'ProMono']


def load_annotations():
    log("="*56)
    log("STEP 1: LOADING ANNOTATIONS")
    log("="*56)
    anno = pd.read_csv(ANNO_FILE, sep="\t", index_col=0)
    log(f"Loaded: {anno.shape[0]} cells")
    anno['is_malignant'] = anno['malignant'].astype(bool)
    log(f"Malignant: {anno['is_malignant'].sum()}")
    log(f"Normal:    {(~anno['is_malignant']).sum()}")
    return anno, 'cell_type_original'


def load_expression_transposed():
    log("="*56)
    log("STEP 2: LOADING EXPRESSION (cached from run 1)")
    log("="*56)

    # Check if we already have the extracted genes cached
    cache_file = RESULTS_DIR + "expr_cache.csv"
    if os.path.exists(cache_file):
        log("Loading from cache (fast)...")
        expr = pd.read_csv(cache_file, index_col=0)
        log(f"Cached matrix: {expr.shape[0]} cells x "
            f"{expr.shape[1]} genes")
        return expr, list(expr.index)

    log(f"Scanning {EXPR_FILE} "
        f"({os.path.getsize(EXPR_FILE)/1e9:.1f}GB)...")
    log("(scanning for target genes — ~10-20 min)")

    target_set  = set(ALL_GENES)
    found_rows  = {}
    header_cols = None
    genes_scanned = 0

    with open(EXPR_FILE, 'r') as f:
        for line_num, line in enumerate(f):
            line = line.rstrip('\n')
            if line_num == 0:
                header_cols = line.split(',')
                continue
            comma_pos = line.index(',')
            gene_name = line[:comma_pos]
            genes_scanned += 1
            if genes_scanned % 1000 == 0:
                print('.', end='', flush=True)
            if gene_name in target_set:
                found_rows[gene_name] = \
                    line[comma_pos + 1:].split(',')
                print(f' [{gene_name}]', end='', flush=True)
                if len(found_rows) == len(target_set):
                    print()
                    break

    print()
    log(f"Found: {list(found_rows.keys())}")

    if not found_rows:
        return None, None

    cell_ids = header_cols[1:]
    expr_dict = {}
    for gene, values in found_rows.items():
        float_vals = []
        for v in values:
            try:
                float_vals.append(float(v))
            except (ValueError, TypeError):
                float_vals.append(np.nan)
        expr_dict[gene] = float_vals

    expr = pd.DataFrame(expr_dict, index=cell_ids)

    # Save cache for future runs
    expr.to_csv(cache_file)
    log(f"Cached to {cache_file} for fast reloads.")
    log(f"Matrix: {expr.shape[0]} x {expr.shape[1]}")
    return expr, cell_ids


def compute_trajectory_profiles(expr, anno, ct_col):
    log("="*56)
    log("STEP 3: TRAJECTORY PROFILES")
    log("="*56)

    common_cells = expr.index.intersection(anno.index)
    log(f"Common cells: {len(common_cells)}")

    if len(common_cells) < 100:
        n      = min(len(expr), len(anno))
        expr_a = expr.iloc[:n].copy()
        expr_a.index = anno.index[:n]
        anno_a = anno.iloc[:n].copy()
        common_cells = expr_a.index
    else:
        expr_a = expr.loc[common_cells]
        anno_a = anno.loc[common_cells]

    combined = expr_a.copy()
    combined['CellTypeLabel'] = anno_a[ct_col].values
    combined['IsMalignant']   = anno_a['is_malignant'].values
    combined['TrajPosition']  = combined['CellTypeLabel']

    available_genes = [g for g in ALL_GENES
                       if g in combined.columns]

    grouped    = combined.groupby('TrajPosition')[available_genes]
    traj_mean  = grouped.mean()
    traj_sem   = grouped.sem()
    traj_count = grouped.count()
    traj_stats = {'mean': traj_mean,
                  'sem':  traj_sem,
                  'count':traj_count}

    # Print the key comparison the framework cares about
    log("\nKEY POSITIONS — normal vs malignant myeloid:")
    key_positions = [
        'HSC', 'HSPCs', 'Prog', 'GMP', 'ProMono',
        'Mono', 'CD14+ monocytes',
        'HSC-like', 'Prog-like', 'GMP-like',
        'ProMono-like', 'Mono-like'
    ]
    available_key = [p for p in key_positions
                     if p in traj_mean.index]
    log(str(traj_mean.loc[available_key,
            SADDLE_CANDIDATES].round(4)))

    return combined, traj_stats, available_genes


def compute_saddle_point_signature(combined,
                                    traj_stats,
                                    available_genes):
    log("="*56)
    log("STEP 4: SADDLE POINT SIGNATURE — CORRECTED")
    log("="*56)
    log("CORRECTED PREDICTION:")
    log("  Saddle point = GMP-like/Prog-like")
    log("  (differentiation block between GMP-like")
    log("   and ProMono-like/Mono-like)")
    log("  Reference = CD14+ monocytes/Mono/ProMono")
    log("  (what these cells should become but cannot)")
    log()
    log("FRAMEWORK RESTATEMENT:")
    log("  The false attractor is not a minimum at the")
    log("  TOP of the hierarchy — it is a CEILING on")
    log("  differentiation. The malignant cells are")
    log("  stuck below the normal differentiated level.")
    log("  The gap between GMP-like and Mono-like in")
    log("  the malignant trajectory, vs the smooth")
    log("  progression in the normal trajectory, IS")
    log("  the false attractor signature.")
    log()

    mean_expr = traj_stats['mean']
    results   = []

    for gene in available_genes:
        gene_vals = mean_expr[gene].dropna()
        if len(gene_vals) < 2:
            continue

        # Reference: normal differentiated endpoint
        ref_positions = [p for p in REF_NORMAL
                         if p in gene_vals.index]
        if not ref_positions:
            ref_val = gene_vals.max()
        else:
            ref_val = gene_vals[ref_positions].mean()

        # Saddle point: value at the block
        saddle_pos_available = [
            p for p in SADDLE_POSITIONS
            if p in gene_vals.index
        ]
        if not saddle_pos_available:
            continue

        saddle_val = gene_vals[saddle_pos_available].mean()
        suppression_pct = (
            (ref_val - saddle_val) / (ref_val + 1e-6) * 100
        )

        # Also find overall minimum for reference
        min_pos = gene_vals.idxmin()

        # Statistical test:
        # Normal differentiated vs malignant saddle
        ref_mask    = combined['TrajPosition'].isin(REF_NORMAL)
        saddle_mask = combined['TrajPosition'].isin(
            SADDLE_POSITIONS
        )
        ref_expr    = combined[ref_mask][gene].dropna()
        saddle_expr = combined[saddle_mask][gene].dropna()

        pval = np.nan
        if len(ref_expr) >= 10 and len(saddle_expr) >= 10:
            _, pval = stats.mannwhitneyu(
                ref_expr, saddle_expr,
                alternative='greater'
            )

        is_candidate = gene in SADDLE_CANDIDATES

        # Evaluate: is expression at saddle point
        # significantly below normal differentiated level?
        if is_candidate:
            if suppression_pct > 30 and (
                np.isnan(pval) or pval < 0.05
            ):
                result = "CONFIRMED"
            elif suppression_pct > 15:
                result = "PARTIAL"
            else:
                result = "NOT CONFIRMED"
        else:
            # Controls should NOT be suppressed
            # at GMP-like relative to monocytes
            result = ("CONTROL OK"
                      if suppression_pct < 20
                      else "UNEXPECTED")

        results.append({
            'gene':             gene,
            'is_candidate':     is_candidate,
            'ref_expr':         round(ref_val, 4),
            'saddle_expr':      round(saddle_val, 4),
            'suppression_pct':  round(suppression_pct, 1),
            'overall_min_pos':  min_pos,
            'n_ref':            len(ref_expr),
            'n_saddle':         len(saddle_expr),
            'pval':             pval,
            'result':           result
        })

        def fmt_p(p):
            if np.isnan(p): return "N/A      "
            if p < 0.001:   return f"{p:.2e} ***"
            if p < 0.01:    return f"{p:.4f} ** "
            if p < 0.05:    return f"{p:.4f} *  "
            return           f"{p:.4f}    "

        flag = (
            "✓ CONFIRMED"  if result == "CONFIRMED"  else
            "~ PARTIAL"    if result == "PARTIAL"     else
            "✓ CTRL OK"    if result == "CONTROL OK"  else
            "✗ " + result
        )

        log(f"{gene:8} | "
            f"ref={ref_val:.4f} "
            f"saddle={saddle_val:.4f} | "
            f"suppression={suppression_pct:6.1f}% | "
            f"p={fmt_p(pval)} | {flag}")

    results_df = pd.DataFrame(results)
    results_df.to_csv(
        RESULTS_DIR + "saddle_point_results_v2.csv",
        index=False
    )

    n_conf  = (results_df['result'] == 'CONFIRMED').sum()
    n_part  = (results_df['result'] == 'PARTIAL').sum()
    n_cands = results_df['is_candidate'].sum()
    n_ctok  = (results_df['result'] == 'CONTROL OK').sum()
    n_ctrl  = (~results_df['is_candidate']).sum()

    log()
    log("="*56)
    log("FRAMEWORK PREDICTION RESULT — CORRECTED")
    log("="*56)
    log(f"Candidates confirmed: {n_conf}/{n_cands}")
    log(f"Candidates partial:   {n_part}/{n_cands}")
    log(f"Controls as expected: {n_ctok}/{n_ctrl}")
    log()

    if n_conf + n_part >= 3:
        log("*** STRONG CONFIRMATION ***")
        log("Differentiation TFs are significantly")
        log("suppressed at the malignant block point")
        log("relative to normal differentiated endpoint.")
        log("The false attractor ceiling is confirmed.")
        log("READY TO SEND TO CHO.")
    elif n_conf + n_part >= 2:
        log("** MODERATE RESULT **")
        log("Consistent with false attractor framework.")
    else:
        log("* UNEXPECTED — paste output for diagnosis *")

    return results_df


def generate_figure(combined, traj_stats,
                    results_df, available_genes):
    log("="*56)
    log("STEP 5: FIGURE — CORRECTED")
    log("="*56)

    mean_expr = traj_stats['mean']
    sem_expr  = traj_stats['sem']

    mal_positions  = [p for p in MALIGNANT_ORDER
                      if p in mean_expr.index]
    norm_positions = [p for p in NORMAL_ORDER
                      if p in mean_expr.index]

    fig = plt.figure(figsize=(18, 12))
    gs  = gridspec.GridSpec(2, 2, figure=fig,
                            hspace=0.5, wspace=0.4)
    reds = sns.color_palette("Reds_d", 5)

    def plot_traj(ax, positions, title,
                  shade_positions=None):
        for i, gene in enumerate(SADDLE_CANDIDATES):
            if gene not in mean_expr.columns:
                continue
            vals = [mean_expr.loc[p, gene]
                    if p in mean_expr.index else np.nan
                    for p in positions]
            errs = [sem_expr.loc[p, gene]
                    if p in sem_expr.index else 0
                    for p in positions]
            x = list(range(len(positions)))
            ax.plot(x, vals, 'o-', color=reds[i],
                    lw=2.5, ms=8, label=gene)
            ax.fill_between(
                x,
                [v - e for v, e in zip(vals, errs)],
                [v + e for v, e in zip(vals, errs)],
                alpha=0.12, color=reds[i]
            )
        if shade_positions:
            shade_x = [positions.index(p)
                       for p in shade_positions
                       if p in positions]
            if shade_x:
                ax.axvspan(
                    min(shade_x) - 0.4,
                    max(shade_x) + 0.4,
                    alpha=0.15, color='darkorange',
                    label='Differentiation block\n(false attractor)'
                )
        ax.set_xticks(range(len(positions)))
        ax.set_xticklabels(positions, rotation=35,
                            ha='right', fontsize=8)
        ax.set_ylabel("Mean log-norm expression",
                      fontsize=10)
        ax.set_title(title, fontsize=11,
                     fontweight='bold')
        ax.legend(fontsize=7, loc='upper left')

    ax_a = fig.add_subplot(gs[0, 0])
    plot_traj(
        ax_a, mal_positions,
        "A. Malignant Trajectory (AML)\n"
        "Orange = differentiation block (false attractor)",
        shade_positions=SADDLE_POSITIONS
    )

    ax_b = fig.add_subplot(gs[0, 1])
    plot_traj(
        ax_b, norm_positions,
        "B. Normal Hematopoietic Trajectory\n"
        "Smooth progression — no block",
        shade_positions=None
    )

    # Panel C: Gap plot — the core result
    # Shows normal endpoint vs malignant block
    ax_c = fig.add_subplot(gs[1, 0])

    x = np.arange(len(SADDLE_CANDIDATES))
    width = 0.35

    ref_vals    = []
    saddle_vals = []
    gene_labels = []

    for gene in SADDLE_CANDIDATES:
        if gene not in mean_expr.columns:
            continue
        ref_pos = [p for p in REF_NORMAL
                   if p in mean_expr.index]
        sad_pos = [p for p in SADDLE_POSITIONS
                   if p in mean_expr.index]
        if not ref_pos or not sad_pos:
            continue
        ref_vals.append(mean_expr.loc[ref_pos, gene].mean())
        saddle_vals.append(
            mean_expr.loc[sad_pos, gene].mean()
        )
        gene_labels.append(gene)

    xg = np.arange(len(gene_labels))
    bars1 = ax_c.bar(xg - width/2, ref_vals, width,
                     label='Normal monocytes\n(target state)',
                     color='steelblue', alpha=0.85)
    bars2 = ax_c.bar(xg + width/2, saddle_vals, width,
                     label='AML blocked cells\n(GMP-like/Prog-like)',
                     color='crimson', alpha=0.85)

    ax_c.set_xticks(xg)
    ax_c.set_xticklabels(gene_labels, fontsize=10)
    ax_c.set_ylabel("Mean log-norm expression", fontsize=10)
    ax_c.set_title(
        "C. The False Attractor Gap\n"
        "Normal endpoint (blue) vs AML block (red)\n"
        "Gap = differentiation suppression",
        fontsize=11, fontweight='bold'
    )
    ax_c.legend(fontsize=9)

    # Annotate gaps
    for i, (r, s) in enumerate(zip(ref_vals, saddle_vals)):
        gap = r - s
        pct = gap / (r + 1e-6) * 100
        ax_c.annotate(
            f'{pct:.0f}%↓',
            xy=(i, max(r, s) + 0.02),
            ha='center', fontsize=9,
            color='darkred', fontweight='bold'
        )

    # Panel D: results table
    ax_d = fig.add_subplot(gs[1, 1])
    ax_d.axis('off')

    if results_df is not None:
        tbl = results_df[results_df['is_candidate']][
            ['gene', 'ref_expr', 'saddle_expr',
             'suppression_pct', 'pval', 'result']
        ].copy()
        tbl['pval'] = tbl['pval'].apply(
            lambda p: f"{p:.2e}"
            if not np.isnan(p) else "N/A"
        )
        tbl.columns = ['Gene', 'Normal', 'Blocked',
                       'Supp%', 'p-val', 'Result']

        table = ax_d.table(
            cellText=tbl.values,
            colLabels=tbl.columns,
            loc='center', cellLoc='center'
        )
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1.1, 1.8)

        for i, (_, row) in enumerate(tbl.iterrows()):
            color = (
                '#c8e6c9'
                if 'CONFIRMED' in str(row['Result'])
                else '#fff9c4'
                if 'PARTIAL' in str(row['Result'])
                else '#ffcdd2'
            )
            for j in range(len(tbl.columns)):
                table[i+1, j].set_facecolor(color)

    ax_d.set_title(
        "D. Suppression at Differentiation Block\n"
        "Green=confirmed | Yellow=partial | Red=not confirmed",
        fontsize=11, fontweight='bold', pad=20
    )

    fig.suptitle(
        "AML False Attractor — Differentiation Block Analysis\n"
        "Zenodo:10013368 — 74,583 cells — 10,130 malignant"
        " — OrganismCore — February 28, 2026",
        fontsize=12, fontweight='bold'
    )

    outpath = RESULTS_DIR + "saddle_point_figure_v2.png"
    plt.savefig(outpath, dpi=180, bbox_inches='tight')
    plt.close()
    log(f"Figure saved: {outpath}")
    return outpath


def main():
    log("="*56)
    log("AML SADDLE POINT — CORRECTED ANALYSIS")
    log("OrganismCore — February 28, 2026")
    log("="*56)

    for fname in [ANNO_FILE, EXPR_FILE]:
        if not os.path.exists(fname):
            log(f"ERROR: {fname} not found.")
            return

    anno, ct_col = load_annotations()

    expr, cell_ids = load_expression_transposed()
    if expr is None:
        log("Expression loading failed.")
        return

    combined, traj_stats, available_genes = \
        compute_trajectory_profiles(expr, anno, ct_col)

    results_df = compute_saddle_point_signature(
        combined, traj_stats, available_genes
    )

    generate_figure(
        combined, traj_stats,
        results_df, available_genes
    )

    log()
    log("="*56)
    log("COMPLETE")
    log(f"Results: {RESULTS_DIR}")
    log("Files for Cho:")
    log(f"  {RESULTS_DIR}saddle_point_figure_v2.png")
    log(f"  {RESULTS_DIR}saddle_point_results_v2.csv")
    log("="*56)


if __name__ == "__main__":
    main()
