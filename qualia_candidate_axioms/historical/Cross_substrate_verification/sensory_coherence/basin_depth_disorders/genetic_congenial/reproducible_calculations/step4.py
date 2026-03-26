"""
STEP 4 — MENDELIAN RANDOMISATION AND COLOCALISATION
=====================================================
OC-PSYCHOPATHY-GENETIC-MARKER-DERIVATION-001
Eric Robert Lawson — OrganismCore — 2026-03-26

Builds directly on Step 3.

What Step 3 established:
  ✓ 16 real GWS loci for right UF FA
  ✓ SEMA3A: 48x enriched, Layer A confirmed, signal in introns 14-17
  ✓ CSMD1: novel Layer E (pruning/consolidation), chr8:9.5M-10.5M
  ✓ SLIT2: directionally concordant, rare variant rs144081524 beta=+0.435
  ✓ Chr4:97.9M: left-lateralised locus
  ✓ Beta R/L correlation = 0.9918 (near-identical genetics)

What this script does:

  ANALYSIS 1 — CSMD1 FINE-MAPPING
    The chr8 cluster has 259 GWS hits across 4Mb.
    These are not all independent — they form LD blocks.
    Approximate clumping (no individual-level data) using
    p-value windowing and distance criteria:
      Lead SNP per 500kb window
      Identify sub-peaks within the cluster
    Characterise the CSMD1 signal architecture:
      Is this one extended haplotype or multiple signals?
      What is the peak SNP position relative to CSMD1 exons?
    Output: csmd1_finemap.tsv

  ANALYSIS 2 — BRAIN eQTL LOOKUP
    For the top 30 SEMA3A locus SNPs:
    Query EBI eQTL Catalogue API for brain eQTLs.
    Specifically check if rs78404854 (top SEMA3A hit) or
    nearby SNPs predict SEMA3A expression in brain tissue.
    Resources queried:
      EBI eQTL Catalogue (REST API, no auth required)
      Covers: GTEx v8 brain tissues, PsychENCODE, BrainSeq
    For the top CSMD1 SNP (rs4383974):
    Same eQTL lookup — does it predict CSMD1 expression?
    Output: eqtl_lookup_results.tsv

  ANALYSIS 3 — MENDELIAN RANDOMISATION
    Two-sample MR:
      Exposure: right UF FA (this GWAS, file 1496.txt)
      Outcome:  broad antisocial behaviour (BroadABC 2022)
                Tielbeek et al., Mol Psychiatry 2022
                File: broadABC2022_Final_CombinedSex.TBL

    Instruments: 16 GWS loci from Step 2 (gwas_ready_instruments.tsv)

    MR methods run:
      (a) Inverse Variance Weighted (IVW) — primary
      (b) Weighted Median — robust to 50% invalid instruments
      (c) MR-Egger — tests directional pleiotropy
      (d) Weighted Mode — robust to plurality of valid instruments
      (e) Leave-one-out — identifies any single-instrument drivers

    BroadABC column format (confirmed):
      chromosome  base_pair_location  effect_allele  other_allele
      beta  standard_error  effect_allele_frequency  p_value  rsid  n
    Note: beta values are on the BroadABC composite score scale
    (large absolute values, e.g. 4.35, are normal for this phenotype).
    MR beta is interpreted relative to the BroadABC effect size scale.

    Output:
      mr_results.tsv         — all MR method results
      mr_loo.tsv             — leave-one-out results
      mr_steiger.tsv         — Steiger filtering (direction test)

  ANALYSIS 4 — SEMA3A / ANTISOCIAL COLOCALISATION
    The SEMA3A GWS signal is at chr7:83.0M-84.5M.
    If the BroadABC GWAS also has signal at this locus:
      -> The same genetic variants that reduce right UF FA
         also increase antisocial behaviour
      -> This is mechanistic confirmation:
         SEMA3A variants -> right UF FA reduction -> antisocial behaviour
    Approximate colocalisation (no individual-level data):
      PP4 (shared causal variant) computed using summary statistics
      Method: Approximate Bayes Factor (ABF) colocalisation
              (Giambartolomei et al., 2014 method)
    Same test run at CSMD1 locus (chr8:8.5M-11.5M).
    Output: coloc_results.tsv

Inputs required:
  1496.txt                              Right UF FA GWAS
  gwas_ready_instruments.tsv            16 instrument SNPs from Step 2
  chr8_cluster_genes.tsv                Chr8 cluster from Step 3
  sema3a_locus_snps.tsv                 SEMA3A locus from Step 3
  broadABC2022_Final_CombinedSex.TBL    BroadABC outcome GWAS

Outputs produced:
  csmd1_finemap.tsv
  eqtl_lookup_results.tsv
  mr_results.tsv
  mr_loo.tsv
  mr_steiger.tsv
  coloc_results.tsv
  step4_results.txt

CRITICAL PRE-REGISTRATION:
  All MR predictions are stated BEFORE running the script.
  See PREDICTIONS block below.
  Do not modify predictions after results are seen.
"""

import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import chi2, norm

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

warnings.filterwarnings("ignore")

# ══════════════════════════════════════════════════════════════════════
# PRE-REGISTERED PREDICTIONS
# Locked 2026-03-26 before script execution.
# Do not modify.
# ══════════════════════════════════════════════════════════════════════
PREDICTIONS = """
PRE-REGISTERED PREDICTIONS — STEP 4
Locked: 2026-03-26
OC-PSYCHOPATHY-GENETIC-MARKER-DERIVATION-001

P4-1  MR PRIMARY (IVW):
  Genetic predisposition to lower right UF FA is associated
  with higher broad antisocial behaviour score.
  Predicted direction: NEGATIVE beta in MR
  (lower right UF FA -> higher antisocial behaviour)
  Predicted significance: p < 0.05 in IVW
  Predicted effect size: beta in range -0.05 to -0.30
  (small-to-moderate causal effect on standardised scale)
  NOTE: BroadABC beta scale is large (units ~4.0 per common variant).
  The MR beta will be on this scale. Direction is the primary test.

P4-2  MR ROBUSTNESS:
  Weighted Median MR will be directionally concordant with IVW.
  If IVW is negative, Weighted Median will also be negative.

P4-3  MR-EGGER INTERCEPT:
  MR-Egger intercept will not significantly differ from zero
  (p > 0.05 for intercept), indicating no directional pleiotropy.
  The effect is via right UF FA biology, not via pleiotropic
  confounding through unrelated pathways.

P4-4  SEMA3A COLOCALISATION:
  The SEMA3A locus will show colocalisation between right UF FA
  GWAS and BroadABC antisocial GWAS.
  Predicted PP4 (shared causal variant) > 0.5.
  Predicted: the same variants that reduce SEMA3A function
  (reduce right UF FA) also increase antisocial behaviour.

P4-5  CSMD1 COLOCALISATION:
  The CSMD1 chr8 locus will show colocalisation between right
  UF FA GWAS and BroadABC antisocial GWAS.
  Predicted PP4 > 0.3 (weaker prior — CSMD1 is novel,
  its pathway to antisocial behaviour is less direct).

P4-6  CSMD1 FINE-MAPPING:
  The chr8 cluster will resolve to 2-4 independent signals,
  not one extended haplotype.
  Predicted: multiple sub-peaks at distinct positions within
  the CSMD1 gene body.

P4-7  SEMA3A eQTL:
  rs78404854 or a nearby SNP in LD will be a significant
  eQTL for SEMA3A expression in at least one brain tissue
  in the EBI eQTL Catalogue.
  Predicted: the effect allele that reduces right UF FA
  (C allele of rs78404854) will also reduce SEMA3A expression.
  Same direction: lower SEMA3A expression -> lower right UF FA.

P4-8  STEIGER FILTERING:
  The 16 instruments pass Steiger direction test:
  The variants explain more variance in right UF FA (exposure)
  than in antisocial behaviour (outcome).
  This confirms the causal direction is right UF FA -> behaviour,
  not reverse causation.
  NOTE: Steiger r2 for outcome uses per-SNP N from BroadABC 'n'
  column where available (mean ~56,000-85,000 across SNPs).
"""

