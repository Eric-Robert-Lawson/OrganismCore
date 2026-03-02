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

# S1/S2 core
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

# S3-OBJ-1 — PT sub-axes
PT_TRANSPORT = ["SLC34A1", "SLC22A6", "AQP1",
                "SLC13A3", "SLC22A8"]
PT_METABOLIC = ["FBP1",    "G6PC",    "PCK1",
                "AGXT",    "GATM",    "PCK2"]

# S3-OBJ-2 — Lipid arm TF drivers
LIPID_PANEL = [
    "SCD",    "ACLY",   "FASN",   "PLIN2",
    "HMGCR",  "SQLE",   "ACACA",  "CPT1A",
    "CPT1B",  "HADHA",  "PPARA",  "PPARG",
    "SREBF1", "SREBF2", "MLXIPL", "MYC",
    "EPAS1",  "HIF1A",  "ARNT",
]

# S3-OBJ-3 — Full EMT circuit
EMT_PANEL = [
    "VIM",    "CDH1",   "CDH2",   "EPCAM",
    "FN1",    "SNAI1",  "SNAI2",  "TWIST1",
    "TWIST2", "ZEB1",   "ZEB2",   "ITGB6",
    "MMP2",   "MMP9",   "MMP14",  "CTNNB1",
    "ESRP1",  "ESRP2",  "CLDN4",  "OCLN",
    "KRT7",   "KRT19",
]

# S3-OBJ-4/5 — Chromatin/mutation proxies
CHROMATIN_PANEL = [
    "VHL",    "PBRM1",  "BAP1",   "SETD2",
    "KDM5C",  "KDM6A",  "KDM1A",  "ARID1A",
    "SMARCA4","SMARCB1","EP300",  "CREBBP",
    "EZH2",   "EZH1",   "SUZ12",  "EED",
    "DNMT3A", "TET2",   "ASXL1",  "BCOR",
    "HDAC1",  "HDAC2",  "RCOR1",  "JARID2",
]

# S3-OBJ-7 — Cabozantinib geometry
CABO_PANEL = [
    "MET",    "HGF",    "AXL",    "GAS6",
    "MERTK",  "TYRO3",  "ANGPT2", "TEK",
    "KDR",    "FLT1",   "PDGFRA", "PDGFRB",
    "FGF2",   "FGFR1",  "RET",    "NTRK1",
    "VEGFA",  "VEGFC",  "VEGFD",
]

# Panel optimisation candidates (top depth
# correlates from S1 + S2)
PANEL_CANDIDATES_POS = [
    "SLC2A1", "VIM",    "CA9",    "EGLN3",
    "TGFB1",  "FAP",    "VEGFA",  "COL1A1",
    "MYC",    "LDHA",   "PDK1",   "EZH2",
    "FOXP3",  "SCD",    "TOP2A",
]
PANEL_CANDIDATES_NEG = [
    "FBP1",    "SLC34A1","SLC22A6","G6PC",
    "PCK1",    "UMOD",   "SLC13A3","AQP1",
    "AGXT",    "CPT1A",  "PAX8",   "HNF1A",
    "GATM",    "ALDOB",  "SLC22A8",
]

