"""
cdRCC — Collecting Duct Renal Cell Carcinoma
FALSE ATTRACTOR — SCRIPT 3
OrganismCore Cancer Validation #13

Dataset primary:    GSE89122
                    7 CDC tumours | 6 matched normals
                    6 matched pairs + 1 unpaired (CDC5)

Dataset replication: GSE83479
                    17 CDC tumours + 9 external normals
                    Illumina HT12 microarray
                    (used only for replication — not
                     for depth scoring or new geometry)

Established by Scripts 1 and 2:
  Switch gene:   PRKAR2B  (PKA regulatory subunit)
                 PKA gap confirmed: ADCY6→PRKAR2B broken
  FA marker:     IL1RAP   (depth r top positive)
  Core module:   PPARG-KLF5-AGR2-ESRP1-IL1RAP (ductal)
  Ectopic module: PAEP-CST1-S100A7-ANXA8 (Müllerian)
  Lock:          EZH2 initiating (uniform, r=+0.19)
                 PPARG-KLF5 active maintenance
  CDC4 artefact: Pearson r inflated by CDC4 outlier
                 Spearman required for reliable ranking

PREDICTIONS LOCKED BEFORE RUNNING (Doc 89b N1-N7):
  S3-P1: Spearman r(Programme A, Programme B) < 0.3
         Two modules are independent
  S3-P2: Spearman r(PPARG, CEBPA) near zero in tumour
         vs positive in normal
         PPARG was coupled to CEBPA, now to KLF5
  S3-P3: ADCY3 driver is MYC or BHLHE40 (not PPARG)
         r(MYC, ADCY3) > 0.5 in tumours
  S3-P4: CELSR1 belongs to PPARG module not NF-kB
         r(CELSR1, KLF5) > r(CELSR1, IL1B)
  S3-P5: CDC3 is biologically shallow not technical
         CDC3 has genuine collecting duct retention
         AQP2/PRKAR2B higher in CDC3 than other tumours
  S3-P6: MYC-MKI67 Spearman r < 0.4 in tumours
         MYC is a metabolic driver not proliferation
  S3-P7: GSE83479 independent replication
         8+/12 key genes replicate in correct direction
         (stated: PPARG-KLF5-AGR2-EZH2-PRKAR2B axis)

Author:    Eric Robert Lawson
Framework: OrganismCore
Protocol:  Phase 3 — Script 3 Replication and Audit
Document:  (to be written after output — Doc 89b addendum)
Date:      2026-03-03
"""

import os
import sys
import gzip
import re
import time
import urllib.request
import urllib.parse
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
S2_DIR      = os.path.join(BASE_DIR, "results_s2")
S3_DIR      = os.path.join(BASE_DIR, "results_s3")
LOG_FILE    = os.path.join(S3_DIR, "analysis_log_s3.txt")

MATRIX_PATH = os.path.join(RESULTS_DIR, "GSE89122_log2cpm.csv")
S2_DEPTH    = os.path.join(S2_DIR, "depth_correlations_s2.csv")

REP_DIR     = os.path.join(BASE_DIR, "GSE83479")

os.makedirs(S3_DIR,  exist_ok=True)
os.makedirs(REP_DIR, exist_ok=True)

# ============================================================
# SAMPLE MAP — GSE89122 (locked in Phase 0)
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
    "GSM2359152": ("CDC5", "tumor"),
    "GSM2359153": ("CDC6", "tumor"),
    "GSM2359154": ("CDC6", "normal"),
    "GSM2359155": ("CDC7", "tumor"),
    "GSM2359156": ("CDC7", "normal"),
}

# ============================================================
# GENE PANELS — from S1/S2 geometry (locked in Doc 89b)
# ============================================================

# Corrected depth axis (from S2)
SWITCH_GENE = "PRKAR2B"   # top suppressed Pearson r
FA_GENE     = "IL1RAP"    # top elevated Pearson r

# Programme A — ductal secretory core
# Drives attractor depth, all tightly correlated
PROG_A = [
    "PPARG", "KLF5", "AGR2", "ESRP1",
    "IL1RAP", "GPRC5A", "SERPINA1",
    "TMPRSS4", "CST6", "KLF10",
]

# Programme B — ectopic Müllerian/squamous
# Co-elevated but predicted independent of Prog A
PROG_B = [
    "PAEP", "CST1", "S100A7",
    "ANXA8", "ANXA8L1", "LY6D",
]

# PKA circuit — the gap tested in S2
PKA_CIRCUIT = [
    "AVPR2", "AVPR1A", "ADCY3", "ADCY6",
    "PRKAR1A", "PRKAR2A", "PRKAR2B",
    "PRKACB", "PRKACA",
    "AQP2", "AQP3", "SCNN1A", "SCNN1B", "SCNN1G",
]

# PPARG rewiring candidates
# Tests what PPARG was coupled to in normal (CEBPA)
# vs what it is coupled to in tumour (KLF5/AGR2)
PPARG_REWIRE = [
    "PPARG", "KLF5", "KLF4", "KLF2",
    "CEBPA", "CEBPB", "RXRA", "RXRB",
    "AGR2", "ESRP1", "IL1RAP",
    "FABP4", "FABP7", "SCD", "FASN", "ACACA",
]

# ADCY3 driver candidates
# Which TF is driving the ADCY3 isoform switch?
ADCY3_DRIVERS = [
    "ADCY3", "ADCY6",
    "MYC", "MYCN", "BHLHE40",
    "HIF1A", "HIF2A", "EPAS1",
    "PPARG", "KLF5",
    "NFKB1", "NFKB2", "RELA",
    "PRKCI", "CEBPB",
    "MKI67",
]

# CELSR1 circuit assignment
# Which module does this PCP gene belong to?
CELSR1_PANEL = [
    "CELSR1", "CELSR2", "CELSR3",
    "FZD3", "FZD6", "VANGL1", "VANGL2",
    "PRICKLE1", "PRICKLE2", "DVL1", "DVL2",
    "KLF5", "PPARG", "AGR2",
    "PRKCI", "IL1B", "IL1RAP",
    "MYC", "BHLHE40",
]

# CDC3 identity panel
# Tests whether CDC3 (depth=0) has retained CD markers
CDC3_PANEL = [
    "AQP2", "PRKAR2B", "AVPR2",
    "SCNN1A", "SCNN1B", "SCNN1G",
    "TFCP2L1", "HNF4A", "FOXI1",
    "ATP6V1G3", "ATP6V0A4",
    "UMOD", "CALB1",
    "IL1RAP", "PPARG", "KLF5",
    "EZH2", "MKI67", "MYC",
]

# MYC metabolic vs proliferation
MYC_PROLIFERATION = [
    "MYC", "MKI67", "TOP2A", "PCNA",
    "CDK4", "CCND1", "AURKA", "PLK1",
    "MCM2", "MCM7",
]

# MYC metabolic targets
MYC_METABOLIC = [
    "MYC", "LDHA", "PKM", "ENO1",
    "SLC2A1", "SLC2A3",
    "ADCY3", "HK1", "HK2",
    "FASN", "SCD", "ACACA",
    "BHLHE40",
]

# Replication panel — 12 genes tested in GSE83479
# Chosen to represent key findings from S1+S2
# All directions pre-stated (locked here)
REPLICATION_PANEL = {
    # gene:  (expected_direction, description)
    "AQP2":    ("DOWN", "PC identity — should be lost"),
    "PRKAR2B": ("DOWN", "switch gene — should be lost"),
    "AVPR2":   ("DOWN", "PC receptor — should be lost"),
    "SCNN1B":  ("DOWN", "ENaC channel — should be lost"),
    "FOXI1":   ("DOWN", "IC identity — should be lost"),
    "HNF4A":   ("DOWN", "tubular TF — should be lost"),
    "PPARG":   ("FLAT", "attractor hub — should be ~flat"),
    "KLF5":    ("UP",   "active driver — should be up"),
    "AGR2":    ("UP",   "ductal marker — should be up"),
    "EZH2":    ("UP",   "initiating lock — should be up"),
    "IL1RAP":  ("UP",   "FA marker — should be up"),
    "MKI67":   ("UP",   "proliferation — should be up"),
}

# Top-20 S2 Pearson r genes for audit table
# Taken from S2 output (Doc 89b step 12)
# Format: (gene, pearson_r_S2)
S2_TOP20_PEARSON = [
    ("LOC101927630", +0.9786),
    ("CDS2",         -0.9744),
    ("USP45",        -0.9683),
    ("IL1RAP",       +0.9682),
    ("MYC",          -0.9668),
    ("PRKCI",        +0.9651),
    ("CD48",         -0.9634),
    ("PRKAR2B",      -0.9596),
    ("INPP4B",       +0.9571),
    ("CHPT1",        -0.9559),
    ("GPRC5A",       +0.9556),
    ("ADPRM",        -0.9523),
    ("KLF5",         +0.9497),
    ("MPP6",         -0.9483),
    ("TMPRSS4",      +0.9464),
    ("RHBDL2",       +0.9456),
    ("NOMO1",        +0.9455),
    ("IKZF2",        +0.9417),
    ("CST6",         +0.9400),
    ("B4GALT5",      +0.9388),
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
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
            try:
                return raw.decode("utf-8")
            except UnicodeDecodeError:
                return raw.decode("latin-1")
    except Exception as e:
        return f"ERROR:{e}"


def download_file(url, local_path):
    def hook(count, block, total):
        if total > 0:
            pct = min(count * block / total * 100, 100)
            mb  = count * block / 1e6
            sys.stdout.write(f"\r    {mb:.2f} MB  {pct:.1f}%")
            sys.stdout.flush()
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req) as resp, \
             open(local_path, "wb") as out:
            total = int(resp.headers.get("Content-Length", 0))
            block = 65536
            count = 0
            while True:
                chunk = resp.read(block)
                if not chunk:
                    break
                out.write(chunk)
                count += 1
                hook(count, block, total)
        print()
        return True
    except Exception as e:
        print()
        log(f"    DOWNLOAD ERROR: {e}")
        return False


