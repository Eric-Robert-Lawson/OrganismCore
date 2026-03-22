"""
BUILD AM STATION TABLE
======================
OC-OBS-002 — Sea Turtle Stranding Analysis
OrganismCore — Eric Robert Lawson

Parses FCC AM Query "List" text export.
Pipe-delimited, coordinates in DMS format.

Sample row:
|CFHS|530 kHz|AM||UNL|Unlimited|C|C|CP|FORT FRANCES|ON|CA|
CA_314615|0.05 kW|||-|106053|N|48|36|34.8|W|93|24|0.5|-|...|

Column positions (0-indexed after splitting on |):
  0  callsign
  1  frequency (e.g. "530   kHz")
  2  service_code
  3  (blank)
  4  status_code
  5  status_label
  6  (class)
  7  (class)
  8  app_type
  9  city
  10 state
  11 country
  12 facility_id
  13 power (e.g. "0.05   kW")
  14 (blank)
  15 (blank)
  16 (dash)
  17 internal_id
  18 lat_dir  (N/S)
  19 lat_deg
  20 lat_min
  21 lat_sec
  22 lon_dir  (E/W)
  23 lon_deg
  24 lon_min
  25 lon_sec
  ... remaining columns not needed

OUTPUT: am_stations_clean.csv

REQUIRES:
    pip install pandas
"""

import os
import sys
import re
import pandas as pd

INPUT_FILE  = "fcc_am_query.txt"
OUTPUT_FILE = "am_stations_clean.csv"

AM_FREQ_MIN = 530
AM_FREQ_MAX = 1700


# ── DMS CONVERSION ────────────────────────────────────────────

def dms_to_decimal(deg, mn, sec, direction):
    """Convert degrees/minutes/seconds + direction to decimal."""
    try:
        d = float(deg)
        m = float(mn)
        s = float(sec)
        decimal = d + m / 60.0 + s / 3600.0
        if str(direction).strip().upper() in ("S", "W"):
            decimal = -decimal
        return round(decimal, 6)
    except (ValueError, TypeError):
        return None


# ── PARSE FREQUENCY ───────────────────────────────────────────

def parse_freq_khz(raw):
    """Extract numeric kHz value from strings like '530   kHz'."""
    try:
        return float(re.sub(r"[^\d.]", "", str(raw).split("k")[0]
                            .split("K")[0]))
    except (ValueError, AttributeError):
        return None


# ── PARSE POWER ───────────────────────────────────────────────

def parse_power_kw(raw):
    """Extract numeric kW value from strings like '0.05   kW'."""
    try:
        num = re.sub(r"[^\d.]", "", str(raw).lower().split("k")[0])
        return float(num) if num else None
    except (ValueError, AttributeError):
        return None


# ── PARSE FCC QUERY TEXT FILE ─────────────────────────────────

def parse_fcc_query_file(filepath):
    """
    Parse the FCC AM Query List text export.
    Returns a list of dicts, one per station.
    """
    rows = []
    skipped = 0
    parse_errors = 0

    with open(filepath, encoding="latin-1") as f:
        lines = f.readlines()

    print(f"  Total lines in file: {len(lines):,}")

    # Show first 5 lines for confirmation
    print("  First 5 lines:")
    for line in lines[:5]:
        print(f"    {repr(line[:120])}")
    print()

    for i, line in enumerate(lines):
        line = line.strip()

        # Skip empty lines and header/footer lines
        if not line:
            skipped += 1
            continue
        if not line.startswith("|"):
            skipped += 1
            continue

        # Split on pipe — remove empty first/last elements
        parts = [p.strip() for p in line.split("|")]
        # Remove leading/trailing empty strings from outer pipes
        if parts and parts[0] == "":
            parts = parts[1:]
        if parts and parts[-1] == "":
            parts = parts[:-1]

        if len(parts) < 25:
            skipped += 1
            continue

        try:
            callsign     = parts[0]
            freq_raw     = parts[1]
            service_code = parts[2]
            city         = parts[9]
            state        = parts[10]
            country      = parts[11]
            facility_id  = parts[12]
            power_raw    = parts[13]

            # Coordinates — DMS
            lat_dir = parts[18]
            lat_deg = parts[19]
            lat_min = parts[20]
            lat_sec = parts[21]
            lon_dir = parts[22]
            lon_deg = parts[23]
            lon_min = parts[24]
            lon_sec = parts[25] if len(parts) > 25 else "0"

            # Skip non-AM service codes
            if service_code.strip().upper() not in ("AM", "AX", ""):
                skipped += 1
                continue

            freq_khz = parse_freq_khz(freq_raw)
            erp_kw   = parse_power_kw(power_raw)
            lat      = dms_to_decimal(lat_deg, lat_min,
                                      lat_sec, lat_dir)
            lon      = dms_to_decimal(lon_deg, lon_min,
                                      lon_sec, lon_dir)

            rows.append({
                "facility_id":   facility_id.strip(),
                "callsign":      callsign.strip(),
                "frequency_khz": freq_khz,
                "lat":           lat,
                "lon":           lon,
                "state":         state.strip().upper(),
                "country":       country.strip().upper(),
                "city":          city.strip(),
                "erp_kw":        erp_kw if erp_kw else 1.0,
                "service_code":  service_code.strip().upper(),
            })

        except (IndexError, ValueError) as e:
            parse_errors += 1
            if parse_errors <= 3:
                print(f"  Parse error on line {i}: {e}")
                print(f"    Parts ({len(parts)}): {parts[:10]}")

    print(f"  Rows parsed:    {len(rows):,}")
    print(f"  Lines skipped:  {skipped:,}")
    print(f"  Parse errors:   {parse_errors:,}")
    return rows


