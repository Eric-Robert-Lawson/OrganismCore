"""
chRCC False Attractor — Script 1
NORMAL POLE · DEPTH SCORE · INITIAL CHARACTERISATION

Framework: OrganismCore
Document 96a | 2026-03-02
Author: Eric Robert Lawson

═══════════════════════════════════════════════════════════════
DATA SOURCE (from chrcc_data_builder_v2.py):
  GSE19982 — 15 chRCC + 15 oncocytoma (GPL570)
  GSE95425 — 53 normal kidney biopsies (GPL10558)
             23 cortex / 24 medulla / 6 cortex-medulla
  Combined: 15244 genes × 83 samples
  Rank-normalised microarray data

BARCODE FORMAT (from builder v2):
  TCGA-KI-{n:04d}-X{n:02d}-{code}{letter}-01-01
  Example: TCGA-KI-0001-X01-01A-01-01
  Split on '-' → parts[4] = code+letter
  parts[4][:2] = "01" → chRCC
  parts[4][:2] = "02" → oncocytoma
  parts[4][:2] = "11" → normal

STATISTICAL THRESHOLDS AT n=15 (chRCC tumours):
  |r| > 0.514  p < 0.05
  |r| > 0.641  p < 0.01
  |r| > 0.760  p < 0.001

═══════════════════════════════════════════════════════════════
PREDICTIONS LOCKED — 2026-03-02 — BEFORE ANALYSIS

  C1-P1:  ATP6V1B1 falls with depth
          r(ATP6V1B1, depth_tumour) < -0.30

  C1-P2:  FOXI1 falls with depth
          r(FOXI1, depth_tumour) < -0.30

  C1-P3:  KRT7 rises with depth
          r(KRT7, depth_tumour) > +0.20

  C1-P4:  EZH2 rises with depth
          r(EZH2, depth_tumour) > +0.20

  C1-P5:  OGDHL falls with depth
          r(OGDHL, depth_tumour) < -0.20

  C1-P6:  Depth score predicts OS
          logrank p < 0.05 (Q4 vs Q1)
          NOTE: OS unavailable in GEO data.
          DEFERRED.
═══════════════════════════════════════════════════════════════
"""

import os
import gzip
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.stats import pearsonr, mannwhitneyu
from scipy.linalg import svd
warnings.filterwarnings("ignore")

# ═══════════════════════════════════════════════════════════════
# PATHS
# ═══════════════════════════════════════════════════════════════

BASE_DIR    = "./chrcc_false_attractor/"
RESULTS_DIR = os.path.join(BASE_DIR, "results_s1/")
LOG_FILE    = os.path.join(RESULTS_DIR, "s1_log.txt")

KICH_EXPR   = os.path.join(BASE_DIR,
                             "TCGA_KICH_HiSeqV2.gz")
KICH_CLIN   = os.path.join(BASE_DIR,
                             "KICH_clinicalMatrix.tsv")
KICH_SURV   = os.path.join(BASE_DIR,
                             "KICH_survival.txt")

os.makedirs(RESULTS_DIR, exist_ok=True)

# ═══════════════════════════════════════════════════════════════
# PRCC FIXED REFERENCE (Documents 95a–95g)
# ═══════════════════════════════════════════════════════════════

PRCC_REF = {
    "KRT19":   +0.803, "SLC22A6": -0.801,
    "LAMC2":   +0.760, "KHK":     -0.746,
    "EZH2":    +0.308, "KDM1A":   +0.443,
    "RUNX1":   +0.590, "GOT1":    -0.519,
    "OGDHL":   -0.402, "FH":      -0.451,
    "MET":     +0.246, "ERBB2":   +0.360,
    "SLC7A9":  -0.720, "KITLG":   +0.690,
    "CDK4":    +0.118, "CDK2":    +0.289,
    "CDKN2A":  +0.036, "ARG1":    +0.076,
    "SLC16A1": -0.488, "LDHA":    +0.210,
    "CA9":     +0.125, "HAVCR2":  -0.396,
    "B2M":     -0.222, "FABP1":   -0.671,
    "MIOX":    -0.429, "SLC5A2":  -0.661,
    "SLC34A1": -0.637, "UMOD":    -0.591,
    "GPX3":    -0.412, "ACADM":   -0.412,
    "CUBN":    -0.397, "KIT":     +0.468,
    "TPSAB1":  +0.689, "HDC":     +0.627,
    "HRH1":    +0.630, "GPX4":    -0.319,
    "ACSL4":   +0.171, "MKI67":   -0.024,
    "TOP2A":   +0.083, "VHL":     +0.072,
    "EPAS1":   -0.082, "HIF1A":   -0.019,
    "PBRM1":   +0.240, "SETD2":   +0.308,
    "TET2":    +0.292, "PDK1":    +0.162,
    "SLC2A1":  +0.137, "KRT7":    +0.200,
    "FOXI1":   -0.050, "ATP6V1B1":-0.060,
    "SDHA":    -0.150, "SDHB":    -0.140,
    "PPARGC1A":-0.180, "ESRRA":   -0.120,
    "TP53":    +0.050, "PTEN":    -0.100,
    "CDK6":    +0.090, "RB1":     -0.080,
    "CCNE1":   +0.150, "CCND1":   +0.080,
}

# ═══════════════════════════════════════════════════════════════
# GENE PANELS
# ═══════════════════════════════════════════════════════════════

INTERCALATED = [
    "ATP6V1B1", "ATP6V0A4", "ATP6V1C2",
    "FOXI1",    "SLC4A1",   "SLC26A4",
    "AQP6",     "CA2",      "RHBG",
    "RHCG",     "KIT",      "SLC4A9",
    "CLCNKB",   "UMOD",
]

PROXIMAL = [
    "SLC22A6", "SLC34A1", "SLC5A2",
    "FABP1",   "CUBN",    "LRP2",
    "MIOX",    "GPX3",    "ACADM",
    "GOT1",    "OGDHL",   "FH",
    "KHK",     "SLC13A2",
]

BILIARY = [
    "KRT7",   "KRT19",  "KRT8",
    "KRT18",  "ERBB2",  "ERBB3",
    "MUC1",   "EPCAM",  "SOX4",
    "CLDN4",  "CLDN7",  "TACSTD2",
    "TFF1",   "TFF3",   "GPC1",
    "HNF1B",
]

INVASION = [
    "LAMC2",  "ITGB6",  "KITLG",
    "VIM",    "CDH2",   "FN1",
    "SNAI1",  "SNAI2",  "ACTA2",
    "COL1A1", "TGFB1",  "LOXL2",
]

MITO = [
    "SDHA",     "SDHB",     "SDHC",
    "SDHD",     "PPARGC1A", "PPARGC1B",
    "ESRRA",    "TFAM",     "NRF1",
    "TOMM20",   "COX5A",    "COX5B",
    "UQCRC1",   "TIMM23",
]

