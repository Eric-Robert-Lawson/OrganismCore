"""
STSSN DATA STRUCTURE DIAGNOSTIC
================================
OC-OBS-002 — Sea Turtle Stranding Analysis
OrganismCore — Eric Robert Lawson

PURPOSE:
    Examines the structure of the NOAA STSSN Excel file ONLY.
    Does NOT examine values, distributions, or any content
    relevant to the pre-registered hypotheses.
    Output is safe to share prior to analysis — it contains
    no information that could constitute data snooping.

WHAT THIS SCRIPT REPORTS:
    1. Sheet names and row/column counts per sheet
    2. Column names exactly as they appear in the file
    3. Column data types (dtype only — not values)
    4. Count of nulls per column (structural completeness only)
    5. Whether pre-specified required fields are present
       (by name match and fuzzy match)
    6. Sample of unique values for categorical/code columns
       ONLY for the fields: species, condition, cause_code,
       state — and only up to 20 unique values per field.
       These are classification fields, not measurement values.
       Knowing the coding scheme is required before writing
       the exclusion pipeline — this is not data snooping.

WHAT THIS SCRIPT DOES NOT REPORT:
    - Any numeric values (lat, lon, dates, counts)
    - Any distributions, means, ranges, or statistics
    - Any spatial or temporal patterns
    - Anything that could inform hypothesis direction

USAGE:
    Place this script in the same directory as the Excel file,
    or update DATA_FILE path below.
    Run: python stssn_diagnostics.py
    Paste the full printed output back to Copilot.

REQUIRES:
    pip install pandas openpyxl
"""

import pandas as pd
import sys
from pathlib import Path

# ── CONFIGURATION ────────────────��────────────────────────────

DATA_FILE = "20260320_lawson.xlsx"

# Pre-specified required fields from pre_registration_analysis.md
REQUIRED_FIELDS = [
    "species",
    "strand_date",
    "strand_lat",
    "strand_lon",
    "condition",
    "cause_code",
    "state",
    "county",
]

# Cold-stun field — critical for exclusion criteria
# May appear under various names — checked by fuzzy match
COLD_STUN_CANDIDATES = [
    "cold_stun",
    "coldstun",
    "cold stun",
    "cold_stunning",
    "hypothermic",
    "cold_shock",
]

# Categorical fields where unique value codes are needed
# to write the exclusion pipeline correctly.
# Knowing the coding scheme is structural, not analytical.
CATEGORICAL_FIELDS_FOR_CODES = [
    "species",
    "condition",
    "cause_code",
    "state",
]

# ── UTILITIES ───────────────────────────────────��─────────────

def normalise(name: str) -> str:
    """Lowercase, strip, replace spaces/hyphens with underscore."""
    return str(name).lower().strip().replace(" ", "_").replace("-", "_")


def fuzzy_match(col_normalised: str, candidates: list) -> bool:
    """Check if any candidate string appears in the column name."""
    return any(c in col_normalised for c in candidates)


def divider(title: str = "") -> None:
    width = 60
    if title:
        pad = (width - len(title) - 2) // 2
        print(f"\n{'─' * pad} {title} {'─' * pad}")
    else:
        print(f"\n{'═' * width}")


# ── MAIN DIAGNOSTIC ───────────────────────────────────────────

