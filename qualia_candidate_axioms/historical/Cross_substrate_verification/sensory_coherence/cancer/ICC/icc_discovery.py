"""
ICC FALSE ATTRACTOR — SCRIPT 0c
DISCOVERY — CORRECT STRATEGY

Diagnosis from v0a/v0b:
  All GEO ICC datasets use Illumina
  platforms (GPL8432, GPL6104, GPL10558)
  with ILMN_###### probe IDs.
  Gene-symbol mapping requires the
  GPL annotation file (separate download).

New strategy:
  PRIMARY:   TCGA-CHOL via GDC/Xena
             RNA-seq, OS, clinical
             Same pipeline as TCGA-LIHC
             ~36 ICC samples (small but
             gold-standard RNA-seq)
  SECONDARY: GEO datasets with GPL
             annotation download
             GSE32225 (n=149, GPL8432)
             via annotation bridge file
  TERTIARY:  GSE255058 (newer, 2024,
             bulk RNA-seq with OS)

Two parallel tracks:
  Track A: TCGA-CHOL (RNA-seq, OS)
  Track B: GSE32225+GPL8432 (microarray,
           large n, ICC vs normal)

Author: Eric Robert Lawson
Framework: OrganismCore
Doc: 93a | Date: 2026-03-02
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
DATA_DIR    = os.path.join(BASE_DIR, "data/")
TCGA_DIR    = os.path.join(BASE_DIR,
                           "tcga_chol/")
GEO_DIR     = os.path.join(BASE_DIR,
                           "geo_icc/")
RESULTS_DIR = os.path.join(BASE_DIR,
                           "results_s0c/")
LOG_FILE    = os.path.join(RESULTS_DIR,
                           "discovery_log_s0c.txt")
for d in [DATA_DIR, TCGA_DIR,
          GEO_DIR, RESULTS_DIR]:
    os.makedirs(d, exist_ok=True)

# ============================================================
# GENE PANELS
# ============================================================

CHOL_SW = [
    "SOX17","HNF1B","FOXA2",
    "KRT7","KRT19","AQP1","ANXA4",
    "GGT1","CDH1","EPCAM","MUC1",
    "CLDN4","CLDN7","KLF4",
    "HNF4A","ALB","APOB","CYP3A4",
    "ALDOB","G6PC","CFTR","SLC4A2",
]
ICC_FA = [
    "SOX4","SOX9","PROM1","CD44",
    "ALDH1A1","CDC20","BIRC5","TOP2A",
    "MKI67","CCNB1","CDK4","CDK6",
    "EZH2","HDAC2","DNMT1",
    "VIM","TWIST1","ZEB1","ZEB2",
    "SNAI1","FN1","FGFR2",
    "IDH1","IDH2","EGFR","ERBB2",
    "MET","KRAS","BAP1","ARID1A",
    "SMAD4","PTEN","CDKN2A","TP53",
    "CD274","CD8A","PRF1","FOXP3",
    "HAVCR2","TGFB1","FAP","ACTA2",
    "COL1A1","POSTN","MMP2","MMP9",
    "STAT3","VEGFA","CTNNB1",
    "CCND1","RB1","NOTCH1","NOTCH2",
    "WNT5A","GLUL","CA9","SF3B1",
]

ALL_PANEL = list(set(CHOL_SW + ICC_FA))

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
        isinstance(p,float) and np.isnan(p)
    ):
        return "p=N/A     "
    if p < 0.001: return f"p={p:.2e} ***"
    elif p < 0.01: return f"p={p:.2e}  **"
    elif p < 0.05: return f"p={p:.4f}   *"
    else:          return f"p={p:.4f}  ns"

def norm01(arr):
    arr = np.asarray(arr, float)
    mn,mx = np.nanmin(arr),np.nanmax(arr)
    if mx > mn: return (arr-mn)/(mx-mn)
    return np.full_like(arr, 0.5)

def safe_pearsonr(x,y):
    x = np.asarray(x,float)
    y = np.asarray(y,float)
    m = np.isfinite(x)&np.isfinite(y)
    if m.sum()<5: return np.nan,np.nan
    return stats.pearsonr(x[m],y[m])

def logrank_p(t1,e1,t0,e0):
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

def try_get(url, dest, min_size=1000):
    if (os.path.exists(dest)
            and os.path.getsize(dest)
            > min_size):
        log(f"  Cached: {os.path.getsize(dest):,}b")
        return dest
    log(f"  GET {url}")
    try:
        r = requests.get(
            url, stream=True,
            timeout=300,
            headers={"User-Agent":"Mozilla/5.0"},
        )
        log(f"  HTTP {r.status_code}")
        if r.status_code == 200:
            data = b"".join(
                r.iter_content(1024*1024)
            )
            if len(data) > min_size:
                with open(dest,"wb") as f:
                    f.write(data)
                log(f"  Saved {len(data):,}b")
                return dest
            else:
                log(f"  Too small: {len(data)}b")
    except Exception as ex:
        log(f"  Error: {ex}")
    return None

# ============================================================
# TRACK A: TCGA-CHOL via UCSC Xena
# ============================================================

XENA_BASE = (
    "https://tcga-xena-hub.s3.us-east-1"
    ".amazonaws.com/download/"
)
XENA_URLS = {
    "expr": [
        XENA_BASE
        + "TCGA.CHOL.sampleMap%2FHiSeqV2.gz",
        XENA_BASE
        + "TCGA.CHOL.sampleMap%2FHiSeqV2_percentile.gz",
        "https://gdc-hub.s3.us-east-1"
        ".amazonaws.com/download/"
        "TCGA-CHOL.htseq_fpkm.tsv.gz",
    ],
    "surv": [
        XENA_BASE
        + "survival%2FCHOL_survival.txt.gz",
        XENA_BASE
        + "TCGA.CHOL.sampleMap%2FCHOL_clinicalMatrix.gz",
        "https://tcga-xena-hub.s3"
        ".us-east-1.amazonaws.com"
        "/download/TCGA.CHOL"
        ".sampleMap%2FCHOL_survival.txt",
    ],
    "pheno": [
        XENA_BASE
        + "TCGA.CHOL.sampleMap%2FCHOL_clinicalMatrix.gz",
        XENA_BASE
        + "TCGA.CHOL.sampleMap%2FCHOL_clinicalMatrix",
    ],
}

def load_tcga_chol():
    log("")
    log("="*65)
    log("TRACK A: TCGA-CHOL")
    log("="*65)

    # Expression
    expr_path = None
    for url in XENA_URLS["expr"]:
        dest = os.path.join(
            TCGA_DIR,
            "CHOL_expr.tsv.gz"
            if "gz" in url else
            "CHOL_expr.tsv",
        )
        p = try_get(url, dest, 100000)
        if p:
            expr_path = p
            break

    # Survival
    surv_path = None
    for url in XENA_URLS["surv"]:
        dest = os.path.join(
            TCGA_DIR,
            "CHOL_survival.txt.gz"
            if "gz" in url else
            "CHOL_survival.txt",
        )
        p = try_get(url, dest, 1000)
        if p:
            surv_path = p
            break

    # Phenotype
    pheno_path = None
    for url in XENA_URLS["pheno"]:
        dest = os.path.join(
            TCGA_DIR,
            "CHOL_pheno.gz"
            if "gz" in url else
            "CHOL_pheno.txt",
        )
        p = try_get(url, dest, 1000)
        if p:
            pheno_path = p
            break

    # Parse expression
    expr = {}
    if expr_path:
        log(f"\n  Parsing expression: "
            f"{expr_path}")
        try:
            opener = (
                gzip.open(expr_path,"rt",
                    encoding="utf-8",
                    errors="ignore")
                if expr_path.endswith(".gz")
                else open(expr_path,"r",
                    encoding="utf-8",
                    errors="ignore")
            )
            sample_ids = []
            with opener as f:
                for line in f:
                    parts = line.rstrip(
                        "\n"
                    ).split("\t")
                    if not sample_ids:
                        sample_ids = [
                            p.strip()
                            for p in parts[1:]
                        ]
                        continue
                    gene = parts[0].strip(
                    ).strip('"')
                    if gene not in \
                            set(ALL_PANEL):
                        continue
                    try:
                        vals = np.array([
                            float(p.strip())
                            if p.strip()
                            not in [
                                "","NA","nan",
                                "NaN",
                            ]
                            else np.nan
                            for p in parts[1:]
                        ])
                        expr[gene] = vals
                    except ValueError:
                        pass
            log(f"  Samples: {len(sample_ids)}")
            log(f"  Genes:   {len(expr)}")
        except Exception as ex:
            log(f"  Expression error: {ex}")
    else:
        sample_ids = []
        log("  Expression: not available")

    # Parse survival
    os_time  = {}
    os_event = {}
    if surv_path:
        log(f"\n  Parsing survival: {surv_path}")
        try:
            opener = (
                gzip.open(surv_path,"rt",
                    encoding="utf-8",
                    errors="ignore")
                if surv_path.endswith(".gz")
                else open(surv_path,"r",
                    encoding="utf-8",
                    errors="ignore")
            )
            hdr = None
            tc = ec = sc = None
            with opener as f:
                for line in f:
                    parts = [
                        p.strip().strip('"')
                        for p in
                        line.rstrip("\n")
                        .split("\t")
                    ]
                    if hdr is None:
                        hdr = [
                            p.lower()
                            for p in parts
                        ]
                        for i,h in \
                                enumerate(hdr):
                            if h in [
                                "sample",
                                "_patient_id",
                                "sampleid",
                            ] and sc is None:
                                sc = i
                            if h in [
                                "os.time",
                                "os_time",
                                "time",
                                "overall_survival",
                            ] and tc is None:
                                tc = i
                            if h in [
                                "os",
                                "vital_status",
                                "event",
                            ] and ec is None:
                                ec = i
                        log(f"  Surv header: "
                            f"{hdr[:6]}")
                        continue
                    sid = (parts[sc].strip()
                           if sc is not None
                           and sc < len(parts)
                           else None)
                    if not sid: continue
                    try:
                        if tc is not None \
                                and tc < len(parts):
                            tv = float(
                                parts[tc].strip()
                            )
                            # Convert days
                            if tv > 1000:
                                tv /= 30.44
                            elif tv > 60:
                                pass
                            os_time[sid] = tv
                    except (ValueError,
                            TypeError):
                        pass
                    try:
                        if ec is not None \
                                and ec < len(parts):
                            ev = parts[ec].strip(
                            ).lower()
                            if ev in [
                                "1","dead",
                                "deceased",
                            ]:
                                os_event[sid] = 1
                            elif ev in [
                                "0","alive",
                                "living",
                            ]:
                                os_event[sid] = 0
                            else:
                                os_event[sid] = \
                                    float(ev)
                    except (ValueError,
                            TypeError):
                        pass
            log(f"  OS time: {len(os_time)} "
                f"OS event: {len(os_event)}")
        except Exception as ex:
            log(f"  Survival error: {ex}")

    # Parse phenotype for stage/subtype
    stage_dict = {}
    subtype_dict = {}
    if pheno_path:
        try:
            opener = (
                gzip.open(pheno_path,"rt",
                    encoding="utf-8",
                    errors="ignore")
                if pheno_path.endswith(".gz")
                else open(pheno_path,"r",
                    encoding="utf-8",
                    errors="ignore")
            )
            hdr = None
            sid_c = stg_c = sub_c = None
            with opener as f:
                for line in f:
                    parts = [
                        p.strip().strip('"')
                        for p in
                        line.rstrip("\n")
                        .split("\t")
                    ]
                    if hdr is None:
                        hdr = [
                            p.lower()
                            for p in parts
                        ]
                        for i,h in \
                                enumerate(hdr):
                            if "sample" in h \
                                    and sid_c \
                                    is None:
                                sid_c = i
                            if "stage" in h \
                                    and stg_c \
                                    is None:
                                stg_c = i
                            if any(x in h
                                   for x in [
                                       "type","subtype",
                                       "histolog",
                                   ]) and sub_c \
                                    is None:
                                sub_c = i
                        continue
                    if sid_c is None \
                            or sid_c >= len(parts):
                        continue
                    sid = parts[sid_c]
                    if stg_c and stg_c < len(parts):
                        stage_dict[sid] = \
                            parts[stg_c]
                    if sub_c and sub_c < len(parts):
                        subtype_dict[sid] = \
                            parts[sub_c]
            log(f"  Stage data: "
                f"{len(stage_dict)} samples")
        except Exception as ex:
            log(f"  Pheno error: {ex}")

    # Align arrays
    n = len(sample_ids)
    t_arr = np.full(n, np.nan)
    e_arr = np.full(n, np.nan)
    for i, sid in enumerate(sample_ids):
        # Try exact then 12-char match
        if sid in os_time:
            t_arr[i] = os_time[sid]
            e_arr[i] = os_event.get(sid, np.nan)
        else:
            for k in os_time:
                if (len(k) >= 12
                        and len(sid) >= 12
                        and k[:12] == sid[:12]):
                    t_arr[i] = os_time[k]
                    e_arr[i] = os_event.get(
                        k, np.nan
                    )
                    break

    valid_os = (
        np.isfinite(t_arr)
        & np.isfinite(e_arr)
        & (t_arr > 0)
    )
    log(f"\n  TCGA-CHOL summary:")
    log(f"  n_samples: {n}")
    log(f"  n_genes:   {len(expr)}")
    log(f"  OS valid:  {valid_os.sum()} "
        f"events="
        f"{int(e_arr[valid_os].sum())}")
    log(f"  Genes found: "
        f"{sorted(list(expr.keys()))}")

    # Identify tumour vs normal
    stype = np.array([
        s[13:15] if len(s) >= 15 else "??"
        for s in sample_ids
    ])
    tumour = (
        (stype == "01")
        | np.array([
            ("-01" in s or "-01A" in s
             or "-01B" in s)
            for s in sample_ids
        ])
    )
    normal = (
        (stype == "11")
        | np.array([
            ("-11" in s or "-11A" in s)
            for s in sample_ids
        ])
    )
    log(f"  Tumour: {tumour.sum()} "
        f"Normal: {normal.sum()}")

    return {
        "sample_ids": sample_ids,
        "expr":       expr,
        "os_time":    t_arr,
        "os_event":   e_arr,
        "valid_os":   valid_os,
        "tumour":     tumour,
        "normal":     normal,
        "stage":      stage_dict,
        "subtype":    subtype_dict,
        "n":          n,
    }

# ============================================================
# TRACK B: GEO with GPL ANNOTATION
# GSE32225 + GPL8432 annotation
# ============================================================

def load_gpl_annotation(gpl_id):
    """
    Download GPL annotation file from GEO.
    Returns dict: probe_id → gene_symbol
    """
    urls = [
        f"https://ftp.ncbi.nlm.nih.gov"
        f"/geo/platforms/"
        f"{gpl_id[:len(gpl_id)-3]}nnn"
        f"/{gpl_id}/annot/"
        f"{gpl_id}.annot.gz",
        f"https://ftp.ncbi.nlm.nih.gov"
        f"/geo/platforms/"
        f"GPL8nnn/{gpl_id}/annot/"
        f"{gpl_id}.annot.gz",
        f"https://ftp.ncbi.nlm.nih.gov"
        f"/geo/platforms/"
        f"GPL6nnn/{gpl_id}/annot/"
        f"{gpl_id}.annot.gz",
        f"https://ftp.ncbi.nlm.nih.gov"
        f"/geo/platforms/"
        f"GPL10nnn/{gpl_id}/annot/"
        f"{gpl_id}.annot.gz",
    ]

    dest = os.path.join(
        DATA_DIR, f"{gpl_id}_annot.gz"
    )
    path = None
    for url in urls:
        p = try_get(url, dest, 1000)
        if p:
            path = p
            break

    if path is None:
        log(f"  GPL annotation not found "
            f"for {gpl_id}")
        return {}

    # Parse annotation
    probe_to_gene = {}
    try:
        opener = (
            gzip.open(path,"rt",
                encoding="utf-8",
                errors="ignore")
            if path.endswith(".gz")
            else open(path,"r",
                encoding="utf-8",
                errors="ignore")
        )
        hdr = None
        id_c = sym_c = None
        with opener as f:
            for line in f:
                if line.startswith("#") \
                        or line.startswith("^") \
                        or line.startswith("!"):
                    continue
                parts = line.rstrip(
                    "\n"
                ).split("\t")
                if hdr is None:
                    hdr = [
                        p.lower().strip()
                        for p in parts
                    ]
                    for i,h in enumerate(hdr):
                        if h in ["id","probe_id",
                                 "id_ref","ilmn"
                                 ] and id_c is None:
                            id_c = i
                        if any(x in h
                               for x in [
                                   "symbol",
                                   "gene_symbol",
                                   "genesymbol",
                               ]) and sym_c is None:
                            sym_c = i
                    if id_c is None: id_c = 0
                    if sym_c is None:
                        # Try to find by value
                        for i,h in enumerate(hdr):
                            if h == "gene symbol":
                                sym_c = i
                                break
                    log(f"  GPL header: "
                        f"{hdr[:8]} "
                        f"id_col={id_c} "
                        f"sym_col={sym_c}")
                    continue
                if (id_c is None
                        or sym_c is None):
                    continue
                if max(id_c,sym_c) \
                        >= len(parts):
                    continue
                pid = parts[id_c].strip()
                sym = parts[sym_c].strip()
                if pid and sym and sym != "NA":
                    probe_to_gene[pid] = sym
    except Exception as ex:
        log(f"  GPL parse error: {ex}")

    log(f"  GPL {gpl_id}: "
        f"{len(probe_to_gene)} probes mapped")
    return probe_to_gene

def load_gse_with_annotation(
    gse_id, matrix_url,
    gpl_id, min_size=100000,
):
    """
    Load a GEO series matrix and annotate
    probes using downloaded GPL annotation.
    """
    log(f"\n  Loading {gse_id} "
        f"(platform {gpl_id})")

    dest = os.path.join(
        GEO_DIR,
        f"{gse_id}_matrix.txt.gz",
    )
    path = try_get(
        matrix_url, dest, min_size
    )
    if path is None:
        log(f"  Matrix download failed")
        return None

    # Get GPL annotation
    probe_to_gene = load_gpl_annotation(
        gpl_id
    )
    if not probe_to_gene:
        log(f"  No annotation — "
            f"trying SOFT file approach")
        # Try to get annotation from
        # the SOFT platform file
        soft_url = (
            f"https://ftp.ncbi.nlm.nih.gov"
            f"/geo/platforms/"
            f"GPL8nnn/{gpl_id}/soft/"
            f"{gpl_id}_family.soft.gz"
        )
        soft_dest = os.path.join(
            DATA_DIR, f"{gpl_id}.soft.gz"
        )
        sp = try_get(
            soft_url, soft_dest, 1000
        )
        if sp:
            probe_to_gene = \
                parse_soft_annotation(sp)

    if not probe_to_gene:
        log(f"  WARNING: No probe→gene "
            f"map for {gpl_id}")
        log(f"  Will try gene-symbol "
            f"matching from matrix")

    # Parse matrix
    opener = (
        gzip.open(path,"rt",
            encoding="utf-8",
            errors="ignore")
        if path.endswith(".gz")
        else open(path,"r",
            encoding="utf-8",
            errors="ignore")
    )

    gsm_ids    = []
    char_block = {}
    expr_data  = {}
    in_table   = tbl_hdr = False
    n_samples  = 0
    genes_want = set(ALL_PANEL)
    probes_seen = matched = 0

    with opener as f:
        for raw in f:
            line = raw.rstrip("\n")
            if line.startswith(
                "!Sample_geo_accession"
            ):
                parts = line.split("\t")
                gsm_ids   = [
                    p.strip().strip('"')
                    for p in parts[1:]
                ]
                n_samples = len(gsm_ids)
                continue
            if line.startswith(
                "!Sample_characteristics_ch1"
            ):
                parts = line.split("\t")
                key   = parts[0]
                vals  = [
                    p.strip().strip('"')
                    for p in parts[1:]
                ]
                if key not in char_block:
                    char_block[key] = []
                char_block[key].append(vals)
                continue
            if "series_matrix_table_begin" \
                    in line:
                in_table = True
                tbl_hdr  = False
                continue
            if "series_matrix_table_end" \
                    in line:
                break
            if not in_table: continue
            if not tbl_hdr:
                tbl_hdr = True
                continue

            parts    = line.split("\t")
            probe_id = parts[0].strip(
            ).strip('"')
            probes_seen += 1

            # Map probe to gene
            gene = probe_to_gene.get(
                probe_id
            )
            # Fallback: probe IS gene symbol
            if gene is None:
                g = probe_id.strip()
                if g in genes_want:
                    gene = g

            if gene is None: continue
            if gene not in genes_want: continue

            matched += 1
            try:
                vals = np.array([
                    float(p.strip())
                    if p.strip() not in
                    ["","NA","nan","NaN"]
                    else np.nan
                    for p in parts[1:n_samples+1]
                ])
                if gene not in expr_data:
                    expr_data[gene] = (
                        probe_id, vals
                    )
                else:
                    if np.nanvar(vals) > \
                            np.nanvar(
                                expr_data[gene][1]
                            ):
                        expr_data[gene] = (
                            probe_id, vals
                        )
            except (ValueError, TypeError):
                continue

    log(f"  Probes seen: {probes_seen} "
        f"matched: {matched}")
    log(f"  Genes extracted: "
        f"{len(expr_data)}")

    expr = {
        g: v for g,(_, v)
        in expr_data.items()
    }
    return {
        "gse_id":     gse_id,
        "gsm_ids":    gsm_ids,
        "char_block": char_block,
        "expr":       expr,
        "n_samples":  n_samples,
    }

def parse_soft_annotation(soft_path):
    """
    Parse probe→gene from SOFT
    platform file.
    """
    probe_to_gene = {}
    in_data = False
    hdr     = None
    id_c = sym_c = None
    try:
        opener = (
            gzip.open(soft_path,"rt",
                encoding="utf-8",
                errors="ignore")
            if soft_path.endswith(".gz")
            else open(soft_path,"r",
                encoding="utf-8",
                errors="ignore")
        )
        with opener as f:
            for line in f:
                line = line.rstrip("\n")
                if "!platform_table_begin" \
                        in line.lower():
                    in_data = True
                    hdr = None
                    continue
                if "!platform_table_end" \
                        in line.lower():
                    break
                if not in_data: continue
                parts = line.split("\t")
                if hdr is None:
                    hdr = [
                        p.lower().strip()
                        for p in parts
                    ]
                    for i,h in enumerate(hdr):
                        if h in ["id"] and \
                                id_c is None:
                            id_c = i
                        if any(x in h
                               for x in [
                                   "symbol",
                                   "gene_symbol",
                               ]) and \
                                sym_c is None:
                            sym_c = i
                    continue
                if id_c is None or \
                        sym_c is None: continue
                if max(id_c,sym_c) \
                        >= len(parts): continue
                pid = parts[id_c].strip()
                sym = parts[sym_c].strip()
                if pid and sym and sym != "NA":
                    # Handle multi-gene probes
                    sym = sym.split("///")[0]\
                        .split(";")[0]\
                        .strip()
                    if sym:
                        probe_to_gene[pid] = sym
    except Exception as ex:
        log(f"  SOFT parse error: {ex}")
    log(f"  SOFT annotation: "
        f"{len(probe_to_gene)} probes")
    return probe_to_gene

# ============================================================
# ANALYSIS FUNCTIONS
# ============================================================

def run_analysis(label, expr, os_t,
                 os_e, tumour_idx,
                 normal_idx=None):
    """
    Run the full discovery analysis
    pipeline on one dataset.
    Returns depth, OS results, diff results.
    """
    log(f"\n{'='*65}")
    log(f"ANALYSIS: {label}")
    log(f"{'='*65}")

    gc = list(expr.keys())
    log(f"  Genes: {len(gc)}")
    log(f"  Found: {sorted(gc)}")
    log(f"  n_tumour: {len(tumour_idx)}")
    if normal_idx is not None:
        log(f"  n_normal: "
            f"{len(normal_idx)}")

    # ── ICC vs Normal ─────────────────────
    diff_res = {}
    if (normal_idx is not None
            and len(normal_idx) >= 3
            and len(tumour_idx) >= 3):
        log(f"\n  ICC vs Normal:")
        log(f"  {'Gene':<12} {'ICC':>8} "
            f"{'Nor':>8} {'FC':>7} "
            f"{'p':>12}  role")
        log(f"  {'-'*58}")
        panel = [g for g in
                 (CHOL_SW+ICC_FA) if g in gc]
        for gene in panel:
            gv  = expr[gene]
            iv  = gv[tumour_idx]
            nv  = gv[normal_idx]
            iv  = iv[np.isfinite(iv)]
            nv  = nv[np.isfinite(nv)]
            if len(iv)<2 or len(nv)<2:
                continue
            im  = iv.mean()
            nm  = nv.mean()
            fc  = im - nm
            _,p = stats.mannwhitneyu(
                iv,nv,
                alternative="two-sided"
            )
            role = (
                "SW↓✓" if (
                    gene in CHOL_SW
                    and fc<-0.3 and p<0.05
                ) else "SW↓ns"
                if gene in CHOL_SW
                else "FA↑✓" if (
                    gene in ICC_FA
                    and fc>0.3 and p<0.05
                ) else "FA↑ns"
            )
            log(f"  {gene:<12} "
                f"{im:>8.3f} {nm:>8.3f} "
                f"{fc:>+7.3f} "
                f"{fmt_p(p):>12}  {role}")
            diff_res[gene] = {
                "icc_mean":im,
                "nor_mean":nm,
                "fc":fc,"p":p,"role":role,
            }
        sw_c = [g for g,r in diff_res.items()
                if "SW↓✓" in r["role"]]
        fa_c = [g for g,r in diff_res.items()
                if "FA↑✓" in r["role"]]
        log(f"\n  SW↓ confirmed: {sw_c}")
        log(f"  FA↑ confirmed: {fa_c}")

    # ── Depth score ───────────────────────
    sw = [g for g in CHOL_SW
          if g in gc
          and diff_res.get(g,{})
          .get("fc",0) < -0.1]
    fa = [g for g in ICC_FA
          if g in gc
          and diff_res.get(g,{})
          .get("fc",0) > 0.1]
    # Fallback: use all available
    if len(sw)+len(fa) < 3:
        sw = [g for g in CHOL_SW if g in gc]
        fa = [g for g in ICC_FA if g in gc]

    log(f"\n  Depth SW: {sw}")
    log(f"  Depth FA: {fa}")

    n_t  = len(tumour_idx)
    d    = np.zeros(n_t)
    nd   = 0
    if sw:
        sm = np.column_stack([
            expr[g][tumour_idx] for g in sw
        ])
        d += 1 - norm01(np.nanmean(sm,axis=1))
        nd += 1
    if fa:
        fm = np.column_stack([
            expr[g][tumour_idx] for g in fa
        ])
        d += norm01(np.nanmean(fm,axis=1))
        nd += 1
    if nd: d /= nd
    log(f"  Depth: mean={d.mean():.4f} "
        f"std={d.std():.4f}")

    # ── Depth correlations ────────────────
    log(f"\n  Depth correlations:")
    log(f"  {'Gene':<12} {'r':>8} "
        f"{'p':>12}")
    log(f"  {'-'*35}")
    dcors = {}
    for gene in (CHOL_SW+ICC_FA):
        if gene not in gc: continue
        gv = expr[gene][tumour_idx]
        rv,pv = safe_pearsonr(d, gv)
        if not np.isnan(rv):
            dcors[gene] = (rv,pv)
            if abs(rv) > 0.25:
                log(f"  {gene:<12} "
                    f"{rv:>+8.4f} "
                    f"{fmt_p(pv)}")

    # ── OS screen ──────────────────────���──
    t  = os_t[tumour_idx]
    e  = os_e[tumour_idx]
    vv = (np.isfinite(t) & np.isfinite(e)
          & (t>0))
    os_res = {}
    log(f"\n  OS screen: n={vv.sum()} "
        f"events={int(e[vv].sum())}")

    if vv.sum() >= 10:
        log(f"\n  {'Gene':<12} {'p':>12} "
            f"{'hi':>7} {'lo':>7}  dir")
        log(f"  {'-'*50}")

        # Depth OS
        med = np.nanmedian(d[vv])
        hi  = vv & (d >= med)
        lo  = vv & (d <  med)
        p_d = logrank_p(
            t[hi],e[hi],t[lo],e[lo]
        )
        m_hi = t[hi].mean() \
            if hi.sum()>0 else np.nan
        m_lo = t[lo].mean() \
            if lo.sum()>0 else np.nan
        log(f"  {'DEPTH':<12} {fmt_p(p_d)} "
            f"{m_hi:>7.1f} {m_lo:>7.1f}  "
            f"{'↑=worse' if m_hi<m_lo else '↑=better'}")
        os_res["DEPTH"] = {
            "p":p_d,"m_hi":m_hi,
            "m_lo":m_lo,"n":int(vv.sum()),
        }

        for gene in (CHOL_SW+ICC_FA):
            if gene not in gc: continue
            gv    = expr[gene][tumour_idx]
            valid = vv & np.isfinite(gv)
            if valid.sum() < 8: continue
            med   = np.nanmedian(gv[valid])
            hi    = valid & (gv >= med)
            lo    = valid & (gv <  med)
            p_os  = logrank_p(
                t[hi],e[hi],t[lo],e[lo]
            )
            m_hi  = t[hi].mean() \
                if hi.sum()>0 else np.nan
            m_lo  = t[lo].mean() \
                if lo.sum()>0 else np.nan
            d_s   = ("↑=worse"
                     if not np.isnan(m_hi)
                     and not np.isnan(m_lo)
                     and m_hi<m_lo
                     else "↑=better")
            if not np.isnan(p_os) \
                    and p_os < 0.10:
                log(f"  {gene:<12} "
                    f"{fmt_p(p_os)} "
                    f"{m_hi:>7.1f} "
                    f"{m_lo:>7.1f}  {d_s}")
            os_res[gene] = {
                "p":p_os,"m_hi":m_hi,
                "m_lo":m_lo,
                "n":int(valid.sum()),
                "dir":d_s,
            }
    else:
        log("  OS insufficient for screen")

    return d, diff_res, os_res, dcors

# ============================================================
# PARSE CLINICAL FROM CHAR BLOCK
# ============================================================

def parse_char_block_clinical(gse_obj):
    n  = gse_obj["n_samples"]
    cb = gse_obj["char_block"]
    os_t = np.full(n, np.nan)
    os_e = np.full(n, np.nan)
    tis  = [""] * n
    sample_chars = [{} for _ in range(n)]
    for key,val_lists in cb.items():
        for val_row in val_lists:
            for i,v in enumerate(val_row):
                if i >= n: break
                v = v.strip()
                if not v: continue
                if ":" in v:
                    k,_,vv = v.partition(":")
                    sample_chars[i][
                        k.strip().lower()
                    ] = vv.strip()
                else:
                    sample_chars[i][
                        key.lower()
                    ] = v

    all_keys = set()
    for sc in sample_chars:
        all_keys.update(sc.keys())
    log(f"  Char keys: {sorted(all_keys)}")

    TIME_K  = {
        "overall survival","os time",
        "survival time","time","months",
        "os (month)","survival days",
        "days to death","follow-up time",
    }
    EVENT_K = {
        "vital status","death","status",
        "event","survival status","os",
        "alive/dead","outcome",
    }
    TISS_K  = {
        "tissue","source","type","disease",
        "cell type","sample type",
        "disease state","histology","diagnosis",
    }

    for i,sc in enumerate(sample_chars):
        for k,v in sc.items():
            kl = k.lower()
            vl = v.lower()
            if any(t in kl for t in TISS_K):
                tis[i] = vl
            if np.isnan(os_t[i]) and \
                    any(t in kl for t in TIME_K):
                try:
                    tv = float(re.sub(
                        r"[^0-9.\-]","",v
                    ))
                    if tv > 1825: tv /= 30.44
                    elif tv > 100: tv /= 30.44
                    if tv > 0: os_t[i] = tv
                except (ValueError,TypeError):
                    pass
            if np.isnan(os_e[i]) and \
                    any(t in kl for t in EVENT_K):
                vl2 = vl.strip()
                if vl2 in ["dead","deceased",
                            "1","died","death"]:
                    os_e[i] = 1
                elif vl2 in ["alive","living",
                              "0","censored"]:
                    os_e[i] = 0
                else:
                    try: os_e[i] = float(vl2)
                    except (ValueError,TypeError):
                        pass

    icc_kw = [
        "icc","cholangiocarcinoma","cholangio",
        "tumor","tumour","cancer","carcinoma",
        "malignant","intrahepatic","cca",
    ]
    nor_kw = [
        "normal","adjacent","non-tumor",
        "non-tumour","control","healthy",
        "biliary epithelial",
    ]
    tis_arr = np.array(tis)
    icc_m = np.array([
        any(k in t for k in icc_kw)
        for t in tis
    ])
    nor_m = np.array([
        any(k in t for k in nor_kw)
        for t in tis
    ])
    if icc_m.sum() == 0:
        icc_m = np.ones(n, dtype=bool)

    valid = (np.isfinite(os_t)
             & np.isfinite(os_e)
             & (os_t > 0))
    log(f"  ICC={icc_m.sum()} "
        f"Normal={nor_m.sum()} "
        f"OS valid={valid.sum()} "
        f"events={int(os_e[valid].sum())}"
        f" if valid>0 else 0")
    return os_t, os_e, icc_m, nor_m

# ============================================================
# GENERATE FIGURE
# ============================================================

def generate_figure(
    tcga_data, tcga_depth,
    tcga_os_res, tcga_diff,
    gse_data, gse_depth,
    gse_os_res, gse_diff,
):
    log("\n--- Generating figure ---")
    fig = plt.figure(figsize=(26,18))
    fig.suptitle(
        "ICC False Attractor — Script 0c "
        "Discovery | TCGA-CHOL + GEO | "
        "OrganismCore | 93a | 2026-03-02",
        fontsize=10, fontweight="bold",
        y=0.99,
    )
    gs_f = gridspec.GridSpec(
        3,4,figure=fig,
        hspace=0.55,wspace=0.42,
    )
    C = ["#27ae60","#e74c3c",
         "#2980b9","#8e44ad",
         "#e67e22","#16a085"]
    kmf = KaplanMeierFitter()

    def km_ax(ax, t_hi,e_hi,t_lo,e_lo,
              l_hi,l_lo,title):
        t_hi=np.asarray(t_hi,float)
        e_hi=np.asarray(e_hi,float)
        t_lo=np.asarray(t_lo,float)
        e_lo=np.asarray(e_lo,float)
        m1=(np.isfinite(t_hi)&np.isfinite(e_hi)
            &(t_hi>0))
        m0=(np.isfinite(t_lo)&np.isfinite(e_lo)
            &(t_lo>0))
        if m1.sum()<3 or m0.sum()<3: return
        kmf.fit(t_hi[m1],e_hi[m1],label=l_hi)
        kmf.plot_survival_function(
            ax=ax,color=C[1],ci_show=False)
        kmf.fit(t_lo[m0],e_lo[m0],label=l_lo)
        kmf.plot_survival_function(
            ax=ax,color=C[0],ci_show=False)
        p = logrank_p(t_hi[m1],e_hi[m1],
                      t_lo[m0],e_lo[m0])
        ax.set_title(
            f"{title}\n{fmt_p(p)}",fontsize=8)
        ax.set_xlabel("Months",fontsize=7)
        ax.legend(fontsize=5)
        ax.set_ylim(-0.05,1.05)

    # Row 0: TCGA-CHOL panels
    if tcga_data and len(tcga_depth) > 0:
        td   = tcga_data
        ti   = np.where(td["tumour"])[0]
        t_os = td["os_time"][ti]
        e_os = td["os_event"][ti]
        vv   = (np.isfinite(t_os)
                & np.isfinite(e_os)
                & (t_os > 0))

        # A: Depth OS TCGA
        ax_a = fig.add_subplot(gs_f[0,0])
        if vv.sum() >= 8:
            dep  = tcga_depth
            med  = np.nanmedian(dep[vv])
            hi   = vv & (dep >= med)
            lo   = vv & (dep <  med)
            m_hi = t_os[hi].mean() \
                if hi.sum()>0 else np.nan
            m_lo = t_os[lo].mean() \
                if lo.sum()>0 else np.nan
            km_ax(
                ax_a,
                t_os[hi],e_os[hi],
                t_os[lo],e_os[lo],
                f"Deep n={hi.sum()} ({m_hi:.0f}mo)",
                f"Shallow n={lo.sum()} ({m_lo:.0f}mo)",
                "A — Depth OS (TCGA-CHOL)",
            )

        # B-D: Top 3 OS genes TCGA
        top_g = sorted(
            [(g,r) for g,r
             in tcga_os_res.items()
             if g != "DEPTH"
             and not np.isnan(r["p"])],
            key=lambda x: x[1]["p"],
        )[:3] if tcga_os_res else []

        for idx,(gene,r) in enumerate(top_g):
            col = idx+1
            ax  = fig.add_subplot(gs_f[0,col])
            gv  = td["expr"].get(gene)
            if gv is None: continue
            gv_t = gv[ti]
            vv2  = vv & np.isfinite(gv_t)
            if vv2.sum() < 5: continue
            med  = np.nanmedian(gv_t[vv2])
            hi   = vv2 & (gv_t >= med)
            lo   = vv2 & (gv_t <  med)
            m_hi = t_os[hi].mean() \
                if hi.sum()>0 else np.nan
            m_lo = t_os[lo].mean() \
                if lo.sum()>0 else np.nan
            km_ax(
                ax,
                t_os[hi],e_os[hi],
                t_os[lo],e_os[lo],
                f"{gene}-hi ({m_hi:.0f}mo)",
                f"{gene}-lo ({m_lo:.0f}mo)",
                f"{'BCD'[idx]} — {gene} OS TCGA",
            )

    # Row 1: Volcano + bar charts
    ax_e = fig.add_subplot(gs_f[1,0])
    diff = tcga_diff or gse_diff or {}
    if diff:
        fcs  = [r["fc"] for r in diff.values()]
        pvs  = [-np.log10(max(r["p"],1e-10))
                for r in diff.values()]
        cols = [C[1] if fc>0 else C[0]
                for fc in fcs]
        ax_e.scatter(fcs,pvs,c=cols,
                     alpha=0.6,s=30)
        ax_e.axvline(0,color="black",lw=0.5)
        ax_e.axhline(-np.log10(0.05),
                     color="grey",ls="--",lw=0.5)
        for g,(fc,pv) in zip(
            diff.keys(),zip(fcs,pvs)
        ):
            if pv>2 or abs(fc)>0.8:
                ax_e.annotate(g,(fc,pv),
                    fontsize=5,
                    xytext=(2,2),
                    textcoords="offset points")
        ax_e.set_xlabel("FC ICC vs Normal",
                        fontsize=7)
        ax_e.set_ylabel("-log10(p)",fontsize=7)
        ax_e.set_title("E — ICC vs Normal",
                       fontsize=8)

    # OS bar — TCGA
    ax_f = fig.add_subplot(gs_f[1,1])
    all_os = tcga_os_res or {}
    top_os = sorted(
        [(g,r) for g,r in all_os.items()
         if not np.isnan(r.get("p",np.nan))],
        key=lambda x: x[1]["p"],
    )[:12]
    if top_os:
        gl = [
            f"{g}\n({r['m_hi']:.0f}/"
            f"{r['m_lo']:.0f}mo)"
            for g,r in top_os
        ]
        pv = [-np.log10(max(r["p"],1e-10))
              for _,r in top_os]
        co = [C[1] if r.get("dir","")
              == "↑=worse"
              else C[0]
              for _,r in top_os]
        ax_f.barh(range(len(gl)),pv,
                  color=co,alpha=0.8)
        ax_f.axvline(-np.log10(0.05),
                     color="black",
                     ls="--",lw=1)
        ax_f.set_yticks(range(len(gl)))
        ax_f.set_yticklabels(gl,fontsize=6)
        ax_f.set_xlabel("-log10(p)",fontsize=7)
        ax_f.set_title("F — Top OS Genes TCGA",
                       fontsize=8)

    # Depth histograms
    ax_g = fig.add_subplot(gs_f[1,2])
    for dep,col,lbl in [
        (tcga_depth, C[2], "TCGA-CHOL"),
        (gse_depth,  C[3], "GEO"),
    ]:
        if dep is not None and len(dep) > 3:
            ax_g.hist(
                dep[np.isfinite(dep)],
                bins=20,alpha=0.6,
                color=col,label=lbl,
                edgecolor="white",
            )
    ax_g.set_xlabel("Depth",fontsize=7)
    ax_g.set_ylabel("n",fontsize=7)
    ax_g.legend(fontsize=6)
    ax_g.set_title("G — Depth Distributions",
                   fontsize=8)

    # Summary
    ax_h = fig.add_subplot(gs_f[2,:])
    ax_h.axis("off")
    n_icc_tcga = int(
        sum(1 for td in [tcga_data]
            if td and td["tumour"].sum() > 0)
        * (tcga_data["tumour"].sum()
           if tcga_data else 0)
    )
    sw_c = len([
        g for g in CHOL_SW
        if (tcga_diff or gse_diff or {})
        .get(g,{}).get("fc",0) < -0.2
    ])
    fa_c = len([
        g for g in ICC_FA
        if (tcga_diff or gse_diff or {})
        .get(g,{}).get("fc",0) > 0.2
    ])
    top5 = [
        f"{g}({fmt_p(r['p'])[:8]})"
        for g,r in (top_os[:5]
                    if top_os else [])
    ]
    summary = (
        "H — SCRIPT 0c SUMMARY\n"
        "═════════════════════════════"
        "═══════════════════════════════\n"
        f"TCGA-CHOL: "
        f"n={tcga_data['n'] if tcga_data else 0} "
        f"tumour={tcga_data['tumour'].sum() if tcga_data else 0} "
        f"OS valid={tcga_data['valid_os'].sum() if tcga_data else 0} "
        f"genes={len(tcga_data['expr']) if tcga_data else 0}\n"
        f"SW↓ confirmed: {sw_c}  "
        f"FA↑ confirmed: {fa_c}  "
        f"Top OS: {' | '.join(top5)}\n"
        f"OrganismCore | ICC False Attractor | "
        f"Doc 93a | 2026-03-02"
    )
    ax_h.text(
        0.01, 0.8, summary,
        transform=ax_h.transAxes,
        fontsize=8, va="top",
        fontfamily="monospace",
        bbox=dict(
            boxstyle="round",
            facecolor="#f8f8f8",
            edgecolor="#cccccc",
        ),
    )

    out = os.path.join(
        RESULTS_DIR,"icc_discovery_s0c.png"
    )
    plt.savefig(out,dpi=150,
                bbox_inches="tight")
    log(f"  Figure: {out}")
    plt.close()

# ============================================================
# MAIN
# ============================================================

def main():
    log("="*65)
    log("ICC FALSE ATTRACTOR — SCRIPT 0c")
    log("DISCOVERY — CORRECT STRATEGY")
    log("Framework: OrganismCore")
    log("Doc: 93a | Date: 2026-03-02")
    log("="*65)
    log("")
    log("STRATEGY:")
    log("  Track A: TCGA-CHOL (RNA-seq)")
    log("           Same GDC/Xena pipeline")
    log("           as TCGA-LIHC")
    log("  Track B: GSE32225 (GPL8432)")
    log("           Download GPL annotation")
    log("           file to map probes")
    log("  Platform fix: all GEO ICC")
    log("    datasets are Illumina, not")
    log("    Affymetrix. Probe maps must")
    log("    come from GPL annotation files")

    # ──────────────────────────────────────
    # TRACK A: TCGA-CHOL
    # ──────────────────────────────────────
    tcga_data = load_tcga_chol()

    tcga_depth  = np.array([])
    tcga_os_res = {}
    tcga_diff   = {}

    if (tcga_data and
            len(tcga_data["expr"]) > 0):
        ti = np.where(
            tcga_data["tumour"]
        )[0]
        ni = np.where(
            tcga_data["normal"]
        )[0]

        if len(ti) > 0:
            tcga_depth, tcga_diff, \
            tcga_os_res, tcga_dcors = \
                run_analysis(
                    "TCGA-CHOL",
                    tcga_data["expr"],
                    tcga_data["os_time"],
                    tcga_data["os_event"],
                    ti,
                    ni if len(ni) >= 3
                    else None,
                )
        else:
            log("  No tumour samples "
                "identified in TCGA-CHOL")
    else:
        log("\n  TCGA-CHOL not available.")
        log("  Proceeding with GEO only.")

    # ──────────────────────────────────────
    # TRACK B: GEO with GPL annotation
    # ──────────────────────────────────────
    log("")
    log("="*65)
    log("TRACK B: GSE32225 + GPL8432")
    log("="*65)

    gse_url = (
        "https://ftp.ncbi.nlm.nih.gov"
        "/geo/series/GSE32nnn/GSE32225"
        "/matrix/GSE32225_series_matrix"
        ".txt.gz"
    )
    gse_obj = load_gse_with_annotation(
        "GSE32225", gse_url, "GPL8432",
        min_size=100000,
    )

    gse_depth   = np.array([])
    gse_os_res  = {}
    gse_diff    = {}

    if gse_obj and len(gse_obj["expr"]) > 0:
        os_t, os_e, icc_m, nor_m = \
            parse_char_block_clinical(gse_obj)
        ti_g = np.where(icc_m)[0]
        ni_g = np.where(nor_m)[0]
        if len(ti_g) > 0:
            gse_depth, gse_diff, \
            gse_os_res, _ = run_analysis(
                "GSE32225",
                gse_obj["expr"],
                os_t, os_e,
                ti_g,
                ni_g if len(ni_g)>=3
                else None,
            )
    else:
        log("  GSE32225 genes=0 after "
            "annotation.")
        log("  Trying GSE26566 + GPL6104...")

        gse26_url = (
            "https://ftp.ncbi.nlm.nih.gov"
            "/geo/series/GSE26nnn/GSE26566"
            "/matrix/GSE26566_series_matrix"
            ".txt.gz"
        )
        gse_obj = load_gse_with_annotation(
            "GSE26566", gse26_url,
            "GPL6104", min_size=100000,
        )
        if gse_obj and \
                len(gse_obj["expr"]) > 0:
            os_t,os_e,icc_m,nor_m = \
                parse_char_block_clinical(
                    gse_obj
                )
            ti_g = np.where(icc_m)[0]
            ni_g = np.where(nor_m)[0]
            if len(ti_g) > 0:
                gse_depth, gse_diff, \
                gse_os_res, _ = run_analysis(
                    "GSE26566",
                    gse_obj["expr"],
                    os_t, os_e,
                    ti_g,
                    ni_g if len(ni_g)>=3
                    else None,
                )

    # ──────────────────────────────────────
    # SUMMARY
    # ──────────────────────────────────────
    log("")
    log("="*65)
    log("DISCOVERY SUMMARY — SCRIPT 0c")
    log("="*65)

    if tcga_data:
        log(f"\n  TCGA-CHOL:")
        log(f"  n={tcga_data['n']} "
            f"tumour={tcga_data['tumour'].sum()} "
            f"normal={tcga_data['normal'].sum()}")
        log(f"  OS valid="
            f"{tcga_data['valid_os'].sum()} "
            f"events="
            f"{int(tcga_data['os_event'][tcga_data['valid_os']].sum())}")
        log(f"  Genes={len(tcga_data['expr'])}: "
            f"{sorted(tcga_data['expr'].keys())}")

    if tcga_os_res:
        top = sorted(
            [(g,r) for g,r
             in tcga_os_res.items()
             if not np.isnan(r["p"])
             and r["p"] < 0.05],
            key=lambda x: x[1]["p"],
        )
        log(f"\n  Top OS genes (TCGA, p<0.05):")
        for g,r in top[:12]:
            log(f"    {g:<12} {fmt_p(r['p'])} "
                f"hi={r['m_hi']:.1f}mo "
                f"lo={r['m_lo']:.1f}mo "
                f"{r.get('dir','')}")

    sw_c = [g for g in CHOL_SW
            if (tcga_diff or gse_diff or {})
            .get(g,{}).get("fc",0) < -0.2]
    fa_c = [g for g in ICC_FA
            if (tcga_diff or gse_diff or {})
            .get(g,{}).get("fc",0) > 0.2]
    log(f"\n  SW↓ confirmed: {sw_c}")
    log(f"  FA↑ confirmed: {fa_c}")

    verdict = (
        "FRAMEWORK CONFIRMED — proceed S1"
        if len(sw_c)>=2 and len(fa_c)>=2
        else "PROCEED — expand in S1"
        if (len(tcga_data["expr"])>5
            if tcga_data else False)
        else "DATA MISSING — check downloads"
    )
    log(f"\n  VERDICT: {verdict}")
    log(f"\n  TCGA-CHOL is the primary "
        f"dataset for ICC series.")
    log(f"  n~36 ICC samples — small but")
    log(f"  RNA-seq + OS + mutations.")
    log(f"  GEO datasets (GSE32225, n=149)")
    log(f"  provide large n for ICC vs normal")
    log(f"  differential but no OS data.")
    log(f"  Strategy: TCGA-CHOL for OS/Cox,")
    log(f"  GSE32225 for ICC architecture.")

    generate_figure(
        tcga_data,
        tcga_depth if len(tcga_depth)>0
        else np.array([]),
        tcga_os_res, tcga_diff,
        gse_obj if gse_obj else None,
        gse_depth if len(gse_depth)>0
        else np.array([]),
        gse_os_res, gse_diff,
    )

    write_log()
    log(f"\n  Log: {LOG_FILE}")
    log(f"  Output: {RESULTS_DIR}")
    log("\n=== SCRIPT 0c COMPLETE ===")
    log("\nPaste full output for Doc 93a.")


if __name__ == "__main__":
    main()
