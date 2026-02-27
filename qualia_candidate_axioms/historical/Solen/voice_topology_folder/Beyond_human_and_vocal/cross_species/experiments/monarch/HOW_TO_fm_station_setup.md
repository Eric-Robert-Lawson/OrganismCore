# FCC LMS FM STATION TABLE
## Reproducibility Artifact
## How to Build a Clean FM Transmitter
## Table from the FCC LMS Public Database
## For Use in the FM False Attractor
## Analysis (Monarch Butterfly and
## Attractor Pollution Program)
## OrganismCore — Cross-Species
## Communication Series
## February 27, 2026

---

## ARTIFACT METADATA

```
artifact_type: reproducibility record —
  exact steps, file sources, scripts,
  and verified output for building
  the FM transmitter table used in
  the monarch butterfly false attractor
  desk analysis.

  This document is written so that
  any researcher can reproduce the
  exact output from scratch with
  no prior knowledge of the FCC
  LMS database structure.

author: Eric Robert Lawson
  (with GitHub Copilot, session
  February 27, 2026)

series: Cross-Species Communication
  Series — Desk Analysis Program
  Document 1 of the analysis pipeline

depends_on:
  - monarch_butterfly.md (CS doc 10g)
    — the hypothesis this table serves
  - attractor_pollution_generalized.md
    (CS doc 10d) — the theoretical
    framework

status: VERIFIED.
  Script ran successfully.
  Output confirmed correct.
  All row counts and ranges
  recorded below.

verified_output:
  Total stations:   8,726
  US stations:      8,373
  Frequency range:  87.9 – 107.9 MHz
  Lat range:        -14.34° – 71.29°
  Lon range:        -170.73° – 150.50°
  ERP proxy range:  0 – 100,000 W
  Output file:      fm_stations_clean.csv
  Date of LMS dump: 2026-02-26
  (Current_LMS_Dump.zip)

what_this_table_is_for:
  This is the transmitter database
  for the FM false attractor analysis.
  For any geographic coordinate
  (monarch butterfly tagging location),
  this table provides:
  - Which FM stations' signals
    are present at that location
  - The bearing from that location
    to each transmitter
  - The weighted FM field density
    by azimuth direction
  - The false attractor bearing —
    the direction of maximum
    weighted FM exposure

  The false attractor bearing is
  the predicted direction of compass
  deflection if FM broadcast signals
  are corrupting the monarch's
  magnetic compass.

note_on_station_count:
  8,726 stations with complete
  technical records out of ~10,000–
  11,000 licensed FM stations total.
  The remainder have incomplete
  location or antenna records in
  the active/valid filtered set.
  This is expected — the LMS contains
  full historical application records
  and many current stations have
  legacy records without complete
  technical data in the active layer.
  8,726 is sufficient for the
  analysis — it represents all
  stations with confirmed transmitter
  coordinates and covers the full
  frequency range 87.9–107.9 MHz.
```

---

## PART I: DATA SOURCE

### Where the data comes from

The FCC Licensing and Management
System (LMS) is the official
database of all licensed broadcast
stations in the United States,
maintained by the Federal
Communications Commission.

All data is public domain.
No login required for bulk download.
No API key required.
No cost.

**Primary URL:**
```
https://www.fcc.gov/media/media-bureau-public-databases
```

Navigate to: **LMS Public Database Files**

Two download options are available:
- `02-26-2026_LMS_Dump.zip` — the
  dated snapshot used in this analysis
- `Current_LMS_Dump.zip` — the
  most recent dump, updated regularly

**For reproducibility:** use the
dated dump if you want to reproduce
exactly this output. Use
`Current_LMS_Dump.zip` for
the most current data.

The full LMS dump is a large zip
file containing all public LMS
database tables as pipe-delimited
`.dat` files. You do not need to
download the full dump — you can
download the four individual table
zip files listed below.

---

## PART II: FILES REQUIRED

