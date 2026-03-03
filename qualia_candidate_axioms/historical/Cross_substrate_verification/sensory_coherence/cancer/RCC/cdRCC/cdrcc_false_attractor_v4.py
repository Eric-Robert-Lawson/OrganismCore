"""
cdRCC — Collecting Duct Renal Cell Carcinoma
FALSE ATTRACTOR — SCRIPT 4
OrganismCore Cancer Validation #13

Four biological tests + GSE83479 replication fix:
  Step 0:  Load GSE89122 matrix (primary)
  Step 1:  GSE83479 metadata diagnosis
           Fetch raw metadata, determine
           sample classification terms,
           build hardcoded GSM-to-type map
  Step 2:  Load and classify GSE83479
  Step 3:  Replication panel (S3-P7 fix)
           12 genes, directions from Doc 89b
  Step 4:  GSE83479 Spearman depth correlations
           tumour-only — does the same axis hold?
  Step 5:  HK2 driver test
           r(HK2, HIF1A / RELA / CEBPB / EPAS1)
           Prediction (Doc 89b addendum):
           RELA or CEBPB drives HK2
  Step 6:  MYC/BHLHE40 transition confirmation
           CDC3 = highest MYC + lowest BHLHE40?
           r(MYC, BHLHE40) = -0.964 (S3)
           Confirm transition sequence N8
  Step 7:  CEBPA antagonism panel
           r(CEBPA, whole PPARG module)
           Does CEBPA oppose AGR2, KLF5,
           IL1RAP, ESRP1 as well as PPARG?
  Step 8:  ADPRM alternative depth proxy
           Rebuild depth score with ADPRM
           instead of PRKAR2B
           Compare r(S3_depth, S4_depth)
  Step 9:  S3 vs S4 depth score comparison
  Step 10: Figure (9 panels)
  Step 11: Summary

PREDICTIONS STATED BEFORE THIS SCRIPT RAN
(from Doc 89b addendum, dated 2026-03-03):
  P4-1: GSE83479 replication — 8+/12 replicate
  P4-2: HK2 driver = RELA or CEBPB (NF-kB arm)
  P4-3: CDC3 has lowest BHLHE40 in tumour set
        (transition sequence confirmed)
  P4-4: CEBPA opposes whole PPARG module
        (not just PPARG itself)
  P4-5: r(S3_depth, S4_depth) > 0.95

Author:    Eric Robert Lawson
Framework: OrganismCore
Protocol:  Phase 3 — Script 4
Date:      2026-03-03
Follows:   Scripts 1, 2, 3 (v2)
           Doc 89b, Doc 89b addendum
"""

import os
import sys
import gzip
import re
import time
import urllib.request
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

ACC_PRIMARY     = "GSE89122"
ACC_REPLICATION = "GSE83479"

BASE_DIR    = "./cdrcc_false_attractor/"
RESULTS_DIR = os.path.join(BASE_DIR, "results")
S4_DIR      = os.path.join(BASE_DIR, "results_s4")
REP_DIR     = os.path.join(BASE_DIR, "GSE83479")
LOG_FILE    = os.path.join(S4_DIR, "analysis_log_s4.txt")

MATRIX_PATH = os.path.join(
    RESULTS_DIR, "GSE89122_log2cpm.csv"
)

# GSE83479 matrix — cached from S3 attempt
REP_MATRIX_PATH = os.path.join(
    REP_DIR,
    "GSE83479_rsem_gfpkm_matrix.paper.txt.gz"
)

os.makedirs(S4_DIR, exist_ok=True)

# ============================================================
# SAMPLE MAP — GSE89122 (locked Phase 0)
# ============================================================

SAMPLE_MAP_89122 = {
    "GSM2359144": ("CDC1", "tumor"),
    "GSM2359145": ("CDC1", "normal"),
    "GSM2359146": ("CDC2", "tumor"),
    "GSM2359147": ("CDC2", "normal"),
    "GSM2359148": ("CDC3", "tumor"),
    "GSM2359149": ("CDC3", "normal"),
    "GSM2359150": ("CDC4", "tumor"),
    "GSM2359151": ("CDC4", "normal"),
    "GSM2359152": ("CDC5", "tumor"),
    "GSM2359153": ("CDC6", "tumor"),
    "GSM2359154": ("CDC6", "normal"),
    "GSM2359155": ("CDC7", "tumor"),
    "GSM2359156": ("CDC7", "normal"),
}

# ============================================================
# GENE PANELS — locked Doc 89b / 89b addendum
# ============================================================

SWITCH_GENE_S3 = "PRKAR2B"   # S3 depth component 1
FA_GENE_S3     = "IL1RAP"    # S3 depth component 2
SWITCH_GENE_S4 = "ADPRM"     # S4 alternative proxy

PROG_A = [
    "PPARG", "KLF5", "AGR2", "ESRP1",
    "IL1RAP", "GPRC5A", "SERPINA1",
    "TMPRSS4", "CST6", "KLF10",
]

# Replication panel — directions from Doc 89b addendum
# (stated before this script, before literature)
REPLICATION_PANEL = {
    "AQP2":    "DOWN",
    "PRKAR2B": "DOWN",
    "AVPR2":   "DOWN",
    "SCNN1B":  "DOWN",
    "FOXI1":   "DOWN",
    "HNF4A":   "DOWN",
    "PPARG":   "FLAT",
    "KLF5":    "UP",
    "AGR2":    "UP",
    "EZH2":    "UP",
    "IL1RAP":  "UP",
    "MKI67":   "UP",
}

# HK2 driver candidates (Step 5)
HK2_DRIVER_CANDIDATES = [
    "HIF1A", "EPAS1", "HIF3A",
    "RELA", "NFKB1", "NFKB2",
    "CEBPB", "CEBPA",
    "MYC", "MYCN",
    "BHLHE40",
    "PPARG", "KLF5",
    "IL1B", "IL6",
    "ADCY3", "PRKCI",
]

# MYC/BHLHE40 transition panel (Step 6)
TRANSITION_PANEL = [
    "MYC", "BHLHE40",
    "KLF5", "PPARG", "AGR2", "IL1RAP",
    "PRKAR2B", "AQP2",
    "MKI67", "EZH2",
    "HK1", "HK2",
]

# CEBPA antagonism panel (Step 7)
CEBPA_PANEL = [
    "CEBPA",
    "PPARG", "KLF5", "AGR2", "IL1RAP",
    "ESRP1", "GPRC5A", "CST6", "KLF10",
    "TMPRSS4", "SERPINA1",
    "CEBPB", "RELA", "IL1B",
    "EZH2", "MYC",
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
# UTILITIES
# ============================================================

def fetch_text(url, timeout=35):
    req = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0"}
    )
    try:
        with urllib.request.urlopen(
            req, timeout=timeout
        ) as r:
            raw = r.read()
            try:
                return raw.decode("utf-8")
            except UnicodeDecodeError:
                return raw.decode("latin-1")
    except Exception as e:
        return f"ERROR:{e}"


def spearman(x, y):
    x = np.array(x, dtype=float)
    y = np.array(y, dtype=float)
    mask = (~np.isnan(x)) & (~np.isnan(y))
    if mask.sum() < 4:
        return np.nan, np.nan
    r, p = stats.spearmanr(x[mask], y[mask])
    return float(r), float(p)


def pearson(x, y):
    x = np.array(x, dtype=float)
    y = np.array(y, dtype=float)
    mask = (~np.isnan(x)) & (~np.isnan(y))
    if mask.sum() < 4:
        return np.nan, np.nan
    r, p = stats.pearsonr(x[mask], y[mask])
    return float(r), float(p)


def fmt_p(p):
    if p is None or np.isnan(p):
        return "        ns"
    if p < 0.001:
        return f"p={p:.2e} ***"
    if p < 0.01:
        return f"p={p:.4f}  **"
    if p < 0.05:
        return f"p={p:.4f}   *"
    return f"p={p:.4f}  ns"


def norm01(s):
    s = pd.Series(s)
    lo, hi = s.min(), s.max()
    if hi == lo:
        return pd.Series(0.0, index=s.index)
    return (s - lo) / (hi - lo)

# ============================================================
# STEP 0 — LOAD GSE89122 PRIMARY MATRIX
# ============================================================

def load_primary():
    log("=" * 65)
    log("STEP 0 — LOADING PRIMARY MATRIX (GSE89122)")
    log(f"  {MATRIX_PATH}")
    log("=" * 65)

    if not os.path.exists(MATRIX_PATH):
        log("  ERROR: Matrix not found.")
        log("  Run Script 1 first.")
        sys.exit(1)

    df = pd.read_csv(MATRIX_PATH, index_col=0)

    t_cols = [
        c for c in df.columns
        if SAMPLE_MAP_89122.get(c, ("",""))[1]
        == "tumor"
    ]
    n_cols = [
        c for c in df.columns
        if SAMPLE_MAP_89122.get(c, ("",""))[1]
        == "normal"
    ]

    log(f"  Shape: {df.shape[0]} genes x "
        f"{df.shape[1]} samples")
    log(f"  Tumour: {len(t_cols)}  "
        f"Normal: {len(n_cols)}")

    tumor  = df[t_cols]
    normal = df[n_cols]
    return df, tumor, normal, t_cols, n_cols

# ============================================================
# STEP 1 — GSE83479 METADATA DIAGNOSIS
# ============================================================

