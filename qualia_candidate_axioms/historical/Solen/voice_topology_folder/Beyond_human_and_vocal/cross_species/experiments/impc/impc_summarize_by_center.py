"""
IMPC OPEN FIELD — SUMMARY BY CENTER
Standalone fix script.

Reads impc_open_field_raw.csv
(already downloaded — 851,255 rows)
and produces the center-level
summary statistics.

Fixes the KeyError: 'biological_sample_id'
by using .get() style column access
with graceful fallback for any field
that may not have been returned by
the API for all rows.

Outputs:
  impc_open_field_by_center.csv
  impc_open_field_by_center_readable.txt
"""

import pandas as pd
import numpy as np

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────

RAW_CSV    = "impc_open_field_raw.csv"
OUT_CSV    = "impc_open_field_by_center.csv"
OUT_TXT    = "impc_open_field_by_center_readable.txt"

# Known parameter IDs → labels
KNOWN_PARAMS = {
    "IMPC_OFD_001_001":
        "distance_traveled_total",
    "IMPC_OFD_002_001":
        "velocity_average",
    "IMPC_OFD_003_001":
        "time_mobile",
    "IMPC_OFD_004_001":
        "time_immobile",
    "IMPC_OFD_008_001":
        "center_entries",
    "IMPC_OFD_009_001":
        "time_in_center",
    "IMPC_OFD_010_001":
        "time_in_periphery_thigmotaxis",
    "IMPC_OFD_011_001":
        "distance_in_center",
    "IMPC_OFD_012_001":
        "distance_in_periphery",
    "IMPC_OFD_013_001":
        "rearing_count",
    "IMPC_OFD_020_001":
        "distance_first_5min",
    "IMPC_OFD_021_001":
        "distance_last_5min",
}

FACILITY_META = {
    'JAX': {
        'address':
            '600 Main St, Bar Harbor, ME',
        'country': 'USA',
        'city': 'Bar Harbor',
        'urban_class': 'rural',
        'elf_prior': 'LOW',
        'lat': 44.388,
        'lon': -68.204,
    },
    'TCP': {
        'address':
            '25 Orde St, Toronto, ON',
        'country': 'Canada',
        'city': 'Toronto',
        'urban_class': 'urban_downtown',
        'elf_prior': 'HIGH',
        'lat': 43.659,
        'lon': -79.386,
    },
    'UCD': {
        'address':
            '279 Cousteau Pl, Davis, CA',
        'country': 'USA',
        'city': 'Davis',
        'urban_class': 'suburban',
        'elf_prior': 'MEDIUM',
        'lat': 38.545,
        'lon': -121.766,
    },
    'WSI': {
        'address':
            'Genome Campus, Hinxton, UK',
        'country': 'UK',
        'city': 'Hinxton',
        'urban_class': 'rural_campus',
        'elf_prior': 'LOW',
        'lat': 52.082,
        'lon': 0.186,
    },
    'HMGU': {
        'address':
            'Ingolstädter Landstr 1, '
            'Munich, DE',
        'country': 'Germany',
        'city': 'Munich',
        'urban_class': 'urban_fringe',
        'elf_prior': 'MEDIUM_HIGH',
        'lat': 48.220,
        'lon': 11.589,
    },
    'MRC Harwell': {
        'address':
            'Harwell Campus, Didcot, UK',
        'country': 'UK',
        'city': 'Didcot',
        'urban_class': 'science_campus',
        'elf_prior': 'MEDIUM',
        'lat': 51.575,
        'lon': -1.309,
    },
    'RBRC': {
        'address':
            '3-1-1 Koyadai, Tsukuba, JP',
        'country': 'Japan',
        'city': 'Tsukuba',
        'urban_class': 'science_city',
        'elf_prior': 'MEDIUM_HIGH',
        'lat': 36.105,
        'lon': 140.098,
    },
    'ICS': {
        'address':
            'Illkirch-Graffenstaden, FR',
        'country': 'France',
        'city': 'Illkirch',
        'urban_class': 'suburban',
        'elf_prior': 'MEDIUM',
        'lat': 48.534,
        'lon': 7.723,
    },
    'CNIO': {
        'address':
            'Melchor Fernández Almagro 3,'
            ' Madrid, ES',
        'country': 'Spain',
        'city': 'Madrid',
        'urban_class': 'urban',
        'elf_prior': 'HIGH',
        'lat': 40.468,
        'lon': -3.690,
    },
    'BCM': {
        'address':
            'One Baylor Plaza, Houston, TX',
        'country': 'USA',
        'city': 'Houston',
        'urban_class': 'urban_medical',
        'elf_prior': 'HIGH',
        'lat': 29.710,
        'lon': -95.396,
    },
    'Monterotondo': {
        'address':
            'Via Ramarini 32, '
            'Monterotondo, IT',
        'country': 'Italy',
        'city': 'Monterotondo',
        'urban_class': 'suburban_rome',
        'elf_prior': 'MEDIUM',
        'lat': 42.053,
        'lon': 12.616,
    },
    'MARC': {
        'address':
            'Nanjing, Jiangsu, CN',
        'country': 'China',
        'city': 'Nanjing',
        'urban_class': 'urban',
        'elf_prior': 'HIGH',
        'lat': 32.060,
        'lon': 118.796,
    },
    'Harwell': {
        'address':
            'Harwell Campus, Didcot, UK',
        'country': 'UK',
        'city': 'Didcot',
        'urban_class': 'science_campus',
        'elf_prior': 'MEDIUM',
        'lat': 51.575,
        'lon': -1.309,
    },
    'WTSI': {
        'address':
            'Genome Campus, Hinxton, UK',
        'country': 'UK',
        'city': 'Hinxton',
        'urban_class': 'rural_campus',
        'elf_prior': 'LOW',
        'lat': 52.082,
        'lon': 0.186,
    },
    'Sanger Institute': {
        'address':
            'Genome Campus, Hinxton, UK',
        'country': 'UK',
        'city': 'Hinxton',
        'urban_class': 'rural_campus',
        'elf_prior': 'LOW',
        'lat': 52.082,
        'lon': 0.186,
    },
    'Institut Clinique de la Souris': {
        'address':
            'Illkirch-Graffenstaden, FR',
        'country': 'France',
        'city': 'Illkirch',
        'urban_class': 'suburban',
        'elf_prior': 'MEDIUM',
        'lat': 48.534,
        'lon': 7.723,
    },
    'UC Davis': {
        'address':
            '279 Cousteau Pl, Davis, CA',
        'country': 'USA',
        'city': 'Davis',
        'urban_class': 'suburban',
        'elf_prior': 'MEDIUM',
        'lat': 38.545,
        'lon': -121.766,
    },
    'University of Toronto Centre'
    ' for Phenogenomics': {
        'address':
            '25 Orde St, Toronto, ON',
        'country': 'Canada',
        'city': 'Toronto',
        'urban_class': 'urban_downtown',
        'elf_prior': 'HIGH',
        'lat': 43.659,
        'lon': -79.386,
    },
}


