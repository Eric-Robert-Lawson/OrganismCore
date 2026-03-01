"""
ESCA DATASET DISCOVERY SCRIPT
Purpose: Inspect available datasets before
         committing to any analysis.
         Read metadata, check sample counts,
         confirm subtype labels, check gene
         coverage, confirm format.

Checks:
  1. GSE53625 — what is actually in the file
  2. GEO search for ESCA datasets with
     both ESCC and EAC labeled
  3. Dataset comparison table
  4. Recommended dataset decision

Doc: 90_discovery | Date: 2026-03-01
Author: Eric Robert Lawson | OrganismCore
"""

import os
import re
import gzip
import requests
import numpy as np
import pandas as pd

BASE_DIR = "./esca_discovery/"
os.makedirs(BASE_DIR, exist_ok=True)

# ============================================================
# UTILITY
# ============================================================

def log(msg=""):
    print(msg)

def download(url, dest, timeout=180):
    if os.path.exists(dest):
        log(f"  Already present: {dest} "
            f"({os.path.getsize(dest):,} bytes)")
        return True
    log(f"  Downloading: {url}")
    try:
        r = requests.get(url, timeout=timeout)
        if r.status_code == 200:
            with open(dest, "wb") as f:
                f.write(r.content)
            log(f"  Saved: {dest} "
                f"({os.path.getsize(dest):,} bytes)")
            return True
        log(f"  HTTP {r.status_code}")
        return False
    except Exception as e:
        log(f"  Error: {e}")
        return False

# ============================================================
# PART 1: INSPECT GSE53625 RAW FILE STRUCTURE
# Find out exactly what is in the file
# before trying to parse it
# ============================================================

def inspect_series_matrix(filepath, n_lines=120):
    log("=" * 65)
    log(f"INSPECTING: {filepath}")
    log(f"First {n_lines} lines raw:")
    log("=" * 65)

    opener = (
        gzip.open(filepath, "rt",
                  encoding="utf-8",
                  errors="ignore")
        if filepath.endswith(".gz")
        else open(filepath, "r",
                  encoding="utf-8",
                  errors="ignore")
    )

    line_types   = {}
    sample_lines = []
    data_start   = None
    data_end     = None
    header_line  = None
    probe_examples = []

    with opener as f:
        for i, line in enumerate(f):
            line = line.rstrip("\n").rstrip("\r")

            # Categorize
            if line.startswith("!"):
                key = line.split("\t")[0]
                line_types[key] = (
                    line_types.get(key, 0) + 1
                )

            if i < n_lines:
                # Print first n lines
                preview = line[:120]
                log(f"  L{i+1:04d}: {preview}")

            # Track key markers
            if "!Sample_geo_accession" in line:
                parts = line.split("\t")
                sample_lines = [
                    p.strip().strip('"')
                    for p in parts[1:]
                    if p.strip()
                ]

            if "series_matrix_table_begin" in line:
                data_start = i

            if "series_matrix_table_end" in line:
                data_end = i

            # First few data rows after header
            if (data_start is not None
                    and data_end is None
                    and i > data_start
                    and i <= data_start + 5):
                probe_examples.append(
                    line[:100]
                )

    log("")
    log("=" * 65)
    log("STRUCTURE SUMMARY:")
    log("=" * 65)
    log(f"  Total line types found:")
    for k, v in sorted(line_types.items()):
        log(f"    {k[:50]}: {v} lines")
    log(f"\n  Sample IDs found: {len(sample_lines)}")
    log(f"  Sample examples: "
        f"{sample_lines[:5]}")
    log(f"\n  Data table start: line {data_start}")
    log(f"  Data table end  : line {data_end}")
    log(f"\n  Probe/header examples after "
        f"table_begin:")
    for ex in probe_examples:
        log(f"    {ex}")

    return {
        "n_samples":   len(sample_lines),
        "sample_ids":  sample_lines,
        "data_start":  data_start,
        "data_end":    data_end,
        "line_types":  line_types,
    }

# ============================================================
# PART 2: FULL METADATA EXTRACTION
# Extract ALL metadata fields from
# the series matrix header
# ============================================================

