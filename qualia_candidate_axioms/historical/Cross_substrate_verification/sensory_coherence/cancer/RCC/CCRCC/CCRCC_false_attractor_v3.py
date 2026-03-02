"""
ccRCC False Attractor — Script 3
SUB-AXIS / CHROMATIN / EMT / PANEL OPTIMISATION

Framework: OrganismCore
Document 94c-pre | 2026-03-02
Author: Eric Robert Lawson

PREDICTIONS LOCKED BEFORE SCRIPT 3:

S3-P1  r(Depth_A, Depth_B) < 0.80
       PT transport and metabolic axes
       are separable sub-axes

S3-P2  SREBF1 > MYC as driver of SCD
       in the lipid arm
       r(SREBF1,SCD) > r(MYC,SCD)

S3-P3  CDH1 DOWN with depth r < -0.25
       Full EMT confirmed — not partial

S3-P4  BAP1 depth-negative r < -0.20
       Low BAP1 = deeper attractor

S3-P5  PBRM1 depth-positive r > +0.10
       Higher PBRM1 = shallower

S3-P6  4-gene panel with SLC34A1(-)
       reaches r >= 0.85 in TCGA

S3-P7  AXL depth-positive r > +0.25
       explaining cabozantinib geometry

DATASETS:
  TCGA-KIRC  HiSeqV2 — 534T / 72N
  GSE53757   GPL570  — 72T / 72N
"""

import os
import gzip
import itertools
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import warnings
warnings.filterwarnings("ignore")

# ═══════════════════════════════════════════════════════
# PATHS
# ═══════════════════════════════════════════════════════

BASE_DIR  = "./ccrcc_false_attractor/"
S1_DIR    = os.path.join(BASE_DIR, "results_s1")
S2_DIR    = os.path.join(BASE_DIR, "results_s2")
S3_DIR    = os.path.join(BASE_DIR, "results_s3")
LOG_FILE  = os.path.join(S3_DIR, "s3_log.txt")
os.makedirs(S3_DIR, exist_ok=True)

XENA_LOCAL   = os.path.join(
    BASE_DIR, "TCGA_KIRC_HiSeqV2.gz")
GEO_LOCAL    = os.path.join(
    BASE_DIR, "GSE53757_series_matrix.txt.gz")
GPL570_LOCAL = os.path.join(
    BASE_DIR, "GPL570_soft.txt")

# ═══════════════════════════════════════════════════════
# GENE PANELS — S3 EXTENDED
# ═══════════════════════════════════════════════════════

SW_GENES = [
    "UMOD",    "SLC34A1", "SLC13A3",
    "AGXT",    "PCK1",    "SLC22A6",
    "GATM",    "AQP1",    "FBP1",    "G6PC",
]
FA_GENES = [
    "CA9",    "VEGFA",  "EGLN3",
    "SLC2A1", "PDK1",   "LDHA",
    "EPAS1",  "SCD",    "ACLY",   "EZH2",
]

PT_TRANSPORT = [
    "SLC34A1", "SLC22A6", "AQP1",
    "SLC13A3", "SLC22A8",
]
PT_METABOLIC = [
    "FBP1",    "G6PC",    "PCK1",
    "AGXT",    "GATM",    "PCK2",
]

LIPID_PANEL = [
    "SCD",    "ACLY",   "FASN",   "PLIN2",
    "HMGCR",  "SQLE",   "ACACA",  "CPT1A",
    "CPT1B",  "HADHA",  "PPARA",  "PPARG",
    "SREBF1", "SREBF2", "MLXIPL", "MYC",
    "EPAS1",  "HIF1A",  "ARNT",
]

EMT_PANEL = [
    "VIM",    "CDH1",   "CDH2",   "EPCAM",
    "FN1",    "SNAI1",  "SNAI2",  "TWIST1",
    "TWIST2", "ZEB1",   "ZEB2",   "ITGB6",
    "MMP2",   "MMP9",   "MMP14",  "CTNNB1",
    "ESRP1",  "ESRP2",  "CLDN4",  "OCLN",
    "KRT7",   "KRT19",
]

CHROMATIN_PANEL = [
    "VHL",    "PBRM1",  "BAP1",   "SETD2",
    "KDM5C",  "KDM6A",  "KDM1A",  "ARID1A",
    "SMARCA4","SMARCB1","EP300",   "CREBBP",
    "EZH2",   "EZH1",   "SUZ12",  "EED",
    "DNMT3A", "TET2",   "ASXL1",  "BCOR",
    "HDAC1",  "HDAC2",  "RCOR1",  "JARID2",
]

CABO_PANEL = [
    "MET",    "HGF",    "AXL",    "GAS6",
    "MERTK",  "TYRO3",  "ANGPT2", "TEK",
    "KDR",    "FLT1",   "PDGFRA", "PDGFRB",
    "FGF2",   "FGFR1",  "RET",    "NTRK1",
    "VEGFA",  "VEGFC",  "VEGFD",
]

PANEL_CANDIDATES_POS = [
    "SLC2A1", "VIM",    "CA9",    "EGLN3",
    "TGFB1",  "FAP",    "VEGFA",  "COL1A1",
    "MYC",    "LDHA",   "PDK1",   "EZH2",
    "FOXP3",  "SCD",    "TOP2A",
]
PANEL_CANDIDATES_NEG = [
    "FBP1",    "SLC34A1", "SLC22A6", "G6PC",
    "PCK1",    "UMOD",    "SLC13A3", "AQP1",
    "AGXT",    "CPT1A",   "PAX8",    "HNF1A",
    "GATM",    "ALDOB",   "SLC22A8",
]

FULL_S3 = list(dict.fromkeys(
    SW_GENES + FA_GENES +
    PT_TRANSPORT + PT_METABOLIC +
    LIPID_PANEL + EMT_PANEL +
    CHROMATIN_PANEL + CABO_PANEL +
    PANEL_CANDIDATES_POS +
    PANEL_CANDIDATES_NEG + [
        "TGFB1", "FAP", "COL1A1",
        "ACTA2", "FOXP3", "CD68",
        "CD274", "MKI67", "CCND1",
        "MET", "MTOR", "PTEN", "PAX8",
        "LHX1", "HNF1A", "HNF1B",
        "ALDOB", "SLC22A8", "KRT7",
        "KRT19", "POSTN", "WNT5A",
    ]
))

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

