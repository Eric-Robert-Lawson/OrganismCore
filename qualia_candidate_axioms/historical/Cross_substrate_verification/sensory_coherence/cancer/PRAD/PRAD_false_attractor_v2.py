"""
Prostate Adenocarcinoma — False Attractor Analysis
SCRIPT 2 — CIRCUIT ANALYSIS
Dataset: GSE32571
  59 PRAD tumors | 39 matched benign prostate
  Illumina HumanHT-12 microarray
  Normalized in Script 1 (reused here)

SCRIPT 2 OBJECTIVES:
  1. GAP ANALYSIS — circuit connections
     AR→FOXA1→AMACR/HOXC6
     EZH2→ACPP/MSMB
     MYC/AURKA with depth
  2. ERG SUBTYPE ANALYSIS
     ERG-high vs ERG-low depth/genes
  3. 3-GENE SCORE
     ACPP + HOXC6 + AMACR formal
  4. NKX3-1 FUNCTION GAP
     NKX3-1→ACPP within tumors
     Circuit intact or broken?
  5. FOXA1 CIRCUIT ARCHITECTURE
     FOXA1→AMACR / FOXA1→HOXC6

ARCHITECTURE QUESTION:
  In PAAD: PTF1A→CTRC r=+0.754 INTACT
           Block at PTF1A INPUT
  In MDS:  CEBPE→ELANE r=0.07 BROKEN
           Circuit disconnected
  In PRAD: NKX3-1→ACPP = ?
           Is the terminal differentiation
           circuit intact or broken?
           This determines the drug target.

Author: Eric Robert Lawson
Framework: OrganismCore Principles-First
Doc: 88b | Date: 2026-03-01
"""

import os
import sys
import gzip
import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import gaussian_kde
from scipy.signal import argrelmin
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import warnings
warnings.filterwarnings("ignore")

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR    = "./prad_false_attractor/"
RESULTS_DIR = os.path.join(BASE_DIR, "results")
S2_DIR      = os.path.join(BASE_DIR, "results_s2")
LOG_FILE    = os.path.join(S2_DIR,
                           "s2_analysis_log.txt")

os.makedirs(S2_DIR, exist_ok=True)

# Reuse normalized data from Script 1
S1_SADDLE = os.path.join(
    RESULTS_DIR, "saddle_results.csv"
)
S1_META   = os.path.join(
    RESULTS_DIR, "metadata.csv"
)
MATRIX    = os.path.join(
    BASE_DIR,
    "GSE32571_non_normalized.txt.gz"
)
PROBE_MAP = os.path.join(
    BASE_DIR, "probe_map.csv"
)
ANNOT_GZ  = os.path.join(
    BASE_DIR, "GPL10558.annot.gz"
)

# ERG threshold from Script 1
ERG_THRESHOLD = 6.4804

# ============================================================
# GENE PANELS
# ============================================================

SWITCH_GENES = [
    "NKX3-1", "FOXA1", "KLK3",
    "ACPP", "KLK2", "MSMB",
]
FA_MARKERS = [
    "ERG", "MKI67", "EZH2",
    "HOXC6", "AMACR",
]
EPIGENETIC = [
    "EZH2", "EED", "SUZ12",
    "KDM6A", "DNMT3A", "BMI1", "JARID2",
]
AR_AXIS = [
    "AR", "KLK3", "KLK2",
    "TMPRSS2", "FKBP5", "STEAP2",
    "NKX3-1", "FOXA1",
]
SCAFFOLD = [
    "MYC", "CCND1", "CDK4",
    "CDK6", "RB1", "PTEN", "TP53",
]
LUMINAL = [
    "KRT8", "KRT18", "KRT19",
    "CDH1", "EPCAM", "HOXB13",
    "GATA2", "GATA3",
]
BASAL = [
    "KRT5", "KRT14", "TP63",
    "CD44", "ITGA6", "NGFR",
]
EMT = [
    "VIM", "CDH2", "SNAI1",
    "SNAI2", "ZEB1", "TWIST1", "FN1",
]
ERG_PROGRAM = [
    "ERG", "ETV1", "ETV4",
    "ETV5", "SPDEF",
]
NEUROENDOCRINE = [
    "CHGA", "SYP", "ENO2",
    "NCAM1", "AURKA", "MYCN", "SOX2",
]
PROGNOSIS = [
    "MKI67", "PCNA", "TOP2A",
    "AURKA", "PLK1", "BUB1B",
]

ALL_TARGET = list(dict.fromkeys(
    SWITCH_GENES + FA_MARKERS +
    EPIGENETIC + AR_AXIS + SCAFFOLD +
    LUMINAL + BASAL + EMT +
    ERG_PROGRAM + NEUROENDOCRINE +
    PROGNOSIS
))

# Circuit connections to test
# (gene_a, gene_b, direction, description)
CIRCUIT_CONNECTIONS = [
    # AR axis
    ("AR",     "FOXA1",  "+",
     "AR drives FOXA1 pioneer factor"),
    ("AR",     "KLK3",   "+",
     "AR drives KLK3/PSA"),
    ("AR",     "NKX3-1", "+",
     "AR drives NKX3-1"),
    ("AR",     "TMPRSS2","+",
     "AR drives TMPRSS2"),
    ("FOXA1",  "AR",     "+",
     "FOXA1 co-activates AR program"),
    # FOXA1 → FA program
    ("FOXA1",  "AMACR",  "+",
     "FOXA1 drives AMACR?"),
    ("FOXA1",  "HOXC6",  "+",
     "FOXA1 drives HOXC6?"),
    ("FOXA1",  "EZH2",   "+",
     "FOXA1 drives EZH2?"),
    # EZH2 → switch gene suppression
    ("EZH2",   "ACPP",   "-",
     "EZH2 silences ACPP"),
    ("EZH2",   "MSMB",   "-",
     "EZH2 silences MSMB"),
    ("EZH2",   "NKX3-1", "-",
     "EZH2 silences NKX3-1"),
    ("EZH2",   "KLK3",   "-",
     "EZH2 silences KLK3"),
    # NKX3-1 function gap
    ("NKX3-1", "ACPP",   "+",
     "NKX3-1 drives ACPP — intact?"),
    ("NKX3-1", "MSMB",   "+",
     "NKX3-1 drives MSMB — intact?"),
    ("NKX3-1", "KLK3",   "+",
     "NKX3-1 drives KLK3 — intact?"),
    # MYC / proliferation
    ("MYC",    "MKI67",  "+",
     "MYC drives proliferation"),
    ("MYC",    "CDK4",   "+",
     "MYC drives CDK4"),
    ("AURKA",  "MKI67",  "+",
     "AURKA tracks proliferation"),
    # Basal dissolution
    ("EZH2",   "TP63",   "-",
     "EZH2 silences basal TP63?"),
    ("EZH2",   "KRT5",   "-",
     "EZH2 silences basal KRT5?"),
]

