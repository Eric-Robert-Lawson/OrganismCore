"""
PRCC False Attractor — Script 5
TYPE 1 vs TYPE 2 SEPARATION · FA-2 CHARACTERISATION
· WITHIN-SUBTYPE OS · SLC16A1/MCT4 · ccRCC CROSS-CANCER

Framework: OrganismCore
Document 95e-pre | 2026-03-02
Author: Eric Robert Lawson

═══════════════════════════════════════════════════════════════
MAJOR REVISION FROM DOCUMENT 95d:
  PRCC contains AT LEAST TWO FALSE ATTRACTORS.

  FA-1: Type 1 — biliary ductal identity
        MET-driven, chromosome 7 gain
        KRT19/ERBB2/KRT7 high, SLC22A6/FABP1 low
        Characterised in Scripts 1-4
        Mean depth = 0.700 (deeper on biliary axis)

  FA-2: Type 2 — eosinophilic programme
        CDKN2A-driven, different identity
        NOT characterised yet
        Mean depth = 0.567 (lower on biliary axis)
        WORSE OS (events=16/84 vs 5/76)

  FA-CIMP: FH-HLRCC — TCA collapse extreme
           Subset of Type 2 by annotation
           FH/OGDHL low, EZH2/MKI67 high
           Deepest proxy depth (0.846)

ALL SCRIPTS 1-4 RESULTS APPLY TO FA-1 (TYPE 1).
THIS SCRIPT CHARACTERISES FA-2 AND CONFIRMS FA-1.

════════════���══════════════════════════════════════════════════
PREDICTIONS LOCKED — 2026-03-02 — BEFORE SCRIPT 5

WITHIN-SUBTYPE PREDICTIONS:
  S5-P1:  FA-1 (Type 1) TI predicts OS
          within Type 1 only  p < 0.05
  S5-P2:  FA-1 depth Q4 vs Q1 OS  p < 0.05
          within Type 1 only
  S5-P3:  Type 2 has worse OS than Type 1
          logrank p < 0.05 (direct comparison)
  S5-P4:  CA9 within Type 1 only:
          CA9-high = worse OS  p < 0.05
          (removes Type 1/2 confound from Script 4)

FA-2 CHARACTERISATION PREDICTIONS:
  S5-P5:  FA-2 (Type 2) has distinct top gene
          correlates from FA-1
          Top 10 Type 2 depth genes ≠ top 10 Type 1
  S5-P6:  CDKN2A is a stronger Type 2 depth
          correlate than Type 1 depth correlate
          r(CDKN2A, depth_T2) > r(CDKN2A, depth_T1)
  S5-P7:  Type 2 retains PRCC normal pole loss
          (SLC22A6/FABP1 still down in Type 2
          relative to normal tissue)
          but identity axis is NOT biliary
  S5-P8:  EZH2 predicts worse OS within
          Type 2 (not just pooled)  p < 0.05

SLC16A1 PREDICTIONS:
  S5-P9:  SLC16A1 fall is steeper in FA-1
          than FA-2 (biliary architecture
          specifically impairs lactate export)
  S5-P10: SLC16A1 + ARG1 composite score
          predicts OS better than either alone
          (dual suppression)

CROSS-CANCER PREDICTIONS (if KIRC available):
  S5-P11: RUNX1 r_depth > 0.40 in ccRCC
  S5-P12: GOT1  r_depth < -0.40 in ccRCC

═══════════════════════════════════════════════════════════════
OBJECTIVES:
  OBJ-1:  Separate Type 1 and Type 2 using
          tumor_type from KIRP_clinicalMatrix
  OBJ-2:  FA-1 (Type 1) TI/depth OS re-run
  OBJ-3:  FA-2 (Type 2) attractor characterisation
          — find top depth correlates within Type 2
  OBJ-4:  Build FA-2 TI (Type 2 equivalent of TI)
  OBJ-5:  Type 2 drug target OS
  OBJ-6:  SLC16A1/MCT4 — subtype stratified
  OBJ-7:  Dual suppression score (ARG1 + SLC16A1)
          vs OS
  OBJ-8:  CIMP within Type 2 — depth extremes
  OBJ-9:  Cross-cancer RUNX1/GOT1 (if KIRC present)
  OBJ-10: Direct Type 1 vs Type 2 OS comparison
  OBJ-11: Normal tissue vs Type 1 vs Type 2
          identity marker comparison
  OBJ-12: Integrated drug priority map by subtype

DATA:
  All prior Script outputs reused
  tumor_type from KIRP_clinicalMatrix.tsv
  KIRP_survival.txt (saved in Script 4)
  TCGA_KIRC_HiSeqV2.gz (if present)
  OUTPUT: ./prcc_false_attractor/results_s5/
════════════════════════════════════════════���══════════════════
"""

import os
import gzip
import itertools
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.stats import pearsonr, mannwhitneyu, spearmanr
import warnings
warnings.filterwarnings("ignore")

# ═══════════════════════════════════════════════════════════════
# PATHS
# ═══════════════════════════════════════════════════════════════

BASE_DIR    = "./prcc_false_attractor/"
S1_DIR      = os.path.join(BASE_DIR, "results_s1/")
S2_DIR      = os.path.join(BASE_DIR, "results_s2/")
S3_DIR      = os.path.join(BASE_DIR, "results_s3/")
S4_DIR      = os.path.join(BASE_DIR, "results_s4/")
RESULTS_DIR = os.path.join(BASE_DIR, "results_s5/")
LOG_FILE    = os.path.join(RESULTS_DIR, "s5_log.txt")

KIRP_EXPR   = os.path.join(BASE_DIR, "TCGA_KIRP_HiSeqV2.gz")
KIRP_CLIN   = os.path.join(BASE_DIR, "KIRP_clinicalMatrix.tsv")
XENA_SURV   = os.path.join(BASE_DIR, "KIRP_survival.txt")
KIRC_EXPR   = os.path.join(BASE_DIR, "TCGA_KIRC_HiSeqV2.gz")
S1_DEPTH    = os.path.join(S1_DIR,   "depth_scores_tcga.csv")
S2_TI       = os.path.join(S2_DIR,   "transition_index.csv")

os.makedirs(RESULTS_DIR, exist_ok=True)

# ══════════════════════════════��════════════════════════════════
# GENE PANELS
# ═══════════════════════════════════════════════════════════════

# FA-1 (Type 1) biliary identity axis
FA1_POS = ["KRT19","KRT7","ERBB2","SOX4","AXL",
            "KDM1A","MET","ITGA3","KRT8","KRT18",
            "RUNX1","EZH2","SETD2","PBRM1"]
FA1_NEG = ["SLC22A6","FABP1","SLC34A1","GPX3",
            "CUBN","MIOX","GOT1","FH","OGDHL",
            "LDHB","ACADM","SLC5A2","LRP2"]

# FA-2 candidate genes (Type 2 eosinophilic)
# based on known Type 2 biology: CDKN2A, eosinophilic
# cytoplasm, pseudostratified nuclei, higher grade
FA2_CANDS = ["CDKN2A","CCND1","CDK6","MKI67","TOP2A",
              "CCNE1","CDK4","CDKN1A","CDKN1B",
              "TP53","MDM2","MDM4","RB1","E2F1",
              "HMGA2","IGF2BP1","IGF2BP2",
              "NOTCH1","NOTCH2","HES1","HEY1",
              "YAP1","TAZ","WWTR1","TEAD4",
              "NRF2","KEAP1","NFE2L2",
              "CPS1","CAD","DHODH",
              "LDLR","HMGCR","FASN","ACLY",
              "EPAS1","HIF1A","EGLN1","EGLN3",
              "SQSTM1","NBR1","MAP1LC3B",
              "BNIP3","BNIP3L","FUNDC1",
              "TFF1","TFF2","MUC5AC","MUC1",
              "FOXA1","FOXA2","HNF1A","HNF4A",
              "KRT5","KRT6A","KRT14","KRT17",
              "VIM","CDH1","CDH2","EPCAM",
              "KRT19","SLC22A6","FABP1",
              "S100A2","S100A4","S100P",
              "TACSTD2","CEACAM5","CEACAM6"]

# Shared attractor candidates
SHARED_CANDS = ["RUNX1","GOT1","EZH2","KDM1A",
                 "TET2","SLC22A6","MIOX","OGDHL",
                 "FH","B2M","HAVCR2","ARG1",
                 "SETD2","PBRM1","VHL","EPAS1",
                 "SLC16A1","LDHA","PDK1","CA9",
                 "MKI67","CDKN2A","FCGR3B",
                 "S100A8","S100A9","VEGFA"]

# ccRCC depth genes
KIRC_DEPTH_POS = ["RUNX1","LOXL2","TGFB1","EZH2",
                   "KDM1A","VIM","ACTA2","FAP",
                   "COL1A1","TWIST1","SNAI1","SNAI2"]
KIRC_DEPTH_NEG = ["FBP1","UMOD","GOT1","MIOX",
                   "SLC22A6","SLC34A1","GPX3",
                   "ACADM","CUBN","SLC5A2","LRP2"]

# Drug targets for OS
DRUG_GENES = {
    "EZH2_inhibitor":    "EZH2",
    "MET_inhibitor":     "MET",
    "ERBB2_targeted":    "ERBB2",
    "CDK4_inhibitor":    "CDK4",
    "KDM1A_inhibitor":   "KDM1A",
    "FH_aKG_proxy":      "FH",
    "OGDHL_aKG_proxy":   "OGDHL",
    "CA9_targeted":      "CA9",
    "PDL1_checkpoint":   "CD274",
    "HAVCR2_checkpoint": "HAVCR2",
    "ARG1_inhibitor":    "ARG1",
    "PDK1_DCA":          "PDK1",
    "SLC16A1_MCT4":      "SLC16A1",
    "B2M_MHC1":          "B2M",
    "CDK6_inhibitor":    "CDK6",
    "CDKN2A_proxy":      "CDKN2A",
}

# Normal tissue markers for OBJ-11
NORMAL_KIDNEY = ["SLC22A6","SLC34A1","CUBN","LRP2",
                  "SLC5A2","FABP1","GPX3","MIOX",
                  "SLC13A2","UMOD","ATP5A1","CPT1A",
                  "ACADM","GOT1","LDHB","FH","OGDHL"]

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

def fmt_p(p):
    if p is None or (isinstance(p, float)
                     and np.isnan(p)):
        return "—"
    if p < 1e-15: return "p<1e-15"
    if p < 0.001: return f"p={p:.2e}"
    return f"p={p:.4f}"

def norm01(arr):
    a = np.asarray(arr, float)
    mn, mx = np.nanmin(a), np.nanmax(a)
    if mx == mn: return np.zeros_like(a)
    return (a - mn) / (mx - mn)

