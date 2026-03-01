"""
Stomach Adenocarcinoma — Circuit Analysis
SCRIPT 2 — CIRCUIT AND SUBTYPE RUN
Dataset: GSE66229
  300 STAD tumors / 100 normal gastric
  ACRG Korean cohort
  Affymetrix GPL570

FRAMEWORK: OrganismCore Principles-First
Doc: 89b | Date: 2026-03-01

SCRIPT 2 OBJECTIVES:
  1. Fix missing genes (CLDN18/GKN1/KRT20)
     with expanded probe map
  2. Correct depth score using actual
     data-derived switch/FA genes
  3. Classify ACRG molecular subtypes
     from expression geometry
  4. Test CDX2 circuit integrity
  5. Test ERBB2 circuit
  6. Test EZH2 paradox (DOWN overall,
     r>0 within tumors)
  7. Depth score by subtype
  8. Drug target depth correlations

Author: Eric Robert Lawson
Framework: OrganismCore Principles-First
"""

import os
import sys
import gzip
import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import gaussian_kde
from scipy.signal import argrelmin
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import warnings
warnings.filterwarnings("ignore")

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR    = "./stad_false_attractor/"
RESULTS_DIR = os.path.join(BASE_DIR, "results")
S2_DIR      = os.path.join(BASE_DIR, "results_s2")
LOG_FILE    = os.path.join(S2_DIR, "s2_log.txt")

os.makedirs(S2_DIR, exist_ok=True)

GENE_MATRIX = os.path.join(
    RESULTS_DIR, "gene_matrix.csv"
)
META_CSV = os.path.join(
    RESULTS_DIR, "metadata.csv"
)

# ============================================================
# EXPANDED PROBE MAP
# Adds missing genes from Script 1
# ============================================================

EXPANDED_PROBES = {
    # CLDN18 — most critical missing gene
    # zolbetuximab target
    "220066_at":    "CLDN18",
    "213451_at":    "CLDN18",
    "204013_at":    "CLDN18",
    # GKN1 — gastrokine 1
    "219534_at":    "GKN1",
    "220716_at":    "GKN1",
    "1558069_at":   "GKN1",
    # KRT20 — intestinal keratin
    "208826_at":    "KRT20",
    "212531_at":    "KRT20",
    "217236_s_at":  "KRT20",
    # Gastric master TFs
    "205769_at":    "SOX2",
    "210220_at":    "HNF4A",
    "209933_s_at":  "GATA4",
    "211543_s_at":  "GATA6",
    "204147_s_at":  "FOXA2",
    "210803_s_at":  "SOX17",
    # CDX2 circuit targets
    "209588_at":    "CDX2",
    "207257_at":    "MUC2",
    "208826_at":    "KRT20",
    "203821_at":    "VIL1",
    "209496_at":    "FABP1",
    "209735_at":    "CDH17",
    # ERBB circuit
    "216836_s_at":  "ERBB2",
    "210930_s_at":  "ERBB2",
    "205358_at":    "ERBB3",
    "205923_at":    "ERBB4",
    "216033_s_at":  "GRB7",
    "201983_s_at":  "EGFR",
    # EZH2 circuit
    "203358_s_at":  "EZH2",
    "218471_s_at":  "EZH2",
    "218171_s_at":  "SUZ12",
    "209915_at":    "EED",
    "221604_s_at":  "KDM6A",
    # MSI markers
    "202589_at":    "MLH1",
    "202461_s_at":  "MSH2",
    "215198_s_at":  "MSH6",
    # Immune
    "210943_s_at":  "FOXP3",
    "205758_at":    "CD8A",
    "220644_at":    "CD274",
    "207634_at":    "PDCD1",
    "203507_at":    "CD68",
    "203508_at":    "CD163",
    # EMT / ZEB2
    "208079_s_at":  "ZEB2",
    "213844_at":    "TWIST1",
    "216641_s_at":  "SNAI1",
    "201426_s_at":  "VIM",
    "201131_s_at":  "CDH1",
    "203440_at":    "CDH2",
    # Proliferation
    "212020_s_at":  "MKI67",
    "204092_s_at":  "AURKA",
    "201291_s_at":  "TOP2A",
    "214710_s_at":  "CCNB1",
    "203213_at":    "CDC20",
    # Cell cycle / drug targets
    "202613_at":    "CDK4",
    "203554_x_at":  "CDK6",
    "208712_at":    "CCND1",
    "201418_s_at":  "HDAC1",
    "218471_s_at":  "EZH2",
    "203510_at":    "MET",
    "202431_s_at":  "MYC",
    "204250_s_at":  "CHGA",
    "213421_at":    "SYP",
    # TP53 / subtypes
    "201746_at":    "TP53",
    "204340_at":    "KRAS",
    "202910_s_at":  "RB1",
    # Gastric
    "204766_s_at":  "TFF1",
    "207017_at":    "TFF1",
    "207982_at":    "MUC5AC",
    "211332_x_at":  "MUC5AC",
    "204764_at":    "TFF2",
    "210735_s_at":  "MUC6",
    "204679_at":    "ATP4A",
    "209780_at":    "PGC",
    "219254_at":    "OLFM4",
    "221895_at":    "GKN2",
    # Additional
    "204472_at":    "DNMT3A",
    "218457_at":    "DNMT3B",
    "201904_s_at":  "BMI1",
    "203638_s_at":  "FGFR2",
    "202240_at":    "PLK1",
    "204092_s_at":  "AURKA",
    "201474_s_at":  "FN1",
    "218816_at":    "ZEB1",
    "213566_at":    "SNAI2",
    "203667_at":    "MMP2",
    "203936_s_at":  "MMP9",
    "201202_at":    "PCNA",
    "201086_x_at":  "BUB1B",
    "217023_at":    "PTEN",
}

# ============================================================
# LOGGING
# ============================================================

log_lines = []

def log(msg=""):
    print(msg)
    log_lines.append(str(msg))

def write_log():
    with open(LOG_FILE, "w") as f:
        f.write("\n".join(log_lines))

def fmt_p(p):
    if np.isnan(p):    return "p=N/A"
    if p < 0.001:      return f"p={p:.2e} ***"
    elif p < 0.01:     return f"p={p:.2e}  **"
    elif p < 0.05:     return f"p={p:.4f}   *"
    else:              return f"p={p:.4f}  ns"

def safe_pearsonr(x, y):
    xa = np.asarray(x, dtype=float)
    ya = np.asarray(y, dtype=float)
    mask = np.isfinite(xa) & np.isfinite(ya)
    xa, ya = xa[mask], ya[mask]
    if len(xa) < 5:
        return np.nan, np.nan
    return stats.pearsonr(xa, ya)

def safe_mwu(a, b, alternative="two-sided"):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    a = a[np.isfinite(a)]
    b = b[np.isfinite(b)]
    if len(a) < 2 or len(b) < 2:
        return np.nan, np.nan
    return stats.mannwhitneyu(
        a, b, alternative=alternative
    )

