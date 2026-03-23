"""
STRANDING DISPLACEMENT ANALYSIS
================================
OC-OBS-002 — Sea Turtle Stranding Analysis
OrganismCore — Eric Robert Lawson
March 2026

PURPOSE:
    Test whether the vector resultant of the geomagnetic
    gradient and AM false attractor predicts stranding
    location displacement better than the geomagnetic
    gradient alone.

    This is the force model test.

    If AM is acting as a deterministic navigational force:
      - The resultant bearing should predict which coastal
        segment the turtle strands at
      - The improvement in fit over geomagnetic-only
        prediction should be significant
      - The magnitude of displacement should correlate with
        the magnitude of the AM force relative to the
        geomagnetic force

    If the A1 result is geographic confound:
      - The resultant bearing should not predict coastal
        segment better than geomagnetic north alone
      - Improvement in fit = 0

APPROACH:
    1. Divide the study coastline into segments (~50 km each).
    2. For each stranding, compute:
         a. The coastal segment geomagnetic north points to
            (from the stranding location, project bearing
            to the nearest coastal segment)
         b. The coastal segment the resultant points to
    3. The actual stranding segment is known.
    4. Test: does the resultant prediction match the actual
       segment better than the geomagnetic prediction?
    5. Measure fit improvement as reduction in mean angular
       error (degrees) from geomagnetic-only to resultant.

SPECIES CONTROL:
    Run the identical analysis on CM (green turtle) and
    DC (leatherback) records from df_all.
    These species share the same geographic reporting bias
    but have different (or less studied) magnetic compass
    mechanisms.
    If the force model result is species-specific
    (stronger for CC than CM/DC), that supports mechanism.
    If all three species show identical results, that
    supports geographic confound.

GEOGRAPHIC NULL MODEL:
    For each stranding, randomly reassign the date while
    keeping the coordinate fixed. Recompute the AM false
    attractor using the real coordinate but a random date
    drawn from the dataset. The geographic bias is preserved.
    The navigation signal is broken.
    Run the displacement analysis on 1000 permutations.
    Compare real improvement in fit against null distribution.

INPUTS:
    stssn_with_resultant.csv   (from vector_resultant_computation.py)
    stssn_loggerhead_working.csv (for full dataset with dates)
    20260320_lawson.xlsx       (for CM and DC records)
    am_false_attractor_computation.py

OUTPUTS:
    displacement_analysis_results.md — full results document

REQUIRES:
    pip install pandas numpy scipy openpyxl
"""

import math
import os
import sys
import warnings
from datetime import datetime

import numpy as np
import pandas as pd
from scipy.stats import spearmanr, mannwhitneyu

try:
    from am_false_attractor_computation import AMFalseAttractor
    from vector_resultant_computation import (
        compute_resultant_batch,
        geomagnetic_horizontal_nT,
        coastal_approach_bearing,
        angular_diff,
    )
except ImportError as e:
    print(f"ERROR: {e}")
    print("Ensure am_false_attractor_computation.py and "
          "vector_resultant_computation.py are in this directory.")
    sys.exit(1)

# ── CONFIGURATION ─────────────────────────────────────────────

RESULTANT_CSV  = "stssn_with_resultant.csv"
WORKING_CSV    = "stssn_loggerhead_working.csv"
RAW_DATA_FILE  = "20260320_lawson.xlsx"
AM_CSV         = "am_stations_clean.csv"
RESULTS_MD     = "displacement_analysis_results.md"

N_PERMUTATIONS = 1000
ALPHA          = 0.05
YEAR           = 2026.2

# Coastal segment size in degrees latitude/longitude
# Approximately 50 km per 0.45° at these latitudes
SEGMENT_SIZE_DEG = 0.45


# ── COASTAL SEGMENT ASSIGNMENT ────────────────────────────────

def assign_segment(lat, lon, size=SEGMENT_SIZE_DEG):
    """
    Assign a stranding to a coastal segment.
    Segment key = (round(lat/size)*size, round(lon/size)*size)
    This creates a grid of ~50 km cells.
    """
    seg_lat = round(lat / size) * size
    seg_lon = round(lon / size) * size
    return (round(seg_lat, 4), round(seg_lon, 4))