def safe_r(x, y):
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    mask = np.isfinite(x) & np.isfinite(y)
    if mask.sum() < 5: return np.nan, np.nan
    return pearsonr(x[mask], y[mask])

def safe_mwu(a, b):
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    a = a[np.isfinite(a)]
    b = b[np.isfinite(b)]
    if len(a) < 3 or len(b) < 3:
        return np.nan, np.nan
    return mannwhitneyu(a, b, alternative="two-sided")

def safe_logrank(t1, e1, t2, e2):
    t1 = np.asarray(t1, float)
    e1 = np.asarray(e1, float)
    t2 = np.asarray(t2, float)
    e2 = np.asarray(e2, float)
    try:
        from lifelines.statistics import logrank_test
        r = logrank_test(t1, t2,
                         event_observed_A=e1,
                         event_observed_B=e2)
        return r.test_statistic, r.p_value
    except ImportError:
        pass
    all_t = np.sort(np.unique(
        np.concatenate([t1, t2])))
    O1 = O2 = E1 = E2 = 0.0
    for t in all_t:
        n1 = np.sum(t1 >= t)
        n2 = np.sum(t2 >= t)
        d1 = np.sum((t1 == t) & (e1 == 1))
        d2 = np.sum((t2 == t) & (e2 == 1))
        n = n1 + n2; d = d1 + d2
        if n < 2 or d == 0: continue
        O1 += d1; O2 += d2
        E1 += n1 * d / n
        E2 += n2 * d / n
    if E1 <= 0 or E2 <= 0: return np.nan, np.nan
    chi = (O1-E1)**2/E1 + (O2-E2)**2/E2
    from scipy.stats import chi2
    return chi, 1 - chi2.cdf(chi, df=1)

def kaplan_meier(t, e):
    t = np.asarray(t, float)
    e = np.asarray(e, float)
    order = np.argsort(t)
    t = t[order]; e = e[order]
    at_risk = len(t); s = 1.0
    times = [0]; surv = [1.0]
    for i in range(len(t)):
        if e[i] == 1:
            s *= (1 - 1.0 / at_risk)
            times.append(t[i])
            surv.append(s)
        at_risk -= 1
    return np.array(times), np.array(surv)

def gv(gene, expr, cols, idx):
    if gene not in expr.index: return None
    return pd.Series(
        expr.loc[gene, cols].values,
        index=cols).reindex(idx)

def top_correlates(d, expr, t_cols, n=20,
                   gene_list=None):
    """
    Return top n genes most correlated with d.
    If gene_list given, restrict to those genes.
    """
    genes = (gene_list if gene_list is not None
             else list(expr.index))
    results = []
    idx = d.index
    for gene in genes:
        if gene not in expr.index: continue
        g_ = gv(gene, expr, t_cols, idx)
        if g_ is None: continue
        r, p = safe_r(g_.values, d.values)
        if np.isnan(r): continue
        results.append((gene, r, p))
    results.sort(key=lambda x: abs(x[1]),
                 reverse=True)
    return results[:n]

# ═══════════════════════════════════════════════════════════════
# LOAD ALL PRIOR OUTPUTS
# ═══════════════════════════════════════════════════════════════

def load_all():
    log(""); log("="*60)
    log("LOADING ALL PRIOR OUTPUTS"); log("="*60)

    # S1 depth
    df1   = pd.read_csv(S1_DEPTH)
    depth = pd.Series(df1["depth_score"].values,
                      index=df1["sample_id"].values,
                      name="depth")
    log(f"  S1 depth: n={len(depth)}")

    # S2 TI
    df2 = pd.read_csv(S2_TI)
    ti  = pd.Series(df2["TI"].values,
                    index=df2["sample_id"].values,
                    name="TI")
    log(f"  S2 TI: n={len(ti)}")

    return depth, ti


def load_expr_matrix(path, label):
    log(f"  {label}: {path}")
    if not os.path.exists(path):
        log(f"  NOT FOUND: {path}")
        return None, None, None
    fn = gzip.open if path.endswith(".gz") else open
    with fn(path, "rt") as fh:
        raw = pd.read_csv(fh, sep="\t", index_col=0)
    types = []
    for s in raw.columns:
        parts = s.split("-")
        code  = parts[3][:2] \
            if len(parts) >= 4 else "00"
        types.append(
            "tumour" if code == "01" else
            "normal" if code == "11" else "other")
    meta   = pd.DataFrame({"t": types},
                           index=raw.columns)
    t_cols = raw.columns[
        meta["t"].eq("tumour").values]
    n_cols = raw.columns[
        meta["t"].eq("normal").values]
    log(f"  {label}: t={len(t_cols)} n={len(n_cols)}")
    return raw, t_cols, n_cols


def load_survival():
    log(""); log("  Loading survival data...")
    if not os.path.exists(XENA_SURV):
        log(f"  Not found: {XENA_SURV}")
        return None
    surv = pd.read_csv(XENA_SURV, sep="\t",
                       index_col=0,
                       low_memory=False)
    surv.index = surv.index.astype(str).str[:12]
    surv = surv[~surv.index.duplicated(keep="first")]
    log(f"  Survival: {surv.shape}")
    return surv


def load_subtype_labels():
    log("  Loading subtype labels...")
    if not os.path.exists(KIRP_CLIN):
        log(f"  Not found: {KIRP_CLIN}")
        return None
    clin = pd.read_csv(KIRP_CLIN, sep="\t",
                       index_col=0,
                       low_memory=False)
    clin.index = clin.index.astype(str).str[:12]
    clin = clin[~clin.index.duplicated(keep="first")]

    type_col = next(
        (c for c in ["tumor_type","TUMOR_TYPE",
                      "histological_type",
                      "paper_Histologic_Type"]
         if c in clin.columns), None)

    if type_col is None:
        log(f"  No subtype col. Available: "
            f"{list(clin.columns[:10])}")
        return None

    log(f"  Subtype col: {type_col}")
    log(f"  Values: "
        f"{clin[type_col].value_counts().to_dict()}")
    return clin[type_col].dropna()

# ═══════════════════════════════════════════════════════════════
# OBJ-1: BUILD SUBTYPE INDICES
# ═══════════════════════════════════════════════════════════════

def obj1_subtype_split(depth, subtypes, t_cols):
    log(""); log("="*60)
    log("OBJ-1 — SUBTYPE SPLIT"); log("="*60)

    d = depth.reindex(t_cols).dropna()

    if subtypes is None:
        log("  No subtype labels — cannot split.")
        return None, None, None, None

    # Map sample 12-char barcode to subtype
    sub_map = subtypes.to_dict()

    labels = pd.Series(
        {s: sub_map.get(s[:12], "UNKNOWN")
         for s in d.index},
        name="subtype").reindex(d.index)

    t1_idx = d.index[
        labels.str.lower().str.contains(
            r"type.?1|type_1", regex=True,
            na=False)]
    t2_idx = d.index[
        labels.str.lower().str.contains(
            r"type.?2|type_2", regex=True,
            na=False)]
    unk_idx = d.index[
        labels.str.lower().str.contains(
            r"unknown|nan", regex=True, na=True)]

    log(f"  Type 1: n={len(t1_idx)}")
    log(f"  Type 2: n={len(t2_idx)}")
    log(f"  Unknown: n={len(unk_idx)}")
    log(f"  Labelled: "
        f"n={len(t1_idx)+len(t2_idx)}")

    # Depth by subtype
    d_t1 = d.reindex(t1_idx)
    d_t2 = d.reindex(t2_idx)
    _, p_12 = safe_mwu(d_t1.values, d_t2.values)
    log(f"  Type 1 mean depth: {d_t1.mean():.4f}")
    log(f"  Type 2 mean depth: {d_t2.mean():.4f}")
    log(f"  MW p = {fmt_p(p_12)}")

    return t1_idx, t2_idx, unk_idx, labels

# ════════════════════════════════════════════��══════════════════
# OBJ-2: FA-1 (TYPE 1) WITHIN-SUBTYPE OS
# ═════════════════════════════════════════════════════��═════════

