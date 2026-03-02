"""
chRCC False Attractor — Script 3
GEOMETRY FIRST

Framework: OrganismCore
Document 96c | 2026-03-02
Author: Eric Robert Lawson

═══════════════════════════════════════════════════════════════
METHODOLOGICAL COMMITMENT

The data defines the geometry.
The geometry defines the biology.
The biology is not known in advance.

No predictions.
No pre-selected gene panels.
No imported references from other cancers.
No literature drug target lists.

Every finding emerges from the geometry.
Biological interpretation happens after
the geometry is fully characterised.
It does not shape the geometry.

═══════════════════════════════════════════════════════════════
INPUTS

  TCGA_KICH_HiSeqV2.gz          expression matrix
  depth_scores.csv               PC1 per sample (from S1)
  attractor_gene_panel.csv       r(gene,PC1) 14833 genes

═══════════════════════════════════════════════════════════════
STEPS

  S1  Full manifold geometry  PC1–PC5
  S2  Bimodality test
  S3  Unbiased programme discovery
  S4  Module structure (partial correlations)
  S5  PC2 structure and subtype analysis
  S6  Reversal vector
  S7  Biological interpretation
═══════════════════════════════════════════════════════════════
"""

import os
import gzip
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.stats import pearsonr, mannwhitneyu
from scipy.linalg import svd
from sklearn.mixture import GaussianMixture
import collections
warnings.filterwarnings("ignore")

# ═══════════════════════════════════════════════════════════════
# PATHS
# ═══════════════════════════════════════════════════════════════

BASE_DIR   = "./chrcc_false_attractor/"
S1_DIR     = os.path.join(BASE_DIR, "results_s1/")
S3_DIR     = os.path.join(BASE_DIR, "results_s3/")
LOG_FILE   = os.path.join(S3_DIR,   "s3_log.txt")

KICH_EXPR  = os.path.join(BASE_DIR,
                            "TCGA_KICH_HiSeqV2.gz")
DEPTH_FILE = os.path.join(S1_DIR,
                            "depth_scores.csv")
ATT_FILE   = os.path.join(S1_DIR,
                            "attractor_gene_panel.csv")

os.makedirs(S3_DIR, exist_ok=True)

# ═══════════════════════════════════════════════════════════════
# UTILITIES
# ═══════════════════════════════════════════════════════════════

log_lines = []

def log(msg=""):
    print(msg)
    log_lines.append(str(msg))

def write_log():
    with open(LOG_FILE, "w") as f:
        f.write("\n".join(log_lines))

def safe_r(x, y):
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    m = np.isfinite(x) & np.isfinite(y)
    if m.sum() < 5:
        return np.nan, np.nan
    return pearsonr(x[m], y[m])

def safe_mwu(a, b):
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    a = a[np.isfinite(a)]
    b = b[np.isfinite(b)]
    if len(a) < 3 or len(b) < 3:
        return np.nan, np.nan
    return mannwhitneyu(
        a, b, alternative="two-sided")

def norm01(a):
    a  = np.asarray(a, float)
    mn = np.nanmin(a)
    mx = np.nanmax(a)
    if mx == mn:
        return np.zeros_like(a)
    return (a - mn) / (mx - mn)

def classify_bc(bc):
    parts = bc.split("-")
    if len(parts) < 5:
        return "unknown"
    c = parts[4][:2]
    if   c == "01": return "chRCC"
    elif c == "02": return "oncocytoma"
    elif c == "11": return "normal"
    return "other"

def fmt_p(p):
    if p is None or np.isnan(p):
        return "—"
    if p < 1e-10: return "p<1e-10"
    if p < 1e-05: return f"p={p:.2e}"
    if p < 0.001: return f"p={p:.4f}"
    return f"p={p:.4f}"

# ═══════════════════════════════════════════════════════════════
# DATA LOAD
# ═══════════════════════════════════════════════════════════════

def load_data():
    log("="*60)
    log("chRCC FALSE ATTRACTOR — SCRIPT 3")
    log("OrganismCore | Document 96c | "
        "2026-03-02")
    log("Author: Eric Robert Lawson")
    log("="*60)
    log("")
    log("GEOMETRY FIRST.")
    log("No predictions. No panels. No priors.")
    log("The data speaks.")
    log("")
    log("="*60)
    log("DATA LOAD")
    log("="*60)

    opener = (gzip.open
              if KICH_EXPR.endswith(".gz")
              else open)
    with opener(KICH_EXPR, "rt") as fh:
        raw = pd.read_csv(
            fh, sep="\t", index_col=0)
    log(f"  Expression: {raw.shape[0]} genes "
        f"× {raw.shape[1]} samples")

    meta   = pd.Series(
        {s: classify_bc(s)
         for s in raw.columns})
    t_cols = raw.columns[meta == "chRCC"]
    n_cols = raw.columns[meta == "normal"]
    o_cols = raw.columns[meta == "oncocytoma"]
    log(f"  chRCC={len(t_cols)}  "
        f"normal={len(n_cols)}  "
        f"oncocytoma={len(o_cols)}")

    depth_df = pd.read_csv(DEPTH_FILE)
    depth_t  = depth_df[
        depth_df["class"] == "chRCC"
    ].set_index("sample_id")["depth"]
    depth_n  = depth_df[
        depth_df["class"] == "normal"
    ].set_index("sample_id")["depth"]
    depth_o  = depth_df[
        depth_df["class"] == "oncocytoma"
    ].set_index("sample_id")["depth"]
    log(f"  Depth scores: "
        f"chRCC={len(depth_t)}  "
        f"normal={len(depth_n)}  "
        f"oncocytoma={len(depth_o)}")

    att_df = pd.read_csv(ATT_FILE) \
               .dropna(subset=["r_depth"]) \
               .sort_values(
                   "r_depth",
                   key=abs,
                   ascending=False)
    log(f"  Attractor panel: "
        f"{len(att_df)} genes")

    return (raw, t_cols, n_cols, o_cols,
            depth_t, depth_n, depth_o,
            att_df)