# ─────────────────────────────────────────
# LOAD
# ─────────────────────────────────────────

print("=" * 52)
print("IMPC OPEN FIELD — CENTER SUMMARY")
print("=" * 52)
print()
print(f"Loading {RAW_CSV}...")

df = pd.read_csv(
    RAW_CSV,
    low_memory=False
)
print(f"  Rows loaded: {len(df):,}")
print()

# ── Audit what columns actually exist ──
print("Columns in raw file:")
for col in sorted(df.columns.tolist()):
    n_null = df[col].isna().sum()
    pct    = 100 * n_null / len(df)
    print(
        f"  {col:<45} "
        f"null: {n_null:>8,} "
        f"({pct:5.1f}%)"
    )
print()


# ─────────────────────────────────────���───
# IDENTIFY THE ANIMAL ID COLUMN
# ─────────────────────────────────────────

# Try in order of preference
ANIMAL_ID_CANDIDATES = [
    'biological_sample_id',
    'external_sample_id',
    'specimen_id',
    'specimenId',
    'mouse_id',
    'animal_id',
]

animal_id_col = None
for candidate in ANIMAL_ID_CANDIDATES:
    if candidate in df.columns:
        animal_id_col = candidate
        print(
            f"Animal ID column found: "
            f"'{animal_id_col}'"
        )
        break

if animal_id_col is None:
    print(
        "WARNING: No animal ID column "
        "found. N_unique_animals will "
        "be reported as N/A."
    )
print()


# ─────────────────────────────────────────
# COERCE data_point TO NUMERIC
# ─────────────────────────────────────────

df['data_point_num'] = pd.to_numeric(
    df['data_point'],
    errors='coerce'
)

df_numeric = df[
    df['data_point_num'].notna()
].copy()

print(
    f"Numeric observations: "
    f"{len(df_numeric):,} / {len(df):,}"
)
print()


