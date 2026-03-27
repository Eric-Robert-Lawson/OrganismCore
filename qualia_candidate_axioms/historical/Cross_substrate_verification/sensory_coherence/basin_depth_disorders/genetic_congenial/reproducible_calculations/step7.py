"""
STEP 7B — GENE ANNOTATION FIX
==============================
Diagnoses why refGene returned NO_REFGENE for 11 loci
and runs corrected annotation.

Run this first. It will print exactly what chromosome
strings are in refGene and fix the matching.
"""

import gzip
import time
import warnings
from pathlib import Path
from collections import Counter

import pandas as pd
import numpy as np

warnings.filterwarnings("ignore")

FILE_REFGENE  = "refGene.txt"
OUT_REPORT    = Path("step7b_results.txt")
OUT_FINAL     = Path("psychopathy_markers_annotated_v2.tsv")
UF_FA_SD      = 0.040

# All loci with correct hg19 positions
LOCI = [
    {"rsid": "rs78404854",        "chr": "7",  "pos": 83_662_138,  "beta": 0.07107, "p": 4.07e-9,  "layer": "A", "step6": "SEMA3A",    "confirmed": True},
    {"rsid": "rs4383974",         "chr": "8",  "pos": 9_619_348,   "beta": 0.05940, "p": 8.24e-12, "layer": "E", "step6": "CSMD1",     "confirmed": True},
    {"rsid": "17:44297459_G_A",   "chr": "17", "pos": 44_297_459,  "beta": 0.06240, "p": 3.66e-8,  "layer": "B", "step6": "MAPT",      "confirmed": True},
    {"rsid": "rs2713546",         "chr": "2",  "pos": 227_177_546, "beta": 0.06227, "p": 6.82e-15, "layer": "B", "step6": "COL4A3BP",  "confirmed": False},
    {"rsid": "rs7733216",         "chr": "5",  "pos": 82_857_870,  "beta": 0.06411, "p": 1.34e-10, "layer": "A", "step6": "DPYSL3",    "confirmed": False},
    {"rsid": "rs12911569",        "chr": "15", "pos": 43_597_297,  "beta": 0.06025, "p": 2.84e-9,  "layer": "B", "step6": "SLC12A6",   "confirmed": False},
    {"rsid": "rs17719345",        "chr": "16", "pos": 89_911_681,  "beta": 0.05630, "p": 1.79e-8,  "layer": "B", "step6": "CBFA2T3",   "confirmed": False},
    {"rsid": "12:69676379_TTA_T", "chr": "12", "pos": 69_676_379,  "beta": 0.05135, "p": 2.34e-9,  "layer": "B?","step6": "UNKNOWN",   "confirmed": False},
    {"rsid": "rs2189574",         "chr": "4",  "pos": 97_943_856,  "beta": 0.06957, "p": 5.70e-16, "layer": "D", "step6": "UNKNOWN",   "confirmed": False},
    {"rsid": "rs263071",          "chr": "4",  "pos": 96_906_564,  "beta": 0.07155, "p": 4.78e-13, "layer": "D", "step6": "UNKNOWN",   "confirmed": False},
    {"rsid": "rs12550039",        "chr": "8",  "pos": 123_850_020, "beta": 0.04853, "p": 6.64e-9,  "layer": "?", "step6": "UNKNOWN",   "confirmed": False},
    {"rsid": "rs3076538",         "chr": "7",  "pos": 101_762_573, "beta": 0.05278, "p": 6.89e-11, "layer": "A", "step6": "UNKNOWN",   "confirmed": False},
    {"rsid": "rs3088186",         "chr": "8",  "pos": 10_226_355,  "beta": 0.05759, "p": 1.97e-11, "layer": "E", "step6": "CSMD1",     "confirmed": False},
    {"rsid": "rs2979255",         "chr": "8",  "pos": 8_919_309,   "beta": 0.04875, "p": 2.70e-9,  "layer": "E", "step6": "CSMD1",     "confirmed": False},
]

BROADABC_DIR = {
    "rs78404854":          "concordant",
    "rs4383974":           "concordant",
    "rs2713546":           "concordant",
    "rs7733216":           "concordant",
    "rs12911569":          "concordant",
    "rs17719345":          "concordant",
    "rs2189574":           "concordant",
    "rs263071":            "concordant",
    "rs12550039":          "concordant",
    "rs3088186":           "noise_p=0.39",
    "rs2979255":           "not_in_broadabc",
    "rs3076538":           "not_in_broadabc",
    "12:69676379_TTA_T":   "not_in_broadabc",
    "17:44297459_G_A":     "not_in_broadabc",
}

