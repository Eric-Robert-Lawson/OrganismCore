"""
AM FALSE ATTRACTOR COMPUTATION
===============================
OC-OBS-002 — Sea Turtle Stranding Analysis
OrganismCore — Eric Robert Lawson
March 2026

PURPOSE:
    For any geographic coordinate (lat, lon), compute:
      - The power-weighted AM false attractor bearing
      - The geomagnetic reference bearing (toward nearest
        major FL nesting beach cluster, or geomagnetic
        north if phase unknown)
      - The opposition angle between them

    This module is called by turtle_stranding_pipeline.py.
    It can also be run standalone for spot checks.

METHOD:
    Exactly as specified in pre_registration_analysis.md
    Part III: AM False Attractor Computation Method.

    1. Load all AM transmitters within 500 km radius.
    2. Compute bearing from stranding location to each
       transmitter (geodesic bearing, 0–360°).
    3. Compute weight = erp_kw / distance_km².
    4. Compute power-weighted circular mean bearing.
    5. Compute geomagnetic reference bearing.
    6. Compute opposition angle |FA – geo|, normalised
       to 0–180°.

    500 km radius: as specified in pre-registration.
    Beyond 500 km, AM ground wave propagation is
    negligible for navigation disruption.

FIELD REMAPPING (Amendment 2, 2026-03-22):
    All column names use the actual NOAA STSSN field names,
    not the pre-registration placeholder names.

INPUTS:
    am_stations_clean.csv  (built by build_am_station_table.py)
    lat, lon               (stranding coordinate, WGS84)

OUTPUTS:
    dict with keys:
      fa_bearing      — false attractor bearing (0–360°)
      geo_bearing     — geomagnetic reference bearing (0–360°)
      opposition_deg  — |fa_bearing - geo_bearing| → 0–180°
      n_stations      — stations within 500 km
      total_weight    — sum of erp/distance² weights
      fa_strength     — weight in dominant bin / total weight

REQUIRES:
    pip install pandas numpy scipy
"""

import math
import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter1d

# ── CONSTANTS ─────────────────────────────────────────────────

RADIUS_KM      = 500      # AM ground-wave influence radius (pre-reg)
EARTH_RADIUS_KM = 6371.0
SMOOTHING_SIGMA = 10.0    # Gaussian smoothing on azimuth bins (degrees)
N_BINS          = 360     # one bin per degree

# Major Florida Atlantic nesting beach cluster centroids.
# Used as geomagnetic navigation targets for turtles in
# natal beach return phase when navigation phase is unknown.
# Source: Spotila et al., FWC beach segment data.
# Pre-specified proxy: bearing toward nearest cluster.
FL_NESTING_CLUSTERS = [
    (28.06, -80.56),   # Melbourne / Brevard County
    (27.18, -80.21),   # Hobe Sound / Martin County
    (26.50, -80.07),   # Palm Beach County
    (25.83, -80.12),   # Miami-Dade
    (25.08, -80.45),   # Florida Keys / Monroe
    (29.08, -81.04),   # Volusia County
]


# ── HAVERSINE DISTANCE ─────────────────────────────────────────

def haversine_km(lat1, lon1, lat2_arr, lon2_arr):
    """
    Vectorised haversine distance from one point to
    an array of points. Returns distances in km.
    """
    lat1_r  = math.radians(lat1)
    lon1_r  = math.radians(lon1)
    lat2_r  = np.radians(lat2_arr)
    lon2_r  = np.radians(lon2_arr)

    dlat = lat2_r - lat1_r
    dlon = lon2_r - lon1_r

    a = (np.sin(dlat / 2.0) ** 2
         + math.cos(lat1_r) * np.cos(lat2_r)
         * np.sin(dlon / 2.0) ** 2)
    c = 2.0 * np.arcsin(np.sqrt(np.clip(a, 0, 1)))
    return EARTH_RADIUS_KM * c


# ── GEODESIC BEARING ──────────────────────────────────────────

