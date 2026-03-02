"""
ICC FALSE ATTRACTOR — SCRIPT 1 v3
CORE ANALYSIS — CLINICAL PARSING FIXED

Fix from v2:
  Clinical parser now uses hardcoded
  column indices from inspection:
    sampleID:          col 0
    days_to_death:     col 28
    days_to_last_followup: col 30
    vital_status:      col 92
    pathologic_stage:  col 67
    histological_type: col 44
    grade:             col 55
  OS time = days_to_death (if DECEASED)
            else days_to_last_followup
  Both in days → /30.44 → months

Author: Eric Robert Lawson
Framework: OrganismCore
Doc: 93c | Date: 2026-03-02
"""

import os
import re
import gzip
import time
import requests
import numpy as np
import pandas as pd
from scipy import stats
from lifelines import KaplanMeierFitter
from lifelines.statistics import logrank_test
from lifelines import CoxPHFitter
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import warnings
warnings.filterwarnings("ignore")

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR    = "./icc_false_attractor/"
TCGA_DIR    = os.path.join(BASE_DIR, "tcga_chol/")
GEO_DIR     = os.path.join(BASE_DIR, "geo_icc/")
DATA_DIR    = os.path.join(BASE_DIR, "data/")
RESULTS_DIR = os.path.join(BASE_DIR, "results_s1v3/")
LOG_FILE    = os.path.join(RESULTS_DIR,
                           "analysis_log_s1v3.txt")
for d in [TCGA_DIR, GEO_DIR, DATA_DIR, RESULTS_DIR]:
    os.makedirs(d, exist_ok=True)

# ============================================================
# GENE PANELS
# ============================================================

CHOL_SW = [
    "FOXA2","HNF4A","ALB","APOB",
    "CYP3A4","ALDOB","G6PC","GGT1",
    "HNF1B","KLF4","CFTR","AQP1",
    "ANXA4","SLC4A2",
]
ICC_FA_T = [
    "SOX4","SOX9","PROM1","CD44",
    "CDC20","BIRC5","TOP2A","MKI67",
    "CCNB1","CDK4","EZH2","HDAC2",
    "DNMT1","TWIST1","VIM",
    "ZEB1","ZEB2","CDKN2A",
]
ICC_FA_S = [
    "FAP","ACTA2","COL1A1","POSTN",
    "TGFB1","MMP2","MMP9","FN1","WNT5A",
]
ICC_DRIVERS = [
    "FGFR2","IDH1","IDH2","BAP1",
    "ARID1A","SMAD4","KRAS","EGFR",
    "ERBB2","NOTCH1","NOTCH2","SF3B1",
    "PTEN","TP53","RB1","CCND1",
    "CTNNB1","STAT3","CD8A","PRF1",
    "CD274","FOXP3","HAVCR2","CA9",
    "VEGFA","GLUL","MET","SNAI1","CDK6",
]
ALL_PANEL = list(set(
    CHOL_SW + ICC_FA_T + ICC_FA_S
    + ICC_DRIVERS
))

# ============================================================
# COLUMN INDICES — HARDCODED FROM INSPECTION
# ============================================================

COL_SAMPLE_ID    = 0
COL_DAYS_DEATH   = 28
COL_DAYS_FOLLOW  = 30
COL_VITAL        = 92
COL_STAGE        = 67
COL_HIST_TYPE    = 44
COL_GRADE        = 55
COL_T            = 66
COL_N            = 65
COL_M            = 64
COL_RESIDUAL     = 80

# ============================================================
# LOGGING
# ============================================================

log_lines = []

def log(msg=""):
    print(msg)
    log_lines.append(str(msg))

def write_log():
    with open(LOG_FILE, "w") as f:
        f.write("\n".join(log_lines))

def fmt_p(p):
    if p is None or (
        isinstance(p, float) and np.isnan(p)
    ):
        return "p=N/A     "
    if p < 0.001:   return f"p={p:.2e} ***"
    elif p < 0.01:  return f"p={p:.2e}  **"
    elif p < 0.05:  return f"p={p:.4f}   *"
    else:           return f"p={p:.4f}  ns"

def norm01(arr):
    arr = np.asarray(arr, float)
    mn, mx = np.nanmin(arr), np.nanmax(arr)
    if mx > mn:
        return (arr - mn) / (mx - mn)
    return np.full_like(arr, 0.5)

def safe_r(x, y):
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    m = np.isfinite(x) & np.isfinite(y)
    if m.sum() < 5:
        return np.nan, np.nan
    return stats.pearsonr(x[m], y[m])

def logrank_p(t1, e1, t0, e0):
    t1=np.asarray(t1,float); e1=np.asarray(e1,float)
    t0=np.asarray(t0,float); e0=np.asarray(e0,float)
    m1=np.isfinite(t1)&np.isfinite(e1)&(t1>0)
    m0=np.isfinite(t0)&np.isfinite(e0)&(t0>0)
    if m1.sum()<5 or m0.sum()<5: return np.nan
    try:
        return logrank_test(
            t1[m1],t0[m0],e1[m1],e0[m0]
        ).p_value
    except Exception: return np.nan

def try_get(url, dest, min_size=500):
    if (os.path.exists(dest)
            and os.path.getsize(dest) > min_size):
        log(f"  Cached {os.path.getsize(dest):,}b")
        return dest
    log(f"  GET {url}")
    try:
        r = requests.get(
            url, stream=True, timeout=300,
            headers={"User-Agent":"Mozilla/5.0"},
        )
        log(f"  HTTP {r.status_code}")
        if r.status_code == 200:
            data = b"".join(r.iter_content(1024*1024))
            if len(data) > min_size:
                with open(dest,"wb") as f:
                    f.write(data)
                log(f"  Saved {len(data):,}b")
                return dest
            log(f"  Too small: {len(data)}b")
    except Exception as ex:
        log(f"  Error: {ex}")
    return None

# ============================================================
# LOAD EXPRESSION
# ============================================================

def load_tcga_expr():
    path = os.path.join(TCGA_DIR, "CHOL_expr.tsv.gz")
    if not os.path.exists(path):
        url = (
            "https://tcga-xena-hub.s3.us-east-1"
            ".amazonaws.com/download/"
            "TCGA.CHOL.sampleMap%2FHiSeqV2.gz"
        )
        path = try_get(url, path, 100000)
    if path is None:
        return {}, []

    expr = {}
    sample_ids = []
    genes_want = set(ALL_PANEL)
    opener = (
        gzip.open(path,"rt",
            encoding="utf-8",errors="ignore")
        if path.endswith(".gz")
        else open(path,"r",
            encoding="utf-8",errors="ignore")
    )
    with opener as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if not sample_ids:
                sample_ids = [p.strip() for p in parts[1:]]
                continue
            gene = parts[0].strip().strip('"')
            if gene not in genes_want: continue
            try:
                vals = np.array([
                    float(p.strip())
                    if p.strip() not in
                    ["","NA","nan","NaN"]
                    else np.nan
                    for p in parts[1:]
                ])
                expr[gene] = vals
            except ValueError: pass
    log(f"  Expr: {len(sample_ids)} samples, "
        f"{len(expr)} genes")
    return expr, sample_ids

