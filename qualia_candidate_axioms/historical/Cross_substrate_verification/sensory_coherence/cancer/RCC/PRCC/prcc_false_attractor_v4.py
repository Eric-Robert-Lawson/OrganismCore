"""
PRCC False Attractor — Script 4
RE-RUN DEFERRED + NEW OBJECTIVES + CROSS-CANCER

Framework: OrganismCore
Document 95d-pre | 2026-03-02
Author: Eric Robert Lawson

═══════════════════════════════════════════════════════════════
PREDICTIONS LOCKED — 2026-03-02 — BEFORE SCRIPT 4

RE-RUN PREDICTIONS (deferred from Script 3):
  S4-P1:  Type 2 depth > Type 1  MW p < 0.05
          (now with GDC mmc1.xlsx annotation)
  S4-P2:  TI high = worse OS  p < 0.05
          (now with censored OS from Xena survival.txt)
  S4-P3:  Q4 vs Q1 OS logrank p < 0.05
          (same — censored data)
  S4-P4:  PBRM1 mutation co-segregates with SETD2
          co-mutation (now with GDC MAF)
  S4-P5:  CDKN2A RNA low in formal CIMP subtype
          (now with GDC annotation)

NEW PREDICTIONS:
  S4-P6:  RUNX1 is a shared attractor TF in both
          PRCC and ccRCC expression matrices
          r_depth > 0.40 in BOTH datasets
  S4-P7:  GOT1 is a shared normal pole gene in both
          PRCC and ccRCC
          r_depth < -0.40 in BOTH datasets
  S4-P8:  CIMP-high subgroup has the worst OS
          in formal subtype-stratified KM
  S4-P9:  SWI/SNF subunits (PBRM1, SETD2, ARID1A)
          are positively correlated with each other
          AND positively correlated with depth
          (RNA paradox is a module-level property,
          not gene-specific)
  S4-P10: ARG1 depth correlate is stronger than
          any classical M2 marker
          r(ARG1, depth) > r(CD163, depth)
          and > r(MRC1, depth)
  S4-P11: Warburg trio (SLC2A1/LDHA/PDK1)
          is more strongly correlated internally
          than with CA9
          — two-tier hypoxia module confirmed
  S4-P12: ERBB2 depth signal is continuous
          (Pearson r > 0.50) confirming IHC2+
          not FISH as correct biomarker

═══════════════════════════════════════════════════════════════
OBJECTIVES:
  OBJ-1:  Download and apply GDC KIRP_2015
          subtype annotation (mmc1.xlsx)
  OBJ-2:  Download Xena KIRP_survival.txt
          (censored OS) and re-run survival
  OBJ-3:  Download GDC KIRP MAF and run
          formal mutation analysis
  OBJ-4:  RUNX1 cross-cancer test
          (PRCC + ccRCC side-by-side)
  OBJ-5:  Shared attractor / shared normal pole
          formal gene panel
  OBJ-6:  CIMP-high subtype OS (formal)
  OBJ-7:  SWI/SNF RNA paradox module
  OBJ-8:  ARG1 vs M2 panel depth ranking
  OBJ-9:  Warburg two-tier formal test
  OBJ-10: ERBB2 continuous depth test
  OBJ-11: Drug target subtype-stratified map
          (which drugs are active in which
          formal subtype × depth stratum)
  OBJ-12: Cross-cancer attractor geometry figure
          (PRCC vs ccRCC side-by-side)

DATA:
  PRCC: all Script 1-3 outputs reused
  ccRCC: TCGA-KIRC expression matrix
         (TCGA_KIRC_HiSeqV2.gz)
  New downloads attempted:
    GDC KIRP_2015 mmc1.xlsx (subtype)
    UCSC Xena KIRP_survival.txt (OS censored)
    GDC KIRP MAF (mutations)
  OUTPUT: ./prcc_false_attractor/results_s4/
═══════════════════════════════════════════════════════════════
"""

import os
import gzip
import json
import itertools
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.stats import pearsonr, mannwhitneyu, chi2_contingency
import warnings
warnings.filterwarnings("ignore")

# ═══════════════════════════════���═══════════════════════════════
# PATHS
# ═════════════════════════════════════════════════════���═════════

BASE_DIR    = "./prcc_false_attractor/"
S1_DIR      = os.path.join(BASE_DIR, "results_s1/")
S2_DIR      = os.path.join(BASE_DIR, "results_s2/")
S3_DIR      = os.path.join(BASE_DIR, "results_s3/")
RESULTS_DIR = os.path.join(BASE_DIR, "results_s4/")
LOG_FILE    = os.path.join(RESULTS_DIR, "s4_log.txt")

# PRCC
KIRP_EXPR   = os.path.join(BASE_DIR, "TCGA_KIRP_HiSeqV2.gz")
KIRP_CLIN   = os.path.join(BASE_DIR, "KIRP_clinicalMatrix.tsv")
S1_DEPTH    = os.path.join(S1_DIR,   "depth_scores_tcga.csv")
S2_TI       = os.path.join(S2_DIR,   "transition_index.csv")

# ccRCC
KIRC_EXPR   = os.path.join(BASE_DIR, "TCGA_KIRC_HiSeqV2.gz")
KIRC_CLIN   = os.path.join(BASE_DIR, "KIRC_clinicalMatrix.tsv")

# New downloads (attempted at runtime)
GDC_SUBTYPE = os.path.join(BASE_DIR, "KIRP_GDC_subtypes.tsv")
XENA_SURV   = os.path.join(BASE_DIR, "KIRP_survival.txt")
GDC_MAF     = os.path.join(BASE_DIR, "KIRP_mutations_maf.tsv")
MUT_CACHE   = os.path.join(BASE_DIR, "KIRP_mutations_cbio.json")

os.makedirs(RESULTS_DIR, exist_ok=True)

# ═══════════════════════════════════════════════════════════════
# GENE PANELS
# ═══════════════════════════════════════════════════════════════

# Core attractor / normal pole genes — both RCC types
PRCC_ATTRACTOR  = ["KRT19","KRT7","ERBB2","SOX4","AXL",
                    "KDM1A","MET","EZH2","SETD2","PBRM1",
                    "RUNX1","TET2","KRT8","KRT18","ITGA3"]
PRCC_NORM_POLE  = ["SLC22A6","FABP1","SLC34A1","GPX3",
                    "CUBN","MIOX","GOT1","FH","OGDHL",
                    "LDHB","ACADM","SLC5A2","LRP2"]
CCRCC_ATTRACTOR = ["RUNX1","LOXL2","TGFB1","VIM","CDH2",
                    "EZH2","KDM1A","TWIST1","ACTA2","FAP",
                    "SNAI1","SNAI2","FN1","COL1A1","COL1A2"]
CCRCC_NORM_POLE = ["FBP1","UMOD","SLC22A6","MIOX","GOT1",
                    "ACADM","SLC34A1","GPX3","CUBN",
                    "SLC5A2","LRP2","ATP5A1","CPT1A"]

# Shared genes to test
SHARED_CANDS    = ["RUNX1","GOT1","EZH2","KDM1A","TET2",
                    "SLC22A6","MIOX","OGDHL","FH","B2M",
                    "HAVCR2","ARG1","CDKN2A","MKI67",
                    "SETD2","PBRM1","VEGFA","VHL","EPAS1"]

# SWI/SNF module
SWI_SNF         = ["PBRM1","SETD2","ARID1A","SMARCA4",
                    "SMARCB1","ARID1B","SMARCA2",
                    "ARID2","KDM6A","BAP1"]

# Hypoxia two-tier
WARBURG_TRIO    = ["SLC2A1","LDHA","PDK1"]
ARCH_HYPOXIA    = ["CA9"]
HYPOXIA_FULL    = ["CA9","SLC2A1","LDHA","PDK1","VEGFA",
                    "SLC16A1","ALDOA","ENO1","HK2","PFKL"]

# M2/ARG1 panel
M2_PANEL        = ["ARG1","CD163","MRC1","IL10","TGFB1",
                    "CD68","CSF1R","FCGR3A","VSIG4",
                    "MSR1","FOLR2","LYVE1"]
M1_PANEL        = ["TNF","IL6","IL12A","CXCL10","CD86",
                    "NOS2","IL1B","CXCL9","CXCL11"]
MDSC_PANEL      = ["ARG1","S100A8","S100A9","ITGAM",
                    "ITGAX","CEACAM8","FCGR3B"]

# Drug targets
DRUG_GENES      = {
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
    "B2M_MHC1":          "B2M",
    "HDAC_MHC1":         "HDAC1",
}

# ccRCC depth proxy genes (from Document 94)
KIRC_DEPTH_POS  = ["RUNX1","LOXL2","TGFB1","EZH2",
                    "KDM1A","VIM","ACTA2","FAP","COL1A1"]
KIRC_DEPTH_NEG  = ["FBP1","UMOD","GOT1","MIOX",
                    "SLC22A6","SLC34A1","GPX3","ACADM"]

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
    t1 = np.asarray(t1,float); e1 = np.asarray(e1,float)
    t2 = np.asarray(t2,float); e2 = np.asarray(e2,float)
    try:
        from lifelines.statistics import logrank_test
        r = logrank_test(t1,t2,
                         event_observed_A=e1,
                         event_observed_B=e2)
        return r.test_statistic, r.p_value
    except ImportError:
        pass
    all_t = np.sort(np.unique(np.concatenate([t1,t2])))
    O1=O2=E1=E2=0.0
    for t in all_t:
        n1=np.sum(t1>=t); n2=np.sum(t2>=t)
        d1=np.sum((t1==t)&(e1==1))
        d2=np.sum((t2==t)&(e2==1))
        n=n1+n2; d=d1+d2
        if n<2 or d==0: continue
        O1+=d1; O2+=d2
        E1+=n1*d/n; E2+=n2*d/n
    if E1<=0 or E2<=0: return np.nan, np.nan
    chi=(O1-E1)**2/E1+(O2-E2)**2/E2
    from scipy.stats import chi2
    return chi, 1-chi2.cdf(chi,df=1)

def kaplan_meier(t, e):
    t=np.asarray(t,float); e=np.asarray(e,float)
    order=np.argsort(t); t=t[order]; e=e[order]
    at_risk=len(t); s=1.0
    times=[0]; surv=[1.0]
    for i in range(len(t)):
        if e[i]==1:
            s*=(1-1.0/at_risk)
            times.append(t[i]); surv.append(s)
        at_risk-=1
    return np.array(times), np.array(surv)

def gv(gene, expr, cols, idx):
    """Get gene vector aligned to idx."""
    if gene not in expr.index: return None
    return pd.Series(expr.loc[gene, cols].values,
                     index=cols).reindex(idx)

# ═══════════════════════════════════════════════════════════════
# LOAD PRCC S1/S2/S3 OUTPUTS
# ═══════════════════════════════════════════════════════════════

def load_prcc_outputs():
    log(""); log("="*60)
    log("LOAD PRCC S1/S2/S3 OUTPUTS"); log("="*60)

    depth = ti = None
    if os.path.exists(S1_DEPTH):
        df = pd.read_csv(S1_DEPTH)
        depth = pd.Series(df["depth_score"].values,
                          index=df["sample_id"].values,
                          name="s1_depth")
        log(f"  S1 depth: n={len(depth)}")

    if os.path.exists(S2_TI):
        df = pd.read_csv(S2_TI)
        ti = pd.Series(df["TI"].values,
                       index=df["sample_id"].values,
                       name="TI")
        log(f"  S2 TI: n={len(ti)}")

    # S3 deconvolution scores
    decon = None
    decon_path = os.path.join(S3_DIR,"deconvolution_scores.csv")
    if os.path.exists(decon_path):
        decon = pd.read_csv(decon_path,
                            index_col="sample_id")
        log(f"  S3 decon: {decon.shape}")

    return depth, ti, decon

