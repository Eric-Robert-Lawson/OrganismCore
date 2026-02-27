"""
IMPC ANALYSIS 3 — STEP 7
KMPC PARAMETER RESOLUTION
AND MRC HARWELL EXTENSION

Three targeted analyses:

ANALYSIS A: KMPC unknown parameters.
  Look up IMPC_OFD_007_001,
  IMPC_OFD_016_001, IMPC_OFD_022_001.
  Pull sample values and determine
  if any is a thigmotaxis substitute.
  Report parameter names from the
  IMPC experiment core name field.

ANALYSIS B: KMPC time-in-center
  implied thigmotaxis.
  KMPC has IMPC_OFD_009_001
  (time in center) for 3,404 animals
  including wildtype.
  Compute:
    implied_thigmo =
      1 - (center_time / test_dur)
  Use as secondary KMPC estimate
  with caveat clearly labeled.

ANALYSIS C: MRC Harwell homozygote
  thigmotaxis profile.
  MRC Harwell has 99,843 homozygotes,
  zero wildtype.
  Pull thigmotaxis for homozygotes
  at MRC and at all other centers.
  Test whether homozygote thigmotaxis
  at MRC is consistent with the
  ELF gradient observed in wildtype
  animals.

  Limitation: homozygote behavior
  reflects both gene knockout effects
  and facility environment. The
  gene knockout effect must be
  treated as noise, not signal.
  Only the center-level mean across
  many diverse knockouts is
  interpretable as a facility effect.

Output:
  impc_parameter_resolution.txt
  impc_resolution_figures.png
  impc_final_extended_table.csv
"""

import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy import stats
import time
import warnings
warnings.filterwarnings('ignore')

RAW_CSV   = "impc_open_field_raw.csv"
SOLR_BASE = (
    "https://www.ebi.ac.uk"
    "/mi/impc/solr/experiment/select"
)

THIGMO_ID  = "IMPC_OFD_010_001"
CENTER_ID  = "IMPC_OFD_009_001"

# KMPC unknown parameters to resolve
KMPC_UNKNOWN = [
    "IMPC_OFD_007_001",
    "IMPC_OFD_016_001",
    "IMPC_OFD_022_001",
]

EXISTING_RESULTS = {
    'UC Davis': {'elf': 31.0,
                 'n_wt': 4402,
                 'median_prop': 0.9213,
                 'protocol_s': 5400},
    'ICS':      {'elf': 36.0,
                 'n_wt': 2418,
                 'median_prop': 0.9431,
                 'protocol_s': 7200},
    'RBRC':     {'elf': 55.0,
                 'n_wt': 1292,
                 'median_prop': 0.7244,
                 'protocol_s': 5400},
    'MARC':     {'elf': 65.0,
                 'n_wt': 1706,
                 'median_prop': 0.7800,
                 'protocol_s': 5400},
    'CCP-IMG':  {'elf': 74.0,
                 'n_wt': 3926,
                 'median_prop': 0.6287,
                 'protocol_s': 3600},
    'BCM':      {'elf': 94.0,
                 'n_wt': 2417,
                 'median_prop': 0.5831,
                 'protocol_s': 3600},
}

ELF_SCORES = {
    'UC Davis':    31.0,
    'ICS':         36.0,
    'RBRC':        55.0,
    'MRC Harwell': 59.0,
    'HMGU':        65.0,
    'MARC':        65.0,
    'KMPC':        67.0,
    'TCP':         74.0,
    'CCP-IMG':     74.0,
    'BCM':         94.0,
}

COLORS = {
    'UC Davis':    '#2ecc71',
    'ICS':         '#27ae60',
    'RBRC':        '#f39c12',
    'MRC Harwell': '#e67e22',
    'MARC':        '#c0392b',
    'KMPC':        '#8e44ad',
    'CCP-IMG':     '#1a5276',
    'BCM':         '#2c3e50',
    'HMGU':        '#bdc3c7',
    'TCP':         '#2980b9',
}

WT_STRINGS = [
    'wild type', 'wildtype',
    'wild-type', 'wt', 'WT',
]

results = []

def log(s=""):
    results.append(s)
    print(s)