def spearman(x, y):
    """Spearman r and p — handles ties correctly."""
    mask = (~np.isnan(x)) & (~np.isnan(y))
    if mask.sum() < 4:
        return np.nan, np.nan
    r, p = stats.spearmanr(x[mask], y[mask])
    return float(r), float(p)


def pearson(x, y):
    """Pearson r and p."""
    mask = (~np.isnan(x)) & (~np.isnan(y))
    if mask.sum() < 4:
        return np.nan, np.nan
    r, p = stats.pearsonr(x[mask], y[mask])
    return float(r), float(p)


def mw_test(a, b):
    """Mann-Whitney U — two-sided."""
    try:
        _, p = stats.mannwhitneyu(a, b, alternative="two-sided")
        return float(p)
    except Exception:
        return np.nan


def fmt_p(p):
    if np.isnan(p):
        return "  ns"
    if p < 0.001:
        return f"p={p:.2e} ***"
    if p < 0.01:
        return f"p={p:.4f}  **"
    if p < 0.05:
        return f"p={p:.4f}   *"
    return f"p={p:.4f}  ns"


def norm01(s):
    """Min-max normalise a pandas Series."""
    lo, hi = s.min(), s.max()
    if hi == lo:
        return s * 0.0
    return (s - lo) / (hi - lo)

# ============================================================
# STEP 0 — LOAD S1/S2 MATRIX
# ============================================================

def load_primary_matrix():
    log("=" * 65)
    log("STEP 0 — LOADING S1/S2 MATRIX (GSE89122)")
    log(f"  {MATRIX_PATH}")
    log("=" * 65)

    if not os.path.exists(MATRIX_PATH):
        log(f"  ERROR: Matrix not found at {MATRIX_PATH}")
        log("  Run Script 1 first to generate the matrix.")
        sys.exit(1)

    df = pd.read_csv(MATRIX_PATH, index_col=0)
    log(f"  Shape: {df.shape[0]} genes × {df.shape[1]} samples")

    # Classify samples
    tumor_cols  = [c for c in df.columns
                   if SAMPLE_MAP.get(c, ("",""))[1] == "tumor"]
    normal_cols = [c for c in df.columns
                   if SAMPLE_MAP.get(c, ("",""))[1] == "normal"]

    log(f"  Tumour cols:  {len(tumor_cols)}")
    log(f"  Normal cols:  {len(normal_cols)}")
    log(f"  Tumour GSMs:  {tumor_cols}")

    tumor  = df[tumor_cols]
    normal = df[normal_cols]

    return df, tumor, normal, tumor_cols, normal_cols

# ============================================================
# STEP 1 — BUILD CORRECTED DEPTH SCORE (S3)
# Using S2 axis (PRKAR2B / IL1RAP) — Spearman-compatible
# ============================================================

def build_depth_score(tumor):
    log("")
    log("=" * 65)
    log("STEP 1 — S3 DEPTH SCORE (PRKAR2B / IL1RAP)")
    log("  Reuses S2 corrected axis.")
    log("  All subsequent Spearman correlations use")
    log("  this same depth vector.")
    log("=" * 65)

    def norm01_s(s):
        lo, hi = s.min(), s.max()
        if hi == lo:
            return pd.Series(0.0, index=s.index)
        return (s - lo) / (hi - lo)

    genes_present = tumor.index.tolist()

    has_switch = SWITCH_GENE in genes_present
    has_fa     = FA_GENE     in genes_present

    if not has_switch:
        log(f"  WARNING: {SWITCH_GENE} not in matrix — "
            f"using mean of PKA suppressed genes")
    if not has_fa:
        log(f"  WARNING: {FA_GENE} not in matrix — "
            f"using mean of Prog A genes")

    if has_switch:
        switch_vals = norm01_s(tumor.loc[SWITCH_GENE])
        depth_switch = 1.0 - switch_vals
    else:
        available = [g for g in PKA_CIRCUIT if g in genes_present]
        depth_switch = 1.0 - norm01_s(
            tumor.loc[available].mean(axis=0)
        )

    if has_fa:
        depth_fa = norm01_s(tumor.loc[FA_GENE])
    else:
        available = [g for g in PROG_A if g in genes_present]
        depth_fa = norm01_s(
            tumor.loc[available].mean(axis=0)
        )

    depth = (depth_switch + depth_fa) / 2.0

    log(f"\n  S3 Depth (7 tumours):")
    log(f"    Mean  : {depth.mean():.4f}")
    log(f"    Median: {depth.median():.4f}")
    log(f"    Std   : {depth.std():.4f}")
    log(f"    Min   : {depth.min():.4f}")
    log(f"    Max   : {depth.max():.4f}")
    log("")
    log("  Per-sample depth:")
    for gsm in depth.index:
        patient, stype = SAMPLE_MAP.get(gsm, ("?","?"))
        log(f"    {gsm} ({patient}): {depth[gsm]:.4f}")

    return depth

# ============================================================
# STEP 2 — SPEARMAN DEPTH CORRELATIONS (FULL GENOME)
# Corrects the CDC4/Pearson inflation from S1/S2
# ============================================================

def spearman_depth_correlations(tumor, depth):
    log("")
    log("=" * 65)
    log("STEP 2 — SPEARMAN DEPTH CORRELATIONS")
    log("  Full genome Spearman r vs depth score")
    log("  Replaces Pearson from S1/S2")
    log("  CDC4 outlier effect: Spearman is robust")
    log("=" * 65)

    depth_arr = depth.values
    records   = []

    for gene in tumor.index:
        vals = tumor.loc[gene].values.astype(float)
        r, p = spearman(vals, depth_arr)
        records.append({"gene": gene, "spearman_r": r, "p": p})

    df_corr = pd.DataFrame(records).set_index("gene")
    df_corr = df_corr.sort_values(
        "spearman_r", key=abs, ascending=False
    )

    # Save full table
    out = os.path.join(S3_DIR, "depth_correlations_spearman_s3.csv")
    df_corr.to_csv(out)
    log(f"  Saved: {out}")

    # Print top 20 positive
    log("\n  Top 20 positive Spearman correlators (FA axis):")
    top_pos = df_corr[df_corr["spearman_r"] > 0].head(20)
    log(f"  {'Gene':<22} {'Spearman_r':>12}  {'p-value':>14}")
    log(f"  {'-'*52}")
    for gene, row in top_pos.iterrows():
        log(f"  {gene:<22} {row['spearman_r']:>+12.4f}  "
            f"{fmt_p(row['p']):>14}")

    # Print top 20 negative
    log("\n  Top 20 negative Spearman correlators (switch axis):")
    top_neg = df_corr[df_corr["spearman_r"] < 0].tail(20).iloc[::-1]
    log(f"  {'Gene':<22} {'Spearman_r':>12}  {'p-value':>14}")
    log(f"  {'-'*52}")
    for gene, row in top_neg.iterrows():
        log(f"  {gene:<22} {row['spearman_r']:>+12.4f}  "
            f"{fmt_p(row['p']):>14}")

    return df_corr

# ============================================================
# STEP 3 — PEARSON vs SPEARMAN AUDIT TABLE
# Identifies CDC4-inflated genes from S1/S2
# ============================================================

def pearson_spearman_audit(tumor, depth, df_spearman):
    log("")
    log("=" * 65)
    log("STEP 3 — PEARSON vs SPEARMAN AUDIT")
    log("  Flags genes where |Pearson| - |Spearman| > 0.15")
    log("  These are CDC4-inflated results from S1/S2")
    log("=" * 65)

    depth_arr = depth.values
    log(f"\n  {'Gene':<22} {'Pearson_S2':>12} {'Spearman_S3':>13} "
        f"{'Diff':>7}  {'Flag':>10}")
    log(f"  {'-'*68}")

    inflated = []
    stable   = []

    for gene, pearson_r in S2_TOP20_PEARSON:
        if gene not in tumor.index:
            log(f"  {gene:<22} {pearson_r:>+12.4f} "
                f"{'NOT IN MATRIX':>13}")
            continue

        vals = tumor.loc[gene].values.astype(float)
        sp_r, _  = spearman(vals, depth_arr)
        diff = abs(pearson_r) - abs(sp_r)

        flag = "INFLATED" if diff > 0.15 else "stable"
        if diff > 0.15:
            inflated.append(gene)
        else:
            stable.append(gene)

        log(f"  {gene:<22} {pearson_r:>+12.4f} "
            f"{sp_r:>+13.4f} {diff:>+7.3f}  {flag:>10}")

    log(f"\n  CDC4-inflated genes: {len(inflated)}")
    log(f"  Stable genes:        {len(stable)}")
    if inflated:
        log(f"  Inflated list: {inflated}")
    if stable:
        log(f"  Stable list:   {stable}")

    log(f"\n  INTERPRETATION:")
    log(f"  Stable genes have genuine biological signal")
    log(f"  regardless of CDC4's library size.")
    log(f"  Inflated genes should be read as")
    log(f"  directional only — their r values overstated.")

    return stable, inflated

