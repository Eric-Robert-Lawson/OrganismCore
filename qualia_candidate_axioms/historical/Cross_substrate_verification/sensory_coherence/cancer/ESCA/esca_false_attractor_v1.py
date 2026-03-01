"""
ESOPHAGEAL CANCER — FALSE ATTRACTOR ANALYSIS
SCRIPT 1 — DISCOVERY RUN
Dataset: GSE26886
  Gene expression profiling of Barrett's
  esophagus, adenocarcinoma, esophageal
  squamous epithelium and squamous cell
  carcinoma
  Platform: GPL570 Affymetrix HGU133Plus2
  N=166 total
  Groups: Barrett's / EAC / Normal squamous
          / ESCC — all labeled

FRAMEWORK: OrganismCore Principles-First
Doc: 90a | Date: 2026-03-01

DATASET SELECTION RATIONALE:
  GSE26886 chosen after systematic
  discovery script (90_discovery).
  Contains both ESCC and EAC labeled.
  Affymetrix GPL570 — standard probes.
  Normal squamous epithelium present.
  Cross-subtype predictions testable.
  GSE72094 rejected — confirmed LUAD
  not ESCC (discovery script verified).
  GSE53625 deferred — numeric probe IDs
  require GPL18109 annotation (HTTP 404).

PREDICTIONS LOCKED 2026-03-01
(before data loaded):

ESCC PREDICTIONS:
  Switch genes (DOWN in ESCC vs normal):
    NOTCH1  — squamous differentiation TF
    KRT1    — suprabasal keratin
    KRT10   — suprabasal keratin
    SPRR1A  — cornified envelope protein
    LORICRIN / IVL — terminal markers
  FA markers (UP in ESCC):
    SOX2    — basal TF / 3q amplification
    TP63    — basal squamous TF / 3q amp
    KRT5    — basal keratin retained
    KRT14   — basal keratin retained
    EGFR    — basal proliferation signal
    CCND1   — 11q amplification
  Epigenetic: EZH2 UP (gain-of-function lock)
  Drug targets: EGFR / CDK4/6 / EZH2i /
                NOTCH pathway

EAC PREDICTIONS:
  Switch genes (DOWN in EAC vs normal):
    NOTCH1  — differentiation signal
    CDH1    — epithelial identity
    KLF4    — columnar differentiation TF
    MUC6    — gastric mucin
  FA markers (UP in EAC):
    CDX2    — intestinal TF
    ERBB2   — HER2 amplified ~30%
    ZEB1    — EMT TF
    AURKA   — mitotic kinase
  Epigenetic: EZH2 UP
  Drug targets: Trastuzumab / Alisertib /
                CDK4/6 / Ramucirumab

CROSS-SUBTYPE PREDICTIONS:
  1. EAC deeper attractor than ESCC
  2. ZEB2-AURKA r>0.80 in EAC /
     r<0.50 in ESCC
     (STAD reference: r=+0.9871)
  3. CDX2 circuit broken in EAC
     (same as STAD)
  4. SOX2 elevated in ESCC not EAC
  5. Barrett's intermediate between
     normal and EAC on depth score

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
RESULTS_DIR = os.path.join(BASE_DIR, "results")
LOG_FILE    = os.path.join(
    RESULTS_DIR,
    "analysis_log_gse26886.txt",
)

os.makedirs(BASE_DIR,    exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

GEO_ACC    = "GSE26886"
MATRIX_URL = (
    "https://ftp.ncbi.nlm.nih.gov/geo/series/"
    "GSE26nnn/GSE26886/matrix/"
    "GSE26886_series_matrix.txt.gz"
)
MATRIX_FILE = os.path.join(
    BASE_DIR, "GSE26886_series_matrix.txt.gz"
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
# AFFYMETRIX HGU133Plus2 PROBE MAP
# GPL570 — hard-coded for target genes
# ============================================================

PROBE_MAP = {
    # Squamous differentiation / switch
    "209183_s_at": "NOTCH1",
    "209130_at":   "KRT1",
    "210633_x_at": "KRT10",
    "205555_s_at": "SPRR1A",
    "206360_at":   "LORICRIN",
    "207724_s_at": "KRT4",
    "210602_s_at": "KRT13",
    "214599_at":   "IVL",
    "205277_at":   "DSG3",
    "204998_s_at": "DSG1",
    # Basal squamous / FA markers
    "213541_s_at": "SOX2",
    "209905_at":   "TP63",
    "201820_at":   "KRT5",
    "201667_s_at": "KRT14",
    "201983_s_at": "EGFR",
    "208712_at":   "CCND1",
    "204579_at":   "FGFR1",
    "212791_at":   "MYC",
    "214854_at":   "PIK3CA",
    # Intestinal / EAC markers
    "209288_s_at": "CDX2",
    "207257_at":   "MUC2",
    "213599_at":   "KRT20",
    "201843_s_at": "TFF3",
    "205014_at":   "MUC5B",
    # Gastric markers
    "204683_at":   "TFF1",
    "207147_at":   "MUC5AC",
    "220752_at":   "GKN1",
    "219446_at":   "CLDN18",
    "209189_at":   "PGC",
    # EMT markers
    "203131_at":   "ZEB2",
    "218559_s_at": "ZEB1",
    "209763_at":   "SNAI2",
    "216262_s_at": "SNAI1",
    "214451_at":   "TWIST1",
    "201131_s_at": "FN1",
    "201130_s_at": "CDH2",
    "201733_at":   "CDH1",
    "201858_s_at": "VIM",
    # Mitotic / proliferation
    "204418_at":   "AURKA",
    "202095_s_at": "MKI67",
    "201291_s_at": "TOP2A",
    "203213_at":   "CDC20",
    "214710_s_at": "CCNB1",
    "202240_at":   "PLK1",
    "201202_at":   "PCNA",
    # Cell cycle / suppressors
    "208641_s_at": "CDK4",
    "209644_x_at": "CDKN2A",
    "202284_s_at": "CDKN1A",
    "202107_s_at": "RB1",
    "201015_s_at": "CCNE1",
    # Drug targets / RTKs
    "216836_s_at": "ERBB2",
    "205047_s_at": "ERBB3",
    "209091_at":   "ERBB4",
    "213807_at":   "MET",
    "204363_at":   "FGFR2",
    "210512_s_at": "VEGFA",
    "203934_at":   "KDR",
    # Apoptosis
    "203685_at":   "BCL2",
    "200797_s_at": "MCL1",
    "211300_s_at": "BAX",
    # Epigenetic
    "203358_s_at": "EZH2",
    "212155_at":   "KDM6A",
    "218457_at":   "DNMT3A",
    "214651_s_at": "TET2",
    "201833_at":   "HDAC1",
    "220436_s_at": "HDAC2",
    # Wnt pathway
    "201474_s_at": "CTNNB1",
    "205990_s_at": "WNT5A",
    "204990_s_at": "APC",
    "222696_at":   "AXIN2",
    # NOTCH
    "209807_at":   "NOTCH2",
    "209097_at":   "JAG1",
    "203411_s_at": "HES1",
    # TGF-B
    "203085_s_at": "TGFB1",
    "212171_at":   "TGFB2",
    "213815_at":   "TGFBR1",
    "204791_at":   "TGFBR2",
    # p53 / DNA damage
    "201746_at":   "TP53",
    "207035_at":   "MDM2",
    # MMR
    "212897_at":   "MLH1",
    "214057_at":   "MSH6",
    # Hypoxia
    "200989_at":   "HIF1A",
    "200650_s_at": "LDHA",
    # Immune
    "206804_at":   "CD8A",
    "206026_s_at": "FOXP3",
    "207429_at":   "PDCD1",
    "223834_at":   "CD274",
    # CDK6 separate probe
    "207828_at":   "CDK6",
}

# Reverse map: gene -> list of probes
GENE_TO_PROBES = {}
for probe, gene in PROBE_MAP.items():
    if gene not in GENE_TO_PROBES:
        GENE_TO_PROBES[gene] = []
    GENE_TO_PROBES[gene].append(probe)

TARGET_GENES = sorted(set(PROBE_MAP.values()))

# ============================================================
# STEP 0: DOWNLOAD
# ============================================================

def download_file(url, dest):
    if os.path.exists(dest):
        log(f"  Already present: {dest} "
            f"({os.path.getsize(dest):,} bytes)")
        return True
    log(f"  Downloading: {url}")
    try:
        r = requests.get(url, timeout=180)
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
# STEP 1: PARSE SERIES MATRIX
# ============================================================

def parse_series_matrix(filepath):
    log("")
    log("=" * 65)
    log("STEP 1: PARSE SERIES MATRIX")
    log(f"  File: {filepath}")
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
                parts = line.split("\t")
                parts = [
                    p.strip().strip('"')
                    for p in parts
                ]

                if not header_cols:
                    header_cols = parts
                    continue

                if not parts or not parts[0]:
                    continue

                probe_id = parts[0]

                # Only keep probes in our map
                if probe_id not in PROBE_MAP:
                    continue

                try:
                    vals = [
                        float(p)
                        if p not in [
                            "", "null", "NA",
                            "nan", "N/A",
                        ]
                        else np.nan
                        for p in parts[1:]
                    ]
                except ValueError:
                    continue

                n_expected = len(header_cols) - 1
                if len(vals) != n_expected:
                    continue

                probe_ids.append(probe_id)
                rows.append(vals)

    log(f"  Sample IDs   : {len(sample_ids)}")
    log(f"  Sample titles: {len(sample_titles)}")
    log(f"  Probes found : {len(probe_ids)}")
    log(f"  Header cols  : "
        f"{len(header_cols) - 1 if header_cols else 0}")

    log(f"\n  Title examples:")
    for t in sample_titles[:8]:
        log(f"    {t}")

    if not probe_ids:
        log("")
        log("  WARNING: No target probes found.")
        log("  Inspecting actual probe IDs...")
        _inspect_probes(filepath)
        return None, None, None

    # Build expression dataframe
    cols = header_cols[1:] if header_cols else []
    if len(cols) == 0 and sample_ids:
        cols = sample_ids

    n_cols = len(rows[0]) if rows else 0
    cols   = cols[:n_cols]

    df = pd.DataFrame(
        rows,
        index=probe_ids,
        columns=cols,
        dtype=float,
    )
    log(f"\n  Raw matrix "
        f"(probes x samples): {df.shape}")

    # Map probes to genes
    gene_expr   = {}
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
    log(f"  Genes found  : "
        f"{sorted(genes_found)}")

    # Build metadata
    meta = pd.DataFrame(index=df_genes.index)
    if len(sample_titles) == len(df_genes):
        meta["title"] = sample_titles
    elif (sample_ids
          and len(sample_titles)
              == len(sample_ids)):
        title_map = dict(
            zip(sample_ids, sample_titles)
        )
        meta["title"] = [
            title_map.get(s, "")
            for s in df_genes.index
        ]

    return df_genes, meta, char_rows


def _inspect_probes(filepath):
    """Show first 30 probe IDs from file."""
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
            if len(seen) >= 30:
                break
    log(f"  First 30 actual probe IDs:")
    for p in seen:
        log(f"    {p}")

# ============================================================
# STEP 2: CLASSIFY SAMPLES
# ============================================================

def classify_samples(df_genes, meta):
    log("")
    log("=" * 65)
    log("STEP 2: CLASSIFY SAMPLES")
    log("Barrett / EAC / Normal / ESCC")
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
        ]):
            groups.append("Barrett")
        elif any(x in title for x in [
            "adenocarcinoma", "eac", "adeno",
        ]):
            groups.append("EAC")
        elif any(x in title for x in [
            "squamous cell carcinoma",
            "escc", "scc",
            "squamous_c", "sq_ca",
        ]):
            groups.append("ESCC")
        elif any(x in title for x in [
            "normal", "squamous epithelium",
            "sq_epi", "sq epi", "nse",
            "normal squamous",
            "squamous epitheliu",
        ]):
            groups.append("Normal")
        else:
            groups.append("Unknown")

    group_series = pd.Series(
        groups, index=df_genes.index
    )

    log(f"\n  Group counts:")
    for g, n in group_series.value_counts(
    ).items():
        log(f"    {g}: {n}")

    log(f"\n  First 10 samples classified:")
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
        g = group_series[s]
        log(f"    {s[:12]:<12} → "
            f"{g:<10} {title}")

    n_unk = (group_series == "Unknown").sum()
    if n_unk > 5:
        log(f"\n  WARNING: {n_unk} Unknown")
        log(f"  All unique titles:")
        if (
            meta is not None
            and "title" in meta.columns
        ):
            for t in meta["title"].unique():
                log(f"    {t}")

    return group_series

# ============================================================
# STEP 3: SADDLE POINT ANALYSIS
# ============================================================

ESCC_SWITCH = [
    "NOTCH1", "KRT1", "KRT10",
    "SPRR1A", "LORICRIN", "KRT4",
    "KRT13", "IVL", "DSG1",
]

ESCC_FA = [
    "SOX2", "TP63", "KRT5", "KRT14",
    "EGFR", "CCND1", "FGFR1", "MYC",
]

EAC_SWITCH = [
    "NOTCH1", "CDH1", "MUC6",
    "MUC5AC", "TFF1", "GKN1",
]

EAC_FA = [
    "CDX2", "ERBB2", "ZEB1",
    "AURKA", "MUC2", "KRT20",
    "TFF3", "VEGFA",
]


def saddle_analysis(
    tumor, normal, switch, fa, label
):
    log("")
    log(f"  === {label} SADDLE POINT ===")
    log(f"  T={len(tumor)} | N={len(normal)}")
    log(
        f"\n  {'Gene':<12} {'Normal':>9} "
        f"{'Tumor':>9} {'Change':>8}  "
        f"Supp-p         Elev-p      "
        f"[Pred] Result"
    )
    log(f"  {'-'*85}")

    results = []
    gc_t    = list(tumor.columns)
    gc_n    = list(normal.columns)

    panel = (
        [(g, "DOWN") for g in switch]
        + [(g, "UP") for g in fa]
    )

    for gene, pred in panel:
        if gene not in gc_t:
            log(f"  {gene:<12} NOT IN MATRIX")
            continue

        nm = (
            normal[gene].mean()
            if gene in gc_n
            else np.nan
        )
        tm  = tumor[gene].mean()
        chg = (
            (tm - nm) / abs(nm) * 100
            if (
                not np.isnan(nm)
                and abs(nm) > 0.01
            )
            else np.nan
        )

        n_v = (
            normal[gene].values
            if gene in gc_n
            else np.array([])
        )
        t_v = tumor[gene].values

        _, p_s = safe_mwu(t_v, n_v, "less")
        _, p_e = safe_mwu(t_v, n_v, "greater")

        if pred == "DOWN":
            if (
                not np.isnan(p_s)
                and p_s < 0.05
            ):
                res = "CONFIRMED ✓"
            elif (
                not np.isnan(p_e)
                and p_e < 0.05
            ):
                res = "INVERTED  ✗"
            else:
                res = "flat      ~"
        else:
            if (
                not np.isnan(p_e)
                and p_e < 0.05
            ):
                res = "CONFIRMED ✓"
            elif (
                not np.isnan(p_s)
                and p_s < 0.05
            ):
                res = "INVERTED  ✗"
            else:
                res = "flat      ~"

        cs = (
            f"{chg:+.1f}%"
            if not np.isnan(chg)
            else "N/A"
        )
        log(
            f"  {gene:<12} "
            f"{nm:>9.4f} {tm:>9.4f} "
            f"{cs:>8}  "
            f"{fmt_p(p_s):>14}  "
            f"{fmt_p(p_e):>14}  "
            f"[{pred}] {res}"
        )

        results.append({
            "gene":   gene,
            "pred":   pred,
            "normal": nm,
            "tumor":  tm,
            "change": chg,
            "p_supp": p_s,
            "p_elev": p_e,
            "result": res,
        })

    df_r = pd.DataFrame(results)
    conf = df_r["result"].str.contains(
        "CONFIRMED"
    ).sum()
    inv  = df_r["result"].str.contains(
        "INVERTED"
    ).sum()
    log(
        f"\n  {label}: "
        f"{conf} confirmed / "
        f"{inv} inverted"
    )
    return df_r

# ============================================================
# STEP 4: EXTENDED GENE SURVEY
# ============================================================

def gene_survey(groups_dict, group_order):
    log("")
    log("=" * 65)
    log("STEP 4: EXTENDED GENE SURVEY")
    log("All target genes across all groups")
    log("=" * 65)

    all_gc = set()
    for df in groups_dict.values():
        all_gc.update(df.columns)

    results = []
    for gene in sorted(all_gc):
        row = {"gene": gene}
        for grp in group_order:
            if grp in groups_dict:
                df = groups_dict[grp]
                row[f"{grp}_mean"] = (
                    df[gene].mean()
                    if gene in df.columns
                    else np.nan
                )
        results.append(row)

    df_s = pd.DataFrame(results)

    if (
        "EAC_mean" in df_s.columns
        and "Normal_mean" in df_s.columns
    ):
        df_s["eac_vs_norm"] = (
            df_s["EAC_mean"]
            - df_s["Normal_mean"]
        )
        df_s = df_s.sort_values(
            "eac_vs_norm", ascending=False
        )

    # Header as single string
    header = f"  {'Gene':<12}"
    for g in group_order:
        header += f" {g[:10]:>12}"
    log(header)
    log(f"  {'-'*60}")

    for _, row in df_s.iterrows():
        if row["gene"] not in TARGET_GENES:
            continue
        line = f"  {row['gene']:<12}"
        for g in group_order:
            v = row.get(f"{g}_mean", np.nan)
            if not np.isnan(v):
                line += f" {v:>12.4f}"
            else:
                line += f" {'N/A':>12}"
        log(line)

    return df_s

# ============================================================
# STEP 5: DEPTH SCORE
# ============================================================

def build_depth_score(df, switch, fa, label):
    log(f"\n  Depth score: {label} "
        f"(n={len(df)})")
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
        depth += norm01(df[fa_].mean(axis=1))
        n += 1
    if n > 0:
        depth /= n

    log(
        f"    Mean={depth.mean():.4f} "
        f"Std={depth.std():.4f} "
        f"Min={depth.min():.4f} "
        f"Max={depth.max():.4f}"
    )
    return depth

# ============================================================
# STEP 6: DEPTH CORRELATIONS
# ============================================================

def depth_correlations(df, depth, label):
    log(f"\n  Depth correlations: {label}")
    corrs = []
    for gene in df.columns:
        rv, pv = safe_pearsonr(
            depth.values, df[gene].values
        )
        if not np.isnan(rv):
            corrs.append((gene, rv, pv))

    corrs.sort(
        key=lambda x: abs(x[1]),
        reverse=True,
    )

    log(
        f"\n  TOP 15 POSITIVE "
        f"(UP in deep {label}):"
    )
    log(f"  {'Gene':<12} {'r':>8}  p-value")
    log(f"  {'-'*35}")
    for g, r, p in [
        x for x in corrs if x[1] > 0
    ][:15]:
        log(
            f"  {g:<12} {r:>+8.4f}  "
            f"{fmt_p(p)}"
        )

    log(
        f"\n  TOP 15 NEGATIVE "
        f"(DOWN in deep {label}):"
    )
    log(f"  {'Gene':<12} {'r':>8}  p-value")
    log(f"  {'-'*35}")
    for g, r, p in [
        x for x in corrs if x[1] < 0
    ][:15]:
        log(
            f"  {g:<12} {r:>+8.4f}  "
            f"{fmt_p(p)}"
        )

    return corrs

# ============================================================
# STEP 7: ZEB2-AURKA COUPLING TEST
# ============================================================

def zeb2_aurka_test(escc, eac):
    log("")
    log("=" * 65)
    log("STEP 7: ZEB2-AURKA COUPLING TEST")
    log("STAD reference: r=+0.9871 ***")
    log("Prediction:")
    log("  EAC : r > 0.80 (columnar origin)")
    log("  ESCC: r < 0.50 (squamous origin)")
    log("=" * 65)

    for label, df in [
        ("ESCC", escc),
        ("EAC",  eac),
    ]:
        gc = list(df.columns)
        if (
            "ZEB2" not in gc
            or "AURKA" not in gc
        ):
            log(f"  {label}: ZEB2/AURKA missing")
            continue

        rv, pv = safe_pearsonr(
            df["ZEB2"].values,
            df["AURKA"].values,
        )
        log(f"\n  {label} (n={len(df)}):")
        log(
            f"  r(ZEB2, AURKA) = {rv:+.4f}  "
            f"{fmt_p(pv)}"
        )
        if not np.isnan(rv):
            log(f"  r² = {rv**2:.4f}")
            if label == "EAC":
                if rv > 0.80:
                    log(
                        "  PREDICTION CONFIRMED ✓ "
                        "(r>0.80 in EAC)"
                    )
                elif rv > 0.50:
                    log(
                        "  PARTIAL — "
                        "moderate coupling"
                    )
                else:
                    log(
                        "  PREDICTION NOT "
                        "CONFIRMED ✗"
                    )
            else:
                if rv < 0.50:
                    log(
                        "  PREDICTION CONFIRMED ✓ "
                        "(r<0.50 in ESCC)"
                    )
                else:
                    log(
                        "  PREDICTION NOT "
                        "CONFIRMED ✗"
                    )

# ============================================================
# STEP 8: CDX2 CIRCUIT TEST
# ============================================================

def cdx2_circuit_test(eac, normal):
    log("")
    log("=" * 65)
    log("STEP 8: CDX2 CIRCUIT TEST (EAC)")
    log("STAD: 1/5 targets intact — broken")
    log("Prediction: circuit broken in EAC")
    log("=" * 65)

    gc = list(eac.columns)

    if "CDX2" not in gc:
        log("  CDX2 not in matrix")
        return

    log(
        f"  CDX2 mean in EAC  : "
        f"{eac['CDX2'].mean():.4f}"
    )
    if "CDX2" in normal.columns:
        log(
            f"  CDX2 mean in Normal: "
            f"{normal['CDX2'].mean():.4f}"
        )

    targets = [
        "MUC2", "KRT20", "TFF3",
        "MUC5B", "CLDN18",
    ]

    log(
        f"\n  CDX2 → target correlations (EAC):"
    )
    log(
        f"  {'Target':<10} {'r':>8}  "
        f"p-value        Status"
    )
    log(f"  {'-'*50}")

    intact = 0
    tested = 0
    for tgt in targets:
        if tgt not in gc:
            continue
        rv, pv = safe_pearsonr(
            eac["CDX2"].values,
            eac[tgt].values,
        )
        tested += 1
        if not np.isnan(rv):
            if rv > 0.15 and pv < 0.05:
                status = "intact ✓"
                intact += 1
            elif rv < -0.15 and pv < 0.05:
                status = "inverted"
            else:
                status = "broken"
            log(
                f"  {tgt:<10} {rv:>+8.4f}  "
                f"{fmt_p(pv):>14}  {status}"
            )
        else:
            log(f"  {tgt:<10} N/A")

    log(
        f"\n  CDX2 circuit: "
        f"{intact}/{tested} intact"
    )
    if intact <= 2:
        log(
            "  PREDICTION CONFIRMED: "
            "circuit broken ✓"
        )
    else:
        log(
            "  Circuit more intact "
            "than predicted"
        )

# ============================================================
# STEP 9: SOX2 SUBTYPE COMPARISON
# ============================================================

def sox2_comparison(escc, eac, normal):
    log("")
    log("=" * 65)
    log("STEP 9: SOX2 SUBTYPE COMPARISON")
    log("Prediction: SOX2 high ESCC / low EAC")
    log("=" * 65)

    markers = [
        "SOX2", "TP63", "KRT5", "KRT14",
        "CDX2", "MUC2", "ERBB2", "EGFR",
    ]

    log(
        f"\n  {'Gene':<10} {'Normal':>10} "
        f"{'ESCC':>10} {'EAC':>10}  "
        f"ESCC vs EAC"
    )
    log(f"  {'-'*55}")

    for gene in markers:
        nm = (
            normal[gene].mean()
            if gene in normal.columns
            else np.nan
        )
        em = (
            escc[gene].mean()
            if gene in escc.columns
            else np.nan
        )
        am = (
            eac[gene].mean()
            if gene in eac.columns
            else np.nan
        )
        _, pp = safe_mwu(
            escc[gene].values
            if gene in escc.columns
            else np.array([]),
            eac[gene].values
            if gene in eac.columns
            else np.array([]),
            "two-sided",
        )
        log(
            f"  {gene:<10} "
            f"{nm:>10.4f} {em:>10.4f} "
            f"{am:>10.4f}  {fmt_p(pp)}"
        )

    if (
        "SOX2" in escc.columns
        and "SOX2" in eac.columns
    ):
        _, p_sox2 = safe_mwu(
            escc["SOX2"].values,
            eac["SOX2"].values,
            "greater",
        )
        log(
            f"\n  SOX2 ESCC > EAC: "
            f"{fmt_p(p_sox2)}"
        )
        if (
            not np.isnan(p_sox2)
            and p_sox2 < 0.05
        ):
            log("  PREDICTION CONFIRMED ✓")
        else:
            log("  PREDICTION NOT CONFIRMED ✗")

# ============================================================
# STEP 10: BARRETT'S PROGRESSION
# ============================================================

def barretts_progression(
    normal, barretts, eac,
    depth_n, depth_b, depth_e,
):
    log("")
    log("=" * 65)
    log("STEP 10: BARRETT'S PROGRESSION")
    log("Normal → Barrett's → EAC")
    log("Prediction: depth increases")
    log("=" * 65)

    log(
        f"\n  {'Group':<14} {'n':>4}  "
        f"{'depth_mean':>10}  depth_std"
    )
    log(f"  {'-'*45}")

    for lbl, df, d in [
        ("Normal",    normal,    depth_n),
        ("Barrett's", barretts,  depth_b),
        ("EAC",       eac,       depth_e),
    ]:
        if d is None or len(df) == 0:
            log(f"  {lbl:<14} {0:>4}  N/A")
            continue
        log(
            f"  {lbl:<14} {len(df):>4}  "
            f"{d.mean():>10.4f}  "
            f"{d.std():>9.4f}"
        )

    if (
        depth_n is not None
        and depth_b is not None
        and depth_e is not None
        and len(depth_n) > 0
        and len(depth_b) > 0
        and len(depth_e) > 0
    ):
        _, p_nb = safe_mwu(
            depth_b.values,
            depth_n.values,
            "greater",
        )
        _, p_be = safe_mwu(
            depth_e.values,
            depth_b.values,
            "greater",
        )
        _, p_ne = safe_mwu(
            depth_e.values,
            depth_n.values,
            "greater",
        )
        log(
            f"\n  Barrett > Normal : "
            f"{fmt_p(p_nb)}"
        )
        log(
            f"  EAC > Barrett    : "
            f"{fmt_p(p_be)}"
        )
        log(
            f"  EAC > Normal     : "
            f"{fmt_p(p_ne)}"
        )
        if not np.isnan(p_ne) and p_ne < 0.05:
            log(
                "  Progression confirmed: "
                "Normal → EAC ✓"
            )
        if not np.isnan(p_be) and p_be < 0.05:
            log(
                "  Barrett intermediate "
                "confirmed ✓"
            )

# ============================================================
# STEP 11: DRUG TARGET DERIVATION
# ============================================================

def drug_targets(corrs_escc, corrs_eac):
    log("")
    log("=" * 65)
    log("STEP 11: DRUG TARGET DERIVATION")
    log("From depth correlations")
    log("Stated BEFORE literature check")
    log("=" * 65)

    known_drugs = {
        "EGFR":   "Cetuximab/Erlotinib/Afatinib",
        "ERBB2":  "Trastuzumab/Lapatinib",
        "FGFR1":  "Erdafitinib/Futibatinib",
        "FGFR2":  "Erdafitinib/Futibatinib",
        "MET":    "Savolitinib/Crizotinib",
        "CDK4":   "Palbociclib/Ribociclib",
        "CDK6":   "Palbociclib/Ribociclib",
        "CCND1":  "CDK4/6i (via CCND1)",
        "AURKA":  "Alisertib",
        "TOP2A":  "Anthracyclines/TopoII",
        "EZH2":   "Tazemetostat",
        "HDAC1":  "Vorinostat/Entinostat",
        "HDAC2":  "Vorinostat/Entinostat",
        "VEGFA":  "Bevacizumab/Ramucirumab",
        "KDR":    "Ramucirumab",
        "BCL2":   "Venetoclax",
        "MCL1":   "AMG-176/S63845",
        "MYC":    "BET inhibitor (indirect)",
        "PIK3CA": "Alpelisib/Idelalisib",
        "TGFBR1": "Galunisertib/Vactosertib",
        "NOTCH1": "Gamma-secretase inhibitor",
        "HIF1A":  "PT2977/Belzutifan",
    }

    for label, corrs in [
        ("ESCC", corrs_escc),
        ("EAC",  corrs_eac),
    ]:
        if not corrs:
            continue
        log(f"\n  {label} DRUG TARGETS "
            f"(depth-correlated):")
        log(
            f"  {'Gene':<10} {'r':>8}  Drug"
        )
        log(f"  {'-'*55}")
        for gene, rv, pv in corrs:
            if gene in known_drugs:
                log(
                    f"  {gene:<10} {rv:>+8.4f}  "
                    f"{known_drugs[gene]}"
                )

# ============================================================
# STEP 12: FIGURE
# ============================================================

def generate_figure(
    groups, depth_dict, corrs_dict,
    group_order,
):
    log("")
    log("--- Generating figure ---")

    fig = plt.figure(figsize=(28, 22))
    fig.suptitle(
        "Esophageal Cancer — False Attractor "
        "Analysis\n"
        "Script 1 | GSE26886 | "
        "Barrett / EAC / Normal / ESCC\n"
        "OrganismCore | 2026-03-01 | "
        "Predictions locked before data",
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

    def gc(g):
        return COLORS.get(g, "#95a5a6")

    w = 0.2

    # A — Squamous markers
    ax_a = fig.add_subplot(gs[0, 0])
    sq_genes = [
        g for g in [
            "SOX2", "TP63", "KRT5",
            "NOTCH1", "KRT1", "KRT10",
        ]
        if any(
            g in grp.columns
            for grp in groups.values()
        )
    ]
    if sq_genes:
        x = np.arange(len(sq_genes))
        for i, grp_name in enumerate(
            ["Normal", "ESCC", "EAC"]
        ):
            if grp_name not in groups:
                continue
            df = groups[grp_name]
            means = [
                df[g].mean()
                if g in df.columns else 0
                for g in sq_genes
            ]
            sems = [
                df[g].sem()
                if g in df.columns else 0
                for g in sq_genes
            ]
            ax_a.bar(
                x + (i - 1) * w,
                means, w,
                color=gc(grp_name),
                label=grp_name,
                yerr=sems,
                capsize=3,
                alpha=0.85,
            )
        ax_a.set_xticks(x)
        ax_a.set_xticklabels(
            sq_genes, rotation=45,
            ha="right", fontsize=7,
        )
        ax_a.legend(fontsize=6)
    ax_a.set_title(
        "A — Squamous / SOX2 / TP63\n"
        "Normal vs ESCC vs EAC",
        fontsize=9,
    )
    ax_a.set_ylabel("Expression", fontsize=8)

    # B — EAC / intestinal markers
    ax_b = fig.add_subplot(gs[0, 1])
    int_genes = [
        g for g in [
            "CDX2", "MUC2", "TFF3",
            "ERBB2", "KRT20", "CLDN18",
        ]
        if any(
            g in grp.columns
            for grp in groups.values()
        )
    ]
    if int_genes:
        x2 = np.arange(len(int_genes))
        for i, grp_name in enumerate(
            ["Normal", "Barrett", "EAC"]
        ):
            if grp_name not in groups:
                continue
            df = groups[grp_name]
            means = [
                df[g].mean()
                if g in df.columns else 0
                for g in int_genes
            ]
            sems = [
                df[g].sem()
                if g in df.columns else 0
                for g in int_genes
            ]
            ax_b.bar(
                x2 + (i - 1) * w,
                means, w,
                color=gc(grp_name),
                label=grp_name,
                yerr=sems,
                capsize=3,
                alpha=0.85,
            )
        ax_b.set_xticks(x2)
        ax_b.set_xticklabels(
            int_genes, rotation=45,
            ha="right", fontsize=7,
        )
        ax_b.legend(fontsize=6)
    ax_b.set_title(
        "B — EAC / Intestinal Markers\n"
        "Normal vs Barrett vs EAC",
        fontsize=9,
    )
    ax_b.set_ylabel("Expression", fontsize=8)

    # C — ZEB2-AURKA scatter
    ax_c = fig.add_subplot(gs[0, 2])
    for grp_name, marker in [
        ("ESCC", "o"),
        ("EAC",  "s"),
    ]:
        if grp_name not in groups:
            continue
        df = groups[grp_name]
        if (
            "ZEB2" in df.columns
            and "AURKA" in df.columns
        ):
            rv, _ = safe_pearsonr(
                df["ZEB2"].values,
                df["AURKA"].values,
            )
            ax_c.scatter(
                df["ZEB2"].values,
                df["AURKA"].values,
                alpha=0.5, s=25,
                color=gc(grp_name),
                marker=marker,
                label=(
                    f"{grp_name} "
                    f"r={rv:+.3f}"
                    if not np.isnan(rv)
                    else grp_name
                ),
            )
    ax_c.set_xlabel("ZEB2", fontsize=8)
    ax_c.set_ylabel("AURKA", fontsize=8)
    ax_c.set_title(
        "C — ZEB2-AURKA Coupling\n"
        "EAC pred r>0.80 / ESCC pred r<0.50\n"
        "STAD ref: r=+0.9871",
        fontsize=8,
    )
    ax_c.legend(fontsize=7)

    # D — Depth by group violin
    ax_d = fig.add_subplot(gs[1, 0])
    d_vals = []
    d_lbls = []
    for g in group_order:
        if (
            g in depth_dict
            and depth_dict[g] is not None
            and len(depth_dict[g]) > 0
        ):
            d_vals.append(depth_dict[g].values)
            d_lbls.append(g)
    if d_vals:
        parts = ax_d.violinplot(
            d_vals,
            positions=range(len(d_vals)),
            showmedians=True,
            showextrema=True,
        )
        for i, pc in enumerate(
            parts["bodies"]
        ):
            pc.set_facecolor(gc(d_lbls[i]))
            pc.set_alpha(0.7)
        ax_d.set_xticks(range(len(d_lbls)))
        ax_d.set_xticklabels(
            d_lbls, fontsize=8
        )
    ax_d.set_ylabel("Depth score", fontsize=8)
    ax_d.set_title(
        "D — Depth Score by Group\n"
        "Prediction: EAC deepest",
        fontsize=9,
    )

    # E — ESCC depth correlations
    ax_e = fig.add_subplot(gs[1, 1])
    if "ESCC" in corrs_dict and corrs_dict["ESCC"]:
        corrs = corrs_dict["ESCC"]
        top  = [
            (g, r) for g, r, p in corrs
            if r > 0
        ][:8]
        bot  = [
            (g, r) for g, r, p in corrs
            if r < 0
        ][:8]
        both = sorted(
            top + bot, key=lambda x: x[1]
        )
        if both:
            genes_ = [x[0] for x in both]
            vals_  = [x[1] for x in both]
            cols_  = [
                COLORS["ESCC"] if v < 0
                else "#f39c12"
                for v in vals_
            ]
            ax_e.barh(genes_, vals_,
                      color=cols_)
            ax_e.axvline(
                0, color="black",
                linewidth=0.8,
            )
            ax_e.tick_params(
                axis="y", labelsize=7
            )
    ax_e.set_xlabel("r with depth", fontsize=8)
    ax_e.set_title(
        "E — ESCC Depth Correlations",
        fontsize=9,
    )

    # F — EAC depth correlations
    ax_f = fig.add_subplot(gs[1, 2])
    if "EAC" in corrs_dict and corrs_dict["EAC"]:
        corrs = corrs_dict["EAC"]
        top  = [
            (g, r) for g, r, p in corrs
            if r > 0
        ][:8]
        bot  = [
            (g, r) for g, r, p in corrs
            if r < 0
        ][:8]
        both = sorted(
            top + bot, key=lambda x: x[1]
        )
        if both:
            genes_ = [x[0] for x in both]
            vals_  = [x[1] for x in both]
            cols_  = [
                COLORS["EAC"] if v < 0
                else "#f39c12"
                for v in vals_
            ]
            ax_f.barh(genes_, vals_,
                      color=cols_)
            ax_f.axvline(
                0, color="black",
                linewidth=0.8,
            )
            ax_f.tick_params(
                axis="y", labelsize=7
            )
    ax_f.set_xlabel("r with depth", fontsize=8)
    ax_f.set_title(
        "F — EAC Depth Correlations",
        fontsize=9,
    )

    # G — Epigenetic genes
    ax_g = fig.add_subplot(gs[2, 0])
    epi   = [
        "EZH2", "KDM6A", "DNMT3A",
        "HDAC1", "HDAC2",
    ]
    epi_a = [
        g for g in epi
        if any(
            g in grp.columns
            for grp in groups.values()
        )
    ]
    if epi_a:
        x3 = np.arange(len(epi_a))
        for i, grp_name in enumerate(
            ["Normal", "ESCC", "EAC"]
        ):
            if grp_name not in groups:
                continue
            df = groups[grp_name]
            means = [
                df[g].mean()
                if g in df.columns else 0
                for g in epi_a
            ]
            ax_g.bar(
                x3 + (i - 1) * w,
                means, w,
                color=gc(grp_name),
                label=grp_name,
                alpha=0.85,
            )
        ax_g.set_xticks(x3)
        ax_g.set_xticklabels(
            epi_a, rotation=45,
            ha="right", fontsize=8,
        )
        ax_g.legend(fontsize=6)
    ax_g.set_title(
        "G — Epigenetic Genes\n"
        "EZH2 predicted UP in both",
        fontsize=9,
    )

    # H — Barrett's progression scatter
    ax_h = fig.add_subplot(gs[2, 1])
    prog  = ["Normal", "Barrett", "EAC"]
    valid = [
        (g, depth_dict[g])
        for g in prog
        if g in depth_dict
        and depth_dict[g] is not None
        and len(depth_dict[g]) > 0
    ]
    if valid:
        for i, (g, d) in enumerate(valid):
            ax_h.scatter(
                [i] * len(d),
                d.values,
                alpha=0.4, s=18,
                color=gc(g),
            )
            ax_h.scatter(
                [i], [d.mean()],
                s=120, color=gc(g),
                zorder=5, marker="D",
                label=f"{g} μ={d.mean():.3f}",
            )
        ax_h.set_xticks(range(len(valid)))
        ax_h.set_xticklabels(
            [x[0] for x in valid],
            fontsize=8,
        )
        ax_h.legend(fontsize=7)
    ax_h.set_ylabel("Depth score", fontsize=8)
    ax_h.set_title(
        "H — Barrett's Progression\n"
        "Normal → Barrett → EAC",
        fontsize=9,
    )

    # I — Summary panel
    ax_i = fig.add_subplot(gs[2, 2])
    ax_i.axis("off")

    def _m(grp_name, gene):
        if (
            grp_name in groups
            and gene in groups[grp_name].columns
        ):
            return (
                f"{groups[grp_name][gene].mean():.4f}"
            )
        return "N/A"

    rv_escc = np.nan
    rv_eac  = np.nan
    if (
        "ESCC" in groups
        and "ZEB2" in groups["ESCC"].columns
        and "AURKA" in groups["ESCC"].columns
    ):
        rv_escc, _ = safe_pearsonr(
            groups["ESCC"]["ZEB2"].values,
            groups["ESCC"]["AURKA"].values,
        )
    if (
        "EAC" in groups
        and "ZEB2" in groups["EAC"].columns
        and "AURKA" in groups["EAC"].columns
    ):
        rv_eac, _ = safe_pearsonr(
            groups["EAC"]["ZEB2"].values,
            groups["EAC"]["AURKA"].values,
        )

    grp_ns = {
        g: len(groups[g])
        for g in groups
    }

    summary = (
        "I — SCRIPT 1 SUMMARY\n"
        "─────────────────────────────\n"
        f"Dataset: GSE26886\n"
        f"Groups : {grp_ns}\n\n"
        "ZEB2-AURKA COUPLING:\n"
        f"  ESCC r={rv_escc:+.4f} (pred <0.50)\n"
        f"  EAC  r={rv_eac:+.4f} (pred >0.80)\n"
        f"  STAD r=+0.9871 (reference)\n\n"
        "KEY MARKERS:\n"
        f"  SOX2  ESCC={_m('ESCC','SOX2')}"
        f" EAC={_m('EAC','SOX2')}\n"
        f"  TP63  ESCC={_m('ESCC','TP63')}"
        f" EAC={_m('EAC','TP63')}\n"
        f"  CDX2  ESCC={_m('ESCC','CDX2')}"
        f" EAC={_m('EAC','CDX2')}\n"
        f"  ERBB2 ESCC={_m('ESCC','ERBB2')}"
        f" EAC={_m('EAC','ERBB2')}\n"
        f"  EZH2  ESCC={_m('ESCC','EZH2')}"
        f" EAC={_m('EAC','EZH2')}\n"
        f"  AURKA ESCC={_m('ESCC','AURKA')}"
        f" EAC={_m('EAC','AURKA')}\n\n"
        "Framework: OrganismCore\n"
        "Doc: 90a | 2026-03-01"
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
        "esca_gse26886_s1.png",
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
    log("FALSE ATTRACTOR ANALYSIS — SCRIPT 1")
    log("Dataset: GSE26886")
    log("Framework: OrganismCore")
    log("Doc: 90a | Date: 2026-03-01")
    log("=" * 65)
    log("")
    log("DATASET RATIONALE:")
    log("  Selected after systematic discovery")
    log("  GSE26886: ESCC+EAC+Normal+Barrett")
    log("  GPL570 Affymetrix — standard probes")
    log("  GSE72094: REJECTED — confirmed LUAD")
    log("  GSE53625: DEFERRED — numeric probes")
    log("            GPL18109 annotation 404")
    log("")
    log("PREDICTIONS LOCKED 2026-03-01:")
    log("ESCC switch DOWN: "
        "NOTCH1/KRT1/KRT10/SPRR1A/IVL")
    log("ESCC FA UP      : "
        "SOX2/TP63/KRT5/EGFR/CCND1")
    log("EAC  switch DOWN: "
        "NOTCH1/CDH1/MUC6/MUC5AC")
    log("EAC  FA UP      : "
        "CDX2/ERBB2/ZEB1/AURKA")
    log("Cross: EAC deeper than ESCC")
    log("Cross: ZEB2-AURKA r>0.80 EAC"
        " / r<0.50 ESCC")
    log("Cross: CDX2 circuit broken in EAC")
    log("Cross: SOX2 ESCC > EAC")
    log("Cross: Barrett intermediate depth")

    # Download
    log("")
    log("=" * 65)
    log("STEP 0: DATA ACQUISITION")
    log("=" * 65)
    ok = download_file(MATRIX_URL, MATRIX_FILE)
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
        log("")
        log("  FATAL: Zero genes mapped.")
        log("  Check probe IDs above.")
        write_log()
        return

    # Classify samples
    group_series = classify_samples(
        df_genes, meta
    )

    # Separate groups
    groups = {}
    for g in [
        "Normal", "Barrett", "EAC", "ESCC"
    ]:
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

    normal   = groups.get("Normal",
                          pd.DataFrame())
    escc     = groups.get("ESCC",
                          pd.DataFrame())
    eac      = groups.get("EAC",
                          pd.DataFrame())
    barretts = groups.get("Barrett",
                          pd.DataFrame())

    # Saddle analysis
    log("")
    log("=" * 65)
    log("STEP 3: SADDLE POINT ANALYSIS")
    log("=" * 65)

    sad_escc = sad_eac = None
    if len(escc) >= 5 and len(normal) >= 3:
        sad_escc = saddle_analysis(
            escc, normal,
            ESCC_SWITCH, ESCC_FA, "ESCC",
        )
        sad_escc.to_csv(
            os.path.join(
                RESULTS_DIR,
                "saddle_escc_gse26886.csv",
            ),
            index=False,
        )

    if len(eac) >= 5 and len(normal) >= 3:
        sad_eac = saddle_analysis(
            eac, normal,
            EAC_SWITCH, EAC_FA, "EAC",
        )
        sad_eac.to_csv(
            os.path.join(
                RESULTS_DIR,
                "saddle_eac_gse26886.csv",
            ),
            index=False,
        )

    # Gene survey
    group_order = [
        "Normal", "Barrett", "EAC", "ESCC"
    ]
    survey = gene_survey(groups, group_order)

    # Depth scores
    log("")
    log("=" * 65)
    log("STEP 5+6: DEPTH SCORES AND "
        "CORRELATIONS")
    log("=" * 65)

    depth_dict = {}
    corrs_dict = {}

    if len(escc) >= 5:
        d_escc = build_depth_score(
            escc, ESCC_SWITCH, ESCC_FA, "ESCC"
        )
        depth_dict["ESCC"] = d_escc
        corrs_dict["ESCC"] = depth_correlations(
            escc, d_escc, "ESCC"
        )

    if len(eac) >= 5:
        d_eac = build_depth_score(
            eac, EAC_SWITCH, EAC_FA, "EAC"
        )
        depth_dict["EAC"] = d_eac
        corrs_dict["EAC"] = depth_correlations(
            eac, d_eac, "EAC"
        )

    if len(barretts) >= 3:
        depth_dict["Barrett"] = build_depth_score(
            barretts, EAC_SWITCH, EAC_FA,
            "Barrett",
        )

    if len(normal) >= 3:
        depth_dict["Normal"] = build_depth_score(
            normal, EAC_SWITCH, EAC_FA,
            "Normal",
        )

    # Cross-subtype depth comparison
    log("")
    log("=" * 65)
    log("CROSS-SUBTYPE DEPTH COMPARISON")
    log("Prediction: EAC deeper than ESCC")
    log("=" * 65)

    if (
        "ESCC" in depth_dict
        and "EAC" in depth_dict
    ):
        d_e  = depth_dict["ESCC"]
        d_ea = depth_dict["EAC"]
        log(f"\n  ESCC depth: "
            f"{d_e.mean():.4f} ± "
            f"{d_e.std():.4f}")
        log(f"  EAC  depth: "
            f"{d_ea.mean():.4f} ± "
            f"{d_ea.std():.4f}")
        _, pp = safe_mwu(
            d_ea.values, d_e.values,
            "two-sided",
        )
        log(f"  EAC vs ESCC: {fmt_p(pp)}")
        if d_ea.mean() > d_e.mean():
            if not np.isnan(pp) and pp < 0.05:
                log("  PREDICTION CONFIRMED: "
                    "EAC deeper ✓")
            else:
                log("  Trend: EAC deeper, "
                    "not significant")
        else:
            log("  PREDICTION NOT CONFIRMED: "
                "ESCC deeper or equal")

    # Cross-cancer tests
    log("")
    log("=" * 65)
    log("CROSS-CANCER PREDICTION TESTS")
    log("=" * 65)

    if len(escc) >= 5 and len(eac) >= 5:
        zeb2_aurka_test(escc, eac)

    if len(eac) >= 5 and len(normal) >= 3:
        cdx2_circuit_test(eac, normal)

    if (
        len(escc) >= 5
        and len(eac) >= 5
        and len(normal) >= 3
    ):
        sox2_comparison(escc, eac, normal)

    # Barrett's progression
    barretts_progression(
        normal, barretts, eac,
        depth_dict.get("Normal"),
        depth_dict.get("Barrett"),
        depth_dict.get("EAC"),
    )

    # Drug targets
    drug_targets(
        corrs_dict.get("ESCC", []),
        corrs_dict.get("EAC",  []),
    )

    # Figure
    generate_figure(
        groups, depth_dict,
        corrs_dict, group_order,
    )

    write_log()
    log(f"\n  Log    : {LOG_FILE}")
    log(f"  Output : {RESULTS_DIR}")
    log("\n=== SCRIPT 1 COMPLETE ===")
    log("\nPaste full output for Document 90a.")


if __name__ == "__main__":
    main()
