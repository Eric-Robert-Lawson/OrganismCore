"""
BLADDER CANCER — FALSE ATTRACTOR ANALYSIS
SCRIPT 3
Dataset: TCGA-BLCA
  408 samples
  Platform: RNA-seq (RSEM)
  Mutation data: YES
  CIN/aneuploidy: YES (via SCNA)
  OS data: YES (MIBC-enriched)
  Source: UCSC Xena / GDC portal

Doc: 91c | Date: 2026-03-01

PURPOSE:
  1. Validate OS predictions from S2
     (MIBC-enriched — powered for OS)
  2. Test NP-BLCA-1: ZEB2-AURKA sign
     vs CIN burden (aneuploidy scores)
  3. Test NP-BLCA-12: ARID1A/KDM6A
     mutation + depth score
  4. Replicate FGFR isoform switch
     in independent cohort
  5. Replicate CCND1 luminal/basal divide
  6. Cross-platform confirmation of
     all S1/S2 key findings

PREDICTIONS LOCKED BEFORE DATA:
(all derived from S1/S2, 2026-03-01)

SURVIVAL (TCGA-BLCA, MIBC-enriched):
  TV-1: Luminal depth predicts OS ***
        (powered now unlike S2)
  TV-2: Basal depth predicts OS ***
  TV-3: FGFR3/CCND1/CLDN3 panel OS lum
  TV-4: TWIST1/CDK6/GATA3 panel OS bas
  TV-5: CSS basal confirmed

REPLICATION:
  TR-1: FGFR3 r>+0.50 luminal depth
  TR-2: FGFR1 r>+0.40 basal depth
  TR-3: CCND1 positive luminal depth
  TR-4: CCND1 NEGATIVE basal depth
  TR-5: GATA3 r<-0.70 basal depth
  TR-6: TWIST1 primary basal anchor
  TR-7: MCL1>BCL2 in basal depth
  TR-8: CDK6>CDK4 in basal depth
  TR-9: MSH2/MSH6 r<-0.35 luminal depth
  TR-10: SMAD3 r>+0.40 luminal depth

NOVEL TESTS:
  NP-BLCA-1: r(ZEB2,AURKA) < 0 in BLCA
             AND sign correlates with CIN
  NP-BLCA-12: ARID1A mut → higher depth
  NP-BLCA-14: OS significant in MIBC cohort
  NP-BLCA-11: S100A8 predicts OS both subtypes

Author: Eric Robert Lawson
Framework: OrganismCore
"""

import os
import re
import gzip
import requests
import numpy as np
import pandas as pd
from scipy import stats
from lifelines import KaplanMeierFitter
from lifelines.statistics import logrank_test
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import warnings
warnings.filterwarnings("ignore")

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR    = "./blca_false_attractor/"
RESULTS_DIR = os.path.join(
    BASE_DIR, "results_s3"
)
LOG_FILE = os.path.join(
    RESULTS_DIR, "analysis_log_s3.txt"
)
os.makedirs(RESULTS_DIR, exist_ok=True)

# TCGA-BLCA via UCSC Xena
# RNA-seq: RSEM normalized
EXPR_URL = (
    "https://tcga-xena-hub.s3.us-east-1"
    ".amazonaws.com/download/"
    "TCGA.BLCA.sampleMap%2FHiSeqV2_PANCAN"
    ".gz"
)
EXPR_FILE = os.path.join(
    BASE_DIR, "TCGA_BLCA_expr.gz"
)

# Clinical / survival
CLIN_URL = (
    "https://tcga-xena-hub.s3.us-east-1"
    ".amazonaws.com/download/"
    "TCGA.BLCA.sampleMap%2FBLCA_clinicalMatrix"
    ".gz"
)
CLIN_FILE = os.path.join(
    BASE_DIR, "TCGA_BLCA_clinical.gz"
)

# Mutation data
MUT_URL = (
    "https://tcga-xena-hub.s3.us-east-1"
    ".amazonaws.com/download/"
    "mc3.v0.2.8.PUBLIC.xena.gz"
)
MUT_FILE = os.path.join(
    BASE_DIR, "TCGA_BLCA_mutations.gz"
)

# SCNA (copy number) for CIN/aneuploidy
SCNA_URL = (
    "https://tcga-xena-hub.s3.us-east-1"
    ".amazonaws.com/download/"
    "TCGA.BLCA.sampleMap%2FGistic2_CopyNumber"
    "_Gistic2_all_thresholded.by_genes.gz"
)
SCNA_FILE = os.path.join(
    BASE_DIR, "TCGA_BLCA_SCNA.gz"
)

# ============================================================
# TARGET GENES
# ============================================================

TARGET_GENES = [
    # Urothelial differentiation
    "UPK1A","UPK1B","UPK2", "UPK3A",
    "UPK3B","CLDN3","CLDN4","CLDN7",
    # Luminal
    "GATA3","FOXA1","PPARG","ERBB2",
    "ERBB3","FGFR3","CCND1","CDH1",
    "KRT7", "KRT8", "KRT18","KRT19",
    "KRT20",
    # Basal
    "KRT5", "KRT14","KRT6A","TP63",
    "CD44", "S100A8","S100A9","VIM",
    "ZEB1", "ZEB2",
    # EMT
    "SNAI1","SNAI2","TWIST1","CDH2",
    "FN1",
    # RTKs
    "EGFR", "MET",  "FGFR1","FGFR2",
    "KDR",  "VEGFA","TACSTD2",
    # Immune
    "CD274","PDCD1","CD8A","FOXP3",
    "CD4",  "CD68",
    # Epigenetic
    "EZH2", "HDAC1","HDAC2","KDM6A",
    "KDM5C","DNMT3A","TET2","ARID1A",
    # Cell cycle
    "CDKN1A","CDKN2A","CDK4","CDK6",
    "CCND1","CCNE1","CCNB1","RB1",
    "E2F1", "E2F3", "CDKN1B","CDKN2B",
    # Proliferation
    "MKI67","TOP2A","AURKA","CDC20",
    "PLK1", "PCNA", "MCM2",
    # Apoptosis
    "BCL2", "MCL1", "BAX","BCL2L1",
    "BIRC5","TP53", "MDM2",
    # Wnt
    "APC",  "CTNNB1","AXIN2","AXIN1",
    "TCF7L2","LGR5", "WNT5A",
    # Oncogenes
    "MYC",  "MYCN", "PIK3CA","KRAS",
    "HRAS", "NRAS", "FGFR3",
    # Notch
    "NOTCH1","NOTCH2","HES1","JAG1",
    # TGF-B
    "TGFB1","TGFBR2","SMAD2","SMAD3",
    # Hypoxia
    "HIF1A","CA9",
    # MMR
    "MLH1", "MSH2", "MSH6",
    # Stem
    "SOX2", "SOX4", "ALDH1A1",
    # FGFR pathway
    "SPRY1","SPRY2","DUSP6",
    # Mutation targets
    "TP73", "PTEN", "TSC1",
    # Cross-cancer
    "CDX2", "FOXA2","NKX2-1",
    # Squamous
    "IVL",  "SPRR1A","DSG1","DSG3",
    "KRT10","KRT4", "KRT13",
    # ZEB2-AURKA axis
    "ZEB2", "AURKA",
]
TARGET_GENES = sorted(set(TARGET_GENES))