def extract_metadata(filepath):
    log("")
    log("=" * 65)
    log("EXTRACTING ALL METADATA FIELDS")
    log("=" * 65)

    opener = (
        gzip.open(filepath, "rt",
                  encoding="utf-8",
                  errors="ignore")
        if filepath.endswith(".gz")
        else open(filepath, "r",
                  encoding="utf-8",
                  errors="ignore")
    )

    meta_fields = {}

    with opener as f:
        for line in f:
            line = line.rstrip()
            if line.startswith(
                "!series_matrix_table_begin"
            ):
                break
            if not line.startswith("!"):
                continue

            parts = line.split("\t")
            key   = parts[0].strip()
            vals  = [
                p.strip().strip('"')
                for p in parts[1:]
            ]

            if key not in meta_fields:
                meta_fields[key] = []
            meta_fields[key].extend(vals)

    log(f"\n  All metadata keys found:")
    for k in sorted(meta_fields.keys()):
        vals = meta_fields[k]
        # Show unique values (up to 5)
        uniq = list(dict.fromkeys(vals))[:5]
        log(f"\n  [{k}]")
        log(f"    count : {len(vals)}")
        log(f"    unique: {uniq}")

    return meta_fields

# ============================================================
# PART 3: PARSE DATA TABLE CORRECTLY
# Now that we know the structure,
# parse it properly
# ============================================================

def parse_data_correctly(filepath, max_probes=None):
    """
    Reads the series matrix data table.
    Returns (header_cols, probe_ids, data_array)
    """
    log("")
    log("=" * 65)
    log("PARSING DATA TABLE")
    log("=" * 65)

    opener = (
        gzip.open(filepath, "rt",
                  encoding="utf-8",
                  errors="ignore")
        if filepath.endswith(".gz")
        else open(filepath, "r",
                  encoding="utf-8",
                  errors="ignore")
    )

    in_table    = False
    header_cols = []
    probe_ids   = []
    rows        = []

    with opener as f:
        for line in f:
            line = line.rstrip("\n").rstrip("\r")

            if "series_matrix_table_begin" in line:
                in_table = True
                continue

            if "series_matrix_table_end" in line:
                break

            if not in_table:
                continue

            # Split — handle quoted fields
            parts = line.split("\t")
            parts = [p.strip().strip('"')
                     for p in parts]

            if not header_cols:
                # First row in table = header
                header_cols = parts
                log(f"  Header: {parts[:6]}...")
                log(f"  Columns: {len(parts)}")
                continue

            # Data row
            if not parts or not parts[0]:
                continue

            probe_id = parts[0]

            try:
                vals = [
                    float(p)
                    if p not in [
                        "", "null", "NA",
                        "nan", "N/A",
                    ] else np.nan
                    for p in parts[1:]
                ]
            except ValueError as e:
                # Show first error then skip
                if len(rows) == 0:
                    log(f"  Parse error: {e}")
                    log(f"  Row: {parts[:5]}")
                continue

            if len(vals) != len(header_cols) - 1:
                continue

            probe_ids.append(probe_id)
            rows.append(vals)

            if (max_probes is not None
                    and len(probe_ids) >= max_probes):
                break

    log(f"  Probes parsed : {len(probe_ids)}")
    log(f"  Columns       : "
        f"{len(header_cols) - 1}")

    if probe_ids:
        log(f"  Probe examples: {probe_ids[:8]}")
        log(f"  Probe format  : "
            f"{probe_ids[0]}")

    return header_cols[1:], probe_ids, rows

# ============================================================
# PART 4: CHECK PROBE FORMAT
# Identify GPL platform and whether
# gene symbols are embedded in probe IDs
# ============================================================