# ═══════════════════════════════════════════════════════
# DATA LOADERS
# ═══════════════════════════════════════════════════════

def parse_tcga():
    log("Loading TCGA-KIRC...")
    gw = set(FULL_S3)
    with gzip.open(XENA_LOCAL, "rt") as f:
        raw = pd.read_csv(f, sep="\t",
                          index_col=0)
    avail = [g for g in raw.index
             if g in gw]
    expr  = raw.loc[avail]

    t_cols = []
    for s in expr.columns:
        p = s.split("-")
        if len(p) >= 4:
            code = p[3][:2]
            if (code.isdigit() and
                    1 <= int(code) <= 9):
                t_cols.append(s)
    log(f"  TCGA genes={len(avail)}, "
        f"tumours={len(t_cols)}")
    return expr, t_cols


def _parse_symbol(raw_sym):
    """
    Robustly extract a gene symbol from a
    GPL annotation field that may contain:
      - empty string
      - "---"
      - "GENE1 /// GENE2"
      - "GENE1; GENE2"
      - plain "GENE"
    Returns the first valid token or None.
    """
    if not raw_sym or not raw_sym.strip():
        return None
    # take first entry of "///" list
    first = raw_sym.split("///")[0].strip()
    if not first or first in ("---", "N/A",
                               "NA", "null"):
        return None
    # take first whitespace-delimited token
    # and upper-case it
    tokens = first.split()
    if not tokens:
        return None
    sym = tokens[0].upper()
    if not sym or sym in ("---", "N/A",
                           "NA", "NULL"):
        return None
    return sym


def parse_geo():
    log("Loading GSE53757...")
    if not os.path.exists(GPL570_LOCAL):
        log("  GPL570 not found — skipping GEO")
        return None, None

    gw = set(FULL_S3)

    # ── Build probe → symbol map ─────────
    probe_map = {}
    with open(GPL570_LOCAL, "r",
              encoding="utf-8",
              errors="replace") as fh:
        header    = None
        id_c      = None
        sym_c     = None
        in_table  = False

        for raw_line in fh:
            line = raw_line.rstrip("\n")

            # GPL SOFT markers
            if "!platform_table_begin" \
                    in line.lower():
                in_table = True
                header   = None
                continue
            if "!platform_table_end" \
                    in line.lower():
                break
            # Skip meta lines outside table
            if not in_table:
                continue

            parts = line.split("\t")

            # First non-meta line = header
            if header is None:
                header = parts
                lower  = [p.strip().lower()
                           for p in parts]
                # id column
                id_c = next(
                    (i for i, h in enumerate(lower)
                     if h == "id"), None)
                if id_c is None:
                    id_c = 0
                # symbol column — various names
                sym_c = None
                for kw in [
                    "gene symbol",
                    "gene_symbol",
                    "symbol",
                    "gene assignment",
                    "gene name",
                ]:
                    for i, h in enumerate(lower):
                        if kw in h:
                            sym_c = i
                            break
                    if sym_c is not None:
                        break
                if sym_c is None:
                    sym_c = 1
                continue

            # Data rows
            if len(parts) <= max(id_c, sym_c):
                continue
            pid     = parts[id_c].strip()
            raw_sym = parts[sym_c].strip()
            sym     = _parse_symbol(raw_sym)
            if sym and sym in gw:
                probe_map[pid] = sym

    log(f"  GPL570 probe map: "
        f"{len(probe_map)} probes → panel genes")

    # ── Parse series matrix ───────────────
    sample_ids   = []
    source_names = []
    with gzip.open(GEO_LOCAL, "rt",
                   encoding="utf-8",
                   errors="replace") as fh:
        for raw_line in fh:
            line = raw_line.rstrip()
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
            elif ("series_matrix_table_begin"
                  in line):
                break

    n = min(len(sample_ids),
            len(source_names))
    types = [
        "normal"
        if "normal" in s.lower()
        else "tumour"
        for s in source_names[:n]
    ]
    t_ids = [sample_ids[i]
             for i in range(n)
             if types[i] == "tumour"]

    # Expression table
    col_hdr   = None
    expr_rows = []
    with gzip.open(GEO_LOCAL, "rt",
                   encoding="utf-8",
                   errors="replace") as fh:
        in_tbl = False
        for raw_line in fh:
            line = raw_line.rstrip()
            if ("series_matrix_table_begin"
                    in line):
                in_tbl  = True
                col_hdr = None
                continue
            if ("series_matrix_table_end"
                    in line):
                break
            if not in_tbl:
                continue
            if col_hdr is None:
                col_hdr = line.split("\t")
                continue
            expr_rows.append(
                line.split("\t"))

    if not col_hdr or not expr_rows:
        log("  GEO matrix empty — skipping")
        return None, None

    probe_ids = [r[0].strip('"')
                 for r in expr_rows]
    col_ids   = [c.strip('"')
                 for c in col_hdr[1:]]

    values = []
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
        columns=col_ids,
    )
    # log2 transform (data are raw
    # intensity — clip negatives)
    probe_df = np.log2(
        probe_df.clip(lower=0) + 1)

    t_cols = [c for c in t_ids
              if c in probe_df.columns]

    # Collapse probes → genes
    # keep highest-variance probe
    gene_rows = {}
    for pid in probe_df.index:
        sym = probe_map.get(pid)
        if sym is None:
            continue
        existing = gene_rows.get(sym)
        if existing is None:
            gene_rows[sym] = probe_df.loc[pid]
        else:
            new_var = float(
                probe_df.loc[pid, t_cols].var()
                if t_cols else
                probe_df.loc[pid].var())
            old_var = float(
                existing[t_cols].var()
                if t_cols else
                existing.var())
            if new_var > old_var:
                gene_rows[sym] = probe_df.loc[pid]

    if not gene_rows:
        log("  No panel genes found in GEO — "
            "skipping")
        return None, None

    gene_df = pd.DataFrame(gene_rows).T
    log(f"  GEO genes={len(gene_df)}, "
        f"tumours={len(t_cols)}")
    return gene_df, t_cols


def load_depth(tag):
    p = os.path.join(
        S1_DIR,
        f"depth_scores_{tag}.csv")
    d = pd.read_csv(p, index_col="sample_id")
    return d["depth_score"]

# ═══════════════════════════════════════════════════════
# OBJ-1  PT SUB-AXIS SEPARATION
# ═══════════════════════════════════════════════════════

