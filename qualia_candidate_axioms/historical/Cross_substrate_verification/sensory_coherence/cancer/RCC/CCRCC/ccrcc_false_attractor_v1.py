"""
ccRCC False Attractor Analysis — Script 1 (Discovery Run)
OrganismCore — Cancer False Attractor Framework
Document 94 | 2026-03-02

BIOLOGICAL GROUNDING (locked before data contact):
    Cancer:         Clear Cell Renal Cell Carcinoma (ccRCC)
    Cell of origin: Proximal tubule epithelium — S3 segment
    Arrest point:   Proximal tubule maturation arrest
    Key driver:     VHL loss → constitutive HIF1A/EPAS1 activation
    Phenotype:      Clear cell (lipid/glycogen accumulation),
                    loss of proximal tubule metabolic identity,
                    retention of partial tubule markers

DATASETS:
    Primary:    TCGA-KIRC (Xena HiSeqV2) — 534T / 72N — RNA-seq log2 CPM
    Validation: GSE53757 (GEO GPL570) — 72T / 72N matched pairs
                Affymetrix HG-U133 Plus 2.0 microarray

GPL570 ANNOTATION:
    Script attempts automatic download from multiple URLs.
    If all fail, it looks for any of these files already present:
        ./ccrcc_false_attractor/GPL570_soft.txt
        ./ccrcc_false_attractor/GPL570_full_table.txt
        ./ccrcc_false_attractor/GPL570_soft.txt.gz
        ./ccrcc_false_attractor/GPL570_full_table.txt.gz
    If none found, TCGA arm runs and GEO arm is skipped with
    clear instructions. Re-run after placing the file.

    Manual download (run once in terminal):
        curl -L "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi
                 ?acc=GPL570&targ=self&form=text&view=full" \
             -o ./ccrcc_false_attractor/GPL570_soft.txt

REPRODUCIBILITY:
    Single script. No external dependencies beyond numpy/pandas/scipy/
    matplotlib. All downloads attempted automatically. Run once.

OUTPUTS (./ccrcc_false_attractor/results/):
    gene_matrix_tcga.csv
    metadata_tcga.csv
    saddle_point_tcga.csv
    depth_score_tcga.csv
    identity_switch_tcga.csv
    figure_s1_tcga.png
    gene_matrix_geo.csv          (GPL570 required)
    metadata_geo.csv             (GPL570 required)
    saddle_point_geo.csv         (GPL570 required)
    depth_score_geo.csv          (GPL570 required)
    identity_switch_geo.csv      (GPL570 required)
    figure_s1_geo.png            (GPL570 required)
    cross_dataset_comparison.csv (GPL570 required)
    s1_log.txt
"""

import os
import gzip
import urllib.request
import urllib.error

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
RESULTS_DIR = os.path.join(BASE_DIR, "results")
LOG_FILE    = os.path.join(RESULTS_DIR, "s1_log.txt")

os.makedirs(RESULTS_DIR, exist_ok=True)

# ═══════════════════════════════════════════════════════════════════════════════
# FILE PATHS
# ═══════════════════════════════════════════════════════════════════════════════

XENA_LOCAL = os.path.join(BASE_DIR, "TCGA_KIRC_HiSeqV2.gz")
GEO_LOCAL  = os.path.join(BASE_DIR, "GSE53757_series_matrix.txt.gz")

# GPL570 — all acceptable filenames, plain or gzipped
GPL570_CANDIDATES = [
    os.path.join(BASE_DIR, "GPL570_soft.txt"),
    os.path.join(BASE_DIR, "GPL570_full_table.txt"),
    os.path.join(BASE_DIR, "GPL570_soft.txt.gz"),
    os.path.join(BASE_DIR, "GPL570_full_table.txt.gz"),
]

# ═══════════════════════════════════════════════════════════════════════════════
# DOWNLOAD URLs
# ═══════════════════════════════════════════════════════════════════════════════

XENA_KIRC_URLS = [
    "https://tcga-xena-hub.s3.us-east-1.amazonaws.com/download/"
    "TCGA.KIRC.sampleMap%2FHiSeqV2.gz",
    "https://tcga.xenahubs.net/download/TCGA.KIRC.sampleMap/HiSeqV2.gz",
]

GEO_MATRIX_URLS = [
    "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE53nnn/GSE53757/"
    "matrix/GSE53757_series_matrix.txt.gz",
]

# GPL570 — multiple attempts before falling back to manual
GPL570_URLS = [
    # GEO SOFT full format — most reliable
    (
        "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi"
        "?acc=GPL570&targ=self&form=text&view=full",
        os.path.join(BASE_DIR, "GPL570_soft.txt"),
    ),
    # NCBI FTP annot (path varies by NCBI version)
    (
        "https://ftp.ncbi.nlm.nih.gov/geo/platforms/GPL570nnn/"
        "GPL570/annot/GPL570.annot.gz",
        os.path.join(BASE_DIR, "GPL570_full_table.txt.gz"),
    ),
    (
        "https://ftp.ncbi.nlm.nih.gov/geo/platforms/GPL570nnn/"
        "GPL570/GPL570.annot.gz",
        os.path.join(BASE_DIR, "GPL570_full_table.txt.gz"),
    ),
]

# ═══════════════════════════════════════════════════════════════════════════════
# GENE PANELS
# Derived exclusively from ccRCC proximal tubule S3 lineage biology.
# All panels locked before data contact.
# ═══════════════════════════════════════════════════════════════════════════════

# VHL-HIF axis — primary lock mechanism in ccRCC
# VHL loss → HIF1A/EPAS1 constitutive activation
VHL_HIF = [
    "VHL",   "HIF1A",  "EPAS1",  "ARNT",
    "CA9",   "VEGFA",  "SLC2A1", "LDHA",
    "PDK1",  "EGLN1",  "EGLN3",
]