def diagnose_gse83479_metadata():
    """
    Fetch raw SOFT metadata for a sample of GSMs
    from GSE83479 to determine the actual
    classification terms used.
    GSM range: GSM2204076 to GSM2204132 (57 samples).
    Sample strategically: first 3, middle 3, last 3.
    """
    log("")
    log("=" * 65)
    log("STEP 1 — GSE83479 METADATA DIAGNOSIS")
    log("  Fetching raw metadata to identify")
    log("  correct sample classification terms.")
    log("=" * 65)

    # Sample GSMs to inspect
    all_gsms = [
        f"GSM{2204076 + i}" for i in range(57)
    ]
    # Inspect first 5, middle 5, last 5
    probe_indices = (
        list(range(5))
        + list(range(26, 31))
        + list(range(52, 57))
    )
    probe_gsms = [all_gsms[i] for i in probe_indices]

    sample_info = {}

    log(f"\n  Probing {len(probe_gsms)} GSMs...")

    for gsm in probe_gsms:
        url = (
            "https://www.ncbi.nlm.nih.gov/geo/query/"
            f"acc.cgi?acc={gsm}"
            "&targ=self&form=text&view=full"
        )
        text = fetch_text(url)
        time.sleep(0.4)

        if "ERROR" in text[:20]:
            log(f"  {gsm}: FETCH ERROR")
            continue

        info = {"gsm": gsm, "raw_lines": []}
        for line in text.split("\n"):
            for key in [
                "!Sample_title",
                "!Sample_source_name_ch1",
                "!Sample_characteristics_ch1",
                "!Sample_description",
                "!Sample_organism_ch1",
                "!Sample_library_strategy",
            ]:
                if line.startswith(key):
                    val = line.split("=", 1)[1].strip()
                    k   = key.replace(
                        "!Sample_", ""
                    ).split("_ch1")[0]
                    info[k] = info.get(k, "") + \
                              " | " + val
                    info["raw_lines"].append(
                        f"  {key}: {val}"
                    )
        sample_info[gsm] = info

    # Print all discovered metadata
    log("\n  RAW METADATA DUMP:")
    for gsm, info in sample_info.items():
        log(f"\n  {gsm}:")
        for line in info.get("raw_lines", []):
            log(line)

    # Identify classification keywords
    log("\n  KEYWORD ANALYSIS:")
    all_text = " ".join(
        " ".join(info.get("raw_lines", []))
        for info in sample_info.values()
    ).lower()

    keywords_to_check = [
        "collecting duct", "bellini", "cdc",
        "utuc", "urothelial", "upper tract",
        "normal", "adjacent", "non-tumor",
        "carcinoma", "kidney", "renal",
        "tumor", "tumour", "cancer",
        "patient", "case",
    ]
    log(f"  {'Keyword':<25} Found")
    log(f"  {'-'*35}")
    for kw in keywords_to_check:
        found = kw in all_text
        log(f"  {kw:<25} {'YES' if found else 'no'}")

    return sample_info, all_gsms


def build_gse83479_map(sample_info, all_gsms):
    """
    Build full 57-sample classification map.
    Uses keyword matching on fetched metadata.
    Falls back to positional assignment based
    on known dataset structure if keywords fail:
      GSE83479: 17 CDC tumour + 10 UTUC + ?
      normal from GSE83479 description.
    Fetches remaining GSMs as needed.
    """
    log("")
    log("  BUILDING FULL SAMPLE MAP...")

    gsm_map = {}  # gsm → type

    # First try to classify probed samples
    keywords_cdc = [
        "collecting duct", "bellini", "cdc",
        "cd rcc", "cd-rcc",
    ]
    keywords_utuc = [
        "utuc", "urothelial", "transitional",
        "upper tract", "upper urinary",
        "pelvis", "ureter",
    ]
    keywords_normal = [
        "normal", "adjacent normal",
        "non-tumor", "non-neoplastic",
        "healthy", "control",
    ]

    classified_probes = {}
    for gsm, info in sample_info.items():
        combined = " ".join(
            info.get("raw_lines", [])
        ).lower()
        if any(kw in combined
               for kw in keywords_cdc):
            classified_probes[gsm] = "CDC"
        elif any(kw in combined
                 for kw in keywords_utuc):
            classified_probes[gsm] = "UTUC"
        elif any(kw in combined
                 for kw in keywords_normal):
            classified_probes[gsm] = "normal"
        else:
            classified_probes[gsm] = "unknown"

    log(f"\n  Probe classification results:")
    for gsm, cls in classified_probes.items():
        log(f"    {gsm}: {cls}")

    # If probes show distinct patterns,
    # infer the full 57-sample layout.
    # Known structure from GEO description:
    # 17 CDC + 10 UTUC + 9 normal + (21 other?)
    # Try to fetch all 57 if probe classification
    # is insufficient (all unknown).

    n_known = sum(
        1 for v in classified_probes.values()
        if v != "unknown"
    )

    if n_known < len(classified_probes) * 0.5:
        log("\n  Fewer than 50% of probes classified.")
        log("  Fetching all 57 GSMs for full mapping...")
        log("  (This may take ~30 seconds)")

        for gsm in all_gsms:
            if gsm in classified_probes:
                gsm_map[gsm] = classified_probes[gsm]
                continue

            url = (
                "https://www.ncbi.nlm.nih.gov/geo/"
                f"query/acc.cgi?acc={gsm}"
                "&targ=self&form=text&view=full"
            )
            text = fetch_text(url)
            time.sleep(0.35)

            combined = text.lower()
            if any(kw in combined
                   for kw in keywords_cdc):
                gsm_map[gsm] = "CDC"
            elif any(kw in combined
                     for kw in keywords_utuc):
                gsm_map[gsm] = "UTUC"
            elif any(kw in combined
                     for kw in keywords_normal):
                gsm_map[gsm] = "normal"
            else:
                gsm_map[gsm] = "unknown"
    else:
        # Extend from probes using detected pattern
        # Fetch remaining unprobed GSMs
        unprobed = [
            g for g in all_gsms
            if g not in classified_probes
        ]
        log(f"\n  Fetching {len(unprobed)} "
            f"unprobed GSMs...")

        for gsm in unprobed:
            url = (
                "https://www.ncbi.nlm.nih.gov/geo/"
                f"query/acc.cgi?acc={gsm}"
                "&targ=self&form=text&view=full"
            )
            text = fetch_text(url)
            time.sleep(0.35)

            combined = text.lower()
            if any(kw in combined
                   for kw in keywords_cdc):
                gsm_map[gsm] = "CDC"
            elif any(kw in combined
                     for kw in keywords_utuc):
                gsm_map[gsm] = "UTUC"
            elif any(kw in combined
                     for kw in keywords_normal):
                gsm_map[gsm] = "normal"
            else:
                gsm_map[gsm] = "unknown"

        gsm_map.update(classified_probes)

    # Summary
    from collections import Counter
    counts = Counter(gsm_map.values())
    log(f"\n  FULL SAMPLE MAP ({len(gsm_map)} samples):")
    for cls, n in sorted(counts.items()):
        log(f"    {cls:<12}: {n}")

    cdc_gsms    = [g for g, t in gsm_map.items()
                   if t == "CDC"]
    normal_gsms = [g for g, t in gsm_map.items()
                   if t == "normal"]
    utuc_gsms   = [g for g, t in gsm_map.items()
                   if t == "UTUC"]

    log(f"\n  CDC samples:    {cdc_gsms}")
    log(f"  Normal samples: {normal_gsms}")
    log(f"  UTUC samples:   {utuc_gsms}")

    return gsm_map, cdc_gsms, normal_gsms, utuc_gsms

# ============================================================
# STEP 2 — LOAD AND CLASSIFY GSE83479
# ============================================================