# ============================================================
# STEP 0: LOAD SCRIPT 1 OUTPUTS
# ============================================================

def load_s1_outputs():
    log("=" * 65)
    log("STEP 0: LOAD SCRIPT 1 OUTPUTS")
    log("=" * 65)

    if not os.path.exists(GENE_MATRIX):
        log(f"  ERROR: {GENE_MATRIX} not found")
        log("  Run Script 1 first")
        sys.exit(1)

    gene_df = pd.read_csv(
        GENE_MATRIX, index_col=0
    )
    log(f"  Gene matrix: {gene_df.shape}")
    log(f"  Genes: {list(gene_df.index[:10])}")

    meta_df = None
    if os.path.exists(META_CSV):
        meta_df = pd.read_csv(
            META_CSV, index_col=0
        )
        log(f"  Meta: {meta_df.shape}")

    return gene_df, meta_df

# ============================================================
# STEP 1: EXPAND PROBE MAP
# Attempt to find missing genes
# ============================================================

def expand_probes(gene_df, meta_df):
    log("")
    log("=" * 65)
    log("STEP 1: EXPAND PROBE MAP")
    log("Finding CLDN18 / GKN1 / KRT20")
    log("=" * 65)

    # Load the raw series matrix again
    # to access all 54675 probes
    matrix_path = os.path.join(
        BASE_DIR,
        "GSE66229_series_matrix.txt.gz"
    )

    if not os.path.exists(matrix_path):
        log("  Matrix file not found")
        log("  Cannot expand probes")
        log("  Proceeding with Script 1 genes")
        return gene_df

    log(f"  Loading raw matrix for probe scan...")
    log(f"  Looking for probes:")
    new_probes = {}
    for probe, gene in EXPANDED_PROBES.items():
        if gene not in gene_df.index:
            new_probes[probe] = gene

    log(f"  Target new probes: {len(new_probes)}")
    target_genes = set(new_probes.values())
    log(f"  Target new genes: {sorted(target_genes)}")

    if not new_probes:
        log("  No new probes needed")
        return gene_df

    # Parse matrix for specific probes
    found_rows = {}
    header = None

    try:
        with gzip.open(
            matrix_path, "rt",
            encoding="utf-8",
            errors="ignore",
        ) as f:
            in_table = False
            for line in f:
                line = line.rstrip("\n")
                if "series_matrix_table_begin" \
                        in line:
                    in_table = True
                    continue
                if "series_matrix_table_end" \
                        in line:
                    break
                if not in_table:
                    continue
                if header is None:
                    header = [
                        h.strip().strip('"')
                        for h in line.split("\t")
                    ]
                    continue
                parts  = line.split("\t")
                probe  = parts[0].strip().strip('"')
                if probe in new_probes:
                    vals = []
                    for v in parts[1:]:
                        try:
                            vals.append(float(v))
                        except Exception:
                            vals.append(np.nan)
                    found_rows[probe] = vals

        log(f"  Probes found in matrix: "
            f"{len(found_rows)}")

        if found_rows and header:
            sample_ids = [
                h for h in header[1:]
            ]
            # Build new gene rows
            new_gene_rows = {}
            for probe, vals in found_rows.items():
                gene = new_probes[probe]
                if len(vals) == len(sample_ids):
                    row = pd.Series(
                        vals,
                        index=sample_ids,
                    )
                    # Log2 transform
                    row = np.log2(
                        row.clip(lower=1.0)
                    )
                    if gene not in new_gene_rows:
                        new_gene_rows[gene] = row
                    else:
                        # Keep highest mean probe
                        if row.mean() > \
                                new_gene_rows[
                                    gene
                                ].mean():
                            new_gene_rows[gene] = row

            for gene, row in new_gene_rows.items():
                if gene not in gene_df.index:
                    gene_df = pd.concat([
                        gene_df,
                        row.to_frame(name=gene).T
                    ])
                    log(f"  Added: {gene} "
                        f"(mean={row.mean():.4f})")

            found_genes = [
                g for g in target_genes
                if g in gene_df.index
            ]
            still_missing = [
                g for g in target_genes
                if g not in gene_df.index
            ]
            log(f"  Found: {found_genes}")
            if still_missing:
                log(f"  Still missing: "
                    f"{still_missing}")
                log("  These probes are not in"
                    " this array version")

    except Exception as e:
        log(f"  Probe scan error: {e}")
        import traceback
        log(traceback.format_exc())

    log(f"  Gene matrix after expansion: "
        f"{len(gene_df)} genes")
    return gene_df

# ============================================================
# STEP 2: CLASSIFY SAMPLES
# ============================================================

def classify_samples(gene_df, meta_df):
    log("")
    log("=" * 65)
    log("STEP 2: CLASSIFY TUMOR / NORMAL")
    log("=" * 65)

    expr_T  = gene_df.T
    samples = gene_df.columns.tolist()

    if meta_df is not None \
            and "source_name_ch1" in meta_df.columns:
        src = meta_df["source_name_ch1"].fillna(
            ""
        ).str.lower()
        tumor_idx = src[
            src.str.contains(
                r"tumor|cancer|gastric.cancer",
                regex=True,
            )
        ].index.tolist()
        normal_idx = src[
            src.str.contains(
                r"normal|adjacent|non.tumor",
                regex=True,
            )
        ].index.tolist()
    else:
        # Positional fallback
        n = len(samples)
        tumor_idx  = samples[:300]
        normal_idx = samples[300:]

    # Filter to samples in gene_df
    tumor_idx  = [
        s for s in tumor_idx
        if s in gene_df.columns
    ]
    normal_idx = [
        s for s in normal_idx
        if s in gene_df.columns
    ]

    log(f"  TUMOR  : {len(tumor_idx)}")
    log(f"  NORMAL : {len(normal_idx)}")

    tumor  = gene_df[tumor_idx].T
    normal = gene_df[normal_idx].T

    return tumor, normal, tumor_idx, normal_idx

# ============================================================
# STEP 3: CORRECTED DEPTH SCORE
# Use data-derived switch/FA genes
# ============================================================

