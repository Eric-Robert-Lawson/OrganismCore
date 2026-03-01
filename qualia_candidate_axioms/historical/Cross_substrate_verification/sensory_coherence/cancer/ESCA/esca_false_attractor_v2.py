"""
ESOPHAGEAL CANCER — FALSE ATTRACTOR ANALYSIS
SCRIPT 2 — CORRECTED FRAMEWORK
Dataset: GSE26886 (reused from Script 1)
Platform: GPL570 Affymetrix HGU133Plus2

FRAMEWORK: OrganismCore Principles-First
Doc: 90b | Date: 2026-03-01

SCRIPT 1 FINDINGS (Doc 90a):
  ESCC:
    Confirmed: IVL DOWN / EGFR/FGFR1/MYC UP
    Inverted:  NOTCH1/KRT10/SPRR1A/DSG1/KRT4
               ALL elevated — squamous FA markers
               not switch genes
    Key depth driver: CDKN1A r=-0.84**
    Attractor: hyperactivated squamous progenitor
               terminal cornification block (IVL)
  EAC:
    Confirmed: CDH1 DOWN / CDX2/KRT20/VEGFA UP
    Inverted:  ZEB1 DOWN (squamous identity lost)
               TFF1 UP +2127% (strongest signal)
               NOTCH1 UP (FA not switch)
    Key depth drivers: APC r=-0.63** /
                       CTNNB1 r=-0.56** (paradox)
                       HDAC1 r=+0.56** /
                       EZH2 r=+0.49*
    Epigenetic: EZH2 + HDAC1 both elevated
  Cross-cancer:
    CDX2 circuit broken 1/5 (same as STAD) ✓
    ZEB1 = squamous/columnar separator
    AURKA absent from GPL570 matrix

SCRIPT 2 PREDICTIONS (locked 2026-03-01):
  S2-1: ZEB1/TFF1 shared axis separates
        all 4 groups on single continuum
  S2-2: TFF1 anchors EAC depth better
        than CDX2 (r(TFF1)>r(CDX2))
  S2-3: APC paradox = CIN not Wnt:
        AXIN2 flat or down in deep EAC
        (canonical Wnt not active)
  S2-4: HDAC1+EZH2 combined score
        outperforms either alone in EAC
  S2-5: CDKN1A corrected ESCC depth
        stronger than original panel
  S2-6: ERBB2 HER2-high EAC has
        different depth than HER2-low
  S2-7: SPRR1A elevation marks
        poorly differentiated EAC subtype
        (co-elevated with CDC20/MKI67)

Author: Eric Robert Lawson
Framework: OrganismCore
"""

import os
import re
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

BASE_DIR     = "./esca_false_attractor/"
RESULTS_S1   = os.path.join(BASE_DIR, "results")
RESULTS_DIR  = os.path.join(
    BASE_DIR, "results_s2"
)
LOG_FILE     = os.path.join(
    RESULTS_DIR,
    "analysis_log_s2.txt",
)

os.makedirs(RESULTS_DIR, exist_ok=True)