GENE_FUNCTION = {
    "SEMA3A":   ("A", "Semaphorin-3A — extracellular axon guidance ligand. Directs UF projection axons to prefrontal target via growth cone repulsion."),
    "CSMD1":    ("E", "CUB and Sushi multiple domains 1 — complement-mediated synaptic pruning precision during UF consolidation."),
    "MAPT":     ("B", "Microtubule-associated protein tau — organises axonal microtubules, determines axon diameter and myelination efficiency."),
    "COL4A3BP": ("B", "CERT ceramide transfer protein — transfers ceramide from ER to Golgi for myelin sphingomyelin biosynthesis."),
    "DPYSL3":   ("A", "CRMP4/Dihydropyrimidinase-like 3 — intracellular transducer of SEMA3A axon guidance signals in growth cones."),
    "SLC12A6":  ("B", "KCC3 K-Cl cotransporter — maintains axon volume during tract development. Loss of function causes Andermann syndrome (white matter agenesis)."),
    "CBFA2T3":  ("B", "MTG16/ETO2 transcriptional repressor — regulates timing of oligodendrocyte differentiation during myelination window."),
    "LRRTM4":   ("D", "Leucine-rich repeat transmembrane neuronal protein 4 — synaptic organisation, lateralisation candidate."),
    "FAT1":     ("D", "FAT atypical cadherin 1 — cell polarity, axon guidance. FAT1 mutations affect neural tube closure and brain asymmetry."),
    "PCDH11X":  ("D", "Protocadherin-11X — X-linked cell adhesion, lateralisation. Hemizygous in males."),
    "LRRTM1":   ("D", "Leucine-rich repeat transmembrane neuronal 1 — handedness and brain asymmetry GWAS hit."),
    "CSMD2":    ("E", "CUB and Sushi multiple domains 2 — complement pruning, same family as CSMD1."),
    "CSMD3":    ("E", "CUB and Sushi multiple domains 3 — complement pruning, same family as CSMD1."),
    "MBP":      ("B", "Myelin basic protein — primary structural component of myelin sheath."),
    "ARHGEF10": ("B", "Rho guanine nucleotide exchange factor 10 — axon myelination. ARHGEF10 mutations cause Charcot-Marie-Tooth neuropathy."),
}


def log(msg, fh=None):
    print(msg)
    if fh:
        fh.write(msg + "\n")
        fh.flush()


def load_refgene_raw(fh):
    """
    Load refGene preserving the EXACT chromosome string.
    Do NOT normalise. Show what is actually in the file.
    """
    p = Path(FILE_REFGENE)
    if not p.exists():
        log(f"  {FILE_REFGENE} not found.", fh)
        log(f"  wget https://hgdownload.soe.ucsc.edu/goldenPath/hg19/database/refGene.txt.gz", fh)
        return None

    log(f"  Loading {FILE_REFGENE}...", fh)
    t0   = time.time()
    rows = []

    opener = gzip.open if str(p).endswith(".gz") else open
    with opener(p, "rt") as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) < 13:
                continue
            try:
                tx_start = int(parts[4])
                tx_end   = int(parts[5])
            except ValueError:
                continue
            rows.append({
                "chrom_raw":  parts[2],          # EXACT string from file
                "tx_start":   tx_start,
                "tx_end":     tx_end,
                "gene":       parts[12].strip(),
                "transcript": parts[1].strip(),
                "strand":     parts[3].strip(),
            })

    df = pd.DataFrame(rows)
    log(f"  Loaded {len(df):,} transcript records [{time.time()-t0:.1f}s]", fh)

    # Show exactly what chromosome strings exist in the file
    chrom_counts = Counter(df["chrom_raw"])
    log(f"\n  Chromosome strings in refGene (sample):", fh)
    for chrom, count in sorted(chrom_counts.items())[:30]:
        log(f"    '{chrom}': {count} transcripts", fh)

    return df


def build_chrom_lookup(df_raw, fh):
    """
    Build a lookup dictionary: normalised_chr -> exact_refgene_string
    so we can match our locus chromosomes to the file's strings.
    """
    log(f"\n  Building chromosome lookup...", fh)

    chrom_map = {}
    for chrom_raw in df_raw["chrom_raw"].unique():
        # Normalise: strip 'chr', strip leading zeros
        norm = (chrom_raw.lower()
                .replace("chr", "")
                .lstrip("0") or "0")
        # Keep only standard chromosomes
        if norm in [str(i) for i in range(1, 23)] + ["x", "y", "m", "mt"]:
            chrom_map[norm] = chrom_raw

    log(f"  Standard chromosomes mapped: {len(chrom_map)}", fh)
    for norm, raw in sorted(chrom_map.items(),
                             key=lambda x: int(x[0])
                             if x[0].isdigit() else 99):
        log(f"    {norm:>4s} -> '{raw}'", fh)

    return chrom_map


def lookup(df_raw, chrom_raw_str, pos, window=500_000):
    """
    Look up genes at a position using the exact chromosome string.
    Returns overlapping genes and nearby genes sorted by distance.
    """
    sub = df_raw[df_raw["chrom_raw"] == chrom_raw_str].copy()
    if sub.empty:
        return pd.DataFrame(), pd.DataFrame()

    sub["tx_length"] = sub["tx_end"] - sub["tx_start"]
    sub = (sub.sort_values("tx_length", ascending=False)
              .drop_duplicates(subset=["gene"]))

    def dist(row):
        if row["tx_start"] <= pos <= row["tx_end"]:
            return 0
        return min(abs(pos - row["tx_start"]),
                   abs(pos - row["tx_end"]))

    sub["distance"] = sub.apply(dist, axis=1)

    overlapping = sub[sub["distance"] == 0].copy()
    nearby = (sub[sub["distance"] <= window]
              .sort_values("distance"))
    return overlapping, nearby


