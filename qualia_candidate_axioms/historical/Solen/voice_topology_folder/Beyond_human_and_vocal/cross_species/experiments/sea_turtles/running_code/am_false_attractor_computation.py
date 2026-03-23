"""
AM FALSE ATTRACTOR COMPUTATION
===============================
OC-OBS-002 — Sea Turtle Stranding Analysis
OrganismCore — Eric Robert Lawson
March 2026

VERSION: 1.3 — geo_bearing formula correctly fixed
  v1.0: geo_bearing used nearest FL nesting cluster bearing.
  v1.1: switched to geomagnetic north but formula inverted:
          (360.0 - decl) with decl=-9.77 → 369.77 % 360 = 9.77°
  v1.2: attempted fix with (-decl) % 360.0:
          -(-9.77) % 360 = 9.77°  — still wrong, same result.
  v1.3: correct formula derived explicitly:
          decl = -9.77° means magnetic north is 9.77° WEST
          of geographic north. West of north on a compass =
          bearing 360 - 9.77 = 350.23°.
          Formula: geo_north = (360.0 + decl) % 360.0
          Check: (360.0 + (-9.77)) % 360.0 = 350.23°  ✓

MAGNETIC DECLINATION SIGN CONVENTION:
  Negative declination = magnetic north is WEST of geographic north.
  geo_north bearing = (360.0 + declination) % 360.0
  For decl = -9.77°: (360 - 9.77) = 350.23° (just west of north ✓)
  For decl = +5.00°: (360 + 5.00) % 360 = 5.00° (just east of north ✓)
  For decl =  0.00°: (360 + 0.00) % 360 = 0.00° (geographic north ✓)
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

FL_NESTING_CLUSTERS = [
    (28.06, -80.56),
    (27.18, -80.21),
    (26.50, -80.07),
    (25.83, -80.12),
    (25.08, -80.45),
    (29.08, -81.04),
]


# ── MAGNETIC DECLINATION (WMM-2025 approximation) ─────────────

def magnetic_declination_deg(lat, lon, year=2026.2):
    """
    WMM-2025 polynomial approximation.
    Accuracy ±1° for lat 24–45°N, lon -98° to -65°W, 2026.
    Negative = west of geographic north (US Atlantic/Gulf coast).
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
    Bearing toward geomagnetic north at (lat, lon).

    Derivation:
      decl = angle FROM geographic north TO magnetic north,
             clockwise positive.
      Negative decl (US coast) = magnetic north is WEST of
      geographic north.
      "9.77° west of north" = bearing 360 - 9.77 = 350.23°.
      Formula: geo_north = (360.0 + decl) % 360.0

    Verification:
      decl = -9.77°  → (360 + (-9.77)) % 360 = 350.23°  ✓
      decl =  0.00°  → (360 + 0.00)   % 360 =   0.00°  ✓
      decl = +5.00°  → (360 + 5.00)   % 360 =   5.00°  ✓
    """
    decl      = magnetic_declination_deg(lat, lon, year)
    geo_north = (360.0 + decl) % 360.0          # v1.3 — correct
    return geo_north, decl


def switch_to_wmm():
    """
    UPGRADE PATH: full WMM-2025 via geomag library.

        pip install geomag
        import geomag
        gm = geomag.GeoMag()
        result = gm.GeoMag(lat, lon, alt=0, time=2026.2)
        decl = result.dec
        geo_north = (360.0 + decl) % 360.0
        return geo_north, decl
    """
    pass


# ── OPTIONAL: NESTING CLUSTER BEARING ─────────────────────────

def nearest_nesting_cluster_bearing(lat, lon):
    """NOT used in primary A1. Retained for Movebank work."""
    cluster_lats = np.array([c[0] for c in FL_NESTING_CLUSTERS])
    cluster_lons = np.array([c[1] for c in FL_NESTING_CLUSTERS])
    dists        = haversine_km(lat, lon, cluster_lats, cluster_lons)
    nearest_idx  = int(np.argmin(dists))
    return bearing_deg(
        lat, lon,
        np.array([cluster_lats[nearest_idx]]),
        np.array([cluster_lons[nearest_idx]])
    )[0]


# ── HAVERSINE DISTANCE ────────────────���────────────────────────

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
    |fa_bearing - geo_bearing| normalised to 0–180°.
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
    print("AM FALSE ATTRACTOR — SPOT CHECK v1.3")
    print("OC-OBS-002 — OrganismCore")
    print("geo_bearing = geomagnetic north (WMM-2025 approx)")
    print("=" * 60)
    print()

    # ── Formula self-test — runs before loading any data ──────
    print("Formula self-test:")
    formula_tests = [
        (-9.77,  350.23),
        (-12.35, 347.65),
        (-7.02,  352.98),
        ( 0.00,    0.00),
        ( 5.00,    5.00),
    ]
    formula_ok = True
    for decl, expected in formula_tests:
        result = (360.0 + decl) % 360.0
        ok     = abs(result - expected) < 0.01
        print(f"  decl={decl:>7.2f}°  →  geo_north={result:>7.2f}°  "
              f"(expected {expected:.2f}°)  {'✓' if ok else '✗ FAIL'}")
        if not ok:
            formula_ok = False
    if not formula_ok:
        print("\nFORMULA SELF-TEST FAILED — do not proceed.")
        raise SystemExit(1)
    print("  All formula checks pass.\n")

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

    print("Declination table:")
    print(f"  {'Location':<28} {'Lat':>6} {'Lon':>8} "
          f"{'Decl°':>8} {'Geo North°':>11}")
    print("  " + "─" * 65)
    for lat, lon, name in test_locs:
        geo_n, decl = geomagnetic_north_bearing(lat, lon)
        print(f"  {name:<28} {lat:>6.2f} {lon:>8.2f} "
              f"{decl:>8.2f}° {geo_n:>10.1f}°")

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
    print("Expected geo bearings: ~348–356° for all locations.")
    print("If the formula self-test passed and geo bearings are")
    print("in that range, proceed to turtle_stranding_pipeline.py")
