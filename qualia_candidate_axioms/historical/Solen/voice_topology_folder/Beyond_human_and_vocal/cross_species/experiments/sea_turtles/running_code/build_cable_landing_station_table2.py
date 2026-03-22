"""
BUILD CABLE LANDING STATIONS TABLE
====================================
OC-OBS-002 — Sea Turtle Stranding Analysis
OrganismCore — Eric Robert Lawson

v4 — Coordinates come from individual landing point
detail endpoints: /api/v3/landing-point/{slug}.json
Cable detail records are already cached in cable_cache/.
This script extracts all unique LP slugs from those
cached files, fetches each LP individually, joins
coordinates back to the cable records.
"""

import os
import sys
import json
import time
import requests
import pandas as pd

OUTPUT_FILE   = "cable_landing_stations.csv"
CABLE_CACHE   = "cable_cache"
LP_CACHE      = "lp_cache"
CABLES_INDEX  = "cables_raw.json"
LP_DETAIL_URL = "https://www.submarinecablemap.com/api/v3/landing-point/{slug}.json"
DELAY_SECONDS = 0.3

SCOPE_LAT_MIN = 24.0
SCOPE_LAT_MAX = 45.0
SCOPE_LON_MIN = -98.0
SCOPE_LON_MAX = -65.0

HEADERS = {"User-Agent": "Mozilla/5.0 (research/academic use)"}


# ── STEP 1: LOAD ALL CACHED CABLE DETAIL FILES ────────────────

def load_all_cable_details() -> list:
    """Load all cached cable detail JSON files."""
    details = []
    if not os.path.exists(CABLE_CACHE):
        print(f"ERROR: {CABLE_CACHE}/ directory not found.")
        print("Re-run the previous version to cache cable details.")
        sys.exit(1)

    files = [f for f in os.listdir(CABLE_CACHE)
             if f.endswith(".json")]
    print(f"Loading {len(files)} cached cable detail files...")

    for fname in files:
        path = os.path.join(CABLE_CACHE, fname)
        try:
            with open(path) as f:
                details.append(json.load(f))
        except Exception as e:
            print(f"  WARN: could not load {fname}: {e}")

    print(f"  Loaded: {len(details)} cable records")
    return details


# ── STEP 2: EXTRACT ALL UNIQUE LP SLUGS ───────────────────────

def extract_lp_slugs(cable_details: list) -> dict:
    """
    Extract all unique landing point slugs across all cables.
    Returns dict: slug -> {cable_ids, countries, names}
    for reference.
    """
    lp_map = {}  # slug -> list of cable_ids that use it

    for cable in cable_details:
        cable_id = cable.get("id", "")
        lps = cable.get("landing_points", [])
        for lp in lps:
            if not isinstance(lp, dict):
                continue
            slug = str(lp.get("id") or lp.get("slug", "")).strip()
            if not slug:
                continue
            if slug not in lp_map:
                lp_map[slug] = {
                    "cable_ids": [],
                    "name":      lp.get("name", ""),
                    "country":   lp.get("country", ""),
                }
            lp_map[slug]["cable_ids"].append(cable_id)

    print(f"  Unique landing point slugs: {len(lp_map)}")
    return lp_map


# ── STEP 3: FETCH INDIVIDUAL LP DETAIL ────────────────────────

def fetch_lp_detail(slug: str) -> dict | None:
    """Fetch one LP detail. Uses local cache if available."""
    os.makedirs(LP_CACHE, exist_ok=True)

    # Sanitise slug for use as filename
    safe = slug.replace("/", "_").replace("\\", "_")
    cache_path = os.path.join(LP_CACHE, f"{safe}.json")

    if os.path.exists(cache_path):
        try:
            with open(cache_path) as f:
                return json.load(f)
        except Exception:
            pass  # re-fetch if cache is corrupt

    url = LP_DETAIL_URL.format(slug=slug)
    try:
        resp = requests.get(url, timeout=30, headers=HEADERS)
        resp.raise_for_status()
        data = resp.json()
        with open(cache_path, "w") as f:
            json.dump(data, f)
        return data
    except Exception as e:
        return None