def annotate_loci(df_raw, chrom_map, fh):
    """
    Annotate all loci using correct chromosome matching.
    """
    log("\n── LOCUS ANNOTATION ──────────────────────────────────────", fh)

    results = []

    for locus in LOCI:
        rsid      = locus["rsid"]
        chrom     = locus["chr"]
        pos       = locus["pos"]
        beta      = locus["beta"]
        gwas_p    = locus["p"]
        layer     = locus["layer"]
        step6     = locus["step6"]
        confirmed = locus["confirmed"]

        log(f"\n  ── {rsid} ──", fh)
        log(f"  chr{chrom}:{pos:,}  "
            f"beta={beta:+.5f}  p={gwas_p:.2e}  "
            f"Layer={layer}  Step6={step6}", fh)

        if confirmed:
            func = GENE_FUNCTION.get(step6, ("?", "See literature"))[1]
            log(f"  CONFIRMED (SNP in gene body): {step6}", fh)
            log(f"  Function: {func}", fh)
            results.append({
                "rsid": rsid, "chr": chrom, "pos": pos,
                "beta_FA": beta, "gwas_p": gwas_p,
                "layer": layer, "gene": step6,
                "distance_bp": 0, "overlapping": True,
                "gene_function": func,
                "confidence": "CONFIRMED",
                "validation": "SNP_IN_GENE_BODY",
            })
            continue

        # Get the exact chromosome string for this locus
        norm_chrom = chrom.lower().lstrip("0") or "0"
        chrom_str  = chrom_map.get(norm_chrom)

        if chrom_str is None:
            log(f"  chr{chrom} not found in chrom_map. "
                f"Available: {list(chrom_map.keys())}", fh)
            results.append({
                "rsid": rsid, "chr": chrom, "pos": pos,
                "beta_FA": beta, "gwas_p": gwas_p,
                "layer": layer, "gene": "CHR_NOT_FOUND",
                "distance_bp": -1, "overlapping": False,
                "gene_function": f"chr{chrom} not in refGene",
                "confidence": "FAILED",
                "validation": "CHR_MISMATCH",
            })
            continue

        overlapping, nearby = lookup(df_raw, chrom_str, pos)

        if not overlapping.empty:
            # SNP is inside one or more gene bodies
            genes_inside = overlapping["gene"].tolist()
            log(f"  SNP is INSIDE gene body: {genes_inside}", fh)

            # Pick best gene — prefer one with known function
            best_gene = None
            for g in genes_inside:
                if g in GENE_FUNCTION:
                    best_gene = g
                    break
            if best_gene is None:
                best_gene = genes_inside[0]

            func_layer, func_desc = GENE_FUNCTION.get(
                best_gene, (layer, "Function requires literature review"))
            if isinstance(func_layer, tuple):
                func_layer, func_desc = func_layer

            log(f"  Best gene: {best_gene}", fh)
            log(f"  Function: {func_desc}", fh)

            # Validate Step 6 assignment
            if step6 != "UNKNOWN":
                match = step6.upper() in best_gene.upper()
                log(f"  Step 6 validation: "
                    f"{'✓ CONFIRMED' if match else f'✗ CONFLICT — Step6={step6}, refGene={best_gene}'}", fh)

            results.append({
                "rsid": rsid, "chr": chrom, "pos": pos,
                "beta_FA": beta, "gwas_p": gwas_p,
                "layer": func_layer if func_layer != "?" else layer,
                "gene": best_gene,
                "distance_bp": 0, "overlapping": True,
                "gene_function": func_desc,
                "confidence": "CONFIRMED",
                "validation": "REFGENE_OVERLAP",
            })

        elif not nearby.empty:
            # Intergenic — use nearest gene
            log(f"  SNP is intergenic.", fh)
            log(f"\n  Nearest genes (within 500kb):", fh)
            log(f"  {'Gene':25s} {'Distance':>10s}  "
                f"{'Start':>12s}  {'End':>12s}  Strand", fh)
            log(f"  {'─'*75}", fh)

            for _, row in nearby.head(15).iterrows():
                fl, fd = GENE_FUNCTION.get(
                    row["gene"],
                    (layer, "")
                )
                if isinstance(fl, tuple):
                    fl, fd = fl
                marker = " ◄" if row["distance"] == nearby.iloc[0]["distance"] else ""
                log(f"  {row['gene']:25s} {int(row['distance']):>10,}  "
                    f"{int(row['tx_start']):>12,}  "
                    f"{int(row['tx_end']):>12,}  "
                    f"{row['strand']:>6s}  "
                    f"{fd[:40]}{marker}", fh)

            nearest   = nearby.iloc[0]
            best_gene = nearest["gene"]
            dist_bp   = int(nearest["distance"])
            fl, fd    = GENE_FUNCTION.get(
                best_gene, (layer, "Function requires literature review"))
            if isinstance(fl, tuple):
                fl, fd = fl

            log(f"\n  NEAREST GENE: {best_gene} ({dist_bp:,} bp)", fh)
            if step6 != "UNKNOWN":
                # Check if step6 gene appears anywhere in nearby
                step6_found = nearby[
                    nearby["gene"].str.upper().str.contains(
                        step6.upper(), regex=False)
                ]
                if not step6_found.empty:
                    d6 = int(step6_found.iloc[0]["distance"])
                    log(f"  Step 6 gene {step6} found at {d6:,} bp from lead SNP", fh)
                    log(f"  ✓ Step 6 assignment PRESENT in window", fh)
                    # Use step6 gene even if not nearest
                    best_gene = step6
                    dist_bp   = d6
                    fl2, fd2  = GENE_FUNCTION.get(
                        best_gene,
                        (layer, "Function requires literature review"))
                    if isinstance(fl2, tuple):
                        fl, fd = fl2
                    else:
                        fl, fd = fl2, fd2
                else:
                    log(f"  Step 6 gene {step6} NOT found in 500kb window", fh)
                    log(f"  Using nearest gene: {best_gene}", fh)

            results.append({
                "rsid": rsid, "chr": chrom, "pos": pos,
                "beta_FA": beta, "gwas_p": gwas_p,
                "layer": fl if fl != "?" else layer,
                "gene": best_gene,
                "distance_bp": dist_bp,
                "overlapping": False,
                "gene_function": fd,
                "confidence": "NEAREST_GENE",
                "validation": "REFGENE_NEAREST",
            })

        else:
            log(f"  No genes found within 500kb. "
                f"Unusual — check position.", fh)
            results.append({
                "rsid": rsid, "chr": chrom, "pos": pos,
                "beta_FA": beta, "gwas_p": gwas_p,
                "layer": layer, "gene": "INTERGENIC_500KB",
                "distance_bp": -1, "overlapping": False,
                "gene_function": "No gene within 500kb",
                "confidence": "INTERGENIC",
                "validation": "NO_GENE_FOUND",
            })

    return pd.DataFrame(results)


