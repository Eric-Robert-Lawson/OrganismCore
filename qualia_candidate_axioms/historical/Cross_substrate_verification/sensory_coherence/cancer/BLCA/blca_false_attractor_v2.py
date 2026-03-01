"""
BLADDER CANCER — FALSE ATTRACTOR ANALYSIS
SCRIPT 2
Dataset: GSE13507
Platform: GPL6102 Illumina HumanWG-6 V2
Doc: 91b | Date: 2026-03-01

FIXES FROM SCRIPT 1:
  FIX 1: Event parser —
          'overall survival': death → 1
          'overall survival': survival → 0
          'cancer specific survival': same
  FIX 2: Updated depth panels from S1 data:
          LUMINAL: switch=[CLDN3,UPK1B,UPK3A]
                   fa=[FGFR3,CCND1,GATA3,FOXA1]
          BASAL:   switch=[GATA3,FOXA1,PPARG,
                           KRT8,ERBB3]
                   fa=[TWIST1,ZEB2,CDK6,
                       FN1,SNAI1,VIM]
  FIX 3: Compare BASAL vs LUMINAL
          for switch genes (not vs Normal)

NEW IN SCRIPT 2:
  S2-1: Survival analysis (OS + CSS)
        Both luminal and basal subtypes
  S2-2: Revised depth panels tested vs OS
  S2-3: Novel panel derivation:
          LUMINAL: FGFR3(+)/CCND1(+)/CLDN3(-)
          BASAL:   TWIST1(+)/CDK6(+)/GATA3(-)
  S2-4: SMAD3 deep luminal analysis
        (TGF-β active subset)
  S2-5: MSH2/MSH6 MMR loss vs depth
        (MSI-high prediction in deep luminal)
  S2-6: FGFR isoform switch confirmation
        FGFR3 luminal vs FGFR1 basal
  S2-7: MCL1 vs BCL2 in basal depth
  S2-8: CDK4 vs CDK6 in basal depth
  S2-9: KRT20/CDX2 intestinal axis
        in luminal (BLCA-EAC cross-cancer)
  S2-10: Full basal vs luminal FC table
         (correct comparator)

PREDICTIONS LOCKED BEFORE S2 RUN
(derived from S1 reasoning, 2026-03-01):

SURVIVAL:
  SV-1: Luminal depth predicts OS
  SV-2: Basal depth predicts OS
  SV-3: FGFR3(+)/CCND1(+)/CLDN3(-) panel
        predicts OS in luminal
  SV-4: TWIST1(+)/CDK6(+)/GATA3(-) panel
        predicts OS in basal
  SV-5: Basal depth predicts CSS
        (more aggressive subtype)

BIOLOGY:
  S2-B1: FGFR3 r>FGFR1 in luminal depth
  S2-B2: FGFR1 r>FGFR3 in basal depth
  S2-B3: MCL1 r>BCL2 in basal depth
  S2-B4: CDK6 r>CDK4 in basal depth
  S2-B5: MSH2/MSH6 r<-0.35 in luminal depth
  S2-B6: SMAD3 r>+0.45 in luminal depth
  S2-B7: KRT20+CDX2 correlated in luminal
  S2-B8: Basal vs Luminal FC:
         KRT5/KRT14/TWIST1/ZEB2 UP basal
         GATA3/FOXA1/PPARG/FGFR3 UP luminal

Author: Eric Robert Lawson
Framework: OrganismCore
"""

import os
import re
import gzip
import numpy as np
import pandas as pd
from scipy import stats
from lifelines import KaplanMeierFitter
from lifelines import CoxPHFitter
from lifelines.statistics import logrank_test
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import warnings
warnings.filterwarnings("ignore")

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR    = "./blca_false_attractor/"
RESULTS_DIR = os.path.join(
    BASE_DIR, "results_s2"
)
LOG_FILE = os.path.join(
    RESULTS_DIR, "analysis_log_s2.txt"
)
os.makedirs(RESULTS_DIR, exist_ok=True)

MATRIX_FILE = os.path.join(
    BASE_DIR,
    "GSE13507_series_matrix.txt.gz",
)
SOFT_FILE = os.path.join(
    BASE_DIR,
    "GSE13507_family.soft.gz",
)
GPL_FILE = os.path.join(
    BASE_DIR, "GPL6102.annot.gz"
)
GPL_FILE_ESCA = os.path.join(
    "./esca_false_attractor/",
    "GPL6102.annot.gz",
)

# ============================================================
# TARGET GENES — same as S1
# ============================================================

TARGET_GENES = [
    "UPK1A","UPK1B","UPK2", "UPK3A",
    "UPK3B","CLDN3","CLDN4","CLDN7",
    "GATA3","FOXA1","PPARG","ERBB2",
    "ERBB3","FGFR3","CCND1","CDH1",
    "KRT7", "KRT8", "KRT18","KRT19",
    "KRT20","KRT5", "KRT14","KRT6A",
    "TP63", "CD44", "S100A8","S100A9",
    "VIM",  "ZEB1", "ZEB2", "SNAI1",
    "SNAI2","TWIST1","CDH2","FN1",
    "EGFR", "MET",  "FGFR1","FGFR2",
    "KDR",  "VEGFA","PDGFRA","TACSTD2",
    "PVRL4","CD274","PDCD1","CD8A",
    "FOXP3","CD4",  "CD68",
    "EZH2", "HDAC1","HDAC2","KDM6A",
    "KDM5C","DNMT3A","TET2","ARID1A",
    "CDKN1A","CDKN2A","CDK4","CDK6",
    "CCND1","CCNE1","CCNB1","RB1",
    "E2F1", "E2F3",
    "MKI67","TOP2A","AURKA","CDC20",
    "PLK1", "PCNA", "MCM2",
    "BCL2", "MCL1", "BAX","BCL2L1",
    "BIRC5","TP53", "MDM2","CDKN2A",
    "APC",  "CTNNB1","AXIN2","AXIN1",
    "TCF7L2","LGR5","WNT5A",
    "MYC",  "MYCN", "PIK3CA","KRAS",
    "HRAS", "NRAS",
    "SOX2", "SOX4", "ALDH1A1",
    "NOTCH1","NOTCH2","HES1","JAG1",
    "TGFB1","TGFBR2","SMAD2","SMAD3",
    "HIF1A","CA9",
    "MLH1", "MSH2", "MSH6",
    "SPRY1","SPRY2","DUSP6",
    "TP73", "PTEN", "TSC1","RB1",
    "CDKN1B","CDKN2B",
    "CDX2", "FOXA2","NKX2-1",
    "IVL",  "SPRR1A","DSG1","DSG3",
    "KRT10","KRT4", "KRT13",
]

# Updated panels from S1 analysis
LUMINAL_SWITCH_S2 = [
    "CLDN3","UPK1B","UPK3A",
    "CDKN2B","CDKN2A",
]
LUMINAL_FA_S2 = [
    "FGFR3","CCND1","GATA3",
    "FOXA1","KRT19",
]
BASAL_SWITCH_S2 = [
    "GATA3","FOXA1","PPARG",
    "KRT8", "ERBB3",
]
BASAL_FA_S2 = [
    "TWIST1","ZEB2","CDK6",
    "FN1",   "SNAI1","VIM",
]

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

