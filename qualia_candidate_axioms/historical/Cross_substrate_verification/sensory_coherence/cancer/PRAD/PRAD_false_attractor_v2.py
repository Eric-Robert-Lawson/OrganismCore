"""
Prostate Adenocarcinoma — False Attractor Analysis
SCRIPT 2 — CIRCUIT ANALYSIS
Dataset: GSE32571

REQUIRES: gene_matrix.csv saved by Script 1
If not present: Script 1 will be re-run
to generate it.

SCRIPT 2 OBJECTIVES:
  1. GAP ANALYSIS — circuit connections
  2. ERG SUBTYPE ANALYSIS
  3. 3-GENE SCORE (ACPP + HOXC6 + AMACR)
  4. NKX3-1 FUNCTION GAP
  5. FOXA1 CIRCUIT ARCHITECTURE

Author: Eric Robert Lawson
Framework: OrganismCore Principles-First
Doc: 88b | Date: 2026-03-01
"""

import os
import sys
import gzip
import urllib.request
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

BASE_DIR    = "./prad_false_attractor/"
RESULTS_DIR = os.path.join(BASE_DIR, "results")
S2_DIR      = os.path.join(BASE_DIR,
                            "results_s2")
LOG_FILE    = os.path.join(S2_DIR,
                            "s2_log.txt")

os.makedirs(S2_DIR, exist_ok=True)

# Script 1 outputs
GENE_MATRIX = os.path.join(
    RESULTS_DIR, "gene_matrix.csv"
)
S1_META = os.path.join(
    RESULTS_DIR, "metadata.csv"
)
MATRIX_RAW = os.path.join(
    BASE_DIR,
    "GSE32571_non_normalized.txt.gz"
)

# ERG threshold from Script 1
ERG_THRESHOLD = 6.4804

# GEO annotation URL
ANNOT_URL = (
    "https://ftp.ncbi.nlm.nih.gov/geo/"
    "platforms/GPL10nnn/GPL10558/annot/"
    "GPL10558.annot.gz"
)
META_URL = (
    "https://www.ncbi.nlm.nih.gov/geo/"
    "query/acc.cgi?acc=GSE32571"
    "&targ=gsm&form=text&view=full"
)

# ============================================================
# GENE PANELS
# ============================================================

SWITCH_GENES = [
    "NKX3-1", "FOXA1", "KLK3",
    "ACPP", "KLK2", "MSMB",
]
FA_MARKERS = [
    "ERG", "MKI67", "EZH2",
    "HOXC6", "AMACR",
]
EPIGENETIC = [
    "EZH2", "EED", "SUZ12",
    "KDM6A", "DNMT3A", "BMI1", "JARID2",
]
AR_AXIS = [
    "AR", "KLK3", "KLK2",
    "TMPRSS2", "FKBP5", "STEAP2",
    "NKX3-1", "FOXA1",
]
SCAFFOLD = [
    "MYC", "CCND1", "CDK4",
    "CDK6", "RB1", "PTEN", "TP53",
]
LUMINAL = [
    "KRT8", "KRT18", "KRT19",
    "CDH1", "EPCAM", "HOXB13",
    "GATA2", "GATA3",
]
BASAL = [
    "KRT5", "KRT14", "TP63",
    "CD44", "ITGA6", "NGFR",
]
EMT = [
    "VIM", "CDH2", "SNAI1",
    "SNAI2", "TWIST1", "FN1",
]
ERG_PROGRAM = [
    "ERG", "ETV1", "ETV4",
    "ETV5", "SPDEF",
]
NEUROENDOCRINE = [
    "CHGA", "SYP", "ENO2",
    "NCAM1", "AURKA", "SOX2",
]
PROGNOSIS = [
    "MKI67", "PCNA", "TOP2A",
    "AURKA", "PLK1",
]

ALL_TARGET = list(dict.fromkeys(
    SWITCH_GENES + FA_MARKERS +
    EPIGENETIC + AR_AXIS + SCAFFOLD +
    LUMINAL + BASAL + EMT +
    ERG_PROGRAM + NEUROENDOCRINE +
    PROGNOSIS
))

