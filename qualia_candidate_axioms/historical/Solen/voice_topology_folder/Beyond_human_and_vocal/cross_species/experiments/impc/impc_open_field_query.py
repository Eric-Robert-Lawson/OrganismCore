"""
IMPC SPATIAL NAVIGATION ANALYSIS
Analysis 3: Dark Archive Mouse Data
Step 1: Data Acquisition

Queries the IMPC SOLR API for Open Field
Test observations grouped by phenotyping
center. Extracts locomotion and thigmotaxis
data for all available centers in Data
Release 23 (April 2025).

Target parameters:
  IMPC_OFD_001 — Open Field procedure

  Primary parameters of interest:
    Distance traveled (locomotion)
    Time in center zone
    Time in periphery (thigmotaxis proxy)
    Velocity
    Rearing count

Output:
  impc_open_field_raw.csv
    — All individual observations
  impc_open_field_by_center.csv
    — Summary statistics per facility
  impc_open_field_parameters.csv
    — Full parameter list for OFD

Facility addresses (for ELF
estimation in subsequent step):
  TCP  — 25 Orde St, Toronto, ON
           (downtown — HIGH ELF)
  JAX  — 600 Main St, Bar Harbor, ME
           (rural — LOW ELF)
  UCD  — 279 Cousteau Pl, Davis, CA
           (suburban — MED ELF)
  WSI  — Hinxton, Cambridgeshire, UK
           (rural campus — LOW ELF)
  HMGU — Ingolstädter Landstr 1,
           Munich, DE
           (urban fringe — MED-HIGH ELF)
  MRC  — Harwell Campus, Didcot, UK
           (science campus — MED ELF)
  RBRC — Tsukuba, Ibaraki, JP
           (science city — MED-HIGH ELF)
  ICS  — Illkirch-Graffenstaden, FR
           (suburban Strasbourg — MED ELF)
  CNIO — Madrid, ES
           (urban — HIGH ELF)
  BCM  — Houston, TX, USA
           (urban medical center —
            HIGH ELF)

License: IMPC data CC BY 4.0.
All data publicly available.
No registration required.

Requirements:
  pip install requests pandas tqdm
"""

import requests
import pandas as pd
import json
import time
from tqdm import tqdm

# ─────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────

SOLR_BASE = (
    "https://www.ebi.ac.uk"
    "/mi/impc/solr/experiment/select"
)

PROCEDURE_ID = "IMPC_OFD_001"

# Fields to retrieve per observation
FIELDS = ",".join([
    "phenotyping_center",
    "phenotyping_center_id",
    "procedure_name",
    "procedure_stable_id",
    "parameter_name",
    "parameter_stable_id",
    "observation_type",
    "data_point",
    "sex",
    "zygosity",
    "strain_name",
    "strain_accession_id",
    "gene_symbol",
    "allele_symbol",
    "biological_sample_id",
    "experiment_id",
    "date_of_experiment",
    "pipeline_stable_id",
    "external_sample_id",
    "metadata_group",
    "litter_id",
    "age_in_weeks",
    "weight",
])

ROWS_PER_PAGE = 5000
MAX_RECORDS   = 500000  # safety cap

# ─────────────────────────────────────────
# STEP 1: DISCOVER ALL OFD PARAMETERS
# ─────────────────────────────────────────

print("=" * 52)
print("IMPC OPEN FIELD DATA ACQUISITION")
print("Analysis 3: Dark Archive Mouse Data")
print("=" * 52)
print()
print("Step 1: Discovering OFD parameters...")
print()

params_url = (
    "https://api.mousephenotype.org"
    f"/impress/protocol/json/{PROCEDURE_ID}"
)

