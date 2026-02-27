"""
EUMODIC Strain Audit
====================
Determines strain rule per center
BEFORE behavioral values are examined.

Reads: eumodic_raw.csv
Outputs:
  - eumodic_strain_decision.csv
  - eumodic_strain_audit.txt

Decision rule (per EUMODIC_README.md
pre-registration):
  PRIMARY:   C57BL/6N strict
  SECONDARY: All C57BL/6 aggregated
             (only if C57BL/6N N < 8
              for any center)

Run AFTER eumodic_query.py.
Run BEFORE eumodic_elf_assignment.py.

OrganismCore — IMPC Series
EUMODIC Replication Analysis
February 2026
"""

import pandas as pd

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────

IN_CSV          = "eumodic_raw.csv"
OUT_DECISION    = "eumodic_strain_decision.csv"
OUT_AUDIT       = "eumodic_strain_audit.txt"

# Minimum N per center for
# C57BL/6N strict to be viable
MIN_N_STRICT    = 8

# C57BL/6N identifier strings
# (check against strain inventory
#  output from eumodic_query.py
#  and add variants if needed)
B6N_STRINGS = [
    "C57BL/6N",
    "C57BL/6NJ",
    "C57BL/6NCrl",
    "C57BL/6NTac",
    "C57BL/6N Tac",
    "C57BL/6N Crl",
]

# All C57BL/6 substrains
# (aggregated secondary analysis)
B6_ALL_STRINGS = [
    "C57BL/6N",
    "C57BL/6NJ",
    "C57BL/6NCrl",
    "C57BL/6NTac",
    "C57BL/6N Tac",
    "C57BL/6N Crl",
    "C57BL/6J",
    "C57BL/6",
    "C57BL/6JOlaHsd",
    "C57BL/6JCrl",
]

# Wildtype zygosity strings
WT_STRINGS = [
    "wild type",
    "wildtype",
    "wild-type",
    "wt",
    "WT",
    "control",
]

results = []

def log(s=""):
    results.append(s)
    print(s)

# ─────────────────────────────────────────
# LOAD
# ─────────────────────────────────────────

log("=" * 52)
log("EUMODIC STRAIN AUDIT")
log("=" * 52)
log()

df = pd.read_csv(IN_CSV, low_memory=False)
log(f"Loaded: {IN_CSV}")
log(f"  Rows:    {len(df):,}")
log(f"  Columns: {len(df.columns)}")
log()

# ─────────────────────────────────────────
# IDENTIFY STRAIN COLUMN
# ─────────────────────────────────────────

strain_col = None
for candidate in [
    "strain_name",
    "strain_accession_id",
]:
    if candidate in df.columns:
        strain_col = candidate
        break

if not strain_col:
    log("ERROR: No strain column found.")
    log("Columns present:")
    for c in df.columns:
        log(f"  {c}")
    exit(1)

log(f"Strain column: {strain_col}")
log()

# ─────────────────────────────────────────
# IDENTIFY ZYGOSITY COLUMN
# ─────────────────────────────────────────

zyg_col = None
for candidate in [
    "zygosity",
    "biological_sample_group",
]:
    if candidate in df.columns:
        zyg_col = candidate
        break

log(f"Zygosity/group column: {zyg_col}")
log()

# ─────────────────────────────────────────
# FILTER: WILDTYPE CONTROLS
# ─────────────────────────────────────────

if zyg_col:
    wt_mask = df[zyg_col].str.lower().isin(
        [w.lower() for w in WT_STRINGS]
    )
    df_wt = df[wt_mask].copy()
else:
    log("WARNING: No zygosity column. "
        "Using all records.")
    df_wt = df.copy()

log(
    f"Wildtype / control records: "
    f"{len(df_wt):,} / {len(df):,}"
)
log()

# ─────────────────────────────────────────
# BUILD STRAIN FLAGS
# ─────────────────────────────────────────

df_wt["is_b6n"] = df_wt[
    strain_col
].str.strip().isin(B6N_STRINGS)

df_wt["is_b6_all"] = df_wt[
    strain_col
].str.strip().isin(B6_ALL_STRINGS)

# ─────────────���───────────────────────────
# PER-CENTER AUDIT
# ─────────────────────────────────────────

log("=" * 52)
log("PER-CENTER STRAIN COUNTS")
log("=" * 52)
log()

centers = sorted(
    df_wt["phenotyping_center"]
    .dropna().unique().tolist()
)

decision_rows = []