CIRCUIT_CONNECTIONS = [
    ("AR",     "FOXA1",  "+",
     "AR drives FOXA1"),
    ("AR",     "KLK3",   "+",
     "AR drives KLK3/PSA"),
    ("AR",     "NKX3-1", "+",
     "AR drives NKX3-1"),
    ("AR",     "TMPRSS2","+",
     "AR drives TMPRSS2"),
    ("FOXA1",  "AR",     "+",
     "FOXA1 co-activates AR"),
    ("FOXA1",  "AMACR",  "+",
     "FOXA1 drives AMACR?"),
    ("FOXA1",  "HOXC6",  "+",
     "FOXA1 drives HOXC6?"),
    ("FOXA1",  "EZH2",   "+",
     "FOXA1 drives EZH2?"),
    ("EZH2",   "ACPP",   "-",
     "EZH2 silences ACPP"),
    ("EZH2",   "MSMB",   "-",
     "EZH2 silences MSMB"),
    ("EZH2",   "NKX3-1", "-",
     "EZH2 silences NKX3-1"),
    ("EZH2",   "KLK3",   "-",
     "EZH2 silences KLK3"),
    ("NKX3-1", "ACPP",   "+",
     "NKX3-1 → ACPP intact?"),
    ("NKX3-1", "MSMB",   "+",
     "NKX3-1 → MSMB intact?"),
    ("NKX3-1", "KLK3",   "+",
     "NKX3-1 → KLK3 intact?"),
    ("MYC",    "MKI67",  "+",
     "MYC drives proliferation"),
    ("MYC",    "CDK4",   "+",
     "MYC drives CDK4"),
    ("AURKA",  "MKI67",  "+",
     "AURKA tracks proliferation"),
    ("EZH2",   "TP63",   "-",
     "EZH2 silences TP63?"),
    ("EZH2",   "KRT5",   "-",
     "EZH2 silences KRT5?"),
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

# ============================================================
# FETCH HELPER
# ============================================================

def fetch_url(url, timeout=30):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(
        req, timeout=timeout
    ) as r:
        return r.read()

# ============================================================
# STEP 0: BUILD GENE MATRIX
# Try to load from Script 1 output.
# If not found, rebuild from raw matrix
# using annotation CSV.
# ============================================================

def build_gene_matrix():
    log("=" * 65)
    log("STEP 0: GENE MATRIX")
    log("=" * 65)

    # Try to load pre-built gene matrix
    if os.path.exists(GENE_MATRIX):
        log(f"  Loading Script 1 output: "
            f"{GENE_MATRIX}")
        gdf = pd.read_csv(
            GENE_MATRIX, index_col=0
        )
        log(f"  Loaded: {gdf.shape} "
            f"(genes x samples)")
        return gdf

    # Not found — rebuild from raw
    log("  gene_matrix.csv not found.")
    log("  Rebuilding from raw matrix...")
    log("  (Add save step to Script 1 to")
    log("   avoid this in future runs)")

    # Load raw matrix
    log(f"\n  Loading raw matrix...")
    with gzip.open(MATRIX_RAW, "rt") as f:
        df = pd.read_csv(
            f, sep="\t", index_col=0,
            low_memory=False
        )
    log(f"  Raw shape: {df.shape}")

    expr_cols = [
        c for c in df.columns
        if "detection" not in c.lower()
        and "pval" not in c.lower()
    ]
    pval_cols = [
        c for c in df.columns
        if "detection" in c.lower()
        or "pval" in c.lower()
    ]

    expr_df = df[expr_cols].apply(
        pd.to_numeric, errors="coerce"
    )

    if pval_cols:
        pval_df = df[pval_cols].apply(
            pd.to_numeric, errors="coerce"
        )
        detected   = (pval_df < 0.05).sum(axis=1)
        min_detect = max(
            3, int(len(pval_cols) * 0.20)
        )
        expr_df = expr_df[
            detected >= min_detect
        ]

    expr_df = expr_df.clip(lower=1.0)
    expr_df = np.log2(expr_df)

    # Quantile normalize
    log("  Quantile normalizing...")
    arr      = expr_df.values.copy()
    sort_arr = np.sort(arr, axis=0)
    mean_ref = sort_arr.mean(axis=1)
    rank_idx = np.argsort(
        np.argsort(arr, axis=0), axis=0
    )
    norm_arr = mean_ref[rank_idx]
    expr_df  = pd.DataFrame(
        norm_arr,
        index=expr_df.index,
        columns=expr_df.columns,
    )
    log(f"  Normalized: {expr_df.shape}")

    # Probe mapping — download annotation
    probe_ids = set(expr_df.index)
    log("\n  Downloading annotation CSV...")

    try:
        raw = fetch_url(ANNOT_URL, timeout=60)
        log(f"  Downloaded: "
            f"{len(raw)/1e6:.1f} MB")

        import io as _io
        with gzip.open(
            _io.BytesIO(raw), "rt"
        ) as gz:
            lines = gz.readlines()

        in_t = False
        cols = None
        ic = sc = None
        mapped = {}

        for line in lines:
            line = line.rstrip()
            if "platform_table_begin" in line:
                in_t = True
                cols = None
                continue
            if "platform_table_end" in line:
                break
            if not in_t:
                continue
            parts = line.split("\t")
            if cols is None:
                cols = parts
                for i, c in enumerate(cols):
                    cl = c.lower()
                    if cl == "id":
                        ic = i
                    if cl in [
                        "gene symbol",
                        "symbol",
                        "gene_symbol",
                    ]:
                        sc = i
                log(f"  Annotation cols: "
                    f"{cols[:6]}")
                log(f"  id_col={ic} "
                    f"sym_col={sc}")
                continue
            if (ic is not None
                    and sc is not None
                    and len(parts)
                    > max(ic, sc)):
                p = parts[ic].strip()
                s = parts[sc].strip()
                if (p and s
                        and "///" not in s
                        and s != "---"
                        and p in probe_ids):
                    mapped[p] = s.split(" ")[0]

        log(f"  Mapped probes: {len(mapped)}")

    except Exception as e:
        log(f"  Annotation download error: {e}")
        log("  Falling back to hard-coded map")
        mapped = {
            p: g
            for p, g in {
                "ILMN_1766707": "NKX3-1",
                "ILMN_1718800": "NKX3-1",
                "ILMN_2337565": "FOXA1",
                "ILMN_1679881": "FOXA1",
                "ILMN_1773275": "KLK3",
                "ILMN_2388574": "KLK3",
                "ILMN_1811083": "ACPP",
                "ILMN_1788078": "KLK2",
                "ILMN_1788866": "MSMB",
                "ILMN_2147486": "MSMB",
                "ILMN_2338729": "ERG",
                "ILMN_1766526": "ERG",
                "ILMN_1806487": "MKI67",
                "ILMN_2413324": "MKI67",
                "ILMN_1688580": "EZH2",
                "ILMN_1795529": "EZH2",
                "ILMN_1712966": "HOXC6",
                "ILMN_1793626": "AMACR",
                "ILMN_1669115": "AMACR",
                "ILMN_2136659": "EED",
                "ILMN_1739177": "SUZ12",
                "ILMN_1778439": "KDM6A",
                "ILMN_1700949": "DNMT3A",
                "ILMN_1670195": "BMI1",
                "ILMN_1786314": "JARID2",
                "ILMN_1701183": "AR",
                "ILMN_2377461": "AR",
                "ILMN_1786475": "TMPRSS2",
                "ILMN_2184373": "TMPRSS2",
                "ILMN_1705169": "FKBP5",
                "ILMN_1788660": "STEAP2",
                "ILMN_1674999": "MYC",
                "ILMN_2348918": "MYC",
                "ILMN_1697622": "CCND1",
                "ILMN_1738801": "CDK4",
                "ILMN_1698467": "CDK6",
                "ILMN_1776507": "RB1",
                "ILMN_2185948": "PTEN",
                "ILMN_2402257": "TP53",
                "ILMN_1688895": "KRT8",
                "ILMN_1711192": "KRT18",
                "ILMN_1765851": "KRT19",
                "ILMN_1791210": "CDH1",
                "ILMN_1668111": "EPCAM",
                "ILMN_2387561": "HOXB13",
                "ILMN_1714588": "GATA2",
                "ILMN_2341949": "GATA3",
                "ILMN_1779323": "KRT5",
                "ILMN_1713464": "KRT14",
                "ILMN_1692128": "TP63",
                "ILMN_2383725": "CD44",
                "ILMN_2364093": "ITGA6",
                "ILMN_1699012": "NGFR",
                "ILMN_1777688": "VIM",
                "ILMN_1714228": "CDH2",
                "ILMN_1697281": "SNAI1",
                "ILMN_1693140": "SNAI2",
                "ILMN_1779677": "ZEB1",
                "ILMN_1796316": "TWIST1",
                "ILMN_1766619": "FN1",
                "ILMN_1772887": "ETV1",
                "ILMN_1668770": "ETV4",
                "ILMN_1791861": "ETV5",
                "ILMN_1715210": "SPDEF",
                "ILMN_1683121": "CHGA",
                "ILMN_1791735": "SYP",
                "ILMN_1770337": "ENO2",
                "ILMN_1808680": "NCAM1",
                "ILMN_1681538": "AURKA",
                "ILMN_1745538": "MYCN",
                "ILMN_1736783": "SOX2",
                "ILMN_1698404": "PCNA",
                "ILMN_1751278": "TOP2A",
                "ILMN_1762653": "PLK1",
                "ILMN_1741308": "BUB1B",
            }.items()
            if p in probe_ids
        }
        log(f"  Hard-coded hits: {len(mapped)}")

    if len(mapped) < 5:
        log("  CRITICAL: Too few probes mapped")
        log("  Check probe ID format:")
        log(f"  {list(expr_df.index[:5])}")
        sys.exit(1)

    # Build gene matrix
    sub = expr_df.loc[
        [p for p in mapped
         if p in expr_df.index]
    ].copy()
    sub["symbol"] = [
        mapped[p] for p in sub.index
    ]
    sub["mean_expr"] = \
        sub.drop(columns=["symbol"]).mean(axis=1)
    sub = sub.sort_values(
        "mean_expr", ascending=False
    )
    sub = sub.drop_duplicates(
        subset=["symbol"], keep="first"
    )
    syms = sub["symbol"].values
    sub  = sub.drop(
        columns=["symbol", "mean_expr"]
    )
    sub.index = syms

    log(f"  Genes: {len(sub)}")

    # Save for future use
    sub.to_csv(GENE_MATRIX)
    log(f"  Saved: {GENE_MATRIX}")
    log("  (Script 1 should also save this)")

    found = [g for g in ALL_TARGET
             if g in sub.index]
    miss  = [g for g in ALL_TARGET
             if g not in sub.index]
    log(f"  Target genes: "
        f"{len(found)}/{len(ALL_TARGET)}")
    if miss:
        log(f"  Missing: {miss[:10]}")

    return sub

# ============================================================
# STEP 1: CLASSIFY SAMPLES
# ============================================================

def classify_samples(gene_df):
    log("")
    log("--- Classifying samples ---")

    meta = pd.read_csv(S1_META, index_col=0)

    def extract_dkfz(title):
        parts = str(title).split("_")
        for i, p in enumerate(parts):
            if p.upper() == "DKFZ" \
                    and i + 1 < len(parts):
                return f"DKFZ_{parts[i+1]}"
        return title

    meta["sample_id"] = \
        meta["title"].apply(extract_dkfz)

    meta_cols = [c for c in [
        "disease_stage",
        "gleason_pattern_group",
        "source",
    ] if c in meta.columns]

    expr_T  = gene_df.T
    merged  = expr_T.join(
        meta.set_index(
            "sample_id"
        )[meta_cols],
        how="left",
    )
    merged["group"] = "UNKNOWN"

    if "disease_stage" in merged.columns:
        ds = merged[
            "disease_stage"
        ].fillna("").str.lower()
        merged.loc[
            ds.str.contains("cancer|tumor"),
            "group"
        ] = "TUMOR"
        merged.loc[
            ds.str.contains("benign|normal"),
            "group"
        ] = "NORMAL"

    for idx in merged[
        merged["group"] == "UNKNOWN"
    ].index:
        il = str(idx).lower()
        if "tumor" in il or "cancer" in il:
            merged.loc[idx, "group"] = "TUMOR"
        elif "benign" in il or "normal" in il:
            merged.loc[idx, "group"] = "NORMAL"

    tumor  = merged[
        merged["group"] == "TUMOR"
    ].copy()
    normal = merged[
        merged["group"] == "NORMAL"
    ].copy()

    log(f"  TUMOR  : {len(tumor)}")
    log(f"  NORMAL : {len(normal)}")

    if "gleason_pattern_group" in tumor.columns:
        gc = tumor[
            "gleason_pattern_group"
        ].value_counts()
        log(f"  Gleason: {dict(gc)}")

    return merged, tumor, normal

# ============================================================
# STEP 2: BUILD DEPTH + ERG STATUS
# ============================================================

def build_depth_erg(tumor):
    log("")
    log("--- Building depth score ---")

    gene_cols = [
        c for c in tumor.columns
        if c in ALL_TARGET
    ]

    def norm01(s):
        mn, mx = s.min(), s.max()
        return (
            (s - mn) / (mx - mn)
            if mx > mn
            else pd.Series(0.0, index=s.index)
        )

    sw_avail = [
        g for g in SWITCH_GENES
        if g in gene_cols
    ]
    fa_avail = [
        g for g in FA_MARKERS
        if g in gene_cols
    ]

    log(f"  Switch genes: {sw_avail}")
    log(f"  FA markers  : {fa_avail}")

    tumor  = tumor.copy()
    depth  = pd.Series(
        np.zeros(len(tumor)), index=tumor.index
    )
    comp   = 0
    if sw_avail:
        depth += (
            1 - norm01(
                tumor[sw_avail].mean(axis=1)
            )
        )
        comp += 1
    if fa_avail:
        depth += norm01(
            tumor[fa_avail].mean(axis=1)
        )
        comp += 1
    if comp > 0:
        depth /= comp

    tumor["block_depth"] = depth.values
    log(f"  Depth mean : {depth.mean():.4f}")
    log(f"  Depth std  : {depth.std():.4f}")

    # ERG status
    if "ERG" in gene_cols:
        erg_vals = tumor["ERG"].values
        try:
            kde  = gaussian_kde(erg_vals)
            xs   = np.linspace(
                erg_vals.min(),
                erg_vals.max(), 300
            )
            ys   = kde(xs)
            mins = argrelmin(ys, order=8)[0]
            if len(mins) > 0:
                thr = xs[mins[0]]
            else:
                thr = ERG_THRESHOLD
        except Exception:
            thr = ERG_THRESHOLD

        log(f"  ERG threshold: {thr:.4f}")
        tumor["erg_status"] = np.where(
            tumor["ERG"] > thr,
            "ERG_high", "ERG_low"
        )
        log(f"  ERG-high: "
            f"{(tumor['erg_status']=='ERG_high').sum()}")
        log(f"  ERG-low : "
            f"{(tumor['erg_status']=='ERG_low').sum()}")

    return tumor

# ============================================================
# ANALYSIS 1: GAP ANALYSIS
# ============================================================

def gap_analysis(tumor):
    log("")
    log("=" * 65)
    log("ANALYSIS 1: GAP ANALYSIS")
    log("Testing circuit connections")
    log("=" * 65)
    log("")
    log("  KEY ARCHITECTURAL QUESTION:")
    log("  NKX3-1→ACPP circuit:")
    log("  INTACT (like PAAD PTF1A→CTRC"
        " r=+0.754)")
    log("  OR BROKEN (like MDS CEBPE→ELANE"
        " r=+0.07)?")
    log("")

    gene_cols = [
        c for c in tumor.columns
        if c in ALL_TARGET
    ]
    avail = set(gene_cols)

    confirmed = []
    not_conf  = []
    missing   = []

    log(f"  {'Connection':<28} "
        f"{'r':>8}  {'p':>12}  "
        f"{'Dir':>5}  Result")
    log(f"  {'-'*72}")

    for ga, gb, direction, desc \
            in CIRCUIT_CONNECTIONS:
        if ga not in avail \
                or gb not in avail:
            missing.append((ga, gb))
            log(f"  {ga}→{gb:<24} MISSING")
            continue

        rv, pv = stats.pearsonr(
            tumor[ga].values,
            tumor[gb].values,
        )
        expected = (
            (direction == "+" and rv > 0)
            or (direction == "-" and rv < 0)
        )
        sig    = pv < 0.05
        result = (
            "CONFIRMED"
            if sig and expected
            else "NOT CONFIRMED"
            if not sig
            else "WRONG DIR"
        )
        stars = (
            "***" if pv < 0.001
            else "**" if pv < 0.01
            else "*" if pv < 0.05
            else "ns"
        )
        conn = f"{ga}→{gb}"
        log(f"  {conn:<28} "
            f"{rv:>+8.4f}  "
            f"p={pv:.2e} {stars}  "
            f"exp{direction}  "
            f"{result}")

        if result == "CONFIRMED":
            confirmed.append(
                (ga, gb, rv, pv, desc)
            )
        else:
            not_conf.append(
                (ga, gb, rv, pv, desc)
            )

    log(f"\n  CONFIRMED    : {len(confirmed)}")
    log(f"  NOT CONFIRMED: {len(not_conf)}")
    log(f"  MISSING      : {len(missing)}")

    nkx_acpp = next(
        (
            (rv, pv)
            for ga, gb, rv, pv, _
            in confirmed + not_conf
            if ga == "NKX3-1" and gb == "ACPP"
        ),
        None,
    )
    if nkx_acpp:
        rv, pv = nkx_acpp
        if rv > 0.3 and pv < 0.05:
            log(f"\n  NKX3-1→ACPP: r={rv:+.4f}")
            log(f"  Architecture: INTACT")
            log(f"  Like PAAD PTF1A→CTRC")
            log(f"  Block at NKX3-1 INPUT")
        elif abs(rv) < 0.15:
            log(f"\n  NKX3-1→ACPP: r={rv:+.4f}")
            log(f"  Architecture: BROKEN")
            log(f"  Like MDS CEBPE→ELANE")
        else:
            log(f"\n  NKX3-1→ACPP: r={rv:+.4f}")
            log(f"  Architecture: PARTIAL")

    return confirmed, not_conf

# ============================================================
# ANALYSIS 2: ERG SUBTYPE
# ============================================================

def erg_subtype_analysis(tumor):
    log("")
    log("=" * 65)
    log("ANALYSIS 2: ERG SUBTYPE")
    log("ERG-high vs ERG-low")
    log("=" * 65)

    if "erg_status" not in tumor.columns:
        log("  ERG status not available")
        return tumor

    gene_cols = [
        c for c in tumor.columns
        if c in ALL_TARGET
    ]

    erg_hi = tumor[
        tumor["erg_status"] == "ERG_high"
    ]
    erg_lo = tumor[
        tumor["erg_status"] == "ERG_low"
    ]
    log(f"  ERG-high: n={len(erg_hi)}")
    log(f"  ERG-low : n={len(erg_lo)}")

    # Depth by ERG
    if "block_depth" in tumor.columns:
        dh = erg_hi["block_depth"]
        dl = erg_lo["block_depth"]
        log(f"\n  Depth by ERG:")
        log(f"    ERG-high: "
            f"{dh.mean():.4f} "
            f"± {dh.std():.4f}")
        log(f"    ERG-low : "
            f"{dl.mean():.4f} "
            f"± {dl.std():.4f}")
        if len(dh) > 3 and len(dl) > 3:
            _, pv = stats.mannwhitneyu(
                dh, dl, alternative="two-sided"
            )
            log(f"    p={pv:.4f} "
                f"({'different' if pv < 0.05 else 'similar'})")

    # Key genes
    key = [g for g in [
        "ACPP", "MSMB", "HOXC6", "AMACR",
        "NKX3-1", "FOXA1", "KLK3", "AR",
        "TMPRSS2", "MYC", "EZH2", "MKI67",
        "TP63", "KRT5", "PTEN",
    ] if g in gene_cols]

    log(f"\n  {'Gene':<12} "
        f"{'ERG-hi':>9} "
        f"{'ERG-lo':>9} "
        f"{'Chg':>8}  p")
    log(f"  {'-'*50}")

    erg_out = []
    for g in key:
        hv  = erg_hi[g].values
        lv  = erg_lo[g].values
        hm  = hv.mean()
        lm  = lv.mean()
        chg = (
            (hm - lm) / lm * 100
            if lm > 0.0001 else np.nan
        )
        _, pv = stats.mannwhitneyu(
            hv, lv, alternative="two-sided"
        )
        cs    = (f"{chg:+.1f}%"
                 if not np.isnan(chg) else "N/A")
        stars = (
            "***" if pv < 0.001
            else "**" if pv < 0.01
            else "*" if pv < 0.05
            else "ns"
        )
        log(f"  {g:<12} "
            f"{hm:>9.4f} "
            f"{lm:>9.4f} "
            f"{cs:>8}  "
            f"p={pv:.2e} {stars}")
        erg_out.append({
            "gene": g, "erg_hi": hm,
            "erg_lo": lm, "change": chg,
            "p": pv,
        })

    pd.DataFrame(erg_out).to_csv(
        os.path.join(S2_DIR, "erg_results.csv"),
        index=False,
    )

    if "gleason_pattern_group" in tumor.columns:
        log(f"\n  Gleason by ERG:")
        for st in ["ERG_high", "ERG_low"]:
            sub = tumor[
                tumor["erg_status"] == st
            ]
            gc = sub[
                "gleason_pattern_group"
            ].value_counts()
            log(f"    {st}: {dict(gc)}")

    return tumor

# ============================================================
# ANALYSIS 3: 3-GENE SCORE
# ============================================================

def three_gene_score(tumor):
    log("")
    log("=" * 65)
    log("ANALYSIS 3: 3-GENE ATTRACTOR SCORE")
    log("ACPP (switch) + HOXC6 + AMACR")
    log("=" * 65)

    gene_cols = [
        c for c in tumor.columns
        if c in ALL_TARGET
    ]
    avail = [
        g for g in ["ACPP", "HOXC6", "AMACR"]
        if g in gene_cols
    ]
    log(f"  Available: {avail}")

    if len(avail) < 2:
        log("  Insufficient genes — skip")
        return tumor

    tumor = tumor.copy()

    def norm01(s):
        mn, mx = s.min(), s.max()
        return (
            (s - mn) / (mx - mn)
            if mx > mn
            else pd.Series(0.0, index=s.index)
        )

    score = pd.Series(
        np.zeros(len(tumor)), index=tumor.index
    )
    n = 0
    if "ACPP" in gene_cols:
        score += (1 - norm01(tumor["ACPP"]))
        n += 1
    if "HOXC6" in gene_cols:
        score += norm01(tumor["HOXC6"])
        n += 1
    if "AMACR" in gene_cols:
        score += norm01(tumor["AMACR"])
        n += 1
    score /= n
    tumor["score_3gene"] = score.values

    log(f"\n  3-gene score:")
    log(f"    Mean  : {score.mean():.4f}")
    log(f"    Median: {score.median():.4f}")
    log(f"    Std   : {score.std():.4f}")

    if "block_depth" in tumor.columns:
        rv, pv = stats.pearsonr(
            tumor["block_depth"].values,
            score.values,
        )
        log(f"\n  3-gene vs block_depth:")
        log(f"    r={rv:+.4f}  p={pv:.2e}")
        agr = (
            "STRONG" if abs(rv) > 0.7
            else "MODERATE" if abs(rv) > 0.5
            else "WEAK"
        )
        log(f"    Agreement: {agr}")

    if "gleason_pattern_group" in tumor.columns:
        hi = tumor[
            tumor["gleason_pattern_group"]
            == "high"
        ]["score_3gene"]
        lo = tumor[
            tumor["gleason_pattern_group"]
            == "low"
        ]["score_3gene"]
        if len(hi) > 3 and len(lo) > 3:
            log(f"\n  3-gene by Gleason:")
            log(f"    High: "
                f"{hi.mean():.4f} "
                f"± {hi.std():.4f} "
                f"(n={len(hi)})")
            log(f"    Low : "
                f"{lo.mean():.4f} "
                f"± {lo.std():.4f} "
                f"(n={len(lo)})")
            _, p3 = stats.mannwhitneyu(
                hi, lo, alternative="greater"
            )
            log(f"    High > Low: p={p3:.4f}  "
                f"{'CONFIRMED' if p3 < 0.05 else 'NOT CONFIRMED'}")

    if "erg_status" in tumor.columns:
        eh = tumor[
            tumor["erg_status"] == "ERG_high"
        ]["score_3gene"]
        el = tumor[
            tumor["erg_status"] == "ERG_low"
        ]["score_3gene"]
        if len(eh) > 3 and len(el) > 3:
            log(f"\n  3-gene by ERG:")
            log(f"    ERG-high: "
                f"{eh.mean():.4f} "
                f"± {eh.std():.4f}")
            log(f"    ERG-low : "
                f"{el.mean():.4f} "
                f"± {el.std():.4f}")
            _, pe = stats.mannwhitneyu(
                eh, el, alternative="two-sided"
            )
            log(f"    p={pe:.4f}")

    return tumor

# ============================================================
# ANALYSIS 4: NKX3-1 FUNCTION GAP
# ============================================================

def nkx31_function_gap(tumor):
    log("")
    log("=" * 65)
    log("ANALYSIS 4: NKX3-1 FUNCTION GAP")
    log("NKX3-1→terminal genes: INTACT or BROKEN?")
    log("=" * 65)
    log("")
    log("  References:")
    log("  PAAD: PTF1A→CTRC  r=+0.754  INTACT")
    log("  MDS:  CEBPE→ELANE r=+0.07   BROKEN")

    gene_cols = [
        c for c in tumor.columns
        if c in ALL_TARGET
    ]

    targets = [
        ("ACPP",   "terminal secretory"),
        ("MSMB",   "terminal secretory"),
        ("KLK3",   "AR-target secretory"),
        ("KLK2",   "AR-target secretory"),
        ("HOXB13", "luminal identity"),
    ]

    log(f"\n  NKX3-1 → target:")
    log(f"  {'Target':<10} {'r':>8}  "
        f"{'p':>12}  Architecture")
    log(f"  {'-'*50}")

    arch = {}
    if "NKX3-1" not in gene_cols:
        log("  NKX3-1 not in gene matrix")
    else:
        for tgt, desc in targets:
            if tgt not in gene_cols:
                log(f"  {tgt:<10} MISSING")
                continue
            rv, pv = stats.pearsonr(
                tumor["NKX3-1"].values,
                tumor[tgt].values,
            )
            if rv > 0.3 and pv < 0.05:
                label = "INTACT"
            elif abs(rv) < 0.15:
                label = "BROKEN"
            else:
                label = "PARTIAL"
            stars = (
                "***" if pv < 0.001
                else "**" if pv < 0.01
                else "*" if pv < 0.05
                else "ns"
            )
            log(f"  {tgt:<10} {rv:>+8.4f}  "
                f"p={pv:.2e} {stars}  "
                f"{label}")
            arch[tgt] = (rv, pv, label)

    log(f"\n  EZH2 → target:")
    log(f"  {'Target':<10} {'r':>8}  "
        f"{'p':>12}  Role")
    log(f"  {'-'*50}")
    if "EZH2" in gene_cols:
        for tgt, desc in targets:
            if tgt not in gene_cols:
                continue
            rv, pv = stats.pearsonr(
                tumor["EZH2"].values,
                tumor[tgt].values,
            )
            role = (
                "EZH2 SUPPRESSES"
                if rv < -0.2 and pv < 0.05
                else "EZH2 ACTIVATES"
                if rv > 0.2 and pv < 0.05
                else "no relationship"
            )
            stars = (
                "***" if pv < 0.001
                else "**" if pv < 0.01
                else "*" if pv < 0.05
                else "ns"
            )
            log(f"  {tgt:<10} {rv:>+8.4f}  "
                f"p={pv:.2e} {stars}  {role}")

    n_intact  = sum(
        1 for v in arch.values()
        if "INTACT" in v[2]
    )
    n_broken  = sum(
        1 for v in arch.values()
        if "BROKEN" in v[2]
    )

    log(f"\n  ARCHITECTURE SUMMARY:")
    log(f"    INTACT : {n_intact}")
    log(f"    BROKEN : {n_broken}")
    log(f"    PARTIAL: "
        f"{len(arch)-n_intact-n_broken}")

    if n_intact >= 2:
        log(f"\n  VERDICT: INTACT")
        log(f"  NKX3-1 present → terminal")
        log(f"  differentiation follows")
        log(f"  Block is at NKX3-1 INPUT")
        log(f"  EZH2 inhibition → NKX3-1")
        log(f"  derepressed → ACPP/MSMB execute")
    elif n_broken >= 2:
        log(f"\n  VERDICT: BROKEN")
        log(f"  NKX3-1 cannot drive terminal")
        log(f"  differentiation in PRAD")
        log(f"  Direct ACPP/MSMB re-expression")
        log(f"  needed — not just NKX3-1")
    else:
        log(f"\n  VERDICT: PARTIAL/UNCLEAR")
        log(f"  Some targets follow NKX3-1")
        log(f"  Others do not")
        log(f"  Circuit partially intact")

    return arch

# ============================================================
# ANALYSIS 5: FOXA1 CIRCUIT
# ============================================================

def foxa1_circuit(tumor):
    log("")
    log("=" * 65)
    log("ANALYSIS 5: FOXA1 CIRCUIT")
    log("FOXA1 +6.4% in PRAD")
    log("Driver of FA or AR consequence?")
    log("=" * 65)

    gene_cols = [
        c for c in tumor.columns
        if c in ALL_TARGET
    ]

    pairs = [
        ("AR",    "FOXA1",  "AR→FOXA1"),
        ("FOXA1", "AMACR",  "FOXA1→AMACR"),
        ("FOXA1", "HOXC6",  "FOXA1→HOXC6"),
        ("FOXA1", "EZH2",   "FOXA1→EZH2"),
        ("FOXA1", "ACPP",   "FOXA1→ACPP"),
        ("FOXA1", "KLK3",   "FOXA1→KLK3"),
        ("FOXA1", "MYC",    "FOXA1→MYC"),
        ("FOXA1", "MKI67",  "FOXA1→MKI67"),
        ("AR",    "AMACR",  "AR→AMACR"),
        ("AR",    "HOXC6",  "AR→HOXC6"),
        ("AR",    "EZH2",   "AR→EZH2"),
        ("AR",    "MYC",    "AR→MYC"),
    ]

    log(f"\n  {'Connection':<20} "
        f"{'r':>8}  {'p':>12}  Result")
    log(f"  {'-'*58}")

    out = {}
    for ga, gb, label in pairs:
        if ga not in gene_cols \
                or gb not in gene_cols:
            log(f"  {label:<20} MISSING")
            continue
        rv, pv = stats.pearsonr(
            tumor[ga].values,
            tumor[gb].values,
        )
        stars = (
            "***" if pv < 0.001
            else "**" if pv < 0.01
            else "*" if pv < 0.05
            else "ns"
        )
        res = (
            "CONNECTED +"
            if pv < 0.05 and rv > 0
            else "CONNECTED -"
            if pv < 0.05 and rv < 0
            else "not connected"
        )
        log(f"  {label:<20} "
            f"{rv:>+8.4f}  "
            f"p={pv:.2e} {stars}  {res}")
        out[label] = (rv, pv)

    # Interpretation
    log(f"\n  FOXA1 ROLE:")
    ar_f  = out.get("AR→FOXA1",    (0, 1))
    f_a   = out.get("FOXA1→AMACR", (0, 1))
    f_h   = out.get("FOXA1→HOXC6", (0, 1))

    if ar_f[1] < 0.05 and ar_f[0] > 0:
        log(f"  AR drives FOXA1: YES")
        log(f"  FOXA1 is downstream of AR")
    else:
        log(f"  AR drives FOXA1: NO")
        log(f"  FOXA1 elevated independently")

    if f_a[1] < 0.05:
        direction = "UP" if f_a[0] > 0 else "DOWN"
        log(f"  FOXA1→AMACR: {direction} "
            f"r={f_a[0]:+.4f}")
        if f_a[0] > 0:
            log(f"  FOXA1 is a FA DRIVER")
        else:
            log(f"  FOXA1 suppresses AMACR")
            log(f"  (unexpected)")
    else:
        log(f"  FOXA1→AMACR: not connected")
        log(f"  FOXA1 is AR consequence")
        log(f"  not primary attractor driver")

    return out

# ============================================================
# ANALYSIS 6: CIRCUIT SUMMARY
# ============================================================

def circuit_summary(confirmed, not_conf,
                    arch, foxa1_res):
    log("")
    log("=" * 65)
    log("ANALYSIS 6: COMPLETE CIRCUIT MAP")
    log("=" * 65)

    log(f"\n  CONFIRMED ({len(confirmed)}):")
    log(f"  {'Connection':<28} {'r':>8}  p")
    log(f"  {'-'*50}")
    for ga, gb, rv, pv, desc in confirmed:
        stars = (
            "***" if pv < 0.001
            else "**" if pv < 0.01
            else "*"
        )
        log(f"  {ga}→{gb:<22} "
            f"{rv:>+8.4f}  "
            f"p={pv:.2e} {stars}")

    log(f"\n  NOT CONFIRMED ({len(not_conf)}):")
    for ga, gb, rv, pv, desc in not_conf:
        log(f"  {ga}→{gb:<22} "
            f"{rv:>+8.4f}  "
            f"p={pv:.2e}  ({desc})")

    n_intact = sum(
        1 for v in arch.values()
        if "INTACT" in v[2]
    )
    log(f"\n  NKX3-1 ARCHITECTURE: "
        f"{'INTACT' if n_intact >= 2 else 'BROKEN/PARTIAL'}")

    f_amacr = foxa1_res.get(
        "FOXA1→AMACR", (0, 1)
    )
    log(f"  FOXA1 ROLE: "
        f"{'FA DRIVER' if f_amacr[1]<0.05 and f_amacr[0]>0 else 'AR consequence / unclear'}")

# ============================================================
# FIGURE
# ============================================================

def generate_figure(tumor, normal,
                    confirmed, arch,
                    foxa1_res):
    log("")
    log("--- Generating figure ---")

    fig = plt.figure(figsize=(26, 20))
    fig.suptitle(
        "PRAD — Circuit Analysis | Script 2\n"
        "GSE32571 | 59 PRAD | 39 Benign | "
        "OrganismCore 2026-03-01\n"
        "Gap analysis | ERG subtypes | "
        "NKX3-1 architecture | Doc 88b",
        fontsize=10, fontweight="bold", y=0.99,
    )
    gs = gridspec.GridSpec(
        3, 3, figure=fig,
        hspace=0.52, wspace=0.42,
    )

    gene_cols = [
        c for c in tumor.columns
        if c in ALL_TARGET
    ]
    clr = {
        "ERG_high": "#8e44ad",
        "ERG_low":  "#e67e22",
        "high":     "#c0392b",
        "low":      "#f39c12",
        "TUMOR":    "#c0392b",
        "NORMAL":   "#2980b9",
    }

    # A — Confirmed circuit connections
    ax_a = fig.add_subplot(gs[0, 0])
    if confirmed:
        gc = [
            f"{ga}→{gb}"
            for ga, gb, *_ in confirmed[:14]
        ]
        vc = [rv for _, _, rv, *_ in confirmed[:14]]
        cc = [
            "#c0392b" if v < 0
            else "#27ae60"
            for v in vc
        ]
        ax_a.barh(gc, vc, color=cc)
        ax_a.axvline(
            0, color="black", linewidth=0.8
        )
        ax_a.set_xlabel("Pearson r", fontsize=8)
        ax_a.set_title(
            "A — Confirmed Circuit\n"
            "Connections (p<0.05)",
            fontsize=9,
        )
        ax_a.tick_params(axis="y", labelsize=7)
    else:
        ax_a.text(
            0.5, 0.5,
            "No confirmed\nconnections",
            ha="center", va="center",
            transform=ax_a.transAxes,
            fontsize=10,
        )
        ax_a.set_title(
            "A — Circuit Connections", fontsize=9
        )

    # B — Depth by Gleason + ERG
    ax_b = fig.add_subplot(gs[0, 1])
    cats, vals, colors = [], [], []
    if ("gleason_pattern_group" in tumor.columns
            and "block_depth" in tumor.columns):
        for g, c in [
            ("high", clr["high"]),
            ("low",  clr["low"]),
        ]:
            sd = tumor[
                tumor["gleason_pattern_group"]
                == g
            ]["block_depth"]
            if len(sd) > 2:
                cats.append(f"Gleason\n{g}")
                vals.append(sd.values)
                colors.append(c)
    if ("erg_status" in tumor.columns
            and "block_depth" in tumor.columns):
        for es, c in [
            ("ERG_high", clr["ERG_high"]),
            ("ERG_low",  clr["ERG_low"]),
        ]:
            sd = tumor[
                tumor["erg_status"] == es
            ]["block_depth"]
            if len(sd) > 2:
                cats.append(
                    es.replace("_", "\n")
                )
                vals.append(sd.values)
                colors.append(c)
    if cats:
        bp = ax_b.boxplot(
            vals,
            patch_artist=True,
            labels=cats,
        )
        for patch, c in zip(bp["boxes"], colors):
            patch.set_facecolor(c)
            patch.set_alpha(0.7)
        ax_b.set_ylabel(
            "Block Depth", fontsize=8
        )
        ax_b.set_title(
            "B — Depth by Subtype\n"
            "Gleason and ERG",
            fontsize=9,
        )

    # C — NKX3-1 vs ACPP scatter
    ax_c = fig.add_subplot(gs[0, 2])
    if ("NKX3-1" in gene_cols
            and "ACPP" in gene_cols):
        ax_c.scatter(
            tumor["NKX3-1"].values,
            tumor["ACPP"].values,
            color=clr["TUMOR"], alpha=0.6,
            s=35,
        )
        rv, pv = stats.pearsonr(
            tumor["NKX3-1"].values,
            tumor["ACPP"].values,
        )
        m, b = np.polyfit(
            tumor["NKX3-1"].values,
            tumor["ACPP"].values, 1,
        )
        xs = np.linspace(
            tumor["NKX3-1"].min(),
            tumor["NKX3-1"].max(), 50,
        )
        ax_c.plot(
            xs, m*xs+b, "k--", linewidth=1.5
        )
        label = (
            "INTACT" if rv > 0.3 and pv < 0.05
            else "BROKEN" if abs(rv) < 0.15
            else "PARTIAL"
        )
        ax_c.set_xlabel(
            "NKX3-1", fontsize=8
        )
        ax_c.set_ylabel("ACPP", fontsize=8)
        ax_c.set_title(
            f"C — NKX3-1 → ACPP\n"
            f"r={rv:+.3f} p={pv:.2e} [{label}]",
            fontsize=9,
        )

    # D — FOXA1 connections
    ax_d = fig.add_subplot(gs[1, 0])
    fg = [g for g in [
        "AR", "AMACR", "HOXC6", "EZH2",
        "ACPP", "KLK3", "MYC", "MKI67",
    ] if g in gene_cols and "FOXA1" in gene_cols]
    if fg:
        fv = []
        fc = []
        for g in fg:
            rv, _ = stats.pearsonr(
                tumor["FOXA1"].values,
                tumor[g].values,
            )
            fv.append(rv)
            fc.append(
                "#c0392b" if rv < 0
                else "#27ae60"
            )
        ax_d.barh(fg, fv, color=fc)
        ax_d.axvline(
            0, color="black", linewidth=0.8
        )
        ax_d.set_xlabel(
            "r with FOXA1", fontsize=8
        )
        ax_d.set_title(
            "D — FOXA1 Connections\n"
            "Driver or AR consequence?",
            fontsize=9,
        )
        ax_d.tick_params(axis="y", labelsize=8)

    # E — EZH2 connections
    ax_e = fig.add_subplot(gs[1, 1])
    eg = [g for g in [
        "ACPP", "MSMB", "NKX3-1", "KLK3",
        "TP63", "KRT5", "HOXC6", "AMACR",
    ] if g in gene_cols and "EZH2" in gene_cols]
    if eg:
        ev = []
        ec = []
        for g in eg:
            rv, _ = stats.pearsonr(
                tumor["EZH2"].values,
                tumor[g].values,
            )
            ev.append(rv)
            ec.append(
                "#c0392b" if rv < 0
                else "#27ae60"
            )
        ax_e.barh(eg, ev, color=ec)
        ax_e.axvline(
            0, color="black", linewidth=0.8
        )
        ax_e.set_xlabel(
            "r with EZH2", fontsize=8
        )
        ax_e.set_title(
            "E — EZH2 Connections\n"
            "Silences switch genes?",
            fontsize=9,
        )
        ax_e.tick_params(axis="y", labelsize=8)

    # F — ERG subtype key genes
    ax_f = fig.add_subplot(gs[1, 2])
    if "erg_status" in tumor.columns:
        eh = tumor[
            tumor["erg_status"] == "ERG_high"
        ]
        el = tumor[
            tumor["erg_status"] == "ERG_low"
        ]
        kg = [g for g in [
            "ACPP", "MSMB", "HOXC6", "AMACR",
            "EZH2", "FOXA1", "TMPRSS2", "NKX3-1",
        ] if g in gene_cols]
        if kg:
            x = np.arange(len(kg))
            w = 0.35
            ax_f.bar(
                x - w/2,
                [eh[g].mean() for g in kg],
                w, color=clr["ERG_high"],
                label="ERG-high", alpha=0.8,
            )
            ax_f.bar(
                x + w/2,
                [el[g].mean() for g in kg],
                w, color=clr["ERG_low"],
                label="ERG-low", alpha=0.8,
            )
            ax_f.set_xticks(x)
            ax_f.set_xticklabels(
                kg, rotation=45,
                ha="right", fontsize=7,
            )
            ax_f.set_title(
                "F — ERG Subtype\n"
                "Key gene expression",
                fontsize=9,
            )
            ax_f.legend(fontsize=7)

    # G — 3-gene vs depth
    ax_g = fig.add_subplot(gs[2, 0])
    if ("score_3gene" in tumor.columns
            and "block_depth" in tumor.columns):
        c_arr = []
        for idx in tumor.index:
            gl = tumor.loc[idx].get(
                "gleason_pattern_group", "low"
            )
            c_arr.append(
                clr.get(str(gl), clr["TUMOR"])
            )
        ax_g.scatter(
            tumor["block_depth"].values,
            tumor["score_3gene"].values,
            c=c_arr, alpha=0.7, s=35,
        )
        rv, pv = stats.pearsonr(
            tumor["block_depth"].values,
            tumor["score_3gene"].values,
        )
        ax_g.set_xlabel(
            "Block Depth", fontsize=8
        )
        ax_g.set_ylabel(
            "3-Gene Score", fontsize=8
        )
        ax_g.set_title(
            f"G — 3-Gene vs Depth\n"
            f"r={rv:+.3f} p={pv:.2e}",
            fontsize=9,
        )

    # H — All depth correlations top 15
    ax_h = fig.add_subplot(gs[2, 1])
    corrs = []
    for gene in gene_cols:
        if gene in [
            "block_depth", "score_3gene",
            "erg_status",
            "gleason_pattern_group",
            "disease_stage", "source", "group",
        ]:
            continue
        try:
            rv, pv = stats.pearsonr(
                tumor["block_depth"].values,
                tumor[gene].values,
            )
            corrs.append((gene, rv, pv))
        except Exception:
            pass
    corrs.sort(
        key=lambda x: abs(x[1]), reverse=True
    )
    if corrs:
        top = corrs[:15]
        gc  = [c[0] for c in top]
        vc  = [c[1] for c in top]
        cc  = [
            "#c0392b" if v < 0
            else "#27ae60"
            for v in vc
        ]
        ax_h.barh(gc, vc, color=cc)
        ax_h.axvline(
            0, color="black", linewidth=0.8
        )
        ax_h.set_xlabel(
            "r with depth", fontsize=8
        )
        ax_h.set_title(
            "H — Depth Correlations\n"
            "Top 15 genes",
            fontsize=9,
        )
        ax_h.tick_params(axis="y", labelsize=7)

    # I — Summary
    ax_i = fig.add_subplot(gs[2, 2])
    ax_i.axis("off")

    n_intact = sum(
        1 for v in arch.values()
        if "INTACT" in v[2]
    )
    f_amacr = foxa1_res.get(
        "FOXA1→AMACR", (0, 1)
    )
    f_role = (
        "FA DRIVER"
        if f_amacr[1] < 0.05
        and f_amacr[0] > 0
        else "AR consequence"
    )
    n_conf = len(confirmed)

    summary = (
        "I — SCRIPT 2 SUMMARY\n"
        "─────────────────────────\n"
        "Dataset: GSE32571\n"
        "  59 PRAD | 39 Benign\n\n"
        f"Genes loaded: "
        f"{len(gene_cols)}\n"
        f"Circuit confirmed: {n_conf}\n\n"
        f"NKX3-1→ACCP:\n"
        f"  {'INTACT' if n_intact>=2 else 'BROKEN'}\n\n"
        f"FOXA1: {f_role}\n\n"
        "Switch genes:\n"
        "  ACPP  r=-0.595\n"
        "  MSMB  r=-0.551\n\n"
        "FA markers:\n"
        "  HOXC6 +34.7%\n"
        "  AMACR +36.1%\n\n"
        "EZH2: 4th solid cancer\n"
        "r=+0.426 with depth\n\n"
        "Gleason: p=0.0024 ✓\n"
        "ERG bimodal: ✓\n\n"
        "Framework: OrganismCore\n"
        "Doc: 88b | 2026-03-01"
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
        S2_DIR, "prad_s2_circuit.png"
    )
    plt.savefig(
        out, dpi=150, bbox_inches="tight"
    )
    log(f"\n  Figure: {out}")
    plt.close()

# ============================================================
# MAIN
# ============================================================

def main():
    log("=" * 65)
    log("PROSTATE ADENOCARCINOMA")
    log("FALSE ATTRACTOR — SCRIPT 2")
    log("Circuit Analysis")
    log("Doc: 88b | Date: 2026-03-01")
    log("=" * 65)

    log("\n=== STEP 0: GENE MATRIX ===")
    gene_df = build_gene_matrix()

    log("\n=== STEP 1: CLASSIFY ===")
    merged, tumor, normal = \
        classify_samples(gene_df)

    log("\n=== STEP 2: DEPTH + ERG ===")
    tumor = build_depth_erg(tumor)

    log("\n=== ANALYSIS 1: GAP ANALYSIS ===")
    confirmed, not_conf = gap_analysis(tumor)

    log("\n=== ANALYSIS 2: ERG SUBTYPE ===")
    tumor = erg_subtype_analysis(tumor)

    log("\n=== ANALYSIS 3: 3-GENE SCORE ===")
    tumor = three_gene_score(tumor)

    log("\n=== ANALYSIS 4: NKX3-1 GAP ===")
    arch = nkx31_function_gap(tumor)

    log("\n=== ANALYSIS 5: FOXA1 CIRCUIT ===")
    foxa1_res = foxa1_circuit(tumor)

    log("\n=== ANALYSIS 6: CIRCUIT SUMMARY ===")
    circuit_summary(
        confirmed, not_conf, arch, foxa1_res
    )

    log("\n=== FIGURE ===")
    generate_figure(
        tumor, normal, confirmed,
        arch, foxa1_res,
    )

    write_log()
    log(f"\n  Log: {LOG_FILE}")
    log(f"  Outputs: {S2_DIR}")
    log("\n=== SCRIPT 2 COMPLETE ===")


if __name__ == "__main__":
    main()