# ============================================================
# PROBE MAP — reuse Script 1 approach
# ============================================================

PROBE_GENE_MAP = {
    "ILMN_1766707": "NKX3-1",
    "ILMN_1718800": "NKX3-1",
    "ILMN_2337565": "FOXA1",
    "ILMN_1679881": "FOXA1",
    "ILMN_1773275": "KLK3",
    "ILMN_2388574": "KLK3",
    "ILMN_1811083": "ACPP",
    "ILMN_1788078": "KLK2",
    "ILMN_1788866": "MSMB",
    "ILMN_2147486": "MSMB",
    "ILMN_2338729": "ERG",
    "ILMN_1766526": "ERG",
    "ILMN_1806487": "MKI67",
    "ILMN_2413324": "MKI67",
    "ILMN_1688580": "EZH2",
    "ILMN_1795529": "EZH2",
    "ILMN_1712966": "HOXC6",
    "ILMN_1793626": "AMACR",
    "ILMN_1669115": "AMACR",
    "ILMN_2136659": "EED",
    "ILMN_1739177": "SUZ12",
    "ILMN_1778439": "KDM6A",
    "ILMN_1700949": "DNMT3A",
    "ILMN_1670195": "BMI1",
    "ILMN_1786314": "JARID2",
    "ILMN_1701183": "AR",
    "ILMN_2377461": "AR",
    "ILMN_1786475": "TMPRSS2",
    "ILMN_2184373": "TMPRSS2",
    "ILMN_1705169": "FKBP5",
    "ILMN_1788660": "STEAP2",
    "ILMN_1674999": "MYC",
    "ILMN_2348918": "MYC",
    "ILMN_1697622": "CCND1",
    "ILMN_1738801": "CDK4",
    "ILMN_1698467": "CDK6",
    "ILMN_1776507": "RB1",
    "ILMN_2185948": "PTEN",
    "ILMN_2402257": "TP53",
    "ILMN_1688895": "KRT8",
    "ILMN_1711192": "KRT18",
    "ILMN_1765851": "KRT19",
    "ILMN_1791210": "CDH1",
    "ILMN_1668111": "EPCAM",
    "ILMN_2387561": "HOXB13",
    "ILMN_1714588": "GATA2",
    "ILMN_2341949": "GATA3",
    "ILMN_1779323": "KRT5",
    "ILMN_1713464": "KRT14",
    "ILMN_1692128": "TP63",
    "ILMN_2383725": "CD44",
    "ILMN_2364093": "ITGA6",
    "ILMN_1699012": "NGFR",
    "ILMN_1777688": "VIM",
    "ILMN_1714228": "CDH2",
    "ILMN_1697281": "SNAI1",
    "ILMN_1693140": "SNAI2",
    "ILMN_1779677": "ZEB1",
    "ILMN_1796316": "TWIST1",
    "ILMN_1766619": "FN1",
    "ILMN_1772887": "ETV1",
    "ILMN_1668770": "ETV4",
    "ILMN_1791861": "ETV5",
    "ILMN_1715210": "SPDEF",
    "ILMN_1683121": "CHGA",
    "ILMN_1791735": "SYP",
    "ILMN_1770337": "ENO2",
    "ILMN_1808680": "NCAM1",
    "ILMN_1681538": "AURKA",
    "ILMN_1745538": "MYCN",
    "ILMN_1736783": "SOX2",
    "ILMN_1698404": "PCNA",
    "ILMN_1751278": "TOP2A",
    "ILMN_1762653": "PLK1",
    "ILMN_1741308": "BUB1B",
}

# ============================================================
# LOGGING
# ============================================================

log_lines = []

def log(msg=""):
    print(msg)
    log_lines.append(str(msg))

def write_log():
    with open(LOG_FILE, "w") as f:
        f.write("\n".join(log_lines))

# ============================================================
# RELOAD DATA
# Reuse Script 1 matrix and annotation
# ============================================================

def reload_data():
    log("=" * 65)
    log("RELOADING NORMALIZED DATA")
    log("Reusing Script 1 preprocessing")
    log("=" * 65)

    # Load matrix
    log(f"\n  Loading matrix: "
        f"{os.path.basename(MATRIX)}")
    with gzip.open(MATRIX, "rt") as f:
        df = pd.read_csv(
            f, sep="\t", index_col=0,
            low_memory=False
        )

    expr_cols = [
        c for c in df.columns
        if "detection" not in c.lower()
        and "pval" not in c.lower()
    ]
    pval_cols = [
        c for c in df.columns
        if "detection" in c.lower()
        or "pval" in c.lower()
    ]

    expr_df = df[expr_cols].apply(
        pd.to_numeric, errors="coerce"
    )

    if pval_cols:
        pval_df = df[pval_cols].apply(
            pd.to_numeric, errors="coerce"
        )
        detected   = (pval_df < 0.05).sum(axis=1)
        min_detect = max(
            3, int(len(pval_cols) * 0.20)
        )
        expr_df = expr_df[
            detected >= min_detect
        ]

    expr_df = expr_df.clip(lower=1.0)
    expr_df = np.log2(expr_df)

    # Quantile normalize
    arr      = expr_df.values.copy()
    sort_arr = np.sort(arr, axis=0)
    mean_ref = sort_arr.mean(axis=1)
    rank_idx = np.argsort(
        np.argsort(arr, axis=0), axis=0
    )
    expr_df = pd.DataFrame(
        mean_ref[rank_idx],
        index=expr_df.index,
        columns=expr_df.columns,
    )

    # Probe mapping — annot CSV first
    probe_ids = set(expr_df.index)
    mapped    = {
        p: g for p, g
        in PROBE_GENE_MAP.items()
        if p in probe_ids
    }

    if os.path.exists(ANNOT_GZ):
        log("  Loading cached annotation...")
        try:
            with gzip.open(ANNOT_GZ, "rt") as gz:
                lines = gz.readlines()
            in_t = False
            cols = None
            ic = sc = None
            extra = {}
            for line in lines:
                line = line.rstrip()
                if "platform_table_begin" \
                        in line:
                    in_t = True
                    cols = None
                    continue
                if "platform_table_end" \
                        in line:
                    break
                if not in_t:
                    continue
                parts = line.split("\t")
                if cols is None:
                    cols = parts
                    for i, c in enumerate(cols):
                        cl = c.lower()
                        if cl == "id":
                            ic = i
                        if cl in [
                            "gene symbol",
                            "symbol",
                            "gene_symbol",
                        ]:
                            sc = i
                    continue
                if (ic is not None
                        and sc is not None
                        and len(parts)
                        > max(ic, sc)):
                    p = parts[ic].strip()
                    s = parts[sc].strip()
                    if (p and s
                            and "///" not in s
                            and s != "---"):
                        extra[p] = \
                            s.split(" ")[0]
            mapped.update({
                p: g for p, g
                in extra.items()
                if p in probe_ids
            })
        except Exception as e:
            log(f"  Annot error: {e}")

    log(f"  Probe→gene hits: {len(mapped)}")

    sub = expr_df.loc[
        [p for p in mapped
         if p in expr_df.index]
    ].copy()
    sub["symbol"] = [
        mapped[p] for p in sub.index
    ]
    sub["mean_expr"] = \
        sub.drop(columns=["symbol"]).mean(axis=1)
    sub = sub.sort_values(
        "mean_expr", ascending=False
    )
    sub = sub.drop_duplicates(
        subset=["symbol"], keep="first"
    )
    syms = sub["symbol"].values
    sub  = sub.drop(
        columns=["symbol", "mean_expr"]
    )
    sub.index = syms

    log(f"  Genes: {len(sub)}")

    # Metadata
    meta = pd.read_csv(S1_META, index_col=0)

    def extract_dkfz(title):
        parts = str(title).split("_")
        for i, p in enumerate(parts):
            if p.upper() == "DKFZ" \
                    and i + 1 < len(parts):
                return f"DKFZ_{parts[i+1]}"
        return title

    meta["sample_id"] = \
        meta["title"].apply(extract_dkfz)

    meta_cols = [c for c in [
        "disease_stage",
        "gleason_pattern_group",
        "source",
    ] if c in meta.columns]

    expr_T  = sub.T
    merged  = expr_T.join(
        meta.set_index("sample_id")[meta_cols],
        how="left",
    )
    merged["group"] = "UNKNOWN"
    if "disease_stage" in merged.columns:
        ds = merged[
            "disease_stage"
        ].fillna("").str.lower()
        merged.loc[
            ds.str.contains("cancer|tumor"),
            "group"
        ] = "TUMOR"
        merged.loc[
            ds.str.contains("benign|normal"),
            "group"
        ] = "NORMAL"

    for idx in merged[
        merged["group"] == "UNKNOWN"
    ].index:
        il = str(idx).lower()
        if "tumor" in il or "cancer" in il:
            merged.loc[idx, "group"] = "TUMOR"
        elif "benign" in il or "normal" in il:
            merged.loc[idx, "group"] = "NORMAL"

    tumor  = merged[
        merged["group"] == "TUMOR"
    ].copy()
    normal = merged[
        merged["group"] == "NORMAL"
    ].copy()

    log(f"  TUMOR  : {len(tumor)}")
    log(f"  NORMAL : {len(normal)}")

    return merged, tumor, normal

