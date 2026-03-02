"""
ccRCC False Attractor — Script 4
LANDSCAPE DISCOVERY — GEOMETRY FIRST

Framework: OrganismCore
Document 94d-pre | 2026-03-02
Author: Eric Robert Lawson

THIS SCRIPT IS DIFFERENT FROM SCRIPTS 1-3.

Scripts 1-3 tested predictions.
Script 4 reveals the landscape.

The depth score from Script 1 is used as
the landscape coordinate — the axis along
which the geometry is measured. Everything
else is discovery. No gene panel. No
predicted directions. No confirmation target
except one:

SINGLE LOCKED PREDICTION:
  S4-P1: The full-genome depth scan will
         find at least 5 genes not in the
         S1-3 panels with |r| > 0.50 in
         TCGA. If it does not, the panels
         were complete. If it does, the
         panels were missing real biology.

EVERYTHING ELSE IS OPEN.

The eight discovery modules:

  Module A — Full genome depth scan
    Every gene in TCGA vs depth score
    No panel filter. Raw discovery.
    Top 100 pos + top 100 neg reported.
    Novel hits (not in S1-3 panels) flagged.

  Module B — Co-expression module discovery
    NMF k=2,3,4,5 on top 150 depth genes
    What coherent modules does the data
    contain? Do they map to known biology
    or reveal new structure?

  Module C — Full immune architecture scan
    ~50 immune marker genes
    All vs depth. Complete immune geometry.
    Special: checkpoint axis, M1/M2,
    T-cell exhaustion, DC maturation.

  Module D — Tumour purity test
    TCGA ESTIMATE-style proxy scores
    Does depth survive purity correction?
    Is depth measuring tumour biology
    or tumour content?

  Module E — Correlation network
    Top 40 depth genes
    Full pairwise matrix
    Hub identification
    Hub genes = landscape nodes

  Module F — Unsupervised tumour clustering
    k-means k=2,3,4,5 on top 60 depth genes
    Do clusters map to depth?
    Or reveal orthogonal biology?

  Module G — Normal field effect
    72 TCGA normals
    Does normal tissue variation predict
    paired tumour depth?
    Field effect = the landscape begins
    before malignant transformation.

  Module H — Splicing factor scan
    ~30 splicing factor / RNA-binding genes
    Are splicing regulators lost in
    deep ccRCC?
    Mechanism of identity gene suppression
    beyond chromatin.

DATASETS:
  TCGA-KIRC  HiSeqV2 — 534T / 72N
  GSE53757   GPL570  — 72T  (validation)
"""

import os
import gzip
import numpy as np
import pandas as pd
from scipy import stats
from scipy.cluster import hierarchy
from scipy.spatial.distance import pdist, squareform
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.colors as mcolors
from sklearn.decomposition import NMF
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings("ignore")

# ═══════════════════════════════════════════════════════
# PATHS
# ═══════════════════════════════════════════════════════

BASE_DIR = "./ccrcc_false_attractor/"
S1_DIR   = os.path.join(BASE_DIR, "results_s1")
S4_DIR   = os.path.join(BASE_DIR, "results_s4")
LOG_FILE = os.path.join(S4_DIR, "s4_log.txt")
os.makedirs(S4_DIR, exist_ok=True)

XENA_LOCAL   = os.path.join(
    BASE_DIR, "TCGA_KIRC_HiSeqV2.gz")
GEO_LOCAL    = os.path.join(
    BASE_DIR, "GSE53757_series_matrix.txt.gz")
GPL570_LOCAL = os.path.join(
    BASE_DIR, "GPL570_soft.txt")

# ═══════════════════════════════════════════════════════
# GENES KNOWN FROM SCRIPTS 1-3
# (used only to flag novel vs known)
# ═══════════════════════════════════════════════════════

S123_PANEL = set([
    # SW
    "UMOD","SLC34A1","SLC13A3","AGXT","PCK1",
    "SLC22A6","GATM","AQP1","FBP1","G6PC",
    "PCK2","SLC22A8","PAX8","HNF1A","HNF1B",
    "LHX1","ALDOB","CPT1A",
    # FA
    "CA9","VEGFA","EGLN3","SLC2A1","PDK1",
    "LDHA","EPAS1","SCD","ACLY","EZH2",
    "SLC2A3","VIM","TWIST1","SNAI1","SNAI2",
    "ZEB1","ZEB2","MMP2","MMP9","FN1",
    "CDH1","CDH2","EPCAM","VIM","FAP","ACTA2",
    "COL1A1","TGFB1","WNT5A","POSTN","MMP14",
    "MYC","MKI67","CDC20","TOP2A","BIRC5",
    "SOX4","PROM1","CD44","CCNB1","CDK4",
    # Chromatin
    "VHL","PBRM1","BAP1","SETD2","KDM5C",
    "KDM6A","KDM1A","ARID1A","SMARCA4",
    "SMARCB1","EP300","CREBBP","EZH1","SUZ12",
    "EED","DNMT3A","TET2","ASXL1","BCOR",
    "HDAC1","HDAC2","RCOR1","JARID2","HDAC2",
    # Cabo
    "MET","HGF","AXL","GAS6","MERTK","TYRO3",
    "ANGPT2","TEK","KDR","FLT1","PDGFRA",
    "PDGFRB","FGF2","FGFR1","RET","NTRK1",
    "VEGFC","VEGFD",
    # Lipid
    "FASN","PLIN2","HMGCR","SQLE","ACACA",
    "CPT1B","HADHA","PPARA","PPARG","SREBF1",
    "SREBF2","MLXIPL","HIF1A","ARNT",
    # Immune (tested)
    "CD274","CD8A","FOXP3","CD68","PRF1",
    "HAVCR2","LAG3","PDCD1","CTLA4",
    # Other
    "FGFR2","IDH1","IDH2","MTOR","PTEN",
    "CTNNB1","STAT3","KRT7","KRT19","ESRP1",
    "ESRP2","CLDN4","OCLN","ITGB6","CCND1",
    "FBP1","SLC34A1","TWIST2","MMP2","FN1",
    "COL1A2","COL3A1","COL5A1","POSTN",
    "PDGFRA","EGFR","ERBB2",
])

# ═══════════════════════════════════════════════════════
# IMMUNE PANEL — MODULE C
# ═══════════════════════════════════════════════════════

IMMUNE_PANEL = [
    # T cells
    "CD3D","CD3E","CD3G","CD8A","CD8B",
    "CD4","CD2","IL7R","TCF7","LEF1",
    # T effector / cytotoxic
    "GZMA","GZMB","GZMK","PRF1","IFNG",
    "TNF","FASLG","NKG7",
    # T exhaustion
    "PDCD1","LAG3","HAVCR2","TIGIT",
    "CTLA4","TOX","ENTPD1","CXCL13",
    # T regulatory
    "FOXP3","IL2RA","IKZF2","TNFRSF18",
    # NK cells
    "NCAM1","KLRB1","KLRD1","KLRK1",
    "NCR1","NCR3","FCGR3A","TYROBP",
    # B cells
    "CD19","CD79A","CD79B","MS4A1",
    "IGHG1","IGKC",
    # Macrophage / monocyte
    "CD68","CD163","MRC1","MSR1",
    "ITGAM","CSF1R","FCGR1A","ADGRE1",
    "S100A8","S100A9","CXCL8","IL1B",
    "IL10","TGFB1",
    # Dendritic cells
    "ITGAX","CD1C","CLEC9A","XCR1",
    "CCR7","CCL17","LAMP3",
    # Mast cells
    "KIT","MS4A2","CPA3",
    # Checkpoints / ligands
    "CD274","CD80","CD86","CD276",
    "PDCD1LG2","LGALS9","CEACAM1",
    # Tumour immune evasion
    "HLA-A","HLA-B","HLA-C",
    "B2M","TAP1","TAPBP",
    # Proliferation (immune)
    "MKI67",
]