# ============================================================
# LOAD OS — HARDCODED COLUMN PARSER
# ============================================================

def load_tcga_os_hardcoded(sample_ids):
    """
    Parse CHOL_pheno.txt using exact
    column indices identified by inspector.

    OS time logic:
      If vital_status == DECEASED:
        use days_to_death (col 28)
      Else (LIVING):
        use days_to_last_followup (col 30)
      Convert days → months (/30.44)

    OS event:
      DECEASED → 1
      LIVING   → 0

    Also extract:
      stage (col 67)
      histological_type (col 44)
        filter: intrahepatic ICC only
      grade (col 55)
    """
    clin_path = os.path.join(
        TCGA_DIR, "CHOL_pheno.txt"
    )
    # Try alternate names
    for alt in ["CHOL_pheno.gz",
                "CHOL_clinicalMatrix",
                "CHOL_clin_fresh.txt"]:
        if not os.path.exists(clin_path):
            clin_path = os.path.join(
                TCGA_DIR, alt
            )

    n = len(sample_ids)
    os_t    = np.full(n, np.nan)
    os_e    = np.full(n, np.nan)
    stage_s = [""] * n
    hist_s  = [""] * n
    grade_s = [""] * n
    t_s     = [""] * n
    n_s     = [""] * n
    m_s     = [""] * n
    resid_s = [""] * n

    # Build sample lookup
    # Expression IDs: TCGA-3X-AAV9-01
    # Clinical IDs:   TCGA-3X-AAV9-01
    # Patient IDs:    TCGA-3X-AAV9
    # Match on full sample ID first,
    # then on first 15 chars (patient+type)
    sid_lookup = {}
    for i, s in enumerate(sample_ids):
        sid_lookup[s.strip()] = i
        if len(s) >= 15:
            sid_lookup[s[:15]] = i
        if len(s) >= 12:
            sid_lookup[s[:12]] = i

    if not os.path.exists(clin_path):
        log(f"  Clinical file not found: "
            f"{clin_path}")
        return (os_t, os_e, stage_s,
                hist_s, grade_s,
                np.zeros(n, dtype=bool))

    log(f"\n  Parsing: {clin_path} "
        f"({os.path.getsize(clin_path):,}b)")

    opener = (
        gzip.open(clin_path,"rt",
            encoding="utf-8",errors="ignore")
        if clin_path.endswith(".gz")
        else open(clin_path,"r",
            encoding="utf-8",errors="ignore")
    )

    n_parsed = n_matched = n_os = 0
    with opener as f:
        for line_no, line in enumerate(f):
            parts = line.rstrip("\n").split("\t")
            # Skip header
            if line_no == 0:
                # Verify our expected columns
                def safe_hdr(i):
                    return parts[i].lower() \
                        if i < len(parts) else "?"
                log(f"  Header check:")
                log(f"    col[{COL_SAMPLE_ID}]"
                    f"={safe_hdr(COL_SAMPLE_ID)}")
                log(f"    col[{COL_DAYS_DEATH}]"
                    f"={safe_hdr(COL_DAYS_DEATH)}")
                log(f"    col[{COL_DAYS_FOLLOW}]"
                    f"={safe_hdr(COL_DAYS_FOLLOW)}")
                log(f"    col[{COL_VITAL}]"
                    f"={safe_hdr(COL_VITAL)}")
                log(f"    col[{COL_STAGE}]"
                    f"={safe_hdr(COL_STAGE)}")
                log(f"    col[{COL_HIST_TYPE}]"
                    f"={safe_hdr(COL_HIST_TYPE)}")
                continue

            n_parsed += 1
            if len(parts) <= COL_VITAL:
                continue

            sid = parts[COL_SAMPLE_ID].strip()
            idx = sid_lookup.get(sid)
            if idx is None and len(sid) >= 15:
                idx = sid_lookup.get(sid[:15])
            if idx is None and len(sid) >= 12:
                idx = sid_lookup.get(sid[:12])
            if idx is None:
                continue

            n_matched += 1

            # Vital status
            vs = parts[COL_VITAL].strip().upper()
            if vs == "DECEASED":
                os_e[idx] = 1
            elif vs == "LIVING":
                os_e[idx] = 0
            # else: leave NaN

            # OS time
            # DECEASED: use days_to_death
            # LIVING:   use days_to_last_followup
            if vs == "DECEASED":
                raw = parts[COL_DAYS_DEATH].strip() \
                    if COL_DAYS_DEATH < len(parts) \
                    else ""
                if raw:
                    try:
                        tv = float(raw) / 30.44
                        if tv > 0:
                            os_t[idx] = tv
                    except ValueError: pass
                # Fallback: if days_to_death empty,
                # use days_to_last_followup
                if np.isnan(os_t[idx]):
                    raw2 = (
                        parts[COL_DAYS_FOLLOW].strip()
                        if COL_DAYS_FOLLOW < len(parts)
                        else ""
                    )
                    if raw2:
                        try:
                            tv = float(raw2) / 30.44
                            if tv > 0:
                                os_t[idx] = tv
                        except ValueError: pass
            else:
                # LIVING or unknown:
                # use days_to_last_followup
                raw = (
                    parts[COL_DAYS_FOLLOW].strip()
                    if COL_DAYS_FOLLOW < len(parts)
                    else ""
                )
                if raw:
                    try:
                        tv = float(raw) / 30.44
                        if tv > 0:
                            os_t[idx] = tv
                    except ValueError: pass
                # If still NaN, try days_to_death
                if np.isnan(os_t[idx]):
                    raw2 = (
                        parts[COL_DAYS_DEATH].strip()
                        if COL_DAYS_DEATH < len(parts)
                        else ""
                    )
                    if raw2:
                        try:
                            tv = float(raw2) / 30.44
                            if tv > 0:
                                os_t[idx] = tv
                        except ValueError: pass

            # Stage
            if COL_STAGE < len(parts):
                stage_s[idx] = \
                    parts[COL_STAGE].strip()

            # Histological type
            if COL_HIST_TYPE < len(parts):
                hist_s[idx] = \
                    parts[COL_HIST_TYPE].strip()

            # Grade
            if COL_GRADE < len(parts):
                grade_s[idx] = \
                    parts[COL_GRADE].strip()

            # T/N/M
            if COL_T < len(parts):
                t_s[idx] = parts[COL_T].strip()
            if COL_N < len(parts):
                n_s[idx] = parts[COL_N].strip()
            if COL_M < len(parts):
                m_s[idx] = parts[COL_M].strip()
            if COL_RESIDUAL < len(parts):
                resid_s[idx] = \
                    parts[COL_RESIDUAL].strip()

            if (not np.isnan(os_t[idx])
                    and not np.isnan(os_e[idx])):
                n_os += 1

    valid = (
        np.isfinite(os_t)
        & np.isfinite(os_e)
        & (os_t > 0)
    )

    log(f"  Parsed: {n_parsed} rows")
    log(f"  Matched to expr: {n_matched}")
    log(f"  OS valid: {valid.sum()} "
        f"events={int(os_e[valid].sum())}")
    log(f"  Median OS: "
        f"{np.nanmedian(os_t[valid]):.1f}mo "
        f"(range "
        f"{os_t[valid].min():.1f}–"
        f"{os_t[valid].max():.1f}mo)")

    # Log histological types
    hist_counts = {}
    for h in hist_s:
        if h:
            hist_counts[h] = \
                hist_counts.get(h, 0) + 1
    log(f"\n  Histological types:")
    for h, c in sorted(
        hist_counts.items(),
        key=lambda x: -x[1],
    ):
        log(f"    {c:>3}x  {h}")

    # Log stages
    stg_counts = {}
    for s in stage_s:
        if s:
            stg_counts[s] = \
                stg_counts.get(s, 0) + 1
    log(f"\n  Pathologic stages:")
    for s, c in sorted(
        stg_counts.items(),
        key=lambda x: x[0],
    ):
        log(f"    {c:>3}x  {s}")

    return (os_t, os_e, stage_s,
            hist_s, grade_s, valid)

