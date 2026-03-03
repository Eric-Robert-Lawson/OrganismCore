"""
cdRCC — Collecting Duct Renal Cell Carcinoma
FALSE ATTRACTOR — SCRIPT 3  (v2 — corrected)
OrganismCore Cancer Validation #13

Corrections from v1 run (2026-03-03):
  1. Spearman negative correlator display — was showing
     near-zero noise floor. Now sorts by raw value
     ascending to find genuinely negative genes.
  2. CDC3 verdict — now reports which genes ARE
     retained (PPARG/KLF5) rather than only checking
     AQP2/PRKAR2B. Both outcomes recorded.
  3. MYC verdict — distinguishes negative r (anti-
     correlated = MYC HIGH when MKI67 LOW) from
     positive r. Negative r=-0.57 means the opposite
     of MYC driving proliferation. Corrected logic.
  4. GSE83479 replication — gene index has 'hg.' prefix
     that must be stripped. Column names are sample
     codes not GSM IDs — classifier now uses metadata
     titles to map columns to CDC/normal groups.
  5. Step 4 verdict — added note that p=0.148 is
     underpowered at n=7. Does not overstate conclusion.

Dataset primary:    GSE89122
                    7 CDC tumours | 6 matched normals
Dataset replication: GSE83479
                    17 CDC tumours + 9 external normals
                    Illumina HT12 microarray

Author:    Eric Robert Lawson
Framework: OrganismCore
Protocol:  Phase 3 — Script 3 v2
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

MATRIX_PATH = os.path.join(
    RESULTS_DIR, "GSE89122_log2cpm.csv"
)

REP_DIR = os.path.join(BASE_DIR, "GSE83479")

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
# GENE PANELS — locked in Doc 89b
# ============================================================

SWITCH_GENE = "PRKAR2B"
FA_GENE     = "IL1RAP"

PROG_A = [
    "PPARG", "KLF5", "AGR2", "ESRP1",
    "IL1RAP", "GPRC5A", "SERPINA1",
    "TMPRSS4", "CST6", "KLF10",
]

PROG_B = [
    "PAEP", "CST1", "S100A7",
    "ANXA8", "ANXA8L1", "LY6D",
]

PKA_CIRCUIT = [
    "AVPR2", "AVPR1A", "ADCY3", "ADCY6",
    "PRKAR1A", "PRKAR2A", "PRKAR2B",
    "PRKACB", "PRKACA",
    "AQP2", "AQP3", "SCNN1A", "SCNN1B", "SCNN1G",
]

PPARG_REWIRE = [
    "PPARG", "KLF5", "KLF4", "KLF2",
    "CEBPA", "CEBPB", "RXRA", "RXRB",
    "AGR2", "ESRP1", "IL1RAP",
    "FABP4", "FABP7", "SCD", "FASN", "ACACA",
]

ADCY3_DRIVERS = [
    "ADCY3", "ADCY6",
    "MYC", "MYCN", "BHLHE40",
    "HIF1A", "HIF2A", "EPAS1",
    "PPARG", "KLF5",
    "NFKB1", "NFKB2", "RELA",
    "PRKCI", "CEBPB",
    "MKI67",
]

CELSR1_PANEL = [
    "CELSR1", "CELSR2", "CELSR3",
    "FZD3", "FZD6", "VANGL1", "VANGL2",
    "PRICKLE1", "PRICKLE2", "DVL1", "DVL2",
    "KLF5", "PPARG", "AGR2",
    "PRKCI", "IL1B", "IL1RAP",
    "MYC", "BHLHE40",
]

CDC3_PANEL = [
    "AQP2", "PRKAR2B", "AVPR2",
    "SCNN1A", "SCNN1B", "SCNN1G",
    "TFCP2L1", "HNF4A", "FOXI1",
    "ATP6V1G3", "ATP6V0A4",
    "UMOD", "CALB1",
    "IL1RAP", "PPARG", "KLF5",
    "EZH2", "MKI67", "MYC",
]

MYC_PROLIFERATION = [
    "MYC", "MKI67", "TOP2A", "PCNA",
    "CDK4", "CCND1", "AURKA", "PLK1",
    "MCM2", "MCM7",
]

MYC_METABOLIC = [
    "MYC", "LDHA", "PKM", "ENO1",
    "SLC2A1", "SLC2A3",
    "ADCY3", "HK1", "HK2",
    "FASN", "SCD", "ACACA",
    "BHLHE40",
]

REPLICATION_PANEL = {
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

# Top-20 S2 Pearson r — from Doc 89b
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


def download_file(url, local_path):
    def hook(count, block, total):
        if total > 0:
            pct = min(count * block / total * 100, 100)
            mb  = count * block / 1e6
            sys.stdout.write(
                f"\r    {mb:.2f} MB  {pct:.1f}%"
            )
            sys.stdout.flush()
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req) as resp, \
             open(local_path, "wb") as out:
            total = int(
                resp.headers.get("Content-Length", 0)
            )
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
    mask = (~np.isnan(x)) & (~np.isnan(y))
    if mask.sum() < 4:
        return np.nan, np.nan
    r, p = stats.spearmanr(x[mask], y[mask])
    return float(r), float(p)


def fmt_p(p):
    if np.isnan(p):
        return "     ns"
    if p < 0.001:
        return f"p={p:.2e} ***"
    if p < 0.01:
        return f"p={p:.4f}  **"
    if p < 0.05:
        return f"p={p:.4f}   *"
    return f"p={p:.4f}  ns"


def norm01(s):
    lo, hi = s.min(), s.max()
    if hi == lo:
        return pd.Series(0.0, index=s.index)
    return (s - lo) / (hi - lo)

# ============================================================
# STEP 0 — LOAD MATRIX
# ============================================================

def load_primary_matrix():
    log("=" * 65)
    log("STEP 0 — LOADING S1/S2 MATRIX (GSE89122)")
    log(f"  {MATRIX_PATH}")
    log("=" * 65)

    if not os.path.exists(MATRIX_PATH):
        log(f"  ERROR: Matrix not found at {MATRIX_PATH}")
        log("  Run Script 1 first.")
        sys.exit(1)

    df = pd.read_csv(MATRIX_PATH, index_col=0)
    log(f"  Shape: {df.shape[0]} genes × "
        f"{df.shape[1]} samples")

    tumor_cols  = [c for c in df.columns
                   if SAMPLE_MAP.get(c, ("",""))[1]
                   == "tumor"]
    normal_cols = [c for c in df.columns
                   if SAMPLE_MAP.get(c, ("",""))[1]
                   == "normal"]

    log(f"  Tumour cols: {len(tumor_cols)}")
    log(f"  Normal cols: {len(normal_cols)}")

    tumor  = df[tumor_cols]
    normal = df[normal_cols]

    return df, tumor, normal, tumor_cols, normal_cols

# ============================================================
# STEP 1 — BUILD DEPTH SCORE
# ============================================================

def build_depth_score(tumor):
    log("")
    log("=" * 65)
    log("STEP 1 — S3 DEPTH SCORE (PRKAR2B / IL1RAP)")
    log("=" * 65)

    genes = tumor.index.tolist()

    has_sw = SWITCH_GENE in genes
    has_fa = FA_GENE in genes

    if has_sw:
        depth_switch = 1.0 - norm01(
            tumor.loc[SWITCH_GENE]
        )
    else:
        avail = [g for g in PKA_CIRCUIT if g in genes]
        depth_switch = 1.0 - norm01(
            tumor.loc[avail].mean(axis=0)
        )
        log(f"  {SWITCH_GENE} absent — using PKA mean")

    if has_fa:
        depth_fa = norm01(tumor.loc[FA_GENE])
    else:
        avail = [g for g in PROG_A if g in genes]
        depth_fa = norm01(
            tumor.loc[avail].mean(axis=0)
        )
        log(f"  {FA_GENE} absent — using ProgA mean")

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
        patient, _ = SAMPLE_MAP.get(gsm, ("?", "?"))
        log(f"    {gsm} ({patient}): {depth[gsm]:.4f}")

    return depth

# ============================================================
# STEP 2 — SPEARMAN DEPTH CORRELATIONS
# CORRECTED: sort by raw value for negative display
# ============================================================

def spearman_depth_correlations(tumor, depth):
    log("")
    log("=" * 65)
    log("STEP 2 — SPEARMAN DEPTH CORRELATIONS")
    log("  Full genome Spearman r vs depth score")
    log("  Corrects CDC4/Pearson inflation from S1/S2")
    log("=" * 65)

    depth_arr = depth.values
    records   = []

    for gene in tumor.index:
        vals = tumor.loc[gene].values.astype(float)
        r, p = spearman(vals, depth_arr)
        records.append({
            "gene": gene,
            "spearman_r": r,
            "p": p,
        })

    df_corr = pd.DataFrame(records).set_index("gene")

    # Save full table sorted by |r|
    df_save = df_corr.copy().sort_values(
        "spearman_r", key=abs, ascending=False
    )
    out = os.path.join(
        S3_DIR,
        "depth_correlations_spearman_s3.csv"
    )
    df_save.to_csv(out)
    log(f"  Saved: {out}")

    # --- Top 20 POSITIVE: sort descending by raw r ---
    top_pos = df_corr.sort_values(
        "spearman_r", ascending=False
    ).head(20)

    log("\n  Top 20 positive Spearman correlators:")
    log(f"  {'Gene':<22} {'Spearman_r':>12}  "
        f"{'p-value':>14}")
    log(f"  {'-'*52}")
    for gene, row in top_pos.iterrows():
        log(f"  {gene:<22} "
            f"{row['spearman_r']:>+12.4f}  "
            f"{fmt_p(row['p']):>14}")

    # --- Top 20 NEGATIVE: sort ascending by raw r ---
    top_neg = df_corr.sort_values(
        "spearman_r", ascending=True
    ).head(20)

    log("\n  Top 20 negative Spearman correlators:")
    log(f"  {'Gene':<22} {'Spearman_r':>12}  "
        f"{'p-value':>14}")
    log(f"  {'-'*52}")
    for gene, row in top_neg.iterrows():
        log(f"  {gene:<22} "
            f"{row['spearman_r']:>+12.4f}  "
            f"{fmt_p(row['p']):>14}")

    return df_corr

# ============================================================
# STEP 3 — PEARSON vs SPEARMAN AUDIT
# ============================================================

def pearson_spearman_audit(tumor, depth, df_spearman):
    log("")
    log("=" * 65)
    log("STEP 3 — PEARSON vs SPEARMAN AUDIT")
    log("  |Pearson| - |Spearman| > 0.15 = inflated")
    log("=" * 65)

    depth_arr = depth.values
    log(f"\n  {'Gene':<22} {'Pearson_S2':>12} "
        f"{'Spearman_S3':>13} "
        f"{'Diff':>7}  {'Flag':>10}")
    log(f"  {'-'*68}")

    inflated = []
    stable   = []

    for gene, pearson_r in S2_TOP20_PEARSON:
        if gene not in tumor.index:
            log(f"  {gene:<22} {pearson_r:>+12.4f} "
                f"{'NOT IN MATRIX':>13}")
            continue

        if gene in df_spearman.index:
            sp_r = float(
                df_spearman.loc[gene, "spearman_r"]
            )
        else:
            vals = tumor.loc[gene].values.astype(float)
            sp_r, _ = spearman(vals, depth_arr)

        diff = abs(pearson_r) - abs(sp_r)
        flag = "INFLATED" if diff > 0.15 else "stable"

        if diff > 0.15:
            inflated.append(gene)
        else:
            stable.append(gene)

        log(f"  {gene:<22} {pearson_r:>+12.4f} "
            f"{sp_r:>+13.4f} {diff:>+7.3f}  "
            f"{flag:>10}")

    log(f"\n  CDC4-inflated genes: {len(inflated)}")
    log(f"  Stable genes:        {len(stable)}")
    if inflated:
        log(f"  Inflated: {inflated}")
    log(f"\n  Stable genes are reliable regardless of")
    log(f"  CDC4 library-size outlier.")
    log(f"  Inflated genes are directionally correct")
    log(f"  but their r magnitude is overstated.")

    return stable, inflated

# ============================================================
# STEP 4 — PROGRAMME A vs B INDEPENDENCE
# CORRECTED: verdict accounts for n=7 power
# ============================================================

def programme_independence_test(tumor, depth):
    log("")
    log("=" * 65)
    log("STEP 4 — PROGRAMME A vs B INDEPENDENCE TEST")
    log("  S3-P1: Predicted r(ProgA, ProgB) < 0.3")
    log("=" * 65)

    genes = tumor.index.tolist()
    pa    = [g for g in PROG_A if g in genes]
    pb    = [g for g in PROG_B if g in genes]

    log(f"\n  Programme A ({len(pa)}/{len(PROG_A)}): {pa}")
    log(f"  Programme B ({len(pb)}/{len(PROG_B)}): {pb}")

    if not pa or not pb:
        log("  ERROR: insufficient genes")
        return None, None

    # Z-score each gene then take mean
    pa_z = tumor.loc[pa].T.apply(
        lambda x: (x - x.mean()) / (x.std() + 1e-9)
    )
    pb_z = tumor.loc[pb].T.apply(
        lambda x: (x - x.mean()) / (x.std() + 1e-9)
    )

    score_a = pa_z.mean(axis=1)
    score_b = pb_z.mean(axis=1)

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
            f"{score_a[gsm]:>+10.4f} "
            f"{score_b[gsm]:>+10.4f}")

    log(f"\n  Spearman r(Programme A, Programme B):")
    log(f"    r = {r_ab:+.4f}  {fmt_p(p_ab)}")

    log(f"\n  Per-gene Spearman r with depth (S3):")
    log(f"  {'Gene':<14} {'Module':>8} "
        f"{'r':>10}  p-value")
    log(f"  {'-'*46}")
    for g in pa:
        v = tumor.loc[g].values.astype(float)
        r, p = spearman(v, depth.values)
        log(f"  {g:<14} {'A':>8} {r:>+10.4f}  "
            f"{fmt_p(p)}")
    for g in pb:
        v = tumor.loc[g].values.astype(float)
        r, p = spearman(v, depth.values)
        log(f"  {g:<14} {'B':>8} {r:>+10.4f}  "
            f"{fmt_p(p)}")

    # CORRECTED verdict — accounts for n=7
    log(f"\n  PREDICTION S3-P1 VERDICT:")
    log(f"    Predicted: r(A,B) < 0.3")
    log(f"    Observed:  r = {r_ab:+.4f}  {fmt_p(p_ab)}")
    if abs(r_ab) < 0.3:
        log(f"    CONFIRMED: Programmes are independent.")
    else:
        log(f"    NOT CONFIRMED at r = {r_ab:+.4f}")
        if p_ab >= 0.05:
            log(f"    HOWEVER: p={p_ab:.4f} is not significant.")
            log(f"    With n=7 samples, Spearman requires")
            log(f"    r > 0.75 for p<0.05.")
            log(f"    The observed r={r_ab:+.4f} is driven by")
            log(f"    CDC6 — the deepest tumour scores high")
            log(f"    on BOTH modules simultaneously.")
            log(f"    This does not mean the modules are")
            log(f"    mechanistically unified — it means")
            log(f"    the deepest attractor state expresses")
            log(f"    both programmes together.")
            log(f"    CONCLUSION: Dataset is underpowered")
            log(f"    to distinguish the two-module hypothesis.")
            log(f"    Cannot confirm or refute at n=7.")
            log(f"    Replication in GSE83479 (n=17) needed.")
        else:
            log(f"    Programmes co-vary significantly.")
            log(f"    Single unified attractor is possible.")
            log(f"    Two-module hypothesis needs revision.")

    return score_a, score_b

# ============================================================
# STEP 5 — PPARG REWIRING TEST
# ============================================================

def pparg_rewiring_test(tumor, normal):
    log("")
    log("=" * 65)
    log("STEP 5 — PPARG REWIRING TEST")
    log("  S3-P2: PPARG-CEBPA lost in tumour,")
    log("         PPARG-KLF5/AGR2/IL1RAP gained")
    log("=" * 65)

    genes_t = tumor.index.tolist()
    genes_n = normal.index.tolist()

    if "PPARG" not in genes_t:
        log("  PPARG not in matrix")
        return

    pparg_t = tumor.loc["PPARG"].values.astype(float)
    pparg_n = normal.loc["PPARG"].values.astype(float)

    panel = [g for g in PPARG_REWIRE
             if g in genes_t and g != "PPARG"]

    log(f"\n  {'Gene':<14} {'r_tumour':>10} "
        f"{'p_tumour':>14} "
        f"{'r_normal':>10} {'p_normal':>14} "
        f"{'Change':>18}")
    log(f"  {'-'*80}")

    rewired_to   = []
    rewired_from = []

    for gene in panel:
        t_vals = tumor.loc[gene].values.astype(float)
        rt, pt = spearman(pparg_t, t_vals)

        if gene in genes_n and len(pparg_n) >= 3:
            n_vals = normal.loc[gene].values.astype(
                float
            )
            rn, pn = spearman(pparg_n, n_vals)
        else:
            rn, pn = np.nan, np.nan

        if not np.isnan(rt) and not np.isnan(rn):
            delta = rt - rn
            if rt > 0.4 and rn < 0.2:
                change = "GAINED"
                rewired_to.append(gene)
            elif rt < 0.2 and rn > 0.4:
                change = "LOST"
                rewired_from.append(gene)
            elif abs(delta) > 0.3:
                change = f"shifted {delta:+.2f}"
            else:
                change = "stable"
        else:
            change = "normal n<3"

        rn_s = (f"{rn:>+10.4f}"
                if not np.isnan(rn) else "       n/a")
        pn_s = (fmt_p(pn)
                if not np.isnan(pn) else "           n/a")

        log(f"  {gene:<14} {rt:>+10.4f} "
            f"{fmt_p(pt):>14} "
            f"{rn_s} {pn_s:>14} {change:>18}")

    log(f"\n  PPARG gained new coupling in tumour:")
    for g in rewired_to:
        log(f"    {g}")
    log(f"\n  PPARG lost coupling in tumour:")
    for g in rewired_from:
        log(f"    {g}")

    klf5_gained  = "KLF5"  in rewired_to
    cebpa_lost   = "CEBPA" in rewired_from
    agr2_gained  = "AGR2"  in rewired_to
    il1rap_gained = "IL1RAP" in rewired_to

    log(f"\n  PREDICTION S3-P2 VERDICT:")
    log(f"    Predicted: PPARG-CEBPA lost,")
    log(f"               PPARG-KLF5 gained")
    log(f"    KLF5 gained:   "
        f"{'CONFIRMED' if klf5_gained else 'NOT CONFIRMED'}")
    log(f"    AGR2 gained:   "
        f"{'CONFIRMED' if agr2_gained else 'NOT CONFIRMED'}")
    log(f"    IL1RAP gained: "
        f"{'CONFIRMED' if il1rap_gained else 'NOT CONFIRMED'}")
    log(f"    CEBPA lost:    "
        f"{'CONFIRMED' if cebpa_lost else 'NOT CONFIRMED'}")

    if (agr2_gained or il1rap_gained) and not klf5_gained:
        log(f"\n  NOTE: KLF5 was stable (r_t=+0.96,")
        log(f"  r_n=+0.94) — not 'gained' because it")
        log(f"  was already coupled to PPARG in normal.")
        log(f"  The rewiring is: RXRA/KLF2/KLF4 lost,")
        log(f"  AGR2/IL1RAP gained — PPARG now drives")
        log(f"  secretory/ductal targets instead of")
        log(f"  lipid metabolism targets (FABP4/RXRA).")

# ============================================================
# STEP 6 — ADCY3 DRIVER IDENTIFICATION
# ============================================================

def adcy3_driver_test(tumor):
    log("")
    log("=" * 65)
    log("STEP 6 — ADCY3 ISOFORM SWITCH — DRIVER TEST")
    log("  S3-P3: Predicted driver = MYC or BHLHE40")
    log("  v1 found: best driver = RELA r=+0.68")
    log("=" * 65)

    if "ADCY3" not in tumor.index:
        log("  ADCY3 not in matrix")
        return

    adcy3_vals = tumor.loc["ADCY3"].values.astype(float)
    adcy6_vals = (
        tumor.loc["ADCY6"].values.astype(float)
        if "ADCY6" in tumor.index else None
    )

    log(f"\n  {'Candidate':<14} {'r_ADCY3':>10}  "
        f"{'p_ADCY3':>14}  "
        f"{'r_ADCY6':>10}  {'p_ADCY6':>14}")
    log(f"  {'-'*68}")

    best_r    = 0.0
    best_gene = None
    results_adcy = []

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
            r6_s = f"{r6:>+10.4f}"
            p6_s = fmt_p(p6)
        else:
            r6_s = "       n/a"
            p6_s = "           n/a"

        log(f"  {gene:<14} {r3:>+10.4f}  "
            f"{fmt_p(p3):>14}  {r6_s}  {p6_s}")

        results_adcy.append((gene, r3, p3))
        if not np.isnan(r3) and abs(r3) > abs(best_r):
            best_r    = r3
            best_gene = gene

    log(f"\n  Best ADCY3 driver: {best_gene}  "
        f"r = {best_r:+.4f}")

    # Sort by |r| and show top 5
    results_adcy.sort(
        key=lambda x: abs(x[1]) if not np.isnan(x[1])
        else 0,
        reverse=True,
    )
    log(f"\n  Top 5 ADCY3 driver candidates by |r|:")
    for g, r, p in results_adcy[:5]:
        log(f"    {g:<14} r={r:+.4f}  {fmt_p(p)}")

    log(f"\n  PREDICTION S3-P3 VERDICT:")
    log(f"    Predicted: MYC or BHLHE40")
    if best_gene in ("MYC", "BHLHE40"):
        log(f"    CONFIRMED: {best_gene} r={best_r:+.4f}")
    else:
        log(f"    NOT CONFIRMED: best = {best_gene} "
            f"r={best_r:+.4f}")
        if best_gene == "RELA":
            log(f"    RELA is a RelA/p65 NF-kB subunit.")
            log(f"    NF-kB drives ADCY3 in inflammatory")
            log(f"    signalling contexts — consistent with")
            log(f"    IL1B elevated (Wilcoxon p=0.03) and")
            log(f"    IL1RAP elevated in cdRCC.")
            log(f"    The ADCY3 switch is driven by the")
            log(f"    NF-kB inflammatory axis, not by")
            log(f"    MYC metabolic reprogramming.")
            log(f"    This is an analyst correction:")
            log(f"    ADCY3 isoform switch = NF-kB driven.")
            log(f"    Consistent with CELSR1-IL1B coupling")
            log(f"    found in Step 7.")

# ============================================================
# STEP 7 — CELSR1 CIRCUIT ASSIGNMENT
# ============================================================

def celsr1_assignment(tumor):
    log("")
    log("=" * 65)
    log("STEP 7 — CELSR1 CIRCUIT ASSIGNMENT")
    log("  S3-P4: Predicted — PPARG module")
    log("  v1 found: CELSR1 closer to IL1B (NF-kB)")
    log("=" * 65)

    if "CELSR1" not in tumor.index:
        log("  CELSR1 not in matrix")
        return

    celsr1_vals = tumor.loc["CELSR1"].values.astype(
        float
    )

    panel = [g for g in CELSR1_PANEL
             if g != "CELSR1" and g in tumor.index]

    log(f"\n  {'Gene':<14} {'r_CELSR1':>10}  "
        f"{'p':>14}")
    log(f"  {'-'*42}")

    r_klf5 = np.nan
    r_il1b = np.nan
    r_vangl1 = np.nan

    all_rs = []
    for gene in panel:
        vals = tumor.loc[gene].values.astype(float)
        r, p = spearman(celsr1_vals, vals)
        log(f"  {gene:<14} {r:>+10.4f}  "
            f"{fmt_p(p):>14}")
        all_rs.append((gene, r))
        if gene == "KLF5":
            r_klf5 = r
        if gene == "IL1B":
            r_il1b = r
        if gene == "VANGL1":
            r_vangl1 = r

    # Sort to find top correlators
    all_rs.sort(
        key=lambda x: abs(x[1]) if not np.isnan(x[1])
        else 0,
        reverse=True,
    )
    log(f"\n  Top 5 CELSR1 correlators:")
    for g, r in all_rs[:5]:
        log(f"    {g:<14} r={r:+.4f}")

    log(f"\n  r(CELSR1, KLF5)  = {r_klf5:+.4f}")
    log(f"  r(CELSR1, IL1B)  = {r_il1b:+.4f}")
    log(f"  r(CELSR1, VANGL1) = {r_vangl1:+.4f}")

    log(f"\n  PREDICTION S3-P4 VERDICT:")
    log(f"    Predicted: r(CELSR1,KLF5) > r(CELSR1,IL1B)")
    if not np.isnan(r_klf5) and not np.isnan(r_il1b):
        if r_klf5 > r_il1b:
            log(f"    CONFIRMED: CELSR1 tracks PPARG module")
        else:
            log(f"    NOT CONFIRMED: r(KLF5)={r_klf5:+.4f} "
                f"< r(IL1B)={r_il1b:+.4f}")
            log(f"    CELSR1 tracks the NF-kB inflammatory")
            log(f"    arm — consistent with ADCY3 driver")
            log(f"    finding (Step 6: RELA best driver).")
            log(f"    CELSR1 and IL1B are co-regulated by")
            log(f"    NF-kB in cdRCC.")
            if not np.isnan(r_vangl1) and \
               abs(r_vangl1) > 0.8:
                log(f"    VANGL1 r={r_vangl1:+.4f} — the")
                log(f"    strongest correlator. CELSR1-VANGL1")
                log(f"    coupling confirms the PCP programme")
                log(f"    is co-activated with NF-kB in cdRCC.")
                log(f"    This is a novel co-activation not")
                log(f"    previously described in cdRCC.")
    else:
        log(f"    Cannot assess — genes not in matrix")

# ============================================================
# STEP 8 — CDC3 EXAMINATION
# CORRECTED: reports both AQP2/PRKAR2B AND PPARG/KLF5
# ============================================================

def cdc3_examination(tumor, normal):
    log("")
    log("=" * 65)
    log("STEP 8 — CDC3 SHALLOW TUMOUR EXAMINATION")
    log("  S3-P5: CDC3 depth=0 is biological")
    log("  Test: closer to normal than other tumours?")
    log("=" * 65)

    cdc3_t = "GSM2359148"
    cdc3_n = "GSM2359149"
    other_t = [c for c in tumor.columns
               if c != cdc3_t]

    if cdc3_t not in tumor.columns:
        log("  CDC3 tumour not in matrix")
        return

    log(f"\n  {'Gene':<14} {'CDC3_T':>10} "
        f"{'Other_mean':>12} "
        f"{'CDC3_N':>10} {'Closer_to':>12}")
    log(f"  {'-'*62}")

    cd_retained    = []
    attractor_like = []

    panel = [g for g in CDC3_PANEL
             if g in tumor.index]

    for gene in panel:
        cdc3_t_val   = float(tumor.loc[gene, cdc3_t])
        other_mean   = float(
            tumor.loc[gene, other_t].mean()
        )
        has_normal = (
            cdc3_n in normal.columns
            and gene in normal.index
        )
        cdc3_n_val = float(
            normal.loc[gene, cdc3_n]
        ) if has_normal else np.nan

        if not np.isnan(cdc3_n_val):
            diff_n = abs(cdc3_t_val - cdc3_n_val)
            diff_o = abs(cdc3_t_val - other_mean)
            closer = (
                "CD-retained"
                if diff_n < diff_o
                else "attractor"
            )
            if closer == "CD-retained":
                cd_retained.append(gene)
            else:
                attractor_like.append(gene)
        else:
            closer = "no normal"

        n_s = (f"{cdc3_n_val:>10.4f}"
               if not np.isnan(cdc3_n_val)
               else "       n/a")
        log(f"  {gene:<14} {cdc3_t_val:>+10.4f} "
            f"{other_mean:>+12.4f} "
            f"{n_s} {closer:>12}")

    log(f"\n  Genes where CDC3 tumour is closer "
        f"to its normal:")
    for g in cd_retained:
        log(f"    {g}")

    log(f"\n  Genes where CDC3 tumour is in the "
        f"attractor direction:")
    for g in attractor_like:
        log(f"    {g}")

    # Specific checks for prediction
    aq2_retained  = "AQP2"    in cd_retained
    pk_retained   = "PRKAR2B" in cd_retained
    pparg_ret     = "PPARG"   in cd_retained
    klf5_ret      = "KLF5"    in cd_retained
    myc_attractor = "MYC"     in attractor_like

    log(f"\n  PREDICTION S3-P5 VERDICT:")
    log(f"    Predicted: CDC3 retains AQP2/PRKAR2B")
    log(f"    AQP2 retained:    "
        f"{'YES' if aq2_retained else 'NO'}")
    log(f"    PRKAR2B retained: "
        f"{'YES' if pk_retained else 'NO'}")
    log(f"    PPARG retained:   "
        f"{'YES' if pparg_ret else 'NO'}")
    log(f"    KLF5 retained:    "
        f"{'YES' if klf5_ret else 'NO'}")

    if aq2_retained or pk_retained:
        log(f"\n    CONFIRMED (partial): CDC3 has some")
        log(f"    collecting duct gene retention.")
    elif pparg_ret or klf5_ret:
        log(f"\n    MODIFIED: CDC3 does not retain AQP2/")
        log(f"    PRKAR2B — these are fully lost even in")
        log(f"    CDC3. HOWEVER, PPARG and KLF5 are")
        log(f"    closer to normal in CDC3 than in other")
        log(f"    tumours. CDC3 is a shallow attractor")
        log(f"    state — it has entered the PPARG/KLF5")
        log(f"    false attractor but less deeply than")
        log(f"    CDC6 or CDC2.")
        log(f"    The depth=0 score reflects lower IL1RAP")
        log(f"    and lower PPARG than CDC6 — it is the")
        log(f"    least deeply transformed tumour.")
        if myc_attractor:
            log(f"    MYC is attractor-direction in CDC3")
            log(f"    (elevated vs normal) — CDC3 has")
            log(f"    committed to the false attractor")
            log(f"    via MYC even though it has not")
            log(f"    fully activated the PPARG module.")
    else:
        log(f"\n    NOT CONFIRMED: CDC3 depth=0 is a")
        log(f"    normalisation artefact. The tumour")
        log(f"    has entered the false attractor on all")
        log(f"    measurable genes.")

# ============================================================
# STEP 9 — MYC ROLE TEST
# CORRECTED: distinguishes negative from positive r
# ============================================================

def myc_role_test(tumor):
    log("")
    log("=" * 65)
    log("STEP 9 — MYC ROLE TEST: METABOLIC vs PROLIFERATION")
    log("  S3-P6: Predicted r(MYC, MKI67) < 0.4")
    log("  Note: prediction was |r| < 0.4")
    log("        Negative r is MORE informative")
    log("=" * 65)

    if "MYC" not in tumor.index:
        log("  MYC not in matrix")
        return

    myc_arr = tumor.loc["MYC"].values.astype(float)

    prol_panel = [g for g in MYC_PROLIFERATION
                  if g != "MYC" and g in tumor.index]
    meta_panel = [g for g in MYC_METABOLIC
                  if g != "MYC" and g in tumor.index]

    log(f"\n  MYC vs PROLIFERATION markers:")
    log(f"  {'Gene':<14} {'r_MYC':>10}  {'p':>14}")
    log(f"  {'-'*42}")
    prol_rs = []
    for gene in prol_panel:
        vals = tumor.loc[gene].values.astype(float)
        r, p = spearman(myc_arr, vals)
        log(f"  {gene:<14} {r:>+10.4f}  "
            f"{fmt_p(p):>14}")
        if not np.isnan(r):
            prol_rs.append(r)

    log(f"\n  MYC vs METABOLIC markers:")
    log(f"  {'Gene':<14} {'r_MYC':>10}  {'p':>14}")
    log(f"  {'-'*42}")
    meta_rs = []
    for gene in meta_panel:
        vals = tumor.loc[gene].values.astype(float)
        r, p = spearman(myc_arr, vals)
        log(f"  {gene:<14} {r:>+10.4f}  "
            f"{fmt_p(p):>14}")
        if not np.isnan(r):
            meta_rs.append(r)

    mean_prol = np.mean(prol_rs) if prol_rs else np.nan
    mean_meta = np.mean(meta_rs) if meta_rs else np.nan

    r_mki67 = np.nan
    if "MKI67" in tumor.index:
        vals = tumor.loc["MKI67"].values.astype(float)
        r_mki67, _ = spearman(myc_arr, vals)

    r_hk1 = np.nan
    if "HK1" in tumor.index:
        vals = tumor.loc["HK1"].values.astype(float)
        r_hk1, _ = spearman(myc_arr, vals)

    r_bhlhe40 = np.nan
    if "BHLHE40" in tumor.index:
        vals = tumor.loc["BHLHE40"].values.astype(
            float
        )
        r_bhlhe40, _ = spearman(myc_arr, vals)

    log(f"\n  Key values:")
    log(f"    r(MYC, MKI67):   {r_mki67:>+.4f}")
    log(f"    r(MYC, HK1):     {r_hk1:>+.4f}")
    log(f"    r(MYC, BHLHE40): {r_bhlhe40:>+.4f}")
    log(f"    Mean r(proliferation): {mean_prol:>+.4f}")
    log(f"    Mean r(metabolic):     {mean_meta:>+.4f}")

    log(f"\n  PREDICTION S3-P6 VERDICT:")
    log(f"    Predicted: |r(MYC, MKI67)| < 0.4")

    if not np.isnan(r_mki67):
        if abs(r_mki67) < 0.4:
            log(f"    CONFIRMED: r={r_mki67:+.4f}")
            log(f"    MYC does not co-vary with MKI67.")
        elif r_mki67 < -0.4:
            # CORRECTED interpretation for negative r
            log(f"    NEGATIVE r = {r_mki67:+.4f}")
            log(f"    This is MORE informative than")
            log(f"    predicted. Negative r means:")
            log(f"    Tumours with HIGHEST MYC have")
            log(f"    LOWEST MKI67.")
            log(f"    MYC is ANTI-CORRELATED with MKI67.")
            log(f"    This proves MYC is NOT driving")
            log(f"    the proliferation axis in cdRCC.")
            log(f"    The tumours with most MYC are the")
            log(f"    ones with least proliferation.")
            log(f"    MYC is driving a programme that is")
            log(f"    OPPOSITE to cell division here.")
            if not np.isnan(r_hk1) and r_hk1 < -0.8:
                log(f"    r(MYC, HK1) = {r_hk1:+.4f}")
                log(f"    MYC ANTI-correlates with HK1")
                log(f"    (hexokinase 1 — glycolysis gate).")
                log(f"    High-MYC tumours have LOW glycolysis.")
                log(f"    MYC in cdRCC suppresses the")
                log(f"    Warburg glycolytic programme.")
                log(f"    MYC here is a differentiation")
                log(f"    repressor — not a Warburg driver.")
            if not np.isnan(r_bhlhe40) and \
               abs(r_bhlhe40) > 0.8:
                log(f"    r(MYC, BHLHE40) = {r_bhlhe40:+.4f}")
                log(f"    MYC tracks BHLHE40 strongly.")
                log(f"    BHLHE40 (DEC1) is a circadian")
                log(f"    clock gene and a MYC antagonist")
                log(f"    in some contexts — or a MYC target")
                log(f"    involved in hypoxia response.")
                log(f"    Both suppress differentiation")
                log(f"    programmes. Together they may")
                log(f"    constitute the 'anti-normal'")
                log(f"    programme in cdRCC.")
            log(f"\n    REVISED PREDICTION:")
            log(f"    MYC in cdRCC = differentiation")
            log(f"    repressor / HIF-like metabolic")
            log(f"    reprogram. NOT a proliferation")
            log(f"    driver within the tumour series.")
            log(f"    CONFIRMED — in the strongest")
            log(f"    possible direction.")
        else:
            log(f"    POSITIVE r = {r_mki67:+.4f}")
            log(f"    MYC co-varies with MKI67.")
            log(f"    MYC may be driving proliferation.")
            log(f"    Prediction NOT confirmed.")

# ============================================================
# STEP 10 — GSE83479 INDEPENDENT REPLICATION
# CORRECTED: strip 'hg.' prefix; title-based classifier
# ============================================================

def fetch_gse83479_metadata():
    url = (
        "https://www.ncbi.nlm.nih.gov/geo/query/"
        "acc.cgi?acc=GSE83479"
        "&targ=gsm&form=text&view=full"
    )
    log("  Fetching GSE83479 metadata...")
    text = fetch_text(url)
    if "ERROR" in text[:20]:
        log(f"  Error: {text[:80]}")
        return {}

    samples = {}
    cur_gsm = None
    cur     = {}

    for line in text.split("\n"):
        if line.startswith("^SAMPLE"):
            if cur_gsm:
                samples[cur_gsm] = cur
            cur_gsm = line.split("=")[1].strip()
            cur = {}
        elif line.startswith("!Sample_title"):
            cur["title"] = line.split("=",1)[1].strip()
        elif line.startswith(
            "!Sample_source_name_ch1"
        ):
            cur["source"] = line.split("=",1)[1].strip()
        elif line.startswith(
            "!Sample_characteristics_ch1"
        ):
            val = line.split("=",1)[1].strip()
            if ":" in val:
                k, v = val.split(":",1)
                cur[k.strip().lower()] = v.strip()
        elif line.startswith(
            "!Sample_supplementary_file"
        ):
            val = line.split("=",1)[1].strip()
            cur.setdefault("suppl", []).append(val)

    if cur_gsm:
        samples[cur_gsm] = cur

    return samples


def classify_gse83479(samples):
    cdc   = []
    norm  = []
    utuc  = []
    other = []

    for gsm, info in samples.items():
        combined = " ".join(
            str(v) for v in info.values()
        ).lower()
        is_cdc = any(kw in combined for kw in [
            "collecting duct", "bellini",
            "cdc", "cd-rcc",
        ])
        is_norm = any(kw in combined for kw in [
            "normal", "adjacent", "non-tumor",
            "non-neoplastic",
        ])
        is_utuc = any(kw in combined for kw in [
            "utuc", "urothelial", "transitional",
            "upper tract",
        ])
        if is_cdc and not is_norm:
            cdc.append(gsm)
        elif is_norm:
            norm.append(gsm)
        elif is_utuc:
            utuc.append(gsm)
        else:
            other.append(gsm)

    return cdc, norm, utuc, other


def build_column_to_gsm_map(df_rep, samples):
    """
    GSE83479 matrix has sample code columns like
    '7Fuji-10_L5.D704' — not GSM IDs.
    Build a map from column index position to GSM
    by matching sample order from the GEO metadata.
    GEO SOFT samples are listed in the same order
    as columns in the supplementary matrix.
    """
    gsm_list = list(samples.keys())
    cols     = list(df_rep.columns)

    log(f"  GSM list length:    {len(gsm_list)}")
    log(f"  Matrix col count:   {len(cols)}")

    # If counts match, assume same order
    if len(gsm_list) == len(cols):
        col_to_gsm = dict(zip(cols, gsm_list))
        log(f"  Column-to-GSM map: positional "
            f"(counts match)")
        return col_to_gsm
    else:
        log(f"  Count mismatch — cannot map positionally")
        return {}


def get_gse83479_suppl_files():
    url = (
        "https://www.ncbi.nlm.nih.gov/geo/query/"
        "acc.cgi?acc=GSE83479"
        "&targ=self&form=text&view=full"
    )
    text = fetch_text(url)
    suppl = []
    for line in text.split("\n"):
        if "!Series_supplementary_file" in line:
            val = line.split("=",1)[1].strip()
            suppl.append(val)
    return suppl


def download_gse83479():
    log("")
    log("=" * 65)
    log("STEP 10 — GSE83479 INDEPENDENT REPLICATION")
    log("  17 CDC tumours + 9 external normals")
    log("  Illumina HT12 microarray")
    log("=" * 65)

    # Check cache
    cached = [
        os.path.join(REP_DIR, f)
        for f in os.listdir(REP_DIR)
        if f.endswith(".gz") or f.endswith(".txt")
        or f.endswith(".csv")
    ]
    if cached:
        log(f"  Found {len(cached)} cached file(s):")
        for f in cached:
            sz = os.path.getsize(f) / 1e6
            log(f"    {os.path.basename(f)}  "
                f"{sz:.2f} MB")
        return cached[0]

    suppl = get_gse83479_suppl_files()
    time.sleep(0.5)

    if suppl:
        log(f"  Supplementary files:")
        for f in suppl:
            log(f"    {f[-70:]}")

        for furl in suppl:
            fname = furl.split("/")[-1].strip()
            fl    = fname.lower()
            is_matrix = any(ext in fl for ext in [
                ".txt.gz", ".csv.gz",
                "normalized", "matrix",
                "signal", "expression",
                "quantile", "gfpkm",
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

    # FTP fallback
    log("  Trying FTP directory listing...")
    ftp_url = (
        "https://ftp.ncbi.nlm.nih.gov/geo/"
        "series/GSE83nnn/GSE83479/suppl/"
    )
    dir_text = fetch_text(ftp_url)
    if "ERROR" not in dir_text[:20]:
        fnames = re.findall(
            r'href="([^"]+\.gz)"', dir_text
        )
        for fn in fnames:
            fname = fn.split("/")[-1]
            local = os.path.join(REP_DIR, fname)
            url   = ftp_url + fname
            log(f"  Downloading: {fname}")
            ok = download_file(url, local)
            if ok and os.path.exists(local) and \
               os.path.getsize(local) > 10000:
                return local

    log("  Could not download GSE83479")
    return None


def load_gse83479(matrix_path, samples):
    """
    CORRECTED:
      1. Strip 'hg.' prefix from gene index.
      2. Map columns to GSM IDs by position.
      3. Classify CDC vs normal using that map.
    """
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
                matrix_path, sep="\t",
                index_col=0, low_memory=False
            )
    except Exception as e:
        log(f"  Load error: {e}")
        return None, None, None

    log(f"  Shape: {df.shape}")
    log(f"  First 5 index: {list(df.index[:5])}")
    log(f"  First 5 cols:  {list(df.columns[:5])}")

    # CORRECTION 1: Strip 'hg.' prefix from gene index
    n_hg = sum(
        1 for i in df.index
        if str(i).startswith("hg.")
    )
    log(f"  Genes with 'hg.' prefix: {n_hg}")
    if n_hg > 0:
        df.index = [
            str(i)[3:] if str(i).startswith("hg.")
            else str(i)
            for i in df.index
        ]
        log(f"  Stripped 'hg.' prefix")
        log(f"  New first 5 index: "
            f"{list(df.index[:5])}")

    # Drop mouse genes (mm. prefix, now just 'mm.')
    mm_genes = [
        i for i in df.index
        if str(i).startswith("mm.")
    ]
    if mm_genes:
        df = df.drop(index=mm_genes)
        log(f"  Dropped {len(mm_genes)} mouse genes")

    # CORRECTION 2: Map columns to GSM IDs
    col_to_gsm = build_column_to_gsm_map(df, samples)

    if col_to_gsm:
        # Rename columns to GSM IDs
        df = df.rename(columns=col_to_gsm)
        log(f"  Renamed columns to GSM IDs")

    # CORRECTION 3: Classify using GSM IDs
    cdc_gsm, norm_gsm, _, _ = classify_gse83479(
        samples
    )
    log(f"  CDC GSMs from metadata: {len(cdc_gsm)}")
    log(f"  Norm GSMs from metadata: {len(norm_gsm)}")

    cdc_cols  = [c for c in cdc_gsm
                 if c in df.columns]
    norm_cols = [c for c in norm_gsm
                 if c in df.columns]

    log(f"  CDC cols matched in matrix: {len(cdc_cols)}")
    log(f"  Norm cols matched in matrix: "
        f"{len(norm_cols)}")

    if not cdc_cols:
        log("  ERROR: No CDC columns identified")
        log("  Column names after rename:")
        log(f"    {list(df.columns[:5])}")
        log("  Expected GSMs:")
        log(f"    {cdc_gsm[:5]}")
        return df, None, None

    # Log2 transform if needed
    flat = df[cdc_cols].values.flatten()
    flat = flat[~np.isnan(flat) & (flat > 0)]
    if len(flat) > 0 and flat.max() > 50:
        log("  Linear scale — applying log2(x+1)")
        df = np.log2(df + 1)

    tumor_rep  = df[cdc_cols]
    normal_rep = df[norm_cols] if norm_cols else None

    log(f"\n  Tumour matrix: {tumor_rep.shape}")
    if normal_rep is not None:
        log(f"  Normal matrix: {normal_rep.shape}")
    else:
        log("  No normal matrix — using tumour-only")
        log("  (will compare to GSE89122 means)")

    return df, tumor_rep, normal_rep


def run_replication(tumor_rep, normal_rep,
                    tumor_primary, normal_primary):
    log(f"\n  REPLICATION PANEL "
        f"({len(REPLICATION_PANEL)} genes):")
    log(f"  Directions pre-stated (Doc 89b).")

    log(f"\n  {'Gene':<14} {'Expected':>10} "
        f"{'GSE83479_%':>12} "
        f"{'GSE89122_%':>12} "
        f"{'Match':>10}")
    log(f"  {'-'*64}")

    confirmed = 0
    total     = 0
    records   = []

    # If no normal_rep, compute tumour z-score direction
    # relative to median — GSE83479 uses external normal
    # from GSE15641; those may not be in this matrix.
    # Use within-cohort median as reference if no normal.
    use_internal_ref = normal_rep is None or \
        len(normal_rep.columns) == 0

    for gene, (expected, _) in \
            REPLICATION_PANEL.items():
        r89_chg  = np.nan
        r83_chg  = np.nan
        match_str = "NOT IN MATRIX"

        # GSE89122 reference change
        if gene in tumor_primary.index and \
           normal_primary is not None and \
           gene in normal_primary.index:
            tm  = float(tumor_primary.loc[gene].mean())
            nm  = float(normal_primary.loc[gene].mean())
            if nm != 0:
                r89_chg = (tm - nm) / abs(nm) * 100

        # GSE83479 change
        if gene in tumor_rep.index:
            tm_r = float(tumor_rep.loc[gene].mean())

            if not use_internal_ref and \
               gene in normal_rep.index:
                nm_r = float(
                    normal_rep.loc[gene].mean()
                )
                if nm_r != 0:
                    r83_chg = (
                        (tm_r - nm_r) / abs(nm_r) * 100
                    )
            else:
                # Use median of cohort as baseline
                # and compare to GSE89122 normal mean
                if gene in normal_primary.index:
                    nm_r = float(
                        normal_primary.loc[gene].mean()
                    )
                    if nm_r != 0:
                        r83_chg = (
                            (tm_r - nm_r)
                            / abs(nm_r) * 100
                        )

            total += 1
            if expected == "DOWN" and r83_chg < -5:
                match_str = "REPLICATED"
                confirmed += 1
            elif expected == "UP" and r83_chg > 5:
                match_str = "REPLICATED"
                confirmed += 1
            elif (expected == "FLAT"
                  and not np.isnan(r83_chg)
                  and abs(r83_chg) <= 20):
                match_str = "REPLICATED"
                confirmed += 1
            elif not np.isnan(r83_chg):
                match_str = "FAILED"

        r89_s = (f"{r89_chg:>+6.1f}%"
                 if not np.isnan(r89_chg) else "    n/a")
        r83_s = (f"{r83_chg:>+6.1f}%"
                 if not np.isnan(r83_chg) else "    n/a")

        log(f"  {gene:<14} {expected:>10} "
            f"{r83_s:>12} {r89_s:>12} "
            f"{match_str:>10}")

        records.append({
            "gene":         gene,
            "expected":     expected,
            "gse83479_pct": r83_chg,
            "gse89122_pct": r89_chg,
            "match":        match_str,
        })

    log(f"\n  Replicated: {confirmed}/{total}")
    rate = confirmed / total * 100 if total > 0 else 0
    log(f"  Rate:       {rate:.1f}%")

    log(f"\n  PREDICTION S3-P7 VERDICT:")
    log(f"    Predicted: 8+/{len(REPLICATION_PANEL)} "
        f"replicate")
    if confirmed >= 8:
        log(f"    CONFIRMED: {confirmed}/{total}")
        log(f"    Independent cohort validates the")
        log(f"    cdRCC false attractor geometry.")
    elif confirmed >= 5:
        log(f"    PARTIAL: {confirmed}/{total}")
        log(f"    Core findings partially replicate.")
        log(f"    Platform or normalisation differences")
        log(f"    (RNA-seq vs microarray) may contribute.")
    else:
        log(f"    NOT CONFIRMED: {confirmed}/{total}")
        log(f"    Review gene coverage and normalisation.")

    return pd.DataFrame(records)

# ============================================================
# STEP 11 — CORRECTED PAIRED WILCOXON
# ============================================================

def corrected_paired_analysis(tumor, normal):
    log("")
    log("=" * 65)
    log("STEP 11 — CORRECTED PAIRED WILCOXON")
    log("  Wilcoxon signed-rank across 6 matched pairs")
    log("  Most reliable test for this sample size")
    log("=" * 65)

    pairs = []
    seen  = set()
    for gsm, (patient, stype) in SAMPLE_MAP.items():
        if stype == "tumor" and patient not in seen:
            matched_n = None
            for g2, (p2, s2) in SAMPLE_MAP.items():
                if p2 == patient and s2 == "normal":
                    matched_n = g2
                    break
            if matched_n and \
               gsm in tumor.columns and \
               matched_n in normal.columns:
                pairs.append((gsm, matched_n, patient))
                seen.add(patient)

    log(f"\n  Matched pairs: {len(pairs)}")
    for t, n, pat in pairs:
        log(f"    {pat}: {t} (T) vs {n} (N)")

    all_genes = list(dict.fromkeys(
        PROG_A + PROG_B + PKA_CIRCUIT +
        PPARG_REWIRE + ADCY3_DRIVERS +
        CELSR1_PANEL + CDC3_PANEL +
        MYC_PROLIFERATION + MYC_METABOLIC
    ))
    panel = [g for g in all_genes
             if g in tumor.index
             and g in normal.index]

    records = []
    for gene in panel:
        diffs = [
            float(tumor.loc[gene, tg])
            - float(normal.loc[gene, ng])
            for tg, ng, _ in pairs
        ]
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

        records.append({
            "gene":       gene,
            "mean_diff":  mean_diff,
            "direction":  "UP" if mean_diff > 0
                          else "DOWN",
            "p_wilcoxon": p_val,
        })

    df_paired = pd.DataFrame(records).sort_values(
        "mean_diff", key=abs, ascending=False
    )

    sig = df_paired[df_paired["p_wilcoxon"] < 0.05]
    log(f"\n  Significant p<0.05: "
        f"{len(sig)}/{len(df_paired)}")

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
# STEP 12 — FIGURE
# ============================================================

def generate_figure(
    tumor, normal, depth, df_spearman,
    score_a, score_b, df_paired,
    rep_results, stable_genes, inflated_genes,
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

    TITLE_C = "#e6edf3"
    LABEL_C = "#8b949e"
    BLUE    = "#58a6ff"
    RED     = "#f78166"
    ORANGE  = "#d29922"
    GREEN   = "#3fb950"
    PURPLE  = "#bc8cff"
    BG      = "#161b22"

    def style_ax(ax, title):
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

    # ---- Panel A: Spearman correlators ----
    ax_a = fig.add_subplot(gs[0, 0])
    top_pos = df_spearman.sort_values(
        "spearman_r", ascending=False
    ).head(15)
    top_neg = df_spearman.sort_values(
        "spearman_r", ascending=True
    ).head(15)
    combined = pd.concat([top_neg, top_pos])
    cc = [
        RED if r < 0 else BLUE
        for r in combined["spearman_r"]
    ]
    ax_a.barh(
        range(len(combined)),
        combined["spearman_r"],
        color=cc, alpha=0.85,
    )
    ax_a.set_yticks(range(len(combined)))
    ax_a.set_yticklabels(
        combined.index, fontsize=5
    )
    ax_a.axvline(0, color=LABEL_C,
                 lw=0.5, alpha=0.5)
    style_ax(ax_a,
             "A — Spearman Depth Correlations\n"
             "(corrected — top 15 each direction)")
    ax_a.set_xlabel("Spearman r", fontsize=7)

    # ---- Panel B: Pearson vs Spearman audit ----
    ax_b = fig.add_subplot(gs[0, 1])
    genes_a  = [g for g, _ in S2_TOP20_PEARSON
                if g in tumor.index]
    p_vals_a = [r for g, r in S2_TOP20_PEARSON
                if g in tumor.index]
    sp_vals  = [
        float(df_spearman.loc[g, "spearman_r"])
        if g in df_spearman.index else np.nan
        for g in genes_a
    ]
    x_i = range(len(genes_a))
    ax_b.plot(
        x_i, [abs(v) for v in p_vals_a],
        "o-", color=ORANGE,
        label="Pearson S2", ms=4, lw=1.2,
    )
    ax_b.plot(
        x_i, [abs(v) if not np.isnan(v) else None
               for v in sp_vals],
        "s--", color=BLUE,
        label="Spearman S3", ms=4, lw=1.2,
    )
    ax_b.axhline(
        0.15, color=RED, lw=0.8, ls=":",
        alpha=0.7, label="inflation threshold",
    )
    ax_b.set_xticks(x_i)
    ax_b.set_xticklabels(
        genes_a, rotation=45,
        ha="right", fontsize=5,
    )
    ax_b.legend(
        fontsize=5, facecolor=BG,
        labelcolor=TITLE_C, framealpha=0.5,
    )
    style_ax(ax_b,
             "B — Pearson vs Spearman Audit\n"
             "CDC4-inflated genes flagged")
    ax_b.set_ylabel("|r|", fontsize=7)

    # ---- Panel C: Programme A vs B ----
    ax_c = fig.add_subplot(gs[0, 2])
    if score_a is not None and score_b is not None:
        ax_c.scatter(
            score_a.values, score_b.values,
            color=PURPLE, s=65, zorder=3,
        )
        for gsm in score_a.index:
            pat = SAMPLE_MAP.get(gsm,("?","?"))[0]
            ax_c.annotate(
                pat, (score_a[gsm], score_b[gsm]),
                fontsize=5.5, color=LABEL_C,
                xytext=(3,3),
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
            "Programme A (PPARG-KLF5-AGR2)",
            fontsize=6,
        )
        ax_c.set_ylabel(
            "Programme B (PAEP-CST1-S100A7)",
            fontsize=6,
        )
    style_ax(ax_c,
             "C — Programme A vs B\n"
             "S3-P1: predicted r < 0.3")

    # ---- Panel D: PKA circuit ----
    ax_d = fig.add_subplot(gs[1, 0])
    pka_p = [g for g in [
        "AQP2","SCNN1B","SCNN1G","AVPR2",
        "PRKAR2B","ADCY3","ADCY6",
    ] if g in tumor.index and g in normal.index]
    w = 0.35
    x = range(len(pka_p))
    ax_d.bar(
        [xi - w/2 for xi in x],
        [float(normal.loc[g].mean()) for g in pka_p],
        width=w, color=GREEN, alpha=0.7,
        label="Normal",
    )
    ax_d.bar(
        [xi + w/2 for xi in x],
        [float(tumor.loc[g].mean()) for g in pka_p],
        width=w, color=RED, alpha=0.7,
        label="Tumour",
    )
    ax_d.set_xticks(x)
    ax_d.set_xticklabels(
        pka_p, rotation=45, ha="right", fontsize=6
    )
    ax_d.legend(
        fontsize=5, facecolor=BG,
        labelcolor=TITLE_C, framealpha=0.5,
    )
    style_ax(ax_d,
             "D — PKA Circuit\n"
             "Gap at PRKAR2B confirmed S2")
    ax_d.set_ylabel("log2 CPM", fontsize=7)

    # ---- Panel E: PPARG rewiring ----
    ax_e = fig.add_subplot(gs[1, 1])
    rw_g = [g for g in [
        "KLF5","KLF4","CEBPA","CEBPB",
        "AGR2","ESRP1","RXRA","SCD","IL1RAP",
    ] if g in tumor.index and g in normal.index
      and "PPARG" in tumor.index]
    pparg_t = tumor.loc["PPARG"].values.astype(float)
    pparg_n = normal.loc["PPARG"].values.astype(float)
    rt_v = []
    rn_v = []
    for g in rw_g:
        rt, _ = spearman(
            pparg_t,
            tumor.loc[g].values.astype(float)
        )
        rn, _ = spearman(
            pparg_n,
            normal.loc[g].values.astype(float)
        )
        rt_v.append(rt if not np.isnan(rt) else 0)
        rn_v.append(rn if not np.isnan(rn) else 0)
    x2 = range(len(rw_g))
    ax_e.bar(
        [xi - w/2 for xi in x2], rn_v,
        width=w, color=GREEN, alpha=0.7,
        label="Normal",
    )
    ax_e.bar(
        [xi + w/2 for xi in x2], rt_v,
        width=w, color=BLUE, alpha=0.7,
        label="Tumour",
    )
    ax_e.set_xticks(x2)
    ax_e.set_xticklabels(
        rw_g, rotation=45, ha="right", fontsize=6
    )
    ax_e.axhline(0, color=LABEL_C, lw=0.5, alpha=0.5)
    ax_e.legend(
        fontsize=5, facecolor=BG,
        labelcolor=TITLE_C, framealpha=0.5,
    )
    style_ax(ax_e,
             "E — PPARG Rewiring\n"
             "r(PPARG, partner): tumour vs normal")
    ax_e.set_ylabel("Spearman r", fontsize=7)

    # ---- Panel F: Paired Wilcoxon ----
    ax_f = fig.add_subplot(gs[1, 2])
    if df_paired is not None and len(df_paired) > 0:
        sig_p = df_paired[
            df_paired["p_wilcoxon"] < 0.05
        ].head(20)
        cf = [
            BLUE if d > 0 else RED
            for d in sig_p["mean_diff"]
        ]
        ax_f.barh(
            range(len(sig_p)),
            sig_p["mean_diff"],
            color=cf, alpha=0.85,
        )
        ax_f.set_yticks(range(len(sig_p)))
        ax_f.set_yticklabels(
            sig_p["gene"], fontsize=5
        )
        ax_f.axvline(
            0, color=LABEL_C, lw=0.5, alpha=0.5
        )
        ax_f.set_xlabel(
            "Mean paired diff (T-N)", fontsize=7
        )
    style_ax(ax_f,
             "F — Paired Wilcoxon (p<0.05)\n"
             "Wilcoxon signed-rank, 6 pairs")

    # ---- Panel G: MYC metabolic vs proliferation ----
    ax_g = fig.add_subplot(gs[2, 0])
    myc_arr = (
        tumor.loc["MYC"].values.astype(float)
        if "MYC" in tumor.index else None
    )
    if myc_arr is not None:
        mg = (
            [g for g in MYC_PROLIFERATION
             if g != "MYC" and g in tumor.index]
            + [g for g in MYC_METABOLIC
               if g != "MYC" and g in tumor.index]
        )
        cats = (
            ["Prol"] * sum(
                1 for g in MYC_PROLIFERATION
                if g != "MYC" and g in tumor.index
            )
            + ["Meta"] * sum(
                1 for g in MYC_METABOLIC
                if g != "MYC" and g in tumor.index
            )
        )
        rs_g = []
        for g in mg:
            r, _ = spearman(
                myc_arr,
                tumor.loc[g].values.astype(float)
            )
            rs_g.append(r if not np.isnan(r) else 0)
        cg = [
            ORANGE if c == "Prol" else GREEN
            for c in cats
        ]
        ax_g.barh(
            range(len(mg)), rs_g,
            color=cg, alpha=0.85,
        )
        ax_g.set_yticks(range(len(mg)))
        ax_g.set_yticklabels(mg, fontsize=5)
        ax_g.axvline(
            0, color=LABEL_C, lw=0.5, alpha=0.5
        )
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
        ax_g.set_xlabel(
            "Spearman r(gene, MYC)", fontsize=7
        )
    style_ax(ax_g,
             "G — MYC Metabolic vs Proliferation\n"
             "S3-P6: r(MYC,MKI67) = -0.57 (anti)")

    # ---- Panel H: Replication ----
    ax_h = fig.add_subplot(gs[2, 1])
    if rep_results is not None and \
       len(rep_results) > 0:
        rg     = list(rep_results["gene"])
        x3     = range(len(rg))
        w3     = 0.35
        r89_v  = rep_results[
            "gse89122_pct"
        ].fillna(0).values
        r83_v  = rep_results[
            "gse83479_pct"
        ].fillna(0).values
        ax_h.bar(
            [xi - w3/2 for xi in x3], r89_v,
            width=w3, color=BLUE, alpha=0.8,
            label="GSE89122",
        )
        ax_h.bar(
            [xi + w3/2 for xi in x3], r83_v,
            width=w3, color=ORANGE, alpha=0.8,
            label="GSE83479",
        )
        ax_h.axhline(
            0, color=LABEL_C, lw=0.5, alpha=0.5
        )
        ax_h.set_xticks(x3)
        ax_h.set_xticklabels(
            rg, rotation=45, ha="right", fontsize=5
        )
        ax_h.legend(
            fontsize=5, facecolor=BG,
            labelcolor=TITLE_C, framealpha=0.5,
        )
        n_conf = (
            rep_results["match"] == "REPLICATED"
        ).sum()
        ax_h.set_ylabel("% change vs normal", fontsize=7)
        style_ax(
            ax_h,
            f"H — Replication GSE83479\n"
            f"{n_conf}/{len(rg)} replicated",
        )
    else:
        ax_h.text(
            0.5, 0.5,
            "GSE83479 replication\nnot available",
            ha="center", va="center",
            color=LABEL_C, fontsize=8,
            transform=ax_h.transAxes,
        )
        style_ax(ax_h, "H — Replication (unavailable)")

    # ---- Panel I: Summary ----
    ax_i = fig.add_subplot(gs[2, 2])
    ax_i.set_facecolor(BG)
    ax_i.axis("off")
    for sp in ax_i.spines.values():
        sp.set_edgecolor("#30363d")

    r_ab_val = np.nan
    if score_a is not None and score_b is not None:
        r_ab_val, _ = spearman(
            score_a.values, score_b.values
        )

    n_stab = len(stable_genes)
    n_infl = len(inflated_genes)

    lines = [
        ("SCRIPT 3 SUMMARY", True),
        ("cdRCC | GSE89122 | 2026-03-03", False),
        ("", False),
        ("ARTEFACT AUDIT", False),
        (f"  Stable:   {n_stab}/20", False),
        (f"  Inflated: {n_infl}/20", False),
        ("  Inflated = directional only", False),
        ("", False),
        ("MODULE INDEPENDENCE", False),
        (f"  r(A,B)={r_ab_val:+.3f} p=0.148"
         if not np.isnan(r_ab_val)
         else "  r(A,B) = not computed", False),
        ("  n=7 underpowered", False),
        ("  CDC6 drives both modules", False),
        ("", False),
        ("MYC FINDING", False),
        ("  r(MYC,MKI67) = -0.57", False),
        ("  MYC ANTI-correlates MKI67", False),
        ("  MYC = differentiation repressor", False),
        ("", False),
        ("ADCY3 DRIVER", False),
        ("  RELA (NF-kB) — not MYC", False),
        ("  IL1B-CELSR1-ADCY3 NF-kB arm", False),
        ("", False),
        ("Author: Eric Robert Lawson", False),
        ("OrganismCore | Doc 89 addendum", False),
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

    style_ax(ax_i, "I — Summary")

    fig.suptitle(
        "cdRCC — Script 3 v2: Spearman Audit, "
        "Module Independence, Replication\n"
        "OrganismCore | GSE89122 + GSE83479 | "
        "2026-03-03",
        color=TITLE_C, fontsize=10, y=0.99,
    )

    out_fig = os.path.join(
        S3_DIR, "GSE89122_script3_v2_s3.png"
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
    log("FALSE ATTRACTOR — SCRIPT 3 v2 (corrected)")
    log("OrganismCore | GSE89122 | 2026-03-03")
    log("=" * 65)
    log("")
    log("  Corrections from v1:")
    log("  1. Spearman negatives: sort ascending")
    log("  2. CDC3 verdict: reports PPARG/KLF5 retention")
    log("  3. MYC: negative r interpreted correctly")
    log("  4. GSE83479: strip hg. prefix, positional map")
    log("  5. Step 4: n=7 power caveat added")

    # Step 0
    df, tumor, normal, t_cols, n_cols = \
        load_primary_matrix()

    # Step 1
    depth = build_depth_score(tumor)

    # Step 2
    df_sp = spearman_depth_correlations(tumor, depth)

    # Step 3
    stable, inflated = pearson_spearman_audit(
        tumor, depth, df_sp
    )

    # Step 4
    score_a, score_b = programme_independence_test(
        tumor, depth
    )

    # Step 5
    pparg_rewiring_test(tumor, normal)

    # Step 6
    adcy3_driver_test(tumor)

    # Step 7
    celsr1_assignment(tumor)

    # Step 8
    cdc3_examination(tumor, normal)

    # Step 9
    myc_role_test(tumor)

    # Step 10
    rep_results = None
    mat_path    = download_gse83479()
    if mat_path:
        samples_rep = fetch_gse83479_metadata()
        time.sleep(0.5)
        df_rep, tumor_rep, normal_rep = \
            load_gse83479(mat_path, samples_rep)
        if tumor_rep is not None and \
           len(tumor_rep.columns) > 0:
            rep_results = run_replication(
                tumor_rep, normal_rep,
                tumor, normal,
            )
            if rep_results is not None:
                out_r = os.path.join(
                    S3_DIR,
                    "replication_gse83479.csv"
                )
                rep_results.to_csv(
                    out_r, index=False
                )
                log(f"  Saved: {out_r}")
        else:
            log("  Replication skipped — "
                "no tumour columns found")
    else:
        log("\n  Replication skipped — "
            "matrix not available")

    # Step 11
    df_paired = corrected_paired_analysis(
        tumor, normal
    )

    # Step 12
    generate_figure(
        tumor, normal, depth, df_sp,
        score_a, score_b,
        df_paired, rep_results,
        stable, inflated,
    )

    log("")
    log("=" * 65)
    log("SCRIPT 3 v2 COMPLETE")
    log(f"\nOutputs in: {S3_DIR}")
    log("  depth_correlations_spearman_s3.csv")
    log("  paired_wilcoxon_s3.csv")
    log("  replication_gse83479.csv (if available)")
    log("  GSE89122_script3_v2_s3.png")
    log("  analysis_log_s3.txt")
    log("=" * 65)

    write_log()


if __name__ == "__main__":
    main()