# ═══════════════════════════════════════════════════════
# SPLICING FACTOR PANEL — MODULE H
# ═══════════════════════════════════════════════════════

SPLICING_PANEL = [
    # Epithelial splicing regulators
    "ESRP1","ESRP2","RBFOX1","RBFOX2",
    "RBFOX3","MBNL1","MBNL2","QKI",
    "PTBP1","PTBP2","HNRNPA1","HNRNPA2B1",
    "HNRNPC","HNRNPD","HNRNPL","HNRNPM",
    "TRA2A","TRA2B","SRSF1","SRSF2",
    "SRSF3","SRSF4","SRSF5","SRSF6",
    "SRSF7","SRSF9","SRSF10","SRSF11",
    # SF3B complex (SF3B1 — ICC finding)
    "SF3B1","SF3B2","SF3B3","SF3A1",
    "SF3A2","SF3A3",
    # U2AF complex
    "U2AF1","U2AF2",
    # Clk kinases (SR protein phosphorylation)
    "CLK1","CLK2","CLK3","CLK4",
    "SRPK1","SRPK2",
    # NMD
    "UPF1","UPF2","UPF3B",
    # Other
    "DDX5","DDX17","DHX9","KHSRP",
    "NOVA1","NOVA2","ELAVL1","ELAVL2",
]

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

def novel(gene):
    """Returns True if gene was NOT in S1-3 panels."""
    return gene.upper() not in S123_PANEL

# ═══════════════════════════════════════════════════════
# DATA LOADING — FULL GENOME
# ════���══════════════════════════════════════════════════

def load_tcga_full():
    """
    Load ALL genes from TCGA-KIRC.
    No panel filter.
    Returns expr (genes×samples DataFrame),
    t_cols (tumour sample IDs),
    n_cols (normal sample IDs).
    """
    log("Loading TCGA-KIRC — FULL GENOME...")
    with gzip.open(XENA_LOCAL, "rt") as f:
        raw = pd.read_csv(f, sep="\t",
                          index_col=0)

    # Tumour vs normal by sample code
    t_cols, n_cols = [], []
    for s in raw.columns:
        p = s.split("-")
        if len(p) >= 4:
            code = p[3][:2]
            if code.isdigit():
                ci = int(code)
                if 1 <= ci <= 9:
                    t_cols.append(s)
                elif 10 <= ci <= 19:
                    n_cols.append(s)

    log(f"  Total genes: {len(raw):,}")
    log(f"  Tumour samples: {len(t_cols)}")
    log(f"  Normal samples: {len(n_cols)}")
    return raw, t_cols, n_cols


def _parse_symbol_geo(raw_sym):
    if not raw_sym or not raw_sym.strip():
        return None
    first = raw_sym.split("///")[0].strip()
    if not first or first in (
            "---", "N/A", "NA", "null"):
        return None
    tokens = first.split()
    if not tokens:
        return None
    sym = tokens[0].upper()
    if not sym or sym in (
            "---", "N/A", "NA", "NULL"):
        return None
    return sym


def load_geo_panel(genes_needed):
    """
    Load GEO GSE53757 for a specific gene set.
    Used for validation of novel Module-A hits.
    """
    log("Loading GSE53757 for validation...")
    if not os.path.exists(GPL570_LOCAL):
        log("  GPL570 not found — skip GEO")
        return None, None

    gw = set(g.upper() for g in genes_needed)
    probe_map = {}
    with open(GPL570_LOCAL, "r",
              encoding="utf-8",
              errors="replace") as fh:
        header   = None
        id_c     = None
        sym_c    = None
        in_table = False
        for raw_line in fh:
            line = raw_line.rstrip("\n")
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
                id_c   = next(
                    (i for i, h in
                     enumerate(lower)
                     if h == "id"), 0)
                sym_c  = None
                for kw in [
                    "gene symbol",
                    "gene_symbol",
                    "symbol",
                ]:
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
            if len(parts) <= max(id_c,
                                  sym_c):
                continue
            pid = parts[id_c].strip()
            sym = _parse_symbol_geo(
                parts[sym_c].strip())
            if sym and sym in gw:
                probe_map[pid] = sym

    # Matrix
    sample_ids   = []
    source_names = []
    with gzip.open(GEO_LOCAL, "rt",
                   encoding="utf-8",
                   errors="replace") as fh:
        for raw_line in fh:
            line = raw_line.rstrip()
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
        values, index=probe_ids,
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
        existing = gene_rows.get(sym)
        if existing is None:
            gene_rows[sym] = probe_df.loc[pid]
        else:
            nv = float(
                probe_df.loc[pid,
                             t_cols_g].var()
                if t_cols_g else
                probe_df.loc[pid].var())
            ov = float(
                existing[t_cols_g].var()
                if t_cols_g else
                existing.var())
            if nv > ov:
                gene_rows[sym] = \
                    probe_df.loc[pid]

    if not gene_rows:
        return None, None

    gene_df = pd.DataFrame(gene_rows).T
    log(f"  GEO genes={len(gene_df)}, "
        f"tumours={len(t_cols_g)}")
    return gene_df, t_cols_g


def load_depth(tag="tcga"):
    p = os.path.join(
        S1_DIR,
        f"depth_scores_{tag}.csv")
    d = pd.read_csv(p, index_col="sample_id")
    return d["depth_score"]

# ═══════════════════════════════════════════════════════
# MODULE A — FULL GENOME DEPTH SCAN
# ═══════════════════════════════════════════════════════

