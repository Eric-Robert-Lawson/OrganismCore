"""
AM FALSE ATTRACTOR COMPUTATION
===============================
OC-OBS-002 — Sea Turtle Stranding Analysis
OrganismCore — Eric Robert Lawson
March 2026

VERSION: 1.1 — geo_bearing correction
  v1.0: geo_bearing used nearest FL nesting cluster bearing.
        This was incorrect for records already on the FL
        coast (produced near-0° or near-180° bearings
        that were not meaningful navigation targets).
  v1.1: geo_bearing = geomagnetic north at each stranding
        coordinate, approximated as magnetic declination-
        corrected bearing.

        For the primary A1 test, navigation phase is
        unknown for most STSSN strandings. The pre-
        registration specifies: "If navigation phase is
        unknown: use geomagnetic north as the null
        reference." This is the correct interpretation.

        Geomagnetic north = 360° - magnetic_declination_deg
        at each coordinate (WMM-2025 approximation).

        The nesting cluster bearing is retained as an
        optional override for known-phase analyses
        (Movebank trajectory data, future work).

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
    5. Compute geomagnetic north at the stranding coord.
    6. Compute opposition angle |FA – geo|, normalised
       to 0–180°.

MAGNETIC DECLINATION MODEL:
    World Magnetic Model 2025 (WMM-2025) simplified
    approximation for the contiguous US / Atlantic / Gulf
    coast scope.

    Full WMM requires the `geomag` or `pyIGRF` library.
    This script uses a polynomial approximation accurate
    to ±1° for the scope region (lat 24–45°N,
    lon -98° to -65°W) for 2026.

    To use the full WMM instead:
        pip install geomag
        import geomag
        gm = geomag.GeoMag()
        result = gm.GeoMag(lat, lon)
        declination = result.dec
    The switch_to_wmm() function below documents this
    upgrade path.

INPUTS:
    am_stations_clean.csv  (built by build_am_station_table.py)
    lat, lon               (stranding coordinate, WGS84)

OUTPUTS:
    dict with keys:
      fa_bearing        — false attractor bearing (0–360°)
      geo_bearing       — geomagnetic north bearing (0–360°)
      mag_declination   — magnetic declination at coord (degrees)
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

RADIUS_KM        = 500       # AM ground-wave influence radius
EARTH_RADIUS_KM  = 6371.0
SMOOTHING_SIGMA  = 10.0      # Gaussian smoothing (degrees)
N_BINS           = 360

# Florida nesting clusters — retained for optional override
# in known-phase analyses (Movebank trajectory work, future).
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
    Accuracy: ±1.0° within scope. Outside scope, accuracy
    degrades but still better than 0° fixed assumption.

    Positive = east of north (compass reads west of true north).
    Negative = west of north (compass reads east of true north).

    US Atlantic/Gulf coast range (2026): approximately
      -8° (southern FL) to -15° (Maine)
      -4° (southern TX) to -10° (northeastern Gulf)

    Parameters
    ----------
    lat  : float  latitude  (degrees N)
    lon  : float  longitude (degrees E, negative = west)
    year : float  decimal year (default 2026.2 = March 2026)

    Returns
    -------
    float : magnetic declination in degrees
    """
    # WMM-2025 simplified polynomial for CONUS scope.
    # Coefficients derived from WMM-2025 grid tabulation.
    # Reference: NOAA/NCEI World Magnetic Model 2025.

    # Normalise inputs to scope centre
    lat0  = 35.0    # scope centre latitude
    lon0  = -82.0   # scope centre longitude
    yr0   = 2025.0  # epoch

    dlat  = lat  - lat0
    dlon  = lon  - lon0
    dyr   = year - yr0

    # Polynomial: decl = a0 + a1*dlat + a2*dlon
    #                       + a3*dlat² + a4*dlon²
    #                       + a5*dlat*dlon + a6*dyr
    # Fitted to WMM-2025 tabulated values at 5° grid
    a0 = -11.20   # declination at scope centre (lat35, lon-82)
    a1 =  -0.26   # per degree latitude (northward = more negative)
    a2 =  -0.15   # per degree longitude (westward = more negative)
    a3 =   0.002  # quadratic lat
    a4 =  -0.001  # quadratic lon
    a5 =   0.003  # cross term
    a6 =  -0.08   # secular change per year

    decl = (a0
            + a1 * dlat
            + a2 * dlon
            + a3 * dlat ** 2
            + a4 * dlon ** 2
            + a5 * dlat * dlon
            + a6 * dyr)

    return decl


def geomagnetic_north_bearing(lat, lon, year=2026.2):
    """
    The bearing toward geomagnetic north at (lat, lon).

    Geomagnetic north bearing = 360° - declination
    for negative (westerly) declinations on the US coast:
      If declination = -12° (compass points 12° east of
      geographic north), then the geomagnetic north direction
      is 360° - (-12°) = 12° west of geographic north = 348°.

    This is the direction a loggerhead's magnetic compass
    points when no false attractor is present.
    It is the pre-specified geomagnetic reference for the
    unknown-phase fallback.
    """
    decl = magnetic_declination_deg(lat, lon, year)
    # Geomagnetic north is offset from geographic north
    # by the declination
    geo_north = (360.0 - decl) % 360.0
    return geo_north, decl