# ============================================================
# DEPTH SCORE — rebuild
# ============================================================

def build_depth(tumor):
    gene_cols = [
        c for c in tumor.columns
        if c in ALL_TARGET
    ]

    def norm01(s):
        mn, mx = s.min(), s.max()
        return (
            (s - mn) / (mx - mn)
            if mx > mn
            else pd.Series(0.0, index=s.index)
        )

    sw_avail = [
        g for g in SWITCH_GENES
        if g in gene_cols
    ]
    fa_avail = [
        g for g in FA_MARKERS
        if g in gene_cols
    ]

    depth = pd.Series(
        np.zeros(len(tumor)), index=tumor.index
    )
    comp  = 0
    if sw_avail:
        depth += (
            1 - norm01(tumor[sw_avail].mean(axis=1))
        )
        comp += 1
    if fa_avail:
        depth += norm01(
            tumor[fa_avail].mean(axis=1)
        )
        comp += 1
    if comp > 0:
        depth /= comp

    tumor = tumor.copy()
    tumor["block_depth"] = depth.values

    # ERG status from Script 1 threshold
    if "ERG" in tumor.columns:
        tumor["erg_status"] = np.where(
            tumor["ERG"] > ERG_THRESHOLD,
            "ERG_high", "ERG_low"
        )
        log(f"  ERG-high: "
            f"{(tumor['erg_status']=='ERG_high').sum()}")
        log(f"  ERG-low : "
            f"{(tumor['erg_status']=='ERG_low').sum()}")

    return tumor

# ============================================================
# ANALYSIS 1: GAP ANALYSIS
# Test circuit connections
# ============================================================

def gap_analysis(tumor):
    log("")
    log("=" * 65)
    log("ANALYSIS 1: GAP ANALYSIS")
    log("Testing circuit connections")
    log("=" * 65)
    log("")
    log("  KEY ARCHITECTURAL QUESTION:")
    log("  Is NKX3-1→ACPP circuit intact")
    log("  (like PAAD PTF1A→CTRC r=+0.754)")
    log("  OR broken (like MDS CEBPE→ELANE"
        " r=0.07)?")
    log("")

    gene_cols = [
        c for c in tumor.columns
        if c in ALL_TARGET
    ]

    confirmed = []
    not_conf  = []

    log(f"  {'Connection':<28} "
        f"{'r':>8}  {'p':>12}  "
        f"{'Dir':>4}  Result")
    log(f"  {'-'*70}")

    for (ga, gb, direction, desc) \
            in CIRCUIT_CONNECTIONS:
        if ga not in gene_cols \
                or gb not in gene_cols:
            log(f"  {ga}→{gb:<20} "
                f"{'MISSING':>8}")
            continue

        av = tumor[ga].values
        bv = tumor[gb].values

        try:
            rv, pv = stats.pearsonr(av, bv)
        except Exception:
            continue

        expected = (
            (direction == "+" and rv > 0)
            or (direction == "-" and rv < 0)
        )
        sig    = pv < 0.05
        result = (
            "CONFIRMED" if (sig and expected)
            else "NOT CONFIRMED"
            if not sig
            else "WRONG DIRECTION"
        )

        stars = (
            "***" if pv < 0.001
            else "**" if pv < 0.01
            else "*" if pv < 0.05
            else "ns"
        )
        conn_str = f"{ga}→{gb}"
        log(f"  {conn_str:<28} "
            f"{rv:>+8.4f}  "
            f"p={pv:.2e} {stars}  "
            f"{'exp'+direction:>4}  "
            f"{result}")

        if result == "CONFIRMED":
            confirmed.append(
                (ga, gb, rv, pv, desc)
            )
        else:
            not_conf.append(
                (ga, gb, rv, pv, desc)
            )

    log(f"\n  CONFIRMED    : {len(confirmed)}")
    log(f"  NOT CONFIRMED: {len(not_conf)}")
    log(f"  Total tested : "
        f"{len(confirmed)+len(not_conf)}")

    # The key architectural finding
    if any(ga == "NKX3-1" and gb == "ACPP"
           for ga, gb, *_ in confirmed):
        log(f"\n  NKX3-1→ACPP: CONFIRMED")
        log(f"  Architecture: INTACT")
        log(f"  Like PAAD PTF1A→CTRC")
        log(f"  Block is at NKX3-1 INPUT")
        log(f"  Restore NKX3-1 → ACPP executes")
    else:
        log(f"\n  NKX3-1→ACPP: NOT CONFIRMED")
        log(f"  Architecture: BROKEN or ABSENT")
        log(f"  Unlike PAAD (broken circuit)")
        log(f"  OR: NKX3-1 haploinsuff bypassed")
        log(f"  Check r value for interpretation")

    return confirmed, not_conf