def print_final_table(df, fh):
    """Print and save the final annotated marker table."""
    log("\n── FINAL MARKER TABLE ────────────────────────────────────", fh)
    log("\n  PSYCHOPATHY GENETIC MARKER SET — FINAL ANNOTATED", fh)
    log("  Right UF FA Build Programme Failure Markers", fh)
    log("  OC-PSYCHOPATHY-GENETIC-MARKER-DERIVATION-001", fh)
    log(f"  {'═'*110}", fh)

    df = df.copy()
    df["broadabc"] = df["rsid"].map(BROADABC_DIR).fillna("unknown")
    df["beta_SD"]  = df["beta_FA"] / UF_FA_SD

    # Layer sort order
    order = {"A": 0, "B": 1, "B?": 2, "C": 3, "D": 4, "E": 5, "?": 6}
    df["_sort"] = df["layer"].map(order).fillna(7)
    df = df.sort_values(["_sort", "gwas_p"])

    log(f"\n  {'#':>3}  {'rsid':25}  {'chr':>4}  {'pos':>12}  "
        f"{'Gene':20}  {'Layer':>5}  "
        f"{'beta_FA':>9}  {'SDs':>5}  "
        f"{'p':>12}  BroadABC", fh)
    log(f"  {'─'*115}", fh)

    for i, (_, r) in enumerate(df.iterrows()):
        log(f"  {i+1:>3}  "
            f"{r['rsid']:25}  "
            f"{str(r['chr']):>4}  "
            f"{int(r['pos']):>12,}  "
            f"{str(r['gene'])[:20]:20}  "
            f"{str(r['layer']):>5}  "
            f"{r['beta_FA']:>+9.5f}  "
            f"{r['beta_SD']:>5.3f}  "
            f"{r['gwas_p']:>12.2e}  "
            f"{r['broadabc']}", fh)

    log(f"\n  Total: {len(df)} active markers", fh)

    log(f"\n  Layer summary:", fh)
    for layer_id in ["A", "B", "B?", "D", "E", "?"]:
        sub = df[df["layer"] == layer_id]
        if sub.empty:
            continue
        genes = ", ".join(g for g in sub["gene"].unique()
                          if g not in ("UNKNOWN","NO_GENE_FOUND",
                                       "INTERGENIC_500KB"))
        log(f"  Layer {layer_id:3}:  {len(sub):2} markers  {genes}", fh)

    log(f"\n  Gene annotations:", fh)
    log(f"  {'Gene':20}  {'Layer':>5}  Function", fh)
    log(f"  {'─'*90}", fh)
    seen = set()
    for _, r in df.iterrows():
        g = r["gene"]
        if g in seen or g in ("UNKNOWN","NO_GENE_FOUND","INTERGENIC_500KB",
                               "CHR_NOT_FOUND","FAILED"):
            continue
        seen.add(g)
        func = str(r["gene_function"])[:70]
        log(f"  {g[:20]:20}  {str(r['layer']):>5}  {func}", fh)

    df.to_csv(OUT_FINAL, sep="\t", index=False)
    log(f"\n  Saved -> {OUT_FINAL}", fh)
    return df


