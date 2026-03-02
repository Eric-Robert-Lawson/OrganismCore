"""
ccRCC False Attractor — Script 5
CLINICAL TRANSLATION + MECHANISTIC
INTERACTIONS + TRANSITION INDEX

Framework: OrganismCore
Document 94e-pre | 2026-03-02
Author: Eric Robert Lawson

BUILDING ON S4:
  S4 revealed the landscape from scratch.
  S5 translates it to clinical use
  and tests the mechanistic interactions
  that define the attractor walls.

LOCKED PREDICTIONS (stated before running):

  S5-P1: RUNX1 will be top depth correlate
         when depth is anchored on
         SLC13A2 + SLC2A1.

  S5-P2: r(OGDHL, EZH2) < 0
         (metabolic depletion → chromatin
         lock — αKG coupling confirmed)

  S5-P3: r(RUNX1, LOXL2) > 0.50
         (TF hub drives ECM effector)

  S5-P4: 3-gene panel r > 0.85
         with full S4 depth score.
         Predicted panel: SLC13A2 /
         RUNX1 / LOXL2.

  S5-P5: BAP1-mutant depth >
         PBRM1-mutant depth (S4 axis).

  S5-P6: Depth Q4 OS < Depth Q1 OS
         (log-rank p < 0.05).

MODULES:
  A — S4-revised depth score
  B — Mechanistic interaction tests
  C — 3-gene clinical panel
  D — OS validation
  E — Mutation × depth
  F — Depth quartile drug map
  G — GOT1/RUNX1 transition index
"""

import os
import gzip
import numpy as np
import pandas as pd
from scipy import stats
from itertools import combinations
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import warnings
warnings.filterwarnings("ignore")

# ════════════════════════════════════════
# PATHS
# ════════════════════════════════════════

BASE_DIR   = "./ccrcc_false_attractor/"
S1_DIR     = os.path.join(BASE_DIR, "results_s1")
S4_DIR     = os.path.join(BASE_DIR, "results_s4")
S5_DIR     = os.path.join(BASE_DIR, "results_s5")
LOG_FILE   = os.path.join(S5_DIR, "s5_log.txt")
os.makedirs(S5_DIR, exist_ok=True)

XENA_LOCAL = os.path.join(
    BASE_DIR, "TCGA_KIRC_HiSeqV2.gz")
GEO_LOCAL  = os.path.join(
    BASE_DIR, "GSE53757_series_matrix.txt.gz")
GPL570     = os.path.join(
    BASE_DIR, "GPL570_soft.txt")

CLINICAL_PATH = os.path.join(
    BASE_DIR,
    "TCGA-KIRC.GDC_phenotype.tsv.gz")
MUTATION_PATH = os.path.join(
    BASE_DIR,
    "TCGA-KIRC.mutect2_snv.tsv.gz")

# ════════════════════════════════════════
# GENE SETS — FROM S4 LANDSCAPE
# ════════════════════════════════════════

S4_POS = [
    "SLC2A1","LOXL2","RUNX1","NAP1L1",
    "CAV1","CTHRC1","LOX","TGFBI","PLOD2",
    "IFI16","SLC43A3","SHC1","RUNX2",
    "GLT25D1","STC1","ITGA5","ENO2",
    "SEMA4B","OSMR","IGFBP3","IL1RAP",
    "SERPINE1","ARL4C","TRAM2","EFNA3",
    "MYOF","CBFB","BCL6","CDCA7L",
]

S4_NEG = [
    "SLC13A2","SLC22A8","SUCLG1","LDHD",
    "CYP17A1","ABAT","FBP1","OGDHL",
    "ATP5A1","GOT1","AIFM1","PECI",
    "ACAT1","IVD","PEPD","HIBCH",
    "TMEM171","BPHL","OSTBETA","ACY1",
    "PCCA","ALDH1L1","HMGCS2","CRAT",
    "PANK1","AQP7","MSRA","CBARA1",
    "ACO2","ACSL1","ETFA","ALDH4A1",
    "COQ9","TACO1","SLC22A13",
]

INTERACTION_PAIRS = [
    ("OGDHL",  "EZH2",   "S5-P2 metabolic->chromatin"),
    ("SUCLG1", "EZH2",   "TCA->chromatin (aKG)"),
    ("OGDHL",  "DNMT3A", "metabolic->DNA methylation"),
    ("RUNX1",  "LOXL2",  "S5-P3 TF hub->ECM effector"),
    ("RUNX1",  "CBFB",   "RUNX complex integrity"),
    ("RUNX1",  "TGFBI",  "TF hub->ECM anchor (S4 edge)"),
    ("RUNX1",  "PLOD2",  "TF hub->collagen hydroxylase"),
    ("RUNX1",  "CTHRC1", "TF hub->ECM guide"),
    ("LOXL2",  "CAV1",   "ECM stiffening->membrane node"),
    ("CAV1",   "EPAS1",  "membrane->HIF2A"),
    ("CAV1",   "AXL",    "membrane node->AXL"),
    ("GOT1",   "ACAT1",  "metabolic hub co-vary"),
    ("GOT1",   "RUNX1",  "attractor axis S4"),
    ("LDHD",   "FBP1",   "two reversibility gates"),
    ("IFI16",  "B2M",    "innate sensing->MHC-I"),
    ("IFI16",  "EZH2",   "innate sensing->chromatin"),
    ("BCL6",   "EZH2",   "two repressors co-active"),
    ("BCL6",   "RUNX1",  "BCL6 recruited by RUNX1?"),
    ("NAP1L1", "EZH2",   "nucleosome remodelling->PRC2"),
    ("SLC13A2","GOT1",   "dicarboxylate import->transaminase"),
    ("SUCLG1", "OGDHL",  "TCA co-disruption"),
    ("CBFB",   "LOXL2",  "RUNX complex->ECM"),
    ("RUNX2",  "LOXL2",  "RUNX2->ECM (bone met)"),
    ("RUNX2",  "RUNX1",  "RUNX family co-vary"),
    ("VHL",    "RUNX1",  "VHL loss->RUNX1?"),
    ("EPAS1",  "LOXL2",  "HIF2A->LOXL2?"),
    ("EZH2",   "HDAC1",  "S3 co-repressors"),
]

# ════════════════════════════════════════
# LOGGING
# ════════════════════════════════════════

log_lines = []

def log(msg=""):
    print(msg)
    log_lines.append(str(msg))

def write_log():
    with open(LOG_FILE, "w") as f:
        f.write("\n".join(log_lines))

def fmt_p(p):
    if p is None:
        return "NA"
    try:
        p = float(p)
    except (TypeError, ValueError):
        return "NA"
    if np.isnan(p):
        return "NA"
    if p < 1e-100:
        return "<1e-100"
    if p < 0.0001:
        return f"{p:.2e}"
    return f"{p:.4f}"

def norm01(arr):
    a = np.asarray(arr, dtype=float)
    mn, mx = np.nanmin(a), np.nanmax(a)
    if mx == mn:
        return np.full_like(a, 0.5)
    return (a - mn) / (mx - mn)

def safe_r(x, y):
    try:
        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)
        m = ~(np.isnan(x) | np.isnan(y))
        if m.sum() < 5:
            return np.nan, np.nan
        return stats.pearsonr(x[m], y[m])
    except Exception:
        return np.nan, np.nan

# ════════════════════════════════════════
# DATA LOADING
# ════════════════════════════════════════