try:
    r = requests.get(params_url, timeout=30)
    if r.status_code == 200:
        impress_data = r.json()
        params_list = []

        # Walk the IMPReSS structure
        if isinstance(impress_data, dict):
            parameters = impress_data.get(
                'parameters', []
            )
            for p in parameters:
                params_list.append({
                    'parameter_key':
                        p.get('parameterKey', ''),
                    'parameter_name':
                        p.get('name', ''),
                    'unit':
                        p.get('unit', ''),
                    'type':
                        p.get('type', ''),
                    'description':
                        p.get('description', ''),
                })

        if params_list:
            params_df = pd.DataFrame(params_list)
            params_df.to_csv(
                'impc_open_field_parameters.csv',
                index=False
            )
            print(
                f"  Parameters found: "
                f"{len(params_df)}"
            )
            for _, row in params_df.iterrows():
                print(
                    f"    {row['parameter_key']:<30}"
                    f" {row['parameter_name']}"
                )
        else:
            print(
                "  Could not parse IMPReSS "
                "response. Using known "
                "parameter IDs."
            )
    else:
        print(
            f"  IMPReSS API returned "
            f"{r.status_code}. "
            f"Using known parameter IDs."
        )
except Exception as e:
    print(f"  IMPReSS lookup failed: {e}")
    print("  Proceeding with known IDs.")

print()

# Known OFD parameter stable IDs
# (confirmed from IMPReSS browser)
KNOWN_PARAMS = {
    "IMPC_OFD_001_001":
        "Distance traveled total",
    "IMPC_OFD_002_001":
        "Velocity average",
    "IMPC_OFD_003_001":
        "Time mobile",
    "IMPC_OFD_004_001":
        "Time immobile",
    "IMPC_OFD_008_001":
        "Center entries",
    "IMPC_OFD_009_001":
        "Time in center",
    "IMPC_OFD_010_001":
        "Time in periphery (thigmotaxis)",
    "IMPC_OFD_011_001":
        "Distance in center",
    "IMPC_OFD_012_001":
        "Distance in periphery",
    "IMPC_OFD_013_001":
        "Rearing count",
    "IMPC_OFD_020_001":
        "Distance traveled first 5 min",
    "IMPC_OFD_021_001":
        "Distance traveled last 5 min",
}

print("Target parameters:")
for k, v in KNOWN_PARAMS.items():
    print(f"  {k}: {v}")
print()


# ─────────────────────────────────────────
# STEP 2: DISCOVER PHENOTYPING CENTERS
# ─────────────────────────────────────────

print("Step 2: Discovering phenotyping "
      "centers with OFD data...")
print()

facet_url = SOLR_BASE
facet_params = {
    "q": (
        f"procedure_stable_id:"
        f"{PROCEDURE_ID}"
    ),
    "rows": 0,
    "facet": "true",
    "facet.field": "phenotyping_center",
    "facet.limit": 50,
    "facet.mincount": 1,
    "wt": "json",
}

try:
    r = requests.get(
        facet_url,
        params=facet_params,
        timeout=60
    )
    r.raise_for_status()
    facet_data = r.json()

    facet_counts = (
        facet_data
        .get('facet_counts', {})
        .get('facet_fields', {})
        .get('phenotyping_center', [])
    )

    # Parse alternating name/count list
    centers = {}
    for i in range(0, len(facet_counts), 2):
        center = facet_counts[i]
        count  = facet_counts[i+1]
        if count > 0:
            centers[center] = count

    print(f"  Centers with OFD data: "
          f"{len(centers)}")
    print()
    print(
        f"  {'Center':<35} "
        f"{'Observations':>14}"
    )
    print("  " + "-" * 51)
    total_obs = 0
    for c, n in sorted(
        centers.items(),
        key=lambda x: -x[1]
    ):
        print(f"  {c:<35} {n:>14,}")
        total_obs += n
    print("  " + "-" * 51)
    print(
        f"  {'TOTAL':<35} "
        f"{total_obs:>14,}"
    )