def bearing_deg(lat1, lon1, lat2_arr, lon2_arr):
    """
    Vectorised initial bearing from (lat1, lon1) to each
    point in lat2_arr/lon2_arr. Returns degrees 0–360.
    """
    lat1_r  = math.radians(lat1)
    lon1_r  = math.radians(lon1)
    lat2_r  = np.radians(lat2_arr)
    lon2_r  = np.radians(lon2_arr)

    dlon = lon2_r - lon1_r

    x = np.sin(dlon) * np.cos(lat2_r)
    y = (math.cos(lat1_r) * np.sin(lat2_r)
         - math.sin(lat1_r) * np.cos(lat2_r) * np.cos(dlon))

    bearing = np.degrees(np.arctan2(x, y))
    return (bearing + 360.0) % 360.0


# ── CIRCULAR MEAN ─────────────────────────────────────────────

def weighted_circular_mean(bearings_deg, weights):
    """
    Power-weighted circular mean of an array of bearings.
    Returns mean bearing in degrees 0–360.
    """
    if len(bearings_deg) == 0 or weights.sum() == 0:
        return None
    rad = np.radians(bearings_deg)
    sin_sum = np.sum(weights * np.sin(rad))
    cos_sum = np.sum(weights * np.cos(rad))
    mean_rad = math.atan2(sin_sum, cos_sum)
    return (math.degrees(mean_rad) + 360.0) % 360.0


# ── OPPOSITION ANGLE ──────────────────────────────────────────

def opposition_angle(fa_bearing, geo_bearing):
    """
    Angle between fa_bearing and geo_bearing, normalised
    to 0–180°.

    0°   = FA and geo bearings identical (no opposition)
    90°  = perpendicular (random)
    180° = directly opposed (maximum disruption)
    """
    if fa_bearing is None or geo_bearing is None:
        return None
    diff = abs(fa_bearing - geo_bearing) % 360.0
    if diff > 180.0:
        diff = 360.0 - diff
    return diff


# ── NEAREST NESTING CLUSTER BEARING ───────────────────────────

def nearest_nesting_cluster_bearing(lat, lon):
    """
    Bearing from (lat, lon) to the nearest FL nesting
    beach cluster. Used as geomagnetic reference bearing
    when navigation phase is unknown.

    Pre-specified in pre_registration_analysis.md Part III:
    'For return-to-natal-beach navigation: bearing toward
    the nearest major Florida nesting beach cluster.'
    """
    cluster_lats = np.array([c[0] for c in FL_NESTING_CLUSTERS])
    cluster_lons = np.array([c[1] for c in FL_NESTING_CLUSTERS])
    dists = haversine_km(lat, lon, cluster_lats, cluster_lons)
    nearest_idx = int(np.argmin(dists))
    return bearing_deg(
        lat, lon,
        np.array([cluster_lats[nearest_idx]]),
        np.array([cluster_lons[nearest_idx]])
    )[0]


# ── CORE COMPUTATION CLASS ─────────────────────────────────────