def module_a_genome_scan(expr_full, t_cols,
                         depth):
    log("")
    log("=" * 65)
    log("MODULE A — FULL GENOME DEPTH SCAN")
    log("No panel. Every gene. Raw discovery.")
    log("=" * 65)

    d = depth.reindex(t_cols).dropna()
    ti = list(d.index)

    log(f"  Computing r(gene, depth) for "
        f"{len(expr_full):,} genes "
        f"across n={len(ti)} tumours...")
    log("  (This may take 30-60 seconds)")

    # Vectorised: compute all correlations
    # at once using the depth array
    d_arr = d.values.astype(float)
    d_c   = d_arr - d_arr.mean()
    d_std = np.sqrt((d_c ** 2).sum())

    genes  = []
    rs     = []
    ps_arr = []

    chunk_size = 1000
    gene_list  = list(expr_full.index)
    n_genes    = len(gene_list)

    for start in range(0, n_genes,
                       chunk_size):
        chunk = gene_list[
            start:start + chunk_size]
        mat = expr_full.loc[
            chunk, ti
        ].values.astype(float)

        for i, gene in enumerate(chunk):
            gv = mat[i]
            m  = np.isfinite(gv) \
                 & np.isfinite(d_arr)
            if m.sum() < 10:
                continue
            gv_m  = gv[m]
            d_m   = d_arr[m]
            gc    = gv_m - gv_m.mean()
            g_std = np.sqrt(
                (gc ** 2).sum())
            d_cm  = d_m - d_m.mean()
            d_stm = np.sqrt(
                (d_cm ** 2).sum())
            if g_std == 0 or d_stm == 0:
                continue
            r = (gc * d_cm).sum() / (
                g_std * d_stm)
            r = float(np.clip(r, -1, 1))
            n_m = m.sum()
            # t-statistic for p-value
            if abs(r) >= 1.0:
                p = 0.0
            else:
                t = r * np.sqrt(
                    (n_m - 2) /
                    (1 - r ** 2))
                p = float(
                    2 * stats.t.sf(
                        abs(t), df=n_m - 2))
            genes.append(gene)
            rs.append(r)
            ps_arr.append(p)

    df = pd.DataFrame({
        "gene": genes,
        "r":    rs,
        "p":    ps_arr,
    })
    df["abs_r"]  = df.r.abs()
    df["novel"]  = df.gene.apply(novel)
    df = df.sort_values("abs_r",
                        ascending=False)
    df.to_csv(os.path.join(
        S4_DIR, "genome_scan_full.csv"),
        index=False)

    log(f"\n  Total genes computed: "
        f"{len(df):,}")
    log(f"  Genes |r|>0.50: "
        f"{(df.abs_r > 0.50).sum():,}")
    log(f"  Genes |r|>0.60: "
        f"{(df.abs_r > 0.60).sum():,}")
    log(f"  Genes |r|>0.70: "
        f"{(df.abs_r > 0.70).sum():,}")

    # Novel hits
    novel_hits = df[df.novel &
                    (df.abs_r > 0.50)]
    log(f"\n  NOVEL HITS |r|>0.50 "
        f"(not in S1-3 panels): "
        f"{len(novel_hits)}")

    # S4-P1 verdict
    log("")
    if len(novel_hits) >= 5:
        log("  S4-P1 CONFIRMED: >= 5 novel "
            "genes with |r|>0.50 ✓")
        log("  The S1-3 panels were INCOMPLETE.")
        log("  The landscape contained real "
            "biology that was missed.")
    else:
        log(f"  S4-P1 NOT CONFIRMED: only "
            f"{len(novel_hits)} novel genes "
            f"with |r|>0.50")
        log("  The S1-3 panels were largely "
            "complete.")

    # Top 50 positive
    top_pos = df[df.r > 0].head(50)
    log("")
    log("  TOP 50 POSITIVE (deeper=higher):")
    log(f"  {'Rank':<5} {'Gene':<14}"
        f" {'r':>8}  {'p':>10}  "
        f"{'novel':>6}  panel_status")
    log(f"  {'-'*5} {'-'*14}"
        f" {'-'*8}  {'-'*10}  "
        f"{'-'*6}  {'-'*14}")
    for i, (_, row) in enumerate(
            top_pos.iterrows(), 1):
        nv = "NEW" if row.novel else "known"
        log(f"  {i:<5} {row.gene:<14}"
            f" {row.r:>+8.4f}  "
            f"{fmt_p(row.p):>10}  "
            f"{nv:>6}")

    # Top 50 negative
    top_neg = df[df.r < 0].head(50)
    log("")
    log("  TOP 50 NEGATIVE (deeper=lower):")
    log(f"  {'Rank':<5} {'Gene':<14}"
        f" {'r':>8}  {'p':>10}  "
        f"{'novel':>6}")
    log(f"  {'-'*5} {'-'*14}"
        f" {'-'*8}  {'-'*10}  "
        f"{'-'*6}")
    for i, (_, row) in enumerate(
            top_neg.iterrows(), 1):
        nv = "NEW" if row.novel else "known"
        log(f"  {i:<5} {row.gene:<14}"
            f" {row.r:>+8.4f}  "
            f"{fmt_p(row.p):>10}  "
            f"{nv:>6}")

    # Novel hits detail
    if len(novel_hits) > 0:
        log("")
        log("  NOVEL HITS — DETAIL:")
        log(f"  {'Gene':<14} {'r':>8}"
            f"  {'p':>10}  direction")
        log(f"  {'-'*14} {'-'*8}"
            f"  {'-'*10}  {'-'*12}")
        for _, row in novel_hits.iterrows():
            direction = (
                "↑ deeper"
                if row.r > 0
                else "↓ shallower")
            log(f"  {row.gene:<14}"
                f" {row.r:>+8.4f}  "
                f"{fmt_p(row.p):>10}  "
                f"{direction}")

    return df, novel_hits

# ═══════════════════════════════════════════════════════
# MODULE B — CO-EXPRESSION MODULE DISCOVERY
# ═══════════════════════════════════════════════════════

def module_b_nmf_modules(expr_full, t_cols,
                         depth, genome_df):
    log("")
    log("=" * 65)
    log("MODULE B — CO-EXPRESSION MODULE "
        "DISCOVERY (NMF)")
    log("Data-driven. No panel assumption.")
    log("=" * 65)

    d = depth.reindex(t_cols).dropna()
    ti = list(d.index)

    # Use top 150 depth genes (by |r|)
    top150 = genome_df.head(150)
    genes  = [g for g in top150.gene
              if g in expr_full.index][:150]

    log(f"  NMF input: top {len(genes)} "
        f"depth-correlated genes")

    mat = expr_full.loc[genes, ti].values\
                   .astype(float)
    # Replace nan with gene mean
    for i in range(mat.shape[0]):
        row = mat[i]
        mask = ~np.isfinite(row)
        if mask.any():
            row[mask] = np.nanmean(row)
        mat[i] = row

    # Shift to non-negative for NMF
    mat_nn = mat - mat.min(axis=1,
                           keepdims=True)
    mat_nn = np.clip(mat_nn, 0, None)

    results = {}
    for k in [2, 3, 4, 5]:
        log(f"\n  NMF k={k}...")
        try:
            model = NMF(
                n_components=k,
                max_iter=500,
                random_state=42)
            W = model.fit_transform(mat_nn.T)
            H = model.components_

            # W: samples × k — component scores
            # H: k × genes — gene loadings

            # Name each component by its
            # top 5 genes
            component_names = []
            for ki in range(k):
                gene_scores = H[ki]
                top_idx = np.argsort(
                    gene_scores)[::-1][:5]
                top_genes = [genes[j]
                             for j in top_idx]
                component_names.append(
                    "/".join(top_genes[:3]))
                log(f"    Component {ki+1}: "
                    f"top genes = "
                    f"{top_genes}")

            # r(component score, depth)
            log(f"    r(component, depth):")
            for ki in range(k):
                r, p = safe_r(
                    W[:, ki], d.values)
                direction = (
                    "↑ depth"
                    if r > 0
                    else "↓ depth")
                log(f"      C{ki+1}: "
                    f"r={r:+.4f} "
                    f"p={fmt_p(p)} "
                    f"{direction}")

            # Reconstruction error
            recon = model.reconstruction_err_
            log(f"    Reconstruction error: "
                f"{recon:.4f}")

            results[k] = {
                "W":     W,
                "H":     H,
                "genes": genes,
                "names": component_names,
                "error": recon,
            }
        except Exception as ex:
            log(f"    NMF k={k} failed: {ex}")

    # Hierarchical clustering
    log("")
    log("  HIERARCHICAL CLUSTERING "
        "(top 60 depth genes):")
    top60 = [g for g in
             genome_df.head(60).gene
             if g in expr_full.index][:60]
    if len(top60) >= 10:
        mat60 = expr_full.loc[
            top60, ti].values.astype(float)
        for i in range(mat60.shape[0]):
            row = mat60[i]
            mask = ~np.isfinite(row)
            if mask.any():
                row[mask] = np.nanmean(row)
            mat60[i] = row

        # Gene-gene correlation matrix
        corr = np.corrcoef(mat60)
        corr = np.clip(corr, -1, 1)
        np.fill_diagonal(corr, 1.0)

        dist = 1 - np.abs(corr)
        np.clip(dist, 0, None, out=dist)

        try:
            linkage = hierarchy.linkage(
                squareform(dist),
                method="ward")
            order = hierarchy.leaves_list(
                linkage)
            ordered_genes = [
                top60[i] for i in order]

            # Report clusters
            clusters = hierarchy.fcluster(
                linkage, t=3,
                criterion="maxclust")
            for ci in range(1, 4):
                cg = [top60[j]
                      for j, c in
                      enumerate(clusters)
                      if c == ci]
                log(f"    Cluster {ci} "
                    f"({len(cg)} genes): "
                    f"{cg[:8]}...")
        except Exception as ex:
            log(f"  Clustering failed: {ex}")
            ordered_genes = top60

        results["hclust_order"] = (
            top60, ordered_genes,
            corr)

    return results