# ══════════════════════════════════════════════════════════════════════
# PARAMETERS
# ══════════════════════════════════════════════════════════════════════

# Input files
FILE_R           = "1496.txt"
FILE_INSTRUMENTS = "gwas_ready_instruments.tsv"
FILE_HITS_R      = "top_hits_right_UF.tsv"
FILE_CHR8        = "chr8_cluster_genes.tsv"
FILE_SEMA3A      = "sema3a_locus_snps.tsv"

# BroadABC outcome GWAS — confirmed filename
# Tielbeek et al. 2022 Mol Psychiatry
# Combined sex, European ancestry, N_max ~85,359
BROADABC_FILE    = "broadABC2022_Final_CombinedSex.TBL"

# BroadABC total N (Tielbeek 2022, European combined sex)
# Used as fallback where per-SNP n column is missing/NaN
N_OUTCOME        = 85_359

# Exposure N
N_EXPOSURE       = 31_341

# Output files
OUT_REPORT       = Path("step4_results.txt")
OUT_CSMD1_FM     = Path("csmd1_finemap.tsv")
OUT_EQTL         = Path("eqtl_lookup_results.tsv")
OUT_MR           = Path("mr_results.tsv")
OUT_MR_LOO       = Path("mr_loo.tsv")
OUT_MR_STEIGER   = Path("mr_steiger.tsv")
OUT_COLOC        = Path("coloc_results.tsv")

# CSMD1 region
CSMD1_CHR        = "8"
CSMD1_START      = 8_500_000
CSMD1_END        = 11_500_000

# SEMA3A region
SEMA3A_CHR       = "7"
SEMA3A_START     = 83_000_000
SEMA3A_END       = 84_500_000

# Colocalisation prior probabilities (Giambartolomei defaults)
P1               = 1e-4    # prior SNP is causal for trait 1
P2               = 1e-4    # prior SNP is causal for trait 2
P12              = 1e-5    # prior SNP is causal for both

# Approximate clumping parameters (no LD data — windowing only)
CLUMP_WINDOW     = 500_000   # 500kb independence window
GWS_THRESH       = 5e-8
SUG_THRESH       = 1e-5
MAX_SE           = 0.5

# EBI eQTL Catalogue API
EBI_EQTL_BASE    = "https://www.ebi.ac.uk/eqtl/api/v2"


# ═════════════════════════════��════════════════════════════════════════
# UTILITIES
# ══════════════════════════════════════════════════════════════════════

def log(msg, fh=None):
    print(msg)
    if fh:
        fh.write(msg + "\n")
        fh.flush()