def solr_get(params, max_rows=50000):
    """Single paginated SOLR fetch."""
    all_docs = []
    count_p  = {**params,
                'rows': 0, 'wt': 'json'}
    try:
        r = requests.get(
            SOLR_BASE, params=count_p,
            timeout=60)
        r.raise_for_status()
        total = min(
            r.json()
            .get('response', {})
            .get('numFound', 0),
            max_rows
        )
    except Exception as e:
        log(f"  Count failed: {e}")
        return []

    if total == 0:
        return []

    start = 0
    rows  = min(5000, total)
    while start < total:
        q = {**params,
             'rows': rows,
             'start': start,
             'wt': 'json'}
        for attempt in range(3):
            try:
                r = requests.get(
                    SOLR_BASE, params=q,
                    timeout=120)
                r.raise_for_status()
                docs = (r.json()
                        .get('response', {})
                        .get('docs', []))
                all_docs.extend(docs)
                start += len(docs)
                time.sleep(0.2)
                break
            except Exception as e:
                if attempt == 2:
                    log(f"  Page {start}"
                        f" failed: {e}")
                else:
                    time.sleep(2)
    return all_docs


def estimate_duration(series):
    if len(series) < 10:
        return None
    p98 = series.quantile(0.98)
    for sd in [3600, 5400, 7200,
               9000, 10800]:
        if p98 <= sd * 1.02:
            return sd
    return int(p98)


def run_spearman(pts, label):
    if len(pts) < 4:
        return None
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    r_s, p_s = stats.spearmanr(xs, ys)
    r_p, p_p = stats.pearsonr(xs, ys)
    sig = ("***" if p_s < 0.001 else
           "**"  if p_s < 0.01  else
           "*"   if p_s < 0.05  else "ns")
    return {'label': label, 'n': len(pts),
            'r_s': r_s, 'p_s': p_s,
            'r_p': r_p, 'p_p': p_p,
            'sig': sig, 'xs': xs, 'ys': ys}


# ─────────────────────────────────────────
# LOAD RAW CSV
# ─────────────────────────────────────────

log("=" * 60)
log("IMPC PARAMETER RESOLUTION")
log("=" * 60)
log()

df = pd.read_csv(RAW_CSV, low_memory=False)
df['data_point'] = pd.to_numeric(
    df['data_point'], errors='coerce')
log(f"Raw CSV rows: {len(df):,}")
log()


# ─────────────────────────────────────────
# ANALYSIS A: KMPC UNKNOWN PARAMETERS
# ─────────────────────────────────────────

log("=" * 60)
log("ANALYSIS A: KMPC UNKNOWN PARAMETERS")
log("=" * 60)
log()

# Pull sample records for each
# unknown parameter to read the
# parameter_name field
for pid in KMPC_UNKNOWN:
    log(f"Parameter: {pid}")

    docs = solr_get({
        'q': (
            f'phenotyping_center:KMPC'
            f' AND parameter_stable_id:{pid}'
            f' AND observation_type:'
            f'unidimensional'
        ),
        'fl': ','.join([
            'parameter_stable_id',
            'parameter_name',
            'data_point',
            'zygosity',
            'sex',
        ]),
        'rows': 20,
    }, max_rows=20)

    if not docs:
        log(f"  No records found.")
        log()
        continue

    df_p = pd.DataFrame(docs)
    df_p['data_point'] = pd.to_numeric(
        df_p['data_point'], errors='coerce')

    if 'parameter_name' in df_p.columns:
        pname = (
            df_p['parameter_name']
            .dropna().iloc[0]
            if len(df_p) > 0 else 'unknown'
        )
        log(f"  parameter_name: '{pname}'")
    else:
        log("  parameter_name: not returned")

    log(f"  Sample values (N=20):")
    vals = df_p['data_point'].dropna()
    if len(vals) > 0:
        log(
            f"    min={vals.min():.2f} "
            f"median={vals.median():.2f} "
            f"max={vals.max():.2f}"
        )
    log()

# Also pull full KMPC stats for
# each unknown parameter
log("Full KMPC distributions for"
    " unknown parameters:")
log()

kmpc_df = df[
    df['phenotyping_center'] == 'KMPC'
].copy()

