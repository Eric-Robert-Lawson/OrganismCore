"""
chRCC FALSE ATTRACTOR — SCRIPT 5
OrganismCore | Document 96e | 2026-03-02
Author: Eric Robert Lawson

GEOMETRIC CHARACTERISATION — COMPLETION PASS
=============================================
Geometry-first. No literature. No priors.

Column map confirmed from diagnostic:
  reversal_vector  : index='gene', gap col='expr_delta', loading='loading'
  pc_loadings      : index=gene (unnamed), cols PC1..PC5
  pc_scores        : index=sample (unnamed), cols PC1..PC5 + sample_class
  depth_scores     : index='sample_id', cols 'depth', 'class'
  top200_attractor : index='gene', cols r_depth/p_depth/n_mean/t_mean
  partial_corr     : index=None (gene names), 100×100 matrix
  gmm4_clusters    : index='sample', cols label/cluster/PC1/PC2/depth

What this script resolves:
  S1 — Full PC2 depth-residualisation for all 15244 genes
  S2 — Extended partial correlation across all Tier1 genes
       Tier3 revalidation with wider co-regulation window
  S3 — Neighbourhood mapping of Tier3 genes
  S4 — PC2-genuine manifold placement + verification of known genes
  S5 — Depth heterogeneity (GMM Cluster 2 vs 3) for Tier3 genes
  S6 — Synthesis and literature readiness verdict

Barcode format (confirmed from pc_scores index):
  TCGA-KI-{n:04d}-X{n:02d}-{code}{letter}-01-01
  parts[4][:2] == '01' → chRCC
  parts[4][:2] == '02' → oncocytoma
  parts[4][:2] == '11' → normal
  (confirmed from sample_class col in pc_scores and label col in gmm4_clusters)
"""

import os
import warnings
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, mannwhitneyu
from sklearn.linear_model import LinearRegression
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

warnings.filterwarnings("ignore")

# ── paths ──────────────────────────────────────────────────────────────────────
BASE_DIR = "./chrcc_false_attractor/"
S1_DIR   = os.path.join(BASE_DIR, "results_s1/")
S3_DIR   = os.path.join(BASE_DIR, "results_s3/")
S4_DIR   = os.path.join(BASE_DIR, "results_s4/")
S5_DIR   = os.path.join(BASE_DIR, "results_s5/")
LOG_FILE = os.path.join(S5_DIR,   "s5_log.txt")

KICH_EXPR  = os.path.join(BASE_DIR, "TCGA_KICH_HiSeqV2.gz")
DEPTH_FILE = os.path.join(S1_DIR,  "depth_scores.csv")
PC_SCORES  = os.path.join(S3_DIR,  "pc_scores.csv")
PC_LOAD    = os.path.join(S3_DIR,  "pc_loadings.csv")
REV_VEC    = os.path.join(S3_DIR,  "reversal_vector.csv")
REV_MIN    = os.path.join(S3_DIR,  "reversal_min_set.csv")
TOP200     = os.path.join(S3_DIR,  "top200_attractor.csv")
BOT200     = os.path.join(S3_DIR,  "bot200_normal.csv")
PCORR      = os.path.join(S3_DIR,  "partial_corr.csv")
GMM_FILE   = os.path.join(S4_DIR,  "gmm4_clusters.csv")

# Known PC2-genuine candidates from Script 4 analysis
PC2_GENUINE_KNOWN = ["TMEM52B", "NOX4", "DDIT4L"]

os.makedirs(S5_DIR, exist_ok=True)

# ── logging ────────────────────────────────────────────────────────────────────
log_lines = []

def log(msg=""):
    print(msg)
    log_lines.append(str(msg))

def write_log():
    with open(LOG_FILE, "w") as f:
        f.write("\n".join(log_lines))

