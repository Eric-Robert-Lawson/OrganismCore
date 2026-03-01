"""
Stomach Adenocarcinoma — Survival and Panel Analysis
SCRIPT 3 — SURVIVAL / CLINICAL PANEL / TF NETWORK
Dataset: GSE66229
  300 STAD tumors / 100 normal gastric
  ACRG Korean cohort
  Affymetrix GPL570
  Survival data available

FRAMEWORK: OrganismCore Principles-First
Doc: 89c-pre | Date: 2026-03-01

SCRIPT 3 OBJECTIVES:
  1. Survival analysis
     Kaplan-Meier by depth quartile
     Cox regression depth vs OS
     Does depth predict survival?
  2. 3-gene clinical panel
     ZEB2 + AURKA + ERBB4
     r > 0.85 with full depth = valid
  3. Gastric TF network
     SOX2 / GATA4 / GATA6 / HNF4A / FOXA2
     Are any tracking with depth?
     Find the actual switch TF
  4. MLH1 paradox
     Within non-MSI tumors
  5. EMT subtype fix
     Re-parameterized classifier
  6. ZEB2 as primary attractor marker
     Circuit analysis

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
S3_DIR      = os.path.join(BASE_DIR, "results_s3")
LOG_FILE    = os.path.join(S3_DIR, "s3_log.txt")

os.makedirs(S3_DIR, exist_ok=True)

GENE_MATRIX  = os.path.join(
    RESULTS_DIR, "gene_matrix.csv"
)
META_CSV     = os.path.join(
    RESULTS_DIR, "metadata.csv"
)
MATRIX_PATH  = os.path.join(
    BASE_DIR,
    "GSE66229_series_matrix.txt.gz"
)

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

def safe_spearmanr(x, y):
    xa = np.asarray(x, dtype=float)
    ya = np.asarray(y, dtype=float)
    mask = np.isfinite(xa) & np.isfinite(ya)
    xa, ya = xa[mask], ya[mask]
    if len(xa) < 5:
        return np.nan, np.nan
    return stats.spearmanr(xa, ya)

# ============================================================
# KAPLAN-MEIER ESTIMATOR
# Pure numpy — no lifelines dependency
# ============================================================

def kaplan_meier(time, event):
    """
    Returns (times, survival) arrays.
    time:  array of follow-up times
    event: array of 0/1 (1=event occurred)
    """
    time  = np.asarray(time,  dtype=float)
    event = np.asarray(event, dtype=float)
    mask  = np.isfinite(time) & np.isfinite(event)
    time  = time[mask]
    event = event[mask]

    order    = np.argsort(time)
    time     = time[order]
    event    = event[order]
    uniq_t   = np.unique(time)
    n        = len(time)
    S        = 1.0
    surv     = [1.0]
    t_out    = [0.0]

    for t in uniq_t:
        idx   = time == t
        d     = event[idx].sum()
        n_at  = (time >= t).sum()
        if n_at > 0 and d > 0:
            S *= (1 - d / n_at)
        surv.append(S)
        t_out.append(t)

    return np.array(t_out), np.array(surv)

def logrank_test(t1, e1, t2, e2):
    """
    Log-rank test between two groups.
    Returns (stat, p_value).
    """
    t1 = np.asarray(t1, dtype=float)
    e1 = np.asarray(e1, dtype=float)
    t2 = np.asarray(t2, dtype=float)
    e2 = np.asarray(e2, dtype=float)

    m1 = np.isfinite(t1) & np.isfinite(e1)
    m2 = np.isfinite(t2) & np.isfinite(e2)
    t1, e1 = t1[m1], e1[m1]
    t2, e2 = t2[m2], e2[m2]

    if len(t1) < 2 or len(t2) < 2:
        return np.nan, np.nan

    all_t = np.unique(
        np.concatenate([t1, t2])
    )
    O1 = O2 = E1 = E2 = 0.0
    V = 0.0

    for t in all_t:
        n1 = (t1 >= t).sum()
        n2 = (t2 >= t).sum()
        d1 = ((t1 == t) & (e1 == 1)).sum()
        d2 = ((t2 == t) & (e2 == 1)).sum()
        n  = n1 + n2
        d  = d1 + d2
        if n < 2 or d == 0:
            continue
        e1_t = d * n1 / n
        O1  += d1
        E1  += e1_t
        O2  += d2
        E2  += d - e1_t
        if n > 1:
            V += (
                n1 * n2 * d * (n - d)
                / (n ** 2 * (n - 1))
            )

    if V < 1e-10:
        return np.nan, np.nan

    stat = (O1 - E1) ** 2 / V
    pv   = 1 - stats.chi2.cdf(stat, df=1)
    return stat, pv

# ============================================================
# STEP 0: LOAD ALL DATA
# ============================================================

def load_all_data():
    log("=" * 65)
    log("STEP 0: LOAD DATA")
    log("=" * 65)

    # Load gene matrix from Script 1
    if not os.path.exists(GENE_MATRIX):
        log(f"  ERROR: {GENE_MATRIX} not found")
        sys.exit(1)

    gene_df = pd.read_csv(
        GENE_MATRIX, index_col=0
    )
    log(f"  Gene matrix S1: {gene_df.shape}")

    # Load metadata
    meta_df = None
    if os.path.exists(META_CSV):
        meta_df = pd.read_csv(
            META_CSV, index_col=0
        )
        log(f"  Meta: {meta_df.shape}")

    return gene_df, meta_df

# ============================================================
# STEP 1: EXPAND TO ALL NEEDED GENES
# Add TFs and any still-missing genes
# ============================================================

def expand_all_genes(gene_df):
    log("")
    log("=" * 65)
    log("STEP 1: EXPAND GENE MATRIX")
    log("Gastric TFs + MLH1 + survival markers")
    log("=" * 65)

    # All probes we want to add
    needed_probes = {
        # Gastric master TFs
        "205769_at":    "SOX2",
        "210220_at":    "HNF4A",
        "209933_s_at":  "GATA4",
        "211543_s_at":  "GATA6",
        "204147_s_at":  "FOXA2",
        "210803_s_at":  "SOX17",
        "212230_s_at":  "FOXA1",
        # Intestinal TFs
        "209588_at":    "CDX2",
        "209748_at":    "CDX1",
        # MMR / MSI markers
        "202589_at":    "MLH1",
        "202461_s_at":  "MSH2",
        "215198_s_at":  "MSH6",
        "204534_at":    "PMS2",
        # ZEB2 circuit targets
        "208079_s_at":  "ZEB2",
        "216641_s_at":  "SNAI1",
        "213566_at":    "SNAI2",
        "218816_at":    "ZEB1",
        "213844_at":    "TWIST1",
        "201131_s_at":  "CDH1",
        "203440_at":    "CDH2",
        # CLDN18 — may have been found
        "220066_at":    "CLDN18",
        "213451_at":    "CLDN18",
        "204013_at":    "CLDN18",
        # GKN1 alternatives
        "219534_at":    "GKN1",
        "220716_at":    "GKN1",
        # KRT20
        "208826_at":    "KRT20",
        "212531_at":    "KRT20",
        "217236_s_at":  "KRT20",
        # Survival-relevant genes
        "204092_s_at":  "AURKA",
        "208079_s_at":  "ZEB2",
        "205923_at":    "ERBB4",
        "216836_s_at":  "ERBB2",
        "203510_at":    "MET",
        "212020_s_at":  "MKI67",
        "201291_s_at":  "TOP2A",
        "203358_s_at":  "EZH2",
        "221604_s_at":  "KDM6A",
        "201418_s_at":  "HDAC1",
        # VEGF pathway
        "210513_s_at":  "VEGFA",
        "204018_at":    "VEGFB",
        "210931_s_at":  "KDR",
        # FGFR
        "203638_s_at":  "FGFR2",
        "212112_at":    "FGFR1",
        # TGF-B (ZEB2 upstream)
        "203085_s_at":  "TGFB1",
        "208655_at":    "TGFB2",
        "213085_s_at":  "TGFBR1",
        "212779_at":    "TGFBR2",
        # Wnt pathway
        "201645_at":    "CTNNB1",
        "213880_at":    "APC",
        "205186_at":    "AXIN2",
        "201251_at":    "WNT5A",
        # Notch
        "209098_s_at":  "NOTCH1",
        "208729_at":    "NOTCH2",
        "215248_at":    "JAG1",
        # p53 pathway
        "201746_at":    "TP53",
        "202284_s_at":  "CDKN1A",
        "209379_at":    "CDKN2A",
        # Apoptosis
        "203685_at":    "BCL2",
        "208479_s_at":  "BCL2L1",
        "209595_at":    "MCL1",
        "201284_s_at":  "BAX",
    }

    # Find which genes already in matrix
    already = set(gene_df.index)
    to_find = {
        p: g for p, g in needed_probes.items()
        if g not in already
    }
    target_new = set(to_find.values())
    log(f"  Already have: {len(already)} genes")
    log(f"  Need to find: {len(target_new)} genes")

    if not to_find or not os.path.exists(
        MATRIX_PATH
    ):
        log("  Cannot expand — using current matrix")
        return gene_df

    # Scan matrix for needed probes
    found_rows = {}
    header     = None
    probes_set = set(to_find.keys())

    log("  Scanning matrix for new probes...")
    try:
        with gzip.open(
            MATRIX_PATH, "rt",
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
                parts = line.split("\t")
                probe = parts[0].strip().strip('"')
                if probe in probes_set:
                    vals = []
                    for v in parts[1:]:
                        try:
                            vals.append(float(v))
                        except Exception:
                            vals.append(np.nan)
                    found_rows[probe] = vals

    except Exception as e:
        log(f"  Matrix scan error: {e}")
        return gene_df

    log(f"  Probes found: {len(found_rows)}")

    if found_rows and header:
        sample_ids = header[1:]
        new_rows   = {}
        for probe, vals in found_rows.items():
            gene = to_find[probe]
            if len(vals) == len(sample_ids):
                row = pd.Series(
                    vals, index=sample_ids
                )
                row = np.log2(
                    row.clip(lower=1.0)
                )
                if gene not in new_rows:
                    new_rows[gene] = row
                else:
                    if row.mean() > \
                            new_rows[gene].mean():
                        new_rows[gene] = row

        added = []
        for gene, row in new_rows.items():
            if gene not in gene_df.index:
                gene_df = pd.concat([
                    gene_df,
                    row.to_frame(name=gene).T
                ])
                added.append(gene)

        log(f"  Added: {added}")

    log(f"  Total genes: {len(gene_df)}")

    still_miss = [
        g for g in target_new
        if g not in gene_df.index
    ]
    if still_miss:
        log(f"  Still missing: {still_miss}")

    return gene_df

# ============================================================
# STEP 2: CLASSIFY + SURVIVAL EXTRACTION
# ============================================================

def classify_and_survival(gene_df, meta_df):
    log("")
    log("=" * 65)
    log("STEP 2: CLASSIFY + SURVIVAL DATA")
    log("=" * 65)

    samples = gene_df.columns.tolist()

    # Classify tumor / normal
    if meta_df is not None \
            and "source_name_ch1" \
            in meta_df.columns:
        src = meta_df[
            "source_name_ch1"
        ].fillna("").str.lower()
        tumor_idx = src[
            src.str.contains(
                r"tumor|cancer",
                regex=True,
            )
        ].index.tolist()
        normal_idx = src[
            src.str.contains(
                r"normal|adjacent",
                regex=True,
            )
        ].index.tolist()
    else:
        tumor_idx  = samples[:300]
        normal_idx = samples[300:]

    tumor_idx  = [
        s for s in tumor_idx
        if s in gene_df.columns
    ]
    normal_idx = [
        s for s in normal_idx
        if s in gene_df.columns
    ]

    tumor  = gene_df[tumor_idx].T
    normal = gene_df[normal_idx].T

    log(f"  TUMOR  : {len(tumor)}")
    log(f"  NORMAL : {len(normal)}")

    # Extract survival data from metadata
    # GSE66229 ACRG cohort has:
    # overall survival (months) and
    # vital status in characteristics
    surv_time   = {}
    surv_event  = {}
    subtype_ann = {}

    if meta_df is not None:
        log(f"\n  Scanning metadata for survival...")
        log(f"  Columns: "
            f"{list(meta_df.columns)}")

        # Show all characteristics columns
        char_cols = [
            c for c in meta_df.columns
            if "characteristics" in c.lower()
        ]
        log(f"  Characteristics columns: "
            f"{char_cols}")
        for c in char_cols:
            log(f"  [{c}] sample values:")
            for v in meta_df[c].dropna(
            ).iloc[:8].tolist():
                log(f"    {v}")

        # Parse all characteristics
        for c in char_cols:
            for idx in meta_df.index:
                val = str(
                    meta_df.loc[idx, c]
                ).lower()

                # Overall survival months
                import re
                m = re.search(
                    r"overall.survival.*?:"
                    r"\s*([0-9.]+)",
                    val,
                )
                if m:
                    surv_time[idx] = float(
                        m.group(1)
                    )

                # OS months alternative patterns
                for pat in [
                    r"os.*?month.*?:\s*([0-9.]+)",
                    r"survival.month.*?:\s*([0-9.]+)",
                    r"months.*?:\s*([0-9.]+)",
                    r"time.*?:\s*([0-9.]+)",
                ]:
                    m = re.search(pat, val)
                    if m and idx not in surv_time:
                        surv_time[idx] = float(
                            m.group(1)
                        )

                # Vital status / event
                if any(x in val for x in [
                    "dead", "deceased",
                    "died", "death",
                    "vital status: 1",
                    "vital: dead",
                    "status: dead",
                ]):
                    surv_event[idx] = 1
                elif any(x in val for x in [
                    "alive", "living",
                    "vital status: 0",
                    "vital: alive",
                    "status: alive",
                    "censored",
                ]):
                    surv_event[idx] = 0

                # ACRG molecular subtype
                for st in [
                    "mss/tp53+", "mss/tp53-",
                    "msi", "mss/emt",
                    "emt", "tp53",
                ]:
                    if st in val:
                        subtype_ann[idx] = val

        log(f"\n  Survival time found: "
            f"{len(surv_time)}")
        log(f"  Vital status found: "
            f"{len(surv_event)}")
        log(f"  Subtype annotation: "
            f"{len(subtype_ann)}")

        if len(surv_time) > 0:
            times = list(surv_time.values())
            log(f"  Time range: "
                f"{min(times):.1f} – "
                f"{max(times):.1f} months")

        # Show sample survival values
        if surv_time:
            log(f"  Sample times:")
            for idx in list(
                surv_time.keys()
            )[:5]:
                ev = surv_event.get(idx, "?")
                log(f"    {idx}: "
                    f"t={surv_time[idx]:.1f} "
                    f"event={ev}")

        # Show raw chars if nothing found
        if len(surv_time) == 0:
            log("\n  No survival parsed.")
            log("  Raw characteristics (first 5):")
            for c in char_cols:
                for v in meta_df[c].iloc[
                    :5
                ].tolist():
                    log(f"  {v}")

    # Add survival to tumor dataframe
    tumor = tumor.copy()
    tumor["surv_time"] = [
        surv_time.get(idx, np.nan)
        for idx in tumor.index
    ]
    tumor["surv_event"] = [
        surv_event.get(idx, np.nan)
        for idx in tumor.index
    ]

    n_surv = tumor["surv_time"].notna().sum()
    log(f"\n  Tumors with survival: {n_surv}")

    return tumor, normal

# ============================================================
# STEP 3: BUILD CORRECTED DEPTH SCORE
# Same as Script 2 corrected score
# ============================================================

def build_depth_score(tumor, normal):
    log("")
    log("=" * 65)
    log("STEP 3: BUILD CORRECTED DEPTH SCORE")
    log("=" * 65)

    gc = list(tumor.columns)

    sw_genes = [
        g for g in [
            "FABP1", "MUC2", "ERBB4",
            "ERBB3", "TWIST1", "CDH2",
            "VIM", "MUC5AC",
        ] if g in gc
    ]
    fa_genes = [
        g for g in [
            "MKI67", "ZEB2", "CDX2",
            "AURKA", "TOP2A", "SNAI1",
            "HDAC1", "MET",
        ] if g in gc
    ]

    log(f"  Switch: {sw_genes}")
    log(f"  FA    : {fa_genes}")

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

    if sw_genes:
        depth += (
            1 - norm01(
                tumor[sw_genes].mean(axis=1)
            )
        )
        comp += 1
    if fa_genes:
        depth += norm01(
            tumor[fa_genes].mean(axis=1)
        )
        comp += 1
    if comp > 0:
        depth /= comp

    tumor["depth"] = depth.values

    log(f"\n  Depth (n={len(tumor)}):")
    log(f"    Mean  : {depth.mean():.4f}")
    log(f"    Median: {depth.median():.4f}")
    log(f"    Std   : {depth.std():.4f}")

    return tumor

# ============================================================
# STEP 4: SURVIVAL ANALYSIS
# Kaplan-Meier by depth quartile
# ============================================================

def survival_analysis(tumor):
    log("")
    log("=" * 65)
    log("STEP 4: SURVIVAL ANALYSIS")
    log("Kaplan-Meier by depth quartile")
    log("Cox: depth vs overall survival")
    log("=" * 65)

    has_surv = (
        tumor["surv_time"].notna().sum() > 10
        and tumor["surv_event"].notna().sum() > 5
    )

    if not has_surv:
        log("\n  Survival data not found in metadata.")
        log("  GSE66229 survival data may be in")
        log("  supplementary files not series matrix.")
        log("")
        log("  Attempting to use characteristics")
        log("  for any available clinical data...")
        log("")
        log("  ALTERNATIVE: testing depth vs")
        log("  proxy clinical markers in expression")
        log("  (TP53, CCND1, KRAS) as surrogates.")

        # Use expression-based surrogates
        gc = list(tumor.columns)
        log(f"\n  Depth vs clinical proxy markers:")
        log(f"  {'Gene':<10} {'r':>8}  "
            f"p-value  Interpretation")
        log(f"  {'-'*50}")
        for gene in [
            "TP53", "CCND1", "KRAS",
            "MKI67", "ERBB2", "MET",
            "AURKA", "ZEB2",
        ]:
            if gene not in gc:
                continue
            rv, pv = safe_pearsonr(
                tumor["depth"].values,
                tumor[gene].values,
            )
            if not np.isnan(rv):
                log(f"  {gene:<10} {rv:>+8.4f}  "
                    f"{fmt_p(pv)}")
        return tumor

    # Have survival data — run KM
    t_all = tumor["surv_time"].values
    e_all = tumor["surv_event"].values

    valid = np.isfinite(t_all) & np.isfinite(e_all)
    log(f"\n  Valid survival: {valid.sum()}")
    log(f"  Events: {int(e_all[valid].sum())}")
    log(f"  Time range: "
        f"{t_all[valid].min():.1f} – "
        f"{t_all[valid].max():.1f} months")

    # Depth quartiles
    d_vals = tumor.loc[valid, "depth"].values
    q1, q2, q3 = np.percentile(
        d_vals, [25, 50, 75]
    )
    log(f"\n  Depth quartiles:")
    log(f"    Q1: {q1:.4f}")
    log(f"    Q2: {q2:.4f}")
    log(f"    Q3: {q3:.4f}")

    def get_grp(depth_thresh_lo,
                depth_thresh_hi=None):
        mask = valid.copy()
        if depth_thresh_hi is not None:
            mask &= (
                (tumor["depth"].values >=
                 depth_thresh_lo)
                & (tumor["depth"].values <
                   depth_thresh_hi)
            )
        else:
            mask &= (
                tumor["depth"].values >=
                depth_thresh_lo
            )
        return (
            tumor.loc[mask, "surv_time"].values,
            tumor.loc[mask, "surv_event"].values,
        )

    # High vs Low depth
    low_mask  = valid & (
        tumor["depth"].values <= q2
    )
    high_mask = valid & (
        tumor["depth"].values > q2
    )
    t_low  = tumor.loc[low_mask,  "surv_time"].values
    e_low  = tumor.loc[low_mask,  "surv_event"].values
    t_high = tumor.loc[high_mask, "surv_time"].values
    e_high = tumor.loc[high_mask, "surv_event"].values

    log(f"\n  High depth: n={len(t_high)} "
        f"events={int(e_high.sum())}")
    log(f"  Low depth : n={len(t_low)} "
        f"events={int(e_low.sum())}")

    _, lrp = logrank_test(t_low, e_low,
                          t_high, e_high)
    log(f"\n  Log-rank test (high vs low depth):")
    log(f"  {fmt_p(lrp) if not np.isnan(lrp) else 'N/A'}")

    # Median survival
    def median_surv(t, e):
        km_t, km_s = kaplan_meier(t, e)
        cross = np.where(km_s <= 0.5)[0]
        if len(cross) > 0:
            return km_t[cross[0]]
        return np.nan

    ms_low  = median_surv(t_low,  e_low)
    ms_high = median_surv(t_high, e_high)
    log(f"\n  Median OS:")
    log(f"    Low depth : "
        f"{ms_low:.1f} months"
        if not np.isnan(ms_low)
        else "    Low depth : not reached")
    log(f"    High depth: "
        f"{ms_high:.1f} months"
        if not np.isnan(ms_high)
        else "    High depth: not reached")

    # 4-quartile KM
    log(f"\n  Kaplan-Meier by quartile:")
    log(f"  {'Quartile':<12} {'n':>5} "
        f"{'Events':>8} {'MedianOS':>10}")
    log(f"  {'-'*40}")
    q_bounds = [
        (0.0, q1, "Q1 (low)"),
        (q1,  q2, "Q2"),
        (q2,  q3, "Q3"),
        (q3,  1.1, "Q4 (high)"),
    ]
    for lo, hi, label in q_bounds:
        mask = valid & (
            tumor["depth"].values >= lo
        ) & (
            tumor["depth"].values < hi
        )
        t_q = tumor.loc[mask, "surv_time"].values
        e_q = tumor.loc[mask, "surv_event"].values
        ms  = median_surv(t_q, e_q)
        ms_str = (
            f"{ms:.1f}"
            if not np.isnan(ms)
            else "NR"
        )
        log(f"  {label:<12} "
            f"{len(t_q):>5} "
            f"{int(e_q.sum()):>8} "
            f"{ms_str:>10}")

    # Cox-like: Pearson(depth, surv_time)
    # among events only (rough proxy)
    ev_mask = valid & (
        tumor["surv_event"].values == 1
    )
    if ev_mask.sum() > 5:
        rv, pv = safe_pearsonr(
            tumor.loc[ev_mask, "depth"].values,
            tumor.loc[ev_mask, "surv_time"].values,
        )
        log(f"\n  Correlation depth vs OS time")
        log(f"  (among events, n={ev_mask.sum()}):")
        log(f"    r={rv:+.4f} {fmt_p(pv)}"
            if not np.isnan(rv)
            else "    r=N/A")
        if not np.isnan(rv) and rv < 0 \
                and pv < 0.05:
            log("    Deeper = shorter survival ✓")
        elif not np.isnan(rv) and rv > 0 \
                and pv < 0.05:
            log("    Deeper = longer survival")
            log("    (unexpected — check)")

    # Save KM data
    tumor.to_csv(
        os.path.join(S3_DIR, "tumor_survival.csv")
    )

    return tumor, t_low, e_low, t_high, e_high

# ============================================================
# STEP 5: 3-GENE CLINICAL PANEL
# ZEB2 + AURKA + ERBB4
# ============================================================

def clinical_panel(tumor, normal):
    log("")
    log("=" * 65)
    log("STEP 5: 3-GENE CLINICAL PANEL")
    log("Predicted: ZEB2 + AURKA + ERBB4")
    log("Target: r > 0.85 with full depth")
    log("=" * 65)

    gc = list(tumor.columns)

    if "depth" not in tumor.columns:
        log("  No depth score — skip")
        return

    # Test predicted panel
    panel_genes = ["ZEB2", "AURKA", "ERBB4"]
    avail = [g for g in panel_genes if g in gc]
    log(f"\n  Predicted panel: {avail}")

    if len(avail) >= 2:
        def norm01_series(s):
            mn, mx = s.min(), s.max()
            return (
                (s - mn) / (mx - mn)
                if mx > mn
                else pd.Series(
                    0.0, index=s.index
                )
            )

        # Build panel score
        # ZEB2: positive (UP in deep tumors)
        # AURKA: positive
        # ERBB4: negative (DOWN in deep tumors)
        panel = pd.Series(
            np.zeros(len(tumor)),
            index=tumor.index,
        )
        comp = 0
        if "ZEB2" in gc:
            panel += norm01_series(tumor["ZEB2"])
            comp += 1
        if "AURKA" in gc:
            panel += norm01_series(tumor["AURKA"])
            comp += 1
        if "ERBB4" in gc:
            panel += (
                1 - norm01_series(tumor["ERBB4"])
            )
            comp += 1
        if comp > 0:
            panel /= comp

        rv, pv = safe_pearsonr(
            panel.values,
            tumor["depth"].values,
        )
        log(f"\n  ZEB2+AURKA+ERBB4 panel:")
        log(f"    r with full depth = {rv:+.4f}")
        log(f"    {fmt_p(pv)}")
        log(f"    Target: r > 0.85")
        log(f"    Result: "
            f"{'PANEL VALID ✓' if not np.isnan(rv) and rv > 0.85 else 'below threshold'}")

        tumor["panel_3gene"] = panel.values

    # Test all 2-gene combinations
    log(f"\n  All 2-gene panel combinations:")
    log(f"  {'Genes':<25} {'r':>8}  p-value")
    log(f"  {'-'*45}")

    depth_up = [
        g for g in [
            "ZEB2", "AURKA", "TOP2A",
            "MKI67", "CDC20", "CCNB1",
            "CDK6", "SNAI1",
        ] if g in gc
    ]
    depth_dn = [
        g for g in [
            "ERBB4", "VIM", "FABP1",
            "CDH2", "TWIST1", "ERBB3",
        ] if g in gc
    ]

    best_r  = 0
    best_combo = None
    results_2g = []

    for up in depth_up:
        for dn in depth_dn:
            s = (
                norm01_series(tumor[up])
                + (1 - norm01_series(tumor[dn]))
            ) / 2
            rv, pv = safe_pearsonr(
                s.values, tumor["depth"].values
            )
            if not np.isnan(rv):
                results_2g.append(
                    (up, dn, rv, pv)
                )
                if rv > best_r:
                    best_r = rv
                    best_combo = (up, dn)

    results_2g.sort(
        key=lambda x: x[2], reverse=True
    )
    for up, dn, rv, pv in results_2g[:10]:
        label = f"{up}(+) / {dn}(-)"
        log(f"  {label:<25} {rv:>+8.4f}  "
            f"{fmt_p(pv)}")

    if best_combo:
        log(f"\n  Best 2-gene panel: "
            f"{best_combo[0]} + {best_combo[1]}")
        log(f"  r = {best_r:.4f}")

    # Test all 3-gene combinations
    log(f"\n  Top 3-gene panels:")
    results_3g = []
    for up1 in depth_up:
        for up2 in depth_up:
            if up2 <= up1:
                continue
            for dn in depth_dn:
                s = (
                    norm01_series(tumor[up1])
                    + norm01_series(tumor[up2])
                    + (1 - norm01_series(
                        tumor[dn]
                    ))
                ) / 3
                rv, pv = safe_pearsonr(
                    s.values,
                    tumor["depth"].values,
                )
                if not np.isnan(rv):
                    results_3g.append(
                        (up1, up2, dn, rv, pv)
                    )

    results_3g.sort(
        key=lambda x: x[3], reverse=True
    )
    log(f"  {'Genes':<35} {'r':>8}  p-value")
    log(f"  {'-'*52}")
    for up1, up2, dn, rv, pv in results_3g[:10]:
        label = f"{up1}+{up2}/{dn}(-)"
        log(f"  {label:<35} {rv:>+8.4f}  "
            f"{fmt_p(pv)}")

    if results_3g:
        best = results_3g[0]
        log(f"\n  Best 3-gene panel:")
        log(f"    {best[0]} + {best[1]} / "
            f"{best[2]} (inverse)")
        log(f"    r = {best[3]:.4f}")
        log(f"    {fmt_p(best[4])}")

    return tumor

# ============================================================
# STEP 6: GASTRIC TF NETWORK
# ============================================================

def gastric_tf_network(tumor, normal):
    log("")
    log("=" * 65)
    log("STEP 6: GASTRIC TF NETWORK")
    log("SOX2/GATA4/GATA6/HNF4A/FOXA2")
    log("Which TF tracks with depth?")
    log("Find the actual switch TF")
    log("=" * 65)

    gc = list(tumor.columns)

    tfs = [
        ("SOX2",  "Gastric pluripotency TF"),
        ("GATA4", "Gastric master TF"),
        ("GATA6", "Gastric master TF"),
        ("HNF4A", "Hepatic/gastric TF"),
        ("FOXA2", "Foregut TF"),
        ("FOXA1", "Luminal/gastric TF"),
        ("SOX17", "Endoderm TF"),
        ("CDX2",  "Intestinal master TF"),
        ("CDX1",  "Intestinal TF"),
    ]

    log(f"\n  TF expression T vs N:")
    log(f"  {'TF':<10} {'Normal':>9} "
        f"{'Tumor':>9} {'Change':>9}  "
        f"{'r(depth)':>10}  p")
    log(f"  {'-'*65}")

    tf_depth_corrs = []
    for tf, desc in tfs:
        if tf not in gc:
            log(f"  {tf:<10} NOT FOUND")
            continue
        nm  = normal[tf].mean() \
            if tf in normal.columns else np.nan
        tm  = tumor[tf].mean()
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
        rv, pv = safe_pearsonr(
            tumor[tf].values,
            tumor["depth"].values,
        )
        rs = (
            f"{rv:+.4f}"
            if not np.isnan(rv) else "N/A"
        )
        ps = (
            fmt_p(pv)
            if not np.isnan(pv) else "N/A"
        )
        log(f"  {tf:<10} {nm:>9.4f} "
            f"{tm:>9.4f} {cs:>9}  "
            f"{rs:>10}  {ps}")
        if not np.isnan(rv):
            tf_depth_corrs.append(
                (tf, desc, nm, tm, chg, rv, pv)
            )

    # Rank by abs(r) with depth
    tf_depth_corrs.sort(
        key=lambda x: abs(x[5]), reverse=True
    )
    log(f"\n  TFs ranked by |r| with depth:")
    for tf, desc, nm, tm, chg, rv, pv in \
            tf_depth_corrs:
        direction = (
            "SWITCH ✓ (DOWN = deeper)"
            if rv < -0.2 and pv < 0.05
            else "FA marker (UP = deeper)"
            if rv > 0.2 and pv < 0.05
            else "weak/no relationship"
        )
        log(f"  {tf:<8} r={rv:+.4f} "
            f"{fmt_p(pv)}  {direction}")

    # TF circuit test — each TF vs targets
    log(f"\n  TF circuit integrity:")
    gastric_targets = [
        g for g in [
            "MUC5AC", "TFF1", "GKN1",
            "GKN2", "ATP4A", "PGC",
            "OLFM4", "CLDN18",
        ] if g in gc
    ]

    for tf, _ in tfs[:5]:  # Top 5 gastric TFs
        if tf not in gc:
            continue
        intact = 0
        tested = 0
        log(f"\n  {tf} → gastric targets:")
        for tgt in gastric_targets:
            rv, pv = safe_pearsonr(
                tumor[tf].values,
                tumor[tgt].values,
            )
            tested += 1
            status = ""
            if not np.isnan(rv):
                if rv > 0.15 and pv < 0.05:
                    intact += 1
                    status = "intact ✓"
                elif rv < -0.15 and pv < 0.05:
                    status = "inverted"
                else:
                    status = "broken"
            log(f"    {tgt:<10} r={rv:+.4f} "
                f"{fmt_p(pv)}  {status}"
                if not np.isnan(rv)
                else f"    {tgt:<10} N/A")
        if tested > 0:
            log(f"  {tf} circuit: "
                f"{intact}/{tested} intact")

# ============================================================
# STEP 7: MLH1 PARADOX
# ============================================================

def mlh1_paradox(tumor, normal):
    log("")
    log("=" * 65)
    log("STEP 7: MLH1 PARADOX")
    log("MLH1 r=+0.5664 with depth ***")
    log("But MSI (MLH1-loss) = shallowest")
    log("=" * 65)

    gc = list(tumor.columns)

    if "MLH1" not in gc:
        log("  MLH1 not in matrix")
        return

    nm_mlh1 = normal["MLH1"].mean() \
        if "MLH1" in normal.columns else np.nan
    tm_mlh1 = tumor["MLH1"].mean()
    log(f"\n  MLH1 normal: {nm_mlh1:.4f}")
    log(f"  MLH1 tumor : {tm_mlh1:.4f}")
    log(f"  Change: "
        f"{(tm_mlh1-nm_mlh1)/nm_mlh1*100:+.1f}%")

    rv, pv = safe_pearsonr(
        tumor["MLH1"].values,
        tumor["depth"].values,
    )
    log(f"  r(MLH1, depth) = {rv:+.4f} "
        f"{fmt_p(pv)}")

    # MLH1 by subtype
    log(f"\n  MLH1 bimodal check:")
    mv = tumor["MLH1"].values
    try:
        kde  = gaussian_kde(mv)
        xs   = np.linspace(
            mv.min(), mv.max(), 300
        )
        ys   = kde(xs)
        mins = argrelmin(ys, order=8)[0]
        log(f"    KDE minima: {len(mins)}")
        if len(mins) > 0:
            thr  = xs[mins[0]]
            n_lo = (mv < thr).sum()
            n_hi = (mv >= thr).sum()
            log(f"    Threshold: {thr:.4f}")
            log(f"    MLH1-low : {n_lo} "
                f"({n_lo/len(mv)*100:.1f}%)")
            log(f"    MLH1-high: {n_hi} "
                f"({n_hi/len(mv)*100:.1f}%)")
            log(f"    Expected MSI (~23%): "
                f"MLH1-low should be ~23%")

            tumor = tumor.copy()
            tumor["mlh1_status"] = np.where(
                tumor["MLH1"] < thr,
                "MLH1_low_MSI",
                "MLH1_high_MSS",
            )

            # Depth by MLH1 status
            d_lo = tumor[
                tumor["mlh1_status"]
                == "MLH1_low_MSI"
            ]["depth"]
            d_hi = tumor[
                tumor["mlh1_status"]
                == "MLH1_high_MSS"
            ]["depth"]

            log(f"\n    Depth by MLH1 status:")
            log(f"    MLH1-low  (MSI): "
                f"{d_lo.mean():.4f}"
                f" ± {d_lo.std():.4f}")
            log(f"    MLH1-high (MSS): "
                f"{d_hi.mean():.4f}"
                f" ± {d_hi.std():.4f}")
            _, pp = safe_mwu(
                d_lo.values, d_hi.values,
                "two-sided",
            )
            log(f"    {fmt_p(pp)}")

            if d_lo.mean() < d_hi.mean():
                log(f"\n    PARADOX RESOLVED:")
                log(f"    MLH1-low (MSI) tumors")
                log(f"    are SHALLOWER than")
                log(f"    MLH1-high (MSS) tumors.")
                log(f"    The bulk r=+0.5664 means:")
                log(f"    MLH1-HIGH tumors are deeper.")
                log(f"    MLH1-LOW (MSI) are shallow.")
                log(f"    MLH1 expression tracks WITH")
                log(f"    the non-MSI attractor depth.")
                log(f"    MLH1 is a depth marker")
                log(f"    within the MSS population.")
    except Exception as e:
        log(f"    KDE error: {e}")

    return tumor

# ============================================================
# STEP 8: EMT SUBTYPE FIX
# ============================================================

def emt_subtype_fix(tumor, normal):
    log("")
    log("=" * 65)
    log("STEP 8: EMT SUBTYPE RE-CLASSIFICATION")
    log("Script 2 found only 1 EMT tumor")
    log("Expected ~15% (45 tumors)")
    log("Re-parameterizing classifier")
    log("=" * 65)

    gc    = list(tumor.columns)
    tumor = tumor.copy()

    # Strategy: CDH1 low + ZEB2 high
    # relative to tumor population
    if "CDH1" not in gc or "ZEB2" not in gc:
        log("  CDH1 or ZEB2 not in matrix")
        return tumor

    cdh1_vals = tumor["CDH1"].values
    zeb2_vals = tumor["ZEB2"].values

    # CDH1 loss: bottom 20% of CDH1
    # ZEB2 high: top 20% of ZEB2
    cdh1_thr = np.percentile(cdh1_vals, 20)
    zeb2_thr = np.percentile(zeb2_vals, 80)

    emt_mask = (
        (cdh1_vals < cdh1_thr)
        & (zeb2_vals > zeb2_thr)
    )
    n_emt = emt_mask.sum()
    log(f"\n  CDH1 threshold (20th pct): "
        f"{cdh1_thr:.4f}")
    log(f"  ZEB2 threshold (80th pct): "
        f"{zeb2_thr:.4f}")
    log(f"  CDH1-low + ZEB2-high: {n_emt} "
        f"({n_emt/len(tumor)*100:.1f}%)")
    log(f"  Expected EMT: ~15%")

    tumor["emt_fixed"] = np.where(
        emt_mask, "EMT", "non_EMT"
    )

    # EMT subtype characteristics
    emt_tumors = tumor[tumor["emt_fixed"] == "EMT"]
    non_emt    = tumor[tumor["emt_fixed"] == "non_EMT"]

    log(f"\n  EMT subtype gene expression:")
    log(f"  {'Gene':<10} {'EMT':>9} "
        f"{'non-EMT':>9} {'Change':>9}")
    log(f"  {'-'*42}")
    for g in [
        "CDH1", "CDH2", "ZEB2", "SNAI1",
        "TWIST1", "VIM", "MKI67", "AURKA",
        "ERBB2", "MET", "CLDN18",
    ]:
        if g not in gc:
            continue
        em = emt_tumors[g].mean() \
            if g in emt_tumors.columns else np.nan
        ne = non_emt[g].mean() \
            if g in non_emt.columns else np.nan
        chg = (
            (em - ne) / ne * 100
            if not np.isnan(ne)
            and abs(ne) > 0.0001
            else np.nan
        )
        cs = (
            f"{chg:+.1f}%"
            if not np.isnan(chg) else "N/A"
        )
        log(f"  {g:<10} {em:>9.4f} "
            f"{ne:>9.4f} {cs:>9}")

    # EMT depth
    if "depth" in tumor.columns:
        d_emt = emt_tumors["depth"]
        d_non = non_emt["depth"]
        log(f"\n  Depth EMT: "
            f"{d_emt.mean():.4f} "
            f"± {d_emt.std():.4f}")
        log(f"  Depth non-EMT: "
            f"{d_non.mean():.4f} "
            f"± {d_non.std():.4f}")
        _, pp = safe_mwu(
            d_emt.values, d_non.values,
            "two-sided",
        )
        log(f"  {fmt_p(pp)}")

    return tumor

# ============================================================
# STEP 9: ZEB2 CIRCUIT
# Primary attractor marker
# ============================================================

def zeb2_circuit(tumor, normal):
    log("")
    log("=" * 65)
    log("STEP 9: ZEB2 CIRCUIT")
    log("r(ZEB2, depth) = +0.8226 ***")
    log("Primary attractor marker in STAD")
    log("TGF-B upstream driver")
    log("=" * 65)

    gc = list(tumor.columns)

    if "ZEB2" not in gc:
        log("  ZEB2 not in matrix")
        return

    nm  = normal["ZEB2"].mean() \
        if "ZEB2" in normal.columns else np.nan
    tm  = tumor["ZEB2"].mean()
    log(f"\n  ZEB2 normal: {nm:.4f}")
    log(f"  ZEB2 tumor : {tm:.4f}")
    log(f"  Change     : "
        f"{(tm-nm)/nm*100:+.1f}%")

    # ZEB2 upstream (TGF-B)
    log(f"\n  ZEB2 upstream (TGF-B pathway):")
    for g in [
        "TGFB1", "TGFB2",
        "TGFBR1", "TGFBR2",
    ]:
        if g not in gc:
            continue
        rv, pv = safe_pearsonr(
            tumor[g].values,
            tumor["ZEB2"].values,
        )
        nm_g = normal[g].mean() \
            if g in normal.columns else np.nan
        tm_g = tumor[g].mean()
        chg  = (
            (tm_g - nm_g) / nm_g * 100
            if not np.isnan(nm_g)
            and abs(nm_g) > 0.0001
            else np.nan
        )
        log(f"  {g:<10} change="
            f"{chg:+.1f}%  "
            f"r(ZEB2)={rv:+.4f}  "
            f"{fmt_p(pv)}"
            if not np.isnan(rv)
            else f"  {g:<10} N/A")

    # ZEB2 downstream
    log(f"\n  ZEB2 downstream correlations:")
    log(f"  {'Gene':<10} {'r':>8}  p-value")
    log(f"  {'-'*36}")
    for g in [
        "SNAI1", "SNAI2", "TWIST1",
        "CDH1", "CDH2", "VIM",
        "MMP2", "MMP9", "FN1",
        "AURKA", "MKI67", "TOP2A",
        "EZH2", "HDAC1",
    ]:
        if g not in gc:
            continue
        rv, pv = safe_pearsonr(
            tumor["ZEB2"].values,
            tumor[g].values,
        )
        if not np.isnan(rv):
            log(f"  {g:<10} {rv:>+8.4f}  "
                f"{fmt_p(pv)}")

    # ZEB2 bimodal
    zv = tumor["ZEB2"].values
    try:
        kde  = gaussian_kde(zv)
        xs   = np.linspace(
            zv.min(), zv.max(), 300
        )
        ys   = kde(xs)
        mins = argrelmin(ys, order=8)[0]
        log(f"\n  ZEB2 bimodal check:")
        log(f"    KDE minima: {len(mins)}")
        if len(mins) > 0:
            thr  = xs[mins[0]]
            n_hi = (zv > thr).sum()
            log(f"    Threshold: {thr:.4f}")
            log(f"    ZEB2-high: {n_hi} "
                f"({n_hi/len(zv)*100:.1f}%)")
    except Exception as e:
        log(f"    KDE error: {e}")

# ============================================================
# STEP 10: FULL DEPTH CORRELATION SURVEY
# All genes vs depth — find new signals
# ============================================================

def full_depth_survey(tumor, normal):
    log("")
    log("=" * 65)
    log("STEP 10: FULL DEPTH CORRELATION SURVEY")
    log("All genes vs corrected depth")
    log("Discovery of novel signals")
    log("=" * 65)

    gc = [
        c for c in tumor.columns
        if c not in [
            "depth", "surv_time",
            "surv_event", "panel_3gene",
            "emt_fixed", "mlh1_status",
            "her2_status", "subtype",
            "group",
        ]
    ]

    corrs = []
    for gene in gc:
        rv, pv = safe_pearsonr(
            tumor["depth"].values,
            tumor[gene].values,
        )
        if not np.isnan(rv):
            corrs.append((gene, rv, pv))

    corrs.sort(
        key=lambda x: abs(x[1]), reverse=True
    )

    log(f"\n  All genes ranked by |r| with depth:")
    log(f"  Total tested: {len(corrs)}")
    log(f"\n  TOP 30 POSITIVE (high in deep tumors):")
    log(f"  {'Gene':<12} {'r':>8}  p-value")
    log(f"  {'-'*36}")
    pos = [
        (g, r, p) for g, r, p in corrs
        if r > 0
    ][:30]
    for gene, rv, pv in pos:
        log(f"  {gene:<12} {rv:>+8.4f}  "
            f"{fmt_p(pv)}")

    log(f"\n  TOP 30 NEGATIVE (low in deep tumors):")
    log(f"  {'Gene':<12} {'r':>8}  p-value")
    log(f"  {'-'*36}")
    neg = [
        (g, r, p) for g, r, p in corrs
        if r < 0
    ][:30]
    for gene, rv, pv in neg:
        log(f"  {gene:<12} {rv:>+8.4f}  "
            f"{fmt_p(pv)}")

    # Save all correlations
    corr_df = pd.DataFrame(
        corrs,
        columns=["gene", "r_depth", "p_depth"],
    )
    corr_df.to_csv(
        os.path.join(
            S3_DIR, "full_depth_correlations.csv"
        ),
        index=False,
    )
    log(f"\n  Saved: full_depth_correlations.csv")

    return corrs

# ============================================================
# STEP 11: FIGURE
# ============================================================

def generate_figure(
    tumor, normal,
    t_low=None, e_low=None,
    t_high=None, e_high=None,
    corrs=None,
):
    log("")
    log("--- Generating Script 3 figure ---")

    if len(tumor) < 2:
        log("  Insufficient data")
        return

    fig = plt.figure(figsize=(26, 22))
    fig.suptitle(
        "Stomach Adenocarcinoma — "
        "Survival / Clinical Panel / TF Network\n"
        "Script 3 | Dataset: GSE66229 | "
        f"T={len(tumor)} | "
        "OrganismCore 2026-03-01\n"
        "Depth → survival | 3-gene panel | "
        "Gastric TFs | ZEB2 circuit | "
        "EMT subtype",
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
    gc    = [
        c for c in tumor.columns
        if c not in [
            "depth", "surv_time",
            "surv_event", "panel_3gene",
            "emt_fixed", "mlh1_status",
            "her2_status", "subtype",
            "group",
        ]
    ]

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

    # A — KM curve (if survival available)
    ax_a = fig.add_subplot(gs[0, 0])
    has_surv = (
        t_low is not None
        and len(t_low) > 2
        and len(t_high) > 2
    )
    if has_surv:
        km_t_lo, km_s_lo = kaplan_meier(
            t_low, e_low
        )
        km_t_hi, km_s_hi = kaplan_meier(
            t_high, e_high
        )
        ax_a.step(
            km_t_lo, km_s_lo,
            color=clr_n, label="Low depth",
            linewidth=2,
        )
        ax_a.step(
            km_t_hi, km_s_hi,
            color=clr_t, label="High depth",
            linewidth=2,
        )
        _, lrp = logrank_test(
            t_low, e_low, t_high, e_high
        )
        ax_a.set_xlabel("Time (months)", fontsize=8)
        ax_a.set_ylabel(
            "Overall survival", fontsize=8
        )
        pstr = (
            fmt_p(lrp)
            if not np.isnan(lrp) else "N/A"
        )
        ax_a.set_title(
            f"A — Kaplan-Meier\n"
            f"High vs Low depth | {pstr}",
            fontsize=9,
        )
        ax_a.legend(fontsize=7)
        ax_a.set_ylim(0, 1.05)
    else:
        # Show depth distribution instead
        if "depth" in tumor.columns:
            ax_a.hist(
                tumor["depth"].values,
                bins=30, color=clr_t,
                alpha=0.7, edgecolor="white",
            )
            ax_a.set_xlabel(
                "Depth score", fontsize=8
            )
            ax_a.set_ylabel(
                "Count", fontsize=8
            )
            ax_a.set_title(
                "A — Depth Distribution\n"
                "(Survival data not in matrix)",
                fontsize=9,
            )
        else:
            ax_a.text(
                0.5, 0.5,
                "No survival data",
                ha="center", va="center",
                transform=ax_a.transAxes,
            )
            ax_a.set_title(
                "A — Survival (N/A)",
                fontsize=9,
            )

    # B — 3-gene panel vs full depth
    ax_b = fig.add_subplot(gs[0, 1])
    if ("panel_3gene" in tumor.columns
            and "depth" in tumor.columns):
        ax_b.scatter(
            tumor["panel_3gene"].values,
            tumor["depth"].values,
            alpha=0.4, s=15, color=clr_t,
        )
        rv, pv = safe_pearsonr(
            tumor["panel_3gene"].values,
            tumor["depth"].values,
        )
        ax_b.set_xlabel(
            "3-gene panel score", fontsize=8
        )
        ax_b.set_ylabel(
            "Full depth score", fontsize=8
        )
        pstr = (
            fmt_p(pv)
            if not np.isnan(pv) else "N/A"
        )
        ax_b.set_title(
            f"B — 3-Gene Panel Validation\n"
            f"r={rv:+.3f} {pstr}",
            fontsize=9,
        )
    else:
        ax_b.text(
            0.5, 0.5, "No panel data",
            ha="center", va="center",
            transform=ax_b.transAxes,
        )
        ax_b.set_title(
            "B — 3-Gene Panel", fontsize=9
        )

    # C — Gastric TFs
    ax_c = fig.add_subplot(gs[0, 2])
    bar_pair(
        ax_c,
        ["SOX2", "GATA4", "GATA6",
         "HNF4A", "FOXA2", "CDX2"],
        "C — Gastric TF Network\n"
        "Normal vs STAD",
    )

    # D — ZEB2 circuit
    ax_d = fig.add_subplot(gs[1, 0])
    bar_pair(
        ax_d,
        ["ZEB2", "TGFB1", "TGFB2",
         "SNAI1", "CDH1", "CDH2"],
        "D — ZEB2 Circuit\n"
        "TGF-B upstream / targets",
    )

    # E — EMT subtype
    ax_e = fig.add_subplot(gs[1, 1])
    if "emt_fixed" in tumor.columns:
        emt_depth = tumor[
            tumor["emt_fixed"] == "EMT"
        ]["depth"].values
        non_depth = tumor[
            tumor["emt_fixed"] == "non_EMT"
        ]["depth"].values
        ax_e.boxplot(
            [non_depth, emt_depth],
            labels=["non-EMT", "EMT"],
            patch_artist=True,
        )
        ax_e.set_ylabel(
            "Depth score", fontsize=8
        )
        _, pp = safe_mwu(
            emt_depth, non_depth, "two-sided"
        )
        pstr = (
            fmt_p(pp)
            if not np.isnan(pp) else "N/A"
        )
        ax_e.set_title(
            f"E — EMT Subtype Depth\n"
            f"{pstr}",
            fontsize=9,
        )
    else:
        ax_e.text(
            0.5, 0.5, "No EMT data",
            ha="center", va="center",
            transform=ax_e.transAxes,
        )
        ax_e.set_title("E — EMT", fontsize=9)

    # F — MLH1 / MSI paradox
    ax_f = fig.add_subplot(gs[1, 2])
    if "mlh1_status" in tumor.columns:
        d_lo = tumor[
            tumor["mlh1_status"]
            == "MLH1_low_MSI"
        ]["depth"].values
        d_hi = tumor[
            tumor["mlh1_status"]
            == "MLH1_high_MSS"
        ]["depth"].values
        ax_f.boxplot(
            [d_lo, d_hi],
            labels=["MLH1-low\n(MSI)",
                    "MLH1-high\n(MSS)"],
            patch_artist=True,
        )
        ax_f.set_ylabel(
            "Depth score", fontsize=8
        )
        ax_f.set_title(
            "F — MLH1 Paradox\n"
            "MSI (shallow) vs MSS (deep)",
            fontsize=9,
        )
    else:
        ax_f.text(
            0.5, 0.5, "No MLH1 data",
            ha="center", va="center",
            transform=ax_f.transAxes,
        )
        ax_f.set_title(
            "F — MLH1", fontsize=9
        )

    # G — Full depth survey top genes
    ax_g = fig.add_subplot(gs[2, 0])
    if corrs:
        top_pos = [
            (g, r) for g, r, p in corrs
            if r > 0
        ][:10]
        top_neg = [
            (g, r) for g, r, p in corrs
            if r < 0
        ][:10]
        top = top_pos + top_neg
        top.sort(key=lambda x: x[1])
        genes_t = [x[0] for x in top]
        vals_t  = [x[1] for x in top]
        colors  = [
            clr_t if v < 0 else "#27ae60"
            for v in vals_t
        ]
        ax_g.barh(genes_t, vals_t, color=colors)
        ax_g.axvline(
            0, color="black", linewidth=0.8
        )
        ax_g.set_xlabel(
            "r with depth", fontsize=8
        )
        ax_g.set_title(
            "G — Full Depth Survey\n"
            "Top positive + negative",
            fontsize=9,
        )
        ax_g.tick_params(axis="y", labelsize=7)

    # H — Wnt / TGF-B pathways
    ax_h = fig.add_subplot(gs[2, 1])
    bar_pair(
        ax_h,
        ["CTNNB1", "APC", "AXIN2",
         "TGFB1", "TGFBR1", "WNT5A"],
        "H — Wnt / TGF-B Pathways\n"
        "ZEB2 upstream signals",
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

    panel_r = "N/A"
    if ("panel_3gene" in tumor.columns
            and "depth" in tumor.columns):
        rv, _ = safe_pearsonr(
            tumor["panel_3gene"].values,
            tumor["depth"].values,
        )
        if not np.isnan(rv):
            panel_r = f"{rv:.4f}"

    summary = (
        "I — SCRIPT 3 SUMMARY\n"
        "─────────────────────────\n"
        f"T={len(tumor)}\n\n"
        "3-GENE PANEL:\n"
        f"  ZEB2+AURKA/ERBB4\n"
        f"  r={panel_r}\n\n"
        "GASTRIC TFs:\n"
        f"  SOX2  : {chg_str('SOX2')}\n"
        f"  GATA4 : {chg_str('GATA4')}\n"
        f"  GATA6 : {chg_str('GATA6')}\n"
        f"  HNF4A : {chg_str('HNF4A')}\n"
        f"  FOXA2 : {chg_str('FOXA2')}\n\n"
        "ZEB2 CIRCUIT:\n"
        f"  TGFB1 : {chg_str('TGFB1')}\n"
        f"  SNAI1 : {chg_str('SNAI1')}\n\n"
        "Framework: OrganismCore\n"
        "Doc: 89c-pre | 2026-03-01"
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
        S3_DIR,
        "stad_survival_panel.png",
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
    log("SURVIVAL / PANEL / TF NETWORK — S3")
    log("Dataset: GSE66229")
    log("Framework: OrganismCore")
    log("Doc: 89c-pre | Date: 2026-03-01")
    log("=" * 65)
    log("")
    log("  OBJECTIVES:")
    log("  1. Survival: depth vs OS")
    log("  2. 3-gene clinical panel")
    log("  3. Gastric TF network")
    log("  4. MLH1 paradox")
    log("  5. EMT subtype fix")
    log("  6. ZEB2 circuit")
    log("  7. Full depth survey")

    log("\n=== STEP 0: LOAD DATA ===")
    gene_df, meta_df = load_all_data()

    log("\n=== STEP 1: EXPAND GENES ===")
    gene_df = expand_all_genes(gene_df)

    log("\n=== STEP 2: CLASSIFY + SURVIVAL ===")
    tumor, normal = classify_and_survival(
        gene_df, meta_df
    )

    log("\n=== STEP 3: DEPTH SCORE ===")
    tumor = build_depth_score(tumor, normal)

    log("\n=== STEP 4: SURVIVAL ANALYSIS ===")
    surv_result = survival_analysis(tumor)
    if isinstance(surv_result, tuple):
        tumor, t_low, e_low, t_high, e_high = \
            surv_result
    else:
        tumor = surv_result
        t_low = e_low = t_high = e_high = None

    log("\n=== STEP 5: 3-GENE PANEL ===")
    tumor = clinical_panel(tumor, normal)

    log("\n=== STEP 6: GASTRIC TF NETWORK ===")
    gastric_tf_network(tumor, normal)

    log("\n=== STEP 7: MLH1 PARADOX ===")
    tumor = mlh1_paradox(tumor, normal)

    log("\n=== STEP 8: EMT SUBTYPE FIX ===")
    tumor = emt_subtype_fix(tumor, normal)

    log("\n=== STEP 9: ZEB2 CIRCUIT ===")
    zeb2_circuit(tumor, normal)

    log("\n=== STEP 10: FULL DEPTH SURVEY ===")
    corrs = full_depth_survey(tumor, normal)

    log("\n=== STEP 11: FIGURE ===")
    generate_figure(
        tumor, normal,
        t_low, e_low, t_high, e_high,
        corrs,
    )

    write_log()
    log(f"\n  Log: {LOG_FILE}")
    log(f"  Outputs: {S3_DIR}")
    log("\n=== SCRIPT 3 COMPLETE ===")


if __name__ == "__main__":
    main()