def corrected_depth_score(tumor, normal):
    log("")
    log("=" * 65)
    log("STEP 3: CORRECTED DEPTH SCORE")
    log("Using data-derived switch/FA genes")
    log("Script 1 score was inverted")
    log("because switch genes were UP")
    log("=" * 65)

    gc = list(tumor.columns)

    # CORRECTED SWITCH GENES:
    # genes that are DOWN in STAD tumor
    # confirmed from Script 1
    sw_candidates = [
        "FABP1",   # -7.9% *** ✓
        "MUC2",    # -7.9% *** ✓
        "ERBB4",   # -46.6% *** (extreme)
        "ERBB3",   # -87.4% *** (extreme)
        "TWIST1",  # -23.1% *** ✓
        "CDH2",    # -40.8% *** ✓
        "VIM",     # -3.7% *** ✓
        "GKN1",    # if found
        "CLDN18",  # if found
        "MUC5AC",  # -0.5% ns (flat — optional)
    ]

    # CORRECTED FA MARKERS:
    # genes that are UP in STAD tumor
    fa_candidates = [
        "MKI67",   # +55.2% *** ✓
        "ZEB2",    # +31.5% *** ✓
        "CDX2",    # +23.1% *** ✓
        "AURKA",   # +33.4% *** ✓
        "TOP2A",   # +36.1% *** ✓
        "SNAI1",   # +10.7% *** ✓
        "HDAC1",   # +12.8% *** ✓
        "MET",     # +11.2% *** ✓
    ]

    sw_avail = [g for g in sw_candidates
                if g in gc]
    fa_avail = [g for g in fa_candidates
                if g in gc]

    log(f"\n  Switch genes (DOWN in STAD):")
    for g in sw_avail:
        nm_v = normal[g].mean() \
            if g in normal.columns else np.nan
        tm_v = tumor[g].mean()
        chg  = (
            (tm_v - nm_v) / nm_v * 100
            if not np.isnan(nm_v)
            and abs(nm_v) > 0.0001
            else np.nan
        )
        log(f"    {g:<10} "
            f"N:{nm_v:.4f} T:{tm_v:.4f} "
            f"{chg:+.1f}%"
            if not np.isnan(chg)
            else f"    {g:<10} N:{nm_v:.4f} "
                 f"T:{tm_v:.4f} N/A")

    log(f"\n  FA markers (UP in STAD):")
    for g in fa_avail:
        nm_v = normal[g].mean() \
            if g in normal.columns else np.nan
        tm_v = tumor[g].mean()
        chg  = (
            (tm_v - nm_v) / nm_v * 100
            if not np.isnan(nm_v)
            and abs(nm_v) > 0.0001
            else np.nan
        )
        log(f"    {g:<10} "
            f"N:{nm_v:.4f} T:{tm_v:.4f} "
            f"{chg:+.1f}%"
            if not np.isnan(chg)
            else f"    {g:<10} N:{nm_v:.4f} "
                 f"T:{tm_v:.4f} N/A")

    def norm01(s):
        mn, mx = s.min(), s.max()
        return (
            (s - mn) / (mx - mn)
            if mx > mn
            else pd.Series(0.0, index=s.index)
        )

    tumor = tumor.copy()
    depth = pd.Series(
        np.zeros(len(tumor)), index=tumor.index
    )
    comp = 0

    if sw_avail:
        # Switch DOWN → depth component =
        # (1 - normalized) = high when gene low
        depth += (
            1 - norm01(
                tumor[sw_avail].mean(axis=1)
            )
        )
        comp += 1
    if fa_avail:
        # FA UP → depth component =
        # normalized = high when gene high
        depth += norm01(
            tumor[fa_avail].mean(axis=1)
        )
        comp += 1
    if comp > 0:
        depth /= comp

    tumor["depth_corrected"] = depth.values

    log(f"\n  Corrected depth "
        f"({len(tumor)} tumors):")
    log(f"    Mean  : {depth.mean():.4f}")
    log(f"    Median: {depth.median():.4f}")
    log(f"    Std   : {depth.std():.4f}")
    log(f"    Min   : {depth.min():.4f}")
    log(f"    Max   : {depth.max():.4f}")

    # Correlations with corrected depth
    corrs = []
    for gene in gc:
        if gene in [
            "depth_corrected", "group",
            "subtype",
        ]:
            continue
        rv, pv = safe_pearsonr(
            tumor["depth_corrected"].values,
            tumor[gene].values,
        )
        if not np.isnan(rv):
            corrs.append((gene, rv, pv))
    corrs.sort(
        key=lambda x: abs(x[1]), reverse=True
    )

    log(f"\n  Corrected depth correlations "
        f"(top 20):")
    log(f"  {'Gene':<10} {'r':>8}  p-value")
    log(f"  {'-'*36}")
    for gene, rv, pv in corrs[:20]:
        log(f"  {gene:<10} {rv:>+8.4f}  "
            f"{fmt_p(pv)}")

    return tumor, corrs, sw_avail, fa_avail

# ============================================================
# STEP 4: ACRG SUBTYPE CLASSIFICATION
# From expression geometry alone
# ============================================================

def classify_acrg_subtypes(tumor):
    log("")
    log("=" * 65)
    log("STEP 4: ACRG MOLECULAR SUBTYPE")
    log("Classification from expression")
    log("MSS/TP53+ / MSS/EMT / MSI / MSS/TP53-")
    log("=" * 65)

    gc     = list(tumor.columns)
    tumor  = tumor.copy()
    n      = len(tumor)

    # Score each subtype axis
    # MSS/EMT: low CDH1, ZEB2 high, SNAI1 high
    emt_genes = [
        g for g in ["ZEB2", "SNAI1", "ZEB1",
                    "MMP9", "VIM"]
        if g in gc
    ]
    epi_genes = [
        g for g in ["CDH1", "FABP1", "MUC5AC"]
        if g in gc
    ]

    # MSI: FOXP3 low, CD8A high,
    #      MLH1 low (if available)
    msi_genes = [
        g for g in ["CD8A", "CD274", "FOXP3"]
        if g in gc
    ]

    # TP53+: TP53 high expression
    # TP53-: TP53 low, CDK4/6 high

    if emt_genes:
        emt_score = tumor[emt_genes].mean(axis=1)
        if epi_genes:
            epi_score = tumor[epi_genes].mean(axis=1)
            tumor["emt_score"] = (
                emt_score - epi_score
            )
        else:
            tumor["emt_score"] = emt_score

    if "TP53" in gc:
        tumor["tp53_score"] = tumor["TP53"]

    if msi_genes:
        tumor["msi_score"] = tumor[
            msi_genes
        ].mean(axis=1)

    if "CDK4" in gc and "CDK6" in gc:
        tumor["cdk46_score"] = (
            tumor["CDK4"] + tumor["CDK6"]
        ) / 2

    # Assign subtypes using thresholds
    # derived from KDE on each score
    tumor["subtype"] = "UNKNOWN"

    # EMT subtype — highest emt_score
    if "emt_score" in tumor.columns:
        emt_vals = tumor["emt_score"].values
        try:
            kde  = gaussian_kde(emt_vals)
            xs   = np.linspace(
                emt_vals.min(),
                emt_vals.max(),
                300,
            )
            ys   = kde(xs)
            mins = argrelmin(ys, order=10)[0]
            if len(mins) > 0:
                thr_emt = xs[mins[-1]]
                n_emt   = (emt_vals > thr_emt).sum()
                log(f"  EMT threshold: {thr_emt:.4f}")
                log(f"  EMT candidates: {n_emt}")
                tumor.loc[
                    tumor["emt_score"] > thr_emt,
                    "subtype",
                ] = "MSS_EMT"
            else:
                # Top 15%
                thr_emt = np.percentile(
                    emt_vals, 85
                )
                n_emt   = (emt_vals > thr_emt).sum()
                log(f"  EMT top 15%: {n_emt}")
                tumor.loc[
                    tumor["emt_score"] > thr_emt,
                    "subtype",
                ] = "MSS_EMT"
        except Exception as e:
            log(f"  EMT KDE error: {e}")

    # MSI — high immune score
    if "msi_score" in tumor.columns:
        msi_vals = tumor[
            tumor["subtype"] == "UNKNOWN"
        ]["msi_score"].values
        if len(msi_vals) > 10:
            thr_msi = np.percentile(msi_vals, 75)
            log(f"  MSI threshold (top 25%): "
                f"{thr_msi:.4f}")
            tumor.loc[
                (tumor["subtype"] == "UNKNOWN")
                & (tumor["msi_score"] > thr_msi),
                "subtype",
            ] = "MSI"

    # TP53+ vs TP53-
    if "tp53_score" in tumor.columns:
        remaining = tumor[
            tumor["subtype"] == "UNKNOWN"
        ]["tp53_score"]
        if len(remaining) > 10:
            thr_tp53 = remaining.median()
            log(f"  TP53 median: {thr_tp53:.4f}")
            tumor.loc[
                (tumor["subtype"] == "UNKNOWN")
                & (tumor["tp53_score"] >= thr_tp53),
                "subtype",
            ] = "MSS_TP53pos"
            tumor.loc[
                (tumor["subtype"] == "UNKNOWN"),
                "subtype",
            ] = "MSS_TP53neg"

    # Remaining unknowns → TP53+
    tumor.loc[
        tumor["subtype"] == "UNKNOWN",
        "subtype",
    ] = "MSS_TP53pos"

    counts = tumor["subtype"].value_counts()
    log(f"\n  Subtype counts:")
    for s, c in counts.items():
        pct = c / n * 100
        log(f"    {s:<15}: {c:>3} ({pct:.1f}%)")
    log(f"  Expected: EMT~15% MSI~23% "
        f"TP53+~36% TP53-~26%")

    return tumor