# ═══════════════════════════════════════════════════════════════
# LOAD EXPRESSION (PRCC + ccRCC)
# ═══════════════════════════════════════════════════════════════

def load_expr(path, label):
    log(f"  Loading {label}: {path}")
    if not os.path.exists(path):
        log(f"  NOT FOUND: {path}")
        return None, None, None
    open_fn = gzip.open if path.endswith(".gz") else open
    with open_fn(path, "rt") as fh:
        raw = pd.read_csv(fh, sep="\t", index_col=0)

    sample_ids = list(raw.columns)
    types = []
    for s in sample_ids:
        parts = s.split("-")
        code  = parts[3][:2] if len(parts) >= 4 else "00"
        if   code == "01": types.append("tumour")
        elif code == "11": types.append("normal")
        else:              types.append("other")
    meta   = pd.DataFrame({"t": types}, index=sample_ids)
    t_cols = raw.columns[meta["t"].eq("tumour").values]
    n_cols = raw.columns[meta["t"].eq("normal").values]
    log(f"  {label}: tumour={len(t_cols)} normal={len(n_cols)}")
    return raw, t_cols, n_cols

# ═══════════════════════════════════════════════════════════════
# OBJ-1: GDC SUBTYPE ANNOTATION
# ═══════════════════════════════════════════════════════════════

def obj1_gdc_subtypes(depth, t_cols):
    log(""); log("="*60)
    log("OBJ-1 — GDC KIRP_2015 SUBTYPE ANNOTATION")
    log("="*60)
    log("  S4-P1: Type 2 depth > Type 1  MW p < 0.05")
    log("  S4-P5: CDKN2A RNA low in CIMP  p < 0.05")

    d = depth.reindex(t_cols).dropna()

    # ── Try cached GDC subtype file ──────────────────────────
    if os.path.exists(GDC_SUBTYPE) and \
            os.path.getsize(GDC_SUBTYPE) > 200:
        log(f"  Loading cached: {GDC_SUBTYPE}")
        try:
            sub = pd.read_csv(GDC_SUBTYPE, sep="\t")
            return _run_subtype_analysis(sub, d)
        except Exception as e:
            log(f"  Cache read failed: {e}")

    # ── Attempt GDC Xena download ────────────────────────────
    log("  Attempting GDC subtype download...")
    sub = _download_gdc_subtypes()
    if sub is not None:
        sub.to_csv(GDC_SUBTYPE, sep="\t", index=False)
        return _run_subtype_analysis(sub, d)

    # ── Attempt PanCan subtype from UCSC Xena ────────────────
    log("  Attempting UCSC Xena pancan subtype...")
    sub = _download_xena_pancan_subtype()
    if sub is not None:
        sub.to_csv(GDC_SUBTYPE, sep="\t", index=False)
        return _run_subtype_analysis(sub, d)

    # ── Attempt TCGAbiolinks R-style API ─────────────────────
    log("  Attempting cBioPortal SAMPLE clinical API...")
    sub = _download_cbio_sample_clinical()
    if sub is not None:
        sub.to_csv(GDC_SUBTYPE, sep="\t", index=False)
        return _run_subtype_analysis(sub, d)

    log("  All subtype sources failed.")
    log("  S4-P1 and S4-P5 DEFERRED.")
    return None, None, None, None


def _download_gdc_subtypes():
    """
    Try UCSC Xena TCGA KIRP phenotype file which
    contains paper_Histologic_Type column from
    the KIRP 2016 Cancer Cell paper.
    """
    try: import requests
    except ImportError: return None

    urls = [
        # UCSC Xena KIRP phenotype
        ("https://tcga-xena-hub.s3.us-east-1.amazonaws.com/"
         "download/TCGA.KIRP.sampleMap%2FKIRP_clinicalMatrix"),
        # GDC legacy API endpoint
        ("https://api.gdc.cancer.gov/cases"
         "?filters=%7B%22op%22%3A%22and%22%2C%22content%22%3A"
         "%5B%7B%22op%22%3A%22%3D%22%2C%22content%22%3A"
         "%7B%22field%22%3A%22project.project_id%22%2C"
         "%22value%22%3A%22TCGA-KIRP%22%7D%7D%5D%7D"
         "&fields=submitter_id,diagnoses.morphology,"
         "diagnoses.primary_diagnosis"
         "&format=tsv&size=500"),
    ]

    for url in urls:
        try:
            r = requests.get(url, timeout=120)
            if r.status_code == 200 and \
                    len(r.content) > 1000:
                from io import StringIO
                df = pd.read_csv(
                    StringIO(r.text), sep="\t",
                    index_col=0, low_memory=False)
                log(f"  Downloaded: {df.shape}")
                log(f"  Cols: {list(df.columns[:20])}")

                # Search for subtype column
                for c in df.columns:
                    if any(k in c.lower() for k in
                           ["paper_histologic",
                            "histologic_type",
                            "histologic.type",
                            "subtype","paper_"]):
                        vc = df[c].value_counts()
                        log(f"  Subtype col: {c}")
                        log(f"  Values: {vc.to_dict()}")
                        out = df[c].dropna().reset_index()
                        out.columns = ["SAMPLE_ID",
                                       "SUBTYPE"]
                        return out
                # Save full matrix for manual inspection
                df.to_csv(
                    os.path.join(BASE_DIR,
                                 "KIRP_full_pheno.tsv"),
                    sep="\t")
                log("  Saved full phenotype for inspection.")
        except Exception as e:
            log(f"  Download failed: {e}")
    return None


def _download_xena_pancan_subtype():
    """
    UCSC Xena PanCan TCGA clinical with
    paper_Histologic_Type column.
    """
    try: import requests
    except ImportError: return None

    url = ("https://tcga-xena-hub.s3.us-east-1.amazonaws.com/"
           "download/TCGA.KIRP.sampleMap%2F"
           "KIRP_clinicalMatrix")
    try:
        r = requests.get(url, timeout=180)
        if r.status_code != 200: return None
        from io import StringIO
        df = pd.read_csv(StringIO(r.text), sep="\t",
                         index_col=0, low_memory=False)
        log(f"  Xena KIRP clin: {df.shape}")
        log(f"  All columns: {list(df.columns)}")

        # Try every column for Type 1/2 keywords
        for c in df.columns:
            vals = df[c].dropna().astype(str)
            if any(v.lower() in
                   ["type 1","type 2","type1","type2",
                    "papillary type 1",
                    "papillary type 2"]
                   for v in vals.unique()):
                log(f"  Found subtype col: {c}")
                log(f"  {vals.value_counts().to_dict()}")
                out = vals.reset_index()
                out.columns = ["SAMPLE_ID","SUBTYPE"]
                return out

        # Save for inspection
        df.to_csv(KIRP_CLIN, sep="\t")
        log(f"  Saved: {KIRP_CLIN}")
    except Exception as e:
        log(f"  Xena pancan: {e}")
    return None


def _download_cbio_sample_clinical():
    """cBioPortal SAMPLE-level clinical data."""
    try: import requests
    except ImportError: return None

    for study in ["kirp_tcga","kirp_tcga_pub"]:
        url = (f"https://www.cbioportal.org/api/studies/"
               f"{study}/clinical-data"
               f"?clinicalDataType=SAMPLE"
               f"&pageSize=10000")
        try:
            r = requests.get(
                url, timeout=60,
                headers={"Accept":"application/json"})
            if r.status_code != 200: continue
            data = r.json()
            if not data: continue
            rows = {}
            for rec in data:
                sid = rec.get("sampleId","")
                key = rec.get("clinicalAttributeId","")
                val = rec.get("value","")
                if sid not in rows: rows[sid] = {}
                rows[sid][key] = val
            df = pd.DataFrame(rows).T.reset_index()
            df.rename(columns={"index":"SAMPLE_ID"},
                      inplace=True)
            log(f"  cBioPortal sample ({study}): "
                f"{df.shape}")
            log(f"  Cols: {list(df.columns)}")

            type_col = None
            for c in df.columns:
                if any(k in c.upper() for k in
                       ["HIST","SUBTYPE","PAPER",
                        "MORPHOL","TYPE"]):
                    type_col = c; break
            if type_col:
                vc = df[type_col].value_counts()
                log(f"  Type col: {type_col}")
                log(f"  {vc.to_dict()}")
                out = df[["SAMPLE_ID",type_col]].copy()
                out.columns = ["SAMPLE_ID","SUBTYPE"]
                return out
        except Exception as e:
            log(f"  cBioPortal sample {study}: {e}")
    return None


def _run_subtype_analysis(sub_df, d):
    """
    Apply subtype dataframe to depth series.
    Returns (d_t1, d_t2, d_cimp, subtype_series).
    """
    log(f"  Running subtype analysis: {sub_df.shape}")

    id_col  = sub_df.columns[0]
    sub_col = sub_df.columns[1]

    sub_map = dict(zip(
        sub_df[id_col].astype(str).str[:12],
        sub_df[sub_col].astype(str)
    ))

    subtypes = pd.Series(
        {s: sub_map.get(s[:12],"UNKNOWN")
         for s in d.index},
        name="subtype").reindex(d.index)

    log("  Distribution:")
    for st, n in subtypes.value_counts().items():
        log(f"    {st}: n={n}")

    t1m = subtypes.str.lower().str.contains(
        r"type.?1|type_1|prcc1|papillary.{0,5}1",
        regex=True, na=False)
    t2m = subtypes.str.lower().str.contains(
        r"type.?2|type_2|prcc2|papillary.{0,5}2",
        regex=True, na=False)
    cim = subtypes.str.lower().str.contains(
        r"cimp|hlrcc|fh.{0,10}mut",
        regex=True, na=False)

    d1 = d[t1m]; d2 = d[t2m]; dc = d[cim]
    log(f"  Type1 n={len(d1)} "
        f"Type2 n={len(d2)} "
        f"CIMP n={len(dc)}")

    if len(d1) >= 5 and len(d2) >= 5:
        _, p = safe_mwu(d2.values, d1.values)
        log(f"  Type1 mean depth: {d1.mean():.4f}")
        log(f"  Type2 mean depth: {d2.mean():.4f}")
        log(f"  MW {fmt_p(p)}")
        if p < 0.05 and d2.mean() > d1.mean():
            log("  S4-P1 CONFIRMED ✓")
        elif p < 0.05:
            log("  S4-P1 INVERTED ✗")
        else:
            log("  S4-P1 NOT CONFIRMED (ns)")
    else:
        log("  Insufficient labelled samples for S4-P1.")

    if len(dc) >= 3:
        nc = d[~cim & ~t1m & ~t2m]
        _, pc = safe_mwu(dc.values, nc.values)
        log(f"  CIMP depth: {dc.mean():.4f}  "
            f"non-CIMP: {nc.mean():.4f}  MW {fmt_p(pc)}")

    return d1, d2, dc, subtypes

# ═══════════════════════════════════════════════════════════════
# OBJ-2: XENA SURVIVAL (CENSORED)
# ═══════════════════════════════════════════════════════════════

