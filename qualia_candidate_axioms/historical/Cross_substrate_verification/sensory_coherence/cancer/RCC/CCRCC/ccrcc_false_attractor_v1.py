"""
ccRCC False Attractor Analysis — Script 1 v3
PROTOCOL-COMPLIANT DISCOVERY RUN

Framework: OrganismCore
Document 94 | 2026-03-02
Author: Eric Robert Lawson

PREDICTIONS LOCKED BEFORE DATA:

CELL OF ORIGIN: Proximal tubule epithelium — S3 segment
LINEAGE:
    Metanephric mesenchyme
        → Nephron progenitor (SIX2+, PAX2+)
        → Renal vesicle
        → S-shaped body
        → Proximal tubule progenitor (LHX1+, JAG1+)
        → Immature proximal tubule (CUBN+, LRP2+, SLC3A1+)
        → Mature PT S1/S2 (SLC34A1+, GATM+, AGXT+)
        → Mature PT S3 (AQP1+, PCK1+)   ← cell of origin
        → FALSE ATTRACTOR (VHL loss → EPAS1 lock)

PREDICTED BLOCK: PT maturation arrest at S3 stage
KEY EVENT:       VHL loss → constitutive EPAS1/HIF2α activation
PHENOTYPE:       Clear cell (lipid/glycogen), PT metabolic identity lost

SWITCH GENES (predicted DOWN in ccRCC):
    UMOD    — PT S3 marker, strongest
    SLC34A1 — NaPi-IIa, PT sodium-phosphate cotransporter
    SLC13A3 — NaDC3, PT S3 dicarboxylate transporter
    AGXT    — PT-specific aminotransferase
    PCK1    — PEPCK1, gluconeogenic PT metabolic identity
    SLC22A6 — OAT1, PT identity transporter
    GATM    — Glycine amidinotransferase, PT specific
    AQP1    — PT water channel
    FBP1    — Fructose-1,6-bisphosphatase, gluconeogenic
    G6PC    — G6Pase, gluconeogenic

FA MARKERS (predicted UP in ccRCC):
    CA9     — direct EPAS1/HIF2α target, canonical ccRCC marker
    VEGFA   — EPAS1 transcriptional target
    EGLN3   — PHD3, HIF feedback target
    SLC2A1  — GLUT1, HIF glycolytic target
    PDK1    — HIF metabolic switch
    LDHA    — HIF glycolytic target
    EPAS1   — HIF2α, constitutively active in ccRCC
    SCD     — fatty acid desaturation
    ACLY    — acetyl-CoA from citrate
    EZH2    — PRC2 lock, predicted to silence PT identity

DRUG TARGETS (pre-data, stated before analysis):
    1. EPAS1/HIF2α inhibitor (belzutifan — MK-6482)
       Mechanism: direct EPAS1 inhibition breaks the lock
    2. mTOR inhibitor (everolimus, temsirolimus)
       Mechanism: mTORC1 downstream of EPAS1 in PT cells
    3. EZH2 inhibitor (tazemetostat)
       Mechanism: epigenetic lock maintenance
    4. VEGF/VEGFR inhibitor (sunitinib, bevacizumab)
       Mechanism: VEGFA is EPAS1 downstream, drives angiogenesis

DATASETS:
    Primary:    TCGA-KIRC (Xena HiSeqV2) — 534T / 72N
    Validation: GSE53757 (GEO GPL570)    — 72T  / 72N matched pairs
"""

import os
import gzip
import urllib.request

import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# ═══════════════════════════════════════════════════════
# DIRECTORIES
# ═══════════════════════════════════════════════════════

BASE_DIR    = "./ccrcc_false_attractor/"
RESULTS_DIR = os.path.join(BASE_DIR, "results_s1")
LOG_FILE    = os.path.join(RESULTS_DIR, "s1_log.txt")
os.makedirs(RESULTS_DIR, exist_ok=True)

# ═══════════════════════════════════════════════════════
# GENE PANELS — PREDICTIONS LOCKED
# ═════════════════════════════════���═════════════════════

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