# ============================================================
# ANALYSIS 2: ERG SUBTYPE
# ============================================================

def erg_subtype_analysis(tumor):
    log("")
    log("=" * 65)
    log("ANALYSIS 2: ERG SUBTYPE ANALYSIS")
    log("ERG-high (fusion+?) vs ERG-low")
    log("=" * 65)

    gene_cols = [
        c for c in tumor.columns
        if c in ALL_TARGET
    ]

    if "erg_status" not in tumor.columns:
        log("  ERG status not set — skip")
        return tumor

    erg_hi = tumor[
        tumor["erg_status"] == "ERG_high"
    ]
    erg_lo = tumor[
        tumor["erg_status"] == "ERG_low"
    ]

    log(f"\n  ERG-high: n={len(erg_hi)}")
    log(f"  ERG-low : n={len(erg_lo)}")

    # Depth by ERG status
    if "block_depth" in tumor.columns:
        dh = erg_hi["block_depth"]
        dl = erg_lo["block_depth"]
        log(f"\n  Block depth by ERG:")
        log(f"    ERG-high: "
            f"{dh.mean():.4f} ± {dh.std():.4f}")
        log(f"    ERG-low : "
            f"{dl.mean():.4f} ± {dl.std():.4f}")
        if len(dh) > 3 and len(dl) > 3:
            _, p_erg = stats.mannwhitneyu(
                dh, dl, alternative="two-sided"
            )
            log(f"    p (depth diff): {p_erg:.4f}")
            log(f"    ERG subtypes have "
                f"{'different' if p_erg < 0.05 else 'similar'} "
                f"depth distributions")

    # Key genes by ERG
    log(f"\n  Key genes ERG-high vs ERG-low:")
    log(f"  {'Gene':<12} "
        f"{'ERG-high':>10} "
        f"{'ERG-low':>10} "
        f"{'Change':>9}  p")
    log(f"  {'-'*54}")

    key_genes = [g for g in [
        "NKX3-1", "FOXA1", "KLK3",
        "AR", "TMPRSS2", "MYC", "EZH2",
        "MKI67", "ACPP", "MSMB",
        "HOXC6", "AMACR", "TP63",
        "KRT5", "PTEN", "AURKA",
    ] if g in gene_cols]

    erg_results = []
    for gene in key_genes:
        hv  = erg_hi[gene].values
        lv  = erg_lo[gene].values
        hm  = hv.mean()
        lm  = lv.mean()
        chg = (
            (hm - lm) / lm * 100
            if lm > 0.0001 else np.nan
        )
        _, pv = stats.mannwhitneyu(
            hv, lv, alternative="two-sided"
        )
        cs = (
            f"{chg:+.1f}%"
            if not np.isnan(chg) else "N/A"
        )
        stars = (
            "***" if pv < 0.001
            else "**" if pv < 0.01
            else "*" if pv < 0.05
            else "ns"
        )
        log(f"  {gene:<12} "
            f"{hm:>10.4f} "
            f"{lm:>10.4f} "
            f"{cs:>9}  "
            f"p={pv:.2e} {stars}")
        erg_results.append({
            "gene":    gene,
            "erg_hi":  hm,
            "erg_lo":  lm,
            "change":  chg,
            "p_value": pv,
        })

    # Gleason by ERG
    if "gleason_pattern_group" in tumor.columns:
        log(f"\n  Gleason by ERG status:")
        for status in ["ERG_high", "ERG_low"]:
            sub = tumor[
                tumor["erg_status"] == status
            ]
            gc = sub[
                "gleason_pattern_group"
            ].value_counts()
            log(f"    {status}: {dict(gc)}")

    pd.DataFrame(erg_results).to_csv(
        os.path.join(S2_DIR, "erg_results.csv"),
        index=False,
    )
    return tumor

# ============================================================
# ANALYSIS 3: 3-GENE SCORE
# ACPP (down) + HOXC6 (up) + AMACR (up)
# ============================================================

def three_gene_score(tumor):
    log("")
    log("=" * 65)
    log("ANALYSIS 3: 3-GENE ATTRACTOR SCORE")
    log("ACPP (switch) + HOXC6 + AMACR (FA)")
    log("=" * 65)

    gene_cols = [
        c for c in tumor.columns
        if c in ALL_TARGET
    ]
    genes_3 = [
        g for g in ["ACPP", "HOXC6", "AMACR"]
        if g in gene_cols
    ]
    if len(genes_3) < 2:
        log("  Insufficient genes — skip")
        return tumor

    log(f"  Genes available: {genes_3}")

    tumor = tumor.copy()

    def norm01(s):
        mn, mx = s.min(), s.max()
        return (
            (s - mn) / (mx - mn)
            if mx > mn
            else pd.Series(0.0, index=s.index)
        )

    score = pd.Series(
        np.zeros(len(tumor)), index=tumor.index
    )
    n = 0
    if "ACPP" in gene_cols:
        score += (1 - norm01(tumor["ACPP"]))
        n += 1
    if "HOXC6" in gene_cols:
        score += norm01(tumor["HOXC6"])
        n += 1
    if "AMACR" in gene_cols:
        score += norm01(tumor["AMACR"])
        n += 1
    if n > 0:
        score /= n

    tumor["score_3gene"] = score.values

    log(f"\n  3-gene score (n={len(tumor)}):")
    log(f"    Mean  : {score.mean():.4f}")
    log(f"    Median: {score.median():.4f}")
    log(f"    Std   : {score.std():.4f}")

    # vs block_depth
    if "block_depth" in tumor.columns:
        rv, pv = stats.pearsonr(
            tumor["block_depth"].values,
            score.values,
        )
        log(f"\n  3-gene score vs block_depth:")
        log(f"    r={rv:+.4f}  p={pv:.2e}")
        log(f"    {'Strong agreement' if abs(rv) > 0.7 else 'Moderate agreement' if abs(rv) > 0.5 else 'Weak agreement'}")

    # vs Gleason
    if "gleason_pattern_group" in tumor.columns:
        hi = tumor[
            tumor["gleason_pattern_group"]
            == "high"
        ]["score_3gene"]
        lo = tumor[
            tumor["gleason_pattern_group"]
            == "low"
        ]["score_3gene"]
        if len(hi) > 3 and len(lo) > 3:
            log(f"\n  3-gene score by Gleason:")
            log(f"    High: "
                f"{hi.mean():.4f} "
                f"± {hi.std():.4f} "
                f"(n={len(hi)})")
            log(f"    Low : "
                f"{lo.mean():.4f} "
                f"± {lo.std():.4f} "
                f"(n={len(lo)})")
            _, p3g = stats.mannwhitneyu(
                hi, lo, alternative="greater"
            )
            log(f"    High > Low: p={p3g:.4f}")
            log(f"    Result: "
                f"{'CONFIRMED' if p3g < 0.05 else 'NOT CONFIRMED'}")

    # vs ERG
    if "erg_status" in tumor.columns:
        eh = tumor[
            tumor["erg_status"] == "ERG_high"
        ]["score_3gene"]
        el = tumor[
            tumor["erg_status"] == "ERG_low"
        ]["score_3gene"]
        if len(eh) > 3 and len(el) > 3:
            log(f"\n  3-gene score by ERG:")
            log(f"    ERG-high: "
                f"{eh.mean():.4f} "
                f"± {eh.std():.4f}")
            log(f"    ERG-low : "
                f"{el.mean():.4f} "
                f"± {el.std():.4f}")
            _, p_e3 = stats.mannwhitneyu(
                eh, el, alternative="two-sided"
            )
            log(f"    p={p_e3:.4f}")

    return tumor

