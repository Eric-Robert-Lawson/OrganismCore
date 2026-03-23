"""
STRANDING DISPLACEMENT ANALYSIS v2
====================================
OC-OBS-002 — Sea Turtle Stranding Analysis
OrganismCore — Eric Robert Lawson
March 2026

CHANGES FROM v1:
    1. Projection direction corrected.
       v1 projected FORWARD from stranding location along
       resultant bearing — geometrically wrong. The turtle
       is already at the stranding location. Forward
       projection predicts where it would go next, not
       where it came from.

       v2 projects BACKWARD — from the stranding location
       along the RECIPROCAL of the resultant bearing to
       find the predicted offshore origin corridor.

    2. Segment resolution reduced from 0.45° (~50 km)
       to 0.10° (~11 km) for primary CC analysis.
       Loggerhead natal homing fidelity operates at finer
       resolution than the original 50 km grid.
       Sensitivity runs at 0.20° and 0.45° also produced.

    3. Fit metric clarified.
       For each stranding, the test now asks:
         - Project backward along reciprocal of resultant
           bearing 300 km offshore. Call this the
           predicted origin point.
         - Project backward along reciprocal of geomagnetic
           north 300 km offshore. Call this the geo origin.
         - The ACTUAL origin is unknown but turtles in the
           same coastal segment should have come from
           similar offshore positions.
         - Within each coastal segment, does the resultant
           origin cluster more tightly than the geo origin?
         - Tighter clustering = better prediction.

    4. Null model uses bearing shuffle (same as v1).

    5. Species control uses same corrected method.

OUTPUTS:
    displacement_analysis_v2_results.md

REQUIRES:
    stssn_with_resultant.csv
    am_stations_clean.csv
    20260320_lawson.xlsx
    am_false_attractor_computation.py
    vector_resultant_computation.py
"""

import math
import os
import sys
from datetime import datetime

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

try:
    from am_false_attractor_computation import AMFalseAttractor
    from vector_resultant_computation import (
        compute_resultant_batch,
        geomagnetic_horizontal_nT,
        angular_diff,
        vector_resultant,
    )
except ImportError as e:
    print(f"ERROR: {e}")
    sys.exit(1)

# ── CONFIGURATION ─────────────────────────────────────────────

RESULTANT_CSV  = "stssn_with_resultant.csv"
RAW_DATA_FILE  = "20260320_lawson.xlsx"
AM_CSV         = "am_stations_clean.csv"
RESULTS_MD     = "displacement_analysis_v2_results.md"

# Projection distance offshore for origin corridor (km)
BACKPROJECT_KM = 300.0

# Segment resolutions to test
# Primary: 0.10° (~11 km) — loggerhead natal homing scale
# Sensitivity: 0.20° (~22 km), 0.45° (~50 km)
SEGMENT_SIZES  = {
    "10km":  0.10,
    "22km":  0.20,
    "50km":  0.45,
}
PRIMARY_RES    = "10km"

N_PERMUTATIONS = 1000
ALPHA          = 0.05
YEAR           = 2026.2


# ── RECIPROCAL BEARING ────────────────────────────────────────

def reciprocal(bearing_deg):
    """Return the reciprocal (opposite) bearing."""
    return (bearing_deg + 180.0) % 360.0


# ── HAVERSINE PROJECTION ──────────────────────────────────────

def project_point(lat, lon, bearing_deg, distance_km):
    """
    Project from (lat, lon) along bearing_deg for distance_km.
    Returns (dest_lat, dest_lon).
    """
    R    = 6371.0
    d    = distance_km / R
    lat1 = math.radians(lat)
    lon1 = math.radians(lon)
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


# ── GREAT CIRCLE DISTANCE ─────────────────────────────────────

def haversine_km(lat1, lon1, lat2, lon2):
    """Great-circle distance in km between two points."""
    R    = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a    = (math.sin(dlat / 2) ** 2
            + math.cos(math.radians(lat1))
            * math.cos(math.radians(lat2))
            * math.sin(dlon / 2) ** 2)
    return 2 * R * math.asin(math.sqrt(max(0.0, min(1.0, a))))


# ── SEGMENT ASSIGNMENT ────────────────────────────────────────