for pid in KMPC_UNKNOWN:
    sub = kmpc_df[
        kmpc_df['parameter_stable_id'] == pid
    ]['data_point'].dropna()

    if len(sub) == 0:
        log(f"  {pid}: no data in raw CSV")
        continue

    # Get parameter name from raw CSV
    pname_series = kmpc_df[
        kmpc_df['parameter_stable_id'] == pid
    ]['parameter_name'] if (
        'parameter_name' in kmpc_df.columns
    ) else pd.Series()

    pname = (
        pname_series.dropna().iloc[0]
        if len(pname_series.dropna()) > 0
        else 'unknown'
    )

    log(f"  {pid}: '{pname}'")
    log(
        f"    N={len(sub):,}  "
        f"min={sub.min():.2f}  "
        f"p25={sub.quantile(0.25):.2f}  "
        f"median={sub.median():.2f}  "
        f"p75={sub.quantile(0.75):.2f}  "
        f"max={sub.max():.2f}"
    )
    log()


# ─────────────────────────────────────────
# ANALYSIS B: KMPC TIME-IN-CENTER
# IMPLIED THIGMOTAXIS
# ─────────────────────────────────────────

log("=" * 60)
log("ANALYSIS B: KMPC IMPLIED THIGMOTAXIS")
log("From time-in-center (IMPC_OFD_009_001)")
log("=" * 60)
log()
log("Method:")
log("  implied_thigmo_proportion =")
log("    1 - (center_time / test_dur)")
log()
log("Assumption:")
log("  center_time + periphery_time")
log("  ≈ test_duration")
log("  (remainder = zone-transition")
log("   time, typically <5% of total)")
log()
log("Caveat:")
log("  This is an INDIRECT estimate.")
log("  The complement of center time")
log("  includes transition time, not")
log("  just periphery time. Actual")
log("  thigmotaxis will be slightly")
log("  lower than 1 - center_prop.")
log("  This is a conservative")
log("  estimate of thigmotaxis.")
log()

# Pull KMPC center time
kmpc_ctr = kmpc_df[
    kmpc_df['parameter_stable_id']
    == CENTER_ID
].copy()

log(
    f"KMPC time-in-center records: "
    f"{len(kmpc_ctr):,}"
)

if len(kmpc_ctr) > 0:
    # Estimate test duration from
    # center + periphery combined
    # Use center time P98 as lower
    # bound, total test = P98 of
    # center time / typical center
    # proportion (~10-15%)
    # Better: use P98 from the 
    # time-in-center distribution
    # to estimate total test duration
    # by checking what value of
    # test_dur makes center_prop
    # consistent with other centers

    ctr_vals = (
        kmpc_ctr['data_point'].dropna()
    )

    log(
        f"  Center time distribution:"
    )
    log(
        f"    min={ctr_vals.min():.1f}  "
        f"p5={ctr_vals.quantile(0.05):.1f}  "
        f"p25={ctr_vals.quantile(0.25):.1f}  "
        f"median={ctr_vals.median():.1f}  "
        f"p75={ctr_vals.quantile(0.75):.1f}  "
        f"p95={ctr_vals.quantile(0.95):.1f}  "
        f"max={ctr_vals.max():.1f}"
    )
    log()

    # Estimate test duration from
    # the center-time distribution.
    # A mouse typically spends 5-15%
    # of time in center.
    # If median center time = X,
    # and typical center proportion
    # is ~10%, then total test
    # duration ≈ X / 0.10 = 10X
    # But this is circular.
    #
    # Better: use the sum of center
    # + periphery distance to
    # estimate total.
    # Actually: use KMPC's center
    # entries parameter to infer
    # test structure.
    #
    # Most reliable: query KMPC
    # parameter 007 which may be
    # total distance or total time
    # (will be determined in A).
    # For now, test multiple assumed
    # durations and report all.

    log("  Implied thigmotaxis under")
    log("  different assumed durations:")
    log()
    log(
        f"  {'Assumed_dur':>14} "
        f"{'Implied_thigmo_median':>22} "
        f"{'Plausible':>10}"
    )
    log("  " + "─" * 52)

    best_dur = None
    best_prop = None

    for dur_s in [3600, 5400, 7200]:
        ctr_prop = (
            ctr_vals / dur_s
        ).clip(0, 1)
        implied_thigmo = (
            1 - ctr_prop
        ).clip(0, 1)
        med_implied = float(
            implied_thigmo.median()
        )
        # Plausible if center proportion
        # is between 2% and 25%
        ctr_med_prop = float(
            ctr_prop.median()
        )
        plausible = (
            0.02 <= ctr_med_prop <= 0.25
        )

        log(
            f"  {dur_s:>14}s "
            f"{med_implied*100:>21.1f}% "
            f"{'YES' if plausible else 'NO':>10}"
            f"  (ctr={ctr_med_prop*100:.1f}%)"
        )

        if plausible and best_dur is None:
            best_dur  = dur_s
            best_prop = med_implied

    log()

    # Wildtype only
    wt_mask = (
        kmpc_ctr['zygosity']
        .str.strip().str.lower()
        .isin([s.lower() for s in WT_STRINGS])
    )
    kmpc_ctr_wt = kmpc_ctr[wt_mask].copy()
    log(
        f"  KMPC wildtype center-time"
        f" records: {len(kmpc_ctr_wt):,}"
    )

    if len(kmpc_ctr_wt) >= 5 and best_dur:
        wt_ctr_vals = (
            kmpc_ctr_wt['data_point'].dropna()
        )
        wt_ctr_prop = (
            wt_ctr_vals / best_dur
        ).clip(0, 1)
        wt_implied_thigmo = (
            1 - wt_ctr_prop
        ).clip(0, 1)

        med_wt_implied = float(
            wt_implied_thigmo.median()
        )

        log()
        log(
            f"  WILDTYPE implied thigmotaxis"
        )
        log(
            f"  (assumed dur={best_dur}s):"
        )
        log(
            f"    N wildtype: "
            f"{len(kmpc_ctr_wt):,}"
        )
        log(
            f"    Median implied thigmo: "
            f"{med_wt_implied*100:.1f}%"
        )
        log(
            f"    ELF score: 67.0"
        )
        log()
        log(
            f"  Prediction: 65–78%"
        )
        log(
            f"  Observed:   "
            f"{med_wt_implied*100:.1f}%"
        )
        in_r = (
            0.65 <= med_wt_implied <= 0.78
        )
        log(
            f"  In range:   "
            f"{'YES ✓' if in_r else 'NO ✗'}"
        )
        log()
        log(
            f"  CAVEAT: This value "
            f"(1 - center_proportion) "
            f"includes zone-transition "
            f"time in the 'non-center' "
            f"estimate. True thigmotaxis "
            f"proportion will be marginally "
            f"lower (~2-5 pp). This is a "
            f"conservative upper bound "
            f"on thigmotaxis."
        )
    else:
        med_wt_implied = None
        log("  Insufficient wildtype data")
        log("  or no plausible duration.")

