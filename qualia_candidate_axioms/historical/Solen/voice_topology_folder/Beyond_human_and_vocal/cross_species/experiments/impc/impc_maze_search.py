"""
IMPC ANALYSIS 3 — STEP 8
MAZE PROCEDURE SEARCH IN DR23

Searches IMPC Data Release 23
for spatial navigation procedures
beyond the open field test.

Target procedures:
  Elevated plus maze
  Morris water maze
  Barnes maze
  Y-maze / T-maze
  Radial arm maze
  Fear conditioning
  Novel object recognition
  Any other spatial/anxiety
  procedure with multi-center
  coverage

Method:
  Step 1: Pull complete procedure
    list from IMPReSS API.
    Identify all procedures with
    'maze', 'fear', 'object',
    'spatial', 'water', 'arm',
    'novel', 'anxiety', 'plus'
    in procedure name.

  Step 2: For each candidate
    procedure, query the SOLR
    experiment core for:
      — Which centers have data
      — How many observations
      — Whether wildtype records
        exist
      — Whether thigmotaxis or
        spatial accuracy parameters
        are included

  Step 3: Score each procedure
    for analytical suitability:
      — N centers with data (want ≥4)
      — N wildtype records (want ≥500)
      — Spatial navigation relevance
        (direct > proxy)
      — Cross-center comparability
        (same protocol version)

  Step 4: For the top-scoring
    procedure, pull the full
    parameter list and sample
    data to confirm usability.

Output:
  impc_maze_search_results.txt
  impc_procedure_suitability.csv
  impc_best_procedure_sample.csv
"""

import requests
import pandas as pd
import numpy as np
import time
import json
import warnings
warnings.filterwarnings('ignore')

SOLR_BASE = (
    "https://www.ebi.ac.uk"
    "/mi/impc/solr/experiment/select"
)
IMPRESS_BASE = (
    "https://api.mousephenotype.org"
    "/impress"
)

# Search terms for candidate
# procedures
SEARCH_TERMS = [
    'maze',
    'plus',
    'elevated',
    'water',
    'barnes',
    'radial',
    'arm',
    'fear',
    'conditioning',
    'object',
    'recognition',
    'novel',
    'spatial',
    'anxiety',
    'locomotion',
    'startle',
    'prepulse',
    'passive',
    'avoidance',
    'active',
    'shuttle',
    'contextual',
    'cued',
    'rotarod',
    'balance',
    'grip',
]

# Relevance scoring weights
RELEVANCE = {
    # Direct spatial navigation
    'water maze':     10,
    'morris':         10,
    'barnes':          9,
    'radial':          8,
    'spatial':         8,
    # Anxiety / exploration
    'elevated':        7,
    'plus maze':       7,
    'fear':            6,
    'conditioning':    6,
    'contextual':      6,
    'novel':           5,
    'object':          5,
    'y-maze':          7,
    'ymaze':           7,
    't-maze':          7,
    'tmaze':           7,
    # Locomotion (indirect)
    'open field':      3,
    'locomotion':      3,
    'rotarod':         2,
}

