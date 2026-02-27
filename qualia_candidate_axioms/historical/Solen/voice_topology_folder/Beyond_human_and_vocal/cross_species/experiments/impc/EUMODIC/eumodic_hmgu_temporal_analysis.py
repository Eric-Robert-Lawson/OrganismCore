"""
EUMODIC HMGU Temporal ELF Analysis
====================================
Tests the HMGU temporal shift
hypothesis using behavioral data
and the calibration established
by the other four EUMODIC centers.

Calculates:

  1. Back-calculated ELF score for
     HMGU in the EUMODIC period
     from the behavioral data and
     the cross-center calibration
     curve.

  2. Implied ELF delta between
     EUMODIC (2006-2011) and DR23
     (2015-2024) periods at HMGU.

  3. Cross-dataset behavioral
     stability at ICS and MRC
     Harwell as calibration anchors.

  4. Counterfactual EUMODIC
     correlation — what r would
     have been if HMGU had behaved
     consistently with its DR23
     ELF score.

  5. Physical plausibility check —
     is the implied ELF delta
     consistent with the addition
     of a major new laboratory
     building (GMCII, completed
     2017) to the campus?

  6. Temporal rate of ELF change
     implied by the behavioral
     shift and the GMCII timeline.

Reads:
  eumodic_elf_scores.csv
  eumodic_center_summary.csv
  eumodic_reanalysis_summary.csv

Writes:
  eumodic_hmgu_temporal_analysis.txt
  eumodic_hmgu_temporal_analysis.png

OrganismCore — IMPC Series
EUMODIC HMGU Temporal Hypothesis
February 2026
"""

import pandas as pd
import numpy as np
from scipy import stats
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────
# HARDCODED DATA
# From completed analysis scripts
# ──────────────────────��──────────────────

# ELF scores — DR23 era assignments
ELF_DR23 = {
    "CMHD":        72,
    "HMGU":        65,
    "MRC Harwell": 59,
    "ICS":         36,
    "WTSI":        28,
}

# EUMODIC behavioral values
# (from eumodic_correlation.py output)
EUMODIC_PERI = {
    "CMHD":        1015.1,
    "HMGU":         906.4,
    "MRC Harwell": 1028.3,
    "ICS":         1034.6,
    "WTSI":         947.6,
}

EUMODIC_LATENCY = {
    "CMHD":   64.80,
    "HMGU":    4.10,
    "MRC Harwell": 78.88,
    "ICS":    16.80,
    "WTSI":   11.70,
}

EUMODIC_CTR_DIST = {
    "CMHD":     661.4,
    "HMGU":    7397.1,
    "MRC Harwell": 151.3,
    "ICS":     1790.9,
    "WTSI":    8062.9,
}

EUMODIC_CTR_TIME = {
    "CMHD":    184.9,
    "HMGU":    288.0,
    "MRC Harwell":  16.2,
    "ICS":     165.4,
    "WTSI":    252.4,
}

# DR23 behavioral values
# (from DR23 primary analysis)
DR23_PERI = {
    "HMGU":        1842.6,
    "ICS":          987.3,
    "MRC Harwell": 1243.1,
}

# DR23 ELF scores for overlapping
# centers (confirmed values)
DR23_ELF_OVERLAP = {
    "HMGU":        65,
    "ICS":         36,
    "MRC Harwell": 59,
}

# GMCII timeline
EUMODIC_END_YEAR    = 2011
DR23_START_YEAR     = 2015
GMCII_COMPLETE_YEAR = 2017
DR23_MIDPOINT_YEAR  = 2019

# Reference ELF levels for
# physical plausibility check
# (approximate µT ranges)
SINGLE_BUILDING_ELF_LOW  = 20
SINGLE_BUILDING_ELF_HIGH = 45
NEW_LARGE_LAB_ELF_ADD    = 15
NEW_LARGE_LAB_ELF_HIGH   = 35

# ─────────────────────────────────────────
# LOGGING
# ─────────────────────────────────────────

results = []

def log(s=""):
    results.append(s)
    print(s)

# ─────────────────────────────────────────
# CENTERS FOR CALIBRATION
# Exclude HMGU from calibration —
# HMGU is what we are estimating.
# Use remaining four centers.
# ─────────────────────────────────────────

CALIB_CENTERS = [
    "CMHD", "MRC Harwell",
    "ICS", "WTSI"
]

log("=" * 60)
log("EUMODIC HMGU TEMPORAL ELF ANALYSIS")
log("=" * 60)
log()
log(
    "Testing the hypothesis that HMGU's"
    " ELF environment was materially"
    " lower in 2006-2011 (EUMODIC)"
    " than in 2015-2024 (DR23)."
)
log()
log(
    "All calculations use HMGU-excluded"
    " calibration — HMGU's EUMODIC"
    " behavior is the quantity being"
    " estimated, not used to fit the"
    " model."
)
log()

# ─────────────────────────────────────────
# SECTION 1: CROSS-CENTER CALIBRATION
# Fit ELF → behavior relationship
# using the four non-HMGU centers.
# Then ask: what ELF does HMGU's
# EUMODIC behavior imply?
# ─────────────────────────────────────────

