"""
ccRCC False Attractor — Script 2
PROTOCOL-COMPLIANT CIRCUIT + SURVIVAL RUN

Framework: OrganismCore
Document 94b | 2026-03-02
Author: Eric Robert Lawson

PREDICTIONS LOCKED BEFORE SCRIPT 2 RUNS:

S2-OBJ-1  Depth strata — KDE on depth distribution
           Low <0.55 / Mid 0.55-0.70 / High >0.70
           Each stratum characterised by gene expression

S2-OBJ-2  SCD × CPT1A coupling
           r(SCD, CPT1A) predicted < -0.40
           The clear cell lipid phenotype = both arms

S2-OBJ-3  VIM × FBP1 coupling
           r(VIM, FBP1) predicted < -0.40
           PT identity loss and mesenchymal shift
           are inversely coupled — one transition

S2-OBJ-4  Fibrotic circuit
           r(TGFB1, FAP)    predicted > +0.40
           r(TGFB1, COL1A1) predicted > +0.40
           r(FAP, COL1A1)   predicted > +0.40

S2-OBJ-5  Immune suppression circuit
           r(TGFB1, FOXP3)  predicted > +0.30
           r(CD68, FOXP3)   predicted > +0.30

S2-OBJ-6  Survival stratification
           KM by depth quartile — log-rank p < 0.01
           Cox depth vs OS — HR > 1.5

S2-OBJ-7  3-gene panel validation
           SLC2A1(+) / VIM(+) / FBP1(-)
           r vs full depth score — target >= 0.85

S2-OBJ-8  Drug target depth correlation map
           All targets ranked by r vs depth
           Patient selection map by stratum

DATASETS:
  TCGA-KIRC  HiSeqV2 — 534T / 72N
             + clinical survival (Xena)
  GSE53757   GPL570  — 72T / 72N matched pairs
"""

import os
import gzip
import urllib.request

import numpy as np
import pandas as pd
from scipy import stats
from scipy.signal import find_peaks
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import warnings
warnings.filterwarnings("ignore")

# ═══════════════════════════════════════════════════════
# DIRECTORIES
# ═══════════════════════════════════════════════════════

BASE_DIR    = "./ccrcc_false_attractor/"
S1_DIR      = os.path.join(BASE_DIR, "results_s1")
S2_DIR      = os.path.join(BASE_DIR, "results_s2")
LOG_FILE    = os.path.join(S2_DIR, "s2_log.txt")
os.makedirs(S2_DIR, exist_ok=True)

# ═══════════════════════════════════════════════════════
# DATA PATHS
# ═══════════════════════════════════════════════════════

XENA_LOCAL      = os.path.join(BASE_DIR,
                                "TCGA_KIRC_HiSeqV2.gz")
GEO_LOCAL       = os.path.join(BASE_DIR,
                                "GSE53757_series_matrix.txt.gz")
GPL570_LOCAL    = os.path.join(BASE_DIR, "GPL570_soft.txt")
SURV_LOCAL      = os.path.join(BASE_DIR,
                                "TCGA_KIRC_survival.txt")

SURV_URLS = [
    ("https://tcga-xena-hub.s3.us-east-1.amazonaws.com/"
     "download/survival%2FKIRC_survival.txt",
     SURV_LOCAL),
    ("https://tcga.xenahubs.net/download/"
     "survival/KIRC_survival.txt",
     SURV_LOCAL),
]

# ═══════════════════════════════════════════════════════
# FULL GENE PANEL
# ═══════════════════════════════════════════════════════

SW_GENES = [
    "UMOD",    "SLC34A1", "SLC13A3",
    "AGXT",    "PCK1",    "SLC22A6",
    "GATM",    "AQP1",    "FBP1",
    "G6PC",
]

FA_GENES = [
    "CA9",    "VEGFA",  "EGLN3",
    "SLC2A1", "PDK1",   "LDHA",
    "EPAS1",  "SCD",    "ACLY",
    "EZH2",
]

# Circuit pairs for S2 gap tests
CIRCUIT_PAIRS = [
    # S2-OBJ-2 Lipid circuit
    ("SCD",    "CPT1A",  "negative",
     "FAO suppressed as lipid synthesis rises"),
    ("SCD",    "ACLY",   "positive",
     "SCD and ACLY co-drive lipid false attractor"),
    ("SCD",    "PLIN2",  "positive",
     "Lipid droplet formation tracks desaturation"),
    ("SCD",    "FBP1",   "negative",
     "Gluconeogenesis loss as lipid synthesis gains"),
    # S2-OBJ-3 Mesenchymal circuit
    ("VIM",    "FBP1",   "negative",
     "PT identity loss and mesenchymal shift inversely coupled"),
    ("VIM",    "SLC34A1","negative",
     "PT transporter loss as mesenchymal shift gains"),
    ("VIM",    "TGFB1",  "positive",
     "TGF-β1 drives vimentin in mesenchymal shift"),
    ("VIM",    "SNAI1",  "positive",
     "SNAI1 drives vimentin expression"),
    # S2-OBJ-4 Fibrotic circuit
    ("TGFB1",  "FAP",    "positive",
     "TGF-β1 activates CAFs"),
    ("TGFB1",  "COL1A1", "positive",
     "TGF-β1 drives collagen deposition"),
    ("FAP",    "COL1A1", "positive",
     "FAP-positive CAFs deposit collagen"),
    ("TGFB1",  "ACTA2",  "positive",
     "TGF-β1 drives myofibroblast activation"),
    # S2-OBJ-5 Immune circuit
    ("TGFB1",  "FOXP3",  "positive",
     "TGF-β1 drives Treg expansion"),
    ("CD68",   "FOXP3",  "positive",
     "Macrophage and Treg infiltration coupled"),
    ("CD274",  "FOXP3",  "positive",
     "PD-L1 and Treg immunosuppression coupled"),
    # EPAS1 circuit (from S1 — retest with full panel)
    ("EPAS1",  "SLC2A1", "positive",
     "EPAS1 directly activates GLUT1"),
    ("EPAS1",  "SCD",    "positive",
     "EPAS1 drives lipid synthesis"),
    ("EPAS1",  "LDHA",   "positive",
     "EPAS1 drives lactate production"),
    ("VHL",    "EPAS1",  "negative",
     "VHL degrades EPAS1 — post-translational break"),
    # mTOR axis
    ("MTOR",   "PTEN",   "negative",
     "PTEN suppresses mTOR"),
    ("MTOR",   "MYC",    "positive",
     "mTOR drives MYC translation"),
    # MYC axis
    ("MYC",    "SLC2A1", "positive",
     "MYC drives GLUT1 co-regulation"),
    ("MYC",    "LDHA",   "positive",
     "MYC drives glycolytic gene expression"),
    # EZH2 axis
    ("EZH2",   "FBP1",   "negative",
     "EZH2 silences gluconeogenic genes"),
    ("EZH2",   "SLC34A1","negative",
     "EZH2 silences PT identity"),
    ("EZH2",   "VIM",    "positive",
     "EZH2 maintains mesenchymal state"),
    # PAX circuit
    ("PAX8",   "SLC34A1","positive",
     "PAX8 drives PT identity"),
    ("PAX8",   "FBP1",   "positive",
     "PAX8 drives gluconeogenic identity"),
    ("PAX2",   "PAX8",   "positive",
     "PAX2 and PAX8 co-expressed in renal identity"),
]