def pt_subaxis(expr, t_cols, depth, label):
    log("")
    log("=" * 60)
    log(f"OBJ-1 — PT SUB-AXES — {label}")
    log("=" * 60)

    d = depth.reindex(t_cols).dropna()

    def axis_score(genes, name):
        avail = [g for g in genes
                 if g in expr.index]
        if not avail:
            log(f"  {name}: no genes available")
            return None
        mat = pd.DataFrame({
            g: pd.Series(
                expr.loc[g, t_cols].values,
                index=t_cols,
            ).reindex(d.index)
            for g in avail
        })
        score = 1 - norm01(
            mat.mean(axis=1).values)
        r, p = safe_r(score, d.values)
        log(f"  {name}")
        log(f"    genes: {avail}")
        log(f"    r vs depth = {r:+.4f}"
            f"  p = {fmt_p(p)}")
        return pd.Series(score,
                         index=d.index)

    score_a = axis_score(PT_TRANSPORT,
                         "Depth_A (transport)")
    score_b = axis_score(PT_METABOLIC,
                         "Depth_B (metabolic)")

    if score_a is None or score_b is None:
        return None, None, np.nan

    r_ab, p_ab = safe_r(score_a.values,
                        score_b.values)
    log("")
    log(f"  r(Depth_A, Depth_B) = "
        f"{r_ab:+.4f}  p = {fmt_p(p_ab)}")
    if r_ab < 0.80:
        log("  PREDICTION S3-P1 CONFIRMED: "
            "r < 0.80 — axes separable ✓")
    else:
        log("  PREDICTION S3-P1 WRONG: "
            "r >= 0.80 — axes not separable ✗")

    # Cross-axis pairwise
    log("")
    log("  Cross-axis gene correlations "
        "(top 10 by |r|):")
    log(f"  {'Gene A':<12} {'Gene B':<12}"
        f" {'r':>8}  class")
    log(f"  {'-'*12} {'-'*12} {'-'*8}"
        f"  {'-'*15}")
    cross = []
    for ga in PT_TRANSPORT:
        for gb in PT_METABOLIC:
            if (ga not in expr.index or
                    gb not in expr.index):
                continue
            va = pd.Series(
                expr.loc[ga, t_cols].values,
                index=t_cols,
            ).reindex(d.index)
            vb = pd.Series(
                expr.loc[gb, t_cols].values,
                index=t_cols,
            ).reindex(d.index)
            r, _ = safe_r(va.values,
                          vb.values)
            cross.append((ga, gb, r))
    cross.sort(key=lambda x:
               -abs(x[2])
               if not np.isnan(x[2]) else 0)
    for ga, gb, r in cross[:10]:
        cls = (
            "COUPLED"   if abs(r) >= 0.40
            else "WEAK" if abs(r) >= 0.20
            else "DECOUPLED")
        log(f"  {ga:<12} {gb:<12}"
            f" {r:>+8.4f}  {cls}")

    # Save
    out_df = pd.DataFrame({
        "depth_a":    score_a,
        "depth_b":    score_b,
        "depth_full": d,
    })
    out_df.to_csv(os.path.join(
        S3_DIR,
        f"pt_subaxes_{label.lower()}.csv"))
    return score_a, score_b, r_ab

# ═══════════════════════════════════════════════════════
# OBJ-2  LIPID ARM TF DRIVER
# ═══════════════════════════════════════════════════════

def lipid_tf_driver(expr, t_cols, depth,
                    label):
    log("")
    log("=" * 60)
    log(f"OBJ-2 — LIPID ARM DRIVERS — {label}")
    log("=" * 60)

    d = depth.reindex(t_cols).dropna()

    lipid_effectors = [
        "SCD", "ACLY", "FASN", "PLIN2"]
    tfs = [
        "SREBF1", "SREBF2", "MYC",
        "EPAS1",  "HIF1A",  "MLXIPL",
        "PPARA",  "PPARG",
    ]

    hdr = (f"  {'TF':<10}  " +
           "  ".join(f"{e:>8}"
                     for e in lipid_effectors)
           + "  depth_r")
    log(hdr)
    log("  " + "-" * (len(hdr) - 2))

    rows = []
    for tf in tfs:
        if tf not in expr.index:
            continue
        tf_v = pd.Series(
            expr.loc[tf, t_cols].values,
            index=t_cols,
        ).reindex(d.index)
        tf_d_r, _ = safe_r(tf_v.values,
                            d.values)

        eff_rs = []
        for eff in lipid_effectors:
            if eff not in expr.index:
                eff_rs.append(np.nan)
                continue
            eff_v = pd.Series(
                expr.loc[eff, t_cols].values,
                index=t_cols,
            ).reindex(d.index)
            r, _ = safe_r(tf_v.values,
                          eff_v.values)
            eff_rs.append(r)

        line = f"  {tf:<10}  "
        line += "  ".join(
            f"{r:>+8.4f}"
            if not np.isnan(r)
            else f"{'NA':>8}"
            for r in eff_rs)
        line += (f"  {tf_d_r:>+7.4f}"
                 if not np.isnan(tf_d_r)
                 else "  NA")
        log(line)
        rows.append({
            "tf":       tf,
            "depth_r":  tf_d_r,
            **{f"r_{e}": r
               for e, r in zip(
                   lipid_effectors,
                   eff_rs)},
        })

    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(
        S3_DIR,
        f"lipid_tfs_{label.lower()}.csv"),
        index=False)

    if len(df) >= 2 and "r_SCD" in df.columns:
        log("")
        top = df.dropna(
            subset=["r_SCD"]
        ).sort_values(
            "r_SCD", key=abs,
            ascending=False)
        if len(top) >= 1:
            winner = top.iloc[0].tf
            wr     = top.iloc[0].r_SCD
            log(f"  TOP TF for SCD: "
                f"{winner}  r={wr:+.4f}")
            if len(top) >= 2:
                runner = top.iloc[1].tf
                rr     = top.iloc[1].r_SCD
                log(f"  2nd TF for SCD: "
                    f"{runner}  r={rr:+.4f}")
            if winner == "SREBF1":
                log("  S3-P2 CONFIRMED: "
                    "SREBF1 > MYC ✓")
            else:
                log(f"  S3-P2 WRONG: "
                    f"{winner} beats SREBF1 ✗")
    return df

# ═══════════════════════════════════════════════════════
# OBJ-3  FULL EMT CIRCUIT
# ═══════════════════════════════════════════════════════