def main():
    with open(OUT_REPORT, "w") as fh:

        log("═"*70, fh)
        log("STEP 7B — GENE ANNOTATION FIX", fh)
        log("OC-PSYCHOPATHY-GENETIC-MARKER-DERIVATION-001", fh)
        log(f"Run: {time.strftime('%Y-%m-%d %H:%M:%S')}", fh)
        log("═"*70, fh)

        log("\n── LOADING REFGENE ───────────────────────────────────────", fh)
        df_raw = load_refgene_raw(fh)

        if df_raw is None:
            log("  Cannot proceed without refGene.txt.gz", fh)
            return

        chrom_map = build_chrom_lookup(df_raw, fh)
        df_ann    = annotate_loci(df_raw, chrom_map, fh)

        if not df_ann.empty:
            df_ann.to_csv("refgene_annotation_v2.tsv", sep="\t", index=False)
            print_final_table(df_ann, fh)

        log(f"\nDone: {time.strftime('%Y-%m-%d %H:%M:%S')}", fh)

    print(f"\nStep 7B complete. Report: {OUT_REPORT}")
    print(f"Final markers: {OUT_FINAL}")


if __name__ == "__main__":
    main()    {"rsid": "rs2189574",         "chr": "4",  "pos": 97_943_856,  "beta": 0.06957, "p": 5.70e-16, "layer": "D", "step6": "UNKNOWN",   "confirmed": False},
    {"rsid": "rs263071",          "chr": "4",  "pos": 96_906_564,  "beta": 0.07155, "p": 4.78e-13, "layer": "D", "step6": "UNKNOWN",   "confirmed": False},
    {"rsid": "rs12550039",        "chr": "8",  "pos": 123_850_020, "beta": 0.04853, "p": 6.64e-9,  "layer": "?", "step6": "UNKNOWN",   "confirmed": False},
    {"rsid": "rs3076538",         "chr": "7",  "pos": 101_762_573, "beta": 0.05278, "p": 6.89e-11, "layer": "A", "step6": "UNKNOWN",   "confirmed": False},
    {"rsid": "rs3088186",         "chr": "8",  "pos": 10_226_355,  "beta": 0.05759, "p": 1.97e-11, "layer": "E", "step6": "CSMD1",     "confirmed": False},
    {"rsid": "rs2979255",         "chr": "8",  "pos": 8_919_309,   "beta": 0.04875, "p": 2.70e-9,  "layer": "E", "step6": "CSMD1",     "confirmed": False},
]

BROADABC_DIR = {
    "rs78404854":          "concordant",
    "rs4383974":           "concordant",
    "rs2713546":           "concordant",
    "rs7733216":           "concordant",
    "rs12911569":          "concordant",
    "rs17719345":          "concordant",
    "rs2189574":           "concordant",
    "rs263071":            "concordant",
    "rs12550039":          "concordant",
    "rs3088186":           "noise_p=0.39",
    "rs2979255":           "not_in_broadabc",
    "rs3076538":           "not_in_broadabc",
    "12:69676379_TTA_T":   "not_in_broadabc",
    "17:44297459_G_A":     "not_in_broadabc",
}

GENE_FUNCTION = {
    "SEMA3A":   ("A", "Semaphorin-3A — extracellular axon guidance ligand. Directs UF projection axons to prefrontal target via growth cone repulsion."),
    "CSMD1":    ("E", "CUB and Sushi multiple domains 1 — complement-mediated synaptic pruning precision during UF consolidation."),
    "MAPT":     ("B", "Microtubule-associated protein tau — organises axonal microtubules, determines axon diameter and myelination efficiency."),
    "COL4A3BP": ("B", "CERT ceramide transfer protein — transfers ceramide from ER to Golgi for myelin sphingomyelin biosynthesis."),
    "DPYSL3":   ("A", "CRMP4/Dihydropyrimidinase-like 3 — intracellular transducer of SEMA3A axon guidance signals in growth cones."),
    "SLC12A6":  ("B", "KCC3 K-Cl cotransporter — maintains axon volume during tract development. Loss of function causes Andermann syndrome (white matter agenesis)."),
    "CBFA2T3":  ("B", "MTG16/ETO2 transcriptional repressor — regulates timing of oligodendrocyte differentiation during myelination window."),
    "LRRTM4":   ("D", "Leucine-rich repeat transmembrane neuronal protein 4 — synaptic organisation, lateralisation candidate."),
    "FAT1":     ("D", "FAT atypical cadherin 1 — cell polarity, axon guidance. FAT1 mutations affect neural tube closure and brain asymmetry."),
    "PCDH11X":  ("D", "Protocadherin-11X — X-linked cell adhesion, lateralisation. Hemizygous in males."),
    "LRRTM1":   ("D", "Leucine-rich repeat transmembrane neuronal 1 — handedness and brain asymmetry GWAS hit."),
    "CSMD2":    ("E", "CUB and Sushi multiple domains 2 — complement pruning, same family as CSMD1."),
    "CSMD3":    ("E", "CUB and Sushi multiple domains 3 — complement pruning, same family as CSMD1."),
    "MBP":      ("B", "Myelin basic protein — primary structural component of myelin sheath."),
    "ARHGEF10": ("B", "Rho guanine nucleotide exchange factor 10 — axon myelination. ARHGEF10 mutations cause Charcot-Marie-Tooth neuropathy."),
}


