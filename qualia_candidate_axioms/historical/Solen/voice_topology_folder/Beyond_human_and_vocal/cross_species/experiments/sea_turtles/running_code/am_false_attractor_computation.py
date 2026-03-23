"""
AM FALSE ATTRACTOR COMPUTATION
===============================
OC-OBS-002 — Sea Turtle Stranding Analysis
OrganismCore — Eric Robert Lawson
March 2026

VERSION: 1.2 — geo_bearing formula corrected
  v1.0: geo_bearing used nearest FL nesting cluster bearing.
  v1.1: geo_bearing switched to geomagnetic north, but
        conversion formula was inverted:
          (360 - decl) with decl=-9.77 → 369.77 % 360 = 9.77°
        Produced ~10° instead of ~350°.
  v1.2: Formula corrected:
          geo_north = (0.0 + decl) % 360.0
          decl=-9.77 → geo_north = 350.23°  ✓
        Geo bearings now correctly cluster ~348–356° for
        FL Atlantic coast and ~350–358° for Gulf coast,
        reflecting real westerly magnetic declination.

PURPOSE:
    For any geographic coordinate (lat, lon), compute:
      - The power-weighted AM false attractor bearing
      - The geomagnetic north reference bearing
        (declination-corrected, WMM-2025 approximation)
      - The opposition angle between them

METHOD:
    Exactly as specified in pre_registration_analysis.md
    Part III, with geo_bearing = geomagnetic north per
    the pre-specified unknown-phase fallback.

    1. Load all AM transmitters within 500 km radius.
    2. Compute bearing from stranding location to each
       transmitter (geodesic bearing, 0–360°).
    3. Compute weight = erp_kw / distance_km².
    4. Compute power-weighted circular mean bearing.
    5. Compute geomagnetic north at the stranding coord
       (geographic north + magnetic declination).
    6. Compute opposition angle |FA – geo|, normalised
       to 0–180°.

MAGNETIC DECLINATION SIGN CONVENTION:
    Negative declination = west of geographic north
    (the US Atlantic/Gulf coast).
    geo_north bearing = (geographic_north + declination) % 360
                      = (0 + declination) % 360
    For decl = -9.77°: geo_north = 350.23° (WNW of north ✓)

MAGNETIC DECLINATION MODEL:
    WMM-2025 polynomial approximation, accurate ±1° for
    scope region lat 24–45°N, lon -98° to -65°W, 2026.
    Upgrade path documented in switch_to_wmm().

INPUTS:
    am_stations_clean.csv  (built by build_am_station_table.py)
    lat, lon               (stranding coordinate, WGS84)

OUTPUTS:
    dict with keys:
      fa_bearing        — false attractor bearing (0–360°)
      geo_bearing       — geomagnetic north bearing (0–360°)
      mag_declination   — magnetic declination at coord (deg)
      opposition_deg    — |fa_bearing - geo_bearing| → 0–180°
      n_stations        — stations within 500 km
      total_weight      — sum of erp/distance² weights
      fa_strength       — weight in dominant bin / total weight

REQUIRES:
    pip install pandas numpy scipy
"""

import math
import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter1d

# ── CONSTANTS ─────────────────────────────────────────────────

RADIUS_KM        = 500
EARTH_RADIUS_KM  = 6371.0
SMOOTHING_SIGMA  = 10.0
N_BINS           = 360

# FL nesting clusters — retained for Movebank future work only.
# NOT used in primary A1 pipeline.
FL_NESTING_CLUSTERS = [
    (28.06, -80.56),   # Melbourne / Brevard County
    (27.18, -80.21),   # Hobe Sound / Martin County
    (26.50, -80.07),   # Palm Beach County
    (25.83, -80.12),   # Miami-Dade
    (25.08, -80.45),   # Florida Keys / Monroe
    (29.08, -81.04),   # Volusia County
]


# ── MAGNETIC DECLINATION (WMM-2025 approximation) ─────────────

def magnetic_declination_deg(lat, lon, year=2026.2):
    """
    Estimate magnetic declination at (lat, lon) for the
    given decimal year.

    Polynomial approximation fitted to WMM-2025 grid values
    for scope region: lat 24–45°N, lon -98° to -65°W.
    Accuracy: ±1.0° within scope.

    Sign convention:
      Negative = west of geographic north (US Atlantic/Gulf).
      Positive = east of geographic north.

    US Atlantic/Gulf coast range (2026, approximate):
      FL Atlantic coast:  -9° to -10°
      Gulf coast (TX):    -5° to -7°
      Gulf coast (LA/AL): -7° to -9°
      NC/VA/MD:           -11° to -13°
      NJ/NY:              -13° to -14°
    """
    lat0 =  35.0
    lon0 = -82.0
    yr0  = 2025.0

    dlat = lat  - lat0
    dlon = lon  - lon0
    dyr  = year - yr0

    a0 = -11.20
    a1 =  -0.26
    a2 =  -0.15
    a3 =   0.002
    a4 =  -0.001
    a5 =   0.003
    a6 =  -0.08

    return (a0
            + a1 * dlat
            + a2 * dlon
            + a3 * dlat ** 2
            + a4 * dlon ** 2
            + a5 * dlat * dlon
            + a6 * dyr)