def assign_segment(lat, lon, size):
    seg_lat = round(lat / size) * size
    seg_lon = round(lon / size) * size
    return (round(seg_lat, 6), round(seg_lon, 6))


# ── CORE FIT METRIC — ORIGIN CORRIDOR CLUSTERING ─────────────

def origin_clustering_score(df, bearing_col, seg_size,
                             backproject_km=BACKPROJECT_KM):
    """
    For each coastal segment, compute the mean pairwise
    distance between predicted offshore origin points
    for all strandings in that segment.

    Lower mean pairwise distance = tighter clustering =
    better prediction (origins are consistent with turtles
    having come from the same offshore corridor).

    This is the corrected metric.

    For each stranding:
      1. Project backward along reciprocal of bearing_col
         for backproject_km to get predicted origin point.
      2. Group by coastal segment.
      3. Within each segment, compute mean pairwise
         great-circle distance between origin points.
      4. Average across all segments (weighted by N).

    Lower score = tighter clustering = better model.
    Improvement = geo_score - resultant_score.
    Positive improvement = resultant is better.
    """
    valid = df[df[bearing_col].notna()].copy()

    # Compute origin points
    origins = []
    for _, row in valid.iterrows():
        b   = row[bearing_col]
        lat = row["Latitude"]
        lon = row["Longitude"]
        # Backward projection: reciprocal bearing
        orig_lat, orig_lon = project_point(
            lat, lon, reciprocal(b), backproject_km
        )
        seg = assign_segment(lat, lon, seg_size)
        origins.append({
            "seg":      seg,
            "orig_lat": orig_lat,
            "orig_lon": orig_lon,
        })

    origins_df = pd.DataFrame(origins)
    seg_scores = []
    seg_weights = []

    for seg, grp in origins_df.groupby("seg"):
        n = len(grp)
        if n < 2:
            continue
        lats = grp["orig_lat"].values
        lons = grp["orig_lon"].values
        # Mean pairwise distance
        dists = []
        for i in range(n):
            for j in range(i + 1, n):
                dists.append(haversine_km(
                    lats[i], lons[i], lats[j], lons[j]
                ))
        seg_scores.append(np.mean(dists))
        seg_weights.append(n)

    if not seg_scores:
        return None

    # Weighted mean across segments
    return float(np.average(seg_scores, weights=seg_weights))


# ── FIT IMPROVEMENT ───────────────────────────────────────────

def fit_improvement(df, seg_size):
    """
    Compute improvement in origin clustering score:
      geo_score - resultant_score

    Positive = resultant clusters better = force model
    predicts approach corridor better than geo alone.
    """
    geo_score = origin_clustering_score(
        df, "am_geo_bearing", seg_size
    )
    res_score = origin_clustering_score(
        df, "resultant_bearing", seg_size
    )
    if geo_score is None or res_score is None:
        return None, None, None
    improvement = geo_score - res_score
    return improvement, geo_score, res_score


# ── NULL MODEL ────────────────────────────────────────────────

def run_null_model(df, seg_size, n_perms=N_PERMUTATIONS):
    """
    Shuffle am_fa_bearing values across records.
    Recompute resultant with shuffled FA.
    Measure improvement in origin clustering score.
    Repeat n_perms times.

    Returns:
        null_improvements — array of null improvements
        real_improvement  — observed improvement
        p_value           — fraction of null >= real
        geo_score         — geomagnetic-only score
        res_score         — resultant score
    """
    valid = df[
        df["am_fa_bearing"].notna() &
        df["resultant_bearing"].notna() &
        df["am_geo_bearing"].notna() &
        df["geo_magnitude_nT"].notna() &
        df["am_weight_scaled"].notna()
    ].copy().reset_index(drop=True)

    n = len(valid)
    if n < 100:
        return None, None, None, None, None

    # Real improvement
    real_imp, geo_sc, res_sc = fit_improvement(valid, seg_size)
    print(f"  Geo score:        {geo_sc:.2f} km")
    print(f"  Resultant score:  {res_sc:.2f} km")
    print(f"  Real improvement: {real_imp:.2f} km")

    fa_bearings = valid["am_fa_bearing"].values.copy()
    geo_bearings = valid["am_geo_bearing"].values
    geo_mags = valid["geo_magnitude_nT"].values
    am_scaled = valid["am_weight_scaled"].values

    null_improvements = []
    print(f"  Running {n_perms} permutations...")

    for i in range(n_perms):
        shuffled_fa = np.random.permutation(fa_bearings)

        # Recompute resultant with shuffled FA bearings
        null_resultants = []
        for j in range(n):
            rb, _ = vector_resultant(
                geo_bearings[j], geo_mags[j],
                shuffled_fa[j],  am_scaled[j]
            )
            null_resultants.append(rb)

        valid["_null_resultant"] = null_resultants
        null_valid = valid[valid["_null_resultant"].notna()]

        null_geo = origin_clustering_score(
            null_valid, "am_geo_bearing", seg_size
        )
        null_res = origin_clustering_score(
            null_valid, "_null_resultant", seg_size
        )
        if null_geo is not None and null_res is not None:
            null_improvements.append(null_geo - null_res)

        if (i + 1) % 100 == 0:
            print(f"    {i + 1} / {n_perms}")

    null_improvements = np.array(null_improvements)
    p_value = float(np.mean(null_improvements >= real_imp))

    return null_improvements, real_imp, p_value, geo_sc, res_sc


