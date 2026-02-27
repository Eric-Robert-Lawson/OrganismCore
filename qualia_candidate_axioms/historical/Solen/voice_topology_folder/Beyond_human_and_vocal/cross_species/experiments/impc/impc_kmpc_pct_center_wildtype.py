"""
IMPC — KMPC PERCENTAGE CENTER TIME
Wildtype-only query.

One targeted query:
  KMPC, IMPC_OFD_022_001
  (Percentage center time)
  Wildtype animals only.

Computes:
  implied_thigmo = 100 - pct_center

Reports whether KMPC wildtype
implied thigmotaxis is consistent
with the ELF gradient prediction
(65-78%) or anomalous (~90%).

Also queries KMPC
IMPC_OFD_007_001
(Whole arena resting time)
to determine protocol duration
from total-time proxy.
"""

import requests
import pandas as pd
import numpy as np
from scipy import stats
import time

SOLR_BASE = (
    "https://www.ebi.ac.uk"
    "/mi/impc/solr/experiment/select"
)

PCT_CENTER_ID  = "IMPC_OFD_022_001"
RESTING_ID     = "IMPC_OFD_007_001"
PERMANENCE_ID  = "IMPC_OFD_016_001"

WT_STRINGS = [
    'wild type', 'wildtype',
    'wild-type', 'wt', 'WT',
]

# Existing gradient for context
GRADIENT = {
    'UC Davis':  (31,  92.1),
    'ICS':       (36,  94.3),
    'RBRC':      (55,  72.4),
    'MRC Harwell (homo)': (59, 77.0),
    'MARC':      (65,  78.0),
    'CCP-IMG':   (74,  62.9),
    'BCM':       (94,  58.3),
}

