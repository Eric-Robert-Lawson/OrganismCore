"""
BUILD CABLE LANDING STATIONS TABLE
====================================
OC-OBS-002 — Sea Turtle Stranding Analysis
OrganismCore — Eric Robert Lawson

v7 — Production version. GeoJSON coordinate coverage is
authoritative: 1,335 landing points are available from the
lintaojlu mirror of the TeleGeography GeoJSON. Of the
~3,200 unique LP slugs referenced in the cable cache,
~537 have no coordinates in the GeoJSON — these are dropped.
This is expected and documented.

Verified output (2026-03-22):
  GeoJSON LPs:          1,335
  Cable cache files:      690
  Total LP records:     2,691
  Matched with coords:  2,093  (598 unmatched slugs dropped)
  In Atlantic/Gulf scope:  60  (35 cables)
  Global output:        2,093  (all matched LPs worldwide)

Sources:
  Landing point coordinates (FeatureCollection):
    https://raw.githubusercontent.com/lintaojlu/
    submarine_cable_information/master/web/public/api/v3/
    landing-point/landing-point-geo.json
  Cable metadata: local cable_cache/ (already fetched)

Manual fallback for lp_all.json:
  Save the GeoJSON FeatureCollection as lp_all.json
  in the working directory. The script loads from cache
  and skips the download.
"""

import os
import sys
import json
import requests
import pandas as pd

OUTPUT_FILE        = "cable_landing_stations.csv"
OUTPUT_FILE_GLOBAL = "cable_landing_stations_global.csv"
CABLE_CACHE        = "cable_cache"

LP_GEOJSON_URL = (
    "https://raw.githubusercontent.com/lintaojlu/"
    "submarine_cable_information/master/web/public/api/v3/"
    "landing-point/landing-point-geo.json"
)

HEADERS = {"User-Agent": "Mozilla/5.0 (research/academic use)"}

# Atlantic + Gulf coast bounding box
SCOPE_LAT_MIN = 24.0
SCOPE_LAT_MAX = 45.0
SCOPE_LON_MIN = -98.0
SCOPE_LON_MAX = -65.0


# ── STEP 1: LOAD LP GEOJSON ───────────────────────────────────

def fetch_lp_geojson() -> dict:
    """
    Load LP GeoJSON. Uses lp_all.json cache if present —
    drop the file manually to force a fresh download.
    """
    cache = "lp_all.json"

    if os.path.exists(cache):
        print(f"Loading LP GeoJSON from cache: {cache}")
        with open(cache) as f:
            data = json.load(f)
        n = len(data.get("features", [])) \
            if isinstance(data, dict) else len(data)
        print(f"  {n:,} features loaded")
        return data

    print(f"Downloading LP GeoJSON...")
    print(f"  {LP_GEOJSON_URL}")
    try:
        resp = requests.get(LP_GEOJSON_URL, timeout=60,
                            headers=HEADERS)
        resp.raise_for_status()
        data = resp.json()
        with open(cache, "w") as f:
            json.dump(data, f)
        n = len(data.get("features", [])) \
            if isinstance(data, dict) else len(data)
        print(f"  Downloaded: {n:,} features. Cached to {cache}")
        return data
    except Exception as e:
        print(f"\n  Download failed: {e}")
        print()
        print("─" * 50)
        print("MANUAL FALLBACK:")
        print("  Save the GeoJSON FeatureCollection as")
        print("  lp_all.json in this directory, then re-run.")
        print("─" * 50)
        sys.exit(1)


# ── STEP 2: BUILD LP LOOKUP ─────��─────────────────────────────