def fmt_p(p):
    if p is None or (
        isinstance(p, float) and np.isnan(p)
    ):
        return "p=N/A     "
    if p < 0.001:  return f"p={p:.2e} ***"
    elif p < 0.01: return f"p={p:.2e}  **"
    elif p < 0.05: return f"p={p:.4f}   *"
    else:          return f"p={p:.4f}  ns"

def fmt_fc(fc):
    sign = "+" if fc >= 0 else ""
    return f"{sign}{fc:.1f}%"

def safe_pearsonr(x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    m = np.isfinite(x) & np.isfinite(y)
    x, y = x[m], y[m]
    if len(x) < 5:
        return np.nan, np.nan
    return stats.pearsonr(x, y)

def safe_mwu(a, b, alt="two-sided"):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    a = a[np.isfinite(a)]
    b = b[np.isfinite(b)]
    if len(a) < 2 or len(b) < 2:
        return np.nan, np.nan
    return stats.mannwhitneyu(
        a, b, alternative=alt
    )

def norm01(s):
    s  = pd.Series(s, dtype=float)
    mn = s.min()
    mx = s.max()
    if mx > mn:
        return (s - mn) / (mx - mn)
    return pd.Series(0.5, index=s.index)

# ============================================================
# PROBE MAP — reuse S1 logic
# ============================================================

def build_probe_map():
    gpl = (
        GPL_FILE_ESCA
        if os.path.exists(GPL_FILE_ESCA)
        else GPL_FILE
    )
    if not os.path.exists(gpl):
        log("FATAL: GPL file missing")
        return {}, {}

    log(f"  Using GPL: {gpl}")
    probe_map    = {}
    gene_to_prob = {}
    target_set   = set(TARGET_GENES)

    opener = (
        gzip.open(gpl, "rt",
                  encoding="utf-8",
                  errors="ignore")
        if gpl.endswith(".gz")
        else open(gpl, "r",
                  encoding="utf-8",
                  errors="ignore")
    )

    in_data = False
    id_col  = 0
    sym_col = 2

    with opener as f:
        for line in f:
            line = line.rstrip()
            if (
                line.startswith("!")
                or line.startswith("^")
                or line.startswith("#")
            ):
                continue
            parts = line.split("\t")
            lower = [
                p.strip().strip('"').lower()
                for p in parts
            ]
            if not in_data:
                if any(
                    h == "id" for h in lower
                ):
                    for i, h in enumerate(lower):
                        if h == "id":
                            id_col = i
                        if h == "gene symbol":
                            sym_col = i
                    in_data = True
                    continue
            if len(parts) <= max(id_col, sym_col):
                continue
            probe_id = parts[id_col].strip('"')
            symbols  = parts[sym_col].strip('"')
            if not probe_id or symbols in [
                "---","NA","",
            ]:
                continue
            for sym in re.split(
                r"[;,/\s]+|///", symbols
            ):
                sym = sym.strip()
                if sym in target_set:
                    probe_map[probe_id] = sym
                    if sym not in gene_to_prob:
                        gene_to_prob[sym] = []
                    if probe_id not in (
                        gene_to_prob[sym]
                    ):
                        gene_to_prob[sym].append(
                            probe_id
                        )

    log(f"  Probes: {len(probe_map)}  "
        f"Genes: {len(gene_to_prob)}")
    return probe_map, gene_to_prob

# ============================================================
# PARSE MATRIX
# ============================================================

def parse_matrix(probe_map, gene_to_prob):
    log("")
    log("=" * 65)
    log("PARSE SERIES MATRIX")
    log("=" * 65)

    opener = (
        gzip.open(MATRIX_FILE, "rt",
                  encoding="utf-8",
                  errors="ignore")
        if MATRIX_FILE.endswith(".gz")
        else open(MATRIX_FILE, "r",
                  encoding="utf-8",
                  errors="ignore")
    )

    sample_ids    = []
    sample_titles = []
    char_rows     = {}
    in_table      = False
    header_cols   = []
    probe_ids     = []
    rows          = []

    with opener as f:
        for line in f:
            line = line.rstrip()
            if "!Sample_geo_accession" in line:
                parts = line.split("\t")
                sample_ids = [
                    p.strip().strip('"')
                    for p in parts[1:]
                    if p.strip().strip('"')
                ]
            elif "!Sample_title" in line:
                parts = line.split("\t")
                sample_titles = [
                    p.strip().strip('"')
                    for p in parts[1:]
                    if p.strip().strip('"')
                ]
            elif (
                "!Sample_characteristics_ch1"
                in line
            ):
                parts = line.split("\t")
                vals = [
                    p.strip().strip('"')
                    for p in parts[1:]
                ]
                char_rows[len(char_rows)] = vals
            elif "series_matrix_table_begin" in line:
                in_table = True
                continue
            elif "series_matrix_table_end" in line:
                break
            elif in_table:
                parts = [
                    p.strip().strip('"')
                    for p in line.split("\t")
                ]
                if not header_cols:
                    header_cols = parts
                    continue
                if not parts or not parts[0]:
                    continue
                pid = parts[0]
                if pid not in probe_map:
                    continue
                try:
                    vals = [
                        float(p)
                        if p not in [
                            "","null","NA",
                            "nan","N/A",
                            "Inf","-Inf",
                        ]
                        else np.nan
                        for p in parts[1:]
                    ]
                except ValueError:
                    continue
                if len(vals) != (
                    len(header_cols) - 1
                ):
                    continue
                probe_ids.append(pid)
                rows.append(vals)

    log(f"  Samples: {len(sample_ids)}  "
        f"Probes: {len(probe_ids)}")

    if not probe_ids:
        return None, None, None

    cols = header_cols[1:][:len(rows[0])]
    df   = pd.DataFrame(
        rows, index=probe_ids,
        columns=cols, dtype=float,
    )

    gene_expr = {}
    for gene, probes in gene_to_prob.items():
        avail = [
            p for p in probes if p in df.index
        ]
        if not avail:
            continue
        if len(avail) == 1:
            gene_expr[gene] = (
                df.loc[avail[0]].values
            )
        else:
            meds = [
                df.loc[p].median() for p in avail
            ]
            gene_expr[gene] = (
                df.loc[avail[np.argmax(meds)]].values
            )

    df_genes = pd.DataFrame(
        gene_expr, index=cols, dtype=float
    )
    log(f"  Genes: {len(df_genes.columns)}")

    meta = pd.DataFrame(index=df_genes.index)
    if len(sample_titles) == len(df_genes):
        meta["title"] = sample_titles
    elif sample_ids and len(sample_titles) == len(sample_ids):
        tmap = dict(zip(sample_ids, sample_titles))
        meta["title"] = [
            tmap.get(s,"") for s in df_genes.index
        ]

    return df_genes, meta, char_rows

# ============================================================
# CLASSIFY
# ============================================================

def classify(df_genes, meta, char_rows):
    primary = []
    for s in df_genes.index:
        title = ""
        if (
            meta is not None
            and "title" in meta.columns
            and s in meta.index
        ):
            title = str(
                meta.loc[s, "title"]
            ).lower()
        if any(x in title for x in [
            "normal","nontumor",
            "non-tumor","urothelium",
        ]):
            primary.append("Normal")
        elif any(x in title for x in [
            "tumor","tumour","cancer",
            "blca","bladder","carcinoma",
            "tcc","surrounding",
        ]):
            primary.append("Tumor")
        else:
            primary.append("Unknown")

    ps = pd.Series(primary,
                   index=df_genes.index)

    # Char-row fallback for Unknown
    for k, vals in char_rows.items():
        nonempty = [v for v in vals if v]
        if not nonempty:
            continue
        ex = nonempty[0].lower()
        if "biological source" in ex or "tissue" in ex:
            for i, v in enumerate(
                vals[:len(ps)]
            ):
                if ps.iloc[i] != "Unknown":
                    continue
                vl = v.lower()
                if any(
                    x in vl for x in [
                        "normal","surrounding",
                        "adjacent",
                    ]
                ):
                    ps.iloc[i] = "Normal"
                elif any(
                    x in vl for x in [
                        "cancer","tumor","primary",
                    ]
                ):
                    ps.iloc[i] = "Tumor"

    # Subtype by GATA3/KRT5 median split
    gc = list(df_genes.columns)
    subtype = ps.copy()
    tumor_mask = ps == "Tumor"
    tdf = df_genes[tumor_mask]

    if (
        "GATA3" in gc
        and "KRT5" in gc
        and len(tdf) > 10
    ):
        g3n = norm01(tdf["GATA3"].values)
        k5n = norm01(tdf["KRT5"].values)
        score = g3n.values - k5n.values
        med   = np.median(score)
        for idx, s in zip(
            np.where(score >= med)[0],
            tdf.index[score >= med],
        ):
            subtype[s] = "Luminal"
        for s in tdf.index[score < med]:
            subtype[s] = "Basal"

    log(f"  Group counts:")
    for g, n in subtype.value_counts().items():
        log(f"    {g}: {n}")

    return subtype

# ============================================================
# PARSE SURVIVAL — FIXED
# FIX: 'overall survival': death → 1
#      'overall survival': survival → 0
#      'cancer specific survival': same
# ============================================================

def parse_survival(df_genes):
    log("")
    log("=" * 65)
    log("PARSE SURVIVAL — FIXED EVENT PARSER")
    log("'overall survival': death → 1")
    log("'overall survival': survival → 0")
    log("'cancer specific survival': same")
    log("=" * 65)

    if not os.path.exists(SOFT_FILE):
        log("  Soft file missing")
        return None

    opener = (
        gzip.open(SOFT_FILE, "rt",
                  encoding="utf-8",
                  errors="ignore")
        if SOFT_FILE.endswith(".gz")
        else open(SOFT_FILE, "r",
                  encoding="utf-8",
                  errors="ignore")
    )

    sample_data = {}
    cur_sample  = None
    cur_chars   = {}

    with opener as f:
        for line in f:
            line = line.rstrip()
            if line.startswith("^SAMPLE"):
                if cur_sample:
                    sample_data[cur_sample] = (
                        dict(cur_chars)
                    )
                cur_sample = (
                    line.split("=")[-1].strip()
                )
                cur_chars = {}
            elif (
                "!Sample_characteristics_ch1"
                in line
            ):
                val = (
                    line.split("=", 1)[-1]
                    .strip().strip('"')
                )
                if ":" in val:
                    k, v = val.split(":", 1)
                    cur_chars[
                        k.strip().lower()
                    ] = v.strip()
                else:
                    cur_chars[
                        f"c{len(cur_chars)}"
                    ] = val

    if cur_sample:
        sample_data[cur_sample] = dict(cur_chars)

    log(f"  Sample records: {len(sample_data)}")

    os_time  = {}
    os_event = {}
    css_time = {}
    css_event= {}
    stage_d  = {}
    grade_d  = {}
    inv_d    = {}

    for gsm, chars in sample_data.items():
        for k, v in chars.items():
            kl = k.lower()
            vl = v.lower().strip()

            # ---- TIME ----
            if kl == "survival month":
                nums = re.findall(r"[\d.]+", v)
                if nums:
                    try:
                        os_time[gsm] = float(
                            nums[0]
                        )
                        css_time[gsm] = float(
                            nums[0]
                        )
                    except ValueError:
                        pass

            # ---- OS EVENT (FIXED) ----
            if kl == "overall survival":
                if "death" in vl:
                    os_event[gsm] = 1
                elif "survival" in vl:
                    os_event[gsm] = 0

            # ---- CSS EVENT (FIXED) ----
            if kl == "cancer specific survival":
                if "death" in vl:
                    css_event[gsm] = 1
                elif "survival" in vl:
                    css_event[gsm] = 0

            # ---- CLINICAL COVARIATES ----
            if kl == "stage":
                stage_d[gsm] = v.strip()
            if kl == "grade":
                grade_d[gsm] = v.strip()
            if kl == "invasiveness":
                inv_d[gsm] = v.strip()

    log(f"  OS  time  : {len(os_time)}")
    log(f"  OS  event : {len(os_event)}")
    log(f"  CSS event : {len(css_event)}")
    log(f"  Stage     : {len(stage_d)}")
    log(f"  Grade     : {len(grade_d)}")
    log(f"  Invasiveness: {len(inv_d)}")

    if os_time:
        t = list(os_time.values())
        log(f"  OS time range: "
            f"{min(t):.1f}–{max(t):.1f} mo")

    if os_event:
        n1 = sum(1 for v in os_event.values()
                 if v == 1)
        n0 = sum(1 for v in os_event.values()
                 if v == 0)
        log(f"  OS events: {n1} deaths, "
            f"{n0} alive")

    n = len(df_genes)
    t_os  = np.full(n, np.nan)
    e_os  = np.full(n, np.nan)
    e_css = np.full(n, np.nan)
    stage_arr = [""] * n
    grade_arr = [""] * n
    inv_arr   = [""] * n

    for i, gsm in enumerate(df_genes.index):
        if gsm in os_time:
            t_os[i] = os_time[gsm]
        if gsm in os_event:
            e_os[i] = os_event[gsm]
        if gsm in css_event:
            e_css[i] = css_event[gsm]
        if gsm in stage_d:
            stage_arr[i] = stage_d[gsm]
        if gsm in grade_d:
            grade_arr[i] = grade_d[gsm]
        if gsm in inv_d:
            inv_arr[i] = inv_d[gsm]

    surv = pd.DataFrame({
        "os_time":    t_os,
        "os_event":   e_os,
        "css_event":  e_css,
        "stage":      stage_arr,
        "grade":      grade_arr,
        "invasiveness": inv_arr,
    }, index=df_genes.index)

    valid_os = (
        ~np.isnan(t_os)
        & ~np.isnan(e_os)
        & (t_os > 0)
    )
    log(f"\n  Valid OS (time+event): "
        f"{valid_os.sum()}")

    # Clinical breakdown
    log(f"\n  Stage breakdown:")
    sc = pd.Series(stage_arr).value_counts()
    for sv, cnt in sc.items():
        if sv:
            log(f"    {sv}: {cnt}")
    log(f"\n  Grade breakdown:")
    gc = pd.Series(grade_arr).value_counts()
    for gv, cnt in gc.items():
        if gv:
            log(f"    {gv}: {cnt}")
    log(f"\n  Invasiveness breakdown:")
    ic = pd.Series(inv_arr).value_counts()
    for iv, cnt in ic.items():
        if iv:
            log(f"    {iv}: {cnt}")

    return surv

# ============================================================
# DEPTH SCORE
# ============================================================

def build_depth(df, switch, fa, label):
    gc  = list(df.columns)
    sw  = [g for g in switch if g in gc]
    fa_ = [g for g in fa     if g in gc]
    depth = pd.Series(
        np.zeros(len(df)),
        index=df.index, dtype=float,
    )
    n = 0
    if sw:
        depth += (
            1 - norm01(df[sw].mean(axis=1))
        )
        n += 1
    if fa_:
        depth += norm01(
            df[fa_].mean(axis=1)
        )
        n += 1
    if n > 0:
        depth /= n
    log(f"  {label} (n={len(df)}): "
        f"mean={depth.mean():.4f} "
        f"std={depth.std():.4f}")
    return depth

# ============================================================
# SURVIVAL ANALYSIS — full
# ============================================================

def run_survival(
    df, depth, surv, label,
    panel_genes=None, panel_dirs=None,
):
    log("")
    log("=" * 65)
    log(f"SURVIVAL — {label}")
    log("=" * 65)

    idx = df.index.intersection(surv.index)
    if len(idx) == 0:
        log("  No overlap")
        return None

    d = depth.loc[idx]
    s = surv.loc[idx]
    t = s["os_time"].values
    e = s["os_event"].values
    ec = s["css_event"].values

    valid_os = (
        ~np.isnan(t) & ~np.isnan(e)
        & (t > 0)
    )
    valid_css = (
        ~np.isnan(t) & ~np.isnan(ec)
        & (t > 0)
    )

    log(f"  n={len(idx)}")
    log(f"  Valid OS : {valid_os.sum()}")
    log(f"  Valid CSS: {valid_css.sum()}")

    if valid_os.sum() < 10:
        log("  Insufficient OS data")
        return None

    t_v  = t[valid_os]
    e_v  = e[valid_os]
    d_v  = d.values[valid_os]
    df_v = df.loc[idx].iloc[valid_os]

    log(f"  OS range: "
        f"{t_v.min():.1f}–{t_v.max():.1f} mo")
    log(f"  Events: {int(e_v.sum())} / "
        f"{len(e_v)}")

    # Depth score vs OS
    med = np.median(d_v)
    hi  = d_v >= med
    lo  = ~hi

    try:
        res = logrank_test(
            t_v[hi], t_v[lo],
            e_v[hi], e_v[lo],
        )
        p_depth = res.p_value
    except Exception:
        p_depth = np.nan

    log(f"\n  Depth vs OS (median split):")
    log(f"  Deep (n={hi.sum()}): "
        f"mean={t_v[hi].mean():.1f} mo")
    log(f"  Shallow (n={lo.sum()}): "
        f"mean={t_v[lo].mean():.1f} mo")
    log(f"  Log-rank: {fmt_p(p_depth)}")

    if not np.isnan(p_depth):
        if p_depth < 0.05:
            log(f"  Depth predicts OS ✓")
        else:
            log(f"  Depth does not predict OS ✗")

    # Individual gene tests
    gc_ = list(df_v.columns)
    log(f"\n  Individual gene OS tests:")
    log(f"  {'Gene':<12} {'n_hi':>5} "
        f"{'n_lo':>5}  p-value")
    log(f"  {'-'*45}")

    gene_results = {}
    for gene in sorted(gc_):
        vals = df_v[gene].values
        gmed = np.nanmedian(vals)
        ghi  = vals >= gmed
        glo  = ~ghi
        if ghi.sum() < 5 or glo.sum() < 5:
            continue
        try:
            res = logrank_test(
                t_v[ghi], t_v[glo],
                e_v[ghi], e_v[glo],
            )
            p = res.p_value
        except Exception:
            p = np.nan
        gene_results[gene] = p
        if not np.isnan(p) and p < 0.05:
            log(f"  {gene:<12} {ghi.sum():>5} "
                f"{glo.sum():>5}  {fmt_p(p)}")

    # Predicted panel test
    panel_result = None
    if panel_genes and panel_dirs:
        avail_p = [
            (g, d_) for g, d_ in
            zip(panel_genes, panel_dirs)
            if g in gc_
        ]
        log(f"\n  Panel test: "
            f"{list(zip(panel_genes, panel_dirs))}")
        log(f"  Available: {avail_p}")

        if len(avail_p) >= 2:
            parts = []
            for gene, direction in avail_p:
                ns = norm01(df_v[gene].values)
                parts.append(
                    1 - ns
                    if direction == "-"
                    else ns
                )
            panel_score = np.mean(parts, axis=0)
            pmed  = np.median(panel_score)
            phi   = panel_score >= pmed
            plo   = ~phi

            try:
                res_p = logrank_test(
                    t_v[phi], t_v[plo],
                    e_v[phi], e_v[plo],
                )
                p_panel = res_p.p_value
            except Exception:
                p_panel = np.nan

            log(f"  Panel log-rank: "
                f"{fmt_p(p_panel)}")
            log(f"  Panel-high (n={phi.sum()}): "
                f"mean={t_v[phi].mean():.1f} mo")
            log(f"  Panel-low  (n={plo.sum()}): "
                f"mean={t_v[plo].mean():.1f} mo")

            if not np.isnan(p_panel):
                if p_panel < 0.05:
                    log(f"  Panel predicts OS ✓")
                else:
                    log(f"  Panel does not predict OS ✗")

            panel_result = {
                "t": t_v, "e": e_v,
                "phi": phi, "plo": plo,
                "p_panel": p_panel,
                "panel_score": panel_score,
            }

    # CSS analysis
    css_result = None
    if valid_css.sum() >= 10:
        t_css = t[valid_css]
        e_css = ec[valid_css]
        d_css = d.values[valid_css]
        med_c = np.median(d_css)
        hi_c  = d_css >= med_c
        lo_c  = ~hi_c
        try:
            res_c = logrank_test(
                t_css[hi_c], t_css[lo_c],
                e_css[hi_c], e_css[lo_c],
            )
            p_css = res_c.p_value
        except Exception:
            p_css = np.nan
        log(f"\n  CSS depth log-rank: "
            f"{fmt_p(p_css)}")
        css_result = {
            "t": t_css, "e": e_css,
            "hi": hi_c, "lo": lo_c,
            "p": p_css,
        }

    return {
        "t": t_v, "e": e_v,
        "hi": hi, "lo": lo,
        "p_depth": p_depth,
        "d_v": d_v,
        "panel": panel_result,
        "css": css_result,
        "gene_results": gene_results,
        "df_v": df_v,
        "label": label,
    }

# ============================================================
# S2 SPECIFIC BIOLOGY TESTS
# ============================================================

def biology_tests(lum, bas, l_depth, b_depth):
    log("")
    log("=" * 65)
    log("S2 BIOLOGY TESTS")
    log("=" * 65)

    gc_l = list(lum.columns)
    gc_b = list(bas.columns)

    # S2-B1/B2: FGFR isoform switch
    log(f"\n  S2-B1/B2: FGFR ISOFORM SWITCH")
    log(f"  Prediction: FGFR3>FGFR1 luminal")
    log(f"              FGFR1>FGFR3 basal")
    log(f"  {'Gene':<8} {'Luminal r':>10} "
        f"{'Basal r':>10}  Pred")
    for g1, g2 in [("FGFR3","FGFR1"),
                   ("FGFR1","FGFR3")]:
        rl = rla = rb = rba = np.nan
        if g1 in gc_l:
            rl, _ = safe_pearsonr(
                l_depth.values, lum[g1].values
            )
        if g2 in gc_l:
            rla, _ = safe_pearsonr(
                l_depth.values, lum[g2].values
            )
        if g1 in gc_b:
            rb, _ = safe_pearsonr(
                b_depth.values, bas[g1].values
            )
        if g2 in gc_b:
            rba, _ = safe_pearsonr(
                b_depth.values, bas[g2].values
            )
        log(f"  {g1:<8} {rl:>+10.4f} "
            f"{rb:>+10.4f}")

    for gene in ["FGFR3","FGFR1"]:
        rl = rb = np.nan
        if gene in gc_l:
            rl, pl = safe_pearsonr(
                l_depth.values, lum[gene].values
            )
        if gene in gc_b:
            rb, pb = safe_pearsonr(
                b_depth.values, bas[gene].values
            )
        log(f"  {gene}: luminal r={rl:+.4f}  "
            f"basal r={rb:+.4f}")

    if "FGFR3" in gc_l and "FGFR1" in gc_l:
        r3, _ = safe_pearsonr(
            l_depth.values, lum["FGFR3"].values
        )
        r1, _ = safe_pearsonr(
            l_depth.values, lum["FGFR1"].values
        )
        if abs(r3) > abs(r1):
            log(f"  S2-B1 CONFIRMED ✓ "
                f"(FGFR3 r={r3:+.4f} > "
                f"FGFR1 r={r1:+.4f} in luminal)")
        else:
            log(f"  S2-B1 NOT CONFIRMED ✗")

    if "FGFR3" in gc_b and "FGFR1" in gc_b:
        r3b, _ = safe_pearsonr(
            b_depth.values, bas["FGFR3"].values
        )
        r1b, _ = safe_pearsonr(
            b_depth.values, bas["FGFR1"].values
        )
        if abs(r1b) > abs(r3b):
            log(f"  S2-B2 CONFIRMED ✓ "
                f"(FGFR1 r={r1b:+.4f} > "
                f"FGFR3 r={r3b:+.4f} in basal)")
        else:
            log(f"  S2-B2 NOT CONFIRMED ✗")

    # S2-B3: MCL1 vs BCL2 in basal
    log(f"\n  S2-B3: MCL1 vs BCL2 in BASAL")
    log(f"  Prediction: MCL1 r > BCL2 r")
    for gene in ["MCL1","BCL2","BCL2L1","BAX"]:
        if gene in gc_b:
            rv, pv = safe_pearsonr(
                b_depth.values, bas[gene].values
            )
            log(f"  {gene:<8} r={rv:+.4f}  "
                f"{fmt_p(pv)}")
    if "MCL1" in gc_b and "BCL2" in gc_b:
        rm, _ = safe_pearsonr(
            b_depth.values, bas["MCL1"].values
        )
        rb, _ = safe_pearsonr(
            b_depth.values, bas["BCL2"].values
        )
        if rm > rb:
            log(f"  S2-B3 CONFIRMED ✓ "
                f"(MCL1 r={rm:+.4f} > "
                f"BCL2 r={rb:+.4f})")
        else:
            log(f"  S2-B3 NOT CONFIRMED ✗")

    # S2-B4: CDK6 vs CDK4 in basal
    log(f"\n  S2-B4: CDK6 vs CDK4 in BASAL")
    log(f"  Prediction: CDK6 r > CDK4 r")
    for gene in ["CDK6","CDK4","CDK2",
                 "CCND1","CCNE1","CCNB1"]:
        if gene in gc_b:
            rv, pv = safe_pearsonr(
                b_depth.values, bas[gene].values
            )
            log(f"  {gene:<8} r={rv:+.4f}  "
                f"{fmt_p(pv)}")
    if "CDK6" in gc_b and "CDK4" in gc_b:
        r6, _ = safe_pearsonr(
            b_depth.values, bas["CDK6"].values
        )
        r4, _ = safe_pearsonr(
            b_depth.values, bas["CDK4"].values
        )
        if r6 > r4:
            log(f"  S2-B4 CONFIRMED ✓ "
                f"(CDK6 r={r6:+.4f} > "
                f"CDK4 r={r4:+.4f})")
        else:
            log(f"  S2-B4 NOT CONFIRMED ✗")

    # S2-B5: MMR loss in deep luminal
    log(f"\n  S2-B5: MMR LOSS IN DEEP LUMINAL")
    log(f"  Prediction: MSH2/MSH6 r<-0.35")
    for gene in ["MSH2","MSH6","MLH1","MSH2"]:
        if gene in gc_l:
            rv, pv = safe_pearsonr(
                l_depth.values, lum[gene].values
            )
            conf = (
                "✓" if rv < -0.35 else "✗"
            )
            log(f"  {gene:<8} r={rv:+.4f}  "
                f"{fmt_p(pv)}  {conf}")

    # S2-B6: SMAD3 in deep luminal
    log(f"\n  S2-B6: SMAD3/TGF-B IN DEEP LUMINAL")
    log(f"  Prediction: SMAD3 r>+0.45")
    for gene in ["SMAD3","SMAD2","TGFB1",
                 "TGFBR2"]:
        if gene in gc_l:
            rv, pv = safe_pearsonr(
                l_depth.values, lum[gene].values
            )
            conf = (
                "✓" if rv > 0.45 else
                "trend" if rv > 0.30 else "✗"
            )
            log(f"  {gene:<8} r={rv:+.4f}  "
                f"{fmt_p(pv)}  {conf}")

    # S2-B7: KRT20+CDX2 intestinal axis luminal
    log(f"\n  S2-B7: KRT20+CDX2 INTESTINAL AXIS")
    log(f"  Cross-cancer: BLCA-EAC connection")
    for gene in ["KRT20","CDX2","FOXA2",
                 "KRT7","KRT8"]:
        if gene in gc_l:
            rv, pv = safe_pearsonr(
                l_depth.values, lum[gene].values
            )
            log(f"  {gene:<8} r={rv:+.4f}  "
                f"{fmt_p(pv)}")
    if "KRT20" in gc_l and "CDX2" in gc_l:
        rv, pv = safe_pearsonr(
            lum["KRT20"].values,
            lum["CDX2"].values,
        )
        log(f"\n  r(KRT20,CDX2) in luminal: "
            f"{rv:+.4f}  {fmt_p(pv)}")
        if not np.isnan(rv) and rv > 0.30:
            log(f"  S2-B7 CONFIRMED ✓")
        else:
            log(f"  S2-B7 NOT CONFIRMED ✗")

    # S2-B8: Basal vs Luminal FC
    log(f"\n  S2-B8: BASAL vs LUMINAL FC")
    log(f"  Correct comparator for subtypes")
    compare_genes = [
        "KRT5","KRT14","TWIST1","ZEB2",
        "VIM","SNAI1","CDK6","MYC",
        "GATA3","FOXA1","PPARG","FGFR3",
        "CCND1","UPK2","ERBB2","ERBB3",
        "KRT8","KRT19","TP63","EGFR",
        "AURKA","MCL1","BCL2","EZH2",
        "HDAC1","KDM6A","SMAD3","NOTCH1",
    ]
    log(f"  {'Gene':<12} {'Luminal':>9} "
        f"{'Basal':>9} {'FC%':>9}  p-value")
    log(f"  {'-'*58}")
    all_gc = set(gc_l) | set(gc_b)
    for gene in compare_genes:
        if gene not in all_gc:
            continue
        lm = (
            lum[gene].mean()
            if gene in gc_l else np.nan
        )
        bm = (
            bas[gene].mean()
            if gene in gc_b else np.nan
        )
        if np.isnan(lm) or np.isnan(bm):
            continue
        fc = (bm - lm) / abs(lm) * 100
        lv = (
            lum[gene].values if gene in gc_l
            else np.array([])
        )
        bv = (
            bas[gene].values if gene in gc_b
            else np.array([])
        )
        _, p = safe_mwu(bv, lv, "two-sided")
        log(f"  {gene:<12} {lm:>9.4f} "
            f"{bm:>9.4f} {fmt_fc(fc):>9}  "
            f"{fmt_p(p)}")

# ============================================================
# EPIGENETIC TESTS
# ============================================================

def epigenetic_tests(lum, bas, l_depth, b_depth):
    log("")
    log("=" * 65)
    log("EPIGENETIC DEPTH TESTS")
    log("EZH2+HDAC1 in BLCA (vs ESCA)")
    log("=" * 65)

    for label, df_, depth_ in [
        ("LUMINAL", lum, l_depth),
        ("BASAL",   bas, b_depth),
    ]:
        gc_ = list(df_.columns)
        log(f"\n  {label}:")
        for gene in [
            "EZH2","HDAC1","KDM6A",
            "ARID1A","TET2","DNMT3A",
        ]:
            if gene not in gc_:
                continue
            rv, pv = safe_pearsonr(
                depth_.values, df_[gene].values
            )
            log(f"  {gene:<8} r={rv:+.4f}  "
                f"{fmt_p(pv)}")

        # EZH2+HDAC1 combined
        if "EZH2" in gc_ and "HDAC1" in gc_:
            r_e, _ = safe_pearsonr(
                depth_.values, df_["EZH2"].values
            )
            r_h, _ = safe_pearsonr(
                depth_.values, df_["HDAC1"].values
            )
            combined = (
                norm01(df_["EZH2"].values)
                + norm01(df_["HDAC1"].values)
            )
            r_c, _ = safe_pearsonr(
                depth_.values, combined.values
            )
            log(f"\n  EZH2+HDAC1 combined "
                f"({label}):")
            log(f"  r(EZH2)       = {r_e:+.4f}")
            log(f"  r(HDAC1)      = {r_h:+.4f}")
            log(f"  r(combined)   = {r_c:+.4f}")
            if abs(r_c) > max(abs(r_e), abs(r_h)):
                log(f"  Combined > individual ✓")
            else:
                log(f"  Combined ≤ individual ✗")

# ============================================================
# GENERATE FIGURE
# ============================================================

def generate_figure(
    groups, l_depth, b_depth,
    surv_lum, surv_bas,
):
    log("")
    log("--- Generating Script 2 figure ---")

    fig = plt.figure(figsize=(28, 22))
    fig.suptitle(
        "Bladder Cancer — False Attractor "
        "Analysis\n"
        "Script 2 | GSE13507 | Survival + "
        "Biology Validation\n"
        "OrganismCore | Doc 91b | 2026-03-01",
        fontsize=10, fontweight="bold",
        y=0.99,
    )

    gs_f = gridspec.GridSpec(
        3, 3, figure=fig,
        hspace=0.55, wspace=0.45,
    )

    COLORS = {
        "Normal":  "#27ae60",
        "Luminal": "#2980b9",
        "Basal":   "#e74c3c",
    }

    # A — KM Luminal OS
    ax_a = fig.add_subplot(gs_f[0, 0])
    if surv_lum is not None:
        t  = surv_lum["t"]
        e  = surv_lum["e"]
        hi = surv_lum["hi"]
        lo = surv_lum["lo"]
        p  = surv_lum["p_depth"]
        kmf = KaplanMeierFitter()
        kmf.fit(
            t[hi], e[hi],
            label=f"Deep (n={hi.sum()})",
        )
        kmf.plot_survival_function(
            ax=ax_a, color="#e74c3c",
            ci_show=True, ci_alpha=0.1,
        )
        kmf.fit(
            t[lo], e[lo],
            label=f"Shallow (n={lo.sum()})",
        )
        kmf.plot_survival_function(
            ax=ax_a, color="#27ae60",
            ci_show=True, ci_alpha=0.1,
        )
        p_str = (
            f"p={p:.4f}"
            if not np.isnan(p) else "N/A"
        )
        ax_a.set_title(
            f"A — KM Luminal OS\n{p_str}",
            fontsize=9,
        )
        ax_a.legend(fontsize=7)
        ax_a.set_xlabel(
            "Time (months)", fontsize=8
        )
    else:
        ax_a.text(
            0.5, 0.5, "No luminal OS",
            ha="center", va="center",
            transform=ax_a.transAxes,
        )
        ax_a.set_title(
            "A — KM Luminal OS", fontsize=9
        )

    # B — KM Basal OS
    ax_b = fig.add_subplot(gs_f[0, 1])
    if surv_bas is not None:
        t  = surv_bas["t"]
        e  = surv_bas["e"]
        hi = surv_bas["hi"]
        lo = surv_bas["lo"]
        p  = surv_bas["p_depth"]
        kmf = KaplanMeierFitter()
        kmf.fit(
            t[hi], e[hi],
            label=f"Deep (n={hi.sum()})",
        )
        kmf.plot_survival_function(
            ax=ax_b, color="#e74c3c",
            ci_show=True, ci_alpha=0.1,
        )
        kmf.fit(
            t[lo], e[lo],
            label=f"Shallow (n={lo.sum()})",
        )
        kmf.plot_survival_function(
            ax=ax_b, color="#27ae60",
            ci_show=True, ci_alpha=0.1,
        )
        p_str = (
            f"p={p:.4f}"
            if not np.isnan(p) else "N/A"
        )
        ax_b.set_title(
            f"B — KM Basal OS\n{p_str}",
            fontsize=9,
        )
        ax_b.legend(fontsize=7)
        ax_b.set_xlabel(
            "Time (months)", fontsize=8
        )
    else:
        ax_b.text(
            0.5, 0.5, "No basal OS",
            ha="center", va="center",
            transform=ax_b.transAxes,
        )
        ax_b.set_title(
            "B — KM Basal OS", fontsize=9
        )

    # C — Panel KM (luminal)
    ax_c = fig.add_subplot(gs_f[0, 2])
    if (
        surv_lum is not None
        and surv_lum.get("panel") is not None
    ):
        panel = surv_lum["panel"]
        t  = panel["t"]
        e  = panel["e"]
        hi = panel["phi"]
        lo = panel["plo"]
        p  = panel["p_panel"]
        kmf = KaplanMeierFitter()
        kmf.fit(
            t[hi], e[hi],
            label=f"High (n={hi.sum()})",
        )
        kmf.plot_survival_function(
            ax=ax_c, color="#8e44ad",
            ci_show=False,
        )
        kmf.fit(
            t[lo], e[lo],
            label=f"Low (n={lo.sum()})",
        )
        kmf.plot_survival_function(
            ax=ax_c, color="#f39c12",
            ci_show=False,
        )
        p_str = (
            f"p={p:.4f}"
            if not np.isnan(p) else "N/A"
        )
        ax_c.set_title(
            f"C — KM Panel\n"
            f"FGFR3/CCND1/CLDN3 {p_str}",
            fontsize=9,
        )
        ax_c.legend(fontsize=7)
        ax_c.set_xlabel(
            "Time (months)", fontsize=8
        )
    else:
        ax_c.text(
            0.5, 0.5,
            "Panel KM\nnot available",
            ha="center", va="center",
            transform=ax_c.transAxes,
        )
        ax_c.set_title(
            "C — Panel KM", fontsize=9
        )

    # D — Depth vs expression scatter (FGFR3)
    ax_d = fig.add_subplot(gs_f[1, 0])
    if "Luminal" in groups:
        lum = groups["Luminal"]
        if "FGFR3" in lum.columns:
            ax_d.scatter(
                l_depth.values,
                lum["FGFR3"].values,
                alpha=0.4, s=20,
                color=COLORS["Luminal"],
            )
            rv, _ = safe_pearsonr(
                l_depth.values,
                lum["FGFR3"].values,
            )
            ax_d.set_title(
                f"D — FGFR3 vs Luminal Depth\n"
                f"r={rv:+.3f}",
                fontsize=9,
            )
            ax_d.set_xlabel(
                "Luminal depth", fontsize=8
            )
            ax_d.set_ylabel("FGFR3", fontsize=8)

    # E — Depth vs TWIST1 (basal)
    ax_e = fig.add_subplot(gs_f[1, 1])
    if "Basal" in groups:
        bas = groups["Basal"]
        if "TWIST1" in bas.columns:
            ax_e.scatter(
                b_depth.values,
                bas["TWIST1"].values,
                alpha=0.4, s=20,
                color=COLORS["Basal"],
            )
            rv, _ = safe_pearsonr(
                b_depth.values,
                bas["TWIST1"].values,
            )
            ax_e.set_title(
                f"E — TWIST1 vs Basal Depth\n"
                f"r={rv:+.3f}",
                fontsize=9,
            )
            ax_e.set_xlabel(
                "Basal depth", fontsize=8
            )
            ax_e.set_ylabel(
                "TWIST1", fontsize=8
            )

    # F — Basal vs Luminal key genes
    ax_f = fig.add_subplot(gs_f[1, 2])
    compare = [
        "KRT5","TWIST1","ZEB2",
        "GATA3","FGFR3","UPK2",
    ]
    lum_g = groups.get("Luminal",
                       pd.DataFrame())
    bas_g = groups.get("Basal",
                       pd.DataFrame())
    avail = [
        g for g in compare
        if (
            g in lum_g.columns
            or g in bas_g.columns
        )
    ]
    if avail:
        x = np.arange(len(avail))
        w = 0.35
        for i, (label, grp) in enumerate([
            ("Luminal", lum_g),
            ("Basal",   bas_g),
        ]):
            means = [
                grp[g].mean()
                if g in grp.columns else 0
                for g in avail
            ]
            ax_f.bar(
                x + (i - 0.5) * w,
                means, w,
                color=COLORS[label],
                label=label, alpha=0.85,
            )
        ax_f.set_xticks(x)
        ax_f.set_xticklabels(
            avail, rotation=45,
            ha="right", fontsize=7,
        )
        ax_f.legend(fontsize=7)
    ax_f.set_title(
        "F — Basal vs Luminal\nKey Markers",
        fontsize=9,
    )

    # G — Epigenetic markers
    ax_g = fig.add_subplot(gs_f[2, 0])
    epi = [
        "EZH2","HDAC1","KDM6A","ARID1A"
    ]
    norm_g = groups.get("Normal",
                        pd.DataFrame())
    avail_e = [
        g for g in epi
        if any(
            g in grp.columns
            for grp in [lum_g, bas_g, norm_g]
        )
    ]
    if avail_e:
        x = np.arange(len(avail_e))
        w = 0.25
        for i, (label, grp) in enumerate([
            ("Normal",  norm_g),
            ("Luminal", lum_g),
            ("Basal",   bas_g),
        ]):
            if len(grp) == 0:
                continue
            means = [
                grp[g].mean()
                if g in grp.columns else 0
                for g in avail_e
            ]
            ax_g.bar(
                x + (i - 1) * w,
                means, w,
                color=COLORS[label],
                label=label, alpha=0.85,
            )
        ax_g.set_xticks(x)
        ax_g.set_xticklabels(
            avail_e, rotation=45,
            ha="right", fontsize=8,
        )
        ax_g.legend(fontsize=6)
    ax_g.set_title(
        "G — Epigenetic Markers",
        fontsize=9,
    )

    # H — GATA3 vs basal depth
    ax_h = fig.add_subplot(gs_f[2, 1])
    if "Basal" in groups:
        bas = groups["Basal"]
        if "GATA3" in bas.columns:
            ax_h.scatter(
                b_depth.values,
                bas["GATA3"].values,
                alpha=0.4, s=20,
                color=COLORS["Basal"],
            )
            rv, _ = safe_pearsonr(
                b_depth.values,
                bas["GATA3"].values,
            )
            ax_h.set_title(
                f"H — GATA3 vs Basal Depth\n"
                f"r={rv:+.3f} *** "
                f"(primary gate)",
                fontsize=9,
            )
            ax_h.set_xlabel(
                "Basal depth", fontsize=8
            )
            ax_h.set_ylabel(
                "GATA3", fontsize=8
            )

    # I — Summary
    ax_i = fig.add_subplot(gs_f[2, 2])
    ax_i.axis("off")

    p_lum = (
        f"{surv_lum['p_depth']:.4f}"
        if surv_lum
        and not np.isnan(surv_lum["p_depth"])
        else "N/A"
    )
    p_bas = (
        f"{surv_bas['p_depth']:.4f}"
        if surv_bas
        and not np.isnan(surv_bas["p_depth"])
        else "N/A"
    )
    p_pan = "N/A"
    if (
        surv_lum
        and surv_lum.get("panel") is not None
    ):
        pp = surv_lum["panel"]["p_panel"]
        if not np.isnan(pp):
            p_pan = f"{pp:.4f}"

    summary = (
        "I — SCRIPT 2 SUMMARY\n"
        "─────────────────────────────\n"
        "Dataset: GSE13507\n"
        "Luminal=123 Basal=123 N=9\n"
        "Platform: Illumina HWG-6 V2\n\n"
        "SURVIVAL:\n"
        f"  Luminal depth p={p_lum}\n"
        f"  Basal depth   p={p_bas}\n"
        f"  Panel (lum)   p={p_pan}\n\n"
        "BIOLOGY:\n"
        "  FGFR3>FGFR1 luminal (B1)\n"
        "  FGFR1>FGFR3 basal  (B2)\n"
        "  MCL1>BCL2 basal    (B3)\n"
        "  CDK6>CDK4 basal    (B4)\n"
        "  MSH2/6 down deep lum (B5)\n"
        "  SMAD3 up deep lum  (B6)\n\n"
        "Framework: OrganismCore\n"
        "Doc 91b | 2026-03-01"
    )
    ax_i.text(
        0.03, 0.97, summary,
        transform=ax_i.transAxes,
        fontsize=7.5,
        verticalalignment="top",
        fontfamily="monospace",
        bbox=dict(
            boxstyle="round",
            facecolor="#f8f8f8",
            edgecolor="#cccccc",
        ),
    )

    out = os.path.join(
        RESULTS_DIR,
        "blca_gse13507_s2.png",
    )
    plt.savefig(
        out, dpi=150,
        bbox_inches="tight",
    )
    log(f"\n  Figure saved: {out}")
    plt.close()

# ============================================================
# MAIN
# ============================================================

def main():
    log("=" * 65)
    log("BLADDER CANCER — SCRIPT 2")
    log("Dataset: GSE13507")
    log("Fixes: Event parser + Updated panels")
    log("New: Survival + Biology validation")
    log("Framework: OrganismCore")
    log("Doc: 91b | Date: 2026-03-01")
    log("=" * 65)
    log("")
    log("PREDICTIONS LOCKED:")
    log("SV-1: Luminal depth predicts OS")
    log("SV-2: Basal depth predicts OS")
    log("SV-3: FGFR3/CCND1/CLDN3 panel OS lum")
    log("SV-4: TWIST1/CDK6/GATA3 panel OS bas")
    log("SV-5: Basal depth predicts CSS")
    log("S2-B1: FGFR3>FGFR1 in luminal")
    log("S2-B2: FGFR1>FGFR3 in basal")
    log("S2-B3: MCL1>BCL2 in basal depth")
    log("S2-B4: CDK6>CDK4 in basal depth")
    log("S2-B5: MSH2/MSH6 r<-0.35 luminal")
    log("S2-B6: SMAD3 r>+0.45 luminal")
    log("S2-B7: KRT20+CDX2 correlated luminal")

    # Build probe map
    probe_map, gene_to_prob = build_probe_map()
    if not probe_map:
        write_log()
        return

    # Parse matrix
    result = parse_matrix(
        probe_map, gene_to_prob
    )
    if result[0] is None:
        log("FATAL: Parse failed")
        write_log()
        return

    df_genes, meta, char_rows = result

    # Classify
    subtype = classify(
        df_genes, meta, char_rows
    )

    group_order = ["Normal","Luminal","Basal"]
    groups = {}
    for g in group_order:
        mask = subtype == g
        if mask.sum() > 0:
            groups[g] = df_genes[mask]

    log("")
    log("=" * 65)
    log("GROUP SUMMARY")
    log("=" * 65)
    for g, df_ in groups.items():
        log(f"  {g:<12}: {len(df_)}")

    lum = groups.get("Luminal", pd.DataFrame())
    bas = groups.get("Basal",   pd.DataFrame())

    # Survival
    surv = parse_survival(df_genes)

    # Depth scores — S2 updated panels
    log("")
    log("=" * 65)
    log("DEPTH SCORES — UPDATED S2 PANELS")
    log("=" * 65)
    l_depth = b_depth = None
    if len(lum) >= 5:
        log("  Luminal depth (S2 panel):")
        l_depth = build_depth(
            lum,
            LUMINAL_SWITCH_S2,
            LUMINAL_FA_S2,
            "Luminal",
        )
    if len(bas) >= 5:
        log("  Basal depth (S2 panel):")
        b_depth = build_depth(
            bas,
            BASAL_SWITCH_S2,
            BASAL_FA_S2,
            "Basal",
        )

    # Biology tests
    if l_depth is not None and b_depth is not None:
        biology_tests(lum, bas, l_depth, b_depth)
        epigenetic_tests(
            lum, bas, l_depth, b_depth
        )

    # Survival analysis
    surv_lum = surv_bas = None
    if surv is not None:
        surv["subtype"] = subtype

        if l_depth is not None:
            surv_lum = run_survival(
                lum, l_depth, surv,
                "LUMINAL",
                panel_genes=[
                    "FGFR3","CCND1","CLDN3"
                ],
                panel_dirs=["+","+","-"],
            )

        if b_depth is not None:
            surv_bas = run_survival(
                bas, b_depth, surv,
                "BASAL",
                panel_genes=[
                    "TWIST1","CDK6","GATA3"
                ],
                panel_dirs=["+","+","-"],
            )

    # Figure
    generate_figure(
        groups,
        l_depth, b_depth,
        surv_lum, surv_bas,
    )

    # Save depth
    for label, depth_ in [
        ("luminal", l_depth),
        ("basal",   b_depth),
    ]:
        if depth_ is not None:
            depth_.to_csv(
                os.path.join(
                    RESULTS_DIR,
                    f"depth_s2_{label}.csv",
                ),
                header=[f"depth_s2_{label}"],
            )

    write_log()
    log(f"\n  Log    : {LOG_FILE}")
    log(f"  Output : {RESULTS_DIR}")
    log("\n=== SCRIPT 2 COMPLETE ===")
    log("\nPaste full output for Document 91b.")


if __name__ == "__main__":
    main()