# ═══════════════════════════════════════════════════════
# MODULE C — FULL IMMUNE ARCHITECTURE
# ═══════════════════════════════════════════════════════

def module_c_immune_scan(expr_full, t_cols,
                         depth):
    log("")
    log("=" * 65)
    log("MODULE C — FULL IMMUNE ARCHITECTURE")
    log("Complete immune geometry vs depth.")
    log("=" * 65)

    d = depth.reindex(t_cols).dropna()

    rows = []
    for gene in IMMUNE_PANEL:
        if gene not in expr_full.index:
            continue
        v = pd.Series(
            expr_full.loc[gene, t_cols]\
                     .values,
            index=t_cols,
        ).reindex(d.index)
        r, p = safe_r(v.values, d.values)
        if np.isnan(r):
            continue
        rows.append({
            "gene": gene,
            "r":    r,
            "p":    p,
        })

    df = pd.DataFrame(rows).sort_values(
        "r", ascending=False)
    df.to_csv(os.path.join(
        S4_DIR, "immune_scan.csv"),
        index=False)

    log(f"\n  {'Gene':<12} {'r(depth)':>10}"
        f"  {'p':>10}  tier  cell_type")
    log(f"  {'-'*12} {'-'*10}  "
        f"{'-'*10}  {'-'*5}  {'-'*15}")

    # Cell type map for annotation
    cell_type = {
        "CD3D":"T-cell","CD3E":"T-cell",
        "CD3G":"T-cell","CD8A":"CD8-T",
        "CD8B":"CD8-T","CD4":"CD4-T",
        "CD2":"T-cell","IL7R":"T-mem",
        "TCF7":"T-naive","LEF1":"T-naive",
        "GZMA":"Cytotoxic","GZMB":"Cytotoxic",
        "GZMK":"Cytotoxic","PRF1":"Cytotoxic",
        "IFNG":"Th1","TNF":"Th1",
        "FASLG":"Cytotoxic","NKG7":"NK/CTL",
        "PDCD1":"Exhaustion","LAG3":"Exhaustion",
        "HAVCR2":"Exhaustion","TIGIT":"Exhaustion",
        "CTLA4":"Exhaustion","TOX":"Exhaustion",
        "ENTPD1":"Exhaustion",
        "CXCL13":"Exhaustion",
        "FOXP3":"Treg","IL2RA":"Treg",
        "IKZF2":"Treg","TNFRSF18":"Treg",
        "NCAM1":"NK","KLRB1":"NK",
        "KLRD1":"NK","KLRK1":"NK",
        "NCR1":"NK","NCR3":"NK",
        "FCGR3A":"NK/Mono",
        "TYROBP":"NK/Macro",
        "CD19":"B-cell","CD79A":"B-cell",
        "CD79B":"B-cell","MS4A1":"B-cell",
        "IGHG1":"Plasma","IGKC":"Plasma",
        "CD68":"Macrophage",
        "CD163":"M2-Macro","MRC1":"M2-Macro",
        "MSR1":"M2-Macro","ITGAM":"Monocyte",
        "CSF1R":"Macrophage",
        "FCGR1A":"Mono/Macro",
        "ADGRE1":"Macrophage",
        "S100A8":"MDSC/Mono",
        "S100A9":"MDSC/Mono",
        "CXCL8":"Neutrophil/MDSC",
        "IL1B":"Inflammatory",
        "IL10":"Immunosuppressive",
        "TGFB1":"Immunosuppressive",
        "ITGAX":"DC","CD1C":"cDC2",
        "CLEC9A":"cDC1","XCR1":"cDC1",
        "CCR7":"mDC","CCL17":"mDC",
        "LAMP3":"mDC","KIT":"Mast",
        "MS4A2":"Mast","CPA3":"Mast",
        "CD274":"PDL1","CD80":"B7-1",
        "CD86":"B7-2","CD276":"B7-H3",
        "PDCD1LG2":"PDL2","LGALS9":"Gal9",
        "CEACAM1":"Checkpoint",
        "HLA-A":"MHC-I","HLA-B":"MHC-I",
        "HLA-C":"MHC-I","B2M":"MHC-I",
        "TAP1":"Ag-present",
        "TAPBP":"Ag-present",
        "MKI67":"Proliferation",
    }

    for _, row in df.iterrows():
        tier = (
            "T1" if abs(row.r) >= 0.40
            else "T2" if abs(row.r) >= 0.25
            else "T3" if abs(row.r) >= 0.10
            else "  ")
        ct = cell_type.get(row.gene, "")
        log(f"  {row.gene:<12}"
            f" {row.r:>+10.4f}  "
            f"{fmt_p(row.p):>10}  "
            f"{tier:>5}  {ct}")

    # Key structural findings
    log("")
    log("  KEY STRUCTURAL FINDINGS:")

    # Checkpoint axis
    log("  Checkpoint axis:")
    for gene in ["CD274","PDCD1","LAG3",
                 "HAVCR2","TIGIT","CTLA4",
                 "PDCD1LG2","CD80","CD86"]:
        row = df[df.gene == gene]
        if len(row) > 0:
            r = float(row.iloc[0].r)
            p = float(row.iloc[0].p)
            log(f"    {gene:<12}"
                f" r={r:>+7.4f}"
                f" p={fmt_p(p)}")

    # Cytotoxic arm
    log("  Cytotoxic / effector arm:")
    for gene in ["CD8A","GZMB","PRF1",
                 "NKG7","IFNG","GZMA",
                 "GZMK","FASLG"]:
        row = df[df.gene == gene]
        if len(row) > 0:
            r = float(row.iloc[0].r)
            p = float(row.iloc[0].p)
            log(f"    {gene:<12}"
                f" r={r:>+7.4f}"
                f" p={fmt_p(p)}")

    # Suppressive arm
    log("  Suppressive arm:")
    for gene in ["FOXP3","IL10","TGFB1",
                 "CD163","MRC1","IL2RA",
                 "S100A8","S100A9","CXCL8"]:
        row = df[df.gene == gene]
        if len(row) > 0:
            r = float(row.iloc[0].r)
            p = float(row.iloc[0].p)
            log(f"    {gene:<12}"
                f" r={r:>+7.4f}"
                f" p={fmt_p(p)}")

    # MHC / antigen presentation
    log("  Antigen presentation:")
    for gene in ["HLA-A","HLA-B","HLA-C",
                 "B2M","TAP1","TAPBP"]:
        row = df[df.gene == gene]
        if len(row) > 0:
            r = float(row.iloc[0].r)
            p = float(row.iloc[0].p)
            log(f"    {gene:<12}"
                f" r={r:>+7.4f}"
                f" p={fmt_p(p)}")

    # CD274 vs FOXP3 independence test
    log("")
    log("  CD274 × FOXP3 INDEPENDENCE TEST:")
    for g1, g2 in [("CD274","FOXP3"),
                   ("CD8A","FOXP3"),
                   ("CD274","CD8A"),
                   ("CD8A","CD274"),
                   ("GZMB","FOXP3")]:
        if (g1 in expr_full.index and
                g2 in expr_full.index):
            v1 = pd.Series(
                expr_full.loc[
                    g1, t_cols].values,
                index=t_cols,
            ).reindex(d.index)
            v2 = pd.Series(
                expr_full.loc[
                    g2, t_cols].values,
                index=t_cols,
            ).reindex(d.index)
            r, p = safe_r(
                v1.values, v2.values)
            status = (
                "INDEPENDENT"
                if abs(r) < 0.20
                else "COUPLED"
                if abs(r) >= 0.40
                else "WEAK")
            log(f"  r({g1},{g2}) = "
                f"{r:>+7.4f}  "
                f"p={fmt_p(p)}  "
                f"{status}")

    return df

# ═══════════════════════════════════════════════════════
# MODULE D — TUMOUR PURITY TEST
# ═══════════════════════════════════════════════════════