DRUG_TARGETS = [
    ("EZH2_inhibitor",     "EZH2"),
    ("KDM1A_inhibitor",    "KDM1A"),
    ("MET_inhibitor",      "MET"),
    ("ERBB2_TDXd",         "ERBB2"),
    ("CDK4_inhibitor",     "CDK4"),
    ("CDK2_inhibitor",     "CDK2"),
    ("CDK6_inhibitor",     "CDK6"),
    ("mTOR_inhibitor",     "MTOR"),
    ("PTEN_loss",          "PTEN"),
    ("TP53_proxy",         "TP53"),
    ("CA9_targeted",       "CA9"),
    ("PDL1_checkpoint",    "CD274"),
    ("HAVCR2_checkpoint",  "HAVCR2"),
    ("ARG1_inhibitor",     "ARG1"),
    ("PDK1_DCA",           "PDK1"),
    ("SLC16A1_MCT4",       "SLC16A1"),
    ("Ferroptosis_GPX4",   "GPX4"),
    ("Ferroptosis_SLC7A9", "SLC7A9"),
    ("HRH1_antihistamine", "HRH1"),
    ("KIT_imatinib",       "KIT"),
    ("CDKN2A_proxy",       "CDKN2A"),
    ("RB1_proxy",          "RB1"),
    ("SDHA_SDHi",          "SDHA"),
    ("PPARGC1A_mito",      "PPARGC1A"),
    ("EZH2_PBAF_synth",    "PBRM1"),
    ("SETD2_proxy",        "SETD2"),
    ("BAP1_proxy",         "BAP1"),
]

# ═══════════════════════════════════════════════════════════════
# LOGGING
# ═══════════════════════════════════════════════════════════════

log_lines = []

def log(msg=""):
    print(msg)
    log_lines.append(str(msg))

def write_log():
    with open(LOG_FILE, "w") as f:
        f.write("\n".join(log_lines))

def fmt_p(p, n=None):
    if p is None or (isinstance(p, float)
                     and np.isnan(p)):
        return "—"
    s = f" [n={n}]" if n else ""
    if p < 1e-10: return f"p<1e-10{s}"
    if p < 1e-05: return f"p={p:.2e}{s}"
    if p < 0.001: return f"p={p:.4f}{s}"
    return f"p={p:.4f}{s}"

def norm01(arr):
    a  = np.asarray(arr, float)
    mn = np.nanmin(a)
    mx = np.nanmax(a)
    if mx == mn: return np.zeros_like(a)
    return (a - mn) / (mx - mn)

def safe_r(x, y):
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    m = np.isfinite(x) & np.isfinite(y)
    if m.sum() < 5:
        return np.nan, np.nan
    return pearsonr(x[m], y[m])

def safe_mwu(a, b):
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    a = a[np.isfinite(a)]
    b = b[np.isfinite(b)]
    if len(a) < 3 or len(b) < 3:
        return np.nan, np.nan
    return mannwhitneyu(a, b,
                         alternative="two-sided")

def sig_flag(r, n):
    if np.isnan(r): return "    "
    if n >= 15:
        if abs(r) >= 0.760: return "★★★ "
        if abs(r) >= 0.641: return "★★  "
        if abs(r) >= 0.514: return "★   "
        if abs(r) >= 0.350: return "~   "
    return "    "

# ════════════════════════════════════════��══════════════════════
# BARCODE CLASSIFIER
# ═══════════════════════════════════════════════════════════════

def classify_barcode(bc):
    """
    Builder v2 barcode format:
    TCGA-KI-{n:04d}-X{n:02d}-{code}{letter}-01-01
    e.g. TCGA-KI-0001-X01-01A-01-01

    Split on '-':
    parts[0] = 'TCGA'
    parts[1] = 'KI'
    parts[2] = '0001'
    parts[3] = 'X01'
    parts[4] = '01A'   ← type code + letter
    parts[5] = '01'
    parts[6] = '01'

    Type codes:
      01x = chRCC
      02x = oncocytoma
      11x = normal (all subtypes)
      06x = unknown
    """
    parts = bc.split("-")
    if len(parts) < 5:
        return "unknown"
    code_field = parts[4]           # e.g. "01A"
    code       = code_field[:2]     # e.g. "01"
    if   code == "01": return "chRCC"
    elif code == "02": return "oncocytoma"
    elif code == "11": return "normal"
    else:              return "other"

def normal_zone(bc):
    """
    Extract normal zone from barcode letter:
      11G = cortex
      11H = medulla
      11I = cortex/medulla
    """
    parts = bc.split("-")
    if len(parts) < 5: return "other"
    code_field = parts[4]
    if len(code_field) < 3: return "other"
    letter = code_field[2]
    return {"G": "cortex",
             "H": "medulla",
             "I": "cortex/medulla"}\
           .get(letter, "other")

# ═══════════════════════════════════════════════════════════════
# OBJ-1: LOAD AND QC
# ═══════════════════════════════════════════════════════════════

def obj1_load_qc():
    log(""); log("="*60)
    log("OBJ-1 — LOAD AND QC")
    log("="*60)

    if not os.path.exists(KICH_EXPR):
        raise FileNotFoundError(
            f"{KICH_EXPR} not found. "
            f"Run chrcc_data_builder_v2.py first.")

    opener = (gzip.open
              if KICH_EXPR.endswith(".gz")
              else open)
    with opener(KICH_EXPR, "rt") as fh:
        raw = pd.read_csv(fh, sep="\t",
                          index_col=0)
    log(f"  Raw matrix: {raw.shape[0]} genes "
        f"× {raw.shape[1]} samples")

    # Print first 5 barcodes for debugging
    log(f"  Barcode examples (first 5):")
    for bc in list(raw.columns)[:5]:
        cls = classify_barcode(bc)
        log(f"    {bc}  →  {cls}")

    # Classify
    meta = pd.Series(
        {s: classify_barcode(s)
         for s in raw.columns})

    t_cols  = raw.columns[meta == "chRCC"]
    n_cols  = raw.columns[meta == "normal"]
    oc_cols = raw.columns[meta == "oncocytoma"]

    log(f"  chRCC:      n={len(t_cols)}")
    log(f"  Oncocytoma: n={len(oc_cols)}")
    log(f"  Normal:     n={len(n_cols)}")

    # If classification failed, try clinical file
    if len(t_cols) == 0:
        log("")
        log("  ⚠ Barcode classification returned "
            "0 tumours.")
        log("  Attempting clinical file fallback...")
        t_cols, n_cols, oc_cols = \
            _clin_fallback(raw)
        log(f"  After fallback: chRCC={len(t_cols)} "
            f"normal={len(n_cols)} "
            f"oncocytoma={len(oc_cols)}")

    if len(t_cols) == 0:
        # Last resort: print all barcodes
        log("  FATAL: Cannot classify samples.")
        log("  All barcodes in matrix:")
        for bc in raw.columns:
            log(f"    {bc}")
        raise ValueError(
            "No chRCC samples found. "
            "Check barcode format.")

    # Normal zone breakdown
    for z in ["cortex", "medulla",
               "cortex/medulla"]:
        n = sum(1 for s in n_cols
                if normal_zone(s) == z)
        log(f"    {z}: n={n}")

    n_t = len(t_cols)
    log(f"")
    log(f"  Statistical thresholds "
        f"at n_tumour={n_t}:")
    log(f"    |r| > 0.514  p < 0.05")
    log(f"    |r| > 0.641  p < 0.01")
    log(f"    |r| > 0.760  p < 0.001")

    # Key gene QC
    log("")
    log("  KEY GENE QC:")
    log(f"  {'Gene':<14} {'N_mean':>8} "
        f"{'T_mean':>8} {'Oc_mean':>8} "
        f"{'Status':>8}")
    log(f"  {'─'*54}")

    CHECK = (INTERCALATED[:5] +
             ["KRT7","EZH2","OGDHL",
              "KIT","TP53","PTEN"])
    for gene in CHECK:
        if gene not in raw.index:
            log(f"  {gene:<14} {'ABSENT':>38}")
            continue
        nm  = raw.loc[gene, n_cols].mean() \
              if len(n_cols) > 0 else np.nan
        tm  = raw.loc[gene, t_cols].mean() \
              if len(t_cols) > 0 else np.nan
        om  = raw.loc[gene, oc_cols].mean() \
              if len(oc_cols) > 0 else np.nan
        log(f"  {gene:<14} {nm:>8.3f} "
            f"{tm:>8.3f} {om:>8.3f} "
            f"{'✓':>8}")

    return raw, t_cols, n_cols, oc_cols