def build_lp_lookup(lp_data) -> dict:
    """
    Build slug -> {lat, lon, name, country} lookup.
    Handles FeatureCollection, plain list, and plain dict.

    Coverage note: the lintaojlu GeoJSON contains 1,335
    landing points. ~537 slugs in the cable cache have no
    entry here — they are dropped at the coord-filter step.
    This is the full extent of publicly available coordinate
    data from this source.
    """
    print()
    print("Building LP coordinate lookup...")

    if isinstance(lp_data, dict):
        feat_count = len(lp_data.get("features", []))
        print(f"  Format: {lp_data.get('type','dict')}, "
              f"{feat_count:,} features")
    elif isinstance(lp_data, list):
        print(f"  Format: list, {len(lp_data):,} entries")

    lookup = {}

    def add(slug, lat, lon, name, country):
        if slug:
            lookup[slug] = {"lat": lat, "lon": lon,
                            "name": name, "country": country}

    # ── FeatureCollection ─────────────────────────────────────
    if isinstance(lp_data, dict) and \
            lp_data.get("type") == "FeatureCollection":
        for feat in lp_data.get("features", []):
            props = feat.get("properties", {})
            geo   = feat.get("geometry", {})
            slug  = str(props.get("id") or
                        props.get("slug", "")).strip()
            name    = props.get("name", "")
            country = props.get("country", "")
            lat = lon = None
            if isinstance(geo, dict) and \
                    geo.get("type") == "Point":
                coords = geo.get("coordinates", [])
                if len(coords) >= 2:
                    try:
                        lon = float(coords[0])  # GeoJSON: [lon, lat]
                        lat = float(coords[1])
                    except (TypeError, ValueError):
                        pass
            add(slug, lat, lon, name, country)

    # ── Plain list ────────────────────────────────────────────
    elif isinstance(lp_data, list):
        for item in lp_data:
            if not isinstance(item, dict):
                continue
            slug    = str(item.get("id") or
                          item.get("slug", "")).strip()
            name    = item.get("name", "")
            country = item.get("country", "")
            lat = lon = None
            for lk in ["lat", "latitude"]:
                if item.get(lk) is not None:
                    try: lat = float(item[lk]); break
                    except (TypeError, ValueError): pass
            for lk in ["lng", "lon", "longitude"]:
                if item.get(lk) is not None:
                    try: lon = float(item[lk]); break
                    except (TypeError, ValueError): pass
            if lat is None:
                geo = item.get("geometry", {})
                if isinstance(geo, dict):
                    coords = geo.get("coordinates", [])
                    if len(coords) >= 2:
                        try:
                            lon = float(coords[0])
                            lat = float(coords[1])
                        except (TypeError, ValueError):
                            pass
            add(slug, lat, lon, name, country)

    # ── Plain dict keyed by slug ──────────────────────────────
    elif isinstance(lp_data, dict):
        for slug, item in lp_data.items():
            if not isinstance(item, dict):
                continue
            name    = item.get("name", "")
            country = item.get("country", "")
            lat = lon = None
            for lk in ["lat", "latitude"]:
                if item.get(lk) is not None:
                    try: lat = float(item[lk]); break
                    except (TypeError, ValueError): pass
            for lk in ["lng", "lon", "longitude"]:
                if item.get(lk) is not None:
                    try: lon = float(item[lk]); break
                    except (TypeError, ValueError): pass
            add(slug, lat, lon, name, country)

    with_coords = sum(1 for v in lookup.values()
                      if v["lat"] is not None)
    print(f"  Lookup entries:      {len(lookup):,}")
    print(f"  With coordinates:    {with_coords:,}")
    print(f"  Without coordinates: {len(lookup) - with_coords:,}")

    if len(lookup) == 0:
        print()
        print("ERROR: LP lookup is empty. GeoJSON format not "
              "recognised.")
        sys.exit(1)

    return lookup


# ── STEP 3: LOAD CABLE CACHE ──────────────────────────────────

def load_cable_details() -> list:
    """Load all cached cable detail JSON files."""
    if not os.path.exists(CABLE_CACHE):
        print(f"ERROR: {CABLE_CACHE}/ not found.")
        sys.exit(1)
    files   = sorted(f for f in os.listdir(CABLE_CACHE)
                     if f.endswith(".json"))
    details = []
    for fname in files:
        try:
            with open(os.path.join(CABLE_CACHE, fname)) as f:
                details.append(json.load(f))
        except Exception:
            pass
    print(f"Cable details loaded: {len(details):,}")
    return details


# ── STEP 4: BUILD TABLE ───────────────────────────────────────

