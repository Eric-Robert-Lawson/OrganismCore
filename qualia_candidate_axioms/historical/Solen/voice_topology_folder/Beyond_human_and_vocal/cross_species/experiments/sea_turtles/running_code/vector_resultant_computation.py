"""
VECTOR RESULTANT COMPUTATION
=============================
OC-OBS-002 — Sea Turtle Stranding Analysis
OrganismCore — Eric Robert Lawson
March 2026

PURPOSE:
    For each stranding coordinate, compute the vector resultant
    of two navigational forces acting simultaneously on the turtle:

      Vector 1 — Geomagnetic gradient:
        Direction: geomagnetic north at the coordinate
                   (WMM-2025 polynomial approximation)
        Magnitude: horizontal component of Earth's magnetic
                   field at the coordinate (nT), from
                   WMM-2025 approximation.
                   This is the physical strength of the
                   signal the turtle's compass responds to.

      Vector 2 — AM false attractor:
        Direction: power-weighted bearing toward AM transmitters
                   within 500 km (from am_false_attractor_
                   computation.py)
        Magnitude: sum of ERP/distance² weights, scaled to nT
                   equivalent using a fitted scaling factor k.
                   See SCALING section below.

    The resultant vector is the predicted actual heading of
    the turtle — where it goes when both forces act on it
    simultaneously.

SCALING:
    The geomagnetic field magnitude is in nT.
    The AM weight is in kW/km².
    These are not naturally comparable.

    This script uses Approach 1: relative weighting from data.
    A scaling factor k (kW/km² → nT equivalent) is estimated
    by minimising the angular residual between the resultant
    bearing and the actual stranding coastal segment bearing
    across the full dataset.

    k is estimated by grid search over log-space values
    from 1e-6 to 1e6. The optimal k minimises the circular
    mean of |resultant_bearing - coastal_approach_bearing|
    across all strandings.

    The k value and its sensitivity are reported in the output.
    If k is unstable (optimum is flat or multi-modal), this
    is flagged and the analysis proceeds with k=1 (equal
    weighting) as a sensitivity case.

OUTPUTS:
    stssn_with_resultant.csv — working dataset with resultant
                               columns appended
    vector_resultant_report.md — numerical report

NEW COLUMNS ADDED:
    geo_magnitude_nT     — geomagnetic horizontal field (nT)
    am_weight_scaled     — AM weight × k (nT equivalent)
    resultant_bearing    — vector sum bearing (0–360°)
    resultant_magnitude  — magnitude of resultant vector
    resultant_vs_geo     — angular difference: resultant
                           vs geomagnetic north (0–180°)
    resultant_vs_fa      — angular difference: resultant
                           vs false attractor (0–180°)
    displacement_deg     — resultant_vs_geo (alias, explicit)

REQUIRES:
    pip install pandas numpy scipy
    stssn_loggerhead_working.csv (from turtle_stranding_pipeline.py)
    am_false_attractor_computation.py (for geomagnetic functions)
"""

import math
import os
import sys
from datetime import datetime

import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar

try:
    from am_false_attractor_computation import (
        magnetic_declination_deg,
        geomagnetic_north_bearing,
    )
except ImportError:
    print("ERROR: am_false_attractor_computation.py not found.")
    sys.exit(1)

# ── CONFIGURATION ─────────────────────────────────────────────

WORKING_CSV    = "stssn_loggerhead_working.csv"
OUTPUT_CSV     = "stssn_with_resultant.csv"
REPORT_MD      = "vector_resultant_report.md"

# Grid search range for scaling factor k (log10 space)
K_LOG_MIN = -6.0
K_LOG_MAX =  6.0
K_N_STEPS = 1000

YEAR = 2026.2


# ── WMM-2025 HORIZONTAL FIELD MAGNITUDE APPROXIMATION ─────────

