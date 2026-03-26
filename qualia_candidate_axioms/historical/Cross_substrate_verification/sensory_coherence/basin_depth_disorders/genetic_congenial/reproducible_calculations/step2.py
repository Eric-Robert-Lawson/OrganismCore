"""
STEP 2 — CALCULATION
=====================================================
OC-PSYCHOPATHY-GENETIC-MARKER-DERIVATION-001
Eric Robert Lawson — OrganismCore — 2026-03-26

Files required (same directory):
    1496.txt   Right UF FA  (IDP 25100, N~31k)
    1497.txt   Left  UF FA  (IDP 25101, N~31k)

Candidate gene sets (from derivation document):
    Layer A — Axon guidance failure:
        SEMA3A, SEMA3D, ROBO1, SLIT2
    Layer B — Myelination timing failure:
        MBP, MAG, PLP1
    Layer C — OXYTOCIN coupling consolidation failure:
        OXTR (specific SNP rs53576 flagged explicitly)
    Layer D — Lateralisation specification failure:
        LRRTM1, PCDH11X/Y, CNTNAP2
        (best available proxies — derivation names the
         function, not specific genes. These are the
         literature's strongest lateralisation candidates.)

Outputs:
    results_summary.txt
    top_hits_right_UF.tsv
    top_hits_left_UF.tsv
    top_hits_asymmetry.tsv
    candidate_genes_all_layers.tsv
    gwas_ready_instruments.tsv
"""

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import ndtr
from scipy.stats import chi2

# ── Files ──────────────────────────────────────────────────────────────────────
FILE_R = "1496.txt"
FILE_L = "1497.txt"

# ── Thresholds ─────────────────────────────────────────────────────────────────
GWS_THRESH  = 5e-8
SUG_THRESH  = 1e-6
CAND_THRESH = 1e-4
MAX_SE      = 0.5

# ── Candidate genes — all four build programme layers ─────────────────────────
#
# Windows: gene body ± 250kb (GRCh37/hg19)
# Sources: Ensembl release 109
#
# Layer A — Axon guidance (temporal-frontal UF pathfinding)
#   SEMA3A: chr7  — semaphorin, UF-specific guidance confirmed in GWAS
#   SEMA3D: chr7  — semaphorin, white matter tract-specific, derivation named
#   ROBO1:  chr3  — roundabout, hemispheric axon decision points
#   SLIT2:  chr4  — slit guidance ligand, ROBO1 partner
#
# Layer B — Myelination timing (right UF latest myelination window)
#   MBP:    chr18 — myelin basic protein
#   MAG:    chr19 — myelin-associated glycoprotein
#   PLP1:   chrX  — proteolipid protein 1
#
# Layer C — OXTR coupling consolidation
#   OXTR:   chr3  — oxytocin receptor
#                   rs53576 explicitly named in derivation document
#
# Layer D — Lateralisation specification
#   LRRTM1:   chr2  — leucine-rich repeat transmembrane neuronal 1
#                     strongest genetic association with brain
#                     left-right asymmetry in literature
#   PCDH11X:  chrX  — protocadherin 11, human-specific sex chromosome pair
#                     PCDH11X/Y implicated in human-specific brain lateralisation
#   CNTNAP2:  chr7  — contactin-associated protein-like 2
#                     asymmetric expression, implicated in language lateralisation
#                     (language lateralisation and UF asymmetry co-determined)

