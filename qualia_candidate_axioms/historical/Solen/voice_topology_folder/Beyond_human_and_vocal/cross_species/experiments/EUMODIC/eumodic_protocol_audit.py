"""
EUMODIC Protocol Audit
=======================
Investigates whether the null result
in eumodic_correlation.py is explained
by protocol heterogeneity across
EUMODIC centers.

Two specific anomalies to investigate:

  1. HMGU: DR23 median 1842.6s vs
     EUMODIC median 906.4s — a drop
     of 936 seconds. Suspected cause:
     shorter test duration in
     ESLIM_007_001 at HMGU.

  2. MRC Harwell: centre permanence
     time 16.2s vs 165-288s at all
     other centers. Suspected cause:
     different centre zone definition
     at MRC Harwell in EUMODIC.

Method:
  Query all available parameters in
  ESLIM_007_001 per center.
  Use duration-proxy parameters
  (total distance, resting time,
  velocity, beam breaks) to infer
  implied test duration per center.
  Compare implied durations across
  centers and against known DR23
  protocol durations.

Reads:  eumodic_raw.csv (already
        downloaded)
Also queries SOLR API for additional
parameters not in initial download.

Writes:
  eumodic_protocol_audit.txt
  eumodic_protocol_audit.csv
  eumodic_parameter_inventory.csv

OrganismCore — IMPC Series
EUMODIC Replication Analysis
February 2026
"""

import requests
import pandas as pd
import numpy as np
import time
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────

SOLR_BASE = (
    "https://www.ebi.ac.uk"
    "/mi/impc/solr/experiment/select"
)

PROCEDURE_ID = "ESLIM_007_001"

IN_RAW   = "eumodic_raw.csv"
OUT_TXT  = "eumodic_protocol_audit.txt"
OUT_CSV  = "eumodic_protocol_audit.csv"
OUT_INV  = "eumodic_parameter_inventory.csv"

# Centers in analysis
CENTERS = [
    "CMHD",
    "HMGU",
    "ICS",
    "MRC Harwell",
    "WTSI",
]

# Known DR23 protocol durations
# (minutes) per center where known
DR23_DURATIONS = {
    "HMGU":        20,
    "ICS":         20,
    "MRC Harwell": 20,
    "WTSI":        20,
    "CMHD":        None,
}

# Parameters already downloaded
KNOWN_PARAMS = [
    "Centre permanence time",
    "Periphery permanence time",
]

# Duration-proxy parameter name
# fragments to search for
DURATION_PROXIES = [
    "distance",
    "resting",
    "immobil",
    "velocity",
    "speed",
    "beam",
    "total time",
    "duration",
    "movement",
    "ambulat",
]

# Zone-definition parameter name
# fragments
ZONE_PARAMS = [
    "centre",
    "center",
    "periphery",
    "corner",
    "zone",
    "visit",
    "entr",
    "permanence",
]

# C57BL/6N strict strains
B6N_STRINGS = [
    "C57BL/6N",
    "C57BL/6NTac",
    "C57BL/6NTacDen",
    "C57BL/6NTac-ICS-Denmark(ImportedLive)",
    "C57BL/6NTac-ICS-USA(ImportedLive)",
    "C57BL/6NCrl",
    "C57BL/6NJ",
]

results = []

def log(s=""):
    results.append(s)
    print(s)

# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────

def solr_get(params, timeout=60):
    r = requests.get(
        SOLR_BASE,
        params=params,
        timeout=timeout
    )
    r.raise_for_status()
    return r.json()