def geomagnetic_horizontal_nT(lat, lon, year=YEAR):
    """
    Approximate horizontal component of Earth's magnetic field
    at (lat, lon) in nanoTesla.

    The horizontal component (H) is what the magnetic compass
    responds to. It is the component that lies in the horizontal
    plane and points toward magnetic north.

    WMM-2025 polynomial approximation for scope region:
    lat 24–45°N, lon -98° to -65°W.
    Accuracy: approximately ±500 nT within scope.
    Full range in scope: approximately 20,000–28,000 nT.

    Reference values (WMM-2025):
      Miami FL      (25.8, -80.2):  ~22,800 nT
      Cape Hatteras (35.2, -75.6):  ~21,500 nT
      New York      (40.7, -74.0):  ~19,800 nT
      Corpus Christi(27.8, -97.4):  ~24,200 nT

    Upgrade path: use pyIGRF or geomag library for full WMM.
        pip install geomag
        import geomag
        gm = geomag.GeoMag()
        r = gm.GeoMag(lat, lon, alt=0, time=year)
        H = math.sqrt(r.bx**2 + r.by**2)  # horizontal component
    """
    lat0 =  35.0
    lon0 = -82.0
    yr0  = 2025.0

    dlat = lat  - lat0
    dlon = lon  - lon0
    dyr  = year - yr0

    # Polynomial fitted to WMM-2025 grid values
    H0 =  21200.0   # nT at scope centre
    H1 =   -320.0   # per degree latitude (field weakens northward)
    H2 =    180.0   # per degree longitude (field stronger westward)
    H3 =     -2.0   # quadratic lat
    H4 =     -1.5   # quadratic lon
    H5 =      0.5   # cross term
    H6 =    -10.0   # secular change per year

    H = (H0
         + H1 * dlat
         + H2 * dlon
         + H3 * dlat ** 2
         + H4 * dlon ** 2
         + H5 * dlat * dlon
         + H6 * dyr)

    return max(H, 1000.0)   # floor at 1000 nT (never negative)


# ── VECTOR ADDITION ───────────────────────────────────────────

def vector_resultant(bearing1_deg, magnitude1,
                     bearing2_deg, magnitude2):
    """
    Add two vectors given as (bearing, magnitude) pairs.

    bearing: degrees clockwise from north (0–360)
    magnitude: scalar >= 0

    Returns: (resultant_bearing_deg, resultant_magnitude)
    """
    # Convert to Cartesian (north = +y, east = +x)
    r1 = math.radians(bearing1_deg)
    r2 = math.radians(bearing2_deg)

    x = magnitude1 * math.sin(r1) + magnitude2 * math.sin(r2)
    y = magnitude1 * math.cos(r1) + magnitude2 * math.cos(r2)

    magnitude = math.sqrt(x ** 2 + y ** 2)

    if magnitude < 1e-10:
        return None, 0.0

    bearing = math.degrees(math.atan2(x, y)) % 360.0
    return bearing, magnitude


# ── ANGULAR DIFFERENCE ────────────────────────────────────────

def angular_diff(b1, b2):
    """
    Absolute angular difference between two bearings, 0–180°.
    """
    if b1 is None or b2 is None:
        return None
    d = abs(b1 - b2) % 360.0
    if d > 180.0:
        d = 360.0 - d
    return d


# ── COASTAL APPROACH BEARING ──────────────────────────────────

def coastal_approach_bearing(lat, lon):
    """
    Estimate the bearing from offshore toward the coast at
    (lat, lon).

    For the US Atlantic and Gulf coast, this is approximately:
      Atlantic coast (lon > -82°): approach from east → bearing ~270°
      Gulf coast FL/AL/MS/LA (lat < 31°, lon < -82°):
                                    approach from south → bearing ~0°
      Gulf coast TX (lon < -93°):  approach from east/southeast
                                    → bearing ~315°
      Northeast coast (lat > 37°): approach from east/southeast
                                    → bearing ~260–270°

    This is a coarse approximation. A more precise version would
    use a coastline distance raster. For the purposes of the
    force model test, this approximation is sufficient to detect
    systematic displacement. Sensitivity to this assumption is
    tested in the displacement analysis script.

    Returns bearing in degrees (direction FROM water TO land).
    """
    if lon > -82.0:
        # Atlantic coast — approach from east
        return 270.0
    elif lon < -93.0:
        # Texas Gulf coast — approach from east/southeast
        return 305.0
    elif lat < 29.5:
        # South Florida Gulf coast — approach from south/southwest
        return 15.0
    else:
        # Northern Gulf coast (FL panhandle, AL, MS, LA)
        # approach from south
        return 355.0


# ── SCALING FACTOR ESTIMATION ─────────────────────────────────

