"""
PRCC False Attractor — Script 2
SUB-AXES / CIRCUITS / SUBTYPE / PANEL / DRUG MAP

Framework: OrganismCore
Document 95b-pre | 2026-03-02
Author: Eric Robert Lawson

═══════════════════════════════════════════��═══════════════════
PREDICTIONS LOCKED — 2026-03-02 — BEFORE SCRIPT 2

S2-P1: r(ERBB2, KRT19) > 0.50 — identity, not proliferative
       r(ERBB2, MKI67) < 0.25

S2-P2: Two separable depth sub-axes
       Axis A: biliary identity (KRT19/KRT7 pole)
       Axis B: TCA metabolic collapse (FABP1/OGDHL pole)
       r(Axis_A, Axis_B) < 0.80

S2-P3: FH as continuous depth stratifier
       r(FH, depth) < -0.45
       FH-low quartile mean depth > FH-high quartile mean depth

S2-P4: PBRM1 loss releases biliary identity genes
       r(PBRM1, KRT19) < -0.20
       r(PBRM1, depth) < -0.20

S2-P5: Type 2 depth > Type 1 depth (S1-P1 deferred)
       MW p < 0.05 once annotation obtained

S2-P6: 3-gene panel r > 0.85
       Predicted panel: KRT19 / SLC22A6 / ERBB2
       or KRT19 / FABP1 / EZH2

S2-P7: Immune exclusion architecture in Q4
       r(depth, CD8A)  < -0.20
       r(depth, B2M)   < -0.15
       r(depth, IL2RA) > +0.20
       PD-L1 LOWER in Q4 than Q1

S2-P8: CA9 driven by HIF1A, not VHL
       r(CA9, HIF1A) > r(CA9, EPAS1)
       r(CA9, HIF1A) > 0.20

═══════════════════════════════════════════════════════════════
OBJECTIVES LOCKED BEFORE RUN:
  OBJ-1: Sub-axis separation (biliary vs TCA)
  OBJ-2: ERBB2 identity vs proliferative circuit
  OBJ-3: FH as continuous depth stratifier
  OBJ-4: PBRM1 → biliary identity circuit
  OBJ-5: Type 1 / Type 2 subtype annotation
          (cBioPortal fetch + MET-proxy fallback)
  OBJ-6: 3-gene clinical panel optimisation
  OBJ-7: Immune architecture confirmation
  OBJ-8: Drug target depth quartile map
  OBJ-9: S1/S2 depth concordance
  OBJ-10: TWIST1 within-tumour EMT axis
           separate from biliary axis?
  OBJ-11: CA9 mechanism — VHL vs HIF1A
  OBJ-12: Transition index (KRT19/SLC22A6 ratio)
           continuous attractor sensor
═══════════════════════════════════════════════════════════════

DATA:
  Loads S1 depth scores from results_s1/
  Reloads TCGA-KIRP expression matrix
  Attempts cBioPortal subtype annotation
  OUTPUT: ./prcc_false_attractor/results_s2/
"""

import os, gzip, itertools
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.stats import pearsonr, mannwhitneyu, spearmanr
import warnings
warnings.filterwarnings("ignore")

# ═══════════════════════════════════════════════════════════════
# PATHS
# ═══════════════════════════════════════════════════════════════

BASE_DIR    = "./prcc_false_attractor/"
S1_DIR      = os.path.join(BASE_DIR, "results_s1/")
RESULTS_DIR = os.path.join(BASE_DIR, "results_s2/")
LOG_FILE    = os.path.join(RESULTS_DIR, "s2_log.txt")

EXPR_PATH   = os.path.join(BASE_DIR, "TCGA_KIRP_HiSeqV2.gz")
CLIN_PATH   = os.path.join(BASE_DIR, "KIRP_clinicalMatrix.tsv")
CBIO_PATH   = os.path.join(BASE_DIR, "KIRP_cbio_clinical.tsv")
S1_DEPTH    = os.path.join(S1_DIR,   "depth_scores_tcga.csv")

os.makedirs(RESULTS_DIR, exist_ok=True)

# ═══════════════════════════════════════════════════════════════
# EXPANDED GENE PANEL — adds genes needed for OBJ-2 through 12
# ═══════════════════════════════════════════════════════════════

# Biliary identity axis (Axis A)
AXIS_A_POS = ["KRT19", "KRT7", "ERBB2", "ITGA3", "SOX4",
               "KRT8", "KRT18", "MET", "PROM1", "EPCAM"]
AXIS_A_NEG = ["SLC22A6", "SLC34A1", "CUBN", "LRP2",
               "SLC5A2", "SLC13A2"]

# TCA / metabolic collapse axis (Axis B)
AXIS_B_POS = ["EZH2", "KDM1A", "MKI67", "TOP2A"]
AXIS_B_NEG = ["FABP1", "OGDHL", "SUCLG1", "GOT1",
               "ACADM", "CPT1A", "ATP5A1", "LDHB", "FH"]

# EMT axis (TWIST1 check — OBJ-10)
EMT_GENES = ["TWIST1", "ZEB1", "ZEB2", "SNAI1", "SNAI2",
             "VIM", "CDH1", "CDH2", "FN1", "ACTA2"]

# ERBB2 circuit (OBJ-2)
ERBB2_CIRCUIT = ["ERBB2", "ERBB3", "EGFR", "MET", "KRT19",
                 "KRT7", "MKI67", "TOP2A", "CDK4", "CCND1"]

# FH / TCA-chromatin circuit (OBJ-3)
FH_CIRCUIT = ["FH", "OGDHL", "SUCLG1", "GOT1", "TET2",
              "EZH2", "SETD2", "DNMT3A", "HDAC1", "KDM1A",
              "SLC13A2", "FABP1"]

# PBRM1 / chromatin circuit (OBJ-4)
PBRM1_CIRCUIT = ["PBRM1", "BAP1", "ARID1A", "SMARCA4",
                 "SMARCB1", "KRT19", "KRT7", "SLC22A6",
                 "EZH2", "SETD2"]

# Immune panel (OBJ-7)
IMMUNE_PANEL = ["CD274", "PDCD1", "HAVCR2", "TIGIT",
                "CD8A", "CD8B", "FOXP3", "IL2RA", "B2M",
                "HLA-A", "TAP1", "IFI16", "IFNG",
                "CD4", "CD68", "ARG1"]

# Drug targets (OBJ-8)
DRUG_TARGETS = {
    "EZH2_inhibitor":     ["EZH2", "SUZ12", "EED"],
    "MET_inhibitor":      ["MET", "HGF", "CBLB"],
    "ERBB2_targeted":     ["ERBB2", "ERBB3"],
    "CDK46_inhibitor":    ["CDK4", "CDK6", "CCND1", "CDKN2A"],
    "KDM1A_inhibitor":    ["KDM1A", "RCOR1"],
    "aKG_combination":    ["FH", "OGDHL", "SUCLG1", "TET2"],
    "NOT_belzutifan":     ["EPAS1", "VHL", "CA9"],
}

# HIF / CA9 circuit (OBJ-11)
HIF_CIRCUIT = ["CA9", "EPAS1", "HIF1A", "VHL",
               "LDHA", "SLC2A1", "VEGFA", "PDK1"]

# Panel candidates (OBJ-6) — top 20 from S1 depth correlations
PANEL_POS = ["KRT19", "KRT7", "ERBB2", "ITGA3", "SOX4",
             "AXL", "KDM1A", "MET", "PROM1", "CD44",
             "EZH2", "CA9", "MKI67", "VIM", "TWIST1"]
PANEL_NEG = ["SLC22A6", "FABP1", "SLC5A2", "SLC34A1",
             "CUBN", "GPX3", "GOT1", "SUCLG1", "LDHB",
             "SLC16A1", "ACADM", "FH", "SLC13A2", "LRP2",
             "ATP5A1"]