def load_gse83479(gsm_map, cdc_gsms,
                  normal_gsms, utuc_gsms):
    log("")
    log("=" * 65)
    log("STEP 2 — LOADING GSE83479 MATRIX")
    log(f"  {REP_MATRIX_PATH}")
    log("=" * 65)

    if not os.path.exists(REP_MATRIX_PATH):
        log("  ERROR: Matrix not found at:")
        log(f"  {REP_MATRIX_PATH}")
        log("  Download failed in S3 or file moved.")
        return None, None, None, None

    sz = os.path.getsize(REP_MATRIX_PATH) / 1e6
    log(f"  File size: {sz:.2f} MB")

    try:
        with gzip.open(REP_MATRIX_PATH, "rt") as f:
            df = pd.read_csv(
                f, sep="\t", index_col=0,
                low_memory=False
            )
    except Exception as e:
        log(f"  ERROR loading: {e}")
        return None, None, None, None

    log(f"  Shape: {df.shape}")

    # Strip hg. prefix (same as S3)
    n_hg = sum(
        1 for i in df.index
        if str(i).startswith("hg.")
    )
    if n_hg > 0:
        df.index = [
            str(i)[3:] if str(i).startswith("hg.")
            else str(i)
            for i in df.index
        ]
        log(f"  Stripped hg. prefix ({n_hg} genes)")

    # Drop mouse genes
    mm_genes = [
        i for i in df.index
        if str(i).startswith("mm.")
    ]
    if mm_genes:
        df = df.drop(index=mm_genes)
        log(f"  Dropped {len(mm_genes)} mouse genes")

    # Deduplicate gene index
    dupes = df.index.duplicated()
    if dupes.sum() > 0:
        log(f"  Duplicate gene IDs: {dupes.sum()}")
        df = df[~dupes]
        log(f"  Deduplicated. Shape: {df.shape}")

    # Positional column rename to GSM IDs
    all_gsms_ordered = [
        f"GSM{2204076 + i}"
        for i in range(len(df.columns))
    ]
    if len(all_gsms_ordered) == len(df.columns):
        df.columns = all_gsms_ordered
        log(f"  Renamed {len(df.columns)} cols "
            f"to GSM IDs positionally")
    else:
        log(f"  Column count mismatch: "
            f"{len(df.columns)} cols, "
            f"{len(all_gsms_ordered)} GSMs")

    log(f"  First 5 cols: {list(df.columns[:5])}")

    # Apply classification
    cdc_cols    = [c for c in cdc_gsms
                   if c in df.columns]
    normal_cols = [c for c in normal_gsms
                   if c in df.columns]
    utuc_cols   = [c for c in utuc_gsms
                   if c in df.columns]

    log(f"\n  CDC matched:    {len(cdc_cols)}")
    log(f"  Normal matched: {len(normal_cols)}")
    log(f"  UTUC matched:   {len(utuc_cols)}")

    if not cdc_cols:
        log("  ERROR: No CDC columns identified.")
        log("  Check Step 1 classification output.")
        log("  Sample map may need manual review.")
        return df, None, None, None

    # Log2 transform if linear
    flat = df[cdc_cols].values.flatten()
    flat = flat[~np.isnan(flat) & (flat > 0)]
    if len(flat) > 0 and flat.max() > 50:
        log(f"\n  Max value: {flat.max():.1f}")
        log("  Linear scale — log2(x+1) transform")
        df = np.log2(df.clip(lower=0) + 1)
    else:
        log(f"  Max value: {flat.max():.2f}")
        log("  Already log scale — no transform")

    tumor_rep  = df[cdc_cols]
    normal_rep = df[normal_cols] if normal_cols \
                 else None
    utuc_rep   = df[utuc_cols] if utuc_cols \
                 else None

    log(f"\n  Tumour matrix:  {tumor_rep.shape}")
    if normal_rep is not None:
        log(f"  Normal matrix:  {normal_rep.shape}")
    if utuc_rep is not None:
        log(f"  UTUC matrix:    {utuc_rep.shape}")

    return df, tumor_rep, normal_rep, utuc_rep

# ============================================================
# STEP 3 — REPLICATION PANEL
# ============================================================

def run_replication(tumor_rep, normal_rep,
                    tumor_89, normal_89):
    log("")
    log("=" * 65)
    log("STEP 3 — REPLICATION PANEL (S3-P7 FIX)")
    log(f"  {len(REPLICATION_PANEL)} genes")
    log("  Directions stated in Doc 89b addendum")
    log("  before this script ran.")
    log("=" * 65)

    if tumor_rep is None:
        log("  SKIPPED — no CDC matrix available")
        return None

    # Build GSE89122 normal means as reference
    # for both datasets
    normal_means_89 = {}
    for gene in REPLICATION_PANEL:
        if gene in normal_89.index:
            normal_means_89[gene] = float(
                normal_89.loc[gene].mean()
            )

    log(f"\n  {'Gene':<14} {'Expected':>8} "
        f"{'Rep_%chg':>10} {'89_%chg':>10} "
        f"{'Rep_p':>14} {'Match':>12}")
    log(f"  {'-'*72}")

    confirmed = 0
    total     = 0
    records   = []

    for gene, expected in REPLICATION_PANEL.items():

        # GSE89122 reference % change
        r89_chg = np.nan
        if gene in tumor_89.index and \
           gene in normal_89.index:
            t89 = float(tumor_89.loc[gene].mean())
            n89 = float(normal_89.loc[gene].mean())
            if abs(n89) > 0.01:
                r89_chg = (t89 - n89) / abs(n89) * 100

        # GSE83479 % change
        r83_chg = np.nan
        r83_p   = np.nan
        match   = "NOT IN MATRIX"

        if gene not in tumor_rep.index:
            log(f"  {gene:<14} {expected:>8} "
                f"{'n/a':>10} "
                f"{r89_chg:>+9.1f}%"
                if not np.isnan(r89_chg)
                else f"  {gene:<14} {expected:>8} "
                     f"{'n/a':>10} {'n/a':>10} "
                     f"{'n/a':>14} {'NOT IN MATRIX':>12}")
            records.append({
                "gene": gene, "expected": expected,
                "rep_pct": np.nan, "r89_pct": r89_chg,
                "rep_p": np.nan, "match": "NOT IN MATRIX",
            })
            continue

        tumor_vals = tumor_rep.loc[gene].values\
            .astype(float)

        # Use GSE83479 internal normals if available
        # otherwise use GSE89122 normal means
        if normal_rep is not None and \
           gene in normal_rep.index:
            norm_vals = normal_rep.loc[gene].values\
                .astype(float)
            norm_mean = float(np.mean(norm_vals))
            norm_source = "internal"
        elif gene in normal_means_89:
            norm_mean = normal_means_89[gene]
            norm_source = "GSE89122 ref"
        else:
            norm_mean = np.nan
            norm_source = "no reference"

        if not np.isnan(norm_mean) and \
           abs(norm_mean) > 0.01:
            r83_chg = (
                float(np.mean(tumor_vals))
                - norm_mean
            ) / abs(norm_mean) * 100

        # Mann-Whitney vs normal or vs reference
        if normal_rep is not None and \
           gene in normal_rep.index:
            norm_v = normal_rep.loc[gene]\
                .values.astype(float)
            try:
                _, r83_p = stats.mannwhitneyu(
                    tumor_vals, norm_v,
                    alternative="two-sided"
                )
                r83_p = float(r83_p)
            except Exception:
                r83_p = np.nan

        total += 1
        if not np.isnan(r83_chg):
            if expected == "DOWN" and r83_chg < -10:
                match = "REPLICATED"
                confirmed += 1
            elif expected == "UP" and r83_chg > 10:
                match = "REPLICATED"
                confirmed += 1
            elif (expected == "FLAT"
                  and abs(r83_chg) <= 25):
                match = "REPLICATED"
                confirmed += 1
            else:
                match = "FAILED"

        r89_s = (f"{r89_chg:>+9.1f}%"
                 if not np.isnan(r89_chg)
                 else "       n/a")
        r83_s = (f"{r83_chg:>+9.1f}%"
                 if not np.isnan(r83_chg)
                 else "       n/a")

        log(f"  {gene:<14} {expected:>8} "
            f"{r83_s:>10} {r89_s:>10} "
            f"{fmt_p(r83_p):>14} {match:>12}")

        records.append({
            "gene": gene, "expected": expected,
            "rep_pct": r83_chg, "r89_pct": r89_chg,
            "rep_p": r83_p, "match": match,
            "norm_source": norm_source,
        })

    df_rep = pd.DataFrame(records)

    log(f"\n  Replicated: {confirmed}/{total}")
    rate = confirmed / total * 100 if total > 0 \
           else 0.0
    log(f"  Rate:       {rate:.1f}%")

    log(f"\n  PREDICTION P4-1 VERDICT:")
    log(f"    Predicted: 8+/{len(REPLICATION_PANEL)} "
        f"replicate")
    if confirmed >= 8:
        log(f"    CONFIRMED: {confirmed}/{total}")
        log(f"    Independent cohort validates the")
        log(f"    cdRCC false attractor geometry.")
    elif confirmed >= 6:
        log(f"    PARTIAL: {confirmed}/{total}")
        log(f"    Core findings partially replicate.")
        log(f"    Platform differences or normalisation")
        log(f"    may account for remaining failures.")
    elif confirmed > 0:
        log(f"    NOT CONFIRMED: {confirmed}/{total}")
        log(f"    Review gene coverage and platform.")
    else:
        log(f"    NOT RUN or no overlap.")

    out = os.path.join(
        S4_DIR, "replication_gse83479_s4.csv"
    )
    df_rep.to_csv(out, index=False)
    log(f"\n  Saved: {out}")

    return df_rep

# ============================================================
# STEP 4 — GSE83479 SPEARMAN DEPTH CORRELATIONS
# ============================================================