def run_diagnostics(filepath: str) -> None:

    path = Path(filepath)

    divider("FILE")
    print(f"File        : {path.name}")
    print(f"Exists      : {path.exists()}")
    if not path.exists():
        print(f"\nERROR: File not found at {path.resolve()}")
        print("Update DATA_FILE path at top of script and retry.")
        sys.exit(1)
    print(f"Size        : {path.stat().st_size / 1024:.1f} KB")

    # ── SHEET INVENTORY ───────────────────────────────────────
    divider("SHEETS")
    xl = pd.ExcelFile(path, engine="openpyxl")
    sheet_names = xl.sheet_names
    print(f"Sheet count : {len(sheet_names)}")
    for i, name in enumerate(sheet_names):
        print(f"  Sheet {i}   : '{name}'")

    # ── PER-SHEET STRUCTURE ───────────────────────────────────
    all_sheets = {}
    for sheet in sheet_names:
        divider(f"SHEET: {sheet}")
        try:
            df = pd.read_excel(path, sheet_name=sheet, engine="openpyxl")
        except Exception as e:
            print(f"  Could not read sheet: {e}")
            continue

        all_sheets[sheet] = df
        nrows, ncols = df.shape
        print(f"  Rows        : {nrows:,}")
        print(f"  Columns     : {ncols}")

        # ── COLUMN INVENTORY ──────────────────────────────────
        print(f"\n  {'#':<5} {'Column name (raw)':<35} {'dtype':<15} {'nulls':>8} {'null%':>7}")
        print(f"  {'─'*5} {'─'*35} {'─'*15} {'─'*8} {'─'*7}")

        col_norm_map = {}  # raw name -> normalised name

        for i, col in enumerate(df.columns):
            dtype = str(df[col].dtype)
            nulls = int(df[col].isna().sum())
            null_pct = (nulls / nrows * 100) if nrows > 0 else 0.0
            norm = normalise(col)
            col_norm_map[col] = norm
            print(f"  {i:<5} {str(col):<35} {dtype:<15} {nulls:>8,} {null_pct:>6.1f}%")

        # ── REQUIRED FIELD CHECK ──────────────────────────────
        divider(f"REQUIRED FIELD CHECK — {sheet}")
        norm_cols = list(col_norm_map.values())
        raw_cols = list(col_norm_map.keys())

        for req in REQUIRED_FIELDS:
            req_norm = normalise(req)
            # Exact normalised match
            exact = req_norm in norm_cols
            # Fuzzy match — req string appears anywhere in column name
            fuzzy = any(req_norm in nc for nc in norm_cols)
            # Find matching raw name(s)
            matches = [raw for raw, norm in col_norm_map.items()
                       if req_norm in norm]
            if exact:
                status = "PRESENT ✓"
            elif fuzzy:
                status = "FUZZY MATCH ?"
            else:
                status = "NOT FOUND ✗"
            match_str = f"  → matched as: {matches}" if matches else ""
            print(f"  {req:<20} {status}{match_str}")

        # ── COLD-STUN FIELD CHECK ─────────────────────────────
        divider(f"COLD-STUN FIELD CHECK — {sheet}")
        cold_found = []
        for raw, norm in col_norm_map.items():
            if fuzzy_match(norm, COLD_STUN_CANDIDATES):
                cold_found.append(raw)
        if cold_found:
            print(f"  Cold-stun field(s) found: {cold_found}")
            for cf in cold_found:
                nulls = int(df[cf].isna().sum())
                print(f"    '{cf}': {nulls:,} nulls of {nrows:,} rows")
        else:
            print("  Cold-stun field: NOT FOUND")
            print("  NOTE: Exclusion fallback rule will be required.")
            print("        (lat > 35°N AND strand_month in Nov-Feb)")
            print("        Confirm this fallback is acceptable before")
            print("        writing the pipeline.")

        # ── CATEGORICAL CODE INVENTORY ────────────────────────
        # Only reports the coding scheme (what codes exist),
        # not counts or distributions.
        divider(f"CATEGORICAL CODE INVENTORY — {sheet}")
        print("  (Coding scheme only — required to write exclusion")
        print("   pipeline. Not value counts or distributions.)\n")

        for cat_field in CATEGORICAL_FIELDS_FOR_CODES:
            cat_norm = normalise(cat_field)
            matched_cols = [raw for raw, norm in col_norm_map.items()
                            if cat_norm in norm]
            if not matched_cols:
                print(f"  {cat_field:<20} — column not found, skipping")
                continue
            for mc in matched_cols:
                try:
                    unique_vals = df[mc].dropna().unique().tolist()
                    # Sort for readability
                    try:
                        unique_vals_sorted = sorted(unique_vals)
                    except TypeError:
                        unique_vals_sorted = unique_vals
                    n_unique = len(unique_vals_sorted)
                    # Cap at 20 to avoid printing entire value space
                    display = unique_vals_sorted[:20]
                    truncated = n_unique > 20
                    print(f"  {str(mc):<30} {n_unique} unique codes")
                    for v in display:
                        print(f"    '{v}'")
                    if truncated:
                        print(f"    ... and {n_unique - 20} more")
                    print()
                except Exception as e:
                    print(f"  {mc}: could not read unique values — {e}")

    # ── MULTI-SHEET SUMMARY ───────────────────────────────────
    if len(all_sheets) > 1:
        divider("MULTI-SHEET SUMMARY")
        print("  More than one sheet detected.")
        print("  Confirm which sheet contains the primary stranding")
        print("  records before writing the pipeline.")
        for name, df in all_sheets.items():
            print(f"    '{name}': {df.shape[0]:,} rows × {df.shape[1]} cols")

    # ── DONE ──────────────────────────────────────────────────
    divider("DIAGNOSTIC COMPLETE")
    print("  Paste the full output of this script (everything")
    print("  printed above this line) back to Copilot.")
    print("  Do not open or examine the data further until the")
    print("  analysis pipeline scripts are written.")
    divider()


if __name__ == "__main__":
    run_diagnostics(DATA_FILE)
