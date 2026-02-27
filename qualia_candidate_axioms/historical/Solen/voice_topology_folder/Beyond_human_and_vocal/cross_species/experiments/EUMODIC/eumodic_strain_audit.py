"""
EUMODIC Strain Audit — v2
==========================
Corrected for EUMODIC data structure:
  - All records are controls
    (biological_sample_group=control,
     zygosity=homozygote)
  - No wildtype string filtering needed
  - All 10,026 records are eligible

Determines strain rule per center
BEFORE behavioral values are examined.

Reads:  eumodic_raw.csv
Writes: eumodic_strain_decision.csv
        eumodic_strain_audit.txt

OrganismCore — IMPC Series
EUMODIC Replication Analysis
February 2026
"""

import pandas as pd

# ─────��───────────────────────────────────
# CONFIG
# ───────────────────────────────────���─────

IN_CSV       = "eumodic_raw.csv"
OUT_DECISION = "eumodic_strain_decision.csv"
OUT_AUDIT    = "eumodic_strain_audit.txt"

MIN_N_STRICT = 8

# C57BL/6N substrains — strict
B6N_STRINGS = [
    "C57BL/6N",
    "C57BL/6NTac",
    "C57BL/6NTacDen",
    "C57BL/6NTac-ICS-Denmark(ImportedLive)",
    "C57BL/6NTac-ICS-USA(ImportedLive)",
    "C57BL/6NCrl",
    "C57BL/6NJ",
]

# All C57BL/6 substrains — aggregated
B6_ALL_STRINGS = B6N_STRINGS + [
    "C57BL/6",
    "C57BL/6J",
    "C57BL/6JIco",
    "C57BL/6Dnk",
    "C57BL/6JTyr;C57BL/6N",
    "C57BL/6JTyr;C57BL/6JIco",
    "C57BL/6JTyr;C57BL/6",
    "C57BL/6JTyr;C57BL/6;129S5",
    "C57BL/6JIco;129P2",
    "C57BL/6JIco;C57BL/6JTyr;129S5",
    "B6J.129S2",
    "B6J.129S2.B6N",
    "B6J.B6N",
    "B6N.129S2.B6J",
    "B6N.B6J.129S2",
]

# DR23 centers for overlap check
DR23_CENTERS = [
    "CCP",
    "HMGU",
    "ICS",
    "IMG",
    "MRC Harwell",
    "TCP",
    "WTSI",
]

results = []

def log(s=""):
    results.append(s)
    print(s)

# ─────────────────────────────────────────
# LOAD
# ─────────────────────────────────────────

log("=" * 56)
log("EUMODIC STRAIN AUDIT v2")
log("=" * 56)
log()

df = pd.read_csv(IN_CSV, low_memory=False)
log(f"Loaded: {IN_CSV}")
log(f"  Total rows:    {len(df):,}")
log(f"  Columns:       {len(df.columns)}")
log()
log("NOTE: All records are controls")
log("(biological_sample_group=control,")
log(" zygosity=homozygote).")
log("No wildtype string filtering applied.")
log()

# ─────────────────────────────────────────
# STRAIN FLAGS
# ─────────────────────────────────────────

df["is_b6n"] = (
    df["strain_name"]
    .str.strip()
    .isin(B6N_STRINGS)
)

df["is_b6all"] = (
    df["strain_name"]
    .str.strip()
    .isin(B6_ALL_STRINGS)
)

log(
    f"Records flagged B6N strict: "
    f"{df['is_b6n'].sum():,}"
)
log(
    f"Records flagged B6 all:     "
    f"{df['is_b6all'].sum():,}"
)
log()

# ─────────────────────────────────────────
# PER-CENTER AUDIT
# ─────────────────────────────────────────

log("=" * 56)
log("PER-CENTER STRAIN COUNTS")
log("=" * 56)
log()

centers = sorted(
    df["phenotyping_center"]
    .dropna().unique().tolist()
)

log(
    f"{'Center':<30} "
    f"{'N B6N':>7} "
    f"{'N B6all':>8} "
    f"{'N total':>8} "
    f"{'Rule':>14}"
)
log("-" * 72)

decision_rows = []

for center in centers:
    cdf = df[
        df["phenotyping_center"] == center
    ]
    n_b6n   = int(cdf["is_b6n"].sum())
    n_b6all = int(cdf["is_b6all"].sum())
    n_total = len(cdf)

    if n_b6n >= MIN_N_STRICT:
        rule = "STRICT_B6N"
    elif n_b6all >= MIN_N_STRICT:
        rule = "AGG_B6ALL"
    else:
        rule = "INSUFFICIENT"

    log(
        f"{center:<30} "
        f"{n_b6n:>7,} "
        f"{n_b6all:>8,} "
        f"{n_total:>8,} "
        f"{rule:>14}"
    )

    decision_rows.append({
        "center":          center,
        "n_b6n":           n_b6n,
        "n_b6all":         n_b6all,
        "n_total":         n_total,
        "strain_rule":     rule,
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

log("=" * 56)
log("STRAIN DECISION SUMMARY")
log("=" * 56)
log()
log(f"STRICT_B6N centers:    {n_strict}")
log(f"AGG_B6ALL centers:     {n_agg}")
log(f"INSUFFICIENT centers:  {n_insuf}")
log()

if n_insuf > 0:
    insuf = decision_df[
        decision_df["strain_rule"]
        == "INSUFFICIENT"
    ]["center"].tolist()
    log("INSUFFICIENT centers (excluded):")
    for c in insuf:
        log(f"  {c}")
    log()

# ─────────────────────────────────────────
# OVERLAP WITH DR23
# ─────────────────────────────────────────

log("=" * 56)
log("OVERLAP WITH DR23 CENTERS")
log("=" * 56)
log()

eumodic_set = set(centers)
dr23_set    = set(DR23_CENTERS)
overlap     = eumodic_set & dr23_set
new_only    = eumodic_set - dr23_set
missing     = dr23_set - eumodic_set

log(
    f"Centers in BOTH datasets "
    f"({len(overlap)}):"
)
for c in sorted(overlap):
    row = decision_df[
        decision_df["center"] == c
    ].iloc[0]
    log(
        f"  {c:<28} "
        f"B6N={row['n_b6n']:,}  "
        f"rule={row['strain_rule']}"
    )
log()

log(
    f"EUMODIC-only centers "
    f"({len(new_only)}):"
)
for c in sorted(new_only):
    row = decision_df[
        decision_df["center"] == c
    ].iloc[0]
    log(
        f"  {c:<28} "
        f"B6N={row['n_b6n']:,}  "
        f"rule={row['strain_rule']}"
    )
log()

log(
    f"DR23 centers absent from "
    f"EUMODIC ({len(missing)}):"
)
for c in sorted(missing):
    log(f"  {c}")
log()

# ─────────────────────────────────────────
# SAVE
# ─────────────────────────────────────────

decision_df.to_csv(
    OUT_DECISION, index=False
)
log(f"Saved: {OUT_DECISION}")

with open(OUT_AUDIT, "w") as f:
    f.write("\n".join(results))
log(f"Saved: {OUT_AUDIT}")
log()

# ─────────────────────────────────────────
# NEXT STEP
# ─────────────────────────────────────────

log("=" * 56)
log("NEXT STEP")
log("=" * 56)
log()
log("Post the center table output here.")
log("ELF scores will be assigned to all")
log("centers before behavioral medians")
log("are computed.")
log()
log("=" * 56)