# ============================================================
# ANALYSIS 4: NKX3-1 FUNCTION GAP
# Is the NKX3-1→terminal gene circuit
# intact (PAAD-like) or broken (MDS-like)?
# ============================================================

def nkx31_function_gap(tumor):
    log("")
    log("=" * 65)
    log("ANALYSIS 4: NKX3-1 FUNCTION GAP")
    log("Is NKX3-1→terminal differentiation")
    log("circuit intact or broken?")
    log("=" * 65)
    log("")
    log("  PAAD reference:")
    log("  PTF1A→CTRC  r=+0.754  INTACT")
    log("  Block at INPUT — restore PTF1A")
    log("  → program executes normally")
    log("")
    log("  MDS reference:")
    log("  CEBPE→ELANE r=+0.07   BROKEN")
    log("  Block AT CONNECTION — restore TF")
    log("  → program still cannot execute")
    log("")
    log("  PRAD question:")
    log("  NKX3-1→ACPP/MSMB/KLK3 = ?")

    gene_cols = [
        c for c in tumor.columns
        if c in ALL_TARGET
    ]

    targets = [
        ("ACPP",  "terminal secretory"),
        ("MSMB",  "terminal secretory"),
        ("KLK3",  "AR target secretory"),
        ("KLK2",  "AR target secretory"),
        ("HOXB13","luminal identity"),
    ]

    log(f"\n  NKX3-1 → target gene correlations:")
    log(f"  {'Target':<12} {'r':>8}  "
        f"{'p':>12}  Architecture")
    log(f"  {'-'*54}")

    architecture = {}
    for tgt, desc in targets:
        if ("NKX3-1" not in gene_cols
                or tgt not in gene_cols):
            log(f"  {tgt:<12} MISSING")
            continue
        rv, pv = stats.pearsonr(
            tumor["NKX3-1"].values,
            tumor[tgt].values,
        )
        if rv > 0.3 and pv < 0.05:
            arch = "INTACT (like PAAD)"
        elif abs(rv) < 0.15:
            arch = "BROKEN (like MDS)"
        else:
            arch = "PARTIAL"

        stars = (
            "***" if pv < 0.001
            else "**" if pv < 0.01
            else "*" if pv < 0.05
            else "ns"
        )
        log(f"  {tgt:<12} {rv:>+8.4f}  "
            f"p={pv:.2e} {stars}  {arch}")
        architecture[tgt] = (rv, pv, arch)

    # Compare with EZH2→ACPP
    log(f"\n  EZH2 → target gene correlations")
    log(f"  (EZH2 is the proposed lock):")
    log(f"  {'Target':<12} {'r':>8}  "
        f"{'p':>12}  Role")
    log(f"  {'-'*52}")
    for tgt, desc in targets:
        if ("EZH2" not in gene_cols
                or tgt not in gene_cols):
            continue
        rv, pv = stats.pearsonr(
            tumor["EZH2"].values,
            tumor[tgt].values,
        )
        role = (
            "EZH2 SUPPRESSES" if rv < -0.2
            else "EZH2 ACTIVATES" if rv > 0.2
            else "no relationship"
        )
        stars = (
            "***" if pv < 0.001
            else "**" if pv < 0.01
            else "*" if pv < 0.05
            else "ns"
        )
        log(f"  {tgt:<12} {rv:>+8.4f}  "
            f"p={pv:.2e} {stars}  {role}")

    # Summary architecture
    log(f"\n  ARCHITECTURE SUMMARY:")
    n_intact  = sum(
        1 for v in architecture.values()
        if "INTACT" in v[2]
    )
    n_broken  = sum(
        1 for v in architecture.values()
        if "BROKEN" in v[2]
    )
    n_partial = sum(
        1 for v in architecture.values()
        if "PARTIAL" in v[2]
    )
    log(f"    INTACT  : {n_intact}")
    log(f"    BROKEN  : {n_broken}")
    log(f"    PARTIAL : {n_partial}")

    if n_intact >= 2:
        log(f"\n  VERDICT: Circuit INTACT")
        log(f"  NKX3-1 present → terminal")
        log(f"  genes follow normally")
        log(f"  Block is at NKX3-1 INPUT")
        log(f"  Haploinsufficiency = input")
        log(f"  below threshold for full")
        log(f"  terminal differentiation")
        log(f"  Restore NKX3-1 dose →")
        log(f"  ACPP/MSMB execute")
    elif n_broken >= 2:
        log(f"\n  VERDICT: Circuit BROKEN")
        log(f"  NKX3-1 present but cannot")
        log(f"  drive terminal genes")
        log(f"  Different target needed —")
        log(f"  not just NKX3-1 restoration")
    else:
        log(f"\n  VERDICT: MIXED/PARTIAL")
        log(f"  Circuit partially intact")
        log(f"  Some terminal genes follow")
        log(f"  NKX3-1 — others do not")

    return architecture

# ============================================================
# ANALYSIS 5: FOXA1 CIRCUIT ARCHITECTURE
# Is FOXA1 a driver or consequence?
# ============================================================