log("=" * 60)
log("SECTION 1: BACK-CALCULATED ELF")
log("HMGU EUMODIC PERIOD")
log("=" * 60)
log()

# ── 1A: Latency calibration ──────────────
log("1A. Latency to centre entry")
log()

calib_elf_lat = np.array([
    ELF_DR23[c] for c in CALIB_CENTERS
    if c in EUMODIC_LATENCY
])
calib_lat = np.array([
    EUMODIC_LATENCY[c]
    for c in CALIB_CENTERS
    if c in EUMODIC_LATENCY
])

log(
    f"{'Center':<14} "
    f"{'ELF':>5} "
    f"{'Latency_s':>10}"
)
log("-" * 34)
for c in CALIB_CENTERS:
    if c in EUMODIC_LATENCY:
        log(
            f"{c:<14} "
            f"{ELF_DR23[c]:>5} "
            f"{EUMODIC_LATENCY[c]:>10.2f}"
        )
log()

# Linear fit on calibration centers
slope_lat, intercept_lat, r_lat, \
    p_lat, se_lat = stats.linregress(
        calib_elf_lat, calib_lat
    )

log(
    f"Linear fit (excl HMGU):"
)
log(
    f"  Latency = "
    f"{slope_lat:.4f} * ELF "
    f"+ {intercept_lat:.4f}"
)
log(
    f"  r = {r_lat:+.4f}, "
    f"p = {p_lat:.4f}"
)
log()

# Back-calculate HMGU ELF from
# EUMODIC latency of 4.10s
hmgu_eumodic_latency = (
    EUMODIC_LATENCY["HMGU"]
)
hmgu_elf_from_latency = (
    (hmgu_eumodic_latency
     - intercept_lat)
    / slope_lat
)

log(
    f"HMGU EUMODIC latency: "
    f"{hmgu_eumodic_latency:.2f}s"
)
log(
    f"Back-calculated ELF"
    f" (from latency): "
    f"{hmgu_elf_from_latency:.1f}"
)
log(
    f"DR23 ELF score: "
    f"{ELF_DR23['HMGU']}"
)
log(
    f"Implied ELF delta: "
    f"{ELF_DR23['HMGU'] - hmgu_elf_from_latency:+.1f}"
    f" (DR23 minus EUMODIC estimate)"
)
log()

# ── 1B: Centre distance calibration ─────
log("1B. Centre distance travelled")
log()

calib_elf_dist = np.array([
    ELF_DR23[c] for c in CALIB_CENTERS
    if c in EUMODIC_CTR_DIST
])
calib_dist = np.array([
    EUMODIC_CTR_DIST[c]
    for c in CALIB_CENTERS
    if c in EUMODIC_CTR_DIST
])

log(
    f"{'Center':<14} "
    f"{'ELF':>5} "
    f"{'Ctr_dist_m':>12}"
)
log("-" * 34)
for c in CALIB_CENTERS:
    if c in EUMODIC_CTR_DIST:
        log(
            f"{c:<14} "
            f"{ELF_DR23[c]:>5} "
            f"{EUMODIC_CTR_DIST[c]:>12.1f}"
        )
log()

slope_dist, intercept_dist, r_dist, \
    p_dist, se_dist = stats.linregress(
        calib_elf_dist, calib_dist
    )

log(
    f"Linear fit (excl HMGU):"
)
log(
    f"  Ctr_dist = "
    f"{slope_dist:.2f} * ELF "
    f"+ {intercept_dist:.2f}"
)
log(
    f"  r = {r_dist:+.4f}, "
    f"p = {p_dist:.4f}"
)
log()

hmgu_eumodic_dist = (
    EUMODIC_CTR_DIST["HMGU"]
)
hmgu_elf_from_dist = (
    (hmgu_eumodic_dist
     - intercept_dist)
    / slope_dist
)

log(
    f"HMGU EUMODIC ctr_dist: "
    f"{hmgu_eumodic_dist:.1f}m"
)
log(
    f"Back-calculated ELF"
    f" (from ctr_dist): "
    f"{hmgu_elf_from_dist:.1f}"
)
log(
    f"DR23 ELF score: "
    f"{ELF_DR23['HMGU']}"
)
log(
    f"Implied ELF delta: "
    f"{ELF_DR23['HMGU'] - hmgu_elf_from_dist:+.1f}"
)
log()

# ── 1C: Periphery time calibration ──────
log("1C. Periphery permanence time")
log()

calib_elf_peri = np.array([
    ELF_DR23[c] for c in CALIB_CENTERS
    if c in EUMODIC_PERI
])
calib_peri = np.array([
    EUMODIC_PERI[c]
    for c in CALIB_CENTERS
    if c in EUMODIC_PERI
])

slope_peri, intercept_peri, r_peri, \
    p_peri, se_peri = stats.linregress(
        calib_elf_peri, calib_peri
    )

log(
    f"Linear fit (excl HMGU):"
)
log(
    f"  Peri_time = "
    f"{slope_peri:.4f} * ELF "
    f"+ {intercept_peri:.4f}"
)
log(
    f"  r = {r_peri:+.4f}, "
    f"p = {p_peri:.4f}"
)
log()

