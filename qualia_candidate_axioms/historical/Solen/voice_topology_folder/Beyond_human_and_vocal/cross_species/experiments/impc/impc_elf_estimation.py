"""
IMPC ANALYSIS 3 — STEP 2:
ELF ESTIMATION AND UNITS
HARMONIZATION

Reads impc_open_field_by_center.csv.

Step A: Units harmonization.
  Detects and corrects centers
  reporting thigmotaxis/time
  parameters in milliseconds
  rather than seconds.
  Flags any center whose mean
  time-in-test exceeds 1800s
  (30 min) as likely ms-scale.

Step B: CCP-IMG and KMPC
  facility metadata assignment.

Step C: Quantitative ELF
  estimation for each facility.
  Method: composite score from
    (1) urban class
    (2) country grid frequency
        (50Hz EU/JP/CN vs 60Hz NA)
    (3) proximity tier to nearest
        known high-voltage line
        (estimated from city
         geography)
    (4) building era proxy
  Produces: elf_score (0-100),
  elf_tier (LOW/MED/HIGH/VERY_HIGH)

Step D: Spearman and Pearson
  correlation between elf_score
  and behavioral means:
    — thigmotaxis (time in periphery)
    — time in center
    — rearing count
  For all centers and wildtype
  animals only.

Step E: Print full results table
  and correlation summary.

Output:
  impc_elf_by_center.csv
  impc_elf_correlation_results.txt
"""

import pandas as pd
import numpy as np
from scipy import stats

# ─────────────────────────────────────────
# FACILITY METADATA — COMPLETE
# Including CCP-IMG and KMPC
# ─────────────────────────────────────────