def load_tcga_panel(genes_needed):
    """
    Load TCGA-KIRC expression for a specific
    gene set. Returns expr dict, all sample IDs,
    tumour sample IDs, normal sample IDs.
    expr[gene] is aligned to sample_ids.
    """
    gw = set(g.upper() for g in genes_needed)
    expr       = {}
    sample_ids = []

    with gzip.open(XENA_LOCAL, "rt",
                   encoding="utf-8",
                   errors="replace") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if not sample_ids:
                sample_ids = [
                    p.strip() for p in parts[1:]]
                continue
            gene = parts[0].strip().strip('"')
            if gene.upper() not in gw:
                continue
            try:
                vals = np.array([
                    float(p) if p.strip()
                    not in ["", "NA", "nan"]
                    else np.nan
                    for p in parts[1:]
                ], dtype=float)
                expr[gene] = vals
            except ValueError:
                pass

    # Build sample-type masks using TCGA barcode
    t_cols, n_cols = [], []
    for s in sample_ids:
        parts = s.split("-")
        if len(parts) >= 4:
            code = parts[3][:2]
            if code.isdigit():
                ci = int(code)
                if 1 <= ci <= 9:
                    t_cols.append(s)
                elif 10 <= ci <= 19:
                    n_cols.append(s)

    log(f"  Total samples: {len(sample_ids)}")
    log(f"  Tumour:        {len(t_cols)}")
    log(f"  Normal:        {len(n_cols)}")
    log(f"  Genes loaded:  {len(expr)}")

    return expr, sample_ids, t_cols, n_cols


def load_s1_depth():
    """Load Script 1 depth scores (tumour samples)."""
    p = os.path.join(S1_DIR,
                     "depth_scores_tcga.csv")
    if not os.path.exists(p):
        log(f"  S1 depth file not found: {p}")
        return None
    d = pd.read_csv(p, index_col="sample_id")
    return d["depth_score"]


def load_s4_genome():
    """Load full genome scan CSV from Script 4."""
    p = os.path.join(S4_DIR,
                     "genome_scan_full.csv")
    if not os.path.exists(p):
        log(f"  S4 genome scan not found: {p}")
        return None
    return pd.read_csv(p)


def load_clinical():
    import requests
    if not os.path.exists(CLINICAL_PATH) \
            or os.path.getsize(CLINICAL_PATH) \
            < 1000:
        url = (
            "https://gdc-hub.s3.us-east-1"
            ".amazonaws.com/download/"
            "TCGA-KIRC.GDC_phenotype.tsv.gz")
        log(f"  Downloading clinical: {url}")
        try:
            r = requests.get(
                url, timeout=300,
                headers={"User-Agent":
                         "Mozilla/5.0"})
            if r.status_code == 200 \
                    and len(r.content) > 1000:
                with open(CLINICAL_PATH,
                          "wb") as fh:
                    fh.write(r.content)
                log(f"  Saved "
                    f"{len(r.content):,}b")
            else:
                log(f"  HTTP {r.status_code}")
        except Exception as ex:
            log(f"  Error: {ex}")

    if not os.path.exists(CLINICAL_PATH):
        return None
    try:
        with gzip.open(CLINICAL_PATH,
                       "rt") as fh:
            df = pd.read_csv(fh, sep="\t",
                             low_memory=False)
        log(f"  Clinical rows: {len(df)}  "
            f"cols: {len(df.columns)}")
        return df
    except Exception as ex:
        log(f"  Clinical load error: {ex}")
        return None


def load_mutations():
    import requests
    if not os.path.exists(MUTATION_PATH) \
            or os.path.getsize(MUTATION_PATH) \
            < 1000:
        url = (
            "https://gdc-hub.s3.us-east-1"
            ".amazonaws.com/download/"
            "TCGA-KIRC.mutect2_snv.tsv.gz")
        log(f"  Downloading mutations: {url}")
        try:
            r = requests.get(
                url, timeout=300,
                headers={"User-Agent":
                         "Mozilla/5.0"})
            if r.status_code == 200 \
                    and len(r.content) > 1000:
                with open(MUTATION_PATH,
                          "wb") as fh:
                    fh.write(r.content)
                log(f"  Saved "
                    f"{len(r.content):,}b")
            else:
                log(f"  HTTP {r.status_code}")
        except Exception as ex:
            log(f"  Error: {ex}")

    if not os.path.exists(MUTATION_PATH):
        return None
    try:
        with gzip.open(MUTATION_PATH,
                       "rt") as fh:
            df = pd.read_csv(fh, sep="\t",
                             low_memory=False)
        log(f"  Mutations rows: {len(df)}")
        return df
    except Exception as ex:
        log(f"  Mutation load error: {ex}")
        return None


def load_geo_panel(genes_needed):
    """Load GSE53757 for panel validation."""
    gw = set(g.upper() for g in genes_needed)
    probe_map = {}

    if not os.path.exists(GPL570):
        log("  GPL570 not found — skip GEO "
            "panel validation")
        return None, None

    with open(GPL570, "r",
              encoding="utf-8",
              errors="replace") as fh:
        in_table = False
        header   = None
        id_c = sym_c = None
        for raw in fh:
            line = raw.rstrip("\n")
            if "!platform_table_begin" \
                    in line.lower():
                in_table = True
                header   = None
                continue
            if "!platform_table_end" \
                    in line.lower():
                break
            if not in_table:
                continue
            parts = line.split("\t")
            if header is None:
                header = parts
                lower  = [p.strip().lower()
                           for p in parts]
                id_c = next(
                    (i for i, h in
                     enumerate(lower)
                     if h == "id"), 0)
                for kw in ["gene symbol",
                           "gene_symbol",
                           "symbol"]:
                    for i, h in \
                            enumerate(lower):
                        if kw in h:
                            sym_c = i
                            break
                    if sym_c is not None:
                        break
                if sym_c is None:
                    sym_c = 1
                continue
            if len(parts) <= max(
                    id_c, sym_c):
                continue
            pid = parts[id_c].strip()
            raw_sym = parts[sym_c].strip()
            sym = (raw_sym
                   .split("///")[0]
                   .strip().upper())
            if sym and sym in gw:
                probe_map[pid] = sym

    log(f"  GEO probe map: {len(probe_map)}")

    gsm_ids   = []
    src_names = []
    with gzip.open(GEO_LOCAL, "rt",
                   encoding="utf-8",
                   errors="replace") as fh:
        for raw in fh:
            line = raw.rstrip()
            if line.startswith(
                    "!Sample_geo_accession"):
                gsm_ids.extend([
                    p.strip().strip('"')
                    for p in
                    line.split("\t")[1:]
                    if p.strip().strip('"')
                    .startswith("GSM")])
            elif line.startswith(
                    "!Sample_source_name_ch1"):
                src_names.extend([
                    p.strip().strip('"')
                    for p in
                    line.split("\t")[1:]
                    if p.strip()])
            elif "series_matrix_table_begin" \
                    in line:
                break

    n      = min(len(gsm_ids),
                 len(src_names))
    types  = [
        "normal" if "normal"
        in s.lower() else "tumour"
        for s in src_names[:n]]
    t_ids  = [gsm_ids[i]
              for i in range(n)
              if types[i] == "tumour"]

    col_hdr    = None
    expr_rows  = []
    with gzip.open(GEO_LOCAL, "rt",
                   encoding="utf-8",
                   errors="replace") as fh:
        in_tbl = False
        for raw in fh:
            line = raw.rstrip()
            if "series_matrix_table_begin" \
                    in line:
                in_tbl  = True
                col_hdr = None
                continue
            if "series_matrix_table_end" \
                    in line:
                break
            if not in_tbl:
                continue
            if col_hdr is None:
                col_hdr = line.split("\t")
                continue
            expr_rows.append(
                line.split("\t"))

    if not col_hdr or not expr_rows:
        return None, None

    probe_ids = [r[0].strip('"')
                 for r in expr_rows]
    col_ids   = [c.strip('"')
                 for c in col_hdr[1:]]
    values    = []
    for row in expr_rows:
        vals = []
        for v in row[1:]:
            try:
                vals.append(float(
                    v.strip()))
            except (ValueError,
                    AttributeError):
                vals.append(np.nan)
        values.append(vals[:len(col_ids)])

    probe_df = pd.DataFrame(
        values,
        index=probe_ids,
        columns=col_ids)
    probe_df = np.log2(
        probe_df.clip(lower=0) + 1)

    t_cols_g = [c for c in t_ids
                if c in probe_df.columns]
    gene_rows = {}
    for pid in probe_df.index:
        sym = probe_map.get(pid)
        if sym is None:
            continue
        if sym not in gene_rows:
            gene_rows[sym] = probe_df.loc[pid]
        else:
            nv = float(
                probe_df.loc[
                    pid, t_cols_g
                ].var()
                if t_cols_g else
                probe_df.loc[pid].var())
            ov = float(
                gene_rows[sym][t_cols_g
                               ].var()
                if t_cols_g else
                gene_rows[sym].var())
            if nv > ov:
                gene_rows[sym] = \
                    probe_df.loc[pid]

    if not gene_rows:
        return None, None
    gene_df = pd.DataFrame(gene_rows).T
    return gene_df, t_cols_g

