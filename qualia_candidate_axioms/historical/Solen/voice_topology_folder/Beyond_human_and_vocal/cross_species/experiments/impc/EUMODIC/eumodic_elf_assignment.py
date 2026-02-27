"""
EUMODIC ELF Score Assignment
=============================
Assigns ELF scores to all EUMODIC
centers BEFORE behavioral medians
are computed.

ELF scores are based on facility
metadata: location, grid frequency,
building era, HV proximity, and
known shielding documentation.

For centers present in DR23, the
same ELF score is used — ELF is a
property of the facility, not the
data collection period.

WTSI: not present in DR23. Score
assigned blind from facility metadata.

CMHD: EUMODIC-only center. Score
assigned blind from facility metadata.

Reads:  eumodic_strain_decision.csv
Writes: eumodic_elf_scores.csv
        eumodic_elf_assignment.txt

Run AFTER eumodic_strain_audit.py.
Run BEFORE eumodic_correlation.py.

OrganismCore — IMPC Series
EUMODIC Replication Analysis
February 2026
"""

import pandas as pd

# ─────────────────────────────────────────
# ELF SCORE TABLE
# Assigned before behavioral values
# are examined.
#
# Score range: 0 (minimal ELF) to
# 100 (maximal ELF exposure)
#
# Method: composite of
#   - Grid frequency (50 Hz vs 60 Hz)
#     60 Hz baseline slightly higher
#     harmonic density in building wiring
#   - Building era (older = higher)
#   - Urban vs rural location
#   - HV proximity (urban campus = higher)
#   - Purpose-built shielding (reduces)
#   - Hospital/heavy industry adjacency
#
# DR23 scores carried forward unchanged
# where center was present in DR23.
# WTSI and CMHD assigned from metadata
# only — blind to behavioral values.
# ─────────────────────────────────────────

ELF_META = {

    "CMHD": {
        "full_name": (
            "Centre for Modeling Human "
            "Disease — Mount Sinai Hospital"
        ),
        "location": "Toronto, Canada",
        "grid_hz": 60,
        "building_era": "academic_hospital",
        "urban_rural": "urban",
        "hv_proximity": "high",
        "shielding": "not_documented",
        "source": "new_assignment_blind",
        "dr23_score": None,
        "elf_score": 72,
        "notes": (
            "Hospital-adjacent urban "
            "academic facility. 60 Hz grid. "
            "High surrounding electrical "
            "infrastructure density from "
            "hospital complex and urban "
            "Toronto environment. No "
            "shielding documentation found. "
            "Assigned blind to behavioral "
            "values per pre-registration."
        ),
    },

    "HMGU": {
        "full_name": (
            "Helmholtz Zentrum München"
        ),
        "location": "Munich, Germany",
        "grid_hz": 50,
        "building_era": "mixed",
        "urban_rural": "suburban_campus",
        "hv_proximity": "moderate",
        "shielding": "not_documented",
        "source": "DR23_carried_forward",
        "dr23_score": 65,
        "elf_score": 65,
        "notes": (
            "Large research campus, mixed "
            "building ages, moderate HV "
            "from campus infrastructure. "
            "Score carried from DR23."
        ),
    },

    "MRC Harwell": {
        "full_name": (
            "MRC Harwell Institute"
        ),
        "location": "Oxfordshire, UK",
        "grid_hz": 50,
        "building_era": "mixed",
        "urban_rural": "rural_campus",
        "hv_proximity": "low_moderate",
        "shielding": "not_documented",
        "source": "DR23_carried_forward",
        "dr23_score": 59,
        "elf_score": 59,
        "notes": (
            "Historic rural campus with "
            "modern additions. Lower HV "
            "density than urban centers. "
            "Score carried from DR23."
        ),
    },

    "ICS": {
        "full_name": (
            "Institut Clinique de la Souris"
        ),
        "location": "Strasbourg, France",
        "grid_hz": 50,
        "building_era": "modern",
        "urban_rural": "campus",
        "hv_proximity": "low",
        "shielding": "partial_modern_standard",
        "source": "DR23_carried_forward",
        "dr23_score": 36,
        "elf_score": 36,
        "notes": (
            "Purpose-built modern facility "
            "est. early 2000s. Lower ambient "
            "ELF than older campuses. "
            "Score carried from DR23."
        ),
    },

    "WTSI": {
        "full_name": (
            "Wellcome Sanger Institute"
        ),
        "location": "Hinxton, Cambridge, UK",
        "grid_hz": 50,
        "building_era": "modern",
        "urban_rural": "rural_campus",
        "hv_proximity": "low",
        "shielding": "purpose_built_likely",
        "source": "new_assignment_blind",
        "dr23_score": None,
        "elf_score": 28,
        "notes": (
            "Purpose-built rural genomics "
            "campus. Not present in DR23 "
            "dataset. ELF score 28 assigned "
            "blind from facility metadata: "
            "rural location, modern build, "
            "low HV proximity, likely "
            "purpose-built shielding. "
            "New assignment — not carried "
            "forward from DR23."
        ),
    },
}

# ─────────────────────────────────────────
# PREDICTED RANK ORDER
# Stated before behavioral values
# are examined — pre-registration anchor.
#
# Higher ELF → higher predicted
# thigmotaxis (periphery permanence time)
# per coherence hypothesis.
# ─────────────────────────────────────────

PREDICTED_RANK = [
    # (center, predicted_thigmo_rank)
    # 1 = highest thigmotaxis
    ("CMHD",        1),
    ("HMGU",        2),
    ("MRC Harwell", 3),
    ("ICS",         4),
    ("WTSI",        5),
]

# ─────────────────────────────────────────
# LOGGING
# ─────────────────────────────────────────

results = []

