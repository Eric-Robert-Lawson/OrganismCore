"""
Myelodysplastic Syndrome — False Attractor Analysis
SCRIPT 2 — CORRECTED ATTRACTOR FRAMEWORK
Built from Script 1 findings. Not a replacement —
an iteration. Script 1 is preserved as-is.

WHAT SCRIPT 1 FOUND (unexpectedly):
  ELANE: -42.8%  r=-0.768  p=3.84e-17  TRUE switch gene
  CD34:  +12.1%  r=+0.696  p=4.03e-13  TRUE FA marker
  CEBPE: +135.3% p=0.029               UNEXPECTED — elevated
  EZH2:  -26.2%  p=7.3e-4              UNEXPECTED — suppressed
  KLF4:  +15.8%  ns                    UNEXPECTED — elevated not suppressed

WHAT THIS MEANS:
  MDS block is at EFFECTOR level (ELANE) not TF level (SPI1/IRF8)
  CEBPE is elevated but ELANE is suppressed
  The CEBPE → ELANE connection is broken
  Something between CEBPE and ELANE is blocking execution

SCRIPT 2 PREDICTIONS — STATED BEFORE RUNNING:
  1. GFI1 elevated in MDS
     GFI1 represses ELANE in early progenitors
     Must be downregulated for ELANE to activate
     If GFI1 is retained/elevated in MDS HSPCs
     it explains CEBPE present but ELANE absent
  2. GATA2 elevated in MDS
     GATA2 is HSPC master TF — must fall for
     granulocyte commitment
     CD34 retention from Script 1 suggests
     HSPC identity is retained → GATA2 should be up
  3. KDM1A (LSD1) dysregulated
     LSD1 is required for granulopoiesis
     LSD1 inhibitors are in clinical use for AML
     LSD1 works at the GFI1/ELANE axis specifically
  4. CEBPB elevated (inflammatory GMP state)
     MDS is inflammatory — CEBPB drives
     monocytic/inflammatory program not granulocytic
  5. Revised depth score (ELANE + CD34 axis only)
     stratifies patients better than Script 1 score
  6. SF3B1_MUT has different GFI1/GATA2 profile
     from WT — explaining shallower depth in Script 1

Dataset: GSE114922 (same as Script 1)
  109 MDS patients, 22 healthy controls
  CD34+ HSPCs, bone marrow bulk RNA-seq

Author: Eric Robert Lawson
Framework: OrganismCore Universal Reasoning Substrate
Date: 2026-03-01
Doc: 86b
"""

import os
import sys
import gzip
import urllib.request
import io
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

BASE_DIR     = "./mds_false_attractor/"
RESULTS_DIR  = os.path.join(BASE_DIR, "results_s2")
LOG_FILE     = os.path.join(RESULTS_DIR,
                            "analysis_log_s2.txt")
S1_RESULTS   = os.path.join(BASE_DIR,
                            "results",
                            "saddle_results.csv")