def _clin_fallback(raw):
    """
    Classify using clinical matrix file
    when barcode parsing fails.
    """
    if not os.path.exists(KICH_CLIN):
        return (raw.columns[:0],
                raw.columns[:0],
                raw.columns[:0])
    clin = pd.read_csv(KICH_CLIN,
                        sep="\t",
                        index_col=0)
    log(f"  Clinical file columns: "
        f"{list(clin.columns)}")

    # Match sample IDs — try index overlap
    common = [s for s in raw.columns
              if s in clin.index]
    log(f"  Samples matching clinical: "
        f"{len(common)}/{len(raw.columns)}")

    if len(common) == 0:
        # Try partial match on GSM ID
        gsm_map = {}
        for bc in raw.columns:
            gsm = bc.split("_")[-1] \
                if "_" in bc else bc
            gsm_map[bc] = gsm
        common = []
        for bc in raw.columns:
            gsm = gsm_map[bc]
            if gsm in clin.index:
                common.append(bc)
        log(f"  After GSM partial match: "
            f"{len(common)}")

    if len(common) == 0:
        return (raw.columns[:0],
                raw.columns[:0],
                raw.columns[:0])

    # Find class column
    cls_col = None
    for c in ["class", "tumor_type",
               "is_chRCC", "Class",
               "sample_type"]:
        if c in clin.columns:
            cls_col = c
            break

    if cls_col is None:
        log(f"  No class column found. "
            f"Columns: {list(clin.columns)}")
        return (raw.columns[:0],
                raw.columns[:0],
                raw.columns[:0])

    t_cols  = [s for s in common
               if str(clin.at[s, cls_col])
               in ["chRCC","1","True","tumor"]]
    n_cols  = [s for s in common
               if str(clin.at[s, cls_col])
               .startswith("normal")]
    oc_cols = [s for s in common
               if "onco" in str(
                   clin.at[s, cls_col]).lower()]

    return (pd.Index(t_cols),
            pd.Index(n_cols),
            pd.Index(oc_cols))

# ═══════════════════════════════════════════════════════════════
# OBJ-2: DEPTH SCORE
# ═══════════════════════════════════════════════════════════════

def obj2_depth_score(raw, t_cols, n_cols,
                      oc_cols):
    log(""); log("="*60)
    log("OBJ-2 — DEPTH SCORE")
    log("="*60)

    all_cols = (list(t_cols) +
                list(n_cols) +
                list(oc_cols))
    sub = raw[all_cols].copy()

    # Expression filter
    mean_expr = sub.mean(axis=1)
    sub = sub[mean_expr > 0.05]
    log(f"  Genes after expression filter "
        f"(mean>0.05): {sub.shape[0]}")

    if sub.shape[0] < 100:
        log("  ⚠ Too few genes after filter — "
            "relaxing to mean>0.01")
        sub = raw[all_cols].copy()
        sub = sub[sub.mean(axis=1) > 0.01]
        log(f"  Genes after relaxed filter: "
            f"{sub.shape[0]}")

    if sub.shape[0] < 50:
        log("  ⚠ Still too few genes — "
            "using all genes with any data")
        sub = raw[all_cols].copy()
        sub = sub.dropna(how="all")
        log(f"  Genes (no filter): "
            f"{sub.shape[0]}")

    # Variance filter top 5000
    gene_var  = sub.var(axis=1)
    n_top     = min(5000, len(gene_var))
    top_genes = gene_var.nlargest(n_top).index
    sub       = sub.loc[top_genes]
    log(f"  Using top {n_top} variable genes")
    log(f"  Matrix for SVD: {sub.shape}")

    # Standardise per gene
    gene_std = sub.std(axis=1).replace(0, 1)
    sub_z = sub.subtract(
        sub.mean(axis=1), axis=0
    ).divide(gene_std, axis=0)

    # Fill any remaining NaN with 0
    sub_z = sub_z.fillna(0)

    # SVD
    mat = sub_z.values.T  # samples × genes
    log(f"  SVD input: {mat.shape}")
    U, S, Vt = svd(mat, full_matrices=False)

    pc1 = pd.Series(U[:, 0] * S[0],
                     index=all_cols)

    # Orient: tumour > normal
    n_mean = pc1[list(n_cols)].mean()
    t_mean = pc1[list(t_cols)].mean()
    if n_mean > t_mean:
        pc1 = -pc1
        log("  PC1 flipped (tumour > normal)")
    else:
        log("  PC1 orientation correct")

    var_exp = S[0]**2 / np.sum(S**2)
    log(f"  PC1 variance explained: "
        f"{100*var_exp:.1f}%")

    depth_all = pd.Series(
        norm01(pc1.values),
        index=all_cols,
        name="depth")

    depth_t  = depth_all.reindex(t_cols)
    depth_n  = depth_all.reindex(n_cols)
    depth_oc = depth_all.reindex(oc_cols)

    log(f"  Normal depth:     "
        f"mean={depth_n.mean():.3f}  "
        f"std={depth_n.std():.3f}")
    log(f"  chRCC depth:      "
        f"mean={depth_t.mean():.3f}  "
        f"std={depth_t.std():.3f}")
    if len(depth_oc) > 0:
        log(f"  Oncocytoma depth: "
            f"mean={depth_oc.mean():.3f}  "
            f"std={depth_oc.std():.3f}")

    _, p_mwu = safe_mwu(depth_t.values,
                         depth_n.values)
    log(f"  MW chRCC > normal: {fmt_p(p_mwu)}")
    if not np.isnan(p_mwu) and p_mwu < 0.05:
        log("  Depth score validated ✓")
    else:
        log("  NOTE: depth separation weak — "
            "proceeding (small n expected)")

    if len(oc_cols) > 0:
        _, p_oc = safe_mwu(
            depth_oc.values, depth_n.values)
        _, p_ct = safe_mwu(
            depth_t.values, depth_oc.values)
        log(f"  MW oncocytoma > normal: "
            f"{fmt_p(p_oc)}")
        log(f"  MW chRCC > oncocytoma:  "
            f"{fmt_p(p_ct)}")

    # Save
    rows = (
        [(s, depth_t[s], "chRCC")
         for s in t_cols] +
        [(s, depth_n[s], "normal")
         for s in n_cols] +
        [(s, depth_oc[s], "oncocytoma")
         for s in oc_cols]
    )
    pd.DataFrame(rows,
                  columns=["sample_id",
                            "depth",
                            "class"])\
      .to_csv(os.path.join(
                  RESULTS_DIR,
                  "depth_scores.csv"),
              index=False)
    log("  Saved: depth_scores.csv")

    return depth_t, depth_n, depth_oc