except Exception as e:
    print(f"  Facet query failed: {e}")
    print("  Using default center list.")
    centers = {
        'JAX':  None,
        'TCP':  None,
        'UCD':  None,
        'WSI':  None,
        'HMGU': None,
        'MRC Harwell': None,
        'RBRC': None,
        'ICS':  None,
        'CNIO': None,
        'BCM':  None,
    }

print()


# ─────────────────────────────────────────
# STEP 3: ALSO DISCOVER AVAILABLE
# PARAMETER IDs FROM DATA
# ─────────────────────────────────────────

print("Step 3: Confirming available "
      "parameters in data...")
print()

param_facet_params = {
    "q": (
        f"procedure_stable_id:"
        f"{PROCEDURE_ID}"
        f" AND observation_type:unidimensional"
    ),
    "rows": 0,
    "facet": "true",
    "facet.field": "parameter_stable_id",
    "facet.limit": 100,
    "facet.mincount": 100,
    "wt": "json",
}

try:
    r = requests.get(
        SOLR_BASE,
        params=param_facet_params,
        timeout=60
    )
    r.raise_for_status()
    pf_data = r.json()

    pf_counts = (
        pf_data
        .get('facet_counts', {})
        .get('facet_fields', {})
        .get('parameter_stable_id', [])
    )

    data_params = {}
    for i in range(0, len(pf_counts), 2):
        pid   = pf_counts[i]
        count = pf_counts[i+1]
        if count >= 100:
            data_params[pid] = count

    print(
        f"  Parameters with ≥100 "
        f"observations: {len(data_params)}"
    )
    print()
    for pid, cnt in sorted(
        data_params.items(),
        key=lambda x: -x[1]
    ):
        label = KNOWN_PARAMS.get(
            pid,
            '(unlabeled)'
        )
        print(
            f"    {pid:<30} "
            f"{cnt:>10,}  {label}"
        )

    # Update target params to only
    # those confirmed in data
    confirmed_params = {
        k: v for k, v in KNOWN_PARAMS.items()
        if k in data_params
    }
    if confirmed_params:
        print()
        print(
            f"  Confirmed target params: "
            f"{len(confirmed_params)}"
        )
    else:
        confirmed_params = KNOWN_PARAMS
        print("  Using all known params.")

except Exception as e:
    print(f"  Parameter facet failed: {e}")
    confirmed_params = KNOWN_PARAMS

print()


# ─────────────────────────────────────────
# STEP 4: PULL RAW OBSERVATIONS
# ─────────────────────────────────────────

print("Step 4: Pulling raw OFD "
      "observations...")
print("  (This will take several "
      "minutes for large datasets)")
print()

all_records = []

# Build parameter filter
param_filter = " OR ".join([
    f"parameter_stable_id:{pid}"
    for pid in confirmed_params.keys()
])

base_query = {
    "q": (
        f"procedure_stable_id:{PROCEDURE_ID}"
        f" AND observation_type:unidimensional"
        f" AND ({param_filter})"
    ),
    "fl": FIELDS,
    "rows": ROWS_PER_PAGE,
    "wt": "json",
    "sort": "id asc",
}

# Get total count first
count_query = base_query.copy()
count_query["rows"] = 0
try:
    r = requests.get(
        SOLR_BASE,
        params=count_query,
        timeout=60
    )
    r.raise_for_status()
    total = (
        r.json()
        .get('response', {})
        .get('numFound', 0)
    )
    print(
        f"  Total observations to "
        f"retrieve: {total:,}"
    )
    if total > MAX_RECORDS:
        print(
            f"  Capping at {MAX_RECORDS:,} "
            f"records for initial run."
        )
        total = MAX_RECORDS
except Exception as e:
    print(f"  Count query failed: {e}")
    total = 50000

print()