def emt_circuit(expr, t_cols, depth, label):
    log("")
    log("=" * 60)
    log(f"OBJ-3 — FULL EMT CIRCUIT — {label}")
    log("=" * 60)

    d = depth.reindex(t_cols).dropna()

    rows = []
    for gene in EMT_PANEL:
        if gene not in expr.index:
            continue
        v = pd.Series(
            expr.loc[gene, t_cols].values,
            index=t_cols,
        ).reindex(d.index)
        r, p = safe_r(v.values, d.values)
        if np.isnan(r):
            continue
        direction = (
            "↑ deeper"
            if r > 0
            else "↓ shallower")
        rows.append({
            "gene": gene, "r": r, "p": p})

    df = pd.DataFrame(rows).sort_values(
        "r", key=abs, ascending=False)
    df.to_csv(os.path.join(
        S3_DIR,
        f"emt_{label.lower()}.csv"),
        index=False)

    log(f"  {'Gene':<10} {'r(depth)':>10}"
        f"  {'p':>10}  direction")
    log(f"  {'-'*10} {'-'*10}  "
        f"{'-'*10}  {'-'*20}")
    for _, row in df.iterrows():
        direction = (
            "↑ deeper"
            if row.r > 0
            else "↓ shallower")
        log(f"  {row.gene:<10} "
            f"{row.r:>+10.4f}  "
            f"{fmt_p(row.p):>10}  "
            f"{direction}")

    # S3-P3 verdict
    cdh1_rows = df[df.gene == "CDH1"]
    if len(cdh1_rows) > 0:
        r_cdh1 = float(cdh1_rows.iloc[0].r)
        log("")
        log(f"  S3-P3: CDH1 r = {r_cdh1:+.4f}")
        if r_cdh1 < -0.25:
            log("  CONFIRMED: CDH1 DOWN "
                "with depth ✓")
        elif r_cdh1 < 0:
            log("  PARTIAL: CDH1 trending "
                "negative but > -0.25")
        else:
            log("  WRONG: CDH1 not "
                "down with depth ✗")

    # Circuit pair tests
    circuits = [
        ("SNAI1",  "CDH1",  "negative"),
        ("ZEB1",   "CDH1",  "negative"),
        ("ZEB2",   "CDH1",  "negative"),
        ("TWIST1", "VIM",   "positive"),
        ("SNAI1",  "VIM",   "positive"),
        ("ZEB1",   "VIM",   "positive"),
        ("VIM",    "CDH2",  "positive"),
        ("VIM",    "EPCAM", "negative"),
        ("CTNNB1", "CDH1",  "positive"),
        ("ESRP1",  "CDH1",  "positive"),
    ]
    log("")
    log("  EMT circuit pairs:")
    log(f"  {'Circuit':<20} {'r':>8}  "
        f"{'Status':>12}  V")
    log(f"  {'-'*20} {'-'*8}  "
        f"{'-'*12}  -")
    for ga, gb, exp in circuits:
        if (ga not in expr.index or
                gb not in expr.index):
            continue
        va = pd.Series(
            expr.loc[ga, t_cols].values,
            index=t_cols,
        ).reindex(d.index)
        vb = pd.Series(
            expr.loc[gb, t_cols].values,
            index=t_cols,
        ).reindex(d.index)
        r, _ = safe_r(va.values, vb.values)
        if np.isnan(r):
            continue
        status = (
            "CONNECTED" if abs(r) >= 0.40
            else "WEAK"  if abs(r) >= 0.20
            else "BROKEN")
        ok = ("✓"
              if ((exp == "negative"
                   and r < 0) or
                  (exp == "positive"
                   and r > 0))
              else "✗")
        log(f"  {ga}→{gb:<14} "
            f"{r:>+8.4f}  "
            f"{status:>12}  {ok}")
    return df

# ═══════════════════════════════════════════════════════
# OBJ-4/5  CHROMATIN GENE DEPTH MAP
# ═══════════════════════════════════════════════════════

def chromatin_depth(expr, t_cols, depth,
                    label):
    log("")
    log("=" * 60)
    log(f"OBJ-4/5 — CHROMATIN DEPTH MAP"
        f" — {label}")
    log("=" * 60)
    log("  Predicted DOWN: BAP1, SETD2, "
        "KDM5C, VHL")
    log("  Predicted UP:   EZH2, PBRM1")
    log("")

    d = depth.reindex(t_cols).dropna()

    rows = []
    for gene in CHROMATIN_PANEL:
        if gene not in expr.index:
            continue
        v = pd.Series(
            expr.loc[gene, t_cols].values,
            index=t_cols,
        ).reindex(d.index)
        r, p = safe_r(v.values, d.values)
        if np.isnan(r):
            continue
        rows.append({
            "gene": gene,
            "r":    round(r, 4),
            "p":    p,
        })

    df = pd.DataFrame(rows).sort_values(
        "r", ascending=True)
    df.to_csv(os.path.join(
        S3_DIR,
        f"chromatin_{label.lower()}.csv"),
        index=False)

    preds = {
        "BAP1":   ("negative", "S3-P4"),
        "PBRM1":  ("positive", "S3-P5"),
        "SETD2":  ("negative", None),
        "KDM5C":  ("negative", None),
        "VHL":    ("negative", None),
        "EZH2":   ("positive", None),
        "KDM1A":  ("positive", None),
        "DNMT3A": ("negative", None),
        "HDAC1":  ("positive", None),
        "SUZ12":  ("positive", None),
    }

    log(f"  {'Gene':<12} {'r(depth)':>10}"
        f"  {'p':>10}  pred        result")
    log(f"  {'-'*12} {'-'*10}  "
        f"{'-'*10}  {'-'*12}  {'-'*8}")
    for _, row in df.iterrows():
        gene      = row.gene
        r         = row.r
        pred_dir, pred_id = preds.get(
            gene, (None, None))
        if pred_dir == "negative":
            ok     = "✓" if r < -0.10 else "✗"
            pred_s = "DOWN pred"
        elif pred_dir == "positive":
            ok     = "✓" if r > +0.10 else "✗"
            pred_s = "UP pred"
        else:
            ok     = ""
            pred_s = ""
        pid = pred_id or ""
        log(f"  {gene:<12} {r:>+10.4f}"
            f"  {fmt_p(row.p):>10}"
            f"  {pred_s:<12}  {ok} {pid}")

    # Explicit threshold checks
    for gene, thresh, pred_name, direction \
            in [
        ("BAP1",  -0.20, "S3-P4", "negative"),
        ("PBRM1", +0.10, "S3-P5", "positive"),
    ]:
        sub = df[df.gene == gene]
        if len(sub) == 0:
            log(f"\n  {pred_name}: "
                f"{gene} not in data")
            continue
        r = float(sub.iloc[0].r)
        log("")
        log(f"  {pred_name}: {gene} "
            f"r = {r:+.4f}")
        if (direction == "negative"
                and r < thresh):
            log("    CONFIRMED ✓")
        elif (direction == "positive"
              and r > thresh):
            log("    CONFIRMED ✓")
        else:
            log("    NOT CONFIRMED ✗")

    # Mutation proxy
    log("")
    log("  MUTATION PROXY ANALYSIS:")
    log("  Q1-low expressers vs Q4-high "
        "— are low-Q1 deeper?")
    log("")
    for gene in ["BAP1", "PBRM1",
                 "SETD2", "KDM5C"]:
        if gene not in expr.index:
            continue
        v = pd.Series(
            expr.loc[gene, t_cols].values,
            index=t_cols,
        ).reindex(d.index).dropna()
        q25 = float(np.percentile(v, 25))
        q75 = float(np.percentile(v, 75))
        low_ix  = v[v <= q25].index
        high_ix = v[v >= q75].index
        d_low   = d.reindex(low_ix).dropna()
        d_high  = d.reindex(high_ix).dropna()
        if len(d_low) < 5 or len(d_high) < 5:
            continue
        _, pmwu = stats.mannwhitneyu(
            d_low, d_high,
            alternative="two-sided")
        diff  = float(d_low.mean()
                      - d_high.mean())
        flag  = ("deeper"
                 if diff > 0
                 else "shallower")
        log(f"  {gene:<8}: "
            f"low-Q1 vs high-Q4  "
            f"Δdepth={diff:+.4f}  "
            f"p={fmt_p(pmwu)}  "
            f"low='{flag}'")
    return df