# ═══════════════════════════════════════════════════════════════
# OBJ-3: NORMAL POLE PANEL
# ═══════════════════════════════════════════════════════════════

def obj3_normal_pole(raw, t_cols, n_cols,
                      depth_t):
    log(""); log("="*60)
    log("OBJ-3 — NORMAL POLE PANEL")
    log("="*60)

    panels = [
        ("INTERCALATED", INTERCALATED),
        ("PROXIMAL",      PROXIMAL),
        ("BILIARY",       BILIARY),
    ]

    all_rows = []
    for pname, genes in panels:
        log(f"\n  {pname}:")
        log(f"  {'Gene':<14} "
            f"{'N_mean':>8} {'T_mean':>8} "
            f"{'T<N':>5} {'r':>8} "
            f"{'sig':>5} {'p':>12}")
        log(f"  {'─'*60}")

        for gene in genes:
            if gene not in raw.index:
                log(f"  {gene:<14} ABSENT")
                continue
            nm = raw.loc[gene, n_cols].mean()
            tm = raw.loc[gene, t_cols].mean()
            tl = "Y" if tm < nm else "N"

            g_ = raw.loc[gene, t_cols]\
                   .reindex(depth_t.index)
            r, p = safe_r(g_.values,
                           depth_t.values)
            fl = sig_flag(r,
                           len(depth_t))
            p_str = fmt_p(p, len(depth_t))
            log(f"  {gene:<14} "
                f"{nm:>8.3f} {tm:>8.3f} "
                f"{tl:>5} {r:>+8.4f} "
                f"{fl:>5} {p_str:>12}")

            all_rows.append({
                "panel":    pname,
                "gene":     gene,
                "n_mean":   nm,
                "t_mean":   tm,
                "T_less_N": tl == "Y",
                "r_depth":  r,
                "p_depth":  p,
                "sig":      fl.strip(),
            })

    df = pd.DataFrame(all_rows)
    df.to_csv(
        os.path.join(RESULTS_DIR,
                     "normal_pole_panel.csv"),
        index=False)

    # C1-P1, C1-P2 checks
    log("")
    for gene, pred, thr in [
        ("ATP6V1B1", "C1-P1", -0.30),
        ("FOXI1",    "C1-P2", -0.30),
    ]:
        row = df[df.gene == gene]
        if len(row) == 0:
            log(f"  {pred} ({gene}): ABSENT")
            continue
        r = row.iloc[0]["r_depth"]
        if not np.isnan(r) and r < thr:
            log(f"  {pred} {gene} "
                f"r={r:+.4f}  CONFIRMED ✓")
        else:
            log(f"  {pred} {gene} "
                f"r={r:+.4f}  NOT CONFIRMED ✗")

    return df

# ═══════════════════════════════════════════════════════════════
# OBJ-4: ATTRACTOR GENES
# ═══════════════════════════════════════════════════════════════

def obj4_attractor_genes(raw, t_cols, n_cols,
                          depth_t):
    log(""); log("="*60)
    log("OBJ-4 — ATTRACTOR POLE GENES")
    log("="*60)
    log(f"  n_tumour = {len(t_cols)}  "
        f"|r|>0.514 for p<0.05")

    d = depth_t.dropna()

    avail = [g for g in raw.index
             if raw.loc[g, t_cols].mean() > 0.05]
    log(f"  Expressed genes: {len(avail)}")

    results = []
    for gene in avail:
        g_ = raw.loc[gene, t_cols]\
               .reindex(d.index)
        r, p = safe_r(g_.values, d.values)
        nm   = raw.loc[gene, n_cols].mean()
        tm   = raw.loc[gene, t_cols].mean()
        results.append({
            "gene":    gene,
            "r_depth": r,
            "p_depth": p,
            "n_mean":  nm,
            "t_mean":  tm,
        })

    df = pd.DataFrame(results)\
           .dropna(subset=["r_depth"])\
           .sort_values("r_depth",
                         key=abs,
                         ascending=False)

    top_pos = df[df.r_depth > 0].head(30)
    top_neg = df[df.r_depth < 0].head(30)

    log("")
    log("  TOP 30 POSITIVE (acquired):")
    log(f"  {'#':>3} {'Gene':<14} "
        f"{'r':>9} {'sig':>5} "
        f"{'N_mean':>8} {'T_mean':>8}")
    log(f"  {'─'*52}")
    for i, (_, row) in enumerate(
            top_pos.iterrows(), 1):
        fl = sig_flag(row.r_depth, len(d))
        log(f"  {i:>3}. {row.gene:<14} "
            f"{row.r_depth:>+9.4f} "
            f"{fl.strip():>5} "
            f"{row.n_mean:>8.3f} "
            f"{row.t_mean:>8.3f}")

    log("")
    log("  TOP 30 NEGATIVE (lost):")
    log(f"  {'#':>3} {'Gene':<14} "
        f"{'r':>9} {'sig':>5} "
        f"{'N_mean':>8} {'T_mean':>8}")
    log(f"  {'─'*52}")
    for i, (_, row) in enumerate(
            top_neg.iterrows(), 1):
        fl = sig_flag(row.r_depth, len(d))
        log(f"  {i:>3}. {row.gene:<14} "
            f"{row.r_depth:>+9.4f} "
            f"{fl.strip():>5} "
            f"{row.n_mean:>8.3f} "
            f"{row.t_mean:>8.3f}")

    # Hypothesis panel
    log("")
    log("  ATTRACTOR IDENTITY HYPOTHESIS PANEL:")
    hyps = [
        ("BILIARY/DUCTAL",   BILIARY),
        ("INVASION/EMT",     INVASION),
        ("MITOCHONDRIAL",    MITO),
        ("INTERCALATED",     INTERCALATED),
        ("PROXIMAL_TUBULE",  PROXIMAL),
    ]
    panel_scores = {}
    for hyp, genes in hyps:
        av  = [g for g in genes
               if g in df.gene.values]
        if not av: continue
        sub = df[df.gene.isin(av)]
        mean_r = sub.r_depth.mean()
        n_sig_pos = (sub.r_depth > 0.514).sum()
        n_sig_neg = (sub.r_depth < -0.514).sum()
        panel_scores[hyp] = mean_r
        log(f"  {hyp:<24} "
            f"mean_r={mean_r:>+8.4f}  "
            f"sig_pos={n_sig_pos}  "
            f"sig_neg={n_sig_neg}  "
            f"({len(av)} genes)")

    if panel_scores:
        dom = max(panel_scores,
                  key=lambda k:
                  panel_scores[k])
        log(f"\n  DOMINANT ACQUIRED IDENTITY: "
            f"{dom} "
            f"(mean_r={panel_scores[dom]:+.4f})")

    # C1-P3, C1-P4, C1-P5
    log("")
    for gene, pred, thr, dirn in [
        ("KRT7",  "C1-P3", +0.20, "pos"),
        ("EZH2",  "C1-P4", +0.20, "pos"),
        ("OGDHL", "C1-P5", -0.20, "neg"),
    ]:
        row = df[df.gene == gene]
        if len(row) == 0:
            log(f"  {pred} ({gene}): ABSENT")
            continue
        r  = row.iloc[0]["r_depth"]
        ok = ((dirn=="pos" and r > thr) or
              (dirn=="neg" and r < thr))
        fl = sig_flag(r, len(d))
        log(f"  {pred} {gene} r={r:+.4f} "
            f"{fl.strip()}  "
            f"{'CONFIRMED ✓' if ok else 'NOT CONFIRMED ✗'}")

    df.to_csv(
        os.path.join(RESULTS_DIR,
                     "attractor_gene_panel.csv"),
        index=False)
    log(f"\n  Saved: attractor_gene_panel.csv "
        f"({len(df)} genes)")

    return df, panel_scores