def inspect_lp_sample(lp_detail: dict) -> None:
    print()
    print("── SAMPLE LP DETAIL STRUCTURE ──")
    print(json.dumps(lp_detail, indent=2)[:1500])
    print(f"── TOP-LEVEL KEYS: {list(lp_detail.keys())}")
    print()


def extract_coords_from_lp(lp_detail: dict) -> tuple:
    """
    Extract lat/lon from an LP detail record.
    Returns (lat, lon) or (None, None).
    Handles direct fields and GeoJSON geometry.
    """
    lat, lon = None, None

    # Direct lat fields
    for lk in ["lat", "latitude", "lat_deg"]:
        v = lp_detail.get(lk)
        if v is not None:
            try:
                lat = float(v)
                break
            except (ValueError, TypeError):
                pass

    # Direct lon fields
    for lk in ["lng", "lon", "longitude", "lng_deg"]:
        v = lp_detail.get(v) if False else lp_detail.get(lk)
        if v is not None:
            try:
                lon = float(v)
                break
            except (ValueError, TypeError):
                pass

    # GeoJSON geometry
    if lat is None or lon is None:
        geo = lp_detail.get("geometry") or \
              lp_detail.get("location") or {}
        if isinstance(geo, dict):
            coords = geo.get("coordinates")
            if coords and len(coords) >= 2:
                try:
                    lon = float(coords[0])
                    lat = float(coords[1])
                except (ValueError, TypeError):
                    pass

    # Nested coordinate object
    if lat is None or lon is None:
        coord = lp_detail.get("coordinate") or \
                lp_detail.get("coordinates") or {}
        if isinstance(coord, dict):
            try:
                lat = float(coord.get("lat") or
                            coord.get("latitude", 0))
                lon = float(coord.get("lng") or
                            coord.get("lon") or
                            coord.get("longitude", 0))
            except (ValueError, TypeError):
                pass

    return lat, lon


# ── STEP 4: FETCH ALL LP COORDINATES ─────────────────────────

def fetch_all_lp_coords(lp_map: dict) -> dict:
    """
    Fetch coordinate detail for every unique LP slug.
    Returns dict: slug -> {lat, lon, name, country}
    """
    slugs     = list(lp_map.keys())
    lp_coords = {}
    inspected = False
    failed    = 0
    no_coords = 0

    print(f"Fetching coordinates for {len(slugs)} "
          f"landing points...")
    print(f"LP cache directory: {LP_CACHE}/")
    print()

    for i, slug in enumerate(slugs):
        detail = fetch_lp_detail(slug)

        if detail is None:
            failed += 1
            lp_coords[slug] = {"lat": None, "lon": None,
                                "name": lp_map[slug]["name"],
                                "country": lp_map[slug]["country"]}
            continue

        if not inspected:
            inspect_lp_sample(detail)
            inspected = True

        lat, lon = extract_coords_from_lp(detail)

        if lat is None:
            no_coords += 1

        lp_coords[slug] = {
            "lat":     lat,
            "lon":     lon,
            "name":    detail.get("name", lp_map[slug]["name"]),
            "country": detail.get("country",
                                  lp_map[slug]["country"]),
        }

        if (i + 1) % 100 == 0:
            cached = len(os.listdir(LP_CACHE))
            with_coords = sum(
                1 for v in lp_coords.values()
                if v["lat"] is not None
            )
            print(f"  {i+1}/{len(slugs)} LPs processed | "
                  f"{cached} cached | "
                  f"{with_coords} with coords | "
                  f"{failed} failed")

        time.sleep(DELAY_SECONDS)

    with_coords = sum(1 for v in lp_coords.values()
                      if v["lat"] is not None)
    print(f"\nLP fetch complete:")
    print(f"  Total:       {len(lp_coords)}")
    print(f"  With coords: {with_coords}")
    print(f"  No coords:   {no_coords}")
    print(f"  Failed:      {failed}")

    return lp_coords


# ── STEP 5: BUILD FINAL TABLE ─────────────────────────────────