# ============================================================
# STEP 4 — PROGRAMME A vs B INDEPENDENCE TEST
# S3-P1: r(ProgA, ProgB) < 0.3 in tumours
# ============================================================

def programme_independence_test(tumor, depth):
    log("")
    log("=" * 65)
    log("STEP 4 — PROGRAMME A vs B INDEPENDENCE TEST")
    log("  S3-P1: Two modules are independent")
    log("  Predicted: Spearman r(ProgA, ProgB) < 0.3")
    log("=" * 65)

    genes_present = tumor.index.tolist()

    pa_genes = [g for g in PROG_A if g in genes_present]
    pb_genes = [g for g in PROG_B if g in genes_present]

    log(f"\n  Programme A genes available: "
        f"{len(pa_genes)}/{len(PROG_A)}")
    log(f"  {pa_genes}")
    log(f"\n  Programme B genes available: "
        f"{len(pb_genes)}/{len(PROG_B)}")
    log(f"  {pb_genes}")

    if not pa_genes or not pb_genes:
        log("  ERROR: insufficient genes for test")
        return None, None

    # Build metagene scores (mean of normalised genes)
    pa_mat = tumor.loc[pa_genes].T.apply(
        lambda x: (x - x.mean()) / (x.std() + 1e-9)
    )
    pb_mat = tumor.loc[pb_genes].T.apply(
        lambda x: (x - x.mean()) / (x.std() + 1e-9)
    )

    score_a = pa_mat.mean(axis=1)
    score_b = pb_mat.mean(axis=1)

    r_ab, p_ab = spearman(
        score_a.values, score_b.values
    )

    log(f"\n  Metagene scores (7 tumours):")
    log(f"  {'GSM':<14} {'Patient':>8} "
        f"{'Score_A':>10} {'Score_B':>10}")
    log(f"  {'-'*46}")
    for gsm in tumor.columns:
        patient, _ = SAMPLE_MAP.get(gsm, ("?","?"))
        log(f"  {gsm:<14} {patient:>8} "
            f"{score_a[gsm]:>+10.4f} {score_b[gsm]:>+10.4f}")

    log(f"\n  Spearman r(Programme A, Programme B):")
    log(f"    r = {r_ab:+.4f}  {fmt_p(p_ab)}")

    log(f"\n  Per-gene Spearman r with depth (S3):")
    log(f"  {'Gene':<14} {'Module':>8} "
        f"{'Spearman_r':>12}  p-value")
    log(f"  {'-'*50}")
    for g in pa_genes:
        vals = tumor.loc[g].values.astype(float)
        r, p = spearman(vals, depth.values)
        log(f"  {g:<14} {'A':>8} {r:>+12.4f}  "
            f"{fmt_p(p)}")
    for g in pb_genes:
        vals = tumor.loc[g].values.astype(float)
        r, p = spearman(vals, depth.values)
        log(f"  {g:<14} {'B':>8} {r:>+12.4f}  "
            f"{fmt_p(p)}")

    # S3-P1 verdict
    log(f"\n  PREDICTION S3-P1 VERDICT:")
    log(f"    Predicted: r(A,B) < 0.3")
    log(f"    Observed:  r = {r_ab:+.4f}")
    if abs(r_ab) < 0.3:
        log(f"    CONFIRMED: Two programmes are independent")
        log(f"    Core ductal module and ectopic Müllerian")
        log(f"    module do not co-vary within tumours.")
        log(f"    They arise from the same reprogramming")
        log(f"    but are maintained independently.")
    else:
        log(f"    NOT CONFIRMED: Programmes are correlated")
        log(f"    r = {r_ab:+.4f} — single unified attractor")
        log(f"    The two-module hypothesis is wrong.")

    return score_a, score_b

# ============================================================
# STEP 5 — PPARG REWIRING TEST
# S3-P2: PPARG coupled to KLF5 in tumour, CEBPA in normal
# ============================================================

def pparg_rewiring_test(tumor, normal):
    log("")
    log("=" * 65)
    log("STEP 5 — PPARG REWIRING TEST")
    log("  S3-P2: PPARG was coupled to CEBPA (normal)")
    log("         PPARG is now coupled to KLF5 (tumour)")
    log("  Method: Spearman r(PPARG, each gene)")
    log("          in tumour vs normal separately")
    log("=" * 65)

    genes_present_t = tumor.index.tolist()
    genes_present_n = normal.index.tolist()

    if "PPARG" not in genes_present_t:
        log("  PPARG not in matrix — cannot run test")
        return

    pparg_t = tumor.loc["PPARG"].values.astype(float)
    pparg_n = normal.loc["PPARG"].values.astype(float)

    panel = [g for g in PPARG_REWIRE
             if g in genes_present_t
             and g != "PPARG"]

    log(f"\n  Panel ({len(panel)} genes):")
    log(f"  {'Gene':<14} {'r_tumour':>10} {'p_tumour':>12} "
        f"{'r_normal':>10} {'p_normal':>12} "
        f"{'Direction_change':>18}")
    log(f"  {'-'*78}")

    rewired_to   = []
    rewired_from = []

    for gene in panel:
        t_vals = tumor.loc[gene].values.astype(float)
        n_vals = normal.loc[gene].values.astype(float) \
            if gene in genes_present_n else None

        rt, pt = spearman(pparg_t, t_vals)

        if n_vals is not None and len(n_vals) >= 3:
            rn, pn = spearman(pparg_n, n_vals)
        else:
            rn, pn = np.nan, np.nan

        # Direction change detection
        if not np.isnan(rt) and not np.isnan(rn):
            delta = rt - rn
            if rt > 0.4 and rn < 0.2:
                direction = "GAINED coupling"
                rewired_to.append(gene)
            elif rt < 0.2 and rn > 0.4:
                direction = "LOST coupling"
                rewired_from.append(gene)
            elif abs(delta) > 0.3:
                direction = f"shifted {delta:+.2f}"
            else:
                direction = "stable"
        else:
            direction = "normal n<3"

        rn_str = f"{rn:+.4f}" if not np.isnan(rn) else "  n/a"
        pn_str = fmt_p(pn) if not np.isnan(pn) else "     n/a"

        log(f"  {gene:<14} {rt:>+10.4f} {fmt_p(pt):>12} "
            f"{rn_str:>10} {pn_str:>12} {direction:>18}")

    log(f"\n  PPARG gained coupling in tumour (not in normal):")
    for g in rewired_to:
        log(f"    {g}")

    log(f"\n  PPARG lost coupling in tumour (was in normal):")
    for g in rewired_from:
        log(f"    {g}")

    # S3-P2 verdict
    cebpa_gained = "CEBPA" in rewired_to
    cebpa_lost   = "CEBPA" in rewired_from
    klf5_gained  = "KLF5"  in rewired_to

    log(f"\n  PREDICTION S3-P2 VERDICT:")
    log(f"    Predicted: PPARG-CEBPA lost, "
        f"PPARG-KLF5 gained")

    if klf5_gained:
        log(f"    KLF5 gained:  CONFIRMED")
    else:
        log(f"    KLF5 gained:  NOT CONFIRMED "
            f"— check r values above")

    if cebpa_lost:
        log(f"    CEBPA lost:   CONFIRMED")
    elif cebpa_gained:
        log(f"    CEBPA gained: INVERTED "
            f"— PPARG-CEBPA coupling NEW in tumour")
    else:
        log(f"    CEBPA:        no directional change")

# ============================================================
# STEP 6 — ADCY3 DRIVER IDENTIFICATION
# S3-P3: r(MYC, ADCY3) > 0.5 OR r(BHLHE40, ADCY3) > 0.5
# ============================================================

def adcy3_driver_test(tumor):
    log("")
    log("=" * 65)
    log("STEP 6 — ADCY3 ISOFORM SWITCH — DRIVER TEST")
    log("  S3-P3: Predicted driver = MYC or BHLHE40")
    log("  Test: Spearman r(candidate, ADCY3) in tumours")
    log("=" * 65)

    if "ADCY3" not in tumor.index:
        log("  ADCY3 not in matrix — cannot run test")
        return

    adcy3_vals = tumor.loc["ADCY3"].values.astype(float)
    adcy6_vals = tumor.loc["ADCY6"].values.astype(float) \
        if "ADCY6" in tumor.index else None

    log(f"\n  {'Candidate':<14} {'r_ADCY3':>10}  "
        f"{'p_ADCY3':>14}  "
        f"{'r_ADCY6':>10}  {'p_ADCY6':>14}")
    log(f"  {'-'*68}")

    best_r    = 0.0
    best_gene = None

    for gene in ADCY3_DRIVERS:
        if gene == "ADCY3":
            continue
        if gene not in tumor.index:
            log(f"  {gene:<14} {'not in matrix':>40}")
            continue

        vals = tumor.loc[gene].values.astype(float)
        r3, p3 = spearman(vals, adcy3_vals)

        if adcy6_vals is not None:
            r6, p6 = spearman(vals, adcy6_vals)
            r6_str = f"{r6:>+10.4f}"
            p6_str = fmt_p(p6)
        else:
            r6_str = "      n/a"
            p6_str = "           n/a"

        log(f"  {gene:<14} {r3:>+10.4f}  "
            f"{fmt_p(p3):>14}  "
            f"{r6_str}  {p6_str}")

        if not np.isnan(r3) and abs(r3) > abs(best_r):
            best_r    = r3
            best_gene = gene

    log(f"\n  Best ADCY3 driver by Spearman r:")
    log(f"    Gene: {best_gene}  r = {best_r:+.4f}")

    log(f"\n  PREDICTION S3-P3 VERDICT:")
    log(f"    Predicted: MYC or BHLHE40 is ADCY3 driver")
    if best_gene in ("MYC", "BHLHE40"):
        log(f"    CONFIRMED: {best_gene} r={best_r:+.4f}")
    else:
        log(f"    NOT CONFIRMED: best driver = {best_gene} "
            f"r={best_r:+.4f}")
        log(f"    Revise: the isoform switch driver "
            f"is {best_gene}")