# ═══════════════════════════════════════════════════════════════
# OBJ-5: CROSS-CANCER
# ═══════════════════════════════════════════════════════════════

def obj5_cross_cancer(raw, t_cols, depth_t,
                       df_all):
    log(""); log("="*60)
    log("OBJ-5 — CROSS-CANCER COMPARISON")
    log("="*60)

    d    = depth_t.dropna()
    rows = []

    log(f"\n  {'Gene':<14} {'chRCC_r':>9} "
        f"{'PRCC_r':>9} {'delta':>8} "
        f"{'pattern':<20}")
    log(f"  {'─'*64}")

    for gene in sorted(PRCC_REF.keys()):
        r_ref = PRCC_REF[gene]
        row   = df_all[df_all.gene == gene]
        if len(row) == 0:
            r_ch, p_ch = np.nan, np.nan
        else:
            r_ch = row.iloc[0]["r_depth"]
            p_ch = row.iloc[0]["p_depth"]

        delta = r_ch - r_ref \
            if not np.isnan(r_ch) else np.nan

        pattern = ""
        if not np.isnan(r_ch):
            if   r_ch >  0.20 and r_ref >  0.20:
                pattern = "SHARED_ATTRACTOR"
            elif r_ch < -0.20 and r_ref < -0.20:
                pattern = "SHARED_NORMAL"
            elif abs(r_ch) > 0.20 and \
                    abs(r_ref) < 0.20:
                pattern = "chRCC_SPECIFIC"
            elif abs(r_ch) < 0.20 and \
                    abs(r_ref) > 0.20:
                pattern = "PRCC_SPECIFIC"
            elif r_ch >  0.20 and r_ref < -0.20:
                pattern = "DIVERGENT(+/-)"
            elif r_ch < -0.20 and r_ref >  0.20:
                pattern = "DIVERGENT(-/+)"
            else:
                pattern = "WEAK_BOTH"

        r_str = f"{r_ch:>+9.4f}" \
            if not np.isnan(r_ch) else \
            f"{'N/A':>9}"
        d_str = f"{delta:>+8.4f}" \
            if not np.isnan(delta) else \
            f"{'N/A':>8}"
        log(f"  {gene:<14} {r_str} "
            f"{r_ref:>+9.4f} {d_str} "
            f"{pattern:<20}")

        rows.append({
            "gene":    gene,
            "r_chRCC": r_ch,
            "p_chRCC": p_ch,
            "r_PRCC":  r_ref,
            "delta":   delta,
            "pattern": pattern,
        })

    df_cc = pd.DataFrame(rows)

    log("\n  PATTERN SUMMARY:")
    for pat in ["SHARED_ATTRACTOR",
                "SHARED_NORMAL",
                "chRCC_SPECIFIC",
                "PRCC_SPECIFIC",
                "DIVERGENT(+/-)",
                "DIVERGENT(-/+)",
                "WEAK_BOTH"]:
        sub = df_cc[df_cc.pattern == pat]
        if len(sub) > 0:
            gs = sub.gene.tolist()
            log(f"  {pat:<22} n={len(sub)}  "
                f"{gs[:6]}")

    df_cc.to_csv(
        os.path.join(RESULTS_DIR,
                     "cross_cancer_panel.csv"),
        index=False)
    return df_cc

# ═══════════════════════════════════════════════════════════════
# OBJ-6: DRUG TARGETS
# ═══════════════════════════════════════════════════════════════

def obj6_drug_targets(raw, t_cols, n_cols,
                       depth_t, df_all):
    log(""); log("="*60)
    log("OBJ-6 — DRUG TARGET PANEL")
    log("="*60)
    log("  OS DEFERRED (no GEO survival data)")

    d    = depth_t.dropna()
    rows = []

    log(f"\n  {'Drug':<28} {'Gene':<12} "
        f"{'r':>9} {'sig':>5} "
        f"{'N_mean':>8} {'T_mean':>8}")
    log(f"  {'─'*74}")

    for drug, gene in DRUG_TARGETS:
        if gene not in raw.index:
            log(f"  {drug:<28} {gene:<12} ABSENT")
            continue
        row = df_all[df_all.gene == gene]
        r   = row.iloc[0]["r_depth"] \
            if len(row) > 0 else np.nan
        p   = row.iloc[0]["p_depth"] \
            if len(row) > 0 else np.nan
        nm  = raw.loc[gene, n_cols].mean()
        tm  = raw.loc[gene, t_cols].mean()
        fl  = sig_flag(r, len(d))
        log(f"  {drug:<28} {gene:<12} "
            f"{r:>+9.4f} {fl.strip():>5} "
            f"{nm:>8.3f} {tm:>8.3f}")
        rows.append({
            "drug":    drug,
            "gene":    gene,
            "r_depth": r,
            "p_depth": p,
            "n_mean":  nm,
            "t_mean":  tm,
        })

    df_dt = pd.DataFrame(rows)
    df_dt.to_csv(
        os.path.join(RESULTS_DIR,
                     "drug_target_panel.csv"),
        index=False)
    log(f"\n  Saved: drug_target_panel.csv")
    return df_dt

# ═══════════════════════════════════════════════════════════════
# OBJ-7: TRANSITION INDEX
# ═══════════════════════════════════════════════════════════════

