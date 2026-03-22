"""
BUILD CABLE LANDING STATIONS TABLE
====================================
OC-OBS-002 — Sea Turtle Stranding Analysis
OrganismCore — Eric Robert Lawson

v3 — fetches individual cable detail endpoints
since all.json only contains id + name.
"""

import os
import sys
import json
import time
import requests
import pandas as pd

OUTPUT_FILE    = "cable_landing_stations.csv"
CACHE_DIR      = "cable_cache"
CABLES_INDEX   = "cables_raw.json"
DETAIL_URL     = "https://www.submarinecablemap.com/api/v3/cable/{cable_id}.json"
DELAY_SECONDS  = 0.3   # polite rate limit between requests

# Atlantic + Gulf coast bounding box
SCOPE_LAT_MIN = 24.0
SCOPE_LAT_MAX = 45.0
SCOPE_LON_MIN = -98.0
SCOPE_LON_MAX = -65.0

HEADERS = {"User-Agent": "Mozilla/5.0 (research/academic use)"}


# ── LOAD CABLE INDEX ──────────────────────────────────────────

def load_cable_index() -> list:
    if not os.path.exists(CABLES_INDEX):
        print(f"ERROR: {CABLES_INDEX} not found.")
        print("Run the previous script first to download the index.")
        sys.exit(1)
    with open(CABLES_INDEX) as f:
        cables = json.load(f)
    print(f"Cable index loaded: {len(cables)} cables")
    return cables


# ── FETCH CABLE DETAIL ────────────────────────────────────────

def fetch_cable_detail(cable_id: str) -> dict | None:
    """
    Fetch detail for one cable. Uses local cache if available.
    """
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_path = os.path.join(CACHE_DIR, f"{cable_id}.json")

    if os.path.exists(cache_path):
        with open(cache_path) as f:
            return json.load(f)

    url = DETAIL_URL.format(cable_id=cable_id)
    try:
        resp = requests.get(url, timeout=30, headers=HEADERS)
        resp.raise_for_status()
        data = resp.json()
        with open(cache_path, "w") as f:
            json.dump(data, f)
        return data
    except Exception as e:
        print(f"  WARN: failed to fetch {cable_id}: {e}")
        return None


# ── INSPECT ONE DETAIL RECORD ─────────────────────────────────

def inspect_detail(detail: dict) -> None:
    print()
    print("── SAMPLE DETAIL RECORD STRUCTURE ──")
    print(json.dumps(detail, indent=2)[:3000])
    print("...")
    print(f"── TOP-LEVEL KEYS: {list(detail.keys())}")
    print()


# ── EXTRACT ROWS FROM DETAIL ──────────────────────────────────

def extract_rows(cable_id: str, detail: dict) -> list:
    """
    Extract landing point rows from a cable detail record.
    Handles multiple known TeleGeography structures.
    """
    rows     = []
    name     = detail.get("name", cable_id)
    rfs      = detail.get("rfs", None)
    capacity = detail.get("capacity", None)

    # Parse install year
    install_year = None
    if rfs:
        try:
            install_year = int(str(rfs)[:4])
        except (ValueError, TypeError):
            pass

    # Parse capacity
    cap_mw = None
    if capacity:
        try:
            raw = str(capacity).lower()
            for unit in ["tbps","gbps","mw","kw","w","tb/s","gb/s"]:
                raw = raw.replace(unit, "")
            cap_mw = float(raw.replace(",","").strip())
        except (ValueError, AttributeError):
            pass

    cable_type = "power" if (cap_mw and cap_mw > 0) \
                 else "fiber_or_unknown"

    # Landing points — may be list of dicts or list of strings
    lp_list = (detail.get("landing_points") or
               detail.get("landingPoints") or
               detail.get("landing_point") or [])

    for lp in lp_list:
        lat, lon = None, None
        lp_name    = ""
        lp_country = ""
        lp_id      = ""

        if isinstance(lp, dict):
            lp_name    = lp.get("name","")
            lp_country = lp.get("country","")
            lp_id      = str(lp.get("id") or lp.get("slug",""))

            # Direct lat/lng
            for lk in ["lat","latitude"]:
                if lp.get(lk) is not None:
                    try: lat = float(lp[lk]); break
                    except: pass
            for lk in ["lng","lon","longitude"]:
                if lp.get(lk) is not None:
                    try: lon = float(lp[lk]); break
                    except: pass

            # GeoJSON geometry
            if lat is None:
                geo = lp.get("geometry") or lp.get("location") or {}
                if isinstance(geo, dict):
                    coords = geo.get("coordinates")
                    if coords and len(coords) >= 2:
                        try:
                            lon = float(coords[0])
                            lat = float(coords[1])
                        except: pass

        elif isinstance(lp, str):
            lp_id = lp
            # No coordinates in string-only format

        rows.append({
            "cable_id":      cable_id,
            "cable_name":    name,
            "lp_id":         lp_id,
            "landing_point": lp_name,
            "country":       lp_country,
            "landing_lat":   lat,
            "landing_lon":   lon,
            "capacity_mw":   cap_mw,
            "cable_type":    cable_type,
            "install_year":  install_year,
        })

    return rows