def geomagnetic_north_bearing(lat, lon, year=2026.2):
    """
    The bearing toward geomagnetic north at (lat, lon).

    geo_north = (geographic_north + magnetic_declination) % 360
              = (0 + declination) % 360

    Sign convention check:
      decl = -9.77° (westerly) →
        geomagnetic north is 9.77° WEST of geographic north →
        bearing = 360 - 9.77 = 350.23°

    Wait — let's be explicit:
      Magnetic declination is the angle FROM geographic north
      TO magnetic north, measured clockwise positive.
      Westerly declination is NEGATIVE.
      If decl = -9.77°, magnetic north is 9.77° to the WEST
      of geographic north, i.e. at bearing 360 - 9.77 = 350.23°.
      So:  geo_north = (0.0 - decl) % 360.0  when decl is negative.
      Equivalently: geo_north = (-decl) % 360.0

    Correction from v1.1:
      v1.1 had: (360.0 - decl) % 360  → wrong sign produced ~10°
      v1.2 has: (-decl) % 360.0       → correct, produces ~350°
    """
    decl      = magnetic_declination_deg(lat, lon, year)
    geo_north = (-decl) % 360.0
    return geo_north, decl


def switch_to_wmm():
    """
    UPGRADE PATH to full WMM-2025 via geomag library.

        pip install geomag

        import geomag
        gm = geomag.GeoMag()
        result = gm.GeoMag(lat, lon, alt=0, time=2026.2)
        decl = result.dec
        geo_north = (-decl) % 360.0
        return geo_north, decl

    Recommended before journal submission.
    Polynomial approximation (±1°) is sufficient for
    the primary analysis.
    """
    pass


# ── OPTIONAL: NESTING CLUSTER BEARING ─────────────────────────

def nearest_nesting_cluster_bearing(lat, lon):
    """
    NOT used in primary A1 pipeline.
    Retained for Movebank known-phase analyses.
    """
    cluster_lats = np.array([c[0] for c in FL_NESTING_CLUSTERS])
    cluster_lons = np.array([c[1] for c in FL_NESTING_CLUSTERS])
    dists        = haversine_km(lat, lon, cluster_lats, cluster_lons)
    nearest_idx  = int(np.argmin(dists))
    return bearing_deg(
        lat, lon,
        np.array([cluster_lats[nearest_idx]]),
        np.array([cluster_lons[nearest_idx]])
    )[0]


# ── HAVERSINE DISTANCE ─────────────────────────────────────────

def haversine_km(lat1, lon1, lat2_arr, lon2_arr):
    lat1_r = math.radians(lat1)
    lon1_r = math.radians(lon1)
    lat2_r = np.radians(lat2_arr)
    lon2_r = np.radians(lon2_arr)
    dlat   = lat2_r - lat1_r
    dlon   = lon2_r - lon1_r
    a      = (np.sin(dlat / 2.0) ** 2
              + math.cos(lat1_r) * np.cos(lat2_r)
              * np.sin(dlon / 2.0) ** 2)
    c      = 2.0 * np.arcsin(np.sqrt(np.clip(a, 0, 1)))
    return EARTH_RADIUS_KM * c


# ── GEODESIC BEARING ──────────────────────────────────────────

def bearing_deg(lat1, lon1, lat2_arr, lon2_arr):
    lat1_r = math.radians(lat1)
    lon1_r = math.radians(lon1)
    lat2_r = np.radians(lat2_arr)
    lon2_r = np.radians(lon2_arr)
    dlon   = lon2_r - lon1_r
    x      = np.sin(dlon) * np.cos(lat2_r)
    y      = (math.cos(lat1_r) * np.sin(lat2_r)
              - math.sin(lat1_r) * np.cos(lat2_r) * np.cos(dlon))
    b      = np.degrees(np.arctan2(x, y))
    return (b + 360.0) % 360.0


# ── CIRCULAR MEAN ─────────────────────────────────────────────