def module_d_purity(expr_full, t_cols,
                    depth):
    log("")
    log("=" * 65)
    log("MODULE D — TUMOUR PURITY TEST")
    log("Does depth survive purity?")
    log("=" * 65)

    d = depth.reindex(t_cols).dropna()

    # ESTIMATE-proxy: tumour purity correlates
    # Immune score proxy: mean of CD3D+CD8A+NKG7
    # Stromal score proxy: mean of COL1A1+FAP+ACTA2
    # Tumour score proxy: inverse of above

    immune_genes = [
        g for g in [
            "CD3D","CD8A","NKG7","CD68",
            "FOXP3","PRF1","GZMB"]
        if g in expr_full.index]
    stromal_genes = [
        g for g in [
            "FAP","ACTA2","COL1A1",
            "POSTN","FN1","VIM"]
        if g in expr_full.index]
    tumour_genes_pos = [
        g for g in [
            "CA9","EPAS1","SLC2A1",
            "LDHA","MKI67","EZH2"]
        if g in expr_full.index]
    tumour_genes_neg = [
        g for g in [
            "FBP1","SLC22A6","AQP1",
            "UMOD","G6PC","PCK1"]
        if g in expr_full.index]

    def proxy_score(pos_genes, neg_genes,
                    name):
        if not pos_genes and not neg_genes:
            log(f"  {name}: no genes")
            return None
        parts = []
        if pos_genes:
            mat = pd.DataFrame({
                g: pd.Series(
                    expr_full.loc[
                        g, t_cols].values,
                    index=t_cols,
                ).reindex(d.index)
                for g in pos_genes
            })
            parts.append(
                norm01(mat.mean(
                    axis=1).values))
        if neg_genes:
            mat = pd.DataFrame({
                g: pd.Series(
                    expr_full.loc[
                        g, t_cols].values,
                    index=t_cols,
                ).reindex(d.index)
                for g in neg_genes
            })
            parts.append(
                1 - norm01(mat.mean(
                    axis=1).values))
        score = np.mean(parts, axis=0)
        r, p = safe_r(score, d.values)
        log(f"  {name}: r(vs depth)="
            f"{r:>+7.4f}  p={fmt_p(p)}")
        return pd.Series(score,
                         index=d.index)

    log("  Proxy scores vs depth:")
    immune_score = proxy_score(
        immune_genes, [],
        "Immune score proxy  ")
    stromal_score = proxy_score(
        stromal_genes, [],
        "Stromal score proxy ")
    tumour_score = proxy_score(
        tumour_genes_pos,
        tumour_genes_neg,
        "Tumour score proxy  ")

    # Purity test: if depth is mainly
    # purity-driven, then r(immune,depth)
    # should be negative (immune = non-tumour)
    # and r(tumour,depth) >> r(immune,depth)
    log("")
    log("  PURITY INTERPRETATION:")
    if immune_score is not None:
        r_imm, _ = safe_r(
            immune_score.values, d.values)
        if r_imm < -0.10:
            log("  r(immune, depth) < 0 —")
            log("  immune infiltration is LOWER")
            log("  in deeper tumours.")
            log("  This is consistent with")
            log("  immune exclusion in deep ccRCC.")
            log("  Depth is NOT simply purity.")
        elif r_imm > 0.10:
            log("  r(immune, depth) > 0 —")
            log("  MORE immune infiltration in")
            log("  deeper tumours.")
            log("  Depth score may conflate")
            log("  tumour and immune biology.")
        else:
            log("  r(immune, depth) near 0 —")
            log("  immune infiltration is")
            log("  depth-agnostic.")

    # Cross-correlations
    log("")
    log("  Cross-correlations:")
    for s1, s2, name in [
        (immune_score,  stromal_score,
         "r(immune, stromal)   "),
        (immune_score,  tumour_score,
         "r(immune, tumour)    "),
        (stromal_score, tumour_score,
         "r(stromal, tumour)   "),
    ]:
        if s1 is not None and s2 is not None:
            r, p = safe_r(s1.values,
                          s2.values)
            log(f"  {name} = {r:>+7.4f}"
                f"  p={fmt_p(p)}")

    return immune_score, stromal_score, \
           tumour_score

# ═══════════════════════════════════════════════════════
# MODULE E — CORRELATION NETWORK
# ═══════════════════════════════════════════════════════

def module_e_network(expr_full, t_cols,
                     depth, genome_df):
    log("")
    log("=" * 65)
    log("MODULE E — CORRELATION NETWORK")
    log("Hub genes = landscape nodes.")
    log("=" * 65)

    d = depth.reindex(t_cols).dropna()
    ti = list(d.index)

    # Top 40 depth genes
    top40 = [g for g in
             genome_df.head(40).gene
             if g in expr_full.index][:40]

    log(f"  Network: {len(top40)} genes")
    log(f"  Computing {len(top40)**2 // 2} "
        f"pairwise correlations...")

    mat = expr_full.loc[top40, ti]\
                   .values.astype(float)
    # Fill nan
    for i in range(mat.shape[0]):
        row = mat[i]
        mask = ~np.isfinite(row)
        if mask.any():
            row[mask] = np.nanmean(row)
        mat[i] = row

    corr = np.corrcoef(mat)
    corr = np.clip(corr, -1, 1)
    np.fill_diagonal(corr, 0.0)

    # Hub score = mean |r| with all others
    hub_scores = np.abs(corr).mean(axis=1)
    hub_order  = np.argsort(
        hub_scores)[::-1]

    log("")
    log("  HUB GENES (by mean |r| "
        "with top-40 network):")
    log(f"  {'Rank':<5} {'Gene':<14}"
        f" {'hub_score':>10}"
        f" {'depth_r':>9}"
        f" {'novel':>6}")
    log(f"  {'-'*5} {'-'*14}"
        f" {'-'*10} {'-'*9} {'-'*6}")

    depth_rs = dict(
        zip(genome_df.gene,
            genome_df.r))

    for rank, idx in enumerate(
            hub_order[:20], 1):
        gene  = top40[idx]
        hs    = hub_scores[idx]
        dr    = depth_rs.get(gene, np.nan)
        nv    = "NEW" if novel(gene) \
            else "known"
        log(f"  {rank:<5} {gene:<14}"
            f" {hs:>10.4f}"
            f" {dr:>+9.4f}"
            f" {nv:>6}")

    # Strongest pairwise edges
    log("")
    log("  STRONGEST EDGES (|r| > 0.70):")
    log(f"  {'Gene A':<14} {'Gene B':<14}"
        f" {'r':>8}  type")
    log(f"  {'-'*14} {'-'*14}"
        f" {'-'*8}  {'-'*10}")
    edges = []
    for i in range(len(top40)):
        for j in range(i + 1, len(top40)):
            r = corr[i, j]
            if abs(r) >= 0.70:
                edges.append(
                    (top40[i], top40[j], r))
    edges.sort(key=lambda x: -abs(x[2]))
    for ga, gb, r in edges[:30]:
        edge_type = (
            "CO-ACTIVATE"
            if r > 0
            else "OPPOSE")
        log(f"  {ga:<14} {gb:<14}"
            f" {r:>+8.4f}  {edge_type}")

    # Save adjacency
    corr_df = pd.DataFrame(
        corr, index=top40, columns=top40)
    corr_df.to_csv(os.path.join(
        S4_DIR, "network_corr.csv"))

    return corr, top40, hub_scores

# ═══════════════════════════════════════════════════════
# MODULE F — UNSUPERVISED CLUSTERING
# ═══════════════════════════════════════════════════════