GENES = {
    # ── Layer A: Axon guidance ─────────────────────────────────────────────
    "SEMA3A":  {"chr": "7",  "start":  83294422, "end":  83953344, "layer": "A",
                "description": "Semaphorin-3A — UF axon guidance, confirmed GWAS"},
    "SEMA3D":  {"chr": "7",  "start":  83953344, "end":  84680000, "layer": "A",
                "description": "Semaphorin-3D — WM tract-specific guidance"},
    "ROBO1":   {"chr": "3",  "start":  78421879, "end":  79404206, "layer": "A",
                "description": "Roundabout-1 — hemispheric axon decision points"},
    "SLIT2":   {"chr": "4",  "start":  20260577, "end":  21094926, "layer": "A",
                "description": "Slit guidance ligand 2 — ROBO1 partner"},

    # ── Layer B: Myelination timing ────────────────────────────────────────
    "MBP":     {"chr": "18", "start":  74435940, "end":  75064555, "layer": "B",
                "description": "Myelin basic protein — myelination structural component"},
    "MAG":     {"chr": "19", "start":  35171502, "end":  35691199, "layer": "B",
                "description": "Myelin-associated glycoprotein — myelination timing"},
    "PLP1":    {"chr": "X",  "start": 102781428, "end": 103310355, "layer": "B",
                "description": "Proteolipid protein 1 — myelin quality"},

    # ── Layer C: OXTR coupling consolidation ──────────────────────────────
    "OXTR":    {"chr": "3",  "start":   8505088, "end":   9021564, "layer": "C",
                "description": "Oxytocin receptor — coupling consolidation signal",
                "key_snp": "rs53576"},

    # ── Layer D: Lateralisation specification ─────────────────────────────
    "LRRTM1":  {"chr": "2",  "start": 135131311, "end": 135649700, "layer": "D",
                "description": "LRRTM1 — strongest genetic lateralisation signal"},
    "PCDH11X": {"chr": "X",  "start":  91261878, "end":  92173588, "layer": "D",
                "description": "Protocadherin-11X — human-specific lateralisation"},
    "CNTNAP2": {"chr": "7",  "start": 145813453, "end": 148118090, "layer": "D",
                "description": "CNTNAP2 — language/UF asymmetry co-determination"},
}

# OXTR key SNP named in derivation
OXTR_KEY_SNP = "rs53576"

# ── Outputs ────────────────────────────────────────────────────────────────────
OUT_SUMMARY     = Path("results_summary.txt")
OUT_RIGHT_HITS  = Path("top_hits_right_UF.tsv")
OUT_LEFT_HITS   = Path("top_hits_left_UF.tsv")
OUT_ASYM_HITS   = Path("top_hits_asymmetry.tsv")
OUT_CANDIDATES  = Path("candidate_genes_all_layers.tsv")
OUT_INSTRUMENTS = Path("gwas_ready_instruments.tsv")


# ══���═══════════════════════════════════════════════════════════════════
# UTILITIES
# ══════════════════════════════════════════════════════════════════════

def log(msg, fh=None):
    print(msg)
    if fh:
        fh.write(msg + "\n")
        fh.flush()


def lambda_gc(p_values):
    """Genomic inflation factor."""
    chisq = chi2.ppf(1 - np.clip(p_values, 1e-300, 1), df=1)
    return float(np.median(chisq) / chi2.ppf(0.5, df=1))


def clump(df, p_col, window_kb=500):
    """Distance-based clumping — keep top SNP per window."""
    if df.empty:
        return df
    window_bp = window_kb * 1000
    df = df.sort_values(p_col).copy()
    kept = []
    sentinels = {}      # chr -> [pos, ...]
    for _, row in df.iterrows():
        ch = str(row["chr"])
        bp = int(row["pos"])
        used = sentinels.get(ch, [])
        if not any(abs(bp - s) < window_bp for s in used):
            kept.append(row)
            used.append(bp)
            sentinels[ch] = used
    return pd.DataFrame(kept)


# ══════════════════════════════════════════════════════════════════════
# LOAD
# ══════════════════════════════════════════════════════════════════════

def load(filepath, label, fh):
    p = Path(filepath)
    if not p.exists():
        p = Path(filepath + ".gz")
    if not p.exists():
        raise FileNotFoundError(f"Cannot find {filepath}")

    log(f"\n  Loading {label}  ({p.stat().st_size/1e6:.0f} MB)...", fh)
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

    # Normalise chr: strip leading zeros
    df["chr"] = df["chr"].str.lstrip("0").replace("", "0")

    # Quality filter
    n0 = len(df)
    df = df[(df["se"] > 0) & (df["se"] <= MAX_SE)].dropna(
        subset=["beta", "se", "p"])
    log(f"  {len(df):,} variants after QC  "
        f"({n0 - len(df):,} removed)  [{time.time()-t0:.1f}s]", fh)
    return df


# ══════════════════════════════════════════════════════════════════════
# ASYMMETRY INDEX
# ══════════════════════════════════════════════════════════════════════