log(
    f"{'Center':<28} "
    f"{'N B6N':>7} "
    f"{'N B6all':>8} "
    f"{'N total':>8} "
    f"{'Rule':>12}"
)
log("-" * 68)

for center in centers:
    cdf = df_wt[
        df_wt["phenotyping_center"]
        == center
    ]

    n_b6n   = cdf["is_b6n"].sum()
    n_b6all = cdf["is_b6_all"].sum()
    n_total = len(cdf)

    if n_b6n >= MIN_N_STRICT:
        rule = "STRICT_B6N"
    elif n_b6all >= MIN_N_STRICT:
        rule = "AGG_B6ALL"
    else:
        rule = "INSUFFICIENT"

    log(
        f"{center:<28} "
        f"{n_b6n:>7,} "
        f"{n_b6all:>8,} "
        f"{n_total:>8,} "
        f"{rule:>12}"
    )

    decision_rows.append({
        "center":        center,
        "n_b6n_wt":      int(n_b6n),
        "n_b6all_wt":    int(n_b6all),
        "n_total_wt":    int(n_total),
        "strain_rule":   rule,
        "min_n_threshold": MIN_N_STRICT,
    })

log()

# ─────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────

decision_df = pd.DataFrame(decision_rows)

n_strict = (
    decision_df["strain_rule"]
    == "STRICT_B6N"
).sum()
n_agg = (
    decision_df["strain_rule"]
    == "AGG_B6ALL"
).sum()
n_insuf = (
    decision_df["strain_rule"]
    == "INSUFFICIENT"
).sum()

log("=" * 52)
log("STRAIN DECISION SUMMARY")
log("=" * 52)
log()
log(
    f"Centers using STRICT_B6N:    "
    f"{n_strict}"
)
log(
    f"Centers using AGG_B6ALL:     "
    f"{n_agg}"
)
log(
    f"Centers INSUFFICIENT (both): "
    f"{n_insuf}"
)
log()

if n_agg > 0:
    log("NOTE: AGG_B6ALL centers will be")
    log("reported separately in primary")
    log("analysis with strain rule flagged.")
    log()

if n_insuf > 0:
    log("NOTE: INSUFFICIENT centers will")
    log("be excluded from correlation.")
    log("Listed below:")
    insuf = decision_df[
        decision_df["strain_rule"]
        == "INSUFFICIENT"
    ]["center"].tolist()
    for c in insuf:
        log(f"  {c}")
    log()

# ─────────────────────────────────────────
# OVERLAPPING CENTERS CHECK
# ─────────────────────────────────────────

# Centers present in DR23 analysis
DR23_CENTERS = [
    "CCP",
    "HMGU",
    "ICS",
    "IMG",
    "MRC Harwell",
    "TCP",
    "WTSI",
]

log("=" * 52)
log("OVERLAP WITH DR23 CENTERS")
log("=" * 52)
log()

eumodic_centers = set(
    decision_df["center"].tolist()
)
dr23_set = set(DR23_CENTERS)

overlap = eumodic_centers & dr23_set
new_centers = eumodic_centers - dr23_set
dr23_missing = dr23_set - eumodic_centers

log(
    f"Centers in both DR23 and EUMODIC: "
    f"{len(overlap)}"
)
for c in sorted(overlap):
    log(f"  {c}")
log()

log(
    f"New centers (EUMODIC only): "
    f"{len(new_centers)}"
)
for c in sorted(new_centers):
    log(f"  {c}")
log()

log(
    f"DR23 centers absent from EUMODIC: "
    f"{len(dr23_missing)}"
)
for c in sorted(dr23_missing):
    log(f"  {c}")
log()

# ─────────────────────────────────────────
# SAVE
# ─────────────────────────────────────────

decision_df.to_csv(
    OUT_DECISION, index=False
)
log(f"Strain decision saved: "
    f"{OUT_DECISION}")
log()

with open(OUT_AUDIT, "w") as f:
    f.write("\n".join(results))
log(f"Audit log saved: {OUT_AUDIT}")
log()

# ─────────────────────────────────────────
# NEXT STEP REMINDER
# ─────────────────────────────────────────

log("=" * 52)
log("NEXT STEP")
log("=" * 52)
log()
log("Run eumodic_elf_assignment.py")
log()
log("ELF scores must be assigned to")
log("all centers BEFORE behavioral")
log("medians are computed.")
log()
log("For overlapping centers use the")
log("same ELF score as DR23.")
log("For new centers assign blind to")
log("behavioral values.")
log()
log("=" * 52)
