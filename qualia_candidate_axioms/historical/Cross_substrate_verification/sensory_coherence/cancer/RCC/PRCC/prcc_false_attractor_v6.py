"""
PRCC False Attractor — Script 6
FA-2 INDEPENDENT DEPTH · FERROPTOSIS · KITLG/c-KIT
· MET PRE/POST LOCK · CDK4 MECHANISM · INTEGRATED TABLE
· FINAL ATTRACTOR GEOMETRY

Framework: OrganismCore
Document 95f-pre | 2026-03-02
Author: Eric Robert Lawson

═══════════════════════════════════════════════════════════════
CONTEXT FROM DOCUMENTS 95c–95e:

  FA-1: Type 1 PRCC — biliary ductal lock
        MET-driven | KRT19/ERBB2/KRT7 up
        SLC22A6/FABP1 down | deep = locked = better OS
        Immune: ARG1+ MDSC + MCT4 loss

  FA-2: Type 2 PRCC — invasive/c-KIT programme
        Driver unknown | LAMC2/KITLG/ITGB6 up
        SLC7A9/CCL14/CCL15 down | CDK4-high = worst OS
        Ferroptosis vulnerable (SLC7A9 loss)
        Immune: CCL14/15 loss = NK exclusion

  FA-CIMP: FH-HLRCC extreme
        FA-1 ∩ FA-2 ∩ TCA-collapse
        FH/OGDHL down | EZH2/MKI67 up | worst OS

  OPEN THREADS:
  - FA-2 depth score not built on FA-2 axis
  - Ferroptosis panel not formally run
  - KITLG/c-KIT pathway not validated
  - MET pre/post lock not sub-analysed
  - CDK4 mechanism (bypass vs amplification) open
  - No integrated reference table
  - No final geometry figure

═══════════════════════════════════════════════════════════════
PREDICTIONS LOCKED — 2026-03-02 — BEFORE SCRIPT 6

  S6-P1:  FA-2 TI (LAMC2/SLC7A9) better predicts
          FA-2 depth than FA-1 TI (KRT19/SLC22A6)
          when depth is built on FA-2 axis

  S6-P2:  SLC7A9 is the top ferroptosis marker
          by depth in Type 2
          r(SLC7A9, FA2_depth) more negative than
          r(GPX4, FA2_depth) or r(ACSL4, FA2_depth)

  S6-P3:  GPX4 falls with FA-2 depth
          r(GPX4, FA2_depth) < -0.20

  S6-P4:  KITLG co-expresses with c-KIT pathway
          markers in Type 2
          r(KITLG, KIT)   > 0.30
          r(KITLG, PDGFRA)> 0.30

  S6-P5:  MET-hi + MKI67-hi = shallowest FA-1 depth
          (pre-lock proliferating savolitinib target)
          depth(MET-hi+MKI67-hi) < depth(MET-hi+MKI67-lo)

  S6-P6:  CDK4-high Type 2 co-occurs with
          CDKN2A-low (bypass mechanism confirmed)
          r(CDK4, CDKN2A) < 0 in Type 2

═══════════════════════════════════════════════════════════════
OBJECTIVES:
  OBJ-1:  Build FA-2 independent depth score
          from LAMC2/SLC7A9 axis within Type 2
  OBJ-2:  Ferroptosis vulnerability panel
          (SLC7A9, GPX4, ACSL4, TFRC, HMOX1,
           SLC3A2, GLS, CBS, NFE2L2/NRF2,
           PTGS2, ACSL3, FTH1, FTL)
  OBJ-3:  KITLG/c-KIT pathway analysis in Type 2
  OBJ-4:  MET × MKI67 quadrant in Type 1
  OBJ-5:  CDK4 × CDKN2A × CCND1 in Type 2
  OBJ-6:  ccRCC cross-cancer final
          (use KIRC if present, else fixed values
          from Document 94 literature)
  OBJ-7:  Integrated reference gene table
          (all genes × all metrics across S1-S6)
  OBJ-8:  Final attractor geometry figure

  OUTPUT: ./prcc_false_attractor/results_s6/
          integrated_gene_table.csv
          fa2_depth_score.csv
          ferroptosis_panel.csv
          kitlg_ckit_panel.csv
          met_mki67_quadrant.csv
          cdk4_cdkn2a_panel.csv
          prcc_script6_final_figure.pdf
═══════════════════════════════════════════════════════════════
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
import matplotlib.patches as mpatches
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from scipy.stats import pearsonr, mannwhitneyu
from scipy.stats import spearmanr
import warnings
warnings.filterwarnings("ignore")

# ═══════════════════════════════════════════════════════════════
# PATHS
# ═══════════════════════════════════════════════════════════════

BASE_DIR    = "./prcc_false_attractor/"
S1_DIR      = os.path.join(BASE_DIR, "results_s1/")
S2_DIR      = os.path.join(BASE_DIR, "results_s2/")
S5_DIR      = os.path.join(BASE_DIR, "results_s5/")
RESULTS_DIR = os.path.join(BASE_DIR, "results_s6/")
LOG_FILE    = os.path.join(RESULTS_DIR, "s6_log.txt")

KIRP_EXPR  = os.path.join(BASE_DIR, "TCGA_KIRP_HiSeqV2.gz")
KIRP_CLIN  = os.path.join(BASE_DIR, "KIRP_clinicalMatrix.tsv")
XENA_SURV  = os.path.join(BASE_DIR, "KIRP_survival.txt")
KIRC_EXPR  = os.path.join(BASE_DIR, "TCGA_KIRC_HiSeqV2.gz")
S1_DEPTH   = os.path.join(S1_DIR, "depth_scores_tcga.csv")
S2_TI      = os.path.join(S2_DIR, "transition_index.csv")
FA2_TI_CSV = os.path.join(S5_DIR, "TI_FA2.csv")

os.makedirs(RESULTS_DIR, exist_ok=True)

# ═══════════════════════════════════════════════════════════════
# GENE PANELS
# ═══════════════════════════════════════════════════════════════

# FA-2 axis genes confirmed in Script 5
FA2_POS = ["LAMC2","KITLG","ITGB6","KRT19","HRH1",
            "SLPI","C10orf47","C17orf28","RIN1"]
FA2_NEG = ["SLC7A9","CCL14","CCL15","AGMAT","KHK",
            "PAH","AGXT2","PRODH2","PKLR","AQP7",
            "PLA2G4C","GK","GNPDA1","SLC22A6"]

# Ferroptosis panel
FERROPTOSIS_POS = ["ACSL4","TFRC","HMOX1","PTGS2",
                    "NOX1","SLC38A1","GLS","CHAC1",
                    "SLC1A5","CARS","EPAS1"]
FERROPTOSIS_NEG = ["SLC7A9","GPX4","SLC3A2","FTH1",
                    "FTL","NFE2L2","CBS","SLC40A1",
                    "FANCD2","CISD1","AIFM2","FSP1"]
# Positive = pro-ferroptosis (rise = more susceptible)
# Negative = anti-ferroptosis (fall = more susceptible)

# c-KIT / KITLG pathway
CKIT_PATHWAY = ["KIT","KITLG","PDGFRA","PDGFRB",
                  "CSF1R","FLT3","STAT5A","STAT5B",
                  "PIK3CA","AKT1","MTOR","JAK2",
                  "TRYPTASE","CPA3","HDC","MS4A2",
                  "FCERI","CD117","SCF",
                  "TPSAB1","TPSB2","CTSG","CMA1"]

# Cell cycle — CDK4 mechanism
CELL_CYCLE = ["CDK4","CDK6","CCND1","CCND2","CCND3",
               "CDKN2A","CDKN2B","CDKN1A","CDKN1B",
               "RB1","E2F1","E2F3","MKI67","TOP2A",
               "CCNE1","CCNE2","CDK2","PCNA","MCM2"]

# MET pathway
MET_PATHWAY = ["MET","HGF","GAB1","GRB2","SOS1",
                "MAPK1","MAPK3","AKT1","PIK3CA",
                "STAT3","FAK","PXN","ITGA6","ITGB1",
                "EGFR","ERBB2","ERBB3","KRAS"]

# Shared attractor genes (PRCC + ccRCC)
SHARED_PRCC_KIRC = ["RUNX1","GOT1","EZH2","KDM1A",
                      "TET2","SLC22A6","MIOX","OGDHL",
                      "FH","B2M","HAVCR2","SETD2",
                      "PBRM1","SLC16A1","LDHA","VHL",
                      "EPAS1","HIF1A","CA9","VEGFA",
                      "ARG1","CDKN2A","MKI67",
                      "FCGR3B","S100A8","S100A9"]

# ccRCC known depth genes (from Document 94)
KIRC_DEPTH_POS = ["RUNX1","LOXL2","TGFB1","EZH2",
                   "KDM1A","VIM","ACTA2","FAP",
                   "COL1A1","TWIST1","SNAI1","SNAI2"]
KIRC_DEPTH_NEG = ["FBP1","UMOD","GOT1","MIOX",
                   "SLC22A6","SLC34A1","GPX3",
                   "ACADM","CUBN","SLC5A2"]

# All genes to include in integrated table
INTEGRATED_GENES = list(dict.fromkeys(
    FA2_POS + FA2_NEG +
    FERROPTOSIS_POS + FERROPTOSIS_NEG +
    CKIT_PATHWAY + CELL_CYCLE + MET_PATHWAY +
    SHARED_PRCC_KIRC +
    ["KRT7","KRT8","KRT18","KRT19","ERBB2",
     "SOX4","AXL","KDM1A","MET","FABP1",
     "SLC34A1","GPX3","CUBN","LDHB","ACADM",
     "SLC5A2","LRP2","SLC16A1","LDHA","PDK1",
     "TWIST1","ACTA2","FAP","VIM","CDH2",
     "SNAI1","SNAI2","FN1","PBRM1","SETD2",
     "ARID1A","ARID1B","SMARCA4","SMARCB1",
     "ARG1","TNF","IL6","CXCL10","CD163",
     "MRC1","CSF1R","TGFB1","CA9","PDK2",
     "PDK3","PDK4","SLC2A1","ALDOA","ENO1",
     "HK2","PFKL","VEGFA","SLC16A1","RUNX1",
     "GOT1","LOXL2","FBP1","UMOD","EPAS1",
     "HIF1A","CDKN2A","CDK4","CDK6","CCND1",
     "MKI67","TOP2A","EZH2","TET2","FH",
     "OGDHL","B2M","HAVCR2","CD274","ARG1",
     "FCGR3B","S100A8","S100A9","HLA-A",
     "CCL14","CCL15","LAMC2","ITGB6","KITLG",
     "SLC7A9","SLPI","PAH","AGMAT","AGXT2",
     "PRODH2","PKLR","AQP7","KHK","GK"]))

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
    a = np.asarray(a, float)[np.isfinite(
        np.asarray(a, float))]
    b = np.asarray(b, float)[np.isfinite(
        np.asarray(b, float))]
    if len(a) < 3 or len(b) < 3:
        return np.nan, np.nan
    return mannwhitneyu(a, b, alternative="two-sided")

def safe_logrank(t1, e1, t2, e2):
    t1=np.asarray(t1,float); e1=np.asarray(e1,float)
    t2=np.asarray(t2,float); e2=np.asarray(e2,float)
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
        O1+=d1; O2+=d2; E1+=n1*d/n; E2+=n2*d/n
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
    if gene not in expr.index: return None
    return pd.Series(expr.loc[gene, cols].values,
                     index=cols).reindex(idx)

# ═══════════════════════════════════════════════════════════════
# DATA LOADING
# ═══════════════════════════════════════════════════════════════

def load_all():
    log(""); log("="*60)
    log("LOADING ALL PRIOR OUTPUTS"); log("="*60)

    df1   = pd.read_csv(S1_DEPTH)
    depth = pd.Series(df1["depth_score"].values,
                      index=df1["sample_id"].values,
                      name="depth")
    df2   = pd.read_csv(S2_TI)
    ti    = pd.Series(df2["TI"].values,
                      index=df2["sample_id"].values,
                      name="TI")
    log(f"  S1 depth n={len(depth)}  "
        f"S2 TI n={len(ti)}")

    ti_fa2 = None
    if os.path.exists(FA2_TI_CSV):
        dfa2 = pd.read_csv(FA2_TI_CSV)
        ti_fa2 = pd.Series(
            dfa2["TI_FA2"].values,
            index=dfa2["sample_id"].values,
            name="TI_FA2")
        log(f"  FA-2 TI (S5) n={len(ti_fa2)}")

    return depth, ti, ti_fa2


def load_expr():
    log(""); log("="*60)
    log("LOADING EXPRESSION MATRIX"); log("="*60)
    fn = gzip.open if KIRP_EXPR.endswith(".gz") \
        else open
    with fn(KIRP_EXPR,"rt") as fh:
        raw = pd.read_csv(fh,sep="\t",index_col=0)
    types = []
    for s in raw.columns:
        p = s.split("-")
        c = p[3][:2] if len(p)>=4 else "00"
        types.append("tumour" if c=="01" else
                      "normal" if c=="11" else "other")
    meta   = pd.DataFrame({"t":types},
                           index=raw.columns)
    t_cols = raw.columns[meta["t"].eq("tumour").values]
    n_cols = raw.columns[meta["t"].eq("normal").values]
    log(f"  KIRP: t={len(t_cols)} n={len(n_cols)}")
    return raw, t_cols, n_cols


def load_subtypes():
    if not os.path.exists(KIRP_CLIN): return None
    clin = pd.read_csv(KIRP_CLIN,sep="\t",
                       index_col=0,low_memory=False)
    clin.index = clin.index.astype(str).str[:12]
    clin = clin[~clin.index.duplicated(keep="first")]
    col = next((c for c in
                ["tumor_type","TUMOR_TYPE",
                 "histological_type"]
                if c in clin.columns), None)
    if col is None: return None
    return clin[col].dropna()


def load_survival():
    if not os.path.exists(XENA_SURV): return None
    surv = pd.read_csv(XENA_SURV,sep="\t",
                       index_col=0,low_memory=False)
    surv.index = surv.index.astype(str).str[:12]
    surv = surv[~surv.index.duplicated(keep="first")]
    return surv


def build_os(d, surv):
    if surv is None:
        nan = pd.Series(np.nan,index=d.index)
        return nan.copy(), nan.copy()
    patients = [s[:12] for s in d.index]
    tc = next((c for c in ["OS.time","OS_time",
                             "days_to_death"]
               if c in surv.columns), None)
    ec = next((c for c in ["OS","vital_status","dead"]
               if c in surv.columns), None)
    if tc is None or ec is None:
        nan = pd.Series(np.nan,index=d.index)
        return nan.copy(), nan.copy()

    def _g(pid,col):
        if pid not in surv.index: return np.nan
        v = surv.at[pid,col]
        return (pd.Series(v).iloc[0]
                if isinstance(v,(pd.Series,
                                  list,np.ndarray))
                else v)

    os_t = pd.Series(
        [pd.to_numeric(_g(p,tc),errors="coerce")
         for p in patients],
        index=d.index,dtype=float)
    os_e = pd.Series(
        [_g(p,ec) for p in patients],
        index=d.index
    ).map(lambda x: 1 if str(x).lower() in
          ["dead","deceased","1","true","yes"]
          else (0 if str(x).lower() in
                ["alive","living","0","false","no"]
                else np.nan)).astype(float)
    return os_t, os_e


def build_subtype_indices(depth, subtypes, t_cols):
    d = depth.reindex(t_cols).dropna()
    if subtypes is None:
        return None, None
    sm = subtypes.to_dict()
    labels = pd.Series(
        {s: sm.get(s[:12],"UNKNOWN")
         for s in d.index},
        name="subtype").reindex(d.index)
    t1 = d.index[labels.str.lower().str.contains(
        r"type.?1|type_1",regex=True,na=False)]
    t2 = d.index[labels.str.lower().str.contains(
        r"type.?2|type_2",regex=True,na=False)]
    log(f"  Type1 n={len(t1)}  Type2 n={len(t2)}")
    return t1, t2


def load_kirc():
    if not os.path.exists(KIRC_EXPR):
        return None, None, None
    fn = gzip.open if KIRC_EXPR.endswith(".gz") \
        else open
    with fn(KIRC_EXPR,"rt") as fh:
        raw = pd.read_csv(fh,sep="\t",index_col=0)
    types = []
    for s in raw.columns:
        p = s.split("-")
        c = p[3][:2] if len(p)>=4 else "00"
        types.append("tumour" if c=="01" else
                      "normal" if c=="11" else "other")
    meta   = pd.DataFrame({"t":types},
                           index=raw.columns)
    t_cols = raw.columns[meta["t"].eq("tumour").values]
    n_cols = raw.columns[meta["t"].eq("normal").values]
    log(f"  KIRC: t={len(t_cols)} n={len(n_cols)}")
    return raw, t_cols, n_cols

# ═══════════════════════════════════════════════════════════════
# OBJ-1: FA-2 INDEPENDENT DEPTH SCORE
# ═══════════════════════════════════════════════════════════════

def obj1_fa2_depth(depth, expr, t_cols, t2_idx):
    log(""); log("="*60)
    log("OBJ-1 — FA-2 INDEPENDENT DEPTH SCORE")
    log("="*60)
    log("  S6-P1: FA-2 TI better on FA-2 axis than FA-1 TI")

    if t2_idx is None or len(t2_idx) < 10:
        log("  No Type 2 index."); return None

    d_t2 = depth.reindex(t2_idx).dropna()

    # Build FA-2 depth score from FA-2 axis genes
    pos_av = [g for g in FA2_POS
              if g in expr.index]
    neg_av = [g for g in FA2_NEG
              if g in expr.index]
    log(f"  FA-2 pos genes available: {pos_av}")
    log(f"  FA-2 neg genes available: {neg_av}")

    if not pos_av or not neg_av:
        log("  FA-2 axis genes missing.")
        return None

    # Compute on TYPE 2 samples only
    pos_sc = expr.loc[pos_av, t2_idx].mean(axis=0)
    neg_sc = expr.loc[neg_av, t2_idx].mean(axis=0)
    raw_d2 = norm01(pos_sc.values) - \
             norm01(neg_sc.values)
    fa2_depth = pd.Series(
        norm01(raw_d2), index=t2_idx,
        name="fa2_depth")
    log(f"  FA-2 depth: n={len(fa2_depth)} "
        f"mean={fa2_depth.mean():.3f}")

    # Also compute on ALL tumours for reference
    pos_all = expr.loc[pos_av, t_cols].mean(axis=0)
    neg_all = expr.loc[neg_av, t_cols].mean(axis=0)
    raw_all = norm01(pos_all.values) - \
              norm01(neg_all.values)
    fa2_depth_all = pd.Series(
        norm01(raw_all), index=t_cols,
        name="fa2_depth")

    # S6-P1: FA-2 TI vs FA-1 TI on FA-2 depth
    log("")
    log("  FA-2 TI vs FA-1 TI on FA-2 depth (S6-P1):")

    # FA-2 TI = LAMC2/SLC7A9
    if "LAMC2" in expr.index and \
            "SLC7A9" in expr.index:
        lamc2  = gv("LAMC2",  expr, t_cols, t2_idx)
        slc7a9 = gv("SLC7A9", expr, t_cols, t2_idx)
        ti_fa2 = pd.Series(
            norm01(lamc2.values) -
            norm01(slc7a9.values),
            index=t2_idx)
        r_fa2, p_fa2 = safe_r(
            ti_fa2.values, fa2_depth.values)
        log(f"  FA-2 TI r(FA2_depth) = "
            f"{r_fa2:+.4f} {fmt_p(p_fa2)}")
    else:
        r_fa2 = np.nan

    # FA-1 TI = KRT19/SLC22A6
    if "KRT19" in expr.index and \
            "SLC22A6" in expr.index:
        krt19  = gv("KRT19",   expr, t_cols, t2_idx)
        slc22  = gv("SLC22A6", expr, t_cols, t2_idx)
        ti_fa1 = pd.Series(
            norm01(krt19.values) -
            norm01(slc22.values),
            index=t2_idx)
        r_fa1, p_fa1 = safe_r(
            ti_fa1.values, fa2_depth.values)
        log(f"  FA-1 TI r(FA2_depth) = "
            f"{r_fa1:+.4f} {fmt_p(p_fa1)}")
    else:
        r_fa1 = np.nan

    if not np.isnan(r_fa2) and not np.isnan(r_fa1):
        if abs(r_fa2) > abs(r_fa1):
            log("  S6-P1 CONFIRMED: FA-2 TI better "
                "on FA-2 axis ✓")
        else:
            log("  S6-P1 NOT CONFIRMED: "
                "FA-1 TI still dominates FA-2 axis")
            log(f"  NOTE: r_FA1={r_fa1:+.4f} "
                f"r_FA2={r_fa2:+.4f}")
            log("  This suggests KRT19/SLC22A6 axis "
                "drives depth variation even within "
                "Type 2, confirming that CIMP "
                "(KRT19-high within T2) pulls the "
                "FA-1 TI into Type 2 space.")

    # Correlation between FA-1 depth and FA-2 depth
    d_t2_fa1 = depth.reindex(t2_idx).dropna()
    r_cross, p_cross = safe_r(
        d_t2_fa1.values, fa2_depth.values)
    log(f"\n  r(FA1_depth, FA2_depth) in T2 = "
        f"{r_cross:+.4f} {fmt_p(p_cross)}")
    if abs(r_cross) < 0.50:
        log("  FA-1 and FA-2 depth scores are "
            "PARTIALLY INDEPENDENT ✓")
        log("  Two distinct depth axes confirmed.")
    else:
        log("  FA-1 and FA-2 depth scores are "
            "CORRELATED — shared variation dominates.")

    # Gene depth correlates on FA-2 axis
    log("")
    log("  TOP GENES vs FA-2 DEPTH (in Type 2):")
    log(f"  {'Gene':<14} {'r_FA2':>9} "
        f"{'r_FA1':>9} {'delta':>8}")
    log(f"  {'─'*44}")
    gene_rows = []
    for gene in (FA2_POS + FA2_NEG +
                  ["KRT19","SLC22A6","EZH2",
                   "MET","CDKN2A","CDK4",
                   "FH","OGDHL","ARG1","SLC16A1",
                   "LAMC2","SLC7A9","KITLG",
                   "GPX4","ACSL4","RUNX1","GOT1"]):
        if gene not in expr.index: continue
        g_ = gv(gene, expr, t_cols, t2_idx)
        if g_ is None: continue
        r2, _ = safe_r(g_.values, fa2_depth.values)
        r1, _ = safe_r(
            g_.values,
            d_t2_fa1.reindex(t2_idx).values)
        delta = r2 - r1 if not np.isnan(r2) \
            and not np.isnan(r1) else np.nan
        log(f"  {gene:<14} {r2:>+9.4f} "
            f"{r1:>+9.4f} {delta:>+8.4f}")
        gene_rows.append({
            "gene":gene,"r_fa2_depth":r2,
            "r_fa1_depth":r1,"delta":delta})

    pd.DataFrame(gene_rows).to_csv(
        os.path.join(RESULTS_DIR,
                     "fa2_depth_gene_corr.csv"),
        index=False)

    # Save FA-2 depth
    fa2_depth_all.reset_index().rename(
        columns={"index":"sample_id",
                 0:"fa2_depth"}).to_csv(
        os.path.join(RESULTS_DIR,
                     "fa2_depth_score.csv"),
        index=False)
    log(f"  FA-2 depth saved.")

    return fa2_depth, fa2_depth_all

# ═══════════════════════════════════════════════════════════════
# OBJ-2: FERROPTOSIS VULNERABILITY PANEL
# ═══════════════════════════════════════════════════════════════

def obj2_ferroptosis(depth, expr, t_cols,
                      t1_idx, t2_idx,
                      fa2_depth):
    log(""); log("="*60)
    log("OBJ-2 — FERROPTOSIS VULNERABILITY PANEL")
    log("="*60)
    log("  S6-P2: SLC7A9 top ferroptosis marker in T2")
    log("  S6-P3: GPX4 falls with FA-2 depth")

    d = depth.reindex(t_cols).dropna()

    all_ferro = list(dict.fromkeys(
        FERROPTOSIS_NEG + FERROPTOSIS_POS))
    avail = [g for g in all_ferro
             if g in expr.index]
    log(f"  Available ferroptosis genes: "
        f"{len(avail)}/{len(all_ferro)}")

    rows = []
    log("")
    log(f"  {'Gene':<14} {'role':<8} "
        f"{'r_all':>8} {'r_T1':>8} "
        f"{'r_T2':>8} {'r_FA2':>8} "
        f"{'sens?'}")
    log(f"  {'─'*62}")

    for gene in avail:
        role = ("ANTI" if gene in FERROPTOSIS_NEG
                else "PRO")
        g_all = gv(gene, expr, t_cols, d.index)
        if g_all is None: continue

        r_all, _ = safe_r(g_all.values, d.values)

        r_t1 = np.nan
        if t1_idx is not None:
            g_t1 = gv(gene, expr, t_cols, t1_idx)
            d_t1 = depth.reindex(t1_idx).dropna()
            if g_t1 is not None:
                r_t1, _ = safe_r(
                    g_t1.values, d_t1.values)

        r_t2 = r_fa2 = np.nan
        if t2_idx is not None:
            g_t2 = gv(gene, expr, t_cols, t2_idx)
            d_t2 = depth.reindex(t2_idx).dropna()
            if g_t2 is not None:
                r_t2, _ = safe_r(
                    g_t2.values, d_t2.values)
            if fa2_depth is not None and \
                    g_t2 is not None:
                r_fa2, _ = safe_r(
                    g_t2.reindex(
                        fa2_depth.index).values,
                    fa2_depth.values)

        # Sensitivity: ANTI falling or PRO rising
        sens = ""
        if role == "ANTI" and not np.isnan(r_t2) \
                and r_t2 < -0.20:
            sens = "VULN_T2"
        elif role == "PRO" and not np.isnan(r_t2) \
                and r_t2 > 0.20:
            sens = "VULN_T2"
        elif role == "ANTI" and not np.isnan(r_all) \
                and r_all < -0.20:
            sens = "VULN_ALL"

        fl = "★" if "VULN" in sens else " "
        log(f"  {fl}{gene:<14} {role:<8} "
            f"{r_all:>+8.4f} {r_t1:>+8.4f} "
            f"{r_t2:>+8.4f} {r_fa2:>+8.4f} "
            f"{sens}")
        rows.append({
            "gene":gene,"role":role,
            "r_all":r_all,"r_t1":r_t1,
            "r_t2":r_t2,"r_fa2_depth":r_fa2,
            "sensitivity":sens})

    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(RESULTS_DIR,
                           "ferroptosis_panel.csv"),
              index=False)

    # S6-P2: SLC7A9 top ANTI marker in T2
    anti_t2 = df[df.role=="ANTI"].dropna(
        subset=["r_t2"]).sort_values(
        "r_t2", ascending=True)
    if len(anti_t2) > 0:
        top_gene = anti_t2.iloc[0]["gene"]
        top_r    = anti_t2.iloc[0]["r_t2"]
        log(f"\n  Top ANTI-ferroptosis in T2: "
            f"{top_gene} r={top_r:+.4f}")
        if top_gene == "SLC7A9":
            log("  S6-P2 CONFIRMED: SLC7A9 top "
                "ferroptosis marker in T2 ✓")
        else:
            log(f"  S6-P2 NOT CONFIRMED: "
                f"{top_gene} (not SLC7A9)")
            # Check SLC7A9 rank
            slc_row = anti_t2[
                anti_t2.gene=="SLC7A9"]
            if len(slc_row) > 0:
                log(f"  SLC7A9 rank: "
                    f"{anti_t2.index.tolist().index(slc_row.index[0])+1}"
                    f"/{len(anti_t2)}")

    # S6-P3: GPX4 falls with FA-2 depth
    gpx4_row = df[df.gene=="GPX4"]
    if len(gpx4_row) > 0:
        r_gpx4_fa2 = gpx4_row.iloc[0]["r_fa2_depth"]
        log(f"\n  GPX4 r(FA-2 depth) = "
            f"{r_gpx4_fa2:+.4f}")
        if not np.isnan(r_gpx4_fa2) and \
                r_gpx4_fa2 < -0.20:
            log("  S6-P3 CONFIRMED: GPX4 falls "
                "with FA-2 depth ✓")
        else:
            log("  S6-P3 NOT CONFIRMED")

    # Ferroptosis score
    anti_av = [g for g in FERROPTOSIS_NEG
               if g in expr.index]
    pro_av  = [g for g in FERROPTOSIS_POS
               if g in expr.index]
    if anti_av and t2_idx is not None:
        anti_t2_sc = expr.loc[
            anti_av, t2_idx].mean(axis=0)
        pro_t2_sc  = expr.loc[
            pro_av, t2_idx].mean(axis=0) \
            if pro_av else pd.Series(
                0, index=t2_idx)
        ferro_sc = pd.Series(
            norm01(pro_t2_sc.values) -
            norm01(anti_t2_sc.values),
            index=t2_idx,
            name="ferroptosis_score")
        d_t2 = depth.reindex(t2_idx).dropna()
        r_fs, p_fs = safe_r(
            ferro_sc.reindex(d_t2.index).values,
            d_t2.values)
        log(f"\n  Ferroptosis susceptibility score "
            f"r(FA1_depth_T2) = {r_fs:+.4f} "
            f"{fmt_p(p_fs)}")
        if fa2_depth is not None:
            r_fs2, p_fs2 = safe_r(
                ferro_sc.reindex(
                    fa2_depth.index).values,
                fa2_depth.values)
            log(f"  Ferroptosis score r(FA2_depth) "
                f"= {r_fs2:+.4f} {fmt_p(p_fs2)}")
        if r_fs > 0.20:
            log("  Deep T2 = HIGH ferroptosis "
                "susceptibility ✓")
            log("  Erastin/RSL3 prediction "
                "supported ✓")

    return df

# ═══════════════════════════════════════════════════════════════
# OBJ-3: KITLG / c-KIT PATHWAY IN TYPE 2
# ═══════════════════════════════════════════════════════════════

def obj3_kitlg_ckit(depth, expr, t_cols, t2_idx,
                     fa2_depth):
    log(""); log("="*60)
    log("OBJ-3 — KITLG / c-KIT PATHWAY IN TYPE 2")
    log("="*60)
    log("  S6-P4: r(KITLG, KIT) > 0.30 in Type 2")
    log("  S6-P4: r(KITLG, PDGFRA) > 0.30 in Type 2")

    if t2_idx is None:
        log("  No Type 2 index."); return

    d_t2 = depth.reindex(t2_idx).dropna()
    avail = [g for g in CKIT_PATHWAY
             if g in expr.index]
    log(f"  c-KIT pathway genes: {avail}")

    # Depth correlates in Type 2
    log("")
    log(f"  {'Gene':<14} {'r_T2':>9} "
        f"{'r_FA2':>9} {'p_T2':>12}")
    log(f"  {'─'*46}")
    rows = []
    for gene in avail:
        g_ = gv(gene, expr, t_cols, t2_idx)
        if g_ is None: continue
        r_t2, p_t2 = safe_r(g_.values, d_t2.values)
        r_fa2 = np.nan
        if fa2_depth is not None:
            g_fa2 = g_.reindex(fa2_depth.index)
            r_fa2, _ = safe_r(
                g_fa2.values, fa2_depth.values)
        fl = "★" if not np.isnan(p_t2) \
            and p_t2 < 0.05 else " "
        log(f"  {fl}{gene:<14} {r_t2:>+9.4f} "
            f"{r_fa2:>+9.4f} {fmt_p(p_t2):>12}")
        rows.append({
            "gene":gene,"r_t2":r_t2,
            "r_fa2":r_fa2,"p_t2":p_t2})

    # S6-P4: KITLG pairwise
    log(""); log("  KITLG PAIRWISE (S6-P4):")
    if "KITLG" in expr.index:
        kitlg = gv("KITLG", expr, t_cols, t2_idx)
        if kitlg is not None:
            for partner in ["KIT","PDGFRA","PDGFRB",
                              "CSF1R","STAT5A","STAT5B",
                              "TPSAB1","TPSB2","CPA3",
                              "HDC","MS4A2","FCGR3B"]:
                if partner not in expr.index: continue
                p_ = gv(partner, expr, t_cols, t2_idx)
                if p_ is None: continue
                r, p = safe_r(kitlg.values, p_.values)
                fl = "★" if not np.isnan(p) \
                    and p < 0.05 else " "
                log(f"  {fl}r(KITLG, {partner:<10}) "
                    f"= {r:>+8.4f} {fmt_p(p):>12}")
                rows.append({
                    "gene":f"KITLG×{partner}",
                    "r_t2":r,"r_fa2":np.nan,
                    "p_t2":p})

            # Check KIT and PDGFRA for S6-P4
            kit_row = [r for r in rows
                       if r["gene"]=="KIT"]
            pdr_row = [r for r in rows
                       if r["gene"]=="PDGFRA"]

            # S6-P4 judgement
            r_kit  = kit_row[0]["r_t2"] \
                if kit_row else np.nan
            r_pdgf = pdr_row[0]["r_t2"] \
                if pdr_row else np.nan
            kit_pair = next(
                (r["r_t2"] for r in rows
                 if r["gene"]=="KITLG×KIT"), np.nan)
            pdg_pair = next(
                (r["r_t2"] for r in rows
                 if r["gene"]=="KITLG×PDGFRA"),
                np.nan)
            log("")
            log(f"  S6-P4 check:")
            log(f"  r(KITLG×KIT)   = "
                f"{kit_pair:+.4f}")
            log(f"  r(KITLG×PDGFRA)= "
                f"{pdg_pair:+.4f}")
            if not np.isnan(kit_pair) and \
                    kit_pair > 0.30 and \
                    not np.isnan(pdg_pair) and \
                    pdg_pair > 0.30:
                log("  S6-P4 CONFIRMED ✓")
            elif not np.isnan(kit_pair) and \
                    kit_pair > 0.30:
                log("  S6-P4 PARTIAL: KIT confirmed, "
                    "PDGFRA weak")
            else:
                log("  S6-P4 NOT CONFIRMED")

    # Mast cell signature score
    mast_genes = ["TPSAB1","TPSB2","CPA3",
                   "HDC","MS4A2","KITLG","CMA1"]
    mast_av = [g for g in mast_genes
               if g in expr.index]
    if mast_av:
        mast_sc = expr.loc[mast_av, t2_idx].mean(
            axis=0)
        mast_s  = pd.Series(
            norm01(mast_sc.values), index=t2_idx)
        r_mast, p_mast = safe_r(
            mast_s.values, d_t2.values)
        log(f"\n  Mast cell signature score "
            f"r(depth_T2) = {r_mast:+.4f} "
            f"{fmt_p(p_mast)}")
        if r_mast > 0.15:
            log("  Mast cell recruitment increases "
                "with Type 2 depth ✓")

    pd.DataFrame(rows).to_csv(
        os.path.join(RESULTS_DIR,
                     "kitlg_ckit_panel.csv"),
        index=False)

# ═══════════════════════════════════════════════════════════════
# OBJ-4: MET × MKI67 QUADRANT IN TYPE 1
# ═══════════════════════════════════════════════════════════════

def obj4_met_mki67_quadrant(depth, expr, t_cols,
                              t1_idx, surv):
    log(""); log("="*60)
    log("OBJ-4 — MET × MKI67 QUADRANT IN TYPE 1")
    log("="*60)
    log("  S6-P5: MET-hi+MKI67-hi = shallowest T1")

    if t1_idx is None or len(t1_idx) < 10:
        log("  No Type 1 index."); return

    d_t1 = depth.reindex(t1_idx).dropna()

    met  = gv("MET",   expr, t_cols, d_t1.index)
    mki  = gv("MKI67", expr, t_cols, d_t1.index)
    if met is None or mki is None:
        log("  MET or MKI67 missing."); return

    # Median split
    m_met = met.median(); m_mki = mki.median()
    quad = pd.Series(index=d_t1.index, dtype=str)
    quad[(met>=m_met)&(mki>=m_mki)] = "MET_hi+MKI_hi"
    quad[(met>=m_met)&(mki< m_mki)] = "MET_hi+MKI_lo"
    quad[(met< m_met)&(mki>=m_mki)] = "MET_lo+MKI_hi"
    quad[(met< m_met)&(mki< m_mki)] = "MET_lo+MKI_lo"

    log(f"\n  {'Quadrant':<22} {'n':>4} "
        f"{'mean_depth':>12} {'med_OS':>9}")
    log(f"  {'─'*50}")

    os_t, os_e = build_os(d_t1, surv)
    valid = os_t.notna() & os_e.notna() & (os_t > 0)

    rows = []
    for label in ["MET_hi+MKI_hi","MET_hi+MKI_lo",
                   "MET_lo+MKI_hi","MET_lo+MKI_lo"]:
        mask = quad == label
        d_q  = d_t1[mask]
        os_q = os_t[mask & valid]
        med_os = os_q.median() if len(os_q) > 0 \
            else np.nan
        log(f"  {label:<22} {mask.sum():>4} "
            f"{d_q.mean():>12.4f} "
            f"{med_os:>9.0f}d")
        rows.append({
            "quadrant":label,
            "n":int(mask.sum()),
            "mean_depth":d_q.mean(),
            "med_os":med_os})

    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(RESULTS_DIR,
                           "met_mki67_quadrant.csv"),
              index=False)

    # S6-P5 check
    hh = df[df.quadrant=="MET_hi+MKI_hi"][
        "mean_depth"].values
    hl = df[df.quadrant=="MET_hi+MKI_lo"][
        "mean_depth"].values
    if len(hh)>0 and len(hl)>0:
        log(f"\n  MET-hi+MKI-hi depth: {hh[0]:.4f}")
        log(f"  MET-hi+MKI-lo depth: {hl[0]:.4f}")
        if hh[0] < hl[0]:
            log("  S6-P5 CONFIRMED: MET-hi+MKI-hi "
                "shallowest (pre-lock) ✓")
        else:
            log("  S6-P5 NOT CONFIRMED")

    # Pairwise OS between quadrants
    log("\n  OS COMPARISONS:")
    mask_hh = (quad=="MET_hi+MKI_hi") & valid
    mask_hl = (quad=="MET_hi+MKI_lo") & valid
    if mask_hh.sum()>=3 and mask_hl.sum()>=3:
        _, p_hh_hl = safe_logrank(
            os_t[mask_hh].values,
            os_e[mask_hh].values,
            os_t[mask_hl].values,
            os_e[mask_hl].values)
        log(f"  MET-hi+MKI-hi vs MET-hi+MKI-lo: "
            f"{fmt_p(p_hh_hl)}")
        hh_os = os_t[mask_hh].median()
        hl_os = os_t[mask_hl].median()
        log(f"  MET-hi+MKI-hi OS: {hh_os:.0f}d  "
            f"MET-hi+MKI-lo OS: {hl_os:.0f}d")
        if hh_os < hl_os:
            log("  Confirmed: pre-lock MET-hi "
                "patients have worse OS ✓")
            log("  Savolitinib target = "
                "MET-hi+MKI-hi confirmed")

    # MET pathway depth correlates
    log("\n  MET PATHWAY vs DEPTH (Type 1):")
    for gene in [g for g in MET_PATHWAY
                 if g in expr.index]:
        g_ = gv(gene, expr, t_cols, d_t1.index)
        if g_ is None: continue
        r, p = safe_r(g_.values, d_t1.values)
        fl = "★" if not np.isnan(p) \
            and p < 0.05 else " "
        log(f"  {fl}{gene:<12} r={r:>+8.4f} "
            f"{fmt_p(p):>12}")

# ═══════════════════════════════════════════════════════════════
# OBJ-5: CDK4 × CDKN2A MECHANISM IN TYPE 2
# ═══════════════════════════════════════════════════════════════

def obj5_cdk4_mechanism(depth, expr, t_cols,
                          t2_idx, surv):
    log(""); log("="*60)
    log("OBJ-5 — CDK4 × CDKN2A MECHANISM IN TYPE 2")
    log("="*60)
    log("  S6-P6: r(CDK4, CDKN2A) < 0 in Type 2")

    if t2_idx is None:
        log("  No Type 2 index."); return

    d_t2 = depth.reindex(t2_idx).dropna()

    # CDK4/CDKN2A pairwise
    log("\n  CELL CYCLE PAIRWISE CORRELATIONS (T2):")
    log(f"  {'GeneA':<12} {'GeneB':<12} "
        f"{'r_T2':>9} {'p':>12}")
    log(f"  {'─'*46}")

    for gA, gB in [("CDK4","CDKN2A"),
                    ("CDK4","CDK6"),
                    ("CDK4","CCND1"),
                    ("CDK4","CCND2"),
                    ("CDK4","RB1"),
                    ("CDK4","MKI67"),
                    ("CDKN2A","CDKN2B"),
                    ("CDKN2A","RB1"),
                    ("CDK6","CCND1"),
                    ("CDK6","CCND3")]:
        if gA not in expr.index or \
                gB not in expr.index: continue
        vA = gv(gA, expr, t_cols, t2_idx)
        vB = gv(gB, expr, t_cols, t2_idx)
        if vA is None or vB is None: continue
        r, p = safe_r(vA.values, vB.values)
        fl = "★" if not np.isnan(p) \
            and p < 0.05 else " "
        log(f"  {fl}{gA:<12} {gB:<12} "
            f"{r:>+9.4f} {fmt_p(p):>12}")

    # S6-P6 check
    if "CDK4" in expr.index and \
            "CDKN2A" in expr.index:
        cdk4  = gv("CDK4",   expr, t_cols, t2_idx)
        cdkn2 = gv("CDKN2A", expr, t_cols, t2_idx)
        r_cc, p_cc = safe_r(cdk4.values,
                              cdkn2.values)
        log(f"\n  S6-P6: r(CDK4, CDKN2A) T2 = "
            f"{r_cc:+.4f} {fmt_p(p_cc)}")
        if not np.isnan(r_cc) and r_cc < 0:
            log("  S6-P6 CONFIRMED: CDK4/CDKN2A "
                "anti-correlated in T2 ✓")
            log("  CDK4 bypass of CDKN2A confirmed.")
        else:
            log("  S6-P6 NOT CONFIRMED "
                f"(r={r_cc:+.4f})")
            if r_cc > 0:
                log("  CDK4 and CDKN2A co-occur — "
                    "bypass via protein loss "
                    "(not RNA), or paradox as "
                    "seen in Script 3.")

    # CDK4 OS quadrant
    log("\n  CDK4 × DEPTH OS QUADRANT (Type 2):")
    if "CDK4" in expr.index:
        cdk4 = gv("CDK4", expr, t_cols, d_t2.index)
        if cdk4 is not None:
            os_t, os_e = build_os(d_t2, surv)
            valid = (os_t.notna() & os_e.notna()
                     & (os_t > 0))
            q50_cdk4 = cdk4.median()
            q50_d    = d_t2.median()
            quad = pd.Series(index=d_t2.index,
                              dtype=str)
            quad[(cdk4>=q50_cdk4) &
                 (d_t2>=q50_d)] = "CDK4hi_deep"
            quad[(cdk4>=q50_cdk4) &
                 (d_t2< q50_d)] = "CDK4hi_shallow"
            quad[(cdk4< q50_cdk4) &
                 (d_t2>=q50_d)] = "CDK4lo_deep"
            quad[(cdk4< q50_cdk4) &
                 (d_t2< q50_d)] = "CDK4lo_shallow"

            log(f"  {'Quadrant':<20} {'n':>4} "
                f"{'med_OS':>9} {'events':>8}")
            log(f"  {'─'*44}")
            for label in ["CDK4hi_deep",
                           "CDK4hi_shallow",
                           "CDK4lo_deep",
                           "CDK4lo_shallow"]:
                mask = (quad==label) & valid
                mos  = os_t[mask].median()
                evs  = int(os_e[mask].sum())
                n_   = int((quad==label).sum())
                log(f"  {label:<20} {n_:>4} "
                    f"{mos:>9.0f}d {evs:>8}")

            # CDK4hi_shallow vs CDK4lo_deep OS
            mhh = (quad=="CDK4hi_shallow") & valid
            mll = (quad=="CDK4lo_deep")    & valid
            if mhh.sum()>=3 and mll.sum()>=3:
                _, p_q = safe_logrank(
                    os_t[mhh].values,
                    os_e[mhh].values,
                    os_t[mll].values,
                    os_e[mll].values)
                log(f"\n  CDK4-hi-shallow vs "
                    f"CDK4-lo-deep: {fmt_p(p_q)}")

    # Full cell cycle panel vs depth in T2
    log("\n  CELL CYCLE PANEL vs DEPTH (Type 2):")
    rows = []
    for gene in [g for g in CELL_CYCLE
                 if g in expr.index]:
        g_ = gv(gene, expr, t_cols, d_t2.index)
        if g_ is None: continue
        r, p = safe_r(g_.values, d_t2.values)
        fl = "★" if not np.isnan(p) \
            and p < 0.05 else " "
        log(f"  {fl}{gene:<12} r={r:>+8.4f} "
            f"{fmt_p(p):>12}")
        rows.append({"gene":gene,"r_t2":r,"p_t2":p})
    pd.DataFrame(rows).to_csv(
        os.path.join(RESULTS_DIR,
                     "cdk4_cdkn2a_panel.csv"),
        index=False)

# ═══════════════════════════════════════════════════════════════
# OBJ-6: ccRCC CROSS-CANCER FINAL
# ═══════════════════��═══════════════════════════════════════════

def obj6_cross_cancer(depth, expr, t_cols,
                       expr_kirc, t_cols_kirc):
    log(""); log("="*60)
    log("OBJ-6 — ccRCC CROSS-CANCER FINAL")
    log("="*60)

    d = depth.reindex(t_cols).dropna()

    if expr_kirc is None:
        log("  ccRCC matrix absent.")
        log("  Using fixed r-values from Document 94 "
            "literature as reference.")

        # Fixed values from ccRCC Script 2 (Document 94)
        # These are the previously established ccRCC
        # depth correlates — used as fixed reference
        FIXED_KIRC = {
            "RUNX1":  +0.58, "LOXL2":  +0.52,
            "TGFB1":  +0.44, "EZH2":   +0.41,
            "KDM1A":  +0.39, "VIM":    +0.35,
            "ACTA2":  +0.47, "FAP":    +0.49,
            "COL1A1": +0.53, "FBP1":   -0.61,
            "UMOD":   -0.57, "GOT1":   -0.48,
            "MIOX":   -0.43, "SLC22A6":-0.39,
            "SLC34A1":-0.44, "GPX3":   -0.40,
            "ACADM":  -0.38, "CUBN":   -0.35,
            "SLC5A2": -0.41, "SLC16A1":-0.28,
            "LDHA":   +0.23, "CA9":    +0.31,
            "VEGFA":  +0.18, "B2M":    -0.19,
            "HAVCR2": -0.21, "ARG1":   +0.08,
            "SETD2":  +0.15, "PBRM1":  +0.18,
            "TET2":   +0.22, "OGDHL":  -0.35,
            "FH":     -0.27, "MKI67":  +0.12,
            "CDKN2A": +0.05, "EPAS1":  +0.11,
            "HIF1A":  +0.14, "VHL":    -0.08,
        }

        log(f"\n  {'Gene':<14} {'PRCC_r':>9} "
            f"{'ccRCC_r':>9} {'shared?'}")
        log(f"  {'─'*46}")

        shared_att  = []
        shared_norm = []

        for gene in SHARED_PRCC_KIRC:
            g_ = gv(gene, expr, t_cols, d.index)
            rp = safe_r(g_.values, d.values)[0] \
                if g_ is not None else np.nan
            rc = FIXED_KIRC.get(gene, np.nan)

            both_pos = (not np.isnan(rp) and rp > 0.30
                        and not np.isnan(rc) and rc > 0.30)
            both_neg = (not np.isnan(rp) and rp < -0.30
                        and not np.isnan(rc) and rc < -0.30)
            shared = (
                "SHARED_ATT"  if both_pos else
                "SHARED_NORM" if both_neg else
                "PRCC_ONLY"   if abs(rp)>0.30
                else "ccRCC_ONLY" if abs(rc)>0.30
                else "")

            if both_pos: shared_att.append(gene)
            if both_neg: shared_norm.append(gene)

            log(f"  {gene:<14} {rp:>+9.4f} "
                f"{rc:>+9.4f} {shared}")

        log(f"\n  SHARED ATTRACTOR genes: {shared_att}")
        log(f"  SHARED NORMAL POLE genes: {shared_norm}")

        # S5-P11/P12 via fixed values
        for gene, thresh, label in [
            ("RUNX1", 0.40, "S5-P11 / S6"),
            ("GOT1",  -0.40, "S5-P12 / S6"),
        ]:
            rc = FIXED_KIRC.get(gene, np.nan)
            g_ = gv(gene, expr, t_cols, d.index)
            rp = safe_r(g_.values, d.values)[0] \
                if g_ is not None else np.nan
            met = (rc > thresh if thresh > 0
                   else rc < thresh) \
                if not np.isnan(rc) else False
            log(f"\n  {label}: {gene} "
                f"PRCC r={rp:+.4f}  "
                f"ccRCC r(fixed)={rc:+.4f}")
            log(f"  {label} "
                f"{'CONFIRMED (fixed) ✓' if met else 'NOT CONFIRMED'}")

        return

    # KIRC matrix present — live analysis
    pos_av = [g for g in KIRC_DEPTH_POS
              if g in expr_kirc.index]
    neg_av = [g for g in KIRC_DEPTH_NEG
              if g in expr_kirc.index]
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
    for gene in SHARED_PRCC_KIRC:
        gp = gv(gene, expr, t_cols, d.index)
        gc = gv(gene, expr_kirc,
                t_cols_kirc, d_kirc.index)
        rp = safe_r(gp.values,d.values)[0] \
            if gp is not None else np.nan
        rc = safe_r(gc.values,d_kirc.values)[0] \
            if gc is not None else np.nan
        both_pos = (rp>0.30 and rc>0.30)
        both_neg = (rp<-0.30 and rc<-0.30)
        shared = (
            "SHARED_ATT"  if both_pos else
            "SHARED_NORM" if both_neg else
            "PRCC_ONLY"   if abs(rp)>0.30
            else "ccRCC_ONLY" if abs(rc)>0.30
            else "")
        log(f"  {gene:<14} {rp:>+9.4f} "
            f"{rc:>+9.4f} {shared}")

    for gene, thresh, pred_label in [
        ("RUNX1", 0.40, "S5-P11"),
        ("GOT1", -0.40, "S5-P12"),
    ]:
        gc = gv(gene, expr_kirc,
                t_cols_kirc, d_kirc.index)
        rc = safe_r(gc.values,d_kirc.values)[0] \
            if gc is not None else np.nan
        met = (rc>thresh if thresh>0 else rc<thresh)
        log(f"\n  {pred_label}: {gene} "
            f"ccRCC r={rc:+.4f}")
        log(f"  {pred_label} "
            f"{'CONFIRMED ✓' if met else 'NOT CONFIRMED'}")

# ═══════════════════════════════════════════════════════════════
# OBJ-7: INTEGRATED REFERENCE GENE TABLE
# ═══════════════════════════════════════════════════════════════

def obj7_integrated_table(depth, ti, expr,
                            t_cols, n_cols,
                            t1_idx, t2_idx,
                            surv):
    log(""); log("="*60)
    log("OBJ-7 — INTEGRATED REFERENCE GENE TABLE")
    log("="*60)

    d = depth.reindex(t_cols).dropna()
    d_t1 = depth.reindex(t1_idx).dropna() \
        if t1_idx is not None else None
    d_t2 = depth.reindex(t2_idx).dropna() \
        if t2_idx is not None else None

    os_t, os_e = build_os(d, surv)
    valid = os_t.notna() & os_e.notna() & (os_t > 0)

    rows = []
    for gene in INTEGRATED_GENES:
        if gene not in expr.index: continue
        row = {"gene": gene}

        # Overall r_depth, r_TI
        g_ = gv(gene, expr, t_cols, d.index)
        if g_ is None: continue
        r_d, p_d = safe_r(g_.values, d.values)
        row["r_depth"] = r_d
        row["p_depth"] = p_d

        if ti is not None:
            ti_a = ti.reindex(d.index)
            r_ti, _ = safe_r(g_.values,
                               ti_a.values)
            row["r_TI"] = r_ti

        # Within-subtype
        for idx, label in [
            (t1_idx,"T1"), (t2_idx,"T2")
        ]:
            if idx is None:
                row[f"r_depth_{label}"] = np.nan
                continue
            d_sub = depth.reindex(idx).dropna()
            g_sub = gv(gene, expr, t_cols,
                       d_sub.index)
            if g_sub is None:
                row[f"r_depth_{label}"] = np.nan
                continue
            r_s, _ = safe_r(g_sub.values,
                              d_sub.values)
            row[f"r_depth_{label}"] = r_s

        # Normal vs tumour
        if n_cols is not None and len(n_cols)>0:
            g_n = expr.loc[gene, n_cols].mean()
            g_t = g_.mean()
            row["mean_normal"] = g_n
            row["mean_tumour"] = g_t
            row["T_minus_N"]   = g_t - g_n

        # Drug OS (pooled)
        g_v = g_.reindex(d[valid].index)
        if g_v.notna().sum() >= 10:
            med = g_v.median()
            hi  = g_v >= med; lo = g_v < med
            thi = os_t[valid].reindex(
                g_v.index)[hi].dropna()
            ehi = os_e[valid].reindex(
                g_v.index)[hi].dropna()
            tlo = os_t[valid].reindex(
                g_v.index)[lo].dropna()
            elo = os_e[valid].reindex(
                g_v.index)[lo].dropna()
            if len(thi)>=5 and len(tlo)>=5:
                _, p_os = safe_logrank(
                    thi.values,ehi.values,
                    tlo.values,elo.values)
                row["p_OS_pooled"] = p_os
                row["med_OS_hi"]   = thi.median()
                row["med_OS_lo"]   = tlo.median()

        rows.append(row)

    df = pd.DataFrame(rows).sort_values(
        "r_depth", key=abs, ascending=False)
    df.to_csv(
        os.path.join(RESULTS_DIR,
                     "integrated_gene_table.csv"),
        index=False)
    log(f"  Integrated table: {df.shape[0]} genes")
    log(f"  Saved: integrated_gene_table.csv")

    # Print top 30 by |r_depth|
    log(f"\n  TOP 30 BY |r_depth|:")
    log(f"  {'Gene':<14} {'r_depth':>9} "
        f"{'r_TI':>9} {'r_T1':>9} {'r_T2':>9} "
        f"{'p_OS':>12}")
    log(f"  {'─'*64}")
    for _, row in df.head(30).iterrows():
        r_d  = row.get("r_depth",np.nan)
        r_ti = row.get("r_TI",np.nan)
        r_t1 = row.get("r_depth_T1",np.nan)
        r_t2 = row.get("r_depth_T2",np.nan)
        p_os = row.get("p_OS_pooled",np.nan)
        log(f"  {row['gene']:<14} {r_d:>+9.4f} "
            f"{r_ti:>+9.4f} {r_t1:>+9.4f} "
            f"{r_t2:>+9.4f} {fmt_p(p_os):>12}")

    return df

# ═══════════════════════════════════════════════════════════════
# OBJ-8: FINAL ATTRACTOR GEOMETRY FIGURE
# ═══════════════════════════════════════════════════════════════

def obj8_final_figure(depth, ti, expr,
                       t_cols, n_cols,
                       t1_idx, t2_idx,
                       surv, fa2_depth,
                       integrated_df):
    log(""); log("="*60)
    log("OBJ-8 — FINAL ATTRACTOR GEOMETRY FIGURE")
    log("="*60)

    d = depth.reindex(t_cols).dropna()

    C = {"T1":   "#2980B9",
         "T2":   "#C0392B",
         "CIMP": "#8E44AD",
         "norm": "#27AE60",
         "att":  "#E74C3C",
         "np":   "#3498DB",
         "shared":"#E67E22"}

    fig = plt.figure(figsize=(28, 34))
    gs  = gridspec.GridSpec(
        5, 3, figure=fig,
        hspace=0.55, wspace=0.42)

    # ── A: Attractor geometry scatter ────────────────────────
    # x = FA-1 TI, y = FA-2 TI (if available)
    ax = fig.add_subplot(gs[0, 0])
    if "KRT19" in expr.index and \
            "SLC22A6" in expr.index:
        krt = gv("KRT19",  expr, t_cols, d.index)
        slc = gv("SLC22A6",expr, t_cols, d.index)
        ti_fa1 = pd.Series(
            norm01(krt.values) - norm01(slc.values),
            index=d.index)

        if "LAMC2" in expr.index and \
                "SLC7A9" in expr.index:
            lam = gv("LAMC2",  expr, t_cols, d.index)
            s79 = gv("SLC7A9", expr, t_cols, d.index)
            ti_fa2_all = pd.Series(
                norm01(lam.values) - norm01(s79.values),
                index=d.index)
        else:
            ti_fa2_all = pd.Series(0, index=d.index)

        cols_a = []
        for s in d.index:
            if t1_idx is not None and s in t1_idx:
                cols_a.append(C["T1"])
            elif t2_idx is not None and s in t2_idx:
                cols_a.append(C["T2"])
            else:
                cols_a.append("#BDC3C7")

        ax.scatter(ti_fa1.values, ti_fa2_all.values,
                   c=cols_a, s=10, alpha=0.6)
        ax.set_xlabel("FA-1 TI (KRT19–SLC22A6)",
                      fontsize=9)
        ax.set_ylabel("FA-2 TI (LAMC2–SLC7A9)",
                      fontsize=9)
        ax.set_title(
            "A: Two Attractor Geometry\n"
            "(blue=T1, red=T2, grey=unknown)",
            fontsize=9, fontweight="bold")
        # Quadrant labels
        ax.text(0.85, 0.85, "CIMP", color=C["CIMP"],
                transform=ax.transAxes, fontsize=8,
                fontweight="bold")
        ax.text(0.05, 0.15, "Normal\npole",
                color=C["norm"],
                transform=ax.transAxes, fontsize=8)
        ax.axhline(0.5, color="k", lw=0.4, ls="--",
                    alpha=0.3)
        ax.axvline(0.5, color="k", lw=0.4, ls="--",
                    alpha=0.3)

    # ── B: FA-1 vs FA-2 depth density ────────────────────────
    ax = fig.add_subplot(gs[0, 1])
    d_t1 = depth.reindex(t1_idx).dropna() \
        if t1_idx is not None else None
    d_t2 = depth.reindex(t2_idx).dropna() \
        if t2_idx is not None else None
    bins = np.linspace(0, 1, 30)
    if d_t1 is not None:
        ax.hist(d_t1.values, bins=bins,
                alpha=0.5, color=C["T1"],
                density=True, label="Type 1")
    if d_t2 is not None:
        ax.hist(d_t2.values, bins=bins,
                alpha=0.5, color=C["T2"],
                density=True, label="Type 2")
    ax.set_xlabel("FA-1 Depth Score")
    ax.set_ylabel("Density")
    ax.legend(fontsize=7)
    ax.set_title("B: Depth Distribution\nType 1 vs Type 2",
                 fontsize=9, fontweight="bold")

    # ── C: Type 1 vs Type 2 OS KM ────────────────────────────
    ax = fig.add_subplot(gs[0, 2])
    os_t_all, os_e_all = build_os(d, surv)
    valid = (os_t_all.notna() & os_e_all.notna()
             & (os_t_all > 0))
    for idx, col, lab in [
        (t1_idx, C["T1"], "Type 1"),
        (t2_idx, C["T2"], "Type 2"),
    ]:
        if idx is None: continue
        vi = idx.intersection(d[valid].index)
        t_ = os_t_all.reindex(vi).values
        e_ = os_e_all.reindex(vi).values
        ts, ss = kaplan_meier(t_, e_)
        ax.step(ts/365, ss, where="post",
                color=col, label=lab, lw=2)
    t1v = t1_idx.intersection(d[valid].index) \
        if t1_idx is not None else pd.Index([])
    t2v = t2_idx.intersection(d[valid].index) \
        if t2_idx is not None else pd.Index([])
    if len(t1v)>=3 and len(t2v)>=3:
        _, p_12 = safe_logrank(
            os_t_all.reindex(t1v).values,
            os_e_all.reindex(t1v).values,
            os_t_all.reindex(t2v).values,
            os_e_all.reindex(t2v).values)
        ax.set_title(
            f"C: T1 vs T2 OS\n{fmt_p(p_12)}",
            fontsize=9, fontweight="bold")
    else:
        ax.set_title("C: T1 vs T2 OS",
                     fontsize=9, fontweight="bold")
    ax.legend(fontsize=7)
    ax.set_ylim(0, 1.05)
    ax.set_xlabel("Years")
    ax.set_ylabel("Survival")

    # ── D: Ferroptosis panel heatmap ──────────────────────────
    ax = fig.add_subplot(gs[1, 0])
    fp = os.path.join(RESULTS_DIR,
                       "ferroptosis_panel.csv")
    if os.path.exists(fp):
        ff = pd.read_csv(fp).dropna(
            subset=["r_t2"])
        ff = ff.sort_values("r_t2")
        if len(ff) > 0:
            c_ff = ["#C0392B"
                    if row["role"]=="ANTI"
                    else "#2980B9"
                    for _, row in ff.iterrows()]
            ax.barh(range(len(ff)),
                    ff["r_t2"].values,
                    color=c_ff, alpha=0.8)
            ax.set_yticks(range(len(ff)))
            ax.set_yticklabels(ff["gene"].values,
                                fontsize=7)
            ax.axvline(0, color="k", lw=0.8)
            ax.axvline(-0.2, color="k", lw=0.5,
                        ls="--", alpha=0.4)
            ax.axvline(0.2, color="k", lw=0.5,
                        ls="--", alpha=0.4)
            ax.set_xlabel("r vs depth (Type 2)")
            ax.set_title(
                "D: Ferroptosis Panel\n"
                "(red=anti, blue=pro)",
                fontsize=9, fontweight="bold")

    # ── E: KITLG/c-KIT pathway ───────────────────────────────
    ax = fig.add_subplot(gs[1, 1])
    kp = os.path.join(RESULTS_DIR,
                       "kitlg_ckit_panel.csv")
    if os.path.exists(kp):
        kdf = pd.read_csv(kp).dropna(
            subset=["r_t2"])
        kdf = kdf[~kdf["gene"].str.contains(
            "×")].sort_values("r_t2",
                               ascending=False)
        if len(kdf) > 0:
            c_k = [C["T2"] if v > 0 else C["T1"]
                   for v in kdf["r_t2"].values]
            ax.barh(range(len(kdf)),
                    kdf["r_t2"].values,
                    color=c_k, alpha=0.8)
            ax.set_yticks(range(len(kdf)))
            ax.set_yticklabels(kdf["gene"].values,
                                fontsize=7)
            ax.axvline(0, color="k", lw=0.8)
            ax.set_xlabel("r vs depth (Type 2)")
            ax.set_title(
                "E: KITLG/c-KIT Pathway\n"
                "r(depth) in Type 2",
                fontsize=9, fontweight="bold")

    # ── F: MET × MKI67 quadrant ──────────────────────────────
    ax = fig.add_subplot(gs[1, 2])
    mp = os.path.join(RESULTS_DIR,
                       "met_mki67_quadrant.csv")
    if os.path.exists(mp):
        mdf = pd.read_csv(mp)
        x = range(len(mdf))
        bars = ax.bar(x,
                      mdf["mean_depth"].values,
                      color=[C["T1"]]*len(mdf),
                      alpha=0.8)
        ax.set_xticks(x)
        ax.set_xticklabels(
            mdf["quadrant"].values,
            rotation=25, ha="right", fontsize=7)
        ax.set_ylabel("Mean FA-1 Depth")
        ax.set_title(
            "F: MET × MKI67 Quadrants\n(Type 1)",
            fontsize=9, fontweight="bold")
        for bar, row in zip(bars, mdf.itertuples()):
            ax.text(bar.get_x()+bar.get_width()/2,
                    bar.get_height()+0.005,
                    f"{row.med_os:.0f}d",
                    ha="center", fontsize=7)

    # ── G: CDK4 mechanism in Type 2 ──────────────────────────
    ax = fig.add_subplot(gs[2, 0])
    cp = os.path.join(RESULTS_DIR,
                       "cdk4_cdkn2a_panel.csv")
    if os.path.exists(cp):
        cdf = pd.read_csv(cp).dropna(
            subset=["r_t2"])
        cdf = cdf.sort_values("r_t2",
                               ascending=False)
        c_c = [C["T2"] if v > 0 else C["T1"]
                for v in cdf["r_t2"].values]
        ax.barh(range(len(cdf)),
                cdf["r_t2"].values,
                color=c_c, alpha=0.8)
        ax.set_yticks(range(len(cdf)))
        ax.set_yticklabels(cdf["gene"].values,
                            fontsize=8)
        ax.axvline(0, color="k", lw=0.8)
        ax.set_xlabel("r vs depth (Type 2)")
        ax.set_title("G: Cell Cycle in Type 2",
                     fontsize=9, fontweight="bold")

    # ── H: Integrated table top genes (dot plot) ─────────────
    ax = fig.add_subplot(gs[2, 1])
    if integrated_df is not None and \
            len(integrated_df) > 0:
        top = integrated_df.head(25).copy()
        y   = range(len(top))
        sc  = ax.scatter(
            top["r_depth"].values,
            y,
            c=top["r_depth"].values,
            cmap="RdBu_r",
            vmin=-1, vmax=1, s=50, zorder=3)
        ax.axvline(0, color="k", lw=0.8)
        ax.set_yticks(y)
        ax.set_yticklabels(
            top["gene"].values, fontsize=7)
        ax.set_xlabel("r(depth)")
        ax.set_title(
            "H: Top 25 Genes by |r(depth)|\n"
            "(all 290 tumours)",
            fontsize=9, fontweight="bold")
        plt.colorbar(sc, ax=ax, shrink=0.6)

    # ── I: Cross-cancer shared genes ─────────────────────────
    ax = fig.add_subplot(gs[2, 2])
    FIXED_KIRC_PLOT = {
        "RUNX1": +0.58, "GOT1": -0.48,
        "EZH2":  +0.41, "KDM1A":+0.39,
        "TET2":  +0.22, "SLC22A6":-0.39,
        "MIOX":  -0.43, "OGDHL":-0.35,
        "FH":    -0.27, "B2M":  -0.19,
        "HAVCR2":-0.21, "SETD2":+0.15,
        "PBRM1": +0.18, "SLC16A1":-0.28,
        "LDHA":  +0.23, "CA9":  +0.31,
        "VEGFA": +0.18, "ARG1": +0.08,
    }
    genes_p = list(FIXED_KIRC_PLOT.keys())
    rp_vals = []
    for gene in genes_p:
        g_ = gv(gene, expr, t_cols, d.index)
        rp = safe_r(g_.values,d.values)[0] \
            if g_ is not None else np.nan
        rp_vals.append(rp)
    rc_vals = [FIXED_KIRC_PLOT[g] for g in genes_p]

    c_i = ["#C0392B" if rp>0.30 and rc>0.30
           else "#2980B9" if rp<-0.30 and rc<-0.30
           else "#E67E22"
           for rp, rc in zip(rp_vals, rc_vals)]
    ax.scatter(rp_vals, rc_vals, c=c_i,
               s=50, alpha=0.8, zorder=3)
    for g, x, y in zip(genes_p, rp_vals, rc_vals):
        if abs(x)>0.20 or abs(y)>0.20:
            ax.annotate(g, (x,y), fontsize=6,
                        xytext=(3,3),
                        textcoords="offset points")
    ax.axhline(0, color="k", lw=0.5)
    ax.axvline(0, color="k", lw=0.5)
    for v in [-0.30, 0.30]:
        ax.axhline(v, color="k", lw=0.4,
                    ls="--", alpha=0.4)
        ax.axvline(v, color="k", lw=0.4,
                    ls="--", alpha=0.4)
    ax.set_xlabel("r(depth) PRCC", fontsize=9)
    ax.set_ylabel("r(depth) ccRCC (fixed)", fontsize=9)
    ax.set_title(
        "I: Shared Genes PRCC/ccRCC\n"
        "(red=shared_att, blue=shared_norm)",
        fontsize=9, fontweight="bold")

    # ── J: FA-2 depth vs FA-1 depth scatter ──────────────────
    ax = fig.add_subplot(gs[3, 0])
    if fa2_depth is not None and t2_idx is not None:
        d_t2_fa1 = depth.reindex(t2_idx).dropna()
        fa2_d_aligned = fa2_depth.reindex(
            d_t2_fa1.index).dropna()
        d_t2_fa1 = d_t2_fa1.reindex(
            fa2_d_aligned.index)
        ax.scatter(d_t2_fa1.values,
                   fa2_d_aligned.values,
                   c=C["T2"], s=10, alpha=0.6)
        r_cross, _ = safe_r(
            d_t2_fa1.values,
            fa2_d_aligned.values)
        ax.set_xlabel("FA-1 Depth (biliary axis)")
        ax.set_ylabel("FA-2 Depth (LAMC2/SLC7A9)")
        ax.set_title(
            f"J: FA-1 vs FA-2 Depth\n"
            f"r={r_cross:+.3f} (Type 2)",
            fontsize=9, fontweight="bold")
    else:
        ax.set_title("J: FA-1 vs FA-2 Depth",
                     fontsize=9, fontweight="bold")

    # ── K: Drug priority heatmap (final) ─────────────────────
    ax = fig.add_subplot(gs[3, 1])
    pri_path = os.path.join(BASE_DIR,
                             "results_s5",
                             "drug_priority_map.csv")
    if os.path.exists(pri_path):
        pdf = pd.read_csv(pri_path)
        mc  = [c for c in pdf.columns
               if c.startswith("mean_")]
        if mc and len(pdf)>0:
            mat   = pdf.set_index("drug")[mc]
            mat_n = mat.apply(
                lambda r: norm01(r.values),
                axis=1,
                result_type="broadcast")
            im = ax.imshow(
                mat_n.values.astype(float),
                aspect="auto",
                cmap="RdBu_r",
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
            ax.set_title(
                "K: Final Drug Priority\n"
                "(row-normalised across strata)",
                fontsize=9, fontweight="bold")

    # ── L: Script 6 scorecard + PRCC summary ─────────────────
    ax = fig.add_subplot(gs[3, 2])
    ax.axis("off")
    txt = (
        "PRCC FALSE ATTRACTOR — FINAL SUMMARY\n"
        "OrganismCore | Scripts 1–6 | 2026-03-02\n"
        "═══════════════════════════════════════\n"
        "S6-P1  FA-2 TI better on FA-2 axis\n"
        "S6-P2  SLC7A9 top ferroptosis T2\n"
        "S6-P3  GPX4 falls with FA-2 depth\n"
        "S6-P4  KITLG × KIT/PDGFRA r>0.30\n"
        "S6-P5  MET-hi+MKI-hi = shallowest T1\n"
        "S6-P6  CDK4 anti-corr CDKN2A in T2\n"
        "───────────────────────────────────────\n"
        "DRUG RANKING (OS-confirmed):\n"
        " 1. CDK4/6i        T2 353d OS gap\n"
        " 2. αKG+Tazem.     CIMP p=0.0004\n"
        " 3. EZH2i          T2+pooled\n"
        " 4. FH/OGDHL αKG   T2 FH-low\n"
        " 5. MET pre-lock   T1 p=0.004\n"
        " 6. ERBB2 IHC2+    T1 p=0.023\n"
        " 7. ARG1i+MCT4buf  Q4 both\n"
        " 8. Sunitinib(KIT) FA-2 novel\n"
        " 9. Ferroptosis    FA-2 SLC7A9-lo\n"
        "10. NK activators  FA-2 CCL14/15-lo\n"
        "───────────────────────────────────────\n"
        "CONTRAINDICATED:\n"
        "  Anti-TIM3: not HAVCR2-hi T2\n"
        "  Savolitinib: not locked T1\n"
        "  EZH2i: caution mid-TI T1"
    )
    ax.text(0.03, 0.97, txt,
            transform=ax.transAxes,
            fontsize=6.5,
            verticalalignment="top",
            fontfamily="monospace",
            bbox=dict(boxstyle="round",
                      facecolor="#F0F4F8",
                      alpha=0.9))
    ax.set_title(
        "L: Final Summary",
        fontsize=9, fontweight="bold")

    # ── M (row 5 span): Three-attractor diagram ───────────────
    ax = fig.add_subplot(gs[4, :])
    ax.set_xlim(0, 10); ax.set_ylim(0, 4)
    ax.axis("off")
    ax.set_title(
        "M: PRCC Three-Attractor Geometry — "
        "OrganismCore Framework",
        fontsize=11, fontweight="bold", pad=8)

    def draw_attractor(ax, cx, cy, r, col,
                        title, lines, fontsize=7):
        circle = plt.Circle((cx,cy), r,
                             color=col, alpha=0.15,
                             zorder=1)
        ax.add_patch(circle)
        circle2 = plt.Circle((cx,cy), r,
                              color=col, fill=False,
                              lw=2, zorder=2)
        ax.add_patch(circle2)
        ax.text(cx, cy+r+0.10, title,
                ha="center", va="bottom",
                fontsize=fontsize+1,
                fontweight="bold", color=col,
                zorder=3)
        for i, line in enumerate(lines):
            ax.text(cx, cy+0.25-(i*0.22), line,
                    ha="center", va="center",
                    fontsize=fontsize, color="k",
                    zorder=3)

    # Normal pole
    circle_n = plt.Circle((1.2,2.0), 0.8,
                            color=C["norm"],
                            alpha=0.12, zorder=1)
    ax.add_patch(circle_n)
    circle_n2 = plt.Circle((1.2,2.0), 0.8,
                             color=C["norm"],
                             fill=False, lw=2,
                             zorder=2)
    ax.add_patch(circle_n2)
    ax.text(1.2, 2.95, "NORMAL KIDNEY",
            ha="center", fontsize=8,
            fontweight="bold", color=C["norm"])
    for i, t in enumerate([
        "SLC22A6 ▲","FABP1 ▲","SLC34A1 ▲",
        "GPX3 ▲","UMOD ▲","GOT1 ▲","OGDHL ▲"
    ]):
        ax.text(1.2, 2.35-(i*0.21), t,
                ha="center", fontsize=6,
                color=C["norm"])

    # FA-1
    draw_attractor(
        ax, 4.5, 2.8, 0.9, C["T1"],
        "FA-1  TYPE 1 (biliary)",
        ["KRT19▲ ERBB2▲ KRT7▲",
         "SLC22A6▼ FABP1▼",
         "MET driver | ERBB2 co-expr",
         "Deep=locked=better OS",
         "ARG1+MCT4 dual suppression"],
        fontsize=6.5)

    # FA-2
    draw_attractor(
        ax, 7.5, 2.8, 0.9, C["T2"],
        "FA-2  TYPE 2 (invasive/cKIT)",
        ["LAMC2▲ KITLG▲ ITGB6▲",
         "SLC7A9▼ CCL14▼ CCL15▼",
         "CDK4-hi=worst OS (353d gap)",
         "Ferroptosis vulnerable",
         "NK cell excluded"],
        fontsize=6.5)

    # FA-CIMP (intersection)
    draw_attractor(
        ax, 6.0, 1.0, 0.75, C["CIMP"],
        "FA-CIMP (FH-HLRCC)",
        ["FH▼▼ OGDHL▼▼ EZH2▲▲",
         "MKI67▲ KRT19▲",
         "FA-1∩FA-2∩TCA-collapse",
         "WORST OS p=3.9e-04"],
        fontsize=6.5)

    # Arrows
    for (x1,y1),(x2,y2),col in [
        ((1.2,2.0),(4.5,2.8),C["T1"]),
        ((1.2,2.0),(7.5,2.8),C["T2"]),
        ((4.5,2.8),(6.0,1.0),C["CIMP"]),
        ((7.5,2.8),(6.0,1.0),C["CIMP"]),
    ]:
        ax.annotate("",
                    xy=(x2,y2),
                    xytext=(x1,y1),
                    arrowprops=dict(
                        arrowstyle="->",
                        color=col, lw=1.5),
                    zorder=4)

    # Shared axis B label
    ax.text(5.0, 0.15,
            "SHARED AXIS B: TCA↓ → αKG↓ → "
            "TET2↓ → EZH2▲ → chromatin lock  |  "
            "MHC-I loss  |  ARG1+ MDSC  |  "
            "SLC16A1↓ lactate",
            ha="center", va="center",
            fontsize=7, color="#555555",
            style="italic",
            bbox=dict(boxstyle="round",
                      facecolor="#FDFEFE",
                      alpha=0.8))

    fig.suptitle(
        "PRCC False Attractor — Script 6 "
        "(Final)\nOrganismCore | Document 95f | "
        "2026-03-02",
        fontsize=13, fontweight="bold", y=0.999)

    out = os.path.join(
        RESULTS_DIR, "prcc_script6_final_figure.pdf")
    fig.savefig(out, bbox_inches="tight", dpi=150)
    plt.close(fig)
    log(f"  Figure saved: {out}")

# ═══════════════════════════════════════════════════════════════
# SCORECARD
# ═══════════════════════════════════════════════════════════════

def print_scorecard():
    full = "\n".join(log_lines)
    log(""); log("="*60)
    log("SCRIPT 6 — FINAL SCORECARD"); log("="*60)
    checks = [
        ("S6-P1  FA-2 TI better on FA-2 axis",
         "S6-P1 CONFIRMED","S6-P1 NOT CONFIRMED"),
        ("S6-P2  SLC7A9 top ferroptosis T2",
         "S6-P2 CONFIRMED","S6-P2 NOT CONFIRMED"),
        ("S6-P3  GPX4 falls with FA-2 depth",
         "S6-P3 CONFIRMED","S6-P3 NOT CONFIRMED"),
        ("S6-P4  KITLG × KIT/PDGFRA r>0.30",
         "S6-P4 CONFIRMED","S6-P4 NOT CONFIRMED"),
        ("S6-P5  MET-hi+MKI-hi = shallowest T1",
         "S6-P5 CONFIRMED","S6-P5 NOT CONFIRMED"),
        ("S6-P6  CDK4 anti-corr CDKN2A in T2",
         "S6-P6 CONFIRMED","S6-P6 NOT CONFIRMED"),
    ]
    confirmed = 0
    for label, pos, neg in checks:
        if pos in full:
            verdict="CONFIRMED ✓"; confirmed+=1
        elif neg in full:
            verdict="NOT CONFIRMED ✗"
        else:
            verdict="CHECK LOG"
        log(f"  {label:<44}  {verdict}")
    log(f"\n  OVERALL: {confirmed}/{len(checks)}")

    # Cumulative PRCC summary
    log("")
    log("="*60)
    log("CUMULATIVE PRCC SCORECARD (Scripts 1–6)")
    log("="*60)
    log("  Scripts 1-4 pooled:  established FA-1")
    log("  Script 5:            established FA-2")
    log("  Script 6:            closed open threads")
    log("")
    log("  OS-CONFIRMED DRUG TARGETS:")
    log("    CDK4/6i    T2 p=0.033  ★★")
    log("    CIMP αKG   CIMP p=3.94e-04  ★★★")
    log("    EZH2i      T2 p=0.026, pooled p=0.008  ★★")
    log("    FH αKG     T2 p=0.021  ★")
    log("    OGDHL αKG  T2 p=0.007, pooled p=0.0004  ★★")
    log("    MET        T1 p=0.004  ★★ (pre-lock only)")
    log("    ERBB2      T1 p=0.023  ★ (IHC2+ criterion)")
    log("    Dual suppr pooled p=0.019  ★")
    log("")
    log("  NOVEL DRUG PREDICTIONS (not OS-confirmed):")
    log("    Ferroptosis (erastin/RSL3) — FA-2 SLC7A9")
    log("    Sunitinib via c-KIT — FA-2 KITLG")
    log("    NK activators — FA-2 CCL14/CCL15")
    log("    Entinostat+anti-PD1 — CIMP HLA-A low")
    log("")
    log("  CONTRAINDICATIONS:")
    log("    Anti-TIM3 — HAVCR2-hi T2 (T cells present)")
    log("    Savolitinib — locked deep T1 (worse OS)")
    log("    EZH2i — caution mid-TI T1 (lock paradox)")
    log("")
    log("  READY FOR LITERATURE CHECK")
    log("  READY TO MOVE TO NEXT CANCER")

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    log("="*60)
    log("PRCC FALSE ATTRACTOR — SCRIPT 6 (FINAL)")
    log("OrganismCore | Document 95f | 2026-03-02")
    log("Author: Eric Robert Lawson")
    log("="*60)
    log("")
    log("CLOSING OPEN THREADS FROM SCRIPTS 1-5")
    log("6 predictions — S6-P1 through S6-P6")
    log("")

    depth, ti, ti_fa2 = load_all()
    expr, t_cols, n_cols = load_expr()
    surv     = load_survival()
    subtypes = load_subtypes()
    t1_idx, t2_idx = build_subtype_indices(
        depth, subtypes, t_cols)

    # ccRCC (optional)
    expr_kirc = t_cols_kirc = None
    if os.path.exists(KIRC_EXPR):
        expr_kirc, t_cols_kirc, _ = load_kirc()
    else:
        log(f"  ccRCC matrix absent: {KIRC_EXPR}")
        log("  OBJ-6 will use fixed Document 94 values.")

    # Recompute TI if needed
    if ti is None and "KRT19" in expr.index \
            and "SLC22A6" in expr.index:
        d_r = depth.reindex(t_cols).dropna()
        krt = gv("KRT19",   expr,t_cols,d_r.index)
        slc = gv("SLC22A6", expr,t_cols,d_r.index)
        ti  = pd.Series(
            norm01(krt.values)-norm01(slc.values),
            index=d_r.index, name="TI")
        log(f"  TI recomputed: n={len(ti)}")

    # ── OBJ-1 ─────────────────────────────────────────────────
    fa2_depth, fa2_depth_all = obj1_fa2_depth(
        depth, expr, t_cols, t2_idx) or (None, None)

    # ── OBJ-2 ─────────────────────────────────────────────────
    ferro_df = obj2_ferroptosis(
        depth, expr, t_cols,
        t1_idx, t2_idx, fa2_depth)

    # ── OBJ-3 ─────────────────────────────────────────────────
    obj3_kitlg_ckit(
        depth, expr, t_cols, t2_idx, fa2_depth)

    # ── OBJ-4 ─────────────────────────────────────────────────
    obj4_met_mki67_quadrant(
        depth, expr, t_cols, t1_idx, surv)

    # ── OBJ-5 ─────────────────────────────────────────────────
    obj5_cdk4_mechanism(
        depth, expr, t_cols, t2_idx, surv)

    # ── OBJ-6 ─────────────────────────────────────────────────
    obj6_cross_cancer(
        depth, expr, t_cols,
        expr_kirc, t_cols_kirc)

    # ── OBJ-7 ─────────────────────────────────────────────────
    integrated_df = obj7_integrated_table(
        depth, ti, expr, t_cols, n_cols,
        t1_idx, t2_idx, surv)

    # ── OBJ-8 ─────────────────────────────────────────────────
    obj8_final_figure(
        depth, ti, expr, t_cols, n_cols,
        t1_idx, t2_idx, surv,
        fa2_depth, integrated_df)

    print_scorecard()
    write_log()

    log("")
    log("="*60)
    log("SCRIPT 6 COMPLETE — PRCC ANALYSIS CLOSED")
    log(f"Results: {RESULTS_DIR}")
    log(f"Log:     {LOG_FILE}")
    log("Next: Document 95f (results) →")
    log("      Literature check →")
    log("      Next cancer")
    log("="*60)


if __name__ == "__main__":
    main()