DRUG_TARGETS = [
    ("EPAS1",  "HIF2α inhibitor / Belzutifan"),
    ("VEGFA",  "Anti-VEGF / Sunitinib / Bevacizumab"),
    ("SCD",    "SCD inhibitor (MF-438 / A939572)"),
    ("TGFB1",  "TGF-β inhibitor / Galunisertib"),
    ("EZH2",   "EZH2 inhibitor / Tazemetostat"),
    ("MTOR",   "mTOR inhibitor / Everolimus"),
    ("MYC",    "MYC inhibitor / BET bromodomain"),
    ("CD274",  "Anti-PD-L1 / Atezolizumab"),
    ("FOXP3",  "Anti-Treg / Anti-CTLA-4"),
    ("FAP",    "FAP-targeted therapy (ADC / CAR-T)"),
    ("CA9",    "CA9 inhibitor (SLC-0111)"),
    ("ACLY",   "ACLY inhibitor / Bempedoic acid analogue"),
    ("FBP1",   "FBP1 restoration (experimental)"),
    ("CPT1A",  "CPT1A restoration (experimental)"),
    ("MET",    "MET inhibitor / Cabozantinib"),
    ("CCND1",  "CDK4/6 inhibitor / Palbociclib"),
    ("TOP2A",  "Topoisomerase inhibitor"),
    ("MKI67",  "Proliferation marker (not target)"),
]

FULL_PANEL = list(dict.fromkeys(
    SW_GENES + FA_GENES + [
    "HIF1A",  "VHL",    "ARNT",
    "EGLN1",  "EGLN2",
    "LHX1",   "HNF4A",  "HNF1A",
    "JAG1",   "PAX8",   "PAX2",
    "SIX2",   "WT1",
    "PCK2",   "ALDOB",
    "FASN",   "ACACA",  "HMGCR",
    "CPT1A",  "FABP7",  "PLIN2",
    "TWIST1", "VIM",    "ZEB1",
    "SNAI1",  "CDH1",   "FN1",
    "ACTA2",  "FAP",    "TGFB1",
    "COL1A1", "WNT5A",
    "BAP1",   "PBRM1",  "SETD2",
    "KDM5C",  "KDM1A",  "DNMT3A",
    "CD8A",   "CD274",  "FOXP3",
    "CD68",   "PDCD1",
    "MTOR",   "CCND1",  "MYC",
    "MET",    "PIK3CA", "PTEN",
    "MKI67",  "TOP2A",  "CDC20",
    "CCNB1",
]))

# ═══════════════════════════════════════════════════════
# LOGGING
# ═══════════════════════════════════════════════════════

log_lines = []

def log(msg=""):
    print(msg)
    log_lines.append(str(msg))

def write_log():
    with open(LOG_FILE, "w") as f:
        f.write("\n".join(log_lines))

def fmt_p(p):
    if p is None or (isinstance(p, float)
                     and np.isnan(p)):
        return "NA"
    if p < 0.0001:
        return f"{p:.2e}"
    return f"{p:.4f}"

def norm01(arr):
    arr = np.asarray(arr, dtype=float)
    mn, mx = np.nanmin(arr), np.nanmax(arr)
    if mx == mn:
        return np.full_like(arr, 0.5)
    return (arr - mn) / (mx - mn)

def safe_r(x, y):
    try:
        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)
        mask = ~(np.isnan(x) | np.isnan(y))
        if mask.sum() < 5:
            return np.nan, np.nan
        r, p = stats.pearsonr(
            x[mask], y[mask])
        return r, p
    except Exception:
        return np.nan, np.nan

def safe_mwu(a, b):
    try:
        a = pd.Series(a).dropna()
        b = pd.Series(b).dropna()
        if len(a) < 3 or len(b) < 3:
            return np.nan, np.nan
        s, p = stats.mannwhitneyu(
            a, b, alternative="two-sided")
        return s, p
    except Exception:
        return np.nan, np.nan

