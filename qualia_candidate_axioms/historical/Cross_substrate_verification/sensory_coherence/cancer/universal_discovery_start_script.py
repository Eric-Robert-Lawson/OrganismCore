# ORGANIS MCORE — UNIVERSAL SCRIPT 1
# CANCER FALSE ATTRACTOR DISCOVERY
# Cancer-Agnostic Geometric Landscape Scan
# The geometry reveals itself.
# No pre-loaded cancer-specific assumptions.
# Version 1.0
# Date: 2026-03-03

---

## THE PROBLEM THIS FIXES

Every previous Script 1 was written for a specific cancer.
NKX3-1 hardcoded. FOXA1 hardcoded. ILMN probe maps hardcoded.
The cancer identity was loaded BEFORE the data ran.

That is backwards.

The workflow is:
  Principles first.
  Data second.
  The geometry reveals the attractor.
  You do not tell the geometry what to find.

This script does not know what cancer it is analyzing.
It does not know which genes are switches.
It does not know which genes are FA markers.
It asks the data.

---

## WHAT THIS SCRIPT DOES

Given any GEO accession:

  1. Downloads the expression matrix
  2. Downloads sample metadata
  3. Separates tumor from normal by metadata keywords
  4. Runs a full-genome saddle point scan
     — every detected gene, tumor vs normal —
     — no pre-selected gene panels —
  5. Ranks genes by absolute % change AND significance
  6. Identifies:
     — Top suppressed genes (switch gene candidates)
     — Top elevated genes (FA marker candidates)
  7. Computes a blind depth score from the
     top N suppressed + top N elevated genes
  8. Runs depth correlations across all genes
  9. Outputs the full ranked table
  10. The analyst reads the output and
      THEN identifies the attractor geometry

The landscape reveals itself.
The analyst names what they see AFTER.

---

## WHAT THIS SCRIPT DOES NOT DO

  Does not pre-load gene panels
  Does not assume which genes are switches
  Does not assume which genes are FA markers
  Does not hard-code probe maps
  Does not require prior knowledge of the cancer
  Does not consult literature before running
  Does not name the attractor before it appears

---

## THE SCRIPT