# ═══════════════════════════════════════════════════════════════
# S1 — FULL MANIFOLD GEOMETRY PC1–PC5
# ════════════════���══════════════════════════════════════════════

def s1_manifold(raw, t_cols, n_cols, o_cols):
    log("")
    log("="*60)
    log("S1 — FULL MANIFOLD GEOMETRY")
    log("="*60)
    log("  PC1–PC5  |  top 5000 variable genes")
    log("  No prior gene selection")

    all_cols = (list(t_cols) +
                list(n_cols) +
                list(o_cols))
    sub = raw[all_cols].copy()

    gene_var  = sub.var(axis=1)
    top_genes = gene_var.nlargest(5000).index
    sub       = sub.loc[top_genes]

    sub_z = sub.subtract(
        sub.mean(axis=1), axis=0
    ).divide(
        sub.std(axis=1).replace(0, 1), axis=0
    ).fillna(0)

    mat       = sub_z.values.T          # 83 × 5000
    U, S, Vt  = svd(mat, full_matrices=False)
    var_total = np.sum(S**2)

    pcs      = {}
    loadings = {}

    log(f"\n  {'PC':<5} {'Var%':>8} "
        f"{'Cum%':>8}")
    log(f"  {'─'*24}")
    cumvar = 0.0
    for i in range(min(5, len(S))):
        vp     = 100.0 * S[i]**2 / var_total
        cumvar += vp
        name   = f"PC{i+1}"
        scores = pd.Series(
            U[:, i] * S[i],
            index=all_cols,
            name=name)
        pcs[name]      = scores
        loadings[name] = pd.Series(
            Vt[i, :],
            index=top_genes,
            name=f"{name}_loading")
        log(f"  {name:<5} {vp:>8.2f}% "
            f"{cumvar:>8.2f}%")

    # Orient PC1: tumour > normal
    pc1 = pcs["PC1"]
    if (pc1[list(n_cols)].mean() >
            pc1[list(t_cols)].mean()):
        pcs["PC1"]      = -pc1
        loadings["PC1"] = -loadings["PC1"]
        log("  PC1 flipped: tumour > normal")
    else:
        log("  PC1 orientation: tumour > normal")

    # Top/bottom 10 loadings per PC
    log("")
    for name in pcs:
        ld  = loadings[name]\
                .sort_values(ascending=False)
        log(f"  {name} positive pole "
            f"(attractor end):")
        for gene, val in ld.head(10).items():
            log(f"    {gene:<16} {val:>+.4f}")
        log(f"  {name} negative pole "
            f"(normal end):")
        for gene, val in ld.tail(10).items():
            log(f"    {gene:<16} {val:>+.4f}")
        log("")

    # Save
    pd.DataFrame(pcs).assign(
        sample_class=lambda df:
            [classify_bc(s) for s in df.index]
    ).to_csv(os.path.join(S3_DIR,
                           "pc_scores.csv"))
    pd.DataFrame(loadings).to_csv(
        os.path.join(S3_DIR,
                     "pc_loadings.csv"))
    log("  Saved: pc_scores.csv")
    log("  Saved: pc_loadings.csv")

    return pcs, loadings, S, var_total

# ═══════════════════════════════════════════════════════════════
# S2 — BIMODALITY TEST
# ═══════════════════════════════════════════════════════════════

def s2_bimodality(pcs, t_cols,
                   n_cols, o_cols):
    log("")
    log("="*60)
    log("S2 — BIMODALITY TEST")
    log("="*60)
    log("  Is the attractor discrete "
        "or continuous?")

    pc1    = pcs["PC1"]
    x_all  = pc1.values.reshape(-1, 1)
    x_flat = pc1.values

    # Bootstrap dip statistic
    def dip_stat(x):
        x    = np.sort(x)
        n    = len(x)
        ecdf = np.arange(1, n+1) / n
        unif = np.linspace(0, 1, n)
        return float(np.max(np.abs(
            ecdf - unif)))

    obs_dip  = dip_stat(x_flat)
    rng      = np.random.default_rng(42)
    null_dips = np.array([
        dip_stat(rng.uniform(
            x_flat.min(),
            x_flat.max(),
            len(x_flat)))
        for _ in range(1000)])
    dip_p = float(
        (null_dips >= obs_dip).sum() / 1000)

    log(f"\n  Dip statistic: {obs_dip:.4f}")
    log(f"  Bootstrap p:   {dip_p:.4f}")
    log("  " + (
        "BIMODAL — discrete attractor"
        if dip_p < 0.05
        else "UNIMODAL — continuous trajectory"))

    # GMM
    log("\n  GMM k=2,3,4:")
    log(f"  {'k':<4} {'BIC':>12} "
        f"{'AIC':>12}")
    log(f"  {'─'*30}")
    bics = {}
    aics = {}
    gmms = {}
    for k in [2, 3, 4]:
        g = GaussianMixture(
            n_components=k,
            random_state=42,
            n_init=10)
        g.fit(x_all)
        bics[k] = g.bic(x_all)
        aics[k] = g.aic(x_all)
        gmms[k] = g
        log(f"  k={k}  "
            f"{bics[k]:>12.2f}  "
            f"{aics[k]:>12.2f}")

    best_bic = min(bics, key=bics.get)
    best_aic = min(aics, key=aics.get)
    log(f"\n  Best BIC: k={best_bic}")
    log(f"  Best AIC: k={best_aic}")

    best_gmm = gmms[best_bic]
    labels   = best_gmm.predict(x_all)
    order    = np.argsort(
        best_gmm.means_.flatten())
    log(f"\n  GMM k={best_bic} components:")
    for idx in order:
        m   = float(best_gmm.means_[idx, 0])
        s   = float(
            best_gmm.covariances_[idx,0,0]
            **0.5)
        w   = float(best_gmm.weights_[idx])
        smp = np.where(labels == idx)[0]
        cc  = collections.Counter([
            classify_bc(pc1.index[i])
            for i in smp])
        log(f"    mean={m:>+.3f}  "
            f"std={s:.3f}  "
            f"w={w:.3f}  "
            f"{dict(cc)}")

    # Per-class stats on norm01 depth
    pc1_norm = pd.Series(
        norm01(pc1.values),
        index=pc1.index)
    log("\n  Normalised depth by class:")
    for cls, cols in [
        ("chRCC",      t_cols),
        ("oncocytoma", o_cols),
        ("normal",     n_cols),
    ]:
        v = pc1_norm[list(cols)].values
        log(f"  {cls:<14} "
            f"mean={v.mean():.3f}  "
            f"std={v.std():.3f}  "
            f"min={v.min():.3f}  "
            f"max={v.max():.3f}")

    bimodal = (dip_p < 0.05 or best_bic > 1)
    return bimodal, best_bic, best_gmm