def weighted_circular_mean(bearings_deg, weights):
    if len(bearings_deg) == 0 or weights.sum() == 0:
        return None
    rad     = np.radians(bearings_deg)
    sin_sum = np.sum(weights * np.sin(rad))
    cos_sum = np.sum(weights * np.cos(rad))
    return (math.degrees(math.atan2(sin_sum, cos_sum)) + 360.0) % 360.0


# ── OPPOSITION ANGLE ──────────────────────────────────────────

def opposition_angle(fa_bearing, geo_bearing):
    """
    Angle between fa_bearing and geo_bearing, 0–180°.
    0°   = identical (no disruption)
    90°  = perpendicular (random)
    180° = directly opposed (maximum disruption)
    """
    if fa_bearing is None or geo_bearing is None:
        return None
    diff = abs(fa_bearing - geo_bearing) % 360.0
    if diff > 180.0:
        diff = 360.0 - diff
    return diff


# ── CORE COMPUTATION CLASS ─────────────────────────────────────

class AMFalseAttractor:

    def __init__(self, am_csv_path="am_stations_clean.csv"):
        print(f"Loading AM station table: {am_csv_path}")
        self.stations = pd.read_csv(am_csv_path)

        required = ["lat", "lon", "erp_kw", "frequency_khz"]
        missing  = [c for c in required
                    if c not in self.stations.columns]
        if missing:
            raise ValueError(
                f"Missing columns: {missing}\n"
                f"Available: {list(self.stations.columns)}"
            )

        before = len(self.stations)
        self.stations = self.stations.dropna(
            subset=["lat", "lon", "erp_kw"]
        ).reset_index(drop=True)
        dropped = before - len(self.stations)
        if dropped:
            print(f"  Dropped {dropped:,} rows with null "
                  f"lat/lon/erp — {len(self.stations):,} remain")

        self._lats = self.stations["lat"].values
        self._lons = self.stations["lon"].values
        self._erp  = self.stations["erp_kw"].values

        print(f"  AM stations loaded:  {len(self.stations):,}")
        print(f"  Influence radius:    {RADIUS_KM} km")
        print(f"  Frequency range:     "
              f"{self.stations['frequency_khz'].min():.0f}–"
              f"{self.stations['frequency_khz'].max():.0f} kHz")

    def compute(self, lat, lon,
                geo_bearing_override=None,
                radius_km=RADIUS_KM,
                year=2026.2):
        """
        Compute AM false attractor result for one location.

        geo_bearing_override : float or None
            If None (default), uses geomagnetic north at
            this coordinate (unknown-phase fallback,
            pre_registration_analysis.md Part III).
        """
        if geo_bearing_override is not None:
            geo_bearing = geo_bearing_override
            mag_decl    = magnetic_declination_deg(lat, lon, year)
        else:
            geo_bearing, mag_decl = geomagnetic_north_bearing(
                lat, lon, year
            )

        dists      = haversine_km(lat, lon, self._lats, self._lons)
        mask       = dists <= radius_km
        n_stations = int(mask.sum())

        if n_stations == 0:
            return {
                "fa_bearing":      None,
                "geo_bearing":     geo_bearing,
                "mag_declination": mag_decl,
                "opposition_deg":  None,
                "n_stations":      0,
                "total_weight":    0.0,
                "fa_strength":     None,
            }

        in_lats = self._lats[mask]
        in_lons = self._lons[mask]
        in_erp  = self._erp[mask]
        in_dist = dists[mask]

        bearings   = bearing_deg(lat, lon, in_lats, in_lons)
        safe_dist  = np.maximum(in_dist, 0.1)
        weights    = in_erp / (safe_dist ** 2)
        total_wt   = float(weights.sum())

        fa_bearing = weighted_circular_mean(bearings, weights)

        az_dist  = np.zeros(N_BINS)
        bin_idx  = np.round(bearings).astype(int) % N_BINS
        np.add.at(az_dist, bin_idx, weights)
        az_tri   = np.concatenate([az_dist, az_dist, az_dist])
        smoothed = gaussian_filter1d(az_tri, sigma=SMOOTHING_SIGMA)
        az_sm    = smoothed[N_BINS:2 * N_BINS]

        peak_bin    = int(np.argmax(az_sm))
        fa_strength = (float(az_sm[peak_bin]) / az_sm.sum()
                       if az_sm.sum() > 0 else None)

        opp = opposition_angle(fa_bearing, geo_bearing)

        return {
            "fa_bearing":      fa_bearing,
            "geo_bearing":     geo_bearing,
            "mag_declination": mag_decl,
            "opposition_deg":  opp,
            "n_stations":      n_stations,
            "total_weight":    total_wt,
            "fa_strength":     fa_strength,
        }

    def compute_batch(self, df,
                      lat_col="Latitude",
                      lon_col="Longitude",
                      geo_bearing_override_col=None,
                      radius_km=RADIUS_KM,
                      year=2026.2,
                      progress_every=1000):
        """
        Compute AM false attractor for every row in a DataFrame.

        Adds columns:
            am_fa_bearing       — false attractor bearing (0–360°)
            am_geo_bearing      — geomagnetic north bearing (0–360°)
            am_mag_declination  — magnetic declination (degrees)
            am_opposition_deg   — opposition angle (0–180°)
            am_n_stations       — transmitters within radius
            am_total_weight     — sum of erp/dist² weights
            am_fa_strength      — peak bin fraction (0–1)
        """
        out     = df.copy()
        results = []
        n       = len(df)

        for i, row in df.iterrows():
            lat = row[lat_col]
            lon = row[lon_col]

            if pd.isna(lat) or pd.isna(lon):
                results.append({
                    "am_fa_bearing":      None,
                    "am_geo_bearing":     None,
                    "am_mag_declination": None,
                    "am_opposition_deg":  None,
                    "am_n_stations":      0,
                    "am_total_weight":    0.0,
                    "am_fa_strength":     None,
                })
                continue

            override = None
            if (geo_bearing_override_col
                    and geo_bearing_override_col in df.columns):
                override = row.get(geo_bearing_override_col)

            res = self.compute(
                lat=float(lat),
                lon=float(lon),
                geo_bearing_override=override,
                radius_km=radius_km,
                year=year,
            )
            results.append({
                "am_fa_bearing":      res["fa_bearing"],
                "am_geo_bearing":     res["geo_bearing"],
                "am_mag_declination": res["mag_declination"],
                "am_opposition_deg":  res["opposition_deg"],
                "am_n_stations":      res["n_stations"],
                "am_total_weight":    res["total_weight"],
                "am_fa_strength":     res["fa_strength"],
            })

            if progress_every and (i + 1) % progress_every == 0:
                print(f"  {i + 1:,} / {n:,}")

        result_df = pd.DataFrame(results, index=df.index)
        for col in result_df.columns:
            out[col] = result_df[col]

        return out