# ============================================================
# DEPTH SCORES — pre-subsetted expr
# ============================================================

def build_depth_scores(expr_sub, label):
    gc  = list(expr_sub.keys())
    sw  = [g for g in CHOL_SW  if g in gc]
    fat = [g for g in ICC_FA_T if g in gc]
    fas = [g for g in ICC_FA_S if g in gc]
    n   = len(next(iter(expr_sub.values())))

    def sub_score(sw_g, fa_g):
        d = np.zeros(n)
        nd = 0
        if sw_g:
            sm = np.column_stack([
                expr_sub[g] for g in sw_g
            ])
            d  += 1 - norm01(
                np.nanmean(sm, axis=1)
            )
            nd += 1
        if fa_g:
            fm = np.column_stack([
                expr_sub[g] for g in fa_g
            ])
            d  += norm01(
                np.nanmean(fm, axis=1)
            )
            nd += 1
        if nd: d /= nd
        return d

    depth_c = sub_score(sw, fat + fas)
    depth_t = sub_score(sw, fat)
    depth_s = sub_score([], fas)

    log(f"\n  Depth — {label} (n={n})")
    log(f"  Depth   {depth_c.mean():.4f} "
        f"±{depth_c.std():.4f}")
    log(f"  Depth_T {depth_t.mean():.4f} "
        f"±{depth_t.std():.4f}")
    log(f"  Depth_S {depth_s.mean():.4f} "
        f"±{depth_s.std():.4f}")
    rt, pt = safe_r(depth_t, depth_s)
    log(f"  r(T,S)={rt:+.4f} {fmt_p(pt)}")
    return depth_c, depth_t, depth_s

# ============================================================
# OS FUNCTIONS — all arrays pre-subsetted
# ============================================================

def depth_os_test(depth, os_t, os_e,
                  valid, label):
    log(f"\n  Depth OS — {label}")
    assert len(depth)==len(os_t)==len(valid)

    if valid.sum() < 8:
        log(f"  n={valid.sum()} — skip")
        return np.nan, np.nan, np.nan

    med  = np.nanmedian(depth[valid])
    hi   = valid & (depth >= med)
    lo   = valid & (depth <  med)
    p    = logrank_p(
        os_t[hi],os_e[hi],
        os_t[lo],os_e[lo],
    )
    m_hi = os_t[hi].mean() if hi.sum()>0 \
        else np.nan
    m_lo = os_t[lo].mean() if lo.sum()>0 \
        else np.nan
    log(f"  Median: hi={m_hi:.1f}mo "
        f"lo={m_lo:.1f}mo {fmt_p(p)}")

    t1   = np.nanpercentile(depth[valid],33)
    t2   = np.nanpercentile(depth[valid],67)
    hi3  = valid & (depth >= t2)
    lo3  = valid & (depth <= t1)
    p3   = logrank_p(
        os_t[hi3],os_e[hi3],
        os_t[lo3],os_e[lo3],
    )
    m3h  = os_t[hi3].mean() if hi3.sum()>0 \
        else np.nan
    m3l  = os_t[lo3].mean() if lo3.sum()>0 \
        else np.nan
    log(f"  Tertile T3={m3h:.1f}mo "
        f"T1={m3l:.1f}mo {fmt_p(p3)}")
    return p, m_hi, m_lo


def os_gene_screen(expr_sub, os_t, os_e,
                   valid, label):
    log(f"\n  OS Screen — {label}")
    n = len(os_t)
    assert all(len(v)==n
               for v in expr_sub.values())
    assert len(valid)==n

    if valid.sum() < 8:
        log(f"  n={valid.sum()} — skip")
        return {}

    log(f"  n={valid.sum()} "
        f"events={int(os_e[valid].sum())}")
    log(f"\n  {'Gene':<12} {'p_OS':>12}  "
        f"{'hi':>6}  {'lo':>6}  "
        f"{'gap':>6}  dir")
    log(f"  {'-'*56}")

    results = {}
    panel = [g for g in
             (CHOL_SW+ICC_FA_T+ICC_FA_S
              +ICC_DRIVERS)
             if g in expr_sub]

    for gene in panel:
        gv     = expr_sub[gene]
        valid2 = valid & np.isfinite(gv)
        if valid2.sum() < 8: continue
        med    = np.nanmedian(gv[valid2])
        hi     = valid2 & (gv >= med)
        lo     = valid2 & (gv <  med)
        p_os   = logrank_p(
            os_t[hi],os_e[hi],
            os_t[lo],os_e[lo],
        )
        m_hi   = os_t[hi].mean() \
            if hi.sum()>0 else np.nan
        m_lo   = os_t[lo].mean() \
            if lo.sum()>0 else np.nan
        gap    = m_lo - m_hi \
            if not (np.isnan(m_hi)
                    or np.isnan(m_lo)) \
            else np.nan
        d_s    = ("↑=worse"
                  if not np.isnan(m_hi)
                  and not np.isnan(m_lo)
                  and m_hi < m_lo
                  else "↑=better")
        if not np.isnan(p_os) and p_os < 0.10:
            log(f"  {gene:<12} {fmt_p(p_os)}  "
                f"{m_hi:>6.1f}  {m_lo:>6.1f}  "
                f"{gap:>+6.1f}  {d_s}")
        results[gene] = {
            "p":p_os,"m_hi":m_hi,
            "m_lo":m_lo,"gap":gap,
            "dir":d_s,"n":int(valid2.sum()),
        }
    return results


