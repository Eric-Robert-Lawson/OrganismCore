#!/usr/bin/env python3
"""
rcc_cross_type_script2.py  —  patched for f-string format error
All logic identical to previous version; only string formatting fixed.
"""

import os
import glob
import warnings
import json
import numpy as np
import pandas as pd
from scipy import stats
from itertools import combinations

warnings.filterwarnings("ignore", category=RuntimeWarning)

# ─────────────────────────────────────────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────────────────────────────────────────

RCC_BASE = "/Users/ericlawson/cancer/RCC"

PATHS = {
    "ccRCC": {
        "depth_corr_primary":  "CCRCC/ccrcc_false_attractor/results_s1/depth_corr_tcga.csv",
        "depth_corr_geo":      "CCRCC/ccrcc_false_attractor/results_s1/depth_corr_geo.csv",
        "genome_scan":         "CCRCC/ccrcc_false_attractor/results_s4/genome_scan_full.csv",
        "saddle":              "CCRCC/ccrcc_false_attractor/results_s1/saddle_tcga.csv",
        "circuits":            "CCRCC/ccrcc_false_attractor/results_s2/circuits_tcga.csv",
        "chromatin":           "CCRCC/ccrcc_false_attractor/results_s3/chromatin_tcga.csv",
        "transition_index":    "CCRCC/ccrcc_false_attractor/results_s5/transition_index.csv",
        "drug_map":            "CCRCC/ccrcc_false_attractor/results_s5/drug_map.csv",
        "depth_s5":            "CCRCC/ccrcc_false_attractor/results_s5/depth_s5.csv",
    },
    "PRCC": {
        "depth_corr_primary":  "PRCC/prcc_false_attractor/results_s1/depth_corr_tcga-kirp.csv",
        "fa2_gene_corr":       "PRCC/prcc_false_attractor/results_s6/fa2_depth_gene_corr.csv",
        "integrated_table":    "PRCC/prcc_false_attractor/results_s6/integrated_gene_table.csv",
        "transition_index":    "PRCC/prcc_false_attractor/results_s2/transition_index.csv",
        "cross_cancer":        "PRCC/prcc_false_attractor/results_s4/cross_cancer_shared_genes.csv",
        "drug_priority":       "PRCC/prcc_false_attractor/results_s5/drug_priority_map.csv",
        "ti_fa2":              "PRCC/prcc_false_attractor/results_s5/TI_FA2.csv",
    },
    "chRCC": {
        "depth_scores":        "chRCC/chrcc_false_attractor/results_s1/depth_scores.csv",
        "pc2_correlates":      "chRCC/chrcc_false_attractor/results_s3/pc2_correlates.csv",
        "pc2_residualised":    "chRCC/chrcc_false_attractor/results_s5/pc2_residualised_full.csv",
        "chromatin_panel":     "chRCC/chrcc_false_attractor/results_s2/chromatin_panel.csv",
        "attractor_panel":     "chRCC/chrcc_false_attractor/results_s1/attractor_gene_panel.csv",
        "transition_index":    "chRCC/chrcc_false_attractor/results_s1/transition_index.csv",
        "tier3":               "chRCC/chrcc_false_attractor/results_s5/tier3_revalidated.csv",
        "cross_cancer":        "chRCC/chrcc_false_attractor/results_s1/cross_cancer_panel.csv",
        "drug_targets":        "chRCC/chrcc_false_attractor/results_s1/drug_target_panel.csv",
    },
    "cdRCC": {
        "depth_corr_primary":  "cdRCC/cdRCC_false_attractor/results_s3/depth_correlations_spearman_s3.csv",
        "depth_corr_s1":       "cdRCC/cdRCC_false_attractor/results/depth_correlations.csv",
        "depth_corr_s2":       "cdRCC/cdRCC_false_attractor/results_s2/depth_correlations_s2.csv",
        "expression_matrix":   "cdRCC/cdRCC_false_attractor/results/GSE89122_log2cpm.csv",
        "paired_results":      "cdRCC/cdRCC_false_attractor/results/paired_results.csv",
        "saddle":              "cdRCC/cdRCC_false_attractor/results/saddle_results.csv",
    },
}