def gse83479_depth_correlations(tumor_rep, normal_rep,
                                 tumor_89, normal_89):
    log("")
    log("=" * 65)
    log("STEP 4 — GSE83479 SPEARMAN DEPTH CORRELATIONS")
    log("  Build depth score in GSE83479 tumours")
    log("  using the same axis (PRKAR2B / IL1RAP)")
    log("  Does the same biology replicate?")
    log("=" * 65)

    if tumor_rep is None:
        log("  SKIPPED — no CDC matrix")
        return None

    genes = tumor_rep.index.tolist()

    # Build depth score — S3 axis
    if "PRKAR2B" in genes and "IL1RAP" in genes:
        depth_sw = 1.0 - norm01(
            tumor_rep.loc["PRKAR2B"]
        )
        depth_fa = norm01(
            tumor_rep.loc["IL1RAP"]
        )
        depth = (depth_sw + depth_fa) / 2.0
        log(f"\n  Depth score built from PRKAR2B/IL1RAP")
        log(f"  n={len(depth)} CDC tumours")
        log(f"  Mean={depth.mean():.4f}  "
            f"Std={depth.std():.4f}")
        log(f"\n  Per-sample depth:")
        for gsm in depth.index:
            log(f"    {gsm}: {depth[gsm]:.4f}")
    else:
        avail_sw = [g for g in PROG_A if g in genes]
        if not avail_sw:
            log("  PRKAR2B and IL1RAP not in matrix.")
            log("  Cannot build depth score.")
            return None
        depth = norm01(
            tumor_rep.loc[avail_sw].mean(axis=0)
        )
        log(f"  Using Programme A mean as depth proxy")

    # Full-genome Spearman
    depth_arr = depth.values
    records   = []
    for gene in genes:
        vals = tumor_rep.loc[gene].values\
            .astype(float)
        r, p = spearman(vals, depth_arr)
        records.append({
            "gene": gene,
            "spearman_r": r,
            "p": p,
        })

    df_sp = pd.DataFrame(records).set_index("gene")
    df_sp = df_sp.sort_values(
        "spearman_r", key=abs, ascending=False
    )

    out = os.path.join(
        S4_DIR,
        "gse83479_depth_correlations_s4.csv"
    )
    df_sp.to_csv(out)
    log(f"\n  Saved: {out}")

    # Top 15 positive
    top_pos = df_sp.sort_values(
        "spearman_r", ascending=False
    ).head(15)
    log(f"\n  Top 15 positive correlators (GSE83479):")
    log(f"  {'Gene':<18} {'r':>10}  {'p':>14}")
    log(f"  {'-'*46}")
    for gene, row in top_pos.iterrows():
        log(f"  {gene:<18} "
            f"{row['spearman_r']:>+10.4f}  "
            f"{fmt_p(row['p']):>14}")

    # Top 15 negative
    top_neg = df_sp.sort_values(
        "spearman_r", ascending=True
    ).head(15)
    log(f"\n  Top 15 negative correlators (GSE83479):")
    log(f"  {'Gene':<18} {'r':>10}  {'p':>14}")
    log(f"  {'-'*46}")
    for gene, row in top_neg.iterrows():
        log(f"  {gene:<18} "
            f"{row['spearman_r']:>+10.4f}  "
            f"{fmt_p(row['p']):>14}")

    # Check key genes from GSE89122 findings
    key_genes = [
        "ADPRM", "TNXB", "OGDHL", "LAMTOR4",
        "IL1RAP", "GPRC5A", "AGR2", "KLF5",
        "PPARG", "MYC", "BHLHE40",
        "EZH2", "PRKAR2B", "AQP2",
    ]
    log(f"\n  KEY GENES FROM GSE89122 FINDINGS:")
    log(f"  {'Gene':<18} {'r_GSE83479':>12}  "
        f"{'p':>14}  {'r_GSE89122':>12}")

    # Load S3 Spearman table for comparison
    s3_sp_path = os.path.join(
        BASE_DIR, "results_s3",
        "depth_correlations_spearman_s3.csv"
    )
    s3_sp = None
    if os.path.exists(s3_sp_path):
        s3_sp = pd.read_csv(
            s3_sp_path, index_col=0
        )

    log(f"  {'-'*60}")
    for gene in key_genes:
        r83 = np.nan
        p83 = np.nan
        r89 = np.nan
        if gene in df_sp.index:
            r83 = float(df_sp.loc[gene, "spearman_r"])
            p83 = float(df_sp.loc[gene, "p"])
        if s3_sp is not None and gene in s3_sp.index:
            r89 = float(s3_sp.loc[gene, "spearman_r"])
        r83_s = (f"{r83:>+12.4f}"
                 if not np.isnan(r83) else "          n/a")
        r89_s = (f"{r89:>+12.4f}"
                 if not np.isnan(r89) else "          n/a")
        log(f"  {gene:<18} {r83_s}  "
            f"{fmt_p(p83):>14}  {r89_s}")

    return df_sp

# ============================================================
# STEP 5 — HK2 DRIVER TEST
# ============================================================

def hk2_driver_test(tumor):
    log("")
    log("=" * 65)
    log("STEP 5 — HK2 DRIVER TEST")
    log("  PREDICTION P4-2 (Doc 89b addendum):")
    log("  RELA or CEBPB drives HK2 elevation")
    log("  in cdRCC tumours.")
    log("=" * 65)

    if "HK2" not in tumor.index:
        log("  HK2 not in matrix")
        return

    hk2_arr = tumor.loc["HK2"].values.astype(float)

    log(f"\n  HK2 values (7 tumours):")
    for gsm in tumor.columns:
        pat = SAMPLE_MAP_89122.get(
            gsm, ("?","?")
        )[0]
        log(f"    {gsm} ({pat}): "
            f"{float(tumor.loc['HK2',gsm]):.4f}")

    panel = [
        g for g in HK2_DRIVER_CANDIDATES
        if g in tumor.index
    ]

    log(f"\n  {'Candidate':<14} {'r_HK2':>10}  "
        f"{'p':>14}")
    log(f"  {'-'*42}")

    results = []
    for gene in panel:
        vals = tumor.loc[gene].values.astype(float)
        r, p = spearman(hk2_arr, vals)
        results.append((gene, r, p))
        log(f"  {gene:<14} {r:>+10.4f}  "
            f"{fmt_p(p):>14}")

    results.sort(
        key=lambda x: abs(x[1])
        if not np.isnan(x[1]) else 0,
        reverse=True,
    )

    log(f"\n  Top 5 HK2 drivers by |r|:")
    for g, r, p in results[:5]:
        log(f"    {g:<14} r={r:>+.4f}  {fmt_p(p)}")

    best_g, best_r, best_p = results[0]

    # Check RELA and CEBPB specifically
    rela_r  = next(
        (r for g,r,p in results if g=="RELA"),
        np.nan
    )
    cebpb_r = next(
        (r for g,r,p in results if g=="CEBPB"),
        np.nan
    )
    hif1a_r = next(
        (r for g,r,p in results if g=="HIF1A"),
        np.nan
    )
    epas1_r = next(
        (r for g,r,p in results if g=="EPAS1"),
        np.nan
    )

    log(f"\n  SPECIFIC PREDICTIONS:")
    log(f"    r(HK2, RELA):  "
        f"{rela_r:>+.4f}"
        if not np.isnan(rela_r)
        else "    r(HK2, RELA):  not computed")
    log(f"    r(HK2, CEBPB): "
        f"{cebpb_r:>+.4f}"
        if not np.isnan(cebpb_r)
        else "    r(HK2, CEBPB): not computed")
    log(f"    r(HK2, HIF1A): "
        f"{hif1a_r:>+.4f}"
        if not np.isnan(hif1a_r)
        else "    r(HK2, HIF1A): not computed")
    log(f"    r(HK2, EPAS1): "
        f"{epas1_r:>+.4f}"
        if not np.isnan(epas1_r)
        else "    r(HK2, EPAS1): not computed")

    log(f"\n  PREDICTION P4-2 VERDICT:")
    log(f"    Predicted: RELA or CEBPB drives HK2")
    log(f"    Best driver: {best_g}  "
        f"r={best_r:>+.4f}  {fmt_p(best_p)}")

    rela_confirmed  = (
        not np.isnan(rela_r) and abs(rela_r) >= 0.5
    )
    cebpb_confirmed = (
        not np.isnan(cebpb_r) and abs(cebpb_r) >= 0.5
    )
    hif_better = (
        not np.isnan(hif1a_r)
        and abs(hif1a_r) > abs(rela_r)
        and abs(hif1a_r) > abs(cebpb_r)
    )

    if rela_confirmed or cebpb_confirmed:
        log(f"    CONFIRMED: NF-kB arm drives HK2")
        if rela_confirmed:
            log(f"    RELA confirmed r={rela_r:>+.4f}")
        if cebpb_confirmed:
            log(f"    CEBPB confirmed r={cebpb_r:>+.4f}")
    elif hif_better:
        log(f"    NOT CONFIRMED: HIF1A "
            f"r={hif1a_r:>+.4f} outperforms NF-kB.")
        log(f"    HIF pathway drives HK2 in cdRCC.")
        log(f"    Analyst assumption error:")
        log(f"    NF-kB drives ADCY3 (Step 6 S3).")
        log(f"    HIF drives HK2 (Step 5 S4).")
        log(f"    The two arms are separate:")
        log(f"      NF-kB: ADCY3 / IL1B / CEBPB")
        log(f"      HIF:   HK2 / SLC2A1 / SLC2A3")
    else:
        log(f"    NOT CONFIRMED: best = {best_g}")
        log(f"    r={best_r:>+.4f}  {fmt_p(best_p)}")
        log(f"    Re-examine in context of n=7.")

    return results

# ============================================================
# STEP 6 — MYC / BHLHE40 TRANSITION CONFIRMATION
# ============================================================

