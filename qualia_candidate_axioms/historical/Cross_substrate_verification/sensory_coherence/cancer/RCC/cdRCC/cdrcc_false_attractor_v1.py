"""
cdRCC — Collecting Duct Renal Cell Carcinoma
FALSE ATTRACTOR DISCOVERY — SCRIPT 1
OrganismCore Cancer Validation

Dataset:   GSE89122
           7 CDC tumours
           6 matched adjacent normals
           Illumina HiSeq 2000
           RNA-seq  GRCh38.p13
           6 matched pairs + 1 tumour-only (CDC5)

Phase 0 established:
  - Dataset confirmed PASS: GSE89122
  - Sample map confirmed: 13/13 samples matched
  - No series-level matrix available on GEO
  - Expression data lives in per-GSM supplementary
    files (individual raw count files per sample)
  - Structure check v2 confirmed RNA-seq platform
    and GRCh38 genome

This script:
  1. Downloads per-GSM count files
  2. Merges into a single counts matrix
  3. Normalises to log2(CPM + 1)
  4. Runs a blind full-genome saddle point scan
     NO pre-loaded gene panels
     NO prior knowledge of the attractor
  5. Computes a geometry-derived blind depth score
  6. Runs depth correlations across all genes
  7. Outputs figure, CSV, and full log

The geometry reveals itself.
The analyst reads the output and writes Phase 1.
Predictions are locked AFTER this script runs —
not before.

Author:    Eric Robert Lawson
Framework: OrganismCore
Protocol:  Phase 2 — Script 1 Discovery Run
Document:  Doc 89a (to be written after output)
Date:      2026-03-03
"""

import os
import sys
import gzip
import re
import urllib.request
import urllib.parse
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
# CONFIGURATION
# ============================================================

ACC         = "GSE89122"
BASE_DIR    = "./cdrcc_false_attractor/"
RESULTS_DIR = os.path.join(BASE_DIR, "results")
LOG_FILE    = os.path.join(RESULTS_DIR, "analysis_log.txt")

os.makedirs(BASE_DIR,    exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# Minimum mean CPM across all samples to keep a gene
# Filters out unexpressed genes before scan
MIN_CPM_MEAN = 0.5

# Number of top movers to use for blind depth score
N_TOP_GENES = 50

# ============================================================
# CONFIRMED SAMPLE MAP
# Established in Phase 0 / structure check
# Locked. Do not modify.
# patient_id, sample_type
# ============================================================

SAMPLE_MAP = {
    "GSM2359144": ("CDC1", "tumor"),
    "GSM2359145": ("CDC1", "normal"),
    "GSM2359146": ("CDC2", "tumor"),
    "GSM2359147": ("CDC2", "normal"),
    "GSM2359148": ("CDC3", "tumor"),
    "GSM2359149": ("CDC3", "normal"),
    "GSM2359150": ("CDC4", "tumor"),
    "GSM2359151": ("CDC4", "normal"),
    "GSM2359152": ("CDC5", "tumor"),   # no matched normal
    "GSM2359153": ("CDC6", "tumor"),
    "GSM2359154": ("CDC6", "normal"),
    "GSM2359155": ("CDC7", "tumor"),
    "GSM2359156": ("CDC7", "normal"),
}

TUMOR_SAMPLES  = [
    gsm for gsm, (_, t) in SAMPLE_MAP.items()
    if t == "tumor"
]
NORMAL_SAMPLES = [
    gsm for gsm, (_, t) in SAMPLE_MAP.items()
    if t == "normal"
]

# ============================================================
# LOGGING
# ============================================================

log_lines = []

def log(msg=""):
    print(msg)
    log_lines.append(str(msg))

def write_log():
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines))

# ============================================================
# FETCH UTILITY
# ============================================================

def fetch_bytes(url, timeout=60, retries=3):
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
            time.sleep(3)
    return None

def download_file(url, local_path, label=""):
    if os.path.exists(local_path):
        sz = os.path.getsize(local_path)
        if sz > 200:
            log(f"  Cached: {label or os.path.basename(local_path)}"
                f" ({sz/1024:.1f} KB)")
            return True

    log(f"  Downloading: {label or url[-60:]}")
    raw = fetch_bytes(url, timeout=90)
    if raw is None:
        log(f"  FAILED: {url[-60:]}")
        return False
    with open(local_path, "wb") as f:
        f.write(raw)
    log(f"  OK: {len(raw)/1024:.1f} KB")
    return True

# ============================================================
# STEP 1: DISCOVER AND DOWNLOAD PER-GSM COUNT FILES
#
# GSE89122 does not have a series-level matrix.
# Each GSM has an individual supplementary count file.
# We fetch the GSM SOFT page to find the file name,
# then download from the GEO FTP.
# ============================================================

def get_gsm_suppl_filename(gsm):
    """
    Fetch the SOFT page for a GSM and extract
    the supplementary file name.
    Returns the filename string or None.
    """
    url = (
        "https://www.ncbi.nlm.nih.gov/geo/query/"
        f"acc.cgi?acc={gsm}"
        "&targ=self&form=text&view=brief"
    )
    raw = fetch_bytes(url, timeout=30)
    if raw is None:
        return None
    text = raw.decode("utf-8", errors="ignore")
    for line in text.split("\n"):
        if "!Sample_supplementary_file" in line:
            val = line.split("=", 1)[1].strip()
            fname = val.split("/")[-1].strip()
            if fname and fname.lower() != "none":
                return fname, val   # (filename, full_url)
    return None, None


def build_gsm_ftp_url(gsm, fname):
    """
    Build the NCBI FTP URL for a GSM supplementary file.
    GSM2359144 → GSM235nnn → GSM2359144/suppl/
    """
    gsm_digits = re.sub(r"\D", "", gsm)
    # Last 3 digits replaced with nnn
    prefix = gsm_digits[:-3] + "nnn"
    return (
        "https://ftp.ncbi.nlm.nih.gov/geo/"
        f"samples/GSM{prefix}/{gsm}/suppl/{fname}"
    )