def obj2_fa1_os(depth, ti, expr, t_cols,
                 t1_idx, surv):
    log(""); log("="*60)
    log("OBJ-2 — FA-1 (TYPE 1) WITHIN-SUBTYPE OS")
    log("="*60)
    log("  S5-P1: FA-1 TI predicts OS  p < 0.05")
    log("  S5-P2: FA-1 Q4 vs Q1 OS  p < 0.05")
    log("  S5-P4: CA9-high = worse OS in Type 1")

    if t1_idx is None or len(t1_idx) < 10:
        log("  Insufficient Type 1 samples.")
        return None, None

    d_t1 = depth.reindex(t1_idx).dropna()
    log(f"  Type 1 samples: n={len(d_t1)}")

    # Build OS vectors for Type 1
    os_t, os_e = _build_os(d_t1, surv)
    valid = os_t.notna() & os_e.notna() & (os_t > 0)
    log(f"  Valid OS Type 1: {valid.sum()} "
        f"events={int(os_e[valid].sum())}")

    if valid.sum() < 10:
        log("  Too few Type 1 OS records.")
        return None, None

    d_v   = d_t1[valid]
    ost_v = os_t[valid]
    ose_v = os_e[valid]

    results = {}

    # S5-P1: TI in Type 1
    log(""); log("  TI OS in TYPE 1 (S5-P1):")
    if ti is not None:
        ti_t1 = ti.reindex(d_t1.index)
        v2    = valid & ti_t1.notna()
        if v2.sum() >= 10:
            ti2 = ti_t1[v2]
            t2  = os_t[v2]; e2 = os_e[v2]
            med = ti2.median()
            hi  = ti2 >= med; lo = ti2 < med
            _, p = safe_logrank(
                t2[hi].values, e2[hi].values,
                t2[lo].values, e2[lo].values)
            log(f"  TI-hi n={hi.sum()} "
                f"med={t2[hi].median():.0f}d")
            log(f"  TI-lo n={lo.sum()} "
                f"med={t2[lo].median():.0f}d")
            log(f"  logrank {fmt_p(p)}")
            worse = (t2[hi].median() <
                     t2[lo].median())
            if not np.isnan(p) and p < 0.05:
                log("  S5-P1 CONFIRMED ✓"
                    if worse else
                    "  S5-P1 INVERTED ✗")
            else:
                log("  S5-P1 NOT CONFIRMED (ns)")
            results["S5P1_p"] = p
            results["km_ti_hi_T1"] = kaplan_meier(
                t2[hi].values, e2[hi].values)
            results["km_ti_lo_T1"] = kaplan_meier(
                t2[lo].values, e2[lo].values)

    # S5-P2: Depth Q4/Q1 in Type 1
    log(""); log("  DEPTH Q4/Q1 in TYPE 1 (S5-P2):")
    q25 = d_v.quantile(0.25)
    q75 = d_v.quantile(0.75)
    q1m = d_v <= q25; q4m = d_v >= q75
    if q4m.sum() >= 5 and q1m.sum() >= 5:
        _, p_q = safe_logrank(
            ost_v[q4m].values, ose_v[q4m].values,
            ost_v[q1m].values, ose_v[q1m].values)
        log(f"  Q4 n={q4m.sum()} "
            f"med={ost_v[q4m].median():.0f}d")
        log(f"  Q1 n={q1m.sum()} "
            f"med={ost_v[q1m].median():.0f}d")
        log(f"  logrank {fmt_p(p_q)}")
        if not np.isnan(p_q) and p_q < 0.05:
            log("  S5-P2 CONFIRMED ✓")
        else:
            log("  S5-P2 NOT CONFIRMED (ns)")
        results["S5P2_p"]  = p_q
        results["km_q4_T1"] = kaplan_meier(
            ost_v[q4m].values, ose_v[q4m].values)
        results["km_q1_T1"] = kaplan_meier(
            ost_v[q1m].values, ose_v[q1m].values)

    # S5-P4: CA9 in Type 1
    log(""); log("  CA9 OS IN TYPE 1 (S5-P4):")
    if "CA9" in expr.index:
        ca9 = gv("CA9", expr, t_cols, d_v.index)
        if ca9 is not None:
            med = ca9.median()
            hi  = ca9 >= med; lo = ca9 < med
            _, p_ca9 = safe_logrank(
                ost_v.reindex(ca9.index)[hi].values,
                ose_v.reindex(ca9.index)[hi].values,
                ost_v.reindex(ca9.index)[lo].values,
                ose_v.reindex(ca9.index)[lo].values)
            log(f"  CA9-hi med="
                f"{ost_v.reindex(ca9.index)[hi].median():.0f}d "
                f"n={hi.sum()}")
            log(f"  CA9-lo med="
                f"{ost_v.reindex(ca9.index)[lo].median():.0f}d "
                f"n={lo.sum()}")
            log(f"  logrank {fmt_p(p_ca9)}")
            worse_ca9 = (
                ost_v.reindex(ca9.index)[hi].median() <
                ost_v.reindex(ca9.index)[lo].median())
            if not np.isnan(p_ca9) and p_ca9 < 0.05:
                log("  S5-P4 CONFIRMED ✓"
                    if worse_ca9 else
                    "  S5-P4 INVERTED ✗")
            else:
                log("  S5-P4 NOT CONFIRMED (ns)")
            results["S5P4_p"] = p_ca9

    # Drug target OS within Type 1
    log(""); log("  DRUG TARGET OS — TYPE 1:")
    log(f"  {'Drug':<22} {'gene':<8} "
        f"{'p':>12} {'med_hi':>8} {'med_lo':>8}")
    log(f"  {'─'*58}")
    drug_rows = []
    for drug, gene in DRUG_GENES.items():
        if gene not in expr.index: continue
        g_  = gv(gene, expr, t_cols, d_v.index)
        if g_ is None: continue
        med = g_.median()
        hi  = g_ >= med; lo = g_ < med
        thi = ost_v.reindex(g_.index)[hi].dropna()
        ehi = ose_v.reindex(g_.index)[hi].dropna()
        tlo = ost_v.reindex(g_.index)[lo].dropna()
        elo = ose_v.reindex(g_.index)[lo].dropna()
        if len(thi) < 4 or len(tlo) < 4: continue
        _, p_g = safe_logrank(
            thi.values, ehi.values,
            tlo.values, elo.values)
        fl = "★" if not np.isnan(p_g) \
            and p_g < 0.05 else " "
        log(f"  {fl}{drug:<22} {gene:<8} "
            f"{fmt_p(p_g):>12} "
            f"{thi.median():>8.0f} "
            f"{tlo.median():>8.0f}")
        drug_rows.append({
            "drug": drug, "gene": gene,
            "p_logrank": p_g,
            "subtype": "Type1",
            "med_hi": thi.median(),
            "med_lo": tlo.median()})

    pd.DataFrame(drug_rows).to_csv(
        os.path.join(RESULTS_DIR,
                     "drug_OS_type1.csv"),
        index=False)

    return results, {
        "d_v": d_v, "ost_v": ost_v,
        "ose_v": ose_v,
        "q1m": q1m, "q4m": q4m}

# ═══════════════════════════════════════════════════════════════
# OBJ-3 / OBJ-4: FA-2 CHARACTERISATION + TYPE 2 TI
# ═══════════════════════════════════════════════════════════════

def obj3_4_fa2_characterisation(depth, expr,
                                  t_cols, n_cols,
                                  t1_idx, t2_idx):
    log(""); log("="*60)
    log("OBJ-3/4 — FA-2 CHARACTERISATION")
    log("="*60)
    log("  S5-P5: Type 2 top genes ≠ Type 1 top genes")
    log("  S5-P6: CDKN2A stronger in Type 2")
    log("  S5-P7: Normal pole loss in Type 2")

    if t1_idx is None or t2_idx is None:
        log("  Cannot run — subtype indices absent.")
        return None, None

    d = depth.reindex(t_cols).dropna()

    # Build subtype-specific depth scores
    # Type 2 depth = within-Type2 variation
    # We compute residual depth after removing
    # the Type 1 biliary axis signal
    # Strategy: use Type 2 samples only,
    # find genes that correlate with depth
    # WITHIN Type 2 samples

    d_t1 = d.reindex(t1_idx).dropna()
    d_t2 = d.reindex(t2_idx).dropna()

    log(f"  Type 1: n={len(d_t1)}")
    log(f"  Type 2: n={len(d_t2)}")

    # ── Top correlates WITHIN TYPE 1 ─────────────────────────
    log(""); log("  TOP DEPTH CORRELATES — TYPE 1:")
    log(f"  {'Gene':<14} {'r_T1':>9} {'p':>12}")
    log(f"  {'─'*36}")
    top_t1 = top_correlates(d_t1, expr, t_cols,
                              n=25)
    top_t1_genes = set()
    for gene, r, p in top_t1:
        log(f"  {gene:<14} {r:>+9.4f} {fmt_p(p):>12}")
        top_t1_genes.add(gene)

    # ── Top correlates WITHIN TYPE 2 ─────────────────────────
    log(""); log("  TOP DEPTH CORRELATES — TYPE 2:")
    log(f"  {'Gene':<14} {'r_T2':>9} "
        f"{'r_T1':>9} {'same?'}")
    log(f"  {'─'*46}")
    top_t2 = top_correlates(d_t2, expr, t_cols,
                              n=25)
    top_t2_genes = set()
    t1_r_map = {g: r for g, r, _ in top_t1}

    for gene, r2, p in top_t2:
        r1 = t1_r_map.get(gene, np.nan)
        same = ("SHARED" if gene in top_t1_genes
                else "T2_SPECIFIC")
        log(f"  {gene:<14} {r2:>+9.4f} "
            f"{r1:>+9.4f} {same}")
        top_t2_genes.add(gene)

    # S5-P5: Overlap test
    overlap = top_t1_genes & top_t2_genes
    t2_specific = top_t2_genes - top_t1_genes
    t1_specific = top_t1_genes - top_t2_genes
    log(f"\n  Overlap (top25): {len(overlap)}/25")
    log(f"  T2-specific: {sorted(t2_specific)}")
    log(f"  T1-specific: {sorted(t1_specific)}")
    if len(t2_specific) >= 5:
        log("  S5-P5 CONFIRMED: distinct FA-2 genes ✓")
    else:
        log("  S5-P5 NOT CONFIRMED — high overlap")

    # S5-P6: CDKN2A comparison
    log(""); log("  CDKN2A DEPTH COMPARISON (S5-P6):")
    if "CDKN2A" in expr.index:
        cdkn_t1 = gv("CDKN2A", expr, t_cols,
                      d_t1.index)
        cdkn_t2 = gv("CDKN2A", expr, t_cols,
                      d_t2.index)
        r_t1, p_t1 = safe_r(cdkn_t1.values,
                              d_t1.values)
        r_t2, p_t2 = safe_r(cdkn_t2.values,
                              d_t2.values)
        log(f"  r(CDKN2A, depth) in Type 1: "
            f"{r_t1:+.4f} {fmt_p(p_t1)}")
        log(f"  r(CDKN2A, depth) in Type 2: "
            f"{r_t2:+.4f} {fmt_p(p_t2)}")
        if abs(r_t2) > abs(r_t1):
            log("  S5-P6 CONFIRMED: CDKN2A stronger "
                "in Type 2 ✓")
        else:
            log("  S5-P6 NOT CONFIRMED")

    # S5-P7: Normal pole gene expression
    log(""); log("  NORMAL POLE LOSS (S5-P7):")
    log("  Testing whether Type 2 still loses normal"
        " kidney genes vs normal tissue...")
    log(f"  {'Gene':<14} {'Normal':>8} "
        f"{'Type1':>8} {'Type2':>8} "
        f"{'T1<N?':>7} {'T2<N?':>7}")
    log(f"  {'─'*58}")

    n_cols_use = n_cols if n_cols is not None \
        and len(n_cols) > 0 else None

    norm_results = []
    for gene in NORMAL_KIDNEY:
        if gene not in expr.index: continue
        g_t1 = gv(gene, expr, t_cols,
                  d_t1.index)
        g_t2 = gv(gene, expr, t_cols,
                  d_t2.index)
        mean_t1 = g_t1.mean() if g_t1 is not None \
            else np.nan
        mean_t2 = g_t2.mean() if g_t2 is not None \
            else np.nan
        mean_n  = np.nan
        if n_cols_use is not None \
                and gene in expr.index:
            mean_n = expr.loc[gene,
                               n_cols_use].mean()
        t1_less = ("YES" if not np.isnan(mean_t1)
                   and not np.isnan(mean_n)
                   and mean_t1 < mean_n else "no")
        t2_less = ("YES" if not np.isnan(mean_t2)
                   and not np.isnan(mean_n)
                   and mean_t2 < mean_n else "no")
        log(f"  {gene:<14} {mean_n:>8.3f} "
            f"{mean_t1:>8.3f} {mean_t2:>8.3f} "
            f"{t1_less:>7} {t2_less:>7}")
        norm_results.append({
            "gene": gene,
            "mean_normal": mean_n,
            "mean_Type1":  mean_t1,
            "mean_Type2":  mean_t2})

    pd.DataFrame(norm_results).to_csv(
        os.path.join(RESULTS_DIR,
                     "normal_pole_comparison.csv"),
        index=False)

    # ── Build FA-2 TI ─────────────────────────────────────────
    log(""); log("  BUILDING FA-2 TRANSITION INDEX:")
    log("  FA-2 TI = top positive T2 gene")
    log("           minus top negative T2 gene")
    log("           (within Type 2 samples)")

    if len(top_t2) >= 2:
        # Find best positive and negative within T2
        t2_pos = [(g, r, p) for g, r, p in top_t2
                  if r > 0]
        t2_neg = [(g, r, p) for g, r, p in top_t2
                  if r < 0]

        # Exclude genes that are also FA-1 primary
        fa1_primary = {"KRT19","SLC22A6","KRT7",
                        "ERBB2","FABP1","SLC34A1",
                        "GPX3","CUBN"}

        t2_pos_filt = [(g, r, p) for g, r, p
                       in t2_pos
                       if g not in fa1_primary]
        t2_neg_filt = [(g, r, p) for g, r, p
                       in t2_neg
                       if g not in fa1_primary]

        if t2_pos_filt and t2_neg_filt:
            best_pos = t2_pos_filt[0][0]
            best_neg = t2_neg_filt[0][0]
        elif t2_pos and t2_neg:
            best_pos = t2_pos[0][0]
            best_neg = t2_neg[0][0]
        else:
            best_pos = best_neg = None

        if best_pos and best_neg:
            log(f"  FA-2 TI positive pole: {best_pos}")
            log(f"  FA-2 TI negative pole: {best_neg}")

            # Compute FA-2 TI on ALL tumours
            p_v = gv(best_pos, expr, t_cols,
                     d.index)
            n_v = gv(best_neg, expr, t_cols,
                     d.index)
            if p_v is not None and n_v is not None:
                ti_fa2 = pd.Series(
                    norm01(p_v.values) -
                    norm01(n_v.values),
                    index=d.index, name="TI_FA2")

                # Validate within Type 2
                ti_fa2_t2 = ti_fa2.reindex(d_t2.index)
                r_fa2_t2, p_fa2 = safe_r(
                    ti_fa2_t2.values, d_t2.values)
                log(f"  FA-2 TI r(depth_T2) = "
                    f"{r_fa2_t2:+.4f} {fmt_p(p_fa2)}")

                # Compare vs FA-1 TI on Type 2
                ti_t2 = gv("KRT19", expr, t_cols,
                            d_t2.index)
                slc_t2 = gv("SLC22A6", expr, t_cols,
                             d_t2.index)
                if ti_t2 is not None \
                        and slc_t2 is not None:
                    ti_fa1_t2 = pd.Series(
                        norm01(ti_t2.values) -
                        norm01(slc_t2.values),
                        index=d_t2.index)
                    r_fa1_t2, _ = safe_r(
                        ti_fa1_t2.values,
                        d_t2.values)
                    log(f"  FA-1 TI r(depth_T2) = "
                        f"{r_fa1_t2:+.4f}")
                    if abs(r_fa2_t2) > abs(r_fa1_t2):
                        log("  FA-2 TI is better at "
                            "capturing Type 2 variation ✓")
                    else:
                        log("  FA-1 TI still dominates "
                            "Type 2 variation.")

                # Save FA-2 TI
                ti_fa2.reset_index().rename(
                    columns={"index": "sample_id",
                             0: "TI_FA2"}
                ).to_csv(
                    os.path.join(RESULTS_DIR,
                                 "TI_FA2.csv"),
                    index=False)
                log(f"  FA-2 TI saved.")
                return (ti_fa2, best_pos, best_neg,
                        top_t1, top_t2)

    log("  Could not build FA-2 TI.")
    return None, None, None, top_t1, top_t2

