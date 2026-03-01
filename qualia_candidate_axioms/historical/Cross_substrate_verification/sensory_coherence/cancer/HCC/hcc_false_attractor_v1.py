"""
HEPATOCELLULAR CARCINOMA — FALSE ATTRACTOR ANALYSIS
SCRIPT 1
Dataset: GSE14520
  Platform: GPL3921 Affymetrix HG-U133A
  445 samples (225 HCC + 220 Normal)
  Survival: GSE14520_Extra_Supplement.txt.gz

Doc: 92a | Date: 2026-03-01

PREDICTIONS LOCKED 2026-03-01:
  HCC-P1: HNF4A r<-0.50 (switch)
  HCC-P2: AFP r>+0.50 (FA gene)
  HCC-P3: MYC r>+0.40 (FA gene)
  HCC-P4: CTNNB1 defines subtype
  HCC-P5: CTNNB1-hi = better prognosis
  HCC-P6: Depth encodes sorafenib resistance
  CC-1:   EZH2 r>+0.40 (like EAC)
  CC-2:   FGFR4 falls with depth
  CC-3:   ZEB2-AURKA r>+0.30
  CC-4:   FOXA1/2 r<-0.40
  CC-5:   S100A8 r>+0.30

KEY FIXES vs PREVIOUS VERSION:
  1. norm01() now returns numpy array
     not pd.Series — eliminates index
     mismatch NaN in build_depth
  2. Survival loaded from supplementary
     file GSE14520_Extra_Supplement.txt.gz
  3. Group assignment from !Sample_title
     directly at parse time

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

BASE_DIR    = "./hcc_false_attractor/"
RESULTS_DIR = os.path.join(BASE_DIR, "results_s1")
LOG_FILE    = os.path.join(RESULTS_DIR,
                           "analysis_log_s1.txt")
os.makedirs(RESULTS_DIR, exist_ok=True)

SERIES_URL = (
    "https://ftp.ncbi.nlm.nih.gov/geo/series/"
    "GSE14nnn/GSE14520/matrix/"
    "GSE14520-GPL3921_series_matrix.txt.gz"
)
SERIES_FILE = os.path.join(
    BASE_DIR, "GSE14520_series_matrix.txt.gz"
)
GPL_URL = (
    "https://ftp.ncbi.nlm.nih.gov/geo/platforms/"
    "GPL3nnn/GPL3921/annot/"
    "GPL3921.annot.gz"
)
GPL_FILE = os.path.join(BASE_DIR, "GPL3921.annot.gz")

SUPPL_URL = (
    "https://ftp.ncbi.nlm.nih.gov/geo/series/"
    "GSE14nnn/GSE14520/suppl/"
    "GSE14520_Extra_Supplement.txt.gz"
)
SUPPL_FILE = os.path.join(
    BASE_DIR, "GSE14520_Extra_Supplement.txt.gz"
)

# ============================================================
# TARGET GENES
# ============================================================

TARGET_GENES = [
    "HNF4A","HNF1A","HNF1B","HNF6",
    "FOXA1","FOXA2","FOXA3",
    "ALB","AFP","APOB","APOE",
    "TTR","TF","GPC3",
    "FABP1","CYP3A4","CYP2C9",
    "G6PC","PCK1","ALDOB",
    "EPCAM","KRT19","KRT7",
    "SOX9","SOX4","SOX2",
    "CD44","CD90","PROM1",
    "CTNNB1","APC","AXIN1","AXIN2",
    "LGR5","GLUL","TBX3","TCF7L2",
    "WNT3A","WNT5A","DKK1","DKK4",
    "FZD3","RNF43",
    "MYC","MYCN","CCND1","CCND2",
    "CDK4","CDK6","CCNE1","CCNB1",
    "E2F1","E2F3","RB1",
    "MKI67","TOP2A","AURKA","CDC20",
    "BIRC5","PLK1","MCM2","PCNA",
    "BCL2","MCL1","BAX","BCL2L1",
    "TP53","MDM2","CDKN1A","CDKN2A",
    "FGFR1","FGFR2","FGFR3","FGFR4",
    "FGF19","FGF21","FGFRL1","KLB",
    "EGFR","ERBB2","MET","KDR",
    "VEGFA","VEGFC","IGF1R","IGF2",
    "IGF1","IGF2R","INSR",
    "TERT",
    "EZH2","EED","SUZ12",
    "HDAC1","HDAC2","HDAC3",
    "KDM6A","KDM5C","KDM4A",
    "DNMT3A","DNMT3B","TET2",
    "ARID1A","ARID2","SMARCA4",
    "KMT2A","KMT2D",
    "TGFB1","TGFBR2","SMAD2","SMAD3",
    "SMAD4","SNAI1","SNAI2","TWIST1",
    "ZEB1","ZEB2","CDH1","CDH2",
    "VIM","FN1",
    "CD274","PDCD1","CD8A","FOXP3",
    "CD4","CD68","ARG1",
    "TSC1","TSC2","MTOR","PIK3CA",
    "PTEN","NFE2L2","KEAP1","ACVR2A",
    "FASN","SCD","ACLY","ACACA",
    "HMGCR","SQLE","LDLR",
    "PPARA","PPARG","RXRA",
    "STAT3","JAK1","JAK2","IL6",
    "IL6R","TNF","NFKB1",
    "S100A8","S100A9","S100A4",
    "KRT5","KRT14","TP63","GATA3",
    "MLH1","MSH2","MSH6",
    "ZEB2","AURKA",
]
TARGET_GENES = sorted(set(TARGET_GENES))

SWITCH_GENES = [
    "HNF4A","FOXA1","FOXA2",
    "ALB","APOB","TTR",
    "CYP3A4","G6PC","PCK1",
]
FA_GENES = [
    "AFP","MYC","BIRC5",
    "TOP2A","MKI67","AURKA",
    "CCND1","EPCAM",
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

# KEY FIX: norm01 returns numpy array
# not pd.Series to prevent index
# alignment NaN in build_depth
def norm01(arr):
    arr = np.asarray(arr, dtype=float)
    mn  = np.nanmin(arr)
    mx  = np.nanmax(arr)
    if mx > mn:
        return (arr - mn) / (mx - mn)
    return np.full_like(arr, 0.5)

# ============================================================
# DOWNLOAD
# ============================================================

def download(url, dest, label=""):
    if os.path.exists(dest):
        sz = os.path.getsize(dest)
        log(f"  Already present: {dest} "
            f"({sz:,} bytes)")
        return True
    log(f"  Downloading {label}...")
    log(f"  URL: {url}")
    try:
        r = requests.get(
            url, timeout=600, stream=True
        )
        if r.status_code == 200:
            with open(dest, "wb") as f:
                for chunk in r.iter_content(
                    chunk_size=1024*1024
                ):
                    f.write(chunk)
            sz = os.path.getsize(dest)
            log(f"  Saved: {dest} ({sz:,} bytes)")
            return True
        log(f"  HTTP {r.status_code}")
        return False
    except Exception as e:
        log(f"  Error: {e}")
        return False

# ============================================================
# PARSE GPL ANNOTATION
# ============================================================

def parse_gpl(gpl_file):
    log("")
    log("=" * 65)
    log("PARSE GPL ANNOTATION")
    log("=" * 65)

    probe_to_gene = {}
    target_set    = set(TARGET_GENES)
    opener = (
        gzip.open(gpl_file, "rt",
                  encoding="utf-8",
                  errors="ignore")
        if gpl_file.endswith(".gz")
        else open(gpl_file, "r",
                  encoding="utf-8",
                  errors="ignore")
    )

    in_table   = False
    headers    = None
    id_col     = 0
    symbol_col = None

    with opener as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith(
                "!platform_table_begin"
            ):
                in_table = True
                continue
            if line.startswith(
                "!platform_table_end"
            ):
                break
            if not in_table:
                continue
            if line.startswith("#"):
                continue
            parts = line.split("\t")
            if headers is None:
                headers = [
                    p.strip().upper()
                    for p in parts
                ]
                for i, h in enumerate(headers):
                    if h == "GENE SYMBOL":
                        symbol_col = i
                        break
                log(f"  Symbol col: {symbol_col} "
                    f"= {headers[symbol_col]}")
                continue
            if symbol_col is None:
                continue
            if len(parts) <= symbol_col:
                continue
            probe = parts[id_col].strip().strip('"')
            raw   = parts[symbol_col].strip().strip('"')
            if not raw or raw in ["---","N/A",""]:
                continue
            for g in re.split(r"[,;/ ]+", raw):
                g = g.strip()
                if g in target_set:
                    if probe not in probe_to_gene:
                        probe_to_gene[probe] = g
                    break

    log(f"  Probes mapped : {len(probe_to_gene)}")
    log(f"  Unique genes  : "
        f"{len(set(probe_to_gene.values()))}")
    return probe_to_gene

# ============================================================
# PARSE SERIES MATRIX
# ============================================================

def parse_series_matrix(series_file,
                        probe_to_gene):
    log("")
    log("=" * 65)
    log("PARSE SERIES MATRIX")
    log("=" * 65)

    opener = (
        gzip.open(series_file, "rt",
                  encoding="utf-8",
                  errors="ignore")
        if series_file.endswith(".gz")
        else open(series_file, "r",
                  encoding="utf-8",
                  errors="ignore")
    )

    sample_ids  = []
    titles      = []
    meta_lines  = {}
    probe_rows  = {}
    header_done = False

    with opener as f:
        for raw_line in f:
            line = raw_line.rstrip("\n")

            if line.startswith("!"):
                key  = line.split("\t")[0]
                vals = line.split("\t")[1:]
                if key not in meta_lines:
                    meta_lines[key] = []
                meta_lines[key].extend(vals)
                # Capture titles immediately
                if key == "!Sample_title":
                    titles = [
                        v.strip().strip('"')
                        for v in vals
                    ]
                continue

            if not line.strip():
                continue

            parts = line.split("\t")
            first = parts[0].strip().strip('"')

            if not header_done and first == "ID_REF":
                sample_ids = [
                    p.strip().strip('"')
                    for p in parts[1:]
                ]
                header_done = True
                log(f"  Samples: {len(sample_ids)}")
                log(f"  IDs[0:3]: {sample_ids[:3]}")
                continue

            if not header_done:
                continue

            if first not in probe_to_gene:
                continue

            try:
                vals_f = []
                for p in parts[1:]:
                    v = p.strip().strip('"')
                    if v in [
                        "","NA","null","nan",
                        "NULL","NaN",
                    ]:
                        vals_f.append(np.nan)
                    else:
                        vals_f.append(float(v))
            except ValueError:
                continue

            gene = probe_to_gene[first]
            if gene not in probe_rows:
                probe_rows[gene] = []
            probe_rows[gene].append(vals_f)

    log(f"  Probe rows matched: {len(probe_rows)}")

    # Collapse probes: highest variance
    gene_matrix = {}
    for gene, rows in probe_rows.items():
        if len(rows) == 1:
            gene_matrix[gene] = rows[0]
        else:
            arr   = np.array(rows, dtype=float)
            vars_ = np.nanvar(arr, axis=1)
            best  = int(np.argmax(vars_))
            gene_matrix[gene] = rows[best]

    n_s = len(sample_ids)
    # Use integer RangeIndex — avoids alignment
    # issues downstream
    df  = pd.DataFrame(
        {g: v[:n_s]
         for g, v in gene_matrix.items()},
        dtype=float,
    )
    # Store sample IDs as a column, not index
    df.insert(0, "_sample_id",
              sample_ids[:len(df)])

    log(f"  Matrix shape: {df.shape}")

    # Assign group from titles
    group = np.array(["Unknown"] * n_s)
    for i, t in enumerate(titles):
        if i >= n_s:
            break
        tl = t.lower()
        if "non-tumor" in tl or "non tumor" in tl:
            group[i] = "Normal"
        elif "tumor" in tl or "tumour" in tl:
            group[i] = "HCC"
        elif "normal" in tl or "adjacent" in tl:
            group[i] = "Normal"

    groups, counts = np.unique(
        group, return_counts=True
    )
    log(f"  Group from titles:")
    for g, c in zip(groups, counts):
        log(f"    {g}: {c}")

    return df, meta_lines, sample_ids, group, titles

# ============================================================
# PARSE SUPPLEMENTARY FILE FOR SURVIVAL
# GSE14520_Extra_Supplement.txt.gz
# Contains: SampleID, OS time, OS event,
#           RFS time, RFS event, AFP, stage
# ============================================================

def parse_supplement(suppl_file, sample_ids):
    log("")
    log("=" * 65)
    log("PARSE SUPPLEMENTARY — SURVIVAL")
    log(f"  File: {suppl_file}")
    log("=" * 65)

    n         = len(sample_ids)
    os_time   = np.full(n, np.nan)
    os_event  = np.full(n, np.nan)
    rfs_time  = np.full(n, np.nan)
    rfs_event = np.full(n, np.nan)
    afp_level = np.full(n, np.nan)
    stage     = np.array([""] * n)

    if not os.path.exists(suppl_file):
        log("  File not found — skipping survival")
        return (os_time, os_event,
                rfs_time, rfs_event,
                afp_level, stage)

    # Build GSM → matrix index map
    gsm_to_idx = {
        sid: i
        for i, sid in enumerate(sample_ids)
    }

    # HARDCODED column indices
    # Confirmed from header inspection
    COL_GSM      = 2   # AFFY_GSM
    COL_OS_E     = 18  # SURVIVAL STATUS (0/1)
    COL_OS_T     = 19  # SURVIVAL MONTHS
    COL_RFS_E    = 20  # RECURR STATUS   (0/1)
    COL_RFS_T    = 21  # RECURR MONTHS
    COL_AFP      = 17  # AFP (>/<=300NG/ML)
    COL_STAGE    = 14  # TNM STAGING

    opener = (
        gzip.open(suppl_file, "rt",
                  encoding="utf-8",
                  errors="ignore")
        if suppl_file.endswith(".gz")
        else open(suppl_file, "r",
                  encoding="utf-8",
                  errors="ignore")
    )

    header_done = False
    n_parsed    = 0
    n_matched   = 0

    with opener as f:
        for line in f:
            line = line.rstrip("\n")
            if not line.strip():
                continue

            parts = [
                p.strip().strip('"')
                for p in line.split("\t")
            ]

            # Skip header
            if not header_done:
                log(f"  Header confirmed: "
                    f"{parts[:5]}...")
                log(f"  Using cols: "
                    f"GSM={COL_GSM} "
                    f"OS_E={COL_OS_E} "
                    f"OS_T={COL_OS_T} "
                    f"RFS_E={COL_RFS_E} "
                    f"RFS_T={COL_RFS_T}")
                header_done = True
                continue

            if len(parts) <= COL_RFS_T:
                continue

            # Match on AFFY_GSM column
            gsm = parts[COL_GSM].strip()
            idx = gsm_to_idx.get(gsm)
            if idx is None:
                continue

            n_matched += 1

            # OS time (months)
            v = parts[COL_OS_T]
            try:
                t = float(
                    re.sub(r"[^\d.]", "", v)
                )
                if t >= 0:
                    os_time[idx] = t
            except (ValueError, TypeError):
                pass

            # OS event (0/1)
            v  = parts[COL_OS_E].strip()
            vl = v.lower()
            if vl in ["1","dead","yes","died"]:
                os_event[idx] = 1
            elif vl in ["0","alive","no","censored"]:
                os_event[idx] = 0
            else:
                try:
                    os_event[idx] = float(v)
                except (ValueError, TypeError):
                    pass

            # RFS time (months)
            v = parts[COL_RFS_T]
            try:
                t = float(
                    re.sub(r"[^\d.]", "", v)
                )
                if t >= 0:
                    rfs_time[idx] = t
            except (ValueError, TypeError):
                pass

            # RFS event (0/1)
            v  = parts[COL_RFS_E].strip()
            vl = v.lower()
            if vl in ["1","yes","recur","recurred"]:
                rfs_event[idx] = 1
            elif vl in ["0","no","free","censored"]:
                rfs_event[idx] = 0
            else:
                try:
                    rfs_event[idx] = float(v)
                except (ValueError, TypeError):
                    pass

            # AFP
            v = parts[COL_AFP].strip()
            vl = v.lower()
            if "high" in vl:
                afp_level[idx] = 1
            elif "low" in vl:
                afp_level[idx] = 0
            else:
                try:
                    afp_level[idx] = float(v)
                except (ValueError, TypeError):
                    pass

            # Stage
            v = parts[COL_STAGE].strip()
            if v and not stage[idx]:
                stage[idx] = v

            n_parsed += 1

    log(f"\n  Rows processed : {n_matched}")
    log(f"  Rows with data : {n_parsed}")

    # Summaries
    for label, t, e in [
        ("OS",  os_time,  os_event),
        ("RFS", rfs_time, rfs_event),
    ]:
        valid = (
            ~np.isnan(t) & ~np.isnan(e)
            & (t >= 0)
        )
        log(f"  {label}: n_valid={valid.sum()}")
        if valid.sum() > 0:
            log(f"    events={int(e[valid].sum())} "
                f"censored="
                f"{int((e[valid]==0).sum())} "
                f"range={t[valid].min():.1f}–"
                f"{t[valid].max():.1f} mo")

    afp_v = afp_level[~np.isnan(afp_level)]
    if len(afp_v) > 0:
        from collections import Counter
        ac = Counter(afp_level[
            ~np.isnan(afp_level)
        ].astype(int).tolist())
        log(f"  AFP: n={len(afp_v)} "
            f"high={ac.get(1,0)} "
            f"low={ac.get(0,0)}")

    stage_vals = [s for s in stage if s]
    if stage_vals:
        from collections import Counter
        sc = Counter(stage_vals)
        log(f"  Stage: "
            f"{dict(sc.most_common(6))}")

    return (os_time, os_event,
            rfs_time, rfs_event,
            afp_level, stage)

# ============================================================
# DEPTH SCORING
# KEY FIX: use .values everywhere,
# reset_index on df subsets,
# norm01 returns numpy array
# ============================================================

def build_depth(df_vals, switch, fa, label):
    """
    df_vals: DataFrame with integer RangeIndex
             (already reset)
    """
    gc  = list(df_vals.columns)
    sw  = [g for g in switch if g in gc]
    fa_ = [g for g in fa    if g in gc]
    log(f"  {label} depth:")
    log(f"    Switch used: {sw}")
    log(f"    FA used:     {fa_}")

    n     = len(df_vals)
    depth = np.zeros(n, dtype=float)
    nd    = 0

    if sw:
        sw_mean = df_vals[sw].mean(axis=1).values
        depth  += (1 - norm01(sw_mean))
        nd     += 1
    if fa_:
        fa_mean = df_vals[fa_].mean(axis=1).values
        depth  += norm01(fa_mean)
        nd     += 1
    if nd > 0:
        depth /= nd

    finite = depth[np.isfinite(depth)]
    log(f"    n={n} "
        f"finite={len(finite)} "
        f"mean={np.nanmean(depth):.4f} "
        f"std={np.nanstd(depth):.4f} "
        f"min={np.nanmin(depth):.4f} "
        f"max={np.nanmax(depth):.4f}")
    return depth

# ============================================================
# NORMAL vs HCC
# ============================================================

def normal_vs_hcc(df_vals, group,
                  switch, fa):
    log("")
    log("=" * 65)
    log("NORMAL vs HCC")
    log("=" * 65)

    hcc_mask = group == "HCC"
    nor_mask = group == "Normal"
    hcc_df   = df_vals[hcc_mask]
    nor_df   = df_vals[nor_mask]

    log(f"  HCC n={hcc_mask.sum()} "
        f"Normal n={nor_mask.sum()}")

    if hcc_mask.sum() == 0 or nor_mask.sum() == 0:
        log("  Cannot compare")
        return {}

    gc       = list(df_vals.columns)
    priority = sorted(set(
        switch + fa + [
            "AFP","HNF4A","FOXA1","FOXA2",
            "ALB","MYC","CTNNB1",
            "AURKA","ZEB2","EZH2","HDAC1",
            "FGFR1","FGFR2","FGFR3","FGFR4",
            "TERT","S100A8","GPC3","GLUL",
            "KRT19","EPCAM","CD44",
            "BIRC5","TOP2A","MKI67",
            "CCND1","CDK6","CDK4",
            "BCL2","MCL1","TP53",
            "SMAD3","TGFB1","VIM",
            "STAT3","IL6","VEGFA",
            "MET","EGFR","LGR5",
            "AXIN2","DKK1","TBX3","GPC3",
        ]
    ))

    log(f"\n  {'Gene':<12} {'Normal':>10} "
        f"{'HCC':>10} {'FC%':>8}  p-value")
    log(f"  {'-'*58}")

    results = {}
    for gene in priority:
        if gene not in gc:
            continue
        n_v = nor_df[gene].dropna().values
        h_v = hcc_df[gene].dropna().values
        if len(n_v) < 3 or len(h_v) < 3:
            continue
        n_m = n_v.mean()
        h_m = h_v.mean()
        fc  = (
            100*(h_m - n_m)/abs(n_m)
            if n_m != 0 else np.nan
        )
        _, p = safe_mwu(h_v, n_v)
        results[gene] = {
            "normal": n_m, "hcc": h_m,
            "fc_pct": fc, "p": p,
        }
        log(f"  {gene:<12} {n_m:>10.4f} "
            f"{h_m:>10.4f} {fc:>+8.1f}%  "
            f"{fmt_p(p)}")

    return results

# ============================================================
# DEPTH CORRELATIONS
# ============================================================

def depth_correlations(df_hcc, depth, label):
    log("")
    log("=" * 65)
    log(f"DEPTH CORRELATIONS — {label}")
    log("=" * 65)

    gc    = list(df_hcc.columns)
    corrs = []
    for gene in sorted(gc):
        if gene == "_sample_id":
            continue
        rv, pv = safe_pearsonr(
            depth, df_hcc[gene].values
        )
        if not np.isnan(rv):
            corrs.append((gene, rv, pv))

    corrs.sort(key=lambda x: x[1], reverse=True)

    log(f"\n  TOP 20 POSITIVE (FA candidates):")
    log(f"  {'Gene':<12} {'r':>8}  p-value")
    for g, r, p in corrs[:20]:
        log(f"  {g:<12} {r:>+8.4f}  {fmt_p(p)}")

    log(f"\n  TOP 20 NEGATIVE (switch candidates):")
    for g, r, p in corrs[-20:][::-1]:
        log(f"  {g:<12} {r:>+8.4f}  {fmt_p(p)}")

    log(f"\n  PREDICTION TESTS:")
    log(f"  {'Gene':<12} {'Role':<8} {'r':>8}  "
        f"p-value         Pred    Result")
    log(f"  {'-'*70}")

    preds = {
        "HNF4A":  ("switch", "<", -0.50),
        "FOXA1":  ("switch", "<", -0.40),
        "FOXA2":  ("switch", "<", -0.40),
        "ALB":    ("switch", "<", -0.50),
        "APOB":   ("switch", "<", -0.30),
        "TTR":    ("switch", "<", -0.30),
        "AFP":    ("FA",     ">", +0.50),
        "MYC":    ("FA",     ">", +0.40),
        "CTNNB1": ("FA",     ">", +0.20),
        "BIRC5":  ("FA",     ">", +0.40),
        "TOP2A":  ("FA",     ">", +0.40),
        "MKI67":  ("FA",     ">", +0.40),
        "EZH2":   ("FA",     ">", +0.40),
        "HDAC1":  ("FA",     ">", +0.30),
        "AURKA":  ("FA",     ">", +0.30),
        "ZEB2":   ("FA",     ">", +0.20),
        "FGFR4":  ("switch", "<", -0.30),
        "FGFR1":  ("FA",     ">", +0.20),
        "S100A8": ("FA",     ">", +0.20),
        "TERT":   ("FA",     ">", +0.20),
        "KRT19":  ("FA",     ">", +0.20),
        "EPCAM":  ("FA",     ">", +0.20),
        "GPC3":   ("FA",     ">", +0.20),
        "STAT3":  ("FA",     ">", +0.20),
    }

    for gene, (role, direction, thr) in (
        preds.items()
    ):
        if gene not in gc:
            log(f"  {gene:<12} NOT IN MATRIX")
            continue
        rv, pv = safe_pearsonr(
            depth, df_hcc[gene].values
        )
        if np.isnan(rv):
            continue
        ok  = (
            rv > thr if direction == ">"
            else rv < thr
        )
        sym     = "✓" if ok else "✗"
        thr_str = (
            f"{'>' if direction=='>' else '<'}"
            f"{thr:+.2f}"
        )
        log(f"  {gene:<12} {role:<8} {rv:>+8.4f}  "
            f"{fmt_p(pv)}  {thr_str:>8}  {sym}")

    return corrs

# ============================================================
# CROSS-CANCER TESTS
# ============================================================

def cross_cancer_tests(df_hcc, depth,
                       hcc_mask, df_vals):
    log("")
    log("=" * 65)
    log("CROSS-CANCER TESTS")
    log("=" * 65)

    gc = list(df_hcc.columns)

    # CC-1
    log(f"\n  CC-1: EZH2+HDAC1 EPIGENETIC LOCK")
    log(f"  EAC r=+0.56/+0.47 | BLCA inverted")
    log(f"  HCC prediction: r>+0.40")
    for gene in ["EZH2","EED","SUZ12","HDAC1",
                 "HDAC2","HDAC3","KDM6A",
                 "ARID1A","DNMT3A"]:
        if gene not in gc:
            continue
        rv, pv = safe_pearsonr(
            depth, df_hcc[gene].values
        )
        conf = ""
        if gene in ["EZH2","HDAC1"]:
            conf = "✓" if rv > 0.40 else "✗"
        log(f"  {gene:<10} r={rv:>+.4f}  "
            f"{fmt_p(pv)}  {conf}")

    # CC-2
    log(f"\n  CC-2: FGFR ISOFORM IN LIVER")
    log(f"  FGFR4=hepatocyte | "
        f"Pred FGFR4<-0.30 FGFR1/2>+0.20")
    for gene in ["FGFR1","FGFR2","FGFR3",
                 "FGFR4","FGF21","KLB"]:
        if gene not in gc:
            continue
        rv, pv = safe_pearsonr(
            depth, df_hcc[gene].values
        )
        pred = ""
        if gene == "FGFR4":
            pred = "✓" if rv < -0.30 else "✗"
        elif gene in ["FGFR1","FGFR2"]:
            pred = "✓" if rv > 0.20 else "✗"
        log(f"  {gene:<8} r={rv:>+.4f}  "
            f"{fmt_p(pv)}  {pred}")

    # CC-3
    log(f"\n  CC-3: ZEB2-AURKA COUPLING")
    log(f"  STAD=+0.99 EAC=+0.47 BLCA≈0")
    log(f"  HCC prediction: r>+0.30")
    nor_mask = ~hcc_mask
    for label, mask in [
        ("All",    np.ones(len(df_vals),
                           dtype=bool)),
        ("HCC",    hcc_mask),
        ("Normal", nor_mask),
    ]:
        sub = df_vals[mask]
        if ("ZEB2" in sub.columns
                and "AURKA" in sub.columns):
            rv, pv = safe_pearsonr(
                sub["ZEB2"].values,
                sub["AURKA"].values,
            )
            conf = ""
            if label == "HCC":
                conf = "✓" if rv > 0.30 else "✗"
            log(f"  {label:<8} "
                f"r(ZEB2,AURKA)={rv:>+.4f}  "
                f"{fmt_p(pv)}  {conf}")

    # CC-4
    log(f"\n  CC-4: FOXA1/FOXA2 SWITCH GENES")
    log(f"  BLCA r=-0.84 BRCA confirmed")
    log(f"  HCC prediction: r<-0.40")
    for gene in ["FOXA1","FOXA2","FOXA3"]:
        if gene not in gc:
            continue
        rv, pv = safe_pearsonr(
            depth, df_hcc[gene].values
        )
        conf = "✓" if rv < -0.40 else "✗"
        log(f"  {gene:<8} r={rv:>+.4f}  "
            f"{fmt_p(pv)}  {conf}")

    # CC-5
    log(f"\n  CC-5: S100A8 POOR PROGNOSIS")
    log(f"  BLCA confirmed | pred r>+0.30")
    for gene in ["S100A8","S100A9","S100A4"]:
        if gene not in gc:
            continue
        rv, pv = safe_pearsonr(
            depth, df_hcc[gene].values
        )
        conf = (
            "✓" if (gene == "S100A8"
                    and rv > 0.30)
            else "✗" if gene == "S100A8"
            else ""
        )
        log(f"  {gene:<8} r={rv:>+.4f}  "
            f"{fmt_p(pv)}  {conf}")

# ============================================================
# CTNNB1 / MYC SUBTYPES
# ============================================================

def ctnnb1_myc_subtypes(df_hcc, depth):
    log("")
    log("=" * 65)
    log("CTNNB1 / MYC SUBTYPE ANALYSIS")
    log("HCC-P4 / HCC-P5")
    log("=" * 65)

    gc = list(df_hcc.columns)
    if "CTNNB1" not in gc or "MYC" not in gc:
        log("  CTNNB1 or MYC not in matrix")
        return

    ctnnb1_med = np.nanmedian(
        df_hcc["CTNNB1"].values
    )
    myc_med    = np.nanmedian(
        df_hcc["MYC"].values
    )
    ctnnb1_hi  = (
        df_hcc["CTNNB1"].values >= ctnnb1_med
    )
    myc_hi     = (
        df_hcc["MYC"].values >= myc_med
    )

    log(f"  CTNNB1 median: {ctnnb1_med:.4f}")
    log(f"  MYC median:    {myc_med:.4f}")
    log(f"  Groups:")
    log(f"    CTNNB1-hi/MYC-hi: "
        f"{(ctnnb1_hi & myc_hi).sum()}")
    log(f"    CTNNB1-hi/MYC-lo: "
        f"{(ctnnb1_hi & ~myc_hi).sum()}")
    log(f"    CTNNB1-lo/MYC-hi: "
        f"{(~ctnnb1_hi & myc_hi).sum()}")
    log(f"    CTNNB1-lo/MYC-lo: "
        f"{(~ctnnb1_hi & ~myc_hi).sum()}")

    log(f"\n  Depth by group:")
    for label, mask in [
        ("CTNNB1-hi",  ctnnb1_hi),
        ("CTNNB1-lo", ~ctnnb1_hi),
        ("MYC-hi",     myc_hi),
        ("MYC-lo",    ~myc_hi),
    ]:
        d = depth[mask]
        log(f"  {label:<15} "
            f"mean={np.nanmean(d):.4f} "
            f"std={np.nanstd(d):.4f}")

    rv_c, pv_c = safe_pearsonr(
        depth, df_hcc["CTNNB1"].values
    )
    rv_m, pv_m = safe_pearsonr(
        depth, df_hcc["MYC"].values
    )
    log(f"\n  r(depth, CTNNB1) = "
        f"{rv_c:>+.4f}  {fmt_p(pv_c)}")
    log(f"  r(depth, MYC)    = "
        f"{rv_m:>+.4f}  {fmt_p(pv_m)}")

    rv_cm, pv_cm = safe_pearsonr(
        df_hcc["CTNNB1"].values,
        df_hcc["MYC"].values,
    )
    log(f"\n  r(CTNNB1, MYC) = "
        f"{rv_cm:>+.4f}  {fmt_p(pv_cm)}")
    if rv_cm < 0:
        log(f"  Anti-correlated ✓ "
            f"(two tracks confirmed)")
    elif rv_cm < 0.3:
        log(f"  Weakly correlated — partial")
    else:
        log(f"  Co-active")

    log(f"\n  Wnt targets CTNNB1-hi vs lo:")
    for gene in ["AXIN2","LGR5","GLUL",
                 "DKK1","DKK4","TBX3",
                 "MYC","CCND1","GPC3"]:
        if gene not in gc:
            continue
        hi_v = df_hcc[gene].values[ctnnb1_hi]
        lo_v = df_hcc[gene].values[~ctnnb1_hi]
        _, p = safe_mwu(hi_v, lo_v)
        fc   = (
            np.nanmean(hi_v) - np.nanmean(lo_v)
        )
        log(f"  {gene:<8} FC={fc:>+.3f}  "
            f"{fmt_p(p)}")

# ============================================================
# SURVIVAL ANALYSIS
# ============================================================

def survival_analysis(df_hcc, depth_hcc,
                      os_time, os_event,
                      rfs_time, rfs_event,
                      hcc_mask):
    log("")
    log("=" * 65)
    log("SURVIVAL ANALYSIS — HCC")
    log("=" * 65)

    hcc_idx  = np.where(hcc_mask)[0]
    gc_hcc   = [
        c for c in df_hcc.columns
        if c != "_sample_id"
    ]

    t_os  = os_time[hcc_idx]
    e_os  = os_event[hcc_idx]
    t_rfs = rfs_time[hcc_idx]
    e_rfs = rfs_event[hcc_idx]
    d_v   = depth_hcc

    results = {}

    for label, t, e in [
        ("OS",  t_os, e_os),
        ("RFS", t_rfs, e_rfs),
    ]:
        valid = (
            ~np.isnan(t) & ~np.isnan(e)
            & ~np.isnan(d_v) & (t > 0)
        )
        log(f"\n  {label}: n_valid={valid.sum()}")
        if valid.sum() < 10:
            log(f"  Insufficient data for {label}")
            continue

        t_v = t[valid]
        e_v = e[valid]
        dv  = d_v[valid]
        log(f"  Events={int(e_v.sum())}/{len(t_v)} "
            f"range={t_v.min():.1f}–"
            f"{t_v.max():.1f} mo")

        med = np.median(dv)
        hi  = dv >= med
        lo  = ~hi

        try:
            res     = logrank_test(
                t_v[hi], t_v[lo],
                e_v[hi], e_v[lo],
            )
            p_depth = res.p_value
        except Exception:
            p_depth = np.nan

        log(f"  Deep    (n={hi.sum()}): "
            f"mean={t_v[hi].mean():.1f} mo")
        log(f"  Shallow (n={lo.sum()}): "
            f"mean={t_v[lo].mean():.1f} mo")
        log(f"  Log-rank: {fmt_p(p_depth)}")
        log(
            f"  "
            f"{'CONFIRMED ✓' if not np.isnan(p_depth) and p_depth < 0.05 else 'NOT CONFIRMED ✗'}"
        )

        log(f"\n  Individual genes {label} p<0.05:")
        for gene in sorted(gc_hcc):
            gv   = df_hcc[gene].values[valid]
            gmed = np.nanmedian(gv)
            ghi  = gv >= gmed
            glo  = ~ghi
            if ghi.sum() < 5 or glo.sum() < 5:
                continue
            try:
                r = logrank_test(
                    t_v[ghi], t_v[glo],
                    e_v[ghi], e_v[glo],
                )
                p = r.p_value
            except Exception:
                p = np.nan
            if not np.isnan(p) and p < 0.05:
                direction = (
                    "↑=worse"
                    if t_v[ghi].mean()
                    < t_v[glo].mean()
                    else "↑=better"
                )
                log(f"  {gene:<12} "
                    f"{fmt_p(p)}  {direction}")

        results[label] = {
            "t": t_v, "e": e_v,
            "hi": hi, "lo": lo,
            "p_depth": p_depth,
        }

    return results

# ============================================================
# GENERATE FIGURE
# ============================================================

def generate_figure(
    df_vals, df_hcc, df_nor,
    depth_hcc, surv_results,
    hcc_mask,
):
    log("")
    log("--- Generating figure ---")

    fig = plt.figure(figsize=(28, 22))
    fig.suptitle(
        "Hepatocellular Carcinoma — "
        "False Attractor Analysis\n"
        "Script 1 | GSE14520 | "
        "OrganismCore | Doc 92a | 2026-03-01",
        fontsize=10, fontweight="bold",
        y=0.99,
    )
    gs_f = gridspec.GridSpec(
        3, 3, figure=fig,
        hspace=0.55, wspace=0.45,
    )

    nor_mask = ~hcc_mask

    # A — HNF4A
    ax_a = fig.add_subplot(gs_f[0, 0])
    for label, mask, color in [
        ("Normal", nor_mask, "#27ae60"),
        ("HCC",    hcc_mask, "#e74c3c"),
    ]:
        if "HNF4A" in df_vals.columns:
            vals = df_vals[mask]["HNF4A"].dropna()
            if len(vals) > 0:
                ax_a.hist(
                    vals, bins=20, alpha=0.6,
                    label=f"{label} n={len(vals)}",
                    color=color,
                )
    ax_a.set_title(
        "A — HNF4A Normal vs HCC\n"
        "(HCC-P1: primary switch gene)",
        fontsize=9,
    )
    ax_a.set_xlabel("HNF4A", fontsize=8)
    ax_a.legend(fontsize=7)

    # B — AFP
    ax_b = fig.add_subplot(gs_f[0, 1])
    for label, mask, color in [
        ("Normal", nor_mask, "#27ae60"),
        ("HCC",    hcc_mask, "#e74c3c"),
    ]:
        if "AFP" in df_vals.columns:
            vals = df_vals[mask]["AFP"].dropna()
            if len(vals) > 0:
                ax_b.hist(
                    vals, bins=20, alpha=0.6,
                    label=f"{label} n={len(vals)}",
                    color=color,
                )
    ax_b.set_title(
        "B — AFP Normal vs HCC\n"
        "(HCC-P2: primary FA gene)",
        fontsize=9,
    )
    ax_b.set_xlabel("AFP", fontsize=8)
    ax_b.legend(fontsize=7)

    # C — Depth vs AFP
    ax_c = fig.add_subplot(gs_f[0, 2])
    if "AFP" in df_hcc.columns:
        rv, _ = safe_pearsonr(
            depth_hcc, df_hcc["AFP"].values
        )
        ax_c.scatter(
            depth_hcc,
            df_hcc["AFP"].values,
            alpha=0.4, s=20, color="#e74c3c",
        )
        ax_c.set_title(
            f"C — Depth vs AFP\nr={rv:+.3f}",
            fontsize=9,
        )
        ax_c.set_xlabel("HCC depth", fontsize=8)
        ax_c.set_ylabel("AFP", fontsize=8)

    # D — Depth vs HNF4A
    ax_d = fig.add_subplot(gs_f[1, 0])
    if "HNF4A" in df_hcc.columns:
        rv, _ = safe_pearsonr(
            depth_hcc, df_hcc["HNF4A"].values
        )
        ax_d.scatter(
            depth_hcc,
            df_hcc["HNF4A"].values,
            alpha=0.4, s=20, color="#2980b9",
        )
        ax_d.set_title(
            f"D — Depth vs HNF4A\nr={rv:+.3f}",
            fontsize=9,
        )
        ax_d.set_xlabel("HCC depth", fontsize=8)
        ax_d.set_ylabel("HNF4A", fontsize=8)

    # E — FGFR isoforms
    ax_e = fig.add_subplot(gs_f[1, 1])
    fgfr_genes = [
        g for g in [
            "FGFR1","FGFR2",
            "FGFR3","FGFR4",
        ]
        if g in df_hcc.columns
    ]
    colors_f = [
        "#e74c3c","#e67e22",
        "#27ae60","#2980b9",
    ]
    for gene, color in zip(fgfr_genes, colors_f):
        rv, _ = safe_pearsonr(
            depth_hcc, df_hcc[gene].values
        )
        ax_e.scatter(
            depth_hcc, df_hcc[gene].values,
            alpha=0.3, s=10,
            label=f"{gene} r={rv:+.2f}",
            color=color,
        )
    ax_e.set_title(
        "E — FGFR Isoforms vs Depth\n"
        "(CC-2)",
        fontsize=9,
    )
    ax_e.set_xlabel("HCC depth", fontsize=8)
    ax_e.legend(fontsize=7)

    # F — ZEB2 vs AURKA
    ax_f = fig.add_subplot(gs_f[1, 2])
    if ("ZEB2" in df_hcc.columns
            and "AURKA" in df_hcc.columns):
        rv, _ = safe_pearsonr(
            df_hcc["ZEB2"].values,
            df_hcc["AURKA"].values,
        )
        ax_f.scatter(
            df_hcc["ZEB2"].values,
            df_hcc["AURKA"].values,
            alpha=0.4, s=20, color="#8e44ad",
        )
        ax_f.set_title(
            f"F — ZEB2 vs AURKA\n"
            f"r={rv:+.3f} "
            f"(CC-3: STAD=+0.99 BLCA≈0)",
            fontsize=9,
        )
        ax_f.set_xlabel("ZEB2", fontsize=8)
        ax_f.set_ylabel("AURKA", fontsize=8)

    # G — EZH2/HDAC1
    ax_g = fig.add_subplot(gs_f[2, 0])
    for gene, color in [
        ("EZH2",  "#e74c3c"),
        ("HDAC1", "#2980b9"),
    ]:
        if gene not in df_hcc.columns:
            continue
        rv, _ = safe_pearsonr(
            depth_hcc, df_hcc[gene].values
        )
        ax_g.scatter(
            depth_hcc, df_hcc[gene].values,
            alpha=0.3, s=10,
            label=f"{gene} r={rv:+.2f}",
            color=color,
        )
    ax_g.set_title(
        "G — EZH2/HDAC1 vs Depth\n"
        "(CC-1: EAC=✓ BLCA=✗ HCC=?)",
        fontsize=9,
    )
    ax_g.set_xlabel("HCC depth", fontsize=8)
    ax_g.legend(fontsize=7)

    # H — KM OS
    ax_h = fig.add_subplot(gs_f[2, 1])
    res_os = surv_results.get("OS")
    if res_os is not None:
        t   = res_os["t"]
        e   = res_os["e"]
        hi  = res_os["hi"]
        lo  = res_os["lo"]
        p   = res_os["p_depth"]
        kmf = KaplanMeierFitter()
        kmf.fit(t[hi], e[hi],
                label=f"Deep n={hi.sum()}")
        kmf.plot_survival_function(
            ax=ax_h, color="#e74c3c",
            ci_show=True, ci_alpha=0.1,
        )
        kmf.fit(t[lo], e[lo],
                label=f"Shallow n={lo.sum()}")
        kmf.plot_survival_function(
            ax=ax_h, color="#27ae60",
            ci_show=True, ci_alpha=0.1,
        )
        p_str = (
            f"p={p:.4f}"
            if not np.isnan(p) else "N/A"
        )
        ax_h.set_title(
            f"H — KM OS\n{p_str}", fontsize=9
        )
        ax_h.legend(fontsize=7)
        ax_h.set_xlabel("Months", fontsize=8)
    else:
        ax_h.set_title(
            "H — KM OS (no survival data)",
            fontsize=9,
        )
        ax_h.text(
            0.5, 0.5,
            "Survival data\nnot available",
            ha="center", va="center",
            transform=ax_h.transAxes,
        )

    # I — Summary
    ax_i = fig.add_subplot(gs_f[2, 2])
    ax_i.axis("off")
    p_os  = "N/A"
    p_rfs = "N/A"
    if surv_results.get("OS"):
        v = surv_results["OS"]["p_depth"]
        if not np.isnan(v):
            p_os = f"{v:.4f}"
    if surv_results.get("RFS"):
        v = surv_results["RFS"]["p_depth"]
        if not np.isnan(v):
            p_rfs = f"{v:.4f}"

    summary = (
        "I — SCRIPT 1 SUMMARY\n"
        "─────────────────────────────\n"
        "Dataset: GSE14520\n"
        "Platform: GPL3921\n"
        "HCC n=225 Normal n=220\n\n"
        "SURVIVAL:\n"
        f"  OS  depth p={p_os}\n"
        f"  RFS depth p={p_rfs}\n\n"
        "PREDICTIONS LOCKED 2026-03-01:\n"
        "  HCC-P1: HNF4A r<-0.50\n"
        "  HCC-P2: AFP   r>+0.50\n"
        "  HCC-P3: MYC   r>+0.40\n"
        "  HCC-P4: CTNNB1 two-track\n"
        "  HCC-P5: CTNNB1 better prog\n"
        "  CC-1:   EZH2  r>+0.40\n"
        "  CC-2:   FGFR4 r<-0.30\n"
        "  CC-3:   ZEB2-AURKA r>+0.30\n"
        "  CC-4:   FOXA1 r<-0.40\n"
        "  CC-5:   S100A8 r>+0.30\n\n"
        "Framework: OrganismCore\n"
        "Doc 92a | 2026-03-01"
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
        RESULTS_DIR, "hcc_gse14520_s1.png"
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
    log("HEPATOCELLULAR CARCINOMA — SCRIPT 1")
    log("Dataset: GSE14520")
    log("Framework: OrganismCore")
    log("Doc: 92a | Date: 2026-03-01")
    log("=" * 65)
    log("")
    log("PREDICTIONS LOCKED 2026-03-01:")
    log("HCC-P1: HNF4A r<-0.50 (switch)")
    log("HCC-P2: AFP r>+0.50 (FA gene)")
    log("HCC-P3: MYC r>+0.40 (FA gene)")
    log("HCC-P4: CTNNB1 defines subtype")
    log("HCC-P5: CTNNB1-hi = better prog")
    log("HCC-P6: Depth → sorafenib resistance")
    log("CC-1:   EZH2 r>+0.40 (like EAC)")
    log("CC-2:   FGFR4 falls with depth")
    log("CC-3:   ZEB2-AURKA r>+0.30")
    log("CC-4:   FOXA1/2 r<-0.40")
    log("CC-5:   S100A8 r>+0.30")

    os.makedirs(BASE_DIR, exist_ok=True)

    log("")
    log("=" * 65)
    log("STEP 0: DATA ACQUISITION")
    log("=" * 65)

    ok_s = download(SERIES_URL, SERIES_FILE,
                    "GSE14520 series matrix")
    ok_g = download(GPL_URL, GPL_FILE,
                    "GPL3921 annotation")
    ok_p = download(SUPPL_URL, SUPPL_FILE,
                    "GSE14520 supplementary")

    if not ok_s or not ok_g:
        log("FATAL: Core download failed")
        write_log()
        return

    # Parse GPL
    probe_to_gene = parse_gpl(GPL_FILE)
    if len(set(probe_to_gene.values())) < 5:
        log("FATAL: GPL < 5 genes")
        write_log()
        return

    # Parse series matrix
    (df_vals, meta_lines,
     sample_ids, group, titles) = (
        parse_series_matrix(
            SERIES_FILE, probe_to_gene
        )
    )

    if df_vals is None or len(df_vals) == 0:
        log("FATAL: Empty expression matrix")
        write_log()
        return

    hcc_mask = group == "HCC"
    nor_mask = group == "Normal"

    # Drop _sample_id for numeric ops
    num_cols = [
        c for c in df_vals.columns
        if c != "_sample_id"
    ]
    df_num   = df_vals[num_cols]
    df_hcc   = df_num[hcc_mask].reset_index(
        drop=True
    )
    df_nor   = df_num[nor_mask].reset_index(
        drop=True
    )

    log("")
    log("=" * 65)
    log("GROUP SUMMARY")
    log("=" * 65)
    log(f"  HCC:     {hcc_mask.sum()}")
    log(f"  Normal:  {nor_mask.sum()}")
    log(f"  Unknown: {(group=='Unknown').sum()}")

    if hcc_mask.sum() < 5:
        log("FATAL: Too few HCC samples")
        write_log()
        return

    # Parse survival
    (os_time, os_event,
     rfs_time, rfs_event,
     afp_level, stage) = parse_supplement(
        SUPPL_FILE, sample_ids
    )

    # Normal vs HCC
    fc_results = normal_vs_hcc(
        df_num, group, SWITCH_GENES, FA_GENES
    )

    # Depth
    log("")
    log("=" * 65)
    log("DEPTH SCORES")
    log("=" * 65)
    depth_hcc = build_depth(
        df_hcc, SWITCH_GENES, FA_GENES, "HCC"
    )

    # Depth correlations
    corrs = depth_correlations(
        df_hcc, depth_hcc, "HCC"
    )

    # Cross-cancer tests
    cross_cancer_tests(
        df_hcc, depth_hcc,
        hcc_mask, df_num,
    )

    # CTNNB1/MYC subtypes
    ctnnb1_myc_subtypes(df_hcc, depth_hcc)

    # Survival
    surv_results = survival_analysis(
        df_hcc, depth_hcc,
        os_time, os_event,
        rfs_time, rfs_event,
        hcc_mask,
    )

    # Figure
    generate_figure(
        df_num, df_hcc, df_nor,
        depth_hcc, surv_results,
        hcc_mask,
    )

    # Save depth
    depth_df = pd.DataFrame({
        "sample_id": [
            s for s, g in zip(sample_ids, group)
            if g == "HCC"
        ],
        "depth_s1": depth_hcc,
    })
    depth_df.to_csv(
        os.path.join(
            RESULTS_DIR, "depth_s1_hcc.csv"
        ),
        index=False,
    )

    write_log()
    log(f"\n  Log    : {LOG_FILE}")
    log(f"  Output : {RESULTS_DIR}")
    log("\n=== SCRIPT 1 COMPLETE ===")
    log("\nPaste full output for Document 92a.")


if __name__ == "__main__":
    main()
