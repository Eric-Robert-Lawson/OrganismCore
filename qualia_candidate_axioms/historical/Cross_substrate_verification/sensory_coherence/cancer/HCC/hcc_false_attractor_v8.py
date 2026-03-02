"""
HEPATOCELLULAR CARCINOMA — FALSE ATTRACTOR ANALYSIS
SCRIPT 8
Dataset: TCGA-LIHC (continued)
         GSE14520 (GEO download attempt)
Purpose: HDAC2 Stage III joint model,
         CDC20 + stage + HDAC2 Cox,
         PRF1 + HDAC2 interaction,
         HCC-P5 if MAF present,
         GSE14520 CDK4 via GEO download,
         final pre-literature summary

Doc: 92h | Date: 2026-03-02

PREDICTIONS LOCKED 2026-03-02:
  S8-P1: CTNNB1-mut better OS (if MAF)
  S8-P2: TP53-mut worse OS (if MAF)
  S8-P3: HDAC2-hi + CDK4-hi Stage III
         worst OS subgroup (< 13.7mo)
  S8-P4: HDAC2-hi + PRF1-lo Stage III
         worst immune subtype
  S8-P5: CDC20 + stage + HDAC2 model
         outperforms stage alone
  S8-P6: CDK4-hi worse OS GSE14520
  S8-P7: HDAC2-hi Stage III Cox HR >
         CDK4 within Stage III

Author: Eric Robert Lawson
Framework: OrganismCore
"""

import os
import re
import gzip
import io
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

BASE_DIR    = "./hcc_false_attractor/"
TCGA_DIR    = os.path.join(BASE_DIR, "tcga_lihc/")
GSE_DIR     = os.path.join(BASE_DIR, "gse14520/")
RESULTS_DIR = os.path.join(BASE_DIR, "results_s8")
LOG_FILE    = os.path.join(RESULTS_DIR,
                           "analysis_log_s8.txt")
