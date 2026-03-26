"""
DIAGNOSTIC — UF FA FILES STRUCTURE INSPECTION
==============================================
OC-PSYCHOPATHY-GENETIC-MARKER-DERIVATION-001
Eric Robert Lawson — OrganismCore — 2026-03-26

Opens 1496.txt (Right UF FA) and 1497.txt (Left UF FA)
and reports everything needed to write the calculation script.

Usage:
    python diagnose_uf_files.py

Files expected in same directory as this script:
    1496.txt   (or 1496.txt.gz)
    1497.txt   (or 1497.txt.gz)
"""

import gzip
import os
import sys
from pathlib import Path

import pandas as pd
import numpy as np

# ── File locations ─────────────────────────────────────────────────────────────
# Adjust these paths if your files are in a subfolder
FILES = {
    "Right_UF_FA (1496)": "1496.txt",
    "Left_UF_FA  (1497)": "1497.txt",
}

# Candidate gene windows (GRCh37/hg19) — build programme Layers A-D
# Will check which are present in the data
CANDIDATE_GENES = {
    "OXTR":   {"chr": "3",  "start": 8505088,   "end": 9021564,  "layer": "C"},
    "SEMA3A": {"chr": "7",  "start": 83294422,  "end": 83953344, "layer": "A"},
    "ROBO1":  {"chr": "3",  "start": 78421879,  "end": 79404206, "layer": "A"},
    "SLIT2":  {"chr": "4",  "start": 20260577,  "end": 21094926, "layer": "A"},
    "MBP":    {"chr": "18", "start": 74435940,  "end": 75064555, "layer": "B"},
    "MAG":    {"chr": "19", "start": 35171502,  "end": 35691199, "layer": "B"},
    "PLP1":   {"chr": "X",  "start": 102781428, "end": 103310355,"layer": "B"},
}


def open_file(path_str):
    """Open .txt or .txt.gz transparently."""
    p = Path(path_str)
    # Try exact path first, then with .gz suffix
    for candidate in [p, Path(path_str + ".gz")]:
        if candidate.exists():
            if str(candidate).endswith(".gz"):
                return gzip.open(candidate, "rt"), str(candidate)
            else:
                return open(candidate, "r"), str(candidate)
    return None, None


def peek_raw(path_str, n_lines=10):
    """Return first n lines of file as raw strings."""
    fh, found = open_file(path_str)
    if fh is None:
        return None, None
    lines = []
    with fh:
        for i, line in enumerate(fh):
            if i >= n_lines:
                break
            lines.append(line.rstrip("\n"))
    return lines, found


def count_lines(path_str):
    """Count total lines including header."""
    fh, _ = open_file(path_str)
    if fh is None:
        return 0
    count = 0
    with fh:
        for _ in fh:
            count += 1
    return count


def load_file(path_str, max_rows=None):
    """Load into DataFrame, trying common separators."""
    fh, found = open_file(path_str)
    if fh is None:
        return None, None
    fh.close()

    p = Path(found)
    for sep in ["\t", " ", ","]:
        try:
            df = pd.read_csv(
                p,
                sep=sep,
                compression="gzip" if str(p).endswith(".gz") else None,
                nrows=max_rows,
                low_memory=False,
                comment="#",
            )
            if len(df.columns) >= 3:
                return df, sep
        except Exception:
            continue
    return None, None


def detect_columns(df):
    """Map canonical names to actual column names."""
    cl = {c.lower().strip(): c for c in df.columns}

    def pick(*candidates):
        for c in candidates:
            if c in cl:
                return cl[c]
        return None

    return {
        "snp":   pick("snp", "rsid", "id", "variant", "rs", "name", "markername"),
        "chr":   pick("chr", "chrom", "chromosome", "#chr", "ch"),
        "pos":   pick("pos", "bp", "position", "bpos", "base_pair", "bp_hg19"),
        "a1":    pick("a1", "allele1", "effect_allele", "alt", "ea"),
        "a2":    pick("a2", "allele2", "other_allele", "ref", "nea"),
        "beta":  pick("beta", "b", "effect", "es", "log_odds", "or"),
        "se":    pick("se", "stderr", "standard_error", "se_gc"),
        "p":     pick("p", "pval", "p_value", "p-value", "pvalue", "gc_pvalue",
                      "p_bolt", "p_lrt"),
        "maf":   pick("maf", "af", "eaf", "frq", "freq", "a1freq"),
        "info":  pick("info", "impinfo", "imp_info", "r2"),
        "n":     pick("n", "nobs", "sample_size", "n_total", "ss"),
    }