# ── MULTI-RESOLUTION TEST ���────────────────────────────────────

def run_multi_resolution(df):
    """
    Run fit improvement at all three resolutions.
    Returns dict of results.
    """
    results = {}
    for name, size in SEGMENT_SIZES.items():
        imp, geo_sc, res_sc = fit_improvement(df, size)
        results[name] = {
            "size_deg":    size,
            "improvement": imp,
            "geo_score":   geo_sc,
            "res_score":   res_sc,
        }
        print(f"  {name}: improvement={imp:.2f} km  "
              f"(geo={geo_sc:.2f}, res={res_sc:.2f})")
    return results


# ── PREDICTIVE MAP ENGINE ─────────────────────────────────────

def build_risk_map(df, seg_size, top_n=20):
    """
    Build the 2026 migration season risk map.

    For each coastal segment:
      - Mean resultant displacement (degrees)
      - Mean opposition angle
      - Migration season N (Apr-Jun, Aug-Nov)
      - Dominant AM station bearing contribution
      - Predicted approach corridor
        (reciprocal of mean resultant bearing)
      - Risk score = migration_N * mean_displacement / 90

    Returns DataFrame ranked by risk score, top_n segments.
    """
    mig_months = [4, 5, 6, 8, 9, 10, 11]

    df["seg"] = df.apply(
        lambda r: assign_segment(r["Latitude"], r["Longitude"],
                                 seg_size), axis=1
    )

    if "strand_month" not in df.columns:
        if "ReportDate" in df.columns:
            df["strand_month"] = pd.to_datetime(
                df["ReportDate"], errors="coerce"
            ).dt.month
        else:
            df["strand_month"] = None

    records = []
    for seg, grp in df.groupby("seg"):
        n_total = len(grp)
        if "strand_month" in grp.columns and grp["strand_month"].notna().any():
            n_mig = grp[grp["strand_month"].isin(mig_months)].shape[0]
        else:
            n_mig = n_total

        mean_disp = grp["displacement_deg"].dropna().mean()
        mean_opp  = grp["am_opposition_deg"].dropna().mean() \
            if "am_opposition_deg" in grp.columns else None
        mean_res_bearing = None

        res_b = grp["resultant_bearing"].dropna()
        if len(res_b) > 0:
            # Circular mean of resultant bearings
            sin_mean = np.sin(np.radians(res_b)).mean()
            cos_mean = np.cos(np.radians(res_b)).mean()
            mean_res_bearing = math.degrees(
                math.atan2(sin_mean, cos_mean)
            ) % 360.0

        approach_corridor = (
            reciprocal(mean_res_bearing)
            if mean_res_bearing is not None else None
        )

        risk_score = (
            n_mig * (mean_disp / 90.0)
            if mean_disp is not None else 0.0
        )

        records.append({
            "seg_lat":          seg[0],
            "seg_lon":          seg[1],
            "n_total":          n_total,
            "n_migration":      n_mig,
            "mean_disp_deg":    round(mean_disp, 2)
                                if mean_disp is not None else None,
            "mean_opp_deg":     round(mean_opp, 2)
                                if mean_opp is not None else None,
            "mean_resultant_bearing": round(mean_res_bearing, 1)
                                if mean_res_bearing is not None
                                else None,
            "approach_corridor_bearing": round(approach_corridor, 1)
                                if approach_corridor is not None
                                else None,
            "risk_score":       round(risk_score, 1),
        })

    risk_df = pd.DataFrame(records)
    risk_df = risk_df.sort_values("risk_score", ascending=False)
    return risk_df.head(top_n).reset_index(drop=True)


