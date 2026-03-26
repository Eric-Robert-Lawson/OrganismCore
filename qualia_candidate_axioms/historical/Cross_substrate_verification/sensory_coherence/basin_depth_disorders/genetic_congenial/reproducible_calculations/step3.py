"""
STEP 3 — DEEPER ANALYSIS
=====================================================
OC-PSYCHOPATHY-GENETIC-MARKER-DERIVATION-001
Eric Robert Lawson — OrganismCore — 2026-03-26

Inputs (from Step 2):
    1496.txt                    Right UF FA raw data
    1497.txt                    Left  UF FA raw data
    top_hits_right_UF.tsv       GWS hits, right UF FA
    top_hits_left_UF.tsv        GWS hits, left UF FA
    candidate_genes_all_layers.tsv  All candidate gene SNPs
    gwas_ready_instruments.tsv  16 instrument SNPs

What this script computes:

    ANALYSIS 1 — GENOMIC INFLATION DECOMPOSITION
      Lambda GC at multiple p-value quantiles.
      Tests whether inflation is uniform (confounding)
      or concentrated at top hits (polygenicity).
      Uniform inflation = population stratification problem.
      Concentrated at top = genuine polygenic signal.

    ANALYSIS 2 — CHR8 CLUSTER IDENTIFICATION
      5 of 16 GWS loci are on chr8 (8.9M-12.4M).
      Identify what genes/regions are in that cluster.
      Is this a single extended haplotype or multiple
      independent signals?

    ANALYSIS 3 — SEMA3A LOCUS DEEP EXTRACTION
      Extract all SNPs in the SEMA3A GWS signal window.
      Rank by p-value. Identify the conditional structure.
      Which SNP is most likely causal?
      Does the signal localise to SEMA3A body or regulatory?

    ANALYSIS 4 — RIGHT vs LEFT EFFECT SIZE COMPARISON
      At all SNPs significant in either right or left UF FA:
      Plot and quantify beta_R vs beta_L.
      Compute correlation and deviation from identity line.
      SNPs above the identity line = stronger effect on right.
      SNPs below = stronger effect on left.
      Lateralised SNPs = candidates for Layer D signal.

    ANALYSIS 5 — CANDIDATE LAYER ENRICHMENT TEST
      For each layer (A/B/C/D):
      Observed: number of SNPs in window with p < threshold.
      Expected: from matched control windows of same size.
      Permutation test: 1000 random windows matched by
      chr and size, count SNPs below threshold.
      Enrichment ratio = observed / expected.
      This answers: is the Layer A signal above chance?

    ANALYSIS 6 — CROSS-LAYER SIGNAL PROFILE
      For each candidate gene window:
      Distribution of p-values (QQ within window).
      Mean chi-squared vs genome-wide mean.
      This identifies which genes within each layer
      are driving the layer signal.

    ANALYSIS 7 — SLIT2 LOCUS (suggestive, p=1.72e-6)
      The SLIT2 ROBO1 partner. Extract the locus.
      What is the lead SNP? What is its beta?
      Is the effect direction consistent with SEMA3A
      (same pathway, should have concordant direction
      on right UF FA if both are axon guidance)?

Outputs:
    step3_results.txt               Full text report
    chr8_cluster_genes.tsv          Chr8 locus annotation
    sema3a_locus_snps.tsv           SEMA3A fine-mapping SNPs
    right_left_beta_comparison.tsv  All shared GWS SNPs R vs L
    layer_enrichment.tsv            Enrichment test results
    cross_layer_profile.tsv         Per-gene signal profile
    slit2_locus_snps.tsv            SLIT2 locus extraction
"""

import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import chi2
from scipy.special import ndtr

warnings.filterwarnings("ignore")

# ── Input files ────────────────────────────────────────────────────────────────
FILE_R          = "1496.txt"
FILE_L          = "1497.txt"
FILE_HITS_R     = "top_hits_right_UF.tsv"
FILE_HITS_L     = "top_hits_left_UF.tsv"
FILE_CANDIDATES = "candidate_genes_all_layers.tsv"
FILE_INSTRUMENTS= "gwas_ready_instruments.tsv"

# ── Output files ───────────────────────────────────────────────────────────────
OUT_REPORT      = Path("step3_results.txt")
OUT_CHR8        = Path("chr8_cluster_genes.tsv")
OUT_SEMA3A      = Path("sema3a_locus_snps.tsv")
OUT_SLIT2       = Path("slit2_locus_snps.tsv")
OUT_BETA_COMP   = Path("right_left_beta_comparison.tsv")
OUT_ENRICHMENT  = Path("layer_enrichment.tsv")
OUT_LAYER_PROF  = Path("cross_layer_profile.tsv")

# ── Parameters ─────────────────────────────────────────────────────────────────
GWS_THRESH   = 5e-8
SUG_THRESH   = 1e-6
MAX_SE       = 0.5
N_PERM       = 1000     # permutations for enrichment test
RAND_SEED    = 20260326