class AMFalseAttractor:
    """
    Load once, call compute() for each stranding coordinate.

    Usage:
        ama = AMFalseAttractor("am_stations_clean.csv")
        result = ama.compute(lat=28.5, lon=-80.6)
        print(result['opposition_deg'])
    """

    def __init__(self, am_csv_path="am_stations_clean.csv"):
        print(f"Loading AM station table: {am_csv_path}")
        self.stations = pd.read_csv(am_csv_path)

        # Validate required columns
        required = ["lat", "lon", "erp_kw", "frequency_khz"]
        missing = [c for c in required
                   if c not in self.stations.columns]
        if missing:
            raise ValueError(
                f"am_stations_clean.csv missing columns: {missing}\n"
                f"Available: {list(self.stations.columns)}"
            )

        # Drop rows with missing coordinates
        before = len(self.stations)
        self.stations = self.stations.dropna(
            subset=["lat", "lon", "erp_kw"]
        ).reset_index(drop=True)
        dropped = before - len(self.stations)
        if dropped:
            print(f"  Dropped {dropped:,} rows with null "
                  f"lat/lon/erp — {len(self.stations):,} remain")

        # Pre-extract arrays for vectorised ops
        self._lats   = self.stations["lat"].values
        self._lons   = self.stations["lon"].values
        self._erp    = self.stations["erp_kw"].values

        print(f"  AM stations loaded:  {len(self.stations):,}")
        print(f"  Influence radius:    {RADIUS_KM} km")
        print(f"  Frequency range:     "
              f"{self.stations['frequency_khz'].min():.0f}–"
              f"{self.stations['frequency_khz'].max():.0f} kHz")

    def compute(self, lat, lon,
                geo_bearing=None,
                radius_km=RADIUS_KM):
        """
        Compute AM false attractor result for one location.

        Parameters
        ----------
        lat, lon : float
            Stranding coordinate (WGS84).
        geo_bearing : float or None
            Pre-computed geomagnetic reference bearing (0–360°).
            If None, uses nearest FL nesting cluster bearing.
        radius_km : float
            Transmitter inclusion radius (default 500 km).

        Returns
        -------
        dict with keys:
            fa_bearing      (float or None)
            geo_bearing     (float)
            opposition_deg  (float or None)
            n_stations      (int)
            total_weight    (float)
            fa_strength     (float or None)
        """
        # Distance to all stations
        dists = haversine_km(lat, lon, self._lats, self._lons)
        mask  = dists <= radius_km

        n_stations = int(mask.sum())

        if n_stations == 0:
            return {
                "fa_bearing":     None,
                "geo_bearing":    geo_bearing,
                "opposition_deg": None,
                "n_stations":     0,
                "total_weight":   0.0,
                "fa_strength":    None,
            }

        in_radius_lats = self._lats[mask]
        in_radius_lons = self._lons[mask]
        in_radius_erp  = self._erp[mask]
        in_radius_dist = dists[mask]

        # Bearings from stranding location to each transmitter
        bearings = bearing_deg(
            lat, lon, in_radius_lats, in_radius_lons
        )

        # Weight = ERP / distance² (inverse square, pre-reg spec)
        # Guard against zero distance (transmitter at same coord)
        safe_dist  = np.maximum(in_radius_dist, 0.1)
        weights    = in_radius_erp / (safe_dist ** 2)
        total_wt   = float(weights.sum())

        # Power-weighted circular mean → false attractor bearing
        fa_bearing = weighted_circular_mean(bearings, weights)

        # Azimuth distribution (360 bins) with Gaussian smoothing
        # Used for fa_strength computation
        az_dist = np.zeros(N_BINS)
        bin_idx = np.round(bearings).astype(int) % N_BINS
        np.add.at(az_dist, bin_idx, weights)

        # Circular Gaussian smoothing
        az_tripled = np.concatenate([az_dist, az_dist, az_dist])
        smoothed   = gaussian_filter1d(az_tripled, sigma=SMOOTHING_SIGMA)
        az_smooth  = smoothed[N_BINS:2 * N_BINS]

        peak_bin   = int(np.argmax(az_smooth))
        fa_strength = (float(az_smooth[peak_bin])
                       / az_smooth.sum()
                       if az_smooth.sum() > 0 else None)

        # Geomagnetic reference bearing
        if geo_bearing is None:
            geo_bearing = nearest_nesting_cluster_bearing(lat, lon)

        # Opposition angle
        opp = opposition_angle(fa_bearing, geo_bearing)

        return {
            "fa_bearing":     fa_bearing,
            "geo_bearing":    geo_bearing,
            "opposition_deg": opp,
            "n_stations":     n_stations,
            "total_weight":   total_wt,
            "fa_strength":    fa_strength,
        }

    def compute_batch(self, df,
                      lat_col="Latitude",
                      lon_col="Longitude",
                      geo_bearing_col=None,
                      radius_km=RADIUS_KM,
                      progress_every=1000):
        """
        Compute AM false attractor for every row in a DataFrame.

        Adds columns:
            am_fa_bearing      — false attractor bearing (0–360°)
            am_geo_bearing     — geomagnetic reference bearing
            am_opposition_deg  — opposition angle (0–180°)
            am_n_stations      — transmitters within radius
            am_total_weight    — sum of erp/dist² weights
            am_fa_strength     — peak bin fraction (0–1)

        Parameters
        ----------
        df : pd.DataFrame
            Must contain lat_col and lon_col columns.
            Field names are the actual NOAA STSSN names
            (Amendment 2 remapping).
        lat_col : str   — default 'Latitude'  (NOAA actual name)
        lon_col : str   — default 'Longitude' (NOAA actual name)
        geo_bearing_col : str or None
            Column with pre-computed geo bearings, if available.
        radius_km : float
            Transmitter inclusion radius.
        progress_every : int
            Print progress every N rows.

        Returns
        -------
        pd.DataFrame — copy of df with six new columns appended.
        """
        out = df.copy()
        results = []
        n = len(df)

        for i, row in df.iterrows():
            lat = row[lat_col]
            lon = row[lon_col]

            # Skip rows with missing coordinates
            if pd.isna(lat) or pd.isna(lon):
                results.append({
                    "am_fa_bearing":     None,
                    "am_geo_bearing":    None,
                    "am_opposition_deg": None,
                    "am_n_stations":     0,
                    "am_total_weight":   0.0,
                    "am_fa_strength":    None,
                })
                continue

            geo_bearing = None
            if geo_bearing_col and geo_bearing_col in df.columns:
                geo_bearing = row.get(geo_bearing_col)

            res = self.compute(
                lat=float(lat),
                lon=float(lon),
                geo_bearing=geo_bearing,
                radius_km=radius_km,
            )
            results.append({
                "am_fa_bearing":     res["fa_bearing"],
                "am_geo_bearing":    res["geo_bearing"],
                "am_opposition_deg": res["opposition_deg"],
                "am_n_stations":     res["n_stations"],
                "am_total_weight":   res["total_weight"],
                "am_fa_strength":    res["fa_strength"],
            })

            if progress_every and (i + 1) % progress_every == 0:
                print(f"  {i + 1:,} / {n:,}")

        result_df = pd.DataFrame(results, index=df.index)
        for col in result_df.columns:
            out[col] = result_df[col]

        return out