def compute_asymmetry(df_r, df_l, fh):
    """
    beta_asym = beta_R - beta_L
    se_asym   = sqrt(se_R^2 + se_L^2)
    p_asym    = 2-tailed p from Z = beta_asym / se_asym

    Represents: genetic effect on right-lateralised UF elaboration.
    Variants with negative beta_asym reduce the right > left advantage.
    This is the Layer D / Layer 6 signal.
    """
    log("\n  Computing asymmetry index...", fh)

    r = df_r[df_r["rsid"].str.startswith("rs")][
        ["rsid", "chr", "pos", "a1", "a2", "beta", "se", "p", "lp"]
    ].copy()
    l = df_l[df_l["rsid"].str.startswith("rs")][
        ["rsid", "beta", "se"]
    ].copy()

    m = pd.merge(r, l, on="rsid", suffixes=("_R", "_L"))
    log(f"  Merged on rsID: {len(m):,} variants", fh)

    m["beta_asym"] = m["beta_R"].astype(np.float64) - \
                     m["beta_L"].astype(np.float64)
    m["se_asym"]   = np.sqrt(m["se_R"].astype(np.float64)**2 +
                             m["se_L"].astype(np.float64)**2)
    m["z_asym"]    = m["beta_asym"] / m["se_asym"]
    m["p_asym"]    = 2.0 * (1.0 - ndtr(np.abs(m["z_asym"])))
    m["lp_asym"]   = -np.log10(m["p_asym"].clip(lower=1e-300))
    return m


# ══════════════════════════════════════════════════════════════════════
# CANDIDATE GENE ANALYSIS
# ══════════════════════════════════════════════════════════════════════

def candidate_analysis(df_r, df_l, df_asym, fh):
    """
    For each candidate gene across all four layers:
    - Extract all SNPs in ±250kb window
    - Report count, best p (right UF), best p (asymmetry),
      top SNP, effect direction
    - For OXTR: explicitly look up rs53576
    """
    log("\n  Candidate gene results by layer:", fh)

    # Header
    log(f"\n  {'Gene':10s} {'L':2s} {'Chr':>4s} "
        f"{'N_SNPs':>8s} {'Best_p_R':>12s} {'Top_SNP':>15s} "
        f"{'Beta_R':>8s} {'Best_p_asym':>12s} {'Note'}", fh)
    log(f"  {'─'*100}", fh)

    records = []
    all_region_snps = []

    for layer in ["A", "B", "C", "D"]:
        layer_genes = {g: v for g, v in GENES.items() if v["layer"] == layer}

        for gene, info in layer_genes.items():
            ch = str(info["chr"])
            s, e = info["start"], info["end"]

            # Right UF
            mask_r = (df_r["chr"] == ch) & \
                     (df_r["pos"] >= s) & (df_r["pos"] <= e)
            reg_r = df_r[mask_r].copy()
            reg_r["gene"] = gene
            reg_r["layer"] = layer
            reg_r["description"] = info["description"]
            all_region_snps.append(reg_r)

            # Asymmetry
            mask_a = (df_asym["chr"] == ch) & \
                     (df_asym["pos"] >= s) & (df_asym["pos"] <= e)
            reg_a = df_asym[mask_a]

            n_r      = len(reg_r)
            best_p_r = reg_r["p"].min()      if n_r > 0 else np.nan
            best_p_a = reg_a["p_asym"].min() if len(reg_a) > 0 else np.nan

            if n_r > 0:
                top = reg_r.loc[reg_r["p"].idxmin()]
                top_snp  = top["rsid"]
                top_beta = float(top["beta"])
            else:
                top_snp = "—"; top_beta = np.nan

            # Note for OXTR key SNP
            note = ""
            if gene == "OXTR":
                rs53576_row = reg_r[reg_r["rsid"] == OXTR_KEY_SNP]
                if not rs53576_row.empty:
                    rs_p    = float(rs53576_row["p"].values[0])
                    rs_beta = float(rs53576_row["beta"].values[0])
                    note = f"rs53576: p={rs_p:.2e} beta={rs_beta:.4f}"
                else:
                    note = f"rs53576: NOT IN DATASET"

            log(f"  {gene:10s} {layer:2s} {ch:>4s} "
                f"{n_r:>8,} {best_p_r:>12.2e} {str(top_snp):>15s} "
                f"{top_beta:>8.4f} {best_p_a:>12.2e}  {note}", fh)

            records.append({
                "layer": layer, "gene": gene, "chr": ch,
                "description": info["description"],
                "n_snps_in_window": n_r,
                "best_p_right_UF": best_p_r,
                "top_snp_right_UF": top_snp,
                "beta_at_top_snp": top_beta,
                "best_p_asymmetry": best_p_a,
                "note": note,
            })

        log(f"  {'·'*60}", fh)   # layer separator

    # Layer ranking
    summary_df = pd.DataFrame(records)
    log(f"\n  Layer ranking by minimum p-value (right UF FA):", fh)
    layer_best = summary_df.groupby("layer")["best_p_right_UF"].min().sort_values()
    for lay, p_val in layer_best.items():
        interpretation = {
            "A": "Axon guidance failure",
            "B": "Myelination timing failure",
            "C": "OXTR coupling consolidation failure",
            "D": "Lateralisation specification failure",
        }.get(lay, "")
        log(f"    Layer {lay} ({interpretation:40s}): best p = {p_val:.2e}", fh)

    strongest_layer = layer_best.index[0]
    log(f"\n  Strongest signal: Layer {strongest_layer}", fh)
    log(f"  Interpretation: the most common build programme failure mode", fh)
    log(f"  in this population is the {interpretation} pathway.", fh)

    # Combine all candidate SNPs
    all_cand_df = pd.concat(all_region_snps, ignore_index=True) \
                    .sort_values("p") if all_region_snps else pd.DataFrame()

    return summary_df, all_cand_df