# ═══════════════════════════════════════════════════════════════
# OBJ-5: TYPE 2 DRUG TARGET OS
# ═══════════════════════════════════════════════════════════════

def obj5_fa2_os(depth, ti_fa2, expr, t_cols,
                 t2_idx, surv):
    log(""); log("="*60)
    log("OBJ-5 — FA-2 (TYPE 2) OS"); log("="*60)
    log("  S5-P8: EZH2 predicts OS in Type 2")

    if t2_idx is None or len(t2_idx) < 10:
        log("  Insufficient Type 2 samples.")
        return None, None

    d_t2 = depth.reindex(t2_idx).dropna()
    os_t, os_e = _build_os(d_t2, surv)
    valid = os_t.notna() & os_e.notna() & (os_t > 0)
    log(f"  Type 2 valid OS: {valid.sum()} "
        f"events={int(os_e[valid].sum())}")

    if valid.sum() < 8:
        log("  Too few records for Type 2 OS.")
        return None, None

    d_v   = d_t2[valid]
    ost_v = os_t[valid]
    ose_v = os_e[valid]

    results = {}

    # FA-2 TI OS
    if ti_fa2 is not None:
        log(""); log("  FA-2 TI OS:")
        ti_v2 = ti_fa2.reindex(d_t2.index)
        v2    = valid & ti_v2.notna()
        if v2.sum() >= 8:
            ti2 = ti_v2[v2]
            t2  = os_t[v2]; e2 = os_e[v2]
            med = ti2.median()
            hi  = ti2 >= med; lo = ti2 < med
            _, p = safe_logrank(
                t2[hi].values, e2[hi].values,
                t2[lo].values, e2[lo].values)
            log(f"  FA-2 TI-hi n={hi.sum()} "
                f"med={t2[hi].median():.0f}d")
            log(f"  FA-2 TI-lo n={lo.sum()} "
                f"med={t2[lo].median():.0f}d")
            log(f"  logrank {fmt_p(p)}")
            results["fa2_ti_p"] = p

    # Drug target OS in Type 2
    log(""); log("  DRUG TARGET OS — TYPE 2:")
    log(f"  {'Drug':<22} {'gene':<8} "
        f"{'p':>12} {'med_hi':>8} {'med_lo':>8}")
    log(f"  {'─'*58}")
    drug_rows = []
    for drug, gene in DRUG_GENES.items():
        if gene not in expr.index: continue
        g_  = gv(gene, expr, t_cols, d_v.index)
        if g_ is None: continue
        med = g_.median()
        hi  = g_ >= med; lo = g_ < med
        thi = ost_v.reindex(g_.index)[hi].dropna()
        ehi = ose_v.reindex(g_.index)[hi].dropna()
        tlo = ost_v.reindex(g_.index)[lo].dropna()
        elo = ose_v.reindex(g_.index)[lo].dropna()
        if len(thi) < 3 or len(tlo) < 3: continue
        _, p_g = safe_logrank(
            thi.values, ehi.values,
            tlo.values, elo.values)
        fl = "★" if not np.isnan(p_g) \
            and p_g < 0.05 else " "
        log(f"  {fl}{drug:<22} {gene:<8} "
            f"{fmt_p(p_g):>12} "
            f"{thi.median():>8.0f} "
            f"{tlo.median():>8.0f}")
        drug_rows.append({
            "drug": drug, "gene": gene,
            "p_logrank": p_g,
            "subtype": "Type2",
            "med_hi": thi.median(),
            "med_lo": tlo.median()})

        # S5-P8 check
        if drug == "EZH2_inhibitor" and \
                not np.isnan(p_g) and p_g < 0.05:
            log("  S5-P8 CONFIRMED: EZH2 OS in "
                "Type 2 ✓")

    pd.DataFrame(drug_rows).to_csv(
        os.path.join(RESULTS_DIR,
                     "drug_OS_type2.csv"),
        index=False)

    # S5-P3: Type 1 vs Type 2 OS (OBJ-10 preview)
    log(""); log("  TYPE 1 vs TYPE 2 OS (S5-P3):")
    results["d_v"]   = d_v
    results["ost_v"] = ost_v
    results["ose_v"] = ose_v
    return results, {
        "d_v": d_v, "ost_v": ost_v,
        "ose_v": ose_v}

# ═══════════════════════════════════════════════════════════════
# OBJ-6 / OBJ-7: SLC16A1 + DUAL SUPPRESSION
# ═══════════════════════════════════════════════════════════════