FACILITY_META = {
    'JAX': {
        'full_name':
            'The Jackson Laboratory',
        'address':
            '600 Main St, Bar Harbor, ME',
        'country': 'USA',
        'city': 'Bar Harbor',
        'urban_class': 'rural',
        'grid_hz': 60,
        'hv_proximity_km': 80,
        'building_era': 1970,
        'research_density': 'medium',
        'lat': 44.388,
        'lon': -68.204,
    },
    'TCP': {
        'full_name':
            'Toronto Centre for Phenogenomics',
        'address':
            '25 Orde St, Toronto, ON',
        'country': 'Canada',
        'city': 'Toronto',
        'urban_class': 'urban_downtown',
        'grid_hz': 60,
        'hv_proximity_km': 1.5,
        'building_era': 2003,
        'research_density': 'high',
        'lat': 43.659,
        'lon': -79.386,
    },
    'CCP-IMG': {
        'full_name':
            'Canadian Centre for '
            'Phenogenomics (Imaging)',
        'address':
            '25 Orde St, Toronto, ON',
        'country': 'Canada',
        'city': 'Toronto',
        'urban_class': 'urban_downtown',
        'grid_hz': 60,
        'hv_proximity_km': 1.5,
        'building_era': 2003,
        'research_density': 'high',
        'lat': 43.659,
        'lon': -79.386,
        'note':
            'Same campus as TCP. '
            'Likely same building.',
    },
    'UC Davis': {
        'full_name':
            'UC Davis Mouse Biology Program',
        'address':
            '279 Cousteau Pl, Davis, CA',
        'country': 'USA',
        'city': 'Davis',
        'urban_class': 'suburban',
        'grid_hz': 60,
        'hv_proximity_km': 12,
        'building_era': 1995,
        'research_density': 'medium',
        'lat': 38.545,
        'lon': -121.766,
    },
    'WSI': {
        'full_name':
            'Wellcome Sanger Institute',
        'address':
            'Genome Campus, Hinxton, UK',
        'country': 'UK',
        'city': 'Hinxton',
        'urban_class': 'rural_campus',
        'grid_hz': 50,
        'hv_proximity_km': 5,
        'building_era': 1993,
        'research_density': 'high',
        'lat': 52.082,
        'lon': 0.186,
    },
    'HMGU': {
        'full_name':
            'Helmholtz Zentrum München',
        'address':
            'Ingolstädter Landstr 1, '
            'Neuherberg, DE',
        'country': 'Germany',
        'city': 'Neuherberg (Munich fringe)',
        'urban_class': 'urban_fringe',
        'grid_hz': 50,
        'hv_proximity_km': 3,
        'building_era': 1985,
        'research_density': 'high',
        'lat': 48.220,
        'lon': 11.589,
        'units_flag':
            'SUSPECTED_MILLISECONDS',
    },
    'MRC Harwell': {
        'full_name':
            'MRC Harwell — Mary Lyon Centre',
        'address':
            'Harwell Campus, Didcot, UK',
        'country': 'UK',
        'city': 'Didcot',
        'urban_class': 'science_campus',
        'grid_hz': 50,
        'hv_proximity_km': 2,
        'building_era': 2000,
        'research_density': 'high',
        'lat': 51.575,
        'lon': -1.309,
        'note':
            'Harwell campus hosts '
            'Diamond Light Source '
            'synchrotron — high local '
            'ELF from facility equipment.',
    },
    'RBRC': {
        'full_name':
            'RIKEN BioResource Research '
            'Center',
        'address':
            '3-1-1 Koyadai, Tsukuba, JP',
        'country': 'Japan',
        'city': 'Tsukuba',
        'urban_class': 'science_city',
        'grid_hz': 50,
        'hv_proximity_km': 4,
        'building_era': 1990,
        'research_density': 'high',
        'lat': 36.105,
        'lon': 140.098,
    },
    'ICS': {
        'full_name':
            'Institut Clinique de la Souris',
        'address':
            'Parc d\'Innovation, '
            'Illkirch-Graffenstaden, FR',
        'country': 'France',
        'city': 'Illkirch',
        'urban_class': 'suburban',
        'grid_hz': 50,
        'hv_proximity_km': 8,
        'building_era': 1994,
        'research_density': 'medium',
        'lat': 48.534,
        'lon': 7.723,
    },
    'CNIO': {
        'full_name':
            'Centro Nacional de '
            'Investigaciones Oncológicas',
        'address':
            'Melchor Fernández Almagro 3,'
            ' Madrid, ES',
        'country': 'Spain',
        'city': 'Madrid',
        'urban_class': 'urban',
        'grid_hz': 50,
        'hv_proximity_km': 2,
        'building_era': 2002,
        'research_density': 'high',
        'lat': 40.468,
        'lon': -3.690,
    },
    'BCM': {
        'full_name':
            'Baylor College of Medicine',
        'address':
            'One Baylor Plaza, Houston, TX',
        'country': 'USA',
        'city': 'Houston',
        'urban_class': 'urban_medical',
        'grid_hz': 60,
        'hv_proximity_km': 0.8,
        'building_era': 1978,
        'research_density': 'very_high',
        'lat': 29.710,
        'lon': -95.396,
        'note':
            'Texas Medical Center — '
            'largest medical complex '
            'in the world. Extremely '
            'high equipment ELF.',
    },
    'MARC': {
        'full_name':
            'Model Animal Research Center, '
            'Nanjing University',
        'address':
            '22 Hankou Rd, Nanjing, CN',
        'country': 'China',
        'city': 'Nanjing',
        'urban_class': 'urban',
        'grid_hz': 50,
        'hv_proximity_km': 3,
        'building_era': 2000,
        'research_density': 'high',
        'lat': 32.060,
        'lon': 118.796,
    },
    'KMPC': {
        'full_name':
            'Korea Mouse Phenotyping Center',
        'address':
            'Seoul National University, '
            'Seoul, KR',
        'country': 'South Korea',
        'city': 'Seoul',
        'urban_class': 'urban',
        'grid_hz': 60,
        'hv_proximity_km': 2,
        'building_era': 2013,
        'research_density': 'high',
        'lat': 37.460,
        'lon': 126.952,
    },
    'Monterotondo': {
        'full_name':
            'INFRAFRONTIER — Monterotondo',
        'address':
            'Via Ramarini 32, '
            'Monterotondo, IT',
        'country': 'Italy',
        'city': 'Monterotondo',
        'urban_class': 'suburban_rome',
        'grid_hz': 50,
        'hv_proximity_km': 6,
        'building_era': 1988,
        'research_density': 'medium',
        'lat': 42.053,
        'lon': 12.616,
    },
}