def module_f_clustering(expr_full, t_cols,
                        depth, genome_df):
    log("")
    log("=" * 65)
    log("MODULE F — UNSUPERVISED CLUSTERING")
    log("Do the data contain natural "
        "subgroups beyond depth?")
    log("=" * 65)

    d = depth.reindex(t_cols).dropna()
    ti = list(d.index)

    top60 = [g for g in
             genome_df.head(60).gene
             if g in expr_full.index][:60]

    mat = expr_full.loc[top60, ti]\
                   .values.T.astype(float)
    # Fill nan per column
    col_means = np.nanmean(mat, axis=0)
    for j in range(mat.shape[1]):
        mask = ~np.isfinite(mat[:, j])
        if mask.any():
            mat[mask, j] = col_means[j]

    scaler = StandardScaler()
    mat_sc = scaler.fit_transform(mat)

    best_k = None
    best_sil = -1

    for k in [2, 3, 4, 5]:
        log(f"\n  k-means k={k}:")
        try:
            km = KMeans(
                n_clusters=k,
                random_state=42,
                n_init=10)
            labels = km.fit_predict(mat_sc)

            # Silhouette (approximate via
            # within/between cluster variance)
            inertia = km.inertia_
            log(f"    Inertia: {inertia:.2f}")

            # Depth by cluster
            depth_arr = d.values
            for ci in range(k):
                mask_c = labels == ci
                d_c    = depth_arr[mask_c]
                n_c    = mask_c.sum()
                log(f"    Cluster {ci+1}: "
                    f"n={n_c}  "
                    f"depth_mean="
                    f"{d_c.mean():.4f}  "
                    f"±{d_c.std():.4f}")

            # Are clusters separable by depth?
            if k == 2:
                m0 = labels == 0
                m1 = labels == 1
                _, p_mw = stats.mannwhitneyu(
                    depth_arr[m0],
                    depth_arr[m1],
                    alternative="two-sided")
                log(f"    MWU depth C1 vs C2:"
                    f" p={fmt_p(p_mw)}")
                if p_mw < 0.001:
                    log("    Clusters ARE depth-"
                        "stratified.")
                else:
                    log("    Clusters NOT depth-"
                        "stratified — "
                        "ORTHOGONAL BIOLOGY.")

            # Top marker genes per cluster
            log(f"    Top marker genes "
                f"(mean difference):")
            gene_vals = mat  # n_samples × genes
            for ci in range(min(k, 3)):
                mask_c   = labels == ci
                mask_oth = ~mask_c
                diff = (gene_vals[mask_c].mean(
                    axis=0) -
                        gene_vals[mask_oth]
                        .mean(axis=0))
                top_idx_up   = np.argsort(
                    diff)[::-1][:5]
                top_idx_down = np.argsort(
                    diff)[:5]
                up_g   = [top60[j]
                          for j in top_idx_up]
                down_g = [top60[j]
                          for j in top_idx_down]
                log(f"    C{ci+1} UP:   {up_g}")
                log(f"    C{ci+1} DOWN: {down_g}")

        except Exception as ex:
            log(f"    k={k} failed: {ex}")

    return labels if 'labels' in dir() else None

# ═══════════════════════════════════════════════════════
# MODULE G — NORMAL FIELD EFFECT
# ═══════════════════════════════════════════════════════

def module_g_field_effect(expr_full,
                          t_cols, n_cols,
                          depth):
    log("")
    log("=" * 65)
    log("MODULE G — NORMAL FIELD EFFECT")
    log("Does normal tissue variation predict "
        "tumour depth?")
    log("=" * 65)

    if len(n_cols) < 5:
        log("  Insufficient normal samples")
        return

    d = depth.reindex(t_cols).dropna()

    # Identify patient-matched pairs
    # TCGA barcode: TCGA-BP-XXXX-01A (tumour)
    #               TCGA-BP-XXXX-11A (normal)
    def patient_id(s):
        parts = s.split("-")
        if len(parts) >= 3:
            return "-".join(parts[:3])
        return s

    t_patients = {
        patient_id(s): s for s in t_cols
        if s in d.index}
    n_patients = {
        patient_id(s): s for s in n_cols}
    matched = {
        pid: (t_patients[pid],
              n_patients[pid])
        for pid in t_patients
        if pid in n_patients}

    log(f"  Matched normal-tumour pairs: "
        f"{len(matched)}")

    if len(matched) < 5:
        log("  Too few matched pairs — "
            "skip field effect test")
        return

    # Depth in tumour for matched pairs
    t_depth = np.array([
        d[ts] for pid, (ts, ns)
        in matched.items()])

    # For each top depth gene:
    # Does normal expression predict
    # paired tumour depth?
    # i.e. r(normal_expr_gene, tumour_depth)

    # Use top 20 SW genes (depth-negative)
    # from genome scan — these should be
    # predictive of field effect
    top_sw = [
        g for g in expr_full.index
        if g in d.index][:5]  # placeholder

    # Better: use known strong SW genes
    field_genes = [
        g for g in [
            "FBP1","SLC22A6","AQP1",
            "G6PC","SLC34A1","UMOD",
            "AGXT","PCK1","GATM",
            "PAX8","CA9","VEGFA","VIM",
            "EZH2","HDAC1","ACTA2"]
        if g in expr_full.index]

    log("")
    log("  r(normal_expr, paired_tumour_depth):")
    log(f"  {'Gene':<14} {'r':>8}"
        f"  {'p':>10}  interpretation")
    log(f"  {'-'*14} {'-'*8}"
        f"  {'-'*10}  {'-'*20}")

    field_rows = []
    for gene in field_genes:
        n_expr = np.array([
            expr_full.loc[gene, ns]
            for pid, (ts, ns)
            in matched.items()
            if gene in expr_full.index])
        if len(n_expr) < 5:
            continue
        m = (np.isfinite(n_expr) &
             np.isfinite(t_depth))
        if m.sum() < 5:
            continue
        r, p = safe_r(
            n_expr[m], t_depth[m])
        if np.isnan(r):
            continue
        interp = (
            "Field effect: YES"
            if abs(r) >= 0.30
            else "Field effect: weak"
            if abs(r) >= 0.15
            else "No field effect")
        log(f"  {gene:<14} {r:>+8.4f}"
            f"  {fmt_p(p):>10}  {interp}")
        field_rows.append({
            "gene": gene, "r": r, "p": p})

    if field_rows:
        df_f = pd.DataFrame(
            field_rows).sort_values(
            "r", key=abs, ascending=False)
        df_f.to_csv(os.path.join(
            S4_DIR, "field_effect.csv"),
            index=False)

        # Key finding
        sig = df_f[df_f.r.abs() >= 0.30]
        log("")
        if len(sig) > 0:
            log("  FIELD EFFECT CONFIRMED:")
            log(f"  {len(sig)} genes show "
                f"r >= 0.30 between normal "
                f"expression and paired "
                f"tumour depth.")
            log("  The landscape begins in "
                "the normal tissue.")
            log("  Pre-malignant PT state "
                "predicts tumour depth.")
        else:
            log("  NO FIELD EFFECT DETECTED.")
            log("  Normal tissue does not "
                "predict tumour depth.")
            log("  The attractor transition "
                "is post-malignant only.")

# ═══════════════════════════════════════════════════════
# MODULE H — SPLICING FACTOR SCAN
# ═══════════════════════════════════════════════════════