# ── SPECIES CONTROL ───────────────────────────────────────────

def run_species_control(raw_file, ama, k, species_code,
                        species_name, seg_size):
    print(f"  Loading {species_code} ({species_name})...")
    df_raw = pd.read_excel(raw_file, sheet_name="Sheet1",
                           engine="openpyxl")
    df_sp  = df_raw[
        df_raw["Species"].str.strip().str.upper() == species_code
    ].copy()
    df_sp  = df_sp.dropna(subset=["Latitude", "Longitude"])
    df_sp  = df_sp.reset_index(drop=True)

    if len(df_sp) < 50:
        print(f"  {species_code}: insufficient records")
        return None

    print(f"  {species_code}: {len(df_sp):,} records")
    df_sp = ama.compute_batch(df_sp, lat_col="Latitude",
                              lon_col="Longitude",
                              progress_every=5000)
    df_sp["geo_magnitude_nT"] = [
        geomagnetic_horizontal_nT(r["Latitude"], r["Longitude"])
        for _, r in df_sp.iterrows()
    ]
    df_sp = compute_resultant_batch(df_sp, k=k)

    imp, geo_sc, res_sc = fit_improvement(df_sp, seg_size)
    mean_disp = float(df_sp["displacement_deg"].dropna().mean())

    print(f"  {species_code}: disp={mean_disp:.2f}°  "
          f"improvement={imp:.2f} km")
    return {
        "species":     species_code,
        "name":        species_name,
        "n":           len(df_sp),
        "mean_disp":   mean_disp,
        "geo_score":   geo_sc,
        "res_score":   res_sc,
        "improvement": imp,
    }


# ── FORCE MAGNITUDE CORRELATION ───────────────────────────────

def displacement_magnitude_correlation(df):
    valid = df[
        df["displacement_deg"].notna() &
        df["am_weight_scaled"].notna() &
        df["geo_magnitude_nT"].notna() &
        (df["geo_magnitude_nT"] > 0)
    ].copy()
    valid["force_ratio"] = (valid["am_weight_scaled"]
                            / valid["geo_magnitude_nT"])
    from scipy.stats import spearmanr
    r, p = spearmanr(valid["force_ratio"],
                     valid["displacement_deg"])
    return float(r), float(p), len(valid)


# ── WRITE REPORT ──────────────────────────────────────────────