# ══════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════��═════════════════════

def main():
    # Dependency check
    try:
        import scipy
    except ImportError:
        print("Run:  pip install pandas numpy scipy")
        sys.exit(1)

    with open(OUT_SUMMARY, "w") as fh:

        log("═"*70, fh)
        log("CALCULATION RESULTS", fh)
        log("OC-PSYCHOPATHY-GENETIC-MARKER-DERIVATION-001", fh)
        log("Right UF Build Programme — Four-Layer Candidate Analysis", fh)
        log(f"Run: {time.strftime('%Y-%m-%d %H:%M:%S')}", fh)
        log("═"*70, fh)
        log("""
Layers under test:
  A — Axon guidance     : SEMA3A, SEMA3D, ROBO1, SLIT2
  B — Myelination       : MBP, MAG, PLP1
  C — OXTR coupling     : OXTR  (rs53576 explicitly tracked)
  D — Lateralisation    : LRRTM1, PCDH11X, CNTNAP2
""", fh)

        # ── Load ──────────────────────────────────────────────────────
        log("── LOADING ───────────────────────────────────────────────", fh)
        df_r = load(FILE_R, "Right UF FA (1496)", fh)
        df_l = load(FILE_L, "Left  UF FA (1497)", fh)

        # ── Global stats ──────────────────────────────────────────────
        log("\n── GLOBAL STATISTICS ─────────────────────────────────────", fh)
        for label, df in [("Right UF FA", df_r), ("Left UF FA", df_l)]:
            lgc = lambda_gc(df["p"].values)
            gws = (df["p"] < GWS_THRESH).sum()
            sug = (df["p"] < SUG_THRESH).sum()
            log(f"\n  {label}:", fh)
            log(f"    Variants        : {len(df):,}", fh)
            log(f"    Lambda GC       : {lgc:.4f}", fh)
            log(f"    GWS  p<5e-8     : {gws:,}", fh)
            log(f"    Suggestive p<1e-6: {sug:,}", fh)

        # ── GWS hits ──────────────────────────────────────────────────
        log("\n── GENOME-WIDE SIGNIFICANT HITS ──────────────────────────", fh)

        for label, df, out_path in [
            ("Right UF FA", df_r, OUT_RIGHT_HITS),
            ("Left  UF FA", df_l, OUT_LEFT_HITS),
        ]:
            hits = df[df["p"] < GWS_THRESH].sort_values("p")
            thresh_used = GWS_THRESH
            if hits.empty:
                log(f"  {label}: 0 GWS hits — using p<1e-6", fh)
                hits = df[df["p"] < SUG_THRESH].sort_values("p")
                thresh_used = SUG_THRESH

            clumped = clump(hits, "p")
            log(f"\n  {label}: {len(hits):,} hits at p<{thresh_used:.0e}  "
                f"-> {len(clumped)} independent loci after clumping", fh)

            if not clumped.empty:
                show = ["rsid","chr","pos","a1","a2","beta","se","p"]
                log(clumped[show].head(20).to_string(index=False), fh)

            hits.to_csv(out_path, sep="\t", index=False)
            log(f"  Saved -> {out_path}", fh)

        # ── Asymmetry index ────────────────────────────────────��──────
        log("\n── ASYMMETRY INDEX (RIGHT − LEFT UF FA) ──────────────────", fh)
        log("  Novel Layer D / Layer 6 exposure.", fh)
        log("  Variants with p_asym < 5e-8 predict right > left UF", fh)
        log("  elaboration — the human-specific lateralised structure.", fh)
        df_asym = compute_asymmetry(df_r, df_l, fh)

        lgc_a = lambda_gc(df_asym["p_asym"].values)
        gws_a = (df_asym["p_asym"] < GWS_THRESH).sum()
        log(f"\n  Asymmetry variants    : {len(df_asym):,}", fh)
        log(f"  Lambda GC             : {lgc_a:.4f}", fh)
        log(f"  GWS hits p<5e-8       : {gws_a:,}", fh)
        log(f"  Mean beta_asym        : {df_asym['beta_asym'].mean():.6f}  "
            f"(0 = symmetric population)", fh)
        log(f"  beta_asym > 0         : "
            f"{(df_asym['beta_asym'] > 0).sum():,}  "
            f"(SNPs that increase right > left)", fh)
        log(f"  beta_asym < 0         : "
            f"{(df_asym['beta_asym'] < 0).sum():,}  "
            f"(SNPs that reduce right > left)", fh)

        hits_asym = df_asym[df_asym["p_asym"] < GWS_THRESH].sort_values("p_asym")
        if hits_asym.empty:
            hits_asym = df_asym[df_asym["p_asym"] < SUG_THRESH].sort_values("p_asym")
            log(f"\n  Using suggestive threshold: {len(hits_asym):,} hits", fh)

        clumped_asym = clump(hits_asym, "p_asym")
        log(f"  Independent asymmetry loci: {len(clumped_asym)}", fh)

        if not clumped_asym.empty:
            show_a = ["rsid","chr","pos","beta_R","beta_L",
                      "beta_asym","se_asym","p_asym"]
            log(f"\n  Top asymmetry loci:", fh)
            log(clumped_asym[show_a].head(20).to_string(index=False), fh)

        hits_asym.to_csv(OUT_ASYM_HITS, sep="\t", index=False)
        log(f"\n  Saved -> {OUT_ASYM_HITS}", fh)

        # ── Candidate gene analysis ───────────────────────────────────
        log("\n── CANDIDATE GENE ANALYSIS: ALL FOUR LAYERS ─────────────", fh)
        gene_summary, cand_all = candidate_analysis(df_r, df_l, df_asym, fh)

        # OXTR rs53576 explicit lookup
        log("\n── OXTR rs53576 EXPLICIT CHECK (Layer C key SNP) ────────", fh)
        rs53576_r = df_r[df_r["rsid"] == OXTR_KEY_SNP]
        rs53576_l = df_l[df_l["rsid"] == OXTR_KEY_SNP]
        rs53576_a = df_asym[df_asym["rsid"] == OXTR_KEY_SNP]

        if not rs53576_r.empty:
            row = rs53576_r.iloc[0]
            log(f"  rs53576 in Right UF FA:", fh)
            log(f"    beta = {row['beta']:.5f}", fh)
            log(f"    se   = {row['se']:.5f}", fh)
            log(f"    p    = {row['p']:.3e}", fh)
            log(f"    chr  = {row['chr']}  pos = {row['pos']}", fh)
            log(f"    a1/a2 = {row['a1']} / {row['a2']}", fh)
        else:
            log(f"  rs53576: NOT FOUND in right UF FA dataset", fh)

        if not rs53576_l.empty:
            row = rs53576_l.iloc[0]
            log(f"  rs53576 in Left UF FA:", fh)
            log(f"    beta = {row['beta']:.5f}  p = {row['p']:.3e}", fh)
        else:
            log(f"  rs53576: NOT FOUND in left UF FA dataset", fh)

        if not rs53576_a.empty:
            row = rs53576_a.iloc[0]
            log(f"  rs53576 asymmetry index:", fh)
            log(f"    beta_asym = {row['beta_asym']:.5f}  "
                f"p_asym = {row['p_asym']:.3e}", fh)
            log(f"    Interpretation: beta_asym "
                f"{'> 0: rs53576 A allele INCREASES right > left UF' if row['beta_asym'] > 0 else '< 0: rs53576 A allele DECREASES right > left UF'}", fh)

        # Save candidates
        if not cand_all.empty:
            cand_all.sort_values("p", inplace=True)
            cand_all.to_csv(OUT_CANDIDATES, sep="\t", index=False)
            log(f"\n  All candidate SNPs saved -> {OUT_CANDIDATES} "
                f"({len(cand_all):,} rows)", fh)

        # ── MR instruments ────────────────────────────────────────────
        log("\n── MR INSTRUMENT FILE ────────────────────────────────────", fh)
        log("  Ready for Step 3 when antisocial GWAS is obtained.", fh)

        # Primary: clumped GWS right UF FA hits
        hits_r_all = df_r[df_r["p"] < GWS_THRESH].sort_values("p")
        if hits_r_all.empty:
            hits_r_all = df_r[df_r["p"] < SUG_THRESH].sort_values("p")
        clumped_r_all = clump(hits_r_all, "p")

        if len(clumped_r_all) >= 3:
            instruments = clumped_r_all.copy()
            instruments["exposure"] = "right_UF_FA"
            instruments["phenotype"] = "IDP_25100_Right_UF_FA"
        else:
            instruments = clumped_asym[
                ["rsid","chr","pos","a1","a2",
                 "beta_asym","se_asym","p_asym"]
            ].copy()
            instruments.rename(columns={
                "beta_asym":"beta","se_asym":"se","p_asym":"p"
            }, inplace=True)
            instruments["exposure"] = "asymmetry_index"
            instruments["phenotype"] = "right_minus_left_UF_FA"

        instruments.to_csv(OUT_INSTRUMENTS, sep="\t", index=False)
        log(f"  {len(instruments)} instrument SNPs saved -> {OUT_INSTRUMENTS}", fh)

        # ── Final interpretation ───────────────────────────────────────
        log("\n═"*70, fh)
        log("INTERPRETATION", fh)
        log("═"*70, fh)

        n_gws_r = (df_r["p"] < GWS_THRESH).sum()
        n_gws_a = (df_asym["p_asym"] < GWS_THRESH).sum()
        oxtr_p  = df_r[df_r["rsid"] == OXTR_KEY_SNP]["p"].values
        oxtr_p  = float(oxtr_p[0]) if len(oxtr_p) > 0 else float("nan")

        # Layer ranking from gene summary
        layer_best = gene_summary.groupby("layer")["best_p_right_UF"].min() \
                                 .sort_values()

        log(f"""
RIGHT UF FA
  GWS hits           : {n_gws_r:,}
  Independent loci   : {len(clumped_r_all)}

ASYMMETRY INDEX (right − left UF FA)
  GWS hits           : {n_gws_a:,}
  Independent loci   : {len(clumped_asym)}

OXTR rs53576 (Layer C key SNP)
  p in right UF FA   : {oxtr_p:.3e}
  {"BELOW 5e-8: Layer C signal confirmed at GWS level"
   if oxtr_p < 5e-8 else
   "BELOW 1e-4: suggestive Layer C signal"
   if oxtr_p < 1e-4 else
   "ABOVE 1e-4: Layer C not the dominant signal in this dataset"
   if not np.isnan(oxtr_p) else
   "rs53576 not found in dataset"}

BUILD PROGRAMME LAYER RANKING (by best p, right UF FA):
{chr(10).join(f"  Layer {lay}: best p = {p:.2e}" for lay, p in layer_best.items())}

WHAT THIS MEANS:
  The layer with the smallest p-value is where the genome
  most strongly influences right UF structural integrity
  in this population dataset.

  If Layer C (OXTR) ranks first or second:
    The derivation's primary prediction is confirmed —
    the oxytocin coupling consolidation pathway is
    genetically encoded as a major determinant of
    right UF structural quality.

  If Layer A (axon guidance) ranks first:
    The axon pathfinding step is the dominant source
    of genetic variance in right UF integrity —
    the build programme fails most often at the
    earliest step.

  If Layer D (lateralisation) ranks first:
    The human-specific right-sided elaboration is the
    most genetically variable component — consistent
    with the asymmetry index being the most sensitive
    biomarker target.

  No layer ranking is a falsification of the framework.
  All four layers are part of the build programme.
  The ranking tells us which failure mode is most
  common in the general population — not which is
  most important for the congenital psychopathy pathway.
""", fh)

        log(f"Report saved: {OUT_SUMMARY}", fh)
        log(f"Done: {time.strftime('%Y-%m-%d %H:%M:%S')}", fh)

    print(f"\n{'═'*60}")
    print(f"Complete.")
    print(f"  {OUT_SUMMARY}")
    print(f"  {OUT_RIGHT_HITS}")
    print(f"  {OUT_LEFT_HITS}")
    print(f"  {OUT_ASYM_HITS}")
    print(f"  {OUT_CANDIDATES}")
    print(f"  {OUT_INSTRUMENTS}")
    print(f"{'═'*60}")


if __name__ == "__main__":
    main()