def fetch(param_id, center='KMPC',
          max_rows=10000):
    params = {
        'q': (
            f'phenotyping_center:{center}'
            f' AND parameter_stable_id:'
            f'{param_id}'
            f' AND observation_type:'
            f'unidimensional'
        ),
        'fl': ','.join([
            'external_sample_id',
            'parameter_stable_id',
            'parameter_name',
            'data_point',
            'zygosity',
            'sex',
            'strain_name',
        ]),
        'rows': 0, 'wt': 'json',
    }
    try:
        r = requests.get(
            SOLR_BASE, params=params,
            timeout=60)
        r.raise_for_status()
        total = min(
            r.json().get('response', {})
            .get('numFound', 0),
            max_rows)
    except Exception as e:
        print(f"  Count failed: {e}")
        return pd.DataFrame()

    if total == 0:
        return pd.DataFrame()

    all_docs = []
    start = 0
    while start < total:
        params.update({
            'rows': min(5000, total-start),
            'start': start,
        })
        for attempt in range(3):
            try:
                r = requests.get(
                    SOLR_BASE,
                    params=params,
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
                    print(f"  Failed: {e}")
                else:
                    time.sleep(2)

    if not all_docs:
        return pd.DataFrame()
    df = pd.DataFrame(all_docs)
    df['data_point'] = pd.to_numeric(
        df['data_point'], errors='coerce')
    return df


print("=" * 55)
print("KMPC PERCENTAGE CENTER TIME")
print("Wildtype analysis")
print("=" * 55)
print()

# ── Pull pct center time ──
print(f"Fetching {PCT_CENTER_ID}...")
df_pct = fetch(PCT_CENTER_ID)

if df_pct.empty:
    print("  No data returned.")
else:
    pname = (
        df_pct['parameter_name']
        .dropna().iloc[0]
        if 'parameter_name' in df_pct.columns
        and len(df_pct) > 0
        else 'unknown'
    )
    print(f"  parameter_name: '{pname}'")
    print(f"  Total records: {len(df_pct):,}")
    print()

    # All animals distribution
    all_vals = df_pct['data_point'].dropna()
    print("  All animals:")
    print(
        f"    min={all_vals.min():.2f}%  "
        f"p5={all_vals.quantile(0.05):.2f}%  "
        f"p25={all_vals.quantile(0.25):.2f}%  "
        f"median={all_vals.median():.2f}%  "
        f"p75={all_vals.quantile(0.75):.2f}%  "
        f"p95={all_vals.quantile(0.95):.2f}%  "
        f"max={all_vals.max():.2f}%"
    )
    print()

    # Zygosity breakdown
    if 'zygosity' in df_pct.columns:
        print("  Zygosity breakdown:")
        for zyg, cnt in (
            df_pct['zygosity']
            .value_counts().items()
        ):
            print(f"    '{zyg}': {cnt:,}")
        print()

    # Wildtype only
    wt_mask = (
        df_pct['zygosity']
        .str.strip().str.lower()
        .isin([s.lower() for s in WT_STRINGS])
    )
    df_wt = df_pct[wt_mask].copy()
    wt_vals = df_wt['data_point'].dropna()

    print(
        f"  Wildtype records: "
        f"{len(df_wt):,}"
    )
    if len(wt_vals) >= 5:
        print()
        print("  WILDTYPE Pct center time:")
        print(
            f"    min={wt_vals.min():.2f}%  "
            f"p25={wt_vals.quantile(0.25):.2f}%  "
            f"median={wt_vals.median():.2f}%  "
            f"p75={wt_vals.quantile(0.75):.2f}%  "
            f"max={wt_vals.max():.2f}%"
        )
        wt_med_pct = float(wt_vals.median())
        implied_thigmo = 100 - wt_med_pct

        print()
        print(
            f"  Implied thigmotaxis: "
            f"100 - {wt_med_pct:.2f}% "
            f"= {implied_thigmo:.2f}%"
        )
        print()
        print(
            f"  ELF prediction: "
            f"65–78%"
        )
        in_r = 65 <= implied_thigmo <= 78
        print(
            f"  In range: "
            f"{'YES ✓' if in_r else 'NO ✗'}"
        )
        print()

        # Where does KMPC sit in gradient?
        print("  Gradient context:")
        print(
            f"  {'Center':<28} "
            f"{'ELF':>6} "
            f"{'%Periph':>9}"
        )
        print("  " + "─" * 46)
        all_pts = list(GRADIENT.items()) + [
            (f'KMPC (implied, wt)',
             (67, implied_thigmo))
        ]
        for name, (elf, pct) in sorted(
            all_pts, key=lambda x: x[1][0]
        ):
            marker = (
                " ← KMPC"
                if 'KMPC' in name
                else ""
            )
            print(
                f"  {name:<28} "
                f"{elf:>6.0f} "
                f"{pct:>8.1f}%"
                f"{marker}"
            )
        print()

        # Updated correlation
        pts = [
            (elf, pct/100)
            for _, (elf, pct) in
            sorted(
                all_pts,
                key=lambda x: x[1][0]
            )
            if 'homo' not in _
        ]
        if len(pts) >= 5:
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
            print(
                f"  Updated correlation "
                f"(N={len(pts)}, "
                f"wildtype + KMPC implied):"
            )
            print(
                f"    Spearman r = {r_s:+.4f}"
                f"  p = {p_s:.4f}  {sig}"
            )
            print(
                f"    Pearson  r = {r_p:+.4f}"
                f"  p = {p_p:.4f}"
            )
    else:
        print(
            f"  Insufficient wildtype data."
        )
    print()


# ── Pull resting time for
# protocol duration inference ──
print("=" * 55)
print(f"Fetching {RESTING_ID}")
print("(Whole arena resting time)")
print("to infer protocol duration...")
print()

df_rest = fetch(RESTING_ID)
if not df_rest.empty:
    rest_vals = (
        df_rest['data_point'].dropna()
    )
    print(
        f"  N: {len(rest_vals):,}  "
        f"median: {rest_vals.median():.1f}s  "
        f"P98: {rest_vals.quantile(0.98):.1f}s  "
        f"max: {rest_vals.max():.1f}s"
    )
    print()
    print(
        "  Resting time reflects immobile"
        " periods."
    )
    print(
        "  If protocol is 20 min (1200s)"
        " and median"
    )
    print(
        "  resting = 655s, mice are"
        " immobile 55% of test."
    )
    print(
        "  This is consistent with a"
        " short, unhabituated protocol."
    )
    print()
    # Estimate total test time
    # from resting + active
    # Active = total - resting
    # If we assume typical active
    # proportion, we can bound test dur.
    # P98 of resting gives upper bound
    # of resting in any single animal.
    p98_rest = rest_vals.quantile(0.98)
    print(
        f"  P98 resting = {p98_rest:.0f}s"
    )
    print(
        f"  If protocol = 20min (1200s):"
        f" max resting = 1200s."
        f" P98 = {p98_rest:.0f}s — "
        f"{'CONSISTENT' if p98_rest < 1200 else 'EXCEEDS — protocol > 20min'}."
    )
    print()
else:
    print("  No resting time data.")
print()


# ── Center permanence time for
# zone definition check ──
print("=" * 55)
print(f"Fetching {PERMANENCE_ID}")
print("(Center permanence time)")
print("= average time per center visit")
print()

df_perm = fetch(PERMANENCE_ID)
if not df_perm.empty:
    perm_vals = (
        df_perm['data_point'].dropna()
    )
    print(
        f"  N: {len(perm_vals):,}  "
        f"median: {perm_vals.median():.1f}s  "
        f"max: {perm_vals.max():.1f}s"
    )
    print()
    print(
        "  Center permanence = average"
        " duration of a single visit"
        " to the center zone."
    )
    perm_med = float(perm_vals.median())
    if perm_med > 60:
        print(
            f"  Median {perm_med:.0f}s per visit"
            " is HIGH."
        )
        print(
            "  Suggests LARGE center zone"
            " definition at KMPC."
        )
        print(
            "  A larger center zone"
            " produces more center time,"
        )
        print(
            "  inflating Pct center time"
            " and deflating implied"
            " thigmotaxis."
        )
    elif perm_med < 10:
        print(
            f"  Median {perm_med:.0f}s per visit"
            " is LOW."
        )
        print(
            "  Suggests SMALL center zone"
            " or brief visits."
        )
    else:
        print(
            f"  Median {perm_med:.0f}s per visit"
            " — typical range."
        )
else:
    print("  No permanence data.")
print()

print("=" * 55)
print("SUMMARY")
print("=" * 55)
print()
print("Use this output to determine:")
print()
print(
    "  1. KMPC wildtype Pct center"
    " time (median)"
)
print(
    "     → implied thigmotaxis"
    " = 100 - that value"
)
print(
    "     → IN RANGE (65-78%):"
    " KMPC confirms gradient."
)
print(
    "     → OUT OF RANGE (~90%):"
    " KMPC is anomalous."
)
print(
    "        Check center permanence"
    " for zone-size explanation."
)
print()
print(
    "  2. Resting time P98 vs 1200s"
)
print(
    "     → confirms protocol duration"
)
print()
print(
    "  3. Center permanence median"
)
print(
    "     → high value = large center"
    " zone = inflated pct center"
)