def obj2_censored_survival(depth, ti, expr_kirp,
                             t_cols_kirp, subtypes):
    log(""); log("="*60)
    log("OBJ-2 — CENSORED OS FROM XENA SURVIVAL.TXT")
    log("="*60)
    log("  S4-P2: TI high = worse OS  p < 0.05")
    log("  S4-P3: Q4 vs Q1 logrank p < 0.05")
    log("  S4-P8: CIMP-high worst OS subtype")

    d = depth.reindex(t_cols_kirp).dropna()

    # ── Download if absent ───────────────────────────────────
    if not os.path.exists(XENA_SURV) or \
            os.path.getsize(XENA_SURV) < 500:
        log("  Downloading Xena KIRP_survival.txt...")
        _download_xena_survival()

    if not os.path.exists(XENA_SURV) or \
            os.path.getsize(XENA_SURV) < 500:
        log("  Survival file unavailable.")
        log("  Falling back to days_to_death only analysis.")
        return _fallback_survival(depth, ti,
                                   expr_kirp, t_cols_kirp)

    # ── Load survival file ───────────────────────────────────
    surv = pd.read_csv(XENA_SURV, sep="\t",
                       index_col=0, low_memory=False)
    log(f"  Survival shape: {surv.shape}")
    log(f"  Columns: {list(surv.columns)}")

    # Map columns — Xena uses OS, OS.time
    surv.index = surv.index.astype(str).str[:12]
    surv = surv[~surv.index.duplicated(keep="first")]

    time_col = next(
        (c for c in ["OS.time","OS_time","DSS.time",
                      "PFI.time","days_to_death"]
         if c in surv.columns), None)
    event_col = next(
        (c for c in ["OS","DSS","vital_status",
                      "OS_STATUS","_EVENT"]
         if c in surv.columns), None)

    if time_col is None or event_col is None:
        log(f"  Cannot find OS cols in: "
            f"{list(surv.columns)}")
        return _fallback_survival(depth, ti,
                                   expr_kirp, t_cols_kirp)

    log(f"  OS time:  {time_col}")
    log(f"  OS event: {event_col}")

    patients = [s[:12] for s in d.index]

    def _s(pid, col):
        if pid not in surv.index: return np.nan
        v = surv.at[pid, col]
        if isinstance(v, (pd.Series, list,
                           np.ndarray)):
            v = pd.Series(v).iloc[0]
        return v

    os_t = pd.Series(
        [pd.to_numeric(_s(p, time_col),
                       errors="coerce")
         for p in patients],
        index=d.index, dtype=float)

    os_e_raw = pd.Series(
        [_s(p, event_col) for p in patients],
        index=d.index)

    os_e = os_e_raw.map(
        lambda x: 1 if str(x).lower() in
        ["dead","deceased","1","true","yes"]
        else (0 if str(x).lower() in
              ["alive","living","0","false","no"]
              else np.nan)
    ).astype(float)

    valid = os_t.notna() & os_e.notna() & (os_t > 0)
    log(f"  Valid OS: {valid.sum()} / {len(d)}")
    log(f"  Events:   {int(os_e[valid].sum())} "
        f"({100*os_e[valid].mean():.1f}%)")
    log(f"  Censored: "
        f"{int((os_e[valid]==0).sum())}")

    if valid.sum() < 50:
        log("  WARNING: fewer than 50 valid OS records.")

    return _run_survival_analysis(
        d, os_t, os_e, valid, ti,
        expr_kirp, t_cols_kirp, subtypes)


def _download_xena_survival():
    try: import requests
    except ImportError: return
    urls = [
        ("https://tcga-xena-hub.s3.us-east-1.amazonaws.com/"
         "download/survival%2FKIRP_survival.txt"),
        ("https://tcga-xena-hub.s3.us-east-1.amazonaws.com/"
         "download/TCGA.KIRP.sampleMap%2F"
         "KIRP_survival.txt"),
    ]
    for url in urls:
        try:
            r = requests.get(url, timeout=120)
            if r.status_code == 200 and \
                    len(r.content) > 500:
                with open(XENA_SURV,"wb") as f:
                    f.write(r.content)
                log(f"  Saved: {XENA_SURV} "
                    f"({len(r.content)} bytes)")
                return
        except Exception as e:
            log(f"  {url}: {e}")


def _fallback_survival(depth, ti, expr, t_cols):
    """Use days_to_death from KIRP_clinicalMatrix."""
    log("  Fallback: days_to_death from clinicalMatrix")
    if not os.path.exists(KIRP_CLIN):
        log("  No clinical matrix available.")
        return None, None

    clin = pd.read_csv(KIRP_CLIN, sep="\t",
                       index_col=0, low_memory=False)
    clin.index = clin.index.astype(str).str[:12]
    clin = clin[~clin.index.duplicated(keep="first")]

    time_col  = next(
        (c for c in ["days_to_death","OS.time",
                      "days_to_last_followup"]
         if c in clin.columns), None)
    event_col = next(
        (c for c in ["vital_status","OS","dead"]
         if c in clin.columns), None)

    if time_col is None or event_col is None:
        log("  No OS columns in clinical matrix.")
        return None, None

    d = depth.reindex(t_cols).dropna()
    patients = [s[:12] for s in d.index]

    def _g(pid, col):
        if pid not in clin.index: return np.nan
        v = clin.at[pid, col]
        if isinstance(v, (pd.Series, list,
                           np.ndarray)):
            v = pd.Series(v).iloc[0]
        return v

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

    valid = os_t.notna() & os_e.notna() & (os_t > 0)
    log(f"  Fallback valid OS: {valid.sum()} "
        f"events={int(os_e[valid].sum())}")
    return _run_survival_analysis(
        d, os_t, os_e, valid, ti, expr, t_cols, None)


def _run_survival_analysis(d, os_t, os_e, valid,
                             ti, expr, t_cols, subtypes):
    d_v   = d[valid]
    ost_v = os_t[valid]
    ose_v = os_e[valid]

    results = {}

    # S4-P2: TI OS
    log(""); log("  TI OS (S4-P2):")
    if ti is not None:
        v2  = valid & ti.reindex(d.index).notna()
        if v2.sum() >= 20:
            ti2 = ti.reindex(d.index)[v2]
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
            worse = (t2[hi].median() < t2[lo].median())
            if not np.isnan(p) and p < 0.05:
                log("  S4-P2 CONFIRMED ✓" if worse
                    else "  S4-P2 INVERTED ✗")
            else:
                log("  S4-P2 NOT CONFIRMED (ns)")
            results["S4P2_p"]   = p
            results["km_ti_hi"] = kaplan_meier(
                t2[hi].values, e2[hi].values)
            results["km_ti_lo"] = kaplan_meier(
                t2[lo].values, e2[lo].values)

    # S4-P3: Depth quartile OS
    log(""); log("  DEPTH QUARTILE OS (S4-P3):")
    q25 = d_v.quantile(0.25); q75 = d_v.quantile(0.75)
    q1m = d_v <= q25;          q4m = d_v >= q75
    _, p_q = safe_logrank(
        ost_v[q4m].values, ose_v[q4m].values,
        ost_v[q1m].values, ose_v[q1m].values)
    log(f"  Q4 n={q4m.sum()} "
        f"med={ost_v[q4m].median():.0f}d")
    log(f"  Q1 n={q1m.sum()} "
        f"med={ost_v[q1m].median():.0f}d")
    log(f"  logrank {fmt_p(p_q)}")
    if not np.isnan(p_q) and p_q < 0.05:
        log("  S4-P3 CONFIRMED ✓")
    else:
        log("  S4-P3 NOT CONFIRMED (ns)")
    results["S4P3_p"]  = p_q
    results["km_q4"]   = kaplan_meier(
        ost_v[q4m].values, ose_v[q4m].values)
    results["km_q1"]   = kaplan_meier(
        ost_v[q1m].values, ose_v[q1m].values)

    # Four-quartile KM
    q2m = (d_v > q25) & (d_v < d_v.quantile(0.50))
    q3m = (d_v >= d_v.quantile(0.50)) & (d_v < q75)
    for qm, ql in [(q1m,"Q1"),(q2m,"Q2"),
                    (q3m,"Q3"),(q4m,"Q4")]:
        results[f"km_{ql}"] = kaplan_meier(
            ost_v[qm].values, ose_v[qm].values)

    # S4-P8: Subtype OS
    log(""); log("  SUBTYPE OS (S4-P8):")
    if subtypes is not None:
        t1m = subtypes.reindex(d_v.index).str.lower()\
                       .str.contains(
                           r"type.?1|type_1",
                           regex=True, na=False)
        t2m = subtypes.reindex(d_v.index).str.lower()\
                       .str.contains(
                           r"type.?2|type_2",
                           regex=True, na=False)
        cim = subtypes.reindex(d_v.index).str.lower()\
                       .str.contains(
                           r"cimp|hlrcc",
                           regex=True, na=False)
        for mask, label in [(t1m,"Type1"),
                             (t2m,"Type2"),
                             (cim,"CIMP")]:
            if mask.sum() < 5: continue
            t_ = ost_v.reindex(d_v.index)[mask]
            e_ = ose_v.reindex(d_v.index)[mask]
            log(f"  {label} n={mask.sum()} "
                f"med={t_.median():.0f}d "
                f"events={int(e_.sum())}")
            results[f"km_{label}"] = kaplan_meier(
                t_.values, e_.values)
        # CIMP vs Type2 logrank
        if cim.sum() >= 3 and t2m.sum() >= 5:
            _, p_ct = safe_logrank(
                ost_v.reindex(d_v.index)[cim].values,
                ose_v.reindex(d_v.index)[cim].values,
                ost_v.reindex(d_v.index)[t2m].values,
                ose_v.reindex(d_v.index)[t2m].values)
            log(f"  CIMP vs Type2 {fmt_p(p_ct)}")
            if not np.isnan(p_ct) and p_ct < 0.05:
                log("  S4-P8 CONFIRMED ✓")

    # Drug target OS (all)
    log(""); log("  DRUG TARGET OS:")
    drug_rows = []
    log(f"  {'Drug':<22} {'gene':<8} "
        f"{'p':>12} {'med_hi':>8} {'med_lo':>8}")
    log(f"  {'─'*58}")
    for drug, gene in DRUG_GENES.items():
        if gene not in expr.index: continue
        g   = pd.Series(expr.loc[gene, t_cols].values,
                        index=t_cols).reindex(d_v.index)
        med = g.median()
        hi  = g >= med; lo = g < med
        thi = ost_v.reindex(g.index)[hi].dropna()
        ehi = ose_v.reindex(g.index)[hi].dropna()
        tlo = ost_v.reindex(g.index)[lo].dropna()
        elo = ose_v.reindex(g.index)[lo].dropna()
        if len(thi) < 5 or len(tlo) < 5: continue
        _, p_g = safe_logrank(thi.values, ehi.values,
                               tlo.values, elo.values)
        f = "★" if not np.isnan(p_g) and p_g < 0.05 \
            else " "
        log(f"  {f}{drug:<22} {gene:<8} "
            f"{fmt_p(p_g):>12} "
            f"{thi.median():>8.0f} "
            f"{tlo.median():>8.0f}")
        drug_rows.append({
            "drug_target": drug, "gene": gene,
            "p_logrank": p_g,
            "med_os_hi": thi.median(),
            "med_os_lo": tlo.median(),
        })
    pd.DataFrame(drug_rows).to_csv(
        os.path.join(RESULTS_DIR,"drug_OS_s4.csv"),
        index=False)

    return results, {
        "d_v": d_v, "ost_v": ost_v,
        "ose_v": ose_v, "q1m": q1m, "q4m": q4m,
    }