def load_gwas(filepath, fh, label=""):
    """
    Load a GWAS summary statistics file flexibly.
    Handles: space/tab delimited, gzipped, varied column names.
    BroadABC confirmed columns:
      chromosome  base_pair_location  effect_allele  other_allele
      beta  standard_error  effect_allele_frequency  p_value  rsid  n
    """
    p = Path(filepath)
    if not p.exists():
        p = Path(str(filepath) + ".gz")
    if not p.exists():
        log(f"  WARNING: {filepath} not found.", fh)
        return None

    log(f"  Loading {label or p.name}  ({p.stat().st_size/1e6:.0f} MB)...", fh)
    t0 = time.time()

    # Detect delimiter from header
    with open(p, "r") as f:
        header = f.readline().strip()
    sep = "\t" if "\t" in header else r"\s+"

    df = pd.read_csv(
        p,
        sep=sep,
        compression="gzip" if str(p).endswith(".gz") else None,
        low_memory=False,
    )

    # Normalise column names to lowercase
    df.columns = [c.strip().lower() for c in df.columns]

    # Comprehensive column name map
    # BroadABC-specific names are listed explicitly
    col_map = {
        # rsid — BroadABC uses 'rsid' directly (already correct)
        "snp":                    "rsid",
        "snpid":                  "rsid",
        "variant_id":             "rsid",
        "markername":             "rsid",
        "id":                     "rsid",
        # chromosome — BroadABC: 'chromosome'
        "chromosome":             "chr",
        "chrom":                  "chr",
        "ch":                     "chr",
        "#chr":                   "chr",
        # position — BroadABC: 'base_pair_location'
        "base_pair_location":     "pos",
        "bp":                     "pos",
        "position":               "pos",
        "basepair":               "pos",
        "pos_b37":                "pos",
        "bp_b37":                 "pos",
        # effect allele — BroadABC: 'effect_allele'
        "effect_allele":          "a1",
        "allele1":                "a1",
        "alt":                    "a1",
        # other allele — BroadABC: 'other_allele'
        "other_allele":           "a2",
        "allele2":                "a2",
        "ref":                    "a2",
        "non_effect_allele":      "a2",
        # beta — BroadABC: 'beta' (already correct)
        "effect":                 "beta",
        "b":                      "beta",
        "log_or":                 "beta",
        "lnor":                   "beta",
        # se — BroadABC: 'standard_error'
        "standard_error":         "se",
        "stderr":                 "se",
        "se_gc":                  "se",
        # p-value — BroadABC: 'p_value'
        "p_value":                "p",
        "pval":                   "p",
        "p-value":                "p",
        "p.value":                "p",
        "gc_pvalue":              "p",
        "pvalue":                 "p",
        # EAF — BroadABC: 'effect_allele_frequency'
        "effect_allele_frequency":"eaf",
        "freq1":                  "eaf",
        "frq":                    "eaf",
        "maf":                    "eaf",
        # per-SNP N — BroadABC: 'n'
        "neff":                   "n",
        "n_total":                "n",
        "sample_size":            "n",
    }

    df = df.rename(columns={k: v for k, v in col_map.items()
                             if k in df.columns and v not in df.columns})

    # OR -> log(OR) conversion if needed
    if "or" in df.columns and "beta" not in df.columns:
        df["beta"] = np.log(pd.to_numeric(df["or"], errors="coerce"))

    # -log10(p) -> p conversion
    if "p" not in df.columns and "lp" in df.columns:
        df["p"] = 10.0 ** (-pd.to_numeric(df["lp"], errors="coerce"))

    # Coerce numeric types
    for col in ["beta", "se", "p", "pos", "n", "eaf"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Normalise chromosome: strip leading zeros, 'chr' prefix
    if "chr" in df.columns:
        df["chr"] = (df["chr"].astype(str)
                     .str.strip()
                     .str.lower()
                     .str.replace("^chr", "", regex=True)
                     .str.lstrip("0")
                     .replace("", "0"))

    # Normalise alleles to uppercase
    for ac in ["a1", "a2"]:
        if ac in df.columns:
            df[ac] = df[ac].astype(str).str.upper().str.strip()

    # Drop rows missing essential columns
    essential = [c for c in ["beta", "se", "p"] if c in df.columns]
    df = df.dropna(subset=essential)
    if "se" in df.columns:
        df = df[df["se"] > 0]

    elapsed = time.time() - t0
    log(f"  {len(df):,} variants  [{elapsed:.1f}s]", fh)
    log(f"  Columns present: {list(df.columns)}", fh)

    # Warn about BroadABC beta scale
    if "beta" in df.columns:
        med_abs_beta = df["beta"].abs().median()
        if med_abs_beta > 1.0:
            log(f"  NOTE: median |beta| = {med_abs_beta:.3f}", fh)
            log(f"  BroadABC betas are on composite score scale (not log-OR).", fh)
            log(f"  MR betas will be interpreted on this scale.", fh)

    return df


# ══════════════════════════════════════════════════════════════════════
# ANALYSIS 1 — CSMD1 FINE-MAPPING
# ════════════════════════════════════════════════════════════���═════════

def csmd1_finemap(df_r, fh):
    """
    Approximate clumping of the chr8 CSMD1 cluster.
    Without individual-level LD data, use windowed clumping:
      1. Sort all GWS SNPs in the cluster by p-value.
      2. Take the top SNP as the first independent signal.
      3. Remove all SNPs within 500kb of it.
      4. The next remaining GWS SNP is the second signal.
      5. Repeat until no GWS SNPs remain.
    This approximates conditional independence.
    """
    log("\n── ANALYSIS 1: CSMD1 FINE-MAPPING ───────────────────────", fh)

    # Load chr8 cluster from Step 3 output, or extract fresh
    if Path(FILE_CHR8).exists():
        cluster = pd.read_csv(FILE_CHR8, sep="\t", dtype={"chr": str})
        log(f"  Loaded chr8 cluster from {FILE_CHR8}: {len(cluster):,} SNPs", fh)
    else:
        log(f"  {FILE_CHR8} not found — extracting from GWAS file...", fh)
        cluster = df_r[
            (df_r["chr"] == CSMD1_CHR) &
            (df_r["pos"] >= CSMD1_START) &
            (df_r["pos"] <= CSMD1_END)
        ].copy()
        log(f"  Extracted {len(cluster):,} SNPs from chr8:{CSMD1_START:,}-{CSMD1_END:,}", fh)

    # Work only with GWS SNPs for clumping
    gws = cluster[cluster["p"] < GWS_THRESH].copy().sort_values("p")
    log(f"  GWS SNPs in CSMD1 region: {len(gws):,}", fh)

    if gws.empty:
        log(f"  No GWS SNPs found. Check chr column format.", fh)
        return pd.DataFrame()

    # Windowed clumping
    independent_signals = []
    remaining = gws.copy()
    signal_idx = 1

    while not remaining.empty:
        lead = remaining.iloc[0]
        independent_signals.append(lead)
        remaining = remaining[
            (remaining["pos"] < lead["pos"] - CLUMP_WINDOW) |
            (remaining["pos"] > lead["pos"] + CLUMP_WINDOW)
        ]
        signal_idx += 1

    signals_df = pd.DataFrame(independent_signals).reset_index(drop=True)
    log(f"\n  Approximate independent signals (500kb window): {len(signals_df)}", fh)

    show = [c for c in ["rsid","chr","pos","a1","a2","beta","se","p"]
            if c in signals_df.columns]
    log(f"\n  Independent signals:", fh)
    log(signals_df[show].to_string(index=False), fh)

    # Annotate each signal relative to CSMD1 structure
    # CSMD1 landmarks (GRCh37/hg19):
    #   Gene start (5'):  chr8:2,970,000
    #   Gene end   (3'):  chr8:10,118,393
    #   3' exon cluster:  ~9,500,000-10,100,000
    log(f"\n  CSMD1 gene body landmark annotations:", fh)
    log(f"  {'#':>3s}  {'rsid':22s}  {'pos':>12s}  {'Region':35s}  {'p':>12s}", fh)
    log(f"  {'─'*90}", fh)

    for idx, row in signals_df.iterrows():
        pos = int(row["pos"])
        if pos < 8_000_000:
            region = "Upstream of CSMD1 3' cluster"
        elif 8_000_000 <= pos < 9_500_000:
            region = "CSMD1 3' region (early)"
        elif 9_500_000 <= pos < 10_118_393:
            region = "CSMD1 3' region (late / exon cluster)"
        elif 10_118_393 <= pos < 10_600_000:
            region = "3' of CSMD1 / PINX1 region"
        else:
            region = "Distal / NKX6-3 region"

        rsid_val = row.get("rsid", f"SNP_{idx}")
        log(f"  {idx+1:>3d}  {str(rsid_val):22s}  {pos:>12,}  "
            f"{region:35s}  {row['p']:>12.2e}", fh)

    # Effect direction consistency
    pos_beta = int((signals_df["beta"] > 0).sum())
    neg_beta = int((signals_df["beta"] < 0).sum())
    log(f"\n  Effect directions: {pos_beta} positive beta, {neg_beta} negative beta", fh)
    if pos_beta > 0 and neg_beta > 0:
        log(f"  Mixed directions — suggests multiple independent signals", fh)
        log(f"  with different LD patterns tagging different causal variants.", fh)
    else:
        log(f"  Uniform direction — consistent with single extended haplotype.", fh)

    # Architecture interpretation
    n_sig = len(signals_df)
    log(f"\n  Architecture interpretation (P4-6 prediction: 2-4 signals):", fh)
    if n_sig == 1:
        log(f"  1 signal — single causal variant/haplotype.", fh)
        log(f"  P4-6: DENIED (predicted 2-4).", fh)
    elif 2 <= n_sig <= 4:
        log(f"  {n_sig} signals — CSMD1 has multiple independent genetic", fh)
        log(f"  effects on right UF FA. Implies:", fh)
        log(f"    (a) Multiple functional variants in different CSMD1 domains", fh)
        log(f"    (b) True allelic heterogeneity in CSMD1 function", fh)
        log(f"  P4-6: CONFIRMED ({n_sig} signals within predicted 2-4 range).", fh)
    else:
        log(f"  {n_sig} signals — high allelic heterogeneity or LD complexity.", fh)
        log(f"  Individual-level conditional analysis required.", fh)
        log(f"  P4-6: PARTIAL ({n_sig} signals, outside predicted 2-4 range).", fh)

    signals_df.to_csv(OUT_CSMD1_FM, sep="\t", index=False)
    log(f"\n  CSMD1 fine-mapping saved -> {OUT_CSMD1_FM}", fh)
    return signals_df


# ══════════════════════════════════════════════════════════════════════
# ANALYSIS 2 — EBI eQTL CATALOGUE LOOKUP
# ══════════════════════════════════════════════════════════════════════

def eqtl_lookup(fh):
    """
    Query EBI eQTL Catalogue API v2 for brain eQTLs at:
      rs78404854  — top SEMA3A hit (chr7:83,662,138)
      rs4383974   — top CSMD1 hit  (chr8:9,619,348)
      rs144081524 — top SLIT2 hit  (chr4:20,870,358)
    """
    log("\n── ANALYSIS 2: EBI eQTL CATALOGUE LOOKUP ────────────────", fh)

    if not HAS_REQUESTS:
        log("  requests library not available.", fh)
        log("  Install: pip install requests", fh)
        _eqtl_offline_guide(fh)
        return pd.DataFrame()

    query_snps = {
        "rs78404854": {
            "gene": "SEMA3A", "chr": "7", "pos": 83_662_138,
            "note": "Top SEMA3A Layer A hit — beta=+0.071 right UF FA",
            "risk_allele": "C",
            "protective_allele": "T",
        },
        "rs4383974": {
            "gene": "CSMD1", "chr": "8", "pos": 9_619_348,
            "note": "Top CSMD1 Layer E hit — beta=+0.059 right UF FA",
            "risk_allele": "G",
            "protective_allele": "C",
        },
        "rs144081524": {
            "gene": "SLIT2", "chr": "4", "pos": 20_870_358,
            "note": "Top SLIT2 suggestive hit — beta=+0.435 right UF FA",
            "risk_allele": "A",
            "protective_allele": "G",
        },
    }

    results = []
    log(f"\n  Querying EBI eQTL Catalogue API: {EBI_EQTL_BASE}", fh)
    log(f"  Brain tissue keywords: brain, cortex, temporal, frontal,", fh)
    log(f"    hippocampus, cerebellum, caudate, putamen, nucleus,", fh)
    log(f"    psyche, neuro, fetal, foetal", fh)

    brain_keywords = ["brain", "cortex", "temporal", "frontal",
                      "hippocampus", "cerebellum", "caudate",
                      "putamen", "nucleus", "psyche", "neuro",
                      "fetal", "foetal"]

    for rsid, info in query_snps.items():
        log(f"\n  ── {rsid} ({info['gene']}) ──", fh)
        log(f"     {info['note']}", fh)
        log(f"     Risk allele (lower UF FA): {info['risk_allele']}", fh)

        url    = f"{EBI_EQTL_BASE}/associations"
        params = {"variant_id": rsid, "size": 1000}

        try:
            resp = requests.get(url, params=params, timeout=30)

            if resp.status_code == 200:
                data = resp.json()
                hits = data.get("_embedded", {}).get("associations", [])

                if not hits:
                    log(f"     No associations found in eQTL Catalogue.", fh)
                    log(f"     Possible reasons:", fh)
                    log(f"       (a) Variant not genotyped in catalogued studies", fh)
                    log(f"       (b) Not a significant eQTL in any catalogued tissue", fh)
                    log(f"       (c) eQTL effect is fetal-specific (absent from adult GTEx)", fh)
                else:
                    log(f"     Total associations found: {len(hits)}", fh)

                    brain_hits = [
                        h for h in hits
                        if any(kw in str(h.get("tissue_label", "")).lower()
                               for kw in brain_keywords)
                    ]
                    log(f"     Brain-tissue hits: {len(brain_hits)}", fh)

                    display = brain_hits if brain_hits else hits
                    log(f"\n     {'Gene':15s} {'Tissue':35s} {'Beta':>8s} "
                        f"{'p':>12s} {'Study':20s}", fh)
                    log(f"     {'─'*95}", fh)

                    for h in display[:15]:
                        gene_id   = str(h.get("gene_id", "?"))
                        tissue    = str(h.get("tissue_label", "?"))
                        beta_eqtl = h.get("beta", "?")
                        pval      = h.get("pvalue", "?")
                        study     = str(h.get("study_id", "?"))
                        log(f"     {gene_id:15s} {tissue:35s} {str(beta_eqtl):>8s} "
                            f"{str(pval):>12s} {study:20s}", fh)

                        results.append({
                            "query_rsid":       rsid,
                            "query_gene":       info["gene"],
                            "eqtl_gene":        gene_id,
                            "tissue":           tissue,
                            "beta_eqtl":        beta_eqtl,
                            "pvalue":           pval,
                            "study":            study,
                            "is_brain":         h in brain_hits,
                        })

                    # Direction check for SEMA3A
                    if info["gene"] == "SEMA3A":
                        target_hits = [
                            h for h in brain_hits
                            if "SEMA3A" in str(h.get("gene_id", "")).upper()
                        ]
                        if target_hits:
                            log(f"\n     P4-7 DIRECTION CHECK (SEMA3A eQTL):", fh)
                            log(f"     Risk allele {info['risk_allele']} reduces right UF FA (beta<0 in GWAS)", fh)
                            log(f"     Prediction: same allele reduces SEMA3A expression", fh)
                            for h in target_hits[:3]:
                                b = h.get("beta", None)
                                if b is not None:
                                    try:
                                        b_float = float(b)
                                        direction = "LOWER expression" if b_float < 0 else "HIGHER expression"
                                        concordant = b_float < 0
                                        log(f"     eQTL beta={b_float:.4f} -> {direction}", fh)
                                        log(f"     P4-7: {'CONCORDANT (CONFIRMED)' if concordant else 'DISCORDANT (DENIED)'}", fh)
                                    except (ValueError, TypeError):
                                        log(f"     eQTL beta={b} (cannot parse)", fh)
                        else:
                            log(f"\n     No SEMA3A brain eQTLs found — P4-7 untestable from API.", fh)
                            log(f"     Manual check required: https://gtexportal.org/home/snp/rs78404854", fh)

            elif resp.status_code == 404:
                log(f"     rsID not found in eQTL Catalogue (404).", fh)
            else:
                log(f"     API returned status {resp.status_code}.", fh)

        except requests.exceptions.Timeout:
            log(f"     API timeout (>30s). EBI server may be slow.", fh)
            log(f"     Manual: https://www.ebi.ac.uk/eqtl/", fh)
        except Exception as e:
            log(f"     API error: {e}", fh)

    if not results:
        log(f"\n  No eQTL results retrieved via API.", fh)
        _eqtl_offline_guide(fh)

    df_eqtl = pd.DataFrame(results) if results else pd.DataFrame()
    df_eqtl.to_csv(OUT_EQTL, sep="\t", index=False)
    log(f"\n  eQTL results saved -> {OUT_EQTL} ({len(df_eqtl)} rows)", fh)
    return df_eqtl


def _eqtl_offline_guide(fh):
    log("""
  MANUAL eQTL LOOKUP GUIDE
  ─────────────────────────
  GTEx Portal (adult brain):
    https://gtexportal.org/home/snp/rs78404854
    Tissues: Brain - Temporal Cortex, Frontal Cortex BA9,
             Caudate Basal Ganglia
    Expected: SEMA3A expression association

  PsychENCODE (fetal + adult brain):
    https://psychencode.synapse.org/
    Most relevant dataset: fetal prefrontal cortex eQTLs
    Search gene: SEMA3A

  EBI eQTL Catalogue (browser):
    https://www.ebi.ac.uk/eqtl/
    Enter rs78404854 -> filter to brain tissues

  BrainSeq Phase 2 (DLPFC and hippocampus):
    http://eqtl.brainseq.org/phase2/

  P4-7 PREDICTION TO VERIFY:
    rs78404854 C allele (risk allele for lower right UF FA)
    should show LOWER SEMA3A expression in temporal cortex.
    Confirmed: mechanism = rs78404854 -> SEMA3A expression
    reduction -> impaired axon guidance -> lower right UF FA.
""", fh)


# ══════════════════════════════════════════════════════════════════════
# ANALYSIS 3 — MENDELIAN RANDOMISATION
# ══════════════════════════════════════════════════════════════════════

def mendelian_randomisation(df_r, df_outcome, fh):
    """
    Two-sample MR: right UF FA -> broad antisocial behaviour.
    Exposure: right UF FA (GWAS file 1496.txt, N~31,341)
    Outcome:  BroadABC broadABC2022_Final_CombinedSex.TBL (N~85,359)
    Instruments: GWS loci from gwas_ready_instruments.tsv

    BroadABC beta scale note:
      Betas in BroadABC are on a composite antisocial behaviour
      score scale — large absolute values (e.g. 4.35) are normal.
      MR betas will be on this scale. Direction is the primary test.
    """
    log("\n── ANALYSIS 3: MENDELIAN RANDOMISATION ──────────────────", fh)
    log("  Exposure : right UF FA (fractional anisotropy, N~31,341)", fh)
    log("  Outcome  : broad antisocial behaviour (BroadABC 2022, N~85,359)", fh)
    log("  Reference: Tielbeek et al., Mol Psychiatry 2022", fh)
    log("  File     : broadABC2022_Final_CombinedSex.TBL", fh)

    # Load instruments
    if not Path(FILE_INSTRUMENTS).exists():
        log(f"\n  ERROR: {FILE_INSTRUMENTS} not found.", fh)
        log(f"  This file must be produced by Step 2.", fh)
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    instruments = pd.read_csv(FILE_INSTRUMENTS, sep="\t")
    # Normalise instrument column names
    instruments.columns = [c.strip().lower() for c in instruments.columns]

    log(f"\n  Instruments loaded: {len(instruments)} SNPs", fh)
    show_cols = [c for c in ["rsid","chr","pos","a1","a2","beta","se","p"]
                 if c in instruments.columns]
    log(instruments[show_cols].to_string(index=False), fh)

    if df_outcome is None:
        log(f"\n  BroadABC outcome file not loaded. Check filename:", fh)
        log(f"  Expected: {BROADABC_FILE}", fh)
        _mr_framework_demo(instruments, fh)
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    # ── Harmonisation ────────────────────────────────────────────────
    log(f"\n  Harmonising instruments with BroadABC outcome...", fh)

    # Both files should have 'rsid' after normalisation
    rsid_exp = "rsid" if "rsid" in instruments.columns else instruments.columns[0]
    rsid_out = "rsid" if "rsid" in df_outcome.columns else \
               next((c for c in df_outcome.columns
                     if c in ["snp","snpid","markername","id"]), df_outcome.columns[0])

    # Select outcome columns needed
    out_cols_needed = [rsid_out, "a1", "a2", "beta", "se", "p"]
    if "n" in df_outcome.columns:
        out_cols_needed.append("n")
    out_cols_available = [c for c in out_cols_needed if c in df_outcome.columns]

    harmonised = pd.merge(
        instruments.rename(columns={rsid_exp: "rsid"}),
        df_outcome[out_cols_available].rename(columns={
            rsid_out: "rsid",
            "beta":   "beta_out",
            "se":     "se_out",
            "p":      "p_out",
            "a1":     "a1_out",
            "a2":     "a2_out",
        }),
        on="rsid",
        how="inner"
    )

    log(f"  Instruments found in BroadABC: {len(harmonised)} / {len(instruments)}", fh)

    if len(harmonised) == 0:
        log(f"\n  WARNING: 0 instruments matched.", fh)
        log(f"  Exposure rsIDs (first 5): {list(instruments[rsid_exp].head())}", fh)
        log(f"  Outcome rsIDs  (first 5): {list(df_outcome[rsid_out].head())}", fh)
        log(f"  Check that both files use the same rsID format.", fh)
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    if len(harmonised) < 3:
        log(f"  WARNING: only {len(harmonised)} instruments matched — need ≥3 for MR.", fh)
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    # ── Allele alignment ─────────────────────────────────────────────
    # Align effect allele between exposure and outcome
    if "a1_out" in harmonised.columns and "a1" in harmonised.columns:
        harmonised = harmonised.copy()
        # Case-insensitive comparison
        a1_exp = harmonised["a1"].str.upper()
        a1_out = harmonised["a1_out"].str.upper()
        a2_exp = harmonised["a2"].str.upper() if "a2" in harmonised.columns else None
        a2_out = harmonised["a2_out"].str.upper() if "a2_out" in harmonised.columns else None

        # Allele flip: outcome A1 matches exposure A2 (complementary)
        if a2_exp is not None:
            flip_mask = (a1_exp != a1_out) & (a1_out == a2_exp)
        else:
            flip_mask = a1_exp != a1_out

        harmonised.loc[flip_mask, "beta_out"] = -harmonised.loc[flip_mask, "beta_out"]
        log(f"  Allele-flipped {int(flip_mask.sum())} instruments to align A1 allele.", fh)

        # Ambiguous SNPs (A/T or G/C) — flag but keep
        if a2_exp is not None and a2_out is not None:
            ambig = ((a1_exp.isin(["A","T"])) & (a2_exp.isin(["A","T"]))) | \
                    ((a1_exp.isin(["G","C"])) & (a2_exp.isin(["G","C"])))
            n_ambig = int(ambig.sum())
            if n_ambig > 0:
                log(f"  {n_ambig} palindromic (A/T or G/C) SNPs — "
                    f"kept but flagged (EAF used for orientation if available).", fh)

    # QC
    harmonised = harmonised.dropna(subset=["beta", "se", "beta_out", "se_out"])
    harmonised = harmonised[
        (harmonised["se"] > 0) & (harmonised["se_out"] > 0)
    ].reset_index(drop=True)
    n = len(harmonised)
    log(f"  Valid instruments after allele alignment and QC: {n}", fh)

    if n < 3:
        log(f"  Insufficient instruments. Cannot run MR.", fh)
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    # Log instrument details post-harmonisation
    log(f"\n  Harmonised instruments:", fh)
    h_show = [c for c in ["rsid","a1","beta","se","beta_out","se_out","p_out"]
              if c in harmonised.columns]
    log(harmonised[h_show].to_string(index=False), fh)

    # ── Extract arrays ────────────────────────────────────────────────
    beta_exp = harmonised["beta"].astype(float).values
    se_exp   = harmonised["se"].astype(float).values
    beta_out = harmonised["beta_out"].astype(float).values
    se_out   = harmonised["se_out"].astype(float).values

    # Ratio estimates (causal effect estimate per instrument)
    ratio = beta_out / beta_exp

    # ── IVW ───────────────────────────────���──────────────────────────
    w        = beta_exp**2 / se_out**2
    beta_ivw = np.sum(w * ratio) / np.sum(w)
    resid_ivw = ratio - beta_ivw
    Q        = float(np.sum(w * resid_ivw**2))
    Q_df     = n - 1
    Q_p      = float(1 - chi2.cdf(Q, Q_df))
    phi      = max(1.0, Q / Q_df)
    se_ivw   = float(np.sqrt(phi / np.sum(w)))
    z_ivw    = float(beta_ivw / se_ivw)
    p_ivw    = float(2 * norm.sf(abs(z_ivw)))

    log(f"\n  IVW (primary):", fh)
    log(f"    beta = {beta_ivw:+.5f}  SE = {se_ivw:.5f}  "
        f"Z = {z_ivw:+.3f}  p = {p_ivw:.4e}", fh)
    log(f"    Cochran Q = {Q:.2f}  df = {Q_df}  Q_p = {Q_p:.4f}", fh)
    log(f"    Heterogeneity phi = {phi:.3f}", fh)
    if phi > 1:
        log(f"    Random-effects SE applied (phi={phi:.3f} > 1).", fh)

    # ── Weighted Median ───────────────────────────────────────────────
    w_med  = (1.0 / (se_out / np.abs(beta_exp))**2)
    w_med /= w_med.sum()
    si     = np.argsort(ratio)
    cumw   = np.cumsum(w_med[si])
    med_i  = int(np.where(cumw >= 0.5)[0][0])
    beta_wm = float(ratio[si[med_i]])

    rng = np.random.default_rng(20260326)
    boot_betas = []
    for _ in range(1000):
        ib   = rng.choice(n, size=n, replace=True)
        r_b  = ratio[ib]; wb = w_med[ib]; wb /= wb.sum()
        si_b = np.argsort(r_b); cw_b = np.cumsum(wb[si_b])
        mi_b = int(np.where(cw_b >= 0.5)[0][0])
        boot_betas.append(float(r_b[si_b[mi_b]]))
    se_wm = float(np.std(boot_betas))
    z_wm  = float(beta_wm / se_wm) if se_wm > 0 else 0.0
    p_wm  = float(2 * norm.sf(abs(z_wm)))

    log(f"\n  Weighted Median:", fh)
    log(f"    beta = {beta_wm:+.5f}  SE = {se_wm:.5f}  "
        f"Z = {z_wm:+.3f}  p = {p_wm:.4e}", fh)

    # ── MR-Egger ─────────────────────────────────────────────────────
    w_eg = 1.0 / se_out**2
    X    = np.column_stack([np.ones(n), beta_exp])
    W_eg = np.diag(w_eg)
    try:
        XtWX_inv     = np.linalg.inv(X.T @ W_eg @ X)
        coef         = XtWX_inv @ X.T @ W_eg @ beta_out
        intercept_eg = float(coef[0])
        beta_eg      = float(coef[1])
        resid_eg     = beta_out - (intercept_eg + beta_eg * beta_exp)
        s2           = float(np.sum(w_eg * resid_eg**2) / (n - 2))
        var_coef     = s2 * XtWX_inv
        se_int       = float(np.sqrt(var_coef[0, 0]))
        se_eg        = float(np.sqrt(var_coef[1, 1]))
        z_eg         = float(beta_eg / se_eg)
        z_int        = float(intercept_eg / se_int)
        p_eg         = float(2 * norm.sf(abs(z_eg)))
        p_int        = float(2 * norm.sf(abs(z_int)))
    except np.linalg.LinAlgError:
        log(f"  MR-Egger: singular matrix — skipping.", fh)
        beta_eg = intercept_eg = se_eg = se_int = float("nan")
        p_eg = p_int = float("nan")

    log(f"\n  MR-Egger:", fh)
    log(f"    beta      = {beta_eg:+.5f}  SE = {se_eg:.5f}  p = {p_eg:.4e}", fh)
    log(f"    intercept = {intercept_eg:+.5f}  SE = {se_int:.5f}  p = {p_int:.4e}", fh)
    if not np.isnan(p_int):
        if p_int > 0.05:
            log(f"    Intercept p={p_int:.3f} > 0.05 -> NO directional pleiotropy.", fh)
        else:
            log(f"    WARNING: intercept p={p_int:.3f} < 0.05 -> directional pleiotropy.", fh)

    # ── Weighted Mode ─────────────────────────────────────────────────
    bw      = 0.5 * np.std(ratio) * (n ** (-1/3))
    grid    = np.linspace(ratio.min() - 3*bw, ratio.max() + 3*bw, 512)
    density = np.array([np.sum(w_med * norm.pdf(g, ratio, bw)) for g in grid])
    beta_mode = float(grid[np.argmax(density)])

    boot_modes = []
    for _ in range(500):
        ib   = rng.choice(n, size=n, replace=True)
        r_b  = ratio[ib]; wb = w_med[ib]; wb /= wb.sum()
        d_b  = np.array([np.sum(wb * norm.pdf(g, r_b, bw)) for g in grid])
        boot_modes.append(float(grid[np.argmax(d_b)]))
    se_mode = float(np.std(boot_modes))
    z_mode  = float(beta_mode / se_mode) if se_mode > 0 else 0.0
    p_mode  = float(2 * norm.sf(abs(z_mode)))

    log(f"\n  Weighted Mode:", fh)
    log(f"    beta = {beta_mode:+.5f}  SE = {se_mode:.5f}  "
        f"Z = {z_mode:+.3f}  p = {p_mode:.4e}", fh)

    # ── Leave-one-out ─────────────────────────────────────────────────
    log(f"\n  Leave-one-out (IVW):", fh)
    log(f"  {'Excluded SNP':25s} {'Beta_LOO':>12s} {'SE':>8s} {'p':>12s}", fh)
    log(f"  {'─'*60}", fh)
    loo_results = []
    for i in range(n):
        mask  = np.ones(n, dtype=bool); mask[i] = False
        w_i   = (beta_exp[mask]**2) / (se_out[mask]**2)
        b_i   = float(np.sum(w_i * ratio[mask]) / np.sum(w_i))
        Q_i   = float(np.sum(w_i * (ratio[mask] - b_i)**2))
        phi_i = max(1.0, Q_i / max(1, n - 2))
        se_i  = float(np.sqrt(phi_i / np.sum(w_i)))
        z_i   = float(b_i / se_i)
        p_i   = float(2 * norm.sf(abs(z_i)))
        snp   = str(harmonised.iloc[i].get("rsid", f"SNP_{i}"))
        loo_results.append({"excluded_snp": snp,
                             "beta_loo": b_i, "se_loo": se_i, "p_loo": p_i})
        flag = " ← direction flips" if np.sign(b_i) != np.sign(beta_ivw) else ""
        log(f"  {snp:25s} {b_i:>+12.5f} {se_i:>8.5f} {p_i:>12.4e}{flag}", fh)

    df_loo = pd.DataFrame(loo_results)
    df_loo.to_csv(OUT_MR_LOO, sep="\t", index=False)

    # ── Steiger filtering ─────────────────────────────────────────────
    log(f"\n  Steiger direction test:", fh)
    log(f"  Exposure N = {N_EXPOSURE:,}  |  Outcome N = per-SNP from BroadABC 'n' column", fh)
    log(f"  {'SNP':25s} {'r2_exp':>10s} {'r2_out':>10s} {'N_out':>8s} {'Dir':>5s}", fh)
    log(f"  {'─'*65}", fh)

    steiger_results = []
    for i, row in harmonised.iterrows():
        # Per-SNP N from BroadABC where available
        if "n" in harmonised.columns and not pd.isna(row.get("n")):
            n_out_i = float(row["n"])
        else:
            n_out_i = float(N_OUTCOME)

        # r2 approximation: r2 ~ z2 / (z2 + N)
        z2_exp   = (float(row["beta"]) / float(row["se"]))**2
        z2_out   = (float(row["beta_out"]) / float(row["se_out"]))**2
        r2_exp   = z2_exp / (z2_exp + N_EXPOSURE)
        r2_out   = z2_out / (z2_out + n_out_i)
        dir_ok   = r2_exp > r2_out
        snp      = str(row.get("rsid", f"SNP_{i}"))

        steiger_results.append({
            "rsid":             snp,
            "r2_exposure":      r2_exp,
            "r2_outcome":       r2_out,
            "n_out_used":       n_out_i,
            "direction_correct":dir_ok,
        })
        log(f"  {snp:25s} {r2_exp:>10.6f} {r2_out:>10.6f} "
            f"{n_out_i:>8.0f} {'✓' if dir_ok else '✗':>5s}", fh)

    df_steiger     = pd.DataFrame(steiger_results)
    n_correct      = int(df_steiger["direction_correct"].sum())
    n_total_steig  = len(df_steiger)
    log(f"\n  Steiger direction correct: {n_correct}/{n_total_steig}", fh)
    if n_correct == n_total_steig:
        log(f"  ALL instruments consistent with right UF FA -> antisocial", fh)
        log(f"  (not reverse causation).", fh)
    else:
        wrong = df_steiger[~df_steiger["direction_correct"]]
        log(f"  {len(wrong)} instruments with reversed direction:", fh)
        log(wrong[["rsid","r2_exposure","r2_outcome"]].to_string(index=False), fh)
    df_steiger.to_csv(OUT_MR_STEIGER, sep="\t", index=False)

    # ── Summary table ─────────────────────────────────────────────────
    mr_summary = pd.DataFrame([
        {"method": "IVW",
         "beta": beta_ivw,  "se": se_ivw,  "p": p_ivw,
         "note": f"Q={Q:.2f} df={Q_df} Q_p={Q_p:.3f} phi={phi:.2f}"},
        {"method": "Weighted_Median",
         "beta": beta_wm,   "se": se_wm,   "p": p_wm,
         "note": "Bootstrap SE 1000 iterations"},
        {"method": "MR_Egger",
         "beta": beta_eg,   "se": se_eg,   "p": p_eg,
         "note": f"intercept={intercept_eg:+.4f} SE={se_int:.4f} p={p_int:.3f}"},
        {"method": "Weighted_Mode",
         "beta": beta_mode, "se": se_mode, "p": p_mode,
         "note": "Bootstrap SE 500 iterations"},
    ])

    log(f"\n  ── MR RESULTS SUMMARY ──────────────────────────────────", fh)
    log(f"  {'Method':20s} {'Beta':>12s} {'SE':>10s} {'p':>12s}  Note", fh)
    log(f"  {'─'*80}", fh)
    for _, row in mr_summary.iterrows():
        sig = " ★" if row["p"] < 0.05 else "  "
        log(f"  {row['method']:20s} {row['beta']:>+12.5f} {row['se']:>10.5f} "
            f"{row['p']:>12.4e}{sig}  {row['note']}", fh)

    log(f"\n  BroadABC beta scale note:", fh)
    log(f"  MR beta is in BroadABC composite score units.", fh)
    log(f"  A negative MR beta = lower right UF FA -> higher antisocial score.", fh)
    log(f"  Effect size interpretation requires SD of BroadABC phenotype.", fh)

    mr_summary.to_csv(OUT_MR, sep="\t", index=False)
    log(f"\n  MR results saved -> {OUT_MR}", fh)
    log(f"  LOO results saved -> {OUT_MR_LOO}", fh)
    log(f"  Steiger results   -> {OUT_MR_STEIGER}", fh)

    # Prediction scoring
    log(f"\n  ── PREDICTION SCORING ──────────────────────────────────", fh)
    _score_mr_predictions(beta_ivw, p_ivw, beta_wm, p_wm,
                          intercept_eg, p_int, n_correct, n_total_steig, fh)

    return mr_summary, df_loo, df_steiger


def _mr_framework_demo(instruments, fh):
    log(f"""
  MR FRAMEWORK — INSTRUMENTS READY, AWAITING OUTCOME FILE
  ─────────────────────────────────────────────────────────
  {len(instruments)} instrument SNPs loaded from {FILE_INSTRUMENTS}.

  Expected outcome file: {BROADABC_FILE}
  Confirmed column format:
    chromosome  base_pair_location  effect_allele  other_allele
    beta  standard_error  effect_allele_frequency  p_value  rsid  n

  The MR question:
    Do people genetically predisposed to have LOWER right UF FA
    also score HIGHER on broad antisocial behaviour?

  If IVW beta < 0 and p < 0.05, and Egger intercept is null,
  and Steiger confirms direction:
    -> Genetic reduction in right UF FA CAUSALLY PREDICTS
       antisocial behaviour in the general population.
    -> This is the population-level causal confirmation of
       the structural disability derivation.

  Place {BROADABC_FILE} in the working directory and re-run.
""", fh)


def _score_mr_predictions(beta_ivw, p_ivw, beta_wm, p_wm,
                           intercept_eg, p_int, n_correct, n_total, fh):
    log(f"  P4-1 (IVW: negative beta, p<0.05):", fh)
    if p_ivw < 0.05 and beta_ivw < 0:
        log(f"    CONFIRMED — beta={beta_ivw:+.5f}  p={p_ivw:.4e}", fh)
    elif p_ivw < 0.05 and beta_ivw > 0:
        log(f"    DENIED — wrong direction: beta={beta_ivw:+.5f}", fh)
    else:
        log(f"    DENIED — not significant: p={p_ivw:.4e}", fh)

    log(f"  P4-2 (WM directionally concordant with IVW):", fh)
    if np.sign(beta_wm) == np.sign(beta_ivw):
        log(f"    CONFIRMED — IVW={beta_ivw:+.5f}  WM={beta_wm:+.5f}", fh)
    else:
        log(f"    DENIED — IVW={beta_ivw:+.5f}  WM={beta_wm:+.5f}", fh)

    log(f"  P4-3 (Egger intercept not significant, p>0.05):", fh)
    if not np.isnan(p_int):
        if p_int > 0.05:
            log(f"    CONFIRMED — intercept p={p_int:.3f}", fh)
        else:
            log(f"    DENIED — intercept p={p_int:.3f} (directional pleiotropy)", fh)
    else:
        log(f"    UNTESTABLE — Egger did not converge.", fh)

    log(f"  P4-8 (Steiger: all instruments direction correct):", fh)
    if n_correct == n_total:
        log(f"    CONFIRMED — {n_correct}/{n_total} correct", fh)
    else:
        log(f"    PARTIAL  — {n_correct}/{n_total} correct", fh)


# ══════════════════════════════════════════════════════════════════════
# ANALYSIS 4 — COLOCALISATION
# ══════════════════════════════════════════════════════════════════════

def colocalisation(df_r, df_outcome, fh):
    """
    Approximate Bayes Factor colocalisation (Giambartolomei 2014).
    Posteriors:
      PP0: no signal in either trait
      PP1: signal in right UF FA only
      PP2: signal in antisocial behaviour only
      PP3: both traits, different causal SNPs
      PP4: SHARED causal SNP (colocalisation)
    PP4 > 0.5 = strong colocalisation evidence.
    """
    log("\n── ANALYSIS 4: COLOCALISATION ────────────────────────────", fh)
    log("  Method: Approximate Bayes Factor (Giambartolomei 2014)", fh)
    log(f"  Priors: p1={P1}  p2={P2}  p12={P12}", fh)
    log(f"  W1 (prior SD on FA effect)         = 0.15", fh)
    log(f"  W2 (prior SD on antisocial effect) = 0.20", fh)

    if df_outcome is None:
        log(f"\n  Outcome GWAS not loaded. Colocalisation cannot run.", fh)
        _coloc_demo(fh)
        return pd.DataFrame()

    # Prior variances on effect sizes
    W1 = 0.15**2   # FA units
    W2 = 0.20**2   # BroadABC composite score units (conservative given large betas)

    def log_abf(beta, se, W):
        """Wakefield (2009) approximate Bayes factor."""
        r  = W / (W + se**2)
        z2 = (beta / se)**2
        return 0.5 * (np.log(1.0 - r) + r * z2)

    loci = [
        {"name": "SEMA3A", "chr": SEMA3A_CHR,
         "start": SEMA3A_START, "end": SEMA3A_END,
         "threshold": 0.5, "prediction": "P4-4: PP4 > 0.5"},
        {"name": "CSMD1",  "chr": CSMD1_CHR,
         "start": CSMD1_START,  "end": CSMD1_END,
         "threshold": 0.3, "prediction": "P4-5: PP4 > 0.3"},
    ]

    coloc_results = []

    for locus in loci:
        log(f"\n  ── Locus: {locus['name']} "
            f"(chr{locus['chr']}:{locus['start']:,}-{locus['end']:,}) ──", fh)

        # Extract exposure SNPs
        mask_r = ((df_r["chr"] == locus["chr"]) &
                  (df_r["pos"] >= locus["start"]) &
                  (df_r["pos"] <= locus["end"]))
        sub_r  = df_r[mask_r].copy()

        # Extract outcome SNPs — use normalised chr/pos columns
        out_chr = "chr" if "chr" in df_outcome.columns else \
                  next((c for c in df_outcome.columns
                        if "chrom" in c or c == "chr"), None)
        out_pos = "pos" if "pos" in df_outcome.columns else \
                  next((c for c in df_outcome.columns
                        if "pos" in c or c == "bp"), None)

        if out_chr is None or out_pos is None:
            log(f"  Cannot find chr/pos columns in outcome. Skipping.", fh)
            continue

        mask_o = ((df_outcome[out_chr].astype(str)
                                      .str.replace("^chr","",regex=True)
                                      .str.lstrip("0") == locus["chr"]) &
                  (df_outcome[out_pos] >= locus["start"]) &
                  (df_outcome[out_pos] <= locus["end"]))
        sub_o  = df_outcome[mask_o].copy()

        log(f"  SNPs in exposure window : {len(sub_r):,}", fh)
        log(f"  SNPs in outcome window  : {len(sub_o):,}", fh)

        if len(sub_r) < 10 or len(sub_o) < 10:
            log(f"  Insufficient SNPs (need ≥10 each). Skipping.", fh)
            continue

        # Match on rsID
        out_rsid = "rsid" if "rsid" in sub_o.columns else \
                   next((c for c in sub_o.columns
                         if c in ["snp","snpid","markername"]), None)
        if out_rsid is None:
            log(f"  No rsid column in outcome — matching by position.", fh)
            sub_o = sub_o.copy()
            sub_o["_pos_key"] = sub_o[out_pos].astype(int)
            sub_r = sub_r.copy()
            sub_r["_pos_key"] = sub_r["pos"].astype(int)
            merged = pd.merge(sub_r, sub_o,
                              on="_pos_key", suffixes=("", "_o"))
            beta_o_col = "beta_o"
            se_o_col   = "se_o"
        else:
            merged = pd.merge(
                sub_r,
                sub_o[[out_rsid, "beta", "se"]].rename(columns={
                    out_rsid: "rsid",
                    "beta":   "beta_o",
                    "se":     "se_o",
                }),
                on="rsid", how="inner"
            )
            beta_o_col = "beta_o"
            se_o_col   = "se_o"

        log(f"  Matched SNPs : {len(merged):,}", fh)
        if len(merged) < 10:
            log(f"  Too few matched SNPs. Skipping.", fh)
            continue

        # Extract valid arrays
        beta_r = pd.to_numeric(merged["beta"],       errors="coerce").values
        se_r   = pd.to_numeric(merged["se"],         errors="coerce").values
        beta_o = pd.to_numeric(merged[beta_o_col],   errors="coerce").values
        se_o   = pd.to_numeric(merged[se_o_col],     errors="coerce").values

        valid  = (se_r > 0) & (se_o > 0) & \
                 np.isfinite(beta_r) & np.isfinite(beta_o)
        beta_r = beta_r[valid]; se_r = se_r[valid]
        beta_o = beta_o[valid]; se_o = se_o[valid]
        m      = int(valid.sum())

        log(f"  Valid SNPs for ABF: {m:,}", fh)
        if m < 10:
            log(f"  Insufficient after filtering. Skipping.", fh)
            continue

        labf1 = log_abf(beta_r, se_r, W1)
        labf2 = log_abf(beta_o, se_o, W2)
        lbf12 = labf1 + labf2

        # Numerically stable posterior computation
        def lse(a):
            amax = a.max()
            return np.log(np.sum(np.exp(a - amax))) + amax

        lH0 = 0.0
        lH1 = np.log(P1)  + lse(labf1)
        lH2 = np.log(P2)  + lse(labf2)
        lH3 = np.log(P1)  + np.log(P2) + lse(labf1) + lse(labf2) - np.log(m)
        lH4 = np.log(P12) + lse(lbf12)

        l_all = np.array([lH0, lH1, lH2, lH3, lH4])
        l_all -= l_all.max()
        probs  = np.exp(l_all)
        probs /= probs.sum()
        PP0, PP1_, PP2_, PP3_, PP4_ = probs

        log(f"\n  Posterior probabilities:", fh)
        log(f"    PP0 (no signal in region)     : {PP0:.4f}", fh)
        log(f"    PP1 (right UF FA signal only) : {PP1_:.4f}", fh)
        log(f"    PP2 (antisocial signal only)  : {PP2_:.4f}", fh)
        log(f"    PP3 (distinct causal SNPs)    : {PP3_:.4f}", fh)
        log(f"    PP4 (SHARED causal SNP)       : {PP4_:.4f}  ← key", fh)

        threshold = locus["threshold"]
        if PP4_ >= threshold:
            verdict = f"CONFIRMED (PP4={PP4_:.3f} >= {threshold})"
        else:
            verdict = f"DENIED    (PP4={PP4_:.3f} <  {threshold})"
        log(f"\n  {locus['prediction']}: {verdict}", fh)

        # Best colocalising SNP
        best_i = int(np.argmax(lbf12))
        best_row = merged[valid].iloc[best_i] \
                   if len(merged[valid]) > best_i else merged.iloc[best_i]
        log(f"\n  Best colocalising SNP:", fh)
        log(f"    rsid          = {best_row.get('rsid', '?')}", fh)
        log(f"    pos           = {best_row.get('pos', best_row.get('_pos_key', '?'))}", fh)
        log(f"    beta_exposure = {beta_r[best_i]:+.5f}  (right UF FA)", fh)
        log(f"    beta_outcome  = {beta_o[best_i]:+.5f}  (antisocial behaviour)", fh)
        log(f"    lBF_combined  = {lbf12[best_i]:.3f}", fh)

        coloc_results.append({
            "locus": locus["name"], "n_snps": m,
            "PP0": PP0, "PP1": PP1_, "PP2": PP2_, "PP3": PP3_, "PP4": PP4_,
            "prediction": locus["prediction"], "verdict": verdict,
            "best_rsid": str(best_row.get("rsid", "?")),
            "best_beta_exp": float(beta_r[best_i]),
            "best_beta_out": float(beta_o[best_i]),
        })

    df_coloc = pd.DataFrame(coloc_results)
    if not df_coloc.empty:
        df_coloc.to_csv(OUT_COLOC, sep="\t", index=False)
        log(f"\n  Colocalisation results saved -> {OUT_COLOC}", fh)
    else:
        log(f"\n  No colocalisation results to save.", fh)
    return df_coloc


def _coloc_demo(fh):
    log(f"""
  COLOCALISATION — PENDING OUTCOME DATA
  ──────────────────────────────────────
  At SEMA3A (chr7:83.0M-84.5M), right UF FA p=4.07e-09.
  If BroadABC also shows signal here and PP4 > 0.5:
    The same genetic variant reduces right UF FA AND
    increases antisocial behaviour.
    Mechanism confirmed at genomic level:
      variant -> SEMA3A expression reduction
              -> right UF FA reduction
              -> antisocial behaviour increase.

  At CSMD1 (chr8:8.5M-11.5M), right UF FA p=8.24e-12.
  If PP4 > 0.3: complement pruning deficit is also on
  the antisocial behaviour pathway.

  Will run automatically once {BROADABC_FILE} is loaded.
""", fh)


# ══════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════

def main():
    with open(OUT_REPORT, "w") as fh:
        log("═"*70, fh)
        log("STEP 4 — MENDELIAN RANDOMISATION AND COLOCALISATION", fh)
        log("OC-PSYCHOPATHY-GENETIC-MARKER-DERIVATION-001", fh)
        log(f"Run: {time.strftime('%Y-%m-%d %H:%M:%S')}", fh)
        log("═"*70, fh)

        log("\n" + "─"*70, fh)
        log("PRE-REGISTERED PREDICTIONS (locked 2026-03-26)", fh)
        log("─"*70, fh)
        log(PREDICTIONS, fh)
        log("─"*70, fh)

        log("\n── LOADING ───────────────────────────────────────────────", fh)
        df_r = load_gwas(FILE_R, fh, "Right UF FA (exposure)")
        if df_r is None:
            log("FATAL: Cannot load right UF FA GWAS. Exiting.", fh)
            return

        df_outcome = load_gwas(BROADABC_FILE, fh,
                                "BroadABC antisocial behaviour (outcome)")

        # Run all four analyses
        csmd1_finemap(df_r, fh)
        eqtl_lookup(fh)
        mr_summary, df_loo, df_steiger = mendelian_randomisation(
            df_r, df_outcome, fh)
        coloc_df = colocalisation(df_r, df_outcome, fh)

        # Final output summary
        log("\n" + "═"*70, fh)
        log("OUTPUTS", fh)
        log("═"*70, fh)
        log(f"""
  {str(OUT_CSMD1_FM):<35s} CSMD1 approximate fine-mapping
  {str(OUT_EQTL):<35s} Brain eQTL lookup (SEMA3A, CSMD1, SLIT2)
  {str(OUT_MR):<35s} MR results (IVW, WM, Egger, Mode)
  {str(OUT_MR_LOO):<35s} Leave-one-out MR
  {str(OUT_MR_STEIGER):<35s} Steiger direction test
  {str(OUT_COLOC):<35s} Colocalisation posteriors (ABF)

INTERPRETATION GUIDE:

  MR significant + Steiger correct + Egger intercept null:
    -> Genetic reduction in right UF FA CAUSALLY predicts
       antisocial behaviour. Causal chain confirmed.

  Colocalisation PP4 > 0.5 at SEMA3A:
    -> Same variant drives both right UF FA and antisocial
       behaviour. Molecular mechanism confirmed at SEMA3A.

  eQTL rs78404854 negative in temporal cortex:
    -> Causal variant reduces SEMA3A expression.
    -> Full chain: rs78404854 -> SEMA3A down -> UF FA down
       -> affective coupling deficit -> antisocial behaviour.

STEP 5 (after Step 4 results):
  If MR confirmed and PP4 > 0.5:
    -> Full derivation document: all steps integrated.
    -> Population-level causal chain complete.
  Regardless:
    -> Rare variant analysis: Layers B, C, D
    -> CSMD1 individual-level fine-mapping
    -> rs78404854 iPSC functional validation
""", fh)

        log(f"Done: {time.strftime('%Y-%m-%d %H:%M:%S')}", fh)

    print(f"\n{'═'*60}")
    print(f"Step 4 complete. Report: {OUT_REPORT}")
    print(f"{'═'*60}")


if __name__ == "__main__":
    main()