def p_stats(df, col_map):
    """Return raw p-values as Series."""
    if "p" not in col_map:
        return None
    pv = pd.to_numeric(df[col_map["p"]], errors="coerce").dropna()
    # Detect -log10 scale
    if pv.max() > 50:
        return 10 ** (-pv.clip(upper=300))
    return pv


def separator_name(sep):
    return {"\\t": "TAB", "\t": "TAB", " ": "SPACE", ",": "COMMA"}.get(sep, repr(sep))


def run_diagnostic(label, path_str):
    print(f"\n{'═'*65}")
    print(f"  {label}")
    print(f"{'═'*65}")

    # ── 1. File existence and size ────────────────────────────────────
    _, found = open_file(path_str)
    if found is None:
        print(f"  [NOT FOUND] Tried: {path_str}  and  {path_str}.gz")
        print(f"  Make sure the file is in the same directory as this script,")
        print(f"  or edit the FILES dict at the top to give the full path.")
        return None

    size_mb = Path(found).stat().st_size / 1_048_576
    print(f"\n  File found : {found}")
    print(f"  File size  : {size_mb:.1f} MB")

    # ── 2. Raw first lines ────────────────────────────────────────────
    raw_lines, _ = peek_raw(path_str, n_lines=5)
    print(f"\n  First 5 raw lines:")
    for i, line in enumerate(raw_lines):
        print(f"    [{i}] {line[:120]}")

    # ── 3. Detect separator and load ─────────────────────────────────
    print(f"\n  Loading full file...")
    df, sep = load_file(path_str)
    if df is None:
        print(f"  [ERROR] Could not parse file. Check format.")
        return None

    print(f"  Separator  : {separator_name(sep)}")
    print(f"  Shape      : {df.shape[0]:,} rows  ×  {df.shape[1]} columns")

    # ── 4. Column names and dtypes ────────────────────────────────────
    print(f"\n  Column names and dtypes:")
    for col in df.columns:
        null_count = df[col].isna().sum()
        sample_val = df[col].dropna().iloc[0] if df[col].notna().any() else "N/A"
        print(f"    {col:30s}  {str(df[col].dtype):10s}  "
              f"nulls={null_count:,}   example={str(sample_val)[:30]}")

    # ── 5. Column mapping ─────────────────────────────────────────────
    col_map = detect_columns(df)
    print(f"\n  Detected column mapping (canonical -> actual):")
    for canon, actual in col_map.items():
        if actual:
            print(f"    {canon:8s} -> {actual}")
        else:
            print(f"    {canon:8s} -> [NOT FOUND]")

    # ── 6. First 3 data rows (mapped columns only) ────────────────────
    mapped_cols = [v for v in col_map.values() if v]
    if mapped_cols:
        print(f"\n  First 3 rows (mapped columns):")
        print(df[mapped_cols].head(3).to_string(index=False))

    # ── 7. SNP ID format ───────────────��──────────────────────────────
    if col_map["snp"]:
        snp_sample = df[col_map["snp"]].dropna().head(5).tolist()
        print(f"\n  SNP ID examples: {snp_sample}")
        first = str(snp_sample[0]) if snp_sample else ""
        if first.startswith("rs"):
            print(f"  SNP format: rsID  (harmonisation by rsID is possible)")
        elif ":" in first:
            print(f"  SNP format: CHR:POS style  (harmonisation by position)")
        else:
            print(f"  SNP format: UNKNOWN — inspect manually")

    # ── 8. Chromosome values ──────────────────────────────────────────
    if col_map["chr"]:
        chrom_vals = df[col_map["chr"]].astype(str).unique()
        chrom_vals_sorted = sorted(chrom_vals,
                                   key=lambda x: (len(x.replace("chr","")),
                                                   x.replace("chr","")))
        print(f"\n  Chromosomes present: {chrom_vals_sorted[:25]}")
        has_chr_prefix = any(str(v).startswith("chr") for v in chrom_vals)
        print(f"  Has 'chr' prefix: {has_chr_prefix}")

    # ── 9. Position range ─────────────────────────────────────────────
    if col_map["pos"]:
        bp = pd.to_numeric(df[col_map["pos"]], errors="coerce").dropna()
        print(f"\n  Position range: {bp.min():,.0f}  —  {bp.max():,.0f}")
        print(f"  Genome build guess: "
              f"{'GRCh37/hg19 (positions look right)' if bp.max() < 3e8 else 'check build'}")

    # ── 10. Effect size (BETA) ────────────────────────────────────────
    if col_map["beta"]:
        bv = pd.to_numeric(df[col_map["beta"]], errors="coerce").dropna()
        print(f"\n  Effect size ({col_map['beta']}):")
        print(f"    min={bv.min():.5f}  max={bv.max():.5f}  "
              f"mean={bv.mean():.5f}  std={bv.std():.5f}")
        print(f"    Symmetric around 0: "
              f"{'YES (BETA, linear)' if abs(bv.mean()) < 0.01 else 'CHECK — may be OR'}")

    # ── 11. SE ────────────────────────────────────────────────────────
    if col_map["se"]:
        sv = pd.to_numeric(df[col_map["se"]], errors="coerce").dropna()
        print(f"\n  Standard error ({col_map['se']}):")
        print(f"    min={sv.min():.6f}  max={sv.max():.6f}  median={sv.median():.6f}")

    # ── 12. P-value distribution ──────────────────────────────────────
    raw_p = p_stats(df, col_map)
    if raw_p is not None:
        gws  = (raw_p < 5e-8).sum()
        sug  = (raw_p < 1e-5).sum()
        nom  = (raw_p < 0.05).sum()
        print(f"\n  P-value distribution:")
        print(f"    Genome-wide significant  p < 5e-8  : {gws:>10,}")
        print(f"    Suggestive               p < 1e-5  : {sug:>10,}")
        print(f"    Nominally significant    p < 0.05  : {nom:>10,}")
        print(f"    Total variants                     : {len(raw_p):>10,}")

        if gws > 0:
            top = df.copy()
            top["_p"] = raw_p
            top_hits = top.nsmallest(10, "_p")
            show = [v for v in col_map.values() if v]
            print(f"\n  Top 10 associations:")
            print(top_hits[show].drop(columns=["_p"] if "_p" in show else [],
                                      errors="ignore").to_string(index=False))

    # ── 13. MAF / AF ──────────────────────────────────────────────────
    if col_map["maf"]:
        maf = pd.to_numeric(df[col_map["maf"]], errors="coerce").dropna()
        print(f"\n  Allele frequency ({col_map['maf']}):")
        print(f"    min={maf.min():.4f}  max={maf.max():.4f}  median={maf.median():.4f}")
        rare = (maf < 0.01).sum()
        print(f"    Rare variants (MAF<0.01): {rare:,}")

    # ── 14. INFO score ────────────────────────────────────────────────
    if col_map["info"]:
        info = pd.to_numeric(df[col_map["info"]], errors="coerce").dropna()
        print(f"\n  Imputation INFO ({col_map['info']}):")
        print(f"    min={info.min():.3f}  max={info.max():.3f}  "
              f"median={info.median():.3f}")
        well_imp = (info >= 0.8).sum()
        print(f"    Well-imputed (INFO>=0.8): {well_imp:,} "
              f"({well_imp/len(info)*100:.1f}%)")

    # ── 15. Candidate gene regions ────────────────────────────────────
    if col_map["chr"] and col_map["pos"]:
        print(f"\n  Candidate gene region check (Layers A-D build programme):")
        d = df.copy()
        d["_chr"] = d[col_map["chr"]].astype(str).str.replace("chr","",regex=False)
        d["_bp"]  = pd.to_numeric(d[col_map["pos"]], errors="coerce")

        for gene, info in CANDIDATE_GENES.items():
            mask = (
                (d["_chr"] == str(info["chr"])) &
                (d["_bp"]  >= info["start"]) &
                (d["_bp"]  <= info["end"])
            )
            n_snps = mask.sum()
            # Best p in region
            if raw_p is not None and n_snps > 0:
                region_p = raw_p[mask.values[:len(raw_p)]]
                best_p = region_p.min() if len(region_p) > 0 else float("nan")
                print(f"    {gene:8s} Layer {info['layer']}  "
                      f"{n_snps:>6,} SNPs   best p = {best_p:.2e}")
            else:
                print(f"    {gene:8s} Layer {info['layer']}  {n_snps:>6,} SNPs")

    print(f"\n  [DONE] {label}")
    return {"df": df, "col_map": col_map, "raw_p": raw_p}


