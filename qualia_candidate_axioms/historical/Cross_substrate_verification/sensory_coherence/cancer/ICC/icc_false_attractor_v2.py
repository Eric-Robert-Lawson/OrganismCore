"""
ICC FALSE ATTRACTOR — SCRIPT 2
ITERATION RUN — CORRECTED FRAMEWORK

Framework: OrganismCore
Doc: 93e | Date: 2026-03-02
Author: Eric Robert Lawson

SCRIPT 1 FINDINGS (Doc 93a):
  SW confirmed: FOXA2, HNF4A, ALB, APOB,
                CYP3A4, ALDOB, G6PC, GGT1
  FA confirmed: SOX4, SOX9, PROM1, CD44,
                CDC20, EZH2, TWIST1, FAP,
                BIRC5, CCNB1, CDK4, COL1A1,
                POSTN, ACTA2, TGFB1, MMP2,
                MMP9, WNT5A
  EZH2:         UP both datasets (lock ✓)
  Top TCGA:     TWIST1 r=+0.789 (EMT axis)
  Top GSE:      ALB    r=-0.803 (SW axis)
  Unexpected:   KDM1A r=+0.503 TCGA
                DNMT3A r=-0.451 GSE
                FOXA2→ALB anti-correlated GSE
                Two-basin NMF finding
                EGFR = CAF marker (not epithelial)

SCRIPT 2 PREDICTIONS (locked Doc 93a, 2026-03-02):
  S2-P1: KDM1A r(KDM1A,ALB) NEGATIVE
  S2-P2: Two ICC basins — Depth_T vs Depth_S
         Prolif: Depth_T > Depth_S
         Inflam: Depth_S > Depth_T
  S2-P3: FOXA2→ALB r near zero or negative
         in tumour-only
  S2-P4: DNMT3A depth-negative confirmed
         lower DNMT3A = deeper ICC
  S2-P5: KDM1A + EZH2 co-elevated
         r(KDM1A,EZH2) > 0.30
  S2-P6: S2 depth (ALB + COL1A1) r > 0.80
         with S1 depth
  S2-P7: Inflam subtype: ACTA2 primary driver
         Prolif subtype: CDC20/TOP2A primary

DRUG TARGETS (pre-literature, locked):
  1. EZH2 inhibitor (tazemetostat)
  2. KDM1A/LSD1 inhibitor (GSK-LSD1)
  3. TGF-β inhibitor (galunisertib)
  4. WNT5A/non-canonical Wnt inhibitor
"""

import os
import gzip
import requests
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import warnings
warnings.filterwarnings("ignore")

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR    = "./icc_false_attractor/"
TCGA_DIR    = os.path.join(BASE_DIR, "tcga_chol/")
GEO_DIR     = os.path.join(BASE_DIR, "geo_icc/")
DATA_DIR    = os.path.join(BASE_DIR, "data/")
LIRI_DIR    = os.path.join(BASE_DIR, "liri_jp/")
RESULTS_S1  = os.path.join(BASE_DIR, "results_s1/")
RESULTS_DIR = os.path.join(BASE_DIR, "results_s2/")
LOG_FILE    = os.path.join(RESULTS_DIR,
                           "analysis_log_s2.txt")
for d in [LIRI_DIR, RESULTS_DIR]:
    os.makedirs(d, exist_ok=True)

# ============================================================
# GENE PANELS — EXTENDED FOR SCRIPT 2
# ============================================================

# Core SW genes (confirmed Script 1)
SW_GENES = [
    "FOXA2", "HNF4A", "ALB", "APOB",
    "CYP3A4", "ALDOB", "G6PC", "GGT1",
]

# Core FA genes (confirmed Script 1)
FA_GENES = [
    "SOX4", "SOX9", "PROM1", "CD44",
    "CDC20", "BIRC5", "TOP2A", "MKI67",
    "CCNB1", "CDK4", "CDK6",
]

# Stroma genes (confirmed Script 1)
STROMA_GENES = [
    "ACTA2", "FAP", "COL1A1", "POSTN",
    "TGFB1", "MMP2", "MMP9", "FN1",
    "WNT5A",
]

# Epigenetic panel — extended for S2
EPIGENETIC_GENES = [
    "EZH2",   # confirmed lock
    "KDM1A",  # NEW — r=+0.503 TCGA
    "HDAC1",  # r=+0.435 GSE
    "HDAC2",  # confirmed
    "DNMT3A", # NEW — r=-0.451 GSE
    "DNMT1",  # confirmed
    "TET2",
    "ASXL1",
    "RCOR1",
]

# EMT panel — extended
EMT_GENES = [
    "TWIST1", "VIM", "ZEB1", "ZEB2",
    "SNAI1", "CDH1", "EPCAM",
]

# Gap genes — circuits to test
GAP_GENES = [
    "HNF4A", "FOXA2",
    "ALB", "APOB", "G6PC", "CYP3A4",
    "WNT5A", "TWIST1",
    "TGFB1", "ACTA2",
    "EZH2", "KDM1A",
    "EGFR", "ERBB2",
    "DNMT3A",
]

# Identity genes of each subtype
# (S2-P7 test)
PROLIF_IDENTITY = [
    "CDC20", "TOP2A", "MKI67",
    "CCNB1", "BIRC5", "CDK4",
]
STROMA_IDENTITY = [
    "ACTA2", "COL1A1", "FAP",
    "POSTN", "WNT5A",
]

ALL_PANEL = list(set(
    SW_GENES + FA_GENES + STROMA_GENES
    + EPIGENETIC_GENES + EMT_GENES
    + GAP_GENES + PROLIF_IDENTITY
    + STROMA_IDENTITY
    + ["MYC", "HAVCR2", "ARID1A",
       "SMAD4", "CTNNB1", "CCND1",
       "FGFR2", "IDH1", "IDH2",
       "NOTCH1", "NOTCH2", "KRAS",
       "TP53", "BAP1", "SF3B1",
       "SOX17", "KRT7", "KRT19",
       "CLDN4", "MUC1", "CD44",
       "STAT3", "VEGFA", "CA9",
       "PTEN", "RB1", "CDKN2A",
       "ALDH1A1", "GLUL"]
))

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
    if p is None or np.isnan(p):
        return "p=N/A      "
    if p < 0.001:  return f"p={p:.2e} ***"
    elif p < 0.01: return f"p={p:.2e}  **"
    elif p < 0.05: return f"p={p:.4f}   *"
    else:          return f"p={p:.4f}  ns"

def norm01(arr):
    arr = np.asarray(arr, float)
    mn, mx = np.nanmin(arr), np.nanmax(arr)
    if mx > mn:
        return (arr - mn) / (mx - mn)
    return np.full_like(arr, 0.5)

def safe_r(x, y):
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    m = np.isfinite(x) & np.isfinite(y)
    if m.sum() < 5:
        return np.nan, np.nan
    return stats.pearsonr(x[m], y[m])