# Centers already in our ELF dataset
ELF_CENTERS = {
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

results = []

def log(s=""):
    results.append(s)
    print(s)


def solr_facet(query, facet_field,
               facet_limit=50):
    """Get facet counts from SOLR."""
    params = {
        'q':              query,
        'rows':           0,
        'facet':          'true',
        'facet.field':    facet_field,
        'facet.limit':    facet_limit,
        'facet.mincount': 1,
        'wt':             'json',
    }
    try:
        r = requests.get(
            SOLR_BASE, params=params,
            timeout=60)
        r.raise_for_status()
        fc = (r.json()
              .get('facet_counts', {})
              .get('facet_fields', {})
              .get(facet_field, []))
        out = {}
        for i in range(0, len(fc), 2):
            out[fc[i]] = fc[i+1]
        return out
    except Exception as e:
        return {}


def solr_count(query):
    """Get total record count."""
    params = {
        'q':    query,
        'rows': 0,
        'wt':   'json',
    }
    try:
        r = requests.get(
            SOLR_BASE, params=params,
            timeout=60)
        r.raise_for_status()
        return (r.json()
                .get('response', {})
                .get('numFound', 0))
    except Exception:
        return 0


def solr_sample(query, n=50,
                fields=None):
    """Pull sample records."""
    fl = fields or [
        'procedure_stable_id',
        'procedure_name',
        'parameter_stable_id',
        'parameter_name',
        'phenotyping_center',
        'data_point',
        'zygosity',
        'observation_type',
    ]
    params = {
        'q':    query,
        'rows': n,
        'fl':   ','.join(fl),
        'wt':   'json',
    }
    try:
        r = requests.get(
            SOLR_BASE, params=params,
            timeout=60)
        r.raise_for_status()
        return (r.json()
                .get('response', {})
                .get('docs', []))
    except Exception:
        return []


# ─────────────────────────────────────────
# STEP 1: DISCOVER ALL PROCEDURES
# IN SOLR DR23
# ─────────────────────────────────────────

log("=" * 60)
log("IMPC DR23 MAZE PROCEDURE SEARCH")
log("=" * 60)
log()
log("Step 1: Discovering all procedures")
log("in SOLR experiment core...")
log()

# Get all procedure stable IDs
# with observation counts
all_procs = solr_facet(
    'observation_type:unidimensional',
    'procedure_stable_id',
    facet_limit=500,
)
log(
    f"  Total unique procedure IDs"
    f" in SOLR: {len(all_procs)}"
)
log()

# Get procedure names by pulling
# one record per procedure
log("  Fetching procedure names...")
log()

proc_names = {}
proc_sample_size = min(
    200, len(all_procs)
)

# Batch fetch procedure names
# using a broad query and facet
# on procedure_name
all_proc_names = solr_facet(
    'observation_type:unidimensional',
    'procedure_name',
    facet_limit=500,
)

log(
    f"  Total unique procedure names:"
    f" {len(all_proc_names)}"
)
log()

# Filter to candidate procedures
log("Step 2: Filtering candidate"
    " procedures...")
log()

candidates = {}

for proc_name, obs_count in (
    all_proc_names.items()
):
    name_lower = proc_name.lower()
    matched_terms = [
        t for t in SEARCH_TERMS
        if t in name_lower
    ]
    if matched_terms:
        # Compute relevance score
        rel_score = max(
            RELEVANCE.get(t, 1)
            for t in matched_terms
        )
        candidates[proc_name] = {
            'n_obs':       obs_count,
            'matched':     matched_terms,
            'relevance':   rel_score,
        }

log(
    f"  Candidate procedures found:"
    f" {len(candidates)}"
)
log()

# Sort by relevance then obs count
sorted_candidates = sorted(
    candidates.items(),
    key=lambda x: (
        -x[1]['relevance'],
        -x[1]['n_obs'],
    )
)

log(
    f"  {'Procedure':<45} "
    f"{'N_obs':>10} "
    f"{'Relevance':>10} "
    f"{'Matched':<25}"
)
log("  " + "─" * 95)

for pname, pdata in sorted_candidates:
    log(
        f"  {pname:<45} "
        f"{pdata['n_obs']:>10,} "
        f"{pdata['relevance']:>10} "
        f"{str(pdata['matched'][:3]):<25}"
    )

log()


# ─────────────────────────────────────────
# STEP 3: SCORE EACH CANDIDATE FOR
# ANALYTICAL SUITABILITY
# ─────────────────────────────────────────

log("=" * 60)
log("Step 3: Suitability scoring")
log("For each candidate procedure:")
log("  — N centers with data")
log("  — N wildtype records")
log("  — Center overlap with ELF set")
log("  — Spatial navigation relevance")
log("=" * 60)
log()

WT_STRINGS_LOWER = [
    'wild type', 'wildtype',
    'wild-type', 'wt',
]

suitability_rows = []

# Process top candidates by
# relevance (up to 20)
top_candidates = sorted_candidates[:20]

for pname, pdata in top_candidates:
    log(f"{'─'*50}")
    log(f"Procedure: {pname}")
    log(
        f"  Relevance: {pdata['relevance']}"
        f"  Total obs: {pdata['n_obs']:,}"
    )

    # Centers with this procedure
    centers_with_data = solr_facet(
        f'procedure_name:"{pname}"'
        f' AND observation_type:'
        f'unidimensional',
        'phenotyping_center',
        facet_limit=50,
    )

    n_centers = len(centers_with_data)
    elf_centers_present = [
        c for c in centers_with_data
        if c in ELF_CENTERS
    ]
    n_elf_overlap = len(elf_centers_present)

    # Wildtype count
    wt_filter = ' OR '.join([
        f'zygosity:"{s}"'
        for s in WT_STRINGS_LOWER
    ])
    n_wt = solr_count(
        f'procedure_name:"{pname}"'
        f' AND observation_type:'
        f'unidimensional'
        f' AND ({wt_filter})'
    )

    # Parameter count
    params_present = solr_facet(
        f'procedure_name:"{pname}"'
        f' AND observation_type:'
        f'unidimensional',
        'parameter_stable_id',
        facet_limit=100,
    )
    n_params = len(params_present)

    log(
        f"  Centers: {n_centers}  "
        f"ELF-overlap: {n_elf_overlap}  "
        f"Wildtype: {n_wt:,}  "
        f"Parameters: {n_params}"
    )
    log(
        f"  Centers present: "
        f"{list(centers_with_data.keys())}"
    )
    if elf_centers_present:
        log(
            f"  ELF centers: "
            f"{elf_centers_present}"
        )

    # Suitability score
    suit = (
        pdata['relevance'] * 3
        + min(n_centers, 10) * 2
        + min(n_elf_overlap, 6) * 4
        + min(n_wt // 500, 5) * 2
        + min(n_params, 10)
    )

    log(f"  Suitability score: {suit}")

    suitability_rows.append({
        'procedure_name':  pname,
        'relevance':       pdata['relevance'],
        'n_obs':           pdata['n_obs'],
        'n_centers':       n_centers,
        'n_elf_overlap':   n_elf_overlap,
        'elf_centers':     str(
            elf_centers_present
        ),
        'n_wildtype':      n_wt,
        'n_params':        n_params,
        'suitability':     suit,
    })

    time.sleep(0.3)

log()


# ─────────────────────────────────────────
# STEP 4: RANK AND REPORT
# ─────────────────────────────────────────

log("=" * 60)
log("Step 4: Ranked suitability table")
log("=" * 60)
log()

suit_df = pd.DataFrame(suitability_rows)
suit_df = suit_df.sort_values(
    'suitability', ascending=False
).reset_index(drop=True)

suit_df.to_csv(
    'impc_procedure_suitability.csv',
    index=False,
)

log(
    f"{'Rank':<5} "
    f"{'Procedure':<42} "
    f"{'Suit':>5} "
    f"{'Rel':>4} "
    f"{'Ctrs':>5} "
    f"{'ELF':>4} "
    f"{'N_wt':>8}"
)
log("─" * 78)

for rank, row in suit_df.iterrows():
    log(
        f"{rank+1:<5} "
        f"{row['procedure_name']:<42} "
        f"{row['suitability']:>5.0f} "
        f"{row['relevance']:>4.0f} "
        f"{row['n_centers']:>5} "
        f"{row['n_elf_overlap']:>4} "
        f"{row['n_wildtype']:>8,}"
    )

log()

# Identify best procedure
best = suit_df.iloc[0]
log(
    f"BEST PROCEDURE: "
    f"{best['procedure_name']}"
)
log(
    f"  Suitability: "
    f"{best['suitability']:.0f}"
)
log(
    f"  Centers: {best['n_centers']}"
    f"  ELF overlap: "
    f"{best['n_elf_overlap']}"
)
log(
    f"  Wildtype N: "
    f"{best['n_wildtype']:,}"
)
log()


# ─────────────────────────────────────────
# STEP 5: DEEP DIVE ON BEST PROCEDURE
# Pull full parameter list and
# sample data
# ─────────────────────────────────────────

log("=" * 60)
log("Step 5: Deep dive on top")
log("procedures (up to 3)")
log("=" * 60)
log()

top_n = min(3, len(suit_df))

for rank in range(top_n):
    row = suit_df.iloc[rank]
    pname = row['procedure_name']

    log(f"{'═'*50}")
    log(
        f"RANK {rank+1}: {pname}"
    )
    log(f"{'═'*50}")
    log()

    # Get all parameters for
    # this procedure
    params_fc = solr_facet(
        f'procedure_name:"{pname}"'
        f' AND observation_type:'
        f'unidimensional',
        'parameter_stable_id',
        facet_limit=200,
    )

    # Get parameter names by
    # pulling sample with
    # parameter_name field
    sample_docs = solr_sample(
        f'procedure_name:"{pname}"'
        f' AND observation_type:'
        f'unidimensional',
        n=500,
        fields=[
            'parameter_stable_id',
            'parameter_name',
            'phenotyping_center',
            'data_point',
            'zygosity',
        ],
    )

    if sample_docs:
        sample_df = pd.DataFrame(
            sample_docs
        )

        # Parameter name lookup
        if 'parameter_name' in (
            sample_df.columns
        ):
            param_labels = (
                sample_df
                .groupby('parameter_stable_id')
                ['parameter_name']
                .first()
                .to_dict()
            )
        else:
            param_labels = {}

        log("  Parameters available:")
        log(
            f"  {'PID':<30} "
            f"{'N_obs':>8} "
            f"{'Name':<40}"
        )
        log("  " + "─" * 82)

        # Flag spatial navigation
        # relevant parameters
        spatial_keywords = [
            'latency', 'path',
            'distance', 'time',
            'escape', 'probe',
            'platform', 'quadrant',
            'entry', 'entries',
            'arm', 'correct',
            'error', 'alternation',
            'freezing', 'immobil',
            'thigmotaxis', 'periphery',
            'center', 'inner',
            'outer', 'anxiety',
            'open', 'closed',
        ]

        for pid, cnt in sorted(
            params_fc.items(),
            key=lambda x: -x[1]
        ):
            plab = param_labels.get(
                pid, ''
            )
            flag = ""
            if any(
                kw in plab.lower()
                for kw in spatial_keywords
            ):
                flag = " ◄ SPATIAL"

            log(
                f"  {pid:<30} "
                f"{cnt:>8,} "
                f"{plab:<40}"
                f"{flag}"
            )

        log()

        # Center breakdown for
        # this procedure
        log("  Center coverage:")
        log(
            f"  {'Center':<25} "
            f"{'N_obs':>8} "
            f"{'ELF':>6} "
            f"{'N_wt':>8}"
        )
        log("  " + "─" * 52)

        centers_fc = solr_facet(
            f'procedure_name:"{pname}"'
            f' AND observation_type:'
            f'unidimensional',
            'phenotyping_center',
            facet_limit=50,
        )

        for center, cnt in sorted(
            centers_fc.items(),
            key=lambda x: -x[1]
        ):
            elf = ELF_CENTERS.get(
                center, None
            )
            elf_str = (
                f"{elf:.0f}"
                if elf is not None
                else "?"
            )

            # Wildtype count for this
            # center/procedure
            wt_filter = ' OR '.join([
                f'zygosity:"{s}"'
                for s in WT_STRINGS_LOWER
            ])
            n_wt_c = solr_count(
                f'procedure_name:"{pname}"'
                f' AND phenotyping_center:'
                f'"{center}"'
                f' AND observation_type:'
                f'unidimensional'
                f' AND ({wt_filter})'
            )

            flag_elf = (
                " ◄ ELF"
                if center in ELF_CENTERS
                else ""
            )

            log(
                f"  {center:<25} "
                f"{cnt:>8,} "
                f"{elf_str:>6} "
                f"{n_wt_c:>8,}"
                f"{flag_elf}"
            )
            time.sleep(0.15)

        log()

        # Spatial navigation assessment
        log("  Spatial navigation")
        log("  assessment:")

        spatial_params = [
            (pid, param_labels.get(pid, ''))
            for pid in params_fc
            if any(
                kw in param_labels.get(
                    pid, ''
                ).lower()
                for kw in spatial_keywords
            )
        ]

        if spatial_params:
            log(
                f"  {len(spatial_params)}"
                f" spatial-relevant "
                f"parameters found:"
            )
            for pid, lab in spatial_params:
                log(f"    {pid}: {lab}")
        else:
            log(
                "  No explicitly spatial"
                " parameters identified"
                " in sample."
            )

        log()

    time.sleep(0.3)


# ─────────────────────────────────────────
# STEP 6: ELEVATED PLUS MAZE
# TARGETED CHECK
# Always check EPM specifically
# even if not in top 3 by suitability
# ─────────────────────────────────────────

log("=" * 60)
log("Step 6: Elevated Plus Maze")
log("targeted check")
log("(canonical anxiety/exploration")
log(" measure — always verify)")
log("=" * 60)
log()

epm_terms = [
    'elevated plus',
    'plus maze',
    'Elevated Plus-maze',
    'EPM',
    'Plus Maze',
    'plus-maze',
]

epm_found = {}
for term in epm_terms:
    for pname in all_proc_names:
        if term.lower() in pname.lower():
            epm_found[pname] = (
                all_proc_names[pname]
            )

if epm_found:
    log("EPM procedures found:")
    for pname, cnt in epm_found.items():
        centers = solr_facet(
            f'procedure_name:"{pname}"',
            'phenotyping_center',
        )
        wt_filter = ' OR '.join([
            f'zygosity:"{s}"'
            for s in WT_STRINGS_LOWER
        ])
        n_wt = solr_count(
            f'procedure_name:"{pname}"'
            f' AND ({wt_filter})'
        )
        log(
            f"  '{pname}': "
            f"N={cnt:,}"
            f" centers={len(centers)}"
            f" wt={n_wt:,}"
        )
        log(
            f"    Centers: "
            f"{list(centers.keys())}"
        )
        elf_overlap = [
            c for c in centers
            if c in ELF_CENTERS
        ]
        log(
            f"    ELF overlap: "
            f"{elf_overlap}"
        )
else:
    log(
        "  No elevated plus maze"
        " procedures found."
    )

log()


# ─────────────────────────────────────────
# STEP 7: SUMMARY AND RECOMMENDATION
# ─────────────────────────────────────────

log("=" * 60)
log("STEP 7: SUMMARY AND RECOMMENDATION")
log("=" * 60)
log()

log("SEARCH COMPLETE.")
log()
log(
    f"Total procedures in DR23: "
    f"{len(all_proc_names)}"
)
log(
    f"Candidate procedures: "
    f"{len(candidates)}"
)
log(
    f"Scored for suitability: "
    f"{len(suitability_rows)}"
)
log()
log("TOP 5 BY SUITABILITY:")
log(
    f"{'Rank':<5} "
    f"{'Procedure':<42} "
    f"{'Suit':>5} "
    f"{'ELF_ctrs':>9} "
    f"{'N_wt':>8}"
)
log("─" * 72)
for rank, row in suit_df.head(5).iterrows():
    log(
        f"{rank+1:<5} "
        f"{row['procedure_name']:<42} "
        f"{row['suitability']:>5.0f} "
        f"{row['n_elf_overlap']:>9} "
        f"{row['n_wildtype']:>8,}"
    )

log()
log("RECOMMENDATION:")
log()

if len(suit_df) > 0:
    best = suit_df.iloc[0]
    n_elf = best['n_elf_overlap']
    n_wt  = best['n_wildtype']

    if n_elf >= 4 and n_wt >= 500:
        log(
            f"  PROCEED with "
            f"'{best['procedure_name']}'"
        )
        log(
            f"  {n_elf} ELF centers,"
            f" {n_wt:,} wildtype records."
        )
        log(
            f"  Run full proportion-"
            f"corrected ELF correlation"
        )
        log(
            f"  using same method as"
            f" primary OFD analysis."
        )
    elif n_elf >= 3 and n_wt >= 200:
        log(
            f"  MARGINAL: "
            f"'{best['procedure_name']}'"
        )
        log(
            f"  {n_elf} ELF centers —"
            f" borderline for correlation."
        )
        log(
            f"  Run analysis with"
            f" explicit N caveat."
        )
    else:
        log(
            "  NO PROCEDURE meets minimum"
        )
        log(
            "  criteria (≥4 ELF centers,"
        )
        log(
            "  ≥500 wildtype records)."
        )
        log(
            "  EUMODIC replication is"
        )
        log(
            "  the next best path."
        )

log()

with open(
    'impc_maze_search_results.txt', 'w'
) as f:
    f.write("\n".join(results))

log("Saved → impc_maze_search_results.txt")
log("Saved → impc_procedure_suitability.csv")
log()
log("=" * 60)
log("READ IN ORDER:")
log()
log("  Step 4: Ranked suitability table")
log("    Which procedure scores highest?")
log()
log("  Step 5: Deep dive results")
log("    For each top procedure:")
log("    — What parameters are available?")
log("    — Which centers have data?")
log("    — Are spatial navigation")
log("      parameters present?")
log()
log("  Step 6: EPM check")
log("    Is elevated plus maze present")
log("    with sufficient ELF center")
log("    coverage?")
log()
log("  Step 7: Recommendation")
log("    PROCEED / MARGINAL / NO")
log("=" * 60)