# ── Chr8 cluster bounds (from Step 2 results) ──────────────────────────────────
CHR8_START = 8_500_000
CHR8_END   = 13_000_000

# ── SEMA3A locus (GWS hit + flanking region) ───────────────────────────────────
SEMA3A_CHR   = "7"
SEMA3A_START = 83_000_000
SEMA3A_END   = 84_500_000

# ── SLIT2 locus ────────────────────────────────────────────────────────────────
SLIT2_CHR   = "4"
SLIT2_START = 19_800_000
SLIT2_END   = 21_600_000

# ── Candidate gene windows (must match Step 2 exactly) ─────────────────────────
GENES = {
    "SEMA3A":  {"chr":"7",  "start": 83294422, "end": 83953344, "layer":"A"},
    "SEMA3D":  {"chr":"7",  "start": 83953344, "end": 84680000, "layer":"A"},
    "ROBO1":   {"chr":"3",  "start": 78421879, "end": 79404206, "layer":"A"},
    "SLIT2":   {"chr":"4",  "start": 20260577, "end": 21094926, "layer":"A"},
    "MBP":     {"chr":"18", "start": 74435940, "end": 75064555, "layer":"B"},
    "MAG":     {"chr":"19", "start": 35171502, "end": 35691199, "layer":"B"},
    "PLP1":    {"chr":"X",  "start":102781428, "end":103310355, "layer":"B"},
    "OXTR":    {"chr":"3",  "start":  8505088, "end":  9021564, "layer":"C"},
    "LRRTM1":  {"chr":"2",  "start":135131311, "end":135649700, "layer":"D"},
    "PCDH11X": {"chr":"X",  "start": 91261878, "end": 92173588, "layer":"D"},
    "CNTNAP2": {"chr":"7",  "start":145813453, "end":148118090, "layer":"D"},
}

# Known genes in the chr8 cluster region for annotation
# (from UCSC/Ensembl GRCh37, chr8:8.5M-13M)
CHR8_KNOWN_GENES = {
    "CSMD1":  {"start":  2_970_000, "end": 10_118_393,
               "note": "CUB and Sushi multiple domains 1 — "
                       "brain-expressed, synapse development, "
                       "implicated in schizophrenia and cognitive traits"},
    "MCPH1":  {"start":  6_520_000, "end":  6_883_639,
               "note": "Microcephalin — brain size, neural progenitor "
                       "cell cycle regulation"},
    "ANGPT2": {"start":  6_319_110, "end":  6_374_709,
               "note": "Angiopoietin-2 — vascular/angiogenic, "
                       "relevant to white matter vascular supply"},
    "ARHGEF10":{"start": 8_000_000, "end":  8_109_000,
                "note": "Rho guanine nucleotide exchange factor 10 — "
                        "axon myelination, Charcot-Marie-Tooth disease"},
    "DLGAP2": {"start": 1_521_200, "end":  2_002_700,
               "note": "Discs large associated protein 2 — "
                       "postsynaptic density, autism risk gene"},
    "NKX6-3": {"start": 10_539_000, "end": 10_544_000,
               "note": "NK6 homeobox 3 — transcription factor"},
    "PINX1":  {"start": 10_600_000, "end": 10_720_000,
               "note": "PIN2/TERF1 interacting telomerase inhibitor"},
    "SLC7A2": {"start": 16_285_000, "end": 16_406_000,
               "note": "Cationic amino acid transporter — "
                       "arginine transport, relevant to NO synthesis"},
}


# ══════════════════════════════════════════════════════════════════════
# UTILITIES
# ══════════════════════════════════════════════════════════════════════

def log(msg, fh=None):
    print(msg)
    if fh:
        fh.write(msg + "\n")
        fh.flush()


def load(filepath, fh):
    p = Path(filepath)
    if not p.exists():
        p = Path(filepath + ".gz")
    log(f"  Loading {p.name}  ({p.stat().st_size/1e6:.0f} MB)...", fh)
    t0 = time.time()
    df = pd.read_csv(
        p,
        sep=r"\s+",
        compression="gzip" if str(p).endswith(".gz") else None,
        dtype={"chr": str, "rsid": str, "pos": np.int32,
               "a1": str, "a2": str,
               "beta": np.float32, "se": np.float32,
               "pval(-log10)": np.float32},
        low_memory=False,
    )
    df.rename(columns={"pval(-log10)": "lp"}, inplace=True)
    df["p"] = 10.0 ** (-df["lp"].clip(upper=300).astype(np.float64))
    df["chr"] = df["chr"].str.lstrip("0").replace("", "0")
    df = df[(df["se"] > 0) & (df["se"] <= MAX_SE)].dropna(
        subset=["beta","se","p"])
    log(f"  {len(df):,} variants  [{time.time()-t0:.1f}s]", fh)
    return df


# ══════════════════════════════════════════════════════════════════════
# ANALYSIS 1 — GENOMIC INFLATION DECOMPOSITION
# ══════════════════════════════════════════════════════════════════════