# ═══════════════════════════════════════════════════════
# OBJ-6  PANEL OPTIMISATION
# ══════════════════════════════════════════════��════════

def panel_optimise(expr_t, depth_t,
                   t_cols_t,
                   expr_g, depth_g,
                   t_cols_g):
    log("")
    log("=" * 60)
    log("OBJ-6 — PANEL OPTIMISATION")
    log("Target: r >= 0.85 BOTH datasets")
    log("=" * 60)

    d_t = depth_t.reindex(
        t_cols_t).dropna()
    d_g = (depth_g.reindex(
        t_cols_g).dropna()
           if (expr_g is not None
               and t_cols_g)
           else None)

    def score_panel(pos_genes, neg_genes,
                    expr, d, t_cols):
        avail_p = [g for g in pos_genes
                   if g in expr.index]
        avail_n = [g for g in neg_genes
                   if g in expr.index]
        if not avail_p and not avail_n:
            return np.nan
        s = np.zeros(len(d), dtype=float)
        c = 0
        if avail_p:
            mat = pd.DataFrame({
                g: pd.Series(
                    expr.loc[g, t_cols].values,
                    index=t_cols,
                ).reindex(d.index)
                for g in avail_p
            })
            s += norm01(
                mat.mean(axis=1).values)
            c += 1
        if avail_n:
            mat = pd.DataFrame({
                g: pd.Series(
                    expr.loc[g, t_cols].values,
                    index=t_cols,
                ).reindex(d.index)
                for g in avail_n
            })
            s += (1 - norm01(
                mat.mean(axis=1).values))
            c += 1
        if c > 0:
            s /= c
        r, _ = safe_r(s, d.values)
        return r

    def rmin(rt, rg):
        if np.isnan(rg):
            return rt
        return min(rt, rg)

    # ── 2-gene ───────────────────────────
    log("")
    log("  2-gene panels (1 pos + 1 neg):")
    log(f"  {'Pos':>10} {'Neg':>12}"
        f" {'r_TCGA':>8} {'r_GEO':>8}"
        f" {'r_min':>8}")
    log(f"  {'-'*10} {'-'*12}"
        f" {'-'*8} {'-'*8} {'-'*8}")

    best_2   = {"r_min": 0, "panel": None}
    res2     = []
    for pos in PANEL_CANDIDATES_POS[:10]:
        for neg in PANEL_CANDIDATES_NEG[:10]:
            rt = score_panel(
                [pos], [neg],
                expr_t, d_t, t_cols_t)
            rg = (score_panel(
                [pos], [neg],
                expr_g, d_g, t_cols_g)
                  if d_g is not None
                  else np.nan)
            rm = rmin(rt, rg)
            res2.append({
                "pos": pos, "neg": neg,
                "rt": rt, "rg": rg,
                "rmin": rm,
            })
            if (not np.isnan(rm)
                    and rm > best_2["r_min"]):
                best_2 = {
                    "r_min": rm,
                    "panel": ([pos], [neg]),
                }

    res2.sort(key=lambda x:
              -(x["rmin"]
                if not np.isnan(x["rmin"])
                else 0))
    for row in res2[:12]:
        rgs = (f"{row['rg']:>8.4f}"
               if not np.isnan(row['rg'])
               else f"{'NA':>8}")
        rms = (f"{row['rmin']:>8.4f}"
               if not np.isnan(row['rmin'])
               else f"{'NA':>8}")
        log(f"  {row['pos']:>10}"
            f" {row['neg']:>12}"
            f" {row['rt']:>8.4f}"
            f" {rgs} {rms}")

    # ── 3-gene ───────────────────────────
    log("")
    log("  3-gene panels:")
    log(f"  {'Pos':>18} {'Neg':>14}"
        f" {'r_TCGA':>8} {'r_GEO':>8}"
        f" {'r_min':>8}")
    log(f"  {'-'*18} {'-'*14}"
        f" {'-'*8} {'-'*8} {'-'*8}")

    best_3 = {"r_min": 0, "panel": None}
    res3   = []

    # 2 pos + 1 neg
    for p1, p2 in itertools.combinations(
            PANEL_CANDIDATES_POS[:8], 2):
        for neg in PANEL_CANDIDATES_NEG[:8]:
            rt = score_panel(
                [p1, p2], [neg],
                expr_t, d_t, t_cols_t)
            rg = (score_panel(
                [p1, p2], [neg],
                expr_g, d_g, t_cols_g)
                  if d_g is not None
                  else np.nan)
            rm = rmin(rt, rg)
            res3.append({
                "pos": f"{p1}+{p2}",
                "neg": neg,
                "rt": rt, "rg": rg,
                "rmin": rm,
            })
            if (not np.isnan(rm)
                    and rm > best_3["r_min"]):
                best_3 = {
                    "r_min": rm,
                    "panel": ([p1, p2], [neg]),
                }

    # 1 pos + 2 neg
    for pos in PANEL_CANDIDATES_POS[:8]:
        for n1, n2 in itertools.combinations(
                PANEL_CANDIDATES_NEG[:8], 2):
            rt = score_panel(
                [pos], [n1, n2],
                expr_t, d_t, t_cols_t)
            rg = (score_panel(
                [pos], [n1, n2],
                expr_g, d_g, t_cols_g)
                  if d_g is not None
                  else np.nan)
            rm = rmin(rt, rg)
            res3.append({
                "pos": pos,
                "neg": f"{n1}+{n2}",
                "rt": rt, "rg": rg,
                "rmin": rm,
            })
            if (not np.isnan(rm)
                    and rm > best_3["r_min"]):
                best_3 = {
                    "r_min": rm,
                    "panel": ([pos],
                               [n1, n2]),
                }

    res3.sort(key=lambda x:
              -(x["rmin"]
                if not np.isnan(x["rmin"])
                else 0))
    for row in res3[:15]:
        rgs = (f"{row['rg']:>8.4f}"
               if not np.isnan(row['rg'])
               else f"{'NA':>8}")
        rms = (f"{row['rmin']:>8.4f}"
               if not np.isnan(row['rmin'])
               else f"{'NA':>8}")
        log(f"  {row['pos']:>18}"
            f" {row['neg']:>14}"
            f" {row['rt']:>8.4f}"
            f" {rgs} {rms}")

    # ── 4-gene (extend best 3-gene) ──────
    log("")
    log("  4-gene panels (extend best 3-gene):")
    log(f"  {'Pos':>24} {'Neg':>16}"
        f" {'r_TCGA':>8} {'r_GEO':>8}"
        f" {'r_min':>8}")
    log(f"  {'-'*24} {'-'*16}"
        f" {'-'*8} {'-'*8} {'-'*8}")

    best_4 = {"r_min": 0, "panel": None}
    res4   = []

    if best_3["panel"]:
        bp_pos, bp_neg = best_3["panel"]

        for add_p in PANEL_CANDIDATES_POS:
            if add_p in bp_pos:
                continue
            new_pos = bp_pos + [add_p]
            rt = score_panel(
                new_pos, bp_neg,
                expr_t, d_t, t_cols_t)
            rg = (score_panel(
                new_pos, bp_neg,
                expr_g, d_g, t_cols_g)
                  if d_g is not None
                  else np.nan)
            rm = rmin(rt, rg)
            res4.append({
                "pos": "+".join(new_pos),
                "neg": "+".join(bp_neg),
                "rt": rt, "rg": rg,
                "rmin": rm,
            })
            if (not np.isnan(rm)
                    and rm > best_4["r_min"]):
                best_4 = {
                    "r_min": rm,
                    "panel": (new_pos,
                               bp_neg),
                }

        for add_n in PANEL_CANDIDATES_NEG:
            if add_n in bp_neg:
                continue
            new_neg = bp_neg + [add_n]
            rt = score_panel(
                bp_pos, new_neg,
                expr_t, d_t, t_cols_t)
            rg = (score_panel(
                bp_pos, new_neg,
                expr_g, d_g, t_cols_g)
                  if d_g is not None
                  else np.nan)
            rm = rmin(rt, rg)
            res4.append({
                "pos": "+".join(bp_pos),
                "neg": "+".join(new_neg),
                "rt": rt, "rg": rg,
                "rmin": rm,
            })
            if (not np.isnan(rm)
                    and rm > best_4["r_min"]):
                best_4 = {
                    "r_min": rm,
                    "panel": (bp_pos,
                               new_neg),
                }

    res4.sort(key=lambda x:
              -(x["rmin"]
                if not np.isnan(x["rmin"])
                else 0))
    for row in res4[:15]:
        rgs = (f"{row['rg']:>8.4f}"
               if not np.isnan(row['rg'])
               else f"{'NA':>8}")
        rms = (f"{row['rmin']:>8.4f}"
               if not np.isnan(row['rmin'])
               else f"{'NA':>8}")
        log(f"  {row['pos']:>24}"
            f" {row['neg']:>16}"
            f" {row['rt']:>8.4f}"
            f" {rgs} {rms}")

    # ── Summary ──────────────────────────
    log("")
    log("  BEST PANELS FOUND:")
    for lbl_b, best in [
        ("2-gene", best_2),
        ("3-gene", best_3),
        ("4-gene", best_4),
    ]:
        if best["panel"]:
            pos_g, neg_g = best["panel"]
            rm_val = best["r_min"]
            flag = (
                "TARGET ACHIEVED ✓"
                if rm_val >= 0.85
                else "near target (~)"
                if rm_val >= 0.80
                else "below target ✗")
            log(f"  {lbl_b}: "
                f"Pos={pos_g}  "
                f"Neg={neg_g}  "
                f"r_min={rm_val:.4f}  "
                f"{flag}")

    # S3-P6 verdict
    best_all = max(
        [best_2, best_3, best_4],
        key=lambda x: x["r_min"])
    log("")
    if best_all["r_min"] >= 0.85:
        log("  S3-P6 CONFIRMED: "
            "r >= 0.85 BOTH datasets ✓")
    else:
        log(f"  S3-P6 NOT CONFIRMED: "
            f"best r_min = "
            f"{best_all['r_min']:.4f}")

    # Save
    for fname, data in [
        ("panel_2gene.csv", res2),
        ("panel_3gene.csv", res3),
        ("panel_4gene.csv", res4),
    ]:
        pd.DataFrame(data).to_csv(
            os.path.join(S3_DIR, fname),
            index=False)

    return best_2, best_3, best_4

