"""
cdRCC — Collecting Duct Renal Cell Carcinoma
FALSE ATTRACTOR ANALYSIS — SCRIPT 1 (DISCOVERY RUN)
Dataset: GSE89122
  7 CDC tumours | 6 matched normal kidney
  Illumina HiSeq 2000 RNA-seq
  Raw counts — 13 individual .count.txt.gz files
  Delivered as GSE89122_RAW.tar

Data structure confirmed by structural check:
  TAR contains: GSM{id}_{patient}-{Td1|N1}.count.txt.gz
  Format: 2-column TSV — Entrez gene ID | raw count
  No series-level matrix — merge required in script

FRAMEWORK: OrganismCore Principles-First
Date: 2026-03-03

PREDICTIONS LOCKED BEFORE DATA:
  PC1 axis: normal → attractor transition
  PC2 axis: principal cell identity programme
            AQP2 / SCNN1 / AVPR2 expected
  NOT on PC2: SLC51B / HSD17B14 / SULT2B1
            (intercalated cell — chRCC markers)

  Switch genes (predicted LOST in tumour):
    AQP2   — principal cell water channel
    SCNN1A — ENaC alpha subunit
    SCNN1B — ENaC beta subunit
    SCNN1G — ENaC gamma subunit
    AVPR2  — vasopressin receptor 2

  False attractor (predicted GAINED):
    EZH2   — epigenetic lock (present in all prior)
    MKI67  — proliferation
    VIM    — EMT / mesenchymal shift
    CDH2   — N-cadherin

  Scaffold (maintained):
    TP53, MYC, NF2

  Depth: structure predicted present
  Two subgroups: predicted recoverable on PC2/PC3

Author: Eric Robert Lawson
Framework: OrganismCore Principles-First
"""

import os
import sys
import gzip
import tarfile
import urllib.request
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import warnings
warnings.filterwarnings("ignore")

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR    = "./cdRCC_false_attractor/"
RESULTS_DIR = os.path.join(BASE_DIR, "results")
LOG_FILE    = os.path.join(RESULTS_DIR,
                           "s1_analysis_log.txt")

os.makedirs(BASE_DIR,    exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

TAR_FILE  = "GSE89122_RAW.tar"
TAR_LOCAL = os.path.join(BASE_DIR, TAR_FILE)
TAR_URL   = (
    "https://ftp.ncbi.nlm.nih.gov/geo/"
    "series/GSE89nnn/GSE89122/suppl/"
    "GSE89122_RAW.tar"
)

META_URL = (
    "https://www.ncbi.nlm.nih.gov/geo/query/"
    "acc.cgi?acc=GSE89122"
    "&targ=gsm&form=text&view=full"
)

# Confirmed sample map from structural check
# GSM → (patient_id, sample_type)
SAMPLE_MAP = {
    "GSM2359144": ("CDC1", "tumor"),
    "GSM2359145": ("CDC1", "normal"),
    "GSM2359146": ("CDC2", "tumor"),
    "GSM2359147": ("CDC2", "normal"),
    "GSM2359148": ("CDC3", "tumor"),
    "GSM2359149": ("CDC3", "normal"),
    "GSM2359150": ("CDC4", "tumor"),
    "GSM2359151": ("CDC4", "normal"),
    "GSM2359152": ("CDC5", "tumor"),
    "GSM2359153": ("CDC6", "tumor"),
    "GSM2359154": ("CDC6", "normal"),
    "GSM2359155": ("CDC7", "tumor"),
    "GSM2359156": ("CDC7", "normal"),
}

# File name → GSM mapping
# Confirmed from TAR listing in structural check
FNAME_TO_GSM = {
    "GSM2359144_CDC001-Td1.count.txt.gz": "GSM2359144",
    "GSM2359145_CDC001-N1.count.txt.gz":  "GSM2359145",
    "GSM2359146_CDC002-Td1.count.txt.gz": "GSM2359146",
    "GSM2359147_CDC002-N1.count.txt.gz":  "GSM2359147",
    "GSM2359148_CDC003-Td1.count.txt.gz": "GSM2359148",
    "GSM2359149_CDC003-N1.count.txt.gz":  "GSM2359149",
    "GSM2359150_CDC004-Td1.count.txt.gz": "GSM2359150",
    "GSM2359151_CDC004-N1.count.txt.gz":  "GSM2359151",
    "GSM2359152_CDC005-Td1.count.txt.gz": "GSM2359152",
    "GSM2359153_CDC006-Td1.count.txt.gz": "GSM2359153",
    "GSM2359154_CDC006-N1.count.txt.gz":  "GSM2359154",
    "GSM2359155_CDC007-Td1.count.txt.gz": "GSM2359155",
    "GSM2359156_CDC007-N1.count.txt.gz":  "GSM2359156",
}

# ============================================================
# GENE PANELS — PREDICTIONS LOCKED BEFORE DATA
# ============================================================

# Principal cell switch genes — predicted LOST
SWITCH_GENES = [
    "AQP2",    # principal cell water channel
    "SCNN1A",  # ENaC alpha
    "SCNN1B",  # ENaC beta
    "SCNN1G",  # ENaC gamma
    "AVPR2",   # vasopressin receptor 2
    "AQP3",    # basolateral water channel
    "AQP4",    # water channel
    "CALB1",   # distal nephron marker
    "SLC12A3", # distal convoluted tubule
    "TFCP2L1", # collecting duct TF
]

# False attractor markers — predicted GAINED
FA_MARKERS = [
    "EZH2",   # epigenetic lock — universal in series
    "MKI67",  # proliferation
    "VIM",    # EMT
    "CDH2",   # N-cadherin
    "SNAI1",  # EMT TF
    "SNAI2",  # EMT TF
    "ZEB1",   # EMT TF
    "TWIST1", # EMT TF
    "FN1",    # fibronectin
]

# Intercalated cell markers — should NOT drive PC2
# These are the chRCC switch genes
# Prediction: absent or not differentially expressed
IC_MARKERS = [
    "SLC51B",   # chRCC #1 switch gene
    "HSD17B14", # chRCC switch gene
    "SULT2B1",  # chRCC diagnostic marker
    "SLC2A2",   # chRCC PC2 discriminant
    "HSD11B2",  # intercalated cell
    "ATP6V1B1", # type A intercalated
    "ATP6V0A4", # type A intercalated
    "SLC4A9",   # type B intercalated
    "FOXI1",    # intercalated cell TF
]

# Epigenetic programme
EPIGENETIC = [
    "EZH2",   "EED",    "SUZ12",
    "KDM6A",  "DNMT3A", "BMI1",
    "JARID2", "KDM2B",  "SETD2",
]

# EMT
EMT = [
    "VIM",   "CDH1",  "CDH2",
    "SNAI1", "SNAI2", "ZEB1",
    "ZEB2",  "TWIST1","FN1",
    "MMP2",  "MMP9",
]

# Proliferation
PROLIF = [
    "MKI67", "PCNA",  "TOP2A",
    "AURKA", "PLK1",  "BUB1B",
    "CCND1", "CCNE1", "CDK4",
]

# Scaffold
SCAFFOLD = [
    "TP53", "PTEN", "RB1",
    "MYC",  "NF2",  "KRAS",
    "EGFR", "CDKN2A",
]

# Collecting duct identity
CD_IDENTITY = [
    "PAX8",    # renal lineage TF
    "CDH16",   # kidney cadherin
    "UMOD",    # thick ascending limb
    "TMEM213", # collecting duct marker
    "GATA3",   # collecting duct / urothelial
    "KRT7",    # cdRCC cytokeratin
    "KRT19",   # cytokeratin
]

# Housekeeping sanity check
HOUSEKEEPING = [
    "ACTB", "GAPDH", "B2M",
    "HPRT1", "SDHA",
]

ALL_TARGET = list(dict.fromkeys(
    SWITCH_GENES + FA_MARKERS + IC_MARKERS +
    EPIGENETIC + EMT + PROLIF +
    SCAFFOLD + CD_IDENTITY + HOUSEKEEPING
))

# ============================================================
# LOGGING
# ============================================================

log_lines = []

def log(msg=""):
    print(msg)
    log_lines.append(str(msg))

def write_log():
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines))