# Gap test circuits — pairs to test
# (gene_A, gene_B, expected, biological_meaning)
GAP_TEST_CIRCUITS = [
    # VHL → PT identity axis
    ("VHL",    "SLC34A1",  "connected",
     "VHL loss = PT identity loss"),
    ("VHL",    "PCK1",     "connected",
     "VHL loss = gluconeogenic loss"),
    # EPAS1 direct targets
    ("EPAS1",  "CA9",      "connected",
     "EPAS1 directly activates CA9"),
    ("EPAS1",  "VEGFA",    "connected",
     "EPAS1 activates VEGFA"),
    ("VHL",    "EPAS1",    "inverse",
     "VHL degrades EPAS1"),
    ("EGLN3",  "EPAS1",    "connected",
     "EGLN3 is EPAS1 feedback target"),
    # PT maturation regulators
    ("LHX1",   "SLC34A1",  "connected",
     "LHX1 drives PT maturation"),
    ("HNF4A",  "PCK1",     "connected",
     "HNF4A drives gluconeogenesis"),
    # Metabolic circuits
    ("CPT1A",  "SCD",      "inverse",
     "FAO loss = desaturation gain"),
    ("PCK1",   "G6PC",     "connected",
     "gluconeogenic co-regulation"),
    # Epigenetic lock
    ("EZH2",   "LHX1",     "inverse",
     "EZH2 silences differentiation TFs"),
    ("EZH2",   "UMOD",     "inverse",
     "EZH2 silences PT identity"),
    # mTOR axis
    ("MTOR",   "SLC2A1",   "connected",
     "mTORC1 drives GLUT1 expression"),
    # VHL circuit integrity test
    ("VHL",    "CA9",      "inverse",
     "VHL intact = CA9 suppressed"),
]

# Full panel for depth correlations
# All genes the script will test r against depth
FULL_PANEL = list(dict.fromkeys(
    SW_GENES + FA_GENES + [
    # HIF circuit
    "HIF1A",  "VHL",    "ARNT",
    "EGLN1",  "EGLN2",
    # PT maturation
    "LHX1",   "HNF4A",  "HNF1A",
    "JAG1",   "PAX8",
    # Nephron progenitor
    "SIX2",   "PAX2",   "WT1",
    # Gluconeogenics
    "PCK2",   "ALDOB",
    # Lipid
    "FASN",   "ACACA",  "HMGCR",
    "CPT1A",  "FABP7",  "PLIN2",
    # EMT — open question
    "TWIST1", "VIM",    "ZEB1",
    "SNAI1",  "CDH1",   "FN1",
    # Stroma
    "ACTA2",  "FAP",    "TGFB1",
    "COL1A1", "WNT5A",
    # Epigenetic
    "BAP1",   "PBRM1",  "SETD2",
    "KDM5C",  "KDM1A",  "DNMT3A",
    # Immune
    "CD8A",   "CD274",  "FOXP3",
    "CD68",   "PDCD1",
    # mTOR / growth
    "MTOR",   "CCND1",  "MYC",
    "MET",    "PIK3CA", "PTEN",
    # Proliferation
    "MKI67",  "TOP2A",  "CDC20",
    "CCNB1",
]))

# ═══════════════════════════════════════════════════════
# DOWNLOADS
# ═══════════════════════════════════════════════════════

XENA_LOCAL = os.path.join(BASE_DIR, "TCGA_KIRC_HiSeqV2.gz")
GEO_LOCAL  = os.path.join(BASE_DIR, "GSE53757_series_matrix.txt.gz")

XENA_URLS = [
    "https://tcga-xena-hub.s3.us-east-1.amazonaws.com/download/"
    "TCGA.KIRC.sampleMap%2FHiSeqV2.gz",
    "https://tcga.xenahubs.net/download/TCGA.KIRC.sampleMap/HiSeqV2.gz",
]
GEO_URLS = [
    "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE53nnn/GSE53757/"
    "matrix/GSE53757_series_matrix.txt.gz",
]
GPL570_URLS = [
    (
        "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi"
        "?acc=GPL570&targ=self&form=text&view=full",
        os.path.join(BASE_DIR, "GPL570_soft.txt"),
    ),
    (
        "https://ftp.ncbi.nlm.nih.gov/geo/platforms/GPL570nnn/"
        "GPL570/annot/GPL570.annot.gz",
        os.path.join(BASE_DIR, "GPL570_full_table.txt.gz"),
    ),
]
GPL570_CANDIDATES = [
    os.path.join(BASE_DIR, "GPL570_soft.txt"),
    os.path.join(BASE_DIR, "GPL570_soft.txt.gz"),
    os.path.join(BASE_DIR, "GPL570_full_table.txt"),
    os.path.join(BASE_DIR, "GPL570_full_table.txt.gz"),
]

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
        r, p = stats.pearsonr(x[mask], y[mask])
        return r, p
    except Exception:
        return np.nan, np.nan

def safe_mwu(a, b):
    try:
        a = pd.Series(a).dropna()
        b = pd.Series(b).dropna()
        if len(a) < 3 or len(b) < 3:
            return np.nan, np.nan
        _, p = stats.mannwhitneyu(
            a, b, alternative="two-sided")
        return _, p
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

def try_urls(url_list, dest):
    if os.path.exists(dest):
        mb = os.path.getsize(dest) / (1024*1024)
        log(f"  Present ({mb:.1f} MB): {dest}")
        return True
    for url in url_list:
        if fetch_url(url, dest):
            return True
    return False