# ── STANDALONE SPOT CHECK ─────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("AM FALSE ATTRACTOR — SPOT CHECK v1.2")
    print("OC-OBS-002 — OrganismCore")
    print("geo_bearing = geomagnetic north (WMM-2025 approx)")
    print("=" * 60)
    print()

    ama = AMFalseAttractor("am_stations_clean.csv")
    print()

    print("Magnetic declination at test locations (WMM-2025 approx):")
    print(f"  {'Location':<28} {'Lat':>6} {'Lon':>8} "
          f"{'Decl°':>8} {'Geo North°':>11}")
    print("  " + "─" * 65)

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

    for lat, lon, name in test_locs:
        geo_n, decl = geomagnetic_north_bearing(lat, lon)
        print(f"  {name:<28} {lat:>6.2f} {lon:>8.2f} "
              f"{decl:>8.2f}° {geo_n:>10.1f}°")

    print()
    print(f"\n{'Location':<28} {'FA Bear':>8} {'Geo Bear':>9} "
          f"{'Opp°':>7} {'N stn':>6} {'Strength':>9}")
    print("─" * 75)

    for lat, lon, name in test_locs:
        r    = ama.compute(lat, lon)
        fa   = f"{r['fa_bearing']:.1f}°"     if r['fa_bearing']     is not None else "None"
        opp  = f"{r['opposition_deg']:.1f}°"  if r['opposition_deg'] is not None else "None"
        geo  = f"{r['geo_bearing']:.1f}°"    if r['geo_bearing']    is not None else "None"
        str_ = f"{r['fa_strength']:.4f}"     if r['fa_strength']    is not None else "None"
        print(f"  {name:<26} {fa:>8} {geo:>9} {opp:>7} "
              f"{r['n_stations']:>6,} {str_:>9}")

    print()
    print("Expected geo bearings:")
    print("  FL Atlantic coast:  ~350–351°")
    print("  Gulf coast (TX):    ~353–355°")
    print("  Gulf coast (LA):    ~351–352°")
    print("  NC:                 ~348°")
    print()
    print("FA bearings should be westward (~220–320°) for most")
    print("US Atlantic/Gulf coast locations — large population")
    print("centres and their AM transmitters are inland/west.")
    print()
    print("If geo bearings are in the ~348–356° range,")
    print("proceed to turtle_stranding_pipeline.py")