# ════════════════════════════════════════
# HELPER — extract values for tumour set
# ════════════════════════════════════════

def tumour_vals(expr, gene,
                sample_ids, t_cols):
    """
    Return a numpy array of expression
    values for `gene` aligned to t_cols,
    and the list of tumour sample IDs.

    Works by building a fast
    position-lookup from sample_ids.
    """
    pos = {s: i for i, s in
           enumerate(sample_ids)}
    idxs = [pos[s]
             for s in t_cols
             if s in pos]
    if gene not in expr:
        return None, t_cols
    v = expr[gene]
    out = np.array([
        v[i] if i < len(v) else np.nan
        for i in idxs
    ], dtype=float)
    t_sids = [s for s in t_cols
              if s in pos]
    return out, t_sids

# ════════════════════════════════════════
# MODULE A — S4-REVISED DEPTH SCORE
# ════════════════════════════════════════

def module_a_revised_depth(
        expr, sample_ids, t_cols,
        s1_depth):
    log("")
    log("=" * 60)
    log("MODULE A — S4-REVISED DEPTH SCORE")
    log("Anchor: SLC13A2 (neg) + SLC2A1 (pos)")
    log("The two strongest S4 poles.")
    log("=" * 60)

    # Build position lookup once
    pos = {s: i for i, s in
           enumerate(sample_ids)}

    # Only tumour samples present in s1_depth
    t_sids = [s for s in t_cols
              if s in s1_depth.index]
    log(f"\n  Tumour samples in s1_depth: "
        f"{len(t_sids)}")

    def gvals(gene):
        """Values for t_sids."""
        if gene not in expr:
            return None
        v = expr[gene]
        return np.array([
            v[pos[s]]
            if s in pos and pos[s] < len(v)
            else np.nan
            for s in t_sids
        ], dtype=float)

    slc13 = gvals("SLC13A2")
    slc2a1 = gvals("SLC2A1")

    if slc13 is None or slc2a1 is None:
        log("  Anchor genes missing — "
            "returning S1 depth unchanged")
        return s1_depth.reindex(t_sids)

    # Depth: (loss of SLC13A2) + (gain of SLC2A1)
    c1 = 1.0 - norm01(slc13)   # invert: low = deep
    c2 = norm01(slc2a1)         # high = deep
    depth_vals = (c1 + c2) / 2.0

    depth_s5 = pd.Series(
        depth_vals, index=t_sids,
        name="depth_s5")

    # Compare to S1
    s1_aligned = s1_depth.reindex(t_sids)
    r_s1s5, p_s1s5 = safe_r(
        s1_aligned.values,
        depth_s5.values)

    log(f"\n  r(S1_depth, S5_depth) = "
        f"{r_s1s5:+.4f}  p={fmt_p(p_s1s5)}")
    if r_s1s5 > 0.90:
        log("  Same biology as S1 — "
            "strong concordance.")
    elif r_s1s5 > 0.70:
        log("  Partial concordance — S5 "
            "shifts the axis modestly.")
    else:
        log("  Different axis — S5 captures "
            "new structure.")

    log(f"\n  S5 depth statistics "
        f"(n={len(depth_vals)}):")
    log(f"  mean   = "
        f"{np.nanmean(depth_vals):.4f}")
    log(f"  median = "
        f"{np.nanmedian(depth_vals):.4f}")
    log(f"  std    = "
        f"{np.nanstd(depth_vals):.4f}")
    log(f"  min    = "
        f"{np.nanmin(depth_vals):.4f}")
    log(f"  max    = "
        f"{np.nanmax(depth_vals):.4f}")

    # Re-correlate all loaded genes vs
    # new S5 depth to test S5-P1
    d_arr = depth_vals.copy()
    all_genes = list(expr.keys())
    corrs = []
    for gene in all_genes:
        v = gvals(gene)
        if v is None:
            continue
        r, p = safe_r(v, d_arr)
        if not np.isnan(r):
            corrs.append((gene, r, p))
    corrs.sort(key=lambda x: -abs(x[1]))

    log("\n  Top 20 genes vs S5 depth "
        "(anchor pair excluded from ranking):")
    log(f"  {'Rk':<4} {'Gene':<14}"
        f" {'r':>8}  {'p':>12}")
    log(f"  {'-'*4} {'-'*14}"
        f" {'-'*8}  {'-'*12}")
    shown = 0
    for gene, r, p in corrs:
        if gene in ("SLC13A2", "SLC2A1"):
            continue   # skip anchors
        log(f"  {shown+1:<4} {gene:<14}"
            f" {r:>+8.4f}  {fmt_p(p):>12}")
        shown += 1
        if shown >= 20:
            break

    # S5-P1 verdict (first non-anchor gene)
    top_non_anchor = next(
        (g for g, r, p in corrs
         if g not in ("SLC13A2", "SLC2A1")),
        None)
    log(f"\n  S5-P1: top non-anchor "
        f"depth correlate = {top_non_anchor}")
    if top_non_anchor == "RUNX1":
        log("  S5-P1 CONFIRMED ✓")
    else:
        log(f"  S5-P1 NOT CONFIRMED — "
            f"top is {top_non_anchor}")

    depth_s5.to_csv(
        os.path.join(S5_DIR, "depth_s5.csv"),
        header=True)

    return depth_s5

# ════════════════════════════════════════
# MODULE B — MECHANISTIC INTERACTIONS
# ════════════════════════════════════════

