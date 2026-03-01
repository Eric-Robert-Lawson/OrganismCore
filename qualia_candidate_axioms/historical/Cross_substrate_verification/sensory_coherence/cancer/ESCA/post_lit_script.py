"""
ESOPHAGEAL CANCER — FALSE ATTRACTOR ANALYSIS
SCRIPT 3 — VALIDATION COHORT
Dataset: GSE13898
  Robust prognostic biomarkers for EAC
  identified by systems-level
  characterization of tumor transcriptome
  64 primary EAC + 15 Barrett's +
  28 surrounding normal tissue
  Platform: GPL6102 Illumina HumanWG-6 V2
  Survival data: YES

FRAMEWORK: OrganismCore Principles-First
Doc: 90d | Date: 2026-03-01

PURPOSE:
  Three independent validations in one
  dataset:

  VALIDATION 1 — SURVIVAL PANEL
    NP-ESCA-6: KRT20(+)/HDAC1(+)/APC(-)
    predicts EAC overall survival.
    Derived from GSE26886 depth geometry.
    First survival test.

  VALIDATION 2 — ZEB2-AURKA COUPLING
    AURKA absent from GPL570 (GSE26886).
    Illumina platform has AURKA probe.
    Test: r(ZEB2, AURKA) in EAC.
    Prediction: r > 0.60 (columnar cancer).
    STAD reference: r=+0.9871.
    Revised downward from 0.80 because:
    GSE26886 had AURKA absent —
    cannot confirm EAC has same
    tight coupling as STAD.
    Keeping prediction directional.

  VALIDATION 3 — PROGRESSION GEOMETRY
    Normal → Barrett's → EAC depth gradient.
    Replicate on independent cohort.
    Validate ZEB1 as squamous separator.
    Validate TFF1 as EAC FA anchor.
    Cross-platform confirmation of
    GSE26886 findings.

PREDICTIONS LOCKED 2026-03-01
(all from Doc 90a/90b/90c):

SURVIVAL PREDICTIONS (before data):
  SP-1: KRT20/HDAC1/APC panel score
        associates with overall survival
        in EAC (high score = worse OS)
  SP-2: KRT20 alone associates with OS
  SP-3: HDAC1 alone associates with OS
  SP-4: APC alone (negative) associates
        with OS (low APC = worse OS)
  SP-5: Combined panel outperforms any
        single gene for OS prediction

ZEB2-AURKA PREDICTIONS:
  ZA-1: r(ZEB2, AURKA) > 0 in EAC
  ZA-2: r(ZEB2, AURKA) > 0.60 in EAC
        (revised from 0.80 given platform
        uncertainty)
  ZA-3: r(ZEB2, AURKA) in Barrett's
        intermediate between Normal and EAC

PROGRESSION PREDICTIONS:
  PG-1: Normal < Barrett < EAC on
        corrected depth axis
  PG-2: ZEB1 separates Normal/Barrett
        from EAC on expression alone
  PG-3: TFF1 highest in EAC relative
        to Normal and Barrett's
  PG-4: CDH1 lowest in EAC relative
        to Normal and Barrett's
  PG-5: EZH2 increases Normal→Barrett→EAC
  PG-6: HDAC1 increases Normal→Barrett→EAC

CROSS-PLATFORM PREDICTIONS:
  CP-1: KRT20/HDAC1/APC pattern from
        GSE26886 replicates in GSE13898
  CP-2: r(KRT20, EAC depth) > 0.50
        in GSE13898 (was +0.87 in S2)
  CP-3: r(APC, EAC depth) < -0.30
        in GSE13898 (was -0.67 in S2)

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
from lifelines import CoxPHFitter
from lifelines.statistics import (
    logrank_test,
    multivariate_logrank_test,
)
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
LOG_FILE    = os.path.join(
    RESULTS_DIR, "analysis_log_s3.txt"
)

os.makedirs(RESULTS_DIR, exist_ok=True)

GEO_ACC    = "GSE13898"
MATRIX_URL = (
    "https://ftp.ncbi.nlm.nih.gov/geo/series/"
    "GSE13nnn/GSE13898/matrix/"
    "GSE13898_series_matrix.txt.gz"
)
MATRIX_FILE = os.path.join(
    BASE_DIR, "GSE13898_series_matrix.txt.gz"
)

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
# ILLUMINA HUMANWG-6 V2 PROBE MAP
# GPL6102 — hard-coded for target genes
# Illumina probe IDs are ILMN_XXXXXXX
# ============================================================

PROBE_MAP = {
    # Core EAC panel genes
    "ILMN_1783171": "KRT20",
    "ILMN_1740831": "HDAC1",
    "ILMN_1743697": "APC",
    "ILMN_1802712": "CDX2",
    "ILMN_2184374": "TFF1",
    "ILMN_1791920": "TFF3",
    "ILMN_1668052": "ZEB1",
    "ILMN_1697173": "ZEB2",
    "ILMN_2415447": "AURKA",
    "ILMN_1652408": "CDH1",
    "ILMN_1688580": "EZH2",
    "ILMN_1800850": "HDAC2",
    "ILMN_1814328": "KDM6A",
    # Squamous identity
    "ILMN_2179102": "KRT5",
    "ILMN_1806377": "KRT14",
    "ILMN_1672502": "SOX2",
    "ILMN_1688915": "TP63",
    "ILMN_2149050": "IVL",
    "ILMN_1740461": "SPRR1A",
    "ILMN_1713671": "NOTCH1",
    # Wnt pathway
    "ILMN_1758146": "CTNNB1",
    "ILMN_2204450": "AXIN2",
    "ILMN_1701789": "AXIN1",
    "ILMN_2333234": "TCF7L2",
    "ILMN_1795232": "LGR5",
    "ILMN_2220797": "WNT5A",
    # Proliferation
    "ILMN_1701789": "MKI67",
    "ILMN_1736218": "AURKA",
    "ILMN_1688315": "TOP2A",
    "ILMN_2388337": "CDC20",
    "ILMN_1762914": "PCNA",
    "ILMN_2337565": "PLK1",
    "ILMN_1737197": "CCNB1",
    # Cell cycle
    "ILMN_1774200": "CDKN1A",
    "ILMN_1804184": "CDKN2A",
    "ILMN_2132830": "CDK4",
    "ILMN_2413979": "CDK6",
    "ILMN_1716767": "RB1",
    "ILMN_1779530": "CCND1",
    "ILMN_1767051": "CCNE1",
    # EMT
    "ILMN_1705398": "VIM",
    "ILMN_2061507": "FN1",
    "ILMN_1674734": "CDH2",
    "ILMN_1807735": "SNAI1",
    "ILMN_1793857": "SNAI2",
    "ILMN_1760173": "TWIST1",
    # RTKs / drug targets
    "ILMN_1758236": "EGFR",
    "ILMN_2109312": "ERBB2",
    "ILMN_1731587": "ERBB3",
    "ILMN_1764993": "MET",
    "ILMN_1736457": "FGFR1",
    "ILMN_1779726": "FGFR2",
    "ILMN_1651341": "VEGFA",
    "ILMN_1705350": "KDR",
    # Epigenetic
    "ILMN_1779777": "DNMT3A",
    "ILMN_1660734": "TET2",
    "ILMN_1814890": "HDAC1",
    # Apoptosis
    "ILMN_2167085": "BCL2",
    "ILMN_2360232": "MCL1",
    "ILMN_1690854": "BAX",
    "ILMN_1713356": "BCL2L1",
    "ILMN_2345618": "BIRC5",
    # p53
    "ILMN_1666199": "TP53",
    "ILMN_1806318": "MDM2",
    # Intestinal markers
    "ILMN_1740006": "MUC2",
    "ILMN_1783171": "KRT20",
    "ILMN_1804024": "MUC5B",
    "ILMN_2413027": "CLDN18",
    "ILMN_2124613": "CDH17",
    "ILMN_1729890": "GKN1",
    "ILMN_1671238": "MUC5AC",
    "ILMN_1705929": "TFF1",
    # Immune
    "ILMN_1811311": "CD274",
    "ILMN_1663100": "PDCD1",
    "ILMN_2228519": "CD8A",
    "ILMN_1814592": "FOXP3",
    # MYC
    "ILMN_1771120": "MYC",
    # PIK3CA
    "ILMN_1791633": "PIK3CA",
    # HIF
    "ILMN_1779030": "HIF1A",
    # MMR
    "ILMN_1758764": "MLH1",
    "ILMN_2359058": "MSH6",
    # DSG
    "ILMN_1725905": "DSG1",
    "ILMN_2159649": "DSG3",
    # NOTCH targets
    "ILMN_2055271": "HES1",
    "ILMN_1716874": "JAG1",
    # TGF-B
    "ILMN_1778720": "TGFB1",
    "ILMN_1788373": "TGFBR2",
    # FOXA2 (Barrett's marker)
    "ILMN_1663909": "FOXA2",
    # SOX9
    "ILMN_1722398": "SOX9",
}

GENE_TO_PROBES = {}
for probe, gene in PROBE_MAP.items():
    if gene not in GENE_TO_PROBES:
        GENE_TO_PROBES[gene] = []
    if probe not in GENE_TO_PROBES[gene]:
        GENE_TO_PROBES[gene].append(probe)

TARGET_GENES = sorted(set(PROBE_MAP.values()))

# Corrected panels from S2
EAC_SWITCH_S2 = [
    "CDH1", "ZEB1", "KRT5", "APC", "CTNNB1"
]
EAC_FA_S2 = [
    "CDX2", "TFF1", "KRT20", "VEGFA",
    "NOTCH1", "HDAC1", "EZH2",
]
SHARED_SQUAMOUS = ["ZEB1", "KRT5", "IVL"]
SHARED_COLUMNAR = ["TFF1", "CDX2", "CDH1"]

# ============================================================
# DOWNLOAD
# ============================================================

def download_file(url, dest):
    if os.path.exists(dest):
        log(f"  Already present: {dest} "
            f"({os.path.getsize(dest):,} bytes)")
        return True
    log(f"  Downloading: {url}")
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

# ============================================================
# PARSE SERIES MATRIX
# Illumina format — slightly different
# probe ID style than Affymetrix
# ============================================================

def parse_series_matrix(filepath):
    log("")
    log("=" * 65)
    log("PARSE SERIES MATRIX")
    log(f"  File: {filepath}")
    log(f"  Platform: GPL6102 Illumina HWG-6 V2")
    log("=" * 65)

    opener = (
        gzip.open(
            filepath, "rt",
            encoding="utf-8",
            errors="ignore",
        )
        if filepath.endswith(".gz")
        else open(
            filepath, "r",
            encoding="utf-8",
            errors="ignore",
        )
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
                vals  = [
                    p.strip().strip('"')
                    for p in parts[1:]
                ]
                key_num = len(char_rows)
                char_rows[key_num] = vals

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
                if probe_id not in PROBE_MAP:
                    continue

                try:
                    vals = [
                        float(p)
                        if p not in [
                            "", "null", "NA",
                            "nan", "N/A", "Inf",
                            "-Inf",
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
    log(f"  Sample titles: {len(sample_titles)}")
    log(f"  Probes found : {len(probe_ids)}")

    if not probe_ids:
        log("  WARNING: No target probes found")
        log("  Inspecting actual probe IDs...")
        _inspect_probes(filepath)
        return None, None, None

    cols = header_cols[1:]
    n_c  = len(rows[0]) if rows else 0
    cols = cols[:n_c]

    df = pd.DataFrame(
        rows,
        index=probe_ids,
        columns=cols,
        dtype=float,
    )

    gene_expr = {}
    genes_found = []
    for gene, probes in GENE_TO_PROBES.items():
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
        gene_expr,
        index=cols,
        dtype=float,
    )
    log(f"  Genes mapped : {len(genes_found)}")
    log(f"  Genes found  : {sorted(genes_found)}")

    # Metadata
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

    # Parse characteristics for survival
    log(f"\n  Characteristics rows: "
        f"{len(char_rows)}")
    log(f"  Characteristic keys (first 5):")
    for k in list(char_rows.keys())[:5]:
        uniq = list(set(char_rows[k]))[:3]
        log(f"    row {k}: {uniq}")

    return df_genes, meta, char_rows


def _inspect_probes(filepath):
    opener = (
        gzip.open(
            filepath, "rt",
            encoding="utf-8",
            errors="ignore",
        )
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
    log("  First 20 actual probe IDs:")
    for p in seen:
        log(f"    {p}")

# ============================================================
# CLASSIFY SAMPLES
# GSE13898: EAC / Barrett / Normal
# ============================================================

def classify_samples(df_genes, meta):
    log("")
    log("=" * 65)
    log("CLASSIFY SAMPLES")
    log("EAC / Barrett / Normal")
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
            "barrett", "be_", "be ",
            "be-", "be0",
        ]):
            groups.append("Barrett")
        elif any(x in title for x in [
            "adenocarcinoma", "eac",
            "adeno", "ac_", "ac ",
        ]):
            groups.append("EAC")
        elif any(x in title for x in [
            "normal", "surrounding",
            "squamous", "nse", "nm_",
        ]):
            groups.append("Normal")
        else:
            groups.append("Unknown")

    gs = pd.Series(groups,
                   index=df_genes.index)

    log(f"\n  Group counts:")
    for g, n in gs.value_counts().items():
        log(f"    {g}: {n}")

    log(f"\n  First 10 classified:")
    for s in df_genes.index[:10]:
        title = ""
        if (
            meta is not None
            and "title" in meta.columns
            and s in meta.index
        ):
            title = str(
                meta.loc[s, "title"]
            )[:55]
        log(f"    {s[:12]:<12} → "
            f"{gs[s]:<10} {title}")

    n_unk = (gs == "Unknown").sum()
    if n_unk > 3:
        log(f"\n  WARNING: {n_unk} Unknown")
        if (
            meta is not None
            and "title" in meta.columns
        ):
            log("  All unique titles:")
            for t in meta["title"].unique():
                log(f"    {t}")

    return gs

# ============================================================
# EXTRACT SURVIVAL DATA
# GSE13898 stores survival in
# Sample_characteristics_ch1 rows
# ============================================================

def extract_survival(
    df_genes, meta, char_rows, group_series
):
    log("")
    log("=" * 65)
    log("EXTRACT SURVIVAL DATA")
    log("=" * 65)

    n = len(df_genes)
    os_time   = np.full(n, np.nan)
    os_event  = np.full(n, np.nan)

    # Show all characteristic rows
    log(f"  All characteristic rows:")
    for k, vals in char_rows.items():
        uniq = list(set(
            v for v in vals if v
        ))[:5]
        log(f"    row {k}: {uniq}")

    # Try to find survival fields
    # Common formats in GEO:
    #   "overall survival (months): XX"
    #   "survival time: XX"
    #   "os: XX"
    #   "vital status: alive/dead"
    #   "recurrence: yes/no"

    time_row   = None
    event_row  = None
    time_pat   = re.compile(
        r"(?:os|survival|time)[^:]*:\s*([\d.]+)",
        re.I,
    )
    event_pat  = re.compile(
        r"(?:vital|status|event|death|"
        r"recurrence|dead|alive)[^:]*:\s*"
        r"([\w]+)",
        re.I,
    )

    for k, vals in char_rows.items():
        non_empty = [v for v in vals if v]
        if not non_empty:
            continue
        sample_val = non_empty[0]
        if time_pat.search(sample_val):
            time_row = k
            log(f"  → Time row: {k} "
                f"(example: {sample_val})")
        if event_pat.search(sample_val):
            event_row = k
            log(f"  → Event row: {k} "
                f"(example: {sample_val})")

    if time_row is not None:
        vals = char_rows[time_row]
        for i, v in enumerate(
            vals[:len(os_time)]
        ):
            m = time_pat.search(str(v))
            if m:
                try:
                    os_time[i] = float(m.group(1))
                except ValueError:
                    pass

    if event_row is not None:
        vals = char_rows[event_row]
        for i, v in enumerate(
            vals[:len(os_event)]
        ):
            m = event_pat.search(str(v))
            if m:
                status = m.group(1).lower()
                if status in [
                    "dead", "deceased",
                    "yes", "1", "true",
                    "died",
                ]:
                    os_event[i] = 1
                elif status in [
                    "alive", "no", "0",
                    "false", "living",
                ]:
                    os_event[i] = 0

    n_time  = np.sum(~np.isnan(os_time))
    n_event = np.sum(~np.isnan(os_event))
    log(f"\n  Survival times found : {n_time}")
    log(f"  Event values found   : {n_event}")

    if n_time > 0:
        log(f"  Time range: "
            f"{np.nanmin(os_time):.1f} – "
            f"{np.nanmax(os_time):.1f}")
    if n_event > 0:
        log(f"  Event counts: "
            f"1={int(np.nansum(os_event==1))} "
            f"0={int(np.nansum(os_event==0))}")

    surv_df = pd.DataFrame({
        "sample":    df_genes.index,
        "os_time":   os_time,
        "os_event":  os_event,
        "group":     group_series.values,
    }, index=df_genes.index)

    return surv_df

# ============================================================
# DEPTH SCORE
# ============================================================

def build_depth_score(
    df, switch, fa, label
):
    gc  = list(df.columns)
    sw  = [g for g in switch if g in gc]
    fa_ = [g for g in fa     if g in gc]

    depth = pd.Series(
        np.zeros(len(df)),
        index=df.index,
        dtype=float,
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

    log(f"  {label} depth (n={len(df)}): "
        f"mean={depth.mean():.4f} "
        f"std={depth.std():.4f}")
    return depth

# ============================================================
# VALIDATION 1 — SURVIVAL PANEL
# KRT20(+)/HDAC1(+)/APC(-) vs OS
# ============================================================

def survival_panel_test(
    eac_df, surv_df
):
    log("")
    log("=" * 65)
    log("VALIDATION 1: SURVIVAL PANEL")
    log("KRT20(+) / HDAC1(+) / APC(-)")
    log("Prediction SP-1 through SP-5")
    log("=" * 65)

    # Subset to EAC with survival data
    eac_idx = surv_df[
        surv_df["group"] == "EAC"
    ].index
    eac_idx = eac_idx.intersection(
        eac_df.index
    )

    if len(eac_idx) < 10:
        log(f"  Insufficient EAC with "
            f"survival (n={len(eac_idx)})")
        log(f"  Check survival extraction")
        return None

    df   = eac_df.loc[eac_idx]
    surv = surv_df.loc[eac_idx]

    t = surv["os_time"].values
    e = surv["os_event"].values

    valid = (
        ~np.isnan(t) & ~np.isnan(e)
        & (t > 0)
    )
    log(f"  EAC with valid survival: "
        f"{valid.sum()} / {len(valid)}")

    if valid.sum() < 10:
        log(f"  Insufficient valid survival "
            f"data — check characteristics")
        return None

    t = t[valid]
    e = e[valid]
    df_v = df[valid]

    gc = list(df_v.columns)

    # Test each gene individually
    log(f"\n  Individual gene survival tests:")
    log(f"  (median split, log-rank)")
    log(f"  {'Gene':<10} {'n_hi':>5} "
        f"{'n_lo':>5}  log-rank p  "
        f"Direction  Prediction")
    log(f"  {'-'*65}")

    single_results = {}
    for gene, pred in [
        ("KRT20",  "UP-worse"),
        ("HDAC1",  "UP-worse"),
        ("APC",    "DOWN-worse"),
        ("CDX2",   "UP-worse"),
        ("TFF1",   "UP-worse"),
        ("EZH2",   "UP-worse"),
        ("ZEB1",   "DOWN-better"),
        ("CDH1",   "DOWN-worse"),
        ("VEGFA",  "UP-worse"),
        ("MKI67",  "UP-worse"),
        ("ERBB2",  "UP-worse"),
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
                t[hi], t[lo],
                e[hi], e[lo],
            )
            p   = res.p_value
            hr  = (
                t[lo].mean() / t[hi].mean()
                if t[hi].mean() > 0
                else np.nan
            )
        except Exception:
            p = np.nan
            hr = np.nan

        # Direction: which group has worse OS
        # (lower mean survival time)
        if not np.isnan(p):
            mean_hi = t[hi].mean()
            mean_lo = t[lo].mean()
            if mean_hi < mean_lo:
                direction = "hi=worse"
            else:
                direction = "lo=worse"

            if pred == "UP-worse":
                pred_conf = (
                    "✓" if direction == "hi=worse"
                    else "✗"
                )
            else:
                pred_conf = (
                    "✓" if direction == "lo=worse"
                    else "✗"
                )
        else:
            direction = "N/A"
            pred_conf = "?"

        log(f"  {gene:<10} {hi.sum():>5} "
            f"{lo.sum():>5}  "
            f"{fmt_p(p):>12}  "
            f"{direction:<12} {pred_conf}")

        single_results[gene] = {
            "p": p, "direction": direction
        }

    # Build combined panel score
    log(f"\n  Combined panel score:")
    log(f"  KRT20(+) + HDAC1(+) + APC(-)")

    panel_genes = [
        g for g in ["KRT20", "HDAC1", "APC"]
        if g in gc
    ]
    log(f"  Panel genes available: {panel_genes}")

    if len(panel_genes) >= 2:
        score_parts = []
        for gene in panel_genes:
            ns = norm01(df_v[gene].values)
            if gene == "APC":
                score_parts.append(1 - ns)
            else:
                score_parts.append(ns)

        panel_score = np.mean(
            score_parts, axis=0
        )

        med_score = np.median(panel_score)
        hi = panel_score >= med_score
        lo = ~hi

        log(f"  n_high={hi.sum()} "
            f"n_low={lo.sum()}")
        log(f"  High score mean OS: "
            f"{t[hi].mean():.1f}")
        log(f"  Low  score mean OS: "
            f"{t[lo].mean():.1f}")

        try:
            res_panel = logrank_test(
                t[hi], t[lo],
                e[hi], e[lo],
            )
            p_panel = res_panel.p_value
        except Exception:
            p_panel = np.nan

        log(f"\n  Panel log-rank p = "
            f"{fmt_p(p_panel)}")

        # Compare panel vs best individual
        p_krt20 = single_results.get(
            "KRT20", {}
        ).get("p", np.nan)
        p_hdac1 = single_results.get(
            "HDAC1", {}
        ).get("p", np.nan)
        p_apc   = single_results.get(
            "APC", {}
        ).get("p", np.nan)

        best_ind = np.nanmin([
            p_krt20, p_hdac1, p_apc
        ])

        log(f"  Best individual p = "
            f"{fmt_p(best_ind)}")
        log(f"  Panel p           = "
            f"{fmt_p(p_panel)}")

        if not np.isnan(p_panel):
            if p_panel < 0.05:
                log(f"\n  SP-1 CONFIRMED: "
                    f"Panel predicts OS ✓")
            else:
                log(f"\n  SP-1 NOT CONFIRMED: "
                    f"Panel ns")

            if (
                not np.isnan(best_ind)
                and p_panel < best_ind
            ):
                log(f"  SP-5 CONFIRMED: "
                    f"Panel > individual ✓")
            else:
                log(f"  SP-5 NOT CONFIRMED: "
                    f"Individual sufficient")

        # KM plot data
        return {
            "t": t, "e": e,
            "hi": hi, "lo": lo,
            "panel_score": panel_score,
            "p_panel": p_panel,
            "single_results": single_results,
            "df_v": df_v,
        }

    return None

# ============================================================
# VALIDATION 2 — ZEB2-AURKA COUPLING
# ============================================================

def zeb2_aurka_validation(groups):
    log("")
    log("=" * 65)
    log("VALIDATION 2: ZEB2-AURKA COUPLING")
    log("STAD reference: r=+0.9871 ***")
    log("Prediction ZA-1: r > 0 in EAC")
    log("Prediction ZA-2: r > 0.60 in EAC")
    log("ZA-3: Barrett intermediate")
    log("GSE26886: AURKA absent (GPL570)")
    log("GSE13898: Illumina — AURKA present")
    log("=" * 65)

    results = {}
    for label in ["EAC", "Barrett", "Normal"]:
        if label not in groups:
            continue
        df = groups[label]
        gc = list(df.columns)

        if (
            "ZEB2" not in gc
            or "AURKA" not in gc
        ):
            log(f"  {label}: ZEB2 or AURKA "
                f"missing")
            log(f"    Present: "
                f"{[g for g in ['ZEB2','AURKA'] if g in gc]}")
            continue

        rv, pv = safe_pearsonr(
            df["ZEB2"].values,
            df["AURKA"].values,
        )
        log(f"\n  {label} (n={len(df)}):")
        log(f"  r(ZEB2, AURKA) = "
            f"{rv:+.4f}  {fmt_p(pv)}")
        if not np.isnan(rv):
            log(f"  r² = {rv**2:.4f}")

        results[label] = (rv, pv)

        if label == "EAC":
            if not np.isnan(rv):
                if rv > 0.60:
                    log(f"  ZA-2 CONFIRMED ✓ "
                        f"(r>0.60 in EAC)")
                elif rv > 0:
                    log(f"  ZA-1 CONFIRMED ✓ "
                        f"(r>0 in EAC)")
                    log(f"  ZA-2 NOT CONFIRMED "
                        f"(r<0.60)")
                else:
                    log(f"  ZA-1/ZA-2 NOT "
                        f"CONFIRMED")

    # Check ZA-3: Barrett intermediate
    if (
        "EAC" in results
        and "Barrett" in results
        and "Normal" in results
    ):
        r_eac = results["EAC"][0]
        r_bar = results["Barrett"][0]
        r_nor = results["Normal"][0]
        log(f"\n  ZA-3 test:")
        log(f"  Normal   r={r_nor:+.4f}")
        log(f"  Barrett  r={r_bar:+.4f}")
        log(f"  EAC      r={r_eac:+.4f}")
        if not any(
            np.isnan(x)
            for x in [r_eac, r_bar, r_nor]
        ):
            if (
                r_bar > r_nor
                and r_eac > r_bar
            ):
                log(f"  ZA-3 CONFIRMED ✓ "
                    f"Barrett intermediate")
            else:
                log(f"  ZA-3 NOT CONFIRMED")

    return results

# ============================================================
# VALIDATION 3 — PROGRESSION GEOMETRY
# ============================================================

def progression_geometry(
    groups, group_order
):
    log("")
    log("=" * 65)
    log("VALIDATION 3: PROGRESSION GEOMETRY")
    log("Normal → Barrett's → EAC")
    log("Independent cohort confirmation")
    log("=" * 65)

    all_gc = set()
    for df in groups.values():
        all_gc.update(df.columns)

    # Test specific predictions
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
        ("FOXA2",  "-",    "EAC>Normal"),
    ]

    log(f"\n  {'Gene':<10} {'Normal':>9} "
        f"{'Barrett':>9} {'EAC':>9}  "
        f"Pred     EAC vs N")
    log(f"  {'-'*65}")

    for gene, pred_id, direction in markers:
        if gene not in all_gc:
            continue

        means = {}
        for g in group_order:
            if (
                g in groups
                and gene in groups[g].columns
            ):
                means[g] = (
                    groups[g][gene].mean()
                )
            else:
                means[g] = np.nan

        # EAC vs Normal test
        eac_v = (
            groups["EAC"][gene].values
            if "EAC" in groups
            and gene in groups["EAC"].columns
            else np.array([])
        )
        nor_v = (
            groups["Normal"][gene].values
            if "Normal" in groups
            and gene in groups["Normal"].columns
            else np.array([])
        )
        _, pp = safe_mwu(
            eac_v, nor_v, "two-sided"
        )

        nm  = means.get("Normal", np.nan)
        bm  = means.get("Barrett", np.nan)
        em  = means.get("EAC", np.nan)

        if not np.isnan(em) and not np.isnan(nm):
            if direction == "EAC>Normal":
                conf = (
                    "✓" if em > nm else "✗"
                )
            else:
                conf = (
                    "✓" if nm > em else "✗"
                )
        else:
            conf = "?"

        log(
            f"  {gene:<10} "
            f"{nm:>9.4f} "
            f"{bm:>9.4f} "
            f"{em:>9.4f}  "
            f"{pred_id:<8} "
            f"{fmt_p(pp)} {conf}"
            if not any(
                np.isnan(x)
                for x in [nm, bm, em]
            )
            else
            f"  {gene:<10} N/A"
        )

    # Build depth scores for all 3 groups
    log(f"\n  Depth scores (S2 EAC panel):")
    depth_dict = {}
    for g in group_order:
        if g not in groups:
            continue
        df = groups[g]
        if len(df) < 3:
            continue
        d = build_depth_score(
            df, EAC_SWITCH_S2,
            EAC_FA_S2, g,
        )
        depth_dict[g] = d

    log(f"\n  Group depth order test (PG-1):")
    log(f"  {'Group':<12} {'n':>4}  "
        f"{'mean':>8}  std")
    for g in group_order:
        if g in depth_dict:
            d = depth_dict[g]
            log(f"  {g:<12} {len(d):>4}  "
                f"{d.mean():>8.4f}  "
                f"{d.std():.4f}")

    # Test ordering
    if (
        "Normal" in depth_dict
        and "Barrett" in depth_dict
        and "EAC" in depth_dict
    ):
        _, p_nb = safe_mwu(
            depth_dict["Barrett"].values,
            depth_dict["Normal"].values,
            "greater",
        )
        _, p_be = safe_mwu(
            depth_dict["EAC"].values,
            depth_dict["Barrett"].values,
            "greater",
        )
        _, p_ne = safe_mwu(
            depth_dict["EAC"].values,
            depth_dict["Normal"].values,
            "greater",
        )
        log(f"\n  Barrett > Normal : "
            f"{fmt_p(p_nb)}")
        log(f"  EAC > Barrett   : "
            f"{fmt_p(p_be)}")
        log(f"  EAC > Normal    : "
            f"{fmt_p(p_ne)}")

        if (
            not np.isnan(p_ne)
            and p_ne < 0.05
        ):
            log(f"  PG-1 CONFIRMED: "
                f"Normal < EAC ✓")
        if (
            not np.isnan(p_nb)
            and p_nb < 0.05
        ):
            log(f"  PG-1 PARTIAL: "
                f"Barrett > Normal ✓")

    return depth_dict

# ============================================================
# CROSS-PLATFORM VALIDATION
# Compare key correlations vs S2
# ============================================================

def cross_platform_validation(
    eac, depth_eac
):
    log("")
    log("=" * 65)
    log("CROSS-PLATFORM VALIDATION")
    log("GSE13898 (Illumina) vs")
    log("GSE26886 (Affymetrix) findings")
    log("=" * 65)

    gc = list(eac.columns)

    markers = [
        ("KRT20",  "+0.87***", "CP-2",  0.50),
        ("HDAC1",  "+0.67***", "-",     0.30),
        ("APC",    "-0.67***", "CP-3", -0.30),
        ("CTNNB1", "-0.56***", "-",    -0.20),
        ("EZH2",   "+0.55*",   "-",     0.30),
        ("CDX2",   "+0.48*",   "-",     0.20),
        ("CDC20",  "+0.62**",  "-",     0.30),
        ("MKI67",  "+0.61**",  "-",     0.30),
        ("VEGFA",  "+0.46*",   "-",     0.20),
        ("CDH1",   "-0.48*",   "-",    -0.20),
        ("MUC5B",  "-0.56**",  "-",    -0.20),
        ("ZEB1",   "separator","-",     None),
    ]

    log(f"\n  {'Gene':<10} "
        f"{'S2 r':>10}  "
        f"{'S3 r':>8}  "
        f"{'S3 p':>14}  "
        f"Pred threshold  "
        f"Replicated?")
    log(f"  {'-'*75}")

    replicated = 0
    tested     = 0

    for gene, s2_r, pred_id, threshold in markers:
        if gene not in gc:
            log(f"  {gene:<10} NOT IN MATRIX")
            continue

        rv, pv = safe_pearsonr(
            depth_eac.values,
            eac[gene].values,
        )

        if threshold is not None and not np.isnan(rv):
            tested += 1
            if threshold > 0:
                rep = (
                    "YES ✓" if rv >= threshold
                    else "NO  ✗"
                )
                if rv >= threshold:
                    replicated += 1
            else:
                rep = (
                    "YES ✓" if rv <= threshold
                    else "NO  ✗"
                )
                if rv <= threshold:
                    replicated += 1
        else:
            rep = "N/A"

        log(
            f"  {gene:<10} "
            f"{s2_r:>10}  "
            f"{rv:>+8.4f}  "
            f"{fmt_p(pv):>14}  "
            f"{'≥'+str(threshold) if threshold and threshold>0 else '≤'+str(threshold) if threshold else 'N/A':>16}  "
            f"{rep}"
            if not np.isnan(rv)
            else
            f"  {gene:<10} {s2_r:>10}  N/A"
        )

    if tested > 0:
        log(f"\n  Replicated: "
            f"{replicated}/{tested} "
            f"({100*replicated/tested:.0f}%)")
        if replicated / tested >= 0.70:
            log(f"  CP-1 CONFIRMED: "
                f"GSE26886 findings replicate "
                f"in GSE13898 ✓")
        else:
            log(f"  CP-1 NOT CONFIRMED: "
                f"Low replication rate")

# ============================================================
# ZEB2-AURKA DEEP DIVE
# Across all EAC samples
# ============================================================

def zeb2_aurka_deep(eac):
    log("")
    log("=" * 65)
    log("ZEB2-AURKA DEEP DIVE")
    log("Individual gene correlations")
    log("in EAC context")
    log("=" * 65)

    gc  = list(eac.columns)
    key = ["ZEB2", "AURKA", "ZEB1",
           "CDC20", "MKI67", "TOP2A",
           "PLK1", "CCNB1", "CDX2",
           "KRT20", "HDAC1", "EZH2"]

    log(f"\n  EAC expression means:")
    for gene in key:
        if gene in gc:
            log(f"  {gene:<10} "
                f"{eac[gene].mean():>9.4f}")

    if "ZEB2" in gc and "AURKA" in gc:
        rv, pv = safe_pearsonr(
            eac["ZEB2"].values,
            eac["AURKA"].values,
        )
        log(f"\n  r(ZEB2, AURKA) in EAC:")
        log(f"  r = {rv:+.4f}  {fmt_p(pv)}")
        log(f"  STAD reference: r=+0.9871")

    # Test ZEB2 with all genes
    if "ZEB2" in gc:
        log(f"\n  ZEB2 correlations in EAC:")
        zeb2_corrs = []
        for gene in gc:
            rv, pv = safe_pearsonr(
                eac["ZEB2"].values,
                eac[gene].values,
            )
            if not np.isnan(rv):
                zeb2_corrs.append((gene, rv, pv))
        zeb2_corrs.sort(
            key=lambda x: abs(x[1]),
            reverse=True,
        )
        log(f"  {'Gene':<10} {'r':>8}  p-value")
        for g, r, p in zeb2_corrs[:10]:
            log(f"  {g:<10} {r:>+8.4f}  "
                f"{fmt_p(p)}")

# ============================================================
# GENERATE FIGURE
# ============================================================

def generate_figure(
    groups, depth_dict,
    survival_results, zeb2_aurka_results,
    group_order,
):
    log("")
    log("--- Generating Script 3 figure ---")

    fig = plt.figure(figsize=(28, 22))
    fig.suptitle(
        "Esophageal Cancer — False Attractor "
        "Analysis\n"
        "Script 3 | GSE13898 | EAC+Barrett+"
        "Normal Validation Cohort\n"
        "OrganismCore | 2026-03-01 | "
        "Doc 90d | Illumina HumanWG-6 V2",
        fontsize=10,
        fontweight="bold",
        y=0.99,
    )

    gs = gridspec.GridSpec(
        3, 3,
        figure=fig,
        hspace=0.55,
        wspace=0.45,
    )

    COLORS = {
        "Normal":  "#27ae60",
        "Barrett": "#f39c12",
        "EAC":     "#2980b9",
        "ESCC":    "#e74c3c",
    }

    def gc_col(g):
        return COLORS.get(g, "#95a5a6")

    # A — Kaplan-Meier survival panel
    ax_a = fig.add_subplot(gs[0, 0])
    if survival_results is not None:
        t  = survival_results["t"]
        e  = survival_results["e"]
        hi = survival_results["hi"]
        lo = survival_results["lo"]
        pp = survival_results.get(
            "p_panel", np.nan
        )

        kmf = KaplanMeierFitter()
        kmf.fit(
            t[hi], e[hi],
            label=f"High score "
                  f"(n={hi.sum()})",
        )
        kmf.plot_survival_function(
            ax=ax_a,
            color="#e74c3c",
            ci_show=False,
        )
        kmf.fit(
            t[lo], e[lo],
            label=f"Low score "
                  f"(n={lo.sum()})",
        )
        kmf.plot_survival_function(
            ax=ax_a,
            color="#27ae60",
            ci_show=False,
        )
        ax_a.set_title(
            f"A — KM: KRT20/HDAC1/APC Panel\n"
            f"p={pp:.4f}" if not np.isnan(pp)
            else
            "A — KM: KRT20/HDAC1/APC Panel",
            fontsize=9,
        )
        ax_a.set_xlabel("Time", fontsize=8)
        ax_a.set_ylabel(
            "Survival probability", fontsize=8
        )
        ax_a.legend(fontsize=7)

    # B — ZEB2-AURKA scatter
    ax_b = fig.add_subplot(gs[0, 1])
    for label, color, marker in [
        ("EAC",     COLORS["EAC"],     "s"),
        ("Barrett", COLORS["Barrett"], "o"),
        ("Normal",  COLORS["Normal"],  "^"),
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
            ax_b.scatter(
                df["ZEB2"].values,
                df["AURKA"].values,
                alpha=0.5, s=30,
                color=color,
                marker=marker,
                label=(
                    f"{label} r={rv:+.3f}"
                    if not np.isnan(rv)
                    else label
                ),
            )
    ax_b.set_xlabel("ZEB2", fontsize=8)
    ax_b.set_ylabel("AURKA", fontsize=8)
    ax_b.set_title(
        "B — ZEB2-AURKA Coupling\n"
        "Prediction: r>0.60 in EAC\n"
        "STAD reference: r=+0.9871",
        fontsize=8,
    )
    ax_b.legend(fontsize=7)

    # C — Progression depth
    ax_c = fig.add_subplot(gs[0, 2])
    valid_groups = [
        (g, depth_dict[g])
        for g in group_order
        if g in depth_dict
        and depth_dict[g] is not None
        and len(depth_dict[g]) > 0
    ]
    if valid_groups:
        for i, (g, d) in enumerate(
            valid_groups
        ):
            ax_c.scatter(
                [i] * len(d),
                d.values,
                alpha=0.4, s=18,
                color=gc_col(g),
            )
            ax_c.scatter(
                [i], [d.mean()],
                s=120, color=gc_col(g),
                zorder=5, marker="D",
                label=f"{g} μ={d.mean():.3f}",
            )
        ax_c.set_xticks(
            range(len(valid_groups))
        )
        ax_c.set_xticklabels(
            [x[0] for x in valid_groups],
            fontsize=8,
        )
        ax_c.legend(fontsize=7)
    ax_c.set_ylabel("Depth score", fontsize=8)
    ax_c.set_title(
        "C — Progression Geometry\n"
        "Normal → Barrett → EAC\n"
        "(GSE13898 independent validation)",
        fontsize=9,
    )

    # D — Key markers by group
    ax_d = fig.add_subplot(gs[1, 0])
    key_genes = [
        "ZEB1", "TFF1", "CDX2",
        "CDH1", "KRT20", "HDAC1",
    ]
    avail = [
        g for g in key_genes
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
            ha="right", fontsize=7,
        )
        ax_d.legend(fontsize=6)
    ax_d.set_title(
        "D — Key Markers by Group\n"
        "Normal vs Barrett vs EAC",
        fontsize=9,
    )

    # E — Epigenetic markers
    ax_e = fig.add_subplot(gs[1, 1])
    epi = [
        "EZH2", "HDAC1", "HDAC2",
        "KDM6A", "TET2",
    ]
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
            ha="right", fontsize=8,
        )
        ax_e.legend(fontsize=6)
    ax_e.set_title(
        "E — Epigenetic Progression\n"
        "EZH2+HDAC1 Normal→Barrett→EAC",
        fontsize=9,
    )

    # F — APC and Wnt by group
    ax_f = fig.add_subplot(gs[1, 2])
    wnt_genes = [
        "APC", "CTNNB1", "AXIN2",
        "TCF7L2", "LGR5",
    ]
    wnt_a = [
        g for g in wnt_genes
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
            ax_f.bar(
                x + (i - 1) * w,
                means, w,
                color=gc_col(grp_name),
                label=grp_name,
                alpha=0.85,
            )
        ax_f.set_xticks(x)
        ax_f.set_xticklabels(
            wnt_a, rotation=45,
            ha="right", fontsize=8,
        )
        ax_f.legend(fontsize=6)
    ax_f.set_title(
        "F — Wnt Pathway Progression\n"
        "APC / CTNNB1 / AXIN2",
        fontsize=9,
    )

    # G — KM individual genes
    ax_g = fig.add_subplot(gs[2, 0])
    if survival_results is not None:
        single = survival_results.get(
            "single_results", {}
        )
        t   = survival_results["t"]
        e   = survival_results["e"]
        df_v = survival_results["df_v"]

        for gene, color in [
            ("KRT20", COLORS["EAC"]),
            ("APC",   COLORS["Normal"]),
        ]:
            if gene not in df_v.columns:
                continue
            vals = df_v[gene].values
            med  = np.nanmedian(vals)
            hi   = vals >= med
            lo   = ~hi
            if hi.sum() < 3 or lo.sum() < 3:
                continue
            kmf = KaplanMeierFitter()
            kmf.fit(
                t[hi], e[hi],
                label=f"{gene}-hi",
            )
            kmf.plot_survival_function(
                ax=ax_g,
                color=color,
                ci_show=False,
                linestyle="-",
            )
            kmf.fit(
                t[lo], e[lo],
                label=f"{gene}-lo",
            )
            kmf.plot_survival_function(
                ax=ax_g,
                color=color,
                ci_show=False,
                linestyle="--",
            )
        ax_g.set_title(
            "G — KM: Individual Genes\n"
            "KRT20 and APC",
            fontsize=9,
        )
        ax_g.set_xlabel("Time", fontsize=8)
        ax_g.legend(fontsize=6)

    # H — ZEB1 separation
    ax_h = fig.add_subplot(gs[2, 1])
    if "ZEB1" in (
        list(groups.get("Normal",
                        pd.DataFrame()).columns)
    ):
        for g in ["Normal", "Barrett", "EAC"]:
            if g not in groups:
                continue
            df = groups[g]
            if "ZEB1" in df.columns:
                vals = df["ZEB1"].values
                ax_h.boxplot(
                    vals[np.isfinite(vals)],
                    positions=[
                        ["Normal", "Barrett",
                         "EAC"].index(g)
                    ],
                    patch_artist=True,
                    boxprops=dict(
                        facecolor=gc_col(g),
                        alpha=0.7,
                    ),
                    medianprops=dict(
                        color="black",
                        linewidth=2,
                    ),
                    widths=0.4,
                )
    ax_h.set_xticks([0, 1, 2])
    ax_h.set_xticklabels(
        ["Normal", "Barrett", "EAC"],
        fontsize=8,
    )
    ax_h.set_ylabel("ZEB1 expression",
                    fontsize=8)
    ax_h.set_title(
        "H — ZEB1 as Squamous Separator\n"
        "Prediction: Normal > EAC",
        fontsize=9,
    )

    # I — Summary
    ax_i = fig.add_subplot(gs[2, 2])
    ax_i.axis("off")

    zeb2_eac_r = np.nan
    if (
        "EAC" in zeb2_aurka_results
        and not np.isnan(
            zeb2_aurka_results["EAC"][0]
        )
    ):
        zeb2_eac_r = (
            zeb2_aurka_results["EAC"][0]
        )

    p_panel = (
        survival_results.get(
            "p_panel", np.nan
        )
        if survival_results else np.nan
    )

    summary = (
        "I — SCRIPT 3 SUMMARY\n"
        "─────────────────────────────\n"
        "Dataset: GSE13898\n"
        "EAC+Barrett+Normal validation\n"
        "Platform: Illumina HumanWG-6 V2\n\n"
        "VALIDATION 1 — SURVIVAL PANEL:\n"
        f"  KRT20/HDAC1/APC\n"
        f"  p={p_panel:.4f}\n\n"
        "VALIDATION 2 — ZEB2-AURKA:\n"
        f"  EAC r={zeb2_eac_r:+.4f}\n"
        f"  (pred >0.60; STAD r=+0.9871)\n\n"
        "VALIDATION 3 — PROGRESSION:\n"
        "  Normal→Barrett→EAC depth\n\n"
        "Framework: OrganismCore\n"
        "Doc: 90d | 2026-03-01"
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
    log("ESOPHAGEAL CANCER")
    log("FALSE ATTRACTOR ANALYSIS — SCRIPT 3")
    log("Dataset: GSE13898")
    log("EAC + Barrett's + Normal")
    log("Platform: GPL6102 Illumina HWG-6 V2")
    log("Survival data: YES")
    log("Framework: OrganismCore")
    log("Doc: 90d | Date: 2026-03-01")
    log("=" * 65)
    log("")
    log("PREDICTIONS LOCKED (from 90a/90b/90c):")
    log("SP-1: KRT20/HDAC1/APC panel OS assoc")
    log("SP-2: KRT20 alone OS assoc")
    log("SP-3: HDAC1 alone OS assoc")
    log("SP-4: APC alone OS assoc (low=worse)")
    log("SP-5: Panel > individual gene")
    log("ZA-1: r(ZEB2,AURKA) > 0 in EAC")
    log("ZA-2: r(ZEB2,AURKA) > 0.60 in EAC")
    log("ZA-3: Barrett intermediate coupling")
    log("PG-1: Normal < Barrett < EAC depth")
    log("PG-2: ZEB1 Normal > EAC")
    log("PG-3: TFF1 EAC > Normal")
    log("PG-4: CDH1 Normal > EAC")
    log("PG-5: EZH2 EAC > Normal")
    log("PG-6: HDAC1 EAC > Normal")
    log("CP-1: GSE26886 patterns replicate")
    log("CP-2: r(KRT20,depth) > 0.50 in EAC")
    log("CP-3: r(APC,depth) < -0.30 in EAC")

    # Download
    log("")
    log("=" * 65)
    log("STEP 0: DATA ACQUISITION")
    log("=" * 65)
    ok = download_file(
        MATRIX_URL, MATRIX_FILE
    )
    if not ok:
        log("  FATAL: Download failed")
        write_log()
        return

    # Parse
    result = parse_series_matrix(MATRIX_FILE)
    if result[0] is None:
        log("  FATAL: Parse failed")
        write_log()
        return

    df_genes, meta, char_rows = result

    if len(df_genes.columns) == 0:
        log("  FATAL: Zero genes mapped")
        log("  Illumina probe IDs may differ")
        log("  Check actual IDs above")
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
        log(f"  {g:<12}: {len(df)} samples")

    if len(groups) < 2:
        log("  FATAL: < 2 groups found")
        write_log()
        return

    eac  = groups.get("EAC", pd.DataFrame())
    norm = groups.get("Normal",
                      pd.DataFrame())
    barr = groups.get("Barrett",
                      pd.DataFrame())

    # Extract survival
    surv_df = extract_survival(
        df_genes, meta,
        char_rows, group_series,
    )

    # Validation 1 — Survival panel
    survival_results = None
    if len(eac) >= 5:
        survival_results = survival_panel_test(
            eac, surv_df
        )

    # Validation 2 — ZEB2-AURKA
    zeb2_aurka_results = zeb2_aurka_validation(
        groups
    )

    # Validation 3 — Progression geometry
    depth_dict = progression_geometry(
        groups, group_order
    )

    # Cross-platform validation
    if len(eac) >= 5 and "EAC" in depth_dict:
        cross_platform_validation(
            eac, depth_dict["EAC"]
        )

    # ZEB2-AURKA deep dive
    if len(eac) >= 5:
        zeb2_aurka_deep(eac)

    # Figure
    generate_figure(
        groups, depth_dict,
        survival_results,
        zeb2_aurka_results,
        group_order,
    )

    # Save outputs
    for label, d in depth_dict.items():
        if d is not None:
            d.to_csv(
                os.path.join(
                    RESULTS_DIR,
                    f"depth_s3_{label.lower()}.csv",
                ),
                header=["depth_s3"],
            )

    if survival_results is not None:
        out_surv = pd.DataFrame({
            "t":     survival_results["t"],
            "e":     survival_results["e"],
            "panel": survival_results[
                "panel_score"
            ],
            "hi":    survival_results["hi"],
        })
        out_surv.to_csv(
            os.path.join(
                RESULTS_DIR,
                "survival_panel_eac.csv",
            ),
            index=False,
        )

    write_log()
    log(f"\n  Log    : {LOG_FILE}")
    log(f"  Output : {RESULTS_DIR}")
    log("\n=== SCRIPT 3 COMPLETE ===")
    log("\nPaste full output for Document 90d.")


if __name__ == "__main__":
    main()