# ============================================================
# STEP 7 — CELSR1 CIRCUIT ASSIGNMENT
# S3-P4: r(CELSR1, KLF5) > r(CELSR1, IL1B)
# ============================================================

def celsr1_assignment(tumor):
    log("")
    log("=" * 65)
    log("STEP 7 — CELSR1 CIRCUIT ASSIGNMENT")
    log("  S3-P4: CELSR1 belongs to PPARG module")
    log("         not to NF-kB/PRKCI arm")
    log("  Test: Compare Spearman r(CELSR1, KLF5)")
    log("        vs r(CELSR1, IL1B)")
    log("=" * 65)

    if "CELSR1" not in tumor.index:
        log("  CELSR1 not in matrix — cannot run test")
        return

    celsr1_vals = tumor.loc["CELSR1"].values.astype(float)

    panel = [g for g in CELSR1_PANEL
             if g != "CELSR1" and g in tumor.index]

    log(f"\n  {'Gene':<14} {'r_CELSR1':>10}  {'p':>14}")
    log(f"  {'-'*42}")

    r_klf5 = np.nan
    r_il1b = np.nan

    for gene in panel:
        vals = tumor.loc[gene].values.astype(float)
        r, p = spearman(celsr1_vals, vals)
        log(f"  {gene:<14} {r:>+10.4f}  {fmt_p(p):>14}")
        if gene == "KLF5":
            r_klf5 = r
        if gene == "IL1B":
            r_il1b = r

    log(f"\n  r(CELSR1, KLF5) = {r_klf5:+.4f}")
    log(f"  r(CELSR1, IL1B) = {r_il1b:+.4f}")

    log(f"\n  PREDICTION S3-P4 VERDICT:")
    log(f"    Predicted: r(CELSR1,KLF5) > r(CELSR1,IL1B)")
    if not np.isnan(r_klf5) and not np.isnan(r_il1b):
        if r_klf5 > r_il1b:
            log(f"    CONFIRMED: CELSR1 belongs to PPARG "
                f"module ({r_klf5:+.4f} vs {r_il1b:+.4f})")
            log(f"    CELSR1 may be a KLF5 target gene in")
            log(f"    the ductal secretory programme.")
        else:
            log(f"    NOT CONFIRMED: CELSR1 belongs to "
                f"NF-kB/PRKCI arm ({r_il1b:+.4f} > "
                f"{r_klf5:+.4f})")
            log(f"    CELSR1 is driven by inflammatory")
            log(f"    signalling not ductal identity.")

# ============================================================
# STEP 8 — CDC3 EXAMINATION
# S3-P5: CDC3 (depth=0) has genuine CD retention
# ============================================================

def cdc3_examination(tumor, normal):
    log("")
    log("=" * 65)
    log("STEP 8 — CDC3 SHALLOW TUMOUR EXAMINATION")
    log("  S3-P5: CDC3 depth=0 is biological")
    log("         not technical artefact")
    log("  Test: CDC3 tumour has higher AQP2/PRKAR2B")
    log("        than other tumours")
    log("=" * 65)

    # CDC3 tumour = GSM2359148, normal = GSM2359149
    cdc3_t  = "GSM2359148"
    cdc3_n  = "GSM2359149"
    other_t = [c for c in tumor.columns
               if c != cdc3_t]

    if cdc3_t not in tumor.columns:
        log("  CDC3 tumour not in matrix")
        return

    log(f"\n  {'Gene':<14} {'CDC3_T':>10} "
        f"{'Other_T_mean':>14} "
        f"{'CDC3_N':>10} {'Direction':>12}")
    log(f"  {'-'*62}")

    retained = []
    normal_like = []

    panel = [g for g in CDC3_PANEL if g in tumor.index]

    for gene in panel:
        cdc3_t_val = float(tumor.loc[gene, cdc3_t])
        other_mean = float(tumor.loc[gene, other_t].mean())
        cdc3_n_val = float(normal.loc[gene, cdc3_n]) \
            if cdc3_n in normal.columns \
            and gene in normal.index else np.nan

        # Is CDC3 tumour more like normal?
        if not np.isnan(cdc3_n_val):
            diff_from_normal = abs(cdc3_t_val - cdc3_n_val)
            diff_from_others = abs(cdc3_t_val - other_mean)
            direction = (
                "CD-retained"
                if diff_from_normal < diff_from_others
                else "attractor"
            )
            if direction == "CD-retained":
                retained.append(gene)
        else:
            direction = "no normal"

        n_str = f"{cdc3_n_val:.4f}" if not np.isnan(
            cdc3_n_val
        ) else "     n/a"

        log(f"  {gene:<14} {cdc3_t_val:>+10.4f} "
            f"{other_mean:>+14.4f} "
            f"{n_str:>10} {direction:>12}")

    log(f"\n  Genes where CDC3 tumour is closer to normal:")
    for g in retained:
        log(f"    {g}")

    log(f"\n  PREDICTION S3-P5 VERDICT:")
    log(f"    Predicted: CDC3 retains AQP2/PRKAR2B")
    aq2_retained = "AQP2" in retained
    pk_retained  = "PRKAR2B" in retained
    if aq2_retained and pk_retained:
        log(f"    CONFIRMED: CDC3 is a genuine shallow")
        log(f"    tumour with partial CD identity retained.")
        log(f"    It is the least-blocked case in the series.")
    elif aq2_retained or pk_retained:
        log(f"    PARTIAL: Some CD retention in CDC3")
        log(f"    AQP2={aq2_retained}, PRKAR2B={pk_retained}")
    else:
        log(f"    NOT CONFIRMED: CDC3 depth=0 is")
        log(f"    likely a scoring artefact from the")
        log(f"    two-gene normalisation, not biology.")

# ============================================================
# STEP 9 — MYC METABOLIC vs PROLIFERATION TEST
# S3-P6: Spearman r(MYC, MKI67) < 0.4 in tumours
# ============================================================

def myc_role_test(tumor):
    log("")
    log("=" * 65)
    log("STEP 9 — MYC ROLE TEST: METABOLIC vs PROLIFERATION")
    log("  S3-P6: Spearman r(MYC, MKI67) < 0.4")
    log("         MYC is a metabolic driver not")
    log("         a proliferation driver in cdRCC")
    log("=" * 65)

    if "MYC" not in tumor.index:
        log("  MYC not in matrix")
        return

    myc_vals = tumor.loc["MYC"].values.astype(float)

    # Proliferation panel
    prol_panel = [g for g in MYC_PROLIFERATION
                  if g != "MYC" and g in tumor.index]
    # Metabolic panel
    meta_panel = [g for g in MYC_METABOLIC
                  if g != "MYC" and g in tumor.index]

    log(f"\n  MYC vs PROLIFERATION markers:")
    log(f"  {'Gene':<14} {'r_MYC':>10}  {'p':>14}")
    log(f"  {'-'*42}")
    prol_rs = []
    for gene in prol_panel:
        vals = tumor.loc[gene].values.astype(float)
        r, p = spearman(myc_vals, vals)
        log(f"  {gene:<14} {r:>+10.4f}  {fmt_p(p):>14}")
        if not np.isnan(r):
            prol_rs.append(r)

    log(f"\n  MYC vs METABOLIC markers:")
    log(f"  {'Gene':<14} {'r_MYC':>10}  {'p':>14}")
    log(f"  {'-'*42}")
    meta_rs = []
    for gene in meta_panel:
        vals = tumor.loc[gene].values.astype(float)
        r, p = spearman(myc_vals, vals)
        log(f"  {gene:<14} {r:>+10.4f}  {fmt_p(p):>14}")
        if not np.isnan(r):
            meta_rs.append(r)

    mean_prol = np.mean(prol_rs) if prol_rs else np.nan
    mean_meta = np.mean(meta_rs) if meta_rs else np.nan
    r_mki67_myc = np.nan
    if "MKI67" in tumor.index:
        vals = tumor.loc["MKI67"].values.astype(float)
        r_mki67_myc, _ = spearman(myc_vals, vals)

    log(f"\n  Mean r(MYC, proliferation panel): "
        f"{mean_prol:+.4f}")
    log(f"  Mean r(MYC, metabolic panel):     "
        f"{mean_meta:+.4f}")
    log(f"  r(MYC, MKI67) specifically:       "
        f"{r_mki67_myc:+.4f}")

    log(f"\n  PREDICTION S3-P6 VERDICT:")
    log(f"    Predicted: r(MYC, MKI67) < 0.4")
    if not np.isnan(r_mki67_myc):
        if abs(r_mki67_myc) < 0.4:
            log(f"    CONFIRMED: r={r_mki67_myc:+.4f}")
            log(f"    MYC is NOT driving proliferation in")
            log(f"    cdRCC (within-tumour variation).")
            if not np.isnan(mean_meta) and \
               not np.isnan(mean_prol) and \
               mean_meta > mean_prol:
                log(f"    MYC tracks metabolic targets more")
                log(f"    strongly (mean r={mean_meta:+.4f})")
                log(f"    than proliferation ({mean_prol:+.4f}).")
                log(f"    MYC is a metabolic reprogramming")
                log(f"    driver in cdRCC, not a cell-cycle")
                log(f"    driver within these tumours.")
        else:
            log(f"    NOT CONFIRMED: r={r_mki67_myc:+.4f}")
            log(f"    MYC and MKI67 co-vary — MYC may be")
            log(f"    driving proliferation here.")