# Updated panels from S1/S2
LUMINAL_SWITCH = [
    "CLDN3","UPK1B","UPK3A",
    "CDKN2B","CDKN2A",
]
LUMINAL_FA = [
    "FGFR3","CCND1","GATA3",
    "FOXA1","KRT19",
]
BASAL_SWITCH = [
    "GATA3","FOXA1","PPARG",
    "KRT8", "ERBB3",
]
BASAL_FA = [
    "TWIST1","ZEB2","CDK6",
    "FN1",   "SNAI1","VIM",
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
    x, y = x[m], y[m]
    if len(x) < 5:
        return np.nan, np.nan
    return stats.pearsonr(x, y)

def safe_mwu(a, b, alt="two-sided"):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    a = a[np.isfinite(a)]
    b = b[np.isfinite(b)]
    if len(a) < 2 or len(b) < 2:
        return np.nan, np.nan
    return stats.mannwhitneyu(
        a, b, alternative=alt
    )

def norm01(s):
    s  = pd.Series(s, dtype=float)
    mn = s.min()
    mx = s.max()
    if mx > mn:
        return (s - mn) / (mx - mn)
    return pd.Series(0.5, index=s.index)

# ============================================================
# DOWNLOAD
# ============================================================

def download(url, dest, label=""):
    if os.path.exists(dest):
        log(f"  Already present: {dest} "
            f"({os.path.getsize(dest):,} bytes)")
        return True
    log(f"  Downloading {label}...")
    log(f"  URL: {url}")
    try:
        r = requests.get(url, timeout=600,
                         stream=True)
        if r.status_code == 200:
            with open(dest, "wb") as f:
                for chunk in r.iter_content(
                    chunk_size=1024*1024
                ):
                    f.write(chunk)
            log(f"  Saved: {dest} "
                f"({os.path.getsize(dest):,} bytes)")
            return True
        log(f"  HTTP {r.status_code}")
        return False
    except Exception as e:
        log(f"  Error: {e}")
        return False

# ============================================================
# LOAD EXPRESSION
# TCGA Xena format:
#   rows = genes, cols = samples
#   first col = gene symbol
#   values = log2(RSEM+1)
# ============================================================

def load_expr(filepath):
    log("")
    log("=" * 65)
    log("LOAD EXPRESSION — TCGA XENA FORMAT")
    log(f"  File: {filepath}")
    log("=" * 65)

    opener = (
        gzip.open(filepath, "rt",
                  encoding="utf-8",
                  errors="ignore")
        if filepath.endswith(".gz")
        else open(filepath, "r",
                  encoding="utf-8",
                  errors="ignore")
    )

    target_set = set(TARGET_GENES)
    header     = None
    rows       = []
    genes      = []
    n_scanned  = 0

    with opener as f:
        for line in f:
            line = line.rstrip("\n").rstrip("\r")
            parts = line.split("\t")

            if header is None:
                header = parts
                log(f"  Samples in header: "
                    f"{len(header)-1}")
                continue

            if not parts or not parts[0]:
                continue

            gene = parts[0].strip().strip('"')
            n_scanned += 1

            if gene not in target_set:
                continue

            try:
                vals = [
                    float(p)
                    if p not in [
                        "","NA","nan",
                        "null","N/A",
                    ]
                    else np.nan
                    for p in parts[1:]
                ]
            except ValueError:
                continue

            genes.append(gene)
            rows.append(vals)

    log(f"  Genes scanned: {n_scanned}")
    log(f"  Target genes found: {len(genes)}")

    if not genes:
        log("  WARNING: No target genes found")
        log("  Checking format...")
        _inspect_expr(filepath)
        return None

    # Build sample x gene dataframe
    sample_ids = [
        h.strip().strip('"')
        for h in header[1:]
    ]
    n_s = len(sample_ids)
    rows_trimmed = [
        r[:n_s] for r in rows
    ]

    df = pd.DataFrame(
        {gene: row for gene, row
         in zip(genes, rows_trimmed)},
        index=sample_ids,
        dtype=float,
    )

    # Keep only primary tumors
    # TCGA sample IDs: TCGA-XX-XXXX-01A
    # -01 = primary tumor
    # -11 = normal tissue
    tumor_mask = [
        s[13:15] in ["01","03","06"]
        if len(s) >= 15 else True
        for s in df.index
    ]
    df_tumor = df[tumor_mask]
    log(f"  Total samples   : {len(df)}")
    log(f"  Primary tumor   : {len(df_tumor)}")
    log(f"  Genes mapped    : "
        f"{len(df_tumor.columns)}")
    log(f"  Genes found     : "
        f"{sorted(df_tumor.columns.tolist())}")

    return df_tumor


def _inspect_expr(filepath):
    opener = (
        gzip.open(filepath, "rt",
                  encoding="utf-8",
                  errors="ignore")
        if filepath.endswith(".gz")
        else open(filepath, "r",
                  encoding="utf-8",
                  errors="ignore")
    )
    lines = []
    with opener as f:
        for line in f:
            lines.append(line.rstrip()[:120])
            if len(lines) >= 5:
                break
    log("  First 5 lines:")
    for l in lines:
        log(f"    {l}")

# ============================================================
# LOAD CLINICAL
# ============================================================

def load_clinical(filepath, df_expr):
    log("")
    log("=" * 65)
    log("LOAD CLINICAL — TCGA")
    log(f"  File: {filepath}")
    log("=" * 65)

    opener = (
        gzip.open(filepath, "rt",
                  encoding="utf-8",
                  errors="ignore")
        if filepath.endswith(".gz")
        else open(filepath, "r",
                  encoding="utf-8",
                  errors="ignore")
    )

    try:
        clin = pd.read_csv(
            opener, sep="\t",
            index_col=0,
            encoding="utf-8",
        )
    except Exception as e:
        log(f"  Error reading clinical: {e}")
        return None

    log(f"  Clinical shape: {clin.shape}")
    log(f"  Columns: {list(clin.columns[:20])}")

    # Align to expression samples
    shared = df_expr.index.intersection(
        clin.index
    )
    log(f"  Expr samples    : {len(df_expr)}")
    log(f"  Clinical samples: {len(clin)}")
    log(f"  Shared          : {len(shared)}")

    if len(shared) < 10:
        # Try partial ID match
        # TCGA expr: TCGA-XX-XXXX-01
        # TCGA clin: TCGA-XX-XXXX
        expr_short = {
            s[:12]: s for s in df_expr.index
        }
        clin_short = {
            s[:12]: s for s in clin.index
        }
        overlap = set(expr_short.keys()) & set(
            clin_short.keys()
        )
        log(f"  Partial ID match: {len(overlap)}")
        if overlap:
            # Reindex clin to match expr
            new_idx = {}
            for short in overlap:
                new_idx[clin_short[short]] = (
                    expr_short[short]
                )
            clin_sub = clin.loc[
                list(new_idx.keys())
            ].copy()
            clin_sub.index = [
                new_idx[i] for i in clin_sub.index
            ]
            shared = df_expr.index.intersection(
                clin_sub.index
            )
            log(f"  After rematch: {len(shared)}")
            clin = clin_sub

    # Show survival columns
    surv_cols = [
        c for c in clin.columns
        if any(
            x in c.lower()
            for x in [
                "survival","vital","days",
                "status","death","os",
                "time","follow",
            ]
        )
    ]
    log(f"\n  Survival-related columns:")
    for c in surv_cols:
        ex = clin[c].dropna().head(3).tolist()
        log(f"    {c}: {ex}")

    return clin


def extract_survival(clin, df_expr):
    """
    Extract OS time and event from
    TCGA clinical matrix.
    Multiple possible column names.
    """
    log("")
    log("  Extracting survival from clinical")

    os_time  = np.full(len(df_expr), np.nan)
    os_event = np.full(len(df_expr), np.nan)

    if clin is None:
        return os_time, os_event

    # Common TCGA survival column names
    time_candidates = [
        "OS.time","days_to_death",
        "days_to_last_followup",
        "days_to_last_follow_up",
        "_OS_IND","OS",
        "Survival_months",
        "survival_time",
    ]
    event_candidates = [
        "OS","vital_status",
        "_OS","OS_IND",
        "vital status",
        "Survival_status",
    ]

    time_col  = None
    event_col = None

    for c in time_candidates:
        if c in clin.columns:
            time_col = c
            break
    for c in event_candidates:
        if c in clin.columns:
            event_col = c
            break

    log(f"  Time col  : {time_col}")
    log(f"  Event col : {event_col}")

    if time_col is None:
        # Show all columns for inspection
        log(f"  All clinical cols:")
        for c in clin.columns:
            log(f"    {c}")
        return os_time, os_event

    for i, sid in enumerate(df_expr.index):
        if sid not in clin.index:
            continue
        row = clin.loc[sid]

        # Time
        if time_col and time_col in row.index:
            tv = row[time_col]
            try:
                t = float(tv)
                if not np.isnan(t) and t > 0:
                    # Convert days to months
                    if t > 365:
                        t = t / 30.44
                    elif t > 30:
                        t = t / 30.44
                    os_time[i] = t
            except (ValueError, TypeError):
                pass

        # Event
        if event_col and event_col in row.index:
            ev = str(row[event_col]).lower()
            if any(
                x in ev for x in [
                    "dead","1","deceased",
                    "died","death",
                ]
            ):
                os_event[i] = 1
            elif any(
                x in ev for x in [
                    "alive","0","living",
                    "censored","censor",
                ]
            ):
                os_event[i] = 0

    valid = (
        ~np.isnan(os_time)
        & ~np.isnan(os_event)
        & (os_time > 0)
    )
    log(f"  Valid OS: {valid.sum()}")
    if valid.sum() > 0:
        t_valid = os_time[valid]
        e_valid = os_event[valid]
        log(f"  Time range: "
            f"{t_valid.min():.1f}–"
            f"{t_valid.max():.1f} months")
        n1 = int(e_valid.sum())
        n0 = int((e_valid == 0).sum())
        log(f"  Events: {n1} deaths, "
            f"{n0} alive")

    return os_time, os_event

# ============================================================
# LOAD MUTATIONS
# ============================================================

def load_mutations(mut_file, df_expr):
    log("")
    log("=" * 65)
    log("LOAD MUTATIONS")
    log(f"  File: {mut_file}")
    log("=" * 65)

    if not os.path.exists(mut_file):
        log("  Mutation file missing — skip")
        return None

    opener = (
        gzip.open(mut_file, "rt",
                  encoding="utf-8",
                  errors="ignore")
        if mut_file.endswith(".gz")
        else open(mut_file, "r",
                  encoding="utf-8",
                  errors="ignore")
    )

    try:
        mut = pd.read_csv(
            opener, sep="\t",
            encoding="utf-8",
            low_memory=False,
        )
    except Exception as e:
        log(f"  Error: {e}")
        return None

    log(f"  Mutations shape: {mut.shape}")
    log(f"  Columns: {list(mut.columns[:10])}")

    # Filter to BLCA samples
    sample_col = None
    gene_col   = None
    for c in mut.columns:
        if c.lower() in [
            "sample","sampleid",
            "tumor_sample_barcode",
            "sample_id",
        ]:
            sample_col = c
        if c.lower() in [
            "gene","hugo_symbol",
            "gene_id","symbol",
        ]:
            gene_col = c

    log(f"  Sample col: {sample_col}")
    log(f"  Gene col  : {gene_col}")

    if sample_col is None or gene_col is None:
        log("  Cannot find required columns")
        return None

    # Get BLCA sample IDs
    blca_ids = set()
    for sid in df_expr.index:
        blca_ids.add(sid[:12])
        blca_ids.add(sid)

    mut["_short"] = mut[sample_col].str[:12]
    blca_mut = mut[
        mut["_short"].isin(blca_ids)
    ]
    log(f"  BLCA mutations: {len(blca_mut)}")

    if len(blca_mut) == 0:
        log("  No BLCA mutations found")
        log("  Sample ID mismatch likely")
        log(f"  Example mut IDs: "
            f"{mut[sample_col].head(3).tolist()}")
        log(f"  Example expr IDs: "
            f"{df_expr.index[:3].tolist()}")
        return None

    # Build mutation matrix
    # genes of interest
    mut_genes = [
        "ARID1A","KDM6A","TP53","FGFR3",
        "RB1","PIK3CA","CDKN2A","TSC1",
        "ERBB2","ERBB3","KDM5C","KDM6A",
        "MLL2","ELF3","STAG2",
    ]

    mut_dict = {}
    for gene in mut_genes:
        gene_mut = blca_mut[
            blca_mut[gene_col] == gene
        ]
        if len(gene_mut) == 0:
            continue
        mutated_samples = set(
            gene_mut["_short"].tolist()
        )
        mut_arr = np.zeros(len(df_expr))
        for i, sid in enumerate(df_expr.index):
            if (
                sid[:12] in mutated_samples
                or sid in mutated_samples
            ):
                mut_arr[i] = 1
        n_mut = int(mut_arr.sum())
        if n_mut > 0:
            mut_dict[gene] = mut_arr
            log(f"  {gene}: {n_mut} mutated "
                f"({100*n_mut/len(df_expr):.1f}%)")

    log(f"  Genes with mutations: "
        f"{list(mut_dict.keys())}")

    return mut_dict

# ============================================================
# COMPUTE CIN SCORE FROM SCNA
# ============================================================

def compute_cin_score(scna_file, df_expr):
    log("")
    log("=" * 65)
    log("COMPUTE CIN SCORE FROM SCNA")
    log(f"  File: {scna_file}")
    log("=" * 65)

    if not os.path.exists(scna_file):
        log("  SCNA file missing — skip")
        return None

    opener = (
        gzip.open(scna_file, "rt",
                  encoding="utf-8",
                  errors="ignore")
        if scna_file.endswith(".gz")
        else open(scna_file, "r",
                  encoding="utf-8",
                  errors="ignore")
    )

    try:
        scna = pd.read_csv(
            opener, sep="\t",
            index_col=0,
            encoding="utf-8",
        )
    except Exception as e:
        log(f"  Error: {e}")
        return None

    log(f"  SCNA shape: {scna.shape}")

    # Match sample IDs
    # SCNA cols may be short form
    scna_samples = scna.columns.tolist()
    log(f"  SCNA sample example: "
        f"{scna_samples[:3]}")
    log(f"  Expr sample example: "
        f"{df_expr.index[:3].tolist()}")

    # Build short-to-long map
    short_to_expr = {}
    for sid in df_expr.index:
        short_to_expr[sid[:15]] = sid
        short_to_expr[sid[:12]] = sid
        short_to_expr[sid]      = sid

    # CIN = fraction of genome altered
    # = number of non-zero GISTIC calls
    # per sample (excluding 0)
    cin_scores = {}

    for col in scna.columns:
        sid_match = (
            short_to_expr.get(col)
            or short_to_expr.get(col[:15])
            or short_to_expr.get(col[:12])
        )
        if sid_match is None:
            continue
        vals = scna[col].values
        finite = vals[np.isfinite(vals)]
        if len(finite) == 0:
            continue
        # CIN = fraction altered
        # (|GISTIC| >= 1 = amplification
        #  or deep deletion)
        cin = np.mean(np.abs(finite) >= 1)
        cin_scores[sid_match] = cin

    log(f"  CIN scores computed: "
        f"{len(cin_scores)}")

    if cin_scores:
        cin_arr = np.full(len(df_expr), np.nan)
        for i, sid in enumerate(df_expr.index):
            if sid in cin_scores:
                cin_arr[i] = cin_scores[sid]
        valid = ~np.isnan(cin_arr)
        log(f"  Mapped to expr: {valid.sum()}")
        if valid.sum() > 0:
            log(f"  CIN range: "
                f"{cin_arr[valid].min():.3f}–"
                f"{cin_arr[valid].max():.3f}")
        return pd.Series(
            cin_arr, index=df_expr.index
        )

    return None

# ============================================================
# CLASSIFY SUBTYPES
# ============================================================

def classify_subtypes(df_expr):
    log("")
    log("=" * 65)
    log("CLASSIFY SUBTYPES")
    log("GATA3/KRT5 median split")
    log("=" * 65)

    gc = list(df_expr.columns)
    g3 = "GATA3" in gc
    k5 = "KRT5"  in gc

    log(f"  GATA3 present: {g3}")
    log(f"  KRT5  present: {k5}")

    subtype = pd.Series(
        "Tumor", index=df_expr.index
    )

    if g3 and k5:
        g3n = norm01(df_expr["GATA3"].values)
        k5n = norm01(df_expr["KRT5"].values)
        score = g3n.values - k5n.values
        med   = np.median(score)
        for s, sc in zip(df_expr.index, score):
            subtype[s] = (
                "Luminal" if sc >= med
                else "Basal"
            )
        log(f"  Luminal: "
            f"{(subtype=='Luminal').sum()}")
        log(f"  Basal  : "
            f"{(subtype=='Basal').sum()}")

        # Validate
        lum_idx = subtype[
            subtype == "Luminal"
        ].index
        bas_idx = subtype[
            subtype == "Basal"
        ].index
        _, pg = safe_mwu(
            df_expr.loc[lum_idx, "GATA3"].values,
            df_expr.loc[bas_idx, "GATA3"].values,
            "two-sided",
        )
        _, pk = safe_mwu(
            df_expr.loc[lum_idx, "KRT5"].values,
            df_expr.loc[bas_idx, "KRT5"].values,
            "two-sided",
        )
        log(f"  GATA3 Luminal vs Basal: "
            f"{fmt_p(pg)}")
        log(f"  KRT5  Luminal vs Basal: "
            f"{fmt_p(pk)}")

        # Show key gene means
        log(f"\n  {'Gene':<10} {'Luminal':>10} "
            f"{'Basal':>10}")
        for gene in [
            "GATA3","KRT5","FGFR3",
            "TWIST1","CCND1","UPK2",
            "TP63","EGFR","AURKA","ZEB2",
        ]:
            if gene not in gc:
                continue
            lm = df_expr.loc[
                lum_idx, gene
            ].mean()
            bm = df_expr.loc[
                bas_idx, gene
            ].mean()
            log(f"  {gene:<10} {lm:>10.4f} "
                f"{bm:>10.4f}")

    return subtype

# ============================================================
# DEPTH SCORE
# ============================================================

def build_depth(df, switch, fa, label):
    gc  = list(df.columns)
    sw  = [g for g in switch if g in gc]
    fa_ = [g for g in fa     if g in gc]
    depth = pd.Series(
        np.zeros(len(df)),
        index=df.index, dtype=float,
    )
    n = 0
    if sw:
        depth += (
            1 - norm01(df[sw].mean(axis=1))
        )
        n += 1
    if fa_:
        depth += norm01(
            df[fa_].mean(axis=1)
        )
        n += 1
    if n > 0:
        depth /= n
    log(f"  {label} (n={len(df)}): "
        f"mean={depth.mean():.4f} "
        f"std={depth.std():.4f} "
        f"sw={sw} fa={fa_}")
    return depth

# ============================================================
# REPLICATION TESTS
# ============================================================

def replication_tests(
    lum, bas, l_depth, b_depth
):
    log("")
    log("=" * 65)
    log("REPLICATION TESTS")
    log("GSE13507 findings → TCGA-BLCA")
    log("=" * 65)

    gc_l = list(lum.columns)
    gc_b = list(bas.columns)

    tests = [
        # (id, gene, subtype, df, depth,
        #  direction, threshold)
        ("TR-1",  "FGFR3",  "Lum", lum,
         l_depth, "+", 0.50),
        ("TR-2",  "FGFR1",  "Bas", bas,
         b_depth, "+", 0.40),
        ("TR-3",  "CCND1",  "Lum", lum,
         l_depth, "+", 0.00),
        ("TR-4",  "CCND1",  "Bas", bas,
         b_depth, "-", 0.00),
        ("TR-5",  "GATA3",  "Bas", bas,
         b_depth, "-", -0.70),
        ("TR-6",  "TWIST1", "Bas", bas,
         b_depth, "+", 0.50),
        ("TR-7a", "MCL1",   "Bas", bas,
         b_depth, "+", 0.30),
        ("TR-7b", "BCL2",   "Bas", bas,
         b_depth, "+", 0.00),
        ("TR-8a", "CDK6",   "Bas", bas,
         b_depth, "+", 0.50),
        ("TR-8b", "CDK4",   "Bas", bas,
         b_depth, "+", -0.10),
        ("TR-9a", "MSH2",   "Lum", lum,
         l_depth, "-", -0.30),
        ("TR-9b", "MSH6",   "Lum", lum,
         l_depth, "-", -0.30),
        ("TR-10", "SMAD3",  "Lum", lum,
         l_depth, "+", 0.40),
        ("TR-11", "S100A8", "Bas", bas,
         b_depth, "+", 0.20),
        ("TR-12", "KDM6A",  "Lum", lum,
         l_depth, "-", -0.10),
        ("TR-13", "ARID1A", "Lum", lum,
         l_depth, "-", -0.10),
    ]

    log(f"\n  {'ID':<8} {'Gene':<10} "
        f"{'Sub':<5} {'r':>8}  "
        f"p-value        Threshold  Result")
    log(f"  {'-'*68}")

    confirmed = total = 0
    for (
        tid, gene, sub_label, df_,
        depth_, direction, threshold,
    ) in tests:
        gc_ = list(df_.columns)
        if gene not in gc_:
            log(f"  {tid:<8} {gene:<10} "
                f"{sub_label:<5} NOT IN MATRIX")
            continue

        rv, pv = safe_pearsonr(
            depth_.values, df_[gene].values
        )
        if not np.isnan(rv):
            total += 1
            ok = (
                rv >= threshold
                if direction == "+"
                else rv <= threshold
            )
            if ok:
                confirmed += 1
            result = "✓" if ok else "✗"
        else:
            result = "?"

        thr_str = (
            f"{'≥' if direction=='+' else '≤'}"
            f"{threshold:.2f}"
        )
        log(
            f"  {tid:<8} {gene:<10} "
            f"{sub_label:<5} {rv:>+8.4f}  "
            f"{fmt_p(pv):>14}  "
            f"{thr_str:>10}  {result}"
            if not np.isnan(rv)
            else
            f"  {tid:<8} {gene:<10} "
            f"{sub_label:<5} N/A"
        )

    if total > 0:
        pct = 100 * confirmed / total
        log(f"\n  Replicated: {confirmed}/{total} "
            f"({pct:.0f}%)")

    # FGFR isoform switch
    log(f"\n  FGFR ISOFORM SWITCH REPLICATION:")
    for gene in ["FGFR3","FGFR1"]:
        rl = rb = np.nan
        if gene in gc_l:
            rl, _ = safe_pearsonr(
                l_depth.values,
                lum[gene].values,
            )
        if gene in gc_b:
            rb, _ = safe_pearsonr(
                b_depth.values,
                bas[gene].values,
            )
        log(f"  {gene}: luminal r={rl:+.4f}  "
            f"basal r={rb:+.4f}")

# ============================================================
# ZEB2-AURKA CIN TEST
# NP-BLCA-1
# ============================================================

def zeb2_aurka_cin_test(
    lum, bas, normal_df,
    cin_series, subtype,
):
    log("")
    log("=" * 65)
    log("ZEB2-AURKA × CIN TEST")
    log("NP-BLCA-1: sign encodes CIN burden")
    log("STAD r=+0.99 | EAC r=+0.47")
    log("GSE13507 BLCA r=-0.43")
    log("Prediction: r<0 in BLCA TCGA")
    log("AND: |r| correlates with CIN")
    log("=" * 65)

    # ZEB2-AURKA per subtype
    results = {}
    for label, df_ in [
        ("Luminal", lum),
        ("Basal",   bas),
    ]:
        gc_ = list(df_.columns)
        if "ZEB2" not in gc_ or "AURKA" not in gc_:
            log(f"  {label}: ZEB2 or AURKA missing")
            continue
        rv, pv = safe_pearsonr(
            df_["ZEB2"].values,
            df_["AURKA"].values,
        )
        log(f"  {label} (n={len(df_)}): "
            f"r(ZEB2,AURKA) = {rv:+.4f}  "
            f"{fmt_p(pv)}")
        results[label] = (rv, pv)
        if not np.isnan(rv):
            if rv < 0:
                log(f"  Negative coupling confirmed ✓")
            else:
                log(f"  Coupling positive — unexpected")

    # Cross-cancer summary
    log(f"\n  CROSS-CANCER ZEB2-AURKA SUMMARY:")
    log(f"  Cancer    r(ZEB2,AURKA)  CIN level")
    log(f"  {'STAD':<10} r=+0.9871     HIGH")
    log(f"  {'EAC':<10} r=+0.4675     MOD")
    for label, (rv, _) in results.items():
        log(f"  {label+'-BLCA':<10} "
            f"r={rv:+.4f}     ??? (test)")

    # Test r(ZEB2,AURKA) vs CIN score
    if cin_series is not None:
        log(f"\n  r(ZEB2,AURKA) vs CIN burden:")
        log(f"  (sample-level test)")
        gc_all = list(lum.columns)
        if "ZEB2" in gc_all and "AURKA" in gc_all:
            # Use all samples (lum+bas)
            all_idx = lum.index.union(bas.index)
            all_df  = pd.concat([lum, bas])
            cin_aligned = cin_series.reindex(
                all_df.index
            )
            valid = (
                ~np.isnan(cin_aligned.values)
                & all_df["ZEB2"].notna().values
                & all_df["AURKA"].notna().values
            )
            if valid.sum() >= 20:
                # Per-sample ZEB2-AURKA product
                # as coupling proxy
                zeb2 = all_df["ZEB2"].values[valid]
                aurka = all_df["AURKA"].values[valid]
                cin_v = cin_aligned.values[valid]
                # r(AURKA, CIN) and r(ZEB2, CIN)
                r_aurka_cin, p_aurka_cin = (
                    safe_pearsonr(cin_v, aurka)
                )
                r_zeb2_cin, p_zeb2_cin = (
                    safe_pearsonr(cin_v, zeb2)
                )
                log(f"  r(AURKA, CIN) = "
                    f"{r_aurka_cin:+.4f}  "
                    f"{fmt_p(p_aurka_cin)}")
                log(f"  r(ZEB2,  CIN) = "
                    f"{r_zeb2_cin:+.4f}  "
                    f"{fmt_p(p_zeb2_cin)}")
                log(f"  NP-BLCA-1 test:")
                log(f"  Predict AURKA correlates"
                    f" with CIN more than ZEB2")
                if (
                    not np.isnan(r_aurka_cin)
                    and not np.isnan(r_zeb2_cin)
                ):
                    if r_aurka_cin > r_zeb2_cin:
                        log(f"  AURKA tracks CIN more "
                            f"than ZEB2 ✓")
                    else:
                        log(f"  ZEB2 tracks CIN more "
                            f"than AURKA")

    return results

# ============================================================
# MUTATION DEPTH TEST
# NP-BLCA-12
# ============================================================

def mutation_depth_test(
    mut_dict, lum, bas,
    l_depth, b_depth,
):
    log("")
    log("=" * 65)
    log("MUTATION × DEPTH TEST")
    log("NP-BLCA-12: ARID1A/KDM6A mutation")
    log("→ higher depth score")
    log("=" * 65)

    if mut_dict is None:
        log("  No mutation data")
        return

    genes_to_test = [
        "ARID1A","KDM6A","TP53","FGFR3",
        "RB1","PIK3CA","TSC1",
    ]

    for subtype_label, df_, depth_ in [
        ("Luminal", lum, l_depth),
        ("Basal",   bas, b_depth),
    ]:
        log(f"\n  {subtype_label}:")
        log(f"  {'Gene':<10} {'n_mut':>7} "
            f"{'n_wt':>7}  "
            f"{'mut_depth':>10} "
            f"{'wt_depth':>10}  p-value")
        log(f"  {'-'*62}")

        for gene in genes_to_test:
            if gene not in mut_dict:
                continue

            mut_arr = mut_dict[gene]
            # Align to subtype
            mut_aligned = pd.Series(
                mut_arr, index=lum.index
                if subtype_label == "Luminal"
                else bas.index,
            )
            # Only use samples in this subtype
            idx = df_.index.intersection(
                mut_aligned.index
            )
            if len(idx) < 5:
                continue

            mut_s = mut_aligned.loc[idx]
            dep_s = depth_.loc[idx]

            mut_mask = mut_s == 1
            wt_mask  = mut_s == 0

            n_mut = mut_mask.sum()
            n_wt  = wt_mask.sum()

            if n_mut < 3 or n_wt < 3:
                continue

            mut_depths = dep_s[mut_mask].values
            wt_depths  = dep_s[wt_mask].values

            _, p = safe_mwu(
                mut_depths, wt_depths,
                "two-sided",
            )
            d_mut = np.mean(mut_depths)
            d_wt  = np.mean(wt_depths)

            conf = ""
            if gene in ["ARID1A","KDM6A"]:
                pred = "higher depth in mut"
                conf = (
                    "✓" if d_mut > d_wt
                    else "✗"
                )

            log(f"  {gene:<10} {n_mut:>7} "
                f"{n_wt:>7}  "
                f"{d_mut:>10.4f} "
                f"{d_wt:>10.4f}  "
                f"{fmt_p(p)}  {conf}")

# ============================================================
# SURVIVAL ANALYSIS
# ============================================================

def run_survival(
    df, depth, os_time, os_event,
    label, panel_genes=None,
    panel_dirs=None,
):
    log("")
    log("=" * 65)
    log(f"SURVIVAL — {label}")
    log("=" * 65)

    t = os_time[
        np.isin(
            np.arange(len(os_time)),
            [df.index.get_loc(s)
             for s in df.index
             if s in df.index],
        )
    ] if False else None

    # Direct alignment
    all_idx  = np.arange(len(df))
    t_arr    = os_time[
        [df.index.get_loc(s)
         if s in df.index else 0
         for s in df.index]
    ] if False else os_time

    # Use positional alignment
    # df.index maps to df_expr.index
    # os_time/os_event are aligned to
    # df_expr.index positionally
    # Need to get positions of df in df_expr
    # This is passed through — use
    # the surv dataframe approach

    log(f"  Using survival aligned to "
        f"subtype (n={len(df)})")

    # Build local surv from passed arrays
    # os_time and os_event are full arrays
    # aligned to df_expr; df is a subset
    # We need to subset them
    # df.index contains GSM/TCGA IDs
    # These are passed as positional arrays
    # — must use mask approach

    return None  # placeholder;
    # actual logic below


def survival_analysis_full(
    lum, bas, os_time, os_event,
    df_expr, label_lum="Luminal",
    label_bas="Basal",
):
    """
    Run survival for luminal and basal
    using positional alignment to df_expr.
    """
    log("")
    log("=" * 65)
    log("SURVIVAL ANALYSIS")
    log("OS — TCGA-BLCA (MIBC-enriched)")
    log("=" * 65)

    n_total = len(df_expr)

    # Get positions of luminal/basal in df_expr
    lum_pos = [
        df_expr.index.get_loc(s)
        for s in lum.index
        if s in df_expr.index
    ]
    bas_pos = [
        df_expr.index.get_loc(s)
        for s in bas.index
        if s in df_expr.index
    ]

    results = {}
    for label, positions, df_ in [
        (label_lum, lum_pos, lum),
        (label_bas, bas_pos, bas),
    ]:
        log(f"\n  {label}:")

        t_sub = os_time[positions]
        e_sub = os_event[positions]

        valid = (
            ~np.isnan(t_sub)
            & ~np.isnan(e_sub)
            & (t_sub > 0)
        )
        log(f"  n={len(positions)}, "
            f"valid OS={valid.sum()}")

        if valid.sum() < 10:
            log(f"  Insufficient OS data")
            results[label] = None
            continue

        t_v = t_sub[valid]
        e_v = e_sub[valid]
        df_v = df_.iloc[
            np.where(valid)[0]
        ]

        log(f"  OS: "
            f"{t_v.min():.1f}–"
            f"{t_v.max():.1f} months")
        log(f"  Events: "
            f"{int(e_v.sum())} / {len(e_v)}")

        # Build depth for valid subset
        gc_ = list(df_v.columns)
        if label == label_lum:
            sw  = [
                g for g in LUMINAL_SWITCH
                if g in gc_
            ]
            fa_ = [
                g for g in LUMINAL_FA
                if g in gc_
            ]
            pg  = ["FGFR3","CCND1","CLDN3"]
            pd_ = ["+","+","-"]
        else:
            sw  = [
                g for g in BASAL_SWITCH
                if g in gc_
            ]
            fa_ = [
                g for g in BASAL_FA
                if g in gc_
            ]
            pg  = ["TWIST1","CDK6","GATA3"]
            pd_ = ["+","+","-"]

        depth_v = pd.Series(
            np.zeros(len(df_v)),
            index=df_v.index,
        )
        nd = 0
        if sw:
            depth_v += (
                1 - norm01(
                    df_v[sw].mean(axis=1)
                )
            )
            nd += 1
        if fa_:
            depth_v += norm01(
                df_v[fa_].mean(axis=1)
            )
            nd += 1
        if nd > 0:
            depth_v /= nd

        d_v = depth_v.values
        med = np.median(d_v)
        hi  = d_v >= med
        lo  = ~hi

        try:
            res = logrank_test(
                t_v[hi], t_v[lo],
                e_v[hi], e_v[lo],
            )
            p_depth = res.p_value
        except Exception:
            p_depth = np.nan

        log(f"  Depth vs OS:")
        log(f"  Deep     (n={hi.sum()}): "
            f"mean={t_v[hi].mean():.1f} mo")
        log(f"  Shallow  (n={lo.sum()}): "
            f"mean={t_v[lo].mean():.1f} mo")
        log(f"  Log-rank : {fmt_p(p_depth)}")

        if not np.isnan(p_depth):
            if p_depth < 0.05:
                log(f"  Depth predicts OS ✓")
            else:
                log(f"  Depth does not predict "
                    f"OS ✗")

        # Panel test
        panel_avail = [
            (g, d)
            for g, d in zip(pg, pd_)
            if g in gc_
        ]
        p_panel = np.nan
        phi = plo = None
        if len(panel_avail) >= 2:
            parts = []
            for gene, direction in panel_avail:
                ns = norm01(df_v[gene].values)
                parts.append(
                    1 - ns
                    if direction == "-"
                    else ns
                )
            panel_score = np.mean(
                parts, axis=0
            )
            pmed = np.median(panel_score)
            phi  = panel_score >= pmed
            plo  = ~phi
            try:
                res_p = logrank_test(
                    t_v[phi], t_v[plo],
                    e_v[phi], e_v[plo],
                )
                p_panel = res_p.p_value
            except Exception:
                p_panel = np.nan

            log(f"\n  Panel "
                f"{[g for g,_ in panel_avail]}:")
            log(f"  Panel-high (n={phi.sum()}): "
                f"mean={t_v[phi].mean():.1f} mo")
            log(f"  Panel-low  (n={plo.sum()}): "
                f"mean={t_v[plo].mean():.1f} mo")
            log(f"  Log-rank: {fmt_p(p_panel)}")

        # Individual gene tests
        log(f"\n  Individual gene OS tests "
            f"(p<0.05):")
        log(f"  {'Gene':<12}  p-value")
        gene_results = {}
        for gene in sorted(gc_):
            vals = df_v[gene].values
            gmed = np.nanmedian(vals)
            ghi  = vals >= gmed
            glo  = ~ghi
            if ghi.sum() < 5 or glo.sum() < 5:
                continue
            try:
                res = logrank_test(
                    t_v[ghi], t_v[glo],
                    e_v[ghi], e_v[glo],
                )
                p = res.p_value
            except Exception:
                p = np.nan
            gene_results[gene] = p
            if not np.isnan(p) and p < 0.05:
                log(f"  {gene:<12}  {fmt_p(p)}")

        results[label] = {
            "t": t_v, "e": e_v,
            "hi": hi, "lo": lo,
            "p_depth": p_depth,
            "phi": phi, "plo": plo,
            "p_panel": p_panel,
            "df_v": df_v,
            "gene_results": gene_results,
            "label": label,
        }

    return results

# ============================================================
# GENERATE FIGURE
# ============================================================

def generate_figure(
    lum, bas, l_depth, b_depth,
    surv_results, zeb2_results,
    cin_series,
):
    log("")
    log("--- Generating Script 3 figure ---")

    fig = plt.figure(figsize=(28, 22))
    fig.suptitle(
        "Bladder Cancer — False Attractor "
        "Analysis\n"
        "Script 3 | TCGA-BLCA | "
        "Replication + CIN + Survival\n"
        "OrganismCore | Doc 91c | 2026-03-01",
        fontsize=10, fontweight="bold",
        y=0.99,
    )

    gs_f = gridspec.GridSpec(
        3, 3, figure=fig,
        hspace=0.55, wspace=0.45,
    )

    COLORS = {
        "Luminal": "#2980b9",
        "Basal":   "#e74c3c",
    }

    def km_plot(ax, result, title):
        if result is None:
            ax.text(
                0.5, 0.5,
                "No data",
                ha="center", va="center",
                transform=ax.transAxes,
            )
            ax.set_title(title, fontsize=9)
            return
        t  = result["t"]
        e  = result["e"]
        hi = result["hi"]
        lo = result["lo"]
        p  = result["p_depth"]
        kmf = KaplanMeierFitter()
        kmf.fit(
            t[hi], e[hi],
            label=f"Deep (n={hi.sum()})",
        )
        kmf.plot_survival_function(
            ax=ax, color="#e74c3c",
            ci_show=True, ci_alpha=0.1,
        )
        kmf.fit(
            t[lo], e[lo],
            label=f"Shallow (n={lo.sum()})",
        )
        kmf.plot_survival_function(
            ax=ax, color="#27ae60",
            ci_show=True, ci_alpha=0.1,
        )
        p_str = (
            f"p={p:.4f}"
            if not np.isnan(p) else "N/A"
        )
        ax.set_title(
            f"{title}\n{p_str}", fontsize=9
        )
        ax.legend(fontsize=7)
        ax.set_xlabel("Time (months)",
                      fontsize=8)

    # A — KM Luminal OS
    ax_a = fig.add_subplot(gs_f[0, 0])
    km_plot(
        ax_a,
        surv_results.get("Luminal"),
        "A — KM Luminal OS (TCGA)",
    )

    # B — KM Basal OS
    ax_b = fig.add_subplot(gs_f[0, 1])
    km_plot(
        ax_b,
        surv_results.get("Basal"),
        "B — KM Basal OS (TCGA)",
    )

    # C — Panel KM luminal
    ax_c = fig.add_subplot(gs_f[0, 2])
    lum_res = surv_results.get("Luminal")
    if (
        lum_res is not None
        and lum_res.get("phi") is not None
    ):
        t   = lum_res["t"]
        e   = lum_res["e"]
        phi = lum_res["phi"]
        plo = lum_res["plo"]
        pp  = lum_res["p_panel"]
        kmf = KaplanMeierFitter()
        kmf.fit(
            t[phi], e[phi],
            label=f"High (n={phi.sum()})",
        )
        kmf.plot_survival_function(
            ax=ax_c, color="#8e44ad",
            ci_show=False,
        )
        kmf.fit(
            t[plo], e[plo],
            label=f"Low (n={plo.sum()})",
        )
        kmf.plot_survival_function(
            ax=ax_c, color="#f39c12",
            ci_show=False,
        )
        p_str = (
            f"p={pp:.4f}"
            if not np.isnan(pp) else "N/A"
        )
        ax_c.set_title(
            f"C — Panel FGFR3/CCND1/CLDN3\n"
            f"{p_str}",
            fontsize=9,
        )
        ax_c.legend(fontsize=7)
        ax_c.set_xlabel("Time (months)",
                        fontsize=8)
    else:
        ax_c.set_title(
            "C — Panel (not available)",
            fontsize=9,
        )

    # D — FGFR3 luminal depth
    ax_d = fig.add_subplot(gs_f[1, 0])
    if "FGFR3" in lum.columns:
        ax_d.scatter(
            l_depth.values,
            lum["FGFR3"].values,
            alpha=0.3, s=15,
            color=COLORS["Luminal"],
        )
        rv, _ = safe_pearsonr(
            l_depth.values, lum["FGFR3"].values
        )
        ax_d.set_title(
            f"D — FGFR3 Luminal Depth\n"
            f"r={rv:+.3f} (TR-1)",
            fontsize=9,
        )
        ax_d.set_xlabel("Luminal depth",
                        fontsize=8)
        ax_d.set_ylabel("FGFR3", fontsize=8)

    # E — GATA3 basal depth
    ax_e = fig.add_subplot(gs_f[1, 1])
    if "GATA3" in bas.columns:
        ax_e.scatter(
            b_depth.values,
            bas["GATA3"].values,
            alpha=0.3, s=15,
            color=COLORS["Basal"],
        )
        rv, _ = safe_pearsonr(
            b_depth.values, bas["GATA3"].values
        )
        ax_e.set_title(
            f"E — GATA3 Basal Depth\n"
            f"r={rv:+.3f} (TR-5)",
            fontsize=9,
        )
        ax_e.set_xlabel("Basal depth",
                        fontsize=8)
        ax_e.set_ylabel("GATA3", fontsize=8)

    # F — ZEB2-AURKA scatter
    ax_f = fig.add_subplot(gs_f[1, 2])
    for label, df_, marker in [
        ("Luminal", lum, "s"),
        ("Basal",   bas, "o"),
    ]:
        gc_ = list(df_.columns)
        if "ZEB2" in gc_ and "AURKA" in gc_:
            rv, _ = safe_pearsonr(
                df_["ZEB2"].values,
                df_["AURKA"].values,
            )
            ax_f.scatter(
                df_["ZEB2"].values,
                df_["AURKA"].values,
                alpha=0.3, s=15,
                color=COLORS[label],
                marker=marker,
                label=(
                    f"{label} r={rv:+.3f}"
                    if not np.isnan(rv)
                    else label
                ),
            )
    ax_f.set_xlabel("ZEB2", fontsize=8)
    ax_f.set_ylabel("AURKA", fontsize=8)
    ax_f.set_title(
        "F — ZEB2-AURKA (NP-BLCA-1)\n"
        "STAD=+0.99 | EAC=+0.47 | "
        "BLCA pred:<0",
        fontsize=8,
    )
    ax_f.legend(fontsize=7)

    # G — CIN vs AURKA/ZEB2
    ax_g = fig.add_subplot(gs_f[2, 0])
    if cin_series is not None:
        all_df = pd.concat([lum, bas])
        gc_all = list(all_df.columns)
        if "AURKA" in gc_all:
            cin_v = cin_series.reindex(
                all_df.index
            ).values
            aurka_v = all_df["AURKA"].values
            valid = (
                np.isfinite(cin_v)
                & np.isfinite(aurka_v)
            )
            ax_g.scatter(
                cin_v[valid],
                aurka_v[valid],
                alpha=0.2, s=10,
                color="#2c3e50",
            )
            rv, _ = safe_pearsonr(
                cin_v[valid], aurka_v[valid]
            )
            ax_g.set_title(
                f"G — AURKA vs CIN\n"
                f"r={rv:+.3f} (NP-BLCA-1)",
                fontsize=9,
            )
            ax_g.set_xlabel("CIN score",
                            fontsize=8)
            ax_g.set_ylabel("AURKA",
                            fontsize=8)
    else:
        ax_g.set_title(
            "G — AURKA vs CIN (N/A)",
            fontsize=9,
        )

    # H — CCND1 luminal vs basal depth
    ax_h = fig.add_subplot(gs_f[2, 1])
    if "CCND1" in lum.columns:
        ax_h.scatter(
            l_depth.values,
            lum["CCND1"].values,
            alpha=0.3, s=15,
            color=COLORS["Luminal"],
            label=f"Luminal",
        )
    if "CCND1" in bas.columns:
        ax_h.scatter(
            b_depth.values,
            bas["CCND1"].values,
            alpha=0.3, s=15,
            color=COLORS["Basal"],
            label=f"Basal",
        )
    rl = rb = np.nan
    if "CCND1" in lum.columns:
        rl, _ = safe_pearsonr(
            l_depth.values, lum["CCND1"].values
        )
    if "CCND1" in bas.columns:
        rb, _ = safe_pearsonr(
            b_depth.values, bas["CCND1"].values
        )
    ax_h.set_title(
        f"H — CCND1 Luminal/Basal Divide\n"
        f"Lum r={rl:+.3f}  Bas r={rb:+.3f}",
        fontsize=9,
    )
    ax_h.set_xlabel("Depth score", fontsize=8)
    ax_h.set_ylabel("CCND1", fontsize=8)
    ax_h.legend(fontsize=7)

    # I — Summary
    ax_i = fig.add_subplot(gs_f[2, 2])
    ax_i.axis("off")
    p_lum = p_bas = "N/A"
    if surv_results.get("Luminal"):
        v = surv_results["Luminal"]["p_depth"]
        if not np.isnan(v):
            p_lum = f"{v:.4f}"
    if surv_results.get("Basal"):
        v = surv_results["Basal"]["p_depth"]
        if not np.isnan(v):
            p_bas = f"{v:.4f}"
    zr_lum = (
        f"{zeb2_results.get('Luminal',(np.nan,))[0]:+.4f}"
        if "Luminal" in zeb2_results else "N/A"
    )
    zr_bas = (
        f"{zeb2_results.get('Basal',(np.nan,))[0]:+.4f}"
        if "Basal"   in zeb2_results else "N/A"
    )
    summary = (
        "I — SCRIPT 3 SUMMARY\n"
        "─────────────────────────────\n"
        "Dataset: TCGA-BLCA\n"
        "MIBC-enriched\n"
        "Platform: RNA-seq RSEM\n\n"
        "SURVIVAL (OS):\n"
        f"  Luminal p={p_lum}\n"
        f"  Basal   p={p_bas}\n\n"
        "ZEB2-AURKA:\n"
        f"  Luminal r={zr_lum}\n"
        f"  Basal   r={zr_bas}\n"
        f"  GSE13507: r=-0.43\n"
        f"  STAD:     r=+0.99\n\n"
        "Framework: OrganismCore\n"
        "Doc 91c | 2026-03-01"
    )
    ax_i.text(
        0.03, 0.97, summary,
        transform=ax_i.transAxes,
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
        RESULTS_DIR,
        "blca_tcga_s3.png",
    )
    plt.savefig(
        out, dpi=150,
        bbox_inches="tight",
    )
    log(f"\n  Figure saved: {out}")
    plt.close()

# ============================================================
# MAIN
# ============================================================

def main():
    log("=" * 65)
    log("BLADDER CANCER — SCRIPT 3")
    log("Dataset: TCGA-BLCA")
    log("MIBC-enriched | Mutation | CIN")
    log("Framework: OrganismCore")
    log("Doc: 91c | Date: 2026-03-01")
    log("=" * 65)
    log("")
    log("PREDICTIONS LOCKED:")
    log("TV-1: Luminal depth predicts OS ***")
    log("TV-2: Basal depth predicts OS ***")
    log("TV-3: FGFR3/CCND1/CLDN3 panel OS lum")
    log("TV-4: TWIST1/CDK6/GATA3 panel OS bas")
    log("TR-1: FGFR3 r>+0.50 luminal")
    log("TR-2: FGFR1 r>+0.40 basal")
    log("NP-BLCA-1: ZEB2-AURKA r<0 in BLCA")
    log("NP-BLCA-12: ARID1A mut → depth↑")

    # Downloads
    log("")
    log("=" * 65)
    log("STEP 0: DATA ACQUISITION")
    log("=" * 65)
    os.makedirs(BASE_DIR, exist_ok=True)

    ok_expr = download(
        EXPR_URL, EXPR_FILE, "TCGA-BLCA expr"
    )
    ok_clin = download(
        CLIN_URL, CLIN_FILE, "TCGA-BLCA clin"
    )
    ok_mut  = download(
        MUT_URL, MUT_FILE, "TCGA mutations"
    )
    ok_scna = download(
        SCNA_URL, SCNA_FILE, "TCGA-BLCA SCNA"
    )

    if not ok_expr:
        log("FATAL: Expression download failed")
        write_log()
        return

    # Load expression
    df_expr = load_expr(EXPR_FILE)
    if df_expr is None or len(df_expr) == 0:
        log("FATAL: Expression load failed")
        write_log()
        return

    # Load clinical
    clin = None
    os_time  = np.full(len(df_expr), np.nan)
    os_event = np.full(len(df_expr), np.nan)
    if ok_clin:
        clin = load_clinical(CLIN_FILE, df_expr)
        if clin is not None:
            os_time, os_event = extract_survival(
                clin, df_expr
            )

    # Load mutations
    mut_dict = None
    if ok_mut:
        mut_dict = load_mutations(
            MUT_FILE, df_expr
        )

    # CIN scores
    cin_series = None
    if ok_scna:
        cin_series = compute_cin_score(
            SCNA_FILE, df_expr
        )

    # Classify subtypes
    subtype = classify_subtypes(df_expr)

    lum_mask = subtype == "Luminal"
    bas_mask = subtype == "Basal"
    lum = df_expr[lum_mask]
    bas = df_expr[bas_mask]

    log("")
    log("=" * 65)
    log("GROUP SUMMARY")
    log("=" * 65)
    log(f"  Luminal: {lum_mask.sum()}")
    log(f"  Basal  : {bas_mask.sum()}")
    log(f"  Total  : {len(df_expr)}")

    # Depth scores
    log("")
    log("=" * 65)
    log("DEPTH SCORES")
    log("=" * 65)
    l_depth = b_depth = None
    if len(lum) >= 5:
        l_depth = build_depth(
            lum, LUMINAL_SWITCH,
            LUMINAL_FA, "Luminal",
        )
    if len(bas) >= 5:
        b_depth = build_depth(
            bas, BASAL_SWITCH,
            BASAL_FA, "Basal",
        )

    # Replication tests
    if l_depth is not None and b_depth is not None:
        replication_tests(
            lum, bas, l_depth, b_depth
        )

    # ZEB2-AURKA CIN test
    zeb2_results = {}
    if l_depth is not None and b_depth is not None:
        zeb2_results = zeb2_aurka_cin_test(
            lum, bas, None,
            cin_series, subtype,
        )

    # Mutation × depth test
    if mut_dict is not None:
        if l_depth is not None and b_depth is not None:
            mutation_depth_test(
                mut_dict, lum, bas,
                l_depth, b_depth,
            )

    # Survival
    surv_results = {}
    valid_os = (
        ~np.isnan(os_time)
        & ~np.isnan(os_event)
        & (os_time > 0)
    )
    log(f"\n  Valid OS across all: "
        f"{valid_os.sum()}")

    if valid_os.sum() >= 10:
        surv_results = survival_analysis_full(
            lum, bas,
            os_time, os_event,
            df_expr,
        )
    else:
        log("  Insufficient OS for survival")

    # Figure
    generate_figure(
        lum, bas,
        l_depth if l_depth is not None
        else pd.Series(dtype=float),
        b_depth if b_depth is not None
        else pd.Series(dtype=float),
        surv_results,
        zeb2_results,
        cin_series,
    )

    # Save depth
    for label, depth_ in [
        ("luminal", l_depth),
        ("basal",   b_depth),
    ]:
        if depth_ is not None:
            depth_.to_csv(
                os.path.join(
                    RESULTS_DIR,
                    f"depth_s3_{label}.csv",
                ),
                header=[f"depth_s3_{label}"],
            )

    write_log()
    log(f"\n  Log    : {LOG_FILE}")
    log(f"  Output : {RESULTS_DIR}")
    log("\n=== SCRIPT 3 COMPLETE ===")
    log("\nPaste full output for Document 91c.")


if __name__ == "__main__":
    main()