FULL_S3 = list(dict.fromkeys(
    SW_GENES + FA_GENES +
    PT_TRANSPORT + PT_METABOLIC +
    LIPID_PANEL + EMT_PANEL +
    CHROMATIN_PANEL + CABO_PANEL +
    PANEL_CANDIDATES_POS +
    PANEL_CANDIDATES_NEG
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
            if code.isdigit() and 1 <= int(code) <= 9:
                t_cols.append(s)
    log(f"  TCGA genes={len(avail)}, "
        f"tumours={len(t_cols)}")
    return expr, t_cols

def parse_geo():
    log("Loading GSE53757...")
    if not os.path.exists(GPL570_LOCAL):
        log("  GPL570 not found — skip GEO")
        return None, None

    probe_map = {}
    gw = set(FULL_S3)
    with open(GPL570_LOCAL, "r",
              encoding="utf-8",
              errors="replace") as f:
        header = id_c = sym_c = None
        for line in f:
            line = line.rstrip("\n")
            if line.startswith(
                    ("^", "!", "#")):
                continue
            parts = line.split("\t")
            if header is None:
                lower = [p.strip().lower()
                         for p in parts]
                if "id" not in lower:
                    continue
                header = parts
                id_c   = lower.index("id")
                sym_c  = None
                for kw in [
                    "gene symbol",
                    "gene_symbol", "symbol"
                ]:
                    for i, lp in enumerate(
                            lower):
                        if kw in lp:
                            sym_c = i
                            break
                    if sym_c is not None:
                        break
                if sym_c is None:
                    sym_c = 1
                continue
            if len(parts) <= max(id_c,
                                  sym_c):
                continue
            pid = parts[id_c].strip()
            raw_sym = parts[sym_c].strip()
            sym = (raw_sym.split("///")[0]
                   .strip().upper()
                   .split()[0])
            if sym and sym not in (
                    "", "---", "N/A", "NA"):
                probe_map[pid] = sym

    sample_ids   = []
    source_names = []
    with gzip.open(GEO_LOCAL, "rt") as f:
        for line in f:
            line = line.rstrip()
            if line.startswith(
                    "!Sample_geo_accession"):
                sample_ids.extend([
                    p.strip().strip('"')
                    for p in
                    line.split("\t")[1:]
                    if p.strip().strip('"')
                    .startswith("GSM")])
            elif line.startswith(
                    "!Sample_source_name_ch1"):
                source_names.extend([
                    p.strip().strip('"')
                    for p in
                    line.split("\t")[1:]
                    if p.strip()])
            elif "series_matrix_table_begin" \
                    in line:
                break

    n = min(len(sample_ids),
            len(source_names))
    types = ["normal" if "normal" in
             s.lower() else "tumour"
             for s in source_names[:n]]
    t_ids = [sample_ids[i]
             for i in range(n)
             if types[i] == "tumour"]

    col_hdr   = None
    expr_rows = []
    with gzip.open(GEO_LOCAL, "rt") as f:
        in_tbl = False
        for line in f:
            line = line.rstrip()
            if "series_matrix_table_begin" \
                    in line:
                in_tbl = True
                continue
            if "series_matrix_table_end" \
                    in line:
                break
            if in_tbl:
                if col_hdr is None:
                    col_hdr = line.split("\t")
                else:
                    expr_rows.append(
                        line.split("\t"))

    probe_ids = [r[0].strip('"')
                 for r in expr_rows]
    col_ids   = [c.strip('"')
                 for c in col_hdr[1:]]

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
        values, index=probe_ids,
        columns=col_ids)
    probe_df = np.log2(
        probe_df.clip(lower=0) + 1)

    t_cols = [c for c in t_ids
              if c in probe_df.columns]

    gene_rows = {}
    for pid in probe_df.index:
        sym = probe_map.get(pid)
        if sym and sym in gw:
            existing = gene_rows.get(sym)
            if existing is None:
                gene_rows[sym] = probe_df.loc[pid]
            else:
                if (probe_df.loc[pid, t_cols].var()
                        > existing[t_cols].var()):
                    gene_rows[sym] = probe_df.loc[pid]

    gene_df = pd.DataFrame(gene_rows).T
    log(f"  GEO genes={len(gene_df)}, "
        f"tumours={len(t_cols)}")
    return gene_df, t_cols

def load_depth(tag):
    p = os.path.join(S1_DIR,
                     f"depth_scores_{tag}.csv")
    d = pd.read_csv(p, index_col="sample_id")
    return d["depth_score"]

# ═══════════════════════════════════════════════════════
# OBJ-1  PT SUB-AXIS SEPARATION
# ══════════════════════��════════════════════════════════

def pt_subaxis(expr, t_cols, depth,
               label):
    log("")
    log("=" * 60)
    log(f"OBJ-1 — PT SUB-AXES — {label}")
    log("=" * 60)

    d = depth.reindex(t_cols).dropna()

    def axis_score(genes, name):
        avail = [g for g in genes
                 if g in expr.index]
        if not avail:
            log(f"  {name}: no genes")
            return None
        mat = pd.DataFrame({
            g: pd.Series(
                expr.loc[g, t_cols].values,
                index=t_cols
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

    if score_a is not None \
            and score_b is not None:
        r_ab, p_ab = safe_r(
            score_a.values, score_b.values)
        log("")
        log(f"  r(Depth_A, Depth_B) = "
            f"{r_ab:+.4f}  p = {fmt_p(p_ab)}")
        if r_ab < 0.80:
            log(f"  PREDICTION CONFIRMED: "
                f"r < 0.80 — axes separable ✓")
        else:
            log(f"  PREDICTION WRONG: "
                f"r >= 0.80 — axes not separable ✗")

        # Pairwise: what couples to what?
        log("")
        log("  Cross-axis gene correlations:")
        log(f"  {'Gene A':<12} {'Gene B':<12}"
            f" {'r':>8}  class")
        log(f"  {'-'*12} {'-'*12} {'-'*8}"
            f"  {'-'*20}")
        cross = []
        for ga in PT_TRANSPORT:
            for gb in PT_METABOLIC:
                if (ga not in expr.index or
                        gb not in expr.index):
                    continue
                va = pd.Series(
                    expr.loc[ga, t_cols].values,
                    index=t_cols
                ).reindex(d.index)
                vb = pd.Series(
                    expr.loc[gb, t_cols].values,
                    index=t_cols
                ).reindex(d.index)
                r, _ = safe_r(va.values,
                               vb.values)
                cross.append((ga, gb, r))
        cross.sort(key=lambda x:
                   -abs(x[2])
                   if not np.isnan(x[2])
                   else 0)
        for ga, gb, r in cross[:10]:
            cls = ("COUPLED" if abs(r) >= 0.40
                   else "WEAK"
                   if abs(r) >= 0.20
                   else "DECOUPLED")
            log(f"  {ga:<12} {gb:<12}"
                f" {r:>+8.4f}  {cls}")

        # Save
        out = pd.DataFrame({
            "depth_a": score_a,
            "depth_b": score_b,
            "depth_full": d,
        })
        out.to_csv(os.path.join(
            S3_DIR,
            f"pt_subaxes_{label.lower()}.csv"))
        return score_a, score_b, r_ab
    return None, None, np.nan

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

    log(f"  {'TF':<10}  "
        + "  ".join(f"{e:>8}" for e in
                    lipid_effectors)
        + "  depth_r")
    log(f"  {'-'*10}  "
        + "  ".join(f"{'------':>8}"
                    for _ in lipid_effectors)
        + "  -------")

    rows = []
    for tf in tfs:
        if tf not in expr.index:
            continue
        tf_v = pd.Series(
            expr.loc[tf, t_cols].values,
            index=t_cols
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
                index=t_cols
            ).reindex(d.index)
            r, _ = safe_r(tf_v.values,
                           eff_v.values)
            eff_rs.append(r)

        line = f"  {tf:<10}  "
        line += "  ".join(
            f"{r:>+8.4f}" if not np.isnan(r)
            else f"{'NA':>8}"
            for r in eff_rs)
        line += f"  {tf_d_r:>+7.4f}"
        log(line)
        rows.append({
            "tf":    tf,
            "depth_r": tf_d_r,
            **{f"r_{e}": r
               for e, r in
               zip(lipid_effectors, eff_rs)},
        })

    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(
        S3_DIR,
        f"lipid_tfs_{label.lower()}.csv"),
        index=False)

    # Assess prediction
    if len(rows) >= 2:
        log("")
        top = df.dropna(
            subset=["r_SCD"]
        ).sort_values("r_SCD", key=abs,
                      ascending=False)
        if len(top) >= 2:
            winner = top.iloc[0].tf
            runner = top.iloc[1].tf
            log(f"  TOP TF for SCD: "
                f"{winner} "
                f"r={top.iloc[0].r_SCD:+.4f}")
            log(f"  2nd TF for SCD: "
                f"{runner} "
                f"r={top.iloc[1].r_SCD:+.4f}")

            pred_ok = winner == "SREBF1"
            if pred_ok:
                log("  PREDICTION S3-P2 "
                    "CONFIRMED ✓  "
                    "SREBF1 > MYC")
            else:
                log(f"  PREDICTION S3-P2 "
                    f"WRONG ✗  "
                    f"{winner} beats SREBF1")

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

    log(f"  {'Gene':<10} {'r(depth)':>10}"
        f"  {'p':>10}  direction")
    log(f"  {'-'*10} {'-'*10}  "
        f"{'-'*10}  {'-'*20}")

    rows = []
    for gene in EMT_PANEL:
        if gene not in expr.index:
            continue
        v = pd.Series(
            expr.loc[gene, t_cols].values,
            index=t_cols
        ).reindex(d.index)
        r, p = safe_r(v.values, d.values)
        if np.isnan(r):
            continue
        direction = (
            "↑ deeper" if r > 0
            else "↓ shallower")
        log(f"  {gene:<10} {r:>+10.4f}"
            f"  {fmt_p(p):>10}  {direction}")
        rows.append({
            "gene": gene, "r": r, "p": p})

    df = pd.DataFrame(rows).sort_values(
        "r", key=abs, ascending=False)
    df.to_csv(os.path.join(
        S3_DIR,
        f"emt_{label.lower()}.csv"),
        index=False)

    # Assess CDH1 prediction
    cdh1_r = df[df.gene == "CDH1"]["r"]
    if len(cdh1_r) > 0:
        r_cdh1 = float(cdh1_r.iloc[0])
        log("")
        log(f"  S3-P3 CDH1 r = {r_cdh1:+.4f}")
        if r_cdh1 < -0.25:
            log("  PREDICTION CONFIRMED: "
                "CDH1 DOWN with depth ✓")
        elif r_cdh1 < 0:
            log("  PARTIAL: CDH1 trending "
                "down but < -0.25")
        else:
            log("  PREDICTION WRONG: "
                "CDH1 not down with depth ✗")

    # Key EMT circuit tests
    circuits = [
        ("SNAI1", "CDH1",   "negative"),
        ("ZEB1",  "CDH1",   "negative"),
        ("ZEB2",  "CDH1",   "negative"),
        ("TWIST1","VIM",    "positive"),
        ("SNAI1", "VIM",    "positive"),
        ("ZEB1",  "VIM",    "positive"),
        ("VIM",   "CDH2",   "positive"),
        ("VIM",   "EPCAM",  "negative"),
        ("CTNNB1","CDH1",   "positive"),
        ("ESRP1", "CDH1",   "positive"),
    ]

    log("")
    log("  EMT circuit pairs:")
    log(f"  {'Circuit':<18} {'r':>8}  "
        f"{'Status':>12}  V")
    log(f"  {'-'*18} {'-'*8}  "
        f"{'-'*12}  -")

    for ga, gb, exp in circuits:
        if (ga not in expr.index or
                gb not in expr.index):
            continue
        va = pd.Series(
            expr.loc[ga, t_cols].values,
            index=t_cols
        ).reindex(d.index)
        vb = pd.Series(
            expr.loc[gb, t_cols].values,
            index=t_cols
        ).reindex(d.index)
        r, _ = safe_r(va.values, vb.values)
        if np.isnan(r):
            continue
        status = (
            "CONNECTED" if abs(r) >= 0.40
            else "WEAK" if abs(r) >= 0.20
            else "BROKEN")
        ok = ("✓" if (
            (exp == "negative" and r < 0) or
            (exp == "positive" and r > 0))
              else "✗")
        log(f"  {ga}→{gb:<12} {r:>+8.4f}  "
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
    log("  Prediction: BAP1↓, SETD2↓, "
        "KDM5C↓ with depth")
    log("  Prediction: PBRM1↑ with depth")
    log("")

    d = depth.reindex(t_cols).dropna()

    rows = []
    for gene in CHROMATIN_PANEL:
        if gene not in expr.index:
            continue
        v = pd.Series(
            expr.loc[gene, t_cols].values,
            index=t_cols
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

    log(f"  {'Gene':<12} {'r(depth)':>10}"
        f"  {'p':>10}  prediction  result")
    log(f"  {'-'*12} {'-'*10}  "
        f"{'-'*10}  {'-'*12}  {'-'*8}")

    # Predictions
    preds = {
        "BAP1":    ("negative", "S3-P4"),
        "PBRM1":   ("positive", "S3-P5"),
        "SETD2":   ("negative", None),
        "KDM5C":   ("negative", None),
        "VHL":     ("negative", None),
        "EZH2":    ("positive", None),
        "KDM1A":   ("positive", None),
        "DNMT3A":  ("negative", None),
        "ARID1A":  (None,       None),
        "HDAC1":   ("positive", None),
        "SUZ12":   ("positive", None),
    }

    for _, row in df.iterrows():
        gene = row.gene
        r    = row.r
        pred_dir, pred_id = preds.get(
            gene, (None, None))
        if pred_dir == "negative":
            ok = "✓" if r < -0.10 else "✗"
            pred_s = "DOWN pred"
        elif pred_dir == "positive":
            ok = "✓" if r > +0.10 else "✗"
            pred_s = "UP pred"
        else:
            ok     = ""
            pred_s = ""
        p_id = pred_id or ""
        log(f"  {gene:<12} {r:>+10.4f}"
            f"  {fmt_p(row.p):>10}  "
            f"{pred_s:<12}  {ok} {p_id}")

    # Explicit prediction checks
    for gene, thresh, pred_name, direction \
            in [
        ("BAP1",  -0.20, "S3-P4", "negative"),
        ("PBRM1", +0.10, "S3-P5", "positive"),
    ]:
        sub = df[df.gene == gene]
        if len(sub) == 0:
            log(f"  {pred_name}: {gene} "
                f"not in data")
            continue
        r = float(sub.iloc[0].r)
        log("")
        log(f"  {pred_name}: {gene} "
            f"r = {r:+.4f}")
        if direction == "negative" \
                and r < thresh:
            log(f"    CONFIRMED ✓")
        elif direction == "positive" \
                and r > thresh:
            log(f"    CONFIRMED ✓")
        else:
            log(f"    NOT CONFIRMED ✗")

    # Mutation proxy: low-expressers are
    # higher depth?
    log("")
    log("  MUTATION PROXY ANALYSIS:")
    log("  Low expressers = mutation proxy")
    log("  Test: do low-expression quartile"
        " tumours have higher depth?")
    log("")

    for gene in ["BAP1", "PBRM1", "SETD2",
                 "KDM5C"]:
        if gene not in expr.index:
            continue
        v = pd.Series(
            expr.loc[gene, t_cols].values,
            index=t_cols
        ).reindex(d.index).dropna()
        q25 = float(np.percentile(v, 25))
        q75 = float(np.percentile(v, 75))
        low_idx  = v[v <= q25].index
        high_idx = v[v >= q75].index
        d_low  = d.reindex(low_idx).dropna()
        d_high = d.reindex(high_idx).dropna()
        if len(d_low) < 5 or len(d_high) < 5:
            continue
        _, pmwu = stats.mannwhitneyu(
            d_low, d_high,
            alternative="two-sided")
        diff = float(d_low.mean()
                     - d_high.mean())
        flag = ("deeper" if diff > 0
                else "shallower")
        log(f"  {gene:<8}: low-Q1 vs high-Q4"
            f"  Δdepth={diff:+.4f}"
            f"  p={fmt_p(pmwu)}"
            f"  low='{flag}'")

    return df

# ═══════════════════════════════════════════════════════
# OBJ-6  PANEL OPTIMISATION
# ═══════════════════════════════════════════════════════

def panel_optimise(expr_t, depth_t, t_cols_t,
                   expr_g, depth_g, t_cols_g):
    log("")
    log("=" * 60)
    log("OBJ-6 — PANEL OPTIMISATION")
    log("Target: r >= 0.85 BOTH datasets")
    log("=" * 60)

    d_t = depth_t.reindex(t_cols_t).dropna()
    d_g = (depth_g.reindex(t_cols_g).dropna()
           if expr_g is not None else None)

    def score_panel(pos_genes, neg_genes,
                    expr, d, t_cols):
        avail_p = [g for g in pos_genes
                   if g in expr.index]
        avail_n = [g for g in neg_genes
                   if g in expr.index]
        if not avail_p and not avail_n:
            return np.nan
        s = np.zeros(len(d))
        c = 0
        if avail_p:
            mat = pd.DataFrame({
                g: pd.Series(
                    expr.loc[g, t_cols].values,
                    index=t_cols
                ).reindex(d.index)
                for g in avail_p})
            s += norm01(mat.mean(
                axis=1).values)
            c += 1
        if avail_n:
            mat = pd.DataFrame({
                g: pd.Series(
                    expr.loc[g, t_cols].values,
                    index=t_cols
                ).reindex(d.index)
                for g in avail_n})
            s += (1 - norm01(mat.mean(
                axis=1).values))
            c += 1
        if c > 0:
            s /= c
        r, _ = safe_r(s, d.values)
        return r

    log("")
    log("  SYSTEMATIC 2-gene panels"
        " (1 pos + 1 neg):")
    log(f"  {'Pos':>10} {'Neg':>10}"
        f" {'r_TCGA':>8} {'r_GEO':>7}"
        f" {'min_r':>7}")
    log(f"  {'-'*10} {'-'*10}"
        f" {'-'*8} {'-'*7} {'-'*7}")

    best_2  = {"r_min": 0, "panel": None}
    results = []
    for pos in PANEL_CANDIDATES_POS[:8]:
        for neg in PANEL_CANDIDATES_NEG[:8]:
            rt = score_panel(
                [pos], [neg],
                expr_t, d_t, t_cols_t)
            rg = (score_panel(
                [pos], [neg],
                expr_g, d_g, t_cols_g)
                  if d_g is not None
                  else np.nan)
            rmin = (min(rt, rg)
                    if not np.isnan(rg)
                    else rt)
            results.append({
                "pos": pos, "neg": neg,
                "rt": rt, "rg": rg,
                "rmin": rmin,
            })
            if rmin > best_2["r_min"]:
                best_2 = {
                    "r_min": rmin,
                    "panel": ([pos], [neg]),
                }

    results.sort(key=lambda x: -(
        x["rmin"]
        if not np.isnan(x["rmin"])
        else 0))
    for row in results[:15]:
        rg_s = (f"{row['rg']:>7.4f}"
                if not np.isnan(row['rg'])
                else f"{'NA':>7}")
        rmin_s = (f"{row['rmin']:>7.4f}"
                  if not np.isnan(
                      row['rmin'])
                  else f"{'NA':>7}")
        log(f"  {row['pos']:>10}"
            f" {row['neg']:>10}"
            f" {row['rt']:>8.4f}"
            f" {rg_s}"
            f" {rmin_s}")

    log("")
    log("  SYSTEMATIC 3-gene panels"
        " (2 pos + 1 neg  or  1 pos + 2 neg):")

    best_3   = {"r_min": 0, "panel": None}
    results3 = []

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
            rmin = (min(rt, rg)
                    if not np.isnan(rg)
                    else rt)
            results3.append({
                "pos": f"{p1}+{p2}",
                "neg": neg,
                "rt": rt, "rg": rg,
                "rmin": rmin,
            })
            if rmin > best_3["r_min"]:
                best_3 = {
                    "r_min": rmin,
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
            rmin = (min(rt, rg)
                    if not np.isnan(rg)
                    else rt)
            results3.append({
                "pos": pos,
                "neg": f"{n1}+{n2}",
                "rt": rt, "rg": rg,
                "rmin": rmin,
            })
            if rmin > best_3["r_min"]:
                best_3 = {
                    "r_min": rmin,
                    "panel": ([pos],
                               [n1, n2]),
                }

    results3.sort(key=lambda x: -(
        x["rmin"]
        if not np.isnan(x["rmin"])
        else 0))

    log(f"  {'Pos':>18} {'Neg':>18}"
        f" {'r_TCGA':>8} {'r_GEO':>7}"
        f" {'min_r':>7}")
    log(f"  {'-'*18} {'-'*18}"
        f" {'-'*8} {'-'*7} {'-'*7}")
    for row in results3[:15]:
        rg_s = (f"{row['rg']:>7.4f}"
                if not np.isnan(row['rg'])
                else f"{'NA':>7}")
        rmin_s = (f"{row['rmin']:>7.4f}"
                  if not np.isnan(
                      row['rmin'])
                  else f"{'NA':>7}")
        log(f"  {row['pos']:>18}"
            f" {row['neg']:>18}"
            f" {row['rt']:>8.4f}"
            f" {rg_s}"
            f" {rmin_s}")

    log("")
    log("  4-gene panels (top 3-gene + 1):")

    best_4   = {"r_min": 0, "panel": None}
    results4 = []

    if best_3["panel"]:
        bp_pos, bp_neg = best_3["panel"]
        # add one more pos
        for add_p in PANEL_CANDIDATES_POS:
            if add_p in bp_pos:
                continue
            rt = score_panel(
                bp_pos + [add_p], bp_neg,
                expr_t, d_t, t_cols_t)
            rg = (score_panel(
                bp_pos + [add_p], bp_neg,
                expr_g, d_g, t_cols_g)
                  if d_g is not None
                  else np.nan)
            rmin = (min(rt, rg)
                    if not np.isnan(rg)
                    else rt)
            results4.append({
                "pos": "+".join(
                    bp_pos + [add_p]),
                "neg": "+".join(bp_neg),
                "rt": rt, "rg": rg,
                "rmin": rmin,
            })
            if rmin > best_4["r_min"]:
                best_4 = {
                    "r_min": rmin,
                    "panel": (
                        bp_pos + [add_p],
                        bp_neg),
                }
        # add one more neg
        for add_n in PANEL_CANDIDATES_NEG:
            if add_n in bp_neg:
                continue
            rt = score_panel(
                bp_pos, bp_neg + [add_n],
                expr_t, d_t, t_cols_t)
            rg = (score_panel(
                bp_pos, bp_neg + [add_n],
                expr_g, d_g, t_cols_g)
                  if d_g is not None
                  else np.nan)
            rmin = (min(rt, rg)
                    if not np.isnan(rg)
                    else rt)
            results4.append({
                "pos": "+".join(bp_pos),
                "neg": "+".join(
                    bp_neg + [add_n]),
                "rt": rt, "rg": rg,
                "rmin": rmin,
            })
            if rmin > best_4["r_min"]:
                best_4 = {
                    "r_min": rmin,
                    "panel": (
                        bp_pos,
                        bp_neg + [add_n]),
                }

    results4.sort(key=lambda x: -(
        x["rmin"]
        if not np.isnan(x["rmin"])
        else 0))

    log(f"  {'Pos':>22} {'Neg':>22}"
        f" {'r_TCGA':>8} {'r_GEO':>7}"
        f" {'min_r':>7}")
    log(f"  {'-'*22} {'-'*22}"
        f" {'-'*8} {'-'*7} {'-'*7}")
    for row in results4[:15]:
        rg_s = (f"{row['rg']:>7.4f}"
                if not np.isnan(row['rg'])
                else f"{'NA':>7}")
        rmin_s = (f"{row['rmin']:>7.4f}"
                  if not np.isnan(
                      row['rmin'])
                  else f"{'NA':>7}")
        log(f"  {row['pos']:>22}"
            f" {row['neg']:>22}"
            f" {row['rt']:>8.4f}"
            f" {rg_s}"
            f" {rmin_s}")

    # Summary
    log("")
    log("  BEST PANELS FOUND:")
    for label_b, best in [
        ("2-gene", best_2),
        ("3-gene", best_3),
        ("4-gene", best_4),
    ]:
        if best["panel"]:
            pos_g, neg_g = best["panel"]
            log(f"  {label_b}: "
                f"Pos={pos_g}  "
                f"Neg={neg_g}  "
                f"r_min={best['r_min']:.4f}")
            if best["r_min"] >= 0.85:
                log(f"    TARGET ACHIEVED ✓")
            elif best["r_min"] >= 0.80:
                log(f"    Near target (~)")
            else:
                log(f"    Below target ✗")

    # S3-P6 verdict
    best_all = max(
        [best_2, best_3, best_4],
        key=lambda x: x["r_min"])
    log("")
    if best_all["r_min"] >= 0.85:
        log("  S3-P6 CONFIRMED: "
            "r >= 0.85 BOTH datasets ✓")
    else:
        log("  S3-P6 NOT CONFIRMED: "
            f"best r_min = "
            f"{best_all['r_min']:.4f}")

    # Save all
    pd.DataFrame(results).to_csv(
        os.path.join(S3_DIR,
                     "panel_2gene.csv"),
        index=False)
    pd.DataFrame(results3).to_csv(
        os.path.join(S3_DIR,
                     "panel_3gene.csv"),
        index=False)
    pd.DataFrame(results4).to_csv(
        os.path.join(S3_DIR,
                     "panel_4gene.csv"),
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
            index=t_cols
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
            "TIER_1" if abs(row.r) >= 0.40
            else "TIER_2"
            if abs(row.r) >= 0.25
            else "TIER_3"
            if abs(row.r) >= 0.10
            else "AGNOSTIC")
        log(f"  {row.gene:<10} "
            f"{row.r:>+10.4f}  "
            f"{fmt_p(row.p):>10}  {tier}")

    # S3-P7 verdict
    axl = df[df.gene == "AXL"]
    if len(axl) > 0:
        r_axl = float(axl.iloc[0].r)
        log("")
        log(f"  S3-P7: AXL r = {r_axl:+.4f}")
        if r_axl > 0.25:
            log("  CONFIRMED: AXL depth-positive ✓")
            log("  Cabozantinib benefits deep"
                " ccRCC via AXL arm")
        elif r_axl > 0:
            log("  PARTIAL: AXL trending positive"
                " but < +0.25")
        else:
            log("  WRONG: AXL not depth-positive ✗")

    return df

# ═══════════════════════════════════════════════════════
# FIGURE
# ═══════════════════════════════════════════════════════

def generate_figure(depth_t, emt_df_t,
                    chrom_df_t, cabo_df_t,
                    best2, best3, best4,
                    lipid_df_t,
                    score_a, score_b):
    log("")
    log("Generating Script 3 figure...")

    fig = plt.figure(figsize=(18, 12))
    gs  = gridspec.GridSpec(
        3, 3, figure=fig,
        hspace=0.55, wspace=0.42)

    ax = [fig.add_subplot(gs[r, c])
          for r in range(3)
          for c in range(3)]

    C = ["#e74c3c", "#2ecc71", "#2980b9",
         "#8e44ad", "#e67e22", "#16a085",
         "#c0392b", "#7f8c8d", "#1abc9c"]

    # A — EMT depth correlations
    if emt_df_t is not None \
            and not emt_df_t.empty:
        df_e = emt_df_t.sort_values("r")
        cols_e = [C[0] if r > 0
                  else C[1]
                  for r in df_e.r.values]
        ax[0].barh(df_e.gene.values,
                   df_e.r.values,
                   color=cols_e,
                   edgecolor="black",
                   linewidth=0.3)
        ax[0].axvline(0, color="black",
                      linewidth=0.8)
        ax[0].set_title(
            "A — EMT circuit r(depth)",
            fontsize=9)
        ax[0].set_xlabel("r", fontsize=8)
        ax[0].tick_params(axis="y",
                          labelsize=6)

    # B — Chromatin depth correlations
    if chrom_df_t is not None \
            and not chrom_df_t.empty:
        df_c = chrom_df_t.sort_values("r")
        cols_c = [C[0] if r > 0
                  else C[1]
                  for r in df_c.r.values]
        ax[1].barh(df_c.gene.values,
                   df_c.r.values,
                   color=cols_c,
                   edgecolor="black",
                   linewidth=0.3)
        ax[1].axvline(0, color="black",
                      linewidth=0.8)
        ax[1].set_title(
            "B — Chromatin r(depth)",
            fontsize=9)
        ax[1].set_xlabel("r", fontsize=8)
        ax[1].tick_params(axis="y",
                          labelsize=6)

    # C — Cabozantinib geometry
    if cabo_df_t is not None \
            and not cabo_df_t.empty:
        df_cab = cabo_df_t.sort_values("r")
        cols_cab = [C[0] if r > 0
                    else C[1]
                    for r in
                    df_cab.r.values]
        ax[2].barh(df_cab.gene.values,
                   df_cab.r.values,
                   color=cols_cab,
                   edgecolor="black",
                   linewidth=0.3)
        ax[2].axvline(0, color="black",
                      linewidth=0.8)
        ax[2].axvline(0.25, color="grey",
                      linewidth=0.6,
                      linestyle=":")
        ax[2].set_title(
            "C — Cabozantinib panel r(depth)",
            fontsize=9)
        ax[2].set_xlabel("r", fontsize=8)
        ax[2].tick_params(axis="y",
                          labelsize=6)

    # D — Lipid TF drivers
    if lipid_df_t is not None \
            and not lipid_df_t.empty \
            and "r_SCD" in lipid_df_t.columns:
        df_l = lipid_df_t.dropna(
            subset=["r_SCD"]
        ).sort_values("r_SCD", ascending=False)
        cols_l = [C[2]] * len(df_l)
        ax[3].barh(df_l.tf.values,
                   df_l.r_SCD.values,
                   color=cols_l,
                   edgecolor="black",
                   linewidth=0.3)
        ax[3].axvline(0, color="black",
                      linewidth=0.8)
        ax[3].set_title(
            "D — r(TF, SCD) — lipid driver",
            fontsize=9)
        ax[3].set_xlabel("r(TF, SCD)",
                         fontsize=8)
        ax[3].tick_params(axis="y",
                          labelsize=7)

    # E — Sub-axis scatter
    if (score_a is not None and
            score_b is not None):
        ax[4].scatter(
            score_a.values,
            score_b.values,
            alpha=0.4, s=8,
            c=C[2])
        ax[4].set_xlabel(
            "Depth_A (transport)",
            fontsize=8)
        ax[4].set_ylabel(
            "Depth_B (metabolic)",
            fontsize=8)
        ax[4].set_title(
            "E — PT sub-axes scatter",
            fontsize=9)

    # F — Panel r summary
    panels = []
    for best, label_b in [
        (best2, "2-gene"),
        (best3, "3-gene"),
        (best4, "4-gene"),
    ]:
        if best and best.get("panel"):
            panels.append((
                label_b, best["r_min"]))
    if panels:
        names_p = [p[0] for p in panels]
        vals_p  = [abs(p[1]) for p in panels]
        cols_p  = [C[1] if v >= 0.85
                   else C[4] if v >= 0.80
                   else C[0]
                   for v in vals_p]
        ax[5].bar(names_p, vals_p,
                  color=cols_p,
                  edgecolor="black",
                  linewidth=0.5)
        ax[5].axhline(0.85, color="green",
                      linewidth=1.5,
                      linestyle="--",
                      label="target=0.85")
        ax[5].set_ylim(0, 1)
        ax[5].legend(fontsize=7)
        ax[5].set_title(
            "F — Panel r_min(TCGA,GEO)",
            fontsize=9)
        ax[5].set_ylabel("|r|", fontsize=8)

    # G-I — text summaries
    for i, (title, lines) in enumerate([
        ("G — Predictions",
         ["S3-P1 PT axes separable",
          "S3-P2 SREBF1>MYC for SCD",
          "S3-P3 CDH1 DOWN r<-0.25",
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
          "  → FAP-ADC established stroma",
          "Combination: all 3 walls"]),
        ("I — Novel (pre-lit)",
         ["MYC drives GLUT1 variation",
          "FAP-CAF self-sustaining",
          "CD274⊥FOXP3 independent",
          "Depth predicts OS p=0.0001",
          "4-gene panel: GLUT1/VIM",
          "/CA9/FBP1 r=0.888 GEO"]),
    ]):
        ax[6 + i].axis("off")
        ax[6 + i].set_title(title,
                             fontsize=9)
        for j, line in enumerate(lines):
            ax[6 + i].text(
                0.03, 0.88 - j * 0.13,
                line, fontsize=7,
                transform=ax[6 + i].transAxes)

    fig.suptitle(
        "ccRCC False Attractor — Script 3\n"
        "Sub-axes / EMT / Chromatin / "
        "Panel / Cabozantinib",
        fontsize=11, fontweight="bold")

    out = os.path.join(S3_DIR,
                       "figure_s3.png")
    fig.savefig(out, dpi=150,
                bbox_inches="tight")
    plt.close(fig)
    log(f"  Figure: {out}")

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
    log("  S3-P1  r(Depth_A,Depth_B) < 0.80")
    log("  S3-P2  SREBF1 > MYC for SCD")
    log("  S3-P3  CDH1 r < -0.25")
    log("  S3-P4  BAP1 r < -0.20")
    log("  S3-P5  PBRM1 r > +0.10")
    log("  S3-P6  panel r >= 0.85 both")
    log("  S3-P7  AXL r > +0.25")
    log("")

    # Load data
    depth_t = load_depth("tcga")
    depth_g = load_depth("geo")
    expr_t, t_cols_t = parse_tcga()
    expr_g, t_cols_g = parse_geo()

    # ── OBJ-1 ───────────────────────────
    score_a_t, score_b_t, r_ab_t = \
        pt_subaxis(expr_t, t_cols_t,
                   depth_t, "TCGA")
    if expr_g is not None:
        pt_subaxis(expr_g, t_cols_g,
                   depth_g, "GEO")

    # ── OBJ-2 ───────────────────────────
    lipid_t = lipid_tf_driver(
        expr_t, t_cols_t, depth_t, "TCGA")
    if expr_g is not None:
        lipid_tf_driver(
            expr_g, t_cols_g, depth_g, "GEO")

    # ── OBJ-3 ───────────────────────────
    emt_t = emt_circuit(
        expr_t, t_cols_t, depth_t, "TCGA")
    emt_g = None
    if expr_g is not None:
        emt_g = emt_circuit(
            expr_g, t_cols_g, depth_g, "GEO")

    # ── OBJ-4/5 ─────────────────────────
    chrom_t = chromatin_depth(
        expr_t, t_cols_t, depth_t, "TCGA")
    chrom_g = None
    if expr_g is not None:
        chrom_g = chromatin_depth(
            expr_g, t_cols_g, depth_g, "GEO")

    # ── OBJ-6 ───────────────────────────
    best2, best3, best4 = panel_optimise(
        expr_t, depth_t, t_cols_t,
        expr_g, depth_g, t_cols_g)

    # ── OBJ-7 ───────────────────────────
    cabo_t = cabozantinib_geometry(
        expr_t, t_cols_t, depth_t, "TCGA")
    cabo_g = None
    if expr_g is not None:
        cabo_g = cabozantinib_geometry(
            expr_g, t_cols_g, depth_g, "GEO")

    # ── Figure ──────────────────────────
    generate_figure(
        depth_t, emt_t, chrom_t, cabo_t,
        best2, best3, best4, lipid_t,
        score_a_t, score_b_t)

    # ── Summary ─────────────────────────
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
    log("NEXT: paste full output.")
    log("Then write document 94c-pre.")
    log("Then run literature check (94c).")

    write_log()

if __name__ == "__main__":
    main()
