"""
PRCC False Attractor — Script 1
DISCOVERY RUN — PREDICTIONS BEFORE DATA

Framework: OrganismCore
Document 95a-pre | 2026-03-02
Author: Eric Robert Lawson

═══════════════════════════════════════════════════════════════
PREDICTIONS LOCKED BEFORE DATA — 2026-03-02
═══════════════════════════════════════════════════════════════

LINEAGE:
  Cell of origin: Proximal tubule epithelial cell (PT)
  Block level:    Papillary PT progenitor state
                  (later saddle point than ccRCC)
  Two basins:     Type 1 (MET/proliferative, shallower)
                  Type 2 (SETD2-EZH2/epigenetic, deeper)

SWITCH GENES — predicted DOWN in PRCC vs normal PT:
  SLC13A2  mature PT citrate transporter (NaDC1)
  SLC22A6  organic anion transporter 1 (OAT1)
  CUBN     PT endocytic receptor (cubilin)
  LRP2     PT endocytic co-receptor (megalin)
  MIOX     PT myo-inositol oxygenase (metabolic)
  UMOD     CONTROL — thick ascending limb only; should be FLAT

FALSE ATTRACTOR MARKERS — predicted UP in PRCC:
  MET      Type 1 primary driver — papillary progenitor
  HMOX1    haem catabolism / foamy macrophage niche
  CAV1     ECM caveolae remodelling
  VIM      dedifferentiation (stronger in Type 2)
  VEGFA    modest elevation downstream of MET/HIF

EPIGENETIC:
  EZH2     UP (gain of function, both types)
  SETD2    DOWN in Type 2 (H3K36me3 writer — loss)
  TET2     DOWN functional (αKG depletion)
  DNMT3A   direction uncertain — read from data

GAP CIRCUITS (predicted):
  MET → SLC22A6:  BROKEN (near zero r)
  SETD2 → EZH2:  NEGATIVE r (lock confirmed)
  MET → CUBN:    BROKEN (near zero r)

SUBTYPE DEPTH:
  S1-P1: Type 2 depth > Type 1 depth (p < 0.05)
  S1-P2: CIMP / FH-mutant = deepest stratum

DRUG TARGETS (pre-data, pre-literature):
  Type 1: MET inhibitor (cabozantinib / savolitinib)
  Type 2: EZH2 inhibitor (tazemetostat)
  CIMP:   αKG + EZH2i combination (NOVEL)
  Both:   VEGFR/mTOR (standard — depth-unaware)
  NOT:    Belzutifan — VHL flat in PRCC
          (structural contrast with ccRCC)

NOVEL PRE-DATA PREDICTIONS:
  N1: Belzutifan inactive in PRCC — VHL/HIF2A flat
  N2: CIMP/FH subtype replicates ccRCC TCA-chromatin axis
  N3: αKG + EZH2i combination in CIMP PRCC
  N4: MET → PT identity circuit broken
      (MET does NOT restore SW genes)

═══════════════════════════════════════════════════════════════
DISCOVERY PRINCIPLE:
  The gene panel is wide — 70+ genes.
  Depth correlations are the primary output.
  Unexpected signals are the finding.
  Confirmations validate the framework.
  Surprises extend it.
═══════════════════════════════════════════════════════════════

DATA:
  PRIMARY:   TCGA-KIRP via UCSC Xena
             HiSeqV2 log2-RSEM
             n ~289 tumour, n=32 normal
             Type 1 / Type 2 / CIMP subtype annotation
  CLINICAL:  KIRP_clinicalMatrix (subtype, stage)
  OUTPUT:    ./prcc_false_attractor/results_s1/
"""

import os, gzip, io, time
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy import stats
from scipy.stats import mannwhitneyu, pearsonr
import warnings
warnings.filterwarnings("ignore")

# ═══════════════════════════════════════════════════════════════
# PATHS
# ═══════════════════════════════════════════════════════════════

BASE_DIR    = "./prcc_false_attractor/"
RESULTS_DIR = os.path.join(BASE_DIR, "results_s1/")
LOG_FILE    = os.path.join(RESULTS_DIR, "s1_log.txt")

XENA_EXPR_URL  = (
    "https://tcga-xena-hub.s3.us-east-1.amazonaws.com/"
    "download/TCGA.KIRP.sampleMap%2FHiSeqV2.gz"
)
XENA_CLIN_URL  = (
    "https://tcga-xena-hub.s3.us-east-1.amazonaws.com/"
    "download/TCGA.KIRP.sampleMap%2FKIRP_clinicalMatrix"
)

EXPR_PATH  = os.path.join(BASE_DIR, "TCGA_KIRP_HiSeqV2.gz")
CLIN_PATH  = os.path.join(BASE_DIR, "KIRP_clinicalMatrix.tsv")

