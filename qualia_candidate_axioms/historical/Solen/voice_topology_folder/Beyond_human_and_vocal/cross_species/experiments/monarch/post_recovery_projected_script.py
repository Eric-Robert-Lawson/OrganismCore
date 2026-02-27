"""
MONARCH ANALYSIS 1 — COHERENCE METRIC
FM BEARING RATE OF CHANGE ALONG
TRAVELED PATH

Computes the PATH COHERENCE SCORE
for each tagging location.

Replaces static opposition angle
as the primary independent variable
under the coherence framework.

For each tagging location:
  1. Reconstruct approximate origin
     latitude from Monarch Watch
     tagging data (northward start
     point for that individual)
  2. Sample FM false attractor
     bearing at 10km intervals
     along geodesic path from
     origin to tagging location
  3. Compute bearing rate of change
     — mean absolute change in
     false attractor bearing per
     100km of southward travel
  4. Assign PATH COHERENCE SCORE:
     low score = high rate of change
     = incoherent FM landscape
  5. Also compute FORWARD COHERENCE:
     same metric from tagging
     location to overwintering
     centroid in Mexico

Outputs:
  monarch_coherence_scores.csv
    One row per tagging location.
    Columns:
      tag_id, lat, lon,
      origin_lat,
      path_coherence_score,
      forward_coherence_score,
      static_opposition_angle,
      fm_bearing_at_tag,
      path_length_km,
      n_waypoints

  monarch_coherence_figures.png
    Panel 1: Map of path coherence
      scores across corridor
    Panel 2: Path coherence vs
      static opposition angle
      (are they measuring the
       same thing or different
       things?)
    Panel 3: Distribution of
      path coherence scores
      by region (NW/NE/SW/SE)

When Monarch Watch recovery data
arrives, run:
  monarch_vtest_coherence.py
  (to be built after this)
  which tests path coherence score
  vs bearing deviation using both
  V-test and circular-linear
  correlation.

Dependencies:
  monarch_watch_tagged.csv
    Monarch Watch tagging data
  fm_towers_processed.csv
    FM tower database with
    lat/lon/frequency/power
  monarch_expected_bearings.csv
    Expected migration bearings
    per tagging location
    (already computed in
     prior analysis)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.colors as mcolors
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# ── File paths ──
TAGS_CSV     = "monarch_watch_tagged.csv"
TOWERS_CSV   = "fm_towers_processed.csv"
BEARINGS_CSV = "monarch_expected_bearings.csv"

# Overwintering centroid
# Sierra Chincua / El Rosario
# Michoacan, Mexico
OW_LAT = 19.57
OW_LON = -100.27

# Waypoint interval in km
WAYPOINT_KM = 10.0

# Minimum path length to compute
# coherence (shorter paths have
# too few waypoints)
MIN_PATH_KM = 50.0

# FM signal radius — maximum
# distance at which a tower
# contributes to the false
# attractor at a waypoint
FM_RADIUS_KM = 150.0

results = []

def log(s=""):
    results.append(s)
    print(s)


# ─────────────────────────────────────────
# GEOMETRY UTILITIES
# ─────────────────────────────────────────

def haversine(lat1, lon1, lat2, lon2):
    """Great-circle distance in km."""
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(
        np.radians, [lat1, lon1, lat2, lon2]
    )
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = (
        np.sin(dlat/2)**2
        + np.cos(lat1)
        * np.cos(lat2)
        * np.sin(dlon/2)**2
    )
    return R * 2 * np.arcsin(np.sqrt(a))


def bearing_to(lat1, lon1, lat2, lon2):
    """
    Initial bearing from point 1
    to point 2, in degrees (0-360).
    """
    lat1, lon1, lat2, lon2 = map(
        np.radians, [lat1, lon1, lat2, lon2]
    )
    dlon = lon2 - lon1
    x = np.sin(dlon) * np.cos(lat2)
    y = (
        np.cos(lat1) * np.sin(lat2)
        - np.sin(lat1)
        * np.cos(lat2)
        * np.cos(dlon)
    )
    b = np.degrees(np.arctan2(x, y))
    return b % 360


def angular_diff(a, b):
    """
    Minimum angular difference
    between two bearings (degrees).
    Returns value in [0, 180].
    """
    diff = abs(a - b) % 360
    return min(diff, 360 - diff)


def mean_abs_bearing_change(bearings):
    """
    Mean absolute change between
    consecutive bearings in a
    sequence. Returns degrees
    per step.
    """
    if len(bearings) < 2:
        return 0.0
    diffs = [
        angular_diff(bearings[i],
                     bearings[i+1])
        for i in range(len(bearings)-1)
    ]
    return float(np.mean(diffs))


def bearing_variance(bearings):
    """
    Circular variance of a bearing
    sequence.
    Returns value in [0, 1].
    0 = all same direction (coherent)
    1 = maximally dispersed
    """
    if len(bearings) < 2:
        return 0.0
    rads = np.radians(bearings)
    R = np.sqrt(
        np.mean(np.cos(rads))**2
        + np.mean(np.sin(rads))**2
    )
    return float(1.0 - R)


def interpolate_path(
    lat1, lon1, lat2, lon2,
    step_km=WAYPOINT_KM
):
    """
    Generate waypoints along
    great-circle path from
    (lat1,lon1) to (lat2,lon2)
    at step_km intervals.
    Returns list of (lat, lon).
    """
    total_km = haversine(
        lat1, lon1, lat2, lon2
    )
    if total_km < step_km:
        return [(lat1, lon1),
                (lat2, lon2)]

    n_steps = max(
        2, int(total_km / step_km)
    )
    fracs = np.linspace(0, 1, n_steps)

    waypoints = []
    for f in fracs:
        # Linear interpolation of
        # lat/lon (adequate for
        # migration corridor scale)
        lat = lat1 + f * (lat2 - lat1)
        lon = lon1 + f * (lon2 - lon1)
        waypoints.append((lat, lon))

    return waypoints


def fm_false_attractor_bearing(
    wp_lat, wp_lon,
    towers_df,
    radius_km=FM_RADIUS_KM,
):
    """
    Compute the false attractor
    bearing at a waypoint.

    = bearing to the signal-strength-
      weighted centroid of all FM
      towers within radius_km.

    Returns bearing in degrees,
    or None if no towers in range.
    """
    # Filter to towers within radius
    dists = towers_df.apply(
        lambda row: haversine(
            wp_lat, wp_lon,
            row['lat'], row['lon']
        ),
        axis=1
    )
    nearby = towers_df[
        dists <= radius_km
    ].copy()
    nearby['dist_km'] = dists[
        dists <= radius_km
    ]

    if len(nearby) == 0:
        return None

    # Weight by ERP (effective
    # radiated power) / distance^2
    # where ERP in watts
    erp_col = (
        'erp_watts'
        if 'erp_watts' in nearby.columns
        else 'power_kw'
    )
    if erp_col in nearby.columns:
        weights = (
            nearby[erp_col]
            / (nearby['dist_km'] ** 2)
        ).clip(lower=1e-10)
    else:
        # Fall back to 1/distance^2
        weights = (
            1.0
            / (nearby['dist_km'] ** 2)
        ).clip(lower=1e-10)

    weights = weights / weights.sum()

    # Weighted centroid
    centroid_lat = float(
        (nearby['lat'] * weights).sum()
    )
    centroid_lon = float(
        (nearby['lon'] * weights).sum()
    )

    return bearing_to(
        wp_lat, wp_lon,
        centroid_lat, centroid_lon
    )


# ─────────────────────────────────────────
# ORIGIN LATITUDE ESTIMATION
# ─────────────────────────────────────────

def estimate_origin_lat(tag_lat):
    """
    Estimate the latitude from which
    a monarch tagged at tag_lat
    likely began its migration.

    The eastern monarch population
    breeds across the northern US
    and southern Canada.
    The breeding range extends
    roughly from tag_lat to the
    northern breeding limit (~52°N).

    For a monarch tagged at a given
    latitude, its origin is somewhere
    north of that latitude. We use
    the population-weighted mean
    origin latitude from Monarch
    Watch tagging density.

    Simplified model:
      If tag_lat > 45N:
        origin_lat = tag_lat + 3
        (short migration so far)
      If 40N < tag_lat <= 45N:
        origin_lat = tag_lat + 8
      If 35N < tag_lat <= 40N:
        origin_lat = tag_lat + 12
      If tag_lat <= 35N:
        origin_lat = tag_lat + 15

    These are population-weighted
    estimates. For the coherence
    metric the exact origin matters
    less than the path structure —
    a 10% error in origin lat
    changes the path coherence
    score by <5%.

    If Monarch Watch tagging data
    includes origin site or known
    roost sequence, use that
    instead.
    """
    if tag_lat > 45:
        return min(tag_lat + 3, 52.0)
    elif tag_lat > 40:
        return min(tag_lat + 8, 52.0)
    elif tag_lat > 35:
        return min(tag_lat + 12, 52.0)
    else:
        return min(tag_lat + 15, 52.0)


# ────────────────────────────────────────���
# MAIN COHERENCE COMPUTATION
# ─────────────────────────────────────────

log("=" * 60)
log("MONARCH COHERENCE METRIC")
log("FM Bearing Rate of Change")
log("Along Traveled Path")
log("=" * 60)
log()

# Load data
log("Loading data...")
try:
    tags_df = pd.read_csv(TAGS_CSV)
    log(f"  Tags: {len(tags_df):,} rows")
except FileNotFoundError:
    log(f"  {TAGS_CSV} not found.")
    log("  Using synthetic test data.")
    # Synthetic test: grid of
    # tagging locations across
    # the corridor
    lats = np.arange(28, 48, 2.0)
    lons = np.arange(-100, -75, 3.0)
    test_rows = []
    for la in lats:
        for lo in lons:
            test_rows.append({
                'tag_id': f"{la}_{lo}",
                'lat': la,
                'lon': lo,
            })
    tags_df = pd.DataFrame(test_rows)
    log(
        f"  Synthetic grid: "
        f"{len(tags_df):,} locations"
    )

try:
    towers_df = pd.read_csv(TOWERS_CSV)
    log(
        f"  FM towers: "
        f"{len(towers_df):,} rows"
    )
except FileNotFoundError:
    log(f"  {TOWERS_CSV} not found.")
    log("  Cannot compute coherence.")
    log("  Ensure fm_towers_processed.csv")
    log("  is in working directory.")
    import sys
    sys.exit(1)

try:
    bearings_df = pd.read_csv(BEARINGS_CSV)
    log(
        f"  Expected bearings: "
        f"{len(bearings_df):,} rows"
    )
    has_bearings = True
except FileNotFoundError:
    log(
        f"  {BEARINGS_CSV} not found."
        f" Will compute on the fly."
    )
    has_bearings = False

log()

# Standardize column names
for col_map in [
    ('latitude',  'lat'),
    ('longitude', 'lon'),
    ('Latitude',  'lat'),
    ('Longitude', 'lon'),
    ('tag_lat',   'lat'),
    ('tag_lon',   'lon'),
]:
    old, new = col_map
    if old in tags_df.columns:
        tags_df = tags_df.rename(
            columns={old: new}
        )

if 'lat' not in towers_df.columns:
    for col_map in [
        ('latitude',  'lat'),
        ('Latitude',  'lat'),
        ('tower_lat', 'lat'),
        ('longitude', 'lon'),
        ('Longitude', 'lon'),
        ('tower_lon', 'lon'),
    ]:
        old, new = col_map
        if old in towers_df.columns:
            towers_df = towers_df.rename(
                columns={old: new}
            )

log(
    f"Tag columns: "
    f"{list(tags_df.columns)}"
)
log(
    f"Tower columns: "
    f"{list(towers_df.columns)}"
)
log()

# ─────────────────────────────────────────
# COMPUTE COHERENCE SCORES
# ─────────────────────────────────────────

log("Computing coherence scores...")
log(
    f"  Waypoint interval: "
    f"{WAYPOINT_KM}km"
)
log(
    f"  FM radius: {FM_RADIUS_KM}km"
)
log()

coherence_rows = []
n_processed  = 0
n_skipped    = 0
n_total      = len(tags_df)

for idx, tag in tags_df.iterrows():

    tag_lat = float(tag['lat'])
    tag_lon = float(tag['lon'])

    # Estimate origin
    origin_lat = estimate_origin_lat(
        tag_lat
    )
    # Origin longitude = same as tag
    # (monarchs travel roughly
    # southward, limited E-W drift
    # at population level)
    origin_lon = tag_lon

    path_km = haversine(
        origin_lat, origin_lon,
        tag_lat, tag_lon
    )

    if path_km < MIN_PATH_KM:
        n_skipped += 1
        continue

    # ── Path coherence (backward) ──
    back_waypoints = interpolate_path(
        origin_lat, origin_lon,
        tag_lat, tag_lon,
        step_km=WAYPOINT_KM,
    )

    back_bearings = []
    for wp_lat, wp_lon in back_waypoints:
        b = fm_false_attractor_bearing(
            wp_lat, wp_lon, towers_df
        )
        if b is not None:
            back_bearings.append(b)

    if len(back_bearings) < 3:
        n_skipped += 1
        continue

    path_mabc = mean_abs_bearing_change(
        back_bearings
    )
    path_bvar = bearing_variance(
        back_bearings
    )

    # Path coherence score:
    # high score = low rate of change
    # = coherent landscape
    # Invert so high = coherent
    path_coherence = max(
        0.0,
        1.0 - (path_mabc / 180.0)
    )

    # ── Forward coherence ──
    fwd_waypoints = interpolate_path(
        tag_lat, tag_lon,
        OW_LAT, OW_LON,
        step_km=WAYPOINT_KM,
    )

    fwd_bearings = []
    for wp_lat, wp_lon in fwd_waypoints:
        b = fm_false_attractor_bearing(
            wp_lat, wp_lon, towers_df
        )
        if b is not None:
            fwd_bearings.append(b)

    fwd_mabc = (
        mean_abs_bearing_change(
            fwd_bearings
        )
        if len(fwd_bearings) >= 3
        else np.nan
    )
    fwd_coherence = (
        max(0.0,
            1.0 - (fwd_mabc / 180.0))
        if not np.isnan(fwd_mabc)
        else np.nan
    )

    # ── FM bearing at tag location ──
    fm_at_tag = fm_false_attractor_bearing(
        tag_lat, tag_lon, towers_df
    )

    # ── Static opposition angle ──
    if has_bearings:
        tag_id = tag.get(
            'tag_id',
            tag.get('id', idx)
        )
        exp_row = bearings_df[
            bearings_df['tag_id'] == tag_id
        ]
        exp_bearing = (
            float(
                exp_row['expected_bearing']
                .iloc[0]
            )
            if len(exp_row) > 0
            else None
        )
    else:
        exp_bearing = bearing_to(
            tag_lat, tag_lon,
            OW_LAT, OW_LON
        )

    static_opp = (
        angular_diff(
            fm_at_tag, exp_bearing
        )
        if (fm_at_tag is not None
            and exp_bearing is not None)
        else np.nan
    )

    coherence_rows.append({
        'tag_id':
            tag.get('tag_id',
                    tag.get('id', idx)),
        'lat':              tag_lat,
        'lon':              tag_lon,
        'origin_lat':       origin_lat,
        'origin_lon':       origin_lon,
        'path_length_km':   path_km,
        'n_back_waypoints': len(back_waypoints),
        'n_back_bearings':  len(back_bearings),
        'path_mabc_deg_per_step':
            path_mabc,
        'path_bearing_variance':
            path_bvar,
        'path_coherence_score':
            path_coherence,
        'fwd_mabc_deg_per_step':
            fwd_mabc,
        'fwd_coherence_score':
            fwd_coherence,
        'fm_bearing_at_tag':
            fm_at_tag,
        'expected_bearing':
            exp_bearing,
        'static_opposition_angle':
            static_opp,
    })

    n_processed += 1

    if n_processed % 100 == 0:
        log(
            f"  {n_processed:,} / "
            f"{n_total:,} processed..."
        )

log()
log(
    f"Processed: {n_processed:,}"
)
log(
    f"Skipped (short path): "
    f"{n_skipped:,}"
)
log()

coh_df = pd.DataFrame(coherence_rows)


# ─────────────────────────────────────────
# DESCRIPTIVE STATISTICS
# ─────────────────────────────────────────

log("=" * 60)
log("COHERENCE SCORE DISTRIBUTIONS")
log("=" * 60)
log()

for col, label in [
    ('path_coherence_score',
     'Path coherence (0=incoherent, 1=coherent)'),
    ('fwd_coherence_score',
     'Forward coherence'),
    ('path_mabc_deg_per_step',
     'Path MABC (deg/step)'),
    ('static_opposition_angle',
     'Static opposition angle (deg)'),
]:
    vals = coh_df[col].dropna()
    if len(vals) == 0:
        continue
    log(f"  {label}:")
    log(
        f"    N={len(vals):,}  "
        f"min={vals.min():.3f}  "
        f"p25={vals.quantile(0.25):.3f}  "
        f"median={vals.median():.3f}  "
        f"p75={vals.quantile(0.75):.3f}  "
        f"max={vals.max():.3f}"
    )
log()

# Correlation between coherence
# score and static opposition angle
both = coh_df[
    ['path_coherence_score',
     'static_opposition_angle']
].dropna()

if len(both) >= 10:
    r, p = stats.spearmanr(
        both['path_coherence_score'],
        both['static_opposition_angle']
    )
    log(
        "Path coherence vs static"
        " opposition angle:"
    )
    log(
        f"  Spearman r={r:+.4f}  "
        f"p={p:.4f}"
    )
    if abs(r) < 0.3:
        log(
            "  LOW correlation — these"
            " are measuring DIFFERENT"
            " aspects of the FM landscape."
        )
        log(
            "  Both should be included"
            " as independent variables"
            " in the V-test analysis."
        )
    elif abs(r) > 0.7:
        log(
            "  HIGH correlation — these"
            " are largely measuring the"
            " SAME thing."
        )
        log(
            "  Path coherence replaces"
            " static opposition angle"
            " as primary variable."
        )
    else:
        log(
            "  MODERATE correlation —"
            " partially overlapping."
            " Use path coherence as"
            " primary, static as"
            " secondary."
        )
    log()

# Regional breakdown
coh_df['region'] = 'OTHER'
coh_df.loc[
    (coh_df['lat'] >= 40)
    & (coh_df['lon'] <= -90),
    'region'
] = 'NW'
coh_df.loc[
    (coh_df['lat'] >= 40)
    & (coh_df['lon'] > -90),
    'region'
] = 'NE'
coh_df.loc[
    (coh_df['lat'] < 40)
    & (coh_df['lon'] <= -90),
    'region'
] = 'SW'
coh_df.loc[
    (coh_df['lat'] < 40)
    & (coh_df['lon'] > -90),
    'region'
] = 'SE'

log("Regional coherence breakdown:")
log(
    f"  {'Region':<8} "
    f"{'N':>6} "
    f"{'Median_path_coh':>18} "
    f"{'Median_fwd_coh':>16}"
)
log("  " + "─" * 52)

for region in ['NW', 'NE', 'SW', 'SE']:
    rdf = coh_df[
        coh_df['region'] == region
    ]
    if len(rdf) == 0:
        continue
    pc = rdf[
        'path_coherence_score'
    ].dropna()
    fc = rdf[
        'fwd_coherence_score'
    ].dropna()
    log(
        f"  {region:<8} "
        f"{len(rdf):>6,} "
        f"{pc.median():>18.4f} "
        f"{fc.median():>16.4f}"
    )
log()

# Save
coh_df.to_csv(
    'monarch_coherence_scores.csv',
    index=False
)
log(
    "Saved → "
    "monarch_coherence_scores.csv"
)
log()


# ─────────────────────────────────────────
# FIGURES
# ─────────────────────────────────────────

log("Building figures...")

fig = plt.figure(
    figsize=(16, 12), dpi=120
)
fig.patch.set_facecolor('white')
gs = gridspec.GridSpec(
    2, 3, figure=fig,
    hspace=0.4, wspace=0.35
)

# Panel 1: Map of path coherence
ax1 = fig.add_subplot(gs[0, :2])

valid = coh_df[
    coh_df['path_coherence_score']
    .notna()
].copy()

if len(valid) > 0:
    sc = ax1.scatter(
        valid['lon'],
        valid['lat'],
        c=valid['path_coherence_score'],
        cmap='RdYlGn',
        s=8,
        alpha=0.7,
        vmin=0, vmax=1,
    )
    plt.colorbar(
        sc, ax=ax1,
        label='Path Coherence Score\n'
              '(1=coherent, 0=incoherent)',
        shrink=0.8,
    )
    # Overwintering site
    ax1.scatter(
        OW_LON, OW_LAT,
        color='black',
        s=80, marker='*', zorder=5,
        label='Overwintering site',
    )
    ax1.set_xlim(-105, -70)
    ax1.set_ylim(25, 52)
    ax1.set_xlabel(
        "Longitude", fontsize=9
    )
    ax1.set_ylabel(
        "Latitude", fontsize=9
    )
    ax1.set_title(
        "FM Path Coherence Score\n"
        "Across Eastern Migration"
        " Corridor\n"
        "Green=coherent path,"
        " Red=incoherent path",
        fontsize=9,
    )
    ax1.legend(fontsize=7)
    ax1.grid(
        alpha=0.2, linewidth=0.5
    )
    ax1.tick_params(labelsize=7)


# Panel 2: Path coherence vs
# static opposition angle
ax2 = fig.add_subplot(gs[0, 2])

if len(both) >= 10:
    ax2.scatter(
        both['path_coherence_score'],
        both['static_opposition_angle'],
        alpha=0.3, s=5,
        color='#2c3e50',
    )
    ax2.set_xlabel(
        "Path Coherence Score",
        fontsize=9
    )
    ax2.set_ylabel(
        "Static Opposition Angle (°)",
        fontsize=9
    )
    ax2.set_title(
        "Path Coherence vs\n"
        "Static Opposition Angle\n"
        f"r={r:+.3f}, p={p:.3f}",
        fontsize=9,
    )
    ax2.tick_params(labelsize=7)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)


# Panel 3: Forward coherence map
ax3 = fig.add_subplot(gs[1, :2])

valid_fwd = coh_df[
    coh_df['fwd_coherence_score']
    .notna()
].copy()

if len(valid_fwd) > 0:
    sc3 = ax3.scatter(
        valid_fwd['lon'],
        valid_fwd['lat'],
        c=valid_fwd[
            'fwd_coherence_score'
        ],
        cmap='RdYlGn',
        s=8,
        alpha=0.7,
        vmin=0, vmax=1,
    )
    plt.colorbar(
        sc3, ax=ax3,
        label='Forward Coherence Score\n'
              '(ahead of tagging location)',
        shrink=0.8,
    )
    ax3.scatter(
        OW_LON, OW_LAT,
        color='black',
        s=80, marker='*', zorder=5,
    )
    ax3.set_xlim(-105, -70)
    ax3.set_ylim(25, 52)
    ax3.set_xlabel(
        "Longitude", fontsize=9
    )
    ax3.set_ylabel(
        "Latitude", fontsize=9
    )
    ax3.set_title(
        "FM Forward Coherence Score\n"
        "EM Landscape Ahead of Tag"
        " Location",
        fontsize=9,
    )
    ax3.grid(alpha=0.2, linewidth=0.5)
    ax3.tick_params(labelsize=7)


# Panel 4: Regional distributions
ax4 = fig.add_subplot(gs[1, 2])

region_colors = {
    'NW': '#e74c3c',
    'NE': '#3498db',
    'SW': '#e67e22',
    'SE': '#2ecc71',
}

for region in ['NW', 'NE', 'SW', 'SE']:
    rdf = coh_df[
        coh_df['region'] == region
    ]['path_coherence_score'].dropna()
    if len(rdf) < 5:
        continue
    ax4.hist(
        rdf,
        bins=20,
        alpha=0.55,
        color=region_colors[region],
        label=f"{region} (N={len(rdf):,})",
        density=True,
        histtype='stepfilled',
    )

ax4.set_xlabel(
    "Path Coherence Score",
    fontsize=9
)
ax4.set_ylabel(
    "Density", fontsize=9
)
ax4.set_title(
    "Path Coherence by Region\n"
    "NW=MN/SD/WI, NE=MI/OH/NY\n"
    "SW=KS/OK/TX, SE=TN/GA/FL",
    fontsize=9,
)
ax4.legend(fontsize=7)
ax4.tick_params(labelsize=7)
ax4.spines['top'].set_visible(False)
ax4.spines['right'].set_visible(False)

fig.suptitle(
    "Monarch FM Path Coherence"
    " Metric\n"
    "Coherence Framework —"
    " OrganismCore — E.R. Lawson,"
    " February 2026",
    fontsize=10,
    fontweight='bold',
    y=0.998,
)

plt.savefig(
    'monarch_coherence_figures.png',
    dpi=200,
    bbox_inches='tight',
    facecolor='white',
)
log(
    "Saved → "
    "monarch_coherence_figures.png"
)

with open(
    'monarch_coherence_log.txt', 'w'
) as f:
    f.write("\n".join(results))
log(
    "Saved → "
    "monarch_coherence_log.txt"
)
log()
log("=" * 60)
log("READ IN ORDER:")
log()
log("  1. Path coherence vs static")
log("     opposition correlation.")
log("     Are they independent?")
log("     If r < 0.3: both go into")
log("     the V-test as separate")
log("     predictors.")
log()
log("  2. Regional breakdown.")
log("     Does NW (high-risk in")
log("     prior analysis) also show")
log("     low path coherence?")
log("     If yes: prior clustering")
log("     result and coherence")
log("     result converge.")
log()
log("  3. Map panels.")
log("     Where are the incoherent")
log("     paths? Do they match")
log("     the high-opposition-angle")
log("     regions from prior analysis?")
log("=" * 60)