# Proximal tubule S3 identity — expected LOST in tumour
PROXIMAL_TUBULE_IDENTITY = [
    "SLC34A1", "GATM",    "AGXT",    "PCK1",
    "AQP1",    "CUBN",    "LRP2",    "SLC3A1",
    "SLC7A9",  "SLC22A6", "UMOD",    "SLC13A3",
    "PRODH",
]

# Nephron progenitor — silent in normal adult kidney
# Re-emergence = dedifferentiation signal
NEPHRON_PROGENITOR = [
    "SIX2",   "PAX2",  "WT1",
    "CITED1", "SALL1", "OSR1",
]

# Proximal tubule maturation markers
PROXIMAL_MATURATION = [
    "LHX1",  "JAG1",  "DLL1",
    "HNF4A", "HNF1A", "PROM1",
]

# Epigenetic regulators — frequently mutated in ccRCC
# BAP1, PBRM1, SETD2 define distinct subtypes
EPIGENETIC_REGULATORS = [
    "BAP1",   "PBRM1",  "SETD2",
    "KDM5C",  "KDM6A",  "SMARCA4",
    "ARID1A",
]

# Metabolic reprogramming — clear cell phenotype
# Lipogenic arm: expected UP in false attractor (lipid synthesis)
METABOLIC_LIPOGENIC = [
    "FASN",  "ACACA", "SCD",
    "HMGCR", "ACLY",  "CPT1A",
]

# Gluconeogenic arm: expected DOWN — PT metabolic identity loss
METABOLIC_GLUCONEOGENIC = [
    "G6PC", "FBP1", "PCK2",
]

METABOLIC_REPROGRAMMING = METABOLIC_LIPOGENIC + METABOLIC_GLUCONEOGENIC

# mTOR pathway — major therapeutic axis in ccRCC
# Note: activation is predominantly post-translational;
# transcript-level signal may be modest
MTOR_PATHWAY = [
    "MTOR",    "RPTOR",    "RICTOR",
    "RPS6KB1", "EIF4EBP1", "AKT1",
    "PIK3CA",  "PTEN",
]

# Immune microenvironment
IMMUNE_MARKERS = [
    "PDCD1", "CD274", "CTLA4",
    "CD8A",  "FOXP3", "CD4",
    "CD68",  "TIGIT", "LAG3",
]

# Proliferation
PROLIFERATION = [
    "MKI67", "TOP2A", "PCNA",
    "CDK4",  "CCND1", "CCNE1",
    "CDK2",
]

# ── Role map ──────────────────────────────────────────────────────────────────

ROLE_MAP = {}
for _g in VHL_HIF:
    ROLE_MAP[_g] = "VHL_HIF"
for _g in PROXIMAL_TUBULE_IDENTITY:
    ROLE_MAP[_g] = "PT_IDENTITY"
for _g in NEPHRON_PROGENITOR:
    ROLE_MAP[_g] = "PROGENITOR"
for _g in PROXIMAL_MATURATION:
    ROLE_MAP[_g] = "PT_MATURATION"
for _g in EPIGENETIC_REGULATORS:
    ROLE_MAP[_g] = "EPIGENETIC"
for _g in METABOLIC_LIPOGENIC:
    ROLE_MAP[_g] = "METABOLIC_LIPOGENIC"
for _g in METABOLIC_GLUCONEOGENIC:
    ROLE_MAP[_g] = "METABOLIC_GLUCONEOGENIC"
for _g in MTOR_PATHWAY:
    ROLE_MAP[_g] = "MTOR"
for _g in IMMUNE_MARKERS:
    ROLE_MAP[_g] = "IMMUNE"
for _g in PROLIFERATION:
    ROLE_MAP[_g] = "PROLIFERATION"