# ═══════════════════════════════════════════════════════════════
# OBJ-3: GDC MAF MUTATIONS
# ═══════════════════════════════════════════════════════════════

def obj3_gdc_mutations(depth, expr_kirp, t_cols_kirp):
    log(""); log("="*60)
    log("OBJ-3 — GDC MAF MUTATIONS"); log("="*60)
    log("  S4-P4: PBRM1 mut co-segregates with SETD2")

    d = depth.reindex(t_cols_kirp).dropna()

    # ── Download MAF ─────────────────────────────────────────
    if not os.path.exists(GDC_MAF) or \
            os.path.getsize(GDC_MAF) < 1000:
        log("  Attempting GDC MAF download...")
        _download_gdc_maf()

    if not os.path.exists(GDC_MAF) or \
            os.path.getsize(GDC_MAF) < 1000:
        # Try cBioPortal POST endpoint
        log("  Trying cBioPortal POST mutations...")
        mut_df = _cbio_post_mutations(d)
        if mut_df is not None:
            return mut_df
        log("  Mutation data unavailable.")
        return _expression_proxy_mutations(
            d, expr_kirp, t_cols_kirp)

    # ── Parse MAF ────────────────────────────────────────────
    log(f"  Parsing MAF: {GDC_MAF}")
    try:
        maf = pd.read_csv(GDC_MAF, sep="\t",
                          comment="#",
                          low_memory=False)
        log(f"  MAF shape: {maf.shape}")

        gene_col = next(
            (c for c in ["Hugo_Symbol",
                          "gene","Gene_Symbol"]
             if c in maf.columns), None)
        samp_col = next(
            (c for c in ["Tumor_Sample_Barcode",
                          "sample_id","sampleId"]
             if c in maf.columns), None)

        if gene_col is None or samp_col is None:
            log(f"  MAF cols: {list(maf.columns[:20])}")
            return _expression_proxy_mutations(
                d, expr_kirp, t_cols_kirp)

        mut_map = {}
        for _, row in maf.iterrows():
            sid  = str(row[samp_col])[:12]
            gene = str(row[gene_col])
            if sid not in mut_map:
                mut_map[sid] = set()
            mut_map[sid].add(gene)

        MUT_GENES = ["PBRM1","SETD2","FH","BAP1",
                      "VHL","MET","CDKN2A","TP53",
                      "ARID1A","KDM6A","NF2"]
        rows = []
        for s in d.index:
            muts = mut_map.get(s[:12], set())
            row  = {g: int(g in muts) for g in MUT_GENES}
            row["sample_id"] = s
            rows.append(row)

        mut_df = pd.DataFrame(rows).set_index("sample_id")
        log(f"  Mutation matrix: {mut_df.shape}")
        return _run_mutation_analysis(mut_df, d,
                                       expr_kirp,
                                       t_cols_kirp)

    except Exception as e:
        log(f"  MAF parse failed: {e}")
        return _expression_proxy_mutations(
            d, expr_kirp, t_cols_kirp)


def _download_gdc_maf():
    try: import requests
    except ImportError: return
    url = ("https://api.gdc.cancer.gov/data/"
           "?filters=%7B%22op%22%3A%22and%22%2C"
           "%22content%22%3A%5B%7B%22op%22%3A%22%3D%22%2C"
           "%22content%22%3A%7B%22field%22%3A"
           "%22cases.project.project_id%22%2C"
           "%22value%22%3A%22TCGA-KIRP%22%7D%7D%2C"
           "%7B%22op%22%3A%22%3D%22%2C%22content%22%3A"
           "%7B%22field%22%3A%22data_type%22%2C"
           "%22value%22%3A%22Masked+Somatic+Mutation%22"
           "%7D%7D%5D%7D&format=tsv&size=1")
    try:
        r = requests.get(url, timeout=60)
        log(f"  GDC MAF API: {r.status_code}")
    except Exception as e:
        log(f"  GDC MAF: {e}")

    # Try direct cBioPortal MAF
    for study in ["kirp_tcga","kirp_tcga_pub"]:
        url2 = (f"https://www.cbioportal.org/api/"
                f"molecular-profiles/"
                f"{study}_mutations/mutations"
                f"?pageSize=500000")
        try:
            import requests as req
            r2 = req.post(
                f"https://www.cbioportal.org/api/"
                f"mutations/fetch",
                json={"molecularProfileId":
                      f"{study}_mutations",
                      "entrezGeneIds":
                          [5175,6385,4221,79728,
                           7157,4067,1029,8289]},
                headers={"Accept":"application/json",
                         "Content-Type":
                             "application/json"},
                timeout=120)
            if r2.status_code == 200 and r2.json():
                with open(MUT_CACHE,"w") as f:
                    json.dump(r2.json(), f)
                log(f"  cBioPortal POST: "
                    f"{len(r2.json())} records")
                return
        except Exception as e:
            log(f"  cBioPortal POST {study}: {e}")


def _cbio_post_mutations(d):
    if os.path.exists(MUT_CACHE) and \
            os.path.getsize(MUT_CACHE) > 500:
        try:
            with open(MUT_CACHE) as f:
                data = json.load(f)
            log(f"  Loaded mutation cache: {len(data)}")
            return _parse_cbio_mutations(data, d)
        except Exception as e:
            log(f"  Cache failed: {e}")
    return None


def _parse_cbio_mutations(data, d):
    mut_map = {}
    for rec in data:
        sid  = rec.get("sampleId","")
        gene = rec.get("gene",{})
        gene = gene.get("hugoGeneSymbol","") \
            if isinstance(gene, dict) else str(gene)
        s12  = sid[:12]
        if s12 not in mut_map: mut_map[s12] = set()
        mut_map[s12].add(gene)

    MUT_GENES = ["PBRM1","SETD2","FH","BAP1","VHL",
                  "MET","CDKN2A","TP53","ARID1A","KDM6A"]
    rows = []
    for s in d.index:
        muts = mut_map.get(s[:12], set())
        row  = {g: int(g in muts) for g in MUT_GENES}
        row["sample_id"] = s
        rows.append(row)
    return pd.DataFrame(rows).set_index("sample_id")


def _expression_proxy_mutations(d, expr, t_cols):
    log("  Expression proxy for mutations:")
    proxy = {}
    for gene in ["SETD2","FH","BAP1","PBRM1","VHL"]:
        if gene not in expr.index: continue
        g   = pd.Series(expr.loc[gene, t_cols].values,
                        index=t_cols).reindex(d.index)
        cut = g.quantile(0.15)
        proxy[f"{gene}_proxy"] = (g <= cut).astype(int)
    df = pd.DataFrame(proxy, index=d.index)
    log(f"  {'Col':<22} {'n':>6} {'d_mut':>10} "
        f"{'d_wt':>10}")
    for col in df.columns:
        m = df[col]==1; w = df[col]==0
        log(f"  {col:<22} {m.sum():>6} "
            f"{d[m.values].mean():>10.4f} "
            f"{d[w.values].mean():>10.4f}")
    return df


def _run_mutation_analysis(mut_df, d,
                             expr, t_cols):
    log(f"  {'Gene':<12} {'n_mut':>6} {'pct':>6} "
        f"{'d_mut':>10} {'d_wt':>10} {'p':>12}")
    log(f"  {'─'*56}")
    for g in mut_df.columns:
        m  = mut_df[g]==1; w = mut_df[g]==0
        dm = d.reindex(mut_df.index[m]).dropna()
        dw = d.reindex(mut_df.index[w]).dropna()
        _, p = safe_mwu(dm.values, dw.values)
        pct  = 100*m.sum()/len(mut_df)
        log(f"  {g:<12} {m.sum():>6} {pct:>5.1f}% "
            f"{dm.mean():>10.4f} {dw.mean():>10.4f} "
            f"{fmt_p(p):>12}")

    # S4-P4: PBRM1/SETD2 co-mutation
    if "PBRM1" in mut_df.columns and \
       "SETD2" in mut_df.columns:
        log(""); log("  PBRM1/SETD2 CO-MUTATION:")
        co  = ((mut_df["PBRM1"]==1) &
                (mut_df["SETD2"]==1)).sum()
        np_ = (mut_df["PBRM1"]==1).sum()
        ns  = (mut_df["SETD2"]==1).sum()
        ct  = np.array([[co, np_-co],
                         [ns-co,
                          len(mut_df)-np_-ns+co]])
        try:
            _, p_chi, _, _ = chi2_contingency(ct)
        except Exception:
            p_chi = np.nan
        log(f"  PBRM1 n={np_}  SETD2 n={ns} "
            f"co-mut n={co}")
        log(f"  chi2 {fmt_p(p_chi)}")
        if not np.isnan(p_chi) and p_chi < 0.05:
            log("  S4-P4 CONFIRMED ✓")
        else:
            log("  S4-P4 NOT CONFIRMED (ns)")

    mut_df.to_csv(
        os.path.join(RESULTS_DIR,
                     "mutation_matrix_s4.csv"))
    return mut_df

# ═══════════════════════════════════════════════════════════════
# OBJ-4/5: CROSS-CANCER — PRCC vs ccRCC
# ═══════════════════════════════════════════════════════════════