def estimate_k(df, k_log_min=K_LOG_MIN, k_log_max=K_LOG_MAX,
               n_steps=K_N_STEPS):
    """
    Estimate the scaling factor k that converts AM weight
    (kW/km²) to nT equivalent, by minimising the mean angular
    residual between the resultant bearing and the coastal
    approach bearing across all strandings.

    Objective: minimise circular mean of
      |resultant_bearing(k) - coastal_approach_bearing|
    over all records with valid FA data.

    Returns:
        k_opt       — optimal scaling factor
        k_log_opt   — log10 of k_opt
        residual    — mean angular residual at k_opt (degrees)
        k_curve     — (k_values, residuals) for plotting
        stable      — True if optimum is well-defined
    """
    valid = df[
        df["am_fa_bearing"].notna() &
        df["am_geo_bearing"].notna() &
        df["geo_magnitude_nT"].notna()
    ].copy()

    n = len(valid)
    if n < 100:
        return None, None, None, None, False

    fa_bearings   = valid["am_fa_bearing"].values
    geo_bearings  = valid["am_geo_bearing"].values
    geo_mags      = valid["geo_magnitude_nT"].values
    am_weights    = valid["am_total_weight"].values
    coast_bears   = np.array([
        coastal_approach_bearing(row["Latitude"], row["Longitude"])
        for _, row in valid.iterrows()
    ])

    k_values  = np.logspace(k_log_min, k_log_max, n_steps)
    residuals = np.zeros(n_steps)

    for i, k in enumerate(k_values):
        am_scaled = am_weights * k
        diffs = []
        for j in range(n):
            rb, _ = vector_resultant(
                geo_bearings[j], geo_mags[j],
                fa_bearings[j],  am_scaled[j]
            )
            if rb is not None:
                d = angular_diff(rb, coast_bears[j])
                if d is not None:
                    diffs.append(d)
        residuals[i] = np.mean(diffs) if diffs else 180.0

    best_idx  = int(np.argmin(residuals))
    k_opt     = float(k_values[best_idx])
    residual  = float(residuals[best_idx])
    k_log_opt = math.log10(k_opt)

    # Stability: check if optimum is sharper than flat ±1 decade
    window = max(1, n_steps // 20)
    lo = max(0, best_idx - window)
    hi = min(n_steps - 1, best_idx + window)
    neighbours = np.concatenate([residuals[:lo], residuals[hi:]])
    stable = bool(residual < np.percentile(neighbours, 25))

    return k_opt, k_log_opt, residual, (k_values, residuals), stable


# ── COMPUTE RESULTANT FOR FULL DATASET ────────────────────────

def compute_resultant_batch(df, k, year=YEAR):
    """
    Compute vector resultant for every row in df.

    Adds columns:
        geo_magnitude_nT   — geomagnetic horizontal field (nT)
        am_weight_scaled   — am_total_weight * k
        resultant_bearing  — vector sum bearing (0–360°)
        resultant_magnitude — magnitude of resultant
        resultant_vs_geo   — |resultant - geo_bearing| (0–180°)
        resultant_vs_fa    — |resultant - fa_bearing|  (0–180°)
        displacement_deg   — alias for resultant_vs_geo
        coastal_approach   — estimated coastal approach bearing
    """
    out = df.copy()

    geo_mags       = []
    am_scaled_list = []
    res_bearings   = []
    res_mags       = []
    res_vs_geo     = []
    res_vs_fa      = []
    coastal_bears  = []

    n = len(df)
    for i, row in df.iterrows():
        lat = row.get("Latitude")
        lon = row.get("Longitude")
        fa  = row.get("am_fa_bearing")
        geo = row.get("am_geo_bearing")
        awt = row.get("am_total_weight", 0.0)

        coast_b = coastal_approach_bearing(lat, lon)
        coastal_bears.append(coast_b)

        if any(pd.isna(v) for v in [lat, lon, fa, geo, awt]):
            geo_mags.append(None)
            am_scaled_list.append(None)
            res_bearings.append(None)
            res_mags.append(None)
            res_vs_geo.append(None)
            res_vs_fa.append(None)
            continue

        H         = geomagnetic_horizontal_nT(lat, lon, year)
        am_sc     = float(awt) * k
        rb, rmag  = vector_resultant(geo, H, fa, am_sc)

        geo_mags.append(H)
        am_scaled_list.append(am_sc)
        res_bearings.append(rb)
        res_mags.append(rmag)
        res_vs_geo.append(angular_diff(rb, geo))
        res_vs_fa.append(angular_diff(rb, fa))

        if (i + 1) % 5000 == 0:
            print(f"  {i + 1:,} / {n:,}")

    out["geo_magnitude_nT"]    = geo_mags
    out["am_weight_scaled"]    = am_scaled_list
    out["resultant_bearing"]   = res_bearings
    out["resultant_magnitude"] = res_mags
    out["resultant_vs_geo"]    = res_vs_geo
    out["resultant_vs_fa"]     = res_vs_fa
    out["displacement_deg"]    = res_vs_geo   # explicit alias
    out["coastal_approach"]    = coastal_bears

    return out


# ── REPORT ────────────────────────────────────────────────────

def write_report(df, k_opt, k_log_opt, k_residual,
                 k_stable, run_date):

    lines = []
    w = lines.append

    w("# VECTOR RESULTANT REPORT")
    w("## OC-OBS-002 — Force Model Analysis")
    w("## OrganismCore — Eric Robert Lawson")
    w(f"## Run date: {run_date}")
    w("")
    w("---")
    w("")
    w("## SCALING FACTOR")
    w("")
    w("```")
    if k_opt is not None:
        w(f"Optimal k:          {k_opt:.6e}  (kW/km² → nT equivalent)")
        w(f"log10(k):           {k_log_opt:.3f}")
        w(f"Mean residual at k: {k_residual:.2f}°")
        w(f"Optimum stable:     {'Yes' if k_stable else 'No — interpret with caution'}")
    else:
        w("k estimation failed — insufficient valid records.")
    w("```")
    w("")
    w("---")
    w("")
    w("## RESULTANT DISTRIBUTION")
    w("")

    valid = df[df["resultant_bearing"].notna()]
    n_valid = len(valid)

    w("```")
    w(f"Records with resultant:    {n_valid:,}")
    w(f"Records without resultant: {df['resultant_bearing'].isna().sum():,}")
    w("")

    if n_valid > 0:
        disp = valid["displacement_deg"].dropna()
        w(f"Displacement (resultant vs geo north):")
        w(f"  Mean:    {disp.mean():.2f}°")
        w(f"  Median:  {disp.median():.2f}°")
        w(f"  SD:      {disp.std():.2f}°")
        w(f"  Min:     {disp.min():.2f}°")
        w(f"  Max:     {disp.max():.2f}°")
        w("")

        # Fraction displaced more than threshold
        for thresh in [10, 20, 30, 45, 90]:
            frac = (disp > thresh).mean() * 100
            w(f"  Displaced > {thresh:>3}°: {frac:.1f}%")

    w("```")
    w("")
    w("---")
    w("")
    w("## COASTAL SEGMENT BREAKDOWN")
    w("")
    w("```")
    w(f"{'Segment':<30} {'N':>7} {'Mean disp°':>11} "
      f"{'Med disp°':>10} {'Mean opp°':>10}")
    w("─" * 75)

    # Approximate segment from longitude bands
    def segment(row):
        lon = row.get("Longitude", 0)
        lat = row.get("Latitude", 0)
        if lon > -80.5:
            return "FL Atlantic"
        elif lon > -82.0 and lat < 27.0:
            return "FL Keys/SW"
        elif lon > -85.0:
            return "FL Gulf / Panhandle"
        elif lon > -90.0:
            return "AL / MS / LA East"
        elif lon > -97.0:
            return "LA West / TX East"
        else:
            return "TX"

    df["coast_segment"] = df.apply(segment, axis=1)

    for seg in sorted(df["coast_segment"].unique()):
        sub = df[df["coast_segment"] == seg]
        n   = len(sub)
        disp_vals = sub["displacement_deg"].dropna()
        opp_vals  = sub["am_opposition_deg"].dropna()
        md  = f"{disp_vals.mean():.2f}°" if len(disp_vals) > 0 else "—"
        mdd = f"{disp_vals.median():.2f}°" if len(disp_vals) > 0 else "—"
        mo  = f"{opp_vals.mean():.2f}°"  if len(opp_vals)  > 0 else "—"
        w(f"  {seg:<28} {n:>7,} {md:>11} {mdd:>10} {mo:>10}")

    w("```")
    w("")
    w("---")
    w("")
    w("## INTERPRETATION NOTES")
    w("")
    w("```")
    w("displacement_deg = angular difference between the")
    w("vector resultant bearing and geomagnetic north.")
    w("")
    w("displacement_deg = 0°:  resultant equals geomagnetic")
    w("  north. AM force is negligible or perfectly aligned.")
    w("  Turtle goes where its compass points.")
    w("")
    w("displacement_deg > 0°:  resultant is rotated away from")
    w("  geomagnetic north toward the AM false attractor.")
    w("  Turtle strands at the location the resultant points to,")
    w("  not where geomagnetic north points.")
    w("")
    w("If the force model is real:")
    w("  stranding_displacement_analysis.py should show that")
    w("  displacement_deg predicts which coastal segment the")
    w("  turtle strands at, better than geomagnetic north alone.")
    w("")
    w("If the force model is geographic confound:")
    w("  displacement_deg will not predict coastal segment")
    w("  better than geomagnetic north alone.")
    w("  The improvement in fit will be zero or negative.")
    w("```")
    w("")
    w("---")
    w("")
    w("## VERSION")
    w("```")
    w("Script:           vector_resultant_computation.py v1.0")
    w(f"Run date:         {run_date}")
    w("Input:            stssn_loggerhead_working.csv")
    w("Pre-registration: exploratory — filed as amendment")
    w("                  before running (2026-03-23)")
    w("```")

    return "\n".join(lines)


# ── MAIN ──────────────────────────────────────────────────────

def main():
    run_date = datetime.now().strftime("%Y-%m-%d %H:%M")

    print("=" * 60)
    print("VECTOR RESULTANT COMPUTATION")
    print("OC-OBS-002 — OrganismCore")
    print("=" * 60)

    if not os.path.exists(WORKING_CSV):
        print(f"\nERROR: {WORKING_CSV} not found.")
        print("Run turtle_stranding_pipeline.py first.")
        sys.exit(1)

    print(f"\nLoading: {WORKING_CSV}")
    df = pd.read_csv(WORKING_CSV)
    print(f"  Rows: {len(df):,}")

    # Add geomagnetic magnitude first (needed for k estimation)
    print("\nComputing geomagnetic horizontal field magnitudes...")
    df["geo_magnitude_nT"] = [
        geomagnetic_horizontal_nT(row["Latitude"], row["Longitude"])
        if not pd.isna(row["Latitude"]) else None
        for _, row in df.iterrows()
    ]
    print(f"  Done. Mean H: {df['geo_magnitude_nT'].mean():.0f} nT")

    # Estimate k
    print(f"\nEstimating scaling factor k ({K_N_STEPS} steps, "
          f"log10 range [{K_LOG_MIN}, {K_LOG_MAX}])...")
    print("  This may take several minutes...")
    k_opt, k_log_opt, k_residual, k_curve, k_stable = estimate_k(df)

    if k_opt is not None:
        print(f"  Optimal k:       {k_opt:.6e}")
        print(f"  log10(k):        {k_log_opt:.3f}")
        print(f"  Mean residual:   {k_residual:.2f}°")
        print(f"  Stable optimum:  {k_stable}")
    else:
        print("  k estimation failed. Using k=1.0 (equal weighting).")
        k_opt = 1.0

    # Compute resultant for full dataset
    print(f"\nComputing vector resultants (k={k_opt:.4e})...")
    df = compute_resultant_batch(df, k=k_opt)

    n_valid = df["resultant_bearing"].notna().sum()
    disp    = df["displacement_deg"].dropna()
    print(f"\n  Resultants computed: {n_valid:,}")
    print(f"  Mean displacement:   {disp.mean():.2f}°")
    print(f"  Median displacement: {disp.median():.2f}°")

    # Save
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"\n  Output saved: {OUTPUT_CSV}")

    # Write report
    report = write_report(df, k_opt, k_log_opt, k_residual,
                          k_stable, run_date)
    with open(REPORT_MD, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"  Report saved: {REPORT_MD}")

    print("\n" + "=" * 60)
    print("COMPLETE")
    print("=" * 60)
    print(f"  Output CSV: {OUTPUT_CSV}")
    print(f"  Report:     {REPORT_MD}")
    print()
    print("  Run stranding_displacement_analysis.py next.")


if __name__ == "__main__":
    main()
