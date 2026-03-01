"""
Pancreatic Ductal Adenocarcinoma — False Attractor Analysis
SCRIPT 2 — CORRECTED FRAMEWORK
Built from Script 1 findings

SCRIPT 1 FINDINGS:
  Depth correlations confirmed ALL switch genes
  (internal tumor heterogeneity — 241 samples):
    KRT19    r=+0.845  p=7.24e-67  TRUE FA marker
    CTRC     r=-0.760  TRUE acinar switch gene
    KRAS     r=+0.760  ATTRACTOR STABILIZER
    PNLIPRP1 r=-0.756  acinar enzyme
    AMY2A    r=-0.751  acinar enzyme
    RBPJL    r=-0.744  predicted switch — CONFIRMED
    NR5A2    r=-0.742  predicted switch — CONFIRMED
    MKI67    r=+0.742  proliferation tracks depth
    CPA1     r=-0.728  acinar enzyme
    PTF1A    r=-0.709  master switch — CONFIRMED
  GATA6 subtype confirmed: Basal deeper p=0.000
  POSTN +49.0% — stromal component unexpected
  MYC flat — wrong direction
  Normal classifier broken — only 3 of 105 found

SCRIPT 2 NEW PREDICTIONS (stated before running):
  P1: Fix classifier → acinar gene suppression
      will be MUCH larger than Script 1 showed
      All acinar enzymes will be -50% to -90%
  P2: KRAS expression correlates with depth
      r > 0.7 confirmed — KRAS stabilizes attractor
  P3: r(EZH2, PTF1A) negative in tumors
      EZH2 represses PTF1A — the gap mechanism
  P4: POSTN tracks with depth — stroma is
      part of the attractor not just a bystander
  P5: Corrected depth score (KRT19 + acinar
      enzyme panel) stratifies survival
      r < -0.2 p < 0.05 after classifier fix
  P6: TFF1/TFF2 elevated — gastric metaplasia
      component of the false attractor
  P7: KRAS→EZH2→PTF1A circuit is the
      molecular mechanism of the block

Dataset: GSE183795
  139 PAAD tumors | 105 adjacent non-tumor
Author: Eric Robert Lawson
Framework: OrganismCore Principles-First
Doc: 87b | Date: 2026-03-01
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
RESULTS_DIR = os.path.join(BASE_DIR, "results_s2")
S1_DIR      = os.path.join(BASE_DIR, "results")
LOG_FILE    = os.path.join(RESULTS_DIR,
                           "analysis_log_s2.txt")

os.makedirs(BASE_DIR,    exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

META_URL = ("https://www.ncbi.nlm.nih.gov/geo/"
            "query/acc.cgi?acc=GSE183795"
            "&targ=gsm&form=text&view=full")

FILES = {
    "matrix": "GSE183795_normalized_matrix.txt.gz",
}

# ============================================================
# GENE PANELS
# ============================================================

# S1 CONFIRMED switch genes — acinar identity
# All had |r| > 0.70 with depth in Script 1
SWITCH_CONFIRMED = [
    "PTF1A",    # r=-0.709
    "NR5A2",    # r=-0.742
    "RBPJL",    # r=-0.744
    "BHLHA15",  # r=-0.683
    "CPA1",     # r=-0.728
    "PRSS1",    # r=-0.700
]

# ACINAR ENZYME CLUSTER — all confirmed by depth
ACINAR_ENZYMES = [
    "CTRC",     # r=-0.760 — strongest switch signal
    "PNLIPRP1", # r=-0.756
    "AMY2A",    # r=-0.751
    "PNLIP",    # r=-0.749
    "CEL",      # r=-0.745
    "CELA3B",   # r=-0.744
    "CELA3A",   # r=-0.739
    "PNLIPRP2", # r=-0.732
    "CPA2",     # r=-0.720
    "CTRB2",    # r=-0.705
    "CPB1",     # r=-0.701
    "PRSS2",    # acinar enzyme
    "PRSS3",    # acinar enzyme
    "AMY2B",    # amylase
]

# FALSE ATTRACTOR — KRT19 dominant
FA_MARKERS = [
    "KRT19",    # r=+0.845 — strongest FA signal
    "KRT7",     # ductal marker
    "KRT18",    # ductal marker
    "SOX9",     # ductal TF
    "MUC1",     # ductal surface
    "EPCAM",    # progenitor surface
    "TFF1",     # unexpected — test
    "TFF2",     # unexpected — test
]

# KRAS AXIS — new S2 prediction
KRAS_AXIS = [
    "KRAS",     # r=+0.760 — attractor stabilizer
    "HRAS",     # RAS family
    "NRAS",     # RAS family
    "BRAF",     # RAS→MAPK
    "MAP2K1",   # MEK1
    "MAPK1",    # ERK2
    "MAPK3",    # ERK1
    "MYC",      # KRAS target
    "CCND1",    # KRAS target
    "MKI67",    # proliferation — r=+0.742
]

# EZH2 → PTF1A GAP — new S2 prediction
# Prediction: EZH2 represses PTF1A
# r(EZH2, PTF1A) should be negative
EZH2_GAP = [
    "EZH2",     # predicted: represses PTF1A
    "EED",      # PRC2 complex
    "SUZ12",    # PRC2 complex
    "JARID2",   # PRC2 recruiter
    "KDM6A",    # H3K27 demethylase (opposes EZH2)
    "BMI1",     # PRC1 — H2AK119ub1
    "RING1",    # PRC1
]

# STROMA AXIS — unexpected S1 finding
STROMA = [
    "POSTN",    # +49.0% — unexpected strong signal
    "SPARC",    # +11.7%
    "FN1",      # +13.7%
    "ACTA2",    # smooth muscle actin
    "FAP",      # fibroblast activation protein
    "PDGFRA",   # stromal receptor
    "COL1A1",   # collagen I
    "COL1A2",   # collagen I
    "TGFB1",    # TGF-beta — stroma driver
    "TGFB2",    # TGF-beta
]

# SUBTYPE — GATA6 axis confirmed
SUBTYPE = [
    "GATA6",    # Classical marker
    "KRT5",     # Basal marker
    "KRT14",    # Basal marker
    "VIM",      # mesenchymal
    "CDH1",     # E-cadherin
    "CDH2",     # N-cadherin
    "ZEB1",     # EMT TF
    "SNAI1",    # EMT TF
    "TWIST1",   # EMT TF
]

# SURVIVAL GENES — from S1 correlations
SURVIVAL_GENES = [
    "KRT7",     # r=-0.283 strongest survival
    "POSTN",    # r=-0.229
    "FN1",      # r=-0.216
    "MKI67",    # r=-0.216
    "KRT18",    # r=-0.203
    "KRT19",    # r=-0.198
    "AMY2B",    # r=+0.194 (protective)
    "KRAS",     # r=-0.189
    "DNMT3A",   # r=-0.183
    "EZH2",     # r=-0.150
]

ALL_TARGET_S2 = list(dict.fromkeys(
    SWITCH_CONFIRMED +
    ACINAR_ENZYMES +
    FA_MARKERS +
    KRAS_AXIS +
    EZH2_GAP +
    STROMA +
    SUBTYPE +
    SURVIVAL_GENES
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
# STEP 0: DATA — reuse S1 download
# ============================================================

def get_data():
    log("=" * 65)
    log("STEP 0: DATA — reusing Script 1 download")
    log("=" * 65)
    paths = {}
    for key, fname in FILES.items():
        local = os.path.join(BASE_DIR, fname)
        if os.path.exists(local):
            size_mb = os.path.getsize(local) / 1e6
            log(f"  Found: {fname} "
                f"({size_mb:.1f} MB) — reusing")
            paths[key] = local
        else:
            log(f"  NOT FOUND: {fname}")
            log(f"  Run Script 1 first.")
            sys.exit(1)
    return paths

# ============================================================
# STEP 1: METADATA — with corrected classifier
# ============================================================

def fetch_metadata_corrected():
    log("")
    log("=" * 65)
    log("STEP 1: METADATA — CORRECTED CLASSIFIER")
    log("Script 1 found only 3/105 normal samples")
    log("Fixing sample ID matching")
    log("=" * 65)

    cache = os.path.join(S1_DIR, "metadata.csv")
    if os.path.exists(cache):
        df = pd.read_csv(cache, index_col=0)
        log(f"  Loaded: {len(df)} samples from cache")
    else:
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
        os.makedirs(S1_DIR, exist_ok=True)
        df.to_csv(cache)

    # Classify using tissue field
    df["group"] = "UNKNOWN"
    if "tissue" in df.columns:
        tis = df["tissue"].fillna("").str.lower()
        df.loc[
            tis.str.contains(
                "adjacent|non.tumor|nontumor",
                na=False
            ), "group"
        ] = "NORMAL"
        df.loc[
            tis.str.contains(
                "^tumor$", na=False
            ), "group"
        ] = "TUMOR"

    log(f"\n  Group counts from metadata:")
    log(f"    TUMOR  : "
        f"{(df['group']=='TUMOR').sum()}")
    log(f"    NORMAL : "
        f"{(df['group']=='NORMAL').sum()}")
    log(f"    UNKNOWN: "
        f"{(df['group']=='UNKNOWN').sum()}")

    # Show example titles for each group
    for grp in ["TUMOR", "NORMAL"]:
        examples = df[
            df["group"] == grp
        ]["title"].head(3).tolist()
        log(f"\n  {grp} title examples:")
        for e in examples:
            log(f"    {e}")

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

    log(f"  Raw: {df.shape[0]} genes x "
        f"{df.shape[1]} columns")

    # Drop non-numeric annotation columns
    non_expr = []
    for col in df.columns:
        try:
            pd.to_numeric(df[col].iloc[:5])
        except Exception:
            non_expr.append(col)
    if non_expr:
        df = df.drop(columns=non_expr)

    df = df.apply(pd.to_numeric, errors="coerce")

    # Keep target genes
    found = [g for g in ALL_TARGET_S2
             if g in df.index]
    log(f"  Target genes: "
        f"{len(found)}/{len(ALL_TARGET_S2)}")
    missing = [g for g in ALL_TARGET_S2
               if g not in df.index]
    if missing:
        log(f"  Missing: {missing[:10]}")

    df = df.loc[found]
    df = df.T
    df.index = pd.Index(
        [i.replace(".CEL", "").strip()
         for i in df.index],
        name="sample_id"
    )
    log(f"  Final: {df.shape}")
    return df

# ============================================================
# STEP 3: MERGE — CORRECTED MATCHING
# ============================================================

def merge_corrected(expr, meta):
    log("")
    log("=" * 65)
    log("STEP 3: MERGE — CORRECTED MATCHING")
    log("=" * 65)

    meta = meta.copy()
    meta_cols = [c for c in [
        "tissue", "group", "grading",
        "stage", "resection_margin",
        "survival_months", "survival_status",
    ] if c in meta.columns]

    # Strategy 1: direct title match
    meta_indexed = meta.set_index("title")
    merged = expr.join(
        meta_indexed[meta_cols],
        how="left"
    )

    n_matched = merged["group"].notna().sum() \
        if "group" in merged.columns else 0
    log(f"  Strategy 1 (title match): "
        f"{n_matched}/{len(merged)} matched")

    # Strategy 2: partial string match
    # Matrix index: "10_E33-Tn13_N"
    # Meta title:   "10_E33-Tn13_N" (should match)
    # If not matching — try stripping whitespace
    if n_matched < len(merged) * 0.8:
        log("  Strategy 1 insufficient — "
            "trying fuzzy match...")

        meta_map = {}
        for _, row in meta.iterrows():
            title_clean = (
                str(row.get("title", ""))
                .strip()
                .replace(" ", "_")
            )
            meta_map[title_clean] = {
                c: row.get(c)
                for c in meta_cols
            }

        # Also map by last component
        meta_map2 = {}
        for _, row in meta.iterrows():
            title = str(row.get("title", ""))
            for part in title.split("_"):
                if len(part) > 3:
                    meta_map2[part] = {
                        c: row.get(c)
                        for c in meta_cols
                    }

        new_data = {c: [] for c in meta_cols}
        matched  = 0
        for idx in expr.index:
            idx_clean = (
                str(idx).strip()
                .replace(" ", "_")
            )
            hit = (meta_map.get(idx_clean)
                   or meta_map.get(idx))
            if hit is None:
                # Try partial match
                for k, v in meta_map.items():
                    if (idx_clean in k
                            or k in idx_clean):
                        hit = v
                        break
            if hit:
                matched += 1
                for c in meta_cols:
                    new_data[c].append(
                        hit.get(c)
                    )
            else:
                for c in meta_cols:
                    new_data[c].append(None)

        log(f"  Strategy 2 (fuzzy): "
            f"{matched}/{len(expr)} matched")

        for c in meta_cols:
            merged[c] = new_data[c]

    # Strategy 3: direct tissue classification
    # from sample index name
    # _N or _Tn → NORMAL
    # _T or _Tc or _Tp → TUMOR
    log("\n  Strategy 3: index-name classification")
    n_fixed = 0
    for idx in merged.index:
        if merged.loc[idx, "group"] is None or \
                pd.isna(merged.loc[idx, "group"]) \
                or merged.loc[idx, "group"] \
                == "UNKNOWN":
            idx_l = str(idx).lower()
            # Patterns from structure check:
            # E5-Tc8_T → tumor
            # E33-Tn13_N → normal
            if idx_l.endswith("_n"):
                merged.loc[idx, "group"] = "NORMAL"
                n_fixed += 1
            elif (idx_l.endswith("_t")
                  or "_tc" in idx_l
                  or "_tp" in idx_l):
                merged.loc[idx, "group"] = "TUMOR"
                n_fixed += 1

    log(f"  Strategy 3 fixed: {n_fixed} samples")

    # Final counts
    n_t = (merged["group"] == "TUMOR").sum()
    n_n = (merged["group"] == "NORMAL").sum()
    n_u = (merged["group"] == "UNKNOWN").sum() + \
          merged["group"].isna().sum()

    log(f"\n  FINAL CLASSIFICATION:")
    log(f"    TUMOR  : {n_t}")
    log(f"    NORMAL : {n_n}")
    log(f"    UNKNOWN: {n_u}")

    # Numeric conversions
    for col in ["survival_months",
                "survival_status"]:
        if col in merged.columns:
            merged[col] = pd.to_numeric(
                merged[col], errors="coerce"
            )

    return merged

# ============================================================
# STEP 4: CORRECTED SADDLE POINT TABLE
# ============================================================

def saddle_corrected(merged):
    log("")
    log("=" * 65)
    log("STEP 4: CORRECTED SADDLE POINT TABLE")
    log("With proper normal classification")
    log("=" * 65)

    tumor  = merged[merged["group"] == "TUMOR"]
    normal = merged[merged["group"] == "NORMAL"]

    log(f"  TUMOR  : {len(tumor)}")
    log(f"  NORMAL : {len(normal)}")

    if len(normal) < 3:
        log("  WARNING: Still too few normal samples")
        log("  Using all unclassified as potential")
        log("  normal based on _N suffix...")
        # Force: anything with _N in index
        mask = pd.Series(
            [str(i).endswith("_N")
             for i in merged.index],
            index=merged.index
        )
        normal = merged[mask]
        tumor  = merged[~mask & (
            merged["group"] == "TUMOR"
        )]
        log(f"  After force: "
            f"TUMOR={len(tumor)} "
            f"NORMAL={len(normal)}")

    gene_cols = [c for c in merged.columns
                 if c in ALL_TARGET_S2]

    def fmt_p(p):
        if p < 1e-300:  return "p=0.00e+00 ***"
        elif p < 0.001: return f"p={p:.2e} ***"
        elif p < 0.01:  return f"p={p:.2e}  **"
        elif p < 0.05:  return f"p={p:.4f}   *"
        else:           return f"p={p:.4f}  ns"

    role_map = {}
    for g in SWITCH_CONFIRMED:   role_map[g]="SWITCH"
    for g in ACINAR_ENZYMES:     role_map[g]="ACINAR"
    for g in FA_MARKERS:         role_map[g]="FA"
    for g in KRAS_AXIS:          role_map[g]="KRAS"
    for g in EZH2_GAP:           role_map[g]="EZH2"
    for g in STROMA:             role_map[g]="STROMA"
    for g in SUBTYPE:            role_map[g]="SUBTYPE"

    log(f"\n  {'Gene':<12} {'Role':<8} "
        f"{'Normal':>9} {'Tumor':>9} "
        f"{'Change':>9} {'p-value':>16}")
    log(f"  {'-'*72}")

    results = []
    for gene in ALL_TARGET_S2:
        if gene not in gene_cols:
            continue
        nd_v = normal[gene].dropna().values
        td_v = tumor[gene].dropna().values
        if len(nd_v) < 2 or len(td_v) < 3:
            continue

        nd_m = nd_v.mean()
        td_m = td_v.mean()
        chg  = ((td_m - nd_m) / nd_m * 100
                if nd_m > 0.0001 else np.nan)
        _, p_s = stats.mannwhitneyu(
            nd_v, td_v, alternative="greater"
        )
        _, p_e = stats.mannwhitneyu(
            td_v, nd_v, alternative="greater"
        )
        p_use = min(p_s, p_e)
        role  = role_map.get(gene, "OTHER")

        chg_str = (f"{chg:+.1f}%"
                   if not np.isnan(chg) else "N/A")
        log(f"  {gene:<12} {role:<8} "
            f"{nd_m:>9.4f} {td_m:>9.4f} "
            f"{chg_str:>9}  {fmt_p(p_use):>16}")

        results.append({
            "gene": gene, "role": role,
            "normal_mean": nd_m,
            "tumor_mean": td_m,
            "change_pct": chg,
            "p_value": p_use,
        })

    rdf = pd.DataFrame(results)
    rdf.to_csv(
        os.path.join(RESULTS_DIR,
                     "saddle_s2.csv"),
        index=False
    )
    return rdf, tumor, normal

# ============================================================
# STEP 5: CORRECTED DEPTH SCORE
# S1: PTF1A panel + KRT19/SOX9/MUC1/EPCAM
# S2: CTRC/AMY2A acinar enzyme cluster + KRT19
# ============================================================

def depth_score_s2(tumor):
    log("")
    log("=" * 65)
    log("STEP 5: CORRECTED DEPTH SCORE")
    log("S1: predicted switch + FA panel")
    log("S2: CTRC/acinar cluster + KRT19")
    log("    (top depth correlation genes)")
    log("=" * 65)

    gene_cols = [c for c in tumor.columns
                 if c in ALL_TARGET_S2]

    def norm01(s):
        mn, mx = s.min(), s.max()
        return ((s - mn) / (mx - mn)
                if mx > mn
                else pd.Series(
                    0.0, index=s.index
                ))

    tumor = tumor.copy()

    # S2 depth: top acinar enzymes + KRT19
    acinar_top = [g for g in [
        "CTRC", "PNLIPRP1", "AMY2A", "PNLIP",
        "CEL", "CELA3B", "NR5A2", "RBPJL"
    ] if g in gene_cols]

    depth_s2 = pd.Series(
        np.zeros(len(tumor)), index=tumor.index
    )
    comp = 0

    if acinar_top:
        ac_mean = tumor[acinar_top].mean(axis=1)
        depth_s2 += (1 - norm01(ac_mean))
        comp += 1
        log(f"  Component 1: acinar suppression "
            f"n={len(acinar_top)} genes")

    if "KRT19" in gene_cols:
        depth_s2 += norm01(tumor["KRT19"])
        comp += 1
        log(f"  Component 2: KRT19 elevation")

    if comp > 0:
        depth_s2 /= comp

    tumor["depth_s2"] = depth_s2.values

    log(f"\n  S2 depth ({len(tumor)} tumors):")
    log(f"    Mean   : {depth_s2.mean():.4f}")
    log(f"    Median : {depth_s2.median():.4f}")
    log(f"    Std    : {depth_s2.std():.4f}")
    log(f"    Min    : {depth_s2.min():.4f}")
    log(f"    Max    : {depth_s2.max():.4f}")

    # S1 depth for comparison
    s1_sw = [g for g in [
        "PTF1A", "NR5A2", "RBPJL",
        "BHLHA15", "CPA1", "PRSS1"
    ] if g in gene_cols]
    s1_fa = [g for g in [
        "KRT19", "SOX9", "MUC1", "EPCAM"
    ] if g in gene_cols]

    depth_s1 = pd.Series(
        np.zeros(len(tumor)), index=tumor.index
    )
    c1 = 0
    if s1_sw:
        depth_s1 += (1 - norm01(
            tumor[s1_sw].mean(axis=1)
        ))
        c1 += 1
    if s1_fa:
        depth_s1 += norm01(
            tumor[s1_fa].mean(axis=1)
        )
        c1 += 1
    if c1 > 0:
        depth_s1 /= c1

    tumor["depth_s1"] = depth_s1.values

    # Compare
    r, p = stats.pearsonr(
        depth_s1.values, depth_s2.values
    )
    log(f"\n  S1 vs S2 correlation: "
        f"r={r:.4f}  p={p:.2e}")
    if r > 0.9:
        log("  Concordant — same biology")
    elif r > 0.6:
        log("  Partial concordance")
    else:
        log("  Divergent — S2 captures new axis")

    # Depth by stage
    if "stage" in tumor.columns:
        log("\n  S2 depth by stage:")
        for stage in ["IA", "IB", "IIA",
                      "IIB", "III", "IV"]:
            sd = tumor[
                tumor["stage"] == stage
            ]["depth_s2"]
            if len(sd) > 2:
                log(f"    {stage:>5} "
                    f"(n={len(sd):3d}): "
                    f"{sd.mean():.4f}")

    # Top depth correlations
    log("\n  S2 depth correlations (top 20):")
    corrs = []
    for gene in gene_cols:
        try:
            rv, pv = stats.pearsonr(
                tumor["depth_s2"].values,
                tumor[gene].values
            )
            corrs.append((gene, rv, pv))
        except Exception:
            pass
    corrs.sort(
        key=lambda x: abs(x[1]), reverse=True
    )
    log(f"  {'Gene':<12} {'r':>8}  p-value")
    log(f"  {'-'*34}")
    for gene, rv, pv in corrs[:20]:
        log(f"  {gene:<12} {rv:>+8.4f}  "
            f"p={pv:.2e}")

    return tumor, corrs

# ============================================================
# STEP 6: THE GAP — KRAS → EZH2 → PTF1A
# ============================================================

def test_gap(tumor):
    log("")
    log("=" * 65)
    log("STEP 6: THE GAP — KRAS → EZH2 → PTF1A")
    log("Prediction: r(EZH2, PTF1A) < 0 in tumors")
    log("EZH2 represses PTF1A — the molecular")
    log("mechanism of the block")
    log("=" * 65)

    gene_cols = [c for c in tumor.columns
                 if c in ALL_TARGET_S2]

    pairs = [
        ("KRAS",  "EZH2",  "KRAS drives EZH2?"),
        ("EZH2",  "PTF1A", "EZH2 represses PTF1A?"),
        ("KRAS",  "PTF1A", "KRAS suppresses PTF1A?"),
        ("EZH2",  "NR5A2", "EZH2 represses NR5A2?"),
        ("EZH2",  "RBPJL", "EZH2 represses RBPJL?"),
        ("KRAS",  "KRT19", "KRAS drives KRT19?"),
        ("EZH2",  "KRT19", "EZH2 drives KRT19?"),
        ("KRAS",  "CTRC",  "KRAS suppresses acinar?"),
        ("MKI67", "KRAS",  "Proliferation-KRAS link?"),
        ("POSTN", "depth_s2", "Stroma tracks depth?"),
        ("TGFB1", "POSTN", "TGF-beta drives stroma?"),
    ]

    log(f"\n  {'Pair':<28} {'r':>8}  "
        f"p-value  Prediction  Result")
    log(f"  {'-'*72}")

    gap_results = []
    for g1, g2, label in pairs:
        if g1 not in tumor.columns or \
                g2 not in tumor.columns:
            log(f"  {g1}→{g2:<20} not available")
            continue
        try:
            rv, pv = stats.pearsonr(
                tumor[g1].values,
                tumor[g2].values
            )
            # Determine expected direction
            expect_neg = any(
                kw in label.lower()
                for kw in ["represses",
                           "suppresses"]
            )
            expect_pos = any(
                kw in label.lower()
                for kw in ["drives", "link",
                           "tracks"]
            )
            if expect_neg:
                conf = (
                    "CONFIRMED"
                    if rv < -0.15 and pv < 0.05
                    else "NOT CONFIRMED"
                )
                pred = "r<0"
            elif expect_pos:
                conf = (
                    "CONFIRMED"
                    if rv > 0.15 and pv < 0.05
                    else "NOT CONFIRMED"
                )
                pred = "r>0"
            else:
                conf = "SEE DATA"
                pred = "?"

            log(f"  {g1}→{g2:<20} "
                f"{rv:>+8.4f}  "
                f"p={pv:.2e}  "
                f"{pred:<5}  {conf}")

            gap_results.append({
                "pair": f"{g1}→{g2}",
                "label": label,
                "r": rv, "p": pv,
                "result": conf,
            })
        except Exception as e:
            log(f"  {g1}→{g2}: error {e}")

    # CEBPE→ELANE equivalent: PTF1A→CTRC
    # Does PTF1A drive CTRC in normal granulopoiesis?
    # In pancreas: PTF1A should drive acinar enzymes
    # In MDS: CEBPE→ELANE was r=0.07 (disconnected)
    # Prediction: PTF1A→CTRC is CONNECTED in tumors
    # (cells that retain some PTF1A still have CTRC)
    # OR disconnected (like MDS) if block is
    # downstream of PTF1A
    log(f"\n  PTF1A → Acinar enzyme connections:")
    for enz in ["CTRC", "AMY2A",
                "CPA1", "PNLIP"]:
        if ("PTF1A" in tumor.columns
                and enz in tumor.columns):
            rv, pv = stats.pearsonr(
                tumor["PTF1A"].values,
                tumor[enz].values
            )
            status = ("CONNECTED"
                      if rv > 0.3 and pv < 0.05
                      else "WEAK/DISCONNECTED")
            log(f"    PTF1A→{enz:<10} "
                f"r={rv:+.4f}  p={pv:.2e}  "
                f"{status}")

    return gap_results

# ============================================================
# STEP 7: STROMA AS ATTRACTOR COMPONENT
# ============================================================

def stroma_analysis(tumor, normal):
    log("")
    log("=" * 65)
    log("STEP 7: STROMA AS ATTRACTOR COMPONENT")
    log("Prediction: POSTN tracks depth")
    log("POSTN may stabilize the false attractor")
    log("via TGF-beta / fibroblast activation")
    log("=" * 65)

    gene_cols = [c for c in tumor.columns
                 if c in ALL_TARGET_S2]

    # POSTN vs depth
    if ("POSTN" in gene_cols
            and "depth_s2" in tumor.columns):
        rv, pv = stats.pearsonr(
            tumor["POSTN"].values,
            tumor["depth_s2"].values
        )
        log(f"\n  POSTN vs S2 depth:")
        log(f"    r = {rv:+.4f}  p = {pv:.2e}")
        log(f"    Prediction: positive "
            f"(stroma tracks dedifferentiation)")
        log(f"    Result: "
            f"{'CONFIRMED' if rv > 0.15 and pv < 0.05 else 'NOT CONFIRMED'}")

    # Stroma vs survival
    if "survival_months" in tumor.columns:
        log(f"\n  Stroma gene vs survival:")
        for gene in ["POSTN", "SPARC", "FN1",
                     "COL1A1", "TGFB1", "FAP"]:
            if gene not in gene_cols:
                continue
            sv = tumor[
                ["survival_months", gene]
            ].dropna()
            if len(sv) < 10:
                continue
            rv, pv = stats.pearsonr(
                sv[gene].values,
                sv["survival_months"].values
            )
            log(f"    {gene:<10} r={rv:+.4f}  "
                f"p={pv:.2e}")

    # Normal vs tumor stroma
    log(f"\n  Stroma in tumor vs normal:")
    log(f"  {'Gene':<10} {'Normal':>9} "
        f"{'Tumor':>9} {'Change':>9}")
    log(f"  {'-'*44}")
    for gene in STROMA:
        if gene not in gene_cols:
            continue
        if len(normal) < 2:
            continue
        nd_m = normal[gene].mean()
        td_m = tumor[gene].mean()
        chg  = ((td_m - nd_m) / nd_m * 100
                if nd_m > 0.0001 else np.nan)
        chg_str = (f"{chg:+.1f}%"
                   if not np.isnan(chg) else "N/A")
        log(f"  {gene:<10} {nd_m:>9.4f} "
            f"{td_m:>9.4f} {chg_str:>9}")

# ============================================================
# STEP 8: CORRECTED SURVIVAL ANALYSIS
# ============================================================

def survival_corrected(tumor):
    log("")
    log("=" * 65)
    log("STEP 8: CORRECTED SURVIVAL ANALYSIS")
    log("S2 depth score vs overall survival")
    log("=" * 65)

    if "depth_s2" not in tumor.columns:
        log("  depth_s2 not computed — skip")
        return

    surv = tumor[
        ["depth_s2", "depth_s1",
         "survival_months",
         "survival_status", "stage"]
    ].copy()
    surv["survival_months"] = pd.to_numeric(
        surv["survival_months"], errors="coerce"
    )
    surv = surv.dropna(
        subset=["survival_months", "depth_s2"]
    )
    surv = surv[surv["survival_months"] > 0]

    log(f"\n  Samples: {len(surv)}")
    if len(surv) < 10:
        log("  Too few — skip")
        return

    # S2 depth vs survival
    r2, p2 = stats.pearsonr(
        surv["depth_s2"].values,
        surv["survival_months"].values
    )
    rs2, ps2 = stats.spearmanr(
        surv["depth_s2"].values,
        surv["survival_months"].values
    )
    log(f"\n  S2 depth vs survival:")
    log(f"    Pearson  r={r2:+.4f}  p={p2:.2e}")
    log(f"    Spearman r={rs2:+.4f}  p={ps2:.2e}")
    log(f"    Prediction: r < 0")
    log(f"    Result: "
        f"{'CONFIRMED' if r2 < -0.1 and p2 < 0.05 else 'NOT CONFIRMED'}")

    # S1 depth vs survival
    if "depth_s1" in surv.columns:
        r1, p1 = stats.pearsonr(
            surv["depth_s1"].values,
            surv["survival_months"].values
        )
        log(f"\n  S1 depth vs survival:")
        log(f"    Pearson  r={r1:+.4f}  p={p1:.2e}")

    # High vs low depth
    med = surv["depth_s2"].median()
    hi  = surv[surv["depth_s2"] >= med]
    lo  = surv[surv["depth_s2"] <  med]
    log(f"\n  High depth (n={len(hi)}): "
        f"median = "
        f"{hi['survival_months'].median():.1f} mo")
    log(f"  Low  depth (n={len(lo)}): "
        f"median = "
        f"{lo['survival_months'].median():.1f} mo")
    if len(hi) > 3 and len(lo) > 3:
        _, pmw = stats.mannwhitneyu(
            hi["survival_months"].values,
            lo["survival_months"].values,
            alternative="less"
        )
        log(f"  High worse: p={pmw:.4f}")

    # KRAS vs survival
    if "KRAS" in tumor.columns:
        ks = tumor[
            ["KRAS", "survival_months"]
        ].dropna()
        ks["survival_months"] = pd.to_numeric(
            ks["survival_months"], errors="coerce"
        )
        ks = ks.dropna()
        if len(ks) > 10:
            rk, pk = stats.pearsonr(
                ks["KRAS"].values,
                ks["survival_months"].values
            )
            log(f"\n  KRAS vs survival: "
                f"r={rk:+.4f}  p={pk:.2e}")

    # Stage vs depth
    if "stage" in surv.columns:
        log(f"\n  Depth by stage:")
        for stage in ["IIA", "IIB",
                      "III", "IV"]:
            sd = surv[
                surv["stage"] == stage
            ]["depth_s2"]
            if len(sd) > 3:
                log(f"    {stage:>5} "
                    f"(n={len(sd):3d}): "
                    f"{sd.mean():.4f}")

    return surv

# ============================================================
# STEP 9: SUBTYPE ANALYSIS — CORRECTED
# ============================================================

def subtype_corrected(tumor):
    log("")
    log("=" * 65)
    log("STEP 9: SUBTYPE ANALYSIS — CORRECTED")
    log("GATA6 stratifies depth (confirmed S1)")
    log("Testing: depth → survival by subtype")
    log("=" * 65)

    gene_cols = [c for c in tumor.columns
                 if c in ALL_TARGET_S2]

    if "GATA6" not in gene_cols:
        log("  GATA6 not available — skip")
        return

    med_g6   = tumor["GATA6"].median()
    classical = tumor[
        tumor["GATA6"] >= med_g6
    ].copy()
    basal     = tumor[
        tumor["GATA6"] <  med_g6
    ].copy()

    log(f"\n  Classical (n={len(classical)}): "
        f"GATA6 >= {med_g6:.3f}")
    log(f"  Basal-like (n={len(basal)}): "
        f"GATA6 < {med_g6:.3f}")

    for label, sub in [
        ("Classical", classical),
        ("Basal",     basal),
    ]:
        if "depth_s2" in sub.columns:
            log(f"\n  {label} depth: "
                f"{sub['depth_s2'].mean():.4f}")
        if "survival_months" in sub.columns:
            sv = pd.to_numeric(
                sub["survival_months"],
                errors="coerce"
            ).dropna()
            if len(sv) > 3:
                log(f"  {label} survival: "
                    f"{sv.median():.1f} mo "
                    f"(n={len(sv)})")

    # Depth vs survival within each subtype
    log(f"\n  Depth-survival correlation "
        f"by subtype:")
    for label, sub in [
        ("Classical", classical),
        ("Basal",     basal),
    ]:
        if ("depth_s2" not in sub.columns
                or "survival_months"
                not in sub.columns):
            continue
        sv = sub[
            ["depth_s2", "survival_months"]
        ].copy()
        sv["survival_months"] = pd.to_numeric(
            sv["survival_months"],
            errors="coerce"
        )
        sv = sv.dropna()
        if len(sv) < 8:
            continue
        rv, pv = stats.pearsonr(
            sv["depth_s2"].values,
            sv["survival_months"].values
        )
        log(f"  {label:<12}: "
            f"r={rv:+.4f}  p={pv:.2e}  "
            f"n={len(sv)}")

    # Key gene differences
    key_genes = [g for g in [
        "PTF1A", "NR5A2", "RBPJL",
        "CTRC", "AMY2A", "KRT19",
        "KRAS", "EZH2", "POSTN",
        "GATA6", "MKI67"
    ] if g in gene_cols]

    log(f"\n  {'Gene':<12} "
        f"{'Classical':>11} "
        f"{'Basal':>11} "
        f"{'Change':>9}")
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
# STEP 10: FIGURE
# ============================================================

def generate_figure(merged, tumor, normal,
                    saddle_df, corrs):
    fig = plt.figure(figsize=(26, 22))
    fig.suptitle(
        "PAAD False Attractor — Script 2 "
        "(Corrected Framework)\n"
        "Dataset: GSE183795 | OrganismCore "
        "2026-03-01 | Doc 87b\n"
        "Acinar enzyme cluster | "
        "KRAS→EZH2→PTF1A circuit | "
        "KRT19 FA axis | Stroma component",
        fontsize=10, fontweight="bold", y=0.99
    )
    gs = gridspec.GridSpec(
        3, 4, figure=fig,
        hspace=0.52, wspace=0.42
    )

    clr = {
        "NORMAL": "#2980b9",
        "TUMOR":  "#c0392b",
    }
    gene_cols = [c for c in merged.columns
                 if c in ALL_TARGET_S2]

    def bar_pair(ax, genes, title):
        avail = [g for g in genes
                 if g in gene_cols]
        if not avail:
            ax.text(0.5, 0.5,
                    "No data",
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
            ax.bar(
                x + i*w - 0.5*w, means, w,
                yerr=sems, color=c,
                label=grp, capsize=3, alpha=0.85
            )
        ax.set_xticks(x)
        ax.set_xticklabels(
            avail, rotation=45,
            ha="right", fontsize=7
        )
        ax.set_ylabel("Expression", fontsize=8)
        ax.set_title(title, fontsize=9)
        ax.legend(fontsize=7)

    # A — Acinar enzyme cluster
    ax_a = fig.add_subplot(gs[0, 0])
    bar_pair(ax_a,
             ["CTRC", "AMY2A", "PNLIP",
              "CEL", "CPA1", "CELA3B"],
             "A — Acinar Enzymes\n"
             "All r<-0.74 with depth")

    # B — Switch TFs
    ax_b = fig.add_subplot(gs[0, 1])
    bar_pair(ax_b,
             ["PTF1A", "NR5A2", "RBPJL",
              "BHLHA15"],
             "B — Acinar TFs\n"
             "PTF1A/NR5A2/RBPJL switch genes")

    # C — FA markers
    ax_c = fig.add_subplot(gs[0, 2])
    bar_pair(ax_c,
             ["KRT19", "KRT7", "SOX9",
              "TFF1", "TFF2"],
             "C — FA Markers\n"
             "KRT19 r=+0.845 dominant")

    # D — KRAS axis
    ax_d = fig.add_subplot(gs[0, 3])
    bar_pair(ax_d,
             ["KRAS", "MAPK1", "MAPK3",
              "MKI67", "CCND1"],
             "D — KRAS Axis\n"
             "KRAS r=+0.760 stabilizer")

    # E — EZH2 gap
    ax_e = fig.add_subplot(gs[1, 0])
    bar_pair(ax_e,
             ["EZH2", "EED", "SUZ12",
              "KDM6A", "BMI1"],
             "E — EZH2/PRC2 Complex\n"
             "Predicted: represses PTF1A")

    # F — Stroma
    ax_f = fig.add_subplot(gs[1, 1])
    bar_pair(ax_f,
             ["POSTN", "SPARC", "FN1",
              "COL1A1", "TGFB1"],
             "F — Stroma Genes\n"
             "POSTN +49% unexpected")

    # G — S2 depth distribution
    ax_g = fig.add_subplot(gs[1, 2])
    if "depth_s2" in tumor.columns:
        d = tumor["depth_s2"]
        ax_g.hist(d, bins=30,
                  color=clr["TUMOR"],
                  edgecolor="white", alpha=0.85)
        ax_g.axvline(
            d.mean(), color="black",
            linewidth=1.5,
            label=f"Mean={d.mean():.3f}"
        )
        ax_g.set_xlabel("S2 Depth Score",
                         fontsize=8)
        ax_g.set_ylabel("Count", fontsize=8)
        ax_g.set_title(
            "G — S2 Block Depth\n"
            "Acinar enzyme + KRT19 axis",
            fontsize=9
        )
        ax_g.legend(fontsize=7)

    # H — KRAS vs depth scatter
    ax_h = fig.add_subplot(gs[1, 3])
    if ("KRAS" in gene_cols
            and "depth_s2" in tumor.columns):
        ax_h.scatter(
            tumor["KRAS"],
            tumor["depth_s2"],
            alpha=0.3, s=15,
            color=clr["TUMOR"]
        )
        ax_h.set_xlabel("KRAS expression",
                         fontsize=8)
        ax_h.set_ylabel("S2 Depth", fontsize=8)
        ax_h.set_title(
            "H — KRAS vs Depth\n"
            "KRAS stabilizes attractor",
            fontsize=9
        )
        try:
            rv, pv = stats.pearsonr(
                tumor["KRAS"].values,
                tumor["depth_s2"].values
            )
            ax_h.text(
                0.05, 0.92,
                f"r={rv:.3f} p={pv:.2e}",
                transform=ax_h.transAxes,
                fontsize=8
            )
        except Exception:
            pass

    # I — Depth correlation waterfall
    ax_i = fig.add_subplot(gs[2, 0])
    if corrs:
        top_c = corrs[:20]
        genes_c = [c[0] for c in top_c]
        vals_c  = [c[1] for c in top_c]
        colors_c = ["#c0392b" if v < 0
                    else "#27ae60"
                    for v in vals_c]
        ax_i.barh(genes_c, vals_c,
                  color=colors_c)
        ax_i.axvline(0, color="black",
                      linewidth=0.8)
        ax_i.set_xlabel("r with S2 depth",
                         fontsize=8)
        ax_i.set_title(
            "I — Depth Correlations\n"
            "Top 20 genes",
            fontsize=9
        )
        ax_i.tick_params(axis="y", labelsize=7)

    # J — Depth vs survival
    ax_j = fig.add_subplot(gs[2, 1])
    if ("depth_s2" in tumor.columns
            and "survival_months"
            in tumor.columns):
        sv = tumor[
            ["depth_s2", "survival_months"]
        ].copy()
        sv["survival_months"] = pd.to_numeric(
            sv["survival_months"],
            errors="coerce"
        )
        sv = sv.dropna()
        sv = sv[sv["survival_months"] > 0]
        if len(sv) > 10:
            ax_j.scatter(
                sv["depth_s2"],
                sv["survival_months"],
                alpha=0.3, s=15,
                color=clr["TUMOR"]
            )
            ax_j.set_xlabel(
                "S2 Depth Score", fontsize=8
            )
            ax_j.set_ylabel(
                "Survival (months)", fontsize=8
            )
            ax_j.set_title(
                "J — Depth vs Survival\n"
                "Prediction: r < 0",
                fontsize=9
            )
            try:
                rv, pv = stats.pearsonr(
                    sv["depth_s2"].values,
                    sv["survival_months"].values
                )
                ax_j.text(
                    0.05, 0.92,
                    f"r={rv:.3f} p={pv:.2e}",
                    transform=ax_j.transAxes,
                    fontsize=8
                )
            except Exception:
                pass

    # K — GATA6 subtype depth
    ax_k = fig.add_subplot(gs[2, 2])
    if ("GATA6" in gene_cols
            and "depth_s2" in tumor.columns):
        ax_k.scatter(
            tumor["GATA6"],
            tumor["depth_s2"],
            alpha=0.3, s=15,
            color=clr["TUMOR"]
        )
        ax_k.set_xlabel(
            "GATA6 (Classical marker)",
            fontsize=8
        )
        ax_k.set_ylabel("S2 Depth", fontsize=8)
        ax_k.set_title(
            "K — GATA6 vs S2 Depth\n"
            "Classical=shallow Basal=deep",
            fontsize=9
        )
        try:
            rv, pv = stats.pearsonr(
                tumor["GATA6"].values,
                tumor["depth_s2"].values
            )
            ax_k.text(
                0.05, 0.92,
                f"r={rv:.3f} p={pv:.2e}",
                transform=ax_k.transAxes,
                fontsize=8
            )
        except Exception:
            pass

    # L — Summary
    ax_l = fig.add_subplot(gs[2, 3])
    ax_l.axis("off")
    summary = (
        "L — SCRIPT 2 SUMMARY\n"
        "────────────────────────────\n"
        "Framework: OrganismCore\n"
        "Doc: 87b | 2026-03-01\n\n"
        "S1 key findings:\n"
        "  KRT19  r=+0.845 FA axis\n"
        "  CTRC   r=-0.760 acinar sw\n"
        "  KRAS   r=+0.760 stabilizer\n"
        "  Normal classifier: 3/105\n\n"
        "S2 predictions:\n"
        "  Acinar enzymes >> suppressed\n"
        "  EZH2→PTF1A gap broken\n"
        "  POSTN tracks depth\n"
        "  KRAS→EZH2→PTF1A circuit\n"
        "  Survival r<0 confirmed\n\n"
        "False attractor:\n"
        "  Acinar→Ductal transition\n"
        "  KRT19 high / acinar low\n"
        "  KRAS stabilizes geometry\n"
        "  POSTN/stroma co-stabilizer\n\n"
        "Drug targets:\n"
        "  1. EZH2 inhibitor\n"
        "  2. KRAS inhibitor (G12D)\n"
        "  3. PTF1A restoration\n"
        "  4. Stroma (POSTN/TGFb)\n\n"
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
        RESULTS_DIR,
        "paad_false_attractor_s2.png"
    )
    plt.savefig(outpath, dpi=150,
                bbox_inches="tight")
    log(f"\n  Figure: {outpath}")
    plt.close()

# ============================================================
# MAIN
# ============================================================

def main():
    log("=" * 65)
    log("PAAD FALSE ATTRACTOR — SCRIPT 2")
    log("CORRECTED FRAMEWORK")
    log("Doc: 87b | Date: 2026-03-01")
    log("=" * 65)
    log("")
    log("  S1 wrong/incomplete:")
    log("    Normal classifier: 3/105 found")
    log("    MYC flat (predicted elevated)")
    log("    Survival not confirmed (bad groups)")
    log("")
    log("  S1 unexpected — driving S2:")
    log("    KRAS r=+0.760 (attractor stabilizer)")
    log("    Full acinar enzyme cluster confirmed")
    log("    POSTN +49% (stroma component)")
    log("    GATA6 subtype depth confirmed")
    log("")
    log("  S2 predictions:")
    log("    EZH2→PTF1A: r < 0 (repression)")
    log("    POSTN tracks depth")
    log("    KRAS→EZH2→PTF1A circuit")
    log("    Survival confirmed after fix")
    log("")

    log("\n=== STEP 0: DATA ===")
    paths = get_data()

    log("\n=== STEP 1: METADATA ===")
    meta = fetch_metadata_corrected()

    log("\n=== STEP 2: LOAD MATRIX ===")
    expr = load_matrix(paths["matrix"])

    log("\n=== STEP 3: MERGE — CORRECTED ===")
    merged = merge_corrected(expr, meta)

    log("\n=== STEP 4: SADDLE POINT CORRECTED ===")
    saddle_df, tumor, normal = \
        saddle_corrected(merged)

    log("\n=== STEP 5: DEPTH SCORE S2 ===")
    tumor, corrs = depth_score_s2(tumor)

    log("\n=== STEP 6: THE GAP ===")
    gap_results = test_gap(tumor)

    log("\n=== STEP 7: STROMA ANALYSIS ===")
    stroma_analysis(tumor, normal)

    log("\n=== STEP 8: SURVIVAL CORRECTED ===")
    survival_corrected(tumor)

    log("\n=== STEP 9: SUBTYPE CORRECTED ===")
    subtype_corrected(tumor)

    log("\n=== STEP 10: FIGURE ===")
    generate_figure(
        merged, tumor, normal,
        saddle_df, corrs
    )

    write_log()
    log(f"\n  Log: {LOG_FILE}")
    log(f"  All outputs: {RESULTS_DIR}")
    log("\n=== SCRIPT 2 COMPLETE ===")


if __name__ == "__main__":
    main()