def inflation_decomposition(df_r, df_l, fh):
    """
    Compute lambda GC at multiple quantile bins.
    If lambda is uniform across quantiles -> confounding.
    If lambda increases at top quantiles -> polygenicity.
    """
    log("\n── ANALYSIS 1: GENOMIC INFLATION DECOMPOSITION ──────────", fh)
    log("  Testing whether inflation is confounding vs polygenicity.", fh)
    log("  Confounding: lambda uniform across p-value quantiles.", fh)
    log("  Polygenicity: lambda larger at top quantiles.", fh)

    results = []
    for label, df in [("Right UF FA", df_r), ("Left UF FA", df_l)]:
        log(f"\n  {label}:", fh)
        log(f"  {'Quantile range':25s} {'N SNPs':>10s} {'Lambda GC':>12s}", fh)
        log(f"  {'─'*50}", fh)

        # Compute chi-squared from p-values
        chisq = chi2.ppf(1 - df["p"].clip(1e-300, 1).values, df=1)
        expected_median = chi2.ppf(0.5, df=1)  # = 0.4549

        # Bin by p-value quantile
        bins = [
            ("Bottom 50% (p>0.5)",      df["p"] > 0.5),
            ("25-50% (0.1<p<0.5)",      (df["p"] > 0.1) & (df["p"] <= 0.5)),
            ("10-25% (0.01<p<0.1)",     (df["p"] > 0.01) & (df["p"] <= 0.1)),
            ("Top 10% (p<0.01)",        df["p"] < 0.01),
            ("Top 1% (p<0.001)",        df["p"] < 0.001),
            ("Top 0.1% (p<1e-4)",       df["p"] < 1e-4),
            ("Top 0.01% (p<1e-5)",      df["p"] < 1e-5),
            ("GWS (p<5e-8)",            df["p"] < 5e-8),
        ]

        row_results = []
        for bin_label, mask in bins:
            sub_chisq = chisq[mask.values]
            if len(sub_chisq) < 10:
                lam = float("nan")
            else:
                lam = float(np.median(sub_chisq) / expected_median)
            log(f"  {bin_label:25s} {mask.sum():>10,} {lam:>12.4f}", fh)
            row_results.append({
                "dataset": label, "quantile": bin_label,
                "n_snps": int(mask.sum()), "lambda_gc": lam
            })
        results.extend(row_results)

    # Interpretation
    log(f"\n  Interpretation:", fh)
    log(f"  If lambda at bottom 50% ~ 1.0 but rises at top 1%:", fh)
    log(f"    -> POLYGENICITY. The trait is genuinely influenced by", fh)
    log(f"       many variants, each with small effect.", fh)
    log(f"    -> The GWS hits are real signals.", fh)
    log(f"  If lambda is uniformly elevated across all quantiles:", fh)
    log(f"    -> CONFOUNDING. Population stratification is inflating", fh)
    log(f"       all test statistics equally.", fh)
    log(f"    -> Results need genomic correction before interpretation.", fh)

    return pd.DataFrame(results)


# ══════════════════════════════════════════════════════════════════════
# ANALYSIS 2 — CHR8 CLUSTER
# ══════════════════════════════════════════════════════════════════════