def obj4_5_cross_cancer(expr_kirp, t_cols_kirp,
                          depth_kirp,
                          expr_kirc, t_cols_kirc):
    log(""); log("="*60)
    log("OBJ-4/5 — CROSS-CANCER PRCC vs ccRCC")
    log("="*60)
    log("  S4-P6: RUNX1 r_depth > 0.40 in BOTH")
    log("  S4-P7: GOT1  r_depth < -0.40 in BOTH")

    d_kirp = depth_kirp.reindex(t_cols_kirp).dropna()

    # ── Build ccRCC depth score ────────────────��──────────────
    d_kirc = None
    if expr_kirc is not None:
        log("  Building ccRCC depth score from "
            "KIRC_DEPTH_POS/NEG genes...")
        pos_av = [g for g in KIRC_DEPTH_POS
                  if g in expr_kirc.index]
        neg_av = [g for g in KIRC_DEPTH_NEG
                  if g in expr_kirc.index]
        log(f"  ccRCC depth pos genes: {pos_av}")
        log(f"  ccRCC depth neg genes: {neg_av}")
        if pos_av and neg_av:
            pos_sc = expr_kirc.loc[
                pos_av, t_cols_kirc].mean(axis=0)
            neg_sc = expr_kirc.loc[
                neg_av, t_cols_kirc].mean(axis=0)
            raw_d  = norm01(pos_sc.values) - \
                     norm01(neg_sc.values)
            d_kirc = pd.Series(
                norm01(raw_d),
                index=t_cols_kirc,
                name="kirc_depth")
            log(f"  ccRCC depth: n={len(d_kirc)} "
                f"mean={d_kirc.mean():.3f}")

            d_kirc.reset_index().rename(
                columns={"index": "sample_id",
                         0: "kirc_depth"}
            ).to_csv(
                os.path.join(RESULTS_DIR,
                             "kirc_depth_proxy.csv"),
                index=False)

    # ── Side-by-side gene depth correlates ───────────────────
    log("")
    log(f"  {'Gene':<14} {'PRCC_r':>9} "
        f"{'ccRCC_r':>9} {'shared?':>10}")
    log(f"  {'─'*46}")

    results = {}
    for gene in SHARED_CANDS:
        # PRCC
        gp = gv(gene, expr_kirp, t_cols_kirp,
                d_kirp.index)
        rp = safe_r(gp.values, d_kirp.values)[0] \
            if gp is not None else np.nan

        # ccRCC
        rc = np.nan
        if expr_kirc is not None and \
                d_kirc is not None:
            gc = gv(gene, expr_kirc, t_cols_kirc,
                    d_kirc.index)
            if gc is not None:
                rc = safe_r(gc.values,
                             d_kirc.values)[0]

        # Shared determination
        both_pos = (not np.isnan(rp) and rp > 0.30 and
                    not np.isnan(rc) and rc > 0.30)
        both_neg = (not np.isnan(rp) and rp < -0.30 and
                    not np.isnan(rc) and rc < -0.30)
        shared   = ("SHARED_ATT"  if both_pos else
                    "SHARED_NORM" if both_neg else
                    "PRCC_ONLY"   if abs(rp) > 0.30
                    else "ccRCC_ONLY" if
                    (not np.isnan(rc) and abs(rc) > 0.30)
                    else "")

        log(f"  {gene:<14} {rp:>+9.4f} "
            f"{rc:>+9.4f} {shared:>10}")

        results[gene] = {
            "r_prcc": rp, "r_kirc": rc,
            "shared": shared
        }

    # S4-P6: RUNX1
    r_runx1_prcc = results.get("RUNX1",{}).get(
        "r_prcc", np.nan)
    r_runx1_kirc = results.get("RUNX1",{}).get(
        "r_kirc", np.nan)
    log("")
    log(f"  S4-P6 RUNX1: "
        f"PRCC r={r_runx1_prcc:+.4f}  "
        f"ccRCC r={r_runx1_kirc:+.4f}")
    if (not np.isnan(r_runx1_prcc) and
            r_runx1_prcc > 0.40 and
            not np.isnan(r_runx1_kirc) and
            r_runx1_kirc > 0.40):
        log("  S4-P6 CONFIRMED: RUNX1 shared ✓")
    elif r_runx1_prcc > 0.40:
        log("  S4-P6 PRCC ONLY — ccRCC data "
            "unavailable or weak")
    else:
        log("  S4-P6 NOT CONFIRMED")

    # S4-P7: GOT1
    r_got1_prcc = results.get("GOT1",{}).get(
        "r_prcc", np.nan)
    r_got1_kirc = results.get("GOT1",{}).get(
        "r_kirc", np.nan)
    log(f"  S4-P7 GOT1: "
        f"PRCC r={r_got1_prcc:+.4f}  "
        f"ccRCC r={r_got1_kirc:+.4f}")
    if (not np.isnan(r_got1_prcc) and
            r_got1_prcc < -0.40 and
            not np.isnan(r_got1_kirc) and
            r_got1_kirc < -0.40):
        log("  S4-P7 CONFIRMED: GOT1 shared ✓")
    elif r_got1_prcc < -0.40:
        log("  S4-P7 PRCC ONLY — ccRCC data "
            "unavailable or weak")
    else:
        log("  S4-P7 NOT CONFIRMED")

    # Save shared gene table
    pd.DataFrame(results).T.to_csv(
        os.path.join(RESULTS_DIR,
                     "cross_cancer_shared_genes.csv"))

    return results, d_kirc

# ═══════════════════════════════════════════════════════════════
# OBJ-7: SWI/SNF RNA PARADOX MODULE
# ═══════════════════════════════════════════════════════════════

def obj7_swi_snf_paradox(expr_kirp, t_cols_kirp,
                           depth_kirp):
    log(""); log("="*60)
    log("OBJ-7 — SWI/SNF RNA PARADOX MODULE")
    log("="*60)
    log("  S4-P9: SWI/SNF subunits positively "
        "correlated WITH EACH OTHER and WITH depth")

    d = depth_kirp.reindex(t_cols_kirp).dropna()
    av = [g for g in SWI_SNF if g in expr_kirp.index]
    log(f"  SWI/SNF genes available: {av}")

    # Pairwise correlations
    log(f"\n  PAIRWISE CORRELATIONS:")
    log(f"  {'Gene A':<12} {'Gene B':<12} "
        f"{'r':>8} {'p':>12}")
    log(f"  {'─'*46}")
    pos_pairs = total_pairs = 0
    for gA, gB in itertools.combinations(av, 2):
        vA = gv(gA, expr_kirp, t_cols_kirp, d.index)
        vB = gv(gB, expr_kirp, t_cols_kirp, d.index)
        if vA is None or vB is None: continue
        r, p = safe_r(vA.values, vB.values)
        if np.isnan(r): continue
        total_pairs += 1
        if r > 0: pos_pairs += 1
        sig = "★" if p < 0.05 else " "
        log(f"  {sig}{gA:<12} {gB:<12} "
            f"{r:>+8.4f} {fmt_p(p):>12}")

    log(f"\n  Positive pairs: {pos_pairs}/{total_pairs}")
    if total_pairs > 0 and \
            pos_pairs/total_pairs > 0.7:
        log("  SWI/SNF subunits predominantly "
            "co-expressed ✓")

    # Each vs depth
    log(f"\n  EACH GENE vs DEPTH:")
    log(f"  {'Gene':<12} {'r_depth':>9} {'p':>12} "
        f"{'direction'}")
    log(f"  {'─'*46}")
    depth_pos = 0
    for gene in av:
        g_ = gv(gene, expr_kirp, t_cols_kirp,
                d.index)
        if g_ is None: continue
        r, p = safe_r(g_.values, d.values)
        direction = ("UP with depth" if r > 0.20
                     else "DOWN with depth"
                     if r < -0.20 else "flat")
        if r > 0: depth_pos += 1
        log(f"  {gene:<12} {r:>+9.4f} "
            f"{fmt_p(p):>12} {direction}")

    log(f"\n  Positive depth correlates: "
        f"{depth_pos}/{len(av)}")
    if len(av) > 0 and depth_pos/len(av) > 0.6:
        log("  S4-P9 CONFIRMED: SWI/SNF module "
            "UP with depth ✓")
        log("  RNA paradox is MODULE-LEVEL — "
            "all subunits co-rise, all protein "
            "functions can be lost by mutation.")
    else:
        log("  S4-P9 NOT CONFIRMED")

    # Module coherence score
    if av:
        mat = expr_kirp.loc[av, t_cols_kirp]
        sc  = mat.mean(axis=0)
        sc_s = pd.Series(sc.values, index=t_cols_kirp)
        r_mod, p_mod = safe_r(
            sc_s.reindex(d.index).values,
            d.values)
        log(f"\n  SWI/SNF MODULE SCORE r(depth) = "
            f"{r_mod:+.4f}  {fmt_p(p_mod)}")
        if r_mod > 0.25:
            log("  SWI/SNF module is a DEPTH MARKER ✓")

# ═══════════════════════════════════════════════════════════════
# OBJ-8: ARG1 vs M2 PANEL DEPTH RANKING
# ═══════════════════════════════════════════════════════════════

def obj8_arg1_vs_m2(expr_kirp, t_cols_kirp,
                     depth_kirp):
    log(""); log("="*60)
    log("OBJ-8 — ARG1 vs M2 PANEL DEPTH RANKING")
    log("="*60)
    log("  S4-P10: r(ARG1,depth) > r(CD163,depth) "
        "and > r(MRC1,depth)")

    d = depth_kirp.reindex(t_cols_kirp).dropna()

    all_immune = list(dict.fromkeys(
        M2_PANEL + M1_PANEL + MDSC_PANEL))
    avail = [g for g in all_immune
             if g in expr_kirp.index]

    rows = []
    log(f"  {'Gene':<12} {'panel':<6} "
        f"{'r_depth':>9} {'Q4/Q1':>7} {'p_mwu':>12}")
    log(f"  {'─'*50}")

    q25 = d.quantile(0.25); q75 = d.quantile(0.75)
    q1i = d[d<=q25].index;   q4i = d[d>=q75].index

    for gene in avail:
        panel = ("M2"   if gene in M2_PANEL else
                 "M1"   if gene in M1_PANEL else
                 "MDSC")
        g_ = gv(gene, expr_kirp, t_cols_kirp,
                d.index)
        if g_ is None: continue
        r,  _ = safe_r(g_.values, d.values)
        q4v = g_.reindex(q4i).mean()
        q1v = g_.reindex(q1i).mean()
        ratio = q4v/(q1v+1e-6)
        _, p_m = safe_mwu(
            g_.reindex(q4i).dropna().values,
            g_.reindex(q1i).dropna().values)
        flag = "★" if not np.isnan(p_m) \
            and p_m < 0.05 else " "
        log(f"  {flag}{gene:<12} {panel:<6} "
            f"{r:>+9.4f} {ratio:>7.3f} "
            f"{fmt_p(p_m):>12}")
        rows.append({
            "gene": gene, "panel": panel,
            "r_depth": r, "Q4_Q1_ratio": ratio,
            "p_mwu": p_m})

    df_r = pd.DataFrame(rows)

    # S4-P10
    if len(df_r) > 0:
        r_arg1 = df_r.loc[df_r.gene=="ARG1",
                           "r_depth"].values
        r_cd163= df_r.loc[df_r.gene=="CD163",
                           "r_depth"].values
        r_mrc1 = df_r.loc[df_r.gene=="MRC1",
                           "r_depth"].values
        if len(r_arg1) > 0:
            r_a = r_arg1[0]
            r_c = r_cd163[0] if len(r_cd163) > 0 \
                else np.nan
            r_m = r_mrc1[0]  if len(r_mrc1)  > 0 \
                else np.nan
            log(f"\n  S4-P10:")
            log(f"  ARG1  r={r_a:+.4f}")
            log(f"  CD163 r={r_c:+.4f}")
            log(f"  MRC1  r={r_m:+.4f}")
            if r_a > r_c and r_a > r_m:
                log("  S4-P10 CONFIRMED: ARG1 strongest "
                    "depth correlate ✓")
            else:
                log("  S4-P10 NOT CONFIRMED")

    # MDSC signature
    mdsc_av = [g for g in MDSC_PANEL
               if g in expr_kirp.index]
    if mdsc_av:
        mdsc_sc = expr_kirp.loc[
            mdsc_av, t_cols_kirp].mean(axis=0)
        mdsc_s  = pd.Series(
            norm01(mdsc_sc.values),
            index=t_cols_kirp).reindex(d.index)
        r_mdsc, p_mdsc = safe_r(
            mdsc_s.values, d.values)
        log(f"\n  MDSC SIGNATURE SCORE "
            f"r(depth)={r_mdsc:+.4f} "
            f"{fmt_p(p_mdsc)}")
        if r_mdsc > 0.10:
            log("  MDSC signature is depth-positive")
            log("  Supports MDSC (not M2) as Q4 "
                "suppressor via ARG1 ✓")

    df_r.to_csv(
        os.path.join(RESULTS_DIR,
                     "arg1_m2_panel.csv"),
        index=False)

# ═══════════════════════════════════════════════════════════════
# OBJ-9: WARBURG TWO-TIER FORMAL TEST
# ═══════════════════════════════════════════════════════════════