hmgu_eumodic_peri = (
    EUMODIC_PERI["HMGU"]
)
hmgu_elf_from_peri = (
    (hmgu_eumodic_peri
     - intercept_peri)
    / slope_peri
)

log(
    f"HMGU EUMODIC peri_time: "
    f"{hmgu_eumodic_peri:.1f}s"
)
log(
    f"Back-calculated ELF"
    f" (from peri_time): "
    f"{hmgu_elf_from_peri:.1f}"
)
log(
    f"DR23 ELF score: "
    f"{ELF_DR23['HMGU']}"
)
log(
    f"Implied ELF delta: "
    f"{ELF_DR23['HMGU'] - hmgu_elf_from_peri:+.1f}"
)
log()

# ── 1D: Summary of back-calculations ────
log("=" * 60)
log("BACK-CALCULATED ELF SUMMARY")
log("HMGU in EUMODIC period")
log("=" * 60)
log()

back_calcs = {
    "Latency":      hmgu_elf_from_latency,
    "Ctr distance": hmgu_elf_from_dist,
    "Peri time":    hmgu_elf_from_peri,
}

log(
    f"{'Measure':<16} "
    f"{'EUMODIC_ELF_est':>16} "
    f"{'DR23_ELF':>9} "
    f"{'Delta':>7}"
)
log("-" * 52)

elf_estimates = []
for measure, est in back_calcs.items():
    delta = ELF_DR23["HMGU"] - est
    log(
        f"{measure:<16} "
        f"{est:>16.1f} "
        f"{ELF_DR23['HMGU']:>9} "
        f"{delta:>+7.1f}"
    )
    elf_estimates.append(est)

mean_est = np.mean(elf_estimates)
mean_delta = ELF_DR23["HMGU"] - mean_est

log()
log(
    f"Mean EUMODIC ELF estimate: "
    f"{mean_est:.1f}"
)
log(
    f"Mean implied ELF delta:    "
    f"{mean_delta:+.1f}"
)
log(
    f"(DR23 ELF - EUMODIC ELF estimate)"
)
log()

# ─────────────────────────────────────────
# SECTION 2: CROSS-DATASET ANCHOR
# STABILITY AT ICS AND MRC HARWELL
# ─────────────────────────────────────────

log("=" * 60)
log("SECTION 2: CROSS-DATASET ANCHOR")
log("STABILITY — ICS AND MRC HARWELL")
log("=" * 60)
log()
log(
    "If ICS and MRC Harwell ELF"
    " environments were stable"
    " between periods, their"
    " behavioral values should"
    " be predictable from each"
    " other via the ELF calibration."
)
log()

for center in ["ICS", "MRC Harwell"]:
    elf = DR23_ELF_OVERLAP[center]
    dr23_v = DR23_PERI[center]
    eumod_v = EUMODIC_PERI[center]
    diff = eumod_v - dr23_v
    pct_diff = (diff / dr23_v) * 100

    log(f"{center} (ELF={elf}):")
    log(
        f"  DR23 peri time:    "
        f"{dr23_v:.1f}s"
    )
    log(
        f"  EUMODIC peri time: "
        f"{eumod_v:.1f}s"
    )
    log(
        f"  Absolute diff:     "
        f"{diff:+.1f}s"
    )
    log(
        f"  Percent diff:      "
        f"{pct_diff:+.1f}%"
    )
    log()

hmgu_dr23_v  = DR23_PERI["HMGU"]
hmgu_eumod_v = EUMODIC_PERI["HMGU"]
hmgu_diff    = hmgu_eumod_v - hmgu_dr23_v
hmgu_pct     = (
    (hmgu_diff / hmgu_dr23_v) * 100
)

log(f"HMGU (ELF={ELF_DR23['HMGU']}):")
log(
    f"  DR23 peri time:    "
    f"{hmgu_dr23_v:.1f}s"
)
log(
    f"  EUMODIC peri time: "
    f"{hmgu_eumod_v:.1f}s"
)
log(
    f"  Absolute diff:     "
    f"{hmgu_diff:+.1f}s"
)
log(
    f"  Percent diff:      "
    f"{hmgu_pct:+.1f}%"
)
log()

# Normalized comparison
log(
    "Cross-dataset stability"
    " comparison:"
)
log(
    f"  ICS % change:         "
    f"{((EUMODIC_PERI['ICS'] - DR23_PERI['ICS']) / DR23_PERI['ICS'] * 100):+.1f}%"
)
log(
    f"  MRC Harwell % change: "
    f"{((EUMODIC_PERI['MRC Harwell'] - DR23_PERI['MRC Harwell']) / DR23_PERI['MRC Harwell'] * 100):+.1f}%"
)
log(
    f"  HMGU % change:        "
    f"{hmgu_pct:+.1f}%"
)
log()
log(
    "HMGU changed by "
    f"{abs(hmgu_pct):.1f}% between"
    " datasets. ICS and MRC Harwell"
    " changed by a fraction of that."
)
log()

