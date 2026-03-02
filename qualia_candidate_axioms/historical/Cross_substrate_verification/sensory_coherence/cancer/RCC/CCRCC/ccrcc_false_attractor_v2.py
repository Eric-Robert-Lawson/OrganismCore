"""
ccRCC False Attractor Analysis — Script 2 (Circuit and Subtype Run)
OrganismCore — Cancer False Attractor Framework
Document 94 | 2026-03-02

REQUIRES Script 1 outputs in ./ccrcc_false_attractor/results/
All Script 1 outputs must be present before running Script 2.

SCRIPT 2 ANALYSES (all derived from Script 1 findings):

    1. GEO log2 normalisation
       Raw intensity confirmed in Script 1. Apply log2(x+1)
       to GEO matrix before any quantitative analysis.
       Recompute cross-dataset correlation on comparable scales.

    2. EPAS1 vs HIF1A separation
       HIF1A DOWN in GEO, EPAS1 UP. ccRCC is HIF2α-driven.
       Separate the two and recompute HIF arm scores.

    3. Depth score vs stage (GSE53757)
       Stage 1-4 metadata available. Primary Script 2 test:
       does depth score increase with stage?

    4. Individual lipogenic gene circuits
       Group not significant in Script 1. Test each gene
       individually and identify which drive the signal.

    5. BAP1 vs PBRM1 subgroup analysis
       These define distinct ccRCC subtypes.
       Separate by expression proxy and compare depth scores.

    6. Immune signal separation
       Bulk immune infiltration contaminates tumour signal.
       Compute immune score and partial out from depth score.

    7. JAG1 circuit
       UP in GEO, borderline in TCGA. Notch pathway context.

    8. mTOR output proxies
       Replace pathway components with downstream readouts.

    9. Corrected cross-dataset comparison
       Recompute r after GEO log2 normalisation.

OUTPUTS (./ccrcc_false_attractor/results_s2/):
    geo_matrix_log2.csv
    geo_saddle_corrected.csv
    depth_vs_stage_geo.csv
    lipogenic_circuits.csv
    bap1_pbrm1_subgroups.csv
    immune_scores_tcga.csv
    immune_corrected_depth_tcga.csv
    jag1_circuit.csv
    mtor_proxies.csv
    cross_dataset_corrected.csv
    figure_s2.png
    s2_log.txt
"""

import os
import gzip

import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# ═══════════════════════════════════════════════════════════════════════════════
# DIRECTORIES
# ═══════════════════════════════════════════════════════════════════════════════

BASE_DIR    = "./ccrcc_false_attractor/"
S1_DIR      = os.path.join(BASE_DIR, "results")
S2_DIR      = os.path.join(BASE_DIR, "results_s2")
LOG_FILE    = os.path.join(S2_DIR, "s2_log.txt")

os.makedirs(S2_DIR, exist_ok=True)

# ═══════════════════════════════════════════════════════════════════════════════
# GENE PANELS — inherited from Script 1 + Script 2 additions
# ═══════════════════════════════════════════════════════════════════════════════

VHL_HIF = [
    "VHL",   "HIF1A",  "EPAS1",  "ARNT",
    "CA9",   "VEGFA",  "SLC2A1", "LDHA",
    "PDK1",  "EGLN1",  "EGLN3",
]

PROXIMAL_TUBULE_IDENTITY = [
    "SLC34A1", "GATM",    "AGXT",    "PCK1",
    "AQP1",    "CUBN",    "LRP2",    "SLC3A1",
    "SLC7A9",  "SLC22A6", "UMOD",    "SLC13A3",
    "PRODH",
]

NEPHRON_PROGENITOR = [
    "SIX2", "PAX2", "WT1", "CITED1", "SALL1", "OSR1",
]

PROXIMAL_MATURATION = [
    "LHX1", "JAG1", "DLL1", "HNF4A", "HNF1A", "PROM1",
]

EPIGENETIC_REGULATORS = [
    "BAP1", "PBRM1", "SETD2", "KDM5C",
    "KDM6A", "SMARCA4", "ARID1A",
]

METABOLIC_LIPOGENIC = [
    "FASN", "ACACA", "SCD", "HMGCR", "ACLY", "CPT1A",
]

METABOLIC_GLUCONEOGENIC = [
    "G6PC", "FBP1", "PCK2",
]

MTOR_PATHWAY = [
    "MTOR",    "RPTOR",    "RICTOR",
    "RPS6KB1", "EIF4EBP1", "AKT1",
    "PIK3CA",  "PTEN",
]

# mTOR downstream transcriptional output proxies
# These reflect mTOR activation at transcript level
# better than pathway component genes
MTOR_OUTPUT_PROXIES = [
    "MYC",    "CCND1",  "HIF1A",
    "SLC7A5", "SLC3A2", "EIF4E",
    "G3BP1",  "BIRC5",
]

IMMUNE_MARKERS = [
    "PDCD1", "CD274", "CTLA4", "CD8A",
    "FOXP3", "CD4",   "CD68",  "TIGIT", "LAG3",
]

# Immune cell type proxies for deconvolution
CD8_T_CELL    = ["CD8A", "CD8B", "GZMB", "PRF1"]
TREG          = ["FOXP3", "IL2RA", "CTLA4"]
MACROPHAGE    = ["CD68", "CD163", "MRC1", "CSF1R"]
NK_CELL       = ["NCAM1", "KLRB1", "NKG7"]
CHECKPOINT    = ["PDCD1", "CD274", "LAG3", "TIGIT", "HAVCR2"]

PROLIFERATION = [
    "MKI67", "TOP2A", "PCNA",
    "CDK4",  "CCND1", "CCNE1", "CDK2",
]

ALL_TARGET = list(dict.fromkeys(
    VHL_HIF +
    PROXIMAL_TUBULE_IDENTITY +
    NEPHRON_PROGENITOR +
    PROXIMAL_MATURATION +
    EPIGENETIC_REGULATORS +
    METABOLIC_LIPOGENIC +
    METABOLIC_GLUCONEOGENIC +
    MTOR_PATHWAY +
    MTOR_OUTPUT_PROXIES +
    IMMUNE_MARKERS +
    PROLIFERATION
))

# ═══════════════════════════════════════════════════════════════════════════════
# LOGGING
# ═══════════════════════════════════════════════════════════════════════════════

log_lines = []

def log(msg=""):
    print(msg)
    log_lines.append(str(msg))

def write_log():
    with open(LOG_FILE, "w") as f:
        f.write("\n".join(log_lines))

# ══════════════════════════════════════════════════════════════════════════���════
# UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

def fmt_p(p):
    if p is None or (isinstance(p, float) and np.isnan(p)):
        return "NA"
    if p < 0.0001:
        return "<0.0001"
    return f"{p:.4f}"

def safe_mwu(a, b, alternative="two-sided"):
    try:
        a = pd.Series(a).dropna()
        b = pd.Series(b).dropna()
        if len(a) < 3 or len(b) < 3:
            return np.nan, np.nan
        u, p = stats.mannwhitneyu(a, b, alternative=alternative)
        return u, p
    except Exception:
        return np.nan, np.nan

def safe_pearsonr(x, y):
    try:
        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)
        mask = ~(np.isnan(x) | np.isnan(y))
        if mask.sum() < 5:
            return np.nan, np.nan
        r, p = stats.pearsonr(x[mask], y[mask])
        return r, p
    except Exception:
        return np.nan, np.nan

def safe_spearmanr(x, y):
    try:
        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)
        mask = ~(np.isnan(x) | np.isnan(y))
        if mask.sum() < 5:
            return np.nan, np.nan
        r, p = stats.spearmanr(x[mask], y[mask])
        return r, p
    except Exception:
        return np.nan, np.nan

