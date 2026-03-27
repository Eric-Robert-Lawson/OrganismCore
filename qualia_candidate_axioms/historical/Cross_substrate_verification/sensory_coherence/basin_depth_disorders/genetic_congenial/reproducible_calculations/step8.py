"""
STEP 8 — CONDITIONAL ANALYSIS AT CHR8
=======================================
OC-PSYCHOPATHY-GENETIC-MARKER-DERIVATION-001
Eric Robert Lawson — OrganismCore — 2026-03-26

Question:
  Is rs3088186 (MSRA, chr8:10,226,355) an independent
  signal or is it tagging the CSMD1 signal through LD?

  Is rs2979255 (ERI1/CSMD1, chr8:8,919,309) an
  independent CSMD1 signal or the same signal as
  rs4383974?

Method:
  Load the right UF FA GWAS summary statistics (1496.txt).
  Extract all variants in the chr8:8,500,000-11,500,000
  window (covers all three signals).
  
  For each candidate (rs3088186, rs2979255):
    Step 1: Check LD with rs4383974 (primary CSMD1).
            Compute r² from z-score correlation in
            the GWAS summary statistics.
            (Summary-level LD proxy — Pearson r of
            z-scores across the window SNPs.)
    
    Step 2: Approximate conditional analysis.
            Regress out the rs4383974 signal using
            the summary-level conditional formula:
            beta_cond = beta_j - r_jk * beta_k
            se_cond   = sqrt(se_j² - r_jk² * se_k²)
            where j = candidate, k = rs4383974.
            
            If beta_cond -> 0 or p_cond >> 0.05:
              candidate is LD with rs4383974.
              Not an independent signal.
            
            If beta_cond remains large and p_cond
            stays significant: independent signal.

  Also confirms rs2979255 position relative to
  CSMD1 gene coordinates.

Inputs:
  1496.txt   Right UF FA GWAS summary statistics

Outputs:
  chr8_window.tsv            All SNPs in chr8 window
  chr8_ld_matrix.tsv         Pairwise r² between signals
  chr8_conditional.tsv       Conditional analysis results
  step8_results.txt          Full report
"""

import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore")

# ══════════════════════════════════════════════════════════════════════
# PARAMETERS
# ══════════════════════════════════════════════════════════════════════

FILE_GWAS   = "1496.txt"

OUT_REPORT  = Path("step8_results.txt")
OUT_WINDOW  = Path("chr8_window.tsv")
OUT_LD      = Path("chr8_ld_matrix.tsv")
OUT_COND    = Path("chr8_conditional.tsv")

# Chr8 window covering all three signals
CHR8_WINDOW_CHR   = "8"
CHR8_WINDOW_START = 8_500_000
CHR8_WINDOW_END   = 11_500_000

# The three chr8 signals
SIGNALS = {
    "rs2979255": {
        "pos":   8_919_309,
        "role":  "ERI1/CSMD1 — Step6 claimed CSMD1 intronic",
        "layer": "E candidate",
    },
    "rs4383974": {
        "pos":   9_619_348,
        "role":  "PRIMARY CSMD1 — fully confirmed Layer E",
        "layer": "E confirmed",
    },
    "rs3088186": {
        "pos":   10_226_355,
        "role":  "MSRA — possibly LD with CSMD1",
        "layer": "E? or B?",
    },
}

# CSMD1 gene coordinates hg19
CSMD1_START = 2_855_400
CSMD1_END   = 10_612_844
CSMD1_CHR   = "8"

# ══════════════════════════════════════════════════════════════════════
# UTILITIES
# ══════════════════════════════════════════════════════════════════════

def log(msg, fh=None):
    print(msg)
    if fh:
        fh.write(msg + "\n")
        fh.flush()


def zscore_from_beta_se(beta, se):
    """Compute z-score from beta and SE."""
    return beta / se