def module_h_splicing(expr_full, t_cols,
                      depth):
    log("")
    log("=" * 65)
    log("MODULE H — SPLICING FACTOR SCAN")
    log("Are RNA splicing regulators lost "
        "in deep ccRCC?")
    log("=" * 65)

    d = depth.reindex(t_cols).dropna()

    rows = []
    for gene in SPLICING_PANEL:
        if gene not in expr_full.index:
            continue
        v = pd.Series(
            expr_full.loc[gene, t_cols]\
                     .values,
            index=t_cols,
        ).reindex(d.index)
        r, p = safe_r(v.values, d.values)
        if np.isnan(r):
            continue
        rows.append({
            "gene": gene,
            "r":    r,
            "p":    p,
        })

    df = pd.DataFrame(rows).sort_values(
        "r", ascending=True)
    df.to_csv(os.path.join(
        S4_DIR, "splicing_scan.csv"),
        index=False)

    log(f"\n  {'Gene':<12} {'r(depth)':>10}"
        f"  {'p':>10}  direction")
    log(f"  {'-'*12} {'-'*10}  "
        f"{'-'*10}  {'-'*15}")
    for _, row in df.iterrows():
        direction = (
            "↑ deeper"
            if row.r > 0
            else "↓ shallower")
        log(f"  {row.gene:<12}"
            f" {row.r:>+10.4f}  "
            f"{fmt_p(row.p):>10}  "
            f"{direction}")

    # Key findings
    lost   = df[df.r < -0.20]
    gained = df[df.r > +0.20]
    log("")
    log(f"  Splicing factors LOST in deep "
        f"ccRCC (r<-0.20): {len(lost)}")
    if len(lost) > 0:
        log(f"  {list(lost.gene)}")
    log(f"  Splicing factors GAINED in deep "
        f"ccRCC (r>+0.20): {len(gained)}")
    if len(gained) > 0:
        log(f"  {list(gained.gene)}")

    # ESRP1/ESRP2 (known from S3)
    for gene in ["ESRP1","ESRP2"]:
        row = df[df.gene == gene]
        if len(row) > 0:
            r = float(row.iloc[0].r)
            log(f"\n  {gene} r = {r:>+7.4f} "
                f"(confirmed from S3: "
                f"ESRP1=-0.158, ESRP2=-0.130)")

    # SF3B1 — ICC finding
    row = df[df.gene == "SF3B1"]
    if len(row) > 0:
        r = float(row.iloc[0].r)
        log(f"\n  SF3B1 r = {r:>+7.4f}")
        if r > 0.15:
            log("  SF3B1 RISES with depth — "
                "same as ICC finding.")
            log("  Aberrant splicing is a "
                "cross-cancer mechanism.")
        elif r < -0.15:
            log("  SF3B1 FALLS with depth — "
                "different from ICC.")
        else:
            log("  SF3B1 flat — splicing "
                "mechanism differs from ICC.")

    return df

# ═══════════════════════════════════════════════════════
# FIGURE — DISCOVERY LANDSCAPE
# ═══════════════════════════════════════════════════════

def generate_figure(genome_df, immune_df,
                    splicing_df,
                    corr_mat, net_genes,
                    hub_scores,
                    nmf_results):
    log("")
    log("Generating Script 4 figure...")

    fig = plt.figure(figsize=(22, 16))
    gs  = gridspec.GridSpec(
        3, 4, figure=fig,
        hspace=0.55, wspace=0.45)

    C = ["#e74c3c","#2ecc71","#2980b9",
         "#8e44ad","#e67e22","#16a085",
         "#c0392b","#7f8c8d"]

    # Panel A — Full genome scan volcano
    ax_a = fig.add_subplot(gs[0, :2])
    if genome_df is not None \
            and not genome_df.empty:
        r_vals = genome_df.r.values
        p_vals = np.clip(
            -np.log10(genome_df.p.values
                      + 1e-300),
            0, 300)
        colors_v = []
        for r, nv in zip(
                r_vals,
                genome_df.novel.values):
            if abs(r) < 0.30:
                colors_v.append("#cccccc")
            elif nv and r > 0:
                colors_v.append("#e74c3c")
            elif nv and r < 0:
                colors_v.append("#2980b9")
            elif not nv and r > 0:
                colors_v.append(
                    "#f1948a")
            else:
                colors_v.append(
                    "#85c1e9")
        ax_a.scatter(
            r_vals, p_vals,
            c=colors_v, s=2, alpha=0.5)
        ax_a.axvline(0.5, color="grey",
                     lw=0.8, ls="--")
        ax_a.axvline(-0.5, color="grey",
                     lw=0.8, ls="--")
        ax_a.axvline(0, color="black",
                     lw=0.5)
        ax_a.set_xlabel("r(gene, depth)",
                        fontsize=8)
        ax_a.set_ylabel("-log10(p)",
                        fontsize=8)
        ax_a.set_title(
            "A — Full genome depth scan\n"
            "red=novel pos, blue=novel neg",
            fontsize=9)

        # Label top novel hits
        novel_top = genome_df[
            genome_df.novel
        ].head(10)
        for _, row in novel_top.iterrows():
            pv = float(np.clip(
                -np.log10(row.p + 1e-300),
                0, 300))
            ax_a.annotate(
                row.gene,
                (row.r, pv),
                fontsize=5,
                ha="center")

    # Panel B — Top 30 pos + neg bar
    ax_b = fig.add_subplot(gs[0, 2])
    if genome_df is not None \
            and not genome_df.empty:
        top15p = genome_df[
            genome_df.r > 0].head(15)
        top15n = genome_df[
            genome_df.r < 0].head(15)
        combined = pd.concat(
            [top15p, top15n])
        combined = combined.sort_values("r")
        cols_b = []
        for _, row in combined.iterrows():
            if row.novel:
                cols_b.append(
                    C[0] if row.r > 0
                    else C[2])
            else:
                cols_b.append(
                    "#f1948a" if row.r > 0
                    else "#85c1e9")
        ax_b.barh(combined.gene.values,
                  combined.r.values,
                  color=cols_b,
                  edgecolor="black",
                  linewidth=0.2)
        ax_b.axvline(0, color="black",
                     lw=0.8)
        ax_b.set_title(
            "B — Top 30 depth genes\n"
            "(dark=novel)",
            fontsize=9)
        ax_b.set_xlabel("r", fontsize=8)
        ax_b.tick_params(axis="y",
                         labelsize=5)

    # Panel C — Immune architecture
    ax_c = fig.add_subplot(gs[0, 3])
    if immune_df is not None \
            and not immune_df.empty:
        top_imm = immune_df[
            immune_df.r.abs() > 0.15
        ].sort_values("r")
        cols_c = [
            C[0] if r > 0 else C[1]
            for r in top_imm.r.values]
        ax_c.barh(
            top_imm.gene.values,
            top_imm.r.values,
            color=cols_c,
            edgecolor="black",
            linewidth=0.2)
        ax_c.axvline(0, color="black",
                     lw=0.8)
        ax_c.set_title(
            "C — Immune r(depth)\n"
            "|r|>0.15 only",
            fontsize=9)
        ax_c.set_xlabel("r", fontsize=8)
        ax_c.tick_params(axis="y",
                         labelsize=6)

    # Panel D — Network heatmap
    ax_d = fig.add_subplot(gs[1, :2])
    if (corr_mat is not None and
            net_genes is not None):
        ng = len(net_genes)
        im = ax_d.imshow(
            corr_mat[:ng, :ng],
            cmap="RdBu_r",
            vmin=-1, vmax=1,
            aspect="auto")
        ax_d.set_xticks(
            range(min(ng, 40)))
        ax_d.set_yticks(
            range(min(ng, 40)))
        ax_d.set_xticklabels(
            net_genes[:40], rotation=90,
            fontsize=4)
        ax_d.set_yticklabels(
            net_genes[:40], fontsize=4)
        plt.colorbar(im, ax=ax_d,
                     fraction=0.02)
        ax_d.set_title(
            "D — Gene correlation network "
            "(top 40 depth genes)",
            fontsize=9)

    # Panel E — Hub scores
    ax_e = fig.add_subplot(gs[1, 2])
    if (hub_scores is not None and
            net_genes is not None):
        hs_order = np.argsort(
            hub_scores)[::-1][:20]
        hs_genes = [net_genes[i]
                    for i in hs_order]
        hs_vals  = [hub_scores[i]
                    for i in hs_order]
        cols_e = [
            C[0] if novel(g) else C[2]
            for g in hs_genes]
        ax_e.barh(
            hs_genes, hs_vals,
            color=cols_e,
            edgecolor="black",
            linewidth=0.3)
        ax_e.set_title(
            "E — Network hubs\n"
            "(red=novel, blue=known)",
            fontsize=9)
        ax_e.set_xlabel(
            "Hub score", fontsize=8)
        ax_e.tick_params(axis="y",
                         labelsize=7)

    # Panel F — Splicing factor scan
    ax_f = fig.add_subplot(gs[1, 3])
    if splicing_df is not None \
            and not splicing_df.empty:
        sf_plot = splicing_df[
            splicing_df.r.abs() > 0.10
        ].sort_values("r")
        cols_f = [
            C[0] if r > 0 else C[1]
            for r in sf_plot.r.values]
        ax_f.barh(
            sf_plot.gene.values,
            sf_plot.r.values,
            color=cols_f,
            edgecolor="black",
            linewidth=0.2)
        ax_f.axvline(0, color="black",
                     lw=0.8)
        ax_f.set_title(
            "F — Splicing factors r(depth)",
            fontsize=9)
        ax_f.set_xlabel("r", fontsize=8)
        ax_f.tick_params(axis="y",
                         labelsize=6)

    # Panels G-I — NMF / summary text
    if (nmf_results and
            2 in nmf_results):
        res = nmf_results[2]
        W   = res["W"]
        ax_g = fig.add_subplot(gs[2, 0])
        d_dummy = np.linspace(0, 1,
                              W.shape[0])
        ax_g.scatter(W[:, 0], W[:, 1],
                     c=d_dummy,
                     cmap="RdYlGn_r",
                     s=8, alpha=0.5)
        ax_g.set_xlabel("NMF C1",
                        fontsize=8)
        ax_g.set_ylabel("NMF C2",
                        fontsize=8)
        ax_g.set_title(
            "G — NMF k=2 components",
            fontsize=9)

    # Summary text
    for i, (title, lines) in enumerate([
        ("H — S4 Findings",
         ["S4-P1: novel hits found?",
          "Full genome → new biology",
          "Immune: exclusion geometry",
          "Splicing: ESRP1/2 loss",
          "Network: hub genes = targets",
          "Field effect: pre-cancer"]),
        ("I — Novel predictions",
         ["Cross-cancer splicing mech?",
          "HIF1A/HIF2A sub-states",
          "Purity-independent depth",
          "Normal field effect: YES/NO",
          "Hub gene = drug target",
          "→ Document 94d"]),
    ]):
        ax_hi = fig.add_subplot(
            gs[2, 1 + i])
        ax_hi.axis("off")
        ax_hi.set_title(title, fontsize=9)
        for j, line in enumerate(lines):
            ax_hi.text(
                0.03,
                0.88 - j * 0.14,
                line,
                fontsize=7,
                transform=ax_hi.transAxes)

    fig.suptitle(
        "ccRCC False Attractor — Script 4\n"
        "LANDSCAPE DISCOVERY — "
        "Full genome / Immune / Network / "
        "Splicing / Clustering / "
        "Field effect",
        fontsize=11,
        fontweight="bold")

    out = os.path.join(S4_DIR,
                       "figure_s4.png")
    fig.savefig(out, dpi=150,
                bbox_inches="tight")
    plt.close(fig)
    log(f"  Figure saved: {out}")