# ============================================================
# STEP 0: DOWNLOAD TAR IF NEEDED
# ============================================================

def download_tar():
    log("=" * 65)
    log("STEP 0 — DATA ACQUISITION")
    log("Dataset: GSE89122")
    log("  7 CDC tumours | 6 matched normal kidney")
    log("  Format: GSE89122_RAW.tar (13 count files)")
    log("=" * 65)

    if os.path.exists(TAR_LOCAL):
        sz = os.path.getsize(TAR_LOCAL) / 1e6
        if sz > 0.5:
            log(f"  TAR found: {TAR_LOCAL} ({sz:.2f} MB)")
            return True

    log(f"  Downloading: {TAR_FILE}")
    log(f"  URL: {TAR_URL}")

    def hook(count, block, total):
        if total > 0:
            pct = min(count * block / total * 100, 100)
            mb  = count * block / 1e6
            sys.stdout.write(
                f"\r  {mb:.2f} MB  {pct:.1f}%"
            )
            sys.stdout.flush()

    try:
        urllib.request.urlretrieve(TAR_URL,
                                   TAR_LOCAL, hook)
        print()
        sz = os.path.getsize(TAR_LOCAL) / 1e6
        log(f"  Done: {sz:.2f} MB")
        return True
    except Exception as e:
        log(f"  ERROR: {e}")
        return False

# ============================================================
# STEP 1: EXTRACT AND MERGE COUNT FILES FROM TAR
# ============================================================

