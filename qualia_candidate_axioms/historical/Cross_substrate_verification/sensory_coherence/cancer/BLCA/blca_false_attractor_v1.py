"""
BLADDER CANCER — FALSE ATTRACTOR ANALYSIS
SCRIPT 1
Dataset: GSE13507
  165 BLCA + 10 normal urothelium
  Platform: GPL6102 Illumina HumanWG-6 V2
  Survival data: YES

FRAMEWORK: OrganismCore Principles-First
Doc: 91a | Date: 2026-03-01

PREDICTIONS LOCKED BEFORE DATA:
(all from 91a prep block)

SWITCH GENES:
  LUMINAL: UPK1B/UPK2/UPK3A DOWN
           CLDN3 DOWN
  BASAL:   GATA3 DOWN
           FOXA1 DOWN
           CDH1  DOWN

FA GENES:
  LUMINAL: FGFR3/ERBB2/CCND1/
           GATA3/FOXA1/PPARG UP
  BASAL:   KRT5/KRT14/EGFR/
           MYC/CD44/VIM/ZEB1 UP

DEPTH DRIVERS:
  L-D1: r(FGFR3, luminal depth) > +0.50
  L-D2: r(PPARG, luminal depth) > +0.40
  L-D3: r(UPK*, luminal depth) < 0
  L-D4: r(CDKN1A, luminal depth) < -0.40
  L-D5: FGFR3+CCND1 combined > FGFR3 alone
  B-D1: r(KRT5, basal depth) > +0.60
  B-D2: r(EGFR, basal depth) > +0.40
  B-D3: r(GATA3, basal depth) < -0.50
  B-D4: r(TP63, basal depth) > +0.50
  B-D5: r(ZEB2, AURKA) > 0.50 in basal

EPIGENETIC:
  EP-1: EZH2 elevated in deep BLCA
  EP-2: HDAC1 elevated in deep luminal
  EP-3: EZH2+HDAC1 combined > alone
  EP-4: KDM6A r < -0.40 with depth
  EP-5: DNMT3A elevated in deep basal

WNT:
  W-1: APC suppressed in deep luminal
  W-2: AXIN2 trending positive deep luminal

CROSS-CANCER TESTS:
  CC-1: TP63 UP in basal, flat luminal
  CC-2: ZEB2-AURKA r = 0.55-0.75 basal
  CC-3: KDM6A DOWN in deep BLCA
  CC-4: CDX2 absent/flat in BLCA
  CC-5: NOTCH1 UP in BLCA (epithelial rule)

DRUG TARGETS (predicted before data):
  LUMINAL: erdafitinib (FGFR3)
           trastuzumab (ERBB2)
           palbociclib (CDK4/6)
           tazemetostat+entinostat
  BASAL:   cetuximab/erlotinib (EGFR)
           sacituzumab (TACSTD2/TROP2)
           enfortumab (PVRL4/Nectin4)
           pembrolizumab (CD274)
           venetoclax (BCL2 — novel)

CLINICAL PANELS (predicted before data):
  LUMINAL: FGFR3(+) / GATA3(+) / UPK2(-)
  BASAL:   KRT5(+) / EGFR(+) / GATA3(-)

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

BASE_DIR    = "./blca_false_attractor/"
RESULTS_DIR = os.path.join(
    BASE_DIR, "results_s1"
)
LOG_FILE = os.path.join(
    RESULTS_DIR, "analysis_log_s1.txt"
)
os.makedirs(RESULTS_DIR, exist_ok=True)

# GSE13507 series matrix
MATRIX_URL  = (
    "https://ftp.ncbi.nlm.nih.gov/geo/series/"
    "GSE13nnn/GSE13507/matrix/"
    "GSE13507_series_matrix.txt.gz"
)
MATRIX_FILE = os.path.join(
    BASE_DIR, "GSE13507_series_matrix.txt.gz"
)

# GPL6102 annotation — reuse from ESCA
# Try ESCA dir first, then download
GPL_FILE_ESCA = os.path.join(
    "./esca_false_attractor/",
    "GPL6102.annot.gz",
)
GPL_FILE = os.path.join(
    BASE_DIR, "GPL6102.annot.gz"
)
GPL_URL  = (
    "https://ftp.ncbi.nlm.nih.gov/geo/platforms/"
    "GPL6nnn/GPL6102/annot/"
    "GPL6102.annot.gz"
)

# GSE13507 soft file for survival
SOFT_URL  = (
    "https://ftp.ncbi.nlm.nih.gov/geo/series/"
    "GSE13nnn/GSE13507/soft/"
    "GSE13507_family.soft.gz"
)
SOFT_FILE = os.path.join(
    BASE_DIR, "GSE13507_family.soft.gz"
)

# ============================================================
# TARGET GENES
# ============================================================

TARGET_GENES = [
    # Urothelial differentiation
    "UPK1A", "UPK1B", "UPK2",  "UPK3A",
    "UPK3B", "CLDN3", "CLDN4", "CLDN7",
    # Luminal identity
    "GATA3", "FOXA1", "PPARG", "ERBB2",
    "ERBB3", "FGFR3", "CCND1", "CDH1",
    "KRT7",  "KRT8",  "KRT18", "KRT19",
    "KRT20",
    # Basal identity
    "KRT5",  "KRT14", "KRT6A", "TP63",
    "CD44",  "S100A8","S100A9","VIM",
    "ZEB1",  "ZEB2",
    # EMT
    "SNAI1", "SNAI2", "TWIST1","CDH2",
    "FN1",
    # RTKs / drug targets
    "EGFR",  "MET",   "FGFR1", "FGFR2",
    "KDR",   "VEGFA", "VEGFR1","PDGFRA",
    "TACSTD2","PVRL4",
    # Immune / checkpoint
    "CD274", "PDCD1", "CD8A",  "FOXP3",
    "CD4",   "CD68",
    # Epigenetic
    "EZH2",  "HDAC1", "HDAC2", "KDM6A",
    "KDM5C", "DNMT3A","TET2",  "ARID1A",
    # Cell cycle
    "CDKN1A","CDKN2A","CDK4",  "CDK6",
    "CCND1", "CCNE1", "CCNB1", "RB1",
    "E2F1",  "E2F3",
    # Proliferation / mitotic
    "MKI67", "TOP2A", "AURKA", "CDC20",
    "PLK1",  "PCNA",  "MCM2",
    # Apoptosis
    "BCL2",  "MCL1",  "BAX",   "BCL2L1",
    "BIRC5",
    # p53 pathway
    "TP53",  "MDM2",  "CDKN2A",
    # Wnt
    "APC",   "CTNNB1","AXIN2", "AXIN1",
    "TCF7L2","LGR5",  "WNT5A",
    # MYC / oncogenes
    "MYC",   "MYCN",  "PIK3CA","KRAS",
    "HRAS",  "NRAS",
    # Stem / basal
    "SOX2",  "SOX4",  "ALDH1A1",
    # Notch
    "NOTCH1","NOTCH2","HES1",  "JAG1",
    # TGF-B
    "TGFB1", "TGFBR2","SMAD2", "SMAD3",
    # Hypoxia
    "HIF1A", "CA9",
    # MMR
    "MLH1",  "MSH2",  "MSH6",
    # FGFR pathway
    "SPRY1", "SPRY2", "DUSP6",
    # Additional urothelial
    "TP73",  "PTEN",  "TSC1",  "RB1",
    "CDKN1B","CDKN2B",
    # Cross-cancer tests
    "CDX2",  "FOXA2", "NKX2-1",
    # Squamous markers (from ESCA)
    "IVL",   "SPRR1A","DSG1",  "DSG3",
    "KRT10", "KRT4",  "KRT13",
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
        return "p=N/A     "
    if p < 0.001:  return f"p={p:.2e} ***"
    elif p < 0.01: return f"p={p:.2e}  **"
    elif p < 0.05: return f"p={p:.4f}   *"
    else:          return f"p={p:.4f}  ns"

def fmt_fc(fc):
    sign = "+" if fc >= 0 else ""
    return f"{sign}{fc:.1f}%"

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

def get_gpl_file():
    """Reuse ESCA GPL6102 if available."""
    if os.path.exists(GPL_FILE_ESCA):
        log(f"  Reusing ESCA GPL6102: "
            f"{GPL_FILE_ESCA}")
        return GPL_FILE_ESCA
    return GPL_FILE if download_file(
        GPL_URL, GPL_FILE, "GPL6102"
    ) else None

# ============================================================
# PROBE MAP — reuse ESCA logic
# GPL6102 col 2 = Gene symbol
# ============================================================

def build_probe_map(gpl_file):
    log("")
    log("=" * 65)
    log("BUILD PROBE MAP — GPL6102")
    log("Reusing ESCA-validated logic")
    log("col 2 = Gene symbol")
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

    in_data  = False
    id_col   = 0
    sym_col  = 2
    n_lines  = 0

    with opener as f:
        for line in f:
            line = line.rstrip()
            if (
                line.startswith("!")
                or line.startswith("^")
                or line.startswith("#")
            ):
                continue

            parts = line.split("\t")
            lower = [
                p.strip().strip('"').lower()
                for p in parts
            ]

            if not in_data:
                if any(
                    h in ["id", "probe_id"]
                    for h in lower
                ):
                    for i, h in enumerate(lower):
                        if h == "id":
                            id_col = i
                        if (
                            h == "gene symbol"
                            or h == "symbol"
                        ):
                            sym_col = i
                    in_data = True
                    log(f"  Header: "
                        f"{[p.strip('\"') for p in parts[:6]]}")
                    log(f"  ID col={id_col} "
                        f"Sym col={sym_col}")
                    continue

            if len(parts) <= max(id_col, sym_col):
                continue

            probe_id = parts[id_col].strip('"')
            symbols  = parts[sym_col].strip('"')
            n_lines += 1

            if not probe_id or symbols in [
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

    log(f"  Lines scanned : {n_lines}")
    log(f"  Probes mapped : {len(probe_map)}")
    log(f"  Genes covered : "
        f"{len(gene_to_prob)}")
    log(f"  Genes found   : "
        f"{sorted(gene_to_prob.keys())}")
    missing = sorted(
        target_set - set(gene_to_prob.keys())
    )
    log(f"  Missing       : {missing[:15]}"
        + ("..." if len(missing) > 15 else ""))

    return probe_map, gene_to_prob

# ============================================================
# PARSE SERIES MATRIX
# ============================================================

def parse_series_matrix(
    filepath, probe_map, gene_to_prob
):
    log("")
    log("=" * 65)
    log("PARSE SERIES MATRIX")
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

            elif (
                "series_matrix_table_begin"
                in line
            ):
                in_table = True
                continue

            elif (
                "series_matrix_table_end"
                in line
            ):
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

    log(f"\n  Characteristics rows: "
        f"{len(char_rows)}")
    for k in list(char_rows.keys())[:5]:
        uniq = list(
            set(v for v in char_rows[k] if v)
        )[:4]
        log(f"    row {k}: {uniq}")

    return df_genes, meta, char_rows

# ============================================================
# CLASSIFY SAMPLES
# GSE13507: Normal urothelium vs BLCA
# Subtype classification:
#   Luminal / Basal from expression
#   Primary classification by title/chars
# ============================================================

def classify_samples(
    df_genes, meta, char_rows
):
    log("")
    log("=" * 65)
    log("CLASSIFY SAMPLES")
    log("Normal / Tumor")
    log("Subtype by expression: Luminal/Basal")
    log("=" * 65)

    primary = []
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
            "normal", "nontumor",
            "non-tumor", "non tumor",
            "urothelium", "adjacent",
        ]):
            primary.append("Normal")
        elif any(x in title for x in [
            "tumor", "tumour", "cancer",
            "blca", "bladder", "carcinoma",
            "tcc", "urothelial",
        ]):
            primary.append("Tumor")
        else:
            primary.append("Unknown")

    ps = pd.Series(primary,
                   index=df_genes.index)

    # If title-based fails, use char_rows
    n_unk = (ps == "Unknown").sum()
    if n_unk > 5:
        log(f"  {n_unk} Unknown — trying "
            f"characteristics...")
        for k, vals in char_rows.items():
            non_empty = [
                v for v in vals if v
            ]
            if not non_empty:
                continue
            ex = non_empty[0].lower()
            if any(
                x in ex for x in [
                    "tumor", "normal",
                    "tissue", "type",
                ]
            ):
                log(f"  Char row {k}: {ex[:60]}")
                for i, v in enumerate(
                    vals[:len(ps)]
                ):
                    if ps.iloc[i] == "Unknown":
                        vl = v.lower()
                        if any(
                            x in vl for x in [
                                "normal",
                                "nontumor",
                                "adjacent",
                            ]
                        ):
                            ps.iloc[i] = "Normal"
                        elif any(
                            x in vl for x in [
                                "tumor",
                                "cancer",
                                "carcinoma",
                            ]
                        ):
                            ps.iloc[i] = "Tumor"

    log(f"\n  Primary classification:")
    for g, n in ps.value_counts().items():
        log(f"    {g}: {n}")

    log(f"\n  First 15 samples:")
    for s in df_genes.index[:15]:
        title = ""
        if (
            meta is not None
            and "title" in meta.columns
            and s in meta.index
        ):
            title = str(
                meta.loc[s, "title"]
            )[:50]
        log(f"    {s[:12]:<12} → "
            f"{ps[s]:<10} {title}")

    return ps

# ============================================================
# SUBTYPE CLASSIFICATION
# Luminal vs Basal from expression
# Using GATA3 and KRT5 as separators
# ============================================================

def classify_subtypes(
    df_genes, primary_series
):
    log("")
    log("=" * 65)
    log("SUBTYPE CLASSIFICATION")
    log("Luminal vs Basal")
    log("Primary markers: GATA3 / KRT5")
    log("=" * 65)

    tumor_mask = primary_series == "Tumor"
    tumor_df   = df_genes[tumor_mask]

    if len(tumor_df) < 5:
        log("  Insufficient tumor samples")
        return primary_series.copy()

    gc = list(tumor_df.columns)

    # Use GATA3 and KRT5 for subtyping
    # Luminal = GATA3-high / KRT5-low
    # Basal   = KRT5-high  / GATA3-low

    g3_present  = "GATA3" in gc
    k5_present  = "KRT5"  in gc
    fp1_present = "FOXA1" in gc

    log(f"  GATA3 present: {g3_present}")
    log(f"  KRT5  present: {k5_present}")
    log(f"  FOXA1 present: {fp1_present}")

    subtype = primary_series.copy()

    if g3_present and k5_present:
        g3_vals = tumor_df["GATA3"].values
        k5_vals = tumor_df["KRT5"].values

        # Normalise each to 0-1
        g3_n = norm01(g3_vals).values
        k5_n = norm01(k5_vals).values

        # Luminal score = GATA3 - KRT5
        lum_score = g3_n - k5_n

        # Median split
        med = np.median(lum_score)
        lum_idx = tumor_df.index[
            lum_score >= med
        ]
        bas_idx = tumor_df.index[
            lum_score < med
        ]

        for idx in lum_idx:
            subtype[idx] = "Luminal"
        for idx in bas_idx:
            subtype[idx] = "Basal"

        log(f"\n  Luminal (GATA3-high/KRT5-low):"
            f" n={len(lum_idx)}")
        log(f"  Basal   (KRT5-high/GATA3-low):"
            f" n={len(bas_idx)}")
        log(f"  Normal  : "
            f"{(subtype=='Normal').sum()}")

        # Report separator statistics
        _, p_g3 = safe_mwu(
            tumor_df.loc[lum_idx, "GATA3"].values,
            tumor_df.loc[bas_idx, "GATA3"].values,
            "two-sided",
        )
        _, p_k5 = safe_mwu(
            tumor_df.loc[lum_idx, "KRT5"].values,
            tumor_df.loc[bas_idx, "KRT5"].values,
            "two-sided",
        )
        log(f"\n  Separator validation:")
        log(f"  GATA3 Luminal vs Basal: "
            f"{fmt_p(p_g3)}")
        log(f"  KRT5  Luminal vs Basal: "
            f"{fmt_p(p_k5)}")
        log(f"\n  Mean expression by subtype:")
        log(f"  {'Gene':<8} {'Normal':>9} "
            f"{'Luminal':>9} {'Basal':>9}")
        for gene in [
            "GATA3", "KRT5", "KRT14",
            "FOXA1", "FGFR3", "EGFR",
            "TP63",  "UPK2",
        ]:
            if gene not in gc:
                continue
            norm_v = (
                df_genes[
                    primary_series == "Normal"
                ][gene].mean()
                if (primary_series == "Normal").sum() > 0
                else np.nan
            )
            lum_v = (
                tumor_df.loc[lum_idx, gene].mean()
                if gene in tumor_df.columns
                else np.nan
            )
            bas_v = (
                tumor_df.loc[bas_idx, gene].mean()
                if gene in tumor_df.columns
                else np.nan
            )
            log(f"  {gene:<8} {norm_v:>9.4f} "
                f"{lum_v:>9.4f} {bas_v:>9.4f}")
    else:
        log("  GATA3 or KRT5 missing — "
            "cannot subtype")
        log("  All tumor = Tumor (unclassified)")

    log(f"\n  Final group counts:")
    for g, n in subtype.value_counts().items():
        log(f"    {g}: {n}")

    return subtype

# ============================================================
# FOLD CHANGE TABLE
# Tumor vs Normal, Luminal vs Normal,
# Basal vs Normal
# ============================================================

def fold_change_analysis(
    df_genes, subtype_series
):
    log("")
    log("=" * 65)
    log("FOLD CHANGE ANALYSIS")
    log("vs Normal urothelium")
    log("=" * 65)

    groups = {}
    for g in ["Normal", "Luminal",
              "Basal", "Tumor"]:
        mask = subtype_series == g
        if mask.sum() > 0:
            groups[g] = df_genes[mask]

    gc = list(df_genes.columns)
    norm = groups.get("Normal",
                      pd.DataFrame())

    if len(norm) == 0:
        log("  No Normal samples — skip FC")
        return {}

    results = {}

    log(f"\n  Normal n={len(norm)}")
    for g in ["Luminal", "Basal", "Tumor"]:
        if g in groups:
            log(f"  {g} n={len(groups[g])}")

    # Compute FC for all genes
    for gene in sorted(gc):
        norm_mean = norm[gene].mean()
        if np.isnan(norm_mean) or norm_mean == 0:
            continue

        gene_results = {"normal_mean": norm_mean}
        for g in ["Luminal", "Basal"]:
            if g not in groups:
                continue
            grp = groups[g]
            if gene not in grp.columns:
                continue
            grp_mean = grp[gene].mean()
            fc = (
                (grp_mean - norm_mean)
                / abs(norm_mean) * 100
            )
            _, p = safe_mwu(
                grp[gene].values,
                norm[gene].values,
                "two-sided",
            )
            gene_results[g] = {
                "mean": grp_mean,
                "fc": fc,
                "p": p,
            }
        results[gene] = gene_results

    # Print predicted switch and FA genes
    # LUMINAL
    log(f"\n  LUMINAL vs NORMAL:")
    log(f"  {'Gene':<12} {'Normal':>9} "
        f"{'Luminal':>9} {'FC%':>9}  p-value")
    log(f"  {'-'*60}")

    luminal_targets = [
        # Predicted switch (DOWN)
        ("UPK1B",  "switch-DOWN"),
        ("UPK2",   "switch-DOWN"),
        ("UPK3A",  "switch-DOWN"),
        ("CLDN3",  "switch-DOWN"),
        # Predicted FA (UP)
        ("FGFR3",  "FA-UP"),
        ("ERBB2",  "FA-UP"),
        ("CCND1",  "FA-UP"),
        ("GATA3",  "FA-UP"),
        ("FOXA1",  "FA-UP"),
        ("PPARG",  "FA-UP"),
        ("CDH1",   "FA-UP"),
        ("KRT20",  "FA-UP"),
        # Epigenetic
        ("EZH2",   "epigenetic"),
        ("HDAC1",  "epigenetic"),
        ("KDM6A",  "epigenetic"),
        # Cross-cancer tests
        ("NOTCH1", "CC-5"),
        ("CDX2",   "CC-4"),
        ("TP63",   "CC-1"),
        # Drug targets
        ("PVRL4",  "drug-enfortumab"),
        ("TACSTD2","drug-sacituzumab"),
        ("CD274",  "checkpoint"),
    ]

    for gene, role in luminal_targets:
        if gene not in results:
            continue
        r = results[gene]
        if "Luminal" not in r:
            continue
        nm = r["normal_mean"]
        lm = r["Luminal"]["mean"]
        fc = r["Luminal"]["fc"]
        p  = r["Luminal"]["p"]
        sig = (
            "***" if p < 0.001
            else "**" if p < 0.01
            else "*"  if p < 0.05
            else "ns"
        )
        log(f"  {gene:<12} {nm:>9.4f} "
            f"{lm:>9.4f} {fmt_fc(fc):>9}  "
            f"{fmt_p(p)}  {role}")

    # BASAL
    log(f"\n  BASAL vs NORMAL:")
    log(f"  {'Gene':<12} {'Normal':>9} "
        f"{'Basal':>9} {'FC%':>9}  p-value")
    log(f"  {'-'*60}")

    basal_targets = [
        # Predicted switch (DOWN)
        ("GATA3",  "switch-DOWN"),
        ("FOXA1",  "switch-DOWN"),
        ("CDH1",   "switch-DOWN"),
        # Predicted FA (UP)
        ("KRT5",   "FA-UP"),
        ("KRT14",  "FA-UP"),
        ("EGFR",   "FA-UP"),
        ("MYC",    "FA-UP"),
        ("CD44",   "FA-UP"),
        ("VIM",    "FA-UP"),
        ("ZEB1",   "FA-UP"),
        ("TP63",   "CC-1-UP"),
        ("S100A8", "FA-UP"),
        # EMT
        ("SNAI1",  "EMT"),
        ("SNAI2",  "EMT"),
        ("TWIST1", "EMT"),
        # Epigenetic
        ("EZH2",   "epigenetic"),
        ("HDAC1",  "epigenetic"),
        ("KDM6A",  "epigenetic"),
        # ZEB2
        ("ZEB2",   "EMT/ZEB"),
        ("AURKA",  "mitotic"),
        # Drug targets
        ("TACSTD2","drug-sacituzumab"),
        ("CD274",  "checkpoint"),
        ("BCL2",   "drug-venetoclax"),
        # Cross-cancer
        ("NOTCH1", "CC-5"),
        ("CDX2",   "CC-4"),
    ]

    for gene, role in basal_targets:
        if gene not in results:
            continue
        r = results[gene]
        if "Basal" not in r:
            continue
        nm = r["normal_mean"]
        bm = r["Basal"]["mean"]
        fc = r["Basal"]["fc"]
        p  = r["Basal"]["p"]
        log(f"  {gene:<12} {nm:>9.4f} "
            f"{bm:>9.4f} {fmt_fc(fc):>9}  "
            f"{fmt_p(p)}  {role}")

    return results

# ============================================================
# DEPTH SCORE
# ============================================================

# Switch and FA gene sets
LUMINAL_SWITCH = [
    "UPK1B", "UPK2", "UPK3A", "CLDN3",
]
LUMINAL_FA = [
    "FGFR3", "ERBB2", "CCND1",
    "GATA3", "FOXA1", "PPARG",
]
BASAL_SWITCH = [
    "GATA3", "FOXA1", "CDH1",
]
BASAL_FA = [
    "KRT5", "KRT14", "EGFR",
    "MYC", "CD44", "VIM",
]

def build_depth_score(
    df, switch, fa, label
):
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
# DEPTH CORRELATIONS
# ============================================================

def depth_correlations(
    df, depth, label, n_top=15
):
    log("")
    log("=" * 65)
    log(f"DEPTH CORRELATIONS — {label}")
    log("=" * 65)

    gc = list(df.columns)
    corrs = []
    for gene in gc:
        rv, pv = safe_pearsonr(
            depth.values,
            df[gene].values,
        )
        if not np.isnan(rv):
            corrs.append((gene, rv, pv))

    corrs.sort(
        key=lambda x: x[1], reverse=True
    )

    log(f"\n  TOP {n_top} POSITIVE "
        f"(UP in deep {label}):")
    log(f"  {'Gene':<12} {'r':>8}  p-value")
    log(f"  {'-'*40}")
    for g, r, p in corrs[:n_top]:
        log(f"  {g:<12} {r:>+8.4f}  {fmt_p(p)}")

    log(f"\n  TOP {n_top} NEGATIVE "
        f"(DOWN in deep {label}):")
    log(f"  {'Gene':<12} {'r':>8}  p-value")
    log(f"  {'-'*40}")
    for g, r, p in corrs[-n_top:][::-1]:
        log(f"  {g:<12} {r:>+8.4f}  {fmt_p(p)}")

    return corrs

# ============================================================
# PREDICTION TESTS
# ============================================================

def test_depth_predictions(
    lum_df, bas_df,
    lum_depth, bas_depth,
):
    log("")
    log("=" * 65)
    log("PREDICTION TESTS")
    log("=" * 65)

    gc_l = list(lum_df.columns)
    gc_b = list(bas_df.columns)

    predictions = [
        # (label, gene, subtype_df, depth,
        #  direction, threshold, pred_id)
        ("L-D1", "FGFR3",  lum_df, lum_depth,
         "+", 0.50),
        ("L-D2", "PPARG",  lum_df, lum_depth,
         "+", 0.40),
        ("L-D3", "UPK2",   lum_df, lum_depth,
         "-", 0.00),
        ("L-D4", "CDKN1A", lum_df, lum_depth,
         "-", -0.40),
        ("B-D1", "KRT5",   bas_df, bas_depth,
         "+", 0.60),
        ("B-D2", "EGFR",   bas_df, bas_depth,
         "+", 0.40),
        ("B-D3", "GATA3",  bas_df, bas_depth,
         "-", -0.50),
        ("B-D4", "TP63",   bas_df, bas_depth,
         "+", 0.50),
        ("EP-1", "EZH2",   lum_df, lum_depth,
         "+", 0.30),
        ("EP-2", "HDAC1",  lum_df, lum_depth,
         "+", 0.30),
        ("EP-4", "KDM6A",  lum_df, lum_depth,
         "-", -0.40),
        ("W-1",  "APC",    lum_df, lum_depth,
         "-", -0.30),
        ("W-2",  "AXIN2",  lum_df, lum_depth,
         "+", 0.00),
        ("CC-1-L","TP63",  lum_df, lum_depth,
         "+", -0.10),
        ("CC-3", "KDM6A",  bas_df, bas_depth,
         "-", -0.40),
    ]

    log(f"\n  {'Pred':<8} {'Gene':<10} "
        f"{'Subtype':<10} {'r':>8}  "
        f"p-value        Threshold  Result")
    log(f"  {'-'*72}")

    for (
        pred_id, gene, df_, depth_,
        direction, threshold,
    ) in predictions:
        subtype_label = (
            "Luminal" if df_ is lum_df
            else "Basal"
        )
        gc_ = list(df_.columns)
        if gene not in gc_:
            log(f"  {pred_id:<8} {gene:<10} "
                f"{subtype_label:<10} "
                f"NOT IN MATRIX")
            continue

        rv, pv = safe_pearsonr(
            depth_.values,
            df_[gene].values,
        )
        if not np.isnan(rv):
            if direction == "+":
                ok = rv >= threshold
            else:
                ok = rv <= threshold
            result = "✓" if ok else "✗"
            thr_str = (
                f"{'≥' if direction=='+' else '≤'}"
                f"{threshold}"
            )
        else:
            ok     = False
            result = "?"
            thr_str = "N/A"

        log(
            f"  {pred_id:<8} {gene:<10} "
            f"{subtype_label:<10} "
            f"{rv:>+8.4f}  "
            f"{fmt_p(pv):>14}  "
            f"{thr_str:>10}  {result}"
            if not np.isnan(rv)
            else
            f"  {pred_id:<8} {gene:<10} "
            f"{subtype_label:<10} N/A"
        )

    # L-D5: FGFR3+CCND1 combined vs FGFR3
    log(f"\n  L-D5: FGFR3+CCND1 combined "
        f"vs FGFR3 alone")
    if (
        "FGFR3" in gc_l
        and "CCND1" in gc_l
    ):
        r_f3, _ = safe_pearsonr(
            lum_depth.values,
            lum_df["FGFR3"].values,
        )
        combined = norm01(
            lum_df["FGFR3"].values
        ) + norm01(lum_df["CCND1"].values)
        r_comb, _ = safe_pearsonr(
            lum_depth.values,
            combined.values,
        )
        log(f"  r(FGFR3)        = {r_f3:+.4f}")
        log(f"  r(FGFR3+CCND1)  = {r_comb:+.4f}")
        if not np.isnan(r_comb) and not np.isnan(r_f3):
            if abs(r_comb) > abs(r_f3):
                log(f"  L-D5 CONFIRMED ✓")
            else:
                log(f"  L-D5 NOT CONFIRMED ✗")

    # EP-3: EZH2+HDAC1 combined
    log(f"\n  EP-3: EZH2+HDAC1 combined "
        f"vs individual")
    if (
        "EZH2" in gc_l
        and "HDAC1" in gc_l
    ):
        r_ezh2, _ = safe_pearsonr(
            lum_depth.values,
            lum_df["EZH2"].values,
        )
        r_hdac1, _ = safe_pearsonr(
            lum_depth.values,
            lum_df["HDAC1"].values,
        )
        combined = norm01(
            lum_df["EZH2"].values
        ) + norm01(lum_df["HDAC1"].values)
        r_comb, _ = safe_pearsonr(
            lum_depth.values,
            combined.values,
        )
        log(f"  r(EZH2)          = {r_ezh2:+.4f}")
        log(f"  r(HDAC1)         = {r_hdac1:+.4f}")
        log(f"  r(EZH2+HDAC1)    = {r_comb:+.4f}")
        if not np.isnan(r_comb):
            if abs(r_comb) > max(
                abs(r_ezh2), abs(r_hdac1)
            ):
                log(f"  EP-3 CONFIRMED ✓")
            else:
                log(f"  EP-3 NOT CONFIRMED ✗")

    # B-D5: ZEB2-AURKA coupling in basal
    log(f"\n  B-D5: ZEB2-AURKA coupling "
        f"in basal BLCA")
    log(f"  STAD reference: r=+0.9871")
    log(f"  EAC reference:  r=+0.4675")
    log(f"  Prediction:     r=0.55–0.75")
    if (
        "ZEB2" in gc_b
        and "AURKA" in gc_b
    ):
        rv, pv = safe_pearsonr(
            bas_df["ZEB2"].values,
            bas_df["AURKA"].values,
        )
        log(f"  r(ZEB2,AURKA) basal = "
            f"{rv:+.4f}  {fmt_p(pv)}")
        if not np.isnan(rv):
            if 0.55 <= rv <= 0.75:
                log(f"  B-D5 CONFIRMED ✓ "
                    f"(r in 0.55–0.75)")
            elif rv > 0.50:
                log(f"  B-D5 PARTIAL ⚠️ "
                    f"(r>0.50 not in range)")
            elif rv > 0:
                log(f"  B-D5 PARTIAL ⚠️ "
                    f"(r>0 but <0.50)")
            else:
                log(f"  B-D5 NOT CONFIRMED ✗")
    else:
        log(f"  ZEB2 or AURKA missing in basal")

    # CC-4: CDX2 absent/flat in BLCA
    log(f"\n  CC-4: CDX2 in BLCA "
        f"(predicted absent/flat)")
    for subtype_label, df_, depth_ in [
        ("Luminal", lum_df, lum_depth),
        ("Basal",   bas_df, bas_depth),
    ]:
        gc_ = list(df_.columns)
        if "CDX2" not in gc_:
            log(f"  {subtype_label}: "
                f"CDX2 NOT IN MATRIX")
            continue
        mean_cdx2 = df_["CDX2"].mean()
        rv, pv    = safe_pearsonr(
            depth_.values,
            df_["CDX2"].values,
        )
        log(f"  {subtype_label}: "
            f"CDX2 mean={mean_cdx2:.4f} "
            f"r={rv:+.4f}  {fmt_p(pv)}")

    # CC-5: NOTCH1 direction
    log(f"\n  CC-5: NOTCH1 in BLCA "
        f"(predicted UP — epithelial rule)")
    for subtype_label, df_ in [
        ("Luminal", lum_df),
        ("Basal",   bas_df),
    ]:
        gc_ = list(df_.columns)
        if "NOTCH1" not in gc_:
            log(f"  {subtype_label}: "
                f"NOTCH1 NOT IN MATRIX")
            continue
        mean_n1 = df_["NOTCH1"].mean()
        log(f"  {subtype_label}: "
            f"NOTCH1 mean={mean_n1:.4f}")

# ============================================================
# CLINICAL PANEL DERIVATION
# ============================================================

def derive_clinical_panels(
    lum_df, bas_df,
    lum_depth, bas_depth,
):
    log("")
    log("=" * 65)
    log("CLINICAL PANEL DERIVATION")
    log("3-gene IHC-deployable panels")
    log("Predicted before data:")
    log("  LUMINAL: FGFR3(+)/GATA3(+)/UPK2(-)")
    log("  BASAL:   KRT5(+)/EGFR(+)/GATA3(-)")
    log("=" * 65)

    for label, df_, depth_ in [
        ("LUMINAL", lum_df, lum_depth),
        ("BASAL",   bas_df, bas_depth),
    ]:
        gc_ = list(df_.columns)
        log(f"\n  {label} PANEL DERIVATION:")

        # Top positive correlates
        log(f"  Top positive (IHC elevated):")
        log(f"  {'Gene':<10} {'r':>8}  p-value")
        pos_corrs = []
        for gene in gc_:
            rv, pv = safe_pearsonr(
                depth_.values,
                df_[gene].values,
            )
            if not np.isnan(rv) and rv > 0:
                pos_corrs.append((gene, rv, pv))
        pos_corrs.sort(
            key=lambda x: x[1], reverse=True
        )
        for g, r, p in pos_corrs[:5]:
            log(f"  {g:<10} {r:>+8.4f}  "
                f"{fmt_p(p)}")

        log(f"  Top negative (IHC suppressed):")
        neg_corrs = [
            (g, r, p)
            for g, r, p in pos_corrs[::-1]
            if r < 0
        ]
        for g, r, p in neg_corrs[:5]:
            log(f"  {g:<10} {r:>+8.4f}  "
                f"{fmt_p(p)}")

        # Test predicted panel
        if label == "LUMINAL":
            panel_genes = [
                ("FGFR3", "+"),
                ("GATA3", "+"),
                ("UPK2",  "-"),
            ]
        else:
            panel_genes = [
                ("KRT5",  "+"),
                ("EGFR",  "+"),
                ("GATA3", "-"),
            ]

        avail = [
            (g, d) for g, d in panel_genes
            if g in gc_
        ]
        log(f"\n  PREDICTED PANEL: "
            f"{[(g,d) for g,d in panel_genes]}")
        log(f"  Available: "
            f"{[(g,d) for g,d in avail]}")

        if len(avail) >= 2:
            parts = []
            for gene, direction in avail:
                ns = norm01(df_[gene].values)
                if direction == "-":
                    parts.append(1 - ns)
                else:
                    parts.append(ns)
            panel_score = np.mean(
                parts, axis=0
            )
            rv, pv = safe_pearsonr(
                depth_.values,
                panel_score,
            )
            log(f"  Panel r with depth = "
                f"{rv:+.4f}  {fmt_p(pv)}")

        # Derive data-driven panel
        top3_pos = [
            g for g, r, p in pos_corrs[:3]
        ]
        top3_neg = [
            g for g, r, p in pos_corrs[-3:]
            if r < 0
        ]
        log(f"\n  DATA-DRIVEN PANEL:")
        log(f"  Top 3 positive: {top3_pos}")
        log(f"  Top 3 negative: {top3_neg}")

        if top3_pos:
            parts = []
            for gene in top3_pos[:2]:
                parts.append(
                    norm01(df_[gene].values)
                )
            if top3_neg:
                parts.append(
                    1 - norm01(
                        df_[top3_neg[0]].values
                    )
                )
            if parts:
                score = np.mean(parts, axis=0)
                rv, pv = safe_pearsonr(
                    depth_.values, score
                )
                log(f"  Data panel r = "
                    f"{rv:+.4f}  {fmt_p(pv)}")

# ============================================================
# SURVIVAL ANALYSIS
# ============================================================

def parse_survival(soft_file, df_genes):
    log("")
    log("=" * 65)
    log("PARSE SURVIVAL — SOFT FILE")
    log(f"  File: {soft_file}")
    log("=" * 65)

    if not os.path.exists(soft_file):
        log("  Soft file missing — skip")
        return None

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
                    cur_chars[
                        k.strip().lower()
                    ] = v.strip()
                else:
                    cur_chars[
                        f"c{len(cur_chars)}"
                    ] = val

    if cur_sample:
        sample_data[cur_sample] = dict(cur_chars)

    log(f"  Sample records: {len(sample_data)}")

    # Show all characteristic keys
    all_keys = set()
    for d in sample_data.values():
        all_keys.update(d.keys())
    log(f"  Characteristic keys:")
    for k in sorted(all_keys):
        ex = next(
            (d[k] for d in sample_data.values()
             if k in d), ""
        )
        log(f"    '{k}': {ex[:60]}")

    # Parse time and event
    os_time  = {}
    os_event = {}

    time_re  = re.compile(
        r"(?:os|survival|time|follow|month)",
        re.I
    )
    event_re = re.compile(
        r"(?:vital|status|event|dead|alive|"
        r"death|censor|outcome)",
        re.I
    )

    for gsm, chars in sample_data.items():
        for k, v in chars.items():
            if time_re.search(k):
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
            if event_re.search(k):
                vl = str(v).lower()
                if any(
                    x in vl for x in [
                        "dead", "1", "yes",
                        "died", "deceased",
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

    log(f"\n  OS time found  : {len(os_time)}")
    log(f"  OS event found : {len(os_event)}")

    if os_time:
        times = list(os_time.values())
        log(f"  Time range: {min(times):.1f}–"
            f"{max(times):.1f}")

    t_arr = np.full(len(df_genes), np.nan)
    e_arr = np.full(len(df_genes), np.nan)

    for i, gsm in enumerate(df_genes.index):
        if gsm in os_time:
            t_arr[i] = os_time[gsm]
        if gsm in os_event:
            e_arr[i] = os_event[gsm]

    surv_df = pd.DataFrame({
        "os_time":  t_arr,
        "os_event": e_arr,
    }, index=df_genes.index)

    log(f"  Mapped: time={( ~np.isnan(t_arr)).sum()} "
        f"event={(~np.isnan(e_arr)).sum()}")

    return surv_df


def survival_analysis(
    df, depth, surv_df, label
):
    log("")
    log("=" * 65)
    log(f"SURVIVAL ANALYSIS — {label}")
    log("=" * 65)

    idx = df.index.intersection(surv_df.index)
    if len(idx) == 0:
        log("  No overlap with survival data")
        return None

    d    = depth.loc[idx]
    surv = surv_df.loc[idx]
    t    = surv["os_time"].values
    e    = surv["os_event"].values

    valid = (
        ~np.isnan(t) & ~np.isnan(e)
        & (t > 0)
    )
    log(f"  n={len(idx)}, "
        f"valid survival={valid.sum()}")

    if valid.sum() < 10:
        log("  Insufficient survival data")
        return None

    t_v = t[valid]
    e_v = e[valid]
    d_v = d.values[valid]

    log(f"  OS: {t_v.min():.1f}–"
        f"{t_v.max():.1f} months")
    log(f"  Events: {int(e_v.sum())} / "
        f"{len(e_v)}")

    # Depth vs OS
    med = np.median(d_v)
    hi  = d_v >= med
    lo  = ~hi

    try:
        res = logrank_test(
            t_v[hi], t_v[lo],
            e_v[hi], e_v[lo],
        )
        p = res.p_value
    except Exception:
        p = np.nan

    log(f"\n  Depth score vs OS:")
    log(f"  High depth (n={hi.sum()}): "
        f"mean OS={t_v[hi].mean():.1f}")
    log(f"  Low  depth (n={lo.sum()}): "
        f"mean OS={t_v[lo].mean():.1f}")
    log(f"  Log-rank p = {fmt_p(p)}")

    if not np.isnan(p) and p < 0.05:
        log(f"  Depth predicts OS ✓")
    elif not np.isnan(p):
        log(f"  Depth does not predict OS ✗")

    return {
        "t": t_v, "e": e_v,
        "hi": hi, "lo": lo,
        "p": p, "label": label,
    }

# ============================================================
# ZEB2-AURKA CROSS-CANCER TEST
# ============================================================

def zeb2_aurka_test(groups):
    log("")
    log("=" * 65)
    log("ZEB2-AURKA CROSS-CANCER TEST")
    log("STAD r=+0.9871 | EAC r=+0.4675")
    log("Basal BLCA prediction: r=0.55-0.75")
    log("=" * 65)

    results = {}
    for label in [
        "Normal", "Luminal", "Basal"
    ]:
        if label not in groups:
            continue
        df = groups[label]
        gc = list(df.columns)
        if "ZEB2" not in gc or "AURKA" not in gc:
            log(f"  {label}: ZEB2 or AURKA missing")
            continue
        rv, pv = safe_pearsonr(
            df["ZEB2"].values,
            df["AURKA"].values,
        )
        log(f"  {label} (n={len(df)}): "
            f"r(ZEB2,AURKA)={rv:+.4f}  "
            f"{fmt_p(pv)}")
        results[label] = (rv, pv)

    return results

# ============================================================
# GENERATE FIGURE
# ============================================================

def generate_figure(
    groups, lum_depth, bas_depth,
    surv_lum, surv_bas,
    zeb2_results,
):
    log("")
    log("--- Generating Script 1 figure ---")

    fig = plt.figure(figsize=(28, 22))
    fig.suptitle(
        "Bladder Cancer — False Attractor "
        "Analysis\n"
        "Script 1 | GSE13507 | "
        "Luminal + Basal BLCA\n"
        "OrganismCore | Doc 91a | 2026-03-01",
        fontsize=10, fontweight="bold",
        y=0.99,
    )

    gs_f = gridspec.GridSpec(
        3, 3, figure=fig,
        hspace=0.55, wspace=0.45,
    )

    COLORS = {
        "Normal":  "#27ae60",
        "Luminal": "#2980b9",
        "Basal":   "#e74c3c",
        "Tumor":   "#95a5a6",
    }

    def gc_col(g):
        return COLORS.get(g, "#95a5a6")

    group_order = [
        "Normal", "Luminal", "Basal"
    ]

    # A — GATA3 vs KRT5 scatter
    ax_a = fig.add_subplot(gs_f[0, 0])
    for label in group_order:
        if label not in groups:
            continue
        df = groups[label]
        gc = list(df.columns)
        if "GATA3" in gc and "KRT5" in gc:
            ax_a.scatter(
                df["GATA3"].values,
                df["KRT5"].values,
                alpha=0.5, s=25,
                color=gc_col(label),
                label=f"{label} "
                      f"(n={len(df)})",
            )
    ax_a.set_xlabel("GATA3", fontsize=8)
    ax_a.set_ylabel("KRT5", fontsize=8)
    ax_a.set_title(
        "A — Subtype Separator\n"
        "GATA3 vs KRT5",
        fontsize=9,
    )
    ax_a.legend(fontsize=7)

    # B — Luminal depth
    ax_b = fig.add_subplot(gs_f[0, 1])
    if lum_depth is not None:
        key_genes = [
            "FGFR3", "GATA3", "FOXA1",
            "PPARG", "UPK2",
        ]
        all_gc = set()
        for df in groups.values():
            all_gc.update(df.columns)
        avail = [
            g for g in key_genes
            if g in all_gc
        ]
        if avail:
            x = np.arange(len(avail))
            w = 0.35
            for i, label in enumerate(
                ["Normal", "Luminal"]
            ):
                if label not in groups:
                    continue
                df = groups[label]
                means = [
                    df[g].mean()
                    if g in df.columns else 0
                    for g in avail
                ]
                ax_b.bar(
                    x + (i - 0.5) * w,
                    means, w,
                    color=gc_col(label),
                    label=label,
                    alpha=0.85,
                )
            ax_b.set_xticks(x)
            ax_b.set_xticklabels(
                avail, rotation=45,
                ha="right", fontsize=7,
            )
            ax_b.legend(fontsize=7)
    ax_b.set_title(
        "B — Luminal FA Genes\nvs Normal",
        fontsize=9,
    )

    # C — Basal markers
    ax_c = fig.add_subplot(gs_f[0, 2])
    key_b = [
        "KRT5", "KRT14", "EGFR",
        "TP63", "CD44",
    ]
    all_gc = set()
    for df in groups.values():
        all_gc.update(df.columns)
    avail_b = [g for g in key_b if g in all_gc]
    if avail_b:
        x = np.arange(len(avail_b))
        w = 0.35
        for i, label in enumerate(
            ["Normal", "Basal"]
        ):
            if label not in groups:
                continue
            df = groups[label]
            means = [
                df[g].mean()
                if g in df.columns else 0
                for g in avail_b
            ]
            ax_c.bar(
                x + (i - 0.5) * w,
                means, w,
                color=gc_col(label),
                label=label,
                alpha=0.85,
            )
        ax_c.set_xticks(x)
        ax_c.set_xticklabels(
            avail_b, rotation=45,
            ha="right", fontsize=7,
        )
        ax_c.legend(fontsize=7)
    ax_c.set_title(
        "C — Basal FA Genes\nvs Normal",
        fontsize=9,
    )

    # D — KM Luminal
    ax_d = fig.add_subplot(gs_f[1, 0])
    if surv_lum is not None:
        t  = surv_lum["t"]
        e  = surv_lum["e"]
        hi = surv_lum["hi"]
        lo = surv_lum["lo"]
        p  = surv_lum["p"]
        kmf = KaplanMeierFitter()
        kmf.fit(
            t[hi], e[hi],
            label=f"Deep (n={hi.sum()})",
        )
        kmf.plot_survival_function(
            ax=ax_d, color="#e74c3c",
            ci_show=False,
        )
        kmf.fit(
            t[lo], e[lo],
            label=f"Shallow (n={lo.sum()})",
        )
        kmf.plot_survival_function(
            ax=ax_d, color="#27ae60",
            ci_show=False,
        )
        p_str = (
            f"p={p:.4f}"
            if not np.isnan(p) else "N/A"
        )
        ax_d.set_title(
            f"D — KM: Luminal Depth\n{p_str}",
            fontsize=9,
        )
        ax_d.legend(fontsize=7)
    else:
        ax_d.text(
            0.5, 0.5,
            "Luminal survival\nnot available",
            ha="center", va="center",
            transform=ax_d.transAxes,
        )
        ax_d.set_title(
            "D — KM: Luminal Depth",
            fontsize=9,
        )
    ax_d.set_xlabel("Time", fontsize=8)

    # E — KM Basal
    ax_e = fig.add_subplot(gs_f[1, 1])
    if surv_bas is not None:
        t  = surv_bas["t"]
        e  = surv_bas["e"]
        hi = surv_bas["hi"]
        lo = surv_bas["lo"]
        p  = surv_bas["p"]
        kmf = KaplanMeierFitter()
        kmf.fit(
            t[hi], e[hi],
            label=f"Deep (n={hi.sum()})",
        )
        kmf.plot_survival_function(
            ax=ax_e, color="#e74c3c",
            ci_show=False,
        )
        kmf.fit(
            t[lo], e[lo],
            label=f"Shallow (n={lo.sum()})",
        )
        kmf.plot_survival_function(
            ax=ax_e, color="#27ae60",
            ci_show=False,
        )
        p_str = (
            f"p={p:.4f}"
            if not np.isnan(p) else "N/A"
        )
        ax_e.set_title(
            f"E — KM: Basal Depth\n{p_str}",
            fontsize=9,
        )
        ax_e.legend(fontsize=7)
    else:
        ax_e.text(
            0.5, 0.5,
            "Basal survival\nnot available",
            ha="center", va="center",
            transform=ax_e.transAxes,
        )
        ax_e.set_title(
            "E — KM: Basal Depth",
            fontsize=9,
        )
    ax_e.set_xlabel("Time", fontsize=8)

    # F — ZEB2-AURKA
    ax_f = fig.add_subplot(gs_f[1, 2])
    for label, marker in [
        ("Normal",  "^"),
        ("Luminal", "s"),
        ("Basal",   "o"),
    ]:
        if label not in groups:
            continue
        df = groups[label]
        if (
            "ZEB2" in df.columns
            and "AURKA" in df.columns
        ):
            rv, _ = safe_pearsonr(
                df["ZEB2"].values,
                df["AURKA"].values,
            )
            ax_f.scatter(
                df["ZEB2"].values,
                df["AURKA"].values,
                alpha=0.5, s=25,
                color=gc_col(label),
                marker=marker,
                label=(
                    f"{label} r={rv:+.3f}"
                    if not np.isnan(rv)
                    else label
                ),
            )
    ax_f.set_xlabel("ZEB2", fontsize=8)
    ax_f.set_ylabel("AURKA", fontsize=8)
    ax_f.set_title(
        "F — ZEB2-AURKA Coupling\n"
        "STAD=0.99 | EAC=0.47\n"
        "Basal BLCA pred: 0.55-0.75",
        fontsize=8,
    )
    ax_f.legend(fontsize=7)

    # G — Epigenetic markers
    ax_g = fig.add_subplot(gs_f[2, 0])
    epi = ["EZH2", "HDAC1", "KDM6A",
           "DNMT3A", "TET2"]
    epi_a = [
        g for g in epi if g in all_gc
    ]
    if epi_a:
        x = np.arange(len(epi_a))
        w = 0.25
        for i, label in enumerate(
            group_order
        ):
            if label not in groups:
                continue
            df = groups[label]
            means = [
                df[g].mean()
                if g in df.columns else 0
                for g in epi_a
            ]
            ax_g.bar(
                x + (i - 1) * w,
                means, w,
                color=gc_col(label),
                label=label,
                alpha=0.85,
            )
        ax_g.set_xticks(x)
        ax_g.set_xticklabels(
            epi_a, rotation=45,
            ha="right", fontsize=8,
        )
        ax_g.legend(fontsize=6)
    ax_g.set_title(
        "G — Epigenetic Markers\n"
        "KDM6A loss predicted",
        fontsize=9,
    )

    # H — Depth distributions
    ax_h = fig.add_subplot(gs_f[2, 1])
    depths_to_plot = []
    if lum_depth is not None:
        depths_to_plot.append(
            ("Luminal", lum_depth)
        )
    if bas_depth is not None:
        depths_to_plot.append(
            ("Basal", bas_depth)
        )
    if depths_to_plot:
        for i, (label, d) in enumerate(
            depths_to_plot
        ):
            ax_h.boxplot(
                d.values[np.isfinite(d.values)],
                positions=[i],
                patch_artist=True,
                boxprops=dict(
                    facecolor=gc_col(label),
                    alpha=0.7,
                ),
                medianprops=dict(
                    color="black",
                    linewidth=2,
                ),
                widths=0.4,
            )
        ax_h.set_xticks(
            range(len(depths_to_plot))
        )
        ax_h.set_xticklabels(
            [x[0] for x in depths_to_plot],
            fontsize=8,
        )
    ax_h.set_ylabel("Depth score", fontsize=8)
    ax_h.set_title(
        "H — Depth Score Distributions\n"
        "Luminal vs Basal",
        fontsize=9,
    )

    # I — Summary
    ax_i = fig.add_subplot(gs_f[2, 2])
    ax_i.axis("off")
    n_lum = (
        len(groups["Luminal"])
        if "Luminal" in groups else 0
    )
    n_bas = (
        len(groups["Basal"])
        if "Basal" in groups else 0
    )
    n_nor = (
        len(groups["Normal"])
        if "Normal" in groups else 0
    )
    p_lum_str = (
        f"{surv_lum['p']:.4f}"
        if surv_lum and not np.isnan(
            surv_lum["p"]
        )
        else "N/A"
    )
    p_bas_str = (
        f"{surv_bas['p']:.4f}"
        if surv_bas and not np.isnan(
            surv_bas["p"]
        )
        else "N/A"
    )
    zr_bas = (
        f"{zeb2_results.get('Basal',(np.nan,))[0]:+.4f}"
        if "Basal" in zeb2_results else "N/A"
    )
    summary = (
        "I — SCRIPT 1 SUMMARY\n"
        "─────────────────────────────\n"
        "Dataset: GSE13507\n"
        f"Normal={n_nor} Lum={n_lum} "
        f"Bas={n_bas}\n"
        "Platform: Illumina HWG-6 V2\n\n"
        "SURVIVAL:\n"
        f"  Luminal p={p_lum_str}\n"
        f"  Basal   p={p_bas_str}\n\n"
        "ZEB2-AURKA (basal):\n"
        f"  r={zr_bas}\n"
        f"  STAD=+0.99 EAC=+0.47\n"
        f"  Pred: 0.55-0.75\n\n"
        "Framework: OrganismCore\n"
        "Doc 91a | 2026-03-01"
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
        "blca_gse13507_s1.png",
    )
    plt.savefig(
        out, dpi=150,
        bbox_inches="tight",
    )
    log(f"\n  Figure saved: {out}")
    plt.close()

# ============================================================
# MAIN
# ============================================================

def main():
    log("=" * 65)
    log("BLADDER CANCER")
    log("FALSE ATTRACTOR ANALYSIS — SCRIPT 1")
    log("Dataset: GSE13507")
    log("Luminal + Basal BLCA")
    log("Framework: OrganismCore")
    log("Doc: 91a | Date: 2026-03-01")
    log("=" * 65)
    log("")
    log("PREDICTIONS LOCKED BEFORE DATA:")
    log("Switch: UPK1B/UPK2/UPK3A DOWN luminal")
    log("        GATA3/FOXA1/CDH1 DOWN basal")
    log("FA:     FGFR3/ERBB2/PPARG UP luminal")
    log("        KRT5/KRT14/EGFR/TP63 UP basal")
    log("Depth:  L-D1 r(FGFR3)>+0.50")
    log("        B-D1 r(KRT5)>+0.60")
    log("        B-D4 r(TP63)>+0.50 basal")
    log("        B-D5 r(ZEB2,AURKA)=0.55-0.75")
    log("Epigen: KDM6A DOWN in deep BLCA")
    log("Drug:   erdafitinib(FGFR3) derived")
    log("        venetoclax(BCL2) novel")
    log("Panel:  FGFR3(+)/GATA3(+)/UPK2(-)")
    log("        KRT5(+)/EGFR(+)/GATA3(-)")

    # Downloads
    log("")
    log("=" * 65)
    log("STEP 0: DATA ACQUISITION")
    log("=" * 65)
    os.makedirs(BASE_DIR, exist_ok=True)

    ok_mat = download_file(
        MATRIX_URL, MATRIX_FILE, "matrix"
    )
    ok_soft = download_file(
        SOFT_URL, SOFT_FILE, "soft"
    )
    gpl_file = get_gpl_file()

    if not ok_mat:
        log("FATAL: Matrix download failed")
        write_log()
        return
    if not gpl_file:
        log("FATAL: GPL annotation missing")
        write_log()
        return

    # Build probe map
    probe_map, gene_to_prob = (
        build_probe_map(gpl_file)
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

    # Classify primary (Normal/Tumor)
    primary_series = classify_samples(
        df_genes, meta, char_rows
    )

    # Classify subtypes (Luminal/Basal)
    subtype_series = classify_subtypes(
        df_genes, primary_series
    )

    # Build group dict
    group_order = [
        "Normal", "Luminal", "Basal"
    ]
    groups = {}
    for g in group_order:
        mask = subtype_series == g
        if mask.sum() > 0:
            groups[g] = df_genes[mask]

    log("")
    log("=" * 65)
    log("GROUP SUMMARY")
    log("=" * 65)
    for g, df in groups.items():
        log(f"  {g:<12}: {len(df)}")

    lum  = groups.get("Luminal",
                      pd.DataFrame())
    bas  = groups.get("Basal",
                      pd.DataFrame())
    norm = groups.get("Normal",
                      pd.DataFrame())

    # Fold change analysis
    fc_results = fold_change_analysis(
        df_genes, subtype_series
    )

    # Build depth scores
    log("")
    log("=" * 65)
    log("DEPTH SCORES")
    log("=" * 65)
    lum_depth = bas_depth = None
    if len(lum) >= 5:
        log("  Luminal depth:")
        lum_depth = build_depth_score(
            lum, LUMINAL_SWITCH,
            LUMINAL_FA, "Luminal",
        )
    if len(bas) >= 5:
        log("  Basal depth:")
        bas_depth = build_depth_score(
            bas, BASAL_SWITCH,
            BASAL_FA, "Basal",
        )

    # Depth correlations
    if lum_depth is not None:
        depth_correlations(
            lum, lum_depth, "LUMINAL"
        )
    if bas_depth is not None:
        depth_correlations(
            bas, bas_depth, "BASAL"
        )

    # Prediction tests
    if (
        lum_depth is not None
        and bas_depth is not None
    ):
        test_depth_predictions(
            lum, bas,
            lum_depth, bas_depth,
        )

    # Clinical panels
    if (
        lum_depth is not None
        and bas_depth is not None
    ):
        derive_clinical_panels(
            lum, bas,
            lum_depth, bas_depth,
        )

    # ZEB2-AURKA cross-cancer test
    zeb2_results = zeb2_aurka_test(groups)

    # Survival
    surv_df  = None
    surv_lum = None
    surv_bas = None
    if ok_soft:
        surv_df = parse_survival(
            SOFT_FILE, df_genes
        )
    if surv_df is not None:
        surv_df["subtype"] = subtype_series
        if lum_depth is not None:
            surv_lum = survival_analysis(
                lum, lum_depth,
                surv_df, "LUMINAL",
            )
        if bas_depth is not None:
            surv_bas = survival_analysis(
                bas, bas_depth,
                surv_df, "BASAL",
            )

    # Figure
    generate_figure(
        groups,
        lum_depth, bas_depth,
        surv_lum, surv_bas,
        zeb2_results,
    )

    # Save depth scores
    for label, depth_ in [
        ("luminal", lum_depth),
        ("basal",   bas_depth),
    ]:
        if depth_ is not None:
            depth_.to_csv(
                os.path.join(
                    RESULTS_DIR,
                    f"depth_s1_{label}.csv",
                ),
                header=[f"depth_s1_{label}"],
            )

    write_log()
    log(f"\n  Log    : {LOG_FILE}")
    log(f"  Output : {RESULTS_DIR}")
    log("\n=== SCRIPT 1 COMPLETE ===")
    log("\nPaste full output for Document 91a.")


if __name__ == "__main__":
    main()
