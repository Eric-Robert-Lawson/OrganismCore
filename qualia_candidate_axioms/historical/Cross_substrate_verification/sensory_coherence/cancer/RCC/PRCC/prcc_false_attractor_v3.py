"""
PRCC False Attractor — Script 3
SURVIVAL / SUBTYPES / DECONVOLUTION / MUTATIONS / CROSS-CANCER

Framework: OrganismCore
Document 95c-pre | 2026-03-02
Author: Eric Robert Lawson

═══════════════════════════════════════════════════════════════
PREDICTIONS LOCKED — 2026-03-02 — BEFORE SCRIPT 3

S3-P1: Formal Type 1 / Type 2 annotation
       will confirm Type 2 depth > Type 1 depth
       MW p < 0.05

S3-P2: Immune deconvolution (ESTIMATE or TIMER2)
       Stromal score r(TWIST1) > 0.40
       confirming TWIST1 = stromal activation
       not epithelial EMT

S3-P3: ARG1 Q4/Q1 > 1.5 confirmed significant
       (p < 0.05) when M2 macrophage
       deconvolution is applied

S3-P4: Axis A and Axis B are independent OS
       predictors (partial r > 0.20 each,
       after controlling for the other)

S3-P5: PBRM1 mutation status co-segregates with
       SETD2 co-mutation and deeper Axis B scores
       (mutation-driven, not RNA-driven)

S3-P6: PDK1 co-elevated with CA9/SLC2A1/LDHA
       as a coherent hypoxia module
       (all pairwise r > 0.50)

S3-P7: CDKN2A/CDK4 co-occurrence at sample level
       confirmed (NOT anti-correlated)

S3-P8: TI (KRT19/SLC22A6) predicts OS
       High TI = worse OS  p < 0.05

═══════════════════════════════════════════════════════════════
OBJECTIVES:
  OBJ-1:  Formal Type 1/Type 2/CIMP annotation
  OBJ-2:  ESTIMATE proxy deconvolution
  OBJ-3:  TWIST1 stromal test
  OBJ-4:  Overall survival with TI
  OBJ-5:  Dual OS: Axis A + Axis B
  OBJ-6:  PBRM1 mutation from cBioPortal
  OBJ-7:  PDK1/CA9 hypoxia module + isoform conflict
  OBJ-8:  CDKN2A/CDK4 paradox at sample level
  OBJ-9:  Cross-cancer comparison
  OBJ-10: Drug target OS stratification
  OBJ-11: ARG1/M2 deconvolution
  OBJ-12: CIMP subgroup isolation

FRAMEWORK CORRECTIONS APPLIED (95-LC / 95-DLC):
  FC-1: Subtype annotation from GDC KIRP_2015
  FC-2: αKG novelty = continuous FH stratification
  FC-3: CA9 = HIF protein not HIF RNA
  FC-4: SAVOIR 27% ORR as clinical context
  FC-5: CDKN2A methylation (CIMP) vs RNA (non-CIMP)
  DC-1: Anti-CD25 downgraded
  DC-2: Anti-CSF1R → repolarisation not depletion
  DC-3: PDK1 isoform conflict flagged
  DC-4: ERBB2 IHC 2+ not FISH criterion
  DC-5: αKG AIM2/PANoptosis safety monitoring
═══════════════════════════════════════════════════════════════
"""

import os
import gzip
import itertools
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.stats import pearsonr, mannwhitneyu, chi2_contingency
import warnings
warnings.filterwarnings("ignore")

# ═══════════════════════════════════════════════════════════════
# PATHS
# ═══════════════════════════════════════════════════════════════

BASE_DIR    = "./prcc_false_attractor/"
S1_DIR      = os.path.join(BASE_DIR, "results_s1/")
S2_DIR      = os.path.join(BASE_DIR, "results_s2/")
RESULTS_DIR = os.path.join(BASE_DIR, "results_s3/")
LOG_FILE    = os.path.join(RESULTS_DIR, "s3_log.txt")

EXPR_PATH   = os.path.join(BASE_DIR, "TCGA_KIRP_HiSeqV2.gz")
CLIN_PATH   = os.path.join(BASE_DIR, "KIRP_clinicalMatrix.tsv")
CBIO_PATH   = os.path.join(BASE_DIR, "KIRP_cbio_clinical.tsv")
S1_DEPTH    = os.path.join(S1_DIR,   "depth_scores_tcga.csv")
S2_TI       = os.path.join(S2_DIR,   "transition_index.csv")
MUT_CACHE   = os.path.join(BASE_DIR, "KIRP_mutations_cbio.json")
SUB_CACHE   = os.path.join(BASE_DIR, "KIRP_subtypes.tsv")

os.makedirs(RESULTS_DIR, exist_ok=True)

# ═══════════════════════════════════════════════════════════════
# GENE PANELS
# ═══════════════════════════════════════════════════════════════

STROMAL_PROXY = [
    "ACTA2","FAP","COL1A1","COL1A2","FN1",
    "PDGFRB","PDGFRA","DCN","LUM","SPARC",
    "THY1","S100A4","TAGLN","MYH11","CNN1",
    "BGN","POSTN","VCAN","MFAP5","AEBP1",
]
IMMUNE_PROXY = [
    "CD2","CD3D","CD3E","CD3G","CD8A",
    "CD8B","CD4","CD19","CD79A","CD79B",
    "MS4A1","IGHG1","IGHG2",
    "CD14","CD68","CD163","CSF1R","FCGR3A",
]
HYPOXIA_MODULE = [
    "CA9","SLC2A1","LDHA","PDK1","VEGFA",
    "SLC16A1","ALDOA","ENO1","PFKL","HK2",
]
PDK_ISOFORMS   = ["PDK1","PDK2","PDK3","PDK4"]
MUT_GENES      = [
    "PBRM1","SETD2","FH","BAP1","VHL",
    "MET","NF2","CDKN2A","TP53","ARID1A",
    "KDM6A","SMARCA4","SMARCB1",
]
PRCC_TI_POS    = ["KRT19","ERBB2","KRT7","SOX4","AXL"]
PRCC_TI_NEG    = ["SLC22A6","FABP1","SLC34A1","GPX3","CUBN"]
CCRCC_TI_POS   = ["GOT1","RUNX1","LOXL2","TGFB1"]
CCRCC_TI_NEG   = ["FBP1","UMOD","SLC22A6","MIOX"]

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
    "ARG1_macrophage":   "ARG1",
}

# ═══════════════════════════════════════════════════════════════
# LOGGING
# ═══════════════════════════════���═══════════════════════════════

log_lines = []

def log(msg=""):
    print(msg)
    log_lines.append(str(msg))

def write_log():
    with open(LOG_FILE, "w") as f:
        f.write("\n".join(log_lines))

def fmt_p(p):
    if p is None or (isinstance(p, float) and np.isnan(p)):
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
    x = np.asarray(x, float); y = np.asarray(y, float)
    mask = np.isfinite(x) & np.isfinite(y)
    if mask.sum() < 5: return np.nan, np.nan
    return pearsonr(x[mask], y[mask])