def extract_and_merge():
    log("")
    log("=" * 65)
    log("STEP 1 — EXTRACT AND MERGE COUNT FILES")
    log("  Source: GSE89122_RAW.tar")
    log("  13 files: GSM*.count.txt.gz")
    log("=" * 65)

    cache = os.path.join(RESULTS_DIR,
                         "raw_counts_merged.csv")
    if os.path.exists(cache):
        log(f"  Loading cached merged matrix: {cache}")
        df = pd.read_csv(cache, index_col=0)
        log(f"  Shape: {df.shape}")
        return df

    frames = {}
    skipped_genes = set()

    with tarfile.open(TAR_LOCAL, "r") as tar:
        members = tar.getmembers()
        log(f"  TAR contains {len(members)} files")

        for member in members:
            fname = os.path.basename(member.name)
            gsm   = FNAME_TO_GSM.get(fname)

            if gsm is None:
                # Try to match by GSM prefix
                for f, g in FNAME_TO_GSM.items():
                    if fname in f or f in fname:
                        gsm = g
                        break

            if gsm is None:
                log(f"  SKIP (no GSM match): {fname}")
                continue

            patient, stype = SAMPLE_MAP[gsm]
            log(f"  Reading: {fname} → "
                f"{gsm} ({patient} {stype})")

            try:
                f_obj = tar.extractfile(member)
                if f_obj is None:
                    log(f"    Cannot extract: {fname}")
                    continue

                raw_bytes = f_obj.read()

                # Decompress gz
                try:
                    content = gzip.decompress(
                        raw_bytes
                    ).decode("utf-8")
                except Exception:
                    content = raw_bytes.decode("utf-8")

                lines = content.strip().split("\n")

                # Parse gene → count
                gene_counts = {}
                n_special   = 0

                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split("\t")
                    if len(parts) < 2:
                        parts = line.split()
                    if len(parts) < 2:
                        continue

                    gene_id  = parts[0].strip()
                    count_str = parts[1].strip()

                    # Skip HTSeq special summary lines
                    if gene_id.startswith("__"):
                        n_special += 1
                        continue
                    # Skip header lines
                    if not count_str.replace(
                        ".", ""
                    ).isdigit():
                        continue

                    try:
                        gene_counts[gene_id] = \
                            float(count_str)
                    except ValueError:
                        pass

                log(f"    Genes: {len(gene_counts)}  "
                    f"Special lines: {n_special}")

                if gene_counts:
                    frames[gsm] = pd.Series(
                        gene_counts,
                        name=gsm,
                        dtype=float
                    )

            except Exception as e:
                log(f"    ERROR reading {fname}: {e}")

    if not frames:
        log("  ERROR: No count files loaded")
        return None

    log(f"\n  Loaded {len(frames)} samples")

    # Merge — outer join preserves all genes
    merged = pd.DataFrame(frames)
    merged = merged.fillna(0)

    log(f"  Merged shape: {merged.shape}")
    log(f"  Samples: {list(merged.columns)}")

    # Report first few gene IDs
    log(f"\n  First 5 gene IDs:")
    for g in list(merged.index[:5]):
        log(f"    {g}")

    # Detect gene ID type
    sample_ids = [str(x) for x in list(
        merged.index[:10]
    )]
    is_entrez  = all(
        s.replace(".", "").isdigit()
        for s in sample_ids
        if s.strip()
    )
    is_ensembl = any(
        s.startswith("ENSG") for s in sample_ids
    )
    id_type = (
        "ENTREZ"  if is_entrez  else
        "ENSEMBL" if is_ensembl else
        "SYMBOL"
    )
    log(f"\n  Gene ID type detected: {id_type}")

    # Save
    merged.to_csv(cache)
    log(f"  Saved: {cache}")

    return merged

# ============================================================
# STEP 2: GENE SYMBOL MAPPING
# For Entrez or Ensembl IDs — map to symbols
# Uses NCBI gene2refseq or Ensembl BioMart
# ============================================================

def fetch_entrez_symbols(entrez_ids):
    """
    Build Entrez → symbol map using NCBI eutils
    for the specific genes we need.
    Fast: only queries genes in our target panel.
    """
    log("")
    log("--- Building Entrez → symbol map ---")

    cache = os.path.join(BASE_DIR,
                         "entrez_symbol_map.csv")
    if os.path.exists(cache):
        df = pd.read_csv(cache,
                         dtype={"entrez": str})
        mapping = dict(zip(df["entrez"],
                           df["symbol"]))
        log(f"  Loaded cached map: {len(mapping)} genes")
        return mapping

    # Query NCBI for target gene symbols
    # Use eutils esearch to find Entrez IDs for our
    # target gene symbols, then build reverse map
    mapping = {}

    # First try: query symbol → entrez via esearch
    base = (
        "https://eutils.ncbi.nlm.nih.gov/"
        "entrez/eutils/"
    )

    import time
    import re as re_mod

    for symbol in ALL_TARGET:
        url = (
            f"{base}esearch.fcgi?"
            f"db=gene&term={symbol}[Gene+Name]"
            f"+AND+Homo+sapiens[Organism]"
            f"&retmode=text&retmax=3"
        )
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(
                req, timeout=15
            ) as r:
                text = r.read().decode("utf-8")
            ids = re_mod.findall(
                r"<Id>(\d+)</Id>", text
            )
            for eid in ids[:1]:
                mapping[eid] = symbol
        except Exception:
            pass
        time.sleep(0.1)

    log(f"  Mapped {len(mapping)} target genes")

    # Save
    rows = [{"entrez": k, "symbol": v}
            for k, v in mapping.items()]
    pd.DataFrame(rows).to_csv(cache, index=False)

    return mapping