def build_table(cable_details: list,
                lp_lookup: dict) -> pd.DataFrame:
    """
    Join cable detail records with LP coordinate lookup.

    For each cable → landing_points list, attempt slug
    lookup in the GeoJSON. Unmatched slugs get None coords
    and are removed at the filter step.

    Power cable detection uses notes keywords — TeleGeography
    does not expose a structured power/fiber flag.
    """
    rows            = []
    unmatched_slugs = set()

    for cable in cable_details:
        cable_id   = cable.get("id", "")
        cable_name = cable.get("name", "")
        rfs        = cable.get("rfs") or cable.get("rfs_year")
        notes      = str(cable.get("notes") or "")
        is_planned = cable.get("is_planned", False)

        if is_planned:
            continue

        install_year = None
        if rfs:
            try:
                install_year = int(str(rfs)[:4])
            except (ValueError, TypeError):
                pass

        note_up    = notes.upper()
        cable_type = "power" if any(
            kw in note_up for kw in
            ["MW", "KV", "HVDC", "HVAC",
             "POWER", "ELECTRIC", "ENERGY"]
        ) else "fiber_or_unknown"

        for lp in cable.get("landing_points", []):
            if not isinstance(lp, dict):
                continue
            slug  = str(lp.get("id") or
                        lp.get("slug", "")).strip()
            coord = lp_lookup.get(slug)

            if coord is None:
                unmatched_slugs.add(slug)
                lat = lon = None
                lp_name = lp.get("name", "")
                country = lp.get("country", "")
            else:
                lat     = coord["lat"]
                lon     = coord["lon"]
                lp_name = coord["name"] or lp.get("name", "")
                country = coord["country"] or lp.get("country", "")

            rows.append({
                "cable_id":      cable_id,
                "cable_name":    cable_name,
                "lp_id":         slug,
                "landing_point": lp_name,
                "country":       country,
                "landing_lat":   lat,
                "landing_lon":   lon,
                "cable_type":    cable_type,
                "install_year":  install_year,
                "notes":         notes,
            })

    print(f"\nTable built: {len(rows):,} LP records total")
    print(f"  Matched in GeoJSON:  "
          f"{len(rows) - len(unmatched_slugs):,}")
    print(f"  Unique unmatched slugs: {len(unmatched_slugs):,}")
    print(f"  (These slugs exist in cable cache but have no")
    print(f"   coordinates in the GeoJSON — expected, see note")
    print(f"   in module docstring.)")

    return pd.DataFrame(rows) if rows else pd.DataFrame()


# ── STEP 5: FILTER AND SAVE ───────────────────────────────────

def filter_and_save(df: pd.DataFrame) -> pd.DataFrame:
    """
    1. Drop rows without coordinates.
    2. Save global (all matched LPs) to OUTPUT_FILE_GLOBAL.
    3. Filter to Atlantic/Gulf scope.
    4. Save scoped output to OUTPUT_FILE.
    """
    if df.empty:
        print("\nERROR: Empty table before filtering.")
        return df

    print(f"\nFiltering {len(df):,} total records...")

    # ── Coord filter ──────────────────────────────────────────
    before = len(df)
    df = df.dropna(subset=["landing_lat", "landing_lon"])
    print(f"  With coordinates:       {len(df):,} "
          f"(removed {before - len(df):,} unmatched)")

    if df.empty:
        print("  ERROR: No records with coordinates.")
        return df

    # ── Save global ─────────────────────��─────────────────────
    df_global = df.sort_values(
        ["cable_type", "cable_name", "landing_lat"]
    ).reset_index(drop=True)
    df_global.to_csv(OUTPUT_FILE_GLOBAL, index=False)
    print(f"\n  Global output saved:    {OUTPUT_FILE_GLOBAL}")
    print(f"  Global rows:            {len(df_global):,}")

    # ── Geographic scope filter ───────────────────────────────
    before = len(df)
    df = df[
        df["landing_lat"].between(SCOPE_LAT_MIN, SCOPE_LAT_MAX) &
        df["landing_lon"].between(SCOPE_LON_MIN, SCOPE_LON_MAX)
    ]
    print(f"\n  In Atlantic/Gulf scope: {len(df):,} "
          f"(removed {before - len(df):,})")

    if df.empty:
        print("  No records in scope.")
        return df

    power = df[df["cable_type"] == "power"]
    fiber = df[df["cable_type"] != "power"]
    print(f"\n  Power cable LPs:        {len(power):,}")
    print(f"  Fiber/unknown LPs:      {len(fiber):,}")
    print(f"\n  All cables in scope:")
    for name in sorted(df["cable_name"].unique()):
        sub = df[df["cable_name"] == name]
        yr  = sub["install_year"].iloc[0]
        ct  = sub["cable_type"].iloc[0]
        lps = len(sub)
        print(f"    [{ct:>18}]  {name}  "
              f"(year: {yr}, LPs: {lps})")

    return df.sort_values(
        ["cable_type", "cable_name", "landing_lat"]
    ).reset_index(drop=True)


# ── MAIN ──────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("BUILD CABLE LANDING STATIONS TABLE v7")
    print("OC-OBS-002 — OrganismCore")
    print("=" * 60)
    print()

    lp_data       = fetch_lp_geojson()
    lp_lookup     = build_lp_lookup(lp_data)
    cable_details = load_cable_details()
    df            = build_table(cable_details, lp_lookup)
    df            = filter_and_save(df)

    df.to_csv(OUTPUT_FILE, index=False)
    print(f"\nSaved: {OUTPUT_FILE}")
    print(f"Rows:  {len(df):,}")
    if not df.empty:
        print(f"Size:  {os.path.getsize(OUTPUT_FILE)/1024:.1f} KB")
        print()
        print("cable_landing_stations.csv — Atlantic/Gulf scope, "
              "ready.")
        print("cable_landing_stations_global.csv — all matched "
              "LPs worldwide.")


if __name__ == "__main__":
    main()
