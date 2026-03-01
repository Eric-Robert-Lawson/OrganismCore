"""
BLADDER CANCER — FALSE ATTRACTOR ANALYSIS
SCRIPT 4
Dataset: TCGA-BLCA (PanCancer Atlas 2018)
Clinical: cBioPortal API (blca_tcga_pan_can_atlas_2018)
n=407 expression + 411 clinical

Doc: 91d | Date: 2026-03-01

PURPOSE:
  Survival validation deferred from S3.
  Clinical data now in hand.
  Run TV-1 through TV-5.
  Additional tests using cBioPortal
  columns available:
    ANEUPLOIDY_SCORE  — direct CIN measure
    MSI_SCORE_MANTIS  — MSI quantitative
    MSI_SENSOR_SCORE  — MSI quantitative
    MUTATION_COUNT    — TMB proxy
    FRACTION_GENOME_ALTERED — CIN proxy
    SUBTYPE           — published subtype
    AJCC stage        — T-stage
    OS_MONTHS / OS_STATUS
    DSS_MONTHS / DSS_STATUS
    PFS_MONTHS / PFS_STATUS
    DFS_MONTHS / DFS_STATUS

PREDICTIONS LOCKED BEFORE RUN:
(all derived from S1/S2/S3 reasoning)

SURVIVAL:
  TV-1: Luminal depth predicts OS p<0.05
  TV-2: Basal depth predicts OS p<0.05
  TV-3: FGFR3/CCND1/CLDN3 panel OS p<0.05
  TV-4: TWIST1/CDK6/GATA3 panel OS p<0.05
  TV-5: Basal depth predicts DSS p<0.01

NEW TESTS FROM AVAILABLE COLUMNS:
  TV-6: r(AURKA, ANEUPLOIDY_SCORE) > 0
        (AURKA tracks CIN confirmed in S3
         via SCNA fraction — now test with
         direct aneuploidy score)
  TV-7: r(ZEB2, ANEUPLOIDY_SCORE) < 0
        (ZEB2 anti-tracks CIN confirmed S3)
  TV-8: r(luminal depth, MSI_SENSOR_SCORE) > 0
        (deep luminal BLCA is MSI-high —
         NP-BLCA-2 direct test)
  TV-9: SUBTYPE comparison with our
        GATA3/KRT5 classification
        (validate our classifier vs
         published Robertson subtypes)
  TV-10: FRACTION_GENOME_ALTERED higher
         in luminal than basal
         (luminal = higher CIN = AURKA-driven)

Author: Eric Robert Lawson
Framework: OrganismCore
"""

import os
import re
import gzip
import numpy as np
import pandas as pd
from scipy import stats
from lifelines import KaplanMeierFitter
from lifelines.statistics import logrank_test
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import warnings
warnings.filterwarnings("ignore")

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR    = "./blca_false_attractor/"
RESULTS_DIR = os.path.join(
    BASE_DIR, "results_s4"
)
LOG_FILE = os.path.join(
    RESULTS_DIR, "analysis_log_s4.txt"
)
os.makedirs(RESULTS_DIR, exist_ok=True)

EXPR_FILE = os.path.join(
    BASE_DIR, "TCGA_BLCA_expr.gz"
)
CLIN_FILE = os.path.join(
    BASE_DIR, "TCGA_BLCA_clinical_cbio.tsv"
)

# ============================================================
# TARGET GENES
# ============================================================

TARGET_GENES = [
    "UPK1A","UPK1B","UPK2", "UPK3A",
    "UPK3B","CLDN3","CLDN4","CLDN7",
    "GATA3","FOXA1","PPARG","ERBB2",
    "ERBB3","FGFR3","CCND1","CDH1",
    "KRT7", "KRT8", "KRT18","KRT19",
    "KRT20","KRT5", "KRT14","KRT6A",
    "TP63", "CD44", "S100A8","S100A9",
    "VIM",  "ZEB1", "ZEB2", "SNAI1",
    "SNAI2","TWIST1","CDH2","FN1",
    "EGFR", "MET",  "FGFR1","FGFR2",
    "KDR",  "VEGFA","TACSTD2",
    "CD274","PDCD1","CD8A","FOXP3",
    "CD4",  "CD68",
    "EZH2", "HDAC1","HDAC2","KDM6A",
    "KDM5C","DNMT3A","TET2","ARID1A",
    "CDKN1A","CDKN2A","CDK4","CDK6",
    "CCND1","CCNE1","CCNB1","RB1",
    "E2F1", "E2F3", "CDKN1B","CDKN2B",
    "MKI67","TOP2A","AURKA","CDC20",
    "PLK1", "PCNA", "MCM2",
    "BCL2", "MCL1", "BAX","BCL2L1",
    "BIRC5","TP53", "MDM2",
    "APC",  "CTNNB1","AXIN2","AXIN1",
    "TCF7L2","LGR5","WNT5A",
    "MYC",  "MYCN", "PIK3CA","KRAS",
    "HRAS", "NRAS",
    "SOX2", "SOX4", "ALDH1A1",
    "NOTCH1","NOTCH2","HES1","JAG1",
    "TGFB1","TGFBR2","SMAD2","SMAD3",
    "HIF1A","CA9",
    "MLH1", "MSH2", "MSH6",
    "SPRY1","SPRY2","DUSP6",
    "TP73", "PTEN", "TSC1",
    "CDX2", "FOXA2","NKX2-1",
    "IVL",  "SPRR1A","DSG1","DSG3",
    "KRT10","KRT4", "KRT13",
]
TARGET_GENES = sorted(set(TARGET_GENES))