def download_all_gsm_files():
    """
    Download per-GSM count files for all 13 samples.
    Returns dict: gsm → local_path
    """
    log("=" * 65)
    log("STEP 1: DOWNLOADING PER-GSM COUNT FILES")
    log(f"  {len(SAMPLE_MAP)} samples")
    log("=" * 65)

    gsm_paths = {}

    for gsm in SAMPLE_MAP:
        patient, stype = SAMPLE_MAP[gsm]
        log(f"\n  {gsm}  ({patient}  {stype})")

        # Check if already cached
        existing = [
            f for f in os.listdir(BASE_DIR)
            if f.startswith(gsm) and (
                f.endswith(".gz") or f.endswith(".txt")
                or f.endswith(".tsv")
            )
        ]
        if existing:
            local = os.path.join(BASE_DIR, existing[0])
            log(f"  Cached: {existing[0]}")
            gsm_paths[gsm] = local
            continue

        # Fetch file name from SOFT page
        fname, full_url = get_gsm_suppl_filename(gsm)
        time.sleep(0.5)

        if fname is None:
            log(f"  WARNING: No supplementary file found "
                f"for {gsm}")
            continue

        log(f"  File: {fname}")

        # Try SOFT-provided URL first
        local = os.path.join(BASE_DIR, fname)
        ok = False

        if full_url and full_url.startswith("http"):
            ok = download_file(full_url, local, fname)

        # Fallback to FTP construction
        if not ok:
            ftp_url = build_gsm_ftp_url(gsm, fname)
            log(f"  FTP fallback: {ftp_url}")
            ok = download_file(ftp_url, local, fname)

        # Fallback to HTTPS GEO download
        if not ok:
            alt_url = (
                "https://www.ncbi.nlm.nih.gov/geo/"
                "download/?acc=" + gsm +
                "&format=file&file=" +
                urllib.parse.quote(fname)
            )
            log(f"  HTTPS fallback: {alt_url[-80:]}")
            ok = download_file(alt_url, local, fname)

        if ok and os.path.exists(local):
            gsm_paths[gsm] = local
        else:
            log(f"  FAILED all attempts: {gsm}")

        time.sleep(0.5)

    log(f"\n  Downloaded: {len(gsm_paths)}/{len(SAMPLE_MAP)}")
    missing = set(SAMPLE_MAP) - set(gsm_paths)
    if missing:
        log(f"  Missing: {sorted(missing)}")

    return gsm_paths

# ============================================================
# STEP 2: LOAD AND MERGE COUNT FILES
#
# Each file is expected to be a two-column TSV:
#   gene_id    count
# (typical STAR / HTSeq / featureCounts output)
# Some may have a header line — detect and handle.
# Gene IDs may be Ensembl (ENSG...) or gene symbols.
# ============================================================

def load_count_file(path):
    """
    Load a single-sample count file.
    Returns Series: gene_id → count
    """
    try:
        opener = gzip.open if path.endswith(".gz") else open
        mode   = "rt" if path.endswith(".gz") else "r"

        with opener(path, mode, errors="ignore") as f:
            lines = f.readlines()

        # Detect header — first line may be a comment or header
        start = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped:
                continue
            # Skip comment lines
            if stripped.startswith("#"):
                start = i + 1
                continue
            # Skip header lines (non-numeric second field)
            parts = stripped.split("\t")
            if len(parts) >= 2:
                try:
                    float(parts[1])
                    start = i
                    break
                except ValueError:
                    start = i + 1
                    continue

        # Parse data lines
        records = {}
        for line in lines[start:]:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) < 2:
                continue
            gene_id = parts[0].strip().strip('"')
            try:
                count = float(parts[1].strip())
                records[gene_id] = count
            except ValueError:
                pass

        if not records:
            log(f"    WARNING: No records parsed from "
                f"{os.path.basename(path)}")
            return None

        return pd.Series(records, dtype=float,
                         name=os.path.basename(path))

    except Exception as e:
        log(f"    ERROR loading {os.path.basename(path)}: "
            f"{e}")
        return None


def merge_count_files(gsm_paths):
    """
    Load all GSM count files and merge into
    a single genes × samples DataFrame.
    Columns are GSM IDs.
    """
    log("")
    log("=" * 65)
    log("STEP 2: MERGING COUNT FILES")
    log("=" * 65)

    series_dict = {}
    for gsm, path in gsm_paths.items():
        patient, stype = SAMPLE_MAP[gsm]
        log(f"  Loading {gsm} ({patient} {stype})...")
        s = load_count_file(path)
        if s is not None:
            s.name = gsm
            series_dict[gsm] = s
            log(f"    {len(s)} genes, "
                f"total counts: {s.sum():.0f}")
        else:
            log(f"    FAILED to load {gsm}")

    if not series_dict:
        log("  FATAL: No count files loaded")
        return None

    counts = pd.DataFrame(series_dict)
    log(f"\n  Merged matrix: {counts.shape[0]} genes × "
        f"{counts.shape[1]} samples")
    log(f"  Samples in matrix: {list(counts.columns)}")

    # Check coverage
    n_loaded = len(series_dict)
    n_total  = len(SAMPLE_MAP)
    if n_loaded < n_total:
        missing = set(SAMPLE_MAP) - set(series_dict)
        log(f"  WARNING: {n_total - n_loaded} samples "
            f"missing: {sorted(missing)}")

    # Remove STAR/HTSeq summary lines (start with __)
    star_rows = counts.index[
        counts.index.astype(str).str.startswith("__")
        | counts.index.astype(str).str.startswith("N_")
    ]
    if len(star_rows) > 0:
        log(f"  Removing {len(star_rows)} summary rows: "
            f"{list(star_rows)}")
        counts = counts.drop(index=star_rows)

    log(f"  Final matrix: {counts.shape}")
    return counts