# ═══════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════

def main():
    log("OrganismCore — ccRCC Script 4")
    log("LANDSCAPE DISCOVERY — geometry first")
    log("Document 94d-pre | 2026-03-02")
    log("")
    log("SINGLE LOCKED PREDICTION:")
    log("  S4-P1: full genome scan finds")
    log("         >= 5 novel |r|>0.50 genes")
    log("")
    log("All other modules: OPEN DISCOVERY.")
    log("No predicted directions.")
    log("No confirmation targets.")
    log("The data speaks.")
    log("")

    # Load depth from Script 1
    depth_t = load_depth("tcga")

    # Load FULL genome — no filter
    expr_full, t_cols, n_cols = \
        load_tcga_full()

    # MODULE A — Full genome scan
    genome_df, novel_hits = \
        module_a_genome_scan(
            expr_full, t_cols, depth_t)

    # MODULE B — Co-expression modules
    nmf_results = module_b_nmf_modules(
        expr_full, t_cols,
        depth_t, genome_df)

    # MODULE C — Full immune architecture
    # Add immune genes to expr if missing
    immune_df = module_c_immune_scan(
        expr_full, t_cols, depth_t)

    # MODULE D — Purity test
    immune_score, stromal_score, \
        tumour_score = module_d_purity(
        expr_full, t_cols, depth_t)

    # MODULE E — Correlation network
    corr_mat, net_genes, hub_scores = \
        module_e_network(
            expr_full, t_cols,
            depth_t, genome_df)

    # MODULE F — Unsupervised clustering
    cluster_labels = module_f_clustering(
        expr_full, t_cols,
        depth_t, genome_df)

    # MODULE G — Normal field effect
    module_g_field_effect(
        expr_full, t_cols, n_cols,
        depth_t)

    # MODULE H — Splicing factor scan
    splicing_df = module_h_splicing(
        expr_full, t_cols, depth_t)

    # GEO validation of top novel hits
    if len(novel_hits) > 0:
        log("")
        log("=" * 65)
        log("VALIDATION — novel hits in GEO")
        log("=" * 65)
        depth_g = load_depth("geo")
        novel_genes = list(
            novel_hits.gene.head(30))
        geo_expr, geo_t = load_geo_panel(
            novel_genes)
        if geo_expr is not None:
            d_g = depth_g.reindex(
                geo_t).dropna()
            log(f"\n  {'Gene':<14}"
                f" {'r_TCGA':>8}"
                f" {'r_GEO':>8}"
                f"  cross_dataset")
            log(f"  {'-'*14}"
                f" {'-'*8} {'-'*8}"
                f"  {'-'*15}")
            for gene in novel_genes:
                r_t = float(
                    novel_hits[
                        novel_hits.gene
                        == gene
                    ].r.iloc[0]
                    if len(novel_hits[
                        novel_hits.gene
                        == gene]) > 0
                    else np.nan)
                if gene not in \
                        geo_expr.index:
                    log(f"  {gene:<14}"
                        f" {r_t:>+8.4f}"
                        f" {'NA':>8}"
                        f"  (not in GEO)")
                    continue
                v_g = pd.Series(
                    geo_expr.loc[
                        gene, geo_t].values,
                    index=geo_t,
                ).reindex(d_g.index)
                r_g, p_g = safe_r(
                    v_g.values, d_g.values)
                consistent = (
                    "CONSISTENT ✓"
                    if (not np.isnan(r_g)
                        and (r_t * r_g > 0)
                        and abs(r_g) > 0.20)
                    else "INCONSISTENT ✗"
                    if (not np.isnan(r_g)
                        and r_t * r_g < 0)
                    else "WEAK/NA")
                log(f"  {gene:<14}"
                    f" {r_t:>+8.4f}"
                    f" {r_g:>+8.4f}"
                    f"  {consistent}")

    # Generate figure
    generate_figure(
        genome_df, immune_df,
        splicing_df,
        corr_mat, net_genes, hub_scores,
        nmf_results)

    # Summary
    log("")
    log("=" * 65)
    log("SCRIPT 4 COMPLETE")
    log("=" * 65)
    for fname in sorted(
            os.listdir(S4_DIR)):
        fp = os.path.join(S4_DIR, fname)
        log(f"  {fname:<50}"
            f" {os.path.getsize(fp):>9} bytes")

    log("")
    log("  NEXT: paste full output.")
    log("  Write document 94d.")
    log("  The landscape is what the data")
    log("  shows, not what was predicted.")

    write_log()


if __name__ == "__main__":
    main()