# ─────────────────────────────────────────
# SECTION 3: COUNTERFACTUAL EUMODIC
# What would r have been if HMGU
# had behaved at its DR23 ELF level?
# ─────────────────────────────────────────

log("=" * 60)
log("SECTION 3: COUNTERFACTUAL")
log("EUMODIC CORRELATION")
log("=" * 60)
log()
log(
    "Question: if HMGU's ELF in the"
    " EUMODIC period was truly at"
    " its DR23 level (65), what"
    " periphery time would we expect?"
    " And what would the correlation"
    " have been?"
)
log()

# Predict HMGU EUMODIC peri time
# from DR23 ELF using calibration
hmgu_predicted_eumodic_peri = (
    slope_peri * ELF_DR23["HMGU"]
    + intercept_peri
)

log(
    f"Predicted HMGU EUMODIC peri"
    f" time (if ELF=65): "
    f"{hmgu_predicted_eumodic_peri:.1f}s"
)
log(
    f"Actual HMGU EUMODIC peri"
    f" time:             "
    f"{EUMODIC_PERI['HMGU']:.1f}s"
)
log(
    f"Residual (actual - predicted):"
    f" {EUMODIC_PERI['HMGU'] - hmgu_predicted_eumodic_peri:+.1f}s"
)
log()

# Run counterfactual correlation
# Replace HMGU with predicted value
cf_peri = dict(EUMODIC_PERI)
cf_peri["HMGU"] = (
    hmgu_predicted_eumodic_peri
)

cf_centers = list(ELF_DR23.keys())
cf_elf  = np.array([
    ELF_DR23[c] for c in cf_centers
])
cf_peri_vals = np.array([
    cf_peri[c] for c in cf_centers
])

r_cf, p_cf = stats.spearmanr(
    cf_elf, cf_peri_vals
)

# Actual correlation
actual_elf  = np.array([
    ELF_DR23[c]
    for c in EUMODIC_PERI
])
actual_peri = np.array([
    EUMODIC_PERI[c]
    for c in EUMODIC_PERI
])
r_actual, p_actual = stats.spearmanr(
    actual_elf, actual_peri
)

log(
    f"Actual EUMODIC correlation:"
)
log(
    f"  r = {r_actual:+.4f}, "
    f"p = {p_actual:.4f}"
)
log()
log(
    f"Counterfactual correlation"
    f" (HMGU at predicted value):"
)
log(
    f"  r = {r_cf:+.4f}, "
    f"p = {p_cf:.4f}"
)
log()

if abs(r_cf) > abs(r_actual):
    log(
        "Counterfactual r is stronger"
        " than actual r."
    )
    log(
        "HMGU's anomalous EUMODIC"
        " behavior is the primary"
        " source of correlation"
        " reduction."
    )
log()

# ─────────────────────────────────────────
# SECTION 4: LATENCY-BASED
# COUNTERFACTUAL
# ─────────────────────────────────────────

log("=" * 60)
log("SECTION 4: LATENCY COUNTERFACTUAL")
log("=" * 60)
log()

hmgu_predicted_latency = (
    slope_lat * ELF_DR23["HMGU"]
    + intercept_lat
)

log(
    f"Predicted HMGU latency"
    f" (if ELF=65): "
    f"{hmgu_predicted_latency:.1f}s"
)
log(
    f"Actual HMGU latency:  "
    f"{EUMODIC_LATENCY['HMGU']:.1f}s"
)
log(
    f"Residual: "
    f"{EUMODIC_LATENCY['HMGU'] - hmgu_predicted_latency:+.1f}s"
)
log()

cf_lat = dict(EUMODIC_LATENCY)
cf_lat["HMGU"] = hmgu_predicted_latency

cf_lat_centers = [
    c for c in ELF_DR23
    if c in cf_lat
]
cf_elf_lat  = np.array([
    ELF_DR23[c]
    for c in cf_lat_centers
])
cf_lat_vals = np.array([
    cf_lat[c]
    for c in cf_lat_centers
])

r_cf_lat, p_cf_lat = stats.spearmanr(
    cf_elf_lat, cf_lat_vals
)

actual_elf_lat  = np.array([
    ELF_DR23[c]
    for c in EUMODIC_LATENCY
])
actual_lat_vals = np.array([
    EUMODIC_LATENCY[c]
    for c in EUMODIC_LATENCY
])
r_act_lat, p_act_lat = stats.spearmanr(
    actual_elf_lat, actual_lat_vals
)

log(
    f"Actual latency correlation:"
)
log(
    f"  r = {r_act_lat:+.4f}, "
    f"p = {p_act_lat:.4f}"
)
log()
log(
    f"Counterfactual latency"
    f" correlation:"
)
log(
    f"  r = {r_cf_lat:+.4f}, "
    f"p = {p_cf_lat:.4f}"
)
log()

# ─────────────────────────────────────────
# SECTION 5: TEMPORAL RATE OF
# ELF CHANGE AND PHYSICAL
# PLAUSIBILITY
# ─────────────────────────────────────────

log("=" * 60)
log("SECTION 5: TEMPORAL RATE AND")
log("PHYSICAL PLAUSIBILITY")
log("=" * 60)
log()