# ═══════════════════════════════════════════════════════
# OBJ-7  CABOZANTINIB GEOMETRY
# ═══════════════════════════════════════════════════════

def cabozantinib_geometry(expr, t_cols,
                          depth, label):
    log("")
    log("=" * 60)
    log(f"OBJ-7 — CABOZANTINIB GEOMETRY"
        f" — {label}")
    log("=" * 60)
    log("  S3-P7: AXL depth-positive "
        "r > +0.25")
    log("")

    d = depth.reindex(t_cols).dropna()

    rows = []
    for gene in CABO_PANEL:
        if gene not in expr.index:
            continue
        v = pd.Series(
            expr.loc[gene, t_cols].values,
            index=t_cols,
        ).reindex(d.index)
        r, p = safe_r(v.values, d.values)
        if np.isnan(r):
            continue
        rows.append({
            "gene": gene, "r": r, "p": p})

    df = pd.DataFrame(rows).sort_values(
        "r", ascending=False)
    df.to_csv(os.path.join(
        S3_DIR,
        f"cabo_{label.lower()}.csv"),
        index=False)

    log(f"  {'Gene':<10} {'r(depth)':>10}"
        f"  {'p':>10}  tier")
    log(f"  {'-'*10} {'-'*10}  "
        f"{'-'*10}  {'-'*15}")
    for _, row in df.iterrows():
        tier = (
            "TIER_1"
            if abs(row.r) >= 0.40
            else "TIER_2"
            if abs(row.r) >= 0.25
            else "TIER_3"
            if abs(row.r) >= 0.10
            else "AGNOSTIC")
        log(f"  {row.gene:<10} "
            f"{row.r:>+10.4f}  "
            f"{fmt_p(row.p):>10}  {tier}")

    axl = df[df.gene == "AXL"]
    if len(axl) > 0:
        r_axl = float(axl.iloc[0].r)
        log("")
        log(f"  S3-P7: AXL r = {r_axl:+.4f}")
        if r_axl > 0.25:
            log("  CONFIRMED: AXL "
                "depth-positive ✓")
            log("  Cabozantinib benefits "
                "deep ccRCC via AXL arm")
        elif r_axl > 0:
            log("  PARTIAL: AXL trending "
                "positive but < +0.25")
        else:
            log("  WRONG: AXL not "
                "depth-positive ✗")
    return df