os.makedirs(TCGA_DIR,    exist_ok=True)
os.makedirs(GSE_DIR,     exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

EXPR_FILE  = os.path.join(
    TCGA_DIR, "TCGA-LIHC.expr.tsv.gz")
SURV_FILE  = os.path.join(
    TCGA_DIR, "TCGA-LIHC.survival.tsv.gz")
PHENO_FILE = os.path.join(
    TCGA_DIR, "TCGA-LIHC.pheno.tsv.gz")
MAF_FILE   = os.path.join(
    TCGA_DIR, "TCGA-LIHC.maf.gz")

# GSE14520 paths
GSE_MATRIX_FILE = os.path.join(
    GSE_DIR, "GSE14520_series_matrix.txt.gz")
GSE_SCORE_FILE  = os.path.join(
    BASE_DIR, "results_s2",
    "depth_scores_s2.csv")

# GEO download URL for GSE14520
# (series matrix — contains expression
#  values and clinical annotations)
GSE14520_MATRIX_URL = (
    "https://ftp.ncbi.nlm.nih.gov/geo/series"
    "/GSE14nnn/GSE14520/matrix/"
    "GSE14520_series_matrix.txt.gz"
)
GSE14520_MATRIX_URL_ALT = (
    "https://www.ncbi.nlm.nih.gov/geo/query"
    "/acc.cgi?acc=GSE14520"
    "&targ=self&form=text&view=full"
)

# CDK4 Affymetrix probes (GPL3921 / HG-U133A)
CDK4_PROBES = [
    "204541_at",
    "204542_s_at",
    "1592_at",
]

# ============================================================
# GENE LISTS
# ============================================================

METAB_SWITCH = [
    "CYP3A4","ALDOB","PCK1","G6PC",
    "CYP2C9","TTR","IGF1","ARG1",
    "APOE","RXRA","PPARA","FGF21",
    "FABP1","ALB","APOB","HNF4A",
]
PROG_FA = [
    "SOX4","PROM1","AFP","EPCAM",
    "CDC20","BIRC5","TOP2A","MKI67",
    "CCNB1","KRT19","EZH2","HDAC2",
]
MUT_GENES = [
    "CTNNB1","TP53","ARID1A","AXIN1",
    "NFE2L2","RB1","PIK3CA","PTEN",
    "TSC1","TSC2","ARID2","RNF43",
    "KMT2D","SETD2","HNF1A","TERT",
    "BAP1","CDKN2A","ALB","IDH1",
    "IDH2","SMARCA4","ELF3","MET",
    "KEAP1","ACVR2A","RPL22",
]
EXHAUSTION_GENES = [
    "PDCD1","HAVCR2","LAG3",
    "TIGIT","CTLA4","CD8A",
]
EXTRA_GENES = [
    "CDK4","SMARCA4","TWIST1","TGFB1",
    "FGFR1","DNMT3A","VIM","CDH1",
    "CTNNB1","GLUL","GPC3","MYC",
    "SMAD3","ZEB1","ZEB2","SNAI1",
    "CD274","PDCD1","HAVCR2","LAG3",
    "TIGIT","CTLA4","CD8A","CD4",
    "FOXP3","GZMB","PRF1","IFNG",
    "CD68","CD247","CD44","CDKN2A",
    "PTEN","IDH2","CDH1","CDC20",
    "BIRC5","CCNB1","APOB","HDAC3",
]
AGE_COLS = {
    "age",
    "age_at_initial_pathologic_diagnosis",
    "age_at_diagnosis","age_at_index",
    "age_at_procurement","patient_age",
    "age_diag",
}

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
    if p < 0.001:  return f"p={p:.2e} ***"
    elif p < 0.01: return f"p={p:.2e}  **"
    elif p < 0.05: return f"p={p:.4f}   *"
    else:          return f"p={p:.4f}  ns"

def safe_pearsonr(x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    m = np.isfinite(x) & np.isfinite(y)
    if m.sum() < 5:
        return np.nan, np.nan
    return stats.pearsonr(x[m], y[m])

def safe_mwu(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    a = a[np.isfinite(a)]
    b = b[np.isfinite(b)]
    if len(a) < 2 or len(b) < 2:
        return np.nan, np.nan
    return stats.mannwhitneyu(
        a, b, alternative="two-sided"
    )

def norm01(arr):
    arr = np.asarray(arr, dtype=float)
    mn, mx = np.nanmin(arr), np.nanmax(arr)
    if mx > mn:
        return (arr - mn) / (mx - mn)
    return np.full_like(arr, 0.5)

def logrank_p(t1, e1, t0, e0):
    t1 = np.asarray(t1, dtype=float)
    e1 = np.asarray(e1, dtype=float)
    t0 = np.asarray(t0, dtype=float)
    e0 = np.asarray(e0, dtype=float)
    m1 = (np.isfinite(t1) & np.isfinite(e1)
          & (t1 > 0))
    m0 = (np.isfinite(t0) & np.isfinite(e0)
          & (t0 > 0))
    if m1.sum() < 5 or m0.sum() < 5:
        return np.nan
    try:
        return logrank_test(
            t1[m1], t0[m0],
            e1[m1], e0[m0],
        ).p_value
    except Exception:
        return np.nan

def safe_km(kmf, t, e, label):
    t = np.asarray(t, dtype=float)
    e = np.asarray(e, dtype=float)
    v = (np.isfinite(t) & np.isfinite(e)
         & (t > 0))
    if v.sum() < 5:
        return False
    kmf.fit(t[v], e[v], label=label)
    return True

def run_cox(df_c, label, penalizer=0.0):
    log(f"\n  {label}:")
    try:
        dc = df_c.copy().dropna()
        dc = dc[dc["T"] > 0]
        if len(dc) < 20:
            log(f"  Skipped: n={len(dc)}")
            return None
        log(f"  n={len(dc)}")
        for col in dc.columns:
            if col in ["T","E"]:
                continue
            sd = dc[col].std()
            if sd > 0:
                dc[col] = (
                    (dc[col] - dc[col].mean())
                    / sd
                )
        cph = CoxPHFitter(
            penalizer=penalizer
        )
        cph.fit(dc, "T", "E")
        log(cph.summary[
            ["coef","exp(coef)","p"]
        ].to_string())
        return cph
    except Exception as ex:
        log(f"  Error: {ex}")
        return None

# ============================================================
# STAGE / GRADE ENCODING
# ============================================================

STAGE_MAP = {
    "stage i":1,    "stage ia":1,
    "stage ib":1,   "i":1,
    "stage ii":2,   "stage iia":2,
    "stage iib":2,  "ii":2,
    "stage iii":3,  "stage iiia":3,
    "stage iiib":3, "stage iiic":3,
    "iii":3,
    "stage iv":4,   "stage iva":4,
    "stage ivb":4,  "iv":4,
    "stage i/ii nos":1,
    "not reported":np.nan,
    "unknown":np.nan,
    "":np.nan,"--":np.nan,
}
GRADE_MAP = {
    "g1":1,"grade 1":1,
    "well differentiated":1,
    "g2":2,"grade 2":2,
    "moderately differentiated":2,
    "g3":3,"grade 3":3,
    "poorly differentiated":3,
    "g4":4,"grade 4":4,
    "undifferentiated":4,
    "high grade":3,"low grade":2,
    "not reported":np.nan,
    "unknown":np.nan,"":np.nan,
}

def encode_stage(s):
    if not isinstance(s, str):
        return np.nan
    sl = s.lower().strip()
    v  = STAGE_MAP.get(sl, np.nan)
    if isinstance(v, float) and np.isnan(v):
        if re.search(r"\biv\b|stage\s*4", sl):
            return 4.0
        if re.search(r"\biii", sl):
            return 3.0
        if re.search(r"\bii\b|stage\s*2", sl):
            return 2.0
        if re.search(r"\bi\b|stage\s*1", sl):
            return 1.0
    return (float(v)
            if v is not None
            and not (isinstance(v, float)
                     and np.isnan(v))
            else np.nan)

def encode_grade(g):
    if not isinstance(g, str):
        return np.nan
    gl = g.lower().strip()
    v  = GRADE_MAP.get(gl, np.nan)
    if isinstance(v, float) and np.isnan(v):
        if re.search(r"g4|grade\s*4|undiff", gl):
            return 4.0
        if re.search(r"g3|grade\s*3|poor", gl):
            return 3.0
        if re.search(r"g2|grade\s*2|moder", gl):
            return 2.0
        if re.search(r"g1|grade\s*1|well", gl):
            return 1.0
    return (float(v)
            if v is not None
            and not (isinstance(v, float)
                     and np.isnan(v))
            else np.nan)

# ============================================================
# PARSE EXPRESSION — TCGA
# ============================================================

def parse_expression_tcga(expr_file):
    log("")
    log("=" * 65)
    log("PARSE EXPRESSION — TCGA-LIHC")
    log("=" * 65)

    genes_wanted = set(
        METAB_SWITCH + PROG_FA
        + MUT_GENES + EXHAUSTION_GENES
        + EXTRA_GENES
    )

    opener = (
        gzip.open(expr_file, "rt",
                  encoding="utf-8",
                  errors="ignore")
        if expr_file.endswith(".gz")
        else open(expr_file, "r",
                  encoding="utf-8",
                  errors="ignore")
    )

    sample_ids  = []
    gene_data   = {}
    header_done = False

    with opener as f:
        for line in f:
            line  = line.rstrip("\n")
            parts = line.split("\t")
            if not header_done:
                sample_ids  = [
                    p.strip() for p in parts[1:]
                ]
                header_done = True
                continue
            gene = parts[0].strip().strip('"')
            if gene not in genes_wanted:
                continue
            try:
                vals = [
                    float(p) if p.strip()
                    not in [
                        "","NA","nan",
                        "NaN","NULL",
                    ]
                    else np.nan
                    for p in parts[1:]
                ]
            except ValueError:
                continue
            if gene not in gene_data:
                gene_data[gene] = vals
            else:
                ex = np.array(
                    gene_data[gene], dtype=float)
                nv = np.array(vals, dtype=float)
                if np.nanvar(nv) > np.nanvar(ex):
                    gene_data[gene] = vals

    n_s = len(sample_ids)
    df  = pd.DataFrame(
        {g: v[:n_s]
         for g, v in gene_data.items()},
        dtype=float,
    )
    log(f"  Matrix: {df.shape}")

    stype  = np.array([
        s[13:15] if len(s) >= 15 else "??"
        for s in sample_ids
    ])
    tumour  = ((stype == "01") | np.array([
        "-01" in s for s in sample_ids
    ]))
    hcc_idx = np.where(tumour)[0]
    df_hcc  = df[tumour].reset_index(drop=True)

    log(f"  HCC: {tumour.sum()}  "
        f"Normal: {(stype=='11').sum()}")
    return df_hcc, df, sample_ids, hcc_idx

# ============================================================
# PARSE CLINICAL
# ============================================================

def parse_clinical(surv_file, pheno_file,
                   sample_ids):
    log("")
    log("=" * 65)
    log("PARSE CLINICAL")
    log("=" * 65)

    n       = len(sample_ids)
    sid_idx = {
        s: i for i, s in enumerate(sample_ids)
    }
    os_time  = np.full(n, np.nan)
    os_event = np.full(n, np.nan)
    stage_s  = [""] * n
    grade_s  = [""] * n
    age      = np.full(n, np.nan)

    def match(sid):
        idx = sid_idx.get(sid)
        if idx is not None:
            return idx
        for k, v in sid_idx.items():
            if k[:15] == sid[:15]:
                return v
        for k, v in sid_idx.items():
            if k[:12] == sid[:12]:
                return v
        return None

    def parse_file(fp):
        if not os.path.exists(fp):
            return
        opener = (
            gzip.open(fp, "rt",
                      encoding="utf-8",
                      errors="ignore")
            if fp.endswith(".gz")
            else open(fp, "r",
                      encoding="utf-8",
                      errors="ignore")
        )
        hdr  = None
        cols = {}
        with opener as f:
            for line in f:
                line  = line.rstrip("\n")
                parts = [
                    p.strip().strip('"')
                    for p in line.split("\t")
                ]
                if hdr is None:
                    hdr = [
                        p.lower() for p in parts
                    ]
                    for i, h in enumerate(hdr):
                        if h in [
                            "sample","sample_id",
                            "_sample_id",
                            "submitter_id",
                            "bcr_patient_barcode",
                        ] and "sc" not in cols:
                            cols["sc"] = i
                        if h in [
                            "os.time","os_time",
                            "time","_time",
                        ] and "tc" not in cols:
                            cols["tc"] = i
                        if h in [
                            "os","os_status",
                            "vital_status",
                            "_vital_status",
                        ] and "ec" not in cols:
                            cols["ec"] = i
                        if any(x in h for x in [
                            "stage","ajcc_pathol",
                            "tumor_stage",
                        ]) and "stc" not in cols:
                            cols["stc"] = i
                        if any(x in h for x in [
                            "grade",
                            "neoplasm_grade",
                        ]) and "gc" not in cols:
                            cols["gc"] = i
                        if (h in AGE_COLS
                                and "ac"
                                not in cols):
                            cols["ac"] = i
                    continue

                sc = cols.get("sc")
                if (sc is None
                        or sc >= len(parts)):
                    continue
                idx = match(parts[sc].strip())
                if idx is None:
                    continue

                def get(key):
                    c = cols.get(key)
                    return (
                        parts[c].strip()
                        if c is not None
                        and c < len(parts)
                        else None
                    )

                tv = get("tc")
                if tv and np.isnan(os_time[idx]):
                    try:
                        t_v = float(tv)
                        if t_v > 200:
                            t_v /= 30.44
                        if t_v > 0:
                            os_time[idx] = t_v
                    except (ValueError,
                            TypeError):
                        pass

                ev = get("ec")
                if ev and np.isnan(os_event[idx]):
                    vl = ev.lower()
                    if vl in [
                        "1","dead","deceased",
                        "died",
                    ]:
                        os_event[idx] = 1
                    elif vl in [
                        "0","alive","living",
                        "censored",
                    ]:
                        os_event[idx] = 0
                    else:
                        try:
                            os_event[idx] = float(vl)
                        except (ValueError,
                                TypeError):
                            pass

                sv = get("stc")
                if sv and not stage_s[idx]:
                    stage_s[idx] = sv
                gv = get("gc")
                if gv and not grade_s[idx]:
                    grade_s[idx] = gv
                av = get("ac")
                if av and np.isnan(age[idx]):
                    try:
                        age[idx] = float(av)
                    except (ValueError,
                            TypeError):
                        pass

    parse_file(surv_file)
    parse_file(pheno_file)

    stage_num = np.array(
        [encode_stage(s) for s in stage_s],
        dtype=float,
    )
    grade_num = np.array(
        [encode_grade(g) for g in grade_s],
        dtype=float,
    )

    valid_os = (
        ~np.isnan(os_time)
        & ~np.isnan(os_event)
        & (os_time > 0)
    )
    from collections import Counter
    sv = stage_num[~np.isnan(stage_num)]
    av = age[~np.isnan(age)]
    log(f"  OS valid: {valid_os.sum()} "
        f"events="
        f"{int(os_event[valid_os].sum())}")
    log(f"  Stage: "
        f"{dict(Counter(sv.astype(int)).most_common())}")
    log(f"  Age valid: {len(av)}"
        + (f"  mean={av.mean():.1f}"
           if len(av) else ""))

    return {
        "os_time":   os_time,
        "os_event":  os_event,
        "stage":     stage_num,
        "grade":     grade_num,
        "age":       age,
    }

# ============================================================
# PARSE MAF
# ============================================================

def parse_maf(maf_file, sample_ids):
    log("")
    log("=" * 65)
    log("PARSE MAF — HCC-P5 FINAL ATTEMPT")
    log("=" * 65)

    n       = len(sample_ids)
    sid_idx = {
        s: i for i, s in enumerate(sample_ids)
    }
    mut_matrix = {
        g: np.zeros(n, dtype=int)
        for g in MUT_GENES
    }

    if not os.path.exists(maf_file):
        log("  MAF not found.")
        _maf_notice()
        return mut_matrix

    sz = os.path.getsize(maf_file)
    log(f"  File: {maf_file} ({sz:,} bytes)")

    if sz < 10000:
        log(f"  File too small ({sz}b).")
        log("  This is the truncated "
            "cBioPortal file — not a full MAF.")
        _maf_notice()
        return mut_matrix

    log("  Full MAF detected — parsing...")
    gene_set = set(MUT_GENES)
    BENIGN   = [
        "synonymous","silent",
        "3_prime_utr","5_prime_utr",
        "3'utr","5'utr","intron",
        "intergenic","igr","rna",
    ]

    opener = (
        gzip.open(maf_file, "rt",
                  encoding="utf-8",
                  errors="ignore")
        if maf_file.endswith(".gz")
        else open(maf_file, "r",
                  encoding="utf-8",
                  errors="ignore")
    )

    hdr    = None
    gene_c = sample_c = effect_c = None
    n_muts = 0

    def match_sid(sid):
        idx = sid_idx.get(sid)
        if idx is not None:
            return idx
        for k, v in sid_idx.items():
            if k[:15] == sid[:15]:
                return v
        for k, v in sid_idx.items():
            if k[:12] == sid[:12]:
                return v
        return None

    with opener as f:
        for raw in f:
            line = raw.rstrip("\n")
            if line.startswith("#"):
                continue
            parts = [
                p.strip().strip('"')
                for p in line.split("\t")
            ]
            if hdr is None:
                hdr = [p.upper() for p in parts]
                for i, h in enumerate(hdr):
                    hl = h.lower()
                    if (hl in [
                        "hugo_symbol","gene",
                    ] and gene_c is None):
                        gene_c = i
                    if (any(x in hl for x in [
                        "tumor_sample_barcode",
                        "tumor_sample",
                    ]) and sample_c is None):
                        sample_c = i
                    if (any(x in hl for x in [
                        "variant_classification",
                        "consequence",
                    ]) and effect_c is None):
                        effect_c = i
                log(f"  Headers: {hdr[:8]}")
                log(f"  gene={gene_c} "
                    f"sample={sample_c}")
                continue

            if (gene_c is None
                    or sample_c is None):
                continue
            if max(gene_c, sample_c) >= len(parts):
                continue

            gene = parts[gene_c].strip()
            if gene not in gene_set:
                continue
            idx  = match_sid(
                parts[sample_c].strip()
            )
            if idx is None:
                continue

            keep = True
            if (effect_c is not None
                    and effect_c < len(parts)):
                eff = parts[effect_c].lower()
                if any(b in eff for b in BENIGN):
                    keep = False
            if keep:
                mut_matrix[gene][idx] = 1
                n_muts += 1

    log(f"\n  Mutations parsed: {n_muts}")
    if n_muts > 0:
        log(f"  {'Gene':<14} {'n':>5} {'%':>8}")
        log(f"  {'-'*30}")
        for g in MUT_GENES:
            freq = mut_matrix[g].sum()
            if freq > 0:
                log(f"  {g:<14} {freq:>5} "
                    f"{100*freq/n:>8.1f}%")
    return mut_matrix


def _maf_notice():
    log("")
    log("  HCC-P5 unresolved after 8 scripts.")
    log("  GDC manual download:")
    log("  https://portal.gdc.cancer.gov"
        "/repository")
    log("  TCGA-LIHC → Masked Somatic "
        "Mutation → WXS → Open → Download")
    log(f"  Save to: {MAF_FILE}")

# ============================================================
# BUILD DEPTH
# ============================================================

def build_depth(df_hcc):
    gc = list(df_hcc.columns)
    sw = [g for g in METAB_SWITCH if g in gc]
    fa = [g for g in PROG_FA      if g in gc]
    n  = len(df_hcc)
    d  = np.zeros(n, dtype=float)
    nd = 0
    if sw:
        d  += 1 - norm01(
            df_hcc[sw].mean(axis=1).values
        )
        nd += 1
    if fa:
        d  += norm01(
            df_hcc[fa].mean(axis=1).values
        )
        nd += 1
    if nd:
        d /= nd
    log(f"  mean={d.mean():.4f}  "
        f"std={d.std():.4f}")
    return d

# ============================================================
# S8-1: MUTATION SURVIVAL
# ============================================================

def mutation_survival(
    mut_matrix, os_time, os_event,
    hcc_idx, df_hcc, depth_metab,
):
    log("")
    log("=" * 65)
    log("S8-1: MUTATION SURVIVAL")
    log("S8-P1: CTNNB1-mut better OS (HCC-P5)")
    log("S8-P2: TP53-mut worse OS")
    log("=" * 65)

    t       = os_time[hcc_idx]
    e       = os_event[hcc_idx]
    gc      = list(df_hcc.columns)
    mut_hcc = {
        g: mut_matrix[g][hcc_idx]
        for g in MUT_GENES
    }

    total = sum(
        mut_hcc[g].sum() for g in MUT_GENES
    )
    if total == 0:
        log("  No mutation data.")
        log("  HCC-P5 unresolved after "
            "8 scripts.")
        log("  Will be addressed in literature "
            "check using published CTNNB1 OS data.")
        return {}

    results = {}
    log(f"\n  {'Gene':<12} {'n_mut':>6} "
        f"{'mut_OS':>9} {'wt_OS':>9}  "
        f"logrank       dir")
    log(f"  {'-'*64}")

    for gene in MUT_GENES:
        gm    = mut_hcc[gene]
        n_mut = int(gm.sum())
        if n_mut < 5:
            continue

        mm  = gm == 1
        wm  = gm == 0
        vm  = (mm & np.isfinite(t)
               & np.isfinite(e) & (t > 0))
        vw  = (wm & np.isfinite(t)
               & np.isfinite(e) & (t > 0))

        m_m = t[vm].mean() if vm.sum() > 0 \
            else np.nan
        m_w = t[vw].mean() if vw.sum() > 0 \
            else np.nan
        p   = logrank_p(
            t[mm], e[mm], t[wm], e[wm]
        )
        d_m = depth_metab[mm].mean() \
            if mm.sum() > 0 else np.nan
        d_w = depth_metab[wm].mean() \
            if wm.sum() > 0 else np.nan

        log(f"  {gene:<12} {n_mut:>6} "
            f"{m_m:>9.1f} {m_w:>9.1f}  "
            f"{fmt_p(p)}  "
            f"{'↑better' if m_m>m_w else '↑worse'}")
        results[gene] = {
            "n_mut": n_mut, "mmask": mm,
            "wmask": wm,    "p":     p,
            "m_mut": m_m,   "m_wt":  m_w,
            "d_mut": d_m,   "d_wt":  d_w,
        }

    log("")
    for gene, better, label in [
        ("CTNNB1", True,
         "S8-P1: CTNNB1-mut better OS (HCC-P5)"),
        ("TP53",   False,
         "S8-P2: TP53-mut worse OS"),
    ]:
        if gene not in results:
            log(f"  {label}")
            log("  STATUS: NOT TESTABLE")
            continue
        res  = results[gene]
        conf = (
            res["m_mut"] > res["m_wt"]
            if better
            else res["m_mut"] < res["m_wt"]
        )
        sig  = (not np.isnan(res["p"])
                and res["p"] < 0.05)
        log(f"  {label}")
        log(f"  n={res['n_mut']}  "
            f"mut={res['m_mut']:.1f}mo  "
            f"wt={res['m_wt']:.1f}mo  "
            f"{fmt_p(res['p'])}")
        log(f"  STATUS: "
            f"{'CONFIRMED ✓' if conf and sig else 'DIRECTIONAL ✓' if conf else 'NOT CONFIRMED ✗'}")

    return results

# ============================================================
# S8-2: HDAC2 STAGE III DEEP-DIVE
# ============================================================

def hdac2_stage3_analysis(
    df_hcc, depth_metab, os_time, os_event,
    hcc_idx, clin,
):
    log("")
    log("=" * 65)
    log("S8-2: HDAC2 STAGE III DEEP-DIVE")
    log("S8-P3: HDAC2-hi+CDK4-hi worst OS")
    log("S8-P7: HDAC2 Cox HR > CDK4 in S3")
    log("=" * 65)

    t   = os_time[hcc_idx]
    e   = os_event[hcc_idx]
    stg = clin["stage"][hcc_idx]
    gc  = list(df_hcc.columns)

    s3      = stg == 3
    t_3     = t[s3]
    e_3     = e[s3]
    d_3     = depth_metab[s3]
    log(f"  Stage III n={s3.sum()}")

    if "HDAC2" not in gc:
        log("  HDAC2 not in matrix")
        return {}

    hdac2_3 = df_hcc["HDAC2"].values[s3]
    cdk4_3  = df_hcc["CDK4"].values[s3] \
        if "CDK4" in gc else None
    prf1_3  = df_hcc["PRF1"].values[s3] \
        if "PRF1" in gc else None

    # HDAC2 univariate in Stage III
    valid3 = (np.isfinite(t_3)
              & np.isfinite(e_3)
              & (t_3 > 0))
    med_h  = np.nanmedian(hdac2_3[valid3])
    hi_h   = valid3 & (hdac2_3 >= med_h)
    lo_h   = valid3 & (hdac2_3 <  med_h)
    p_h    = logrank_p(
        t_3[hi_h], e_3[hi_h],
        t_3[lo_h], e_3[lo_h],
    )
    m_hi_h = t_3[hi_h].mean() \
        if hi_h.sum() > 0 else np.nan
    m_lo_h = t_3[lo_h].mean() \
        if lo_h.sum() > 0 else np.nan
    log(f"\n  HDAC2 OS Stage III:")
    log(f"  hi={m_hi_h:.1f}mo  lo={m_lo_h:.1f}mo  "
        f"{fmt_p(p_h)}  gap="
        f"{abs(m_hi_h-m_lo_h):.1f}mo")

    # HDAC2 tertile in Stage III
    t33h, t67h = np.percentile(
        hdac2_3[valid3], [33, 67]
    )
    h_t1 = valid3 & (hdac2_3 <= t33h)
    h_t2 = (valid3 & (hdac2_3 > t33h)
            & (hdac2_3 <= t67h))
    h_t3 = valid3 & (hdac2_3 > t67h)
    p_h13 = logrank_p(
        t_3[h_t1], e_3[h_t1],
        t_3[h_t3], e_3[h_t3],
    )
    log(f"\n  HDAC2 tertile Stage III:")
    for tlbl, tmask in [
        ("T1 low",  h_t1),
        ("T2 mid",  h_t2),
        ("T3 high", h_t3),
    ]:
        vm = tmask & np.isfinite(t_3)
        m  = t_3[vm].mean() \
            if vm.sum() > 0 else np.nan
        log(f"  {tlbl}: n={tmask.sum()} "
            f"OS={m:.1f}mo")
    log(f"  T3 vs T1: {fmt_p(p_h13)}")

    # S8-P7: HDAC2 vs CDK4 Cox Stage III
    log(f"\n  S8-P7: HDAC2 vs CDK4 Cox "
        f"Stage III:")
    if cdk4_3 is not None:
        run_cox(
            pd.DataFrame({
                "T":     t_3,
                "E":     e_3,
                "HDAC2": hdac2_3,
                "CDK4":  cdk4_3,
                "depth": d_3,
            }),
            "HDAC2 + CDK4 + depth "
            "(Stage III)",
        )

    # S8-P3: HDAC2 × CDK4 joint groups
    log(f"\n  S8-P3: HDAC2 × CDK4 joint "
        f"OS Stage III:")
    if cdk4_3 is not None:
        med_cdk4 = np.nanmedian(
            cdk4_3[valid3]
        )
        both_hi  = (valid3
                    & (hdac2_3 >= med_h)
                    & (cdk4_3 >= med_cdk4))
        both_lo  = (valid3
                    & (hdac2_3 <  med_h)
                    & (cdk4_3 <  med_cdk4))
        h_hi_c_lo = (valid3
                     & (hdac2_3 >= med_h)
                     & (cdk4_3 <  med_cdk4))
        h_lo_c_hi = (valid3
                     & (hdac2_3 <  med_h)
                     & (cdk4_3 >= med_cdk4))

        log(f"  {'Group':<24} {'n':>4} "
            f"{'OS_mean':>9}  events")
        log(f"  {'-'*45}")
        grp_means = {}
        for label, mask in [
            ("HDAC2-hi+CDK4-hi", both_hi),
            ("HDAC2-hi+CDK4-lo", h_hi_c_lo),
            ("HDAC2-lo+CDK4-hi", h_lo_c_hi),
            ("HDAC2-lo+CDK4-lo", both_lo),
        ]:
            vm  = mask & np.isfinite(t_3) \
                & np.isfinite(e_3)
            m_t = t_3[vm].mean() \
                if vm.sum() > 0 else np.nan
            n_e = int(e_3[vm].sum()) \
                if vm.sum() > 0 else 0
            log(f"  {label:<24} {vm.sum():>4} "
                f"{m_t:>9.1f}  {n_e}")
            grp_means[label] = (m_t, mask)

        # Best vs worst logrank
        worst_lbl = min(
            grp_means,
            key=lambda k: grp_means[k][0]
            if not np.isnan(grp_means[k][0])
            else np.inf,
        )
        best_lbl  = max(
            grp_means,
            key=lambda k: grp_means[k][0]
            if not np.isnan(grp_means[k][0])
            else -np.inf,
        )
        p_bw = logrank_p(
            t_3[grp_means[worst_lbl][1]],
            e_3[grp_means[worst_lbl][1]],
            t_3[grp_means[best_lbl][1]],
            e_3[grp_means[best_lbl][1]],
        )
        log(f"\n  Worst: {worst_lbl} "
            f"OS={grp_means[worst_lbl][0]:.1f}mo")
        log(f"  Best:  {best_lbl} "
            f"OS={grp_means[best_lbl][0]:.1f}mo")
        log(f"  Logrank: {fmt_p(p_bw)}")

        # S8-P3 check
        worst_is_both_hi = (
            worst_lbl == "HDAC2-hi+CDK4-hi"
        )
        worst_os = grp_means[worst_lbl][0]
        log(f"\n  S8-P3: HDAC2-hi+CDK4-hi "
            f"Stage III worst OS")
        log(f"  Worst group: {worst_lbl} "
            f"({worst_os:.1f}mo)")
        log(f"  STATUS: "
            f"{'CONFIRMED ✓' if worst_is_both_hi else 'NOT CONFIRMED ✗'}")

        # Store for figure
        ret = {
            "both_hi": both_hi,
            "both_lo": both_lo,
            "h_hi_c_lo": h_hi_c_lo,
            "h_lo_c_hi": h_lo_c_hi,
            "grp_means": grp_means,
            "p_bw": p_bw,
            "t_3": t_3, "e_3": e_3,
            "hi_h": hi_h, "lo_h": lo_h,
            "p_h": p_h,
            "m_hi_h": m_hi_h,
            "m_lo_h": m_lo_h,
        }
    else:
        ret = {
            "hi_h": hi_h, "lo_h": lo_h,
            "p_h": p_h,
            "m_hi_h": m_hi_h,
            "m_lo_h": m_lo_h,
            "t_3": t_3, "e_3": e_3,
        }

    # S8-P4: HDAC2 × PRF1 joint groups
    log(f"\n  S8-P4: HDAC2 × PRF1 joint OS "
        f"Stage III:")
    if prf1_3 is not None:
        med_prf1 = np.nanmedian(
            prf1_3[valid3]
        )
        h_hi_p_lo = (valid3
                     & (hdac2_3 >= med_h)
                     & (prf1_3 <  med_prf1))
        h_lo_p_hi = (valid3
                     & (hdac2_3 <  med_h)
                     & (prf1_3 >= med_prf1))
        h_hi_p_hi = (valid3
                     & (hdac2_3 >= med_h)
                     & (prf1_3 >= med_prf1))
        h_lo_p_lo = (valid3
                     & (hdac2_3 <  med_h)
                     & (prf1_3 <  med_prf1))

        log(f"  {'Group':<24} {'n':>4} "
            f"{'OS_mean':>9}  events")
        log(f"  {'-'*45}")
        prf_means = {}
        for label, mask in [
            ("HDAC2-hi+PRF1-lo", h_hi_p_lo),
            ("HDAC2-hi+PRF1-hi", h_hi_p_hi),
            ("HDAC2-lo+PRF1-lo", h_lo_p_lo),
            ("HDAC2-lo+PRF1-hi", h_lo_p_hi),
        ]:
            vm  = mask & np.isfinite(t_3) \
                & np.isfinite(e_3)
            m_t = t_3[vm].mean() \
                if vm.sum() > 0 else np.nan
            n_e = int(e_3[vm].sum()) \
                if vm.sum() > 0 else 0
            log(f"  {label:<24} {vm.sum():>4} "
                f"{m_t:>9.1f}  {n_e}")
            prf_means[label] = (m_t, mask)

        worst_p = min(
            prf_means,
            key=lambda k: prf_means[k][0]
            if not np.isnan(prf_means[k][0])
            else np.inf,
        )
        best_p  = max(
            prf_means,
            key=lambda k: prf_means[k][0]
            if not np.isnan(prf_means[k][0])
            else -np.inf,
        )
        p_prf = logrank_p(
            t_3[prf_means[worst_p][1]],
            e_3[prf_means[worst_p][1]],
            t_3[prf_means[best_p][1]],
            e_3[prf_means[best_p][1]],
        )
        log(f"\n  Worst: {worst_p} "
            f"OS={prf_means[worst_p][0]:.1f}mo")
        log(f"  Best:  {best_p} "
            f"OS={prf_means[best_p][0]:.1f}mo")
        log(f"  Logrank: {fmt_p(p_prf)}")

        worst_is_hdac2hi_prf1lo = (
            worst_p == "HDAC2-hi+PRF1-lo"
        )
        log(f"\n  S8-P4: HDAC2-hi+PRF1-lo "
            f"Stage III worst immune")
        log(f"  STATUS: "
            f"{'CONFIRMED ✓' if worst_is_hdac2hi_prf1lo else 'NOT CONFIRMED ✗'}")

        ret["prf_means"] = prf_means
        ret["p_prf"] = p_prf

    return ret

# ============================================================
# S8-3: CDC20 + STAGE + HDAC2 COX MODEL
# ============================================================

def cdc20_hdac2_stage_model(
    df_hcc, depth_metab, os_time, os_event,
    hcc_idx, clin,
):
    log("")
    log("=" * 65)
    log("S8-3: CDC20 + STAGE + HDAC2 COX")
    log("S8-P5: Three-variable model beats "
        "stage alone")
    log("=" * 65)

    t   = os_time[hcc_idx]
    e   = os_event[hcc_idx]
    stg = clin["stage"][hcc_idx]
    gc  = list(df_hcc.columns)

    cdc20 = df_hcc["CDC20"].values \
        if "CDC20" in gc else None
    hdac2 = df_hcc["HDAC2"].values \
        if "HDAC2" in gc else None

    if cdc20 is None or hdac2 is None:
        log("  CDC20 or HDAC2 missing")
        return

    # Baseline: stage alone
    cph_s = run_cox(
        pd.DataFrame({
            "T": t, "E": e, "stage": stg,
        }),
        "Baseline: stage alone",
    )

    # Stage + depth
    run_cox(
        pd.DataFrame({
            "T": t, "E": e,
            "stage": stg,
            "depth": depth_metab,
        }),
        "Model A: stage + depth",
    )

    # Stage + CDC20
    run_cox(
        pd.DataFrame({
            "T": t, "E": e,
            "stage": stg, "CDC20": cdc20,
        }),
        "Model B: stage + CDC20",
    )

    # Stage + HDAC2
    run_cox(
        pd.DataFrame({
            "T": t, "E": e,
            "stage": stg, "HDAC2": hdac2,
        }),
        "Model C: stage + HDAC2",
    )

    # Stage + CDC20 + HDAC2 (primary)
    cph_3 = run_cox(
        pd.DataFrame({
            "T":     t, "E": e,
            "stage": stg,
            "CDC20": cdc20,
            "HDAC2": hdac2,
        }),
        "Model D: stage + CDC20 + HDAC2",
    )

    # Stage + CDC20 + HDAC2 + depth
    run_cox(
        pd.DataFrame({
            "T":     t, "E": e,
            "stage": stg,
            "CDC20": cdc20,
            "HDAC2": hdac2,
            "depth": depth_metab,
        }),
        "Model E: stage + CDC20 + "
        "HDAC2 + depth",
    )

    # S8-P5 check: compare C-stat of
    # stage alone vs Model D
    # Use AIC as proxy
    if cph_s is not None and cph_3 is not None:
        try:
            aic_s = cph_s.AIC_
            aic_d = cph_3.AIC_
            log(f"\n  AIC comparison:")
            log(f"  Stage alone:            "
                f"AIC={aic_s:.2f}")
            log(f"  Stage+CDC20+HDAC2:      "
                f"AIC={aic_d:.2f}")
            log(f"  ΔAIC = {aic_s - aic_d:.2f}")
            improved = aic_d < aic_s
            log(f"\n  S8-P5: Three-variable model "
                f"beats stage alone")
            log(f"  STATUS: "
                f"{'CONFIRMED ✓' if improved else 'NOT CONFIRMED ✗'} "
                f"(ΔAIC={aic_s-aic_d:.2f}, "
                f"positive=improvement)")
        except Exception as ex:
            log(f"  AIC error: {ex}")

# ============================================================
# S8-4: GSE14520 CDK4 VIA GEO DOWNLOAD
# ============================================================

def gse14520_cdk4_geo():
    log("")
    log("=" * 65)
    log("S8-4: GSE14520 CDK4 — GEO DOWNLOAD")
    log("S8-P6: CDK4-hi worse OS GSE14520")
    log("=" * 65)

    # Check if already downloaded
    if os.path.exists(GSE_MATRIX_FILE):
        sz = os.path.getsize(GSE_MATRIX_FILE)
        log(f"  Matrix file exists: "
            f"{sz:,} bytes")
        return _parse_gse_matrix_for_cdk4(
            GSE_MATRIX_FILE
        )

    log("  Downloading GSE14520 series "
        "matrix from NCBI GEO...")
    log(f"  URL: {GSE14520_MATRIX_URL}")

    try:
        r = requests.get(
            GSE14520_MATRIX_URL,
            stream=True, timeout=300,
            headers={
                "User-Agent":
                "OrganismCore/1.0 "
                "(eric.lawson@research)"
            },
        )
        log(f"  HTTP {r.status_code}")
        if r.status_code == 200:
            raw = b"".join(
                r.iter_content(1024 * 1024)
            )
            with open(
                GSE_MATRIX_FILE, "wb"
            ) as f:
                f.write(raw)
            sz = os.path.getsize(
                GSE_MATRIX_FILE
            )
            log(f"  Saved: {sz:,} bytes")
            if sz > 100000:
                return _parse_gse_matrix_for_cdk4(
                    GSE_MATRIX_FILE
                )
            else:
                log("  File too small "
                    "— download may have failed")
                os.remove(GSE_MATRIX_FILE)
        else:
            log(f"  Download failed: "
                f"HTTP {r.status_code}")
    except Exception as ex:
        log(f"  Download error: {ex}")

    # Try alternative URL construction
    # GSE14520 has two sub-series
    for acc, url in [
        ("GSE14520_part1",
         "https://ftp.ncbi.nlm.nih.gov/geo"
         "/series/GSE14nnn/GSE14520/matrix"
         "/GSE14520-GPL3921_series_matrix"
         ".txt.gz"),
        ("GSE14520_part2",
         "https://ftp.ncbi.nlm.nih.gov/geo"
         "/series/GSE14nnn/GSE14520/matrix"
         "/GSE14520-GPL10687_series_matrix"
         ".txt.gz"),
    ]:
        log(f"  Trying: {url}")
        try:
            r = requests.get(
                url, stream=True,
                timeout=300,
                headers={
                    "User-Agent":
                    "OrganismCore/1.0"
                },
            )
            log(f"  HTTP {r.status_code}")
            if r.status_code == 200:
                fp = os.path.join(
                    GSE_DIR,
                    f"{acc}_matrix.txt.gz",
                )
                raw = b"".join(
                    r.iter_content(
                        1024 * 1024
                    )
                )
                with open(fp, "wb") as f:
                    f.write(raw)
                sz = os.path.getsize(fp)
                log(f"  Saved {acc}: "
                    f"{sz:,} bytes")
                if sz > 100000:
                    result = (
                        _parse_gse_matrix_for_cdk4(
                            fp
                        )
                    )
                    if result:
                        return result
        except Exception as ex:
            log(f"  Error: {ex}")

    log("  GEO download failed.")
    log("  S8-P6: NOT TESTABLE")
    log("  CDK4 in GSE14520 remains "
        "deferred post-literature.")
    return False


def _parse_gse_matrix_for_cdk4(matrix_file):
    log(f"\n  Parsing: {matrix_file}")

    opener = (
        gzip.open(matrix_file, "rt",
                  encoding="utf-8",
                  errors="ignore")
        if matrix_file.endswith(".gz")
        else open(matrix_file, "r",
                  encoding="utf-8",
                  errors="ignore")
    )

    # GSE series matrix format:
    # !Series_... metadata lines
    # !Sample_... sample metadata
    # "ID_REF"  "GSM..."  "GSM..."  ...
    # probe_id  val1      val2      ...
    # !series_matrix_table_end

    sample_ids_gse = []
    os_time_gse    = []
    os_event_gse   = []
    cdk4_vals      = None
    depth_vals     = None   # from score file
    in_table       = False
    header_found   = False

    # Clinical from series matrix
    # sample characteristics
    surv_dict  = {}  # GSM_id -> (t, e)
    char_lines = []

    with opener as f:
        for raw in f:
            line = raw.rstrip("\n")

            # Collect sample characteristics
            if line.startswith(
                "!Sample_characteristics_ch1"
            ):
                char_lines.append(line)
                continue

            if line.startswith(
                "!Sample_geo_accession"
            ):
                parts = line.split("\t")
                sample_ids_gse = [
                    p.strip().strip('"')
                    for p in parts[1:]
                ]
                continue

            if "series_matrix_table_begin" \
                    in line:
                in_table = True
                continue

            if "series_matrix_table_end" \
                    in line:
                break

            if not in_table:
                continue

            parts = [
                p.strip().strip('"')
                for p in line.split("\t")
            ]
            if not header_found:
                # Header row: ID_REF  GSM...
                header_found = True
                if not sample_ids_gse:
                    sample_ids_gse = parts[1:]
                continue

            probe_id = parts[0].strip()

            if probe_id in CDK4_PROBES:
                log(f"  Found CDK4 probe: "
                    f"{probe_id}")
                try:
                    cdk4_vals = np.array([
                        float(p)
                        if p not in [
                            "","null","NA",
                            "nan","NaN",
                        ]
                        else np.nan
                        for p in parts[1:]
                    ])
                except (ValueError,
                        TypeError):
                    pass

    if cdk4_vals is None:
        log("  CDK4 probe not found "
            "in matrix")
        log("  S8-P6: NOT TESTABLE")
        return False

    n_s = len(sample_ids_gse)
    log(f"  Samples: {n_s}")
    log(f"  CDK4 values: "
        f"n={np.isfinite(cdk4_vals).sum()}")

    # Load depth scores and survival from
    # Script 2 score file
    if not os.path.exists(GSE_SCORE_FILE):
        log(f"  Score file not found: "
            f"{GSE_SCORE_FILE}")
        log("  Cannot match CDK4 to survival.")
        return False

    df_s = pd.read_csv(GSE_SCORE_FILE)
    log(f"  Score file: {df_s.shape}  "
        f"cols={list(df_s.columns)}")

    n_sc = len(df_s)
    if n_sc != len(cdk4_vals):
        log(f"  Length mismatch: "
            f"CDK4={len(cdk4_vals)} "
            f"scores={n_sc}")
        log("  Attempting positional match...")
        min_n = min(n_sc, len(cdk4_vals))
        cdk4_vals = cdk4_vals[:min_n]
        df_s = df_s.iloc[:min_n]

    # Extract survival
    t_col = next(
        (c for c in df_s.columns
         if "time" in c.lower()
         or "os_t" in c.lower()),
        None,
    )
    e_col = next(
        (c for c in df_s.columns
         if c.lower() in [
             "os", "os_event",
             "event","status",
         ]),
        None,
    )
    d_col = next(
        (c for c in df_s.columns
         if "depth" in c.lower()
         or "metab" in c.lower()),
        None,
    )

    if t_col is None or e_col is None:
        log("  Survival columns not found")
        log(f"  Available: "
            f"{list(df_s.columns)}")
        return False

    t_arr = df_s[t_col].values.astype(float)
    e_arr = df_s[e_col].values.astype(float)
    d_arr = df_s[d_col].values.astype(float) \
        if d_col else None

    # Days to months
    if np.nanmedian(t_arr[t_arr > 0]) > 200:
        t_arr = t_arr / 30.44

    valid = (np.isfinite(cdk4_vals)
             & np.isfinite(t_arr)
             & np.isfinite(e_arr)
             & (t_arr > 0))
    log(f"  Valid samples: {valid.sum()}")

    if valid.sum() < 20:
        log("  Too few valid samples")
        return False

    # Depth correlation
    if d_arr is not None:
        rv, pv = safe_pearsonr(
            d_arr, cdk4_vals
        )
        log(f"\n  r(depth, CDK4) = "
            f"{rv:+.4f}  {fmt_p(pv)}")

    # OS analysis
    med   = np.nanmedian(cdk4_vals[valid])
    hi    = valid & (cdk4_vals >= med)
    lo    = valid & (cdk4_vals <  med)
    p_os  = logrank_p(
        t_arr[hi], e_arr[hi],
        t_arr[lo], e_arr[lo],
    )
    m_hi  = t_arr[hi].mean() \
        if hi.sum() > 0 else np.nan
    m_lo  = t_arr[lo].mean() \
        if lo.sum() > 0 else np.nan

    # Tertile
    t33, t67 = np.percentile(
        cdk4_vals[valid], [33, 67]
    )
    t1 = valid & (cdk4_vals <= t33)
    t2 = (valid & (cdk4_vals > t33)
          & (cdk4_vals <= t67))
    t3 = valid & (cdk4_vals > t67)
    p13 = logrank_p(
        t_arr[t1], e_arr[t1],
        t_arr[t3], e_arr[t3],
    )

    log(f"\n  CDK4 OS — GSE14520:")
    log(f"  Median split: {fmt_p(p_os)}")
    log(f"  CDK4-hi={m_hi:.1f}mo  "
        f"CDK4-lo={m_lo:.1f}mo")
    log(f"  Tertile T3 vs T1: {fmt_p(p13)}")
    for tlbl, tmask in [
        ("T1 low", t1), ("T2 mid", t2),
        ("T3 high", t3),
    ]:
        vm = tmask & np.isfinite(t_arr)
        m  = t_arr[vm].mean() \
            if vm.sum() > 0 else np.nan
        log(f"    {tlbl}: n={tmask.sum()} "
            f"OS={m:.1f}mo")

    conf = (not np.isnan(m_hi)
            and not np.isnan(m_lo)
            and m_hi < m_lo)
    sig  = (not np.isnan(p_os)
            and p_os < 0.05)
    log(f"\n  S8-P6: CDK4-hi worse OS "
        f"in GSE14520")
    log(f"  STATUS: "
        f"{'CONFIRMED ✓' if conf and sig else 'DIRECTIONAL ✓' if conf else 'NOT CONFIRMED ✗'}")

    return {
        "cdk4": cdk4_vals,
        "t":    t_arr,
        "e":    e_arr,
        "hi":   hi,
        "lo":   lo,
        "p_os": p_os,
        "m_hi": m_hi,
        "m_lo": m_lo,
    }

# ============================================================
# S8-5: FINAL FRAMEWORK SUMMARY
# ============================================================

def final_framework_summary(
    df_hcc, depth_metab, os_time, os_event,
    hcc_idx, clin,
):
    log("")
    log("=" * 65)
    log("S8-5: FINAL PRE-LITERATURE SUMMARY")
    log("All confirmed findings across 8 scripts")
    log("=" * 65)

    t   = os_time[hcc_idx]
    e   = os_event[hcc_idx]
    stg = clin["stage"][hcc_idx]
    gc  = list(df_hcc.columns)

    log(f"\n  CORE FRAMEWORK:")
    log(f"  {'Finding':<50}  {'Evidence'}")
    log(f"  {'-'*70}")

    findings = [
        ("Depth score predicts OS (TCGA-LIHC)",
         "p=1.01e-04  HR=1.362"),
        ("Depth score predicts OS (GSE14520)",
         "p=1.78e-05"),
        ("Depth independent of stage (Cox)",
         "HR=1.245  p=0.017"),
        ("Depth absorbs grade (grade NS Cox)",
         "grade HR=0.977  p=0.808"),
        ("Age independently prognostic",
         "HR=1.225  p=0.030"),
        ("Full model: depth+stage+grade+age",
         "depth HR=1.244  p=0.027"),
        ("CDC20 = best depth proxy gene",
         "r=+0.677  absorbs depth in Cox"),
        ("Stage I depth reversal",
         "deep=31.9mo > shal=27.1mo"),
        ("Stage II-III depth predicts OS",
         "S3 tertile p=0.017"),
        ("HDAC2 Stage III gap = 19.2mo",
         "p=1.93e-04  13.7 vs 32.9mo"),
        ("CDK4 Stage III gap = 14.0mo",
         "p=4.88e-04  16.3 vs 30.3mo"),
        ("CDKN2A co-expresses with CDK4",
         "r=+0.277  p=5.94e-08"),
        ("CDK4+CDKN2A-hi worst quadrant",
         "OS=21.1mo vs 32.3mo"),
        ("Deep+Cold immune-desert subtype",
         "OS=24.7mo  CD8A p=3.66e-21"),
        ("CD8A-high better OS",
         "p=0.013  29.6 vs 23.8mo"),
        ("PRF1-high better OS Stage III",
         "p=0.035  29.5 vs 16.9mo"),
        ("Immune exhaustion r=+0.37 w depth",
         "composite p=3.42e-13"),
        ("CDC20 tertile T3 vs T1",
         "p=5.23e-06  22.1 vs 30.7mo"),
        ("5 co-inhibitory receptors up",
         "PD-1/TIM-3/LAG-3/TIGIT/CTLA-4"),
    ]
    for f_txt, e_txt in findings:
        log(f"  ✓  {f_txt:<50}  {e_txt}")

    log(f"\n  PENDING:")
    log(f"  ?  HCC-P5 (CTNNB1 mut OS)  "
        f"— MAF file incomplete")
    log(f"  ?  CDK4 in GSE14520  "
        f"— expression data needed")

    log(f"\n  DRUG HYPOTHESIS PRIORITIES:")
    log(f"  {'Target':<20} {'Biomarker':<25} "
        f"{'Stage':<10} Grade")
    log(f"  {'-'*65}")
    drugs = [
        ("HDAC2 inhib",
         "HDAC2-high",
         "Stage III", "A"),
        ("CDK4/6 inhib",
         "CDK4-hi+CDKN2A-hi",
         "Stage II-III", "A"),
        ("Checkpoint inhib",
         "PRF1-hi/exhaust-hi",
         "Stage II-III", "B"),
        ("CDC20 inhib",
         "CDC20-high/depth",
         "Stage II-III", "B"),
        ("mTOR inhib",
         "PTEN-low+Deep+Hot",
         "All", "B"),
        ("Sorafenib",
         "Depth-deep",
         "Stage II-III", "B"),
    ]
    for d, b, s, g in drugs:
        log(f"  {d:<20} {b:<25} "
            f"{s:<10} {g}")

    # Save final summary CSV
    valid = (np.isfinite(t)
             & np.isfinite(e)
             & (t > 0))
    gene_rows = []
    for gene in sorted(gc):
        gv = df_hcc[gene].values
        rv, pv = safe_pearsonr(
            depth_metab, gv
        )
        vv = (np.isfinite(gv)
              & np.isfinite(t)
              & np.isfinite(e)
              & (t > 0))
        if vv.sum() < 20:
            continue
        med  = np.nanmedian(gv[vv])
        hi   = vv & (gv >= med)
        lo   = vv & (gv <  med)
        p_os = logrank_p(
            t[hi], e[hi], t[lo], e[lo]
        )
        m_hi = t[hi].mean() \
            if hi.sum() > 0 else np.nan
        m_lo = t[lo].mean() \
            if lo.sum() > 0 else np.nan
        gene_rows.append({
            "gene":     gene,
            "r_depth":  rv,
            "p_r_depth": pv,
            "OS_p":     p_os,
            "hi_OS":    m_hi,
            "lo_OS":    m_lo,
            "OS_gap":   m_hi - m_lo
            if not np.isnan(m_hi)
            and not np.isnan(m_lo)
            else np.nan,
        })

    df_genes = pd.DataFrame(gene_rows)
    df_genes.sort_values(
        "OS_p", inplace=True
    )
    df_genes.to_csv(
        os.path.join(
            RESULTS_DIR,
            "gene_os_summary_s8.csv",
        ),
        index=False,
    )
    log(f"\n  Gene OS summary saved: "
        f"gene_os_summary_s8.csv")

# ============================================================
# GENERATE FIGURE
# ============================================================

def generate_figure(
    df_hcc, depth_metab,
    os_time, os_event, hcc_idx,
    clin, mut_results,
    hdac2_res, gse_cdk4_res,
):
    log("")
    log("--- Generating Script 8 figure ---")

    fig = plt.figure(figsize=(30, 26))
    fig.suptitle(
        "HCC — False Attractor Script 8 | "
        "TCGA-LIHC | HDAC2×CDK4 | "
        "HDAC2×PRF1 | CDC20 Model | "
        "OrganismCore | 92h | 2026-03-02",
        fontsize=10, fontweight="bold",
        y=0.99,
    )
    gs_f = gridspec.GridSpec(
        4, 3, figure=fig,
        hspace=0.62, wspace=0.42,
    )

    t   = os_time[hcc_idx]
    e   = os_event[hcc_idx]
    stg = clin["stage"][hcc_idx]
    kmf = KaplanMeierFitter()
    gc  = list(df_hcc.columns)
    C   = [
        "#27ae60","#e74c3c",
        "#2980b9","#8e44ad","#e67e22",
        "#16a085","#c0392b","#2c3e50",
    ]

    def km_panel(ax, groups, title, ci=True):
        for label, ti, ei, col in groups:
            if safe_km(kmf, ti, ei, label):
                kmf.plot_survival_function(
                    ax=ax, color=col,
                    ci_show=ci,
                    ci_alpha=0.10,
                )
        ax.set_title(title, fontsize=9)
        ax.set_xlabel("Months", fontsize=8)
        ax.legend(fontsize=6)
        ax.set_ylim(-0.05, 1.05)

    # ── A: HDAC2 OS Stage III ──────────────────────────────
    ax_a = fig.add_subplot(gs_f[0, 0])
    if hdac2_res and "hi_h" in hdac2_res:
        t_3   = hdac2_res["t_3"]
        e_3   = hdac2_res["e_3"]
        hi_h  = hdac2_res["hi_h"]
        lo_h  = hdac2_res["lo_h"]
        p_h   = hdac2_res["p_h"]
        m_hi_h = hdac2_res["m_hi_h"]
        m_lo_h = hdac2_res["m_lo_h"]
        km_panel(
            ax_a,
            [(f"HDAC2-hi n={hi_h.sum()} "
              f"({m_hi_h:.1f}mo)",
              t_3[hi_h], e_3[hi_h], C[1]),
             (f"HDAC2-lo n={lo_h.sum()} "
              f"({m_lo_h:.1f}mo)",
              t_3[lo_h], e_3[lo_h], C[0])],
            f"A — HDAC2 OS Stage III\n"
            f"{fmt_p(p_h)}  "
            f"gap={abs(m_hi_h-m_lo_h):.1f}mo",
        )

    # ── B: HDAC2 × CDK4 joint Stage III ───────────────────
    ax_b = fig.add_subplot(gs_f[0, 1])
    if (hdac2_res
            and "grp_means" in hdac2_res):
        gm  = hdac2_res["grp_means"]
        t_3 = hdac2_res["t_3"]
        e_3 = hdac2_res["e_3"]
        cols_grp = [C[1],C[4],C[2],C[0]]
        for (lbl, (m_t, mask)), col in zip(
            gm.items(), cols_grp
        ):
            short = lbl.replace(
                "HDAC2-","H"
            ).replace("CDK4-","C")
            if safe_km(
                kmf,
                t_3[mask], e_3[mask],
                f"{short} n={mask.sum()} "
                f"({m_t:.0f}mo)"
            ):
                kmf.plot_survival_function(
                    ax=ax_b, ci_show=False,
                    color=col,
                )
        p_bw = hdac2_res.get("p_bw", np.nan)
        ax_b.set_title(
            f"B — HDAC2×CDK4 Stage III "
            f"(S8-P3)\n{fmt_p(p_bw)}",
            fontsize=9,
        )
        ax_b.set_xlabel("Months", fontsize=8)
        ax_b.legend(fontsize=5.5)
        ax_b.set_ylim(-0.05, 1.05)

    # ── C: HDAC2 × PRF1 joint Stage III ───────────────────
    ax_c = fig.add_subplot(gs_f[0, 2])
    if (hdac2_res
            and "prf_means" in hdac2_res):
        pm  = hdac2_res["prf_means"]
        t_3 = hdac2_res["t_3"]
        e_3 = hdac2_res["e_3"]
        cols_prf = [C[1],C[4],C[7],C[0]]
        for (lbl, (m_t, mask)), col in zip(
            pm.items(), cols_prf
        ):
            short = lbl.replace(
                "HDAC2-","H"
            ).replace("PRF1-","P")
            if safe_km(
                kmf,
                t_3[mask], e_3[mask],
                f"{short} n={mask.sum()} "
                f"({m_t:.0f}mo)"
            ):
                kmf.plot_survival_function(
                    ax=ax_c, ci_show=False,
                    color=col,
                )
        p_prf = hdac2_res.get("p_prf", np.nan)
        ax_c.set_title(
            f"C — HDAC2×PRF1 Stage III "
            f"(S8-P4)\n{fmt_p(p_prf)}",
            fontsize=9,
        )
        ax_c.set_xlabel("Months", fontsize=8)
        ax_c.legend(fontsize=5.5)
        ax_c.set_ylim(-0.05, 1.05)

    # ── D: CTNNB1 / HCC-P5 panel ──────────────────────────
    ax_d = fig.add_subplot(gs_f[1, 0])
    if "CTNNB1" in mut_results:
        res = mut_results["CTNNB1"]
        km_panel(
            ax_d,
            [(f"CTNNB1-mut "
              f"n={res['mmask'].sum()}",
              t[res["mmask"]],
              e[res["mmask"]], C[0]),
             (f"CTNNB1-WT "
              f"n={res['wmask'].sum()}",
              t[res["wmask"]],
              e[res["wmask"]], C[1])],
            f"D — CTNNB1 OS (HCC-P5)\n"
            f"{fmt_p(res['p'])}",
        )
    else:
        ax_d.axis("off")
        ax_d.text(
            0.5, 0.55,
            "D — HCC-P5\nCTNNB1 mut OS",
            ha="center", va="center",
            transform=ax_d.transAxes,
            fontsize=11, fontweight="bold",
        )
        ax_d.text(
            0.5, 0.35,
            "PENDING\nGDC MAF download\nrequired",
            ha="center", va="center",
            transform=ax_d.transAxes,
            fontsize=9,
            bbox=dict(
                boxstyle="round",
                facecolor="#fff3cd",
                edgecolor="#f0ad4e",
            ),
        )
        ax_d.text(
            0.5, 0.12,
            "Expected CTNNB1-mut: n≈111\n"
            "Prediction: mut better OS\n"
            "Literature: Wnt-mut ↑ OS (known)",
            ha="center", va="center",
            transform=ax_d.transAxes,
            fontsize=7,
            color="#555555",
        )

    # ── E: CDK4 GSE14520 KM (if available) ────────────────
    ax_e = fig.add_subplot(gs_f[1, 1])
    if gse_cdk4_res and isinstance(
        gse_cdk4_res, dict
    ) and "hi" in gse_cdk4_res:
        t_g = gse_cdk4_res["t"]
        e_g = gse_cdk4_res["e"]
        km_panel(
            ax_e,
            [(f"CDK4-hi n="
              f"{gse_cdk4_res['hi'].sum()}",
              t_g[gse_cdk4_res["hi"]],
              e_g[gse_cdk4_res["hi"]], C[1]),
             (f"CDK4-lo n="
              f"{gse_cdk4_res['lo'].sum()}",
              t_g[gse_cdk4_res["lo"]],
              e_g[gse_cdk4_res["lo"]], C[0])],
            f"E — CDK4 OS GSE14520 (S8-P6)\n"
            f"{fmt_p(gse_cdk4_res['p_os'])}",
        )
    else:
        ax_e.axis("off")
        ax_e.text(
            0.5, 0.5,
            "E — CDK4 GSE14520\n"
            "NOT TESTABLE\n"
            "(series matrix unavailable)",
            ha="center", va="center",
            transform=ax_e.transAxes,
            fontsize=9,
            bbox=dict(
                boxstyle="round",
                facecolor="#e8f4fd",
            ),
        )

    # ── F: CDC20 KM ────────────────────────────────────────
    ax_f = fig.add_subplot(gs_f[1, 2])
    if "CDC20" in gc:
        cdc20 = df_hcc["CDC20"].values
        valid = (np.isfinite(cdc20)
                 & np.isfinite(t)
                 & np.isfinite(e)
                 & (t > 0))
        t33, t67 = np.percentile(
            cdc20[valid], [33, 67]
        )
        t1_m = valid & (cdc20 <= t33)
        t3_m = valid & (cdc20 > t67)
        p13  = logrank_p(
            t[t1_m], e[t1_m],
            t[t3_m], e[t3_m],
        )
        m1 = t[t1_m].mean() \
            if t1_m.sum() > 0 else np.nan
        m3 = t[t3_m].mean() \
            if t3_m.sum() > 0 else np.nan
        km_panel(
            ax_f,
            [(f"CDC20-hi n={t3_m.sum()} "
              f"({m3:.0f}mo)",
              t[t3_m], e[t3_m], C[1]),
             (f"CDC20-lo n={t1_m.sum()} "
              f"({m1:.0f}mo)",
              t[t1_m], e[t1_m], C[0])],
            f"F — CDC20 OS (tertile)\n"
            f"{fmt_p(p13)}",
        )

    # ── G: HDAC2 vs depth scatter Stage III ───────────────
    ax_g = fig.add_subplot(gs_f[2, 0])
    if "HDAC2" in gc:
        s3     = stg == 3
        h_s3   = df_hcc["HDAC2"].values[s3]
        d_s3   = depth_metab[s3]
        rv, _  = safe_pearsonr(d_s3, h_s3)
        ax_g.scatter(
            d_s3, h_s3,
            alpha=0.5, s=20, c=C[1],
        )
        ax_g.set_xlabel(
            "Metabolic depth (Stage III)",
            fontsize=8,
        )
        ax_g.set_ylabel(
            "HDAC2 (Stage III)", fontsize=8)
        ax_g.set_title(
            f"G — HDAC2 vs depth "
            f"Stage III\nr={rv:+.3f}",
            fontsize=9,
        )

    # ── H: Stage III gene OS heatmap bar ──────────────────
    ax_h = fig.add_subplot(gs_f[2, 1])
    s3    = stg == 3
    t_3   = t[s3]
    e_3   = e[s3]
    focus = [
        "HDAC2","CDK4","BIRC5","CDC20",
        "CCNB1","MKI67","TOP2A","EZH2",
        "PTEN","PRF1","SMARCA4","CD8A",
    ]
    pv_h  = []
    cl_h  = []
    lb_h  = []
    for gene in focus:
        if gene not in gc:
            continue
        gv = df_hcc[gene].values[s3]
        vv = (np.isfinite(gv)
              & np.isfinite(t_3)
              & np.isfinite(e_3)
              & (t_3 > 0))
        if vv.sum() < 10:
            continue
        med = np.nanmedian(gv[vv])
        hi  = vv & (gv >= med)
        lo  = vv & (gv <  med)
        p   = logrank_p(
            t_3[hi], e_3[hi],
            t_3[lo], e_3[lo],
        )
        m_h = t_3[hi].mean() \
            if hi.sum() > 0 else np.nan
        m_l = t_3[lo].mean() \
            if lo.sum() > 0 else np.nan
        if np.isnan(p):
            continue
        pv_h.append(
            -np.log10(max(p, 1e-10))
        )
        cl_h.append(
            C[1] if m_h < m_l else C[0]
        )
        lb_h.append(
            f"{gene}\n({m_h:.0f}/"
            f"{m_l:.0f}mo)"
        )
    if pv_h:
        ax_h.barh(
            range(len(lb_h)),
            pv_h, color=cl_h, alpha=0.8,
        )
        ax_h.axvline(
            -np.log10(0.05),
            color="black",
            linestyle="--", linewidth=1,
        )
        ax_h.set_yticks(range(len(lb_h)))
        ax_h.set_yticklabels(
            lb_h, fontsize=6.5)
        ax_h.set_xlabel(
            "-log10(p)", fontsize=8)
    ax_h.set_title(
        "H — Stage III gene OS\n"
        "(red=worse, green=better)",
        fontsize=9,
    )

    # ── I: Depth OS all stages overlay ────────────────────
    ax_i = fig.add_subplot(gs_f[2, 2])
    for sv, col, ls in [
        (1, C[0], "-"),
        (2, C[2], "-"),
        (3, C[1], "-"),
    ]:
        mask  = stg == sv
        if mask.sum() < 10:
            continue
        t_s   = t[mask]
        e_s   = e[mask]
        d_s   = depth_metab[mask]
        valid = (np.isfinite(t_s)
                 & np.isfinite(e_s)
                 & (t_s > 0))
        med   = np.median(d_s[valid])
        hi    = valid & (d_s >= med)
        lo    = valid & (d_s <  med)
        for lbl, tmask, style in [
            (f"S{sv}deep", hi, "-"),
            (f"S{sv}shal", lo, "--"),
        ]:
            if safe_km(
                kmf, t_s[tmask],
                e_s[tmask], lbl
            ):
                kmf.plot_survival_function(
                    ax=ax_i, color=col,
                    ci_show=False,
                    linestyle=style,
                )
    ax_i.set_title(
        "I — Depth OS by stage\n"
        "(solid=deep, dashed=shallow)",
        fontsize=9,
    )
    ax_i.set_xlabel("Months", fontsize=8)
    ax_i.legend(fontsize=5, ncol=2)
    ax_i.set_ylim(-0.05, 1.05)

    # ── J: HDAC2 all-stage OS ─────────────────────────────
    ax_j = fig.add_subplot(gs_f[3, 0])
    if "HDAC2" in gc:
        hdac2 = df_hcc["HDAC2"].values
        valid = (np.isfinite(hdac2)
                 & np.isfinite(t)
                 & np.isfinite(e)
                 & (t > 0))
        med   = np.nanmedian(hdac2[valid])
        hi    = valid & (hdac2 >= med)
        lo    = valid & (hdac2 <  med)
        p_all = logrank_p(
            t[hi], e[hi], t[lo], e[lo]
        )
        m_hi  = t[hi].mean() \
            if hi.sum() > 0 else np.nan
        m_lo  = t[lo].mean() \
            if lo.sum() > 0 else np.nan
        km_panel(
            ax_j,
            [(f"HDAC2-hi n={hi.sum()} "
              f"({m_hi:.1f}mo)",
              t[hi], e[hi], C[1]),
             (f"HDAC2-lo n={lo.sum()} "
              f"({m_lo:.1f}mo)",
              t[lo], e[lo], C[0])],
            f"J — HDAC2 OS all stages\n"
            f"{fmt_p(p_all)}",
        )

    # ── K: CDC20 by stage ─────────────────────────────────
    ax_k = fig.add_subplot(gs_f[3, 1])
    if "CDC20" in gc:
        cdc20 = df_hcc["CDC20"].values
        for sv, col in [
            (1,C[0]),(2,C[2]),(3,C[1])
        ]:
            mask  = stg == sv
            if mask.sum() < 10:
                continue
            t_s   = t[mask]
            e_s   = e[mask]
            c_s   = cdc20[mask]
            vv    = (np.isfinite(t_s)
                     & np.isfinite(e_s)
                     & np.isfinite(c_s)
                     & (t_s > 0))
            med   = np.nanmedian(c_s[vv])
            hi    = vv & (c_s >= med)
            lo    = vv & (c_s <  med)
            p_s   = logrank_p(
                t_s[hi], e_s[hi],
                t_s[lo], e_s[lo],
            )
            for lbl, tmask, ls in [
                (f"S{sv}hi "
                 f"{fmt_p(p_s)[:9]}",
                 hi, "-"),
                (f"S{sv}lo", lo, "--"),
            ]:
                if safe_km(
                    kmf, t_s[tmask],
                    e_s[tmask], lbl
                ):
                    kmf.plot_survival_function(
                        ax=ax_k, color=col,
                        ci_show=False,
                        linestyle=ls,
                    )
        ax_k.set_title(
            "K — CDC20 OS by stage\n"
            "(solid=hi, dashed=lo)",
            fontsize=9,
        )
        ax_k.set_xlabel("Months", fontsize=8)
        ax_k.legend(fontsize=5, ncol=2)
        ax_k.set_ylim(-0.05, 1.05)

    # ── L: Final summary ──────────────────────────────────
    ax_l = fig.add_subplot(gs_f[3, 2])
    ax_l.axis("off")

    hdac2_s3_p = hdac2_res.get(
        "p_h", np.nan
    ) if hdac2_res else np.nan
    bw_p = hdac2_res.get(
        "p_bw", np.nan
    ) if hdac2_res else np.nan
    ct_p = (mut_results.get(
        "CTNNB1",{}
    ).get("p", np.nan))

    summary = (
        "L — SCRIPT 8 SUMMARY\n"
        "─────────────────────────────\n"
        "PREDICTIONS:\n"
        f"  S8-P1 CTNNB1-mut OS\n"
        f"        {fmt_p(ct_p)}\n"
        f"  S8-P3 HDAC2+CDK4 worst S3\n"
        f"        {fmt_p(bw_p)}\n"
        f"  S8-P4 HDAC2+PRF1-lo worst\n"
        f"  S8-P5 CDC20+HDAC2 beats stg\n"
        f"  S8-P6 CDK4 GSE14520\n"
        f"  S8-P7 HDAC2 HR > CDK4 S3\n\n"
        "LITERATURE CHECK: NEXT\n"
        "Scripts: 8  Documents: 92a-92h\n"
        "Confirmed findings: 19\n"
        "Drug targets: 6\n"
        "Pending: HCC-P5\n\n"
        "OrganismCore | Doc 92h | "
        "2026-03-02"
    )
    ax_l.text(
        0.03, 0.97, summary,
        transform=ax_l.transAxes,
        fontsize=7.5,
        verticalalignment="top",
        fontfamily="monospace",
        bbox=dict(
            boxstyle="round",
            facecolor="#f8f8f8",
            edgecolor="#cccccc",
        ),
    )

    out = os.path.join(
        RESULTS_DIR, "hcc_tcga_s8.png")
    plt.savefig(
        out, dpi=150, bbox_inches="tight")
    log(f"\n  Figure saved: {out}")
    plt.close()

# ============================================================
# MAIN
# ============================================================

def main():
    log("=" * 65)
    log("HEPATOCELLULAR CARCINOMA — SCRIPT 8")
    log("Dataset: TCGA-LIHC (continued)")
    log("Framework: OrganismCore")
    log("Doc: 92h | Date: 2026-03-02")
    log("=" * 65)
    log("")
    log("PREDICTIONS LOCKED 2026-03-02:")
    log("S8-P1: CTNNB1-mut better OS (if MAF)")
    log("S8-P2: TP53-mut worse OS (if MAF)")
    log("S8-P3: HDAC2-hi+CDK4-hi Stage III "
        "worst OS")
    log("S8-P4: HDAC2-hi+PRF1-lo Stage III "
        "worst immune")
    log("S8-P5: CDC20+stage+HDAC2 beats "
        "stage alone")
    log("S8-P6: CDK4-hi worse OS GSE14520")
    log("S8-P7: HDAC2 Cox HR > CDK4 "
        "Stage III")

    # ── Expression ────────────────────────────────────────
    df_hcc, df_all, sample_ids, hcc_idx = (
        parse_expression_tcga(EXPR_FILE)
    )

    # ── Clinical ──────────────────────────────────────────
    clin     = parse_clinical(
        SURV_FILE, PHENO_FILE, sample_ids
    )
    os_time  = clin["os_time"]
    os_event = clin["os_event"]

    # ── MAF ───────────────────────────────────────────────
    mut_matrix = parse_maf(MAF_FILE, sample_ids)

    # ── Depth ─────────────────────────────────────────────
    log("")
    log("=" * 65)
    log("DEPTH SCORE")
    log("=" * 65)
    depth_metab = build_depth(df_hcc)

    # ── S8-1: Mutation survival ───────────────────────────
    mut_results = mutation_survival(
        mut_matrix, os_time, os_event,
        hcc_idx, df_hcc, depth_metab,
    )

    # ── S8-2: HDAC2 Stage III deep-dive ──────────────────
    hdac2_res = hdac2_stage3_analysis(
        df_hcc, depth_metab,
        os_time, os_event,
        hcc_idx, clin,
    )

    # ── S8-3: CDC20 + stage + HDAC2 Cox ──────────────────
    cdc20_hdac2_stage_model(
        df_hcc, depth_metab,
        os_time, os_event,
        hcc_idx, clin,
    )

    # ── S8-4: GSE14520 CDK4 via GEO ──────────────────────
    gse_cdk4_res = gse14520_cdk4_geo()

    # ── S8-5: Final framework summary ─────────────────────
    final_framework_summary(
        df_hcc, depth_metab,
        os_time, os_event,
        hcc_idx, clin,
    )

    # ── Figure ────────────────────────────────────────────
    generate_figure(
        df_hcc, depth_metab,
        os_time, os_event, hcc_idx,
        clin, mut_results,
        hdac2_res, gse_cdk4_res,
    )

    # ── Save ──────────────────────────────────────────────
    pd.DataFrame({
        "sample_id": [
            sample_ids[i] for i in hcc_idx
        ],
        "depth_metabolic": depth_metab,
        "stage":  clin["stage"][hcc_idx],
        "grade":  clin["grade"][hcc_idx],
        "age":    clin["age"][hcc_idx],
        "CTNNB1_mut": (
            mut_matrix["CTNNB1"][hcc_idx]
        ),
        "TP53_mut": (
            mut_matrix["TP53"][hcc_idx]
        ),
    }).to_csv(
        os.path.join(
            RESULTS_DIR, "depth_scores_s8.csv"
        ),
        index=False,
    )

    write_log()
    log(f"\n  Log:    {LOG_FILE}")
    log(f"  Output: {RESULTS_DIR}")
    log("\n=== SCRIPT 8 COMPLETE ===")
    log("")
    log("  Literature check: Document 92h → 92i")
    log("  Compare all confirmed findings to")
    log("  published HCC molecular biology.")
    log("")
    log("Paste full output for Document 92h.")


if __name__ == "__main__":
    main()