def log(msg, fh=None):
    print(msg)
    if fh:
        fh.write(msg + "\n")
        fh.flush()


def load_refgene_raw(fh):
    """
    Load refGene preserving the EXACT chromosome string.
    Do NOT normalise. Show what is actually in the file.
    """
    p = Path(FILE_REFGENE)
    if not p.exists():
        log(f"  {FILE_REFGENE} not found.", fh)
        log(f"  wget https://hgdownload.soe.ucsc.edu/goldenPath/hg19/database/refGene.txt.gz", fh)
        return None

    log(f"  Loading {FILE_REFGENE}...", fh)
    t0   = time.time()
    rows = []

    opener = gzip.open if str(p).endswith(".gz") else open
    with opener(p, "rt") as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) < 13:
                continue
            try:
                tx_start = int(parts[4])
                tx_end   = int(parts[5])
            except ValueError:
                continue
            rows.append({
                "chrom_raw":  parts[2],          # EXACT string from file
                "tx_start":   tx_start,
                "tx_end":     tx_end,
                "gene":       parts[12].strip(),
                "transcript": parts[1].strip(),
                "strand":     parts[3].strip(),
            })

    df = pd.DataFrame(rows)
    log(f"  Loaded {len(df):,} transcript records [{time.time()-t0:.1f}s]", fh)

    # Show exactly what chromosome strings exist in the file
    chrom_counts = Counter(df["chrom_raw"])
    log(f"\n  Chromosome strings in refGene (sample):", fh)
    for chrom, count in sorted(chrom_counts.items())[:30]:
        log(f"    '{chrom}': {count} transcripts", fh)

    return df


def build_chrom_lookup(df_raw, fh):
    """
    Build a lookup dictionary: normalised_chr -> exact_refgene_string
    so we can match our locus chromosomes to the file's strings.
    """
    log(f"\n  Building chromosome lookup...", fh)

    chrom_map = {}
    for chrom_raw in df_raw["chrom_raw"].unique():
        # Normalise: strip 'chr', strip leading zeros
        norm = (chrom_raw.lower()
                .replace("chr", "")
                .lstrip("0") or "0")
        # Keep only standard chromosomes
        if norm in [str(i) for i in range(1, 23)] + ["x", "y", "m", "mt"]:
            chrom_map[norm] = chrom_raw

    log(f"  Standard chromosomes mapped: {len(chrom_map)}", fh)
    for norm, raw in sorted(chrom_map.items(),
                             key=lambda x: int(x[0])
                             if x[0].isdigit() else 99):
        log(f"    {norm:>4s} -> '{raw}'", fh)

    return chrom_map


def lookup(df_raw, chrom_raw_str, pos, window=500_000):
    """
    Look up genes at a position using the exact chromosome string.
    Returns overlapping genes and nearby genes sorted by distance.
    """
    sub = df_raw[df_raw["chrom_raw"] == chrom_raw_str].copy()
    if sub.empty:
        return pd.DataFrame(), pd.DataFrame()

    sub["tx_length"] = sub["tx_end"] - sub["tx_start"]
    sub = (sub.sort_values("tx_length", ascending=False)
              .drop_duplicates(subset=["gene"]))

    def dist(row):
        if row["tx_start"] <= pos <= row["tx_end"]:
            return 0
        return min(abs(pos - row["tx_start"]),
                   abs(pos - row["tx_end"]))

    sub["distance"] = sub.apply(dist, axis=1)

    overlapping = sub[sub["distance"] == 0].copy()
    nearby = (sub[sub["distance"] <= window]
              .sort_values("distance"))
    return overlapping, nearby