def cox_model(depth, os_t, os_e,
              valid, extra_sub, label):
    log(f"\n  Cox — {label}")
    vv = valid & np.isfinite(depth)
    for v in extra_sub.values():
        vv = vv & np.isfinite(v)
    if vv.sum() < 15:
        log(f"  n={vv.sum()} — insufficient")
        return {}
    df_d = {"T":os_t[vv],"E":os_e[vv],
            "depth":depth[vv]}
    for k,v in extra_sub.items():
        df_d[k] = v[vv]
    df  = pd.DataFrame(df_d)
    cph = CoxPHFitter()
    try:
        cph.fit(df,"T","E")
        log(f"  n={vv.sum()} "
            f"events={int(os_e[vv].sum())}")
        log(f"  {'Var':<12} {'HR':>8} "
            f"{'p':>12}")
        log(f"  {'-'*34}")
        res = {}
        for var in df_d:
            if var in ["T","E"]: continue
            row = cph.summary.loc[var]
            hr  = np.exp(row["coef"])
            p   = row["p"]
            log(f"  {var:<12} {hr:>8.3f} "
                f"{fmt_p(p)}")
            res[var] = {"HR":hr,"p":p}
        return res
    except Exception as ex:
        log(f"  Cox error: {ex}")
        return {}

# ============================================================
# STAGE ANALYSIS
# ============================================================

def stage_analysis(expr_sub, depth_c,
                   os_t, os_e, valid,
                   stage_s, label):
    log(f"\n  Stage Analysis — {label}")

    stage_map = {}
    for i,s in enumerate(stage_s):
        sl = s.lower()
        if "stage i" in sl \
                and "ii" not in sl \
                and "iv" not in sl:
            stage_map[i] = "I"
        elif "stage ii" in sl \
                and "iii" not in sl \
                and "iv" not in sl:
            stage_map[i] = "II"
        elif "stage iii" in sl \
                and "iv" not in sl:
            stage_map[i] = "III"
        elif "stage iv" in sl:
            stage_map[i] = "IV"

    for stg in ["I","II","III","IV"]:
        si = np.array([
            j for j,s in stage_map.items()
            if s == stg
        ])
        if len(si) == 0: continue
        vv = valid[si]
        dc = depth_c[si]
        log(f"  Stage {stg}: n={len(si)} "
            f"OS_valid={vv.sum()} "
            f"depth_mean={dc.mean():.4f}")
        if vv.sum() >= 5:
            med = np.nanmedian(dc[vv])
            hi  = vv & (dc >= med)
            lo  = vv & (dc <  med)
            p   = logrank_p(
                os_t[si[hi]],os_e[si[hi]],
                os_t[si[lo]],os_e[si[lo]],
            )
            m_h = os_t[si[hi]].mean() \
                if hi.sum()>0 else np.nan
            m_l = os_t[si[lo]].mean() \
                if lo.sum()>0 else np.nan
            log(f"    Depth OS: "
                f"hi={m_h:.1f}mo "
                f"lo={m_l:.1f}mo "
                f"{fmt_p(p)}")

# ============================================================
# SUBTYPE ANALYSIS: ICC vs non-ICC
# ============================================================

def icc_subtype_filter(hist_s, sample_ids):
    """
    Identify intrahepatic ICC samples.
    histological_type values:
      'Cholangiocarcinoma; intrahepatic' → ICC
      'Cholangiocarcinoma; distal'       → ECC
      'Cholangiocarcinoma; perihilar'    → PHC
    """
    log("\n  Subtype filter:")
    icc_idx  = []
    ecc_idx  = []
    phc_idx  = []
    other_idx = []
    for i, h in enumerate(hist_s):
        hl = h.lower()
        if "intrahepatic" in hl:
            icc_idx.append(i)
        elif "distal" in hl:
            ecc_idx.append(i)
        elif "perihilar" in hl \
                or "hilar" in hl:
            phc_idx.append(i)
        elif h:
            other_idx.append(i)

    log(f"  Intrahepatic ICC: {len(icc_idx)}")
    log(f"  Distal ECC:       {len(ecc_idx)}")
    log(f"  Perihilar PHC:    {len(phc_idx)}")
    log(f"  Other/unknown:    {len(other_idx)}")
    log(f"  Total tumour:     "
        f"{len(icc_idx)+len(ecc_idx)+len(phc_idx)+len(other_idx)}")

    return np.array(icc_idx)

# ============================================================
# NMF ANALYSIS (GSE32225)
# ============================================================

def nmf_depth_analysis(gse_data, dc, dt, ds):
    log("\n" + "=" * 65)
    log("S1-P5: NMF SUBTYPE DEPTH")
    log("=" * 65)
    labels  = gse_data["nmf_labels"]
    icc_i   = np.where(gse_data["icc_mask"])[0]
    classes = sorted(set(l for l in labels if l))
    log(f"  Classes: {classes}")
    log(f"\n  {'Class':<22} {'n':>5} "
        f"{'Depth':>8} {'D_T':>8} "
        f"{'D_S':>8}")
    log(f"  {'-'*52}")
    cd = {}
    for c in classes:
        cm = np.array([
            labels[icc_i[j]] == c
            for j in range(len(icc_i))
        ])
        ci = np.where(cm)[0]
        if len(ci) == 0: continue
        log(f"  {c:<22} {len(ci):>5} "
            f"{np.nanmean(dc[ci]):>8.4f} "
            f"{np.nanmean(dt[ci]):>8.4f} "
            f"{np.nanmean(ds[ci]):>8.4f}")
        cd[c] = {"depth_c":dc[ci],
                 "depth_t":dt[ci],
                 "depth_s":ds[ci],
                 "n":len(ci)}
    pk = next((k for k in cd
               if "prolif" in k.lower()), None)
    ik = next((k for k in cd
               if "inflam" in k.lower()), None)
    p5_pv = np.nan
    if pk and ik:
        _,p5_pv = stats.mannwhitneyu(
            cd[pk]["depth_c"],
            cd[ik]["depth_c"],
            alternative="greater",
        )
        log(f"\n  MW Prolif>Inflam: {fmt_p(p5_pv)}")
        log(f"  S1-P5: "
            f"{'CONFIRMED ✓' if p5_pv<0.05 else 'DIRECTIONAL' if p5_pv<0.10 else 'NOT CONFIRMED ✗'}")
    return cd, p5_pv