log()


# ─────────────────────────────────────────
# ANALYSIS C: MRC HARWELL HOMOZYGOTE
# THIGMOTAXIS PROFILE
# ─────────────────────────────────────────

log("=" * 60)
log("ANALYSIS C: MRC HARWELL")
log("HOMOZYGOTE THIGMOTAXIS PROFILE")
log("=" * 60)
log()
log("Method:")
log("  MRC Harwell has no wildtype")
log("  records (homozygote-only")
log("  pipeline). Comparing MRC")
log("  homozygote thigmotaxis to")
log("  homozygote thigmotaxis at")
log("  other centers.")
log()
log("  Cross-center homozygote")
log("  comparison has a major")
log("  confounder: different gene")
log("  knockouts produce different")
log("  behavioral phenotypes. The")
log("  center-level mean across")
log("  many diverse knockouts")
log("  averages over this noise.")
log()
log("  This analysis is exploratory")
log("  and clearly labeled as such.")
log()

# Pull thigmotaxis for homozygotes
# at all centers
homo_mask = (
    df['zygosity']
    .str.strip().str.lower()
    == 'homozygote'
)
df_homo = df[
    homo_mask
    & (df['parameter_stable_id'] == THIGMO_ID)
].copy()

log(
    f"Homozygote thigmotaxis records:"
    f" {len(df_homo):,}"
)
log()

PROTOCOL_DURATIONS = {
    'BCM':         3600,
    'CCP-IMG':     3600,
    'ICS':         7200,
    'MARC':        5400,
    'MRC Harwell': 5400,
    'RBRC':        5400,
    'TCP':         5400,
    'UC Davis':    5400,
    'HMGU':        None,
    'KMPC':        None,
}

log(
    f"{'Center':<22} "
    f"{'N_homo':>8} "
    f"{'ELF':>6} "
    f"{'Median_%':>10} "
    f"{'Protocol':>10}"
)
log("─" * 62)

homo_pts = []
homo_center_data = []

