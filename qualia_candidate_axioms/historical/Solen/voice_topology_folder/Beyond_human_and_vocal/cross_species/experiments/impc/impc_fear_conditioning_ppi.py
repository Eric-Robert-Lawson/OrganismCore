"""
IMPC ANALYSIS 3 — STEP 9
FEAR CONDITIONING AND ACOUSTIC
STARTLE ELF CORRELATION

Two parallel analyses:

ANALYSIS A: Fear Conditioning
  Primary parameter:
    Context % Freezing Time
    (hippocampal context memory)
  Secondary parameters:
    Cue Tone % Freezing Time
    (amygdala cued memory)
    Conditioning Post-shock
    % Freezing Time
    (acquisition)
  Centers: UC Davis, ICS, KMPC,
    TCP, CCP-IMG
    (MRC Harwell excluded:
     no wildtype records)
  ELF range: 31–74

  Key question: Does facility
  ELF correlate with context
  freezing in the same direction
  as OFD thigmotaxis (anxiolytic)
  or opposite (memory impairment)?

ANALYSIS B: Acoustic Startle / PPI
  Primary parameter:
    % Pre-pulse inhibition Global
    (sensorimotor gating)
  Centers: UC Davis, ICS, RBRC,
    MARC, KMPC, TCP, CCP-IMG, BCM
    (10 ELF centers, 8 with WT)
  ELF range: 31–94

  Key question: Does facility ELF
  correlate with sensorimotor
  gating? Broader center coverage
  than either OFD or FEA.

Both analyses use wildtype C57BL/6N
animals only. Parameter IDs
harmonized across center-specific
namespaces by semantic equivalence.

Output:
  impc_fea_ppi_results.txt
  impc_fea_ppi_figures.png
  impc_fea_center_table.csv
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

# ── Parameter ID maps ──
# Context % Freezing per center
CONTEXT_PCT_IDS = {
    'UC Davis':    'IMPC_FEA_009_001',
    'TCP':         'IMPC_FEA_009_001',
    'CCP-IMG':     'IMPC_FEA_009_001',
    'ICS':         'ICS_FEA_009_001',
    'KMPC':        'KMPCLA_FEA_009_001',
    'MRC Harwell': 'HRWLLA_FEA_009_001',
}

# Cue tone % freezing per center
CUE_PCT_IDS = {
    'UC Davis':    'IMPC_FEA_021_001',
    'TCP':         'IMPC_FEA_021_001',
    'CCP-IMG':     'IMPC_FEA_021_001',
    'ICS':         'ICS_FEA_020_001',
    'KMPC':        'KMPCLA_FEA_021_001',
    'MRC Harwell': 'HRWLLA_FEA_021_001',
}

# Post-shock % freezing per center
SHOCK_PCT_IDS = {
    'UC Davis':    'IMPC_FEA_100_001',
    'TCP':         'IMPC_FEA_100_001',
    'CCP-IMG':     'IMPC_FEA_100_001',
    'ICS':         'IMPC_FEA_100_001',
    'KMPC':        'KMPCLA_FEA_100_001',
    'MRC Harwell': 'HRWLLA_FEA_100_001',
}

# Context - Baseline difference
# (net contextual learning)
CONTEXT_DIFF_IDS = {
    'UC Davis':    'IMPC_FEA_105_001',
    'TCP':         'IMPC_FEA_105_001',
    'CCP-IMG':     'IMPC_FEA_105_001',
    'ICS':         'IMPC_FEA_105_001',
    'KMPC':        'KMPCLA_FEA_105_001',
    'MRC Harwell': 'HRWLLA_FEA_105_001',
}

# PPI global per center
PPI_GLOBAL_IDS = {
    'UC Davis':    'IMPC_ACS_037_001',
    'TCP':         'IMPC_ACS_037_001',
    'CCP-IMG':     'IMPC_ACS_037_001',
    'ICS':         'IMPC_ACS_037_001',
    'KMPC':        'KMPCLA_ACS_037_001',
    'MARC':        'IMPC_ACS_037_001',
    'RBRC':        'IMPC_ACS_037_001',
    'BCM':         'BCMLA_ACS_037_001',
    'MRC Harwell': 'IMPC_ACS_037_001',
    'HMGU':        'HMGULA_ACS_037_001',
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


def fetch_param(
    center, param_id,
    max_rows=100000
):
    """
    Fetch all records for one
    center + parameter combination.
    Returns DataFrame with wildtype
    flag.
    """
    params = {
        'q': (
            f'phenotyping_center:'
            f'"{center}"'
            f' AND parameter_stable_id:'
            f'{param_id}'
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
            'parameter_stable_id',
            'parameter_name',
        ]),
        'rows': 0,
        'wt':   'json',
    }
    try:
        r = requests.get(
            SOLR_BASE, params=params,
            timeout=60)
        r.raise_for_status()
        total = min(
            r.json()
            .get('response', {})
            .get('numFound', 0),
            max_rows
        )
    except Exception as e:
        log(f"    Count failed: {e}")
        return pd.DataFrame()

    if total == 0:
        return pd.DataFrame()

    all_docs = []
    start = 0
    rows  = min(5000, total)
    while start < total:
        params.update({
            'rows': rows,
            'start': start,
        })
        for attempt in range(3):
            try:
                r = requests.get(
                    SOLR_BASE,
                    params=params,
                    timeout=120)
                r.raise_for_status()
                docs = (
                    r.json()
                    .get('response', {})
                    .get('docs', [])
                )
                all_docs.extend(docs)
                start += len(docs)
                time.sleep(0.2)
                break
            except Exception as e:
                if attempt == 2:
                    log(
                        f"    Page {start}"
                        f" failed: {e}"
                    )
                else:
                    time.sleep(2)

    if not all_docs:
        return pd.DataFrame()

    df = pd.DataFrame(all_docs)
    df['data_point'] = pd.to_numeric(
        df['data_point'], errors='coerce'
    )
    df['is_wildtype'] = (
        df['zygosity']
        .str.strip()
        .str.lower()
        .isin([s.lower() for s in WT_STRINGS])
    )
    return df


def analyze_parameter_set(
    param_id_map,
    param_label,
    analysis_label,
    expected_range=(0, 100),
    higher_means=None,
):
    """
    Pull data for all centers in
    param_id_map, compute wildtype
    medians, run Spearman correlation
    with ELF scores.

    higher_means: string describing
      what higher values indicate
      biologically.

    Returns dict with results.
    """
    log(f"{'─'*50}")
    log(f"Parameter: {param_label}")
    log(f"Analysis:  {analysis_label}")
    if higher_means:
        log(
            f"Higher values mean: "
            f"{higher_means}"
        )
    log()

    center_data = {}

    for center, pid in (
        param_id_map.items()
    ):
        elf = ELF_SCORES.get(
            center, None
        )
        if elf is None:
            continue

        log(
            f"  Fetching {center} "
            f"({pid})..."
        )
        df = fetch_param(center, pid)

        if df.empty:
            log(f"    No data.")
            continue

        df_wt = df[
            df['is_wildtype']
        ].copy()
        wt_vals = (
            df_wt['data_point'].dropna()
        )

        if len(wt_vals) < 5:
            log(
                f"    {len(wt_vals)} "
                f"wildtype records — skip"
            )
            continue

        med  = float(wt_vals.median())
        mean = float(wt_vals.mean())
        sd   = float(wt_vals.std())

        # Clip to expected range
        # for sanity check
        pct_out = float(
            (
                (wt_vals < expected_range[0])
                | (wt_vals > expected_range[1])
            ).mean() * 100
        )

        log(
            f"    N_wt={len(wt_vals):,}  "
            f"median={med:.2f}  "
            f"mean={mean:.2f}  "
            f"sd={sd:.2f}  "
            f"out_of_range={pct_out:.1f}%"
        )

        if pct_out > 20:
            log(
                f"    WARNING: "
                f"{pct_out:.1f}% of values"
                f" outside expected range"
                f" {expected_range}."
                f" Check units."
            )

        center_data[center] = {
            'center':   center,
            'elf':      elf,
            'pid':      pid,
            'n_wt':     len(wt_vals),
            'median':   med,
            'mean':     mean,
            'sd':       sd,
            'pct_out':  pct_out,
        }

    log()

    if len(center_data) < 4:
        log(
            f"  Only {len(center_data)}"
            f" centers — insufficient"
            f" for correlation."
        )
        return None

    # Correlation
    pts = [
        (v['elf'], v['median'])
        for v in center_data.values()
    ]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]

    r_s, p_s = stats.spearmanr(xs, ys)
    r_p, p_p = stats.pearsonr(xs, ys)

    sig = (
        "***" if p_s < 0.001 else
        "**"  if p_s < 0.01  else
        "*"   if p_s < 0.05  else "ns"
    )

    log(
        f"  Spearman r={r_s:+.4f}  "
        f"p={p_s:.4f}  {sig}  "
        f"N={len(pts)}"
    )
    log(
        f"  Pearson  r={r_p:+.4f}  "
        f"p={p_p:.4f}"
    )
    log()

    # Per-center table
    log(
        f"  {'Center':<22} "
        f"{'ELF':>6} "
        f"{'N_wt':>7} "
        f"{'Median':>9} "
        f"{'Mean':>9} "
        f"{'SD':>7}"
    )
    log("  " + "─" * 64)
    for cd in sorted(
        center_data.values(),
        key=lambda x: x['elf']
    ):
        log(
            f"  {cd['center']:<22} "
            f"{cd['elf']:>6.0f} "
            f"{cd['n_wt']:>7,} "
            f"{cd['median']:>9.3f} "
            f"{cd['mean']:>9.3f} "
            f"{cd['sd']:>7.3f}"
        )
    log()

    # LOO
    log("  Leave-one-out:")
    loo_sigs = 0
    loo_total = 0
    for drop in list(center_data.keys()):
        sub = [
            (v['elf'], v['median'])
            for k, v in center_data.items()
            if k != drop
        ]
        if len(sub) >= 4:
            r2, p2 = stats.spearmanr(
                [p[0] for p in sub],
                [p[1] for p in sub]
            )
            s2 = (
                "***" if p2 < 0.001 else
                "**"  if p2 < 0.01  else
                "*"   if p2 < 0.05  else
                "ns"
            )
            log(
                f"    drop {drop:<20} "
                f"r={r2:+.3f}  "
                f"p={p2:.4f}  {s2}"
            )
            loo_total += 1
            if s2 != 'ns':
                loo_sigs += 1

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
        f"  LOO: {loo_sigs}/{loo_total}"
        f" significant — {fragility}"
    )
    log()

    return {
        'label':        param_label,
        'analysis':     analysis_label,
        'n_centers':    len(pts),
        'r_s':          r_s,
        'p_s':          p_s,
        'r_p':          r_p,
        'p_p':          p_p,
        'sig':          sig,
        'fragility':    fragility,
        'loo_sigs':     loo_sigs,
        'loo_total':    loo_total,
        'center_data':  center_data,
        'xs':           xs,
        'ys':           ys,
        'higher_means': higher_means,
    }


# ─────────────────────────────────────────
# ANALYSIS A: FEAR CONDITIONING
# ─────────────────────────────────────────

log("=" * 60)
log("ANALYSIS A: FEAR CONDITIONING")
log("=" * 60)
log()
log("Biological framework:")
log("  Contextual fear conditioning")
log("  requires the hippocampus to")
log("  form a spatial-contextual")
log("  memory associating the test")
log("  chamber with aversive shock.")
log()
log("  Context % Freezing = memory")
log("  of the dangerous context.")
log("  Higher = better contextual")
log("  memory = more hippocampal")
log("  consolidation.")
log()
log("  If ELF impairs hippocampal")
log("  LTP: high-ELF centers should")
log("  show LOWER context freezing.")
log("  r negative = impairment signal.")
log()
log("  If ELF produces general")
log("  anxiolysis (OFD result):")
log("  high-ELF centers may show")
log("  LOWER freezing also — but")
log("  for a different reason.")
log()
log("  Cue tone freezing (amygdala)")
log("  vs context freezing (hippocampus)")
log("  dissociation is the key test.")
log("  If BOTH are equally reduced:")
log("    general anxiolysis.")
log("  If CONTEXT reduced more than")
log("  CUE: hippocampal-specific.")
log()

fea_results = {}

for param_label, id_map, higher, eid in [
    (
        "Context % Freezing",
        CONTEXT_PCT_IDS,
        "better hippocampal context memory",
        "context"
    ),
    (
        "Cue Tone % Freezing",
        CUE_PCT_IDS,
        "better amygdala cued memory",
        "cue"
    ),
    (
        "Post-shock % Freezing",
        SHOCK_PCT_IDS,
        "stronger immediate fear response",
        "shock"
    ),
    (
        "Context minus Baseline diff",
        CONTEXT_DIFF_IDS,
        "net contextual learning above baseline",
        "diff"
    ),
]:
    res = analyze_parameter_set(
        id_map,
        param_label,
        "Fear Conditioning vs ELF",
        expected_range=(0, 100),
        higher_means=higher,
    )
    fea_results[eid] = res


# ─────────────────────────────────────────
# ANALYSIS B: ACOUSTIC STARTLE / PPI
# ─────────────────────────────────────────

log("=" * 60)
log("ANALYSIS B: ACOUSTIC STARTLE / PPI")
log("=" * 60)
log()
log("Biological framework:")
log("  Prepulse inhibition (PPI)")
log("  measures sensorimotor gating")
log("  — the brain's ability to")
log("  suppress a startle response")
log("  when preceded by a weak")
log("  prepulse stimulus.")
log()
log("  Higher PPI % = stronger")
log("  sensorimotor gating = more")
log("  intact thalamo-cortical")
log("  filtering.")
log()
log("  ELF effects on PPI are")
log("  plausible via thalamic and")
log("  brainstem circuits.")
log()
log("  10 ELF centers available")
log("  (vs 6 for OFD, 5 for FEA).")
log("  Highest statistical power")
log("  of any procedure in DR23.")
log()

ppi_res = analyze_parameter_set(
    PPI_GLOBAL_IDS,
    "% PPI Global",
    "Acoustic Startle / PPI vs ELF",
    expected_range=(-200, 100),
    higher_means=(
        "stronger sensorimotor gating"
    ),
)


# ─────────────────────────────────────────
# CROSS-ANALYSIS SUMMARY
# ─────────────────────────────────────────

log("=" * 60)
log("CROSS-ANALYSIS SUMMARY")
log("=" * 60)
log()

# OFD reference result
OFD = {
    'label':      "OFD Thigmotaxis Proportion",
    'r_s':        -0.8857,
    'p_s':         0.0188,
    'sig':        "*",
    'n_centers':   6,
    'fragility':  "FRAGILE (4/6 LOO)",
    'direction':  "NEGATIVE (anxiolytic)",
}

log(
    f"{'Analysis':<35} "
    f"{'N':>4} "
    f"{'r_S':>8} "
    f"{'p_S':>8} "
    f"{'sig':>4} "
    f"{'Fragility':<20}"
)
log("─" * 83)

# OFD
log(
    f"{'OFD Thigmotaxis (primary)':<35} "
    f"{OFD['n_centers']:>4} "
    f"{OFD['r_s']:>+8.4f} "
    f"{OFD['p_s']:>8.4f} "
    f"{OFD['sig']:>4} "
    f"{OFD['fragility']:<20}"
)

# Fear conditioning results
for eid, res in fea_results.items():
    if res:
        log(
            f"{'FEA '+res['label']:<35} "
            f"{res['n_centers']:>4} "
            f"{res['r_s']:>+8.4f} "
            f"{res['p_s']:>8.4f} "
            f"{res['sig']:>4} "
            f"{res['fragility']:<20}"
        )

# PPI
if ppi_res:
    log(
        f"{'PPI Global':<35} "
        f"{ppi_res['n_centers']:>4} "
        f"{ppi_res['r_s']:>+8.4f} "
        f"{ppi_res['p_s']:>8.4f} "
        f"{ppi_res['sig']:>4} "
        f"{ppi_res['fragility']:<20}"
    )

log()

# Interpretation of cross-analysis
# pattern
log("CROSS-ANALYSIS INTERPRETATION:")
log()

context_res = fea_results.get('context')
cue_res     = fea_results.get('cue')

if context_res and cue_res:
    ctx_sig = context_res['sig'] != 'ns'
    cue_sig = cue_res['sig'] != 'ns'
    same_dir = (
        (context_res['r_s'] > 0)
        == (cue_res['r_s'] > 0)
    )

    if ctx_sig and cue_sig and same_dir:
        log(
            "  Both context (hippocampal)"
            " and cue (amygdala)"
            " freezing correlate with"
            " ELF in the same direction."
        )
        log(
            "  → General arousal/anxiety"
            " effect, not region-specific."
        )
        if context_res['r_s'] < 0:
            log(
                "  → Negative direction:"
                " high ELF → less freezing."
                " Consistent with OFD"
                " anxiolytic result."
            )
        else:
            log(
                "  → Positive direction:"
                " high ELF → more freezing."
                " Inconsistent with OFD."
                " Investigate."
            )
    elif ctx_sig and not cue_sig:
        log(
            "  Context freezing correlates"
            " with ELF but cue freezing"
            " does not."
        )
        log(
            "  → Hippocampal-specific"
            " effect. Context memory"
            " (hippocampus) is ELF-"
            " sensitive. Amygdala cued"
            " memory is not."
        )
        log(
            "  → This is the strongest"
            " possible pattern for the"
            " hippocampal ELF hypothesis."
        )
    elif not ctx_sig and not cue_sig:
        log(
            "  Neither context nor cue"
            " freezing correlates with"
            " ELF significantly."
        )
        log(
            "  → Fear memory circuits"
            " are not ELF-sensitive in"
            " this dataset."
        )
        log(
            "  → OFD result is"
            " anxiety-behavior specific."
            " Not generalized to memory."
        )
    else:
        log(
            "  Mixed pattern — see"
            " individual results above."
        )


# ─────────────────────────────────────────
# FIGURES
# ─────────────────────────────────────────

log()
log("Building figures...")

fig = plt.figure(
    figsize=(18, 12), dpi=120
)
fig.patch.set_facecolor('white')
gs = gridspec.GridSpec(
    3, 4, figure=fig,
    hspace=0.46, wspace=0.36
)


def scatter_panel(
    ax, res, title,
    ylabel, ref_line=None
):
    """Standard scatter panel."""
    if res is None:
        ax.text(
            0.5, 0.5,
            "No data",
            ha='center', va='center',
            transform=ax.transAxes,
            fontsize=10, color='gray'
        )
        ax.set_title(title, fontsize=8)
        return

    xs = res['xs']
    ys = res['ys']
    cd = res['center_data']

    clrs = [
        COLORS.get(c, '#888888')
        for c in sorted(
            cd, key=lambda c:
            cd[c]['elf']
        )
    ]

    ax.scatter(
        xs, ys,
        c=clrs, s=90, zorder=4,
        edgecolors='black',
        linewidth=0.6,
    )
    for c, v in cd.items():
        ax.annotate(
            c,
            (v['elf'], v['median']),
            fontsize=6,
            xytext=(4, 3),
            textcoords='offset points',
        )

    if len(xs) >= 3:
        z = np.polyfit(xs, ys, 1)
        xfit = np.linspace(
            min(xs)-3, max(xs)+3, 100
        )
        ax.plot(
            xfit, np.polyval(z, xfit),
            color='#2c3e50',
            linewidth=1.5,
            alpha=0.5,
            linestyle='--',
        )

    if ref_line is not None:
        ax.axhline(
            ref_line,
            color='#e74c3c',
            linewidth=0.8,
            linestyle=':',
            alpha=0.6,
        )

    sig = res['sig']
    color = (
        '#27ae60' if sig != 'ns'
        else '#7f8c8d'
    )

    ax.set_title(
        f"{title}\n"
        f"r={res['r_s']:+.3f},"
        f" p={res['p_s']:.3f} {sig}",
        fontsize=8,
        color=color,
    )
    ax.set_xlabel(
        "ELF Score", fontsize=8
    )
    ax.set_ylabel(ylabel, fontsize=8)
    ax.tick_params(labelsize=7)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)


# Row 0: Fear conditioning panels
scatter_panel(
    fig.add_subplot(gs[0, 0]),
    fea_results.get('context'),
    "Context % Freezing vs ELF\n"
    "(hippocampal memory)",
    "Context % Freezing (wildtype)",
)
scatter_panel(
    fig.add_subplot(gs[0, 1]),
    fea_results.get('cue'),
    "Cue % Freezing vs ELF\n"
    "(amygdala memory)",
    "Cue % Freezing (wildtype)",
)
scatter_panel(
    fig.add_subplot(gs[0, 2]),
    fea_results.get('shock'),
    "Post-shock % Freezing vs ELF\n"
    "(acquisition)",
    "Post-shock % Freezing",
)
scatter_panel(
    fig.add_subplot(gs[0, 3]),
    fea_results.get('diff'),
    "Context–Baseline Diff vs ELF\n"
    "(net contextual learning)",
    "Context–Baseline diff (pp)",
    ref_line=0,
)

# Row 1: PPI panels
scatter_panel(
    fig.add_subplot(gs[1, :2]),
    ppi_res,
    "% PPI Global vs ELF\n"
    "(sensorimotor gating — "
    "10 ELF centers)",
    "% Pre-pulse Inhibition",
)

# OFD reference (Row 1 right)
ax_ofd = fig.add_subplot(gs[1, 2:])
ofd_data = {
    'UC Davis':  (31.0, 92.1),
    'ICS':       (36.0, 94.3),
    'RBRC':      (55.0, 72.4),
    'MARC':      (65.0, 78.0),
    'CCP-IMG':   (74.0, 62.9),
    'BCM':       (94.0, 58.3),
}
for name, (elf, pct) in (
    ofd_data.items()
):
    ax_ofd.scatter(
        elf, pct,
        color=COLORS.get(name, '#888'),
        s=90, zorder=4,
        edgecolors='black',
        linewidth=0.6,
    )
    ax_ofd.annotate(
        name, (elf, pct),
        fontsize=6,
        xytext=(4, 3),
        textcoords='offset points',
    )
xs_o = [v[0] for v in ofd_data.values()]
ys_o = [v[1] for v in ofd_data.values()]
z_o = np.polyfit(xs_o, ys_o, 1)
xf_o = np.linspace(
    min(xs_o)-3, max(xs_o)+3, 100
)
ax_ofd.plot(
    xf_o, np.polyval(z_o, xf_o),
    color='#2c3e50', linewidth=1.5,
    alpha=0.5, linestyle='--',
)
ax_ofd.set_title(
    "OFD Thigmotaxis vs ELF\n"
    "(primary result: r=-0.886,"
    " p=0.019 *)",
    fontsize=8, color='#27ae60',
)
ax_ofd.set_xlabel(
    "ELF Score", fontsize=8
)
ax_ofd.set_ylabel(
    "% Time in Periphery",
    fontsize=8
)
ax_ofd.tick_params(labelsize=7)
ax_ofd.spines['top'].set_visible(False)
ax_ofd.spines['right'].set_visible(False)

# Row 2: Summary panel
ax_sum = fig.add_subplot(gs[2, :])
ax_sum.axis('off')

sum_lines = [
    "MULTI-PROCEDURE ELF CORRELATION"
    " SUMMARY — ANALYSIS 3",
    "─" * 100,
    "",
    f"{'Procedure':<38}"
    f"{'N_ctr':>6}"
    f"{'Spearman_r':>12}"
    f"{'p':>10}"
    f"{'sig':>5}"
    f"{'Fragility':<22}"
    f"{'Direction'}",
    "─" * 100,
]

# OFD
sum_lines.append(
    f"{'OFD Thigmotaxis (primary)':<38}"
    f"{6:>6}"
    f"{-0.8857:>+12.4f}"
    f"{0.0188:>10.4f}"
    f"{'*':>5}"
    f"{'FRAGILE (4/6)':<22}"
    f"NEGATIVE (anxiolytic)"
)

for eid, label in [
    ('context', 'FEA Context % Freezing'),
    ('cue',     'FEA Cue % Freezing'),
    ('shock',   'FEA Post-shock % Freezing'),
    ('diff',    'FEA Context-Baseline diff'),
]:
    res = fea_results.get(eid)
    if res:
        dirn = (
            "NEGATIVE"
            if res['r_s'] < 0
            else "POSITIVE"
        )
        sum_lines.append(
            f"{label:<38}"
            f"{res['n_centers']:>6}"
            f"{res['r_s']:>+12.4f}"
            f"{res['p_s']:>10.4f}"
            f"{res['sig']:>5}"
            f"{res['fragility']:<22}"
            f"{dirn}"
        )
    else:
        sum_lines.append(
            f"{label:<38}"
            f"{'—':>6}"
            f"{'—':>12}"
            f"{'—':>10}"
            f"{'—':>5}"
            f"{'no data':<22}"
        )

if ppi_res:
    dirn = (
        "NEGATIVE"
        if ppi_res['r_s'] < 0
        else "POSITIVE"
    )
    sum_lines.append(
        f"{'PPI Global (startle)':<38}"
        f"{ppi_res['n_centers']:>6}"
        f"{ppi_res['r_s']:>+12.4f}"
        f"{ppi_res['p_s']:>10.4f}"
        f"{ppi_res['sig']:>5}"
        f"{ppi_res['fragility']:<22}"
        f"{dirn}"
    )

for i, line in enumerate(sum_lines):
    col = (
        '#27ae60'
        if '***' in line
        or '**' in line
        or ('*' in line
            and 'ns' not in line
            and '0.0' in line)
        else '#7f8c8d'
        if '—' in line
        else 'black'
    )
    ax_sum.text(
        0.01,
        0.97 - i * 0.115,
        line,
        transform=ax_sum.transAxes,
        fontsize=7,
        fontfamily='monospace',
        va='top',
        color=col,
    )

fig.suptitle(
    "IMPC Analysis 3 — Multi-Procedure"
    " ELF Correlation\n"
    "Fear Conditioning + Acoustic"
    " Startle/PPI — "
    "OrganismCore — E.R. Lawson,"
    " February 2026",
    fontsize=10, fontweight='bold',
    y=0.998,
)

plt.savefig(
    'impc_fea_ppi_figures.png',
    dpi=200, bbox_inches='tight',
    facecolor='white',
)
log("Saved → impc_fea_ppi_figures.png")

# Save center table
all_rows = []
for eid, res in fea_results.items():
    if res:
        for c, v in (
            res['center_data'].items()
        ):
            all_rows.append({
                'procedure': 'FEA',
                'parameter': res['label'],
                **v
            })
if ppi_res:
    for c, v in (
        ppi_res['center_data'].items()
    ):
        all_rows.append({
            'procedure': 'PPI',
            'parameter': ppi_res['label'],
            **v
        })

pd.DataFrame(all_rows).to_csv(
    'impc_fea_ppi_center_table.csv',
    index=False,
)
log("Saved → impc_fea_ppi_center_table.csv")

with open(
    'impc_fea_ppi_results.txt', 'w'
) as f:
    f.write("\n".join(results))
log("Saved → impc_fea_ppi_results.txt")
log()
log("=" * 60)
log("THE DECISIVE RESULTS TO READ:")
log()
log("  Context vs Cue dissociation:")
log("    If context r significant")
log("    and cue r not significant:")
log("    → hippocampal-specific ELF")
log("      effect. Strongest result")
log("      possible for this series.")
log()
log("    If both significant, same dir:")
log("    → general arousal change,")
log("      consistent with OFD.")
log()
log("    If neither significant:")
log("    → ELF effect is anxiety-")
log("      specific. OFD result holds")
log("      but does not generalize")
log("      to fear memory.")
log()
log("  PPI correlation:")
log("    With 10 ELF centers this is")
log("    the highest-power test in")
log("    the analysis. If significant,")
log("    it is the most robust result")
log("    in the entire series.")
log("=" * 60)