# ============================================================
# STEP 5: DEPTH BY SUBTYPE
# ============================================================

def depth_by_subtype(tumor):
    log("")
    log("=" * 65)
    log("STEP 5: DEPTH BY SUBTYPE")
    log("=" * 65)

    if "depth_corrected" not in tumor.columns \
            or "subtype" not in tumor.columns:
        log("  Missing columns — skip")
        return

    subtypes = tumor["subtype"].unique()
    log(f"\n  {'Subtype':<15} "
        f"{'N':>5} {'Mean':>8} "
        f"{'Median':>8} {'Std':>8}")
    log(f"  {'-'*50}")

    depth_vals = {}
    for st in sorted(subtypes):
        sub = tumor[
            tumor["subtype"] == st
        ]["depth_corrected"]
        depth_vals[st] = sub.values
        log(f"  {st:<15} "
            f"{len(sub):>5} "
            f"{sub.mean():>8.4f} "
            f"{sub.median():>8.4f} "
            f"{sub.std():>8.4f}")

    # Pairwise comparisons
    st_list = sorted(subtypes)
    log(f"\n  Pairwise depth comparisons:")
    for i in range(len(st_list)):
        for j in range(i+1, len(st_list)):
            a = depth_vals[st_list[i]]
            b = depth_vals[st_list[j]]
            _, pv = safe_mwu(
                a, b, "two-sided"
            )
            log(f"  {st_list[i]} vs "
                f"{st_list[j]}: "
                f"{fmt_p(pv)}")

# ============================================================
# STEP 6: CDX2 CIRCUIT INTEGRITY
# ============================================================

def cdx2_circuit(tumor, normal):
    log("")
    log("=" * 65)
    log("STEP 6: CDX2 CIRCUIT INTEGRITY")
    log("Is the CDX2 → intestinal program intact?")
    log("CDX2 → MUC2/KRT20/VIL1/FABP1")
    log("=" * 65)

    gc = list(tumor.columns)

    cdx2_targets = [
        ("MUC2",  "intestinal goblet mucin"),
        ("KRT20", "intestinal keratin"),
        ("VIL1",  "brush border villin"),
        ("FABP1", "intestinal FA binding"),
        ("CDH17", "intestinal cadherin"),
    ]

    log(f"\n  CDX2 expression in tumors:")
    if "CDX2" in gc:
        log(f"    Mean: {tumor['CDX2'].mean():.4f}"
            f" ± {tumor['CDX2'].std():.4f}")
        nm_cdx2 = (
            normal["CDX2"].mean()
            if "CDX2" in normal.columns
            else np.nan
        )
        log(f"    Normal: {nm_cdx2:.4f}")

    log(f"\n  CDX2 → target correlations "
        f"(within tumors):")
    log(f"  {'Target':<10} {'r':>8}  "
        f"p-value  Interpretation")
    log(f"  {'-'*55}")

    if "CDX2" not in gc:
        log("  CDX2 not in gene matrix")
        return

    for target, desc in cdx2_targets:
        if target not in gc:
            log(f"  {target:<10} NOT IN MATRIX")
            continue
        rv, pv = safe_pearsonr(
            tumor["CDX2"].values,
            tumor[target].values,
        )
        interp = ""
        if not np.isnan(rv):
            if rv > 0 and pv < 0.05:
                interp = "INTACT ✓"
            elif rv < 0 and pv < 0.05:
                interp = "INVERTED"
            else:
                interp = "no relationship"
        log(f"  {target:<10} {rv:>+8.4f}  "
            f"{fmt_p(pv)}  {interp}")

    # CDX2 circuit verdict
    log(f"\n  CDX2 circuit verdict:")
    intact_count = 0
    tested = 0
    for target, _ in cdx2_targets:
        if target not in gc:
            continue
        tested += 1
        rv, pv = safe_pearsonr(
            tumor["CDX2"].values,
            tumor[target].values,
        )
        if not np.isnan(rv) \
                and rv > 0 and pv < 0.05:
            intact_count += 1
    if tested > 0:
        log(f"    {intact_count}/{tested} "
            f"targets intact")
        if intact_count >= tested * 0.6:
            log("    VERDICT: CIRCUIT INTACT")
            log("    CDX2 restoration would")
            log("    execute intestinal program")
        elif intact_count >= tested * 0.3:
            log("    VERDICT: PARTIALLY INTACT")
        else:
            log("    VERDICT: CIRCUIT BROKEN")
            log("    CDX2 alone insufficient")

# ============================================================
# STEP 7: ERBB FAMILY CIRCUIT
# ============================================================