# Reuse Script 1 download
MATRIX_FILE = os.path.join(
    BASE_DIR, "GSE26886_series_matrix.txt.gz"
)
MATRIX_URL  = (
    "https://ftp.ncbi.nlm.nih.gov/geo/series/"
    "GSE26nnn/GSE26886/matrix/"
    "GSE26886_series_matrix.txt.gz"
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
    if p is None or (
        isinstance(p, float) and np.isnan(p)
    ):
        return "p=N/A   "
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
# PROBE MAP — extended for Script 2
# Adds Wnt pathway genes and
# additional markers not in Script 1
# ============================================================

PROBE_MAP = {
    # Script 1 probes (all retained)
    "209183_s_at": "NOTCH1",
    "209130_at":   "KRT1",
    "210633_x_at": "KRT10",
    "205555_s_at": "SPRR1A",
    "206360_at":   "LORICRIN",
    "207724_s_at": "KRT4",
    "210602_s_at": "KRT13",
    "214599_at":   "IVL",
    "205277_at":   "DSG3",
    "204998_s_at": "DSG1",
    "213541_s_at": "SOX2",
    "209905_at":   "TP63",
    "201820_at":   "KRT5",
    "201667_s_at": "KRT14",
    "201983_s_at": "EGFR",
    "208712_at":   "CCND1",
    "204579_at":   "FGFR1",
    "212791_at":   "MYC",
    "214854_at":   "PIK3CA",
    "209288_s_at": "CDX2",
    "207257_at":   "MUC2",
    "213599_at":   "KRT20",
    "201843_s_at": "TFF3",
    "205014_at":   "MUC5B",
    "204683_at":   "TFF1",
    "207147_at":   "MUC5AC",
    "220752_at":   "GKN1",
    "219446_at":   "CLDN18",
    "209189_at":   "PGC",
    "203131_at":   "ZEB2",
    "218559_s_at": "ZEB1",
    "209763_at":   "SNAI2",
    "216262_s_at": "SNAI1",
    "214451_at":   "TWIST1",
    "201131_s_at": "FN1",
    "201130_s_at": "CDH2",
    "201733_at":   "CDH1",
    "201858_s_at": "VIM",
    "204418_at":   "AURKA",
    "202095_s_at": "MKI67",
    "201291_s_at": "TOP2A",
    "203213_at":   "CDC20",
    "214710_s_at": "CCNB1",
    "202240_at":   "PLK1",
    "201202_at":   "PCNA",
    "208641_s_at": "CDK4",
    "209644_x_at": "CDKN2A",
    "202284_s_at": "CDKN1A",
    "202107_s_at": "RB1",
    "201015_s_at": "CCNE1",
    "216836_s_at": "ERBB2",
    "205047_s_at": "ERBB3",
    "209091_at":   "ERBB4",
    "213807_at":   "MET",
    "204363_at":   "FGFR2",
    "210512_s_at": "VEGFA",
    "203934_at":   "KDR",
    "203685_at":   "BCL2",
    "200797_s_at": "MCL1",
    "211300_s_at": "BAX",
    "203358_s_at": "EZH2",
    "212155_at":   "KDM6A",
    "218457_at":   "DNMT3A",
    "214651_s_at": "TET2",
    "201833_at":   "HDAC1",
    "220436_s_at": "HDAC2",
    "201474_s_at": "CTNNB1",
    "205990_s_at": "WNT5A",
    "204990_s_at": "APC",
    "222696_at":   "AXIN2",
    "209807_at":   "NOTCH2",
    "209097_at":   "JAG1",
    "203411_s_at": "HES1",
    "203085_s_at": "TGFB1",
    "212171_at":   "TGFB2",
    "213815_at":   "TGFBR1",
    "204791_at":   "TGFBR2",
    "201746_at":   "TP53",
    "207035_at":   "MDM2",
    "212897_at":   "MLH1",
    "214057_at":   "MSH6",
    "200989_at":   "HIF1A",
    "200650_s_at": "LDHA",
    "206804_at":   "CD8A",
    "206026_s_at": "FOXP3",
    "207429_at":   "PDCD1",
    "223834_at":   "CD274",
    "207828_at":   "CDK6",
    # Script 2 additions — Wnt resolution
    "201236_s_at": "TCF7L2",   # TCF4
    "219709_at":   "LEF1",
    "204336_s_at": "AXIN1",
    "209833_s_at": "MYC",      # alternate
    "209291_at":   "LGR5",     # Wnt stem
    "201540_at":   "CTGF",     # Wnt target
    # Script 2 additions — Barrett gap
    "204831_at":   "SOX9",
    "209735_at":   "KLF4",
    "213508_at":   "FOXA2",
    "202018_s_at": "NKX2-1",
    "205047_s_at": "ERBB3",
    # Script 2 additions — ESCC
    "204114_at":   "CDKN1B",   # p27
    "209773_s_at": "CDKN2B",   # p15
    "212241_at":   "CCNA2",
    "203398_at":   "CDK2",
    # Script 2 additions — immune
    "210029_at":   "CD274",    # PD-L1 alt
    "213761_at":   "TIGIT",
    "210254_at":   "LAG3",
    # Script 2 additions — apoptosis
    "209616_s_at": "BCL2L1",   # BCL-XL
    "209790_s_at": "BIRC5",    # survivin
    "204353_s_at": "BIRC2",
}

GENE_TO_PROBES = {}
for probe, gene in PROBE_MAP.items():
    if gene not in GENE_TO_PROBES:
        GENE_TO_PROBES[gene] = []
    GENE_TO_PROBES[gene].append(probe)

TARGET_GENES = sorted(set(PROBE_MAP.values()))

# ============================================================
# CORRECTED GENE PANELS
# From Script 1 findings
# ============================================================

# ESCC — corrected from 90a
# Switch: only what is truly suppressed
ESCC_SWITCH_S2 = [
    "IVL",      # confirmed DOWN -62.9% ***
    "CDKN1A",   # r=-0.84** depth driver
    "CDKN2A",   # cell cycle brake
    "RB1",      # tumor suppressor
]

# FA: confirmed + inverted-to-FA
ESCC_FA_S2 = [
    "EGFR",     # confirmed UP +364.8% ***
    "FGFR1",    # confirmed UP +52.4%  ***
    "MYC",      # confirmed UP +346.3% ***
    "NOTCH1",   # inverted — FA marker
    "KRT10",    # inverted — squamous FA
    "DSG1",     # inverted — squamous FA
    "CDK4",     # r=+0.57 depth
]

# EAC — corrected from 90a
# Switch: confirmed + inverted-to-switch
EAC_SWITCH_S2 = [
    "CDH1",     # confirmed DOWN -557% ***
    "ZEB1",     # inverted — squamous lost
    "KRT5",     # r=-0.48* squamous lost
    "APC",      # r=-0.63** depth driver
    "CTNNB1",   # r=-0.56** paradox gene
]

# FA: confirmed + inverted-to-FA
EAC_FA_S2 = [
    "CDX2",     # confirmed UP +136% ***
    "TFF1",     # inverted — strongest FA
    "KRT20",    # confirmed UP +166% *
    "VEGFA",    # confirmed UP +133% **
    "NOTCH1",   # inverted — FA marker
    "HDAC1",    # r=+0.56** epigenetic
    "EZH2",     # r=+0.49* epigenetic
]

# Shared axis — for cross-subtype
# comparison on single continuum
SHARED_SQUAMOUS = ["ZEB1", "KRT5", "IVL"]
SHARED_COLUMNAR = ["TFF1", "CDX2", "CDH1"]

# ============================================================
# DOWNLOAD (reuse S1 file)
# ============================================================

def download_file(url, dest):
    if os.path.exists(dest):
        log(f"  Reusing S1 download: {dest} "
            f"({os.path.getsize(dest):,} bytes)")
        return True
    log(f"  Downloading: {url}")
    try:
        r = requests.get(url, timeout=180)
        if r.status_code == 200:
            with open(dest, "wb") as f:
                f.write(r.content)
            log(f"  Saved: {dest}")
            return True
        log(f"  HTTP {r.status_code}")
        return False
    except Exception as e:
        log(f"  Error: {e}")
        return False

# ============================================================
# PARSE SERIES MATRIX (same as S1)
# ============================================================

def parse_series_matrix(filepath):
    log("")
    log("=" * 65)
    log("PARSE SERIES MATRIX (reused S1)")
    log(f"  File: {filepath}")
    log("=" * 65)

    opener = (
        gzip.open(
            filepath, "rt",
            encoding="utf-8",
            errors="ignore",
        )
        if filepath.endswith(".gz")
        else open(filepath, "r",
                  encoding="utf-8",
                  errors="ignore")
    )

    sample_ids    = []
    sample_titles = []
    in_table      = False
    header_cols   = []
    probe_ids     = []
    rows          = []

    with opener as f:
        for line in f:
            line = line.rstrip("\n").rstrip("\r")

            if "!Sample_geo_accession" in line:
                parts = line.split("\t")
                sample_ids = [
                    p.strip().strip('"')
                    for p in parts[1:]
                    if p.strip().strip('"')
                ]

            elif "!Sample_title" in line:
                parts = line.split("\t")
                sample_titles = [
                    p.strip().strip('"')
                    for p in parts[1:]
                    if p.strip().strip('"')
                ]

            elif (
                "series_matrix_table_begin"
                in line
            ):
                in_table = True
                continue

            elif (
                "series_matrix_table_end"
                in line
            ):
                break

            elif in_table:
                parts = [
                    p.strip().strip('"')
                    for p in line.split("\t")
                ]

                if not header_cols:
                    header_cols = parts
                    continue

                if not parts or not parts[0]:
                    continue

                probe_id = parts[0]
                if probe_id not in PROBE_MAP:
                    continue

                try:
                    vals = [
                        float(p)
                        if p not in [
                            "", "null", "NA",
                            "nan", "N/A",
                        ] else np.nan
                        for p in parts[1:]
                    ]
                except ValueError:
                    continue

                if len(vals) != (
                    len(header_cols) - 1
                ):
                    continue

                probe_ids.append(probe_id)
                rows.append(vals)

    log(f"  Probes found : {len(probe_ids)}")
    log(f"  Samples      : {len(sample_ids)}")

    if not probe_ids:
        return None, None

    cols = header_cols[1:]
    n_c  = len(rows[0]) if rows else 0
    cols = cols[:n_c]

    df = pd.DataFrame(
        rows,
        index=probe_ids,
        columns=cols,
        dtype=float,
    )

    gene_expr = {}
    for gene, probes in GENE_TO_PROBES.items():
        avail = [
            p for p in probes
            if p in df.index
        ]
        if not avail:
            continue
        if len(avail) == 1:
            gene_expr[gene] = (
                df.loc[avail[0]].values
            )
        else:
            meds = [
                df.loc[p].median()
                for p in avail
            ]
            best = avail[np.argmax(meds)]
            gene_expr[gene] = (
                df.loc[best].values
            )

    df_genes = pd.DataFrame(
        gene_expr, index=cols, dtype=float
    )

    meta = pd.DataFrame(index=df_genes.index)
    if len(sample_titles) == len(df_genes):
        meta["title"] = sample_titles
    elif (sample_ids
          and len(sample_titles)
              == len(sample_ids)):
        tmap = dict(
            zip(sample_ids, sample_titles)
        )
        meta["title"] = [
            tmap.get(s, "")
            for s in df_genes.index
        ]

    log(f"  Genes mapped : "
        f"{len(df_genes.columns)}")
    log(f"  New S2 genes : "
        f"{[g for g in df_genes.columns if g in ['TCF7L2','LEF1','AXIN1','LGR5','SOX9','KLF4','FOXA2','CDKN1B','BIRC5','BCL2L1']]}")

    return df_genes, meta

# ============================================================
# CLASSIFY SAMPLES
# ============================================================

def classify_samples(df_genes, meta):
    groups = []
    for s in df_genes.index:
        title = ""
        if (
            meta is not None
            and "title" in meta.columns
            and s in meta.index
        ):
            title = str(
                meta.loc[s, "title"]
            ).lower()

        if any(x in title for x in [
            "barrett", "be_", "be ",
        ]):
            groups.append("Barrett")
        elif any(x in title for x in [
            "adenocarcinoma", "eac", "adeno",
        ]):
            groups.append("EAC")
        elif any(x in title for x in [
            "squamous cell carcinoma",
            "escc", "scc",
        ]):
            groups.append("ESCC")
        elif any(x in title for x in [
            "normal", "squamous epithelium",
            "squamous epitheliu",
        ]):
            groups.append("Normal")
        else:
            groups.append("Unknown")

    return pd.Series(groups,
                     index=df_genes.index)

# ============================================================
# DEPTH SCORE
# ============================================================

def build_depth_score(
    df, switch, fa, label
):
    gc  = list(df.columns)
    sw  = [g for g in switch if g in gc]
    fa_ = [g for g in fa     if g in gc]

    depth = pd.Series(
        np.zeros(len(df)),
        index=df.index,
        dtype=float,
    )
    n = 0
    if sw:
        depth += (
            1 - norm01(df[sw].mean(axis=1))
        )
        n += 1
    if fa_:
        depth += norm01(
            df[fa_].mean(axis=1)
        )
        n += 1
    if n > 0:
        depth /= n

    log(f"  {label} depth "
        f"(n={len(df)}): "
        f"mean={depth.mean():.4f} "
        f"std={depth.std():.4f} "
        f"min={depth.min():.4f} "
        f"max={depth.max():.4f}")
    return depth

# ============================================================
# DEPTH CORRELATIONS
# ============================================================

def depth_correlations(df, depth, label):
    corrs = []
    for gene in df.columns:
        rv, pv = safe_pearsonr(
            depth.values, df[gene].values
        )
        if not np.isnan(rv):
            corrs.append((gene, rv, pv))

    corrs.sort(
        key=lambda x: abs(x[1]),
        reverse=True,
    )

    log(f"\n  TOP 15 POSITIVE "
        f"(UP in deep {label}):")
    log(f"  {'Gene':<12} {'r':>8}  p-value")
    log(f"  {'-'*35}")
    for g, r, p in [
        x for x in corrs if x[1] > 0
    ][:15]:
        log(f"  {g:<12} {r:>+8.4f}  "
            f"{fmt_p(p)}")

    log(f"\n  TOP 15 NEGATIVE "
        f"(DOWN in deep {label}):")
    log(f"  {'Gene':<12} {'r':>8}  p-value")
    log(f"  {'-'*35}")
    for g, r, p in [
        x for x in corrs if x[1] < 0
    ][:15]:
        log(f"  {g:<12} {r:>+8.4f}  "
            f"{fmt_p(p)}")

    return corrs

# ============================================================
# TEST 1: SHARED ZEB1/TFF1 AXIS
# Single continuum across all 4 groups
# ============================================================

def shared_axis_test(groups):
    log("")
    log("=" * 65)
    log("TEST 1: SHARED ZEB1/TFF1 AXIS")
    log("Prediction S2-1: single axis")
    log("separates all 4 groups cleanly")
    log("=" * 65)

    all_samples = pd.concat(
        list(groups.values())
    )
    gc = list(all_samples.columns)

    sq_genes = [
        g for g in SHARED_SQUAMOUS
        if g in gc
    ]
    col_genes = [
        g for g in SHARED_COLUMNAR
        if g in gc
    ]

    log(f"  Squamous axis genes: {sq_genes}")
    log(f"  Columnar axis genes: {col_genes}")

    if not sq_genes or not col_genes:
        log("  Insufficient genes for axis")
        return None

    # Shared axis score:
    # 0 = pure squamous / 1 = pure columnar
    sq_score  = norm01(
        all_samples[sq_genes].mean(axis=1)
    )
    col_score = norm01(
        all_samples[col_genes].mean(axis=1)
    )

    # axis = columnar - squamous (normalized)
    raw_axis = (
        col_score.values - sq_score.values
    )
    axis_min = raw_axis.min()
    axis_max = raw_axis.max()
    if axis_max > axis_min:
        shared_axis = (
            raw_axis - axis_min
        ) / (axis_max - axis_min)
    else:
        shared_axis = np.full(
            len(raw_axis), 0.5
        )

    shared_series = pd.Series(
        shared_axis,
        index=all_samples.index,
    )

    log(f"\n  Shared axis score by group:")
    log(f"  {'Group':<12} {'n':>4}  "
        f"{'mean':>8}  {'std':>8}")
    log(f"  {'-'*38}")

    group_order = [
        "Normal", "Barrett", "EAC", "ESCC"
    ]
    group_means = {}
    for g in group_order:
        if g not in groups:
            continue
        idx   = groups[g].index
        vals  = shared_series[idx].values
        group_means[g] = vals.mean()
        log(f"  {g:<12} {len(idx):>4}  "
            f"{vals.mean():>8.4f}  "
            f"{vals.std():>8.4f}")

    # Test separation
    log(f"\n  Group separation tests:")
    pairs = [
        ("Normal", "Barrett"),
        ("Barrett", "EAC"),
        ("Normal", "EAC"),
        ("EAC", "ESCC"),
        ("Normal", "ESCC"),
    ]
    for g1, g2 in pairs:
        if g1 not in groups or g2 not in groups:
            continue
        v1 = shared_series[groups[g1].index]
        v2 = shared_series[groups[g2].index]
        _, pp = safe_mwu(
            v1.values, v2.values, "two-sided"
        )
        direction = (
            ">" if v1.mean() > v2.mean()
            else "<"
        )
        log(f"  {g1} {direction} {g2}: "
            f"{fmt_p(pp)}")

    # Check if prediction confirmed
    # Expected order: ESCC > Normal > Barrett
    # > EAC on squamous axis
    # Or: EAC > Barrett > Normal > ESCC
    # on columnar axis
    if (
        "ESCC" in group_means
        and "Normal" in group_means
        and "EAC" in group_means
    ):
        escc_m = group_means["ESCC"]
        norm_m = group_means["Normal"]
        eac_m  = group_means["EAC"]

        if eac_m < escc_m and eac_m < norm_m:
            log(f"\n  PREDICTION S2-1 CONFIRMED ✓")
            log(f"  EAC scores low on squamous/")
            log(f"  columnar axis (pure columnar)")
            log(f"  ESCC scores high (squamous)")
        else:
            log(f"\n  PREDICTION S2-1 PARTIAL")
            log(f"  Axis does not cleanly separate")

    return shared_series

# ============================================================
# TEST 2: TFF1 vs CDX2 AS EAC ANCHOR
# ============================================================

def tff1_vs_cdx2_test(eac, depth_eac_s1):
    log("")
    log("=" * 65)
    log("TEST 2: TFF1 vs CDX2 AS EAC ANCHOR")
    log("Prediction S2-2: r(TFF1) > r(CDX2)")
    log("Script 1 TFF1 was +2127% in EAC")
    log("=" * 65)

    gc = list(eac.columns)

    if depth_eac_s1 is None:
        log("  No S1 depth — build from S1 panel")
        return

    results = {}
    for gene in ["TFF1", "CDX2", "KRT20",
                 "VEGFA", "NOTCH1", "SPRR1A",
                 "HDAC1", "EZH2", "CDC20"]:
        if gene not in gc:
            continue
        rv, pv = safe_pearsonr(
            depth_eac_s1.values,
            eac[gene].values,
        )
        results[gene] = (rv, pv)
        log(f"  r({gene:<8}, depth_S1) = "
            f"{rv:>+8.4f}  {fmt_p(pv)}")

    if (
        "TFF1" in results
        and "CDX2" in results
    ):
        r_tff1 = abs(results["TFF1"][0])
        r_cdx2 = abs(results["CDX2"][0])
        log(f"\n  |r(TFF1)| = {r_tff1:.4f}")
        log(f"  |r(CDX2)| = {r_cdx2:.4f}")
        if r_tff1 > r_cdx2:
            log(f"  PREDICTION S2-2 CONFIRMED ✓")
            log(f"  TFF1 anchors EAC depth better")
        else:
            log(f"  PREDICTION S2-2 NOT CONFIRMED")
            log(f"  CDX2 remains stronger anchor")

    return results

# ============================================================
# TEST 3: APC/WNT PARADOX RESOLUTION
# ============================================================

def apc_wnt_resolution(eac, depth_eac):
    log("")
    log("=" * 65)
    log("TEST 3: APC/WNT PARADOX RESOLUTION")
    log("S1: APC r=-0.63** / CTNNB1 r=-0.56**")
    log("Both suppressed in deep EAC")
    log("Prediction S2-3: AXIN2 flat or down")
    log("(canonical Wnt not active = CIN)")
    log("=" * 65)

    gc = list(eac.columns)

    wnt_genes = [
        ("APC",     "Wnt brake — suppressed S1"),
        ("CTNNB1",  "beta-catenin — suppressed S1"),
        ("AXIN2",   "Wnt target — KEY TEST"),
        ("AXIN1",   "Wnt scaffold"),
        ("TCF7L2",  "Wnt TF / TCF4"),
        ("LEF1",    "Wnt TF"),
        ("LGR5",    "Wnt stem cell marker"),
        ("CTGF",    "Wnt target"),
        ("MYC",     "Wnt target (also ESCC FA)"),
        ("CCND1",   "Wnt target (also ESCC FA)"),
        ("WNT5A",   "non-canonical Wnt"),
    ]

    log(f"\n  {'Gene':<10} {'r with depth':>14}  "
        f"p-value         Role")
    log(f"  {'-'*65}")

    axin2_r = np.nan
    for gene, role in wnt_genes:
        if gene not in gc:
            log(f"  {gene:<10} NOT IN MATRIX  "
                f"  {role}")
            continue
        rv, pv = safe_pearsonr(
            depth_eac.values,
            eac[gene].values,
        )
        log(f"  {gene:<10} {rv:>+14.4f}  "
            f"{fmt_p(pv):>14}  {role}")
        if gene == "AXIN2":
            axin2_r = rv

    log(f"\n  INTERPRETATION:")
    if not np.isnan(axin2_r):
        if abs(axin2_r) < 0.15:
            log(f"  AXIN2 flat (r={axin2_r:.4f})")
            log(f"  PREDICTION S2-3 CONFIRMED ✓")
            log(f"  Canonical Wnt NOT active")
            log(f"  APC loss = CIN mechanism")
            log(f"  not Wnt activation")
        elif axin2_r > 0.15:
            log(f"  AXIN2 positive (r={axin2_r:.4f})")
            log(f"  PREDICTION S2-3 NOT CONFIRMED")
            log(f"  Wnt pathway IS active in deep EAC")
            log(f"  Tankyrase inhibitor is drug target")
        else:
            log(f"  AXIN2 negative (r={axin2_r:.4f})")
            log(f"  Wnt suppressed in deep EAC")
            log(f"  APC loss = non-Wnt mechanism")

# ============================================================
# TEST 4: HDAC1 + EZH2 COMBINED
# EPIGENETIC SCORE
# ============================================================

def epigenetic_combined_test(
    eac, depth_eac
):
    log("")
    log("=" * 65)
    log("TEST 4: HDAC1 + EZH2 COMBINED")
    log("Epigenetic depth score")
    log("Prediction S2-4: combined score")
    log("outperforms either alone")
    log("=" * 65)

    gc = list(eac.columns)

    epi_genes = [
        "EZH2", "HDAC1", "HDAC2",
        "KDM6A", "TET2", "DNMT3A",
        "CDKN2A",
    ]

    log(f"\n  Individual epigenetic correlations:")
    log(f"  {'Gene':<10} {'r':>8}  p-value")
    log(f"  {'-'*35}")

    r_vals = {}
    for gene in epi_genes:
        if gene not in gc:
            continue
        rv, pv = safe_pearsonr(
            depth_eac.values,
            eac[gene].values,
        )
        r_vals[gene] = (rv, pv)
        log(f"  {gene:<10} {rv:>+8.4f}  "
            f"{fmt_p(pv)}")

    # Build combined score
    epi_pos = [
        g for g in ["EZH2", "HDAC1", "HDAC2"]
        if g in gc
    ]
    if len(epi_pos) >= 2:
        epi_score = norm01(
            eac[epi_pos].mean(axis=1)
        )
        rv_comb, pv_comb = safe_pearsonr(
            depth_eac.values,
            epi_score.values,
        )
        log(f"\n  Combined HDAC1+EZH2 score:")
        log(f"  r = {rv_comb:+.4f}  "
            f"{fmt_p(pv_comb)}")

        # Compare to individuals
        r_ezh2 = abs(
            r_vals.get("EZH2", (np.nan,))[0]
        )
        r_hdac1 = abs(
            r_vals.get("HDAC1", (np.nan,))[0]
        )
        r_comb  = abs(rv_comb)

        log(f"\n  |r(EZH2)|    = {r_ezh2:.4f}")
        log(f"  |r(HDAC1)|   = {r_hdac1:.4f}")
        log(f"  |r(combined)]= {r_comb:.4f}")

        best_individual = max(r_ezh2, r_hdac1)
        if r_comb > best_individual:
            log(f"  PREDICTION S2-4 CONFIRMED ✓")
            log(f"  Combined outperforms individual")
        else:
            log(f"  PREDICTION S2-4 NOT CONFIRMED")
            log(f"  Individual gene sufficient")

        return epi_score
    return None

# ============================================================
# TEST 5: CDKN1A CORRECTED ESCC DEPTH
# ============================================================

def cdkn1a_escc_depth(
    escc, depth_escc_s1
):
    log("")
    log("=" * 65)
    log("TEST 5: CDKN1A CORRECTED ESCC DEPTH")
    log("S1: CDKN1A r=-0.84** — strongest")
    log("Prediction S2-5: corrected panel")
    log("(CDKN1A/EGFR/MYC) > original")
    log("=" * 65)

    gc = list(escc.columns)

    if depth_escc_s1 is None:
        log("  No S1 depth provided")
        return None

    # Build corrected depth score
    sw2 = [
        g for g in ESCC_SWITCH_S2
        if g in gc
    ]
    fa2 = [
        g for g in ESCC_FA_S2
        if g in gc
    ]

    log(f"  S2 switch genes: {sw2}")
    log(f"  S2 FA genes    : {fa2}")

    depth_s2 = build_depth_score(
        escc, ESCC_SWITCH_S2,
        ESCC_FA_S2, "ESCC_S2",
    )

    # Compare S1 vs S2
    rv_compare, pv_compare = safe_pearsonr(
        depth_escc_s1.values,
        depth_s2.values,
    )
    log(f"\n  r(S1_depth, S2_depth) = "
        f"{rv_compare:+.4f}  "
        f"{fmt_p(pv_compare)}")

    if rv_compare > 0.9:
        log(f"  Same biology captured")
        log(f"  Corrected panel confirms S1")
    elif rv_compare > 0.5:
        log(f"  Partial overlap — S2 extends S1")
    else:
        log(f"  Different axis — S2 captures")
        log(f"  new biology not in S1")

    # Test CDKN1A specifically
    if "CDKN1A" in gc:
        rv_ck, pv_ck = safe_pearsonr(
            depth_s2.values,
            escc["CDKN1A"].values,
        )
        log(f"\n  r(CDKN1A, S2_depth) = "
            f"{rv_ck:+.4f}  {fmt_p(pv_ck)}")
        log(f"  S1 reference: r=-0.8391 **")

    # All cell cycle genes vs S2 depth
    log(f"\n  Cell cycle genes vs S2 depth:")
    cc_genes = [
        "CDKN1A", "CDKN2A", "CDKN1B",
        "RB1", "CDK4", "CDK6", "CCND1",
        "CCNE1", "CCNA2", "CDK2",
        "CCNB1", "CDC20", "PLK1",
    ]
    for gene in cc_genes:
        if gene not in gc:
            continue
        rv, pv = safe_pearsonr(
            depth_s2.values,
            escc[gene].values,
        )
        log(f"  {gene:<10} r={rv:>+8.4f}  "
            f"{fmt_p(pv)}")

    return depth_s2

# ============================================================
# TEST 6: ERBB2 SUBTYPE SPLIT IN EAC
# ============================================================

def erbb2_subtype_test(eac, depth_eac):
    log("")
    log("=" * 65)
    log("TEST 6: ERBB2 SUBTYPE IN EAC")
    log("Prediction S2-6: HER2-high EAC")
    log("has different depth than HER2-low")
    log("ERBB2 flat in bulk S1 (-32.7% ns)")
    log("=" * 65)

    gc = list(eac.columns)

    if "ERBB2" not in gc:
        log("  ERBB2 not in matrix")
        return

    erbb2_vals = eac["ERBB2"].values
    med        = np.median(erbb2_vals)
    q75        = np.percentile(erbb2_vals, 75)

    log(f"  ERBB2 in EAC:")
    log(f"    median = {med:.4f}")
    log(f"    Q75    = {q75:.4f}")
    log(f"    mean   = {erbb2_vals.mean():.4f}")
    log(f"    std    = {erbb2_vals.std():.4f}")

    hi_mask = erbb2_vals >= q75
    lo_mask = erbb2_vals < q75

    n_hi = hi_mask.sum()
    n_lo = lo_mask.sum()
    log(f"\n  HER2-high (top quartile): n={n_hi}")
    log(f"  HER2-low  (rest)         : n={n_lo}")

    if n_hi < 3 or n_lo < 3:
        log(f"  Insufficient samples per group")
        return

    d_hi = depth_eac.values[hi_mask]
    d_lo = depth_eac.values[lo_mask]

    log(f"\n  Depth by HER2 status:")
    log(f"  HER2-high: {d_hi.mean():.4f} "
        f"± {d_hi.std():.4f}")
    log(f"  HER2-low : {d_lo.mean():.4f} "
        f"± {d_lo.std():.4f}")

    _, pp = safe_mwu(
        d_hi, d_lo, "two-sided"
    )
    log(f"  p (two-sided) = {fmt_p(pp)}")

    if not np.isnan(pp) and pp < 0.05:
        log(f"\n  PREDICTION S2-6 CONFIRMED ✓")
        if d_hi.mean() > d_lo.mean():
            log(f"  HER2-high = deeper attractor")
            log(f"  Same as STAD geometry")
        else:
            log(f"  HER2-high = shallower")
            log(f"  HER2 not a depth driver in EAC")
    else:
        log(f"\n  PREDICTION S2-6 NOT CONFIRMED")
        log(f"  HER2 does not separate depth")

    # r(ERBB2, depth)
    rv, pv = safe_pearsonr(
        depth_eac.values, erbb2_vals
    )
    log(f"\n  r(ERBB2, depth) = {rv:+.4f}  "
        f"{fmt_p(pv)}")

# ============================================================
# TEST 7: SPRR1A IN DEEP EAC
# ============================================================

def sprr1a_eac_test(eac, depth_eac):
    log("")
    log("=" * 65)
    log("TEST 7: SPRR1A IN DEEP EAC")
    log("S1: SPRR1A r=+0.53* in EAC")
    log("Unexpected squamous marker")
    log("Prediction S2-7: co-elevated with")
    log("CDC20/MKI67 = poorly diff subtype")
    log("=" * 65)

    gc = list(eac.columns)

    markers = [
        ("SPRR1A", "squamous cornified"),
        ("CDC20",  "mitotic — co-elevated?"),
        ("MKI67",  "proliferation"),
        ("TOP2A",  "proliferation"),
        ("PCNA",   "proliferation"),
        ("KRT4",   "squamous keratin"),
        ("KRT13",  "squamous keratin"),
        ("DSG1",   "desmosomal squamous"),
        ("IVL",    "terminal squamous"),
        ("KRT5",   "basal squamous"),
        ("SOX2",   "squamous stem"),
        ("TP63",   "squamous TF"),
    ]

    log(f"\n  SPRR1A correlation with EAC depth:")
    rv_spr, pv_spr = safe_pearsonr(
        depth_eac.values,
        eac["SPRR1A"].values,
    ) if "SPRR1A" in gc else (np.nan, np.nan)
    log(f"  r(SPRR1A, depth) = "
        f"{rv_spr:+.4f}  {fmt_p(pv_spr)}")

    log(f"\n  Co-elevation test — squamous")
    log(f"  and proliferation markers:")
    log(f"  {'Gene':<10} {'r(depth)':>10}  "
        f"{'r(SPRR1A)':>10}  Role")
    log(f"  {'-'*55}")

    if "SPRR1A" not in gc:
        log("  SPRR1A not in matrix")
        return

    for gene, role in markers:
        if gene not in gc:
            continue
        rv_d, pv_d = safe_pearsonr(
            depth_eac.values,
            eac[gene].values,
        )
        rv_s, pv_s = safe_pearsonr(
            eac["SPRR1A"].values,
            eac[gene].values,
        )
        log(f"  {gene:<10} {rv_d:>+10.4f}  "
            f"{rv_s:>+10.4f}  {role}")

    # Identify the SPRR1A-high subgroup
    sprr1a_vals = eac["SPRR1A"].values
    q75_s = np.percentile(sprr1a_vals, 75)
    hi_s  = sprr1a_vals >= q75_s
    lo_s  = sprr1a_vals < q75_s

    log(f"\n  SPRR1A-high EAC (top quartile):")
    log(f"  n={hi_s.sum()}")

    for gene in ["CDC20", "MKI67", "TOP2A",
                 "KRT5", "TP63"]:
        if gene not in gc:
            continue
        hi_m = eac[gene].values[hi_s].mean()
        lo_m = eac[gene].values[lo_s].mean()
        _, pp = safe_mwu(
            eac[gene].values[hi_s],
            eac[gene].values[lo_s],
            "two-sided",
        )
        log(f"  {gene:<8} hi={hi_m:.4f} "
            f"lo={lo_m:.4f}  {fmt_p(pp)}")

    # Confirm or deny prediction
    if "CDC20" in gc and "MKI67" in gc:
        rv_cdc, _ = safe_pearsonr(
            eac["SPRR1A"].values,
            eac["CDC20"].values,
        )
        rv_mki, _ = safe_pearsonr(
            eac["SPRR1A"].values,
            eac["MKI67"].values,
        )
        log(f"\n  r(SPRR1A, CDC20) = "
            f"{rv_cdc:+.4f}")
        log(f"  r(SPRR1A, MKI67) = "
            f"{rv_mki:+.4f}")
        if rv_cdc > 0.30 and rv_mki > 0.30:
            log(f"  PREDICTION S2-7 CONFIRMED ✓")
            log(f"  SPRR1A co-elevated with")
            log(f"  proliferation markers")
            log(f"  = poorly differentiated")
            log(f"    squamous-like EAC subtype")
        else:
            log(f"  PREDICTION S2-7 NOT CONFIRMED")
            log(f"  SPRR1A not co-proliferative")

# ============================================================
# TEST 8: S1 vs S2 DEPTH COMPARISON
# ============================================================

def s1_vs_s2_comparison(
    depth_s1_dict, depth_s2_dict
):
    log("")
    log("=" * 65)
    log("TEST 8: S1 vs S2 DEPTH COMPARISON")
    log("r(S1, S2) tells if same biology")
    log("r>0.90: same | r<0.50: new signal")
    log("=" * 65)

    for label in ["ESCC", "EAC"]:
        d1 = depth_s1_dict.get(label)
        d2 = depth_s2_dict.get(label)
        if d1 is None or d2 is None:
            log(f"  {label}: missing depth")
            continue

        # Align indices
        common = d1.index.intersection(
            d2.index
        )
        if len(common) < 5:
            log(f"  {label}: insufficient overlap")
            continue

        rv, pv = safe_pearsonr(
            d1[common].values,
            d2[common].values,
        )
        log(f"\n  {label}:")
        log(f"  r(S1, S2) = {rv:+.4f}  "
            f"{fmt_p(pv)}")
        log(f"  S1 mean   = "
            f"{d1[common].mean():.4f}")
        log(f"  S2 mean   = "
            f"{d2[common].mean():.4f}")

        if not np.isnan(rv):
            if rv > 0.90:
                log(f"  Same biology — "
                    f"S2 confirms S1")
            elif rv > 0.50:
                log(f"  Partial — S2 extends S1")
            else:
                log(f"  Different axis — "
                    f"S2 new biology")

# ============================================================
# TEST 9: CORRECTED EAC DEPTH
# TFF1-anchored
# ============================================================

def eac_corrected_depth(eac, depth_eac_s1):
    log("")
    log("=" * 65)
    log("TEST 9: EAC CORRECTED DEPTH SCORE")
    log("TFF1-anchored instead of CDX2")
    log("=" * 65)

    gc = list(eac.columns)

    depth_s2 = build_depth_score(
        eac, EAC_SWITCH_S2,
        EAC_FA_S2, "EAC_S2",
    )

    if depth_eac_s1 is not None:
        common = depth_eac_s1.index.intersection(
            depth_s2.index
        )
        if len(common) >= 5:
            rv, pv = safe_pearsonr(
                depth_eac_s1[common].values,
                depth_s2[common].values,
            )
            log(f"\n  r(S1_EAC, S2_EAC) = "
                f"{rv:+.4f}  {fmt_p(pv)}")

    log(f"\n  EAC S2 depth correlations:")
    corrs = depth_correlations(
        eac, depth_s2, "EAC_S2"
    )

    return depth_s2, corrs

# ============================================================
# TEST 10: CLINICAL PANEL DERIVATION
# 3-gene IHC-deployable panels
# ============================================================

def derive_clinical_panels(
    escc, eac,
    depth_escc_s2, depth_eac_s2,
):
    log("")
    log("=" * 65)
    log("TEST 10: CLINICAL PANEL DERIVATION")
    log("3-gene IHC-deployable panels")
    log("Stated before literature check")
    log("=" * 65)

    for label, df, depth in [
        ("ESCC", escc, depth_escc_s2),
        ("EAC",  eac,  depth_eac_s2),
    ]:
        if df is None or depth is None:
            continue

        gc = list(df.columns)
        log(f"\n  {label} PANEL DERIVATION:")

        # Find top 2 positive + top 1 negative
        corrs = []
        for gene in gc:
            rv, pv = safe_pearsonr(
                depth.values, df[gene].values
            )
            if not np.isnan(rv):
                corrs.append((gene, rv, pv))

        corrs.sort(
            key=lambda x: abs(x[1]),
            reverse=True,
        )

        pos = [
            (g, r, p) for g, r, p in corrs
            if r > 0.30 and p < 0.10
        ]
        neg = [
            (g, r, p) for g, r, p in corrs
            if r < -0.30 and p < 0.10
        ]

        log(f"  Top positive (IHC elevated):")
        for g, r, p in pos[:5]:
            log(f"    {g:<10} r={r:>+8.4f}  "
                f"{fmt_p(p)}")

        log(f"  Top negative (IHC suppressed):")
        for g, r, p in neg[:5]:
            log(f"    {g:<10} r={r:>+8.4f}  "
                f"{fmt_p(p)}")

        # Propose 3-gene panel
        if len(pos) >= 1 and len(neg) >= 1:
            p1 = pos[0][0]
            p2 = pos[1][0] if len(pos) > 1 else ""
            n1 = neg[0][0]

            log(f"\n  PROPOSED 3-GENE PANEL ({label}):")
            log(f"    {p1}(+) + "
                f"{'  '+p2 if p2 else ''}(+) / "
                f"{n1}(-)")

            # Test panel correlation with depth
            if p2 and p2 in gc and n1 in gc:
                panel_score = norm01(
                    0.5 * norm01(df[p1].values)
                    + 0.5 * norm01(df[p2].values)
                    - norm01(df[n1].values)
                )
                rv_panel, pv_panel = (
                    safe_pearsonr(
                        depth.values,
                        panel_score.values,
                    )
                )
                log(f"    Panel r with depth = "
                    f"{rv_panel:+.4f}  "
                    f"{fmt_p(pv_panel)}")

# ============================================================
# FIGURE
# ============================================================

def generate_figure(
    groups,
    shared_axis,
    depth_s1_dict,
    depth_s2_dict,
    corrs_s2_dict,
    wnt_test_results=None,
):
    log("")
    log("--- Generating Script 2 figure ---")

    fig = plt.figure(figsize=(28, 22))
    fig.suptitle(
        "Esophageal Cancer — False Attractor "
        "Analysis\n"
        "Script 2 | GSE26886 | Corrected "
        "Framework\n"
        "OrganismCore | 2026-03-01 | "
        "Doc 90b",
        fontsize=10,
        fontweight="bold",
        y=0.99,
    )

    gs = gridspec.GridSpec(
        3, 3,
        figure=fig,
        hspace=0.55,
        wspace=0.45,
    )

    COLORS = {
        "Normal":  "#27ae60",
        "Barrett": "#f39c12",
        "EAC":     "#2980b9",
        "ESCC":    "#e74c3c",
    }

    def gc_col(g):
        return COLORS.get(g, "#95a5a6")

    group_order = [
        "Normal", "Barrett", "EAC", "ESCC"
    ]

    # A — Shared ZEB1/TFF1 axis
    ax_a = fig.add_subplot(gs[0, 0])
    if shared_axis is not None:
        for g in group_order:
            if g not in groups:
                continue
            idx  = groups[g].index
            vals = shared_axis[
                shared_axis.index.isin(idx)
            ].values
            ax_a.scatter(
                [group_order.index(g)] * len(vals),
                vals,
                alpha=0.5, s=25,
                color=gc_col(g),
            )
            ax_a.scatter(
                [group_order.index(g)],
                [vals.mean()],
                s=120, color=gc_col(g),
                zorder=5, marker="D",
                label=f"{g} μ={vals.mean():.3f}",
            )
        ax_a.set_xticks(
            range(len(group_order))
        )
        ax_a.set_xticklabels(
            group_order, fontsize=8
        )
        ax_a.legend(fontsize=6)
    ax_a.set_ylabel(
        "Squamous→Columnar axis", fontsize=8
    )
    ax_a.set_title(
        "A — Shared ZEB1/TFF1 Axis\n"
        "All 4 groups on single continuum",
        fontsize=9,
    )

    # B — S1 vs S2 depth scatter
    ax_b = fig.add_subplot(gs[0, 1])
    for label, color in [
        ("ESCC", COLORS["ESCC"]),
        ("EAC",  COLORS["EAC"]),
    ]:
        d1 = depth_s1_dict.get(label)
        d2 = depth_s2_dict.get(label)
        if d1 is None or d2 is None:
            continue
        common = d1.index.intersection(
            d2.index
        )
        if len(common) < 3:
            continue
        rv, _ = safe_pearsonr(
            d1[common].values,
            d2[common].values,
        )
        ax_b.scatter(
            d1[common].values,
            d2[common].values,
            alpha=0.5, s=25,
            color=color,
            label=f"{label} r={rv:+.3f}",
        )
    ax_b.set_xlabel("S1 depth", fontsize=8)
    ax_b.set_ylabel("S2 depth", fontsize=8)
    ax_b.set_title(
        "B — S1 vs S2 Depth\n"
        "Same biology or new signal?",
        fontsize=9,
    )
    ax_b.legend(fontsize=7)
    ax_b.plot(
        [0, 1], [0, 1], "k--",
        alpha=0.3, linewidth=1,
    )

    # C — EAC corrected depth correlations
    ax_c = fig.add_subplot(gs[0, 2])
    if "EAC" in corrs_s2_dict:
        corrs = corrs_s2_dict["EAC"]
        top  = [
            (g, r) for g, r, p in corrs
            if r > 0
        ][:8]
        bot  = [
            (g, r) for g, r, p in corrs
            if r < 0
        ][:8]
        both = sorted(
            top + bot, key=lambda x: x[1]
        )
        if both:
            genes_ = [x[0] for x in both]
            vals_  = [x[1] for x in both]
            cols_  = [
                COLORS["EAC"] if v < 0
                else "#f39c12"
                for v in vals_
            ]
            ax_c.barh(genes_, vals_,
                      color=cols_)
            ax_c.axvline(
                0, color="black",
                linewidth=0.8,
            )
            ax_c.tick_params(
                axis="y", labelsize=7
            )
    ax_c.set_xlabel("r with depth", fontsize=8)
    ax_c.set_title(
        "C — EAC S2 Depth Correlations\n"
        "TFF1-anchored panel",
        fontsize=9,
    )

    # D — ESCC corrected depth correlations
    ax_d = fig.add_subplot(gs[1, 0])
    if "ESCC" in corrs_s2_dict:
        corrs = corrs_s2_dict["ESCC"]
        top  = [
            (g, r) for g, r, p in corrs
            if r > 0
        ][:8]
        bot  = [
            (g, r) for g, r, p in corrs
            if r < 0
        ][:8]
        both = sorted(
            top + bot, key=lambda x: x[1]
        )
        if both:
            genes_ = [x[0] for x in both]
            vals_  = [x[1] for x in both]
            cols_  = [
                COLORS["ESCC"] if v < 0
                else "#f39c12"
                for v in vals_
            ]
            ax_d.barh(genes_, vals_,
                      color=cols_)
            ax_d.axvline(
                0, color="black",
                linewidth=0.8,
            )
            ax_d.tick_params(
                axis="y", labelsize=7
            )
    ax_d.set_xlabel("r with depth", fontsize=8)
    ax_d.set_title(
        "D — ESCC S2 Depth Correlations\n"
        "CDKN1A-anchored panel",
        fontsize=9,
    )

    # E — Epigenetic score EAC
    ax_e = fig.add_subplot(gs[1, 1])
    epi_genes = [
        "EZH2", "HDAC1", "HDAC2",
        "KDM6A", "TET2",
    ]
    epi_avail = [
        g for g in epi_genes
        if any(
            g in grp.columns
            for grp in groups.values()
        )
    ]
    if epi_avail:
        x = np.arange(len(epi_avail))
        w = 0.2
        for i, grp_name in enumerate(
            ["Normal", "Barrett",
             "EAC", "ESCC"]
        ):
            if grp_name not in groups:
                continue
            df = groups[grp_name]
            means = [
                df[g].mean()
                if g in df.columns else 0
                for g in epi_avail
            ]
            ax_e.bar(
                x + (i - 1.5) * w,
                means, w,
                color=gc_col(grp_name),
                label=grp_name,
                alpha=0.85,
            )
        ax_e.set_xticks(x)
        ax_e.set_xticklabels(
            epi_avail, rotation=45,
            ha="right", fontsize=8,
        )
        ax_e.legend(fontsize=6)
    ax_e.set_title(
        "E — Epigenetic Genes\n"
        "EZH2+HDAC1 in EAC",
        fontsize=9,
    )

    # F — TFF1 and ZEB1 by group
    ax_f = fig.add_subplot(gs[1, 2])
    key_genes = [
        "TFF1", "ZEB1", "CDX2",
        "IVL", "EGFR", "CDH1",
    ]
    avail = [
        g for g in key_genes
        if any(
            g in grp.columns
            for grp in groups.values()
        )
    ]
    if avail:
        x = np.arange(len(avail))
        w = 0.2
        for i, grp_name in enumerate(
            ["Normal", "Barrett",
             "EAC", "ESCC"]
        ):
            if grp_name not in groups:
                continue
            df = groups[grp_name]
            means = [
                df[g].mean()
                if g in df.columns else 0
                for g in avail
            ]
            ax_f.bar(
                x + (i - 1.5) * w,
                means, w,
                color=gc_col(grp_name),
                label=grp_name,
                alpha=0.85,
            )
        ax_f.set_xticks(x)
        ax_f.set_xticklabels(
            avail, rotation=45,
            ha="right", fontsize=7,
        )
        ax_f.legend(fontsize=6)
    ax_f.set_title(
        "F — Key Corrected Markers\n"
        "TFF1/ZEB1/CDX2/IVL/EGFR/CDH1",
        fontsize=9,
    )

    # G — Depth distributions S2
    ax_g = fig.add_subplot(gs[2, 0])
    d_vals = []
    d_lbls = []
    for g in group_order:
        if g in depth_s2_dict and (
            depth_s2_dict[g] is not None
        ):
            d_vals.append(
                depth_s2_dict[g].values
            )
            d_lbls.append(g)
    if d_vals:
        parts = ax_g.violinplot(
            d_vals,
            positions=range(len(d_vals)),
            showmedians=True,
        )
        for i, pc in enumerate(
            parts["bodies"]
        ):
            pc.set_facecolor(
                gc_col(d_lbls[i])
            )
            pc.set_alpha(0.7)
        ax_g.set_xticks(range(len(d_lbls)))
        ax_g.set_xticklabels(
            d_lbls, fontsize=8
        )
    ax_g.set_ylabel(
        "S2 depth score", fontsize=8
    )
    ax_g.set_title(
        "G — S2 Depth by Group",
        fontsize=9,
    )

    # H — SPRR1A co-elevation in EAC
    ax_h = fig.add_subplot(gs[2, 1])
    if "EAC" in groups:
        eac = groups["EAC"]
        if (
            "SPRR1A" in eac.columns
            and "CDC20" in eac.columns
        ):
            rv, _ = safe_pearsonr(
                eac["SPRR1A"].values,
                eac["CDC20"].values,
            )
            ax_h.scatter(
                eac["SPRR1A"].values,
                eac["CDC20"].values,
                alpha=0.6, s=40,
                color=COLORS["EAC"],
            )
            ax_h.set_xlabel(
                "SPRR1A", fontsize=8
            )
            ax_h.set_ylabel(
                "CDC20", fontsize=8
            )
            ax_h.set_title(
                f"H — SPRR1A vs CDC20 (EAC)\n"
                f"r={rv:+.4f} "
                f"(squamous-prolif link?)",
                fontsize=8,
            )

    # I — Summary
    ax_i = fig.add_subplot(gs[2, 2])
    ax_i.axis("off")

    confirmed = 0
    not_conf  = 0
    partial   = 0

    summary = (
        "I — SCRIPT 2 SUMMARY\n"
        "─────────────────────────────\n"
        "Dataset : GSE26886 (reused)\n"
        "Script  : esca_false_attractor_2.py\n"
        "Doc     : 90b | 2026-03-01\n\n"
        "CORRECTED PANELS:\n"
        "  ESCC switch: IVL/CDKN1A\n"
        "  ESCC FA    : EGFR/FGFR1/MYC\n"
        "               NOTCH1/KRT10\n"
        "  EAC  switch: CDH1/ZEB1/APC\n"
        "  EAC  FA    : CDX2/TFF1/KRT20\n"
        "               VEGFA/HDAC1/EZH2\n\n"
        "S2 PREDICTIONS:\n"
        "  S2-1: ZEB1/TFF1 shared axis\n"
        "  S2-2: TFF1 > CDX2 anchor\n"
        "  S2-3: APC = CIN not Wnt\n"
        "  S2-4: HDAC1+EZH2 combined\n"
        "  S2-5: CDKN1A ESCC depth\n"
        "  S2-6: HER2 subtype in EAC\n"
        "  S2-7: SPRR1A poorly diff EAC\n\n"
        "Framework: OrganismCore\n"
        "Doc: 90b | 2026-03-01"
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
        RESULTS_DIR,
        "esca_gse26886_s2.png",
    )
    plt.savefig(
        out, dpi=150,
        bbox_inches="tight",
    )
    log(f"\n  Figure saved: {out}")
    plt.close()

# ============================================================
# MAIN
# ============================================================

def main():
    log("=" * 65)
    log("ESOPHAGEAL CANCER")
    log("FALSE ATTRACTOR ANALYSIS — SCRIPT 2")
    log("Dataset: GSE26886 (reused from S1)")
    log("Framework: OrganismCore")
    log("Doc: 90b | Date: 2026-03-01")
    log("=" * 65)
    log("")
    log("SCRIPT 1 FINDINGS (90a):")
    log("  ESCC: IVL confirmed DOWN ***")
    log("        EGFR/FGFR1/MYC confirmed UP")
    log("        NOTCH1/KRT10/DSG1 inverted FA")
    log("        CDKN1A r=-0.84** depth driver")
    log("  EAC:  CDH1 confirmed DOWN ***")
    log("        CDX2/KRT20/VEGFA confirmed UP")
    log("        TFF1 +2127% — strongest signal")
    log("        ZEB1 inverted — squamous lost")
    log("        HDAC1 r=+0.56** EZH2 r=+0.49*")
    log("        APC r=-0.63** CTNNB1 r=-0.56**")
    log("  Cross: CDX2 circuit 1/5 broken ✓")
    log("         AURKA absent from GPL570")
    log("")
    log("SCRIPT 2 PREDICTIONS LOCKED:")
    log("  S2-1: ZEB1/TFF1 shared axis")
    log("  S2-2: TFF1 > CDX2 as EAC anchor")
    log("  S2-3: APC = CIN not Wnt")
    log("        AXIN2 flat/down in deep EAC")
    log("  S2-4: HDAC1+EZH2 combined > alone")
    log("  S2-5: CDKN1A corrected ESCC depth")
    log("  S2-6: HER2-high EAC ≠ HER2-low depth")
    log("  S2-7: SPRR1A co-elevated CDC20/MKI67")

    # Download (reuse)
    ok = download_file(
        MATRIX_URL, MATRIX_FILE
    )
    if not ok:
        log("  FATAL: Download failed")
        write_log()
        return

    # Parse
    result = parse_series_matrix(MATRIX_FILE)
    if result[0] is None:
        log("  FATAL: Parse failed")
        write_log()
        return

    df_genes, meta = result

    # Classify
    group_series = classify_samples(
        df_genes, meta
    )

    groups = {}
    for g in [
        "Normal", "Barrett", "EAC", "ESCC"
    ]:
        mask = group_series == g
        if mask.sum() > 0:
            groups[g] = df_genes[mask]

    log("")
    log("=" * 65)
    log("GROUP SUMMARY")
    log("=" * 65)
    for g, df in groups.items():
        log(f"  {g:<12}: {len(df)} samples")

    normal   = groups.get("Normal",
                          pd.DataFrame())
    escc     = groups.get("ESCC",
                          pd.DataFrame())
    eac      = groups.get("EAC",
                          pd.DataFrame())
    barretts = groups.get("Barrett",
                          pd.DataFrame())

    # Build S1 depth scores
    # (replicate S1 panels for comparison)
    log("")
    log("=" * 65)
    log("S1 DEPTH SCORES (replicated)")
    log("For S1 vs S2 comparison")
    log("=" * 65)

    ESCC_SWITCH_S1 = [
        "NOTCH1", "KRT1", "KRT10",
        "SPRR1A", "IVL",
    ]
    ESCC_FA_S1 = [
        "SOX2", "TP63", "KRT5",
        "EGFR", "CCND1",
    ]
    EAC_SWITCH_S1 = [
        "NOTCH1", "CDH1", "MUC6",
        "MUC5AC", "TFF1", "GKN1",
    ]
    EAC_FA_S1 = [
        "CDX2", "ERBB2", "ZEB1",
        "MUC2", "KRT20", "TFF3", "VEGFA",
    ]

    depth_s1_dict = {}
    if len(escc) >= 5:
        depth_s1_dict["ESCC"] = (
            build_depth_score(
                escc,
                ESCC_SWITCH_S1,
                ESCC_FA_S1,
                "ESCC_S1",
            )
        )
    if len(eac) >= 5:
        depth_s1_dict["EAC"] = (
            build_depth_score(
                eac,
                EAC_SWITCH_S1,
                EAC_FA_S1,
                "EAC_S1",
            )
        )

    # Run all tests
    log("")
    log("=" * 65)
    log("SCRIPT 2 TESTS")
    log("=" * 65)

    # Test 1
    shared_axis = shared_axis_test(groups)

    # Test 2
    log("")
    log("=" * 65)
    log("TEST 2: TFF1 vs CDX2 AS EAC ANCHOR")
    log("=" * 65)
    tff1_results = tff1_vs_cdx2_test(
        eac if len(eac) >= 5 else pd.DataFrame(),
        depth_s1_dict.get("EAC"),
    )

    # Test 3
    eac_d_s1 = depth_s1_dict.get("EAC")
    if eac_d_s1 is None and len(eac) >= 5:
        eac_d_s1 = build_depth_score(
            eac, EAC_SWITCH_S2,
            EAC_FA_S2, "EAC_tmp",
        )
    if len(eac) >= 5:
        apc_wnt_resolution(eac, eac_d_s1)

    # Test 4
    if len(eac) >= 5:
        epi_score = epigenetic_combined_test(
            eac, eac_d_s1
        )

    # Test 5
    depth_s2_dict = {}
    escc_s2_depth = None
    if len(escc) >= 5:
        escc_s2_depth = cdkn1a_escc_depth(
            escc,
            depth_s1_dict.get("ESCC"),
        )
        if escc_s2_depth is not None:
            depth_s2_dict["ESCC"] = (
                escc_s2_depth
            )

    # Test 6
    if len(eac) >= 5 and eac_d_s1 is not None:
        erbb2_subtype_test(eac, eac_d_s1)

    # Test 7
    if len(eac) >= 5 and eac_d_s1 is not None:
        sprr1a_eac_test(eac, eac_d_s1)

    # Test 9 — EAC corrected depth
    eac_s2_depth = eac_s2_corrs = None
    if len(eac) >= 5:
        log("")
        log("=" * 65)
        log("EAC CORRECTED DEPTH (S2)")
        log("=" * 65)
        eac_s2_depth, eac_s2_corrs = (
            eac_corrected_depth(
                eac,
                depth_s1_dict.get("EAC"),
            )
        )
        depth_s2_dict["EAC"] = eac_s2_depth

    # Barrett and Normal S2 depths
    if len(barretts) >= 3:
        depth_s2_dict["Barrett"] = (
            build_depth_score(
                barretts,
                EAC_SWITCH_S2,
                EAC_FA_S2,
                "Barrett_S2",
            )
        )
    if len(normal) >= 3:
        depth_s2_dict["Normal"] = (
            build_depth_score(
                normal,
                EAC_SWITCH_S2,
                EAC_FA_S2,
                "Normal_S2",
            )
        )

    # Test 8 — S1 vs S2
    s1_vs_s2_comparison(
        depth_s1_dict, depth_s2_dict
    )

    # Test 10 — clinical panels
    derive_clinical_panels(
        escc if len(escc) >= 5 else None,
        eac  if len(eac)  >= 5 else None,
        depth_s2_dict.get("ESCC"),
        depth_s2_dict.get("EAC"),
    )

    # Depth correlations for S2
    corrs_s2_dict = {}
    if (
        len(escc) >= 5
        and "ESCC" in depth_s2_dict
    ):
        log("")
        log("=" * 65)
        log("ESCC S2 DEPTH CORRELATIONS")
        log("=" * 65)
        corrs_s2_dict["ESCC"] = (
            depth_correlations(
                escc,
                depth_s2_dict["ESCC"],
                "ESCC_S2",
            )
        )

    if eac_s2_corrs:
        corrs_s2_dict["EAC"] = eac_s2_corrs

    # Figure
    generate_figure(
        groups,
        shared_axis,
        depth_s1_dict,
        depth_s2_dict,
        corrs_s2_dict,
    )

    # Save depth scores
    for label, d in depth_s2_dict.items():
        if d is not None:
            d.to_csv(
                os.path.join(
                    RESULTS_DIR,
                    f"depth_s2_{label.lower()}.csv",
                ),
                header=["depth_s2"],
            )

    write_log()
    log(f"\n  Log    : {LOG_FILE}")
    log(f"  Output : {RESULTS_DIR}")
    log("\n=== SCRIPT 2 COMPLETE ===")
    log("\nPaste full output for Document 90b.")


if __name__ == "__main__":
    main()