def check_probe_format(probe_ids):
    log("")
    log("=" * 65)
    log("PROBE FORMAT ANALYSIS")
    log("=" * 65)

    if not probe_ids:
        log("  No probes to analyze")
        return

    log(f"  Total probes: {len(probe_ids)}")
    log(f"  First 20 probes:")
    for p in probe_ids[:20]:
        log(f"    {p}")

    # Identify format
    agilent_pattern = re.compile(
        r"^A_\d+_P\d+"
    )
    numeric_pattern = re.compile(
        r"^\d+$"
    )
    affymetrix_pattern = re.compile(
        r"^\d+_[as]_at$"
    )
    ensg_pattern = re.compile(
        r"^ENSG\d+"
    )

    formats = {
        "agilent_A_XX_PXXXXXX": 0,
        "numeric_only": 0,
        "affymetrix_XXXXXX_at": 0,
        "ensembl_ENSG": 0,
        "gene_symbol_like": 0,
        "other": 0,
    }

    for p in probe_ids[:1000]:
        if agilent_pattern.match(p):
            formats["agilent_A_XX_PXXXXXX"] += 1
        elif numeric_pattern.match(p):
            formats["numeric_only"] += 1
        elif affymetrix_pattern.match(p):
            formats["affymetrix_XXXXXX_at"] += 1
        elif ensg_pattern.match(p):
            formats["ensembl_ENSG"] += 1
        elif re.match(r"^[A-Z][A-Z0-9\-]+$", p):
            formats["gene_symbol_like"] += 1
        else:
            formats["other"] += 1

    log(f"\n  Probe format distribution "
        f"(first 1000):")
    for fmt, count in formats.items():
        if count > 0:
            log(f"    {fmt}: {count}")

    # Determine annotation strategy
    log(f"\n  Annotation strategy:")
    if formats["gene_symbol_like"] > 100:
        log(f"  → Probe IDs ARE gene symbols")
        log(f"  → No annotation needed")
        log(f"  → Direct gene name mapping")
    elif formats["agilent_A_XX_PXXXXXX"] > 100:
        log(f"  → Agilent probe format")
        log(f"  → Need GPL annotation file")
        log(f"  → Or use GEO soft file")
    elif formats["numeric_only"] > 100:
        log(f"  → Numeric probe IDs")
        log(f"  → Need platform annotation")
    elif formats["affymetrix_XXXXXX_at"] > 100:
        log(f"  → Affymetrix probe format")
        log(f"  → Use probe-to-symbol map")
    else:
        log(f"  → Unknown format")
        log(f"  → Inspect first 5 probes above")

# ============================================================
# PART 5: CHECK GPL ANNOTATION AVAILABILITY
# ============================================================

def check_gpl_annotation(meta_fields):
    log("")
    log("=" * 65)
    log("GPL PLATFORM ANNOTATION CHECK")
    log("=" * 65)

    # Find GPL ID from metadata
    gpl_id = None
    for key, vals in meta_fields.items():
        if "platform_id" in key.lower():
            for v in vals:
                if v.startswith("GPL"):
                    gpl_id = v
                    break

    if not gpl_id:
        # Try series platform
        for key, vals in meta_fields.items():
            if "platform" in key.lower():
                log(f"  [{key}]: {vals[:3]}")

    log(f"\n  GPL ID: {gpl_id}")

    if gpl_id:
        # Check if annotation is downloadable
        gpl_num = gpl_id.replace("GPL", "")
        prefix  = gpl_id[:6] + "nnn"
        annot_url = (
            f"https://ftp.ncbi.nlm.nih.gov/"
            f"geo/platforms/{prefix}/"
            f"{gpl_id}/soft/"
            f"{gpl_id}.annot.gz"
        )
        soft_url = (
            f"https://ftp.ncbi.nlm.nih.gov/"
            f"geo/platforms/{prefix}/"
            f"{gpl_id}/soft/"
            f"{gpl_id}_family.soft.gz"
        )

        log(f"  Annotation URL candidates:")
        log(f"    {annot_url}")
        log(f"    {soft_url}")

        # Try HEAD request to check availability
        for url in [annot_url, soft_url]:
            try:
                r = requests.head(
                    url, timeout=15
                )
                log(f"  HEAD {url[-50:]}: "
                    f"HTTP {r.status_code} "
                    f"({r.headers.get('Content-Length', 'unknown')} bytes)")
            except Exception as e:
                log(f"  HEAD failed: {e}")

    return gpl_id

# ============================================================
# PART 6: SURVEY OTHER ESCA DATASETS
# Check what else is available on GEO
# ============================================================