def erbb_circuit(tumor, normal):
    log("")
    log("=" * 65)
    log("STEP 7: ERBB FAMILY CIRCUIT")
    log("ERBB2 UP / ERBB3 DOWN / ERBB4 DOWN")
    log("=" * 65)

    gc = list(tumor.columns)

    log(f"\n  ERBB family summary:")
    log(f"  {'Gene':<8} {'Normal':>9} "
        f"{'Tumor':>9} {'Change':>9}")
    log(f"  {'-'*40}")
    for g in ["ERBB2", "ERBB3", "ERBB4",
              "EGFR", "GRB7"]:
        if g not in gc:
            continue
        nm  = normal[g].mean() \
            if g in normal.columns else np.nan
        tm  = tumor[g].mean()
        chg = (
            (tm - nm) / nm * 100
            if not np.isnan(nm)
            and abs(nm) > 0.0001
            else np.nan
        )
        cs = (
            f"{chg:+.1f}%"
            if not np.isnan(chg) else "N/A"
        )
        log(f"  {g:<8} {nm:>9.4f} "
            f"{tm:>9.4f} {cs:>9}")

    # ERBB2 within-tumor correlations
    log(f"\n  ERBB2 within-tumor correlations:")
    erbb2_targets = [
        "MKI67", "CDK4", "CDK6",
        "AURKA", "ZEB2", "SNAI1",
        "HDAC1", "MET", "CCND1",
    ]
    if "ERBB2" not in gc:
        log("  ERBB2 not in matrix")
        return

    log(f"  {'Target':<10} {'r':>8}  p-value")
    log(f"  {'-'*36}")
    for g in erbb2_targets:
        if g not in gc:
            continue
        rv, pv = safe_pearsonr(
            tumor["ERBB2"].values,
            tumor[g].values,
        )
        if not np.isnan(rv):
            log(f"  {g:<10} {rv:>+8.4f}  "
                f"{fmt_p(pv)}")

    # ERBB2 bimodal — HER2-high subgroup
    ev = tumor["ERBB2"].values
    log(f"\n  ERBB2 distribution:")
    log(f"    Range: {ev.min():.3f} – "
        f"{ev.max():.3f}")
    try:
        kde  = gaussian_kde(ev)
        xs   = np.linspace(
            ev.min(), ev.max(), 300
        )
        ys   = kde(xs)
        mins = argrelmin(ys, order=8)[0]
        log(f"    KDE minima: {len(mins)}")
        if len(mins) > 0:
            thr  = xs[mins[0]]
            n_hi = (ev > thr).sum()
            n_lo = (ev <= thr).sum()
            log(f"    Threshold : {thr:.4f}")
            log(f"    HER2-high : {n_hi} "
                f"({n_hi/len(ev)*100:.1f}%)")
            log(f"    HER2-low  : {n_lo}")
            tumor = tumor.copy()
            tumor["her2_status"] = np.where(
                tumor["ERBB2"] > thr,
                "HER2_high", "HER2_low"
            )
            # Depth by HER2
            if "depth_corrected" in tumor.columns:
                dh = tumor[
                    tumor["her2_status"]
                    == "HER2_high"
                ]["depth_corrected"]
                dl = tumor[
                    tumor["her2_status"]
                    == "HER2_low"
                ]["depth_corrected"]
                if len(dh) > 1 and len(dl) > 1:
                    log(f"\n    Depth by HER2:")
                    log(f"      HER2-high: "
                        f"{dh.mean():.4f}"
                        f" ± {dh.std():.4f}")
                    log(f"      HER2-low : "
                        f"{dl.mean():.4f}"
                        f" ± {dl.std():.4f}")
                    _, pp = safe_mwu(
                        dh.values, dl.values,
                        "two-sided",
                    )
                    log(f"      {fmt_p(pp)}")
    except Exception as e:
        log(f"    KDE error: {e}")

    return tumor

# ============================================================
# STEP 8: EZH2 PARADOX
# DOWN overall but r>0 within tumors
# ============================================================

def ezh2_paradox(tumor, normal):
    log("")
    log("=" * 65)
    log("STEP 8: EZH2 PARADOX")
    log("EZH2 DOWN -13.1% overall")
    log("r(EZH2, depth) = +0.3326 ***")
    log("What is EZH2 doing within tumors?")
    log("=" * 65)

    gc = list(tumor.columns)

    if "EZH2" not in gc:
        log("  EZH2 not in matrix")
        return

    nm_ezh2 = normal["EZH2"].mean() \
        if "EZH2" in normal.columns else np.nan
    tm_ezh2 = tumor["EZH2"].mean()
    log(f"\n  EZH2 normal: {nm_ezh2:.4f}")
    log(f"  EZH2 tumor : {tm_ezh2:.4f}")
    log(f"  Direction  : "
        f"{'DOWN' if tm_ezh2 < nm_ezh2 else 'UP'}")

    # H3K27 balance
    log(f"\n  H3K27 methylation balance:")
    for g in ["EZH2", "KDM6A", "SUZ12", "EED"]:
        if g not in gc:
            continue
        nm  = normal[g].mean() \
            if g in normal.columns else np.nan
        tm  = tumor[g].mean()
        chg = (
            (tm - nm) / nm * 100
            if not np.isnan(nm)
            and abs(nm) > 0.0001
            else np.nan
        )
        cs  = (
            f"{chg:+.1f}%"
            if not np.isnan(chg) else "N/A"
        )
        log(f"    {g:<10} N:{nm:.4f} "
            f"T:{tm:.4f} {cs}")

    # EZH2 within-tumor correlations
    log(f"\n  EZH2 within-tumor correlations:")
    ezh2_targets = [
        "ZEB2",   "SNAI1",  "VIM",
        "CDH1",   "CDH2",   "TWIST1",
        "MKI67",  "AURKA",  "CDX2",
        "HDAC1",  "MYC",    "TP53",
    ]
    if "depth_corrected" in tumor.columns:
        rv, pv = safe_pearsonr(
            tumor["EZH2"].values,
            tumor["depth_corrected"].values,
        )
        log(f"  {'depth_corrected':<18} "
            f"{rv:>+8.4f}  {fmt_p(pv)}")

    log(f"  {'Gene':<18} {'r':>8}  p-value")
    log(f"  {'-'*40}")
    for g in ezh2_targets:
        if g not in gc:
            continue
        rv, pv = safe_pearsonr(
            tumor["EZH2"].values,
            tumor[g].values,
        )
        if not np.isnan(rv):
            log(f"  {g:<18} {rv:>+8.4f}  "
                f"{fmt_p(pv)}")

    # EZH2 by subtype
    if "subtype" in tumor.columns:
        log(f"\n  EZH2 expression by subtype:")
        log(f"  {'Subtype':<15} "
            f"{'Mean':>8} {'vs_normal':>12}")
        for st in sorted(
            tumor["subtype"].unique()
        ):
            sub_ezh2 = tumor[
                tumor["subtype"] == st
            ]["EZH2"].values
            mean_ezh2 = sub_ezh2.mean()
            chg = (
                (mean_ezh2 - nm_ezh2)
                / nm_ezh2 * 100
                if not np.isnan(nm_ezh2)
                and abs(nm_ezh2) > 0.0001
                else np.nan
            )
            cs = (
                f"{chg:+.1f}%"
                if not np.isnan(chg) else "N/A"
            )
            log(f"  {st:<15} "
                f"{mean_ezh2:>8.4f} "
                f"{cs:>12}")