# ============================================================
# LOAD GSE32225
# ============================================================

def load_gse32225():
    matrix_path = None
    for c in [
        os.path.join(GEO_DIR,
                     "GSE32225_matrix.txt.gz"),
        os.path.join(DATA_DIR,
                     "GSE32225_matrix.txt.gz"),
    ]:
        if os.path.exists(c) \
                and os.path.getsize(c) > 100000:
            matrix_path = c
            break
    if matrix_path is None:
        url = (
            "https://ftp.ncbi.nlm.nih.gov"
            "/geo/series/GSE32nnn/GSE32225"
            "/matrix/GSE32225_series_matrix.txt.gz"
        )
        dest = os.path.join(
            GEO_DIR, "GSE32225_matrix.txt.gz"
        )
        matrix_path = try_get(url, dest, 100000)
    if matrix_path is None:
        return None

    soft_path = None
    for c in [
        os.path.join(DATA_DIR, "GPL8432.soft.gz"),
    ]:
        if os.path.exists(c) \
                and os.path.getsize(c) > 10000:
            soft_path = c
            break
    if soft_path is None:
        url = (
            "https://ftp.ncbi.nlm.nih.gov"
            "/geo/platforms/GPL8nnn/GPL8432"
            "/soft/GPL8432_family.soft.gz"
        )
        soft_path = try_get(
            url,
            os.path.join(DATA_DIR,
                         "GPL8432.soft.gz"),
            10000,
        )

    # Probe map
    p2g = {}
    if soft_path and os.path.exists(soft_path):
        gw = set(ALL_PANEL)
        in_d = False; hdr = None
        id_c = sym_c = None
        opener = (
            gzip.open(soft_path,"rt",
                encoding="utf-8",errors="ignore")
            if soft_path.endswith(".gz")
            else open(soft_path,"r",
                encoding="utf-8",errors="ignore")
        )
        with opener as f:
            for line in f:
                line = line.rstrip("\n")
                if "!platform_table_begin" \
                        in line.lower():
                    in_d=True; hdr=None; continue
                if "!platform_table_end" \
                        in line.lower():
                    break
                if not in_d: continue
                parts = line.split("\t")
                if hdr is None:
                    hdr=[p.lower().strip()
                         for p in parts]
                    for i,h in enumerate(hdr):
                        if h=="id" and id_c is None:
                            id_c=i
                        if any(x in h for x in [
                            "symbol","gene_symbol"
                        ]) and sym_c is None:
                            sym_c=i
                    continue
                if id_c is None \
                        or sym_c is None: continue
                if max(id_c,sym_c)>=len(parts):
                    continue
                pid=parts[id_c].strip()
                sym=(parts[sym_c].strip()
                     .split("///")[0]
                     .split(";")[0].strip())
                if pid and sym \
                        and sym!="NA" \
                        and sym in gw:
                    p2g[pid]=sym

    # Matrix
    gsm_ids=[]; char_block={}; expr_data={}
    in_table=tbl_hdr=False; n_samples=0
    opener=(
        gzip.open(matrix_path,"rt",
            encoding="utf-8",errors="ignore")
        if matrix_path.endswith(".gz")
        else open(matrix_path,"r",
            encoding="utf-8",errors="ignore")
    )
    with opener as f:
        for raw in f:
            line=raw.rstrip("\n")
            if line.startswith(
                "!Sample_geo_accession"
            ):
                parts=line.split("\t")
                gsm_ids=[p.strip().strip('"')
                          for p in parts[1:]]
                n_samples=len(gsm_ids); continue
            if line.startswith(
                "!Sample_characteristics_ch1"
            ):
                parts=line.split("\t")
                key=parts[0]
                vals=[p.strip().strip('"')
                      for p in parts[1:]]
                if key not in char_block:
                    char_block[key]=[]
                char_block[key].append(vals)
                continue
            if "series_matrix_table_begin" in line:
                in_table=True; tbl_hdr=False; continue
            if "series_matrix_table_end" in line:
                break
            if not in_table: continue
            if not tbl_hdr: tbl_hdr=True; continue
            parts=line.split("\t")
            pid=parts[0].strip().strip('"')
            gene=p2g.get(pid)
            if gene is None: continue
            try:
                vals=np.array([
                    float(p.strip())
                    if p.strip() not in
                    ["","NA","nan","NaN"]
                    else np.nan
                    for p in parts[1:n_samples+1]
                ])
                if gene not in expr_data:
                    expr_data[gene]=(pid,vals)
                else:
                    if np.nanvar(vals)>np.nanvar(
                        expr_data[gene][1]
                    ):
                        expr_data[gene]=(pid,vals)
            except (ValueError,TypeError):
                continue

    expr={g:v for g,(_,v) in expr_data.items()}
    nmf_labels=[""]*n_samples
    icc_mask=np.ones(n_samples,dtype=bool)
    nor_mask=np.zeros(n_samples,dtype=bool)
    for key,val_lists in char_block.items():
        for val_row in val_lists:
            for i,v in enumerate(val_row):
                if i>=n_samples: break
                if ":" in v:
                    k,_,vv=v.partition(":")
                    kl=k.strip().lower()
                    vv=vv.strip()
                    if "nmf" in kl:
                        nmf_labels[i]=vv
                    if "cell type" in kl \
                            and "normal" \
                            in vv.lower():
                        icc_mask[i]=False
                        nor_mask[i]=True
                else:
                    if "normal biliary" in v.lower():
                        icc_mask[i]=False
                        nor_mask[i]=True
    log(f"  GSE32225: {n_samples} samples "
        f"ICC={icc_mask.sum()} "
        f"Normal={nor_mask.sum()} "
        f"genes={len(expr)}")
    return {
        "gsm_ids":gsm_ids,"expr":expr,
        "nmf_labels":nmf_labels,
        "icc_mask":icc_mask,
        "nor_mask":nor_mask,
        "n_samples":n_samples,
    }

# ============================================================
# FIGURE
# ============================================================