def safe_mwu(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    a = a[np.isfinite(a)];    b = b[np.isfinite(b)]
    if len(a) < 3 or len(b) < 3: return np.nan, np.nan
    return mannwhitneyu(a, b, alternative="two-sided")

def safe_logrank(t1, e1, t2, e2):
    t1 = np.asarray(t1, float); e1 = np.asarray(e1, float)
    t2 = np.asarray(t2, float); e2 = np.asarray(e2, float)
    try:
        from lifelines.statistics import logrank_test
        res = logrank_test(t1, t2,
                           event_observed_A=e1,
                           event_observed_B=e2)
        return res.test_statistic, res.p_value
    except ImportError:
        pass
    # Gehan-Breslow fallback
    all_t = np.sort(np.unique(np.concatenate([t1, t2])))
    O1 = O2 = E1 = E2 = 0.0
    for t in all_t:
        n1 = np.sum(t1 >= t); n2 = np.sum(t2 >= t)
        d1 = np.sum((t1 == t) & (e1 == 1))
        d2 = np.sum((t2 == t) & (e2 == 1))
        n = n1 + n2; d = d1 + d2
        if n < 2 or d == 0: continue
        O1 += d1; O2 += d2
        E1 += n1 * d / n; E2 += n2 * d / n
    if E1 <= 0 or E2 <= 0: return np.nan, np.nan
    chi = (O1 - E1)**2 / E1 + (O2 - E2)**2 / E2
    from scipy.stats import chi2
    return chi, 1 - chi2.cdf(chi, df=1)

def kaplan_meier(t, e):
    t = np.asarray(t, float); e = np.asarray(e, float)
    order = np.argsort(t); t = t[order]; e = e[order]
    at_risk = len(t); s = 1.0
    times = [0]; surv = [1.0]
    for i in range(len(t)):
        if e[i] == 1:
            s *= (1 - 1.0 / at_risk)
            times.append(t[i]); surv.append(s)
        at_risk -= 1
    return np.array(times), np.array(surv)

# ═══════════════════════════════════════════════════════════════
# LOAD S1 / S2 OUTPUTS
# ═══════════════════════════════════════════════════════════════

def load_s1_s2():
    log(""); log("=" * 60)
    log("LOADING SCRIPT 1 AND SCRIPT 2 OUTPUTS")
    log("=" * 60)
    if not os.path.exists(S1_DEPTH):
        log(f"  ERROR: S1 depth not found: {S1_DEPTH}")
        return None, None
    df1   = pd.read_csv(S1_DEPTH)
    depth = pd.Series(df1["depth_score"].values,
                      index=df1["sample_id"].values,
                      name="s1_depth")
    ti = None
    if os.path.exists(S2_TI):
        df2 = pd.read_csv(S2_TI)
        ti  = pd.Series(df2["TI"].values,
                        index=df2["sample_id"].values,
                        name="TI")
        log(f"  S1 depth: n={len(depth)}")
        log(f"  S2 TI:    n={len(ti)}")
    else:
        log(f"  S2 TI not found — will recompute.")
    return depth, ti

# ═══════════════════════════════════════════════════════════════
# LOAD EXPRESSION
# ═══════════════════════════════════════════════════════════════

def load_expression():
    log(""); log("=" * 60)
    log("RELOAD EXPRESSION MATRIX"); log("=" * 60)
    open_fn = gzip.open if EXPR_PATH.endswith(".gz") else open
    with open_fn(EXPR_PATH, "rt") as fh:
        raw = pd.read_csv(fh, sep="\t", index_col=0)

    need = list(dict.fromkeys(
        STROMAL_PROXY + IMMUNE_PROXY + HYPOXIA_MODULE +
        PDK_ISOFORMS + PRCC_TI_POS + PRCC_TI_NEG +
        CCRCC_TI_POS + CCRCC_TI_NEG +
        list(DRUG_GENES.values()) +
        ["TWIST1","KRT19","SLC22A6","FH","OGDHL",
         "CDKN2A","CDK4","CCND1","EZH2","SETD2",
         "PBRM1","BAP1","ARID1A","MET","ERBB2",
         "KDM1A","TET2","B2M","HLA-A","IFI16",
         "ARG1","CD274","HAVCR2","FOXP3","IL2RA",
         "SUCLG1","GOT1","ACADM","FABP1","LDHB",
         "GPX3","SLC34A1","CUBN","SLC5A2",
         "MKI67","TOP2A","CDK6","CDKN2B",
         "KRT7","KRT8","KRT18","SOX4","AXL",
         "PROM1","EPCAM","ITGA3","HMOX1",
         "SLC13A2","SLC16A1","MIOX","LRP2",
         "RUNX1","LOXL2","TGFB1","FBP1","UMOD",
         "CPT1A","ATP5A1","ACAT1",
         "CA9","VHL","EPAS1","HIF1A","PDK1",
         "LDHA","SLC2A1","VEGFA",
         "CDKN1A","CDKN1B","CCNE1","CDC20",
         "CDH1","CDH2","ZEB1","SNAI1","SNAI2",
         "VIM","FN1","MRC1","IL10","CD86",
         "TNF","IL6","NOS2","IL1B","CXCL10",
         "IL12A","S100A4"]
    ))
    avail   = [g for g in need if g in raw.index]
    missing = [g for g in need if g not in raw.index]
    expr    = raw.loc[avail].copy()
    log(f"  Genes: {len(avail)}/{len(need)} available")
    if missing: log(f"  Missing: {missing}")

    sample_ids  = list(expr.columns)
    sample_type = []
    for s in sample_ids:
        parts = s.split("-")
        code  = parts[3][:2] if len(parts) >= 4 else "00"
        if   code == "01": sample_type.append("tumour")
        elif code == "11": sample_type.append("normal")
        else:              sample_type.append("other")

    meta   = pd.DataFrame({"sample_type": sample_type},
                           index=sample_ids)
    t_cols = expr.columns[
        meta.reindex(expr.columns)["sample_type"]
            .eq("tumour").values]
    n_cols = expr.columns[
        meta.reindex(expr.columns)["sample_type"]
            .eq("normal").values]
    log(f"  Tumour: n={len(t_cols)}  Normal: n={len(n_cols)}")
    return expr, t_cols, n_cols

# ═══════════════════════════════════════════════════════════════
# LOAD CLINICAL
# ═══════════════════════════════════════════════════════════════

def load_clinical():
    log(""); log("=" * 60)
    log("LOAD CLINICAL DATA — OS"); log("=" * 60)
    if not os.path.exists(CLIN_PATH):
        log(f"  Not found: {CLIN_PATH}")
        return None
    clin = pd.read_csv(CLIN_PATH, sep="\t", index_col=0,
                       low_memory=False)
    log(f"  Shape: {clin.shape}")
    log(f"  Columns (first 20): {list(clin.columns[:20])}")
    return clin

# ═══════════════════════════════════════════════════════════════
# OBJ-1: SUBTYPE ANNOTATION
# ═══════════════════════════════════════════════════════════════

def obj1_subtype_annotation(expr, depth, t_cols):
    log(""); log("=" * 60)
    log("OBJ-1 — FORMAL SUBTYPE ANNOTATION"); log("=" * 60)
    log("  S3-P1: Type 2 depth > Type 1  MW p < 0.05")

    d = depth.reindex(t_cols).dropna()

    # ── cached TSV ──────────────────────────────────────────
    if os.path.exists(SUB_CACHE) and \
            os.path.getsize(SUB_CACHE) > 200:
        log(f"  Loading cached: {SUB_CACHE}")
        try:
            sub_df = pd.read_csv(SUB_CACHE, sep="\t",
                                 low_memory=False)
            log(f"  Cols: {list(sub_df.columns)}")
            return _apply_subtype(sub_df, d, "cached")
        except Exception as e:
            log(f"  Cache failed: {e}")

    # ── cBioPortal saved TSV ─────────────────────────────────
    if os.path.exists(CBIO_PATH):
        try:
            cbio = pd.read_csv(CBIO_PATH, sep="\t",
                               low_memory=False)
            for c in ["TUMOR_TYPE","CANCER_TYPE_DETAILED",
                       "HISTOLOGICAL_TYPE",
                       "paper_Histologic_Type"]:
                if c in cbio.columns:
                    log(f"  Using cBioPortal col: {c}")
                    log(f"  Values: "
                        f"{cbio[c].value_counts().to_dict()}")
                    return _apply_subtype(cbio, d, c)
        except Exception as e:
            log(f"  cBioPortal TSV failed: {e}")

    # ── cBioPortal API ───────────────────────────────────────
    cbio_pat = _fetch_cbio_patient_clinical()
    if cbio_pat is not None:
        for c in cbio_pat.columns:
            if any(kw in c.upper() for kw in
                   ["HIST","PAPER_HISTOLOGIC",
                    "MORPHOLOGY","SUBTYPE","TYPE"]):
                log(f"  API col: {c}")
                return _apply_subtype(cbio_pat, d, c)
        log(f"  API cols: {list(cbio_pat.columns)}")

    # ── Xena ────────────────────────────────────────────────
    xena = _fetch_xena_subtype()
    if xena is not None:
        sub_df = xena.reset_index()
        sub_df.columns = ["SAMPLE_ID","subtype"]
        sub_df.to_csv(SUB_CACHE, sep="\t", index=False)
        return _apply_subtype(sub_df, d, "subtype")

    # ── expression proxy ────────────────────────────────────
    log("  All annotation sources failed — expression proxy.")
    return _expression_proxy_subtype(expr, depth, t_cols)


def _fetch_cbio_patient_clinical():
    try: import requests
    except ImportError: return None
    for study_id in ["kirp_tcga","kirp_tcga_pub"]:
        url = (f"https://www.cbioportal.org/api/studies/"
               f"{study_id}/clinical-data"
               f"?clinicalDataType=PATIENT&pageSize=10000")
        try:
            r = requests.get(url, timeout=60,
                             headers={"Accept":
                                      "application/json"})
            if r.status_code == 200 and r.json():
                rows = {}
                for rec in r.json():
                    pid = rec.get("patientId","")
                    key = rec.get("clinicalAttributeId","")
                    val = rec.get("value","")
                    if pid not in rows: rows[pid] = {}
                    rows[pid][key] = val
                df = pd.DataFrame(rows).T.reset_index()
                df.rename(columns={"index":"PATIENT_ID"},
                          inplace=True)
                log(f"  cBioPortal API ({study_id}): "
                    f"{df.shape}")
                return df
        except Exception as e:
            log(f"  API {study_id}: {e}")
    return None


def _fetch_xena_subtype():
    try: import requests
    except ImportError: return None
    url = ("https://tcga-xena-hub.s3.us-east-1.amazonaws.com/"
           "download/TCGA.KIRP.sampleMap%2FKIRP_clinicalMatrix")
    try:
        r = requests.get(url, timeout=120)
        if r.status_code == 200 and len(r.content) > 1000:
            from io import StringIO
            df = pd.read_csv(StringIO(r.text), sep="\t",
                             index_col=0, low_memory=False)
            df.to_csv(CLIN_PATH, sep="\t")
            log(f"  Xena clinical saved: {CLIN_PATH}")
            for c in df.columns:
                if any(kw in c.lower() for kw in
                       ["histol","type1","type2",
                        "subtype","paper_"]):
                    log(f"  Xena subtype col: {c}")
                    return df[c].dropna()
    except Exception as e:
        log(f"  Xena: {e}")
    return None


def _apply_subtype(df, d, type_col):
    log(f"  Applying subtype col: {type_col}")
    id_col = None
    for c in ["SAMPLE_ID","PATIENT_ID",
               "bcr_sample_barcode",
               "bcr_patient_barcode","sample_id"]:
        if c in df.columns:
            id_col = c; break
    if id_col is None: id_col = df.columns[0]

    sub_map = dict(zip(
        df[id_col].astype(str).str[:12],
        df[type_col].astype(str)
    ))
    subtypes = pd.Series(
        {s: sub_map.get(s[:12], "UNKNOWN")
         for s in d.index},
        name="subtype").reindex(d.index)

    for st, n in subtypes.value_counts().items():
        log(f"    {st}: n={n}")

    t1m = subtypes.str.lower().str.contains(
        r"type.?1|papillary.{0,5}1|type_1|prcc1",
        regex=True, na=False)
    t2m = subtypes.str.lower().str.contains(
        r"type.?2|papillary.{0,5}2|type_2|prcc2",
        regex=True, na=False)
    cim = subtypes.str.lower().str.contains(
        r"cimp|hlrcc|fh.{0,10}mutant",
        regex=True, na=False)

    d1 = d[t1m]; d2 = d[t2m]; dc = d[cim]
    log(f"  Type1: n={len(d1)}  Type2: n={len(d2)}"
        f"  CIMP: n={len(dc)}")

    if len(d1) >= 5 and len(d2) >= 5:
        _, p = safe_mwu(d2.values, d1.values)
        direction = ("Type2 DEEPER"
                     if d2.mean() > d1.mean()
                     else "Type1 DEEPER")
        log(f"  Type1 mean depth: {d1.mean():.4f}")
        log(f"  Type2 mean depth: {d2.mean():.4f}")
        log(f"  {direction}  MW {fmt_p(p)}")
        if p < 0.05 and d2.mean() > d1.mean():
            log("  S3-P1 CONFIRMED ✓")
        elif p < 0.05:
            log("  S3-P1 INVERTED ✗")
        else:
            log("  S3-P1 NOT CONFIRMED (ns)")
    else:
        log("  Insufficient labelled samples.")

    if len(dc) >= 3:
        non_c = d[~cim & ~t1m & ~t2m]
        _, pc  = safe_mwu(dc.values, non_c.values)
        log(f"  CIMP mean depth: {dc.mean():.4f}  "
            f"MW {fmt_p(pc)}")

    return d1, d2, dc, subtypes


def _expression_proxy_subtype(expr, depth, t_cols):
    log("  Expression proxy subtype:")
    log("    Type1 proxy:  MET top-40%")
    log("    Type2 proxy:  CDKN2A top-40% OR FH bot-40%")
    log("    CIMP proxy:   FH<Q20 & OGDHL<Q20 & EZH2>Q80")
    d = depth.reindex(t_cols).dropna()

    def gv(gene):
        if gene not in expr.index: return None
        return pd.Series(expr.loc[gene, t_cols].values,
                         index=t_cols).reindex(d.index)

    met  = gv("MET");  cdkn = gv("CDKN2A")
    fh   = gv("FH");   ogdh = gv("OGDHL")
    ezh2 = gv("EZH2")

    t1m = (met  >= met.quantile(0.60)) \
        if met  is not None \
        else pd.Series(False, index=d.index)
    t2m = ((cdkn >= cdkn.quantile(0.60)) |
           (fh   <= fh.quantile(0.40))) \
        if (cdkn is not None and fh is not None) \
        else pd.Series(False, index=d.index)
    cim = ((fh   <= fh.quantile(0.20)) &
           (ogdh <= ogdh.quantile(0.20)) &
           (ezh2 >= ezh2.quantile(0.80))) \
        if (fh is not None and ogdh is not None
            and ezh2 is not None) \
        else pd.Series(False, index=d.index)

    subtypes = pd.Series("UNCLASSIFIED", index=d.index)
    subtypes[t1m & ~t2m & ~cim] = "Type_1_proxy"
    subtypes[t2m & ~t1m & ~cim] = "Type_2_proxy"
    subtypes[cim]                = "CIMP_proxy"

    dummy = subtypes.reset_index()
    dummy.columns = ["SAMPLE_ID","subtype"]
    return _apply_subtype(dummy, d, "subtype")

# ═══════════════════════════════════════════════════════════════
# OBJ-2/3: DECONVOLUTION + TWIST1
# ═══════════════════════════════════════════════════════════════

def obj2_3_deconvolution(expr, depth, t_cols):
    log(""); log("=" * 60)
    log("OBJ-2/3 — DECONVOLUTION + TWIST1 STROMAL TEST")
    log("=" * 60)
    log("  S3-P2: r(TWIST1, stromal_score) > 0.40")

    d = depth.reindex(t_cols).dropna()
    st_av = [g for g in STROMAL_PROXY if g in expr.index]
    im_av = [g for g in IMMUNE_PROXY  if g in expr.index]
    log(f"  Stromal genes: {len(st_av)}/{len(STROMAL_PROXY)}")
    log(f"  Immune genes:  {len(im_av)}/{len(IMMUNE_PROXY)}")

    def make_score(genes, name):
        if not genes: return None
        sc = expr.loc[genes, t_cols].mean(axis=0)
        return pd.Series(norm01(sc.values),
                         index=t_cols,
                         name=name).reindex(d.index)

    stromal_score = make_score(st_av, "stromal_score")
    immune_score  = make_score(im_av, "immune_score")

    for sc, label in [(stromal_score, "Stromal"),
                       (immune_score,  "Immune")]:
        if sc is not None:
            r, p = safe_r(sc.values, d.values)
            log(f"  {label} r(depth) = {r:+.4f}  {fmt_p(p)}")

    log("")
    log("  TWIST1 STROMAL TEST:")
    if "TWIST1" in expr.index and stromal_score is not None:
        tw = pd.Series(expr.loc["TWIST1", t_cols].values,
                       index=t_cols).reindex(d.index)
        r_ts, p_ts = safe_r(tw.values, stromal_score.values)
        r_td, _    = safe_r(tw.values, d.values)
        r_tk, _    = safe_r(
            tw.values,
            pd.Series(expr.loc["KRT19", t_cols].values,
                      index=t_cols).reindex(d.index).values
            if "KRT19" in expr.index
            else np.full(len(d), np.nan))
        log(f"  r(TWIST1, stromal) = {r_ts:+.4f}  {fmt_p(p_ts)}")
        log(f"  r(TWIST1, depth)   = {r_td:+.4f}")
        log(f"  r(TWIST1, KRT19)   = {r_tk:+.4f}")
        if r_ts > 0.40:
            log("  S3-P2 CONFIRMED: TWIST1 = stromal ✓")
        else:
            log(f"  S3-P2 NOT CONFIRMED: r={r_ts:+.4f}")

        emt_genes = ["TWIST1","ACTA2","FAP","VIM","ZEB1",
                     "SNAI1","SNAI2","FN1","CDH2","S100A4"]
        log("")
        log(f"  {'Gene':<12} {'r_stromal':>10} "
            f"{'r_depth':>10} {'verdict'}")
        log(f"  {'─'*46}")
        for gene in emt_genes:
            if gene not in expr.index: continue
            gv = pd.Series(expr.loc[gene, t_cols].values,
                           index=t_cols).reindex(d.index)
            rs, _ = safe_r(gv.values, stromal_score.values)
            rd, _ = safe_r(gv.values, d.values)
            v = ("STROMAL"    if rs > 0.35 else
                 "EPITHELIAL" if rs < 0.15 else "MIXED")
            log(f"  {gene:<12} {rs:>+10.4f} {rd:>+10.4f} {v}")

    if stromal_score is not None and immune_score is not None:
        pd.DataFrame({
            "sample_id":     d.index,
            "s1_depth":      d.values,
            "stromal_score": stromal_score.values,
            "immune_score":  immune_score.values,
        }).to_csv(os.path.join(RESULTS_DIR,
                               "deconvolution_scores.csv"),
                  index=False)

    return stromal_score, immune_score

# ═══════════════════════════════════════════════════════════════
# OBJ-4/5/8/10: SURVIVAL
# ═══════════════════════════════════════════════════════════════

def obj4_5_8_10_survival(depth, ti, expr, t_cols, clin):
    log(""); log("=" * 60)
    log("OBJ-4/5/8/10 — OVERALL SURVIVAL"); log("=" * 60)
    log("  S3-P4: Axis A + B independent OS predictors")
    log("  S3-P8: TI high = worse OS  p < 0.05")

    if clin is None:
        log("  No clinical data — OS skipped.")
        return None, None

    # ── build clin_idx — deduplicated 12-char patient index ──
    clin_idx = clin.copy()
    clin_idx.index = clin_idx.index.astype(str).str[:12]
    clin_idx = clin_idx[~clin_idx.index.duplicated(keep="first")]

    col_time_cand  = ["OS.time","os_time","days_to_death",
                      "days_to_last_followup","_OS",
                      "OS_MONTHS"]
    col_event_cand = ["OS","vital_status","dead",
                      "OS_STATUS","_EVENT"]

    col_os_time = next(
        (c for c in col_time_cand if c in clin_idx.columns),
        None)
    col_os_event = next(
        (c for c in col_event_cand if c in clin_idx.columns),
        None)

    if col_os_time is None or col_os_event is None:
        log(f"  OS cols not found. Available: "
            f"{list(clin_idx.columns)}")
        return None, None

    log(f"  OS time:  {col_os_time}")
    log(f"  OS event: {col_os_event}")

    d = depth.reindex(t_cols).dropna()
    patients = [s[:12] for s in d.index]

    # ── scalar extraction helpers ────────────────────────────
    def _get_num(pid, col):
        if pid not in clin_idx.index:
            return np.nan
        val = clin_idx.at[pid, col]
        if isinstance(val, (pd.Series, pd.DataFrame,
                             np.ndarray, list)):
            val = pd.Series(val).iloc[0]
        return pd.to_numeric(val, errors="coerce")

    def _get_raw(pid, col):
        if pid not in clin_idx.index:
            return np.nan
        val = clin_idx.at[pid, col]
        if isinstance(val, (pd.Series, pd.DataFrame,
                             np.ndarray, list)):
            val = pd.Series(val).iloc[0]
        return val

    os_t = pd.Series(
        [_get_num(p, col_os_time) for p in patients],
        index=d.index, dtype=float)

    os_e_raw = pd.Series(
        [_get_raw(p, col_os_event) for p in patients],
        index=d.index)

    os_e = os_e_raw.map(
        lambda x: 1 if str(x).lower() in
        ["dead","deceased","1","true","yes"]
        else (0 if str(x).lower() in
              ["alive","living","0","false","no"]
              else np.nan)
    ).astype(float)

    valid = os_t.notna() & os_e.notna() & (os_t > 0)
    log(f"  Valid OS records: {valid.sum()} / {len(d)}")

    if valid.sum() < 30:
        log("  Too few valid OS records.")
        return None, None

    d_v   = d[valid];   ost_v = os_t[valid]
    ose_v = os_e[valid]
    log(f"  OS range: [{ost_v.min():.0f}, "
        f"{ost_v.max():.0f}] days")
    log(f"  Events:   {int(ose_v.sum())} "
        f"({100*ose_v.mean():.1f}%)")

    results = {}

    # S3-P8: TI vs OS
    log(""); log("  S3-P8 — TI OS:")
    if ti is not None:
        valid2 = valid & ti.reindex(d.index).notna()
        if valid2.sum() >= 20:
            ti2  = ti.reindex(d.index)[valid2]
            ost2 = os_t[valid2]; ose2 = os_e[valid2]
            med  = ti2.median()
            hi   = ti2 >= med; lo = ti2 < med
            _, p_ti = safe_logrank(
                ost2[hi].values, ose2[hi].values,
                ost2[lo].values, ose2[lo].values)
            log(f"  TI-high n={hi.sum()} "
                f"med={ost2[hi].median():.0f}d")
            log(f"  TI-low  n={lo.sum()} "
                f"med={ost2[lo].median():.0f}d")
            log(f"  logrank {fmt_p(p_ti)}")
            if not np.isnan(p_ti) and p_ti < 0.05:
                worse = ost2[hi].median() < ost2[lo].median()
                log("  S3-P8 CONFIRMED ✓" if worse
                    else "  S3-P8 INVERTED ✗")
            else:
                log("  S3-P8 NOT CONFIRMED (ns)")
            results["TI_logrank_p"]  = p_ti
            results["km_ti_hi"] = kaplan_meier(
                ost2[hi].values, ose2[hi].values)
            results["km_ti_lo"] = kaplan_meier(
                ost2[lo].values, ose2[lo].values)

    # Depth quartile OS
    log(""); log("  DEPTH QUARTILE OS:")
    q25 = d_v.quantile(0.25); q75 = d_v.quantile(0.75)
    q1m = d_v <= q25;          q4m = d_v >= q75
    _, p_q = safe_logrank(
        ost_v[q4m].values, ose_v[q4m].values,
        ost_v[q1m].values, ose_v[q1m].values)
    log(f"  Q4 n={q4m.sum()} med={ost_v[q4m].median():.0f}d")
    log(f"  Q1 n={q1m.sum()} med={ost_v[q1m].median():.0f}d")
    log(f"  logrank {fmt_p(p_q)}")
    if not np.isnan(p_q) and p_q < 0.05:
        log("  Depth quartile OS CONFIRMED ✓")
    results["q4_vs_q1_logrank_p"] = p_q
    results["km_q4"] = kaplan_meier(
        ost_v[q4m].values, ose_v[q4m].values)
    results["km_q1"] = kaplan_meier(
        ost_v[q1m].values, ose_v[q1m].values)

    # S3-P4: Axis A + Axis B OS
    log(""); log("  AXIS A + B OS (S3-P4):")
    axis_a_pos = ["KRT19","KRT7","ERBB2","SOX4","ITGA3",
                   "KRT8","KRT18"]
    axis_a_neg = ["SLC22A6","SLC34A1","CUBN","LRP2","SLC5A2"]
    axis_b_neg = ["FABP1","OGDHL","SUCLG1","GOT1",
                   "ACADM","FH","LDHB"]
    axis_b_pos = ["EZH2","KDM1A","MKI67"]

    def axis_score(pos_g, neg_g, idx):
        pa = [g for g in pos_g if g in expr.index]
        na = [g for g in neg_g if g in expr.index]
        parts = []
        if pa:
            parts.append(norm01(
                expr.loc[pa, t_cols].mean(axis=0)
                    .reindex(idx).values))
        if na:
            parts.append(1 - norm01(
                expr.loc[na, t_cols].mean(axis=0)
                    .reindex(idx).values))
        if not parts: return None
        return pd.Series(np.nanmean(parts, axis=0),
                         index=idx)

    for sc_pos, sc_neg, name in [
        (axis_a_pos, axis_a_neg, "Axis_A"),
        (axis_b_neg, axis_b_pos, "Axis_B"),
    ]:
        sc = axis_score(sc_pos, sc_neg, d_v.index)
        if sc is None: continue
        med = sc.median(); hi = sc >= med; lo = sc < med
        _, p_s = safe_logrank(
            ost_v.reindex(sc.index)[hi].values,
            ose_v.reindex(sc.index)[hi].values,
            ost_v.reindex(sc.index)[lo].values,
            ose_v.reindex(sc.index)[lo].values)
        log(f"  {name} high vs low: {fmt_p(p_s)}")
        results[f"{name}_logrank_p"] = p_s

    # OBJ-10: drug target gene OS
    log(""); log("  OBJ-10 DRUG TARGET OS:")
    log(f"  {'Drug':<22} {'gene':<8} {'p':>12} "
        f"{'med_hi':>8} {'med_lo':>8}")
    log(f"  {'─'*62}")
    drug_rows = []
    for drug, gene in DRUG_GENES.items():
        if gene not in expr.index: continue
        gv  = pd.Series(expr.loc[gene, t_cols].values,
                        index=t_cols).reindex(d_v.index)
        med = gv.median()
        hi  = gv >= med; lo = gv < med
        thi = ost_v.reindex(gv.index)[hi].dropna()
        ehi = ose_v.reindex(gv.index)[hi].dropna()
        tlo = ost_v.reindex(gv.index)[lo].dropna()
        elo = ose_v.reindex(gv.index)[lo].dropna()
        if len(thi) < 5 or len(tlo) < 5: continue
        _, p_g = safe_logrank(thi.values, ehi.values,
                               tlo.values, elo.values)
        flag = "★" if not np.isnan(p_g) and p_g < 0.05 \
            else " "
        log(f"  {flag}{drug:<22} {gene:<8} "
            f"{fmt_p(p_g):>12} "
            f"{thi.median():>8.0f} {tlo.median():>8.0f}")
        drug_rows.append({
            "drug_target": drug, "gene": gene,
            "p_logrank": p_g,
            "med_os_hi": thi.median(),
            "med_os_lo": tlo.median(),
        })
    pd.DataFrame(drug_rows).to_csv(
        os.path.join(RESULTS_DIR, "drug_target_OS.csv"),
        index=False)

    return results, {
        "d_v": d_v, "ost_v": ost_v, "ose_v": ose_v,
        "q1m": q1m, "q4m": q4m,
    }

# ═══════════════════════════════════════════════════════════════
# OBJ-6: MUTATIONS
# ═══════════════════════════════════════════════════════════════

def obj6_mutations(depth, expr, t_cols):
    log(""); log("=" * 60)
    log("OBJ-6 — MUTATION DATA"); log("=" * 60)
    log("  S3-P5: PBRM1 mut co-segregates with SETD2 + Axis B")

    d = depth.reindex(t_cols).dropna()
    mut_data = _fetch_cbio_mutations()

    if mut_data is None:
        log("  Mutation API unavailable — expression proxy.")
        return _expression_proxy_mutations(depth, expr, t_cols)

    log(f"  Mutation records: {len(mut_data)}")
    mut_map = {}
    for rec in mut_data:
        sid  = rec.get("sampleId","")
        gene = rec.get("gene",{})
        gene = gene.get("hugoGeneSymbol","") \
            if isinstance(gene, dict) else str(gene)
        if sid not in mut_map: mut_map[sid] = set()
        mut_map[sid].add(gene)

    rows = []
    for s in d.index:
        muts = set()
        s12  = s[:12]
        for k, v in mut_map.items():
            if k[:12] == s12: muts |= v
        row = {g: int(g in muts) for g in MUT_GENES}
        row["sample_id"] = s
        rows.append(row)

    mut_df = pd.DataFrame(rows).set_index("sample_id")
    log(f"  Mutation matrix: {mut_df.shape}")
    log(f"  {'Gene':<12} {'n_mut':>6} {'pct':>6}")
    for g in MUT_GENES:
        if g not in mut_df.columns: continue
        n = mut_df[g].sum()
        log(f"  {g:<12} {n:>6} {100*n/len(mut_df):>5.1f}%")

    # PBRM1 mutation vs depth
    log(""); log("  PBRM1 MUT vs DEPTH:")
    if "PBRM1" in mut_df.columns:
        p_mut  = mut_df["PBRM1"] == 1
        p_wt   = mut_df["PBRM1"] == 0
        d_mut  = d.reindex(mut_df.index[p_mut]).dropna()
        d_wt   = d.reindex(mut_df.index[p_wt]).dropna()
        _, p_p = safe_mwu(d_mut.values, d_wt.values)
        log(f"  Mutant depth: {d_mut.mean():.4f} (n={len(d_mut)})")
        log(f"  WT depth:     {d_wt.mean():.4f} (n={len(d_wt)})")
        log(f"  MW {fmt_p(p_p)}")

        # RNA concordance test (N-S2-6)
        if "PBRM1" in expr.index:
            rna = pd.Series(expr.loc["PBRM1", t_cols].values,
                            index=t_cols)
            r_mut = rna.reindex(mut_df.index[p_mut]).dropna()
            r_wt  = rna.reindex(mut_df.index[p_wt]).dropna()
            _, pr = safe_mwu(r_mut.values, r_wt.values)
            log(f"  PBRM1 RNA mutant: {r_mut.mean():.3f}")
            log(f"  PBRM1 RNA WT:     {r_wt.mean():.3f}")
            log(f"  MW {fmt_p(pr)}")
            if r_mut.mean() < r_wt.mean():
                log("  N-S2-6 partial — RNA does fall in mutant")
            else:
                log("  N-S2-6 CONFIRMED — RNA unreliable ✓")

    # PBRM1/SETD2 co-mutation
    log(""); log("  PBRM1/SETD2 CO-MUTATION:")
    if "PBRM1" in mut_df.columns and \
       "SETD2" in mut_df.columns:
        co  = ((mut_df["PBRM1"]==1) & (mut_df["SETD2"]==1)).sum()
        np_ = (mut_df["PBRM1"]==1).sum()
        ns  = (mut_df["SETD2"]==1).sum()
        ct  = np.array([[co, np_-co],
                         [ns-co, len(mut_df)-np_-ns+co]])
        try:
            chi2_val, p_chi, _, _ = chi2_contingency(ct)
        except Exception:
            chi2_val = p_chi = np.nan
        log(f"  PBRM1: {np_}  SETD2: {ns}  co-mut: {co}")
        log(f"  chi2 {fmt_p(p_chi)}")
        if not np.isnan(p_chi) and p_chi < 0.05:
            log("  PBRM1/SETD2 co-mutation: SIGNIFICANT ✓")
        else:
            log("  PBRM1/SETD2 co-mutation: NS")

    mut_df.to_csv(
        os.path.join(RESULTS_DIR, "mutation_matrix.csv"))
    return mut_df


def _fetch_cbio_mutations():
    if os.path.exists(MUT_CACHE) and \
            os.path.getsize(MUT_CACHE) > 500:
        log(f"  Loading cached mutations: {MUT_CACHE}")
        try:
            with open(MUT_CACHE) as f:
                return json.load(f)
        except Exception as e:
            log(f"  Cache read failed: {e}")
    try: import requests
    except ImportError:
        log("  requests not available.")
        return None
    for study_id in ["kirp_tcga","kirp_tcga_pub"]:
        url = (f"https://www.cbioportal.org/api/"
               f"molecular-profiles/{study_id}_mutations"
               f"/mutations?pageSize=500000")
        log(f"  Fetching mutations: {study_id}...")
        try:
            r = requests.get(url, timeout=180,
                             headers={"Accept":
                                      "application/json"})
            if r.status_code == 200:
                data = r.json()
                log(f"  Fetched: {len(data)} records")
                with open(MUT_CACHE,"w") as f:
                    json.dump(data, f)
                return data
            log(f"  HTTP {r.status_code}")
        except Exception as e:
            log(f"  {study_id}: {e}")
    return None


def _expression_proxy_mutations(depth, expr, t_cols):
    log("  Expression proxy mutation status:")
    d = depth.reindex(t_cols).dropna()
    proxy = {}
    for gene in ["SETD2","FH","BAP1","PBRM1","VHL"]:
        if gene not in expr.index: continue
        gv  = pd.Series(expr.loc[gene, t_cols].values,
                        index=t_cols).reindex(d.index)
        cut = gv.quantile(0.15)
        proxy[f"{gene}_proxy_mut"] = (gv <= cut).astype(int)
    if proxy:
        proxy_df = pd.DataFrame(proxy, index=d.index)
        log(f"  {'Col':<22} {'n_mut':>8} "
            f"{'d_mut':>10} {'d_wt':>10}")
        for col in proxy_df.columns:
            mt = proxy_df[col]==1; wt = proxy_df[col]==0
            log(f"  {col:<22} {mt.sum():>8} "
                f"{d[mt.values].mean():>10.4f} "
                f"{d[wt.values].mean():>10.4f}")
        return proxy_df
    return None

# ═══════════════════════════════════════════════════════════════
# OBJ-7: PDK1 / CA9 HYPOXIA MODULE
# ═══════��═══════════════════════════════════════════════════════

def obj7_pdk1_hypoxia_module(expr, depth, t_cols):
    log(""); log("=" * 60)
    log("OBJ-7 — PDK1/CA9 HYPOXIA MODULE"); log("=" * 60)
    log("  S3-P6: core pairwise r > 0.50")
    log("  DC-3:  PDK1 isoform conflict resolution")

    d = depth.reindex(t_cols).dropna()
    mod_av = [g for g in HYPOXIA_MODULE if g in expr.index]
    log(f"  Module genes: {mod_av}")

    # Pairwise correlations
    log(f"\n  {'Gene A':<12} {'Gene B':<12} "
        f"{'r':>8} {'p':>12} {'core?'}")
    log(f"  {'─'*50}")
    core   = ["CA9","SLC2A1","LDHA","PDK1"]
    core_av = [g for g in core if g in expr.index]
    confirmed = total = 0

    for gA, gB in itertools.combinations(mod_av, 2):
        vA = pd.Series(expr.loc[gA, t_cols].values,
                       index=t_cols).reindex(d.index)
        vB = pd.Series(expr.loc[gB, t_cols].values,
                       index=t_cols).reindex(d.index)
        r, p = safe_r(vA.values, vB.values)
        if np.isnan(r): continue
        flag = ""
        if gA in core_av and gB in core_av:
            total += 1
            if r > 0.50: confirmed += 1
            flag = "★ CORE"
        log(f"  {gA:<12} {gB:<12} {r:>+8.4f} "
            f"{fmt_p(p):>12} {flag}")

    log(f"\n  S3-P6: {confirmed}/{total} core pairs r>0.50")
    if total > 0:
        if confirmed == total:
            log("  S3-P6 CONFIRMED ✓")
        elif confirmed > 0:
            log(f"  S3-P6 PARTIAL ({confirmed}/{total})")
        else:
            log("  S3-P6 NOT CONFIRMED ✗")

    # PDK isoform analysis (DC-3)
    log("\n  DC-3 — PDK ISOFORM DEPTH CORRELATES:")
    ca9_v  = pd.Series(expr.loc["CA9", t_cols].values,
                        index=t_cols).reindex(d.index) \
        if "CA9" in expr.index else None
    ldha_v = pd.Series(expr.loc["LDHA", t_cols].values,
                        index=t_cols).reindex(d.index) \
        if "LDHA" in expr.index else None
    slc_v  = pd.Series(expr.loc["SLC2A1", t_cols].values,
                        index=t_cols).reindex(d.index) \
        if "SLC2A1" in expr.index else None

    log(f"  {'Isoform':<8} {'r_depth':>9} "
        f"{'r_CA9':>8} {'r_LDHA':>8} "
        f"{'r_GLUT1':>8} {'module?'}")
    log(f"  {'─'*55}")
    for pdk in PDK_ISOFORMS:
        if pdk not in expr.index: continue
        gv = pd.Series(expr.loc[pdk, t_cols].values,
                       index=t_cols).reindex(d.index)
        rd, _ = safe_r(gv.values, d.values)
        rc = safe_r(gv.values, ca9_v.values)[0]  \
            if ca9_v  is not None else np.nan
        rl = safe_r(gv.values, ldha_v.values)[0] \
            if ldha_v is not None else np.nan
        rs = safe_r(gv.values, slc_v.values)[0]  \
            if slc_v  is not None else np.nan
        arch = ("ARCH_HYPOXIA" if rc > 0.30 and rs > 0.30
                else "OXPHOS"  if rc < 0.10
                else "MIXED")
        log(f"  {pdk:<8} {rd:>+9.4f} {rc:>+8.4f} "
            f"{rl:>+8.4f} {rs:>+8.4f} {arch}")

    # DC-3 conflict resolution
    if "PDK1" in expr.index and ca9_v is not None:
        pdk1_v = pd.Series(expr.loc["PDK1", t_cols].values,
                           index=t_cols).reindex(d.index)
        both = ((pdk1_v >= pdk1_v.quantile(0.67)) &
                (ca9_v  >= ca9_v.quantile(0.67)))
        solo = ((pdk1_v >= pdk1_v.quantile(0.67)) &
                (ca9_v  <  ca9_v.quantile(0.33)))
        db = d[both.values]; ds = d[solo.values]
        _, p_dc3 = safe_mwu(db.values, ds.values)
        log(f"\n  DC-3 CONFLICT:")
        log(f"  PDK1-hi+CA9-hi (arch): "
            f"n={len(db)}  depth={db.mean():.4f}")
        log(f"  PDK1-hi+CA9-lo (oxph): "
            f"n={len(ds)}  depth={ds.mean():.4f}")
        log(f"  MW {fmt_p(p_dc3)}")
        if db.mean() > ds.mean():
            log("  DC-3 RESOLVED: arch-hypoxia PDK1 "
                "is deeper ✓")
            log("  DCA target = PDK1+CA9 co-high only.")
        else:
            log("  DC-3 UNRESOLVED.")

# ═══════════════════════════════════════════════════════════════
# OBJ-8: CDKN2A / CDK4 PARADOX
# ═══════════════════════════════════════════════════════════════

def obj8_cdkn2a_cdk4_paradox(expr, depth, t_cols):
    log(""); log("=" * 60)
    log("OBJ-8 — CDKN2A/CDK4 PARADOX"); log("=" * 60)
    log("  S3-P7: CDKN2A and CDK4 co-occur (not anti-corr)")
    log("  FC-5:  CDKN2A RNA low in CIMP")

    d = depth.reindex(t_cols).dropna()
    if "CDKN2A" not in expr.index or \
       "CDK4"   not in expr.index:
        log("  CDKN2A or CDK4 missing.")
        return

    cdkn = pd.Series(expr.loc["CDKN2A", t_cols].values,
                      index=t_cols).reindex(d.index)
    cdk4 = pd.Series(expr.loc["CDK4", t_cols].values,
                      index=t_cols).reindex(d.index)

    r_ck, p_ck = safe_r(cdkn.values, cdk4.values)
    log(f"  r(CDKN2A, CDK4) = {r_ck:+.4f}  {fmt_p(p_ck)}")
    if r_ck > 0:
        log("  CO-OCCUR (positive r)")
        log("  S3-P7 CONFIRMED: oncogenic stress bypass ✓")
    else:
        log("  ANTI-CORRELATED")
        log("  S3-P7 NOT CONFIRMED ✗")

    # Quadrant distribution
    qhb = (cdkn >= cdkn.median()) & (cdk4 >= cdk4.median())
    qhc = (cdkn >= cdkn.median()) & (cdk4 <  cdk4.median())
    qlb = (cdkn <  cdkn.median()) & (cdk4 <  cdk4.median())
    qhd = (cdkn <  cdkn.median()) & (cdk4 >= cdk4.median())
    log(f"\n  CDKN2A-hi + CDK4-hi (PARADOX): "
        f"n={qhb.sum():>3}  "
        f"d={d[qhb.values].mean():.4f}")
    log(f"  CDKN2A-hi + CDK4-lo:           "
        f"n={qhc.sum():>3}  "
        f"d={d[qhc.values].mean():.4f}")
    log(f"  CDKN2A-lo + CDK4-lo:           "
        f"n={qlb.sum():>3}  "
        f"d={d[qlb.values].mean():.4f}")
    log(f"  CDKN2A-lo + CDK4-hi:           "
        f"n={qhd.sum():>3}  "
        f"d={d[qhd.values].mean():.4f}")

    # FC-5: CIMP CDKN2A test
    log("\n  FC-5 — CDKN2A RNA IN CIMP PROXY:")
    if all(g in expr.index for g in ["FH","OGDHL","EZH2"]):
        fh   = pd.Series(expr.loc["FH",   t_cols].values,
                          index=t_cols).reindex(d.index)
        ogdh = pd.Series(expr.loc["OGDHL",t_cols].values,
                          index=t_cols).reindex(d.index)
        ezh2 = pd.Series(expr.loc["EZH2", t_cols].values,
                          index=t_cols).reindex(d.index)
        cimp = ((fh   <= fh.quantile(0.20)) &
                (ogdh <= ogdh.quantile(0.20)) &
                (ezh2 >= ezh2.quantile(0.80)))
        c_vals = cdkn[cimp.values]
        n_vals = cdkn[~cimp.values]
        _, pc  = safe_mwu(c_vals.values, n_vals.values)
        log(f"  CIMP proxy n={cimp.sum()}")
        log(f"  CDKN2A in CIMP:     {c_vals.mean():.3f}")
        log(f"  CDKN2A in non-CIMP: {n_vals.mean():.3f}")
        log(f"  MW {fmt_p(pc)}")
        if c_vals.mean() < n_vals.mean() and \
                not np.isnan(pc) and pc < 0.05:
            log("  FC-5 CONFIRMED: CDKN2A RNA LOW in CIMP ✓")
        else:
            log("  FC-5 NOT CONFIRMED")

    # Cell cycle panel
    log("\n  CELL CYCLE PANEL vs DEPTH:")
    cc = ["CDKN2A","CDK4","CDK6","CCND1",
           "CDKN1A","CDKN1B","MKI67","TOP2A","CCNE1"]
    log(f"  {'Gene':<12} {'r_depth':>9} {'r_CDK4':>9}")
    for gene in [g for g in cc if g in expr.index]:
        gv = pd.Series(expr.loc[gene, t_cols].values,
                       index=t_cols).reindex(d.index)
        rd, _ = safe_r(gv.values, d.values)
        rc, _ = safe_r(gv.values, cdk4.values)
        log(f"  {gene:<12} {rd:>+9.4f} {rc:>+9.4f}")

# ═══════════════════════════════════════════════════════════════
# OBJ-9: CROSS-CANCER COMPARISON
# ═══════════════════════════════════════════════════════════════

def obj9_cross_cancer(expr, depth, t_cols):
    log(""); log("=" * 60)
    log("OBJ-9 — CROSS-CANCER COMPARISON"); log("=" * 60)

    d = depth.reindex(t_cols).dropna()

    if "KRT19" not in expr.index or \
       "SLC22A6" not in expr.index:
        log("  KRT19 or SLC22A6 missing.")
        return

    krt = pd.Series(expr.loc["KRT19",   t_cols].values,
                     index=t_cols).reindex(d.index)
    slc = pd.Series(expr.loc["SLC22A6", t_cols].values,
                     index=t_cols).reindex(d.index)
    ti_s = pd.Series(norm01(krt.values) - norm01(slc.values),
                      index=d.index)

    cross = list(dict.fromkeys(
        PRCC_TI_POS + PRCC_TI_NEG +
        CCRCC_TI_POS + CCRCC_TI_NEG +
        ["TWIST1","VIM","FH","EZH2","PBRM1","SETD2",
         "MET","ERBB2","CA9","EPAS1","HIF1A","B2M",
         "HAVCR2","ARG1","KDM1A","TET2"]
    ))
    log(f"  {'Gene':<14} {'r_TI':>9} {'r_depth':>9}"
        f"  {'pole'}")
    log(f"  {'─'*50}")
    for gene in [g for g in cross if g in expr.index]:
        gv = pd.Series(expr.loc[gene, t_cols].values,
                       index=t_cols).reindex(d.index)
        rti, _ = safe_r(gv.values, ti_s.values)
        rd,  _ = safe_r(gv.values, d.values)
        pole = ("PRCC_ATTRACTOR"  if rti > 0.30 else
                "PRCC_NORM_POLE"  if rti < -0.30 else
                "ccRCC_ATTRACTOR" if gene in CCRCC_TI_POS
                else "")
        log(f"  {gene:<14} {rti:>+9.4f} {rd:>+9.4f}"
            f"  {pole}")

    log("")
    log("  ATTRACTOR GEOMETRY COMPARISON:")
    log("  ┌─────────────────────────────────────────────┐")
    log("  │ ccRCC: ECM/myofibroblast identity            │")
    log("  │   RUNX1▲ LOXL2▲ TGFB1▲ / FBP1▼ GOT1▼      │")
    log("  │   TI = norm(GOT1) – norm(RUNX1)             │")
    log("  ├─────────────────────────────────────────────┤")
    log("  │ PRCC: Biliary ductal identity                │")
    log("  │   KRT19▲ ERBB2▲ KRT7▲ / SLC22A6▼ FABP1▼   │")
    log("  │   TI = norm(KRT19) – norm(SLC22A6)          │")
    log("  ├─────────────────────────────────────────────┤")
    log("  │ SHARED MECHANISM (Axis B):                  │")
    log("  │   TCA collapse → αKG↓ → TET2↓ → EZH2▲     │")
    log("  │   Identity axis is cancer-type specific     │")
    log("  │   Metabolic axis is universal               │")
    log("  └─────────────────────────────────────────────┘")

# ═══════════════════════════════════════════════════════════════
# OBJ-11: ARG1 / M2 MACROPHAGE
# ═══════════════════════════════════════════════════════════════

def obj11_arg1_m2(expr, depth, t_cols,
                   stromal_score, immune_score):
    log(""); log("=" * 60)
    log("OBJ-11 — ARG1 / M2 MACROPHAGE"); log("=" * 60)
    log("  S3-P3: ARG1 Q4/Q1 > 1.5  p < 0.05")
    log("  DC-2:  Repolarisation not depletion")

    d = depth.reindex(t_cols).dropna()
    if "ARG1" not in expr.index:
        log("  ARG1 missing."); return

    q25 = d.quantile(0.25); q75 = d.quantile(0.75)
    q1i = d[d <= q25].index; q4i = d[d >= q75].index

    arg1_v = pd.Series(expr.loc["ARG1", t_cols].values,
                        index=t_cols).reindex(d.index)
    q4m = arg1_v.reindex(
        q4i.intersection(arg1_v.index)).mean()
    q1m = arg1_v.reindex(
        q1i.intersection(arg1_v.index)).mean()
    _, p_a = safe_mwu(
        arg1_v.reindex(q4i).dropna().values,
        arg1_v.reindex(q1i).dropna().values)

    log(f"  ARG1 Q4 mean: {q4m:.4f}")
    log(f"  ARG1 Q1 mean: {q1m:.4f}")
    log(f"  ARG1 Q4/Q1:   {q4m/(q1m+1e-6):.3f}")
    log(f"  MW {fmt_p(p_a)}")
    if q4m/(q1m+1e-6) > 1.5 and \
            not np.isnan(p_a) and p_a < 0.05:
        log("  S3-P3 CONFIRMED ✓")
    else:
        log("  S3-P3 NOT CONFIRMED")

    m2_genes = ["ARG1","MRC1","CD163","IL10","TGFB1",
                 "CD68","CSF1R","FCGR3A"]
    m1_genes = ["TNF","IL6","IL12A","CXCL10",
                 "CD86","NOS2","IL1B"]
    av_m2 = [g for g in m2_genes if g in expr.index]
    av_m1 = [g for g in m1_genes if g in expr.index]

    log(f"\n  {'Gene':<10} {'pheno':<5} {'r_depth':>9} "
        f"{'Q4/Q1':>7}")
    log(f"  {'─'*34}")
    for gene, ph in ([(g,"M2") for g in av_m2] +
                      [(g,"M1") for g in av_m1]):
        gv  = pd.Series(expr.loc[gene, t_cols].values,
                        index=t_cols).reindex(d.index)
        r,_ = safe_r(gv.values, d.values)
        q4v = expr.loc[gene,
                        q4i.intersection(expr.columns)].mean()
        q1v = expr.loc[gene,
                        q1i.intersection(expr.columns)].mean()
        log(f"  {gene:<10} {ph:<5} {r:>+9.4f} "
            f"{q4v/(q1v+1e-6):>7.3f}")

    if av_m2 and av_m1:
        m2s = norm01(expr.loc[av_m2, t_cols].mean(
            axis=0).reindex(d.index).values)
        m1s = norm01(expr.loc[av_m1, t_cols].mean(
            axis=0).reindex(d.index).values)
        idx = pd.Series(m2s - m1s, index=d.index)
        r_idx, p_idx = safe_r(idx.values, d.values)
        log(f"\n  M2/M1 polarisation index r(depth) = "
            f"{r_idx:+.4f}  {fmt_p(p_idx)}")
        if r_idx > 0.15:
            log("  M2 polarisation INCREASES with depth ✓")
            log("  DC-2: lenvatinib/cabozantinib "
                "(repolarisation) preferred over "
                "anti-CSF1R depletion in Q4. ✓")

    if stromal_score is not None:
        r_as, p_as = safe_r(arg1_v.values,
                             stromal_score.values)
        log(f"\n  r(ARG1, stromal_score) = "
            f"{r_as:+.4f}  {fmt_p(p_as)}")

# ═══════════════════════════════════════════════════════════════
# OBJ-12: CIMP SUBGROUP
# ═══════════════════════════════════════════════════════════════

def obj12_cimp_subgroup(expr, depth, t_cols):
    log(""); log("=" * 60)
    log("OBJ-12 — CIMP SUBGROUP"); log("=" * 60)
    log("  FC-5: CDKN2A methylated in CIMP, RNA in non-CIMP")

    d = depth.reindex(t_cols).dropna()
    if not all(g in expr.index for g in
               ["FH","OGDHL","EZH2"]):
        log("  FH/OGDHL/EZH2 missing."); return

    fh   = pd.Series(expr.loc["FH",   t_cols].values,
                      index=t_cols).reindex(d.index)
    ogdh = pd.Series(expr.loc["OGDHL",t_cols].values,
                      index=t_cols).reindex(d.index)
    ezh2 = pd.Series(expr.loc["EZH2", t_cols].values,
                      index=t_cols).reindex(d.index)

    cimp_hi  = ((fh   <= fh.quantile(0.15)) &
                 (ogdh <= ogdh.quantile(0.15)) &
                 (ezh2 >= ezh2.quantile(0.85)))
    cimp_mid = ((fh   <= fh.quantile(0.25)) &
                 (ogdh <= ogdh.quantile(0.25)) &
                 (ezh2 >= ezh2.quantile(0.75)) &
                 ~cimp_hi)
    non_cimp = ~(cimp_hi | cimp_mid)

    log(f"  CIMP-high n={cimp_hi.sum()}")
    log(f"  CIMP-mid  n={cimp_mid.sum()}")
    log(f"  Non-CIMP  n={non_cimp.sum()}")

    genes = ["CDKN2A","CDK4","KRT19","SLC22A6",
              "SETD2","PBRM1","TET2","B2M","HLA-A",
              "MKI67","MET","ERBB2","EZH2",
              "FH","OGDHL","CA9","ARG1"]
    avail = [g for g in genes if g in expr.index]

    log(f"\n  {'Gene':<12} {'CIMP_hi':>10} "
        f"{'CIMP_mid':>10} {'non_CIMP':>10} "
        f"{'p_hi_vs_rest':>14}")
    log(f"  {'─'*60}")
    rows = []
    for gene in avail:
        gv = pd.Series(expr.loc[gene, t_cols].values,
                       index=t_cols).reindex(d.index)
        mh = gv[cimp_hi.values].mean()
        mm = gv[cimp_mid.values].mean()
        mn = gv[non_cimp.values].mean()
        _, p = safe_mwu(gv[cimp_hi.values].values,
                         gv[non_cimp.values].values)
        f = "★" if not np.isnan(p) and p < 0.05 else " "
        log(f"  {f}{gene:<12} {mh:>10.3f} "
            f"{mm:>10.3f} {mn:>10.3f} "
            f"{fmt_p(p):>14}")
        rows.append({"gene": gene, "CIMP_hi": mh,
                     "CIMP_mid": mm, "non_CIMP": mn,
                     "p_hi_vs_rest": p})

    pd.DataFrame(rows).to_csv(
        os.path.join(RESULTS_DIR, "cimp_subgroup.csv"),
        index=False)

    d_chi = d[cimp_hi.values]
    d_non = d[non_cimp.values]
    _, pt  = safe_mwu(d_chi.values, d_non.values)
    log(f"\n  CIMP-hi depth: {d_chi.mean():.4f}")
    log(f"  non-CIMP depth: {d_non.mean():.4f}")
    log(f"  MW {fmt_p(pt)}")
    if not np.isnan(pt) and pt < 0.05:
        log("  CIMP proxy is SIGNIFICANTLY DEEPER ✓")

# ═══════════════════════════════════════════════════════════════
# FIGURE
# ═══════════════════════════════════════════════════════════════

def generate_figure(expr, depth, t_cols,
                     stromal_score, immune_score,
                     os_results, os_data):
    log(""); log("=" * 60)
    log("GENERATING FIGURE"); log("=" * 60)

    d = depth.reindex(t_cols).dropna()
    fig = plt.figure(figsize=(26, 30))
    gs  = gridspec.GridSpec(4, 3, figure=fig,
                             hspace=0.55, wspace=0.40)

    # ── A: TI KM ─────────────────────────────────────────────
    ax = fig.add_subplot(gs[0, 0])
    if os_results and "km_ti_hi" in os_results:
        for (t, s), col, lab in [
            (os_results["km_ti_hi"],
             "#C0392B", "TI-high (deep)"),
            (os_results["km_ti_lo"],
             "#2980B9", "TI-low (shallow)"),
        ]:
            ax.step(t/365, s, where="post",
                    color=col, label=lab, lw=2)
        p = os_results.get("TI_logrank_p", np.nan)
        ax.set_title(f"A: TI OS\n{fmt_p(p)}",
                     fontsize=9, fontweight="bold")
        ax.legend(fontsize=7); ax.set_ylim(0, 1.05)
        ax.set_xlabel("Years"); ax.set_ylabel("Survival")
    else:
        ax.text(0.5, 0.5, "OS unavailable",
                ha="center", va="center",
                transform=ax.transAxes)
        ax.set_title("A: TI OS", fontsize=9,
                     fontweight="bold")

    # ── B: Depth quartile KM ─────────────────────────────────
    ax = fig.add_subplot(gs[0, 1])
    if os_results and "km_q4" in os_results:
        for (t, s), col, lab in [
            (os_results["km_q4"], "#C0392B", "Q4 (deep)"),
            (os_results["km_q1"], "#2980B9", "Q1 (shallow)"),
        ]:
            ax.step(t/365, s, where="post",
                    color=col, label=lab, lw=2)
        p = os_results.get("q4_vs_q1_logrank_p", np.nan)
        ax.set_title(f"B: Depth Quartile OS\n{fmt_p(p)}",
                     fontsize=9, fontweight="bold")
        ax.legend(fontsize=7); ax.set_ylim(0, 1.05)
        ax.set_xlabel("Years"); ax.set_ylabel("Survival")
    else:
        ax.text(0.5, 0.5, "OS unavailable",
                ha="center", va="center",
                transform=ax.transAxes)
        ax.set_title("B: Depth Q OS", fontsize=9,
                     fontweight="bold")

    # ── C: Stromal vs depth ───────────────────────────────────
    ax = fig.add_subplot(gs[0, 2])
    if stromal_score is not None:
        ax.scatter(d.values, stromal_score.values,
                   c=d.values, cmap="RdBu_r",
                   s=8, alpha=0.5)
        r, _ = safe_r(d.values, stromal_score.values)
        ax.set_title(f"C: Stromal Score vs Depth\nr={r:+.3f}",
                     fontsize=9, fontweight="bold")
        ax.set_xlabel("Depth"); ax.set_ylabel("Stromal")
    else:
        ax.set_title("C: Stromal Score", fontsize=9,
                     fontweight="bold")

    # ── D: CDKN2A vs CDK4 ────────────────────────────────────
    ax = fig.add_subplot(gs[1, 0])
    if "CDKN2A" in expr.index and "CDK4" in expr.index:
        cdkn = pd.Series(expr.loc["CDKN2A", t_cols].values,
                          index=t_cols).reindex(d.index)
        cdk4 = pd.Series(expr.loc["CDK4",   t_cols].values,
                          index=t_cols).reindex(d.index)
        ax.scatter(cdkn.values, cdk4.values,
                   c=d.values, cmap="RdBu_r",
                   s=8, alpha=0.6)
        r, _ = safe_r(cdkn.values, cdk4.values)
        ax.set_title(
            f"D: CDKN2A/CDK4 Paradox\n"
            f"r={r:+.3f} "
            f"({'CO-OCCUR' if r>0 else 'ANTI-CORR'})",
            fontsize=9, fontweight="bold")
        ax.set_xlabel("CDKN2A"); ax.set_ylabel("CDK4")

    # ── E: CA9 vs GLUT1 ───────────────────────────────────────
    ax = fig.add_subplot(gs[1, 1])
    if "CA9" in expr.index and "SLC2A1" in expr.index:
        ca9  = pd.Series(expr.loc["CA9",    t_cols].values,
                          index=t_cols).reindex(d.index)
        glut = pd.Series(expr.loc["SLC2A1", t_cols].values,
                          index=t_cols).reindex(d.index)
        ax.scatter(ca9.values, glut.values,
                   c=d.values, cmap="RdBu_r",
                   s=8, alpha=0.6)
        r, _ = safe_r(ca9.values, glut.values)
        ax.set_title(
            f"E: Arch Hypoxia Module\n"
            f"r(CA9,GLUT1)={r:+.3f}",
            fontsize=9, fontweight="bold")
        ax.set_xlabel("CA9"); ax.set_ylabel("SLC2A1")

    # ── F: TWIST1 vs stromal ──────────────────────────────────
    ax = fig.add_subplot(gs[1, 2])
    if "TWIST1" in expr.index and stromal_score is not None:
        tw = pd.Series(expr.loc["TWIST1", t_cols].values,
                       index=t_cols).reindex(d.index)
        ax.scatter(stromal_score.values, tw.values,
                   c=d.values, cmap="RdBu_r",
                   s=8, alpha=0.6)
        r, _ = safe_r(tw.values, stromal_score.values)
        ax.set_title(
            f"F: TWIST1 vs Stromal (S3-P2)\n"
            f"r={r:+.3f} "
            f"({'STROMAL ✓' if r>0.40 else 'not conf.'})",
            fontsize=9, fontweight="bold")
        ax.set_xlabel("Stromal Score")
        ax.set_ylabel("TWIST1")

    # ── G: ARG1 vs depth ──────────────────────────────────────
    ax = fig.add_subplot(gs[2, 0])
    if "ARG1" in expr.index:
        arg1 = pd.Series(expr.loc["ARG1", t_cols].values,
                          index=t_cols).reindex(d.index)
        ax.scatter(d.values, arg1.values,
                   c=d.values, cmap="RdBu_r",
                   s=8, alpha=0.6)
        r, _ = safe_r(arg1.values, d.values)
        ax.set_title(f"G: ARG1 M2 vs Depth\nr={r:+.3f}",
                     fontsize=9, fontweight="bold")
        ax.set_xlabel("Depth"); ax.set_ylabel("ARG1")

    # ── H: PDK isoform bar ────────────────────────────────────
    ax = fig.add_subplot(gs[2, 1])
    pdk_r = {}
    for pdk in PDK_ISOFORMS:
        if pdk not in expr.index: continue
        gv = pd.Series(expr.loc[pdk, t_cols].values,
                       index=t_cols).reindex(d.index)
        r, _ = safe_r(gv.values, d.values)
        pdk_r[pdk] = r
    if pdk_r:
        cols = ["#C0392B" if v > 0 else "#2980B9"
                for v in pdk_r.values()]
        ax.bar(range(len(pdk_r)), list(pdk_r.values()),
               color=cols, alpha=0.85)
        ax.set_xticks(range(len(pdk_r)))
        ax.set_xticklabels(list(pdk_r.keys()), fontsize=9)
        ax.axhline(0, color="black", lw=0.8)
        ax.set_ylabel("r vs depth")
        ax.set_title("H: PDK Isoforms (DC-3)",
                     fontsize=9, fontweight="bold")

    # ── I: CIMP proxy scatter ─────────────────────────────────
    ax = fig.add_subplot(gs[2, 2])
    if all(g in expr.index for g in ["FH","OGDHL","EZH2"]):
        fh   = pd.Series(expr.loc["FH",   t_cols].values,
                          index=t_cols).reindex(d.index)
        ogdh = pd.Series(expr.loc["OGDHL",t_cols].values,
                          index=t_cols).reindex(d.index)
        ezh2 = pd.Series(expr.loc["EZH2", t_cols].values,
                          index=t_cols).reindex(d.index)
        cimp = ((fh   <= fh.quantile(0.15)) &
                (ogdh <= ogdh.quantile(0.15)) &
                (ezh2 >= ezh2.quantile(0.85)))
        cols_I = ["#C0392B" if c else "#2980B9"
                  for c in cimp.values]
        ax.scatter(d.values, fh.values, c=cols_I,
                   s=10, alpha=0.6)
        ax.set_xlabel("Depth"); ax.set_ylabel("FH")
        ax.set_title("I: CIMP Proxy (red) vs Depth",
                     fontsize=9, fontweight="bold")

    # ── J: Cross-cancer bar ───────────────────────────────────
    ax = fig.add_subplot(gs[3, 0])
    cross_plot = ["KRT19","SLC22A6","ERBB2",
                   "RUNX1","LOXL2","FBP1","GOT1","UMOD"]
    cr = {}
    for gene in cross_plot:
        if gene not in expr.index: continue
        gv = pd.Series(expr.loc[gene, t_cols].values,
                       index=t_cols).reindex(d.index)
        r, _ = safe_r(gv.values, d.values)
        cr[gene] = r
    if cr:
        c_map = {"KRT19":  "#C0392B", "SLC22A6": "#2980B9",
                  "ERBB2":  "#C0392B", "RUNX1":   "#E67E22",
                  "LOXL2":  "#E67E22", "FBP1":    "#16A085",
                  "GOT1":   "#16A085", "UMOD":    "#16A085"}
        ax.barh(range(len(cr)), list(cr.values()),
                color=[c_map.get(g,"#95A5A6") for g in cr],
                alpha=0.85)
        ax.set_yticks(range(len(cr)))
        ax.set_yticklabels(list(cr.keys()), fontsize=8)
        ax.axvline(0, color="black", lw=0.8)
        ax.set_xlabel("r vs depth")
        ax.set_title("J: Cross-Cancer Attractor Genes",
                     fontsize=9, fontweight="bold")

    # ── K: Drug target OS ─────────────────────────────────────
    ax = fig.add_subplot(gs[3, 1])
    dop = os.path.join(RESULTS_DIR, "drug_target_OS.csv")
    if os.path.exists(dop):
        ddf = pd.read_csv(dop).dropna(subset=["p_logrank"])
        ddf = ddf.sort_values("p_logrank")
        if len(ddf) > 0:
            nlp  = -np.log10(
                ddf["p_logrank"].clip(1e-10, 1))
            colK = ["#C0392B" if p < 0.05 else "#95A5A6"
                    for p in ddf["p_logrank"]]
            ax.barh(range(len(ddf)), nlp,
                    color=colK, alpha=0.85)
            ax.set_yticks(range(len(ddf)))
            ax.set_yticklabels(
                ddf["drug_target"].values, fontsize=7)
            ax.axvline(-np.log10(0.05), color="black",
                        lw=0.8, ls="--")
            ax.set_xlabel("-log10(p)")
            ax.set_title("K: Drug Target OS",
                         fontsize=9, fontweight="bold")
    else:
        ax.set_title("K: Drug Target OS",
                     fontsize=9, fontweight="bold")
        ax.text(0.5, 0.5, "No OS data",
                ha="center", va="center",
                transform=ax.transAxes)

    # ── L: Scorecard ──────────────────────────────────────────
    ax = fig.add_subplot(gs[3, 2])
    ax.axis("off")
    txt = (
        "PRCC False Attractor — Script 3\n"
        "OrganismCore | 2026-03-02\n"
        "─────────────────────────────\n"
        "S3-P1  Type2 > Type1 depth\n"
        "S3-P2  TWIST1 = stromal  r>0.40\n"
        "S3-P3  ARG1 Q4/Q1 > 1.5  p<0.05\n"
        "S3-P4  Axis A + B → OS indep.\n"
        "S3-P5  PBRM1 mut + SETD2 comut\n"
        "S3-P6  CA9/SLC2A1/LDHA/PDK1 r>0.50\n"
        "S3-P7  CDKN2A/CDK4 co-occur\n"
        "S3-P8  TI high = worse OS\n"
        "─────────────────────────────\n"
        "DC-1 Anti-CD25 downgraded\n"
        "DC-2 CSF1R → repolarisation\n"
        "DC-3 PDK1 isoform resolved\n"
        "DC-4 ERBB2 IHC2+ criterion\n"
        "DC-5 αKG AIM2 safety flag"
    )
    ax.text(0.05, 0.95, txt,
            transform=ax.transAxes, fontsize=7.5,
            verticalalignment="top",
            fontfamily="monospace",
            bbox=dict(boxstyle="round",
                      facecolor="#F0F4F8", alpha=0.8))
    ax.set_title("L: Script 3 Scorecard",
                 fontsize=9, fontweight="bold")

    fig.suptitle(
        "PRCC False Attractor — Script 3\n"
        "Survival · Subtypes · Deconvolution · "
        "Mutations · Cross-Cancer",
        fontsize=12, fontweight="bold", y=0.998)

    out = os.path.join(RESULTS_DIR,
                        "prcc_script3_figure.pdf")
    fig.savefig(out, bbox_inches="tight", dpi=150)
    plt.close(fig)
    log(f"  Figure saved: {out}")

# ═══════════════════════════════════════════════════════════════
# SCORECARD
# ═══════════════════════════════════════════════════════════════

def print_scorecard():
    full = "\n".join(log_lines)
    log(""); log("=" * 60)
    log("SCRIPT 3 — FINAL SCORECARD"); log("=" * 60)

    checks = [
        ("S3-P1: Type 2 depth > Type 1",
         "S3-P1 CONFIRMED", "S3-P1 NOT CONFIRMED"),
        ("S3-P2: TWIST1 = stromal r>0.40",
         "S3-P2 CONFIRMED", "S3-P2 NOT CONFIRMED"),
        ("S3-P3: ARG1 Q4/Q1 > 1.5 p<0.05",
         "S3-P3 CONFIRMED", "S3-P3 NOT CONFIRMED"),
        ("S3-P4: Axis A + B independent OS",
         "Axis_A_logrank_p", "not confirmed"),
        ("S3-P5: PBRM1 + SETD2 co-mutation",
         "co-mutation: SIGNIFICANT",
         "co-mutation: NS"),
        ("S3-P6: CA9/SLC2A1/LDHA/PDK1 r>0.50",
         "S3-P6 CONFIRMED", "S3-P6 NOT CONFIRMED"),
        ("S3-P7: CDKN2A/CDK4 co-occur",
         "S3-P7 CONFIRMED", "S3-P7 NOT CONFIRMED"),
        ("S3-P8: TI high = worse OS",
         "S3-P8 CONFIRMED", "S3-P8 NOT CONFIRMED"),
    ]
    confirmed = 0
    for label, pos, neg in checks:
        if pos in full:
            verdict = "CONFIRMED ✓"; confirmed += 1
        elif neg in full:
            verdict = "NOT CONFIRMED ✗"
        else:
            verdict = "CHECK LOG"
        log(f"  {label:<42}  {verdict}")

    log(f"\n  OVERALL: {confirmed}/{len(checks)}")

    log("\n  DRUG CORRECTIONS APPLIED:")
    for c in [
        "DC-1  Anti-CD25 downgraded",
        "DC-2  Anti-CSF1R → repolarisation",
        "DC-3  PDK1 arch-hypoxia subpop tested",
        "DC-4  ERBB2 IHC2+ (not FISH) criterion",
        "DC-5  αKG AIM2/PANoptosis safety flag",
    ]:
        log(f"    {c}")

    log("\n  NOVEL FINDINGS:")
    novel = [
        ("N-S3-1: CIMP proxy deepest tier",
         "CIMP proxy is SIGNIFICANTLY DEEPER"),
        ("N-S3-2: PDK1+CA9 deeper than PDK1 alone",
         "DC-3 RESOLVED"),
        ("N-S3-3: M2/M1 index increases with depth",
         "M2 polarisation INCREASES with depth"),
        ("N-S3-4: TWIST1 stromal confirmed",
         "S3-P2 CONFIRMED"),
        ("N-S3-5: CDKN2A RNA low in CIMP",
         "FC-5 CONFIRMED"),
    ]
    for label, check in novel:
        v = "CONFIRMED ✓" if check in full \
            else "NOT CONFIRMED / CHECK LOG"
        log(f"    {label:<50}  {v}")

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    log("=" * 60)
    log("PRCC FALSE ATTRACTOR — SCRIPT 3")
    log("OrganismCore | Document 95c | 2026-03-02")
    log("Author: Eric Robert Lawson")
    log("=" * 60)
    log("")
    log("PREDICTIONS LOCKED 2026-03-02 BEFORE RUN")
    log("FRAMEWORK CORRECTIONS FROM 95-LC / 95-DLC:")
    for fc in ["FC-1 Subtypes from GDC KIRP_2015",
               "FC-2 αKG novelty = FH RNA stratification",
               "FC-3 CA9 = HIF protein not RNA",
               "FC-4 SAVOIR 27% ORR context",
               "FC-5 CDKN2A methylation vs RNA",
               "DC-1 Anti-CD25 downgraded",
               "DC-2 CSF1R → repolarisation",
               "DC-3 PDK1 isoform conflict",
               "DC-4 ERBB2 IHC2+ criterion",
               "DC-5 αKG AIM2 safety"]:
        log(f"  {fc}")

    depth, ti = load_s1_s2()
    if depth is None:
        log("FATAL: S1 depth not found.")
        write_log(); return

    expr, t_cols, n_cols = load_expression()

    # Recompute TI if absent
    if ti is None and "KRT19" in expr.index and \
            "SLC22A6" in expr.index:
        log("\nRecomputing TI...")
        d_r = depth.reindex(t_cols).dropna()
        krt = pd.Series(expr.loc["KRT19",   t_cols].values,
                        index=t_cols).reindex(d_r.index)
        slc = pd.Series(expr.loc["SLC22A6", t_cols].values,
                        index=t_cols).reindex(d_r.index)
        ti  = pd.Series(
            norm01(krt.values) - norm01(slc.values),
            index=d_r.index, name="TI")
        os.makedirs(S2_DIR, exist_ok=True)
        ti.reset_index().rename(
            columns={"index": "sample_id", 0: "TI"}
        ).to_csv(S2_TI, index=False)
        log(f"  TI recomputed: n={len(ti)}")

    clin = load_clinical()

    d1, d2, dc, subtypes = obj1_subtype_annotation(
        expr, depth, t_cols)

    stromal_score, immune_score = obj2_3_deconvolution(
        expr, depth, t_cols)

    os_results, os_data = obj4_5_8_10_survival(
        depth, ti, expr, t_cols, clin)

    mut_df = obj6_mutations(depth, expr, t_cols)

    obj7_pdk1_hypoxia_module(expr, depth, t_cols)

    obj8_cdkn2a_cdk4_paradox(expr, depth, t_cols)

    obj9_cross_cancer(expr, depth, t_cols)

    obj11_arg1_m2(expr, depth, t_cols,
                   stromal_score, immune_score)

    obj12_cimp_subgroup(expr, depth, t_cols)

    generate_figure(expr, depth, t_cols,
                     stromal_score, immune_score,
                     os_results, os_data)

    print_scorecard()
    write_log()

    log("")
    log("=" * 60)
    log("SCRIPT 3 COMPLETE")
    log(f"Results: {RESULTS_DIR}")
    log(f"Log:     {LOG_FILE}")
    log("Next: Document 95c (results)")
    log("=" * 60)


if __name__ == "__main__":
    main()