# ============================================================
# STEP 10 — GSE83479 INDEPENDENT REPLICATION
# S3-P7: 8+/12 key genes replicate in correct direction
# ============================================================

def fetch_gse83479_metadata():
    """Fetch sample metadata for GSE83479."""
    url = (
        "https://www.ncbi.nlm.nih.gov/geo/query/"
        "acc.cgi?acc=GSE83479"
        "&targ=gsm&form=text&view=full"
    )
    log(f"  Fetching GSE83479 metadata...")
    text = fetch_text(url)
    if "ERROR" in text[:20]:
        log(f"  Metadata fetch error: {text[:80]}")
        return {}

    samples = {}
    current_gsm = None
    current = {}

    for line in text.split("\n"):
        if line.startswith("^SAMPLE"):
            if current_gsm:
                samples[current_gsm] = current
            current_gsm = line.split("=")[1].strip()
            current = {}
        elif line.startswith("!Sample_title"):
            current["title"] = line.split("=",1)[1].strip()
        elif line.startswith("!Sample_source_name_ch1"):
            current["source"] = line.split("=",1)[1].strip()
        elif line.startswith("!Sample_characteristics_ch1"):
            val = line.split("=",1)[1].strip()
            if ":" in val:
                k, v = val.split(":",1)
                current[k.strip().lower()] = v.strip()
        elif line.startswith("!Sample_supplementary_file"):
            val = line.split("=",1)[1].strip()
            current.setdefault("suppl", []).append(val)

    if current_gsm:
        samples[current_gsm] = current

    return samples


def classify_gse83479(samples):
    """Classify GSE83479 samples into CDC tumour vs normal."""
    cdc_tumor  = []
    normal_ref = []
    utuc       = []
    other      = []

    for gsm, info in samples.items():
        combined = " ".join(
            str(v) for v in info.values()
        ).lower()

        is_cdc = any(kw in combined for kw in [
            "collecting duct", "bellini",
            "cdc", "cd-rcc",
        ])
        is_normal = any(kw in combined for kw in [
            "normal", "adjacent", "non-tumor",
            "non-neoplastic",
        ])
        is_utuc = any(kw in combined for kw in [
            "utuc", "urothelial", "transitional",
            "upper tract",
        ])

        if is_cdc and not is_normal:
            cdc_tumor.append(gsm)
        elif is_normal:
            normal_ref.append(gsm)
        elif is_utuc:
            utuc.append(gsm)
        else:
            other.append(gsm)

    return cdc_tumor, normal_ref, utuc, other


def get_gse83479_suppl_files(samples):
    """Find series-level or per-sample supplementary files."""
    # Try series-level first
    series_url = (
        "https://www.ncbi.nlm.nih.gov/geo/query/"
        "acc.cgi?acc=GSE83479"
        "&targ=self&form=text&view=full"
    )
    text = fetch_text(series_url)
    suppl = []
    for line in text.split("\n"):
        if "!Series_supplementary_file" in line:
            val = line.split("=",1)[1].strip()
            suppl.append(val)
    return suppl


def download_gse83479():
    """
    Download GSE83479 expression matrix.
    Returns path to downloaded file or None.
    """
    log("")
    log("=" * 65)
    log("STEP 10 — GSE83479 INDEPENDENT REPLICATION")
    log("  17 CDC tumours + 9 external normals")
    log("  Illumina HT12 microarray")
    log("  Testing 12 key genes for replication")
    log("=" * 65)

    # Check cache
    cached = [
        os.path.join(REP_DIR, f)
        for f in os.listdir(REP_DIR)
        if f.endswith(".gz") or f.endswith(".txt")
        or f.endswith(".csv")
    ]
    if cached:
        log(f"  Found {len(cached)} cached file(s) "
            f"in {REP_DIR}")
        for f in cached:
            sz = os.path.getsize(f) / 1e6
            log(f"    {os.path.basename(f)}  {sz:.2f} MB")
        return cached[0]

    # Fetch metadata
    samples  = fetch_gse83479_metadata()
    log(f"  Total GSE83479 samples: {len(samples)}")
    time.sleep(0.5)

    cdc_t, norm, utuc, other = classify_gse83479(samples)
    log(f"  CDC tumour: {len(cdc_t)}")
    log(f"  Normal ref: {len(norm)}")
    log(f"  UTUC:       {len(utuc)}")
    log(f"  Other:      {len(other)}")

    # Get supplementary files
    suppl = get_gse83479_suppl_files(samples)
    time.sleep(0.5)

    if suppl:
        log(f"\n  Series supplementary files:")
        for f in suppl:
            log(f"    {f[-70:]}")

        for furl in suppl:
            fname    = furl.split("/")[-1].strip()
            fl       = fname.lower()
            is_matrix = any(ext in fl for ext in [
                ".txt.gz", ".csv.gz",
                "normalized", "matrix",
                "signal", "expression",
                "quantile", "non_normalized",
            ])
            if is_matrix:
                local = os.path.join(REP_DIR, fname)
                if os.path.exists(local) and \
                   os.path.getsize(local) > 10000:
                    log(f"  Cached: {fname}")
                    return local
                log(f"\n  Downloading: {fname}")
                ok = download_file(furl, local)
                if ok and os.path.exists(local) and \
                   os.path.getsize(local) > 10000:
                    return local
    else:
        log("  No series-level supplementary files found")
        log("  Attempting FTP directory listing...")
        ftp_url = (
            "https://ftp.ncbi.nlm.nih.gov/geo/"
            "series/GSE83nnn/GSE83479/suppl/"
        )
        dir_text = fetch_text(ftp_url)
        if "ERROR" not in dir_text[:20]:
            fnames = re.findall(
                r'href="([^"]+\.gz)"', dir_text
            )
            if not fnames:
                fnames = re.findall(
                    r'(GSE83479[^\s]+\.gz)', dir_text
                )
            log(f"  Found {len(fnames)} files in FTP:")
            for fn in fnames:
                log(f"    {fn}")
                fname = fn.split("/")[-1]
                local = os.path.join(REP_DIR, fname)
                url   = ftp_url + fname
                log(f"  Downloading: {fname}")
                ok = download_file(url, local)
                if ok and os.path.exists(local) and \
                   os.path.getsize(local) > 10000:
                    return local

    log("  Could not download GSE83479 matrix")
    log("  Replication step will be skipped")
    return None


def load_gse83479(matrix_path, samples):
    """Load and parse GSE83479 expression matrix."""
    log(f"\n  Loading: {os.path.basename(matrix_path)}")
    sz = os.path.getsize(matrix_path) / 1e6
    log(f"  File size: {sz:.2f} MB")

    try:
        if matrix_path.endswith(".gz"):
            with gzip.open(matrix_path, "rt") as f:
                df = pd.read_csv(
                    f, sep="\t", index_col=0,
                    low_memory=False
                )
        else:
            df = pd.read_csv(
                matrix_path, sep="\t", index_col=0,
                low_memory=False
            )
    except Exception as e:
        log(f"  Load error: {e}")
        return None, None, None

    log(f"  Shape: {df.shape}")
    log(f"  First 5 index values: "
        f"{list(df.index[:5])}")
    log(f"  First 5 columns: "
        f"{list(df.columns[:5])}")

    # Classify columns
    cdc_t, norm, utuc, _ = classify_gse83479(samples)

    cdc_cols  = [c for c in cdc_t  if c in df.columns]
    norm_cols = [c for c in norm   if c in df.columns]

    # Fallback: if GSM IDs not in columns, try to match
    if not cdc_cols and not norm_cols:
        log("  GSM IDs not in column names — "
            "attempting title match")
        col_lower = [c.lower() for c in df.columns]
        for i, cl in enumerate(col_lower):
            if any(kw in cl for kw in [
                "cdc", "collecting", "bellini"
            ]):
                cdc_cols.append(df.columns[i])
            elif any(kw in cl for kw in [
                "normal", "adjacent"
            ]):
                norm_cols.append(df.columns[i])

    log(f"  CDC tumour columns:  {len(cdc_cols)}")
    log(f"  Normal ref columns:  {len(norm_cols)}")

    if not cdc_cols:
        log("  ERROR: No CDC columns identified")
        return df, None, None

    # Log2 transform if needed
    flat = df[cdc_cols + norm_cols if norm_cols
              else cdc_cols].values.flatten()
    flat = flat[~np.isnan(flat) & (flat > 0)]
    if len(flat) > 0 and flat.max() > 50:
        log("  Linear scale detected — applying log2(x+1)")
        df = np.log2(df + 1)

    tumor_rep  = df[cdc_cols]
    normal_rep = df[norm_cols] if norm_cols else None

    return df, tumor_rep, normal_rep