# ─────────────────────────────────────────
# IDENTIFY WHICH PARAMS ARE PRESENT
# ────────────���────────────────────────────

print("Parameters present in data:")
present_params = {}

if 'parameter_stable_id' in df.columns:
    obs_param_counts = (
        df_numeric['parameter_stable_id']
        .value_counts()
    )
    for pid, label in KNOWN_PARAMS.items():
        if pid in obs_param_counts.index:
            n = obs_param_counts[pid]
            present_params[pid] = label
            print(
                f"  {pid:<30} "
                f"{n:>10,}  {label}"
            )

    # Also report any unknown params
    for pid in obs_param_counts.index:
        if pid not in KNOWN_PARAMS:
            n = obs_param_counts[pid]
            if n >= 100:
                print(
                    f"  {pid:<30} "
                    f"{n:>10,}  "
                    f"(unknown — will include)"
                )
                present_params[pid] = pid
else:
    print(
        "  WARNING: 'parameter_stable_id'"
        " column not found."
    )
    present_params = KNOWN_PARAMS

print()


# ─────────────────────────────────────────
# SUMMARY BY CENTER
# ─────────────────────────────────────────

print("Computing per-center statistics...")
print()

# Get center column name
center_col_name = 'phenotyping_center'
if center_col_name not in df.columns:
    # Try alternatives
    for alt in [
        'center', 'centre',
        'phenotypingCenter',
        'phenotyping_centre'
    ]:
        if alt in df.columns:
            center_col_name = alt
            break

centers = sorted(
    df_numeric[center_col_name].dropna()
    .unique().tolist()
)
print(f"Centers found: {len(centers)}")
for c in centers:
    print(f"  '{c}'")
print()

summary_rows = []

for center in centers:
    cdf = df_numeric[
        df_numeric[center_col_name] == center
    ].copy()

    meta = {}
    # Try exact match first,
    # then substring match
    if center in FACILITY_META:
        meta = FACILITY_META[center]
    else:
        for key in FACILITY_META:
            if (key.lower() in center.lower()
                    or center.lower()
                    in key.lower()):
                meta = FACILITY_META[key]
                break

    row = {
        'phenotyping_center': center,
        'n_observations': len(cdf),
        'n_unique_animals': (
            cdf[animal_id_col].nunique()
            if animal_id_col
            else None
        ),
        'address':
            meta.get('address', 'UNKNOWN'),
        'city':
            meta.get('city', 'UNKNOWN'),
        'country':
            meta.get('country', 'UNKNOWN'),
        'urban_class':
            meta.get('urban_class', 'UNKNOWN'),
        'elf_prior':
            meta.get('elf_prior', 'UNKNOWN'),
        'lat': meta.get('lat', None),
        'lon': meta.get('lon', None),
    }

    # Per-parameter stats
    for pid, plabel in present_params.items():
        pdata = cdf[
            cdf['parameter_stable_id'] == pid
        ]['data_point_num'].dropna()

        safe = (
            plabel
            .replace(' ', '_')
            .replace('(', '')
            .replace(')', '')
            .replace('/', '_')
            [:35]
        )

        if len(pdata) >= 5:
            row[f'{safe}__n']      = len(pdata)
            row[f'{safe}__mean']   = float(
                pdata.mean()
            )
            row[f'{safe}__median'] = float(
                pdata.median()
            )
            row[f'{safe}__sd']     = float(
                pdata.std()
            )
            row[f'{safe}__sem']    = float(
                pdata.std()
                / np.sqrt(len(pdata))
            )
            row[f'{safe}__q25']    = float(
                pdata.quantile(0.25)
            )
            row[f'{safe}__q75']    = float(
                pdata.quantile(0.75)
            )
        else:
            for suffix in [
                '__n', '__mean', '__median',
                '__sd', '__sem',
                '__q25', '__q75'
            ]:
                row[f'{safe}{suffix}'] = None

    # Sex breakdown
    if 'sex' in cdf.columns:
        sex_vc = cdf['sex'].value_counts()
        row['n_male']   = int(
            sex_vc.get('male', 0)
        )
        row['n_female'] = int(
            sex_vc.get('female', 0)
        )
    else:
        row['n_male']   = None
        row['n_female'] = None

    # Zygosity breakdown
    if 'zygosity' in cdf.columns:
        zyg_vc = cdf['zygosity'].value_counts()
        row['n_homozygote']   = int(
            zyg_vc.get('homozygote', 0)
        )
        row['n_heterozygote'] = int(
            zyg_vc.get('heterozygote', 0)
        )
        row['n_wildtype']     = int(
            zyg_vc.get('wild type', 0)
        )
    else:
        row['n_homozygote']   = None
        row['n_heterozygote'] = None
        row['n_wildtype']     = None

    # Strain count
    if 'strain_name' in cdf.columns:
        row['n_strains'] = int(
            cdf['strain_name'].nunique()
        )
    else:
        row['n_strains'] = None

    summary_rows.append(row)
    print(
        f"  {center:<40} "
        f"n={len(cdf):>8,}"
    )