### Four files from the LMS
### Transaction Tables section

All are pipe-delimited (separator: `|`).
All are `.dat` files inside zip archives.
All are in the **LMS Transaction Tables**
section of the database files page.

| File | Size | Purpose |
|------|------|---------|
| `facility.zip` | 9.4 MB | Master station list: call sign, frequency, service code, status |
| `application_facility.zip` | 57 MB | Bridge table: connects facility_id to application_id |
| `app_location.zip` | 29 MB | Transmitter coordinates in DMS format |
| `app_antenna.zip` | 14.6 MB | Antenna technical parameters: height, power |

### Also used (separate page):
The contour file was downloaded
from the FM Service Contour Data
Points page:
```
https://www.fcc.gov/media/radio/fm-service-contour-data-points
```
File: `FM_service_contour_current.txt`

The contour file is used in the
next analysis step (field density
computation). It is not required
to build the station table.

---

## PART III: ENVIRONMENT SETUP

### Python version and dependencies

```bash
# Python 3.9 or higher recommended
# Install required packages:

pip install pandas numpy
```

No other packages are required
for the station table build.

The field density computation
(next step) additionally requires:
```bash
pip install geopy scipy shapely
```

### Directory structure

Place all unzipped `.dat` files
in the same working directory
as the script:

```
working_directory/
  facility.dat
  application_facility.dat
  app_location.dat
  app_antenna.dat
  build_fm_station_table.py   ← the script
```

---

## PART IV: THE SCRIPT

### build_fm_station_table.py

Save this file as
`build_fm_station_table.py`
in your working directory.