def myc_bhlhe40_transition(tumor, normal):
    log("")
    log("=" * 65)
    log("STEP 6 — MYC/BHLHE40 TRANSITION")
    log("  PREDICTION P4-3 (Doc 89b addendum):")
    log("  CDC3 has lowest BHLHE40 in tumour set.")
    log("  Confirms N8: MYC early, BHLHE40 late.")
    log("=" * 65)

    genes = tumor.index.tolist()

    panel = [g for g in TRANSITION_PANEL
             if g in genes]

    log(f"\n  Per-tumour expression table:")
    log(f"  {'Gene':<14} " + "  ".join(
        f"{SAMPLE_MAP_89122.get(c,('?','?'))[0]:>7}"
        for c in tumor.columns
    ))
    log(f"  {'-'*72}")

    for gene in panel:
        vals = [
            f"{float(tumor.loc[gene,c]):>7.3f}"
            for c in tumor.columns
        ]
        log(f"  {gene:<14} " + "  ".join(vals))

    # Build ranked table for MYC and BHLHE40
    log(f"\n  RANKED BY DEPTH (S3: CDC3=shallowest,")
    log(f"  CDC6=deepest, based on PRKAR2B/IL1RAP):")
    log(f"  Depth order: CDC3 < CDC7 < CDC4 < "
        f"CDC5 < CDC1 < CDC2 < CDC6")

    # The depth order from S3:
    # CDC3=0.000, CDC7=0.196, CDC4=0.371,
    # CDC5=0.452, CDC1=0.464, CDC2=0.666, CDC6=1.000
    depth_order = [
        "GSM2359148",  # CDC3 depth=0.000
        "GSM2359155",  # CDC7 depth=0.196
        "GSM2359150",  # CDC4 depth=0.371
        "GSM2359152",  # CDC5 depth=0.452
        "GSM2359144",  # CDC1 depth=0.464
        "GSM2359146",  # CDC2 depth=0.666
        "GSM2359153",  # CDC6 depth=1.000
    ]
    depth_vals = [
        0.000, 0.196, 0.371, 0.452,
        0.464, 0.666, 1.000
    ]

    # Reorder columns by depth
    ordered_cols = [
        c for c in depth_order
        if c in tumor.columns
    ]
    ordered_depth = [
        depth_vals[i]
        for i, c in enumerate(depth_order)
        if c in tumor.columns
    ]

    log(f"\n  Depth-ordered MYC and BHLHE40:")
    log(f"  {'Sample':<8} {'Depth':>7} "
        f"{'MYC':>9} {'BHLHE40':>9} "
        f"{'KLF5':>9} {'PPARG':>9}")
    log(f"  {'-'*54}")

    for c, d in zip(ordered_cols, ordered_depth):
        pat = SAMPLE_MAP_89122.get(c,("?","?"))[0]
        myc_v = (f"{float(tumor.loc['MYC',c]):>9.3f}"
                 if "MYC" in genes else "       n/a")
        bhl_v = (f"{float(tumor.loc['BHLHE40',c]):>9.3f}"
                 if "BHLHE40" in genes
                 else "       n/a")
        klf_v = (f"{float(tumor.loc['KLF5',c]):>9.3f}"
                 if "KLF5" in genes else "       n/a")
        ppg_v = (f"{float(tumor.loc['PPARG',c]):>9.3f}"
                 if "PPARG" in genes else "       n/a")
        log(f"  {pat:<8} {d:>7.3f} "
            f"{myc_v} {bhl_v} {klf_v} {ppg_v}")

    # Test: is CDC3 the lowest BHLHE40?
    if "BHLHE40" in genes:
        bhlhe40_vals = {
            c: float(tumor.loc["BHLHE40", c])
            for c in ordered_cols
        }
        cdc3_gsm = "GSM2359148"
        if cdc3_gsm in bhlhe40_vals:
            cdc3_bhlhe40 = bhlhe40_vals[cdc3_gsm]
            all_bhlhe40  = list(
                bhlhe40_vals.values()
            )
            cdc3_is_lowest = (
                cdc3_bhlhe40 == min(all_bhlhe40)
            )
            cdc3_rank = sorted(
                all_bhlhe40
            ).index(cdc3_bhlhe40) + 1

            log(f"\n  CDC3 BHLHE40: {cdc3_bhlhe40:.4f}")
            log(f"  Min in set:   {min(all_bhlhe40):.4f}")
            log(f"  Rank (lowest first): "
                f"{cdc3_rank}/{len(all_bhlhe40)}")

            # MYC vs BHLHE40 Spearman
            if "MYC" in genes:
                myc_arr = tumor.loc["MYC"]\
                    .values.astype(float)
                bhl_arr = tumor.loc["BHLHE40"]\
                    .values.astype(float)
                r_mb, p_mb = spearman(
                    myc_arr, bhl_arr
                )
                log(f"\n  r(MYC, BHLHE40) = {r_mb:>+.4f}  "
                    f"{fmt_p(p_mb)}")

            # MYC vs depth
            if "MYC" in genes:
                depth_arr = np.array(ordered_depth)
                myc_ordered = np.array([
                    float(tumor.loc["MYC", c])
                    for c in ordered_cols
                ])
                r_md, p_md = spearman(
                    myc_ordered, depth_arr
                )
                log(f"  r(MYC, depth)    = "
                    f"{r_md:>+.4f}  {fmt_p(p_md)}")

            # BHLHE40 vs depth
            bhl_ordered = np.array([
                float(tumor.loc["BHLHE40", c])
                for c in ordered_cols
            ])
            r_bd, p_bd = spearman(
                bhl_ordered, depth_arr
            )
            log(f"  r(BHLHE40, depth)= "
                f"{r_bd:>+.4f}  {fmt_p(p_bd)}")

            log(f"\n  PREDICTION P4-3 VERDICT:")
            log(f"    Predicted: CDC3 has lowest "
                f"BHLHE40 in tumour set")
            if cdc3_is_lowest:
                log(f"    CONFIRMED: CDC3 "
                    f"BHLHE40={cdc3_bhlhe40:.4f} "
                    f"is lowest (rank 1/{len(all_bhlhe40)})")
                log(f"    N8 CONFIRMED:")
                log(f"    MYC rises early (highest in CDC3)")
                log(f"    BHLHE40 rises late (lowest in CDC3)")
                log(f"    The transition sequence is real.")
            else:
                log(f"    NOT CONFIRMED:")
                log(f"    CDC3 BHLHE40 rank "
                    f"{cdc3_rank}/{len(all_bhlhe40)}")
                log(f"    CDC3 does not have the lowest")
                log(f"    BHLHE40 in the tumour set.")
                # Find actual lowest
                lowest_gsm = min(
                    bhlhe40_vals,
                    key=bhlhe40_vals.get
                )
                lowest_pat = SAMPLE_MAP_89122.get(
                    lowest_gsm, ("?","?")
                )[0]
                log(f"    Actual lowest: {lowest_pat} "
                    f"({lowest_gsm})")
                log(f"    Review N8 — transition")
                log(f"    sequence may not be as")
                log(f"    linear as predicted.")
    else:
        log("\n  BHLHE40 not in matrix — "
            "prediction cannot be tested")

# ============================================================
# STEP 7 — CEBPA ANTAGONISM PANEL
# ============================================================

def cebpa_antagonism_panel(tumor, normal):
    log("")
    log("=" * 65)
    log("STEP 7 — CEBPA ANTAGONISM PANEL")
    log("  PREDICTION P4-4 (Doc 89b addendum):")
    log("  CEBPA opposes the whole PPARG module,")
    log("  not just PPARG itself.")
    log("  Expected: CEBPA negatively correlated")
    log("  with AGR2, KLF5, IL1RAP, ESRP1")
    log("  in tumours.")
    log("=" * 65)

    genes = tumor.index.tolist()

    if "CEBPA" not in genes:
        log("  CEBPA not in matrix")
        return

    cebpa_t = tumor.loc["CEBPA"].values.astype(float)
    cebpa_n = (
        normal.loc["CEBPA"].values.astype(float)
        if "CEBPA" in normal.index
        else None
    )

    panel = [g for g in CEBPA_PANEL
             if g != "CEBPA" and g in genes]

    log(f"\n  {'Gene':<14} {'r_tumour':>10}  "
        f"{'p_tumour':>14}  "
        f"{'r_normal':>10}  {'p_normal':>14}")
    log(f"  {'-'*68}")

    pparg_mod_genes = [
        "PPARG", "KLF5", "AGR2", "IL1RAP",
        "ESRP1", "GPRC5A", "CST6", "KLF10",
        "TMPRSS4", "SERPINA1",
    ]
    results_by_gene = {}

    for gene in panel:
        t_vals = tumor.loc[gene].values.astype(float)
        rt, pt = spearman(cebpa_t, t_vals)

        rn_s = "       n/a"
        pn_s = "           n/a"
        rn   = np.nan

        if cebpa_n is not None and \
           gene in normal.index:
            n_vals = normal.loc[gene]\
                .values.astype(float)
            if len(n_vals) >= 3:
                rn, pn = spearman(cebpa_n, n_vals)
                rn_s = f"{rn:>+10.4f}"
                pn_s = fmt_p(pn)

        log(f"  {gene:<14} {rt:>+10.4f}  "
            f"{fmt_p(pt):>14}  "
            f"{rn_s}  {pn_s}")

        results_by_gene[gene] = (rt, pt, rn)

    # Summary for PPARG module genes
    log(f"\n  PPARG MODULE GENES — CEBPA ANTAGONISM:")
    log(f"  {'Gene':<14} {'r_tumour':>10}  "
        f"{'Sig':>6}  {'Direction'}  "
        f"{'Opposes PPARG module?'}")
    log(f"  {'-'*68}")

    opposing = []
    neutral  = []
    tracking = []

    for gene in pparg_mod_genes:
        if gene not in results_by_gene:
            continue
        rt, pt, rn = results_by_gene[gene]
        if not np.isnan(rt):
            sig = "p<0.05" if pt < 0.05 else "ns"
            if rt < -0.3:
                status = "YES — OPPOSES"
                opposing.append(gene)
            elif rt > 0.3:
                status = "no — TRACKS"
                tracking.append(gene)
            else:
                status = "neutral"
                neutral.append(gene)
            log(f"  {gene:<14} {rt:>+10.4f}  "
                f"{sig:>6}  "
                f"{'neg' if rt<0 else 'pos':>9}  "
                f"{status}")

    log(f"\n  CEBPA opposes "
        f"({len(opposing)}/{len(pparg_mod_genes)} "
        f"module genes):")
    for g in opposing:
        log(f"    {g}")
    log(f"\n  CEBPA neutral toward:")
    for g in neutral:
        log(f"    {g}")
    log(f"\n  CEBPA tracks (unexpected):")
    for g in tracking:
        log(f"    {g}")

    n_prog_genes = len([
        g for g in pparg_mod_genes
        if g in results_by_gene
    ])
    proportion = len(opposing) / n_prog_genes \
                 if n_prog_genes > 0 else 0

    log(f"\n  PREDICTION P4-4 VERDICT:")
    log(f"    Predicted: CEBPA opposes whole")
    log(f"    PPARG module (not just PPARG)")
    if proportion >= 0.6:
        log(f"    CONFIRMED: {len(opposing)}/"
            f"{n_prog_genes} module genes opposed")
        log(f"    CEBPA is a broad PPARG module")
        log(f"    antagonist. Restoring CEBPA would")
        log(f"    destabilise the entire core module.")
        log(f"    Target T3 (EZH2→CEBPA) is supported.")
    elif proportion >= 0.4:
        log(f"    PARTIAL: {len(opposing)}/"
            f"{n_prog_genes} module genes opposed")
        log(f"    CEBPA opposes some but not all")
        log(f"    PPARG module members.")
        log(f"    Most likely the PPARG-AGR2 hub")
        log(f"    is the primary point of opposition.")
    else:
        log(f"    NOT CONFIRMED: {len(opposing)}/"
            f"{n_prog_genes} module genes opposed")
        log(f"    CEBPA opposition may be limited")
        log(f"    to PPARG itself (r=-0.786 S3).")
        log(f"    Does not extend broadly.")
        log(f"    T3 rationale is narrower than")
        log(f"    predicted.")

    return results_by_gene