# ============================================================
# STEP 3: NORMALISE TO log2(CPM + 1)
#
# RNA-seq raw counts normalisation:
#   CPM = count / (library_size / 1e6)
#   log2(CPM + 1)
#
# Filter genes with mean CPM < MIN_CPM_MEAN
# ============================================================

def normalise_counts(counts):
    log("")
    log("=" * 65)
    log("STEP 3: NORMALISATION  log2(CPM + 1)")
    log("=" * 65)

    # Library sizes
    lib_sizes = counts.sum(axis=0)
    log("  Library sizes:")
    for gsm in counts.columns:
        patient, stype = SAMPLE_MAP.get(gsm, ("?", "?"))
        log(f"    {gsm} ({patient} {stype}): "
            f"{lib_sizes[gsm]:,.0f}")

    # CPM
    cpm = counts.divide(lib_sizes / 1e6, axis=1)

    # Filter low-expressed genes
    mean_cpm  = cpm.mean(axis=1)
    keep_mask = mean_cpm >= MIN_CPM_MEAN
    cpm_filt  = cpm[keep_mask]
    log(f"\n  Genes before filter: {len(cpm)}")
    log(f"  CPM >= {MIN_CPM_MEAN}: {keep_mask.sum()}")
    log(f"  Genes removed: {(~keep_mask).sum()}")

    # log2(CPM + 1)
    log2_cpm = np.log2(cpm_filt + 1)

    log(f"\n  log2(CPM+1) statistics:")
    flat = log2_cpm.values.flatten()
    log(f"    Min:    {flat.min():.4f}")
    log(f"    Max:    {flat.max():.4f}")
    log(f"    Mean:   {flat.mean():.4f}")
    log(f"    Median: {np.median(flat):.4f}")

    # Save normalised matrix
    out = os.path.join(RESULTS_DIR,
                       "GSE89122_log2cpm.csv")
    log2_cpm.to_csv(out)
    log(f"\n  Saved: {out}")

    return log2_cpm

# ============================================================
# STEP 4: HANDLE GENE IDs
#
# Gene IDs may be Ensembl (ENSG...) — check and map.
# If Ensembl: strip version suffix (ENSG00000xxx.y → ENSG...)
# We do NOT use a hard-coded map.
# We use the Ensembl ID directly as gene label unless
# a symbol map can be fetched from MyGene.info (API-free
# bulk approach using gene info file).
# ============================================================

def clean_gene_ids(log2_cpm):
    log("")
    log("=" * 65)
    log("STEP 4: GENE ID HANDLING")
    log("=" * 65)

    sample_ids = [str(x) for x in log2_cpm.index[:15]]
    log(f"  Sample gene IDs: {sample_ids}")

    is_ensembl = any(
        str(x).startswith("ENSG") for x in log2_cpm.index
    )
    is_symbol = not is_ensembl and not any(
        str(x).replace(".", "").isdigit()
        for x in log2_cpm.index[:10]
    )
    is_entrez = not is_ensembl and any(
        str(x).replace(".", "").isdigit()
        for x in log2_cpm.index[:10]
    )

    log(f"  Ensembl IDs: {is_ensembl}")
    log(f"  Gene symbols: {is_symbol}")
    log(f"  Entrez IDs: {is_entrez}")

    if is_ensembl:
        # Strip version suffix: ENSG00000123.4 → ENSG00000123
        new_index = [
            str(x).split(".")[0]
            for x in log2_cpm.index
        ]
        log2_cpm = log2_cpm.copy()
        log2_cpm.index = new_index
        log(f"  Stripped version suffixes.")
        log(f"  First 5 IDs: {log2_cpm.index[:5].tolist()}")

        # Attempt to map Ensembl → symbol using
        # NCBI gene2ensembl or Ensembl REST (no API key needed)
        log("")
        log("  Attempting Ensembl → symbol mapping...")
        log2_cpm = map_ensembl_to_symbol(log2_cpm)

    elif is_symbol:
        log("  Gene symbols — no mapping needed.")
        # Deduplicate: keep highest-mean row
        log2_cpm = dedup_by_mean(log2_cpm)

    elif is_entrez:
        log("  Entrez IDs — proceeding with Entrez IDs.")
        log("  Depth correlations will use Entrez IDs.")

    log(f"  Final gene count: {len(log2_cpm)}")
    return log2_cpm


def map_ensembl_to_symbol(df):
    """
    Map Ensembl IDs to gene symbols using
    Ensembl REST API (no API key, bulk POST).
    Falls back to Ensembl IDs if mapping fails.
    Returns DataFrame with symbol index.
    """
    ensembl_ids = df.index.tolist()
    log(f"  Mapping {len(ensembl_ids)} Ensembl IDs...")

    # Batch size for REST API
    batch_size = 1000
    symbol_map = {}

    for i in range(0, len(ensembl_ids), batch_size):
        batch = ensembl_ids[i : i + batch_size]
        batch_n = len(batch)
        log(f"  Batch {i//batch_size + 1}: "
            f"{batch_n} IDs...")

        try:
            import json
            payload = json.dumps(
                {"ids": batch}
            ).encode("utf-8")
            req = urllib.request.Request(
                "https://rest.ensembl.org/lookup/id",
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "Accept":       "application/json",
                    "User-Agent":   "Mozilla/5.0",
                },
                method="POST",
            )
            with urllib.request.urlopen(
                req, timeout=30
            ) as r:
                result = json.loads(
                    r.read().decode("utf-8")
                )
            for eid, info in result.items():
                if info and isinstance(info, dict):
                    sym = info.get(
                        "display_name",
                        info.get("id", eid)
                    )
                    if sym:
                        symbol_map[eid] = sym
            log(f"    Mapped: {len(symbol_map)} so far")
        except Exception as e:
            log(f"    REST batch failed: {e}")

        time.sleep(0.5)

    log(f"  Total mapped: {len(symbol_map)} / "
        f"{len(ensembl_ids)}")

    if len(symbol_map) < 100:
        log("  Too few mapped. Keeping Ensembl IDs.")
        return df

    # Apply mapping — keep Ensembl ID if no symbol found
    new_index = [
        symbol_map.get(eid, eid)
        for eid in df.index
    ]
    df = df.copy()
    df.index = new_index

    # Deduplicate by highest mean
    df = dedup_by_mean(df)
    log(f"  After symbol map + dedup: {len(df)} genes")
    return df