def main():
    print("═"*65)
    print("  UF FA FILES — DIAGNOSTIC INSPECTION")
    print("  OC-PSYCHOPATHY-GENETIC-MARKER-DERIVATION-001")
    print("═"*65)

    results = {}
    for label, path in FILES.items():
        results[label] = run_diagnostic(label, path)

    # ── Cross-file check: SNP overlap for asymmetry index ─────────────
    print(f"\n{'═'*65}")
    print("  CROSS-FILE CHECK: Asymmetry index feasibility")
    print(f"{'═'*65}")

    r_key = "Right_UF_FA (1496)"
    l_key = "Left_UF_FA  (1497)"

    if results.get(r_key) and results.get(l_key):
        r = results[r_key]
        l = results[l_key]
        cm_r = r["col_map"]; cm_l = l["col_map"]

        if cm_r["snp"] and cm_l["snp"]:
            ids_r = set(r["df"][cm_r["snp"]].dropna().astype(str))
            ids_l = set(l["df"][cm_l["snp"]].dropna().astype(str))
            overlap = ids_r & ids_l
            print(f"\n  Right UF FA variants : {len(ids_r):,}")
            print(f"  Left  UF FA variants : {len(ids_l):,}")
            print(f"  Shared SNP IDs       : {len(overlap):,}")
            if len(overlap) > 10000:
                print(f"  [OK] Asymmetry index (beta_R - beta_L) is computable.")
                print(f"       This is the novel Layer 6 exposure.")
            else:
                print(f"  [WARN] Low overlap — may need CHR:POS merge instead of SNP ID.")

        if cm_r["chr"] and cm_r["pos"] and cm_l["chr"] and cm_l["pos"]:
            # Build CHR:POS keys for both
            def chrpos(df, cm):
                ch = df[cm["chr"]].astype(str).str.replace("chr","",regex=False)
                bp = df[cm["pos"]].astype(str)
                return set(ch + ":" + bp)
            cp_r = chrpos(r["df"], cm_r)
            cp_l = chrpos(l["df"], cm_l)
            cp_ov = cp_r & cp_l
            print(f"\n  CHR:POS overlap      : {len(cp_ov):,}")
            if len(cp_ov) > 10000:
                print(f"  [OK] CHR:POS merge is viable as backup harmonisation.")

    # ── Summary for Step 2 ────────────────────────────────────────────
    print(f"\n{'═'*65}")
    print("  WHAT STEP 2 NEEDS FROM THIS REPORT")
    print(f"{'═'*65}")
    print("""
  Read the output above and note:

  1. COLUMN NAMES (exact spelling, case-sensitive)
     -> The calculation script will use these directly

  2. SNP ID FORMAT (rsID / CHR:POS / other)
     -> Determines how right and left files are merged

  3. GENOME-WIDE SIGNIFICANT SNP COUNT (p < 5e-8)
     -> If > 10: strong instrument set for analysis
     -> If < 10: use p < 1e-6 threshold

  4. CANDIDATE GENE REGION HITS
     -> Which of OXTR / SEMA3A / ROBO1 / SLIT2 / MBP / MAG / PLP1
        have SNPs present and what are their best p-values?
     -> OXTR is the primary target — its p-value here is key

  5. ASYMMETRY INDEX FEASIBILITY
     -> SNP overlap count between the two files

  Step 2 will:
    A. Merge right and left UF FA on shared SNPs
    B. Compute asymmetry index: beta_asym = beta_R - beta_L
    C. Identify top SNPs for right UF FA and asymmetry index
    D. Extract and report full candidate gene windows (Layers A-D)
    E. Produce a ranked table: which layer shows strongest signal?
    F. Statistical summary of OXTR region specifically
""")
    print("═"*65)


if __name__ == "__main__":
    # Install check
    try:
        import pandas, numpy
    except ImportError:
        print("Run:  pip install pandas numpy")
        sys.exit(1)

    main()