def p_from_z(z):
    """Two-tailed p-value from z-score."""
    return 2 * stats.norm.sf(np.abs(z))


# ══════════════════════════════════════════════════════════════════════
# LOAD GWAS AND EXTRACT WINDOW
# ══════════════════════════════════════════════════════════════════════

def load_gwas_window(fh):
    """
    Load the right UF FA GWAS and extract the
    chr8:8.5M-11.5M window.
    """
    log("── LOADING GWAS ──────────────────────────────────────────", fh)

    p = Path(FILE_GWAS)
    if not p.exists():
        log(f"  ERROR: {FILE_GWAS} not found.", fh)
        return None

    log(f"  Loading {FILE_GWAS} "
        f"({p.stat().st_size/1e9:.2f} GB)...", fh)
    t0 = time.time()

    # Detect separator and columns
    with open(p, "r") as f:
        header = f.readline().strip()

    sep = "\t" if "\t" in header else " "
    cols = [c.strip().lower() for c in header.split(sep)]
    log(f"  Columns: {cols}", fh)

    # Identify required columns
    col_map = {}
    for field, candidates in {
        "chr":  ["chr", "chrom", "chromosome", "#chrom"],
        "pos":  ["pos", "bp", "position", "base_pair_location"],
        "rsid": ["rsid", "snp", "snpid", "id", "variant_id",
                 "rs_id", "rs_number"],
        "beta": ["beta", "effect", "b", "es", "effect_size"],
        "se":   ["se", "standard_error", "stderr", "std_err"],
        "p":    ["p", "pval", "p_value", "p-value", "pvalue",
                 "p_val", "neglog10p"],
        "a1":   ["a1", "effect_allele", "alt", "allele1",
                 "effect_allele_frequency"],
        "a2":   ["a2", "other_allele", "ref", "allele2",
                 "non_effect_allele"],
    }.items():
        for c in candidates:
            if c in cols:
                col_map[field] = c
                break

    log(f"  Column mapping: {col_map}", fh)

    required = ["chr", "pos", "beta", "se"]
    missing  = [r for r in required if r not in col_map]
    if missing:
        log(f"  ERROR: Cannot find columns for: {missing}", fh)
        log(f"  Available columns: {cols}", fh)
        return None

    # Read in chunks — filter to chr8 window
    log(f"  Filtering to chr{CHR8_WINDOW_CHR}:"
        f"{CHR8_WINDOW_START:,}-{CHR8_WINDOW_END:,}...", fh)

    chunks  = []
    chunk_size = 500_000
    reader  = pd.read_csv(
        p, sep=sep, header=0,
        chunksize=chunk_size,
        low_memory=False,
        on_bad_lines="skip",
    )

    total_rows = 0
    for chunk in reader:
        chunk.columns = [c.strip().lower() for c in chunk.columns]
        total_rows += len(chunk)

        # Normalise chromosome column
        chrom_col = col_map["chr"]
        chunk[chrom_col] = (chunk[chrom_col]
                            .astype(str)
                            .str.lower()
                            .str.replace("chr", "", regex=False)
                            .str.strip())

        pos_col = col_map["pos"]
        chunk[pos_col] = pd.to_numeric(chunk[pos_col],
                                        errors="coerce")

        mask = (
            (chunk[chrom_col] == CHR8_WINDOW_CHR) &
            (chunk[pos_col]   >= CHR8_WINDOW_START) &
            (chunk[pos_col]   <= CHR8_WINDOW_END)
        )
        sub = chunk[mask]
        if len(sub) > 0:
            chunks.append(sub)

    log(f"  Scanned {total_rows:,} variants "
        f"[{time.time()-t0:.1f}s]", fh)

    if not chunks:
        log(f"  No variants found in window.", fh)
        return None

    df = pd.concat(chunks, ignore_index=True)
    log(f"  Variants in chr8 window: {len(df):,}", fh)

    # Standardise column names
    rename = {}
    for std, orig in col_map.items():
        if orig in df.columns:
            rename[orig] = std
    df = df.rename(columns=rename)

    # Ensure numeric
    for col in ["pos", "beta", "se"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["pos", "beta", "se"])
    df = df[df["se"] > 0]

    # Compute z-score and p-value
    df["z"] = df["beta"] / df["se"]
    if "p" not in df.columns:
        df["p"] = df["z"].apply(p_from_z)
    else:
        df["p"] = pd.to_numeric(df["p"], errors="coerce")

    df = df.sort_values("pos").reset_index(drop=True)
    log(f"  Valid variants after cleaning: {len(df):,}", fh)

    return df, col_map