def build_symbol_index(counts_df):
    """
    Given a raw counts matrix with gene IDs as index,
    detect ID type and return a symbol-indexed matrix.

    Handles:
    - Entrez IDs (integers)
    - Ensembl IDs (ENSG...)
    - Gene symbols (already correct)
    """
    log("")
    log("=" * 65)
    log("STEP 2 — GENE ID MAPPING")
    log("=" * 65)

    ids = [str(x) for x in list(counts_df.index[:15])]
    is_entrez  = all(
        s.replace(".", "").isdigit()
        for s in ids if s.strip()
    )
    is_ensembl = any(
        s.startswith("ENSG") for s in ids
    )

    log(f"  ID sample: {ids[:8]}")
    log(f"  Entrez:    {is_entrez}")
    log(f"  Ensembl:   {is_ensembl}")

    if not is_entrez and not is_ensembl:
        log("  IDs appear to be gene symbols — "
            "using directly")
        return counts_df

    if is_entrez:
        entrez_ids = [
            str(x) for x in counts_df.index
        ]
        mapping = fetch_entrez_symbols(entrez_ids)

        if mapping:
            counts_df.index = counts_df.index.astype(str)
            counts_df["symbol"] = counts_df.index.map(
                mapping
            )
            mapped = counts_df.dropna(
                subset=["symbol"]
            )
            mapped = mapped.drop_duplicates(
                subset=["symbol"]
            )
            mapped = mapped.set_index("symbol")
            log(f"  After mapping: {mapped.shape[0]} "
                f"genes with symbols")
            log(f"  Unmapped genes: "
                f"{len(counts_df) - len(mapped)}")
            return mapped
        else:
            log("  WARNING: Could not fetch symbol map")
            log("  Proceeding with Entrez IDs")
            return counts_df

    if is_ensembl:
        log("  Ensembl IDs detected")
        log("  Fetching Ensembl → symbol from BioMart")
        biomart_url = (
            "https://biomart.genenames.org/martservice/results"
            "?action=results&mart=ENSEMBL_MART_ENSEMBL"
            "&dataset=hsapiens_gene_ensembl"
            "&attributes=ensembl_gene_id,hgnc_symbol"
            "&format=TSV"
        )
        try:
            req = urllib.request.Request(
                biomart_url,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(
                req, timeout=30
            ) as r:
                text = r.read().decode("utf-8")
            lines = text.strip().split("\n")
            ens_map = {}
            for line in lines[1:]:
                parts = line.split("\t")
                if len(parts) >= 2 and parts[1].strip():
                    ens_map[parts[0]] = parts[1]
            log(f"  BioMart returned {len(ens_map)} mappings")
            counts_df["symbol"] = counts_df.index.map(
                ens_map
            )
            mapped = counts_df.dropna(
                subset=["symbol"]
            )
            mapped = mapped.drop_duplicates(
                subset=["symbol"]
            )
            mapped = mapped.set_index("symbol")
            return mapped
        except Exception as e:
            log(f"  BioMart error: {e}")
            log("  Proceeding with Ensembl IDs")
            return counts_df

    return counts_df

# ============================================================
# STEP 3: NORMALISE — CPM + log2
# ============================================================

def normalise(counts_df):
    """
    Raw counts → CPM → log2(CPM + 1)
    CPM = counts per million mapped reads
    Standard for RNA-seq when no DESeq2/edgeR available
    """
    log("")
    log("=" * 65)
    log("STEP 3 — NORMALISATION")
    log("  Raw counts → CPM → log2(CPM + 1)")
    log("=" * 65)

    # Library sizes
    lib_sizes = counts_df.sum(axis=0)
    log("\n  Library sizes (total mapped reads):")
    for gsm in lib_sizes.index:
        p, t = SAMPLE_MAP.get(gsm, ("?","?"))
        log(f"    {gsm} ({p:6s} {t:6s}): "
            f"{lib_sizes[gsm]:>12,.0f}")

    log(f"\n  Min library size: "
        f"{lib_sizes.min():>12,.0f}")
    log(f"  Max library size: "
        f"{lib_sizes.max():>12,.0f}")
    log(f"  Ratio max/min:    "
        f"{lib_sizes.max()/lib_sizes.min():.2f}x")

    # CPM
    cpm = counts_df.div(lib_sizes, axis=1) * 1e6

    # Filter: keep genes with mean CPM > 1
    mean_cpm = cpm.mean(axis=1)
    before   = len(cpm)
    cpm      = cpm[mean_cpm > 1.0]
    after    = len(cpm)
    log(f"\n  Gene filter (mean CPM > 1):")
    log(f"    Before: {before}")
    log(f"    After:  {after}")
    log(f"    Removed: {before - after} "
        f"low-expression genes")

    # log2 transform
    log2_cpm = np.log2(cpm + 1)

    log(f"\n  log2(CPM + 1) value range:")
    vals = log2_cpm.values.flatten()
    log(f"    Min:    {vals.min():.3f}")
    log(f"    Max:    {vals.max():.3f}")
    log(f"    Mean:   {vals.mean():.3f}")
    log(f"    Median: {np.median(vals):.3f}")

    return log2_cpm

# ============================================================
# BUILD METADATA FRAME
# ============================================================

def build_metadata(log2_cpm):
    cols  = list(log2_cpm.columns)
    rows  = []
    for gsm in cols:
        p, t = SAMPLE_MAP.get(gsm, ("unknown","unknown"))
        rows.append({
            "gsm":     gsm,
            "patient": p,
            "type":    t,
        })
    return pd.DataFrame(rows)

# ============================================================
# STEP 4: SADDLE POINT ANALYSIS
# ============================================================

def saddle_point_analysis(log2_cpm, meta):
    log("")
    log("=" * 65)
    log("STEP 4 — SADDLE POINT ANALYSIS")
    log("  Tumour vs Normal per gene")
    log("=" * 65)

    tumor_gsm  = meta[
        meta["type"] == "tumor"
    ]["gsm"].tolist()
    normal_gsm = meta[
        meta["type"] == "normal"
    ]["gsm"].tolist()

    tumor_gsm  = [g for g in tumor_gsm
                  if g in log2_cpm.columns]
    normal_gsm = [g for g in normal_gsm
                  if g in log2_cpm.columns]

    log(f"  Tumour: {len(tumor_gsm)}  "
        f"Normal: {len(normal_gsm)}")

    tumor_df  = log2_cpm[tumor_gsm]
    normal_df = log2_cpm[normal_gsm]

    results = []
    for gene in log2_cpm.index:
        t_vals = tumor_df.loc[gene].values.astype(float)
        n_vals = normal_df.loc[gene].values.astype(float)
        mean_t = float(np.mean(t_vals))
        mean_n = float(np.mean(n_vals))
        diff   = mean_t - mean_n

        if len(t_vals) >= 3 and len(n_vals) >= 2:
            try:
                _, pval = stats.ttest_ind(
                    t_vals, n_vals,
                    equal_var=False
                )
            except Exception:
                pval = 1.0
        else:
            pval = 1.0

        results.append({
            "gene":   gene,
            "mean_t": mean_t,
            "mean_n": mean_n,
            "diff":   diff,
            "pval":   pval,
        })

    saddle = pd.DataFrame(results).set_index("gene")
    saddle = saddle.sort_values("diff")

    # Save
    out = os.path.join(RESULTS_DIR,
                       "saddle_table.csv")
    saddle.to_csv(out)
    log(f"  Saved: {out}")

    # Report all target genes
    log("\n  TARGET GENE SADDLE TABLE")
    log(f"  {'Gene':12s}  {'MeanT':7s}  "
        f"{'MeanN':7s}  {'Diff':7s}  "
        f"{'p':8s}  Direction")
    log("  " + "-" * 65)

    report_genes = (
        SWITCH_GENES + FA_MARKERS + IC_MARKERS +
        CD_IDENTITY + HOUSEKEEPING[:3]
    )

    for gene in report_genes:
        if gene not in saddle.index:
            log(f"  {gene:12s}  NOT IN DATASET")
            continue
        row = saddle.loc[gene]
        d = float(row["diff"])
        p = float(row["pval"])
        direction = (
            "LOST   ↓↓" if d < -1.0 else
            "lost    ↓" if d < -0.5 else
            "gained  ↑" if d >  0.5 else
            "GAINED ↑↑" if d >  1.0 else
            "stable  ="
        )
        # Recheck after assignment
        if d < -1.0:
            direction = "LOST   ↓↓"
        elif d < -0.5:
            direction = "lost    ↓"
        elif d >  1.0:
            direction = "GAINED ↑↑"
        elif d >  0.5:
            direction = "gained  ↑"
        else:
            direction = "stable  ="

        fmt_p = (f"{p:.4f}" if p >= 0.0001
                 else "<0.0001")
        log(
            f"  {gene:12s}  {row['mean_t']:7.3f}  "
            f"{row['mean_n']:7.3f}  {d:+7.3f}  "
            f"{fmt_p:8s}  {direction}"
        )

    # Top movers
    log("\n  TOP 15 GENES LOST IN TUMOUR:")
    for gene, row in saddle.head(15).iterrows():
        log(f"    {gene:15s}  "
            f"diff={float(row['diff']):+.3f}  "
            f"T={float(row['mean_t']):.3f}  "
            f"N={float(row['mean_n']):.3f}")

    log("\n  TOP 15 GENES GAINED IN TUMOUR:")
    for gene, row in saddle.tail(15).iterrows():
        log(f"    {gene:15s}  "
            f"diff={float(row['diff']):+.3f}  "
            f"T={float(row['mean_t']):.3f}  "
            f"N={float(row['mean_n']):.3f}")

    return saddle

# ============================================================
# STEP 5: PCA — GEOMETRY
# ============================================================

def run_pca(log2_cpm, meta, saddle):
    log("")
    log("=" * 65)
    log("STEP 5 — PCA GEOMETRY")
    log("=" * 65)

    # Transpose: samples × genes
    X = log2_cpm.T
    gene_names = list(log2_cpm.index)

    log(f"  Matrix: {X.shape[0]} samples × "
        f"{X.shape[1]} genes")

    # Standardise
    scaler  = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # PCA — max components = n_samples - 1
    n_comp = min(X.shape[0], X.shape[1], 12)
    pca    = PCA(n_components=n_comp)
    coords = pca.fit_transform(X_scaled)
    var    = pca.explained_variance_ratio_

    log(f"\n  Variance explained:")
    cumvar = 0.0
    for i, v in enumerate(var):
        cumvar += v
        marker = " ←" if i < 3 else ""
        log(f"    PC{i+1:2d}: {v*100:6.2f}%  "
            f"cumulative: {cumvar*100:6.2f}%"
            f"{marker}")
        if cumvar > 0.97 and i > 3:
            break

    # Build PCA dataframe
    n_show = min(6, n_comp)
    pca_df = pd.DataFrame(
        coords[:, :n_show],
        columns=[f"PC{i+1}" for i in range(n_show)],
        index=X.index
    )
    pca_df = pca_df.join(
        meta.set_index("gsm")[["patient", "type"]]
    )

    log("\n  PCA COORDINATES")
    log(f"  {'GSM':12s}  {'Patient':8s}  "
        f"{'Type':6s}  {'PC1':8s}  "
        f"{'PC2':8s}  {'PC3':8s}")
    log("  " + "-" * 62)

    for gsm, row in pca_df.iterrows():
        log(
            f"  {gsm:12s}  "
            f"{row['patient']:8s}  "
            f"{row['type']:6s}  "
            f"{float(row.get('PC1',0)):+8.3f}  "
            f"{float(row.get('PC2',0)):+8.3f}  "
            f"{float(row.get('PC3',0)):+8.3f}"
        )

    # PC1 separation test
    t_pc1 = pca_df[
        pca_df["type"] == "tumor"
    ]["PC1"].values.astype(float)
    n_pc1 = pca_df[
        pca_df["type"] == "normal"
    ]["PC1"].values.astype(float)

    sep = float(np.mean(t_pc1) - np.mean(n_pc1))
    log(f"\n  PC1 SEPARATION")
    log(f"    Mean tumour PC1:  {np.mean(t_pc1):+.3f}")
    log(f"    Mean normal PC1:  {np.mean(n_pc1):+.3f}")
    log(f"    Separation:       {sep:+.3f}")

    if abs(sep) > 3:
        log("    → PC1 SEPARATES tumour/normal ✓")
        log("    → PC1 = attractor transition axis")
    elif abs(sep) > 1:
        log("    → PC1 weak separation — check PC2")
    else:
        log("    → PC1 does not separate — "
            "check all PCs")

    # PC loadings
    loadings = pd.DataFrame(
        pca.components_[:n_show].T,
        index=gene_names,
        columns=[f"PC{i+1}" for i in range(n_show)]
    )

    log("\n  PC1 TOP LOADINGS — LOST direction (neg):")
    pc1_sorted = loadings["PC1"].sort_values()
    for gene in pc1_sorted.head(15).index:
        log(f"    {gene:15s}  "
            f"{float(pc1_sorted[gene]):+.5f}")

    log("\n  PC1 TOP LOADINGS — GAINED direction (pos):")
    for gene in pc1_sorted.tail(15).index:
        log(f"    {gene:15s}  "
            f"{float(pc1_sorted[gene]):+.5f}")

    log("\n  PC2 TOP LOADINGS — negative pole:")
    pc2_sorted = loadings["PC2"].sort_values()
    for gene in pc2_sorted.head(15).index:
        log(f"    {gene:15s}  "
            f"{float(pc2_sorted[gene]):+.5f}")

    log("\n  PC2 TOP LOADINGS — positive pole:")
    for gene in pc2_sorted.tail(15).index:
        log(f"    {gene:15s}  "
            f"{float(pc2_sorted[gene]):+.5f}")

    # Target gene loadings
    log("\n  TARGET GENE PC1/PC2 LOADINGS:")
    log(f"  {'Gene':12s}  {'PC1':8s}  {'PC2':8s}")
    log("  " + "-" * 35)
    for gene in (SWITCH_GENES + FA_MARKERS
                 + IC_MARKERS[:4]):
        if gene in loadings.index:
            pc1 = float(loadings.loc[gene, "PC1"])
            pc2 = float(loadings.loc[gene, "PC2"])
            log(f"  {gene:12s}  {pc1:+8.5f}  "
                f"{pc2:+8.5f}")

    # Save
    pca_df.to_csv(
        os.path.join(RESULTS_DIR, "pca_coords.csv")
    )
    loadings.to_csv(
        os.path.join(RESULTS_DIR, "pca_loadings.csv")
    )

    return pca_df, pca, loadings, var

# ============================================================
# STEP 6: DEPTH SCORING
# ============================================================

def depth_scoring(log2_cpm, meta, pca_df):
    log("")
    log("=" * 65)
    log("STEP 6 — DEPTH SCORING")
    log("  Position on PC1 attractor axis")
    log("  Normalised 0→1 across all samples")
    log("=" * 65)

    pc1 = pca_df["PC1"].astype(float)

    # Determine orientation:
    # tumours should be deeper (higher depth)
    # if mean tumour PC1 < mean normal PC1,
    # invert the axis
    t_mean = pc1[
        pca_df["type"] == "tumor"
    ].mean()
    n_mean = pc1[
        pca_df["type"] == "normal"
    ].mean()

    if t_mean < n_mean:
        pc1 = -pc1
        log("  PC1 inverted (tumours were neg pole)")

    mn, mx = pc1.min(), pc1.max()
    depth  = (pc1 - mn) / (mx - mn) \
        if mx > mn else pc1 * 0

    pca_df["depth"] = depth.values

    log(f"\n  {'GSM':12s}  {'Patient':8s}  "
        f"{'Type':6s}  {'PC1':8s}  {'Depth':6s}")
    log("  " + "-" * 52)

    for gsm, row in pca_df.sort_values(
        "depth", ascending=False
    ).iterrows():
        log(
            f"  {gsm:12s}  "
            f"{row['patient']:8s}  "
            f"{row['type']:6s}  "
            f"{float(row['PC1']):+8.3f}  "
            f"{float(row['depth']):.4f}"
        )

    t_depth = pca_df[
        pca_df["type"] == "tumor"
    ]["depth"].astype(float).values
    n_depth = pca_df[
        pca_df["type"] == "normal"
    ]["depth"].astype(float).values

    mis = float(np.mean(t_depth))
    log(f"\n  Tumour depth:  "
        f"mean={np.mean(t_depth):.4f}  "
        f"std={np.std(t_depth):.4f}")
    log(f"  Normal depth:  "
        f"mean={np.mean(n_depth):.4f}  "
        f"std={np.std(n_depth):.4f}")
    log(f"  MIS (mean tumour depth): {mis:.4f}")

    if len(t_depth) >= 3 and len(n_depth) >= 2:
        tstat, pval = stats.ttest_ind(
            t_depth, n_depth, equal_var=False
        )
        log(f"\n  T-test depth tumour vs normal:")
        log(f"    t={tstat:.3f}  p={pval:.4f}")
        if pval < 0.05:
            log("    STATUS: Depth significantly higher "
                "in tumour ✓")
        else:
            log("    STATUS: p > 0.05 — small N, "
                "direction more important than p-value")

    # Depth correlation for target genes
    log("\n  DEPTH CORRELATION — KEY GENES")
    log(f"  {'Gene':12s}  {'r':7s}  {'p':8s}  note")
    log("  " + "-" * 48)

    all_gsm   = list(pca_df.index)
    all_depth = pca_df.loc[
        all_gsm, "depth"
    ].astype(float).values

    check = (SWITCH_GENES + FA_MARKERS
             + IC_MARKERS[:4])
    for gene in check:
        if gene not in log2_cpm.index:
            continue
        expr = log2_cpm.loc[
            gene, all_gsm
        ].astype(float).values
        if np.std(expr) < 1e-9:
            continue
        try:
            r, p = stats.pearsonr(all_depth, expr)
        except Exception:
            continue
        note = (
            "depth+gain" if r > 0.5  else
            "depth+loss" if r < -0.5 else
            "weak"
        )
        fmt_p = (f"{p:.4f}" if p >= 0.0001
                 else "<0.0001")
        log(f"  {gene:12s}  {r:+7.4f}  "
            f"{fmt_p:8s}  {note}")

    pca_df[
        ["patient", "type", "PC1", "depth"]
    ].to_csv(
        os.path.join(RESULTS_DIR,
                     "depth_scores.csv")
    )

    return pca_df

# ============================================================
# STEP 7: FIGURE
# ============================================================

def generate_figure(pca_df, saddle, var):
    log("")
    log("--- Generating figure ---")

    colours = {
        "tumor":  "#d62728",
        "normal": "#1f77b4",
    }

    fig = plt.figure(figsize=(18, 12))
    gs  = gridspec.GridSpec(
        2, 3, figure=fig,
        hspace=0.42, wspace=0.35
    )

    # ---- A: PC1 vs PC2 ----
    ax1 = fig.add_subplot(gs[0, 0])
    for stype, grp in pca_df.groupby("type"):
        ax1.scatter(
            grp["PC1"].astype(float),
            grp.get("PC2", pd.Series(
                [0]*len(grp)
            )).astype(float),
            c=colours[stype], label=stype,
            s=100, alpha=0.9,
            edgecolors="k", linewidths=0.6
        )
    for gsm, row in pca_df.iterrows():
        ax1.annotate(
            row["patient"],
            (float(row["PC1"]),
             float(row.get("PC2", 0))),
            fontsize=7, ha="center",
            va="bottom", fontweight="bold"
        )
    ax1.set_xlabel(
        f"PC1 ({var[0]*100:.1f}%)", fontsize=10
    )
    ax1.set_ylabel(
        f"PC2 ({var[1]*100:.1f}%)", fontsize=10
    )
    ax1.set_title(
        "PCA — cdRCC Tumour vs Normal",
        fontsize=11, fontweight="bold"
    )
    ax1.legend(fontsize=8)
    ax1.axhline(0, color="grey", lw=0.5, ls="--")
    ax1.axvline(0, color="grey", lw=0.5, ls="--")

    # ---- B: PC1 vs PC3 ----
    ax2 = fig.add_subplot(gs[0, 1])
    if "PC3" in pca_df.columns:
        for stype, grp in pca_df.groupby("type"):
            ax2.scatter(
                grp["PC1"].astype(float),
                grp["PC3"].astype(float),
                c=colours[stype], label=stype,
                s=100, alpha=0.9,
                edgecolors="k", linewidths=0.6
            )
        for gsm, row in pca_df.iterrows():
            ax2.annotate(
                row["patient"],
                (float(row["PC1"]),
                 float(row["PC3"])),
                fontsize=7, ha="center",
                va="bottom"
            )
        ax2.set_xlabel(
            f"PC1 ({var[0]*100:.1f}%)", fontsize=10
        )
        ax2.set_ylabel(
            f"PC3 ({var[2]*100:.1f}%)", fontsize=10
        )
        ax2.set_title("PC1 vs PC3", fontsize=11)
        ax2.axhline(0, color="grey", lw=0.5, ls="--")
        ax2.axvline(0, color="grey", lw=0.5, ls="--")

    # ---- C: Scree plot ----
    ax3 = fig.add_subplot(gs[0, 2])
    n_plot = min(10, len(var))
    pcs    = [f"PC{i+1}" for i in range(n_plot)]
    ax3.bar(
        pcs, var[:n_plot] * 100,
        color="#2ca02c", alpha=0.8,
        edgecolor="k"
    )
    ax3.set_xlabel("Component", fontsize=10)
    ax3.set_ylabel("Variance (%)", fontsize=10)
    ax3.set_title("Variance Explained", fontsize=11)
    ax3.tick_params(axis="x", labelsize=8)

    # ---- D: Switch gene diffs ----
    ax4 = fig.add_subplot(gs[1, 0])
    sw_found = [g for g in SWITCH_GENES
                if g in saddle.index]
    if sw_found:
        diffs = [float(saddle.loc[g, "diff"])
                 for g in sw_found]
        clrs  = [
            "#d62728" if d > 0 else "#1f77b4"
            for d in diffs
        ]
        ax4.barh(sw_found, diffs, color=clrs,
                 alpha=0.85, edgecolor="k")
        ax4.axvline(0, color="k", lw=1.0)
        ax4.set_xlabel(
            "Mean Diff (Tumour − Normal log2 CPM)",
            fontsize=9
        )
        ax4.set_title(
            "Switch Genes\n(predicted LOST)",
            fontsize=10, fontweight="bold"
        )
        ax4.invert_yaxis()

    # ---- E: FA marker diffs ----
    ax5 = fig.add_subplot(gs[1, 1])
    fa_found = [g for g in FA_MARKERS
                if g in saddle.index]
    if fa_found:
        diffs = [float(saddle.loc[g, "diff"])
                 for g in fa_found]
        clrs  = [
            "#d62728" if d > 0 else "#1f77b4"
            for d in diffs
        ]
        ax5.barh(fa_found, diffs, color=clrs,
                 alpha=0.85, edgecolor="k")
        ax5.axvline(0, color="k", lw=1.0)
        ax5.set_xlabel(
            "Mean Diff (Tumour − Normal log2 CPM)",
            fontsize=9
        )
        ax5.set_title(
            "False Attractor Markers\n"
            "(predicted GAINED)",
            fontsize=10, fontweight="bold"
        )
        ax5.invert_yaxis()

    # ---- F: Depth scores ----
    ax6 = fig.add_subplot(gs[1, 2])
    if "depth" in pca_df.columns:
        sdf = pca_df.sort_values("depth")
        bar_c = [
            colours[t] for t in sdf["type"]
        ]
        labels = [
            f"{r['patient']} "
            f"({'T' if r['type']=='tumor' else 'N'})"
            for _, r in sdf.iterrows()
        ]
        ax6.barh(
            labels,
            sdf["depth"].astype(float),
            color=bar_c, alpha=0.85,
            edgecolor="k"
        )
        ax6.set_xlabel(
            "Attractor Depth (0→1)", fontsize=10
        )
        ax6.set_title(
            "Depth Scores\nRed=Tumour  Blue=Normal",
            fontsize=10, fontweight="bold"
        )
        ax6.axvline(
            0.5, color="grey", lw=0.8, ls="--"
        )

    fig.suptitle(
        "cdRCC False Attractor Analysis — "
        "Script 1 Discovery Run\n"
        "GSE89122 | 7 CDC tumours | "
        "6 matched normal kidney | "
        "Illumina HiSeq 2000",
        fontsize=12, fontweight="bold"
    )

    out = os.path.join(
        RESULTS_DIR, "cdRCC_s1_figure.png"
    )
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    log(f"  Saved: {out}")

# ============================================================
# STEP 8: EXPORT
# ============================================================

def export(log2_cpm, meta, saddle):
    log("")
    log("--- Exporting data ---")
    gm  = os.path.join(RESULTS_DIR,
                       "gene_matrix.csv")
    mf  = os.path.join(RESULTS_DIR,
                       "metadata.csv")
    log2_cpm.to_csv(gm)
    meta.to_csv(mf, index=False)
    log(f"  gene_matrix.csv: {log2_cpm.shape}")
    log(f"  metadata.csv:    {len(meta)} samples")

# ============================================================
# STEP 9: ATTRACTOR SUMMARY
# ============================================================

def attractor_summary(pca_df, saddle, var):
    log("")
    log("=" * 65)
    log("ATTRACTOR SUMMARY — SCRIPT 1")
    log("=" * 65)

    t_pc1 = pca_df[
        pca_df["type"] == "tumor"
    ]["PC1"].astype(float).values
    n_pc1 = pca_df[
        pca_df["type"] == "normal"
    ]["PC1"].astype(float).values

    log(f"\n  PC1 variance:      {var[0]*100:.2f}%")
    log(f"  PC2 variance:      {var[1]*100:.2f}%")
    log(f"  PC1 separation:    "
        f"{np.mean(t_pc1)-np.mean(n_pc1):+.3f}")

    log("\n  PREDICTION VERIFICATION")
    log("  " + "-" * 50)

    log("\n  Switch genes (predicted LOST):")
    for gene in SWITCH_GENES:
        if gene not in saddle.index:
            log(f"    {gene:12s}  not detected")
            continue
        d = float(saddle.loc[gene, "diff"])
        status = (
            "✓ LOST    " if d < -1.0 else
            "~ lost    " if d < -0.3 else
            "✗ NOT LOST"
        )
        log(f"    {gene:12s}  diff={d:+.3f}  {status}")

    log("\n  FA markers (predicted GAINED):")
    for gene in FA_MARKERS:
        if gene not in saddle.index:
            log(f"    {gene:12s}  not detected")
            continue
        d = float(saddle.loc[gene, "diff"])
        status = (
            "✓ GAINED  " if d >  1.0 else
            "~ gained  " if d >  0.3 else
            "✗ NOT GAINED"
        )
        log(f"    {gene:12s}  diff={d:+.3f}  {status}")

    log("\n  IC markers (should NOT dominate PC2):")
    for gene in IC_MARKERS[:5]:
        if gene not in saddle.index:
            log(f"    {gene:12s}  not in dataset")
            continue
        d = float(saddle.loc[gene, "diff"])
        log(f"    {gene:12s}  diff={d:+.3f}")

    if "depth" in pca_df.columns:
        mis = float(pca_df[
            pca_df["type"] == "tumor"
        ]["depth"].mean())
        log(f"\n  MIS (mean tumour depth): {mis:.4f}")
        desc = (
            "DEEP — aggressive biology predicted"
            if mis > 0.65 else
            "MODERATE attractor depth"
            if mis > 0.45 else
            "SHALLOW — check PC1 orientation"
        )
        log(f"  Interpretation: {desc}")

    log("\n  STATUS: SCRIPT 1 COMPLETE")
    log("  Lock all findings before literature check.")
    log("  Do NOT search literature until this log "
        "is saved.")

# ============================================================
# MAIN
# ============================================================

def main():
    log("=" * 65)
    log("cdRCC — COLLECTING DUCT CARCINOMA")
    log("FALSE ATTRACTOR ANALYSIS — SCRIPT 1")
    log("Dataset: GSE89122")
    log("Date: 2026-03-03")
    log("=" * 65)
    log("PREDICTIONS LOCKED:")
    log("  PC1 = normal → attractor transition")
    log("  PC2 = principal cell identity")
    log("  Switch: AQP2 / SCNN1A/B/G / AVPR2")
    log("  FA:     EZH2 / MKI67 / VIM / CDH2")
    log("  IC markers (SLC51B etc) NOT on PC2")
    log("=" * 65)

    # Step 0 — ensure TAR is present
    ok = download_tar()
    if not ok:
        log("FATAL: TAR not available")
        return

    # Step 1 — extract and merge
    counts = extract_and_merge()
    if counts is None:
        log("FATAL: Could not build count matrix")
        return

    # Step 2 — symbol mapping
    counts = build_symbol_index(counts)

    # Step 3 — normalise
    log2_cpm = normalise(counts)

    # Build metadata
    meta = build_metadata(log2_cpm)

    # Step 4 — saddle point
    saddle = saddle_point_analysis(log2_cpm, meta)

    # Step 5 — PCA
    pca_df, pca, loadings, var = run_pca(
        log2_cpm, meta, saddle
    )

    # Step 6 — depth
    pca_df = depth_scoring(log2_cpm, meta, pca_df)

    # Step 7 — figure
    generate_figure(pca_df, saddle, var)

    # Step 8 — export
    export(log2_cpm, meta, saddle)

    # Step 9 — summary
    attractor_summary(pca_df, saddle, var)

    write_log()
    log(f"\nLog: {LOG_FILE}")
    log("\n[SCRIPT 1 COMPLETE]")


if __name__ == "__main__":
    main()
