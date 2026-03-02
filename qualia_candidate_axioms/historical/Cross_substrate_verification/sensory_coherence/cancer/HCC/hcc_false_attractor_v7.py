"""
HEPATOCELLULAR CARCINOMA — FALSE ATTRACTOR ANALYSIS
SCRIPT 7
Dataset: TCGA-LIHC (continued)
         GSE14520 (CDK4 reprocessing)
Purpose: Stage III deep-dive,
         CDK4 in GSE14520,
         depth x stage interaction Cox,
         CDKN2A/PTEN investigation,
         PTEN in Deep+Cold,
         HCC-P5 if MAF present

Doc: 92g | Date: 2026-03-02

PREDICTIONS LOCKED 2026-03-02:
  S7-P1: CTNNB1-mut better OS (if MAF)
  S7-P2: CDK4-hi worse OS in Stage III
  S7-P3: Depth x stage interaction
         significant in Cox
  S7-P4: CDK4 probe in GSE14520 and
         CDK4-hi worse OS p<0.05
  S7-P5: PTEN-low enriched in Deep+Cold
  S7-P6: CDKN2A-high co-occurs with
         CDK4-high
  S7-P7: Depth predicts OS within
         Stage III (p<0.05)

Author: Eric Robert Lawson
Framework: OrganismCore
"""

import os
import re
import gzip
import json
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
RESULTS_DIR = os.path.join(BASE_DIR, "results_s7")
LOG_FILE    = os.path.join(RESULTS_DIR,
                           "analysis_log_s7.txt")