# ═══════════════════════════════════════════════════════
# FIGURE
# ═══════════════════════════════════════════════════════

def generate_figure(depth_t, emt_df,
                    chrom_df, cabo_df,
                    best2, best3, best4,
                    lipid_df,
                    score_a, score_b):
    log("")
    log("Generating Script 3 figure...")

    fig = plt.figure(figsize=(18, 12))
    gs  = gridspec.GridSpec(
        3, 3, figure=fig,
        hspace=0.55, wspace=0.42)
    axs = [fig.add_subplot(gs[r, c])
           for r in range(3)
           for c in range(3)]

    C = ["#e74c3c", "#2ecc71", "#2980b9",
         "#8e44ad", "#e67e22", "#16a085"]

    # A — EMT r(depth)
    if emt_df is not None \
            and not emt_df.empty:
        df_e = emt_df.sort_values("r")
        cols_e = [C[0] if r > 0
                  else C[1]
                  for r in df_e.r.values]
        axs[0].barh(df_e.gene.values,
                    df_e.r.values,
                    color=cols_e,
                    edgecolor="black",
                    linewidth=0.3)
        axs[0].axvline(0, color="black",
                       linewidth=0.8)
        axs[0].set_title(
            "A — EMT r(depth) TCGA",
            fontsize=9)
        axs[0].set_xlabel("r", fontsize=8)
        axs[0].tick_params(axis="y",
                           labelsize=6)

    # B — Chromatin r(depth)
    if chrom_df is not None \
            and not chrom_df.empty:
        df_c = chrom_df.sort_values("r")
        cols_c = [C[0] if r > 0
                  else C[1]
                  for r in df_c.r.values]
        axs[1].barh(df_c.gene.values,
                    df_c.r.values,
                    color=cols_c,
                    edgecolor="black",
                    linewidth=0.3)
        axs[1].axvline(0, color="black",
                       linewidth=0.8)
        axs[1].set_title(
            "B — Chromatin r(depth) TCGA",
            fontsize=9)
        axs[1].set_xlabel("r", fontsize=8)
        axs[1].tick_params(axis="y",
                           labelsize=6)

    # C — Cabozantinib r(depth)
    if cabo_df is not None \
            and not cabo_df.empty:
        df_cab = cabo_df.sort_values("r")
        cols_cab = [C[0] if r > 0
                    else C[1]
                    for r in
                    df_cab.r.values]
        axs[2].barh(df_cab.gene.values,
                    df_cab.r.values,
                    color=cols_cab,
                    edgecolor="black",
                    linewidth=0.3)
        axs[2].axvline(0, color="black",
                       linewidth=0.8)
        axs[2].axvline(0.25, color="grey",
                       linewidth=0.6,
                       linestyle=":")
        axs[2].set_title(
            "C — Cabozantinib r(depth)",
            fontsize=9)
        axs[2].set_xlabel("r", fontsize=8)
        axs[2].tick_params(axis="y",
                           labelsize=6)

    # D — Lipid TF drivers
    if (lipid_df is not None and
            not lipid_df.empty and
            "r_SCD" in lipid_df.columns):
        df_l = lipid_df.dropna(
            subset=["r_SCD"]
        ).sort_values("r_SCD",
                      ascending=False)
        axs[3].barh(df_l.tf.values,
                    df_l.r_SCD.values,
                    color=C[2],
                    edgecolor="black",
                    linewidth=0.3)
        axs[3].axvline(0, color="black",
                       linewidth=0.8)
        axs[3].set_title(
            "D — r(TF, SCD) lipid driver",
            fontsize=9)
        axs[3].set_xlabel(
            "r(TF, SCD)", fontsize=8)
        axs[3].tick_params(axis="y",
                           labelsize=7)

    # E — Sub-axis scatter
    if (score_a is not None
            and score_b is not None):
        d_t = depth_t.reindex(
            score_a.index).dropna()
        common = score_a.index.intersection(
            score_b.index).intersection(
            d_t.index)
        sc = axs[4].scatter(
            score_a.reindex(common).values,
            score_b.reindex(common).values,
            c=d_t.reindex(common).values,
            cmap="RdYlGn_r",
            alpha=0.5, s=10)
        plt.colorbar(sc, ax=axs[4],
                     label="depth")
        axs[4].set_xlabel(
            "Depth_A (transport)", fontsize=8)
        axs[4].set_ylabel(
            "Depth_B (metabolic)", fontsize=8)
        axs[4].set_title(
            "E — PT sub-axes scatter",
            fontsize=9)

    # F — Panel optimisation summary
    panels = []
    for best, lbl_b in [
        (best2, "2-gene"),
        (best3, "3-gene"),
        (best4, "4-gene"),
    ]:
        if best and best.get("panel"):
            panels.append(
                (lbl_b, best["r_min"]))
    if panels:
        names_p = [p[0] for p in panels]
        vals_p  = [abs(p[1])
                   for p in panels]
        cols_p  = [C[1] if v >= 0.85
                   else C[4] if v >= 0.80
                   else C[0]
                   for v in vals_p]
        axs[5].bar(names_p, vals_p,
                   color=cols_p,
                   edgecolor="black",
                   linewidth=0.5)
        axs[5].axhline(
            0.85, color="green",
            linewidth=1.5,
            linestyle="--",
            label="target=0.85")
        axs[5].set_ylim(0, 1)
        axs[5].legend(fontsize=7)
        axs[5].set_title(
            "F — Panel r_min(TCGA, GEO)",
            fontsize=9)
        axs[5].set_ylabel("|r|", fontsize=8)

    # G-I — text summaries
    summaries = [
        ("G — S3 Predictions",
         ["S3-P1 PT axes separable r<0.80",
          "S3-P2 SREBF1>MYC for SCD",
          "S3-P3 CDH1 r<-0.25",
          "S3-P4 BAP1 r<-0.20",
          "S3-P5 PBRM1 r>+0.10",
          "S3-P6 panel r>=0.85 both",
          "S3-P7 AXL r>+0.25"]),
        ("H — Three-wall attractor",
         ["Wall 1: EPAS1 (VHL lost)",
          "  → Belzutifan universal",
          "Wall 2: EZH2 epigenetic",
          "  → Tazemetostat depth-high",
          "Wall 3: FAP-CAF paracrine",
          "  → FAP-ADC advanced stage",
          "Triple combo: all 3 walls"]),
        ("I — Novel (pre-literature)",
         ["MYC drives GLUT1 variation",
          "FAP-CAF self-sustaining",
          "CD274 ⊥ FOXP3 (independent)",
          "Depth → OS p=0.0001",
          "4-gene panel GEO r=0.888",
          "Chromatin: BAP1/PBRM1 axis"]),
    ]
    for i, (title, lines) in \
            enumerate(summaries):
        axs[6 + i].axis("off")
        axs[6 + i].set_title(
            title, fontsize=9)
        for j, line in enumerate(lines):
            axs[6 + i].text(
                0.03,
                0.88 - j * 0.13,
                line,
                fontsize=7,
                transform=axs[
                    6 + i].transAxes)

    fig.suptitle(
        "ccRCC False Attractor — Script 3\n"
        "Sub-axes / EMT / Chromatin / "
        "Panel / Cabozantinib",
        fontsize=11,
        fontweight="bold")

    out = os.path.join(S3_DIR,
                       "figure_s3.png")
    fig.savefig(out, dpi=150,
                bbox_inches="tight")
    plt.close(fig)
    log(f"  Figure saved: {out}")

