"""
cdRCC — Collecting Duct Renal Cell Carcinoma
FALSE ATTRACTOR CIRCUIT ANALYSIS — SCRIPT 2
OrganismCore Cancer Validation #13

Dataset:   GSE89122
           7 CDC tumours
           6 matched adjacent normals
           Illumina HiSeq 2000
           RNA-seq  GRCh38.p13
           6 matched pairs + 1 tumour-only (CDC5)

SCRIPT 1 ESTABLISHED (Doc 89a):
  False attractor identity:
    PAEP high   — Müllerian secretory epithelium
    CST1 high   — mucous/salivary secretory
    S100A7 high — squamous epithelium
    AGR2 high   — ductal secretory ER programme
    IL1RAP high — inflammatory signalling
    (NOT a progenitor state. NOT MYC-driven.)

  Switch gene candidates:
    PRKAR2B  r=-0.946  (PKA/cAMP/vasopressin axis)
    CDS2     r=-0.960  (CDP-DAG synthase)
    OGDHL    r=-0.931  (TCA/mitochondrial)
    ATP6V1G3 -83%      (intercalated cell ID)

  Depth correlations top positive:
    IL1RAP r=+0.960  PRKCI  r=+0.958
    AGR2   r=+0.931  KLF5   r=+0.930
    CYP24A1 r=+0.929 PPARG  r=+0.928
    ESRP1  r=+0.924  INPP4B r=+0.926

  Unexpected: MYC r=-0.941 (suppressed with depth)

SCRIPT 2 PREDICTIONS (locked in Doc 89a,
  2026-03-03, before this script was written):

  PREDICTION 1: IL1RAP CIRCUIT
    r(IL1B, IL1RAP) > 0.5 in tumours
    Autocrine IL-1 loop maintains the attractor

  PREDICTION 2: PKA GAP TEST
    r(AVPR2, PRKAR2B) < 0.4 in tumours
    r(AVPR2, PRKAR2B) > 0.4 in normals
    Collecting duct PKA circuit is broken

  PREDICTION 3: PPARG DRIVER VS MARKER
    r(PPARG, KLF5)  > 0.5 in tumours
    r(PPARG, PAEP)  tested — direction tells role
    r(PPARG, AGR2)  tested — direction tells role

  PREDICTION 4: EZH2 NOT THE LOCK
    EZH2 not elevated > 15% vs normal
    EZH2 not in top 30 depth correlators
    VDR/CYP24A1 axis confirmed as candidate lock

  PREDICTION 5: PRKCI POLARITY LOCK
    PRKCI coordinated with PAR complex genes
    r(PRKCI, LLGL2) tested

  PREDICTION 6: CDC4 ROBUSTNESS
    Top 10 depth correlators stable
    when CDC4 is excluded

This script:
  1. Reuses Script 1 downloads (checks for cached files)
  2. Reuses Script 1 normalised matrix
  3. Runs extended gene panel on confirmed circuits
  4. Tests all 6 predictions from Doc 89a
  5. Derives corrected depth score from Script 1 top genes
  6. Compares S1 vs S2 depth scores
  7. Runs CDC4 robustness check
  8. Writes to results_s2/ (Script 1 untouched)

Author:    Eric Robert Lawson
Framework: OrganismCore
Protocol:  Phase 3 — Script 2 Circuit Analysis
Document:  Doc 89b (to be written after output)
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
S2_DIR      = os.path.join(BASE_DIR, "results_s2")
LOG_FILE    = os.path.join(S2_DIR, "analysis_log_s2.txt")

# Script 1 outputs — reused, not modified
S1_LOG2CPM  = os.path.join(RESULTS_DIR,
                            "GSE89122_log2cpm.csv")
S1_DEPTH    = os.path.join(RESULTS_DIR,
                            "depth_correlations.csv")
S1_SADDLE   = os.path.join(RESULTS_DIR,
                            "saddle_scan.csv")

os.makedirs(S2_DIR, exist_ok=True)

# ============================================================
# CONFIRMED SAMPLE MAP (locked in Phase 0)
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

TUMOR_SAMPLES  = [g for g, (_, t) in SAMPLE_MAP.items()
                  if t == "tumor"]
NORMAL_SAMPLES = [g for g, (_, t) in SAMPLE_MAP.items()
                  if t == "normal"]

MATCHED_PAIRS = [
    ("CDC1", "GSM2359144", "GSM2359145"),
    ("CDC2", "GSM2359146", "GSM2359147"),
    ("CDC3", "GSM2359148", "GSM2359149"),
    ("CDC4", "GSM2359150", "GSM2359151"),
    ("CDC6", "GSM2359153", "GSM2359154"),
    ("CDC7", "GSM2359155", "GSM2359156"),
]

# CDC4 tumour is the low-library outlier
CDC4_TUMOR = "GSM2359150"
TUMOR_NO_CDC4 = [g for g in TUMOR_SAMPLES
                 if g != CDC4_TUMOR]

# ============================================================
# SCRIPT 2 EXTENDED GENE PANEL
# Derived entirely from Script 1 geometry (Doc 89a).
# Not pre-loaded cancer knowledge.
# ============================================================

# --- Circuit genes: PKA/vasopressin gap test ---
PKA_CIRCUIT = [
    "AVPR2",    # vasopressin V2 receptor
    "AVPR1A",   # vasopressin V1A (alt receptor)
    "ADCY3",    # adenylyl cyclase 3
    "ADCY6",    # adenylyl cyclase 6 (kidney CD)
    "PRKAR1A",  # PKA regulatory Ialpha
    "PRKAR2A",  # PKA regulatory IIalpha
    "PRKAR2B",  # PKA regulatory IIbeta — top S1 switch
    "PRKACB",   # PKA catalytic beta
    "PRKACA",   # PKA catalytic alpha
    "AQP2",     # principal cell effector
    "AQP3",     # basolateral water channel
    "AQP4",     # basolateral
    "SCNN1A",   # epithelial Na channel alpha
    "SCNN1B",   # epithelial Na channel beta
    "SCNN1G",   # epithelial Na channel gamma
]

# --- IL-1 autocrine loop test ---
IL1_CIRCUIT = [
    "IL1RAP",   # top depth correlator S1 r=+0.960
    "IL1B",     # IL-1 beta (autocrine ligand?)
    "IL1A",     # IL-1 alpha
    "IL1R1",    # IL-1 receptor 1
    "IL1R2",    # decoy receptor
    "IL1RN",    # IL-1 receptor antagonist
    "NLRP3",    # inflammasome sensor
    "IL18",     # related IL
    "NFKB1",    # downstream TF
    "NFKBIA",   # IkB (NF-kB inhibitor)
    "TNFA",     # TNF alpha (related pathway)
    "IL6",      # IL-6 (parallel inflammatory)
]

# --- PPARG driver/marker test ---
PPARG_CIRCUIT = [
    "PPARG",    # depth r=+0.928
    "RXRA",     # PPARG obligate heterodimer
    "KLF5",     # depth r=+0.930
    "KLF4",     # related KLF
    "KLF2",     # related KLF
    "FABP4",    # canonical PPARG target (adipocyte)
    "ADIPOQ",   # PPARG target
    "CEBPA",    # PPARG cooperating TF
    "CEBPB",    # related
    "FASN",     # lipid synthesis (PPARG target)
    "SCD",      # stearoyl-CoA desaturase
    "ACACA",    # acetyl-CoA carboxylase
]

# --- VDR/CYP24A1 lock test ---
VDR_CIRCUIT = [
    "VDR",      # vitamin D receptor
    "CYP24A1",  # 24-hydroxylase (depth r=+0.929)
    "CYP27B1",  # 1alpha-hydroxylase (activates VitD)
    "CYP2R1",   # 25-hydroxylase
    "GC",       # vitamin D binding protein
    "CUBN",     # cubilin (proximal tubule VitD uptake)
    "LRP2",     # megalin (VitD endocytosis)
    "CASR",     # calcium sensing receptor
    "PTH",      # parathyroid hormone
    "PTHLH",    # PTH-related protein
]

# --- EZH2 / epigenetic lock test ---
EPIGENETIC = [
    "EZH2",     # PRC2 methyltransferase
    "EED",      # PRC2 component
    "SUZ12",    # PRC2 component
    "BMI1",     # PRC1 component
    "DNMT3A",   # de novo methylation
    "DNMT3B",   # de novo methylation
    "TET2",     # demethylation
    "HDAC1",    # deacetylase
    "HDAC2",    # deacetylase
    "KDM6A",    # H3K27me3 demethylase
    "KDM6B",    # H3K27me3 demethylase
    "ASXL1",    # chromatin modifier
    "SETD2",    # H3K36me3 — mutation in ccRCC
]

# --- PRKCI polarity complex test ---
POLARITY = [
    "PRKCI",    # top depth correlator r=+0.958
    "PRKCZ",    # atypical PKC zeta (related)
    "PARD3",    # PAR3 — polarity complex
    "PARD6A",   # PAR6 alpha
    "PARD6B",   # PAR6 beta
    "LLGL2",    # LATS oncogene — antagonised by PRKCI
    "LLGL1",    # related
    "SCRIB",    # scribble complex
    "DLG1",     # discs large
    "CDC42",    # Rho GTPase (PAR complex activator)
    "RAC1",     # Rho GTPase
    "RHOA",     # Rho GTPase
]

# --- Collecting duct identity genes ---
CD_IDENTITY = [
    "ATP6V1G3", # intercalated cell V-ATPase (S1: -83%)
    "ATP6V0A4", # V-ATPase a4 subunit (type A IC)
    "FOXI1",    # intercalated cell master TF
    "TFCP2L1",  # CD progenitor/PC TF
    "HNF1B",    # CD development TF
    "HNF4A",    # tubular differentiation
    "PAX8",     # renal epithelial TF
    "KRT7",     # collecting duct keratin
    "KRT8",     # collecting duct keratin
    "KRT18",    # collecting duct keratin
    "KRT19",    # ductal keratin
    "CALB1",    # calbindin (distal nephron)
    "UMOD",     # uromodulin (TALH marker)
]

# --- False attractor identity (confirmed S1) ---
FA_IDENTITY = [
    "PAEP",     # Müllerian secretory — top FA marker
    "CST1",     # mucous secretory — paired confirmed
    "S100A7",   # squamous — paired confirmed
    "AGR2",     # ductal secretory ER — depth r=+0.931
    "IL1RAP",   # inflammatory — top depth r=+0.960
    "ANXA8",    # squamous/urothelial
    "ANXA8L1",  # squamous/urothelial
    "LY6D",     # urothelial/squamous
    "HOXC13",   # hair/ectodermal HOX
    "BARX1",    # gastric homeodomain
    "NPBWR1",   # neuropeptide receptor
    "ISL2",     # paired confirmed
    "ESRP1",    # epithelial splicing — depth r=+0.924
    "ESRP2",    # related
    "GPRC5A",   # depth r=+0.925
    "SERPINA1", # depth r=+0.941
]

# --- Scaffold/proliferation ---
SCAFFOLD = [
    "MYC",      # S1: r=-0.941 SUPPRESSED with depth
    "MYCN",     # N-myc
    "MKI67",    # proliferation
    "CCND1",    # cyclin D1
    "CDKN1A",   # p21 — differentiation arrest
    "CDKN2A",   # p16
    "TP53",     # tumour suppressor
    "PTEN",     # PI3K suppressor
    "INPP4B",   # depth r=+0.926
    "AKT1",     # PI3K effector
    "MTOR",     # downstream PI3K
    "VHL",      # ccRCC suppressor (not expected)
    "HIF1A",    # hypoxia (downstream VHL)
    "HIF2A",    # EPAS1 — ccRCC driver
]

# --- Additional depth-correlated genes from S1 ---
DEPTH_EXTENDED = [
    "IL1RAP",   # r=+0.960
    "CDS2",     # r=-0.960
    "PRKCI",    # r=+0.958
    "RHBDL2",   # r=+0.946
    "PRKAR2B",  # r=-0.946
    "ZBED6CL",  # r=-0.944
    "B4GALT5",  # r=+0.943
    "SERPINA1", # r=+0.941
    "ADPRM",    # r=-0.941
    "MYC",      # r=-0.941
    "AGR2",     # r=+0.931
    "KLF5",     # r=+0.930
    "CYP24A1",  # r=+0.929
    "PPARG",    # r=+0.928
    "INPP4B",   # r=+0.926
    "GPRC5A",   # r=+0.925
    "ESRP1",    # r=+0.924
    "MIR31HG",  # r=+0.924
]

# Full panel — deduplicated
ALL_S2_GENES = list(dict.fromkeys(
    PKA_CIRCUIT + IL1_CIRCUIT + PPARG_CIRCUIT +
    VDR_CIRCUIT + EPIGENETIC + POLARITY +
    CD_IDENTITY + FA_IDENTITY + SCAFFOLD +
    DEPTH_EXTENDED
))

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
# UTILITY
# ============================================================

def fmt_p(p):
    if np.isnan(p):      return "p=NA     "
    if p < 1e-10:        return f"p={p:.2e} ***"
    if p < 0.001:        return f"p={p:.2e} ***"
    if p < 0.01:         return f"p={p:.2e}  **"
    if p < 0.05:         return f"p={p:.4f}   *"
    return                      f"p={p:.4f}  ns"

def pearson_safe(a, b):
    a = np.array(a, dtype=float)
    b = np.array(b, dtype=float)
    mask = ~(np.isnan(a) | np.isnan(b))
    a, b = a[mask], b[mask]
    if len(a) < 3:
        return np.nan, np.nan
    if np.std(a) < 1e-8 or np.std(b) < 1e-8:
        return np.nan, np.nan
    return stats.pearsonr(a, b)

def mw_test(group1, group2):
    group1 = [x for x in group1 if not np.isnan(x)]
    group2 = [x for x in group2 if not np.isnan(x)]
    if len(group1) < 2 or len(group2) < 2:
        return np.nan
    _, p = stats.mannwhitneyu(
        group1, group2, alternative="two-sided"
    )
    return p

def norm01(s):
    mn, mx = s.min(), s.max()
    if mx > mn:
        return (s - mn) / (mx - mn)
    return pd.Series(0.5, index=s.index)

# ============================================================
# STEP 1: LOAD SCRIPT 1 MATRIX
# Reuse exactly. Do not re-download.
# ============================================================

def load_s1_matrix():
    log("=" * 65)
    log("STEP 1: LOADING SCRIPT 1 MATRIX")
    log(f"  {S1_LOG2CPM}")
    log("=" * 65)

    if not os.path.exists(S1_LOG2CPM):
        log(f"  ERROR: Script 1 matrix not found.")
        log(f"  Run cdrcc_false_attractor.py first.")
        return None

    df = pd.read_csv(S1_LOG2CPM, index_col=0)
    log(f"  Shape: {df.shape[0]} genes × "
        f"{df.shape[1]} samples")
    log(f"  Columns: {list(df.columns)}")

    # Verify all expected samples present
    for gsm in SAMPLE_MAP:
        if gsm not in df.columns:
            log(f"  WARNING: {gsm} missing from matrix")

    tumor_cols  = [c for c in df.columns
                   if c in TUMOR_SAMPLES]
    normal_cols = [c for c in df.columns
                   if c in NORMAL_SAMPLES]
    log(f"  Tumour cols: {len(tumor_cols)}")
    log(f"  Normal cols: {len(normal_cols)}")

    return df

# ============================================================
# STEP 2: LOAD SCRIPT 1 DEPTH CORRELATIONS
# ============================================================

def load_s1_depth_corrs():
    log("")
    log("=" * 65)
    log("STEP 2: LOADING SCRIPT 1 DEPTH CORRELATIONS")
    log("=" * 65)

    if not os.path.exists(S1_DEPTH):
        log("  ERROR: Script 1 depth correlations not found")
        return None

    df = pd.read_csv(S1_DEPTH)
    log(f"  Loaded {len(df)} depth correlations")

    top_pos = df[df["r"] > 0].head(10)
    top_neg = df[df["r"] < 0].head(10)

    log("\n  Top positive correlators (FA axis):")
    for _, row in top_pos.iterrows():
        log(f"    {row['gene']:<20} r={row['r']:+.4f}  "
            f"p={row['p_value']:.2e}")

    log("\n  Top negative correlators (switch axis):")
    for _, row in top_neg.iterrows():
        log(f"    {row['gene']:<20} r={row['r']:+.4f}  "
            f"p={row['p_value']:.2e}")

    return df

# ============================================================
# STEP 3: BUILD S2 CORRECTED DEPTH SCORE
#
# Script 2 depth score uses the two highest-|r| genes
# from Script 1 as the axis:
#   Top suppressed: CDS2  (r=-0.960)
#   Top elevated:   IL1RAP (r=+0.960)
#
# Depth_S2 = mean(
#   1 - norm(CDS2),   <- suppression
#   norm(IL1RAP)      <- elevation
# )
# ============================================================

def build_s2_depth(log2_cpm, s1_corrs):
    log("")
    log("=" * 65)
    log("STEP 3: CORRECTED DEPTH SCORE (S2)")
    log("  Top S1 suppressed: CDS2  (r=-0.960)")
    log("  Top S1 elevated:   IL1RAP (r=+0.960)")
    log("  Depth_S2 = mean(1-norm(CDS2), norm(IL1RAP))")
    log("=" * 65)

    tumor_cols = [c for c in log2_cpm.columns
                  if c in TUMOR_SAMPLES]
    all_cols   = [c for c in log2_cpm.columns
                  if c in list(SAMPLE_MAP.keys())]

    # Confirm genes present
    top_switch = "CDS2"
    top_fa     = "IL1RAP"

    if top_switch not in log2_cpm.index:
        # Find best available from S1 corrs
        for g in s1_corrs[s1_corrs["r"] < 0]["gene"]:
            if g in log2_cpm.index:
                top_switch = g
                log(f"  CDS2 not found — using {top_switch}")
                break

    if top_fa not in log2_cpm.index:
        for g in s1_corrs[s1_corrs["r"] > 0]["gene"]:
            if g in log2_cpm.index:
                top_fa = g
                log(f"  IL1RAP not found — using {top_fa}")
                break

    log(f"  Switch gene: {top_switch}")
    log(f"  FA marker:   {top_fa}")

    # Compute on tumour samples
    tumor_expr = log2_cpm[tumor_cols].T

    sw_vals = tumor_expr[top_switch]
    fa_vals = tumor_expr[top_fa]

    depth_s2 = (
        (1 - norm01(sw_vals)) + norm01(fa_vals)
    ) / 2

    log(f"\n  S2 Depth ({len(tumor_cols)} tumours):")
    log(f"    Mean  : {depth_s2.mean():.4f}")
    log(f"    Median: {depth_s2.median():.4f}")
    log(f"    Std   : {depth_s2.std():.4f}")
    log(f"    Min   : {depth_s2.min():.4f}")
    log(f"    Max   : {depth_s2.max():.4f}")

    log(f"\n  Per-sample S2 depth:")
    for gsm in tumor_cols:
        patient, _ = SAMPLE_MAP.get(gsm, ("?", "?"))
        log(f"    {gsm} ({patient}): {depth_s2[gsm]:.4f}")

    # Also build S1 depth for comparison
    # S1 used top 50 suppressed + top 50 elevated
    # Reconstruct from saddle scan
    saddle = None
    if os.path.exists(S1_SADDLE):
        saddle = pd.read_csv(S1_SADDLE)

    depth_s1 = None
    if saddle is not None:
        sig_down = saddle[
            (saddle["direction"] == "DOWN")
            & (saddle["p_value"] < 0.05)
        ].head(50)
        sig_up = saddle[
            (saddle["direction"] == "UP")
            & (saddle["p_value"] < 0.05)
        ].head(50)

        down_genes = [g for g in sig_down["gene"].values
                      if g in log2_cpm.index][:50]
        up_genes   = [g for g in sig_up["gene"].values
                      if g in log2_cpm.index][:50]

        if down_genes and up_genes:
            sw_m   = tumor_expr[down_genes].mean(axis=1)
            fa_m   = tumor_expr[up_genes].mean(axis=1)
            depth_s1 = (
                (1 - norm01(sw_m)) + norm01(fa_m)
            ) / 2

    # Compare S1 vs S2
    if depth_s1 is not None:
        aligned = depth_s1.reindex(tumor_cols).dropna()
        d2_aligned = depth_s2.reindex(aligned.index)
        if len(aligned) >= 3:
            r_s1s2, p_s1s2 = pearson_safe(
                aligned.values, d2_aligned.values
            )
            log(f"\n  S1 vs S2 depth comparison:")
            log(f"    r(S1, S2) = {r_s1s2:+.4f}  "
                f"p={p_s1s2:.4f}")
            if r_s1s2 > 0.9:
                log(f"    SAME BIOLOGY — both axes capture "
                    f"the same attractor")
            elif r_s1s2 > 0.5:
                log(f"    PARTIAL CONCORDANCE — S2 refines S1")
            else:
                log(f"    DIFFERENT AXES — S2 captures "
                    f"distinct signal from S1")
        else:
            r_s1s2, p_s1s2 = np.nan, np.nan
    else:
        r_s1s2, p_s1s2 = np.nan, np.nan
        depth_s1 = None

    return depth_s2, depth_s1, top_switch, top_fa, r_s1s2

# ============================================================
# STEP 4: PREDICTION 1 — IL1RAP AUTOCRINE CIRCUIT TEST
# ============================================================

def test_il1_circuit(log2_cpm, depth_s2):
    log("")
    log("=" * 65)
    log("STEP 4: PREDICTION 1 — IL1 AUTOCRINE CIRCUIT")
    log("  Prediction: r(IL1B, IL1RAP) > 0.5 in tumours")
    log("  Autocrine IL-1 loop maintains the attractor")
    log("=" * 65)

    tumor_cols  = [c for c in log2_cpm.columns
                   if c in TUMOR_SAMPLES]
    normal_cols = [c for c in log2_cpm.columns
                   if c in NORMAL_SAMPLES]

    il1_genes = [g for g in IL1_CIRCUIT
                 if g in log2_cpm.index]

    log(f"\n  IL-1 panel genes found: "
        f"{len(il1_genes)}/{len(IL1_CIRCUIT)}")
    log(f"  Genes: {il1_genes}")

    if not il1_genes:
        log("  SKIP: No IL-1 circuit genes in matrix")
        return None

    # Expression in tumour vs normal
    log(f"\n  {'Gene':<12} {'Normal':>8} {'Tumour':>8} "
        f"{'Change':>9}  {'p':>14}")
    log(f"  {'-'*58}")

    results = []
    for gene in il1_genes:
        if gene not in log2_cpm.index:
            continue
        tv = log2_cpm.loc[gene, tumor_cols].values
        nv = log2_cpm.loc[gene, normal_cols].values
        nm = nv.mean()
        tm = tv.mean()
        chg = ((tm - nm) / max(abs(nm), 0.01) * 100)
        p = mw_test(tv, nv)
        log(f"  {gene:<12} {nm:>8.4f} {tm:>8.4f} "
            f"{chg:>+8.1f}%  {fmt_p(p)}")
        results.append({
            "gene": gene, "normal_mean": nm,
            "tumor_mean": tm, "change_pct": chg,
            "p_value": p,
        })

    # Intra-tumour correlations
    log(f"\n  INTRA-TUMOUR CORRELATIONS:")
    log(f"  {'Pair':<24} {'r':>8}  p-value")
    log(f"  {'-'*42}")

    tumor_expr = log2_cpm[tumor_cols].T

    key_pairs = [
        ("IL1B",  "IL1RAP"),
        ("IL1A",  "IL1RAP"),
        ("IL1B",  "IL1R1"),
        ("IL1RN", "IL1RAP"),
        ("IL1RN", "IL1B"),
        ("NFKB1", "IL1B"),
        ("NFKB1", "IL1RAP"),
        ("IL6",   "IL1B"),
    ]

    circuit_confirmed = False
    for g1, g2 in key_pairs:
        if (g1 not in log2_cpm.index or
                g2 not in log2_cpm.index):
            continue
        r, p = pearson_safe(
            tumor_expr[g1].values,
            tumor_expr[g2].values
        )
        log(f"  {g1+' → '+g2:<24} {r:>+8.4f}  "
            f"{fmt_p(p)}")
        if g1 == "IL1B" and g2 == "IL1RAP":
            if not np.isnan(r) and r > 0.5:
                circuit_confirmed = True

    # Depth correlations for IL-1 genes
    log(f"\n  DEPTH CORRELATIONS (IL-1 genes):")
    log(f"  {'Gene':<12} {'r':>8}  p-value")
    log(f"  {'-'*30}")
    for gene in il1_genes:
        if gene not in log2_cpm.index:
            continue
        gene_vals = log2_cpm.loc[gene, tumor_cols].values
        r, p = pearson_safe(depth_s2.values, gene_vals)
        log(f"  {gene:<12} {r:>+8.4f}  {fmt_p(p)}")

    # Verdict
    log(f"\n  PREDICTION 1 VERDICT:")
    log(f"  Predicted: r(IL1B, IL1RAP) > 0.5")
    if circuit_confirmed:
        log(f"  CONFIRMED: autocrine IL-1 loop present")
    else:
        log(f"  NOT CONFIRMED or IL1B not detectable")
        log(f"  IL1RAP elevation may reflect receptor")
        log(f"  upregulation without autocrine ligand")

    return pd.DataFrame(results)

# ============================================================
# STEP 5: PREDICTION 2 — PKA GAP TEST
# r(AVPR2, PRKAR2B) in tumours vs normals
# ============================================================

def test_pka_gap(log2_cpm, depth_s2):
    log("")
    log("=" * 65)
    log("STEP 5: PREDICTION 2 — PKA/VASOPRESSIN GAP TEST")
    log("  Prediction: r(AVPR2, PRKAR2B) < 0.4 in tumours")
    log("  Prediction: r(AVPR2, PRKAR2B) > 0.4 in normals")
    log("  Circuit: AVPR2 → ADCY6 → cAMP →")
    log("           PRKAR2B/PKA → AQP2 insertion")
    log("=" * 65)

    tumor_cols  = [c for c in log2_cpm.columns
                   if c in TUMOR_SAMPLES]
    normal_cols = [c for c in log2_cpm.columns
                   if c in NORMAL_SAMPLES]

    pka_genes = [g for g in PKA_CIRCUIT
                 if g in log2_cpm.index]

    log(f"\n  PKA circuit genes found: "
        f"{len(pka_genes)}/{len(PKA_CIRCUIT)}")
    log(f"  Genes: {pka_genes}")

    # Expression table
    log(f"\n  {'Gene':<12} {'Normal':>8} {'Tumour':>8} "
        f"{'Change':>9}  {'p':>14}")
    log(f"  {'-'*58}")

    for gene in pka_genes:
        tv = log2_cpm.loc[gene, tumor_cols].values
        nv = log2_cpm.loc[gene, normal_cols].values
        nm = nv.mean()
        tm = tv.mean()
        chg = ((tm - nm) / max(abs(nm), 0.01) * 100)
        p  = mw_test(tv, nv)
        log(f"  {gene:<12} {nm:>8.4f} {tm:>8.4f} "
            f"{chg:>+8.1f}%  {fmt_p(p)}")

    # Gap test: intra-tumour vs intra-normal correlations
    log(f"\n  CIRCUIT CONNECTIONS — TUMOUR vs NORMAL:")
    log(f"  {'Pair':<22} {'r_tumour':>10} "
        f"{'r_normal':>10}  Architecture")
    log(f"  {'-'*58}")

    tumor_expr  = log2_cpm[tumor_cols].T
    normal_expr = log2_cpm[normal_cols].T

    circuit_pairs = [
        ("AVPR2",   "PRKAR2B"),
        ("AVPR2",   "AQP2"),
        ("AVPR2",   "ADCY6"),
        ("ADCY6",   "PRKAR2B"),
        ("PRKAR2B", "AQP2"),
        ("PRKAR2B", "PRKACB"),
        ("PRKAR2B", "PRKACA"),
        ("AQP2",    "AQP3"),
        ("SCNN1A",  "PRKAR2B"),
    ]

    gap_confirmed = False
    for g1, g2 in circuit_pairs:
        if (g1 not in log2_cpm.index or
                g2 not in log2_cpm.index):
            continue
        rt, pt = pearson_safe(
            tumor_expr[g1].values,
            tumor_expr[g2].values
        )
        rn, pn = pearson_safe(
            normal_expr[g1].values,
            normal_expr[g2].values
        )
        arch = "?"
        if not np.isnan(rt) and not np.isnan(rn):
            if abs(rt) < 0.4 and abs(rn) > 0.4:
                arch = "GAP CONFIRMED"
                gap_confirmed = True
            elif abs(rt) > 0.5:
                arch = "INTACT"
            elif abs(rt) < 0.3:
                arch = "BROKEN/LOW"
            else:
                arch = "WEAK"
        rt_s = f"{rt:+.3f}" if not np.isnan(rt) else "  NA"
        rn_s = f"{rn:+.3f}" if not np.isnan(rn) else "  NA"
        log(f"  {g1+' → '+g2:<22} "
            f"{rt_s:>10}  {rn_s:>10}  {arch}")

    # Depth correlations for PKA genes
    log(f"\n  DEPTH CORRELATIONS (PKA circuit):")
    log(f"  {'Gene':<12} {'r':>8}  p-value")
    log(f"  {'-'*30}")
    for gene in pka_genes:
        gene_vals = log2_cpm.loc[gene, tumor_cols].values
        r, p = pearson_safe(depth_s2.values, gene_vals)
        log(f"  {gene:<12} {r:>+8.4f}  {fmt_p(p)}")

    # Verdict
    log(f"\n  PREDICTION 2 VERDICT:")
    log(f"  Predicted: AVPR2→PRKAR2B gap in tumours")
    if gap_confirmed:
        log(f"  CONFIRMED: PKA circuit broken in tumours, "
            f"intact in normals")
    else:
        log(f"  NOT CONFIRMED or genes below detection")
        log(f"  PRKAR2B suppression confirmed in S1 (-0.946)")
        log(f"  Absence of AVPR2 signal means:")
        log(f"    Either receptor itself is gone")
        log(f"    Or entire upstream arm not expressed")
        log(f"    in this tumour type")

    return gap_confirmed

# ============================================================
# STEP 6: PREDICTION 3 — PPARG DRIVER VS MARKER
# ============================================================

def test_pparg_circuit(log2_cpm, depth_s2):
    log("")
    log("=" * 65)
    log("STEP 6: PREDICTION 3 — PPARG DRIVER VS MARKER")
    log("  Prediction: r(PPARG, KLF5) > 0.5 in tumours")
    log("  Determines if PPARG drives the attractor")
    log("  or is a co-marker of the same state")
    log("=" * 65)

    tumor_cols  = [c for c in log2_cpm.columns
                   if c in TUMOR_SAMPLES]
    normal_cols = [c for c in log2_cpm.columns
                   if c in NORMAL_SAMPLES]

    pparg_genes = [g for g in PPARG_CIRCUIT
                   if g in log2_cpm.index]

    log(f"\n  PPARG panel genes found: "
        f"{len(pparg_genes)}/{len(PPARG_CIRCUIT)}")

    # Expression table
    log(f"\n  {'Gene':<12} {'Normal':>8} {'Tumour':>8} "
        f"{'Change':>9}  {'p':>14}")
    log(f"  {'-'*58}")
    for gene in pparg_genes:
        tv = log2_cpm.loc[gene, tumor_cols].values
        nv = log2_cpm.loc[gene, normal_cols].values
        nm = nv.mean()
        tm = tv.mean()
        chg = ((tm - nm) / max(abs(nm), 0.01) * 100)
        p  = mw_test(tv, nv)
        log(f"  {gene:<12} {nm:>8.4f} {tm:>8.4f} "
            f"{chg:>+8.1f}%  {fmt_p(p)}")

    # Circuit correlations in tumours
    log(f"\n  INTRA-TUMOUR CORRELATIONS (PPARG circuit):")
    log(f"  {'Pair':<24} {'r':>8}  p-value")
    log(f"  {'-'*42}")

    tumor_expr = log2_cpm[tumor_cols].T

    pparg_pairs = [
        ("PPARG",  "KLF5"),    # key prediction
        ("PPARG",  "RXRA"),    # obligate partner
        ("PPARG",  "PAEP"),    # FA marker
        ("PPARG",  "AGR2"),    # ductal identity
        ("PPARG",  "IL1RAP"),  # top depth gene
        ("PPARG",  "CEBPA"),
        ("KLF5",   "PAEP"),
        ("KLF5",   "AGR2"),
        ("KLF5",   "IL1RAP"),
        ("KLF5",   "ESRP1"),
        ("RXRA",   "CYP24A1"), # VDR heterodimer test
    ]

    pparg_is_driver = False
    for g1, g2 in pparg_pairs:
        if (g1 not in log2_cpm.index or
                g2 not in log2_cpm.index):
            continue
        r, p = pearson_safe(
            tumor_expr[g1].values,
            tumor_expr[g2].values
        )
        r_s = f"{r:+.4f}" if not np.isnan(r) else "    NA"
        log(f"  {g1+' vs '+g2:<24} {r_s:>8}  {fmt_p(p)}")
        if g1 == "PPARG" and g2 == "KLF5":
            if not np.isnan(r) and r > 0.5:
                pparg_is_driver = True

    # PPARG depth correlation
    log(f"\n  PPARG depth correlations:")
    for gene in ["PPARG", "KLF5", "RXRA", "CEBPA"]:
        if gene not in log2_cpm.index:
            continue
        gene_vals = log2_cpm.loc[gene, tumor_cols].values
        r, p = pearson_safe(depth_s2.values, gene_vals)
        log(f"  {gene:<12} r={r:+.4f}  {fmt_p(p)}")

    # Verdict
    log(f"\n  PREDICTION 3 VERDICT:")
    log(f"  Predicted: PPARG drives attractor "
        f"(r(PPARG,KLF5) > 0.5)")
    if pparg_is_driver:
        log(f"  CONFIRMED: PPARG is a driver of the "
            f"attractor identity")
        log(f"  PPARG agonist paradox: may push deeper")
        log(f"  PPARG inhibitor OR upstream pathway")
        log(f"  disruption is the therapeutic target")
    else:
        log(f"  NOT CONFIRMED: PPARG is a co-marker")
        log(f"  PPARG and KLF5 elevated in same state")
        log(f"  but not causally connected here")
        log(f"  Upstream driver remains to be identified")

    return pparg_is_driver

# ============================================================
# STEP 7: PREDICTION 4 — EZH2 LOCK TEST
# ============================================================

def test_ezh2_lock(log2_cpm, depth_s2):
    log("")
    log("=" * 65)
    log("STEP 7: PREDICTION 4 — EZH2 / EPIGENETIC LOCK")
    log("  Prediction: EZH2 NOT elevated (< +15%)")
    log("  Prediction: EZH2 NOT in top depth correlators")
    log("  VDR/CYP24A1 axis is the candidate lock instead")
    log("=" * 65)

    tumor_cols  = [c for c in log2_cpm.columns
                   if c in TUMOR_SAMPLES]
    normal_cols = [c for c in log2_cpm.columns
                   if c in NORMAL_SAMPLES]

    epig_genes = [g for g in EPIGENETIC
                  if g in log2_cpm.index]
    vdr_genes  = [g for g in VDR_CIRCUIT
                  if g in log2_cpm.index]

    all_lock_genes = list(dict.fromkeys(
        epig_genes + vdr_genes
    ))

    log(f"\n  Epigenetic genes found: "
        f"{len(epig_genes)}/{len(EPIGENETIC)}")
    log(f"  VDR circuit genes found: "
        f"{len(vdr_genes)}/{len(VDR_CIRCUIT)}")

    log(f"\n  {'Gene':<12} {'Normal':>8} {'Tumour':>8} "
        f"{'Change':>9}  {'p':>14}  r_depth")
    log(f"  {'-'*68}")

    ezh2_elevated   = False
    cyp24a1_elevated = False
    vdr_suppressed  = False

    results = []
    for gene in all_lock_genes:
        tv = log2_cpm.loc[gene, tumor_cols].values
        nv = log2_cpm.loc[gene, normal_cols].values
        nm = nv.mean()
        tm = tv.mean()
        chg = ((tm - nm) / max(abs(nm), 0.01) * 100)
        p  = mw_test(tv, nv)
        r_d, _ = pearson_safe(depth_s2.values, tv)
        r_s = f"{r_d:+.3f}" if not np.isnan(r_d) else "   NA"
        log(f"  {gene:<12} {nm:>8.4f} {tm:>8.4f} "
            f"{chg:>+8.1f}%  {fmt_p(p)}  {r_s}")
        results.append({
            "gene": gene, "normal_mean": nm,
            "tumor_mean": tm, "change_pct": chg,
            "p_value": p, "r_depth": r_d,
        })
        if gene == "EZH2" and chg > 15 and p < 0.05:
            ezh2_elevated = True
        if gene == "CYP24A1" and chg > 15 and p < 0.05:
            cyp24a1_elevated = True
        if gene == "VDR" and chg < -15 and p < 0.05:
            vdr_suppressed = True

    # Check EZH2 depth correlation
    ezh2_depth_r = np.nan
    if "EZH2" in log2_cpm.index:
        ezh2_vals = log2_cpm.loc["EZH2", tumor_cols].values
        ezh2_depth_r, _ = pearson_safe(
            depth_s2.values, ezh2_vals
        )

    log(f"\n  PREDICTION 4 VERDICT:")
    log(f"  Predicted: EZH2 NOT the lock mechanism")
    log(f"  EZH2 elevated >15%: {ezh2_elevated}")
    log(f"  EZH2 depth r:       {ezh2_depth_r:+.4f}"
        if not np.isnan(ezh2_depth_r) else
        f"  EZH2 depth r:       NA")
    log(f"  CYP24A1 elevated:   {cyp24a1_elevated}")
    log(f"  VDR suppressed:     {vdr_suppressed}")

    if not ezh2_elevated and (
        cyp24a1_elevated or vdr_suppressed
    ):
        log(f"  CONFIRMED: EZH2 is not the lock")
        log(f"  VDR/CYP24A1 axis confirmed as candidate")
        if vdr_suppressed:
            log(f"  VDR itself suppressed — receptor loss "
                f"is primary mechanism")
        elif cyp24a1_elevated:
            log(f"  CYP24A1 elevated — VDR signal "
                f"self-destruction confirmed")
    elif ezh2_elevated:
        log(f"  NOT CONFIRMED: EZH2 IS elevated")
        log(f"  cdRCC joins BRCA/PAAD/PRAD pattern")
        log(f"  EZH2 inhibitor target prediction holds")
    else:
        log(f"  PARTIAL: EZH2 not elevated but VDR/")
        log(f"  CYP24A1 axis not clearly confirmed either")

    return pd.DataFrame(results), ezh2_elevated

# ============================================================
# STEP 8: PREDICTION 5 — PRKCI POLARITY LOCK
# ============================================================

def test_prkci_polarity(log2_cpm, depth_s2):
    log("")
    log("=" * 65)
    log("STEP 8: PREDICTION 5 — PRKCI POLARITY LOCK")
    log("  Prediction: PRKCI coordinates with PAR complex")
    log("  Polarity complex maintains false attractor ID")
    log("=" * 65)

    tumor_cols  = [c for c in log2_cpm.columns
                   if c in TUMOR_SAMPLES]
    normal_cols = [c for c in log2_cpm.columns
                   if c in NORMAL_SAMPLES]

    pol_genes = [g for g in POLARITY
                 if g in log2_cpm.index]

    log(f"\n  Polarity genes found: "
        f"{len(pol_genes)}/{len(POLARITY)}")

    # Expression
    log(f"\n  {'Gene':<12} {'Normal':>8} {'Tumour':>8} "
        f"{'Change':>9}  {'p':>14}  r_depth")
    log(f"  {'-'*68}")
    for gene in pol_genes:
        tv = log2_cpm.loc[gene, tumor_cols].values
        nv = log2_cpm.loc[gene, normal_cols].values
        nm = nv.mean()
        tm = tv.mean()
        chg = ((tm - nm) / max(abs(nm), 0.01) * 100)
        p  = mw_test(tv, nv)
        r_d, _ = pearson_safe(depth_s2.values, tv)
        r_s = f"{r_d:+.3f}" if not np.isnan(r_d) else "   NA"
        log(f"  {gene:<12} {nm:>8.4f} {tm:>8.4f} "
            f"{chg:>+8.1f}%  {fmt_p(p)}  {r_s}")

    # Intra-tumour circuit correlations
    log(f"\n  INTRA-TUMOUR CORRELATIONS (polarity):")
    log(f"  {'Pair':<22} {'r':>8}  p-value")
    log(f"  {'-'*40}")

    tumor_expr = log2_cpm[tumor_cols].T

    pol_pairs = [
        ("PRKCI", "PARD3"),
        ("PRKCI", "PARD6A"),
        ("PRKCI", "PARD6B"),
        ("PRKCI", "LLGL2"),
        ("PRKCI", "SCRIB"),
        ("PRKCI", "CDC42"),
        ("PRKCI", "IL1RAP"),  # co-localisation test
        ("PRKCI", "PPARG"),
        ("PRKCI", "KLF5"),
        ("LLGL2", "SCRIB"),
    ]

    prkci_complex_confirmed = False
    for g1, g2 in pol_pairs:
        if (g1 not in log2_cpm.index or
                g2 not in log2_cpm.index):
            continue
        r, p = pearson_safe(
            tumor_expr[g1].values,
            tumor_expr[g2].values
        )
        r_s = f"{r:+.4f}" if not np.isnan(r) else "    NA"
        log(f"  {g1+' vs '+g2:<22} {r_s:>8}  {fmt_p(p)}")
        if g1 == "PRKCI" and g2 in ("PARD3", "PARD6A"):
            if not np.isnan(r) and r > 0.5:
                prkci_complex_confirmed = True

    # LLGL2 direction — should be negative if PRKCI antagonises
    log(f"\n  PREDICTION 5 VERDICT:")
    log(f"  Predicted: PRKCI coordinates PAR complex")
    if prkci_complex_confirmed:
        log(f"  CONFIRMED: PRKCI-PAR complex coordinated")
        log(f"  Polarity lock is operating")
    else:
        log(f"  NOT CONFIRMED or PAR complex genes below")
        log(f"  detection threshold")
        log(f"  PRKCI still depth-correlated (r=+0.958)")
        log(f"  May act independently of PAR complex here")

    return prkci_complex_confirmed

# ============================================================
# STEP 9: PREDICTION 6 — CDC4 ROBUSTNESS CHECK
# ============================================================

def test_cdc4_robustness(log2_cpm, depth_s2):
    log("")
    log("=" * 65)
    log("STEP 9: PREDICTION 6 — CDC4 ROBUSTNESS CHECK")
    log("  CDC4 tumour library: 3.4M (outlier)")
    log("  Prediction: top 10 depth correlators")
    log("  stable when CDC4 excluded")
    log("=" * 65)

    tumor_cols_full  = [c for c in log2_cpm.columns
                        if c in TUMOR_SAMPLES]
    tumor_cols_no4   = [c for c in tumor_cols_full
                        if c != CDC4_TUMOR]

    if len(tumor_cols_no4) < 4:
        log("  SKIP: Not enough tumours after CDC4 removal")
        return

    log(f"  Full set:    {len(tumor_cols_full)} tumours "
        f"(includes CDC4)")
    log(f"  No-CDC4 set: {len(tumor_cols_no4)} tumours")

    # Build depth score without CDC4
    top_switch = "CDS2"
    top_fa     = "IL1RAP"

    for g in [top_switch, top_fa]:
        if g not in log2_cpm.index:
            log(f"  WARNING: {g} not in matrix — "
                f"skipping robustness check")
            return

    tumor_expr_full = log2_cpm[tumor_cols_full].T
    tumor_expr_no4  = log2_cpm[tumor_cols_no4].T

    depth_no4 = (
        (1 - norm01(tumor_expr_no4[top_switch]))
        + norm01(tumor_expr_no4[top_fa])
    ) / 2

    # Recompute depth correlations without CDC4
    corrs_full = []
    corrs_no4  = []

    test_genes = [g for g in log2_cpm.index
                  if g in ALL_S2_GENES
                  or g in [top_switch, top_fa]]

    for gene in log2_cpm.index:
        try:
            vals_full = log2_cpm.loc[gene, tumor_cols_full].values
            r_f, _ = pearson_safe(
                depth_s2.values, vals_full
            )
            corrs_full.append((gene, r_f))

            vals_no4 = log2_cpm.loc[gene, tumor_cols_no4].values
            r_n4, _ = pearson_safe(
                depth_no4.values, vals_no4
            )
            corrs_no4.append((gene, r_n4))
        except Exception:
            pass

    corrs_full.sort(key=lambda x: abs(x[1])
                    if not np.isnan(x[1]) else 0,
                    reverse=True)
    corrs_no4.sort(key=lambda x: abs(x[1])
                   if not np.isnan(x[1]) else 0,
                   reverse=True)

    top10_full = [g for g, r in corrs_full[:10]]
    top10_no4  = [g for g, r in corrs_no4[:10]]
    overlap    = len(set(top10_full) & set(top10_no4))

    log(f"\n  Top 10 depth correlators (full vs no-CDC4):")
    log(f"  {'Gene (full)':>20}  {'Gene (no-CDC4)':>20}")
    log(f"  {'-'*44}")
    for i in range(10):
        gf = top10_full[i] if i < len(top10_full) else ""
        gn = top10_no4[i]  if i < len(top10_no4)  else ""
        match = "✓" if gf == gn else " "
        log(f"  {gf:>20}  {gn:>20}  {match}")

    log(f"\n  Overlap in top 10: {overlap}/10")

    log(f"\n  PREDICTION 6 VERDICT:")
    log(f"  Predicted: top 10 stable when CDC4 excluded")
    if overlap >= 7:
        log(f"  CONFIRMED: findings are CDC4-independent")
    elif overlap >= 5:
        log(f"  PARTIAL: mostly stable — CDC4 has modest "
            f"influence")
    else:
        log(f"  NOT CONFIRMED: CDC4 significantly drives "
            f"depth correlations")
        log(f"  Interpret all depth results cautiously")

    return overlap

# ============================================================
# STEP 10: COLLECTING DUCT IDENTITY ANALYSIS
# The state of the normal CD programme in tumours
# ============================================================

def test_cd_identity(log2_cpm, depth_s2):
    log("")
    log("=" * 65)
    log("STEP 10: COLLECTING DUCT IDENTITY ANALYSIS")
    log("  Are BOTH collecting duct programmes lost?")
    log("  Principal cell (AVPR2/AQP2/PRKAR2B)")
    log("  Intercalated cell (ATP6V1G3/FOXI1)")
    log("=" * 65)

    tumor_cols  = [c for c in log2_cpm.columns
                   if c in TUMOR_SAMPLES]
    normal_cols = [c for c in log2_cpm.columns
                   if c in NORMAL_SAMPLES]

    cd_genes = [g for g in CD_IDENTITY
                if g in log2_cpm.index]

    log(f"\n  CD identity genes found: "
        f"{len(cd_genes)}/{len(CD_IDENTITY)}")

    log(f"\n  {'Gene':<12} {'Normal':>8} {'Tumour':>8} "
        f"{'Change':>9}  {'p':>14}  r_depth")
    log(f"  {'-'*68}")

    pc_lost = 0
    ic_lost = 0
    pc_genes = ["AQP2", "AQP3", "AVPR2", "PRKAR2B",
                "SCNN1A", "SCNN1B", "SCNN1G", "TFCP2L1"]
    ic_genes = ["ATP6V1G3", "ATP6V0A4", "FOXI1"]

    for gene in cd_genes:
        tv = log2_cpm.loc[gene, tumor_cols].values
        nv = log2_cpm.loc[gene, normal_cols].values
        nm = nv.mean()
        tm = tv.mean()
        chg = ((tm - nm) / max(abs(nm), 0.01) * 100)
        p  = mw_test(tv, nv)
        r_d, _ = pearson_safe(depth_s2.values, tv)
        r_s = f"{r_d:+.3f}" if not np.isnan(r_d) else "   NA"
        log(f"  {gene:<12} {nm:>8.4f} {tm:>8.4f} "
            f"{chg:>+8.1f}%  {fmt_p(p)}  {r_s}")

        if gene in pc_genes and chg < -20 and p < 0.1:
            pc_lost += 1
        if gene in ic_genes and chg < -30 and p < 0.1:
            ic_lost += 1

    log(f"\n  SUMMARY:")
    log(f"  Principal cell markers lost (>20% down): {pc_lost}")
    log(f"  Intercalated cell markers lost (>30% down): {ic_lost}")

    if pc_lost > 0 and ic_lost > 0:
        log(f"  BOTH collecting duct identities lost")
        log(f"  Tumour is not stuck at collecting duct")
        log(f"  progenitor — it has escaped entirely")
    elif ic_lost > 0:
        log(f"  Intercalated cell identity lost")
        log(f"  Principal cell programme partially retained")
    elif pc_lost > 0:
        log(f"  Principal cell identity lost")
        log(f"  Intercalated cell programme partially retained")
    else:
        log(f"  CD identity programmes present but low signal")

# ============================================================
# STEP 11: FALSE ATTRACTOR IDENTITY PANEL
# Confirm and extend the FA signature
# ============================================================

def test_fa_identity(log2_cpm, depth_s2):
    log("")
    log("=" * 65)
    log("STEP 11: FALSE ATTRACTOR IDENTITY PANEL")
    log("  Confirming and extending S1 FA signature")
    log("=" * 65)

    tumor_cols  = [c for c in log2_cpm.columns
                   if c in TUMOR_SAMPLES]
    normal_cols = [c for c in log2_cpm.columns
                   if c in NORMAL_SAMPLES]

    fa_genes = [g for g in FA_IDENTITY
                if g in log2_cpm.index]

    log(f"\n  FA identity genes found: "
        f"{len(fa_genes)}/{len(FA_IDENTITY)}")

    log(f"\n  {'Gene':<12} {'Normal':>8} {'Tumour':>8} "
        f"{'Change':>9}  {'p':>14}  r_depth")
    log(f"  {'-'*68}")

    confirmed_fa = []
    results = []
    for gene in fa_genes:
        tv = log2_cpm.loc[gene, tumor_cols].values
        nv = log2_cpm.loc[gene, normal_cols].values
        nm = nv.mean()
        tm = tv.mean()
        chg = ((tm - nm) / max(abs(nm), 0.01) * 100)
        p  = mw_test(tv, nv)
        r_d, p_d = pearson_safe(depth_s2.values, tv)
        r_s = f"{r_d:+.3f}" if not np.isnan(r_d) else "   NA"
        log(f"  {gene:<12} {nm:>8.4f} {tm:>8.4f} "
            f"{chg:>+8.1f}%  {fmt_p(p)}  {r_s}")
        results.append({
            "gene": gene, "normal_mean": nm,
            "tumor_mean": tm, "change_pct": chg,
            "p_value": p, "r_depth": r_d,
        })
        if (chg > 20 and p < 0.05
                and not np.isnan(r_d) and r_d > 0.3):
            confirmed_fa.append(gene)

    # Intra-tumour co-expression of FA markers
    log(f"\n  FA MARKER CO-EXPRESSION (tumour):")
    log(f"  {'Pair':<22} {'r':>8}  p-value")
    log(f"  {'-'*40}")

    tumor_expr = log2_cpm[tumor_cols].T

    fa_pairs = [
        ("PAEP",    "CST1"),
        ("PAEP",    "S100A7"),
        ("PAEP",    "AGR2"),
        ("PAEP",    "IL1RAP"),
        ("AGR2",    "ESRP1"),
        ("AGR2",    "IL1RAP"),
        ("IL1RAP",  "PRKCI"),
        ("PPARG",   "IL1RAP"),
        ("KLF5",    "PPARG"),
        ("GPRC5A",  "IL1RAP"),
    ]

    for g1, g2 in fa_pairs:
        if (g1 not in log2_cpm.index or
                g2 not in log2_cpm.index):
            continue
        r, p = pearson_safe(
            tumor_expr[g1].values,
            tumor_expr[g2].values
        )
        r_s = f"{r:+.4f}" if not np.isnan(r) else "    NA"
        log(f"  {g1+' vs '+g2:<22} {r_s:>8}  {fmt_p(p)}")

    log(f"\n  Confirmed FA markers (elevated + depth-r>0.3):")
    for g in confirmed_fa:
        log(f"    {g}")

    pd.DataFrame(results).to_csv(
        os.path.join(S2_DIR, "fa_identity_s2.csv"),
        index=False
    )

    return confirmed_fa

# ============================================================
# STEP 12: FULL DEPTH CORRELATION TABLE (S2)
# ============================================================

def full_depth_correlations_s2(log2_cpm, depth_s2):
    log("")
    log("=" * 65)
    log("STEP 12: FULL DEPTH CORRELATIONS (S2)")
    log("  All genes vs S2 corrected depth score")
    log("=" * 65)

    tumor_cols = [c for c in log2_cpm.columns
                  if c in TUMOR_SAMPLES]

    corrs = []
    for gene in log2_cpm.index:
        try:
            vals = log2_cpm.loc[gene, tumor_cols].values
            r, p = pearson_safe(depth_s2.values, vals)
            corrs.append((str(gene), r, p))
        except Exception:
            pass

    corrs.sort(key=lambda x: abs(x[1])
               if not np.isnan(x[1]) else 0,
               reverse=True)

    log(f"\n  {'='*65}")
    log(f"  S2 DEPTH CORRELATIONS (top 40)")
    log(f"  Using corrected depth axis: IL1RAP / CDS2")
    log(f"  {'='*65}")
    log(f"  {'Gene':<20} {'r':>8}  p-value")
    log(f"  {'-'*44}")
    for gene, r, p in corrs[:40]:
        r_s = f"{r:+.4f}" if not np.isnan(r) else "    NA"
        log(f"  {gene:<20} {r_s:>8}  {fmt_p(p)}")

    corr_df = pd.DataFrame(
        corrs, columns=["gene", "r", "p_value"]
    )
    corr_df.to_csv(
        os.path.join(S2_DIR, "depth_correlations_s2.csv"),
        index=False
    )
    log(f"\n  Saved: depth_correlations_s2.csv")

    return corrs

# ============================================================
# STEP 13: PAIRED ANALYSIS WITH S2 PANEL
# ============================================================

def paired_analysis_s2(log2_cpm):
    log("")
    log("=" * 65)
    log("STEP 13: PAIRED ANALYSIS — S2 PANEL")
    log("  6 matched pairs")
    log("  Extended gene panel")
    log("=" * 65)

    available_pairs = []
    for patient, t_gsm, n_gsm in MATCHED_PAIRS:
        if (t_gsm in log2_cpm.columns and
                n_gsm in log2_cpm.columns):
            available_pairs.append(
                (patient, t_gsm, n_gsm)
            )
        else:
            log(f"  Missing: {patient}")

    log(f"  Available pairs: {len(available_pairs)}")

    test_genes = [g for g in ALL_S2_GENES
                  if g in log2_cpm.index]

    log(f"  Genes tested: {len(test_genes)}")

    paired_results = []
    for gene in test_genes:
        diffs = []
        for patient, t_gsm, n_gsm in available_pairs:
            tv = log2_cpm.loc[gene, t_gsm]
            nv = log2_cpm.loc[gene, n_gsm]
            diffs.append(tv - nv)

        if len(diffs) < 3:
            continue

        diffs      = np.array(diffs)
        mean_diff  = diffs.mean()
        direction  = "DOWN" if mean_diff < 0 else "UP"

        try:
            if len(set(diffs)) == 1:
                p_paired = 1.0
            else:
                _, p_paired = stats.wilcoxon(
                    diffs, alternative="two-sided"
                )
        except Exception:
            p_paired = np.nan

        paired_results.append({
            "gene":      gene,
            "mean_diff": mean_diff,
            "direction": direction,
            "p_paired":  p_paired,
        })

    paired_df = pd.DataFrame(paired_results)
    paired_df = paired_df.sort_values(
        "mean_diff", key=abs, ascending=False
    )

    sig = paired_df[paired_df["p_paired"] < 0.05]
    log(f"\n  Paired significant (p<0.05): {len(sig)}")

    log(f"\n  {'Gene':<20} {'MeanDiff':>10} "
        f"{'Dir':>6}  p_paired")
    log(f"  {'-'*50}")
    for _, row in paired_df.head(30).iterrows():
        p_s = (f"p={row['p_paired']:.4f}"
               if not np.isnan(row["p_paired"])
               else "p=NA")
        flag = (" *" if row["p_paired"] < 0.05
                else "  " if not np.isnan(row["p_paired"])
                else "  ")
        log(
            f"  {row['gene']:<20} "
            f"{row['mean_diff']:>+10.4f}  "
            f"{row['direction']:>6}  "
            f"{p_s}{flag}"
        )

    paired_df.to_csv(
        os.path.join(S2_DIR, "paired_results_s2.csv"),
        index=False
    )
    log(f"\n  Saved: paired_results_s2.csv")

    return paired_df

# ============================================================
# STEP 14: ALL GENES SADDLE TABLE FOR S2 PANEL
# ============================================================

def saddle_table_s2(log2_cpm):
    log("")
    log("=" * 65)
    log("STEP 14: SADDLE TABLE — S2 GENE PANEL")
    log("=" * 65)

    tumor_cols  = [c for c in log2_cpm.columns
                   if c in TUMOR_SAMPLES]
    normal_cols = [c for c in log2_cpm.columns
                   if c in NORMAL_SAMPLES]

    test_genes = [g for g in ALL_S2_GENES
                  if g in log2_cpm.index]

    log(f"  S2 panel genes found: "
        f"{len(test_genes)}/{len(ALL_S2_GENES)}")

    log(f"\n  {'Gene':<12} {'Normal':>8} {'Tumour':>8} "
        f"{'Change':>9}  {'p':>14}")
    log(f"  {'-'*58}")

    results = []
    for gene in test_genes:
        tv = log2_cpm.loc[gene, tumor_cols].values
        nv = log2_cpm.loc[gene, normal_cols].values
        nm = nv.mean()
        tm = tv.mean()
        chg = ((tm - nm) / max(abs(nm), 0.01) * 100)
        p  = mw_test(tv, nv)
        log(f"  {gene:<12} {nm:>8.4f} {tm:>8.4f} "
            f"{chg:>+8.1f}%  {fmt_p(p)}")
        results.append({
            "gene": gene, "normal_mean": nm,
            "tumor_mean": tm, "change_pct": chg,
            "p_value": p,
        })

    rdf = pd.DataFrame(results)
    rdf.to_csv(
        os.path.join(S2_DIR, "saddle_s2.csv"),
        index=False
    )
    log(f"\n  Saved: saddle_s2.csv")
    return rdf

# ============================================================
# STEP 15: FIGURE
# ============================================================

def generate_figure_s2(
    log2_cpm, depth_s2, depth_s1,
    saddle_df, corrs_s2, fa_confirmed,
    r_s1s2, paired_df
):
    log("")
    log("--- Generating S2 figure ---")

    tumor_cols  = [c for c in log2_cpm.columns
                   if c in TUMOR_SAMPLES]
    normal_cols = [c for c in log2_cpm.columns
                   if c in NORMAL_SAMPLES]

    clr_t = "#c0392b"
    clr_n = "#2980b9"
    clr_u = "#27ae60"
    clr_d = "#c0392b"

    fig = plt.figure(figsize=(26, 20))
    fig.suptitle(
        "OrganismCore — cdRCC False Attractor Circuit Analysis\n"
        "SCRIPT 2 | GSE89122 | 7 tumours | 6 normals | 6 pairs\n"
        "Corrected depth axis: IL1RAP (r=+0.960) / CDS2 (r=-0.960)\n"
        "Doc 89b — 2026-03-03",
        fontsize=11, fontweight="bold", y=0.99,
    )
    gs = gridspec.GridSpec(
        3, 3, figure=fig,
        hspace=0.52, wspace=0.44,
    )

    # ---- Panel A: S1 vs S2 depth comparison ----
    ax_a = fig.add_subplot(gs[0, 0])
    if depth_s1 is not None:
        d1_aligned = depth_s1.reindex(tumor_cols).dropna()
        d2_aligned = depth_s2.reindex(d1_aligned.index)
        ax_a.scatter(
            d1_aligned.values, d2_aligned.values,
            color=clr_t, alpha=0.8, s=60
        )
        for gsm in d1_aligned.index:
            patient, _ = SAMPLE_MAP.get(gsm, ("?", "?"))
            ax_a.annotate(
                patient,
                (d1_aligned[gsm], d2_aligned[gsm]),
                fontsize=8,
                xytext=(4, 4),
                textcoords="offset points",
            )
        r_lab = (f"r={r_s1s2:.3f}"
                 if not np.isnan(r_s1s2)
                 else "r=NA")
        ax_a.set_xlabel("S1 Depth", fontsize=8)
        ax_a.set_ylabel("S2 Depth", fontsize=8)
        ax_a.set_title(
            f"A — S1 vs S2 Depth\n{r_lab}",
            fontsize=9
        )
    else:
        ax_a.set_title("A — S1 depth not available",
                       fontsize=9)

    # ---- Panel B: FA identity confirmed markers ----
    ax_b = fig.add_subplot(gs[0, 1])
    fa_show = [g for g in FA_IDENTITY
               if g in log2_cpm.index][:12]
    if fa_show:
        nm_vals = [log2_cpm.loc[g, normal_cols].mean()
                   for g in fa_show]
        tm_vals = [log2_cpm.loc[g, tumor_cols].mean()
                   for g in fa_show]
        x = np.arange(len(fa_show))
        w = 0.35
        ax_b.bar(x - w/2, nm_vals, w,
                 color=clr_n, label="Normal", alpha=0.85)
        ax_b.bar(x + w/2, tm_vals, w,
                 color=clr_t, label="Tumour", alpha=0.85)
        ax_b.set_xticks(x)
        ax_b.set_xticklabels(
            fa_show, rotation=45, ha="right", fontsize=6
        )
        ax_b.set_title(
            "B — FA Identity Panel\n"
            "PAEP/CST1/S100A7/AGR2/IL1RAP",
            fontsize=9
        )
        ax_b.legend(fontsize=7)
        ax_b.set_ylabel("log2(CPM+1)", fontsize=8)

    # ---- Panel C: PKA circuit ----
    ax_c = fig.add_subplot(gs[0, 2])
    pka_show = [g for g in PKA_CIRCUIT
                if g in log2_cpm.index][:10]
    if pka_show:
        nm_vals = [log2_cpm.loc[g, normal_cols].mean()
                   for g in pka_show]
        tm_vals = [log2_cpm.loc[g, tumor_cols].mean()
                   for g in pka_show]
        x = np.arange(len(pka_show))
        w = 0.35
        ax_c.bar(x - w/2, nm_vals, w,
                 color=clr_n, label="Normal", alpha=0.85)
        ax_c.bar(x + w/2, tm_vals, w,
                 color=clr_t, label="Tumour", alpha=0.85)
        ax_c.set_xticks(x)
        ax_c.set_xticklabels(
            pka_show, rotation=45, ha="right", fontsize=6
        )
        ax_c.set_title(
            "C — PKA/Vasopressin Circuit\n"
            "Collecting duct switch programme",
            fontsize=9
        )
        ax_c.legend(fontsize=7)
        ax_c.set_ylabel("log2(CPM+1)", fontsize=8)

    # ---- Panel D: S2 depth correlations ----
    ax_d = fig.add_subplot(gs[1, 0])
    if corrs_s2:
        top_c = corrs_s2[:25]
        gc = [c[0] for c in top_c]
        vc = [c[1] if not np.isnan(c[1]) else 0
              for c in top_c]
        cc = [clr_d if v < 0 else clr_u for v in vc]
        ax_d.barh(gc, vc, color=cc)
        ax_d.axvline(0, color="black", linewidth=0.8)
        ax_d.set_xlabel("r with S2 depth", fontsize=8)
        ax_d.set_title(
            "D — S2 Depth Correlations\n"
            "Top 25 (corrected axis)",
            fontsize=9
        )
        ax_d.tick_params(axis="y", labelsize=6)

    # ---- Panel E: Epigenetic / VDR panel ----
    ax_e = fig.add_subplot(gs[1, 1])
    lock_show = [g for g in
                 EPIGENETIC[:8] + VDR_CIRCUIT[:5]
                 if g in log2_cpm.index]
    if lock_show:
        nm_vals = [log2_cpm.loc[g, normal_cols].mean()
                   for g in lock_show]
        tm_vals = [log2_cpm.loc[g, tumor_cols].mean()
                   for g in lock_show]
        x = np.arange(len(lock_show))
        w = 0.35
        ax_e.bar(x - w/2, nm_vals, w,
                 color=clr_n, label="Normal", alpha=0.85)
        ax_e.bar(x + w/2, tm_vals, w,
                 color=clr_t, label="Tumour", alpha=0.85)
        ax_e.set_xticks(x)
        ax_e.set_xticklabels(
            lock_show, rotation=45, ha="right", fontsize=6
        )
        ax_e.set_title(
            "E — Epigenetic / VDR Lock Panel\n"
            "Prediction 4: EZH2 vs CYP24A1/VDR",
            fontsize=9
        )
        ax_e.legend(fontsize=7)
        ax_e.set_ylabel("log2(CPM+1)", fontsize=8)

    # ---- Panel F: PPARG / polarity panel ----
    ax_f = fig.add_subplot(gs[1, 2])
    ppol_show = [g for g in
                 PPARG_CIRCUIT[:6] + POLARITY[:6]
                 if g in log2_cpm.index]
    if ppol_show:
        nm_vals = [log2_cpm.loc[g, normal_cols].mean()
                   for g in ppol_show]
        tm_vals = [log2_cpm.loc[g, tumor_cols].mean()
                   for g in ppol_show]
        x = np.arange(len(ppol_show))
        w = 0.35
        ax_f.bar(x - w/2, nm_vals, w,
                 color=clr_n, label="Normal", alpha=0.85)
        ax_f.bar(x + w/2, tm_vals, w,
                 color=clr_t, label="Tumour", alpha=0.85)
        ax_f.set_xticks(x)
        ax_f.set_xticklabels(
            ppol_show, rotation=45, ha="right", fontsize=6
        )
        ax_f.set_title(
            "F — PPARG + Polarity Complex\n"
            "Prediction 3 & 5",
            fontsize=9
        )
        ax_f.legend(fontsize=7)
        ax_f.set_ylabel("log2(CPM+1)", fontsize=8)

    # ---- Panel G: S2 depth per sample ----
    ax_g = fig.add_subplot(gs[2, 0])
    patients = [SAMPLE_MAP[g][0] for g in tumor_cols]
    colors_g = [clr_t] * len(tumor_cols)
    bars = ax_g.bar(patients, depth_s2.values,
                    color=colors_g, alpha=0.8)
    ax_g.axhline(depth_s2.mean(), color="black",
                 linewidth=1.5, linestyle="--",
                 label=f"mean={depth_s2.mean():.3f}")
    ax_g.set_ylabel("S2 Block Depth", fontsize=8)
    ax_g.set_title(
        "G — S2 Depth by Sample\n"
        f"(IL1RAP / CDS2 axis)",
        fontsize=9
    )
    ax_g.legend(fontsize=7)
    ax_g.tick_params(axis="x", labelsize=8)

    # ---- Panel H: Paired results S2 panel ----
    ax_h = fig.add_subplot(gs[2, 1])
    if paired_df is not None and len(paired_df) > 0:
        top_p = paired_df.head(15)
        genes_h = top_p["gene"].values
        diffs_h = top_p["mean_diff"].values
        sig_h   = top_p["p_paired"].values
        cols_h  = [clr_d if v < 0 else clr_u
                   for v in diffs_h]
        alphas  = [0.95 if p < 0.05 else 0.5
                   for p in sig_h]
        x_h = np.arange(len(genes_h))
        for i, (xi, di, ci, ai) in enumerate(
            zip(x_h, diffs_h, cols_h, alphas)
        ):
            ax_h.bar(xi, di, color=ci, alpha=ai)
        ax_h.axhline(0, color="black", linewidth=0.8)
        ax_h.set_xticks(x_h)
        ax_h.set_xticklabels(
            genes_h, rotation=45, ha="right", fontsize=6
        )
        ax_h.set_ylabel("Mean paired diff", fontsize=8)
        ax_h.set_title(
            "H — Paired Differences (S2 panel)\n"
            "Solid = p<0.05",
            fontsize=9
        )

    # ---- Panel I: Summary text ----
    ax_i = fig.add_subplot(gs[2, 2])
    ax_i.axis("off")
    r_s1s2_str = (f"{r_s1s2:.3f}"
                  if not np.isnan(r_s1s2) else "NA")
    summary = (
        f"I — SCRIPT 2 SUMMARY\n"
        f"──────────────────────────────\n"
        f"Corrected depth axis:\n"
        f"  FA:     IL1RAP  r=+0.960\n"
        f"  Switch: CDS2    r=-0.960\n\n"
        f"S1 vs S2 depth: r={r_s1s2_str}\n\n"
        f"Predictions tested: 6\n"
        f"  P1 IL1 circuit:  see log\n"
        f"  P2 PKA gap:      see log\n"
        f"  P3 PPARG driver: see log\n"
        f"  P4 EZH2 lock:    see log\n"
        f"  P5 PRKCI polar:  see log\n"
        f"  P6 CDC4 robust:  see log\n\n"
        f"FA confirmed markers:\n"
        + "".join(f"  {g}\n" for g in fa_confirmed[:6]) +
        f"\nFalse attractor:\n"
        f"  Secretory ectopic\n"
        f"  epithelial state\n"
        f"  PPARG+KLF5+PRKCI\n"
        f"  IL1RAP convergence\n\n"
        f"OrganismCore  2026-03-03\n"
        f"Doc 89b follows."
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
        S2_DIR,
        "GSE89122_circuit_analysis_s2.png"
    )
    plt.savefig(outpath, dpi=150, bbox_inches="tight")
    log(f"\n  Figure saved: {outpath}")
    plt.close()

# ============================================================
# MAIN
# ============================================================

def main():
    log("=" * 65)
    log("OrganismCore — cdRCC False Attractor Circuit Analysis")
    log("SCRIPT 2 — PREDICTIONS FROM DOC 89a")
    log("Dataset: GSE89122")
    log("7 CDC tumours | 6 matched normals | 6 pairs")
    log("Date: 2026-03-03")
    log("=" * 65)
    log("")
    log("Script 1 established geometry.")
    log("Script 2 tests 6 predictions locked in Doc 89a.")
    log("")
    log("PREDICTIONS UNDER TEST:")
    log("  P1: IL1B-IL1RAP autocrine loop (r > 0.5)")
    log("  P2: PKA/vasopressin circuit broken in tumours")
    log("  P3: PPARG drives attractor (r(PPARG,KLF5) > 0.5)")
    log("  P4: EZH2 NOT the lock — VDR/CYP24A1 is")
    log("  P5: PRKCI coordinates PAR polarity complex")
    log("  P6: Findings CDC4-independent")
    log("")

    # Step 1: Load S1 matrix (reuse, no re-download)
    log2_cpm = load_s1_matrix()
    if log2_cpm is None:
        log("FATAL: Cannot proceed without S1 matrix")
        write_log()
        return

    # Step 2: Load S1 depth correlations
    s1_corrs = load_s1_depth_corrs()
    if s1_corrs is None:
        log("WARNING: S1 depth correlations not found")
        log("  Using hardcoded top genes (IL1RAP / CDS2)")
        s1_corrs = pd.DataFrame({
            "gene": ["IL1RAP", "CDS2"],
            "r":    [0.960,    -0.960],
            "p_value": [5.85e-4, 6.04e-4]
        })

    # Step 3: S2 corrected depth score
    (depth_s2, depth_s1,
     top_switch, top_fa,
     r_s1s2) = build_s2_depth(log2_cpm, s1_corrs)

    # Step 4: P1 — IL1 autocrine circuit
    il1_results = test_il1_circuit(log2_cpm, depth_s2)

    # Step 5: P2 — PKA gap test
    gap_confirmed = test_pka_gap(log2_cpm, depth_s2)

    # Step 6: P3 — PPARG driver vs marker
    pparg_driver = test_pparg_circuit(log2_cpm, depth_s2)

    # Step 7: P4 — EZH2 lock test
    epig_results, ezh2_elevated = test_ezh2_lock(
        log2_cpm, depth_s2
    )

    # Step 8: P5 — PRKCI polarity lock
    prkci_confirmed = test_prkci_polarity(
        log2_cpm, depth_s2
    )

    # Step 9: P6 — CDC4 robustness
    cdc4_overlap = test_cdc4_robustness(
        log2_cpm, depth_s2
    )

    # Step 10: Collecting duct identity
    test_cd_identity(log2_cpm, depth_s2)

    # Step 11: FA identity panel
    fa_confirmed = test_fa_identity(
        log2_cpm, depth_s2
    )

    # Step 12: Full S2 depth correlations
    corrs_s2 = full_depth_correlations_s2(
        log2_cpm, depth_s2
    )

    # Step 13: Paired analysis S2 panel
    paired_df = paired_analysis_s2(log2_cpm)

    # Step 14: Saddle table for S2 panel
    saddle_df = saddle_table_s2(log2_cpm)

    # Step 15: Figure
    generate_figure_s2(
        log2_cpm, depth_s2, depth_s1,
        saddle_df, corrs_s2, fa_confirmed,
        r_s1s2, paired_df
    )

    # Save log
    write_log()

    log("")
    log("=" * 65)
    log("SCRIPT 2 COMPLETE")
    log("")
    log("Outputs:")
    log(f"  {S2_DIR}/saddle_s2.csv")
    log(f"  {S2_DIR}/fa_identity_s2.csv")
    log(f"  {S2_DIR}/depth_correlations_s2.csv")
    log(f"  {S2_DIR}/paired_results_s2.csv")
    log(f"  {S2_DIR}/GSE89122_circuit_analysis_s2.png")
    log(f"  {S2_DIR}/analysis_log_s2.txt")
    log("")
    log("Read the output now:")
    log("  1. S1 vs S2 depth r — same biology?")
    log("  2. Each prediction — confirmed or not?")
    log("  3. S2 depth corrs — new signals or same?")
    log("  4. Paired results — new confirmations?")
    log("")
    log("Write Doc 89b after reading.")
    log("Lock novel predictions before literature check.")
    log("=" * 65)


if __name__ == "__main__":
    main()