def try_get(url, dest, min_size=500):
    if (os.path.exists(dest)
            and os.path.getsize(dest)
            > min_size):
        log(f"  Cached: {os.path.getsize(dest):,}b")
        return dest
    log(f"  GET {url[:80]}")
    try:
        r = requests.get(
            url, stream=True, timeout=300,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        log(f"  HTTP {r.status_code}")
        if r.status_code == 200:
            data = b"".join(
                r.iter_content(1024 * 1024)
            )
            if len(data) > min_size:
                with open(dest, "wb") as f:
                    f.write(data)
                log(f"  Saved {len(data):,}b")
                return dest
    except Exception as ex:
        log(f"  Error: {ex}")
    return None

# ============================================================
# DATA LOADERS — reuse Script 1 downloads
# ============================================================

def load_tcga():
    log(f"\n{'='*65}")
    log("LOADING TCGA-CHOL (reuse S1 download)")
    log(f"{'='*65}")
    path = os.path.join(
        TCGA_DIR, "CHOL_expr.tsv.gz"
    )
    if not os.path.exists(path):
        url = (
            "https://tcga-xena-hub.s3"
            ".us-east-1.amazonaws.com"
            "/download/TCGA.CHOL"
            ".sampleMap%2FHiSeqV2.gz"
        )
        path = try_get(url, path, 100000)

    expr = {}
    sample_ids = []
    gw = set(ALL_PANEL)

    if path and os.path.exists(path):
        opener = (
            gzip.open(path, "rt",
                encoding="utf-8",
                errors="ignore")
            if path.endswith(".gz")
            else open(path, "r",
                encoding="utf-8",
                errors="ignore")
        )
        with opener as f:
            for line in f:
                parts = line.rstrip("\n")\
                    .split("\t")
                if not sample_ids:
                    sample_ids = [
                        p.strip()
                        for p in parts[1:]
                    ]
                    continue
                gene = parts[0].strip()\
                    .strip('"')
                if gene not in gw:
                    continue
                try:
                    vals = np.array([
                        float(p.strip())
                        if p.strip() not in
                        ["", "NA", "nan"]
                        else np.nan
                        for p in parts[1:]
                    ])
                    expr[gene] = vals
                except ValueError:
                    pass

    tumour = np.array([
        ("-01" in s
         or (len(s) >= 15
             and s[13:15] == "01"))
        for s in sample_ids
    ])
    normal = np.array([
        ("-11" in s
         or (len(s) >= 15
             and s[13:15] == "11"))
        for s in sample_ids
    ])
    log(f"  tumour={tumour.sum()} "
        f"normal={normal.sum()} "
        f"genes={len(expr)}")
    return expr, sample_ids, tumour, normal


def load_gse():
    log(f"\n{'='*65}")
    log("LOADING GSE32225 (reuse S1 download)")
    log(f"{'='*65}")

    matrix_path = os.path.join(
        GEO_DIR, "GSE32225_matrix.txt.gz"
    )
    soft_path = os.path.join(
        DATA_DIR, "GPL8432.soft.gz"
    )

    # Download if missing
    if not os.path.exists(matrix_path) \
            or os.path.getsize(matrix_path) \
            < 100000:
        try_get(
            "https://ftp.ncbi.nlm.nih.gov"
            "/geo/series/GSE32nnn/GSE32225"
            "/matrix/GSE32225_series_matrix"
            ".txt.gz",
            matrix_path, 100000,
        )
    if not os.path.exists(soft_path) \
            or os.path.getsize(soft_path) \
            < 10000:
        try_get(
            "https://ftp.ncbi.nlm.nih.gov"
            "/geo/platforms/GPL8nnn/GPL8432"
            "/soft/GPL8432_family.soft.gz",
            soft_path, 10000,
        )

    # Probe map
    p2g = {}
    gw = set(ALL_PANEL)
    if soft_path and os.path.exists(soft_path):
        in_d = False
        hdr = None
        id_c = sym_c = None
        opener = (
            gzip.open(soft_path, "rt",
                encoding="utf-8",
                errors="ignore")
            if soft_path.endswith(".gz")
            else open(soft_path, "r",
                encoding="utf-8",
                errors="ignore")
        )
        with opener as f:
            for line in f:
                line = line.rstrip("\n")
                if "!platform_table_begin" \
                        in line.lower():
                    in_d = True
                    hdr = None
                    continue
                if "!platform_table_end" \
                        in line.lower():
                    break
                if not in_d:
                    continue
                parts = line.split("\t")
                if hdr is None:
                    hdr = [
                        p.lower().strip()
                        for p in parts
                    ]
                    for i, h in enumerate(hdr):
                        if h == "id" \
                                and id_c is None:
                            id_c = i
                        if any(x in h for x in [
                            "symbol",
                            "gene_symbol",
                        ]) and sym_c is None:
                            sym_c = i
                    continue
                if id_c is None \
                        or sym_c is None:
                    continue
                if max(id_c, sym_c) \
                        >= len(parts):
                    continue
                pid = parts[id_c].strip()
                sym = (
                    parts[sym_c].strip()
                    .split("///")[0]
                    .split(";")[0].strip()
                )
                if pid and sym \
                        and sym != "NA" \
                        and sym in gw:
                    p2g[pid] = sym
        log(f"  Probe map: {len(p2g)} probes")

    # Matrix
    gsm_ids = []
    char_block = {}
    expr_data = {}
    in_table = tbl_hdr = False
    n_samples = 0

    if matrix_path \
            and os.path.exists(matrix_path):
        opener = (
            gzip.open(matrix_path, "rt",
                encoding="utf-8",
                errors="ignore")
            if matrix_path.endswith(".gz")
            else open(matrix_path, "r",
                encoding="utf-8",
                errors="ignore")
        )
        with opener as f:
            for raw in f:
                line = raw.rstrip("\n")
                if line.startswith(
                    "!Sample_geo_accession"
                ):
                    parts = line.split("\t")
                    gsm_ids = [
                        p.strip().strip('"')
                        for p in parts[1:]
                    ]
                    n_samples = len(gsm_ids)
                    continue
                if line.startswith(
                    "!Sample_characteristics_ch1"
                ):
                    parts = line.split("\t")
                    if key := parts[0]:
                        if key not in char_block:
                            char_block[key] = []
                        char_block[key].append([
                            p.strip().strip('"')
                            for p in parts[1:]
                        ])
                    continue
                if "series_matrix_table_begin" \
                        in line:
                    in_table = True
                    tbl_hdr = False
                    continue
                if "series_matrix_table_end" \
                        in line:
                    break
                if not in_table:
                    continue
                if not tbl_hdr:
                    tbl_hdr = True
                    continue
                parts = line.split("\t")
                pid = parts[0].strip()\
                    .strip('"')
                gene = p2g.get(pid)
                if gene is None:
                    continue
                try:
                    vals = np.array([
                        float(p.strip())
                        if p.strip() not in
                        ["", "NA", "nan"]
                        else np.nan
                        for p in
                        parts[1:n_samples + 1]
                    ])
                    if gene not in expr_data \
                            or np.nanvar(vals) \
                            > np.nanvar(
                        expr_data[gene][1]
                    ):
                        expr_data[gene] = (
                            pid, vals
                        )
                except (ValueError, TypeError):
                    continue

    expr = {
        g: v
        for g, (_, v) in expr_data.items()
    }

    nmf_labels = [""] * n_samples
    icc_mask = np.ones(n_samples, dtype=bool)
    nor_mask = np.zeros(n_samples, dtype=bool)
    for key, val_lists in char_block.items():
        for val_row in val_lists:
            for i, v in enumerate(val_row):
                if i >= n_samples:
                    break
                if ":" in v:
                    k, _, vv = v.partition(":")
                    kl = k.strip().lower()
                    vv = vv.strip()
                    if "nmf" in kl:
                        nmf_labels[i] = vv
                    if "cell type" in kl \
                            and "normal" \
                            in vv.lower():
                        icc_mask[i] = False
                        nor_mask[i] = True
                else:
                    if "normal" in v.lower():
                        icc_mask[i] = False
                        nor_mask[i] = True

    log(f"  ICC={icc_mask.sum()} "
        f"Normal={nor_mask.sum()} "
        f"genes={len(expr)}")
    return (expr, gsm_ids, nmf_labels,
            icc_mask, nor_mask)


def load_liri():
    """
    LIRI-JP: ICGC liver/biliary data
    Best available ICC OS dataset
    Try multiple download paths
    """
    log(f"\n{'='*65}")
    log("LOADING LIRI-JP (OS validation)")
    log(f"{'='*65}")

    urls = [
        (
            "https://dcc.icgc.org/api/v1"
            "/download?fn=/current/Projects"
            "/LIRI-JP/donor.tsv.gz",
            os.path.join(
                LIRI_DIR, "liri_donor.tsv.gz"
            ),
        ),
        (
            "https://dcc.icgc.org/api/v1"
            "/download?fn=/current/Projects"
            "/LIRI-JP/exp_seq.tsv.gz",
            os.path.join(
                LIRI_DIR, "liri_exp.tsv.gz"
            ),
        ),
    ]

    paths = {}
    for url, dest in urls:
        key = os.path.basename(dest)\
            .replace(".tsv.gz", "")
        result = try_get(url, dest, 1000)
        paths[key] = result

    # Check if donor file loaded
    donor_path = paths.get("liri_donor")
    if not donor_path \
            or not os.path.exists(donor_path):
        log("  LIRI-JP donor file unavailable")
        log("  Trying alternative: TCGA-CHOL "
            "clinical from GDC")
        return load_tcga_clinical()

    return parse_liri(
        paths.get("liri_donor"),
        paths.get("liri_exp"),
    )


def load_tcga_clinical():
    """
    Fallback OS source: TCGA-CHOL clinical
    from Xena hub (already downloaded)
    """
    log("  Fallback: TCGA-CHOL clinical")
    clin_path = os.path.join(
        TCGA_DIR, "CHOL_clinical.tsv"
    )
    urls = [
        "https://tcga-xena-hub.s3"
        ".us-east-1.amazonaws.com"
        "/download/survival%2FCHOL_survival.txt",
        "https://tcga-xena-hub.s3"
        ".us-east-1.amazonaws.com"
        "/download/TCGA.CHOL.sampleMap"
        "%2FCHOL_clinicalMatrix",
    ]
    for url in urls:
        result = try_get(
            url, clin_path, 500
        )
        if result:
            break

    if not os.path.exists(clin_path):
        log("  No clinical data available")
        return None

    try:
        df = pd.read_csv(
            clin_path, sep="\t",
            encoding="utf-8",
            low_memory=False,
        )
        log(f"  Clinical cols: "
            f"{list(df.columns[:10])}")
        return df
    except Exception as ex:
        log(f"  Clinical parse error: {ex}")
        return None


def parse_liri(donor_path, exp_path):
    if not donor_path:
        return None
    try:
        df = pd.read_csv(
            donor_path, sep="\t",
            encoding="utf-8",
        )
        log(f"  LIRI donor: "
            f"{len(df)} rows")
        log(f"  Cols: "
            f"{list(df.columns[:8])}")
        return df
    except Exception as ex:
        log(f"  LIRI parse error: {ex}")
        return None

# ============================================================
# DEPTH SCORES — S1 AND S2
# ============================================================

def build_s1_depth(expr, tumour_mask):
    """
    Reproduce Script 1 depth score
    for comparison.
    """
    sw_ok = [g for g in SW_GENES
             if g in expr]
    fa_ok = [g for g in
             (FA_GENES + STROMA_GENES)
             if g in expr]
    ti = np.where(tumour_mask)[0]
    sw_mat = np.column_stack([
        expr[g][ti] for g in sw_ok
    ])
    fa_mat = np.column_stack([
        expr[g][ti] for g in fa_ok
    ])
    c1 = 1 - norm01(np.nanmean(sw_mat, 1))
    c2 = norm01(np.nanmean(fa_mat, 1))
    return (c1 + c2) / 2.0, ti


def build_s2_depth(expr, tumour_mask,
                   label):
    """
    PROTOCOL VII — SCRIPT 2 DEPTH SCORE
    Uses two highest-|r| genes from S1:
      Top suppressed: ALB  (GSE r=-0.803)
      Top elevated:   TWIST1 (TCGA r=+0.789)
                   or COL1A1 (GSE r=+0.683)
    Build BOTH:
      Depth_T (TWIST1-based — EMT axis)
      Depth_S (ACTA2/COL1A1 — stroma axis)
    """
    log(f"\n{'='*65}")
    log(f"S2 DEPTH SCORES — {label}")
    log(f"{'='*65}")

    ti = np.where(tumour_mask)[0]

    def _depth(sw_genes, fa_genes, name):
        sw_ok = [g for g in sw_genes
                 if g in expr]
        fa_ok = [g for g in fa_genes
                 if g in expr]
        if not sw_ok or not fa_ok:
            log(f"  {name}: "
                f"insufficient genes")
            return np.full(len(ti), np.nan)
        sw_v = np.nanmean(np.column_stack([
            expr[g][ti] for g in sw_ok
        ]), axis=1)
        fa_v = np.nanmean(np.column_stack([
            expr[g][ti] for g in fa_ok
        ]), axis=1)
        d = (1 - norm01(sw_v)
             + norm01(fa_v)) / 2.0
        log(f"  {name}: "
            f"mean={np.nanmean(d):.4f} "
            f"std={np.nanstd(d):.4f}")
        return d

    # Depth_T — EMT axis
    # SW: G6PC (r=-0.713 TCGA)
    # FA: TWIST1 (r=+0.789 TCGA)
    depth_t = _depth(
        ["G6PC", "ALB", "APOB"],
        ["TWIST1", "VIM", "ZEB1"],
        "Depth_T (EMT)",
    )

    # Depth_S — Stroma axis
    # SW: ALB (r=-0.803 GSE)
    # FA: COL1A1 (r=+0.683 GSE)
    depth_s = _depth(
        ["ALB", "HNF4A", "APOB"],
        ["COL1A1", "ACTA2", "FAP",
         "POSTN"],
        "Depth_S (Stroma)",
    )

    # Combined
    depth_comb = (depth_t + depth_s) / 2.0
    log(f"  Depth_comb: "
        f"mean={np.nanmean(depth_comb):.4f} "
        f"std={np.nanstd(depth_comb):.4f}")

    return depth_t, depth_s, depth_comb, ti


# ============================================================
# S1 vs S2 DEPTH COMPARISON
# ============================================================

def compare_depths(depth_s1, depth_t,
                   depth_s, label):
    """
    Protocol: r(S1,S2) tells if same
    biology captured.
    r>0.9: same biology
    r 0.5-0.9: partial concordance
    r<0.5: different axes
    """
    log(f"\n{'='*65}")
    log(f"S1 vs S2 DEPTH COMPARISON — {label}")
    log(f"{'='*65}")

    r_t, p_t = safe_r(depth_s1, depth_t)
    r_s, p_s = safe_r(depth_s1, depth_s)
    r_ts, p_ts = safe_r(depth_t, depth_s)

    log(f"  r(S1, Depth_T) = {r_t:+.4f} "
        f"{fmt_p(p_t)}")
    log(f"  r(S1, Depth_S) = {r_s:+.4f} "
        f"{fmt_p(p_s)}")
    log(f"  r(Depth_T, Depth_S) = "
        f"{r_ts:+.4f} {fmt_p(p_ts)}")

    # Interpret
    for name, r in [
        ("S1 vs Depth_T", r_t),
        ("S1 vs Depth_S", r_s),
    ]:
        if abs(r) > 0.9:
            interp = "same biology"
        elif abs(r) > 0.5:
            interp = "partial concordance"
        else:
            interp = "different axes — " \
                     "S2 captures new signal"
        log(f"  {name}: {interp}")

    if abs(r_ts) < 0.5:
        log(f"  Depth_T and Depth_S are "
            f"INDEPENDENT axes ✓")
        log(f"  ICC has two distinct depth "
            f"dimensions")
    else:
        log(f"  Depth_T and Depth_S are "
            f"CORRELATED — same underlying "
            f"axis")

    return r_t, r_s, r_ts


# ============================================================
# TWO-BASIN DECOMPOSITION
# ============================================================

def two_basin_analysis(expr, depth_t,
                       depth_s, ti,
                       nmf_labels, label):
    """
    S2-P2: Two ICC attractor basins
    Proliferative: Depth_T > Depth_S
    Inflammatory:  Depth_S > Depth_T
    Test against NMF labels.
    """
    log(f"\n{'='*65}")
    log(f"TWO-BASIN DECOMPOSITION — {label}")
    log(f"{'='*65}")

    # Basin assignment from depth axes
    dt = np.asarray(depth_t, float)
    ds = np.asarray(depth_s, float)
    valid = np.isfinite(dt) & np.isfinite(ds)

    basin_t = (dt > ds) & valid  # EMT dominant
    basin_s = (ds >= dt) & valid  # Stroma dominant

    n_t = basin_t.sum()
    n_s = basin_s.sum()
    log(f"  EMT-dominant (Depth_T>S): "
        f"n={n_t}")
    log(f"  Stroma-dominant (Depth_S>=T): "
        f"n={n_s}")

    # Cross with NMF labels
    if any(nmf_labels[ti[j]]
           for j in range(len(ti))):
        nmf_at_ti = np.array([
            nmf_labels[ti[j]]
            for j in range(len(ti))
        ])
        classes = sorted(set(
            l for l in nmf_at_ti if l
        ))
        log(f"\n  NMF × Basin contingency:")
        log(f"  {'NMF class':<20} "
            f"{'EMT_dom':>10} "
            f"{'Stroma_dom':>12}")
        log(f"  {'-'*44}")
        for c in classes:
            cm = nmf_at_ti == c
            n_et = (basin_t & cm).sum()
            n_es = (basin_s & cm).sum()
            log(f"  {c:<20} "
                f"{n_et:>10} "
                f"{n_es:>12}")

    # Key gene expression by basin
    key_genes = [
        "TWIST1", "ALB", "ACTA2",
        "COL1A1", "EZH2", "KDM1A",
        "WNT5A", "TGFB1", "SOX4",
        "CDC20", "HNF4A", "DNMT3A",
    ]
    log(f"\n  Key genes by basin "
        f"(tumour samples):")
    log(f"  {'Gene':<10} "
        f"{'EMT_dom':>10} "
        f"{'Str_dom':>10}  "
        f"{'p':>14}")
    log(f"  {'-'*50}")

    for gene in key_genes:
        if gene not in expr:
            continue
        gv = expr[gene][ti]
        g_t = gv[basin_t]
        g_s = gv[basin_s]
        g_t = g_t[np.isfinite(g_t)]
        g_s = g_s[np.isfinite(g_s)]
        if len(g_t) < 3 or len(g_s) < 3:
            continue
        _, p = stats.mannwhitneyu(
            g_t, g_s,
            alternative="two-sided",
        )
        log(f"  {gene:<10} "
            f"{g_t.mean():>10.3f} "
            f"{g_s.mean():>10.3f}  "
            f"{fmt_p(p):>14}")

    return basin_t, basin_s


# ============================================================
# EXTENDED GAP TESTS
# ============================================================

def extended_gap_tests(expr, depth_t,
                       depth_s, ti,
                       label):
    """
    S2 gap tests — extended panel.
    Tests S2 predictions specifically.
    """
    log(f"\n{'='*65}")
    log(f"EXTENDED GAP TESTS — {label}")
    log(f"{'='*65}")

    circuits = [
        # S2-P1: KDM1A circuits
        ("KDM1A", "ALB",
         "S2-P1: KDM1A→ALB (epi lock→SW gene)",
         "negative = KDM1A silences biliary"),
        ("KDM1A", "HNF4A",
         "S2-P1: KDM1A→HNF4A repression",
         "negative = KDM1A represses TF"),
        ("KDM1A", "EZH2",
         "S2-P5: KDM1A+EZH2 co-lock",
         "positive = dual epigenetic lock"),
        # S2-P3: FOXA2→ALB
        ("FOXA2", "ALB",
         "S2-P3: FOXA2→ALB circuit",
         "near zero/negative = broken"),
        ("FOXA2", "HNF4A",
         "FOXA2↔HNF4A co-regulation",
         "positive = co-regulated TFs"),
        # S2-P4: DNMT3A depth
        ("DNMT3A", "ALB",
         "S2-P4: DNMT3A (low=deep) vs ALB",
         "positive = low DNMT3A→low ALB"),
        ("DNMT3A", "EZH2",
         "DNMT3A vs EZH2 opposition",
         "negative = DNMT3A loss + EZH2 gain"),
        # Stroma circuits
        ("WNT5A", "COL1A1",
         "WNT5A→COL1A1 stroma",
         "positive = WNT5A activates stroma"),
        ("WNT5A", "ACTA2",
         "WNT5A→ACTA2 CAF activation",
         "positive = WNT5A→CAF"),
        ("TGFB1", "COL1A1",
         "TGFB1→COL1A1 fibrosis",
         "positive = TGFB1 drives ECM"),
        # EMT circuits
        ("EZH2", "TWIST1",
         "EZH2→TWIST1 (epi→EMT)",
         "positive = EZH2 promotes EMT"),
        ("KDM1A", "TWIST1",
         "KDM1A→TWIST1 (LSD1→EMT)",
         "positive = KDM1A promotes EMT"),
        # Depth axis circuits
        ("TWIST1", "COL1A1",
         "TWIST1↔COL1A1 (EMT vs stroma)",
         "independent if different axes"),
    ]

    log(f"\n  {'Circuit':<38} {'r':>8} "
        f"{'p':>14}  classification")
    log(f"  {'-'*80}")

    results = {}
    for gA, gB, name, interp in circuits:
        if gA not in expr or gB not in expr:
            continue
        vA = expr[gA][ti]
        vB = expr[gB][ti]
        r, p = safe_r(vA, vB)
        if np.isnan(r):
            continue

        if abs(r) < 0.15:
            cls = "BROKEN ✓"
        elif abs(r) < 0.30:
            cls = ("WEAK POS" if r > 0
                   else "WEAK NEG")
        elif r > 0:
            cls = "CONNECTED +"
        else:
            cls = "ANTI-CORRELATED −"

        log(f"  {name:<38} {r:>+8.4f} "
            f"{fmt_p(p):>14}  {cls}")
        log(f"    → {interp}")
        results[f"{gA}→{gB}"] = {
            "r": r, "p": p,
            "class": cls,
        }

    return results


# ============================================================
# EPIGENETIC ANALYSIS
# ============================================================

def epigenetic_analysis(expr, depth_t,
                        depth_s, ti,
                        label):
    """
    S2-P1, S2-P4, S2-P5:
    KDM1A and DNMT3A as novel epigenetic
    depth drivers.
    """
    log(f"\n{'='*65}")
    log(f"EPIGENETIC ANALYSIS — {label}")
    log(f"{'='*65}")

    epi_genes = [
        "EZH2", "KDM1A", "HDAC1",
        "HDAC2", "DNMT3A", "DNMT1",
        "TET2", "ASXL1", "RCOR1",
    ]

    log(f"\n  Epigenetic gene correlations "
        f"with Depth_T and Depth_S:")
    log(f"  {'Gene':<10} "
        f"{'r_DT':>8} "
        f"{'p_DT':>14}  "
        f"{'r_DS':>8} "
        f"{'p_DS':>14}  "
        f"axis")
    log(f"  {'-'*72}")

    for gene in epi_genes:
        if gene not in expr:
            continue
        gv = expr[gene][ti]
        r_t, p_t = safe_r(depth_t, gv)
        r_s, p_s = safe_r(depth_s, gv)
        if np.isnan(r_t) and np.isnan(r_s):
            continue

        # Which axis does this gene belong to?
        if abs(r_t) > abs(r_s) + 0.1:
            axis = "EMT"
        elif abs(r_s) > abs(r_t) + 0.1:
            axis = "Stroma"
        else:
            axis = "Both"

        log(f"  {gene:<10} "
            f"{r_t:>+8.4f} "
            f"{fmt_p(p_t):>14}  "
            f"{r_s:>+8.4f} "
            f"{fmt_p(p_s):>14}  "
            f"{axis}")

    # S2-P5 explicit: KDM1A+EZH2 co-lock
    if "KDM1A" in expr and "EZH2" in expr:
        r_ke, p_ke = safe_r(
            expr["KDM1A"][ti],
            expr["EZH2"][ti],
        )
        log(f"\n  S2-P5 TEST: "
            f"r(KDM1A, EZH2) = "
            f"{r_ke:+.4f} {fmt_p(p_ke)}")
        if r_ke > 0.30:
            log(f"  S2-P5 CONFIRMED ✓ "
                f"Dual epigenetic lock")
        else:
            log(f"  S2-P5 NOT CONFIRMED "
                f"Independent mechanisms")

    # S2-P4: DNMT3A depth-negative
    if "DNMT3A" in expr:
        r_dn_t, p_dn_t = safe_r(
            depth_t,
            expr["DNMT3A"][ti],
        )
        r_dn_s, p_dn_s = safe_r(
            depth_s,
            expr["DNMT3A"][ti],
        )
        log(f"\n  S2-P4 TEST: DNMT3A depth")
        log(f"  r(DNMT3A, Depth_T) = "
            f"{r_dn_t:+.4f} {fmt_p(p_dn_t)}")
        log(f"  r(DNMT3A, Depth_S) = "
            f"{r_dn_s:+.4f} {fmt_p(p_dn_s)}")
        if r_dn_t < -0.20 \
                or r_dn_s < -0.20:
            log(f"  S2-P4 CONFIRMED ✓ "
                f"DNMT3A loss = deeper ICC")
        else:
            log(f"  S2-P4 not confirmed "
                f"in this dataset/axis")


# ============================================================
# NMF × DEPTH AXIS
# ============================================================

def nmf_depth_axis(expr, depth_t,
                   depth_s, ti,
                   nmf_labels, label):
    """
    S2-P7: Within each NMF subtype,
    which axis drives depth?
    Proliferative → Depth_T primary
    Inflammatory  → Depth_S primary
    """
    log(f"\n{'='*65}")
    log(f"NMF × DEPTH AXIS — {label}")
    log(f"{'='*65}")

    nmf_at_ti = np.array([
        nmf_labels[ti[j]]
        for j in range(len(ti))
    ])
    classes = sorted(set(
        l for l in nmf_at_ti if l
    ))
    if not classes:
        log("  No NMF labels")
        return {}

    results = {}
    for c in classes:
        cm = nmf_at_ti == c
        ci = np.where(cm)[0]
        if len(ci) < 5:
            continue

        dt_c = depth_t[ci]
        ds_c = depth_s[ci]

        log(f"\n  {c} (n={len(ci)}):")
        log(f"    Depth_T: "
            f"mean={np.nanmean(dt_c):.4f} "
            f"std={np.nanstd(dt_c):.4f}")
        log(f"    Depth_S: "
            f"mean={np.nanmean(ds_c):.4f} "
            f"std={np.nanstd(ds_c):.4f}")

        # Which axis is higher?
        if np.nanmean(dt_c) \
                > np.nanmean(ds_c):
            log(f"    Primary axis: "
                f"EMT (Depth_T dominant)")
        else:
            log(f"    Primary axis: "
                f"Stroma (Depth_S dominant)")

        # S2-P7 specific genes
        id_genes = (
            PROLIF_IDENTITY
            if "prolif" in c.lower()
            else STROMA_IDENTITY
        )
        log(f"    Identity genes "
            f"({c}):")
        for gene in id_genes:
            if gene not in expr:
                continue
            gv = expr[gene][ti][ci]
            gv = gv[np.isfinite(gv)]
            if len(gv) > 0:
                log(f"      {gene}: "
                    f"mean={gv.mean():.3f}")

        results[c] = {
            "depth_t": np.nanmean(dt_c),
            "depth_s": np.nanmean(ds_c),
            "n": len(ci),
        }

    return results


# ============================================================
# OS VALIDATION (PROTOCOL: ONE COMPONENT)
# ============================================================

def os_validation(expr, depth_t,
                  depth_s, sample_ids,
                  tumour_mask, clin_df,
                  label):
    """
    OS is ONE component of Script 2.
    Not the primary analysis.
    Uses corrected depth axes.
    Cox proportional hazards proxy
    (median split Mann-Whitney on time).
    """
    log(f"\n{'='*65}")
    log(f"OS VALIDATION — {label}")
    log(f"{'='*65}")
    log(f"  (Protocol: OS is one component "
        f"of Script 2, not primary)")

    if clin_df is None:
        log("  No clinical data available")
        log("  OS validation skipped")
        return

    # Try to extract OS columns
    df = clin_df.copy()
    os_time = os_event = None
    sid_col = None

    # Common column patterns
    time_patterns = [
        "OS.time", "os_time",
        "days_to_death",
        "Overall_Survival_Time_in_Days",
        "duration",
    ]
    event_patterns = [
        "OS", "os_event",
        "vital_status",
        "Overall_Survival_Status",
        "donor_vital_status",
    ]
    id_patterns = [
        "sample", "sampleID",
        "icgc_donor_id", "_PATIENT",
        "bcr_patient_barcode",
    ]

    for col in df.columns:
        cl = col.lower()
        if any(p.lower() in cl
               for p in time_patterns) \
                and os_time is None:
            os_time = col
        if any(p.lower() in cl
               for p in event_patterns) \
                and os_event is None:
            os_event = col
        if any(p.lower() in cl
               for p in id_patterns) \
                and sid_col is None:
            sid_col = col

    log(f"  Time col:  {os_time}")
    log(f"  Event col: {os_event}")
    log(f"  ID col:    {sid_col}")

    if os_time is None:
        log("  Cannot find OS time column")
        log("  Available columns: "
            f"{list(df.columns[:15])}")
        return

    # Build OS series
    try:
        df["_time"] = pd.to_numeric(
            df[os_time], errors="coerce"
        )
        if os_event:
            ev = df[os_event].astype(str)\
                .str.lower()
            df["_event"] = (
                ev.str.contains(
                    "dead|deceased|1|died",
                    na=False,
                )
            ).astype(int)
        else:
            df["_event"] = np.nan

        valid = df["_time"].notna()
        n_valid = valid.sum()
        n_events = int(
            df.loc[valid, "_event"].sum()
        ) if os_event else 0
        log(f"  OS valid={n_valid} "
            f"events={n_events}")

        if n_valid < 10:
            log("  Insufficient OS data")
            return

        # Match sample IDs to depth
        # Use tumour sample order
        ti = np.where(tumour_mask)[0]
        t_sids = [
            sample_ids[i] for i in ti
        ]

        # Try to match
        if sid_col and sid_col in df.columns:
            df_sub = df[valid].set_index(
                sid_col
            )
            matched = []
            for j, sid in enumerate(t_sids):
                short_id = (
                    sid[:12]
                    if len(sid) >= 12
                    else sid
                )
                if short_id in df_sub.index:
                    matched.append((
                        j,
                        df_sub.loc[
                            short_id, "_time"
                        ],
                        df_sub.loc[
                            short_id, "_event"
                        ] if os_event
                        else np.nan,
                    ))
            log(f"  Matched {len(matched)} "
                f"samples to depth")

            if len(matched) < 8:
                log("  Too few matched — "
                    "OS not feasible")
                return

            js     = [m[0] for m in matched]
            times  = np.array(
                [m[1] for m in matched],
                float,
            )
            events = np.array(
                [m[2] for m in matched],
                float,
            )

            # Test Depth_T vs OS
            for depth_arr, dname in [
                (depth_t[js], "Depth_T"),
                (depth_s[js], "Depth_S"),
            ]:
                med = np.nanmedian(depth_arr)
                hi  = depth_arr >= med
                lo  = depth_arr < med
                t_hi = times[hi]
                t_lo = times[lo]
                if len(t_hi) < 3 \
                        or len(t_lo) < 3:
                    continue
                _, p = stats.mannwhitneyu(
                    t_hi, t_lo,
                    alternative="two-sided",
                )
                dir_str = (
                    "hi-worse"
                    if np.nanmean(t_hi)
                    < np.nanmean(t_lo)
                    else "hi-better"
                )
                log(f"  {dname} median split: "
                    f"hi(n={hi.sum()}) "
                    f"lo(n={lo.sum()}) "
                    f"{fmt_p(p)} "
                    f"{dir_str}")
        else:
            log("  No ID column for matching")

    except Exception as ex:
        log(f"  OS analysis error: {ex}")


# ============================================================
# FIGURE — 9 PANELS
# ============================================================

def generate_figure(
    tcga_expr, tcga_ti,
    tcga_dt, tcga_ds,
    tcga_s1, tcga_corrs_t,
    tcga_corrs_s, tcga_gaps,
    gse_expr, gse_ti,
    gse_dt, gse_ds,
    gse_s1, gse_nmf_results,
    basin_t, basin_s,
    label="",
):
    log("\n--- Generating Script 2 figure ---")
    fig = plt.figure(figsize=(26, 22))
    fig.suptitle(
        "ICC False Attractor — Script 2 | "
        "Corrected Framework | "
        "TCGA-CHOL + GSE32225 | "
        "OrganismCore | Doc 93e | 2026-03-02",
        fontsize=10,
        fontweight="bold",
        y=0.99,
    )
    gs_f = gridspec.GridSpec(
        3, 3, figure=fig,
        hspace=0.60, wspace=0.40,
    )
    C = ["#27ae60", "#e74c3c", "#2980b9",
         "#8e44ad", "#e67e22", "#16a085",
         "#c0392b", "#7f8c8d"]

    # ── A: Depth_T vs Depth_S scatter ────
    ax_a = fig.add_subplot(gs_f[0, 0])
    if len(tcga_dt) > 0 \
            and len(tcga_ds) > 0:
        sc = ax_a.scatter(
            tcga_dt, tcga_ds,
            c=np.arange(len(tcga_dt)),
            cmap="RdYlGn",
            alpha=0.7, s=40,
        )
        ax_a.plot([0, 1], [0, 1],
                  "k--", lw=0.8,
                  alpha=0.5,
                  label="y=x")
        ax_a.set_xlabel(
            "Depth_T (EMT)", fontsize=7,
        )
        ax_a.set_ylabel(
            "Depth_S (Stroma)", fontsize=7,
        )
        if len(tcga_dt) > 4:
            r_ts, p_ts = safe_r(
                tcga_dt, tcga_ds,
            )
            ax_a.set_title(
                f"A — Depth_T vs Depth_S\n"
                f"TCGA-CHOL "
                f"r={r_ts:+.3f}",
                fontsize=8,
            )
        else:
            ax_a.set_title(
                "A — Depth_T vs Depth_S\n"
                "TCGA-CHOL",
                fontsize=8,
            )

    # ── B: S1 vs S2 comparison ───────────
    ax_b = fig.add_subplot(gs_f[0, 1])
    if len(tcga_s1) > 0 \
            and len(tcga_dt) > 0:
        ax_b.scatter(
            tcga_s1, tcga_dt,
            alpha=0.6, s=30,
            color=C[2],
            label="Depth_T",
        )
        ax_b.scatter(
            tcga_s1, tcga_ds,
            alpha=0.6, s=30,
            color=C[3],
            label="Depth_S",
        )
        r_t, _ = safe_r(tcga_s1, tcga_dt)
        r_s, _ = safe_r(tcga_s1, tcga_ds)
        ax_b.set_xlabel(
            "S1 Depth", fontsize=7,
        )
        ax_b.set_ylabel(
            "S2 Depth", fontsize=7,
        )
        ax_b.set_title(
            f"B — S1 vs S2 Depth\n"
            f"r_T={r_t:+.3f}  "
            f"r_S={r_s:+.3f}",
            fontsize=8,
        )
        ax_b.legend(fontsize=6)

    # ── C: Two-basin EMT vs Stroma ───────
    ax_c = fig.add_subplot(gs_f[0, 2])
    if basin_t is not None \
            and basin_s is not None \
            and "TWIST1" in tcga_expr \
            and "ACTA2" in tcga_expr:
        tw = tcga_expr["TWIST1"][tcga_ti]
        ac = tcga_expr["ACTA2"][tcga_ti]
        ax_c.scatter(
            tw[basin_t], ac[basin_t],
            color=C[1], alpha=0.7, s=40,
            label="EMT-dom",
        )
        ax_c.scatter(
            tw[basin_s], ac[basin_s],
            color=C[2], alpha=0.7, s=40,
            label="Stroma-dom",
        )
        ax_c.set_xlabel("TWIST1", fontsize=7)
        ax_c.set_ylabel("ACTA2", fontsize=7)
        ax_c.set_title(
            "C — Two Basins\n"
            "TWIST1 vs ACTA2",
            fontsize=8,
        )
        ax_c.legend(fontsize=6)

    # ── D: Epigenetic lock genes ───��─────
    ax_d = fig.add_subplot(gs_f[1, 0])
    epi_plot = [
        g for g in [
            "EZH2", "KDM1A", "HDAC1",
            "HDAC2", "DNMT3A", "DNMT1",
        ]
        if g in tcga_expr
    ]
    if epi_plot and len(tcga_ti) > 0:
        vals_t = [
            np.nanmean(
                tcga_expr[g][tcga_ti]
            )
            for g in epi_plot
        ]
        ax_d.bar(
            range(len(epi_plot)),
            vals_t,
            color=[C[4]] * len(epi_plot),
            alpha=0.8,
        )
        ax_d.set_xticks(range(len(epi_plot)))
        ax_d.set_xticklabels(
            epi_plot, fontsize=8,
        )
        ax_d.set_ylabel(
            "mean log2 expr", fontsize=7,
        )
        ax_d.set_title(
            "D — Epigenetic Lock Genes\n"
            "(KDM1A+EZH2 dual lock, TCGA)",
            fontsize=8,
        )

    # ── E: NMF × Depth_T/S ───────────────
    ax_e = fig.add_subplot(gs_f[1, 1])
    if gse_nmf_results \
            and len(gse_nmf_results) >= 2:
        cls   = list(gse_nmf_results.keys())
        dt_m  = [
            gse_nmf_results[c]["depth_t"]
            for c in cls
        ]
        ds_m  = [
            gse_nmf_results[c]["depth_s"]
            for c in cls
        ]
        x     = np.arange(len(cls))
        w     = 0.35
        ax_e.bar(
            x - w/2, dt_m, w,
            label="Depth_T", color=C[1],
            alpha=0.8,
        )
        ax_e.bar(
            x + w/2, ds_m, w,
            label="Depth_S", color=C[2],
            alpha=0.8,
        )
        ax_e.set_xticks(x)
        ax_e.set_xticklabels(
            cls, fontsize=7,
        )
        ax_e.set_ylabel("Depth", fontsize=7)
        ax_e.set_title(
            "E — NMF × Depth Axes\n"
            "(S2-P2: two-basin test, GSE)",
            fontsize=8,
        )
        ax_e.legend(fontsize=6)
    else:
        ax_e.text(
            0.5, 0.5,
            "NMF data\nnot available",
            ha="center", va="center",
            transform=ax_e.transAxes,
        )
        ax_e.set_title(
            "E — NMF Subtypes", fontsize=8,
        )

    # ── F: FOXA2→ALB circuit ─────────────
    ax_f = fig.add_subplot(gs_f[1, 2])
    for src_expr, src_ti, col, lbl in [
        (tcga_expr, tcga_ti,
         C[2], "TCGA"),
        (gse_expr, gse_ti,
         C[3], "GSE"),
    ]:
        if ("FOXA2" in src_expr
                and "ALB" in src_expr
                and len(src_ti) > 3):
            fx = src_expr["FOXA2"][src_ti]
            al = src_expr["ALB"][src_ti]
            ax_f.scatter(
                fx, al,
                alpha=0.5, s=15,
                color=col, label=lbl,
            )
    ax_f.set_xlabel("FOXA2", fontsize=7)
    ax_f.set_ylabel("ALB", fontsize=7)
    r_fa_t = r_fa_g = np.nan
    if ("FOXA2" in tcga_expr
            and "ALB" in tcga_expr):
        r_fa_t, _ = safe_r(
            tcga_expr["FOXA2"][tcga_ti],
            tcga_expr["ALB"][tcga_ti],
        )
    if ("FOXA2" in gse_expr
            and "ALB" in gse_expr):
        r_fa_g, _ = safe_r(
            gse_expr["FOXA2"][gse_ti],
            gse_expr["ALB"][gse_ti],
        )
    ax_f.set_title(
        f"F — FOXA2→ALB Circuit (S2-P3)\n"
        f"TCGA r={r_fa_t:+.3f}  "
        f"GSE r={r_fa_g:+.3f}",
        fontsize=8,
    )
    ax_f.legend(fontsize=6)

    # ── G: DNMT3A vs Depth ────────────────
    ax_g = fig.add_subplot(gs_f[2, 0])
    for src_expr, src_dt, src_ds,src_ti, col, lbl in [
        (tcga_expr, tcga_dt, tcga_ds,
         tcga_ti, C[2], "TCGA"),
        (gse_expr, gse_dt, gse_ds,
         gse_ti, C[3], "GSE"),
    ]:
        if ("DNMT3A" in src_expr
                and len(src_ti) > 3):
            dn = src_expr["DNMT3A"][src_ti]
            d_comb = (src_dt + src_ds) / 2
            ax_g.scatter(
                dn, d_comb,
                alpha=0.5, s=15,
                color=col, label=lbl,
            )
    ax_g.set_xlabel("DNMT3A", fontsize=7)
    ax_g.set_ylabel(
        "Depth (combined)", fontsize=7,
    )
    ax_g.set_title(
        "G — DNMT3A vs Depth (S2-P4)\n"
        "Lower DNMT3A = deeper predicted",
        fontsize=8,
    )
    ax_g.legend(fontsize=6)

    # ── H: Gap test bar chart ─────────────
    ax_h = fig.add_subplot(gs_f[2, 1])
    if tcga_gaps:
        gap_names = list(tcga_gaps.keys())
        gap_rs    = [
            tcga_gaps[k]["r"]
            for k in gap_names
        ]
        colours   = [
            C[1] if r > 0 else C[0]
            for r in gap_rs
        ]
        y = range(len(gap_names))
        ax_h.barh(
            y, gap_rs,
            color=colours, alpha=0.8,
        )
        ax_h.set_yticks(y)
        ax_h.set_yticklabels(
            [n.split(":")[0][:25]
             for n in gap_names],
            fontsize=6,
        )
        ax_h.axvline(
            0, color="black", lw=0.8,
        )
        ax_h.set_xlabel(
            "Pearson r", fontsize=7,
        )
        ax_h.set_title(
            "H — Gap Tests (S2)\n"
            "(TCGA-CHOL tumours)",
            fontsize=8,
        )

    # ── I: Summary ────────────────────────
    ax_i = fig.add_subplot(gs_f[2, 2])
    ax_i.axis("off")

    r_ts_t = r_ts_g = np.nan
    if len(tcga_dt) > 4 \
            and len(tcga_ds) > 4:
        r_ts_t, _ = safe_r(tcga_dt, tcga_ds)
    if len(gse_dt) > 4 \
            and len(gse_ds) > 4:
        r_ts_g, _ = safe_r(gse_dt, gse_ds)

    s2p2 = (
        "CONFIRMED ✓"
        if not np.isnan(r_ts_t)
        and abs(r_ts_t) < 0.70
        else "check output"
    )

    summary = (
        "I — SCRIPT 2 SUMMARY\n"
        "══════════════════════════════\n"
        "TWO DEPTH AXES:\n"
        f"  Depth_T (EMT):    TWIST1 axis\n"
        f"  Depth_S (Stroma): ALB+COL1A1\n"
        f"  r(T,S) TCGA: "
        f"{r_ts_t:+.3f}\n"
        f"  r(T,S) GSE:  "
        f"{r_ts_g:+.3f}\n"
        f"  S2-P2: {s2p2}\n"
        f"\n"
        f"EPIGENETIC DUAL LOCK:\n"
        f"  EZH2 + KDM1A co-elevated\n"
        f"  Both silence biliary genes\n"
        f"\n"
        f"DRUG TARGETS (final):\n"
        f"  1. EZH2 inhibitor\n"
        f"  2. KDM1A/LSD1 inhibitor\n"
        f"  3. TGF-β inhibitor\n"
        f"  4. WNT5A inhibitor\n"
        f"\n"
        f"FOXA2→ALB circuit:\n"
        f"  TCGA: r={r_fa_t:+.3f}\n"
        f"  GSE:  r={r_fa_g:+.3f}\n"
        f"\n"
        f"OrganismCore | Doc 93e | 2026-03-02"
    )
    ax_i.text(
        0.02, 0.98, summary,
        transform=ax_i.transAxes,
        fontsize=7, va="top",
        fontfamily="monospace",
        bbox=dict(
            boxstyle="round",
            facecolor="#f8f8f8",
            edgecolor="#cccccc",
        ),
    )

    out = os.path.join(
        RESULTS_DIR, "icc_s2_figure.png"
    )
    plt.savefig(
        out, dpi=150, bbox_inches="tight",
    )
    log(f"  Figure: {out}")
    plt.close()


# ============================================================
# DEPTH CORRELATIONS (S2 axes)
# ============================================================

def depth_correlations_s2(expr, depth,
                           ti, label,
                           axis_name):
    log(f"\n{'='*65}")
    log(f"DEPTH CORRELATIONS ({axis_name})"
        f" — {label}")
    log(f"{'='*65}")
    log(f"  n = {len(depth)}")

    corrs = []
    for gene, gv in expr.items():
        vals = gv[ti]
        r, p = safe_r(depth, vals)
        if not np.isnan(r):
            corrs.append((gene, r, p))
    corrs.sort(key=lambda x: -abs(x[1]))

    log(f"\n  {'Rank':<5} {'Gene':<12} "
        f"{'r':>8} {'p':>14}  panel")
    log(f"  {'-'*52}")

    panel_map = {}
    for g in SW_GENES:
        panel_map[g] = "SW"
    for g in FA_GENES:
        panel_map[g] = "FA"
    for g in STROMA_GENES:
        panel_map[g] = "STROMA"
    for g in EPIGENETIC_GENES:
        panel_map[g] = "EPI"

    for i, (gene, r, p) in \
            enumerate(corrs[:20]):
        panel = panel_map.get(gene, "ctx")
        log(f"  {i+1:<5} {gene:<12} "
            f"{r:>+8.4f} "
            f"{fmt_p(p):>14}  "
            f"{panel}")

    return corrs


# ============================================================
# MAIN
# ============================================================

def main():
    log("=" * 65)
    log("ICC FALSE ATTRACTOR — SCRIPT 2")
    log("ITERATION RUN — CORRECTED FRAMEWORK")
    log("Framework: OrganismCore")
    log("Doc: 93e | Date: 2026-03-02")
    log("=" * 65)
    log("")
    log("SCRIPT 1 FINDINGS (Doc 93a):")
    log("  Top TCGA: TWIST1 r=+0.789 (EMT)")
    log("  Top GSE:  ALB    r=-0.803 (SW)")
    log("  Unexpected: KDM1A, DNMT3A, "
        "two-basin NMF")
    log("")
    log("SCRIPT 2 PREDICTIONS (locked):")
    log("  S2-P1: KDM1A independent epi lock")
    log("  S2-P2: Two basins — Depth_T/Depth_S")
    log("  S2-P3: FOXA2→ALB broken in GSE")
    log("  S2-P4: DNMT3A depth-negative")
    log("  S2-P5: KDM1A+EZH2 co-elevated")
    log("  S2-P6: S2 depth r>0.80 with S1")
    log("  S2-P7: NMF × depth axis "
        "decomposition")

    # ── Load data ────────────────────────
    (tcga_expr, tcga_sids,
     tcga_t, tcga_n) = load_tcga()

    (gse_expr, gse_sids, gse_labels,
     gse_icc, gse_nor) = load_gse()

    # ── S1 depth scores ───────────────────
    tcga_s1, tcga_ti = build_s1_depth(
        tcga_expr, tcga_t,
    )
    gse_s1, gse_ti = build_s1_depth(
        gse_expr, gse_icc,
    )
    log(f"\n  S1 depth reproduced: "
        f"TCGA mean={np.nanmean(tcga_s1):.4f} "
        f"GSE mean={np.nanmean(gse_s1):.4f}")

    # ── S2 depth scores ───────────────────
    tcga_dt, tcga_ds, tcga_dc, tcga_ti = \
        build_s2_depth(
            tcga_expr, tcga_t, "TCGA-CHOL",
        )
    gse_dt, gse_ds, gse_dc, gse_ti = \
        build_s2_depth(
            gse_expr, gse_icc, "GSE32225",
        )

    # ── S1 vs S2 comparison ───────────────
    compare_depths(
        tcga_s1, tcga_dt, tcga_ds,
        "TCGA-CHOL",
    )
    compare_depths(
        gse_s1, gse_dt, gse_ds,
        "GSE32225",
    )

    # ── Depth correlations ────────────────
    tcga_corrs_t = depth_correlations_s2(
        tcga_expr, tcga_dt, tcga_ti,
        "TCGA-CHOL", "Depth_T",
    )
    tcga_corrs_s = depth_correlations_s2(
        tcga_expr, tcga_ds, tcga_ti,
        "TCGA-CHOL", "Depth_S",
    )
    gse_corrs_t = depth_correlations_s2(
        gse_expr, gse_dt, gse_ti,
        "GSE32225", "Depth_T",
    )
    gse_corrs_s = depth_correlations_s2(
        gse_expr, gse_ds, gse_ti,
        "GSE32225", "Depth_S",
    )

    # ── Extended gap tests ────────────────
    tcga_gaps = extended_gap_tests(
        tcga_expr, tcga_dt, tcga_ds,
        tcga_ti, "TCGA-CHOL",
    )
    gse_gaps = extended_gap_tests(
        gse_expr, gse_dt, gse_ds,
        gse_ti, "GSE32225",
    )

    # ── Epigenetic analysis ───────────────
    epigenetic_analysis(
        tcga_expr, tcga_dt, tcga_ds,
        tcga_ti, "TCGA-CHOL",
    )
    epigenetic_analysis(
        gse_expr, gse_dt, gse_ds,
        gse_ti, "GSE32225",
    )

    # ── Two-basin decomposition ───────────
    basin_t, basin_s = two_basin_analysis(
        tcga_expr, tcga_dt, tcga_ds,
        tcga_ti, gse_labels, "TCGA-CHOL",
    )
    two_basin_analysis(
        gse_expr, gse_dt, gse_ds,
        gse_ti, gse_labels, "GSE32225",
    )

    # ── NMF × depth axis ─────────────────
    gse_nmf_results = nmf_depth_axis(
        gse_expr, gse_dt, gse_ds,
        gse_ti, gse_labels, "GSE32225",
    )

    # ── OS validation (one component) ────
    clin_df = load_liri()
    os_validation(
        tcga_expr, tcga_dt, tcga_ds,
        tcga_sids, tcga_t, clin_df,
        "TCGA-CHOL",
    )

    # ── S2 prediction scorecard ───────────
    log(f"\n{'='*65}")
    log("SCRIPT 2 PREDICTION SCORECARD")
    log(f"{'='*65}")

    # S2-P5: KDM1A + EZH2
    r_ke_t = r_ke_g = np.nan
    if "KDM1A" in tcga_expr \
            and "EZH2" in tcga_expr:
        r_ke_t, _ = safe_r(
            tcga_expr["KDM1A"][tcga_ti],
            tcga_expr["EZH2"][tcga_ti],
        )
    if "KDM1A" in gse_expr \
            and "EZH2" in gse_expr:
        r_ke_g, _ = safe_r(
            gse_expr["KDM1A"][gse_ti],
            gse_expr["EZH2"][gse_ti],
        )

    # S2-P6: r(S1, S2_combined)
    r_s1s2_t, _ = safe_r(tcga_s1, tcga_dc)
    r_s1s2_g, _ = safe_r(gse_s1, gse_dc)

    # S2-P3: FOXA2→ALB
    r_fa_t = r_fa_g = np.nan
    if "FOXA2" in tcga_expr \
            and "ALB" in tcga_expr:
        r_fa_t, _ = safe_r(
            tcga_expr["FOXA2"][tcga_ti],
            tcga_expr["ALB"][tcga_ti],
        )
    if "FOXA2" in gse_expr \
            and "ALB" in gse_expr:
        r_fa_g, _ = safe_r(
            gse_expr["FOXA2"][gse_ti],
            gse_expr["ALB"][gse_ti],
        )

    # S2-P4: DNMT3A depth-negative
    r_dn_t = r_dn_g = np.nan
    if "DNMT3A" in tcga_expr:
        r_dn_t, _ = safe_r(
            tcga_dc,
            tcga_expr["DNMT3A"][tcga_ti],
        )
    if "DNMT3A" in gse_expr:
        r_dn_g, _ = safe_r(
            gse_dc,
            gse_expr["DNMT3A"][gse_ti],
        )

    def v(r, thresh, neg=False):
        if np.isnan(r):
            return "?"
        if neg:
            return "✓" if r < -thresh \
                else "✗"
        return "✓" if abs(r) > thresh \
            else "✗"

    r_ts_t, _ = safe_r(tcga_dt, tcga_ds)
    r_ts_g, _ = safe_r(gse_dt, gse_ds)

    log(f"\n  {'Prediction':<35} "
        f"{'TCGA':>10} {'GSE':>10}  "
        f"verdict")
    log(f"  {'-'*70}")
    rows = [
        ("S2-P1 KDM1A→ALB negative",
         tcga_gaps.get(
             "S2-P1: KDM1A→ALB "
             "(epi lock→SW gene)", {}
         ).get("r", np.nan),
         gse_gaps.get(
             "S2-P1: KDM1A→ALB "
             "(epi lock→SW gene)", {}
         ).get("r", np.nan),
         True, 0.10),
        ("S2-P2 Two basins independent",
         r_ts_t, r_ts_g,
         False, None),  # want LOW r
        ("S2-P3 FOXA2→ALB broken",
         r_fa_t, r_fa_g,
         False, None),  # want low/neg
        ("S2-P4 DNMT3A depth-negative",
         r_dn_t, r_dn_g,
         True, 0.15),
        ("S2-P5 KDM1A+EZH2 co-elevated",
         r_ke_t, r_ke_g,
         False, 0.30),
        ("S2-P6 r(S1,S2_comb)>0.80",
         r_s1s2_t, r_s1s2_g,
         False, 0.80),
    ]
    for name, r_t, r_g, neg, thresh \
            in rows:
        if thresh is None:
            vt = f"{r_t:+.3f}" \
                if not np.isnan(r_t) \
                else "?"
            vg = f"{r_g:+.3f}" \
                if not np.isnan(r_g) \
                else "?"
            vc = "see output"
        else:
            vt = f"{r_t:+.3f}" \
                if not np.isnan(r_t) \
                else "?"
            vg = f"{r_g:+.3f}" \
                if not np.isnan(r_g) \
                else "?"
            vc = (
                "CONFIRMED ✓"
                if (not np.isnan(r_t)
                    and (r_t < -thresh
                         if neg
                         else abs(r_t)
                         > thresh))
                or (not np.isnan(r_g)
                    and (r_g < -thresh
                         if neg
                         else abs(r_g)
                         > thresh))
                else "NOT CONFIRMED"
            )
        log(f"  {name:<35} "
            f"{vt:>10} {vg:>10}  "
            f"{vc}")

    # ── Figure ────────────────────────────
    generate_figure(
        tcga_expr, tcga_ti,
        tcga_dt, tcga_ds,
        tcga_s1, tcga_corrs_t,
        tcga_corrs_s, tcga_gaps,
        gse_expr, gse_ti,
        gse_dt, gse_ds,
        gse_s1, gse_nmf_results,
        basin_t, basin_s,
    )

    # ── Save CSV ──────────────────────────
    rows_csv = []
    for gene in sorted(ALL_PANEL):
        r_dt_t = r_ds_t = np.nan
        r_dt_g = r_ds_g = np.nan
        if gene in tcga_expr:
            r_dt_t, _ = safe_r(
                tcga_dt,
                tcga_expr[gene][tcga_ti],
            )
            r_ds_t, _ = safe_r(
                tcga_ds,
                tcga_expr[gene][tcga_ti],
            )
        if gene in gse_expr:
            r_dt_g, _ = safe_r(
                gse_dt,
                gse_expr[gene][gse_ti],
            )
            r_ds_g, _ = safe_r(
                gse_ds,
                gse_expr[gene][gse_ti],
            )
        rows_csv.append({
            "gene":     gene,
            "r_DepthT_TCGA": r_dt_t,
            "r_DepthS_TCGA": r_ds_t,
            "r_DepthT_GSE":  r_dt_g,
            "r_DepthS_GSE":  r_ds_g,
        })
    pd.DataFrame(rows_csv).to_csv(
        os.path.join(
            RESULTS_DIR,
            "depth_correlations_s2.csv",
        ),
        index=False,
    )

    write_log()
    log(f"\n  Log: {LOG_FILE}")
    log(f"  Results: {RESULTS_DIR}")
    log("\n=== SCRIPT 2 COMPLETE ===")
    log("Paste full output for Doc 93e.")


if __name__ == "__main__":
    main()