def obj7_transition_index(raw, t_cols,
                           depth_t, df_all):
    log(""); log("="*60)
    log("OBJ-7 — TRANSITION INDEX")
    log("="*60)

    d = depth_t.dropna()

    sig_pos = df_all[
        (df_all.r_depth > 0) &
        (df_all.p_depth < 0.10) &
        (~df_all.gene.str.startswith("MT-"))
    ].head(10)
    sig_neg = df_all[
        (df_all.r_depth < 0) &
        (df_all.p_depth < 0.10) &
        (~df_all.gene.str.startswith("MT-"))
    ].head(10)

    pos_gene = sig_pos.iloc[0]["gene"] \
        if len(sig_pos) > 0 else None
    neg_gene = sig_neg.iloc[0]["gene"] \
        if len(sig_neg) > 0 else None

    log(f"  TI positive pole: {pos_gene}")
    log(f"  TI negative pole: {neg_gene}")

    if pos_gene is None or neg_gene is None:
        log("  TI not built — insufficient "
            "significant genes at p<0.10")
        return None

    pv = raw.loc[pos_gene, t_cols]\
           .reindex(d.index)
    nv = raw.loc[neg_gene, t_cols]\
           .reindex(d.index)

    ti = pd.Series(
        norm01(pv.values) - norm01(nv.values),
        index=d.index,
        name="TI")

    r_ti, p_ti = safe_r(ti.values, d.values)
    log(f"  TI r(depth) = {r_ti:+.4f} "
        f"{fmt_p(p_ti, len(d))}")

    pd.DataFrame({
        "sample_id": ti.index,
        "TI":        ti.values,
    }).to_csv(
        os.path.join(RESULTS_DIR,
                     "transition_index.csv"),
        index=False)
    log("  Saved: transition_index.csv")

    return ti

# ═══════════════════════════════════════════════════════════════
# OBJ-8: FIGURE
# ═══════════════════════════════════════════════════════════════