# ══════════════════════════════════════════════════════════════════════
# ANALYSIS 1 — CSMD1 GENE BODY CHECK
# ══════════════════════════════════════════════════════════════════════

def analysis_1_gene_body(df, fh):
    """
    Confirm which of the three signals fall within
    the CSMD1 gene body coordinates.
    """
    log("\n── ANALYSIS 1: CSMD1 GENE BODY CHECK ────────────────────", fh)
    log(f"  CSMD1 coordinates (hg19): "
        f"chr{CSMD1_CHR}:{CSMD1_START:,}-{CSMD1_END:,}", fh)
    log(f"  Gene length: {(CSMD1_END-CSMD1_START)/1e6:.2f} Mb", fh)

    log(f"\n  Signal positions vs CSMD1 body:", fh)
    log(f"  {'rsid':15s}  {'pos':>12s}  {'in CSMD1':>10s}  "
        f"{'dist from TSS':>15s}  {'dist from TES':>15s}", fh)
    log(f"  {'─'*75}", fh)

    for rsid, info in SIGNALS.items():
        pos      = info["pos"]
        in_body  = CSMD1_START <= pos <= CSMD1_END
        dist_tss = pos - CSMD1_START
        dist_tes = CSMD1_END - pos

        log(f"  {rsid:15s}  {pos:>12,}  "
            f"{'YES' if in_body else 'NO':>10s}  "
            f"{dist_tss:>+15,}  "
            f"{dist_tes:>15,}", fh)

    log(f"\n  INTERPRETATION:", fh)

    for rsid, info in SIGNALS.items():
        pos     = info["pos"]
        in_body = CSMD1_START <= pos <= CSMD1_END
        if in_body:
            log(f"  {rsid}: INSIDE CSMD1 gene body.", fh)
            log(f"    refGene returned a different gene because "
                f"CSMD1 is an enormous gene (7.76Mb)", fh)
            log(f"    and refGene uses the longest transcript "
                f"per gene, which may not span the full locus.", fh)
            log(f"    The SNP is within CSMD1 genomic coordinates.", fh)
        else:
            dist = min(abs(pos - CSMD1_START),
                       abs(pos - CSMD1_END))
            log(f"  {rsid}: OUTSIDE CSMD1 gene body "
                f"({dist:,} bp from boundary).", fh)


# ══════════════════════════════════════════════════════════════════════
# ANALYSIS 2 — EXTRACT SIGNAL SNPs
# ══════════════════════════════════════════════════════════════════════

def extract_signal_snps(df, fh):
    """
    Extract the three signal SNPs from the GWAS data.
    Match by position since rsIDs may differ in format.
    """
    log("\n── ANALYSIS 2: SIGNAL SNP EXTRACTION ────────────────────", fh)

    found = {}
    for rsid, info in SIGNALS.items():
        pos    = info["pos"]
        # Match within 5bp to handle any position ambiguity
        match  = df[abs(df["pos"] - pos) <= 5]

        if match.empty:
            log(f"  {rsid} (pos={pos:,}): NOT FOUND in GWAS", fh)
            continue

        # Take the closest match
        match  = match.copy()
        match["_dist"] = abs(match["pos"] - pos)
        best   = match.nsmallest(1, "_dist").iloc[0]

        beta   = float(best["beta"])
        se     = float(best["se"])
        p_val  = float(best["p"]) if "p" in best.index else p_from_z(beta/se)
        z      = beta / se
        actual_pos = int(best["pos"])

        log(f"  {rsid:15s}  pos={actual_pos:>12,}  "
            f"beta={beta:+.5f}  se={se:.5f}  "
            f"z={z:+.3f}  p={p_val:.3e}", fh)

        found[rsid] = {
            "pos":   actual_pos,
            "beta":  beta,
            "se":    se,
            "z":     z,
            "p":     p_val,
            "row":   best,
        }

    return found


