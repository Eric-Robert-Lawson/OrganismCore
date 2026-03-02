"""
HEPATOCELLULAR CARCINOMA — FALSE ATTRACTOR ANALYSIS
SCRIPT 5
Dataset: TCGA-LIHC (continued)
         GSE14520 (re-analysis for CDK4)
Purpose: Mutation survival (HCC-P5 final),
         stage encoding fix,
         CDK4 replication,
         exhaustion score vs OS,
         depth x exhaustion interaction,
         full Cox multivariate

Doc: 92e | Date: 2026-03-02

PREDICTIONS LOCKED 2026-03-02:
  S5-P1: CTNNB1-mut better OS (HCC-P5)
  S5-P2: TP53-mut worse OS
  S5-P3: CTNNB1-mut shallower than TP53-mut
  S5-P4: CDK4-hi worse OS in GSE14520
  S5-P5: Exhaustion-high worse OS
  S5-P6: Depth independent of stage (Cox)
  S5-P7: Deep+exhaustion-hi worst OS group

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
RESULTS_DIR = os.path.join(BASE_DIR, "results_s5")
LOG_FILE    = os.path.join(RESULTS_DIR,
                           "analysis_log_s5.txt")
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

GSE_SCORE_FILE = os.path.join(
    BASE_DIR, "results_s2",
    "depth_scores_s2.csv")

GDC_BASE = "https://api.gdc.cancer.gov"

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
    "CD68","CD247","CD44",
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
    m1 = np.isfinite(t1) & np.isfinite(e1) & (t1>0)
    m0 = np.isfinite(t0) & np.isfinite(e0) & (t0>0)
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
    v = np.isfinite(t) & np.isfinite(e) & (t>0)
    if v.sum() < 5:
        return False
    kmf.fit(t[v], e[v], label=label)
    return True

# ============================================================
# STAGE / GRADE MAPS  (fixed from Script 4)
# ============================================================

STAGE_MAP = {
    "stage i":     1, "stage ia":   1,
    "stage ib":    1, "i":          1,
    "stage ii":    2, "stage iia":  2,
    "stage iib":   2, "ii":         2,
    "stage iii":   3, "stage iiia": 3,
    "stage iiib":  3, "stage iiic": 3,
    "iii":         3,
    "stage iv":    4, "stage iva":  4,
    "stage ivb":   4, "iv":         4,
    "stage i/ii nos": 1,
    "not reported": np.nan,
    "unknown":      np.nan,
    "":             np.nan,
    "--":           np.nan,
}

GRADE_MAP = {
    "g1":1, "grade 1":1,
    "well differentiated":1,
    "g2":2, "grade 2":2,
    "moderately differentiated":2,
    "g3":3, "grade 3":3,
    "poorly differentiated":3,
    "g4":4, "grade 4":4,
    "undifferentiated":4,
    "high grade":3, "low grade":2,
    "not reported":np.nan,
    "unknown":np.nan,
    "":np.nan,
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
    return float(v) if v is not None \
        and not (isinstance(v, float)
                 and np.isnan(v)) \
        else np.nan

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
    return float(v) if v is not None \
        and not (isinstance(v, float)
                 and np.isnan(v)) \
        else np.nan

# ============================================================
# GDC MAF DOWNLOAD
# ============================================================

def download_maf_gdc():
    if os.path.exists(MAF_FILE):
        sz = os.path.getsize(MAF_FILE)
        if sz > 10000:
            log(f"  MAF present: {sz:,} bytes")
            return True
        log(f"  MAF too small ({sz}b) — "
            f"re-downloading")
        os.remove(MAF_FILE)

    log("  Querying GDC for TCGA-LIHC MAF...")

    data_types = [
        "Masked Somatic Mutation",
        "Aggregated Somatic Mutation",
    ]

    file_id = None
    for dt in data_types:
        query = {
            "filters": {
                "op": "and",
                "content": [
                    {
                        "op": "=",
                        "content": {
                            "field":
                            "cases.project"
                            ".project_id",
                            "value": "TCGA-LIHC",
                        },
                    },
                    {
                        "op": "=",
                        "content": {
                            "field": "data_type",
                            "value": dt,
                        },
                    },
                    {
                        "op": "=",
                        "content": {
                            "field": "data_format",
                            "value": "MAF",
                        },
                    },
                ],
            },
            "fields": (
                "file_id,file_name,"
                "file_size,access"
            ),
            "size": "20",
        }
        try:
            r = requests.post(
                f"{GDC_BASE}/files",
                json=query,
                headers={
                    "Content-Type":
                    "application/json"
                },
                timeout=30,
            )
            if r.status_code == 200:
                hits = (
                    r.json()
                    .get("data", {})
                    .get("hits", [])
                )
                if hits:
                    log(f"  Found {len(hits)} "
                        f"file(s) [{dt}]")
                    for h in hits:
                        log(
                            f"    {h.get('file_id','')} "
                            f"{h.get('file_name','')[:50]} "
                            f"access={h.get('access','')} "
                            f"{h.get('file_size',0):,}b"
                        )
                        if h.get("access") == "open":
                            file_id = h["file_id"]
                            break
                    if file_id is None:
                        file_id = hits[0]["file_id"]
                    break
        except Exception as e:
            log(f"  Query error: {e}")

    if file_id:
        log(f"  Downloading {file_id}...")
        try:
            r2 = requests.get(
                f"{GDC_BASE}/data/{file_id}",
                stream=True, timeout=600,
                headers={
                    "User-Agent":
                    "OrganismCore/1.0"
                },
            )
            log(f"  HTTP {r2.status_code}")
            if r2.status_code == 200:
                raw = b"".join(
                    r2.iter_content(1024*1024)
                )
                _save_maf(raw)
                sz = os.path.getsize(MAF_FILE)
                log(f"  Saved: {sz:,} bytes")
                return sz > 10000
        except Exception as e:
            log(f"  Download error: {e}")

    log("  Trying cBioPortal fallback...")
    return _cbio_maf_fallback()


def _save_maf(raw):
    import zipfile, io
    if raw[:2] == b"PK":
        zf = zipfile.ZipFile(io.BytesIO(raw))
        for name in zf.namelist():
            if ".maf" in name.lower():
                content = zf.read(name)
                with gzip.open(MAF_FILE, "wb") as f:
                    f.write(content)
                return
    if raw[:2] == b"\x1f\x8b":
        with open(MAF_FILE, "wb") as f:
            f.write(raw)
        return
    with gzip.open(MAF_FILE, "wb") as f:
        f.write(raw)


def _cbio_maf_fallback():
    CBIO = "https://www.cbioportal.org/api"
    try:
        r_s = requests.get(
            f"{CBIO}/studies/lihc_tcga/samples"
            f"?pageSize=10000",
            timeout=60,
            headers={"Accept": "application/json"},
        )
        if r_s.status_code != 200:
            log(f"  Sample list HTTP "
                f"{r_s.status_code}")
            _print_manual_instructions()
            return False

        all_sids = [
            s["sampleId"] for s in r_s.json()
        ]
        log(f"  cBioPortal samples: "
            f"{len(all_sids)}")

        profiles = [
            "lihc_tcga_mutations",
            "lihc_tcga_pan_can_atlas_2018"
            "_mutations",
        ]
        all_muts = []
        for profile in profiles:
            url_m = (
                f"{CBIO}/molecular-profiles"
                f"/{profile}/mutations/fetch"
                f"?projection=SUMMARY"
            )
            BATCH = 200
            batch_total = 0
            for i in range(
                0, len(all_sids), BATCH
            ):
                payload = {
                    "sampleIds":
                        all_sids[i:i+BATCH],
                    "hugoGeneSymbols": MUT_GENES,
                }
                try:
                    r_m = requests.post(
                        url_m, json=payload,
                        headers={
                            "Accept":
                            "application/json",
                            "Content-Type":
                            "application/json",
                        },
                        timeout=60,
                    )
                    if r_m.status_code == 200:
                        bm = r_m.json()
                        all_muts.extend(bm)
                        batch_total += len(bm)
                except Exception:
                    pass
                time.sleep(0.25)
            log(f"  Profile {profile}: "
                f"{batch_total} mutations")
            if batch_total > 0:
                break

        log(f"  Total mutations: {len(all_muts)}")
        if not all_muts:
            log("  cBioPortal: 0 mutations")
            _print_manual_instructions()
            return False

        lines = [
            "Hugo_Symbol\tTumor_Sample_Barcode\t"
            "Variant_Classification\tHGVSp_Short\t"
            "Chromosome\tStart_Position\t"
            "Reference_Allele\tTumor_Seq_Allele2"
        ]
        for m in all_muts:
            gene = (
                m.get("gene", {})
                 .get("hugoGeneSymbol", "")
                if isinstance(m.get("gene"), dict)
                else m.get(
                    "hugoGeneSymbol",
                    m.get("gene", ""))
            )
            lines.append("\t".join([
                gene,
                m.get("sampleId", ""),
                m.get("mutationType",
                      m.get(
                        "variantClassification","")),
                m.get("proteinChange", ""),
                str(m.get("chr",
                    m.get("chromosome", ""))),
                str(m.get("startPosition", "")),
                m.get("referenceAllele", ""),
                m.get("variantAllele", ""),
            ]))

        with gzip.open(
            MAF_FILE, "wt", encoding="utf-8"
        ) as f:
            f.write("\n".join(lines))
        sz = os.path.getsize(MAF_FILE)
        log(f"  MAF saved: {sz:,} bytes")
        return True

    except Exception as e:
        log(f"  cBioPortal error: {e}")
        _print_manual_instructions()
        return False


def _print_manual_instructions():
    log("")
    log("  " + "=" * 30)
    log("  MANUAL MAF DOWNLOAD REQUIRED")
    log("  " + "=" * 30)
    log("  1. https://portal.gdc.cancer.gov"
        "/repository")
    log("  2. Filters:")
    log("     Project = TCGA-LIHC")
    log("     Data Category = Simple "
        "Nucleotide Variation")
    log("     Data Type = Masked Somatic "
        "Mutation")
    log("     Experimental Strategy = WXS")
    log("     Access = Open")
    log("  3. Add to cart → Download")
    log(f"  4. Save/rename to: {MAF_FILE}")
    log("  5. Re-run script")
    log("  " + "=" * 30)

# ============================================================
# PARSE EXPRESSION
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
                        "","NA","nan","NaN","NULL"
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
    log(f"  Sample IDs[0:3]: {sample_ids[:3]}")

    stype = np.array([
        s[13:15] if len(s) >= 15 else "??"
        for s in sample_ids
    ])
    tumour = (stype == "01") | np.array([
        "-01" in s for s in sample_ids
    ])
    normal = (stype == "11") | np.array([
        "-11" in s for s in sample_ids
    ])
    hcc_idx = np.where(tumour)[0]
    df_hcc  = df[tumour].reset_index(drop=True)

    log(f"  HCC: {tumour.sum()}  "
        f"Normal: {normal.sum()}")
    log(f"  Genes: {list(df_hcc.columns)[:10]}")
    return df_hcc, df, sample_ids, hcc_idx

# ============================================================
# PARSE CLINICAL
# ============================================================

def parse_clinical(surv_file, pheno_file,
                   sample_ids):
    log("")
    log("=" * 65)
    log("PARSE CLINICAL (S5 — stage map fixed)")
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
            log(f"  Not found: {fp}")
            return
        sz = os.path.getsize(fp)
        log(f"  Parsing: {fp} ({sz:,} bytes)")
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
                    log(f"  Headers: {hdr[:15]}")
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
                            "stage",
                            "ajcc_pathol",
                            "tumor_stage",
                            "clinical_stage",
                        ]) and "stc" not in cols:
                            cols["stc"] = i
                        if any(x in h for x in [
                            "grade",
                            "neoplasm_grade",
                        ]) and "gc" not in cols:
                            cols["gc"] = i
                        if any(x in h for x in [
                            "age_at","age_diag",
                            "age_at_index",
                        ]) and "ac" not in cols:
                            cols["ac"] = i
                        if h in [
                            "gender","sex"
                        ] and "genc" not in cols:
                            cols["genc"] = i
                    log(f"  Cols: {cols}")
                    continue

                sc = cols.get("sc")
                if sc is None or sc >= len(parts):
                    continue
                sid = parts[sc].strip()
                idx = match(sid)
                if idx is None:
                    continue

                def get_col(key):
                    c = cols.get(key)
                    if c is not None \
                            and c < len(parts):
                        return parts[c].strip()
                    return None

                tv = get_col("tc")
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

                ev = get_col("ec")
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

                sv = get_col("stc")
                if sv and not stage_s[idx]:
                    stage_s[idx] = sv

                gv = get_col("gc")
                if gv and not grade_s[idx]:
                    grade_s[idx] = gv

                av = get_col("ac")
                if av and np.isnan(age[idx]):
                    try:
                        age[idx] = float(av)
                    except (ValueError,
                            TypeError):
                        pass

                gnv = get_col("genc")
                if gnv and not gender[idx]:
                    gender[idx] = gnv

    parse_file(surv_file)
    parse_file(pheno_file)

    # Encode with fixed maps
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
    log(f"\n  OS valid: {valid_os.sum()} "
        f"events="
        f"{int(os_event[valid_os].sum())}")

    from collections import Counter
    sv = stage_num[~np.isnan(stage_num)]
    gv = grade_num[~np.isnan(grade_num)]
    log(f"  Stage encoded: "
        f"{dict(Counter(sv.astype(int)).most_common())}")
    log(f"  Grade encoded: "
        f"{dict(Counter(gv.astype(int)).most_common())}")
    av = age[~np.isnan(age)]
    if len(av):
        log(f"  Age: mean={av.mean():.1f} "
            f"range={av.min():.0f}–"
            f"{av.max():.0f}")

    return {
        "os_time":   os_time,
        "os_event":  os_event,
        "stage":     stage_num,
        "grade":     grade_num,
        "age":       age,
        "gender":    np.array(gender),
        "stage_s":   np.array(stage_s),
        "grade_s":   np.array(grade_s),
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
    gene_set = set(MUT_GENES)

    if not os.path.exists(maf_file):
        log("  MAF not found — skipping")
        return mut_matrix

    sz = os.path.getsize(maf_file)
    if sz < 500:
        log(f"  MAF too small ({sz}b) — skipping")
        return mut_matrix

    log(f"  {maf_file} ({sz:,} bytes)")

    BENIGN = [
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

    hdr                  = None
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
                log(f"  Headers: {hdr[:8]}")
                for i, h in enumerate(hdr):
                    hl = h.lower()
                    if hl in [
                        "hugo_symbol","gene",
                        "gene_name",
                    ] and gene_c is None:
                        gene_c = i
                    if any(x in hl for x in [
                        "tumor_sample_barcode",
                        "tumor_sample","sampleid",
                        "sample_id",
                    ]) and sample_c is None:
                        sample_c = i
                    if any(x in hl for x in [
                        "variant_classification",
                        "consequence","effect",
                        "mutation_type",
                    ]) and effect_c is None:
                        effect_c = i
                log(f"  gene={gene_c} "
                    f"sample={sample_c} "
                    f"effect={effect_c}")
                continue

            if gene_c is None or sample_c is None:
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

    log(f"\n  Mutations parsed: {n_muts}")
    if n_muts > 0:
        log(f"\n  Frequencies:")
        log(f"  {'Gene':<14} {'n':>5} {'%':>8}")
        log(f"  {'-'*30}")
        for g in MUT_GENES:
            freq = mut_matrix[g].sum()
            if freq > 0:
                pct = 100 * freq / n
                log(f"  {g:<14} {freq:>5} "
                    f"{pct:>8.1f}%")
    return mut_matrix

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
    log(f"  Switch genes: {sw}")
    log(f"  FA genes:     {fa}")
    log(f"  mean={d.mean():.4f} "
        f"std={d.std():.4f} "
        f"range={d.min():.4f}–{d.max():.4f}")
    return d

# ============================================================
# S5-1: MUTATION SURVIVAL
# ============================================================

def mutation_survival(
    mut_matrix, os_time, os_event,
    hcc_idx, df_hcc, depth_metab,
):
    log("")
    log("=" * 65)
    log("S5-1: MUTATION SURVIVAL")
    log("S5-P1: CTNNB1-mut better OS (HCC-P5)")
    log("S5-P2: TP53-mut worse OS")
    log("S5-P3: CTNNB1-mut shallower than TP53-mut")
    log("=" * 65)

    # ── IMPORTANT: mut_matrix is indexed over
    # ALL samples (n=423). We must slice with
    # hcc_idx to get HCC-only vectors.
    t  = os_time[hcc_idx]
    e  = os_event[hcc_idx]
    gc = list(df_hcc.columns)

    # Slice mutation matrix to HCC samples once
    mut_hcc = {
        g: mut_matrix[g][hcc_idx]
        for g in MUT_GENES
    }

    total_muts = sum(
        mut_hcc[g].sum() for g in MUT_GENES
    )
    if total_muts == 0:
        log("\n  No mutation data available.")
        log("  S5-P1, P2, P3: NOT TESTABLE")
        log("  HCC-P5 remains pending.")
        return {}

    results = {}
    log(f"\n  {'Gene':<12} {'n_mut':>6} "
        f"{'mut_OS':>9} {'wt_OS':>9}  "
        f"logrank       direction")
    log(f"  {'-'*66}")

    for gene in MUT_GENES:
        gm    = mut_hcc[gene]
        n_mut = int(gm.sum())
        if n_mut < 5:
            continue

        mmask = gm == 1
        wmask = gm == 0
        vm    = (mmask & np.isfinite(t)
                 & np.isfinite(e) & (t > 0))
        vw    = (wmask & np.isfinite(t)
                 & np.isfinite(e) & (t > 0))

        m_m = t[vm].mean() if vm.sum()>0 \
            else np.nan
        m_w = t[vw].mean() if vw.sum()>0 \
            else np.nan
        p   = logrank_p(
            t[mmask], e[mmask],
            t[wmask], e[wmask],
        )
        d_m = depth_metab[mmask].mean() \
            if mmask.sum()>0 else np.nan
        d_w = depth_metab[wmask].mean() \
            if wmask.sum()>0 else np.nan

        direction = (
            "↑mut=better" if m_m > m_w
            else "↑mut=worse"
        )
        log(f"  {gene:<12} {n_mut:>6} "
            f"{m_m:>9.1f} {m_w:>9.1f}  "
            f"{fmt_p(p)}  {direction}")

        results[gene] = {
            "n_mut":  n_mut,
            "mmask":  mmask,
            "wmask":  wmask,
            "p":      p,
            "m_mut":  m_m,
            "m_wt":   m_w,
            "d_mut":  d_m,
            "d_wt":   d_w,
        }

    log("")
    for gene, better, pred in [
        ("CTNNB1", True,
         "S5-P1: CTNNB1-mut better OS (HCC-P5)"),
        ("TP53",   False,
         "S5-P2: TP53-mut worse OS"),
    ]:
        if gene not in results:
            log(f"  {pred}")
            log("  STATUS: NOT TESTABLE (n_mut<5)")
            continue
        res  = results[gene]
        conf = (
            res["m_mut"] > res["m_wt"]
            if better
            else res["m_mut"] < res["m_wt"]
        )
        sig  = (
            not np.isnan(res["p"])
            and res["p"] < 0.05
        )
        label = (
            "CONFIRMED ✓" if conf and sig
            else "DIRECTIONAL ✓" if conf
            else "NOT CONFIRMED ✗"
        )
        log(f"  {pred}")
        log(f"  n_mut={res['n_mut']}  "
            f"mut={res['m_mut']:.1f}mo  "
            f"wt={res['m_wt']:.1f}mo  "
            f"{fmt_p(res['p'])}")
        log(f"  STATUS: {label}")

    # S5-P3: depth comparison
    log("")
    log("  S5-P3: CTNNB1-mut shallower "
        "than TP53-mut")
    if "CTNNB1" in results and "TP53" in results:
        d_ct = results["CTNNB1"]["d_mut"]
        d_tp = results["TP53"]["d_mut"]
        conf = (
            not np.isnan(d_ct)
            and not np.isnan(d_tp)
            and d_ct < d_tp
        )
        log(f"  CTNNB1-mut depth: "
            f"{d_ct:.4f}")
        log(f"  TP53-mut depth:   "
            f"{d_tp:.4f}")
        log(f"  STATUS: "
            f"{'CONFIRMED ✓' if conf else 'NOT CONFIRMED ✗'}")
    else:
        log("  STATUS: NOT TESTABLE")

    # GLUL proxy
    if "CTNNB1" in results and "GLUL" in gc:
        mmask = results["CTNNB1"]["mmask"]
        wmask = results["CTNNB1"]["wmask"]
        glul  = df_hcc["GLUL"].values
        rv, pv = safe_pearsonr(
            mut_hcc["CTNNB1"].astype(float),
            glul,
        )
        m_gm = glul[mmask].mean() \
            if mmask.sum()>0 else np.nan
        m_gw = glul[wmask].mean() \
            if wmask.sum()>0 else np.nan
        _, p_g = safe_mwu(
            glul[mmask], glul[wmask]
        )
        log(f"\n  GLUL (Wnt proxy) by CTNNB1 mut:")
        log(f"  CTNNB1-mut GLUL={m_gm:.4f}  "
            f"WT GLUL={m_gw:.4f}  "
            f"{fmt_p(p_g)}")
        log(f"  r(CTNNB1_mut, GLUL) = "
            f"{rv:+.4f}  {fmt_p(pv)}")

    return results

# ============================================================
# S5-2: FULL COX WITH STAGE/GRADE (fixed)
# ============================================================

def cox_full(
    depth_metab, os_time, os_event,
    hcc_idx, clin, mut_matrix,
):
    log("")
    log("=" * 65)
    log("S5-2: FULL COX MULTIVARIATE")
    log("S5-P6: Depth independent of stage")
    log("=" * 65)

    t   = os_time[hcc_idx]
    e   = os_event[hcc_idx]

    # Slice clinical arrays to HCC samples
    stg = clin["stage"][hcc_idx]
    grd = clin["grade"][hcc_idx]
    ag  = clin["age"][hcc_idx]

    # Slice mutation matrix to HCC samples
    ctnnb1 = mut_matrix["CTNNB1"][hcc_idx]
    tp53   = mut_matrix["TP53"][hcc_idx]

    s_ok = int((~np.isnan(stg)).sum())
    g_ok = int((~np.isnan(grd)).sum())
    a_ok = int((~np.isnan(ag)).sum())
    c_ok = int(ctnnb1.sum())
    t_ok = int(tp53.sum())

    log(f"  Stage valid: {s_ok}")
    log(f"  Grade valid: {g_ok}")
    log(f"  Age valid:   {a_ok}")
    log(f"  CTNNB1 mut:  {c_ok}")
    log(f"  TP53 mut:    {t_ok}")

    def run_cox(df_c, label):
        log(f"\n  {label}:")
        try:
            dc = df_c.copy().dropna()
            dc = dc[dc["T"] > 0]
            if len(dc) < 20:
                log(f"  Skipped: n={len(dc)} < 20")
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
            cph = CoxPHFitter()
            cph.fit(dc, "T", "E")
            log(cph.summary[
                ["coef","exp(coef)","p"]
            ].to_string())
            return cph
        except Exception as ex:
            log(f"  Error: {ex}")
            return None

    # Model 1: depth alone
    cph1 = run_cox(
        pd.DataFrame({
            "T": t, "E": e,
            "depth": depth_metab,
        }),
        "Model 1: depth alone",
    )

    # Model 2: depth + age
    run_cox(
        pd.DataFrame({
            "T": t, "E": e,
            "depth": depth_metab,
            "age":   ag,
        }),
        "Model 2: depth + age",
    )

    # Model 3: depth + stage
    cph3 = None
    if s_ok >= 30:
        cph3 = run_cox(
            pd.DataFrame({
                "T":     t, "E": e,
                "depth": depth_metab,
                "stage": stg,
            }),
            "Model 3: depth + stage",
        )
        if (cph3 is not None
                and "depth" in cph3.summary.index):
            p_d = cph3.summary.loc["depth","p"]
            conf = (
                not np.isnan(p_d) and p_d < 0.05
            )
            log(f"\n  S5-P6: depth independent "
                f"of stage")
            log(f"  depth p={p_d:.6f}")
            log(f"  STATUS: "
                f"{'CONFIRMED ✓' if conf else 'NOT CONFIRMED ✗'}")
    else:
        log(f"\n  Model 3 skipped: "
            f"stage_valid={s_ok}")
        log("  S5-P6: NOT TESTABLE "
            "(stage data insufficient)")

    # Model 4: depth + grade
    if g_ok >= 30:
        run_cox(
            pd.DataFrame({
                "T":     t, "E": e,
                "depth": depth_metab,
                "grade": grd,
            }),
            "Model 4: depth + grade",
        )

    # Model 5: depth + stage + grade + age
    if s_ok >= 30 and g_ok >= 30:
        run_cox(
            pd.DataFrame({
                "T":     t, "E": e,
                "depth": depth_metab,
                "stage": stg,
                "grade": grd,
                "age":   ag,
            }),
            "Model 5: depth+stage+grade+age",
        )

    # Model 6: depth + stage + mutations
    if s_ok >= 30 and c_ok >= 5 and t_ok >= 5:
        run_cox(
            pd.DataFrame({
                "T":          t, "E": e,
                "depth":      depth_metab,
                "stage":      stg,
                "CTNNB1_mut": ctnnb1.astype(float),
                "TP53_mut":   tp53.astype(float),
            }),
            "Model 6: depth+stage+CTNNB1+TP53",
        )

    return cph3

# ============================================================
# S5-3: CDK4 IN GSE14520
# ============================================================

def cdk4_gse14520(gse_score_file):
    log("")
    log("=" * 65)
    log("S5-3: CDK4 REPLICATION — GSE14520")
    log("S5-P4: CDK4-hi worse OS in GSE14520")
    log("=" * 65)

    for fpath in [
        gse_score_file,
        os.path.join(BASE_DIR, "results_s1",
                     "depth_scores_s1.csv"),
        os.path.join(BASE_DIR, "results_s2",
                     "depth_scores_s2.csv"),
    ]:
        if os.path.exists(fpath):
            df_s = pd.read_csv(fpath)
            if "CDK4" in df_s.columns:
                log(f"  Found CDK4 in {fpath}")
                break
            log(f"  CDK4 not in {fpath} "
                f"(cols: "
                f"{list(df_s.columns)[:8]})")
    else:
        log("  CDK4 not in any GSE14520 "
            "score file.")
        log("  CDK4 was not in the 152-gene "
            "target list for Scripts 1-2.")
        log("  S5-P4: NOT TESTABLE — "
            "deferred to Script 6")
        log("  Script 6 will re-process "
            "GSE14520 with CDK4 added.")
        return {}

    return {}

# ============================================================
# S5-4: EXHAUSTION SCORE vs OS
# ============================================================

def exhaustion_analysis(
    df_hcc, depth_metab, os_time, os_event,
    hcc_idx,
):
    log("")
    log("=" * 65)
    log("S5-4: EXHAUSTION SCORE vs OS")
    log("S5-P5: Exhaustion-high worse OS")
    log("S5-P7: Deep+exhaustion-hi worst OS")
    log("=" * 65)

    t  = os_time[hcc_idx]
    e  = os_event[hcc_idx]
    gc = list(df_hcc.columns)

    ex_genes = [g for g in EXHAUSTION_GENES
                if g in gc]
    log(f"  Exhaustion genes: {ex_genes}")

    if len(ex_genes) < 3:
        log("  Too few exhaustion genes — skip")
        return {}

    ex_arr   = df_hcc[ex_genes].values
    ex_score = norm01(
        np.nanmean(ex_arr, axis=1)
    )

    rv, pv = safe_pearsonr(depth_metab, ex_score)
    log(f"\n  r(depth, exhaustion_score) = "
        f"{rv:+.4f}  {fmt_p(pv)}")

    valid  = (
        np.isfinite(t) & np.isfinite(e)
        & np.isfinite(ex_score) & (t > 0)
    )
    med_ex = np.median(ex_score[valid])
    hi_ex  = valid & (ex_score >= med_ex)
    lo_ex  = valid & (ex_score <  med_ex)
    p_ex   = logrank_p(
        t[hi_ex], e[hi_ex],
        t[lo_ex], e[lo_ex],
    )
    m_hi   = t[hi_ex].mean() \
        if hi_ex.sum()>0 else np.nan
    m_lo   = t[lo_ex].mean() \
        if lo_ex.sum()>0 else np.nan

    log(f"\n  Exhaustion OS: "
        f"hi={m_hi:.1f}mo  lo={m_lo:.1f}mo  "
        f"{fmt_p(p_ex)}")

    conf_p5 = (
        not np.isnan(m_hi)
        and not np.isnan(m_lo)
        and m_hi < m_lo
    )
    sig_p5  = (
        not np.isnan(p_ex) and p_ex < 0.05
    )
    log(f"\n  S5-P5: Exhaustion-high worse OS")
    log(f"  STATUS: "
        f"{'CONFIRMED ✓' if conf_p5 and sig_p5 else 'DIRECTIONAL ✓' if conf_p5 else 'NOT CONFIRMED ✗'} "
        f"(dir={'✓' if conf_p5 else '✗'} "
        f"sig={'✓' if sig_p5 else '✗'})")

    # Individual genes
    log(f"\n  Individual gene OS:")
    log(f"  {'Gene':<10} {'r_depth':>10}  "
        f"{'OS_p':>14}  hi_OS  lo_OS")
    log(f"  {'-'*55}")
    gene_results = {}
    for gene in ex_genes:
        gv = df_hcc[gene].values
        rv2, pv2 = safe_pearsonr(
            depth_metab, gv
        )
        vv = (
            np.isfinite(gv)
            & np.isfinite(t)
            & np.isfinite(e) & (t > 0)
        )
        if vv.sum() < 10:
            continue
        med_g = np.nanmedian(gv[vv])
        hi_g  = vv & (gv >= med_g)
        lo_g  = vv & (gv <  med_g)
        p_g   = logrank_p(
            t[hi_g], e[hi_g],
            t[lo_g], e[lo_g],
        )
        m_hg = t[hi_g].mean() \
            if hi_g.sum()>0 else np.nan
        m_lg = t[lo_g].mean() \
            if lo_g.sum()>0 else np.nan
        log(f"  {gene:<10} {rv2:>+10.4f}  "
            f"{fmt_p(p_g)}  "
            f"{m_hg:>6.1f} {m_lg:>6.1f}")
        gene_results[gene] = {
            "r":    rv2,
            "p_os": p_g,
            "m_hi": m_hg,
            "m_lo": m_lg,
            "hi":   hi_g,
            "lo":   lo_g,
        }

    # S5-P7: 4-group KM
    log("")
    log("=" * 65)
    log("S5-P7: DEPTH × EXHAUSTION 4-GROUP KM")
    log("=" * 65)

    med_d  = np.median(depth_metab[valid])
    deep   = valid & (depth_metab >= med_d)
    shall  = valid & (depth_metab <  med_d)

    groups = {
        "Deep+Exhaust-hi":  deep  & hi_ex,
        "Deep+Exhaust-lo":  deep  & lo_ex,
        "Shall+Exhaust-hi": shall & hi_ex,
        "Shall+Exhaust-lo": shall & lo_ex,
    }

    log(f"  {'Group':<22} {'n':>5} "
        f"{'OS_mean':>9}  events")
    log(f"  {'-'*46}")
    group_means = {}
    for label, mask in groups.items():
        vm   = mask & np.isfinite(t) \
            & np.isfinite(e)
        m_t  = t[vm].mean() \
            if vm.sum()>0 else np.nan
        n_ev = int(e[vm].sum()) \
            if vm.sum()>0 else 0
        log(f"  {label:<22} {vm.sum():>5} "
            f"{m_t:>9.1f}  {n_ev}")
        group_means[label] = m_t

    best  = groups["Shall+Exhaust-lo"]
    worst = groups["Deep+Exhaust-hi"]
    p_bw  = logrank_p(
        t[best],  e[best],
        t[worst], e[worst],
    )
    log(f"\n  Shall+lo vs Deep+hi: {fmt_p(p_bw)}")

    conf_p7 = (
        not np.isnan(
            group_means.get(
                "Deep+Exhaust-hi", np.nan
            )
        )
        and group_means["Deep+Exhaust-hi"]
        <= group_means.get(
            "Shall+Exhaust-lo", np.inf
        )
    )
    log(f"\n  S5-P7: Deep+exhaustion-hi worst OS")
    log(f"  Deep+hi={group_means.get('Deep+Exhaust-hi',np.nan):.1f}mo  "
        f"Shall+lo={group_means.get('Shall+Exhaust-lo',np.nan):.1f}mo")
    log(f"  STATUS: "
        f"{'CONFIRMED ✓' if conf_p7 else 'NOT CONFIRMED ✗'}")

    return {
        "ex_score":     ex_score,
        "hi_ex":        hi_ex,
        "lo_ex":        lo_ex,
        "p_ex":         p_ex,
        "m_hi":         m_hi,
        "m_lo":         m_lo,
        "gene_results": gene_results,
        "groups":       groups,
        "p_bw":         p_bw,
        "group_means":  group_means,
    }

# ============================================================
# S5-5: CDK4 ANALYSIS — TCGA-LIHC
# ============================================================

def cdk4_analysis(
    df_hcc, depth_metab, os_time,
    os_event, hcc_idx,
):
    log("")
    log("=" * 65)
    log("S5-5: CDK4 — TCGA-LIHC")
    log("CDK4 r=+0.65 OS p=0.001 (Script 4)")
    log("=" * 65)

    t  = os_time[hcc_idx]
    e  = os_event[hcc_idx]
    gc = list(df_hcc.columns)

    if "CDK4" not in gc:
        log("  CDK4 not in matrix")
        return {}

    cdk4 = df_hcc["CDK4"].values
    rv, pv = safe_pearsonr(depth_metab, cdk4)
    log(f"  r(depth, CDK4) = {rv:+.4f}  "
        f"{fmt_p(pv)}")

    valid = (
        np.isfinite(cdk4)
        & np.isfinite(t)
        & np.isfinite(e) & (t > 0)
    )
    med   = np.nanmedian(cdk4[valid])
    hi    = valid & (cdk4 >= med)
    lo    = valid & (cdk4 <  med)
    p_os  = logrank_p(
        t[hi], e[hi], t[lo], e[lo]
    )
    m_hi  = t[hi].mean() if hi.sum()>0 \
        else np.nan
    m_lo  = t[lo].mean() if lo.sum()>0 \
        else np.nan

    log(f"\n  CDK4 OS: {fmt_p(p_os)}")
    log(f"  CDK4-hi={m_hi:.1f}mo  "
        f"CDK4-lo={m_lo:.1f}mo")

    # Tertile
    t33, t67 = np.percentile(
        cdk4[valid], [33, 67]
    )
    t1 = valid & (cdk4 <= t33)
    t2 = valid & (cdk4 > t33) & (cdk4 <= t67)
    t3 = valid & (cdk4 > t67)
    p13 = logrank_p(
        t[t1], e[t1], t[t3], e[t3]
    )
    log(f"\n  CDK4 tertile OS:")
    for tlbl, tmask in [
        ("T1 low", t1), ("T2 mid", t2),
        ("T3 high", t3),
    ]:
        vm = tmask & np.isfinite(t) \
            & np.isfinite(e)
        m  = t[vm].mean() \
            if vm.sum()>0 else np.nan
        log(f"  {tlbl}: n={tmask.sum()} "
            f"OS={m:.1f}mo")
    log(f"  T3 vs T1: {fmt_p(p13)}")

    # Cox CDK4 + depth
    log(f"\n  Cox: CDK4 + depth:")
    try:
        df_c = pd.DataFrame({
            "T":     t,
            "E":     e,
            "CDK4":  cdk4,
            "depth": depth_metab,
        }).dropna()
        df_c = df_c[df_c["T"] > 0]
        for col in ["CDK4","depth"]:
            sd = df_c[col].std()
            if sd > 0:
                df_c[col] = (
                    (df_c[col] - df_c[col].mean())
                    / sd
                )
        cph = CoxPHFitter()
        cph.fit(df_c, "T", "E")
        log(cph.summary[
            ["coef","exp(coef)","p"]
        ].to_string())
    except Exception as ex:
        log(f"  Error: {ex}")

    return {
        "r":    rv,
        "p_os": p_os,
        "m_hi": m_hi,
        "m_lo": m_lo,
        "hi":   hi,
        "lo":   lo,
    }

# ============================================================
# GENERATE FIGURE
# ============================================================

def generate_figure(
    df_hcc, depth_metab,
    os_time, os_event, hcc_idx,
    mut_results, ex_results,
    cdk4_results, mut_matrix,
):
    log("")
    log("--- Generating Script 5 figure ---")

    fig = plt.figure(figsize=(30, 26))
    fig.suptitle(
        "HCC — False Attractor Script 5 | "
        "TCGA-LIHC | Mutations | Exhaustion | "
        "CDK4 | OrganismCore | 92e | 2026-03-02",
        fontsize=10, fontweight="bold", y=0.99,
    )
    gs_f = gridspec.GridSpec(
        4, 3, figure=fig,
        hspace=0.62, wspace=0.42,
    )

    t   = os_time[hcc_idx]
    e   = os_event[hcc_idx]
    kmf = KaplanMeierFitter()
    gc  = list(df_hcc.columns)
    C   = [
        "#27ae60","#e74c3c",
        "#2980b9","#8e44ad","#e67e22",
    ]

    def km_panel(ax, groups, title):
        for label, ti, ei, col in groups:
            if safe_km(kmf, ti, ei, label):
                kmf.plot_survival_function(
                    ax=ax, color=col,
                    ci_show=True, ci_alpha=0.10,
                )
        ax.set_title(title, fontsize=9)
        ax.set_xlabel("Months", fontsize=8)
        ax.legend(fontsize=6.5)
        ax.set_ylim(-0.05, 1.05)

    # Slice mutation matrix to HCC
    mut_hcc = {
        g: mut_matrix[g][hcc_idx]
        for g in MUT_GENES
    }

    # ── A: CTNNB1 mutation KM ──────────────────────────────
    ax_a = fig.add_subplot(gs_f[0, 0])
    if "CTNNB1" in mut_results:
        res = mut_results["CTNNB1"]
        km_panel(
            ax_a,
            [
                (f"CTNNB1-mut "
                 f"n={res['mmask'].sum()}",
                 t[res["mmask"]],
                 e[res["mmask"]], C[0]),
                (f"CTNNB1-WT "
                 f"n={res['wmask'].sum()}",
                 t[res["wmask"]],
                 e[res["wmask"]], C[1]),
            ],
            f"A — CTNNB1 mut OS (HCC-P5)\n"
            f"{fmt_p(res['p'])}",
        )
    else:
        ax_a.set_title(
            "A — CTNNB1 mut OS\n(no mut data)",
            fontsize=9)
        ax_a.axis("off")

    # ── B: TP53 mutation KM ────────────────────────────────
    ax_b = fig.add_subplot(gs_f[0, 1])
    if "TP53" in mut_results:
        res = mut_results["TP53"]
        km_panel(
            ax_b,
            [
                (f"TP53-mut "
                 f"n={res['mmask'].sum()}",
                 t[res["mmask"]],
                 e[res["mmask"]], C[1]),
                (f"TP53-WT "
                 f"n={res['wmask'].sum()}",
                 t[res["wmask"]],
                 e[res["wmask"]], C[0]),
            ],
            f"B — TP53 mut OS\n"
            f"{fmt_p(res['p'])}",
        )
    else:
        ax_b.set_title(
            "B — TP53 mut OS\n(no mut data)",
            fontsize=9)
        ax_b.axis("off")

    # ── C: CDK4 KM ─────────────────────────────────────────
    ax_c = fig.add_subplot(gs_f[0, 2])
    if cdk4_results and "hi" in cdk4_results:
        km_panel(
            ax_c,
            [
                (f"CDK4-hi "
                 f"n={cdk4_results['hi'].sum()}",
                 t[cdk4_results["hi"]],
                 e[cdk4_results["hi"]], C[1]),
                (f"CDK4-lo "
                 f"n={cdk4_results['lo'].sum()}",
                 t[cdk4_results["lo"]],
                 e[cdk4_results["lo"]], C[0]),
            ],
            f"C — CDK4 OS\n"
            f"{fmt_p(cdk4_results.get('p_os', np.nan))}",
        )
    else:
        ax_c.set_title("C — CDK4 OS", fontsize=9)

    # ── D: Exhaustion score KM ─────────────────────────────
    ax_d = fig.add_subplot(gs_f[1, 0])
    if ex_results and "hi_ex" in ex_results:
        km_panel(
            ax_d,
            [
                (f"Exhaust-hi "
                 f"n={ex_results['hi_ex'].sum()}",
                 t[ex_results["hi_ex"]],
                 e[ex_results["hi_ex"]], C[1]),
                (f"Exhaust-lo "
                 f"n={ex_results['lo_ex'].sum()}",
                 t[ex_results["lo_ex"]],
                 e[ex_results["lo_ex"]], C[0]),
            ],
            f"D — Exhaustion score OS\n"
            f"{fmt_p(ex_results.get('p_ex', np.nan))}",
        )
    else:
        ax_d.set_title(
            "D — Exhaustion OS", fontsize=9)

    # ── E: 4-group depth × exhaustion KM ──────────────────
    ax_e = fig.add_subplot(gs_f[1, 1])
    if ex_results and "groups" in ex_results:
        grp_colors = {
            "Deep+Exhaust-hi":  C[1],
            "Deep+Exhaust-lo":  C[4],
            "Shall+Exhaust-hi": C[2],
            "Shall+Exhaust-lo": C[0],
        }
        for lbl, mask in (
            ex_results["groups"].items()
        ):
            col = grp_colors.get(lbl, C[2])
            if safe_km(
                kmf, t[mask], e[mask],
                f"{lbl} n={mask.sum()}"
            ):
                kmf.plot_survival_function(
                    ax=ax_e, color=col,
                    ci_show=False,
                )
        p_bw = ex_results.get("p_bw", np.nan)
        ax_e.set_title(
            f"E — Depth × Exhaustion 4-group\n"
            f"Best vs worst: {fmt_p(p_bw)}",
            fontsize=9,
        )
        ax_e.set_xlabel("Months", fontsize=8)
        ax_e.legend(fontsize=5.5)
        ax_e.set_ylim(-0.05, 1.05)

    # ── F: Exhaustion score vs depth scatter ───────────────
    ax_f = fig.add_subplot(gs_f[1, 2])
    if ex_results and "ex_score" in ex_results:
        rv_f, _ = safe_pearsonr(
            depth_metab,
            ex_results["ex_score"],
        )
        ax_f.scatter(
            depth_metab,
            ex_results["ex_score"],
            alpha=0.3, s=10, c=C[2],
        )
        ax_f.set_xlabel(
            "Metabolic depth", fontsize=8)
        ax_f.set_ylabel(
            "Exhaustion score", fontsize=8)
        ax_f.set_title(
            f"F — Depth vs exhaustion\n"
            f"r={rv_f:+.3f}",
            fontsize=9,
        )

    # ── G: Mutation vs depth bar ───────────────────────────
    ax_g = fig.add_subplot(gs_f[2, 0])
    if mut_results:
        genes_g = list(mut_results.keys())
        d_muts  = [
            mut_results[g]["d_mut"]
            for g in genes_g
        ]
        d_wts   = [
            mut_results[g]["d_wt"]
            for g in genes_g
        ]
        x = np.arange(len(genes_g))
        w = 0.35
        ax_g.bar(
            x - w/2, d_muts, w,
            color=C[0], alpha=0.8,
            label="Mutant",
        )
        ax_g.bar(
            x + w/2, d_wts, w,
            color=C[1], alpha=0.8,
            label="WT",
        )
        ax_g.set_xticks(x)
        ax_g.set_xticklabels(
            genes_g, rotation=45,
            fontsize=7, ha="right",
        )
        ax_g.set_ylabel(
            "Mean depth", fontsize=8)
        ax_g.legend(fontsize=7)
        ax_g.set_title(
            "G — Mutation vs depth",
            fontsize=9,
        )
    else:
        ax_g.set_title(
            "G — Mutation vs depth\n(no data)",
            fontsize=9)
        ax_g.axis("off")

    # ── H: Mutation OS forest plot ─────────────────────────
    ax_h = fig.add_subplot(gs_f[2, 1])
    if mut_results:
        genes_h = list(mut_results.keys())
        pvals_h = [
            -np.log10(
                max(mut_results[g]["p"], 1e-10)
            ) if not np.isnan(
                mut_results[g]["p"]
            ) else 0
            for g in genes_h
        ]
        colors_h = [
            C[0]
            if mut_results[g]["m_mut"]
            > mut_results[g]["m_wt"]
            else C[1]
            for g in genes_h
        ]
        yp = range(len(genes_h))
        ax_h.barh(
            yp, pvals_h,
            color=colors_h, alpha=0.8,
        )
        ax_h.axvline(
            -np.log10(0.05),
            color="black",
            linestyle="--", linewidth=1,
        )
        ax_h.set_yticks(yp)
        ax_h.set_yticklabels(
            genes_h, fontsize=7)
        ax_h.set_xlabel(
            "-log10(p)", fontsize=8)
        ax_h.set_title(
            "H — Mutation OS summary\n"
            "(green=better, red=worse)",
            fontsize=9,
        )
    else:
        ax_h.set_title(
            "H — Mutation OS", fontsize=9)
        ax_h.axis("off")

    # ── I: CDK4 vs depth scatter ───────────────────────────
    ax_i = fig.add_subplot(gs_f[2, 2])
    if "CDK4" in gc:
        cdk4_v = df_hcc["CDK4"].values
        rv_i, _ = safe_pearsonr(
            depth_metab, cdk4_v)
        ax_i.scatter(
            depth_metab, cdk4_v,
            alpha=0.3, s=10, c=C[1],
        )
        ax_i.set_xlabel(
            "Metabolic depth", fontsize=8)
        ax_i.set_ylabel("CDK4", fontsize=8)
        ax_i.set_title(
            f"I — CDK4 vs depth\nr={rv_i:+.3f}",
            fontsize=9,
        )

    # ── J: Depth KM (baseline) ─────────────────────────────
    ax_j = fig.add_subplot(gs_f[3, 0])
    valid_j = (
        np.isfinite(t) & np.isfinite(e)
        & np.isfinite(depth_metab) & (t > 0)
    )
    if valid_j.sum() >= 10:
        med_j = np.median(depth_metab[valid_j])
        hi_j  = valid_j & (depth_metab >= med_j)
        lo_j  = valid_j & (depth_metab <  med_j)
        p_j   = logrank_p(
            t[hi_j], e[hi_j],
            t[lo_j], e[lo_j],
        )
        km_panel(
            ax_j,
            [
                (f"Deep n={hi_j.sum()}",
                 t[hi_j], e[hi_j], C[1]),
                (f"Shallow n={lo_j.sum()}",
                 t[lo_j], e[lo_j], C[0]),
            ],
            f"J — Metabolic depth OS\n"
            f"{fmt_p(p_j)}",
        )

    # ── K: Exhaustion genes vs depth ───────────────────────
    ax_k = fig.add_subplot(gs_f[3, 1])
    for gene, col in [
        ("PDCD1", C[1]), ("HAVCR2", C[2]),
        ("LAG3",  C[3]), ("CD8A",   C[0]),
    ]:
        if gene not in gc:
            continue
        rv_k, _ = safe_pearsonr(
            depth_metab,
            df_hcc[gene].values,
        )
        ax_k.scatter(
            depth_metab,
            df_hcc[gene].values,
            alpha=0.2, s=6, c=col,
            label=f"{gene} r={rv_k:+.2f}",
        )
    ax_k.set_title(
        "K — Exhaustion genes vs depth",
        fontsize=9,
    )
    ax_k.set_xlabel(
        "Metabolic depth", fontsize=8)
    ax_k.legend(fontsize=6.5)

    # ── L: Summary ─────────────────────────────────────────
    ax_l = fig.add_subplot(gs_f[3, 2])
    ax_l.axis("off")

    def pf(d, key="p"):
        v = d.get(key, np.nan) \
            if isinstance(d, dict) else np.nan
        return (
            f"{v:.4f}"
            if isinstance(v, float)
            and not np.isnan(v)
            else "N/A"
        )

    ct_res = mut_results.get("CTNNB1", {})
    tp_res = mut_results.get("TP53", {})
    ex_p   = ex_results.get("p_ex", np.nan) \
        if ex_results else np.nan
    bw_p   = ex_results.get("p_bw", np.nan) \
        if ex_results else np.nan

    summary = (
        "L — SCRIPT 5 SUMMARY\n"
        "─────────────────────────────\n"
        "PREDICTIONS:\n"
        f"  S5-P1 CTNNB1-mut better OS\n"
        f"        (HCC-P5) p={pf(ct_res)}\n"
        f"  S5-P2 TP53-mut worse OS\n"
        f"        p={pf(tp_res)}\n"
        "  S5-P3 CTNNB1-mut shallower\n"
        "        than TP53-mut\n"
        "  S5-P4 CDK4-hi worse OS (GSE)\n"
        "        deferred to Script 6\n"
        f"  S5-P5 Exhaust-hi worse OS\n"
        f"        {fmt_p(ex_p)}\n"
        "  S5-P6 Depth indep stage\n"
        f"  S5-P7 Deep+exhaust-hi worst\n"
        f"        {fmt_p(bw_p)}\n\n"
        "OrganismCore | Doc 92e | 2026-03-02"
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
        RESULTS_DIR, "hcc_tcga_s5.png")
    plt.savefig(
        out, dpi=150, bbox_inches="tight")
    log(f"\n  Figure saved: {out}")
    plt.close()

# ============================================================
# MAIN
# ============================================================

def main():
    log("=" * 65)
    log("HEPATOCELLULAR CARCINOMA — SCRIPT 5")
    log("Dataset: TCGA-LIHC (continued)")
    log("Framework: OrganismCore")
    log("Doc: 92e | Date: 2026-03-02")
    log("=" * 65)
    log("")
    log("PREDICTIONS LOCKED 2026-03-02:")
    log("S5-P1: CTNNB1-mut better OS (HCC-P5)")
    log("S5-P2: TP53-mut worse OS")
    log("S5-P3: CTNNB1-mut shallower than "
        "TP53-mut")
    log("S5-P4: CDK4-hi worse OS in GSE14520")
    log("S5-P5: Exhaustion-high worse OS")
    log("S5-P6: Depth independent of stage "
        "(Cox)")
    log("S5-P7: Deep+exhaustion-hi worst OS "
        "group")

    # ── MAF status ─────────────────────────────────���──────
    log("")
    log("=" * 65)
    log("MAF STATUS")
    log("=" * 65)
    maf_present = (
        os.path.exists(MAF_FILE)
        and os.path.getsize(MAF_FILE) > 10000
    )
    if maf_present:
        log(f"  MAF: {os.path.getsize(MAF_FILE):,} bytes ✓")
    else:
        log("  MAF not present — downloading...")
        maf_present = download_maf_gdc()
        if not maf_present:
            log("  Continuing without mutations.")

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
    # mut_matrix is indexed 0..n_samples-1
    # (all 423 samples, not just HCC)
    # All downstream functions slice with
    # hcc_idx before use.
    mut_matrix = parse_maf(MAF_FILE, sample_ids)

    # ── Depth score ───────────────────────────────────────
    log("")
    log("=" * 65)
    log("DEPTH SCORE")
    log("=" * 65)
    depth_metab = build_depth(df_hcc)

    # ── S5-1: Mutation survival ───────────────────────────
    mut_results = mutation_survival(
        mut_matrix, os_time, os_event,
        hcc_idx, df_hcc, depth_metab,
    )

    # ── S5-2: Full Cox ────────────────────────────────────
    # All arrays passed at full length;
    # cox_full slices with hcc_idx internally.
    cox_full(
        depth_metab, os_time, os_event,
        hcc_idx, clin, mut_matrix,
    )

    # ── S5-3: CDK4 in GSE14520 ───────────────────────────
    cdk4_gse14520(GSE_SCORE_FILE)

    # ── S5-4: Exhaustion analysis ─────────────────────────
    ex_results = exhaustion_analysis(
        df_hcc, depth_metab,
        os_time, os_event, hcc_idx,
    )

    # ── S5-5: CDK4 in TCGA ──────────────��────────────────
    cdk4_results = cdk4_analysis(
        df_hcc, depth_metab,
        os_time, os_event, hcc_idx,
    )

    # ── Figure ────────────────────────────────────────────
    generate_figure(
        df_hcc, depth_metab,
        os_time, os_event, hcc_idx,
        mut_results, ex_results,
        cdk4_results, mut_matrix,
    )

    # ── Save scores ───────────────────────────────────────
    ex_score = (
        ex_results.get(
            "ex_score",
            np.zeros(len(df_hcc)),
        )
        if ex_results
        else np.zeros(len(df_hcc))
    )
    pd.DataFrame({
        "sample_id": [
            sample_ids[i] for i in hcc_idx
        ],
        "depth_metabolic":  depth_metab,
        "exhaustion_score": ex_score,
        "CTNNB1_mut": (
            mut_matrix["CTNNB1"][hcc_idx]
        ),
        "TP53_mut": (
            mut_matrix["TP53"][hcc_idx]
        ),
    }).to_csv(
        os.path.join(
            RESULTS_DIR, "depth_scores_s5.csv"
        ),
        index=False,
    )

    write_log()
    log(f"\n  Log:    {LOG_FILE}")
    log(f"  Output: {RESULTS_DIR}")
    log("\n=== SCRIPT 5 COMPLETE ===")
    log("\nPaste full output for Document 92e.")


if __name__ == "__main__":
    main()