def project_to_segment(from_lat, from_lon, bearing_deg,
                        distance_km=200.0):
    """
    Project a point (from_lat, from_lon) along bearing_deg
    for distance_km. Returns the destination (lat, lon).

    Used to find which coastal segment a bearing points toward.
    """
    R    = 6371.0
    d    = distance_km / R
    lat1 = math.radians(from_lat)
    lon1 = math.radians(from_lon)
    b    = math.radians(bearing_deg)

    lat2 = math.asin(
        math.sin(lat1) * math.cos(d)
        + math.cos(lat1) * math.sin(d) * math.cos(b)
    )
    lon2 = lon1 + math.atan2(
        math.sin(b) * math.sin(d) * math.cos(lat1),
        math.cos(d) - math.sin(lat1) * math.sin(lat2)
    )
    return math.degrees(lat2), math.degrees(lon2)


# ── FIT METRIC ────────────────────────────────────────────────

def bearing_to_segment_error(df, bearing_col):
    """
    For each stranding, compute the angular error between:
      - The segment the bearing_col points toward
        (projected 200 km along bearing from stranding coord)
      - The actual stranding segment

    Returns array of angular errors in degrees.
    """
    errors = []
    for _, row in df.iterrows():
        b = row.get(bearing_col)
        if pd.isna(b):
            continue
        lat = row["Latitude"]
        lon = row["Longitude"]

        # Project bearing to predicted landfall
        pred_lat, pred_lon = project_to_segment(lat, lon, b, 200.0)
        pred_seg = assign_segment(pred_lat, pred_lon)
        actual_seg = assign_segment(lat, lon)

        # Angular error = great-circle distance between
        # predicted segment centre and actual segment centre
        dlat = math.radians(pred_seg[0] - actual_seg[0])
        dlon = math.radians(pred_seg[1] - actual_seg[1])
        a = (math.sin(dlat / 2) ** 2
             + math.cos(math.radians(actual_seg[0]))
             * math.cos(math.radians(pred_seg[0]))
             * math.sin(dlon / 2) ** 2)
        dist_km = 2 * 6371.0 * math.asin(math.sqrt(max(0, min(1, a))))
        errors.append(dist_km)

    return np.array(errors)


# ── DISPLACEMENT MAGNITUDE CORRELATION ────────────────────────

def displacement_magnitude_correlation(df):
    """
    Test whether displacement magnitude (displacement_deg)
    correlates with the relative AM force magnitude
    (am_weight_scaled / geo_magnitude_nT).

    If AM is a real force: larger AM/geo ratio → larger
    displacement. Spearman r should be positive and significant.

    If result is geographic: no correlation.
    """
    valid = df[
        df["displacement_deg"].notna() &
        df["am_weight_scaled"].notna() &
        df["geo_magnitude_nT"].notna() &
        (df["geo_magnitude_nT"] > 0)
    ].copy()

    valid["force_ratio"] = (valid["am_weight_scaled"]
                            / valid["geo_magnitude_nT"])

    r, p = spearmanr(valid["force_ratio"], valid["displacement_deg"])
    return float(r), float(p), len(valid)


# ── GEOGRAPHIC NULL MODEL ─────────────────────────────────────

def run_null_model(df, ama, k, n_perms=N_PERMUTATIONS):
    """
    Permutation null model.

    For each permutation:
      - Randomly reassign dates within the dataset
        (preserving coordinates, breaking navigation signal)
      - The AM false attractor bearing does not change
        (it depends only on coordinate, not date)
      - But the MONTH changes, which affects which records
        are included in migration-season subsets
      - More importantly: this tests whether the observed
        improvement in fit could arise by chance given the
        geographic distribution of strandings

    For the force model test specifically:
      - Randomly shuffle the am_fa_bearing values across records
        (preserves the distribution of FA bearings and the
        distribution of stranding locations, but breaks the
        spatial correspondence between them)
      - Recompute resultant with shuffled FA bearings
      - Measure improvement in fit
      - Repeat n_perms times

    Returns:
        null_improvements — array of fit improvements under null
        real_improvement  — the observed fit improvement
        p_value           — fraction of null >= real
    """
    valid = df[
        df["am_fa_bearing"].notna() &
        df["resultant_bearing"].notna()
    ].copy().reset_index(drop=True)

    n = len(valid)
    if n < 100:
        return None, None, None

    # Real fit
    geo_errors      = bearing_to_segment_error(valid, "am_geo_bearing")
    resultant_errors = bearing_to_segment_error(valid, "resultant_bearing")
    real_improvement = float(np.mean(geo_errors)
                             - np.mean(resultant_errors))

    print(f"  Real improvement in fit: {real_improvement:.2f} km")
    print(f"  Running {n_perms} permutations...")

    null_improvements = []
    fa_bearings = valid["am_fa_bearing"].values.copy()

    for i in range(n_perms):
        shuffled_fa = np.random.permutation(fa_bearings)

        # Recompute resultant with shuffled FA
        null_improvements_i = []
        for j in range(n):
            geo_b   = valid.at[j, "am_geo_bearing"]
            geo_mag = valid.at[j, "geo_magnitude_nT"]
            am_sc   = valid.at[j, "am_weight_scaled"]

            if any(pd.isna(v) for v in [geo_b, geo_mag, am_sc]):
                continue

            from vector_resultant_computation import vector_resultant
            rb, _ = vector_resultant(geo_b, geo_mag,
                                     shuffled_fa[j], am_sc)
            if rb is not None:
                valid.at[j, "_null_resultant"] = rb

        null_errors = bearing_to_segment_error(valid, "_null_resultant")
        null_imp    = float(np.mean(geo_errors) - np.mean(null_errors))
        null_improvements.append(null_imp)

        if (i + 1) % 100 == 0:
            print(f"    {i + 1} / {n_perms}")

    null_improvements = np.array(null_improvements)
    p_value = float(np.mean(null_improvements >= real_improvement))

    return null_improvements, real_improvement, p_value