def foxa1_circuit(tumor):
    log("")
    log("=" * 65)
    log("ANALYSIS 5: FOXA1 CIRCUIT")
    log("FOXA1 elevated (+6.4%) in PRAD")
    log("Driver of FA or consequence of AR?")
    log("=" * 65)

    gene_cols = [
        c for c in tumor.columns
        if c in ALL_TARGET
    ]

    connections = [
        ("AR",    "FOXA1",  "AR→FOXA1"),
        ("FOXA1", "AMACR",  "FOXA1→AMACR"),
        ("FOXA1", "HOXC6",  "FOXA1→HOXC6"),
        ("FOXA1", "EZH2",   "FOXA1→EZH2"),
        ("FOXA1", "ACPP",   "FOXA1→ACPP"),
        ("FOXA1", "MSMB",   "FOXA1→MSMB"),
        ("FOXA1", "KLK3",   "FOXA1→KLK3"),
        ("FOXA1", "MYC",    "FOXA1→MYC"),
        ("FOXA1", "MKI67",  "FOXA1→MKI67"),
        ("AR",    "AMACR",  "AR→AMACR direct"),
        ("AR",    "HOXC6",  "AR→HOXC6 direct"),
        ("AR",    "EZH2",   "AR→EZH2"),
    ]

    log(f"\n  {'Connection':<20} "
        f"{'r':>8}  {'p':>12}  Interpretation")
    log(f"  {'-'*62}")

    foxa1_results = {}
    for ga, gb, label in connections:
        if ga not in gene_cols \
                or gb not in gene_cols:
            continue
        rv, pv = stats.pearsonr(
            tumor[ga].values,
            tumor[gb].values,
        )
        stars = (
            "***" if pv < 0.001
            else "**" if pv < 0.01
            else "*" if pv < 0.05
            else "ns"
        )
        interp = ""
        if pv < 0.05 and rv > 0:
            interp = "CONNECTED +"
        elif pv < 0.05 and rv < 0:
            interp = "CONNECTED -"
        else:
            interp = "not connected"

        log(f"  {label:<20} "
            f"{rv:>+8.4f}  "
            f"p={pv:.2e} {stars}  "
            f"{interp}")
        foxa1_results[label] = (rv, pv)

    # Key interpretation
    log(f"\n  KEY QUESTIONS:")
    ar_foxa1  = foxa1_results.get(
        "AR→FOXA1", (0, 1)
    )
    f1_amacr  = foxa1_results.get(
        "FOXA1→AMACR", (0, 1)
    )
    f1_hoxc6  = foxa1_results.get(
        "FOXA1→HOXC6", (0, 1)
    )
    ar_amacr  = foxa1_results.get(
        "AR→AMACR direct", (0, 1)
    )

    log(f"\n  AR→FOXA1: "
        f"r={ar_foxa1[0]:+.4f} "
        f"p={ar_foxa1[1]:.3f}")
    if ar_foxa1[1] < 0.05 and ar_foxa1[0] > 0:
        log(f"  → AR drives FOXA1 expression")
        log(f"    FOXA1 is downstream of AR")
    else:
        log(f"  → AR does NOT drive FOXA1")
        log(f"    FOXA1 elevated independently")

    log(f"\n  FOXA1→AMACR: "
        f"r={f1_amacr[0]:+.4f} "
        f"p={f1_amacr[1]:.3f}")
    if f1_amacr[1] < 0.05:
        log(f"  → FOXA1 connects to AMACR")
        if f1_amacr[0] > 0:
            log(f"    FOXA1 DRIVES false attractor")
        else:
            log(f"    FOXA1 suppresses AMACR")
            log(f"    (unexpected — note)")
    else:
        log(f"  → FOXA1 not connected to AMACR")
        log(f"    FOXA1 is consequence not driver")

    log(f"\n  FOXA1→HOXC6: "
        f"r={f1_hoxc6[0]:+.4f} "
        f"p={f1_hoxc6[1]:.3f}")
    if f1_hoxc6[1] < 0.05:
        log(f"  → FOXA1 connects to HOXC6")
    else:
        log(f"  → FOXA1 not connected to HOXC6")

    return foxa1_results

# ============================================================
# ANALYSIS 6: COMPLETE CIRCUIT MAP
# ============================================================

def circuit_summary(confirmed, not_conf,
                    architecture,
                    foxa1_results):
    log("")
    log("=" * 65)
    log("ANALYSIS 6: COMPLETE CIRCUIT MAP")
    log("All confirmed connections")
    log("=" * 65)

    log(f"\n  CONFIRMED CONNECTIONS:")
    log(f"  {'Connection':<28} "
        f"{'r':>8}  p")
    log(f"  {'-'*50}")
    for ga, gb, rv, pv, desc in confirmed:
        log(f"  {ga}→{gb:<22} "
            f"{rv:>+8.4f}  p={pv:.2e}")

    log(f"\n  NOT CONFIRMED:")
    for ga, gb, rv, pv, desc in not_conf:
        log(f"  {ga}→{gb:<22} "
            f"{rv:>+8.4f}  p={pv:.2e}  "
            f"({desc})")

    # Architecture verdict
    n_intact = sum(
        1 for v in architecture.values()
        if "INTACT" in v[2]
    )
    log(f"\n  ARCHITECTURE:")
    log(f"  NKX3-1→terminal: "
        f"{'INTACT' if n_intact >= 2 else 'BROKEN/PARTIAL'}")

    # Foxa1 verdict
    f1_amacr = foxa1_results.get(
        "FOXA1→AMACR", (0, 1)
    )
    f1_hoxc6 = foxa1_results.get(
        "FOXA1→HOXC6", (0, 1)
    )
    ar_foxa1 = foxa1_results.get(
        "AR→FOXA1", (0, 1)
    )

    log(f"\n  FOXA1 ROLE:")
    if (f1_amacr[1] < 0.05
            and f1_amacr[0] > 0):
        log(f"  FOXA1 drives AMACR")
        log(f"  FOXA1 is an FA DRIVER")
        log(f"  not just AR consequence")
    elif ar_foxa1[1] < 0.05:
        log(f"  FOXA1 follows AR")
        log(f"  FOXA1 is AR CONSEQUENCE")
        log(f"  not primary driver")
    else:
        log(f"  FOXA1 role unclear")
        log(f"  No strong connections found")

# ============================================================
# FIGURE
# ============================================================