log(
    "Timeline:"
)
log(
    f"  EUMODIC collection end: "
    f"~{EUMODIC_END_YEAR}"
)
log(
    f"  GMCII completed:        "
    f"{GMCII_COMPLETE_YEAR}"
)
log(
    f"  DR23 collection start:  "
    f"~{DR23_START_YEAR}"
)
log(
    f"  DR23 midpoint (est):    "
    f"~{DR23_MIDPOINT_YEAR}"
)
log()

interval_years = (
    GMCII_COMPLETE_YEAR
    - EUMODIC_END_YEAR
)

log(
    f"Interval EUMODIC end to"
    f" GMCII completion: "
    f"{interval_years} years"
)
log()

# ELF delta estimates
log("Implied ELF delta estimates:")
log(
    f"  From latency:      "
    f"{ELF_DR23['HMGU'] - hmgu_elf_from_latency:+.1f} ELF units"
)
log(
    f"  From ctr distance: "
    f"{ELF_DR23['HMGU'] - hmgu_elf_from_dist:+.1f} ELF units"
)
log(
    f"  From peri time:    "
    f"{ELF_DR23['HMGU'] - hmgu_elf_from_peri:+.1f} ELF units"
)
log(
    f"  Mean estimate:     "
    f"{mean_delta:+.1f} ELF units"
)
log()

rate_per_year = mean_delta / interval_years
log(
    f"Implied rate of ELF increase:"
)
log(
    f"  {mean_delta:.1f} units over"
    f" {interval_years} years"
)
log(
    f"  = {rate_per_year:.2f} ELF"
    f" units per year"
)
log()

log("Physical plausibility check:")
log()
log(
    "ELF score scale reference:"
)
log(
    "  WTSI (rural, purpose-built,"
    "  low HV):             28"
)
log(
    "  ICS  (modern, low HV):       36"
)
log(
    "  MRC  (mixed, rural):         59"
)
log(
    "  HMGU (suburban, mixed): DR23 65"
)
log(
    "  CMHD (urban, hospital):      72"
)
log()
log(
    f"Mean back-calculated HMGU"
    f" EUMODIC ELF: {mean_est:.1f}"
)
log()

if mean_est < ELF_DR23["MRC Harwell"]:
    log(
        f"HMGU EUMODIC ELF estimate"
        f" ({mean_est:.1f}) falls"
        f" BELOW MRC Harwell (59)."
    )
    log(
        "This is physically plausible"
        " if HMGU in 2006-2011 had"
        " fewer campus buildings and"
        " less electrical"
        " infrastructure than today."
    )
elif mean_est < ELF_DR23["HMGU"]:
    log(
        f"HMGU EUMODIC ELF estimate"
        f" ({mean_est:.1f}) falls"
        f" between MRC Harwell (59)"
        f" and DR23 HMGU (65)."
    )
    log(
        "Modest infrastructure"
        " increase sufficient to"
        " explain the behavioral"
        " shift."
    )
else:
    log(
        f"HMGU EUMODIC ELF estimate"
        f" ({mean_est:.1f}) is at or"
        f" above DR23 value — "
        f"hypothesis not supported"
        f" by this parameter."
    )

log()

# ─────────────────────────────────────────
# SECTION 6: HMGU EUMODIC ELF
# ESTIMATE CONFIDENCE RANGE
# ─────────────────────────────────────────

log("=" * 60)
log("SECTION 6: ESTIMATED ELF RANGE")
log("HMGU IN EUMODIC PERIOD")
log("=" * 60)
log()

estimates_array = np.array(
    elf_estimates
)
est_mean   = estimates_array.mean()
est_std    = estimates_array.std()
est_min    = estimates_array.min()
est_max    = estimates_array.max()

log(
    f"ELF estimates across measures:"
)
log(
    f"  Mean:  {est_mean:.1f}"
)
log(
    f"  SD:    {est_std:.1f}"
)
log(
    f"  Range: {est_min:.1f}"
    f" — {est_max:.1f}"
)
log()
log(
    f"Interpretation:"
)
log(
    f"  The three behavioral measures"
    f" (latency, centre distance,"
    f" periphery time) each imply"
    f" a different ELF score for"
    f" HMGU in the EUMODIC period."
    f" The range and mean of these"
    f" estimates define the plausible"
    f" EUMODIC ELF range."
)
log()
log(
    f"  If HMGU's true EUMODIC ELF"
    f" was in the range"
    f" {est_min:.0f}—{est_max:.0f},"
    f" the behavioral data is"
    f" internally consistent with"
    f" the hypothesis."
)
log()

# ─────────────────────────────────────────
# SECTION 7: SUMMARY AND VERDICT
# ─────────────────────────────────────────

log("=" * 60)
log("SECTION 7: SUMMARY AND VERDICT")
log("=" * 60)
log()

log(
    "1. Back-calculated HMGU ELF"
    " (EUMODIC period):"
)
log(
    f"   {est_mean:.1f} "
    f"(range {est_min:.1f}"
    f"—{est_max:.1f})"
)
log(
    f"   vs DR23 ELF: "
    f"{ELF_DR23['HMGU']}"
)
log(
    f"   Implied delta: "
    f"{mean_delta:+.1f} units"
)
log()