def chr8_cluster(df_r, fh):
    """
    Five GWS loci on chr8 between 8.9M and 12.4M.
    Extract and annotate the full cluster.
    """
    log("\n── ANALYSIS 2: CHR8 CLUSTER ──────────────────────────────", fh)
    log(f"  5 of 16 GWS loci on chr8:{CHR8_START/1e6:.1f}M-{CHR8_END/1e6:.1f}M", fh)
    log(f"  Extracting full cluster for gene annotation...", fh)

    mask = (df_r["chr"] == "8") & \
           (df_r["pos"] >= CHR8_START) & \
           (df_r["pos"] <= CHR8_END)
    cluster = df_r[mask].copy().sort_values("p")

    log(f"\n  Total SNPs in cluster region: {len(cluster):,}", fh)
    log(f"  GWS hits in cluster: {(cluster['p'] < GWS_THRESH).sum():,}", fh)
    log(f"  Suggestive hits: {(cluster['p'] < SUG_THRESH).sum():,}", fh)

    # Top 20 SNPs
    show = ["rsid","chr","pos","a1","a2","beta","se","p"]
    log(f"\n  Top 20 SNPs in chr8 cluster:", fh)
    log(cluster[show].head(20).to_string(index=False), fh)

    # P-value landscape across the cluster
    log(f"\n  Position landscape (binned by 500kb windows):", fh)
    log(f"  {'Window':30s} {'SNPs':>8s} {'GWS':>6s} {'Best_p':>12s}", fh)
    for win_start in range(CHR8_START, CHR8_END, 500_000):
        win_end = win_start + 500_000
        win_mask = (cluster["pos"] >= win_start) & (cluster["pos"] < win_end)
        win_df = cluster[win_mask]
        if len(win_df) == 0:
            continue
        best_p = win_df["p"].min()
        gws_n  = (win_df["p"] < GWS_THRESH).sum()
        label  = f"chr8:{win_start/1e6:.1f}M-{win_end/1e6:.1f}M"
        log(f"  {label:30s} {len(win_df):>8,} {gws_n:>6,} {best_p:>12.2e}", fh)

    # Known gene annotation
    log(f"\n  Known genes in chr8:{CHR8_START/1e6:.0f}M-{CHR8_END/1e6:.0f}M region:", fh)
    for gene, info in CHR8_KNOWN_GENES.items():
        overlap_start = max(info["start"], CHR8_START)
        overlap_end   = min(info["end"],   CHR8_END)
        if overlap_end > overlap_start:
            gene_mask = (cluster["pos"] >= info["start"]) & \
                        (cluster["pos"] <= info["end"])
            n_snps  = gene_mask.sum()
            best_p  = cluster[gene_mask]["p"].min() if n_snps > 0 else float("nan")
            log(f"\n  {gene}:", fh)
            log(f"    Position : chr8:{info['start']:,}-{info['end']:,}", fh)
            log(f"    Note     : {info['note']}", fh)
            log(f"    SNPs     : {n_snps:,}  Best p: {best_p:.2e}", fh)

    log(f"\n  KEY QUESTION for chr8 cluster:", fh)
    log(f"  ARHGEF10 (chr8:~8M) is directly implicated in axon", fh)
    log(f"  myelination — Charcot-Marie-Tooth disease gene.", fh)
    log(f"  If the chr8 cluster signal overlaps ARHGEF10:", fh)
    log(f"    -> This is a Layer B (myelination) signal that", fh)
    log(f"       was not in the original candidate gene windows.", fh)
    log(f"    -> Would suggest the myelination layer is actually", fh)
    log(f"       stronger than Layer B ranking indicated.", fh)
    log(f"  CSMD1 (chr8:2.9M-10.1M) overlaps the cluster window.", fh)
    log(f"  CSMD1 is brain-expressed and synapse-relevant.", fh)
    log(f"  Its role in white matter tract development is not", fh)
    log(f"  well characterised — this may be a novel signal.", fh)

    cluster.to_csv(OUT_CHR8, sep="\t", index=False)
    log(f"\n  Chr8 cluster saved -> {OUT_CHR8} ({len(cluster):,} rows)", fh)
    return cluster


# ══════════════════════════════════════════════════════════════════════
# ANALYSIS 3 — SEMA3A LOCUS DEEP EXTRACTION
# ══════════════════════════════════════════════════════════════════════

def sema3a_locus(df_r, fh):
    """
    Extract the full SEMA3A signal region and characterise it.
    The GWS hit rs78404854 is at chr7:83,662,138.
    SEMA3A gene body: chr7:83,294,422-83,703,344.
    Extract ±1Mb around the hit to see full LD block.
    """
    log("\n── ANALYSIS 3: SEMA3A LOCUS DEEP EXTRACTION ─────────────", fh)
    log("  GWS hit: rs78404854  chr7:83,662,138  p=4.07e-09  beta=+0.071", fh)
    log("  Extracting ±1Mb window for fine-mapping context...", fh)

    mask = (df_r["chr"] == SEMA3A_CHR) & \
           (df_r["pos"] >= SEMA3A_START) & \
           (df_r["pos"] <= SEMA3A_END)
    locus = df_r[mask].copy().sort_values("p")

    log(f"\n  SNPs in locus window: {len(locus):,}", fh)
    log(f"  GWS hits: {(locus['p'] < GWS_THRESH).sum():,}", fh)
    log(f"  p < 1e-5: {(locus['p'] < 1e-5).sum():,}", fh)
    log(f"  p < 1e-4: {(locus['p'] < 1e-4).sum():,}", fh)

    # Top 30 SNPs
    show = ["rsid","chr","pos","a1","a2","beta","se","p"]
    log(f"\n  Top 30 SNPs in SEMA3A locus:", fh)
    log(locus[show].head(30).to_string(index=False), fh)

    # Effect direction at top SNPs
    log(f"\n  Effect direction analysis:", fh)
    top20 = locus.head(20)
    pos_beta = (top20["beta"] > 0).sum()
    neg_beta = (top20["beta"] < 0).sum()
    log(f"  Top 20 SNPs: {pos_beta} with positive beta "
        f"(increase right UF FA), {neg_beta} with negative beta", fh)

    # Positional clustering within SEMA3A
    sema3a_body_mask = (locus["pos"] >= 83_294_422) & \
                       (locus["pos"] <= 83_703_344)
    upstream_mask    = locus["pos"] < 83_294_422
    downstream_mask  = locus["pos"] > 83_703_344

    for region_label, rmask in [
        ("SEMA3A gene body (83.29M-83.70M)", sema3a_body_mask),
        ("Upstream of SEMA3A (<83.29M)",      upstream_mask),
        ("Downstream/SEMA3D (>83.70M)",       downstream_mask),
    ]:
        sub = locus[rmask]
        if len(sub) == 0:
            continue
        best_p = sub["p"].min()
        gws_n  = (sub["p"] < GWS_THRESH).sum()
        log(f"\n  {region_label}:", fh)
        log(f"    SNPs: {len(sub):,}  GWS: {gws_n}  Best p: {best_p:.2e}", fh)
        if gws_n > 0:
            top_snp = sub.loc[sub["p"].idxmin()]
            log(f"    Top SNP: {top_snp['rsid']}  pos={top_snp['pos']:,}  "
                f"beta={top_snp['beta']:.4f}  p={top_snp['p']:.2e}", fh)

    log(f"\n  Localisation interpretation:", fh)
    log(f"  If top SNPs cluster in gene body -> coding/splicing variant", fh)
    log(f"  If top SNPs cluster upstream -> regulatory/promoter variant", fh)
    log(f"  If top SNPs span SEMA3A+SEMA3D -> may tag both genes", fh)

    locus.to_csv(OUT_SEMA3A, sep="\t", index=False)
    log(f"\n  SEMA3A locus saved -> {OUT_SEMA3A} ({len(locus):,} rows)", fh)
    return locus