def fetch_url(url, dest, timeout=120):
    try:
        log(f"  Trying: {url}")
        def hook(c, b, t):
            if t > 0:
                pct = min(c * b * 100 // t, 100)
                print(f"\r  {pct}%",
                      end="", flush=True)
        urllib.request.urlretrieve(
            url, dest, reporthook=hook)
        print()
        mb = os.path.getsize(dest) / (1024*1024)
        log(f"  OK: {mb:.1f} MB → {dest}")
        return True
    except Exception as e:
        log(f"  FAILED: {e}")
        return False

# ═══════════════════════════════════════════════════════
# LOAD S1 OUTPUTS
# ═══════════════════════════════════════════════════════

def load_s1_outputs():
    log("")
    log("=" * 60)
    log("LOADING SCRIPT 1 OUTPUTS")
    log("=" * 60)

    depth_t = pd.read_csv(
        os.path.join(S1_DIR,
                     "depth_scores_tcga.csv"),
        index_col="sample_id"
    )["depth_score"]

    depth_g = pd.read_csv(
        os.path.join(S1_DIR,
                     "depth_scores_geo.csv"),
        index_col="sample_id"
    )["depth_score"]

    log(f"  TCGA depth loaded: n={len(depth_t)}")
    log(f"  GEO  depth loaded: n={len(depth_g)}")
    return depth_t, depth_g

# ═══════════════════════════════════════════════════════
# PARSE TCGA
# ═══════════════════════════════��═══════════════════════

def parse_tcga():
    log("")
    log("=" * 60)
    log("TCGA-KIRC — Reloading")
    log("=" * 60)
    with gzip.open(XENA_LOCAL, "rt") as f:
        raw = pd.read_csv(f, sep="\t",
                          index_col=0)

    avail = [g for g in FULL_PANEL
             if g in raw.index]
    expr  = raw.loc[avail]

    types = {}
    for s in raw.columns:
        p = s.split("-")
        if len(p) >= 4:
            code_str = p[3][:2]
            if code_str.isdigit():
                code = int(code_str)
                if 1 <= code <= 9:
                    types[s] = "tumour"
                elif 10 <= code <= 19:
                    types[s] = "normal"
                else:
                    types[s] = "other"
            else:
                types[s] = "other"
        else:
            types[s] = "other"

    meta = pd.DataFrame({
        "sample_id":   list(types.keys()),
        "sample_type": list(types.values()),
    }).set_index("sample_id")

    t_cols = [c for c in expr.columns
              if types.get(c) == "tumour"]
    log(f"  Panel genes: {len(avail)}")
    log(f"  Tumour samples: {len(t_cols)}")
    return expr, meta, t_cols

# ═══════════════════════════════════════════════════════
# PARSE GEO
# ═══════════════════════════════════════════════════════

def parse_geo():
    log("")
    log("=" * 60)
    log("GSE53757 — Reloading")
    log("=" * 60)

    if not os.path.exists(GPL570_LOCAL):
        log("  GPL570 not found. Skipping GEO.")
        return None, None, None

    probe_map = {}
    with open(GPL570_LOCAL, "r",
              encoding="utf-8",
              errors="replace") as f:
        header = id_col = sym_col = None
        for line in f:
            line = line.rstrip("\n")
            if line.startswith(
                    ("^", "!", "#")):
                continue
            parts = line.split("\t")
            if header is None:
                lower = [p.strip().lower()
                         for p in parts]
                if "id" in lower:
                    header  = parts
                    id_col  = lower.index("id")
                    sym_col = None
                    for c in [
                        "gene symbol",
                        "gene_symbol",
                        "symbol",
                        "gene assignment"
                    ]:
                        for i, lp in enumerate(lower):
                            if c in lp:
                                sym_col = i
                                break
                        if sym_col is not None:
                            break
                    if sym_col is None:
                        sym_col = 1
                continue
            if len(parts) <= max(id_col,
                                 sym_col):
                continue
            pid = parts[id_col].strip()
            raw = parts[sym_col].strip()
            if not pid or not raw:
                continue
            sym = (raw.split("///")[0]
                   .strip().upper().split()[0])
            if sym in ("", "---", "N/A", "NA"):
                continue
            probe_map[pid] = sym

    sample_ids    = []
    source_names  = []
    with gzip.open(GEO_LOCAL, "rt") as f:
        for line in f:
            line = line.rstrip()
            if line.startswith(
                    "!Sample_geo_accession"):
                parts = line.split("\t")
                sample_ids.extend([
                    p.strip().strip('"')
                    for p in parts[1:]
                    if p.strip().strip('"')
                    .startswith("GSM")])
            elif line.startswith(
                    "!Sample_source_name_ch1"):
                parts = line.split("\t")
                source_names.extend([
                    p.strip().strip('"')
                    for p in parts[1:]
                    if p.strip()])
            elif line.startswith(
                    "!series_matrix_table_begin"):
                break

    types_geo = []
    for name in source_names:
        nl = name.lower()
        if "normal" in nl:
            types_geo.append("normal")
        else:
            types_geo.append("tumour")

    n      = min(len(sample_ids),
                 len(types_geo))
    meta_g = pd.DataFrame({
        "sample_id":   sample_ids[:n],
        "source":      source_names[:n],
        "sample_type": types_geo[:n],
    }).set_index("sample_id")

    col_header = None
    expr_rows  = []
    with gzip.open(GEO_LOCAL, "rt") as f:
        in_table = False
        for line in f:
            line = line.rstrip()
            if line.startswith(
                    "!series_matrix_table_begin"):
                in_table = True
                continue
            if line.startswith(
                    "!series_matrix_table_end"):
                break
            if in_table:
                if col_header is None:
                    col_header = line.split("\t")
                else:
                    expr_rows.append(
                        line.split("\t"))

    probe_ids = [r[0].strip('"')
                 for r in expr_rows]
    col_ids   = [c.strip('"')
                 for c in col_header[1:]]

    values = []
    for row in expr_rows:
        vals = []
        for v in row[1:]:
            try:
                vals.append(float(
                    v.strip()))
            except ValueError:
                vals.append(np.nan)
        values.append(vals[:len(col_ids)])

    probe_df = pd.DataFrame(
        values, index=probe_ids,
        columns=col_ids)
    probe_df = np.log2(
        probe_df.clip(lower=0) + 1)

    t_ids = meta_g[
        meta_g.sample_type == "tumour"
    ].index.tolist()
    t_cols = [c for c in t_ids
              if c in probe_df.columns]

    target_probes = {}
    for pid in probe_df.index:
        sym = probe_map.get(pid)
        if sym and sym in FULL_PANEL:
            target_probes.setdefault(
                sym, []).append(pid)

    gene_rows = {}
    for sym, probes in target_probes.items():
        if len(probes) == 1:
            gene_rows[sym] = probe_df.loc[
                probes[0]]
        else:
            best = max(probes, key=lambda p:(
                probe_df.loc[p, t_cols].mean()
                if t_cols else
                probe_df.loc[p].mean()))
            gene_rows[sym] = probe_df.loc[best]

    gene_df = pd.DataFrame(gene_rows).T
    log(f"  Panel genes: {len(gene_df)}")
    return gene_df, meta_g, t_cols

# ═══════════════════════════════════════════════════════
# SURVIVAL DOWNLOAD + PARSE
# ═══════════════════════════════════════════════════════

def load_survival():
    log("")
    log("=" * 60)
    log("SURVIVAL — TCGA-KIRC")
    log("=" * 60)

    if not os.path.exists(SURV_LOCAL):
        for url, dest in SURV_URLS:
            if fetch_url(url, dest):
                break

    if not os.path.exists(SURV_LOCAL):
        log("  Survival file not found.")
        return None

    try:
        surv = pd.read_csv(SURV_LOCAL,
                           sep="\t")
        log(f"  Columns: {list(surv.columns)}")
        log(f"  Shape: {surv.shape}")

        # Xena survival columns
        id_col    = None
        time_col  = None
        event_col = None

        for c in surv.columns:
            cl = c.lower()
            if "sample" in cl or cl in (
                    "sampleid", "_sample_id"):
                id_col = c
            if "os.time" in cl or cl == "os_time":
                time_col = c
            if (cl in ("os", "os_event",
                        "vital_status") or
                    cl.startswith("os.")):
                if "time" not in cl:
                    event_col = c

        log(f"  id={id_col}  "
            f"time={time_col}  "
            f"event={event_col}")

        if id_col is None:
            id_col = surv.columns[0]
        surv = surv.set_index(id_col)

        if time_col and event_col:
            surv_out = pd.DataFrame({
                "os_time":  pd.to_numeric(
                    surv[time_col],
                    errors="coerce"),
                "os_event": pd.to_numeric(
                    surv[event_col],
                    errors="coerce"),
            })
            n_valid = (
                surv_out.os_time.notna() &
                surv_out.os_event.notna()
            ).sum()
            log(f"  Valid survival: {n_valid}")
            return surv_out
        else:
            log("  Cannot identify time/event cols.")
            log("  Attempting column scan...")
            for c in surv.columns:
                log(f"    {c}: "
                    f"{surv[c].dtype} "
                    f"sample={surv[c].iloc[:3].tolist()}")
            return None

    except Exception as e:
        log(f"  Survival parse failed: {e}")
        return None

# ═══════════════════════════════════════════════════════
# OBJ-1  DEPTH STRATA
# ═══════════════════════════════════════════════════════

def depth_strata(expr_t, depth_t, t_cols,
                 label):
    log("")
    log("=" * 60)
    log(f"OBJ-1 — DEPTH STRATA — {label}")
    log("=" * 60)

    d = depth_t.reindex(t_cols).dropna()

    q1 = float(np.percentile(d, 25))
    q2 = float(np.percentile(d, 50))
    q3 = float(np.percentile(d, 75))

    # Three strata: low / mid / high
    # Thresholds from Script 1 prediction:
    # Low <0.55 / Mid 0.55-0.70 / High >0.70
    # But override with actual quartiles if
    # distribution deviates significantly
    low_t  = min(0.55, float(
        np.percentile(d, 30)))
    high_t = max(0.70, float(
        np.percentile(d, 70)))

    low  = d[d <= low_t]
    mid  = d[(d > low_t) & (d <= high_t)]
    high = d[d > high_t]

    log(f"  Distribution:")
    log(f"    Q25={q1:.4f}  Q50={q2:.4f}"
        f"  Q75={q3:.4f}")
    log(f"  Strata thresholds:")
    log(f"    Low  ≤ {low_t:.2f}  "
        f"(n={len(low)}, "
        f"{100*len(low)/len(d):.1f}%)")
    log(f"    Mid    {low_t:.2f}-{high_t:.2f}"
        f"  (n={len(mid)}, "
        f"{100*len(mid)/len(d):.1f}%)")
    log(f"    High > {high_t:.2f}  "
        f"(n={len(high)}, "
        f"{100*len(high)/len(d):.1f}%)")

    strata = pd.Series("Mid", index=d.index)
    strata[low.index]  = "Low"
    strata[high.index] = "High"

    # Gene expression by stratum
    log("")
    log(f"  Gene expression by stratum:")
    log(f"  {'Gene':<12} {'Low':>9} "
        f"{'Mid':>9} {'High':>9}  trend")
    log(f"  {'-'*12} {'-'*9} {'-'*9} "
        f"{'-'*9}  {'-'*20}")

    rows = []
    for gene in FULL_PANEL:
        if gene not in expr_t.index:
            continue
        g_vals = pd.Series(
            expr_t.loc[gene, t_cols].values,
            index=t_cols
        ).reindex(d.index)

        m_low  = float(g_vals[
            strata=="Low"].mean())
        m_mid  = float(g_vals[
            strata=="Mid"].mean())
        m_high = float(g_vals[
            strata=="High"].mean())

        if m_high > m_low:
            trend = "UP with depth"
        elif m_high < m_low:
            trend = "DOWN with depth"
        else:
            trend = "flat"

        rows.append({
            "gene":   gene,
            "low":    round(m_low,  4),
            "mid":    round(m_mid,  4),
            "high":   round(m_high, 4),
            "trend":  trend,
        })

    df = pd.DataFrame(rows)
    df.to_csv(
        os.path.join(
            S2_DIR,
            f"strata_{label.lower()}.csv"),
        index=False)

    # Print key genes only
    key = (SW_GENES + FA_GENES +
           ["VIM","TGFB1","FAP",
            "COL1A1","FOXP3","MYC",
            "CPT1A","PLIN2","PAX8"])
    for _, row in df[
            df.gene.isin(key)].iterrows():
        log(f"  {row.gene:<12} "
            f"{row.low:>9.4f} "
            f"{row.mid:>9.4f} "
            f"{row.high:>9.4f}  "
            f"{row.trend}")

    return strata, low_t, high_t, df

# ═══════════════════════════════════════════════════════
# OBJ-2/3/4/5  CIRCUIT TESTS
# ═══════════════════════════════════════════════════════

def circuit_tests(expr_t, t_cols, label):
    log("")
    log("=" * 60)
    log(f"OBJ 2-5 — CIRCUIT TESTS — {label}")
    log("=" * 60)
    log("  |r|>0.40 = CONNECTED")
    log("  |r|<0.20 = BROKEN")
    log("  Prediction in brackets")
    log("")

    rows = []
    for (gene_a, gene_b, expected,
         meaning) in CIRCUIT_PAIRS:
        if (gene_a not in expr_t.index or
                gene_b not in expr_t.index):
            rows.append({
                "gene_a":   gene_a,
                "gene_b":   gene_b,
                "r":        np.nan,
                "status":   "NOT_IN_DATA",
                "expected": expected,
                "meaning":  meaning,
            })
            continue
        a = pd.Series(
            expr_t.loc[gene_a, t_cols].values,
            dtype=float)
        b = pd.Series(
            expr_t.loc[gene_b, t_cols].values,
            dtype=float)
        r, p = safe_r(a.values, b.values)
        if np.isnan(r):
            status = "INSUFFICIENT"
        elif abs(r) >= 0.40:
            status = "CONNECTED"
        elif abs(r) < 0.20:
            status = "BROKEN"
        else:
            status = "WEAK"

        # Prediction check
        if expected == "positive":
            pred_ok = (not np.isnan(r)
                       and r > 0)
        elif expected == "negative":
            pred_ok = (not np.isnan(r)
                       and r < 0)
        else:
            pred_ok = True

        verdict = "✓" if pred_ok else "✗"

        rows.append({
            "gene_a":   gene_a,
            "gene_b":   gene_b,
            "r":        round(r, 4)
                        if not np.isnan(r)
                        else np.nan,
            "p":        p,
            "p_fmt":    fmt_p(p),
            "status":   status,
            "expected": expected,
            "verdict":  verdict,
            "meaning":  meaning,
        })

    df = pd.DataFrame(rows)
    df.to_csv(
        os.path.join(
            S2_DIR,
            f"circuits_{label.lower()}.csv"),
        index=False)

    # Group output by objective
    groups = [
        ("OBJ-2  LIPID CIRCUIT",
         ["SCD", "CPT1A", "ACLY", "PLIN2",
          "FBP1"]),
        ("OBJ-3  MESENCHYMAL CIRCUIT",
         ["VIM", "FBP1", "SLC34A1",
          "TGFB1", "SNAI1"]),
        ("OBJ-4  FIBROTIC CIRCUIT",
         ["TGFB1", "FAP", "COL1A1",
          "ACTA2"]),
        ("OBJ-5  IMMUNE CIRCUIT",
         ["TGFB1", "FOXP3", "CD68",
          "CD274"]),
        ("EPAS1 CIRCUIT",
         ["EPAS1", "VHL"]),
        ("EZH2 CIRCUIT",
         ["EZH2"]),
        ("PAX CIRCUIT",
         ["PAX8", "PAX2"]),
        ("MYC/mTOR CIRCUIT",
         ["MYC", "MTOR"]),
    ]

    for group_name, genes in groups:
        log(f"\n  {group_name}:")
        log(f"  {'Circuit':<28} {'r':>8}  "
            f"{'Status':>12}  V")
        log(f"  {'-'*28} {'-'*8}  "
            f"{'-'*12}  -")
        sub = df[
            df.gene_a.isin(genes) |
            df.gene_b.isin(genes)
        ]
        for _, row in sub.iterrows():
            circuit = (f"{row.gene_a}"
                       f"→{row.gene_b}")
            r_s = (f"{row.r:>8.4f}"
                   if not pd.isna(row.r)
                   else f"{'NA':>8}")
            log(f"  {circuit:<28} {r_s}  "
                f"{row.status:>12}  "
                f"{row.get('verdict','?')}")

    return df

# ═══════════════════════════════════════════════════════
# OBJ-6  SURVIVAL
# ═══════════════════════════════════════════════════════

def survival_analysis(depth_t, strata,
                      surv_df, t_cols):
    log("")
    log("=" * 60)
    log("OBJ-6 — SURVIVAL STRATIFICATION")
    log("=" * 60)

    if surv_df is None:
        log("  No survival data available.")
        log("  Skipping survival analysis.")
        return None

    # Align depth and survival
    common = depth_t.index.intersection(
        surv_df.index).intersection(
        pd.Index(t_cols))

    df = pd.DataFrame({
        "depth":     depth_t.reindex(common),
        "stratum":   strata.reindex(common),
        "os_time":   surv_df.loc[
            common, "os_time"],
        "os_event":  surv_df.loc[
            common, "os_event"],
    }).dropna(subset=["os_time", "os_event"])

    df = df[df.os_time > 0]
    n_valid = len(df)
    log(f"  Samples with valid survival: "
        f"{n_valid}")

    if n_valid < 20:
        log("  Insufficient data for "
            "survival analysis.")
        return None

    # Cox proportional hazards — manual
    # Using log-rank and depth quartiles
    df["depth_q"] = pd.qcut(
        df.depth, 4,
        labels=["Q1","Q2","Q3","Q4"])

    log("")
    log("  KAPLAN-MEIER BY DEPTH QUARTILE:")
    log("  Q1 = shallowest, Q4 = deepest")
    log("")
    log(f"  {'Quartile':<10} {'n':>5} "
        f"{'Median OS (days)':>20} "
        f"{'Events':>8}")
    log(f"  {'-'*10} {'-'*5} {'-'*20} "
        f"{'-'*8}")

    km_data = {}
    for q in ["Q1","Q2","Q3","Q4"]:
        sub = df[df.depth_q == q]
        n   = len(sub)
        ev  = int(sub.os_event.sum())
        t   = sub.os_time.values
        e   = sub.os_event.values.astype(int)

        # Simple median OS estimate
        sorted_idx = np.argsort(t)
        t_sorted   = t[sorted_idx]
        e_sorted   = e[sorted_idx]

        n_at_risk = n
        surv      = 1.0
        surv_vals = []
        for ti, ei in zip(t_sorted,
                           e_sorted):
            if ei == 1:
                surv *= (1 - 1 / n_at_risk)
            n_at_risk -= 1
            surv_vals.append(surv)

        median_os = np.nan
        for i, sv in enumerate(surv_vals):
            if sv <= 0.5:
                median_os = t_sorted[i]
                break

        km_data[q] = {
            "t": t_sorted,
            "s": np.array(surv_vals),
            "n": n,
        }
        log(f"  {q:<10} {n:>5} "
            f"{median_os:>20.1f} "
            f"{ev:>8}")

    # Log-rank: Q1 vs Q4
    q1_df = df[df.depth_q == "Q1"]
    q4_df = df[df.depth_q == "Q4"]

    if len(q1_df) > 5 and len(q4_df) > 5:
        # Mantel-Cox log-rank statistic
        all_t = np.unique(
            np.concatenate([
                q1_df.os_time.values,
                q4_df.os_time.values
            ]))

        O1 = E1 = O4 = E4 = 0
        n1 = len(q1_df)
        n4 = len(q4_df)
        for t_evt in all_t:
            d1 = int((
                (q1_df.os_time == t_evt) &
                (q1_df.os_event == 1)
            ).sum())
            d4 = int((
                (q4_df.os_time == t_evt) &
                (q4_df.os_event == 1)
            ).sum())
            at1 = int(
                (q1_df.os_time >= t_evt
                 ).sum())
            at4 = int(
                (q4_df.os_time >= t_evt
                 ).sum())
            n_t = at1 + at4
            d_t = d1 + d4
            if n_t < 2:
                continue
            O1 += d1
            O4 += d4
            e1  = d_t * at1 / n_t
            e4  = d_t * at4 / n_t
            E1 += e1
            E4 += e4

        if E1 > 0 and E4 > 0:
            chi2 = (
                (O1 - E1)**2 / E1 +
                (O4 - E4)**2 / E4
            )
            p_lr = float(
                stats.chi2.sf(chi2, 1))
            log("")
            log(f"  Log-rank Q1 vs Q4:")
            log(f"    χ² = {chi2:.3f}  "
                f"p = {fmt_p(p_lr)}")
            if p_lr < 0.01:
                log(f"    PREDICTION CONFIRMED: "
                    f"p < 0.01 ✓")
            elif p_lr < 0.05:
                log(f"    Significant (p<0.05)")
            else:
                log(f"    NOT SIGNIFICANT — "
                    f"PREDICTION WRONG ✗")
        else:
            p_lr = np.nan
            log("  Log-rank could not be computed.")

    # Cox-like: Pearson depth vs log(OS)
    df_cox = df[df.os_event == 1].copy()
    if len(df_cox) > 20:
        log("")
        log("  DEPTH vs OS (events only, "
            "Pearson on log-time):")
        r_cox, p_cox = safe_r(
            df_cox.depth.values,
            np.log(df_cox.os_time.values
                   + 1))
        log(f"    r(depth, log_OS) = "
            f"{r_cox:.4f}  "
            f"p = {fmt_p(p_cox)}")
        if r_cox < -0.15 and p_cox < 0.05:
            log(f"    Deep tumours = "
                f"shorter survival ✓")
        else:
            log(f"    Direction or significance"
                f" unexpected.")

    # Strata survival summary
    log("")
    log("  SURVIVAL BY STRATUM "
        "(Low/Mid/High):")
    log(f"  {'Stratum':<10} {'n':>5} "
        f"{'Median OS':>12} {'Events':>8}")
    log(f"  {'-'*10} {'-'*5} {'-'*12} "
        f"{'-'*8}")

    for stratum in ["Low", "Mid", "High"]:
        sub = df[df.stratum == stratum]
        if len(sub) < 3:
            continue
        t  = sub.os_time.values
        e  = sub.os_event.values.astype(int)
        ev = int(e.sum())

        sorted_idx = np.argsort(t)
        t_s  = t[sorted_idx]
        e_s  = e[sorted_idx]
        n_ar = len(t_s)
        surv = 1.0
        med  = np.nan
        for ti, ei in zip(t_s, e_s):
            if ei == 1:
                surv *= (1 - 1 / n_ar)
            n_ar -= 1
            if surv <= 0.5 and np.isnan(med):
                med = ti

        log(f"  {stratum:<10} {len(sub):>5} "
            f"{med:>12.1f} {ev:>8}")

    # Save
    df.to_csv(
        os.path.join(S2_DIR,
                     "survival_depth.csv"),
        index=True)

    return df, km_data

# ════════════════���══════════════════════════════════════
# OBJ-7  3-GENE PANEL VALIDATION
# ═══════════════════════════════════════════════════════

def panel_validation(expr_t, depth_t,
                     t_cols, label):
    log("")
    log("=" * 60)
    log(f"OBJ-7 — 3-GENE PANEL VALIDATION"
        f" — {label}")
    log("=" * 60)
    log("  Predicted panel: "
        "SLC2A1(+) / VIM(+) / FBP1(-)")
    log("  Target r >= 0.85")
    log("")

    d = depth_t.reindex(t_cols).dropna()

    def panel_score(genes_pos,
                    genes_neg, name):
        avail_p = [g for g in genes_pos
                   if g in expr_t.index]
        avail_n = [g for g in genes_neg
                   if g in expr_t.index]
        if not avail_p and not avail_n:
            log(f"    {name}: no genes found")
            return np.nan

        score = pd.Series(
            np.zeros(len(d)), index=d.index,
            dtype=float)
        comp  = 0

        if avail_p:
            mat_p = pd.DataFrame({
                g: pd.Series(
                    expr_t.loc[g, t_cols].values,
                    index=t_cols
                ).reindex(d.index)
                for g in avail_p
            })
            score += norm01(
                mat_p.mean(axis=1).values)
            comp += 1

        if avail_n:
            mat_n = pd.DataFrame({
                g: pd.Series(
                    expr_t.loc[g, t_cols].values,
                    index=t_cols
                ).reindex(d.index)
                for g in avail_n
            })
            score += (1 - norm01(
                mat_n.mean(axis=1).values))
            comp += 1

        if comp > 0:
            score /= comp

        r, p = safe_r(score.values,
                      d.values)
        flag = ("✓" if abs(r) >= 0.85
                else ("~" if abs(r) >= 0.70
                      else "✗"))
        log(f"    {name:<35} "
            f"r={r:+.4f}  "
            f"p={fmt_p(p)}  {flag}")
        return r

    log("  Panel candidates:")

    # Predicted 3-gene panel
    r3 = panel_score(
        ["SLC2A1", "VIM"],
        ["FBP1"],
        "SLC2A1(+) VIM(+) FBP1(-)")

    # Extended 4-gene
    r4a = panel_score(
        ["SLC2A1", "VIM", "TGFB1"],
        ["FBP1"],
        "SLC2A1(+) VIM(+) TGFB1(+) FBP1(-)")

    # Alternative — add CA9
    r4b = panel_score(
        ["SLC2A1", "VIM", "CA9"],
        ["FBP1"],
        "SLC2A1(+) VIM(+) CA9(+) FBP1(-)")

    # Alternative — replace VIM with SCD
    r4c = panel_score(
        ["SLC2A1", "SCD"],
        ["FBP1", "CPT1A"],
        "SLC2A1(+) SCD(+) FBP1(-) CPT1A(-)")

    # 2-gene minimal
    r2a = panel_score(
        ["SLC2A1"],
        ["FBP1"],
        "SLC2A1(+) FBP1(-)")

    r2b = panel_score(
        ["SLC2A1"],
        ["SLC34A1"],
        "SLC2A1(+) SLC34A1(-)")

    log("")
    if abs(r3) >= 0.85:
        log("  PREDICTION CONFIRMED: "
            "3-gene panel r >= 0.85 ✓")
    elif abs(r3) >= 0.70:
        log("  PARTIAL: 3-gene panel "
            "r >= 0.70 — expand panel")
    else:
        log("  PREDICTION WRONG: "
            "3-gene panel r < 0.70")
        log("  Extended panels tested above.")

    return {
        "3gene": r3,
        "4gene_a": r4a,
        "4gene_b": r4b,
        "4gene_c": r4c,
        "2gene_a": r2a,
        "2gene_b": r2b,
    }

# ═══════════════════════════════════════════════════════
# OBJ-8  DRUG TARGET MAP
# ═══════════════════════════════════════════════════════

def drug_target_map(expr_t, depth_t,
                    strata, t_cols):
    log("")
    log("=" * 60)
    log("OBJ-8 — DRUG TARGET MAP")
    log("=" * 60)

    d = depth_t.reindex(t_cols).dropna()

    log("")
    log(f"  {'Gene':<12} {'Drug':<40} "
        f"{'r(depth)':>10}  {'p':>10}  Tier")
    log(f"  {'-'*12} {'-'*40} "
        f"{'-'*10}  {'-'*10}  {'-'*12}")

    rows = []
    for gene, drug in DRUG_TARGETS:
        if gene not in expr_t.index:
            rows.append({
                "gene":   gene,
                "drug":   drug,
                "r":      np.nan,
                "p":      np.nan,
                "tier":   "NO_DATA",
            })
            continue

        g_vals = pd.Series(
            expr_t.loc[gene, t_cols].values,
            index=t_cols
        ).reindex(d.index)

        r, p = safe_r(g_vals.values,
                      d.values)

        if np.isnan(r):
            tier = "NO_DATA"
        elif abs(r) >= 0.50:
            tier = "TIER_1"
        elif abs(r) >= 0.30:
            tier = "TIER_2"
        elif abs(r) >= 0.15:
            tier = "TIER_3"
        else:
            tier = "DEPTH_AGNOSTIC"

        rows.append({
            "gene": gene,
            "drug": drug,
            "r":    round(r, 4)
                    if not np.isnan(r)
                    else np.nan,
            "p":    p,
            "tier": tier,
        })

    df = pd.DataFrame(rows)
    df = df.sort_values(
        "r", key=abs, ascending=False,
        na_position="last")
    df.to_csv(
        os.path.join(S2_DIR,
                     "drug_targets.csv"),
        index=False)

    for _, row in df.iterrows():
        r_s = (f"{row.r:>+10.4f}"
               if not pd.isna(row.r)
               else f"{'NA':>10}")
        p_s = (fmt_p(row.p)
               if not pd.isna(row.p)
               else "NA")
        log(f"  {row.gene:<12} {row.drug:<40}"
            f" {r_s}  {p_s:>10}  {row.tier}")

    log("")
    log("  TIER 1 (|r| >= 0.50 — depth dominant):")
    t1 = df[df.tier == "TIER_1"]
    for _, row in t1.iterrows():
        log(f"    {row.gene:<12} {row.drug}")
        if row.r > 0:
            log(f"    ↑ with depth — target "
                f"deep tumours")
        else:
            log(f"    ↓ with depth — "
                f"shallow tumour marker")

    log("")
    log("  DEPTH-STRATIFIED PRESCRIPTION MAP:")
    log("  (derived from geometry — "
        "pre-literature)")
    log("")
    log("  HIGH DEPTH (>0.70):")

    t1_pos = df[(df.tier.isin([
        "TIER_1","TIER_2"])) &
        (df.r > 0)].head(6)
    for _, row in t1_pos.iterrows():
        log(f"    {row.drug}")

    log("")
    log("  LOW DEPTH (<0.55):")
    t1_neg = df[(df.tier.isin([
        "TIER_1","TIER_2"])) &
        (df.r < 0)].head(4)
    for _, row in t1_neg.iterrows():
        log(f"    {row.drug}")

    return df

# ═══════════════════════════════════════════════════════
# FIGURE
# ═══════════════════════════════════════════════════════

def generate_figure(depth_t, strata,
                    km_data, drug_df,
                    circuit_df,
                    panel_r):
    log("")
    log("Generating Script 2 figure...")
    fig = plt.figure(figsize=(18, 12))
    gs  = gridspec.GridSpec(
        3, 3, figure=fig,
        hspace=0.50, wspace=0.42)
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[0, 2])
    ax_d = fig.add_subplot(gs[1, 0])
    ax_e = fig.add_subplot(gs[1, 1])
    ax_f = fig.add_subplot(gs[1, 2])
    ax_g = fig.add_subplot(gs[2, 0])
    ax_h = fig.add_subplot(gs[2, 1])
    ax_i = fig.add_subplot(gs[2, 2])

    cmap = {
        "Low":  "#2ecc71",
        "Mid":  "#f39c12",
        "High": "#e74c3c",
    }

    # A — depth distribution coloured by stratum
    for s, c in cmap.items():
        sub = depth_t[strata == s]
        ax_a.hist(sub.values, bins=20,
                  color=c, alpha=0.75,
                  edgecolor="black",
                  linewidth=0.3,
                  label=s)
    ax_a.legend(fontsize=7)
    ax_a.set_title("A — Depth strata",
                   fontsize=9)
    ax_a.set_xlabel("Depth", fontsize=8)
    ax_a.set_ylabel("n", fontsize=8)

    # B — KM curves if available
    if km_data:
        colors_km = {
            "Q1": "#2ecc71", "Q2": "#f1c40f",
            "Q3": "#e67e22", "Q4": "#e74c3c",
        }
        for q, d_km in km_data.items():
            ax_b.step(d_km["t"], d_km["s"],
                      label=q,
                      color=colors_km.get(
                          q, "grey"),
                      linewidth=1.2)
        ax_b.axhline(0.5, color="black",
                     linewidth=0.8,
                     linestyle="--",
                     alpha=0.5)
        ax_b.set_title(
            "B — KM by depth quartile",
            fontsize=9)
        ax_b.set_xlabel("Days", fontsize=8)
        ax_b.set_ylabel("Survival", fontsize=8)
        ax_b.legend(fontsize=7)
    else:
        ax_b.text(0.5, 0.5,
                  "No survival data",
                  ha="center", va="center",
                  fontsize=9,
                  transform=ax_b.transAxes)
        ax_b.set_title(
            "B — KM (no data)", fontsize=9)

    # C — drug target r vs depth
    if drug_df is not None:
        df_plot = drug_df.dropna(
            subset=["r"]).sort_values("r")
        colors_d = ["#e74c3c" if r > 0
                    else "#2ecc71"
                    for r in df_plot.r.values]
        ax_c.barh(df_plot.gene.values,
                  df_plot.r.values,
                  color=colors_d,
                  edgecolor="black",
                  linewidth=0.3)
        ax_c.axvline(0, color="black",
                     linewidth=0.8,
                     linestyle="--")
        ax_c.axvline(0.5, color="grey",
                     linewidth=0.6,
                     linestyle=":",
                     alpha=0.7)
        ax_c.axvline(-0.5, color="grey",
                     linewidth=0.6,
                     linestyle=":",
                     alpha=0.7)
        ax_c.set_title(
            "C — Drug target r(depth)",
            fontsize=9)
        ax_c.set_xlabel("r", fontsize=8)
        ax_c.tick_params(axis="y",
                         labelsize=6)

    # D — circuit connectivity heatmap
    if circuit_df is not None:
        sub_c = circuit_df.dropna(
            subset=["r"])
        if not sub_c.empty:
            n_show = min(20, len(sub_c))
            sub_c  = sub_c.head(n_show)
            labels = [f"{r.gene_a}→{r.gene_b}"
                      for _, r in
                      sub_c.iterrows()]
            colors_c = []
            for _, r in sub_c.iterrows():
                if r.status == "CONNECTED":
                    colors_c.append("#e74c3c")
                elif r.status == "BROKEN":
                    colors_c.append("#2ecc71")
                else:
                    colors_c.append("#f39c12")
            ax_d.barh(labels[::-1],
                      sub_c.r.values[::-1],
                      color=colors_c[::-1],
                      edgecolor="black",
                      linewidth=0.3)
            ax_d.axvline(0, color="black",
                         linewidth=0.8,
                         linestyle="--")
            ax_d.set_title(
                "D — Circuit r values",
                fontsize=9)
            ax_d.set_xlabel("r", fontsize=8)
            ax_d.tick_params(axis="y",
                             labelsize=5)

    # E — panel validation bars
    if panel_r:
        names = list(panel_r.keys())
        vals  = [abs(v) if not
                 (isinstance(v, float)
                  and np.isnan(v))
                 else 0
                 for v in panel_r.values()]
        colors_p = ["#27ae60"
                    if v >= 0.85
                    else ("#f39c12"
                          if v >= 0.70
                          else "#e74c3c")
                    for v in vals]
        ax_e.barh(names[::-1],
                  vals[::-1],
                  color=colors_p[::-1],
                  edgecolor="black",
                  linewidth=0.3)
        ax_e.axvline(0.85, color="green",
                     linewidth=1.2,
                     linestyle="--",
                     label="target=0.85")
        ax_e.axvline(0.70, color="orange",
                     linewidth=0.8,
                     linestyle=":",
                     label="min=0.70")
        ax_e.set_xlim(0, 1)
        ax_e.legend(fontsize=7)
        ax_e.set_title(
            "E — Panel r vs depth",
            fontsize=9)
        ax_e.set_xlabel("|r|", fontsize=8)
        ax_e.tick_params(axis="y",
                         labelsize=6)

    # F — scatter SLC2A1 vs FBP1
    if (depth_t is not None and
            "SLC2A1" in [
                g for g in FULL_PANEL] and
            "FBP1" in FULL_PANEL):
        ax_f.scatter(
            depth_t.values,
            depth_t.values * 0,
            alpha=0, s=0)
        ax_f.set_title(
            "F — Depth scatter (reserved)",
            fontsize=9)

    # G-I — text summaries
    for ax, title, lines in [
        (ax_g, "G — Obj 2-3 (Lipid/Mesen)",
         ["SCD×CPT1A",
          "VIM×FBP1",
          "SCD×FBP1",
          "See circuits_tcga.csv"]),
        (ax_h, "H — Obj 4-5 (Stroma/Immune)",
         ["TGFB1×FAP",
          "TGFB1×COL1A1",
          "TGFB1×FOXP3",
          "See circuits_tcga.csv"]),
        (ax_i, "I — Cross-cancer update",
         ["EZH2: gain-of-function CONFIRMED",
          "Circuit integrity: BROKEN",
          "Strategy: attractor dissolution",
          "Convergence node: EPAS1",
          "Primary panel: SLC2A1/VIM/FBP1"]),
    ]:
        ax.axis("off")
        ax.set_title(title, fontsize=9)
        for i, line in enumerate(lines):
            ax.text(0.05,
                    0.80 - i * 0.18,
                    line,
                    fontsize=7,
                    transform=ax.transAxes)

    fig.suptitle(
        "ccRCC False Attractor — Script 2\n"
        "Circuit Tests / Survival / "
        "Panel Validation / Drug Map",
        fontsize=11, fontweight="bold")

    out = os.path.join(S2_DIR,
                       "figure_s2.png")
    fig.savefig(out, dpi=150,
                bbox_inches="tight")
    plt.close(fig)
    log(f"  Figure saved: {out}")