def generate_figure(
    tumor, normal, confirmed,
    architecture, foxa1_results
):
    log("")
    log("--- Generating Script 2 figure ---")

    fig = plt.figure(figsize=(26, 20))
    fig.suptitle(
        "PRAD — False Attractor Circuit Analysis\n"
        "Script 2 | GSE32571 | "
        "59 PRAD | 39 Benign | "
        "OrganismCore 2026-03-01\n"
        "Gap analysis | ERG subtypes | "
        "NKX3-1 architecture | Doc 88b",
        fontsize=10, fontweight="bold", y=0.99,
    )
    gs = gridspec.GridSpec(
        3, 3, figure=fig,
        hspace=0.52, wspace=0.42,
    )

    gene_cols = [
        c for c in tumor.columns
        if c in ALL_TARGET
    ]
    clr = {
        "NORMAL":    "#2980b9",
        "TUMOR":     "#c0392b",
        "ERG_high":  "#8e44ad",
        "ERG_low":   "#e67e22",
        "high":      "#c0392b",
        "low":       "#f39c12",
    }

    # A — Circuit connections waterfall
    ax_a = fig.add_subplot(gs[0, 0])
    if confirmed:
        genes_c = [
            f"{ga}→{gb}"
            for ga, gb, *_ in confirmed[:14]
        ]
        vals_c  = [
            rv for _, _, rv, *_
            in confirmed[:14]
        ]
        cols_c  = [
            "#c0392b" if v < 0
            else "#27ae60"
            for v in vals_c
        ]
        ax_a.barh(genes_c, vals_c, color=cols_c)
        ax_a.axvline(
            0, color="black", linewidth=0.8
        )
        ax_a.set_xlabel(
            "Pearson r", fontsize=8
        )
        ax_a.set_title(
            "A — Circuit Connections\n"
            "Confirmed (p<0.05)",
            fontsize=9,
        )
        ax_a.tick_params(
            axis="y", labelsize=7
        )

    # B — Depth by Gleason and ERG
    ax_b = fig.add_subplot(gs[0, 1])
    categories = []
    depths     = []
    colors     = []
    if "gleason_pattern_group" in tumor.columns:
        for g, c in [
            ("high", clr["high"]),
            ("low",  clr["low"]),
        ]:
            sd = tumor[
                tumor["gleason_pattern_group"]
                == g
            ]["block_depth"]
            if len(sd) > 2:
                categories.append(
                    f"Gleason\n{g}"
                )
                depths.append(sd.values)
                colors.append(c)
    if "erg_status" in tumor.columns:
        for es, c in [
            ("ERG_high", clr["ERG_high"]),
            ("ERG_low",  clr["ERG_low"]),
        ]:
            sd = tumor[
                tumor["erg_status"] == es
            ]["block_depth"]
            if len(sd) > 2:
                categories.append(
                    es.replace("_", "\n")
                )
                depths.append(sd.values)
                colors.append(c)
    if categories:
        bp = ax_b.boxplot(
            depths,
            patch_artist=True,
            labels=categories,
        )
        for patch, c in zip(
            bp["boxes"], colors
        ):
            patch.set_facecolor(c)
            patch.set_alpha(0.7)
        ax_b.set_ylabel(
            "Block Depth Score", fontsize=8
        )
        ax_b.set_title(
            "B — Depth by Subtype\n"
            "Gleason and ERG status",
            fontsize=9,
        )

    # C — NKX3-1 vs ACPP scatter
    ax_c = fig.add_subplot(gs[0, 2])
    if ("NKX3-1" in gene_cols
            and "ACPP" in gene_cols):
        ax_c.scatter(
            tumor["NKX3-1"].values,
            tumor["ACPP"].values,
            color=clr["TUMOR"], alpha=0.6,
            s=30, label="PRAD",
        )
        rv, pv = stats.pearsonr(
            tumor["NKX3-1"].values,
            tumor["ACPP"].values,
        )
        m, b = np.polyfit(
            tumor["NKX3-1"].values,
            tumor["ACPP"].values, 1,
        )
        xs = np.linspace(
            tumor["NKX3-1"].min(),
            tumor["NKX3-1"].max(), 50,
        )
        ax_c.plot(
            xs, m*xs+b,
            color="black",
            linewidth=1.5, linestyle="--",
        )
        ax_c.set_xlabel(
            "NKX3-1 expression", fontsize=8
        )
        ax_c.set_ylabel(
            "ACPP expression", fontsize=8
        )
        arch_label = (
            "INTACT" if rv > 0.3 and pv < 0.05
            else "BROKEN" if abs(rv) < 0.15
            else "PARTIAL"
        )
        ax_c.set_title(
            f"C — NKX3-1 → ACPP Circuit\n"
            f"r={rv:+.3f} p={pv:.2e} "
            f"[{arch_label}]",
            fontsize=9,
        )

    # D — FOXA1 connections
    ax_d = fig.add_subplot(gs[1, 0])
    foxa1_genes = [
        g for g in [
            "AR", "AMACR", "HOXC6",
            "EZH2", "ACPP", "KLK3",
            "MYC", "MKI67",
        ] if g in gene_cols
    ]
    if foxa1_genes and "FOXA1" in gene_cols:
        f_vals = []
        f_cols = []
        for g in foxa1_genes:
            rv, pv = stats.pearsonr(
                tumor["FOXA1"].values,
                tumor[g].values,
            )
            f_vals.append(rv)
            f_cols.append(
                "#c0392b" if rv < 0
                else "#27ae60"
            )
        ax_d.barh(
            foxa1_genes, f_vals,
            color=f_cols,
        )
        ax_d.axvline(
            0, color="black", linewidth=0.8
        )
        ax_d.set_xlabel(
            "r with FOXA1", fontsize=8
        )
        ax_d.set_title(
            "D — FOXA1 Connections\n"
            "Driver or consequence?",
            fontsize=9,
        )
        ax_d.tick_params(
            axis="y", labelsize=8
        )

    # E — EZH2 connections
    ax_e = fig.add_subplot(gs[1, 1])
    ezh2_genes = [
        g for g in [
            "ACPP", "MSMB", "NKX3-1",
            "KLK3", "TP63", "KRT5",
            "HOXC6", "AMACR", "MKI67",
        ] if g in gene_cols
    ]
    if ezh2_genes and "EZH2" in gene_cols:
        e_vals = []
        e_cols = []
        for g in ezh2_genes:
            rv, pv = stats.pearsonr(
                tumor["EZH2"].values,
                tumor[g].values,
            )
            e_vals.append(rv)
            e_cols.append(
                "#c0392b" if rv < 0
                else "#27ae60"
            )
        ax_e.barh(
            ezh2_genes, e_vals,
            color=e_cols,
        )
        ax_e.axvline(
            0, color="black", linewidth=0.8
        )
        ax_e.set_xlabel(
            "r with EZH2", fontsize=8
        )
        ax_e.set_title(
            "E — EZH2 Connections\n"
            "EZH2 silences switch genes?",
            fontsize=9,
        )
        ax_e.tick_params(
            axis="y", labelsize=8
        )

    # F — ERG-high vs ERG-low key genes
    ax_f = fig.add_subplot(gs[1, 2])
    if "erg_status" in tumor.columns:
        erg_hi = tumor[
            tumor["erg_status"] == "ERG_high"
        ]
        erg_lo = tumor[
            tumor["erg_status"] == "ERG_low"
        ]
        key_g  = [g for g in [
            "ACPP", "MSMB", "HOXC6",
            "AMACR", "EZH2", "FOXA1",
            "NKX3-1", "TMPRSS2",
        ] if g in gene_cols]
        x = np.arange(len(key_g))
        w = 0.35
        mh = [erg_hi[g].mean() for g in key_g]
        ml = [erg_lo[g].mean() for g in key_g]
        ax_f.bar(
            x - w/2, mh, w,
            color=clr["ERG_high"],
            label="ERG-high", alpha=0.8,
        )
        ax_f.bar(
            x + w/2, ml, w,
            color=clr["ERG_low"],
            label="ERG-low", alpha=0.8,
        )
        ax_f.set_xticks(x)
        ax_f.set_xticklabels(
            key_g, rotation=45,
            ha="right", fontsize=7,
        )
        ax_f.set_title(
            "F — ERG Subtype\n"
            "High vs Low key genes",
            fontsize=9,
        )
        ax_f.legend(fontsize=7)

    # G — 3-gene score vs depth scatter
    ax_g = fig.add_subplot(gs[2, 0])
    if ("score_3gene" in tumor.columns
            and "block_depth" in tumor.columns):
        c_arr = [
            clr["high"]
            if g == "high" else clr["low"]
            for g in tumor.get(
                "gleason_pattern_group",
                pd.Series(
                    "unknown", index=tumor.index
                ),
            )
        ] if "gleason_pattern_group" \
            in tumor.columns \
            else [clr["TUMOR"]] * len(tumor)

        ax_g.scatter(
            tumor["block_depth"].values,
            tumor["score_3gene"].values,
            c=c_arr, alpha=0.7, s=35,
        )
        rv, pv = stats.pearsonr(
            tumor["block_depth"].values,
            tumor["score_3gene"].values,
        )
        ax_g.set_xlabel(
            "Block Depth Score", fontsize=8
        )
        ax_g.set_ylabel(
            "3-Gene Score", fontsize=8
        )
        ax_g.set_title(
            f"G — 3-Gene vs Depth\n"
            f"r={rv:+.3f} p={pv:.2e}",
            fontsize=9,
        )

    # H — Depth correlations top 15
    ax_h = fig.add_subplot(gs[2, 1])
    corrs = []
    for gene in gene_cols:
        if gene in [
            "block_depth", "score_3gene",
            "erg_status",
            "gleason_pattern_group",
            "disease_stage", "source",
            "group",
        ]:
            continue
        try:
            rv, pv = stats.pearsonr(
                tumor["block_depth"].values,
                tumor[gene].values,
            )
            corrs.append((gene, rv, pv))
        except Exception:
            pass
    corrs.sort(
        key=lambda x: abs(x[1]), reverse=True
    )
    if corrs:
        top = corrs[:15]
        gc  = [c[0] for c in top]
        vc  = [c[1] for c in top]
        cc  = [
            "#c0392b" if v < 0
            else "#27ae60"
            for v in vc
        ]
        ax_h.barh(gc, vc, color=cc)
        ax_h.axvline(
            0, color="black", linewidth=0.8
        )
        ax_h.set_xlabel(
            "r with depth", fontsize=8
        )
        ax_h.set_title(
            "H — Depth Correlations\n"
            "Top 15 genes",
            fontsize=9,
        )
        ax_h.tick_params(
            axis="y", labelsize=7
        )

    # I — Summary
    ax_i = fig.add_subplot(gs[2, 2])
    ax_i.axis("off")

    n_intact = sum(
        1 for v in architecture.values()
        if "INTACT" in v[2]
    )
    f1_amacr = foxa1_results.get(
        "FOXA1→AMACR", (0, 1)
    )
    f1_role  = (
        "FA DRIVER"
        if f1_amacr[1] < 0.05
        and f1_amacr[0] > 0
        else "AR consequence"
    )
    n_conf = len(confirmed)

    summary = (
        "I — SCRIPT 2 SUMMARY\n"
        "─────────────────────────\n"
        "Dataset: GSE32571\n"
        "  59 PRAD | 39 Benign\n\n"
        f"Circuit connections:\n"
        f"  Confirmed: {n_conf}\n\n"
        f"NKX3-1→ACPP:\n"
        f"  {'INTACT' if n_intact >= 2 else 'BROKEN'}\n\n"
        f"FOXA1 role: {f1_role}\n\n"
        "EZH2 lock:\n"
        "  4th solid cancer\n"
        "  r=+0.426 with depth\n\n"
        "Switch genes:\n"
        "  ACPP r=-0.595\n"
        "  MSMB r=-0.551\n\n"
        "FA markers:\n"
        "  HOXC6 +34.7%\n"
        "  AMACR +36.1%\n\n"
        "Gleason depth: p=0.0024\n"
        "ERG bimodal: confirmed\n\n"
        "Framework: OrganismCore\n"
        "Doc: 88b | 2026-03-01"
    )
    ax_i.text(
        0.03, 0.97, summary,
        transform=ax_i.transAxes,
        fontsize=8.5,
        verticalalignment="top",
        fontfamily="monospace",
        bbox=dict(
            boxstyle="round",
            facecolor="#f8f8f8",
            edgecolor="#cccccc",
        ),
    )

    outpath = os.path.join(
        S2_DIR, "prad_s2_circuit.png"
    )
    plt.savefig(
        outpath, dpi=150,
        bbox_inches="tight",
    )
    log(f"\n  Figure saved: {outpath}")
    plt.close()