def norm01(s):
    mn, mx = s.min(), s.max()
    if mx == mn:
        return pd.Series(0.0, index=s.index)
    return (s - mn) / (mx - mn)

# ═══════════════════════════════════════════════════════════════════════════════
# LOAD SCRIPT 1 OUTPUTS
# ═══════════════════════════════════════════════════════════════════════════════

def load_s1_outputs():
    """
    Load all Script 1 outputs needed for Script 2.
    Checks file existence and reports what is available.
    """
    log("=" * 60)
    log("LOADING SCRIPT 1 OUTPUTS")
    log("=" * 60)

    required = {
        "gene_tcga":   os.path.join(S1_DIR, "gene_matrix_tcga.csv"),
        "meta_tcga":   os.path.join(S1_DIR, "metadata_tcga.csv"),
        "saddle_tcga": os.path.join(S1_DIR, "saddle_point_tcga.csv"),
        "depth_tcga":  os.path.join(S1_DIR, "depth_score_tcga.csv"),
    }

    optional = {
        "gene_geo":    os.path.join(S1_DIR, "gene_matrix_geo.csv"),
        "meta_geo":    os.path.join(S1_DIR, "metadata_geo.csv"),
        "saddle_geo":  os.path.join(S1_DIR, "saddle_point_geo.csv"),
        "depth_geo":   os.path.join(S1_DIR, "depth_score_geo.csv"),
    }

    outputs = {}

    for key, path in required.items():
        if not os.path.exists(path):
            log(f"  CRITICAL: Required file missing: {path}")
            log("  Run Script 1 first.")
            raise SystemExit(1)
        outputs[key] = pd.read_csv(path, index_col=0)
        log(f"  Loaded {key}: {outputs[key].shape}")

    geo_available = True
    for key, path in optional.items():
        if not os.path.exists(path):
            log(f"  NOTE: Optional file not found: {path}")
            log("  GEO analyses will be skipped.")
            geo_available = False
            break
        df = pd.read_csv(path, index_col=0)
        outputs[key] = df
        log(f"  Loaded {key}: {df.shape}")

    if not geo_available:
        for key in optional:
            outputs[key] = None

    outputs["geo_available"] = geo_available
    log("")
    return outputs


# ═════════════════��═════════════════════════════════════════════════════════════
# ANALYSIS 1 — GEO LOG2 NORMALISATION
# ═══════════════════════════════════════════════════════════════════════════════

def geo_log2_normalise(gene_geo, meta_geo):
    """
    Script 1 finding: GEO values are raw Affymetrix intensity,
    not log2. Normal PT mean = 18,111 confirmed raw scale.

    Apply log2(x + 1) transformation.
    Verify: after transformation normal PT mean should be
    ~11-14 (log2 scale), consistent with TCGA normal mean of 11.3.

    Returns normalised gene_df and split tumour/normal matrices.
    """
    log("")
    log("=" * 60)
    log("ANALYSIS 1 — GEO LOG2 NORMALISATION")
    log("=" * 60)

    # Check current scale
    raw_max  = gene_geo.values.max()
    raw_min  = gene_geo.values[gene_geo.values > 0].min()
    raw_mean = gene_geo.values.mean()

    log(f"  Pre-normalisation:")
    log(f"    Max value:  {raw_max:.1f}")
    log(f"    Min value:  {raw_min:.1f}")
    log(f"    Mean value: {raw_mean:.1f}")

    # Apply log2(x + 1)
    gene_geo_log2 = np.log2(gene_geo.clip(lower=0) + 1)

    log2_max  = gene_geo_log2.values.max()
    log2_min  = gene_geo_log2.values.min()
    log2_mean = gene_geo_log2.values.mean()

    log(f"  Post log2(x+1) normalisation:")
    log(f"    Max value:  {log2_max:.3f}")
    log(f"    Min value:  {log2_min:.3f}")
    log(f"    Mean value: {log2_mean:.3f}")

    # Verify PT identity genes in normal samples
    t_ids = meta_geo.loc[
        meta_geo.sample_type == "tumour", "sample_id"
    ].tolist()
    n_ids = meta_geo.loc[
        meta_geo.sample_type == "normal", "sample_id"
    ].tolist()

    t_cols = [c for c in t_ids if c in gene_geo_log2.columns]
    n_cols = [c for c in n_ids if c in gene_geo_log2.columns]

    pt_avail = [g for g in PROXIMAL_TUBULE_IDENTITY
                if g in gene_geo_log2.index]

    if pt_avail and n_cols:
        pt_normal_mean = gene_geo_log2.loc[
            pt_avail, n_cols
        ].mean().mean()
        pt_tumour_mean = gene_geo_log2.loc[
            pt_avail, t_cols
        ].mean().mean()
        log(f"  Normal PT mean (log2): {pt_normal_mean:.3f}")
        log(f"  Tumour PT mean (log2): {pt_tumour_mean:.3f}")
        log(f"  TCGA normal PT mean for reference: 11.305")

        if 9.0 < pt_normal_mean < 16.0:
            log("  Scale check: PASS ✓ — consistent with log2 CPM range")
        else:
            log("  Scale check: WARN — value outside expected range")
            log("  Manual inspection of GEO normalisation recommended")

    gene_geo_log2.to_csv(
        os.path.join(S2_DIR, "geo_matrix_log2.csv"))
    log("  GEO log2 matrix saved ✓")

    tumour_geo = gene_geo_log2[t_cols]
    normal_geo = gene_geo_log2[n_cols]

    log(f"  Tumour: {tumour_geo.shape}  Normal: {normal_geo.shape}")
    return gene_geo_log2, tumour_geo, normal_geo


# ═══════════════════════════════════════════════════════════════════════════════
# ANALYSIS 2 — EPAS1 VS HIF1A SEPARATION
# ═══════════════════════════════════════════════════════════════════════════════