for center in sorted(
    df_homo['phenotyping_center'].unique()
):
    cdf = df_homo[
        df_homo['phenotyping_center']
        == center
    ]['data_point'].dropna()

    dur = PROTOCOL_DURATIONS.get(
        center, None
    )
    elf = ELF_SCORES.get(center, None)

    if len(cdf) < 10 or dur is None:
        log(
            f"{center:<22} "
            f"{len(cdf):>8,} "
            f"{str(elf or '?'):>6} "
            f"{'—':>10} "
            f"{str(dur or '?'):>10}"
        )
        continue

    prop = (cdf / dur).clip(0, 1)
    med  = float(prop.median())

    log(
        f"{center:<22} "
        f"{len(cdf):>8,} "
        f"{str(elf or '?'):>6} "
        f"{med*100:>9.1f}% "
        f"{dur:>10}s"
    )

    if elf is not None:
        homo_pts.append((elf, med))
        homo_center_data.append({
            'center':  center,
            'elf':     elf,
            'n_homo':  len(cdf),
            'median_prop': med,
            'dur':     dur,
        })

log()

# Spearman on homozygote data
if len(homo_pts) >= 4:
    res_homo = run_spearman(
        homo_pts,
        "Homozygote thigmotaxis vs ELF"
    )
    if res_homo:
        log(
            f"Homozygote Spearman: "
            f"r={res_homo['r_s']:+.4f}, "
            f"p={res_homo['p_s']:.4f} "
            f"{res_homo['sig']}"
        )
        log(
            f"Pearson: "
            f"r={res_homo['r_p']:+.4f}, "
            f"p={res_homo['p_p']:.4f}"
        )
        log()
        log("Per-center (sorted by ELF):")
        for cd in sorted(
            homo_center_data,
            key=lambda x: x['elf']
        ):
            log(
                f"  {cd['center']:<22} "
                f"ELF={cd['elf']:>5.0f} "
                f"homo={cd['median_prop']*100:.1f}%"
            )
else:
    log("Insufficient centers for"
        " homozygote correlation.")
    res_homo = None

log()


# ─────────────────────────────────────────
# EXTENDED CORRELATION TABLE
# Including KMPC implied if available
# ─────────────────────────────────────────

log("=" * 60)
log("FINAL EXTENDED CORRELATION TABLE")
log("=" * 60)
log()

extended = dict(EXISTING_RESULTS)
new_additions = {}

# Add KMPC implied if we have it
if (
    'kmpc_ctr_wt' in dir()
    and len(kmpc_ctr_wt) >= 5
    and best_dur is not None
    and med_wt_implied is not None
):
    extended['KMPC (implied)'] = {
        'elf':          67.0,
        'n_wt':         len(kmpc_ctr_wt),
        'median_prop':  med_wt_implied,
        'protocol_s':   best_dur,
    }
    new_additions['KMPC (implied)'] = (
        med_wt_implied
    )
    log(
        f"KMPC (implied) added: "
        f"ELF=67, "
        f"thigmo={med_wt_implied*100:.1f}%"
    )

# Add MRC Harwell homozygote
# as labeled separate entry
mrc_homo = next(
    (cd for cd in homo_center_data
     if cd['center'] == 'MRC Harwell'),
    None
)
if mrc_homo:
    log(
        f"MRC Harwell homozygote: "
        f"ELF=59, "
        f"thigmo={mrc_homo['median_prop']*100:.1f}%"
        f" (homozygote — labeled separately)"
    )

log()

# Run correlation with all additions
pts_ext = [
    (v['elf'], v['median_prop'])
    for v in extended.values()
]

# Also: wildtype + MRC homozygote
# as mixed-zygosity sensitivity
pts_with_mrc = list(pts_ext)
if mrc_homo:
    pts_with_mrc.append(
        (59.0, mrc_homo['median_prop'])
    )

log(
    f"{'Analysis':<45} "
    f"{'N':>4} "
    f"{'r_S':>8} "
    f"{'p_S':>8} "
    f"{'r_P':>8} "
    f"{'sig':>4}"
)
log("─" * 80)

for label, pts in [
    ("Original wildtype (N=6)",
     [(v['elf'], v['median_prop'])
      for v in EXISTING_RESULTS.values()]),
    ("+ KMPC implied (N=6 or 7)",
     pts_ext),
    ("+ MRC homozygote sensitivity",
     pts_with_mrc),
]:
    res = run_spearman(pts, label)
    if res:
        log(
            f"{label:<45} "
            f"{res['n']:>4} "
            f"{res['r_s']:>+8.4f} "
            f"{res['p_s']:>8.4f} "
            f"{res['r_p']:>+8.4f} "
            f"{res['sig']:>4}"
        )