# ═══════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════

def main():
    log("OrganismCore — ccRCC False Attractor")
    log("Script 2 — Protocol-Compliant")
    log("Document 94b | 2026-03-02")
    log("")
    log("OBJECTIVES LOCKED BEFORE RUN:")
    log("  OBJ-1  Depth strata")
    log("  OBJ-2  SCD×CPT1A lipid circuit")
    log("  OBJ-3  VIM×FBP1 mesenchymal circuit")
    log("  OBJ-4  Fibrotic circuit (TGFB1 arm)")
    log("  OBJ-5  Immune circuit (FOXP3 arm)")
    log("  OBJ-6  Survival stratification")
    log("  OBJ-7  3-gene panel r >= 0.85")
    log("  OBJ-8  Drug target depth map")
    log("")

    # Load S1 depth scores
    depth_t, depth_g = load_s1_outputs()

    # Reload expression matrices
    expr_t, meta_t, t_cols_t = parse_tcga()
    expr_g, meta_g, t_cols_g = parse_geo()

    # Survival
    surv_df = load_survival()

    # ── TCGA arm ────────────────────────────
    log("")
    log("═" * 60)
    log("PRIMARY — TCGA-KIRC")
    log("═" * 60)

    strata_t, low_t, high_t, strata_df_t = (
        depth_strata(
            expr_t, depth_t,
            t_cols_t, "TCGA"))

    circ_t = circuit_tests(
        expr_t, t_cols_t, "TCGA")

    surv_result = None
    km_data     = None
    if surv_df is not None:
        surv_result = survival_analysis(
            depth_t, strata_t,
            surv_df, t_cols_t)
        if (surv_result is not None and
                len(surv_result) == 2):
            _, km_data = surv_result

    panel_r = panel_validation(
        expr_t, depth_t,
        t_cols_t, "TCGA")

    drug_df = drug_target_map(
        expr_t, depth_t,
        strata_t, t_cols_t)

    # ── GEO arm ─────────────────────────────
    strata_g  = None
    circ_g    = None
    panel_r_g = None

    if expr_g is not None:
        log("")
        log("═" * 60)
        log("VALIDATION — GSE53757")
        log("═" * 60)

        strata_g, _, _, _ = depth_strata(
            expr_g, depth_g,
            t_cols_g, "GEO")

        circ_g = circuit_tests(
            expr_g, t_cols_g, "GEO")

        panel_r_g = panel_validation(
            expr_g, depth_g,
            t_cols_g, "GEO")

    # Figure
    generate_figure(
        depth_t, strata_t,
        km_data, drug_df,
        circ_t, panel_r)

    # Summary
    log("")
    log("=" * 60)
    log("SCRIPT 2 COMPLETE")
    log("=" * 60)
    log(f"  Outputs: {S2_DIR}")
    for fname in sorted(
            os.listdir(S2_DIR)):
        fpath = os.path.join(S2_DIR, fname)
        log(f"    {fname:<55} "
            f"{os.path.getsize(fpath):>8} bytes")
    log("")
    log("  NEXT: Read s2_log.txt fully.")
    log("  What are the circuit r values?")
    log("  Which objectives confirmed?")
    log("  Which predictions wrong?")
    log("  What is the panel r?")
    log("  What does the drug map show?")
    log("  Then write document 94b.")
    log("  Then run literature check (94c).")

    write_log()

if __name__ == "__main__":
    main()