def dedup_by_mean(df):
    """
    Keep one row per gene symbol — the row
    with the highest mean expression.
    """
    df = df.copy()
    df["_mean"] = df.select_dtypes(
        include=[np.number]
    ).mean(axis=1)
    df = df.sort_values("_mean", ascending=False)
    df = df[~df.index.duplicated(keep="first")]
    df = df.drop(columns=["_mean"])
    return df

# ============================================================
# STEP 5: BUILD SAMPLE LABELS
# ============================================================

def build_labels(log2_cpm):
    """
    Build a sample label DataFrame aligned to
    the columns of log2_cpm.
    """
    rows = []
    for gsm in log2_cpm.columns:
        patient, stype = SAMPLE_MAP.get(
            gsm, ("UNKNOWN", "UNKNOWN")
        )
        rows.append({
            "gsm":     gsm,
            "patient": patient,
            "type":    stype,
        })
    return pd.DataFrame(rows).set_index("gsm")

# ============================================================
# STEP 6: BLIND SADDLE POINT SCAN
#
# Every detected gene tested.
# Tumour vs normal.
# No pre-loaded panels.
# The geometry reveals itself.
# ============================================================

def blind_saddle_point_scan(log2_cpm, labels):
    log("")
    log("=" * 65)
    log("STEP 6: BLIND SADDLE POINT SCAN")
    log("All genes. No pre-selected panels.")
    log("Tumour vs Normal. Geometry reveals itself.")
    log("=" * 65)

    tumor_cols  = [
        c for c in log2_cpm.columns
        if c in TUMOR_SAMPLES
    ]
    normal_cols = [
        c for c in log2_cpm.columns
        if c in NORMAL_SAMPLES
    ]

    log(f"  Tumour samples : {len(tumor_cols)}")
    log(f"  Normal samples : {len(normal_cols)}")
    log(f"  Genes to test  : {len(log2_cpm)}")

    if len(tumor_cols) < 3 or len(normal_cols) < 2:
        log("  ERROR: Insufficient samples for scan")
        return None

    def fmt_p(p):
        if p < 1e-10: return f"p={p:.2e} ***"
        if p < 0.001: return f"p={p:.2e} ***"
        if p < 0.01:  return f"p={p:.2e}  **"
        if p < 0.05:  return f"p={p:.4f}   *"
        return              f"p={p:.4f}  ns"

    results = []
    genes   = log2_cpm.index.tolist()

    for gene in genes:
        try:
            tv = log2_cpm.loc[gene, tumor_cols].values
            nv = log2_cpm.loc[gene, normal_cols].values
            tv = tv[~np.isnan(tv)]
            nv = nv[~np.isnan(nv)]

            if len(tv) < 3 or len(nv) < 2:
                continue

            nm  = nv.mean()
            tm  = tv.mean()

            if abs(nm) < 0.0001 and abs(tm) < 0.0001:
                continue

            chg = (
                (tm - nm) / max(abs(nm), 0.01) * 100
            )

            # Mann-Whitney U — two-sided via min of one-sided
            _, p_down = stats.mannwhitneyu(
                nv, tv, alternative="greater"
            )
            _, p_up   = stats.mannwhitneyu(
                tv, nv, alternative="greater"
            )
            p_use     = min(p_down, p_up)
            direction = "DOWN" if tm < nm else "UP"

            results.append({
                "gene":        str(gene),
                "normal_mean": nm,
                "tumor_mean":  tm,
                "change_pct":  chg,
                "direction":   direction,
                "p_value":     p_use,
                "abs_change":  abs(chg),
            })
        except Exception:
            pass

    rdf = pd.DataFrame(results)
    if len(rdf) == 0:
        log("  ERROR: No genes tested")
        return None

    rdf = rdf.sort_values("abs_change", ascending=False)
    log(f"  Genes tested: {len(rdf)}")
    log(f"  Significant (p<0.05): "
        f"{(rdf['p_value'] < 0.05).sum()}")

    # Save full scan
    rdf.to_csv(
        os.path.join(RESULTS_DIR, "saddle_scan.csv"),
        index=False
    )

    # Report top suppressed
    sig_down = rdf[
        (rdf["direction"] == "DOWN")
        & (rdf["p_value"] < 0.05)
    ].head(40)

    # Report top elevated
    sig_up = rdf[
        (rdf["direction"] == "UP")
        & (rdf["p_value"] < 0.05)
    ].head(40)

    log(f"\n  {'='*65}")
    log(f"  TOP SUPPRESSED IN TUMOUR  "
        f"(switch gene candidates)")
    log(f"  {'='*65}")
    log(f"  {'Gene':<20} {'Normal':>8} {'Tumour':>8} "
        f"{'Change':>9}  {'p-value':>16}")
    log(f"  {'-'*68}")
    for _, row in sig_down.head(30).iterrows():
        log(
            f"  {row['gene']:<20} "
            f"{row['normal_mean']:>8.4f} "
            f"{row['tumor_mean']:>8.4f} "
            f"{row['change_pct']:>+8.1f}%  "
            f"{fmt_p(row['p_value']):>16}"
        )

    log(f"\n  {'='*65}")
    log(f"  TOP ELEVATED IN TUMOUR    "
        f"(FA marker candidates)")
    log(f"  {'='*65}")
    log(f"  {'Gene':<20} {'Normal':>8} {'Tumour':>8} "
        f"{'Change':>9}  {'p-value':>16}")
    log(f"  {'-'*68}")
    for _, row in sig_up.head(30).iterrows():
        log(
            f"  {row['gene']:<20} "
            f"{row['normal_mean']:>8.4f} "
            f"{row['tumor_mean']:>8.4f} "
            f"{row['change_pct']:>+8.1f}%  "
            f"{fmt_p(row['p_value']):>16}"
        )

    return rdf

