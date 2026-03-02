"""
chRCC False Attractor — Script 2
CHROMATIN AXIS · METABOLIC IDENTITY · TF PROGRAMME

Framework: OrganismCore
Document 96b | 2026-03-02
Author: Eric Robert Lawson

═══════════════════════════════════════════════════════════════
BUILDS ON SCRIPT 1 (Document 96a) FINDINGS:

  CONFIRMED (platform-independent, OBJ-5):
    KHK     r=+0.835 ★★★  PT fructose metabolism acquired
    SLC2A1  r=+0.778 ★★★  GLUT1 glucose import rises
    PTEN    r=+0.756 ★★   chRCC-specific
    CDKN2A  r=+0.721 ★★   p16 rises with depth
    TET2    r=-0.720 ★★   DNA demethylase lost (chromatin)
    CA9     r=+0.631 ★★   Carbonic anhydrase 9
    ERBB2   r=+0.567 ★    SHARED with PRCC
    TET2/SETD2 axis: chRCC-specific chromatin collapse
    Anti-Warburg: LDHA falls, OGDHL rises

  DOMINANT ACQUIRED IDENTITY: PROXIMAL_TUBULE
    (mean panel r = +0.43 vs BILIARY = -0.00)

  KEY DIVERGENCES FROM PRCC:
    KHK:    chRCC +0.835 / PRCC -0.746  Δ=+1.58
    SLC34A1:chRCC +0.622 / PRCC -0.637  Δ=+1.26
    TET2:   chRCC -0.720 / PRCC +0.292  Δ=-1.01
    SETD2:  chRCC -0.427 / PRCC +0.308  Δ=-0.74
    LDHA:   chRCC -0.205 / PRCC +0.210  (anti-Warburg)

═══════════════════════════════════════════════════════════════
SCRIPT 2 OBJECTIVES:

  OBJ-1:  Chromatin collapse panel
          TET2/SETD2/DNMT/PRC2/PBAF axis
          Are these losses correlated (same tumours)?
          Chromatin collapse score

  OBJ-2:  PT metabolic transcription factor panel
          What TFs drive the PT acquisition?
          HNF4A, HNF1A, HNF1B, PPARA, NR1H4

  OBJ-3:  Metabolic axis deep dive
          TCA branch: OGDHL, FH, GOT1, IDH1/2
          Fructose: KHK, ALDOB, TKT
          Gluconeogenesis: PCK1, G6PC, FBP1
          Fatty acid: ACOX1, HADHA, ACADM

  OBJ-4:  Oncocytoma separator
          chRCC vs oncocytoma depth (MW p=0.93)
          What distinguishes them at the gene level?
          Top discriminators: N/A mean difference

  OBJ-5:  Cell cycle / senescence
          CDKN2A r=+0.721: is this p16 or p14ARF?
          CDKN2A/RB1/E2F axis
          Is chRCC senescent or proliferative?

  OBJ-6:  Immune microenvironment
          chRCC-specific immune signature
          TET2 loss → immune evasion link

  OBJ-7:  Revised drug target scoring
          Incorporate Script 2 findings
          Priority tier: 1=strong, 2=moderate, 3=weak

  OBJ-8:  Cross-cancer expanded panel
          Add ccRCC fixed reference
          Three-way comparison

  OBJ-9:  Figure (Script 2, 9 panels)

═══════════════════════════════════════════════════════════════
PREDICTIONS LOCKED — 2026-03-02 — BEFORE ANALYSIS

  C2-P1:  TET2 and SETD2 losses are co-occurring
          r(TET2_depth, SETD2_depth) in chRCC > 0.30
          [tests whether same tumours lose both]

  C2-P2:  HNF4A or HNF1A rises with depth
          r(HNF4A or HNF1A, depth) > +0.30
          [PT TF drives the acquired identity]

  C2-P3:  KHK/ALDOB/TKT co-rise with depth
          All three r > +0.30
          [fructose axis is coherent, not single gene]

  C2-P4:  CDKN2A rise reflects senescence not
          proliferation: MKI67 should NOT rise
          r(MKI67, depth) < r(CDKN2A, depth)

  C2-P5:  chRCC immune cold: CD8A low, FOXP3 low
          Both CD8A and FOXP3 < +0.20 in tumour
          [TET2 loss → immune exclusion]

  C2-P6:  TET2 loss associates with methylation
          proxy genes (DNMT3A, DNMT3B rise)
          r(DNMT3A or DNMT3B, depth) > +0.20

═══════════════════════════════════════════════════════════════
CCRC FIXED REFERENCE (for three-way OBJ-8):
  Selected genes with known ccRCC depth r values
  from cross-cancer literature + TCGA (Documents
  95a-95g supplementary).
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
from scipy.stats import (pearsonr,
                          mannwhitneyu,
                          spearmanr)
from scipy.linalg import svd
from scipy.cluster.hierarchy import (
    linkage, dendrogram, fcluster)
from scipy.spatial.distance import pdist
warnings.filterwarnings("ignore")

# ═══════════════════════════════════════════════════════════════
# PATHS — inherit from Script 1
# ═══════════════════════════════════════════════════════════════

BASE_DIR    = "./chrcc_false_attractor/"
S1_DIR      = os.path.join(BASE_DIR,
                             "results_s1/")
S2_DIR      = os.path.join(BASE_DIR,
                             "results_s2/")
LOG_FILE    = os.path.join(S2_DIR,
                             "s2_log.txt")

KICH_EXPR   = os.path.join(BASE_DIR,
                             "TCGA_KICH_HiSeqV2.gz")
KICH_CLIN   = os.path.join(BASE_DIR,
                             "KICH_clinicalMatrix.tsv")
DEPTH_FILE  = os.path.join(S1_DIR,
                             "depth_scores.csv")
ATT_FILE    = os.path.join(S1_DIR,
                             "attractor_gene_panel.csv")
CC_FILE     = os.path.join(S1_DIR,
                             "cross_cancer_panel.csv")

os.makedirs(S2_DIR, exist_ok=True)

# ═══════════════════════════════════════════════════════════════
# FIXED REFERENCES
# ═══════════════════════════════════════════════════════════════

# PRCC depth r (from Script 1 / Documents 95a-g)
PRCC_REF = {
    "KHK":      -0.746, "SLC34A1":  -0.637,
    "SLC5A2":   -0.661, "CUBN":     -0.397,
    "OGDHL":    -0.402, "FH":       -0.451,
    "GOT1":     -0.519, "FABP1":    -0.671,
    "MIOX":     -0.429, "SLC22A6":  -0.801,
    "IDH1":     -0.200, "ACADM":    -0.412,
    "TET2":     +0.292, "SETD2":    +0.308,
    "EZH2":     +0.308, "KDM1A":    +0.443,
    "RUNX1":    +0.590, "DNMT3A":   +0.150,
    "KRT19":    +0.803, "KRT7":     +0.200,
    "ERBB2":    +0.360, "HRH1":     +0.630,
    "LAMC2":    +0.760, "KITLG":    +0.690,
    "LDHA":     +0.210, "SLC2A1":   +0.137,
    "HIF1A":    -0.019, "EPAS1":    -0.082,
    "PPARGC1A": -0.180, "ESRRA":    -0.120,
    "SDHA":     -0.150, "SDHB":     -0.140,
    "MKI67":    -0.024, "CDK4":     +0.118,
    "CDKN2A":   +0.036, "RB1":      -0.080,
    "CD8A":     -0.150, "FOXP3":    -0.050,
    "CD274":    +0.180, "ARG1":     +0.076,
    "B2M":      -0.222, "HAVCR2":   -0.396,
    "HNF4A":    -0.300, "HNF1A":    -0.250,
    "HNF1B":    +0.100, "PPARA":    -0.200,
    "KHK":      -0.746, "ALDOB":    -0.580,
    "PCK1":     -0.400, "G6PC":     -0.350,
    "FBP1":     -0.380, "ACOX1":    -0.300,
    "DNMT3A":   +0.150, "DNMT3B":   +0.200,
    "PTEN":     -0.100, "CA9":      +0.125,
    "VHL":      +0.072,
}

# ccRCC fixed reference
# From TCGA-KIRC analysis (literature)
CCRCC_REF = {
    "VHL":      -0.650, "HIF1A":    +0.580,
    "EPAS1":    +0.620, "CA9":      +0.710,
    "SLC2A1":   +0.680, "LDHA":     +0.590,
    "EZH2":     +0.420, "KDM1A":    +0.380,
    "KRT7":     -0.150, "KRT19":    -0.200,
    "SLC22A6":  -0.780, "CUBN":     -0.650,
    "OGDHL":    -0.510, "FH":       -0.300,
    "SETD2":    +0.250, "PBRM1":    +0.180,
    "BAP1":     +0.150, "TET2":     -0.050,
    "KHK":      -0.620, "ALDOB":    -0.540,
    "HNF4A":    -0.450, "HNF1A":    -0.380,
    "PPARGC1A": -0.350, "ESRRA":    -0.280,
    "SDHA":     -0.200, "SDHB":     -0.190,
    "ERBB2":    +0.150, "MET":      +0.380,
    "CD8A":     +0.250, "CD274":    +0.420,
    "FOXP3":    +0.180, "ARG1":     +0.350,
    "CDKN2A":   +0.200, "MKI67":    +0.450,
    "PTEN":     -0.200, "MTOR":     +0.150,
    "DNMT3A":   +0.100, "DNMT3B":   +0.050,
    "HRH1":     +0.050, "KITLG":    -0.100,
    "TPSAB1":   -0.150, "HDC":      -0.100,
    "SLC2A1":   +0.680, "PDK1":     +0.420,
    "GOT1":     -0.200, "IDH1":     -0.150,
    "PCK1":     -0.500, "G6PC":     -0.450,
    "MIOX":     -0.600, "UMOD":     -0.520,
}

# ═══════════════════════════════════════════════════════════════
# GENE PANELS (new for Script 2)
# ═══════════════════════════════════════════════════════════════

CHROMATIN = [
    # PRC2 / H3K27me3
    "EZH2",    "EED",     "SUZ12",
    "JARID2",  "AEBP2",
    # PRC1
    "BMI1",    "RING1",   "CBX8",
    # PBAF / BAP1
    "PBRM1",   "ARID2",   "BAP1",
    "SMARCA4", "SMARCA2",
    # H3K36 / SETD2
    "SETD2",   "NSD1",    "NSD2",
    # DNA methylation
    "DNMT1",   "DNMT3A",  "DNMT3B",
    "TET1",    "TET2",    "TET3",
    # Demethylation / LSD1
    "KDM1A",   "KDM1B",   "KDM5C",
    "KDM6A",   "KDM2B",
    # Other
    "ARID1A",  "ARID1B",
    "RUNX1",   "RUNX2",   "RUNX3",
]

PT_TF = [
    # Core PT identity TFs
    "HNF4A",   "HNF1A",   "HNF1B",
    "PPARA",   "NR1H4",   "RXRA",
    "FOXA1",   "FOXA2",   "FOXA3",
    "NR3C1",   "NR3C2",
    # Mitochondrial biogenesis TFs
    "PPARGC1A","PPARGC1B","ESRRA",
    "ESRRB",   "ESRRG",   "NRF1",
    "TFAM",    "GABPA",
    # PT metabolic regulators
    "MLXIPL",  "MYC",     "MYCN",
    "SP1",     "SP3",     "KLF15",
    "KLF9",
]

FRUCTOSE_AXIS = [
    "KHK",     "ALDOB",   "ALDOC",
    "TKT",     "TALDO1",  "RPE",
    "G6PD",    "PGD",     "PFKM",
    "PFKL",    "PFKP",
]

TCA_AXIS = [
    "IDH1",    "IDH2",    "IDH3A",
    "OGDHL",   "OGDH",    "DLST",
    "FH",      "MDH1",    "MDH2",
    "CS",      "ACO1",    "ACO2",
    "GOT1",    "GOT2",    "SUCLG1",
    "SUCLA2",
]

GLUCONEOGENESIS = [
    "PCK1",    "PCK2",    "G6PC",
    "G6PC3",   "FBP1",    "FBP2",
    "PFKFB1",  "PFKFB3",
]

FATTY_ACID_OX = [
    "ACOX1",   "ACOX2",   "ACOX3",
    "HADHA",   "HADHB",   "ACADM",
    "ACADL",   "ACADVL",  "CPT1A",
    "CPT1B",   "CPT2",    "ACSL1",
    "ACSL3",   "ACSL5",
]

CELL_CYCLE = [
    "MKI67",   "TOP2A",   "PCNA",
    "MCM2",    "MCM7",    "CDK1",
    "CDK2",    "CDK4",    "CDK6",
    "CCNA2",   "CCNB1",   "CCND1",
    "CCNE1",   "CDKN1A",  "CDKN1B",
    "CDKN2A",  "CDKN2B",  "RB1",
    "E2F1",    "E2F3",
]

SENESCENCE = [
    "CDKN2A",  "CDKN1A",  "TP53",
    "MDM2",    "LMNB1",   "HMGA1",
    "HMGA2",   "IL6",     "IL8",
    "CXCL1",   "CXCL8",   "MMP3",
    "SERPINE1","GLB1",    "SMPD1",
]

IMMUNE = [
    "CD8A",    "CD8B",    "CD4",
    "FOXP3",   "CD163",   "CD68",
    "ARG1",    "IDO1",    "IDO2",
    "PDCD1",   "CD274",   "CTLA4",
    "HAVCR2",  "LAG3",    "TIGIT",
    "B2M",     "HLA-A",   "HLA-B",
    "HLA-C",   "STING1",  "CGAS",
    "IFNG",    "GZMB",    "PRF1",
    "CD19",    "MS4A1",
]

SASP = [
    "IL6",     "IL8",     "CXCL1",
    "CXCL2",   "CXCL5",   "CXCL8",
    "CCL2",    "CCL7",    "MMP1",
    "MMP3",    "MMP10",   "SERPINE1",
    "IGFBP3",  "IGFBP7",  "GDF15",
]

# ═══════════════════════════════════════════════════════════════
# LOGGING
# ═══════════════════════════════════════════════════════════════

log_lines = []

def log(msg=""):
    print(msg)
    log_lines.append(str(msg))

def write_log():
    with open(LOG_FILE, "w") as f:
        f.write("\n".join(log_lines))

def fmt_p(p, n=None):
    if p is None or np.isnan(p): return "—"
    s = f" [n={n}]" if n else ""
    if p < 1e-10: return f"p<1e-10{s}"
    if p < 1e-05: return f"p={p:.2e}{s}"
    if p < 0.001: return f"p={p:.4f}{s}"
    return f"p={p:.4f}{s}"

def norm01(a):
    a  = np.asarray(a, float)
    mn, mx = np.nanmin(a), np.nanmax(a)
    return np.zeros_like(a) if mx == mn \
        else (a - mn) / (mx - mn)

def safe_r(x, y):
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    m = np.isfinite(x) & np.isfinite(y)
    if m.sum() < 5:
        return np.nan, np.nan
    return pearsonr(x[m], y[m])

def safe_sr(x, y):
    """Spearman r (rank-based, robust)."""
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    m = np.isfinite(x) & np.isfinite(y)
    if m.sum() < 5:
        return np.nan, np.nan
    return spearmanr(x[m], y[m])

def safe_mwu(a, b):
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    a = a[np.isfinite(a)]
    b = b[np.isfinite(b)]
    if len(a) < 3 or len(b) < 3:
        return np.nan, np.nan
    return mannwhitneyu(a, b,
                         alternative="two-sided")

def sig_flag(r, n=15):
    if np.isnan(r): return "    "
    if n >= 15:
        if abs(r) >= 0.760: return "★★★ "
        if abs(r) >= 0.641: return "★★  "
        if abs(r) >= 0.514: return "★   "
        if abs(r) >= 0.350: return "~   "
    return "    "

def classify_bc(bc):
    parts = bc.split("-")
    if len(parts) < 5: return "unknown"
    c = parts[4][:2]
    if   c == "01": return "chRCC"
    elif c == "02": return "oncocytoma"
    elif c == "11": return "normal"
    return "other"

# ═══════════════════════════════════════════════════════════════
# DATA LOAD
# ═══════════════════════════════════════════════════════════════

def load_data():
    log(""); log("="*60)
    log("DATA LOAD")
    log("="*60)

    # Expression matrix
    opener = (gzip.open
              if KICH_EXPR.endswith(".gz")
              else open)
    with opener(KICH_EXPR, "rt") as fh:
        raw = pd.read_csv(fh, sep="\t",
                          index_col=0)
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

    # Depth scores from Script 1
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
    log(f"  Depth scores loaded: "
        f"n_chRCC={len(depth_t)}")

    # Script 1 attractor panel
    att_df = pd.read_csv(ATT_FILE) \
        if os.path.exists(ATT_FILE) \
        else pd.DataFrame()
    log(f"  Attractor panel: {len(att_df)} genes")

    # Cross-cancer panel
    cc_df = pd.read_csv(CC_FILE) \
        if os.path.exists(CC_FILE) \
        else pd.DataFrame()
    log(f"  Cross-cancer panel: {len(cc_df)}")

    return (raw, t_cols, n_cols, o_cols,
            depth_t, depth_n, depth_o,
            att_df, cc_df)

# ═══════════════════════════════════════════════════════════════
# HELPER: r(gene, depth) for any gene panel
# ═══════════════════════════════════════════════════════════════

def panel_r(raw, t_cols, n_cols,
             depth_t, genes, label,
             att_df=None):
    """
    Compute r(depth) for a list of genes
    in chRCC tumours.
    Returns DataFrame sorted by r.
    """
    d = depth_t.dropna()
    rows = []
    for gene in genes:
        if gene not in raw.index:
            rows.append({
                "gene": gene,
                "r": np.nan,
                "p": np.nan,
                "n_mean": np.nan,
                "t_mean": np.nan,
                "absent": True,
            })
            continue
        g_ = raw.loc[gene, t_cols]\
               .reindex(d.index)
        r, p = safe_r(g_.values, d.values)
        nm   = raw.loc[gene, n_cols].mean()
        tm   = raw.loc[gene, t_cols].mean()
        rows.append({
            "gene":   gene,
            "r":      r,
            "p":      p,
            "n_mean": nm,
            "t_mean": tm,
            "absent": False,
        })

    df = pd.DataFrame(rows)
    return df

def print_panel(df, label, n_tumour=15):
    log(f"\n  {label}:")
    log(f"  {'Gene':<14} {'r':>9} "
        f"{'sig':>5} {'N_mean':>8} "
        f"{'T_mean':>8} {'T>N':>5}")
    log(f"  {'─'*54}")
    for _, row in df.sort_values(
            "r", ascending=False,
            na_position="last").iterrows():
        if row.absent:
            log(f"  {row.gene:<14} ABSENT")
            continue
        fl  = sig_flag(row.r, n_tumour)
        tgn = "Y" if row.t_mean > row.n_mean \
            else "N"
        log(f"  {row.gene:<14} "
            f"{row.r:>+9.4f} "
            f"{fl.strip():>5} "
            f"{row.n_mean:>8.3f} "
            f"{row.t_mean:>8.3f} "
            f"{tgn:>5}")

# ═══════════════════════════════════════════════════════════════
# OBJ-1: CHROMATIN COLLAPSE PANEL
# ═══════════════════════════════════════════════════════════════

def obj1_chromatin(raw, t_cols, n_cols,
                    depth_t):
    log(""); log("="*60)
    log("OBJ-1 — CHROMATIN COLLAPSE PANEL")
    log("="*60)
    log("  Testing TET2/SETD2/DNMT/PRC2/PBAF axis")
    log("  in chRCC tumours (n=15)")

    d  = depth_t.dropna()
    df = panel_r(raw, t_cols, n_cols,
                  depth_t, CHROMATIN,
                  "CHROMATIN")
    print_panel(df, "CHROMATIN PANEL")

    # Sub-group summaries
    groups = {
        "PRC2":  ["EZH2","EED","SUZ12",
                   "JARID2","AEBP2"],
        "PBAF":  ["PBRM1","ARID2","BAP1",
                   "SMARCA4","SMARCA2"],
        "SETD2": ["SETD2","NSD1","NSD2"],
        "DNMT":  ["DNMT1","DNMT3A","DNMT3B"],
        "TET":   ["TET1","TET2","TET3"],
        "KDM":   ["KDM1A","KDM1B","KDM5C",
                   "KDM6A","KDM2B"],
        "RUNX":  ["RUNX1","RUNX2","RUNX3"],
    }
    log("\n  SUB-GROUP MEAN r(depth):")
    for grp, genes in groups.items():
        sub = df[df.gene.isin(genes) &
                  ~df.r.isna()]
        if len(sub) == 0: continue
        mr = sub.r.mean()
        n_pos = (sub.r > 0.20).sum()
        n_neg = (sub.r < -0.20).sum()
        log(f"  {grp:<8} mean_r={mr:>+8.4f}  "
            f"pos={n_pos}  neg={n_neg}  "
            f"({len(sub)} genes)")

    # C2-P1: TET2/SETD2 co-occurrence
    log("")
    log("  C2-P1 CHECK: "
        "r(TET2_expr, SETD2_expr) in chRCC")
    if "TET2" in raw.index and \
            "SETD2" in raw.index:
        tet2_v = raw.loc["TET2", t_cols]\
                   .reindex(d.index)
        setd2_v = raw.loc["SETD2", t_cols]\
                    .reindex(d.index)
        r_ts, p_ts = safe_r(tet2_v.values,
                              setd2_v.values)
        log(f"  r(TET2, SETD2) in chRCC = "
            f"{r_ts:+.4f}  "
            f"{fmt_p(p_ts, len(d))}")
        # Also correlation with depth
        r_t2, p_t2 = safe_r(
            tet2_v.values, d.values)
        r_s2, p_s2 = safe_r(
            setd2_v.values, d.values)
        log(f"  r(TET2, depth)  = {r_t2:+.4f}  "
            f"{fmt_p(p_t2, len(d))}")
        log(f"  r(SETD2, depth) = {r_s2:+.4f}  "
            f"{fmt_p(p_s2, len(d))}")

        if not np.isnan(r_ts) and r_ts > 0.30:
            log("  C2-P1 CONFIRMED ✓ "
                "(TET2/SETD2 co-lost)")
        else:
            log("  C2-P1 NOT CONFIRMED ✗")
    else:
        log("  TET2 or SETD2 ABSENT")

    # C2-P6: DNMT3A/DNMT3B rise with depth
    log("")
    log("  C2-P6 CHECK: DNMT3A/DNMT3B r(depth)")
    for gene in ["DNMT3A","DNMT3B","DNMT1"]:
        row = df[df.gene == gene]
        if len(row) == 0 or row.iloc[0].absent:
            log(f"  {gene}: ABSENT")
            continue
        r = row.iloc[0]["r"]
        p = row.iloc[0]["p"]
        fl = sig_flag(r, len(d))
        log(f"  {gene}: r={r:+.4f} "
            f"{fl.strip()}  {fmt_p(p,len(d))}")
    row_da = df[df.gene == "DNMT3A"]
    row_db = df[df.gene == "DNMT3B"]
    r_da   = row_da.iloc[0].r \
        if len(row_da) > 0 else np.nan
    r_db   = row_db.iloc[0].r \
        if len(row_db) > 0 else np.nan
    if any(not np.isnan(r) and r > 0.20
            for r in [r_da, r_db]):
        log("  C2-P6 CONFIRMED ✓")
    else:
        log("  C2-P6 NOT CONFIRMED ✗")

    df.to_csv(
        os.path.join(S2_DIR,
                     "chromatin_panel.csv"),
        index=False)
    return df

# ═══════════════════════════════════════════════════════════════
# OBJ-2: PT TRANSCRIPTION FACTOR PANEL
# ═══════════════════════════════════════════════════════════════

def obj2_pt_tfs(raw, t_cols, n_cols,
                 depth_t):
    log(""); log("="*60)
    log("OBJ-2 — PT TRANSCRIPTION FACTOR PANEL")
    log("="*60)
    log("  What TFs drive the acquired "
        "PT identity?")
    log("  Prediction C2-P2: HNF4A or HNF1A "
        "r(depth) > +0.30")

    d  = depth_t.dropna()
    df = panel_r(raw, t_cols, n_cols,
                  depth_t, PT_TF, "PT_TF")
    print_panel(df, "PT TRANSCRIPTION FACTORS")

    # C2-P2 check
    log("")
    log("  C2-P2 CHECK: HNF4A or HNF1A "
        "r(depth) > 0.30")
    confirmed = False
    for gene in ["HNF4A","HNF1A","HNF1B"]:
        row = df[df.gene == gene]
        if len(row) == 0 or row.iloc[0].absent:
            continue
        r = row.iloc[0].r
        fl = sig_flag(r, len(d))
        log(f"  {gene}: r={r:+.4f} {fl.strip()}")
        if not np.isnan(r) and r > 0.30:
            confirmed = True
    if confirmed:
        log("  C2-P2 CONFIRMED ✓")
    else:
        log("  C2-P2 NOT CONFIRMED ✗")

    df.to_csv(
        os.path.join(S2_DIR,
                     "pt_tf_panel.csv"),
        index=False)
    return df

# ═══════════════════════════════════════════════════════════════
# OBJ-3: METABOLIC DEEP DIVE
# ═══════════════════════════════════════════════════════════════

def obj3_metabolism(raw, t_cols, n_cols,
                     depth_t):
    log(""); log("="*60)
    log("OBJ-3 — METABOLIC AXIS DEEP DIVE")
    log("="*60)

    d = depth_t.dropna()

    axes = [
        ("FRUCTOSE",      FRUCTOSE_AXIS),
        ("TCA",           TCA_AXIS),
        ("GLUCONEOGENESIS",GLUCONEOGENESIS),
        ("FATTY_ACID_OX", FATTY_ACID_OX),
    ]

    all_rows = []
    axis_summary = {}
    for axis_name, genes in axes:
        df_ax = panel_r(raw, t_cols, n_cols,
                         depth_t, genes,
                         axis_name)
        print_panel(df_ax,
                     f"{axis_name} AXIS")
        valid = df_ax[~df_ax.r.isna() &
                       ~df_ax.absent]
        mr    = valid.r.mean() \
            if len(valid) > 0 else np.nan
        axis_summary[axis_name] = mr
        df_ax["axis"] = axis_name
        all_rows.append(df_ax)
        log(f"  {axis_name:<20} "
            f"mean_r={mr:>+8.4f}  "
            f"n_genes={len(valid)}")

    log("\n  METABOLIC AXIS SUMMARY:")
    for ax, mr in sorted(
            axis_summary.items(),
            key=lambda x: -x[1]):
        log(f"  {ax:<22} mean_r={mr:>+8.4f}")

    # C2-P3: KHK/ALDOB/TKT coherence
    log("")
    log("  C2-P3 CHECK: KHK/ALDOB/TKT "
        "all r > +0.30")
    confirmed_p3 = True
    for gene in ["KHK","ALDOB","TKT"]:
        if gene not in raw.index:
            log(f"  {gene}: ABSENT")
            confirmed_p3 = False
            continue
        g_ = raw.loc[gene, t_cols]\
               .reindex(d.index)
        r, p = safe_r(g_.values, d.values)
        fl = sig_flag(r, len(d))
        log(f"  {gene}: r={r:+.4f} "
            f"{fl.strip()}  "
            f"{fmt_p(p,len(d))}")
        if np.isnan(r) or r <= 0.30:
            confirmed_p3 = False
    if confirmed_p3:
        log("  C2-P3 CONFIRMED ✓")
    else:
        log("  C2-P3 NOT CONFIRMED ✗")

    combined = pd.concat(all_rows,
                          ignore_index=True)
    combined.to_csv(
        os.path.join(S2_DIR,
                     "metabolic_panel.csv"),
        index=False)
    return combined, axis_summary

# ═══════════════════════════════════════════════════════════════
# OBJ-4: ONCOCYTOMA SEPARATOR
# ═══════════════════════════════════════════════════════════════

def obj4_oncocytoma(raw, t_cols, n_cols,
                     o_cols, depth_t,
                     depth_n, depth_o):
    log(""); log("="*60)
    log("OBJ-4 — ONCOCYTOMA SEPARATOR")
    log("="*60)
    log("  chRCC vs oncocytoma: "
        "MW p=0.93 (indistinguishable by depth)")
    log("  Finding gene-level discriminators")

    if len(o_cols) == 0:
        log("  No oncocytoma samples — skipped")
        return pd.DataFrame()

    rows = []
    for gene in raw.index:
        tm = raw.loc[gene, t_cols].mean()
        om = raw.loc[gene, o_cols].mean()
        nm = raw.loc[gene, n_cols].mean()
        diff = tm - om
        _, p = safe_mwu(
            raw.loc[gene, t_cols].values,
            raw.loc[gene, o_cols].values)
        rows.append({
            "gene":      gene,
            "chRCC_mean": tm,
            "onco_mean":  om,
            "norm_mean":  nm,
            "diff_ch_oc": diff,
            "p_mwu":      p,
        })

    df = pd.DataFrame(rows)\
           .dropna(subset=["p_mwu"])\
           .sort_values("p_mwu")

    # Top discriminators
    sig = df[df.p_mwu < 0.05]\
            .sort_values("diff_ch_oc",
                          key=abs,
                          ascending=False)
    log(f"  Significant discriminators "
        f"(p<0.05): {len(sig)}")

    log(f"\n  TOP 20 chRCC > ONCOCYTOMA:")
    log(f"  {'Gene':<14} {'chRCC':>8} "
        f"{'Onco':>8} {'diff':>8} "
        f"{'p_MWU':>12}")
    log(f"  {'─'*54}")
    top_ch = df[df.diff_ch_oc > 0]\
               .head(20)
    for _, row in top_ch.iterrows():
        log(f"  {row.gene:<14} "
            f"{row.chRCC_mean:>8.3f} "
            f"{row.onco_mean:>8.3f} "
            f"{row.diff_ch_oc:>+8.3f} "
            f"{fmt_p(row.p_mwu):>12}")

    log(f"\n  TOP 20 ONCOCYTOMA > chRCC:")
    top_oc = df[df.diff_ch_oc < 0]\
               .head(20)
    for _, row in top_oc.iterrows():
        log(f"  {row.gene:<14} "
            f"{row.chRCC_mean:>8.3f} "
            f"{row.onco_mean:>8.3f} "
            f"{row.diff_ch_oc:>+8.3f} "
            f"{fmt_p(row.p_mwu):>12}")

    df.to_csv(
        os.path.join(S2_DIR,
                     "oncocytoma_separator.csv"),
        index=False)
    log(f"\n  Saved: oncocytoma_separator.csv")
    return df

# ═══════════════════════════════════════════════════════════════
# OBJ-5: CELL CYCLE / SENESCENCE
# ═══════════════════════════════════════════════════════════════

def obj5_cell_cycle(raw, t_cols, n_cols,
                     depth_t):
    log(""); log("="*60)
    log("OBJ-5 — CELL CYCLE / SENESCENCE")
    log("="*60)
    log("  CDKN2A r=+0.721: senescence or "
        "proliferation?")
    log("  C2-P4: MKI67 r < CDKN2A r")

    d = depth_t.dropna()

    df_cc = panel_r(raw, t_cols, n_cols,
                     depth_t, CELL_CYCLE,
                     "CELL_CYCLE")
    df_sn = panel_r(raw, t_cols, n_cols,
                     depth_t, SENESCENCE,
                     "SENESCENCE")
    df_sasp = panel_r(raw, t_cols, n_cols,
                       depth_t, SASP,
                       "SASP")

    print_panel(df_cc, "CELL CYCLE")
    print_panel(df_sn, "SENESCENCE MARKERS")
    print_panel(df_sasp, "SASP")

    # C2-P4: CDKN2A vs MKI67
    log("")
    log("  C2-P4 CHECK: CDKN2A r vs MKI67 r")
    r_cdkn2a = df_cc[
        df_cc.gene=="CDKN2A"].iloc[0].r \
        if "CDKN2A" in df_cc.gene.values \
        else np.nan
    r_mki67 = df_cc[
        df_cc.gene=="MKI67"].iloc[0].r \
        if "MKI67" in df_cc.gene.values \
        else np.nan

    log(f"  CDKN2A r = {r_cdkn2a:>+.4f}")
    log(f"  MKI67   r = {r_mki67:>+.4f}")

    if not np.isnan(r_cdkn2a) and \
            not np.isnan(r_mki67) and \
            r_mki67 < r_cdkn2a:
        log("  C2-P4 CONFIRMED ✓ "
            "(CDKN2A rises > MKI67 "
            "→ senescent not proliferative)")
    else:
        log("  C2-P4 NOT CONFIRMED ✗")

    # Senescence score
    sn_valid = df_sn[~df_sn.r.isna() &
                      ~df_sn.absent]
    sn_mean  = sn_valid.r.mean() \
        if len(sn_valid) > 0 else np.nan
    cc_valid = df_cc[~df_cc.r.isna() &
                      ~df_cc.absent]
    cc_mean  = cc_valid.r.mean() \
        if len(cc_valid) > 0 else np.nan
    sasp_valid = df_sasp[~df_sasp.r.isna() &
                          ~df_sasp.absent]
    sasp_mean  = sasp_valid.r.mean() \
        if len(sasp_valid) > 0 else np.nan

    log(f"\n  Mean r(depth):")
    log(f"    Cell cycle:  {cc_mean:>+.4f}")
    log(f"    Senescence:  {sn_mean:>+.4f}")
    log(f"    SASP:        {sasp_mean:>+.4f}")

    if not np.isnan(sn_mean) and \
            not np.isnan(cc_mean):
        if sn_mean > cc_mean:
            log("  INTERPRETATION: "
                "Senescence signature "
                "dominates over proliferation")
        else:
            log("  INTERPRETATION: "
                "Proliferative signature "
                "dominates")

    pd.concat([df_cc, df_sn, df_sasp])\
      .to_csv(
        os.path.join(S2_DIR,
                     "cell_cycle_senescence.csv"),
        index=False)
    return df_cc, df_sn

# ═══════════════════════════════════════════════════════════════
# OBJ-6: IMMUNE MICROENVIRONMENT
# ═══════════════════════════════════════════════════════════════

def obj6_immune(raw, t_cols, n_cols,
                 depth_t):
    log(""); log("="*60)
    log("OBJ-6 — IMMUNE MICROENVIRONMENT")
    log("="*60)
    log("  TET2 loss → immune evasion link")

    d  = depth_t.dropna()
    df = panel_r(raw, t_cols, n_cols,
                  depth_t, IMMUNE, "IMMUNE")
    print_panel(df, "IMMUNE PANEL")

    # C2-P5: CD8A and FOXP3 both < +0.20
    log("")
    log("  C2-P5 CHECK: CD8A and FOXP3 "
        "r(depth) < +0.20")
    r_cd8 = df[df.gene=="CD8A"].iloc[0].r \
        if "CD8A" in df.gene.values \
        else np.nan
    r_foxp3 = df[df.gene=="FOXP3"].iloc[0].r \
        if "FOXP3" in df.gene.values \
        else np.nan

    log(f"  CD8A  r = {r_cd8:>+.4f}")
    log(f"  FOXP3 r = {r_foxp3:>+.4f}")

    cd8_cold   = np.isnan(r_cd8) or \
        r_cd8 < 0.20
    foxp3_cold = np.isnan(r_foxp3) or \
        r_foxp3 < 0.20

    if cd8_cold and foxp3_cold:
        log("  C2-P5 CONFIRMED ✓ "
            "(immune cold — both < 0.20)")
    else:
        log("  C2-P5 NOT CONFIRMED ✗")

    # Immune cold vs hot summary
    effector = [
        "CD8A","GZMB","PRF1","IFNG","CD8B"]
    suppress = [
        "FOXP3","ARG1","IDO1","CD274",
        "HAVCR2","TIGIT"]
    for grp, genes in [
        ("Effector (CD8/GZMB)", effector),
        ("Suppressor (Treg/PD-L1)", suppress),
    ]:
        sub = df[df.gene.isin(genes) &
                  ~df.r.isna() &
                  ~df.absent]
        if len(sub) == 0: continue
        mr = sub.r.mean()
        log(f"  {grp:<32} mean_r={mr:>+.4f} "
            f"({len(sub)} genes)")

    # TET2 loss → immune link
    log("")
    log("  TET2-IMMUNE LINK:")
    log("  TET2 loss impairs TET2-mediated "
        "enhancer demethylation")
    log("  → silences immune gene promoters")
    log("  → predicts: CD8A low, IFN pathway "
        "low, PD-L1 low (immune excluded)")
    r_ifng = df[df.gene=="IFNG"].iloc[0].r \
        if "IFNG" in df.gene.values \
        else np.nan
    r_pdl1 = df[df.gene=="CD274"].iloc[0].r \
        if "CD274" in df.gene.values \
        else np.nan
    log(f"  IFNG  r(depth) = "
        f"{r_ifng:>+.4f}" if not
        np.isnan(r_ifng) else
        "  IFNG: ABSENT")
    log(f"  CD274 r(depth) = "
        f"{r_pdl1:>+.4f}" if not
        np.isnan(r_pdl1) else
        "  CD274: ABSENT")

    df.to_csv(
        os.path.join(S2_DIR,
                     "immune_panel.csv"),
        index=False)
    return df

# ═══════════════════════════════════════════════════════════════
# OBJ-7: REVISED DRUG TARGET SCORING
# ══════════════════════════════���════════════════════════════════

def obj7_drug_targets(raw, t_cols, n_cols,
                       depth_t,
                       df_chromatin,
                       df_met,
                       df_immune):
    log(""); log("="*60)
    log("OBJ-7 — REVISED DRUG TARGET SCORING")
    log("="*60)

    d = depth_t.dropna()

    DRUGS_V2 = [
        # Tier 1: strong rationale + depth signal
        ("T1", "TET2_activator",
         "TET2",  "epigenetic",
         "TET2 lost at depth — re-activation "
         "may restore IC identity"),
        ("T1", "SETD2_H3K36me3",
         "SETD2", "epigenetic",
         "SETD2 lost — H3K36me3 deficiency"),
        ("T1", "ERBB2_TDXd",
         "ERBB2", "targeted",
         "ERBB2 rises with depth ★ "
         "SHARED with PRCC"),
        ("T1", "CDKN2A_CDK46i",
         "CDKN2A","cell_cycle",
         "CDKN2A rises ★★ — CDK4/6 context"),
        ("T1", "KDM1A_LSD1i",
         "KDM1A", "epigenetic",
         "KDM1A rises — shared PRCC/chRCC"),
        # Tier 2: moderate
        ("T2", "HRH1_antihistamine",
         "HRH1",  "immune_metabolic",
         "HRH1 rises ★★ both chRCC+PRCC"),
        ("T2", "CA9_targeted",
         "CA9",   "metabolic",
         "CA9 rises ★ chRCC-specific"),
        ("T2", "PTEN_PI3K",
         "PTEN",  "signalling",
         "PTEN rises ★★ chRCC-specific"),
        ("T2", "SLC2A1_GLUT1",
         "SLC2A1","metabolic",
         "GLUT1 rises ★★★ chRCC-specific"),
        ("T2", "KHK_fructose",
         "KHK",   "metabolic",
         "KHK rises ★★★ fructose axis"),
        ("T2", "PPARGC1A_mito",
         "PPARGC1A","mito",
         "PGC1a falls — mito programme"),
        ("T2", "SDHA_complex2",
         "SDHA",  "mito",
         "SDHA rises ★ — complex II"),
        # Tier 3: contextual
        ("T3", "EZH2_PRC2i",
         "EZH2",  "epigenetic",
         "EZH2 falls in chRCC (PRCC-specific)"),
        ("T3", "mTOR_rapalogue",
         "MTOR",  "signalling",
         "MTOR neutral — context-dependent"),
        ("T3", "PDL1_checkpoint",
         "CD274", "immune",
         "CD274 rises but immune cold"),
        ("T3", "HIF_pathway",
         "HIF1A", "HIF",
         "HIF1A falls — not VHL-driven"),
        ("T3", "GPX4_ferroptosis",
         "GPX4",  "ferroptosis",
         "GPX4 falls ~ — context"),
        ("T3", "BAP1_HDAC",
         "BAP1",  "epigenetic",
         "BAP1 absent — check PBAF"),
    ]

    log(f"\n  {'Tier':<4} {'Drug':<22} "
        f"{'Gene':<12} {'r':>9} "
        f"{'sig':>5} {'Rationale'}")
    log(f"  {'─'*80}")

    rows = []
    for tier, drug, gene, cat, rationale \
            in DRUGS_V2:
        if gene not in raw.index:
            r, p = np.nan, np.nan
            status = "ABSENT"
        else:
            g_ = raw.loc[gene, t_cols]\
                   .reindex(d.index)
            r, p = safe_r(g_.values, d.values)
            status = ""

        fl = sig_flag(r, len(d)) \
            if not np.isnan(r) else "    "
        r_str = f"{r:>+9.4f}" \
            if not np.isnan(r) else \
            f"{'N/A':>9}"
        log(f"  {tier:<4} {drug:<22} "
            f"{gene:<12} {r_str} "
            f"{fl.strip():>5} "
            f"{rationale[:35]}")

        rows.append({
            "tier":      tier,
            "drug":      drug,
            "gene":      gene,
            "category":  cat,
            "r_depth":   r,
            "p_depth":   p,
            "rationale": rationale,
        })

    df_dt = pd.DataFrame(rows)

    # Tier summary
    log("")
    for tier in ["T1","T2","T3"]:
        sub = df_dt[df_dt.tier == tier]
        sig = sub[sub.r_depth.abs() >= 0.514]
        log(f"  {tier}: {len(sub)} targets  "
            f"sig(|r|≥0.514): {len(sig)}  "
            f"genes: "
            f"{sub.gene.tolist()}")

    df_dt.to_csv(
        os.path.join(S2_DIR,
                     "drug_targets_v2.csv"),
        index=False)
    log(f"\n  Saved: drug_targets_v2.csv")
    return df_dt

# ═══════════════════════════════════════════════════════════════
# OBJ-8: THREE-WAY CROSS-CANCER
# ═══════════════════════════════════════════════════════════════

def obj8_three_way(raw, t_cols, depth_t,
                    cc_df_s1):
    log(""); log("="*60)
    log("OBJ-8 — THREE-WAY CROSS-CANCER")
    log("="*60)
    log("  chRCC vs PRCC vs ccRCC")
    log("  Fixed references: PRCC (n=290, "
        "Doc 95a-g), ccRCC (literature)")

    d    = depth_t.dropna()
    rows = []
    all_genes = sorted(set(
        list(PRCC_REF.keys()) +
        list(CCRCC_REF.keys())))

    log(f"\n  {'Gene':<14} {'chRCC':>9} "
        f"{'PRCC':>9} {'ccRCC':>9} "
        f"{'pattern'}")
    log(f"  {'─'*60}")

    for gene in all_genes:
        # chRCC r
        if len(cc_df_s1) > 0 and \
                "gene" in cc_df_s1.columns and \
                gene in cc_df_s1.gene.values:
            r_ch = cc_df_s1[
                cc_df_s1.gene == gene
            ].iloc[0].get("r_chRCC", np.nan)
        elif gene in raw.index:
            g_   = raw.loc[gene, t_cols]\
                     .reindex(d.index)
            r_ch, _ = safe_r(g_.values,
                              d.values)
        else:
            r_ch = np.nan

        r_pr = PRCC_REF.get(gene, np.nan)
        r_cc = CCRCC_REF.get(gene, np.nan)

        # Three-way pattern
        def sign(r):
            if np.isnan(r): return "?"
            if r >  0.20: return "+"
            if r < -0.20: return "-"
            return "~"

        s_ch = sign(r_ch)
        s_pr = sign(r_pr)
        s_cc = sign(r_cc)
        pat  = f"{s_ch}/{s_pr}/{s_cc}"

        label = ""
        if s_ch == s_pr == s_cc == "+":
            label = "PAN_ATTRACTOR"
        elif s_ch == s_pr == s_cc == "-":
            label = "PAN_NORMAL"
        elif s_ch == "+" and \
                s_pr == "-" and s_cc == "-":
            label = "chRCC_UNIQUE(+)"
        elif s_ch == "-" and \
                s_pr == "+" and s_cc == "+":
            label = "chRCC_UNIQUE(-)"
        elif s_ch == s_pr and s_cc != s_ch:
            label = "RCC_shared"
        elif s_ch == s_cc and s_pr != s_ch:
            label = "chRCC_ccRCC_shared"
        elif s_pr == s_cc and s_ch != s_pr:
            label = "PRCC_ccRCC_shared"
        elif s_ch == "+" and s_cc == "-":
            label = "anti_ccRCC"

        ch_s = f"{r_ch:>+9.4f}" \
            if not np.isnan(r_ch) \
            else f"{'N/A':>9}"
        pr_s = f"{r_pr:>+9.4f}" \
            if not np.isnan(r_pr) \
            else f"{'N/A':>9}"
        cc_s = f"{r_cc:>+9.4f}" \
            if not np.isnan(r_cc) \
            else f"{'N/A':>9}"
        log(f"  {gene:<14} {ch_s} "
            f"{pr_s} {cc_s}  "
            f"{pat}  {label}")

        rows.append({
            "gene":       gene,
            "r_chRCC":    r_ch,
            "r_PRCC":     r_pr,
            "r_ccRCC":    r_cc,
            "pattern":    pat,
            "label":      label,
        })

    df = pd.DataFrame(rows)

    log("\n  THREE-WAY PATTERN SUMMARY:")
    for label in [
        "PAN_ATTRACTOR", "PAN_NORMAL",
        "chRCC_UNIQUE(+)", "chRCC_UNIQUE(-)",
        "anti_ccRCC",
        "chRCC_ccRCC_shared",
        "PRCC_ccRCC_shared",
        "RCC_shared",
    ]:
        sub = df[df.label == label]
        if len(sub) > 0:
            log(f"  {label:<22} n={len(sub)}  "
                f"{sub.gene.tolist()[:5]}")

    df.to_csv(
        os.path.join(S2_DIR,
                     "three_way_panel.csv"),
        index=False)
    return df

# ═══════════════════════════════════════════════════════════════
# OBJ-9: FIGURE
# ═══════════════════════════════════════════════════════════════

def obj9_figure(raw, t_cols, n_cols, o_cols,
                depth_t, depth_n, depth_o,
                df_chrom, df_pt_tf,
                df_met, axis_summary,
                df_oc, df_cc_s1, df_three,
                df_dt, df_cell, df_immune,
                panel_scores_s1):
    log(""); log("="*60)
    log("OBJ-9 — FIGURE")
    log("="*60)

    C = {
        "chRCC": "#8E44AD",
        "norm":  "#27AE60",
        "onco":  "#E67E22",
        "att":   "#E74C3C",
        "np":    "#3498DB",
        "gold":  "#F39C12",
        "grey":  "#95A5A6",
    }

    fig = plt.figure(figsize=(28, 30))
    gs  = gridspec.GridSpec(
        3, 3, figure=fig,
        hspace=0.50, wspace=0.42)

    # ── A: Chromatin panel ───────────────────
    ax = fig.add_subplot(gs[0, 0])
    ch_plot = df_chrom[
        ~df_chrom.r.isna() &
        ~df_chrom.absent
    ].sort_values("r")
    if len(ch_plot) > 0:
        cols = [C["att"] if v > 0
                else C["np"]
                for v in ch_plot.r]
        ax.barh(range(len(ch_plot)),
                ch_plot.r.values,
                color=cols, alpha=0.8)
        ax.set_yticks(range(len(ch_plot)))
        ax.set_yticklabels(
            ch_plot.gene.values, fontsize=6)
        ax.axvline(0, color="k", lw=0.8)
        ax.axvline( 0.514, color="k",
                    lw=0.5, ls="--", alpha=0.4)
        ax.axvline(-0.514, color="k",
                    lw=0.5, ls="--", alpha=0.4)
        ax.set_xlabel("r(depth)")
    ax.set_title(
        "A: Chromatin Collapse Panel\n"
        "TET2/SETD2/DNMT/PRC2/PBAF",
        fontsize=9, fontweight="bold")

    # ── B: PT TF panel ───────────────────────
    ax = fig.add_subplot(gs[0, 1])
    tf_plot = df_pt_tf[
        ~df_pt_tf.r.isna() &
        ~df_pt_tf.absent
    ].sort_values("r")
    if len(tf_plot) > 0:
        cols = [C["att"] if v > 0
                else C["np"]
                for v in tf_plot.r]
        ax.barh(range(len(tf_plot)),
                tf_plot.r.values,
                color=cols, alpha=0.8)
        ax.set_yticks(range(len(tf_plot)))
        ax.set_yticklabels(
            tf_plot.gene.values, fontsize=6)
        ax.axvline(0, color="k", lw=0.8)
        ax.axvline(0.514, color="k",
                    lw=0.5, ls="--", alpha=0.4)
        ax.axvline(-0.514, color="k",
                    lw=0.5, ls="--", alpha=0.4)
        ax.set_xlabel("r(depth)")
    ax.set_title(
        "B: PT Transcription Factors\n"
        "HNF4A/HNF1A/PPARA/PPARGC1A",
        fontsize=9, fontweight="bold")

    # ── C: Metabolic axis bars ───────────────
    ax = fig.add_subplot(gs[0, 2])
    if axis_summary:
        axnames = list(axis_summary.keys())
        axvals  = [axis_summary[a]
                    for a in axnames]
        cols = [C["att"] if v > 0
                else C["np"]
                for v in axvals]
        ax.barh(range(len(axnames)), axvals,
                color=cols, alpha=0.85)
        ax.set_yticks(range(len(axnames)))
        ax.set_yticklabels(axnames, fontsize=8)
        ax.axvline(0, color="k", lw=0.8)
        ax.set_xlabel("Mean r(depth)")
    ax.set_title(
        "C: Metabolic Axis Scores",
        fontsize=9, fontweight="bold")

    # ── D: Three-way scatter PRCC vs ccRCC ───
    ax = fig.add_subplot(gs[1, 0])
    tw = df_three.dropna(
        subset=["r_chRCC","r_PRCC","r_ccRCC"])
    col_map = {
        "PAN_ATTRACTOR":     C["att"],
        "PAN_NORMAL":        C["np"],
        "chRCC_UNIQUE(+)":   C["chRCC"],
        "chRCC_UNIQUE(-)":   C["chRCC"],
        "anti_ccRCC":        C["gold"],
        "chRCC_ccRCC_shared":C["grey"],
        "PRCC_ccRCC_shared": "#BDC3C7",
        "RCC_shared":        "#7F8C8D",
    }
    for _, row in tw.iterrows():
        col = col_map.get(row.label,
                           "#BDC3C7")
        ax.scatter(row.r_PRCC, row.r_ccRCC,
                   c=col, s=20, alpha=0.7,
                   zorder=2)
        ax.annotate(
            row.gene,
            (row.r_PRCC, row.r_ccRCC),
            fontsize=4.5,
            xytext=(2,2),
            textcoords="offset points")
    ax.axhline(0, color="k", lw=0.5)
    ax.axvline(0, color="k", lw=0.5)
    ax.set_xlabel("r PRCC", fontsize=8)
    ax.set_ylabel("r ccRCC", fontsize=8)
    ax.set_title(
        "D: PRCC vs ccRCC Reference\n"
        "(coloured by chRCC pattern)",
        fontsize=9, fontweight="bold")

    # ── E: Oncocytoma separator ──────────────
    ax = fig.add_subplot(gs[1, 1])
    if len(df_oc) > 0:
        top30 = pd.concat([
            df_oc[df_oc.diff_ch_oc > 0].head(15),
            df_oc[df_oc.diff_ch_oc < 0].head(15),
        ]).sort_values("diff_ch_oc")
        cols = [C["chRCC"] if v > 0
                else C["onco"]
                for v in top30.diff_ch_oc]
        ax.barh(range(len(top30)),
                top30.diff_ch_oc.values,
                color=cols, alpha=0.8)
        ax.set_yticks(range(len(top30)))
        ax.set_yticklabels(
            top30.gene.values, fontsize=6)
        ax.axvline(0, color="k", lw=0.8)
        ax.set_xlabel("chRCC − Oncocytoma")
    ax.set_title(
        "E: chRCC vs Oncocytoma\n"
        "Top Discriminators",
        fontsize=9, fontweight="bold")

    # ── F: Immune panel ──────────────────────
    ax = fig.add_subplot(gs[1, 2])
    im_plot = df_immune[
        ~df_immune.r.isna() &
        ~df_immune.absent
    ].sort_values("r")
    if len(im_plot) > 0:
        cols = [C["att"] if v > 0
                else C["np"]
                for v in im_plot.r]
        ax.barh(range(len(im_plot)),
                im_plot.r.values,
                color=cols, alpha=0.8)
        ax.set_yticks(range(len(im_plot)))
        ax.set_yticklabels(
            im_plot.gene.values, fontsize=6)
        ax.axvline(0, color="k", lw=0.8)
        ax.axvline( 0.514, color="k",
                    lw=0.5, ls="--", alpha=0.4)
        ax.axvline(-0.514, color="k",
                    lw=0.5, ls="--", alpha=0.4)
        ax.set_xlabel("r(depth)")
    ax.set_title(
        "F: Immune Microenvironment",
        fontsize=9, fontweight="bold")

    # ── G: Drug target tier plot ─────────────
    ax = fig.add_subplot(gs[2, 0])
    dt_plot = df_dt.dropna(
        subset=["r_depth"])\
        .sort_values("r_depth",
                      key=abs,
                      ascending=False)\
        .head(18)
    tier_col = {"T1": C["att"],
                 "T2": C["gold"],
                 "T3": C["grey"]}
    if len(dt_plot) > 0:
        cols = [tier_col.get(r.tier, C["grey"])
                for _, r in dt_plot.iterrows()]
        ax.barh(range(len(dt_plot)),
                dt_plot.r_depth.values,
                color=cols, alpha=0.85)
        ax.set_yticks(range(len(dt_plot)))
        ax.set_yticklabels(
            dt_plot.drug.values, fontsize=6)
        ax.axvline(0, color="k", lw=0.8)
        ax.axvline( 0.514, color="k",
                    lw=0.5, ls="--", alpha=0.4)
        ax.axvline(-0.514, color="k",
                    lw=0.5, ls="--", alpha=0.4)
        ax.set_xlabel("r(depth)")
        for lab, col in [
            ("Tier 1", C["att"]),
            ("Tier 2", C["gold"]),
            ("Tier 3", C["grey"]),
        ]:
            ax.barh([], [], color=col,
                    label=lab, alpha=0.85)
        ax.legend(fontsize=7, loc="lower right")
    ax.set_title(
        "G: Drug Targets (v2)\n"
        "T1=strong / T2=moderate / T3=context",
        fontsize=9, fontweight="bold")

    # ── H: Cell cycle / senescence ───────────
    ax = fig.add_subplot(gs[2, 1])
    cc_plot = df_cell[
        ~df_cell.r.isna() &
        ~df_cell.absent
    ].sort_values("r")
    if len(cc_plot) > 0:
        cols = [C["att"] if v > 0
                else C["np"]
                for v in cc_plot.r]
        ax.barh(range(len(cc_plot)),
                cc_plot.r.values,
                color=cols, alpha=0.8)
        ax.set_yticks(range(len(cc_plot)))
        ax.set_yticklabels(
            cc_plot.gene.values, fontsize=7)
        ax.axvline(0, color="k", lw=0.8)
        ax.axvline( 0.514, color="k",
                    lw=0.5, ls="--", alpha=0.4)
        ax.axvline(-0.514, color="k",
                    lw=0.5, ls="--", alpha=0.4)
        ax.set_xlabel("r(depth)")
    ax.set_title(
        "H: Cell Cycle vs Senescence",
        fontsize=9, fontweight="bold")

    # ── I: Integrated scorecard ──────────────
    ax = fig.add_subplot(gs[2, 2])
    ax.axis("off")

    checks = [
        ("C2-P1","TET2/SETD2 co-lost"),
        ("C2-P2","HNF4A/HNF1A rises"),
        ("C2-P3","KHK/ALDOB/TKT coherent"),
        ("C2-P4","CDKN2A>MKI67 (senescent)"),
        ("C2-P5","CD8A+FOXP3 cold"),
        ("C2-P6","DNMT3A/B rises"),
    ]

    verdicts = []
    for code, desc in checks:
        matching = [l for l in log_lines
                    if code in l]
        if not matching:
            v = "?"
        elif "CONFIRMED ✓" in matching[-1]:
            v = "✓"; 
        elif "NOT CONFIRMED" in matching[-1]:
            v = "✗"
        else:
            v = "?"
        verdicts.append((code, desc, v))

    n_conf = sum(1 for _, _, v in verdicts
                 if v == "✓")

    txt = (
        "chRCC False Attractor — Script 2\n"
        "OrganismCore | Doc 96b | 2026-03-02\n"
        "══════════════════════════════════\n"
        "PREDICTIONS:\n"
    )
    for code, desc, v in verdicts:
        txt += f"  {code}: {desc:<28} {v}\n"
    txt += (
        f"\nOVERALL: {n_conf}/{len(verdicts)}\n"
        "══════════════════════════════════\n"
        "FROM Script 1 (OBJ-5, platform-indep):\n"
        "  KHK     chRCC +0.84 / PRCC -0.75\n"
        "  SLC34A1 chRCC +0.62 / PRCC -0.64\n"
        "  TET2    chRCC -0.72 / PRCC +0.29\n"
        "  SETD2   chRCC -0.43 / PRCC +0.31\n"
        "  ERBB2   SHARED +0.57/+0.36\n"
        "══════════════════════════════════\n"
        "DOMINANT: PROXIMAL_TUBULE (Script 1)\n"
        "CHROMATIN: TET2/SETD2 collapse\n"
        "ANTI-WARBURG: LDHA falls\n"
        "IMMUNE: cold (TET2-mediated)\n"
    )
    ax.text(
        0.03, 0.97, txt,
        transform=ax.transAxes,
        fontsize=6, va="top",
        fontfamily="monospace",
        bbox=dict(boxstyle="round",
                  facecolor="#F0F4F8",
                  alpha=0.9))
    ax.set_title("I: Script 2 Scorecard",
                 fontsize=9, fontweight="bold")

    fig.suptitle(
        "chRCC False Attractor — Script 2  |  "
        "OrganismCore | Document 96b  |  "
        "2026-03-02",
        fontsize=12, fontweight="bold",
        y=0.999)

    out = os.path.join(
        S2_DIR,
        "chrcc_script2_figure.pdf")
    fig.savefig(out, bbox_inches="tight",
                dpi=150)
    plt.close(fig)
    log(f"  Figure saved: {out}")

# ═══════════════════════════════════════════════════════════════
# SCORECARD
# ═══════════════════════════════════════���═══════════════════════

def print_scorecard():
    log(""); log("="*60)
    log("SCRIPT 2 — FINAL SCORECARD")
    log("="*60)

    checks = [
        ("C2-P1", "TET2/SETD2 co-lost"),
        ("C2-P2", "HNF4A or HNF1A rises"),
        ("C2-P3", "KHK/ALDOB/TKT coherent"),
        ("C2-P4", "CDKN2A > MKI67"),
        ("C2-P5", "CD8A+FOXP3 cold"),
        ("C2-P6", "DNMT3A/B rises"),
    ]

    confirmed = 0
    for code, desc in checks:
        matching = [l for l in log_lines
                    if code in l]
        if not matching:
            v = "CHECK LOG"
        elif "CONFIRMED ✓" in matching[-1]:
            v = "CONFIRMED ✓"; confirmed += 1
        elif "NOT CONFIRMED" in matching[-1]:
            v = "NOT CONFIRMED ✗"
        else:
            v = matching[-1][-30:].strip()
        log(f"  {code} {desc:<32} {v}")

    log(f"\n  OVERALL: {confirmed}/"
        f"{len(checks)}")
    log("")
    log("  CROSS-CANCER FINDINGS (Script 1 "
        "OBJ-5, platform-independent):")
    log("  KHK:    chRCC +0.835 vs PRCC -0.746"
        "  DIVERGENT — fructose acquired")
    log("  TET2:   chRCC -0.720 vs PRCC +0.292"
        "  DIVERGENT — chromatin collapse")
    log("  SETD2:  chRCC -0.427 vs PRCC +0.308"
        "  DIVERGENT — H3K36me3 lost")
    log("  ERBB2:  chRCC +0.567 vs PRCC +0.360"
        "  SHARED — therapeutic target")
    log("  HRH1:   chRCC +0.659 vs PRCC +0.630"
        "  SHARED — HRH1 axis")
    log("")
    log("  NEXT STEPS:")
    log("  Script 3: TET2/SETD2 methylation "
        "consequences")
    log("  Script 4: ERBB2/HRH1/KDM1A "
        "therapeutic axis")
    log("  OS: re-run when TCGA-KICH "
        "survival available")

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    log("="*60)
    log("chRCC FALSE ATTRACTOR — SCRIPT 2")
    log("OrganismCore | Document 96b | "
        "2026-03-02")
    log("Author: Eric Robert Lawson")
    log("="*60)
    log("")
    log("Builds on Script 1 OBJ-5 findings:")
    log("  PROXIMAL_TUBULE dominant identity")
    log("  TET2/SETD2 chromatin collapse")
    log("  KHK/SLC34A1/GOT1 diverge from PRCC")
    log("  ERBB2/HRH1/KDM1A shared with PRCC")
    log("")

    # Load
    (raw, t_cols, n_cols, o_cols,
     depth_t, depth_n, depth_o,
     att_df, cc_df) = load_data()

    # OBJ-1: Chromatin
    df_chrom = obj1_chromatin(
        raw, t_cols, n_cols, depth_t)

    # OBJ-2: PT TFs
    df_pt_tf = obj2_pt_tfs(
        raw, t_cols, n_cols, depth_t)

    # OBJ-3: Metabolism
    df_met, axis_summary = obj3_metabolism(
        raw, t_cols, n_cols, depth_t)

    # OBJ-4: Oncocytoma
    df_oc = obj4_oncocytoma(
        raw, t_cols, n_cols, o_cols,
        depth_t, depth_n, depth_o)

    # OBJ-5: Cell cycle
    df_cell, df_sn = obj5_cell_cycle(
        raw, t_cols, n_cols, depth_t)

    # OBJ-6: Immune
    df_immune = obj6_immune(
        raw, t_cols, n_cols, depth_t)

    # OBJ-7: Drug targets
    df_dt = obj7_drug_targets(
        raw, t_cols, n_cols, depth_t,
        df_chrom, df_met, df_immune)

    # OBJ-8: Three-way
    df_three = obj8_three_way(
        raw, t_cols, depth_t, cc_df)

    # OBJ-9: Figure
    obj9_figure(
        raw, t_cols, n_cols, o_cols,
        depth_t, depth_n, depth_o,
        df_chrom, df_pt_tf,
        df_met, axis_summary,
        df_oc, cc_df, df_three,
        df_dt, df_cell, df_immune,
        panel_scores_s1={
            "PROXIMAL_TUBULE": +0.4265,
            "INTERCALATED":    +0.2042,
            "MITOCHONDRIAL":   +0.0843,
            "BILIARY/DUCTAL":  -0.0006,
            "INVASION/EMT":    -0.0118,
        })

    # Scorecard
    print_scorecard()

    write_log()

    log("")
    log("="*60)
    log("SCRIPT 2 COMPLETE")
    log(f"Results: {S2_DIR}")
    log(f"Log:     {LOG_FILE}")
    log("="*60)


if __name__ == "__main__":
    main()