def annotate_loci(df_raw, chrom_map, fh):
    """
    Annotate all loci using correct chromosome matching.
    """
    log("\n── LOCUS ANNOTATION ──────────────────────────────────────", fh)

    results = []

    for locus in LOCI:
        rsid      = locus["rsid"]
        chrom     = locus["chr"]
        pos       = locus["pos"]
        beta      = locus["beta"]
        gwas_p    = locus["p"]
        layer     = locus["layer"]
        step6     = locus["step6"]
        confirmed = locus["confirmed"]

        log(f"\n  ── {rsid} ──", fh)
        log(f"  chr{chrom}:{pos:,}  "
            f"beta={beta:+.5f}  p={gwas_p:.2e}  "
            f"Layer={layer}  Step6={step6}", fh)

        if confirmed:
            func = GENE_FUNCTION.get(step6, ("?", "See literature"))[1]
            log(f"  CONFIRMED (SNP in gene body): {step6}", fh)
            log(f"  Function: {func}", fh)
            results.append({
                "rsid": rsid, "chr": chrom, "pos": pos,
                "beta_FA": beta, "gwas_p": gwas_p,
                "layer": layer, "gene": step6,
                "distance_bp": 0, "overlapping": True,
                "gene_function": func,
                "confidence": "CONFIRMED",
                "validation": "SNP_IN_GENE_BODY",
            })
            continue

        # Get the exact chromosome string for this locus
        norm_chrom = chrom.lower().lstrip("0") or "0"
        chrom_str  = chrom_map.get(norm_chrom)

        if chrom_str is None:
            log(f"  chr{chrom} not found in chrom_map. "
                f"Available: {list(chrom_map.keys())}", fh)
            results.append({
                "rsid": rsid, "chr": chrom, "pos": pos,
                "beta_FA": beta, "gwas_p": gwas_p,
                "layer": layer, "gene": "CHR_NOT_FOUND",
                "distance_bp": -1, "overlapping": False,
                "gene_function": f"chr{chrom} not in refGene",
                "confidence": "FAILED",
                "validation": "CHR_MISMATCH",
            })
            continue

        overlapping, nearby = lookup(df_raw, chrom_str, pos)

        if not overlapping.empty:
            # SNP is inside one or more gene bodies
            genes_inside = overlapping["gene"].tolist()
            log(f"  SNP is INSIDE gene body: {genes_inside}", fh)

            # Pick best gene — prefer one with known function
            best_gene = None
            for g in genes_inside:
                if g in GENE_FUNCTION:
                    best_gene = g
                    break
            if best_gene is None:
                best_gene = genes_inside[0]

            func_layer, func_desc = GENE_FUNCTION.get(
                best_gene, (layer, "Function requires literature review"))
            if isinstance(func_layer, tuple):
                func_layer, func_desc = func_layer

            log(f"  Best gene: {best_gene}", fh)
            log(f"  Function: {func_desc}", fh)

            # Validate Step 6 assignment
            if step6 != "UNKNOWN":
                match = step6.upper() in best_gene.upper()
                log(f"  Step 6 validation: "
                    f"{'✓ CONFIRMED' if match else f'✗ CONFLICT — Step6={step6}, refGene={best_gene}'}", fh)

            results.append({
                "rsid": rsid, "chr": chrom, "pos": pos,
                "beta_FA": beta, "gwas_p": gwas_p,
                "layer": func_layer if func_layer != "?" else layer,
                "gene": best_gene,
                "distance_bp": 0, "overlapping": True,
                "gene_function": func_desc,
                "confidence": "CONFIRMED",
                "validation": "REFGENE_OVERLAP",
            })

        elif not nearby.empty:
            # Intergenic — use nearest gene
            log(f"  SNP is intergenic.", fh)
            log(f"\n  Nearest genes (within 500kb):", fh)
            log(f"  {'Gene':25s} {'Distance':>10s}  "
                f"{'Start':>12s}  {'End':>12s}  Strand", fh)
            log(f"  {'─'*75}", fh)

            for _, row in nearby.head(15).iterrows():
                fl, fd = GENE_FUNCTION.get(
                    row["gene"],
                    (layer, "")
                )
                if isinstance(fl, tuple):
                    fl, fd = fl
                marker = " ◄" if row["distance"] == nearby.iloc[0]["distance"] else ""
                log(f"  {row['gene']:25s} {int(row['distance']):>10,}  "
                    f"{int(row['tx_start']):>12,}  "
                    f"{int(row['tx_end']):>12,}  "
                    f"{row['strand']:>6s}  "
                    f"{fd[:40]}{marker}", fh)

            nearest   = nearby.iloc[0]
            best_gene = nearest["gene"]
            dist_bp   = int(nearest["distance"])
            fl, fd    = GENE_FUNCTION.get(
                best_gene, (layer, "Function requires literature review"))
            if isinstance(fl, tuple):
                fl, fd = fl

            log(f"\n  NEAREST GENE: {best_gene} ({dist_bp:,} bp)", fh)
            if step6 != "UNKNOWN":
                # Check if step6 gene appears anywhere in nearby
                step6_found = nearby[
                    nearby["gene"].str.upper().str.contains(
                        step6.upper(), regex=False)
                ]
                if not step6_found.empty:
                    d6 = int(step6_found.iloc[0]["distance"])
                    log(f"  Step 6 gene {step6} found at {d6:,} bp from lead SNP", fh)
                    log(f"  ✓ Step 6 assignment PRESENT in window", fh)
                    # Use step6 gene even if not nearest
                    best_gene = step6
                    dist_bp   = d6
                    fl2, fd2  = GENE_FUNCTION.get(
                        best_gene,
                        (layer, "Function requires literature review"))
                    if isinstance(fl2, tuple):
                        fl, fd = fl2
                    else:
                        fl, fd = fl2, fd2
                else:
                    log(f"  Step 6 gene {step6} NOT found in 500kb window", fh)
                    log(f"  Using nearest gene: {best_gene}", fh)

            results.append({
                "rsid": rsid, "chr": chrom, "pos": pos,
                "beta_FA": beta, "gwas_p": gwas_p,
                "layer": fl if fl != "?" else layer,
                "gene": best_gene,
                "distance_bp": dist_bp,
                "overlapping": False,
                "gene_function": fd,
                "confidence": "NEAREST_GENE",
                "validation": "REFGENE_NEAREST",
            })

        else:
            log(f"  No genes found within 500kb. "
                f"Unusual — check position.", fh)
            results.append({
                "rsid": rsid, "chr": chrom, "pos": pos,
                "beta_FA": beta, "gwas_p": gwas_p,
                "layer": layer, "gene": "INTERGENIC_500KB",
                "distance_bp": -1, "overlapping": False,
                "gene_function": "No gene within 500kb",
                "confidence": "INTERGENIC",
                "validation": "NO_GENE_FOUND",
            })

    return pd.DataFrame(results)