# ============================================================
# STEP 7: BLIND DEPTH SCORE
#
# Derived from top N suppressed + top N elevated genes.
# No pre-loaded panels.
# The geometry defines the score.
# ============================================================

def blind_depth_score(log2_cpm, rdf):
    log("")
    log("=" * 65)
    log("STEP 7: BLIND DEPTH SCORE")
    log(f"  Top {N_TOP_GENES} suppressed + "
        f"top {N_TOP_GENES} elevated (p<0.05)")
    log("  Geometry-derived. No pre-loaded panels.")
    log("=" * 65)

    tumor_cols = [
        c for c in log2_cpm.columns
        if c in TUMOR_SAMPLES
    ]

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
        if g in log2_cpm.index
    ]
    up_genes = [
        g for g in sig_up["gene"].values
        if g in log2_cpm.index
    ]

    log(f"  Switch candidates used : {len(down_genes)}")
    log(f"  FA candidates used     : {len(up_genes)}")

    def norm01(s):
        mn, mx = s.min(), s.max()
        if mx > mn:
            return (s - mn) / (mx - mn)
        return pd.Series(0.5, index=s.index)

    tumor_expr = log2_cpm[tumor_cols].T   # samples × genes
    depth = pd.Series(
        np.zeros(len(tumor_cols)),
        index=tumor_cols
    )
    comp = 0

    if down_genes:
        sw_m   = tumor_expr[down_genes].mean(axis=1)
        depth += (1 - norm01(sw_m))
        comp  += 1

    if up_genes:
        fa_m   = tumor_expr[up_genes].mean(axis=1)
        depth += norm01(fa_m)
        comp  += 1

    if comp > 0:
        depth /= comp

    log(f"\n  Block depth ({len(tumor_cols)} tumours):")
    log(f"    Mean  : {depth.mean():.4f}")
    log(f"    Median: {depth.median():.4f}")
    log(f"    Std   : {depth.std():.4f}")
    log(f"    Min   : {depth.min():.4f}")
    log(f"    Max   : {depth.max():.4f}")

    # Per-sample depth
    log(f"\n  Depth by sample:")
    for gsm in tumor_cols:
        patient, _ = SAMPLE_MAP.get(gsm, ("?", "?"))
        log(f"    {gsm} ({patient}): {depth[gsm]:.4f}")

    # Depth correlations — all genes
    log(f"\n  {'='*65}")
    log(f"  DEPTH CORRELATIONS (top 30)")
    log(f"  These are the true biology signals.")
    log(f"  {'='*65}")
    log(f"  {'Gene':<20} {'r':>8}  p-value")
    log(f"  {'-'*44}")

    corrs = []
    for gene in log2_cpm.index:
        try:
            gene_vals = log2_cpm.loc[gene, tumor_cols].values
            gene_vals = gene_vals.astype(float)
            if np.std(gene_vals) < 1e-8:
                continue
            rv, pv = stats.pearsonr(
                depth.values, gene_vals
            )
            corrs.append((str(gene), rv, pv))
        except Exception:
            pass

    corrs.sort(key=lambda x: abs(x[1]), reverse=True)

    for gene, rv, pv in corrs[:30]:
        log(f"  {gene:<20} {rv:>+8.4f}  p={pv:.2e}")

    # Save
    corr_df = pd.DataFrame(
        corrs, columns=["gene", "r", "p_value"]
    )
    corr_df.to_csv(
        os.path.join(RESULTS_DIR, "depth_correlations.csv"),
        index=False
    )
    log(f"\n  Saved: depth_correlations.csv")

    # Save saddle results with depth
    saddle_out = os.path.join(
        RESULTS_DIR, "saddle_results.csv"
    )
    rdf.to_csv(saddle_out, index=False)
    log(f"  Saved: saddle_results.csv")

    return depth, corrs

# ============================================================
# STEP 8: PAIRED ANALYSIS
#
# 6 matched pairs available (CDC1–CDC4, CDC6, CDC7).
# Paired analysis is more powerful with n=7 tumours.
# Run paired t-test / Wilcoxon signed-rank for the
# top candidates from the blind scan.
# ============================================================