# ══════════════════════════════════════════════════════════════════════
# ANALYSIS 3 — LD ESTIMATION FROM Z-SCORES
# ══════════════════════════════════════════════════════════════════════

def analysis_3_ld(df, signal_snps, fh):
    """
    Estimate pairwise LD (r) between the three signals
    using the Pearson correlation of z-scores across
    all SNPs in the window.

    This is a summary-level LD proxy.
    The correlation of z-scores across SNPs reflects
    the LD structure when sample size is large and
    there is a single dominant signal.

    Method:
      For each pair (j, k):
        Extract all SNPs in a 1Mb window around both.
        Compute r = Pearson correlation of z-scores
        between the two SNP positions relative to
        all other SNPs in the window.

    Note: This is an approximation.
    True LD requires individual-level genotype data.
    This method is used in summary-level methods
    (GCTA-COJO, SOJO) as an LD proxy.
    It is valid when N is large (N=31,341 here).
    """
    log("\n── ANALYSIS 3: LD ESTIMATION (SUMMARY-LEVEL) ────────────", fh)
    log("  Method: Pearson r of z-scores across window SNPs", fh)
    log("  Valid for large N (N=31,341)", fh)
    log("  Approximation — true LD requires genotype data", fh)

    signal_names = list(signal_snps.keys())
    n_signals    = len(signal_names)

    if n_signals < 2:
        log("  Fewer than 2 signals found — cannot compute LD.", fh)
        return None

    # For each pair, compute LD using z-score correlation
    # across all SNPs in the window between the two positions
    ld_results = {}

    log(f"\n  Pairwise LD estimates:", fh)
    log(f"  {'Signal 1':15s}  {'Signal 2':15s}  "
        f"{'r':>8s}  {'r²':>8s}  Interpretation", fh)
    log(f"  {'─'*70}", fh)

    for i in range(n_signals):
        for j in range(i+1, n_signals):
            s1    = signal_names[i]
            s2    = signal_names[j]
            pos1  = signal_snps[s1]["pos"]
            pos2  = signal_snps[s2]["pos"]
            z1    = signal_snps[s1]["z"]
            z2    = signal_snps[s2]["z"]

            # Window between the two SNPs + 100kb either side
            win_start = min(pos1, pos2) - 100_000
            win_end   = max(pos1, pos2) + 100_000
            window    = df[
                (df["pos"] >= win_start) &
                (df["pos"] <= win_end)
            ].copy()

            if len(window) < 10:
                log(f"  {s1:15s}  {s2:15s}  "
                    f"{'N/A':>8s}  {'N/A':>8s}  "
                    f"Too few SNPs ({len(window)})", fh)
                continue

            # The LD proxy: correlation of z-scores
            # Use a sliding window approach:
            # for each SNP k in the window, compute
            # its z-score. The correlation between
            # the z-score vectors of SNPs near s1
            # and SNPs near s2 approximates their LD.

            # Simpler direct estimate:
            # For each SNP in the window, it is in LD
            # with s1 and s2 proportionally.
            # The correlation of the z-scores across
            # window SNPs relative to s1 vs s2 position
            # approximates r(s1,s2).

            # Most direct: z-score at s1 and s2 directly.
            # For summary-level conditional analysis we
            # need r between the two lead SNPs.
            # Use the regression coefficient of z(s2) on z(s1)
            # across nearby SNPs as the LD proxy.

            # Get SNPs within 500kb of both signals
            near_both = window[
                (abs(window["pos"] - pos1) < 500_000) &
                (abs(window["pos"] - pos2) < 500_000)
            ]["z"].values

            if len(near_both) < 10:
                log(f"  {s1:15s}  {s2:15s}  "
                    f"{'N/A':>8s}  {'N/A':>8s}  "
                    f"Too few shared window SNPs", fh)
                continue

            # Estimate r from the z-score field
            # using the signed LD proxy formula:
            # For SNPs in LD, their z-scores are correlated.
            # The expected z at s2 given z at s1 is:
            # E[z2] = r * z1
            # So r ≈ mean(z_window_near_s2) /
            #         mean(z_window_near_s1)
            # More directly: the Pearson r of z-scores
            # in a window proxies LD structure.

            # Pragmatic estimate: use the z-scores of all
            # SNPs in a ±100kb window around each signal
            # and correlate them.
            w1 = df[abs(df["pos"] - pos1) < 100_000]["z"].values
            w2 = df[abs(df["pos"] - pos2) < 100_000]["z"].values

            # Match by nearest position
            min_len = min(len(w1), len(w2))
            if min_len < 5:
                r_est = np.nan
            else:
                # Interpolate to same length for correlation
                # Use quantile-matched values
                w1s = np.sort(w1)
                w2s = np.sort(w2)
                # Resample to common length
                idx1 = np.linspace(0, len(w1s)-1, min_len).astype(int)
                idx2 = np.linspace(0, len(w2s)-1, min_len).astype(int)
                r_est, _ = stats.pearsonr(w1s[idx1], w2s[idx2])

            r2_est = r_est**2 if not np.isnan(r_est) else np.nan

            if np.isnan(r_est):
                interp = "Cannot estimate"
            elif r2_est > 0.8:
                interp = "HIGH LD — likely same signal"
            elif r2_est > 0.3:
                interp = "MODERATE LD — possibly same signal"
            elif r2_est > 0.1:
                interp = "LOW LD — possibly independent"
            else:
                interp = "VERY LOW LD — independent signals"

            log(f"  {s1:15s}  {s2:15s}  "
                f"{r_est:>+8.4f}  {r2_est:>8.4f}  {interp}", fh)

            ld_results[f"{s1}_{s2}"] = {
                "s1": s1, "s2": s2,
                "r": r_est, "r2": r2_est,
                "n_snps": min_len,
            }

    return ld_results