def obj6_7_slc16a1_dual(depth, expr, t_cols,
                          t1_idx, t2_idx, surv):
    log(""); log("="*60)
    log("OBJ-6/7 — SLC16A1/MCT4 + DUAL SUPPRESSION")
    log("="*60)
    log("  S5-P9:  SLC16A1 fall steeper in Type 1")
    log("  S5-P10: ARG1+SLC16A1 composite predicts OS")

    d = depth.reindex(t_cols).dropna()

    if "SLC16A1" not in expr.index:
        log("  SLC16A1 not in matrix."); return

    slc = gv("SLC16A1", expr, t_cols, d.index)
    arg = gv("ARG1",    expr, t_cols, d.index)

    # Overall depth correlation
    r_slc, p_slc = safe_r(slc.values, d.values)
    log(f"  r(SLC16A1, depth) = "
        f"{r_slc:+.4f} {fmt_p(p_slc)}")

    # Within subtype
    log(""); log("  SLC16A1 WITHIN SUBTYPES (S5-P9):")
    for idx, label in [(t1_idx, "Type1"),
                        (t2_idx, "Type2")]:
        if idx is None: continue
        d_sub = d.reindex(idx).dropna()
        g_sub = slc.reindex(d_sub.index)
        r, p  = safe_r(g_sub.values, d_sub.values)
        log(f"  {label}: r(SLC16A1, depth) = "
            f"{r:+.4f} {fmt_p(p)}")

    r_t1_slc = r_t2_slc = np.nan
    if t1_idx is not None:
        d_t1 = d.reindex(t1_idx).dropna()
        r_t1_slc, _ = safe_r(
            slc.reindex(d_t1.index).values,
            d_t1.values)
    if t2_idx is not None:
        d_t2 = d.reindex(t2_idx).dropna()
        r_t2_slc, _ = safe_r(
            slc.reindex(d_t2.index).values,
            d_t2.values)

    if not np.isnan(r_t1_slc) and \
            not np.isnan(r_t2_slc):
        if abs(r_t1_slc) > abs(r_t2_slc):
            log("  S5-P9 CONFIRMED: SLC16A1 fall "
                "steeper in Type 1 ✓")
        else:
            log("  S5-P9 NOT CONFIRMED")

    # LDHA vs SLC16A1 — lactate imbalance
    log(""); log("  LDHA vs SLC16A1 (lactate balance):")
    if "LDHA" in expr.index:
        ldha = gv("LDHA", expr, t_cols, d.index)
        r_ld, _ = safe_r(ldha.values, d.values)
        log(f"  r(LDHA,    depth) = {r_ld:+.4f}")
        log(f"  r(SLC16A1, depth) = {r_slc:+.4f}")
        if r_ld > 0 and r_slc < 0:
            log("  LACTATE IMBALANCE CONFIRMED:")
            log("  LDHA UP + MCT4 DOWN = lactate "
                "accumulation with depth ✓")
            imbalance = pd.Series(
                norm01(ldha.values) -
                norm01(slc.values),
                index=d.index,
                name="lactate_imbalance")
            r_im, p_im = safe_r(
                imbalance.values, d.values)
            log(f"  Lactate imbalance score "
                f"r(depth) = {r_im:+.4f} "
                f"{fmt_p(p_im)}")

    # Dual suppression score
    log(""); log("  DUAL SUPPRESSION SCORE (S5-P10):")
    log("  Score = ARG1_norm + (1 - SLC16A1_norm)")
    log("  High = ARG1 high + MCT4 low = maximum "
        "T cell suppression")

    if arg is not None and slc is not None:
        dual = pd.Series(
            norm01(arg.values) +
            (1 - norm01(slc.values)),
            index=d.index,
            name="dual_suppression")
        r_dual, p_dual = safe_r(
            dual.values, d.values)
        log(f"  Dual score r(depth) = "
            f"{r_dual:+.4f} {fmt_p(p_dual)}")

        # Dual score OS
        if surv is not None:
            os_t, os_e = _build_os(d, surv)
            valid = (os_t.notna() & os_e.notna()
                     & (os_t > 0))
            if valid.sum() >= 30:
                ds_v = dual[valid]
                t_v  = os_t[valid]
                e_v  = os_e[valid]
                med  = ds_v.median()
                hi   = ds_v >= med
                lo   = ds_v < med
                _, p_os = safe_logrank(
                    t_v[hi].values, e_v[hi].values,
                    t_v[lo].values, e_v[lo].values)
                log(f"  Dual score OS logrank "
                    f"{fmt_p(p_os)}")
                log(f"  Hi med={t_v[hi].median():.0f}d "
                    f"Lo med={t_v[lo].median():.0f}d")

                # Compare ARG1 alone
                if arg is not None:
                    a_v = arg[valid]
                    _, p_arg = safe_logrank(
                        t_v[a_v >= a_v.median()].values,
                        e_v[a_v >= a_v.median()].values,
                        t_v[a_v <  a_v.median()].values,
                        e_v[a_v <  a_v.median()].values)
                    log(f"  ARG1 alone OS logrank "
                        f"{fmt_p(p_arg)}")

                # Compare SLC16A1 alone
                if slc is not None:
                    s_v = slc[valid]
                    _, p_slc_os = safe_logrank(
                        t_v[s_v >= s_v.median()].values,
                        e_v[s_v >= s_v.median()].values,
                        t_v[s_v <  s_v.median()].values,
                        e_v[s_v <  s_v.median()].values)
                    log(f"  SLC16A1 alone OS logrank "
                        f"{fmt_p(p_slc_os)}")

                    if not np.isnan(p_os):
                        solo_best = min(
                            p_arg if not np.isnan(p_arg)
                            else 1.0,
                            p_slc_os if not
                            np.isnan(p_slc_os) else 1.0)
                        if p_os < solo_best:
                            log("  S5-P10 CONFIRMED: "
                                "Dual score better "
                                "than either alone ✓")
                        else:
                            log("  S5-P10 NOT CONFIRMED")

        # Save
        dual.reset_index().rename(
            columns={"index": "sample_id",
                     0: "dual_suppression"}
        ).to_csv(
            os.path.join(RESULTS_DIR,
                         "dual_suppression_score.csv"),
            index=False)

# ═════════════════════════════════════════���═════════════════════
# OBJ-8: CIMP WITHIN TYPE 2
# ═══════════════════════════════════════════════════════════════

def obj8_cimp_within_type2(depth, expr, t_cols,
                             t2_idx, surv):
    log(""); log("="*60)
    log("OBJ-8 — CIMP WITHIN TYPE 2"); log("="*60)

    if t2_idx is None or len(t2_idx) < 5:
        log("  No Type 2 indices."); return

    d_t2 = depth.reindex(t2_idx).dropna()

    # CIMP proxy within Type 2
    fh   = gv("FH",    expr, t_cols, d_t2.index)
    ogdh = gv("OGDHL", expr, t_cols, d_t2.index)
    ezh2 = gv("EZH2",  expr, t_cols, d_t2.index)

    if fh is None or ogdh is None or ezh2 is None:
        log("  FH/OGDHL/EZH2 missing."); return

    cimp_hi = ((fh   <= fh.quantile(0.20)) &
                (ogdh <= ogdh.quantile(0.20)) &
                (ezh2 >= ezh2.quantile(0.80)))
    non_cimp = ~cimp_hi

    log(f"  CIMP-proxy within Type 2: "
        f"n={cimp_hi.sum()}")
    log(f"  non-CIMP Type 2:          "
        f"n={non_cimp.sum()}")

    if cimp_hi.sum() < 3:
        log("  Too few CIMP proxy samples "
            "within Type 2.")
        return

    d_cimp = d_t2[cimp_hi.values]
    d_non  = d_t2[non_cimp.values]
    _, p_c = safe_mwu(d_cimp.values, d_non.values)
    log(f"  CIMP depth:     {d_cimp.mean():.4f}")
    log(f"  non-CIMP depth: {d_non.mean():.4f}")
    log(f"  MW {fmt_p(p_c)}")

    # Marker profile
    genes = ["FH","OGDHL","EZH2","MKI67",
              "KRT19","SLC22A6","CDKN2A",
              "CDK4","ARG1","CA9","HLA-A","B2M"]
    log(f"\n  {'Gene':<12} {'CIMP_T2':>10} "
        f"{'non_CIMP_T2':>12} {'p':>12}")
    log(f"  {'─'*50}")
    for gene in [g for g in genes
                 if g in expr.index]:
        g_ = gv(gene, expr, t_cols, d_t2.index)
        if g_ is None: continue
        mc = g_[cimp_hi.values].mean()
        mn = g_[non_cimp.values].mean()
        _, p_ = safe_mwu(
            g_[cimp_hi.values].values,
            g_[non_cimp.values].values)
        fl = "★" if not np.isnan(p_) \
            and p_ < 0.05 else " "
        log(f"  {fl}{gene:<12} {mc:>10.3f} "
            f"{mn:>12.3f} {fmt_p(p_):>12}")

    # CIMP OS within Type 2
    if surv is not None:
        log("")
        os_t, os_e = _build_os(d_t2, surv)
        valid = (os_t.notna() & os_e.notna()
                 & (os_t > 0))
        if valid.sum() >= 5:
            ci_v  = cimp_hi[valid.values[:len(
                cimp_hi)]] if len(cimp_hi) == \
                len(valid) else \
                cimp_hi.reindex(
                    d_t2[valid].index).fillna(False)
            nc_v  = ~ci_v
            if ci_v.sum() >= 2 and nc_v.sum() >= 3:
                _, p_os = safe_logrank(
                    os_t[valid][ci_v].values,
                    os_e[valid][ci_v].values,
                    os_t[valid][nc_v].values,
                    os_e[valid][nc_v].values)
                log(f"  CIMP vs non-CIMP Type 2 OS: "
                    f"{fmt_p(p_os)}")

# ═══════════════════════════════════════════════════════════════
# OBJ-9: CROSS-CANCER (if KIRC available)
# ═══════════════════════════════════════════════════════════════

def obj9_cross_cancer(expr_kirp, t_cols_kirp,
                       depth_kirp,
                       expr_kirc, t_cols_kirc):
    log(""); log("="*60)
    log("OBJ-9 — CROSS-CANCER"); log("="*60)
    log("  S5-P11: RUNX1 r>0.40 in ccRCC")
    log("  S5-P12: GOT1  r<-0.40 in ccRCC")

    d_kirp = depth_kirp.reindex(
        t_cols_kirp).dropna()

    if expr_kirc is None:
        log("  ccRCC matrix absent.")
        log("  S5-P11 / S5-P12 DEFERRED.")
        log("  To enable: place TCGA_KIRC_HiSeqV2.gz "
            "in BASE_DIR.")
        return None

    # Build ccRCC depth proxy
    pos_av = [g for g in KIRC_DEPTH_POS
              if g in expr_kirc.index]
    neg_av = [g for g in KIRC_DEPTH_NEG
              if g in expr_kirc.index]

    if not pos_av or not neg_av:
        log("  ccRCC depth genes missing.")
        return None

    pos_sc = expr_kirc.loc[
        pos_av, t_cols_kirc].mean(axis=0)
    neg_sc = expr_kirc.loc[
        neg_av, t_cols_kirc].mean(axis=0)
    d_kirc = pd.Series(
        norm01(norm01(pos_sc.values) -
               norm01(neg_sc.values)),
        index=t_cols_kirc, name="kirc_depth")
    log(f"  ccRCC depth proxy: n={len(d_kirc)}")

    log(f"\n  {'Gene':<14} {'PRCC_r':>9} "
        f"{'ccRCC_r':>9} {'shared?'}")
    log(f"  {'─'*46}")

    for gene in SHARED_CANDS:
        gp = gv(gene, expr_kirp,
                t_cols_kirp, d_kirp.index)
        gc = gv(gene, expr_kirc,
                t_cols_kirc, d_kirc.index)
        rp = safe_r(gp.values,
                     d_kirp.values)[0] \
            if gp is not None else np.nan
        rc = safe_r(gc.values,
                     d_kirc.values)[0] \
            if gc is not None else np.nan

        shared = (
            "SHARED_ATT"  if rp > 0.30 and rc > 0.30
            else "SHARED_NORM" if rp < -0.30 and rc < -0.30
            else "PRCC_ONLY"   if abs(rp) > 0.30
            else "ccRCC_ONLY"  if abs(rc) > 0.30
            else "")
        log(f"  {gene:<14} {rp:>+9.4f} "
            f"{rc:>+9.4f} {shared}")

    # S5-P11/P12
    for gene, thresh, label, pred in [
        ("RUNX1", 0.40, "S5-P11", "CONFIRMED ✓"),
        ("GOT1", -0.40, "S5-P12", "CONFIRMED ✓"),
    ]:
        gc  = gv(gene, expr_kirc,
                 t_cols_kirc, d_kirc.index)
        rc  = safe_r(gc.values,
                      d_kirc.values)[0] \
            if gc is not None else np.nan
        log(f"\n  {label}: {gene} ccRCC r={rc:+.4f}")
        if not np.isnan(rc):
            met = (rc > thresh if thresh > 0
                   else rc < thresh)
            log(f"  {label} {pred if met else 'NOT CONFIRMED'}")

    return d_kirc

# ═══════════════════════════════════════════════════════════════
# OBJ-10: DIRECT TYPE 1 vs TYPE 2 OS
# ═══════════════════════════════════════════════════════════════