# Paginated retrieval
n_pages = (total // ROWS_PER_PAGE) + 1
failed_pages = []

with tqdm(
    total=total,
    desc="  Fetching",
    unit=" obs"
) as pbar:
    for page in range(n_pages):
        start = page * ROWS_PER_PAGE
        if start >= total:
            break

        query = base_query.copy()
        query["start"] = start

        for attempt in range(3):
            try:
                r = requests.get(
                    SOLR_BASE,
                    params=query,
                    timeout=120
                )
                r.raise_for_status()
                docs = (
                    r.json()
                    .get('response', {})
                    .get('docs', [])
                )
                all_records.extend(docs)
                pbar.update(len(docs))
                time.sleep(0.3)
                break
            except Exception as e:
                if attempt == 2:
                    print(
                        f"\n  Page {page} "
                        f"failed after 3 "
                        f"attempts: {e}"
                    )
                    failed_pages.append(page)
                else:
                    time.sleep(2)

print()
print(
    f"  Records retrieved: "
    f"{len(all_records):,}"
)
if failed_pages:
    print(
        f"  Failed pages: "
        f"{failed_pages}"
    )
print()


# ─────────────────────────────────────────
# STEP 5: BUILD DATAFRAME AND SAVE RAW
# ─────────────────────────────────────────

print("Step 5: Building dataframe...")
print()

df = pd.DataFrame(all_records)

if df.empty:
    print("ERROR: No data retrieved.")
    print("Check API connectivity and "
          "try running again.")
    raise SystemExit(1)

# Add human-readable parameter label
df['parameter_label'] = (
    df['parameter_stable_id']
    .map(confirmed_params)
    .fillna(df['parameter_stable_id'])
)

# Add facility address lookup
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
}

# Map facility metadata
for meta_field in [
    'address', 'country', 'city',
    'urban_class', 'elf_prior',
    'lat', 'lon'
]:
    df[meta_field] = df[
        'phenotyping_center'
    ].map(
        lambda c, f=meta_field:
        FACILITY_META.get(c, {}).get(f, None)
    )

# Save raw
df.to_csv(
    'impc_open_field_raw.csv',
    index=False
)
print(
    f"  Saved → impc_open_field_raw.csv"
    f"  ({len(df):,} rows)"
)
print()


# ─────────────────────────────────────────
# STEP 6: SUMMARY STATISTICS BY CENTER
# ─────────────────────────────────────────

print("Step 6: Computing summary "
      "statistics by center...")
print()

# Pivot so each parameter is a column
df_numeric = df[
    pd.to_numeric(
        df['data_point'],
        errors='coerce'
    ).notna()
].copy()
df_numeric['data_point'] = pd.to_numeric(
    df_numeric['data_point']
)

summary_rows = []

for center in df_numeric[
    'phenotyping_center'
].unique():
    center_df = df_numeric[
        df_numeric['phenotyping_center']
        == center
    ]
    meta = FACILITY_META.get(center, {})

    row = {
        'phenotyping_center': center,
        'n_observations':
            len(center_df),
        'n_unique_animals':
            center_df[
                'biological_sample_id'
            ].nunique(),
        'address':
            meta.get('address', ''),
        'city':
            meta.get('city', ''),
        'country':
            meta.get('country', ''),
        'urban_class':
            meta.get('urban_class', ''),
        'elf_prior':
            meta.get('elf_prior', ''),
        'lat':
            meta.get('lat', None),
        'lon':
            meta.get('lon', None),
    }

    # Per-parameter stats
    for pid, plabel in confirmed_params.items():
        param_df = center_df[
            center_df['parameter_stable_id']
            == pid
        ]['data_point']

        if len(param_df) >= 5:
            safe = plabel.replace(
                ' ', '_'
            ).replace('(', '').replace(
                ')', ''
            )[:30]
            row[f'{safe}_n']      = len(param_df)
            row[f'{safe}_mean']   = param_df.mean()
            row[f'{safe}_median'] = param_df.median()
            row[f'{safe}_sd']     = param_df.std()
            row[f'{safe}_sem']    = (
                param_df.std()
                / (len(param_df) ** 0.5)
            )
        else:
            safe = plabel.replace(
                ' ', '_'
            ).replace('(', '').replace(
                ')', ''
            )[:30]
            row[f'{safe}_n']      = 0
            row[f'{safe}_mean']   = None
            row[f'{safe}_median'] = None
            row[f'{safe}_sd']     = None
            row[f'{safe}_sem']    = None

    # Sex breakdown
    sex_counts = center_df[
        'sex'
    ].value_counts()
    row['n_male']   = sex_counts.get('male', 0)
    row['n_female'] = sex_counts.get('female', 0)

    # Zygosity breakdown
    zyg_counts = center_df[
        'zygosity'
    ].value_counts()
    row['n_homozygote'] = zyg_counts.get(
        'homozygote', 0
    )
    row['n_heterozygote'] = zyg_counts.get(
        'heterozygote', 0
    )
    row['n_wildtype'] = zyg_counts.get(
        'wild type', 0
    )

    summary_rows.append(row)