summary_df = pd.DataFrame(summary_rows)
summary_df = summary_df.sort_values(
    'n_observations',
    ascending=False
).reset_index(drop=True)

summary_df.to_csv(OUT_CSV, index=False)
print()
print(f"Saved → {OUT_CSV}")
print()


# ─────────────────────────────────────────
# READABLE REPORT
# ─────────────────────────────────────────

lines = []

def log(s=""):
    lines.append(s)
    print(s)

log("=" * 68)
log("IMPC OPEN FIELD TEST — FACILITY SUMMARY")
log(f"N facilities: {len(summary_df)}")
log(f"N total observations: "
    f"{summary_df['n_observations'].sum():,}")
log("=" * 68)
log()

# Find key behavioral columns
def find_col(df, fragments):
    """Find first column containing
    all fragments (case insensitive)."""
    for col in df.columns:
        if all(
            f.lower() in col.lower()
            for f in fragments
        ):
            return col
    return None

loco_col   = find_col(
    summary_df,
    ['distance_traveled_total', 'mean']
)
thigmo_col = find_col(
    summary_df,
    ['periphery', 'mean']
)
center_tc  = find_col(
    summary_df,
    ['time_in_center', 'mean']
)
velocity_c = find_col(
    summary_df,
    ['velocity', 'mean']
)
rearing_c  = find_col(
    summary_df,
    ['rearing', 'mean']
)

log(
    f"{'Facility':<35} "
    f"{'N_obs':>8} "
    f"{'ELF':>8} "
    + (f"{'Loco':>9} " if loco_col else "")
    + (f"{'Thigmo':>9} " if thigmo_col else "")
    + (f"{'CtrTime':>9} " if center_tc else "")
    + (f"{'Veloc':>8} " if velocity_c else "")
    + (f"{'Rear':>7}" if rearing_c else "")
)
log("-" * 90)

for _, row in summary_df.iterrows():
    line = (
        f"{str(row['phenotyping_center']):<35}"
        f"{int(row['n_observations']):>8,}"
        f"{str(row.get('elf_prior','?')):>8}"
    )
    for col, width in [
        (loco_col, 9),
        (thigmo_col, 9),
        (center_tc, 9),
        (velocity_c, 8),
        (rearing_c, 7),
    ]:
        if col:
            val = row.get(col)
            if pd.notna(val) and val is not None:
                line += f"{val:>{width}.2f} "
            else:
                line += f"{'—':>{width}} "
    log(line)

log()
log("Column guide:")
log(
    f"  Loco   = mean total distance "
    f"traveled (cm)")
log(
    f"  Thigmo = mean time in periphery "
    f"(s) — thigmotaxis proxy")
log(
    f"  CtrTime = mean time in center "
    f"zone (s)")
log(
    f"  Veloc  = mean velocity (cm/s)")
log(
    f"  Rear   = mean rearing count")
log()
log("ELF prior codes:")
log("  LOW          — rural, isolated")
log("  MEDIUM       — suburban/campus")
log("  MEDIUM_HIGH  — urban fringe/"
    "science city")
log("  HIGH         — urban downtown/"
    "medical center")
log("  UNKNOWN      — not yet mapped")
log()
log("NOTE: ELF_prior is qualitative.")
log("Quantitative estimation follows")
log("in impc_elf_estimation.py using")
log("power line proximity, building")
log("era, and equipment density.")
log()
log("=" * 68)
log("FILES SAVED:")
log(f"  {OUT_CSV}")
log(f"  {OUT_TXT}")
log()
log("NEXT STEP:")
log("  Run impc_elf_estimation.py")
log("  to assign quantitative ELF")
log("  estimates to each facility,")
log("  then correlate against the")
log("  behavioral means above.")
log("=" * 68)

with open(OUT_TXT, "w") as f:
    f.write("\n".join(lines))
print()
print(f"Saved → {OUT_TXT}")