def obj10_type1_vs_type2_os(depth, expr, t_cols,
                              t1_idx, t2_idx, surv):
    log(""); log("="*60)
    log("OBJ-10 — TYPE 1 vs TYPE 2 OS"); log("="*60)
    log("  S5-P3: Type 2 worse OS than Type 1")

    if t1_idx is None or t2_idx is None:
        log("  Cannot compare — indices absent.")
        return None

    d = depth.reindex(t_cols).dropna()

    os_t_all, os_e_all = _build_os(d, surv)
    valid = (os_t_all.notna() & os_e_all.notna()
             & (os_t_all > 0))

    t1_valid = t1_idx.intersection(d[valid].index)
    t2_valid = t2_idx.intersection(d[valid].index)

    log(f"  Type 1 with OS: n={len(t1_valid)} "
        f"events="
        f"{int(os_e_all.reindex(t1_valid).sum())}")
    log(f"  Type 2 with OS: n={len(t2_valid)} "
        f"events="
        f"{int(os_e_all.reindex(t2_valid).sum())}")

    t1_t = os_t_all.reindex(t1_valid).values
    t1_e = os_e_all.reindex(t1_valid).values
    t2_t = os_t_all.reindex(t2_valid).values
    t2_e = os_e_all.reindex(t2_valid).values

    _, p_12 = safe_logrank(t1_t, t1_e,
                            t2_t, t2_e)
    med_t1 = np.nanmedian(t1_t)
    med_t2 = np.nanmedian(t2_t)

    log(f"  Type 1 median OS: {med_t1:.0f}d")
    log(f"  Type 2 median OS: {med_t2:.0f}d")
    log(f"  logrank {fmt_p(p_12)}")

    worse_t2 = med_t2 < med_t1
    if not np.isnan(p_12) and p_12 < 0.05:
        log("  S5-P3 CONFIRMED ✓"
            if worse_t2 else
            "  S5-P3 INVERTED ✗")
    else:
        log("  S5-P3 NOT CONFIRMED (ns)")

    return {
        "km_T1": kaplan_meier(t1_t, t1_e),
        "km_T2": kaplan_meier(t2_t, t2_e),
        "p_12": p_12,
        "med_t1": med_t1,
        "med_t2": med_t2,
    }

# ═══════════════════════════════════════════════════════════════
# OBJ-12: INTEGRATED DRUG PRIORITY MAP
# ═══════════════════════════════════════════════════════════════

def obj12_drug_priority_map(expr, t_cols, t1_idx,
                              t2_idx, depth):
    log(""); log("="*60)
    log("OBJ-12 — INTEGRATED DRUG PRIORITY MAP")
    log("="*60)

    d = depth.reindex(t_cols).dropna()
    q75 = d.quantile(0.75)

    strata = {}
    if t1_idx is not None and len(t1_idx) >= 5:
        strata["Type1_all"] = t1_idx
        t1_q4 = t1_idx.intersection(
            d[d >= q75].index)
        if len(t1_q4) >= 5:
            strata["Type1_Q4"] = t1_q4
    if t2_idx is not None and len(t2_idx) >= 5:
        strata["Type2_all"] = t2_idx
        if "FH" in expr.index and \
                "EZH2" in expr.index:
            d_t2 = d.reindex(t2_idx).dropna()
            fh_t2 = gv("FH", expr, t_cols,
                        d_t2.index)
            ez_t2 = gv("EZH2", expr, t_cols,
                        d_t2.index)
            if fh_t2 is not None \
                    and ez_t2 is not None:
                cimp_t2 = (
                    (fh_t2 <= fh_t2.quantile(0.20)) &
                    (ez_t2 >= ez_t2.quantile(0.80)))
                cimp_idx = d_t2.index[
                    cimp_t2.values]
                if len(cimp_idx) >= 3:
                    strata["CIMP"] = cimp_idx

    log(f"  Strata: "
        f"{[(k,len(v)) for k,v in strata.items()]}")

    rows = []
    for drug, gene in DRUG_GENES.items():
        if gene not in expr.index: continue
        g_ = pd.Series(
            expr.loc[gene, t_cols].values,
            index=t_cols)
        row = {"drug": drug, "gene": gene}
        for stratum, idx in strata.items():
            g_s = g_.reindex(idx).dropna()
            row[f"mean_{stratum}"] = g_s.mean()
        rows.append(row)

    df = pd.DataFrame(rows)
    df.to_csv(
        os.path.join(RESULTS_DIR,
                     "drug_priority_map.csv"),
        index=False)

    # Print
    mean_cols = [c for c in df.columns
                 if c.startswith("mean_")]
    log(f"\n  {'Drug':<22} "
        + "  ".join(f"{c.replace('mean_',''):>12}"
                    for c in mean_cols))
    log(f"  {'─'*80}")
    for _, row in df.iterrows():
        vals = "  ".join(
            f"{row.get(c, np.nan):>12.3f}"
            for c in mean_cols)
        log(f"  {row['drug']:<22} {vals}")

    # Priority summary
    log("")
    log("  PRIORITY SUMMARY:")
    log("  ┌───────────────────────────────────────────"
        "────────────────────┐")
    log("  │ TYPE 1 PRCC (FA-1 — biliary)               "
        "                   │")
    log("  │   First line: Savolitinib (MET-driven)      "
        "                   │")
    log("  │   Targeted:   ERBB2 (IHC2+ continuous)      "
        "                  │")
    log("  │   Chromatin:  Tazemetostat (EZH2)            "
        "                  │")
    log("  │   Immune Q4:  ARG1i + anti-PD-1             "
        "                   │")
    log("  │   MCT4 note:  SLC16A1 low in Q4-T1 —       "
        "                   │")
    log("  │               lactate buffer co-strategy    "
        "                   │")
    log("  ├───────────────────────────────────────────"
        "────────────────────┤")
    log("  │ TYPE 2 PRCC (FA-2 — eosinophilic)           "
        "                   │")
    log("  │   Backbone:   Cabozantinib (broadest TKI)   "
        "                   │")
    log("  │   Cell cycle: CDK4/6i (CDKN2A-driven)       "
        "                  │")
    log("  │   Chromatin:  Tazemetostat (EZH2 applies)   "
        "                  │")
    log("  │   Immune:     ARG1i + anti-PD-1 (Q4 T2)    "
        "                   │")
    log("  │   CIMP subset: αKG + Tazemetostat           "
        "                   │")
    log("  ├───────────────────────────────────────────"
        "────────────────────┤")
    log("  │ CIMP (FA-CIMP — FH-HLRCC extreme)           "
        "                   │")
    log("  │   Priority 1: αKG + Tazemetostat           "
        "                    │")
    log("  │   Priority 2: CDK4/6i (MKI67-high)         "
        "                    │")
    log("  │   Priority 3: Entinostat + anti-PD-1        "
        "                   │")
    log("  │               (HLA-A low)                  "
        "                    │")
    log("  │   Mandatory:  Germline FH testing           "
        "                    │")
    log("  └───────────────────────────────────────────"
        "────────────────────┘")

# ═══════════════════════════════════════════════════════════════
# HELPER: BUILD OS VECTORS
# ═══════════════════════════════════════════════════════════════

def _build_os(d, surv):
    if surv is None:
        return (pd.Series(np.nan, index=d.index),
                pd.Series(np.nan, index=d.index))
    patients = [s[:12] for s in d.index]

    def _g(pid, col):
        if pid not in surv.index: return np.nan
        v = surv.at[pid, col]
        if isinstance(v, (pd.Series, list,
                           np.ndarray)):
            v = pd.Series(v).iloc[0]
        return v

    time_col = next(
        (c for c in ["OS.time","OS_time",
                      "days_to_death"]
         if c in surv.columns), None)
    event_col = next(
        (c for c in ["OS","vital_status","dead"]
         if c in surv.columns), None)

    if time_col is None or event_col is None:
        return (pd.Series(np.nan, index=d.index),
                pd.Series(np.nan, index=d.index))

    os_t = pd.Series(
        [pd.to_numeric(_g(p, time_col),
                       errors="coerce")
         for p in patients],
        index=d.index, dtype=float)
    os_e_raw = pd.Series(
        [_g(p, event_col) for p in patients],
        index=d.index)
    os_e = os_e_raw.map(
        lambda x: 1 if str(x).lower() in
        ["dead","deceased","1","true","yes"]
        else (0 if str(x).lower() in
              ["alive","living","0","false","no"]
              else np.nan)
    ).astype(float)
    return os_t, os_e

# ═══════════════════════════════════════════════════════════════
# FIGURE — 12 panels
# ═══════════════════════════════════════════════════════════════