def build_table(cable_details: list,
                lp_coords: dict) -> pd.DataFrame:
    """Join cable metadata with LP coordinates."""
    rows = []

    for cable in cable_details:
        cable_id   = cable.get("id", "")
        cable_name = cable.get("name", "")
        rfs        = cable.get("rfs") or cable.get("rfs_year")
        notes      = cable.get("notes", "")

        # Parse install year
        install_year = None
        if rfs:
            try:
                install_year = int(str(rfs)[:4])
            except (ValueError, TypeError):
                pass

        # Capacity — determines power vs fiber
        # TeleGeography does not include capacity in detail
        # endpoint for most cables. Power cables are identified
        # by notes containing "MW" or "kV" or "HVDC/HVAC".
        cap_mw     = None
        cable_type = "fiber_or_unknown"
        if notes:
            note_upper = str(notes).upper()
            if any(kw in note_upper for kw in
                   ["MW", "KV", "HVDC", "HVAC",
                    "POWER", "ELECTRIC", "ENERGY"]):
                cable_type = "power"

        lp_list = cable.get("landing_points", [])

        for lp in lp_list:
            if not isinstance(lp, dict):
                continue
            slug = str(lp.get("id") or lp.get("slug", "")).strip()
            coord = lp_coords.get(slug, {})

            rows.append({
                "cable_id":      cable_id,
                "cable_name":    cable_name,
                "lp_id":         slug,
                "landing_point": coord.get("name",
                                           lp.get("name", "")),
                "country":       coord.get("country",
                                           lp.get("country", "")),
                "landing_lat":   coord.get("lat"),
                "landing_lon":   coord.get("lon"),
                "capacity_mw":   cap_mw,
                "cable_type":    cable_type,
                "install_year":  install_year,
                "notes":         notes,
            })

    return pd.DataFrame(rows)


# ── STEP 6: FILTER ────────────────────────────────────────────

def filter_scope(df: pd.DataFrame) -> pd.DataFrame:
    print(f"\nFiltering {len(df):,} total LP records...")

    before = len(df)
    df = df.dropna(subset=["landing_lat", "landing_lon"])
    print(f"  With coordinates: {len(df):,} "
          f"(removed {before - len(df):,} missing)")

    if df.empty:
        return df

    before = len(df)
    df = df[
        df["landing_lat"].between(SCOPE_LAT_MIN, SCOPE_LAT_MAX) &
        df["landing_lon"].between(SCOPE_LON_MIN, SCOPE_LON_MAX)
    ]
    print(f"  In Atlantic/Gulf scope: {len(df):,} "
          f"(removed {before - len(df):,})")

    power = df[df["cable_type"] == "power"]
    fiber = df[df["cable_type"] != "power"]
    print(f"\n  Power cable LPs:        {len(power):,}")
    print(f"  Fiber/unknown LPs:      {len(fiber):,}")

    if not df.empty:
        print(f"\n  All cables in scope:")
        for name in sorted(df["cable_name"].unique()):
            sub = df[df["cable_name"] == name]
            yr  = sub["install_year"].iloc[0]
            ct  = sub["cable_type"].iloc[0]
            print(f"    [{ct:>18}]  {name}  "
                  f"(year: {yr}, LPs: {len(sub)})")

    return df.sort_values(
        ["cable_type", "cable_name", "landing_lat"]
    ).reset_index(drop=True)


# ── MAIN ──────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("BUILD CABLE LANDING STATIONS TABLE v4")
    print("OC-OBS-002 — OrganismCore")
    print("=" * 60)
    print()

    cable_details = load_all_cable_details()
    lp_map        = extract_lp_slugs(cable_details)
    lp_coords     = fetch_all_lp_coords(lp_map)
    df            = build_table(cable_details, lp_coords)
    df            = filter_scope(df)

    df.to_csv(OUTPUT_FILE, index=False)
    print(f"\nSaved: {OUTPUT_FILE}")
    print(f"Rows:  {len(df):,}")
    print(f"Size:  {os.path.getsize(OUTPUT_FILE)/1024:.1f} KB")
    print()
    print("cable_landing_stations.csv is ready.")


if __name__ == "__main__":
    main()