def obj8_figure(raw, t_cols, n_cols, oc_cols,
                depth_t, depth_n, depth_oc,
                df_normal, df_all, df_cc,
                df_dt, ti, panel_scores):
    log(""); log("="*60)
    log("OBJ-8 — FIGURE")
    log("="*60)

    C = {
        "chRCC": "#8E44AD",
        "norm":  "#27AE60",
        "onco":  "#E67E22",
        "att":   "#E74C3C",
        "np":    "#3498DB",
    }

    fig = plt.figure(figsize=(26, 28))
    gs  = gridspec.GridSpec(
        4, 3, figure=fig,
        hspace=0.52, wspace=0.40)

    # ── A: Depth distribution ────────────────
    ax = fig.add_subplot(gs[0, 0])
    bins = np.linspace(0, 1, 20)
    ax.hist(depth_t.dropna().values,
            bins=bins, alpha=0.75,
            color=C["chRCC"],
            label=f"chRCC (n={len(depth_t)})",
            density=True)
    ax.hist(depth_n.dropna().values,
            bins=bins, alpha=0.75,
            color=C["norm"],
            label=f"Normal (n={len(depth_n)})",
            density=True)
    if len(depth_oc) > 0:
        ax.hist(depth_oc.dropna().values,
                bins=bins, alpha=0.75,
                color=C["onco"],
                label=f"Onco (n={len(depth_oc)})",
                density=True)
    ax.set_xlabel("Depth Score")
    ax.set_ylabel("Density")
    ax.legend(fontsize=7)
    ax.set_title(
        "A: Depth Distribution",
        fontsize=9, fontweight="bold")

    # ── B: Intercalated panel ────────────────
    ax = fig.add_subplot(gs[0, 1])
    ic = df_normal[
        df_normal.panel == "INTERCALATED"
    ].dropna(subset=["r_depth"])\
     .sort_values("r_depth")
    if len(ic) > 0:
        colors = [C["np"] if v < 0
                  else C["att"]
                  for v in ic.r_depth]
        ax.barh(range(len(ic)),
                ic.r_depth.values,
                color=colors, alpha=0.8)
        ax.set_yticks(range(len(ic)))
        ax.set_yticklabels(ic.gene.values,
                            fontsize=7)
        ax.axvline(0, color="k", lw=0.8)
        ax.axvline(-0.514, color="k",
                    lw=0.6, ls="--",
                    alpha=0.5)
        ax.axvline(+0.514, color="k",
                    lw=0.6, ls="--",
                    alpha=0.5,
                    label="p<0.05 (n=15)")
        ax.legend(fontsize=6)
        ax.set_xlabel("r(depth)")
    ax.set_title(
        "B: Intercalated Cell Markers",
        fontsize=9, fontweight="bold")

    # ── C: Top attractor genes ───────────────
    ax = fig.add_subplot(gs[0, 2])
    top20 = df_all[
        ~df_all.gene.str.startswith("MT-")
    ].head(20)
    colors = [C["att"] if v > 0
              else C["np"]
              for v in top20.r_depth]
    ypos = range(len(top20))
    ax.barh(list(ypos)[::-1],
            top20.r_depth.values,
            color=colors, alpha=0.8)
    ax.set_yticks(list(ypos))
    ax.set_yticklabels(
        top20.gene.values[::-1], fontsize=7)
    ax.axvline(0, color="k", lw=0.8)
    ax.axvline( 0.514, color="k",
                lw=0.6, ls="--", alpha=0.5)
    ax.axvline(-0.514, color="k",
                lw=0.6, ls="--", alpha=0.5)
    ax.set_xlabel("r(depth)")
    ax.set_title(
        "C: Top Depth Correlates",
        fontsize=9, fontweight="bold")

    # ── D: Hypothesis scores ─────────────────
    ax = fig.add_subplot(gs[1, 0])
    if panel_scores:
        names  = list(panel_scores.keys())
        vals   = [panel_scores[h]
                  for h in names]
        cols_d = [C["att"] if v > 0
                  else C["np"]
                  for v in vals]
        ax.barh(range(len(names)), vals,
                color=cols_d, alpha=0.8)
        ax.set_yticks(range(len(names)))
        ax.set_yticklabels(names, fontsize=8)
        ax.axvline(0, color="k", lw=0.8)
        ax.set_xlabel("Mean r(depth)")
    ax.set_title(
        "D: Attractor Identity Scores",
        fontsize=9, fontweight="bold")

    # ── E: Drug targets ──────────────────────
    ax = fig.add_subplot(gs[1, 1])
    dt_sub = df_dt.dropna(
        subset=["r_depth"])\
        .sort_values("r_depth",
                      key=abs,
                      ascending=False).head(20)
    if len(dt_sub) > 0:
        col_e = [C["att"] if v > 0
                 else C["np"]
                 for v in dt_sub.r_depth]
        ax.barh(range(len(dt_sub)),
                dt_sub.r_depth.values,
                color=col_e, alpha=0.8)
        ax.set_yticks(range(len(dt_sub)))
        ax.set_yticklabels(dt_sub.drug.values,
                            fontsize=6)
        ax.axvline(0, color="k", lw=0.8)
        ax.axvline( 0.514, color="k",
                    lw=0.5, ls="--", alpha=0.4)
        ax.axvline(-0.514, color="k",
                    lw=0.5, ls="--", alpha=0.4)
        ax.set_xlabel("r(depth)")
    ax.set_title(
        "E: Drug Target Correlates\n"
        "(OS deferred)",
        fontsize=9, fontweight="bold")

    # ── F: Cross-cancer scatter ──────────────
    ax = fig.add_subplot(gs[1, 2])
    cc = df_cc.dropna(subset=["r_chRCC",
                                "r_PRCC"])
    cmap = {
        "SHARED_ATTRACTOR": C["att"],
        "SHARED_NORMAL":    C["np"],
        "chRCC_SPECIFIC":   C["chRCC"],
        "PRCC_SPECIFIC":    "#95A5A6",
        "DIVERGENT(+/-)":   "#E74C3C",
        "DIVERGENT(-/+)":   "#E74C3C",
        "WEAK_BOTH":        "#BDC3C7",
    }
    for _, row in cc.iterrows():
        col = cmap.get(row.pattern,
                        "#BDC3C7")
        ax.scatter(row.r_PRCC, row.r_chRCC,
                   c=col, s=25, alpha=0.8,
                   zorder=3)
        if abs(row.r_chRCC) > 0.35 or \
                abs(row.r_PRCC) > 0.50:
            ax.annotate(
                row.gene,
                (row.r_PRCC, row.r_chRCC),
                fontsize=5,
                xytext=(3, 3),
                textcoords="offset points")
    for v in [-0.514, 0.514]:
        ax.axhline(v, color="k", lw=0.4,
                    ls="--", alpha=0.3)
        ax.axvline(v, color="k", lw=0.4,
                    ls="--", alpha=0.3)
    ax.axhline(0, color="k", lw=0.5)
    ax.axvline(0, color="k", lw=0.5)
    ax.set_xlabel("r PRCC (n=290)",
                   fontsize=8)
    ax.set_ylabel("r chRCC (n=15)",
                   fontsize=8)
    ax.set_title(
        "F: chRCC vs PRCC Depth Axis",
        fontsize=9, fontweight="bold")
    for lab, col in [
        ("SHARED_ATT", C["att"]),
        ("SHARED_NORM", C["np"]),
        ("chRCC_SPEC", C["chRCC"]),
    ]:
        ax.scatter([], [], c=col,
                   s=20, label=lab)
    ax.legend(fontsize=6)

    # ── G: TI vs depth ───────────────────────
    ax = fig.add_subplot(gs[2, 0])
    if ti is not None:
        d_al = depth_t.reindex(ti.index)
        ax.scatter(d_al.values, ti.values,
                   c=C["chRCC"], s=30,
                   alpha=0.7, zorder=3)
        r_ti, _ = safe_r(d_al.values,
                          ti.values)
        ax.set_xlabel("Depth Score")
        ax.set_ylabel("Transition Index")
        ax.set_title(
            f"G: TI vs Depth  r={r_ti:+.3f}",
            fontsize=9, fontweight="bold")
    else:
        ax.set_title("G: TI not built",
                     fontsize=9)
        ax.axis("off")

    # ── H: Mitochondrial panel ───────────────
    ax = fig.add_subplot(gs[2, 1])
    mrows = []
    for gene in MITO:
        if gene not in raw.index: continue
        row = df_all[df_all.gene == gene]
        if len(row) == 0: continue
        mrows.append({
            "gene": gene,
            "r":    row.iloc[0]["r_depth"],
        })
    if mrows:
        mdf = pd.DataFrame(mrows)\
                .dropna(subset=["r"])\
                .sort_values("r")
        col_m = [C["att"] if v > 0
                 else C["np"]
                 for v in mdf.r]
        ax.barh(range(len(mdf)),
                mdf.r.values,
                color=col_m, alpha=0.8)
        ax.set_yticks(range(len(mdf)))
        ax.set_yticklabels(mdf.gene.values,
                            fontsize=7)
        ax.axvline(0, color="k", lw=0.8)
        ax.axvline( 0.514, color="k",
                    lw=0.5, ls="--", alpha=0.4)
        ax.axvline(-0.514, color="k",
                    lw=0.5, ls="--", alpha=0.4)
        ax.set_xlabel("r(depth)")
    ax.set_title(
        "H: Mitochondrial Programme",
        fontsize=9, fontweight="bold")

    # ── I: Scorecard ─────────────────────────
    ax = fig.add_subplot(gs[2, 2])
    ax.axis("off")

    full_log = "\n".join(log_lines)

    pred_checks = []
    for code in ["C1-P1","C1-P2","C1-P3",
                  "C1-P4","C1-P5"]:
        lines = [l for l in log_lines
                 if code in l]
        if not lines:
            pred_checks.append(
                f"{code}  ?")
            continue
        last = lines[-1]
        if "CONFIRMED ✓" in last:
            pred_checks.append(
                f"{code}  CONFIRMED ✓")
        elif "NOT CONFIRMED" in last:
            pred_checks.append(
                f"{code}  NOT CONFIRMED ✗")
        else:
            pred_checks.append(
                f"{code}  {last[-20:].strip()}")
    pred_checks.append("C1-P6  DEFERRED")

    n_conf = sum(1 for l in pred_checks
                 if "✓" in l)
    dom    = max(panel_scores,
                 key=lambda k:
                 panel_scores[k]) \
        if panel_scores else "UNKNOWN"

    txt = (
        "chRCC False Attractor — Script 1\n"
        "OrganismCore | Doc 96a | 2026-03-02\n"
        "══════════════════════════════════\n"
        + "\n".join(pred_checks) +
        f"\n\nOVERALL: {n_conf}/5 "
        f"(+1 deferred)\n"
        "══════════════════════════════════\n"
        f"n_chRCC:   {len(t_cols)}\n"
        f"n_normal:  {len(n_cols)}\n"
        f"n_oncocyt: {len(oc_cols)}\n"
        f"Genes:     {len(df_all)}\n"
        "r>0.514 ⟹ p<0.05 (n=15)\n"
        "══════════════════════════════════\n"
        "ORIGIN:  Intercalated cell\n"
        f"DOMINANT: {dom}\n"
    )
    ax.text(
        0.03, 0.97, txt,
        transform=ax.transAxes,
        fontsize=6.5, va="top",
        fontfamily="monospace",
        bbox=dict(boxstyle="round",
                  facecolor="#F0F4F8",
                  alpha=0.9))
    ax.set_title("I: Scorecard",
                 fontsize=9, fontweight="bold")

    # ── J: Geometry row ──────────────────────
    ax = fig.add_subplot(gs[3, :])
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3.5)
    ax.axis("off")
    ax.set_title(
        "J: chRCC False Attractor Geometry",
        fontsize=11, fontweight="bold", pad=8)

    dom_short = dom[:12] \
        if panel_scores else "UNKNOWN"

    for cx, cy, r, col, title, lines in [
        (1.5, 1.8, 0.75, C["norm"],
         "NORMAL IC CELL",
         ["ATP6V1B1 ▲",
          "FOXI1 ▲",
          "SLC4A1 ▲"]),
        (5.0, 2.2, 1.0, C["chRCC"],
         "chRCC ATTRACTOR",
         [f"Identity: {dom_short}",
          "EZH2 ▲",
          "RUNX1 ▲"]),
        (8.5, 1.8, 0.65, C["onco"],
         "ONCOCYTOMA",
         ["Benign",
          "IC origin"]),
    ]:
        ax.add_patch(plt.Circle(
            (cx, cy), r,
            color=col, alpha=0.12))
        ax.add_patch(plt.Circle(
            (cx, cy), r,
            color=col, fill=False, lw=2))
        ax.text(cx, cy+r+0.10, title,
                ha="center", va="bottom",
                fontsize=8, fontweight="bold",
                color=col)
        for i, line in enumerate(lines):
            ax.text(cx,
                    cy + 0.2 - i*0.22,
                    line,
                    ha="center", va="center",
                    fontsize=6.5)

    ax.annotate(
        "", xy=(3.95, 2.2),
        xytext=(2.25, 1.95),
        arrowprops=dict(arrowstyle="->",
                         color=C["chRCC"],
                         lw=1.8))
    ax.annotate(
        "", xy=(7.82, 1.9),
        xytext=(5.95, 2.1),
        arrowprops=dict(arrowstyle="->",
                         color=C["onco"],
                         lw=1.2, ls="dashed"))
    ax.text(3.0, 2.55,
            "False attractor transition",
            fontsize=7.5, style="italic",
            color=C["chRCC"], ha="center")
    ax.text(5.0, 0.35,
            "SHARED AXIS (chRCC + PRCC + ccRCC): "
            "TCA↓ → αKG↓ → EZH2▲ → "
            "chromatin lock | RUNX1▲ | KDM1A▲",
            ha="center", fontsize=7.5,
            color="#444444", style="italic",
            bbox=dict(boxstyle="round",
                      facecolor="#FDFEFE",
                      alpha=0.85))

    fig.suptitle(
        "chRCC False Attractor — Script 1  |  "
        "OrganismCore | Document 96a  |  "
        "2026-03-02",
        fontsize=12, fontweight="bold",
        y=0.999)

    out = os.path.join(
        RESULTS_DIR,
        "chrcc_script1_figure.pdf")
    fig.savefig(out, bbox_inches="tight",
                dpi=150)
    plt.close(fig)
    log(f"  Figure saved: {out}")