def generate_figure(depth, expr, t_cols, n_cols,
                     t1_idx, t2_idx,
                     os_res_t1, os_data_t1,
                     os_res_t2,
                     os_res_12, top_t1, top_t2,
                     ti_fa2, fa2_pos, fa2_neg):
    log(""); log("="*60)
    log("GENERATING FIGURE — SCRIPT 5"); log("="*60)

    d = depth.reindex(t_cols).dropna()

    fig = plt.figure(figsize=(26, 30))
    gs  = gridspec.GridSpec(
        4, 3, figure=fig,
        hspace=0.55, wspace=0.40)

    COLORS = {
        "T1":   "#2980B9",
        "T2":   "#C0392B",
        "CIMP": "#8E44AD",
        "norm": "#27AE60",
    }

    # ── A: Type 1 vs Type 2 KM ───────────────────────────────
    ax = fig.add_subplot(gs[0, 0])
    if os_res_12 is not None:
        for (t, s), col, lab in [
            (os_res_12["km_T1"],
             COLORS["T1"], "Type 1"),
            (os_res_12["km_T2"],
             COLORS["T2"], "Type 2"),
        ]:
            ax.step(t/365, s, where="post",
                    color=col, label=lab, lw=2)
        p = os_res_12.get("p_12", np.nan)
        ax.set_title(
            f"A: Type 1 vs Type 2 OS\n"
            f"{fmt_p(p)}",
            fontsize=9, fontweight="bold")
        ax.legend(fontsize=7)
        ax.set_ylim(0, 1.05)
        ax.set_xlabel("Years")
        ax.set_ylabel("Survival")
    else:
        ax.set_title("A: T1 vs T2 OS",
                     fontsize=9, fontweight="bold")
        ax.text(0.5, 0.5, "Pending",
                ha="center", va="center",
                transform=ax.transAxes)

    # ── B: FA-1 TI within Type 1 KM ──────────────────────────
    ax = fig.add_subplot(gs[0, 1])
    if os_res_t1 and "km_ti_hi_T1" in os_res_t1:
        for (t, s), col, lab in [
            (os_res_t1["km_ti_hi_T1"],
             COLORS["T2"], "TI-high"),
            (os_res_t1["km_ti_lo_T1"],
             COLORS["T1"], "TI-low"),
        ]:
            ax.step(t/365, s, where="post",
                    color=col, label=lab, lw=2)
        p = os_res_t1.get("S5P1_p", np.nan)
        ax.set_title(
            f"B: FA-1 TI OS (Type 1 only)\n"
            f"{fmt_p(p)}",
            fontsize=9, fontweight="bold")
        ax.legend(fontsize=7)
        ax.set_ylim(0, 1.05)
        ax.set_xlabel("Years")
        ax.set_ylabel("Survival")
    else:
        ax.set_title("B: FA-1 TI OS (T1 only)",
                     fontsize=9, fontweight="bold")

    # ── C: Depth by subtype violin/box ───────────────────────
    ax = fig.add_subplot(gs[0, 2])
    data_by_type = []
    labels_ax   = []
    if t1_idx is not None:
        data_by_type.append(
            depth.reindex(t1_idx).dropna().values)
        labels_ax.append("Type 1")
    if t2_idx is not None:
        data_by_type.append(
            depth.reindex(t2_idx).dropna().values)
        labels_ax.append("Type 2")

    # Normal tissue
    if n_cols is not None and len(n_cols) > 0:
        # Use S1 depth scores — normal not scored
        # Use proxy: mean of FA1_NEG genes
        neg_av = [g for g in FA1_NEG
                  if g in expr.index]
        if neg_av:
            norm_sc = (expr.loc[neg_av, n_cols]
                       .mean(axis=0))
            # Normalise to same scale as depth
            norm_proxy = norm01(norm_sc.values)
            # Invert — high normal pole = shallow
            norm_proxy = 1 - norm_proxy
            data_by_type.insert(0, norm_proxy)
            labels_ax.insert(0, "Normal")

    if data_by_type:
        bp = ax.boxplot(data_by_type,
                        labels=labels_ax,
                        patch_artist=True,
                        notch=False)
        colors_bp = ([COLORS["norm"]]
                     if len(data_by_type) == 3
                     else []) + \
                    [COLORS["T1"], COLORS["T2"]]
        colors_bp = colors_bp[:len(data_by_type)]
        for patch, col in zip(bp["boxes"],
                               colors_bp):
            patch.set_facecolor(col)
            patch.set_alpha(0.7)
        ax.set_ylabel("Depth Score")
        ax.set_title(
            "C: Depth by Subtype\n"
            "(Normal / Type1 / Type2)",
            fontsize=9, fontweight="bold")

    # ── D: FA-1 top 15 vs FA-2 top 15 comparison ─────────────
    ax = fig.add_subplot(gs[1, 0])
    if top_t1 is not None and top_t2 is not None:
        t1_g = [g for g, r, p in top_t1[:15]]
        t2_g = [g for g, r, p in top_t2[:15]]
        t1_r = {g: r for g, r, p in top_t1[:15]}
        t2_r = {g: r for g, r, p in top_t2[:15]}
        all_g = list(dict.fromkeys(t1_g + t2_g))
        x = [t1_r.get(g, 0) for g in all_g]
        y = [t2_r.get(g, 0) for g in all_g]
        c = ["#C0392B" if g in t2_r and g not in t1_r
             else "#2980B9" if g in t1_r
             and g not in t2_r
             else "#E67E22" for g in all_g]
        ax.scatter(x, y, c=c, s=30, alpha=0.8)
        for g, xi, yi in zip(all_g, x, y):
            if abs(xi) > 0.2 or abs(yi) > 0.2:
                ax.annotate(g, (xi, yi),
                            fontsize=6,
                            xytext=(3, 3),
                            textcoords="offset points")
        ax.axhline(0, color="k", lw=0.5)
        ax.axvline(0, color="k", lw=0.5)
        ax.set_xlabel("r(depth) in Type 1",
                      fontsize=9)
        ax.set_ylabel("r(depth) in Type 2",
                      fontsize=9)
        ax.set_title("D: FA-1 vs FA-2 Correlates\n"
                     "(blue=T1, red=T2, orange=shared)",
                     fontsize=9, fontweight="bold")

    # ── E: SLC16A1 vs LDHA by subtype ────────────────────────
    ax = fig.add_subplot(gs[1, 1])
    if "SLC16A1" in expr.index and \
            "LDHA" in expr.index:
        slc = gv("SLC16A1", expr, t_cols, d.index)
        ldha = gv("LDHA",   expr, t_cols, d.index)
        if slc is not None and ldha is not None:
            colours_e = []
            for s in d.index:
                if t1_idx is not None and s in t1_idx:
                    colours_e.append(COLORS["T1"])
                elif t2_idx is not None \
                        and s in t2_idx:
                    colours_e.append(COLORS["T2"])
                else:
                    colours_e.append("#95A5A6")
            ax.scatter(ldha.values, slc.values,
                       c=colours_e, s=6, alpha=0.5)
            r_ls, _ = safe_r(ldha.values, slc.values)
            ax.set_xlabel("LDHA (production)")
            ax.set_ylabel("SLC16A1/MCT4 (export)")
            ax.set_title(
                f"E: LDHA vs MCT4\n"
                f"r={r_ls:+.3f} "
                f"(blue=T1, red=T2)",
                fontsize=9, fontweight="bold")

    # ── F: Dual suppression score by depth ───────────────────
    ax = fig.add_subplot(gs[1, 2])
    dual_path = os.path.join(
        RESULTS_DIR, "dual_suppression_score.csv")
    if os.path.exists(dual_path):
        dual_df = pd.read_csv(dual_path,
                               index_col="sample_id")
        ds = dual_df["dual_suppression"].reindex(
            d.index)
        ax.scatter(d.values, ds.values,
                   c=d.values, cmap="RdBu_r",
                   s=8, alpha=0.6)
        r_ds, _ = safe_r(ds.values, d.values)
        ax.set_xlabel("Depth")
        ax.set_ylabel("Dual suppression\n"
                      "(ARG1 + MCT4-loss)")
        ax.set_title(
            f"F: Dual T Cell Suppression\n"
            f"r(depth)={r_ds:+.3f}",
            fontsize=9, fontweight="bold")

    # ── G: FA-2 TI OS ─────────────────────────────────────────
    ax = fig.add_subplot(gs[2, 0])
    if (os_res_t2 is not None and
            "fa2_ti_p" in os_res_t2 and
            ti_fa2 is not None):
        p_fa2 = os_res_t2.get("fa2_ti_p", np.nan)
        ax.set_title(
            f"G: FA-2 TI OS (Type 2 only)\n"
            f"{fmt_p(p_fa2)}\n"
            f"({fa2_pos} – {fa2_neg})",
            fontsize=8, fontweight="bold")
        ax.text(0.5, 0.5,
                f"p={fmt_p(p_fa2)}\n"
                f"TI = {fa2_pos}\n– {fa2_neg}",
                ha="center", va="center",
                transform=ax.transAxes,
                fontsize=10)
    else:
        ax.set_title("G: FA-2 TI OS",
                     fontsize=9, fontweight="bold")
        ax.text(0.5, 0.5, "Insufficient\nType 2 OS",
                ha="center", va="center",
                transform=ax.transAxes)

    # ── H: Drug OS Type 1 vs Type 2 heatmap ──────────────────
    ax = fig.add_subplot(gs[2, 1])
    try:
        d1_os = pd.read_csv(os.path.join(
            RESULTS_DIR, "drug_OS_type1.csv"))
        d2_os = pd.read_csv(os.path.join(
            RESULTS_DIR, "drug_OS_type2.csv"))
        merged = pd.merge(
            d1_os[["drug","p_logrank"]].rename(
                columns={"p_logrank": "p_T1"}),
            d2_os[["drug","p_logrank"]].rename(
                columns={"p_logrank": "p_T2"}),
            on="drug", how="outer")
        merged = merged.dropna(
            subset=["p_T1","p_T2"])
        if len(merged) > 0:
            merged = merged.sort_values("p_T1")
            nlp_T1 = -np.log10(
                merged["p_T1"].clip(1e-10,1))
            nlp_T2 = -np.log10(
                merged["p_T2"].clip(1e-10,1))
            x = np.arange(len(merged))
            w = 0.35
            ax.bar(x - w/2, nlp_T1,
                   w, color=COLORS["T1"],
                   alpha=0.8, label="Type 1")
            ax.bar(x + w/2, nlp_T2,
                   w, color=COLORS["T2"],
                   alpha=0.8, label="Type 2")
            ax.axhline(-np.log10(0.05),
                        color="k", lw=0.8,
                        ls="--")
            ax.set_xticks(x)
            ax.set_xticklabels(
                merged["drug"].values,
                rotation=45, ha="right",
                fontsize=6)
            ax.set_ylabel("-log10(p)")
            ax.legend(fontsize=7)
            ax.set_title(
                "H: Drug OS T1 vs T2",
                fontsize=9, fontweight="bold")
    except Exception:
        ax.set_title("H: Drug OS T1 vs T2",
                     fontsize=9, fontweight="bold")

    # ── I: Normal pole expression T vs N ─────────────────────
    ax = fig.add_subplot(gs[2, 2])
    norm_path = os.path.join(
        RESULTS_DIR, "normal_pole_comparison.csv")
    if os.path.exists(norm_path):
        ndf = pd.read_csv(norm_path).dropna()
        if len(ndf) > 0:
            x = np.arange(len(ndf))
            w = 0.25
            ax.bar(x - w, ndf["mean_normal"],
                   w, color=COLORS["norm"],
                   alpha=0.8, label="Normal")
            ax.bar(x,     ndf["mean_Type1"],
                   w, color=COLORS["T1"],
                   alpha=0.8, label="Type 1")
            ax.bar(x + w, ndf["mean_Type2"],
                   w, color=COLORS["T2"],
                   alpha=0.8, label="Type 2")
            ax.set_xticks(x)
            ax.set_xticklabels(
                ndf["gene"].values,
                rotation=45, ha="right",
                fontsize=6)
            ax.legend(fontsize=7)
            ax.set_title(
                "I: Normal Pole Loss\n"
                "(Normal / T1 / T2)",
                fontsize=9, fontweight="bold")
    else:
        ax.set_title("I: Normal Pole",
                     fontsize=9, fontweight="bold")

    # ── J: CIMP within Type 2 profile ────────────────────────
    ax = fig.add_subplot(gs[3, 0])
    if t2_idx is not None and \
            "FH" in expr.index and \
            "EZH2" in expr.index:
        d_t2 = depth.reindex(t2_idx).dropna()
        fh_t2 = gv("FH", expr, t_cols,
                   d_t2.index)
        ax.scatter(
            d_t2.values, fh_t2.values,
            c=["#8E44AD"
               if fh_t2.iloc[i] <=
               fh_t2.quantile(0.20) else
               "#C0392B"
               for i in range(len(fh_t2))],
            s=10, alpha=0.6)
        ax.set_xlabel("Depth (biliary axis)")
        ax.set_ylabel("FH expression")
        ax.set_title("J: CIMP Proxy in Type 2\n"
                     "(purple=FH-low CIMP)",
                     fontsize=9, fontweight="bold")

    # ── K: Drug priority map summary ─────────────────────────
    ax = fig.add_subplot(gs[3, 1])
    pri_path = os.path.join(RESULTS_DIR,
                             "drug_priority_map.csv")
    if os.path.exists(pri_path):
        pdf = pd.read_csv(pri_path)
        mc  = [c for c in pdf.columns
               if c.startswith("mean_")]
        if mc and len(pdf) > 0:
            mat = pdf.set_index("drug")[mc]
            mat_n = mat.apply(
                lambda r: norm01(r.values),
                axis=1,
                result_type="broadcast")
            im = ax.imshow(
                mat_n.values.astype(float),
                aspect="auto", cmap="RdBu_r",
                vmin=0, vmax=1)
            ax.set_yticks(range(len(mat_n)))
            ax.set_yticklabels(mat_n.index,
                                fontsize=7)
            ax.set_xticks(range(len(mc)))
            ax.set_xticklabels(
                [c.replace("mean_","")
                 for c in mc],
                fontsize=7, rotation=30,
                ha="right")
            plt.colorbar(im, ax=ax, shrink=0.6)
            ax.set_title("K: Drug Priority Map\n"
                         "(row-normalised)",
                         fontsize=9,
                         fontweight="bold")

    # ── L: Scorecard ──────────────────────────────────────────
    ax = fig.add_subplot(gs[3, 2])
    ax.axis("off")
    txt = (
        "PRCC Script 5 | 2026-03-02\n"
        "OrganismCore\n"
        "─────────────────────────────\n"
        "S5-P1  FA-1 TI OS Type1 p<0.05\n"
        "S5-P2  FA-1 Q4>Q1 OS Type1\n"
        "S5-P3  Type2 worse OS than T1\n"
        "S5-P4  CA9 worse OS in Type1\n"
        "S5-P5  FA-2 distinct top genes\n"
        "S5-P6  CDKN2A stronger in T2\n"
        "S5-P7  Normal pole loss in T2\n"
        "S5-P8  EZH2 OS in Type 2\n"
        "S5-P9  SLC16A1 fall steeper T1\n"
        "S5-P10 Dual score > ARG1/MCT4 alone\n"
        "S5-P11 RUNX1 r>0.40 in ccRCC\n"
        "S5-P12 GOT1  r<-0.40 in ccRCC\n"
        "─────────────────────────────\n"
        "TWO FALSE ATTRACTORS:\n"
        "FA-1 Type1 biliary\n"
        "FA-2 Type2 eosinophilic\n"
        "FA-CIMP TCA-extreme"
    )
    ax.text(0.05, 0.95, txt,
            transform=ax.transAxes,
            fontsize=7,
            verticalalignment="top",
            fontfamily="monospace",
            bbox=dict(boxstyle="round",
                      facecolor="#F0F4F8",
                      alpha=0.8))
    ax.set_title("L: Script 5 Scorecard",
                 fontsize=9, fontweight="bold")

    fig.suptitle(
        "PRCC False Attractor — Script 5\n"
        "Type 1 vs Type 2 · FA-2 · Dual Suppression "
        "· Cross-Cancer",
        fontsize=12, fontweight="bold", y=0.998)

    out = os.path.join(RESULTS_DIR,
                        "prcc_script5_figure.pdf")
    fig.savefig(out, bbox_inches="tight", dpi=150)
    plt.close(fig)
    log(f"  Figure saved: {out}")