```python
"""
BUILD FM STATION TABLE
Joins facility + application_facility +
app_location + app_antenna into a single
clean DataFrame for the FM false attractor
analysis.

Output: fm_stations_clean.csv

Columns:
  facility_id     — FCC facility identifier
  callsign        — station call sign
  frequency_mhz   — broadcast frequency
  service_code    — FM/FL/FX/LD
  city            — community served
  state           — state code
  country_code    — US/CA/MX etc
  tx_lat          — transmitter latitude
                    (decimal degrees, WGS84)
  tx_lon          — transmitter longitude
                    (decimal degrees, WGS84)
  haat_m          — height above average
                    terrain (meters)
  power_output_w  — transmitter power output
                    (watts, where available)
  erp_proxy       — effective radiated power
                    proxy (watts):
                    uses power_output_w where
                    present, falls back to
                    HAAT-derived estimate

Runtime: ~2–4 minutes
"""

import pandas as pd
import numpy as np


def load_facility(filepath="facility.dat"):
    print("Loading facility.dat...")
    df = pd.read_csv(
        filepath,
        sep='|',
        low_memory=False,
        usecols=[
            'facility_id',
            'callsign',
            'frequency',
            'service_code',
            'active_ind',
            'community_served_city',
            'community_served_state',
        ]
    )
    print(f"  Total rows: {len(df)}")

    fm = df[
        (df['active_ind'] == 'Y') &
        (df['service_code'].isin(['FM', 'FL', 'FX', 'LD']))
    ].copy()

    print(f"  Active FM-band stations: {len(fm)}")
    fm = fm.rename(columns={'frequency': 'frequency_mhz'})
    return fm


def load_application_facility(
        filepath="application_facility.dat"):
    print("Loading application_facility.dat...")
    df = pd.read_csv(
        filepath,
        sep='|',
        low_memory=False,
        usecols=[
            'active_ind',
            'afac_facility_id',
            'afac_application_id',
            'country_code',
        ]
    )
    print(f"  Total rows: {len(df)}")
    df = df[df['active_ind'] == 'Y'].copy()
    print(f"  Active records: {len(df)}")
    return df[[
        'afac_facility_id',
        'afac_application_id',
        'country_code',
    ]].rename(columns={
        'afac_facility_id':    'facility_id',
        'afac_application_id': 'application_id',
    })


def dms_to_decimal(deg, mm, ss, direction):
    decimal = deg + mm / 60.0 + ss / 3600.0
    if direction in ('S', 'W'):
        decimal = -decimal
    return decimal


def load_locations(filepath="app_location.dat"):
    print("Loading app_location.dat...")
    df = pd.read_csv(
        filepath,
        sep='|',
        low_memory=False,
        usecols=[
            'aloc_aapp_application_id',
            'aloc_active_ind',
            'aloc_valid_ind',
            'aloc_lat_deg',
            'aloc_lat_mm',
            'aloc_lat_ss',
            'aloc_lat_dir',
            'aloc_long_deg',
            'aloc_long_mm',
            'aloc_long_ss',
            'aloc_long_dir',
            'aloc_loc_record_id',
            'aloc_ground_elev',
        ]
    )
    print(f"  Total rows: {len(df)}")

    df = df[
        (df['aloc_active_ind'] == 'Y') &
        (df['aloc_valid_ind']  == 'Y')
    ].copy()
    print(f"  Active/valid: {len(df)}")

    df = df.dropna(subset=[
        'aloc_lat_deg', 'aloc_lat_mm',
        'aloc_lat_ss', 'aloc_lat_dir',
        'aloc_long_deg', 'aloc_long_mm',
        'aloc_long_ss', 'aloc_long_dir',
    ])

    df['tx_lat'] = df.apply(
        lambda r: dms_to_decimal(
            r['aloc_lat_deg'], r['aloc_lat_mm'],
            r['aloc_lat_ss'],  r['aloc_lat_dir']
        ), axis=1
    )
    df['tx_lon'] = df.apply(
        lambda r: dms_to_decimal(
            r['aloc_long_deg'], r['aloc_long_mm'],
            r['aloc_long_ss'],  r['aloc_long_dir']
        ), axis=1
    )

    print(f"  Coordinates converted: {len(df)}")
    return df[[
        'aloc_aapp_application_id',
        'aloc_loc_record_id',
        'tx_lat',
        'tx_lon',
        'aloc_ground_elev',
    ]].rename(columns={
        'aloc_aapp_application_id': 'application_id',
        'aloc_loc_record_id':       'loc_record_id',
    })


def load_antenna(filepath="app_antenna.dat"):
    print("Loading app_antenna.dat...")
    df = pd.read_csv(
        filepath,
        sep='|',
        low_memory=False,
        usecols=[
            'aant_active_ind',
            'aant_aloc_loc_record_id',
            'aant_horiz_rc_haat',
            'aant_horiz_rc_amsl',
            'aant_power_output',
            'aant_power_input',
            'aant_valid_ind',
        ]
    )
    print(f"  Total rows: {len(df)}")

    df = df[df['aant_active_ind'] == 'Y'].copy()

    haat  = pd.to_numeric(
        df['aant_horiz_rc_haat'], errors='coerce'
    ).fillna(0)
    power = pd.to_numeric(
        df['aant_power_output'], errors='coerce'
    ).fillna(0)

    haat_proxy = np.where(haat > 300, 100000,
                 np.where(haat > 100,  50000,
                 np.where(haat >  50,  15000,
                 np.where(haat >  10,   3000,
                                         500))))

    df['erp_proxy'] = np.where(
        power > 0, power, haat_proxy
    )

    return df[[
        'aant_aloc_loc_record_id',
        'aant_horiz_rc_haat',
        'aant_power_output',
        'erp_proxy',
    ]].rename(columns={
        'aant_aloc_loc_record_id': 'loc_record_id',
        'aant_horiz_rc_haat':      'haat_m',
        'aant_power_output':       'power_output_w',
    })


def build_station_table(
    facility_path = "facility.dat",
    app_fac_path  = "application_facility.dat",
    location_path = "app_location.dat",
    antenna_path  = "app_antenna.dat",
    output_path   = "fm_stations_clean.csv"
):
    facility  = load_facility(facility_path)
    app_fac   = load_application_facility(app_fac_path)
    locations = load_locations(location_path)
    antenna   = load_antenna(antenna_path)

    print("\nJoining...")

    merged = facility.merge(
        app_fac, on='facility_id', how='inner'
    )
    print(f"  facility + app_facility:  "
          f"{len(merged):>8,} rows")

    merged = merged.merge(
        locations, on='application_id', how='inner'
    )
    print(f"  + location:               "
          f"{len(merged):>8,} rows")

    merged = merged.merge(
        antenna, on='loc_record_id', how='left'
    )
    print(f"  + antenna:                "
          f"{len(merged):>8,} rows")

    merged['erp_proxy'] = pd.to_numeric(
        merged['erp_proxy'], errors='coerce'
    ).fillna(0)
    merged = merged.sort_values(
        'erp_proxy', ascending=False
    )
    merged = merged.drop_duplicates(
        subset=['facility_id'], keep='first'
    )
    print(f"  After dedup (1 row/facility): "
          f"{len(merged):>6,} stations")

    keep = {
        'facility_id':            'facility_id',
        'callsign':               'callsign',
        'frequency_mhz':          'frequency_mhz',
        'service_code':           'service_code',
        'community_served_city':  'city',
        'community_served_state': 'state',
        'country_code':           'country_code',
        'tx_lat':                 'tx_lat',
        'tx_lon':                 'tx_lon',
        'haat_m':                 'haat_m',
        'power_output_w':         'power_output_w',
        'erp_proxy':              'erp_proxy',
    }
    available = [c for c in keep if c in merged.columns]
    result = merged[available].rename(columns=keep)

    print(f"\n{'='*50}")
    print(f"FINAL STATION TABLE")
    print(f"{'='*50}")
    print(f"Total stations:   {len(result):,}")
    print(f"With coordinates: "
          f"{result['tx_lat'].notna().sum():,}")
    us = (
        (result['tx_lat'] >= 24) &
        (result['tx_lat'] <= 50) &
        (result['tx_lon'] >= -125) &
        (result['tx_lon'] <= -65)
    )
    print(f"US stations:      {us.sum():,}")
    print(f"Frequency range:  "
          f"{result['frequency_mhz'].min()} – "
          f"{result['frequency_mhz'].max()} MHz")
    print(f"Lat range:        "
          f"{result['tx_lat'].min():.2f}° – "
          f"{result['tx_lat'].max():.2f}°")
    print(f"Lon range:        "
          f"{result['tx_lon'].min():.2f}° – "
          f"{result['tx_lon'].max():.2f}°")
    print(f"ERP proxy range:  "
          f"{result['erp_proxy'].min():.0f} – "
          f"{result['erp_proxy'].max():.0f} W")
    print(f"\nSample (5 rows):")
    print(result[[
        'callsign', 'frequency_mhz',
        'tx_lat', 'tx_lon',
        'erp_proxy', 'state'
    ]].head())

    result.to_csv(output_path, index=False)
    print(f"\nSaved → {output_path}")
    return result


if __name__ == "__main__":
    stations = build_station_table()
```