# ── SPECIES CONTROL ───────────────────────────────────────────

def run_species_control(raw_file, ama, k, species_code,
                        species_name):
    """
    Run the displacement analysis on a non-loggerhead species.
    Uses the same pipeline as the primary analysis.
    Returns mean displacement and fit improvement.
    """
    print(f"  Loading {species_code} ({species_name}) records...")
    df_raw = pd.read_excel(raw_file, sheet_name="Sheet1",
                           engine="openpyxl")
    df_sp  = df_raw[
        df_raw["Species"].str.strip().str.upper() == species_code
    ].copy()

    df_sp["ReportDate"]   = pd.to_datetime(df_sp["ReportDate"],
                                           errors="coerce")
    df_sp["strand_month"] = df_sp["ReportDate"].dt.month
    df_sp = df_sp.dropna(subset=["Latitude", "Longitude"])
    df_sp = df_sp.reset_index(drop=True)

    if len(df_sp) < 50:
        print(f"  {species_code}: insufficient records ({len(df_sp)})")
        return None

    print(f"  {species_code}: {len(df_sp):,} records — computing FA...")
    df_sp = ama.compute_batch(df_sp, lat_col="Latitude",
                              lon_col="Longitude",
                              progress_every=5000)

    df_sp["geo_magnitude_nT"] = [
        geomagnetic_horizontal_nT(row["Latitude"], row["Longitude"])
        for _, row in df_sp.iterrows()
    ]

    df_sp = compute_resultant_batch(df_sp, k=k)

    geo_errors = bearing_to_segment_error(df_sp, "am_geo_bearing")
    res_errors = bearing_to_segment_error(df_sp, "resultant_bearing")
    improvement = float(np.mean(geo_errors) - np.mean(res_errors))
    mean_disp   = float(df_sp["displacement_deg"].dropna().mean())

    print(f"  {species_code}: mean displacement={mean_disp:.2f}°  "
          f"fit improvement={improvement:.2f} km")

    return {
        "species":     species_code,
        "name":        species_name,
        "n":           len(df_sp),
        "mean_disp":   mean_disp,
        "improvement": improvement,
    }


# ── WRITE REPORT ──────────────────────────────────────────────