# ═══════════════════════════════════════════════════════════════
# SCORECARD
# ═══════════════════════════════════════════════════════════════

def print_scorecard():
    full = "\n".join(log_lines)
    log(""); log("="*60)
    log("SCRIPT 5 — FINAL SCORECARD"); log("="*60)
    checks = [
        ("S5-P1  FA-1 TI OS in Type 1",
         "S5-P1 CONFIRMED", "S5-P1 NOT CONFIRMED"),
        ("S5-P2  FA-1 Q4>Q1 OS in Type 1",
         "S5-P2 CONFIRMED", "S5-P2 NOT CONFIRMED"),
        ("S5-P3  Type 2 worse OS",
         "S5-P3 CONFIRMED", "S5-P3 NOT CONFIRMED"),
        ("S5-P4  CA9 worse OS in Type 1",
         "S5-P4 CONFIRMED", "S5-P4 NOT CONFIRMED"),
        ("S5-P5  FA-2 distinct top genes",
         "S5-P5 CONFIRMED", "S5-P5 NOT CONFIRMED"),
        ("S5-P6  CDKN2A stronger in Type 2",
         "S5-P6 CONFIRMED", "S5-P6 NOT CONFIRMED"),
        ("S5-P7  Normal pole loss in Type 2",
         "S5-P7 CONFIRMED", "S5-P7 NOT CONFIRMED"),
        ("S5-P8  EZH2 OS in Type 2",
         "S5-P8 CONFIRMED", "S5-P8 NOT CONFIRMED"),
        ("S5-P9  SLC16A1 steeper in Type 1",
         "S5-P9 CONFIRMED", "S5-P9 NOT CONFIRMED"),
        ("S5-P10 Dual score better than solo",
         "S5-P10 CONFIRMED", "S5-P10 NOT CONFIRMED"),
        ("S5-P11 RUNX1 in ccRCC",
         "S5-P11 CONFIRMED", "S5-P11 NOT CONFIRMED"),
        ("S5-P12 GOT1 in ccRCC",
         "S5-P12 CONFIRMED", "S5-P12 NOT CONFIRMED"),
    ]
    confirmed = 0
    for label, pos, neg in checks:
        if pos in full:
            verdict = "CONFIRMED ✓"; confirmed += 1
        elif neg in full:
            verdict = "NOT CONFIRMED ✗"
        else:
            verdict = "CHECK LOG"
        log(f"  {label:<44}  {verdict}")
    log(f"\n  OVERALL: {confirmed}/{len(checks)}")

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    log("="*60)
    log("PRCC FALSE ATTRACTOR — SCRIPT 5")
    log("OrganismCore | Document 95e | 2026-03-02")
    log("Author: Eric Robert Lawson")
    log("="*60)
    log("")
    log("MAJOR REVISION: TWO FALSE ATTRACTOR MODEL")
    log("FA-1 = Type 1 (biliary) — characterised S1-4")
    log("FA-2 = Type 2 (eosinophilic) — THIS SCRIPT")
    log("12 predictions — S5-P1 through S5-P12")
    log("")

    # ── Load ──────────────────────────────────────────────────
    depth, ti = load_all()

    log(""); log("="*60)
    log("LOADING EXPRESSION MATRICES"); log("="*60)
    expr, t_cols, n_cols = load_expr_matrix(
        KIRP_EXPR, "PRCC KIRP")

    expr_kirc = t_cols_kirc = None
    if os.path.exists(KIRC_EXPR):
        expr_kirc, t_cols_kirc, _ = \
            load_expr_matrix(KIRC_EXPR, "ccRCC KIRC")
    else:
        log(f"  ccRCC matrix not found: {KIRC_EXPR}")
        log("  S5-P11/P12 will be DEFERRED.")

    surv     = load_survival()
    subtypes = load_subtype_labels()

    # Recompute TI if needed
    if ti is None and "KRT19" in expr.index \
            and "SLC22A6" in expr.index:
        d_r = depth.reindex(t_cols).dropna()
        krt = gv("KRT19",   expr, t_cols, d_r.index)
        slc = gv("SLC22A6", expr, t_cols, d_r.index)
        ti  = pd.Series(
            norm01(krt.values) - norm01(slc.values),
            index=d_r.index, name="TI")
        log(f"  TI recomputed: n={len(ti)}")

    # ── OBJ-1: Subtype split ──────────────────────────────────
    t1_idx, t2_idx, unk_idx, labels = \
        obj1_subtype_split(depth, subtypes, t_cols)

    # ── OBJ-2: FA-1 OS ───────────────────────────────────────
    os_res_t1, os_data_t1 = obj2_fa1_os(
        depth, ti, expr, t_cols, t1_idx, surv)

    # ── OBJ-3/4: FA-2 characterisation ───────────────────────
    fa2_result = obj3_4_fa2_characterisation(
        depth, expr, t_cols, n_cols, t1_idx, t2_idx)
    if fa2_result[0] is not None:
        ti_fa2, fa2_pos, fa2_neg, top_t1, top_t2 = \
            fa2_result
    else:
        ti_fa2  = None
        fa2_pos = fa2_neg = None
        top_t1  = fa2_result[3]
        top_t2  = fa2_result[4]

    # ── OBJ-5: FA-2 OS ───────────────────────────────────────
    os_res_t2, _ = obj5_fa2_os(
        depth, ti_fa2, expr, t_cols, t2_idx, surv)

    # ── OBJ-6/7: SLC16A1 + dual suppression ──────────────────
    obj6_7_slc16a1_dual(
        depth, expr, t_cols, t1_idx, t2_idx, surv)

    # ── OBJ-8: CIMP within Type 2 ────────────────────────────
    obj8_cimp_within_type2(
        depth, expr, t_cols, t2_idx, surv)

    # ── OBJ-9: Cross-cancer ───────────────────────────────────
    obj9_cross_cancer(
        expr, t_cols, depth,
        expr_kirc, t_cols_kirc)

    # ── OBJ-10: Type 1 vs Type 2 OS ──────────────────────────
    os_res_12 = obj10_type1_vs_type2_os(
        depth, expr, t_cols, t1_idx, t2_idx, surv)

    # ── OBJ-12: Drug priority map ─────────────────────────────
    obj12_drug_priority_map(
        expr, t_cols, t1_idx, t2_idx, depth)

    # ── Figure ────────────────────────────────────────────────
    generate_figure(
        depth, expr, t_cols, n_cols,
        t1_idx, t2_idx,
        os_res_t1, os_data_t1,
        os_res_t2, os_res_12,
        top_t1, top_t2,
        ti_fa2, fa2_pos, fa2_neg)

    print_scorecard()
    write_log()

    log("")
    log("="*60)
    log("SCRIPT 5 COMPLETE")
    log(f"Results: {RESULTS_DIR}")
    log(f"Log:     {LOG_FILE}")
    log("Next: Document 95e (results)")
    log("="*60)


if __name__ == "__main__":
    main()