# ─────────────────────────────────────────
# ELF SCORING FUNCTION
# ─────────────────────────────────────────

def compute_elf_score(meta):
    """
    Composite ELF score 0-100.
    Higher = more ambient ELF.

    Components:
      Urban class:       0-35 pts
      HV proximity:      0-30 pts
      Research density:  0-20 pts
      Building era:      0-15 pts
        (older = more ELF from
         unshielded wiring)
    """
    score = 0.0

    # Urban class component (0-35)
    urban_scores = {
        'rural':          0,
        'rural_campus':   5,
        'suburban':       12,
        'suburban_rome':  12,
        'science_campus': 18,
        'science_city':   20,
        'urban_fringe':   22,
        'urban':          28,
        'urban_downtown': 33,
        'urban_medical':  35,
    }
    score += urban_scores.get(
        meta.get('urban_class', 'urban'),
        15
    )

    # HV line proximity (0-30)
    # Inverse: closer = higher score
    hv_km = meta.get('hv_proximity_km', 10)
    if hv_km <= 0.5:
        score += 30
    elif hv_km <= 1:
        score += 27
    elif hv_km <= 2:
        score += 24
    elif hv_km <= 3:
        score += 20
    elif hv_km <= 5:
        score += 15
    elif hv_km <= 10:
        score += 10
    elif hv_km <= 20:
        score += 5
    else:
        score += 0

    # Research density (0-20)
    density_scores = {
        'low':       0,
        'medium':    8,
        'high':     14,
        'very_high': 20,
    }
    score += density_scores.get(
        meta.get('research_density',
                 'medium'),
        8
    )

    # Building era (0-15)
    # Older buildings have less
    # EMC shielding in wiring
    era = meta.get('building_era', 2000)
    if era < 1970:
        score += 15
    elif era < 1980:
        score += 12
    elif era < 1990:
        score += 9
    elif era < 2000:
        score += 6
    elif era < 2010:
        score += 3
    else:
        score += 1

    return round(score, 1)


def elf_tier(score):
    if score < 20:
        return 'LOW'
    elif score < 40:
        return 'MEDIUM'
    elif score < 60:
        return 'HIGH'
    else:
        return 'VERY_HIGH'


# ─────────────────────────────────────────
# LOAD SUMMARY DATA
# ─────────────────────────────────────────

print("=" * 60)
print("IMPC ANALYSIS 3 — ELF ESTIMATION")
print("AND BEHAVIORAL CORRELATION")
print("=" * 60)
print()

df = pd.read_csv(
    'impc_open_field_by_center.csv',
    low_memory=False
)
print(f"Centers loaded: {len(df)}")
print()


# ─────────────────────────────────────────
# STEP A: UNITS AUDIT
# ─────────────────────────────────────────

print("STEP A: Units audit")
print("─" * 50)
print()
print("Open field test duration:")
print("  Standard IMPC OFD: 20 min")
print("  = 1200 seconds maximum")
print("  Any mean > 1200s is likely ms")
print()

# Find thigmotaxis mean column
def find_col(df, *fragments):
    for col in df.columns:
        col_l = col.lower()
        if all(f.lower() in col_l
               for f in fragments):
            return col
    return None

thigmo_mean = find_col(
    df, 'periphery', 'mean'
)
center_mean = find_col(
    df, 'time_in_center', 'mean'
)
rearing_mean = find_col(
    df, 'rearing', 'mean'
)
dist_mean = find_col(
    df, 'distance_traveled_total', 'mean'
)

print(
    f"Thigmo column:  {thigmo_mean}"
)
print(
    f"Center column:  {center_mean}"
)
print(
    f"Rearing column: {rearing_mean}"
)
print(
    f"Distance column: {dist_mean}"
)
print()

MS_THRESHOLD = 1200  # seconds

