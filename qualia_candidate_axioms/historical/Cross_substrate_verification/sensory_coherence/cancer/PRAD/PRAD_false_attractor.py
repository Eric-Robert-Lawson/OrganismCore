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
             most commonly deleted in PRAD
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
    MYC    — elevated (no secretory bias here)

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
GEO: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE32571
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

# Illumina probe annotation
# HumanHT-12 v4 — download from Illumina
# via GEO platform GPL10558
PLATFORM_URL = (
    "https://www.ncbi.nlm.nih.gov/geo/"
    "query/acc.cgi?acc=GPL10558"
    "&targ=self&form=text&view=full"
)

# ============================================================
# GENE PANELS — LOCKED BEFORE DATA
# ============================================================

# SWITCH GENES — luminal identity
# Predicted suppressed in PRAD
SWITCH_GENES = [
    "NKX3-1",   # master luminal TF
    "FOXA1",    # AR pioneer factor
    "KLK3",     # PSA — AR terminal target
    "ACPP",     # acid phosphatase
    "KLK2",     # kallikrein 2 — luminal
    "MSMB",     # microseminoprotein-beta
]

# FALSE ATTRACTOR — dedifferentiated/
# progenitor markers
FA_MARKERS = [
    "ERG",      # TMPRSS2-ERG fusion product
    "MKI67",    # proliferation
    "EZH2",     # epigenetic lock — predicted UP
    "HOXC6",    # HOX gene EMT
    "AMACR",    # alpha-methylacyl-CoA racemase
                # elevated in PRAD
    "PCA3",     # prostate cancer antigen 3
]

# EPIGENETIC
EPIGENETIC = [
    "EZH2",     # H3K27me3 — predicted UP
    "EED",      # PRC2 complex
    "SUZ12",    # PRC2 complex
    "KDM6A",    # H3K27 demethylase
    "DNMT3A",   # DNA methylation
    "BMI1",     # PRC1
    "JARID2",   # PRC2 recruiter
]

# AR AXIS
AR_AXIS = [
    "AR",       # androgen receptor
    "KLK3",     # PSA — AR target
    "KLK2",     # AR target
    "TMPRSS2",  # AR target + ERG fusion
    "FKBP5",    # AR target
    "STEAP2",   # AR regulated
    "NKX3-1",   # AR co-regulated
    "FOXA1",    # AR pioneer
]

# SCAFFOLD
SCAFFOLD = [
    "MYC",      # predicted elevated
    "CCND1",    # cyclin D1
    "CDK4",     # cell cycle
    "CDK6",     # cell cycle
    "RB1",      # tumor suppressor
    "PTEN",     # tumor suppressor
    "TP53",     # tumor suppressor
]

# LUMINAL DIFFERENTIATION MARKERS
LUMINAL = [
    "KRT8",     # luminal keratin
    "KRT18",    # luminal keratin
    "KRT19",    # luminal/ductal
    "CDH1",     # E-cadherin epithelial
    "EPCAM",    # epithelial surface
    "HOXB13",   # prostate luminal TF
    "GATA2",    # AR cofactor luminal
    "GATA3",    # luminal TF
]

# BASAL MARKERS
BASAL = [
    "KRT5",     # basal keratin
    "KRT14",    # basal keratin
    "TP63",     # basal TF (p63)
    "CD44",     # basal/stem marker
    "ITGA6",    # integrin alpha 6 basal
    "NGFR",     # p75NTR basal marker
]

# EMT / INVASION
EMT = [
    "VIM",      # vimentin mesenchymal
    "CDH2",     # N-cadherin mesenchymal
    "SNAI1",    # EMT TF
    "SNAI2",    # SLUG EMT TF
    "ZEB1",     # EMT TF
    "TWIST1",   # EMT TF
    "FN1",      # fibronectin
]

# ERG PROGRAM
ERG_PROGRAM = [
    "ERG",      # ETS TF — fusion product
    "ETV1",     # ETS family — alternative
    "ETV4",     # ETS family — alternative
    "ETV5",     # ETS family
    "SPDEF",    # ETS — luminal
    "ETS2",     # ETS family
]