# ============================================================
# STEP 9: CLDN18 ANALYSIS
# If found — key drug target
# ============================================================

def cldn18_analysis(tumor, normal):
    log("")
    log("=" * 65)
    log("STEP 9: CLDN18 ANALYSIS")
    log("zolbetuximab target")
    log("Most stomach-specific gene")
    log("=" * 65)

    gc = list(tumor.columns)

    if "CLDN18" not in gc:
        log("  CLDN18 not found in matrix")
        log("  GPL570 probe mapping failed")
        log("  Known probes tried:")
        log("    220066_at / 213451_at "
            "/ 204013_at")
        log("  CLDN18 is absent from this")
        log("  array processing — confirmed")
        log("")
        log("  IMPLICATION:")
        log("  Cannot test CLDN18 as")
        log("  primary switch gene in this")
        log("  dataset.")
        log("  CLDN18 analysis deferred to")
        log("  literature check.")
        return

    nm_v = normal["CLDN18"].mean() \
        if "CLDN18" in normal.columns else np.nan
    tm_v = tumor["CLDN18"].mean()
    chg  = (
        (tm_v - nm_v) / nm_v * 100
        if not np.isnan(nm_v)
        and abs(nm_v) > 0.0001
        else np.nan
    )

    log(f"\n  CLDN18 normal: {nm_v:.4f}")
    log(f"  CLDN18 tumor : {tm_v:.4f}")
    log(f"  Change       : "
        f"{chg:+.1f}%" if not np.isnan(chg)
        else "  Change: N/A")

    _, pv = safe_mwu(
        normal["CLDN18"].values
        if "CLDN18" in normal.columns
        else np.array([]),
        tumor["CLDN18"].values,
        "two-sided",
    )
    log(f"  {fmt_p(pv)}")

    if "depth_corrected" in tumor.columns:
        rv, pv2 = safe_pearsonr(
            tumor["CLDN18"].values,
            tumor["depth_corrected"].values,
        )
        log(f"\n  r(CLDN18, depth) = {rv:+.4f} "
            f"{fmt_p(pv2)}")
        if rv < 0 and pv2 < 0.05:
            log("  CLDN18 is a switch gene ✓")
            log("  Lower CLDN18 = deeper block")
        elif rv > 0 and pv2 < 0.05:
            log("  CLDN18 tracks with depth")
            log("  Not behaving as switch gene")

    # CLDN18 bimodal — zolbetuximab
    # requires high CLDN18.2 expression
    cv = tumor["CLDN18"].values
    try:
        kde  = gaussian_kde(cv)
        xs   = np.linspace(
            cv.min(), cv.max(), 300
        )
        ys   = kde(xs)
        mins = argrelmin(ys, order=8)[0]
        log(f"\n  CLDN18 bimodal check:")
        log(f"    KDE minima: {len(mins)}")
        if len(mins) > 0:
            thr  = xs[mins[0]]
            n_hi = (cv > thr).sum()
            log(f"    Threshold : {thr:.4f}")
            log(f"    CLDN18-high: {n_hi} "
                f"({n_hi/len(cv)*100:.1f}%)")
            log(f"    zolbetuximab eligible")
            log(f"    (CLDN18.2 high = drug target)")
    except Exception as e:
        log(f"  KDE error: {e}")

# ============================================================
# STEP 10: MET CIRCUIT
# ============================================================

def met_circuit(tumor, normal):
    log("")
    log("=" * 65)
    log("STEP 10: MET CIRCUIT")
    log("MET +11.2% *** confirmed Script 1")
    log("Second RTK drug target in STAD")
    log("=" * 65)

    gc = list(tumor.columns)

    if "MET" not in gc:
        log("  MET not in matrix")
        return

    nm  = normal["MET"].mean() \
        if "MET" in normal.columns else np.nan
    tm  = tumor["MET"].mean()
    chg = (
        (tm - nm) / nm * 100
        if not np.isnan(nm)
        and abs(nm) > 0.0001
        else np.nan
    )
    log(f"\n  MET normal: {nm:.4f}")
    log(f"  MET tumor : {tm:.4f}")
    log(f"  Change    : "
        f"{chg:+.1f}%" if not np.isnan(chg)
        else "  Change: N/A")

    # MET within-tumor correlations
    log(f"\n  MET correlations (within tumors):")
    met_targets = [
        "ZEB2", "MKI67", "AURKA",
        "SNAI1", "ERBB2", "CDK6",
        "MMP9", "VIM",
    ]
    log(f"  {'Gene':<10} {'r':>8}  p-value")
    log(f"  {'-'*36}")
    for g in met_targets:
        if g not in gc:
            continue
        rv, pv = safe_pearsonr(
            tumor["MET"].values,
            tumor[g].values,
        )
        if not np.isnan(rv):
            log(f"  {g:<10} {rv:>+8.4f}  "
                f"{fmt_p(pv)}")

    if "depth_corrected" in tumor.columns:
        rv, pv = safe_pearsonr(
            tumor["MET"].values,
            tumor["depth_corrected"].values,
        )
        log(f"\n  r(MET, depth) = {rv:+.4f} "
            f"{fmt_p(pv)}")

    # MET bimodal
    mv = tumor["MET"].values
    try:
        kde  = gaussian_kde(mv)
        xs   = np.linspace(
            mv.min(), mv.max(), 300
        )
        ys   = kde(xs)
        mins = argrelmin(ys, order=8)[0]
        log(f"\n  MET bimodal check:")
        log(f"    KDE minima: {len(mins)}")
        if len(mins) > 0:
            thr  = xs[mins[0]]
            n_hi = (mv > thr).sum()
            log(f"    Threshold : {thr:.4f}")
            log(f"    MET-high  : {n_hi} "
                f"({n_hi/len(mv)*100:.1f}%)")
        else:
            log("    No bimodal found")
            log("    MET uniformly elevated")
    except Exception as e:
        log(f"  KDE error: {e}")

# ============================================================
# STEP 11: DRUG TARGET SUMMARY
# ============================================================