def write_report(multi_res, null_results, force_r, force_p,
                 force_n, species_results, risk_map, run_date):

    lines = []
    w = lines.append

    def sig(p):
        if p is None: return "—"
        return "SIGNIFICANT" if float(p) < ALPHA else "NULL"

    w("# STRANDING DISPLACEMENT ANALYSIS v2")
    w("## Force Model Test — Corrected Projection")
    w("## OC-OBS-002 — OrganismCore — Eric Robert Lawson")
    w(f"## Run date: {run_date}")
    w("")
    w("---")
    w("")
    w("## CORRECTIONS FROM v1")
    w("")
    w("```")
    w("1. Projection direction: BACKWARD (corrected)")
    w("   v1: forward from stranding along resultant bearing")
    w("   v2: backward from stranding along RECIPROCAL")
    w("       of resultant bearing → offshore origin corridor")
    w("")
    w("2. Fit metric: origin corridor clustering (corrected)")
    w("   v1: segment of projected landfall vs actual segment")
    w("   v2: within-segment clustering of offshore origin")
    w("       points — tighter = better prediction")
    w("")
    w("3. Resolution: multi-resolution (corrected)")
    w("   v1: 0.45° (~50 km) only")
    w("   v2: 0.10° (~11 km) primary, 0.20°, 0.45° sensitivity")
    w("```")
    w("")
    w("---")
    w("")
    w("## MULTI-RESOLUTION FIT IMPROVEMENT")
    w("")
    w("```")
    w(f"{'Resolution':<12} {'Seg size':>10} {'Geo score':>12} "
      f"{'Res score':>12} {'Improvement':>13}")
    w("─" * 65)
    for name, res in multi_res.items():
        imp = res["improvement"]
        gs  = res["geo_score"]
        rs  = res["res_score"]
        marker = " ← PRIMARY" if name == PRIMARY_RES else ""
        w(f"  {name:<10} {res['size_deg']:>10.2f}° "
          f"{gs:>11.2f}km {rs:>11.2f}km "
          f"{imp:>12.2f}km{marker}")
    w("```")
    w("")
    w("---")
    w("")
    w("## GEOGRAPHIC NULL MODEL")
    w(f"## Resolution: {PRIMARY_RES} (~11 km segments)")
    w("")
    w("```")
    if null_results[0] is not None:
        null_imps, real_imp, p_val, geo_sc, res_sc = null_results
        w(f"Permutations:         {N_PERMUTATIONS}")
        w(f"Geo score:            {geo_sc:.2f} km")
        w(f"Resultant score:      {res_sc:.2f} km")
        w(f"Real improvement:     {real_imp:.2f} km")
        w(f"Null mean:            {null_imps.mean():.2f} km")
        w(f"Null SD:              {null_imps.std():.2f} km")
        w(f"Null 95th pctile:     {np.percentile(null_imps,95):.2f} km")
        w(f"p (real >= null):     {p_val:.4f}")
        w(f"Result:               {sig(p_val)}")
        w("")
        if p_val < ALPHA:
            w("Resultant origin clustering exceeds null.")
            w("Geographic reporting density does not explain")
            w("the improvement. Force model supported.")
        else:
            w("Resultant origin clustering does not exceed null.")
            w("Geographic reporting density may explain result.")
    else:
        w("Null model: not run")
    w("```")
    w("")
    w("---")
    w("")
    w("## FORCE MAGNITUDE CORRELATION")
    w("")
    w("```")
    w(f"Spearman r:   {force_r:.4f}")
    w(f"p:            {force_p:.6f}")
    w(f"N:            {force_n:,}")
    w(f"Result:       {sig(force_p)}")
    w(f"Direction:    {'Predicted (positive)' if force_r > 0 else 'Opposite'}")
    w("```")
    w("")
    w("---")
    w("")
    w("## SPECIES CONTROL")
    w("")
    w("```")
    w(f"{'Species':<12} {'N':>8} {'Mean disp°':>12} "
      f"{'Geo score':>11} {'Res score':>11} {'Improv (km)':>12}")
    w("─" * 72)
    for res in species_results:
        if res is not None:
            w(f"  {res['species']:<10} {res['n']:>8,} "
              f"{res['mean_disp']:>11.2f}° "
              f"{res['geo_score']:>10.2f}km "
              f"{res['res_score']:>10.2f}km "
              f"{res['improvement']:>11.2f}km")
    w("```")
    w("")
    w("---")
    w("")
    w("## 2026 MIGRATION SEASON RISK MAP")
    w(f"## Top {len(risk_map)} coastal segments by risk score")
    w("## Migration window: April–June, August–November")
    w("")
    w("```")
    w(f"{'Rank':<5} {'Lat':>7} {'Lon':>8} {'N mig':>7} "
      f"{'Disp°':>7} {'Opp°':>7} "
      f"{'Approach':>10} {'Risk':>8}")
    w("─" * 65)
    for i, row in risk_map.iterrows():
        w(f"  {i+1:<3} "
          f"{row['seg_lat']:>7.2f} "
          f"{row['seg_lon']:>8.2f} "
          f"{int(row['n_migration']):>7} "
          f"{row['mean_disp_deg']:>6.1f}° "
          f"{row['mean_opp_deg']:>6.1f}° "
          f"{row['approach_corridor_bearing']:>8.1f}° "
          f"{row['risk_score']:>8.1f}")
    w("")
    w("Approach bearing = direction FROM which turtles are")
    w("predicted to arrive at each segment.")
    w("Deploy boat/drone coverage along this bearing")
    w("offshore of each high-risk segment.")
    w("```")
    w("")
    w("---")
    w("")
    w("## VERSION")
    w("```")
    w("Script:    stranding_displacement_analysis_v2.py")
    w(f"Run date:  {run_date}")
    w("Input:     stssn_with_resultant.csv")
    w("Status:    Exploratory — amendment filed 2026-03-23")
    w("```")

    return "\n".join(lines)