```python
"""
OrganismCore — Universal False Attractor Discovery
SCRIPT 1 — BLIND GEOMETRIC LANDSCAPE SCAN

The geometry reveals itself.

No pre-loaded cancer-specific gene lists.
No hardcoded switch genes or FA markers.
No probe maps for a specific platform.

Give it any GEO accession with:
  - Tumor samples
  - Normal/adjacent samples
  - Any expression platform (RNA-seq, microarray)

It will show you the attractor landscape.
You name what you see.

Usage:
  Set GEO_ACCESSION below.
  Set N_TOP_GENES (default 50 — top movers).
  Run.
  Read the output.
  THEN write your Phase 1 document.

Author: Eric Robert Lawson
Framework: OrganismCore
Protocol: Phase 2 — Script 1 Discovery Run
Version: 1.0
Date: 2026-03-03
"""

import os
import sys
import gzip
import urllib.request
import urllib.error
import tarfile
import io
import time
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# ============================================================
# CONFIGURATION — SET THESE BEFORE RUNNING
# ============================================================

GEO_ACCESSION = "GSE32571"   # <-- change to your accession

# How many top genes to include in blind depth score
# (top N suppressed + top N elevated)
N_TOP_GENES = 50

# Minimum sample counts to proceed
MIN_TUMOR  = 5
MIN_NORMAL = 3

# Output directory
BASE_DIR    = f"./{GEO_ACCESSION}_discovery/"
RESULTS_DIR = os.path.join(BASE_DIR, "results")
LOG_FILE    = os.path.join(RESULTS_DIR, "discovery_log.txt")

os.makedirs(BASE_DIR,    exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# ============================================================
# KEYWORDS FOR SAMPLE CLASSIFICATION
# These are generic. They do not assume cancer type.
# ============================================================

TUMOR_KEYWORDS = [
    "tumor", "cancer", "malignant", "carcinoma",
    "adenocarcinoma", "leukemia", "lymphoma",
    "sarcoma", "glioma", "glioblastoma",
    "neoplasm", "neoplastic", "primary",
    "metastatic", "metastasis", "disease",
    "case", "patient",
]

NORMAL_KEYWORDS = [
    "normal", "adjacent", "benign", "non-tumor",
    "nontumor", "non-malignant", "non-cancer",
    "healthy", "control", "bph",
    "non-neoplastic", "non-malignant",
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
# FETCH UTILITY
# ============================================================

def fetch_url(url, timeout=30, retries=3):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(
                req, timeout=timeout
            ) as r:
                return r.read()
        except Exception as e:
            log(f"  Fetch attempt {attempt+1} failed: {e}")
            time.sleep(2)
    return None

# ============================================================
# STEP 0: FETCH GEO SERIES METADATA
# Discover what files are available.
# Do not assume file names.
# ============================================================

def fetch_series_info(accession):
    log("=" * 65)
    log(f"STEP 0: SERIES DISCOVERY")
    log(f"Accession: {accession}")
    log("=" * 65)

    url = (
        "https://www.ncbi.nlm.nih.gov/geo/"
        f"query/acc.cgi?acc={accession}"
        "&targ=self&form=text&view=full"
    )
    raw = fetch_url(url)
    if raw is None:
        log("  ERROR: Could not fetch series info")
        return {}

    text = raw.decode("utf-8", errors="ignore")
    info = {}
    suppl_files = []

    for line in text.split("\n"):
        line = line.rstrip()
        if line.startswith("!Series_title"):
            info["title"] = line.split("=", 1)[1].strip()
        elif line.startswith("!Series_summary"):
            info["summary"] = info.get(
                "summary", ""
            ) + " " + line.split("=", 1)[1].strip()
        elif line.startswith("!Series_overall_design"):
            info["design"] = info.get(
                "design", ""
            ) + " " + line.split("=", 1)[1].strip()
        elif line.startswith("!Series_organism"):
            info["organism"] = line.split("=", 1)[1].strip()
        elif line.startswith("!Series_sample_count"):
            info["n_samples"] = line.split("=", 1)[1].strip()
        elif line.startswith(
            "!Series_supplementary_file"
        ):
            fname = line.split("=", 1)[1].strip()
            if fname:
                suppl_files.append(fname)

    info["suppl_files"] = suppl_files

    log(f"  Title   : {info.get('title', 'N/A')}")
    log(f"  Organism: {info.get('organism', 'N/A')}")
    log(f"  Samples : {info.get('n_samples', 'N/A')}")
    log(f"  Summary : {info.get('summary','')[:200]}")
    log(f"\n  Supplementary files ({len(suppl_files)}):")
    for f in suppl_files:
        log(f"    {f[-80:]}")

    return info

# ============================================================
# STEP 1: FETCH SAMPLE METADATA
# Classify tumor vs normal from sample characteristics.
# Do not assume tissue type — read what is there.
# ============================================================

def fetch_sample_metadata(accession):
    log("")
    log("=" * 65)
    log("STEP 1: SAMPLE METADATA")
    log("Classifying tumor vs normal from metadata.")
    log("=" * 65)

    cache = os.path.join(RESULTS_DIR, "metadata.csv")
    if os.path.exists(cache):
        df = pd.read_csv(cache, index_col=0)
        log(f"  Loaded cache: {len(df)} samples")
        return df

    url = (
        "https://www.ncbi.nlm.nih.gov/geo/"
        f"query/acc.cgi?acc={accession}"
        "&targ=gsm&form=text&view=full"
    )
    raw = fetch_url(url, timeout=60)
    if raw is None:
        log("  ERROR: Could not fetch sample metadata")
        return pd.DataFrame()

    text = raw.decode("utf-8", errors="ignore")
    samples  = []
    current  = {}

    for line in text.split("\n"):
        line = line.rstrip()
        if line.startswith("^SAMPLE"):
            if current:
                samples.append(current)
            current = {
                "gsm": line.split("=")[1].strip()
            }
        elif line.startswith("!Sample_title"):
            current["title"] = \
                line.split("=", 1)[1].strip()
        elif line.startswith(
            "!Sample_source_name_ch1"
        ):
            current["source"] = \
                line.split("=", 1)[1].strip()
        elif line.startswith(
            "!Sample_characteristics_ch1"
        ):
            val = line.split("=", 1)[1].strip()
            if ":" in val:
                k, v = val.split(":", 1)
                key = (
                    k.strip().lower()
                    .replace(" ", "_")
                )
                # Append if key already exists
                if key in current:
                    current[key] = (
                        current[key] + " | " + v.strip()
                    )
                else:
                    current[key] = v.strip()
    if current:
        samples.append(current)

    df = pd.DataFrame(samples)
    df.to_csv(cache)
    log(f"  Fetched {len(df)} samples")
    log(f"  Columns: {list(df.columns)[:10]}")

    # Show all characteristic keys found
    char_keys = [
        c for c in df.columns
        if c not in ["gsm", "title", "source"]
    ]
    log(f"\n  Characteristic fields found:")
    for k in char_keys:
        vals = df[k].dropna().value_counts().head(5)
        log(f"    {k}:")
        for v, n in vals.items():
            log(f"      {v!r:40s} n={n}")

    return df

# ============================================================
# STEP 2: CLASSIFY SAMPLES
# Use keywords — do not assume tissue type.
# Show the analyst what was classified and why.
# ============================================================

def classify_samples(meta_df):
    log("")
    log("=" * 65)
    log("STEP 2: SAMPLE CLASSIFICATION")
    log("Tumor vs Normal — keyword scan.")
    log("=" * 65)

    df = meta_df.copy()
    df["group"] = "UNKNOWN"

    # Build a single combined text field per sample
    text_cols = [
        c for c in df.columns
        if c not in ["gsm"]
    ]
    df["_combined"] = df[text_cols].fillna("").apply(
        lambda row: " ".join(str(v) for v in row).lower(),
        axis=1
    )

    # Classify
    for idx, row in df.iterrows():
        txt = row["_combined"]
        is_normal = any(kw in txt for kw in NORMAL_KEYWORDS)
        is_tumor  = any(kw in txt for kw in TUMOR_KEYWORDS)

        if is_normal and not is_tumor:
            df.at[idx, "group"] = "NORMAL"
        elif is_tumor and not is_normal:
            df.at[idx, "group"] = "TUMOR"
        elif is_normal and is_tumor:
            # Both — normal keyword takes precedence
            # (adjacent normal in tumor context)
            df.at[idx, "group"] = "NORMAL"
        # else: remains UNKNOWN

    n_t = (df["group"] == "TUMOR").sum()
    n_n = (df["group"] == "NORMAL").sum()
    n_u = (df["group"] == "UNKNOWN").sum()

    log(f"  TUMOR  : {n_t}")
    log(f"  NORMAL : {n_n}")
    log(f"  UNKNOWN: {n_u}")

    # Show first 5 of each class for verification
    for grp in ["TUMOR", "NORMAL", "UNKNOWN"]:
        sub = df[df["group"] == grp].head(5)
        if len(sub) > 0:
            log(f"\n  First {len(sub)} {grp}:")
            for _, row in sub.iterrows():
                log(
                    f"    {row['gsm']} — "
                    f"{str(row.get('title',''))[:60]}"
                )

    if n_t < MIN_TUMOR:
        log(
            f"\n  WARNING: Only {n_t} tumor samples. "
            f"Minimum is {MIN_TUMOR}."
        )
        log(
            "  REVIEW UNKNOWN samples manually."
        )
        log(
            "  If UNKNOWN are tumors, re-classify "
            "by adding keywords."
        )

    if n_n < MIN_NORMAL:
        log(
            f"\n  WARNING: Only {n_n} normal samples. "
            f"Minimum is {MIN_NORMAL}."
        )

    return df

# ============================================================
# STEP 3: FIND AND DOWNLOAD EXPRESSION MATRIX
# Handles: normalized text, raw txt.gz, matrix.
# Does not require knowing the platform in advance.
# ============================================================

def find_expression_matrix(series_info, accession):
    log("")
    log("=" * 65)
    log("STEP 3: EXPRESSION MATRIX DISCOVERY")
    log("=" * 65)

    suppl = series_info.get("suppl_files", [])

    # Priority order for file selection
    # Prefer normalized over raw
    # Prefer txt.gz over tar
    priority = []
    for f in suppl:
        flower = f.lower()
        score  = 0
        if "raw" in flower or "raw.tar" in flower:
            score -= 10
        if "normalized" in flower:
            score += 5
        if "non_normalized" in flower:
            score -= 3
        if flower.endswith(".txt.gz"):
            score += 4
        if flower.endswith(".csv.gz"):
            score += 4
        if "matrix" in flower:
            score += 3
        if "count" in flower:
            score += 2
        if "tpm" in flower or "fpkm" in flower:
            score += 3
        if "series_matrix" in flower:
            score += 2
        priority.append((score, f))

    priority.sort(reverse=True)

    log(f"  Ranked supplementary files:")
    for score, f in priority:
        log(f"    score={score:+3d}  {f[-70:]}")

    # Try each file in order
    for score, url in priority:
        if score < -5:
            log(f"  Skipping low-score file: {url[-50:]}")
            continue

        fname   = url.split("/")[-1]
        local   = os.path.join(BASE_DIR, fname)

        if os.path.exists(local):
            size_mb = os.path.getsize(local) / 1e6
            if size_mb > 0.05:
                log(f"  Found cached: {fname} "
                    f"({size_mb:.1f} MB)")
                result = try_load_matrix(local, fname)
                if result is not None:
                    return result

        log(f"  Downloading: {fname}")
        raw = fetch_url(url, timeout=120)
        if raw is None:
            log(f"  Download failed: {fname}")
            continue

        with open(local, "wb") as f:
            f.write(raw)
        size_mb = len(raw) / 1e6
        log(f"  Downloaded: {fname} ({size_mb:.1f} MB)")

        result = try_load_matrix(local, fname)
        if result is not None:
            return result

    # Fallback: try GEO Series Matrix file
    log("\n  Trying GEO Series Matrix fallback...")
    return try_series_matrix(accession)

# ============================================================
# MATRIX LOADERS
# ============================================================

def try_load_matrix(local_path, fname):
    """
    Try to load an expression matrix from a file.
    Returns (DataFrame, platform_type) or None.
    Handles:
      - gzipped tab-separated text (microarray/RNA-seq)
      - gzipped CSV
      - plain text
    """
    log(f"\n  Trying to load: {fname}")
    flower = fname.lower()

    try:
        # gzipped text/csv
        if flower.endswith(".gz"):
            with gzip.open(local_path, "rt",
                           errors="ignore") as f:
                # Peek at first few lines
                head = []
                for i, line in enumerate(f):
                    head.append(line.rstrip())
                    if i >= 10:
                        break

            log(f"  First line: {head[0][:100]}")
            if len(head) > 1:
                log(f"  Second line: {head[1][:100]}")

            # Determine separator
            sep = "\t"
            if "," in head[0] and "\t" not in head[0]:
                sep = ","

            # Determine if first line is header
            # by checking if it contains sample IDs
            # (non-numeric in most columns)
            with gzip.open(local_path, "rt",
                           errors="ignore") as f:
                df = pd.read_csv(
                    f, sep=sep, index_col=0,
                    low_memory=False,
                    nrows=5
                )
            log(f"  Shape (5 rows): {df.shape}")
            log(f"  Columns (first 5): "
                f"{list(df.columns[:5])}")
            log(f"  Index (first 5): "
                f"{list(df.index[:5])}")

            # Check if index looks like probe IDs
            # or gene symbols
            sample_idx = str(df.index[0]).strip()
            looks_like_probe = (
                sample_idx.upper().startswith("ILMN")
                or sample_idx.upper().startswith("A_")
                or sample_idx.upper().startswith("TC_")
                or sample_idx.replace(".", "").isdigit()
            )

            # Load full matrix
            with gzip.open(local_path, "rt",
                           errors="ignore") as f:
                df_full = pd.read_csv(
                    f, sep=sep, index_col=0,
                    low_memory=False
                )
            log(f"  Full shape: {df_full.shape}")
            return df_full

        # plain text
        elif flower.endswith(".txt"):
            df_full = pd.read_csv(
                local_path, sep="\t", index_col=0,
                low_memory=False
            )
            log(f"  Full shape: {df_full.shape}")
            return df_full

    except Exception as e:
        log(f"  Load error: {e}")
        return None

    return None


def try_series_matrix(accession):
    """
    Fall back to GEO Series Matrix file.
    Contains processed values and is always available.
    """
    log(f"\n  Fetching GEO Series Matrix...")
    url = (
        "https://ftp.ncbi.nlm.nih.gov/geo/"
        f"series/{accession[:6]}nnn/{accession}/"
        f"matrix/{accession}_series_matrix.txt.gz"
    )
    log(f"  URL: {url}")

    local = os.path.join(
        BASE_DIR, f"{accession}_series_matrix.txt.gz"
    )
    if not os.path.exists(local):
        raw = fetch_url(url, timeout=120)
        if raw is None:
            log("  Series matrix fetch failed.")
            return None
        with open(local, "wb") as f:
            f.write(raw)
        log(f"  Downloaded: {len(raw)/1e6:.1f} MB")

    log("  Parsing series matrix...")
    expr_rows = {}
    sample_ids = []

    try:
        with gzip.open(local, "rt",
                       errors="ignore") as f:
            for line in f:
                line = line.rstrip()
                if line.startswith("!Sample_geo_accession"):
                    sample_ids = (
                        line.split("\t")[1:]
                    )
                elif line.startswith(
                    "!series_matrix_table_begin"
                ):
                    # Next line is header
                    header = f.readline().rstrip()
                    cols   = header.split("\t")[1:]
                    for data_line in f:
                        data_line = data_line.rstrip()
                        if "series_matrix_table_end" in data_line:
                            break
                        parts = data_line.split("\t")
                        if len(parts) < 2:
                            continue
                        probe_id = parts[0].strip('"')
                        try:
                            vals = [
                                float(v.strip('"'))
                                for v in parts[1:]
                            ]
                            expr_rows[probe_id] = vals
                        except ValueError:
                            pass
                    break

        if not expr_rows:
            log("  No expression data found in series matrix.")
            return None

        col_ids = cols if cols else sample_ids
        df = pd.DataFrame.from_dict(
            expr_rows, orient="index",
            columns=col_ids[:len(
                list(expr_rows.values())[0]
            )]
        )
        log(f"  Series matrix shape: {df.shape}")
        return df

    except Exception as e:
        log(f"  Series matrix parse error: {e}")
        return None

# ============================================================
# STEP 4: NORMALIZE
# Log2 transform and quantile normalize if needed.
# ============================================================

def normalize_matrix(df):
    log("")
    log("=" * 65)
    log("STEP 4: NORMALIZATION")
    log("=" * 65)

    # Separate expression from p-value columns
    # (Illumina arrays include Detection.Pval columns)
    expr_cols = [
        c for c in df.columns
        if ("detection" not in str(c).lower()
            and "pval" not in str(c).lower()
            and "p_value" not in str(c).lower())
    ]
    pval_cols = [
        c for c in df.columns
        if ("detection" in str(c).lower()
            or "pval" in str(c).lower()
            or "p_value" in str(c).lower())
    ]

    log(f"  Expression cols : {len(expr_cols)}")
    log(f"  Pval/detect cols: {len(pval_cols)}")

    expr_df = df[expr_cols].copy()
    expr_df = expr_df.apply(
        pd.to_numeric, errors="coerce"
    )
    expr_df = expr_df.dropna(how="all")

    log(f"  Shape after numeric: {expr_df.shape}")

    # Detection filter for Illumina
    if pval_cols:
        pval_df = df[pval_cols].apply(
            pd.to_numeric, errors="coerce"
        )
        detected = (pval_df < 0.05).sum(axis=1)
        min_det  = max(3, int(len(pval_cols) * 0.20))
        mask     = detected >= min_det
        expr_df  = expr_df[mask]
        log(f"  After detection filter: "
            f"{mask.sum()} rows")

    # Check if already log2 transformed
    sample_vals = expr_df.values.flatten()
    sample_vals = sample_vals[~np.isnan(sample_vals)]
    sample_vals = sample_vals[sample_vals > 0][:10000]
    median_val  = np.median(sample_vals)

    already_log2 = median_val < 30

    log(f"  Median value: {median_val:.2f}")
    log(f"  Already log2: {already_log2}")

    if not already_log2:
        expr_df = expr_df.clip(lower=1.0)
        expr_df = np.log2(expr_df)
        log("  Applied log2 transform")

    # Quantile normalize
    log("  Quantile normalizing...")
    arr      = expr_df.values.copy()
    nan_mask = np.isnan(arr)
    arr[nan_mask] = 0.0

    sort_arr = np.sort(arr, axis=0)
    mean_ref = sort_arr.mean(axis=1)
    rank_idx = np.argsort(
        np.argsort(arr, axis=0), axis=0
    )
    norm_arr = mean_ref[rank_idx]
    norm_arr[nan_mask] = np.nan

    expr_df = pd.DataFrame(
        norm_arr,
        index=expr_df.index,
        columns=expr_df.columns,
    )
    log(f"  Final shape: {expr_df.shape}")
    return expr_df

# ============================================================
# STEP 5: MAP PROBE IDs TO GENE SYMBOLS
# If the index is already gene symbols — skip.
# If probe IDs — fetch annotation from GEO.
# ============================================================

def map_to_genes(expr_df, series_info, accession):
    log("")
    log("=" * 65)
    log("STEP 5: GENE MAPPING")
    log("=" * 65)

    # Check if index already looks like gene symbols
    sample_probes = [str(x) for x in expr_df.index[:20]]
    probe_like = sum(
        1 for p in sample_probes
        if (
            p.upper().startswith("ILMN_")
            or p.upper().startswith("A_")
            or p.replace(".", "").isdigit()
            or p.upper().startswith("TC_")
            or p.upper().startswith("GN_")
        )
    )

    log(f"  Sample index values: {sample_probes[:5]}")
    log(f"  Probe-like count (of 20): {probe_like}")

    if probe_like < 5:
        log("  Index appears to be gene symbols. "
            "No mapping needed.")
        # Deduplicate by keeping highest-mean row
        expr_df["_mean"] = expr_df.mean(axis=1)
        expr_df = expr_df.sort_values(
            "_mean", ascending=False
        )
        expr_df = expr_df[~expr_df.index.duplicated(
            keep="first"
        )]
        expr_df = expr_df.drop(columns=["_mean"])
        log(f"  After dedup: {expr_df.shape}")
        return expr_df

    # Need to map probes — fetch platform annotation
    # Determine platform from series info
    platform = fetch_platform_id(accession)
    if platform:
        mapped = map_via_geo_platform(
            expr_df, platform
        )
        if mapped is not None and len(mapped) > 50:
            return mapped

    log("  Could not map probes to gene symbols.")
    log("  Returning probe IDs as row names.")
    log("  Drug target analysis will use probe IDs.")
    return expr_df


def fetch_platform_id(accession):
    url = (
        "https://www.ncbi.nlm.nih.gov/geo/"
        f"query/acc.cgi?acc={accession}"
        "&targ=self&form=text&view=quick"
    )
    raw = fetch_url(url)
    if raw is None:
        return None
    text = raw.decode("utf-8", errors="ignore")
    for line in text.split("\n"):
        if line.startswith("!Series_platform_id"):
            return line.split("=", 1)[1].strip()
    return None


def map_via_geo_platform(expr_df, platform):
    log(f"  Fetching platform annotation: {platform}")
    url = (
        "https://www.ncbi.nlm.nih.gov/geo/"
        f"query/acc.cgi?acc={platform}"
        "&targ=self&form=text&view=brief"
    )
    raw = fetch_url(url, timeout=30)
    if raw is None:
        return None

    text      = raw.decode("utf-8", errors="ignore")
    in_table  = False
    col_names = None
    id_col    = None
    sym_col   = None
    probe_map = {}

    for line in text.split("\n"):
        line = line.rstrip()
        if "platform_table_begin" in line:
            in_table  = True
            col_names = None
            continue
        if "platform_table_end" in line:
            break
        if not in_table:
            continue
        parts = line.split("\t")
        if col_names is None:
            col_names = parts
            for i, c in enumerate(col_names):
                cl = c.lower().strip()
                if cl == "id":
                    id_col = i
                if cl in [
                    "gene_symbol", "symbol",
                    "gene symbol", "ilmn_gene",
                    "gene_name", "gene",
                ]:
                    sym_col = i
            log(f"  Platform cols: {col_names[:6]}")
            log(f"  id_col={id_col} sym_col={sym_col}")
            continue

        if (id_col is not None
                and sym_col is not None
                and len(parts) > max(id_col, sym_col)):
            probe = parts[id_col].strip()
            sym   = parts[sym_col].strip()
            if (probe and sym
                    and sym not in ["", "---", "NA"]
                    and "///" not in sym):
                probe_map[probe] = sym.split(" ")[0]

    log(f"  Probe map entries: {len(probe_map)}")

    if len(probe_map) < 100:
        log("  Too few mappings. Skipping.")
        return None

    probe_ids = set(expr_df.index)
    matched   = {
        p: g for p, g in probe_map.items()
        if p in probe_ids
    }
    log(f"  Matched probes: {len(matched)}")

    if len(matched) < 50:
        log("  Too few matched. Returning raw.")
        return None

    sub = expr_df.loc[
        [p for p in matched if p in expr_df.index]
    ].copy()
    sub["_symbol"]  = [matched[p] for p in sub.index]
    sub["_mean"]    = sub.drop(
        columns=["_symbol"]
    ).mean(axis=1)
    sub = sub.sort_values("_mean", ascending=False)
    sub = sub.drop_duplicates(
        subset=["_symbol"], keep="first"
    )
    symbols = sub["_symbol"].values
    sub     = sub.drop(columns=["_symbol", "_mean"])
    sub.index = symbols

    log(f"  Mapped gene matrix: {sub.shape}")
    return sub

# ============================================================
# STEP 6: MERGE EXPRESSION WITH METADATA
# Match sample IDs in expression columns to
# sample GSM IDs in metadata.
# ============================================================

def merge_expression_metadata(expr_df, meta_df):
    log("")
    log("=" * 65)
    log("STEP 6: MERGE EXPRESSION + METADATA")
    log("=" * 65)

    log(f"  Expression columns: {len(expr_df.columns)}")
    log(f"  Metadata samples  : {len(meta_df)}")
    log(f"  Expr col sample   : "
        f"{list(expr_df.columns[:5])}")

    # Transpose so samples are rows
    expr_T = expr_df.T
    expr_T.index.name = "sample_key"

    # Try to match by GSM ID
    meta_copy = meta_df.copy()
    if "gsm" in meta_copy.columns:
        meta_copy = meta_copy.set_index("gsm")

    # Direct join attempt
    overlap = set(expr_T.index) & set(meta_copy.index)
    log(f"  Direct GSM overlap: {len(overlap)}")

    if len(overlap) > 0:
        merged = expr_T.join(
            meta_copy[["group"]],
            how="left"
        )
    else:
        # Samples in matrix may not be GSM IDs
        # Try matching by column order
        log("  No direct overlap. "
            "Trying order-based assignment.")
        if len(expr_T) == len(meta_copy):
            meta_ordered = meta_copy.reset_index()
            merged = expr_T.copy()
            merged["group"] = (
                meta_ordered["group"].values
            )
        else:
            log("  WARNING: Cannot match samples.")
            log("  Proceeding with UNKNOWN group.")
            merged = expr_T.copy()
            merged["group"] = "UNKNOWN"

    n_t = (merged.get("group") == "TUMOR").sum()
    n_n = (merged.get("group") == "NORMAL").sum()
    n_u = (
        (merged.get("group") == "UNKNOWN").sum()
        if "group" in merged.columns else len(merged)
    )

    log(f"  TUMOR  : {n_t}")
    log(f"  NORMAL : {n_n}")
    log(f"  UNKNOWN: {n_u}")

    return merged

# ============================================================
# STEP 7: BLIND SADDLE POINT SCAN
# No pre-loaded gene panels.
# Every gene gets tested.
# Results ranked by effect size and significance.
# ============================================================

def blind_saddle_point_scan(merged):
    log("")
    log("=" * 65)
    log("STEP 7: BLIND SADDLE POINT SCAN")
    log("All genes. No pre-selected panels.")
    log("Tumor vs Normal. Geometry reveals itself.")
    log("=" * 65)

    tumor  = merged[merged["group"] == "TUMOR"]
    normal = merged[merged["group"] == "NORMAL"]

    log(f"  TUMOR  : {len(tumor)}")
    log(f"  NORMAL : {len(normal)}")

    if len(tumor) < MIN_TUMOR:
        log(f"  ERROR: Insufficient tumor samples.")
        return None, tumor, normal

    if len(normal) < MIN_NORMAL:
        log(f"  ERROR: Insufficient normal samples.")
        return None, tumor, normal

    gene_cols = [
        c for c in merged.columns
        if c not in [
            "group", "gsm", "title", "source",
            "_combined",
        ]
        and str(c) not in [
            "disease_stage", "gleason_pattern_group",
            "sample_type", "tissue",
        ]
    ]

    log(f"  Genes to test: {len(gene_cols)}")
    log("  Running Mann-Whitney U for each gene...")

    results = []
    n_tested = 0

    for gene in gene_cols:
        try:
            nv = normal[gene].dropna().values
            tv = tumor[gene].dropna().values
            if len(nv) < MIN_NORMAL or len(tv) < MIN_TUMOR:
                continue

            nm  = nv.mean()
            tm  = tv.mean()
            chg = (
                (tm - nm) / abs(nm) * 100
                if abs(nm) > 0.0001 else np.nan
            )

            _, p_down = stats.mannwhitneyu(
                nv, tv, alternative="greater"
            )
            _, p_up   = stats.mannwhitneyu(
                tv, nv, alternative="greater"
            )
            p_use     = min(p_down, p_up)
            direction = (
                "DOWN" if tm < nm else "UP"
            )

            results.append({
                "gene":        str(gene),
                "normal_mean": nm,
                "tumor_mean":  tm,
                "change_pct":  chg,
                "direction":   direction,
                "p_value":     p_use,
                "abs_change":  abs(chg)
                    if not np.isnan(chg) else 0,
            })
            n_tested += 1

        except Exception:
            pass

    log(f"  Genes tested: {n_tested}")

    rdf = pd.DataFrame(results)
    if len(rdf) == 0:
        log("  ERROR: No genes tested successfully.")
        return None, tumor, normal

    rdf = rdf.sort_values(
        "abs_change", ascending=False
    )
    rdf.to_csv(
        os.path.join(RESULTS_DIR, "saddle_scan.csv"),
        index=False
    )
    log(f"  Saved: saddle_scan.csv")

    # Report top 30 suppressed and top 30 elevated
    sig_down = rdf[
        (rdf["direction"] == "DOWN")
        & (rdf["p_value"] < 0.05)
    ].head(30)

    sig_up = rdf[
        (rdf["direction"] == "UP")
        & (rdf["p_value"] < 0.05)
    ].head(30)

    def fmt_p(p):
        if p < 1e-300:  return "p=0.00e+00 ***"
        elif p < 0.001: return f"p={p:.2e} ***"
        elif p < 0.01:  return f"p={p:.2e}  **"
        elif p < 0.05:  return f"p={p:.4f}   *"
        else:           return f"p={p:.4f}  ns"

    log(f"\n  {'='*65}")
    log(f"  TOP SUPPRESSED IN TUMOR (switch gene candidates)")
    log(f"  {'='*65}")
    log(f"  {'Gene':<20} {'Normal':>9} {'Tumor':>9} "
        f"{'Change':>9} {'p-value':>16}")
    log(f"  {'-'*68}")
    for _, row in sig_down.iterrows():
        log(
            f"  {row['gene']:<20} "
            f"{row['normal_mean']:>9.4f} "
            f"{row['tumor_mean']:>9.4f} "
            f"{row['change_pct']:>+8.1f}%  "
            f"{fmt_p(row['p_value']):>16}"
        )

    log(f"\n  {'='*65}")
    log(f"  TOP ELEVATED IN TUMOR (FA marker candidates)")
    log(f"  {'='*65}")
    log(f"  {'Gene':<20} {'Normal':>9} {'Tumor':>9} "
        f"{'Change':>9} {'p-value':>16}")
    log(f"  {'-'*68}")
    for _, row in sig_up.iterrows():
        log(
            f"  {row['gene']:<20} "
            f"{row['normal_mean']:>9.4f} "
            f"{row['tumor_mean']:>9.4f} "
            f"{row['change_pct']:>+8.1f}%  "
            f"{fmt_p(row['p_value']):>16}"
        )

    return rdf, tumor, normal

# ============================================================
# STEP 8: BLIND DEPTH SCORE
# Use top N suppressed + top N elevated genes.
# No pre-loaded panels.
# The geometry defines the score.
# ============================================================

def blind_depth_score(merged, rdf, tumor):
    log("")
    log("=" * 65)
    log("STEP 8: BLIND DEPTH SCORE")
    log(f"Top {N_TOP_GENES} suppressed + "
        f"top {N_TOP_GENES} elevated.")
    log("Geometry-derived. No pre-loaded panels.")
    log("=" * 65)

    sig_down = rdf[
        (rdf["direction"] == "DOWN")
        & (rdf["p_value"] < 0.05)
    ].head(N_TOP_GENES)

    sig_up = rdf[
        (rdf["direction"] == "UP")
        & (rdf["p_value"] < 0.05)
    ].head(N_TOP_GENES)

    down_genes = [
        g for g in sig_down["gene"].values
        if g in tumor.columns
    ]
    up_genes = [
        g for g in sig_up["gene"].values
        if g in tumor.columns
    ]

    log(f"  Switch candidates used : {len(down_genes)}")
    log(f"  FA candidates used     : {len(up_genes)}")

    if not down_genes and not up_genes:
        log("  ERROR: No genes available for scoring.")
        return tumor

    def norm01(s):
        mn, mx = s.min(), s.max()
        if mx > mn:
            return (s - mn) / (mx - mn)
        return pd.Series(0.5, index=s.index)

    tumor  = tumor.copy()
    depth  = pd.Series(
        np.zeros(len(tumor)), index=tumor.index
    )
    comp   = 0

    if down_genes:
        sw_m    = tumor[down_genes].mean(axis=1)
        depth  += (1 - norm01(sw_m))
        comp   += 1
        log(f"  Component 1: switch suppression "
            f"({len(down_genes)} genes)")

    if up_genes:
        fa_m    = tumor[up_genes].mean(axis=1)
        depth  += norm01(fa_m)
        comp   += 1
        log(f"  Component 2: FA elevation "
            f"({len(up_genes)} genes)")

    if comp > 0:
        depth /= comp

    tumor["block_depth"] = depth.values

    log(f"\n  Block depth ({len(tumor)} tumors):")
    log(f"    Mean  : {depth.mean():.4f}")
    log(f"    Median: {depth.median():.4f}")
    log(f"    Std   : {depth.std():.4f}")
    log(f"    Min   : {depth.min():.4f}")
    log(f"    Max   : {depth.max():.4f}")

    # Depth correlations — across all genes
    log(f"\n  Top depth correlations (all genes):")
    log(f"  {'Gene':<20} {'r':>8}  p-value")
    log(f"  {'-'*44}")

    gene_cols = [
        c for c in tumor.columns
        if c not in [
            "block_depth", "group", "_combined",
            "gsm", "title", "source",
        ]
    ]
    corrs = []
    for gene in gene_cols:
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
    for gene, rv, pv in corrs[:30]:
        log(f"  {gene:<20} {rv:>+8.4f}  p={pv:.2e}")

    # Save depth correlation table
    corr_df = pd.DataFrame(
        corrs, columns=["gene", "r", "p_value"]
    )
    corr_df.to_csv(
        os.path.join(RESULTS_DIR, "depth_correlations.csv"),
        index=False
    )
    log(f"\n  Saved: depth_correlations.csv")

    tumor.to_csv(
        os.path.join(RESULTS_DIR, "tumor_with_depth.csv")
    )
    log(f"  Saved: tumor_with_depth.csv")

    return tumor, corrs

# ============================================================
# STEP 9: FIGURE — BLIND ATTRACTOR LANDSCAPE
# Shows the geometry without naming it.
# The analyst names it after reading the output.
# ============================================================

def generate_landscape_figure(
    tumor, normal, rdf, corrs, accession
):
    log("")
    log("--- Generating landscape figure ---")

    fig = plt.figure(figsize=(24, 18))
    fig.suptitle(
        f"OrganismCore — Blind False Attractor Scan\n"
        f"Accession: {accession} | "
        f"Tumor: {len(tumor)} | "
        f"Normal: {len(normal)}\n"
        f"Geometry-first. No pre-loaded panels.",
        fontsize=11, fontweight="bold", y=0.99,
    )
    gs = gridspec.GridSpec(
        3, 3, figure=fig,
        hspace=0.52, wspace=0.42,
    )

    clr = {
        "normal": "#2980b9",
        "tumor":  "#c0392b",
        "down":   "#c0392b",
        "up":     "#27ae60",
    }

    # A — Top suppressed (switch candidates)
    ax_a = fig.add_subplot(gs[0, 0])
    top_down = rdf[
        rdf["direction"] == "DOWN"
    ].head(15)
    if len(top_down) > 0:
        genes   = top_down["gene"].values
        nm_vals = top_down["normal_mean"].values
        tm_vals = top_down["tumor_mean"].values
        x       = np.arange(len(genes))
        w       = 0.35
        ax_a.bar(
            x - w/2, nm_vals, w,
            color=clr["normal"],
            label="Normal", alpha=0.85,
        )
        ax_a.bar(
            x + w/2, tm_vals, w,
            color=clr["tumor"],
            label="Tumor", alpha=0.85,
        )
        ax_a.set_xticks(x)
        ax_a.set_xticklabels(
            genes, rotation=45,
            ha="right", fontsize=6,
        )
        ax_a.set_title(
            "A — Top Suppressed\n"
            "(Switch gene candidates)",
            fontsize=9,
        )
        ax_a.legend(fontsize=7)
        ax_a.set_ylabel("Expression", fontsize=8)

    # B — Top elevated (FA marker candidates)
    ax_b = fig.add_subplot(gs[0, 1])
    top_up = rdf[rdf["direction"] == "UP"].head(15)
    if len(top_up) > 0:
        genes   = top_up["gene"].values
        nm_vals = top_up["normal_mean"].values
        tm_vals = top_up["tumor_mean"].values
        x       = np.arange(len(genes))
        w       = 0.35
        ax_b.bar(
            x - w/2, nm_vals, w,
            color=clr["normal"],
            label="Normal", alpha=0.85,
        )
        ax_b.bar(
            x + w/2, tm_vals, w,
            color=clr["tumor"],
            label="Tumor", alpha=0.85,
        )
        ax_b.set_xticks(x)
        ax_b.set_xticklabels(
            genes, rotation=45,
            ha="right", fontsize=6,
        )
        ax_b.set_title(
            "B — Top Elevated\n"
            "(FA marker candidates)",
            fontsize=9,
        )
        ax_b.legend(fontsize=7)
        ax_b.set_ylabel("Expression", fontsize=8)

    # C — Waterfall (all significant genes)
    ax_c = fig.add_subplot(gs[0, 2])
    sig = rdf[rdf["p_value"] < 0.05].copy()
    sig = sig.sort_values("change_pct")
    if len(sig) > 0:
        # Show top 40 movers
        n_each = 20
        show   = pd.concat([
            sig.head(n_each),
            sig.tail(n_each),
        ]).drop_duplicates()
        bc = [
            clr["down"] if v < 0 else clr["up"]
            for v in show["change_pct"]
        ]
        ax_c.barh(
            show["gene"],
            show["change_pct"],
            color=bc,
        )
        ax_c.axvline(
            0, color="black", linewidth=0.8
        )
        ax_c.set_xlabel(
            "% change vs normal", fontsize=8
        )
        ax_c.set_title(
            f"C — Waterfall\nTop {len(show)} movers",
            fontsize=9,
        )
        ax_c.tick_params(axis="y", labelsize=5)

    # D — Depth distribution
    ax_d = fig.add_subplot(gs[1, 0])
    if "block_depth" in tumor.columns:
        ax_d.hist(
            tumor["block_depth"].values,
            bins=20,
            color=clr["tumor"],
            alpha=0.7,
            edgecolor="white",
        )
        ax_d.axvline(
            tumor["block_depth"].mean(),
            color="black",
            linewidth=1.5,
            linestyle="--",
            label=f"mean={tumor['block_depth'].mean():.3f}",
        )
        ax_d.set_xlabel(
            "Block Depth Score", fontsize=8
        )
        ax_d.set_ylabel("Count", fontsize=8)
        ax_d.set_title(
            "D — Depth Distribution\n"
            "Blind score from top movers",
            fontsize=9,
        )
        ax_d.legend(fontsize=7)

    # E — Top depth correlations
    ax_e = fig.add_subplot(gs[1, 1])
    if corrs:
        top_corrs = corrs[:25]
        gc = [c[0] for c in top_corrs]
        vc = [c[1] for c in top_corrs]
        cc = [
            clr["down"] if v < 0 else clr["up"]
            for v in vc
        ]
        ax_e.barh(gc, vc, color=cc)
        ax_e.axvline(
            0, color="black", linewidth=0.8
        )
        ax_e.set_xlabel(
            "r with depth score", fontsize=8
        )
        ax_e.set_title(
            "E — Depth Correlations\nTop 25",
            fontsize=9,
        )
        ax_e.tick_params(axis="y", labelsize=6)

    # F — Summary statistics
    ax_f = fig.add_subplot(gs[1, 2])
    ax_f.axis("off")
    n_sig   = (rdf["p_value"] < 0.05).sum()
    n_down  = (
        (rdf["direction"] == "DOWN")
        & (rdf["p_value"] < 0.05)
    ).sum()
    n_up    = (
        (rdf["direction"] == "UP")
        & (rdf["p_value"] < 0.05)
    ).sum()
    summary = (
        f"F — DISCOVERY SUMMARY\n"
        f"─────────────────────────\n"
        f"Accession : {accession}\n"
        f"Tumor     : {len(tumor)}\n"
        f"Normal    : {len(normal)}\n\n"
        f"Genes tested  : {len(rdf)}\n"
        f"Sig (p<0.05)  : {n_sig}\n"
        f"  Suppressed  : {n_down}\n"
        f"  Elevated    : {n_up}\n\n"
        f"Depth score:\n"
        f"  Mean   : "
        f"{tumor['block_depth'].mean():.4f}\n"
        f"  Std    : "
        f"{tumor['block_depth'].std():.4f}\n\n"
        f"Top suppressed (switch candidates):\n"
    )
    for g in rdf[rdf["direction"]=="DOWN"].head(5)["gene"]:
        summary += f"  {g}\n"
    summary += "\nTop elevated (FA candidates):\n"
    for g in rdf[rdf["direction"]=="UP"].head(5)["gene"]:
        summary += f"  {g}\n"
    summary += (
        f"\nFramework: OrganismCore\n"
        f"Date: 2026-03-03\n"
        f"The geometry revealed itself.\n"
        f"Analyst names it next."
    )
    ax_f.text(
        0.03, 0.97, summary,
        transform=ax_f.transAxes,
        fontsize=8,
        verticalalignment="top",
        fontfamily="monospace",
        bbox=dict(
            boxstyle="round",
            facecolor="#f8f8f8",
            edgecolor="#cccccc",
        ),
    )

    # G — Scatter: depth vs top elevated gene
    ax_g = fig.add_subplot(gs[2, 0])
    if (corrs and "block_depth" in tumor.columns):
        # Top positive correlator
        pos_corrs = [
            (g, r, p) for g, r, p in corrs if r > 0
        ]
        if pos_corrs:
            top_gene = pos_corrs[0][0]
            if top_gene in tumor.columns:
                ax_g.scatter(
                    tumor[top_gene].values,
                    tumor["block_depth"].values,
                    color=clr["tumor"],
                    alpha=0.6, s=20,
                )
                ax_g.set_xlabel(
                    f"{top_gene} expression",
                    fontsize=8,
                )
                ax_g.set_ylabel(
                    "Block Depth", fontsize=8
                )
                ax_g.set_title(
                    f"G — Depth vs {top_gene}\n"
                    f"r={pos_corrs[0][1]:.3f}",
                    fontsize=9,
                )

    # H — Scatter: depth vs top suppressed gene
    ax_h = fig.add_subplot(gs[2, 1])
    if (corrs and "block_depth" in tumor.columns):
        neg_corrs = [
            (g, r, p) for g, r, p in corrs if r < 0
        ]
        if neg_corrs:
            top_gene = neg_corrs[0][0]
            if top_gene in tumor.columns:
                ax_h.scatter(
                    tumor[top_gene].values,
                    tumor["block_depth"].values,
                    color=clr["down"],
                    alpha=0.6, s=20,
                )
                ax_h.set_xlabel(
                    f"{top_gene} expression",
                    fontsize=8,
                )
                ax_h.set_ylabel(
                    "Block Depth", fontsize=8
                )
                ax_h.set_title(
                    f"H — Depth vs {top_gene}\n"
                    f"r={neg_corrs[0][1]:.3f}",
                    fontsize=9,
                )

    # I — p-value distribution
    ax_i = fig.add_subplot(gs[2, 2])
    ax_i.hist(
        rdf["p_value"].values,
        bins=50,
        color="#95a5a6",
        edgecolor="white",
    )
    ax_i.axvline(
        0.05, color="red",
        linewidth=1, linestyle="--",
        label="p=0.05",
    )
    ax_i.set_xlabel("p-value", fontsize=8)
    ax_i.set_ylabel("Count", fontsize=8)
    ax_i.set_title(
        "I — p-value Distribution\n"
        "Left enrichment = real signal",
        fontsize=9,
    )
    ax_i.legend(fontsize=7)

    outpath = os.path.join(
        RESULTS_DIR,
        f"{accession}_attractor_landscape.png"
    )
    plt.savefig(
        outpath, dpi=150, bbox_inches="tight"
    )
    log(f"\n  Figure saved: {outpath}")
    plt.close()

# ============================================================
# MAIN
# ============================================================

def main():
    log("=" * 65)
    log("OrganismCore — Universal False Attractor Discovery")
    log("SCRIPT 1 — BLIND GEOMETRIC LANDSCAPE SCAN")
    log(f"Accession : {GEO_ACCESSION}")
    log(f"N_TOP_GENES: {N_TOP_GENES}")
    log("=" * 65)
    log("")
    log("The geometry reveals itself.")
    log("No pre-loaded cancer-specific assumptions.")
    log("The analyst names what they see after.")
    log("")

    # Step 0: Series info
    series_info = fetch_series_info(GEO_ACCESSION)

    # Step 1: Sample metadata
    meta_df = fetch_sample_metadata(GEO_ACCESSION)
    if len(meta_df) == 0:
        log("FATAL: No metadata. Cannot proceed.")
        write_log()
        return

    # Step 2: Classify tumor vs normal
    meta_df = classify_samples(meta_df)

    # Step 3: Download expression matrix
    expr_df = find_expression_matrix(
        series_info, GEO_ACCESSION
    )
    if expr_df is None:
        log("FATAL: Could not load expression matrix.")
        write_log()
        return

    # Step 4: Normalize
    expr_df = normalize_matrix(expr_df)

    # Step 5: Map to gene symbols
    expr_df = map_to_genes(
        expr_df, series_info, GEO_ACCESSION
    )

    # Step 6: Merge expression + metadata
    merged = merge_expression_metadata(
        expr_df, meta_df
    )

    # Step 7: Blind saddle point scan
    result = blind_saddle_point_scan(merged)
    if result[0] is None:
        log("FATAL: Saddle point scan failed.")
        write_log()
        return
    rdf, tumor, normal = result

    # Step 8: Blind depth score + correlations
    result2 = blind_depth_score(merged, rdf, tumor)
    tumor, corrs = result2

    # Step 9: Figure
    generate_landscape_figure(
        tumor, normal, rdf, corrs, GEO_ACCESSION
    )

    # Save full results
    write_log()
    log(f"\n  Outputs in: {RESULTS_DIR}")
    log(f"  Log: {LOG_FILE}")
    log("")
    log("=" * 65)
    log("SCRIPT 1 COMPLETE")
    log("")
    log("The landscape has been revealed.")
    log("Now read the output.")
    log("Top suppressed = switch gene candidates.")
    log("Top elevated   = FA marker candidates.")
    log("Depth correlations = convergence node hints.")
    log("")
    log("Write your Phase 1 document now.")
    log("Name what you see in the geometry.")
    log("Then run Script 2 with that knowledge.")
    log("=" * 65)


if __name__ == "__main__":
    main()
```