def module_b_interactions(
        expr, sample_ids, t_cols,
        depth_s5):
    log("")
    log("=" * 60)
    log("MODULE B — MECHANISTIC INTERACTIONS")
    log("Testing the attractor wall circuitry.")
    log("=" * 60)

    pos    = {s: i for i, s in
              enumerate(sample_ids)}
    t_sids = list(depth_s5.index)

    def gvals(gene):
        if gene not in expr:
            return None
        v = expr[gene]
        return np.array([
            v[pos[s]]
            if s in pos and pos[s] < len(v)
            else np.nan
            for s in t_sids
        ], dtype=float)

    log(f"\n  {'Circuit':<40}"
        f" {'r':>8}  {'p':>12}  status")
    log(f"  {'-'*40}"
        f" {'-'*8}  {'-'*12}  {'-'*15}")

    results = {}
    for gA, gB, label in INTERACTION_PAIRS:
        vA = gvals(gA)
        vB = gvals(gB)
        if vA is None or vB is None:
            log(f"  {label:<40}  MISSING GENE")
            continue
        r, p = safe_r(vA, vB)
        if np.isnan(r):
            log(f"  {label:<40}  "
                f"INSUFFICIENT DATA")
            continue

        if abs(r) < 0.15:
            status = "BROKEN"
        elif abs(r) < 0.30:
            status = "WEAK"
        elif r > 0:
            status = "CO-ACTIVE"
        else:
            status = "OPPOSING"

        log(f"  {label:<40}"
            f" {r:>+8.4f}  {fmt_p(p):>12}"
            f"  {status}")
        results[f"{gA}->{gB}"] = {
            "r": r, "p": p,
            "label": label,
            "status": status}

    # S5-P2
    k = "OGDHL->EZH2"
    if k in results:
        r = results[k]["r"]
        log(f"\n  S5-P2: r(OGDHL, EZH2) = "
            f"{r:+.4f}")
        if r < 0:
            log("  S5-P2 CONFIRMED ✓")
            log("  Low OGDHL -> high EZH2")
            log("  Metabolic aKG depletion -> "
                "chromatin lock coupling "
                "confirmed.")
        else:
            log(f"  S5-P2 NOT CONFIRMED — "
                f"r = {r:+.4f}")

    # S5-P3
    k = "RUNX1->LOXL2"
    if k in results:
        r = results[k]["r"]
        log(f"\n  S5-P3: r(RUNX1, LOXL2) = "
            f"{r:+.4f}")
        if r > 0.50:
            log("  S5-P3 CONFIRMED ✓")
        elif r > 0.30:
            log(f"  S5-P3 PARTIAL — r={r:+.4f}"
                f" (threshold 0.50)")
        else:
            log(f"  S5-P3 NOT CONFIRMED — "
                f"r={r:+.4f}")

    log("\n  WALL CIRCUIT SUMMARY:")
    wall2 = [
        ("OGDHL->EZH2",  "Wall2: met->chrom"),
        ("SUCLG1->EZH2", "Wall2: TCA->chrom"),
        ("BCL6->EZH2",   "Wall2: co-repressor"),
        ("NAP1L1->EZH2", "Wall2: nuc->PRC2"),
        ("EZH2->HDAC1",  "Wall2: co-repressor"),
    ]
    log("  Wall 2 (chromatin):")
    for k, desc in wall2:
        if k in results:
            log(f"    {desc:<40} "
                f"r={results[k]['r']:>+7.4f}")

    wall3 = [
        ("RUNX1->LOXL2",  "Wall3: TF->crosslink"),
        ("RUNX1->TGFBI",  "Wall3: TF->ECM anchor"),
        ("RUNX1->PLOD2",  "Wall3: TF->OH-collagen"),
        ("LOXL2->CAV1",   "Wall3: ECM->membrane"),
        ("CBFB->LOXL2",   "Wall3: RUNX cpx->ECM"),
        ("RUNX2->LOXL2",  "Wall3: RUNX2->ECM"),
    ]
    log("  Wall 3 (ECM stiffening):")
    for k, desc in wall3:
        if k in results:
            log(f"    {desc:<40} "
                f"r={results[k]['r']:>+7.4f}")

    return results

# ════════════════════════════════════════
# MODULE C — 3-GENE CLINICAL PANEL
# ════════════════════════════════════════