# ══════════════════════════════════════════════════════════════════════
# ANALYSIS 4 — RIGHT vs LEFT EFFECT SIZE COMPARISON
# ══════════════════════════════════════════════════════════════════════

def right_left_beta_comparison(df_r, df_l, fh):
    """
    At all SNPs significant in either right or left UF FA,
    compare beta_R vs beta_L.
    SNPs with beta_R > beta_L = stronger effect on right = Layer D candidates.
    """
    log("\n── ANALYSIS 4: RIGHT vs LEFT EFFECT SIZE COMPARISON ─────", fh)
    log("  At all GWS/suggestive SNPs: how does beta_R compare to beta_L?", fh)
    log("  Identifies lateralised SNPs — Layer D candidates.", fh)

    # Get all significant SNPs from either trait
    sig_r = df_r[df_r["p"] < SUG_THRESH][["rsid","chr","pos","a1","a2",
                                            "beta","se","p"]].copy()
    sig_l = df_l[df_l["p"] < SUG_THRESH][["rsid","beta","se","p"]].copy()

    # Merge
    merged = pd.merge(
        sig_r, sig_l,
        on="rsid", suffixes=("_R","_L")
    )
    log(f"\n  SNPs significant (p<1e-6) in right UF FA:  {len(sig_r):,}", fh)
    log(f"  SNPs significant (p<1e-6) in left UF FA:   {len(sig_l):,}", fh)
    log(f"  Shared significant SNPs (merged on rsID):  {len(merged):,}", fh)

    if merged.empty:
        log("  No shared significant SNPs found.", fh)
        return pd.DataFrame()

    merged["beta_R"] = merged["beta_R"].astype(np.float64)
    merged["beta_L"] = merged["beta_L"].astype(np.float64)
    merged["beta_diff"] = merged["beta_R"] - merged["beta_L"]
    merged["abs_diff"]  = merged["beta_diff"].abs()
    merged["direction"] = np.where(
        merged["beta_diff"] > 0, "R>L (right stronger)",
        np.where(merged["beta_diff"] < 0, "L>R (left stronger)", "equal")
    )

    # Summary statistics
    r_stronger = (merged["beta_diff"] > 0.01).sum()
    l_stronger = (merged["beta_diff"] < -0.01).sum()
    symmetric  = (merged["beta_diff"].abs() <= 0.01).sum()

    log(f"\n  Effect direction at shared significant SNPs:", fh)
    log(f"    Right stronger (beta_R > beta_L + 0.01) : {r_stronger:,}", fh)
    log(f"    Left  stronger (beta_L > beta_R + 0.01) : {l_stronger:,}", fh)
    log(f"    Symmetric      (|diff| <= 0.01)          : {symmetric:,}", fh)

    # Correlation between beta_R and beta_L
    corr = merged["beta_R"].corr(merged["beta_L"])
    log(f"\n  Pearson correlation beta_R vs beta_L: {corr:.4f}", fh)
    log(f"  Interpretation:", fh)
    if corr > 0.95:
        log(f"    Very high correlation (r>{0.95:.2f}) — right and left UF FA", fh)
        log(f"    are driven by largely the same genetic variants.", fh)
        log(f"    This explains asymmetry index lambda GC deflation.", fh)
        log(f"    The traits are genetically near-identical.", fh)
    elif corr > 0.80:
        log(f"    High correlation — substantial genetic overlap.", fh)
        log(f"    Some lateralised SNPs exist but are a minority.", fh)
    else:
        log(f"    Moderate correlation — genuine lateralisation signal", fh)
        log(f"    present in the genetics. Layer D is real.", fh)

    # Most lateralised SNPs (largest |beta_diff|)
    top_lat = merged.nlargest(20, "abs_diff")
    show = ["rsid","chr","pos","beta_R","beta_L","beta_diff","p_R","p_L"]
    log(f"\n  Top 20 most lateralised SNPs (|beta_R - beta_L|):", fh)
    log(top_lat[show].to_string(index=False), fh)

    # SNPs where right is significantly stronger
    log(f"\n  SNPs where beta_R > beta_L by > 0.02 (strong lateralisation):", fh)
    strongly_lat = merged[merged["beta_diff"] > 0.02].sort_values(
        "beta_diff", ascending=False)
    if not strongly_lat.empty:
        log(strongly_lat[show].head(15).to_string(index=False), fh)
    else:
        log(f"  None found at this threshold.", fh)

    merged.to_csv(OUT_BETA_COMP, sep="\t", index=False)
    log(f"\n  Beta comparison saved -> {OUT_BETA_COMP} ({len(merged):,} rows)", fh)
    return merged