# ── CLEAN AND FILTER ──────────────────────────────────────────

def clean(rows):
    df = pd.DataFrame(rows)
    print(f"\n  Input rows: {len(df):,}")

    # Frequency filter
    before = len(df)
    df = df[df["frequency_khz"].between(AM_FREQ_MIN, AM_FREQ_MAX)]
    print(f"  After frequency filter "
          f"({AM_FREQ_MIN}-{AM_FREQ_MAX} kHz): "
          f"{len(df):,} (removed {before - len(df):,})")

    # Drop missing coordinates
    before = len(df)
    df = df.dropna(subset=["lat", "lon"])
    print(f"  After coordinate filter: "
          f"{len(df):,} (removed {before - len(df):,})")

    # Coordinate sanity
    before = len(df)
    df = df[df["lat"].between(-90, 90) &
            df["lon"].between(-180, 180)]
    print(f"  After bounds check: "
          f"{len(df):,} (removed {before - len(df):,})")

    # Deduplicate on facility_id
    before = len(df)
    df = df.drop_duplicates(subset=["facility_id"])
    print(f"  After dedup (facility_id): "
          f"{len(df):,} (removed {before - len(df):,})")

    return df.reset_index(drop=True)


# ── MAIN ──────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("BUILD AM STATION TABLE")
    print("OC-OBS-002 — OrganismCore")
    print("=" * 60)
    print()

    if not os.path.exists(INPUT_FILE):
        print(f"ERROR: {INPUT_FILE} not found.")
        print(f"Place the FCC AM Query List export in this "
              f"directory as '{INPUT_FILE}' and re-run.")
        sys.exit(1)

    print(f"Reading: {INPUT_FILE}")
    rows = parse_fcc_query_file(INPUT_FILE)

    if not rows:
        print("ERROR: No rows parsed. Check file format.")
        sys.exit(1)

    print("\nCleaning...")
    df = clean(rows)

    df.to_csv(OUTPUT_FILE, index=False)

    print()
    print("=" * 60)
    print("FINAL AM STATION TABLE")
    print("=" * 60)
    print(f"  Total stations:   {len(df):,}")
    print(f"  US stations:      "
          f"{(df['country'] == 'US').sum():,}")
    print(f"  CA stations:      "
          f"{(df['country'] == 'CA').sum():,}")
    print(f"  Frequency range:  "
          f"{df['frequency_khz'].min():.0f}–"
          f"{df['frequency_khz'].max():.0f} kHz")
    print(f"  Lat range:        "
          f"{df['lat'].min():.2f}° – {df['lat'].max():.2f}°")
    print(f"  Lon range:        "
          f"{df['lon'].min():.2f}° – {df['lon'].max():.2f}°")
    print(f"  ERP range:        "
          f"{df['erp_kw'].min():.3f}–"
          f"{df['erp_kw'].max():.3f} kW")
    print()
    print(f"Saved: {OUTPUT_FILE}")
    print(f"Size:  {os.path.getsize(OUTPUT_FILE)/1024:.1f} KB")
    print()
    print("am_stations_clean.csv is ready.")


if __name__ == "__main__":
    main()