# ═══════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════

def main():
    log("OrganismCore — ccRCC Script 3")
    log("Sub-axis / EMT / Chromatin / "
        "Panel Optimisation")
    log("Document 94c-pre | 2026-03-02")
    log("")
    log("PREDICTIONS LOCKED:")
    log("  S3-P1  r(Depth_A,Depth_B)<0.80")
    log("  S3-P2  SREBF1>MYC for SCD")
    log("  S3-P3  CDH1 r<-0.25")
    log("  S3-P4  BAP1 r<-0.20")
    log("  S3-P5  PBRM1 r>+0.10")
    log("  S3-P6  panel r>=0.85 both")
    log("  S3-P7  AXL r>+0.25")
    log("")

    # Load depth scores from Script 1
    depth_t = load_depth("tcga")
    depth_g = load_depth("geo")

    # Reload expression
    expr_t, t_cols_t = parse_tcga()
    expr_g, t_cols_g = parse_geo()

    # OBJ-1 — PT sub-axes
    score_a_t, score_b_t, r_ab_t = \
        pt_subaxis(
            expr_t, t_cols_t,
            depth_t, "TCGA")
    if expr_g is not None:
        pt_subaxis(
            expr_g, t_cols_g,
            depth_g, "GEO")

    # OBJ-2 — Lipid TF drivers
    lipid_t = lipid_tf_driver(
        expr_t, t_cols_t, depth_t, "TCGA")
    if expr_g is not None:
        lipid_tf_driver(
            expr_g, t_cols_g,
            depth_g, "GEO")

    # OBJ-3 — Full EMT circuit
    emt_t = emt_circuit(
        expr_t, t_cols_t, depth_t, "TCGA")
    if expr_g is not None:
        emt_circuit(
            expr_g, t_cols_g,
            depth_g, "GEO")

    # OBJ-4/5 — Chromatin depth map
    chrom_t = chromatin_depth(
        expr_t, t_cols_t, depth_t, "TCGA")
    if expr_g is not None:
        chromatin_depth(
            expr_g, t_cols_g,
            depth_g, "GEO")

    # OBJ-6 — Panel optimisation
    best2, best3, best4 = panel_optimise(
        expr_t, depth_t, t_cols_t,
        expr_g, depth_g,
        t_cols_g if expr_g is not None
        else [])

    # OBJ-7 — Cabozantinib geometry
    cabo_t = cabozantinib_geometry(
        expr_t, t_cols_t, depth_t, "TCGA")
    if expr_g is not None:
        cabozantinib_geometry(
            expr_g, t_cols_g,
            depth_g, "GEO")

    # Figure
    generate_figure(
        depth_t,
        emt_t, chrom_t, cabo_t,
        best2, best3, best4,
        lipid_t,
        score_a_t, score_b_t)

    # Summary
    log("")
    log("=" * 60)
    log("SCRIPT 3 COMPLETE")
    log("=" * 60)
    for fname in sorted(
            os.listdir(S3_DIR)):
        fp = os.path.join(S3_DIR, fname)
        log(f"  {fname:<45}"
            f" {os.path.getsize(fp):>8} bytes")
    log("")
    log("  NEXT: paste full output.")
    log("  Classify all 7 predictions.")
    log("  Write document 94c-pre.")
    log("  Then literature check (94c).")

    write_log()


if __name__ == "__main__":
    main()