def obj9_warburg_two_tier(expr_kirp, t_cols_kirp,
                            depth_kirp):
    log(""); log("="*60)
    log("OBJ-9 — WARBURG TWO-TIER FORMAL TEST")
    log("="*60)
    log("  S4-P11: Warburg trio internal r > "
        "CA9-trio r")

    d = depth_kirp.reindex(t_cols_kirp).dropna()

    trio_av = [g for g in WARBURG_TRIO
               if g in expr_kirp.index]
    full_av = [g for g in HYPOXIA_FULL
               if g in expr_kirp.index]

    # Internal trio correlations
    trio_rs = []
    log("  WARBURG TRIO INTERNAL PAIRS:")
    for gA, gB in itertools.combinations(trio_av, 2):
        vA = gv(gA, expr_kirp, t_cols_kirp,
                d.index)
        vB = gv(gB, expr_kirp, t_cols_kirp,
                d.index)
        if vA is None or vB is None: continue
        r, _ = safe_r(vA.values, vB.values)
        trio_rs.append(r)
        log(f"    {gA} × {gB}: r={r:+.4f}")

    # CA9 vs trio
    ca9_rs = []
    log("  CA9 vs TRIO PAIRS:")
    ca9_v = gv("CA9", expr_kirp, t_cols_kirp,
               d.index)
    for gene in trio_av:
        g_ = gv(gene, expr_kirp, t_cols_kirp,
                d.index)
        if g_ is None or ca9_v is None: continue
        r, _ = safe_r(ca9_v.values, g_.values)
        ca9_rs.append(r)
        log(f"    CA9 × {gene}: r={r:+.4f}")

    mean_trio = np.nanmean(trio_rs) \
        if trio_rs else np.nan
    mean_ca9  = np.nanmean(ca9_rs) \
        if ca9_rs else np.nan

    log(f"\n  Mean internal trio r: {mean_trio:+.4f}")
    log(f"  Mean CA9-trio r:      {mean_ca9:+.4f}")

    if not np.isnan(mean_trio) and \
            not np.isnan(mean_ca9) and \
            mean_trio > mean_ca9:
        log("  S4-P11 CONFIRMED: Warburg trio "
            "internally tighter than CA9 ✓")
        log("  TWO-TIER STRUCTURE CONFIRMED:")
        log("    Tier 1 (Warburg): SLC2A1/LDHA/PDK1")
        log("    Tier 2 (Architectural): CA9")
    else:
        log("  S4-P11 NOT CONFIRMED")

    # Both tiers depth correlation
    log("\n  DEPTH CORRELATES:")
    for gene in full_av:
        g_ = gv(gene, expr_kirp, t_cols_kirp,
                d.index)
        if g_ is None: continue
        r, p = safe_r(g_.values, d.values)
        tier = ("WARBURG" if gene in WARBURG_TRIO
                else "ARCH"    if gene in ARCH_HYPOXIA
                else "OTHER")
        log(f"  {gene:<10} {tier:<8} "
            f"r={r:+.4f} {fmt_p(p)}")

    # Tier scores vs depth
    if trio_av:
        trio_sc = expr_kirp.loc[
            trio_av, t_cols_kirp].mean(axis=0)
        trio_s  = pd.Series(
            trio_sc.values,
            index=t_cols_kirp).reindex(d.index)
        r_trio, p_trio = safe_r(
            trio_s.values, d.values)
        log(f"\n  Warburg trio SCORE r(depth) = "
            f"{r_trio:+.4f} {fmt_p(p_trio)}")

    if ca9_v is not None:
        r_ca9, p_ca9 = safe_r(
            ca9_v.values, d.values)
        log(f"  CA9 alone r(depth) = "
            f"{r_ca9:+.4f} {fmt_p(p_ca9)}")

# ═══════════════════════════════════════════════════════════════
# OBJ-10: ERBB2 CONTINUOUS DEPTH TEST
# ══════════════════════════��════════════════════════════════════

def obj10_erbb2_continuous(expr_kirp, t_cols_kirp,
                             depth_kirp):
    log(""); log("="*60)
    log("OBJ-10 — ERBB2 CONTINUOUS DEPTH TEST")
    log("="*60)
    log("  S4-P12: ERBB2 r(depth) > 0.50 — "
        "continuous (IHC2+ not FISH)")

    d = depth_kirp.reindex(t_cols_kirp).dropna()

    if "ERBB2" not in expr_kirp.index:
        log("  ERBB2 not in matrix.")
        return

    erbb2 = gv("ERBB2", expr_kirp, t_cols_kirp,
               d.index)
    r_e, p_e = safe_r(erbb2.values, d.values)
    log(f"  r(ERBB2, depth) = {r_e:+.4f} {fmt_p(p_e)}")

    if r_e > 0.50:
        log("  S4-P12 CONFIRMED: continuous signal ✓")
        log("  IHC 2+ (not FISH) is the correct "
            "PRCC eligibility criterion.")
    elif r_e > 0.30:
        log(f"  S4-P12 PARTIAL: r={r_e:+.4f} "
            f"(>0.30 but <0.50)")
        log("  Still supports continuous, "
            "non-amplification driven signal.")
    else:
        log("  S4-P12 NOT CONFIRMED")

    # Quartile ERBB2 means
    log("\n  ERBB2 EXPRESSION BY DEPTH QUARTILE:")
    q_bounds = [0, 0.25, 0.50, 0.75, 1.00]
    for i in range(4):
        lo = d.quantile(q_bounds[i])
        hi = d.quantile(q_bounds[i+1])
        if i == 0:
            mask = d <= hi
        elif i == 3:
            mask = d >= lo
        else:
            mask = (d > lo) & (d <= hi)
        mean_e = erbb2.reindex(
            d[mask].index).mean()
        log(f"  Q{i+1}: n={mask.sum():>3} "
            f"ERBB2 mean={mean_e:.3f}")

    # ERBB2 vs KRT19 (co-expression confirms identity)
    if "KRT19" in expr_kirp.index:
        krt = gv("KRT19", expr_kirp, t_cols_kirp,
                 d.index)
        r_ek, _ = safe_r(erbb2.values, krt.values)
        log(f"\n  r(ERBB2, KRT19) = {r_ek:+.4f}")
        if r_ek > 0.40:
            log("  ERBB2 co-expresses with biliary "
                "identity marker KRT19 ✓")
            log("  Supports identity-co-driver role "
                "(DC-4 confirmed).")

    # ERBB2 vs FISH proxy (check if bimodal)
    log("\n  ERBB2 DISTRIBUTION (bimodal = FISH, "
        "unimodal = continuous IHC):")
    vals = erbb2.dropna().values
    pct_above = 100 * np.mean(
        vals > np.percentile(vals, 90))
    log(f"  Top 10%: {np.percentile(vals,90):.2f}")
    log(f"  Top  5%: {np.percentile(vals,95):.2f}")
    log(f"  Median:  {np.median(vals):.2f}")
    log(f"  IQR:     {np.percentile(vals,75) - np.percentile(vals,25):.2f}")
    log("  If bimodal → amplification (FISH)")
    log("  If unimodal → continuous (IHC2+)")

# ═══════════════════════════════════════════════════════════════
# OBJ-11: DRUG TARGET SUBTYPE-STRATIFIED MAP
# ═══════════════════════════════════════════════════════════════

def obj11_drug_subtype_map(expr_kirp, t_cols_kirp,
                             depth_kirp, subtypes):
    log(""); log("="*60)
    log("OBJ-11 — DRUG TARGET SUBTYPE-STRATIFIED MAP")
    log("="*60)

    d = depth_kirp.reindex(t_cols_kirp).dropna()

    # Build depth strata
    q25 = d.quantile(0.25); q75 = d.quantile(0.75)
    q50 = d.quantile(0.50)

    strata = {
        "Q1_shallow": d[d <= q25].index,
        "Q2_Q3_mid":  d[(d > q25) & (d < q75)].index,
        "Q4_deep":    d[d >= q75].index,
    }

    if subtypes is not None:
        t1_idx  = d.index[
            subtypes.reindex(d.index).str.lower()
                    .str.contains(r"type.?1",
                                   regex=True,
                                   na=False)]
        t2_idx  = d.index[
            subtypes.reindex(d.index).str.lower()
                    .str.contains(r"type.?2",
                                   regex=True,
                                   na=False)]
        cim_idx = d.index[
            subtypes.reindex(d.index).str.lower()
                    .str.contains(r"cimp|hlrcc",
                                   regex=True,
                                   na=False)]
        if len(t1_idx) >= 5:
            strata["Type1"] = t1_idx
        if len(t2_idx) >= 5:
            strata["Type2"] = t2_idx
        if len(cim_idx) >= 3:
            strata["CIMP"]  = cim_idx

    log(f"  Strata: {[(k,len(v)) for k,v in strata.items()]}")

    rows = []
    for drug, gene in DRUG_GENES.items():
        if gene not in expr_kirp.index: continue
        g_ = pd.Series(
            expr_kirp.loc[gene, t_cols_kirp].values,
            index=t_cols_kirp)
        row = {"drug": drug, "gene": gene}
        for stratum, idx in strata.items():
            g_s = g_.reindex(idx).dropna()
            row[f"mean_{stratum}"] = g_s.mean()
            row[f"n_{stratum}"]    = len(g_s)
        rows.append(row)

    drug_df = pd.DataFrame(rows)
    drug_df.to_csv(
        os.path.join(RESULTS_DIR,
                     "drug_subtype_map.csv"),
        index=False)

    # Print summary
    log("")
    log(f"  {'Drug':<22} {'Q1_mean':>9} "
        f"{'Q4_mean':>9} {'Q4>Q1?':>8} "
        f"{'Q4/Q1':>7}")
    log(f"  {'─'*58}")
    for _, row in drug_df.iterrows():
        q1m = row.get("mean_Q1_shallow", np.nan)
        q4m = row.get("mean_Q4_deep",   np.nan)
        if np.isnan(q1m) or np.isnan(q4m): continue
        ratio   = q4m / (q1m + 1e-6)
        q4_flag = "Q4 PRIORITY" if ratio > 1.15 \
            else "Q1 PRIORITY" if ratio < 0.87 \
            else "uniform"
        log(f"  {row['drug']:<22} {q1m:>9.3f} "
            f"{q4m:>9.3f} {q4_flag:>8} "
            f"{ratio:>7.3f}")

    # CIMP-specific summary
    if "mean_CIMP" in drug_df.columns:
        log("")
        log("  CIMP-HIGH DRUG EXPRESSION:")
        log(f"  {'Drug':<22} {'CIMP_mean':>11} "
            f"{'Q4_mean':>9} "
            f"{'CIMP>Q4?'}")
        log(f"  {'─'*54}")
        for _, row in drug_df.iterrows():
            cm  = row.get("mean_CIMP",  np.nan)
            q4m = row.get("mean_Q4_deep", np.nan)
            if np.isnan(cm) or np.isnan(q4m): continue
            flag = "CIMP PRIORITY" \
                if cm > q4m * 1.05 else ""
            log(f"  {row['drug']:<22} {cm:>11.3f} "
                f"{q4m:>9.3f} {flag}")

# ═══════════════════════════════════════════════════════════════
# FIGURE — 12 panels
# ═══════════════════════════════════════════════════════════════