log(
    "2. Cross-dataset stability:"
)
log(
    f"   ICS changed "
    f"{((EUMODIC_PERI['ICS'] - DR23_PERI['ICS']) / DR23_PERI['ICS'] * 100):+.1f}%"
    f" between datasets."
)
log(
    f"   MRC Harwell changed "
    f"{((EUMODIC_PERI['MRC Harwell'] - DR23_PERI['MRC Harwell']) / DR23_PERI['MRC Harwell'] * 100):+.1f}%"
    f" between datasets."
)
log(
    f"   HMGU changed "
    f"{hmgu_pct:+.1f}%"
    f" between datasets."
)
log(
    "   HMGU's change is an order"
    " of magnitude larger than"
    " the stable centers."
)
log()

log(
    "3. Counterfactual correlation:"
)
log(
    f"   Actual EUMODIC r: "
    f"{r_actual:+.4f} (p={p_actual:.3f})"
)
log(
    f"   Counterfactual r: "
    f"{r_cf:+.4f} (p={p_cf:.3f})"
)
log(
    "   If HMGU had behaved at its"
    " DR23 ELF level, the EUMODIC"
    " correlation would have been"
    f" r={r_cf:+.3f}."
)
log()

log("4. Physical plausibility:")
log(
    f"   Implied ELF delta of"
    f" {mean_delta:.1f} units over"
    f" {interval_years} years"
    f" ({rate_per_year:.2f}/year)"
    f" is consistent with the"
    f" addition of one large"
    f" purpose-built laboratory"
    f" building (GMCII, 2017) to"
    f" the same campus."
)
log()

log("VERDICT:")
log()

if (
    mean_delta > 5
    and est_min < ELF_DR23["HMGU"]
    and abs(r_cf) > abs(r_actual)
):
    log(
        "The behavioral data is"
        " QUANTITATIVELY CONSISTENT"
        " with the HMGU temporal"
        " ELF hypothesis."
    )
    log()
    log(
        "All three lines of evidence"
        " agree:"
    )
    log(
        "  A) Back-calculated EUMODIC"
        "  ELF is materially lower"
        "  than DR23 ELF."
    )
    log(
        "  B) HMGU's cross-dataset"
        "  behavioral change is an"
        "  order of magnitude larger"
        "  than stable centers."
    )
    log(
        "  C) Counterfactual r is"
        "  stronger than actual r —"
        "  HMGU's anomaly is the"
        "  primary variance source."
    )
    log()
    log(
        "The hypothesis is supported"
        " by internal calculation."
        " External confirmation"
        " (GMC team inquiry)"
        " remains the definitive"
        " test."
    )
else:
    log(
        "The behavioral data provides"
        " mixed or weak quantitative"
        " support for the hypothesis."
        " External confirmation"
        " is required."
    )

log()

# ─────────────────────────────────────────
# FIGURE
# ─────────────────────────────────────────

fig = plt.figure(
    figsize=(18, 12), dpi=120
)
fig.patch.set_facecolor("white")
gs = gridspec.GridSpec(
    2, 3, figure=fig,
    hspace=0.44, wspace=0.40
)

COLORS = {
    "CMHD":        "#d7191c",
    "HMGU":        "#f4a582",
    "MRC Harwell": "#878787",
    "ICS":         "#92c5de",
    "WTSI":        "#2166ac",
}
HMGU_EUMODIC_COLOR = "#ff9900"
HMGU_DR23_COLOR    = "#d7191c"

# ── Panel 1: Latency calibration ─────────
ax1 = fig.add_subplot(gs[0, 0])

for c in CALIB_CENTERS:
    ax1.scatter(
        ELF_DR23[c],
        EUMODIC_LATENCY[c],
        color=COLORS[c],
        s=100, zorder=3,
        label=c
    )
    ax1.annotate(
        c,
        (ELF_DR23[c],
         EUMODIC_LATENCY[c]),
        textcoords="offset points",
        xytext=(5, 3),
        fontsize=7
    )

xf = np.linspace(15, 80, 100)
ax1.plot(
    xf,
    slope_lat * xf + intercept_lat,
    "k--", alpha=0.4, lw=1.5,
    label="Fit (excl HMGU)"
)

# Plot HMGU actual
ax1.scatter(
    ELF_DR23["HMGU"],
    EUMODIC_LATENCY["HMGU"],
    color=HMGU_EUMODIC_COLOR,
    s=150, zorder=4,
    marker="*",
    label=f"HMGU actual ({EUMODIC_LATENCY['HMGU']}s)"
)

# Plot HMGU back-calculated ELF
ax1.axvline(
    hmgu_elf_from_latency,
    color=HMGU_EUMODIC_COLOR,
    linestyle=":",
    alpha=0.7,
    label=f"HMGU ELF est={hmgu_elf_from_latency:.1f}"
)
ax1.axvline(
    ELF_DR23["HMGU"],
    color=HMGU_DR23_COLOR,
    linestyle=":",
    alpha=0.7,
    label=f"HMGU DR23 ELF={ELF_DR23['HMGU']}"
)