CANDIDATE_DATASETS = {
    "GSE53625": {
        "desc": "ESCC 179T+179N Korean "
                "Agilent lncRNA+mRNA",
        "url_matrix": (
            "https://ftp.ncbi.nlm.nih.gov/"
            "geo/series/GSE53nnn/GSE53625/"
            "matrix/GSE53625_series_matrix"
            ".txt.gz"
        ),
        "url_soft": (
            "https://ftp.ncbi.nlm.nih.gov/"
            "geo/series/GSE53nnn/GSE53625/"
            "soft/GSE53625_family.soft.gz"
        ),
        "subtype": "ESCC only",
        "n_total": 358,
        "has_normal": True,
        "has_survival": False,
        "platform": "Agilent",
    },
    "GSE26886": {
        "desc": "Mixed ESCC+EAC+Normal "
                "Affymetrix HG-U133Plus2",
        "url_matrix": (
            "https://ftp.ncbi.nlm.nih.gov/"
            "geo/series/GSE26nnn/GSE26886/"
            "matrix/GSE26886_series_matrix"
            ".txt.gz"
        ),
        "subtype": "ESCC + EAC + normal",
        "n_total": 166,
        "has_normal": True,
        "has_survival": False,
        "platform": "Affymetrix",
    },
    "GSE23400": {
        "desc": "ESCC 53T+53N Chinese "
                "Affymetrix HG-U133A",
        "url_matrix": (
            "https://ftp.ncbi.nlm.nih.gov/"
            "geo/series/GSE23nnn/GSE23400/"
            "matrix/GSE23400_series_matrix"
            ".txt.gz"
        ),
        "subtype": "ESCC only",
        "n_total": 106,
        "has_normal": True,
        "has_survival": True,
        "platform": "Affymetrix",
    },
    "GSE75241": {
        "desc": "EAC 90 samples "
                "Affymetrix",
        "url_matrix": (
            "https://ftp.ncbi.nlm.nih.gov/"
            "geo/series/GSE75nnn/GSE75241/"
            "matrix/GSE75241_series_matrix"
            ".txt.gz"
        ),
        "subtype": "EAC only",
        "n_total": 90,
        "has_normal": False,
        "has_survival": True,
        "platform": "Affymetrix",
    },
    "GSE13898": {
        "desc": "EAC+Barrett+Normal "
                "Affymetrix",
        "url_matrix": (
            "https://ftp.ncbi.nlm.nih.gov/"
            "geo/series/GSE13nnn/GSE13898/"
            "matrix/GSE13898_series_matrix"
            ".txt.gz"
        ),
        "subtype": "EAC + Barrett + Normal",
        "n_total": 149,
        "has_normal": True,
        "has_survival": False,
        "platform": "Affymetrix",
    },
    "GSE72094": {
        "desc": "ESCC 119T+39N Chinese "
                "Affymetrix HG-U133Plus2",
        "url_matrix": (
            "https://ftp.ncbi.nlm.nih.gov/"
            "geo/series/GSE72nnn/GSE72094/"
            "matrix/GSE72094_series_matrix"
            ".txt.gz"
        ),
        "subtype": "ESCC only",
        "n_total": 158,
        "has_normal": True,
        "has_survival": True,
        "platform": "Affymetrix",
    },
    "GSE29001": {
        "desc": "ESCC Chinese with survival "
                "Affymetrix HG-U133Plus2",
        "url_matrix": (
            "https://ftp.ncbi.nlm.nih.gov/"
            "geo/series/GSE29nnn/GSE29001/"
            "matrix/GSE29001_series_matrix"
            ".txt.gz"
        ),
        "subtype": "ESCC only",
        "n_total": 60,
        "has_normal": False,
        "has_survival": True,
        "platform": "Affymetrix",
    },
}