# ══════════════════════════════════════════════════════════════════════
# ANALYSIS 5 — CANDIDATE LAYER ENRICHMENT TEST
# ══════════════════════════════════════════════════════════════════════

def enrichment_test(df_r, fh):
    """
    Permutation test: is each candidate gene window enriched for
    signal beyond what is expected from a random genomic window
    of the same size?
    1000 permutations per gene.
    """
    log("\n── ANALYSIS 5: CANDIDATE LAYER ENRICHMENT TEST ──────────", fh)
    log(f"  {N_PERM} permutations per gene.", fh)
    log(f"  Matched on: chromosome size, window size.", fh)
    log(f"  Enrichment p < 0.05 = this gene window has more signal", fh)
    log(f"  than expected by chance.", fh)

    rng = np.random.default_rng(RAND_SEED)

    # Pre-compute chromosome ranges and SNP positions
    chr_ranges = {}
    for ch in df_r["chr"].unique():
        sub = df_r[df_r["chr"] == ch]
        chr_ranges[ch] = (int(sub["pos"].min()), int(sub["pos"].max()))

    results = []
    log(f"\n  {'Gene':10s} {'L':2s} {'Win_size':>12s} "
        f"{'Obs_p<1e-4':>12s} {'Exp_mean':>10s} "
        f"{'Enrich':>8s} {'Perm_p':>8s}", fh)
    log(f"  {'─'*70}", fh)

    thresh = 1e-4   # use 1e-4 for candidate gene test (more power)

    for gene, info in GENES.items():
        ch       = info["chr"]
        g_start  = info["start"]
        g_end    = info["end"]
        win_size = g_end - g_start

        # Observed count
        mask_obs = (df_r["chr"] == ch) & \
                   (df_r["pos"] >= g_start) & \
                   (df_r["pos"] <= g_end)
        obs_total = mask_obs.sum()
        obs_sig   = (df_r[mask_obs]["p"] < thresh).sum()

        if obs_total == 0:
            log(f"  {gene:10s} {info['layer']:2s} — no SNPs found", fh)
            continue

        # Permutation: random windows on same chromosome
        if ch not in chr_ranges:
            continue
        ch_min, ch_max = chr_ranges[ch]

        perm_counts = []
        for _ in range(N_PERM):
            max_start = ch_max - win_size
            if max_start <= ch_min:
                perm_counts.append(obs_sig)
                continue
            rand_start = int(rng.integers(ch_min, max_start))
            rand_end   = rand_start + win_size
            perm_mask  = (df_r["chr"] == ch) & \
                         (df_r["pos"] >= rand_start) & \
                         (df_r["pos"] <= rand_end)
            perm_counts.append(int((df_r[perm_mask]["p"] < thresh).sum()))

        perm_arr = np.array(perm_counts)
        exp_mean = perm_arr.mean()
        enrich   = obs_sig / exp_mean if exp_mean > 0 else float("nan")
        perm_p   = (perm_arr >= obs_sig).mean()

        log(f"  {gene:10s} {info['layer']:2s} {win_size:>12,} "
            f"{obs_sig:>12,} {exp_mean:>10.1f} "
            f"{enrich:>8.2f} {perm_p:>8.3f}", fh)

        results.append({
            "gene": gene, "layer": info["layer"],
            "window_size": win_size, "obs_sig": obs_sig,
            "exp_mean": exp_mean, "enrichment": enrich,
            "perm_p": perm_p, "threshold": thresh,
        })

    df_enrich = pd.DataFrame(results)

    if not df_enrich.empty:
        log(f"\n  Significant enrichments (perm_p < 0.05):", fh)
        sig_enrich = df_enrich[df_enrich["perm_p"] < 0.05].sort_values("perm_p")
        if not sig_enrich.empty:
            log(sig_enrich[["gene","layer","enrichment","perm_p"]].to_string(
                index=False), fh)
        else:
            log(f"  None at p < 0.05.", fh)

        log(f"\n  Layer-level enrichment summary:", fh)
        for layer in ["A","B","C","D"]:
            layer_df = df_enrich[df_enrich["layer"] == layer]
            if layer_df.empty:
                continue
            min_p  = layer_df["perm_p"].min()
            mean_e = layer_df["enrichment"].mean()
            log(f"    Layer {layer}: best perm_p = {min_p:.3f}  "
                f"mean enrichment = {mean_e:.2f}x", fh)

    df_enrich.to_csv(OUT_ENRICHMENT, sep="\t", index=False)
    log(f"\n  Enrichment results saved -> {OUT_ENRICHMENT}", fh)
    return df_enrich