def find_gpl570():
    for path in GPL570_CANDIDATES:
        if os.path.exists(path):
            return path
    return None

def download_all():
    log("=" * 60)
    log("DOWNLOAD")
    log("=" * 60)
    if not try_urls(XENA_URLS, XENA_LOCAL):
        raise SystemExit("CRITICAL: TCGA-KIRC download failed.")
    if not try_urls(GEO_URLS, GEO_LOCAL):
        raise SystemExit("CRITICAL: GSE53757 download failed.")
    gpl570 = find_gpl570()
    if gpl570:
        return gpl570
    for url, dest in GPL570_URLS:
        if os.path.exists(dest):
            return dest
        if fetch_url(url, dest):
            return dest
    log("  GPL570 not found — GEO arm will be skipped.")
    return None

# ═══════════════════════════════════════════════════════
# GPL570 LOADER
# ═══════════════════════════════════════════════════════

def load_gpl570(path):
    is_gz  = path.endswith(".gz")
    opener = gzip.open if is_gz else open
    probe_map = {}
    header = id_col = sym_col = None
    try:
        with opener(path, "rt",
                    encoding="utf-8",
                    errors="replace") as f:
            for line in f:
                line = line.rstrip("\n")
                if line.startswith(("^","!","#")):
                    continue
                parts = line.split("\t")
                if header is None:
                    lower = [
                        p.strip().lower()
                        for p in parts]
                    if "id" in lower:
                        header  = parts
                        id_col  = lower.index("id")
                        sym_col = None
                        for c in [
                            "gene symbol","gene_symbol",
                            "symbol","gene assignment"]:
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
                sym = raw.split("///")[0].strip(
                    ).upper().split()[0]
                if sym in ("","---","N/A","NA"):
                    continue
                probe_map[pid] = sym
        log(f"  GPL570 probes: {len(probe_map)}")
        return probe_map
    except Exception as e:
        log(f"  GPL570 load failed: {e}")
        return None

# ═══════════════════════════════════════════════════════
# TCGA PARSER
# ═══════════════════════════════════════════════════════

def parse_tcga():
    log("")
    log("=" * 60)
    log("TCGA-KIRC — Parsing")
    log("=" * 60)
    with gzip.open(XENA_LOCAL, "rt") as f:
        raw = pd.read_csv(f, sep="\t",
                          index_col=0)
    log(f"  Shape: {raw.shape}")

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
    })
    n_t = (meta.sample_type=="tumour").sum()
    n_n = (meta.sample_type=="normal").sum()
    log(f"  Tumour: {n_t}  Normal: {n_n}")

    avail = [g for g in FULL_PANEL
             if g in raw.index]
    miss  = [g for g in FULL_PANEL
             if g not in raw.index]
    log(f"  Panel available: "
        f"{len(avail)} / {len(FULL_PANEL)}")
    if miss:
        log(f"  Missing: {miss}")

    expr = raw.loc[avail]
    return expr, meta

# ═══════════════════════════════════════════════════════
# GEO PARSER
# ═══════════════════════════════════════════════════════