def write_report(df, real_improvement, null_improvements,
                 null_p, force_r, force_p, force_n,
                 species_results, run_date):

    lines = []
    w = lines.append

    def sig(p):
        if p is None:
            return "—"
        return "SIGNIFICANT" if float(p) < ALPHA else "null"

    w("# STRANDING DISPLACEMENT ANALYSIS")
    w("## Force Model Test — OC-OBS-002")
    w("## OrganismCore — Eric Robert Lawson")
    w(f"## Run date: {run_date}")
    w("")
    w("---")
    w("")
    w("## CORE QUESTION")
    w("")
    w("```")
    w("Does the vector resultant of the geomagnetic gradient")
    w("and AM false attractor predict stranding location")
    w("displacement better than the geomagnetic gradient alone?")
    w("")
    w("If yes: AM is acting as a deterministic navigational")
    w("force. The A1 result is not explained by geographic")
    w("reporting density.")
    w("")
    w("If no: the A1 result may be geographic confound.")
    w("```")
    w("")
    w("---")
    w("")
    w("## FIT IMPROVEMENT — PRIMARY RESULT")
    w("")
    w("```")
    if real_improvement is not None:
        w(f"Mean error (geomagnetic only):   see null model")
        w(f"Mean error (resultant):          see null model")
        w(f"Improvement in fit:              {real_improvement:.2f} km")
        w(f"  Positive = resultant predicts stranding segment")
        w(f"  better than geomagnetic north alone.")
        w(f"  Negative = resultant is worse than geo north alone.")
    else:
        w("Fit improvement: not computed (insufficient data)")
    w("```")
    w("")
    w("---")
    w("")
    w("## GEOGRAPHIC NULL MODEL")
    w("")
    w("```")
    if null_improvements is not None:
        w(f"Permutations:         {N_PERMUTATIONS}")
        w(f"Real improvement:     {real_improvement:.2f} km")
        w(f"Null mean:            {null_improvements.mean():.2f} km")
        w(f"Null SD:              {null_improvements.std():.2f} km")
        w(f"Null 95th pctile:     {np.percentile(null_improvements, 95):.2f} km")
        w(f"p (real >= null):     {null_p:.4f}")
        w(f"Result:               {sig(null_p)}")
        w("")
        w("Interpretation:")
        if null_p is not None and float(null_p) < ALPHA:
            w("  Real improvement exceeds null distribution.")
            w("  Geographic reporting density does not explain")
            w("  the fit improvement. Force model is supported.")
        else:
            w("  Real improvement does not exceed null distribution.")
            w("  Geographic reporting density may explain the result.")
            w("  Force model is not supported by this test.")
    else:
        w("Null model: not run (insufficient data)")
    w("```")
    w("")
    w("---")
    w("")
    w("## FORCE MAGNITUDE CORRELATION")
    w("")
    w("```")
    w("Test: Spearman correlation between")
    w("  am_weight_scaled / geo_magnitude_nT  (relative AM force)")
    w("  and displacement_deg  (resultant vs geo north)")
    w("")
    w("Prediction: positive correlation.")
    w("Larger AM force relative to geomagnetic field →")
    w("larger displacement of resultant from geo north.")
    w("")
    if force_r is not None:
        w(f"Spearman r:   {force_r:.4f}")
        w(f"p:            {force_p:.6f}")
        w(f"N:            {force_n:,}")
        w(f"Result:       {sig(force_p)}")
        w(f"Direction:    {'Predicted (positive)' if force_r > 0 else 'Opposite to prediction'}")
    else:
        w("Force correlation: not computed")
    w("```")
    w("")
    w("---")
    w("")
    w("## SPECIES CONTROL")
    w("")
    w("```")
    w("Loggerhead (CC) result compared against green turtle")
    w("(CM) and leatherback (DC).")
    w("")
    w("Same geographic reporting bias.")
    w("Different magnetic compass mechanisms.")
    w("")
    w("Prediction: CC shows strongest displacement signal.")
    w("If CM and DC show identical displacement, result is")
    w("geographic. If CC > CM >= DC, result is mechanistic.")
    w("")
    w(f"{'Species':<12} {'N':>8} {'Mean disp°':>12} "
      f"{'Fit improv (km)':>17}")
    w("─" * 55)

    for res in species_results:
        if res is not None:
            w(f"  {res['species']:<10} {res['n']:>8,} "
              f"{res['mean_disp']:>11.2f}° "
              f"{res['improvement']:>16.2f}")
        else:
            w("  (species result unavailable)")
    w("```")
    w("")
    w("---")
    w("")
    w("## OVERALL VERDICT")
    w("")
    w("```")
    w("Force model supported if ALL of:")
    w("  1. Real fit improvement > 0")
    w("  2. Null model p < 0.05")
    w("  3. Force magnitude correlation r > 0, p < 0.05")
    w("  4. CC displacement > CM and DC displacement")
    w("")
    supported = []
    not_supported = []

    if real_improvement is not None:
        if real_improvement > 0:
            supported.append("Fit improvement > 0")
        else:
            not_supported.append("Fit improvement <= 0")

    if null_p is not None:
        if float(null_p) < ALPHA:
            supported.append("Null model significant")
        else:
            not_supported.append("Null model not significant")

    if force_r is not None:
        if force_r > 0 and float(force_p) < ALPHA:
            supported.append("Force magnitude correlation positive")
        else:
            not_supported.append("Force magnitude correlation absent")

    for s in supported:
        w(f"  SUPPORTED:     {s}")
    for s in not_supported:
        w(f"  NOT SUPPORTED: {s}")

    if len(supported) == 3:
        w("")
        w("ALL THREE CRITERIA MET.")
        w("Force model is supported.")
        w("Geographic confound is not sufficient to explain result.")
    elif len(supported) == 0:
        w("")
        w("NO CRITERIA MET.")
        w("Force model is not supported.")
        w("Geographic confound cannot be excluded.")
    else:
        w("")
        w("PARTIAL SUPPORT.")
        w("Interpret with caution. See individual tests above.")
    w("```")
    w("")
    w("---")
    w("")
    w("## VERSION")
    w("```")
    w("Script:           stranding_displacement_analysis.py v1.0")
    w(f"Run date:         {run_date}")
    w("Classification:   Exploratory — pre-registered amendment")
    w("                  filed 2026-03-23 before running.")
    w("```")

    return "\n".join(lines)