# Updated panels from S1/S2/S3
LUMINAL_SWITCH = [
    "CLDN3","UPK1B","UPK3A",
    "CDKN2B","CDKN2A",
]
LUMINAL_FA = [
    "FGFR3","CCND1","GATA3",
    "FOXA1","KRT19",
]
BASAL_SWITCH = [
    "GATA3","FOXA1","PPARG",
    "KRT8", "ERBB3",
]
BASAL_FA = [
    "TWIST1","ZEB2","CDK6",
    "FN1",   "SNAI1","VIM",
]

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
    if p is None or (
        isinstance(p, float) and np.isnan(p)
    ):
        return "p=N/A     "
    if p < 0.001:  return f"p={p:.2e} ***"
    elif p < 0.01: return f"p={p:.2e}  **"
    elif p < 0.05: return f"p={p:.4f}   *"
    else:          return f"p={p:.4f}  ns"

def safe_pearsonr(x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    m = np.isfinite(x) & np.isfinite(y)
    x, y = x[m], y[m]
    if len(x) < 5:
        return np.nan, np.nan
    return stats.pearsonr(x, y)

def safe_mwu(a, b, alt="two-sided"):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    a = a[np.isfinite(a)]
    b = b[np.isfinite(b)]
    if len(a) < 2 or len(b) < 2:
        return np.nan, np.nan
    return stats.mannwhitneyu(
        a, b, alternative=alt
    )

def norm01(s):
    s  = pd.Series(s, dtype=float)
    mn = s.min()
    mx = s.max()
    if mx > mn:
        return (s - mn) / (mx - mn)
    return pd.Series(0.5, index=s.index)

# ============================================================
# LOAD EXPRESSION
# ============================================================

def load_expr():
    log("")
    log("=" * 65)
    log("LOAD EXPRESSION")
    log(f"  File: {EXPR_FILE}")
    log("=" * 65)

    target_set = set(TARGET_GENES)
    opener = (
        gzip.open(EXPR_FILE, "rt",
                  encoding="utf-8",
                  errors="ignore")
        if EXPR_FILE.endswith(".gz")
        else open(EXPR_FILE, "r",
                  encoding="utf-8",
                  errors="ignore")
    )

    header = None
    rows   = []
    genes  = []

    with opener as f:
        for line in f:
            line  = line.rstrip()
            parts = line.split("\t")
            if header is None:
                header = parts
                continue
            if not parts or not parts[0]:
                continue
            gene = parts[0].strip().strip('"')
            if gene not in target_set:
                continue
            try:
                vals = [
                    float(p)
                    if p not in [
                        "","NA","nan","null",
                    ]
                    else np.nan
                    for p in parts[1:]
                ]
            except ValueError:
                continue
            genes.append(gene)
            rows.append(vals)

    sample_ids = [
        h.strip().strip('"')
        for h in header[1:]
    ]
    n_s = len(sample_ids)

    df = pd.DataFrame(
        {g: r[:n_s] for g, r in
         zip(genes, rows)},
        index=sample_ids,
        dtype=float,
    )

    # Primary tumors only
    tumor_mask = [
        s[13:15] in ["01","03","06"]
        if len(s) >= 15 else True
        for s in df.index
    ]
    df = df[tumor_mask]
    log(f"  Primary tumor samples: {len(df)}")
    log(f"  Genes loaded: {len(df.columns)}")
    return df

# ============================================================
# LOAD AND MERGE CLINICAL
# cBioPortal file columns confirmed:
#   SAMPLE_ID
#   OS_MONTHS / OS_STATUS (patient-level)
#   DSS_MONTHS / DSS_STATUS
#   PFS_MONTHS / PFS_STATUS
#   DFS_MONTHS / DFS_STATUS
#   ANEUPLOIDY_SCORE
#   MSI_SCORE_MANTIS / MSI_SENSOR_SCORE
#   MUTATION_COUNT
#   FRACTION_GENOME_ALTERED
#   SUBTYPE
#   AJCC_PATHOLOGIC_TUMOR_STAGE
#   PATH_T_STAGE
# ============================================================

def load_clinical(df_expr):
    log("")
    log("=" * 65)
    log("LOAD CLINICAL — cBioPortal")
    log(f"  File: {CLIN_FILE}")
    log("=" * 65)

    clin = pd.read_csv(
        CLIN_FILE, sep="\t",
        low_memory=False,
    )
    log(f"  Shape: {clin.shape}")
    log(f"  Columns: "
        f"{list(clin.columns[:10])}")

    # Set SAMPLE_ID as index
    if "SAMPLE_ID" in clin.columns:
        clin = clin.set_index("SAMPLE_ID")
    elif clin.index.name != "SAMPLE_ID":
        log("  WARNING: No SAMPLE_ID column")

    log(f"  Sample IDs example: "
        f"{clin.index[:3].tolist()}")
    log(f"  Expr IDs example: "
        f"{df_expr.index[:3].tolist()}")

    # Match sample IDs
    # cBioPortal: TCGA-XX-XXXX-01
    # Expr:       TCGA-XX-XXXX-01 (same)
    shared = df_expr.index.intersection(
        clin.index
    )
    log(f"  Direct match: {len(shared)}")

    if len(shared) < 50:
        # Try truncating to 15 chars
        clin_15 = {
            s[:15]: s for s in clin.index
        }
        expr_15 = {
            s[:15]: s for s in df_expr.index
        }
        overlap = set(clin_15) & set(expr_15)
        log(f"  15-char match: {len(overlap)}")

        if len(overlap) > len(shared):
            new_map = {}
            for short in overlap:
                new_map[clin_15[short]] = (
                    expr_15[short]
                )
            clin_reindexed = clin.loc[
                list(new_map.keys())
            ].copy()
            clin_reindexed.index = [
                new_map[i]
                for i in clin_reindexed.index
            ]
            clin = clin_reindexed
            shared = df_expr.index.intersection(
                clin.index
            )
            log(f"  After remap: {len(shared)}")

    # Show survival columns
    surv_cols = [
        c for c in clin.columns
        if any(
            x in c.upper()
            for x in [
                "OS","DSS","PFS","DFS",
                "VITAL","DEATH","MONTHS",
                "STATUS","SURVIVAL",
            ]
        )
    ]
    log(f"\n  Survival columns:")
    for c in surv_cols:
        ex = (
            clin.loc[shared, c]
            .dropna().head(3).tolist()
            if len(shared) > 0 else []
        )
        log(f"    {c}: {ex}")

    # Clinical enrichment columns
    extra_cols = [
        "ANEUPLOIDY_SCORE",
        "FRACTION_GENOME_ALTERED",
        "MSI_SCORE_MANTIS",
        "MSI_SENSOR_SCORE",
        "MUTATION_COUNT",
        "TMB_NONSYNONYMOUS",
        "SUBTYPE",
        "AJCC_PATHOLOGIC_TUMOR_STAGE",
        "PATH_T_STAGE",
        "PATH_N_STAGE",
    ]
    log(f"\n  Extra columns available:")
    for c in extra_cols:
        if c in clin.columns:
            ex = (
                clin.loc[shared, c]
                .dropna().head(3).tolist()
                if len(shared) > 0 else []
            )
            log(f"    {c}: {ex}")

    # Align clinical to expression
    clin_aligned = clin.reindex(df_expr.index)
    log(f"\n  Aligned rows: {len(clin_aligned)}")
    log(f"  OS_MONTHS non-null: "
        f"{clin_aligned['OS_MONTHS'].notna().sum()}"
        if "OS_MONTHS" in clin_aligned.columns
        else "  OS_MONTHS: not found"
    )

    return clin_aligned

# ============================================================
# PARSE SURVIVAL VECTORS
# ============================================================

def parse_surv_vectors(clin_aligned):
    """
    Extract numpy arrays aligned to df_expr.
    OS_STATUS: '1:DECEASED' → 1, '0:LIVING' → 0
    DSS_STATUS: '1:DEAD WITH TUMOR' → 1
    """
    n = len(clin_aligned)

    def parse_time(col):
        arr = np.full(n, np.nan)
        if col not in clin_aligned.columns:
            return arr
        for i, v in enumerate(
            clin_aligned[col].values
        ):
            try:
                t = float(v)
                if t > 0:
                    arr[i] = t
            except (ValueError, TypeError):
                pass
        return arr

    def parse_event(col, pos_keywords):
        arr = np.full(n, np.nan)
        if col not in clin_aligned.columns:
            return arr
        for i, v in enumerate(
            clin_aligned[col].values
        ):
            vl = str(v).lower()
            if any(
                k in vl for k in pos_keywords
            ):
                arr[i] = 1
            elif any(
                k in vl for k in [
                    "0:","living","alive",
                    "censored","free",
                ]
            ):
                arr[i] = 0
        return arr

    os_t  = parse_time("OS_MONTHS")
    os_e  = parse_event(
        "OS_STATUS", ["1:","deceased","dead"]
    )
    dss_t = parse_time("DSS_MONTHS")
    dss_e = parse_event(
        "DSS_STATUS",
        ["1:","dead with tumor","dead of disease"],
    )
    pfs_t = parse_time("PFS_MONTHS")
    pfs_e = parse_event(
        "PFS_STATUS",
        ["1:","progression","progressed"],
    )

    for label, t, e in [
        ("OS",  os_t,  os_e),
        ("DSS", dss_t, dss_e),
        ("PFS", pfs_t, pfs_e),
    ]:
        valid = (
            ~np.isnan(t) & ~np.isnan(e)
            & (t > 0)
        )
        n1 = int(np.nansum(e[valid]))
        log(f"  {label}: n={valid.sum()} "
            f"events={n1} "
            f"range={np.nanmin(t[valid]):.1f}"
            f"–{np.nanmax(t[valid]):.1f} mo"
            if valid.sum() > 0
            else f"  {label}: no valid data"
        )

    # Parse numeric columns
    def parse_numeric(col):
        arr = np.full(n, np.nan)
        if col not in clin_aligned.columns:
            return arr
        for i, v in enumerate(
            clin_aligned[col].values
        ):
            try:
                arr[i] = float(v)
            except (ValueError, TypeError):
                pass
        return arr

    aneuploidy  = parse_numeric(
        "ANEUPLOIDY_SCORE"
    )
    fga         = parse_numeric(
        "FRACTION_GENOME_ALTERED"
    )
    msi_mantis  = parse_numeric(
        "MSI_SCORE_MANTIS"
    )
    msi_sensor  = parse_numeric(
        "MSI_SENSOR_SCORE"
    )
    mut_count   = parse_numeric(
        "MUTATION_COUNT"
    )

    log(f"\n  Aneuploidy: "
        f"{(~np.isnan(aneuploidy)).sum()} valid")
    log(f"  FGA:        "
        f"{(~np.isnan(fga)).sum()} valid")
    log(f"  MSI Mantis: "
        f"{(~np.isnan(msi_mantis)).sum()} valid")
    log(f"  MSI Sensor: "
        f"{(~np.isnan(msi_sensor)).sum()} valid")
    log(f"  Mut count:  "
        f"{(~np.isnan(mut_count)).sum()} valid")

    # Published subtype
    subtype_pub = [""] * n
    if "SUBTYPE" in clin_aligned.columns:
        for i, v in enumerate(
            clin_aligned["SUBTYPE"].values
        ):
            subtype_pub[i] = str(v)
        unique_st = list(
            set(s for s in subtype_pub if s
                and s != "nan")
        )
        log(f"\n  Published subtypes: "
            f"{unique_st}")

    return {
        "os_t":   os_t,  "os_e":  os_e,
        "dss_t":  dss_t, "dss_e": dss_e,
        "pfs_t":  pfs_t, "pfs_e": pfs_e,
        "aneuploidy":  aneuploidy,
        "fga":         fga,
        "msi_mantis":  msi_mantis,
        "msi_sensor":  msi_sensor,
        "mut_count":   mut_count,
        "subtype_pub": subtype_pub,
    }

# ============================================================
# CLASSIFY SUBTYPES
# ============================================================

def classify_subtypes(df_expr):
    gc = list(df_expr.columns)
    subtype = pd.Series(
        "Tumor", index=df_expr.index
    )
    if "GATA3" in gc and "KRT5" in gc:
        g3n   = norm01(
            df_expr["GATA3"].values
        )
        k5n   = norm01(
            df_expr["KRT5"].values
        )
        score = g3n.values - k5n.values
        med   = np.median(score)
        for s, sc in zip(
            df_expr.index, score
        ):
            subtype[s] = (
                "Luminal" if sc >= med
                else "Basal"
            )
    return subtype

# ============================================================
# DEPTH SCORE
# ============================================================

def build_depth(df, switch, fa, label):
    gc  = list(df.columns)
    sw  = [g for g in switch if g in gc]
    fa_ = [g for g in fa     if g in gc]
    depth = pd.Series(
        np.zeros(len(df)),
        index=df.index, dtype=float,
    )
    nd = 0
    if sw:
        depth += (
            1 - norm01(df[sw].mean(axis=1))
        )
        nd += 1
    if fa_:
        depth += norm01(
            df[fa_].mean(axis=1)
        )
        nd += 1
    if nd > 0:
        depth /= nd
    log(f"  {label} n={len(df)} "
        f"mean={depth.mean():.4f} "
        f"std={depth.std():.4f}")
    return depth

# ============================================================
# SURVIVAL ANALYSIS
# ============================================================

def run_km(
    t, e, depth_vals,
    label, endpoint_label,
    panel_genes=None,
    panel_dirs=None,
    df_v=None,
):
    valid = (
        ~np.isnan(t) & ~np.isnan(e)
        & ~np.isnan(depth_vals)
        & (t > 0)
    )
    log(f"\n  {label} — {endpoint_label}:")
    log(f"  n valid = {valid.sum()}")

    if valid.sum() < 10:
        log(f"  Insufficient data")
        return None

    t_v = t[valid]
    e_v = e[valid]
    d_v = depth_vals[valid]

    n1 = int(e_v.sum())
    log(f"  Events = {n1}/{len(t_v)}")
    log(f"  Time: "
        f"{t_v.min():.1f}–{t_v.max():.1f} mo")

    # Median split
    med = np.median(d_v)
    hi  = d_v >= med
    lo  = ~hi

    try:
        res = logrank_test(
            t_v[hi], t_v[lo],
            e_v[hi], e_v[lo],
        )
        p_depth = res.p_value
    except Exception:
        p_depth = np.nan

    log(f"  Deep   (n={hi.sum()}): "
        f"mean={t_v[hi].mean():.1f} mo")
    log(f"  Shallow(n={lo.sum()}): "
        f"mean={t_v[lo].mean():.1f} mo")
    log(f"  Log-rank depth: {fmt_p(p_depth)}")

    if not np.isnan(p_depth):
        log(
            f"  {'CONFIRMED ✓' if p_depth<0.05 else 'NOT CONFIRMED ✗'}"
        )

    # Panel test
    p_panel = np.nan
    phi = plo = None
    if (
        panel_genes and panel_dirs
        and df_v is not None
    ):
        gc_ = list(df_v.columns)
        avail = [
            (g, d) for g, d in
            zip(panel_genes, panel_dirs)
            if g in gc_
        ]
        if len(avail) >= 2:
            parts = []
            for gene, direction in avail:
                ns = norm01(
                    df_v[gene].values
                )
                parts.append(
                    1 - ns
                    if direction == "-"
                    else ns
                )
            panel_v = np.mean(parts, axis=0)
            panel_valid = panel_v[valid]
            pmed = np.median(panel_valid)
            phi  = panel_valid >= pmed
            plo  = ~phi
            try:
                res_p = logrank_test(
                    t_v[phi], t_v[plo],
                    e_v[phi], e_v[plo],
                )
                p_panel = res_p.p_value
            except Exception:
                p_panel = np.nan

            log(f"\n  Panel "
                f"{[g for g,_ in avail]}:")
            log(f"  High (n={phi.sum()}): "
                f"mean={t_v[phi].mean():.1f}")
            log(f"  Low  (n={plo.sum()}): "
                f"mean={t_v[plo].mean():.1f}")
            log(f"  Panel log-rank: "
                f"{fmt_p(p_panel)}")
            log(
                f"  {'CONFIRMED ✓' if not np.isnan(p_panel) and p_panel<0.05 else 'NOT CONFIRMED ✗'}"
            )

    # Individual gene tests
    if df_v is not None:
        gc_ = list(df_v.columns)
        log(f"\n  Individual genes p<0.05:")
        for gene in sorted(gc_):
            gv = df_v[gene].values[valid]
            gmed = np.nanmedian(gv)
            ghi  = gv >= gmed
            glo  = ~ghi
            if ghi.sum() < 5 or glo.sum() < 5:
                continue
            try:
                r = logrank_test(
                    t_v[ghi], t_v[glo],
                    e_v[ghi], e_v[glo],
                )
                p = r.p_value
            except Exception:
                p = np.nan
            if not np.isnan(p) and p < 0.05:
                hi_mean = t_v[ghi].mean()
                lo_mean = t_v[glo].mean()
                direction = (
                    "↑=worse"
                    if hi_mean < lo_mean
                    else "↑=better"
                )
                log(f"  {gene:<12} "
                    f"{fmt_p(p)}  "
                    f"{direction}")

    return {
        "t": t_v, "e": e_v,
        "hi": hi, "lo": lo,
        "p_depth": p_depth,
        "phi": phi, "plo": plo,
        "p_panel": p_panel,
        "label": label,
        "endpoint": endpoint_label,
    }

# ============================================================
# CIN / MSI TESTS
# ============================================================

def cin_msi_tests(
    lum, bas, l_depth, b_depth,
    surv_data, df_expr, subtype,
):
    log("")
    log("=" * 65)
    log("CIN / MSI TESTS")
    log("TV-6 through TV-10")
    log("=" * 65)

    gc_l = list(lum.columns)
    gc_b = list(bas.columns)

    aneuploidy = surv_data["aneuploidy"]
    fga        = surv_data["fga"]
    msi_m      = surv_data["msi_mantis"]
    msi_s      = surv_data["msi_sensor"]

    # TV-6: r(AURKA, ANEUPLOIDY) > 0
    log(f"\n  TV-6: r(AURKA, ANEUPLOIDY) > 0")
    log(f"  Prediction: AURKA tracks CIN")
    if "AURKA" in df_expr.columns:
        rv, pv = safe_pearsonr(
            aneuploidy,
            df_expr["AURKA"].values,
        )
        log(f"  r(AURKA, ANEUPLOIDY) = "
            f"{rv:+.4f}  {fmt_p(pv)}")
        log(
            f"  {'TV-6 CONFIRMED ✓' if not np.isnan(rv) and rv>0 and pv<0.05 else 'TV-6 NOT CONFIRMED ✗'}"
        )
        # Also test FGA
        rv2, pv2 = safe_pearsonr(
            fga,
            df_expr["AURKA"].values,
        )
        log(f"  r(AURKA, FGA) = "
            f"{rv2:+.4f}  {fmt_p(pv2)}")

    # TV-7: r(ZEB2, ANEUPLOIDY) < 0
    log(f"\n  TV-7: r(ZEB2, ANEUPLOIDY) < 0")
    log(f"  Prediction: ZEB2 anti-tracks CIN")
    if "ZEB2" in df_expr.columns:
        rv, pv = safe_pearsonr(
            aneuploidy,
            df_expr["ZEB2"].values,
        )
        log(f"  r(ZEB2, ANEUPLOIDY) = "
            f"{rv:+.4f}  {fmt_p(pv)}")
        log(
            f"  {'TV-7 CONFIRMED ✓' if not np.isnan(rv) and rv<0 and pv<0.05 else 'TV-7 NOT CONFIRMED ✗'}"
        )

    # Comprehensive CIN correlations
    log(f"\n  All genes vs ANEUPLOIDY_SCORE:")
    log(f"  (top 10 positive and negative)")
    cin_corrs = []
    for gene in df_expr.columns:
        rv, pv = safe_pearsonr(
            aneuploidy,
            df_expr[gene].values,
        )
        if not np.isnan(rv):
            cin_corrs.append((gene, rv, pv))
    cin_corrs.sort(key=lambda x: x[1],
                   reverse=True)
    log(f"\n  TOP 10 POSITIVE (UP with CIN):")
    for g, r, p in cin_corrs[:10]:
        log(f"  {g:<12} r={r:+.4f}  "
            f"{fmt_p(p)}")
    log(f"\n  TOP 10 NEGATIVE (DOWN with CIN):")
    for g, r, p in cin_corrs[-10:][::-1]:
        log(f"  {g:<12} r={r:+.4f}  "
            f"{fmt_p(p)}")

    # TV-8: r(luminal depth, MSI) > 0
    log(f"\n  TV-8: r(luminal depth, MSI) > 0")
    log(f"  Prediction: deep luminal = MSI-high")
    lum_pos = [
        df_expr.index.get_loc(s)
        for s in lum.index
        if s in df_expr.index
    ]
    l_depth_full = np.full(
        len(df_expr), np.nan
    )
    for i, pos in enumerate(lum_pos):
        l_depth_full[pos] = (
            l_depth.values[i]
        )

    for msi_label, msi_arr in [
        ("MSI_SCORE_MANTIS", msi_m),
        ("MSI_SENSOR_SCORE", msi_s),
    ]:
        rv, pv = safe_pearsonr(
            l_depth_full, msi_arr
        )
        log(f"  r(luminal_depth, "
            f"{msi_label}) = "
            f"{rv:+.4f}  {fmt_p(pv)}")

    # Also test MSH2/MSH6 vs MSI
    log(f"\n  MSH2/MSH6 vs MSI scores:")
    for gene in ["MSH2","MSH6","MLH1"]:
        if gene not in df_expr.columns:
            continue
        for msi_label, msi_arr in [
            ("MANTIS", msi_m),
            ("SENSOR", msi_s),
        ]:
            rv, pv = safe_pearsonr(
                df_expr[gene].values, msi_arr
            )
            log(f"  r({gene}, {msi_label}) = "
                f"{rv:+.4f}  {fmt_p(pv)}")

    # TV-9: Subtype comparison
    log(f"\n  TV-9: SUBTYPE COMPARISON")
    log(f"  Our GATA3/KRT5 vs Robertson")
    subtype_pub = surv_data["subtype_pub"]
    pub_series  = pd.Series(
        subtype_pub, index=df_expr.index
    )
    unique_pub = [
        s for s in pub_series.unique()
        if s and s != "nan"
    ]
    log(f"  Published subtypes: {unique_pub}")

    if unique_pub:
        log(f"\n  Cross-tabulation:")
        log(f"  {'Our':>15}  {'Published':>25}")
        xtab = pd.crosstab(
            subtype.reindex(df_expr.index),
            pub_series,
        )
        log(xtab.to_string())

    # TV-10: FGA luminal vs basal
    log(f"\n  TV-10: FGA LUMINAL vs BASAL")
    log(f"  Prediction: luminal higher CIN")
    lum_fga = fga[lum_pos]
    bas_pos = [
        df_expr.index.get_loc(s)
        for s in bas.index
        if s in df_expr.index
    ]
    bas_fga = fga[bas_pos]
    valid_l = lum_fga[~np.isnan(lum_fga)]
    valid_b = bas_fga[~np.isnan(bas_fga)]
    if len(valid_l) > 5 and len(valid_b) > 5:
        _, p = safe_mwu(
            valid_l, valid_b, "two-sided"
        )
        log(f"  Luminal FGA mean = "
            f"{valid_l.mean():.3f}")
        log(f"  Basal   FGA mean = "
            f"{valid_b.mean():.3f}")
        log(f"  MWU: {fmt_p(p)}")
        if valid_l.mean() > valid_b.mean():
            log(f"  TV-10 CONFIRMED ✓ "
                f"(luminal > basal FGA)")
        else:
            log(f"  TV-10 NOT CONFIRMED ✗")

    # Aneuploidy vs depth correlations
    log(f"\n  ANEUPLOIDY vs DEPTH:")
    b_depth_full = np.full(
        len(df_expr), np.nan
    )
    for i, pos in enumerate(bas_pos):
        b_depth_full[pos] = (
            b_depth.values[i]
        )
    rv_l, pv_l = safe_pearsonr(
        aneuploidy, l_depth_full
    )
    rv_b, pv_b = safe_pearsonr(
        aneuploidy, b_depth_full
    )
    log(f"  r(aneuploidy, luminal_depth) = "
        f"{rv_l:+.4f}  {fmt_p(pv_l)}")
    log(f"  r(aneuploidy, basal_depth) = "
        f"{rv_b:+.4f}  {fmt_p(pv_b)}")

# ============================================================
# GENERATE FIGURE
# ============================================================

def generate_figure(
    lum, bas, l_depth, b_depth,
    results, surv_data, df_expr,
):
    log("")
    log("--- Generating Script 4 figure ---")

    fig = plt.figure(figsize=(28, 22))
    fig.suptitle(
        "Bladder Cancer — False Attractor "
        "Analysis\n"
        "Script 4 | TCGA-BLCA | "
        "Survival + CIN + MSI Validation\n"
        "OrganismCore | Doc 91d | 2026-03-01",
        fontsize=10, fontweight="bold",
        y=0.99,
    )

    gs_f = gridspec.GridSpec(
        3, 3, figure=fig,
        hspace=0.55, wspace=0.45,
    )

    COLORS = {
        "Luminal": "#2980b9",
        "Basal":   "#e74c3c",
        "Deep":    "#c0392b",
        "Shallow": "#27ae60",
    }

    def km_panel(ax, res, title):
        if res is None:
            ax.text(
                0.5, 0.5, "No data",
                ha="center", va="center",
                transform=ax.transAxes,
            )
            ax.set_title(title, fontsize=9)
            return
        t   = res["t"]
        e   = res["e"]
        hi  = res["hi"]
        lo  = res["lo"]
        p   = res["p_depth"]
        kmf = KaplanMeierFitter()
        kmf.fit(
            t[hi], e[hi],
            label=f"Deep (n={hi.sum()})",
        )
        kmf.plot_survival_function(
            ax=ax, color=COLORS["Deep"],
            ci_show=True, ci_alpha=0.1,
        )
        kmf.fit(
            t[lo], e[lo],
            label=f"Shallow (n={lo.sum()})",
        )
        kmf.plot_survival_function(
            ax=ax, color=COLORS["Shallow"],
            ci_show=True, ci_alpha=0.1,
        )
        p_str = (
            f"p={p:.4f}"
            if not np.isnan(p) else "N/A"
        )
        ax.set_title(
            f"{title}\n{p_str}", fontsize=9
        )
        ax.legend(fontsize=7)
        ax.set_xlabel("Time (months)",
                      fontsize=8)

    # A — KM Luminal OS
    ax_a = fig.add_subplot(gs_f[0, 0])
    km_panel(
        ax_a, results.get("lum_os"),
        "A — KM Luminal OS (TV-1)"
    )

    # B — KM Basal OS
    ax_b = fig.add_subplot(gs_f[0, 1])
    km_panel(
        ax_b, results.get("bas_os"),
        "B — KM Basal OS (TV-2)"
    )

    # C — KM Basal DSS
    ax_c = fig.add_subplot(gs_f[0, 2])
    km_panel(
        ax_c, results.get("bas_dss"),
        "C — KM Basal DSS (TV-5)"
    )

    # D — AURKA vs Aneuploidy
    ax_d = fig.add_subplot(gs_f[1, 0])
    aneuploidy = surv_data["aneuploidy"]
    if "AURKA" in df_expr.columns:
        valid = (
            np.isfinite(aneuploidy)
            & np.isfinite(
                df_expr["AURKA"].values
            )
        )
        ax_d.scatter(
            aneuploidy[valid],
            df_expr["AURKA"].values[valid],
            alpha=0.3, s=15, c="#2c3e50",
        )
        rv, _ = safe_pearsonr(
            aneuploidy, df_expr["AURKA"].values
        )
        ax_d.set_title(
            f"D — AURKA vs Aneuploidy\n"
            f"r={rv:+.3f} (TV-6)",
            fontsize=9,
        )
        ax_d.set_xlabel(
            "Aneuploidy score", fontsize=8
        )
        ax_d.set_ylabel("AURKA", fontsize=8)

    # E — ZEB2 vs Aneuploidy
    ax_e = fig.add_subplot(gs_f[1, 1])
    if "ZEB2" in df_expr.columns:
        valid = (
            np.isfinite(aneuploidy)
            & np.isfinite(
                df_expr["ZEB2"].values
            )
        )
        ax_e.scatter(
            aneuploidy[valid],
            df_expr["ZEB2"].values[valid],
            alpha=0.3, s=15, c="#8e44ad",
        )
        rv, _ = safe_pearsonr(
            aneuploidy, df_expr["ZEB2"].values
        )
        ax_e.set_title(
            f"E — ZEB2 vs Aneuploidy\n"
            f"r={rv:+.3f} (TV-7)",
            fontsize=9,
        )
        ax_e.set_xlabel(
            "Aneuploidy score", fontsize=8
        )
        ax_e.set_ylabel("ZEB2", fontsize=8)

    # F — Luminal depth vs MSI
    ax_f = fig.add_subplot(gs_f[1, 2])
    lum_pos = [
        df_expr.index.get_loc(s)
        for s in lum.index
        if s in df_expr.index
    ]
    l_depth_full = np.full(
        len(df_expr), np.nan
    )
    for i, pos in enumerate(lum_pos):
        l_depth_full[pos] = l_depth.values[i]
    msi_s = surv_data["msi_sensor"]
    valid = (
        np.isfinite(l_depth_full)
        & np.isfinite(msi_s)
    )
    if valid.sum() > 5:
        ax_f.scatter(
            l_depth_full[valid],
            msi_s[valid],
            alpha=0.3, s=15,
            c=COLORS["Luminal"],
        )
        rv, _ = safe_pearsonr(
            l_depth_full, msi_s
        )
        ax_f.set_title(
            f"F — Luminal Depth vs MSI\n"
            f"r={rv:+.3f} (TV-8 / NP-BLCA-2)",
            fontsize=9,
        )
        ax_f.set_xlabel(
            "Luminal depth", fontsize=8
        )
        ax_f.set_ylabel(
            "MSI sensor score", fontsize=8
        )
    else:
        ax_f.set_title(
            "F — Luminal Depth vs MSI (N/A)",
            fontsize=9,
        )

    # G — FGA luminal vs basal
    ax_g = fig.add_subplot(gs_f[2, 0])
    fga = surv_data["fga"]
    bas_pos = [
        df_expr.index.get_loc(s)
        for s in bas.index
        if s in df_expr.index
    ]
    lum_fga = fga[lum_pos]
    bas_fga = fga[bas_pos]
    data_g  = [
        lum_fga[~np.isnan(lum_fga)],
        bas_fga[~np.isnan(bas_fga)],
    ]
    bp = ax_g.boxplot(
        [d for d in data_g if len(d) > 0],
        patch_artist=True,
        medianprops=dict(
            color="black", linewidth=2
        ),
    )
    colors_g = [
        COLORS["Luminal"], COLORS["Basal"]
    ]
    labels_g = [
        f"Luminal\nn={len(data_g[0])}",
        f"Basal\nn={len(data_g[1])}",
    ]
    for patch, color in zip(
        bp["boxes"], colors_g
    ):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    ax_g.set_xticks(
        range(1, len(labels_g) + 1)
    )
    ax_g.set_xticklabels(
        labels_g, fontsize=8
    )
    ax_g.set_ylabel(
        "Fraction genome altered", fontsize=8
    )
    ax_g.set_title(
        "G — FGA Luminal vs Basal\n"
        "(TV-10 CIN comparison)",
        fontsize=9,
    )

    # H — Panel KM luminal
    ax_h = fig.add_subplot(gs_f[2, 1])
    lum_res = results.get("lum_os")
    if (
        lum_res is not None
        and lum_res.get("phi") is not None
    ):
        t   = lum_res["t"]
        e   = lum_res["e"]
        phi = lum_res["phi"]
        plo = lum_res["plo"]
        pp  = lum_res["p_panel"]
        kmf = KaplanMeierFitter()
        kmf.fit(
            t[phi], e[phi],
            label=f"High (n={phi.sum()})",
        )
        kmf.plot_survival_function(
            ax=ax_h, color="#8e44ad",
            ci_show=False,
        )
        kmf.fit(
            t[plo], e[plo],
            label=f"Low (n={plo.sum()})",
        )
        kmf.plot_survival_function(
            ax=ax_h, color="#f39c12",
            ci_show=False,
        )
        p_str = (
            f"p={pp:.4f}"
            if not np.isnan(pp) else "N/A"
        )
        ax_h.set_title(
            f"H — Panel FGFR3/CCND1/CLDN3\n"
            f"{p_str} (TV-3)",
            fontsize=9,
        )
        ax_h.legend(fontsize=7)
        ax_h.set_xlabel(
            "Time (months)", fontsize=8
        )
    else:
        ax_h.set_title(
            "H — Panel KM (not available)",
            fontsize=9,
        )

    # I — Summary
    ax_i = fig.add_subplot(gs_f[2, 2])
    ax_i.axis("off")

    def pstr(key):
        r = results.get(key)
        if r is None:
            return "N/A"
        p = r.get("p_depth", np.nan)
        return (
            f"{p:.4f}" if not np.isnan(p)
            else "N/A"
        )

    aneu_aurka = safe_pearsonr(
        aneuploidy,
        df_expr["AURKA"].values
        if "AURKA" in df_expr.columns
        else np.array([]),
    )[0]
    aneu_zeb2 = safe_pearsonr(
        aneuploidy,
        df_expr["ZEB2"].values
        if "ZEB2" in df_expr.columns
        else np.array([]),
    )[0]

    summary = (
        "I — SCRIPT 4 SUMMARY\n"
        "─────────────────────────────\n"
        "Dataset: TCGA-BLCA PanCan 2018\n"
        "Luminal=204 Basal=203\n"
        "Clinical: cBioPortal API\n\n"
        "SURVIVAL:\n"
        f"  Lum OS  p={pstr('lum_os')}\n"
        f"  Bas OS  p={pstr('bas_os')}\n"
        f"  Bas DSS p={pstr('bas_dss')}\n\n"
        "CIN/MSI:\n"
        f"  r(AURKA,aneuploidy)="
        f"{aneu_aurka:+.3f}\n"
        f"  r(ZEB2, aneuploidy)="
        f"{aneu_zeb2:+.3f}\n\n"
        "Framework: OrganismCore\n"
        "Doc 91d | 2026-03-01"
    )
    ax_i.text(
        0.03, 0.97, summary,
        transform=ax_i.transAxes,
        fontsize=7.5,
        verticalalignment="top",
        fontfamily="monospace",
        bbox=dict(
            boxstyle="round",
            facecolor="#f8f8f8",
            edgecolor="#cccccc",
        ),
    )

    out = os.path.join(
        RESULTS_DIR, "blca_tcga_s4.png"
    )
    plt.savefig(
        out, dpi=150, bbox_inches="tight"
    )
    log(f"\n  Figure saved: {out}")
    plt.close()

# ============================================================
# MAIN
# ============================================================

def main():
    log("=" * 65)
    log("BLADDER CANCER — SCRIPT 4")
    log("Dataset: TCGA-BLCA PanCan Atlas 2018")
    log("Clinical: cBioPortal (confirmed)")
    log("Framework: OrganismCore")
    log("Doc: 91d | Date: 2026-03-01")
    log("=" * 65)
    log("")
    log("PREDICTIONS LOCKED:")
    log("TV-1: Luminal depth predicts OS")
    log("TV-2: Basal depth predicts OS")
    log("TV-3: FGFR3/CCND1/CLDN3 panel OS")
    log("TV-4: TWIST1/CDK6/GATA3 panel OS")
    log("TV-5: Basal depth predicts DSS")
    log("TV-6: r(AURKA, aneuploidy) > 0")
    log("TV-7: r(ZEB2,  aneuploidy) < 0")
    log("TV-8: r(lum depth, MSI) > 0")
    log("TV-9: Our subtypes match Robertson")
    log("TV-10: Luminal FGA > Basal FGA")

    # Load expression
    df_expr = load_expr()
    if df_expr is None or len(df_expr) == 0:
        log("FATAL: Expression load failed")
        write_log()
        return

    # Load clinical
    clin_aligned = load_clinical(df_expr)
    if clin_aligned is None:
        log("FATAL: Clinical load failed")
        write_log()
        return

    # Parse survival vectors
    log("")
    log("=" * 65)
    log("PARSE SURVIVAL VECTORS")
    log("=" * 65)
    surv_data = parse_surv_vectors(
        clin_aligned
    )

    # Classify subtypes
    subtype = classify_subtypes(df_expr)
    lum = df_expr[subtype == "Luminal"]
    bas = df_expr[subtype == "Basal"]

    log("")
    log("=" * 65)
    log("GROUP SUMMARY")
    log("=" * 65)
    log(f"  Luminal: {len(lum)}")
    log(f"  Basal  : {len(bas)}")

    # Depth scores
    log("")
    log("=" * 65)
    log("DEPTH SCORES")
    log("=" * 65)
    l_depth = build_depth(
        lum, LUMINAL_SWITCH,
        LUMINAL_FA, "Luminal",
    )
    b_depth = build_depth(
        bas, BASAL_SWITCH,
        BASAL_FA, "Basal",
    )

    # Survival — positional alignment
    lum_pos = [
        df_expr.index.get_loc(s)
        for s in lum.index
        if s in df_expr.index
    ]
    bas_pos = [
        df_expr.index.get_loc(s)
        for s in bas.index
        if s in df_expr.index
    ]

    os_t  = surv_data["os_t"]
    os_e  = surv_data["os_e"]
    dss_t = surv_data["dss_t"]
    dss_e = surv_data["dss_e"]
    pfs_t = surv_data["pfs_t"]
    pfs_e = surv_data["pfs_e"]

    log("")
    log("=" * 65)
    log("SURVIVAL ANALYSIS")
    log("=" * 65)

    results = {}

    # Luminal OS (TV-1, TV-3)
    log("\n  === LUMINAL ===")
    results["lum_os"] = run_km(
        os_t[lum_pos], os_e[lum_pos],
        l_depth.values,
        "Luminal", "OS",
        panel_genes=["FGFR3","CCND1","CLDN3"],
        panel_dirs=["+","+","-"],
        df_v=lum,
    )

    # Luminal DSS
    results["lum_dss"] = run_km(
        dss_t[lum_pos], dss_e[lum_pos],
        l_depth.values,
        "Luminal", "DSS",
    )

    # Basal OS (TV-2, TV-4)
    log("\n  === BASAL ===")
    results["bas_os"] = run_km(
        os_t[bas_pos], os_e[bas_pos],
        b_depth.values,
        "Basal", "OS",
        panel_genes=["TWIST1","CDK6","GATA3"],
        panel_dirs=["+","+","-"],
        df_v=bas,
    )

    # Basal DSS (TV-5)
    results["bas_dss"] = run_km(
        dss_t[bas_pos], dss_e[bas_pos],
        b_depth.values,
        "Basal", "DSS",
    )

    # Basal PFS
    results["bas_pfs"] = run_km(
        pfs_t[bas_pos], pfs_e[bas_pos],
        b_depth.values,
        "Basal", "PFS",
    )

    # Summary
    log("")
    log("=" * 65)
    log("SURVIVAL PREDICTION SUMMARY")
    log("=" * 65)
    for pred, key, label in [
        ("TV-1", "lum_os",  "Luminal OS"),
        ("TV-2", "bas_os",  "Basal OS"),
        ("TV-5", "bas_dss", "Basal DSS"),
    ]:
        r = results.get(key)
        if r is None:
            log(f"  {pred}: {label} — "
                f"NO DATA")
            continue
        p = r.get("p_depth", np.nan)
        conf = (
            "CONFIRMED ✓"
            if not np.isnan(p) and p < 0.05
            else "NOT CONFIRMED ✗"
        )
        log(f"  {pred}: {label} — "
            f"{fmt_p(p)}  {conf}")

    for pred, key, label in [
        ("TV-3", "lum_os",  "Luminal panel"),
        ("TV-4", "bas_os",  "Basal panel"),
    ]:
        r = results.get(key)
        if r is None:
            continue
        p = r.get("p_panel", np.nan)
        conf = (
            "CONFIRMED ✓"
            if not np.isnan(p) and p < 0.05
            else "NOT CONFIRMED ✗"
        )
        log(f"  {pred}: {label} — "
            f"{fmt_p(p)}  {conf}")

    # CIN/MSI tests
    cin_msi_tests(
        lum, bas, l_depth, b_depth,
        surv_data, df_expr, subtype,
    )

    # Figure
    generate_figure(
        lum, bas, l_depth, b_depth,
        results, surv_data, df_expr,
    )

    # Save depth scores
    for label, depth_ in [
        ("luminal", l_depth),
        ("basal",   b_depth),
    ]:
        depth_.to_csv(
            os.path.join(
                RESULTS_DIR,
                f"depth_s4_{label}.csv",
            ),
            header=[f"depth_s4_{label}"],
        )

    write_log()
    log(f"\n  Log    : {LOG_FILE}")
    log(f"  Output : {RESULTS_DIR}")
    log("\n=== SCRIPT 4 COMPLETE ===")
    log("\nPaste full output for Document 91d.")


if __name__ == "__main__":
    main()