# Full panel for expression reload
ALL_PANEL = list(dict.fromkeys(
    AXIS_A_POS + AXIS_A_NEG +
    AXIS_B_POS + AXIS_B_NEG +
    EMT_GENES + ERBB2_CIRCUIT + FH_CIRCUIT +
    PBRM1_CIRCUIT + IMMUNE_PANEL +
    HIF_CIRCUIT + PANEL_POS + PANEL_NEG +
    ["CDKN2A", "CDKN1A", "CCND1", "TOP2A",
     "LOXL2", "TGFB1", "TGFBI", "CAV1",
     "IL1RAP", "IL2RA", "HAVCR2", "IFI16",
     "UMOD", "MIOX", "GPX3", "FBP1",
     "DNMT3A", "ASXL1", "PBRM1", "BAP1",
     "HMOX1", "CD44", "MTOR", "RPTOR",
     "AXL", "LDHD", "ACAT1", "SLC16A1",
     "ERBB2", "ERBB3", "KRT8", "KRT18"]
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

def fmt_p(p):
    if p is None or np.isnan(p): return "—"
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
    if mask.sum() < 5: return np.nan, np.nan
    return pearsonr(x[mask], y[mask])

def safe_mwu(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    a = a[np.isfinite(a)]; b = b[np.isfinite(b)]
    if len(a) < 3 or len(b) < 3: return np.nan, np.nan
    return mannwhitneyu(a, b, alternative="two-sided")

# ═══════════════════════════════════════════════════════════════
# LOAD S1 OUTPUTS
# ═══════════════════════════════════════════════════════════════

def load_s1_depth():
    log("")
    log("=" * 60)
    log("LOADING SCRIPT 1 OUTPUTS")
    log("=" * 60)

    if not os.path.exists(S1_DEPTH):
        log(f"  ERROR: S1 depth not found: {S1_DEPTH}")
        log("  Run prcc_false_attractor_v1.py first.")
        return None

    df = pd.read_csv(S1_DEPTH)
    depth = pd.Series(
        df["depth_score"].values,
        index=df["sample_id"].values,
        name="s1_depth"
    )
    log(f"  S1 depth loaded: n={len(depth)}")
    log(f"    mean={depth.mean():.4f}  "
        f"std={depth.std():.4f}  "
        f"range=[{depth.min():.4f}, {depth.max():.4f}]")
    return depth

# ═══════════════════════════════════════════════════════════════
# RELOAD TCGA-KIRP EXPRESSION
# ═══════════════════════════════════════════════════════════════

def load_expression():
    log("")
    log("=" * 60)
    log("RELOAD TCGA-KIRP EXPRESSION")
    log("=" * 60)

    open_fn = gzip.open if EXPR_PATH.endswith(".gz") else open
    with open_fn(EXPR_PATH, "rt") as fh:
        raw = pd.read_csv(fh, sep="\t", index_col=0)

    avail   = [g for g in ALL_PANEL if g in raw.index]
    missing = [g for g in ALL_PANEL if g not in raw.index]
    expr    = raw.loc[avail].copy()

    log(f"  Genes available: {len(avail)}/{len(ALL_PANEL)}")
    if missing:
        log(f"  Missing: {missing}")

    sample_ids   = list(expr.columns)
    sample_type  = []
    for s in sample_ids:
        parts = s.split("-")
        code  = parts[3][:2] if len(parts) >= 4 else "00"
        if   code == "01": sample_type.append("tumour")
        elif code == "11": sample_type.append("normal")
        else:              sample_type.append("other")

    meta = pd.DataFrame({
        "sample_id":   sample_ids,
        "sample_type": sample_type,
    })
    meta_idx = meta.set_index("sample_id").reindex(expr.columns)
    t_cols   = expr.columns[(meta_idx.sample_type == "tumour").values]
    n_cols   = expr.columns[(meta_idx.sample_type == "normal").values]

    log(f"  Tumour: n={len(t_cols)}  Normal: n={len(n_cols)}")
    return expr, meta, t_cols, n_cols

# ═══════════════════════════════════════════════════════════════
# FETCH cBioPortal SUBTYPE ANNOTATION
# ═══════════════════════════════════════════════════════════════

def fetch_subtype_annotation():
    """
    Attempt cBioPortal REST API for KIRP subtype.
    Study IDs to try: kirp_tcga_pan_can_atlas_2018, kirp_tcga
    Field: paper_Histologic.type or similar.
    Falls back gracefully if unavailable.
    """
    log("")
    log("=" * 60)
    log("OBJ-5 — FETCH SUBTYPE ANNOTATION")
    log("=" * 60)

    if os.path.exists(CBIO_PATH) and \
            os.path.getsize(CBIO_PATH) > 500:
        log(f"  Cached: {CBIO_PATH}")
        try:
            df = pd.read_csv(CBIO_PATH, sep="\t",
                             low_memory=False)
            log(f"  Loaded: {df.shape[0]} rows, "
                f"{df.shape[1]} cols")
            log(f"  Cols: {list(df.columns[:15])}")
            return df
        except Exception as e:
            log(f"  Cache read failed: {e}")

    try:
        import requests
    except ImportError:
        log("  requests not available — subtype deferred.")
        return None

    CBIO  = "https://www.cbioportal.org/api"
    STUDY_IDS = [
        "kirp_tcga_pan_can_atlas_2018",
        "kirp_tcga",
    ]

    for study_id in STUDY_IDS:
        log(f"  Trying cBioPortal study: {study_id}")
        url_s = (f"{CBIO}/studies/{study_id}"
                 f"/clinical-data?clinicalDataType=SAMPLE"
                 f"&pageSize=10000")
        url_p = (f"{CBIO}/studies/{study_id}"
                 f"/clinical-data?clinicalDataType=PATIENT"
                 f"&pageSize=10000")

        for url_label, url in [
            ("SAMPLE", url_s),
            ("PATIENT", url_p),
        ]:
            try:
                r = requests.get(
                    url, timeout=60,
                    headers={
                        "Accept":     "application/json",
                        "User-Agent": "OrganismCore/1.0",
                    }
                )
                if r.status_code == 200:
                    data = r.json()
                    log(f"  {url_label}: "
                        f"n={len(data)} records")
                    if not data:
                        continue

                    # Pivot: rows = sample, cols = clinicalAttributeId
                    rows_wide = {}
                    for rec in data:
                        sid = rec.get("sampleId") or \
                              rec.get("patientId", "")
                        key = rec.get("clinicalAttributeId", "")
                        val = rec.get("value", "")
                        if sid not in rows_wide:
                            rows_wide[sid] = {}
                        rows_wide[sid][key] = val

                    df = pd.DataFrame(rows_wide).T.reset_index()
                    df.rename(columns={"index": "SAMPLE_ID"},
                              inplace=True)

                    # Show relevant columns
                    hist_cols = [c for c in df.columns
                                 if any(kw in c.upper()
                                        for kw in
                                        ["HIST", "TYPE", "SUBTYPE",
                                         "PAPER", "MORPHOLOGY"])]
                    log(f"  Subtype-related cols: {hist_cols}")

                    df.to_csv(CBIO_PATH, sep="\t", index=False)
                    log(f"  Saved: {CBIO_PATH}")
                    return df
                else:
                    log(f"  HTTP {r.status_code} — {url_label}")
            except Exception as e:
                log(f"  {url_label} fetch failed: {e}")

    log("  cBioPortal fetch failed — "
        "using MET-proxy stratification.")
    return None

def extract_subtype(cbio_df, t_cols):
    """
    From cBioPortal dataframe extract type1/type2.
    Returns Series indexed by sample barcode.
    """
    if cbio_df is None:
        return None

    # Look for histologic type column
    hist_col = None
    for c in cbio_df.columns:
        if any(kw in c.upper()
               for kw in ["HIST", "MORPHOLOGY",
                           "PAPER_HISTOLOGIC"]):
            hist_col = c
            break

    if hist_col is None:
        log("  No histologic type column found in cBioPortal data.")
        log(f"  Available: {list(cbio_df.columns)}")
        return None

    log(f"  Using column: {hist_col}")
    vc = cbio_df[hist_col].value_counts()
    log(f"  Values:\n{vc.to_string()}")

    # Build map: sample_id_12char → subtype string
    if "SAMPLE_ID" in cbio_df.columns:
        id_col = "SAMPLE_ID"
    else:
        id_col = cbio_df.columns[0]

    sub_map = dict(zip(
        cbio_df[id_col].str[:12],
        cbio_df[hist_col]
    ))

    subtypes = pd.Series(
        {s: sub_map.get(s[:12], "UNKNOWN")
         for s in t_cols},
        name="subtype"
    )
    return subtypes

# ═══════════════════════════════════════════════════════════════
# OBJ-1: SUB-AXIS SEPARATION
# ═══════════════════════════════════════════════════════════════

def obj1_subaxis_separation(expr, depth, t_cols):
    log("")
    log("=" * 60)
    log("OBJ-1 — SUB-AXIS SEPARATION")
    log("=" * 60)
    log("  Axis A: biliary identity (KRT19/SLC22A6 poles)")
    log("  Axis B: TCA metabolic collapse (FABP1/EZH2 poles)")
    log("  S2-P2: r(Axis_A, Axis_B) < 0.80")
    log("")

    d = depth.reindex(t_cols).dropna()

    def build_axis(pos_genes, neg_genes, name):
        pos_av = [g for g in pos_genes if g in expr.index]
        neg_av = [g for g in neg_genes if g in expr.index]
        if not pos_av and not neg_av:
            log(f"  {name}: no genes available")
            return None
        parts = []
        if pos_av:
            pm = expr.loc[pos_av, t_cols].mean(axis=0)
            parts.append(norm01(pm.reindex(d.index).values))
        if neg_av:
            nm = expr.loc[neg_av, t_cols].mean(axis=0)
            parts.append(1 - norm01(nm.reindex(d.index).values))
        score = np.nanmean(parts, axis=0)
        score_s = pd.Series(score, index=d.index)
        r, p = safe_r(score_s.values, d.values)
        log(f"  {name}")
        log(f"    pos genes: {pos_av}")
        log(f"    neg genes: {neg_av}")
        log(f"    r vs S1_depth = {r:+.4f}  {fmt_p(p)}")
        return score_s

    score_a = build_axis(AXIS_A_POS, AXIS_A_NEG, "Axis A (biliary identity)")
    score_b = build_axis(AXIS_B_NEG, AXIS_B_POS, "Axis B (TCA metabolic)")
    # Note: AXIS_B_NEG are the "down" genes — they define the
    # negative pole. We flip so score rises with depth.

    if score_a is None or score_b is None:
        log("  Cannot test sub-axis separation.")
        return score_a, score_b, np.nan

    r_ab, p_ab = safe_r(score_a.values, score_b.values)
    log("")
    log(f"  r(Axis_A, Axis_B) = {r_ab:+.4f}  {fmt_p(p_ab)}")
    if r_ab < 0.80:
        log(f"  S2-P2 CONFIRMED: axes separable ✓  (r < 0.80)")
    else:
        log(f"  S2-P2 NOT CONFIRMED: r >= 0.80 — axes not separable ✗")

    # Cross-axis correlations — what genes bridge A and B?
    log("")
    log("  CROSS-AXIS BRIDGING GENES (r with both axes):")
    log(f"  {'Gene':<14} {'r_AxisA':>9} {'r_AxisB':>9} {'bridge':>8}")
    log(f"  {'─'*44}")
    bridge_rows = []
    for gene in expr.index:
        v = pd.Series(expr.loc[gene, t_cols].values,
                      index=t_cols).reindex(d.index).dropna()
        if len(v) < 10:
            continue
        ra, _ = safe_r(v.values,
                       score_a.reindex(v.index).values)
        rb, _ = safe_r(v.values,
                       score_b.reindex(v.index).values)
        if np.isnan(ra) or np.isnan(rb):
            continue
        bridge = min(abs(ra), abs(rb))
        bridge_rows.append((gene, ra, rb, bridge))

    bridge_rows.sort(key=lambda x: -x[3])
    for gene, ra, rb, br in bridge_rows[:15]:
        log(f"  {gene:<14} {ra:>+9.4f} {rb:>+9.4f} {br:>8.4f}")

    return score_a, score_b, r_ab

# ═══════════════════════════════════════════════════════════════
# OBJ-2: ERBB2 IDENTITY VS PROLIFERATIVE CIRCUIT
# ═══════════════════════════════════════════════════════════════

def obj2_erbb2_circuit(expr, depth, t_cols):
    log("")
    log("=" * 60)
    log("OBJ-2 — ERBB2 IDENTITY vs PROLIFERATIVE CIRCUIT")
    log("=" * 60)
    log("  S2-P1: r(ERBB2, KRT19) > 0.50 — identity")
    log("         r(ERBB2, MKI67) < 0.25 — not proliferative")
    log("")

    d = depth.reindex(t_cols).dropna()

    def cr(gA, gB):
        if gA not in expr.index or gB not in expr.index:
            return np.nan, np.nan
        vA = pd.Series(expr.loc[gA, t_cols].values,
                       index=t_cols).reindex(d.index)
        vB = pd.Series(expr.loc[gB, t_cols].values,
                       index=t_cols).reindex(d.index)
        both = pd.DataFrame({"A": vA, "B": vB}).dropna()
        return safe_r(both.A.values, both.B.values)

    log(f"  {'Circuit':<30} {'r':>8} {'p':>12} {'Verdict'}")
    log(f"  {'─'*65}")

    results = {}
    tests = [
        ("ERBB2", "KRT19",  "ERBB2 → KRT19 (identity co-expr)"),
        ("ERBB2", "KRT7",   "ERBB2 → KRT7  (biliary identity)"),
        ("ERBB2", "KRT8",   "ERBB2 → KRT8  (simple epithelial)"),
        ("ERBB2", "KRT18",  "ERBB2 → KRT18 (simple epithelial)"),
        ("ERBB2", "MKI67",  "ERBB2 → MKI67 (proliferation)"),
        ("ERBB2", "TOP2A",  "ERBB2 → TOP2A (replication)"),
        ("ERBB2", "CDK4",   "ERBB2 → CDK4  (cell cycle)"),
        ("ERBB2", "MET",    "ERBB2 → MET   (RTK co-activation)"),
        ("ERBB2", "EPCAM",  "ERBB2 → EPCAM (epithelial identity)"),
        ("ERBB2", "SOX4",   "ERBB2 → SOX4  (progenitor TF)"),
        ("ERBB2", "EZH2",   "ERBB2 → EZH2  (chromatin lock)"),
        ("ERBB2", "SLC22A6","ERBB2 → OAT1  (PT identity lost)"),
    ]
    for gA, gB, label in tests:
        r, p = cr(gA, gB)
        if np.isnan(r):
            log(f"  {label:<30} {'—':>8} {'—':>12} not in matrix")
            continue
        verdict = (
            "IDENTITY ✓" if gA == "ERBB2" and gB in
            ("KRT19", "KRT7", "KRT8", "KRT18", "EPCAM", "SOX4")
            and abs(r) > 0.30 else
            "PROLIF ✓" if gA == "ERBB2" and gB in
            ("MKI67", "TOP2A", "CDK4") and abs(r) > 0.30 else
            "CONNECTED" if abs(r) > 0.30 else
            "WEAK"
        )
        results[f"{gA}→{gB}"] = {"r": r, "p": p}
        log(f"  {label:<30} {r:>+8.4f} {fmt_p(p):>12} {verdict}")

    # S2-P1 formal test
    log("")
    r_krt19 = results.get("ERBB2→KRT19", {}).get("r", np.nan)
    r_mki67 = results.get("ERBB2→MKI67", {}).get("r", np.nan)
    log(f"  S2-P1 FORMAL TEST:")
    log(f"    r(ERBB2, KRT19) = {r_krt19:+.4f}  "
        f"(pred > 0.50) → "
        f"{'CONFIRMED ✓' if r_krt19 > 0.50 else 'NOT CONFIRMED ✗'}")
    log(f"    r(ERBB2, MKI67) = {r_mki67:+.4f}  "
        f"(pred < 0.25) → "
        f"{'CONFIRMED ✓' if r_mki67 < 0.25 else 'NOT CONFIRMED ✗'}")

    return results

# ═══════════════════════════════════════════════════════════════
# OBJ-3: FH AS CONTINUOUS DEPTH STRATIFIER
# ═══════════════════════════════════════════════════════════════

def obj3_fh_stratifier(expr, depth, t_cols):
    log("")
    log("=" * 60)
    log("OBJ-3 — FH AS CONTINUOUS DEPTH STRATIFIER")
    log("=" * 60)
    log("  S2-P3: r(FH, depth) < -0.45")
    log("         FH-low quartile deeper than FH-high")
    log("")

    d = depth.reindex(t_cols).dropna()

    if "FH" not in expr.index:
        log("  FH not in expression matrix.")
        return

    fh_vals = pd.Series(
        expr.loc["FH", t_cols].values,
        index=t_cols
    ).reindex(d.index).dropna()

    r_fh, p_fh = safe_r(fh_vals.values, d.reindex(fh_vals.index).values)
    log(f"  r(FH, S1_depth) = {r_fh:+.4f}  {fmt_p(p_fh)}")
    log(f"  S2-P3 test: pred r < -0.45 → "
        f"{'CONFIRMED ✓' if r_fh < -0.45 else 'NOT CONFIRMED ✗'}")

    # FH quartile depth comparison
    q25_fh = fh_vals.quantile(0.25)
    q75_fh = fh_vals.quantile(0.75)
    fh_lo  = fh_vals[fh_vals <= q25_fh].index
    fh_hi  = fh_vals[fh_vals >= q75_fh].index

    d_lo = d.reindex(fh_lo).dropna()
    d_hi = d.reindex(fh_hi).dropna()

    _, p_mw = safe_mwu(d_lo.values, d_hi.values)
    direction = "FH-low DEEPER" if d_lo.mean() > d_hi.mean() \
        else "FH-high DEEPER"

    log(f"  FH-low  quartile: n={len(d_lo)}  "
        f"mean depth={d_lo.mean():.4f}")
    log(f"  FH-high quartile: n={len(d_hi)}  "
        f"mean depth={d_hi.mean():.4f}")
    log(f"  Direction: {direction}")
    log(f"  MW p = {fmt_p(p_mw)}")

    # FH circuit correlations
    log("")
    log("  FH CIRCUIT CORRELATIONS (TCA-chromatin axis):")
    log(f"  {'Gene':<14} {'r_vs_FH':>9} {'p':>12}")
    log(f"  {'─'*38}")
    for gene in FH_CIRCUIT:
        if gene == "FH" or gene not in expr.index:
            continue
        v = pd.Series(expr.loc[gene, t_cols].values,
                      index=t_cols).reindex(fh_vals.index).dropna()
        r, p = safe_r(fh_vals.reindex(v.index).values, v.values)
        if not np.isnan(r):
            log(f"  {gene:<14} {r:>+9.4f} {fmt_p(p):>12}")

    return r_fh, d_lo.mean(), d_hi.mean(), p_mw

# ═══════════════════════════════════════════════════════════════
# OBJ-4: PBRM1 → BILIARY IDENTITY CIRCUIT
# ═══════════════════════════════════════════════════════════════

def obj4_pbrm1_circuit(expr, depth, t_cols):
    log("")
    log("=" * 60)
    log("OBJ-4 — PBRM1 → BILIARY IDENTITY CIRCUIT")
    log("=" * 60)
    log("  S2-P4: r(PBRM1, KRT19) < -0.20")
    log("         r(PBRM1, depth) < -0.20")
    log("  PBRM1 loss releases biliary identity genes?")
    log("")

    d = depth.reindex(t_cols).dropna()

    if "PBRM1" not in expr.index:
        log("  PBRM1 not in matrix.")
        return

    pbrm1 = pd.Series(
        expr.loc["PBRM1", t_cols].values,
        index=t_cols
    ).reindex(d.index).dropna()

    r_d, p_d = safe_r(pbrm1.values, d.reindex(pbrm1.index).values)
    log(f"  r(PBRM1, depth) = {r_d:+.4f}  {fmt_p(p_d)}")
    log(f"  S2-P4 depth test: pred < -0.20 → "
        f"{'CONFIRMED ✓' if r_d < -0.20 else 'NOT CONFIRMED ✗'}")

    targets = [
        ("KRT19",   "biliary cytokeratin"),
        ("KRT7",    "biliary cytokeratin"),
        ("SLC22A6", "PT identity — expected POSITIVE"),
        ("SLC34A1", "PT identity — expected POSITIVE"),
        ("EZH2",    "chromatin lock — expected NEGATIVE"),
        ("SETD2",   "H3K36me3 writer"),
        ("BAP1",    "deubiquitinase partner"),
        ("ARID1A",  "SWI/SNF subunit"),
        ("SMARCA4", "SWI/SNF ATPase"),
        ("FABP1",   "PT metabolic"),
    ]

    log("")
    log(f"  {'Gene':<14} {'r vs PBRM1':>12} {'p':>12} {'note'}")
    log(f"  {'─'*60}")
    for gene, note in targets:
        if gene not in expr.index:
            log(f"  {gene:<14} {'—':>12} {'—':>12} not in matrix")
            continue
        v = pd.Series(expr.loc[gene, t_cols].values,
                      index=t_cols).reindex(pbrm1.index).dropna()
        r, p = safe_r(pbrm1.reindex(v.index).values, v.values)
        verdict = ""
        if gene in ("KRT19", "KRT7") and r < -0.20:
            verdict = "CONFIRMED ✓"
        elif gene in ("KRT19", "KRT7") and r >= -0.20:
            verdict = "NOT CONFIRMED ✗"
        log(f"  {gene:<14} {r:>+12.4f} {fmt_p(p):>12} "
            f"{note}  {verdict}")

# ═══════════════════════════════════════════════════════════════
# OBJ-5: SUBTYPE DEPTH STRATIFICATION
# ═══════════════════════════════════════════════════════════════

def obj5_subtype_depth(expr, depth, t_cols,
                        subtypes):
    log("")
    log("=" * 60)
    log("OBJ-5 — SUBTYPE DEPTH STRATIFICATION")
    log("=" * 60)
    log("  S2-P5: Type 2 depth > Type 1 depth  MW p < 0.05")
    log("")

    d = depth.reindex(t_cols).dropna()

    # ── Formal subtype test ──────────────────────────────────
    if subtypes is not None:
        sub_aligned = subtypes.reindex(d.index).fillna("UNKNOWN")
        counts = sub_aligned.value_counts()
        log("  Subtype counts (annotated):")
        for st, n in counts.items():
            log(f"    {st}: n={n}")

        # Find type 1 and type 2 keys
        t1_mask = sub_aligned.str.lower().str.contains(
            "type.?1|type 1|papillary.*1|1.*papillary",
            regex=True, na=False)
        t2_mask = sub_aligned.str.lower().str.contains(
            "type.?2|type 2|papillary.*2|2.*papillary",
            regex=True, na=False)

        d1 = d[t1_mask]
        d2 = d[t2_mask]

        log(f"\n  Type 1: n={len(d1)}  mean={d1.mean():.4f}  "
            f"median={d1.median():.4f}"
            if len(d1) > 0 else "\n  Type 1: n=0 — not found")
        log(f"  Type 2: n={len(d2)}  mean={d2.mean():.4f}  "
            f"median={d2.median():.4f}"
            if len(d2) > 0 else "  Type 2: n=0 — not found")

        if len(d1) >= 5 and len(d2) >= 5:
            _, p12 = safe_mwu(d2.values, d1.values)
            direction = "Type2 > Type1" if d2.mean() > d1.mean() \
                else "Type1 > Type2"
            log(f"\n  S2-P5 FORMAL TEST: {direction}")
            log(f"  MW p = {fmt_p(p12)}")
            if p12 < 0.05 and d2.mean() > d1.mean():
                log("  S2-P5 CONFIRMED ✓")
            elif p12 < 0.05:
                log("  S2-P5 INVERTED ✗ — Type 1 deeper")
            else:
                log("  S2-P5 NOT CONFIRMED (ns)")
        else:
            log("  Insufficient labelled samples for formal test.")
            log("  Proceeding to MET-proxy stratification.")

    # ── MET-proxy stratification ─────────────────────────────
    log("")
    log("  MET-PROXY STRATIFICATION:")
    log("  (Type 1 proxy: MET-high | Type 2 proxy: FH-low)")

    if "MET" in expr.index and "FH" in expr.index:
        met_vals = pd.Series(
            expr.loc["MET", t_cols].values,
            index=t_cols).reindex(d.index).dropna()
        fh_vals  = pd.Series(
            expr.loc["FH", t_cols].values,
            index=t_cols).reindex(d.index).dropna()

        # MET-high = top 33% = Type 1 proxy
        q67_met = met_vals.quantile(0.67)
        q33_fh  = fh_vals.quantile(0.33)
        met_hi  = met_vals[met_vals >= q67_met].index
        fh_lo   = fh_vals[fh_vals  <= q33_fh ].index

        d_met_hi = d.reindex(met_hi).dropna()
        d_fh_lo  = d.reindex(fh_lo).dropna()

        log(f"  MET-high (Type 1 proxy): n={len(d_met_hi)}  "
            f"mean={d_met_hi.mean():.4f}")
        log(f"  FH-low   (Type 2 proxy): n={len(d_fh_lo)}   "
            f"mean={d_fh_lo.mean():.4f}")
        _, p_proxy = safe_mwu(d_fh_lo.values, d_met_hi.values)
        direction = "FH-low DEEPER" if d_fh_lo.mean() > d_met_hi.mean() \
            else "MET-high DEEPER"
        log(f"  Direction: {direction}  MW p = {fmt_p(p_proxy)}")

        # Gene expression per proxy subtype
        key_genes = ["MET", "KRT19", "ERBB2", "EZH2",
                     "SETD2", "FH", "OGDHL", "SLC22A6",
                     "CDKN2A", "PBRM1", "BAP1", "VIM"]
        avail = [g for g in key_genes if g in expr.index]
        log("")
        log(f"  KEY GENE EXPRESSION — PROXY SUBTYPES:")
        log(f"  {'Gene':<14} {'MET-hi (T1)':>14} "
            f"{'FH-low (T2)':>14}")
        log(f"  {'─'*45}")
        for g in avail:
            v_t1 = expr.loc[g, met_hi.intersection(expr.columns)].mean()
            v_t2 = expr.loc[g, fh_lo.intersection(expr.columns)].mean()
            log(f"  {g:<14} {v_t1:>14.3f} {v_t2:>14.3f}")

        return d_met_hi, d_fh_lo

    return None, None

# ═══════════════════════════════════════════════════════════════
# OBJ-6: 3-GENE CLINICAL PANEL OPTIMISATION
# ═══════════════════════════════════════════════════════════════

def obj6_panel_optimisation(expr, depth, t_cols):
    log("")
    log("=" * 60)
    log("OBJ-6 — 3-GENE CLINICAL PANEL OPTIMISATION")
    log("=" * 60)
    log("  S2-P6: r > 0.85  target")
    log("  Predicted panel: KRT19/SLC22A6/ERBB2")
    log("  Exhaustive search over top candidates from S1")
    log("")

    d = depth.reindex(t_cols).dropna()
    d_arr = d.values

    def panel_r(pos_genes, neg_genes):
        pos_av = [g for g in pos_genes if g in expr.index]
        neg_av = [g for g in neg_genes if g in expr.index]
        if not pos_av and not neg_av:
            return np.nan
        parts = []
        if pos_av:
            pm = expr.loc[pos_av, t_cols].mean(axis=0)
            parts.append(norm01(pm.reindex(d.index).values))
        if neg_av:
            nm = expr.loc[neg_av, t_cols].mean(axis=0)
            parts.append(1 - norm01(nm.reindex(d.index).values))
        score = np.nanmean(parts, axis=0)
        mask  = np.isfinite(score) & np.isfinite(d_arr)
        if mask.sum() < 10:
            return np.nan
        r, _ = pearsonr(score[mask], d_arr[mask])
        return r

    # Test predicted panel first
    r_pred = panel_r(["KRT19", "ERBB2"], ["SLC22A6"])
    log(f"  Predicted panel (KRT19/ERBB2 + SLC22A6): r={r_pred:+.4f}")

    r_pred2 = panel_r(["KRT19"], ["SLC22A6", "FABP1"])
    log(f"  Alternative    (KRT19 + SLC22A6/FABP1):  r={r_pred2:+.4f}")

    # 2-gene search
    log("")
    log("  2-GENE PANELS (1 pos + 1 neg):")
    log(f"  {'Pos':<14} {'Neg':<14} {'r':>8}")
    log(f"  {'─'*38}")
    res2 = []
    pos_av = [g for g in PANEL_POS if g in expr.index]
    neg_av = [g for g in PANEL_NEG if g in expr.index]
    for pos in pos_av[:10]:
        for neg in neg_av[:10]:
            r = panel_r([pos], [neg])
            if not np.isnan(r):
                res2.append((pos, neg, r))
    res2.sort(key=lambda x: -abs(x[2]))
    for pos, neg, r in res2[:10]:
        log(f"  {pos:<14} {neg:<14} {r:>+8.4f}")

    # 3-gene search: 1pos+1neg+1(pos or neg)
    log("")
    log("  3-GENE PANELS (exhaustive top-15 candidates):")
    log(f"  {'Panel':<42} {'r':>8}")
    log(f"  {'─'*52}")

    best_r   = 0.0
    best_pan = None
    res3     = []

    # 1 pos + 2 neg
    for pos in pos_av[:12]:
        for n1, n2 in itertools.combinations(neg_av[:12], 2):
            r = panel_r([pos], [n1, n2])
            if np.isnan(r): continue
            res3.append(([pos], [n1, n2], r))
            if abs(r) > best_r:
                best_r   = abs(r)
                best_pan = ([pos], [n1, n2])

    # 2 pos + 1 neg
    for p1, p2 in itertools.combinations(pos_av[:12], 2):
        for neg in neg_av[:12]:
            r = panel_r([p1, p2], [neg])
            if np.isnan(r): continue
            res3.append(([p1, p2], [neg], r))
            if abs(r) > best_r:
                best_r   = abs(r)
                best_pan = ([p1, p2], [neg])

    res3.sort(key=lambda x: -abs(x[2]))
    for pos_g, neg_g, r in res3[:15]:
        pan_str = "+".join(pos_g) + " / " + "+".join(neg_g)
        flag = "★" if abs(r) >= 0.85 else " "
        log(f"  {flag} {pan_str:<40} {r:>+8.4f}")

    log("")
    if best_pan:
        log(f"  BEST 3-GENE PANEL:")
        log(f"    Positive: {best_pan[0]}")
        log(f"    Negative: {best_pan[1]}")
        log(f"    r = {best_r:+.4f}")
        if best_r >= 0.85:
            log("    S2-P6 CONFIRMED ✓  r >= 0.85")
        else:
            log(f"    S2-P6 NOT MET — best r = {best_r:.4f}")

    # Save panel results
    rows = [{"pos": "+".join(p), "neg": "+".join(n), "r": r}
            for p, n, r in res3[:50]]
    pd.DataFrame(rows).to_csv(
        os.path.join(RESULTS_DIR, "panel_results.csv"),
        index=False)

    return best_pan, best_r

# ═══════════════════════════════════════════════════════════════
# OBJ-7: IMMUNE ARCHITECTURE
# ═══════════════════════════════════════════════════════════════

def obj7_immune_architecture(expr, depth, t_cols):
    log("")
    log("=" * 60)
    log("OBJ-7 — IMMUNE ARCHITECTURE")
    log("=" * 60)
    log("  S2-P7: CD8A & B2M depth-negative")
    log("         IL2RA depth-positive")
    log("         PD-L1 lower in Q4 — immune exclusion")
    log("")

    d = depth.reindex(t_cols).dropna()
    q25 = d.quantile(0.25)
    q75 = d.quantile(0.75)
    q1  = d[d <= q25].index
    q4  = d[d >= q75].index

    log(f"  {'Gene':<14} {'r_depth':>9} {'p':>12} "
        f"{'Q4_mean':>9} {'Q1_mean':>9} "
        f"{'Q4/Q1':>7} {'Verdict'}")
    log(f"  {'─'*80}")

    immune_results = {}
    for gene in IMMUNE_PANEL:
        if gene not in expr.index:
            continue
        v = pd.Series(expr.loc[gene, t_cols].values,
                      index=t_cols).reindex(d.index).dropna()
        r, p = safe_r(v.values, d.reindex(v.index).values)
        q4_m = expr.loc[gene, q4.intersection(
            expr.columns)].mean()
        q1_m = expr.loc[gene, q1.intersection(
            expr.columns)].mean()
        ratio = q4_m / (q1_m + 1e-6)

        if np.isnan(r): continue

        verdict = ""
        if gene in ("CD8A", "CD8B") and r < -0.15:
            verdict = "EXCLUDED ✓"
        elif gene == "B2M" and r < -0.10:
            verdict = "MHC-I DOWN ✓"
        elif gene in ("IL2RA", "FOXP3") and r > 0.15:
            verdict = "TREG UP ✓"
        elif gene == "CD274" and ratio < 1.0:
            verdict = "PDL1 DOWN ✓"
        elif gene == "HAVCR2" and r < -0.10:
            verdict = "TIM3 DOWN ✓"

        immune_results[gene] = {
            "r": r, "p": p,
            "Q4": q4_m, "Q1": q1_m, "ratio": ratio,
        }
        log(f"  {gene:<14} {r:>+9.4f} {fmt_p(p):>12} "
            f"{q4_m:>9.3f} {q1_m:>9.3f} "
            f"{ratio:>7.3f} {verdict}")

    # S2-P7 test
    log("")
    r_cd8  = immune_results.get("CD8A", {}).get("r", np.nan)
    r_b2m  = immune_results.get("B2M",  {}).get("r", np.nan)
    r_il2r = immune_results.get("IL2RA",{}).get("r", np.nan)
    pdl1_r = immune_results.get("CD274",{}).get("ratio", np.nan)

    log(f"  S2-P7 SCORECARD:")
    log(f"    r(CD8A, depth) = {r_cd8:+.4f}  "
        f"(pred < -0.20) → "
        f"{'CONFIRMED ✓' if r_cd8 < -0.20 else 'NOT CONFIRMED ✗'}")
    log(f"    r(B2M,  depth) = {r_b2m:+.4f}  "
        f"(pred < -0.15) → "
        f"{'CONFIRMED ✓' if r_b2m < -0.15 else 'NOT CONFIRMED ✗'}")
    log(f"    r(IL2RA,depth) = {r_il2r:+.4f} "
        f"(pred > +0.20) → "
        f"{'CONFIRMED ✓' if r_il2r > 0.20 else 'NOT CONFIRMED ✗'}")
    log(f"    PDL1 Q4/Q1     = {pdl1_r:.3f}   "
        f"(pred < 1.0)   → "
        f"{'CONFIRMED ✓' if pdl1_r < 1.0 else 'NOT CONFIRMED ✗'}")

    return immune_results

# ═══════════════════════════════════════════════════════════════
# OBJ-8: DRUG TARGET DEPTH MAP
# ═══════════════════════════════════════════════════════════════

def obj8_drug_map(expr, depth, t_cols):
    log("")
    log("=" * 60)
    log("OBJ-8 — DRUG TARGET DEPTH MAP")
    log("=" * 60)
    log("  Q1/Q2/Q3/Q4 expression for each drug target gene.")
    log("  States geometry-derived drug priority per stratum.")
    log("")

    d = depth.reindex(t_cols).dropna()
    q1_idx = d[d <= d.quantile(0.25)].index
    q2_idx = d[(d > d.quantile(0.25)) &
                (d <= d.quantile(0.50))].index
    q3_idx = d[(d > d.quantile(0.50)) &
                (d <= d.quantile(0.75))].index
    q4_idx = d[d > d.quantile(0.75)].index

    log(f"  Q1 n={len(q1_idx)}  Q2 n={len(q2_idx)}  "
        f"Q3 n={len(q3_idx)}  Q4 n={len(q4_idx)}")
    log("")

    all_target_genes = list(dict.fromkeys(
        [g for genes in DRUG_TARGETS.values()
         for g in genes]
    ))

    log(f"  {'Gene':<14} {'Drug':<22} {'Q1':>7} "
        f"{'Q2':>7} {'Q3':>7} {'Q4':>7} {'Q4/Q1':>7}")
    log(f"  {'─'*75}")

    drug_rows = []
    for drug, genes in DRUG_TARGETS.items():
        for gene in genes:
            if gene not in expr.index:
                continue
            def qm(idx):
                return expr.loc[
                    gene,
                    idx.intersection(expr.columns)
                ].mean()
            q1m, q2m, q3m, q4m = qm(q1_idx), qm(q2_idx), \
                                   qm(q3_idx), qm(q4_idx)
            ratio = q4m / (q1m + 1e-6)
            trend = "▲" if ratio > 1.10 else \
                    "▼" if ratio < 0.90 else "—"
            log(f"  {gene:<14} {drug:<22} {q1m:>7.3f} "
                f"{q2m:>7.3f} {q3m:>7.3f} {q4m:>7.3f} "
                f"{ratio:>7.3f}{trend}")
            drug_rows.append({
                "gene": gene, "drug_target": drug,
                "Q1": q1m, "Q2": q2m, "Q3": q3m, "Q4": q4m,
                "Q4_Q1": ratio,
            })

    pd.DataFrame(drug_rows).to_csv(
        os.path.join(RESULTS_DIR, "drug_map.csv"),
        index=False)

    log("")
    log("  DRUG MAP INTERPRETATION:")
    log("  ┌───────────────────────────────────────────────────┐")
    log("  │ Q1 (shallowest):                                  │")
    log("  │   MET inhibitor — identity disruption             │")
    log("  │   VEGFR/mTOR — anti-proliferative (current SOC)  │")
    log("  ├───────────────────────────────────────────────────┤")
    log("  │ Q2/Q3 (intermediate):                             │")
    log("  │   EZH2 inhibitor — epigenetic lock opener         │")
    log("  │   KDM1A inhibitor — H3K4me restoration           │")
    log("  │   CDK4/6 inhibitor — CDKN2A paradox              │")
    log("  ├───────────────────────────────────────────────────┤")
    log("  │ Q4 (deepest):                                     │")
    log("  │   ERBB2-targeted (HER2-high deep PRCC)           │")
    log("  │   αKG + EZH2i combination (FH-low)               │")
    log("  │   Anti-CD25/IL2RA (Treg dominant)                │")
    log("  │   NOT anti-PD-L1 (PD-L1 falls with depth)        │")
    log("  │   NOT belzutifan (EPAS1 suppressed)              │")
    log("  └───────────────────────────────────────────────────┘")

    return drug_rows

# ═══════════════════════════════════════════════════════════════
# OBJ-9: S1 / S2 DEPTH CONCORDANCE
# ═══════════════════════════════════════════════════════════════

def obj9_depth_concordance(s1_depth, expr, t_cols):
    log("")
    log("=" * 60)
    log("OBJ-9 — S1 / S2 DEPTH CONCORDANCE")
    log("=" * 60)
    log("  Compute alternative S2 depth anchors.")
    log("  Test concordance with S1 depth score.")
    log("")

    d_s1 = s1_depth.reindex(t_cols).dropna()

    # S2 Axis A depth (KRT19 pole / SLC22A6 pole)
    krt19 = pd.Series(
        expr.loc["KRT19", t_cols].values,
        index=t_cols).reindex(d_s1.index)
    slc22 = pd.Series(
        expr.loc["SLC22A6", t_cols].values,
        index=t_cols).reindex(d_s1.index)

    if "KRT19" in expr.index and "SLC22A6" in expr.index:
        c1 = norm01(krt19.values)
        c2 = 1 - norm01(slc22.values)
        d_s2a = (c1 + c2) / 2.0
        d_s2a_s = pd.Series(d_s2a, index=d_s1.index)
        r_a, p_a = safe_r(d_s1.values, d_s2a_s.values)
        log(f"  S2 Axis A depth (KRT19/SLC22A6):")
        log(f"    r(S1_depth, S2a_depth) = {r_a:+.4f}  {fmt_p(p_a)}")
        log(f"    S2a mean={d_s2a_s.mean():.4f}  "
            f"std={d_s2a_s.std():.4f}")

    # Transition index: KRT19/SLC22A6 ratio
    log("")
    log("  TRANSITION INDEX (TI):")
    log("  TI = norm(KRT19) - norm(SLC22A6)")
    log("  High TI = KRT19-dominant = deep false attractor")
    log("  Low TI  = SLC22A6-dominant = normal PT identity")

    if "KRT19" in expr.index and "SLC22A6" in expr.index:
        ti = norm01(krt19.values) - norm01(slc22.values)
        ti_s = pd.Series(ti, index=d_s1.index)
        r_ti, p_ti = safe_r(ti_s.values, d_s1.values)

        log(f"  TI mean   = {ti_s.mean():.4f}")
        log(f"  TI median = {ti_s.median():.4f}")
        log(f"  TI std    = {ti_s.std():.4f}")
        log(f"  TI range  = [{ti_s.min():.3f}, {ti_s.max():.3f}]")
        log(f"  r(TI, S1_depth) = {r_ti:+.4f}  {fmt_p(p_ti)}")

        if ti_s.mean() > 0:
            log("  Mean TI > 0: average PRCC tumour is "
                "KRT19-dominant (biliary identity)")
        else:
            log("  Mean TI < 0: average PRCC tumour retains "
                "SLC22A6 (partial PT identity)")

        # TI correlations with all panel genes
        log("")
        log("  TOP TI CORRELATES (same format as ccRCC GOT1/RUNX1 TI):")
        log(f"  {'Gene':<14} {'r_TI':>9} {'p':>12}")
        log(f"  {'─'*38}")
        ti_rows = []
        for gene in expr.index:
            v = pd.Series(
                expr.loc[gene, t_cols].values,
                index=t_cols).reindex(ti_s.index).dropna()
            if len(v) < 10: continue
            r, p = safe_r(v.values,
                          ti_s.reindex(v.index).values)
            if not np.isnan(r):
                ti_rows.append((gene, r, p))
        ti_rows.sort(key=lambda x: -abs(x[1]))
        for gene, r, p in ti_rows[:20]:
            log(f"  {gene:<14} {r:>+9.4f} {fmt_p(p):>12}")

        # Save
        pd.DataFrame([{
            "sample_id": s, "s1_depth": d_s1.get(s, np.nan),
            "TI": ti_s.get(s, np.nan),
        } for s in d_s1.index]).to_csv(
            os.path.join(RESULTS_DIR,
                         "transition_index.csv"),
            index=False)

        return ti_s

    return None

# ═══════════════════════════════════════════════════════════════
# OBJ-10: TWIST1 EMT AXIS
# ═══════════════════════════════════════════════════════════════

def obj10_twist1_emt(expr, depth, t_cols):
    log("")
    log("=" * 60)
    log("OBJ-10 — TWIST1 WITHIN-TUMOUR EMT AXIS")
    log("=" * 60)
    log("  Is TWIST1 separable from the biliary KRT19 axis?")
    log("  TWIST1 Q4/Q1=1.563 despite being DOWN vs normal.")
    log("")

    d = depth.reindex(t_cols).dropna()

    emt_genes_av = [g for g in EMT_GENES if g in expr.index]
    log(f"  {'Gene':<14} {'r_depth':>9} {'p':>12} "
        f"{'r_KRT19':>9} {'r_TWIST1':>9}")
    log(f"  {'─'*58}")

    if "KRT19" not in expr.index or \
       "TWIST1" not in expr.index:
        log("  KRT19 or TWIST1 not in matrix.")
        return

    krt19_v  = pd.Series(
        expr.loc["KRT19", t_cols].values,
        index=t_cols).reindex(d.index).dropna()
    twist1_v = pd.Series(
        expr.loc["TWIST1", t_cols].values,
        index=t_cols).reindex(d.index).dropna()

    for gene in emt_genes_av:
        v = pd.Series(
            expr.loc[gene, t_cols].values,
            index=t_cols).reindex(d.index).dropna()
        r_d,  _ = safe_r(v.values, d.reindex(v.index).values)
        r_k,  _ = safe_r(v.values,
                         krt19_v.reindex(v.index).values)
        r_t,  _ = safe_r(v.values,
                         twist1_v.reindex(v.index).values)
        log(f"  {gene:<14} {r_d:>+9.4f} {'':>12} "
            f"{r_k:>+9.4f} {r_t:>+9.4f}")

    # Separate EMT axis score
    emt_pos = [g for g in ["TWIST1", "VIM", "ZEB1", "SNAI2"]
               if g in expr.index]
    emt_neg = [g for g in ["CDH1", "CDH2"] if g in expr.index]
    # CDH1 is DOWN and CDH2 varies — use VIM/TWIST1 only

    if emt_pos:
        emt_mat = expr.loc[emt_pos, t_cols].mean(axis=0)
        emt_score = norm01(
            emt_mat.reindex(d.index).values
        )
        emt_s = pd.Series(emt_score, index=d.index)
        r_emt_depth, p_emt = safe_r(emt_s.values, d.values)
        r_emt_krt19, _     = safe_r(
            emt_s.values,
            krt19_v.reindex(d.index).values)

        log("")
        log(f"  EMT score (VIM/TWIST1/ZEB1/SNAI2 mean):")
        log(f"    r(EMT_score, S1_depth) = "
            f"{r_emt_depth:+.4f}  {fmt_p(p_emt)}")
        log(f"    r(EMT_score, KRT19)    = "
            f"{r_emt_krt19:+.4f}")

        r_krt19_depth, _ = safe_r(
            krt19_v.values, d.reindex(krt19_v.index).values)

        if abs(r_emt_depth) > 0.20 and abs(r_krt19_depth) > 0.40:
            diff = abs(r_emt_depth) - abs(r_krt19_depth)
            if diff < -0.10:
                log("  VERDICT: Biliary identity axis (KRT19) "
                    "is STRONGER depth driver than EMT axis.")
                log("  TWIST1 is a secondary within-tumour "
                    "signal, not the primary axis.")
            else:
                log("  VERDICT: EMT and biliary axes are "
                    "comparably strong.")

    return

# ═══════════════════════════════════════════════════════════════
# OBJ-11: CA9 MECHANISM — VHL vs HIF1A
# ═══════════════════════════════════════════════════════════════

def obj11_ca9_mechanism(expr, depth, t_cols):
    log("")
    log("=" * 60)
    log("OBJ-11 — CA9 MECHANISM (VHL vs HIF1A)")
    log("=" * 60)
    log("  S2-P8: r(CA9, HIF1A) > r(CA9, EPAS1)")
    log("         VHL→CA9 BROKEN confirmed in S1")
    log("         What DOES drive CA9 in PRCC?")
    log("")

    d = depth.reindex(t_cols).dropna()

    genes_to_test = ["CA9", "EPAS1", "HIF1A", "VHL",
                     "LDHA", "SLC2A1", "VEGFA", "PDK1",
                     "KRT19", "MET", "ERBB2"]
    avail = [g for g in genes_to_test if g in expr.index]

    if "CA9" not in avail:
        log("  CA9 not in expression matrix.")
        return

    ca9_v = pd.Series(
        expr.loc["CA9", t_cols].values,
        index=t_cols).reindex(d.index).dropna()

    log(f"  {'Gene':<12} {'r vs CA9':>10} {'p':>12} {'note'}")
    log(f"  {'─'*52}")

    r_hif1a = np.nan
    r_epas1 = np.nan

    for gene in avail:
        if gene == "CA9": continue
        v = pd.Series(
            expr.loc[gene, t_cols].values,
            index=t_cols).reindex(ca9_v.index).dropna()
        r, p = safe_r(ca9_v.reindex(v.index).values, v.values)
        if np.isnan(r): continue

        if gene == "HIF1A": r_hif1a = r
        if gene == "EPAS1": r_epas1 = r

        note = ""
        if gene == "VHL"   and abs(r) < 0.15: note = "BROKEN (confirmed)"
        if gene == "EPAS1" and abs(r) > 0.20: note = "EPAS1-mediated"
        if gene == "HIF1A" and abs(r) > 0.20: note = "HIF1A-mediated ★"
        if gene == "KRT19" and abs(r) > 0.20: note = "co-biliary-identity"
        log(f"  {gene:<12} {r:>+10.4f} {fmt_p(p):>12} {note}")

    log("")
    log(f"  S2-P8 FORMAL TEST:")
    log(f"    r(CA9, HIF1A) = {r_hif1a:+.4f}")
    log(f"    r(CA9, EPAS1) = {r_epas1:+.4f}")
    if not np.isnan(r_hif1a) and not np.isnan(r_epas1):
        if abs(r_hif1a) > abs(r_epas1):
            log("    S2-P8 CONFIRMED: HIF1A drives CA9 "
                "more than EPAS1 ✓")
        else:
            log("    S2-P8 NOT CONFIRMED: EPAS1 >= HIF1A ✗")

    # CA9 correlation with depth
    r_ca9_d, p_ca9_d = safe_r(ca9_v.values,
                               d.reindex(ca9_v.index).values)
    log(f"  r(CA9, depth) = {r_ca9_d:+.4f}  {fmt_p(p_ca9_d)}")

# ���══════════════════════════════════════════════════════════════
# FIGURE — 12 panels
# ═══════════════════════════════════════════════════════════════

def generate_figure(expr, depth, t_cols, n_cols,
                    score_a, score_b, r_ab,
                    ti_s, subtype_depths,
                    immune_results, drug_rows):
    log("")
    log("=" * 60)
    log("GENERATING FIGURE — SCRIPT 2")
    log("=" * 60)

    d = depth.reindex(t_cols).dropna()

    fig = plt.figure(figsize=(26, 30))
    gs  = gridspec.GridSpec(4, 3, figure=fig,
                             hspace=0.55, wspace=0.40)

    # Panel A: Sub-axis comparison scatter
    ax_A = fig.add_subplot(gs[0, 0])
    if score_a is not None and score_b is not None:
        idx = score_a.index.intersection(score_b.index)
        ax_A.scatter(score_a.reindex(idx),
                     score_b.reindex(idx),
                     c=d.reindex(idx), cmap="RdBu_r",
                     s=12, alpha=0.6)
        ax_A.set_xlabel("Axis A (biliary identity)", fontsize=9)
        ax_A.set_ylabel("Axis B (TCA metabolic)", fontsize=9)
        ax_A.set_title(
            f"A: Sub-axis Separation\n"
            f"r(A,B)={r_ab:+.3f} "
            f"({'separable' if r_ab < 0.80 else 'not separable'})",
            fontsize=9, fontweight="bold")
    else:
        ax_A.text(0.5, 0.5, "Axes not computed",
                  ha="center", va="center",
                  transform=ax_A.transAxes)
        ax_A.set_title("A: Sub-axis Separation",
                       fontsize=9, fontweight="bold")

    # Panel B: ERBB2 co-expression
    ax_B = fig.add_subplot(gs[0, 1])
    if "ERBB2" in expr.index and "KRT19" in expr.index:
        e_v = expr.loc["ERBB2", t_cols]
        k_v = expr.loc["KRT19", t_cols]
        ax_B.scatter(e_v, k_v,
                     c=d.reindex(t_cols), cmap="RdBu_r",
                     s=12, alpha=0.6)
        r_ek, _ = safe_r(e_v.values, k_v.values)
        ax_B.set_xlabel("ERBB2", fontsize=9)
        ax_B.set_ylabel("KRT19", fontsize=9)
        ax_B.set_title(
            f"B: ERBB2 → KRT19 Identity\n"
            f"r={r_ek:+.3f}",
            fontsize=9, fontweight="bold")

    # Panel C: FH depth correlation
    ax_C = fig.add_subplot(gs[0, 2])
    if "FH" in expr.index:
        fh_v = pd.Series(
            expr.loc["FH", t_cols].values,
            index=t_cols).reindex(d.index).dropna()
        ax_C.scatter(fh_v.values,
                     d.reindex(fh_v.index).values,
                     c=d.reindex(fh_v.index).values,
                     cmap="RdBu_r", s=12, alpha=0.6)
        r_fhd, _ = safe_r(fh_v.values,
                           d.reindex(fh_v.index).values)
        ax_C.set_xlabel("FH expression", fontsize=9)
        ax_C.set_ylabel("Depth score", fontsize=9)
        ax_C.set_title(
            f"C: FH as Depth Stratifier\n"
            f"r={r_fhd:+.3f}",
            fontsize=9, fontweight="bold")

    # Panel D: Transition Index distribution
    ax_D = fig.add_subplot(gs[1, 0])
    if ti_s is not None:
        ax_D.hist(ti_s.values, bins=30,
                  color="#8E44AD", alpha=0.8,
                  edgecolor="white")
        ax_D.axvline(ti_s.mean(), color="black",
                     linestyle="--",
                     label=f"Mean={ti_s.mean():.3f}")
        ax_D.axvline(0, color="red", linewidth=0.8,
                     linestyle=":", label="Saddle=0")
        ax_D.set_xlabel("Transition Index\n"
                        "norm(KRT19) − norm(SLC22A6)",
                        fontsize=8)
        ax_D.set_ylabel("Count", fontsize=9)
        ax_D.set_title("D: Transition Index\n"
                       "(KRT19/SLC22A6 saddle)",
                       fontsize=9, fontweight="bold")
        ax_D.legend(fontsize=7)

    # Panel E: Immune architecture heatmap-style
    ax_E = fig.add_subplot(gs[1, 1])
    if immune_results:
        genes_im = list(immune_results.keys())
        r_vals   = [immune_results[g]["r"] for g in genes_im]
        colors_e = ["#C0392B" if r > 0 else "#2980B9"
                    for r in r_vals]
        ax_E.barh(range(len(genes_im)), r_vals,
                  color=colors_e, alpha=0.85)
        ax_E.set_yticks(range(len(genes_im)))
        ax_E.set_yticklabels(genes_im, fontsize=8)
        ax_E.invert_yaxis()
        ax_E.axvline(0, color="black", linewidth=0.8)
        ax_E.set_xlabel("r vs depth score", fontsize=9)
        ax_E.set_title("E: Immune Architecture\n"
                       "(r with depth)",
                       fontsize=9, fontweight="bold")

    # Panel F: Drug map Q4/Q1
    ax_F = fig.add_subplot(gs[1, 2])
    if drug_rows:
        drdf = pd.DataFrame(drug_rows)
        drdf = drdf.drop_duplicates("gene").sort_values(
            "Q4_Q1", ascending=True)
        colors_f = ["#C0392B" if r > 1.10 else
                    "#2980B9" if r < 0.90 else
                    "#95A5A6"
                    for r in drdf.Q4_Q1]
        ax_F.barh(range(len(drdf)),
                  drdf.Q4_Q1.values,
                  color=colors_f, alpha=0.85)
        ax_F.set_yticks(range(len(drdf)))
        ax_F.set_yticklabels(drdf.gene.values, fontsize=7)
        ax_F.axvline(1.0, color="black", linewidth=0.8)
        ax_F.set_xlabel("Q4/Q1 expression ratio", fontsize=9)
        ax_F.set_title("F: Drug Target Q4/Q1\n"
                       "(deep vs shallow PRCC)",
                       fontsize=9, fontweight="bold")

    # Panel G: PBRM1 → KRT19 scatter
    ax_G = fig.add_subplot(gs[2, 0])
    if "PBRM1" in expr.index and "KRT19" in expr.index:
        p_v = expr.loc["PBRM1", t_cols]
        k_v = expr.loc["KRT19", t_cols]
        ax_G.scatter(p_v, k_v,
                     c=d.reindex(t_cols), cmap="RdBu_r",
                     s=12, alpha=0.6)
        r_pk, _ = safe_r(p_v.values, k_v.values)
        ax_G.set_xlabel("PBRM1", fontsize=9)
        ax_G.set_ylabel("KRT19", fontsize=9)
        ax_G.set_title(
            f"G: PBRM1 → KRT19\n"
            f"r={r_pk:+.3f}  "
            f"({'CONFIRMED' if r_pk < -0.20 else 'weak'})",
            fontsize=9, fontweight="bold")

    # Panel H: S1 vs S2 depth concordance
    ax_H = fig.add_subplot(gs[2, 1])
    if ti_s is not None:
        ax_H.scatter(d.values,
                     ti_s.reindex(d.index).values,
                     s=8, alpha=0.5,
                     color="#E74C3C")
        r_conc, _ = safe_r(d.values,
                            ti_s.reindex(d.index).values)
        ax_H.set_xlabel("S1 Depth Score", fontsize=9)
        ax_H.set_ylabel("Transition Index", fontsize=9)
        ax_H.set_title(
            f"H: S1 Depth vs TI\nr={r_conc:+.3f}",
            fontsize=9, fontweight="bold")

    # Panel I: ERBB2 vs MKI67 scatter
    ax_I = fig.add_subplot(gs[2, 2])
    if "ERBB2" in expr.index and "MKI67" in expr.index:
        e_v = expr.loc["ERBB2", t_cols]
        m_v = expr.loc["MKI67", t_cols]
        ax_I.scatter(e_v, m_v,
                     c=d.reindex(t_cols), cmap="RdBu_r",
                     s=12, alpha=0.6)
        r_em, _ = safe_r(e_v.values, m_v.values)
        ax_I.set_xlabel("ERBB2", fontsize=9)
        ax_I.set_ylabel("MKI67", fontsize=9)
        ax_I.set_title(
            f"I: ERBB2 vs MKI67\n"
            f"r={r_em:+.3f}  "
            f"({'identity' if r_em < 0.25 else 'proliferative'})",
            fontsize=9, fontweight="bold")

    # Panel J: CA9 mechanism scatter
    ax_J = fig.add_subplot(gs[3, 0])
    if "CA9" in expr.index and "HIF1A" in expr.index:
        c_v  = expr.loc["CA9",  t_cols]
        h1_v = expr.loc["HIF1A", t_cols]
        ax_J.scatter(h1_v, c_v,
                     c=d.reindex(t_cols), cmap="RdBu_r",
                     s=12, alpha=0.6)
        r_ch, _ = safe_r(h1_v.values, c_v.values)
        ax_J.set_xlabel("HIF1A", fontsize=9)
        ax_J.set_ylabel("CA9", fontsize=9)
        ax_J.set_title(
            f"J: HIF1A → CA9\nr={r_ch:+.3f}",
            fontsize=9, fontweight="bold")

    # Panel K: FH-TCA-EZH2 axis
    ax_K = fig.add_subplot(gs[3, 1])
    if "FH" in expr.index and "EZH2" in expr.index:
        f_v  = expr.loc["FH",  t_cols]
        ez_v = expr.loc["EZH2", t_cols]
        ax_K.scatter(f_v, ez_v,
                     c=d.reindex(t_cols), cmap="RdBu_r",
                     s=12, alpha=0.6)
        r_fe, _ = safe_r(f_v.values, ez_v.values)
        ax_K.set_xlabel("FH", fontsize=9)
        ax_K.set_ylabel("EZH2", fontsize=9)
        ax_K.set_title(
            f"K: FH → EZH2 (TCA-chromatin)\nr={r_fe:+.3f}",
            fontsize=9, fontweight="bold")

    # Panel L: Summary
    ax_L = fig.add_subplot(gs[3, 2])
    ax_L.axis("off")
    summary = [
        "PRCC FALSE ATTRACTOR — Script 2",
        "OrganismCore | 2026-03-02",
        "",
        "ATTRACTOR TYPE:",
        "Biliary-papillary cytokeratin identity",
        "NOT EMT. NOT Warburg. NOT HIF-driven.",
        "",
        "PRIMARY AXIS:",
        "KRT19 (+) / SLC22A6 (-)",
        "ERBB2 = identity co-driver",
        "",
        "EPIGENETIC LOCK:",
        "EZH2 + KDM1A (chromatin)",
        "FH/OGDHL/SUCLG1 → αKG → TCA-EZH2",
        "",
        "NOT PREDICTED — CONFIRMED:",
        "ERBB2 identity circuit",
        "MET = identity, NOT mitogen",
        "CDKN2A/CDK4 stress bypass",
        "Belzutifan INACTIVE (EPAS1 DOWN)",
    ]
    ax_L.text(0.05, 0.95, "\n".join(summary),
              transform=ax_L.transAxes,
              fontsize=7.5, va="top",
              family="monospace",
              bbox=dict(boxstyle="round",
                        facecolor="#ECF0F1",
                        alpha=0.8))
    ax_L.set_title("L: Script 2 Summary",
                   fontsize=9, fontweight="bold")

    fig.suptitle(
        "PRCC False Attractor — Script 2\n"
        "OrganismCore | Document 95b | 2026-03-02",
        fontsize=13, fontweight="bold", y=0.99)

    fig_path = os.path.join(RESULTS_DIR, "prcc_s2_figure.png")
    fig.savefig(fig_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    log(f"  Figure saved: {fig_path}")

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    log("OrganismCore — PRCC False Attractor")
    log("Script 2 — Sub-axes / Circuits / "
        "Subtype / Panel / Drug Map")
    log("Document 95b | 2026-03-02")
    log("")
    log("PREDICTIONS LOCKED 2026-03-02:")
    log("  S2-P1: r(ERBB2,KRT19) > 0.50  identity not prolif")
    log("  S2-P2: r(AxisA,AxisB) < 0.80  axes separable")
    log("  S2-P3: r(FH,depth) < -0.45   continuous stratifier")
    log("  S2-P4: r(PBRM1,KRT19) < -0.20  biliary release")
    log("  S2-P5: Type2 depth > Type1   MW p<0.05")
    log("  S2-P6: 3-gene panel r > 0.85")
    log("  S2-P7: CD8A/B2M down, IL2RA up in Q4")
    log("  S2-P8: HIF1A drives CA9 more than EPAS1")
    log("")

    # Load S1 depth
    s1_depth = load_s1_depth()
    if s1_depth is None:
        log("FATAL: cannot proceed without S1 depth.")
        write_log()
        return

    # Reload expression
    expr, meta, t_cols, n_cols = load_expression()

    # Fetch subtype annotation
    cbio_df  = fetch_subtype_annotation()
    subtypes = extract_subtype(cbio_df, t_cols)

    log("")
    log("═" * 60)
    log("PRIMARY ANALYSIS — TCGA-KIRP")
    log("═" * 60)

    # OBJ-1: Sub-axis separation
    score_a, score_b, r_ab = obj1_subaxis_separation(
        expr, s1_depth, t_cols)

    # OBJ-2: ERBB2 identity circuit
    erbb2_res = obj2_erbb2_circuit(expr, s1_depth, t_cols)

    # OBJ-3: FH depth stratifier
    fh_res = obj3_fh_stratifier(expr, s1_depth, t_cols)

    # OBJ-4: PBRM1 → biliary circuit
    obj4_pbrm1_circuit(expr, s1_depth, t_cols)

    # OBJ-5: Subtype depth stratification
    d_t1, d_t2 = obj5_subtype_depth(
        expr, s1_depth, t_cols, subtypes)

    # OBJ-6: Panel optimisation
    best_pan, best_r = obj6_panel_optimisation(
        expr, s1_depth, t_cols)

    # OBJ-7: Immune architecture
    immune_res = obj7_immune_architecture(
        expr, s1_depth, t_cols)

    # OBJ-8: Drug map
    drug_rows = obj8_drug_map(
        expr, s1_depth, t_cols)

    # OBJ-9: Depth concordance + Transition Index
    ti_s = obj9_depth_concordance(
        s1_depth, expr, t_cols)

    # OBJ-10: TWIST1 EMT axis
    obj10_twist1_emt(expr, s1_depth, t_cols)

    # OBJ-11: CA9 mechanism
    obj11_ca9_mechanism(expr, s1_depth, t_cols)

    # Figure
    generate_figure(
        expr, s1_depth, t_cols, n_cols,
        score_a, score_b, r_ab,
        ti_s,
        {"Type1_proxy": d_t1,
         "Type2_proxy": d_t2}
        if d_t1 is not None else {},
        immune_res, drug_rows)

    # ── COMPLETE ──────────────────────────────────────────────
    log("")
    log("=" * 60)
    log("SCRIPT 2 COMPLETE")
    log("=" * 60)
    log(f"  Outputs: {RESULTS_DIR}")
    for fname in sorted(os.listdir(RESULTS_DIR)):
        fpath = os.path.join(RESULTS_DIR, fname)
        log(f"    {fname:<55} "
            f"{os.path.getsize(fpath):>8} bytes")
    log("")
    log("  ┌──────────────────────────────────────────────────┐")
    log("  │  READING ORDER FOR DOCUMENT 95b                  │")
    log("  │                                                  │")
    log("  │  1. OBJ-1: Are the two axes separable?          │")
    log("  │     r(Axis_A, Axis_B) — read the number.        │")
    log("  │     What bridges them?                          │")
    log("  │                                                  │")
    log("  │  2. OBJ-2: Is ERBB2 identity or proliferative?  │")
    log("  │     r(ERBB2,KRT19) vs r(ERBB2,MKI67)            │")
    log("  │     This determines the drug mechanism.         │")
    log("  │                                                  │")
    log("  │  3. OBJ-3: Is FH a continuous depth sensor?     │")
    log("  │     FH-low depth vs FH-high depth. Drug proxy.  │")
    log("  │                                                  │")
    log("  │  4. OBJ-6: Did the panel hit r > 0.85?          │")
    log("  │     Read best_panel. Is KRT19 in it?            │")
    log("  │     Is ERBB2 the third gene?                    │")
    log("  │                                                  │")
    log("  │  5. OBJ-7: Immune exclusion confirmed?          │")
    log("  │     CD8A down? IL2RA up? PDL1 down?             │")
    log("  │     Anti-PD-L1 contra-indicated in Q4?          │")
    log("  │                                                  │")
    log("  │  6. OBJ-9: Transition Index mean.               │")
    log("  │     >0 = KRT19-dominant (biliary locked)        │")
    log("  │     <0 = SLC22A6-dominant (PT identity partial) │")
    log("  │                                                  │")
    log("  │  7. Write Document 95b before Script 3.         │")
    log("  └──────────────────────────────────────────────────┘")

    write_log()


if __name__ == "__main__":
    main()