def generate_figure(
    expr_t, valid, os_t, os_e,
    dc, dt, ds, os_res,
    gse_data, gse_dc, gse_dt, gse_ds,
    gse_nmf, stage_s, icc_only_idx,
):
    log("\n--- Generating figure ---")
    fig = plt.figure(figsize=(26,22))
    fig.suptitle(
        "ICC False Attractor — Script 1 v3 | "
        "TCGA-CHOL + GSE32225 | "
        "OrganismCore | Doc 93c | 2026-03-02",
        fontsize=10,fontweight="bold",y=0.99,
    )
    gs_f=gridspec.GridSpec(
        4,4,figure=fig,hspace=0.65,wspace=0.45,
    )
    C=["#27ae60","#e74c3c","#2980b9",
       "#8e44ad","#e67e22","#16a085"]
    kmf=KaplanMeierFitter()

    def km_ax(ax,t_hi,e_hi,t_lo,e_lo,
              l_hi,l_lo,title):
        m1=(np.isfinite(t_hi)&np.isfinite(e_hi)
            &(t_hi>0))
        m0=(np.isfinite(t_lo)&np.isfinite(e_lo)
            &(t_lo>0))
        if m1.sum()<3 or m0.sum()<3:
            ax.set_title(title+"\n(n<3)",
                         fontsize=8); return
        kmf.fit(t_hi[m1],e_hi[m1],label=l_hi)
        kmf.plot_survival_function(
            ax=ax,color=C[1],ci_show=False)
        kmf.fit(t_lo[m0],e_lo[m0],label=l_lo)
        kmf.plot_survival_function(
            ax=ax,color=C[0],ci_show=False)
        p=logrank_p(t_hi[m1],e_hi[m1],
                    t_lo[m0],e_lo[m0])
        ax.set_title(f"{title}\n{fmt_p(p)}",
                     fontsize=8)
        ax.set_xlabel("Months",fontsize=7)
        ax.legend(fontsize=5)
        ax.set_ylim(-0.05,1.05)

    # A: Depth OS all tumours
    ax_a=fig.add_subplot(gs_f[0,0])
    if valid.sum()>=8:
        med=np.nanmedian(dc[valid])
        hi=valid&(dc>=med); lo=valid&(dc<med)
        km_ax(ax_a,os_t[hi],os_e[hi],
              os_t[lo],os_e[lo],
              f"Deep ({os_t[hi].mean():.0f}mo)",
              f"Shallow ({os_t[lo].mean():.0f}mo)",
              "A — Depth OS all (P1)")
    else:
        ax_a.text(0.5,0.5,"OS pending",
                  ha="center",va="center",
                  transform=ax_a.transAxes)
        ax_a.set_title("A — Depth OS",fontsize=8)

    # B: Depth OS ICC only
    ax_b=fig.add_subplot(gs_f[0,1])
    if len(icc_only_idx)>0:
        icc_v=valid[icc_only_idx]
        icc_dc=dc[icc_only_idx]
        icc_t=os_t[icc_only_idx]
        icc_e=os_e[icc_only_idx]
        if icc_v.sum()>=5:
            med=np.nanmedian(icc_dc[icc_v])
            hi=icc_v&(icc_dc>=med)
            lo=icc_v&(icc_dc<med)
            km_ax(ax_b,icc_t[hi],icc_e[hi],
                  icc_t[lo],icc_e[lo],
                  f"Deep ({icc_t[hi].mean():.0f}mo)",
                  f"Shallow ({icc_t[lo].mean():.0f}mo)",
                  "B — Depth OS ICC only")
        else:
            ax_b.set_title("B — ICC only\n(n<5)",
                           fontsize=8)
    else:
        ax_b.set_title("B — ICC only\n(no data)",
                       fontsize=8)

    # C-D: Top 2 OS genes
    top_g=sorted(
        [(g,r) for g,r in (os_res or {}).items()
         if not np.isnan(r["p"])],
        key=lambda x: x[1]["p"],
    )[:2]
    for idx,(gene,r) in enumerate(top_g):
        ax=fig.add_subplot(gs_f[0,2+idx])
        gv=expr_t.get(gene)
        if gv is None: continue
        vv2=valid&np.isfinite(gv)
        if vv2.sum()<5: continue
        med=np.nanmedian(gv[vv2])
        hi=vv2&(gv>=med); lo=vv2&(gv<med)
        km_ax(ax,os_t[hi],os_e[hi],
              os_t[lo],os_e[lo],
              f"{gene}-hi ({os_t[hi].mean():.0f}mo)",
              f"{gene}-lo ({os_t[lo].mean():.0f}mo)",
              f"{'CD'[idx]} — {gene} OS")

    # E: Depth_T vs Depth_S scatter GSE
    ax_e=fig.add_subplot(gs_f[1,0])
    if len(gse_dt)>5 and len(gse_ds)>5:
        ax_e.scatter(gse_dt,gse_ds,
                     alpha=0.4,s=12,c=C[2])
        r,_=safe_r(gse_dt,gse_ds)
        ax_e.set_xlabel("Depth_T",fontsize=7)
        ax_e.set_ylabel("Depth_S",fontsize=7)
        ax_e.set_title(
            f"E — Depth_T vs Depth_S (GSE)\n"
            f"r={r:+.3f} (P7)",fontsize=8)

    # F: NMF boxplot
    ax_f=fig.add_subplot(gs_f[1,1])
    if gse_nmf and len(gse_nmf)>=2:
        cls=list(gse_nmf.keys())
        ax_f.boxplot(
            [gse_nmf[c]["depth_c"] for c in cls],
            labels=cls,
        )
        ax_f.set_ylabel("Depth",fontsize=7)
        ax_f.set_title("F — NMF Depth (P5)",
                       fontsize=8)
        ax_f.tick_params(axis="x",labelsize=7)

    # G: OS gene bar
    ax_g=fig.add_subplot(gs_f[1,2:])
    top_os=sorted(
        [(g,r) for g,r in (os_res or {}).items()
         if not np.isnan(r.get("p",np.nan))],
        key=lambda x: x[1]["p"],
    )[:14]
    if top_os:
        gl=[f"{g}\n({r['m_hi']:.0f}/"
            f"{r['m_lo']:.0f}mo)"
            for g,r in top_os]
        pv=[-np.log10(max(r["p"],1e-10))
            for _,r in top_os]
        co=[C[1] if r.get("dir")=="↑=worse"
            else C[0] for _,r in top_os]
        ax_g.barh(range(len(gl)),pv,
                  color=co,alpha=0.8)
        ax_g.axvline(-np.log10(0.05),
                     color="black",ls="--",lw=1)
        ax_g.set_yticks(range(len(gl)))
        ax_g.set_yticklabels(gl,fontsize=6)
        ax_g.set_xlabel("-log10(p)",fontsize=7)
        ax_g.set_title(
            "G — OS Gene Panel TCGA-CHOL "
            "(red=worse, green=better)",
            fontsize=8)
    else:
        ax_g.text(0.5,0.5,"OS screen pending",
                  ha="center",va="center",
                  transform=ax_g.transAxes)

    # H: Depth histograms comparison
    ax_h=fig.add_subplot(gs_f[2,0])
    for dep,col,lbl in [
        (dc,C[2],"TCGA-CHOL"),
        (gse_dc,C[3],"GSE32225"),
    ]:
        if dep is not None and len(dep)>3:
            ax_h.hist(dep[np.isfinite(dep)],
                      bins=20,alpha=0.5,
                      color=col,label=lbl,
                      edgecolor="white")
    ax_h.set_xlabel("Depth",fontsize=7)
    ax_h.set_title("H — Depth Distributions",
                   fontsize=8)
    ax_h.legend(fontsize=6)

    # I-K: FGFR2, HDAC2, KRAS OS
    for idx,(gene,ttl) in enumerate([
        ("FGFR2","I — FGFR2 OS (P6)"),
        ("HDAC2","J — HDAC2 OS (P4)"),
        ("KRAS", "K — KRAS OS"),
    ]):
        ax=fig.add_subplot(gs_f[2,idx+1])
        if valid.sum()<8:
            ax.set_title(ttl+"\n(OS pending)",
                         fontsize=8); continue
        gv=expr_t.get(gene)
        if gv is None:
            ax.set_title(ttl+"\n(absent)",
                         fontsize=8); continue
        vv2=valid&np.isfinite(gv)
        if vv2.sum()<5: continue
        med=np.nanmedian(gv[vv2])
        hi=vv2&(gv>=med); lo=vv2&(gv<med)
        km_ax(ax,os_t[hi],os_e[hi],
              os_t[lo],os_e[lo],
              f"{gene}-hi ({os_t[hi].mean():.0f}mo)",
              f"{gene}-lo ({os_t[lo].mean():.0f}mo)",
              ttl)

    # L: Summary panel
    ax_l=fig.add_subplot(gs_f[3,:])
    ax_l.axis("off")
    n_os=int(valid.sum())
    n_ev=int(os_e[valid].sum()) if n_os>0 else 0
    ax_l.text(
        0.01,0.85,
        "L — SCRIPT 1 v3 SUMMARY\n"
        "══════════════════════════════"
        "══════════════\n"
        f"TCGA-CHOL: n_tumour=36  "
        f"OS valid={n_os}  events={n_ev}  "
        f"(days_to_death/last_followup col 28/30)\n"
        f"GSE32225: n_ICC=149  "
        f"NMF={sorted(set(gse_data['nmf_labels'])) if gse_data else 'N/A'}\n"
        "OrganismCore | ICC | Doc 93c | 2026-03-02",
        transform=ax_l.transAxes,
        fontsize=8,va="top",
        fontfamily="monospace",
        bbox=dict(boxstyle="round",
                  facecolor="#f8f8f8",
                  edgecolor="#cccccc"),
    )

    out=os.path.join(RESULTS_DIR,"icc_s1v3.png")
    plt.savefig(out,dpi=150,bbox_inches="tight")
    log(f"  Figure: {out}")
    plt.close()