OUT_DIR = os.path.join(RCC_BASE, "results_cross_type_s2")
os.makedirs(OUT_DIR, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# LOCKED PREDICTIONS  (Document 97x-2, 2026-03-03)
# ─────────────────────────────────────────────────────────────────────────────

PREDICTIONS = {
    "P2-1a": {"type": "ccRCC", "gene_a": "EZH2",   "gene_b": "DNMT3A",  "expected": "> 0.30"},
    "P2-1b": {"type": "PRCC",  "gene_a": "EZH2",   "gene_b": "DNMT3A",  "expected": "> 0.30"},
    "P2-1c": {"type": "cdRCC", "gene_a": "EZH2",   "gene_b": "DNMT3A",  "expected": "> 0.30"},
    "P2-1d": {"type": "chRCC", "gene_a": "EZH2",   "gene_b": "DNMT3A",  "expected": "< 0.20"},
    "P2-2a": {"type": "ccRCC", "gene_a": "MYC",    "gene_b": "RUNX1",   "expected": "< -0.20"},
    "P2-2b": {"type": "PRCC",  "gene_a": "MYC",    "gene_b": "KDM1A",   "expected": "< -0.20"},
    "P2-2c": {"type": "cdRCC", "gene_a": "MYC",    "gene_b": "BHLHE40", "expected": "< -0.90"},
    "P2-2d": {"type": "chRCC", "gene_a": "MYC",    "gene_b": "BHLHE40", "expected": "< -0.30"},
    "P2-2e": {"type": "ccRCC", "gene_a": "MYC",    "gene_b": "BHLHE40", "expected": "< -0.20"},
    "P2-3a": {"type": "PRCC",  "gene_a": "IL1RAP", "gene_b": "depth",   "expected": "> 0.25"},
    "P2-3b": {"type": "chRCC", "gene_a": "IL1RAP", "gene_b": "depth",   "expected": "< 0.15"},
    "P2-5a": {"type": "ccRCC", "gene_a": "TI",     "gene_b": "depth",   "expected": "< -0.50"},
    "P2-5b": {"type": "PRCC",  "gene_a": "TI",     "gene_b": "depth",   "expected": "< -0.35"},
    "P2-5c": {"type": "chRCC", "gene_a": "TI",     "gene_b": "depth",   "expected": "> -0.20"},
    "P2-5d": {"type": "cdRCC", "gene_a": "TI",     "gene_b": "depth",   "expected": "< -0.30"},
    "P2-7a": {"type": "PRCC",  "gene_a": "LOXL2",  "gene_b": "depth",   "expected": "> 0.25"},
    "P2-7b": {"type": "chRCC", "gene_a": "LOXL2",  "gene_b": "depth",   "expected": "< 0.15"},
    "P2-8a": {"type": "PRCC",  "gene_a": "RUNX1",  "gene_b": "depth",   "expected": "> 0.30"},
}

PHASE2_TF = {
    "ccRCC": "RUNX1",
    "PRCC":  "KDM1A",
    "chRCC": "BHLHE40",
    "cdRCC": "BHLHE40",
}

AKG_GENES       = ["OGDHL", "SUCLG1", "FH", "SLC13A2"]
CHROMATIN_GENES = ["EZH2", "DNMT3A", "DNMT3B", "KDM1A", "HDAC1",
                   "HDAC2", "SETD2", "PBRM1", "KDM5C", "KDM6A"]
PHASE_PAIRS     = [("MYC", "RUNX1"),   ("MYC", "BHLHE40"), ("MYC", "KDM1A"),
                   ("MYC", "MKI67"),   ("MYC", "CCND1"),   ("MKI67", "RUNX1"),
                   ("MKI67", "BHLHE40"), ("RUNX1", "BHLHE40")]

R_THRESHOLD = 0.15
N_MIN       = 15

# ─────────────────────────────────────────────────────────────────────────────
# UTILITIES
# ─────────────────────────────────────────────────────────────────────────────

def absp(rel_path):
    return os.path.join(RCC_BASE, rel_path)

def load_csv(rel_path, **kwargs):
    full = absp(rel_path)
    if not os.path.isfile(full):
        return None
    try:
        return pd.read_csv(full, **kwargs)
    except Exception as e:
        print(f"    LOAD ERROR {rel_path}: {e}")
        return None

def fmt(v):
    """Format a float for printing — no conditional inside f-string."""
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "  N/A "
    return f"{v:+.3f}"

def normalise_dc(df):
    """Return DataFrame with columns [gene, r] from various column name conventions."""
    if df is None:
        return None
    df = df.copy()
    # gene column
    for cand in ("gene", "gene_name", "symbol", "Gene", "GENE"):
        if cand in df.columns:
            df = df.rename(columns={cand: "gene"})
            break
    if "gene" not in df.columns:
        if df.index.name and df.index.dtype == object:
            df = df.reset_index().rename(columns={df.index.name: "gene"})
        else:
            return None
    # r column
    for cand in ("r", "spearman_r", "rho", "correlation", "corr",
                 "r_PC2", "clean_r"):
        if cand in df.columns:
            df = df.rename(columns={cand: "r"})
            break
    if "r" not in df.columns:
        return None
    # p column (optional)
    for cand in ("p", "pvalue", "p_value", "pval", "p_PC2", "p_mwu"):
        if cand in df.columns:
            df = df.rename(columns={cand: "p"})
            break
    keep = ["gene", "r"] + (["p"] if "p" in df.columns else [])
    df = df[keep].dropna(subset=["gene", "r"]).copy()
    df["r"]    = pd.to_numeric(df["r"], errors="coerce")
    df["gene"] = df["gene"].astype(str).str.strip().str.upper()
    return df.dropna(subset=["r"])

def get_r(dc, gene):
    if dc is None:
        return np.nan
    mask = dc["gene"] == gene.upper()
    if mask.sum() == 0:
        return np.nan
    return float(dc.loc[mask, "r"].iloc[0])

def safe_spearman(x, y):
    mask = (~np.isnan(x)) & (~np.isnan(y))
    xm, ym = x[mask], y[mask]
    n = int(mask.sum())
    if n < 5:
        return np.nan, np.nan, n
    r, p = stats.spearmanr(xm, ym)
    return float(r), float(p), n

def verdict(r_val, expected, approx=False, low_power=False):
    if r_val is None or (isinstance(r_val, float) and np.isnan(r_val)):
        return "UNTESTABLE"
    if expected.startswith("> "):
        v = "CONFIRMED" if r_val > float(expected[2:]) else "DENIED"
    elif expected.startswith("< "):
        v = "CONFIRMED" if r_val < float(expected[2:]) else "DENIED"
    else:
        return "UNTESTABLE"
    if approx:
        v += " [APPROX]"
    if low_power:
        v += " [LOW-POWER]"
    return v

def gene_gene_approx(dc, gene_a, gene_b):
    ra = get_r(dc, gene_a)
    rb = get_r(dc, gene_b)
    if np.isnan(ra) or np.isnan(rb):
        return np.nan
    return float(np.sign(ra * rb) * np.sqrt(abs(ra) * abs(rb)))

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1 — LOAD DEPTH CORRELATION FILES
# ─────────────────────────────────────────────────────────────────────────────

print("=" * 65)
print("RCC CROSS-TYPE ANALYSIS — SCRIPT 2")
print("OrganismCore | 2026-03-03 | Eric Robert Lawson")
print("=" * 65)
print()
print("=" * 65)
print("STEP 1 — LOADING DEPTH CORRELATION FILES")
print("=" * 65)

# ── ccRCC ──────────────────────────────────────────────────────────────────
print("\n[ccRCC]")
ccRCC_dc  = normalise_dc(load_csv(PATHS["ccRCC"]["depth_corr_primary"]))
ccRCC_gs  = normalise_dc(load_csv(PATHS["ccRCC"]["genome_scan"]))
pieces = [x for x in [ccRCC_gs, ccRCC_dc] if x is not None]
ccRCC_full = (pd.concat(pieces).drop_duplicates(subset="gene", keep="first")
              .reset_index(drop=True)) if pieces else None
n_cc = len(ccRCC_full) if ccRCC_full is not None else 0
print(f"  genes loaded: {n_cc}  "
      f"(s1={len(ccRCC_dc) if ccRCC_dc is not None else 0}, "
      f"genome_scan={len(ccRCC_gs) if ccRCC_gs is not None else 0})")

# ── PRCC ───────────────────────────────────────────────────────────────────
print("\n[PRCC]")
prcc_dc   = normalise_dc(load_csv(PATHS["PRCC"]["depth_corr_primary"]))
prcc_fa2  = normalise_dc(load_csv(PATHS["PRCC"]["fa2_gene_corr"]))
prcc_int  = normalise_dc(load_csv(PATHS["PRCC"]["integrated_table"]))
pieces = [x for x in [prcc_dc, prcc_fa2, prcc_int] if x is not None]
prcc_full = (pd.concat(pieces).drop_duplicates(subset="gene", keep="first")
             .reset_index(drop=True)) if pieces else None
n_pr = len(prcc_full) if prcc_full is not None else 0
print(f"  genes loaded: {n_pr}  "
      f"(s1={len(prcc_dc) if prcc_dc is not None else 0}, "
      f"fa2={len(prcc_fa2) if prcc_fa2 is not None else 0}, "
      f"int={len(prcc_int) if prcc_int is not None else 0})")

# ── chRCC ──────────────────────────────────────────────────────────────────
print("\n[chRCC]")
chrcc_res = normalise_dc(load_csv(PATHS["chRCC"]["pc2_residualised"]))
chrcc_pc2 = normalise_dc(load_csv(PATHS["chRCC"]["pc2_correlates"]))
chrcc_att = normalise_dc(load_csv(PATHS["chRCC"]["attractor_panel"]))
pieces = [x for x in [chrcc_res, chrcc_pc2, chrcc_att] if x is not None]
chrcc_full = (pd.concat(pieces).drop_duplicates(subset="gene", keep="first")
              .reset_index(drop=True)) if pieces else None
n_ch = len(chrcc_full) if chrcc_full is not None else 0
print(f"  PC2/attractor genes loaded: {n_ch}  "
      f"(residualised={len(chrcc_res) if chrcc_res is not None else 0}, "
      f"pc2_corr={len(chrcc_pc2) if chrcc_pc2 is not None else 0}, "
      f"attractor={len(chrcc_att) if chrcc_att is not None else 0})")
print("  NOTE: chRCC r = PC2 correlation (positive = chRCC identity)")

# ── cdRCC ──────────────────────────────────────────────────────────────────
print("\n[cdRCC]")
cdrcc_s3  = normalise_dc(load_csv(PATHS["cdRCC"]["depth_corr_primary"]))
cdrcc_s1  = normalise_dc(load_csv(PATHS["cdRCC"]["depth_corr_s1"]))
cdrcc_s2n = normalise_dc(load_csv(PATHS["cdRCC"]["depth_corr_s2"]))
pieces = [x for x in [cdrcc_s3, cdrcc_s1, cdrcc_s2n] if x is not None]
cdrcc_full = (pd.concat(pieces).drop_duplicates(subset="gene", keep="first")
              .reset_index(drop=True)) if pieces else None
n_cd = len(cdrcc_full) if cdrcc_full is not None else 0
print(f"  genes loaded: {n_cd}  "
      f"(s3={len(cdrcc_s3) if cdrcc_s3 is not None else 0}, "
      f"s1={len(cdrcc_s1) if cdrcc_s1 is not None else 0}, "
      f"s2={len(cdrcc_s2n) if cdrcc_s2n is not None else 0})")
print("  NOTE: cdRCC n=7 — ALL correlations LOW-POWER")

# Load cdRCC raw expression
cdrcc_expr_raw = load_csv(PATHS["cdRCC"]["expression_matrix"], index_col=0)
if cdrcc_expr_raw is not None:
    cdrcc_expr = (cdrcc_expr_raw.T
                  if cdrcc_expr_raw.shape[0] > cdrcc_expr_raw.shape[1]
                  else cdrcc_expr_raw)
    cdrcc_expr.columns = [c.strip().upper() for c in cdrcc_expr.columns]
    print(f"  Raw expression: {cdrcc_expr.shape[0]} samples x "
          f"{cdrcc_expr.shape[1]} genes")
else:
    cdrcc_expr = None
    print("  Raw expression: NOT FOUND")

DC = {
    "ccRCC": ccRCC_full,
    "PRCC":  prcc_full,
    "chRCC": chrcc_full,
    "cdRCC": cdrcc_full,
}
N_APPROX  = {"ccRCC": 534, "PRCC": 290, "chRCC": 150, "cdRCC": 7}
LOW_POWER = {"ccRCC": False, "PRCC": False, "chRCC": False, "cdRCC": True}

# ─────────────────────────────────────────────────────────────────────────────
# STEP 2 — LOAD EXISTING TI FILES
# ─────────────────────────────────────────────────────────────────────────────

print()
print("=" * 65)
print("STEP 2 — EXISTING TRANSITION INDEX FILES")
print("=" * 65)

TI_files = {}
for rcc_type in ("ccRCC", "PRCC", "chRCC"):
    ti_raw = load_csv(PATHS[rcc_type]["transition_index"])
    TI_files[rcc_type] = ti_raw
    status = f"{len(ti_raw)} rows, cols={list(ti_raw.columns)}" \
             if ti_raw is not None else "NOT FOUND"
    print(f"  [{rcc_type}] {status}")

prcc_ti_fa2 = load_csv(PATHS["PRCC"]["ti_fa2"])
if prcc_ti_fa2 is not None:
    print(f"  [PRCC] TI_FA2: {len(prcc_ti_fa2)} rows, "
          f"cols={list(prcc_ti_fa2.columns)}")

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS — unified lookup and gene-gene
# ─────────────────────────────────────────────────────────────────────────────

def lookup_depth_r(rcc_type, gene):
    """(r, method, low_power)"""
    r_val = get_r(DC[rcc_type], gene)
    return r_val, ("depth_corr" if not np.isnan(r_val) else "not_found"), LOW_POWER[rcc_type]

def compute_gg_r(rcc_type, gene_a, gene_b):
    """(r, method, low_power, n)"""
    lp = LOW_POWER[rcc_type]
    n  = N_APPROX[rcc_type]
    # cdRCC direct from expression
    if rcc_type == "cdRCC" and cdrcc_expr is not None:
        ga, gb = gene_a.upper(), gene_b.upper()
        if ga in cdrcc_expr.columns and gb in cdrcc_expr.columns:
            x = cdrcc_expr[ga].values.astype(float)
            y = cdrcc_expr[gb].values.astype(float)
            r, _, n_act = safe_spearman(x, y)
            return r, "expr_direct", True, n_act
    # Sign approximation from depth corr
    dc = DC[rcc_type]
    if dc is not None:
        r_approx = gene_gene_approx(dc, gene_a, gene_b)
        if not np.isnan(r_approx):
            return r_approx, "approx_depth_corr", lp, n
    return np.nan, "unavailable", lp, n

# ─────────────────────────────────────────────────────────────────────────────
# OBJ-1 — EZH2 / DNMT3A CO-ELEVATION
# ─────────────────────────────────────────────────────────────────────────────

print()
print("=" * 65)
print("OBJ-1 — EZH2 / DNMT3A CO-ELEVATION")
print("P2-1: r(EZH2,DNMT3A) > 0.30 in ccRCC/PRCC/cdRCC, < 0.20 in chRCC")
print("=" * 65)

obj1_records = []
pred_map_1 = {"ccRCC": "P2-1a", "PRCC": "P2-1b",
              "cdRCC": "P2-1c", "chRCC": "P2-1d"}

for rcc_type in ["ccRCC", "PRCC", "chRCC", "cdRCC"]:
    r_ezh2,  _, _  = lookup_depth_r(rcc_type, "EZH2")
    r_dnmt3a, _, _ = lookup_depth_r(rcc_type, "DNMT3A")
    r_pair, method, lp, n = compute_gg_r(rcc_type, "EZH2", "DNMT3A")
    approx = "approx" in method

    pk   = pred_map_1[rcc_type]
    pred = PREDICTIONS[pk]
    v    = verdict(r_pair, pred["expected"], approx=approx, low_power=lp)

    print(f"\n  [{rcc_type}]")
    print(f"    EZH2   depth r = {fmt(r_ezh2)}  |  "
          f"DNMT3A depth r = {fmt(r_dnmt3a)}")
    ap_str = " [APPROX]" if approx else ""
    lp_str = " ⚠️ LOW-POWER" if lp else ""
    print(f"    r(EZH2, DNMT3A) = {fmt(r_pair)}{ap_str}  "
          f"(method: {method}, n≈{n}){lp_str}")
    print(f"    {pk} ({pred['expected']}) → {v}")

    obj1_records.append({
        "rcc_type": rcc_type, "pred": pk,
        "r_EZH2_depth": r_ezh2, "r_DNMT3A_depth": r_dnmt3a,
        "r_pair": r_pair, "method": method,
        "n": n, "low_power": lp, "approx": approx, "verdict": v,
    })

obj1_df = pd.DataFrame(obj1_records)

# ─────────────────────────────────────────────────────────────────────────────
# OBJ-2 — TWO-PHASE TRANSITION
# ─────────────────────────────────────────────────────────────────────────────

print()
print("=" * 65)
print("OBJ-2 — TWO-PHASE TRANSITION: r(MYC, Phase2_TF)")
print("=" * 65)

pred_map_2 = {"ccRCC": "P2-2a", "PRCC": "P2-2b",
              "cdRCC": "P2-2c", "chRCC": "P2-2d"}
obj2_records = []

for rcc_type in ["ccRCC", "PRCC", "chRCC", "cdRCC"]:
    phase2_tf = PHASE2_TF[rcc_type]
    print(f"\n  [{rcc_type}]  Phase 2 TF = {phase2_tf}")

    r_myc,   _, _ = lookup_depth_r(rcc_type, "MYC")
    r_p2tf,  _, _ = lookup_depth_r(rcc_type, phase2_tf)
    r_mki67, _, _ = lookup_depth_r(rcc_type, "MKI67")

    print(f"    MYC    depth r = {fmt(r_myc)}")
    print(f"    {phase2_tf:<8} depth r = {fmt(r_p2tf)}")
    print(f"    MKI67  depth r = {fmt(r_mki67)}")

    r_pair, method, lp, n = compute_gg_r(rcc_type, "MYC", phase2_tf)
    approx = "approx" in method

    pk   = pred_map_2[rcc_type]
    pred = PREDICTIONS[pk]
    v    = verdict(r_pair, pred["expected"], approx=approx, low_power=lp)

    ap_str = " [APPROX]" if approx else ""
    lp_str = " ⚠️ LOW-POWER" if lp else ""
    print(f"    r(MYC, {phase2_tf}) = {fmt(r_pair)}{ap_str}  "
          f"(method: {method}){lp_str}")
    print(f"    {pk} ({pred['expected']}) → {v}")

    obj2_records.append({
        "rcc_type": rcc_type, "phase2_tf": phase2_tf, "pred": pk,
        "r_MYC_depth": r_myc, "r_Phase2TF_depth": r_p2tf,
        "r_MKI67_depth": r_mki67,
        "r_MYC_Phase2TF": r_pair, "method": method,
        "n": n, "low_power": lp, "approx": approx, "verdict": v,
    })

    # P2-2e: r(MYC, BHLHE40) in ccRCC
    if rcc_type == "ccRCC":
        r_bhlhe, m2, lp2, n2 = compute_gg_r(rcc_type, "MYC", "BHLHE40")
        ap2 = " [APPROX]" if "approx" in m2 else ""
        v2  = verdict(r_bhlhe, "< -0.20", approx="approx" in m2, low_power=lp2)
        print(f"    r(MYC, BHLHE40)  = {fmt(r_bhlhe)}{ap2}  [P2-2e] → {v2}")
        obj2_records.append({
            "rcc_type": rcc_type, "phase2_tf": "BHLHE40", "pred": "P2-2e",
            "r_MYC_depth": r_myc,
            "r_Phase2TF_depth": get_r(DC[rcc_type], "BHLHE40"),
            "r_MKI67_depth": r_mki67,
            "r_MYC_Phase2TF": r_bhlhe, "method": m2,
            "n": n2, "low_power": lp2, "approx": "approx" in m2, "verdict": v2,
        })

    # MKI67 vs Phase2_TF
    r_mki_p2, m3, _, _ = compute_gg_r(rcc_type, "MKI67", phase2_tf)
    ap3 = " [APPROX]" if "approx" in m3 else ""
    print(f"    r(MKI67, {phase2_tf:<8}) = {fmt(r_mki_p2)}{ap3}  "
          f"[identity-proliferation decoupling]")

obj2_df = pd.DataFrame(obj2_records)

# ─────────────────────────────────────────────────────────────────────────────
# OBJ-3 — IL1RAP DEPTH CORRELATION
# ─────────────────────────────────────────────────────────────────────────────

print()
print("=" * 65)
print("OBJ-3 — IL1RAP DEPTH CORRELATION IN PRCC AND chRCC")
print("=" * 65)

obj3_records = []
for rcc_type in ["ccRCC", "PRCC", "chRCC", "cdRCC"]:
    r_val, method, lp = lookup_depth_r(rcc_type, "IL1RAP")
    lp_str = " ⚠️ LOW-POWER" if lp else ""
    pred_str = ""
    v = "context"

    if rcc_type == "PRCC":
        v = verdict(r_val, "> 0.25", low_power=lp)
        pred_str = f"  P2-3a (> 0.25) → {v}"
    elif rcc_type == "chRCC":
        v = verdict(r_val, "< 0.15", low_power=lp)
        pred_str = f"  P2-3b (< 0.15) → {v}"
    elif rcc_type in ("ccRCC", "cdRCC"):
        pred_str = "  ← reference (Script 1)"

    print(f"  [{rcc_type}] r(IL1RAP, depth) = {fmt(r_val)}  "
          f"(method: {method}){lp_str}{pred_str}")

    obj3_records.append({
        "rcc_type": rcc_type, "gene": "IL1RAP",
        "r_depth": r_val, "method": method, "low_power": lp, "verdict": v,
    })

obj3_df = pd.DataFrame(obj3_records)

# ─────────────────────────────────────────────────────────────────────────────
# OBJ-4 — αKG DEFICIT SCORE RANKING
# ─────────────────────────────────────────────────────────────────────────────

print()
print("=" * 65)
print("OBJ-4 — αKG DEFICIT SCORE RANKING")
print("P2-4: cdRCC > PRCC > ccRCC > chRCC")
print("=" * 65)

akg_records = []
print()
for rcc_type in ["ccRCC", "PRCC", "chRCC", "cdRCC"]:
    gene_rs    = {}
    deficit    = 0.0
    n_contrib  = 0
    print(f"  [{rcc_type}]")
    for gene in AKG_GENES:
        r_val, _, lp = lookup_depth_r(rcc_type, gene)
        gene_rs[gene] = r_val
        contrib = not np.isnan(r_val) and r_val < -R_THRESHOLD
        if contrib:
            deficit   += abs(r_val)
            n_contrib += 1
        mark = "  ← contributes" if contrib else ""
        print(f"    {gene:<12} r = {fmt(r_val)}{mark}")
    lp_str = "  ⚠️ LOW-POWER (n=7)" if LOW_POWER[rcc_type] else ""
    print(f"    αKG deficit = {deficit:.3f}  "
          f"({n_contrib}/{len(AKG_GENES)} genes){lp_str}")
    akg_records.append({
        "rcc_type": rcc_type, "akg_deficit_score": deficit,
        "n_contributing": n_contrib, "low_power": LOW_POWER[rcc_type],
        **{f"r_{g}": gene_rs[g] for g in AKG_GENES},
    })

akg_df = pd.DataFrame(akg_records).sort_values(
    "akg_deficit_score", ascending=False).reset_index(drop=True)

ranked = akg_df["rcc_type"].tolist()
predicted_rank = ["cdRCC", "PRCC", "ccRCC", "chRCC"]
rank_verdict = ("CONFIRMED" if ranked == predicted_rank else
                "PARTIAL"   if ranked[:2] == predicted_rank[:2] else
                "DENIED")

print()
print("  RANKED αKG DEFICIT:")
for i, row in akg_df.iterrows():
    lp_s = "  ⚠️ LOW-POWER (n=7)" if row["low_power"] else ""
    print(f"    {i+1}. {row['rcc_type']}: {row['akg_deficit_score']:.3f}{lp_s}")
print(f"  Expected: {' > '.join(predicted_rank)}")
print(f"  Actual:   {' > '.join(ranked)}")
print(f"  P2-4 verdict: {rank_verdict}")

# ─────────────────────────────────────────────────────────────────────────────
# OBJ-5 — GOT1/RUNX1 TRANSITION INDEX
# ─────────────────────────────────────────────────────────────────────────────

print()
print("=" * 65)
print("OBJ-5 — GOT1/RUNX1 TRANSITION INDEX")
print("TI = norm(GOT1) - norm(RUNX1)")
print("=" * 65)

pred_map_5 = {"ccRCC": "P2-5a", "PRCC": "P2-5b",
              "chRCC": "P2-5c", "cdRCC": "P2-5d"}
ti_records = []

for rcc_type in ["ccRCC", "PRCC", "chRCC", "cdRCC"]:
    pk   = pred_map_5[rcc_type]
    pred = PREDICTIONS[pk]

    r_got1,  m_g, lp = lookup_depth_r(rcc_type, "GOT1")
    r_runx1, m_r, _  = lookup_depth_r(rcc_type, "RUNX1")

    print(f"\n  [{rcc_type}]")
    print(f"    GOT1  depth r = {fmt(r_got1)}  (method: {m_g})")
    print(f"    RUNX1 depth r = {fmt(r_runx1)}  (method: {m_r})")

    # Try reading from existing TI file
    ti_r = np.nan
    ti_method = "unavailable"

    ti_file = TI_files.get(rcc_type)
    if ti_file is not None:
        for col in ti_file.columns:
            if col.lower() in ("r", "spearman_r", "ti_r", "corr"):
                if len(ti_file) == 1:
                    try:
                        ti_r = float(ti_file[col].iloc[0])
                        ti_method = "from_ti_file"
                    except Exception:
                        pass
                break

    # cdRCC: compute directly from expression if available
    if rcc_type == "cdRCC" and cdrcc_expr is not None:
        has_got1  = "GOT1"  in cdrcc_expr.columns
        has_runx1 = "RUNX1" in cdrcc_expr.columns
        if has_got1 and has_runx1:
            def norm01(v):
                mn, mx = np.nanmin(v), np.nanmax(v)
                return (v - mn) / (mx - mn) if mx > mn else np.zeros_like(v)
            got1_n  = norm01(cdrcc_expr["GOT1"].values.astype(float))
            runx1_n = norm01(cdrcc_expr["RUNX1"].values.astype(float))
            ti_vals = got1_n - runx1_n
            # Depth proxy: IL1RAP - PRKAR2B
            if ("IL1RAP" in cdrcc_expr.columns and
                    "PRKAR2B" in cdrcc_expr.columns):
                depth_proxy = (cdrcc_expr["IL1RAP"].values.astype(float) -
                               cdrcc_expr["PRKAR2B"].values.astype(float))
                r_ti, p_ti, n_ti = safe_spearman(ti_vals, depth_proxy)
                print(f"    TI direct (n={n_ti}): r={fmt(r_ti)} p={p_ti:.3f}  "
                      f"[depth=IL1RAP-PRKAR2B proxy]")
                ti_r = r_ti
                ti_method = "expr_direct_cdRCC"

    # Approximation fallback
    if np.isnan(ti_r) and not np.isnan(r_got1) and not np.isnan(r_runx1):
        ti_r = r_got1 - r_runx1
        ti_method = "approx_diff_depth_r"
        print(f"    TI ≈ {fmt(r_got1)} - {fmt(r_runx1)} = {fmt(ti_r)}  [APPROX]")
    elif not np.isnan(ti_r):
        print(f"    TI r from file: {fmt(ti_r)}  (method: {ti_method})")

    approx = "approx" in ti_method
    v = verdict(ti_r, pred["expected"], approx=approx, low_power=lp)
    print(f"    {pk} ({pred['expected']}) → {v}")

    ti_records.append({
        "rcc_type": rcc_type, "pred": pk,
        "r_GOT1_depth": r_got1, "r_RUNX1_depth": r_runx1,
        "ti_r": ti_r, "method": ti_method,
        "low_power": lp, "approx": approx, "verdict": v,
    })

ti_df = pd.DataFrame(ti_records)

# ─────────────────────────────────────────────────────────────────────────────
# OBJ-6 — chRCC INTEGRATION STATUS
# ─────────────────────────────────────────────────────────────────────────────

print()
print("=" * 65)
print("OBJ-6 — chRCC DATA INTEGRATION STATUS")
print("=" * 65)

r_ezh2_ch   = get_r(DC["chRCC"], "EZH2")
r_dnmt3a_ch = get_r(DC["chRCC"], "DNMT3A")
ezh2_present  = not np.isnan(r_ezh2_ch)
dnmt3a_absent = np.isnan(r_dnmt3a_ch) or abs(r_dnmt3a_ch) < R_THRESHOLD
genes_ok      = n_ch >= 30

print()
key_genes = ["EZH2", "DNMT3A", "IL1RAP", "LOXL2", "RUNX1", "BHLHE40",
             "MYC", "GOT1", "SLC51B", "ABCC2", "SULT2B1", "PKM",
             "CCND1", "KDM1A", "MKI67"]
for gene in key_genes:
    r_val = get_r(DC["chRCC"], gene)
    if not np.isnan(r_val):
        direction = "chRCC↑" if r_val > 0 else "oncocytoma↑"
        print(f"  {gene:<12} r_PC2 = {fmt(r_val)}  [{direction}]")
    else:
        print(f"  {gene:<12} NOT FOUND in chRCC data")

print()
print(f"  P2-6 sub-predictions:")
print(f"    EZH2 present:     {ezh2_present}  "
      f"r={fmt(r_ezh2_ch)}  → {'✓' if ezh2_present else 'NOT MET'}")
print(f"    DNMT3A absent:    {dnmt3a_absent}  "
      f"r={fmt(r_dnmt3a_ch)}  → {'✓' if dnmt3a_absent else 'NOT MET'}")
print(f"    Gene count >= 30: {n_ch}  → {'✓' if genes_ok else 'NOT MET'}")

chrcc_status = {
    "pc2_correlates_loaded":   chrcc_pc2   is not None,
    "pc2_residualised_loaded": chrcc_res   is not None,
    "attractor_panel_loaded":  chrcc_att   is not None,
    "genes_loaded": n_ch,
    "ezh2_present": ezh2_present,
    "dnmt3a_absent": dnmt3a_absent,
    "genes_ok": genes_ok,
    "r_EZH2":  float(r_ezh2_ch)   if not np.isnan(r_ezh2_ch)   else None,
    "r_DNMT3A": float(r_dnmt3a_ch) if not np.isnan(r_dnmt3a_ch) else None,
}

# ─────────────────────────────────────────────────────────────────────────────
# OBJ-7 — LOXL2 AND RUNX1 IN PRCC AND chRCC
# ─────────────────────────────────────────────────────────────────────────────

print()
print("=" * 65)
print("OBJ-7 — LOXL2 AND RUNX1 DEPTH CORRELATIONS")
print("=" * 65)

obj7_records = []
for gene, pred_map_7 in [
    ("LOXL2", {"PRCC": "P2-7a", "chRCC": "P2-7b"}),
    ("RUNX1", {"PRCC": "P2-8a"}),
]:
    print(f"\n  {gene}:")
    for rcc_type in ["ccRCC", "PRCC", "chRCC", "cdRCC"]:
        r_val, method, lp = lookup_depth_r(rcc_type, gene)
        lp_str = " ⚠️" if lp else ""
        v_str  = ""
        if rcc_type in pred_map_7:
            pk   = pred_map_7[rcc_type]
            pred = PREDICTIONS[pk]
            v    = verdict(r_val, pred["expected"], low_power=lp)
            v_str = f"  {pk} ({pred['expected']}) → {v}"
        print(f"    [{rcc_type}] r({gene}, depth) = {fmt(r_val)}  "
              f"(method: {method}){lp_str}{v_str}")
        obj7_records.append({
            "gene": gene, "rcc_type": rcc_type,
            "r_depth": r_val, "method": method, "low_power": lp,
        })

obj7_df = pd.DataFrame(obj7_records)

# ─────────────────────────────────────────────────────────────────────────────
# OBJ-8 — CHROMATIN AND PHASE GENE-PAIR TABLES
# ─────────────────────────────────────────────────────────────────────────────

print()
print("=" * 65)
print("OBJ-8 — GENE-PAIR CORRELATION TABLES")
print("=" * 65)

chromatin_records = []
for rcc_type in ["ccRCC", "PRCC", "chRCC", "cdRCC"]:
    for ga, gb in combinations(CHROMATIN_GENES, 2):
        r_val, method, lp, n = compute_gg_r(rcc_type, ga, gb)
        chromatin_records.append({
            "rcc_type": rcc_type, "gene_a": ga, "gene_b": gb,
            "r": r_val, "n": n, "method": method, "low_power": lp,
        })

chromatin_df = pd.DataFrame(chromatin_records)
notable = (chromatin_df[chromatin_df["r"].abs() > 0.35]
           .sort_values(["rcc_type", "r"], ascending=[True, False]))
print(f"\n  Notable chromatin pairs (|r| > 0.35):")
if len(notable) == 0:
    print("    None above threshold (all values are approximations)")
for _, row in notable.iterrows():
    ap  = " [A]" if "approx" in row["method"] else ""
    lps = " ⚠️"  if row["low_power"] else ""
    print(f"    [{row['rcc_type']}] r({row['gene_a']}, {row['gene_b']}) = "
          f"{fmt(row['r'])}{ap}{lps}")

print()
print("  Phase gene correlations:")
phase_records = []
for rcc_type in ["ccRCC", "PRCC", "chRCC", "cdRCC"]:
    for ga, gb in PHASE_PAIRS:
        r_val, method, lp, n = compute_gg_r(rcc_type, ga, gb)
        ap  = " [A]" if "approx" in method else ""
        lps = " ⚠️" if lp else ""
        print(f"    [{rcc_type}] r({ga:<8}, {gb:<8}) = "
              f"{fmt(r_val)}{ap}{lps}")
        phase_records.append({
            "rcc_type": rcc_type, "gene_a": ga, "gene_b": gb,
            "r": r_val, "n": n, "method": method, "low_power": lp,
        })

phase_df = pd.DataFrame(phase_records)

# ─────────────────────────────────────────────────────────────────────────────
# PREDICTION SCORING SUMMARY
# ─────────────────────────────────────────────────────────────────────────────

print()
print("=" * 65)
print("PREDICTION SCORING SUMMARY")
print("=" * 65)

score_records = []
for pk, pred in PREDICTIONS.items():
    rcc_type = pred["type"]
    gene_a   = pred["gene_a"]
    gene_b   = pred["gene_b"]
    expected = pred["expected"]

    if gene_a == "TI":
        row    = next((r for r in ti_records if r["rcc_type"] == rcc_type), None)
        r_val  = row["ti_r"]      if row else np.nan
        method = row["method"]    if row else "unavailable"
        lp     = row["low_power"] if row else True
        approx = row["approx"]    if row else False
    elif gene_b == "depth":
        r_val, method, lp = lookup_depth_r(rcc_type, gene_a)
        approx = False
    else:
        r_val, method, lp, _ = compute_gg_r(rcc_type, gene_a, gene_b)
        approx = "approx" in method

    v = verdict(r_val, expected, approx=approx, low_power=lp)
    print(f"  {pk:<7} [{rcc_type:<5}] r({gene_a},{gene_b}) = {fmt(r_val)}  "
          f"exp {expected:<10}  {v}")
    score_records.append({
        "prediction": pk, "rcc_type": rcc_type,
        "gene_a": gene_a, "gene_b": gene_b,
        "expected": expected, "r_value": r_val,
        "method": method, "low_power": lp,
        "approx": approx, "verdict": v,
    })

score_df = pd.DataFrame(score_records)
confirmed  = score_df["verdict"].str.startswith("CONFIRMED").sum()
denied     = score_df["verdict"].str.startswith("DENIED").sum()
untestable = score_df["verdict"].str.startswith("UNTESTABLE").sum()
total      = len(score_df)

print()
print(f"  TOTAL: {total}  |  CONFIRMED: {confirmed}  |  "
      f"DENIED: {denied}  |  UNTESTABLE: {untestable}")
print("  [APPROX] = sign approx from depth corr; "
      "[LOW-POWER] = cdRCC n=7 or chRCC caveat")

# ─────────────────────────────────────────────────────────────────────────────
# EXPORT
# ─────────────────────────────────────────────────────────────────────────────

print()
print("=" * 65)
print("EXPORTING")
print("=" * 65)

def save(df, name):
    path = os.path.join(OUT_DIR, name)
    df.to_csv(path, index=False)
    print(f"  {name}  ({len(df)} rows)")

save(score_df,     "prediction_scores_s2.csv")
save(obj1_df,      "ezh2_dnmt3a_coelev_s2.csv")
save(obj2_df,      "phase_transition_s2.csv")
save(obj3_df,      "il1rap_depth_corr_s2.csv")
save(akg_df,       "akg_deficit_scores_s2.csv")
save(ti_df,        "transition_index_s2.csv")
save(obj7_df,      "loxl2_runx1_depth_s2.csv")
save(chromatin_df, "chromatin_module_pairs_s2.csv")
save(phase_df,     "phase_gene_pairs_s2.csv")

with open(os.path.join(OUT_DIR, "chrcc_integration_s2.json"), "w") as fh:
    json.dump(chrcc_status, fh, indent=2)
print("  chrcc_integration_s2.json")

print()
print("=" * 65)
print("SCRIPT 2 COMPLETE")
print("=" * 65)
print("Next: 97x-2-results — score predictions against locked doc 97x-2")
print("[DONE]")