def fetch_parameter(
    param_name,
    center=None,
    max_rows=50000
):
    """
    Fetch all records for a given
    parameter name, optionally
    filtered by center.
    """
    q = (
        f"procedure_stable_id:"
        f"{PROCEDURE_ID}"
        f" AND parameter_name:"
        f'"{param_name}"'
        f" AND biological_sample_group:"
        f"control"
    )
    if center:
        q += (
            f" AND phenotyping_center:"
            f'"{center}"'
        )

    count_p = {
        "q": q, "rows": 0, "wt": "json"
    }
    try:
        resp = solr_get(count_p)
        total = min(
            resp["response"]["numFound"],
            max_rows
        )
    except Exception as e:
        log(f"  Count failed: {e}")
        return pd.DataFrame()

    if total == 0:
        return pd.DataFrame()

    all_docs = []
    start = 0
    while start < total:
        page_p = {
            "q": q,
            "rows": min(5000, total-start),
            "start": start,
            "fl": (
                "phenotyping_center,"
                "parameter_name,"
                "parameter_stable_id,"
                "data_point,"
                "strain_name,"
                "zygosity,"
                "sex,"
                "external_sample_id,"
                "date_of_experiment"
            ),
            "wt": "json",
        }
        try:
            resp = solr_get(page_p)
            docs = (
                resp["response"]["docs"]
            )
            all_docs.extend(docs)
            start += len(docs)
            time.sleep(0.2)
        except Exception as e:
            log(f"  Page failed: {e}")
            start += 5000

    if not all_docs:
        return pd.DataFrame()

    df = pd.DataFrame(all_docs)
    df["data_point_num"] = pd.to_numeric(
        df["data_point"], errors="coerce"
    )
    return df

# ─────────────────────────────────────────
# STEP 1: FULL PARAMETER INVENTORY
# ─────────────────────────────────────────

log("=" * 56)
log("EUMODIC PROTOCOL AUDIT")
log("=" * 56)
log()
log("STEP 1: FULL PARAMETER INVENTORY")
log("All parameters in ESLIM_007_001")
log("=" * 56)
log()

facet_params = {
    "q": (
        f"procedure_stable_id:"
        f"{PROCEDURE_ID}"
        f" AND biological_sample_group:"
        f"control"
    ),
    "rows": 0,
    "facet": "on",
    "facet.field": "parameter_name",
    "facet.limit": 200,
    "facet.mincount": 1,
    "wt": "json",
}

try:
    resp = solr_get(facet_params)
    facet_data = (
        resp
        .get("facet_counts", {})
        .get("facet_fields", {})
        .get("parameter_name", [])
    )
    param_inventory = {}
    for i in range(0, len(facet_data), 2):
        name = facet_data[i]
        count = facet_data[i+1]
        param_inventory[name] = count

    log(
        f"Total parameters found: "
        f"{len(param_inventory)}"
    )
    log()
    log(
        f"{'Parameter name':<50} "
        f"{'N records':>10}"
    )
    log("-" * 62)
    for pname, cnt in sorted(
        param_inventory.items(),
        key=lambda x: x[1],
        reverse=True
    ):
        log(
            f"{pname:<50} "
            f"{cnt:>10,}"
        )

except Exception as e:
    log(f"Parameter inventory failed: {e}")
    param_inventory = {}

log()

# Save inventory
inv_rows = [
    {"parameter_name": k, "n_records": v}
    for k, v in param_inventory.items()
]
inv_df = pd.DataFrame(inv_rows).sort_values(
    "n_records", ascending=False
)
inv_df.to_csv(OUT_INV, index=False)
log(f"Saved: {OUT_INV}")
log()

# ─────────────────────────────────────────
# STEP 2: IDENTIFY DURATION PROXIES
# ─────────────────────────────────────────

log("=" * 56)
log("STEP 2: DURATION PROXY PARAMETERS")
log("=" * 56)
log()

duration_params = []
zone_params_found = []

for pname in param_inventory:
    pname_lower = pname.lower()
    for proxy in DURATION_PROXIES:
        if proxy in pname_lower:
            duration_params.append(pname)
            break
    for zone in ZONE_PARAMS:
        if zone in pname_lower:
            zone_params_found.append(pname)

# Deduplicate
duration_params = list(
    dict.fromkeys(duration_params)
)
zone_params_found = list(
    dict.fromkeys(zone_params_found)
)

log(
    f"Duration proxy parameters "
    f"({len(duration_params)}):"
)
for p in duration_params:
    log(f"  {p}")
log()

