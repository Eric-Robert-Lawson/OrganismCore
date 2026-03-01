"""
Prostate Adenocarcinoma — False Attractor Analysis
SCRIPT 1 — DISCOVERY RUN
Dataset: GSE32571
  59 PRAD tumors | 39 matched benign prostate
  Illumina HumanHT-12 microarray
  Non-normalized — normalization in script
  Gleason high/low annotated
  Matched pairs design (DKFZ cohort)

FRAMEWORK: OrganismCore Principles-First
Doc: 88a | Date: 2026-03-01

PREDICTIONS LOCKED BEFORE DATA:
  Switch genes (predicted suppressed):
    NKX3-1 — master luminal TF
    FOXA1  — AR pioneer factor
    KLK3   — PSA terminal AR target
    ACPP   — acid phosphatase luminal marker

  False attractor (predicted elevated):
    ERG    — TMPRSS2-ERG fusion product
    MKI67  — proliferation
    EZH2   — epigenetic lock (4th solid cancer)
    HOXC6  — HOX gene EMT program

  Scaffold:
    AR     — maintained/elevated
    MYC    — elevated (no secretory bias)

  Gleason prediction:
    High Gleason = deeper block
    r(depth, Gleason_high) > 0

  ERG prediction:
    Bimodal expression — fusion+ vs fusion-
    Threshold derivable from expression alone

  Drug targets (geometry-derived):
    1. AR pathway inhibitor (confirmed std)
    2. EZH2 inhibitor (tazemetostat)
    3. NKX3-1 restoration
    4. MYC inhibitor / BET inhibitor

Author: Eric Robert Lawson
Framework: OrganismCore Principles-First
"""

import os
import sys
import gzip
import urllib.request
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import warnings
warnings.filterwarnings("ignore")

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR    = "./prad_false_attractor/"
RESULTS_DIR = os.path.join(BASE_DIR, "results")
LOG_FILE    = os.path.join(RESULTS_DIR,
                           "analysis_log.txt")