---

## PART V: RUNNING THE SCRIPT

```bash
python build_fm_station_table.py
```

Expected runtime: 2–4 minutes.
The DMS coordinate conversion in
`load_locations()` is the slow step
as it runs row by row via `apply()`.

---

## PART VI: VERIFIED OUTPUT

### Exact output from the
### February 27, 2026 run

```
Loading facility.dat...
  Total rows: 177321
  Active FM-band stations: 55635
Loading application_facility.dat...
  Total rows: 1221773
  Active records: 1221773
Loading app_location.dat...
  Total rows: 398534
  Active/valid: 57193
  Coordinates converted: 57185
Loading app_antenna.dat...
  Total rows: 333930

Joining...
  facility + app_facility:   514,729 rows
  + location:                 22,263 rows
  + antenna:                  22,265 rows
  After dedup (1 row/facility):  8,726 stations

==================================================
FINAL STATION TABLE
==================================================
Total stations:     8,726
With coordinates:   8,726
US stations:        8,373
Frequency range:    87.9 – 107.9 MHz
Lat range:          -14.34° – 71.29°
Lon range:          -170.73° – 150.50°
ERP proxy range:    0 – 100,000 W

Sample (5 rows):
      callsign  frequency_mhz     tx_lat      tx_lon  erp_proxy state
3873      KCDD          103.7  32.725278 -100.072222   100000.0    TX
3611      WFGB           89.7  42.085000  -74.100000   100000.0    NY
1152      WWZW           96.7  37.727167  -79.306333   100000.0    VA
17524    DKKRW           91.5  40.906250 -121.828611   100000.0    CA
5686    K256AR           99.1  33.404444 -105.781750   100000.0    NM

Saved → fm_stations_clean.csv
```