log()

# LOO on extended set
if len(pts_ext) > 6:
    log("LOO on extended set:")
    ext_keys = list(extended.keys())
    loo_sigs  = 0
    loo_total = 0
    log(
        f"  {'Dropped':<28} "
        f"{'N':>4} "
        f"{'r_S':>8} "
        f"{'p_S':>8} "
        f"{'sig':>4}"
    )
    log("  " + "─" * 56)
    for drop in ext_keys:
        sub_pts = [
            (v['elf'], v['median_prop'])
            for k, v in extended.items()
            if k != drop
        ]
        res = run_spearman(
            sub_pts, f"drop {drop}"
        )
        if res:
            log(
                f"  {drop:<28} "
                f"{res['n']:>4} "
                f"{res['r_s']:>+8.4f} "
                f"{res['p_s']:>8.4f} "
                f"{res['sig']:>4}"
            )
            loo_total += 1
            if res['sig'] != 'ns':
                loo_sigs += 1
    log()
    fragility = (
        "ROBUST"
        if loo_sigs == loo_total else
        "MODERATELY ROBUST"
        if loo_sigs >= loo_total * 0.75
        else "FRAGILE"
        if loo_sigs >= loo_total * 0.5
        else "VERY FRAGILE"
    )
    log(
        f"  {loo_sigs}/{loo_total} "
        f"LOO significant — {fragility}"
    )
    log()


# ──────────────��──────────────────────────
# FIGURES
# ─────────────────────────────────────────

log("Building figures...")

fig = plt.figure(
    figsize=(16, 10), dpi=120
)
fig.patch.set_facecolor('white')
gs  = gridspec.GridSpec(
    2, 3, figure=fig,
    hspace=0.44, wspace=0.36
)


# ── Panel 1: Wildtype + KMPC implied ──

ax1 = fig.add_subplot(gs[0, :2])

for cname, cd in EXISTING_RESULTS.items():
    ax1.scatter(
        cd['elf'],
        cd['median_prop'] * 100,
        color=COLORS.get(cname, '#888'),
        s=100, zorder=4,
        edgecolors='black',
        linewidth=0.7, marker='o',
    )
    ax1.annotate(
        cname,
        (cd['elf'], cd['median_prop']*100),
        fontsize=7, xytext=(5, 4),
        textcoords='offset points',
    )

# KMPC implied
if 'KMPC (implied)' in extended:
    v = extended['KMPC (implied)']
    ax1.scatter(
        v['elf'], v['median_prop'] * 100,
        color=COLORS.get('KMPC', '#8e44ad'),
        s=140, zorder=5,
        edgecolors='black',
        linewidth=1.0, marker='D',
        label='KMPC (implied from CtrTime)',
    )
    ax1.annotate(
        'KMPC◆',
        (v['elf'], v['median_prop']*100),
        fontsize=7.5, fontweight='bold',
        xytext=(5, 5),
        textcoords='offset points',
        color=COLORS.get('KMPC', '#8e44ad'),
    )
    # Prediction band
    ax1.axhspan(
        65, 78, alpha=0.06,
        color=COLORS.get('KMPC', '#8e44ad'),
        label='KMPC predicted range',
    )

# MRC Harwell homozygote
if mrc_homo:
    ax1.scatter(
        59.0,
        mrc_homo['median_prop'] * 100,
        color=COLORS.get(
            'MRC Harwell', '#e67e22'
        ),
        s=120, zorder=4,
        edgecolors='black',
        linewidth=0.7, marker='s',
        label='MRC Harwell (homozygote)',
        alpha=0.6,
    )
    ax1.annotate(
        'MRC■ (homo)',
        (59.0,
         mrc_homo['median_prop'] * 100),
        fontsize=7, alpha=0.7,
        xytext=(5, 4),
        textcoords='offset points',
        color=COLORS.get(
            'MRC Harwell', '#e67e22'
        ),
    )

# Regression on wildtype
orig_xs = [
    v['elf'] for v in
    EXISTING_RESULTS.values()
]
orig_ys = [
    v['median_prop']*100 for v in
    EXISTING_RESULTS.values()
]
z = np.polyfit(orig_xs, orig_ys, 1)
xfit = np.linspace(
    min(orig_xs) - 10,
    max(orig_xs) + 5, 100
)
ax1.plot(
    xfit, np.polyval(z, xfit),
    color='#2c3e50', linewidth=1.8,
    alpha=0.5, linestyle='--',
    label='Regression (wildtype only)',
)