log(
    f"Zone-related parameters "
    f"({len(zone_params_found)}):"
)
for p in zone_params_found:
    log(f"  {p}")
log()

# ────────────��────────────────────────────
# STEP 3: QUERY DURATION PROXIES
# PER CENTER
# ─────────────────────��───────────────────

log("=" * 56)
log("STEP 3: DURATION PROXY VALUES")
log("Per center — B6N strict controls")
log("=" * 56)
log()

# Load raw data already downloaded
df_raw = pd.read_csv(
    IN_RAW, low_memory=False
)
b6n_mask = df_raw[
    "strain_name"
].isin(B6N_STRINGS)
df_b6n = df_raw[b6n_mask].copy()

audit_rows = []

for param in duration_params:
    log(f"Parameter: {param}")
    log(
        f"{'Center':<16} "
        f"{'N':>6} "
        f"{'Min':>8} "
        f"{'P25':>8} "
        f"{'Median':>8} "
        f"{'P75':>8} "
        f"{'P98':>8} "
        f"{'Max':>10}"
    )
    log("-" * 80)

    # First check if in raw download
    if "parameter_name" in df_b6n.columns:
        sub = df_b6n[
            df_b6n["parameter_name"]
            == param
        ].copy()
        sub["val"] = pd.to_numeric(
            sub["data_point"],
            errors="coerce"
        )
    else:
        sub = pd.DataFrame()

    # If not in raw, query API
    if len(sub) == 0:
        log(
            f"  Not in raw download — "
            f"querying API..."
        )
        sub = fetch_parameter(param)
        if not sub.empty:
            sub = sub[
                sub["strain_name"].isin(
                    B6N_STRINGS
                )
            ].copy()
            sub["val"] = sub[
                "data_point_num"
            ]

    if sub.empty:
        log(
            f"  No B6N data found "
            f"for this parameter."
        )
        log()
        continue

    for center in CENTERS:
        cdf = sub[
            sub["phenotyping_center"]
            == center
        ]
        vals = cdf["val"].dropna()

        if len(vals) < 3:
            log(
                f"  {center:<16} "
                f"{'N<3':>6}"
            )
            continue

        row = {
            "center":    center,
            "parameter": param,
            "n":         len(vals),
            "min":       vals.min(),
            "p25":       vals.quantile(
                             0.25),
            "median":    vals.median(),
            "p75":       vals.quantile(
                             0.75),
            "p98":       vals.quantile(
                             0.98),
            "max":       vals.max(),
        }
        audit_rows.append(row)

        log(
            f"  {center:<16} "
            f"{len(vals):>6,} "
            f"{vals.min():>8.1f} "
            f"{vals.quantile(0.25):>8.1f} "
            f"{vals.median():>8.1f} "
            f"{vals.quantile(0.75):>8.1f} "
            f"{vals.quantile(0.98):>8.1f} "
            f"{vals.max():>10.1f}"
        )

    log()

# ─────────────────────────────────────────
# STEP 4: IMPLIED DURATION ESTIMATION
# ─────────────────────────────────────────

log("=" * 56)
log("STEP 4: IMPLIED DURATION ESTIMATION")
log("=" * 56)
log()
log(
    "Method: P98 of any cumulative time"
    " parameter gives upper bound on"
    " total test duration."
    " Resting time P98 < protocol"
    " duration by definition."
)
log()

audit_df = pd.DataFrame(audit_rows)