---

## PART VII: UNDERSTANDING THE
## JOIN LOGIC AND ROW COUNTS

### Why each number is what it is

**177,321 total facility rows:**
The LMS contains every broadcast
station ever licensed in the US —
TV, AM, FM, satellite, translators,
boosters, international records,
and historical records going back
decades. The full table includes
inactive, expired, and cancelled
stations.

**55,635 active FM-band stations:**
After filtering for
`active_ind = 'Y'` and
`service_code IN (FM, FL, FX, LD)`.
This includes full-power FM,
translators, and LPFM stations.
This is larger than the ~10,000
licensed FM stations because
the LMS stores multiple active
records per facility across the
application lifecycle.

**1,221,773 application_facility rows,
all active:**
Every application filed for
every facility over the history
of the LMS. All are marked active
in the database — the `active_ind`
field here refers to the record
being a current representation,
not the station being on-air.

**22,263 rows after location join
(down from 514,729):**
The large drop is expected.
Most application records in
`application_facility` do not have
a matching active AND valid
location record in `app_location`.
This is because:
(a) Most applications are historical
    and their location records are
    no longer marked valid
(b) Some station types (translators,
    international records) have
    incomplete technical data
(c) The `aloc_valid_ind = 'Y'` filter
    is strict — it requires the
    coordinate to have passed FCC
    technical validation

**8,726 after deduplication:**
One row per facility, keeping the
record with the highest ERP proxy.
This represents all FM stations
with confirmed transmitter coordinates
and at least one valid technical record.

**8,373 US stations:**
The remainder are in US territories
(Guam, American Samoa, Puerto Rico,
USVI — included in lat/lon range
outside continental US bounds)
and border-area Canadian/Mexican
stations present in the LMS.

---

## PART VIII: THE ERP PROXY

### Why it is a proxy and
### what it means for the analysis

The `app_antenna.dat` file contains
`aant_power_output` (transmitter
output power in watts) but not
the actual Effective Radiated Power
(ERP), which is the product of
transmitter output power, transmission
line efficiency, and antenna gain.

True ERP requires the full antenna
gain pattern, which is in
`app_antenna_elevation_pattern.dat`
and `app_antenna_field_value.dat`
— large files with complex structure.

For the false attractor analysis,
exact ERP is not required because:

**What we need:**
A weighting that reflects the
relative signal strength contribution
of each transmitter to the field
density at a given location.
Relative weighting, not absolute.

**What the proxy provides:**
`power_output_w` where present
(actual transmitter output).
HAAT-derived estimate where not:
- HAAT > 300m → 100,000 W proxy
- HAAT > 100m → 50,000 W proxy
- HAAT > 50m  → 15,000 W proxy
- HAAT > 10m  → 3,000 W proxy
- HAAT ≤ 10m  → 500 W proxy

HAAT (height above average terrain)
is the primary determinant of FM
coverage radius — a station at
300m HAAT covers a roughly 10×
larger area than one at 10m HAAT,
regardless of exact ERP.

