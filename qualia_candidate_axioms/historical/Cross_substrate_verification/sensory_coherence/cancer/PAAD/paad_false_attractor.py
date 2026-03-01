"""
Pancreatic Ductal Adenocarcinoma — False Attractor Analysis
SCRIPT 1 — DISCOVERY RUN
Dataset: GSE183795
  139 PAAD tumors | 105 adjacent non-tumor pancreas
  Affymetrix HuGene-1.0-ST arrays
  Pre-normalized matrix — gene symbols as row index
  Stage, grading, resection margin, survival annotated

FRAMEWORK: OrganismCore Principles-First
Doc: 87a | Date: 2026-03-01

PREDICTIONS LOCKED BEFORE DATA:
  Switch genes (predicted suppressed in PAAD):
    PTF1A  — acinar master TF — ADM initiating event
    NR5A2  — acinar TF — PAAD germline risk gene
    RBPJL  — acinar-specific Notch TF
    MIST1  — (BHLHA15) acinar secretory identity
    CPA1   — acinar digestive enzyme effector
    PRSS1  — trypsinogen 1 acinar effector

  False attractor (predicted elevated in PAAD):
    KRT19  — ductal identity marker
    SOX9   — ductal/progenitor TF
    MUC1   — ductal surface marker
    EPCAM  — progenitor/ductal surface marker

  Epigenetic prediction:
    EZH2 ELEVATED — gain of function lock
    Silences acinar program (PTF1A locus)
    Same direction as BRCA — opposite to MDS

  Scaffold:
    MYC ELEVATED — KRAS drives MYC
    KRAS → RAS/MAPK → MYC → dedifferentiation

  Survival prediction:
    Block depth correlates negatively with survival
    Higher depth = more dedifferentiated = worse OS

  Subtype prediction:
    GATA6 high (Classical) = shallower depth
    GATA6 low (Basal-like) = deeper depth
    Depth stratifies subtypes

  Drug targets (stated before literature):
    1. EZH2 inhibitor — tazemetostat
    2. PTF1A restoration — HMA / demethylation
    3. KRAS→MYC axis — BET inhibitor / OMO-103

ADJACENT NORMAL CAVEAT:
  Normal = adjacent non-tumor pancreas
  Not healthy donor pancreas
  Field effects may understate true differences

Author: Eric Robert Lawson
Framework: OrganismCore Universal Reasoning Substrate
GEO: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE183795
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

BASE_DIR    = "./paad_false_attractor/"
RESULTS_DIR = os.path.join(BASE_DIR, "results")
LOG_FILE    = os.path.join(RESULTS_DIR,
                           "analysis_log.txt")

os.makedirs(BASE_DIR,    exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

GEO_BASE = ("https://ftp.ncbi.nlm.nih.gov/geo/"
            "series/GSE183nnn/GSE183795/suppl/")

FILES = {
    "matrix": "GSE183795_normalized_matrix.txt.gz",
}

META_URL = ("https://www.ncbi.nlm.nih.gov/geo/"
            "query/acc.cgi?acc=GSE183795"
            "&targ=gsm&form=text&view=full")

# ============================================================
# GENE PANELS — LOCKED BEFORE DATA
# ============================================================

# TRUE SWITCH GENES — acinar identity
# Predicted suppressed in PAAD
SWITCH_GENES = [
    "PTF1A",    # acinar master TF
    "NR5A2",    # acinar nuclear receptor
    "RBPJL",    # acinar Notch TF
    "BHLHA15",  # MIST1 — acinar secretory TF
    "CPA1",     # acinar digestive enzyme
    "PRSS1",    # trypsinogen 1
]

# FALSE ATTRACTOR — ductal/progenitor identity
# Predicted elevated in PAAD
FALSE_ATTRACTOR = [
    "KRT19",    # ductal marker
    "SOX9",     # ductal/progenitor TF
    "MUC1",     # ductal surface marker
    "EPCAM",    # progenitor surface marker
]

# EPIGENETIC — EZH2 predicted elevated (gain lock)
EPIGENETIC = [
    "EZH2",     # H3K27me3 — predicted UP
    "EED",      # PRC2 complex
    "SUZ12",    # PRC2 complex
    "TET2",     # DNA demethylation
    "DNMT3A",   # DNA methylation
    "ASXL1",    # chromatin regulator
    "KDM6A",    # H3K27 demethylase (UTX)
]

# SCAFFOLD
SCAFFOLD = [
    "MYC",      # KRAS→MYC — predicted UP
    "KRAS",     # driver mutation — expression
    "MKI67",    # proliferation
    "CCND1",    # cyclin D1
]

# SUBTYPE MARKERS
SUBTYPE = [
    "GATA6",    # Classical subtype marker
    "KRT5",     # Basal-like marker
    "KRT14",    # Basal-like marker
    "VIMENTIN",
    "VIM",      # mesenchymal
    "CDH1",     # E-cadherin — epithelial
    "CDH2",     # N-cadherin — mesenchymal
    "SNAI1",    # EMT TF
    "ZEB1",     # EMT TF
]

# ACINAR EFFECTORS — extended panel
ACINAR_EFFECTORS = [
    "AMY2A",    # amylase 2A
    "AMY2B",    # amylase 2B
    "CELA3A",   # elastase
    "CELA3B",   # elastase
    "CTRB1",    # chymotrypsinogen
    "CTRB2",    # chymotrypsinogen
    "CTRC",     # chymotrypsin C
    "PRSS2",    # trypsinogen 2
    "PRSS3",    # trypsinogen 3
    "PNLIP",    # pancreatic lipase
    "PNLIPRP1", # lipase related
    "PNLIPRP2", # lipase related
    "CEL",      # carboxyl ester lipase
    "CPA2",     # carboxypeptidase A2
    "CPB1",     # carboxypeptidase B1
]

# DUCTAL MARKERS — extended panel
DUCTAL_MARKERS = [
    "KRT7",     # ductal keratin
    "KRT18",    # ductal keratin
    "HNF1B",    # ductal TF
    "CFTR",     # ductal ion channel
    "MUC5B",    # ductal mucin
    "MUC6",     # ductal mucin
    "TFF1",     # trefoil factor
    "TFF2",     # trefoil factor
]

# SURVIVAL / PROGNOSIS
PROGNOSIS = [
    "SPARC",    # stromal — known PAAD marker
    "POSTN",    # periostin — stroma
    "FN1",      # fibronectin — ECM
    "ACTA2",    # smooth muscle actin — stroma
    "PDGFRA",   # stromal receptor
]

ALL_TARGET = list(dict.fromkeys(
    SWITCH_GENES +
    FALSE_ATTRACTOR +
    EPIGENETIC +
    SCAFFOLD +
    SUBTYPE +
    ACINAR_EFFECTORS +
    DUCTAL_MARKERS +
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

def check_and_download(fname):
    local = os.path.join(BASE_DIR, fname)
    if os.path.exists(local):
        size_mb = os.path.getsize(local) / 1e6
        if size_mb > 0.1:
            log(f"  Already downloaded: {fname} "
                f"({size_mb:.1f} MB) — skipping")
            return local
        else:
            log(f"  Found but small: {fname} "
                f"({size_mb:.3f} MB) — re-downloading")
            os.remove(local)

    url = GEO_BASE + fname
    log(f"  Downloading: {fname}")
    log(f"  URL: {url}")

    def reporthook(count, block_size, total_size):
        if total_size > 0:
            pct = min(
                count * block_size
                / total_size * 100, 100
            )
            mb = count * block_size / 1e6
            sys.stdout.write(
                f"\r  {mb:.1f} MB ({pct:.1f}%)"
            )
            sys.stdout.flush()

    urllib.request.urlretrieve(
        url, local, reporthook
    )
    print()
    size_mb = os.path.getsize(local) / 1e6
    log(f"  Complete: {local} ({size_mb:.1f} MB)")
    return local


def download_all():
    log("=" * 65)
    log("STEP 0: DATA ACQUISITION")
    log("Dataset: GSE183795")
    log("  139 PAAD tumors")
    log("  105 adjacent non-tumor pancreas")
    log("  Affymetrix HuGene-1.0-ST")
    log("=" * 65)
    log("\n  Checking for existing downloads...")
    paths = {}
    for key, fname in FILES.items():
        paths[key] = check_and_download(fname)
    log("\n  File status:")
    for key, path in paths.items():
        size_mb = os.path.getsize(path) / 1e6
        log(f"    {key:<10}: "
            f"{os.path.basename(path)} "
            f"({size_mb:.1f} MB)")
    return paths

# ============================================================
# STEP 1: METADATA
# ============================================================

def fetch_metadata():
    log("")
    log("--- Fetching sample metadata ---")

    cache = os.path.join(RESULTS_DIR,
                         "metadata.csv")
    if os.path.exists(cache):
        df = pd.read_csv(cache, index_col=0)
        log(f"  Loaded from cache: {len(df)} samples")
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
    log(f"  Fetched {len(df)} samples — cached")
    return df

# ============================================================
# STEP 2: LOAD MATRIX
# ============================================================

def load_matrix(path):
    log(f"\n  Loading: {os.path.basename(path)}")

    with gzip.open(path, "rt") as f:
        df = pd.read_csv(
            f, sep="\t", index_col=0,
            low_memory=False
        )

    log(f"  Raw shape: {df.shape[0]} genes x "
        f"{df.shape[1]} columns")
    log(f"  First 5 columns: "
        f"{list(df.columns[:5])}")
    log(f"  First 5 index:   "
        f"{list(df.index[:5])}")

    # Drop non-expression columns
    # (Transcript ID, gene_assignment, RefSeq)
    non_expr = []
    for col in df.columns:
        try:
            pd.to_numeric(df[col].iloc[:5])
        except Exception:
            non_expr.append(col)
    if non_expr:
        log(f"  Dropping non-numeric columns: "
            f"{non_expr}")
        df = df.drop(columns=non_expr)

    log(f"  After cleanup: {df.shape[0]} genes x "
        f"{df.shape[1]} samples")

    # Convert to numeric
    df = df.apply(pd.to_numeric, errors="coerce")

    # Keep only target genes
    found   = [g for g in ALL_TARGET
               if g in df.index]
    missing = [g for g in ALL_TARGET
               if g not in df.index]
    log(f"  Target genes found  : "
        f"{len(found)}/{len(ALL_TARGET)}")
    if missing:
        log(f"  Missing: {missing}")

    df = df.loc[found]

    # Transpose: samples x genes
    df = df.T
    df.index.name = "sample_id"

    # Clean index: strip .CEL suffix
    df.index = pd.Index(
        [i.replace(".CEL", "").strip()
         for i in df.index],
        name="sample_id"
    )

    log(f"  Final shape: {df.shape}")
    log(f"  Index sample: {list(df.index[:3])}")
    return df

# ============================================================
# STEP 3: MERGE AND CLASSIFY
# ============================================================

def merge_with_meta(expr, meta):
    log("\n  Merging expression with metadata...")

    meta = meta.copy()

    # Build sample_id from title
    # Title format: 1_E5-Tc8_T or 10_E33-Tn13_N
    # Column names in matrix: 10_E33-Tn13_N
    meta["sample_id"] = (
        meta["title"].astype(str).str.strip()
    )

    meta_cols = [c for c in [
        "tissue",
        "grading",
        "stage",
        "resection_margin",
        "survival_months",
        "survival_status",
    ] if c in meta.columns]

    merged = expr.join(
        meta.set_index("sample_id")[meta_cols],
        how="left"
    )

    log(f"  Merged shape: {merged.shape}")

    # Classify groups
    if "tissue" in merged.columns:
        tis = merged["tissue"].str.lower()
    else:
        tis = pd.Series("unknown",
                        index=merged.index)

    merged["group"] = "UNKNOWN"
    merged.loc[
        tis.str.contains(
            "adjacent|non.tumor|nontumor|normal",
            na=False
        ), "group"
    ] = "NORMAL"
    merged.loc[
        tis.str.contains(
            "tumor|cancer|pdac|carcinoma",
            na=False
        ), "group"
    ] = "TUMOR"

    log(f"\n  Group counts:")
    log(f"    TUMOR  : "
        f"{(merged['group']=='TUMOR').sum()}")
    log(f"    NORMAL : "
        f"{(merged['group']=='NORMAL').sum()}")
    log(f"    UNKNOWN: "
        f"{(merged['group']=='UNKNOWN').sum()}")

    # If too many unknown — try direct title match
    n_unk = (merged["group"] == "UNKNOWN").sum()
    if n_unk > len(merged) * 0.3:
        log(f"\n  WARNING: {n_unk} samples "
            f"unclassified")
        log("  Attempting title-based "
            "classification...")
        for idx in merged[
            merged["group"] == "UNKNOWN"
        ].index:
            idx_l = str(idx).lower()
            if any(kw in idx_l for kw in
                   ["_n", "-tn", "normal",
                    "adjacent"]):
                merged.loc[idx, "group"] = "NORMAL"
            elif any(kw in idx_l for kw in
                     ["_t", "-tc", "-tp",
                      "tumor"]):
                merged.loc[idx, "group"] = "TUMOR"
        log(f"  After fallback:")
        log(f"    TUMOR  : "
            f"{(merged['group']=='TUMOR').sum()}")
        log(f"    NORMAL : "
            f"{(merged['group']=='NORMAL').sum()}")
        log(f"    UNKNOWN: "
            f"{(merged['group']=='UNKNOWN').sum()}")

    # Stage distribution
    if "stage" in merged.columns:
        tumor_stage = merged[
            merged["group"] == "TUMOR"
        ]["stage"].value_counts()
        log(f"\n  Stage distribution (tumor):")
        for stage, n in tumor_stage.items():
            log(f"    {stage}: {n}")

    # Survival
    if "survival_months" in merged.columns:
        merged["survival_months"] = pd.to_numeric(
            merged["survival_months"],
            errors="coerce"
        )
        merged["survival_status"] = pd.to_numeric(
            merged["survival_status"],
            errors="coerce"
        )
        tumor_surv = merged[
            merged["group"] == "TUMOR"
        ]["survival_months"].dropna()
        log(f"\n  Survival (tumor samples):")
        log(f"    n with data: {len(tumor_surv)}")
        log(f"    Median: "
            f"{tumor_surv.median():.1f} months")
        log(f"    Range: "
            f"{tumor_surv.min():.1f} – "
            f"{tumor_surv.max():.1f} months")

    return merged

# ============================================================
# STEP 4: SADDLE POINT ANALYSIS
# ============================================================

def saddle_point_analysis(merged):
    log("")
    log("=" * 70)
    log("STEP 4: SADDLE POINT ANALYSIS")
    log("PAAD TUMOR vs ADJACENT NORMAL PANCREAS")
    log("=" * 70)

    tumor  = merged[merged["group"] == "TUMOR"]
    normal = merged[merged["group"] == "NORMAL"]

    log(f"  TUMOR  : {len(tumor)}")
    log(f"  NORMAL : {len(normal)}")
    log("")
    log("  FRAMEWORK PREDICTIONS (locked before data):")
    log("  Switch genes: PTF1A/NR5A2/RBPJL/"
        "BHLHA15/CPA1/PRSS1 suppressed")
    log("  FA markers:   KRT19/SOX9/MUC1/"
        "EPCAM elevated")
    log("  Epigenetic:   EZH2 elevated (gain lock)")
    log("  Scaffold:     MYC elevated (KRAS driven)")
    log("")

    role_map = {}
    for g in SWITCH_GENES:
        role_map[g] = "SWITCH"
    for g in FALSE_ATTRACTOR:
        role_map[g] = "FA"
    for g in EPIGENETIC:
        role_map[g] = "EPIGEN"
    for g in SCAFFOLD:
        role_map[g] = "SCAFFOLD"
    for g in SUBTYPE:
        role_map[g] = "SUBTYPE"
    for g in ACINAR_EFFECTORS:
        role_map[g] = "ACINAR"
    for g in DUCTAL_MARKERS:
        role_map[g] = "DUCTAL"
    for g in PROGNOSIS:
        role_map[g] = "PROG"

    def fmt_p(p):
        if p < 1e-300:  return "p=0.00e+00 ***"
        elif p < 0.001: return f"p={p:.2e} ***"
        elif p < 0.01:  return f"p={p:.2e}  **"
        elif p < 0.05:  return f"p={p:.4f}   *"
        else:           return f"p={p:.4f}  ns"

    log(f"  {'Gene':<10} {'Role':<10} "
        f"{'Normal':>9} {'Tumor':>9} "
        f"{'Change':>9} {'p-value':>16}  Result")
    log(f"  {'-'*80}")

    results     = []
    gene_cols   = [c for c in merged.columns
                   if c in ALL_TARGET]

    for gene in ALL_TARGET:
        if gene not in gene_cols:
            continue

        nd_v = normal[gene].dropna().values
        td_v = tumor[gene].dropna().values

        if len(nd_v) < 3 or len(td_v) < 3:
            continue

        nd_m = nd_v.mean()
        td_m = td_v.mean()
        chg  = ((td_m - nd_m) / nd_m * 100
                if nd_m > 0.0001 else np.nan)

        _, p_supp = stats.mannwhitneyu(
            nd_v, td_v, alternative="greater"
        )
        _, p_elev = stats.mannwhitneyu(
            td_v, nd_v, alternative="greater"
        )
        p_use = min(p_supp, p_elev)
        role  = role_map.get(gene, "OTHER")

        if role == "SWITCH":
            if p_supp < 0.05 and (chg or 0) < -20:
                result = "CONFIRMED"
            elif p_supp < 0.05:
                result = "WEAKLY SUPPRESSED"
            elif (chg or 0) > 20:
                result = "INVERTED"
            else:
                result = "NOT CONFIRMED"
        elif role == "FA":
            if p_elev < 0.05 and (chg or 0) > 20:
                result = "FA CONFIRMED"
            elif p_elev < 0.05:
                result = "WEAKLY ELEVATED"
            else:
                result = "NOT ELEVATED"
        else:
            result = "SEE DATA"

        chg_str = (f"{chg:+.1f}%"
                   if not np.isnan(chg) else "  N/A")
        log(f"  {gene:<10} {role:<10} "
            f"{nd_m:>9.4f} {td_m:>9.4f} "
            f"{chg_str:>9}  "
            f"{fmt_p(p_use):>16}  {result}")

        results.append({
            "gene":         gene,
            "role":         role,
            "normal_mean":  nd_m,
            "tumor_mean":   td_m,
            "change_pct":   chg,
            "p_supp":       p_supp,
            "p_elev":       p_elev,
            "p_value":      p_use,
            "result":       result,
        })

    rdf = pd.DataFrame(results)
    rdf.to_csv(
        os.path.join(RESULTS_DIR,
                     "saddle_results.csv"),
        index=False
    )
    log(f"\n  Saved: {RESULTS_DIR}/saddle_results.csv")
    return rdf, tumor, normal

# ============================================================
# STEP 5: DEPTH SCORING
# ============================================================

def depth_scoring(merged, tumor, normal, results_df):
    log("")
    log("=" * 70)
    log("STEP 5: BLOCK DEPTH SCORING")
    log("Score = switch suppression + FA elevation")
    log("=" * 70)

    gene_cols = [c for c in merged.columns
                 if c in ALL_TARGET]

    def norm01(s):
        mn, mx = s.min(), s.max()
        return ((s - mn) / (mx - mn)
                if mx > mn
                else pd.Series(0.0, index=s.index))

    depth      = pd.Series(
        np.zeros(len(tumor)), index=tumor.index
    )
    components = 0

    sw_avail = [g for g in SWITCH_GENES
                if g in gene_cols]
    fa_avail = [g for g in FALSE_ATTRACTOR
                if g in gene_cols]

    if sw_avail:
        sw_norm     = norm01(
            tumor[sw_avail].mean(axis=1)
        )
        depth      += (1 - sw_norm)
        components += 1
        log(f"  Component 1: Switch suppression "
            f"genes={sw_avail}")

    if fa_avail:
        fa_norm     = norm01(
            tumor[fa_avail].mean(axis=1)
        )
        depth      += fa_norm
        components += 1
        log(f"  Component 2: FA elevation "
            f"genes={fa_avail}")

    if components > 0:
        depth /= components

    tumor = tumor.copy()
    tumor["block_depth"] = depth.values

    log(f"\n  Depth statistics ({len(tumor)} tumors):")
    log(f"    Mean   : {depth.mean():.4f}")
    log(f"    Median : {depth.median():.4f}")
    log(f"    Std    : {depth.std():.4f}")
    log(f"    Min    : {depth.min():.4f}")
    log(f"    Max    : {depth.max():.4f}")
    log(f"    Q25    : {depth.quantile(0.25):.4f}")
    log(f"    Q75    : {depth.quantile(0.75):.4f}")

    # Depth by stage
    if "stage" in tumor.columns:
        log("\n  Block depth by stage:")
        for stage in ["IA", "IB", "IIA", "IIB",
                      "III", "IV"]:
            s_depth = tumor[
                tumor["stage"] == stage
            ]["block_depth"]
            if len(s_depth) > 2:
                log(f"    {stage:>5} "
                    f"(n={len(s_depth):3d}): "
                    f"{s_depth.mean():.4f} ± "
                    f"{s_depth.std():.4f}")

    # Depth correlations
    log("\n  Depth correlations (all genes):")
    corrs = []
    for gene in gene_cols:
        try:
            r, p = stats.pearsonr(
                tumor["block_depth"].values,
                tumor[gene].values
            )
            corrs.append((gene, r, p))
        except Exception:
            pass
    corrs.sort(
        key=lambda x: abs(x[1]), reverse=True
    )
    log(f"  {'Gene':<12} {'r':>8}  p-value")
    log(f"  {'-'*36}")
    for gene, r, p in corrs[:20]:
        log(f"  {gene:<12} {r:>+8.4f}  "
            f"p={p:.2e}")

    return tumor, corrs

# ============================================================
# STEP 6: SURVIVAL ANALYSIS
# ============================================================

def survival_analysis(tumor):
    log("")
    log("=" * 70)
    log("STEP 6: SURVIVAL ANALYSIS")
    log("Prediction: depth correlates negatively "
        "with survival")
    log("Higher depth = more dedifferentiated "
        "= worse prognosis")
    log("=" * 70)

    if "block_depth" not in tumor.columns:
        log("  block_depth not computed — skip")
        return

    if "survival_months" not in tumor.columns:
        log("  survival_months not in data — skip")
        return

    surv = tumor[
        ["block_depth",
         "survival_months",
         "survival_status",
         "stage"]
    ].copy()
    surv = surv.dropna(
        subset=["survival_months", "block_depth"]
    )
    surv["survival_months"] = pd.to_numeric(
        surv["survival_months"], errors="coerce"
    )
    surv = surv.dropna(subset=["survival_months"])

    log(f"\n  Samples with survival data: {len(surv)}")

    if len(surv) < 10:
        log("  Too few samples — skip")
        return

    # Pearson r: depth vs survival
    r, p = stats.pearsonr(
        surv["block_depth"].values,
        surv["survival_months"].values
    )
    log(f"\n  Depth vs survival (Pearson):")
    log(f"    r = {r:+.4f}  p = {p:.2e}")
    log(f"    Prediction: negative r")
    log(f"    Result: "
        f"{'CONFIRMED' if r < -0.1 and p < 0.05 else 'NOT CONFIRMED'}")

    # Spearman (non-parametric)
    rs, ps = stats.spearmanr(
        surv["block_depth"].values,
        surv["survival_months"].values
    )
    log(f"\n  Depth vs survival (Spearman):")
    log(f"    rho = {rs:+.4f}  p = {ps:.2e}")

    # High vs low depth survival
    median_depth = surv["block_depth"].median()
    high = surv[surv["block_depth"] >= median_depth]
    low  = surv[surv["block_depth"] <  median_depth]

    log(f"\n  High depth (n={len(high)}): "
        f"median survival = "
        f"{high['survival_months'].median():.1f} mo")
    log(f"  Low  depth (n={len(low)}): "
        f"median survival = "
        f"{low['survival_months'].median():.1f} mo")

    if len(high) > 3 and len(low) > 3:
        _, p_mw = stats.mannwhitneyu(
            high["survival_months"].dropna().values,
            low["survival_months"].dropna().values,
            alternative="less"
        )
        log(f"  High vs Low depth "
            f"(high worse): p={p_mw:.4f}")
        log(f"  Result: "
            f"{'CONFIRMED' if p_mw < 0.05 else 'NOT CONFIRMED'}")

    # Gene-level survival correlations
    gene_cols = [c for c in tumor.columns
                 if c in ALL_TARGET]
    log(f"\n  Gene vs survival correlations "
        f"(top 15):")
    gene_surv = tumor[
        gene_cols + ["survival_months"]
    ].dropna(subset=["survival_months"]).copy()
    gene_surv["survival_months"] = pd.to_numeric(
        gene_surv["survival_months"], errors="coerce"
    ).dropna()

    surv_corrs = []
    for gene in gene_cols:
        if gene in gene_surv.columns:
            try:
                r2, p2 = stats.pearsonr(
                    gene_surv[gene].values,
                    gene_surv[
                        "survival_months"
                    ].values
                )
                surv_corrs.append((gene, r2, p2))
            except Exception:
                pass
    surv_corrs.sort(
        key=lambda x: abs(x[1]), reverse=True
    )
    log(f"  {'Gene':<12} {'r':>8}  p-value  "
        f"Role")
    log(f"  {'-'*48}")

    role_map = {}
    for g in SWITCH_GENES:
        role_map[g] = "SWITCH"
    for g in FALSE_ATTRACTOR:
        role_map[g] = "FA"
    for g in ACINAR_EFFECTORS:
        role_map[g] = "ACINAR"
    for g in DUCTAL_MARKERS:
        role_map[g] = "DUCTAL"
    for g in EPIGENETIC:
        role_map[g] = "EPIGEN"
    for g in SCAFFOLD:
        role_map[g] = "SCAFFOLD"

    for gene, r2, p2 in surv_corrs[:15]:
        role = role_map.get(gene, "")
        log(f"  {gene:<12} {r2:>+8.4f}  "
            f"p={p2:.2e}  {role}")

    return surv

# ============================================================
# STEP 7: SUBTYPE ANALYSIS
# ============================================================

def subtype_analysis(tumor):
    log("")
    log("=" * 70)
    log("STEP 7: SUBTYPE ANALYSIS")
    log("Prediction: GATA6 stratifies depth")
    log("Classical (GATA6 high) = shallower")
    log("Basal-like (GATA6 low) = deeper")
    log("=" * 70)

    gene_cols = [c for c in tumor.columns
                 if c in ALL_TARGET]

    if "GATA6" not in gene_cols:
        log("  GATA6 not in matrix — skip")
        return

    if "block_depth" not in tumor.columns:
        log("  block_depth not computed — skip")
        return

    gata6_med = tumor["GATA6"].median()
    classical = tumor[tumor["GATA6"] >= gata6_med]
    basal     = tumor[tumor["GATA6"] <  gata6_med]

    log(f"\n  GATA6 median: {gata6_med:.4f}")
    log(f"  Classical (GATA6 high): n={len(classical)}")
    log(f"  Basal-like (GATA6 low): n={len(basal)}")

    if len(classical) > 5 and len(basal) > 5:
        cl_d = classical["block_depth"]
        ba_d = basal["block_depth"]

        log(f"\n  Classical depth: "
            f"{cl_d.mean():.4f} ± {cl_d.std():.4f}")
        log(f"  Basal depth:     "
            f"{ba_d.mean():.4f} ± {ba_d.std():.4f}")

        _, p = stats.mannwhitneyu(
            ba_d, cl_d, alternative="greater"
        )
        log(f"\n  Basal > Classical: p={p:.4f}")
        log(f"  Prediction: Basal deeper")
        log(f"  Result: "
            f"{'CONFIRMED' if p < 0.05 else 'NOT CONFIRMED'}")

        # Survival by subtype
        if "survival_months" in tumor.columns:
            cl_s = classical[
                "survival_months"
            ].dropna()
            ba_s = basal[
                "survival_months"
            ].dropna()
            if len(cl_s) > 3 and len(ba_s) > 3:
                _, p_s = stats.mannwhitneyu(
                    cl_s, ba_s,
                    alternative="greater"
                )
                log(f"\n  Classical survival: "
                    f"{cl_s.median():.1f} mo")
                log(f"  Basal survival:     "
                    f"{ba_s.median():.1f} mo")
                log(f"  Classical > Basal: "
                    f"p={p_s:.4f}")

        # Key genes by subtype
        key_genes = [g for g in
                     SWITCH_GENES[:4] +
                     FALSE_ATTRACTOR[:3] +
                     ["GATA6", "EZH2", "MYC"]
                     if g in gene_cols]

        log(f"\n  {'Gene':<12} "
            f"{'Classical':>11} "
            f"{'Basal':>11} {'Change':>9}")
        log(f"  {'-'*48}")
        for gene in key_genes:
            cl_m = classical[gene].mean()
            ba_m = basal[gene].mean()
            chg  = ((ba_m - cl_m) / cl_m * 100
                    if cl_m > 0.0001 else np.nan)
            chg_str = (f"{chg:+.1f}%"
                       if not np.isnan(chg)
                       else "N/A")
            log(f"  {gene:<12} {cl_m:>11.4f} "
                f"{ba_m:>11.4f} {chg_str:>9}")

# ============================================================
# STEP 8: DRUG TARGET DERIVATION
# ============================================================

def drug_target_derivation(normal, tumor,
                            results_df):
    log("")
    log("=" * 70)
    log("STEP 8: DRUG TARGET DERIVATION")
    log("From geometry — before literature")
    log("=" * 70)

    gene_cols = [c for c in tumor.columns
                 if c in ALL_TARGET]

    log("\n  Switch gene expression:")
    log(f"  {'Gene':<12} {'Normal':>9} "
        f"{'Tumor':>9} {'Change':>9}")
    log(f"  {'-'*44}")
    for gene in SWITCH_GENES:
        if gene in gene_cols:
            nd_m = normal[gene].mean()
            td_m = tumor[gene].mean()
            chg  = ((td_m - nd_m) / nd_m * 100
                    if nd_m > 0.0001 else np.nan)
            chg_str = (f"{chg:+.1f}%"
                       if not np.isnan(chg)
                       else "N/A")
            log(f"  {gene:<12} {nd_m:>9.4f} "
                f"{td_m:>9.4f} {chg_str:>9}")

    log("\n  EZH2 status:")
    if "EZH2" in gene_cols:
        nd_m = normal["EZH2"].mean()
        td_m = tumor["EZH2"].mean()
        chg  = ((td_m - nd_m) / nd_m * 100
                if nd_m > 0.0001 else np.nan)
        log(f"    Normal: {nd_m:.4f}  "
            f"Tumor: {td_m:.4f}  "
            f"Change: {chg:+.1f}%")
        log(f"    Prediction: ELEVATED")
        log(f"    Result: "
            f"{'CONFIRMED' if (chg or 0) > 10 else 'NOT CONFIRMED'}")

    log(f"""
  ============================================================
  DRUG TARGET PREDICTIONS — GEOMETRY-DERIVED
  Stated before literature consultation
  ============================================================

  PREDICTION 1: EZH2 INHIBITOR
    Geometry: EZH2 gain-of-function lock
              Silences acinar TF program
              PTF1A locus H3K27me3 methylated
    Drug:     Tazemetostat (FDA approved)
              EZH2 inhibitor + gemcitabine
    Mechanism: Demethylate acinar gene loci
               Restore PTF1A/NR5A2 expression
               Dissolve false attractor

  PREDICTION 2: PTF1A RESTORATION / HMA
    Geometry: PTF1A is the master switch gene
              Its suppression is the block
    Drug:     Azacitidine/decitabine
              Demethylate PTF1A promoter
              Or: direct CRISPRa at PTF1A locus
    Mechanism: Restore acinar identity
               → PAAD cannot maintain
               ductal/mesenchymal phenotype

  PREDICTION 3: BET INHIBITOR / MYC AXIS
    Geometry: MYC elevated (KRAS driven)
              MYC maintains dedifferentiation
    Drug:     JQ1 / BET inhibitor
              OMO-103 (MYC inhibitor in trials)
    Mechanism: Reduce MYC transcription
               Collapse proliferative drive
               at the block point
               Combined with differentiation
               therapy (EZH2i) for dual attack

  PREDICTION 4: DEPTH SCORE AS BIOMARKER
    Geometry: Block depth correlates with survival
              High depth = basal-like = worse OS
    Clinical: Depth score at diagnosis stratifies
              high-risk vs low-risk PAAD
              High depth → aggressive combo therapy
              Low depth → single agent tolerable
  ============================================================
    """)

# ============================================================
# STEP 9: FIGURE
# ============================================================

def generate_figure(merged, tumor, normal,
                    results_df, surv_data):

    clr = {
        "NORMAL": "#2980b9",
        "TUMOR":  "#c0392b",
    }

    fig = plt.figure(figsize=(26, 20))
    fig.suptitle(
        "Pancreatic Ductal Adenocarcinoma — "
        "False Attractor Analysis\n"
        "Dataset: GSE183795 | 139 PAAD | "
        "105 Adjacent Normal | "
        "OrganismCore 2026-03-01\n"
        "Acinar → Ductal/Mesenchymal false "
        "attractor | EZH2 lock | "
        "PTF1A switch gene | Doc 87a",
        fontsize=10, fontweight="bold", y=0.99
    )
    gs = gridspec.GridSpec(
        3, 3, figure=fig,
        hspace=0.52, wspace=0.42
    )

    gene_cols = [c for c in merged.columns
                 if c in ALL_TARGET]

    def bar_pair(ax, genes, title,
                 ylabel="Expression"):
        avail = [g for g in genes
                 if g in gene_cols]
        if not avail:
            ax.text(0.5, 0.5,
                    "No genes available",
                    ha="center", va="center",
                    transform=ax.transAxes)
            ax.set_title(title)
            return
        x = np.arange(len(avail))
        w = 0.35
        for i, (grp, df_g, c) in enumerate([
            ("Normal", normal, clr["NORMAL"]),
            ("PAAD",   tumor,  clr["TUMOR"]),
        ]):
            means = [df_g[g].mean()
                     if g in df_g.columns else 0
                     for g in avail]
            sems  = [df_g[g].sem()
                     if g in df_g.columns else 0
                     for g in avail]
            ax.bar(x + i*w - 0.5*w, means, w,
                   yerr=sems, color=c,
                   label=grp, capsize=3,
                   alpha=0.85)
        ax.set_xticks(x)
        ax.set_xticklabels(
            avail, rotation=45,
            ha="right", fontsize=8
        )
        ax.set_ylabel(ylabel, fontsize=8)
        ax.set_title(title, fontsize=9)
        ax.legend(fontsize=7)

    # A — Switch genes
    ax_a = fig.add_subplot(gs[0, 0])
    bar_pair(ax_a, SWITCH_GENES,
             "A — Switch Genes\n"
             "PTF1A/NR5A2/CPA1 predicted DOWN")

    # B — False attractor
    ax_b = fig.add_subplot(gs[0, 1])
    bar_pair(ax_b, FALSE_ATTRACTOR,
             "B — False Attractor Markers\n"
             "KRT19/SOX9/MUC1 predicted UP")

    # C — Waterfall
    ax_c = fig.add_subplot(gs[0, 2])
    if len(results_df) > 0:
        plot_df = results_df[
            results_df["normal_mean"] > 0.01
        ].copy().sort_values("change_pct")
        bar_c = ["#c0392b" if v < 0
                 else "#27ae60"
                 for v in plot_df["change_pct"]]
        ax_c.barh(
            plot_df["gene"],
            plot_df["change_pct"],
            color=bar_c
        )
        ax_c.axvline(
            0, color="black", linewidth=0.8
        )
        ax_c.set_xlabel(
            "% change PAAD vs Normal",
            fontsize=8
        )
        ax_c.set_title(
            "C — All Genes % Change\n"
            "Red=suppressed Green=elevated",
            fontsize=9
        )
        ax_c.tick_params(axis="y", labelsize=6)

    # D — Block depth distribution
    ax_d = fig.add_subplot(gs[1, 0])
    if "block_depth" in tumor.columns:
        d = tumor["block_depth"]
        ax_d.hist(d, bins=30,
                  color=clr["TUMOR"],
                  edgecolor="white", alpha=0.85)
        ax_d.axvline(
            d.mean(), color="black",
            linewidth=1.5,
            label=f"Mean={d.mean():.3f}"
        )
        ax_d.set_xlabel("Block Depth Score",
                         fontsize=8)
        ax_d.set_ylabel("Count", fontsize=8)
        ax_d.set_title(
            "D — Block Depth Distribution\n"
            "(PAAD tumors)",
            fontsize=9
        )
        ax_d.legend(fontsize=7)

    # E — Depth vs survival scatter
    ax_e = fig.add_subplot(gs[1, 1])
    if ("block_depth" in tumor.columns and
            "survival_months" in tumor.columns):
        sv = tumor[
            ["block_depth", "survival_months"]
        ].dropna()
        sv["survival_months"] = pd.to_numeric(
            sv["survival_months"], errors="coerce"
        )
        sv = sv.dropna()
        if len(sv) > 5:
            ax_e.scatter(
                sv["block_depth"],
                sv["survival_months"],
                alpha=0.4, s=20,
                color=clr["TUMOR"]
            )
            ax_e.set_xlabel(
                "Block Depth Score",
                fontsize=8
            )
            ax_e.set_ylabel(
                "Survival (months)",
                fontsize=8
            )
            ax_e.set_title(
                "E — Depth vs Survival\n"
                "Prediction: negative r",
                fontsize=9
            )
            try:
                r, p = stats.pearsonr(
                    sv["block_depth"].values,
                    sv["survival_months"].values
                )
                ax_e.text(
                    0.05, 0.92,
                    f"r={r:.3f} p={p:.2e}",
                    transform=ax_e.transAxes,
                    fontsize=8
                )
            except Exception:
                pass

    # F — Epigenetic genes
    ax_f = fig.add_subplot(gs[1, 2])
    bar_pair(ax_f,
             ["EZH2", "EED", "SUZ12",
              "KDM6A", "TET2", "DNMT3A"],
             "F — Epigenetic Regulators\n"
             "EZH2 predicted UP (gain lock)")

    # G — Acinar effectors
    ax_g = fig.add_subplot(gs[2, 0])
    bar_pair(ax_g,
             ACINAR_EFFECTORS[:8],
             "G — Acinar Effector Genes\n"
             "All predicted suppressed")

    # H — GATA6 subtype scatter
    ax_h = fig.add_subplot(gs[2, 1])
    if ("GATA6" in gene_cols and
            "block_depth" in tumor.columns):
        ax_h.scatter(
            tumor["GATA6"],
            tumor["block_depth"],
            alpha=0.4, s=20,
            color=clr["TUMOR"]
        )
        ax_h.set_xlabel("GATA6 (Classical marker)",
                         fontsize=8)
        ax_h.set_ylabel("Block Depth Score",
                         fontsize=8)
        ax_h.set_title(
            "H — GATA6 vs Depth\n"
            "Classical low depth / Basal high",
            fontsize=9
        )
        try:
            r, p = stats.pearsonr(
                tumor["GATA6"].values,
                tumor["block_depth"].values
            )
            ax_h.text(
                0.05, 0.92,
                f"r={r:.3f} p={p:.2e}",
                transform=ax_h.transAxes,
                fontsize=8
            )
        except Exception:
            pass

    # I — Summary
    ax_i = fig.add_subplot(gs[2, 2])
    ax_i.axis("off")

    conf_sw = (results_df[
        results_df["result"] == "CONFIRMED"
    ]["gene"].tolist()
    if len(results_df) > 0 else [])
    conf_fa = (results_df[
        results_df["result"] == "FA CONFIRMED"
    ]["gene"].tolist()
    if len(results_df) > 0 else [])

    summary = (
        "I — SUMMARY\n"
        "────────────────────────────\n"
        "Dataset: GSE183795\n"
        "  139 PAAD | 105 Normal\n"
        "  Adjacent non-tumor pancreas\n\n"
        "LINEAGE: Acinar → Ductal/Mesen\n"
        "Block: Acinar identity lost\n"
        "       Ductal program retained\n\n"
        f"Switch confirmed:\n"
        f"  {', '.join(conf_sw[:4]) if conf_sw else 'see data'}\n\n"
        f"FA confirmed:\n"
        f"  {', '.join(conf_fa[:4]) if conf_fa else 'see data'}\n\n"
        "Drug predictions:\n"
        "  1. EZH2 inhibitor\n"
        "  2. PTF1A restoration / HMA\n"
        "  3. BET / MYC inhibitor\n"
        "  4. Depth → survival biomarker\n\n"
        "Framework: OrganismCore\n"
        "Doc: 87a\n"
        "Status: PENDING RUN"
    )
    ax_i.text(
        0.03, 0.97, summary,
        transform=ax_i.transAxes,
        fontsize=8.5, verticalalignment="top",
        fontfamily="monospace",
        bbox=dict(boxstyle="round",
                  facecolor="#f8f8f8",
                  edgecolor="#cccccc")
    )

    outpath = os.path.join(
        RESULTS_DIR,
        "paad_false_attractor.png"
    )
    plt.savefig(outpath, dpi=150,
                bbox_inches="tight")
    log(f"\n  Figure saved: {outpath}")
    plt.close()

# ============================================================
# MAIN
# ============================================================

def main():
    log("=" * 70)
    log("PANCREATIC DUCTAL ADENOCARCINOMA")
    log("FALSE ATTRACTOR ANALYSIS — SCRIPT 1")
    log("Dataset: GSE183795")
    log("Framework: OrganismCore Principles-First")
    log("Doc: 87a | Date: 2026-03-01")
    log("=" * 70)
    log("")
    log("  GEO accession : GSE183795")
    log("  Tumor samples : 139 PAAD")
    log("  Normal samples: 105 adjacent non-tumor")
    log("  Platform      : Affymetrix HuGene-1.0-ST")
    log("  Survival data : YES")
    log("  Stage data    : YES")
    log("")
    log("  PREDICTIONS LOCKED BEFORE DATA:")
    log("  Switch: PTF1A/NR5A2/RBPJL/"
        "BHLHA15/CPA1/PRSS1 suppressed")
    log("  FA:     KRT19/SOX9/MUC1/EPCAM elevated")
    log("  EZH2:   ELEVATED (gain lock)")
    log("  MYC:    ELEVATED (KRAS driven)")
    log("  Survival: depth r < 0 with OS")
    log("  Subtype: GATA6 stratifies depth")
    log("")

    log("\n=== STEP 0: DATA ACQUISITION ===")
    paths = download_all()

    log("\n=== STEP 1: METADATA ===")
    meta = fetch_metadata()

    log("\n=== STEP 2: LOAD MATRIX ===")
    expr = load_matrix(paths["matrix"])

    log("\n=== STEP 3: MERGE AND CLASSIFY ===")
    merged = merge_with_meta(expr, meta)

    log("\n=== STEP 4: SADDLE POINT ANALYSIS ===")
    results_df, tumor, normal = \
        saddle_point_analysis(merged)

    log("\n=== STEP 5: DEPTH SCORING ===")
    tumor, corrs = depth_scoring(
        merged, tumor, normal, results_df
    )

    log("\n=== STEP 6: SURVIVAL ANALYSIS ===")
    surv_data = survival_analysis(tumor)

    log("\n=== STEP 7: SUBTYPE ANALYSIS ===")
    subtype_analysis(tumor)

    log("\n=== STEP 8: DRUG TARGET DERIVATION ===")
    drug_target_derivation(
        normal, tumor, results_df
    )

    log("\n=== STEP 9: FIGURE ===")
    generate_figure(
        merged, tumor, normal,
        results_df, surv_data
    )

    write_log()
    log(f"\n  Log: {LOG_FILE}")
    log(f"  All outputs: {RESULTS_DIR}")
    log("\n=== SCRIPT 1 COMPLETE ===")


if __name__ == "__main__":
    main()