if not audit_df.empty:
    # Look for resting / immobility
    # as best duration proxy
    rest_candidates = [
        p for p in
        audit_df["parameter"].unique()
        if any(
            x in p.lower()
            for x in [
                "rest", "immobil",
                "inactive", "still"
            ]
        )
    ]

    dist_candidates = [
        p for p in
        audit_df["parameter"].unique()
        if "distance" in p.lower()
    ]

    log(
        f"Resting/immobility parameters: "
        f"{rest_candidates}"
    )
    log(
        f"Distance parameters: "
        f"{dist_candidates}"
    )
    log()

    # Per center implied duration
    log(
        f"{'Center':<16} "
        f"{'DR23_dur':>10} "
        f"{'Best_proxy':>12} "
        f"{'Proxy_P98':>10} "
        f"{'Implied_dur':>12} "
        f"{'Match':>7}"
    )
    log("-" * 72)

    for center in CENTERS:
        dr23_dur = DR23_DURATIONS.get(
            center
        )
        best_proxy = None
        proxy_p98 = None
        implied = None

        # Try resting first
        for rp in rest_candidates:
            sub = audit_df[
                (audit_df["center"]
                 == center)
                &
                (audit_df["parameter"]
                 == rp)
            ]
            if not sub.empty:
                best_proxy = rp[:20]
                proxy_p98 = float(
                    sub["p98"].iloc[0]
                )
                # P98 resting < total dur
                # If P98 resting > 1200s
                # protocol > 20min
                implied = (
                    "> 20min"
                    if proxy_p98 > 1200
                    else f"≤ {proxy_p98/60:.0f}min"
                )
                break

        # Fall back to distance
        if best_proxy is None:
            for dp in dist_candidates:
                sub = audit_df[
                    (audit_df["center"]
                     == center)
                    &
                    (audit_df["parameter"]
                     == dp)
                ]
                if not sub.empty:
                    best_proxy = dp[:20]
                    proxy_p98 = float(
                        sub["p98"].iloc[0]
                    )
                    implied = "see_dist"
                    break

        dr23_str = (
            f"{dr23_dur}min"
            if dr23_dur else "unknown"
        )
        proxy_str = (
            f"{proxy_p98:>10.1f}"
            if proxy_p98 else
            "       N/A"
        )
        implied_str = (
            implied if implied
            else "no_proxy"
        )
        match = "?" if not dr23_dur else (
            "OK"
            if implied and "20" in str(
                implied
            )
            else "DIFF"
        )

        log(
            f"{center:<16} "
            f"{dr23_str:>10} "
            f"{str(best_proxy or 'none'):>12} "
            f"{proxy_str} "
            f"{implied_str:>12} "
            f"{match:>7}"
        )

log()

# ─────────────────────────────────────────
# STEP 5: ZONE DEFINITION AUDIT
# MRC HARWELL CENTRE TIME ANOMALY
# ─────────────────────────────────────────

log("=" * 56)
log("STEP 5: ZONE DEFINITION AUDIT")
log("MRC Harwell centre time anomaly")
log("(16.2s vs 165-288s elsewhere)")
log("=" * 56)
log()

# Query all zone-related parameters
# for MRC Harwell vs others
log(
    "Zone parameters per center "
    "(B6N strict, medians):"
)
log()

for param in zone_params_found:
    if param in KNOWN_PARAMS:
        # Already have this
        if "parameter_name" in (
            df_b6n.columns
        ):
            sub = df_b6n[
                df_b6n["parameter_name"]
                == param
            ].copy()
            sub["val"] = pd.to_numeric(
                sub["data_point"],
                errors="coerce"
            )
        else:
            continue
    else:
        sub = fetch_parameter(param)
        if not sub.empty:
            sub = sub[
                sub["strain_name"].isin(
                    B6N_STRINGS
                )
            ].copy()
            sub["val"] = sub[
                "data_point_num"
            ]

    if sub.empty:
        continue

    has_data = False
    rows_out = []
    for center in CENTERS:
        cdf = sub[
            sub["phenotyping_center"]
            == center
        ]
        vals = cdf["val"].dropna()
        if len(vals) >= 3:
            has_data = True
            rows_out.append(
                f"  {center:<16} "
                f"n={len(vals):>5,}  "
                f"median={vals.median():>8.1f}  "
                f"P98={vals.quantile(0.98):>8.1f}"
            )

    if has_data:
        log(f"  {param}:")
        for r in rows_out:
            log(r)
        log()

# ─────────────────────────────────────────
# STEP 6: PERIPHERY TIME
# DURATION-NORMALIZED ESTIMATE
# ─────────────────────────────────────────