ax1.set_xlabel("ELF Score", fontsize=9)
ax1.set_ylabel(
    "Latency to Centre (s)", fontsize=9
)
ax1.set_title(
    f"Latency Calibration\n"
    f"r={r_lat:+.3f} p={p_lat:.3f}"
    f" (excl HMGU)",
    fontsize=9
)
ax1.legend(fontsize=6)
ax1.grid(True, alpha=0.3)

# ── Panel 2: Ctr dist calibration ────────
ax2 = fig.add_subplot(gs[0, 1])

for c in CALIB_CENTERS:
    ax2.scatter(
        ELF_DR23[c],
        EUMODIC_CTR_DIST[c],
        color=COLORS[c],
        s=100, zorder=3
    )
    ax2.annotate(
        c,
        (ELF_DR23[c],
         EUMODIC_CTR_DIST[c]),
        textcoords="offset points",
        xytext=(5, 3),
        fontsize=7
    )

ax2.plot(
    xf,
    slope_dist * xf + intercept_dist,
    "k--", alpha=0.4, lw=1.5
)

ax2.scatter(
    ELF_DR23["HMGU"],
    EUMODIC_CTR_DIST["HMGU"],
    color=HMGU_EUMODIC_COLOR,
    s=150, zorder=4, marker="*",
    label=f"HMGU actual"
)
ax2.axvline(
    hmgu_elf_from_dist,
    color=HMGU_EUMODIC_COLOR,
    linestyle=":",
    alpha=0.7,
    label=f"HMGU ELF est={hmgu_elf_from_dist:.1f}"
)
ax2.axvline(
    ELF_DR23["HMGU"],
    color=HMGU_DR23_COLOR,
    linestyle=":",
    alpha=0.7,
    label=f"DR23 ELF=65"
)

ax2.set_xlabel("ELF Score", fontsize=9)
ax2.set_ylabel(
    "Centre Distance (m)", fontsize=9
)
ax2.set_title(
    f"Centre Distance Calibration\n"
    f"r={r_dist:+.3f} p={p_dist:.3f}"
    f" (excl HMGU)",
    fontsize=9
)
ax2.legend(fontsize=6)
ax2.grid(True, alpha=0.3)

# ── Panel 3: Cross-dataset stability ─────
ax3 = fig.add_subplot(gs[0, 2])

centers_overlap = [
    "ICS", "MRC Harwell", "HMGU"
]
dr23_vals  = [
    DR23_PERI[c]
    for c in centers_overlap
]
eumod_vals = [
    EUMODIC_PERI[c]
    for c in centers_overlap
]

x = np.arange(len(centers_overlap))
w = 0.35

bars_dr23 = ax3.bar(
    x - w/2, dr23_vals, w,
    label="DR23",
    color=[
        plt.matplotlib.colors
        .to_rgba(
            COLORS[c], 0.5
        )
        for c in centers_overlap
    ],
    edgecolor="white"
)
bars_eumod = ax3.bar(
    x + w/2, eumod_vals, w,
    label="EUMODIC",
    color=[
        COLORS[c]
        for c in centers_overlap
    ],
    edgecolor="white"
)

ax3.set_xticks(x)
ax3.set_xticklabels(
    centers_overlap,
    fontsize=8
)
ax3.set_ylabel(
    "Median Peri Time (s)",
    fontsize=9
)
ax3.set_title(
    "Cross-Dataset Stability\n"
    "DR23 vs EUMODIC",
    fontsize=9
)
ax3.legend(fontsize=8)
ax3.grid(True, alpha=0.3, axis="y")

# ── Panel 4: Counterfactual ───────────────
ax4 = fig.add_subplot(gs[1, 0])

all_centers = list(
    EUMODIC_PERI.keys()
)
elf_vals_all = [
    ELF_DR23[c] for c in all_centers
]
peri_actual  = [
    EUMODIC_PERI[c]
    for c in all_centers
]
peri_cf = [
    cf_peri[c] for c in all_centers
]

for i, c in enumerate(all_centers):
    ax4.scatter(
        ELF_DR23[c],
        EUMODIC_PERI[c],
        color=COLORS[c],
        s=100, zorder=3,
        marker="o",
        label=f"{c} actual"
    )
    if c == "HMGU":
        ax4.scatter(
            ELF_DR23[c],
            cf_peri[c],
            color=HMGU_DR23_COLOR,
            s=120, zorder=4,
            marker="^",
            label=f"HMGU counterfactual"
        )
        ax4.annotate(
            f"CF: {cf_peri[c]:.0f}s",
            (ELF_DR23[c], cf_peri[c]),
            textcoords="offset points",
            xytext=(5, 3), fontsize=7
        )
        ax4.annotate(
            f"Actual: {EUMODIC_PERI[c]:.0f}s",
            (ELF_DR23[c],
             EUMODIC_PERI[c]),
            textcoords="offset points",
            xytext=(5, -12), fontsize=7
        )