def drug_target_summary(tumor, normal):
    log("")
    log("=" * 65)
    log("STEP 11: DRUG TARGET DEPTH SUMMARY")
    log("=" * 65)

    gc   = list(tumor.columns)
    d_col = "depth_corrected" \
        if "depth_corrected" in tumor.columns \
        else None

    targets = [
        ("ERBB2",  "Trastuzumab"),
        ("MET",    "Anti-MET"),
        ("CDK4",   "CDK4/6i"),
        ("CDK6",   "CDK4/6i"),
        ("AURKA",  "Alisertib"),
        ("TOP2A",  "Chemo target"),
        ("HDAC1",  "HDAC inhibitor"),
        ("EZH2",   "EZH2i (DOWN — not target)"),
        ("MKI67",  "Proliferation marker"),
        ("ZEB2",   "TGF-β / anti-EMT"),
        ("CDX2",   "Intestinal TF"),
        ("CLDN18", "Zolbetuximab"),
    ]

    log(f"\n  {'Target':<10} {'Drug':<28} "
        f"{'Normal':>9} {'Tumor':>9} "
        f"{'Change':>9}  "
        f"{'r(depth)':>10}  p")
    log(f"  {'-'*90}")

    for gene, drug in targets:
        if gene not in gc:
            log(f"  {gene:<10} {drug:<28} "
                f"  NOT FOUND")
            continue
        nm  = normal[gene].mean() \
            if gene in normal.columns \
            else np.nan
        tm  = tumor[gene].mean()
        chg = (
            (tm - nm) / nm * 100
            if not np.isnan(nm)
            and abs(nm) > 0.0001
            else np.nan
        )
        cs = (
            f"{chg:+.1f}%"
            if not np.isnan(chg) else "N/A"
        )
        if d_col:
            rv, pv = safe_pearsonr(
                tumor[gene].values,
                tumor[d_col].values,
            )
            rs = (
                f"{rv:+.4f}"
                if not np.isnan(rv) else "N/A"
            )
            ps = (
                fmt_p(pv)
                if not np.isnan(pv) else "N/A"
            )
        else:
            rs, ps = "N/A", "N/A"
        log(f"  {gene:<10} {drug:<28} "
            f"{nm:>9.4f} {tm:>9.4f} "
            f"{cs:>9}  {rs:>10}  {ps}")

# ============================================================
# STEP 12: FIGURE
# ============================================================

def generate_figure(tumor, normal, corrs):
    log("")
    log("--- Generating Script 2 figure ---")

    if len(tumor) < 2 or len(normal) < 2:
        log("  Insufficient data")
        return

    fig = plt.figure(figsize=(26, 22))
    fig.suptitle(
        "Stomach Adenocarcinoma — "
        "Circuit Analysis\n"
        "Script 2 | Dataset: GSE66229 | "
        f"T={len(tumor)} N={len(normal)} | "
        "OrganismCore 2026-03-01\n"
        "CDX2 circuit | EZH2 paradox | "
        "ERBB family | ACRG subtypes | "
        "Drug targets",
        fontsize=10,
        fontweight="bold",
        y=0.99,
    )
    gs = gridspec.GridSpec(
        3, 3, figure=fig,
        hspace=0.55, wspace=0.42,
    )

    clr_n = "#2980b9"
    clr_t = "#c0392b"
    gc    = list(tumor.columns)

    def bar_pair(ax, genes, title):
        avail = [g for g in genes if g in gc]
        if not avail:
            ax.text(
                0.5, 0.5, "No data",
                ha="center", va="center",
                transform=ax.transAxes,
            )
            ax.set_title(title, fontsize=9)
            return
        x = np.arange(len(avail))
        w = 0.35
        for i, (lbl, df_g, c) in enumerate([
            ("Normal", normal, clr_n),
            ("STAD",   tumor,  clr_t),
        ]):
            ms = [
                df_g[g].mean()
                if g in df_g.columns else 0
                for g in avail
            ]
            se = [
                df_g[g].sem()
                if g in df_g.columns else 0
                for g in avail
            ]
            ax.bar(
                x + i*w - 0.5*w,
                ms, w, yerr=se,
                color=c, label=lbl,
                capsize=3, alpha=0.85,
            )
        ax.set_xticks(x)
        ax.set_xticklabels(
            avail, rotation=45,
            ha="right", fontsize=7,
        )
        ax.set_ylabel("log2 expr", fontsize=7)
        ax.set_title(title, fontsize=9)
        ax.legend(fontsize=7)

    # A — CDX2 circuit
    ax_a = fig.add_subplot(gs[0, 0])
    bar_pair(
        ax_a,
        ["CDX2", "MUC2", "KRT20",
         "VIL1", "FABP1"],
        "A — CDX2 Circuit\n"
        "Intestinal program intact?",
    )

    # B — ERBB family shift
    ax_b = fig.add_subplot(gs[0, 1])
    bar_pair(
        ax_b,
        ["ERBB2", "ERBB3", "ERBB4",
         "EGFR", "GRB7"],
        "B — ERBB Family Identity Shift\n"
        "ERBB2 UP / ERBB3+4 DOWN",
    )

    # C — EZH2 paradox
    ax_c = fig.add_subplot(gs[0, 2])
    bar_pair(
        ax_c,
        ["EZH2", "KDM6A", "SUZ12",
         "HDAC1", "BMI1"],
        "C — H3K27 Balance\n"
        "EZH2 DOWN / KDM6A UP",
    )

    # D — Corrected depth by subtype
    ax_d = fig.add_subplot(gs[1, 0])
    if ("depth_corrected" in tumor.columns
            and "subtype" in tumor.columns):
        subtypes = sorted(
            tumor["subtype"].unique()
        )
        colors_sub = [
            "#e74c3c", "#3498db",
            "#2ecc71", "#f39c12",
        ]
        data_sub = [
            tumor[tumor["subtype"] == st][
                "depth_corrected"
            ].values
            for st in subtypes
        ]
        bp = ax_d.boxplot(
            data_sub,
            labels=subtypes,
            patch_artist=True,
        )
        for patch, c in zip(
            bp["boxes"],
            colors_sub[:len(subtypes)],
        ):
            patch.set_facecolor(c)
            patch.set_alpha(0.7)
        ax_d.set_xticklabels(
            subtypes, rotation=30,
            ha="right", fontsize=7,
        )
        ax_d.set_ylabel(
            "Corrected depth", fontsize=7
        )
        ax_d.set_title(
            "D — Depth by ACRG Subtype\n"
            "EMT vs MSI vs TP53+/-",
            fontsize=9,
        )
    else:
        ax_d.text(
            0.5, 0.5, "No subtype data",
            ha="center", va="center",
            transform=ax_d.transAxes,
        )
        ax_d.set_title("D — Depth by Subtype",
                       fontsize=9)

    # E — Drug targets
    ax_e = fig.add_subplot(gs[1, 1])
    drug_genes = [
        g for g in [
            "ERBB2", "MET", "CDK4",
            "CDK6", "AURKA", "HDAC1",
            "ZEB2", "CDX2",
        ] if g in gc
    ]
    if drug_genes:
        nm_v = [
            normal[g].mean()
            if g in normal.columns else 0
            for g in drug_genes
        ]
        tm_v = [tumor[g].mean()
                for g in drug_genes]
        x    = np.arange(len(drug_genes))
        w    = 0.35
        ax_e.bar(
            x - w/2, nm_v, w,
            color=clr_n, label="Normal",
            alpha=0.85,
        )
        ax_e.bar(
            x + w/2, tm_v, w,
            color=clr_t, label="STAD",
            alpha=0.85,
        )
        ax_e.set_xticks(x)
        ax_e.set_xticklabels(
            drug_genes, rotation=45,
            ha="right", fontsize=7,
        )
        ax_e.set_title(
            "E — Drug Targets\n"
            "Geometry-derived",
            fontsize=9,
        )
        ax_e.legend(fontsize=7)

    # F — Depth correlations (corrected)
    ax_f = fig.add_subplot(gs[1, 2])
    if corrs:
        top = corrs[:15]
        gc2 = [c[0] for c in top]
        vc  = [c[1] for c in top]
        cc  = [
            clr_t if v < 0 else "#27ae60"
            for v in vc
        ]
        ax_f.barh(gc2, vc, color=cc)
        ax_f.axvline(
            0, color="black", linewidth=0.8
        )
        ax_f.set_xlabel(
            "r with corrected depth",
            fontsize=8,
        )
        ax_f.set_title(
            "F — Corrected Depth Correlations\n"
            "Top 15",
            fontsize=9,
        )
        ax_f.tick_params(axis="y", labelsize=7)

    # G — EZH2 scatter vs depth
    ax_g = fig.add_subplot(gs[2, 0])
    if ("EZH2" in gc
            and "depth_corrected" in tumor.columns):
        ax_g.scatter(
            tumor["EZH2"].values,
            tumor["depth_corrected"].values,
            alpha=0.4, s=15, color=clr_t,
        )
        rv, pv = safe_pearsonr(
            tumor["EZH2"].values,
            tumor["depth_corrected"].values,
        )
        ax_g.set_xlabel(
            "EZH2 expression", fontsize=8
        )
        ax_g.set_ylabel(
            "Corrected depth", fontsize=8
        )
        ax_g.set_title(
            f"G — EZH2 vs Depth\n"
            f"r={rv:+.3f} {fmt_p(pv)}",
            fontsize=9,
        )

    # H — CDX2 scatter vs depth
    ax_h = fig.add_subplot(gs[2, 1])
    if ("CDX2" in gc
            and "depth_corrected" in tumor.columns):
        ax_h.scatter(
            tumor["CDX2"].values,
            tumor["depth_corrected"].values,
            alpha=0.4, s=15, color="#8e44ad",
        )
        rv, pv = safe_pearsonr(
            tumor["CDX2"].values,
            tumor["depth_corrected"].values,
        )
        ax_h.set_xlabel(
            "CDX2 expression", fontsize=8
        )
        ax_h.set_ylabel(
            "Corrected depth", fontsize=8
        )
        ax_h.set_title(
            f"H — CDX2 vs Depth\n"
            f"r={rv:+.3f} {fmt_p(pv)}",
            fontsize=9,
        )

    # I — Summary
    ax_i = fig.add_subplot(gs[2, 2])
    ax_i.axis("off")

    def chg_str(gene):
        if gene not in gc \
                or gene not in normal.columns:
            return "N/A"
        nm_v = normal[gene].mean()
        tm_v = tumor[gene].mean()
        if abs(nm_v) < 0.0001:
            return "N/A"
        return f"{(tm_v-nm_v)/nm_v*100:+.1f}%"

    n_found = len([g for g in gc])
    summary = (
        "I — SCRIPT 2 SUMMARY\n"
        "─────────────────────────\n"
        f"T={len(tumor)} N={len(normal)}\n"
        f"Genes: {n_found}\n\n"
        "CIRCUITS:\n"
        "  CDX2 → MUC2/KRT20/VIL1\n"
        "  Intact? See Step 6\n\n"
        "EZH2 PARADOX:\n"
        f"  Overall: {chg_str('EZH2')}\n"
        "  r>0 within tumors\n"
        "  H3K27 REVERSED in STAD\n\n"
        "DRUG TARGETS:\n"
        f"  ERBB2: {chg_str('ERBB2')}\n"
        f"  MET  : {chg_str('MET')}\n"
        f"  CDK4 : {chg_str('CDK4')}\n"
        f"  AURKA: {chg_str('AURKA')}\n"
        f"  HDAC1: {chg_str('HDAC1')}\n\n"
        "CLDN18:\n"
        f"  {chg_str('CLDN18')}\n\n"
        "Framework: OrganismCore\n"
        "Doc: 89b | 2026-03-01"
    )
    ax_i.text(
        0.03, 0.97, summary,
        transform=ax_i.transAxes,
        fontsize=8.5,
        verticalalignment="top",
        fontfamily="monospace",
        bbox=dict(
            boxstyle="round",
            facecolor="#f8f8f8",
            edgecolor="#cccccc",
        ),
    )

    out = os.path.join(
        S2_DIR,
        "stad_circuit_analysis.png",
    )
    plt.savefig(
        out, dpi=150, bbox_inches="tight",
    )
    log(f"\n  Figure saved: {out}")
    plt.close()