def survey_datasets():
    log("")
    log("=" * 65)
    log("CANDIDATE DATASET SURVEY")
    log("=" * 65)

    results = {}

    for acc, info in CANDIDATE_DATASETS.items():
        log(f"\n  --- {acc} ---")
        log(f"  {info['desc']}")
        log(f"  Subtype    : {info['subtype']}")
        log(f"  N total    : {info['n_total']}")
        log(f"  Has normal : {info['has_normal']}")
        log(f"  Has survival: "
            f"{info['has_survival']}")
        log(f"  Platform   : {info['platform']}")

        # Check if matrix URL is reachable
        url = info["url_matrix"]
        try:
            r = requests.head(url, timeout=15)
            size = r.headers.get(
                "Content-Length", "unknown"
            )
            status = r.status_code
            log(f"  Matrix URL : "
                f"HTTP {status} "
                f"({size} bytes)")
            results[acc] = {
                **info,
                "http_status": status,
                "file_size":   size,
                "reachable":   status == 200,
            }
        except Exception as e:
            log(f"  Matrix URL : UNREACHABLE "
                f"({e})")
            results[acc] = {
                **info,
                "http_status": None,
                "reachable":   False,
            }

    return results

# ============================================================
# PART 7: QUICK PEEK AT A SMALL DATASET
# Download first 200 lines of a small
# series matrix to check format and
# sample labels without committing
# to a full download
# ============================================================

def peek_dataset(acc, url, n_bytes=50000):
    log("")
    log(f"  PEEKING: {acc}")
    dest = os.path.join(
        BASE_DIR, f"{acc}_peek.txt.gz"
    )

    if os.path.exists(dest):
        log(f"  Already peeked: {dest}")
    else:
        try:
            headers = {
                "Range": f"bytes=0-{n_bytes}"
            }
            r = requests.get(
                url, headers=headers, timeout=30
            )
            with open(dest, "wb") as f:
                f.write(r.content)
            log(f"  Saved {len(r.content):,} bytes")
        except Exception as e:
            log(f"  Peek failed: {e}")
            return

    # Try to read the peek
    try:
        with gzip.open(
            dest, "rt",
            encoding="utf-8",
            errors="ignore",
        ) as f:
            lines = []
            for i, line in enumerate(f):
                lines.append(
                    line.rstrip()[:120]
                )
                if i >= 80:
                    break

        log(f"  First 30 readable lines:")
        for line in lines[:30]:
            log(f"    {line}")

    except Exception as e:
        log(f"  Could not read peek: {e}")
        log(f"  (Partial gz may not be readable)")
        log(f"  Download full file to inspect")

# ============================================================
# PART 8: DECISION TABLE
# ============================================================

def print_decision_table(survey_results):
    log("")
    log("=" * 65)
    log("DATASET DECISION TABLE")
    log("=" * 65)

    log(f"\n  {'ACC':<12} {'Subtype':<22} "
        f"{'N':>6} {'Norm':>5} "
        f"{'Surv':>5} {'Plat':<14} "
        f"{'OK':>4}")
    log(f"  {'-'*80}")

    for acc, info in survey_results.items():
        ok = "✓" if info.get("reachable") else "✗"
        log(f"  {acc:<12} "
            f"{info['subtype'][:21]:<22} "
            f"{info['n_total']:>6} "
            f"{'Y' if info['has_normal'] else 'N':>5} "
            f"{'Y' if info['has_survival'] else 'N':>5} "
            f"{info['platform']:<14} "
            f"{ok:>4}")

    log("")
    log("  SELECTION CRITERIA:")
    log("  1. Has matched normal tissue")
    log("  2. Has survival data")
    log("  3. Affymetrix platform preferred")
    log("     (Agilent requires extra")
    log("      annotation step)")
    log("  4. Large n preferred (>100 tumors)")
    log("  5. Contains both subtypes if")
    log("     cross-subtype test planned")
    log("")
    log("  BEST CANDIDATES:")
    log("  ESCC only + survival:")
    log("    GSE23400 — 53T+53N + survival")
    log("    GSE72094 — 119T+39N + survival")
    log("  Both subtypes:")
    log("    GSE26886 — ESCC+EAC+Normal")
    log("  EAC + progression:")
    log("    GSE13898 — EAC+Barrett+Normal")

# ============================================================
# MAIN
# ============================================================