# ── STANDALONE SPOT CHECK ─────────────────────────────────────

if __name__ == "__main__":
    """
    Quick verification against known locations.
    Does not use any stranding data.
    Safe to run before opening STSSN file.
    """
    print("=" * 60)
    print("AM FALSE ATTRACTOR — SPOT CHECK")
    print("OC-OBS-002 — OrganismCore")
    print("=" * 60)
    print()

    ama = AMFalseAttractor("am_stations_clean.csv")
    print()

    test_locs = [
        (28.50, -80.56, "Cape Canaveral FL"),
        (27.18, -80.21, "Hobe Sound FL"),
        (29.08, -81.04, "Daytona Beach FL"),
        (25.77, -80.19, "Miami FL"),
        (30.33, -81.66, "Jacksonville FL"),
        (27.96, -97.06, "Corpus Christi TX"),
        (29.95, -90.07, "New Orleans LA"),
        (35.23, -75.59, "Cape Hatteras NC"),
    ]

    print(f"\n{'Location':<28} {'FA Bear':>8} {'Geo Bear':>9} "
          f"{'Opp°':>7} {'N stn':>6} {'Strength':>9}")
    print("─" * 75)

    for lat, lon, name in test_locs:
        r = ama.compute(lat, lon)
        fa   = f"{r['fa_bearing']:.1f}°"    if r['fa_bearing']     is not None else "None"
        opp  = f"{r['opposition_deg']:.1f}°" if r['opposition_deg'] is not None else "None"
        geo  = f"{r['geo_bearing']:.1f}°"   if r['geo_bearing']    is not None else "None"
        str_ = f"{r['fa_strength']:.4f}"    if r['fa_strength']    is not None else "None"
        print(f"  {name:<26} {fa:>8} {geo:>9} {opp:>7} "
              f"{r['n_stations']:>6,} {str_:>9}")

    print()
    print("Spot check complete.")
    print("If output looks reasonable, proceed to "
          "turtle_stranding_pipeline.py")