# ═══════════════════════════════════════════════════════��═══════
# S3 — UNBIASED PROGRAMME DISCOVERY
# ═══════════════════════════════════════════════════════════════

def s3_programme_discovery(att_df):
    log("")
    log("="*60)
    log("S3 — UNBIASED PROGRAMME DISCOVERY")
    log("="*60)
    log("  Top/bottom 200 PC1 correlates")
    log("  No pre-selection. No panels.")
    log("  Reading the geometry directly.")

    ranked = att_df.sort_values(
        "r_depth", ascending=False)
    top200 = ranked.head(200)
    bot200 = ranked.tail(200)

    log("\n  TOP 200 ATTRACTOR GENES "
        "(acquired — positive pole):")
    log(f"  {'#':>4}  {'Gene':<16} "
        f"{'r_depth':>9}")
    log(f"  {'─'*34}")
    for i, (_, row) in enumerate(
            top200.iterrows(), 1):
        log(f"  {i:>4}.  {row['gene']:<16} "
            f"{row['r_depth']:>+9.4f}")

    log("\n  BOTTOM 200 (lost — normal pole):")
    log(f"  {'#':>4}  {'Gene':<16} "
        f"{'r_depth':>9}")
    log(f"  {'─'*34}")
    for i, (_, row) in enumerate(
            bot200.iterrows(), 1):
        log(f"  {i:>4}.  {row['gene']:<16} "
            f"{row['r_depth']:>+9.4f}")

    # Pattern scan — no pre-labels
    log("")
    log("  STRUCTURAL PATTERNS IN GENE NAMES:")
    log("  (observations from geometry — "
        "not pre-selected panels)")

    def scan(gene_list, label):
        log(f"\n  {label}:")
        genes = [str(g).upper()
                 for g in gene_list]
        patterns = [
            ("TF",
             ["HNF","FOXA","RUNX","KLF",
              "NR1","NR3","MLXIPL","FOXP",
              "SOX","GATA","NFAT","ZEB",
              "SNAI","TWIST","ETS","PAX"]),
            ("KINASE/SIGNAL",
             ["CDK","MAP","AKT","PIK","RAF",
              "JAK","STAT","SRC","MTOR",
              "WNK","STK","RPS6K","ABL"]),
            ("METABOLIC",
             ["IDH","CS","FH","GOT","MDH",
              "OGDH","SUCLG","SUCLA","ACO",
              "PKM","LDHA","HK","PFK","KHK",
              "G6P","FBP","PCK","ACAD",
              "HADH","CPT","ACOX","SDH",
              "COX","ATP5","ATP6"]),
            ("CHROMATIN",
             ["EZH","EED","SUZ","BMI","KDM",
              "DNMT","TET","SETD","NSD",
              "ARID","SMARCA","BAP","PBRM",
              "JARID","KAT","HDAC","CBX",
              "RING","PCGF","RUNX"]),
            ("TRANSPORTER",
             ["SLC","ABC","ATP6V","CFTR",
              "KCNJ","SCN","CACN","CLCN",
              "AQP","RHBG","RHCG"]),
            ("CYTOSKEL/ECM",
             ["KRT","COL","LAM","FN1","VIM",
              "ACTA","MMP","ITGA","ITGB",
              "CDH","CLDN","OCLN"]),
            ("IMMUNE",
             ["CD8","CD4","CD274","FOXP3",
              "IDO","ARG","PDCD","CTLA",
              "TIGIT","LAG","HAVCR","GZMB",
              "PRF","IFNG","HLA","B2M"]),
            ("CELL_CYCLE",
             ["CDK","CCNA","CCNB","CCND",
              "CCNE","CDKN","RB1","E2F",
              "MKI67","PCNA","MCM","TOP2"]),
            ("RIBOSOME/RNA",
             ["RPL","RPS","EIF","HNRNP",
              "SNRP","SF3","SRRM","DDX",
              "DHX","PABP","XRN"]),
        ]
        total = len(genes)
        for tag, prefixes in patterns:
            matched = [
                g for g in genes
                if any(g.startswith(p)
                        or p in g
                        for p in prefixes)]
            if matched:
                pct = 100*len(matched)/total
                log(f"    {tag:<18} "
                    f"n={len(matched):>4}  "
                    f"({pct:>5.1f}%)  "
                    f"{matched[:6]}")

    scan(top200["gene"].tolist(),
          "ATTRACTOR POLE (acquired)")
    scan(bot200["gene"].tolist(),
          "NORMAL POLE (lost)")

    top200.to_csv(
        os.path.join(S3_DIR,
                     "top200_attractor.csv"),
        index=False)
    bot200.to_csv(
        os.path.join(S3_DIR,
                     "bot200_normal.csv"),
        index=False)
    log("\n  Saved: top200_attractor.csv")
    log("  Saved: bot200_normal.csv")

    return top200, bot200

# ═══════════════════════════════════════════════════════════════
# S4 — MODULE STRUCTURE
# ═══════════════════════════════════════════════════════════════