def run_replication(tumor_rep, normal_rep, tumor_primary,
                    normal_primary):
    """
    Test 12 key genes in GSE83479.
    Compares direction vs GSE89122 findings.
    """
    log(f"\n  REPLICATION PANEL ({len(REPLICATION_PANEL)} genes):")
    log(f"  Stated before running — directions from Doc 89b.")
    log(f"\n  {'Gene':<14} {'Expected':>10} "
        f"{'GSE83479_change':>17} "
        f"{'GSE89122_change':>17} "
        f"{'Match':>8}")
    log(f"  {'-'*72}")

    confirmed = 0
    total     = 0

    results_rep = []

    for gene, (expected, desc) in REPLICATION_PANEL.items():
        # GSE83479
        r89122_change = np.nan
        r83479_change = np.nan
        match_str     = "NOT IN MATRIX"

        # Primary dataset change
        if gene in tumor_primary.index and \
           normal_primary is not None and \
           gene in normal_primary.index:
            t_mean = float(
                tumor_primary.loc[gene].mean()
            )
            n_mean = float(
                normal_primary.loc[gene].mean()
            )
            if n_mean != 0:
                r89122_change = (
                    (t_mean - n_mean) / abs(n_mean) * 100
                )

        # Replication dataset change
        if gene in tumor_rep.index:
            t_mean_r = float(tumor_rep.loc[gene].mean())
            if normal_rep is not None and \
               gene in normal_rep.index:
                n_mean_r = float(
                    normal_rep.loc[gene].mean()
                )
                if n_mean_r != 0:
                    r83479_change = (
                        (t_mean_r - n_mean_r)
                        / abs(n_mean_r) * 100
                    )
            else:
                # No matched normal — use absolute
                r83479_change = t_mean_r

            # Check direction match
            total += 1
            if expected == "DOWN" and r83479_change < -5:
                match_str = "REPLICATED"
                confirmed += 1
            elif expected == "UP" and r83479_change > 5:
                match_str = "REPLICATED"
                confirmed += 1
            elif expected == "FLAT" and abs(
                r83479_change
            ) <= 15:
                match_str = "REPLICATED"
                confirmed += 1
            else:
                match_str = "FAILED"

        r89_str = (f"{r89122_change:>+6.1f}%"
                   if not np.isnan(r89122_change)
                   else "       n/a")
        r83_str = (f"{r83479_change:>+6.1f}%"
                   if not np.isnan(r83479_change)
                   else "       n/a")

        log(f"  {gene:<14} {expected:>10} "
            f"{r83_str:>17} "
            f"{r89_str:>17} "
            f"{match_str:>8}")

        results_rep.append({
            "gene":    gene,
            "expected": expected,
            "gse83479_pct": r83479_change,
            "gse89122_pct": r89122_change,
            "match":   match_str,
        })

    log(f"\n  Replicated: {confirmed}/{total}")
    rate = confirmed / total * 100 if total > 0 else 0
    log(f"  Rate:       {rate:.1f}%")

    log(f"\n  PREDICTION S3-P7 VERDICT:")
    log(f"    Predicted: 8+/{len(REPLICATION_PANEL)} replicate")
    if confirmed >= 8:
        log(f"    CONFIRMED: {confirmed}/{total} replicated")
        log(f"    Independent cohort validates the")
        log(f"    cdRCC false attractor geometry.")
        log(f"    GSE89122 findings are generalisable.")
    elif confirmed >= 5:
        log(f"    PARTIAL: {confirmed}/{total} replicated")
        log(f"    Core findings partially generalise.")
        log(f"    Platform differences (RNA-seq vs")
        log(f"    microarray) may explain gaps.")
    else:
        log(f"    NOT CONFIRMED: {confirmed}/{total}")
        log(f"    Dataset may have different biology")
        log(f"    or platform/normalisation issues.")

    return pd.DataFrame(results_rep)


# ============================================================
# STEP 11 — CORRECTED PAIRED WILCOXON
# Full S2 panel re-tested with rank-based test
# ============================================================

def corrected_paired_analysis(tumor, normal):
    log("")
    log("=" * 65)
    log("STEP 11 — CORRECTED PAIRED WILCOXON ANALYSIS")
    log("  Full S2 gene panel")
    log("  Wilcoxon signed-rank on matched pairs")
    log("  This is the most reliable test for n=6 pairs")
    log("=" * 65)

    # Matched pairs from SAMPLE_MAP
    pairs = []
    seen_patients = set()
    for gsm, (patient, stype) in SAMPLE_MAP.items():
        if stype == "tumor" and patient not in seen_patients:
            # Find matched normal
            matched_n = None
            for gsm2, (pat2, stype2) in SAMPLE_MAP.items():
                if pat2 == patient and stype2 == "normal":
                    matched_n = gsm2
                    break
            if matched_n and gsm in tumor.columns \
               and matched_n in normal.columns:
                pairs.append((gsm, matched_n, patient))
                seen_patients.add(patient)

    log(f"\n  Matched pairs: {len(pairs)}")
    for t_gsm, n_gsm, patient in pairs:
        log(f"    {patient}: {t_gsm} (T) vs {n_gsm} (N)")

    all_genes = (
        PROG_A + PROG_B + PKA_CIRCUIT +
        PPARG_REWIRE + ADCY3_DRIVERS +
        CELSR1_PANEL + CDC3_PANEL +
        MYC_PROLIFERATION + MYC_METABOLIC
    )
    all_genes = list(dict.fromkeys(all_genes))
    genes_present = [g for g in all_genes
                     if g in tumor.index
                     and g in normal.index]

    records = []
    for gene in genes_present:
        diffs = []
        for t_gsm, n_gsm, _ in pairs:
            t_val = float(tumor.loc[gene, t_gsm])
            n_val = float(normal.loc[gene, n_gsm])
            diffs.append(t_val - n_val)

        diffs_arr = np.array(diffs)
        mean_diff = float(np.mean(diffs_arr))

        try:
            if all(d == 0 for d in diffs):
                p_val = 1.0
            else:
                _, p_val = stats.wilcoxon(diffs_arr)
            p_val = float(p_val)
        except Exception:
            p_val = np.nan

        direction = "UP" if mean_diff > 0 else "DOWN"
        records.append({
            "gene":      gene,
            "mean_diff": mean_diff,
            "direction": direction,
            "p_wilcoxon": p_val,
        })

    df_paired = pd.DataFrame(records).sort_values(
        "mean_diff", key=abs, ascending=False
    )

    sig = df_paired[df_paired["p_wilcoxon"] < 0.05]
    log(f"\n  Significant (p<0.05): {len(sig)}/{len(df_paired)}")

    log(f"\n  {'Gene':<16} {'MeanDiff':>10}  "
        f"{'Dir':>5}  {'p_Wilcoxon':>14}")
    log(f"  {'-'*50}")
    for _, row in df_paired.head(40).iterrows():
        log(f"  {row['gene']:<16} "
            f"{row['mean_diff']:>+10.4f}  "
            f"{row['direction']:>5}  "
            f"{fmt_p(row['p_wilcoxon']):>14}")

    out = os.path.join(
        S3_DIR, "paired_wilcoxon_s3.csv"
    )
    df_paired.to_csv(out, index=False)
    log(f"\n  Saved: {out}")

    return df_paired

# ============================================================
# STEP 12 — 9-PANEL FIGURE
# ============================================================