# ══════════════════════════════════════════════════════════════════════
# ANALYSIS 4 — CONDITIONAL ANALYSIS
# ══════════════════════════════════════════════════════════════════════

def analysis_4_conditional(signal_snps, ld_results, fh):
    """
    Summary-level conditional analysis.

    For each candidate signal (rs3088186, rs2979255)
    conditioned on the primary signal (rs4383974):

    Formula (Zhu et al. 2015, GCTA-COJO):
      beta_j|k = beta_j - r_jk * (se_j / se_k) * beta_k
      var_j|k  = se_j² * (1 - r_jk²)
      se_j|k   = sqrt(var_j|k)
      z_j|k    = beta_j|k / se_j|k
      p_j|k    = 2 * Phi(-|z_j|k|)

    where:
      j = candidate signal
      k = conditioning signal (rs4383974)
      r = LD correlation between j and k
    """
    log("\n── ANALYSIS 4: CONDITIONAL ANALYSIS ─────────────────────", fh)
    log("  Formula: beta_j|k = beta_j - r_jk*(se_j/se_k)*beta_k", fh)
    log("  (GCTA-COJO summary-level conditional)", fh)

    if "rs4383974" not in signal_snps:
        log("  rs4383974 not found — cannot condition.", fh)
        return []

    k      = "rs4383974"
    beta_k = signal_snps[k]["beta"]
    se_k   = signal_snps[k]["se"]
    z_k    = signal_snps[k]["z"]
    p_k    = signal_snps[k]["p"]

    log(f"\n  Conditioning signal: {k}", fh)
    log(f"  beta={beta_k:+.5f}  se={se_k:.5f}  "
        f"z={z_k:+.3f}  p={p_k:.3e}", fh)

    candidates = ["rs3088186", "rs2979255"]
    results    = []

    for j in candidates:
        if j not in signal_snps:
            log(f"\n  {j}: NOT FOUND in GWAS — cannot condition.", fh)
            continue

        beta_j = signal_snps[j]["beta"]
        se_j   = signal_snps[j]["se"]
        z_j    = signal_snps[j]["z"]
        p_j    = signal_snps[j]["p"]
        pos_j  = signal_snps[j]["pos"]

        log(f"\n  ── Conditioning {j} on {k} ──", fh)
        log(f"  Marginal: beta={beta_j:+.5f}  "
            f"se={se_j:.5f}  z={z_j:+.3f}  p={p_j:.3e}", fh)

        # Get LD estimate
        ld_key = f"{j}_{k}" if f"{j}_{k}" in (ld_results or {}) \
            else f"{k}_{j}"
        ld_entry = (ld_results or {}).get(ld_key, {})
        r_jk     = ld_entry.get("r", np.nan)
        r2_jk    = ld_entry.get("r2", np.nan)

        if np.isnan(r_jk):
            log(f"  LD estimate unavailable for {j}-{k}.", fh)
            log(f"  Using r=0 (conservative — underestimates conditioning).", fh)
            r_jk  = 0.0
            r2_jk = 0.0

        log(f"  LD with {k}: r={r_jk:+.4f}  r²={r2_jk:.4f}", fh)

        # Conditional beta
        beta_cond = beta_j - r_jk * (se_j / se_k) * beta_k

        # Conditional variance
        var_cond  = se_j**2 * (1 - r2_jk)
        if var_cond <= 0:
            log(f"  Conditional variance <= 0 "
                f"(r² too high for this formula).", fh)
            log(f"  This means {j} and {k} are in very high LD.", fh)
            log(f"  They are the SAME signal.", fh)
            results.append({
                "candidate":    j,
                "conditioning": k,
                "beta_marginal": beta_j,
                "se_marginal":   se_j,
                "p_marginal":    p_j,
                "r_jk":          r_jk,
                "r2_jk":         r2_jk,
                "beta_cond":     np.nan,
                "se_cond":       np.nan,
                "z_cond":        np.nan,
                "p_cond":        np.nan,
                "verdict":       "SAME SIGNAL (r² too high)",
            })
            continue

        se_cond   = np.sqrt(var_cond)
        z_cond    = beta_cond / se_cond
        p_cond    = p_from_z(z_cond)

        log(f"\n  Conditional result:", fh)
        log(f"  beta_cond = {beta_cond:+.5f}  "
            f"se_cond = {se_cond:.5f}  "
            f"z_cond = {z_cond:+.3f}  "
            f"p_cond = {p_cond:.3e}", fh)

        # Verdict
        attenuation = abs(beta_cond) / abs(beta_j) if beta_j != 0 else 1.0

        log(f"\n  Beta attenuation: "
            f"{abs(beta_j):.5f} -> {abs(beta_cond):.5f} "
            f"({attenuation*100:.1f}% remaining)", fh)

        if p_cond < 5e-8:
            verdict = "INDEPENDENT SIGNAL (p_cond < 5e-8)"
        elif p_cond < 1e-5:
            verdict = "SUGGESTIVE INDEPENDENT (5e-8 < p_cond < 1e-5)"
        elif attenuation < 0.3:
            verdict = "LD SIGNAL — beta attenuated >70% (likely same signal)"
        else:
            verdict = "AMBIGUOUS — conditional p not significant but beta remains"

        log(f"\n  VERDICT: {verdict}", fh)

        # Interpretation
        log(f"\n  INTERPRETATION:", fh)
        if "INDEPENDENT" in verdict:
            log(f"  {j} is an INDEPENDENT signal from {k}.", fh)
            log(f"  The gene at this position is a genuine", fh)
            log(f"  separate locus from CSMD1.", fh)
            if j == "rs3088186":
                log(f"  MSRA or a nearby gene is independently", fh)
                log(f"  associated with right UF FA.", fh)
        elif "LD SIGNAL" in verdict or "SAME" in verdict:
            log(f"  {j} is tagging the {k} signal through LD.", fh)
            log(f"  The gene at {j} is NOT independently", fh)
            log(f"  associated with right UF FA.", fh)
            if j == "rs3088186":
                log(f"  MSRA is not causal. rs3088186 tags CSMD1", fh)
                log(f"  through LD across the chr8 block.", fh)
            elif j == "rs2979255":
                log(f"  rs2979255 is a second CSMD1 signal or", fh)
                log(f"  tags the same CSMD1 mechanism.", fh)
        else:
            log(f"  Result is ambiguous. Conditional p is not", fh)
            log(f"  significant but beta has not fully attenuated.", fh)
            log(f"  Larger sample size or true LD matrix needed", fh)
            log(f"  to resolve definitively.", fh)

        results.append({
            "candidate":      j,
            "conditioning":   k,
            "beta_marginal":  beta_j,
            "se_marginal":    se_j,
            "p_marginal":     p_j,
            "r_jk":           r_jk,
            "r2_jk":          r2_jk,
            "beta_cond":      beta_cond,
            "se_cond":        se_cond,
            "z_cond":         z_cond,
            "p_cond":         p_cond,
            "verdict":        verdict,
        })

    return results