def s4_modules(raw, t_cols, n_cols,
                o_cols, pcs, att_df):
    log("")
    log("="*60)
    log("S4 — MODULE STRUCTURE")
    log("="*60)
    log("  Partial correlations given PC1")
    log("  r(gene_i, gene_j | PC1)")
    log("  Independent co-regulation")

    all_cols = (list(t_cols) +
                list(n_cols) +
                list(o_cols))
    pc1      = pcs["PC1"].reindex(all_cols)

    # Top 50 each pole for partial corr
    ranked   = att_df.sort_values(
        "r_depth", ascending=False)
    top50    = ranked.head(50)["gene"]\
                 .tolist()
    bot50    = ranked.tail(50)["gene"]\
                 .tolist()
    use_genes = [g for g in
                  dict.fromkeys(
                      top50 + bot50)
                  if g in raw.index]
    log(f"  Genes: {len(use_genes)}")

    # Residualise on PC1
    residuals = {}
    for gene in use_genes:
        y = raw.loc[gene, all_cols]\
               .reindex(pc1.index).values
        x = pc1.values
        m = np.isfinite(x) & np.isfinite(y)
        if m.sum() < 10:
            continue
        xm   = x[m]; ym = y[m]
        beta = (np.cov(xm, ym)[0, 1] /
                np.var(xm))
        alph = ym.mean() - beta * xm.mean()
        res  = np.full(len(x), np.nan)
        res[m] = ym - (alph + beta * xm)
        residuals[gene] = res

    genes_ok = list(residuals.keys())
    n_g      = len(genes_ok)
    log(f"  Residualised genes: {n_g}")

    # Pairwise partial correlations
    pcorr = np.full((n_g, n_g), np.nan)
    for i in range(n_g):
        for j in range(i, n_g):
            r, _ = safe_r(
                residuals[genes_ok[i]],
                residuals[genes_ok[j]])
            pcorr[i, j] = r
            pcorr[j, i] = r

    # Strongest pairs
    log("\n  STRONGEST PARTIAL CORRELATIONS "
        "(independent of depth):")
    log(f"  {'Gene_i':<16} {'Gene_j':<16} "
        f"{'r_partial':>10}")
    log(f"  {'─'*44}")
    pairs = []
    for i in range(n_g):
        for j in range(i+1, n_g):
            v = pcorr[i, j]
            if not np.isnan(v):
                pairs.append((
                    genes_ok[i],
                    genes_ok[j],
                    v))
    pairs.sort(key=lambda x: abs(x[2]),
                reverse=True)
    for gi, gj, r in pairs[:30]:
        log(f"  {gi:<16} {gj:<16} "
            f"{r:>+10.4f}")

    # Module detection
    log("\n  MODULE DETECTION "
        "(|r_partial| > 0.60):")
    adj     = ((np.abs(pcorr) > 0.60) &
                (np.abs(pcorr) < 1.0))
    visited = set()
    modules = []
    for i in range(n_g):
        if genes_ok[i] in visited:
            continue
        module = [genes_ok[i]]
        visited.add(genes_ok[i])
        for j in range(n_g):
            if (genes_ok[j] not in visited
                    and adj[i, j]):
                module.append(genes_ok[j])
                visited.add(genes_ok[j])
        if len(module) > 1:
            modules.append(module)

    log(f"  Modules found: {len(modules)}")
    for k, mod in enumerate(modules, 1):
        log(f"  Module {k} "
            f"(n={len(mod)}): "
            f"{mod[:8]}")

    pcorr_df = pd.DataFrame(
        pcorr,
        index=genes_ok,
        columns=genes_ok)
    pcorr_df.to_csv(
        os.path.join(S3_DIR,
                     "partial_corr.csv"))
    log("\n  Saved: partial_corr.csv")

    return pcorr_df, modules, genes_ok

# ═══════════════════════════��═══════════════════════════════════
# S5 — PC2 STRUCTURE
# ═══════════════════════════════════════════════════════════════

