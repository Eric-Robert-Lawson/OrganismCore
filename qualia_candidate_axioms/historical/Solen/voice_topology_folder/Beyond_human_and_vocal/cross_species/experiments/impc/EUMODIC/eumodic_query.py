"""
EUMODIC Open Field Query
========================
Acquires raw ESLIM_007_001 data from the
IMPC SOLR API for:
  - Centre permanence time
  - Periphery permanence time
  - Wildtype controls
  - All centers

Outputs:
  - eumodic_raw.csv        : full record set
  - eumodic_centers.txt    : center inventory
    with record counts

Run BEFORE eumodic_strain_audit.py.
Do NOT examine behavioral value
distributions before strain audit
is complete.

OrganismCore — IMPC Series
EUMODIC Replication Analysis
February 2026
"""

import requests
import pandas as pd
import time
import os

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────

SOLR_BASE = (
    "https://www.ebi.ac.uk"
    "/mi/impc/solr/experiment/select"
)

PROCEDURE_ID = "ESLIM_007_001"

PARAM_NAMES = [
    "Centre permanence time",
    "Periphery permanence time",
]

SAMPLE_GROUP = "control"

ROWS_PER_PAGE = 5000
MAX_RECORDS   = 500000  # safety cap

OUT_RAW     = "eumodic_raw.csv"
OUT_CENTERS = "eumodic_centers.txt"

FIELDS = ",".join([
    "phenotyping_center",
    "procedure_stable_id",
    "parameter_stable_id",
    "parameter_name",
    "data_point",
    "biological_sample_group",
    "strain_name",
    "strain_accession_id",
    "zygosity",
    "sex",
    "date_of_experiment",
    "external_sample_id",
    "pipeline_stable_id",
    "colony_id",
    "metadata_group",
])

# ─────────────────────────────────────────
# LOGGING
# ─────────────────────────────────────────

results = []

def log(s=""):
    results.append(s)
    print(s)

# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────

def solr_get(params, max_rows=50000):
    """
    Single SOLR request. Returns
    response dict or raises on failure.
    """
    r = requests.get(
        SOLR_BASE,
        params=params,
        timeout=60
    )
    r.raise_for_status()
    return r.json()

def build_param_filter():
    """
    Builds SOLR OR filter for
    parameter names.
    """
    clauses = " OR ".join([
        f'parameter_name:"{p}"'
        for p in PARAM_NAMES
    ])
    return clauses

# ─────────────────────────────────────────
# STEP 1: COUNT TOTAL RECORDS
# ─────────────────────────────────────────

log("=" * 52)
log("EUMODIC OPEN FIELD QUERY")
log("ESLIM_007_001 — All centers")
log("=" * 52)
log()

param_filter = build_param_filter()

count_params = {
    "q": (
        f"procedure_stable_id:{PROCEDURE_ID}"
        f" AND ({param_filter})"
        f" AND biological_sample_group:"
        f"{SAMPLE_GROUP}"
    ),
    "rows": 0,
    "wt":   "json",
}

log("Querying total record count...")
count_resp = solr_get(count_params)
total = count_resp["response"]["numFound"]
log(f"Total records found: {total:,}")
log()

if total == 0:
    log("ERROR: No records returned.")
    log("Check procedure ID and parameter")
    log("names against SOLR directly.")
    log()
    log("Verification URL:")
    log(
        "https://www.ebi.ac.uk/mi/impc/solr"
        "/experiment/select?"
        "q=procedure_stable_id:ESLIM_007_001"
        "%20AND%20(parameter_name:%22Centre"
        "%20permanence%20time%22%20OR%20"
        "parameter_name:%22Periphery%20"
        "permanence%20time%22)%20AND%20"
        "biological_sample_group:control"
        "&rows=1"
    )
    exit(1)

# ─────────────────────────────────────────
# STEP 2: PAGINATED DOWNLOAD
# ─────────────────────────────────────────

log(f"Downloading in pages of "
    f"{ROWS_PER_PAGE:,}...")
log()

all_records  = []
failed_pages = []
n_pages      = (
    min(total, MAX_RECORDS)
    // ROWS_PER_PAGE
) + 1

for page in range(n_pages):
    offset = page * ROWS_PER_PAGE
    if offset >= min(total, MAX_RECORDS):
        break

    page_params = {
        "q": count_params["q"],
        "rows":  ROWS_PER_PAGE,
        "start": offset,
        "fl":    FIELDS,
        "wt":    "json",
    }

    try:
        resp = solr_get(page_params)
        docs = resp["response"]["docs"]
        all_records.extend(docs)
        log(
            f"  Page {page+1:>3} | "
            f"offset {offset:>7,} | "
            f"records this page: "
            f"{len(docs):>5,} | "
            f"total so far: "
            f"{len(all_records):>7,}"
        )
        time.sleep(0.25)

    except Exception as e:
        log(
            f"  Page {page+1} FAILED: {e}"
        )
        failed_pages.append(page)
        time.sleep(1.0)