# ═══════════════════════════════════════════════════════════════
# SCORECARD
# ═══════════════════════════════════════════════════════════════

def print_scorecard(df_all, panel_scores):
    log(""); log("="*60)
    log("FINAL SCORECARD")
    log("="*60)

    checks = [
        ("C1-P1  ATP6V1B1 falls with depth",
         "C1-P1"),
        ("C1-P2  FOXI1 falls with depth",
         "C1-P2"),
        ("C1-P3  KRT7 rises with depth",
         "C1-P3"),
        ("C1-P4  EZH2 rises with depth",
         "C1-P4"),
        ("C1-P5  OGDHL falls with depth",
         "C1-P5"),
        ("C1-P6  Depth predicts OS",
         "C1-P6"),
    ]

    confirmed = 0
    for label, code in checks:
        matching = [l for l in log_lines
                    if code in l]
        if not matching:
            v = "CHECK LOG"
        elif "CONFIRMED ✓" in matching[-1]:
            v = "CONFIRMED ✓"; confirmed += 1
        elif "NOT CONFIRMED" in matching[-1]:
            v = "NOT CONFIRMED ✗"
        elif "DEFERRED" in matching[-1] or \
                code == "C1-P6":
            v = "DEFERRED (no OS data)"
        else:
            v = matching[-1][-30:].strip()
        log(f"  {label:<42}  {v}")

    log(f"\n  OVERALL: {confirmed}/5 "
        f"(+1 deferred)")

    if panel_scores:
        dom = max(panel_scores,
                  key=lambda k:
                  panel_scores[k])
        log(f"\n  DOMINANT ACQUIRED IDENTITY: "
            f"{dom}")
        for h, v in sorted(
                panel_scores.items(),
                key=lambda x: -x[1]):
            log(f"    {h:<26} {v:>+8.4f}")

    top5p = df_all[
        ~df_all.gene.str.startswith("MT-")
    ].head(5)
    top5n = df_all[
        df_all.r_depth < 0
    ].head(5)

    log("\n  TOP 5 ACQUIRED (positive depth):")
    for _, row in top5p.iterrows():
        fl = sig_flag(row.r_depth, 15)
        log(f"    {row.gene:<14} "
            f"r={row.r_depth:>+.4f} "
            f"{fl.strip()}")

    log("\n  TOP 5 LOST (negative depth):")
    for _, row in top5n.iterrows():
        fl = sig_flag(row.r_depth, 15)
        log(f"    {row.gene:<14} "
            f"r={row.r_depth:>+.4f} "
            f"{fl.strip()}")

    log("\n  NEXT: review OBJ-4 attractor genes")
    log("  to set Script 2 predictions.")
    log("  OS: re-run when TCGA-KICH "
        "survival available.")

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    log("="*60)
    log("chRCC FALSE ATTRACTOR — SCRIPT 1")
    log("OrganismCore | Document 96a | "
        "2026-03-02")
    log("Author: Eric Robert Lawson")
    log("="*60)
    log("")
    log("DATA:  GSE19982 + GSE95425")
    log("GENES: 15244  |  SAMPLES: 83")
    log("n_tumour=15  r>0.514 for p<0.05")
    log("")

    # OBJ-1
    raw, t_cols, n_cols, oc_cols = \
        obj1_load_qc()

    # OBJ-2
    depth_t, depth_n, depth_oc = \
        obj2_depth_score(raw, t_cols,
                          n_cols, oc_cols)

    # OBJ-3
    df_normal = obj3_normal_pole(
        raw, t_cols, n_cols, depth_t)

    # OBJ-4
    df_all, panel_scores = \
        obj4_attractor_genes(
            raw, t_cols, n_cols, depth_t)

    # OBJ-5
    df_cc = obj5_cross_cancer(
        raw, t_cols, depth_t, df_all)

    # OBJ-6
    df_dt = obj6_drug_targets(
        raw, t_cols, n_cols,
        depth_t, df_all)

    # OBJ-7
    ti = obj7_transition_index(
        raw, t_cols, depth_t, df_all)

    # OBJ-8
    obj8_figure(
        raw, t_cols, n_cols, oc_cols,
        depth_t, depth_n, depth_oc,
        df_normal, df_all, df_cc,
        df_dt, ti, panel_scores)

    # Scorecard
    print_scorecard(df_all, panel_scores)

    write_log()

    log("")
    log("="*60)
    log("SCRIPT 1 COMPLETE")
    log(f"Results: {RESULTS_DIR}")
    log(f"Log:     {LOG_FILE}")
    log("="*60)


if __name__ == "__main__":
    main()