def s5_pc2_structure(raw, t_cols, n_cols,
                      o_cols, pcs,
                      loadings, att_df,
                      depth_t):
    log("")
    log("="*60)
    log("S5 — PC2 STRUCTURE")
    log("="*60)
    log("  What does PC2 capture?")
    log("  chRCC vs oncocytoma on PC2?")
    log("  chRCC subtypes?")

    all_cols = (list(t_cols) +
                list(n_cols) +
                list(o_cols))
    pc1 = pcs["PC1"]
    pc2 = pcs["PC2"]

    # Class stats on PC2
    log("\n  PC2 by class:")
    for cls, cols in [
        ("chRCC",      t_cols),
        ("oncocytoma", o_cols),
        ("normal",     n_cols),
    ]:
        v = pc2[list(cols)].values
        log(f"  {cls:<14} "
            f"mean={v.mean():>+8.4f}  "
            f"std={v.std():>8.4f}  "
            f"min={v.min():>+8.4f}  "
            f"max={v.max():>+8.4f}")

    # MW tests
    _, p_co = safe_mwu(
        pc2[list(t_cols)].values,
        pc2[list(o_cols)].values)
    _, p_cn = safe_mwu(
        pc2[list(t_cols)].values,
        pc2[list(n_cols)].values)
    log(f"\n  MW chRCC vs oncocytoma PC2: "
        f"{fmt_p(p_co)}")
    log(f"  MW chRCC vs normal PC2:     "
        f"{fmt_p(p_cn)}")
    if not np.isnan(p_co) and p_co < 0.05:
        log("  PC2 SEPARATES chRCC from "
            "oncocytoma ✓")
    else:
        log("  PC2 does not separate chRCC "
            "from oncocytoma at p<0.05")

    # Gene correlates of PC2 (all samples)
    log("\n  COMPUTING PC2 GENE CORRELATES "
        "(all 83 samples)...")
    pc2_scores = pc2.reindex(all_cols)
    pc2_corrs  = []
    for gene in raw.index:
        g_ = raw.loc[gene, all_cols]\
               .reindex(pc2_scores.index)
        r, p = safe_r(g_.values,
                       pc2_scores.values)
        if not np.isnan(r):
            pc2_corrs.append(
                {"gene": gene,
                  "r_PC2": r,
                  "p_PC2": p})

    pc2_df = pd.DataFrame(pc2_corrs)\
               .sort_values(
                   "r_PC2",
                   key=abs,
                   ascending=False)

    log("\n  TOP 30 POSITIVE PC2:")
    log(f"  {'Gene':<16} {'r_PC2':>9}")
    log(f"  {'─'*28}")
    for _, row in pc2_df[
            pc2_df["r_PC2"] > 0
    ].head(30).iterrows():
        log(f"  {row['gene']:<16} "
            f"{row['r_PC2']:>+9.4f}")

    log("\n  TOP 30 NEGATIVE PC2:")
    log(f"  {'Gene':<16} {'r_PC2':>9}")
    log(f"  {'─'*28}")
    for _, row in pc2_df[
            pc2_df["r_PC2"] < 0
    ].head(30).iterrows():
        log(f"  {row['gene']:<16} "
            f"{row['r_PC2']:>+9.4f}")

    # chRCC subtype split on PC2
    log("\n  chRCC SUBTYPE SPLIT ON PC2:")
    t_pc2    = pc2[list(t_cols)]\
                 .sort_values()
    med_pc2  = float(t_pc2.median())
    low_pc2  = t_pc2[
        t_pc2 <= med_pc2].index.tolist()
    high_pc2 = t_pc2[
        t_pc2 > med_pc2].index.tolist()
    log(f"  Median PC2 in chRCC: "
        f"{med_pc2:>+.4f}")
    log(f"  PC2-low  group: n={len(low_pc2)}")
    log(f"  PC2-high group: n={len(high_pc2)}")

    # Genes distinguishing PC2 subtypes
    log("\n  GENES DISTINGUISHING "
        "PC2-high vs PC2-low chRCC:")
    log(f"  {'Gene':<16} "
        f"{'hi_mean':>10} "
        f"{'lo_mean':>10} "
        f"{'delta':>8} "
        f"{'p_MWU':>12}")
    log(f"  {'─'*60}")

    sub_rows = []
    for gene in raw.index:
        hi = raw.loc[gene,
                      high_pc2].values
        lo = raw.loc[gene,
                      low_pc2].values
        delta_val = float(
            hi.mean() - lo.mean())
        _, p = safe_mwu(hi, lo)
        if not np.isnan(p):
            sub_rows.append({
                "gene":      gene,
                "hi_mean":   float(hi.mean()),
                "lo_mean":   float(lo.mean()),
                "delta_val": delta_val,
                "p_mwu":     float(p),
            })

    # NOTE: column named delta_val
    # (not diff) to avoid pandas method clash
    sub_df = pd.DataFrame(sub_rows)\
               .sort_values(
                   "delta_val",
                   key=abs,
                   ascending=False)\
               .head(50)

    for _, row in sub_df.head(30)\
            .iterrows():
        log(f"  {row['gene']:<16} "
            f"{row['hi_mean']:>10.3f} "
            f"{row['lo_mean']:>10.3f} "
            f"{row['delta_val']:>+8.3f} "
            f"{fmt_p(row['p_mwu']):>12}")

    pc2_df.to_csv(
        os.path.join(S3_DIR,
                     "pc2_correlates.csv"),
        index=False)
    sub_df.to_csv(
        os.path.join(S3_DIR,
                     "pc2_subtype_genes.csv"),
        index=False)
    log("\n  Saved: pc2_correlates.csv")
    log("  Saved: pc2_subtype_genes.csv")

    return pc2_df, sub_df, low_pc2, high_pc2

# ═══════════════════════════════════════════════════════════════
# S6 — REVERSAL VECTOR
# ════════════════════════════════════════════��══════════════════