ax1.set_xlabel(
    "ELF Score (composite)", fontsize=9
)
ax1.set_ylabel(
    "% Test Time in Periphery",
    fontsize=9
)
ax1.set_title(
    "Wildtype C57BL/6N Thigmotaxis"
    " vs Facility ELF Score\n"
    "◆ = KMPC implied (1-CtrTime/dur) "
    "■ = MRC Harwell homozygote"
    " (sensitivity)",
    fontsize=8.5,
)
ax1.set_ylim(40, 102)
ax1.legend(fontsize=6.5, loc='upper right')
ax1.tick_params(labelsize=8)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.grid(axis='y', alpha=0.2,
          linewidth=0.5)


# ── Panel 2: KMPC parameter values ──

ax2 = fig.add_subplot(gs[0, 2])

kmpc_param_data = {}
for pid in [CENTER_ID] + KMPC_UNKNOWN:
    sub = kmpc_df[
        kmpc_df['parameter_stable_id'] == pid
    ]['data_point'].dropna()
    if len(sub) > 0:
        pname = ''
        if 'parameter_name' in kmpc_df.columns:
            pn = kmpc_df[
                kmpc_df['parameter_stable_id']
                == pid
            ]['parameter_name'].dropna()
            pname = (
                pn.iloc[0] if len(pn) > 0
                else pid
            )
        label = (
            pname[:20] if pname else pid
        )
        kmpc_param_data[label] = sub.values

if kmpc_param_data:
    labels_k = list(kmpc_param_data.keys())
    data_k   = [
        kmpc_param_data[l]
        for l in labels_k
    ]
    bp = ax2.boxplot(
        data_k,
        patch_artist=True,
        showfliers=False,
        medianprops=dict(
            color='black',
            linewidth=1.5
        ),
    )
    for patch in bp['boxes']:
        patch.set_facecolor(
            COLORS.get('KMPC', '#8e44ad')
        )
        patch.set_alpha(0.6)
    ax2.set_xticklabels(
        labels_k, fontsize=6,
        rotation=45, ha='right'
    )
    ax2.set_ylabel(
        "Raw value", fontsize=8
    )
    ax2.set_title(
        "KMPC — OFD Parameter\n"
        "Value Distributions",
        fontsize=8
    )
    ax2.tick_params(labelsize=7)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)


# ── Panel 3: Homozygote vs wildtype ──

ax3 = fig.add_subplot(gs[1, 0])

# Wildtype points
wt_elf  = [v['elf'] for v in
            EXISTING_RESULTS.values()]
wt_prop = [v['median_prop']*100 for v in
            EXISTING_RESULTS.values()]
ax3.scatter(
    wt_elf, wt_prop,
    color='#27ae60', s=90,
    zorder=4, edgecolors='black',
    linewidth=0.6, label='Wildtype',
)

# Homozygote points
for cd in homo_center_data:
    ax3.scatter(
        cd['elf'],
        cd['median_prop']*100,
        color=COLORS.get(
            cd['center'], '#888'
        ),
        s=90, zorder=3, marker='s',
        edgecolors='black',
        linewidth=0.5, alpha=0.6,
        label=(
            cd['center']
            + ' (homo)'
        ),
    )

if res_homo:
    ax3.set_title(
        f"Homozygote Thigmotaxis vs ELF\n"
        f"r={res_homo['r_s']:+.3f},"
        f" p={res_homo['p_s']:.3f}"
        f" {res_homo['sig']}",
        fontsize=8
    )

ax3.set_xlabel(
    "ELF Score", fontsize=8
)
ax3.set_ylabel(
    "% Time in Periphery",
    fontsize=8
)
ax3.legend(fontsize=5.5,
            loc='upper right')
ax3.tick_params(labelsize=7)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)


# ── Panel 4: Summary table ──

ax4 = fig.add_subplot(gs[1, 1:])
ax4.axis('off')

summary_rows = []
for cname in sorted(
    extended,
    key=lambda c: extended[c]['elf']
):
    cd = extended[cname]
    is_new = cname not in EXISTING_RESULTS
    summary_rows.append(
        f"  {cname:<22} "
        f"ELF={cd['elf']:>5.0f}  "
        f"N={cd['n_wt']:>5,}  "
        f"thigmo={cd['median_prop']*100:.1f}%"
        + (" ◆ implied" if is_new else "")
    )