os.makedirs(BASE_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# ═══════════════════════════════════════════════════════════════
# GENE PANELS — deliberately wide for discovery
# ═══════════════════════════════════════════════════════════════

# --- Switch genes: mature PT identity (predicted DOWN) --------
SW_GENES = [
    "SLC13A2",   # NaDC1 — apical citrate transporter (top SW ccRCC)
    "SLC22A6",   # OAT1  — basolateral organic anion transporter
    "SLC34A1",   # NaPi-IIa — phosphate transporter (PT-specific)
    "CUBN",      # cubilin — endocytic receptor
    "LRP2",      # megalin — endocytic co-receptor
    "MIOX",      # myo-inositol oxygenase (PT metabolic)
    "UMOD",      # CONTROL: thick ascending limb — should be FLAT
    "SLC5A2",    # SGLT2 — glucose transporter (PT-specific)
    "FABP1",     # fatty acid binding protein 1 (PT metabolic)
    "GPX3",      # glutathione peroxidase 3 (PT antioxidant)
    "FBP1",      # fructose-1,6-bisphosphatase (was key ccRCC SW)
]

# --- False attractor markers (predicted UP in PRCC) -----------
FA_GENES = [
    "MET",       # Type 1 primary driver
    "HMOX1",     # haem oxygenase 1 — foamy macrophage niche
    "CAV1",      # caveolin-1 — ECM/lipid raft remodelling
    "VIM",       # vimentin — dedifferentiation
    "VEGFA",     # angiogenesis — downstream MET/HIF
    "KRT7",      # cytokeratin 7 — papillary epithelial identity
    "KRT19",     # cytokeratin 19 — biliary/papillary marker
    "PROM1",     # CD133 — progenitor identity
    "CD44",      # progenitor / adhesion
    "SOX4",      # progenitor TF
    "TWIST1",    # EMT driver (was strong in ICC)
    "CDH1",      # E-cadherin — epithelial retention check
    "ITGA3",     # integrin α3 — papillary adhesion
]

# --- Epigenetic panel ------------------------------------------
EPIGENETIC_GENES = [
    "EZH2",      # PRC2 H3K27me3 writer (predicted UP)
    "SETD2",     # H3K36me3 writer (predicted DOWN Type 2)
    "TET2",      # 5mC → 5hmC (αKG-dependent; predicted low)
    "DNMT3A",    # DNA methyltransferase (uncertain direction)
    "KDM1A",     # LSD1 — H3K4me demethylase
    "HDAC1",     # deacetylase — CoREST complex
    "RCOR1",     # CoREST scaffold
    "ASXL1",     # Polycomb accessory
    "BAP1",      # deubiquitinase — PBRM1 complex partner
    "PBRM1",     # SWI/SNF — chromatin remodeller (KIRP common mutation)
]

# --- TCA / metabolic circuit ----------------------------------
TCA_GENES = [
    "FH",        # fumarate hydratase — CIMP subtype driver
    "OGDHL",     # oxoglutarate dehydrogenase-like (was key ccRCC)
    "SUCLG1",    # succinyl-CoA ligase (αKG axis)
    "GOT1",      # aspartate aminotransferase (transition index ccRCC)
    "LDHB",      # lactate dehydrogenase B (metabolic ID)
    "LDHD",      # lactate dehydrogenase D
    "ATP5A1",    # ATP synthase (OXPHOS identity)
    "ACAT1",     # acetyl-CoA acetyltransferase
    "SLC16A1",   # MCT1 — monocarboxylate transporter
    "SLC2A1",    # GLUT1 — glucose transporter (was ccRCC FA)
    "SLC2A9",    # GLUT9 — urate transporter (PT-specific)
    "ACADM",     # medium-chain acyl-CoA dehydrogenase (FAO)
    "CPT1A",     # carnitine palmitoyltransferase (FAO)
]

# --- ECM / stroma panel ----------------------------------------
ECM_GENES = [
    "LOXL2",     # lysyl oxidase-like 2 (was #1 ccRCC)
    "COL1A1",    # collagen type 1
    "ACTA2",     # alpha-SMA — activated fibroblast
    "POSTN",     # periostin — ECM remodelling
    "TGFB1",     # TGF-beta 1 — stroma activator
    "MMP9",      # matrix metalloproteinase 9
    "MMP2",      # matrix metalloproteinase 2
    "FN1",       # fibronectin 1
]

# --- Immune / TME panel ----------------------------------------
IMMUNE_GENES = [
    "CD274",     # PD-L1 — checkpoint
    "FOXP3",     # Treg marker
    "IL2RA",     # CD25 — Treg activation
    "HAVCR2",    # TIM-3 — exhaustion
    "CD8A",      # cytotoxic T cell
    "IFI16",     # innate DNA sensor (was strong ccRCC)
    "B2M",       # MHC-I component
    "TIGIT",     # immune checkpoint
]

# --- MET pathway / RTK ----------------------------------------
RTK_GENES = [
    "MET",       # (also in FA — duplicated intentionally)
    "EGFR",      # EGF receptor
    "ERBB2",     # HER2
    "FGFR1",     # FGF receptor 1
    "FGFR3",     # FGF receptor 3
    "AXL",       # AXL receptor (was Wall 4 ccRCC)
    "MTOR",      # mTOR — downstream MET
    "RPTOR",     # raptor — mTORC1
]

# --- HIF / VHL axis (structural contrast with ccRCC) ----------
HIF_GENES = [
    "EPAS1",     # HIF2A — should be FLAT (not VHL-driven in PRCC)
    "HIF1A",     # HIF1A
    "VHL",       # VHL — should not be primary driver in PRCC
    "CA9",       # carbonic anhydrase 9 (HIF target — was UP ccRCC)
    "VEGFA",     # (also in FA)
]

# --- Scaffold / proliferation ---------------------------------
SCAFFOLD_GENES = [
    "MKI67",     # Ki67 — proliferation
    "MYC",       # MYC — oncogenic scaffold
    "CDK4",      # cell cycle
    "CCND1",     # cyclin D1
    "CDKN2A",    # p16 — predicted DOWN Type 2 (silenced)
    "CDKN1A",    # p21
    "TOP2A",     # topoisomerase IIa
]

# --- Build full panel (deduplicated) --------------------------
ALL_PANEL = list(dict.fromkeys(
    SW_GENES + FA_GENES + EPIGENETIC_GENES +
    TCA_GENES + ECM_GENES + IMMUNE_GENES +
    RTK_GENES + HIF_GENES + SCAFFOLD_GENES
))

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
    log_lines.clear()

def fmt_p(p):
    if p < 1e-15: return "p<1e-15"
    if p < 0.001: return f"p={p:.2e}"
    return f"p={p:.4f}"

def norm01(arr):
    a = np.asarray(arr, dtype=float)
    mn, mx = np.nanmin(a), np.nanmax(a)
    if mx == mn: return np.zeros_like(a)
    return (a - mn) / (mx - mn)

def safe_r(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    mask = np.isfinite(x) & np.isfinite(y)
    if mask.sum() < 5:
        return (np.nan, np.nan)
    return pearsonr(x[mask], y[mask])

def safe_mwu(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    a, b = a[np.isfinite(a)], b[np.isfinite(b)]
    if len(a) < 3 or len(b) < 3:
        return (np.nan, np.nan)
    return mannwhitneyu(a, b, alternative="two-sided")

# ═══════════════════════════════════════════════════════════════
# DOWNLOAD
# ═══════════════════════════════════════════════════════════════

def try_get(url, dest, min_size=500):
    try:
        import urllib.request
        if os.path.exists(dest):
            if os.path.getsize(dest) > min_size:
                log(f"  Cached: {dest}")
                return True
        log(f"  Trying: {url}")
        urllib.request.urlretrieve(url, dest)
        sz = os.path.getsize(dest)
        log(f"  OK: {sz/1e6:.1f} MB → {dest}")
        return True
    except Exception as e:
        log(f"  FAIL: {e}")
        return False

def download_all():
    log("=" * 60)
    log("DOWNLOAD")
    log("=" * 60)

    # Expression
    ok_expr = try_get(XENA_EXPR_URL, EXPR_PATH, min_size=5_000_000)

    # Clinical
    ok_clin = try_get(XENA_CLIN_URL, CLIN_PATH, min_size=10_000)

    return ok_expr, ok_clin

# ═══════════════════════════════════════════════════════════════
# PARSE TCGA-KIRP
# ═══════════════════════════════════════════════════════════════

def parse_tcga():
    """
    Load HiSeqV2 log2-RSEM matrix.
    Returns:
      expr   — DataFrame (genes × samples), panel genes only
      meta   — DataFrame with sample_id, sample_type
    """
    log("")
    log("=" * 60)
    log("PARSE TCGA-KIRP HiSeqV2")
    log("=" * 60)

    # --- load expression ----------------------------------------
    open_fn = gzip.open if EXPR_PATH.endswith(".gz") else open
    with open_fn(EXPR_PATH, "rt") as fh:
        raw = pd.read_csv(fh, sep="\t", index_col=0)

    log(f"  Raw matrix: {raw.shape[0]} genes × {raw.shape[1]} samples")

    # Filter to panel genes present in matrix
    avail = [g for g in ALL_PANEL if g in raw.index]
    missing = [g for g in ALL_PANEL if g not in raw.index]
    log(f"  Panel genes available: {len(avail)}/{len(ALL_PANEL)}")
    if missing:
        log(f"  Missing from matrix:   {missing}")

    expr = raw.loc[avail].copy()

    # --- sample classification ----------------------------------
    # TCGA barcode: TCGA-XX-XXXX-01A → sample_type from digit 13-14
    # -01  = Primary Solid Tumour
    # -11  = Solid Tissue Normal
    sample_ids = list(expr.columns)
    sample_type = []
    for s in sample_ids:
        parts = s.split("-")
        if len(parts) >= 4:
            code = parts[3][:2]
            if code == "01":
                sample_type.append("tumour")
            elif code == "11":
                sample_type.append("normal")
            else:
                sample_type.append("other")
        else:
            sample_type.append("other")

    meta = pd.DataFrame({
        "sample_id":   sample_ids,
        "sample_type": sample_type,
    })

    t_n = (meta.sample_type == "tumour").sum()
    n_n = (meta.sample_type == "normal").sum()
    o_n = (meta.sample_type == "other").sum()
    log(f"  Tumour samples:  {t_n}")
    log(f"  Normal samples:  {n_n}")
    log(f"  Other:           {o_n}")

    return expr, meta

# ═══════════════════════════════════════════════════════════════
# PARSE CLINICAL — subtype annotation
# ═══════════════════════════════════════════════════════════════

def parse_clinical():
    """
    Load KIRP clinical matrix.
    Extract histologic subtype (Type 1 / Type 2),
    stage, and any FH / CIMP flags if present.
    Returns DataFrame indexed by sample_id (short barcode).
    """
    log("")
    log("=" * 60)
    log("PARSE CLINICAL — KIRP")
    log("=" * 60)

    if not os.path.exists(CLIN_PATH):
        log("  Clinical file not found — skipping.")
        return None

    clin = pd.read_csv(CLIN_PATH, sep="\t", index_col=0,
                       low_memory=False)
    log(f"  Clinical rows: {clin.shape[0]}, "
        f"cols: {clin.shape[1]}")
    log(f"  Columns: {list(clin.columns[:20])}")

    # Standardise index to short barcode (first 12 chars)
    clin.index = clin.index.str[:12]

    # Identify subtype column
    subtype_col = None
    for candidate in [
        "histological_type", "histologic_diagnosis",
        "tumor_histology", "paper_Histologic.type",
        "paper_histologic_type",
    ]:
        if candidate in clin.columns:
            subtype_col = candidate
            break

    if subtype_col:
        counts = clin[subtype_col].value_counts()
        log(f"  Subtype column: {subtype_col}")
        log(f"  Values:\n{counts.to_string()}")
    else:
        log("  Subtype column not identified — "
            "will attempt to infer from available columns.")
        # Show all columns for manual inspection
        log(f"  All columns: {list(clin.columns)}")

    return clin, subtype_col

# ═══════════════════════════════════════════════════════════════
# SADDLE ANALYSIS
# ═══════════════════════════════════════════════════════════════

def saddle_analysis(expr, meta, label):
    """
    Per-gene tumour vs normal.
    Mann-Whitney U, fold change (median difference log2 space).
    Returns saddle_res dict: gene → {result, fc, p}
    Also returns formatted table for logging.
    """
    log("")
    log("=" * 60)
    log(f"SADDLE ANALYSIS — {label}")
    log("=" * 60)
    log("  Per-gene tumour vs normal comparison.")
    log("  Predictions vs actuals for each panel gene.")
    log("")

    meta_idx = meta.set_index("sample_id").reindex(expr.columns)
    t_cols = expr.columns[(meta_idx.sample_type == "tumour").values]
    n_cols = expr.columns[(meta_idx.sample_type == "normal").values]

    log(f"  Tumour n={len(t_cols)}, Normal n={len(n_cols)}")

    if len(n_cols) == 0:
        log("  ERROR: No normal samples — cannot run saddle.")
        return {}

    saddle_res = {}
    rows = []

    # Determine predicted direction per gene
    predicted = {}
    for g in SW_GENES:
        predicted[g] = "DOWN" if g != "UMOD" else "FLAT"
    for g in FA_GENES:
        predicted[g] = "UP"
    for g in EPIGENETIC_GENES:
        predicted[g] = "UP"  # default; will note exceptions
    predicted["SETD2"] = "DOWN"
    predicted["TET2"]  = "DOWN"
    predicted["BAP1"]  = "UNCERTAIN"
    predicted["DNMT3A"] = "UNCERTAIN"
    for g in TCA_GENES:
        predicted[g] = "DOWN"  # PT metabolic genes lost
    predicted["SLC2A1"] = "UP"   # GLUT1 up (as in ccRCC)
    predicted["SLC16A1"] = "UP"  # MCT1 up
    for g in ECM_GENES:
        predicted[g] = "UP"
    for g in IMMUNE_GENES:
        predicted[g] = "UNCERTAIN"
    for g in RTK_GENES:
        predicted[g] = "UNCERTAIN"
    for g in HIF_GENES:
        predicted["EPAS1"] = "FLAT"
        predicted["VHL"]   = "FLAT"
        predicted["CA9"]   = "FLAT"
        predicted["HIF1A"] = "UNCERTAIN"
    for g in SCAFFOLD_GENES:
        predicted[g] = "UP"
    predicted["CDKN2A"] = "DOWN"  # silenced in Type 2

    for gene in expr.index:
        t_vals = expr.loc[gene, t_cols].dropna().values
        n_vals = expr.loc[gene, n_cols].dropna().values
        if len(t_vals) < 3 or len(n_vals) < 3:
            continue
        fc = float(np.median(t_vals) - np.median(n_vals))
        _, p = safe_mwu(t_vals, n_vals)
        if np.isnan(p):
            result = "NS"
        elif p < 0.05 and fc > 0:
            result = "UP"
        elif p < 0.05 and fc < 0:
            result = "DOWN"
        else:
            result = "NS"

        pred = predicted.get(gene, "UNCERTAIN")
        if pred in ("FLAT", "UNCERTAIN"):
            verdict = "—"
        elif result == pred:
            verdict = "CONFIRMED ✓"
        elif result == "NS":
            verdict = "FLAT (ns)"
        else:
            verdict = f"WRONG ({result})"

        saddle_res[gene] = {
            "result":  result,
            "fc":      fc,
            "p":       p,
            "pred":    pred,
            "verdict": verdict,
        }
        rows.append({
            "Gene":    gene,
            "Pred":    pred,
            "FC":      round(fc, 3),
            "p":       p,
            "Result":  result,
            "Verdict": verdict,
        })

    df = pd.DataFrame(rows).sort_values("p")

    # --- Log by panel section -----------------------------------
    def log_section(genes, title):
        log(f"\n{'─'*60}")
        log(f"  {title}")
        log(f"{'─'*60}")
        hdr = f"  {'Gene':<12} {'Pred':<12} {'FC':>7} {'p':>12} {'Result':<8} {'Verdict'}"
        log(hdr)
        log(f"  {'─'*80}")
        for g in genes:
            if g not in saddle_res:
                log(f"  {g:<12} {'—':<12} {'n/a':>7} {'—':>12} {'—':<8} not in matrix")
                continue
            r = saddle_res[g]
            log(f"  {g:<12} {r['pred']:<12} "
                f"{r['fc']:>+7.3f} {fmt_p(r['p']):>12} "
                f"{r['result']:<8} {r['verdict']}")

    log_section(SW_GENES,        "SWITCH GENES (PT identity — predicted DOWN)")
    log_section(FA_GENES,        "FALSE ATTRACTOR MARKERS (predicted UP)")
    log_section(EPIGENETIC_GENES,"EPIGENETIC PANEL")
    log_section(TCA_GENES,       "TCA / METABOLIC PANEL")
    log_section(ECM_GENES,       "ECM / STROMA PANEL")
    log_section(IMMUNE_GENES,    "IMMUNE / TME PANEL")
    log_section(RTK_GENES,       "RTK / MET PATHWAY")
    log_section(HIF_GENES,       "HIF / VHL AXIS (structural contrast with ccRCC)")
    log_section(SCAFFOLD_GENES,  "SCAFFOLD / PROLIFERATION")

    # Score predictions
    n_confirmed = sum(
        1 for v in saddle_res.values()
        if v["verdict"] == "CONFIRMED ✓"
    )
    n_predicted = sum(
        1 for v in saddle_res.values()
        if v["pred"] not in ("UNCERTAIN", "FLAT")
    )
    log("")
    log(f"  SCORECARD: {n_confirmed}/{n_predicted} predictions confirmed")

    # Save CSV
    df.to_csv(
        os.path.join(RESULTS_DIR, "saddle_results.csv"),
        index=False)

    return saddle_res

# ═══════════════════════════════════════════════════════════════
# BUILD DEPTH SCORE
# ═══════════════════════════════════════════════════════════════

def build_depth_score(expr, meta, saddle_res, label):
    """
    Protocol-canonical depth score:
      C1 = 1 - norm(mean of confirmed SW genes)
      C2 = norm(mean of confirmed FA genes)
      depth = (C1 + C2) / 2
    Falls back to full predicted panel if <2 confirmed in either.
    Computes in tumour samples only.
    """
    log("")
    log("=" * 60)
    log(f"DEPTH SCORE — {label}")
    log("=" * 60)

    meta_idx = meta.set_index("sample_id").reindex(expr.columns)
    t_cols = expr.columns[(meta_idx.sample_type == "tumour").values]

    # Confirmed SW genes (DOWN and predicted DOWN)
    sw_confirmed = [
        g for g in SW_GENES
        if g in saddle_res
        and saddle_res[g]["result"] == "DOWN"
        and saddle_res[g]["pred"] == "DOWN"
    ]
    # Confirmed FA genes (UP and predicted UP)
    fa_confirmed = [
        g for g in FA_GENES
        if g in saddle_res
        and saddle_res[g]["result"] == "UP"
        and saddle_res[g]["pred"] == "UP"
    ]

    log(f"  SW confirmed ({len(sw_confirmed)}): {sw_confirmed}")
    log(f"  FA confirmed ({len(fa_confirmed)}): {fa_confirmed}")

    # Fallback to full panel if too few confirmed
    sw_use = sw_confirmed if len(sw_confirmed) >= 2 else \
        [g for g in SW_GENES
         if g in expr.index and g != "UMOD"]
    fa_use = fa_confirmed if len(fa_confirmed) >= 2 else \
        [g for g in FA_GENES if g in expr.index]

    log(f"  SW used  ({len(sw_use)}): {sw_use}")
    log(f"  FA used  ({len(fa_use)}): {fa_use}")

    t_expr = expr[t_cols]

    # C1: SW suppression
    sw_avail = [g for g in sw_use if g in t_expr.index]
    if sw_avail:
        sw_mean = t_expr.loc[sw_avail].mean(axis=0).values
        C1 = 1 - norm01(sw_mean)
    else:
        C1 = np.zeros(len(t_cols))
        log("  WARNING: no SW genes available — C1 = 0")

    # C2: FA elevation
    fa_avail = [g for g in fa_use if g in t_expr.index]
    if fa_avail:
        fa_mean = t_expr.loc[fa_avail].mean(axis=0).values
        C2 = norm01(fa_mean)
    else:
        C2 = np.zeros(len(t_cols))
        log("  WARNING: no FA genes available — C2 = 0")

    depth = (C1 + C2) / 2.0
    depth_s = pd.Series(depth, index=t_cols, name="depth")

    log(f"  Depth score (n={len(depth_s)} tumours):")
    log(f"    mean   = {depth_s.mean():.4f}")
    log(f"    median = {depth_s.median():.4f}")
    log(f"    std    = {depth_s.std():.4f}")
    log(f"    min    = {depth_s.min():.4f}")
    log(f"    max    = {depth_s.max():.4f}")
    log(f"    Q25    = {depth_s.quantile(0.25):.4f}")
    log(f"    Q75    = {depth_s.quantile(0.75):.4f}")

    return depth_s

# ═══════════════════════════════════════════════════════════════
# DEPTH CORRELATIONS — THE DISCOVERY
# ═══════════════════════════════════════════════════════════════

def depth_correlations(expr, depth, meta, label):
    """
    Pearson r for every panel gene vs depth score.
    Tumour samples only.
    Sorted by |r| descending.
    This is the primary discovery step.
    Read this before interpreting the saddle table.
    """
    log("")
    log("=" * 60)
    log(f"DEPTH CORRELATIONS — {label}")
    log("=" * 60)
    log("  Pearson r vs depth score, tumour samples only.")
    log("  Protocol Step 2.3: read this before the saddle table.")
    log("  The depth correlations are the discovery.")
    log("")

    meta_idx = meta.set_index("sample_id").reindex(expr.columns)
    t_cols = expr.columns[(meta_idx.sample_type == "tumour").values]

    # Align depth to t_cols
    d = depth.reindex(t_cols).dropna()

    rows = []
    for gene in expr.index:
        vals = pd.Series(
            expr.loc[gene, t_cols].values,
            index=t_cols
        ).reindex(d.index).dropna()
        if len(vals) < 10:
            continue
        r, p = safe_r(vals.values, d.reindex(vals.index).values)
        if np.isnan(r):
            continue

        # Panel membership label
        panel_label = "—"
        if gene in SW_GENES:      panel_label = "SW"
        elif gene in FA_GENES:    panel_label = "FA"
        elif gene in EPIGENETIC_GENES: panel_label = "EPI"
        elif gene in TCA_GENES:   panel_label = "TCA"
        elif gene in ECM_GENES:   panel_label = "ECM"
        elif gene in IMMUNE_GENES: panel_label = "IMM"
        elif gene in RTK_GENES:   panel_label = "RTK"
        elif gene in HIF_GENES:   panel_label = "HIF"
        elif gene in SCAFFOLD_GENES: panel_label = "SCAF"

        rows.append({
            "gene":  gene,
            "r":     r,
            "p":     p,
            "abs_r": abs(r),
            "panel": panel_label,
        })

    corr_df = pd.DataFrame(rows).sort_values(
        "abs_r", ascending=False
    ).reset_index(drop=True)

    # Log top 30
    log(f"  {'Rank':>5} {'Gene':<14} {'r':>8} {'p':>14} {'Panel'}")
    log(f"  {'─'*55}")
    for i, row in corr_df.head(30).iterrows():
        log(f"  {i+1:>5} {row['gene']:<14} "
            f"{row['r']:>+8.4f} {fmt_p(row['p']):>14} "
            f"{row['panel']}")

    log("")
    log("  TOP POSITIVES (FA candidates):")
    pos = corr_df[corr_df.r > 0].head(10)
    for _, row in pos.iterrows():
        log(f"    {row['gene']:<14} r={row['r']:+.4f}  {fmt_p(row['p'])}")

    log("")
    log("  TOP NEGATIVES (SW candidates):")
    neg = corr_df[corr_df.r < 0].sort_values("r").head(10)
    for _, row in neg.iterrows():
        log(f"    {row['gene']:<14} r={row['r']:+.4f}  {fmt_p(row['p'])}")

    corr_df.to_csv(
        os.path.join(RESULTS_DIR, f"depth_corr_{label.lower()}.csv"),
        index=False)

    return corr_df

# ═══════════════════════════════════════════════════════════════
# GAP TESTS
# ═══════════════════════════════════════════════════════════════

def gap_tests(expr, meta, label):
    """
    Test circuit connectivity.
    Near-zero r = circuit broken = the gap = intervention point.
    Positive r = connected.
    Negative r = anti-correlated = repressor relationship.
    """
    log("")
    log("=" * 60)
    log(f"GAP TESTS — {label}")
    log("=" * 60)
    log("  r near 0 = BROKEN circuit = therapeutic gap")
    log("")

    meta_idx = meta.set_index("sample_id").reindex(expr.columns)
    t_cols = expr.columns[(meta_idx.sample_type == "tumour").values]

    circuits = [
        # MET pathway → PT identity (predicted BROKEN)
        ("MET",    "SLC22A6",  "MET → OAT1 (PT identity)"),
        ("MET",    "CUBN",     "MET → CUBN (PT endocytic)"),
        ("MET",    "LRP2",     "MET → LRP2 (PT endocytic)"),
        ("MET",    "SLC13A2",  "MET → NaDC1 (PT citrate)"),
        ("MET",    "FABP1",    "MET → FABP1 (PT metabolic)"),

        # Epigenetic lock circuits
        ("SETD2",  "EZH2",     "SETD2 → EZH2 (H3K36/H3K27 opposition)"),
        ("EZH2",   "SLC13A2",  "EZH2 → SLC13A2 (epigenetic silencing)"),
        ("EZH2",   "FBP1",     "EZH2 → FBP1 (metabolic silencing)"),
        ("KDM1A",  "SLC13A2",  "KDM1A → SLC13A2 (LSD1 demethylase)"),

        # TCA / chromatin coupling (FH → αKG axis)
        ("FH",     "TET2",     "FH → TET2 (fumarate-αKG coupling)"),
        ("FH",     "EZH2",     "FH → EZH2 (FH loss → EZH2 gain)"),
        ("FH",     "OGDHL",    "FH → OGDHL (TCA integrity)"),
        ("OGDHL",  "EZH2",     "OGDHL → EZH2 (αKG production)"),
        ("SUCLG1", "EZH2",     "SUCLG1 → EZH2 (αKG axis)"),

        # VHL / HIF axis (structural contrast with ccRCC)
        ("VHL",    "EPAS1",    "VHL → HIF2A (should be BROKEN in PRCC)"),
        ("VHL",    "CA9",      "VHL → CA9 (HIF target — flat in PRCC?)"),
        ("EPAS1",  "SLC2A1",   "HIF2A → GLUT1 (weaker than ccRCC?)"),

        # EMT / stroma circuits
        ("TGFB1",  "ACTA2",    "TGFB1 → ACTA2 (stroma activation)"),
        ("LOXL2",  "COL1A1",   "LOXL2 → COL1A1 (ECM stiffening)"),
        ("VIM",    "CDH1",     "VIM → CDH1 (EMT — CDH1 lost?)"),

        # Immune circuit
        ("IFI16",  "B2M",      "IFI16 → B2M (innate sensing → MHC-I)"),
        ("FOXP3",  "CD274",    "FOXP3 → CD274 (Treg → PD-L1)"),
        ("IL2RA",  "FOXP3",    "IL2RA → FOXP3 (Treg circuit)"),

        # Type 1 specific
        ("MET",    "MKI67",    "MET → MKI67 (proliferative drive)"),
        ("MET",    "VEGFA",    "MET → VEGFA (angiogenic drive)"),
        ("MET",    "MTOR",     "MET → mTOR (signalling)"),
    ]

    gap_results = {}
    log(f"  {'Circuit':<45} {'r':>8} {'p':>12} {'Verdict'}")
    log(f"  {'─'*80}")

    for geneA, geneB, label_c in circuits:
        if geneA not in expr.index or geneB not in expr.index:
            log(f"  {label_c:<45} {'—':>8} {'—':>12} not in matrix")
            continue

        vA = pd.Series(expr.loc[geneA, t_cols].values, index=t_cols)
        vB = pd.Series(expr.loc[geneB, t_cols].values, index=t_cols)
        both = pd.DataFrame({"A": vA, "B": vB}).dropna()
        if len(both) < 10:
            continue

        r, p = safe_r(both.A.values, both.B.values)
        if np.isnan(r):
            continue

        if abs(r) < 0.15:
            verdict = "BROKEN ✓ (gap)"
        elif r < -0.15:
            verdict = f"ANTI-CORRELATED ({r:+.3f})"
        elif r > 0.40:
            verdict = f"CONNECTED ({r:+.3f})"
        elif r > 0.15:
            verdict = f"WEAK ({r:+.3f})"
        else:
            verdict = f"NS ({r:+.3f})"

        gap_results[f"{geneA}→{geneB}"] = {
            "r": r, "p": p, "verdict": verdict
        }
        log(f"  {label_c:<45} {r:>+8.4f} {fmt_p(p):>12} {verdict}")

    return gap_results

# ═══════════════════════════════════════════════════════════════
# SUBTYPE ANALYSIS
# ═══════════════════════════════════════════════════════════════

def subtype_analysis(expr, depth, meta, clin, subtype_col, label):
    """
    If subtype annotation available:
    - Depth score by Type 1 / Type 2 / CIMP
    - Mann-Whitney between subtypes
    - Key gene expression per subtype
    Tests S1-P1: Type 2 depth > Type 1 depth
    """
    log("")
    log("=" * 60)
    log(f"SUBTYPE ANALYSIS — {label}")
    log("=" * 60)

    if clin is None or subtype_col is None:
        log("  No subtype annotation — skipping.")
        return None

    meta_idx = meta.set_index("sample_id").reindex(expr.columns)
    t_cols = expr.columns[(meta_idx.sample_type == "tumour").values]
    d = depth.reindex(t_cols).dropna()

    # Map sample → subtype using first 12 chars of barcode
    short_ids = pd.Index([s[:12] for s in d.index])

    try:
        subtype_map = clin[subtype_col].dropna()
    except Exception as e:
        log(f"  Subtype mapping failed: {e}")
        return None

    subtypes = []
    for s in d.index:
        key = s[:12]
        st = subtype_map.get(key, "UNKNOWN")
        subtypes.append(str(st))

    subtype_s = pd.Series(subtypes, index=d.index)
    counts = subtype_s.value_counts()
    log(f"  Subtype counts:")
    for st, n in counts.items():
        log(f"    {st}: n={n}")

    # Depth by subtype
    log("")
    log(f"  {'Subtype':<30} {'n':>5} {'Mean depth':>12} {'Median':>10}")
    log(f"  {'─'*60}")
    subtype_depths = {}
    for st in counts.index:
        mask = subtype_s == st
        ds = d[mask]
        if len(ds) < 3:
            continue
        subtype_depths[st] = ds
        log(f"  {st:<30} {len(ds):>5} "
            f"{ds.mean():>12.4f} {ds.median():>10.4f}")

    # Test S1-P1: Type 2 > Type 1
    type1_key = None
    type2_key = None
    for k in subtype_depths.keys():
        kl = k.lower()
        if "type 1" in kl or "type1" in kl or "papillary type 1" in kl:
            type1_key = k
        if "type 2" in kl or "type2" in kl or "papillary type 2" in kl:
            type2_key = k

    if type1_key and type2_key:
        d1 = subtype_depths[type1_key]
        d2 = subtype_depths[type2_key]
        _, p12 = safe_mwu(d2.values, d1.values)
        direction = "Type2 > Type1" if d2.mean() > d1.mean() else "Type1 > Type2"
        log("")
        log(f"  S1-P1 TEST: Type 2 depth > Type 1 depth")
        log(f"    Type1 mean={d1.mean():.4f}  "
            f"Type2 mean={d2.mean():.4f}")
        log(f"    Direction: {direction}")
        log(f"    MW p = {fmt_p(p12)}")
        if p12 < 0.05 and d2.mean() > d1.mean():
            log(f"    S1-P1 CONFIRMED ✓")
        elif p12 < 0.05 and d2.mean() < d1.mean():
            log(f"    S1-P1 INVERTED — Type 1 deeper (ANALYST ASSUMPTION ERROR)")
        else:
            log(f"    S1-P1 NOT CONFIRMED (ns)")
    else:
        log(f"  S1-P1: Type 1/Type 2 keys not found in subtype column.")
        log(f"  Available subtypes: {list(subtype_depths.keys())}")

    # Key gene expression per subtype
    key_genes = [
        "MET", "SETD2", "EZH2", "FH", "PBRM1", "BAP1",
        "SLC13A2", "SLC22A6", "VIM", "CDKN2A", "HMOX1",
        "FBP1", "OGDHL", "TET2", "CA9", "EPAS1",
    ]
    avail = [g for g in key_genes if g in expr.index]

    if avail and len(subtype_depths) >= 2:
        log("")
        log(f"  KEY GENE EXPRESSION BY SUBTYPE")
        log(f"  {'Gene':<12}" +
            "".join(f"  {st[:10]:>12}" for st in subtype_depths.keys()))
        log(f"  {'─'*70}")
        for g in avail:
            g_expr = {}
            for st, ds in subtype_depths.items():
                vals = expr.loc[g, ds.index.intersection(
                    expr.columns)].dropna()
                g_expr[st] = f"{vals.mean():.2f}" if len(vals) else "—"
            log(f"  {g:<12}" +
                "".join(f"  {g_expr.get(st, '—'):>12}"
                        for st in subtype_depths.keys()))

    return subtype_depths

# ═══════════════════════════════════════════════════════════════
# DEPTH QUARTILE ANALYSIS
# ═══════════════════════════════════════════════════════════════

def depth_quartile_analysis(expr, depth, meta, label):
    """
    Divide tumours into Q1 (shallowest) and Q4 (deepest).
    Compare Q4/Q1 ratios for every panel gene.
    This reveals what genes define the deep attractor.
    """
    log("")
    log("=" * 60)
    log(f"DEPTH QUARTILE ANALYSIS — {label}")
    log("=" * 60)

    meta_idx = meta.set_index("sample_id").reindex(expr.columns)
    t_cols = expr.columns[(meta_idx.sample_type == "tumour").values]
    d = depth.reindex(t_cols).dropna()

    q25 = d.quantile(0.25)
    q75 = d.quantile(0.75)
    q4_idx = d[d >= q75].index
    q1_idx = d[d <= q25].index

    log(f"  Q1 (shallowest, depth ≤ {q25:.3f}): n={len(q1_idx)}")
    log(f"  Q4 (deepest,    depth ≥ {q75:.3f}): n={len(q4_idx)}")

    rows = []
    for gene in expr.index:
        q4_vals = expr.loc[gene, q4_idx.intersection(
            expr.columns)].dropna()
        q1_vals = expr.loc[gene, q1_idx.intersection(
            expr.columns)].dropna()
        if len(q4_vals) < 5 or len(q1_vals) < 5:
            continue
        ratio = q4_vals.mean() / (q1_vals.mean() + 1e-6)
        _, p = safe_mwu(q4_vals.values, q1_vals.values)
        rows.append({
            "gene":  gene,
            "Q4_mean": q4_vals.mean(),
            "Q1_mean": q1_vals.mean(),
            "Q4_Q1":   ratio,
            "p":       p,
        })

    qdf = pd.DataFrame(rows).sort_values("Q4_Q1", ascending=False)

    log("")
    log(f"  TOP 20 Q4-ENRICHED GENES:")
    log(f"  {'Gene':<14} {'Q4_mean':>10} {'Q1_mean':>10} "
        f"{'Q4/Q1':>8} {'p':>12}")
    log(f"  {'─'*60}")
    for _, row in qdf.head(20).iterrows():
        log(f"  {row['gene']:<14} {row['Q4_mean']:>10.3f} "
            f"{row['Q1_mean']:>10.3f} {row['Q4_Q1']:>8.3f} "
            f"{fmt_p(row['p']):>12}")

    log("")
    log(f"  TOP 10 Q1-ENRICHED GENES (SW candidates):")
    for _, row in qdf.tail(10).iloc[::-1].iterrows():
        log(f"  {row['gene']:<14} Q4/Q1={row['Q4_Q1']:.3f}  "
            f"{fmt_p(row['p'])}")

    qdf.to_csv(
        os.path.join(RESULTS_DIR,
                     f"quartile_analysis_{label.lower()}.csv"),
        index=False)

    return qdf

# ═══════════════════════════════════════════════════════════════
# FIGURE — 9 panel
# ═══════════════════════════════════════════════════════════════

def generate_figure(expr, depth, meta, saddle_res,
                    corr_df, subtype_depths, label):
    """
    9-panel figure:
    A: SW genes bar chart (tumour vs normal)
    B: FA markers bar chart
    C: Depth score distribution
    D: Top 20 depth correlations (|r|)
    E: Depth by subtype (if available)
    F: HIF axis comparison (PRCC vs ccRCC concept)
    G: Epigenetic genes tumour vs normal
    H: ECM/stroma panel
    I: Summary text
    """
    log("")
    log("=" * 60)
    log(f"GENERATING FIGURE — {label}")
    log("=" * 60)

    meta_idx = meta.set_index("sample_id").reindex(expr.columns)
    t_cols = expr.columns[(meta_idx.sample_type == "tumour").values]
    n_cols = expr.columns[(meta_idx.sample_type == "normal").values]

    fig = plt.figure(figsize=(22, 28))
    gs  = gridspec.GridSpec(3, 3, figure=fig,
                            hspace=0.5, wspace=0.4)

    pal = {"tumour": "#C0392B", "normal": "#2980B9"}

    def bar_panel(ax, genes, title):
        genes_av = [g for g in genes if g in expr.index]
        x = np.arange(len(genes_av))
        t_means = [expr.loc[g, t_cols].mean() for g in genes_av]
        n_means = [expr.loc[g, n_cols].mean() for g in genes_av]
        w = 0.35
        ax.bar(x - w/2, t_means, w,
               color=pal["tumour"], label="Tumour", alpha=0.85)
        ax.bar(x + w/2, n_means, w,
               color=pal["normal"], label="Normal", alpha=0.85)
        ax.set_xticks(x)
        ax.set_xticklabels(genes_av, rotation=45, ha="right",
                           fontsize=8)
        ax.set_title(title, fontsize=10, fontweight="bold")
        ax.legend(fontsize=7)
        ax.set_ylabel("log2 RSEM", fontsize=8)

    # Panel A: SW genes
    ax_A = fig.add_subplot(gs[0, 0])
    bar_panel(ax_A, SW_GENES, "A: Switch Genes (PT identity)")

    # Panel B: FA markers
    ax_B = fig.add_subplot(gs[0, 1])
    bar_panel(ax_B, FA_GENES[:8], "B: False Attractor Markers")

    # Panel C: Depth distribution
    ax_C = fig.add_subplot(gs[0, 2])
    d_vals = depth.values
    ax_C.hist(d_vals, bins=30, color="#8E44AD", alpha=0.8,
              edgecolor="white", linewidth=0.5)
    ax_C.axvline(np.median(d_vals), color="black",
                 linestyle="--", linewidth=1.5,
                 label=f"Median={np.median(d_vals):.3f}")
    ax_C.set_xlabel("Depth Score", fontsize=9)
    ax_C.set_ylabel("Count", fontsize=9)
    ax_C.set_title("C: Depth Score Distribution\n(PRCC tumours)",
                   fontsize=10, fontweight="bold")
    ax_C.legend(fontsize=8)

    # Panel D: Top 20 depth correlations
    ax_D = fig.add_subplot(gs[1, 0])
    top20 = corr_df.head(20)
    colors_d = [
        "#C0392B" if r > 0 else "#2980B9"
        for r in top20.r
    ]
    bars = ax_D.barh(
        range(len(top20)), top20.r.values,
        color=colors_d, alpha=0.85
    )
    ax_D.set_yticks(range(len(top20)))
    ax_D.set_yticklabels(top20.gene.values, fontsize=8)
    ax_D.invert_yaxis()
    ax_D.axvline(0, color="black", linewidth=0.8)
    ax_D.set_xlabel("Pearson r vs depth", fontsize=9)
    ax_D.set_title("D: Top 20 Depth Correlations\n(|r| ranked)",
                   fontsize=10, fontweight="bold")

    # Panel E: Depth by subtype
    ax_E = fig.add_subplot(gs[1, 1])
    if subtype_depths and len(subtype_depths) >= 2:
        st_names = list(subtype_depths.keys())
        box_data = [subtype_depths[st].values
                    for st in st_names]
        bp = ax_E.boxplot(box_data, patch_artist=True)
        cmap_sub = plt.cm.Set2(
            np.linspace(0, 1, len(st_names)))
        for patch, col in zip(bp["boxes"], cmap_sub):
            patch.set_facecolor(col)
        ax_E.set_xticklabels(
            [st[:15] for st in st_names],
            rotation=30, ha="right", fontsize=7)
        ax_E.set_ylabel("Depth Score", fontsize=9)
        ax_E.set_title("E: Depth by Subtype\n(S1-P1 test)",
                       fontsize=10, fontweight="bold")
    else:
        ax_E.text(0.5, 0.5, "No subtype\nannotation",
                  ha="center", va="center",
                  transform=ax_E.transAxes, fontsize=10)
        ax_E.set_title("E: Depth by Subtype",
                       fontsize=10, fontweight="bold")

    # Panel F: HIF axis — structural contrast with ccRCC
    ax_F = fig.add_subplot(gs[1, 2])
    hif_genes = [g for g in HIF_GENES if g in expr.index]
    bar_panel(ax_F, hif_genes,
              "F: HIF / VHL Axis\n(structural contrast with ccRCC)")

    # Panel G: Epigenetic panel
    ax_G = fig.add_subplot(gs[2, 0])
    bar_panel(ax_G, EPIGENETIC_GENES,
              "G: Epigenetic Panel\n(lock mechanism)")

    # Panel H: ECM / stroma
    ax_H = fig.add_subplot(gs[2, 1])
    bar_panel(ax_H, ECM_GENES,
              "H: ECM / Stroma Panel")

    # Panel I: Summary text
    ax_I = fig.add_subplot(gs[2, 2])
    ax_I.axis("off")

    n_confirmed = sum(
        1 for v in saddle_res.values()
        if v.get("verdict") == "CONFIRMED ✓"
    )
    n_predicted = sum(
        1 for v in saddle_res.values()
        if v.get("pred") not in ("UNCERTAIN", "FLAT", None)
    )
    top1 = corr_df.iloc[0] if len(corr_df) > 0 else None
    bot1 = corr_df.iloc[-1] if len(corr_df) > 0 else None

    summary_lines = [
        "PRCC FALSE ATTRACTOR — Script 1",
        "OrganismCore | 2026-03-02",
        "",
        f"Dataset: TCGA-KIRP HiSeqV2",
        f"Tumour n ≈ {len(depth)}",
        "",
        f"Predictions: {n_confirmed}/{n_predicted} confirmed",
        "",
        f"Top depth correlate (+): "
        f"{top1['gene'] if top1 is not None else '—'} "
        f"r={top1['r']:+.3f}" if top1 is not None else "",
        f"Top depth correlate (−): "
        f"{bot1['gene'] if bot1 is not None else '—'} "
        f"r={bot1['r']:+.3f}" if bot1 is not None else "",
        "",
        "KEY FINDING (read depth corr first):",
        "What is rank 1 positive?",
        "What is rank 1 negative?",
        "What was not predicted?",
        "That is the PRCC attractor.",
    ]
    ax_I.text(0.05, 0.95, "\n".join(summary_lines),
              transform=ax_I.transAxes,
              fontsize=8, va="top", family="monospace",
              bbox=dict(boxstyle="round", facecolor="#ECF0F1",
                        alpha=0.8))
    ax_I.set_title("I: Script 1 Summary",
                   fontsize=10, fontweight="bold")

    fig.suptitle(
        "PRCC False Attractor — Script 1\n"
        "OrganismCore | Document 95a | 2026-03-02",
        fontsize=13, fontweight="bold", y=0.98
    )

    fig_path = os.path.join(RESULTS_DIR, "prcc_s1_figure.png")
    fig.savefig(fig_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    log(f"  Figure saved: {fig_path}")

# ═══════════════════════════════════════════════════════════════
# DRUG TARGET DERIVATION
# ═══════════════════════════════════════════════════════════════

def derive_drug_targets(corr_df, gap_results, saddle_res):
    """
    State drug targets derived from geometry alone.
    No literature. Stated before literature check.
    Four targets minimum per protocol.
    """
    log("")
    log("=" * 60)
    log("DRUG TARGET DERIVATION — FROM GEOMETRY")
    log("=" * 60)
    log("  Stated before literature check. Locked 2026-03-02.")
    log("")

    # Pull top positives and negatives from depth correlations
    top_pos = corr_df[corr_df.r > 0].head(5)
    top_neg = corr_df[corr_df.r < 0].head(5)

    log("  Top depth-positive genes (FA — target for inhibition):")
    for _, row in top_pos.iterrows():
        log(f"    {row['gene']:<14} r={row['r']:+.4f}  "
            f"{fmt_p(row['p'])}")

    log("")
    log("  Top depth-negative genes (SW — target for restoration):")
    for _, row in top_neg.iterrows():
        log(f"    {row['gene']:<14} r={row['r']:+.4f}  "
            f"{fmt_p(row['p'])}")

    log("")
    log("  DERIVED DRUG TARGETS (geometry, no literature):")
    log("")
    log("  TARGET 1: MET INHIBITOR")
    log("    Basis: MET as predicted FA marker")
    log("    Depth-positive → higher MET = deeper attractor")
    log("    Mechanism: MET drives papillary progenitor state")
    log("    Drug: Cabozantinib, savolitinib, tepotinib")
    log("    Best for: Type 1 (MET-amplified)")
    log("")
    log("  TARGET 2: EZH2 INHIBITOR")
    log("    Basis: EZH2 epigenetic lock on PT identity")
    log("    EZH2 UP + SETD2 DOWN → uncontrolled H3K27me3")
    log("    Mechanism: Derepresses SW gene promoters")
    log("    Drug: Tazemetostat (FDA approved)")
    log("    Best for: Type 2 / SETD2-low")
    log("")
    log("  TARGET 3: αKG SUPPLEMENTATION + EZH2i (NOVEL COMBINATION)")
    log("    Basis: FH mutation → fumarate blocks αKG dioxygenases")
    log("    Same TCA-chromatin axis as deep ccRCC")
    log("    Mechanism: Restore TET/KDM function + block EZH2 writing")
    log("    Drug: DMKG (cell-permeable αKG) + tazemetostat")
    log("    Best for: CIMP/FH-mutant Type 2")
    log("    STATED BEFORE LITERATURE — locked 2026-03-02")
    log("")
    log("  TARGET 4: VEGFR/mTOR INHIBITOR")
    log("    Basis: VEGFA elevation, MET → mTOR connection")
    log("    Mechanism: Reduces proliferative drive")
    log("    Drug: Sunitinib, pazopanib, everolimus")
    log("    Both types — depth-unaware (current standard)")
    log("")
    log("  NOT PREDICTED:")
    log("  Belzutifan (HIF2A inhibitor) — structural prediction:")
    log("  EPAS1 (HIF2A) should be FLAT in PRCC (no VHL loss).")
    log("  This is a direct testable contrast with ccRCC.")
    log("  If EPAS1 is flat and CA9 is flat → belzutifan inactive.")
    log("  Read the saddle table to confirm or falsify.")

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    log("OrganismCore — PRCC False Attractor")
    log("Script 1 — Discovery Run")
    log("Document 95a | 2026-03-02")
    log("")
    log("PROTOCOL ORDER (canonical):")
    log("  1. saddle_analysis()")
    log("     → per-gene tumour vs normal")
    log("     → predictions vs actuals")
    log("  2. build_depth_score()")
    log("     → uses confirmed genes")
    log("     → fallback to full panel if <2")
    log("  3. depth_correlations()")
    log("     → Pearson r, every panel gene")
    log("     → READ THIS FIRST — THE DISCOVERY")
    log("  4. gap_tests()")
    log("     → circuit topology")
    log("     → BROKEN = intervention point")
    log("  5. subtype_analysis()")
    log("     → Type 1 vs Type 2 vs CIMP depth")
    log("     → tests S1-P1")
    log("  6. quartile_analysis()")
    log("     → Q4/Q1 gene ratios")
    log("  7. drug_targets()")
    log("     → stated before literature")
    log("")
    log("DISCOVERY PRINCIPLE:")
    log("  Panel is wide (70+ genes).")
    log("  Unexpected signals are the finding.")
    log("  Confirmations validate the framework.")
    log("  Surprises extend it.")
    log("")

    # Downloads
    ok_expr, ok_clin = download_all()

    # Parse expression
    expr, meta = parse_tcga()

    # Parse clinical (subtype annotation)
    clin_result = parse_clinical()
    if clin_result is not None:
        clin, subtype_col = clin_result
    else:
        clin, subtype_col = None, None

    # ── TCGA PRIMARY ARM ────────────────────────────────────────
    log("")
    log("═" * 60)
    log("PRIMARY — TCGA-KIRP")
    log("═" * 60)

    # Step 1: saddle analysis
    saddle_res = saddle_analysis(expr, meta, "TCGA-KIRP")

    # Step 2: depth score
    depth = build_depth_score(
        expr, meta, saddle_res, "TCGA-KIRP"
    )

    # Save depth scores
    pd.DataFrame({
        "sample_id":   depth.index,
        "depth_score": depth.values,
    }).to_csv(
        os.path.join(RESULTS_DIR, "depth_scores_tcga.csv"),
        index=False)

    # Step 3: depth correlations (THE DISCOVERY)
    log("")
    log("╔" + "═"*58 + "╗")
    log("║  DEPTH CORRELATIONS — READ THIS BEFORE SADDLE TABLE  ║")
    log("╚" + "═"*58 + "╝")
    corr_df = depth_correlations(expr, depth, meta, "TCGA-KIRP")

    # Step 4: gap tests
    gap_results = gap_tests(expr, meta, "TCGA-KIRP")

    # Step 5: subtype analysis
    subtype_depths = subtype_analysis(
        expr, depth, meta, clin, subtype_col, "TCGA-KIRP"
    )

    # Step 6: depth quartile analysis
    qdf = depth_quartile_analysis(
        expr, depth, meta, "TCGA-KIRP"
    )

    # Step 7: drug target derivation
    derive_drug_targets(corr_df, gap_results, saddle_res)

    # Figure
    generate_figure(
        expr, depth, meta, saddle_res,
        corr_df, subtype_depths, "TCGA-KIRP"
    )

    # ── COMPLETE ────────────────────────────────────────────────
    log("")
    log("=" * 60)
    log("SCRIPT 1 COMPLETE")
    log("=" * 60)
    log(f"  Outputs: {RESULTS_DIR}")
    for fname in sorted(os.listdir(RESULTS_DIR)):
        fpath = os.path.join(RESULTS_DIR, fname)
        log(f"    {fname:<55} "
            f"{os.path.getsize(fpath):>8} bytes")
    log("")
    log("  ┌─────────────────────────────────────────────────────┐")
    log("  │  READING ORDER FOR DOCUMENT 95a                     │")
    log("  │                                                     │")
    log("  │  1. Read depth_corr_tcga-kirp.csv                   │")
    log("  │     What is rank 1 positive? (primary FA gene)      │")
    log("  │     What is rank 1 negative? (primary SW gene)      │")
    log("  │     What genes were NOT in the panel? (discovery)   │")
    log("  │                                                     │")
    log("  │  2. Read saddle_results.csv                         │")
    log("  │     How many SW genes confirmed DOWN?               │")
    log("  │     How many FA genes confirmed UP?                 │")
    log("  │     Which predictions were WRONG? Read them.        │")
    log("  │     Wrong predictions reveal assumption errors.     │")
    log("  │                                                     │")
    log("  │  3. Read the gap test results                       │")
    log("  │     Which circuits are BROKEN?                      │")
    log("  │     The broken circuits = intervention points.      │")
    log("  │                                                     │")
    log("  │  4. Check subtype_analysis                          │")
    log("  │     Is Type 2 deeper than Type 1?                   │")
    log("  │     Is EPAS1 / CA9 flat? (belzutifan contrast)      │")
    log("  │                                                     │")
    log("  │  5. Write Document 95a before running Script 2      │")
    log("  └─────────────────────────────────────────────────────┘")

    write_log()


if __name__ == "__main__":
    main()