def main():
    log("=" * 65)
    log("ESCA DATASET DISCOVERY")
    log("Doc: 90_discovery | 2026-03-01")
    log("Framework: OrganismCore")
    log("=" * 65)
    log("")
    log("PURPOSE:")
    log("  Inspect available datasets")
    log("  before committing to analysis.")
    log("  Check format, metadata,")
    log("  sample labels, gene coverage.")

    # --------------------------------------------------------
    # Part 1: Inspect GSE53625 raw structure
    # --------------------------------------------------------
    log("")
    log("=" * 65)
    log("PART 1: INSPECT GSE53625 RAW STRUCTURE")
    log("=" * 65)

    gse53625_file = os.path.join(
        BASE_DIR, "..",
        "esca_false_attractor",
        "GSE53625_series_matrix.txt.gz",
    )
    # Normalize path
    gse53625_file = os.path.normpath(
        gse53625_file
    )

    if os.path.exists(gse53625_file):
        log(f"  Found: {gse53625_file}")
        struct = inspect_series_matrix(
            gse53625_file, n_lines=80
        )
    else:
        log(f"  GSE53625 not found at:")
        log(f"  {gse53625_file}")
        log(f"  Skipping inspection")
        struct = {}

    # --------------------------------------------------------
    # Part 2: Extract full metadata from GSE53625
    # --------------------------------------------------------
    if os.path.exists(gse53625_file):
        log("")
        log("=" * 65)
        log("PART 2: FULL METADATA — GSE53625")
        log("=" * 65)
        meta_fields = extract_metadata(
            gse53625_file
        )

        # --------------------------------------------------------
        # Part 3: Try correct data parse
        # --------------------------------------------------------
        log("")
        log("=" * 65)
        log("PART 3: DATA TABLE PARSE ATTEMPT")
        log("First 200 probes only")
        log("=" * 65)
        cols, probes, rows = parse_data_correctly(
            gse53625_file, max_probes=200
        )

        # --------------------------------------------------------
        # Part 4: Check probe format
        # --------------------------------------------------------
        check_probe_format(probes)

        # --------------------------------------------------------
        # Part 5: Check GPL annotation
        # --------------------------------------------------------
        check_gpl_annotation(meta_fields)

    # --------------------------------------------------------
    # Part 6: Survey all candidate datasets
    # --------------------------------------------------------
    log("")
    log("=" * 65)
    log("PART 6: CANDIDATE DATASET SURVEY")
    log("Checking availability of all candidates")
    log("=" * 65)
    survey_results = survey_datasets()

    # --------------------------------------------------------
    # Part 7: Peek at top candidates
    # --------------------------------------------------------
    log("")
    log("=" * 65)
    log("PART 7: PEEK AT TOP CANDIDATES")
    log("=" * 65)

    peek_targets = {
        "GSE26886": (
            "https://ftp.ncbi.nlm.nih.gov/"
            "geo/series/GSE26nnn/GSE26886/"
            "matrix/GSE26886_series_matrix"
            ".txt.gz"
        ),
        "GSE23400": (
            "https://ftp.ncbi.nlm.nih.gov/"
            "geo/series/GSE23nnn/GSE23400/"
            "matrix/GSE23400_series_matrix"
            ".txt.gz"
        ),
        "GSE72094": (
            "https://ftp.ncbi.nlm.nih.gov/"
            "geo/series/GSE72nnn/GSE72094/"
            "matrix/GSE72094_series_matrix"
            ".txt.gz"
        ),
        "GSE13898": (
            "https://ftp.ncbi.nlm.nih.gov/"
            "geo/series/GSE13nnn/GSE13898/"
            "matrix/GSE13898_series_matrix"
            ".txt.gz"
        ),
    }

    for acc, url in peek_targets.items():
        if survey_results.get(acc, {}).get(
            "reachable"
        ):
            peek_dataset(acc, url)
        else:
            log(f"\n  {acc}: not reachable — skip")

    # --------------------------------------------------------
    # Part 8: Decision table
    # --------------------------------------------------------
    print_decision_table(survey_results)

    log("")
    log("=" * 65)
    log("DISCOVERY COMPLETE")
    log("=" * 65)
    log("")
    log("NEXT STEP:")
    log("  Read the output above.")
    log("  Confirm which datasets are")
    log("  reachable and correctly formatted.")
    log("  Confirm subtype labels are present.")
    log("  Then select the dataset and")
    log("  write the analysis script.")


if __name__ == "__main__":
    main()