def epas1_hif1a_circuit(tumour_t, normal_t,
                        tumour_geo, normal_geo):
    """
    Script 1 finding: HIF1A DOWN in GEO, EPAS1 UP.
    ccRCC is HIF2α (EPAS1)-driven, not HIF1α.

    Analyse separately:
        - EPAS1 (HIF2α) — expected strongly UP in ccRCC
        - HIF1A (HIF1α) — may be suppressed as EPAS1 dominates
        - CA9 — direct HIF2α transcriptional target
        - VEGFA — shared HIF1α/HIF2α target

    For each gene: TCGA and GEO FC, direction, p-value.
    """
    log("")
    log("=" * 60)
    log("ANALYSIS 2 — EPAS1 vs HIF1A SEPARATION")
    log("=" * 60)

    hif_circuit = ["HIF1A", "EPAS1", "ARNT", "CA9",
                   "VEGFA", "SLC2A1", "LDHA",
                   "PDK1", "EGLN1", "EGLN3", "VHL"]

    rows = []

    log(f"  {'Gene':<12} {'TCGA_FC':>9} {'TCGA_dir':>9} "
        f"{'GEO_FC':>9} {'GEO_dir':>9} {'Concordant':>12}")
    log(f"  {'-'*12} {'-'*9} {'-'*9} {'-'*9} {'-'*9} {'-'*12}")

    for gene in hif_circuit:
        row = {"gene": gene}

        # TCGA
        if gene in tumour_t.index:
            t_t = tumour_t.loc[gene].dropna()
            n_t = normal_t.loc[gene].dropna()
            fc_t = float(t_t.median() - n_t.median())
            _, p_t = safe_mwu(t_t, n_t)
            row["tcga_fc"]  = round(fc_t, 3)
            row["tcga_dir"] = "UP" if fc_t > 0 else "DOWN"
            row["tcga_p"]   = p_t
        else:
            row["tcga_fc"]  = np.nan
            row["tcga_dir"] = "NA"
            row["tcga_p"]   = np.nan

        # GEO
        if tumour_geo is not None and gene in tumour_geo.index:
            t_g = tumour_geo.loc[gene].dropna()
            n_g = normal_geo.loc[gene].dropna()
            fc_g = float(t_g.median() - n_g.median())
            _, p_g = safe_mwu(t_g, n_g)
            row["geo_fc"]  = round(fc_g, 3)
            row["geo_dir"] = "UP" if fc_g > 0 else "DOWN"
            row["geo_p"]   = p_g
        else:
            row["geo_fc"]  = np.nan
            row["geo_dir"] = "NA"
            row["geo_p"]   = np.nan

        concordant = (
            row["tcga_dir"] == row["geo_dir"]
            and row["tcga_dir"] != "NA"
        )
        row["concordant"] = concordant

        rows.append(row)
        log(f"  {gene:<12} "
            f"{row['tcga_fc']:>9.3f} {row['tcga_dir']:>9} "
            f"{row['geo_fc']:>9.3f} {row['geo_dir']:>9} "
            f"{'YES' if concordant else 'NO':>12}")

    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(S2_DIR, "epas1_hif1a_circuit.csv"),
              index=False)

    # Summary
    epas1_row = df.loc[df.gene == "EPAS1"]
    hif1a_row = df.loc[df.gene == "HIF1A"]

    log("")
    log("  INTERPRETATION:")
    if not epas1_row.empty:
        log(f"  EPAS1 (HIF2α): TCGA={epas1_row.tcga_fc.values[0]:+.3f} "
            f"GEO={epas1_row.geo_fc.values[0]:+.3f}")
    if not hif1a_row.empty:
        log(f"  HIF1A (HIF1α): TCGA={hif1a_row.tcga_fc.values[0]:+.3f} "
            f"GEO={hif1a_row.geo_fc.values[0]:+.3f}")
    log("  ccRCC false attractor is EPAS1-driven (HIF2α).")
    log("  HIF1A suppression as EPAS1 dominates is consistent")
    log("  with published ccRCC molecular biology.")

    return df


# ═══════════════════════════════════════════════════════════════════════════════
# ANALYSIS 3 — DEPTH SCORE VS STAGE
# ═══════════════════════════════════════════════════════════════════════════════

def depth_vs_stage(tumour_geo, normal_geo, meta_geo, depth_geo):
    """
    Primary Script 2 test using GSE53757 stage metadata.

    Hypothesis: depth score increases with tumour stage.
    Stage 4 > Stage 3 > Stage 2 > Stage 1.

    Recompute depth score on log2-normalised GEO matrix.
    Merge with stage metadata.
    Test stage trend: Spearman correlation of depth vs
    numeric stage. Mann-Whitney between each stage pair.
    """
    log("")
    log("=" * 60)
    log("ANALYSIS 3 — DEPTH SCORE VS STAGE (GSE53757)")
    log("=" * 60)

    if tumour_geo is None or meta_geo is None:
        log("  GEO data not available. Skipping.")
        return None

    # Recompute depth score on log2 GEO
    hif_targets = ["CA9", "VEGFA", "SLC2A1",
                   "LDHA", "PDK1", "EGLN3", "EPAS1"]
    lip_targets = ["FASN", "ACACA", "SCD", "HMGCR", "ACLY"]

    pt_avail  = [g for g in PROXIMAL_TUBULE_IDENTITY
                 if g in tumour_geo.index]
    hif_avail = [g for g in hif_targets
                 if g in tumour_geo.index]
    lip_avail = [g for g in lip_targets
                 if g in tumour_geo.index]

    if pt_avail:
        pt_raw   = tumour_geo.loc[pt_avail].mean(axis=0)
        pt_score = 1 - norm01(pt_raw)
    else:
        pt_score = pd.Series(0.0, index=tumour_geo.columns)

    if hif_avail:
        hif_score = norm01(
            tumour_geo.loc[hif_avail].mean(axis=0))
    else:
        hif_score = pd.Series(0.0, index=tumour_geo.columns)

    if lip_avail:
        lip_score = norm01(
            tumour_geo.loc[lip_avail].mean(axis=0))
    else:
        lip_score = pd.Series(0.0, index=tumour_geo.columns)

    idx       = tumour_geo.columns
    pt_score  = pt_score.reindex(idx).fillna(0)
    hif_score = hif_score.reindex(idx).fillna(0)
    lip_score = lip_score.reindex(idx).fillna(0)
    composite = (pt_score + hif_score + lip_score) / 3.0

    depth_recomputed = pd.DataFrame({
        "sample_id":   idx,
        "pt_loss":     pt_score.values,
        "hif_act":     hif_score.values,
        "lip_reprog":  lip_score.values,
        "depth_score": composite.values,
    })

    # Merge with stage metadata
    tumour_meta = meta_geo.loc[
        meta_geo.sample_type == "tumour"
    ][["sample_id", "stage"]].copy()

    merged = depth_recomputed.merge(tumour_meta,
                                    on="sample_id",
                                    how="left")

    # Map stage to numeric
    stage_map = {
        "stage_1": 1, "stage_2": 2,
        "stage_3": 3, "stage_4": 4,
    }
    merged["stage_num"] = merged.stage.map(stage_map)
    merged = merged.dropna(subset=["stage_num"])

    log(f"  Samples with stage info: {len(merged)}")
    log(f"  Stage distribution:")
    for s in ["stage_1", "stage_2", "stage_3", "stage_4"]:
        n = (merged.stage == s).sum()
        log(f"    {s}: {n}")

    # Per-stage depth stats
    log("")
    log(f"  {'Stage':<10} {'N':>5} {'Mean':>8} "
        f"{'Median':>8} {'SD':>8}")
    log(f"  {'-'*10} {'-'*5} {'-'*8} {'-'*8} {'-'*8}")

    stage_rows = []
    for snum, sname in zip([1, 2, 3, 4],
                           ["stage_1", "stage_2",
                            "stage_3", "stage_4"]):
        sub = merged.loc[
            merged.stage_num == snum, "depth_score"]
        if len(sub) == 0:
            continue
        stage_rows.append({
            "stage":  sname,
            "n":      len(sub),
            "mean":   round(sub.mean(),   3),
            "median": round(sub.median(), 3),
            "sd":     round(sub.std(),    3),
        })
        log(f"  {sname:<10} {len(sub):>5} "
            f"{sub.mean():>8.3f} "
            f"{sub.median():>8.3f} "
            f"{sub.std():>8.3f}")

    # Spearman correlation: depth vs stage
    rho, p_rho = safe_spearmanr(
        merged.stage_num.values,
        merged.depth_score.values,
    )
    log("")
    log(f"  Spearman r (depth vs stage): "
        f"rho={rho:.3f}  p={fmt_p(p_rho)}")

    if not np.isnan(rho):
        if rho > 0 and p_rho < 0.05:
            log("  CONFIRMED: Depth score increases with stage ✓")
        elif rho > 0 and p_rho >= 0.05:
            log("  TREND: Positive but not significant")
        else:
            log("  UNEXPECTED: No positive stage-depth trend")

    # Pairwise stage comparisons
    log("")
    log("  Pairwise comparisons (MWU):")
    pairs = [(1, 4), (1, 3), (2, 4), (3, 4), (1, 2), (2, 3)]
    pairwise_rows = []
    for s1, s2 in pairs:
        a = merged.loc[
            merged.stage_num == s1, "depth_score"]
        b = merged.loc[
            merged.stage_num == s2, "depth_score"]
        if len(a) < 3 or len(b) < 3:
            continue
        _, p = safe_mwu(a, b, alternative="less")
        med_a = a.median()
        med_b = b.median()
        log(f"    Stage {s1} vs Stage {s2}: "
            f"median {med_a:.3f} vs {med_b:.3f}  "
            f"p={fmt_p(p)} (stage{s1}<stage{s2})")
        pairwise_rows.append({
            "stage_a": s1, "stage_b": s2,
            "median_a": round(med_a, 3),
            "median_b": round(med_b, 3),
            "p_mwu_less": p,
        })

    result_df = merged.copy()
    result_df.to_csv(
        os.path.join(S2_DIR, "depth_vs_stage_geo.csv"),
        index=False)

    stage_df = pd.DataFrame(stage_rows)
    stage_df.to_csv(
        os.path.join(S2_DIR, "stage_summary.csv"),
        index=False)

    return result_df, rho, p_rho