# ── MAIN ──────────────────────────────────────────────────────

def main():
    run_date = datetime.now().strftime("%Y-%m-%d %H:%M")

    print("=" * 60)
    print("STRANDING DISPLACEMENT ANALYSIS v2")
    print("Corrected backward projection + multi-resolution")
    print("OC-OBS-002 — OrganismCore")
    print("=" * 60)

    if not os.path.exists(RESULTANT_CSV):
        print(f"\nERROR: {RESULTANT_CSV} not found.")
        sys.exit(1)

    print(f"\nLoading: {RESULTANT_CSV}")
    df = pd.read_csv(RESULTANT_CSV)
    print(f"  Rows: {len(df):,}")

    # Recover k
    valid_k = df[
        df["am_weight_scaled"].notna() &
        df["am_total_weight"].notna() &
        (df["am_total_weight"] > 0)
    ]
    k = float((valid_k["am_weight_scaled"]
               / valid_k["am_total_weight"]).median()) \
        if len(valid_k) > 0 else 1.0
    print(f"  Recovered k: {k:.6e}")

    # Force magnitude correlation (unchanged from v1)
    print("\nForce magnitude correlation...")
    force_r, force_p, force_n = displacement_magnitude_correlation(df)
    print(f"  r={force_r:.4f}  p={force_p:.6f}  N={force_n:,}")

    # Multi-resolution fit improvement
    print("\nMulti-resolution fit improvement...")
    multi_res = run_multi_resolution(df)

    # Null model at primary resolution
    print(f"\nNull model at {PRIMARY_RES} resolution "
          f"({N_PERMUTATIONS} permutations)...")
    seg_size_primary = SEGMENT_SIZES[PRIMARY_RES]
    null_results = run_null_model(df, seg_size_primary,
                                  n_perms=N_PERMUTATIONS)

    # Species control
    print("\nSpecies control...")
    species_results = []
    ama = AMFalseAttractor(AM_CSV)

    # Loggerhead from existing resultant data
    imp_cc, geo_cc, res_cc = fit_improvement(df, seg_size_primary)
    species_results.append({
        "species":     "CC",
        "name":        "Loggerhead",
        "n":           len(df),
        "mean_disp":   float(df["displacement_deg"].dropna().mean()),
        "geo_score":   geo_cc,
        "res_score":   res_cc,
        "improvement": imp_cc,
    })

    if os.path.exists(RAW_DATA_FILE):
        for code, name in [("CM", "Green turtle"),
                           ("DC", "Leatherback")]:
            res = run_species_control(
                RAW_DATA_FILE, ama, k, code, name,
                seg_size_primary
            )
            if res:
                species_results.append(res)
    else:
        print(f"  {RAW_DATA_FILE} not found — skipping CM/DC")

    # Risk map
    print("\nBuilding 2026 migration season risk map...")
    risk_map = build_risk_map(df, seg_size_primary, top_n=20)
    print(f"  Top segment: lat={risk_map.iloc[0]['seg_lat']:.2f}  "
          f"lon={risk_map.iloc[0]['seg_lon']:.2f}  "
          f"risk={risk_map.iloc[0]['risk_score']:.1f}")

    # Save risk map CSV
    risk_map.to_csv("risk_map_2026.csv", index=False)
    print("  Risk map saved: risk_map_2026.csv")

    # Write report
    report = write_report(
        multi_res, null_results, force_r, force_p, force_n,
        species_results, risk_map, run_date
    )
    with open(RESULTS_MD, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\nResults written: {RESULTS_MD}")

    print("\n" + "=" * 60)
    print("COMPLETE")
    print("=" * 60)
    print(f"  Results:  {RESULTS_MD}")
    print(f"  Risk map: risk_map_2026.csv")
    print()
    print("  Report all results regardless of direction.")


if __name__ == "__main__":
    main()