def paired_analysis(log2_cpm, rdf):
    log("")
    log("=" * 65)
    log("STEP 8: PAIRED ANALYSIS")
    log("  6 matched tumour–normal pairs")
    log("  Wilcoxon signed-rank for top movers")
    log("=" * 65)

    pairs = [
        ("CDC1",  "GSM2359144", "GSM2359145"),
        ("CDC2",  "GSM2359146", "GSM2359147"),
        ("CDC3",  "GSM2359148", "GSM2359149"),
        ("CDC4",  "GSM2359150", "GSM2359151"),
        ("CDC6",  "GSM2359153", "GSM2359154"),
        ("CDC7",  "GSM2359155", "GSM2359156"),
    ]

    # Filter to pairs where both samples loaded
    available_pairs = []
    for patient, t_gsm, n_gsm in pairs:
        if (t_gsm in log2_cpm.columns
                and n_gsm in log2_cpm.columns):
            available_pairs.append(
                (patient, t_gsm, n_gsm)
            )
        else:
            log(f"  Missing: {patient} "
                f"({t_gsm} or {n_gsm})")

    log(f"  Pairs available: {len(available_pairs)}")

    if len(available_pairs) < 3:
        log("  Too few pairs for paired analysis")
        return None

    # Use top 50 candidates from blind scan
    top_genes = rdf.head(200)["gene"].values
    top_genes = [
        g for g in top_genes if g in log2_cpm.index
    ][:50]

    paired_results = []
    for gene in top_genes:
        diffs = []
        for patient, t_gsm, n_gsm in available_pairs:
            tv = log2_cpm.loc[gene, t_gsm]
            nv = log2_cpm.loc[gene, n_gsm]
            diffs.append(tv - nv)

        if len(diffs) < 3:
            continue

        diffs = np.array(diffs)
        mean_diff = diffs.mean()

        # Wilcoxon signed-rank
        try:
            if len(set(diffs)) == 1:
                p_paired = 1.0
            else:
                _, p_paired = stats.wilcoxon(
                    diffs, alternative="two-sided"
                )
        except Exception:
            p_paired = np.nan

        direction = "DOWN" if mean_diff < 0 else "UP"
        paired_results.append({
            "gene":       gene,
            "mean_diff":  mean_diff,
            "direction":  direction,
            "p_paired":   p_paired,
            "diffs":      diffs.tolist(),
        })

    paired_df = pd.DataFrame(paired_results)
    paired_df = paired_df.sort_values(
        "mean_diff", key=abs, ascending=False
    )

    log(f"\n  Paired analysis ({len(available_pairs)} pairs):")
    log(f"  Top genes by mean paired difference:")
    log(f"\n  {'Gene':<20} {'MeanDiff':>10} "
        f"{'Dir':>6} {'p_paired':>12}")
    log(f"  {'-'*54}")

    sig_paired = paired_df[
        paired_df["p_paired"] < 0.05
    ].head(30)

    for _, row in paired_df.head(30).iterrows():
        p_str = (
            f"p={row['p_paired']:.4f}"
            if not np.isnan(row["p_paired"])
            else "p=NA"
        )
        sig_flag = (
            " *" if row["p_paired"] < 0.05
            else ("  " if not np.isnan(row["p_paired"])
                  else "")
        )
        log(
            f"  {row['gene']:<20} "
            f"{row['mean_diff']:>+10.4f}  "
            f"{row['direction']:>6}  "
            f"{p_str}{sig_flag}"
        )

    paired_df.drop(
        columns=["diffs"]
    ).to_csv(
        os.path.join(RESULTS_DIR, "paired_results.csv"),
        index=False
    )
    log(f"\n  Saved: paired_results.csv")

    return paired_df

# ============================================================
# STEP 9: FIGURE
#
# 9-panel attractor landscape figure.
# Shows geometry without naming it.
# ============================================================