def log(s=""):
    results.append(s)
    print(s)

# ─────────────────────────────────────────
# BUILD OUTPUT TABLE
# ─────────────────────────────────────────

log("=" * 56)
log("EUMODIC ELF SCORE ASSIGNMENT")
log("=" * 56)
log()
log("Scores assigned BEFORE behavioral")
log("medians are computed.")
log()
log("DR23 scores carried forward for:")
log("  HMGU, ICS, MRC Harwell")
log()
log("New blind assignments for:")
log("  WTSI (not in DR23)")
log("  CMHD (EUMODIC-only center)")
log()

rows = []
for center, meta in ELF_META.items():
    rows.append({
        "center":       center,
        "full_name":    meta["full_name"],
        "location":     meta["location"],
        "grid_hz":      meta["grid_hz"],
        "building_era": meta["building_era"],
        "urban_rural":  meta["urban_rural"],
        "hv_proximity": meta["hv_proximity"],
        "shielding":    meta["shielding"],
        "elf_score":    meta["elf_score"],
        "dr23_score":   meta["dr23_score"],
        "source":       meta["source"],
        "notes":        meta["notes"],
    })

elf_df = pd.DataFrame(rows)
elf_df = elf_df.sort_values(
    "elf_score", ascending=False
).reset_index(drop=True)

# ─────────────────────��───────────────────
# PRINT ASSIGNMENT TABLE
# ─────────────────────────────────────────

log(
    f"{'Center':<14} "
    f"{'ELF':>5} "
    f"{'DR23':>6} "
    f"{'Hz':>4} "
    f"{'Source':<26}"
)
log("-" * 60)

for _, row in elf_df.iterrows():
    dr23 = (
        f"{int(row['dr23_score']):>6}"
        if pd.notna(row["dr23_score"])
        else "   NEW"
    )
    log(
        f"{row['center']:<14} "
        f"{row['elf_score']:>5.0f} "
        f"{dr23} "
        f"{row['grid_hz']:>4} "
        f"{row['source']:<26}"
    )

log()

# ─────────────────────────────────────────
# NOTES PER CENTER
# ─────────────────────────────────────────

log("=" * 56)
log("ASSIGNMENT NOTES")
log("=" * 56)
log()

for _, row in elf_df.iterrows():
    log(f"{row['center']}:")
    log(f"  {row['notes']}")
    log()

# ─────────────────────────────────────────
# PREDICTED RANK ORDER
# ─────────────────────────────────────────

log("=" * 56)
log("PREDICTED THIGMOTAXIS RANK ORDER")
log("(high to low — stated pre-analysis)")
log("=" * 56)
log()
log("Prediction: higher ELF score ->")
log("higher periphery permanence time")
log("per EM coherence hypothesis.")
log()

pred_df = pd.DataFrame(
    PREDICTED_RANK,
    columns=["center", "predicted_rank"]
)
pred_df = pred_df.merge(
    elf_df[["center", "elf_score"]],
    on="center"
)
pred_df = pred_df.sort_values(
    "predicted_rank"
)

log(
    f"{'Rank':<6} "
    f"{'Center':<14} "
    f"{'ELF Score':>10}"
)
log("-" * 34)
for _, row in pred_df.iterrows():
    log(
        f"{int(row['predicted_rank']):<6} "
        f"{row['center']:<14} "
        f"{row['elf_score']:>10.0f}"
    )

log()
log(
    "This rank order is the"
)
log(
    "pre-registration anchor."
)
log(
    "It will be compared against"
)
log(
    "observed thigmotaxis ranks"
)
log(
    "in eumodic_correlation.py."
)
log()

# ─────────────────────────────────────────
# CROSS-CHECK: DECISION FILE
# ─────────────────────────────────────────

log("=" * 56)
log("CROSS-CHECK: STRAIN DECISION FILE")
log("=" * 56)
log()

try:
    dec_df = pd.read_csv(
        "eumodic_strain_decision.csv"
    )
    dec_centers = set(
        dec_df["center"].tolist()
    )
    elf_centers = set(ELF_META.keys())

    missing_elf = dec_centers - elf_centers
    missing_dec = elf_centers - dec_centers

    if missing_elf:
        log(
            "WARNING: Centers in strain "
            "decision without ELF score:"
        )
        for c in sorted(missing_elf):
            log(f"  {c}")
        log()

    if missing_dec:
        log(
            "WARNING: Centers with ELF "
            "score not in strain decision:"
        )
        for c in sorted(missing_dec):
            log(f"  {c}")
        log()

    if (
        not missing_elf
        and not missing_dec
    ):
        log(
            "Cross-check passed: all "
            "centers have both strain "
            "rule and ELF score."
        )
        log()

except FileNotFoundError:
    log(
        "WARNING: eumodic_strain_"
        "decision.csv not found."
    )
    log(
        "Run eumodic_strain_audit.py "
        "first."
    )
    log()

# ─────────────────────────────────────────
# SAVE
# ─────────────────────────────────────────

elf_df.to_csv(
    "eumodic_elf_scores.csv",
    index=False
)
log("Saved: eumodic_elf_scores.csv")

with open(
    "eumodic_elf_assignment.txt", "w"
) as f:
    f.write("\n".join(results))
log("Saved: eumodic_elf_assignment.txt")
log()

# ─────────────────────────────────────────
# NEXT STEP
# ─────────────────────────────────────────

log("=" * 56)
log("NEXT STEP")
log("=" * 56)
log()
log("Run eumodic_correlation.py")
log()
log("That script will compute center-")
log("level median periphery permanence")
log("time and run the Spearman")
log("correlation against ELF scores.")
log()
log("The predicted rank order above")
log("will be tested against observed")
log("behavioral ranks.")
log()
log("=" * 56)