units_issues = []
for _, row in df.iterrows():
    center = row['phenotyping_center']
    issues = []

    for col, label in [
        (thigmo_mean, 'thigmotaxis'),
        (center_mean, 'center_time'),
    ]:
        if col and pd.notna(row.get(col)):
            val = float(row[col])
            if val > MS_THRESHOLD:
                issues.append(
                    f"{label}: "
                    f"{val:.0f}s "
                    f"(SUSPECTED ms — "
                    f"will divide by 1000)"
                )

    if issues:
        units_issues.append(center)
        print(
            f"  UNITS FLAG: {center}"
        )
        for iss in issues:
            print(f"    {iss}")
    else:
        val_t = (
            float(row[thigmo_mean])
            if thigmo_mean and
            pd.notna(row.get(thigmo_mean))
            else None
        )
        print(
            f"  OK:          {center:<30}"
            + (f"  thigmo={val_t:.1f}s"
               if val_t else "")
        )

print()


# Apply unit correction
def correct_units(val, center,
                  flagged_centers):
    if val is None or pd.isna(val):
        return None
    val = float(val)
    if (center in flagged_centers
            and val > MS_THRESHOLD):
        return val / 1000.0
    return val


print("Applying unit corrections...")
df_clean = df.copy()

for col in [thigmo_mean, center_mean]:
    if col is None:
        continue
    df_clean[col + '_corrected'] = [
        correct_units(
            row.get(col),
            row['phenotyping_center'],
            units_issues
        )
        for _, row in df_clean.iterrows()
    ]

# Use corrected columns going forward
thigmo_use = (
    thigmo_mean + '_corrected'
    if thigmo_mean else None
)
center_use = (
    center_mean + '_corrected'
    if center_mean else None
)
rearing_use = rearing_mean
dist_use    = dist_mean

print()


# ─────────────────────────────────────────
# STEP B: ASSIGN ELF SCORES
# ─────────────────────────────────────────

print("STEP B: ELF score assignment")
print("─" * 50)
print()

elf_scores  = []
elf_tiers   = []
full_names  = []
hv_prox     = []
grid_hz_col = []
build_era   = []
notes       = []

for _, row in df_clean.iterrows():
    center = row['phenotyping_center']
    meta = {}

    if center in FACILITY_META:
        meta = FACILITY_META[center]
    else:
        for key in FACILITY_META:
            if (key.lower() in center.lower()
                    or center.lower()
                    in key.lower()):
                meta = FACILITY_META[key]
                break

    score = (
        compute_elf_score(meta)
        if meta else 30.0
    )
    tier = elf_tier(score)

    elf_scores.append(score)
    elf_tiers.append(tier)
    full_names.append(
        meta.get('full_name', center)
    )
    hv_prox.append(
        meta.get('hv_proximity_km', None)
    )
    grid_hz_col.append(
        meta.get('grid_hz', None)
    )
    build_era.append(
        meta.get('building_era', None)
    )
    notes.append(
        meta.get('note', '')
    )

    print(
        f"  {center:<20} "
        f"ELF score: {score:>5.1f}  "
        f"tier: {tier:<10}  "
        f"HV: {meta.get('hv_proximity_km','?'):>5}km"
    )

df_clean['elf_score']        = elf_scores
df_clean['elf_tier']         = elf_tiers
df_clean['facility_name']    = full_names
df_clean['hv_proximity_km']  = hv_prox
df_clean['grid_hz']          = grid_hz_col
df_clean['building_era']     = build_era
df_clean['facility_note']    = notes

print()


# ─────────────────────────────────────────
# STEP C: CORRELATION ANALYSIS
# ─────────────────────────────────────────

print("STEP C: Correlation analysis")
print("─" * 50)
print()

results = []

def log(s=""):
    results.append(s)
    print(s)

log("ELF score vs behavioral means")
log("(Spearman rank correlation)")
log("N centers = "
    f"{len(df_clean)}")
log()

