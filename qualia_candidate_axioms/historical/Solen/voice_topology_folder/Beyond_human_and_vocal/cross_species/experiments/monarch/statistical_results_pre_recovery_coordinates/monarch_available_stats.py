"""
MONARCH FM FALSE ATTRACTOR —
AVAILABLE STATISTICAL TESTS
Runs on monarch_with_fm.csv
without recovery coordinates.

Four tests:

TEST 1: Rayleigh test on FM
  false attractor bearing
  distribution across all
  3,074 unique tagging locations.
  Question: is the FM false
  attractor bearing distribution
  non-uniform across the migration
  corridor?

TEST 2: Watson-Williams test —
  Oklahoma vs Ontario.
  Question: are FM false attractor
  bearing distributions statistically
  different between the highest-
  opposition state (OK) and the
  lowest-opposition state (ON)?
  Establishes the dose contrast
  for the recovery analysis.

TEST 3: Circular-linear
  correlation — FM strength
  vs FM opposition angle.
  Question: do high-strength
  false attractors co-vary with
  high opposition angles?
  Characterizes co-distribution
  of the two risk factors.

TEST 4: Monte Carlo permutation
  test on high-risk cluster
  geography.
  Question: is the geographic
  clustering of high-risk
  tagging locations statistically
  significant or explainable by
  the distribution of tagging
  effort alone?

All results are EXPLORATORY
and DESCRIPTIVE.
None of these are the primary
pre-registered hypothesis test.
None involve recovery coordinates.
All are pre-registered as
secondary or exploratory in
the OSF registration filed
February 26, 2026.

Input:
  monarch_with_fm.csv

Output:
  monarch_available_stats_results.txt
  monarch_available_stats_figures.png

Requirements:
  pip install pandas numpy scipy
      matplotlib pingouin
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy import stats
from scipy.stats import chi2
import warnings
warnings.filterwarnings('ignore')

# Try pingouin for Watson-Williams
try:
    import pingouin as pg
    HAS_PINGOUIN = True
except ImportError:
    HAS_PINGOUIN = False
    print("pingouin not found.")
    print("Install with: pip install pingouin")
    print("Watson-Williams test will use")
    print("manual implementation instead.")


# ─────────────────────────────────────────
# CIRCULAR STATISTICS UTILITIES
# ─────────────────────────────────────────

def deg2rad(d):
    return np.radians(np.asarray(d,
                                  dtype=float))

def rad2deg(r):
    return np.degrees(r) % 360

def circular_mean(angles_deg):
    """Mean direction of circular data."""
    r = deg2rad(angles_deg)
    return rad2deg(np.arctan2(
        np.mean(np.sin(r)),
        np.mean(np.cos(r))
    ))

def mean_resultant_length(angles_deg):
    """
    R-bar: mean resultant length.
    0 = uniform distribution.
    1 = all angles identical.
    """
    r = deg2rad(angles_deg)
    C = np.mean(np.cos(r))
    S = np.mean(np.sin(r))
    return np.sqrt(C**2 + S**2)

def rayleigh_test(angles_deg):
    """
    Rayleigh test for uniformity
    of circular distribution.
    H0: distribution is uniform.
    Returns: (R_bar, z_statistic, p_value)
    """
    n = len(angles_deg)
    R_bar = mean_resultant_length(
        angles_deg
    )
    R = n * R_bar
    z = R**2 / n

    # P-value approximation
    # (Zar 1999, accurate for n>=10)
    p = np.exp(
        np.sqrt(1 + 4*n + 4*(n**2 - R**2))
        - (1 + 2*n)
    )
    # Clip to valid range
    p = float(np.clip(p, 0, 1))
    return R_bar, z, p

def circular_diff(a, b):
    """
    Signed circular difference a - b.
    Result in range -180 to +180.
    """
    d = (np.asarray(a, float) -
         np.asarray(b, float) + 180
         ) % 360 - 180
    return d

def watson_williams_test(group1_deg,
                          group2_deg):
    """
    Watson-Williams two-sample test
    for equal mean directions.
    H0: mean directions are equal.
    Returns: (F_stat, p_value,
              mean1, mean2, diff)
    """
    def kappa_mle(R_bar, n):
        """
        MLE of kappa (concentration)
        from R_bar.
        Approximation from
        Mardia & Jupp 2000.
        """
        if R_bar < 0.53:
            k = 2*R_bar + R_bar**3 + \
                5*R_bar**5/6
        elif R_bar < 0.85:
            k = -0.4 + 1.39*R_bar + \
                0.43/(1-R_bar)
        else:
            k = 1/(R_bar**3 - \
                   4*R_bar**2 + \
                   3*R_bar)
        return k

    n1 = len(group1_deg)
    n2 = len(group2_deg)
    n = n1 + n2

    R1 = n1 * mean_resultant_length(
        group1_deg
    )
    R2 = n2 * mean_resultant_length(
        group2_deg
    )

    # Pooled
    combined = np.concatenate([
        group1_deg, group2_deg
    ])
    R = n * mean_resultant_length(combined)

    R_bar_pooled = (R1 + R2) / n
    kappa = kappa_mle(R_bar_pooled / n,
                       n)

    # Correction factor
    if kappa > 2:
        corr = 1 + 3/(8*kappa)
    else:
        corr = 1.0

    # F statistic
    F = corr * (n - 2) * \
        (R1 + R2 - R) / \
        (n - R1 - R2)
    F = max(F, 0)

    # P-value: F(1, n-2)
    p = 1 - stats.f.cdf(F, 1, n-2)

    mean1 = circular_mean(group1_deg)
    mean2 = circular_mean(group2_deg)
    diff = circular_diff(mean1, mean2)

    return F, p, mean1, mean2, diff

def circular_linear_correlation(
        angles_deg, linear_vals):
    """
    Circular-linear correlation
    (Mardia 1976 method).
    Tests association between a
    circular variable and a
    linear variable.
    Returns: (r_cl, F_stat, p_value)
    """
    a = deg2rad(angles_deg)
    x = np.asarray(linear_vals,
                    dtype=float)
    n = len(a)

    r_xc = np.corrcoef(x,
                        np.cos(a))[0, 1]
    r_xs = np.corrcoef(x,
                        np.sin(a))[0, 1]
    r_cs = np.corrcoef(
        np.cos(a), np.sin(a)
    )[0, 1]

    r_cl2 = (r_xc**2 + r_xs**2 -
             2*r_xc*r_xs*r_cs) / \
            (1 - r_cs**2)
    r_cl2 = float(np.clip(r_cl2, 0, 1))
    r_cl = np.sqrt(r_cl2)

    F = (n - 3) * r_cl2 / \
        (2 * (1 - r_cl2))
    F = max(F, 0)
    p = 1 - stats.f.cdf(F, 2, n-3)

    return r_cl, F, p


# ─────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────

print("=" * 52)
print("MONARCH FM FALSE ATTRACTOR")
print("AVAILABLE STATISTICAL TESTS")
print("=" * 52)
print()
print("Loading monarch_with_fm.csv...")

df = pd.read_csv(
    "monarch_with_fm.csv",
    low_memory=False
)
print(f"  Records loaded: {len(df):,}")

# Unique tagging locations
# with valid FM data
unique = df.dropna(
    subset=[
        'fm_false_attractor_bearing',
        'fm_false_attractor_strength',
        'expected_bearing',
        'tag_lat', 'tag_lon'
    ]
).drop_duplicates(
    subset=['tag_lat', 'tag_lon']
).copy()

# Opposition angle
unique['fm_opposition'] = np.abs(
    circular_diff(
        unique['fm_false_attractor_bearing'],
        unique['expected_bearing']
    )
)

print(f"  Unique locations: {len(unique):,}")
print()

# ─────────────────────────────────────────
# RESULTS COLLECTOR
# ─────────────────────────────────────────

results = []

def log(line=""):
    results.append(line)
    print(line)


# ──��──────────────────────────────────────
# TEST 1: RAYLEIGH TEST ON FM FALSE
# ATTRACTOR BEARING DISTRIBUTION
# ─────────────────────────────────────────

log("=" * 52)
log("TEST 1: RAYLEIGH TEST")
log("FM False Attractor Bearing")
log("Distribution — All Unique")
log("Tagging Locations")
log("=" * 52)
log()
log("H0: FM false attractor bearings")
log("    are uniformly distributed")
log("    across all compass directions.")
log()
log("H1: FM false attractor bearings")
log("    are non-uniformly distributed,")
log("    indicating systematic bias in")
log("    the FM infrastructure relative")
log("    to the migration corridor.")
log()

bearings = unique[
    'fm_false_attractor_bearing'
].values

n1 = len(bearings)
R_bar1, z1, p1 = rayleigh_test(bearings)
mean_dir1 = circular_mean(bearings)

log(f"N locations:          {n1:,}")
log(f"Mean resultant length R̄: "
    f"{R_bar1:.4f}")
log(f"Mean direction:       "
    f"{mean_dir1:.1f}°")
log(f"Rayleigh z:           {z1:.4f}")
log(f"p-value:              {p1:.6f}")
log()

if p1 < 0.001:
    sig = "p < 0.001 — HIGHLY SIGNIFICANT"
elif p1 < 0.01:
    sig = "p < 0.01 — SIGNIFICANT"
elif p1 < 0.05:
    sig = "p < 0.05 — SIGNIFICANT"
else:
    sig = "p >= 0.05 — NOT SIGNIFICANT"

log(f"Result: {sig}")
log()

# Cardinal direction of mean
dirs = ['N','NNE','NE','ENE','E','ESE',
        'SE','SSE','S','SSW','SW','WSW',
        'W','WNW','NW','NNW']
card = dirs[int((mean_dir1 + 11.25)
               / 22.5) % 16]
log(f"Mean FM false attractor bearing")
log(f"across migration corridor:")
log(f"  {mean_dir1:.1f}° ({card})")
log()
log("Interpretation:")
log("  Non-uniform distribution means")
log("  the FM infrastructure is not")
log("  randomly oriented relative to")
log("  tagging locations — it shows")
log("  systematic directional bias.")
log()

# Also test opposition angles
# as a circular variable
opp_angles = unique['fm_opposition'].values
# Convert to circular (0-180° → doubled
# to use full circle for Rayleigh)
opp_doubled = opp_angles * 2
R_bar_opp, z_opp, p_opp = rayleigh_test(
    opp_doubled
)

log("Supplementary: Rayleigh test on")
log("FM opposition angle distribution")
log("(opposition angles doubled to")
log(" use full circular range):")
log(f"  N: {len(opp_angles):,}")
log(f"  Mean opposition: "
    f"{np.mean(opp_angles):.1f}°")
log(f"  R̄ (doubled): {R_bar_opp:.4f}")
log(f"  p-value: {p_opp:.6f}")
log()


# ─────────────────────────────────────────
# TEST 2: WATSON-WILLIAMS TEST
# OKLAHOMA vs ONTARIO
# ─────────────────────────────────────────

log("=" * 52)
log("TEST 2: WATSON-WILLIAMS TEST")
log("Oklahoma vs Ontario")
log("FM False Attractor Bearing")
log("Distributions")
log("=" * 52)
log()
log("H0: Mean FM false attractor bearing")
log("    is equal in Oklahoma and Ontario.")
log()
log("H1: Mean FM false attractor bearing")
log("    differs between the highest-")
log("    opposition state (OK, 142.6°)")
log("    and lowest-opposition state")
log("    (ON, 49.5°), establishing the")
log("    dose contrast for the recovery")
log("    analysis.")
log()

# Get state-level data from full
# dataset (not just unique locations)
ok_df = df[
    df['stateProvince'] == 'OK'
].dropna(
    subset=['fm_false_attractor_bearing']
)
on_df = df[
    df['stateProvince'] == 'ON'
].dropna(
    subset=['fm_false_attractor_bearing']
)

# Use unique locations per state
# for the circular test
ok_unique = ok_df.drop_duplicates(
    subset=['tag_lat', 'tag_lon']
)
on_unique = on_df.drop_duplicates(
    subset=['tag_lat', 'tag_lon']
)

ok_bearings = ok_unique[
    'fm_false_attractor_bearing'
].values
on_bearings = on_unique[
    'fm_false_attractor_bearing'
].values

log(f"Oklahoma unique locations: "
    f"{len(ok_bearings):,}")
log(f"Ontario unique locations:  "
    f"{len(on_bearings):,}")
log()

# Individual Rayleigh tests
R_bar_ok, z_ok, p_ok = rayleigh_test(
    ok_bearings
)
R_bar_on, z_on, p_on = rayleigh_test(
    on_bearings
)
mean_ok = circular_mean(ok_bearings)
mean_on = circular_mean(on_bearings)

log(f"Oklahoma:")
log(f"  Mean FM bearing: {mean_ok:.1f}°")
log(f"  R̄: {R_bar_ok:.4f}")
log(f"  Rayleigh p: {p_ok:.6f}")
log()
log(f"Ontario:")
log(f"  Mean FM bearing: {mean_on:.1f}°")
log(f"  R̄: {R_bar_on:.4f}")
log(f"  Rayleigh p: {p_on:.6f}")
log()

# Watson-Williams test
F2, p2, m1, m2, diff2 = \
    watson_williams_test(
        ok_bearings, on_bearings
    )

log(f"Watson-Williams test:")
log(f"  F(1, {len(ok_bearings)+len(on_bearings)-2})"
    f" = {F2:.4f}")
log(f"  p-value: {p2:.6f}")
log()

if p2 < 0.001:
    sig2 = "p < 0.001 — HIGHLY SIGNIFICANT"
elif p2 < 0.01:
    sig2 = "p < 0.01 — SIGNIFICANT"
elif p2 < 0.05:
    sig2 = "p < 0.05 — SIGNIFICANT"
else:
    sig2 = "p >= 0.05 — NOT SIGNIFICANT"

log(f"Result: {sig2}")
log()

# Compute mean expected bearing
# per state for context
ok_exp = df[
    df['stateProvince'] == 'OK'
]['expected_bearing'].mean()
on_exp = df[
    df['stateProvince'] == 'ON'
]['expected_bearing'].mean()

log("Context:")
log(f"  OK mean expected bearing: "
    f"{ok_exp:.1f}°")
log(f"  OK mean FM bearing:       "
    f"{mean_ok:.1f}°")
log(f"  OK mean opposition:       "
    f"{abs(circular_diff(mean_ok, ok_exp)):.1f}°")
log()
log(f"  ON mean expected bearing: "
    f"{on_exp:.1f}°")
log(f"  ON mean FM bearing:       "
    f"{mean_on:.1f}°")
log(f"  ON mean opposition:       "
    f"{abs(circular_diff(mean_on, on_exp)):.1f}°")
log()
log("Interpretation:")
log("  A significant Watson-Williams")
log("  result confirms that OK and ON")
log("  monarchs face statistically")
log("  distinct FM false attractor")
log("  environments — establishing")
log("  the dose contrast that will")
log("  be used in the recovery")
log("  bearing analysis.")
log()

# Extended: all top states
log("Extended: Rayleigh test by state")
log("(top 10 states by tagging volume)")
log()
log(f"{'State':<8} {'N_locs':>6} "
    f"{'Mean_FM':>8} {'R_bar':>6} "
    f"{'p':>10} {'Mean_exp':>9} "
    f"{'Opp':>6}")
log("-" * 58)

top_states = (
    df.groupby('stateProvince')
    .size()
    .sort_values(ascending=False)
    .head(10)
    .index.tolist()
)

state_results = []
for st in top_states:
    st_df = df[
        df['stateProvince'] == st
    ].dropna(
        subset=['fm_false_attractor_bearing',
                'expected_bearing']
    ).drop_duplicates(
        subset=['tag_lat', 'tag_lon']
    )
    if len(st_df) < 5:
        continue
    b = st_df[
        'fm_false_attractor_bearing'
    ].values
    e = st_df['expected_bearing'].values
    Rb, zb, pb = rayleigh_test(b)
    mb = circular_mean(b)
    me = np.mean(e)
    opp = abs(circular_diff(mb, me))
    log(f"{st:<8} {len(b):>6} "
        f"{mb:>8.1f}° {Rb:>6.3f} "
        f"{pb:>10.6f} {me:>8.1f}° "
        f"{opp:>5.1f}°")
    state_results.append({
        'state': st,
        'n_locs': len(b),
        'mean_fm_bearing': mb,
        'R_bar': Rb,
        'p_rayleigh': pb,
        'mean_expected': me,
        'opposition': opp
    })
log()


# ─────────────────────────────────────────
# TEST 3: CIRCULAR-LINEAR CORRELATION
# FM STRENGTH vs FM OPPOSITION ANGLE
# ─────────────────────────────────────────

log("=" * 52)
log("TEST 3: CIRCULAR-LINEAR")
log("CORRELATION")
log("FM Strength vs FM Opposition")
log("Angle")
log("=" * 52)
log()
log("Question: do locations with")
log("stronger FM false attractor")
log("signals (higher strength) tend")
log("to have higher opposition angles")
log("— i.e., are the two risk factors")
log("(strong signal AND wrong direction)")
log("co-distributed geographically?")
log()
log("A positive correlation means")
log("high-strength attractors tend to")
log("point in more-opposed directions.")
log("A near-zero correlation means the")
log("two risk factors are independent.")
log()

# Use unique locations
strength_vals = unique[
    'fm_false_attractor_strength'
].values
opp_vals = unique[
    'fm_opposition'
].values

# Pearson correlation (linear)
r_pearson, p_pearson = stats.pearsonr(
    strength_vals, opp_vals
)
log(f"N unique locations: {len(strength_vals):,}")
log()
log("Linear (Pearson) correlation")
log("  FM strength vs opposition angle:")
log(f"  r = {r_pearson:.4f}")
log(f"  p = {p_pearson:.6f}")
log()

# Spearman (rank, more robust)
r_spearman, p_spearman = stats.spearmanr(
    strength_vals, opp_vals
)
log("Rank (Spearman) correlation")
log("  FM strength vs opposition angle:")
log(f"  rho = {r_spearman:.4f}")
log(f"  p = {p_spearman:.6f}")
log()

# Circular-linear correlation
# Opposition as circular variable
r_cl3, F3, p3 = circular_linear_correlation(
    opp_vals, strength_vals
)
log("Circular-linear correlation")
log("  (Mardia 1976 method):")
log(f"  r_cl = {r_cl3:.4f}")
log(f"  F = {F3:.4f}")
log(f"  p = {p3:.6f}")
log()

if p3 < 0.05:
    log("Result: SIGNIFICANT circular-")
    log("linear association between FM")
    log("strength and opposition angle.")
else:
    log("Result: No significant circular-")
    log("linear association detected.")
log()

# Quartile breakdown
log("FM strength quartile breakdown")
log("(pre-registered boundaries):")
log()
boundaries = [0.012318, 0.018706, 0.024320]
unique['fm_q'] = pd.cut(
    unique['fm_false_attractor_strength'],
    bins=[-np.inf] + boundaries + [np.inf],
    labels=['Q1', 'Q2', 'Q3', 'Q4']
)

log(f"{'Quartile':<10} {'N':>6} "
    f"{'Mean_opp':>10} "
    f"{'Median_opp':>12} "
    f"{'Mean_str':>10}")
log("-" * 52)
for q in ['Q1', 'Q2', 'Q3', 'Q4']:
    qdf = unique[unique['fm_q'] == q]
    if len(qdf) == 0:
        continue
    log(f"{q:<10} {len(qdf):>6} "
        f"{qdf['fm_opposition'].mean():>9.1f}° "
        f"{qdf['fm_opposition'].median():>11.1f}° "
        f"{qdf['fm_false_attractor_strength'].mean():>10.4f}")
log()
log("Interpretation:")
log("  If high-strength FM signals")
log("  (Q4) show higher mean opposition")
log("  than low-strength signals (Q1),")
log("  the two risk factors co-vary —")
log("  the most disruptive locations")
log("  are also the most misdirecting.")
log()


# ─────────────────────────────────────────
# TEST 4: MONTE CARLO PERMUTATION TEST
# ON HIGH-RISK CLUSTER GEOGRAPHY
# ─────────────────────────────────────────

log("=" * 52)
log("TEST 4: MONTE CARLO PERMUTATION")
log("TEST")
log("Geographic Clustering of")
log("High-Risk Locations")
log("=" * 52)
log()
log("Question: is the geographic")
log("concentration of high-risk")
log("tagging locations (opposition")
log("> 120°, strength > 0.01) more")
log("clustered than expected by chance")
log("given the distribution of all")
log("tagging effort?")
log()
log("Method: permute FM false attractor")
log("bearings and strengths across all")
log("3,074 unique locations 10,000 times.")
log("Each permutation computes the")
log("high-risk location count within")
log("each of 4 geographic quadrants.")
log("Compare observed quadrant counts")
log("to the permutation null distribution.")
log()

N_PERM = 10000

# Define 4 geographic quadrants
# centered on the migration corridor
# NW: MN/SD/ND area
# NE: MA/CT/NJ/NY
# SC: OK/KS/TX
# SE: SC/FL/GA
quadrants = {
    'NW (MN/SD/WI)':
        (unique['tag_lat'] >= 42) &
        (unique['tag_lon'] <= -88),
    'NE (MA/CT/NJ/NY)':
        (unique['tag_lat'] >= 40) &
        (unique['tag_lon'] >= -76),
    'Central (OK/KS/TX)':
        (unique['tag_lat'] < 42) &
        (unique['tag_lat'] >= 29) &
        (unique['tag_lon'] <= -94),
    'SE (SC/FL/GA)':
        (unique['tag_lat'] < 36) &
        (unique['tag_lon'] >= -84),
}

# Observed high-risk flag
def is_high_risk(opp, strength):
    return (opp > 120) & (strength > 0.01)

hr_flag = is_high_risk(
    unique['fm_opposition'].values,
    unique['fm_false_attractor_strength'].values
)

log(f"Observed high-risk locations: "
    f"{hr_flag.sum():,} / "
    f"{len(hr_flag):,} "
    f"({100*hr_flag.mean():.1f}%)")
log()
log("Observed high-risk count by")
log("geographic quadrant:")
log()

obs_counts = {}
for qname, qmask in quadrants.items():
    obs = (hr_flag & qmask.values).sum()
    total = qmask.values.sum()
    obs_counts[qname] = obs
    log(f"  {qname}:")
    log(f"    High-risk: {obs} / {total} "
        f"({100*obs/max(total,1):.1f}%)")
log()

# Permutation
print("  Running 10,000 permutations...")
print("  (this takes ~20 seconds)")

bearings_perm = unique[
    'fm_false_attractor_bearing'
].values.copy()
strengths_perm = unique[
    'fm_false_attractor_strength'
].values.copy()
opp_perm_base = unique[
    'fm_opposition'
].values.copy()

# Precompute quadrant masks
q_masks = {
    qname: qmask.values
    for qname, qmask in quadrants.items()
}

perm_counts = {
    qname: np.zeros(N_PERM, dtype=int)
    for qname in quadrants
}

rng = np.random.default_rng(42)

for i in range(N_PERM):
    # Shuffle both bearing and strength
    # together (preserve their pairing)
    idx = rng.permutation(len(unique))
    shuf_b = bearings_perm[idx]
    shuf_s = strengths_perm[idx]

    # Recompute opposition with shuffled
    # FM bearings (expected bearing fixed)
    exp_b = unique['expected_bearing'].values
    shuf_opp = np.abs(
        circular_diff(shuf_b, exp_b)
    )
    shuf_hr = is_high_risk(shuf_opp, shuf_s)

    for qname, qmask in q_masks.items():
        perm_counts[qname][i] = (
            shuf_hr & qmask
        ).sum()

    if (i+1) % 2000 == 0:
        print(f"    {i+1:,} / {N_PERM:,}")

print()
log("Permutation test results:")
log()
log(f"{'Quadrant':<28} "
    f"{'Observed':>9} "
    f"{'Perm_mean':>10} "
    f"{'Perm_SD':>8} "
    f"{'p-value':>9}")
log("-" * 68)

perm_results = {}
for qname in quadrants:
    obs = obs_counts[qname]
    perm = perm_counts[qname]
    perm_mean = perm.mean()
    perm_sd = perm.std()
    # One-tailed: p(observed >= perm)
    p4 = (perm >= obs).mean()
    perm_results[qname] = {
        'observed': obs,
        'perm_mean': perm_mean,
        'perm_sd': perm_sd,
        'p': p4
    }
    sig_flag = (
        " ***" if p4 < 0.001 else
        " **"  if p4 < 0.01  else
        " *"   if p4 < 0.05  else
        ""
    )
    log(f"{qname:<28} "
        f"{obs:>9} "
        f"{perm_mean:>10.1f} "
        f"{perm_sd:>8.2f} "
        f"{p4:>9.4f}{sig_flag}")

log()
log("* p<0.05  ** p<0.01  *** p<0.001")
log()
log("Interpretation:")
log("  Significant quadrants show more")
log("  high-risk locations than expected")
log("  by chance given the tagging effort")
log("  distribution. This means the FM")
log("  infrastructure in those regions")
log("  is genuinely more opposed to")
log("  migration than a random FM")
log("  landscape would be.")
log()


# ─────────────────────────────────────────
# SUMMARY TABLE
# ─────────────────────────────────────────

log("=" * 52)
log("SUMMARY OF ALL FOUR TESTS")
log("=" * 52)
log()
log(f"{'Test':<40} {'Result':<14} {'p':>10}")
log("-" * 66)
log(f"{'1. Rayleigh — FM bearing dist':<40} "
    f"{'SIGNIFICANT' if p1<0.05 else 'NS':<14} "
    f"{p1:>10.6f}")
log(f"{'2. Watson-Williams — OK vs ON':<40} "
    f"{'SIGNIFICANT' if p2<0.05 else 'NS':<14} "
    f"{p2:>10.6f}")
log(f"{'3. Circ-lin corr — str vs opp':<40} "
    f"{'SIGNIFICANT' if p3<0.05 else 'NS':<14} "
    f"{p3:>10.6f}")

# Summarize Test 4
any_sig4 = any(
    v['p'] < 0.05
    for v in perm_results.values()
)
min_p4 = min(
    v['p'] for v in perm_results.values()
)
log(f"{'4. Permutation — cluster geo':<40} "
    f"{'SIGNIFICANT' if any_sig4 else 'NS':<14} "
    f"{min_p4:>10.4f}")
log()
log("NOTE: All four tests are exploratory")
log("and descriptive. None are the")
log("primary pre-registered hypothesis")
log("test. All run on tagging data only.")
log("The primary V-test requires recovery")
log("coordinates (Monarch Watch pending).")
log()


# ─────────────────────────────────────────
# SAVE TEXT RESULTS
# ─────────────────────────────────────────

with open(
    "monarch_available_stats_results.txt",
    "w"
) as f:
    f.write("\n".join(results))
print("Saved → monarch_available_stats"
      "_results.txt")


# ─────────────────────────────────────────
# FIGURES
# ─────────────────────────────────────────

print()
print("Building figures...")

fig = plt.figure(figsize=(18, 14),
                  dpi=120)
fig.patch.set_facecolor('white')

gs = gridspec.GridSpec(
    2, 3,
    figure=fig,
    hspace=0.38,
    wspace=0.32
)

ax1 = fig.add_subplot(
    gs[0, 0], projection='polar'
)
ax2 = fig.add_subplot(gs[0, 1])
ax3 = fig.add_subplot(gs[0, 2])
ax4 = fig.add_subplot(gs[1, 0])
ax5 = fig.add_subplot(gs[1, 1])
ax6 = fig.add_subplot(gs[1, 2])

# ── Figure 1A: Circular histogram
# of FM false attractor bearings ──
ax1.set_theta_zero_location('N')
ax1.set_theta_direction(-1)

bins = np.linspace(0, 2*np.pi, 37)
b_rad = np.radians(
    unique['fm_false_attractor_bearing']
    .values
)
counts, _ = np.histogram(b_rad, bins=bins)
bin_centers = (bins[:-1] + bins[1:]) / 2
width = bins[1] - bins[0]

bars1 = ax1.bar(
    bin_centers, counts,
    width=width,
    alpha=0.7,
    color='steelblue',
    edgecolor='white',
    linewidth=0.3
)

# Mean direction arrow
mean_rad1 = np.radians(mean_dir1)
ax1.annotate(
    '',
    xy=(mean_rad1,
        counts.max() * 0.9),
    xytext=(0, 0),
    arrowprops=dict(
        arrowstyle='-|>',
        color='red',
        lw=2.0
    )
)
ax1.set_title(
    f'Test 1: FM False Attractor\n'
    f'Bearing Distribution\n'
    f'Rayleigh p={p1:.4f}  '
    f'R̄={R_bar1:.3f}\n'
    f'Mean dir={mean_dir1:.1f}°',
    fontsize=8, pad=10
)
ax1.set_yticklabels([])

# ── Figure 1B: OK vs ON bearing
# circular histograms ──
ax2.set_aspect('equal')
ax2.set_xlim(-1.5, 1.5)
ax2.set_ylim(-1.5, 1.5)
ax2.axis('off')

# Draw two circular distributions
# as polar-style on a flat axis
circle = plt.Circle(
    (0, 0), 1.0,
    fill=False,
    color='#cccccc',
    linewidth=0.5
)
ax2.add_patch(circle)

# Compass labels
for angle, label in zip(
    [0, 90, 180, 270],
    ['N', 'E', 'S', 'W']
):
    rad = np.radians(90 - angle)
    ax2.text(
        1.25 * np.cos(rad),
        1.25 * np.sin(rad),
        label,
        ha='center', va='center',
        fontsize=7, color='#888888'
    )

# OK mean bearing arrow
ok_rad = np.radians(90 - mean_ok)
ax2.annotate(
    '',
    xy=(0.85*np.cos(ok_rad),
        0.85*np.sin(ok_rad)),
    xytext=(0, 0),
    arrowprops=dict(
        arrowstyle='-|>',
        color='#cc2222',
        lw=2.5
    )
)
# ON mean bearing arrow
on_rad = np.radians(90 - mean_on)
ax2.annotate(
    '',
    xy=(0.85*np.cos(on_rad),
        0.85*np.sin(on_rad)),
    xytext=(0, 0),
    arrowprops=dict(
        arrowstyle='-|>',
        color='#2255cc',
        lw=2.5
    )
)
# Expected migration reference
ok_exp_rad = np.radians(90 - ok_exp)
ax2.annotate(
    '',
    xy=(0.7*np.cos(ok_exp_rad),
        0.7*np.sin(ok_exp_rad)),
    xytext=(0, 0),
    arrowprops=dict(
        arrowstyle='-|>',
        color='#22aa44',
        lw=1.5,
        linestyle='dashed'
    )
)

ax2.text(
    0, -1.45,
    f'OK mean FM: {mean_ok:.0f}°   '
    f'ON mean FM: {mean_on:.0f}°\n'
    f'Watson-Williams F={F2:.2f}  '
    f'p={p2:.4f}',
    ha='center', va='center',
    fontsize=7
)

from matplotlib.lines import Line2D
legend_els = [
    Line2D([0],[0], color='#cc2222',
           lw=2, label=f'OK FM ({mean_ok:.0f}°)'),
    Line2D([0],[0], color='#2255cc',
           lw=2, label=f'ON FM ({mean_on:.0f}°)'),
    Line2D([0],[0], color='#22aa44',
           lw=1.5, linestyle='--',
           label=f'Expected ({ok_exp:.0f}°)'),
]
ax2.legend(
    handles=legend_els,
    loc='upper right',
    fontsize=6,
    framealpha=0.8
)
ax2.set_title(
    'Test 2: Oklahoma vs Ontario\n'
    'Mean FM False Attractor Bearing',
    fontsize=8, pad=6
)

# ── Figure 1C: Strength vs
# opposition scatter ──
sample_n = min(1000, len(unique))
sample = unique.sample(
    sample_n, random_state=42
)

sc3 = ax3.scatter(
    sample['fm_false_attractor_strength'],
    sample['fm_opposition'],
    alpha=0.3,
    s=8,
    c=sample['fm_opposition'],
    cmap='RdYlGn_r',
    vmin=0, vmax=180,
    linewidths=0
)

# Trend line
z_fit = np.polyfit(
    unique['fm_false_attractor_strength'],
    unique['fm_opposition'],
    1
)
x_fit = np.linspace(
    unique['fm_false_attractor_strength'].min(),
    unique['fm_false_attractor_strength'].max(),
    100
)
ax3.plot(
    x_fit,
    np.polyval(z_fit, x_fit),
    color='black',
    linewidth=1.5,
    alpha=0.7,
    label=f'Trend (r={r_pearson:.3f})'
)

ax3.axhline(
    90, color='#888888',
    linewidth=0.8, linestyle='--',
    alpha=0.6
)
ax3.axhline(
    120, color='#cc4444',
    linewidth=0.8, linestyle='--',
    alpha=0.6
)
ax3.set_xlabel(
    'FM False Attractor Strength',
    fontsize=7
)
ax3.set_ylabel(
    'FM Opposition Angle (°)',
    fontsize=7
)
ax3.set_title(
    f'Test 3: FM Strength vs\n'
    f'Opposition Angle\n'
    f'Pearson r={r_pearson:.3f}  '
    f'p={p_pearson:.4f}\n'
    f'Spearman ρ={r_spearman:.3f}  '
    f'p={p_spearman:.4f}',
    fontsize=8, pad=6
)
ax3.legend(fontsize=6)
ax3.tick_params(labelsize=7)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)

# ── Figure 1D: Quartile opposition
# boxplot ──
quartile_data = [
    unique[unique['fm_q'] == q
           ]['fm_opposition'].values
    for q in ['Q1', 'Q2', 'Q3', 'Q4']
]

colors4 = ['#4dac26', '#b8e186',
           '#f4a582', '#d7191c']
bp = ax4.boxplot(
    quartile_data,
    patch_artist=True,
    notch=False,
    medianprops=dict(
        color='black', linewidth=1.5
    ),
    whiskerprops=dict(
        color='#555555', linewidth=0.8
    ),
    capprops=dict(
        color='#555555', linewidth=0.8
    ),
    flierprops=dict(
        marker='.',
        markerfacecolor='#aaaaaa',
        markersize=2, alpha=0.3
    )
)
for patch, color in zip(
    bp['boxes'], colors4
):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)

ax4.axhline(
    90, color='#888888',
    linewidth=0.8, linestyle='--',
    alpha=0.7, label='90° threshold'
)
ax4.set_xticklabels(
    ['Q1\n(weakest)', 'Q2', 'Q3',
     'Q4\n(strongest)'],
    fontsize=7
)
ax4.set_ylabel(
    'FM Opposition Angle (°)',
    fontsize=7
)
ax4.set_title(
    'FM Opposition by\n'
    'FM Strength Quartile\n'
    '(pre-registered boundaries)',
    fontsize=8, pad=6
)
ax4.tick_params(labelsize=7)
ax4.spines['top'].set_visible(False)
ax4.spines['right'].set_visible(False)
ax4.legend(fontsize=6)

# ── Figure 1E: Permutation test
# results ──
q_names_short = [
    'NW\n(MN/SD/WI)',
    'NE\n(MA/CT/NJ)',
    'Central\n(OK/KS/TX)',
    'SE\n(SC/FL/GA)'
]
obs_vals = [
    perm_results[q]['observed']
    for q in quadrants
]
perm_means = [
    perm_results[q]['perm_mean']
    for q in quadrants
]
perm_sds = [
    perm_results[q]['perm_sd']
    for q in quadrants
]
p_vals4 = [
    perm_results[q]['p']
    for q in quadrants
]

x4 = np.arange(4)
w = 0.35

bars_obs = ax5.bar(
    x4 - w/2, obs_vals,
    width=w,
    color='#cc2222',
    alpha=0.8,
    label='Observed',
    zorder=3
)
bars_perm = ax5.bar(
    x4 + w/2, perm_means,
    width=w,
    color='#aaaaaa',
    alpha=0.8,
    label='Permutation mean',
    zorder=3
)
ax5.errorbar(
    x4 + w/2, perm_means,
    yerr=perm_sds,
    fmt='none',
    color='#555555',
    capsize=3,
    linewidth=1,
    zorder=4
)

# Significance stars
for i, p in enumerate(p_vals4):
    star = (
        '***' if p < 0.001 else
        '**'  if p < 0.01  else
        '*'   if p < 0.05  else
        'ns'
    )
    max_h = max(
        obs_vals[i], perm_means[i]
    ) + perm_sds[i] + 1
    ax5.text(
        i, max_h + 1,
        star,
        ha='center',
        fontsize=8,
        color=(
            '#cc2222'
            if p < 0.05
            else '#888888'
        )
    )

ax5.set_xticks(x4)
ax5.set_xticklabels(
    q_names_short, fontsize=6.5
)
ax5.set_ylabel(
    'High-Risk Locations (count)',
    fontsize=7
)
ax5.set_title(
    'Test 4: Permutation Test\n'
    'High-Risk Geographic Clustering\n'
    '(10,000 permutations)',
    fontsize=8, pad=6
)
ax5.legend(fontsize=6.5)
ax5.tick_params(labelsize=7)
ax5.spines['top'].set_visible(False)
ax5.spines['right'].set_visible(False)

# ── Figure 1F: Summary panel ──
ax6.axis('off')

summary_lines = [
    "STATISTICAL SUMMARY",
    "─" * 32,
    "",
    "TEST 1: Rayleigh — FM bearing",
    f"  R̄ = {R_bar1:.4f}",
    f"  Mean dir = {mean_dir1:.1f}°",
    f"  p = {p1:.2e}",
    f"  {'SIGNIFICANT' if p1<0.05 else 'NOT SIGNIFICANT'}",
    "",
    "TEST 2: Watson-Williams OK/ON",
    f"  OK mean FM = {mean_ok:.1f}°",
    f"  ON mean FM = {mean_on:.1f}°",
    f"  F = {F2:.3f}",
    f"  p = {p2:.2e}",
    f"  {'SIGNIFICANT' if p2<0.05 else 'NOT SIGNIFICANT'}",
    "",
    "TEST 3: Strength vs Opposition",
    f"  Pearson r = {r_pearson:.4f}",
    f"  Spearman ρ = {r_spearman:.4f}",
    f"  p = {p_pearson:.2e}",
    f"  {'SIGNIFICANT' if p_pearson<0.05 else 'NOT SIGNIFICANT'}",
    "",
    "TEST 4: Permutation Clustering",
    f"  Most sig quadrant p={min_p4:.4f}",
    f"  {'SIGNIFICANT' if any_sig4 else 'NOT SIGNIFICANT'}",
    "",
    "─" * 32,
    "ALL: Tagging data only.",
    "PRIMARY V-TEST: pending",
    "Monarch Watch recovery data.",
]

for i, line in enumerate(summary_lines):
    weight = (
        'bold'
        if i in [0, 7, 14, 21, 26]
        else 'normal'
    )
    color = (
        '#cc2222'
        if 'SIGNIFICANT' in line
        and 'NOT' not in line
        and 'PRIMARY' not in line
        else '#888888'
        if 'NOT SIGNIFICANT' in line
        or 'pending' in line
        else 'black'
    )
    ax6.text(
        0.05, 0.97 - i*0.048,
        line,
        transform=ax6.transAxes,
        fontsize=7,
        fontfamily='monospace',
        color=color,
        fontweight=weight,
        va='top'
    )

# Figure title
fig.suptitle(
    'Monarch FM False Attractor — '
    'Available Statistical Tests\n'
    '(Tagging Data Only — '
    'Pre-Recovery-Data Results)\n'
    'OrganismCore — E.R. Lawson, '
    'February 2026',
    fontsize=10,
    fontweight='bold',
    y=0.99
)

plt.savefig(
    'monarch_available_stats_figures.png',
    dpi=200,
    bbox_inches='tight',
    facecolor='white'
)
print("Saved → monarch_available_stats"
      "_figures.png")
print()
print("Done.")
print()
print("Files saved:")
print("  monarch_available_stats_"
      "results.txt")
print("  monarch_available_stats_"
      "figures.png")
print()
print("Primary V-test: pending")
print("Monarch Watch recovery data.")