def parse_geo(probe_map):
    log("")
    log("=" * 60)
    log("GSE53757 — Parsing")
    log("=" * 60)
    if probe_map is None:
        log("  No probe map. Skipping.")
        return None, None

    sample_ids = []
    source_names = []
    sample_titles = []

    with gzip.open(GEO_LOCAL, "rt") as f:
        for line in f:
            line = line.rstrip()
            if line.startswith(
                    "!Sample_geo_accession"):
                parts = line.split("\t")
                sample_ids.extend([
                    p.strip().strip('"')
                    for p in parts[1:]
                    if p.strip().strip('"'
                    ).startswith("GSM")])
            elif line.startswith(
                    "!Sample_source_name_ch1"):
                parts = line.split("\t")
                source_names.extend([
                    p.strip().strip('"')
                    for p in parts[1:]
                    if p.strip()])
            elif line.startswith(
                    "!Sample_title"):
                parts = line.split("\t")
                sample_titles.extend([
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

    n = min(len(sample_ids),
            len(types_geo))
    meta_geo = pd.DataFrame({
        "sample_id":   sample_ids[:n],
        "title":       sample_titles[:n],
        "source":      source_names[:n],
        "sample_type": types_geo[:n],
    })
    n_t = (meta_geo.sample_type=="tumour").sum()
    n_n = (meta_geo.sample_type=="normal").sum()
    log(f"  Tumour: {n_t}  Normal: {n_n}")

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

    if not col_header or not expr_rows:
        log("  CRITICAL: No expression table.")
        return None, None

    probe_ids = [r[0].strip('"')
                 for r in expr_rows]
    col_ids   = [c.strip('"')
                 for c in col_header[1:]]

    values = []
    for row in expr_rows:
        vals = []
        for v in row[1:]:
            try:
                vals.append(float(v.strip()))
            except ValueError:
                vals.append(np.nan)
        values.append(vals[:len(col_ids)])

    probe_df = pd.DataFrame(
        values,
        index=probe_ids,
        columns=col_ids)
    probe_df = np.log2(
        probe_df.clip(lower=0) + 1)
    log("  Log2(x+1) applied ✓")

    target_probes = {}
    for pid in probe_df.index:
        sym = probe_map.get(pid)
        if sym and sym in FULL_PANEL:
            target_probes.setdefault(
                sym, []).append(pid)

    t_ids = meta_geo.loc[
        meta_geo.sample_type == "tumour",
        "sample_id"].tolist()
    t_cols = [c for c in t_ids
              if c in probe_df.columns]

    gene_rows = {}
    for sym, probes in target_probes.items():
        if len(probes) == 1:
            gene_rows[sym] = probe_df.loc[
                probes[0]]
        else:
            best = max(probes, key=lambda p:(
                probe_df.loc[p, t_cols].mean()
                if t_cols
                else probe_df.loc[p].mean()))
            gene_rows[sym] = probe_df.loc[best]

    gene_df = pd.DataFrame(gene_rows).T
    gene_df.columns = col_ids[:gene_df.shape[1]]
    log(f"  Panel genes mapped: {len(gene_df)}")
    return gene_df, meta_geo

# ═══════════════════════════════════════════════════════
# SADDLE ANALYSIS
#
# Step 1 of the framework — canonical.
# Per-gene tumour vs normal FC + MWU.
# Produces saddle_res: gene → {result, fc, p}
# where result = "UP", "DOWN", or "NS".
# This feeds directly into build_depth_score.
# ═══════════════════════════════════════════════════════

def saddle_analysis(expr, tumour_mask,
                    meta, label):
    log("")
    log("=" * 60)
    log(f"SADDLE ANALYSIS — {label}")
    log("=" * 60)
    log("  Per-gene tumour vs normal.")
    log("  Produces saddle_res for depth score.")
    log("")

    t_cols = expr.columns[tumour_mask]
    n_mask = (
        meta.set_index("sample_id")
        .reindex(expr.columns)
        .sample_type == "normal"
    ).values
    n_cols = expr.columns[n_mask]

    if len(n_cols) == 0:
        log("  No normal samples. "
            "Using full panel for depth.")
        saddle_res = {
            g: {"result": "PREDICTED_UP"
                if g in FA_GENES else
                "PREDICTED_DOWN",
                "fc": 0.0, "p": 1.0}
            for g in expr.index
        }
        return saddle_res

    saddle_res = {}
    rows = []

    for gene in expr.index:
        t_vals = expr.loc[gene, t_cols].dropna()
        n_vals = expr.loc[gene, n_cols].dropna()
        if len(t_vals) < 3 or len(n_vals) < 3:
            continue
        fc  = float(
            t_vals.median() - n_vals.median())
        _, p = safe_mwu(t_vals, n_vals)
        if np.isnan(p):
            result = "NS"
        elif p < 0.05 and fc > 0:
            result = "UP"
        elif p < 0.05 and fc < 0:
            result = "DOWN"
        else:
            result = "NS"
        saddle_res[gene] = {
            "result": result,
            "fc":     fc,
            "p":      p,
        }
        rows.append({
            "gene":      gene,
            "log2FC":    round(fc, 4),
            "direction": result,
            "p_mwu":     p,
            "p_fmt":     fmt_p(p),
        })

    df = pd.DataFrame(rows)
    df = df.sort_values("log2FC",
                        key=abs,
                        ascending=False)
    df.to_csv(
        os.path.join(RESULTS_DIR,
                     f"saddle_{label.lower()}.csv"),
        index=False)

    # Prediction scorecard
    log(f"  {'Gene':<12} {'Pred':>6} "
        f"{'Found':>6} {'FC':>8}  Verdict")
    log(f"  {'-'*12} {'-'*6} {'-'*6} "
        f"{'-'*8}  {'-'*12}")

    sw_conf  = []
    fa_conf  = []
    sw_wrong = []
    fa_wrong = []

    for gene in SW_GENES + FA_GENES:
        pred = ("DOWN" if gene in SW_GENES
                else "UP")
        res  = saddle_res.get(gene, {})
        found = res.get("result", "NOT_IN_DATA")
        fc    = res.get("fc", np.nan)
        if found == pred:
            verdict = "✓"
            if gene in SW_GENES:
                sw_conf.append(gene)
            else:
                fa_conf.append(gene)
        else:
            verdict = "✗ WRONG"
            if gene in SW_GENES:
                sw_wrong.append(gene)
            else:
                fa_wrong.append(gene)
        fc_str = (f"{fc:.3f}"
                  if not np.isnan(fc) else "NA")
        log(f"  {gene:<12} {pred:>6} "
            f"{found:>6} {fc_str:>8}  {verdict}")

    log("")
    log(f"  SW↓ confirmed ({len(sw_conf)}): "
        f"{sw_conf}")
    log(f"  SW↓ wrong     ({len(sw_wrong)}): "
        f"{sw_wrong}")
    log(f"  FA↑ confirmed ({len(fa_conf)}): "
        f"{fa_conf}")
    log(f"  FA↑ wrong     ({len(fa_wrong)}): "
        f"{fa_wrong}")

    return saddle_res

# ═══════════════════════════════════════════════════════
# DEPTH SCORE
#
# Protocol-canonical build:
#   C1 = 1 - norm(mean of confirmed SW genes)
#   C2 = norm(mean of confirmed FA genes)
#   depth = (C1 + C2) / 2
#
# Uses saddle_res to select confirmed genes.
# Fallback to full predicted panel if <2 confirmed.
# This is identical to ICC v1 architecture.
# ═══════════════════════════════════════════════════════

def build_depth_score(expr, tumour_mask,
                      saddle_res, label):
    log("")
    log("=" * 60)
    log(f"DEPTH SCORE — {label}")
    log("=" * 60)

    # Confirmed SW genes (predicted DOWN, found DOWN)
    sw_ok = [g for g in SW_GENES
             if g in expr.index
             and saddle_res.get(g, {})
             .get("result") == "DOWN"]
    # Confirmed FA genes (predicted UP, found UP)
    fa_ok = [g for g in FA_GENES
             if g in expr.index
             and saddle_res.get(g, {})
             .get("result") == "UP"]

    # Fallback: use full predicted panel
    if len(sw_ok) < 2:
        log("  WARNING: <2 SW confirmed. "
            "Using full SW panel.")
        sw_ok = [g for g in SW_GENES
                 if g in expr.index]
    if len(fa_ok) < 2:
        log("  WARNING: <2 FA confirmed. "
            "Using full FA panel.")
        fa_ok = [g for g in FA_GENES
                 if g in expr.index]

    log(f"  SW genes ({len(sw_ok)}): {sw_ok}")
    log(f"  FA genes ({len(fa_ok)}): {fa_ok}")

    idx = expr.columns[tumour_mask]

    sw_mat = expr.loc[sw_ok, idx].values.T
    fa_mat = expr.loc[fa_ok, idx].values.T

    sw_mean = np.nanmean(sw_mat, axis=1)
    fa_mean = np.nanmean(fa_mat, axis=1)

    c1 = 1 - norm01(sw_mean)
    c2 = norm01(fa_mean)
    depth = (c1 + c2) / 2.0
    depth = pd.Series(depth, index=idx)

    log(f"  n tumour: {len(depth)}")
    log(f"  mean:     {depth.mean():.4f}")
    log(f"  median:   {depth.median():.4f}")
    log(f"  std:      {depth.std():.4f}")
    log(f"  Q25:      "
        f"{depth.quantile(0.25):.4f}")
    log(f"  Q75:      "
        f"{depth.quantile(0.75):.4f}")

    return depth

# ═══════════════════════════════════════════════════════
# DEPTH CORRELATIONS
#
# Protocol Step 2.3 — canonical.
# Pearson r for EVERY gene in full panel
# vs depth score, in tumour samples only.
# Sorted by |r|.
# This is the discovery step.
# ═══════════════════════════════════════════════════════

def depth_correlations(expr, depth,
                       tumour_mask, label):
    log("")
    log("=" * 60)
    log(f"DEPTH CORRELATIONS — {label}")
    log("=" * 60)

    idx        = expr.columns[tumour_mask]
    depth_vals = depth.reindex(idx).dropna()

    rows = []
    for gene in expr.index:
        gene_vals = expr.loc[
            gene, idx].reindex(depth_vals.index)
        r, p = safe_r(gene_vals.values,
                      depth_vals.values)
        if not np.isnan(r):
            rows.append({
                "gene": gene,
                "r":    round(r, 4),
                "p":    p,
                "p_fmt": fmt_p(p),
            })

    df = pd.DataFrame(rows)
    df = df.sort_values("r", ascending=False)
    df.to_csv(
        os.path.join(RESULTS_DIR,
                     f"depth_corr_{label.lower()}.csv"),
        index=False)

    log(f"  {'Rank':<5} {'Gene':<12} "
        f"{'r':>8}  direction")
    log(f"  {'-'*5} {'-'*12} {'-'*8}  {'-'*20}")

    pos = df[df.r > 0].head(15)
    log(f"\n  TOP 15 POSITIVE "
        f"(UP in deeper tumours):")
    for rank, (_, row) in enumerate(
            pos.iterrows(), 1):
        log(f"  {rank:<5} {row.gene:<12} "
            f"{row.r:>+8.4f}  {row.p_fmt}")

    neg = df[df.r < 0].tail(15).iloc[::-1]
    log(f"\n  TOP 15 NEGATIVE "
        f"(DOWN in deeper tumours):")
    for rank, (_, row) in enumerate(
            neg.iterrows(), 1):
        log(f"  {rank:<5} {row.gene:<12} "
            f"{row.r:>+8.4f}  {row.p_fmt}")

    return df

# ═══════════════════════════════════════════════════════
# GAP TESTS
# ═══════════════════════════════════════════════════════

def gap_tests(expr, tumour_mask, label):
    log("")
    log("=" * 60)
    log(f"GAP TESTS — {label}")
    log("=" * 60)
    log("  |r|>0.4 = CONNECTED")
    log("  |r|<0.2 = BROKEN → intervention point")
    log("")

    idx  = expr.columns[tumour_mask]
    rows = []

    for gene_a, gene_b, expected, meaning \
            in GAP_TEST_CIRCUITS:
        if (gene_a not in expr.index or
                gene_b not in expr.index):
            rows.append({
                "gene_a":   gene_a,
                "gene_b":   gene_b,
                "r":        np.nan,
                "status":   "NOT_IN_DATA",
                "expected": expected,
                "meaning":  meaning,
            })
            continue
        a = expr.loc[gene_a, idx]
        b = expr.loc[gene_b, idx]
        r, p = safe_r(a.values, b.values)
        if np.isnan(r):
            status = "INSUFFICIENT"
        elif abs(r) > 0.4:
            status = "CONNECTED"
        elif abs(r) < 0.2:
            status = "BROKEN"
        else:
            status = "WEAK"
        rows.append({
            "gene_a":   gene_a,
            "gene_b":   gene_b,
            "r":        round(r, 4),
            "p_fmt":    fmt_p(p),
            "status":   status,
            "expected": expected,
            "meaning":  meaning,
        })

    df = pd.DataFrame(rows)
    df.to_csv(
        os.path.join(RESULTS_DIR,
                     f"gap_tests_{label.lower()}.csv"),
        index=False)

    log(f"  {'Circuit':<26} {'r':>8} "
        f"  {'Status':>12}  Meaning")
    log(f"  {'-'*26} {'-'*8}  {'-'*12}  {'-'*35}")
    for _, row in df.iterrows():
        circuit = f"{row.gene_a}→{row.gene_b}"
        r_s = (f"{row.r:>8.4f}"
               if not pd.isna(row.r)
               else f"{'NA':>8}")
        log(f"  {circuit:<26} {r_s}  "
            f"{row.status:>12}  {row.meaning}")

    broken = df[df.status == "BROKEN"]
    if not broken.empty:
        log("")
        log("  BROKEN CIRCUITS — INTERVENTION POINTS:")
        for _, row in broken.iterrows():
            log(f"    {row.gene_a} → {row.gene_b}  "
                f"r={row.r:.3f}")
            log(f"    Block is between "
                f"{row.gene_a} and {row.gene_b}.")
            log(f"    Meaning: {row.meaning}")

    return df

# ═══════════════════════════════════════════════════════
# FIGURE
# ═══════════════════════════════════════════════════════

def generate_figure(depth_t, depth_g,
                    corr_t, corr_g,
                    saddle_t, expr_t,
                    tumour_mask_t):
    log("")
    log("Generating figure...")
    fig = plt.figure(figsize=(16, 10))
    gs  = gridspec.GridSpec(
        2, 3, figure=fig,
        hspace=0.45, wspace=0.40)
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[0, 2])
    ax_d = fig.add_subplot(gs[1, 0])
    ax_e = fig.add_subplot(gs[1, 1])
    ax_f = fig.add_subplot(gs[1, 2])

    # Panel A — depth distribution
    ax_a.hist(depth_t.values, bins=30,
              color="#e74c3c",
              edgecolor="black",
              linewidth=0.4, alpha=0.85)
    ax_a.axvline(depth_t.median(),
                 color="black",
                 linewidth=1.5,
                 linestyle="--")
    ax_a.set_title("A — Depth (TCGA)", fontsize=9)
    ax_a.set_xlabel("Depth Score", fontsize=8)
    ax_a.set_ylabel("Samples", fontsize=8)

    # Panel B — top depth correlates TCGA
    if corr_t is not None and not corr_t.empty:
        top = pd.concat([
            corr_t.head(10),
            corr_t.tail(10).iloc[::-1]
        ])
        colors_b = ["#e74c3c" if r > 0
                    else "#2ecc71"
                    for r in top.r.values]
        ax_b.barh(top.gene[::-1].values,
                  top.r[::-1].values,
                  color=colors_b[::-1],
                  edgecolor="black",
                  linewidth=0.3)
        ax_b.axvline(0, color="black",
                     linewidth=0.8,
                     linestyle="--")
        ax_b.set_title(
            "B — Top Depth Correlates (TCGA)",
            fontsize=9)
        ax_b.set_xlabel("r with depth", fontsize=8)
        ax_b.tick_params(axis="y",
                         labelsize=6)

    # Panel C — saddle FC plot
    if saddle_t is not None:
        saddle_df = pd.DataFrame([
            {"gene": g,
             "fc":   saddle_t.get(g, {}).get(
                 "fc", 0)}
            for g in SW_GENES + FA_GENES
            if g in saddle_t
        ])
        if not saddle_df.empty:
            saddle_df = saddle_df.sort_values("fc")
            colors_c = [
                "#e74c3c" if fc > 0
                else "#2ecc71"
                for fc in saddle_df.fc.values]
            ax_c.barh(saddle_df.gene.values,
                      saddle_df.fc.values,
                      color=colors_c,
                      edgecolor="black",
                      linewidth=0.3)
            ax_c.axvline(0, color="black",
                         linewidth=0.8,
                         linestyle="--")
            ax_c.set_title(
                "C — Saddle FC (T/N)",
                fontsize=9)
            ax_c.set_xlabel(
                "log2FC", fontsize=8)
            ax_c.tick_params(axis="y",
                             labelsize=7)

    # Panel D — GEO depth distribution
    if depth_g is not None:
        ax_d.hist(depth_g.values, bins=20,
                  color="#3498db",
                  edgecolor="black",
                  linewidth=0.4, alpha=0.85)
        ax_d.axvline(depth_g.median(),
                     color="black",
                     linewidth=1.5,
                     linestyle="--")
        ax_d.set_title(
            "D — Depth (GEO)", fontsize=9)
        ax_d.set_xlabel("Depth Score",
                        fontsize=8)
        ax_d.set_ylabel("Samples", fontsize=8)

    # Panel E — GEO top correlates
    if corr_g is not None and not corr_g.empty:
        top_g = pd.concat([
            corr_g.head(10),
            corr_g.tail(10).iloc[::-1]
        ])
        colors_e = ["#e74c3c" if r > 0
                    else "#2ecc71"
                    for r in top_g.r.values]
        ax_e.barh(top_g.gene[::-1].values,
                  top_g.r[::-1].values,
                  color=colors_e[::-1],
                  edgecolor="black",
                  linewidth=0.3)
        ax_e.axvline(0, color="black",
                     linewidth=0.8,
                     linestyle="--")
        ax_e.set_title(
            "E — Top Depth Correlates (GEO)",
            fontsize=9)
        ax_e.set_xlabel("r with depth",
                        fontsize=8)
        ax_e.tick_params(axis="y",
                         labelsize=6)

    # Panel F — cross-dataset r comparison
    if (corr_t is not None
            and corr_g is not None
            and not corr_t.empty
            and not corr_g.empty):
        merged = corr_t.merge(
            corr_g[["gene","r"]],
            on="gene",
            suffixes=("_tcga","_geo"))
        if not merged.empty:
            ax_f.scatter(
                merged.r_tcga.values,
                merged.r_geo.values,
                alpha=0.5, s=15,
                color="#9b59b6",
                edgecolors="black",
                linewidths=0.3)
            for _, row in merged.iterrows():
                if abs(row.r_tcga) > 0.45:
                    ax_f.annotate(
                        row.gene,
                        (row.r_tcga,
                         row.r_geo),
                        fontsize=5,
                        xytext=(3, 3),
                        textcoords="offset points")
            r_cr, _ = safe_r(
                merged.r_tcga.values,
                merged.r_geo.values)
            ax_f.set_title(
                f"F — Cross-Dataset r "
                f"(r={r_cr:.3f})",
                fontsize=9)
            ax_f.set_xlabel(
                "r TCGA", fontsize=8)
            ax_f.set_ylabel(
                "r GEO", fontsize=8)
            merged.to_csv(
                os.path.join(
                    RESULTS_DIR,
                    "cross_dataset_r.csv"),
                index=False)

    fig.suptitle(
        "ccRCC False Attractor — Script 1 v3\n"
        "Protocol-compliant: saddle → "
        "depth → correlations → gap tests",
        fontsize=11, fontweight="bold")
    out = os.path.join(RESULTS_DIR,
                       "figure_s1_v3.png")
    fig.savefig(out, dpi=150,
                bbox_inches="tight")
    plt.close(fig)
    log(f"  Figure saved: {out}")

# ═══════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════

def main():
    log("OrganismCore — ccRCC False Attractor")
    log("Script 1 v3 — Protocol-Compliant")
    log("Document 94 | 2026-03-02")
    log("")
    log("PROTOCOL ORDER (canonical):")
    log("  1. saddle_analysis()")
    log("     → per-gene tumour vs normal")
    log("     → produces saddle_res")
    log("  2. build_depth_score(saddle_res)")
    log("     → uses CONFIRMED genes only")
    log("     → fallback to full panel if <2")
    log("  3. depth_correlations()")
    log("     → Pearson r, every panel gene")
    log("     → THE DISCOVERY")
    log("  4. gap_tests()")
    log("     → circuit topology")
    log("     → BROKEN = intervention point")
    log("")

    # Downloads
    gpl570_path = download_all()
    probe_map   = None
    if gpl570_path:
        log("")
        log("=" * 60)
        log("GPL570")
        log("=" * 60)
        probe_map = load_gpl570(gpl570_path)

    # ── TCGA arm ────────────────────────────
    log("")
    log("═" * 60)
    log("PRIMARY — TCGA-KIRC")
    log("═" * 60)

    expr_t, meta_t = parse_tcga()

    meta_idx_t = (
        meta_t.set_index("sample_id")
        .reindex(expr_t.columns))
    tumour_mask_t = (
        meta_idx_t.sample_type == "tumour"
    ).values

    # Step 1 — saddle
    saddle_t = saddle_analysis(
        expr_t, tumour_mask_t,
        meta_t, "TCGA")

    # Step 2 — depth from confirmed genes
    depth_t = build_depth_score(
        expr_t, tumour_mask_t,
        saddle_t, "TCGA")

    # Step 3 — depth correlations (discovery)
    corr_t = depth_correlations(
        expr_t, depth_t,
        tumour_mask_t, "TCGA")

    # Step 4 — gap tests
    gap_t = gap_tests(
        expr_t, tumour_mask_t, "TCGA")

    # Save depth scores
    pd.DataFrame({
        "sample_id":   depth_t.index,
        "depth_score": depth_t.values,
    }).to_csv(
        os.path.join(RESULTS_DIR,
                     "depth_scores_tcga.csv"),
        index=False)

    # ── GEO arm ─────────────────────────────
    depth_g = None
    corr_g  = None

    if probe_map is not None:
        log("")
        log("═" * 60)
        log("VALIDATION — GSE53757")
        log("═" * 60)

        expr_g, meta_g = parse_geo(probe_map)

        if expr_g is not None:
            meta_idx_g = (
                meta_g.set_index("sample_id")
                .reindex(expr_g.columns))
            tumour_mask_g = (
                meta_idx_g.sample_type
                == "tumour").values

            saddle_g = saddle_analysis(
                expr_g, tumour_mask_g,
                meta_g, "GEO")

            depth_g = build_depth_score(
                expr_g, tumour_mask_g,
                saddle_g, "GEO")

            corr_g = depth_correlations(
                expr_g, depth_g,
                tumour_mask_g, "GEO")

            gap_g = gap_tests(
                expr_g, tumour_mask_g, "GEO")

            pd.DataFrame({
                "sample_id":   depth_g.index,
                "depth_score": depth_g.values,
            }).to_csv(
                os.path.join(
                    RESULTS_DIR,
                    "depth_scores_geo.csv"),
                index=False)

    # Figure
    generate_figure(
        depth_t, depth_g,
        corr_t, corr_g,
        saddle_t, expr_t,
        tumour_mask_t)

    # Summary
    log("")
    log("=" * 60)
    log("SCRIPT 1 v3 COMPLETE")
    log("=" * 60)
    log(f"  Outputs: {RESULTS_DIR}")
    for fname in sorted(
            os.listdir(RESULTS_DIR)):
        fpath = os.path.join(
            RESULTS_DIR, fname)
        log(f"    {fname:<55} "
            f"{os.path.getsize(fpath):>8} bytes")
    log("")
    log("  NEXT: Read saddle predictions.")
    log("  How many SW genes confirmed DOWN?")
    log("  How many FA genes confirmed UP?")
    log("  Any wrong predictions reveal")
    log("  assumption errors — read them.")
    log("  Then read depth_corr_tcga.csv.")
    log("  What is rank 1 positive?")
    log("  What is rank 1 negative?")
    log("  What was not predicted?")
    log("  That is the ccRCC attractor geometry.")

    write_log()

if __name__ == "__main__":
    main()