def generate_figure(
    tumor, normal,
    depth, df_spearman,
    score_a, score_b,
    df_paired,
    rep_results,
    stable_genes, inflated_genes,
):
    log("")
    log("=" * 65)
    log("STEP 12 — GENERATING FIGURE")
    log("=" * 65)

    fig = plt.figure(figsize=(22, 18))
    fig.patch.set_facecolor("#0d1117")
    gs  = gridspec.GridSpec(
        3, 3, figure=fig,
        hspace=0.45, wspace=0.38,
    )

    TITLE_C  = "#e6edf3"
    LABEL_C  = "#8b949e"
    BLUE     = "#58a6ff"
    RED      = "#f78166"
    ORANGE   = "#d29922"
    GREEN    = "#3fb950"
    PURPLE   = "#bc8cff"
    BG       = "#161b22"

    def style_ax(ax, title):
        ax.set_facecolor(BG)
        for spine in ax.spines.values():
            spine.set_edgecolor("#30363d")
        ax.tick_params(
            colors=LABEL_C, labelsize=7
        )
        ax.set_title(
            title, color=TITLE_C,
            fontsize=8, pad=5
        )
        ax.xaxis.label.set_color(LABEL_C)
        ax.yaxis.label.set_color(LABEL_C)

    # --------------------------------------------------
    # Panel A — Spearman top 15 each direction
    # --------------------------------------------------
    ax_a = fig.add_subplot(gs[0, 0])
    top_pos = df_spearman[
        df_spearman["spearman_r"] > 0
    ].head(15)
    top_neg = df_spearman[
        df_spearman["spearman_r"] < 0
    ].tail(15).iloc[::-1]
    combined_sp = pd.concat([top_neg, top_pos])
    colours_sp  = [
        RED  if r < 0 else BLUE
        for r in combined_sp["spearman_r"]
    ]
    ax_a.barh(
        range(len(combined_sp)),
        combined_sp["spearman_r"],
        color=colours_sp, alpha=0.85,
    )
    ax_a.set_yticks(range(len(combined_sp)))
    ax_a.set_yticklabels(
        combined_sp.index, fontsize=5
    )
    ax_a.axvline(0, color=LABEL_C,
                 linewidth=0.5, alpha=0.5)
    style_ax(ax_a,
             "A — Spearman Depth Correlations\n"
             "(corrected for CDC4 artefact)")
    ax_a.set_xlabel("Spearman r", fontsize=7)

    # --------------------------------------------------
    # Panel B — Pearson vs Spearman audit
    # --------------------------------------------------
    ax_b = fig.add_subplot(gs[0, 1])
    pearson_vals  = [r for _, r in S2_TOP20_PEARSON]
    genes_audit   = [g for g, _ in S2_TOP20_PEARSON
                     if g in tumor.index]
    spearman_vals = []
    for gene in genes_audit:
        if gene in df_spearman.index:
            spearman_vals.append(
                float(df_spearman.loc[gene, "spearman_r"])
            )
        else:
            spearman_vals.append(np.nan)

    x_idx = range(len(genes_audit))
    p_vals_plot = [r for g, r in S2_TOP20_PEARSON
                   if g in tumor.index]

    ax_b.plot(
        x_idx, [abs(v) for v in p_vals_plot],
        "o-", color=ORANGE, label="Pearson (S2)",
        markersize=4, linewidth=1.2,
    )
    ax_b.plot(
        x_idx, [abs(v) if not np.isnan(v) else None
                for v in spearman_vals],
        "s--", color=BLUE, label="Spearman (S3)",
        markersize=4, linewidth=1.2,
    )
    ax_b.set_xticks(x_idx)
    ax_b.set_xticklabels(
        genes_audit, rotation=45, ha="right",
        fontsize=5,
    )
    ax_b.axhline(
        0.15, color=RED, linewidth=0.8,
        linestyle=":", alpha=0.7,
        label="inflation threshold",
    )
    ax_b.legend(
        fontsize=5, facecolor=BG,
        labelcolor=TITLE_C, framealpha=0.5,
    )
    style_ax(ax_b,
             "B — Pearson vs Spearman Audit\n"
             "(CDC4-inflated genes flagged)")
    ax_b.set_ylabel("|r|", fontsize=7)

    # --------------------------------------------------
    # Panel C — Programme A vs B scatter
    # --------------------------------------------------
    ax_c = fig.add_subplot(gs[0, 2])
    if score_a is not None and score_b is not None:
        ax_c.scatter(
            score_a.values, score_b.values,
            color=PURPLE, s=60, zorder=3,
        )
        for i, (gsm, sa, sb) in enumerate(
            zip(score_a.index,
                score_a.values,
                score_b.values)
        ):
            patient = SAMPLE_MAP.get(
                gsm, ("?","?")
            )[0]
            ax_c.annotate(
                patient, (sa, sb),
                fontsize=5.5, color=LABEL_C,
                xytext=(3, 3),
                textcoords="offset points",
            )
        r_ab, _ = spearman(
            score_a.values, score_b.values
        )
        ax_c.text(
            0.05, 0.92,
            f"r = {r_ab:+.3f}",
            transform=ax_c.transAxes,
            color=TITLE_C, fontsize=7,
        )
        ax_c.set_xlabel(
            "Programme A score\n"
            "(PPARG-KLF5-AGR2 ductal)",
            fontsize=6,
        )
        ax_c.set_ylabel(
            "Programme B score\n"
            "(PAEP-CST1-S100A7 ectopic)",
            fontsize=6,
        )
    style_ax(ax_c,
             "C — Programme A vs B Independence\n"
             "S3-P1: predicted r < 0.3")

    # --------------------------------------------------
    # Panel D — PKA circuit tumour vs normal
    # --------------------------------------------------
    ax_d = fig.add_subplot(gs[1, 0])
    pka_panel = [g for g in [
        "AQP2","SCNN1B","SCNN1G","AVPR2",
        "PRKAR2B","ADCY3","ADCY6",
    ] if g in tumor.index and g in normal.index]
    t_means = [float(tumor.loc[g].mean())
               for g in pka_panel]
    n_means = [float(normal.loc[g].mean())
               for g in pka_panel]
    x       = range(len(pka_panel))
    w       = 0.35
    ax_d.bar(
        [xi - w/2 for xi in x], n_means,
        width=w, color=GREEN,
        alpha=0.7, label="Normal",
    )
    ax_d.bar(
        [xi + w/2 for xi in x], t_means,
        width=w, color=RED,
        alpha=0.7, label="Tumour",
    )
    ax_d.set_xticks(x)
    ax_d.set_xticklabels(
        pka_panel, rotation=45,
        ha="right", fontsize=6,
    )
    ax_d.legend(
        fontsize=5, facecolor=BG,
        labelcolor=TITLE_C, framealpha=0.5,
    )
    style_ax(ax_d,
             "D — PKA Circuit\n"
             "(gap at PRKAR2B confirmed S2)")
    ax_d.set_ylabel("log2 CPM", fontsize=7)

    # --------------------------------------------------
    # Panel E — PPARG rewiring: tumour vs normal r
    # --------------------------------------------------
    ax_e = fig.add_subplot(gs[1, 1])
    rw_genes = [
        g for g in [
            "KLF5","KLF4","CEBPA","CEBPB",
            "AGR2","ESRP1","RXRA","SCD","FASN",
        ]
        if g in tumor.index and g in normal.index
        and "PPARG" in tumor.index
    ]
    pparg_t = tumor.loc["PPARG"].values.astype(float)
    pparg_n = normal.loc["PPARG"].values.astype(float)
    rt_vals = []
    rn_vals = []
    for g in rw_genes:
        rt, _ = spearman(
            pparg_t,
            tumor.loc[g].values.astype(float)
        )
        rn, _ = spearman(
            pparg_n,
            normal.loc[g].values.astype(float)
        )
        rt_vals.append(rt if not np.isnan(rt) else 0)
        rn_vals.append(rn if not np.isnan(rn) else 0)
    x2 = range(len(rw_genes))
    ax_e.bar(
        [xi - w/2 for xi in x2], rn_vals,
        width=w, color=GREEN,
        alpha=0.7, label="Normal",
    )
    ax_e.bar(
        [xi + w/2 for xi in x2], rt_vals,
        width=w, color=BLUE,
        alpha=0.7, label="Tumour",
    )
    ax_e.set_xticks(x2)
    ax_e.set_xticklabels(
        rw_genes, rotation=45,
        ha="right", fontsize=6,
    )
    ax_e.axhline(0, color=LABEL_C,
                 linewidth=0.5, alpha=0.5)
    ax_e.legend(
        fontsize=5, facecolor=BG,
        labelcolor=TITLE_C, framealpha=0.5,
    )
    style_ax(ax_e,
             "E — PPARG Rewiring\n"
             "r(PPARG, partner) in tumour vs normal")
    ax_e.set_ylabel("Spearman r", fontsize=7)

    # --------------------------------------------------
    # Panel F — Paired Wilcoxon top genes
    # --------------------------------------------------
    ax_f = fig.add_subplot(gs[1, 2])
    if df_paired is not None and len(df_paired) > 0:
        sig_paired = df_paired[
            df_paired["p_wilcoxon"] < 0.05
        ].head(20)
        cols_f = [
            BLUE if d > 0 else RED
            for d in sig_paired["mean_diff"]
        ]
        ax_f.barh(
            range(len(sig_paired)),
            sig_paired["mean_diff"],
            color=cols_f, alpha=0.85,
        )
        ax_f.set_yticks(range(len(sig_paired)))
        ax_f.set_yticklabels(
            sig_paired["gene"], fontsize=5
        )
        ax_f.axvline(
            0, color=LABEL_C,
            linewidth=0.5, alpha=0.5,
        )
        ax_f.set_xlabel(
            "Mean paired diff (T-N)", fontsize=7
        )
    style_ax(ax_f,
             "F — Paired Wilcoxon (top 20)\n"
             "Wilcoxon signed-rank across 6 pairs")

    # --------------------------------------------------
    # Panel G — MYC metabolic vs proliferation
    # --------------------------------------------------
    ax_g = fig.add_subplot(gs[2, 0])
    myc_prol = [g for g in MYC_PROLIFERATION
                if g != "MYC" and g in tumor.index]
    myc_meta = [g for g in MYC_METABOLIC
                if g != "MYC" and g in tumor.index]
    myc_vals_arr = tumor.loc["MYC"].values.astype(float) \
        if "MYC" in tumor.index else None

    if myc_vals_arr is not None:
        genes_myc = myc_prol + myc_meta
        rs_myc    = []
        cats_myc  = (
            ["Proliferation"] * len(myc_prol)
            + ["Metabolic"] * len(myc_meta)
        )
        for g in genes_myc:
            r, _ = spearman(
                myc_vals_arr,
                tumor.loc[g].values.astype(float)
            )
            rs_myc.append(r if not np.isnan(r) else 0)

        cols_myc = [
            ORANGE if c == "Proliferation" else GREEN
            for c in cats_myc
        ]
        ax_g.barh(
            range(len(genes_myc)),
            rs_myc, color=cols_myc, alpha=0.85,
        )
        ax_g.set_yticks(range(len(genes_myc)))
        ax_g.set_yticklabels(
            genes_myc, fontsize=5
        )
        ax_g.axvline(
            0, color=LABEL_C,
            linewidth=0.5, alpha=0.5,
        )
        # legend
        from matplotlib.patches import Patch
        ax_g.legend(
            handles=[
                Patch(color=ORANGE,
                      label="Proliferation"),
                Patch(color=GREEN,
                      label="Metabolic"),
            ],
            fontsize=5, facecolor=BG,
            labelcolor=TITLE_C, framealpha=0.5,
        )
        ax_g.set_xlabel("Spearman r(gene,MYC)", fontsize=7)
    style_ax(ax_g,
             "G — MYC Metabolic vs Proliferation\n"
             "S3-P6: r(MYC,MKI67) predicted < 0.4")

    # --------------------------------------------------
    # Panel H — Replication: GSE89122 vs GSE83479
    # --------------------------------------------------
    ax_h = fig.add_subplot(gs[2, 1])
    if rep_results is not None and len(rep_results) > 0:
        rep_genes = list(rep_results["gene"])
        x3        = range(len(rep_genes))
        w3        = 0.35
        r89_vals  = rep_results[
            "gse89122_pct"
        ].fillna(0).values
        r83_vals  = rep_results[
            "gse83479_pct"
        ].fillna(0).values
        ax_h.bar(
            [xi - w3/2 for xi in x3],
            r89_vals, width=w3,
            color=BLUE, alpha=0.8,
            label="GSE89122 (RNA-seq)",
        )
        ax_h.bar(
            [xi + w3/2 for xi in x3],
            r83_vals, width=w3,
            color=ORANGE, alpha=0.8,
            label="GSE83479 (microarray)",
        )
        ax_h.axhline(
            0, color=LABEL_C,
            linewidth=0.5, alpha=0.5,
        )
        ax_h.set_xticks(x3)
        ax_h.set_xticklabels(
            rep_genes, rotation=45,
            ha="right", fontsize=5,
        )
        ax_h.legend(
            fontsize=5, facecolor=BG,
            labelcolor=TITLE_C, framealpha=0.5,
        )
        ax_h.set_ylabel("% change vs normal", fontsize=7)

        # Colour-code bars by match
        confirmed_genes = rep_results[
            rep_results["match"] == "REPLICATED"
        ]["gene"].tolist()
        n_confirmed = len(confirmed_genes)
        ax_h.set_title(
            f"H — Independent Replication\n"
            f"GSE83479 vs GSE89122  "
            f"({n_confirmed}/{len(rep_genes)} replicated)",
            color=TITLE_C, fontsize=8, pad=5,
        )
        ax_h.set_facecolor(BG)
        for spine in ax_h.spines.values():
            spine.set_edgecolor("#30363d")
        ax_h.tick_params(colors=LABEL_C, labelsize=7)
        ax_h.xaxis.label.set_color(LABEL_C)
        ax_h.yaxis.label.set_color(LABEL_C)
    else:
        ax_h.text(
            0.5, 0.5,
            "GSE83479 not available\n"
            "Run again with network access",
            ha="center", va="center",
            color=LABEL_C, fontsize=8,
            transform=ax_h.transAxes,
        )
        style_ax(ax_h,
                 "H — Independent Replication\n"
                 "(GSE83479 not loaded)")

    # --------------------------------------------------
    # Panel I — Summary text
    # --------------------------------------------------
    ax_i = fig.add_subplot(gs[2, 2])
    ax_i.set_facecolor(BG)
    ax_i.axis("off")

    n_stable   = len(stable_genes)
    n_inflated = len(inflated_genes)
    r_ab_val   = np.nan
    if score_a is not None and score_b is not None:
        r_ab_val, _ = spearman(
            score_a.values, score_b.values
        )

    summary_lines = [
        "SCRIPT 3 SUMMARY",
        "cdRCC | GSE89122 | 2026-03-03",
        "",
        "ARTEFACT AUDIT",
        f"  Stable genes:   {n_stable}/20",
        f"  CDC4-inflated:  {n_inflated}/20",
        "",
        "PROGRAMME INDEPENDENCE",
        f"  r(A,B) = {r_ab_val:+.3f}"
        if not np.isnan(r_ab_val)
        else "  r(A,B) = not computed",
        "  Predicted < 0.3",
        "",
        "NOVEL PREDICTIONS TESTED:",
        "  S3-P1: ProgA/B independence",
        "  S3-P2: PPARG rewiring",
        "  S3-P3: ADCY3 driver",
        "  S3-P4: CELSR1 circuit",
        "  S3-P5: CDC3 biology",
        "  S3-P6: MYC metabolic",
        "  S3-P7: Replication",
        "",
        "See log for verdict on each.",
        "",
        "Author: Eric Robert Lawson",
        "OrganismCore | Doc 89b addendum",
    ]

    for i, line in enumerate(summary_lines):
        colour = TITLE_C if i == 0 else LABEL_C
        weight = "bold" if i == 0 else "normal"
        size   = 7.5 if i == 0 else 6.5
        ax_i.text(
            0.04, 0.97 - i * 0.048, line,
            transform=ax_i.transAxes,
            color=colour, fontsize=size,
            fontweight=weight, va="top",
            fontfamily="monospace",
        )

    for spine in ax_i.spines.values():
        spine.set_edgecolor("#30363d")

    style_ax(ax_i, "I — Summary")

    # --------------------------------------------------
    # Super-title and save
    # --------------------------------------------------
    fig.suptitle(
        "cdRCC — Script 3: Spearman Audit, "
        "Module Independence & Replication\n"
        "OrganismCore | GSE89122 + GSE83479 | "
        "Doc 89b addendum | 2026-03-03",
        color=TITLE_C, fontsize=10, y=0.99,
    )

    out_fig = os.path.join(
        S3_DIR, "GSE89122_script3_s3.png"
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
    log("FALSE ATTRACTOR — SCRIPT 3")
    log("Spearman Audit + Module Independence + Replication")
    log("OrganismCore | GSE89122 | 2026-03-03")
    log("=" * 65)

    # Step 0 — Load matrix
    df, tumor, normal, tumor_cols, normal_cols = \
        load_primary_matrix()

    # Step 1 — Build corrected depth score
    depth = build_depth_score(tumor)

    # Step 2 — Spearman depth correlations (full genome)
    df_spearman = spearman_depth_correlations(tumor, depth)

    # Step 3 — Pearson vs Spearman audit
    stable_genes, inflated_genes = pearson_spearman_audit(
        tumor, depth, df_spearman
    )

    # Step 4 — Programme A vs B independence
    score_a, score_b = programme_independence_test(
        tumor, depth
    )

    # Step 5 — PPARG rewiring
    pparg_rewiring_test(tumor, normal)

    # Step 6 — ADCY3 driver
    adcy3_driver_test(tumor)

    # Step 7 — CELSR1 circuit assignment
    celsr1_assignment(tumor)

    # Step 8 — CDC3 examination
    cdc3_examination(tumor, normal)

    # Step 9 — MYC metabolic vs proliferation
    myc_role_test(tumor)

    # Step 10 — GSE83479 independent replication
    rep_results = None
    matrix_path = download_gse83479()
    if matrix_path:
        samples_rep = fetch_gse83479_metadata()
        time.sleep(0.5)
        df_rep, tumor_rep, normal_rep = load_gse83479(
            matrix_path, samples_rep
        )
        if tumor_rep is not None and len(tumor_rep) > 0:
            rep_results = run_replication(
                tumor_rep, normal_rep,
                tumor, normal,
            )
            if rep_results is not None:
                out_rep = os.path.join(
                    S3_DIR, "replication_gse83479.csv"
                )
                rep_results.to_csv(out_rep, index=False)
                log(f"  Saved: {out_rep}")
        else:
            log("  GSE83479 matrix loaded but no "
                "tumour columns found — skipping replication")
    else:
        log("\n  Skipping replication — matrix not available")

    # Step 11 — Corrected paired Wilcoxon
    df_paired = corrected_paired_analysis(tumor, normal)

    # Step 12 — Figure
    generate_figure(
        tumor, normal,
        depth, df_spearman,
        score_a, score_b,
        df_paired,
        rep_results,
        stable_genes, inflated_genes,
    )

    # Final outputs
    log("")
    log("=" * 65)
    log("SCRIPT 3 COMPLETE")
    log(f"\nOutputs in: {S3_DIR}")
    log(f"  depth_correlations_spearman_s3.csv")
    log(f"  paired_wilcoxon_s3.csv")
    log(f"  replication_gse83479.csv  (if downloaded)")
    log(f"  GSE89122_script3_s3.png")
    log(f"  analysis_log_s3.txt")
    log("")
    log("Read the output in this order:")
    log("  1. Step 3 — Pearson vs Spearman audit")
    log("     Which S1/S2 genes are reliable?")
    log("  2. Step 4 — Programme A vs B")
    log("     Are the two modules truly independent?")
    log("  3. Step 5 — PPARG rewiring")
    log("     What did PPARG leave? What did it gain?")
    log("  4. Step 10 — Replication verdict")
    log("     How many of 12 genes replicate?")
    log("  5. Each prediction verdict (CONFIRMED / NOT)")
    log("")
    log("Write Doc 89b addendum after reading.")
    log("=" * 65)

    write_log()


if __name__ == "__main__":
    main()