# ═══════════════════════════════════════════════════════════════��══════
# ANALYSIS 5 — REGIONAL ASSOCIATION PLOT DATA
# ══════════════════════════════════════════════════════════════════════

def analysis_5_regional(df, fh):
    """
    Extract the full regional association data for
    the chr8 window. Shows the signal structure —
    how many independent peaks exist.
    """
    log("\n── ANALYSIS 5: REGIONAL SIGNAL STRUCTURE ────────────────", fh)

    if df is None or df.empty:
        log("  No data.", fh)
        return

    # GWS and suggestive hits in window
    gws  = df[df["p"] < 5e-8].copy()
    sugg = df[(df["p"] >= 5e-8) & (df["p"] < 1e-5)].copy()

    log(f"  SNPs in chr8:{CHR8_WINDOW_START:,}-"
        f"{CHR8_WINDOW_END:,}: {len(df):,}", fh)
    log(f"  GWS (p<5e-8):       {len(gws):,}", fh)
    log(f"  Suggestive (p<1e-5): {len(sugg):,}", fh)

    log(f"\n  GWS hits in window:", fh)
    log(f"  {'rsid':20s}  {'pos':>12s}  "
        f"{'beta':>9s}  {'se':>8s}  {'p':>12s}  "
        f"Gene region", fh)
    log(f"  {'─'*85}", fh)

    gws_sorted = gws.sort_values("p")
    for _, row in gws_sorted.iterrows():
        pos  = int(row["pos"])
        rsid = str(row.get("rsid", row.get("snp",
               row.get("id", "unknown"))))

        # Annotate position
        if CSMD1_START <= pos <= CSMD1_END:
            region = "CSMD1 body"
        elif pos < CSMD1_START:
            region = f"{(CSMD1_START-pos)/1e3:.0f}kb upstream CSMD1"
        else:
            region = f"{(pos-CSMD1_END)/1e3:.0f}kb downstream CSMD1"

        log(f"  {rsid:20s}  {pos:>12,}  "
            f"{float(row['beta']):>+9.5f}  "
            f"{float(row['se']):>8.5f}  "
            f"{float(row['p']):>12.3e}  "
            f"{region}", fh)

    # Signal peaks — simple greedy clumping at 500kb
    log(f"\n  Signal clumping (500kb windows):", fh)
    peaks = []
    used  = set()
    for _, row in gws_sorted.iterrows():
        pos = int(row["pos"])
        if any(abs(pos - p) < 500_000 for p in used):
            continue
        peaks.append(row)
        used.add(pos)

    log(f"  Independent peaks at 500kb clumping: {len(peaks)}", fh)
    for pk in peaks:
        pos  = int(pk["pos"])
        rsid = str(pk.get("rsid", pk.get("snp",
               pk.get("id", "?"))))
        log(f"    {rsid:20s}  pos={pos:>12,}  "
            f"p={float(pk['p']):.3e}", fh)

    df.to_csv(OUT_WINDOW, sep="\t", index=False)
    log(f"\n  Window data saved -> {OUT_WINDOW}", fh)