ALL_TARGET = list(dict.fromkeys(
    VHL_HIF +
    PROXIMAL_TUBULE_IDENTITY +
    NEPHRON_PROGENITOR +
    PROXIMAL_MATURATION +
    EPIGENETIC_REGULATORS +
    METABOLIC_REPROGRAMMING +
    MTOR_PATHWAY +
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

# ═══════════════════════════════════════════════════════════════════════════════
# UTILITIES
# ═════════════════════════════════════════════════════════��═════════════════════

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

def fetch_url(url, dest, timeout=120):
    try:
        log(f"  Trying: {url}")
        def hook(count, block_size, total_size):
            if total_size > 0:
                pct = min(count * block_size * 100 // total_size, 100)
                print(f"\r  Progress: {pct}%", end="", flush=True)
        urllib.request.urlretrieve(url, dest, reporthook=hook)
        print()
        size_mb = os.path.getsize(dest) / (1024 * 1024)
        log(f"  Downloaded: {size_mb:.1f} MB → {dest}")
        return True
    except urllib.error.URLError as e:
        log(f"  FAILED: {e}")
        return False
    except Exception as e:
        log(f"  FAILED (unexpected): {e}")
        return False

def try_urls(url_list, dest):
    if os.path.exists(dest):
        size_mb = os.path.getsize(dest) / (1024 * 1024)
        log(f"  Already present ({size_mb:.1f} MB): {dest}")
        return True
    for url in url_list:
        if fetch_url(url, dest):
            return True
    return False

# ═════════════════════════════════════════���═════════════════════════════════════
# DOWNLOAD
# ═══════════════════════════════════════════════════════════════════════════════

def download_all():
    log("=" * 60)
    log("DOWNLOAD")
    log("=" * 60)

    # TCGA-KIRC — required
    xena_ok = try_urls(XENA_KIRC_URLS, XENA_LOCAL)
    if not xena_ok:
        log("CRITICAL: TCGA-KIRC download failed. Cannot proceed.")
        raise SystemExit(1)

    # GSE53757 — required
    geo_ok = try_urls(GEO_MATRIX_URLS, GEO_LOCAL)
    if not geo_ok:
        log("CRITICAL: GSE53757 download failed. Cannot proceed.")
        raise SystemExit(1)

    # GPL570 — attempt automatic download
    log("")
    log("  GPL570 annotation — checking...")

    # Check if already present under any acceptable name
    gpl570_path = _find_gpl570()
    if gpl570_path is not None:
        return gpl570_path

    # Attempt automatic download
    for url, dest in GPL570_URLS:
        if os.path.exists(dest):
            log(f"  Already present: {dest}")
            return dest
        if fetch_url(url, dest):
            log(f"  GPL570 downloaded ✓ → {dest}")
            return dest

    # All automatic attempts failed — instruct manual download
    log("")
    log("=" * 60)
    log("  GPL570 ANNOTATION — AUTOMATIC DOWNLOAD FAILED")
    log("  GSE53757 validation arm will be SKIPPED.")
    log("")
    log("  To enable validation arm, run once in terminal:")
    log('  curl -L "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi'
        '?acc=GPL570&targ=self&form=text&view=full" \\')
    log(f'       -o {os.path.join(BASE_DIR, "GPL570_soft.txt")}')
    log("  Then re-run this script.")
    log("=" * 60)
    return None

def _find_gpl570():
    """Return path to GPL570 file if any candidate exists."""
    for path in GPL570_CANDIDATES:
        if os.path.exists(path):
            size_mb = os.path.getsize(path) / (1024 * 1024)
            log(f"  GPL570 found ({size_mb:.1f} MB): {path}")
            return path
    return None

# ═══════════════════════════════════════════════════════════════════════════════
# GPL570 ANNOTATION PARSER
# ═══════════════════════════════════════════════════════════════════════════════

def load_gpl570_annotation(gpl570_path):
    """
    Load GPL570 probe → gene symbol mapping.

    Handles:
        - NCBI GEO SOFT format (lines starting with ^, !, #)
        - Plain tab-delimited full table
        - Gzipped versions of either

    Returns dict: probe_id (str) → gene_symbol (str, uppercase)
    Returns None if loading fails.
    """
    log("")
    log("=" * 60)
    log("GPL570 ANNOTATION — Loading")
    log("=" * 60)
    log(f"  File: {gpl570_path}")

    is_gz  = gpl570_path.endswith(".gz")
    opener = gzip.open if is_gz else open

    probe_map = {}
    header    = None
    id_col    = None
    sym_col   = None

    try:
        with opener(gpl570_path, "rt",
                    encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.rstrip("\n")

                # Skip SOFT metadata and comment lines
                if line.startswith(("^", "!", "#")):
                    continue

                parts = line.split("\t")

                # Detect header — must contain "ID" column
                if header is None:
                    lower = [p.strip().lower() for p in parts]
                    if "id" in lower:
                        header = parts
                        id_col = lower.index("id")
                        sym_col = None
                        # Gene symbol column — try common names
                        for candidate in [
                            "gene symbol",
                            "gene_symbol",
                            "genesymbol",
                            "symbol",
                            "gene assignment",
                            "gene_assignment",
                            "gene title",
                        ]:
                            for i, lp in enumerate(lower):
                                if candidate in lp:
                                    sym_col = i
                                    break
                            if sym_col is not None:
                                break
                        if sym_col is None:
                            sym_col = 1  # fallback: second column
                        log(f"  Header detected.")
                        log(f"  ID col:     {id_col} "
                            f"('{parts[id_col]}')")
                        log(f"  Symbol col: {sym_col} "
                            f"('{parts[sym_col]}')")
                    continue

                # Parse data rows
                if len(parts) <= max(id_col, sym_col):
                    continue

                probe_id = parts[id_col].strip()
                raw_sym  = parts[sym_col].strip()

                if not probe_id or not raw_sym:
                    continue

                # Take first symbol before " /// "
                sym = raw_sym.split("///")[0].strip().upper()

                # Skip empty / missing annotations
                if sym in ("", "---", "----", "N/A", "NA",
                           "NULL", "NONE"):
                    continue

                # Take first token (some fields have extra text)
                sym = sym.split()[0]

                probe_map[probe_id] = sym

        log(f"  Probes mapped: {len(probe_map)}")

        if not probe_map:
            log("  WARNING: No probes mapped. "
                "Check annotation file format.")
            return None

        # Spot check
        items = list(probe_map.items())[:4]
        for pid, gsym in items:
            log(f"    {pid} → {gsym}")
        log("  GPL570 annotation: LOADED ✓")
        return probe_map

    except Exception as e:
        log(f"  CRITICAL: Failed to load GPL570: {e}")
        return None

# ═══════════════════════════════════════════════════════════════════════════════
# TCGA-KIRC PARSER
# ═══════════════════════════════════════════════════════════════════════════════

def parse_tcga_kirc():
    """
    Parse TCGA-KIRC HiSeqV2.
    Format: gzipped TSV, first col = gene symbol,
            remaining cols = TCGA barcodes (log2 CPM).
    Tumour/normal from TCGA barcode sample type code
    (4th hyphen-delimited field, first 2 chars):
        01-09 = tumour
        10-19 = normal
    Returns:
        gene_df  — DataFrame (target genes x all samples)
        meta_df  — DataFrame (sample_id, sample_type)
    """
    log("")
    log("=" * 60)
    log("TCGA-KIRC — Parsing")
    log("=" * 60)

    with gzip.open(XENA_LOCAL, "rt") as f:
        gene_df = pd.read_csv(f, sep="\t", index_col=0)

    log(f"  Shape (genes x samples): {gene_df.shape}")

    sample_types = {}
    for s in gene_df.columns:
        parts = s.split("-")
        if len(parts) >= 4:
            code_str = parts[3][:2]
            if code_str.isdigit():
                code = int(code_str)
                if 1 <= code <= 9:
                    sample_types[s] = "tumour"
                elif 10 <= code <= 19:
                    sample_types[s] = "normal"
                else:
                    sample_types[s] = "other"
            else:
                sample_types[s] = "other"
        else:
            sample_types[s] = "other"

    meta_df = pd.DataFrame({
        "sample_id":   list(sample_types.keys()),
        "sample_type": list(sample_types.values()),
    })

    n_t = (meta_df.sample_type == "tumour").sum()
    n_n = (meta_df.sample_type == "normal").sum()
    log(f"  Tumour: {n_t}  Normal: {n_n}")

    available = [g for g in ALL_TARGET if g in gene_df.index]
    missing   = [g for g in ALL_TARGET if g not in gene_df.index]
    log(f"  Target genes available: {len(available)} / {len(ALL_TARGET)}")
    if missing:
        log(f"  Missing: {missing}")

    gene_df = gene_df.loc[available]

    gene_df.to_csv(os.path.join(RESULTS_DIR, "gene_matrix_tcga.csv"))
    meta_df.to_csv(os.path.join(RESULTS_DIR, "metadata_tcga.csv"),
                   index=False)
    log("  TCGA-KIRC parsed and saved ✓")
    return gene_df, meta_df

# ═══════════════════════════════════════════════════════════════════════════════
# GSE53757 PARSER
# ═══════════════════════════════════════════════════════════════════════════════

def parse_gse53757(probe_map):
    """
    Parse GSE53757 Affymetrix series matrix (GPL570).

    Classification uses exact source name strings confirmed
    in Phase 0 diagnostic:
        'Stage X ccRCC'              → tumour, stage X
        'normal match to Stage X...' → normal, matched

    Sample titles NNNT / NNNL / NNNN:
        suffix T or absence of N = tumour
        suffix N = normal
        numeric prefix = matched pair ID

    Probe → gene symbol via probe_map (GPL570 annotation).
    Multiple probes per gene: keep probe with highest mean
    expression across tumour samples (most informative).

    Values: log2 microarray intensity.
    Comparable to TCGA log2 CPM for FC direction analysis.

    Returns:
        gene_df  — DataFrame (target genes x samples)
        meta_df  — DataFrame (sample_id, sample_type, stage, pair_id)
    """
    log("")
    log("=" * 60)
    log("GSE53757 — Parsing")
    log("=" * 60)

    if probe_map is None:
        log("  probe_map is None. Skipping.")
        return None, None

    # ── Metadata pass ─────────────────────────────────────────
    sample_ids    = []
    source_names  = []
    sample_titles = []

    with gzip.open(GEO_LOCAL, "rt") as f:
        for line in f:
            line = line.rstrip()

            if line.startswith("!Sample_geo_accession"):
                parts = line.split("\t")
                ids = [
                    p.strip().strip('"') for p in parts[1:]
                    if p.strip().strip('"').startswith("GSM")
                ]
                sample_ids.extend(ids)

            elif line.startswith("!Sample_source_name_ch1"):
                parts = line.split("\t")
                names = [
                    p.strip().strip('"') for p in parts[1:]
                    if p.strip()
                ]
                source_names.extend(names)

            elif line.startswith("!Sample_title"):
                parts = line.split("\t")
                titles = [
                    p.strip().strip('"') for p in parts[1:]
                    if p.strip()
                ]
                sample_titles.extend(titles)

            elif line.startswith("!series_matrix_table_begin"):
                break

    log(f"  Sample IDs:    {len(sample_ids)}")
    log(f"  Source names:  {len(source_names)}")

    # Classify — exact strings from Phase 0 diagnostic
    sample_types_geo = []
    stages_geo       = []
    pair_ids_geo     = []

    for name in source_names:
        nl = name.lower()
        if "normal" in nl:
            sample_types_geo.append("normal")
            stages_geo.append("normal")
        elif "ccrcc" in nl or "stage" in nl:
            sample_types_geo.append("tumour")
            stage = "stage_unknown"
            for sn in ["1", "2", "3", "4"]:
                if f"stage {sn}" in nl:
                    stage = f"stage_{sn}"
                    break
            stages_geo.append(stage)
        else:
            sample_types_geo.append("unknown")
            stages_geo.append("unknown")

    # Extract matched pair ID from title (e.g. '102T' → '102')
    for title in sample_titles[:len(sample_types_geo)]:
        pair_id = title.rstrip("TtNnLl")
        pair_ids_geo.append(pair_id)

    n = min(len(sample_ids), len(sample_types_geo))
    meta_geo = pd.DataFrame({
        "sample_id":   sample_ids[:n],
        "title":       sample_titles[:n],
        "source":      source_names[:n],
        "sample_type": sample_types_geo[:n],
        "stage":       stages_geo[:n],
        "pair_id":     pair_ids_geo[:n],
    })

    n_t = (meta_geo.sample_type == "tumour").sum()
    n_n = (meta_geo.sample_type == "normal").sum()
    log(f"  Tumour: {n_t}  Normal: {n_n}")

    # ── Expression table pass ─────────────────────────────────
    log("  Parsing expression table...")

    col_header = None
    expr_rows  = []

    with gzip.open(GEO_LOCAL, "rt") as f:
        in_table = False
        for line in f:
            line = line.rstrip()
            if line.startswith("!series_matrix_table_begin"):
                in_table = True
                continue
            if line.startswith("!series_matrix_table_end"):
                break
            if in_table:
                if col_header is None:
                    col_header = line.split("\t")
                else:
                    expr_rows.append(line.split("\t"))

    if col_header is None or not expr_rows:
        log("  CRITICAL: Expression table not found.")
        return None, None

    probe_ids = [row[0].strip('"') for row in expr_rows]
    col_ids   = [c.strip('"') for c in col_header[1:]]

    values = []
    for row in expr_rows:
        vals = []
        for v in row[1:]:
            v = v.strip()
            try:
                vals.append(float(v))
            except ValueError:
                vals.append(np.nan)
        values.append(vals)

    n_cols = len(col_ids)
    values = [v[:n_cols] for v in values]

    probe_df = pd.DataFrame(
        values,
        index=probe_ids,
        columns=col_ids,
    )

    log(f"  Probes: {len(probe_ids)}  Columns: {len(col_ids)}")

    # ── Probe → gene mapping ──────────────────────────────────
    log("  Mapping probes to target genes...")

    tumour_ids  = meta_geo.loc[
        meta_geo.sample_type == "tumour", "sample_id"
    ].tolist()
    tumour_cols = [c for c in tumour_ids if c in probe_df.columns]

    target_probes = {}
    for probe_id in probe_df.index:
        sym = probe_map.get(probe_id)
        if sym and sym in ALL_TARGET:
            target_probes.setdefault(sym, []).append(probe_id)

    log(f"  Target genes with probes: {len(target_probes)}")

    gene_rows = {}
    for sym, probes in target_probes.items():
        if len(probes) == 1:
            gene_rows[sym] = probe_df.loc[probes[0]]
        else:
            best_probe = max(
                probes,
                key=lambda p: (
                    probe_df.loc[p, tumour_cols].mean()
                    if tumour_cols
                    else probe_df.loc[p].mean()
                )
            )
            gene_rows[sym] = probe_df.loc[best_probe]

    gene_df_geo = pd.DataFrame(gene_rows).T
    gene_df_geo.columns = col_ids[:gene_df_geo.shape[1]]

    log(f"  Gene matrix shape: {gene_df_geo.shape}")

    gene_df_geo.to_csv(
        os.path.join(RESULTS_DIR, "gene_matrix_geo.csv"))
    meta_geo.to_csv(
        os.path.join(RESULTS_DIR, "metadata_geo.csv"),
        index=False)
    log("  GSE53757 parsed and saved ✓")
    return gene_df_geo, meta_geo

# ═══════════════════════════════════════════════════════════════════════════════
# SAMPLE SPLITTER
# ═══════════════════════════════════════════════════════════════════════════════

def split_tumour_normal(gene_df, meta_df):
    t_ids = meta_df.loc[
        meta_df.sample_type == "tumour", "sample_id"].tolist()
    n_ids = meta_df.loc[
        meta_df.sample_type == "normal", "sample_id"].tolist()
    t_cols = [c for c in t_ids if c in gene_df.columns]
    n_cols = [c for c in n_ids if c in gene_df.columns]
    return gene_df[t_cols], gene_df[n_cols]

# ═══════════════════════════════════════════════════════════════════════════════
# SADDLE POINT ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════

def saddle_point_analysis(tumour, normal, label="TCGA"):
    """
    Per-gene:
        log2FC = tumour median − normal median (log2 space)
        Mann-Whitney U test (two-sided)
        Direction: UP / DOWN
    Ranked by |log2FC|.
    """
    log("")
    log("=" * 60)
    log(f"SADDLE POINT ANALYSIS — {label}")
    log("=" * 60)

    results = []
    for gene in ALL_TARGET:
        if gene not in tumour.index:
            continue
        t_vals = tumour.loc[gene].dropna()
        n_vals = normal.loc[gene].dropna()
        if len(t_vals) < 3 or len(n_vals) < 3:
            continue
        t_med = float(t_vals.median())
        n_med = float(n_vals.median())
        fc    = t_med - n_med
        _, p  = safe_mwu(t_vals, n_vals)
        results.append({
            "gene":      gene,
            "role":      ROLE_MAP.get(gene, "UNKNOWN"),
            "log2FC":    round(fc,    4),
            "t_median":  round(t_med, 4),
            "n_median":  round(n_med, 4),
            "direction": "UP" if fc > 0 else "DOWN",
            "p_mwu":     p,
            "p_fmt":     fmt_p(p),
        })

    df = pd.DataFrame(results)
    if df.empty:
        log("  WARNING: No results.")
        return df

    df = df.sort_values("log2FC", key=abs, ascending=False)
    df.to_csv(
        os.path.join(RESULTS_DIR,
                     f"saddle_point_{label.lower()}.csv"),
        index=False,
    )

    log(f"  Genes analysed: {len(df)}")
    log("")
    log(f"  {'Gene':<14} {'Role':<26} "
        f"{'log2FC':>8} {'Dir':>5}  {'p':>10}")
    log(f"  {'-'*14} {'-'*26} "
        f"{'-'*8} {'-'*5}  {'-'*10}")
    for _, row in df.head(25).iterrows():
        log(f"  {row.gene:<14} {row.role:<26} "
            f"{row.log2FC:>8.3f} {row.direction:>5}  "
            f"{row.p_fmt:>10}")

    # Prediction checks
    log("")
    log("  PREDICTION CHECK:")

    def check(panel, direction, label_str):
        sub   = df.loc[
            df.gene.isin(panel) & (df.direction == direction)]
        total = df.loc[df.gene.isin(panel)]
        log(f"  {label_str:<35} "
            f"{len(sub)}/{len(total)}  (predicted {direction})")

    check(PROXIMAL_TUBULE_IDENTITY, "DOWN", "PT identity DOWN")
    check(VHL_HIF,                  "UP",   "VHL-HIF UP")
    check(METABOLIC_LIPOGENIC,      "UP",   "Lipogenic UP")
    check(METABOLIC_GLUCONEOGENIC,  "DOWN", "Gluconeogenic DOWN")

    return df

# ════════════════════════════════════════════════════════════��══════════════════
# DEPTH SCORING
# ═══════════════════════════════════════════════════════════════════════════════

def depth_scoring(tumour, normal, label="TCGA"):
    """
    Composite false attractor depth score per tumour sample.

    Three components (each normalised 0-1 before combining):
        1. PT identity loss  — mean PT identity genes, inverted
           (low PT identity = high arrest depth)
        2. HIF activation    — mean HIF downstream targets
        3. Lipogenic reprog  — mean lipogenic arm genes

    Composite = mean of three normalised components.
    Range 0-1. Higher = more deeply arrested in false attractor.
    """
    log("")
    log("=" * 60)
    log(f"DEPTH SCORING — {label}")
    log("=" * 60)

    def norm01(s):
        mn, mx = s.min(), s.max()
        if mx == mn:
            return pd.Series(0.0, index=s.index)
        return (s - mn) / (mx - mn)

    hif_targets = [
        "CA9", "VEGFA", "SLC2A1", "LDHA", "PDK1", "EGLN3"
    ]
    lip_targets = [
        "FASN", "ACACA", "SCD", "HMGCR", "ACLY"
    ]

    pt_avail  = [g for g in PROXIMAL_TUBULE_IDENTITY
                 if g in tumour.index]
    hif_avail = [g for g in hif_targets if g in tumour.index]
    lip_avail = [g for g in lip_targets if g in tumour.index]

    idx = tumour.columns

    if pt_avail:
        pt_raw   = tumour.loc[pt_avail].mean(axis=0)
        pt_score = 1 - norm01(pt_raw)
    else:
        pt_score = pd.Series(0.0, index=idx)

    if hif_avail:
        hif_score = norm01(tumour.loc[hif_avail].mean(axis=0))
    else:
        hif_score = pd.Series(0.0, index=idx)

    if lip_avail:
        lip_score = norm01(tumour.loc[lip_avail].mean(axis=0))
    else:
        lip_score = pd.Series(0.0, index=idx)

    pt_score  = pt_score.reindex(idx).fillna(0)
    hif_score = hif_score.reindex(idx).fillna(0)
    lip_score = lip_score.reindex(idx).fillna(0)

    composite = (pt_score + hif_score + lip_score) / 3.0

    depth_df = pd.DataFrame({
        "sample_id":   idx,
        "pt_loss":     pt_score.values,
        "hif_act":     hif_score.values,
        "lip_reprog":  lip_score.values,
        "depth_score": composite.values,
    })

    depth_df.to_csv(
        os.path.join(RESULTS_DIR,
                     f"depth_score_{label.lower()}.csv"),
        index=False,
    )

    log(f"  PT identity genes:    {len(pt_avail)}")
    log(f"  HIF target genes:     {len(hif_avail)}")
    log(f"  Lipogenic genes:      {len(lip_avail)}")
    log(f"  Mean depth score:     {composite.mean():.3f}")
    log(f"  Range:                "
        f"{composite.min():.3f} — {composite.max():.3f}")

    if pt_avail:
        pt_n = [g for g in pt_avail if g in normal.index]
        if pt_n:
            log(f"  Normal PT mean:       "
                f"{normal.loc[pt_n].mean().mean():.3f}")
            log(f"  Tumour PT mean:       "
                f"{tumour.loc[pt_avail].mean().mean():.3f}")

    return depth_df

# ═══════════════════════════════════════════════════════════════════════════════
# IDENTITY SWITCH ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════

def identity_switch(tumour, normal, label="TCGA"):
    """
    Group-level mean expression: tumour vs normal.
    Reports Δ (tumour − normal) and MWU p-value per group.
    Identity switch score = HIF_delta − PT_delta
    Positive = switched from PT identity toward HIF lock.
    """
    log("")
    log("=" * 60)
    log(f"IDENTITY SWITCH ANALYSIS — {label}")
    log("=" * 60)

    groups = {
        "PT_identity":        PROXIMAL_TUBULE_IDENTITY,
        "HIF_targets":        [
            "CA9", "VEGFA", "SLC2A1",
            "LDHA", "PDK1", "EGLN3"
        ],
        "Progenitor":         NEPHRON_PROGENITOR,
        "PT_maturation":      PROXIMAL_MATURATION,
        "Epigenetic":         EPIGENETIC_REGULATORS,
        "Metabolic_lipogenic":METABOLIC_LIPOGENIC,
        "Metabolic_gluconeo": METABOLIC_GLUCONEOGENIC,
        "mTOR":               MTOR_PATHWAY,
        "Immune":             IMMUNE_MARKERS,
        "Proliferation":      PROLIFERATION,
    }

    rows = []
    log(f"  {'Group':<24} {'T_mean':>8} {'N_mean':>8} "
        f"{'Δ':>8}  {'p':>10}")
    log(f"  {'-'*24} {'-'*8} {'-'*8} "
        f"{'-'*8}  {'-'*10}")

    for gname, glist in groups.items():
        avail = [g for g in glist
                 if g in tumour.index and g in normal.index]
        if not avail:
            continue
        t_arr = tumour.loc[avail].values.flatten()
        n_arr = normal.loc[avail].values.flatten()
        t_arr = t_arr[~np.isnan(t_arr)]
        n_arr = n_arr[~np.isnan(n_arr)]
        t_mean = float(np.mean(t_arr))
        n_mean = float(np.mean(n_arr))
        delta  = t_mean - n_mean
        _, p   = safe_mwu(pd.Series(t_arr), pd.Series(n_arr))

        rows.append({
            "group":   gname,
            "t_mean":  round(t_mean, 4),
            "n_mean":  round(n_mean, 4),
            "delta":   round(delta,  4),
            "p_mwu":   p,
            "p_fmt":   fmt_p(p),
            "n_genes": len(avail),
        })
        log(f"  {gname:<24} {t_mean:>8.3f} {n_mean:>8.3f} "
            f"{delta:>8.3f}  {fmt_p(p):>10}")

    sw_df = pd.DataFrame(rows)
    sw_df.to_csv(
        os.path.join(RESULTS_DIR,
                     f"identity_switch_{label.lower()}.csv"),
        index=False,
    )

    hif_row = sw_df.loc[sw_df.group == "HIF_targets"]
    pt_row  = sw_df.loc[sw_df.group == "PT_identity"]
    if not hif_row.empty and not pt_row.empty:
        score = (hif_row.delta.values[0]
                 - pt_row.delta.values[0])
        log("")
        log(f"  Identity switch score: {score:.4f}")
        log("  Positive = PT→HIF switch confirmed ✓"
            if score > 0
            else "  Negative — review required")

    return sw_df

# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE
# ═══════════════════════════════════════════════════════════════════════════════

ROLE_COLORS = {
    "VHL_HIF":                "#e74c3c",
    "PT_IDENTITY":            "#2ecc71",
    "PROGENITOR":             "#9b59b6",
    "PT_MATURATION":          "#1abc9c",
    "EPIGENETIC":             "#f39c12",
    "METABOLIC_LIPOGENIC":    "#e67e22",
    "METABOLIC_GLUCONEOGENIC":"#d35400",
    "MTOR":                   "#3498db",
    "IMMUNE":                 "#95a5a6",
    "PROLIFERATION":          "#c0392b",
    "UNKNOWN":                "#bdc3c7",
}

def generate_figure(tumour, normal, saddle_df,
                    depth_df, switch_df, label="TCGA"):
    log("")
    log(f"Generating figure — {label}...")

    fig = plt.figure(figsize=(16, 12))
    gs  = gridspec.GridSpec(
        2, 2, figure=fig, hspace=0.45, wspace=0.35)
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[1, 0])
    ax_d = fig.add_subplot(gs[1, 1])

    # ── Panel A: Top 25 genes by |log2FC| ─────────────────────
    top = saddle_df.head(25).copy()
    ax_a.barh(
        top.gene[::-1],
        top.log2FC[::-1],
        color=[ROLE_COLORS.get(r, "#bdc3c7")
               for r in top.role[::-1]],
        edgecolor="black", linewidth=0.4,
    )
    ax_a.axvline(0, color="black",
                 linewidth=0.8, linestyle="--")
    ax_a.set_xlabel(
        "log2 Fold Change (Tumour / Normal)", fontsize=9)
    ax_a.set_title(
        f"A — Top 25 Genes |log2FC| ({label})", fontsize=10)
    ax_a.tick_params(axis="y", labelsize=7)

    # ── Panel B: Identity switch by group ─────────────────────
    if switch_df is not None and not switch_df.empty:
        grp_colors = []
        for g in switch_df.group:
            if "PT_identity" in g:
                grp_colors.append("#2ecc71")
            elif "HIF" in g:
                grp_colors.append("#e74c3c")
            elif "Progenitor" in g:
                grp_colors.append("#9b59b6")
            elif "lipogenic" in g.lower():
                grp_colors.append("#e67e22")
            elif "gluconeo" in g.lower():
                grp_colors.append("#d35400")
            elif "Immune" in g:
                grp_colors.append("#95a5a6")
            elif "Prolif" in g:
                grp_colors.append("#c0392b")
            else:
                grp_colors.append("#7f8c8d")

        ax_b.barh(
            switch_df.group[::-1],
            switch_df.delta[::-1],
            color=grp_colors[::-1],
            edgecolor="black", linewidth=0.4,
        )
        ax_b.axvline(0, color="black",
                     linewidth=0.8, linestyle="--")
        ax_b.set_xlabel(
            "Mean Δ Expression (Tumour − Normal)", fontsize=9)
        ax_b.set_title(
            "B — Identity Switch by Gene Group", fontsize=10)
        ax_b.tick_params(axis="y", labelsize=8)

    # ── Panel C: Depth score distribution ─────────────────────
    if depth_df is not None and not depth_df.empty:
        ax_c.hist(
            depth_df.depth_score, bins=30,
            color="#e74c3c", edgecolor="black",
            linewidth=0.4, alpha=0.8,
        )
        med = depth_df.depth_score.median()
        ax_c.axvline(
            med, color="black", linewidth=1.5,
            linestyle="--",
            label=f"Median = {med:.2f}",
        )
        ax_c.set_xlabel("Composite Depth Score", fontsize=9)
        ax_c.set_ylabel("Samples", fontsize=9)
        ax_c.set_title(
            "C — False Attractor Depth Distribution",
            fontsize=10)
        ax_c.legend(fontsize=8)

    # ── Panel D: PT loss vs HIF activation scatter ────────────
    if depth_df is not None and not depth_df.empty:
        sc = ax_d.scatter(
            depth_df.pt_loss,
            depth_df.hif_act,
            alpha=0.4, s=14,
            c=depth_df.depth_score,
            cmap="RdYlGn_r",
            edgecolors="none",
        )
        ax_d.set_xlabel("PT Identity Loss Score", fontsize=9)
        ax_d.set_ylabel("HIF Activation Score", fontsize=9)
        ax_d.set_title(
            "D — PT Loss vs HIF Activation (per sample)",
            fontsize=10)
        plt.colorbar(sc, ax=ax_d,
                     label="Depth Score", pad=0.01)

    fig.suptitle(
        f"ccRCC False Attractor — Script 1 Discovery ({label})\n"
        "Proximal Tubule S3 Maturation Arrest | VHL-HIF Lock",
        fontsize=12, fontweight="bold",
    )

    out = os.path.join(
        RESULTS_DIR, f"figure_s1_{label.lower()}.png")
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    log(f"  Figure saved: {out}")

# ═══════════════════════════════════════════════════════════════════════════════
# CROSS-DATASET COMPARISON
# ═══════════════════════════════════════════════════════════════════════════════

def cross_dataset_comparison(saddle_tcga, saddle_geo):
    log("")
    log("=" * 60)
    log("CROSS-DATASET COMPARISON")
    log("=" * 60)

    if saddle_geo is None or saddle_geo.empty:
        log("  GSE53757 arm not available. Skipping.")
        return

    merged = saddle_tcga.merge(
        saddle_geo[["gene", "log2FC", "direction"]],
        on="gene",
        suffixes=("_tcga", "_geo"),
    )

    if merged.empty:
        log("  No common genes found. Skipping.")
        return

    concordant = (
        merged.direction_tcga == merged.direction_geo
    ).sum()
    total = len(merged)
    pct   = 100 * concordant / total if total > 0 else 0.0

    r, p = safe_pearsonr(
        merged.log2FC_tcga.values,
        merged.log2FC_geo.values,
    )

    log(f"  Common genes:          {total}")
    log(f"  Direction concordant:  "
        f"{concordant}/{total} ({pct:.1f}%)")
    log(f"  log2FC correlation:    "
        f"r={r:.3f}  p={fmt_p(p)}")

    discordant = merged.loc[
        merged.direction_tcga != merged.direction_geo]
    if not discordant.empty:
        log(f"  Discordant genes ({len(discordant)}):")
        for _, row in discordant.iterrows():
            log(f"    {row.gene:<12} "
                f"TCGA:{row.direction_tcga}"
                f"({row.log2FC_tcga:+.2f})  "
                f"GEO:{row.direction_geo}"
                f"({row.log2FC_geo:+.2f})")

    merged.to_csv(
        os.path.join(RESULTS_DIR,
                     "cross_dataset_comparison.csv"),
        index=False,
    )

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    log("OrganismCore — ccRCC False Attractor Framework")
    log("Script 1 — Discovery Run")
    log("Document 94 | 2026-03-02")
    log("")
    log("BIOLOGICAL GROUNDING (locked):")
    log("  Cancer:         ccRCC")
    log("  Cell of origin: Proximal tubule S3")
    log("  Driver:         VHL loss → HIF1A/EPAS1 activation")
    log("  Arrest:         Proximal tubule maturation arrest")
    log("  Phenotype:      Clear cell, metabolic reprogramming,")
    log("                  loss of PT identity")
    log(f"  Target genes:   {len(ALL_TARGET)}")
    log("")

    # ── Downloads + GPL570 location ───────────────────────────
    gpl570_path = download_all()

    # ── GPL570 annotation ─────────────────────────────────────
    probe_map = None
    if gpl570_path is not None:
        probe_map = load_gpl570_annotation(gpl570_path)

    # ── TCGA arm ──────────────────────────────────────────────
    log("")
    log("═" * 60)
    log("PRIMARY ARM — TCGA-KIRC")
    log("═" * 60)

    gene_df_t, meta_t    = parse_tcga_kirc()
    tumour_t, normal_t   = split_tumour_normal(gene_df_t, meta_t)
    log(f"  Tumour: {tumour_t.shape}  Normal: {normal_t.shape}")

    saddle_t = saddle_point_analysis(tumour_t, normal_t, "TCGA")
    depth_t  = depth_scoring(tumour_t, normal_t, "TCGA")
    switch_t = identity_switch(tumour_t, normal_t, "TCGA")
    generate_figure(
        tumour_t, normal_t,
        saddle_t, depth_t, switch_t, "TCGA")

    # ── GEO arm ───────────────────────────────────────────────
    saddle_geo = None

    if probe_map is not None:
        log("")
        log("═" * 60)
        log("VALIDATION ARM — GSE53757")
        log("═" * 60)

        gene_df_geo, meta_geo = parse_gse53757(probe_map)

        if gene_df_geo is not None and meta_geo is not None:
            tumour_geo, normal_geo = split_tumour_normal(
                gene_df_geo, meta_geo)
            log(f"  Tumour: {tumour_geo.shape}  "
                f"Normal: {normal_geo.shape}")

            saddle_geo = saddle_point_analysis(
                tumour_geo, normal_geo, "GEO")
            depth_geo  = depth_scoring(
                tumour_geo, normal_geo, "GEO")
            switch_geo = identity_switch(
                tumour_geo, normal_geo, "GEO")
            generate_figure(
                tumour_geo, normal_geo,
                saddle_geo, depth_geo, switch_geo, "GEO")
    else:
        log("")
        log("GSE53757 arm SKIPPED — GPL570 annotation not found.")
        log("Run once in terminal to enable:")
        log('  curl -L "https://www.ncbi.nlm.nih.gov/geo/query/'
            'acc.cgi?acc=GPL570&targ=self&form=text&view=full" \\')
        log(f'       -o '
            f'{os.path.join(BASE_DIR, "GPL570_soft.txt")}')
        log("Then re-run this script.")

    # ── Cross-dataset ─────────────────────────────────────────
    cross_dataset_comparison(saddle_t, saddle_geo)

    # ── Summary ───────────────────────────────────────────────
    log("")
    log("=" * 60)
    log("SCRIPT 1 COMPLETE")
    log("=" * 60)
    log(f"  Outputs: {RESULTS_DIR}")
    for fname in sorted(os.listdir(RESULTS_DIR)):
        fpath = os.path.join(RESULTS_DIR, fname)
        log(f"    {fname:<50} "
            f"{os.path.getsize(fpath):>8} bytes")
    log("")
    log("  NEXT STEP:")
    log("  Read saddle_point_tcga.csv against locked predictions.")
    log("  Record confirmations, contradictions, surprises.")
    log("  Then proceed to Script 2.")

    write_log()


if __name__ == "__main__":
    main()