# ============================================================
# SCORECARD
# ============================================================

def scorecard(results):
    log("\n"+"="*65)
    log("PREDICTION SCORECARD — SCRIPT 1 v3")
    log("="*65)
    log(f"\n  {'ID':<8} {'Prediction':<42} Status")
    log(f"  {'-'*72}")
    for pid,pred,status in results:
        log(f"  {pid:<8} {pred:<42} {status}")

# ============================================================
# MAIN
# ============================================================

def main():
    log("="*65)
    log("ICC FALSE ATTRACTOR — SCRIPT 1 v3")
    log("CLINICAL PARSING FIXED")
    log("Framework: OrganismCore")
    log("Doc: 93c | Date: 2026-03-02")
    log("="*65)
    log("")
    log("CLINICAL FIX:")
    log("  col[0]  sampleID")
    log("  col[28] days_to_death (DECEASED)")
    log("  col[30] days_to_last_followup (LIVING)")
    log("  col[92] vital_status")
    log("  col[67] pathologic_stage")
    log("  col[44] histological_type")
    log("  Both time cols in DAYS → /30.44")

    # ── TCGA-CHOL expression ─────────────
    log("\n"+"="*65)
    log("TRACK A: TCGA-CHOL")
    log("="*65)
    tcga_expr, tcga_sids = load_tcga_expr()
    n_all = len(tcga_sids)
    tumour = np.array([
        ("-01" in s
         or (len(s)>=15 and s[13:15]=="01"))
        for s in tcga_sids
    ])
    normal = np.array([
        ("-11" in s
         or (len(s)>=15 and s[13:15]=="11"))
        for s in tcga_sids
    ])
    ti = np.where(tumour)[0]
    log(f"  n_all={n_all} "
        f"tumour={tumour.sum()} "
        f"normal={normal.sum()}")

    # Subset expression to tumour
    expr_t = {g: v[ti]
              for g,v in tcga_expr.items()}

    # ── OS — hardcoded columns ────────────
    (os_t_all, os_e_all, stage_all,
     hist_all, grade_all,
     valid_all) = load_tcga_os_hardcoded(
        tcga_sids
    )

    # Subset to tumour
    os_t   = os_t_all[ti]
    os_e   = os_e_all[ti]
    stage_t= [stage_all[i] for i in ti]
    hist_t = [hist_all[i]  for i in ti]
    grade_t= [grade_all[i] for i in ti]
    valid  = valid_all[ti]
    log(f"\n  Tumour OS: valid={valid.sum()} "
        f"events={int(os_e[valid].sum())}")

    # Identify ICC-only within tumour subset
    icc_only_idx = icc_subtype_filter(
        hist_t,
        [tcga_sids[i] for i in ti],
    )

    # ── Depth scores ──────────────────────
    depth_c,depth_t,depth_s = \
        build_depth_scores(expr_t,"TCGA-CHOL")

    # ── P1: Depth OS ──────────────────────
    log("\n"+"="*65)
    log("S1-P1: DEPTH OS — all tumours")
    log("="*65)
    p1,m1h,m1l = depth_os_test(
        depth_c,os_t,os_e,valid,"TCGA-CHOL all"
    )
    s1p1=(
        "CONFIRMED ✓"
        if not np.isnan(p1) and p1<0.05
        and not np.isnan(m1h) and m1h<m1l
        else "DIRECTIONAL"
        if not np.isnan(p1) and p1<0.10
        and not np.isnan(m1h) and m1h<m1l
        else "NOT CONFIRMED ✗"
        if not np.isnan(p1)
        else "NOT TESTABLE (OS=0)"
    )
    log(f"  S1-P1 STATUS: {s1p1}")

    # ICC-only depth OS
    if len(icc_only_idx) >= 5:
        log("\n  Depth OS — ICC intrahepatic only:")
        p1b,m1bh,m1bl = depth_os_test(
            depth_c[icc_only_idx],
            os_t[icc_only_idx],
            os_e[icc_only_idx],
            valid[icc_only_idx],
            "TCGA-CHOL ICC-only",
        )
        log(f"  S1-P1 ICC-only: "
            f"{'CONFIRMED ✓' if not np.isnan(p1b) and p1b<0.05 and m1bh<m1bl else 'DIRECTIONAL' if not np.isnan(p1b) and p1b<0.10 else 'NOT CONFIRMED ✗'}")

    # ── OS gene screen ────────────────────
    log("\n"+"="*65)
    log("S1-2: OS GENE SCREEN — TCGA-CHOL")
    log("="*65)
    tcga_os_res = os_gene_screen(
        expr_t,os_t,os_e,valid,"TCGA-CHOL"
    )

    def get_status(gene, expected="worse"):
        r=tcga_os_res.get(gene,{})
        p=r.get("p",np.nan)
        d=r.get("dir","")
        if np.isnan(p): return "NOT TESTABLE"
        if expected=="worse":
            if p<0.05 and d=="↑=worse":
                return "CONFIRMED ✓"
            elif p<0.10 and d=="↑=worse":
                return "DIRECTIONAL"
            elif p<0.05: return "REVERSED ✗"
            else: return "NOT CONFIRMED ✗"
        else:
            if p<0.05 and d=="↑=better":
                return "CONFIRMED ✓"
            elif p<0.10 and d=="↑=better":
                return "DIRECTIONAL"
            elif p<0.05: return "REVERSED ✗"
            else: return "NOT CONFIRMED ✗"

    s1p2=get_status("TWIST1","worse")
    s1p3=get_status("FAP","worse")
    s1p4=get_status("HDAC2","worse")
    s1p6=get_status("FGFR2","better")
    log(f"\n  S1-P2 TWIST1: {s1p2}")
    log(f"  S1-P3 FAP:    {s1p3}")
    log(f"  S1-P4 HDAC2:  {s1p4}")
    log(f"  S1-P6 FGFR2:  {s1p6}")

    # ── Stage analysis ────────────────────
    log("\n"+"="*65)
    log("STAGE ANALYSIS")
    log("="*65)
    stage_analysis(
        expr_t,depth_c,os_t,os_e,
        valid,stage_t,"TCGA-CHOL"
    )

    # ── Cox ──────────────────────────────
    log("\n"+"="*65)
    log("COX — TCGA-CHOL")
    log("="*65)
    extra={g:expr_t[g] for g in [
        "TWIST1","FAP","HDAC2",
        "FGFR2","EZH2","CDC20","KRAS",
    ] if g in expr_t}
    cox_res=cox_model(
        depth_c,os_t,os_e,valid,extra,
        "depth+panel"
    )

    # ── GSE32225 ──────────────────────────
    log("\n"+"="*65)
    log("TRACK B: GSE32225")
    log("="*65)
    gse_data=load_gse32225()
    gse_dc=gse_dt=gse_ds=np.array([])
    gse_nmf={}
    s1p5=s1p7="NOT TESTABLE"

    if gse_data and len(gse_data["expr"])>0:
        icc_i=np.where(gse_data["icc_mask"])[0]
        expr_gse={g:v[icc_i]
                  for g,v
                  in gse_data["expr"].items()}
        gse_dc,gse_dt,gse_ds=\
            build_depth_scores(
                expr_gse,"GSE32225"
            )

        nmf_res=nmf_depth_analysis(
            gse_data,gse_dc,gse_dt,gse_ds
        )
        if nmf_res and len(nmf_res)==2:
            gse_nmf,p5_pv=nmf_res
            s1p5=(
                "CONFIRMED ✓"
                if not np.isnan(p5_pv) and p5_pv<0.05
                else "DIRECTIONAL"
                if not np.isnan(p5_pv) and p5_pv<0.10
                else "NOT CONFIRMED ✗"
            )
        else:
            gse_nmf={}; s1p5="NOT TESTABLE"

        # P7
        log("\n"+"="*65)
        log("S1-P7: r(Depth_T, Depth_S)<0.70")
        log("="*65)
        r7_t,_=safe_r(depth_t,depth_s)
        r7_g,_=safe_r(gse_dt,gse_ds)
        log(f"  TCGA-CHOL: r={r7_t:+.4f} "
            f"{'<0.70 ✓' if not np.isnan(r7_t) and r7_t<0.70 else '≥0.70 ✗'}")
        log(f"  GSE32225:  r={r7_g:+.4f} "
            f"{'<0.70 ✓' if not np.isnan(r7_g) and r7_g<0.70 else '≥0.70 ✗'}")
        s1p7=(
            "CONFIRMED ✓"
            if (not np.isnan(r7_t) and r7_t<0.70)
            or (not np.isnan(r7_g) and r7_g<0.70)
            else "NOT CONFIRMED ✗"
        )

    # ── Scorecard ─────────────────────────
    scorecard([
        ("S1-P1","Depth worse OS TCGA-CHOL",s1p1),
        ("S1-P2","TWIST1-hi worse OS",s1p2),
        ("S1-P3","FAP-hi worse OS",s1p3),
        ("S1-P4","HDAC2-hi worse OS",s1p4),
        ("S1-P5","Prolif NMF depth > Inflam",s1p5),
        ("S1-P6","FGFR2-hi better OS",s1p6),
        ("S1-P7","r(Depth_T,Depth_S)<0.70",s1p7),
    ])

    # ── Figure ────────────────────────────
    generate_figure(
        expr_t,valid,os_t,os_e,
        depth_c,depth_t,depth_s,
        tcga_os_res,gse_data,
        gse_dc,gse_dt,gse_ds,
        gse_nmf,stage_t,icc_only_idx,
    )

    # ── Save CSV ──────────────────────────
    rows=[]
    for j,sid in enumerate(
        [tcga_sids[i] for i in ti]
    ):
        rows.append({
            "sample_id":   sid,
            "hist_type":   hist_t[j],
            "stage":       stage_t[j],
            "grade":       grade_t[j],
            "depth":       float(depth_c[j]),
            "depth_T":     float(depth_t[j]),
            "depth_S":     float(depth_s[j]),
            "os_time_mo":  float(os_t[j]),
            "os_event":    float(os_e[j]),
        })
    out_csv=os.path.join(
        RESULTS_DIR,"tcga_chol_s1v3.csv"
    )
    pd.DataFrame(rows).to_csv(
        out_csv,index=False
    )
    log(f"\n  CSV: {out_csv}")
    write_log()
    log(f"  Log: {LOG_FILE}")
    log("\n=== SCRIPT 1 v3 COMPLETE ===")
    log("Paste full output for Doc 93c.")


if __name__ == "__main__":
    main()
