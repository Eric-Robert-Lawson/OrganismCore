"""
IMPC ANALYSIS 3 — STEP 6
KMPC AND JAX TARGETED QUERIES

Two targeted queries to extend
the 6-center ELF correlation.

QUERY 1: KMPC
  Korea Mouse Phenotyping Center
  Seoul National University, Seoul
  ELF score: 67 (VERY_HIGH)
  Known wildtype N: 6,964
  Thigmotaxis absent from prior
  wildtype table — investigate why.

  If KMPC thigmotaxis proportion
  falls 66-75%: fills the dose-
  response gap between MARC (65,
  78.0%) and CCP-IMG (74, 62.9%).
  Predicted: ~70-75% if gradient
  is real.

QUERY 2: JAX
  The Jackson Laboratory
  Bar Harbor, Maine
  ELF score: ~15 (LOW — rural,
  coastal Maine, no heavy industry)
  Not present in prior dataset.

  If JAX has wildtype thigmotaxis
  data and proportion falls 90-97%:
  adds the cleanest low-ELF anchor
  at the far end of the gradient.
  16 ELF points below UC Davis.
  Predicted: >92% if gradient
  continues.

Both queries hit the live IMPC
SOLR API. Results appended to
the correlation table and LOO
re-run with updated N.

Output:
  impc_kmpc_jax_results.txt
  impc_extended_correlation_table.csv
  impc_extended_figures.png
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

SOLR_BASE = (
    "https://www.ebi.ac.uk"
    "/mi/impc/solr/experiment/select"
)

THIGMO_ID = "IMPC_OFD_010_001"
CENTER_ID = "IMPC_OFD_009_001"

# Existing 6-center result
# (from Document 1)
EXISTING_RESULTS = {
    'UC Davis': {
        'elf': 31.0,
        'n_wt': 4402,
        'median_prop': 0.9213,
        'protocol_s': 5400,
        'city': 'Davis, CA',
        'country': 'USA',
    },
    'ICS': {
        'elf': 36.0,
        'n_wt': 2418,
        'median_prop': 0.9431,
        'protocol_s': 7200,
        'city': 'Illkirch, FR',
        'country': 'France',
    },
    'RBRC': {
        'elf': 55.0,
        'n_wt': 1292,
        'median_prop': 0.7244,
        'protocol_s': 5400,
        'city': 'Tsukuba, JP',
        'country': 'Japan',
    },
    'MARC': {
        'elf': 65.0,
        'n_wt': 1706,
        'median_prop': 0.7800,
        'protocol_s': 5400,
        'city': 'Nanjing, CN',
        'country': 'China',
    },
    'CCP-IMG': {
        'elf': 74.0,
        'n_wt': 3926,
        'median_prop': 0.6287,
        'protocol_s': 3600,
        'city': 'Toronto, CA',
        'country': 'Canada',
    },
    'BCM': {
        'elf': 94.0,
        'n_wt': 2417,
        'median_prop': 0.5831,
        'protocol_s': 3600,
        'city': 'Houston, TX',
        'country': 'USA',
    },
}

# New centers to query
NEW_CENTERS = {
    'KMPC': {
        'elf': 67.0,
        'city': 'Seoul, KR',
        'country': 'South Korea',
        'urban_class': 'urban',
        'elf_prior': 'VERY_HIGH',
        'predicted_prop': 0.72,
        'predicted_range': (0.65, 0.78),
        'note':
            'Seoul National University.'
            ' Downtown Seoul.',
    },
    'JAX': {
        'elf': 15.0,
        'city': 'Bar Harbor, ME',
        'country': 'USA',
        'urban_class': 'rural',
        'elf_prior': 'LOW',
        'predicted_prop': 0.93,
        'predicted_range': (0.88, 0.97),
        'note':
            'Rural coastal Maine.'
            ' Nearest major city'
            ' 45+ miles.',
    },
}

# Wildtype zygosity strings
WT_STRINGS = [
    'wild type', 'wildtype',
    'wild-type', 'wt', 'WT',
]

COLORS = {
    'UC Davis':    '#2ecc71',
    'ICS':         '#27ae60',
    'RBRC':        '#f39c12',
    'MARC':        '#e67e22',
    'CCP-IMG':     '#1a5276',
    'BCM':         '#2c3e50',
    'KMPC':        '#8e44ad',
    'JAX':         '#1abc9c',
}

results = []

def log(s=""):
    results.append(s)
    print(s)


def solr_query(params, max_rows=200000):
    """
    Paginated SOLR query with retry.
    Returns list of docs.
    """
    all_docs = []
    start    = 0
    rows     = min(5000, max_rows)

    # Get total first
    count_p = {**params,
               'rows': 0,
               'wt': 'json'}
    try:
        r = requests.get(
            SOLR_BASE,
            params=count_p,
            timeout=60,
        )
        r.raise_for_status()
        total = (
            r.json()
            .get('response', {})
            .get('numFound', 0)
        )
    except Exception as e:
        log(f"  Count query failed: {e}")
        return []

    total = min(total, max_rows)
    if total == 0:
        return []

    log(f"  Records found: {total:,}")

    while start < total:
        query = {
            **params,
            'rows':  rows,
            'start': start,
            'wt':    'json',
        }
        for attempt in range(3):
            try:
                r = requests.get(
                    SOLR_BASE,
                    params=query,
                    timeout=120,
                )
                r.raise_for_status()
                docs = (
                    r.json()
                    .get('response', {})
                    .get('docs', [])
                )
                all_docs.extend(docs)
                start += len(docs)
                time.sleep(0.25)
                break
            except Exception as e:
                if attempt == 2:
                    log(
                        f"  Page {start}"
                        f" failed: {e}"
                    )
                else:
                    time.sleep(2)

    return all_docs


def get_center_thigmo(center_name):
    """
    Pull all thigmotaxis observations
    for a given center.
    Returns raw DataFrame.
    """
    params = {
        'q': (
            f'phenotyping_center:'
            f'"{center_name}"'
            f' AND procedure_stable_id:'
            f'IMPC_OFD_001'
            f' AND parameter_stable_id:'
            f'{THIGMO_ID}'
            f' AND observation_type:'
            f'unidimensional'
        ),
        'fl': ','.join([
            'external_sample_id',
            'phenotyping_center',
            'sex',
            'zygosity',
            'strain_name',
            'data_point',
            'date_of_experiment',
            'age_in_weeks',
            'pipeline_stable_id',
            'procedure_stable_id',
            'parameter_stable_id',
        ]),
    }
    docs = solr_query(params)
    if not docs:
        return pd.DataFrame()
    df = pd.DataFrame(docs)
    df['data_point'] = pd.to_numeric(
        df['data_point'], errors='coerce'
    )
    return df


def get_all_ofd_params(center_name):
    """
    Pull ALL OFD parameters for a
    center to see what is available.
    Returns parameter counts.
    """
    params = {
        'q': (
            f'phenotyping_center:'
            f'"{center_name}"'
            f' AND procedure_stable_id:'
            f'IMPC_OFD_001'
            f' AND observation_type:'
            f'unidimensional'
        ),
        'rows': 0,
        'facet': 'true',
        'facet.field': 'parameter_stable_id',
        'facet.limit': 50,
        'facet.mincount': 1,
        'wt': 'json',
    }
    try:
        r = requests.get(
            SOLR_BASE,
            params=params,
            timeout=60,
        )
        r.raise_for_status()
        fc = (
            r.json()
            .get('facet_counts', {})
            .get('facet_fields', {})
            .get('parameter_stable_id', [])
        )
        out = {}
        for i in range(0, len(fc), 2):
            out[fc[i]] = fc[i+1]
        return out
    except Exception as e:
        log(f"  Param facet failed: {e}")
        return {}


def estimate_duration(series):
    """
    Estimate test duration in seconds
    from P98 of thigmotaxis distribution,
    rounded to nearest standard duration.
    """
    if len(series) < 10:
        return None
    p98 = series.quantile(0.98)
    for sd in [3600, 5400, 7200,
               9000, 10800]:
        if p98 <= sd * 1.02:
            return sd
    return int(p98)


def analyze_center(name, meta):
    """
    Full analysis pipeline for one
    new center.
    Returns dict with results or None.
    """
    log(f"{'─'*50}")
    log(f"Center: {name}")
    log(f"  ELF score: {meta['elf']}")
    log(
        f"  Location: {meta['city']}, "
        f"{meta['country']}"
    )
    log(
        f"  Predicted thigmo: "
        f"{meta['predicted_prop']*100:.1f}%"
        f" (range "
        f"{meta['predicted_range'][0]*100:.0f}"
        f"–"
        f"{meta['predicted_range'][1]*100:.0f}"
        f"%)"
    )
    log()

    # Step 1: Check available params
    log("  Available OFD parameters:")
    param_counts = get_all_ofd_params(name)
    if not param_counts:
        log("  No OFD data found.")
        return None
    for pid, cnt in sorted(
        param_counts.items(),
        key=lambda x: -x[1]
    ):
        flag = (
            " ← THIGMO"
            if pid == THIGMO_ID
            else ""
        )
        log(
            f"    {pid:<30} "
            f"{cnt:>8,}{flag}"
        )
    log()

    if THIGMO_ID not in param_counts:
        log(
            f"  WARNING: Thigmotaxis "
            f"({THIGMO_ID}) not found "
            f"for {name}."
        )
        log(
            f"  Available parameters "
            f"suggest different pipeline."
        )
        return None

    # Step 2: Pull thigmo data
    log(f"  Pulling thigmotaxis data...")
    df = get_center_thigmo(name)

    if df.empty:
        log(f"  No data returned.")
        return None

    log(
        f"  Total observations: "
        f"{len(df):,}"
    )

    # Step 3: Zygosity breakdown
    if 'zygosity' in df.columns:
        log("  Zygosity breakdown:")
        zyg_vc = (
            df['zygosity'].value_counts()
        )
        for zyg, cnt in zyg_vc.items():
            log(
                f"    '{zyg}': {cnt:,}"
            )
    log()

    # Step 4: Strain check
    if 'strain_name' in df.columns:
        strain_vc = (
            df['strain_name']
            .value_counts()
            .head(5)
        )
        log("  Strain breakdown:")
        for strain, cnt in (
            strain_vc.items()
        ):
            log(
                f"    {strain}: {cnt:,}"
            )
    log()

    # Step 5: Test duration estimation
    all_vals = df[
        'data_point'
    ].dropna()
    dur = estimate_duration(all_vals)
    log(
        f"  Estimated test duration: "
        f"{dur}s "
        f"({dur//60 if dur else '?'} min)"
    )
    log()

    # Step 6: Wildtype extraction
    wt_mask = (
        df['zygosity']
        .str.strip()
        .str.lower()
        .isin([s.lower() for s in WT_STRINGS])
    )
    df_wt = df[wt_mask].copy()
    log(
        f"  Wildtype records: "
        f"{len(df_wt):,}"
    )

    if len(df_wt) < 5:
        log(
            f"  INSUFFICIENT wildtype"
            f" data for {name}."
        )
        log(
            f"  Zygosity strings tried: "
            f"{WT_STRINGS}"
        )

        # Try broader filter
        log("  Trying broader filter...")
        all_zyg = (
            df['zygosity']
            .str.lower()
            .unique()
        )
        log(
            f"  Actual zygosity values:"
            f" {list(all_zyg)}"
        )
        return None

    # Step 7: Proportion computation
    if dur is None:
        log(
            f"  Cannot compute proportion"
            f" — unknown test duration."
        )
        return None

    wt_vals = df_wt['data_point'].dropna()
    proportions = (
        wt_vals / dur
    ).clip(0, 1)

    med_prop  = float(proportions.median())
    mean_prop = float(proportions.mean())
    sd_prop   = float(proportions.std())

    log("  WILDTYPE THIGMOTAXIS:")
    log(
        f"    N:               "
        f"{len(wt_vals):,}"
    )
    log(
        f"    Median raw:      "
        f"{wt_vals.median():.1f}s"
    )
    log(
        f"    Median prop:     "
        f"{med_prop:.4f} "
        f"({100*med_prop:.1f}%)"
    )
    log(
        f"    Mean prop:       "
        f"{mean_prop:.4f} "
        f"({100*mean_prop:.1f}%)"
    )
    log(
        f"    SD prop:         "
        f"{sd_prop:.4f}"
    )
    log(
        f"    Protocol dur:    {dur}s"
    )
    log()

    # Step 8: Prediction check
    pred = meta['predicted_prop']
    lo, hi = meta['predicted_range']
    in_range = lo <= med_prop <= hi

    log(
        f"  Prediction: "
        f"{pred*100:.1f}% "
        f"[{lo*100:.0f}–{hi*100:.0f}%]"
    )
    log(
        f"  Observed:   "
        f"{med_prop*100:.1f}%"
    )
    log(
        f"  In predicted range: "
        f"{'YES ✓' if in_range else 'NO ✗'}"
    )
    log()

    return {
        'center':       name,
        'elf':          meta['elf'],
        'city':         meta['city'],
        'country':      meta['country'],
        'n_wt':         len(wt_vals),
        'median_prop':  med_prop,
        'mean_prop':    mean_prop,
        'sd_prop':      sd_prop,
        'protocol_s':   dur,
        'in_range':     in_range,
        'predicted':    pred,
        'raw_df':       df_wt,
    }


# ─────────────────────────────────────────
# MAIN
# ��────────────────────────────────────────

log("=" * 60)
log("IMPC TARGETED CENTER QUERIES")
log("KMPC and JAX")
log("=" * 60)
log()
log("Querying live IMPC SOLR API...")
log()

new_results = {}

for center_name, meta in (
    NEW_CENTERS.items()
):
    result = analyze_center(
        center_name, meta
    )
    if result:
        new_results[center_name] = result
    log()

log("=" * 60)
log("QUERY RESULTS SUMMARY")
log("=" * 60)
log()

for cname, res in new_results.items():
    log(
        f"  {cname}: "
        f"N={res['n_wt']:,}, "
        f"median={res['median_prop']*100:.1f}%, "
        f"ELF={res['elf']}"
    )

if not new_results:
    log(
        "  No new centers returned"
        " usable data."
    )
log()


# ─────────────────────────────────────────
# EXTENDED CORRELATION TABLE
# ─────────────────────────────────────────

log("=" * 60)
log("EXTENDED CORRELATION")
log("Original 6 + new centers")
log("=" * 60)
log()

# Build combined dataset
all_centers = {}

for cname, cdata in (
    EXISTING_RESULTS.items()
):
    all_centers[cname] = {
        'elf':          cdata['elf'],
        'n_wt':         cdata['n_wt'],
        'median_prop':  cdata['median_prop'],
        'protocol_s':   cdata['protocol_s'],
        'city':         cdata['city'],
        'source':       'original',
    }

for cname, res in new_results.items():
    all_centers[cname] = {
        'elf':          res['elf'],
        'n_wt':         res['n_wt'],
        'median_prop':  res['median_prop'],
        'protocol_s':   res['protocol_s'],
        'city':         res['city'],
        'source':       'new',
    }

# Sort by ELF
sorted_centers = sorted(
    all_centers.items(),
    key=lambda x: x[1]['elf']
)

log(
    f"{'Center':<22} "
    f"{'ELF':>6} "
    f"{'N_wt':>7} "
    f"{'%Periph':>9} "
    f"{'Protocol':>10} "
    f"{'Source':>8}"
)
log("─" * 68)

for cname, cd in sorted_centers:
    log(
        f"{cname:<22} "
        f"{cd['elf']:>6.0f} "
        f"{cd['n_wt']:>7,} "
        f"{cd['median_prop']*100:>8.1f}% "
        f"{cd['protocol_s']:>8}s "
        f"{cd['source']:>8}"
    )

log()


# ─────────────────────────────────────────
# EXTENDED SPEARMAN CORRELATION
# ─────────────────────────────────────────

def run_spearman(centers_dict, label):
    pts = [
        (v['elf'], v['median_prop'])
        for v in centers_dict.values()
        if v['median_prop'] is not None
    ]
    if len(pts) < 4:
        log(
            f"  {label}: only {len(pts)}"
            f" centers — skip"
        )
        return None

    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]

    r_s, p_s = stats.spearmanr(xs, ys)
    r_p, p_p = stats.pearsonr(xs, ys)

    sig = (
        "***" if p_s < 0.001 else
        "**"  if p_s < 0.01  else
        "*"   if p_s < 0.05  else
        "ns"
    )

    return {
        'label':       label,
        'n':           len(pts),
        'r_s':         r_s,
        'p_s':         p_s,
        'r_p':         r_p,
        'p_p':         p_p,
        'sig':         sig,
        'xs':          xs,
        'ys':          ys,
    }


log("Spearman correlations:")
log()

corr_original = run_spearman(
    {k: v for k, v in
     EXISTING_RESULTS.items()},
    "Original 6 centers"
)
corr_extended = run_spearman(
    all_centers,
    f"Extended {len(all_centers)} centers"
)

# LOO on extended set
log(
    f"{'Analysis':<40} "
    f"{'N':>4} "
    f"{'r_S':>8} "
    f"{'p_S':>8} "
    f"{'sig':>4}"
)
log("─" * 68)

for res in [corr_original, corr_extended]:
    if res:
        log(
            f"{res['label']:<40} "
            f"{res['n']:>4} "
            f"{res['r_s']:>+8.4f} "
            f"{res['p_s']:>8.4f} "
            f"{res['sig']:>4}"
        )

log()

# LOO on extended
if corr_extended and len(all_centers) >= 5:
    log("Leave-one-out (extended set):")
    log(
        f"  {'Dropped':<20} "
        f"{'N':>4} "
        f"{'r_S':>8} "
        f"{'p_S':>8} "
        f"{'sig':>4}"
    )
    log("  " + "─" * 48)

    loo_sigs = 0
    loo_total = 0

    for drop in list(all_centers.keys()):
        sub = {
            k: v for k, v in
            all_centers.items()
            if k != drop
        }
        res = run_spearman(
            sub,
            f"drop {drop}"
        )
        if res:
            sig = (
                "***" if res['p_s']
                < 0.001 else
                "**"  if res['p_s']
                < 0.01  else
                "*"   if res['p_s']
                < 0.05  else
                "ns"
            )
            log(
                f"  {drop:<20} "
                f"{res['n']:>4} "
                f"{res['r_s']:>+8.4f} "
                f"{res['p_s']:>8.4f} "
                f"{sig:>4}"
            )
            loo_total += 1
            if sig != 'ns':
                loo_sigs += 1

    log()
    if loo_total > 0:
        log(
            f"  Significant in "
            f"{loo_sigs}/{loo_total} "
            f"LOO configurations."
        )
        fragility = (
            "ROBUST"
            if loo_sigs == loo_total else
            "MODERATELY ROBUST"
            if loo_sigs
            >= loo_total * 0.75 else
            "FRAGILE"
            if loo_sigs
            >= loo_total * 0.5 else
            "VERY FRAGILE"
        )
        log(f"  Fragility: {fragility}")
log()


# ─────────────────────────────────────────
# PREDICTION REPORT
# ─────────────────────────────────────────

log("=" * 60)
log("PREDICTION REPORT")
log("Were new center values in the")
log("predicted range?")
log("=" * 60)
log()

for cname, meta in NEW_CENTERS.items():
    pred = meta['predicted_prop']
    lo, hi = meta['predicted_range']
    elf   = meta['elf']

    if cname in new_results:
        obs = new_results[cname][
            'median_prop'
        ]
        in_r = lo <= obs <= hi
        delta = obs - pred

        log(f"  {cname} (ELF={elf}):")
        log(
            f"    Predicted: "
            f"{pred*100:.1f}% "
            f"[{lo*100:.0f}–{hi*100:.0f}%]"
        )
        log(
            f"    Observed:  "
            f"{obs*100:.1f}%"
        )
        log(
            f"    In range:  "
            f"{'YES ✓' if in_r else 'NO ✗'}"
        )
        log(
            f"    Delta:     "
            f"{delta*100:+.1f} pp"
        )
    else:
        log(f"  {cname}: NO DATA RETURNED")
        log(
            f"    Predicted: "
            f"{pred*100:.1f}% "
            f"[{lo*100:.0f}–{hi*100:.0f}%]"
        )
        log(f"    Check SOLR for center")
        log(f"    name variant.")
    log()


# ─────────────────────────────────────────
# CHECK ALTERNATE CENTER NAME SPELLINGS
# If JAX or KMPC returned nothing
# ─────────────────────────────────────────

missing = [
    c for c in NEW_CENTERS
    if c not in new_results
]

if missing:
    log("=" * 60)
    log("ALTERNATE NAME SEARCH")
    log("Centers with no results —")
    log("checking name variants")
    log("=" * 60)
    log()

    # Query the phenotyping_center
    # facet for all centers with OFD
    # data to find correct names
    facet_params = {
        'q': 'procedure_stable_id:'
             'IMPC_OFD_001',
        'rows': 0,
        'facet': 'true',
        'facet.field': 'phenotyping_center',
        'facet.limit': 100,
        'facet.mincount': 1,
        'wt': 'json',
    }
    try:
        r = requests.get(
            SOLR_BASE,
            params=facet_params,
            timeout=60,
        )
        r.raise_for_status()
        fc = (
            r.json()
            .get('facet_counts', {})
            .get('facet_fields', {})
            .get('phenotyping_center', [])
        )
        all_center_names = {}
        for i in range(0, len(fc), 2):
            all_center_names[fc[i]] = fc[i+1]

        log("All center names in SOLR:")
        for cname, cnt in sorted(
            all_center_names.items(),
            key=lambda x: -x[1]
        ):
            flag = ""
            for miss in missing:
                if (miss.lower() in
                        cname.lower()
                        or cname.lower() in
                        miss.lower()):
                    flag = (
                        f" ← possible "
                        f"match for {miss}"
                    )
            log(
                f"  {cname:<40} "
                f"{cnt:>10,}{flag}"
            )
        log()

        # Retry missing centers with
        # all possible name variants
        for miss in missing:
            log(
                f"Retrying {miss} with"
                f" name variants..."
            )
            for solr_name, cnt in (
                all_center_names.items()
            ):
                if (
                    miss.lower()
                    in solr_name.lower()
                    or solr_name.lower()
                    in miss.lower()
                    or any(
                        part in
                        solr_name.lower()
                        for part in
                        miss.lower().split()
                    )
                ):
                    log(
                        f"  Trying: "
                        f"'{solr_name}' "
                        f"(N={cnt:,})"
                    )
                    meta = NEW_CENTERS[miss]
                    result = analyze_center(
                        solr_name, meta
                    )
                    if result:
                        result['center'] = (
                            miss
                        )
                        result[
                            'solr_name'
                        ] = solr_name
                        new_results[miss] = (
                            result
                        )
                        log(
                            f"  Found {miss}"
                            f" as '{solr_name}'"
                        )
                        break
            log()

    except Exception as e:
        log(
            f"Alternate name search "
            f"failed: {e}"
        )


# ─────────────────────────────────────────
# SAVE RESULTS TABLE
# ─────────────────────────────────────────

rows = []
for cname, cd in sorted_centers:
    rows.append({
        'center':          cname,
        'elf_score':       cd['elf'],
        'city':            cd['city'],
        'n_wt':            cd['n_wt'],
        'median_prop':
            round(cd['median_prop'], 4),
        'pct_periphery':
            round(
                cd['median_prop'] * 100,
                2
            ),
        'protocol_s':      cd['protocol_s'],
        'source':          cd['source'],
    })

# Add new results if any
for cname, res in new_results.items():
    if cname not in all_centers:
        rows.append({
            'center':      cname,
            'elf_score':   res['elf'],
            'city':        res['city'],
            'n_wt':        res['n_wt'],
            'median_prop':
                round(res['median_prop'], 4),
            'pct_periphery':
                round(
                    res['median_prop'] * 100,
                    2
                ),
            'protocol_s':  res['protocol_s'],
            'source':      'new',
        })

ext_df = pd.DataFrame(rows)
ext_df = ext_df.sort_values(
    'elf_score'
).reset_index(drop=True)

ext_df.to_csv(
    'impc_extended_correlation_table.csv',
    index=False,
)
log(
    "Saved → "
    "impc_extended_correlation_table.csv"
)
log()


# ─────────────────────────────────────────
# FIGURES
# ─────────────────────────────────────────

log("Building figures...")

fig = plt.figure(
    figsize=(16, 10), dpi=120
)
fig.patch.set_facecolor('white')
gs = gridspec.GridSpec(
    2, 3, figure=fig,
    hspace=0.42, wspace=0.36,
)


# ── Panel 1: Extended scatter ──

ax1 = fig.add_subplot(gs[0, :2])

# Plot original points
for cname, cd in (
    EXISTING_RESULTS.items()
):
    ax1.scatter(
        cd['elf'],
        cd['median_prop'] * 100,
        color=COLORS.get(cname, '#888'),
        s=110,
        zorder=4,
        edgecolors='black',
        linewidth=0.7,
        marker='o',
    )
    ax1.annotate(
        cname,
        (cd['elf'],
         cd['median_prop'] * 100),
        fontsize=7.5,
        xytext=(5, 4),
        textcoords='offset points',
    )

# Plot new points (stars)
for cname, res in new_results.items():
    ax1.scatter(
        res['elf'],
        res['median_prop'] * 100,
        color=COLORS.get(cname, '#e74c3c'),
        s=160,
        zorder=5,
        edgecolors='black',
        linewidth=1.0,
        marker='*',
        label=f"{cname} (NEW)",
    )
    ax1.annotate(
        f"{cname} ★",
        (res['elf'],
         res['median_prop'] * 100),
        fontsize=8,
        fontweight='bold',
        xytext=(5, 5),
        textcoords='offset points',
        color=COLORS.get(cname, '#e74c3c'),
    )

    # Add predicted range band
    lo, hi = (
        NEW_CENTERS[cname]['predicted_range']
    )
    ax1.axhspan(
        lo * 100, hi * 100,
        alpha=0.07,
        color=COLORS.get(cname, '#888'),
        label=(
            f"{cname} predicted range"
        ),
    )

# Regression line on all points
all_xs = (
    [v['elf'] for v in
     EXISTING_RESULTS.values()]
    + [r['elf'] for r in
       new_results.values()]
)
all_ys = (
    [v['median_prop'] * 100 for v in
     EXISTING_RESULTS.values()]
    + [r['median_prop'] * 100 for r in
       new_results.values()]
)
if len(all_xs) >= 3:
    z = np.polyfit(all_xs, all_ys, 1)
    xfit = np.linspace(
        min(all_xs) - 5,
        max(all_xs) + 5,
        100,
    )
    ax1.plot(
        xfit,
        np.polyval(z, xfit),
        color='#2c3e50',
        linewidth=1.8,
        alpha=0.5,
        linestyle='--',
        label='Regression (extended)',
    )

# Also original regression
orig_xs = [
    v['elf'] for v in
    EXISTING_RESULTS.values()
]
orig_ys = [
    v['median_prop'] * 100 for v in
    EXISTING_RESULTS.values()
]
if len(orig_xs) >= 3:
    z2 = np.polyfit(orig_xs, orig_ys, 1)
    ax1.plot(
        xfit,
        np.polyval(z2, xfit),
        color='#7f8c8d',
        linewidth=1.2,
        alpha=0.4,
        linestyle=':',
        label='Regression (original)',
    )

if corr_extended:
    rs = corr_extended['r_s']
    ps = corr_extended['p_s']
    sig = corr_extended['sig']
    title_str = (
        f"Extended: r={rs:+.3f},"
        f" p={ps:.3f} {sig}"
    )
elif corr_original:
    rs = corr_original['r_s']
    ps = corr_original['p_s']
    sig = corr_original['sig']
    title_str = (
        f"Original only: r={rs:+.3f},"
        f" p={ps:.3f} {sig}"
    )
else:
    title_str = "Correlation pending"

ax1.set_title(
    f"Wildtype C57BL/6N "
    f"Thigmotaxis Proportion vs ELF\n"
    f"{title_str}\n"
    f"★ = new center",
    fontsize=9,
)
ax1.set_xlabel(
    "ELF Score (composite estimate)",
    fontsize=9,
)
ax1.set_ylabel(
    "% Test Time in Periphery\n"
    "(wildtype median)",
    fontsize=9,
)
ax1.set_ylim(40, 102)
ax1.legend(fontsize=6.5, loc='upper right')
ax1.tick_params(labelsize=8)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.grid(
    axis='y', alpha=0.2,
    linewidth=0.5,
)


# ── Panel 2: Prediction check ──

ax2 = fig.add_subplot(gs[0, 2])

pred_centers = list(NEW_CENTERS.keys())
pred_vals = [
    NEW_CENTERS[c]['predicted_prop'] * 100
    for c in pred_centers
]
obs_vals = [
    new_results[c]['median_prop'] * 100
    if c in new_results else None
    for c in pred_centers
]

y_pos = np.arange(len(pred_centers))
bar_width = 0.35

ax2.barh(
    y_pos - bar_width / 2,
    pred_vals,
    height=bar_width,
    color='#bdc3c7',
    alpha=0.8,
    label='Predicted',
    edgecolor='white',
)

obs_colors = []
for c, obs in zip(
    pred_centers, obs_vals
):
    if obs is None:
        obs_colors.append('#e74c3c')
    else:
        lo, hi = (
            NEW_CENTERS[c]
            ['predicted_range']
        )
        obs_colors.append(
            '#27ae60'
            if lo * 100 <= obs <= hi * 100
            else '#e67e22'
        )

for i, (obs, col) in enumerate(
    zip(obs_vals, obs_colors)
):
    if obs is not None:
        ax2.barh(
            i + bar_width / 2,
            obs,
            height=bar_width,
            color=col,
            alpha=0.8,
            label=(
                'Observed (in range)'
                if col == '#27ae60'
                else 'Observed (out of range)'
            ),
            edgecolor='white',
        )
    else:
        ax2.barh(
            i + bar_width / 2,
            0,
            height=bar_width,
            color='#e74c3c',
            alpha=0.4,
            label='No data',
            edgecolor='white',
        )
        ax2.text(
            2, i + bar_width / 2,
            'NO DATA',
            va='center',
            fontsize=8,
            color='#e74c3c',
        )

ax2.set_yticks(y_pos)
ax2.set_yticklabels(
    pred_centers, fontsize=9
)
ax2.set_xlabel(
    "% Time in Periphery", fontsize=8
)
ax2.set_title(
    "Prediction vs Observation\n"
    "New Centers",
    fontsize=9,
)
ax2.tick_params(labelsize=7)

# De-duplicate legend
handles, labels = ax2.get_legend_handles_labels()
seen = set()
uniq_h, uniq_l = [], []
for h, l in zip(handles, labels):
    if l not in seen:
        uniq_h.append(h)
        uniq_l.append(l)
        seen.add(l)
ax2.legend(
    uniq_h, uniq_l,
    fontsize=6.5,
    loc='lower right',
)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)


# ── Panel 3: LOO extended ──

ax3 = fig.add_subplot(gs[1, 0])

if corr_extended and len(all_centers) >= 5:
    loo_data = []
    for drop in list(all_centers.keys()):
        sub = {
            k: v for k, v in
            all_centers.items()
            if k != drop
        }
        res = run_spearman(sub, drop)
        if res:
            loo_data.append({
                'dropped': drop,
                'r': res['r_s'],
                'p': res['p_s'],
                'sig': res['sig'],
            })

    if loo_data:
        loo_data.sort(key=lambda x: x['r'])
        loo_labels = [
            d['dropped'] for d in loo_data
        ]
        loo_rs = [d['r'] for d in loo_data]
        loo_cols = [
            '#27ae60'
            if d['sig'] != 'ns'
            else '#e74c3c'
            for d in loo_data
        ]
        y2 = np.arange(len(loo_labels))
        ax3.barh(
            y2, loo_rs,
            color=loo_cols,
            alpha=0.8,
            edgecolor='white',
        )
        if corr_extended:
            ax3.axvline(
                corr_extended['r_s'],
                color='black',
                linewidth=1.5,
                linestyle='--',
                alpha=0.5,
                label=(
                    f"Full r="
                    f"{corr_extended['r_s']:.3f}"
                ),
            )
        ax3.axvline(
            0, color='gray',
            linewidth=0.7, alpha=0.4
        )
        ax3.set_yticks(y2)
        ax3.set_yticklabels(
            loo_labels, fontsize=7
        )
        ax3.set_xlabel(
            "Spearman r", fontsize=8
        )
        ax3.set_title(
            "LOO Sensitivity\n"
            "Extended Set\n"
            "Green=sig, Red=ns",
            fontsize=8,
        )
        ax3.legend(fontsize=6.5)
        ax3.tick_params(labelsize=7)
        ax3.spines['top'].set_visible(False)
        ax3.spines['right'].set_visible(False)


# ── Panel 4: Full dose-response ──
# All centers sorted by ELF

ax4 = fig.add_subplot(gs[1, 1:])

all_plot = {**EXISTING_RESULTS}
for cname, res in new_results.items():
    all_plot[cname] = {
        'elf': res['elf'],
        'median_prop': res['median_prop'],
        'n_wt': res['n_wt'],
    }

sorted_plot = sorted(
    all_plot.items(),
    key=lambda x: x[1]['elf'],
)

elfs_plot  = [x[1]['elf'] for x in
              sorted_plot]
props_plot = [x[1]['median_prop'] * 100
              for x in sorted_plot]
names_plot = [x[0] for x in sorted_plot]
cols_plot  = [
    COLORS.get(n, '#888888')
    for n in names_plot
]
ns_plot = [
    x[1]['n_wt'] for x in sorted_plot
]

bars = ax4.bar(
    names_plot, props_plot,
    color=cols_plot,
    alpha=0.85,
    edgecolor='white',
    linewidth=0.5,
)

# Annotate with ELF score
for bar, elf, n in zip(
    bars, elfs_plot, ns_plot
):
    ax4.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.5,
        f"ELF={elf:.0f}\nN={n:,}",
        ha='center', va='bottom',
        fontsize=6.5,
        color='#2c3e50',
    )

# Mark new centers
for i, name in enumerate(names_plot):
    if name in new_results:
        bars[i].set_linewidth(2.5)
        bars[i].set_edgecolor('#e74c3c')

ax4.set_ylabel(
    "% Test Time in Periphery\n"
    "(wildtype median)",
    fontsize=9,
)
ax4.set_title(
    "Dose-Response: % Periphery by"
    " Facility ELF Score\n"
    "Sorted by ELF (low→high)."
    " Red border = new center.",
    fontsize=9,
)
ax4.set_ylim(0, 108)
ax4.tick_params(
    axis='x', labelsize=8,
    rotation=30,
)
ax4.tick_params(axis='y', labelsize=8)
ax4.spines['top'].set_visible(False)
ax4.spines['right'].set_visible(False)
ax4.grid(
    axis='y', alpha=0.2,
    linewidth=0.5,
)

fig.suptitle(
    "IMPC Open Field — Extended"
    " ELF Correlation\n"
    "KMPC + JAX Targeted Queries —"
    " OrganismCore — E.R. Lawson,"
    " February 2026",
    fontsize=10,
    fontweight='bold',
    y=0.995,
)

plt.savefig(
    'impc_extended_figures.png',
    dpi=200,
    bbox_inches='tight',
    facecolor='white',
)
log("Saved → impc_extended_figures.png")

with open(
    'impc_kmpc_jax_results.txt', 'w'
) as f:
    f.write("\n".join(results))
log("Saved → impc_kmpc_jax_results.txt")
log()
log("=" * 60)
log("SUMMARY OF WHAT TO READ:")
log()
log("  PREDICTION REPORT — Step 7:")
log("    Were KMPC and JAX in range?")
log()
log("  EXTENDED CORRELATION:")
log("    New Spearman r and p.")
log("    Did adding new centers")
log("    strengthen or weaken")
log("    the result?")
log()
log("  LOO extended:")
log("    Fragility reassessment.")
log("    Did fragility improve?")
log("=" * 60)