# NEUROENDOCRINE — important for CRPC
NEUROENDOCRINE = [
    "CHGA",     # chromogranin A
    "SYP",      # synaptophysin
    "ENO2",     # NSE
    "NCAM1",    # neural adhesion
    "AURKA",    # Aurora kinase NEPC
    "MYCN",     # NEPC driver
    "SOX2",     # pluripotency NEPC
]

# PROGNOSIS / CLINICAL
PROGNOSIS = [
    "MKI67",    # Ki67 proliferation
    "PCNA",     # proliferation
    "TOP2A",    # topoisomerase — grade marker
    "AURKA",    # Aurora kinase
    "PLK1",     # polo-like kinase
    "BUB1B",    # spindle checkpoint
]

ALL_TARGET = list(dict.fromkeys(
    SWITCH_GENES +
    FA_MARKERS +
    EPIGENETIC +
    AR_AXIS +
    SCAFFOLD +
    LUMINAL +
    BASAL +
    EMT +
    ERG_PROGRAM +
    NEUROENDOCRINE +
    PROGNOSIS
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
    log("  Non-normalized")
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

        def hook(count, block, total):
            if total > 0:
                pct = min(
                    count * block
                    / total * 100, 100
                )
                mb = count * block / 1e6
                sys.stdout.write(
                    f"\r  {mb:.1f} MB "
                    f"({pct:.1f}%)"
                )
                sys.stdout.flush()

        urllib.request.urlretrieve(
            url, local, hook
        )
        print()
        size_mb = os.path.getsize(local) / 1e6
        log(f"  Done: {local} "
            f"({size_mb:.1f} MB)")
        paths[key] = local
    return paths

# ============================================================
# STEP 1: METADATA
# ============================================================

def fetch_metadata():
    log("")
    log("--- Fetching metadata ---")
    cache = os.path.join(RESULTS_DIR,
                         "metadata.csv")
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
        elif line.startswith(
                "!Sample_description"):
            current["description"] = \
                line.split("=", 1)[1].strip()
    if current:
        samples.append(current)

    df = pd.DataFrame(samples)
    df.to_csv(cache)
    log(f"  Fetched {len(df)} samples")
    return df

# ============================================================
# STEP 2: LOAD AND NORMALIZE MATRIX
# Illumina non-normalized data:
#   Rows = ILMN probe IDs
#   Columns interleaved:
#     sample_expression, sample_Detection.Pval
#   Need to:
#     1. Separate expression from pval columns
#     2. Filter low-detection probes
#     3. log2 transform
#     4. Quantile normalize
#     5. Map ILMN probes → gene symbols
# ============================================================

def load_and_normalize(path):
    log(f"\n  Loading: {os.path.basename(path)}")

    with gzip.open(path, "rt") as f:
        df = pd.read_csv(
            f, sep="\t", index_col=0,
            low_memory=False
        )

    log(f"  Raw shape: {df.shape}")
    log(f"  Columns sample: "
        f"{list(df.columns[:6])}")

    # Separate expression columns from
    # Detection.Pval columns
    expr_cols = [
        c for c in df.columns
        if "Detection" not in c
        and "Pval" not in c
        and "detection" not in c.lower()
    ]
    pval_cols = [
        c for c in df.columns
        if "Detection" in c
        or "Pval" in c
    ]

    log(f"  Expression columns: {len(expr_cols)}")
    log(f"  Pval columns      : {len(pval_cols)}")

    expr_df = df[expr_cols].copy()
    expr_df = expr_df.apply(
        pd.to_numeric, errors="coerce"
    )

    # Filter probes: keep probes detected
    # in at least 20% of samples
    if pval_cols:
        pval_df = df[pval_cols].apply(
            pd.to_numeric, errors="coerce"
        )
        # Detection Pval < 0.05 = detected
        detected = (pval_df < 0.05).sum(axis=1)
        min_detect = max(
            3, int(len(pval_cols) * 0.2)
        )
        keep_mask = detected >= min_detect
        expr_df = expr_df[keep_mask]
        log(f"  Probes after detection filter "
            f"(>={min_detect} samples): "
            f"{keep_mask.sum()}/{len(keep_mask)}")

    # Replace zeros/negatives
    expr_df = expr_df.clip(lower=1.0)

    # log2 transform
    expr_df = np.log2(expr_df)
    log(f"  log2 transformed")

    # Quantile normalize
    log(f"  Quantile normalizing...")
    arr    = expr_df.values.copy()
    sorted_arr = np.sort(arr, axis=0)
    mean_ref   = sorted_arr.mean(axis=1)
    rank_idx   = np.argsort(
        np.argsort(arr, axis=0), axis=0
    )
    norm_arr = mean_ref[rank_idx]
    expr_df  = pd.DataFrame(
        norm_arr,
        index=expr_df.index,
        columns=expr_df.columns,
    )
    log(f"  Quantile normalization complete")
    log(f"  Shape after norm: {expr_df.shape}")

    return expr_df, expr_cols


# ============================================================
# STEP 3: PROBE → GENE SYMBOL MAPPING
# Download GPL10558 platform annotation
# ============================================================

def get_probe_map():
    cache = os.path.join(BASE_DIR,
                         "probe_map.csv")
    if os.path.exists(cache):
        pm = pd.read_csv(cache, index_col=0)
        log(f"  Probe map cache: {len(pm)} probes")
        return pm

    log("  Fetching GPL10558 annotation...")
    # Try GEO soft file
    url = (
        "https://ftp.ncbi.nlm.nih.gov/geo/"
        "platforms/GPL10nnn/GPL10558/soft/"
        "GPL10558_family.soft.gz"
    )
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(
            req, timeout=60
        ) as r:
            raw = r.read()

        with gzip.open(
            __import__("io").BytesIO(raw), "rt"
        ) as gz:
            lines = gz.readlines()

        # Parse table section
        in_table  = False
        col_names = None
        rows      = []
        for line in lines:
            line = line.rstrip()
            if line.startswith(
                "!platform_table_begin"
            ):
                in_table  = True
                col_names = None
                continue
            if line.startswith(
                "!platform_table_end"
            ):
                break
            if in_table:
                parts = line.split("\t")
                if col_names is None:
                    col_names = parts
                else:
                    rows.append(parts)

        if col_names and rows:
            pm = pd.DataFrame(
                rows, columns=col_names
            )
            log(f"  Platform columns: "
                f"{list(pm.columns[:8])}")

            # Find symbol column
            sym_col = None
            for c in pm.columns:
                if c.lower() in [
                    "symbol", "gene_symbol",
                    "ilmn_gene", "gene",
                ]:
                    sym_col = c
                    break
            if sym_col is None:
                for c in pm.columns:
                    if "symbol" in c.lower() \
                            or "gene" in c.lower():
                        sym_col = c
                        break

            if sym_col:
                probe_col = pm.columns[0]
                pm2 = pm[[
                    probe_col, sym_col
                ]].copy()
                pm2.columns = ["probe", "symbol"]
                pm2 = pm2[
                    pm2["symbol"].notna()
                    & (pm2["symbol"] != "")
                    & (pm2["symbol"] != "---")
                ]
                pm2 = pm2.set_index("probe")
                pm2.to_csv(cache)
                log(f"  Probe map: "
                    f"{len(pm2)} probes mapped")
                return pm2

    except Exception as e:
        log(f"  GPL10558 fetch error: {e}")

    # Fallback: parse from matrix file header
    log("  Falling back to direct gene mapping")
    return None


def map_probes_to_genes(expr_df, probe_map):
    if probe_map is None:
        log("  No probe map — "
            "using probe IDs as gene names")
        log("  Attempting SOFT file download...")
        return expr_df

    log(f"\n  Mapping probes to gene symbols...")

    # Join probe IDs to symbols
    matched = expr_df.index.intersection(
        probe_map.index
    )
    log(f"  Probes matched: "
        f"{len(matched)}/{len(expr_df)}")

    if len(matched) == 0:
        log("  WARNING: No probes matched")
        log("  Trying case-insensitive match...")
        pm_upper = probe_map.copy()
        pm_upper.index = pm_upper.index.str.upper()
        expr_upper = expr_df.copy()
        expr_upper.index = \
            expr_upper.index.str.upper()
        matched = expr_upper.index.intersection(
            pm_upper.index
        )
        log(f"  After upper: {len(matched)}")
        if len(matched) > 0:
            expr_df    = expr_upper
            probe_map  = pm_upper

    sub = expr_df.loc[matched].copy()
    sub["symbol"] = probe_map.loc[
        matched, "symbol"
    ].values

    # For multi-probe genes: keep probe
    # with highest mean expression
    sub["mean_expr"] = sub.drop(
        columns=["symbol"]
    ).mean(axis=1)
    sub = sub.sort_values(
        "mean_expr", ascending=False
    )
    sub = sub.drop_duplicates(
        subset=["symbol"], keep="first"
    )
    sub = sub.drop(
        columns=["symbol", "mean_expr"]
    )
    sub.index = probe_map.loc[
        sub.index, "symbol"
    ].values if len(
        sub.index.intersection(
            probe_map.index
        )
    ) == len(sub) else sub.index

    # Re-map index cleanly
    idx_mapped = []
    for probe in sub.index:
        sym = probe_map.loc[probe, "symbol"] \
            if probe in probe_map.index \
            else probe
        idx_mapped.append(sym)
    sub.index = idx_mapped

    log(f"  Genes after dedup: {len(sub)}")
    log(f"  Sample genes: "
        f"{list(sub.index[:5])}")
    return sub


# ============================================================
# STEP 4: MERGE AND CLASSIFY
# ============================================================

def merge_with_meta(expr_T, meta):
    log("")
    log("--- Merging with metadata ---")

    meta = meta.copy()

    # Sample ID from column names
    # Matrix columns: DKFZ_01, DKFZ_02 etc
    # Metadata title: Human_..._DKFZ_02
    # Extract DKFZ_XX from title
    def extract_id(title):
        title = str(title)
        for part in title.split("_"):
            if part.upper().startswith("DKFZ"):
                # get next part too
                idx = title.split("_").index(
                    part
                )
                parts = title.split("_")
                if idx + 1 < len(parts):
                    return (
                        parts[idx]
                        + "_"
                        + parts[idx + 1]
                    )
                return part
        return title

    meta["sample_id"] = meta[
        "title"
    ].apply(extract_id)

    log(f"  Meta sample IDs: "
        f"{list(meta['sample_id'].head(5))}")
    log(f"  Expr columns  : "
        f"{list(expr_T.columns[:5])}")

    meta_cols = [c for c in [
        "tissue",
        "disease_stage",
        "gleason_pattern_group",
        "source",
    ] if c in meta.columns]

    merged = expr_T.T.join(
        meta.set_index("sample_id")[meta_cols],
        how="left",
    )

    # Classify
    merged["group"] = "UNKNOWN"
    if "disease_stage" in merged.columns:
        ds = merged["disease_stage"].fillna(
            ""
        ).str.lower()
        merged.loc[
            ds.str.contains("cancer|tumor"),
            "group"
        ] = "TUMOR"
        merged.loc[
            ds.str.contains("benign|normal"),
            "group"
        ] = "NORMAL"

    # Fallback from source
    if (merged["group"] == "UNKNOWN").sum() > 5:
        src = merged["source"].fillna(
            ""
        ).str.lower() \
            if "source" in merged.columns \
            else pd.Series(
                "", index=merged.index
            )
        merged.loc[
            src.str.contains("tumor|cancer|malignant"),
            "group"
        ] = "TUMOR"
        merged.loc[
            src.str.contains(
                "benign|normal|adjacent"
            ),
            "group"
        ] = "NORMAL"

    # Fallback from column name
    for idx in merged[
        merged["group"] == "UNKNOWN"
    ].index:
        idx_l = str(idx).lower()
        if "tumor" in idx_l \
                or "cancer" in idx_l:
            merged.loc[idx, "group"] = "TUMOR"
        elif "benign" in idx_l \
                or "normal" in idx_l:
            merged.loc[idx, "group"] = "NORMAL"

    log(f"  TUMOR  : "
        f"{(merged['group']=='TUMOR').sum()}")
    log(f"  NORMAL : "
        f"{(merged['group']=='NORMAL').sum()}")
    log(f"  UNKNOWN: "
        f"{(merged['group']=='UNKNOWN').sum()}")

    # Gleason
    if "gleason_pattern_group" in merged.columns:
        gc = merged[
            merged["group"] == "TUMOR"
        ]["gleason_pattern_group"].value_counts()
        log(f"\n  Gleason distribution:")
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
    log("")

    role_map = {}
    for g in SWITCH_GENES:     role_map[g]="SWITCH"
    for g in FA_MARKERS:       role_map[g]="FA"
    for g in EPIGENETIC:       role_map[g]="EPIGEN"
    for g in AR_AXIS:          role_map[g]="AR"
    for g in SCAFFOLD:         role_map[g]="SCAFFOLD"
    for g in LUMINAL:          role_map[g]="LUMINAL"
    for g in BASAL:            role_map[g]="BASAL"
    for g in EMT:              role_map[g]="EMT"
    for g in ERG_PROGRAM:      role_map[g]="ERG"
    for g in NEUROENDOCRINE:   role_map[g]="NE"
    for g in PROGNOSIS:        role_map[g]="PROG"

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

    log(f"  {'Gene':<12} {'Role':<9} "
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

        chg_str = (
            f"{chg:+.1f}%"
            if not np.isnan(chg) else "N/A"
        )
        log(f"  {gene:<12} {role:<9} "
            f"{nd_m:>9.4f} {td_m:>9.4f} "
            f"{chg_str:>9}  "
            f"{fmt_p(p_use):>16}")

        results.append({
            "gene":        gene,
            "role":        role,
            "normal_mean": nd_m,
            "tumor_mean":  td_m,
            "change_pct":  chg,
            "p_supp":      p_s,
            "p_elev":      p_e,
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
            else pd.Series(
                0.0, index=s.index
            )
        )

    tumor  = tumor.copy()
    depth  = pd.Series(
        np.zeros(len(tumor)),
        index=tumor.index,
    )
    comp   = 0

    sw_avail = [
        g for g in SWITCH_GENES
        if g in gene_cols
    ]
    fa_avail = [
        g for g in FA_MARKERS
        if g in gene_cols
    ]

    if sw_avail:
        sw_mean = tumor[sw_avail].mean(axis=1)
        depth  += (1 - norm01(sw_mean))
        comp   += 1
        log(f"  Comp 1: switch suppression "
            f"genes={sw_avail}")

    if fa_avail:
        fa_mean = tumor[fa_avail].mean(axis=1)
        depth  += norm01(fa_mean)
        comp   += 1
        log(f"  Comp 2: FA elevation "
            f"genes={fa_avail}")

    if comp > 0:
        depth /= comp

    tumor["block_depth"] = depth.values

    log(f"\n  Depth ({len(tumor)} tumors):")
    log(f"    Mean  : {depth.mean():.4f}")
    log(f"    Median: {depth.median():.4f}")
    log(f"    Std   : {depth.std():.4f}")
    log(f"    Min   : {depth.min():.4f}")
    log(f"    Max   : {depth.max():.4f}")

    # Gleason stratification
    if "gleason_pattern_group" in tumor.columns:
        log(f"\n  Depth by Gleason:")
        for g in ["high", "low"]:
            sd = tumor[
                tumor["gleason_pattern_group"]
                == g
            ]["block_depth"]
            if len(sd) > 2:
                log(f"    {g:<6} "
                    f"(n={len(sd):3d}): "
                    f"{sd.mean():.4f} "
                    f"± {sd.std():.4f}")
        # Test high > low
        hi = tumor[
            tumor["gleason_pattern_group"]
            == "high"
        ]["block_depth"]
        lo = tumor[
            tumor["gleason_pattern_group"]
            == "low"
        ]["block_depth"]
        if len(hi) > 3 and len(lo) > 3:
            _, p_gl = stats.mannwhitneyu(
                hi, lo, alternative="greater"
            )
            log(f"\n  High > Low depth: "
                f"p={p_gl:.4f}")
            log(f"  Prediction: high Gleason "
                f"= deeper block")
            log(f"  Result: "
                f"{'CONFIRMED' if p_gl < 0.05 else 'NOT CONFIRMED'}")

    # Depth correlations
    corrs = []
    for gene in gene_cols:
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
    log(f"  {'Gene':<12} {'r':>8}  p-value")
    log(f"  {'-'*34}")
    for gene, rv, pv in corrs[:20]:
        log(f"  {gene:<12} {rv:>+8.4f}  "
            f"p={pv:.2e}")

    return tumor, corrs

# ============================================================
# STEP 7: ERG ANALYSIS
# Predict: bimodal ERG expression
# Fusion-positive = ERG high
# ============================================================

def erg_analysis(tumor, normal):
    log("")
    log("=" * 65)
    log("STEP 7: ERG ANALYSIS")
    log("Prediction: bimodal ERG in tumors")
    log("Fusion+ = ERG high / Fusion- = ERG low")
    log("=" * 65)

    gene_cols = [
        c for c in tumor.columns
        if c in ALL_TARGET
    ]

    if "ERG" not in gene_cols:
        log("  ERG not found in matrix — skip")
        return tumor

    erg_t = tumor["ERG"].values
    erg_n = normal["ERG"].values

    log(f"\n  ERG in normal: "
        f"{erg_n.mean():.4f} ± {erg_n.std():.4f}")
    log(f"  ERG in tumor:  "
        f"{erg_t.mean():.4f} ± {erg_t.std():.4f}")
    log(f"  ERG range (tumor): "
        f"{erg_t.min():.4f} – {erg_t.max():.4f}")

    # Bimodality test
    from scipy.stats import gaussian_kde
    try:
        kde  = gaussian_kde(erg_t)
        xmin = erg_t.min()
        xmax = erg_t.max()
        xs   = np.linspace(xmin, xmax, 200)
        ys   = kde(xs)

        # Find local minima in KDE
        from scipy.signal import argrelmin
        mins_idx = argrelmin(ys, order=5)[0]
        log(f"\n  KDE local minima: "
            f"{len(mins_idx)}")
        if len(mins_idx) > 0:
            threshold = xs[mins_idx[0]]
            log(f"  Threshold: {threshold:.4f}")
            n_high = (erg_t > threshold).sum()
            n_low  = (erg_t <= threshold).sum()
            log(f"  ERG-high (fusion+?): {n_high}")
            log(f"  ERG-low  (fusion-?): {n_low}")
            log(f"  Prediction: bimodal")
            log(f"  Result: "
                f"{'CONFIRMED' if len(mins_idx) > 0 else 'NOT CONFIRMED'}")
            tumor = tumor.copy()
            tumor["erg_status"] = np.where(
                tumor["ERG"] > threshold,
                "ERG_high", "ERG_low"
            )
        else:
            log("  No clear bimodal threshold found")
            tumor = tumor.copy()
            med   = np.median(erg_t)
            tumor["erg_status"] = np.where(
                tumor["ERG"] > med,
                "ERG_high", "ERG_low"
            )
    except Exception as e:
        log(f"  KDE error: {e}")

    # ERG-high vs ERG-low key genes
    if "erg_status" in tumor.columns:
        erg_hi = tumor[
            tumor["erg_status"] == "ERG_high"
        ]
        erg_lo = tumor[
            tumor["erg_status"] == "ERG_low"
        ]
        log(f"\n  Key genes by ERG status:")
        log(f"  {'Gene':<12} "
            f"{'ERG-high':>10} "
            f"{'ERG-low':>10} "
            f"{'Change':>9}")
        log(f"  {'-'*48}")
        key_genes = [g for g in [
            "NKX3-1", "FOXA1", "KLK3",
            "AR", "TMPRSS2", "MYC",
            "EZH2", "MKI67",
        ] if g in gene_cols]
        for gene in key_genes:
            hm = erg_hi[gene].mean()
            lm = erg_lo[gene].mean()
            chg = ((hm - lm) / lm * 100
                   if lm > 0.0001 else np.nan)
            chg_str = (
                f"{chg:+.1f}%"
                if not np.isnan(chg) else "N/A"
            )
            log(f"  {gene:<12} "
                f"{hm:>10.4f} "
                f"{lm:>10.4f} "
                f"{chg_str:>9}")

    return tumor

# ============================================================
# STEP 8: AR AXIS ANALYSIS
# ============================================================

def ar_axis_analysis(tumor, normal):
    log("")
    log("=" * 65)
    log("STEP 8: AR AXIS ANALYSIS")
    log("AR drives luminal identity")
    log("Prediction: AR maintained/elevated")
    log("KLK3/PSA: suppressed in high Gleason")
    log("=" * 65)

    gene_cols = [
        c for c in tumor.columns
        if c in ALL_TARGET
    ]

    log(f"\n  AR axis in tumor vs normal:")
    log(f"  {'Gene':<10} {'Normal':>9} "
        f"{'Tumor':>9} {'Change':>9}")
    log(f"  {'-'*40}")
    for gene in AR_AXIS:
        if gene not in gene_cols:
            continue
        nm = normal[gene].mean()
        tm = tumor[gene].mean()
        chg = ((tm - nm) / nm * 100
               if nm > 0.0001 else np.nan)
        chg_str = (
            f"{chg:+.1f}%"
            if not np.isnan(chg) else "N/A"
        )
        log(f"  {gene:<10} {nm:>9.4f} "
            f"{tm:>9.4f} {chg_str:>9}")

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
                log(f"    {g:<6}: "
                    f"{sd.mean():.4f} "
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
                lo_k, hi_k,
                alternative="greater"
            )
            log(f"  Low > High Gleason KLK3: "
                f"p={p_k:.4f}")
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

    clr = {
        "NORMAL": "#2980b9",
        "TUMOR":  "#c0392b",
    }
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
            sems  = [
                df_g[g].sem()
                if g in df_g.columns else 0
                for g in avail
            ]
            ax.bar(
                x + i*w - 0.5*w, means, w,
                yerr=sems, color=c,
                label=grp, capsize=3,
                alpha=0.85,
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
    bar_pair(ax_a, SWITCH_GENES,
             "A — Switch Genes\n"
             "NKX3-1/FOXA1/KLK3 predicted DOWN")

    # B — FA markers
    ax_b = fig.add_subplot(gs[0, 1])
    bar_pair(ax_b,
             ["ERG", "EZH2", "MKI67",
              "HOXC6", "AMACR"],
             "B — FA Markers\n"
             "ERG/EZH2/MKI67 predicted UP")

    # C — Waterfall
    ax_c = fig.add_subplot(gs[0, 2])
    if len(results_df) > 0:
        pdf = results_df[
            results_df["normal_mean"] > 0.01
        ].copy().sort_values("change_pct")
        bar_c = [
            "#c0392b" if v < 0
            else "#27ae60"
            for v in pdf["change_pct"]
        ]
        ax_c.barh(
            pdf["gene"],
            pdf["change_pct"],
            color=bar_c,
        )
        ax_c.axvline(
            0, color="black", linewidth=0.8
        )
        ax_c.set_xlabel(
            "% change vs benign", fontsize=8
        )
        ax_c.set_title(
            "C — All Genes % Change\n"
            "Red=down Green=up",
            fontsize=9,
        )
        ax_c.tick_params(
            axis="y", labelsize=6
        )

    # D — Block depth by Gleason
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
                    sd, bins=15, alpha=0.6,
                    color=c, label=f"Gleason {g}",
                    edgecolor="white",
                )
        ax_d.set_xlabel(
            "Block Depth Score", fontsize=8
        )
        ax_d.set_ylabel("Count", fontsize=8)
        ax_d.set_title(
            "D — Depth by Gleason\n"
            "Prediction: high deeper",
            fontsize=9,
        )
        ax_d.legend(fontsize=7)

    # E — AR axis
    ax_e = fig.add_subplot(gs[1, 1])
    bar_pair(ax_e, AR_AXIS,
             "E — AR Axis\n"
             "AR/KLK3/FOXA1/NKX3-1")

    # F — Epigenetic
    ax_f = fig.add_subplot(gs[1, 2])
    bar_pair(ax_f,
             ["EZH2", "EED", "SUZ12",
              "KDM6A", "BMI1"],
             "F — Epigenetic\n"
             "EZH2 predicted UP")

    # G — ERG scatter
    ax_g = fig.add_subplot(gs[2, 0])
    if "ERG" in gene_cols:
        ax_g.scatter(
            range(len(normal)),
            normal["ERG"].values,
            color=clr["NORMAL"],
            alpha=0.5, s=20, label="Normal",
        )
        ax_g.scatter(
            range(len(tumor)),
            tumor["ERG"].values,
            color=clr["TUMOR"],
            alpha=0.5, s=20, label="PRAD",
        )
        ax_g.set_xlabel("Sample index",
                         fontsize=8)
        ax_g.set_ylabel("ERG expression",
                         fontsize=8)
        ax_g.set_title(
            "G — ERG Expression\n"
            "Bimodal? Fusion+ vs Fusion-",
            fontsize=9,
        )
        ax_g.legend(fontsize=7)

    # H — Depth correlations waterfall
    ax_h = fig.add_subplot(gs[2, 1])
    if corrs:
        top_c  = corrs[:20]
        genes_c = [c[0] for c in top_c]
        vals_c  = [c[1] for c in top_c]
        cols_c  = [
            "#c0392b" if v < 0
            else "#27ae60"
            for v in vals_c
        ]
        ax_h.barh(genes_c, vals_c,
                  color=cols_c)
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
        ax_h.tick_params(
            axis="y", labelsize=7
        )

    # I — Summary
    ax_i = fig.add_subplot(gs[2, 2])
    ax_i.axis("off")
    summary = (
        "I — SUMMARY\n"
        "───────────────────────────\n"
        "Dataset: GSE32571\n"
        "  59 PRAD | 39 Benign\n"
        "  Matched pairs (DKFZ)\n"
        "  Illumina HumanHT-12\n"
        "  Gleason high/low\n\n"
        "Lineage:\n"
        "  Luminal epithelial\n"
        "  → dedifferentiated\n"
        "    progenitor hybrid\n\n"
        "Predictions:\n"
        "  Switch: NKX3-1/FOXA1/KLK3\n"
        "  FA: ERG/EZH2/MKI67\n"
        "  EZH2 gain lock\n"
        "  MYC elevated\n\n"
        "Drug targets:\n"
        "  1. AR inhibitor (std)\n"
        "  2. EZH2 inhibitor\n"
        "  3. NKX3-1 restoration\n"
        "  4. MYC/BET inhibitor\n\n"
        "Framework: OrganismCore\n"
        "Doc: 88a | 2026-03-01\n"
        "Status: PENDING RUN"
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
        RESULTS_DIR,
        "prad_false_attractor.png",
    )
    plt.savefig(
        outpath, dpi=150,
        bbox_inches="tight",
    )
    log(f"\n  Figure: {outpath}")
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
    log("  MYC:    ELEVATED (not secretory bias)")
    log("  Gleason: high grade = deeper block")
    log("  ERG: bimodal (fusion+ vs fusion-)")
    log("")

    log("\n=== STEP 0: DATA ===")
    paths = download_all()

    log("\n=== STEP 1: METADATA ===")
    meta = fetch_metadata()

    log("\n=== STEP 2: LOAD + NORMALIZE ===")
    expr_df, expr_cols = load_and_normalize(
        paths["matrix"]
    )

    log("\n=== STEP 3: PROBE MAPPING ===")
    probe_map = get_probe_map()
    gene_df   = map_probes_to_genes(
        expr_df, probe_map
    )

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