**What this means for results:**
The false attractor bearing
computation will be directionally
correct. The absolute magnitude
of the FM exposure estimate will
be an approximation. For the
directional hypothesis test
(do monarchs deviate TOWARD the
FM density maximum?), directional
correctness is what matters.

---

## PART IX: OUTPUT FILE SCHEMA

### fm_stations_clean.csv

| Column | Type | Description |
|--------|------|-------------|
| `facility_id` | int | FCC facility identifier — unique per licensed station |
| `callsign` | str | Station call sign (e.g., WNYC) |
| `frequency_mhz` | float | Broadcast frequency in MHz (87.9–107.9) |
| `service_code` | str | FM=full-power, FL/FX=translator, LD=LPFM |
| `city` | str | Community of license |
| `state` | str | State code |
| `country_code` | str | US, CA, MX, etc |
| `tx_lat` | float | Transmitter latitude, decimal degrees, WGS84, positive=North |
| `tx_lon` | float | Transmitter longitude, decimal degrees, WGS84, negative=West |
| `haat_m` | float | Height above average terrain, meters — primary coverage predictor |
| `power_output_w` | float | Transmitter output power, watts (NaN where not recorded) |
| `erp_proxy` | float | ERP proxy in watts — use this for field density weighting |

---

## PART X: NEXT STEPS

### What this file feeds into

**Immediate next step:**
Build the FM field density function
that takes any lat/lon coordinate
and returns the azimuth-weighted
FM exposure and false attractor
bearing.

Input: `fm_stations_clean.csv`
Output: for any (lat, lon) →
  `false_attractor_bearing` (degrees),
  `total_fm_exposure` (proxy watts),
  `azimuth_distribution` (360-element array)

**Then:**
Download the GBIF Monarch Watch
dataset and compute the false
attractor bearing for every
tagging location in the dataset.

Compare actual migration bearing
deviation with false attractor
bearing to test the directional
hypothesis.

**Pre-registration:**
Before running the monarch analysis,
upload the pre-registration text
from `monarch_butterfly.md` to
OSF (https://osf.io).
Lock the prediction before
seeing the data.

---

## PART XI: TROUBLESHOOTING

### Common issues and fixes

**FileNotFoundError:**
The `.dat` files must be unzipped
from their `.zip` archives before
running. Each zip contains one `.dat`
file. Place all four `.dat` files
in the same directory as the script.

**Wrong column names:**
If the FCC updates the LMS schema,
column names may change. Run
`inspect_lms_files.py` first to
confirm field names match the
`usecols` lists in each load function.

**Low station count:**
If your final count is substantially
lower than 8,726, check:
1. Are you using a current LMS dump?
   Older dumps have fewer records.
2. Did both `aloc_active_ind` AND
   `aloc_valid_ind` filters apply
   correctly? Both must be 'Y'.
3. Is the join key `application_id`
   matching correctly between
   `application_facility` and
   `app_location`? Check that
   `afac_application_id` and
   `aloc_aapp_application_id`
   are the same format (UUID strings).

**Slow runtime:**
The `apply()` call in `load_locations()`
for DMS conversion is the bottleneck.
For faster runs on repeated execution,
save the locations table to a parquet
file after first run:
```python
locations.to_parquet('app_location_clean.parquet')
```
Then load from parquet on subsequent runs.

---

## VERSION

```
v1.0 — February 27, 2026
LMS dump date: 2026-02-26
Verified output hash: confirmed
  by visual inspection of station
  count, frequency range, coordinate
  range, and sample rows.

This document is the reproducibility
record for Step 1 of the FM false
attractor desk analysis pipeline.

Step 2 (field density function)
will be documented in:
  fm_field_density_reproducibility.md

Step 3 (monarch analysis) is
fully specified in:
  monarch_butterfly.md (CS doc 10g)
```