os.makedirs(BASE_DIR,    exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

GEO_BASE = ("https://ftp.ncbi.nlm.nih.gov/geo/series/"
            "GSE114nnn/GSE114922/suppl/")
CPM_FILE = "GSE114922_CPM_table.txt.gz"
META_URL = ("https://www.ncbi.nlm.nih.gov/geo/query/"
            "acc.cgi?acc=GSE114922&targ=gsm"
            "&form=text&view=full")

# ============================================================
# GENE PANELS — CORRECTED FROM SCRIPT 1 FINDINGS
# Stated before running Script 2
# ============================================================

# CONFIRMED FROM SCRIPT 1 — the real MDS axis
S1_CONFIRMED = {
    "ELANE": "switch_confirmed",   # r=-0.768
    "CD34":  "fa_confirmed",       # r=+0.696
    "CEBPE": "unexpected_elevated",# +135%
    "EZH2":  "unexpected_suppressed",
    "ASXL1": "unexpected_suppressed",
    "MYC":   "elevated",
    "ZRSR2": "elevated",
}

# NEW PREDICTIONS — the CEBPE → ELANE gap
# GFI1 represses ELANE — must fall for granulopoiesis
CEBPE_ELANE_GAP = ["GFI1", "GFI1B", "RCOR1"]

# LSD1 complex — chromatin at effector loci
LSD1_COMPLEX = ["KDM1A",   # LSD1 itself
                "HDAC1",   # CoREST complex
                "HDAC2",   # CoREST complex
                "RCOR1"]   # CoREST scaffold

# HSPC identity — should fall for granulocyte commitment
HSPC_IDENTITY = ["GATA2",  # HSPC master TF
                 "HOXA9",  # stem program
                 "MEIS1",  # stem program (Script 1)
                 "FLT3",   # progenitor receptor
                 "CD34"]   # HSPC surface marker

# INFLAMMATORY GMP — alternative fate
INFLAMMATORY = ["CEBPB",  # inflammatory CEBP
                "CEBPD",  # stress response CEBP
                "IRF1",   # inflammatory TF
                "STAT3"]  # JAK/STAT — MDS pathway

# GRANULOCYTE COMPLETION — the target state
GRANULOCYTE_PROGRAM = ["ELANE",   # neutrophil elastase
                       "MPO",     # myeloperoxidase
                       "PRTN3",   # proteinase 3
                       "AZU1",    # azurocidin
                       "CTSG",    # cathepsin G
                       "CEBPE",   # granulocyte CEBP
                       "CEBPA"]   # myeloid scaffold

# SPLICING — confirmed MDS-specific
SPLICING = ["SF3B1", "SRSF2", "U2AF1", "ZRSR2"]

ALL_TARGET_S2 = list(dict.fromkeys(
    list(S1_CONFIRMED.keys()) +
    CEBPE_ELANE_GAP +
    LSD1_COMPLEX +
    HSPC_IDENTITY +
    INFLAMMATORY +
    GRANULOCYTE_PROGRAM +
    SPLICING
))

# ============================================================
# ENSEMBL → GENE SYMBOL MAP
# Extended from Script 1
# ============================================================

ENSEMBL_MAP = {
    # Script 1 confirmed
    "ENSG00000197561": "ELANE",
    "ENSG00000174059": "CD34",
    "ENSG00000146700": "CEBPE",
    "ENSG00000106462": "EZH2",
    "ENSG00000171456": "ASXL1",
    "ENSG00000136997": "MYC",
    "ENSG00000169241": "ZRSR2",
    "ENSG00000066336": "SPI1",
    "ENSG00000101361": "KLF4",
    "ENSG00000140968": "IRF8",
    "ENSG00000245848": "CEBPA",
    "ENSG00000168769": "TET2",
    "ENSG00000119772": "DNMT3A",
    "ENSG00000115524": "SF3B1",
    "ENSG00000161547": "SRSF2",
    "ENSG00000160201": "U2AF1",
    "ENSG00000148773": "MKI67",
    # CEBPE → ELANE gap
    "ENSG00000162949": "GFI1",
    "ENSG00000165702": "GFI1B",
    "ENSG00000122877": "RCOR1",
    # LSD1 complex
    "ENSG00000004487": "KDM1A",
    "ENSG00000116478": "HDAC1",
    "ENSG00000196591": "HDAC2",
    # HSPC identity
    "ENSG00000179348": "GATA2",
    "ENSG00000078399": "HOXA9",
    "ENSG00000130755": "MEIS1",
    "ENSG00000122025": "FLT3",
    # Inflammatory GMP
    "ENSG00000242685": "CEBPB",
    "ENSG00000108839": "CEBPD",
    "ENSG00000125347": "IRF1",
    "ENSG00000168610": "STAT3",
    # Granulocyte completion
    "ENSG00000267534": "MPO",
    "ENSG00000197253": "PRTN3",
    "ENSG00000117697": "AZU1",
    "ENSG00000100448": "CTSG",
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

# ============================================================
# STEP 0: DATA — reuse Script 1 downloads
# ============================================================

def acquire_data():
    log("=" * 65)
    log("STEP 0: DATA ACQUISITION")
    log("Reusing Script 1 downloads where possible")
    log("=" * 65)

    local = os.path.join(BASE_DIR, CPM_FILE)

    if os.path.exists(local):
        size_mb = os.path.getsize(local) / 1e6
        if size_mb > 0.1:
            log(f"  Found: {CPM_FILE} ({size_mb:.1f} MB)"
                f" — skipping download")
            return local

    log(f"  Downloading: {CPM_FILE}")
    url = GEO_BASE + CPM_FILE

    def reporthook(count, block_size, total_size):
        if total_size > 0:
            pct = min(count * block_size
                      / total_size * 100, 100)
            mb  = count * block_size / 1e6
            sys.stdout.write(
                f"\r  {mb:.1f} MB ({pct:.1f}%)"
            )
            sys.stdout.flush()

    urllib.request.urlretrieve(url, local, reporthook)
    print()
    log(f"  Complete: {local}")
    return local

# ============================================================
# STEP 1: METADATA — reuse Script 1 cache
# ============================================================

def fetch_metadata():
    log("")
    log("--- Sample metadata ---")

    # Reuse Script 1 cache if present
    cache = os.path.join(BASE_DIR,
                         "results", "metadata.csv")
    if os.path.exists(cache):
        df = pd.read_csv(cache, index_col=0)
        log(f"  Loaded from Script 1 cache: "
            f"{len(df)} samples")
        return df

    # Fallback: fetch fresh
    log("  Script 1 cache not found — fetching...")
    req = urllib.request.Request(
        META_URL, headers={"User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(req, timeout=30) as r:
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
                "!Sample_characteristics_ch1"):
            val = line.split("=", 1)[1].strip()
            if ":" in val:
                k, v = val.split(":", 1)
                key = (k.strip().lower()
                       .replace(" ", "_"))
                current[key] = v.strip()
    if current:
        samples.append(current)

    df = pd.DataFrame(samples)
    if "patient_id" not in df.columns:
        extracted = df["title"].str.extract(
            r"(A\d+)", expand=False
        )
        df["patient_id"] = np.where(
            extracted.notna(), extracted, df["title"]
        )

    os.makedirs(os.path.join(BASE_DIR, "results"),
                exist_ok=True)
    df.to_csv(cache)
    log(f"  Fetched and cached: {len(df)} samples")
    return df

# ============================================================
# STEP 2: LOAD CPM — extended gene panel
# ============================================================

def load_cpm(path):
    log(f"\n  Loading: {os.path.basename(path)}")

    with gzip.open(path, "rt") as f:
        df = pd.read_csv(f, sep="\t", index_col=0)

    log(f"  Raw: {df.shape[0]} genes x "
        f"{df.shape[1]} samples")

    df.index = df.index.map(
        lambda x: ENSEMBL_MAP.get(x, x)
    )

    found   = [g for g in ALL_TARGET_S2
               if g in df.index]
    missing = [g for g in ALL_TARGET_S2
               if g not in df.index]
    log(f"  Target genes found  : "
        f"{len(found)}/{len(ALL_TARGET_S2)}")
    if missing:
        log(f"  Missing: {missing}")

    df = df.loc[found]
    df = df.T
    df.index.name = "patient_id"

    extracted = df.index.str.extract(
        r"(A\d+)", expand=False
    )
    new_index = [
        extracted[i]
        if pd.notna(extracted[i])
        else df.index[i]
        for i in range(len(df.index))
    ]
    df.index = pd.Index(new_index, name="patient_id")

    log(f"  Final: {df.shape}")
    return df

# ============================================================
# STEP 3: MERGE AND CLASSIFY
# ============================================================

def merge_with_meta(expr, meta):
    log("\n  Merging with metadata...")

    meta = meta.copy()
    meta["patient_id"] = (
        meta["patient_id"].astype(str).str.strip()
    )

    meta_cols = [c for c in [
        "disease_status",
        "sf3b1_mutational_status",
        "srsf2_mutational_status",
        "u2af1_mutational_status",
        "zrsr2_mutational_status",
    ] if c in meta.columns]

    merged = expr.join(
        meta.set_index("patient_id")[meta_cols],
        how="left"
    )

    if "disease_status" in merged.columns:
        ds = merged["disease_status"].str.lower()
    else:
        ds = pd.Series("unknown", index=merged.index)

    merged["group"] = "UNKNOWN"
    merged.loc[
        ds.str.contains("healthy|normal|control",
                        na=False), "group"
    ] = "NORMAL"
    merged.loc[
        ds.str.contains("myelodysplastic|mds",
                        na=False), "group"
    ] = "MDS"

    log(f"  NORMAL: {(merged['group']=='NORMAL').sum()}"
        f"  MDS: {(merged['group']=='MDS').sum()}"
        f"  UNKNOWN: {(merged['group']=='UNKNOWN').sum()}")

    return merged

# ============================================================
# STEP 4: TEST THE CEBPE → ELANE GAP
# Core hypothesis of Script 2
# ============================================================

def test_cebpe_elane_gap(merged):
    log("")
    log("=" * 70)
    log("STEP 4: THE CEBPE → ELANE GAP")
    log("Core hypothesis of Script 2")
    log("CEBPE is elevated but ELANE is suppressed")
    log("What sits between them?")
    log("=" * 70)

    normal = merged[merged["group"] == "NORMAL"]
    mds    = merged[merged["group"] == "MDS"]

    log(f"\n  Normal: {len(normal)}  "
        f"MDS: {len(mds)}")

    # The gap genes
    gap_genes = (CEBPE_ELANE_GAP +
                 GRANULOCYTE_PROGRAM +
                 LSD1_COMPLEX)

    role_map = {}
    for g in CEBPE_ELANE_GAP:
        role_map[g] = "GAP"
    for g in GRANULOCYTE_PROGRAM:
        role_map[g] = "GRANULO"
    for g in LSD1_COMPLEX:
        role_map[g] = "LSD1"

    log(f"\n  {'Gene':<10} {'Role':<10} "
        f"{'Normal':>9} {'MDS':>9} "
        f"{'Change':>9} {'p-value':>16}  "
        f"S2 Prediction")
    log(f"  {'-'*82}")

    results = []
    gene_cols = [c for c in merged.columns
                 if c in ALL_TARGET_S2]

    predictions = {
        "GFI1":  ("elevated", "GFI1 blocks ELANE"),
        "GFI1B": ("elevated", "GFI1 paralog"),
        "RCOR1": ("elevated", "CoREST/LSD1 cofactor"),
        "KDM1A": ("dysregulated", "LSD1"),
        "HDAC1": ("dysregulated", "CoREST complex"),
        "HDAC2": ("dysregulated", "CoREST complex"),
        "ELANE": ("suppressed", "confirmed Script 1"),
        "MPO":   ("suppressed", "granulocyte effector"),
        "PRTN3": ("suppressed", "granulocyte effector"),
        "AZU1":  ("suppressed", "granulocyte effector"),
        "CTSG":  ("suppressed", "granulocyte effector"),
        "CEBPE": ("elevated", "confirmed Script 1"),
        "CEBPA": ("suppressed", "myeloid scaffold"),
    }

    def fmt_p(p):
        if p < 1e-300:  return "p=0.00e+00 ***"
        elif p < 0.001: return f"p={p:.2e} ***"
        elif p < 0.01:  return f"p={p:.2e}  **"
        elif p < 0.05:  return f"p={p:.4f}   *"
        else:           return f"p={p:.4f}  ns"

    for gene in gap_genes:
        if gene not in gene_cols:
            log(f"  {gene:<10} {'---':<10} "
                f"{'not in matrix':>40}")
            continue

        nd_v = normal[gene].dropna().values
        md_v = mds[gene].dropna().values

        if len(nd_v) < 2 or len(md_v) < 2:
            continue

        nd_m = nd_v.mean()
        md_m = md_v.mean()
        chg  = ((md_m - nd_m) / nd_m * 100
                if nd_m > 0.0001 else np.nan)

        _, p_supp = stats.mannwhitneyu(
            nd_v, md_v, alternative="greater"
        )
        _, p_elev = stats.mannwhitneyu(
            md_v, nd_v, alternative="greater"
        )
        p_use = min(p_supp, p_elev)
        role  = role_map.get(gene, "OTHER")
        pred  = predictions.get(gene, ("?", ""))[0]
        note  = predictions.get(gene, ("?", ""))[1]

        # Assess vs prediction
        if pred == "elevated":
            if p_elev < 0.05 and (chg or 0) > 0:
                assess = "CONFIRMED"
            elif (chg or 0) > 10:
                assess = "TREND"
            else:
                assess = "NOT CONFIRMED"
        elif pred == "suppressed":
            if p_supp < 0.05 and (chg or 0) < 0:
                assess = "CONFIRMED"
            elif (chg or 0) < -10:
                assess = "TREND"
            else:
                assess = "NOT CONFIRMED"
        else:
            assess = "SEE DATA"

        chg_str = (f"{chg:+.1f}%"
                   if not np.isnan(chg) else "  N/A")
        log(f"  {gene:<10} {role:<10} "
            f"{nd_m:>9.4f} {md_m:>9.4f} "
            f"{chg_str:>9}  {fmt_p(p_use):>16}  "
            f"{assess} — {note}")

        results.append({
            "gene":        gene,
            "role":        role,
            "normal_mean": nd_m,
            "mds_mean":    md_m,
            "change_pct":  chg,
            "p_value":     p_use,
            "prediction":  pred,
            "assessment":  assess,
        })

    rdf = pd.DataFrame(results)
    rdf.to_csv(
        os.path.join(RESULTS_DIR,
                     "gap_results_s2.csv"),
        index=False
    )
    return rdf, normal, mds

# ============================================================
# STEP 5: FULL SADDLE POINT — ALL S2 GENES
# ============================================================

def full_saddle_s2(merged, normal, mds):
    log("")
    log("=" * 70)
    log("STEP 5: FULL SADDLE POINT — ALL S2 GENES")
    log("=" * 70)

    gene_cols = [c for c in merged.columns
                 if c in ALL_TARGET_S2]

    def fmt_p(p):
        if p < 1e-300:  return "p=0.00e+00 ***"
        elif p < 0.001: return f"p={p:.2e} ***"
        elif p < 0.01:  return f"p={p:.2e}  **"
        elif p < 0.05:  return f"p={p:.4f}   *"
        else:           return f"p={p:.4f}  ns"

    panel_map = {}
    for g in CEBPE_ELANE_GAP:    panel_map[g] = "GAP"
    for g in LSD1_COMPLEX:       panel_map[g] = "LSD1"
    for g in HSPC_IDENTITY:      panel_map[g] = "HSPC_ID"
    for g in INFLAMMATORY:       panel_map[g] = "INFLAM"
    for g in GRANULOCYTE_PROGRAM:panel_map[g] = "GRANULO"
    for g in SPLICING:           panel_map[g] = "SPLICE"
    for g in S1_CONFIRMED:       panel_map[g] = "S1_CONF"

    log(f"\n  {'Gene':<10} {'Panel':<10} "
        f"{'Normal':>9} {'MDS':>9} "
        f"{'Change':>9} {'p-value':>16}")
    log(f"  {'-'*70}")

    all_results = []
    for gene in ALL_TARGET_S2:
        if gene not in gene_cols:
            continue
        nd_v = normal[gene].dropna().values
        md_v = mds[gene].dropna().values
        if len(nd_v) < 2 or len(md_v) < 2:
            continue

        nd_m = nd_v.mean()
        md_m = md_v.mean()
        chg  = ((md_m - nd_m) / nd_m * 100
                if nd_m > 0.0001 else np.nan)

        _, p_s = stats.mannwhitneyu(
            nd_v, md_v, alternative="greater"
        )
        _, p_e = stats.mannwhitneyu(
            md_v, nd_v, alternative="greater"
        )
        p_use = min(p_s, p_e)
        panel = panel_map.get(gene, "OTHER")

        chg_str = (f"{chg:+.1f}%"
                   if not np.isnan(chg) else " N/A")
        log(f"  {gene:<10} {panel:<10} "
            f"{nd_m:>9.4f} {md_m:>9.4f} "
            f"{chg_str:>9}  {fmt_p(p_use):>16}")

        all_results.append({
            "gene": gene, "panel": panel,
            "normal_mean": nd_m, "mds_mean": md_m,
            "change_pct": chg, "p_value": p_use,
        })

    adf = pd.DataFrame(all_results)
    adf.to_csv(
        os.path.join(RESULTS_DIR,
                     "all_genes_s2.csv"),
        index=False
    )
    return adf

# ============================================================
# STEP 6: REVISED DEPTH SCORE
# Script 1: SW suppression + FA elevation (AML genes)
# Script 2: ELANE suppression + CD34 elevation (correct axis)
# Compare — does S2 score stratify better?
# ============================================================

def revised_depth_score(merged, normal, mds,
                        all_results_df):
    log("")
    log("=" * 70)
    log("STEP 6: REVISED DEPTH SCORE")
    log("S1 score: AML gene panel")
    log("S2 score: ELANE suppression + CD34 elevation")
    log("Compare stratification")
    log("=" * 70)

    gene_cols = [c for c in merged.columns
                 if c in ALL_TARGET_S2]
    mds = mds.copy()

    def norm01(s):
        mn, mx = s.min(), s.max()
        return ((s - mn) / (mx - mn)
                if mx > mn
                else pd.Series(0.0, index=s.index))

    # S2 depth: ELANE suppression + CD34 elevation
    depth_s2 = pd.Series(
        np.zeros(len(mds)), index=mds.index
    )
    components = 0

    if "ELANE" in gene_cols:
        elane_norm = norm01(mds["ELANE"])
        depth_s2  += (1 - elane_norm)
        components += 1
        log("  Component 1: ELANE suppression "
            "(1 - norm(ELANE))")

    if "CD34" in gene_cols:
        cd34_norm  = norm01(mds["CD34"])
        depth_s2  += cd34_norm
        components += 1
        log("  Component 2: CD34 elevation "
            "(norm(CD34))")

    if components > 0:
        depth_s2 /= components

    mds["depth_s2"] = depth_s2.values

    log(f"\n  S2 Depth statistics ({len(mds)} MDS):")
    log(f"    Mean   : {depth_s2.mean():.4f}")
    log(f"    Median : {depth_s2.median():.4f}")
    log(f"    Std    : {depth_s2.std():.4f}")
    log(f"    Min    : {depth_s2.min():.4f}")
    log(f"    Max    : {depth_s2.max():.4f}")

    # Depth by mutation subtype — S2 score
    log("\n  S2 Block depth by mutation subtype:")
    subtype_depth = {}
    for col, label in [
        ("sf3b1_mutational_status", "SF3B1"),
        ("srsf2_mutational_status", "SRSF2"),
        ("u2af1_mutational_status", "U2AF1"),
    ]:
        if col in mds.columns:
            mut = mds[mds[col] == "MUT"]["depth_s2"]
            wt  = mds[mds[col] == "WT"]["depth_s2"]
            if len(mut) > 2 and len(wt) > 2:
                _, p = stats.mannwhitneyu(
                    mut, wt, alternative="two-sided"
                )
                log(f"    {label}_MUT (n={len(mut):3d}): "
                    f"{mut.mean():.4f}  vs  "
                    f"WT (n={len(wt):3d}): "
                    f"{wt.mean():.4f}  p={p:.4f}")
                subtype_depth[label] = {
                    "MUT": mut, "WT": wt, "p": p
                }

    # S2 depth correlations
    log("\n  S2 depth correlations (all S2 genes):")
    corrs = []
    for gene in gene_cols:
        try:
            r, p = stats.pearsonr(
                mds["depth_s2"].values,
                mds[gene].values
            )
            corrs.append((gene, r, p))
        except Exception:
            pass
    corrs.sort(key=lambda x: abs(x[1]), reverse=True)
    log(f"  {'Gene':<10} {'r':>8}  p-value")
    log(f"  {'-'*34}")
    for gene, r, p in corrs[:15]:
        log(f"  {gene:<10} {r:>+8.4f}  p={p:.2e}")

    return mds, subtype_depth

# ============================================================
# STEP 7: HSPC IDENTITY AND INFLAMMATORY GMP
# ============================================================

def hspc_and_inflammatory(merged, normal, mds):
    log("")
    log("=" * 70)
    log("STEP 7: HSPC IDENTITY vs INFLAMMATORY GMP")
    log("Prediction: GATA2 elevated (retained HSPC ID)")
    log("Prediction: CEBPB elevated (inflammatory state)")
    log("=" * 70)

    gene_cols = [c for c in merged.columns
                 if c in ALL_TARGET_S2]

    def fmt_p(p):
        if p < 1e-300:  return "p=0.00e+00 ***"
        elif p < 0.001: return f"p={p:.2e} ***"
        elif p < 0.01:  return f"p={p:.2e}  **"
        elif p < 0.05:  return f"p={p:.4f}   *"
        else:           return f"p={p:.4f}  ns"

    log(f"\n  HSPC IDENTITY GENES:")
    log(f"  {'Gene':<10} {'Normal':>9} {'MDS':>9} "
        f"{'Change':>9} {'p-value':>16}  Prediction")
    log(f"  {'-'*70}")

    preds = {
        "GATA2": "elevated",
        "HOXA9": "elevated",
        "MEIS1": "elevated",
        "FLT3":  "elevated",
        "CD34":  "elevated",
    }

    for gene in HSPC_IDENTITY:
        if gene not in gene_cols:
            log(f"  {gene:<10} not in matrix")
            continue
        nd_m = normal[gene].mean()
        md_m = mds[gene].mean()
        chg  = ((md_m - nd_m) / nd_m * 100
                if nd_m > 0.0001 else np.nan)
        _, p_e = stats.mannwhitneyu(
            mds[gene].dropna().values,
            normal[gene].dropna().values,
            alternative="greater"
        )
        pred = preds.get(gene, "?")
        conf = ("✓" if p_e < 0.05
                    and (chg or 0) > 0
                else "✗" if (chg or 0) < 0
                else "~")
        chg_str = (f"{chg:+.1f}%"
                   if not np.isnan(chg) else " N/A")
        log(f"  {gene:<10} {nd_m:>9.4f} {md_m:>9.4f} "
            f"{chg_str:>9}  {fmt_p(p_e):>16}  "
            f"{conf} predicted {pred}")

    log(f"\n  INFLAMMATORY GMP GENES:")
    log(f"  {'Gene':<10} {'Normal':>9} {'MDS':>9} "
        f"{'Change':>9} {'p-value':>16}  Prediction")
    log(f"  {'-'*70}")

    inflam_preds = {
        "CEBPB": "elevated",
        "CEBPD": "elevated",
        "IRF1":  "elevated",
        "STAT3": "elevated",
    }

    for gene in INFLAMMATORY:
        if gene not in gene_cols:
            log(f"  {gene:<10} not in matrix")
            continue
        nd_m = normal[gene].mean()
        md_m = mds[gene].mean()
        chg  = ((md_m - nd_m) / nd_m * 100
                if nd_m > 0.0001 else np.nan)
        _, p_e = stats.mannwhitneyu(
            mds[gene].dropna().values,
            normal[gene].dropna().values,
            alternative="greater"
        )
        pred = inflam_preds.get(gene, "?")
        conf = ("✓" if p_e < 0.05
                    and (chg or 0) > 0
                else "✗" if (chg or 0) < 0
                else "~")
        chg_str = (f"{chg:+.1f}%"
                   if not np.isnan(chg) else " N/A")
        log(f"  {gene:<10} {nd_m:>9.4f} {md_m:>9.4f} "
            f"{chg_str:>9}  {fmt_p(p_e):>16}  "
            f"{conf} predicted {pred}")

# ============================================================
# STEP 8: GFI1 DEPTH CORRELATION
# Is GFI1 elevation the mechanism of ELANE suppression?
# ============================================================

def gfi1_depth_analysis(mds):
    log("")
    log("=" * 70)
    log("STEP 8: GFI1 ANALYSIS")
    log("Is GFI1 the block between CEBPE and ELANE?")
    log("Prediction: GFI1 elevated AND correlates "
        "with ELANE suppression")
    log("=" * 70)

    gene_cols = [c for c in mds.columns
                 if c in ALL_TARGET_S2]

    if "GFI1" not in gene_cols or \
            "ELANE" not in gene_cols:
        log("  GFI1 or ELANE not in matrix — skip")
        return

    # GFI1 vs ELANE correlation
    r, p = stats.pearsonr(
        mds["GFI1"].values,
        mds["ELANE"].values
    )
    log(f"\n  GFI1 vs ELANE correlation:")
    log(f"    r = {r:+.4f}  p = {p:.2e}")
    log(f"    Prediction: negative (GFI1 represses ELANE)")
    log(f"    Result: {'CONFIRMED' if r < -0.2 and p < 0.05 else 'NOT CONFIRMED'}")

    # GFI1 vs depth_s2
    if "depth_s2" in mds.columns:
        r2, p2 = stats.pearsonr(
            mds["depth_s2"].values,
            mds["GFI1"].values
        )
        log(f"\n  GFI1 vs S2 depth:")
        log(f"    r = {r2:+.4f}  p = {p2:.2e}")
        log(f"    Prediction: positive "
            f"(higher GFI1 = deeper block)")
        log(f"    Result: "
            f"{'CONFIRMED' if r2 > 0.2 and p2 < 0.05 else 'NOT CONFIRMED'}")

    # CEBPE vs GFI1
    if "CEBPE" in gene_cols:
        r3, p3 = stats.pearsonr(
            mds["CEBPE"].values,
            mds["GFI1"].values
        )
        log(f"\n  CEBPE vs GFI1:")
        log(f"    r = {r3:+.4f}  p = {p3:.2e}")
        log(f"    Positive = both elevated together")
        log(f"    Negative = opposing programs")

    # CEBPE vs ELANE
    if "CEBPE" in gene_cols:
        r4, p4 = stats.pearsonr(
            mds["CEBPE"].values,
            mds["ELANE"].values
        )
        log(f"\n  CEBPE vs ELANE:")
        log(f"    r = {r4:+.4f}  p = {p4:.2e}")
        log(f"    Normal granulopoiesis: positive")
        log(f"    MDS if connection broken: ~0 or negative")
        log(f"    Result: "
            f"{'DISCONNECTED' if abs(r4) < 0.2 else 'CONNECTED' if r4 > 0.2 else 'INVERTED'}")

# ============================================================
# STEP 9: COMPARE S1 vs S2 DEPTH SCORES
# ============================================================

def compare_depth_scores(merged, mds):
    log("")
    log("=" * 70)
    log("STEP 9: S1 vs S2 DEPTH SCORE COMPARISON")
    log("Does the corrected score stratify better?")
    log("=" * 70)

    s1_path = os.path.join(BASE_DIR,
                           "results",
                           "saddle_results.csv")

    # Recompute S1 depth from merged data
    gene_cols = [c for c in merged.columns
                 if c in ALL_TARGET_S2]
    mds_full  = merged[merged["group"] == "MDS"].copy()

    s1_sw = ["SPI1", "KLF4", "IRF8",
             "CEBPA", "CEBPE", "ELANE"]
    s1_fa = ["CD34", "HOXA9", "MEIS1", "FLT3", "MPO"]

    def norm01(s):
        mn, mx = s.min(), s.max()
        return ((s - mn) / (mx - mn)
                if mx > mn
                else pd.Series(0.0, index=s.index))

    s1_sw_avail = [g for g in s1_sw if g in gene_cols]
    s1_fa_avail = [g for g in s1_fa if g in gene_cols]

    depth_s1 = pd.Series(np.zeros(len(mds_full)),
                         index=mds_full.index)
    comp = 0
    if s1_sw_avail:
        depth_s1 += (
            1 - norm01(mds_full[s1_sw_avail].mean(axis=1))
        )
        comp += 1
    if s1_fa_avail:
        depth_s1 += norm01(
            mds_full[s1_fa_avail].mean(axis=1)
        )
        comp += 1
    if comp > 0:
        depth_s1 /= comp

    depth_s2 = mds["depth_s2"].reindex(mds_full.index)

    log(f"\n  S1 score (AML gene panel):")
    log(f"    Mean={depth_s1.mean():.4f}  "
        f"Std={depth_s1.std():.4f}")
    log(f"  S2 score (ELANE + CD34 axis):")
    log(f"    Mean={depth_s2.mean():.4f}  "
        f"Std={depth_s2.std():.4f}")

    # Correlation between scores
    common = depth_s1.index.intersection(depth_s2.index)
    if len(common) > 5:
        r, p = stats.pearsonr(
            depth_s1.loc[common].values,
            depth_s2.loc[common].values
        )
        log(f"\n  S1 vs S2 correlation: "
            f"r={r:.4f}  p={p:.2e}")
        if r > 0.8:
            log("  Scores are concordant — same biology")
        elif r > 0.5:
            log("  Partial concordance — overlapping signal")
        else:
            log("  Divergent — S2 captures different axis")

    # Which score better separates SF3B1_MUT vs WT?
    if "sf3b1_mutational_status" in mds_full.columns:
        s1_mut = depth_s1[
            mds_full["sf3b1_mutational_status"] == "MUT"
        ]
        s1_wt  = depth_s1[
            mds_full["sf3b1_mutational_status"] == "WT"
        ]
        s2_mut = depth_s2[
            mds_full["sf3b1_mutational_status"] == "MUT"
        ].dropna()
        s2_wt  = depth_s2[
            mds_full["sf3b1_mutational_status"] == "WT"
        ].dropna()

        if len(s1_mut) > 2 and len(s1_wt) > 2:
            _, p_s1 = stats.mannwhitneyu(
                s1_mut, s1_wt,
                alternative="two-sided"
            )
            log(f"\n  SF3B1 MUT vs WT — S1 score: "
                f"MUT={s1_mut.mean():.4f}  "
                f"WT={s1_wt.mean():.4f}  "
                f"p={p_s1:.4f}")

        if len(s2_mut) > 2 and len(s2_wt) > 2:
            _, p_s2 = stats.mannwhitneyu(
                s2_mut, s2_wt,
                alternative="two-sided"
            )
            log(f"  SF3B1 MUT vs WT — S2 score: "
                f"MUT={s2_mut.mean():.4f}  "
                f"WT={s2_wt.mean():.4f}  "
                f"p={p_s2:.4f}")

    return depth_s1, depth_s2, mds_full

# ============================================================
# STEP 10: FIGURE
# ============================================================

def generate_figure(merged, normal, mds,
                    gap_df, all_df,
                    depth_s1, depth_s2,
                    mds_full):

    fig = plt.figure(figsize=(26, 22))
    fig.suptitle(
        "MDS False Attractor — Script 2 "
        "(Corrected Attractor Framework)\n"
        "Dataset: GSE114922 | OrganismCore "
        "2026-03-01 | Doc 86b\n"
        "Testing: CEBPE→ELANE gap | GFI1 hypothesis | "
        "LSD1 complex | Revised depth score",
        fontsize=11, fontweight="bold", y=0.99
    )
    gs = gridspec.GridSpec(
        3, 4, figure=fig, hspace=0.52, wspace=0.42
    )

    gene_cols = [c for c in merged.columns
                 if c in ALL_TARGET_S2]

    clr = {"NORMAL": "#2980b9", "MDS": "#c0392b"}

    def bar_pair(ax, genes, title, ylabel="CPM"):
        avail = [g for g in genes if g in gene_cols]
        if not avail:
            ax.text(0.5, 0.5, "No genes available",
                    ha="center", va="center",
                    transform=ax.transAxes)
            ax.set_title(title)
            return
        x = np.arange(len(avail))
        w = 0.35
        for i, (grp, df_g, c) in enumerate([
            ("Normal", normal, clr["NORMAL"]),
            ("MDS",    mds,    clr["MDS"]),
        ]):
            means = [df_g[g].mean()
                     if g in df_g.columns else 0
                     for g in avail]
            sems  = [df_g[g].sem()
                     if g in df_g.columns else 0
                     for g in avail]
            ax.bar(x + i*w - 0.5*w, means, w,
                   yerr=sems, color=c, label=grp,
                   capsize=3, alpha=0.85)
        ax.set_xticks(x)
        ax.set_xticklabels(avail,
                            rotation=45, ha="right",
                            fontsize=8)
        ax.set_ylabel(ylabel, fontsize=8)
        ax.set_title(title, fontsize=9)
        ax.legend(fontsize=7)

    # A — CEBPE→ELANE gap genes
    ax_a = fig.add_subplot(gs[0, 0])
    bar_pair(ax_a,
             ["CEBPE", "GFI1", "GFI1B", "ELANE"],
             "A — CEBPE→ELANE Gap\nGFI1 predicted elevated")

    # B — LSD1 complex
    ax_b = fig.add_subplot(gs[0, 1])
    bar_pair(ax_b,
             LSD1_COMPLEX,
             "B — LSD1 Complex\nChromatin at effector loci")

    # C — Granulocyte completion program
    ax_c = fig.add_subplot(gs[0, 2])
    bar_pair(ax_c,
             GRANULOCYTE_PROGRAM,
             "C — Granulocyte Program\n"
             "ELANE/MPO/PRTN3/AZU1/CTSG")

    # D — HSPC identity
    ax_d = fig.add_subplot(gs[0, 3])
    bar_pair(ax_d,
             HSPC_IDENTITY,
             "D — HSPC Identity\n"
             "GATA2/CD34/MEIS1/FLT3")

    # E — Inflammatory GMP
    ax_e = fig.add_subplot(gs[1, 0])
    bar_pair(ax_e,
             INFLAMMATORY,
             "E — Inflammatory GMP\n"
             "CEBPB/IRF1/STAT3 predicted up")

    # F — S2 depth distribution
    ax_f = fig.add_subplot(gs[1, 1])
    if "depth_s2" in mds.columns:
        d = mds["depth_s2"]
        ax_f.hist(d, bins=25, color="#c0392b",
                  edgecolor="white", alpha=0.85)
        ax_f.axvline(d.mean(), color="black",
                     linewidth=1.5,
                     label=f"Mean={d.mean():.3f}")
        ax_f.set_xlabel("S2 Depth Score "
                         "(ELANE+CD34 axis)",
                         fontsize=8)
        ax_f.set_ylabel("Count", fontsize=8)
        ax_f.set_title("F — S2 Block Depth\n"
                        "Corrected axis",
                        fontsize=9)
        ax_f.legend(fontsize=7)

    # G — S1 vs S2 scatter
    ax_g = fig.add_subplot(gs[1, 2])
    common = depth_s1.index.intersection(
        depth_s2.index
    )
    if len(common) > 5:
        ax_g.scatter(
            depth_s1.loc[common].values,
            depth_s2.loc[common].values,
            alpha=0.5, s=20, color="#8e44ad"
        )
        ax_g.set_xlabel("S1 Depth (AML genes)",
                         fontsize=8)
        ax_g.set_ylabel("S2 Depth (ELANE+CD34)",
                         fontsize=8)
        ax_g.set_title("G — S1 vs S2 Depth\n"
                        "Same biology?",
                        fontsize=9)
        try:
            r, _ = stats.pearsonr(
                depth_s1.loc[common].values,
                depth_s2.loc[common].values
            )
            ax_g.text(0.05, 0.92,
                       f"r = {r:.3f}",
                       transform=ax_g.transAxes,
                       fontsize=8)
        except Exception:
            pass

    # H — GFI1 vs ELANE scatter
    ax_h = fig.add_subplot(gs[1, 3])
    if ("GFI1" in mds.columns
            and "ELANE" in mds.columns):
        ax_h.scatter(mds["GFI1"], mds["ELANE"],
                      alpha=0.5, s=20,
                      color="#e67e22")
        ax_h.set_xlabel("GFI1 (CPM)", fontsize=8)
        ax_h.set_ylabel("ELANE (CPM)", fontsize=8)
        ax_h.set_title("H — GFI1 vs ELANE\n"
                        "Prediction: negative r",
                        fontsize=9)
        try:
            r, p = stats.pearsonr(
                mds["GFI1"].values,
                mds["ELANE"].values
            )
            ax_h.text(0.05, 0.92,
                       f"r={r:.3f} p={p:.2e}",
                       transform=ax_h.transAxes,
                       fontsize=8)
        except Exception:
            pass

    # I — Depth by mutation (S2 score)
    ax_i = fig.add_subplot(gs[2, 0])
    box_data, box_labels, box_colors = [], [], []
    mut_clr = {
        "SF3B1": "#8e44ad",
        "SRSF2": "#e67e22",
        "U2AF1": "#27ae60",
        "WT":    "#95a5a6",
    }
    for col, label in [
        ("sf3b1_mutational_status", "SF3B1"),
        ("srsf2_mutational_status", "SRSF2"),
        ("u2af1_mutational_status", "U2AF1"),
    ]:
        if col in mds.columns:
            mut_d = mds[
                mds[col] == "MUT"
            ]["depth_s2"].dropna()
            if len(mut_d) > 2:
                box_data.append(mut_d.values)
                box_labels.append(
                    f"{label}_MUT\nn={len(mut_d)}"
                )
                box_colors.append(
                    mut_clr.get(label, "#95a5a6")
                )
    wt_all_mask = pd.Series(True, index=mds.index)
    for col in ["sf3b1_mutational_status",
                "srsf2_mutational_status",
                "u2af1_mutational_status"]:
        if col in mds.columns:
            wt_all_mask &= (mds[col] == "WT")
    wt_d = mds[wt_all_mask]["depth_s2"].dropna()
    if len(wt_d) > 2:
        box_data.append(wt_d.values)
        box_labels.append(f"ALL_WT\nn={len(wt_d)}")
        box_colors.append(mut_clr["WT"])

    if box_data:
        bp = ax_i.boxplot(box_data,
                          patch_artist=True,
                          medianprops=dict(
                              color="black",
                              linewidth=2))
        for patch, c in zip(bp["boxes"], box_colors):
            patch.set_facecolor(c)
            patch.set_alpha(0.7)
        ax_i.set_xticklabels(box_labels, fontsize=7)
        ax_i.set_ylabel("S2 Depth Score", fontsize=8)
        ax_i.set_title("I — S2 Depth by Subtype\n"
                        "SF3B1/SRSF2/U2AF1 vs WT",
                        fontsize=9)

    # J — CEBPE vs ELANE scatter
    ax_j = fig.add_subplot(gs[2, 1])
    if ("CEBPE" in mds.columns
            and "ELANE" in mds.columns):
        ax_j.scatter(mds["CEBPE"], mds["ELANE"],
                      alpha=0.5, s=20,
                      color="#c0392b")
        ax_j.set_xlabel("CEBPE (CPM)", fontsize=8)
        ax_j.set_ylabel("ELANE (CPM)", fontsize=8)
        ax_j.set_title("J — CEBPE vs ELANE\n"
                        "Is the link broken in MDS?",
                        fontsize=9)
        try:
            r, p = stats.pearsonr(
                mds["CEBPE"].values,
                mds["ELANE"].values
            )
            ax_j.text(0.05, 0.92,
                       f"r={r:.3f} p={p:.2e}",
                       transform=ax_j.transAxes,
                       fontsize=8)
        except Exception:
            pass

    # K — Depth correlations waterfall
    ax_k = fig.add_subplot(gs[2, 2])
    if "depth_s2" in mds.columns:
        corrs = []
        for gene in gene_cols:
            try:
                r, p = stats.pearsonr(
                    mds["depth_s2"].values,
                    mds[gene].values
                )
                corrs.append((gene, r, p))
            except Exception:
                pass
        corrs.sort(key=lambda x: x[1])
        genes_c = [c[0] for c in corrs]
        vals_c  = [c[1] for c in corrs]
        colors_c = ["#c0392b" if v < 0
                    else "#27ae60"
                    for v in vals_c]
        ax_k.barh(genes_c, vals_c, color=colors_c)
        ax_k.axvline(0, color="black", linewidth=0.8)
        ax_k.set_xlabel("r with S2 depth", fontsize=8)
        ax_k.set_title("K — S2 Depth Correlations\n"
                        "All S2 genes",
                        fontsize=9)
        ax_k.tick_params(axis="y", labelsize=7)

    # L — Summary
    ax_l = fig.add_subplot(gs[2, 3])
    ax_l.axis("off")

    gfi1_conf = ("not in matrix"
                 if "GFI1" not in gene_cols
                 else "see panel H")
    gata2_conf = ("not in matrix"
                  if "GATA2" not in gene_cols
                  else "see panel D")

    summary = (
        "L — SCRIPT 2 SUMMARY\n"
        "────────────────────────────\n"
        "Framework iteration\n"
        "Built from Script 1 findings\n\n"
        "S1 found unexpectedly:\n"
        "  ELANE r=-0.768 (true switch)\n"
        "  CD34  r=+0.696 (true FA)\n"
        "  CEBPE +135% (unexpected)\n\n"
        "S2 predictions:\n"
        f"  GFI1 elevated: {gfi1_conf}\n"
        f"  GATA2 elevated: {gata2_conf}\n"
        "  CEBPE→ELANE disconnected\n"
        "  LSD1 complex dysregulated\n"
        "  CEBPB elevated (inflam)\n\n"
        "Revised depth score:\n"
        "  ELANE suppression\n"
        "  + CD34 elevation\n"
        "  (correct attractor axis)\n\n"
        "Drug targets from S2:\n"
        "  LSD1 inhibitor (KDM1A)\n"
        "  GFI1 inhibitor\n"
        "  Splicing correction\n"
        "  ELANE restoration\n\n"
        "Framework: OrganismCore\n"
        "Doc: 86b\n"
        "Status: COMPLETE"
    )
    ax_l.text(
        0.03, 0.97, summary,
        transform=ax_l.transAxes,
        fontsize=8, verticalalignment="top",
        fontfamily="monospace",
        bbox=dict(boxstyle="round",
                  facecolor="#f8f8f8",
                  edgecolor="#cccccc")
    )

    outpath = os.path.join(
        RESULTS_DIR, "mds_false_attractor_s2.png"
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
    log("MDS FALSE ATTRACTOR — SCRIPT 2")
    log("CORRECTED ATTRACTOR FRAMEWORK")
    log("Built from Script 1 findings")
    log("Doc: 86b | Date: 2026-03-01")
    log("=" * 70)
    log("")
    log("  Script 1 wrong predictions:")
    log("    SPI1/KLF4/IRF8 as switch genes — "
        "not confirmed")
    log("    HOXA9/MEIS1/FLT3 as FA markers — "
        "not confirmed")
    log("")
    log("  Script 1 unexpected findings:")
    log("    ELANE: -42.8%  r=-0.768  TRUE switch gene")
    log("    CD34:  +12.1%  r=+0.696  TRUE FA marker")
    log("    CEBPE: +135.3%  elevated — unexpected")
    log("    EZH2/ASXL1 suppressed — epigenetic loss")
    log("")
    log("  Script 2 new predictions (before running):")
    log("    GFI1 elevated — blocks ELANE despite CEBPE")
    log("    GATA2 elevated — retained HSPC identity")
    log("    CEBPB elevated — inflammatory GMP state")
    log("    KDM1A dysregulated — LSD1 complex")
    log("    CEBPE→ELANE correlation broken in MDS")
    log("    S2 depth score stratifies better than S1")
    log("")

    log("\n=== STEP 0: DATA ACQUISITION ===")
    cpm_path = acquire_data()

    log("\n=== STEP 1: METADATA ===")
    meta = fetch_metadata()

    log("\n=== STEP 2: LOAD CPM ===")
    expr = load_cpm(cpm_path)

    log("\n=== STEP 3: MERGE AND CLASSIFY ===")
    merged = merge_with_meta(expr, meta)

    log("\n=== STEP 4: CEBPE → ELANE GAP ===")
    gap_df, normal, mds = test_cebpe_elane_gap(merged)

    log("\n=== STEP 5: FULL SADDLE POINT ===")
    all_df = full_saddle_s2(merged, normal, mds)

    log("\n=== STEP 6: REVISED DEPTH SCORE ===")
    mds, subtype_depth = revised_depth_score(
        merged, normal, mds, all_df
    )

    log("\n=== STEP 7: HSPC IDENTITY + "
        "INFLAMMATORY GMP ===")
    hspc_and_inflammatory(merged, normal, mds)

    log("\n=== STEP 8: GFI1 ANALYSIS ===")
    gfi1_depth_analysis(mds)

    log("\n=== STEP 9: S1 vs S2 COMPARISON ===")
    depth_s1, depth_s2, mds_full = compare_depth_scores(
        merged, mds
    )

    log("\n=== STEP 10: FIGURE ===")
    generate_figure(
        merged, normal, mds, gap_df, all_df,
        depth_s1, depth_s2, mds_full
    )

    write_log()
    log(f"\n  Log: {LOG_FILE}")
    log(f"  All outputs: {RESULTS_DIR}")
    log("\n=== SCRIPT 2 COMPLETE ===")


if __name__ == "__main__":
    main()