summary_df = pd.DataFrame(summary_rows)
summary_df = summary_df.sort_values(
    'n_observations',
    ascending=False
)

summary_df.to_csv(
    'impc_open_field_by_center.csv',
    index=False
)
print(
    f"  Saved → "
    f"impc_open_field_by_center.csv"
)
print()


# ─────────────────────────────────────────
# STEP 7: PRINT READABLE SUMMARY
# ─────────────────────────────────────────

print("=" * 60)
print("FACILITY SUMMARY — OPEN FIELD TEST")
print("=" * 60)
print()

# Identify the locomotion and
# thigmotaxis columns
loco_col    = None
thigmo_col  = None
center_col  = None

for col in summary_df.columns:
    if 'Distance_traveled_total' in col \
            and '_mean' in col:
        loco_col = col
    if 'periphery' in col.lower() \
            and '_mean' in col:
        thigmo_col = col
    if 'Time_in_center' in col \
            and '_mean' in col:
        center_col = col

print(
    f"{'Center':<20} "
    f"{'N_obs':>8} "
    f"{'N_animals':>10} "
    f"{'ELF_prior':>12} "
    + (f"{'Loco_mean':>12} " if loco_col else "")
    + (f"{'Thigmo_mean':>12} " if thigmo_col else "")
    + (f"{'Center_mean':>12}" if center_col else "")
)
print("-" * 80)

for _, row in summary_df.iterrows():
    line = (
        f"{str(row['phenotyping_center']):<20}"
        f"{int(row['n_observations']):>8,}"
        f"{int(row['n_unique_animals']):>10,}"
        f"{str(row.get('elf_prior','?')):>12}"
    )
    if loco_col and row.get(loco_col):
        line += f"{row[loco_col]:>12.1f}"
    elif loco_col:
        line += f"{'—':>12}"
    if thigmo_col and row.get(thigmo_col):
        line += f"{row[thigmo_col]:>12.1f}"
    elif thigmo_col:
        line += f"{'—':>12}"
    if center_col and row.get(center_col):
        line += f"{row[center_col]:>12.1f}"
    elif center_col:
        line += f"{'—':>12}"
    print(line)

print()
print("NOTE: ELF_prior is a qualitative")
print("prediction based on facility")
print("location and urban class only.")
print("Quantitative ELF estimation")
print("(Step 2 of Analysis 3) will")
print("replace this with computed values")
print("from power line proximity,")
print("building era, and equipment")
print("density reconstruction.")
print()
print("=" * 60)
print("FILES SAVED:")
print("  impc_open_field_raw.csv")
print("  impc_open_field_by_center.csv")
print("  impc_open_field_parameters.csv")
print()
print("NEXT STEP:")
print("  impc_elf_estimation.py")
print("  Estimate ambient ELF at each")
print("  facility using power line")
print("  proximity and urban class.")
print("  Then correlate ELF estimates")
print("  against facility-level open")
print("  field behavioral means.")
print("=" * 60)