# Drop centers with missing
# behavioral values per analysis
for beh_col, beh_label in [
    (thigmo_use, 'Thigmotaxis '
                 '(time in periphery)'),
    (center_use, 'Time in center'),
    (rearing_use, 'Rearing count'),
    (dist_use,   'Distance traveled'),
]:
    if beh_col is None:
        log(f"{beh_label}: column not found")
        continue

    valid = df_clean[
        ['phenotyping_center',
         'elf_score',
         'elf_tier',
         beh_col]
    ].dropna(subset=['elf_score', beh_col])

    if len(valid) < 4:
        log(
            f"{beh_label}: "
            f"only {len(valid)} centers "
            f"with data — skip"
        )
        continue

    x = valid['elf_score'].values
    y = valid[beh_col].values

    r_s, p_s = stats.spearmanr(x, y)
    r_p, p_p = stats.pearsonr(x, y)

    direction = (
        "POSITIVE (higher ELF → "
        "more behavior)"
        if r_s > 0
        else "NEGATIVE (higher ELF → "
             "less behavior)"
    )

    sig = (
        "***" if p_s < 0.001 else
        "**"  if p_s < 0.01  else
        "*"   if p_s < 0.05  else
        "ns"
    )

    log(f"{'─'*50}")
    log(f"Behavior: {beh_label}")
    log(f"  N centers:        {len(valid)}")
    log(f"  Spearman r:       {r_s:+.4f}")
    log(f"  Spearman p:       {p_s:.4f}  {sig}")
    log(f"  Pearson  r:       {r_p:+.4f}")
    log(f"  Pearson  p:       {p_p:.4f}")
    log(f"  Direction:        {direction}")
    log()
    log("  Per-center values "
        "(sorted by ELF score):")
    log(
        f"  {'Center':<22} "
        f"{'ELF_score':>10} "
        f"{'ELF_tier':<14} "
        f"{'Value':>10}"
    )
    log("  " + "─" * 60)
    for _, vrow in valid.sort_values(
        'elf_score'
    ).iterrows():
        log(
            f"  {vrow['phenotyping_center']:<22}"
            f"{vrow['elf_score']:>10.1f} "
            f"{vrow['elf_tier']:<14} "
            f"{vrow[beh_col]:>10.3f}"
        )
    log()


# ─────────────────────────────────────────
# STEP D: FULL RESULTS TABLE
# ─────────────────────────────────────────

log("=" * 68)
log("FULL FACILITY TABLE")
log("(sorted by ELF score ascending)")
log("=" * 68)
log()
log(
    f"{'Center':<20} "
    f"{'ELF':>6} "
    f"{'Tier':<12} "
    f"{'HV_km':>6} "
    f"{'Hz':>4} "
    f"{'Era':>5} "
    + (f"{'Thigmo':>9} " if thigmo_use else "")
    + (f"{'CtrTime':>8} " if center_use else "")
    + (f"{'Rear':>6}" if rearing_use else "")
)
log("─" * 85)

for _, row in df_clean.sort_values(
    'elf_score'
).iterrows():
    def fv(col, fmt="{:>9.2f}"):
        v = row.get(col)
        if v is None or pd.isna(v):
            return f"{'—':>9}"
        return fmt.format(float(v))

    line = (
        f"{str(row['phenotyping_center']):<20}"
        f"{row['elf_score']:>6.1f} "
        f"{str(row['elf_tier']):<12} "
        f"{str(row.get('hv_proximity_km','?')):>6} "
        f"{str(row.get('grid_hz','?')):>4} "
        f"{str(row.get('building_era','?')):>5} "
    )
    if thigmo_use:
        line += fv(thigmo_use) + " "
    if center_use:
        line += fv(center_use, "{:>8.2f}") + " "
    if rearing_use:
        line += fv(rearing_use, "{:>6.2f}")
    log(line)

log()
log("Notes:")
for _, row in df_clean.iterrows():
    note = row.get('facility_note', '')
    if note:
        log(
            f"  {row['phenotyping_center']}: "
            f"{note}"
        )
log()
log("UNITS CORRECTIONS APPLIED:")
for c in units_issues:
    log(f"  {c}: time params divided by 1000")
log("  (suspected milliseconds → seconds)")
log()


# ─────────────────────────────────────────
# SAVE
# ─────────────────────────────────────────

df_clean.to_csv(
    'impc_elf_by_center.csv',
    index=False
)

with open(
    'impc_elf_correlation_results.txt',
    'w'
) as f:
    f.write("\n".join(results))

print()
print("Saved → impc_elf_by_center.csv")
print("Saved → impc_elf_correlation_results.txt")
print()
print("NEXT STEP:")
print("  impc_wildtype_analysis.py")
print("  Repeat correlation using")
print("  wildtype animals only")
print("  (removes genotype confound).")