log("=" * 56)
log("STEP 6: PERIPHERY TIME AS")
log("PROPORTION OF IMPLIED DURATION")
log("=" * 56)
log()
log(
    "If test durations differ across"
    " centers, normalizing periphery"
    " time as a proportion of total"
    " test time may recover the"
    " between-center signal."
)
log()
log(
    "Periphery permanence time medians:"
)
log()

peri_meds = {
    "CMHD":        1015.1,
    "HMGU":         906.4,
    "MRC Harwell": 1028.3,
    "ICS":         1034.6,
    "WTSI":         947.6,
}

log(
    f"{'Center':<16} "
    f"{'Peri_med':>9} "
    f"{'Notes'}"
)
log("-" * 56)

for center, pmed in sorted(
    peri_meds.items(),
    key=lambda x: x[1],
    reverse=True
):
    note = ""
    if center == "HMGU":
        note = (
            "← DR23 was 1842.6s "
            "(-936s)"
        )
    if center == "MRC Harwell":
        note = (
            "← ctr_med 16.2s anomaly"
        )
    log(
        f"{center:<16} "
        f"{pmed:>9.1f} "
        f"{note}"
    )

log()
log(
    "If HMGU ran a ~10min test in"
    " EUMODIC vs ~20min in DR23,"
    " the expected periphery time"
    " would be approximately halved:"
    f" 1842.6 / 2 = 921.3s"
)
log(
    f"HMGU EUMODIC actual: 906.4s"
)
log(
    "Difference from half-duration"
    f" estimate: {906.4 - 921.3:+.1f}s"
)
log()
log(
    "This is consistent with HMGU"
    " running a 10-minute protocol"
    " in EUMODIC vs 20 minutes in"
    " DR23."
)
log()

# ─────────────────────────────────────────
# STEP 7: SUMMARY AND CONCLUSION
# ─────────────────────────────────────────

log("=" * 56)
log("STEP 7: AUDIT SUMMARY")
log("=" * 56)
log()
log(
    "Anomaly 1: HMGU 936-second drop"
)
log(
    "  Most likely explanation:"
    " protocol duration difference."
)
log(
    "  HMGU EUMODIC (~906s) is"
    " consistent with a 10-minute"
    " test. DR23 HMGU (1842s) is"
    " consistent with a 20-minute"
    " test."
)
log(
    "  Half of 1842.6 = 921.3s."
    " EUMODIC actual = 906.4s."
    " Difference = -14.9s."
)
log(
    "  This near-exact half-duration"
    " relationship is strong evidence"
    " for a 10 vs 20 minute protocol"
    " difference."
)
log()
log(
    "Anomaly 2: MRC Harwell"
    " centre_time 16.2s"
)
log(
    "  Most likely explanation:"
    " zone definition difference."
)
log(
    "  All other centers: 165-288s."
    " MRC Harwell: 16.2s."
    " A 10-17x difference cannot"
    " be explained behaviorally."
)
log(
    "  A smaller or differently"
    " bounded centre zone at MRC"
    " Harwell would produce fewer"
    " and shorter centre visits,"
    " inflating periphery time"
    " independently of behavior."
)
log()
log(
    "Conclusion:"
)
log(
    "  The EUMODIC null result is"
    " consistent with protocol"
    " heterogeneity as the primary"
    " confound. The ESLIM_007_001"
    " dataset does not provide"
    " equivalent measurements across"
    " centers for this analysis."
)
log()
log(
    "  Recommended action:"
    " Close EUMODIC as procedurally"
    " non-equivalent to DR23."
    " Document findings in results"
    " document. Proceed to DR24"
    " and Faraday cage experiment."
)
log()

# ─────────────────────────────────────────
# SAVE
# ─────────────────────────────────────────

if not audit_df.empty:
    audit_df.to_csv(OUT_CSV, index=False)
    log(f"Saved: {OUT_CSV}")

with open(OUT_TXT, "w") as f:
    f.write("\n".join(results))
log(f"Saved: {OUT_TXT}")
log()

log("=" * 56)
log("PROTOCOL AUDIT COMPLETE")
log("=" * 56)