# ── MAIN ──────────────────────────────────────────────────────

def main():
    run_date = datetime.now().strftime("%Y-%m-%d %H:%M")

    print("=" * 60)
    print("STRANDING DISPLACEMENT ANALYSIS")
    print("OC-OBS-002 — OrganismCore")
    print("=" * 60)

    for f in [RESULTANT_CSV, AM_CSV]:
        if not os.path.exists(f):
            print(f"\nERROR: Required file not found: {f}")
            sys.exit(1)

    # Load resultant dataset
    print(f"\nLoading: {RESULTANT_CSV}")
    df = pd.read_csv(RESULTANT_CSV)
    print(f"  Rows: {len(df):,}")
    print(f"  Resultant bearings: {df['resultant_bearing'].notna().sum():,}")

    # Get k from the dataset (am_weight_scaled / am_total_weight)
    valid_k = df[
        df["am_weight_scaled"].notna() &
        df["am_total_weight"].notna() &
        (df["am_total_weight"] > 0)
    ]
    if len(valid_k) > 0:
        k = float((valid_k["am_weight_scaled"]
                   / valid_k["am_total_weight"]).median())
        print(f"  Recovered k from data: {k:.6e}")
    else:
        k = 1.0
        print("  Could not recover k — using 1.0")

    # Load AM engine
    ama = AMFalseAttractor(AM_CSV)

    # Force magnitude correlation
    print("\nRunning force magnitude correlation...")
    force_r, force_p, force_n = displacement_magnitude_correlation(df)
    print(f"  Spearman r = {force_r:.4f},  p = {force_p:.6f},  "
          f"N = {force_n:,}")

    # Geographic null model
    print(f"\nRunning geographic null model "
          f"({N_PERMUTATIONS} permutations)...")
    null_improvements, real_improvement, null_p = run_null_model(
        df, ama, k, n_perms=N_PERMUTATIONS
    )

    if null_p is not None:
        print(f"  Real improvement:  {real_improvement:.2f} km")
        print(f"  Null mean:         {null_improvements.mean():.2f} km")
        print(f"  p:                 {null_p:.4f}")

    # Species control
    print("\nRunning species control...")
    species_results = []
    if os.path.exists(RAW_DATA_FILE):
        for code, name in [("CM", "Green turtle"),
                           ("DC", "Leatherback")]:
            res = run_species_control(RAW_DATA_FILE, ama, k,
                                      code, name)
            species_results.append(res)

        # Add loggerhead for comparison
        cc_disp = float(df["displacement_deg"].dropna().mean())
        geo_err = bearing_to_segment_error(df, "am_geo_bearing")
        res_err = bearing_to_segment_error(df, "resultant_bearing")
        cc_imp  = float(np.mean(geo_err) - np.mean(res_err))
        species_results.insert(0, {
            "species":     "CC",
            "name":        "Loggerhead",
            "n":           len(df),
            "mean_disp":   cc_disp,
            "improvement": cc_imp,
        })
    else:
        print(f"  {RAW_DATA_FILE} not found — skipping species control")

    # Write report
    report = write_report(
        df, real_improvement, null_improvements, null_p,
        force_r, force_p, force_n, species_results, run_date
    )
    with open(RESULTS_MD, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\nResults written: {RESULTS_MD}")

    print("\n" + "=" * 60)
    print("COMPLETE")
    print("=" * 60)
    print(f"  Results: {RESULTS_MD}")
    print()
    print("  Report all results regardless of direction.")


if __name__ == "__main__":
    main()