log()
log(f"Download complete.")
log(f"  Total records: {len(all_records):,}")
log(f"  Failed pages:  {len(failed_pages)}")
if failed_pages:
    log(
        f"  Failed page numbers: "
        f"{failed_pages}"
    )
log()

# ─────────────────────────────────────────
# STEP 3: BUILD DATAFRAME
# ─────────────────────────────────────────

df = pd.DataFrame(all_records)

log(f"DataFrame shape: {df.shape}")
log(f"Columns present: "
    f"{list(df.columns)}")
log()

# Numeric conversion
if "data_point" in df.columns:
    df["data_point_num"] = pd.to_numeric(
        df["data_point"], errors="coerce"
    )
    n_numeric = df[
        "data_point_num"
    ].notna().sum()
    log(
        f"Numeric data_point values: "
        f"{n_numeric:,} / {len(df):,}"
    )
else:
    log("WARNING: data_point column "
        "not found.")
log()

# ─────────────────────────────────────────
# STEP 4: CENTER INVENTORY
# ─────────────────────────────────────────

log("=" * 52)
log("CENTER INVENTORY")
log("=" * 52)
log()

if "phenotyping_center" in df.columns:
    center_counts = (
        df.groupby("phenotyping_center")
        .size()
        .sort_values(ascending=False)
    )
    log(
        f"{'Center':<30} "
        f"{'N records':>10}"
    )
    log("-" * 42)
    for center, n in center_counts.items():
        log(f"{center:<30} {n:>10,}")
    log()
    log(
        f"Total centers: "
        f"{len(center_counts)}"
    )
else:
    log("WARNING: phenotyping_center "
        "column not found.")

log()

# ─────────────────────────────────────────
# STEP 5: PARAMETER INVENTORY
# ─────────────────────────────────────────

log("=" * 52)
log("PARAMETER INVENTORY")
log("=" * 52)
log()

if "parameter_name" in df.columns:
    param_counts = (
        df.groupby("parameter_name")
        .size()
        .sort_values(ascending=False)
    )
    for pname, n in param_counts.items():
        log(f"  {pname}: {n:,}")
else:
    log("WARNING: parameter_name "
        "column not found.")

log()

# ─────────────────────────────────────────
# STEP 6: STRAIN INVENTORY
# (Do NOT examine behavioral values yet)
# ─────────────────────────────────────────

log("=" * 52)
log("STRAIN INVENTORY")
log("(For strain audit — behavioral")
log(" values NOT examined here)")
log("=" * 52)
log()

strain_col = None
for candidate in [
    "strain_name",
    "strain_accession_id"
]:
    if candidate in df.columns:
        strain_col = candidate
        break

if strain_col:
    strain_counts = (
        df.groupby(strain_col)
        .size()
        .sort_values(ascending=False)
    )
    log(
        f"{'Strain':<40} "
        f"{'N records':>10}"
    )
    log("-" * 52)
    for strain, n in strain_counts.items():
        log(
            f"{str(strain):<40} "
            f"{n:>10,}"
        )
    log()
    log(
        f"Total distinct strains: "
        f"{len(strain_counts)}"
    )
else:
    log("WARNING: strain column not found.")

log()

# ─────────────────────────────────────��───
# STEP 7: SAVE OUTPUTS
# ─────────────────────────────────────────

df.to_csv(OUT_RAW, index=False)
log(f"Raw data saved: {OUT_RAW}")
log(f"  Rows: {len(df):,}")
log(f"  Columns: {len(df.columns)}")
log()

with open(OUT_CENTERS, "w") as f:
    f.write("\n".join(results))
log(f"Center inventory saved: "
    f"{OUT_CENTERS}")
log()

# ─────────────────────────────────────────
# STEP 8: NEXT STEP REMINDER
# ─────────────────────────────────────────

log("=" * 52)
log("NEXT STEP")
log("=" * 52)
log()
log("Run eumodic_strain_audit.py")
log("BEFORE examining any behavioral")
log("value distributions.")
log()
log("The strain decision (C57BL/6N")
log("strict vs. aggregated C57BL/6)")
log("must be finalized before medians")
log("are computed — per pre-registration")
log("record in EUMODIC_README.md.")
log()
log("=" * 52)