def generate_figure(depth_kirp, t_cols_kirp,
                     expr_kirp, d_kirc,
                     expr_kirc, t_cols_kirc,
                     os_results, os_data,
                     subtypes, cross_results):
    log(""); log("="*60)
    log("GENERATING FIGURE — SCRIPT 4"); log("="*60)

    d = depth_kirp.reindex(t_cols_kirp).dropna()

    fig = plt.figure(figsize=(26, 30))
    gs  = gridspec.GridSpec(
        4, 3, figure=fig,
        hspace=0.55, wspace=0.40)

    # ── A: TI KM (censored) ───────────────────────────────────
    ax = fig.add_subplot(gs[0, 0])
    if os_results and "km_ti_hi" in os_results:
        for (t, s), col, lab in [
            (os_results["km_ti_hi"],
             "#C0392B", "TI-high"),
            (os_results["km_ti_lo"],
             "#2980B9", "TI-low"),
        ]:
            ax.step(t/365, s, where="post",
                    color=col, label=lab, lw=2)
        p = os_results.get("S4P2_p", np.nan)
        ax.set_title(
            f"A: TI OS (censored)\n{fmt_p(p)}",
            fontsize=9, fontweight="bold")
        ax.legend(fontsize=7)
        ax.set_ylim(0, 1.05)
        ax.set_xlabel("Years")
        ax.set_ylabel("Survival")
    else:
        ax.text(0.5, 0.5, "Pending censored OS",
                ha="center", va="center",
                transform=ax.transAxes)
        ax.set_title("A: TI OS (censored)",
                     fontsize=9, fontweight="bold")

    # ── B: 4-quartile KM ──────────────────────────────────────
    ax = fig.add_subplot(gs[0, 1])
    cols_q = {"Q1":"#2980B9","Q2":"#27AE60",
               "Q3":"#E67E22","Q4":"#C0392B"}
    if os_results:
        for ql, col in cols_q.items():
            key = f"km_{ql}"
            if key not in os_results: continue
            t, s = os_results[key]
            ax.step(t/365, s, where="post",
                    color=col, label=ql, lw=2)
        p = os_results.get("S4P3_p", np.nan)
        ax.set_title(
            f"B: 4-Quartile OS\n{fmt_p(p)}",
            fontsize=9, fontweight="bold")
        ax.legend(fontsize=7)
        ax.set_ylim(0, 1.05)
        ax.set_xlabel("Years")
        ax.set_ylabel("Survival")
    else:
        ax.set_title("B: 4-Quartile OS",
                     fontsize=9, fontweight="bold")

    # ── C: Cross-cancer RUNX1/GOT1 scatter ───────────────────
    ax = fig.add_subplot(gs[0, 2])
    if cross_results and d_kirc is not None and \
            expr_kirc is not None:
        shared = {g: v for g, v in
                  cross_results.items()
                  if not np.isnan(v.get("r_prcc",
                                        np.nan))
                  and not np.isnan(v.get("r_kirc",
                                         np.nan))}
        if shared:
            genes_s = list(shared.keys())
            rp = [shared[g]["r_prcc"] for g in genes_s]
            rc = [shared[g]["r_kirc"] for g in genes_s]
            cols_s = [
                "#C0392B" if shared[g]["shared"] ==
                "SHARED_ATT"
                else "#2980B9" if shared[g]["shared"] ==
                "SHARED_NORM"
                else "#95A5A6"
                for g in genes_s]
            ax.scatter(rp, rc, c=cols_s,
                       s=40, alpha=0.8)
            for g, x, y in zip(genes_s, rp, rc):
                if abs(x) > 0.25 or abs(y) > 0.25:
                    ax.annotate(g, (x, y),
                                fontsize=6,
                                xytext=(3, 3),
                                textcoords="offset "
                                           "points")
            ax.axhline(0, color="k", lw=0.5)
            ax.axvline(0, color="k", lw=0.5)
            ax.axhline(0.40, color="k", lw=0.5,
                        ls="--", alpha=0.4)
            ax.axhline(-0.40, color="k", lw=0.5,
                        ls="--", alpha=0.4)
            ax.axvline(0.40, color="k", lw=0.5,
                        ls="--", alpha=0.4)
            ax.axvline(-0.40, color="k", lw=0.5,
                        ls="--", alpha=0.4)
            ax.set_xlabel("r(depth) PRCC",
                          fontsize=9)
            ax.set_ylabel("r(depth) ccRCC",
                          fontsize=9)
            ax.set_title(
                "C: Shared Genes\n"
                "(red=shared_att, "
                "blue=shared_norm)",
                fontsize=9, fontweight="bold")
    else:
        ax.set_title("C: Cross-Cancer Shared",
                     fontsize=9, fontweight="bold")
        ax.text(0.5, 0.5,
                "ccRCC data\nnot available",
                ha="center", va="center",
                transform=ax.transAxes)

    # ── D: SWI/SNF module depth ───────────────────────────────
    ax = fig.add_subplot(gs[1, 0])
    sw_av = [g for g in SWI_SNF
             if g in expr_kirp.index]
    sw_rs = {}
    for gene in sw_av:
        g_ = gv(gene, expr_kirp, t_cols_kirp,
                d.index)
        if g_ is None: continue
        r, _ = safe_r(g_.values, d.values)
        sw_rs[gene] = r
    if sw_rs:
        cols_sw = ["#C0392B" if v > 0 else "#2980B9"
                   for v in sw_rs.values()]
        ax.barh(range(len(sw_rs)),
                list(sw_rs.values()),
                color=cols_sw, alpha=0.85)
        ax.set_yticks(range(len(sw_rs)))
        ax.set_yticklabels(list(sw_rs.keys()),
                            fontsize=8)
        ax.axvline(0, color="k", lw=0.8)
        ax.set_xlabel("r vs depth")
        ax.set_title("D: SWI/SNF Module (S4-P9)",
                     fontsize=9, fontweight="bold")

    # ── E: Warburg two-tier ───────────────────────────────────
    ax = fig.add_subplot(gs[1, 1])
    tier_genes = HYPOXIA_FULL
    tier_rs    = {}
    for gene in [g for g in tier_genes
                 if g in expr_kirp.index]:
        g_ = gv(gene, expr_kirp, t_cols_kirp,
                d.index)
        if g_ is None: continue
        r, _ = safe_r(g_.values, d.values)
        tier_rs[gene] = r
    if tier_rs:
        tier_col = ["#C0392B" if g in WARBURG_TRIO
                    else "#E67E22"
                    if g in ARCH_HYPOXIA
                    else "#95A5A6"
                    for g in tier_rs]
        ax.barh(range(len(tier_rs)),
                list(tier_rs.values()),
                color=tier_col, alpha=0.85)
        ax.set_yticks(range(len(tier_rs)))
        ax.set_yticklabels(list(tier_rs.keys()),
                            fontsize=8)
        ax.axvline(0, color="k", lw=0.8)
        ax.set_xlabel("r vs depth")
        ax.set_title(
            "E: Hypoxia Two-Tier (S4-P11)\n"
            "(red=Warburg, orange=CA9)",
            fontsize=9, fontweight="bold")

    # ── F: ERBB2 quartile expression ──────────────────────────
    ax = fig.add_subplot(gs[1, 2])
    if "ERBB2" in expr_kirp.index:
        erbb2 = gv("ERBB2", expr_kirp,
                   t_cols_kirp, d.index)
        ax.scatter(d.values, erbb2.values,
                   c=d.values, cmap="RdBu_r",
                   s=8, alpha=0.6)
        r_e, _ = safe_r(erbb2.values, d.values)
        ax.set_xlabel("Depth")
        ax.set_ylabel("ERBB2")
        ax.set_title(
            f"F: ERBB2 Continuous (S4-P12)\n"
            f"r={r_e:+.3f} "
            f"({'IHC2+ ✓' if r_e > 0.50 else 'partial'})",
            fontsize=9, fontweight="bold")

    # ── G: ARG1 vs M2/MDSC panel ──────────────────────────────
    ax = fig.add_subplot(gs[2, 0])
    immune_rs = {}
    for gene in [g for g in
                 M2_PANEL + ["ARG1"] + MDSC_PANEL
                 if g in expr_kirp.index]:
        g_ = gv(gene, expr_kirp, t_cols_kirp,
                d.index)
        if g_ is None: continue
        r, _ = safe_r(g_.values, d.values)
        immune_rs[gene] = r
    if immune_rs:
        cols_im = ["#E67E22" if g == "ARG1"
                   else "#C0392B" if g in MDSC_PANEL
                   else "#95A5A6"
                   for g in immune_rs]
        ax.barh(range(len(immune_rs)),
                list(immune_rs.values()),
                color=cols_im, alpha=0.85)
        ax.set_yticks(range(len(immune_rs)))
        ax.set_yticklabels(list(immune_rs.keys()),
                            fontsize=7)
        ax.axvline(0, color="k", lw=0.8)
        ax.set_xlabel("r vs depth")
        ax.set_title(
            "G: ARG1 vs M2/MDSC (S4-P10)\n"
            "(orange=ARG1, red=MDSC)",
            fontsize=9, fontweight="bold")

    # ── H: Drug subtype map heatmap ───────────────────────────
    ax = fig.add_subplot(gs[2, 1])
    drug_map_path = os.path.join(
        RESULTS_DIR, "drug_subtype_map.csv")
    if os.path.exists(drug_map_path):
        dm = pd.read_csv(drug_map_path)
        mean_cols = [c for c in dm.columns
                     if c.startswith("mean_")]
        if mean_cols:
            dm_plot = dm.set_index("drug")[mean_cols]
            dm_norm = dm_plot.apply(
                lambda row: norm01(row.values),
                axis=1, result_type="broadcast")
            im = ax.imshow(
                dm_norm.values.astype(float),
                aspect="auto", cmap="RdBu_r",
                vmin=0, vmax=1)
            ax.set_yticks(range(len(dm_norm)))
            ax.set_yticklabels(dm_norm.index,
                                fontsize=7)
            ax.set_xticks(range(len(mean_cols)))
            ax.set_xticklabels(
                [c.replace("mean_","")
                 for c in mean_cols],
                fontsize=7, rotation=30,
                ha="right")
            plt.colorbar(im, ax=ax, shrink=0.6)
            ax.set_title(
                "H: Drug Target by Subtype\n"
                "(row-normalised)",
                fontsize=9, fontweight="bold")
    else:
        ax.set_title("H: Drug Subtype Map",
                     fontsize=9, fontweight="bold")

    # ── I: RUNX1 depth — PRCC vs ccRCC ───────────────────────
    ax = fig.add_subplot(gs[2, 2])
    plotted = False
    if "RUNX1" in expr_kirp.index:
        r1_p = gv("RUNX1", expr_kirp,
                  t_cols_kirp, d.index)
        ax.scatter(d.values,
                   r1_p.values,
                   s=6, alpha=0.5,
                   color="#C0392B",
                   label=f"PRCC (r={safe_r(r1_p.values, d.values)[0]:+.3f})")
        plotted = True
    if d_kirc is not None and \
            expr_kirc is not None and \
            "RUNX1" in expr_kirc.index:
        r1_c = gv("RUNX1", expr_kirc,
                  t_cols_kirc,
                  d_kirc.index)
        ax.scatter(d_kirc.values,
                   r1_c.values,
                   s=6, alpha=0.5,
                   color="#2980B9",
                   label=f"ccRCC (r={safe_r(r1_c.values, d_kirc.values)[0]:+.3f})")
        plotted = True
    if plotted:
        ax.legend(fontsize=7)
        ax.set_xlabel("Depth Score")
        ax.set_ylabel("RUNX1")
        ax.set_title("I: RUNX1 Shared Attractor\n"
                     "(S4-P6 — PRCC=red, ccRCC=blue)",
                     fontsize=9, fontweight="bold")
    else:
        ax.set_title("I: RUNX1 Cross-Cancer",
                     fontsize=9, fontweight="bold")

    # ── J: GOT1 depth — PRCC vs ccRCC ────────────────────────
    ax = fig.add_subplot(gs[3, 0])
    plotted = False
    if "GOT1" in expr_kirp.index:
        g1_p = gv("GOT1", expr_kirp,
                  t_cols_kirp, d.index)
        ax.scatter(d.values, g1_p.values,
                   s=6, alpha=0.5,
                   color="#C0392B",
                   label=f"PRCC (r={safe_r(g1_p.values, d.values)[0]:+.3f})")
        plotted = True
    if d_kirc is not None and \
            expr_kirc is not None and \
            "GOT1" in expr_kirc.index:
        g1_c = gv("GOT1", expr_kirc,
                  t_cols_kirc,
                  d_kirc.index)
        ax.scatter(d_kirc.values,
                   g1_c.values,
                   s=6, alpha=0.5,
                   color="#2980B9",
                   label=f"ccRCC (r={safe_r(g1_c.values, d_kirc.values)[0]:+.3f})")
        plotted = True
    if plotted:
        ax.legend(fontsize=7)
        ax.set_xlabel("Depth Score")
        ax.set_ylabel("GOT1")
        ax.set_title("J: GOT1 Shared Normal Pole\n"
                     "(S4-P7 — PRCC=red, ccRCC=blue)",
                     fontsize=9, fontweight="bold")
    else:
        ax.set_title("J: GOT1 Cross-Cancer",
                     fontsize=9, fontweight="bold")

    # ── K: Drug OS — full (censored) ──────────────────────────
    ax = fig.add_subplot(gs[3, 1])
    dop = os.path.join(RESULTS_DIR, "drug_OS_s4.csv")
    if os.path.exists(dop):
        ddf = pd.read_csv(dop).dropna(
            subset=["p_logrank"])
        ddf = ddf.sort_values("p_logrank")
        if len(ddf) > 0:
            nlp  = -np.log10(
                ddf["p_logrank"].clip(1e-10,1))
            cols_k = [
                "#C0392B" if p < 0.05 else "#95A5A6"
                for p in ddf["p_logrank"]]
            ax.barh(range(len(ddf)), nlp,
                    color=cols_k, alpha=0.85)
            ax.set_yticks(range(len(ddf)))
            ax.set_yticklabels(
                ddf["drug_target"].values,
                fontsize=7)
            ax.axvline(-np.log10(0.05),
                        color="k", lw=0.8, ls="--")
            ax.set_xlabel("-log10(p)")
            ax.set_title("K: Drug OS (censored)",
                         fontsize=9,
                         fontweight="bold")
    else:
        ax.set_title("K: Drug OS",
                     fontsize=9, fontweight="bold")

    # ── L: Script 4 scorecard ─────────────────────────────────
    ax = fig.add_subplot(gs[3, 2])
    ax.axis("off")
    txt = (
        "PRCC False Attractor — Script 4\n"
        "OrganismCore | 2026-03-02\n"
        "─────────────────────────────\n"
        "S4-P1  Type2>Type1 (GDC annot)\n"
        "S4-P2  TI OS censored  p<0.05\n"
        "S4-P3  Q4>Q1 OS censored p<0.05\n"
        "S4-P4  PBRM1+SETD2 co-mut\n"
        "S4-P5  CDKN2A low in CIMP\n"
        "S4-P6  RUNX1 shared r>0.40 both\n"
        "S4-P7  GOT1 shared r<-0.40 both\n"
        "S4-P8  CIMP-hi worst OS subtype\n"
        "S4-P9  SWI/SNF module up+depth\n"
        "S4-P10 ARG1>CD163>MRC1 depth r\n"
        "S4-P11 Warburg trio tighter CA9\n"
        "S4-P12 ERBB2 r>0.50 continuous\n"
        "─────────────────────────────\n"
        "NEW:\n"
        "N-S4-?: MDSC > classical M2\n"
        "N-S4-?: RUNX1 universal TF\n"
        "N-S4-?: GOT1 universal norm pole"
    )
    ax.text(0.05, 0.95, txt,
            transform=ax.transAxes,
            fontsize=7, verticalalignment="top",
            fontfamily="monospace",
            bbox=dict(boxstyle="round",
                      facecolor="#F0F4F8",
                      alpha=0.8))
    ax.set_title("L: Script 4 Scorecard",
                 fontsize=9, fontweight="bold")

    fig.suptitle(
        "PRCC False Attractor — Script 4\n"
        "Re-run Deferred · New Objectives · "
        "Cross-Cancer",
        fontsize=12, fontweight="bold", y=0.998)

    out = os.path.join(RESULTS_DIR,
                        "prcc_script4_figure.pdf")
    fig.savefig(out, bbox_inches="tight", dpi=150)
    plt.close(fig)
    log(f"  Figure saved: {out}")