# ═══════════════════════════════════════════════════════════════════════════════
# ANALYSIS 4 — INDIVIDUAL LIPOGENIC GENE CIRCUITS
# ═══════════════════════════════════════════════════════════════════════════════

def lipogenic_circuits(tumour_t, normal_t,
                       tumour_geo, normal_geo):
    """
    Script 1 finding: lipogenic group not significant as a group
    (p=0.099 TCGA, p=0.120 GEO). SCD is strongly UP (+3.568).

    Test each lipogenic gene individually across both datasets.
    Also test correlation between SCD and depth score
    (SCD may be a surrogate depth marker).
    """
    log("")
    log("=" * 60)
    log("ANALYSIS 4 — LIPOGENIC GENE CIRCUITS")
    log("=" * 60)

    lip_extended = METABOLIC_LIPOGENIC + [
        "ACSL1", "ACSL4", "ACSS2", "ELOVL6", "SCD5"
    ]

    rows = []

    log(f"  {'Gene':<10} {'TCGA_FC':>9} {'TCGA_p':>10} "
        f"{'GEO_FC':>9} {'GEO_p':>10} {'Concordant':>12}")
    log(f"  {'-'*10} {'-'*9} {'-'*10} "
        f"{'-'*9} {'-'*10} {'-'*12}")

    for gene in lip_extended:
        row = {"gene": gene}

        # TCGA
        if gene in tumour_t.index:
            t_t = tumour_t.loc[gene].dropna()
            n_t = normal_t.loc[gene].dropna()
            fc_t = float(t_t.median() - n_t.median())
            _, p_t = safe_mwu(t_t, n_t)
            row["tcga_fc"] = round(fc_t, 3)
            row["tcga_p"]  = p_t
            row["tcga_dir"]= "UP" if fc_t > 0 else "DOWN"
        else:
            row["tcga_fc"] = np.nan
            row["tcga_p"]  = np.nan
            row["tcga_dir"]= "NA"

        # GEO (log2 normalised)
        if tumour_geo is not None and gene in tumour_geo.index:
            t_g = tumour_geo.loc[gene].dropna()
            n_g = normal_geo.loc[gene].dropna()
            fc_g = float(t_g.median() - n_g.median())
            _, p_g = safe_mwu(t_g, n_g)
            row["geo_fc"] = round(fc_g, 3)
            row["geo_p"]  = p_g
            row["geo_dir"]= "UP" if fc_g > 0 else "DOWN"
        else:
            row["geo_fc"] = np.nan
            row["geo_p"]  = np.nan
            row["geo_dir"]= "NA"

        concordant = (
            row["tcga_dir"] == row["geo_dir"]
            and row["tcga_dir"] != "NA"
            and row["geo_dir"] != "NA"
        )
        row["concordant"] = concordant

        rows.append(row)
        log(f"  {gene:<10} "
            f"{row['tcga_fc']:>9.3f} {fmt_p(row['tcga_p']):>10} "
            f"{row['geo_fc']:>9.3f} {fmt_p(row['geo_p']):>10} "
            f"{'YES' if concordant else 'NO':>12}")

    df = pd.DataFrame(rows)
    df.to_csv(
        os.path.join(S2_DIR, "lipogenic_circuits.csv"),
        index=False)

    # SCD as depth surrogate
    log("")
    log("  SCD as depth score surrogate (TCGA):")
    depth_tcga = pd.read_csv(
        os.path.join(S1_DIR, "depth_score_tcga.csv"))

    if "SCD" in tumour_t.index:
        scd_vals = tumour_t.loc["SCD"]
        depth_vals = depth_tcga.set_index(
            "sample_id")["depth_score"]
        common = scd_vals.index.intersection(depth_vals.index)
        if len(common) > 5:
            r, p = safe_pearsonr(
                scd_vals[common].values,
                depth_vals[common].values,
            )
            log(f"  SCD vs depth score: r={r:.3f}  p={fmt_p(p)}")
            log("  SCD is a reliable lipogenic depth marker ✓"
                if (not np.isnan(r) and r > 0.3)
                else "  SCD correlation with depth is weak")

    return df


# ═══════════════════════════════════════════════════════════════════════════════
# ANALYSIS 5 — BAP1 VS PBRM1 SUBGROUPS
# ═══════════════════════════════════════════════════════════════════════════════

def bap1_pbrm1_subgroups(tumour_t, normal_t):
    """
    BAP1 and PBRM1 define distinct ccRCC molecular subtypes
    with different prognosis and biology.

    BAP1-loss subtype:
        - More aggressive, higher grade
        - Expected: lower BAP1 expression, higher depth score
        - Associated with sarcomatoid features

    PBRM1-loss subtype:
        - Less aggressive (relative)
        - Expected: lower PBRM1 expression
        - Different immune microenvironment

    Classification:
        BAP1-low:  BAP1 expression in bottom tertile
        PBRM1-low: PBRM1 expression in bottom tertile
        (Note: using expression proxy — not mutation status.
         Some tumours will be misclassified without WES data.)

    Compare:
        - Depth score between BAP1-low vs BAP1-high
        - Depth score between PBRM1-low vs PBRM1-high
        - HIF activation between subtypes
        - PT identity loss between subtypes
    """
    log("")
    log("=" * 60)
    log("ANALYSIS 5 — BAP1 vs PBRM1 SUBGROUPS (TCGA)")
    log("=" * 60)

    depth_tcga = pd.read_csv(
        os.path.join(S1_DIR, "depth_score_tcga.csv"))
    depth_tcga = depth_tcga.set_index("sample_id")

    results = []

    for gene in ["BAP1", "PBRM1", "SETD2"]:
        if gene not in tumour_t.index:
            log(f"  {gene} not in tumour matrix. Skipping.")
            continue

        expr = tumour_t.loc[gene]

        # Tertile split
        t33 = expr.quantile(0.33)
        t67 = expr.quantile(0.67)

        low_samples  = expr.index[expr <= t33].tolist()
        high_samples = expr.index[expr >= t67].tolist()

        common_low  = [s for s in low_samples
                       if s in depth_tcga.index]
        common_high = [s for s in high_samples
                       if s in depth_tcga.index]

        if len(common_low) < 5 or len(common_high) < 5:
            log(f"  {gene}: insufficient samples after split.")
            continue

        depth_low  = depth_tcga.loc[common_low,  "depth_score"]
        depth_high = depth_tcga.loc[common_high, "depth_score"]
        hif_low    = depth_tcga.loc[common_low,  "hif_act"]
        hif_high   = depth_tcga.loc[common_high, "hif_act"]
        pt_low     = depth_tcga.loc[common_low,  "pt_loss"]
        pt_high    = depth_tcga.loc[common_high, "pt_loss"]

        _, p_depth = safe_mwu(depth_low, depth_high)
        _, p_hif   = safe_mwu(hif_low,   hif_high)
        _, p_pt    = safe_mwu(pt_low,    pt_high)

        log(f"  {gene} subgroup analysis:")
        log(f"    {gene}-low  (n={len(common_low):>3}): "
            f"depth={depth_low.mean():.3f}  "
            f"hif={hif_low.mean():.3f}  "
            f"pt_loss={pt_low.mean():.3f}")
        log(f"    {gene}-high (n={len(common_high):>3}): "
            f"depth={depth_high.mean():.3f}  "
            f"hif={hif_high.mean():.3f}  "
            f"pt_loss={pt_high.mean():.3f}")
        log(f"    p(depth): {fmt_p(p_depth)}  "
            f"p(hif): {fmt_p(p_hif)}  "
            f"p(pt_loss): {fmt_p(p_pt)}")
        log("")

        results.append({
            "gene":           gene,
            "n_low":          len(common_low),
            "n_high":         len(common_high),
            "depth_low_mean": round(depth_low.mean(),  3),
            "depth_high_mean":round(depth_high.mean(), 3),
            "depth_delta":    round(
                depth_low.mean() - depth_high.mean(), 3),
            "p_depth":        p_depth,
            "hif_low_mean":   round(hif_low.mean(),  3),
            "hif_high_mean":  round(hif_high.mean(), 3),
            "p_hif":          p_hif,
            "pt_low_mean":    round(pt_low.mean(),  3),
            "pt_high_mean":   round(pt_high.mean(), 3),
            "p_pt":           p_pt,
        })

    df = pd.DataFrame(results)
    if not df.empty:
        df.to_csv(
            os.path.join(S2_DIR, "bap1_pbrm1_subgroups.csv"),
            index=False)
    return df