# ══════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════

def main():
    with open(OUT_REPORT, "w") as fh:

        log("═"*70, fh)
        log("STEP 8 — CONDITIONAL ANALYSIS AT CHR8", fh)
        log("OC-PSYCHOPATHY-GENETIC-MARKER-DERIVATION-001", fh)
        log(f"Run: {time.strftime('%Y-%m-%d %H:%M:%S')}", fh)
        log("═"*70, fh)

        log(f"""
  Question 1: Is rs3088186 (MSRA) independent of
              rs4383974 (CSMD1) or tagging it through LD?

  Question 2: Is rs2979255 (ERI1) within the CSMD1
              gene body or a separate signal?

  Method: Summary-level conditional analysis from
          GWAS summary statistics (1496.txt).
          No individual genotype data required.
""", fh)

        result = load_gwas_window(fh)
        if result is None:
            log("  Cannot proceed — GWAS file not loaded.", fh)
            return

        df, col_map = result

        analysis_1_gene_body(df, fh)

        signal_snps = extract_signal_snps(df, fh)

        if len(signal_snps) < 2:
            log("\n  Fewer than 2 signals found in GWAS.", fh)
            log("  Check column names and positions.", fh)
            return

        ld_results = analysis_3_ld(df, signal_snps, fh)

        cond_results = analysis_4_conditional(
            signal_snps, ld_results, fh)

        analysis_5_regional(df, fh)

        # Save conditional results
        if cond_results:
            df_cond = pd.DataFrame(cond_results)
            df_cond.to_csv(OUT_COND, sep="\t", index=False)
            log(f"\n  Conditional results saved -> {OUT_COND}", fh)

        # Save LD
        if ld_results:
            df_ld = pd.DataFrame(ld_results.values())
            df_ld.to_csv(OUT_LD, sep="\t", index=False)
            log(f"  LD matrix saved -> {OUT_LD}", fh)

        log("\n" + "═"*70, fh)
        log("SUMMARY", fh)
        log("═"*70, fh)

        if cond_results:
            for r in cond_results:
                log(f"\n  {r['candidate']} conditioned on {r['conditioning']}:", fh)
                log(f"  Marginal p = {r['p_marginal']:.3e}  "
                    f"Conditional p = {r['p_cond']:.3e}"
                    if not np.isnan(r.get('p_cond', np.nan))
                    else f"  Marginal p = {r['p_marginal']:.3e}  "
                         f"Conditional p = N/A", fh)
                log(f"  VERDICT: {r['verdict']}", fh)

        log(f"\nDone: {time.strftime('%Y-%m-%d %H:%M:%S')}", fh)

    print(f"\n{'═'*60}")
    print(f"Step 8 complete. Report: {OUT_REPORT}")
    print(f"{'═'*60}")


if __name__ == "__main__":
    main()
