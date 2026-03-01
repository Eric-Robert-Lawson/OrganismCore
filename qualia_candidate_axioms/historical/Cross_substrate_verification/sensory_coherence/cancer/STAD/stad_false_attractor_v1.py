"""
Stomach Adenocarcinoma — False Attractor Analysis
SCRIPT 1 — DISCOVERY RUN
Dataset: GSE66229
  Gastric adenocarcinoma
  Affymetrix GPL570 (HG-U133 Plus 2.0)
  Korean cohort
  Tumor + normal pairs
  Survival data available

FRAMEWORK: OrganismCore Principles-First
Doc: pre-STAD | Date: 2026-03-01

PREDICTIONS LOCKED BEFORE DATA:
  Switch genes (predicted suppressed):
    CLDN18  — most stomach-specific gene
    MUC5AC  — gastric surface mucin
    TFF1    — foveolar pit cell marker
    GKN1    — gastrokine 1
    CDH1    — E-cadherin

  False attractor (predicted elevated):
    CDX2    — intestinal master TF
    MUC2    — intestinal goblet mucin
    KRT20   — intestinal keratin
    VIM     — EMT vimentin
    CDH2    — N-cadherin

  Epigenetic lock:
    EZH2    — 5th solid cancer prediction
              r(EZH2, depth) > 0

  Scaffold:
    MYC     — elevated
    ERBB2   — HER2 (must find from geometry)
    FGFR2   — elevated subset

  Identity switch prediction:
    MUC5AC (gastric) down
    MUC2   (intestinal) up
    CLDN18 down / CDX2 up

Author: Eric Robert Lawson
Framework: OrganismCore Principles-First
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

BASE_DIR    = "./stad_false_attractor/"
RESULTS_DIR = os.path.join(BASE_DIR, "results")
LOG_FILE    = os.path.join(
    RESULTS_DIR, "s1_log.txt"
)

os.makedirs(BASE_DIR,    exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

LOCAL_MATRIX = os.path.join(
    BASE_DIR,
    "GSE66229_series_matrix.txt.gz"
)

MATRIX_CANDIDATES = [
    (
        "https://ftp.ncbi.nlm.nih.gov/geo/"
        "series/GSE66nnn/GSE66229/matrix/"
        "GSE66229_series_matrix.txt.gz"
    ),
    (
        "https://ftp.ncbi.nlm.nih.gov/geo/"
        "series/GSE66nnn/GSE66229/matrix/"
        "GSE66229-GPL570_series_matrix.txt.gz"
    ),
    (
        "https://ftp.ncbi.nlm.nih.gov/geo/"
        "series/GSE66nnn/GSE66229/matrix/"
        "GSE66229-GPL6947_series_matrix.txt.gz"
    ),
]

ANNOT_LOCAL = os.path.join(
    BASE_DIR, "GPL570.annot.gz"
)
ANNOT_URLS = [
    (
        "https://ftp.ncbi.nlm.nih.gov/geo/"
        "platforms/GPL570nnn/GPL570/annot/"
        "GPL570.annot.gz"
    ),
    (
        "https://ftp.ncbi.nlm.nih.gov/geo/"
        "platforms/GPL570nnn/GPL570/soft/"
        "GPL570.soft.gz"
    ),
]

# ============================================================
# GENE PANELS — LOCKED BEFORE DATA
# ============================================================

SWITCH_GENES = [
    "CLDN18", "MUC5AC", "TFF1",
    "GKN1",   "GKN2",   "CDH1",
    "OLFM4",  "ATP4A",  "PGC",
    "TFF2",   "MUC6",
]
FA_MARKERS = [
    "CDX2",  "MUC2",   "KRT20",
    "VIM",   "CDH2",   "TWIST1",
    "ZEB1",  "SNAI1",  "SNAI2",
    "FN1",
]
EPIGENETIC = [
    "EZH2",  "EED",    "SUZ12",
    "BMI1",  "KDM6A",  "DNMT3A",
    "DNMT3B","HDAC1",  "HDAC2",
]
SCAFFOLD = [
    "MYC",   "ERBB2",  "EGFR",
    "FGFR2", "MET",    "CCND1",
    "CDK4",  "CDK6",   "RB1",
    "PTEN",  "TP53",   "KRAS",
]
LUMINAL_GASTRIC = [
    "CLDN18","MUC5AC", "TFF1",
    "GKN1",  "GKN2",   "ATP4A",
    "PGC",   "OLFM4",  "TFF2",
    "MUC6",
]
INTESTINAL = [
    "CDX2",  "MUC2",   "KRT20",
    "VIL1",  "SI",     "LCT",
    "FABP1", "FABP2",
]
EMT = [
    "VIM",   "CDH2",   "CDH1",
    "SNAI1", "SNAI2",  "TWIST1",
    "ZEB1",  "ZEB2",   "FN1",
    "MMP2",  "MMP9",
]
PROLIFERATION = [
    "MKI67", "PCNA",   "TOP2A",
    "AURKA", "PLK1",   "CCNB1",
    "CDC20", "BUB1B",
]
HER2_PATHWAY = [
    "ERBB2", "ERBB3",  "GRB7",
    "EGFR",  "ERBB4",
]
IMMUNE_MARKERS = [
    "CD274", "PDCD1",  "CD8A",
    "CD4",   "FOXP3",  "CD68",
    "CD163",
]
NEUROENDOCRINE = [
    "CHGA",  "SYP",    "ENO2",
    "NCAM1",
]

ALL_TARGET = list(dict.fromkeys(
    SWITCH_GENES    + FA_MARKERS     +
    EPIGENETIC      + SCAFFOLD       +
    LUMINAL_GASTRIC + INTESTINAL     +
    EMT             + PROLIFERATION  +
    HER2_PATHWAY    + IMMUNE_MARKERS +
    NEUROENDOCRINE
))

ROLE_MAP = {}
for g in SWITCH_GENES:     ROLE_MAP[g] = "SWITCH"
for g in FA_MARKERS:       ROLE_MAP[g] = "FA"
for g in EPIGENETIC:       ROLE_MAP[g] = "EPIGEN"
for g in SCAFFOLD:         ROLE_MAP[g] = "SCAFFOLD"
for g in LUMINAL_GASTRIC:  ROLE_MAP[g] = "GASTRIC"
for g in INTESTINAL:       ROLE_MAP[g] = "INTESTINAL"
for g in EMT:              ROLE_MAP[g] = "EMT"
for g in PROLIFERATION:    ROLE_MAP[g] = "PROLIF"
for g in HER2_PATHWAY:     ROLE_MAP[g] = "HER2"
for g in IMMUNE_MARKERS:   ROLE_MAP[g] = "IMMUNE"
for g in NEUROENDOCRINE:   ROLE_MAP[g] = "NE"

# Hard-coded GPL570 probe→gene map
TARGET_PROBES = {
    "204013_at":    "CLDN18",
    "207982_at":    "MUC5AC",
    "211332_x_at":  "MUC5AC",
    "204766_s_at":  "TFF1",
    "207017_at":    "TFF1",
    "219534_at":    "GKN1",
    "221895_at":    "GKN2",
    "201131_s_at":  "CDH1",
    "208069_s_at":  "CDH1",
    "219254_at":    "OLFM4",
    "204679_at":    "ATP4A",
    "209780_at":    "PGC",
    "204764_at":    "TFF2",
    "210735_s_at":  "MUC6",
    "209588_at":    "CDX2",
    "207257_at":    "MUC2",
    "208826_at":    "KRT20",
    "201426_s_at":  "VIM",
    "201425_at":    "VIM",
    "203440_at":    "CDH2",
    "213844_at":    "TWIST1",
    "218816_at":    "ZEB1",
    "201474_s_at":  "FN1",
    "216641_s_at":  "SNAI1",
    "213566_at":    "SNAI2",
    "203821_at":    "VIL1",
    "209496_at":    "FABP1",
    "203358_s_at":  "EZH2",
    "218471_s_at":  "EZH2",
    "209915_at":    "EED",
    "218171_s_at":  "SUZ12",
    "201904_s_at":  "BMI1",
    "221604_s_at":  "KDM6A",
    "204472_at":    "DNMT3A",
    "218457_at":    "DNMT3B",
    "201418_s_at":  "HDAC1",
    "201419_s_at":  "HDAC2",
    "202431_s_at":  "MYC",
    "216836_s_at":  "ERBB2",
    "210930_s_at":  "ERBB2",
    "201983_s_at":  "EGFR",
    "203638_s_at":  "FGFR2",
    "203510_at":    "MET",
    "208712_at":    "CCND1",
    "202613_at":    "CDK4",
    "203554_x_at":  "CDK6",
    "202910_s_at":  "RB1",
    "217023_at":    "PTEN",
    "201746_at":    "TP53",
    "204340_at":    "KRAS",
    "205358_at":    "ERBB3",
    "216033_s_at":  "GRB7",
    "205923_at":    "ERBB4",
    "203667_at":    "MMP2",
    "203936_s_at":  "MMP9",
    "208079_s_at":  "ZEB2",
    "212020_s_at":  "MKI67",
    "201202_at":    "PCNA",
    "201291_s_at":  "TOP2A",
    "204092_s_at":  "AURKA",
    "202240_at":    "PLK1",
    "214710_s_at":  "CCNB1",
    "203213_at":    "CDC20",
    "201086_x_at":  "BUB1B",
    "220644_at":    "CD274",
    "207634_at":    "PDCD1",
    "205758_at":    "CD8A",
    "206545_s_at":  "CD4",
    "210943_s_at":  "FOXP3",
    "203507_at":    "CD68",
    "203508_at":    "CD163",
    "204250_s_at":  "CHGA",
    "213421_at":    "SYP",
    "201313_at":    "ENO2",
    "203868_s_at":  "NCAM1",
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

def fetch_url(url, timeout=60):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(
        req, timeout=timeout
    ) as r:
        return r.read()

def fmt_p(p):
    if p < 0.001:  return f"p={p:.2e} ***"
    elif p < 0.01: return f"p={p:.2e}  **"
    elif p < 0.05: return f"p={p:.4f}   *"
    else:          return f"p={p:.4f}  ns"

def safe_pearsonr(x, y):
    """Pearsonr with length guard."""
    xa = np.asarray(x, dtype=float)
    ya = np.asarray(y, dtype=float)
    mask = np.isfinite(xa) & np.isfinite(ya)
    xa, ya = xa[mask], ya[mask]
    if len(xa) < 3:
        return np.nan, np.nan
    return stats.pearsonr(xa, ya)

def safe_mwu(a, b, alternative="two-sided"):
    """Mann-Whitney U with length guard."""
    if len(a) < 2 or len(b) < 2:
        return np.nan, np.nan
    return stats.mannwhitneyu(
        a, b, alternative=alternative
    )

# ============================================================
# STEP 0: DOWNLOAD MATRIX
# ============================================================

def download_all():
    log("=" * 65)
    log("STEP 0: DATA ACQUISITION")
    log("Dataset: GSE66229")
    log("  Gastric adenocarcinoma")
    log("  Affymetrix GPL570")
    log("  Korean cohort")
    log("=" * 65)

    if os.path.exists(LOCAL_MATRIX):
        sz = os.path.getsize(LOCAL_MATRIX) / 1e6
        if sz > 0.5:
            log(f"  Found: "
                f"{os.path.basename(LOCAL_MATRIX)}"
                f" ({sz:.1f} MB) — reusing")
            return LOCAL_MATRIX

    def hook(c, b, t):
        if t > 0:
            pct = min(c * b / t * 100, 100)
            mb  = c * b / 1e6
            sys.stdout.write(
                f"\r  {mb:.1f} MB ({pct:.1f}%)"
            )
            sys.stdout.flush()

    for url in MATRIX_CANDIDATES:
        log(f"  Trying: {url}")
        try:
            urllib.request.urlretrieve(
                url, LOCAL_MATRIX, hook
            )
            print()
            sz = os.path.getsize(
                LOCAL_MATRIX
            ) / 1e6
            if sz > 0.5:
                log(f"  Downloaded: {sz:.1f} MB")
                return LOCAL_MATRIX
            else:
                log(f"  Too small ({sz:.1f} MB)")
                os.remove(LOCAL_MATRIX)
        except Exception as e:
            log(f"  Failed: {e}")
            if os.path.exists(LOCAL_MATRIX):
                os.remove(LOCAL_MATRIX)

    # FTP directory listing fallback
    log("\n  Fetching FTP directory listing...")
    try:
        import re
        dir_url = (
            "https://ftp.ncbi.nlm.nih.gov"
            "/geo/series/GSE66nnn/"
            "GSE66229/matrix/"
        )
        raw  = fetch_url(dir_url, timeout=30)
        text = raw.decode("utf-8", errors="ignore")
        found_urls = []
        for line in text.split("\n"):
            if ".txt.gz" in line:
                log(f"    {line.strip()}")
                m = re.search(
                    r'href="([^"]*\.txt\.gz)"',
                    line
                )
                if m:
                    fname = m.group(1)
                    furl  = (
                        "https://ftp.ncbi.nlm."
                        "nih.gov/geo/series/"
                        "GSE66nnn/GSE66229/"
                        f"matrix/{fname}"
                    )
                    found_urls.append(
                        (fname, furl)
                    )
        found_urls.sort(
            key=lambda x: (
                0 if "GPL570" in x[0] else 1
            )
        )
        for fname, furl in found_urls:
            log(f"  Trying: {fname}")
            try:
                urllib.request.urlretrieve(
                    furl, LOCAL_MATRIX, hook
                )
                print()
                sz = os.path.getsize(
                    LOCAL_MATRIX
                ) / 1e6
                if sz > 0.5:
                    log(f"  OK: {sz:.1f} MB")
                    return LOCAL_MATRIX
                os.remove(LOCAL_MATRIX)
            except Exception as e:
                log(f"  Failed: {e}")
                if os.path.exists(LOCAL_MATRIX):
                    os.remove(LOCAL_MATRIX)
    except Exception as e:
        log(f"  Directory listing failed: {e}")

    log("\n  ALL DOWNLOADS FAILED.")
    log("  Manual steps:")
    log("  1. https://www.ncbi.nlm.nih.gov"
        "/geo/query/acc.cgi?acc=GSE66229")
    log("  2. Download Series Matrix File(s)")
    log("  3. Save GPL570 matrix as:")
    log(f"     {LOCAL_MATRIX}")
    log("  4. Re-run")
    sys.exit(1)

# ============================================================
# STEP 1: PARSE SERIES MATRIX
# ============================================================

def parse_series_matrix(path):
    log(f"\n  Parsing: {os.path.basename(path)}")

    meta_rows  = {}
    data_lines = []
    in_table   = False
    header     = None

    with gzip.open(
        path, "rt",
        encoding="utf-8",
        errors="ignore",
    ) as f:
        for line in f:
            line = line.rstrip("\n")

            if "series_matrix_table_begin" in line:
                in_table = True
                continue
            if "series_matrix_table_end" in line:
                in_table = False
                continue

            if in_table:
                if header is None:
                    header = line.split("\t")
                else:
                    data_lines.append(line)
                continue

            if line.startswith("!Sample_"):
                parts = line.split("\t")
                key   = parts[0].strip()
                vals  = [
                    v.strip().strip('"')
                    for v in parts[1:]
                ]
                if key not in meta_rows:
                    meta_rows[key] = vals
                else:
                    meta_rows[key].extend(vals)

    log(f"  Data lines: {len(data_lines)}")
    if not data_lines or header is None:
        log("  ERROR: No expression table found")
        sys.exit(1)

    sample_ids = [
        h.strip().strip('"')
        for h in header[1:]
    ]
    log(f"  Samples: {len(sample_ids)}")

    probe_ids = []
    expr_vals = []
    for line in data_lines:
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        probe_ids.append(
            parts[0].strip().strip('"')
        )
        expr_vals.append([
            float(v)
            if v not in (
                "", "null", "NA",
                "NaN", "nan",
            )
            else np.nan
            for v in parts[1:]
        ])

    expr_df = pd.DataFrame(
        expr_vals,
        index=probe_ids,
        columns=sample_ids,
    )
    log(f"  Raw shape: {expr_df.shape}")
    log(f"  Sample IDs (first 4): "
        f"{sample_ids[:4]}")

    n = len(sample_ids)
    meta = {}
    for key, vals in meta_rows.items():
        short = key.replace("!Sample_", "")
        if len(vals) >= n:
            meta[short] = vals[:n]
        elif len(vals) > 0:
            meta[short] = (
                vals + [""] * (n - len(vals))
            )

    meta_df = pd.DataFrame(
        meta, index=sample_ids
    )
    log(f"  Meta shape: {meta_df.shape}")
    log(f"  Meta cols: "
        f"{list(meta_df.columns[:10])}")
    log("  Meta sample values:")
    for c in meta_df.columns[:8]:
        log(f"    [{c}]: "
            f"{meta_df[c].iloc[:3].tolist()}")

    return expr_df, meta_df, sample_ids

# ============================================================
# STEP 2: NORMALIZE
# ============================================================

def normalize(expr_df):
    log(f"\n  Normalizing {expr_df.shape}...")

    expr_df = expr_df.apply(
        pd.to_numeric, errors="coerce"
    )
    expr_df = expr_df.dropna(how="all", axis=0)
    expr_df = expr_df[expr_df.max(axis=1) > 0]
    expr_df = expr_df.clip(lower=1.0)
    expr_df = np.log2(expr_df)

    row_med = expr_df.median(axis=1)
    for col in expr_df.columns:
        mask = expr_df[col].isna()
        expr_df.loc[mask, col] = row_med[mask]

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
    return expr_df

# ============================================================
# STEP 3: PROBE MAPPING
# ============================================================

def map_probes(expr_df):
    log("")
    log("--- Probe mapping (GPL570) ---")

    probe_ids = set(expr_df.index)
    log(f"  Probes: {len(probe_ids)}")
    log(f"  Sample: {list(expr_df.index[:5])}")

    mapped = {}

    # Try downloading annotation
    if not os.path.exists(ANNOT_LOCAL) \
            or os.path.getsize(ANNOT_LOCAL) < 1000:
        for url in ANNOT_URLS:
            log(f"  Trying annotation: {url}")
            try:
                raw = fetch_url(url, timeout=120)
                with open(ANNOT_LOCAL, "wb") as f:
                    f.write(raw)
                log(f"  Downloaded: "
                    f"{len(raw)/1e6:.1f} MB")
                break
            except Exception as e:
                log(f"  Failed: {e}")

    # Parse annotation
    if os.path.exists(ANNOT_LOCAL) \
            and os.path.getsize(ANNOT_LOCAL) > 1000:
        log("  Parsing annotation...")
        try:
            import io as _io
            with open(ANNOT_LOCAL, "rb") as f:
                raw = f.read()
            with gzip.open(
                _io.BytesIO(raw), "rt",
                encoding="utf-8",
                errors="ignore",
            ) as gz:
                lines = gz.readlines()

            log(f"  Lines: {len(lines)}")
            shown = 0
            for line in lines:
                s = line.strip()
                if s and not s.startswith("#") \
                        and shown < 3:
                    log(f"  Preview: {s[:100]}")
                    shown += 1

            in_t = False
            cols = None
            ic = sc = None

            for line in lines:
                line = line.rstrip()

                if "platform_table_begin" in line:
                    in_t = True
                    cols = None
                    continue
                if "platform_table_end" in line:
                    break

                if not in_t:
                    s = line.lstrip()
                    if (s.startswith("ID")
                            or s.startswith('"ID')):
                        in_t  = True
                        parts = line.split("\t")
                        cols  = [
                            p.strip().strip('"')
                            for p in parts
                        ]
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
                        log(f"  Header: {cols[:6]}")
                        log(f"  id={ic} sym={sc}")
                    continue

                if cols is None:
                    parts = line.split("\t")
                    cols  = [
                        p.strip().strip('"')
                        for p in parts
                    ]
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
                    log(f"  Header: {cols[:6]}")
                    log(f"  id={ic} sym={sc}")
                    continue

                if ic is None or sc is None:
                    continue

                parts = line.split("\t")
                if len(parts) <= max(ic, sc):
                    continue

                p = parts[ic].strip().strip('"')
                s = parts[sc].strip().strip('"')

                if (p and s
                        and s not in
                        ("---", "", "NA", "null")
                        and p in probe_ids):
                    sym = (
                        s.split(" /// ")[0]
                         .split(" // ")[0]
                         .split(",")[0]
                         .strip()
                    )
                    if sym and len(sym) > 1:
                        mapped[p] = sym

            log(f"  Annotation mapped: {len(mapped)}")

        except Exception as e:
            log(f"  Annotation parse error: {e}")

    # Hard-coded fallback
    if len(mapped) < 1000:
        log("  Using hard-coded target probe map...")
        for probe, gene in TARGET_PROBES.items():
            if probe in probe_ids \
                    and probe not in mapped:
                mapped[probe] = gene
        hc = set(
            g for p, g in TARGET_PROBES.items()
            if p in probe_ids
        )
        log(f"  Hard-coded genes: {len(hc)}")
        log(f"  Genes: {sorted(hc)}")

    if len(mapped) < 5:
        log("  CRITICAL: Probe mapping failed.")
        sys.exit(1)

    log(f"  Total mapped: {len(mapped)}")

    valid = [p for p in mapped
             if p in expr_df.index]
    sub   = expr_df.loc[valid].copy()
    sub["_symbol"] = [mapped[p] for p in sub.index]
    sub["_mean"]   = sub.drop(
        columns=["_symbol"]
    ).mean(axis=1)
    sub = sub.sort_values("_mean", ascending=False)
    sub = sub.drop_duplicates(
        subset=["_symbol"], keep="first"
    )
    syms = sub["_symbol"].values
    sub  = sub.drop(columns=["_symbol", "_mean"])
    sub.index = syms

    log(f"  Gene matrix: {len(sub)} genes")
    found = [g for g in ALL_TARGET
             if g in sub.index]
    miss  = [g for g in ALL_TARGET
             if g not in sub.index]
    log(f"  Target genes: "
        f"{len(found)}/{len(ALL_TARGET)}")
    if miss:
        log(f"  Missing: {miss}")

    sub.to_csv(
        os.path.join(RESULTS_DIR, "gene_matrix.csv")
    )
    log(f"  Saved: gene_matrix.csv")
    return sub

# ============================================================
# STEP 4: CLASSIFY SAMPLES
# ============================================================

def classify_samples(gene_df, meta_df):
    log("")
    log("--- Classifying samples ---")
    log(f"  Total samples: {len(meta_df)}")

    # Print ALL meta columns and first 4 values
    # so we can see exactly what is available
    log("\n  ALL META COLUMNS:")
    for c in meta_df.columns:
        vals = meta_df[c].iloc[:4].tolist()
        log(f"  [{c}]: {vals}")

    expr_T = gene_df.T
    merged = expr_T.join(meta_df, how="left")
    merged["group"] = "UNKNOWN"

    # ---- Strategy 1: source_name_ch1 ----
    for col in meta_df.columns:
        if merged["group"].eq("UNKNOWN").all() \
                or True:
            vals = meta_df[col].fillna(
                ""
            ).str.lower()
            n_t = vals.str.contains(
                r"gastric.cancer|tumor|cancer"
                r"|adenocarcinoma|carcinoma",
                regex=True,
            ).sum()
            n_n = vals.str.contains(
                r"normal|adjacent|non.tumor"
                r"|nontumor|non-cancerous"
                r"|non-neoplastic|benign",
                regex=True,
            ).sum()
            if n_t > 5 or n_n > 5:
                log(f"  Using col '{col}': "
                    f"T={n_t} N={n_n}")
                sv = merged[col].fillna(
                    ""
                ).str.lower()
                merged.loc[
                    sv.str.contains(
                        r"gastric.cancer|tumor"
                        r"|cancer|adenocarcinoma"
                        r"|carcinoma",
                        regex=True,
                    ),
                    "group",
                ] = "TUMOR"
                merged.loc[
                    sv.str.contains(
                        r"normal|adjacent"
                        r"|non.tumor|nontumor"
                        r"|non-cancerous"
                        r"|non-neoplastic|benign",
                        regex=True,
                    ),
                    "group",
                ] = "NORMAL"
                break

    # ---- Strategy 2: scan characteristics ----
    for col in meta_df.columns:
        if "characteristics" not in col.lower():
            continue
        for idx in merged.index:
            if merged.loc[idx, "group"] != "UNKNOWN":
                continue
            val = str(
                merged.loc[idx, col]
            ).lower()
            if any(x in val for x in [
                "tumor", "cancer",
                "adenocarcinoma", "carcinoma",
            ]):
                merged.loc[idx, "group"] = "TUMOR"
            elif any(x in val for x in [
                "normal", "adjacent",
                "non-tumor", "nontumor",
                "non-cancerous", "non-neoplastic",
            ]):
                merged.loc[idx, "group"] = "NORMAL"

    # ---- Strategy 3: title ----
    if "title" in meta_df.columns:
        for idx in merged.index:
            if merged.loc[idx, "group"] != "UNKNOWN":
                continue
            val = str(
                merged.loc[idx, "title"]
            ).lower()
            if any(x in val for x in [
                "tumor", "cancer", "gc",
                "gastric cancer",
            ]):
                merged.loc[idx, "group"] = "TUMOR"
            elif any(x in val for x in [
                "normal", "adjacent",
                "non-tumor", "nontumor", "non",
            ]):
                merged.loc[idx, "group"] = "NORMAL"

    # ---- Strategy 4: description ----
    if "description" in meta_df.columns:
        for idx in merged.index:
            if merged.loc[idx, "group"] != "UNKNOWN":
                continue
            val = str(
                merged.loc[idx, "description"]
            ).lower()
            if "tumor" in val or "cancer" in val:
                merged.loc[idx, "group"] = "TUMOR"
            elif "normal" in val \
                    or "adjacent" in val:
                merged.loc[idx, "group"] = "NORMAL"

    # ---- Strategy 5: geo_accession prefix ----
    # GSE66229: tumor GSM IDs tend to be
    # higher range — not reliable, skip

    n_t = (merged["group"] == "TUMOR").sum()
    n_n = (merged["group"] == "NORMAL").sum()
    n_u = (merged["group"] == "UNKNOWN").sum()
    log(f"\n  TUMOR  : {n_t}")
    log(f"  NORMAL : {n_n}")
    log(f"  UNKNOWN: {n_u}")

    if n_u > 0:
        log("\n  Unknown samples (first 10):")
        for idx in merged[
            merged["group"] == "UNKNOWN"
        ].index[:10]:
            log(f"    {idx}")
            for c in meta_df.columns[:5]:
                if c in merged.columns:
                    log(f"      {c}: "
                        f"{merged.loc[idx, c]}")

    # Emergency fallback:
    # If classification completely failed,
    # try splitting by sample index position
    # GSE66229 is known to have tumors first
    # then normals — try 300T/100N split
    if n_t < 5 and n_n < 5:
        log("\n  Classification failed entirely.")
        log("  Emergency: splitting by position")
        log("  GSE66229: ~300 tumor, 38 normal")
        log("  Assuming last 38 are normal...")
        n_samples = len(merged)
        n_normal  = 38
        n_tumor   = n_samples - n_normal
        merged.iloc[
            :n_tumor, merged.columns.get_loc("group")
        ] = "TUMOR"
        merged.iloc[
            n_tumor:, merged.columns.get_loc("group")
        ] = "NORMAL"
        n_t = (merged["group"] == "TUMOR").sum()
        n_n = (merged["group"] == "NORMAL").sum()
        log(f"  After split: T={n_t} N={n_n}")
        log("  WARNING: positional split used")
        log("  Verify results make biological sense")

    tumor  = merged[merged["group"] == "TUMOR"].copy()
    normal = merged[merged["group"] == "NORMAL"].copy()

    log(f"\n  Final: TUMOR={len(tumor)} "
        f"NORMAL={len(normal)}")

    if len(tumor) < 3 or len(normal) < 3:
        log("  CRITICAL: Too few samples.")
        log("  Paste the meta output above")
        log("  to diagnose classification.")
        sys.exit(1)

    meta_df.to_csv(
        os.path.join(RESULTS_DIR, "metadata.csv")
    )
    return merged, tumor, normal

# ============================================================
# STEP 5: SADDLE POINT ANALYSIS
# ============================================================

def saddle_point_analysis(tumor, normal):
    log("")
    log("=" * 65)
    log("STEP 5: SADDLE POINT ANALYSIS")
    log("STAD TUMOR vs NORMAL GASTRIC MUCOSA")
    log("=" * 65)
    log(f"  TUMOR  : {len(tumor)}")
    log(f"  NORMAL : {len(normal)}")
    log("")
    log("  PREDICTIONS:")
    log("  DOWN: CLDN18/MUC5AC/TFF1/GKN1/CDH1")
    log("  UP:   CDX2/MUC2/KRT20/VIM/CDH2")
    log("  LOCK: EZH2 (5th cancer)")
    log("  FIND: ERBB2 elevated")

    gene_cols = [
        c for c in tumor.columns
        if c in ALL_TARGET
        and c in normal.columns
    ]

    log(f"\n  {'Gene':<10} {'Role':<11} "
        f"{'Normal':>9} {'Tumor':>9} "
        f"{'Change':>9}  p-value")
    log(f"  {'-'*68}")

    results = []
    for gene in ALL_TARGET:
        if gene not in gene_cols:
            continue
        nv = normal[gene].dropna().values
        tv = tumor[gene].dropna().values
        if len(nv) < 3 or len(tv) < 3:
            continue
        nm   = nv.mean()
        tm   = tv.mean()
        chg  = (
            (tm - nm) / nm * 100
            if abs(nm) > 0.0001 else np.nan
        )
        _, ps = safe_mwu(nv, tv, "greater")
        _, pe = safe_mwu(tv, nv, "greater")
        p_use = (
            min(ps, pe)
            if not (np.isnan(ps) or np.isnan(pe))
            else np.nan
        )
        role = ROLE_MAP.get(gene, "OTHER")
        cs   = (
            f"{chg:+.1f}%"
            if not np.isnan(chg) else "N/A"
        )
        pstr = (
            fmt_p(p_use)
            if not np.isnan(p_use)
            else "p=N/A"
        )
        log(f"  {gene:<10} {role:<11} "
            f"{nm:>9.4f} {tm:>9.4f} "
            f"{cs:>9}  {pstr}")
        results.append({
            "gene":        gene,
            "role":        role,
            "normal_mean": nm,
            "tumor_mean":  tm,
            "change_pct":  chg,
            "p_value":     p_use,
        })

    rdf = pd.DataFrame(results)
    rdf.to_csv(
        os.path.join(
            RESULTS_DIR, "saddle_results.csv"
        ),
        index=False,
    )
    log(f"\n  Saved: saddle_results.csv")

    log(f"\n  IDENTITY SWITCH CHECK:")
    for g in [
        "MUC5AC", "CLDN18", "TFF1", "GKN1",
        "CDX2", "MUC2", "KRT20",
    ]:
        if g in gene_cols:
            nm_v = normal[g].mean()
            tm_v = tumor[g].mean()
            chg  = (
                (tm_v - nm_v) / nm_v * 100
                if abs(nm_v) > 0.0001
                else np.nan
            )
            cs = (
                f"{chg:+.1f}%"
                if not np.isnan(chg) else "N/A"
            )
            log(f"    {g:<10} "
                f"N:{nm_v:.4f} "
                f"T:{tm_v:.4f} {cs}")

    return rdf, tumor, normal

# ============================================================
# STEP 6: DEPTH SCORING
# ============================================================

def depth_scoring(merged, tumor, normal):
    log("")
    log("=" * 65)
    log("STEP 6: BLOCK DEPTH SCORING")
    log("=" * 65)

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

    tumor = tumor.copy()
    depth = pd.Series(
        np.zeros(len(tumor)), index=tumor.index
    )
    comp = 0

    sw_avail = [g for g in SWITCH_GENES
                if g in gene_cols]
    fa_avail = [g for g in FA_MARKERS
                if g in gene_cols]

    log(f"  Switch genes: {sw_avail}")
    log(f"  FA markers  : {fa_avail}")

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

    log(f"\n  Block depth ({len(tumor)} tumors):")
    log(f"    Mean  : {depth.mean():.4f}")
    log(f"    Median: {depth.median():.4f}")
    log(f"    Std   : {depth.std():.4f}")
    log(f"    Min   : {depth.min():.4f}")
    log(f"    Max   : {depth.max():.4f}")

    corrs = []
    for gene in gene_cols:
        if gene in [
            "block_depth", "group",
            "erbb2_status",
        ]:
            continue
        rv, pv = safe_pearsonr(
            tumor["block_depth"].values,
            tumor[gene].values,
        )
        if not np.isnan(rv):
            corrs.append((gene, rv, pv))
    corrs.sort(
        key=lambda x: abs(x[1]), reverse=True
    )

    log(f"\n  Top depth correlations (top 20):")
    log(f"  {'Gene':<10} {'r':>8}  "
        f"p-value         Role")
    log(f"  {'-'*50}")
    for gene, rv, pv in corrs[:20]:
        role = ROLE_MAP.get(gene, "")
        log(f"  {gene:<10} {rv:>+8.4f}  "
            f"{fmt_p(pv)}  {role}")

    return tumor, corrs

# ============================================================
# STEP 7: EZH2 — 5TH CANCER PREDICTION
# ============================================================

def ezh2_analysis(tumor, normal):
    log("")
    log("=" * 65)
    log("STEP 7: EZH2 ANALYSIS")
    log("5th solid cancer prediction")
    log("r(EZH2, depth) > 0 predicted")
    log("=" * 65)

    if len(tumor) < 3 or len(normal) < 3:
        log("  Insufficient samples — skip")
        return tumor

    gene_cols = [
        c for c in tumor.columns
        if c in ALL_TARGET
    ]

    if "EZH2" not in gene_cols \
            or "EZH2" not in normal.columns:
        log("  EZH2 not available")
        return tumor

    nm  = normal["EZH2"].mean()
    tm  = tumor["EZH2"].mean()
    chg = (tm - nm) / nm * 100

    log(f"\n  EZH2 normal: {nm:.4f} "
        f"± {normal['EZH2'].std():.4f}")
    log(f"  EZH2 tumor : {tm:.4f} "
        f"± {tumor['EZH2'].std():.4f}")
    log(f"  Change     : {chg:+.1f}%")

    _, pv = safe_mwu(
        normal["EZH2"].values,
        tumor["EZH2"].values,
        alternative="less",
    )
    pstr = fmt_p(pv) if not np.isnan(pv) else "N/A"
    log(f"  p (tumor > normal): {pstr}")
    conf = (
        "CONFIRMED"
        if (not np.isnan(pv) and pv < 0.05)
        else "NOT CONFIRMED"
    )
    log(f"  EZH2 elevated: {conf}")

    rv2 = pv2 = np.nan
    if "block_depth" in tumor.columns \
            and len(tumor) >= 3:
        rv2, pv2 = safe_pearsonr(
            tumor["block_depth"].values,
            tumor["EZH2"].values,
        )
        if not np.isnan(rv2):
            log(f"\n  r(EZH2, depth) = {rv2:+.4f} "
                f"p={pv2:.2e}")
            conf2 = (
                "CONFIRMED"
                if pv2 < 0.05 and rv2 > 0
                else "NOT CONFIRMED"
            )
            log(f"  r > 0 predicted: {conf2}")

    log(f"\n  Cross-cancer EZH2 pattern:")
    log(f"  BRCA: elevated ✓")
    log(f"  PAAD: elevated ✓  r>0 ✓")
    log(f"  PRAD: elevated ✓  r>0 ✓")
    up = (not np.isnan(pv) and pv < 0.05)
    r_ok = (
        not np.isnan(rv2)
        and pv2 < 0.05
        and rv2 > 0
    )
    log(f"  STAD: "
        f"{'elevated ✓' if up else 'not confirmed'}"
        f"  "
        f"{'r>0 ✓' if r_ok else 'r>0 ?'}")

    return tumor

# ============================================================
# STEP 8: ERBB2/HER2 ANALYSIS
# ============================================================

def erbb2_analysis(tumor, normal):
    log("")
    log("=" * 65)
    log("STEP 8: ERBB2/HER2 ANALYSIS")
    log("Must find from geometry alone")
    log("Trastuzumab = standard of care ~20%")
    log("=" * 65)

    if len(tumor) < 3 or len(normal) < 3:
        log("  Insufficient samples — skip")
        return tumor

    gene_cols = [
        c for c in tumor.columns
        if c in ALL_TARGET
    ]

    log(f"\n  {'Gene':<8} "
        f"{'Normal':>9} {'Tumor':>9} "
        f"{'Change':>9}  p")
    log(f"  {'-'*52}")

    for gene in [
        "ERBB2", "GRB7", "EGFR",
        "FGFR2", "MET", "ERBB3", "ERBB4",
    ]:
        if gene not in gene_cols \
                or gene not in normal.columns:
            continue
        nm  = normal[gene].mean()
        tm  = tumor[gene].mean()
        chg = (
            (tm - nm) / nm * 100
            if abs(nm) > 0.0001 else np.nan
        )
        _, pv = safe_mwu(
            normal[gene].values,
            tumor[gene].values,
            alternative="less",
        )
        cs  = (
            f"{chg:+.1f}%"
            if not np.isnan(chg) else "N/A"
        )
        pstr = (
            fmt_p(pv)
            if not np.isnan(pv) else "N/A"
        )
        log(f"  {gene:<8} "
            f"{nm:>9.4f} {tm:>9.4f} "
            f"{cs:>9}  {pstr}")

    tumor = tumor.copy()
    if "ERBB2" in gene_cols and len(tumor) >= 5:
        ev = tumor["ERBB2"].values
        log(f"\n  ERBB2 bimodal check:")
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
                log(f"    Expected  : ~20%")
                tumor["erbb2_status"] = np.where(
                    tumor["ERBB2"] > thr,
                    "HER2_high", "HER2_low"
                )
                if "block_depth" in tumor.columns:
                    dh = tumor[
                        tumor["erbb2_status"]
                        == "HER2_high"
                    ]["block_depth"]
                    dl = tumor[
                        tumor["erbb2_status"]
                        == "HER2_low"
                    ]["block_depth"]
                    if len(dh) > 1 and len(dl) > 1:
                        log(f"\n    Depth by HER2:")
                        log(f"      HER2-high: "
                            f"{dh.mean():.4f} "
                            f"± {dh.std():.4f}")
                        log(f"      HER2-low : "
                            f"{dl.mean():.4f} "
                            f"�� {dl.std():.4f}")
                        _, pp = safe_mwu(
                            dh.values, dl.values,
                            "two-sided",
                        )
                        if not np.isnan(pp):
                            log(f"      p={pp:.4f}")
            else:
                log("    No bimodal threshold found")
        except Exception as e:
            log(f"    KDE error: {e}")

    return tumor

# ============================================================
# STEP 9: IDENTITY SWITCH
# ============================================================

def identity_switch(tumor, normal):
    log("")
    log("=" * 65)
    log("STEP 9: GASTRIC→INTESTINAL SWITCH")
    log("MUC5AC → MUC2 | CLDN18 → CDX2")
    log("=" * 65)

    if len(tumor) < 3 or len(normal) < 3:
        log("  Insufficient samples — skip")
        return

    gene_cols = [
        c for c in tumor.columns
        if c in ALL_TARGET
        and c in normal.columns
    ]

    gastric_m = [
        g for g in [
            "CLDN18", "MUC5AC", "TFF1",
            "GKN1", "GKN2", "ATP4A",
            "PGC", "TFF2", "MUC6",
        ] if g in gene_cols
    ]
    intestinal_m = [
        g for g in [
            "CDX2", "MUC2", "KRT20",
            "VIL1", "FABP1",
        ] if g in gene_cols
    ]

    log(f"\n  Gastric ({len(gastric_m)}):")
    log(f"  {'Gene':<10} "
        f"{'Normal':>9} {'Tumor':>9} Change")
    log(f"  {'-'*40}")
    for g in gastric_m:
        nm  = normal[g].mean()
        tm  = tumor[g].mean()
        chg = (
            (tm - nm) / nm * 100
            if abs(nm) > 0.0001 else np.nan
        )
        cs = (
            f"{chg:+.1f}%"
            if not np.isnan(chg) else "N/A"
        )
        log(f"  {g:<10} "
            f"{nm:>9.4f} {tm:>9.4f} {cs:>9}")

    log(f"\n  Intestinal ({len(intestinal_m)}):")
    log(f"  {'Gene':<10} "
        f"{'Normal':>9} {'Tumor':>9} Change")
    log(f"  {'-'*40}")
    for g in intestinal_m:
        nm  = normal[g].mean()
        tm  = tumor[g].mean()
        chg = (
            (tm - nm) / nm * 100
            if abs(nm) > 0.0001 else np.nan
        )
        cs = (
            f"{chg:+.1f}%"
            if not np.isnan(chg) else "N/A"
        )
        log(f"  {g:<10} "
            f"{nm:>9.4f} {tm:>9.4f} {cs:>9}")

    if gastric_m and intestinal_m:
        gs_n = normal[gastric_m].mean(axis=1).mean()
        gs_t = tumor[gastric_m].mean(axis=1).mean()
        is_n = normal[intestinal_m].mean(axis=1).mean()
        is_t = tumor[intestinal_m].mean(axis=1).mean()
        log(f"\n  Identity composite:")
        log(f"    Gastric    "
            f"N:{gs_n:.4f} T:{gs_t:.4f} "
            f"({(gs_t-gs_n)/gs_n*100:+.1f}%)")
        log(f"    Intestinal "
            f"N:{is_n:.4f} T:{is_t:.4f} "
            f"({(is_t-is_n)/is_n*100:+.1f}%)")
        if gs_t < gs_n and is_t > is_n:
            log("\n  VERDICT: "
                "GASTRIC→INTESTINAL CONFIRMED")
        elif gs_t < gs_n:
            log("\n  VERDICT: "
                "Gastric loss confirmed — "
                "intestinal gain not confirmed")
        elif is_t > is_n:
            log("\n  VERDICT: "
                "Intestinal gain confirmed — "
                "gastric loss not confirmed")
        else:
            log("\n  VERDICT: "
                "Identity switch not confirmed")

# ============================================================
# STEP 10: FIGURE
# ============================================================

def generate_figure(
    merged, tumor, normal,
    results_df, corrs,
):
    log("")
    log("--- Generating figure ---")

    if len(tumor) < 2 or len(normal) < 2:
        log("  Insufficient data for figure")
        return

    fig = plt.figure(figsize=(26, 20))
    fig.suptitle(
        "Stomach Adenocarcinoma �� "
        "False Attractor Analysis\n"
        f"Dataset: GSE66229 | "
        f"T={len(tumor)} N={len(normal)} | "
        "OrganismCore 2026-03-01\n"
        "Gastric→intestinal identity switch | "
        "EZH2 (5th cancer) | ERBB2/HER2",
        fontsize=10,
        fontweight="bold",
        y=0.99,
    )
    gs = gridspec.GridSpec(
        3, 3, figure=fig,
        hspace=0.52, wspace=0.42,
    )

    clr_n = "#2980b9"
    clr_t = "#c0392b"
    gene_cols = [
        c for c in merged.columns
        if c in ALL_TARGET
    ]

    def bar_pair(ax, genes, title):
        avail = [g for g in genes
                 if g in gene_cols]
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

    ax_a = fig.add_subplot(gs[0, 0])
    bar_pair(
        ax_a,
        ["CLDN18", "MUC5AC", "TFF1",
         "GKN1",   "GKN2",   "CDH1"],
        "A — Gastric Switch Genes\n"
        "Predicted DOWN",
    )

    ax_b = fig.add_subplot(gs[0, 1])
    bar_pair(
        ax_b,
        ["CDX2", "MUC2", "KRT20",
         "VIM",  "CDH2", "TWIST1"],
        "B — False Attractor Markers\n"
        "Predicted UP",
    )

    ax_c = fig.add_subplot(gs[0, 2])
    if len(results_df) > 0:
        pdf = results_df.dropna(
            subset=["change_pct"]
        ).sort_values("change_pct")
        colors = [
            clr_t if v < 0 else "#27ae60"
            for v in pdf["change_pct"]
        ]
        ax_c.barh(
            pdf["gene"], pdf["change_pct"],
            color=colors,
        )
        ax_c.axvline(
            0, color="black", linewidth=0.8
        )
        ax_c.set_xlabel(
            "% change vs normal", fontsize=8
        )
        ax_c.set_title(
            "C — All Target Genes\n"
            "% change tumor vs normal",
            fontsize=9,
        )
        ax_c.tick_params(axis="y", labelsize=6)

    ax_d = fig.add_subplot(gs[1, 0])
    bar_pair(
        ax_d,
        ["EZH2", "EED",   "SUZ12",
         "BMI1", "KDM6A", "DNMT3A"],
        "D — Epigenetic Lock\n"
        "EZH2 predicted UP (5th cancer)",
    )

    ax_e = fig.add_subplot(gs[1, 1])
    bar_pair(
        ax_e,
        ["ERBB2", "EGFR",  "FGFR2",
         "MET",   "MYC",   "CCND1"],
        "E — Scaffold / HER2\n"
        "ERBB2 must be elevated",
    )

    ax_f = fig.add_subplot(gs[1, 2])
    bar_pair(
        ax_f,
        ["CDH1",  "CDH2",  "VIM",
         "SNAI1", "SNAI2", "TWIST1", "ZEB1"],
        "F — EMT Markers\n"
        "CDH1 loss / CDH2 VIM gain?",
    )

    ax_g = fig.add_subplot(gs[2, 0])
    if corrs:
        top = corrs[:15]
        gc  = [c[0] for c in top]
        vc  = [c[1] for c in top]
        cc  = [
            clr_t if v < 0 else "#27ae60"
            for v in vc
        ]
        ax_g.barh(gc, vc, color=cc)
        ax_g.axvline(
            0, color="black", linewidth=0.8
        )
        ax_g.set_xlabel(
            "r with depth", fontsize=8
        )
        ax_g.set_title(
            "G — Depth Correlations\nTop 15",
            fontsize=9,
        )
        ax_g.tick_params(axis="y", labelsize=7)

    ax_h = fig.add_subplot(gs[2, 1])
    id_genes = [
        g for g in [
            "CLDN18", "MUC5AC", "TFF1",
            "GKN1",   "CDX2",   "MUC2",
            "KRT20",
        ] if g in gene_cols
    ]
    if id_genes:
        n_m = [
            normal[g].mean()
            if g in normal.columns else 0
            for g in id_genes
        ]
        t_m = [tumor[g].mean() for g in id_genes]
        x   = np.arange(len(id_genes))
        w   = 0.35
        ax_h.bar(
            x - w/2, n_m, w,
            color=clr_n, label="Normal",
            alpha=0.85,
        )
        ax_h.bar(
            x + w/2, t_m, w,
            color=clr_t, label="STAD",
            alpha=0.85,
        )
        ax_h.set_xticks(x)
        ax_h.set_xticklabels(
            id_genes, rotation=45,
            ha="right", fontsize=8,
        )
        ax_h.set_title(
            "H — Identity Switch\n"
            "Gastric → Intestinal?",
            fontsize=9,
        )
        ax_h.legend(fontsize=7)
        n_gast = sum(
            1 for g in id_genes
            if g in ["CLDN18", "MUC5AC",
                     "TFF1", "GKN1"]
        )
        if 0 < n_gast < len(id_genes):
            ax_h.axvline(
                n_gast - 0.5,
                color="gray",
                linewidth=1.5, linestyle="--",
            )

    ax_i = fig.add_subplot(gs[2, 2])
    ax_i.axis("off")
    n_found = len([g for g in ALL_TARGET
                   if g in gene_cols])

    def chg_str(gene):
        if gene not in gene_cols \
                or gene not in normal.columns:
            return "N/A"
        nm_v = normal[gene].mean()
        tm_v = tumor[gene].mean()
        if abs(nm_v) < 0.0001:
            return "N/A"
        return f"{(tm_v-nm_v)/nm_v*100:+.1f}%"

    summary = (
        "I — SCRIPT 1 SUMMARY\n"
        "─────────────────────────\n"
        f"TUMOR  : {len(tumor)}\n"
        f"NORMAL : {len(normal)}\n"
        f"Genes  : {n_found}/{len(ALL_TARGET)}\n\n"
        "SWITCH:\n"
        f"  CLDN18 : {chg_str('CLDN18')}\n"
        f"  MUC5AC : {chg_str('MUC5AC')}\n"
        f"  TFF1   : {chg_str('TFF1')}\n"
        f"  GKN1   : {chg_str('GKN1')}\n\n"
        "FA MARKERS:\n"
        f"  CDX2   : {chg_str('CDX2')}\n"
        f"  MUC2   : {chg_str('MUC2')}\n"
        f"  VIM    : {chg_str('VIM')}\n\n"
        "LOCK:\n"
        f"  EZH2   : {chg_str('EZH2')}\n\n"
        "MUST FIND:\n"
        f"  ERBB2  : {chg_str('ERBB2')}\n\n"
        "Cross-cancer EZH2:\n"
        "  BRCA ✓ PAAD ✓ PRAD ✓\n"
        "  STAD: ?\n\n"
        "Framework: OrganismCore\n"
        "2026-03-01"
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
        RESULTS_DIR,
        "stad_false_attractor.png",
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
    log("FALSE ATTRACTOR ANALYSIS — SCRIPT 1")
    log("Dataset: GSE66229")
    log("Framework: OrganismCore")
    log("Doc: pre-STAD | Date: 2026-03-01")
    log("=" * 65)
    log("")
    log("  PREDICTIONS LOCKED:")
    log("  Switch: CLDN18/MUC5AC/TFF1/GKN1 DOWN")
    log("  FA:     CDX2/MUC2/KRT20/VIM UP")
    log("  Lock:   EZH2 UP (5th cancer)")
    log("  Find:   ERBB2/HER2 elevated")
    log("  Switch: MUC5AC→MUC2 identity")

    log("\n=== STEP 0: DOWNLOAD ===")
    matrix_path = download_all()

    log("\n=== STEP 1: PARSE MATRIX ===")
    expr_df, meta_df, sample_ids = \
        parse_series_matrix(matrix_path)

    log("\n=== STEP 2: NORMALIZE ===")
    expr_df = normalize(expr_df)

    log("\n=== STEP 3: PROBE MAPPING ===")
    gene_df = map_probes(expr_df)

    log("\n=== STEP 4: CLASSIFY ===")
    merged, tumor, normal = \
        classify_samples(gene_df, meta_df)

    log("\n=== STEP 5: SADDLE POINT ===")
    results_df, tumor, normal = \
        saddle_point_analysis(tumor, normal)

    log("\n=== STEP 6: DEPTH SCORING ===")
    tumor, corrs = depth_scoring(
        merged, tumor, normal
    )

    log("\n=== STEP 7: EZH2 ===")
    tumor = ezh2_analysis(tumor, normal)

    log("\n=== STEP 8: ERBB2/HER2 ===")
    tumor = erbb2_analysis(tumor, normal)

    log("\n=== STEP 9: IDENTITY SWITCH ===")
    identity_switch(tumor, normal)

    log("\n=== STEP 10: FIGURE ===")
    generate_figure(
        merged, tumor, normal,
        results_df, corrs,
    )

    write_log()
    log(f"\n  Log: {LOG_FILE}")
    log(f"  Outputs: {RESULTS_DIR}")
    log("\n=== SCRIPT 1 COMPLETE ===")


if __name__ == "__main__":
    main()