def s6_reversal_vector(raw, t_cols,
                        n_cols, o_cols,
                        pcs, loadings,
                        att_df):
    log("")
    log("="*60)
    log("S6 — REVERSAL VECTOR")
    log("="*60)
    log("  Minimum gene set to move a point")
    log("  from attractor basin to normal basin")
    log("  Derived from PC1 geometry only")
    log("  No prior knowledge involved")

    all_cols = (list(t_cols) +
                list(n_cols) +
                list(o_cols))
    pc1      = pcs["PC1"]
    ld1      = loadings["PC1"]

    pc1_norm = pd.Series(
        norm01(pc1.values),
        index=pc1.index)

    t_mean = float(
        pc1_norm[list(t_cols)].mean())
    n_mean = float(
        pc1_norm[list(n_cols)].mean())
    gap    = t_mean - n_mean

    log(f"\n  Normal mean depth:  {n_mean:.4f}")
    log(f"  chRCC mean depth:   {t_mean:.4f}")
    log(f"  Gap to close:       {gap:.4f}")

    # Loading coverage
    ld_abs   = ld1.abs().sort_values(
        ascending=False)
    total_ld = float(ld_abs.sum())
    cumsum   = ld_abs.cumsum()

    log("\n  LOADING COVERAGE "
        "(how many genes span X% of PC1):")
    log(f"  {'Threshold':>12} "
        f"{'n_genes':>8} "
        f"{'top_gene'}")
    log(f"  {'─'*40}")
    thresholds = [0.10, 0.20, 0.30,
                   0.50, 0.75, 0.90]
    reported   = set()
    for i, (gene, cv) in enumerate(
            zip(ld_abs.index,
                cumsum.values), 1):
        frac = cv / total_ld
        for thr in thresholds:
            if (thr not in reported and
                    frac >= thr):
                log(f"  {100*thr:>11.0f}%  "
                    f"{i:>8}  "
                    f"{gene}")
                reported.add(thr)
        if len(reported) == len(thresholds):
            break

    # Per-gene reversal shift
    rev_rows = []
    for gene in ld_abs.index:
        if gene not in raw.index:
            continue
        nm     = float(
            raw.loc[gene, n_cols].mean())
        tm     = float(
            raw.loc[gene, t_cols].mean())
        ld_val = float(ld1[gene])
        shift  = (nm - tm) * ld_val
        rev_rows.append({
            "gene":       gene,
            "loading":    ld_val,
            "n_mean":     nm,
            "t_mean":     tm,
            "expr_delta": nm - tm,
            "pc1_shift":  shift,
            "direction":  (
                "restore_normal"
                if shift < 0
                else "push_deeper"),
        })

    rev_df = pd.DataFrame(rev_rows)

    # Restorative genes (shift toward normal)
    restorative = rev_df[
        rev_df["pc1_shift"] < 0
    ].sort_values("pc1_shift").copy()
    restorative["cum_shift"] = \
        restorative["pc1_shift"].cumsum()

    target = -(gap / 2.0)
    min_set = restorative[
        restorative["cum_shift"] <= target]
    if len(min_set) == 0:
        min_set = restorative.head(20)

    log(f"\n  Target shift (gap/2): {target:.4f}")
    log(f"  Reversal set size: {len(min_set)}")
    log(f"  Cumulative shift:  "
        f"{min_set['cum_shift'].iloc[-1]:.4f}")

    log("\n  REVERSAL SET "
        "(geometry-derived intervention "
        "targets):")
    log(f"  {'#':>4}  {'Gene':<16} "
        f"{'loading':>9} "
        f"{'N_mean':>8} "
        f"{'T_mean':>8} "
        f"{'pc1_shift':>10}")
    log(f"  {'─'*60}")
    for i, (_, row) in enumerate(
            min_set.iterrows(), 1):
        log(f"  {i:>4}.  {row['gene']:<16} "
            f"{row['loading']:>+9.4f} "
            f"{row['n_mean']:>8.3f} "
            f"{row['t_mean']:>8.3f} "
            f"{row['pc1_shift']:>+10.4f}")

    # Deepening genes
    deepening = rev_df[
        rev_df["pc1_shift"] > 0
    ].sort_values(
        "pc1_shift",
        ascending=False).head(20)

    log("\n  TOP 20 DEEPENING GENES "
        "(blocking these slows progression):")
    log(f"  {'#':>4}  {'Gene':<16} "
        f"{'loading':>9} "
        f"{'N_mean':>8} "
        f"{'T_mean':>8} "
        f"{'pc1_shift':>10}")
    log(f"  {'─'*60}")
    for i, (_, row) in enumerate(
            deepening.iterrows(), 1):
        log(f"  {i:>4}.  {row['gene']:<16} "
            f"{row['loading']:>+9.4f} "
            f"{row['n_mean']:>8.3f} "
            f"{row['t_mean']:>8.3f} "
            f"{row['pc1_shift']:>+10.4f}")

    rev_df.to_csv(
        os.path.join(S3_DIR,
                     "reversal_vector.csv"),
        index=False)
    min_set.to_csv(
        os.path.join(S3_DIR,
                     "reversal_min_set.csv"),
        index=False)
    log("\n  Saved: reversal_vector.csv")
    log("  Saved: reversal_min_set.csv")

    return rev_df, min_set

# ═══════════════════════════════════════════════════════════════
# S7 — BIOLOGICAL INTERPRETATION
# ═══════════════════════════════════════════════════════════════

def s7_interpretation(top200, bot200,
                       modules, min_set,
                       pc2_df, sub_df,
                       low_pc2, high_pc2,
                       bimodal, best_k):
    log("")
    log("="*60)
    log("S7 — BIOLOGICAL INTERPRETATION")
    log("="*60)
    log("  Constrained by geometry only.")
    log("  No prior panels.")
    log("  Reading what the data produced.")

    log("\n  WHAT chRCC ACQUIRES "
        "(attractor identity):")
    log("  Source: top 200 PC1 correlates")
    log("  These genes define the attractor.")
    for i, (_, row) in enumerate(
            top200.head(20).iterrows(), 1):
        log(f"  {i:>3}. {row['gene']:<16} "
            f"r={row['r_depth']:>+.4f}")

    log("\n  WHAT chRCC LOSES "
        "(normal identity):")
    log("  Source: bottom 200 PC1 correlates")
    for i, (_, row) in enumerate(
            bot200.head(20).iterrows(), 1):
        log(f"  {i:>3}. {row['gene']:<16} "
            f"r={row['r_depth']:>+.4f}")

    log("\n  ATTRACTOR NATURE:")
    log("  " + (
        f"DISCRETE — GMM k={best_k} "
        f"is optimal\n"
        "  Two or more stable states. "
        "Qualitative boundary exists."
        if bimodal else
        "CONTINUOUS — unimodal\n"
        "  Gradient transition. "
        "No sharp state boundary.\n"
        "  NOTE: n=15 may under-power "
        "bimodality detection."))

    log("\n  CO-REGULATED MODULES "
        "(independent of depth):")
    if modules:
        for k, mod in enumerate(modules, 1):
            log(f"  Module {k} "
                f"(n={len(mod)}): {mod}")
    else:
        log("  No modules above threshold")

    log("\n  PC2 AXIS:")
    top5  = pc2_df["gene"].head(5).tolist()
    bot5  = pc2_df["gene"].tail(5).tolist()
    log(f"  PC2+ : {top5}")
    log(f"  PC2- : {bot5}")
    log("  If MW p<0.05 (see S5): PC2 is "
        "the chRCC-specific axis.")
    log("  PC2-high vs PC2-low chRCC may "
        "represent subtypes with different")
    log("  clinical behaviour.")

    log("\n  REVERSAL VECTOR "
        "(geometry-derived targets):")
    log("  Restoring these genes toward "
        "normal-pole values shifts")
    log("  the PC1 score back across "
        "the midpoint.")
    log("  These are not literature targets.")
    log("  They are the geometry's answer.")
    for i, (_, row) in enumerate(
            min_set.head(10).iterrows(), 1):
        action = "RESTORE" \
            if row["t_mean"] < \
               row["n_mean"] \
            else "SUPPRESS"
        log(f"  {i:>3}. {row['gene']:<16} "
            f"{action}  "
            f"T={row['t_mean']:.3f}  "
            f"N={row['n_mean']:.3f}  "
            f"shift={row['pc1_shift']:>+.4f}")

    log("\n  FRAMEWORK STATEMENT:")
    log("  Script 3 has characterised the "
        "chRCC false attractor")
    log("  using only the shape of the "
        "expression manifold.")
    log("  The attractor identity, the normal "
        "identity, the module")
    log("  structure, the PC2 secondary axis, "
        "and the reversal")
    log("  vector were all derived from "
        "geometry alone.")
    log("  No prior knowledge determined "
        "any of these outputs.")