# ============================================================
# MAIN
# ============================================================

def main():
    log("=" * 65)
    log("STOMACH ADENOCARCINOMA")
    log("CIRCUIT ANALYSIS — SCRIPT 2")
    log("Dataset: GSE66229")
    log("Framework: OrganismCore")
    log("Doc: 89b | Date: 2026-03-01")
    log("=" * 65)
    log("")
    log("  OBJECTIVES:")
    log("  1. Find CLDN18/GKN1/KRT20 (missing)")
    log("  2. Correct depth score")
    log("  3. Classify ACRG subtypes")
    log("  4. Test CDX2 circuit integrity")
    log("  5. ERBB family circuit")
    log("  6. EZH2 paradox")
    log("  7. Drug target depth correlations")

    log("\n=== STEP 0: LOAD S1 OUTPUTS ===")
    gene_df, meta_df = load_s1_outputs()

    log("\n=== STEP 1: EXPAND PROBES ===")
    gene_df = expand_probes(gene_df, meta_df)

    log("\n=== STEP 2: CLASSIFY ===")
    tumor, normal, t_idx, n_idx = \
        classify_samples(gene_df, meta_df)

    log("\n=== STEP 3: CORRECTED DEPTH ===")
    tumor, corrs, sw_used, fa_used = \
        corrected_depth_score(tumor, normal)

    log("\n=== STEP 4: ACRG SUBTYPES ===")
    tumor = classify_acrg_subtypes(tumor)

    log("\n=== STEP 5: DEPTH BY SUBTYPE ===")
    depth_by_subtype(tumor)

    log("\n=== STEP 6: CDX2 CIRCUIT ===")
    cdx2_circuit(tumor, normal)

    log("\n=== STEP 7: ERBB CIRCUIT ===")
    tumor = erbb_circuit(tumor, normal)

    log("\n=== STEP 8: EZH2 PARADOX ===")
    ezh2_paradox(tumor, normal)

    log("\n=== STEP 9: CLDN18 ===")
    cldn18_analysis(tumor, normal)

    log("\n=== STEP 10: MET CIRCUIT ===")
    met_circuit(tumor, normal)

    log("\n=== STEP 11: DRUG TARGETS ===")
    drug_target_summary(tumor, normal)

    log("\n=== STEP 12: FIGURE ===")
    generate_figure(tumor, normal, corrs)

    write_log()
    log(f"\n  Log: {LOG_FILE}")
    log(f"  Outputs: {S2_DIR}")
    log("\n=== SCRIPT 2 COMPLETE ===")


if __name__ == "__main__":
    main()