os.makedirs(BASE_DIR,    exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

GEO_BASE = (
    "https://ftp.ncbi.nlm.nih.gov/geo/"
    "series/GSE32nnn/GSE32571/suppl/"
)

FILES = {
    "matrix": "GSE32571_non_normalized.txt.gz",
}

META_URL = (
    "https://www.ncbi.nlm.nih.gov/geo/"
    "query/acc.cgi?acc=GSE32571"
    "&targ=gsm&form=text&view=full"
)

# ============================================================
# ILLUMINA PROBE → GENE SYMBOL
# Hard-coded for key targets only
# Avoids downloading 100MB platform file
# Source: Illumina HumanHT-12 v4 annotation
# ============================================================

# These are the ILMN probe IDs for our
# target genes on HumanHT-12 v4
# Multiple probes per gene — all included
# Script will pick highest-expressed probe

PROBE_GENE_MAP = {
    # SWITCH GENES
    "ILMN_1766707": "NKX3-1",
    "ILMN_1718800": "NKX3-1",
    "ILMN_2337565": "FOXA1",
    "ILMN_1679881": "FOXA1",
    "ILMN_1773275": "KLK3",
    "ILMN_2388574": "KLK3",
    "ILMN_1811083": "ACPP",
    "ILMN_1788078": "KLK2",
    "ILMN_1788866": "MSMB",
    "ILMN_2147486": "MSMB",

    # FALSE ATTRACTOR / FA
    "ILMN_2338729": "ERG",
    "ILMN_1766526": "ERG",
    "ILMN_1806487": "MKI67",
    "ILMN_2413324": "MKI67",
    "ILMN_1688580": "EZH2",
    "ILMN_1795529": "EZH2",
    "ILMN_1712966": "HOXC6",
    "ILMN_1793626": "AMACR",
    "ILMN_1669115": "AMACR",

    # EPIGENETIC
    "ILMN_1688580": "EZH2",
    "ILMN_2136659": "EED",
    "ILMN_1739177": "SUZ12",
    "ILMN_1778439": "KDM6A",
    "ILMN_1700949": "DNMT3A",
    "ILMN_1670195": "BMI1",
    "ILMN_1786314": "JARID2",

    # AR AXIS
    "ILMN_1701183": "AR",
    "ILMN_2377461": "AR",
    "ILMN_1773275": "KLK3",
    "ILMN_1788078": "KLK2",
    "ILMN_1786475": "TMPRSS2",
    "ILMN_2184373": "TMPRSS2",
    "ILMN_1705169": "FKBP5",
    "ILMN_1788660": "STEAP2",

    # SCAFFOLD
    "ILMN_1674999": "MYC",
    "ILMN_2348918": "MYC",
    "ILMN_1697622": "CCND1",
    "ILMN_1738801": "CDK4",
    "ILMN_1698467": "CDK6",
    "ILMN_1776507": "RB1",
    "ILMN_2185948": "PTEN",
    "ILMN_2402257": "TP53",

    # LUMINAL
    "ILMN_1688895": "KRT8",
    "ILMN_1711192": "KRT18",
    "ILMN_1765851": "KRT19",
    "ILMN_1791210": "CDH1",
    "ILMN_1668111": "EPCAM",
    "ILMN_2387561": "HOXB13",
    "ILMN_1714588": "GATA2",
    "ILMN_2341949": "GATA3",

    # BASAL
    "ILMN_1779323": "KRT5",
    "ILMN_1713464": "KRT14",
    "ILMN_1692128": "TP63",
    "ILMN_2383725": "CD44",
    "ILMN_2364093": "ITGA6",
    "ILMN_1699012": "NGFR",

    # EMT
    "ILMN_1777688": "VIM",
    "ILMN_1714228": "CDH2",
    "ILMN_1697281": "SNAI1",
    "ILMN_1693140": "SNAI2",
    "ILMN_1779677": "ZEB1",
    "ILMN_1796316": "TWIST1",
    "ILMN_1766619": "FN1",

    # ERG PROGRAM
    "ILMN_2338729": "ERG",
    "ILMN_1772887": "ETV1",
    "ILMN_1668770": "ETV4",
    "ILMN_1791861": "ETV5",
    "ILMN_1715210": "SPDEF",

    # NEUROENDOCRINE
    "ILMN_1683121": "CHGA",
    "ILMN_1791735": "SYP",
    "ILMN_1770337": "ENO2",
    "ILMN_1808680": "NCAM1",
    "ILMN_1681538": "AURKA",
    "ILMN_1745538": "MYCN",
    "ILMN_1736783": "SOX2",

    # PROGNOSIS
    "ILMN_1806487": "MKI67",
    "ILMN_1698404": "PCNA",
    "ILMN_1751278": "TOP2A",
    "ILMN_1681538": "AURKA",
    "ILMN_1762653": "PLK1",
    "ILMN_1741308": "BUB1B",
}

# ============================================================
# GENE PANELS — LOCKED BEFORE DATA
# ============================================================

SWITCH_GENES = [
    "NKX3-1", "FOXA1", "KLK3",
    "ACPP", "KLK2", "MSMB",
]
FA_MARKERS = [
    "ERG", "MKI67", "EZH2",
    "HOXC6", "AMACR",
]
EPIGENETIC = [
    "EZH2", "EED", "SUZ12",
    "KDM6A", "DNMT3A", "BMI1", "JARID2",
]
AR_AXIS = [
    "AR", "KLK3", "KLK2",
    "TMPRSS2", "FKBP5", "STEAP2",
    "NKX3-1", "FOXA1",
]
SCAFFOLD = [
    "MYC", "CCND1", "CDK4",
    "CDK6", "RB1", "PTEN", "TP53",
]
LUMINAL = [
    "KRT8", "KRT18", "KRT19",
    "CDH1", "EPCAM", "HOXB13",
    "GATA2", "GATA3",
]
BASAL = [
    "KRT5", "KRT14", "TP63",
    "CD44", "ITGA6", "NGFR",
]
EMT = [
    "VIM", "CDH2", "SNAI1",
    "SNAI2", "ZEB1", "TWIST1", "FN1",
]
ERG_PROGRAM = [
    "ERG", "ETV1", "ETV4",
    "ETV5", "SPDEF",
]
NEUROENDOCRINE = [
    "CHGA", "SYP", "ENO2",
    "NCAM1", "AURKA", "MYCN", "SOX2",
]
PROGNOSIS = [
    "MKI67", "PCNA", "TOP2A",
    "AURKA", "PLK1", "BUB1B",
]

ALL_TARGET = list(dict.fromkeys(
    SWITCH_GENES + FA_MARKERS +
    EPIGENETIC + AR_AXIS + SCAFFOLD +
    LUMINAL + BASAL + EMT +
    ERG_PROGRAM + NEUROENDOCRINE + PROGNOSIS
))

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

# ============================================================
# STEP 0: DOWNLOAD
# ============================================================

def download_all():
    log("=" * 65)
    log("STEP 0: DATA ACQUISITION")
    log("Dataset: GSE32571")
    log("  59 PRAD tumors")
    log("  39 matched benign prostate")
    log("  Illumina HumanHT-12 microarray")
    log("=" * 65)

    paths = {}
    for key, fname in FILES.items():
        local = os.path.join(BASE_DIR, fname)
        if os.path.exists(local):
            size_mb = os.path.getsize(local) / 1e6
            if size_mb > 0.1:
                log(f"  Found: {fname} "
                    f"({size_mb:.1f} MB) — reusing")
                paths[key] = local
                continue
        url = GEO_BASE + fname
        log(f"  Downloading: {fname}")
        log(f"  URL: {url}")

        def hook(count, block, total):
            if total > 0:
                pct = min(
                    count * block / total * 100,
                    100
                )
                mb = count * block / 1e6
                sys.stdout.write(
                    f"\r  {mb:.1f} MB ({pct:.1f}%)"
                )
                sys.stdout.flush()

        urllib.request.urlretrieve(
            url, local, hook
        )
        print()
        size_mb = os.path.getsize(local) / 1e6
        log(f"  Done: {local} ({size_mb:.1f} MB)")
        paths[key] = local
    return paths

# ============================================================
# STEP 1: METADATA
# ============================================================

def fetch_metadata():
    log("")
    log("--- Fetching metadata ---")
    cache = os.path.join(
        RESULTS_DIR, "metadata.csv"
    )
    if os.path.exists(cache):
        df = pd.read_csv(cache, index_col=0)
        log(f"  Loaded cache: {len(df)} samples")
        return df

    log("  Fetching from GEO...")
    req = urllib.request.Request(
        META_URL,
        headers={"User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(
        req, timeout=30
    ) as r:
        text = r.read().decode("utf-8")

    samples, current = [], {}
    for line in text.split("\n"):
        if line.startswith("^SAMPLE"):
            if current:
                samples.append(current)
            current = {
                "gsm": line.split("=")[1].strip()
            }
        elif line.startswith("!Sample_title"):
            current["title"] = \
                line.split("=", 1)[1].strip()
        elif line.startswith(
                "!Sample_source_name_ch1"):
            current["source"] = \
                line.split("=", 1)[1].strip()
        elif line.startswith(
                "!Sample_characteristics_ch1"):
            val = line.split("=", 1)[1].strip()
            if ":" in val:
                k, v = val.split(":", 1)
                current[
                    k.strip().lower()
                    .replace(" ", "_")
                ] = v.strip()
    if current:
        samples.append(current)

    df = pd.DataFrame(samples)
    df.to_csv(cache)
    log(f"  Fetched {len(df)} samples")
    return df

# ============================================================
# STEP 2: LOAD AND NORMALIZE
# ============================================================

def load_and_normalize(path):
    log(f"\n  Loading: {os.path.basename(path)}")

    with gzip.open(path, "rt") as f:
        df = pd.read_csv(
            f, sep="\t", index_col=0,
            low_memory=False
        )

    log(f"  Raw shape: {df.shape}")
    log(f"  Col sample: {list(df.columns[:4])}")

    # Separate expression from Detection.Pval
    expr_cols = [
        c for c in df.columns
        if "detection" not in c.lower()
        and "pval" not in c.lower()
    ]
    pval_cols = [
        c for c in df.columns
        if "detection" in c.lower()
        or "pval" in c.lower()
    ]

    log(f"  Expression cols: {len(expr_cols)}")
    log(f"  Pval cols      : {len(pval_cols)}")

    expr_df = df[expr_cols].copy()
    expr_df = expr_df.apply(
        pd.to_numeric, errors="coerce"
    )

    # Filter: keep probes detected in
    # >= 20% of samples
    if pval_cols:
        pval_df = df[pval_cols].apply(
            pd.to_numeric, errors="coerce"
        )
        detected   = (pval_df < 0.05).sum(axis=1)
        min_detect = max(
            3, int(len(pval_cols) * 0.20)
        )
        keep_mask  = detected >= min_detect
        expr_df    = expr_df[keep_mask]
        log(f"  After detection filter: "
            f"{keep_mask.sum()} probes")

    expr_df = expr_df.clip(lower=1.0)
    expr_df = np.log2(expr_df)
    log(f"  log2 transformed")

    # Quantile normalize
    log(f"  Quantile normalizing...")
    arr      = expr_df.values.copy()
    sort_arr = np.sort(arr, axis=0)
    mean_ref = sort_arr.mean(axis=1)
    rank_idx = np.argsort(
        np.argsort(arr, axis=0), axis=0
    )
    norm_arr = mean_ref[rank_idx]
    expr_df  = pd.DataFrame(
        norm_arr,
        index=expr_df.index,
        columns=expr_df.columns,
    )
    log(f"  Normalized shape: {expr_df.shape}")
    return expr_df

# ============================================================
# STEP 3: PROBE MAPPING — FAST LOCAL
# Use hard-coded PROBE_GENE_MAP first
# Then try GEO miniSOFT as fallback
# (much smaller than full SOFT file)
# ============================================================

def map_probes_fast(expr_df):
    log("")
    log("--- Probe mapping (fast local) ---")

    # Method 1: hard-coded map
    probe_ids = set(expr_df.index)
    mapped    = {
        p: g for p, g in PROBE_GENE_MAP.items()
        if p in probe_ids
    }
    log(f"  Hard-coded map hits: "
        f"{len(mapped)}/{len(PROBE_GENE_MAP)}")

    # Method 2: if too few hits
    # try GEO miniSOFT annotation table
    # (just the table section — much faster)
    if len(mapped) < 20:
        log("  Trying GEO annotation table...")
        ann_url = (
            "https://www.ncbi.nlm.nih.gov/geo/"
            "query/acc.cgi?acc=GPL10558"
            "&targ=self&form=text&view=brief"
        )
        try:
            req = urllib.request.Request(
                ann_url,
                headers={
                    "User-Agent": "Mozilla/5.0"
                }
            )
            with urllib.request.urlopen(
                req, timeout=20
            ) as r:
                text = r.read().decode(
                    "utf-8", errors="ignore"
                )

            in_table  = False
            col_names = None
            id_col    = None
            sym_col   = None
            extra     = {}

            for line in text.split("\n"):
                line = line.rstrip()
                if "platform_table_begin" in line:
                    in_table  = True
                    col_names = None
                    continue
                if "platform_table_end" in line:
                    break
                if not in_table:
                    continue
                parts = line.split("\t")
                if col_names is None:
                    col_names = parts
                    for i, c in enumerate(
                        col_names
                    ):
                        cl = c.lower()
                        if cl == "id":
                            id_col = i
                        if cl in [
                            "symbol",
                            "ilmn_gene",
                            "gene_symbol",
                        ]:
                            sym_col = i
                    log(f"  Cols: {col_names[:6]}")
                    log(f"  id_col={id_col} "
                        f"sym_col={sym_col}")
                    continue
                if (id_col is not None
                        and sym_col is not None
                        and len(parts)
                        > max(id_col, sym_col)):
                    probe = parts[id_col].strip()
                    sym   = parts[sym_col].strip()
                    if (probe and sym
                            and sym != ""
                            and sym != "---"):
                        extra[probe] = sym

            log(f"  GEO brief: "
                f"{len(extra)} probes")
            mapped.update({
                p: g for p, g in extra.items()
                if p in probe_ids
            })
            log(f"  Total after GEO: "
                f"{len(mapped)}")

        except Exception as e:
            log(f"  GEO brief error: {e}")

    # Method 3: if still too few,
    # try downloading just the annotation
    # CSV (not full SOFT)
    if len(mapped) < 20:
        log("  Trying annotation CSV...")
        csv_url = (
            "https://ftp.ncbi.nlm.nih.gov/geo/"
            "platforms/GPL10nnn/GPL10558/annot/"
            "GPL10558.annot.gz"
        )
        try:
            req = urllib.request.Request(
                csv_url,
                headers={
                    "User-Agent": "Mozilla/5.0"
                }
            )
            with urllib.request.urlopen(
                req, timeout=30
            ) as r:
                raw = r.read()

            import io as _io
            with gzip.open(
                _io.BytesIO(raw), "rt"
            ) as gz:
                lines = gz.readlines()

            log(f"  Annot lines: {len(lines)}")
            in_t   = False
            cols   = None
            ic, sc = None, None
            extra2 = {}
            for line in lines:
                line = line.rstrip()
                if "platform_table_begin" in line:
                    in_t = True
                    cols = None
                    continue
                if "platform_table_end" in line:
                    break
                if not in_t:
                    continue
                parts = line.split("\t")
                if cols is None:
                    cols = parts
                    for i, c in enumerate(cols):
                        cl = c.lower()
                        if cl == "id":
                            ic = i
                        if cl in [
                            "gene symbol",
                            "symbol",
                            "gene_symbol",
                        ]:
                            sc = i
                    continue
                if (ic is not None
                        and sc is not None
                        and len(parts)
                        > max(ic, sc)):
                    probe = parts[ic].strip()
                    sym   = parts[sc].strip()
                    if (probe and sym
                            and "///" not in sym
                            and sym != "---"):
                        extra2[probe] = \
                            sym.split(" ")[0]

            log(f"  Annot CSV: {len(extra2)}")
            mapped.update({
                p: g for p, g
                in extra2.items()
                if p in probe_ids
            })
            log(f"  Total after CSV: "
                f"{len(mapped)}")

        except Exception as e:
            log(f"  Annot CSV error: {e}")

    # Apply mapping
    log(f"\n  Final probe→gene hits: "
        f"{len(mapped)}")

    if len(mapped) < 5:
        log("  WARNING: Very few probes mapped")
        log("  Returning probe IDs as gene names")
        log("  Check probe ID format in matrix")
        log(f"  Sample probe IDs: "
            f"{list(expr_df.index[:5])}")
        return expr_df

    # Build gene-level matrix
    sub = expr_df.loc[
        [p for p in mapped if p in expr_df.index]
    ].copy()
    sub["symbol"] = [
        mapped[p] for p in sub.index
    ]
    sub["mean_expr"] = \
        sub.drop(columns=["symbol"]).mean(axis=1)
    sub = sub.sort_values(
        "mean_expr", ascending=False
    )
    sub = sub.drop_duplicates(
        subset=["symbol"], keep="first"
    )
    symbols = sub["symbol"].values
    sub = sub.drop(columns=["symbol",
                             "mean_expr"])
    sub.index = symbols

    log(f"  Genes after dedup: {len(sub)}")
    log(f"  Sample genes: "
        f"{list(sub.index[:10])}")

    # Report target gene coverage
    found = [g for g in ALL_TARGET
             if g in sub.index]
    miss  = [g for g in ALL_TARGET
             if g not in sub.index]
    log(f"\n  Target genes found: "
        f"{len(found)}/{len(ALL_TARGET)}")
    if miss:
        log(f"  Missing: {miss[:15]}")

    return sub

# ============================================================
# STEP 4: MERGE AND CLASSIFY
# ============================================================

def merge_with_meta(gene_df, meta):
    log("")
    log("--- Merging with metadata ---")

    meta = meta.copy()

    # Extract DKFZ_XX identifier from title
    def extract_dkfz(title):
        title = str(title)
        parts = title.split("_")
        for i, p in enumerate(parts):
            if p.upper() == "DKFZ" \
                    and i + 1 < len(parts):
                return f"DKFZ_{parts[i+1]}"
        return title

    meta["sample_id"] = \
        meta["title"].apply(extract_dkfz)

    log(f"  Meta IDs (first 5): "
        f"{list(meta['sample_id'].head(5))}")
    log(f"  Expr cols (first 5): "
        f"{list(gene_df.columns[:5])}")

    meta_cols = [c for c in [
        "disease_stage",
        "gleason_pattern_group",
        "source",
    ] if c in meta.columns]

    # Transpose so samples are rows
    expr_T = gene_df.T
    expr_T.index.name = "sample_id"

    merged = expr_T.join(
        meta.set_index("sample_id")[meta_cols],
        how="left",
    )

    # Classify
    merged["group"] = "UNKNOWN"

    if "disease_stage" in merged.columns:
        ds = merged[
            "disease_stage"
        ].fillna("").str.lower()
        merged.loc[
            ds.str.contains("cancer|tumor"),
            "group"
        ] = "TUMOR"
        merged.loc[
            ds.str.contains("benign|normal"),
            "group"
        ] = "NORMAL"

    # Fallback: column name contains clue
    for idx in merged[
        merged["group"] == "UNKNOWN"
    ].index:
        il = str(idx).lower()
        if "tumor" in il or "cancer" in il:
            merged.loc[idx, "group"] = "TUMOR"
        elif "benign" in il or "normal" in il:
            merged.loc[idx, "group"] = "NORMAL"

    n_t = (merged["group"] == "TUMOR").sum()
    n_n = (merged["group"] == "NORMAL").sum()
    n_u = (merged["group"] == "UNKNOWN").sum()
    log(f"  TUMOR  : {n_t}")
    log(f"  NORMAL : {n_n}")
    log(f"  UNKNOWN: {n_u}")

    # Gleason distribution
    if "gleason_pattern_group" in merged.columns:
        gc = merged[
            merged["group"] == "TUMOR"
        ]["gleason_pattern_group"].value_counts()
        log(f"\n  Gleason distribution (tumor):")
        for g, n in gc.items():
            log(f"    {g}: {n}")

    return merged

# ============================================================
# STEP 5: SADDLE POINT ANALYSIS
# ============================================================

def saddle_point_analysis(merged):
    log("")
    log("=" * 65)
    log("STEP 5: SADDLE POINT ANALYSIS")
    log("PRAD TUMOR vs BENIGN PROSTATE")
    log("=" * 65)

    tumor  = merged[merged["group"] == "TUMOR"]
    normal = merged[merged["group"] == "NORMAL"]

    log(f"  TUMOR  : {len(tumor)}")
    log(f"  NORMAL : {len(normal)}")
    log("")
    log("  PREDICTIONS (locked before data):")
    log("  Switch: NKX3-1/FOXA1/KLK3/ACPP DOWN")
    log("  FA:     ERG/EZH2/MKI67/HOXC6 UP")
    log("  Scaffold: MYC/AR elevated")

    role_map = {}
    for g in SWITCH_GENES:   role_map[g]="SWITCH"
    for g in FA_MARKERS:     role_map[g]="FA"
    for g in EPIGENETIC:     role_map[g]="EPIGEN"
    for g in AR_AXIS:        role_map[g]="AR"
    for g in SCAFFOLD:       role_map[g]="SCAFFOLD"
    for g in LUMINAL:        role_map[g]="LUMINAL"
    for g in BASAL:          role_map[g]="BASAL"
    for g in EMT:            role_map[g]="EMT"
    for g in ERG_PROGRAM:    role_map[g]="ERG"
    for g in NEUROENDOCRINE: role_map[g]="NE"
    for g in PROGNOSIS:      role_map[g]="PROG"

    def fmt_p(p):
        if p < 1e-300:  return "p=0.00e+00 ***"
        elif p < 0.001: return f"p={p:.2e} ***"
        elif p < 0.01:  return f"p={p:.2e}  **"
        elif p < 0.05:  return f"p={p:.4f}   *"
        else:           return f"p={p:.4f}  ns"

    gene_cols = [
        c for c in merged.columns
        if c in ALL_TARGET
    ]

    log(f"\n  {'Gene':<12} {'Role':<9} "
        f"{'Normal':>9} {'Tumor':>9} "
        f"{'Change':>9} {'p-value':>16}")
    log(f"  {'-'*68}")

    results = []
    for gene in ALL_TARGET:
        if gene not in gene_cols:
            continue
        nd_v = normal[gene].dropna().values
        td_v = tumor[gene].dropna().values
        if len(nd_v) < 3 or len(td_v) < 3:
            continue

        nd_m = nd_v.mean()
        td_m = td_v.mean()
        chg  = (
            (td_m - nd_m) / nd_m * 100
            if nd_m > 0.0001 else np.nan
        )
        _, p_s = stats.mannwhitneyu(
            nd_v, td_v, alternative="greater"
        )
        _, p_e = stats.mannwhitneyu(
            td_v, nd_v, alternative="greater"
        )
        p_use = min(p_s, p_e)
        role  = role_map.get(gene, "OTHER")
        chg_s = (f"{chg:+.1f}%"
                 if not np.isnan(chg) else "N/A")

        log(f"  {gene:<12} {role:<9} "
            f"{nd_m:>9.4f} {td_m:>9.4f} "
            f"{chg_s:>9}  {fmt_p(p_use):>16}")

        results.append({
            "gene":        gene,
            "role":        role,
            "normal_mean": nd_m,
            "tumor_mean":  td_m,
            "change_pct":  chg,
            "p_value":     p_use,
        })

    rdf = pd.DataFrame(results)
    rdf.to_csv(
        os.path.join(RESULTS_DIR,
                     "saddle_results.csv"),
        index=False,
    )
    log(f"\n  Saved: saddle_results.csv")
    return rdf, tumor, normal

# ============================================================
# STEP 6: DEPTH SCORING
# ============================================================

def depth_scoring(merged, tumor, normal):
    log("")
    log("=" * 65)
    log("STEP 6: BLOCK DEPTH SCORING")
    log("Score = switch suppression + FA elevation")
    log("=" * 65)

    gene_cols = [
        c for c in merged.columns
        if c in ALL_TARGET
    ]

    def norm01(s):
        mn, mx = s.min(), s.max()
        return (
            (s - mn) / (mx - mn)
            if mx > mn
            else pd.Series(0.0, index=s.index)
        )

    tumor = tumor.copy()
    depth = pd.Series(
        np.zeros(len(tumor)), index=tumor.index
    )
    comp = 0

    sw_avail = [
        g for g in SWITCH_GENES
        if g in gene_cols
    ]
    fa_avail = [
        g for g in FA_MARKERS
        if g in gene_cols
    ]

    if sw_avail:
        sw_m   = tumor[sw_avail].mean(axis=1)
        depth += (1 - norm01(sw_m))
        comp  += 1
        log(f"  Component 1: switch suppression "
            f"{sw_avail}")

    if fa_avail:
        fa_m   = tumor[fa_avail].mean(axis=1)
        depth += norm01(fa_m)
        comp  += 1
        log(f"  Component 2: FA elevation "
            f"{fa_avail}")

    if comp > 0:
        depth /= comp

    tumor["block_depth"] = depth.values

    log(f"\n  Block depth ({len(tumor)} tumors):")
    log(f"    Mean  : {depth.mean():.4f}")
    log(f"    Median: {depth.median():.4f}")
    log(f"    Std   : {depth.std():.4f}")
    log(f"    Min   : {depth.min():.4f}")
    log(f"    Max   : {depth.max():.4f}")

    # Gleason
    if "gleason_pattern_group" in tumor.columns:
        log(f"\n  Depth by Gleason:")
        hi = tumor[
            tumor["gleason_pattern_group"]
            == "high"
        ]["block_depth"]
        lo = tumor[
            tumor["gleason_pattern_group"]
            == "low"
        ]["block_depth"]
        for label, sd in [
            ("high", hi), ("low", lo)
        ]:
            if len(sd) > 2:
                log(f"    {label:<6} "
                    f"(n={len(sd):3d}): "
                    f"{sd.mean():.4f} "
                    f"± {sd.std():.4f}")
        if len(hi) > 3 and len(lo) > 3:
            _, p_gl = stats.mannwhitneyu(
                hi, lo, alternative="greater"
            )
            log(f"\n  High > Low Gleason depth: "
                f"p={p_gl:.4f}")
            log(f"  Prediction: high Gleason "
                f"= deeper")
            log(f"  Result: "
                f"{'CONFIRMED' if p_gl < 0.05 else 'NOT CONFIRMED'}")

    # Top depth correlations
    corrs = []
    for gene in gene_cols:
        if gene in ["block_depth",
                    "gleason_pattern_group",
                    "disease_stage", "source",
                    "group"]:
            continue
        try:
            rv, pv = stats.pearsonr(
                tumor["block_depth"].values,
                tumor[gene].values,
            )
            corrs.append((gene, rv, pv))
        except Exception:
            pass
    corrs.sort(
        key=lambda x: abs(x[1]), reverse=True
    )

    log(f"\n  Depth correlations (top 20):")
    log(f"  {'Gene':<12} {'r':>8}  p-value  Role")
    log(f"  {'-'*42}")
    role_map = {}
    for g in SWITCH_GENES:   role_map[g]="SWITCH"
    for g in FA_MARKERS:     role_map[g]="FA"
    for g in AR_AXIS:        role_map[g]="AR"
    for g in EPIGENETIC:     role_map[g]="EPIGEN"
    for g in SCAFFOLD:       role_map[g]="SCAFFOLD"
    for g in LUMINAL:        role_map[g]="LUMINAL"

    for gene, rv, pv in corrs[:20]:
        role = role_map.get(gene, "")
        log(f"  {gene:<12} {rv:>+8.4f}  "
            f"p={pv:.2e}  {role}")

    return tumor, corrs

# ============================================================
# STEP 7: ERG ANALYSIS
# ============================================================

def erg_analysis(tumor, normal):
    log("")
    log("=" * 65)
    log("STEP 7: ERG ANALYSIS")
    log("Prediction: bimodal ERG in tumors")
    log("Fusion+ = ERG high / Fusion- = low")
    log("=" * 65)

    gene_cols = [
        c for c in tumor.columns
        if c in ALL_TARGET
    ]
    if "ERG" not in gene_cols:
        log("  ERG not found — skip")
        return tumor

    erg_t = tumor["ERG"].values
    erg_n = normal["ERG"].values if \
        "ERG" in normal.columns else np.array([])

    if len(erg_n) > 0:
        log(f"\n  ERG normal: "
            f"{erg_n.mean():.4f} "
            f"± {erg_n.std():.4f}")
    log(f"  ERG tumor:  "
        f"{erg_t.mean():.4f} "
        f"± {erg_t.std():.4f}")
    log(f"  ERG range:  "
        f"{erg_t.min():.4f} — "
        f"{erg_t.max():.4f}")

    # Bimodality via KDE
    try:
        from scipy.stats import gaussian_kde
        from scipy.signal import argrelmin
        kde  = gaussian_kde(erg_t)
        xs   = np.linspace(
            erg_t.min(), erg_t.max(), 300
        )
        ys   = kde(xs)
        mins = argrelmin(ys, order=8)[0]
        log(f"\n  KDE local minima: {len(mins)}")

        tumor = tumor.copy()
        if len(mins) > 0:
            threshold = xs[mins[0]]
            log(f"  Bimodal threshold: "
                f"{threshold:.4f}")
            n_hi = (erg_t > threshold).sum()
            n_lo = (erg_t <= threshold).sum()
            log(f"  ERG-high (fusion+?): {n_hi}")
            log(f"  ERG-low  (fusion-?): {n_lo}")
            log(f"  Prediction: CONFIRMED")
            tumor["erg_status"] = np.where(
                tumor["ERG"] > threshold,
                "ERG_high", "ERG_low"
            )
        else:
            log("  No clear bimodal threshold")
            med = np.median(erg_t)
            tumor["erg_status"] = np.where(
                tumor["ERG"] > med,
                "ERG_high", "ERG_low"
            )

    except Exception as e:
        log(f"  KDE error: {e}")
        tumor = tumor.copy()
        med   = np.median(erg_t)
        tumor["erg_status"] = np.where(
            tumor["ERG"] > med,
            "ERG_high", "ERG_low"
        )

    # Key genes by ERG status
    if "erg_status" in tumor.columns:
        erg_hi = tumor[
            tumor["erg_status"] == "ERG_high"
        ]
        erg_lo = tumor[
            tumor["erg_status"] == "ERG_low"
        ]
        key = [g for g in [
            "NKX3-1", "FOXA1", "KLK3",
            "AR", "TMPRSS2", "MYC",
            "EZH2", "MKI67",
        ] if g in gene_cols]

        log(f"\n  Key genes by ERG status:")
        log(f"  {'Gene':<12} "
            f"{'ERG-high':>10} "
            f"{'ERG-low':>10} "
            f"{'Change':>9}")
        log(f"  {'-'*46}")
        for gene in key:
            hm  = erg_hi[gene].mean()
            lm  = erg_lo[gene].mean()
            chg = ((hm - lm) / lm * 100
                   if lm > 0.0001 else np.nan)
            cs  = (f"{chg:+.1f}%"
                   if not np.isnan(chg) else "N/A")
            log(f"  {gene:<12} "
                f"{hm:>10.4f} "
                f"{lm:>10.4f} {cs:>9}")

    return tumor

# ============================================================
# STEP 8: AR AXIS
# ============================================================

def ar_axis_analysis(tumor, normal):
    log("")
    log("=" * 65)
    log("STEP 8: AR AXIS ANALYSIS")
    log("AR maintained/elevated predicted")
    log("KLK3/PSA lower in high Gleason")
    log("=" * 65)

    gene_cols = [
        c for c in tumor.columns
        if c in ALL_TARGET
    ]

    log(f"\n  {'Gene':<10} {'Normal':>9} "
        f"{'Tumor':>9} {'Change':>9}")
    log(f"  {'-'*40}")
    for gene in AR_AXIS:
        if gene not in gene_cols:
            continue
        nm  = normal[gene].mean() \
            if gene in normal.columns else np.nan
        tm  = tumor[gene].mean()
        if np.isnan(nm):
            continue
        chg = ((tm - nm) / nm * 100
               if nm > 0.0001 else np.nan)
        cs  = (f"{chg:+.1f}%"
               if not np.isnan(chg) else "N/A")
        log(f"  {gene:<10} {nm:>9.4f} "
            f"{tm:>9.4f} {cs:>9}")

    # KLK3 by Gleason
    if ("KLK3" in gene_cols
            and "gleason_pattern_group"
            in tumor.columns):
        log(f"\n  KLK3/PSA by Gleason:")
        for g in ["high", "low"]:
            sd = tumor[
                tumor["gleason_pattern_group"]
                == g
            ]["KLK3"]
            if len(sd) > 2:
                log(f"    {g}: {sd.mean():.4f} "
                    f"± {sd.std():.4f} "
                    f"(n={len(sd)})")
        hi_k = tumor[
            tumor["gleason_pattern_group"]
            == "high"
        ]["KLK3"]
        lo_k = tumor[
            tumor["gleason_pattern_group"]
            == "low"
        ]["KLK3"]
        if len(hi_k) > 3 and len(lo_k) > 3:
            _, p_k = stats.mannwhitneyu(
                lo_k, hi_k, alternative="greater"
            )
            log(f"  Low > High KLK3: p={p_k:.4f}")
            log(f"  Prediction: KLK3 lower "
                f"in high Gleason")
            log(f"  Result: "
                f"{'CONFIRMED' if p_k < 0.05 else 'NOT CONFIRMED'}")

# ============================================================
# STEP 9: FIGURE
# ============================================================

def generate_figure(
    merged, tumor, normal, results_df, corrs
):
    log("")
    log("--- Generating figure ---")

    fig = plt.figure(figsize=(26, 20))
    fig.suptitle(
        "Prostate Adenocarcinoma — "
        "False Attractor Analysis\n"
        "Dataset: GSE32571 | "
        "59 PRAD | 39 Benign | "
        "OrganismCore 2026-03-01\n"
        "Luminal identity loss | "
        "EZH2 gain lock | "
        "NKX3-1 switch gene | Doc 88a",
        fontsize=10, fontweight="bold", y=0.99,
    )
    gs = gridspec.GridSpec(
        3, 3, figure=fig,
        hspace=0.52, wspace=0.42,
    )

    clr = {"NORMAL": "#2980b9",
           "TUMOR":  "#c0392b"}
    gene_cols = [
        c for c in merged.columns
        if c in ALL_TARGET
    ]

    def bar_pair(ax, genes, title):
        avail = [
            g for g in genes
            if g in gene_cols
        ]
        if not avail:
            ax.text(
                0.5, 0.5, "No data",
                ha="center", va="center",
                transform=ax.transAxes,
            )
            ax.set_title(title)
            return
        x = np.arange(len(avail))
        w = 0.35
        for i, (grp, df_g, c) in enumerate([
            ("Normal", normal, clr["NORMAL"]),
            ("PRAD",   tumor,  clr["TUMOR"]),
        ]):
            means = [
                df_g[g].mean()
                if g in df_g.columns else 0
                for g in avail
            ]
            sems = [
                df_g[g].sem()
                if g in df_g.columns else 0
                for g in avail
            ]
            ax.bar(
                x + i*w - 0.5*w, means, w,
                yerr=sems, color=c,
                label=grp, capsize=3, alpha=0.85,
            )
        ax.set_xticks(x)
        ax.set_xticklabels(
            avail, rotation=45,
            ha="right", fontsize=7,
        )
        ax.set_ylabel("Expression", fontsize=8)
        ax.set_title(title, fontsize=9)
        ax.legend(fontsize=7)

    # A — Switch genes
    ax_a = fig.add_subplot(gs[0, 0])
    bar_pair(
        ax_a, SWITCH_GENES,
        "A — Switch Genes\n"
        "NKX3-1/FOXA1/KLK3 predicted DOWN"
    )

    # B — FA markers
    ax_b = fig.add_subplot(gs[0, 1])
    bar_pair(
        ax_b,
        ["ERG", "EZH2", "MKI67",
         "HOXC6", "AMACR"],
        "B — FA Markers\n"
        "ERG/EZH2/MKI67 predicted UP"
    )

    # C — Waterfall
    ax_c = fig.add_subplot(gs[0, 2])
    if len(results_df) > 0:
        pdf = results_df.copy().sort_values(
            "change_pct"
        )
        bc  = [
            "#c0392b" if v < 0 else "#27ae60"
            for v in pdf["change_pct"]
        ]
        ax_c.barh(
            pdf["gene"], pdf["change_pct"],
            color=bc,
        )
        ax_c.axvline(
            0, color="black", linewidth=0.8
        )
        ax_c.set_xlabel(
            "% change vs benign", fontsize=8
        )
        ax_c.set_title(
            "C — All Target Genes\n"
            "% change tumor vs benign",
            fontsize=9,
        )
        ax_c.tick_params(axis="y", labelsize=6)

    # D — Depth by Gleason
    ax_d = fig.add_subplot(gs[1, 0])
    if ("block_depth" in tumor.columns
            and "gleason_pattern_group"
            in tumor.columns):
        for g, c in [
            ("high", "#c0392b"),
            ("low",  "#f39c12"),
        ]:
            sd = tumor[
                tumor["gleason_pattern_group"]
                == g
            ]["block_depth"]
            if len(sd) > 2:
                ax_d.hist(
                    sd, bins=12, alpha=0.6,
                    color=c,
                    label=f"Gleason {g}",
                    edgecolor="white",
                )
        ax_d.set_xlabel(
            "Block Depth Score", fontsize=8
        )
        ax_d.set_title(
            "D — Depth by Gleason\n"
            "High Gleason = deeper block?",
            fontsize=9,
        )
        ax_d.legend(fontsize=7)

    # E — AR axis
    ax_e = fig.add_subplot(gs[1, 1])
    bar_pair(
        ax_e, AR_AXIS,
        "E — AR Axis\n"
        "AR/KLK3/FOXA1/NKX3-1"
    )

    # F — Epigenetic
    ax_f = fig.add_subplot(gs[1, 2])
    bar_pair(
        ax_f,
        ["EZH2", "EED", "SUZ12",
         "KDM6A", "BMI1"],
        "F — Epigenetic\n"
        "EZH2 predicted UP (4th cancer)"
    )

    # G — ERG expression
    ax_g = fig.add_subplot(gs[2, 0])
    if "ERG" in gene_cols:
        ax_g.scatter(
            range(len(normal)),
            sorted(normal["ERG"].values),
            color=clr["NORMAL"],
            alpha=0.6, s=25, label="Normal",
        )
        ax_g.scatter(
            range(len(tumor)),
            sorted(tumor["ERG"].values),
            color=clr["TUMOR"],
            alpha=0.6, s=25, label="PRAD",
        )
        ax_g.set_xlabel(
            "Sample (sorted)", fontsize=8
        )
        ax_g.set_ylabel(
            "ERG expression", fontsize=8
        )
        ax_g.set_title(
            "G — ERG Expression\n"
            "Bimodal? Fusion+ vs Fusion-",
            fontsize=9,
        )
        ax_g.legend(fontsize=7)

    # H — Depth correlations
    ax_h = fig.add_subplot(gs[2, 1])
    if corrs:
        top_c  = corrs[:20]
        gc     = [c[0] for c in top_c]
        vc     = [c[1] for c in top_c]
        cc     = [
            "#c0392b" if v < 0 else "#27ae60"
            for v in vc
        ]
        ax_h.barh(gc, vc, color=cc)
        ax_h.axvline(
            0, color="black", linewidth=0.8
        )
        ax_h.set_xlabel(
            "r with depth score", fontsize=8
        )
        ax_h.set_title(
            "H — Depth Correlations\n"
            "Top 20 genes",
            fontsize=9,
        )
        ax_h.tick_params(axis="y", labelsize=7)

    # I — Summary text
    ax_i = fig.add_subplot(gs[2, 2])
    ax_i.axis("off")
    n_found = len([
        g for g in ALL_TARGET
        if g in gene_cols
    ])
    summary = (
        "I — SCRIPT 1 SUMMARY\n"
        "─────────────────────────\n"
        "Dataset: GSE32571\n"
        "  59 PRAD | 39 Benign\n"
        "  Illumina HumanHT-12\n"
        "  Gleason high/low\n"
        "  Matched pairs (DKFZ)\n\n"
        f"Genes found: {n_found}/"
        f"{len(ALL_TARGET)}\n\n"
        "Lineage:\n"
        "  Luminal epithelial\n"
        "  NKX3-1 master switch\n"
        "  → progenitor hybrid\n\n"
        "Predictions:\n"
        "  NKX3-1/FOXA1/KLK3 DOWN\n"
        "  ERG/EZH2/MKI67 UP\n"
        "  MYC UP (valid here)\n"
        "  High Gleason = deeper\n"
        "  ERG bimodal\n\n"
        "EZH2: 4th solid cancer\n"
        "Same gain lock as:\n"
        "  BRCA | PAAD | now PRAD\n\n"
        "Framework: OrganismCore\n"
        "Doc: 88a | 2026-03-01"
    )
    ax_i.text(
        0.03, 0.97, summary,
        transform=ax_i.transAxes,
        fontsize=8.5,
        verticalalignment="top",
        fontfamily="monospace",
        bbox=dict(
            boxstyle="round",
            facecolor="#f8f8f8",
            edgecolor="#cccccc",
        ),
    )

    outpath = os.path.join(
        RESULTS_DIR, "prad_false_attractor.png"
    )
    plt.savefig(
        outpath, dpi=150, bbox_inches="tight"
    )
    log(f"\n  Figure saved: {outpath}")
    plt.close()

# ============================================================
# MAIN
# ============================================================

def main():
    log("=" * 65)
    log("PROSTATE ADENOCARCINOMA")
    log("FALSE ATTRACTOR ANALYSIS — SCRIPT 1")
    log("Dataset: GSE32571")
    log("Framework: OrganismCore")
    log("Doc: 88a | Date: 2026-03-01")
    log("=" * 65)
    log("")
    log("  PREDICTIONS LOCKED:")
    log("  Switch: NKX3-1/FOXA1/KLK3/ACPP DOWN")
    log("  FA:     ERG/EZH2/MKI67/HOXC6 UP")
    log("  EZH2:   ELEVATED (4th solid cancer)")
    log("  MYC:    ELEVATED")
    log("  Gleason: high = deeper block")
    log("  ERG:    bimodal (fusion+ vs fusion-)")
    log("")

    log("\n=== STEP 0: DATA ===")
    paths = download_all()

    log("\n=== STEP 1: METADATA ===")
    meta = fetch_metadata()

    log("\n=== STEP 2: LOAD + NORMALIZE ===")
    expr_df = load_and_normalize(paths["matrix"])

    log("\n=== STEP 3: PROBE MAPPING ===")
    gene_df = map_probes_fast(expr_df)

    log("\n=== STEP 4: MERGE + CLASSIFY ===")
    merged = merge_with_meta(gene_df, meta)

    log("\n=== STEP 5: SADDLE POINT ===")
    results_df, tumor, normal = \
        saddle_point_analysis(merged)

    log("\n=== STEP 6: DEPTH SCORING ===")
    tumor, corrs = depth_scoring(
        merged, tumor, normal
    )

    log("\n=== STEP 7: ERG ANALYSIS ===")
    tumor = erg_analysis(tumor, normal)

    log("\n=== STEP 8: AR AXIS ===")
    ar_axis_analysis(tumor, normal)

    log("\n=== STEP 9: FIGURE ===")
    generate_figure(
        merged, tumor, normal,
        results_df, corrs,
    )

    write_log()
    log(f"\n  Log: {LOG_FILE}")
    log(f"  Outputs: {RESULTS_DIR}")
    log("\n=== SCRIPT 1 COMPLETE ===")


if __name__ == "__main__":
    main()