# ══════════════════════════════════════════════════════════════════════
# ANALYSIS 6 — CROSS-LAYER SIGNAL PROFILE
# ══════════════════════════════════════════════════════════════════════

def cross_layer_profile(df_r, fh):
    """
    For each candidate gene window:
    - Mean chi-squared vs genome-wide mean
    - Fraction of SNPs below each threshold
    - Signal concentration (Gini-like: is signal from 1 SNP or spread?)
    """
    log("\n── ANALYSIS 6: CROSS-LAYER SIGNAL PROFILE ───────────────", fh)

    genome_mean_chisq = np.mean(chi2.ppf(
        1 - df_r["p"].clip(1e-300, 1).values, df=1))
    log(f"  Genome-wide mean chi-squared: {genome_mean_chisq:.4f}", fh)
    log(f"  (Expected under null: 1.0)", fh)

    records = []
    log(f"\n  {'Gene':10s} {'Layer':6s} "
        f"{'N':>8s} {'Mean_X2':>10s} {'Ratio':>8s} "
        f"{'p<0.05':>8s}% {'p<1e-4':>8s}% {'Top_SNP_lp':>12s}", fh)
    log(f"  {'─'*80}", fh)

    for gene, info in GENES.items():
        mask = (df_r["chr"] == info["chr"]) & \
               (df_r["pos"] >= info["start"]) & \
               (df_r["pos"] <= info["end"])
        sub = df_r[mask]
        if len(sub) == 0:
            continue

        chisq_sub = chi2.ppf(1 - sub["p"].clip(1e-300, 1).values, df=1)
        mean_x2   = float(np.mean(chisq_sub))
        ratio     = mean_x2 / genome_mean_chisq
        pct_005   = float((sub["p"] < 0.05).mean() * 100)
        pct_1e4   = float((sub["p"] < 1e-4).mean() * 100)
        top_lp    = float(sub["lp"].max())

        log(f"  {gene:10s} {info['layer']:6s} "
            f"{len(sub):>8,} {mean_x2:>10.4f} {ratio:>8.3f} "
            f"{pct_005:>8.2f} {pct_1e4:>8.3f} {top_lp:>12.3f}", fh)

        records.append({
            "gene": gene, "layer": info["layer"],
            "n_snps": len(sub), "mean_chisq": mean_x2,
            "ratio_to_genome": ratio,
            "pct_p005": pct_005, "pct_p1e4": pct_1e4,
            "top_snp_lp": top_lp,
        })

    df_prof = pd.DataFrame(records)

    log(f"\n  Ratio interpretation:", fh)
    log(f"  ratio > 1.0 = more signal than genome average", fh)
    log(f"  ratio > 1.5 = clearly enriched", fh)
    log(f"  ratio > 2.0 = strongly enriched (likely real signal)", fh)

    if not df_prof.empty:
        log(f"\n  Genes with ratio > 1.5 (enriched windows):", fh)
        enriched = df_prof[df_prof["ratio_to_genome"] > 1.5].sort_values(
            "ratio_to_genome", ascending=False)
        if not enriched.empty:
            log(enriched[["gene","layer","ratio_to_genome",
                           "top_snp_lp"]].to_string(index=False), fh)
        else:
            log(f"  None at ratio > 1.5.", fh)

    df_prof.to_csv(OUT_LAYER_PROF, sep="\t", index=False)
    log(f"\n  Profile saved -> {OUT_LAYER_PROF}", fh)
    return df_prof


# ══════════════════════════════════════════════════════════════════════
# ANALYSIS 7 — SLIT2 LOCUS
# ══════════════════════════════════════════════════════════════════════

def slit2_locus(df_r, fh):
    """
    SLIT2 showed best p = 1.72e-06 (suggestive, Layer A partner of ROBO1).
    Extract the locus and check if it is directionally consistent
    with SEMA3A (both axon guidance — should have concordant biology).
    """
    log("\n── ANALYSIS 7: SLIT2 LOCUS (LAYER A PARTNER) ────────────", fh)
    log("  SLIT2 p=1.72e-06 — suggestive. ROBO1/SLIT2 are the", fh)
    log("  guidance couplet at hemispheric axon decision points.", fh)
    log("  Checking directional concordance with SEMA3A hit.", fh)

    mask = (df_r["chr"] == SLIT2_CHR) & \
           (df_r["pos"] >= SLIT2_START) & \
           (df_r["pos"] <= SLIT2_END)
    locus = df_r[mask].copy().sort_values("p")

    log(f"\n  SNPs in SLIT2 region: {len(locus):,}", fh)
    log(f"  Best p: {locus['p'].min():.2e}", fh)
    log(f"  Suggestive (p<1e-5): {(locus['p'] < 1e-5).sum():,}", fh)

    show = ["rsid","chr","pos","a1","a2","beta","se","p"]
    log(f"\n  Top 15 SLIT2 region SNPs:", fh)
    log(locus[show].head(15).to_string(index=False), fh)

    # Directional check vs SEMA3A
    # SEMA3A top hit beta = +0.0711 (positive = risk allele increases right UF FA)
    # If SLIT2 top hit is also positive: same directional pathway
    if not locus.empty:
        top_slit2 = locus.iloc[0]
        sema3a_beta_direction = "positive"  # from Step 2 results
        slit2_direction = "positive" if top_slit2["beta"] > 0 else "negative"
        log(f"\n  SEMA3A top hit beta direction: {sema3a_beta_direction}", fh)
        log(f"  SLIT2  top hit beta direction: {slit2_direction}", fh)
        if slit2_direction == sema3a_beta_direction:
            log(f"  CONCORDANT: Both Layer A genes push in same direction.", fh)
            log(f"  Supports shared axon guidance pathway interpretation.", fh)
        else:
            log(f"  DISCORDANT: Opposite directions.", fh)
            log(f"  May reflect different roles within the guidance pathway,", fh)
            log(f"  or may be tagging different biology.", fh)

    locus.to_csv(OUT_SLIT2, sep="\t", index=False)
    log(f"\n  SLIT2 locus saved -> {OUT_SLIT2} ({len(locus):,} rows)", fh)
    return locus