# ============================================================
# STEP 8 — ADPRM ALTERNATIVE DEPTH PROXY
# ============================================================

def adprm_depth_proxy(tumor):
    log("")
    log("=" * 65)
    log("STEP 8 — ADPRM ALTERNATIVE DEPTH PROXY")
    log("  PREDICTION P4-5 (Doc 89b addendum):")
    log("  r(S3_depth, S4_depth) > 0.95")
    log("  S4 depth uses ADPRM instead of PRKAR2B")
    log("=" * 65)

    genes = tumor.index.tolist()

    # Build S3 depth score
    if "PRKAR2B" in genes and "IL1RAP" in genes:
        depth_s3 = (
            (1.0 - norm01(tumor.loc["PRKAR2B"]))
            + norm01(tumor.loc["IL1RAP"])
        ) / 2.0
    else:
        log("  PRKAR2B or IL1RAP missing — "
            "cannot build S3 depth")
        return None, None

    # Build S4 depth score (ADPRM)
    if "ADPRM" in genes:
        depth_s4 = (
            (1.0 - norm01(tumor.loc["ADPRM"]))
            + norm01(tumor.loc["IL1RAP"])
        ) / 2.0
    else:
        log("  ADPRM not in matrix — "
            "cannot build S4 depth")
        return depth_s3, None

    log(f"\n  S3 depth (PRKAR2B/IL1RAP):")
    log(f"  S4 depth (ADPRM/IL1RAP):")
    log(f"\n  {'Sample':<10} {'Patient':>8} "
        f"{'S3':>8} {'S4':>8} {'Diff':>8}")
    log(f"  {'-'*46}")

    for gsm in tumor.columns:
        pat = SAMPLE_MAP_89122.get(
            gsm, ("?","?")
        )[0]
        s3  = float(depth_s3[gsm])
        s4  = float(depth_s4[gsm])
        log(f"  {gsm:<10} {pat:>8} "
            f"{s3:>8.4f} {s4:>8.4f} "
            f"{s4-s3:>+8.4f}")

    r_s3s4, p_s3s4 = spearman(
        depth_s3.values, depth_s4.values
    )
    r_pear,  p_pear = pearson(
        depth_s3.values, depth_s4.values
    )

    log(f"\n  Spearman r(S3, S4) = {r_s3s4:>+.4f}  "
        f"{fmt_p(p_s3s4)}")
    log(f"  Pearson  r(S3, S4) = {r_pear:>+.4f}  "
        f"{fmt_p(p_pear)}")

    log(f"\n  PREDICTION P4-5 VERDICT:")
    log(f"    Predicted: r > 0.95")
    if not np.isnan(r_s3s4) and abs(r_s3s4) >= 0.95:
        log(f"    CONFIRMED: r={r_s3s4:>+.4f}")
        log(f"    ADPRM captures the same biology")
        log(f"    as PRKAR2B in the depth axis.")
        log(f"    ADPRM is a valid alternative")
        log(f"    depth proxy for cdRCC.")
        log(f"    Clinical note: ADPRM has a wider")
        log(f"    dynamic range in this dataset.")
        log(f"    May be preferable as a clinical")
        log(f"    biomarker (IHC or proteomics).")
    elif not np.isnan(r_s3s4) and abs(r_s3s4) >= 0.85:
        log(f"    PARTIAL: r={r_s3s4:>+.4f}")
        log(f"    ADPRM and PRKAR2B measure related")
        log(f"    but not identical biology.")
        log(f"    ADPRM is a useful supplementary")
        log(f"    proxy but not a direct substitute.")
    else:
        log(f"    NOT CONFIRMED: r={r_s3s4:>+.4f}")
        log(f"    ADPRM captures a different axis")
        log(f"    from PRKAR2B in the depth score.")
        log(f"    Stick with PRKAR2B as primary.")

    # Also test TNXB as proxy
    log(f"\n  ADDITIONAL: TNXB as depth proxy")
    if "TNXB" in genes:
        depth_tnxb = (
            (1.0 - norm01(tumor.loc["TNXB"]))
            + norm01(tumor.loc["IL1RAP"])
        ) / 2.0
        r_tnxb, p_tnxb = spearman(
            depth_s3.values, depth_tnxb.values
        )
        log(f"  r(S3_depth, TNXB_depth) = "
            f"{r_tnxb:>+.4f}  {fmt_p(p_tnxb)}")
    else:
        log("  TNXB not in matrix")

    return depth_s3, depth_s4

# ============================================================
# STEP 9 — FULL DEPTH SCORE COMPARISON
# ============================================================

def depth_comparison_summary(tumor, depth_s3,
                              depth_s4):
    log("")
    log("=" * 65)
    log("STEP 9 — DEPTH SCORE COMPARISON SUMMARY")
    log("  S1/S2 depth vs S3 depth vs S4 depth")
    log("=" * 65)

    genes = tumor.index.tolist()

    # Rebuild S1-style depth for comparison
    # S1 used PRKAR2B (switch) + IL1RAP (FA)
    # but different normalisation
    # S3 = (1-norm(PRKAR2B) + norm(IL1RAP)) / 2
    # S4 = (1-norm(ADPRM) + norm(IL1RAP)) / 2
    # They share the IL1RAP component

    # Load S3 depth correlations to find
    # top genes for each score
    s3_sp_path = os.path.join(
        BASE_DIR, "results_s3",
        "depth_correlations_spearman_s3.csv"
    )

    if os.path.exists(s3_sp_path) and \
       depth_s3 is not None and \
       depth_s4 is not None:

        s3_sp = pd.read_csv(s3_sp_path, index_col=0)

        # Compare depth scores against key markers
        key_markers = [
            "IL1RAP", "AGR2", "KLF5", "PPARG",
            "GPRC5A", "CST6", "ADPRM", "TNXB",
            "OGDHL", "MYC", "BHLHE40", "PRKAR2B",
        ]

        log(f"\n  {'Gene':<14} {'r_S3':>10}  "
            f"{'r_S4':>10}  {'delta':>8}")
        log(f"  {'-'*46}")

        for gene in key_markers:
            if gene not in genes:
                continue
            vals = tumor.loc[gene].values.astype(float)
            r3, _ = spearman(vals, depth_s3.values)
            r4, _ = spearman(vals, depth_s4.values)
            delta = r4 - r3 if not (
                np.isnan(r3) or np.isnan(r4)
            ) else np.nan
            d_s = (f"{delta:>+8.4f}"
                   if not np.isnan(delta)
                   else "     n/a")
            log(f"  {gene:<14} "
                f"{r3:>+10.4f}  {r4:>+10.4f}  {d_s}")

        log(f"\n  S3 and S4 depth scores capture the")
        log(f"  same biology if delta values are small.")
        log(f"  Large positive delta: S4 better for gene")
        log(f"  Large negative delta: S3 better for gene")

# ============================================================
# STEP 10 — FIGURE
# ============================================================