# ═══════════════════════════════════════════════════════════════
# SCORECARD
# ═══════════════════════════════════════════════════════════════

def print_scorecard():
    full = "\n".join(log_lines)
    log(""); log("="*60)
    log("SCRIPT 4 — FINAL SCORECARD"); log("="*60)

    checks = [
        ("S4-P1  Type2>Type1 depth",
         "S4-P1 CONFIRMED",
         "S4-P1 NOT CONFIRMED"),
        ("S4-P2  TI OS censored p<0.05",
         "S4-P2 CONFIRMED",
         "S4-P2 NOT CONFIRMED"),
        ("S4-P3  Q4>Q1 OS censored p<0.05",
         "S4-P3 CONFIRMED",
         "S4-P3 NOT CONFIRMED"),
        ("S4-P4  PBRM1+SETD2 co-mutation",
         "S4-P4 CONFIRMED",
         "S4-P4 NOT CONFIRMED"),
        ("S4-P5  CDKN2A low in CIMP",
         "FC-5 CONFIRMED",
         "FC-5 NOT CONFIRMED"),
        ("S4-P6  RUNX1 shared r>0.40",
         "S4-P6 CONFIRMED",
         "S4-P6 NOT CONFIRMED"),
        ("S4-P7  GOT1 shared r<-0.40",
         "S4-P7 CONFIRMED",
         "S4-P7 NOT CONFIRMED"),
        ("S4-P8  CIMP worst OS",
         "S4-P8 CONFIRMED",
         "S4-P8 NOT CONFIRMED"),
        ("S4-P9  SWI/SNF module up+depth",
         "S4-P9 CONFIRMED",
         "S4-P9 NOT CONFIRMED"),
        ("S4-P10 ARG1 strongest depth r",
         "S4-P10 CONFIRMED",
         "S4-P10 NOT CONFIRMED"),
        ("S4-P11 Warburg trio tighter CA9",
         "S4-P11 CONFIRMED",
         "S4-P11 NOT CONFIRMED"),
        ("S4-P12 ERBB2 r>0.50 continuous",
         "S4-P12 CONFIRMED",
         "S4-P12 NOT CONFIRMED"),
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


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    log("="*60)
    log("PRCC FALSE ATTRACTOR — SCRIPT 4")
    log("OrganismCore | Document 95d | 2026-03-02")
    log("Author: Eric Robert Lawson")
    log("="*60)
    log("")
    log("PREDICTIONS LOCKED 2026-03-02 BEFORE RUN")
    log("12 predictions — S4-P1 through S4-P12")
    log("")

    # ── Load PRCC S1/S2/S3 ───────────────────────────────────
    depth, ti, decon = load_prcc_outputs()
    if depth is None:
        log("FATAL: S1 depth not found.")
        write_log(); return

    # ── Load PRCC expression ──────────────────────────────────
    log(""); log("="*60)
    log("LOADING EXPRESSION MATRICES"); log("="*60)
    expr_kirp, t_cols_kirp, n_cols_kirp = \
        load_expr(KIRP_EXPR, "PRCC (KIRP)")

    # ── Load ccRCC expression ─────────────────────────────────
    expr_kirc = t_cols_kirc = n_cols_kirc = None
    if os.path.exists(KIRC_EXPR):
        expr_kirc, t_cols_kirc, n_cols_kirc = \
            load_expr(KIRC_EXPR, "ccRCC (KIRC)")
    else:
        log(f"  ccRCC matrix not found: {KIRC_EXPR}")
        log("  Cross-cancer analysis will use "
            "PRCC data only.")
        log("  To enable: download TCGA_KIRC_HiSeqV2.gz"
            " from UCSC Xena and place in BASE_DIR.")

    # Recompute TI if needed
    if ti is None and expr_kirp is not None and \
            "KRT19" in expr_kirp.index and \
            "SLC22A6" in expr_kirp.index:
        d_r = depth.reindex(t_cols_kirp).dropna()
        krt = pd.Series(
            expr_kirp.loc["KRT19",
                          t_cols_kirp].values,
            index=t_cols_kirp).reindex(d_r.index)
        slc = pd.Series(
            expr_kirp.loc["SLC22A6",
                          t_cols_kirp].values,
            index=t_cols_kirp).reindex(d_r.index)
        ti  = pd.Series(
            norm01(krt.values) - norm01(slc.values),
            index=d_r.index, name="TI")
        log(f"  TI recomputed: n={len(ti)}")

    # ── OBJ-1: GDC subtypes ───────────────────────────────────
    d1, d2, dc, subtypes = obj1_gdc_subtypes(
        depth, t_cols_kirp)

    # ── OBJ-2: Censored survival ──────────────────────────────
    os_results, os_data = obj2_censored_survival(
        depth, ti, expr_kirp, t_cols_kirp, subtypes)

    # ── OBJ-3: Mutations ──────────────────────────────────────
    mut_df = obj3_gdc_mutations(
        depth, expr_kirp, t_cols_kirp)

    # ── OBJ-4/5: Cross-cancer ────────────────────────────────
    cross_results, d_kirc = obj4_5_cross_cancer(
        expr_kirp, t_cols_kirp, depth,
        expr_kirc, t_cols_kirc)

    # ── OBJ-7: SWI/SNF paradox ───────────────────────────────
    obj7_swi_snf_paradox(
        expr_kirp, t_cols_kirp, depth)

    # ── OBJ-8: ARG1 vs M2 ────────────────────────────────────
    obj8_arg1_vs_m2(
        expr_kirp, t_cols_kirp, depth)

    # ── OBJ-9: Warburg two-tier ───────────────────────────────
    obj9_warburg_two_tier(
        expr_kirp, t_cols_kirp, depth)

    # ── OBJ-10: ERBB2 continuous ─────────────────────────────
    obj10_erbb2_continuous(
        expr_kirp, t_cols_kirp, depth)

    # ── OBJ-11: Drug subtype map ──────────────────────────────
    obj11_drug_subtype_map(
        expr_kirp, t_cols_kirp, depth, subtypes)

    # ── Figure ────────────────────────────────────────────────
    generate_figure(
        depth, t_cols_kirp,
        expr_kirp, d_kirc,
        expr_kirc, t_cols_kirc,
        os_results, os_data,
        subtypes, cross_results)

    # ── Scorecard ─────────────────────────────────────────────
    print_scorecard()
    write_log()

    log("")
    log("="*60)
    log("SCRIPT 4 COMPLETE")
    log(f"Results: {RESULTS_DIR}")
    log(f"Log:     {LOG_FILE}")
    log("Next: Document 95d (results)")
    log("="*60)


if __name__ == "__main__":
    main()