if mrc_homo:
    summary_rows.append(
        f"  {'MRC Harwell (homo)':<22} "
        f"ELF={59:>5.0f}  "
        f"N={mrc_homo['n_homo']:>5,}  "
        f"thigmo={mrc_homo['median_prop']*100:.1f}%"
        f" ■ homozygote"
    )

res_final = run_spearman(
    pts_ext,
    "Final extended"
)

lines = [
    "CURRENT STATUS — ANALYSIS 3",
    "─" * 55,
    "",
    "Wildtype C57BL/6N dataset:",
] + summary_rows + [
    "",
    "─" * 55,
    f"Primary r_S = -0.886, p = 0.019 *"
    f" (N=6 wildtype)",
]
if res_final and len(pts_ext) > 6:
    lines.append(
        f"Extended r_S = "
        f"{res_final['r_s']:+.3f}, "
        f"p = {res_final['p_s']:.3f} "
        f"{res_final['sig']}"
        f" (N={res_final['n']})"
    )
lines += [
    "",
    "JAX: absent from DR23 OFD dataset.",
    "KMPC: no thigmotaxis parameter —",
    "  IMPC_OFD_010_001 not in pipeline.",
    "  Implied estimate from CtrTime",
    "  available if duration confirmed.",
    "",
    "MRC Harwell (ELF=59): homozygote",
    "  only — wildtype not available.",
    "  Homozygote result labeled",
    "  separately in all analyses.",
]

for i, line in enumerate(lines):
    ax4.text(
        0.02,
        0.97 - i * 0.072,
        line,
        transform=ax4.transAxes,
        fontsize=7.5,
        fontfamily='monospace',
        va='top',
        color=(
            '#27ae60'
            if '*' in line and 'r_S' in line
            else '#8e44ad'
            if 'implied' in line
            else '#e67e22'
            if 'homozygote' in line
            else '#c0392b'
            if 'absent' in line
            else 'black'
        ),
    )

fig.suptitle(
    "IMPC Analysis 3 — Parameter"
    " Resolution & Extended Correlation\n"
    "OrganismCore — E.R. Lawson,"
    " February 2026",
    fontsize=10, fontweight='bold',
    y=0.995,
)

plt.savefig(
    'impc_resolution_figures.png',
    dpi=200, bbox_inches='tight',
    facecolor='white',
)
log("Saved → impc_resolution_figures.png")

ext_rows = []
for cname, cd in sorted(
    extended.items(),
    key=lambda x: x[1]['elf']
):
    ext_rows.append({
        'center':       cname,
        'elf_score':    cd['elf'],
        'n_wt':         cd['n_wt'],
        'median_prop':  round(
            cd['median_prop'], 4),
        'pct_periphery': round(
            cd['median_prop']*100, 2),
        'protocol_s':   cd['protocol_s'],
        'data_type':    (
            'implied_from_center_time'
            if '(implied)' in cname
            else 'wildtype_direct'
        ),
    })

if mrc_homo:
    ext_rows.append({
        'center':       'MRC Harwell',
        'elf_score':    59.0,
        'n_wt':         mrc_homo['n_homo'],
        'median_prop':  round(
            mrc_homo['median_prop'], 4),
        'pct_periphery': round(
            mrc_homo['median_prop']*100, 2),
        'protocol_s':   5400,
        'data_type':    'homozygote_only',
    })

pd.DataFrame(ext_rows).to_csv(
    'impc_final_extended_table.csv',
    index=False,
)
log("Saved → impc_final_extended_table.csv")

with open(
    'impc_parameter_resolution.txt', 'w'
) as f:
    f.write("\n".join(results))
log("Saved → impc_parameter_resolution.txt")
log()
log("=" * 60)
log("READ IN ORDER:")
log()
log("  Analysis A:")
log("    Unknown KMPC parameter names.")
log("    Is any of them thigmotaxis?")
log()
log("  Analysis B:")
log("    KMPC implied thigmo value.")
log("    Which duration is plausible?")
log("    Is it in the 65-78% range?")
log()
log("  Analysis C:")
log("    MRC Harwell homozygote r and p.")
log("    Does homozygote data support")
log("    the wildtype gradient?")
log()
log("  Final table:")
log("    Updated r_S and fragility")
log("    with all additions.")
log("=" * 60)