def print_final_table(df, fh):
    """Print and save the final annotated marker table."""
    log("\n── FINAL MARKER TABLE ────────────────────────────────────", fh)
    log("\n  PSYCHOPATHY GENETIC MARKER SET — FINAL ANNOTATED", fh)
    log("  Right UF FA Build Programme Failure Markers", fh)
    log("  OC-PSYCHOPATHY-GENETIC-MARKER-DERIVATION-001", fh)
    log(f"  {'═'*110}", fh)

    df = df.copy()
    df["broadabc"] = df["rsid"].map(BROADABC_DIR).fillna("unknown")
    df["beta_SD"]  = df["beta_FA"] / UF_FA_SD

    # Layer sort order
    order = {"A": 0, "B": 1, "B?": 2, "C": 3, "D": 4, "E": 5, "?": 6}
    df["_sort"] = df["layer"].map(order).fillna(7)
    df = df.sort_values(["_sort", "gwas_p"])

    log(f"\n  {'#':>3}  {'rsid':25}  {'chr':>4}  {'pos':>12}  "
        f"{'Gene':20}  {'Layer':>5}  "
        f"{'beta_FA':>9}  {'SDs':>5}  "
        f"{'p':>12}  BroadABC", fh)
    log(f"  {'─'*115}", fh)

    for i, (_, r) in enumerate(df.iterrows()):
        log(f"  {i+1:>3}  "
            f"{r['rsid']:25}  "
            f"{str(r['chr']):>4}  "
            f"{int(r['pos']):>12,}  "
            f"{str(r['gene'])[:20]:20}  "
            f"{str(r['layer']):>5}  "
            f"{r['beta_FA']:>+9.5f}  "
            f"{r['beta_SD']:>5.3f}  "
            f"{r['gwas_p']:>12.2e}  "
            f"{r['broadabc']}", fh)

    log(f"\n  Total: {len(df)} active markers", fh)

    log(f"\n  Layer summary:", fh)
    for layer_id in ["A", "B", "B?", "D", "E", "?"]:
        sub = df[df["layer"] == layer_id]
        if sub.empty:
            continue
        genes = ", ".join(g for g in sub["gene"].unique()
                          if g not in ("UNKNOWN","NO_GENE_FOUND",
                                       "INTERGENIC_500KB"))
        log(f"  Layer {layer_id:3}:  {len(sub):2} markers  {genes}", fh)

    log(f"\n  Gene annotations:", fh)
    log(f"  {'Gene':20}  {'Layer':>5}  Function", fh)
    log(f"  {'─'*90}", fh)
    seen = set()
    for _, r in df.iterrows():
        g = r["gene"]
        if g in seen or g in ("UNKNOWN","NO_GENE_FOUND","INTERGENIC_500KB",
                               "CHR_NOT_FOUND","FAILED"):
            continue
        seen.add(g)
        func = str(r["gene_function"])[:70]
        log(f"  {g[:20]:20}  {str(r['layer']):>5}  {func}", fh)

    df.to_csv(OUT_FINAL, sep="\t", index=False)
    log(f"\n  Saved -> {OUT_FINAL}", fh)
    return df


def main():
    with open(OUT_REPORT, "w") as fh:

        log("═"*70, fh)
        log("STEP 7B — GENE ANNOTATION FIX", fh)
        log("OC-PSYCHOPATHY-GENETIC-MARKER-DERIVATION-001", fh)
        log(f"Run: {time.strftime('%Y-%m-%d %H:%M:%S')}", fh)
        log("═"*70, fh)

        log("\n── LOADING REFGENE ───────────────────────────────────────", fh)
        df_raw = load_refgene_raw(fh)

        if df_raw is None:
            log("  Cannot proceed without refGene.txt.gz", fh)
            return

        chrom_map = build_chrom_lookup(df_raw, fh)
        df_ann    = annotate_loci(df_raw, chrom_map, fh)

        if not df_ann.empty:
            df_ann.to_csv("refgene_annotation_v2.tsv", sep="\t", index=False)
            print_final_table(df_ann, fh)

        log(f"\nDone: {time.strftime('%Y-%m-%d %H:%M:%S')}", fh)

    print(f"\nStep 7B complete. Report: {OUT_REPORT}")
    print(f"Final markers: {OUT_FINAL}")


if __name__ == "__main__":
    main()