# ── MAIN ──────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("BUILD CABLE LANDING STATIONS TABLE")
    print("OC-OBS-002 — OrganismCore")
    print("=" * 60)
    print()

    cables  = load_cable_index()
    all_rows = []
    inspected = False

    print(f"Fetching detail for {len(cables)} cables...")
    print(f"Cache directory: {CACHE_DIR}/")
    print(f"(Cached cables will not be re-fetched)")
    print()

    for i, cable in enumerate(cables):
        cable_id = str(cable.get("id") or cable.get("slug",""))
        if not cable_id:
            continue

        detail = fetch_cable_detail(cable_id)
        if detail is None:
            continue

        # Inspect first successfully fetched detail record
        if not inspected:
            inspect_detail(detail)
            inspected = True

        rows = extract_rows(cable_id, detail)
        all_rows.extend(rows)

        # Progress every 50
        if (i + 1) % 50 == 0:
            cached = len(os.listdir(CACHE_DIR))
            print(f"  {i+1}/{len(cables)} cables processed "
                  f"| {cached} cached "
                  f"| {len(all_rows)} LP records so far")

        time.sleep(DELAY_SECONDS)

    print(f"\nDone. Total LP records: {len(all_rows)}")

    if not all_rows:
        print()
        print("ERROR: No landing point records extracted.")
        print("Check the SAMPLE DETAIL RECORD STRUCTURE printed")
        print("above and paste it back to Copilot.")
        sys.exit(1)

    df = pd.DataFrame(all_rows)

    # ── FILTER ────────────────────────────────────────────────
    print()
    print("Filtering...")

    before = len(df)
    df_with_coords = df.dropna(subset=["landing_lat","landing_lon"])
    df_no_coords   = df[df["landing_lat"].isna() |
                        df["landing_lon"].isna()]
    print(f"  Records with coordinates:    {len(df_with_coords):,}")
    print(f"  Records without coordinates: {len(df_no_coords):,}")

    df = df_with_coords.copy()

    if df.empty:
        print()
        print("WARNING: All landing points lack coordinates.")
        print("Saving full unfiltered table as diagnostic.")
        pd.DataFrame(all_rows).to_csv(
            "cable_debug_all.csv", index=False)
        print("Inspect cable_debug_all.csv manually.")
        sys.exit(1)

    before = len(df)
    df = df[
        df["landing_lat"].between(SCOPE_LAT_MIN, SCOPE_LAT_MAX) &
        df["landing_lon"].between(SCOPE_LON_MIN, SCOPE_LON_MAX)
    ]
    print(f"  After geographic scope filter: "
          f"{len(df):,} (removed {before - len(df):,})")

    power = df[df["cable_type"] == "power"]
    fiber = df[df["cable_type"] != "power"]
    print()
    print(f"  Power cable LPs in scope:  {len(power):,}")
    print(f"  Fiber/unknown LPs in scope: {len(fiber):,}")

    if len(power) > 0:
        print()
        print("  Power cables found:")
        for n in sorted(power["cable_name"].unique()):
            sub = power[power["cable_name"] == n]
            print(f"    {n}  "
                  f"(year: {sub['install_year'].iloc[0]}, "
                  f"LPs: {len(sub)})")

    df = df.sort_values(
        ["cable_type","cable_name","landing_lat"]
    ).reset_index(drop=True)

    df.to_csv(OUTPUT_FILE, index=False)
    print()
    print(f"Saved: {OUTPUT_FILE}")
    print(f"Rows:  {len(df):,}")
    print(f"Size:  {os.path.getsize(OUTPUT_FILE)/1024:.1f} KB")


if __name__ == "__main__":
    main()