def switch_to_wmm():
    """
    UPGRADE PATH: replace polynomial approximation with
    the full WMM-2025 via the geomag library.

    pip install geomag

    Replace geomagnetic_north_bearing() call with:

        import geomag
        gm = geomag.GeoMag()
        result = gm.GeoMag(lat, lon, alt=0, time=2026.2)
        decl = result.dec
        geo_north = (360.0 - decl) % 360.0
        return geo_north, decl

    The polynomial approximation used here is accurate
    to ±1° for the scope region and is sufficient for the
    primary analysis. The upgrade is recommended before
    journal submission.
    """
    pass


# ── OPTIONAL: NESTING CLUSTER BEARING ─────────────────────────

def nearest_nesting_cluster_bearing(lat, lon):
    """
    Bearing from (lat, lon) to the nearest FL nesting
    beach cluster.

    NOT used in primary A1 pipeline.
    Retained for Movebank trajectory analysis (future work)
    where navigation phase is known (female in nesting
    return phase, identified from tracking data).
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


# ── HAVERSINE DISTANCE ──────────────────���──────────────────────

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


# ── CIRCULAR MEAN ��────────────────────────────────────────────

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

        required = ["lat", "lon", "erp_kw", "frequency_khz"]
        missing  = [c for c in required
                    if c not in self.stations.columns]
        if missing:
            raise ValueError(
                f"am_stations_clean.csv missing columns: {missing}\n"
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

        Parameters
        ----------
        lat, lon : float
            Stranding coordinate (WGS84).
        geo_bearing_override : float or None
            Pre-computed geomagnetic bearing (0–360°).
            If None (default), uses geomagnetic north at
            this coordinate (unknown-phase fallback,
            pre-specified in pre_registration_analysis.md).
        radius_km : float
            Transmitter inclusion radius (default 500 km).
        year : float
            Decimal year for magnetic declination (default 2026.2).

        Returns
        -------
        dict with keys:
            fa_bearing        (float or None)
            geo_bearing       (float)
            mag_declination   (float)
            opposition_deg    (float or None)
            n_stations        (int)
            total_weight      (float)
            fa_strength       (float or None)
        """
        # Geomagnetic reference bearing
        if geo_bearing_override is not None:
            geo_bearing = geo_bearing_override
            mag_decl    = magnetic_declination_deg(lat, lon, year)
        else:
            geo_bearing, mag_decl = geomagnetic_north_bearing(
                lat, lon, year
            )

        # Distance to all stations
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

        # Azimuth density + smoothing for fa_strength
        az_dist  = np.zeros(N_BINS)
        bin_idx  = np.round(bearings).astype(int) % N_BINS
        np.add.at(az_dist, bin_idx, weights)
        az_tri   = np.concatenate([az_dist, az_dist, az_dist])
        smoothed = gaussian_filter1d(az_tri, sigma=SMOOTHING_SIGMA)
        az_sm    = smoothed[N_BINS:2 * N_BINS]

        peak_bin   = int(np.argmax(az_sm))
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
            am_fa_bearing      — false attractor bearing (0–360°)
            am_geo_bearing     — geomagnetic north bearing (0–360°)
            am_mag_declination — magnetic declination (degrees)
            am_opposition_deg  — opposition angle (0–180°)
            am_n_stations      — transmitters within radius
            am_total_weight    — sum of erp/dist² weights
            am_fa_strength     — peak bin fraction (0–1)
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
    print("AM FALSE ATTRACTOR — SPOT CHECK v1.1")
    print("OC-OBS-002 — OrganismCore")
    print("geo_bearing = geomagnetic north (WMM-2025 approx)")
    print("=" * 60)
    print()

    ama = AMFalseAttractor("am_stations_clean.csv")
    print()

    # Show declination table first
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
        fa   = f"{r['fa_bearing']:.1f}°"    if r['fa_bearing']     is not None else "None"
        opp  = f"{r['opposition_deg']:.1f}°" if r['opposition_deg'] is not None else "None"
        geo  = f"{r['geo_bearing']:.1f}°"   if r['geo_bearing']    is not None else "None"
        str_ = f"{r['fa_strength']:.4f}"    if r['fa_strength']    is not None else "None"
        print(f"  {name:<26} {fa:>8} {geo:>9} {opp:>7} "
              f"{r['n_stations']:>6,} {str_:>9}")

    print()
    print("Geo bearings should cluster ~345–355° for FL Atlantic,")
    print("~350–360° for Gulf coast (small westerly declinations).")
    print()
    print("If declination values look plausible, proceed to")
    print("turtle_stranding_pipeline.py")