# ============================================================
# MAIN
# ============================================================

def main():
    log("=" * 65)
    log("PROSTATE ADENOCARCINOMA")
    log("FALSE ATTRACTOR — SCRIPT 2")
    log("Circuit Analysis")
    log("Dataset: GSE32571")
    log("Framework: OrganismCore")
    log("Doc: 88b | Date: 2026-03-01")
    log("=" * 65)
    log("")
    log("  SCRIPT 2 OBJECTIVES:")
    log("  1. Circuit connections (gap analysis)")
    log("  2. ERG subtype depth analysis")
    log("  3. 3-gene attractor score")
    log("  4. NKX3-1 function gap test")
    log("     INTACT (PAAD-like) or")
    log("     BROKEN (MDS-like)?")
    log("  5. FOXA1 circuit architecture")
    log("     Driver or AR consequence?")

    log("\n=== RELOAD DATA ===")
    merged, tumor, normal = reload_data()

    log("\n=== BUILD DEPTH SCORE ===")
    tumor = build_depth(tumor)

    log("\n=== ANALYSIS 1: GAP ANALYSIS ===")
    confirmed, not_conf = gap_analysis(tumor)

    log("\n=== ANALYSIS 2: ERG SUBTYPE ===")
    tumor = erg_subtype_analysis(tumor)

    log("\n=== ANALYSIS 3: 3-GENE SCORE ===")
    tumor = three_gene_score(tumor)

    log("\n=== ANALYSIS 4: NKX3-1 GAP ===")
    architecture = nkx31_function_gap(tumor)

    log("\n=== ANALYSIS 5: FOXA1 CIRCUIT ===")
    foxa1_results = foxa1_circuit(tumor)

    log("\n=== ANALYSIS 6: CIRCUIT SUMMARY ===")
    circuit_summary(
        confirmed, not_conf,
        architecture, foxa1_results,
    )

    log("\n=== FIGURE ===")
    generate_figure(
        tumor, normal, confirmed,
        architecture, foxa1_results,
    )

    write_log()
    log(f"\n  Log: {LOG_FILE}")
    log(f"  Outputs: {S2_DIR}")
    log("\n=== SCRIPT 2 COMPLETE ===")


if __name__ == "__main__":
    main()