# ══════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════

def main():
    try:
        import scipy
    except ImportError:
        print("Run: pip install pandas numpy scipy")
        sys.exit(1)

    with open(OUT_REPORT, "w") as fh:
        log("═"*70, fh)
        log("STEP 3 DEEPER ANALYSIS", fh)
        log("OC-PSYCHOPATHY-GENETIC-MARKER-DERIVATION-001", fh)
        log(f"Run: {time.strftime('%Y-%m-%d %H:%M:%S')}", fh)
        log("═"*70, fh)
        log("""
Seven analyses:
  1. Genomic inflation decomposition (confounding vs polygenicity)
  2. Chr8 cluster identification (5 GWS loci in 4Mb)
  3. SEMA3A locus fine-mapping
  4. Right vs left beta comparison at shared significant SNPs
  5. Candidate layer enrichment test (1000 permutations)
  6. Cross-layer signal profile (mean chi-squared per window)
  7. SLIT2 locus extraction and directional check
""", fh)

        # Load
        log("── LOADING ───────────────────────────────────────────────", fh)
        df_r = load(FILE_R, fh)
        df_l = load(FILE_L, fh)

        # Run analyses
        inflation_decomposition(df_r, df_l, fh)
        chr8_cluster(df_r, fh)
        sema3a_locus(df_r, fh)
        right_left_beta_comparison(df_r, df_l, fh)
        enrichment_test(df_r, fh)     # takes ~2-3 min with 1000 perms
        cross_layer_profile(df_r, fh)
        slit2_locus(df_r, fh)

        # Summary
        log("\n═"*70, fh)
        log("OUTPUTS PRODUCED", fh)
        log("═"*70, fh)
        log(f"""
  {OUT_REPORT}       — this report
  {OUT_CHR8}      — chr8 cluster full SNP table
  {OUT_SEMA3A}       — SEMA3A locus fine-mapping SNPs
  {OUT_SLIT2}        — SLIT2 locus SNPs
  {OUT_BETA_COMP}  — right vs left beta at shared SNPs
  {OUT_ENRICHMENT}      — layer enrichment permutation results
  {OUT_LAYER_PROF}   — per-gene signal profile

WHAT THESE RESULTS DETERMINE:

  After Step 3:

  1. If inflation is concentrated at top hits (not uniform):
     -> GWS hits are real. Proceed with confidence.

  2. If chr8 cluster overlaps ARHGEF10 (myelination gene):
     -> Layer B signal is stronger than candidate window showed.
     -> ARHGEF10 should be added to the Layer B candidate set.

  3. If SEMA3A signal localises to gene body:
     -> Candidate causal variant is a coding/splicing change.
     -> Functional follow-up is sequencing the SEMA3A coding region.

  4. If beta_R correlation with beta_L is very high (r>0.95):
     -> Asymmetry index requires individual-level data (confirmed).
     -> Most genetic variance is shared between right and left UF.
     -> The lateralisation signal is real but small.

  5. If Layer A enrichment is significant in permutation test:
     -> Axon guidance is confirmed as the primary failure mode.

  6. If SLIT2 is directionally concordant with SEMA3A:
     -> Two-gene convergent confirmation of Layer A pathway.
     -> The axon guidance conclusion is robust.

STEP 4 (after obtaining antisocial GWAS):
  Two-sample Mendelian Randomisation using gwas_ready_instruments.tsv
  Exposure: right UF FA (16 instrument SNPs)
  Outcome:  antisocial behaviour
  Test: does genetic predisposition to lower right UF FA
        causally predict antisocial phenotype?
""", fh)

        log(f"Done: {time.strftime('%Y-%m-%d %H:%M:%S')}", fh)

    print(f"\n{'═'*60}")
    print(f"Step 3 complete. Report: {OUT_REPORT}")
    print(f"{'═'*60}")


if __name__ == "__main__":
    main()