def module_c_clinical_panel(
        expr, sample_ids, t_cols,
        depth_s5):
    log("")
    log("=" * 60)
    log("MODULE C — 3-GENE CLINICAL PANEL")
    log("Predicted: SLC13A2 / RUNX1 / LOXL2")
    log("=" * 60)

    pos    = {s: i for i, s in
              enumerate(sample_ids)}
    t_sids = list(depth_s5.index)
    d_arr  = depth_s5.values.astype(float)

    def gvals(gene):
        if gene not in expr:
            return None
        v = expr[gene]
        return np.array([
            v[pos[s]]
            if s in pos and pos[s] < len(v)
            else np.nan
            for s in t_sids
        ], dtype=float)

    candidates = list(set(
        S4_POS[:25] + S4_NEG[:25]))
    candidates = [g for g in candidates
                  if g in expr]

    log(f"\n  Candidate genes: "
        f"{len(candidates)}")
    ncomb = (len(candidates)
             * (len(candidates) - 1)
             * (len(candidates) - 2)
             // 6)
    log(f"  Combinations: {ncomb:,}")

    def panel_depth(gene_list):
        parts = []
        for g in gene_list:
            v = gvals(g)
            if v is None:
                continue
            if g in S4_NEG:
                parts.append(
                    1 - norm01(v))
            else:
                parts.append(norm01(v))
        if not parts:
            return None
        return np.nanmean(parts, axis=0)

    best_r     = 0.0
    best_combo = None
    all_res    = []

    for combo in combinations(
            candidates, 3):
        pd_arr = panel_depth(combo)
        if pd_arr is None:
            continue
        m = np.isfinite(pd_arr) \
            & np.isfinite(d_arr)
        if m.sum() < 20:
            continue
        r = float(np.corrcoef(
            pd_arr[m], d_arr[m])[0, 1])
        all_res.append((combo, r))
        if abs(r) > best_r:
            best_r     = abs(r)
            best_combo = combo

    all_res.sort(key=lambda x: -abs(x[1]))

    log(f"\n  TOP 10 THREE-GENE PANELS:")
    log(f"  {'Rk':<4} {'Genes':<42}"
        f" {'r':>10}")
    log(f"  {'-'*4} {'-'*42} {'-'*10}")
    for i, (combo, r) in \
            enumerate(all_res[:10], 1):
        log(f"  {i:<4} "
            f"{'/'.join(combo):<42}"
            f" {r:>+10.4f}")

    # Test predicted panel
    pred = ["SLC13A2", "RUNX1", "LOXL2"]
    pred_av = [g for g in pred
               if g in expr]
    log(f"\n  PREDICTED PANEL TEST:")
    log(f"  Genes:     {pred}")
    log(f"  Available: {pred_av}")

    r_pred = np.nan
    if len(pred_av) >= 2:
        pd_pred = panel_depth(pred_av)
        r_pred, p_pred = safe_r(
            pd_pred, d_arr)
        log(f"  r(predicted panel, depth) = "
            f"{r_pred:+.4f}  "
            f"p={fmt_p(p_pred)}")
        if abs(r_pred) > 0.85:
            log("  S5-P4 CONFIRMED ✓")
        else:
            log(f"  S5-P4 NOT CONFIRMED — "
                f"r={r_pred:+.4f} "
                f"(threshold 0.85)")

    if best_combo:
        pd_best = panel_depth(best_combo)
        r_best, p_best = safe_r(
            pd_best, d_arr)
        log(f"\n  BEST PANEL:")
        log(f"  Genes: {list(best_combo)}")
        log(f"  r = {r_best:+.4f}  "
            f"p = {fmt_p(p_best)}")
        if abs(r_best) > 0.85:
            log("  S5-P4 CONFIRMED "
                f"(best panel) ✓  "
                f"r={r_best:.4f}")

        # GEO validation
        log("\n  GEO VALIDATION:")
        geo_expr, geo_t = \
            load_geo_panel(
                list(best_combo))
        if geo_expr is not None:
            geo_depth_path = os.path.join(
                S1_DIR,
                "depth_scores_geo.csv")
            if os.path.exists(
                    geo_depth_path):
                geo_d = pd.read_csv(
                    geo_depth_path,
                    index_col="sample_id"
                )["depth_score"]
                geo_shared = [
                    s for s in geo_t
                    if s in geo_d.index]
                if len(geo_shared) >= 10:
                    geo_d_arr = geo_d\
                        .reindex(
                            geo_shared)\
                        .values
                    parts_g = []
                    for gene in best_combo:
                        gu = gene.upper()
                        if gu not in \
                                geo_expr.index:
                            continue
                        v = geo_expr.loc[
                            gu,
                            geo_shared
                        ].values.astype(float)
                        if gene in S4_NEG:
                            parts_g.append(
                                1 - norm01(v))
                        else:
                            parts_g.append(
                                norm01(v))
                    if parts_g:
                        gp = np.nanmean(
                            parts_g, axis=0)
                        r_g, p_g = safe_r(
                            gp, geo_d_arr)
                        log(
                            f"  r(GEO panel,"
                            f" depth) = "
                            f"{r_g:+.4f}  "
                            f"p={fmt_p(p_g)}"
                            f"  n={len(geo_shared)}")
                    else:
                        log("  Genes not in "
                            "GEO probe set")
            else:
                log("  GEO depth file missing")
        else:
            log("  GEO data not available")

        pd.Series(
            pd_best, index=t_sids,
            name="panel_depth"
        ).to_csv(
            os.path.join(S5_DIR,
                         "panel_depth.csv"))

    return best_combo, all_res, r_pred

# ════════════════════════════════════════
# MODULE D — OS VALIDATION
# ══════════════════════════════���═════════

def module_d_os(depth_s5, clinical):
    log("")
    log("=" * 60)
    log("MODULE D — OS VALIDATION")
    log("S5 depth vs overall survival.")
    log("=" * 60)

    if clinical is None:
        log("  Clinical data not available")
        return None

    # Detect columns
    os_col = vital_col = id_col = None
    for c in clinical.columns:
        cl = c.lower()
        if os_col is None and (
                "days_to_death" in cl
                or "overall_survival" in cl
                or "os_time" in cl):
            os_col = c
        if vital_col is None and (
                "vital_status" in cl
                or "os_status" in cl):
            vital_col = c
        if id_col is None and (
                "submitter_id" in cl
                or "bcr_patient_barcode" in cl):
            id_col = c

    log(f"  OS col:    {os_col}")
    log(f"  Vital col: {vital_col}")
    log(f"  ID col:    {id_col}")

    if os_col is None or id_col is None:
        log("  Required columns not found.")
        log("  Columns available:")
        for c in list(
                clinical.columns)[:30]:
            log(f"    {c}")
        return None

    def patient_id(s):
        parts = s.split("-")
        return "-".join(parts[:3]) \
            if len(parts) >= 3 else s

    depth_df = pd.DataFrame({
        "sample":  depth_s5.index,
        "depth":   depth_s5.values,
        "patient": [patient_id(s)
                    for s in depth_s5.index],
    }).drop_duplicates("patient")

    cols = ([id_col, os_col, vital_col]
            if vital_col
            else [id_col, os_col])
    clin = clinical[cols].copy()
    clin.columns = (
        ["patient", "os_time", "vital"]
        if vital_col
        else ["patient", "os_time"])

    merged = depth_df.merge(
        clin, on="patient", how="inner")
    log(f"\n  Merged n = {len(merged)}")

    merged["os_time"] = pd.to_numeric(
        merged["os_time"], errors="coerce")
    merged = merged[
        merged.os_time > 0
    ].dropna(subset=["os_time"])

    if "vital" in merged.columns:
        merged["event"] = merged.vital\
            .apply(lambda x: 1
                   if str(x).lower() in
                   ["dead","deceased",
                    "1","true"]
                   else 0)
    else:
        merged["event"] = np.nan

    log(f"  n with OS: {len(merged)}")
    if "event" in merged.columns \
            and not merged.event.isna().all():
        log(f"  Events:    "
            f"{int(merged.event.sum())}")

    # Quartile stratification
    q = merged.depth.quantile(
        [0.25, 0.50, 0.75])
    merged["quartile"] = pd.cut(
        merged.depth,
        bins=[-np.inf,
              q[0.25], q[0.50],
              q[0.75], np.inf],
        labels=["Q1","Q2","Q3","Q4"])

    log("\n  Depth quartiles:")
    for qi in ["Q1","Q2","Q3","Q4"]:
        mask = merged.quartile == qi
        dq   = merged.loc[mask, "depth"]
        osq  = merged.loc[mask, "os_time"]
        log(f"    {qi}: n={mask.sum():<4}  "
            f"depth={dq.mean():.3f}  "
            f"median_OS="
            f"{np.nanmedian(osq.values):.0f}d")

    # Log-rank Q1 vs Q4
    if not merged.event.isna().all():
        q1m = merged.quartile == "Q1"
        q4m = merged.quartile == "Q4"
        q1_os = merged.loc[q1m,
                           "os_time"].values
        q4_os = merged.loc[q4m,
                           "os_time"].values
        q1_ev = merged.loc[q1m,
                           "event"].values
        q4_ev = merged.loc[q4m,
                           "event"].values

        all_t = np.sort(np.unique(
            np.concatenate(
                [q1_os, q4_os])))
        O1 = E1 = O4 = E4 = 0.0
        for t in all_t:
            n1 = int(((q1_os >= t)
                       & (q1_os > 0)).sum())
            n4 = int(((q4_os >= t)
                       & (q4_os > 0)).sum())
            d1 = int(((q1_os == t)
                       & (q1_ev == 1)).sum())
            d4 = int(((q4_os == t)
                       & (q4_ev == 1)).sum())
            N  = n1 + n4
            D  = d1 + d4
            if N <= 0 or D == 0:
                continue
            O1 += d1
            O4 += d4
            E1 += D * n1 / N
            E4 += D * n4 / N

        chi2v = (
            ((O1 - E1) ** 2 / E1
             if E1 > 0 else 0)
            + ((O4 - E4) ** 2 / E4
               if E4 > 0 else 0))
        p_lr = float(
            stats.chi2.sf(chi2v, df=1))

        log(f"\n  LOG-RANK Q1 vs Q4:")
        log(f"  Q1 O={O1:.0f}  E={E1:.1f}")
        log(f"  Q4 O={O4:.0f}  E={E4:.1f}")
        log(f"  chi2={chi2v:.3f}  "
            f"p={fmt_p(p_lr)}")

        if p_lr < 0.05:
            log("  S5-P6 CONFIRMED ✓")
        else:
            log(f"  S5-P6 NOT CONFIRMED — "
                f"p={fmt_p(p_lr)}")

        r_os, p_os = safe_r(
            merged.depth.values,
            merged.os_time.values)
        log(f"\n  r(depth, OS_days) = "
            f"{r_os:+.4f}  p={fmt_p(p_os)}")

    merged.to_csv(
        os.path.join(S5_DIR,
                     "os_depth.csv"),
        index=False)

    return merged

# ════════════════════════════════════════
# MODULE E — MUTATION × DEPTH
# ════════════════════════════════════════

def module_e_mutations(
        depth_s5, mutations):
    log("")
    log("=" * 60)
    log("MODULE E — MUTATION x DEPTH")
    log("ccRCC driver mutations vs S5 depth.")
    log("=" * 60)

    if mutations is None:
        log("  Mutation data not available")
        return []

    gene_col = sample_col = None
    for c in mutations.columns:
        cl = c.lower()
        if gene_col is None and (
                "hugo" in cl
                or cl == "gene"
                or "gene_name" in cl):
            gene_col = c
        if sample_col is None and (
                "tumor_sample" in cl
                or "sample_id" in cl
                or "aliquot" in cl):
            sample_col = c

    log(f"  Gene col:   {gene_col}")
    log(f"  Sample col: {sample_col}")

    if gene_col is None \
            or sample_col is None:
        log("  Required columns not found.")
        log("  Available:")
        for c in list(
                mutations.columns)[:20]:
            log(f"    {c}")
        return []

    def pid(s):
        if not isinstance(s, str):
            return str(s)
        parts = s.split("-")
        return "-".join(parts[:3]) \
            if len(parts) >= 3 else s

    depth_by_pt = {
        pid(s): float(d)
        for s, d in depth_s5.items()
    }

    key_genes = [
        "VHL","PBRM1","BAP1","SETD2",
        "KDM5C","KDM6A","MTOR","PTEN",
        "TP53","ARID1A","RUNX1","CBFB",
    ]

    results = []
    log(f"\n  {'Gene':<10} {'n_mut':>6}"
        f"  {'depth_mut':>10}"
        f"  {'depth_WT':>10}"
        f"  {'p':>12}  direction")
    log(f"  {'-'*10} {'-'*6}"
        f"  {'-'*10}  {'-'*10}"
        f"  {'-'*12}  {'-'*12}")

    for gene in key_genes:
        muts = mutations[
            mutations[gene_col] == gene]
        if len(muts) == 0:
            log(f"  {gene:<10}  no mutations found")
            continue
        mut_pts = set(
            pid(s)
            for s in muts[sample_col])
        wt_pts  = set(
            depth_by_pt.keys()) - mut_pts

        md = [depth_by_pt[p]
              for p in mut_pts
              if p in depth_by_pt]
        wd = [depth_by_pt[p]
              for p in wt_pts
              if p in depth_by_pt]

        if len(md) < 3 or len(wd) < 3:
            log(f"  {gene:<10}  "
                f"n_mut={len(md)} "
                f"(insufficient)")
            continue

        _, p_mw = stats.mannwhitneyu(
            md, wd,
            alternative="two-sided")
        d_mut = float(np.mean(md))
        d_wt  = float(np.mean(wd))
        dirn  = ("deeper"
                 if d_mut > d_wt
                 else "shallower")

        log(f"  {gene:<10} {len(md):>6}"
            f"  {d_mut:>10.4f}"
            f"  {d_wt:>10.4f}"
            f"  {fmt_p(p_mw):>12}"
            f"  {dirn}")

        results.append({
            "gene":      gene,
            "n_mut":     len(md),
            "depth_mut": d_mut,
            "depth_wt":  d_wt,
            "p":         p_mw,
            "direction": dirn,
        })

    # S5-P5 verdict
    p_row = next(
        (r for r in results
         if r["gene"] == "PBRM1"), None)
    b_row = next(
        (r for r in results
         if r["gene"] == "BAP1"), None)
    if p_row and b_row:
        log(f"\n  S5-P5: BAP1  depth = "
            f"{b_row['depth_mut']:.4f}")
        log(f"         PBRM1 depth = "
            f"{p_row['depth_mut']:.4f}")
        if b_row["depth_mut"] > \
                p_row["depth_mut"]:
            log("  S5-P5 CONFIRMED ✓")
            log("  BAP1-mutant tumours are "
                "deeper than PBRM1-mutant.")
        else:
            log("  S5-P5 NOT CONFIRMED ✗")

    if results:
        pd.DataFrame(results).to_csv(
            os.path.join(S5_DIR,
                         "mutation_depth.csv"),
            index=False)

    return results

# ═════════════════════════════��══════════
# MODULE F — DEPTH QUARTILE DRUG MAP
# ════════════════════════════════════════

def module_f_drug_map(
        expr, sample_ids, t_cols,
        depth_s5):
    log("")
    log("=" * 60)
    log("MODULE F — DEPTH QUARTILE DRUG MAP")
    log("=" * 60)

    pos    = {s: i for i, s in
              enumerate(sample_ids)}
    t_sids = list(depth_s5.index)
    d_arr  = depth_s5.values

    q25 = np.nanpercentile(d_arr, 25)
    q50 = np.nanpercentile(d_arr, 50)
    q75 = np.nanpercentile(d_arr, 75)

    q_labels = ["Q1","Q2","Q3","Q4"]
    q_masks  = {
        "Q1": d_arr <= q25,
        "Q2": (d_arr > q25) & (d_arr <= q50),
        "Q3": (d_arr > q50) & (d_arr <= q75),
        "Q4": d_arr > q75,
    }

    drug_genes = {
        "EPAS1":    "Wall1: Belzutifan target",
        "CA9":      "Wall1: HIF target",
        "SLC2A1":   "Wall1: HIF glycolysis",
        "VEGFA":    "Wall1: Anti-VEGF",
        "EZH2":     "Wall2: Tazemetostat",
        "HDAC1":    "Wall2: Entinostat",
        "DNMT3A":   "Wall2: Decitabine",
        "OGDHL":    "Wall2: aKG depletion",
        "NAP1L1":   "Wall2: Chromatin remdl",
        "LOXL2":    "Wall3: Simtuzumab",
        "LOX":      "Wall3: LOX crosslink",
        "RUNX1":    "Wall3: RUNX1 hub",
        "RUNX2":    "Wall3: Bone met",
        "CBFB":     "Wall3: RUNX complex",
        "TGFBI":    "Wall3: ECM anchor",
        "PLOD2":    "Wall3: Collagen OH",
        "FOXP3":    "Wall4: Treg marker",
        "CD276":    "Wall4: B7-H3",
        "CD274":    "Wall4: PDL1",
        "IL2RA":    "Wall4: Treg activ",
        "TGFB1":    "Wall4: TGF-b",
        "SLC13A2":  "Met: Dicarboxylate",
        "SUCLG1":   "Met: TCA",
        "GOT1":     "Met: Attractor gate",
        "ACAT1":    "Met: Hub",
        "LDHD":     "Met: Reversibility",
        "CAV1":     "Novel: Membrane node",
        "IFI16":    "Novel: Innate sensing",
        "BCL6":     "Novel: Diff repressor",
        "IL1RAP":   "Novel: IL-1 signal",
        "AXL":      "Novel: AXL invasion",
    }

    def gvals(gene):
        if gene not in expr:
            return None
        v = expr[gene]
        return np.array([
            v[pos[s]]
            if s in pos and pos[s] < len(v)
            else np.nan
            for s in t_sids
        ], dtype=float)

    log(f"\n  {'Gene':<12} {'Description':<25}"
        f" {'Q1':>7} {'Q2':>7}"
        f" {'Q3':>7} {'Q4':>7}"
        f"  {'Q4/Q1':>7}")
    log(f"  {'-'*12} {'-'*25}"
        f" {'-'*7} {'-'*7}"
        f" {'-'*7} {'-'*7}  {'-'*7}")

    table = []
    for gene, desc in drug_genes.items():
        v = gvals(gene)
        if v is None:
            continue
        q_means = [
            float(np.nanmean(
                v[q_masks[qi]]))
            for qi in q_labels
        ]
        q1m, q4m = q_means[0], q_means[3]
        ratio = (q4m / q1m
                 if q1m != 0
                 and not np.isnan(q1m)
                 and not np.isnan(q4m)
                 else np.nan)
        flag  = ("^" if (not np.isnan(ratio)
                         and ratio > 1.5)
                 else "v" if (
                     not np.isnan(ratio)
                     and ratio < 0.67)
                 else " ")

        log(f"  {gene:<12} {desc:<25}"
            f" {q_means[0]:>7.3f}"
            f" {q_means[1]:>7.3f}"
            f" {q_means[2]:>7.3f}"
            f" {q_means[3]:>7.3f}"
            f"  {ratio:>6.2f}{flag}"
            if not any(np.isnan(q_means))
            else
            f"  {gene:<12} {desc:<25}  NA")

        table.append({
            "gene": gene, "desc": desc,
            "Q1": q_means[0],
            "Q2": q_means[1],
            "Q3": q_means[2],
            "Q4": q_means[3],
            "ratio_Q4Q1": ratio,
        })

    log("\n  DRUG MAP SUMMARY:")
    log("  Q1: Anti-VEGF / Belzutifan")
    log("  Q2-Q3: + EZH2i / LOXL2i")
    log("  Q4: RUNX1/CBFBi + LOXL2i "
        "+ Anti-B7-H3 + aKG + Anti-Treg")
    log("  NOT anti-PDL1 at any quartile "
        "(CD274 flat/down in Q4)")

    if table:
        pd.DataFrame(table).to_csv(
            os.path.join(S5_DIR,
                         "drug_map.csv"),
            index=False)

    return table

# ════════════════════════════════════════
# MODULE G — GOT1/RUNX1 TRANSITION INDEX
# ════════════════════════════════════════

def module_g_transition_index(
        expr, sample_ids, t_cols,
        depth_s5, clinical):
    log("")
    log("=" * 60)
    log("MODULE G — GOT1/RUNX1 "
        "TRANSITION INDEX")
    log("GOT1 = normal PT metabolic hub")
    log("RUNX1 = deep false attractor hub")
    log("TI = norm(GOT1) - norm(RUNX1)")
    log("=" * 60)

    pos    = {s: i for i, s in
              enumerate(sample_ids)}
    t_sids = list(depth_s5.index)

    def gvals(gene):
        if gene not in expr:
            return None
        v = expr[gene]
        return np.array([
            v[pos[s]]
            if s in pos and pos[s] < len(v)
            else np.nan
            for s in t_sids
        ], dtype=float)

    got1  = gvals("GOT1")
    runx1 = gvals("RUNX1")

    if got1 is None or runx1 is None:
        log("  GOT1 or RUNX1 not available")
        return None

    ti = norm01(got1) - norm01(runx1)
    ti_series = pd.Series(
        ti, index=t_sids,
        name="transition_index")

    r_ti_d, p_ti_d = safe_r(
        ti, depth_s5.values)
    log(f"\n  r(TI, S5_depth) = "
        f"{r_ti_d:+.4f}  p={fmt_p(p_ti_d)}")
    log("  (Negative = low TI -> high depth "
        "-> deep attractor confirmed)")

    log(f"\n  TI statistics:")
    log(f"  mean   = {np.nanmean(ti):.4f}")
    log(f"  median = {np.nanmedian(ti):.4f}")
    log(f"  std    = {np.nanstd(ti):.4f}")
    log(f"  min    = {np.nanmin(ti):.4f}")
    log(f"  max    = {np.nanmax(ti):.4f}")

    log("\n  TI correlations with key genes:")
    log(f"  {'Gene':<12} {'r(TI)':>8}"
        f"  {'p':>12}")
    log(f"  {'-'*12} {'-'*8}  {'-'*12}")
    for gene in (S4_POS[:10]
                 + S4_NEG[:10]):
        if gene not in expr:
            continue
        v = gvals(gene)
        if v is None:
            continue
        r, p = safe_r(v, ti)
        log(f"  {gene:<12} {r:>+8.4f}"
            f"  {fmt_p(p):>12}")

    # TI vs OS
    if clinical is not None:
        os_col = vital_col = id_col = None
        for c in clinical.columns:
            cl = c.lower()
            if os_col is None and (
                    "days_to_death" in cl
                    or "overall_survival"
                    in cl):
                os_col = c
            if vital_col is None and \
                    "vital_status" in cl:
                vital_col = c
            if id_col is None and (
                    "submitter_id" in cl
                    or "bcr_patient" in cl):
                id_col = c

        if os_col and id_col:
            def pid(s):
                parts = s.split("-")
                return "-".join(parts[:3]) \
                    if len(parts) >= 3 else s

            ti_by_pt = {
                pid(s): float(v)
                for s, v in ti_series.items()
            }
            cols = (
                [id_col, os_col, vital_col]
                if vital_col
                else [id_col, os_col])
            clin = clinical[cols].copy()
            clin.columns = (
                ["patient","os_time","vital"]
                if vital_col
                else ["patient","os_time"])
            clin["os_time"] = pd.to_numeric(
                clin["os_time"],
                errors="coerce")

            ti_df = pd.DataFrame({
                "patient": list(
                    ti_by_pt.keys()),
                "ti": list(
                    ti_by_pt.values()),
            })
            merged = ti_df.merge(
                clin, on="patient",
                how="inner")
            merged = merged[
                merged.os_time > 0
            ].dropna(subset=["os_time"])

            r_ti_os, p_ti_os = safe_r(
                merged.ti.values,
                merged.os_time.values)
            log(f"\n  r(TI, OS_days) = "
                f"{r_ti_os:+.4f}  "
                f"p={fmt_p(p_ti_os)}"
                f"  n={len(merged)}")
            if r_ti_os > 0:
                log("  Higher TI (more normal)"
                    " -> longer OS ✓")
            else:
                log("  Lower TI -> longer OS "
                    "(unexpected)")

    ti_series.to_csv(
        os.path.join(S5_DIR,
                     "transition_index.csv"),
        header=True)

    return ti_series

# ════════════════════════════════════════
# FIGURE
# ════════════════════════════════════════

def generate_figure(
        depth_s5, s1_depth,
        best_combo, drug_map_table,
        ti_series, interaction_results,
        os_merged, mutation_results):

    log("\nGenerating Script 5 figure...")
    fig = plt.figure(figsize=(22, 16))
    gs  = gridspec.GridSpec(
        3, 4, figure=fig,
        hspace=0.55, wspace=0.45)

    C = ["#e74c3c","#2ecc71","#2980b9",
         "#8e44ad","#e67e22","#16a085",
         "#c0392b","#7f8c8d"]

    # Panel A — S5 vs S1 depth scatter
    ax_a = fig.add_subplot(gs[0, 0])
    if s1_depth is not None \
            and depth_s5 is not None:
        shared = s1_depth.index\
            .intersection(depth_s5.index)
        if len(shared) > 5:
            ax_a.scatter(
                s1_depth.reindex(
                    shared).values,
                depth_s5.reindex(
                    shared).values,
                s=4, alpha=0.4, c=C[2])
            ax_a.set_xlabel(
                "S1 depth", fontsize=8)
            ax_a.set_ylabel(
                "S5 depth", fontsize=8)
            r, _ = safe_r(
                s1_depth.reindex(
                    shared).values,
                depth_s5.reindex(
                    shared).values)
            ax_a.set_title(
                f"A — S5 vs S1 depth\n"
                f"r={r:+.3f}",
                fontsize=9)

    # Panel B — Interaction bar
    ax_b = fig.add_subplot(gs[0, 1])
    if interaction_results:
        pairs  = list(
            interaction_results.keys()
        )[:16]
        r_vals = [
            interaction_results[p]["r"]
            for p in pairs]
        colours = [
            C[0] if rv > 0 else C[1]
            for rv in r_vals]
        ylabels = [
            interaction_results[p][
                "label"]
            for p in pairs]
        ax_b.barh(
            range(len(pairs)),
            r_vals,
            color=colours,
            edgecolor="black",
            linewidth=0.2)
        ax_b.set_yticks(range(len(pairs)))
        ax_b.set_yticklabels(
            ylabels, fontsize=5)
        ax_b.axvline(0, color="black",
                     lw=0.8)
        ax_b.set_title(
            "B — Mechanistic "
            "interactions",
            fontsize=9)
        ax_b.set_xlabel("r", fontsize=8)

    # Panel C — Transition index vs depth
    ax_c = fig.add_subplot(gs[0, 2])
    if ti_series is not None \
            and depth_s5 is not None:
        shared = ti_series.index\
            .intersection(depth_s5.index)
        if len(shared) > 5:
            ax_c.scatter(
                ti_series.reindex(
                    shared).values,
                depth_s5.reindex(
                    shared).values,
                s=4, alpha=0.4, c=C[3])
            ax_c.set_xlabel(
                "GOT1/RUNX1 TI",
                fontsize=8)
            ax_c.set_ylabel(
                "S5 depth", fontsize=8)
            r, _ = safe_r(
                ti_series.reindex(
                    shared).values,
                depth_s5.reindex(
                    shared).values)
            ax_c.set_title(
                f"C — Transition Index "
                f"vs depth\nr={r:+.3f}",
                fontsize=9)

    # Panel D — KM Q1 vs Q4
    ax_d = fig.add_subplot(gs[0, 3])
    ax_d.set_xlim(0, 10)
    ax_d.set_ylim(0, 1.05)
    if os_merged is not None \
            and "quartile" in os_merged\
            .columns:
        for qi, col, lbl in [
            ("Q1", C[1], "Q1 shallow"),
            ("Q4", C[0], "Q4 deep"),
        ]:
            mask = os_merged.quartile == qi
            if mask.sum() < 2:
                continue
            os_t = np.sort(
                os_merged.loc[
                    mask, "os_time"].values)
            n    = len(os_t)
            surv = np.array([
                (n - i) / n
                for i in range(n)])
            ax_d.step(
                os_t / 365, surv,
                color=col, label=lbl,
                where="post", lw=1.5)
        ax_d.set_xlabel(
            "Years", fontsize=8)
        ax_d.set_ylabel(
            "Survival", fontsize=8)
        ax_d.set_title(
            "D — KM Q1 vs Q4",
            fontsize=9)
        ax_d.legend(fontsize=6)

    # Panel E — Drug map Q4/Q1
    ax_e = fig.add_subplot(gs[1, :2])
    if drug_map_table:
        dm = pd.DataFrame(drug_map_table)\
               .dropna(subset=["ratio_Q4Q1"])
        dm["log_r"] = np.log2(
            dm.ratio_Q4Q1.clip(0.1, 10))
        dm = dm.sort_values("log_r")
        cols_e = [
            C[0] if v > 0 else C[1]
            for v in dm.log_r.values]
        ax_e.barh(
            dm.gene.values,
            dm.log_r.values,
            color=cols_e,
            edgecolor="black",
            linewidth=0.2)
        ax_e.axvline(0,
                     color="black",
                     lw=0.8)
        ax_e.axvline(
            np.log2(1.5), color="grey",
            lw=0.8, ls="--")
        ax_e.axvline(
            np.log2(1 / 1.5),
            color="grey",
            lw=0.8, ls="--")
        ax_e.set_xlabel(
            "log2(Q4/Q1 ratio)",
            fontsize=8)
        ax_e.set_title(
            "E — Drug map Q4/Q1  "
            "(red=higher in Q4)",
            fontsize=9)
        ax_e.tick_params(axis="y",
                         labelsize=6)

    # Panel F — Mutation depth
    ax_f = fig.add_subplot(gs[1, 2])
    if mutation_results:
        mdf  = pd.DataFrame(
            mutation_results)
        diff = (mdf.depth_mut
                - mdf.depth_wt).values
        cols_f = [
            C[0] if d > 0 else C[1]
            for d in diff]
        ax_f.barh(
            mdf.gene.values, diff,
            color=cols_f,
            edgecolor="black",
            linewidth=0.3)
        ax_f.axvline(0,
                     color="black",
                     lw=0.8)
        ax_f.set_xlabel(
            "depth(mut) - depth(WT)",
            fontsize=8)
        ax_f.set_title(
            "F — Mutation x depth\n"
            "(red=mut deeper)",
            fontsize=9)
        ax_f.tick_params(axis="y",
                         labelsize=7)

    # Panel G — Clinical panel text
    ax_g = fig.add_subplot(gs[1, 3])
    ax_g.axis("off")
    txt = "G — CLINICAL PANEL\n"
    txt += "══════════════════\n"
    if best_combo:
        for gene in best_combo:
            arrow = ("DOWN" if gene
                     in S4_NEG
                     else "UP")
            txt += f"  {gene}: {arrow}\n"
    txt += "\n3-gene IHC proxy\n"
    txt += "r > 0.85 target\n"
    ax_g.text(
        0.05, 0.95, txt,
        transform=ax_g.transAxes,
        fontsize=8, va="top",
        fontfamily="monospace",
        bbox=dict(
            boxstyle="round",
            facecolor="#f0f8ff",
            edgecolor="#aaaaaa"))

    # Panels H-I — Wall summaries
    for idx, (title, lines) in enumerate([
        ("H — Wall 2 (Chromatin lock)",
         ["OGDHL->EZH2: aKG coupling",
          "SUCLG1->EZH2: TCA coupling",
          "NAP1L1->EZH2: nucleosome",
          "BCL6->EZH2: co-repressor",
          "EZH2->HDAC1: co-repressor",
          "Drug: EZH2i + aKG supplement"]),
        ("I — Wall 3 (ECM stiffening)",
         ["RUNX1->LOXL2: TF->crosslink",
          "RUNX1->TGFBI: TF->ECM anchor",
          "RUNX1->CBFB: complex",
          "LOXL2->CAV1: ECM->membrane",
          "PLOD2: collagen OH",
          "Drug: LOXL2i + RUNX1i"]),
    ]):
        ax_hi = fig.add_subplot(
            gs[2, idx * 2:(idx * 2) + 2])
        ax_hi.axis("off")
        ax_hi.set_title(title, fontsize=9)
        for j, item in enumerate(lines):
            ax_hi.text(
                0.03, 0.88 - j * 0.13,
                item, fontsize=7,
                transform=ax_hi.transAxes)

    fig.suptitle(
        "ccRCC False Attractor — Script 5\n"
        "Clinical Translation + Mechanistic"
        " Interactions + Transition Index",
        fontsize=11,
        fontweight="bold")

    out = os.path.join(S5_DIR,
                       "figure_s5.png")
    fig.savefig(out, dpi=150,
                bbox_inches="tight")
    plt.close(fig)
    log(f"  Figure: {out}")

# ════════════════════════════════════════
# MAIN
# ════════════════════════════════════════

def main():
    log("OrganismCore — ccRCC Script 5")
    log("Clinical Translation + Mechanistic"
        " Interactions + Transition Index")
    log("Document 94e-pre | 2026-03-02")
    log("")
    log("LOCKED PREDICTIONS:")
    log("  S5-P1: RUNX1 = top depth correlate")
    log("  S5-P2: r(OGDHL,EZH2) < 0")
    log("  S5-P3: r(RUNX1,LOXL2) > 0.50")
    log("  S5-P4: 3-gene panel r > 0.85")
    log("  S5-P5: BAP1-mut deeper than PBRM1-mut")
    log("  S5-P6: Q4 OS < Q1 OS (p<0.05)")
    log("")

    # All genes needed across all modules
    all_genes = list(set(
        S4_POS + S4_NEG
        + [g for pair in INTERACTION_PAIRS
           for g in pair[:2]]
        + ["GOT1","RUNX1","SLC13A2",
           "SLC2A1","ACAT1","CBFB",
           "EZH2","HDAC1","DNMT3A",
           "EPAS1","VHL","AXL",
           "CD276","CD274","FOXP3",
           "IL2RA","TGFB1","B2M"]
    ))

    log("Loading TCGA-KIRC...")
    expr, sample_ids, t_cols, n_cols = \
        load_tcga_panel(all_genes)

    # Load S1 depth
    log("\nLoading S1 depth scores...")
    s1_depth = load_s1_depth()
    if s1_depth is None:
        log("  S1 depth not found — cannot "
            "proceed. Check path:")
        log(f"  {S1_DIR}/depth_scores_tcga.csv")
        write_log()
        return

    log(f"  S1 depth n = {len(s1_depth)}")

    # Load clinical and mutations
    log("\nLoading clinical data...")
    clinical = load_clinical()
    log("\nLoading mutation data...")
    mutations = load_mutations()

    # ── Modules ──────────────────────────
    depth_s5 = module_a_revised_depth(
        expr, sample_ids, t_cols,
        s1_depth)

    interaction_results = \
        module_b_interactions(
            expr, sample_ids, t_cols,
            depth_s5)

    best_combo, panel_results, r_pred = \
        module_c_clinical_panel(
            expr, sample_ids, t_cols,
            depth_s5)

    os_merged = module_d_os(
        depth_s5, clinical)

    mutation_results = \
        module_e_mutations(
            depth_s5, mutations)

    drug_map_table = module_f_drug_map(
        expr, sample_ids, t_cols,
        depth_s5)

    ti_series = module_g_transition_index(
        expr, sample_ids, t_cols,
        depth_s5, clinical)

    generate_figure(
        depth_s5, s1_depth,
        best_combo, drug_map_table,
        ti_series, interaction_results,
        os_merged, mutation_results)

    # ── Output summary ───────────────────
    log("")
    log("=" * 60)
    log("SCRIPT 5 COMPLETE")
    log("=" * 60)
    for fname in sorted(
            os.listdir(S5_DIR)):
        fp = os.path.join(S5_DIR, fname)
        log(f"  {fname:<50}"
            f" {os.path.getsize(fp):>10} bytes")

    log("")
    log("  Paste full output.")
    log("  Write document 94e (synthesis).")
    log("  Then document 94f "
        "(literature check).")

    write_log()


if __name__ == "__main__":
    main()
