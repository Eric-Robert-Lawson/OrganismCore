"""
ESOPHAGEAL CANCER — FALSE ATTRACTOR ANALYSIS
SCRIPT 3 — VALIDATION COHORT (v3)
Dataset: GSE13898
Platform: GPL6102 Illumina HumanWG-6 V2
Doc: 90d | Date: 2026-03-01

FIXES vs v2:
  FIX 1: GPL annotation — use col index 2
          ('Gene symbol') not col 5
          ('UniGene symbol').
  FIX 2: Survival — fetch from GEO
          supplementary files.
          GSE13898 suppl contains
          patient clinical data.
  FIX 3: AURKA — scan GPL for actual
          probe ID after correct mapping.

Author: Eric Robert Lawson
Framework: OrganismCore
"""

import os
import re
import gzip
import requests
import numpy as np
import pandas as pd
from scipy import stats
from lifelines import KaplanMeierFitter
from lifelines.statistics import logrank_test
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import warnings
warnings.filterwarnings("ignore")

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR    = "./esca_false_attractor/"
RESULTS_DIR = os.path.join(
    BASE_DIR, "results_s3"
)
LOG_FILE = os.path.join(
    RESULTS_DIR, "analysis_log_s3.txt"
)
os.makedirs(RESULTS_DIR, exist_ok=True)

MATRIX_URL  = (
    "https://ftp.ncbi.nlm.nih.gov/geo/series/"
    "GSE13nnn/GSE13898/matrix/"
    "GSE13898_series_matrix.txt.gz"
)
MATRIX_FILE = os.path.join(
    BASE_DIR, "GSE13898_series_matrix.txt.gz"
)
GPL_URL  = (
    "https://ftp.ncbi.nlm.nih.gov/geo/platforms/"
    "GPL6nnn/GPL6102/annot/"
    "GPL6102.annot.gz"
)
GPL_FILE = os.path.join(
    BASE_DIR, "GPL6102.annot.gz"
)
SOFT_URL  = (
    "https://ftp.ncbi.nlm.nih.gov/geo/series/"
    "GSE13nnn/GSE13898/soft/"
    "GSE13898_family.soft.gz"
)
SOFT_FILE = os.path.join(
    BASE_DIR, "GSE13898_family.soft.gz"
)

# Supplementary file — clinical data
# GSE13898 stores survival here
SUPPL_URLS = [
    (
        "https://ftp.ncbi.nlm.nih.gov/geo/series/"
        "GSE13nnn/GSE13898/suppl/"
        "GSE13898_clinical_data.txt.gz",
        os.path.join(
            BASE_DIR,
            "GSE13898_clinical_data.txt.gz",
        ),
    ),
    (
        "https://ftp.ncbi.nlm.nih.gov/geo/series/"
        "GSE13nnn/GSE13898/suppl/"
        "GSE13898_clinical_data.txt",
        os.path.join(
            BASE_DIR,
            "GSE13898_clinical_data.txt",
        ),
    ),
    (
        "https://ftp.ncbi.nlm.nih.gov/geo/series/"
        "GSE13nnn/GSE13898/suppl/"
        "GSE13898%5Fclinical%5Fdata.txt.gz",
        os.path.join(
            BASE_DIR,
            "GSE13898_clinical_data2.txt.gz",
        ),
    ),
]

# ============================================================
# TARGET GENES
# ============================================================

TARGET_GENES = [
    "KRT20", "HDAC1", "APC",   "CDX2",
    "TFF1",  "TFF3",  "ZEB1",  "ZEB2",
    "AURKA", "CDH1",  "EZH2",  "HDAC2",
    "KDM6A", "KRT5",  "KRT14", "SOX2",
    "TP63",  "IVL",   "SPRR1A","NOTCH1",
    "KRT10", "KRT4",  "KRT13", "DSG1",
    "DSG3",  "CTNNB1","AXIN2", "AXIN1",
    "TCF7L2","LGR5",  "WNT5A", "MKI67",
    "TOP2A", "CDC20", "PCNA",  "PLK1",
    "CCNB1", "CCND1", "CCNE1", "CDKN1A",
    "CDKN2A","CDK4",  "CDK6",  "RB1",
    "VIM",   "FN1",   "CDH2",  "SNAI1",
    "SNAI2", "TWIST1","EGFR",  "ERBB2",
    "ERBB3", "MET",   "FGFR1", "FGFR2",
    "VEGFA", "KDR",   "DNMT3A","TET2",
    "BCL2",  "MCL1",  "BAX",   "BCL2L1",
    "BIRC5", "TP53",  "MDM2",  "MUC2",
    "MUC5B", "CLDN18","GKN1",  "MUC5AC",
    "CD274", "PDCD1", "CD8A",  "FOXP3",
    "MYC",   "PIK3CA","HIF1A", "MLH1",
    "MSH6",  "HES1",  "JAG1",  "TGFB1",
    "TGFBR2","FOXA2", "SOX9",  "KLF4",
    "LDHA",  "PGC",   "CCNA2", "CDK2",
]

# ============================================================
# LOGGING
# ============================================================

log_lines = []

def log(msg=""):
    print(msg)
    log_lines.append(str(msg))

def write_log():
    with open(LOG_FILE, "w") as f:
        f.write("\n".join(log_lines))

def fmt_p(p):
    if p is None or (
        isinstance(p, float) and np.isnan(p)
    ):
        return "p=N/A   "
    if p < 0.001:  return f"p={p:.2e} ***"
    elif p < 0.01: return f"p={p:.2e}  **"
    elif p < 0.05: return f"p={p:.4f}   *"
    else:          return f"p={p:.4f}  ns"