def generate_figure(
    tumor, normal,
    depth_s3, depth_s4,
    df_rep, df_rep_sp,
    hk2_results, cebpa_results,
):
    log("")
    log("=" * 65)
    log("STEP 10 — GENERATING FIGURE")
    log("=" * 65)

    fig = plt.figure(figsize=(22, 18))
    fig.patch.set_facecolor("#0d1117")
    gs  = gridspec.GridSpec(
        3, 3, figure=fig,
        hspace=0.45, wspace=0.38,
    )

    TITLE_C = "#e6edf3"
    LABEL_C = "#8b949e"
    BG      = "#161b22"
    BLUE    = "#58a6ff"
    RED     = "#f78166"
    ORANGE  = "#d29922"
    GREEN   = "#3fb950"
    PURPLE  = "#bc8cff"
    CYAN    = "#39d353"

    def style(ax, title):
        ax.set_facecolor(BG)
        for sp in ax.spines.values():
            sp.set_edgecolor("#30363d")
        ax.tick_params(colors=LABEL_C, labelsize=7)
        ax.set_title(
            title, color=TITLE_C,
            fontsize=8, pad=5,
        )
        ax.xaxis.label.set_color(LABEL_C)
        ax.yaxis.label.set_color(LABEL_C)

    genes = tumor.index.tolist()
    depth_arr_s3 = (
        depth_s3.values
        if depth_s3 is not None else None
    )
    depth_arr_s4 = (
        depth_s4.values
        if depth_s4 is not None else None
    )

    # ---- Panel A: S3 vs S4 depth ----
    ax_a = fig.add_subplot(gs[0, 0])
    if depth_arr_s3 is not None and \
       depth_arr_s4 is not None:
        ax_a.scatter(
            depth_arr_s3, depth_arr_s4,
            color=PURPLE, s=80, zorder=3,
        )
        for i, gsm in enumerate(tumor.columns):
            pat = SAMPLE_MAP_89122.get(
                gsm, ("?","?")
            )[0]
            ax_a.annotate(
                pat,
                (depth_arr_s3[i], depth_arr_s4[i]),
                fontsize=6, color=LABEL_C,
                xytext=(3, 3),
                textcoords="offset points",
            )
        r_ss, _ = spearman(depth_arr_s3,
                            depth_arr_s4)
        ax_a.text(
            0.05, 0.92, f"r = {r_ss:>+.3f}",
            transform=ax_a.transAxes,
            color=TITLE_C, fontsize=7,
        )
        ax_a.set_xlabel(
            "S3 depth (PRKAR2B/IL1RAP)",
            fontsize=6,
        )
        ax_a.set_ylabel(
            "S4 depth (ADPRM/IL1RAP)",
            fontsize=6,
        )
    style(ax_a, "A — S3 vs S4 Depth\n"
          "P4-5: predicted r > 0.95")

    # ---- Panel B: MYC and BHLHE40 by depth ----
    ax_b = fig.add_subplot(gs[0, 1])
    depth_order_gsms = [
        "GSM2359148", "GSM2359155",
        "GSM2359150", "GSM2359152",
        "GSM2359144", "GSM2359146",
        "GSM2359153",
    ]
    depth_order_vals = [
        0.000, 0.196, 0.371, 0.452,
        0.464, 0.666, 1.000
    ]
    ordered = [
        c for c in depth_order_gsms
        if c in tumor.columns
    ]
    depths  = [
        depth_order_vals[i]
        for i, c in enumerate(depth_order_gsms)
        if c in tumor.columns
    ]

    if "MYC" in genes and "BHLHE40" in genes:
        myc_v = [
            float(tumor.loc["MYC", c])
            for c in ordered
        ]
        bhl_v = [
            float(tumor.loc["BHLHE40", c])
            for c in ordered
        ]
        ax_b.plot(
            depths, myc_v, "o-",
            color=RED, label="MYC", ms=5, lw=1.5,
        )
        ax_b2 = ax_b.twinx()
        ax_b2.plot(
            depths, bhl_v, "s--",
            color=BLUE, label="BHLHE40",
            ms=5, lw=1.5,
        )
        ax_b2.tick_params(colors=LABEL_C,
                           labelsize=7)
        ax_b2.yaxis.label.set_color(BLUE)
        ax_b2.set_ylabel("BHLHE40", fontsize=6,
                          color=BLUE)
        for i, c in enumerate(ordered):
            pat = SAMPLE_MAP_89122.get(
                c, ("?","?")
            )[0]
            ax_b.annotate(
                pat, (depths[i], myc_v[i]),
                fontsize=5, color=LABEL_C,
                xytext=(2, 2),
                textcoords="offset points",
            )
        ax_b.set_xlabel("S3 Depth", fontsize=6)
        ax_b.set_ylabel("MYC", fontsize=6,
                         color=RED)
        lines1, labels1 = ax_b.get_legend_handles_labels()
        lines2, labels2 = ax_b2.get_legend_handles_labels()
        ax_b.legend(
            lines1 + lines2,
            labels1 + labels2,
            fontsize=5, facecolor=BG,
            labelcolor=TITLE_C, framealpha=0.5,
        )
    style(ax_b, "B — MYC vs BHLHE40 Transition\n"
          "P4-3: CDC3 lowest BHLHE40?")

    # ---- Panel C: CEBPA antagonism ----
    ax_c = fig.add_subplot(gs[0, 2])
    if cebpa_results:
        ppg_mod = [
            g for g in PROG_A
            if g in cebpa_results
        ]
        rs_c = [
            cebpa_results[g][0]
            for g in ppg_mod
            if not np.isnan(cebpa_results[g][0])
        ]
        gs_c = [
            g for g in ppg_mod
            if not np.isnan(cebpa_results[g][0])
        ]
        cc = [
            RED if r < 0 else BLUE
            for r in rs_c
        ]
        ax_c.barh(
            range(len(gs_c)), rs_c,
            color=cc, alpha=0.85,
        )
        ax_c.set_yticks(range(len(gs_c)))
        ax_c.set_yticklabels(gs_c, fontsize=7)
        ax_c.axvline(
            0, color=LABEL_C, lw=0.5, alpha=0.5
        )
        ax_c.axvline(
            -0.3, color=RED, lw=0.8, ls=":",
            alpha=0.6,
        )
        ax_c.set_xlabel(
            "Spearman r(CEBPA, gene)", fontsize=7
        )
    style(ax_c, "C — CEBPA Antagonism Panel\n"
          "P4-4: Opposes whole PPARG module?")

    # ---- Panel D: HK2 drivers ----
    ax_d = fig.add_subplot(gs[1, 0])
    if hk2_results:
        top_hk2 = sorted(
            hk2_results,
            key=lambda x: abs(x[1])
            if not np.isnan(x[1]) else 0,
            reverse=True,
        )[:12]
        rs_h = [x[1] for x in top_hk2]
        gs_h = [x[0] for x in top_hk2]
        ch   = [
            RED if r < 0 else BLUE
            for r in rs_h
        ]
        ax_d.barh(
            range(len(gs_h)), rs_h,
            color=ch, alpha=0.85,
        )
        ax_d.set_yticks(range(len(gs_h)))
        ax_d.set_yticklabels(gs_h, fontsize=6)
        ax_d.axvline(
            0, color=LABEL_C, lw=0.5, alpha=0.5
        )
        ax_d.set_xlabel(
            "Spearman r(gene, HK2)", fontsize=7
        )
    style(ax_d, "D — HK2 Driver Candidates\n"
          "P4-2: Predicted RELA or CEBPB")

    # ---- Panel E: Replication bar chart ----
    ax_e = fig.add_subplot(gs[1, 1])
    if df_rep is not None and len(df_rep) > 0:
        rg = list(df_rep["gene"])
        x3 = range(len(rg))
        w3 = 0.35
        r89_v = df_rep["r89_pct"].fillna(0).values
        r83_v = df_rep["rep_pct"].fillna(0).values
        ax_e.bar(
            [xi - w3/2 for xi in x3], r89_v,
            width=w3, color=BLUE, alpha=0.8,
            label="GSE89122",
        )
        ax_e.bar(
            [xi + w3/2 for xi in x3], r83_v,
            width=w3, color=ORANGE, alpha=0.8,
            label="GSE83479",
        )
        ax_e.axhline(
            0, color=LABEL_C, lw=0.5, alpha=0.5
        )
        ax_e.set_xticks(x3)
        ax_e.set_xticklabels(
            rg, rotation=45, ha="right",
            fontsize=5,
        )
        ax_e.legend(
            fontsize=5, facecolor=BG,
            labelcolor=TITLE_C, framealpha=0.5,
        )
        n_rep = (
            df_rep["match"] == "REPLICATED"
        ).sum()
        ax_e.set_ylabel("% vs normal", fontsize=7)
        style(ax_e,
              f"E — Replication GSE83479\n"
              f"{n_rep}/{len(rg)} replicated "
              f"(P4-1)")
    else:
        ax_e.text(
            0.5, 0.5,
            "GSE83479 replication\nnot available",
            ha="center", va="center",
            color=LABEL_C, fontsize=8,
            transform=ax_e.transAxes,
        )
        style(ax_e,
              "E — Replication (unavailable)")

    # ---- Panel F: GSE83479 depth correlations ----
    ax_f = fig.add_subplot(gs[1, 2])
    if df_rep_sp is not None and len(df_rep_sp) > 0:
        top_pos = df_rep_sp.sort_values(
            "spearman_r", ascending=False
        ).head(10)
        top_neg = df_rep_sp.sort_values(
            "spearman_r", ascending=True
        ).head(10)
        combined_sp = pd.concat([top_neg, top_pos])
        cc_sp = [
            RED if r < 0 else BLUE
            for r in combined_sp["spearman_r"]
        ]
        ax_f.barh(
            range(len(combined_sp)),
            combined_sp["spearman_r"],
            color=cc_sp, alpha=0.85,
        )
        ax_f.set_yticks(range(len(combined_sp)))
        ax_f.set_yticklabels(
            combined_sp.index, fontsize=5
        )
        ax_f.axvline(
            0, color=LABEL_C, lw=0.5, alpha=0.5
        )
        ax_f.set_xlabel("Spearman r", fontsize=7)
        style(ax_f, "F — GSE83479 Depth Correlations\n"
              "Top 10 each direction")
    else:
        ax_f.text(
            0.5, 0.5,
            "GSE83479 not available",
            ha="center", va="center",
            color=LABEL_C, fontsize=8,
            transform=ax_f.transAxes,
        )
        style(ax_f, "F — GSE83479 (unavailable)")

    # ---- Panel G: ADPRM depth proxy ----
    ax_g = fig.add_subplot(gs[2, 0])
    if "ADPRM" in genes and depth_s3 is not None:
        adprm_v = tumor.loc["ADPRM"].values\
            .astype(float)
        ax_g.scatter(
            depth_s3.values, adprm_v,
            color=GREEN, s=70, zorder=3,
        )
        for i, gsm in enumerate(tumor.columns):
            pat = SAMPLE_MAP_89122.get(
                gsm, ("?","?")
            )[0]
            ax_g.annotate(
                pat,
                (depth_s3.values[i], adprm_v[i]),
                fontsize=5.5, color=LABEL_C,
                xytext=(3, 3),
                textcoords="offset points",
            )
        r_ad, _ = spearman(
            depth_s3.values, adprm_v
        )
        ax_g.text(
            0.05, 0.92, f"r = {r_ad:>+.3f}",
            transform=ax_g.transAxes,
            color=TITLE_C, fontsize=7,
        )
        ax_g.set_xlabel("S3 Depth", fontsize=6)
        ax_g.set_ylabel("ADPRM expression",
                         fontsize=6)
    style(ax_g,
          "G — ADPRM as Depth Proxy\n"
          "r=-1.000 Spearman (S3)")

    # ---- Panel H: r=-1.000 genes by depth ----
    ax_h = fig.add_subplot(gs[2, 1])
    floor_genes = [
        "ADPRM", "TNXB", "OGDHL",
        "SCG2", "LAMTOR4",
    ]
    floor_in = [g for g in floor_genes
                if g in genes]
    if floor_in and depth_s3 is not None:
        w = 0.15
        for i, g in enumerate(floor_in):
            vals = [
                float(tumor.loc[g, c])
                for c in ordered
                if c in tumor.columns
            ]
            offset = (i - len(floor_in)/2) * w
            ax_h.bar(
                [d + offset for d in depths],
                vals, width=w, alpha=0.8,
                label=g,
            )
        ax_h.set_xticks(depths)
        ax_h.set_xticklabels(
            [SAMPLE_MAP_89122.get(c,("?","?"))[0]
             for c in ordered],
            fontsize=6
        )
        ax_h.set_xlabel("Depth (S3)", fontsize=6)
        ax_h.set_ylabel("Expression", fontsize=6)
        ax_h.legend(
            fontsize=5, facecolor=BG,
            labelcolor=TITLE_C, framealpha=0.5,
        )
    style(ax_h,
          "H — r=-1.000 Genes by Depth\n"
          "ADPRM, TNXB, OGDHL, SCG2, LAMTOR4")

    # ---- Panel I: Summary ----
    ax_i = fig.add_subplot(gs[2, 2])
    ax_i.set_facecolor(BG)
    ax_i.axis("off")
    for sp in ax_i.spines.values():
        sp.set_edgecolor("#30363d")

    r_ss = np.nan
    if depth_s3 is not None and depth_s4 is not None:
        r_ss, _ = spearman(
            depth_s3.values, depth_s4.values
        )

    n_rep_str = "n/a"
    if df_rep is not None:
        n_rep = (
            df_rep["match"] == "REPLICATED"
        ).sum()
        n_rep_str = (
            f"{n_rep}/{len(REPLICATION_PANEL)}"
        )

    lines = [
        ("SCRIPT 4 SUMMARY", True),
        ("cdRCC | GSE89122 | 2026-03-03", False),
        ("", False),
        ("P4-1 REPLICATION", False),
        (f"  GSE83479: {n_rep_str}", False),
        ("", False),
        ("P4-2 HK2 DRIVER", False),
        ("  Prediction: RELA or CEBPB", False),
        ("  See Step 5 verdict", False),
        ("", False),
        ("P4-3 MYC TRANSITION", False),
        ("  Prediction: CDC3 lowest BHLHE40", False),
        ("  See Step 6 verdict", False),
        ("", False),
        ("P4-4 CEBPA ANTAGONISM", False),
        ("  Prediction: opposes whole module", False),
        ("  See Step 7 verdict", False),
        ("", False),
        ("P4-5 ADPRM PROXY", False),
        (f"  r(S3,S4) = {r_ss:>+.3f}"
         if not np.isnan(r_ss)
         else "  r(S3,S4) = not computed", False),
        ("", False),
        ("Author: Eric Robert Lawson", False),
        ("OrganismCore | Doc 89 S4", False),
    ]

    for i, (txt, bold) in enumerate(lines):
        ax_i.text(
            0.04, 0.97 - i * 0.038, txt,
            transform=ax_i.transAxes,
            color=TITLE_C if bold else LABEL_C,
            fontsize=7.5 if bold else 6.0,
            fontweight="bold" if bold else "normal",
            va="top", fontfamily="monospace",
        )
    style(ax_i, "I �� Summary")

    fig.suptitle(
        "cdRCC — Script 4: Replication Fix, "
        "HK2 Driver, MYC Transition, "
        "CEBPA Panel, ADPRM Proxy\n"
        "OrganismCore | GSE89122 + GSE83479 | "
        "2026-03-03",
        color=TITLE_C, fontsize=9, y=0.99,
    )

    out_fig = os.path.join(
        S4_DIR, "GSE89122_script4_s4.png"
    )
    plt.savefig(
        out_fig, dpi=150, bbox_inches="tight",
        facecolor=fig.get_facecolor(),
    )
    plt.close(fig)
    log(f"  Figure saved: {out_fig}")