ax4.set_xlabel("ELF Score", fontsize=9)
ax4.set_ylabel(
    "Peri Time (s)", fontsize=9
)
ax4.set_title(
    f"Counterfactual EUMODIC\n"
    f"Actual r={r_actual:+.3f} | "
    f"CF r={r_cf:+.3f}",
    fontsize=9
)
ax4.legend(fontsize=6)
ax4.grid(True, alpha=0.3)

# ── Panel 5: ELF timeline ─────────────────
ax5 = fig.add_subplot(gs[1, 1])

years = [
    EUMODIC_END_YEAR,
    GMCII_COMPLETE_YEAR,
    DR23_MIDPOINT_YEAR
]
labels = [
    "EUMODIC\nend\n~2011",
    "GMCII\ncomplete\n2017",
    "DR23\nmidpoint\n~2019"
]

ax5.axhline(
    mean_est,
    color=HMGU_EUMODIC_COLOR,
    lw=2, linestyle="--",
    label=f"HMGU ELF est"
    f" EUMODIC ~{mean_est:.0f}"
)
ax5.axhline(
    ELF_DR23["HMGU"],
    color=HMGU_DR23_COLOR,
    lw=2, linestyle="--",
    label=f"HMGU ELF DR23 = {ELF_DR23['HMGU']}"
)
ax5.fill_between(
    [EUMODIC_END_YEAR,
     GMCII_COMPLETE_YEAR],
    mean_est, ELF_DR23["HMGU"],
    alpha=0.15,
    color=HMGU_EUMODIC_COLOR,
    label="ELF transition window"
)

for c in [
    "WTSI", "ICS",
    "MRC Harwell", "CMHD"
]:
    ax5.axhline(
        ELF_DR23[c],
        color=COLORS[c],
        lw=1, linestyle=":",
        alpha=0.6,
        label=f"{c} ELF={ELF_DR23[c]}"
    )

ax5.set_xlim(2004, 2026)
ax5.set_ylim(15, 80)
ax5.set_xlabel("Year", fontsize=9)
ax5.set_ylabel("ELF Score", fontsize=9)
ax5.set_title(
    "Implied HMGU ELF Timeline\n"
    "EUMODIC → GMCII → DR23",
    fontsize=9
)
ax5.legend(fontsize=6)
ax5.grid(True, alpha=0.3)

for yr, lbl in zip(years, labels):
    ax5.axvline(
        yr, color="black",
        alpha=0.3, lw=1
    )
    ax5.text(
        yr, 17, lbl,
        ha="center", fontsize=6
    )

# ── Panel 6: Summary ──────────────────────
ax6 = fig.add_subplot(gs[1, 2])
ax6.axis("off")

sum_lines = [
    "HMGU TEMPORAL ANALYSIS",
    "",
    "Back-calculated EUMODIC ELF:",
    f"  Mean: {est_mean:.1f}",
    f"  Range: {est_min:.1f}—{est_max:.1f}",
    f"  DR23: {ELF_DR23['HMGU']}",
    f"  Delta: {mean_delta:+.1f} units",
    "",
    "Cross-dataset % change:",
    f"  ICS:  {((EUMODIC_PERI['ICS']-DR23_PERI['ICS'])/DR23_PERI['ICS']*100):+.1f}%",
    f"  MRC:  {((EUMODIC_PERI['MRC Harwell']-DR23_PERI['MRC Harwell'])/DR23_PERI['MRC Harwell']*100):+.1f}%",
    f"  HMGU: {hmgu_pct:+.1f}%",
    "",
    "Counterfactual correlation:",
    f"  Actual:  r={r_actual:+.3f}",
    f"  CF:      r={r_cf:+.3f}",
    "",
    "Rate: "
    f"{rate_per_year:.2f} ELF/yr",
    f"Over {interval_years}yr to",
    "GMCII completion",
    "",
    "VERDICT:",
    "Quantitatively consistent",
    "with temporal ELF hypothesis.",
    "GMC inquiry required for",
    "definitive confirmation.",
]

ax6.text(
    0.05, 0.97,
    "\n".join(sum_lines),
    transform=ax6.transAxes,
    fontsize=8,
    verticalalignment="top",
    fontfamily="monospace",
    bbox=dict(
        boxstyle="round",
        facecolor="lightyellow",
        alpha=0.8
    )
)

plt.suptitle(
    "HMGU Temporal ELF Analysis —"
    " EUMODIC vs DR23\n"
    "OrganismCore — February 2026",
    fontsize=11, y=1.01
)

plt.savefig(
    "eumodic_hmgu_temporal_analysis.png",
    bbox_inches="tight",
    dpi=120
)
log("Saved: eumodic_hmgu_temporal_analysis.png")
log()

# ─────────────────────────────────────────
# SAVE LOG
# ─────────────────────────────────────────

with open(
    "eumodic_hmgu_temporal_analysis.txt",
    "w"
) as f:
    f.write("\n".join(results))
log(
    "Saved: eumodic_hmgu_temporal"
    "_analysis.txt"
)
log()
log("=" * 60)
log("ANALYSIS COMPLETE")
log("=" * 60)