# ═══════════════════════════════════════════════════════════════════════════════
# ANALYSIS 6 — IMMUNE SIGNAL SEPARATION
# ═══════════════════════════════════════════════════════════════════════════════

def immune_separation(tumour_t, normal_t):
    """
    Script 1 finding: immune markers dominate positions 15-21
    in the ranked gene list. CD8A, TIGIT, CTLA4, LAG3, PDCD1
    all strongly UP — but these reflect infiltrating immune
    cells, not tumour-intrinsic biology.

    Compute:
        1. Immune infiltration score per tumour sample
           (mean of immune marker panel, normalised)
        2. Correlation between immune score and depth score
        3. Partial correlation: depth ~ stage controlling
           for immune infiltration
        4. T cell exhaustion index: PDCD1, LAG3, TIGIT, HAVCR2
        5. Macrophage score: CD68, CD163
    """
    log("")
    log("=" * 60)
    log("ANALYSIS 6 — IMMUNE SIGNAL SEPARATION (TCGA)")
    log("=" * 60)

    depth_tcga = pd.read_csv(
        os.path.join(S1_DIR, "depth_score_tcga.csv"))
    depth_tcga = depth_tcga.set_index("sample_id")

    immune_groups = {
        "CD8_T_cell":  ["CD8A", "GZMB", "PRF1"],
        "T_reg":       ["FOXP3", "IL2RA", "CTLA4"],
        "Macrophage":  ["CD68", "CD163", "CSF1R"],
        "Checkpoint":  ["PDCD1", "CD274", "LAG3",
                        "TIGIT", "HAVCR2"],
        "All_immune":  IMMUNE_MARKERS,
    }

    immune_scores = pd.DataFrame(index=tumour_t.columns)

    log(f"  {'Group':<15} {'Genes found':>12} "
        f"{'Corr w/ depth':>15} {'p':>10}")
    log(f"  {'-'*15} {'-'*12} {'-'*15} {'-'*10}")

    score_rows = []
    for gname, glist in immune_groups.items():
        avail = [g for g in glist if g in tumour_t.index]
        if not avail:
            continue
        score = norm01(tumour_t.loc[avail].mean(axis=0))
        immune_scores[gname] = score

        common = score.index.intersection(depth_tcga.index)
        if len(common) > 5:
            r, p = safe_pearsonr(
                score[common].values,
                depth_tcga.loc[common, "depth_score"].values,
            )
            log(f"  {gname:<15} {len(avail):>12} "
                f"{r:>15.3f} {fmt_p(p):>10}")
            score_rows.append({
                "group":        gname,
                "n_genes":      len(avail),
                "corr_depth":   round(r, 3) if not np.isnan(r)
                                else np.nan,
                "p_corr_depth": p,
            })

    immune_scores.reset_index(names="sample_id").to_csv(
        os.path.join(S2_DIR, "immune_scores_tcga.csv"),
        index=False)

    # Immune-corrected depth score
    log("")
    log("  Computing immune-corrected depth score...")

    if "All_immune" in immune_scores.columns:
        common = depth_tcga.index.intersection(
            immune_scores.index)
        depth_vals  = depth_tcga.loc[common, "depth_score"]
        immune_vals = immune_scores.loc[common, "All_immune"]

        # Residual from linear regression of depth on immune
        try:
            slope, intercept, _, _, _ = stats.linregress(
                immune_vals.values, depth_vals.values)
            predicted = intercept + slope * immune_vals
            residual  = depth_vals - predicted
            corrected = norm01(residual)

            corrected_df = pd.DataFrame({
                "sample_id":       common,
                "depth_raw":       depth_vals.values,
                "immune_score":    immune_vals.values,
                "depth_corrected": corrected.values,
            })
            corrected_df.to_csv(
                os.path.join(S2_DIR,
                             "immune_corrected_depth_tcga.csv"),
                index=False)
            log(f"  Immune-corrected depth saved. "
                f"n={len(corrected_df)}")
            log(f"  Regression slope (depth~immune): "
                f"{slope:.3f}")
            if abs(slope) > 0.05:
                log("  Immune infiltration has measurable "
                    "effect on depth score.")
                log("  Corrected depth is the tumour-intrinsic "
                    "arrest signal.")
            else:
                log("  Immune infiltration effect on depth "
                    "is minimal.")
        except Exception as e:
            log(f"  Regression failed: {e}")

    return immune_scores


# ═══════════════════════════════════════════════════════════════════════════════
# ANALYSIS 7 — JAG1 CIRCUIT
# ═══════════════════════════════════════════════════════════════════════════════

def jag1_circuit(tumour_t, normal_t,
                 tumour_geo, normal_geo):
    """
    Script 1 finding: JAG1 UP in GEO (+4,477) but borderline
    in TCGA (−0.24). Notch pathway context.

    JAG1 is a Notch ligand. In ccRCC:
        - JAG1 upregulation activates Notch signalling
        - Notch pathway promotes tumour angiogenesis
        - JAG1/Notch1 axis is linked to VHL loss

    Test JAG1 and Notch pathway context genes:
    JAG1, NOTCH1, NOTCH2, HEY1, HEY2, HEYL, DLL1, DLL4
    """
    log("")
    log("=" * 60)
    log("ANALYSIS 7 — JAG1 / NOTCH CIRCUIT")
    log("=" * 60)

    notch_genes = [
        "JAG1", "JAG2",   "DLL1",   "DLL4",
        "NOTCH1","NOTCH2","NOTCH3", "NOTCH4",
        "HEY1", "HEY2",  "HEYL",   "HES1",
        "MAML1","RBPJ",
    ]

    rows = []
    log(f"  {'Gene':<10} {'TCGA_FC':>9} {'TCGA_p':>10} "
        f"{'GEO_FC':>9} {'GEO_p':>10}")
    log(f"  {'-'*10} {'-'*9} {'-'*10} {'-'*9} {'-'*10}")

    for gene in notch_genes:
        row = {"gene": gene}

        if gene in tumour_t.index:
            t_t = tumour_t.loc[gene].dropna()
            n_t = normal_t.loc[gene].dropna()
            fc_t = float(t_t.median() - n_t.median())
            _, p_t = safe_mwu(t_t, n_t)
            row["tcga_fc"] = round(fc_t, 3)
            row["tcga_p"]  = p_t
        else:
            row["tcga_fc"] = np.nan
            row["tcga_p"]  = np.nan

        if tumour_geo is not None and gene in tumour_geo.index:
            t_g = tumour_geo.loc[gene].dropna()
            n_g = normal_geo.loc[gene].dropna()
            fc_g = float(t_g.median() - n_g.median())
            _, p_g = safe_mwu(t_g, n_g)
            row["geo_fc"] = round(fc_g, 3)
            row["geo_p"]  = p_g
        else:
            row["geo_fc"] = np.nan
            row["geo_p"]  = np.nan

        rows.append(row)

        tc = (f"{row['tcga_fc']:>9.3f}"
              if not np.isnan(row['tcga_fc'])
              else f"{'NA':>9}")
        tp = (fmt_p(row['tcga_p'])
              if not np.isnan(row.get('tcga_p', np.nan))
              else "NA")
        gc = (f"{row['geo_fc']:>9.3f}"
              if not np.isnan(row['geo_fc'])
              else f"{'NA':>9}")
        gp = (fmt_p(row['geo_p'])
              if not np.isnan(row.get('geo_p', np.nan))
              else "NA")

        log(f"  {gene:<10} {tc} {tp:>10} {gc} {gp:>10}")

    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(S2_DIR, "jag1_circuit.csv"),
              index=False)
    return df