def safe_pearsonr(x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    m = np.isfinite(x) & np.isfinite(y)
    x, y = x[m], y[m]
    if len(x) < 5:
        return np.nan, np.nan
    return stats.pearsonr(x, y)

def safe_mwu(a, b, alt="two-sided"):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    a = a[np.isfinite(a)]
    b = b[np.isfinite(b)]
    if len(a) < 2 or len(b) < 2:
        return np.nan, np.nan
    return stats.mannwhitneyu(
        a, b, alternative=alt
    )

def norm01(s):
    s  = pd.Series(s, dtype=float)
    mn = s.min()
    mx = s.max()
    if mx > mn:
        return (s - mn) / (mx - mn)
    return pd.Series(0.5, index=s.index)

# ============================================================
# DOWNLOAD
# ============================================================

def download_file(url, dest, label=""):
    if os.path.exists(dest):
        log(f"  Already present: {dest} "
            f"({os.path.getsize(dest):,} bytes)")
        return True
    log(f"  Downloading {label}: {url}")
    try:
        r = requests.get(url, timeout=300)
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

def download_suppl():
    """Try all supplementary URL patterns."""
    for url, dest in SUPPL_URLS:
        if os.path.exists(dest):
            log(f"  Suppl already present: {dest}")
            return dest
        log(f"  Trying suppl: {url}")
        try:
            r = requests.get(url, timeout=60)
            if r.status_code == 200:
                with open(dest, "wb") as f:
                    f.write(r.content)
                log(f"  Suppl saved: {dest} "
                    f"({os.path.getsize(dest):,} bytes)")
                return dest
            log(f"  HTTP {r.status_code}")
        except Exception as e:
            log(f"  Error: {e}")
    return None

# ============================================================
# STEP 1: BUILD PROBE MAP
# FIX: use 'Gene symbol' col (index 2)
#      not 'UniGene symbol' (index 5)
# ============================================================

def build_probe_map_from_gpl(gpl_file):
    log("")
    log("=" * 65)
    log("STEP 1: BUILD PROBE MAP (FIXED v3)")
    log("Using 'Gene symbol' col not")
    log("'UniGene symbol' col")
    log("=" * 65)

    probe_map    = {}
    gene_to_prob = {}
    target_set   = set(TARGET_GENES)

    opener = (
        gzip.open(gpl_file, "rt",
                  encoding="utf-8",
                  errors="ignore")
        if gpl_file.endswith(".gz")
        else open(gpl_file, "r",
                  encoding="utf-8",
                  errors="ignore")
    )

    header   = []
    id_col   = None
    sym_col  = None
    in_data  = False
    n_lines  = 0

    with opener as f:
        for line in f:
            line = line.rstrip()
            if (
                line.startswith("!")
                or line.startswith("^")
            ):
                continue
            if line.startswith("#"):
                continue

            parts = line.split("\t")
            lower = [
                p.strip().strip('"').lower()
                for p in parts
            ]

            if not in_data:
                # Detect header by looking for
                # 'id' and 'gene symbol' columns
                has_id  = any(
                    h in ["id", "probe_id"]
                    for h in lower
                )
                has_sym = any(
                    "gene symbol" in h
                    or h == "symbol"
                    for h in lower
                )
                if has_id or has_sym or (
                    len(parts) > 3
                    and parts[0].startswith(
                        "ILMN"
                    )
                ):
                    if not has_id:
                        # First line is data,
                        # no header — probe in col 0
                        id_col  = 0
                        sym_col = None
                        # scan for symbol col
                        # based on content
                        in_data = True
                    else:
                        header = [
                            p.strip().strip('"')
                            for p in parts
                        ]
                        for i, h in enumerate(
                            lower
                        ):
                            if h == "id":
                                id_col = i
                            # FIX: prefer exact
                            # 'gene symbol' over
                            # 'unigene symbol'
                            if (
                                h == "gene symbol"
                                or h == "symbol"
                            ):
                                sym_col = i
                        # Fallback: any col with
                        # 'symbol' not 'unigene'
                        if sym_col is None:
                            for i, h in enumerate(
                                lower
                            ):
                                if (
                                    "symbol" in h
                                    and "unigene"
                                    not in h
                                    and "title"
                                    not in h
                                ):
                                    sym_col = i
                                    break
                        in_data = True
                        log(f"  Header cols: "
                            f"{header[:8]}")
                        log(f"  ID col  : {id_col}"
                            f" ({header[id_col] if id_col is not None and id_col < len(header) else 'N/A'})")
                        log(f"  Sym col : {sym_col}"
                            f" ({header[sym_col] if sym_col is not None and sym_col < len(header) else 'N/A'})")
                    continue

            if (
                id_col is None
                or sym_col is None
            ):
                # Try to find sym col from data
                # GPL6102 'Gene symbol' is col 2
                id_col  = 0
                sym_col = 2
                log(f"  Fallback: id=0 sym=2")

            if len(parts) <= max(
                id_col, sym_col
            ):
                continue

            probe_id = parts[id_col].strip('"')
            symbols  = parts[sym_col].strip('"')
            n_lines += 1

            if not probe_id or not symbols:
                continue
            if symbols in [
                "---", "NA", "", " "
            ]:
                continue

            for sym in re.split(
                r"[;,/\s]+|///", symbols
            ):
                sym = sym.strip()
                if not sym or sym in [
                    "---", "NA"
                ]:
                    continue
                if sym in target_set:
                    probe_map[probe_id] = sym
                    if sym not in gene_to_prob:
                        gene_to_prob[sym] = []
                    if probe_id not in (
                        gene_to_prob[sym]
                    ):
                        gene_to_prob[sym].append(
                            probe_id
                        )

    log(f"  Data lines scanned: {n_lines}")
    log(f"  Probes mapped     : "
        f"{len(probe_map)}")
    log(f"  Genes covered     : "
        f"{len(gene_to_prob)}")

    if gene_to_prob:
        log(f"  Genes found       : "
            f"{sorted(gene_to_prob.keys())}")
        # Report missing targets
        missing = sorted(
            set(TARGET_GENES)
            - set(gene_to_prob.keys())
        )
        log(f"  Missing targets   : "
            f"{missing[:20]}"
            + ("..." if len(missing) > 20
               else ""))
    else:
        log("  WARNING: Still 0 genes mapped")
        log("  Running full header dump...")
        _dump_gpl_header(gpl_file)

    return probe_map, gene_to_prob


def _dump_gpl_header(gpl_file):
    """Print first 10 data lines of GPL."""
    opener = (
        gzip.open(gpl_file, "rt",
                  encoding="utf-8",
                  errors="ignore")
        if gpl_file.endswith(".gz")
        else open(gpl_file, "r",
                  encoding="utf-8",
                  errors="ignore")
    )
    lines = []
    with opener as f:
        for line in f:
            if not line.startswith("!"):
                lines.append(line.rstrip())
            if len(lines) >= 12:
                break
    log("  GPL first 12 lines:")
    for l in lines:
        log(f"    {l[:120]}")

# ============================================================
# STEP 2: PARSE SERIES MATRIX
# ============================================================

def parse_series_matrix(
    filepath, probe_map, gene_to_prob
):
    log("")
    log("=" * 65)
    log("STEP 2: PARSE SERIES MATRIX")
    log(f"  File: {filepath}")
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

    sample_ids    = []
    sample_titles = []
    char_rows     = {}
    in_table      = False
    header_cols   = []
    probe_ids     = []
    rows          = []

    with opener as f:
        for line in f:
            line = line.rstrip("\n").rstrip("\r")

            if "!Sample_geo_accession" in line:
                parts = line.split("\t")
                sample_ids = [
                    p.strip().strip('"')
                    for p in parts[1:]
                    if p.strip().strip('"')
                ]

            elif "!Sample_title" in line:
                parts = line.split("\t")
                sample_titles = [
                    p.strip().strip('"')
                    for p in parts[1:]
                    if p.strip().strip('"')
                ]

            elif (
                "!Sample_characteristics_ch1"
                in line
            ):
                parts = line.split("\t")
                vals = [
                    p.strip().strip('"')
                    for p in parts[1:]
                ]
                char_rows[len(char_rows)] = vals

            elif "series_matrix_table_begin" in line:
                in_table = True
                continue

            elif "series_matrix_table_end" in line:
                break

            elif in_table:
                parts = [
                    p.strip().strip('"')
                    for p in line.split("\t")
                ]
                if not header_cols:
                    header_cols = parts
                    continue
                if not parts or not parts[0]:
                    continue

                probe_id = parts[0]
                if probe_id not in probe_map:
                    continue

                try:
                    vals = [
                        float(p)
                        if p not in [
                            "", "null", "NA",
                            "nan", "N/A",
                            "Inf", "-Inf",
                        ]
                        else np.nan
                        for p in parts[1:]
                    ]
                except ValueError:
                    continue

                if len(vals) != (
                    len(header_cols) - 1
                ):
                    continue

                probe_ids.append(probe_id)
                rows.append(vals)

    log(f"  Sample IDs   : {len(sample_ids)}")
    log(f"  Probes found : {len(probe_ids)}")

    if not probe_ids:
        log("  WARNING: No probes found")
        _inspect_matrix_probes(filepath,
                               probe_map)
        return None, None, None

    cols = header_cols[1:]
    n_c  = len(rows[0]) if rows else 0
    cols = cols[:n_c]

    df = pd.DataFrame(
        rows, index=probe_ids,
        columns=cols, dtype=float,
    )

    gene_expr   = {}
    genes_found = []
    for gene, probes in gene_to_prob.items():
        avail = [
            p for p in probes
            if p in df.index
        ]
        if not avail:
            continue
        if len(avail) == 1:
            gene_expr[gene] = (
                df.loc[avail[0]].values
            )
        else:
            meds = [
                df.loc[p].median()
                for p in avail
            ]
            best = avail[np.argmax(meds)]
            gene_expr[gene] = (
                df.loc[best].values
            )
        genes_found.append(gene)

    df_genes = pd.DataFrame(
        gene_expr, index=cols, dtype=float
    )
    log(f"  Genes mapped : {len(genes_found)}")
    log(f"  Genes found  : "
        f"{sorted(genes_found)}")

    meta = pd.DataFrame(index=df_genes.index)
    if len(sample_titles) == len(df_genes):
        meta["title"] = sample_titles
    elif (sample_ids
          and len(sample_titles)
              == len(sample_ids)):
        tmap = dict(
            zip(sample_ids, sample_titles)
        )
        meta["title"] = [
            tmap.get(s, "")
            for s in df_genes.index
        ]

    return df_genes, meta, char_rows


def _inspect_matrix_probes(
    filepath, probe_map
):
    opener = (
        gzip.open(filepath, "rt",
                  encoding="utf-8",
                  errors="ignore")
        if filepath.endswith(".gz")
        else open(filepath, "r",
                  encoding="utf-8",
                  errors="ignore")
    )
    seen = []
    in_t = False
    hdr  = []
    with opener as f:
        for line in f:
            line = line.rstrip()
            if "table_begin" in line:
                in_t = True
                continue
            if "table_end" in line:
                break
            if not in_t:
                continue
            parts = [
                p.strip().strip('"')
                for p in line.split("\t")
            ]
            if not hdr:
                hdr = parts
                continue
            if parts and parts[0]:
                seen.append(parts[0])
            if len(seen) >= 20:
                break
    log("  First 20 actual probe IDs in matrix:")
    for p in seen:
        in_map = p in probe_map
        log(f"    {p}  {'← IN MAP' if in_map else ''}")
    # Show sample from probe_map
    log(f"\n  Sample probe_map entries (first 5):")
    for k, v in list(probe_map.items())[:5]:
        log(f"    {k} → {v}")

# ============================================================
# STEP 3: CLASSIFY SAMPLES
# ============================================================

def classify_samples(df_genes, meta):
    log("")
    log("=" * 65)
    log("STEP 3: CLASSIFY SAMPLES")
    log("=" * 65)

    groups = []
    for s in df_genes.index:
        title = ""
        if (
            meta is not None
            and "title" in meta.columns
            and s in meta.index
        ):
            title = str(
                meta.loc[s, "title"]
            ).lower()

        if any(x in title for x in [
            "barrett", "be_", "be-",
        ]):
            groups.append("Barrett")
        elif any(x in title for x in [
            "eac_", "eac-", "eac ",
            " eac", "adenocarcinoma",
            "adeno",
        ]):
            groups.append("EAC")
        elif any(x in title for x in [
            "normal", "squamous",
            "eso_st_", "nse",
        ]):
            groups.append("Normal")
        else:
            groups.append("Unknown")

    gs = pd.Series(groups,
                   index=df_genes.index)

    log(f"\n  Group counts:")
    for g, n in gs.value_counts().items():
        log(f"    {g}: {n}")

    return gs

# ============================================================
# STEP 4: SURVIVAL FROM SOFT FILE
# Extended key matching
# ============================================================

def parse_survival_from_soft(
    soft_file, df_genes
):
    log("")
    log("=" * 65)
    log("STEP 4: SURVIVAL FROM SOFT FILE")
    log("Extended clinical key search")
    log("=" * 65)

    opener = (
        gzip.open(soft_file, "rt",
                  encoding="utf-8",
                  errors="ignore")
        if soft_file.endswith(".gz")
        else open(soft_file, "r",
                  encoding="utf-8",
                  errors="ignore")
    )

    sample_data = {}
    cur_sample  = None
    cur_chars   = {}

    with opener as f:
        for line in f:
            line = line.rstrip()

            if line.startswith("^SAMPLE"):
                if cur_sample:
                    sample_data[cur_sample] = (
                        dict(cur_chars)
                    )
                cur_sample = (
                    line.split("=")[-1].strip()
                )
                cur_chars = {}

            elif (
                "!Sample_characteristics_ch1"
                in line
            ):
                val = (
                    line.split("=", 1)[-1]
                    .strip().strip('"')
                )
                if ":" in val:
                    k, v = val.split(":", 1)
                    key = k.strip().lower()
                    cur_chars[key] = v.strip()
                else:
                    n = f"c{len(cur_chars)}"
                    cur_chars[n] = val

    if cur_sample:
        sample_data[cur_sample] = dict(cur_chars)

    log(f"  Sample records: {len(sample_data)}")

    # Show all unique keys
    all_keys = set()
    for d in sample_data.values():
        all_keys.update(d.keys())
    log(f"  All characteristic keys:")
    for k in sorted(all_keys):
        ex = next(
            (d[k] for d in sample_data.values()
             if k in d), ""
        )
        log(f"    '{k}': {ex[:50]}")

    # Parse survival — look for any
    # time and event fields
    os_time  = {}
    os_event = {}

    time_patterns = [
        re.compile(
            r"(?:os|survival|time|months|"
            r"follow.?up)[^:]*",
            re.I
        ),
    ]
    event_patterns = [
        re.compile(
            r"(?:vital|status|event|death|"
            r"dead|alive|censor)",
            re.I
        ),
    ]

    for gsm, chars in sample_data.items():
        for k, v in chars.items():
            # Time
            if any(
                p.search(k)
                for p in time_patterns
            ):
                nums = re.findall(
                    r"[\d.]+", str(v)
                )
                if nums:
                    try:
                        os_time[gsm] = float(
                            nums[0]
                        )
                    except ValueError:
                        pass

            # Event
            if any(
                p.search(k)
                for p in event_patterns
            ):
                vl = str(v).lower()
                if any(
                    x in vl for x in [
                        "dead", "died",
                        "deceased", "1",
                        "yes",
                    ]
                ):
                    os_event[gsm] = 1
                elif any(
                    x in vl for x in [
                        "alive", "0", "no",
                        "living", "censor",
                    ]
                ):
                    os_event[gsm] = 0

    log(f"\n  OS time  : {len(os_time)}")
    log(f"  OS event : {len(os_event)}")

    if len(os_time) == 0:
        log("  NOTE: No survival data in soft")
        log("  GSE13898 survival may be in")
        log("  supplementary file only.")

    t_arr = np.full(len(df_genes), np.nan)
    e_arr = np.full(len(df_genes), np.nan)
    path_arr = [""] * len(df_genes)

    for i, gsm in enumerate(df_genes.index):
        if gsm in os_time:
            t_arr[i] = os_time[gsm]
        if gsm in os_event:
            e_arr[i] = os_event[gsm]
        # Pathology
        chars = sample_data.get(gsm, {})
        for k in ["pathology", "histology",
                  "diagnosis"]:
            if k in chars:
                path_arr[i] = chars[k]
                break

    surv_df = pd.DataFrame({
        "os_time":   t_arr,
        "os_event":  e_arr,
        "pathology": path_arr,
    }, index=df_genes.index)

    log(f"\n  Pathology breakdown:")
    pc = pd.Series(path_arr).value_counts()
    for pv, cnt in pc.items():
        if pv:
            log(f"    {pv}: {cnt}")

    return surv_df

# ============================================================
# STEP 4b: TRY SUPPLEMENTARY FILE
# ============================================================

def parse_survival_from_suppl(
    suppl_file, df_genes
):
    log("")
    log("=" * 65)
    log("STEP 4b: SURVIVAL FROM SUPPL FILE")
    log(f"  File: {suppl_file}")
    log("=" * 65)

    if not suppl_file or not os.path.exists(
        suppl_file
    ):
        log("  Suppl file not available")
        return None

    try:
        opener = (
            gzip.open(suppl_file, "rt",
                      encoding="utf-8",
                      errors="ignore")
            if suppl_file.endswith(".gz")
            else open(suppl_file, "r",
                      encoding="utf-8",
                      errors="ignore")
        )
        with opener as f:
            content = f.read(2000)
        log(f"  First 2000 chars:")
        log(content[:1000])

        # Try parsing as TSV
        opener2 = (
            gzip.open(suppl_file, "rt",
                      encoding="utf-8",
                      errors="ignore")
            if suppl_file.endswith(".gz")
            else open(suppl_file, "r",
                      encoding="utf-8",
                      errors="ignore")
        )
        df_s = pd.read_csv(
            opener2,
            sep="\t",
            encoding="utf-8",
        )
        log(f"  Suppl columns: "
            f"{list(df_s.columns)}")
        log(f"  Suppl shape: {df_s.shape}")
        log(f"  Head:\n{df_s.head(3)}")
        return df_s

    except Exception as e:
        log(f"  Error parsing suppl: {e}")
        return None

# ============================================================
# PANELS AND DEPTH
# ============================================================

EAC_SWITCH_S2 = [
    "CDH1", "ZEB1", "KRT5", "APC", "CTNNB1"
]
EAC_FA_S2 = [
    "CDX2", "TFF1", "KRT20", "VEGFA",
    "NOTCH1", "HDAC1", "EZH2",
]

def build_depth_score(df, switch, fa, label):
    gc  = list(df.columns)
    sw  = [g for g in switch if g in gc]
    fa_ = [g for g in fa     if g in gc]
    depth = pd.Series(
        np.zeros(len(df)),
        index=df.index, dtype=float,
    )
    n = 0
    if sw:
        depth += (
            1 - norm01(df[sw].mean(axis=1))
        )
        n += 1
    if fa_:
        depth += norm01(
            df[fa_].mean(axis=1)
        )
        n += 1
    if n > 0:
        depth /= n

    log(f"  {label} (n={len(df)}): "
        f"mean={depth.mean():.4f} "
        f"std={depth.std():.4f} "
        f"sw={sw} fa={fa_}")
    return depth

# ============================================================
# VALIDATION 1 — SURVIVAL
# ============================================================

def survival_panel_test(
    eac_df, surv_df, group_series
):
    log("")
    log("=" * 65)
    log("VALIDATION 1: SURVIVAL PANEL")
    log("KRT20(+) / HDAC1(+) / APC(-)")
    log("=" * 65)

    eac_idx = group_series[
        group_series == "EAC"
    ].index.intersection(eac_df.index)

    df   = eac_df.loc[eac_idx]
    surv = surv_df.loc[eac_idx]
    t    = surv["os_time"].values
    e    = surv["os_event"].values

    valid = (
        ~np.isnan(t) & ~np.isnan(e)
        & (t > 0)
    )
    log(f"  EAC n={len(eac_idx)}")
    log(f"  Valid survival: {valid.sum()}")

    if valid.sum() < 8:
        log("  Insufficient survival data")
        log("  Checking pathology:")
        if "pathology" in surv.columns:
            pc = (
                surv["pathology"]
                .value_counts()
            )
            for pv, cnt in pc.items():
                if pv:
                    log(f"    {pv}: {cnt}")
        log("")
        log("  NOTE: GSE13898 OS data not in")
        log("  GEO soft/matrix files.")
        log("  Supplementary table required.")
        log("  Survival tests skipped.")
        log("  Progression geometry and")
        log("  ZEB2-AURKA tests proceed.")
        return None

    t    = t[valid]
    e    = e[valid]
    df_v = df.iloc[valid]
    gc   = list(df_v.columns)

    log(f"  OS: {t.min():.1f}–{t.max():.1f} mo")
    log(f"  Events: {int(e.sum())} / {len(e)}")

    # Individual gene tests
    log(f"\n  {'Gene':<10} {'p-value':>14}  "
        f"Direction  Conf")
    log(f"  {'-'*50}")

    single = {}
    for gene, pred in [
        ("KRT20", "UP-worse"),
        ("HDAC1", "UP-worse"),
        ("APC",   "DOWN-worse"),
        ("EZH2",  "UP-worse"),
        ("ZEB1",  "DOWN-better"),
        ("CDH1",  "DOWN-worse"),
        ("VEGFA", "UP-worse"),
        ("MKI67", "UP-worse"),
        ("AURKA", "UP-worse"),
        ("ERBB2", "UP-worse"),
    ]:
        if gene not in gc:
            continue
        vals = df_v[gene].values
        med  = np.nanmedian(vals)
        hi   = vals >= med
        lo   = ~hi
        if hi.sum() < 3 or lo.sum() < 3:
            continue
        try:
            res = logrank_test(
                t[hi], t[lo], e[hi], e[lo]
            )
            p = res.p_value
        except Exception:
            p = np.nan
        direction = (
            "hi=worse"
            if (
                not np.isnan(p)
                and t[hi].mean() < t[lo].mean()
            )
            else "lo=worse"
        )
        conf = (
            "✓"
            if (
                pred == "UP-worse"
                and direction == "hi=worse"
            )
            or (
                pred == "DOWN-worse"
                and direction == "hi=worse"
            )
            else "✗"
        )
        log(f"  {gene:<10} {fmt_p(p):>14}  "
            f"{direction}  {conf}")
        single[gene] = {"p": p,
                        "direction": direction}

    # Panel
    pg = [
        g for g in ["KRT20", "HDAC1", "APC"]
        if g in gc
    ]
    panel_result = None
    if len(pg) >= 2:
        parts = []
        for gene in pg:
            ns = norm01(df_v[gene].values)
            parts.append(
                1 - ns if gene == "APC" else ns
            )
        score = np.mean(parts, axis=0)
        med_s = np.median(score)
        hi = score >= med_s
        lo = ~hi
        try:
            res_p = logrank_test(
                t[hi], t[lo], e[hi], e[lo]
            )
            p_panel = res_p.p_value
        except Exception:
            p_panel = np.nan

        log(f"\n  Panel ({pg}):")
        log(f"  p={fmt_p(p_panel)}")
        if not np.isnan(p_panel):
            if p_panel < 0.05:
                log("  SP-1 CONFIRMED ✓")
            else:
                log("  SP-1 NOT CONFIRMED ✗")

        panel_result = {
            "t": t, "e": e,
            "hi": hi, "lo": lo,
            "panel_score": score,
            "p_panel": p_panel,
            "single_results": single,
            "df_v": df_v,
        }

    return panel_result

# ============================================================
# VALIDATION 2 — ZEB2-AURKA
# ============================================================

def zeb2_aurka_validation(groups):
    log("")
    log("=" * 65)
    log("VALIDATION 2: ZEB2-AURKA COUPLING")
    log("Pred ZA-2: r > 0.60 in EAC")
    log("STAD reference: r=+0.9871")
    log("=" * 65)

    results = {}
    for label in ["EAC", "Barrett", "Normal"]:
        if label not in groups:
            continue
        df = groups[label]
        gc = list(df.columns)
        missing = [
            g for g in ["ZEB2", "AURKA"]
            if g not in gc
        ]
        if missing:
            log(f"  {label}: missing {missing}")
            avail = [
                g for g in ["ZEB2", "AURKA"]
                if g in gc
            ]
            log(f"  Available: {avail}")
            continue

        rv, pv = safe_pearsonr(
            df["ZEB2"].values,
            df["AURKA"].values,
        )
        log(f"\n  {label} (n={len(df)}):")
        log(f"  r(ZEB2,AURKA) = "
            f"{rv:+.4f}  {fmt_p(pv)}")
        results[label] = (rv, pv)

        if label == "EAC":
            if not np.isnan(rv):
                if rv > 0.60:
                    log("  ZA-2 CONFIRMED ✓")
                elif rv > 0:
                    log("  ZA-1 CONFIRMED ✓ "
                        "(r>0, not >0.60)")
                else:
                    log("  ZA-1/ZA-2 NOT CONFIRMED")

    return results

# ============================================================
# VALIDATION 3 — PROGRESSION
# ============================================================

def progression_geometry(groups, group_order):
    log("")
    log("=" * 65)
    log("VALIDATION 3: PROGRESSION GEOMETRY")
    log("Normal → Barrett → EAC")
    log("=" * 65)

    all_gc = set()
    for df in groups.values():
        all_gc.update(df.columns)

    log(f"  Genes in matrix: {sorted(all_gc)}")

    markers = [
        ("ZEB1",   "PG-2", "Normal>EAC"),
        ("TFF1",   "PG-3", "EAC>Normal"),
        ("CDH1",   "PG-4", "Normal>EAC"),
        ("EZH2",   "PG-5", "EAC>Normal"),
        ("HDAC1",  "PG-6", "EAC>Normal"),
        ("KRT20",  "CP-2", "EAC>Normal"),
        ("APC",    "CP-3", "Normal>EAC"),
        ("CDX2",   "-",    "EAC>Normal"),
        ("VEGFA",  "-",    "EAC>Normal"),
        ("KRT5",   "-",    "Normal>EAC"),
        ("AURKA",  "-",    "EAC>Normal"),
        ("ERBB2",  "-",    "EAC>Normal"),
        ("AXIN2",  "-",    "EAC>Normal"),
        ("MKI67",  "-",    "EAC>Normal"),
    ]

    log(f"\n  {'Gene':<10} {'Normal':>9} "
        f"{'Barrett':>9} {'EAC':>9}  "
        f"p(EAC vs N)    Pred  Conf")
    log(f"  {'-'*72}")

    for gene, pred_id, direction in markers:
        if gene not in all_gc:
            continue
        vals = {}
        for g in group_order:
            if (
                g in groups
                and gene in groups[g].columns
            ):
                vals[g] = (
                    groups[g][gene].mean()
                )
            else:
                vals[g] = np.nan

        ev = (
            groups["EAC"][gene].values
            if "EAC" in groups
            and gene in groups["EAC"].columns
            else np.array([])
        )
        nv = (
            groups["Normal"][gene].values
            if "Normal" in groups
            and gene in groups["Normal"].columns
            else np.array([])
        )
        _, pp = safe_mwu(ev, nv, "two-sided")

        nm = vals.get("Normal", np.nan)
        bm = vals.get("Barrett", np.nan)
        em = vals.get("EAC", np.nan)

        conf = "?"
        if (
            not np.isnan(em)
            and not np.isnan(nm)
        ):
            conf = (
                "✓"
                if (
                    direction == "EAC>Normal"
                    and em > nm
                )
                or (
                    direction == "Normal>EAC"
                    and nm > em
                )
                else "✗"
            )

        log(
            f"  {gene:<10} "
            f"{nm:>9.4f} "
            f"{bm:>9.4f} "
            f"{em:>9.4f}  "
            f"{fmt_p(pp):>14}  "
            f"{pred_id:<6} {conf}"
            if not any(
                np.isnan(x)
                for x in [nm, bm, em]
            )
            else
            f"  {gene:<10} "
            + ("N/A" if np.isnan(nm) else f"{nm:.4f}")
            + " "
            + ("N/A" if np.isnan(bm) else f"{bm:.4f}")
            + " "
            + ("N/A" if np.isnan(em) else f"{em:.4f}")
        )

    # Depth scores
    log(f"\n  Depth scores:")
    depth_dict = {}
    for g in group_order:
        if g not in groups:
            continue
        if len(groups[g]) < 3:
            continue
        d = build_depth_score(
            groups[g],
            EAC_SWITCH_S2,
            EAC_FA_S2,
            g,
        )
        depth_dict[g] = d

    log(f"\n  Group order test (PG-1):")
    log(f"  {'Group':<12} {'n':>4}  "
        f"{'mean':>8}  std")
    for g in group_order:
        if g in depth_dict:
            d = depth_dict[g]
            log(f"  {g:<12} {len(d):>4}  "
                f"{d.mean():>8.4f}  "
                f"{d.std():.4f}")

    if (
        "Normal" in depth_dict
        and "EAC" in depth_dict
    ):
        _, p_ne = safe_mwu(
            depth_dict["EAC"].values,
            depth_dict["Normal"].values,
            "greater",
        )
        log(f"\n  EAC > Normal  : {fmt_p(p_ne)}")
        if not np.isnan(p_ne) and p_ne < 0.05:
            log("  PG-1 CONFIRMED ✓")

    if (
        "Normal" in depth_dict
        and "Barrett" in depth_dict
    ):
        _, p_nb = safe_mwu(
            depth_dict["Barrett"].values,
            depth_dict["Normal"].values,
            "greater",
        )
        log(f"  Barrett>Normal: {fmt_p(p_nb)}")

    if (
        "Barrett" in depth_dict
        and "EAC" in depth_dict
    ):
        _, p_be = safe_mwu(
            depth_dict["EAC"].values,
            depth_dict["Barrett"].values,
            "greater",
        )
        log(f"  EAC > Barrett : {fmt_p(p_be)}")

    return depth_dict

# ============================================================
# CROSS-PLATFORM
# ============================================================

def cross_platform_validation(
    eac, depth_eac
):
    log("")
    log("=" * 65)
    log("CROSS-PLATFORM VALIDATION")
    log("GSE13898 vs GSE26886")
    log("=" * 65)

    gc = list(eac.columns)
    checks = [
        ("KRT20",   0.50, "CP-2 ≥0.50"),
        ("HDAC1",   0.30, "≥0.30"),
        ("APC",    -0.30, "CP-3 ≤-0.30"),
        ("EZH2",    0.30, "≥0.30"),
        ("CDX2",    0.20, "≥0.20"),
        ("VEGFA",   0.20, "≥0.20"),
        ("ZEB1",   -0.20, "≤-0.20"),
        ("CDH1",   -0.20, "≤-0.20"),
        ("MKI67",   0.30, "≥0.30"),
        ("AURKA",   0.20, "≥0.20"),
    ]

    log(f"\n  {'Gene':<10} {'S3 r':>8}  "
        f"p-value        Threshold  Result")
    log(f"  {'-'*60}")

    rep = total = 0
    for gene, thr, label in checks:
        if gene not in gc:
            log(f"  {gene:<10} NOT IN MATRIX")
            continue
        rv, pv = safe_pearsonr(
            depth_eac.values,
            eac[gene].values,
        )
        if not np.isnan(rv):
            total += 1
            ok = rv >= thr if thr >= 0 else rv <= thr
            if ok:
                rep += 1
            res = "YES ✓" if ok else "NO  ✗"
        else:
            res = "N/A"
        log(
            f"  {gene:<10} {rv:>+8.4f}  "
            f"{fmt_p(pv):>14}  "
            f"{label:>10}  {res}"
            if not np.isnan(rv)
            else f"  {gene:<10} N/A"
        )

    if total > 0:
        pct = 100 * rep / total
        log(f"\n  Replicated: {rep}/{total} "
            f"({pct:.0f}%)")
        if pct >= 70:
            log("  CP-1 CONFIRMED ✓")
        else:
            log("  CP-1 NOT CONFIRMED")

# ============================================================
# ZEB2-AURKA DEEP DIVE
# ============================================================

def zeb2_aurka_deep(eac):
    log("")
    log("=" * 65)
    log("ZEB2-AURKA DEEP DIVE")
    log("=" * 65)

    gc = list(eac.columns)
    log(f"  Genes in EAC: {sorted(gc)}")

    if "ZEB2" in gc:
        corrs = []
        for gene in gc:
            rv, pv = safe_pearsonr(
                eac["ZEB2"].values,
                eac[gene].values,
            )
            if not np.isnan(rv):
                corrs.append((gene, rv, pv))
        corrs.sort(
            key=lambda x: abs(x[1]),
            reverse=True,
        )
        log(f"\n  ZEB2 correlates in EAC "
            f"(n={len(eac)}):")
        for g, r, p in corrs[:12]:
            log(f"  {g:<10} r={r:>+8.4f}  "
                f"{fmt_p(p)}")

    if "AURKA" not in gc:
        log(f"\n  AURKA not in GPL6102 matrix")
        log(f"  Searching for AURKA proxy genes")
        log(f"  (mitotic kinase correlates):")
        proxy = [
            "CDC20", "PLK1", "CCNB1",
            "TOP2A", "MKI67",
        ]
        for gene in proxy:
            if gene in gc:
                log(f"  {gene} present — "
                    f"can serve as mitotic proxy")

# ============================================================
# FIGURE
# ============================================================

def generate_figure(
    groups, depth_dict,
    surv_result, zeb2_result,
    group_order,
):
    log("")
    log("--- Generating figure ---")

    fig = plt.figure(figsize=(28, 22))
    fig.suptitle(
        "Esophageal Cancer — Script 3\n"
        "GSE13898 | EAC + Barrett + Normal\n"
        "OrganismCore | Doc 90d | 2026-03-01",
        fontsize=10, fontweight="bold",
        y=0.99,
    )

    gs_f = gridspec.GridSpec(
        3, 3, figure=fig,
        hspace=0.55, wspace=0.45,
    )
    COLORS = {
        "Normal":  "#27ae60",
        "Barrett": "#f39c12",
        "EAC":     "#2980b9",
    }

    def gc_col(g):
        return COLORS.get(g, "#95a5a6")

    # A — KM or message
    ax_a = fig.add_subplot(gs_f[0, 0])
    if surv_result is not None:
        t  = surv_result["t"]
        e  = surv_result["e"]
        hi = surv_result["hi"]
        lo = surv_result["lo"]
        pp = surv_result.get("p_panel", np.nan)
        kmf = KaplanMeierFitter()
        kmf.fit(t[hi], e[hi],
                label=f"High (n={hi.sum()})")
        kmf.plot_survival_function(
            ax=ax_a, color="#e74c3c",
            ci_show=False)
        kmf.fit(t[lo], e[lo],
                label=f"Low (n={lo.sum()})")
        kmf.plot_survival_function(
            ax=ax_a, color="#27ae60",
            ci_show=False)
        p_str = (f"p={pp:.4f}"
                 if not np.isnan(pp) else "N/A")
        ax_a.set_title(
            f"A — KM Panel\n{p_str}",
            fontsize=9)
        ax_a.legend(fontsize=7)
    else:
        ax_a.text(
            0.5, 0.5,
            "OS data not in\nGEO soft file.\n"
            "Supplementary\ntable required.",
            ha="center", va="center",
            transform=ax_a.transAxes,
            fontsize=9,
        )
        ax_a.set_title(
            "A — KM: Panel (survival N/A)",
            fontsize=9)

    # B — ZEB2 correlates scatter
    ax_b = fig.add_subplot(gs_f[0, 1])
    if "EAC" in groups:
        df = groups["EAC"]
        gc_eac = list(df.columns)
        if "ZEB2" in gc_eac and len(gc_eac) > 1:
            # Plot ZEB2 vs best correlate
            corrs = []
            for gene in gc_eac:
                if gene == "ZEB2":
                    continue
                rv, pv = safe_pearsonr(
                    df["ZEB2"].values,
                    df[gene].values,
                )
                if not np.isnan(rv):
                    corrs.append((gene, rv, pv))
            if corrs:
                corrs.sort(
                    key=lambda x: abs(x[1]),
                    reverse=True,
                )
                best_gene = corrs[0][0]
                rv_best   = corrs[0][1]
                ax_b.scatter(
                    df["ZEB2"].values,
                    df[best_gene].values,
                    alpha=0.6, s=30,
                    color=COLORS["EAC"],
                )
                ax_b.set_xlabel(
                    "ZEB2", fontsize=8)
                ax_b.set_ylabel(
                    best_gene, fontsize=8)
                ax_b.set_title(
                    f"B — ZEB2 vs {best_gene}\n"
                    f"r={rv_best:+.3f} "
                    f"(best correlate in EAC)",
                    fontsize=8)
    else:
        ax_b.set_title("B — ZEB2 correlates",
                       fontsize=9)

    # C — Progression depth
    ax_c = fig.add_subplot(gs_f[0, 2])
    vg = [
        (g, depth_dict[g])
        for g in group_order
        if g in depth_dict
    ]
    if vg:
        for i, (g, d) in enumerate(vg):
            ax_c.scatter(
                [i] * len(d), d.values,
                alpha=0.4, s=18,
                color=gc_col(g))
            ax_c.scatter(
                [i], [d.mean()],
                s=120, color=gc_col(g),
                zorder=5, marker="D",
                label=f"{g} μ={d.mean():.3f}")
        ax_c.set_xticks(range(len(vg)))
        ax_c.set_xticklabels(
            [x[0] for x in vg], fontsize=8)
        ax_c.legend(fontsize=7)
    ax_c.set_ylabel("Depth score", fontsize=8)
    ax_c.set_title(
        "C — Progression Geometry\n"
        "Normal → Barrett → EAC",
        fontsize=9)

    # D — Key markers
    ax_d = fig.add_subplot(gs_f[1, 0])
    key  = [
        "ZEB1", "TFF1", "CDX2",
        "CDH1", "EZH2", "HDAC1",
    ]
    avail = [
        g for g in key
        if any(
            g in grp.columns
            for grp in groups.values()
        )
    ]
    if avail:
        x = np.arange(len(avail))
        w = 0.25
        for i, grp_name in enumerate(
            ["Normal", "Barrett", "EAC"]
        ):
            if grp_name not in groups:
                continue
            df = groups[grp_name]
            means = [
                df[g].mean()
                if g in df.columns else 0
                for g in avail
            ]
            ax_d.bar(
                x + (i - 1) * w,
                means, w,
                color=gc_col(grp_name),
                label=grp_name,
                alpha=0.85,
            )
        ax_d.set_xticks(x)
        ax_d.set_xticklabels(
            avail, rotation=45,
            ha="right", fontsize=7)
        ax_d.legend(fontsize=6)
    ax_d.set_title(
        "D — Key Markers\nNormal/Barrett/EAC",
        fontsize=9)

    # E — Epigenetic
    ax_e = fig.add_subplot(gs_f[1, 1])
    epi  = ["EZH2", "HDAC1", "HDAC2", "KDM6A"]
    epi_a = [
        g for g in epi
        if any(
            g in grp.columns
            for grp in groups.values()
        )
    ]
    if epi_a:
        x = np.arange(len(epi_a))
        w = 0.25
        for i, grp_name in enumerate(
            ["Normal", "Barrett", "EAC"]
        ):
            if grp_name not in groups:
                continue
            df = groups[grp_name]
            means = [
                df[g].mean()
                if g in df.columns else 0
                for g in epi_a
            ]
            ax_e.bar(
                x + (i - 1) * w,
                means, w,
                color=gc_col(grp_name),
                label=grp_name,
                alpha=0.85,
            )
        ax_e.set_xticks(x)
        ax_e.set_xticklabels(
            epi_a, rotation=45,
            ha="right", fontsize=8)
        ax_e.legend(fontsize=6)
    ax_e.set_title(
        "E — Epigenetic Progression",
        fontsize=9)

    # F — ZEB1 boxplot
    ax_f = fig.add_subplot(gs_f[1, 2])
    for i, g in enumerate(
        ["Normal", "Barrett", "EAC"]
    ):
        if (
            g not in groups
            or "ZEB1" not in groups[g].columns
        ):
            continue
        vals = groups[g]["ZEB1"].values
        vals = vals[np.isfinite(vals)]
        ax_f.boxplot(
            vals, positions=[i],
            patch_artist=True,
            boxprops=dict(
                facecolor=gc_col(g), alpha=0.7
            ),
            medianprops=dict(
                color="black", linewidth=2
            ),
            widths=0.4,
        )
    ax_f.set_xticks([0, 1, 2])
    ax_f.set_xticklabels(
        ["Normal", "Barrett", "EAC"],
        fontsize=8)
    ax_f.set_title(
        "F — ZEB1 Squamous Separator",
        fontsize=9)

    # G — Wnt
    ax_g = fig.add_subplot(gs_f[2, 0])
    wnt = [
        "APC", "CTNNB1", "AXIN2", "LGR5"
    ]
    wnt_a = [
        g for g in wnt
        if any(
            g in grp.columns
            for grp in groups.values()
        )
    ]
    if wnt_a:
        x = np.arange(len(wnt_a))
        w = 0.25
        for i, grp_name in enumerate(
            ["Normal", "Barrett", "EAC"]
        ):
            if grp_name not in groups:
                continue
            df = groups[grp_name]
            means = [
                df[g].mean()
                if g in df.columns else 0
                for g in wnt_a
            ]
            ax_g.bar(
                x + (i - 1) * w,
                means, w,
                color=gc_col(grp_name),
                label=grp_name,
                alpha=0.85,
            )
        ax_g.set_xticks(x)
        ax_g.set_xticklabels(
            wnt_a, rotation=45,
            ha="right", fontsize=8)
        ax_g.legend(fontsize=6)
    ax_g.set_title("G — Wnt Pathway",
                   fontsize=9)

    # H — RTK/proliferation
    ax_h = fig.add_subplot(gs_f[2, 1])
    rtk  = [
        "EGFR", "ERBB2", "MKI67",
        "VEGFA", "FGFR2",
    ]
    rtk_a = [
        g for g in rtk
        if any(
            g in grp.columns
            for grp in groups.values()
        )
    ]
    if rtk_a:
        x = np.arange(len(rtk_a))
        w = 0.25
        for i, grp_name in enumerate(
            ["Normal", "Barrett", "EAC"]
        ):
            if grp_name not in groups:
                continue
            df = groups[grp_name]
            means = [
                df[g].mean()
                if g in df.columns else 0
                for g in rtk_a
            ]
            ax_h.bar(
                x + (i - 1) * w,
                means, w,
                color=gc_col(grp_name),
                label=grp_name,
                alpha=0.85,
            )
        ax_h.set_xticks(x)
        ax_h.set_xticklabels(
            rtk_a, rotation=45,
            ha="right", fontsize=8)
        ax_h.legend(fontsize=6)
    ax_h.set_title(
        "H — RTK / Proliferation",
        fontsize=9)

    # I — Summary
    ax_i = fig.add_subplot(gs_f[2, 2])
    ax_i.axis("off")
    p_panel = (
        surv_result.get("p_panel", np.nan)
        if surv_result else np.nan
    )
    zr = (
        zeb2_result.get("EAC", (np.nan,))[0]
        if zeb2_result else np.nan
    )
    summary = (
        "I — SCRIPT 3 SUMMARY\n"
        "─────────────────────────────\n"
        "Dataset: GSE13898\n"
        "N=118 | EAC=75 | Barr=15 | N=28\n"
        "Platform: Illumina HWG-6 V2\n\n"
        "SURVIVAL:\n"
        f"  OS data: not in GEO soft\n"
        f"  Suppl table needed\n\n"
        "ZEB2-AURKA:\n"
        f"  EAC r={zr:+.4f}\n"
        f"  STAD ref: r=+0.9871\n\n"
        "Framework: OrganismCore\n"
        "Doc 90d | 2026-03-01"
    )
    ax_i.text(
        0.03, 0.97, summary,
        transform=ax_i.transAxes,
        fontsize=7.5,
        verticalalignment="top",
        fontfamily="monospace",
        bbox=dict(
            boxstyle="round",
            facecolor="#f8f8f8",
            edgecolor="#cccccc",
        ),
    )

    out = os.path.join(
        RESULTS_DIR,
        "esca_gse13898_s3.png",
    )
    plt.savefig(out, dpi=150,
                bbox_inches="tight")
    log(f"\n  Figure saved: {out}")
    plt.close()

# ============================================================
# MAIN
# ============================================================

def main():
    log("=" * 65)
    log("ESOPHAGEAL CANCER — SCRIPT 3 (v3)")
    log("Dataset: GSE13898")
    log("Framework: OrganismCore")
    log("Doc: 90d | 2026-03-01")
    log("=" * 65)

    # Downloads
    log("")
    log("=" * 65)
    log("STEP 0: DATA ACQUISITION")
    log("=" * 65)
    ok_mat = download_file(
        MATRIX_URL, MATRIX_FILE, "matrix"
    )
    ok_gpl = download_file(
        GPL_URL, GPL_FILE, "GPL6102"
    )
    ok_soft = download_file(
        SOFT_URL, SOFT_FILE, "soft"
    )
    suppl_file = download_suppl()

    if not ok_mat:
        log("FATAL: Matrix download failed")
        write_log()
        return

    # Build probe map
    if not ok_gpl:
        log("FATAL: No GPL annotation")
        write_log()
        return

    probe_map, gene_to_prob = (
        build_probe_map_from_gpl(GPL_FILE)
    )

    if not probe_map:
        log("FATAL: Probe map empty")
        write_log()
        return

    # Parse matrix
    result = parse_series_matrix(
        MATRIX_FILE, probe_map, gene_to_prob
    )
    if result[0] is None:
        log("FATAL: Parse failed")
        write_log()
        return

    df_genes, meta, char_rows = result

    if len(df_genes.columns) == 0:
        log("FATAL: Zero genes")
        write_log()
        return

    # Classify
    group_series = classify_samples(
        df_genes, meta
    )

    group_order = ["Normal", "Barrett", "EAC"]
    groups = {}
    for g in group_order:
        mask = group_series == g
        if mask.sum() > 0:
            groups[g] = df_genes[mask]

    log("")
    log("=" * 65)
    log("GROUP SUMMARY")
    log("=" * 65)
    for g, df in groups.items():
        log(f"  {g:<12}: {len(df)}")

    eac  = groups.get("EAC", pd.DataFrame())

    # Survival
    surv_df = None
    if ok_soft:
        surv_df = parse_survival_from_soft(
            SOFT_FILE, df_genes
        )
    if suppl_file:
        parse_survival_from_suppl(
            suppl_file, df_genes
        )
    if surv_df is None:
        surv_df = pd.DataFrame({
            "os_time":   np.full(
                len(df_genes), np.nan
            ),
            "os_event":  np.full(
                len(df_genes), np.nan
            ),
            "pathology": [""] * len(df_genes),
        }, index=df_genes.index)

    surv_df["group"] = group_series

    # Run validations
    surv_result = None
    if len(eac) >= 5:
        surv_result = survival_panel_test(
            eac, surv_df, group_series
        )

    zeb2_result = zeb2_aurka_validation(groups)

    depth_dict = progression_geometry(
        groups, group_order
    )

    if len(eac) >= 5 and "EAC" in depth_dict:
        cross_platform_validation(
            eac, depth_dict["EAC"]
        )

    if len(eac) >= 5:
        zeb2_aurka_deep(eac)

    generate_figure(
        groups, depth_dict,
        surv_result, zeb2_result,
        group_order,
    )

    for label, d in depth_dict.items():
        d.to_csv(
            os.path.join(
                RESULTS_DIR,
                f"depth_s3_{label.lower()}.csv",
            ),
            header=["depth_s3"],
        )

    write_log()
    log(f"\n  Log    : {LOG_FILE}")
    log(f"  Output : {RESULTS_DIR}")
    log("\n=== SCRIPT 3 COMPLETE ===")
    log("\nPaste full output for Document 90d.")


if __name__ == "__main__":
    main()