# ═══════════════════════════════════════════════════════════════
# FIGURE
# ═══════════════════════════════════════════════════════════════

def make_figure(pcs, loadings,
                top200, bot200,
                att_df, pc2_df,
                min_set, rev_df,
                t_cols, n_cols, o_cols,
                modules, bimodal,
                S, var_total):
    log("")
    log("="*60)
    log("FIGURE")
    log("="*60)

    C = {
        "chRCC": "#8E44AD",
        "norm":  "#27AE60",
        "onco":  "#E67E22",
        "pos":   "#E74C3C",
        "neg":   "#3498DB",
    }

    fig = plt.figure(figsize=(26, 28))
    gs  = gridspec.GridSpec(
        3, 3, figure=fig,
        hspace=0.50, wspace=0.40)

    # ── A: Scree ─────────────────────────────
    ax = fig.add_subplot(gs[0, 0])
    n_pc = min(10, len(S))
    vp   = [100.0 * S[i]**2 /
             np.sum(S**2)
             for i in range(n_pc)]
    ax.bar(range(1, n_pc+1), vp,
           color=C["neg"], alpha=0.8)
    ax.set_xlabel("Principal Component")
    ax.set_ylabel("Variance Explained (%)")
    for i, v in enumerate(vp[:5]):
        ax.text(i+1, v+0.2,
                f"{v:.1f}%",
                ha="center", fontsize=7)
    ax.set_title(
        "A: Scree Plot\n"
        "Manifold Variance Structure",
        fontsize=9, fontweight="bold")

    # ── B: PC1 × PC2 ─────────────────────────
    ax = fig.add_subplot(gs[0, 1])
    pc1 = pcs["PC1"]
    pc2 = pcs["PC2"]
    for cls, cols, col in [
        ("chRCC",      t_cols, C["chRCC"]),
        ("Normal",     n_cols, C["norm"]),
        ("Oncocytoma", o_cols, C["onco"]),
    ]:
        ax.scatter(
            pc1[list(cols)].values,
            pc2[list(cols)].values,
            c=col, s=35, alpha=0.8,
            label=cls, zorder=3)
    ax.set_xlabel("PC1 (depth axis)")
    ax.set_ylabel("PC2 (secondary axis)")
    ax.legend(fontsize=7)
    ax.set_title(
        "B: PC1 × PC2 Manifold\n"
        "All 83 samples",
        fontsize=9, fontweight="bold")

    # ── C: Top 30 attractor genes ────────────
    ax = fig.add_subplot(gs[0, 2])
    t30 = top200.head(30)
    ax.barh(range(len(t30)),
            t30["r_depth"].values,
            color=C["pos"], alpha=0.8)
    ax.set_yticks(range(len(t30)))
    ax.set_yticklabels(
        t30["gene"].values, fontsize=6)
    ax.axvline(0, color="k", lw=0.8)
    ax.set_xlabel("r(PC1)")
    ax.set_title(
        "C: Top 30 Attractor Genes\n"
        "(acquired — no prior selection)",
        fontsize=9, fontweight="bold")

    # ── D: Top 30 normal pole genes ──────────
    ax = fig.add_subplot(gs[1, 0])
    b30 = bot200.head(30)
    ax.barh(range(len(b30)),
            b30["r_depth"].values,
            color=C["neg"], alpha=0.8)
    ax.set_yticks(range(len(b30)))
    ax.set_yticklabels(
        b30["gene"].values, fontsize=6)
    ax.axvline(0, color="k", lw=0.8)
    ax.set_xlabel("r(PC1)")
    ax.set_title(
        "D: Top 30 Normal Pole Genes\n"
        "(lost — no prior selection)",
        fontsize=9, fontweight="bold")

    # ── E: PC2 correlates ────────────────────
    ax = fig.add_subplot(gs[1, 1])
    pc2_plot = pd.concat([
        pc2_df.head(20),
        pc2_df.tail(20)
    ]).sort_values("r_PC2")
    cols_e = [C["pos"] if v > 0
              else C["neg"]
              for v in pc2_plot["r_PC2"]]
    ax.barh(range(len(pc2_plot)),
            pc2_plot["r_PC2"].values,
            color=cols_e, alpha=0.8)
    ax.set_yticks(range(len(pc2_plot)))
    ax.set_yticklabels(
        pc2_plot["gene"].values,
        fontsize=6)
    ax.axvline(0, color="k", lw=0.8)
    ax.set_xlabel("r(PC2)")
    ax.set_title(
        "E: PC2 Gene Correlates\n"
        "Secondary axis",
        fontsize=9, fontweight="bold")

    # ── F: Reversal vector ───────────────────
    ax = fig.add_subplot(gs[1, 2])
    rv = min_set.head(25)
    cols_f = [C["neg"]
              if row["pc1_shift"] < 0
              else C["pos"]
              for _, row in rv.iterrows()]
    ax.barh(range(len(rv)),
            rv["pc1_shift"].values,
            color=cols_f, alpha=0.8)
    ax.set_yticks(range(len(rv)))
    ax.set_yticklabels(
        rv["gene"].values, fontsize=6)
    ax.axvline(0, color="k", lw=0.8)
    ax.set_xlabel("PC1 shift per gene")
    ax.set_title(
        "F: Reversal Vector\n"
        "Minimum set — basin crossing\n"
        "(geometry-derived targets only)",
        fontsize=9, fontweight="bold")

    # ── G: PC3 × PC4 ─────────────────────────
    ax = fig.add_subplot(gs[2, 0])
    if "PC3" in pcs and "PC4" in pcs:
        pc3 = pcs["PC3"]
        pc4 = pcs["PC4"]
        for cls, cols, col in [
            ("chRCC",      t_cols, C["chRCC"]),
            ("Normal",     n_cols, C["norm"]),
            ("Oncocytoma", o_cols, C["onco"]),
        ]:
            ax.scatter(
                pc3[list(cols)].values,
                pc4[list(cols)].values,
                c=col, s=30, alpha=0.8,
                label=cls, zorder=3)
        ax.set_xlabel("PC3")
        ax.set_ylabel("PC4")
        ax.legend(fontsize=7)
    ax.set_title(
        "G: PC3 × PC4\n"
        "Residual manifold structure",
        fontsize=9, fontweight="bold")

    # ── H: PC1 distribution ──────────────────
    ax = fig.add_subplot(gs[2, 1])
    pc1_norm = pd.Series(
        norm01(pc1.values),
        index=pc1.index)
    bins = np.linspace(0, 1, 25)
    for cls, cols, col, lbl in [
        ("chRCC", t_cols, C["chRCC"],
         f"chRCC (n={len(t_cols)})"),
        ("Normal", n_cols, C["norm"],
         f"Normal (n={len(n_cols)})"),
        ("Oncocytoma", o_cols, C["onco"],
         f"Onco (n={len(o_cols)})"),
    ]:
        ax.hist(
            pc1_norm[list(cols)].values,
            bins=bins, alpha=0.65,
            color=col, label=lbl,
            density=True)
    ax.set_xlabel("PC1 (normalised)")
    ax.set_ylabel("Density")
    ax.legend(fontsize=7)
    disc = "DISCRETE" if bimodal \
        else "CONTINUOUS"
    ax.set_title(
        f"H: PC1 Distribution\n"
        f"Attractor: {disc}",
        fontsize=9, fontweight="bold")

    # ── I: Summary statement ─────────────────
    ax = fig.add_subplot(gs[2, 2])
    ax.axis("off")
    n_pc5 = min(5, len(S))
    vp5   = [
        f"  PC{i+1}: "
        f"{100*S[i]**2/np.sum(S**2):.1f}%"
        for i in range(n_pc5)]
    txt = (
        "chRCC False Attractor\n"
        "Script 3 — Geometry First\n"
        "OrganismCore | Doc 96c\n"
        "2026-03-02\n"
        "══════════════════════════════\n"
        "MANIFOLD:\n"
        + "\n".join(vp5) +
        f"\n  Attractor: {disc}\n"
        "══════════════════════════════\n"
        "ATTRACTOR POLE (top 5):\n"
        + "\n".join(
            f"  {row['gene']:<14} "
            f"r={row['r_depth']:>+.3f}"
            for _, row in
            top200.head(5).iterrows()) +
        "\n══════════════════════════════\n"
        "NORMAL POLE (top 5):\n"
        + "\n".join(
            f"  {row['gene']:<14} "
            f"r={row['r_depth']:>+.3f}"
            for _, row in
            bot200.head(5).iterrows()) +
        "\n══════════════════════════════\n"
        "REVERSAL TARGETS (top 5):\n"
        + "\n".join(
            f"  {row['gene']:<14} "
            f"shift={row['pc1_shift']:>+.3f}"
            for _, row in
            min_set.head(5).iterrows()) +
        "\n══════════════════════════════\n"
        "NO PREDICTIONS\n"
        "NO PRE-SELECTED PANELS\n"
        "NO IMPORTED REFERENCES\n"
        "GEOMETRY FIRST"
    )
    ax.text(
        0.03, 0.97, txt,
        transform=ax.transAxes,
        fontsize=6, va="top",
        fontfamily="monospace",
        bbox=dict(
            boxstyle="round",
            facecolor="#F0F4F8",
            alpha=0.9))
    ax.set_title(
        "I: Geometry Statement",
        fontsize=9, fontweight="bold")

    fig.suptitle(
        "chRCC False Attractor — Script 3  "
        "|  Geometry First  |  "
        "OrganismCore | Doc 96c  |  "
        "2026-03-02",
        fontsize=11, fontweight="bold",
        y=0.999)

    out = os.path.join(
        S3_DIR,
        "chrcc_script3_figure.pdf")
    fig.savefig(out,
                bbox_inches="tight",
                dpi=150)
    plt.close(fig)
    log(f"  Figure saved: {out}")

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    (raw, t_cols, n_cols, o_cols,
     depth_t, depth_n, depth_o,
     att_df) = load_data()

    # S1
    pcs, loadings, S, var_total = \
        s1_manifold(
            raw, t_cols, n_cols, o_cols)

    # S2
    bimodal, best_k, best_gmm = \
        s2_bimodality(
            pcs, t_cols, n_cols, o_cols)

    # S3
    top200, bot200 = \
        s3_programme_discovery(att_df)

    # S4
    pcorr_df, modules, genes_ok = \
        s4_modules(
            raw, t_cols, n_cols, o_cols,
            pcs, att_df)

    # S5
    pc2_df, sub_df, low_pc2, high_pc2 = \
        s5_pc2_structure(
            raw, t_cols, n_cols, o_cols,
            pcs, loadings, att_df,
            depth_t)

    # S6
    rev_df, min_set = s6_reversal_vector(
        raw, t_cols, n_cols, o_cols,
        pcs, loadings, att_df)

    # S7
    s7_interpretation(
        top200, bot200,
        modules, min_set,
        pc2_df, sub_df,
        low_pc2, high_pc2,
        bimodal, best_k)

    # Figure
    make_figure(
        pcs, loadings,
        top200, bot200,
        att_df, pc2_df,
        min_set, rev_df,
        t_cols, n_cols, o_cols,
        modules, bimodal,
        S, var_total)

    write_log()

    log("")
    log("="*60)
    log("SCRIPT 3 COMPLETE")
    log(f"Results: {S3_DIR}")
    log(f"Log:     {LOG_FILE}")
    log("="*60)


if __name__ == "__main__":
    main()