# ── helpers ────────────────────────────────────────────────────────────────────
def safe_r(x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    mask = np.isfinite(x) & np.isfinite(y)
    if mask.sum() < 5:
        return np.nan, np.nan
    r, p = pearsonr(x[mask], y[mask])
    return float(r), float(p)

def safe_mwu(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    a = a[np.isfinite(a)]
    b = b[np.isfinite(b)]
    if len(a) < 3 or len(b) < 3:
        return np.nan
    _, p = mannwhitneyu(a, b, alternative="two-sided")
    return float(p)

def residualise(y, x):
    """Return residuals of y after regressing out x (both 1-D arrays)."""
    y = np.asarray(y, dtype=float)
    x = np.asarray(x, dtype=float)
    mask = np.isfinite(y) & np.isfinite(x)
    if mask.sum() < 5:
        return np.full(len(y), np.nan, dtype=float)
    reg   = LinearRegression().fit(x[mask].reshape(-1, 1), y[mask])
    resid = np.full(len(y), np.nan, dtype=float)
    resid[mask] = y[mask] - reg.predict(x[mask].reshape(-1, 1))
    return resid

def norm01(a):
    a  = np.asarray(a, dtype=float)
    mn = np.nanmin(a)
    mx = np.nanmax(a)
    if mx == mn:
        return np.zeros_like(a)
    return (a - mn) / (mx - mn)

def fmt_p(p):
    if p is None or (isinstance(p, float) and np.isnan(p)):
        return "NA"
    if p < 0.001:
        return f"{p:.2e}"
    return f"{p:.4f}"

# ── barcode classification ─────────────────────────────────────────────────────
# Confirmed format: TCGA-KI-{n:04d}-X{n:02d}-{code}{letter}-01-01
# parts[4][:2]:  '01'=chRCC  '02'=oncocytoma  '11'=normal
def classify_bc(bc):
    parts = str(bc).split("-")
    if len(parts) < 5:
        return "unknown"
    code = parts[4][:2]
    if code == "11":
        return "normal"
    if code == "01":
        return "chrcc"
    if code == "02":
        return "onco"
    return "other"

def is_tumour(bc):
    return classify_bc(bc) in ("chrcc", "onco")

def is_normal(bc):
    return classify_bc(bc) == "normal"

# ── data loading ───────────────────────────────────────────────────────────────
def load_data():
    log("=" * 62)
    log("DATA LOAD")
    log("=" * 62)

    # expression
    raw = pd.read_csv(KICH_EXPR, sep="\t", index_col=0, compression="gzip")
    raw = raw.T
    log(f"  Expression matrix: {raw.shape[1]} genes × {raw.shape[0]} samples")

    # classify
    t_cols   = [c for c in raw.index if is_tumour(c)]
    n_cols   = [c for c in raw.index if is_normal(c)]
    chr_cols = [c for c in raw.index if classify_bc(c) == "chrcc"]
    onc_cols = [c for c in raw.index if classify_bc(c) == "onco"]
    log(f"  chRCC={len(chr_cols)}  oncocytoma={len(onc_cols)}  "
        f"normal={len(n_cols)}")

    # depth — confirmed col name: 'depth'
    depth_df = pd.read_csv(DEPTH_FILE, index_col=0)
    depth_col = "depth" if "depth" in depth_df.columns else depth_df.columns[0]
    depth = depth_df[depth_col]
    log(f"  Depth scores: {len(depth)}  (col='{depth_col}')")

    # pc scores — confirmed: index unnamed, cols PC1..PC5 + sample_class
    pcs = pd.read_csv(PC_SCORES, index_col=0)
    pc1 = pcs["PC1"]
    pc2 = pcs["PC2"]
    log(f"  PC scores: {pcs.shape}")

    # pc loadings — confirmed: index unnamed (gene), cols PC1..PC5
    load_df = pd.read_csv(PC_LOAD, index_col=0)
    log(f"  PC loadings: {load_df.shape}")

    # reversal vector — confirmed: index='gene', gap col='expr_delta'
    rev_vec = pd.read_csv(REV_VEC, index_col=0)
    log(f"  Reversal vector: {len(rev_vec)} genes  "
        f"cols={list(rev_vec.columns)}")

    # reversal min set
    rev_min = pd.read_csv(REV_MIN, index_col=0)
    log(f"  Reversal min set: {len(rev_min)} genes")

    # top200 / bot200
    top200 = pd.read_csv(TOP200, index_col=0)
    bot200 = pd.read_csv(BOT200, index_col=0)
    log(f"  Top200 attractor: {len(top200)}")
    log(f"  Bot200 normal:    {len(bot200)}")

    # partial corr — confirmed: index=None (gene names as index col 0)
    pcorr = pd.read_csv(PCORR, index_col=0)
    log(f"  Partial corr: {pcorr.shape}  "
        f"index[:3]={list(pcorr.index[:3])}")

    # gmm clusters — confirmed: index='sample', cols label/cluster/PC1/PC2/depth
    gmm_df = pd.read_csv(GMM_FILE, index_col=0)
    log(f"  GMM clusters: {gmm_df.shape}")

    return (raw, t_cols, n_cols, chr_cols, onc_cols,
            depth, pc1, pc2, load_df,
            rev_vec, rev_min, top200, bot200, pcorr, gmm_df)


# ── tier reconstruction ────────────────────────────────────────────────────────
def reconstruct_tiers(rev_vec, top200, pcorr, load_df):
    """
    Rebuild Tier1 / Tier2 / Tier3 using confirmed column names:
      rev_vec gap col  = 'expr_delta'   (values -0.90 to +0.90)
      rev_vec load col = 'loading'      (values -0.0166 to +0.0166)
      top200  index    = gene names
      pcorr   index    = gene names (index_col=0)
      load_df index    = gene names, col 'PC1'
    """
    # confirmed gap column
    gap_col   = "expr_delta"
    load_col  = "loading"

    # sanity check
    assert gap_col  in rev_vec.columns, f"Missing col '{gap_col}' in rev_vec"
    assert load_col in rev_vec.columns, f"Missing col '{load_col}' in rev_vec"

    rv         = rev_vec.copy()
    q75        = float(np.nanpercentile(rv[load_col].abs(), 75))

    # Tier1: |expr_delta| > 0.50 AND |loading| >= Q75
    tier1_mask  = (rv[gap_col].abs() > 0.50) & (rv[load_col].abs() >= q75)
    tier1_genes = set(rv.index[tier1_mask])

    # Tier2: Tier1 ∩ top200 attractor genes
    tier2_genes = tier1_genes & set(top200.index)

    # Tier3: Tier2 ∩ partial_corr genes (the 100-gene co-reg window)
    # pcorr index confirmed as gene names
    tier3_genes = tier2_genes & set(pcorr.index)

    return tier1_genes, tier2_genes, tier3_genes, rv, gap_col, load_col, q75


# ── S1: Full PC2 depth-residualisation ────────────────────────────────────────
def s1_full_pc2_residualisation(raw, t_cols, n_cols, depth, pc2):
    log()
    log("=" * 62)
    log("S1 — FULL PC2 DEPTH-RESIDUALISATION")
    log("=" * 62)

    all_cols = [c for c in (t_cols + n_cols) if c in raw.index]
    expr     = raw.loc[all_cols]
    pc2_arr  = pc2.reindex(all_cols).values.astype(float)
    dep_arr  = depth.reindex(all_cols).values.astype(float)

    n_t = sum(1 for c in all_cols if is_tumour(c))
    n_n = sum(1 for c in all_cols if is_normal(c))
    log(f"  Samples: {len(all_cols)}  (tumour={n_t}, normal={n_n})")

    # residualise PC2 on depth once
    pc2_resid = residualise(pc2_arr, dep_arr)

    genes = [g for g in expr.columns
             if expr[g].notna().sum() >= 10]
    log(f"  Genes with sufficient data: {len(genes)}")

    rows = []
    for g in genes:
        g_arr    = expr[g].values.astype(float)
        raw_r,  raw_p  = safe_r(g_arr, pc2_arr)
        g_resid  = residualise(g_arr, dep_arr)
        clean_r, clean_p = safe_r(g_resid, pc2_resid)
        delta_r  = (float(clean_r) - float(raw_r)) \
                   if not (np.isnan(clean_r) or np.isnan(raw_r)) else np.nan
        rows.append({
            "gene"            : g,
            "raw_r"           : round(float(raw_r),   4) if not np.isnan(raw_r)   else np.nan,
            "raw_p"           : float(raw_p)               if not np.isnan(raw_p)   else np.nan,
            "clean_r"         : round(float(clean_r), 4) if not np.isnan(clean_r) else np.nan,
            "clean_p"         : float(clean_p)             if not np.isnan(clean_p) else np.nan,
            "delta_r"         : round(delta_r, 4)          if not np.isnan(delta_r) else np.nan,
            "depth_confounded": bool(not np.isnan(delta_r) and abs(delta_r) >= 0.20),
        })

    pc2_full = pd.DataFrame(rows)

    # sort by |clean_r| descending
    pc2_full["_abs_clean"] = pc2_full["clean_r"].abs()
    pc2_full = pc2_full.sort_values("_abs_clean", ascending=False)\
                       .drop(columns="_abs_clean")\
                       .reset_index(drop=True)

    pc2_full.to_csv(os.path.join(S5_DIR, "pc2_residualised_full.csv"),
                    index=False)

    # top 100: top 50 positive + top 50 negative clean_r
    valid = pc2_full.dropna(subset=["clean_r"])
    sorted_asc  = valid.sort_values("clean_r", ascending=True)
    sorted_desc = valid.sort_values("clean_r", ascending=False)
    top50_pos   = sorted_desc.head(50)
    top50_neg   = sorted_asc.head(50)
    pc2_top100  = pd.concat([top50_pos, top50_neg]).drop_duplicates("gene")
    pc2_top100.to_csv(os.path.join(S5_DIR, "pc2_clean_top100.csv"),
                      index=False)

    n_conf = int(pc2_full["depth_confounded"].sum())
    pct    = 100 * n_conf / max(len(pc2_full), 1)
    log(f"  Genes evaluated: {len(pc2_full)}")
    log(f"  Depth-confounded (|Δr|>=0.20): {n_conf} ({pct:.1f}%)")

    log()
    log("  TOP 20 PC2-GENUINE (positive pole — chRCC side):")
    log(f"  {'Gene':<20} {'raw_r':>8} {'clean_r':>8} "
        f"{'delta_r':>8} {'clean_p':>12}")
    log("  " + "-" * 62)
    for _, row in top50_pos.head(20).iterrows():
        log(f"  {row['gene']:<20} {row['raw_r']:>+8.4f} "
            f"{row['clean_r']:>+8.4f} {row['delta_r']:>+8.4f} "
            f"{fmt_p(row['clean_p']):>12}")

    log()
    log("  TOP 20 PC2-GENUINE (negative pole — oncocytoma side):")
    log(f"  {'Gene':<20} {'raw_r':>8} {'clean_r':>8} "
        f"{'delta_r':>8} {'clean_p':>12}")
    log("  " + "-" * 62)
    for _, row in top50_neg.head(20).iterrows():
        log(f"  {row['gene']:<20} {row['raw_r']:>+8.4f} "
            f"{row['clean_r']:>+8.4f} {row['delta_r']:>+8.4f} "
            f"{fmt_p(row['clean_p']):>12}")

    log()
    log("  KNOWN PC2-GENUINE GENE CHECK (from Script 4):")
    log(f"  {'Gene':<20} {'raw_r':>8} {'clean_r':>8} "
        f"{'delta_r':>8} {'confounded':>12}")
    log("  " + "-" * 62)
    for g in PC2_GENUINE_KNOWN:
        hit = pc2_full[pc2_full["gene"] == g]
        if len(hit) == 0:
            log(f"  {g:<20}  not in matrix")
            continue
        r = hit.iloc[0]
        log(f"  {r['gene']:<20} {r['raw_r']:>+8.4f} "
            f"{r['clean_r']:>+8.4f} {r['delta_r']:>+8.4f} "
            f"{'YES' if r['depth_confounded'] else 'no':>12}")

    return pc2_full, pc2_top100


# ── S2: Extended partial correlation (Tier 1 window) ──────────────────────────
def s2_extended_partial_corr(raw, t_cols, n_cols, tier1_genes,
                              tier3_genes, rv, gap_col, load_col):
    log()
    log("=" * 62)
    log("S2 — EXTENDED PARTIAL CORRELATION (Tier1 window)")
    log("=" * 62)

    all_cols   = [c for c in (t_cols + n_cols) if c in raw.index]
    expr       = raw.loc[all_cols]
    tier1_list = sorted(tier1_genes & set(expr.columns))
    n          = len(tier1_list)
    log(f"  Tier1 genes in expression matrix: {n}")
    log(f"  Computing {n}×{n} correlation matrix...")

    matrix  = np.full((n, n), np.nan)
    expr_t  = expr[tier1_list].values.astype(float)

    for i in range(n):
        matrix[i, i] = 1.0
        for j in range(i + 1, n):
            r, _ = safe_r(expr_t[:, i], expr_t[:, j])
            matrix[i, j] = r
            matrix[j, i] = r

    corr_df = pd.DataFrame(matrix, index=tier1_list, columns=tier1_list)
    corr_df.to_csv(os.path.join(S5_DIR, "partial_corr_tier1.csv"))
    log(f"  Saved: partial_corr_tier1.csv  ({corr_df.shape})")

    # revalidate Tier3
    log()
    log("  TIER3 REVALIDATION (n partners |r|>=0.50 in Tier1 window):")
    log(f"  {'Gene':<20} {'n_partners':>12} {'gap':>9} "
        f"{'loading':>10} {'stable':>8}")
    log("  " + "-" * 65)

    reval_rows = []
    for g in sorted(tier3_genes):
        if g not in corr_df.index:
            reval_rows.append({
                "gene": g, "n_partners_ext": 0,
                "gap": np.nan, "loading": np.nan,
                "stable": False, "note": "not in Tier1 matrix"
            })
            log(f"  {g:<20}  not in Tier1 matrix")
            continue
        row_r      = corr_df.loc[g].drop(g)
        n_partners = int((row_r.abs() >= 0.50).sum())
        gap_val    = rv.loc[g, gap_col]  if g in rv.index else np.nan
        load_val   = rv.loc[g, load_col] if g in rv.index else np.nan
        stable     = n_partners >= 3
        reval_rows.append({
            "gene"          : g,
            "n_partners_ext": n_partners,
            "gap"           : round(float(gap_val),  4) if not np.isnan(gap_val)  else np.nan,
            "loading"       : round(float(load_val), 5) if not np.isnan(load_val) else np.nan,
            "stable"        : stable,
            "note"          : "",
        })
        flag = "STABLE" if stable else "UNSTABLE"
        log(f"  {g:<20} {n_partners:>12} "
            f"{gap_val:>+9.4f} {load_val:>+10.5f} {flag:>8}")

    reval_df     = pd.DataFrame(reval_rows)
    reval_df.to_csv(os.path.join(S5_DIR, "tier3_revalidated.csv"), index=False)

    stable_tier3   = set(reval_df.loc[reval_df["stable"] == True, "gene"])
    unstable_tier3 = tier3_genes - stable_tier3

    log()
    log(f"  Stable Tier3   ({len(stable_tier3)}): {sorted(stable_tier3)}")
    log(f"  Unstable Tier3 ({len(unstable_tier3)}): {sorted(unstable_tier3)}")
    if unstable_tier3:
        log("  Unstable genes had <3 partners in wider Tier1 window.")
        log("  Their Tier3 membership was an artefact of the 100-gene window.")

    return corr_df, reval_df, stable_tier3, tier1_list


# ── S3: Neighbourhood mapping ───────���──────────────────────────────────────────
def s3_tier3_neighbourhood(corr_df, tier3_genes, rv, gap_col, load_col):
    log()
    log("=" * 62)
    log("S3 — NEIGHBOURHOOD MAPPING OF TIER3 GENES")
    log("=" * 62)

    tier3_list = sorted(tier3_genes & set(corr_df.index))
    if not tier3_list:
        log("  No Tier3 genes in correlation matrix — skipping.")
        return pd.DataFrame()

    # internal connectivity
    log("  INTERNAL TIER3 CONNECTIVITY (|r|>=0.50):")
    log(f"  {'Gene':<20} {'internal_partners':>20}")
    log("  " + "-" * 42)
    for g in tier3_list:
        others   = [x for x in tier3_list if x != g and x in corr_df.columns]
        internal = sum(1 for x in others
                       if not np.isnan(corr_df.loc[g, x])
                       and abs(corr_df.loc[g, x]) >= 0.50)
        log(f"  {g:<20} {internal:>20}")

    neigh_rows = []
    log()
    log("  TOP 10 NEIGHBOURHOOD PARTNERS PER TIER3 GENE:")

    for g in tier3_list:
        if g not in corr_df.index:
            log(f"  {g}: not in Tier1 matrix")
            continue
        row_r = corr_df.loc[g].drop(g).dropna()
        top10 = row_r.abs().nlargest(10)
        g_gap  = rv.loc[g, gap_col]  if g in rv.index else np.nan
        g_load = rv.loc[g, load_col] if g in rv.index else np.nan
        log()
        log(f"  {g}  gap={g_gap:+.4f}  loading={g_load:+.5f}:")
        log(f"  {'Partner':<22} {'r':>8} {'in_t3':>7} {'partner_gap':>13}")
        log("  " + "-" * 54)
        for partner in top10.index:
            r_val  = corr_df.loc[g, partner]
            in_t3  = partner in tier3_genes
            p_gap  = rv.loc[partner, gap_col] if partner in rv.index else np.nan
            gs     = f"{p_gap:>+13.4f}" if not np.isnan(p_gap) else f"{'NA':>13}"
            log(f"  {partner:<22} {r_val:>+8.4f} "
                f"{'YES' if in_t3 else '':>7} {gs}")
            neigh_rows.append({
                "tier3_gene" : g,
                "partner"    : partner,
                "r"          : round(float(r_val), 4),
                "in_tier3"   : in_t3,
                "partner_gap": round(float(p_gap), 4) if not np.isnan(p_gap)
                               else np.nan,
            })

    log()
    log("  HUB vs PERIPHERY classification (Tier1 network, |r|>=0.50):")
    log(f"  {'Gene':<20} {'n_tier1_partners':>18} {'role':>12}")
    log("  " + "-" * 54)
    for g in tier3_list:
        if g not in corr_df.index:
            continue
        n_p  = int((corr_df.loc[g].drop(g).abs() >= 0.50).sum())
        role = "HUB" if n_p >= 20 else "CONNECTOR" if n_p >= 10 else "PERIPHERAL"
        log(f"  {g:<20} {n_p:>18} {role:>12}")

    neigh_df = pd.DataFrame(neigh_rows)
    neigh_df.to_csv(os.path.join(S5_DIR, "tier3_neighbourhood.csv"),
                    index=False)
    return neigh_df


# ── S4: PC2-genuine manifold placement ────────────────────────────────────────
def s4_pc2_genuine_manifold(raw, t_cols, n_cols, pc1, pc2, depth, pc2_full):
    log()
    log("=" * 62)
    log("S4 — PC2-GENUINE MANIFOLD PLACEMENT")
    log("=" * 62)

    all_cols = [c for c in (t_cols + n_cols) if c in raw.index]
    expr     = raw.loc[all_cols]
    pc1_arr  = pc1.reindex(all_cols).values.astype(float)
    pc2_arr  = pc2.reindex(all_cols).values.astype(float)
    dep_arr  = depth.reindex(all_cols).values.astype(float)

    # PC2-genuine: |clean_r|>=0.40 AND |delta_r|<0.20
    if len(pc2_full) > 0:
        genuine_mask  = (pc2_full["clean_r"].abs() >= 0.40) & \
                        (pc2_full["delta_r"].abs() < 0.20)
        genuine_genes = pc2_full.loc[genuine_mask, "gene"].tolist()
    else:
        genuine_genes = []

    # always include Script 4 known genes
    for g in PC2_GENUINE_KNOWN:
        if g not in genuine_genes:
            genuine_genes.append(g)

    log(f"  PC2-genuine candidates "
        f"(|clean_r|>=0.40 AND |Δr|<0.20): {len(genuine_genes)}")

    manifold_rows = []
    for g in genuine_genes:
        if g not in expr.columns:
            continue
        g_arr     = expr[g].values.astype(float)
        r_pc1, _  = safe_r(g_arr, pc1_arr)
        r_pc2, _  = safe_r(g_arr, pc2_arr)
        r_dep, _  = safe_r(g_arr, dep_arr)
        dominant  = "PC2" if abs(r_pc2) >= abs(r_dep) else "depth"
        row_match = pc2_full[pc2_full["gene"] == g] \
                    if len(pc2_full) > 0 else pd.DataFrame()
        clean_r   = float(row_match.iloc[0]["clean_r"]) \
                    if len(row_match) > 0 else np.nan
        manifold_rows.append({
            "gene"    : g,
            "r_pc1"   : round(float(r_pc1), 4),
            "r_pc2"   : round(float(r_pc2), 4),
            "r_depth" : round(float(r_dep), 4),
            "clean_r" : round(clean_r, 4) if not np.isnan(clean_r) else np.nan,
            "dominant": dominant,
        })

    manifold_df = pd.DataFrame(manifold_rows)
    manifold_df.to_csv(os.path.join(S5_DIR, "pc2_genuine_manifold.csv"),
                       index=False)

    log()
    log("  PC2-GENUINE MANIFOLD VERIFICATION:")
    log(f"  {'Gene':<20} {'r_pc1':>7} {'r_pc2':>7} "
        f"{'r_depth':>8} {'clean_r':>8} {'dominant':>10}")
    log("  " + "-" * 66)
    for _, row in manifold_df.iterrows():
        log(f"  {row['gene']:<20} {row['r_pc1']:>+7.4f} "
            f"{row['r_pc2']:>+7.4f} {row['r_depth']:>+8.4f} "
            f"{row['clean_r']:>+8.4f} {row['dominant']:>10}")

    confirmed    = manifold_df[manifold_df["dominant"] == "PC2"]
    n_depth_dom  = len(manifold_df) - len(confirmed)
    log()
    log(f"  PC2-dominant (genuine): {len(confirmed)}")
    log(f"  Depth-dominant (confounded): {n_depth_dom}")

    return manifold_df, genuine_genes, pc1_arr, pc2_arr, dep_arr, all_cols


# ── S5: Depth heterogeneity check ─────────────────────────────────────────────
def s5_cluster_depth_check(raw, tier3_genes, depth, gmm_df, t_cols):
    log()
    log("=" * 62)
    log("S5 — DEPTH HETEROGENEITY CHECK (GMM Cluster 2 vs 3)")
    log("=" * 62)

    tier3_list = sorted(tier3_genes & set(raw.columns))
    if not tier3_list:
        log("  No Tier3 genes in expression matrix — skipping.")
        return pd.DataFrame(), False

    # confirmed: gmm_df has 'cluster' column, index='sample'
    clust2 = [bc for bc in gmm_df.index
              if gmm_df.loc[bc, "cluster"] == 2 and bc in raw.index]
    clust3 = [bc for bc in gmm_df.index
              if gmm_df.loc[bc, "cluster"] == 3 and bc in raw.index]
    log(f"  Cluster2 (shallow tumour): n={len(clust2)}")
    log(f"  Cluster3 (deep tumour):    n={len(clust3)}")

    # fallback if clusters too small
    if len(clust2) < 3 or len(clust3) < 3:
        log("  Cluster sizes < 3 — falling back to depth quantile split")
        dep_t  = depth.reindex(t_cols).dropna().sort_values()
        q33    = dep_t.quantile(0.33)
        q67    = dep_t.quantile(0.67)
        clust2 = [c for c in dep_t[dep_t <= q33].index if c in raw.index]
        clust3 = [c for c in dep_t[dep_t >= q67].index if c in raw.index]
        log(f"  Depth fallback: shallow n={len(clust2)}, deep n={len(clust3)}")

    clust_rows   = []
    any_specific = False

    log()
    log("  TIER3 EXPRESSION — CLUSTER 2 vs CLUSTER 3:")
    log(f"  {'Gene':<20} {'C2_mean':>9} {'C3_mean':>9} "
        f"{'MW_p':>10} {'depth_specific':>16}")
    log("  " + "-" * 70)

    for g in tier3_list:
        if g not in raw.columns:
            continue
        c2e    = raw.loc[[b for b in clust2 if b in raw.index], g]\
                    .values.astype(float)
        c3e    = raw.loc[[b for b in clust3 if b in raw.index], g]\
                    .values.astype(float)
        c2m    = float(np.nanmean(c2e))
        c3m    = float(np.nanmean(c3e))
        mwu_p  = safe_mwu(c2e, c3e)
        spec   = bool(not np.isnan(mwu_p) and mwu_p < 0.05)
        if spec:
            any_specific = True
        clust_rows.append({
            "gene"          : g,
            "c2_mean"       : round(c2m, 4),
            "c3_mean"       : round(c3m, 4),
            "mwu_p"         : mwu_p,
            "depth_specific": spec,
        })
        log(f"  {g:<20} {c2m:>+9.4f} {c3m:>+9.4f} "
            f"{fmt_p(mwu_p):>10} "
            f"{'YES' if spec else 'no':>16}")

    clust_df = pd.DataFrame(clust_rows)
    clust_df.to_csv(os.path.join(S5_DIR, "tier3_cluster_comparison.csv"),
                    index=False)

    log()
    if any_specific:
        spec_genes = clust_df.loc[clust_df["depth_specific"], "gene"].tolist()
        log(f"  FINDING: {spec_genes} differ between depth clusters.")
        log("  These targets may be depth-subtype specific.")
    else:
        log("  FINDING: No Tier3 genes differ between depth clusters.")
        log("  All Tier3 targets are GENERAL to the attractor state.")

    return clust_df, any_specific


# ── S6: Synthesis ──────────────────────────────────────────────────────────────
def s6_synthesis(tier1_genes, tier2_genes, tier3_genes,
                 stable_tier3, reval_df,
                 pc2_full, manifold_df, clust_df, any_specific):
    log()
    log("=" * 62)
    log("S6 — SYNTHESIS: GEOMETRY COMPLETION ASSESSMENT")
    log("=" * 62)

    unstable = tier3_genes - stable_tier3

    log()
    log("  1. TIER SUMMARY")
    log(f"     Tier1 (|expr_delta|>0.50 + |loading|>=Q75): "
        f"{len(tier1_genes)}")
    log(f"     Tier2 (Tier1 ∩ top200 attractor):           "
        f"{len(tier2_genes)}")
    log(f"     Tier3 (Tier2 ∩ partial_corr 100-gene):      "
        f"{len(tier3_genes)}")
    log(f"     Stable Tier3 (Tier1 window, >=3 partners):  "
        f"{len(stable_tier3)}")
    if unstable:
        log(f"     Demoted (artefact of 100-gene window): "
            f"{sorted(unstable)}")
    log(f"     DEFINITIVE TIER3: {sorted(stable_tier3)}")

    log()
    log("  2. PC2 CLEAN PROGRAMME")
    if len(pc2_full) > 0:
        n_conf = int(pc2_full["depth_confounded"].sum())
        pct    = 100 * n_conf / max(len(pc2_full), 1)
        log(f"     {pct:.1f}% of genome depth-confounded on PC2 (|Δr|>=0.20)")
    if len(manifold_df) > 0:
        confirmed = manifold_df[manifold_df["dominant"] == "PC2"]
        log(f"     PC2-genuine confirmed: "
            f"{sorted(confirmed['gene'].tolist())}")
    else:
        log("     No manifold data available.")

    log()
    log("  3. DEPTH HETEROGENEITY")
    if any_specific and len(clust_df) > 0:
        spec = clust_df.loc[clust_df["depth_specific"], "gene"].tolist()
        log(f"     Depth-subtype specific: {spec}")
        general = sorted(stable_tier3 - set(spec))
        log(f"     General attractor targets: {general}")
    else:
        log("     All Tier3 targets general to the attractor state.")

    log()
    log("  4. LITERATURE READINESS")
    blockers = []

    if len(stable_tier3) == 0:
        blockers.append("     ✗ No stable Tier3 genes — check tier "
                        "reconstruction parameters.")
    else:
        log(f"     ✓ Stable Tier3 confirmed: {sorted(stable_tier3)}")

    if len(pc2_full) == 0:
        blockers.append("     ✗ PC2 residualisation produced no output.")
    else:
        log("     ✓ PC2 depth-residualisation complete (full genome).")

    if len(manifold_df) > 0:
        confirmed = manifold_df[manifold_df["dominant"] == "PC2"]
        if len(confirmed) > 0:
            log(f"     ✓ PC2-genuine manifold confirmed: "
                f"{sorted(confirmed['gene'].tolist())}")
        else:
            blockers.append("     ✗ No PC2-genuine genes confirmed on manifold.")
    else:
        blockers.append("     ✗ Manifold placement not available.")

    if any_specific and len(clust_df) > 0:
        spec = clust_df.loc[clust_df["depth_specific"], "gene"].tolist()
        log(f"     ⚠ Note: {spec} are depth-subtype specific.")
    else:
        log("     ✓ Tier3 targets depth-independent.")

    log()
    if not blockers:
        log("  ══ GEOMETRY COMPLETE — READY FOR LITERATURE CHECK ══")
        log()
        log("  Entry points for literature:")
        log(f"    A. Definitive Tier3: {sorted(stable_tier3)}")
        log("       Triple-filter validated — attractor-general.")
        if len(manifold_df) > 0:
            confirmed = manifold_df[manifold_df["dominant"] == "PC2"]
            log(f"    B. PC2-genuine discriminants: "
                f"{sorted(confirmed['gene'].tolist())}")
        log()
        log("  Questions geometry produces (not hypothesis-driven):")
        log("    — What regulatory context explains Tier3 co-regulation?")
        log("    — Do PC2-genuine genes mark chRCC vs oncocytoma "
            "cell identity?")
        log("    — Do any Tier3 genes have prior chromatin or metabolic "
            "roles in kidney?")
    else:
        log("  GEOMETRY NOT YET COMPLETE. Blockers:")
        for b in blockers:
            log(b)


# ── Figure ─────────────────────────────────────────────────────────────────────
def make_figure(pc1_arr, pc2_arr, dep_arr, all_cols,
                t_cols, n_cols, pc2_full, manifold_df,
                genuine_genes, corr_df, tier3_genes,
                stable_tier3, clust_df, reval_df, raw):

    fig = plt.figure(figsize=(22, 16))
    gs  = gridspec.GridSpec(2, 3, hspace=0.44, wspace=0.36)

    # ── A: manifold coloured by depth ──────────────────────────────────────
    ax_a = fig.add_subplot(gs[0, 0])
    sc   = ax_a.scatter(pc1_arr, pc2_arr, c=dep_arr, cmap="RdYlBu_r",
                        s=32, alpha=0.85, vmin=0, vmax=1)
    plt.colorbar(sc, ax=ax_a, label="Depth score")
    ax_a.set_xlabel("PC1"); ax_a.set_ylabel("PC2")
    ax_a.set_title("A — Manifold (colour = depth)")

    # ── B: clean_r distribution ────────────────────────────────────────────
    ax_b = fig.add_subplot(gs[0, 1])
    if len(pc2_full) > 0:
        vals = pc2_full["clean_r"].dropna().values
        ax_b.hist(vals, bins=60, color="#4575b4", alpha=0.80,
                  edgecolor="white", linewidth=0.3)
        for thr in (0.40, -0.40):
            ax_b.axvline(thr, color="#d73027", lw=1.5, ls="--",
                         label="|r|=0.40" if thr > 0 else None)
        ax_b.legend(fontsize=8)
    ax_b.set_xlabel("clean_r  (PC2 | depth)")
    ax_b.set_ylabel("Gene count")
    ax_b.set_title("B — PC2 clean correlation (full genome)")

    # ── C: Tier3 neighbourhood heatmap ─────────────────────────────────────
    ax_c = fig.add_subplot(gs[0, 2])
    tier3_list = sorted(tier3_genes & set(corr_df.index)) \
                 if len(corr_df) > 0 else []
    if tier3_list and len(corr_df) > 0:
        partner_pool = set()
        for g in tier3_list:
            if g not in corr_df.index:
                continue
            top6 = corr_df.loc[g].drop(g).dropna().abs().nlargest(6).index
            partner_pool.update(top6.tolist())
        partner_pool -= set(tier3_list)
        partner_list  = sorted(partner_pool)[:12]
        plot_genes    = tier3_list + partner_list
        plot_genes    = [g for g in plot_genes if g in corr_df.index]
        if len(plot_genes) > 1:
            heat = corr_df.loc[plot_genes, plot_genes].astype(float)
            im   = ax_c.imshow(heat.values, aspect="auto", cmap="RdBu_r",
                               vmin=-1, vmax=1, interpolation="nearest")
            ax_c.set_xticks(range(len(plot_genes)))
            ax_c.set_xticklabels(plot_genes, rotation=90, fontsize=6)
            ax_c.set_yticks(range(len(plot_genes)))
            ax_c.set_yticklabels(plot_genes, fontsize=6)
            for idx, g in enumerate(plot_genes):
                col = "#d73027" if g in stable_tier3 else \
                      "#ff8800" if g in tier3_genes  else "black"
                ax_c.get_xticklabels()[idx].set_color(col)
                ax_c.get_yticklabels()[idx].set_color(col)
            plt.colorbar(im, ax=ax_c, label="Pearson r")
    ax_c.set_title("C — Tier3 neighbourhood\n"
                   "(red=stable T3, orange=unstable T3)")

    # ── D: PC2-genuine manifold overlays ───────────────────────────────────
    ax_d = fig.add_subplot(gs[1, 0])
    type_col = ["#2166ac" if is_normal(bc) else "#969696" for bc in all_cols]
    ax_d.scatter(pc1_arr, pc2_arr, c=type_col, s=18, alpha=0.45, zorder=1)
    cmap_t = plt.cm.tab10
    for i, g in enumerate(genuine_genes[:6]):
        if g not in raw.columns:
            continue
        g_vals = raw.loc[all_cols, g].values.astype(float)
        g_norm = norm01(g_vals)
        w      = g_norm
        finite = np.isfinite(pc1_arr) & np.isfinite(pc2_arr) & np.isfinite(w)
        if w[finite].sum() > 0:
            cx = np.average(pc1_arr[finite], weights=w[finite])
            cy = np.average(pc2_arr[finite], weights=w[finite])
            ax_d.annotate(g, (cx, cy), fontsize=7,
                          color=cmap_t(i % 10), fontweight="bold")
    ax_d.set_xlabel("PC1"); ax_d.set_ylabel("PC2")
    ax_d.set_title("D — PC2-genuine gene manifold placement")

    # ── E: Tier3 cluster comparison ────────────────────────────────────────
    ax_e = fig.add_subplot(gs[1, 1])
    if len(clust_df) > 0 and "gene" in clust_df.columns:
        genes_e  = clust_df["gene"].tolist()
        c2_means = clust_df["c2_mean"].values.astype(float)
        c3_means = clust_df["c3_mean"].values.astype(float)
        x = np.arange(len(genes_e))
        w = 0.35
        ax_e.bar(x - w/2, c2_means, w, label="Cluster2 (shallow)",
                 color="#4393c3", alpha=0.85)
        ax_e.bar(x + w/2, c3_means, w, label="Cluster3 (deep)",
                 color="#d6604d", alpha=0.85)
        for i, row in clust_df.iterrows():
            if row.get("depth_specific", False):
                ymax = max(row["c2_mean"], row["c3_mean"])
                ax_e.text(int(i), ymax + 0.01, "*",
                          ha="center", fontsize=12)
        ax_e.set_xticks(x)
        ax_e.set_xticklabels(genes_e, rotation=45, ha="right", fontsize=8)
        ax_e.set_ylabel("Mean expression (norm.)")
        ax_e.legend(fontsize=8)
    ax_e.set_title("E — Tier3: Cluster2 vs Cluster3\n(* = MW p<0.05)")

    # ── F: Tier3 revalidation ──────────────────────────────────────────────
    ax_f = fig.add_subplot(gs[1, 2])
    if len(reval_df) > 0 and "n_partners_ext" in reval_df.columns:
        genes_f = reval_df["gene"].tolist()
        n_part  = reval_df["n_partners_ext"].fillna(0).values.astype(float)
        colors  = ["#1a9850" if bool(s) else "#d73027"
                   for s in reval_df["stable"].values]
        ax_f.barh(range(len(genes_f)), n_part, color=colors, alpha=0.85)
        ax_f.axvline(3, color="black", lw=1.2, ls="--",
                     label="threshold = 3")
        ax_f.set_yticks(range(len(genes_f)))
        ax_f.set_yticklabels(genes_f, fontsize=9)
        ax_f.set_xlabel("n Tier1 partners (|r|>=0.50)")
        ax_f.legend(fontsize=8)
    ax_f.set_title("F — Tier3 revalidation\n(green=stable, red=demoted)")

    fig.suptitle(
        "chRCC False Attractor — Script 5\n"
        "Geometric Characterisation Completion Pass",
        fontsize=13, fontweight="bold"
    )
    fig.savefig(os.path.join(S5_DIR, "s5_figure.png"),
                dpi=150, bbox_inches="tight")
    plt.close(fig)
    log(f"\n  Figure saved: {os.path.join(S5_DIR, 's5_figure.png')}")


# ── main ───────────────────────────────���───────────────────────────────────────
def main():
    log("=" * 62)
    log("chRCC FALSE ATTRACTOR — SCRIPT 5")
    log("OrganismCore | Document 96e | 2026-03-02")
    log("Author: Eric Robert Lawson")
    log("=" * 62)
    log("GEOMETRIC CHARACTERISATION — COMPLETION PASS")
    log("Geometry-first. No literature. No priors.")
    log("=" * 62)

    (raw, t_cols, n_cols, chr_cols, onc_cols,
     depth, pc1, pc2, load_df,
     rev_vec, rev_min, top200, bot200, pcorr, gmm_df) = load_data()

    # ── tier reconstruction ────────────────────────────────────────────────
    (tier1_genes, tier2_genes, tier3_genes,
     rv, gap_col, load_col, q75) = reconstruct_tiers(
        rev_vec, top200, pcorr, load_df)

    log()
    log("  TIER RECONSTRUCTION:")
    log(f"  gap_col='{gap_col}'  load_col='{load_col}'  "
        f"q75_loading={q75:.6f}")
    log(f"  Tier1={len(tier1_genes)}  "
        f"Tier2={len(tier2_genes)}  "
        f"Tier3={len(tier3_genes)}")
    log(f"  Tier3 genes: {sorted(tier3_genes)}")

    # ── S1 ─────────────────────────────────────────────────────────────────
    pc2_full, pc2_top100 = s1_full_pc2_residualisation(
        raw, t_cols, n_cols, depth, pc2)

    # ── S2 ─────────────────────────────────────────────────────────────────
    corr_df, reval_df, stable_tier3, tier1_list = s2_extended_partial_corr(
        raw, t_cols, n_cols, tier1_genes, tier3_genes,
        rv, gap_col, load_col)

    # ── S3 ──────────��──────────────────────────────────────────────────────
    neigh_df = s3_tier3_neighbourhood(
        corr_df, tier3_genes, rv, gap_col, load_col)

    # ── S4 ─────────────────────────────────────────────────────────────────
    (manifold_df, genuine_genes,
     pc1_arr, pc2_arr, dep_arr, all_cols) = s4_pc2_genuine_manifold(
        raw, t_cols, n_cols, pc1, pc2, depth, pc2_full)

    # ── S5 ─────────────────────────────────────────────────────────────────
    clust_df, any_specific = s5_cluster_depth_check(
        raw, tier3_genes, depth, gmm_df, t_cols)

    # ── S6 ─────────────────────────────────────────────────────────────────
    s6_synthesis(tier1_genes, tier2_genes, tier3_genes,
                 stable_tier3, reval_df,
                 pc2_full, manifold_df, clust_df, any_specific)

    # ── figure ─────────────────────────────────────────────────────────────
    make_figure(pc1_arr, pc2_arr, dep_arr, all_cols,
                t_cols, n_cols, pc2_full, manifold_df,
                genuine_genes, corr_df, tier3_genes,
                stable_tier3, clust_df, reval_df, raw)

    log()
    log("=" * 62)
    log("SCRIPT 5 COMPLETE")
    log("=" * 62)
    log()
    log("  Output files in: " + S5_DIR)
    log("  pc2_residualised_full.csv    — r(gene, PC2|depth) all genes")
    log("  pc2_clean_top100.csv         — top 100 PC2-genuine genes")
    log("  partial_corr_tier1.csv       — Tier1 co-regulation matrix")
    log("  tier3_revalidated.csv        — Tier3 stability in Tier1 window")
    log("  tier3_neighbourhood.csv      — top partners per Tier3 gene")
    log("  tier3_cluster_comparison.csv — Cluster2 vs Cluster3 expression")
    log("  pc2_genuine_manifold.csv     — PC2-genuine manifold coordinates")
    log("  s5_log.txt                   — full log")
    log("  s5_figure.png                — 6-panel geometry figure")

    write_log()


if __name__ == "__main__":
    main()