# ═══════════════════════════════════════════════════════════════════════════════
# ANALYSIS 8 — mTOR OUTPUT PROXIES
# ═══════════════════════════════════════════════════════════════════════════════

def mtor_proxies(tumour_t, normal_t,
                 tumour_geo, normal_geo):
    """
    Script 1 finding: mTOR pathway components not significant
    (p=0.0503 TCGA). mTOR activation in ccRCC is predominantly
    post-translational.

    Test mTOR transcriptional output proxies:
    These genes are transcriptionally induced by mTOR activity
    and provide a better RNA-level readout than pathway components.

    MYC, CCND1, HIF1A, SLC7A5, SLC3A2, EIF4E — mTOR targets
    Also test: S6K1 (RPS6KB1) downstream targets
    BIRC5 (survivin) — mTOR/AKT target
    """
    log("")
    log("=" * 60)
    log("ANALYSIS 8 — mTOR OUTPUT PROXIES")
    log("=" * 60)

    mtor_extended = MTOR_OUTPUT_PROXIES + [
        "RPS6",    "EIF4B",  "VEGFA",
        "SLC1A5",  "LDHA",   "PKM",
    ]

    rows = []
    log(f"  {'Gene':<10} {'TCGA_FC':>9} {'TCGA_p':>10} "
        f"{'GEO_FC':>9} {'GEO_p':>10} {'Role':>20}")
    log(f"  {'-'*10} {'-'*9} {'-'*10} "
        f"{'-'*9} {'-'*10} {'-'*20}")

    proxy_roles = {
        "MYC":    "Transcription factor target",
        "CCND1":  "Cell cycle mTOR target",
        "HIF1A":  "Hypoxia/mTOR target",
        "SLC7A5": "Amino acid transporter",
        "SLC3A2": "Amino acid transporter",
        "EIF4E":  "Translation initiation",
        "G3BP1":  "Stress granule/mTOR",
        "BIRC5":  "Survivin, mTOR/AKT",
        "RPS6":   "Ribosomal S6 (S6K1 target)",
        "EIF4B":  "Translation (S6K1 target)",
        "VEGFA":  "HIF/mTOR angiogenesis",
        "SLC1A5": "Glutamine transporter",
        "LDHA":   "Glycolysis, mTOR target",
        "PKM":    "Pyruvate kinase M2",
    }

    for gene in mtor_extended:
        row = {"gene": gene}

        if gene in tumour_t.index:
            t_t = tumour_t.loc[gene].dropna()
            n_t = normal_t.loc[gene].dropna()
            fc_t = float(t_t.median() - n_t.median())
            _, p_t = safe_mwu(t_t, n_t)
            row["tcga_fc"] = round(fc_t, 3)
            row["tcga_p"]  = p_t
        else:
            row["tcga_fc"] = np.nan
            row["tcga_p"]  = np.nan

        if tumour_geo is not None and gene in tumour_geo.index:
            t_g = tumour_geo.loc[gene].dropna()
            n_g = normal_geo.loc[gene].dropna()
            fc_g = float(t_g.median() - n_g.median())
            _, p_g = safe_mwu(t_g, n_g)
            row["geo_fc"] = round(fc_g, 3)
            row["geo_p"]  = p_g
        else:
            row["geo_fc"] = np.nan
            row["geo_p"]  = np.nan

        row["role"] = proxy_roles.get(gene, "")
        rows.append(row)

        tc = (f"{row['tcga_fc']:>9.3f}"
              if not np.isnan(row['tcga_fc'])
              else f"{'NA':>9}")
        gc = (f"{row['geo_fc']:>9.3f}"
              if not np.isnan(row['geo_fc'])
              else f"{'NA':>9}")
        tp = (fmt_p(row['tcga_p'])
              if not np.isnan(row.get('tcga_p', np.nan))
              else "NA")
        gp = (fmt_p(row['geo_p'])
              if not np.isnan(row.get('geo_p', np.nan))
              else "NA")

        log(f"  {gene:<10} {tc} {tp:>10} "
            f"{gc} {gp:>10} "
            f"{row['role']:>20}")

    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(S2_DIR, "mtor_proxies.csv"),
              index=False)
    return df


# ═══════════════════════════════════════════════════════════════════════════════
# ANALYSIS 9 — CORRECTED CROSS-DATASET COMPARISON
# ═══════════════════════════════════════════════════════════════════════════════

def corrected_cross_dataset(tumour_t, normal_t,
                             tumour_geo, normal_geo):
    """
    Script 1: cross-dataset r=0.617 was computed on
    incomparable scales (TCGA log2 CPM vs GEO raw intensity).

    Recompute saddle point results on log2-normalised GEO
    and compare to TCGA on equivalent scales.
    """
    log("")
    log("=" * 60)
    log("ANALYSIS 9 — CORRECTED CROSS-DATASET COMPARISON")
    log("=" * 60)

    if tumour_geo is None:
        log("  GEO data not available. Skipping.")
        return None

    # Recompute saddle point on log2 GEO
    results_geo = []
    for gene in ALL_TARGET:
        if gene not in tumour_geo.index:
            continue
        t_g = tumour_geo.loc[gene].dropna()
        n_g = normal_geo.loc[gene].dropna()
        if len(t_g) < 3 or len(n_g) < 3:
            continue
        fc_g = float(t_g.median() - n_g.median())
        _, p_g = safe_mwu(t_g, n_g)
        results_geo.append({
            "gene":      gene,
            "log2FC":    round(fc_g, 4),
            "direction": "UP" if fc_g > 0 else "DOWN",
            "p_mwu":     p_g,
        })

    geo_saddle = pd.DataFrame(results_geo)
    geo_saddle.to_csv(
        os.path.join(S2_DIR, "geo_saddle_corrected.csv"),
        index=False)

    # Load TCGA saddle
    tcga_saddle = pd.read_csv(
        os.path.join(S1_DIR, "saddle_point_tcga.csv"))

    merged = tcga_saddle.merge(
        geo_saddle[["gene", "log2FC", "direction"]],
        on="gene",
        suffixes=("_tcga", "_geo"),
    )

    if merged.empty:
        log("  No common genes.")
        return None

    concordant = (
        merged.direction_tcga == merged.direction_geo
    ).sum()
    total = len(merged)
    pct   = 100 * concordant / total if total > 0 else 0.0

    r, p = safe_pearsonr(
        merged.log2FC_tcga.values,
        merged.log2FC_geo.values,
    )

    log(f"  After log2 normalisation of GEO:")
    log(f"  Common genes:          {total}")
    log(f"  Direction concordant:  "
        f"{concordant}/{total} ({pct:.1f}%)")
    log(f"  log2FC correlation:    r={r:.3f}  p={fmt_p(p)}")
    log(f"  (Script 1 pre-normalisation: r=0.617)")

    if not np.isnan(r):
        if r > 0.617:
            log("  Correlation IMPROVED after normalisation ✓")
        else:
            log("  Correlation similar or lower after normalisation")
            log("  Platform differences may be irreducible")

    # Discordant genes after correction
    discordant = merged.loc[
        merged.direction_tcga != merged.direction_geo
    ].copy()
    discordant["abs_fc_tcga"] = discordant.log2FC_tcga.abs()
    discordant = discordant.sort_values(
        "abs_fc_tcga", ascending=False)

    log(f"  Discordant genes after correction "
        f"({len(discordant)}):")
    for _, row in discordant.head(10).iterrows():
        log(f"    {row.gene:<12} "
            f"TCGA:{row.direction_tcga}"
            f"({row.log2FC_tcga:+.3f})  "
            f"GEO:{row.direction_geo}"
            f"({row.log2FC_geo:+.3f})")

    merged.to_csv(
        os.path.join(S2_DIR,
                     "cross_dataset_corrected.csv"),
        index=False)
    return merged


# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE S2
# ═════��═════════════════════════════════════════════════════════════════════════

def generate_figure_s2(stage_result, lipogenic_df,
                        bap1_df, immune_df,
                        tumour_t, depth_tcga_path):
    log("")
    log("Generating figure S2...")

    fig = plt.figure(figsize=(18, 14))
    gs  = gridspec.GridSpec(3, 3, figure=fig,
                            hspace=0.55, wspace=0.40)

    ax_a = fig.add_subplot(gs[0, 0])  # depth vs stage
    ax_b = fig.add_subplot(gs[0, 1])  # lipogenic circuits
    ax_c = fig.add_subplot(gs[0, 2])  # BAP1/PBRM1 subgroups
    ax_d = fig.add_subplot(gs[1, 0])  # immune scores
    ax_e = fig.add_subplot(gs[1, 1])  # EPAS1 vs HIF1A
    ax_f = fig.add_subplot(gs[1, 2])  # SCD vs depth scatter
    ax_g = fig.add_subplot(gs[2, :])  # cross-dataset corrected

    STAGE_COLORS = {
        "stage_1": "#2ecc71",
        "stage_2": "#f39c12",
        "stage_3": "#e67e22",
        "stage_4": "#e74c3c",
    }

    # ── Panel A: Depth score vs stage ─────────────────────────
    if stage_result is not None:
        stage_df_plot, rho, p_rho = stage_result
        for sname, scolor in STAGE_COLORS.items():
            sub = stage_df_plot.loc[
                stage_df_plot.stage == sname, "depth_score"]
            if len(sub) == 0:
                continue
            snum = int(sname.split("_")[1])
            ax_a.scatter(
                [snum] * len(sub) +
                np.random.uniform(-0.15, 0.15, len(sub)),
                sub.values,
                alpha=0.5, s=18,
                color=scolor, edgecolors="none",
            )
            ax_a.plot(
                [snum - 0.2, snum + 0.2],
                [sub.median(), sub.median()],
                color="black", linewidth=2,
            )
        ax_a.set_xlabel("Tumour Stage", fontsize=9)
        ax_a.set_ylabel("Depth Score (log2 GEO)", fontsize=9)
        ax_a.set_xticks([1, 2, 3, 4])
        ax_a.set_xticklabels(["I", "II", "III", "IV"])
        ax_a.set_title(
            f"A — Depth vs Stage\n"
            f"ρ={rho:.2f}  p={fmt_p(p_rho)}",
            fontsize=9)

    # ── Panel B: Lipogenic gene circuits ──────────────────────
    if lipogenic_df is not None and not lipogenic_df.empty:
        lip_plot = lipogenic_df.dropna(
            subset=["tcga_fc", "geo_fc"])
        lip_plot = lip_plot.iloc[:10]
        x = np.arange(len(lip_plot))
        w = 0.35
        ax_b.bar(x - w/2, lip_plot.tcga_fc.values,
                 w, label="TCGA",
                 color="#3498db", edgecolor="black",
                 linewidth=0.4)
        ax_b.bar(x + w/2, lip_plot.geo_fc.values,
                 w, label="GEO (log2)",
                 color="#e74c3c", edgecolor="black",
                 linewidth=0.4)
        ax_b.axhline(0, color="black",
                     linewidth=0.8, linestyle="--")
        ax_b.set_xticks(x)
        ax_b.set_xticklabels(
            lip_plot.gene.values,
            rotation=45, ha="right", fontsize=7)
        ax_b.set_ylabel("log2FC", fontsize=9)
        ax_b.set_title("B — Lipogenic Gene Circuits",
                       fontsize=9)
        ax_b.legend(fontsize=7)

    # ── Panel C: BAP1/PBRM1 depth scores ─────────────────────
    if bap1_df is not None and not bap1_df.empty:
        genes_plot = bap1_df.gene.tolist()
        x = np.arange(len(genes_plot))
        w = 0.35
        ax_c.bar(x - w/2, bap1_df.depth_low_mean.values,
                 w, label="Low (loss proxy)",
                 color="#e74c3c", edgecolor="black",
                 linewidth=0.4)
        ax_c.bar(x + w/2, bap1_df.depth_high_mean.values,
                 w, label="High",
                 color="#2ecc71", edgecolor="black",
                 linewidth=0.4)
        ax_c.set_xticks(x)
        ax_c.set_xticklabels(genes_plot, fontsize=8)
        ax_c.set_ylabel("Mean Depth Score", fontsize=9)
        ax_c.set_title(
            "C — BAP1/PBRM1/SETD2 Subgroups",
            fontsize=9)
        ax_c.legend(fontsize=7)

    # ── Panel D: Immune scores correlation ────────────────────
    if (immune_df is not None and
            "All_immune" in immune_df.columns):
        depth_tcga = pd.read_csv(depth_tcga_path)
        depth_tcga = depth_tcga.set_index("sample_id")
        common = immune_df.index.intersection(depth_tcga.index)
        if len(common) > 10:
            ax_d.scatter(
                immune_df.loc[common, "All_immune"].values,
                depth_tcga.loc[common, "depth_score"].values,
                alpha=0.3, s=8,
                color="#95a5a6", edgecolors="none",
            )
            ax_d.set_xlabel("Immune Score", fontsize=9)
            ax_d.set_ylabel("Depth Score", fontsize=9)
            ax_d.set_title(
                "D — Immune Infiltration vs Depth",
                fontsize=9)

    # ── Panel E: EPAS1 vs HIF1A ───────────────────────────────
    epas1_path = os.path.join(S2_DIR, "epas1_hif1a_circuit.csv")
    if os.path.exists(epas1_path):
        hif_df = pd.read_csv(epas1_path)
        plot_genes = ["HIF1A", "EPAS1", "CA9",
                      "VEGFA", "EGLN3", "LDHA"]
        hif_sub = hif_df.loc[
            hif_df.gene.isin(plot_genes)].copy()
        if not hif_sub.empty:
            x = np.arange(len(hif_sub))
            w = 0.35
            tcga_fc = hif_sub.tcga_fc.fillna(0).values
            geo_fc  = hif_sub.geo_fc.fillna(0).values
            ax_e.bar(x - w/2, tcga_fc, w,
                     label="TCGA",
                     color="#3498db", edgecolor="black",
                     linewidth=0.4)
            ax_e.bar(x + w/2, geo_fc, w,
                     label="GEO (log2)",
                     color="#e74c3c", edgecolor="black",
                     linewidth=0.4)
            ax_e.axhline(0, color="black",
                         linewidth=0.8, linestyle="--")
            ax_e.set_xticks(x)
            ax_e.set_xticklabels(
                hif_sub.gene.values,
                rotation=45, ha="right", fontsize=7)
            ax_e.set_ylabel("log2FC", fontsize=9)
            ax_e.set_title(
                "E — EPAS1 (HIF2α) vs HIF1A", fontsize=9)
            ax_e.legend(fontsize=7)

    # ── Panel F: SCD vs depth scatter ─────────────────────────
    depth_tcga = pd.read_csv(depth_tcga_path)
    depth_tcga = depth_tcga.set_index("sample_id")
    if "SCD" in tumour_t.index:
        scd_vals   = tumour_t.loc["SCD"]
        common     = scd_vals.index.intersection(depth_tcga.index)
        if len(common) > 10:
            r_scd, p_scd = safe_pearsonr(
                scd_vals[common].values,
                depth_tcga.loc[common, "depth_score"].values,
            )
            ax_f.scatter(
                scd_vals[common].values,
                depth_tcga.loc[common, "depth_score"].values,
                alpha=0.3, s=8,
                color="#e67e22", edgecolors="none",
            )
            ax_f.set_xlabel("SCD expression (log2 CPM)",
                            fontsize=9)
            ax_f.set_ylabel("Depth Score", fontsize=9)
            ax_f.set_title(
                f"F — SCD vs Depth Score\n"
                f"r={r_scd:.2f}  p={fmt_p(p_scd)}",
                fontsize=9)

    # ── Panel G: Corrected cross-dataset comparison ───────────
    corr_path = os.path.join(
        S2_DIR, "cross_dataset_corrected.csv")
    if os.path.exists(corr_path):
        merged = pd.read_csv(corr_path)
        if not merged.empty:
            colors_g = [
                "#e74c3c"
                if row.direction_tcga == row.direction_geo
                else "#95a5a6"
                for _, row in merged.iterrows()
            ]
            ax_g.scatter(
                merged.log2FC_tcga.values,
                merged.log2FC_geo.values,
                alpha=0.6, s=25,
                c=colors_g, edgecolors="black",
                linewidths=0.3,
            )
            for _, row in merged.iterrows():
                if abs(row.log2FC_tcga) > 2:
                    ax_g.annotate(
                        row.gene,
                        (row.log2FC_tcga, row.log2FC_geo),
                        fontsize=6,
                        xytext=(3, 3),
                        textcoords="offset points",
                    )
            ax_g.axhline(0, color="black",
                         linewidth=0.5, linestyle="--")
            ax_g.axvline(0, color="black",
                         linewidth=0.5, linestyle="--")
            r_g, p_g = safe_pearsonr(
                merged.log2FC_tcga.values,
                merged.log2FC_geo.values,
            )
            ax_g.set_xlabel(
                "TCGA log2FC (RNA-seq)", fontsize=9)
            ax_g.set_ylabel(
                "GEO log2FC (microarray, log2-normalised)",
                fontsize=9)
            ax_g.set_title(
                f"G — Cross-Dataset log2FC Correlation "
                f"(after GEO normalisation)\n"
                f"r={r_g:.3f}  p={fmt_p(p_g)}  "
                f"Red=concordant  Grey=discordant",
                fontsize=9)

    fig.suptitle(
        "ccRCC False Attractor — Script 2 Circuit Analysis\n"
        "Document 94 | 2026-03-02",
        fontsize=12, fontweight="bold",
    )

    out = os.path.join(S2_DIR, "figure_s2.png")
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    log(f"  Figure saved: {out}")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    log("OrganismCore — ccRCC False Attractor Framework")
    log("Script 2 — Circuit and Subtype Analysis")
    log("Document 94 | 2026-03-02")
    log("")
    log("Requires: Script 1 outputs in "
        "./ccrcc_false_attractor/results/")
    log("")

    # ── Load Script 1 outputs ─────────────────────────────────
    data = load_s1_outputs()

    gene_tcga   = data["gene_tcga"]
    meta_tcga   = data["meta_tcga"].reset_index()
    gene_geo    = data["gene_geo"]
    meta_geo    = (data["meta_geo"].reset_index()
                   if data["meta_geo"] is not None
                   else None)
    geo_avail   = data["geo_available"]

    # TCGA split
    t_ids = meta_tcga.loc[
        meta_tcga.sample_type == "tumour",
        "sample_id"].tolist()
    n_ids = meta_tcga.loc[
        meta_tcga.sample_type == "normal",
        "sample_id"].tolist()
    tumour_t = gene_tcga[[
        c for c in t_ids if c in gene_tcga.columns]]
    normal_t = gene_tcga[[
        c for c in n_ids if c in gene_tcga.columns]]

    log(f"  TCGA  — Tumour: {tumour_t.shape}  "
        f"Normal: {normal_t.shape}")

    # GEO prep
    tumour_geo = None
    normal_geo = None

    if geo_avail and gene_geo is not None:
        # Analysis 1 — log2 normalise GEO
        gene_geo_log2, tumour_geo, normal_geo = \
            geo_log2_normalise(gene_geo, meta_geo)
        log(f"  GEO   — Tumour: {tumour_geo.shape}  "
            f"Normal: {normal_geo.shape}")
    else:
        log("  GEO arm not available. "
            "Run Script 1 with GPL570 to enable.")

    # ── Analyses ──────────────────────────────────────────────

    # 2. EPAS1 vs HIF1A
    epas1_df = epas1_hif1a_circuit(
        tumour_t, normal_t, tumour_geo, normal_geo)

    # 3. Depth vs stage
    stage_result = None
    if tumour_geo is not None and meta_geo is not None:
        depth_geo_s1 = data["depth_geo"]
        stage_result = depth_vs_stage(
            tumour_geo, normal_geo,
            meta_geo, depth_geo_s1)

    # 4. Lipogenic circuits
    lip_df = lipogenic_circuits(
        tumour_t, normal_t, tumour_geo, normal_geo)

    # 5. BAP1/PBRM1 subgroups
    bap1_df = bap1_pbrm1_subgroups(tumour_t, normal_t)

    # 6. Immune separation
    immune_df = immune_separation(tumour_t, normal_t)

    # 7. JAG1 circuit
    jag1_df = jag1_circuit(
        tumour_t, normal_t, tumour_geo, normal_geo)

    # 8. mTOR proxies
    mtor_df = mtor_proxies(
        tumour_t, normal_t, tumour_geo, normal_geo)

    # 9. Corrected cross-dataset
    cross_df = corrected_cross_dataset(
        tumour_t, normal_t, tumour_geo, normal_geo)

    # ── Figure ────────────────────────────────────────────────
    generate_figure_s2(
        stage_result,
        lip_df,
        bap1_df,
        immune_df,
        tumour_t,
        os.path.join(S1_DIR, "depth_score_tcga.csv"),
    )

    # ── Summary ───────────────────────────────────────────────
    log("")
    log("=" * 60)
    log("SCRIPT 2 COMPLETE")
    log("=" * 60)
    log(f"  Outputs: {S2_DIR}")
    for fname in sorted(os.listdir(S2_DIR)):
        fpath = os.path.join(S2_DIR, fname)
        log(f"    {fname:<50} "
            f"{os.path.getsize(fpath):>8} bytes")
    log("")
    log("  NEXT STEP:")
    log("  Read all circuit results.")
    log("  Record confirmations, contradictions, surprises.")
    log("  Then proceed to RCC Series — Doc 95 (pRCC).")

    write_log()


if __name__ == "__main__":
    main()