def generate_figure(log2_cpm, rdf, depth, corrs, paired_df):
    log("")
    log("--- Generating figure ---")

    tumor_cols  = [
        c for c in log2_cpm.columns
        if c in TUMOR_SAMPLES
    ]
    normal_cols = [
        c for c in log2_cpm.columns
        if c in NORMAL_SAMPLES
    ]

    fig = plt.figure(figsize=(24, 18))
    fig.suptitle(
        f"OrganismCore — cdRCC False Attractor Discovery\n"
        f"GSE89122  |  "
        f"Tumour: {len(tumor_cols)}  |  "
        f"Normal: {len(normal_cols)}  |  "
        f"Pairs: 6\n"
        f"Blind scan — geometry first — no pre-loaded panels",
        fontsize=11, fontweight="bold", y=0.99,
    )
    gs = gridspec.GridSpec(
        3, 3, figure=fig,
        hspace=0.52, wspace=0.42,
    )

    clr_t = "#c0392b"   # tumour red
    clr_n = "#2980b9"   # normal blue
    clr_d = "#c0392b"   # down red
    clr_u = "#27ae60"   # up green

    # ---- Panel A: Top suppressed ----
    ax_a = fig.add_subplot(gs[0, 0])
    top_down = rdf[
        (rdf["direction"] == "DOWN")
        & (rdf["p_value"] < 0.05)
    ].head(15)
    if len(top_down) > 0:
        genes   = top_down["gene"].values
        nm_vals = top_down["normal_mean"].values
        tm_vals = top_down["tumor_mean"].values
        x = np.arange(len(genes))
        w = 0.35
        ax_a.bar(x - w/2, nm_vals, w,
                 color=clr_n, label="Normal", alpha=0.85)
        ax_a.bar(x + w/2, tm_vals, w,
                 color=clr_t, label="Tumour", alpha=0.85)
        ax_a.set_xticks(x)
        ax_a.set_xticklabels(
            genes, rotation=45, ha="right", fontsize=6
        )
        ax_a.set_title(
            "A — Top Suppressed\n(switch candidates)",
            fontsize=9
        )
        ax_a.legend(fontsize=7)
        ax_a.set_ylabel("log2(CPM+1)", fontsize=8)

    # ---- Panel B: Top elevated ----
    ax_b = fig.add_subplot(gs[0, 1])
    top_up = rdf[
        (rdf["direction"] == "UP")
        & (rdf["p_value"] < 0.05)
    ].head(15)
    if len(top_up) > 0:
        genes   = top_up["gene"].values
        nm_vals = top_up["normal_mean"].values
        tm_vals = top_up["tumor_mean"].values
        x = np.arange(len(genes))
        w = 0.35
        ax_b.bar(x - w/2, nm_vals, w,
                 color=clr_n, label="Normal", alpha=0.85)
        ax_b.bar(x + w/2, tm_vals, w,
                 color=clr_t, label="Tumour", alpha=0.85)
        ax_b.set_xticks(x)
        ax_b.set_xticklabels(
            genes, rotation=45, ha="right", fontsize=6
        )
        ax_b.set_title(
            "B — Top Elevated\n(FA marker candidates)",
            fontsize=9
        )
        ax_b.legend(fontsize=7)
        ax_b.set_ylabel("log2(CPM+1)", fontsize=8)

    # ---- Panel C: Waterfall ----
    ax_c = fig.add_subplot(gs[0, 2])
    sig  = rdf[rdf["p_value"] < 0.05].copy()
    sig  = sig.sort_values("change_pct")
    if len(sig) > 0:
        n_each = 20
        show = pd.concat([
            sig.head(n_each),
            sig.tail(n_each),
        ]).drop_duplicates()
        bc = [
            clr_d if v < 0 else clr_u
            for v in show["change_pct"]
        ]
        ax_c.barh(show["gene"], show["change_pct"], color=bc)
        ax_c.axvline(0, color="black", linewidth=0.8)
        ax_c.set_xlabel("% change vs normal", fontsize=8)
        ax_c.set_title(
            f"C — Waterfall  (top {len(show)} movers)",
            fontsize=9
        )
        ax_c.tick_params(axis="y", labelsize=5)

    # ---- Panel D: Depth distribution ----
    ax_d = fig.add_subplot(gs[1, 0])
    ax_d.hist(
        depth.values, bins=max(5, len(depth) // 2),
        color=clr_t, alpha=0.7, edgecolor="white"
    )
    ax_d.axvline(
        depth.mean(), color="black",
        linewidth=1.5, linestyle="--",
        label=f"mean={depth.mean():.3f}"
    )
    ax_d.set_xlabel("Block Depth Score", fontsize=8)
    ax_d.set_ylabel("Count", fontsize=8)
    ax_d.set_title(
        "D — Depth Distribution\nBlind geometry score",
        fontsize=9
    )
    ax_d.legend(fontsize=7)

    # Add per-sample labels
    for gsm, d_val in depth.items():
        patient, _ = SAMPLE_MAP.get(gsm, ("?", "?"))
        ax_d.annotate(
            patient,
            xy=(d_val, 0.1),
            xycoords=("data", "axes fraction"),
            fontsize=5, rotation=90, ha="center",
        )

    # ---- Panel E: Top depth correlations ----
    ax_e = fig.add_subplot(gs[1, 1])
    if corrs:
        top_c = corrs[:25]
        gc = [c[0] for c in top_c]
        vc = [c[1] for c in top_c]
        cc = [clr_d if v < 0 else clr_u for v in vc]
        ax_e.barh(gc, vc, color=cc)
        ax_e.axvline(0, color="black", linewidth=0.8)
        ax_e.set_xlabel("r with depth score", fontsize=8)
        ax_e.set_title(
            "E — Depth Correlations\nTop 25",
            fontsize=9
        )
        ax_e.tick_params(axis="y", labelsize=6)

    # ---- Panel F: Paired differences ----
    ax_f = fig.add_subplot(gs[1, 2])
    if paired_df is not None and len(paired_df) > 0:
        top_paired = paired_df.head(15)
        genes_p    = top_paired["gene"].values
        diffs_p    = top_paired["mean_diff"].values
        colors_p   = [
            clr_d if v < 0 else clr_u for v in diffs_p
        ]
        x_p = np.arange(len(genes_p))
        ax_f.bar(x_p, diffs_p, color=colors_p, alpha=0.8)
        ax_f.axhline(0, color="black", linewidth=0.8)
        ax_f.set_xticks(x_p)
        ax_f.set_xticklabels(
            genes_p, rotation=45, ha="right", fontsize=6
        )
        ax_f.set_ylabel("Mean paired diff", fontsize=8)
        ax_f.set_title(
            "F — Paired Differences\n(6 matched pairs)",
            fontsize=9
        )

    # ---- Panel G: Scatter depth vs top FA gene ----
    ax_g = fig.add_subplot(gs[2, 0])
    pos_corrs = [c for c in corrs if c[1] > 0]
    if pos_corrs and len(tumor_cols) >= 3:
        top_fa   = pos_corrs[0][0]
        if top_fa in log2_cpm.index:
            fa_expr = log2_cpm.loc[top_fa, tumor_cols]
            ax_g.scatter(
                fa_expr.values, depth.values,
                color=clr_t, alpha=0.7, s=40
            )
            # Label each point
            for gsm in tumor_cols:
                patient, _ = SAMPLE_MAP.get(
                    gsm, ("?", "?")
                )
                ax_g.annotate(
                    patient,
                    (fa_expr[gsm], depth[gsm]),
                    fontsize=7,
                    xytext=(3, 3),
                    textcoords="offset points",
                )
            ax_g.set_xlabel(
                f"{top_fa} log2(CPM+1)", fontsize=8
            )
            ax_g.set_ylabel("Block Depth", fontsize=8)
            ax_g.set_title(
                f"G — Depth vs {top_fa}\n"
                f"r={pos_corrs[0][1]:.3f}",
                fontsize=9
            )

    # ---- Panel H: Scatter depth vs top switch gene ----
    ax_h = fig.add_subplot(gs[2, 1])
    neg_corrs = [c for c in corrs if c[1] < 0]
    if neg_corrs and len(tumor_cols) >= 3:
        top_sw = neg_corrs[0][0]
        if top_sw in log2_cpm.index:
            sw_expr = log2_cpm.loc[top_sw, tumor_cols]
            ax_h.scatter(
                sw_expr.values, depth.values,
                color=clr_d, alpha=0.7, s=40
            )
            for gsm in tumor_cols:
                patient, _ = SAMPLE_MAP.get(
                    gsm, ("?", "?")
                )
                ax_h.annotate(
                    patient,
                    (sw_expr[gsm], depth[gsm]),
                    fontsize=7,
                    xytext=(3, 3),
                    textcoords="offset points",
                )
            ax_h.set_xlabel(
                f"{top_sw} log2(CPM+1)", fontsize=8
            )
            ax_h.set_ylabel("Block Depth", fontsize=8)
            ax_h.set_title(
                f"H — Depth vs {top_sw}\n"
                f"r={neg_corrs[0][1]:.3f}",
                fontsize=9
            )

    # ---- Panel I: Summary text ----
    ax_i = fig.add_subplot(gs[2, 2])
    ax_i.axis("off")
    n_sig  = (rdf["p_value"] < 0.05).sum()
    n_down = (
        (rdf["direction"] == "DOWN")
        & (rdf["p_value"] < 0.05)
    ).sum()
    n_up = (
        (rdf["direction"] == "UP")
        & (rdf["p_value"] < 0.05)
    ).sum()
    top5_down = rdf[
        (rdf["direction"] == "DOWN")
        & (rdf["p_value"] < 0.05)
    ].head(5)["gene"].tolist()
    top5_up = rdf[
        (rdf["direction"] == "UP")
        & (rdf["p_value"] < 0.05)
    ].head(5)["gene"].tolist()
    summary = (
        f"I — DISCOVERY SUMMARY\n"
        f"──────────────────────────────\n"
        f"Dataset   : GSE89122\n"
        f"Tumour    : {len(tumor_cols)}\n"
        f"Normal    : {len(normal_cols)}\n"
        f"Pairs     : 6 matched\n\n"
        f"Genes tested: {len(rdf)}\n"
        f"p<0.05:     {n_sig}\n"
        f"  Suppressed: {n_down}\n"
        f"  Elevated:   {n_up}\n\n"
        f"Depth score:\n"
        f"  Mean: {depth.mean():.4f}\n"
        f"  Std:  {depth.std():.4f}\n\n"
        f"Top suppressed:\n"
        + "".join(f"  {g}\n" for g in top5_down) +
        f"\nTop elevated:\n"
        + "".join(f"  {g}\n" for g in top5_up) +
        f"\nOrganismCore  2026-03-03\n"
        f"The geometry revealed itself.\n"
        f"Analyst writes Phase 1 next."
    )
    ax_i.text(
        0.03, 0.97, summary,
        transform=ax_i.transAxes,
        fontsize=8,
        verticalalignment="top",
        fontfamily="monospace",
        bbox=dict(
            boxstyle="round",
            facecolor="#f8f8f8",
            edgecolor="#cccccc",
        ),
    )

    outpath = os.path.join(
        RESULTS_DIR,
        "GSE89122_attractor_landscape.png"
    )
    plt.savefig(outpath, dpi=150, bbox_inches="tight")
    log(f"\n  Figure saved: {outpath}")
    plt.close()

# ============================================================
# MAIN
# ============================================================

def main():
    log("=" * 65)
    log("OrganismCore — cdRCC False Attractor Discovery")
    log("SCRIPT 1 — BLIND GEOMETRIC LANDSCAPE SCAN")
    log("Dataset: GSE89122")
    log("7 CDC tumours | 6 matched normals | 6 pairs")
    log("Platform: Illumina HiSeq 2000 | RNA-seq")
    log("Date: 2026-03-03")
    log("=" * 65)
    log("")
    log("The geometry reveals itself.")
    log("No pre-loaded cancer-specific gene panels.")
    log("Analyst reads output and writes Phase 1.")
    log("")

    # Step 1: Download per-GSM count files
    gsm_paths = download_all_gsm_files()

    if len(gsm_paths) < 5:
        log(f"FATAL: Only {len(gsm_paths)} samples "
            f"downloaded. Minimum 5 needed.")
        write_log()
        return

    # Step 2: Merge counts
    counts = merge_count_files(gsm_paths)
    if counts is None:
        log("FATAL: Could not merge counts")
        write_log()
        return

    # Step 3: Normalise
    log2_cpm = normalise_counts(counts)

    # Step 4: Gene IDs
    log2_cpm = clean_gene_ids(log2_cpm)

    # Step 5: Labels (implicit via SAMPLE_MAP)
    labels = build_labels(log2_cpm)

    # Step 6: Blind saddle point scan
    rdf = blind_saddle_point_scan(log2_cpm, labels)
    if rdf is None:
        log("FATAL: Saddle point scan failed")
        write_log()
        return

    # Step 7: Blind depth score
    depth, corrs = blind_depth_score(log2_cpm, rdf)

    # Step 8: Paired analysis
    paired_df = paired_analysis(log2_cpm, rdf)

    # Step 9: Figure
    generate_figure(
        log2_cpm, rdf, depth, corrs, paired_df
    )

    # Save log
    write_log()

    log("")
    log("=" * 65)
    log("SCRIPT 1 COMPLETE")
    log("")
    log("Outputs:")
    log(f"  {RESULTS_DIR}/saddle_scan.csv")
    log(f"  {RESULTS_DIR}/saddle_results.csv")
    log(f"  {RESULTS_DIR}/depth_correlations.csv")
    log(f"  {RESULTS_DIR}/paired_results.csv")
    log(f"  {RESULTS_DIR}/GSE89122_log2cpm.csv")
    log(f"  {RESULTS_DIR}/GSE89122_attractor_landscape.png")
    log(f"  {RESULTS_DIR}/analysis_log.txt")
    log("")
    log("Read the output now:")
    log("  1. Top suppressed = switch gene candidates")
    log("  2. Top elevated   = FA marker candidates")
    log("  3. Depth corrs    = convergence node")
    log("  4. Paired diffs   = paired-confirmed signals")
    log("")
    log("Write Doc 89a after reading.")
    log("Lock Phase 1 predictions before Script 2.")
    log("=" * 65)


if __name__ == "__main__":
    main()