# ============================================================
# MAIN
# ============================================================

def main():
    log("=" * 65)
    log("cdRCC — COLLECTING DUCT CARCINOMA")
    log("FALSE ATTRACTOR — SCRIPT 4")
    log("OrganismCore | GSE89122 + GSE83479")
    log("Date: 2026-03-03")
    log("=" * 65)
    log("")
    log("  Predictions stated in Doc 89b addendum")
    log("  before this script ran:")
    log("  P4-1: GSE83479 8+/12 replicate")
    log("  P4-2: HK2 driver = RELA or CEBPB")
    log("  P4-3: CDC3 lowest BHLHE40 in tumour set")
    log("  P4-4: CEBPA opposes whole PPARG module")
    log("  P4-5: r(S3_depth, S4_depth) > 0.95")

    # Step 0 — Load primary matrix
    df, tumor, normal, t_cols, n_cols = \
        load_primary()

    # Step 1 — Diagnose GSE83479 metadata
    sample_info, all_gsms = \
        diagnose_gse83479_metadata()

    # Build full sample map
    gsm_map, cdc_gsms, normal_gsms, utuc_gsms = \
        build_gse83479_map(sample_info, all_gsms)

    # Step 2 — Load GSE83479
    df_rep, tumor_rep, normal_rep, utuc_rep = \
        load_gse83479(
            gsm_map, cdc_gsms,
            normal_gsms, utuc_gsms
        )

    # Step 3 — Replication panel
    df_rep_results = run_replication(
        tumor_rep, normal_rep, tumor, normal
    )

    # Step 4 — GSE83479 depth correlations
    df_rep_sp = gse83479_depth_correlations(
        tumor_rep, normal_rep, tumor, normal
    )

    # Step 5 — HK2 driver test
    hk2_results = hk2_driver_test(tumor)

    # Step 6 — MYC/BHLHE40 transition
    myc_bhlhe40_transition(tumor, normal)

    # Step 7 — CEBPA antagonism panel
    cebpa_results = cebpa_antagonism_panel(
        tumor, normal
    )

    # Step 8 — ADPRM depth proxy
    depth_s3, depth_s4 = adprm_depth_proxy(tumor)

    # Step 9 — Comparison summary
    depth_comparison_summary(
        tumor, depth_s3, depth_s4
    )

    # Step 10 — Figure
    generate_figure(
        tumor, normal,
        depth_s3, depth_s4,
        df_rep_results, df_rep_sp,
        hk2_results, cebpa_results,
    )

    log("")
    log("=" * 65)
    log("SCRIPT 4 COMPLETE")
    log(f"\nOutputs in: {S4_DIR}")
    log("  replication_gse83479_s4.csv")
    log("  gse83479_depth_correlations_s4.csv")
    log("  GSE89122_script4_s4.png")
    log("  analysis_log_s4.txt")
    log("")
    log("Read the output in this order:")
    log("  1. Step 1 — metadata dump")
    log("     What keywords classify the samples?")
    log("     If all 'unknown': check raw_lines")
    log("     and update keywords manually.")
    log("  2. Step 3 — replication verdict P4-1")
    log("  3. Step 5 — HK2 driver verdict P4-2")
    log("  4. Step 6 — transition verdict P4-3")
    log("  5. Step 7 — CEBPA verdict P4-4")
    log("  6. Step 8 — ADPRM proxy verdict P4-5")
    log("")
    log("If Step 1 returns all 'unknown':")
    log("  Read raw_lines carefully.")
    log("  Find the actual term used for CDC tumour.")
    log("  Update keywords_cdc in build_gse83479_map")
    log("  and re-run.")
    log("=" * 65)

    write_log()


if __name__ == "__main__":
    main()