os.makedirs(TCGA_DIR,    exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

EXPR_FILE  = os.path.join(
    TCGA_DIR, "TCGA-LIHC.expr.tsv.gz")
SURV_FILE  = os.path.join(
    TCGA_DIR, "TCGA-LIHC.survival.tsv.gz")
PHENO_FILE = os.path.join(
    TCGA_DIR, "TCGA-LIHC.pheno.tsv.gz")
MAF_FILE   = os.path.join(
    TCGA_DIR, "TCGA-LIHC.maf.gz")

# GSE14520 — all plausible paths
GSE_EXPR_PATHS = [
    os.path.join(GSE_DIR,
                 "GSE14520_expr.tsv.gz"),
    os.path.join(GSE_DIR,
                 "gse14520_expression.csv.gz"),
    os.path.join(GSE_DIR,
                 "gse14520_expr.csv"),
    os.path.join(GSE_DIR,
                 "GSE14520_series_matrix.txt.gz"),
]
GSE_SCORE_PATHS = [
    os.path.join(BASE_DIR, "results_s2",
                 "depth_scores_s2.csv"),
    os.path.join(BASE_DIR, "results_s1",
                 "depth_scores_s1.csv"),
]

GDC_BASE = "https://api.gdc.cancer.gov"

# CDK4 Affymetrix probe IDs on GPL3921
# (HG-U133A / HG-U133 Plus 2.0)
CDK4_PROBES = [
    "204541_at",   # primary CDK4 probe
    "204542_s_at", # secondary
    "1592_at",     # older annotation
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
    "PTEN","IDH2","CDH1","PRF1",
    "CDC20","BIRC5","CCNB1","APOB",
]

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

# ============================================================
# STAGE / GRADE MAPS
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
    "":np.nan, "--":np.nan,
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
AGE_COLS = {
    "age",
    "age_at_initial_pathologic_diagnosis",
    "age_at_diagnosis","age_at_index",
    "age_at_procurement","patient_age",
    "age_diag",
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
    tumour = ((stype == "01") | np.array([
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
    gender   = [""] * n

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
                            "_sample_id","sampleid",
                            "submitter_id",
                            "case_submitter_id",
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
                            "event","status",
                        ] and "ec" not in cols:
                            cols["ec"] = i
                        if any(x in h for x in [
                            "stage","ajcc_pathol",
                            "tumor_stage",
                            "clinical_stage",
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
                        if h in [
                            "gender","sex",
                        ] and "genc" not in cols:
                            cols["genc"] = i
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
                gnv = get("genc")
                if gnv and not gender[idx]:
                    gender[idx] = gnv

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
    log(f"  Age valid: {len(av)}  "
        f"mean={av.mean():.1f}" if len(av) else
        f"  Age valid: 0")

    return {
        "os_time":   os_time,
        "os_event":  os_event,
        "stage":     stage_num,
        "grade":     grade_num,
        "age":       age,
        "gender":    np.array(gender),
    }

# ============================================================
# PARSE MAF
# ============================================================

def parse_maf(maf_file, sample_ids):
    log("")
    log("=" * 65)
    log("PARSE MAF")
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
        _maf_instructions(maf_file)
        return mut_matrix

    sz = os.path.getsize(maf_file)
    log(f"  {maf_file} ({sz:,} bytes)")

    if sz < 10000:
        log(f"  MAF too small ({sz}b).")
        log("  This file contains only "
            "header rows — not a full MAF.")
        _maf_instructions(maf_file)
        return mut_matrix

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
                        "gene_name",
                    ] and gene_c is None):
                        gene_c = i
                    if (any(x in hl for x in [
                        "tumor_sample_barcode",
                        "tumor_sample","sampleid",
                        "sample_id",
                    ]) and sample_c is None):
                        sample_c = i
                    if (any(x in hl for x in [
                        "variant_classification",
                        "consequence","effect",
                        "mutation_type",
                    ]) and effect_c is None):
                        effect_c = i
                log(f"  Headers: {hdr[:8]}")
                log(f"  gene={gene_c} "
                    f"sample={sample_c} "
                    f"effect={effect_c}")
                continue

            if (gene_c is None
                    or sample_c is None):
                continue
            if max(gene_c, sample_c) >= len(parts):
                continue

            gene = parts[gene_c].strip()
            if gene not in gene_set:
                continue

            idx = match_sid(
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

    log(f"  Mutations parsed: {n_muts}")
    if n_muts > 0:
        log(f"\n  {'Gene':<14} {'n':>5} {'%':>8}")
        log(f"  {'-'*30}")
        for g in MUT_GENES:
            freq = mut_matrix[g].sum()
            if freq > 0:
                log(f"  {g:<14} {freq:>5} "
                    f"{100*freq/n:>8.1f}%")
    return mut_matrix


def _maf_instructions(maf_file):
    log("")
    log("  " + "=" * 40)
    log("  MANUAL MAF DOWNLOAD — FINAL NOTICE")
    log("  HCC-P5 has been pending 7 scripts.")
    log("  " + "=" * 40)
    log("  1. Open:")
    log("     https://portal.gdc.cancer.gov"
        "/repository")
    log("  2. Left panel — apply filters:")
    log("     Project:  TCGA-LIHC")
    log("     Data Category: "
        "Simple Nucleotide Variation")
    log("     Data Type: "
        "Masked Somatic Mutation")
    log("     Experimental Strategy: WXS")
    log("     Access: Open")
    log("  3. One file appears (~3-10 MB)")
    log("     Filename contains 'mutect2'")
    log("  4. Click filename → Download")
    log("  5. Rename/move to:")
    log(f"     {maf_file}")
    log("  6. Re-run this script.")
    log("  CTNNB1 result will be first "
        "output block.")
    log("  " + "=" * 40)

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
    log(f"  n={n}  mean={d.mean():.4f}  "
        f"std={d.std():.4f}")
    return d

# ============================================================
# S7-1: MUTATION SURVIVAL
# ============================================================

def mutation_survival(
    mut_matrix, os_time, os_event,
    hcc_idx, df_hcc, depth_metab,
):
    log("")
    log("=" * 65)
    log("S7-1: MUTATION SURVIVAL (HCC-P5)")
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
            "7 scripts.")
        return {}

    results = {}
    log(f"\n  {'Gene':<12} {'n_mut':>6} "
        f"{'mut_OS':>9} {'wt_OS':>9}  "
        f"logrank       dir  depth_mut  depth_wt")
    log(f"  {'-'*80}")

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
        direction = (
            "↑better" if m_m > m_w
            else "↑worse"
        )
        log(f"  {gene:<12} {n_mut:>6} "
            f"{m_m:>9.1f} {m_w:>9.1f}  "
            f"{fmt_p(p)}  {direction}  "
            f"{d_m:>9.4f}  {d_w:>8.4f}")

        results[gene] = {
            "n_mut":  n_mut,
            "mmask":  mm,
            "wmask":  wm,
            "p":      p,
            "m_mut":  m_m,
            "m_wt":   m_w,
            "d_mut":  d_m,
            "d_wt":   d_w,
        }

    log("")
    for gene, better, label in [
        ("CTNNB1", True,
         "S7-P1: CTNNB1-mut better OS (HCC-P5)"),
        ("TP53",   False,
         "S7-P1: TP53-mut worse OS"),
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

    # CTNNB1 vs TP53 depth
    if "CTNNB1" in results and "TP53" in results:
        d_ct = results["CTNNB1"]["d_mut"]
        d_tp = results["TP53"]["d_mut"]
        conf = (not np.isnan(d_ct)
                and not np.isnan(d_tp)
                and d_ct < d_tp)
        log(f"\n  CTNNB1-mut depth={d_ct:.4f}  "
            f"TP53-mut depth={d_tp:.4f}")
        log(f"  CTNNB1-mut shallower than "
            f"TP53-mut: "
            f"{'YES ✓' if conf else 'NO ✗'}")

    return results

# ============================================================
# S7-2: DEPTH × STAGE INTERACTION COX
# ============================================================

def depth_stage_interaction(
    depth_metab, os_time, os_event,
    hcc_idx, clin,
):
    log("")
    log("=" * 65)
    log("S7-2: DEPTH × STAGE INTERACTION")
    log("S7-P3: Interaction term significant")
    log("=" * 65)

    t   = os_time[hcc_idx]
    e   = os_event[hcc_idx]
    stg = clin["stage"][hcc_idx]
    ag  = clin["age"][hcc_idx]

    # Create interaction term
    # Standardise depth and stage first
    d_std = np.full_like(depth_metab, np.nan)
    s_std = np.full_like(stg, np.nan)

    valid = (np.isfinite(depth_metab)
             & np.isfinite(stg))
    if valid.sum() > 0:
        d_mean = depth_metab[valid].mean()
        d_sd   = depth_metab[valid].std()
        s_mean = stg[valid].mean()
        s_sd   = stg[valid].std()
        if d_sd > 0:
            d_std = (depth_metab - d_mean) / d_sd
        if s_sd > 0:
            s_std = (stg - s_mean) / s_sd

    interaction = d_std * s_std

    log(f"  Interaction term n_valid="
        f"{np.isfinite(interaction).sum()}")

    def run_cox(df_c, label):
        log(f"\n  {label}:")
        try:
            dc = df_c.copy().dropna()
            dc = dc[dc["T"] > 0]
            if len(dc) < 20:
                log(f"  Skipped: n={len(dc)}")
                return None
            log(f"  n={len(dc)}")
            # Do NOT re-standardise
            # interaction term columns —
            # they are already on a
            # meaningful scale
            cph = CoxPHFitter(
                penalizer=0.1
            )
            cph.fit(dc, "T", "E")
            log(cph.summary[
                ["coef","exp(coef)","p"]
            ].to_string())
            return cph
        except Exception as ex:
            log(f"  Error: {ex}")
            return None

    # Model A: depth + stage (no interaction)
    cph_a = run_cox(
        pd.DataFrame({
            "T":     t,
            "E":     e,
            "depth": d_std,
            "stage": s_std,
        }),
        "Model A: depth + stage "
        "(standardised)",
    )

    # Model B: depth + stage + interaction
    cph_b = run_cox(
        pd.DataFrame({
            "T":           t,
            "E":           e,
            "depth":       d_std,
            "stage":       s_std,
            "depth_x_stg": interaction,
        }),
        "Model B: depth + stage + "
        "depth×stage",
    )

    # Model C: + age
    cph_c = run_cox(
        pd.DataFrame({
            "T":           t,
            "E":           e,
            "depth":       d_std,
            "stage":       s_std,
            "depth_x_stg": interaction,
            "age":         ag,
        }),
        "Model C: depth + stage + "
        "interaction + age",
    )

    # S7-P3 check
    if cph_b and "depth_x_stg" in \
            cph_b.summary.index:
        p_int = cph_b.summary.loc[
            "depth_x_stg","p"
        ]
        hr_int = cph_b.summary.loc[
            "depth_x_stg","exp(coef)"
        ]
        conf = (not np.isnan(p_int)
                and p_int < 0.05)
        log(f"\n  S7-P3: Depth×stage "
            f"interaction significant")
        log(f"  HR(interaction)={hr_int:.4f}  "
            f"{fmt_p(p_int)}")
        log(f"  STATUS: "
            f"{'CONFIRMED ✓' if conf else 'NOT CONFIRMED ✗'}")
        log(f"  (positive HR = depth is more "
            f"harmful at higher stage)")

    # Sensitivity: depth OS by stage
    # using continuous stage interaction
    log(f"\n  Depth effect stratified by stage:")
    log(f"  {'Stage':<10} {'n':>5}  "
        f"depth_OS_p   deep_OS  shal_OS")
    log(f"  {'-'*52}")
    for sv in [1, 2, 3]:
        mask  = stg == sv
        n_s   = int(mask.sum())
        if n_s < 10:
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
        p_s   = logrank_p(
            t_s[hi], e_s[hi],
            t_s[lo], e_s[lo],
        )
        m_hi  = t_s[hi].mean() \
            if hi.sum() > 0 else np.nan
        m_lo  = t_s[lo].mean() \
            if lo.sum() > 0 else np.nan
        log(f"  Stage {sv:<5} {n_s:>5}  "
            f"{fmt_p(p_s)}  "
            f"{m_hi:>7.1f}  {m_lo:>7.1f}")

    return cph_b

# ============================================================
# S7-3: STAGE III DEEP-DIVE
# ============================================================

def stage3_deep_dive(
    df_hcc, depth_metab, os_time, os_event,
    hcc_idx, clin, mut_matrix,
):
    log("")
    log("=" * 65)
    log("S7-3: STAGE III DEEP-DIVE")
    log("S7-P2: CDK4-hi worse OS Stage III")
    log("S7-P7: Depth OS Stage III p<0.05")
    log("=" * 65)

    t   = os_time[hcc_idx]
    e   = os_event[hcc_idx]
    stg = clin["stage"][hcc_idx]
    grd = clin["grade"][hcc_idx]
    gc  = list(df_hcc.columns)

    s3 = stg == 3
    log(f"  Stage III: n={s3.sum()}")

    t_3 = t[s3]
    e_3 = e[s3]
    d_3 = depth_metab[s3]

    # Depth OS in Stage III
    valid3 = (np.isfinite(t_3)
              & np.isfinite(e_3)
              & (t_3 > 0))
    med3   = np.median(d_3[valid3])
    hi3    = valid3 & (d_3 >= med3)
    lo3    = valid3 & (d_3 <  med3)
    p_d3   = logrank_p(
        t_3[hi3], e_3[hi3],
        t_3[lo3], e_3[lo3],
    )
    m_hi3  = t_3[hi3].mean() \
        if hi3.sum() > 0 else np.nan
    m_lo3  = t_3[lo3].mean() \
        if lo3.sum() > 0 else np.nan

    log(f"\n  Depth OS Stage III:")
    log(f"  deep={m_hi3:.1f}mo  "
        f"shallow={m_lo3:.1f}mo  "
        f"{fmt_p(p_d3)}")
    conf_p7 = (not np.isnan(m_hi3)
               and not np.isnan(m_lo3)
               and m_hi3 < m_lo3
               and not np.isnan(p_d3)
               and p_d3 < 0.05)
    log(f"  S7-P7: Depth OS Stage III p<0.05")
    log(f"  STATUS: "
        f"{'CONFIRMED ✓' if conf_p7 else 'DIRECTIONAL ✓' if m_hi3 < m_lo3 else 'NOT CONFIRMED ✗'}")

    # Stage III depth tertiles
    if valid3.sum() >= 15:
        t33, t67 = np.percentile(
            d_3[valid3], [33, 67]
        )
        t3_1 = valid3 & (d_3 <= t33)
        t3_2 = (valid3 & (d_3 > t33)
                & (d_3 <= t67))
        t3_3 = valid3 & (d_3 > t67)
        log(f"\n  Stage III depth tertiles:")
        for tlbl, tmask in [
            ("T1 shallow", t3_1),
            ("T2 mid",     t3_2),
            ("T3 deep",    t3_3),
        ]:
            vm = tmask & np.isfinite(t_3) \
                & np.isfinite(e_3)
            m  = t_3[vm].mean() \
                if vm.sum() > 0 else np.nan
            log(f"  {tlbl}: n={tmask.sum()} "
                f"OS={m:.1f}mo")
        p_t13 = logrank_p(
            t_3[t3_1], e_3[t3_1],
            t_3[t3_3], e_3[t3_3],
        )
        log(f"  T3 vs T1: {fmt_p(p_t13)}")

    # CDK4 OS in Stage III
    log(f"\n  Key gene OS in Stage III:")
    log(f"  {'Gene':<12} {'n':>5}  "
        f"OS_p           hi_OS  lo_OS  dir")
    log(f"  {'-'*60}")

    stage3_gene_results = {}
    focus = [
        "CDK4","CDC20","BIRC5","CCNB1",
        "EZH2","HDAC2","MKI67","TOP2A",
        "SMARCA4","TWIST1","PTEN","CDKN2A",
        "CD8A","PRF1","VIM","AFP",
    ]
    for gene in focus:
        if gene not in gc:
            continue
        gv_3 = df_hcc[gene].values[s3]
        valid = (np.isfinite(gv_3)
                 & np.isfinite(t_3)
                 & np.isfinite(e_3)
                 & (t_3 > 0))
        if valid.sum() < 10:
            continue
        med   = np.nanmedian(gv_3[valid])
        hi    = valid & (gv_3 >= med)
        lo    = valid & (gv_3 <  med)
        p_os  = logrank_p(
            t_3[hi], e_3[hi],
            t_3[lo], e_3[lo],
        )
        m_hi  = t_3[hi].mean() \
            if hi.sum() > 0 else np.nan
        m_lo  = t_3[lo].mean() \
            if lo.sum() > 0 else np.nan
        direction = (
            "↑=worse"
            if m_hi < m_lo
            else "↑=better"
        )
        log(f"  {gene:<12} {valid.sum():>5}  "
            f"{fmt_p(p_os)}  "
            f"{m_hi:>6.1f}  {m_lo:>6.1f}  "
            f"{direction}")
        stage3_gene_results[gene] = {
            "p":    p_os,
            "m_hi": m_hi,
            "m_lo": m_lo,
            "hi":   hi,
            "lo":   lo,
            "t_3":  t_3,
            "e_3":  e_3,
        }

    # S7-P2 check
    if "CDK4" in stage3_gene_results:
        res  = stage3_gene_results["CDK4"]
        conf = (not np.isnan(res["m_hi"])
                and not np.isnan(res["m_lo"])
                and res["m_hi"] < res["m_lo"])
        sig  = (not np.isnan(res["p"])
                and res["p"] < 0.05)
        log(f"\n  S7-P2: CDK4-hi worse OS "
            f"Stage III")
        log(f"  CDK4-hi={res['m_hi']:.1f}mo  "
            f"CDK4-lo={res['m_lo']:.1f}mo  "
            f"{fmt_p(res['p'])}")
        log(f"  STATUS: "
            f"{'CONFIRMED ✓' if conf and sig else 'DIRECTIONAL ✓' if conf else 'NOT CONFIRMED ✗'}")

    # Cox within Stage III
    log(f"\n  Cox within Stage III:")
    try:
        cdk4_3 = df_hcc["CDK4"].values[s3] \
            if "CDK4" in gc else None
        dc = pd.DataFrame({
            "T":     t_3,
            "E":     e_3,
            "depth": d_3,
        })
        if cdk4_3 is not None:
            dc["CDK4"] = cdk4_3
        dc = dc.dropna()
        dc = dc[dc["T"] > 0]
        if len(dc) >= 20:
            for col in ["depth","CDK4"]:
                if col not in dc.columns:
                    continue
                sd = dc[col].std()
                if sd > 0:
                    dc[col] = (
                        (dc[col] - dc[col].mean())
                        / sd
                    )
            cph = CoxPHFitter()
            cph.fit(dc, "T", "E")
            log(f"  n={len(dc)}")
            log(cph.summary[
                ["coef","exp(coef)","p"]
            ].to_string())
    except Exception as ex:
        log(f"  Cox Stage III error: {ex}")

    return stage3_gene_results, hi3, lo3, t_3, e_3

# ============================================================
# S7-4: CDKN2A / PTEN INVESTIGATION
# ============================================================

def cdkn2a_pten_analysis(
    df_hcc, depth_metab, os_time, os_event,
    hcc_idx, clin,
):
    log("")
    log("=" * 65)
    log("S7-4: CDKN2A / PTEN INVESTIGATION")
    log("S7-P5: PTEN-low enriched in Deep+Cold")
    log("S7-P6: CDKN2A-high co-occurs with "
        "CDK4-high")
    log("=" * 65)

    t   = os_time[hcc_idx]
    e   = os_event[hcc_idx]
    gc  = list(df_hcc.columns)

    # Rebuild exhaustion score for deep+cold
    ex_genes = [g for g in EXHAUSTION_GENES
                if g in gc]
    ex_score = norm01(
        np.nanmean(
            df_hcc[ex_genes].values, axis=1
        )
    ) if len(ex_genes) >= 3 else np.zeros(
        len(df_hcc)
    )

    valid_d = np.isfinite(depth_metab)
    med_d   = np.median(depth_metab[valid_d])
    med_ex  = np.median(ex_score[valid_d])
    deep_cold = ((depth_metab >= med_d)
                 & (ex_score < med_ex))
    deep_hot  = ((depth_metab >= med_d)
                 & (ex_score >= med_ex))
    shallow   = depth_metab < med_d

    log(f"\n  Deep+Cold n={deep_cold.sum()}")
    log(f"  Deep+Hot  n={deep_hot.sum()}")
    log(f"  Shallow   n={shallow.sum()}")

    # CDKN2A analysis
    log(f"\n  CDKN2A analysis:")
    if "CDKN2A" in gc:
        cdkn2a = df_hcc["CDKN2A"].values

        # Correlation with depth
        rv_d, pv_d = safe_pearsonr(
            depth_metab, cdkn2a
        )
        log(f"  r(depth, CDKN2A) = "
            f"{rv_d:+.4f}  {fmt_p(pv_d)}")

        # Correlation with CDK4
        if "CDK4" in gc:
            cdk4 = df_hcc["CDK4"].values
            rv_c, pv_c = safe_pearsonr(
                cdk4, cdkn2a
            )
            log(f"  r(CDK4, CDKN2A) = "
                f"{rv_c:+.4f}  {fmt_p(pv_c)}")

            # S7-P6: co-occurrence
            conf_p6 = (not np.isnan(rv_c)
                       and rv_c > 0.2)
            log(f"\n  S7-P6: CDKN2A-high co-occurs "
                f"with CDK4-high")
            log(f"  r={rv_c:+.4f}  "
                f"(positive = co-expression)")
            log(f"  STATUS: "
                f"{'CONFIRMED ✓' if conf_p6 else 'NOT CONFIRMED ✗'}")

            # Quadrant analysis
            med_cdk4   = np.nanmedian(cdk4)
            med_cdkn2a = np.nanmedian(cdkn2a)
            both_hi = ((cdk4 >= med_cdk4)
                       & (cdkn2a >= med_cdkn2a))
            both_lo = ((cdk4 < med_cdk4)
                       & (cdkn2a < med_cdkn2a))
            cdk4_hi_cdkn2a_lo = (
                (cdk4 >= med_cdk4)
                & (cdkn2a < med_cdkn2a)
            )
            log(f"\n  CDK4/CDKN2A quadrants:")
            log(f"  CDK4-hi + CDKN2A-hi: "
                f"n={both_hi.sum()}")
            log(f"  CDK4-hi + CDKN2A-lo: "
                f"n={cdk4_hi_cdkn2a_lo.sum()}")
            log(f"  CDK4-lo + CDKN2A-lo: "
                f"n={both_lo.sum()}")

            # OS of worst quadrant
            valid = (np.isfinite(t)
                     & np.isfinite(e)
                     & (t > 0))
            for lbl, mask in [
                ("CDK4-hi+CDKN2A-hi",
                 both_hi),
                ("CDK4-hi+CDKN2A-lo",
                 cdk4_hi_cdkn2a_lo),
                ("CDK4-lo+CDKN2A-lo",
                 both_lo),
            ]:
                vm  = mask & valid
                m_t = t[vm].mean() \
                    if vm.sum() > 0 else np.nan
                n_e = int(e[vm].sum()) \
                    if vm.sum() > 0 else 0
                log(f"  {lbl}: "
                    f"n={vm.sum()}  "
                    f"OS={m_t:.1f}mo  "
                    f"ev={n_e}")

    # PTEN analysis
    log(f"\n  PTEN analysis:")
    if "PTEN" in gc:
        pten = df_hcc["PTEN"].values
        rv_d, pv_d = safe_pearsonr(
            depth_metab, pten
        )
        log(f"  r(depth, PTEN) = "
            f"{rv_d:+.4f}  {fmt_p(pv_d)}")

        # PTEN in Deep+Cold vs Deep+Hot
        pten_dc = pten[deep_cold]
        pten_dh = pten[deep_hot]
        pten_sh = pten[shallow]
        m_dc = pten_dc[
            np.isfinite(pten_dc)
        ].mean() if np.isfinite(
            pten_dc
        ).sum() > 0 else np.nan
        m_dh = pten_dh[
            np.isfinite(pten_dh)
        ].mean() if np.isfinite(
            pten_dh
        ).sum() > 0 else np.nan
        m_sh = pten_sh[
            np.isfinite(pten_sh)
        ].mean() if np.isfinite(
            pten_sh
        ).sum() > 0 else np.nan

        _, p_dc_dh = safe_mwu(pten_dc, pten_dh)
        _, p_dc_sh = safe_mwu(pten_dc, pten_sh)

        log(f"  PTEN by subgroup:")
        log(f"  Deep+Cold: {m_dc:.4f}")
        log(f"  Deep+Hot:  {m_dh:.4f}")
        log(f"  Shallow:   {m_sh:.4f}")
        log(f"  Deep+Cold vs Deep+Hot: "
            f"{fmt_p(p_dc_dh)}")
        log(f"  Deep+Cold vs Shallow: "
            f"{fmt_p(p_dc_sh)}")

        conf_p5 = (not np.isnan(m_dc)
                   and not np.isnan(m_dh)
                   and m_dc < m_dh)
        log(f"\n  S7-P5: PTEN-low enriched "
            f"in Deep+Cold")
        log(f"  (PTEN Deep+Cold < Deep+Hot: "
            f"{'YES ✓' if conf_p5 else 'NO ✗'})")
        log(f"  STATUS: "
            f"{'CONFIRMED ✓' if conf_p5 else 'NOT CONFIRMED ✗'}")

        # PTEN Cox
        log(f"\n  PTEN Cox with depth:")
        try:
            valid = (np.isfinite(t)
                     & np.isfinite(e)
                     & (t > 0)
                     & np.isfinite(pten)
                     & np.isfinite(depth_metab))
            dc = pd.DataFrame({
                "T":     t[valid],
                "E":     e[valid],
                "depth": depth_metab[valid],
                "PTEN":  pten[valid],
            })
            for col in ["depth","PTEN"]:
                sd = dc[col].std()
                if sd > 0:
                    dc[col] = (
                        (dc[col] - dc[col].mean())
                        / sd
                    )
            cph = CoxPHFitter()
            cph.fit(dc, "T", "E")
            log(f"  n={len(dc)}")
            log(cph.summary[
                ["coef","exp(coef)","p"]
            ].to_string())
        except Exception as ex:
            log(f"  Error: {ex}")

# ============================================================
# S7-5: CDK4 IN GSE14520 REPROCESSING
# ============================================================

def cdk4_gse14520_reprocess():
    log("")
    log("=" * 65)
    log("S7-5: CDK4 IN GSE14520")
    log("S7-P4: CDK4-hi worse OS GSE14520")
    log("=" * 65)

    # Search all plausible expression files
    for fp in GSE_EXPR_PATHS:
        if not os.path.exists(fp):
            log(f"  Not found: {fp}")
            continue

        log(f"  Checking: {fp}")
        sz = os.path.getsize(fp)
        log(f"  Size: {sz:,} bytes")

        # Check first 2000 lines for CDK4
        # or CDK4 probe IDs
        opener = (
            gzip.open(fp, "rt",
                      encoding="utf-8",
                      errors="ignore")
            if fp.endswith(".gz")
            else open(fp, "r",
                      encoding="utf-8",
                      errors="ignore")
        )
        found_cdk4 = False
        header_line = None
        cdk4_data   = None

        with opener as f:
            for i, raw in enumerate(f):
                line = raw.rstrip("\n")
                parts = [
                    p.strip().strip('"')
                    for p in line.split(
                        "\t" if "\t" in line
                        else ","
                    )
                ]
                if i == 0:
                    header_line = parts
                    continue
                row_id = parts[0].strip()
                # Check for CDK4 by gene name
                # or by probe ID
                if (row_id == "CDK4"
                        or row_id in CDK4_PROBES):
                    log(f"  Found CDK4 row: "
                        f"'{row_id}'")
                    found_cdk4 = True
                    try:
                        cdk4_data = [
                            float(p)
                            if p not in [
                                "","NA","nan",
                                "NaN","NULL",
                            ]
                            else np.nan
                            for p in parts[1:]
                        ]
                    except (ValueError,
                            TypeError):
                        pass
                    break
                if i > 50000:
                    break

        if not found_cdk4 or cdk4_data is None:
            log(f"  CDK4 not found in {fp}")
            continue

        log(f"  CDK4 data: n={len(cdk4_data)} "
            f"values")

        # Load corresponding survival
        # data from score file
        for score_fp in GSE_SCORE_PATHS:
            if not os.path.exists(score_fp):
                continue
            df_s = pd.read_csv(score_fp)
            log(f"  Score file: {score_fp} "
                f"({df_s.shape})")

            n_cdk4 = len(cdk4_data)
            n_sc   = len(df_s)
            if n_cdk4 != n_sc:
                log(f"  Length mismatch: "
                    f"CDK4={n_cdk4} "
                    f"scores={n_sc}")
                continue

            # Check survival columns
            if "os_time" not in df_s.columns \
                    and "OS.time" not in \
                    df_s.columns:
                log(f"  No survival in "
                    f"{score_fp}")
                continue

            cdk4_arr = np.array(cdk4_data)
            t_col    = (
                "os_time"
                if "os_time" in df_s.columns
                else "OS.time"
            )
            e_col    = (
                "os_event"
                if "os_event" in df_s.columns
                else "OS"
            )
            t_arr    = df_s[t_col].values
            e_arr    = df_s[e_col].values

            # Convert days to months if needed
            if np.nanmedian(t_arr) > 200:
                t_arr = t_arr / 30.44

            valid   = (np.isfinite(cdk4_arr)
                       & np.isfinite(t_arr)
                       & np.isfinite(e_arr)
                       & (t_arr > 0))
            log(f"  Valid: {valid.sum()}")

            if valid.sum() < 20:
                log("  Too few valid samples")
                continue

            # OS analysis
            med   = np.nanmedian(
                cdk4_arr[valid]
            )
            hi    = valid & (cdk4_arr >= med)
            lo    = valid & (cdk4_arr <  med)
            p_os  = logrank_p(
                t_arr[hi], e_arr[hi],
                t_arr[lo], e_arr[lo],
            )
            m_hi  = t_arr[hi].mean() \
                if hi.sum() > 0 else np.nan
            m_lo  = t_arr[lo].mean() \
                if lo.sum() > 0 else np.nan

            # Depth correlation
            depth_col = (
                "depth_s2_metabolic"
                if "depth_s2_metabolic"
                in df_s.columns
                else "depth_combined"
                if "depth_combined"
                in df_s.columns
                else None
            )
            if depth_col:
                d_arr   = df_s[depth_col].values
                rv, pv  = safe_pearsonr(
                    d_arr, cdk4_arr
                )
                log(f"\n  CDK4 RESULTS — GSE14520:")
                log(f"  r(depth, CDK4) = "
                    f"{rv:+.4f}  {fmt_p(pv)}")
            else:
                log(f"\n  CDK4 RESULTS — GSE14520:")

            log(f"  OS: {fmt_p(p_os)}")
            log(f"  CDK4-hi={m_hi:.1f}mo  "
                f"CDK4-lo={m_lo:.1f}mo")

            conf = (not np.isnan(m_hi)
                    and not np.isnan(m_lo)
                    and m_hi < m_lo)
            sig  = (not np.isnan(p_os)
                    and p_os < 0.05)
            log(f"\n  S7-P4: CDK4-hi worse OS "
                f"in GSE14520")
            log(f"  STATUS: "
                f"{'CONFIRMED ✓' if conf and sig else 'DIRECTIONAL ✓' if conf else 'NOT CONFIRMED ✗'}")
            return True

    log("  CDK4 not found in any "
        "GSE14520 file.")
    log("  S7-P4: NOT TESTABLE")
    log("  GSE14520 must be reprocessed "
        "with CDK4 added.")
    log("  CDK4 Affymetrix probe "
        "(GPL3921): 204541_at")
    return False

# ============================================================
# S7-6: CDC20 DEEP-DIVE
# ============================================================

def cdc20_analysis(
    df_hcc, depth_metab, os_time, os_event,
    hcc_idx, clin,
):
    log("")
    log("=" * 65)
    log("S7-6: CDC20 — STRONGEST OS PREDICTOR")
    log("p=2.57e-07  r(depth)=+0.677")
    log("=" * 65)

    t   = os_time[hcc_idx]
    e   = os_event[hcc_idx]
    stg = clin["stage"][hcc_idx]
    gc  = list(df_hcc.columns)

    if "CDC20" not in gc:
        log("  CDC20 not in matrix")
        return {}

    cdc20 = df_hcc["CDC20"].values
    rv, pv = safe_pearsonr(depth_metab, cdc20)
    log(f"  r(depth, CDC20) = {rv:+.4f}  "
        f"{fmt_p(pv)}")

    valid = (np.isfinite(cdc20)
             & np.isfinite(t)
             & np.isfinite(e)
             & (t > 0))

    # Tertile
    t33, t67 = np.percentile(
        cdc20[valid], [33, 67]
    )
    t1 = valid & (cdc20 <= t33)
    t2 = (valid & (cdc20 > t33)
          & (cdc20 <= t67))
    t3 = valid & (cdc20 > t67)
    p13 = logrank_p(
        t[t1], e[t1], t[t3], e[t3]
    )
    log(f"\n  CDC20 tertile OS:")
    for tlbl, tmask in [
        ("T1 low",  t1),
        ("T2 mid",  t2),
        ("T3 high", t3),
    ]:
        vm = tmask & np.isfinite(t) \
            & np.isfinite(e)
        m  = t[vm].mean() \
            if vm.sum() > 0 else np.nan
        log(f"  {tlbl}: n={tmask.sum()} "
            f"OS={m:.1f}mo")
    log(f"  T3 vs T1: {fmt_p(p13)}")

    # Stage-stratified CDC20
    log(f"\n  CDC20 OS by stage:")
    for sv in [1, 2, 3]:
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
        m_hi  = t_s[hi].mean() \
            if hi.sum() > 0 else np.nan
        m_lo  = t_s[lo].mean() \
            if lo.sum() > 0 else np.nan
        log(f"  Stage {sv}: {fmt_p(p_s)}  "
            f"hi={m_hi:.1f}mo  lo={m_lo:.1f}mo")

    # Cox: CDC20 vs depth
    log(f"\n  Cox: CDC20 + depth:")
    try:
        dc = pd.DataFrame({
            "T":     t,
            "E":     e,
            "CDC20": cdc20,
            "depth": depth_metab,
        }).dropna()
        dc = dc[dc["T"] > 0]
        for col in ["CDC20","depth"]:
            sd = dc[col].std()
            if sd > 0:
                dc[col] = (
                    (dc[col] - dc[col].mean())
                    / sd
                )
        cph = CoxPHFitter()
        cph.fit(dc, "T", "E")
        log(f"  n={len(dc)}")
        log(cph.summary[
            ["coef","exp(coef)","p"]
        ].to_string())
    except Exception as ex:
        log(f"  Error: {ex}")

    return {"t1": t1, "t3": t3}

# ============================================================
# GENERATE FIGURE
# ============================================================

def generate_figure(
    df_hcc, depth_metab,
    os_time, os_event, hcc_idx,
    clin, mut_results,
    stage3_gene_res, hi3, lo3, t_3, e_3,
    cdc20_res,
):
    log("")
    log("--- Generating Script 7 figure ---")

    fig = plt.figure(figsize=(30, 26))
    fig.suptitle(
        "HCC — False Attractor Script 7 | "
        "TCGA-LIHC | Stage III | CDK4 | "
        "CDKN2A/PTEN | CDC20 | "
        "OrganismCore | 92g | 2026-03-02",
        fontsize=10, fontweight="bold", y=0.99,
    )
    gs_f = gridspec.GridSpec(
        4, 3, figure=fig,
        hspace=0.62, wspace=0.42,
    )

    t   = os_time[hcc_idx]
    e   = os_event[hcc_idx]
    stg = clin["stage"][hcc_idx]
    grd = clin["grade"][hcc_idx]
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

    # ── A: Depth OS Stage III ──────────────────────────────
    ax_a = fig.add_subplot(gs_f[0, 0])
    if hi3 is not None and lo3 is not None:
        p_d3 = logrank_p(
            t_3[hi3], e_3[hi3],
            t_3[lo3], e_3[lo3],
        )
        km_panel(
            ax_a,
            [(f"Deep n={hi3.sum()}",
              t_3[hi3], e_3[hi3], C[1]),
             (f"Shallow n={lo3.sum()}",
              t_3[lo3], e_3[lo3], C[0])],
            f"A — Depth OS Stage III "
            f"(S7-P7)\n{fmt_p(p_d3)}",
        )
    else:
        ax_a.set_title(
            "A — Depth OS Stage III",
            fontsize=9)

    # ── B: CDK4 OS Stage III ───────────────────────────────
    ax_b = fig.add_subplot(gs_f[0, 1])
    if "CDK4" in gc and "CDK4" in stage3_gene_res:
        res = stage3_gene_res["CDK4"]
        km_panel(
            ax_b,
            [(f"CDK4-hi n={res['hi'].sum()}",
              res["t_3"][res["hi"]],
              res["e_3"][res["hi"]], C[1]),
             (f"CDK4-lo n={res['lo'].sum()}",
              res["t_3"][res["lo"]],
              res["e_3"][res["lo"]], C[0])],
            f"B — CDK4 OS Stage III "
            f"(S7-P2)\n{fmt_p(res['p'])}",
        )
    else:
        ax_b.set_title(
            "B — CDK4 OS Stage III",
            fontsize=9)

    # ── C: CTNNB1 mutation KM ──────────────────────────────
    ax_c = fig.add_subplot(gs_f[0, 2])
    if "CTNNB1" in mut_results:
        res = mut_results["CTNNB1"]
        km_panel(
            ax_c,
            [(f"CTNNB1-mut "
              f"n={res['mmask'].sum()}",
              t[res["mmask"]],
              e[res["mmask"]], C[0]),
             (f"CTNNB1-WT "
              f"n={res['wmask'].sum()}",
              t[res["wmask"]],
              e[res["wmask"]], C[1])],
            f"C — CTNNB1 mut OS (HCC-P5)\n"
            f"{fmt_p(res['p'])}",
        )
    else:
        ax_c.set_title(
            "C — CTNNB1 mut OS\n"
            "(GDC MAF required)", fontsize=9)
        ax_c.text(
            0.5, 0.5,
            "HCC-P5 pending\n"
            "GDC MAF download\nrequired",
            ha="center", va="center",
            transform=ax_c.transAxes,
            fontsize=9,
            bbox=dict(
                boxstyle="round",
                facecolor="#fff3cd",
            ),
        )

    # ── D: CDC20 tertile KM ────────────────────────────────
    ax_d = fig.add_subplot(gs_f[1, 0])
    if ("CDC20" in gc
            and cdc20_res
            and "t1" in cdc20_res):
        t1   = cdc20_res["t1"]
        t3_m = cdc20_res["t3"]
        p13  = logrank_p(
            t[t1], e[t1], t[t3_m], e[t3_m]
        )
        km_panel(
            ax_d,
            [(f"CDC20-hi n={t3_m.sum()}",
              t[t3_m], e[t3_m], C[1]),
             (f"CDC20-lo n={t1.sum()}",
              t[t1],   e[t1],   C[0])],
            f"D — CDC20 OS "
            f"(strongest predictor)\n"
            f"{fmt_p(p13)}",
        )
    else:
        ax_d.set_title("D — CDC20 OS",
                       fontsize=9)

    # ── E: CDKN2A vs CDK4 scatter ─────────────────────────
    ax_e = fig.add_subplot(gs_f[1, 1])
    if "CDK4" in gc and "CDKN2A" in gc:
        cdk4   = df_hcc["CDK4"].values
        cdkn2a = df_hcc["CDKN2A"].values
        rv, _  = safe_pearsonr(cdk4, cdkn2a)
        ax_e.scatter(
            cdk4, cdkn2a,
            alpha=0.3, s=10, c=C[2],
        )
        ax_e.set_xlabel("CDK4", fontsize=8)
        ax_e.set_ylabel("CDKN2A", fontsize=8)
        ax_e.set_title(
            f"E — CDK4 vs CDKN2A\n"
            f"r={rv:+.3f} (S7-P6)",
            fontsize=9,
        )

    # ── F: PTEN by subgroup ────────────────────────────────
    ax_f = fig.add_subplot(gs_f[1, 2])
    if "PTEN" in gc:
        pten    = df_hcc["PTEN"].values
        ex_genes = [g for g in EXHAUSTION_GENES
                    if g in gc]
        ex_score = norm01(
            np.nanmean(
                df_hcc[ex_genes].values,
                axis=1,
            )
        ) if len(ex_genes) >= 3 \
            else np.zeros(len(df_hcc))
        med_d  = np.median(depth_metab)
        med_ex = np.median(ex_score)
        groups = {
            "Deep+Cold": (
                (depth_metab >= med_d)
                & (ex_score < med_ex)
            ),
            "Deep+Hot": (
                (depth_metab >= med_d)
                & (ex_score >= med_ex)
            ),
            "Shallow": depth_metab < med_d,
        }
        grp_pten = [
            pten[mask][np.isfinite(pten[mask])]
            for mask in groups.values()
        ]
        ax_f.boxplot(
            grp_pten,
            labels=list(groups.keys()),
            patch_artist=True,
        )
        ax_f.set_title(
            "F — PTEN by subgroup\n"
            "(S7-P5: low in Deep+Cold?)",
            fontsize=9,
        )
        ax_f.set_ylabel("PTEN", fontsize=8)

    # ── G: Stage III gene OS bar ───────────────────────────
    ax_g = fig.add_subplot(gs_f[2, 0])
    if stage3_gene_res:
        genes_g = list(stage3_gene_res.keys())
        pvals_g = [
            -np.log10(
                max(
                    stage3_gene_res[g]["p"],
                    1e-10,
                )
            ) if not np.isnan(
                stage3_gene_res[g]["p"]
            ) else 0
            for g in genes_g
        ]
        colors_g = [
            C[1]
            if stage3_gene_res[g]["m_hi"]
            < stage3_gene_res[g]["m_lo"]
            else C[0]
            for g in genes_g
        ]
        yp = range(len(genes_g))
        ax_g.barh(
            yp, pvals_g,
            color=colors_g, alpha=0.8,
        )
        ax_g.axvline(
            -np.log10(0.05),
            color="black",
            linestyle="--", linewidth=1,
        )
        ax_g.set_yticks(yp)
        ax_g.set_yticklabels(
            genes_g, fontsize=7)
        ax_g.set_xlabel(
            "-log10(p)", fontsize=8)
        ax_g.set_title(
            "G — Stage III gene OS\n"
            "(red=worse, green=better)",
            fontsize=9,
        )

    # ── H: Depth OS all 4 stages overlay ──────────────────
    ax_h = fig.add_subplot(gs_f[2, 1])
    colors_stage = [C[0], C[2], C[1], C[3]]
    for sv, col in zip([1,2,3], colors_stage):
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
        for label, tmask, ls in [
            (f"S{sv}-deep",    hi, "-"),
            (f"S{sv}-shallow", lo, "--"),
        ]:
            ok = safe_km(
                kmf, t_s[tmask],
                e_s[tmask], label
            )
            if ok:
                kmf.plot_survival_function(
                    ax=ax_h, color=col,
                    ci_show=False,
                    linestyle=ls,
                )
    ax_h.set_title(
        "H — Depth OS by stage overlay\n"
        "(solid=deep, dashed=shallow)",
        fontsize=9,
    )
    ax_h.set_xlabel("Months", fontsize=8)
    ax_h.legend(fontsize=5, ncol=2)
    ax_h.set_ylim(-0.05, 1.05)

    # ── I: Depth score by stage boxplot ───────────────────
    ax_i = fig.add_subplot(gs_f[2, 2])
    stage_data   = []
    stage_labels = []
    for sv in [1, 2, 3]:
        mask = stg == sv
        if mask.sum() < 5:
            continue
        stage_data.append(depth_metab[mask])
        stage_labels.append(
            f"S{sv}\nn={mask.sum()}"
        )
    if stage_data:
        bp = ax_i.boxplot(
            stage_data,
            labels=stage_labels,
            patch_artist=True,
        )
        for patch, col in zip(
            bp["boxes"],
            [C[0], C[2], C[1]],
        ):
            patch.set_facecolor(col)
            patch.set_alpha(0.7)
    ax_i.set_title(
        "I — Depth by stage",
        fontsize=9,
    )
    ax_i.set_ylabel(
        "Metabolic depth", fontsize=8)

    # ── J: SMARCA4 Stage III KM ────────────────────────────
    ax_j = fig.add_subplot(gs_f[3, 0])
    if "SMARCA4" in gc and "SMARCA4" \
            in stage3_gene_res:
        res = stage3_gene_res["SMARCA4"]
        km_panel(
            ax_j,
            [(f"SMARCA4-hi "
              f"n={res['hi'].sum()}",
              res["t_3"][res["hi"]],
              res["e_3"][res["hi"]], C[1]),
             (f"SMARCA4-lo "
              f"n={res['lo'].sum()}",
              res["t_3"][res["lo"]],
              res["e_3"][res["lo"]], C[0])],
            f"J — SMARCA4 OS Stage III\n"
            f"{fmt_p(res['p'])}",
        )
    else:
        ax_j.set_title(
            "J — SMARCA4 OS Stage III",
            fontsize=9)

    # ── K: CDC20 vs depth scatter ──────────────────────────
    ax_k = fig.add_subplot(gs_f[3, 1])
    if "CDC20" in gc:
        cdc20 = df_hcc["CDC20"].values
        rv_k, _ = safe_pearsonr(
            depth_metab, cdc20)
        ax_k.scatter(
            depth_metab, cdc20,
            alpha=0.3, s=10, c=C[1],
        )
        ax_k.set_xlabel(
            "Metabolic depth", fontsize=8)
        ax_k.set_ylabel("CDC20", fontsize=8)
        ax_k.set_title(
            f"K — CDC20 vs depth\n"
            f"r={rv_k:+.3f}",
            fontsize=9,
        )

    # ── L: Summary ─────────────────────────────────────────
    ax_l = fig.add_subplot(gs_f[3, 2])
    ax_l.axis("off")

    ct_p = (mut_results.get("CTNNB1",{})
            .get("p", np.nan))
    cdk4_s3_p = (
        stage3_gene_res.get("CDK4",{})
        .get("p", np.nan)
    )
    depth_s3_p = logrank_p(
        t_3[hi3], e_3[hi3],
        t_3[lo3], e_3[lo3],
    ) if hi3 is not None else np.nan

    summary = (
        "L — SCRIPT 7 SUMMARY\n"
        "─────────────────────────────\n"
        "PREDICTIONS:\n"
        f"  S7-P1 CTNNB1-mut OS (HCC-P5)\n"
        f"        {fmt_p(ct_p)}\n"
        f"  S7-P2 CDK4-hi worse Stage III\n"
        f"        {fmt_p(cdk4_s3_p)}\n"
        "  S7-P3 Depth×stage interaction\n"
        f"  S7-P4 CDK4 GSE14520\n"
        "  S7-P5 PTEN-low in Deep+Cold\n"
        "  S7-P6 CDKN2A co-CDK4\n"
        f"  S7-P7 Depth OS Stage III\n"
        f"        {fmt_p(depth_s3_p)}\n\n"
        "CDC20: strongest predictor\n"
        "p=2.57e-07 r=+0.677\n\n"
        "OrganismCore | Doc 92g | "
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
        RESULTS_DIR, "hcc_tcga_s7.png")
    plt.savefig(
        out, dpi=150, bbox_inches="tight")
    log(f"\n  Figure saved: {out}")
    plt.close()

# ============================================================
# MAIN
# ============================================================

def main():
    log("=" * 65)
    log("HEPATOCELLULAR CARCINOMA — SCRIPT 7")
    log("Dataset: TCGA-LIHC (continued)")
    log("Framework: OrganismCore")
    log("Doc: 92g | Date: 2026-03-02")
    log("=" * 65)
    log("")
    log("PREDICTIONS LOCKED 2026-03-02:")
    log("S7-P1: CTNNB1-mut better OS (HCC-P5)")
    log("S7-P2: CDK4-hi worse OS Stage III")
    log("S7-P3: Depth×stage interaction "
        "significant")
    log("S7-P4: CDK4-hi worse OS GSE14520")
    log("S7-P5: PTEN-low enriched in "
        "Deep+Cold")
    log("S7-P6: CDKN2A-high co-occurs with "
        "CDK4-high")
    log("S7-P7: Depth OS Stage III p<0.05")

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

    # ── S7-1: Mutation survival ───────────────────────────
    mut_results = mutation_survival(
        mut_matrix, os_time, os_event,
        hcc_idx, df_hcc, depth_metab,
    )

    # ── S7-2: Depth × stage interaction ──────────────────
    depth_stage_interaction(
        depth_metab, os_time, os_event,
        hcc_idx, clin,
    )

    # ── S7-3: Stage III deep-dive ─────────────────────────
    (stage3_gene_res,
     hi3, lo3, t_3, e_3) = stage3_deep_dive(
        df_hcc, depth_metab,
        os_time, os_event,
        hcc_idx, clin, mut_matrix,
    )

    # ── S7-4: CDKN2A / PTEN ──────────────────────────────
    cdkn2a_pten_analysis(
        df_hcc, depth_metab,
        os_time, os_event,
        hcc_idx, clin,
    )

    # ── S7-5: CDK4 in GSE14520 ───────────────────────────
    cdk4_gse14520_reprocess()

    # ── S7-6: CDC20 deep-dive ─────────────────────────────
    cdc20_res = cdc20_analysis(
        df_hcc, depth_metab,
        os_time, os_event,
        hcc_idx, clin,
    )

    # ── Figure ───────────────────────��────────────────────
    generate_figure(
        df_hcc, depth_metab,
        os_time, os_event, hcc_idx,
        clin, mut_results,
        stage3_gene_res, hi3, lo3, t_3, e_3,
        cdc20_res,
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
            RESULTS_DIR, "depth_scores_s7.csv"
        ),
        index=False,
    )

    write_log()
    log(f"\n  Log:    {LOG_FILE}")
    log(f"  Output: {RESULTS_DIR}")
    log("\n=== SCRIPT 7 COMPLETE ===")
    log("\nPaste full output for Document 92g.")


if __name__ == "__main__":
    main()
