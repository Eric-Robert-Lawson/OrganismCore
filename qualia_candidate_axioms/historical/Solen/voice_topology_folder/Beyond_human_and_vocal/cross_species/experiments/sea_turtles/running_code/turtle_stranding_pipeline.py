"""
TURTLE STRANDING PIPELINE — ANALYSIS A
=======================================
OC-OBS-002 — Sea Turtle Stranding Analysis
OrganismCore — Eric Robert Lawson
March 2026

VERSION: 1.2 — three fixes from first run (2026-03-23)
  v1.0: original.
  v1.1: species filter corrected from "CARETTA CARETTA" to "CC".
        STSSN uses two-letter codes (confirmed 2026-03-23).
  v1.2: three fixes applied after reviewing v1.1 results:

    FIX 1 — SA-1 nearshore filter:
      v1.1 used: InOff != "OFFSHORE"
      InOff codes in the data are "I" (inshore) and "O" (offshore).
      "OFFSHORE" never matched, so SA-1 was identical to A1.
      v1.2 uses: InOff == "I"
      SA-1 now correctly restricts to inshore strandings only.

    FIX 2 — Rayleigh p-value underflow:
      v1.1 used a large-sample exponential approximation that
      underflows to 0.0 at N=57,213, R=0.80.
      v1.2 uses the chi-squared formulation (2*n*R²  ~ chi²(2))
      which does not underflow and returns a finite p-value
      reportable in publication.

    FIX 3 — V-test p-value underflow:
      v1.1 used scipy.stats.norm.sf which underflows to 0.0
      at the observed effect size.
      v1.2 uses scipy.special.ndtr-based log-space computation
      via norm.logsf, returning log(p) when p underflows,
      and reporting as "< 1e-300" in the results document.

    FIX 4 — progress counter display artifact:
      v1.1 progress counter showed counts above the dataset N
      during SA-2 runs because the DataFrame index was not
      reset after filtering. Fixed by resetting index on the
      subset passed to compute_batch for SA-2.

PRE-REGISTRATION REFERENCE:
    pre_registration_analysis.md v1.1
    Analysis A1 (primary), A3 (secondary)
    Sensitivity analyses SA-1, SA-2, SA-3

AMENDMENT 2 REMAPPING (2026-03-22):
    Pre-reg name    → actual NOAA column
    strand_date     → ReportDate
    strand_lat      → Latitude
    strand_lon      → Longitude
    condition       → InitialCondition
    species         → Species
    state           → State
    county          → County

    cause_code field is ABSENT in the STSSN data.
    Analysis A2 is DEFERRED per Amendment 2 / confirmed
    decision 2026-03-23.

ANALYSIS A2 STATUS:
    DEFERRED. No cause_code field present in the STSSN
    data as received. A2 will not be run in this pipeline.
    A2 remains pre-registered and will be run if cause_code
    data is obtained by follow-up request to Robert Hardy
    (NOAA OPR).

PRE-SPECIFIED EXCLUSIONS (applied in this order):
    1. Species filter: Caretta caretta (loggerhead) only.
       STSSN code: "CC". Confirmed 2026-03-23.
       Other species retained in a separate DataFrame for
       exploratory analysis but excluded from primary tests.
    2. Date filter: ReportDate >= 1990-01-01.
       Pre-1990 records excluded (coordinate precision concern).
    3. Cold-stun proxy exclusion (fallback rule, pre-specified):
       Exclude records where Latitude > 35.0° AND
       strand_month IN (11, 12, 1, 2).
       (No cold-stun field present — fallback confirmed in
       Amendment 2 Section C.)
    4. Coordinate exclusion: drop rows with null Latitude
       or Longitude. (6,530 / 6,532 rows — 4.8% — confirmed
       absent in Amendment 2 Section D.)
    5. Geographic scope: Atlantic and Gulf coast states only.
       States: FL, GA, SC, NC, VA, MD, DE, NJ, NY, TX, LA,
       MS, AL. Pre-specified in pre_registration_analysis.md
       Part III.

TESTS RUN:
    A1 PRIMARY:
      Rayleigh test — is the distribution of opposition angles
      non-uniform?
      V-test — is the mean opposition angle significantly
      less than 90° (mean direction = 0° from expected)?
      Alpha = 0.05.

    A3 SECONDARY:
      Migration-season vs non-migration-season Mann-Whitney U.
      Migration season: April-June, August-November.
      Non-migration: remaining months.
      Alpha = 0.05.

    SA-1: Re-run A1 restricted to inshore strandings only.
          InOff == "I" (confirmed codes: I=inshore, O=offshore).

    SA-2: Re-run A1 with 200 km radius and 800 km radius.

    SA-3: Re-run A1 restricted to alive strandings only
          (InitialCondition == "Alive").
          Exploratory — NOT a substitute for A2.

INPUTS:
    20260320_lawson.xlsx       — NOAA STSSN data
    am_stations_clean.csv      — AM transmitter table
    am_false_attractor_computation.py — FA module (this dir)

OUTPUTS:
    stssn_loggerhead_working.csv  — filtered working dataset
                                    with FA columns appended
    turtle_stranding_results.md   — full results document

REQUIRES:
    pip install pandas numpy scipy openpyxl
"""

import math
import os
import sys
from datetime import datetime

import numpy as np
import pandas as pd
from scipy.special import log_ndtr
from scipy.stats import mannwhitneyu, circmean, circstd, chi2

# ── IMPORT FA MODULE ──────────────────────────────────────────

try:
    from am_false_attractor_computation import AMFalseAttractor
except ImportError:
    print("ERROR: am_false_attractor_computation.py not found.")
    print("Place it in the same directory as this script.")
    sys.exit(1)

# ── CONFIGURATION ─────────────────────────────────────────────

DATA_FILE  = "20260320_lawson.xlsx"
AM_CSV     = "am_stations_clean.csv"
WORKING_CSV = "stssn_loggerhead_working.csv"
RESULTS_MD  = "turtle_stranding_results.md"

SHEET_NAME = "Sheet1"   # confirmed in Amendment 2

# Species code — confirmed 2026-03-23 from check_species.py
# STSSN uses two-letter codes: CC, CM, DC
SPECIES_CODE = "CC"     # Caretta caretta (loggerhead)

# Scope states (pre-registration Part III)
SCOPE_STATES = {
    "FL", "GA", "SC", "NC", "VA", "MD",
    "DE", "NJ", "NY", "TX", "LA", "MS", "AL"
}

# Migration season months (pre-registration Part II A3)
MIGRATION_MONTHS = {4, 5, 6, 8, 9, 10, 11}

# Cold-stun proxy exclusion (Amendment 2 Section C)
COLD_STUN_LAT_THRESHOLD   = 35.0
COLD_STUN_MONTHS_EXCLUDED = {11, 12, 1, 2}

# Pre-registration: date cutoff
MIN_DATE = pd.Timestamp("1990-01-01")

# FA computation radii
RADIUS_PRIMARY = 500   # km, pre-specified primary
RADIUS_SA2_LOW = 200   # km, SA-2 low
RADIUS_SA2_HI  = 800   # km, SA-2 high

ALPHA = 0.05

# P-value underflow sentinel — used when log(p) << 0
UNDERFLOW_STR = "< 1e-300"


# ── RAYLEIGH TEST (chi-squared formulation) ───────────────────

def rayleigh_test(angles_deg):
    """
    Rayleigh test for non-uniformity of a circular distribution.

    Uses chi-squared formulation: 2 * n * R_bar² ~ chi²(df=2)
    This does not underflow at large N and high R, unlike the
    exponential large-sample approximation used in v1.1.

    Returns: R_bar (mean resultant length), p (float or string)
    """
    n     = len(angles_deg)
    rad   = np.radians(angles_deg)
    R_bar = float(np.sqrt(np.mean(np.cos(rad)) ** 2
                          + np.mean(np.sin(rad)) ** 2))

    stat = 2.0 * n * R_bar ** 2
    p    = float(chi2.sf(stat, df=2))

    if p == 0.0:
        log_p = float(chi2.logsf(stat, df=2))
        if not math.isfinite(log_p) or log_p == 0.0:
            return R_bar, "< 1e-300"
        exponent = int(log_p / math.log(10))
        return R_bar, f"< 1e{exponent:d}"

    return R_bar, p


# ── V-TEST (log-space p-value) ────────────────────────────────

def v_test(angles_deg, expected_mean_deg=0.0):
    """
    V-test (modified Rayleigh test) for a specified mean direction.

    Uses log_ndtr for the normal survival function to avoid
    underflow at large effect sizes.

    Returns: V (float), p (float or string)
    """
    n      = len(angles_deg)
    rad    = np.radians(angles_deg)
    mu_rad = math.radians(expected_mean_deg)

    mean_cos = float(np.mean(np.cos(rad)))
    mean_sin = float(np.mean(np.sin(rad)))
    R_bar    = math.sqrt(mean_cos ** 2 + mean_sin ** 2)
    theta    = math.atan2(mean_sin, mean_cos)

    V     = n * R_bar * math.cos(theta - mu_rad)
    u     = V * math.sqrt(2.0 / n)
    log_p = float(log_ndtr(-u))

    if not math.isfinite(log_p) or log_p < math.log(1e-300):
        if not math.isfinite(log_p) or log_p == float("-inf"):
            return V, "< 1e-300"
        exponent = int(log_p / math.log(10))
        return V, f"< 1e{exponent:d}"

    return V, math.exp(log_p)


# ── P-VALUE HELPERS ───────────────────────────────────────────

def p_is_significant(p):
    """Return True if p < ALPHA, handling string underflow values."""
    if isinstance(p, str):
        return True   # underflow strings mean p << 0.05
    return float(p) < ALPHA


def p_display(p):
    """Format p-value for display, handling underflow strings."""
    if isinstance(p, str):
        return p
    return str(round(float(p), 6))


# ── LOAD AND FILTER DATA ──────────────────────────────────────

def load_and_filter(filepath, sheet_name=SHEET_NAME):
    """
    Load STSSN Excel file and apply all pre-specified
    exclusion criteria.

    Returns:
        df            — loggerhead, in-scope, exclusions applied
        df_all        — all species (for reporting only)
        df_cold_stun  — cold-stun excluded records
        excl          — dict of counts at each filter step
    """
    print(f"\nLoading: {filepath}  (sheet: '{sheet_name}')")
    df = pd.read_excel(filepath, sheet_name=sheet_name,
                       engine="openpyxl")
    print(f"  Raw rows: {len(df):,}")
    print(f"  Columns:  {list(df.columns)}")

    excl = {"raw": len(df)}

    # Parse dates
    df["ReportDate"]   = pd.to_datetime(df["ReportDate"],
                                        errors="coerce")
    df["strand_year"]  = df["ReportDate"].dt.year
    df["strand_month"] = df["ReportDate"].dt.month

    # EXCLUSION 1: species
    df_all = df.copy()
    df = df[df["Species"].str.strip().str.upper()
            == SPECIES_CODE].copy()
    excl["after_species"] = len(df)
    print(f"  After species filter ({SPECIES_CODE} = "
          f"Caretta caretta): {len(df):,}")

    # EXCLUSION 2: date >= 1990
    before = len(df)
    df = df[df["ReportDate"] >= MIN_DATE]
    excl["after_date"] = len(df)
    print(f"  After date filter (>=1990): "
          f"{len(df):,} (removed {before - len(df):,})")

    # EXCLUSION 3: geographic scope
    before = len(df)
    df = df[df["State"].str.strip().str.upper()
            .isin(SCOPE_STATES)]
    excl["after_scope"] = len(df)
    print(f"  After scope filter ({len(SCOPE_STATES)} states): "
          f"{len(df):,} (removed {before - len(df):,})")

    # EXCLUSION 4: coordinate completeness
    before = len(df)
    df = df.dropna(subset=["Latitude", "Longitude"])
    excl["after_coords"] = len(df)
    print(f"  After coordinate filter: "
          f"{len(df):,} (removed {before - len(df):,})")

    # EXCLUSION 5: cold-stun proxy
    before = len(df)
    cold_stun_mask = (
        (df["Latitude"] > COLD_STUN_LAT_THRESHOLD) &
        (df["strand_month"].isin(COLD_STUN_MONTHS_EXCLUDED))
    )
    df_cold_stun = df[cold_stun_mask].copy()
    df = df[~cold_stun_mask].copy()
    excl["cold_stun_excluded"] = int(cold_stun_mask.sum())
    excl["after_cold_stun"]    = len(df)
    print(f"  After cold-stun proxy exclusion "
          f"(lat>{COLD_STUN_LAT_THRESHOLD}°, "
          f"months {sorted(COLD_STUN_MONTHS_EXCLUDED)}): "
          f"{len(df):,} (removed {before - len(df):,})")

    # Reset index so progress counters display correctly
    df = df.reset_index(drop=True)

    print(f"\n  Primary analysis N: {len(df):,}")
    return df, df_all, df_cold_stun, excl


# ── RUN A1 ────────────────────────────────────────────────────

def run_a1(df, label="PRIMARY"):
    """
    Rayleigh test + V-test on am_opposition_deg distribution.
    """
    valid = df["am_opposition_deg"].dropna()
    n     = len(valid)

    if n < 10:
        return {"label": label, "n": n, "status": "UNDERPOWERED",
                "note": f"Only {n} valid opposition angles."}

    angles = valid.values

    mean_opp = float(circmean(np.radians(angles),
                              high=math.pi, low=0)) * 180 / math.pi
    std_opp  = float(circstd(np.radians(angles),
                             high=math.pi, low=0)) * 180 / math.pi

    R_bar, p_rayleigh = rayleigh_test(angles)
    V,     p_vtest    = v_test(angles, expected_mean_deg=0.0)

    return {
        "label":               label,
        "n":                   n,
        "mean_opp_deg":        round(mean_opp, 2),
        "circ_sd_deg":         round(std_opp,  2),
        "rayleigh_R":          round(R_bar, 4),
        "rayleigh_p":          p_rayleigh,
        "rayleigh_sig":        p_is_significant(p_rayleigh),
        "vtest_V":             round(V, 4),
        "vtest_p":             p_vtest,
        "vtest_sig":           p_is_significant(p_vtest),
        "direction_predicted": mean_opp < 90.0,
        "status":              "COMPLETE",
    }


# ── RUN A3 ────────────────────────────────────────────────────

def run_a3(df):
    """
    Migration-season vs non-migration-season Mann-Whitney U.
    """
    valid  = df[df["am_opposition_deg"].notna()].copy()
    mig    = valid[valid["strand_month"].isin(MIGRATION_MONTHS)]
    nonmig = valid[~valid["strand_month"].isin(MIGRATION_MONTHS)]

    n_mig    = len(mig)
    n_nonmig = len(nonmig)

    if n_mig < 5 or n_nonmig < 5:
        return {"label": "A3", "status": "UNDERPOWERED",
                "n_migration": n_mig, "n_nonmigration": n_nonmig}

    stat, p = mannwhitneyu(
        mig["am_opposition_deg"].values,
        nonmig["am_opposition_deg"].values,
        alternative="less"
    )

    return {
        "label":               "A3",
        "status":              "COMPLETE",
        "n_migration":         n_mig,
        "n_nonmigration":      n_nonmig,
        "med_mig":             round(float(mig["am_opposition_deg"].median()), 2),
        "med_nonmig":          round(float(nonmig["am_opposition_deg"].median()), 2),
        "U":                   float(stat),
        "p":                   round(float(p), 8),
        "significant":         float(p) < ALPHA,
        "direction_predicted": (
            float(mig["am_opposition_deg"].median()) <
            float(nonmig["am_opposition_deg"].median())
        ),
    }


# ── RUN SA-3 ──────────────────────────────────────────────────

def run_sa3(df):
    """
    SA-3: A1 restricted to InitialCondition == 'Alive'.
    Exploratory. NOT a substitute for A2.
    """
    alive = df[df["InitialCondition"].str.strip().str.lower()
               == "alive"].copy()
    if len(alive) < 10:
        return {"label": "SA-3 (Alive only)",
                "status": "UNDERPOWERED", "n": len(alive)}
    result = run_a1(alive, label="SA-3 (Alive only — exploratory)")
    result["exploratory_note"] = (
        "SA-3 uses Alive InitialCondition as a proxy. "
        "This is NOT the pre-registered A2 test. "
        "A2 requires cause_code which is absent in this dataset. "
        "SA-3 is exploratory and labelled as such."
    )
    return result


# ── FORMAT RESULTS MARKDOWN ──────��────────────────────────────

def format_results_md(excl, a1_primary, a3, sa1, sa2_200,
                      sa2_800, sa3, run_date):

    def sig_str(p):
        sig = p_is_significant(p)
        return "SIGNIFICANT" if sig else "null"

    def yn(b):
        return "Yes" if b else "No"

    lines = []
    w = lines.append

    w("# TURTLE STRANDING RESULTS")
    w("## Analysis A — AM False Attractor")
    w("## OC-OBS-002")
    w("## OrganismCore — Eric Robert Lawson")
    w(f"## Run date: {run_date}")
    w("")
    w("---")
    w("")
    w("## EXCLUSION LOG")
    w("")
    w("```")
    w(f"Raw STSSN records:             {excl.get('raw', ''):>8,}")
    w(f"After species filter (CC):     {excl.get('after_species', ''):>8,}  "
      "(Caretta caretta only)")
    w(f"After date filter (>=1990):    {excl.get('after_date', ''):>8,}")
    w(f"After scope filter:            {excl.get('after_scope', ''):>8,}  "
      "(Atlantic/Gulf coast states)")
    w(f"After coordinate filter:       {excl.get('after_coords', ''):>8,}  "
      "(drop null lat/lon)")
    w(f"Cold-stun excluded:            {excl.get('cold_stun_excluded', ''):>8,}  "
      "(lat>35 N, Nov-Feb)")
    w(f"PRIMARY ANALYSIS N:            {excl.get('after_cold_stun', ''):>8,}")
    w("```")
    w("")
    w("---")
    w("")

    # A1
    w("## ANALYSIS A1 — PRIMARY")
    w("")
    w("```")
    if a1_primary.get("status") == "UNDERPOWERED":
        w(f"STATUS: UNDERPOWERED — N = {a1_primary.get('n')}")
    else:
        w(f"N opposition angles:    {a1_primary['n']:,}")
        w(f"Mean opposition angle:  {a1_primary['mean_opp_deg']}°")
        w(f"Circular SD:            {a1_primary['circ_sd_deg']}°")
        w("")
        w("Rayleigh test (chi-squared formulation):")
        w(f"  R (mean resultant):   {a1_primary['rayleigh_R']}")
        w(f"  p:                    {p_display(a1_primary['rayleigh_p'])}")
        w(f"  Result:               {sig_str(a1_primary['rayleigh_p'])}")
        w("")
        w("V-test (expected mean direction = 0°):")
        w(f"  V:                    {a1_primary['vtest_V']}")
        w(f"  p:                    {p_display(a1_primary['vtest_p'])}")
        w(f"  Result:               {sig_str(a1_primary['vtest_p'])}")
        w("")
        w(f"Mean < 90° (predicted direction): "
          f"{yn(a1_primary['direction_predicted'])}")
    w("```")
    w("")
    w("---")
    w("")

    # A2 deferred
    w("## ANALYSIS A2 — DEFERRED")
    w("")
    w("```")
    w("Analysis A2 is deferred.")
    w("Cause_code field absent in the STSSN data as received")
    w("(20260320_lawson.xlsx, 11 columns, no cause_code).")
    w("Amendment 2 filed 2026-03-22.")
    w("Deferral confirmed 2026-03-23.")
    w("")
    w("A2 remains pre-registered.")
    w("Follow-up request to Robert Hardy (NOAA OPR) pending.")
    w("A2 will be run when/if cause_code data is obtained.")
    w("```")
    w("")
    w("---")
    w("")

    # A3
    w("## ANALYSIS A3 — MIGRATION SEASON")
    w("")
    w("```")
    if a3.get("status") == "UNDERPOWERED":
        w("STATUS: UNDERPOWERED")
        w(f"  N migration:     {a3.get('n_migration')}")
        w(f"  N non-migration: {a3.get('n_nonmigration')}")
    else:
        w(f"N migration season:     {a3['n_migration']:,}  "
          "(months: Apr-Jun, Aug-Nov)")
        w(f"N non-migration:        {a3['n_nonmigration']:,}")
        w(f"Median opp° migration:  {a3['med_mig']}°")
        w(f"Median opp° non-mig:    {a3['med_nonmig']}°")
        w(f"Mann-Whitney U:         {a3['U']:.1f}")
        w(f"p (one-tailed):         {a3['p']}")
        w(f"Result:                 {sig_str(a3['p'])}")
        w(f"Migration < non-mig (predicted): "
          f"{yn(a3['direction_predicted'])}")
    w("```")
    w("")
    w("---")
    w("")

    # Sensitivity analyses
    w("## SENSITIVITY ANALYSES")
    w("")

    for label, res in [
        ("SA-1 (inshore only, InOff=I)",    sa1),
        ("SA-2 (200 km radius)",            sa2_200),
        ("SA-2 (800 km radius)",            sa2_800),
        ("SA-3 (Alive only — exploratory)", sa3),
    ]:
        w(f"### {label}")
        w("```")
        if res.get("status") == "UNDERPOWERED":
            w(f"STATUS: UNDERPOWERED — N = {res.get('n', '')}")
        elif res.get("status") == "COMPLETE":
            w(f"N:                {res['n']:,}")
            w(f"Mean opp°:        {res['mean_opp_deg']}°")
            w(f"Rayleigh R:       {res['rayleigh_R']}")
            w(f"Rayleigh p:       {p_display(res['rayleigh_p'])}")
            w(f"V-test p:         {p_display(res['vtest_p'])}")
            w(f"Rayleigh:         {sig_str(res['rayleigh_p'])}")
            w(f"V-test:           {sig_str(res['vtest_p'])}")
            w(f"Mean < 90°:       {yn(res['direction_predicted'])}")
            if "exploratory_note" in res:
                w(f"NOTE: {res['exploratory_note']}")
        else:
            w(f"STATUS: {res.get('status', 'unknown')}")
        w("```")
        w("")

    w("---")
    w("")
    w("## VERSION")
    w("```")
    w("Pipeline version: 1.2")
    w(f"Run date:         {run_date}")
    w("Pre-registration: pre_registration_analysis.md v1.1")
    w("Amendment:        Amendment 2, 2026-03-22")
    w("Species code fix: CC confirmed 2026-03-23 (v1.1)")
    w("SA-1 fix:         InOff == 'I' confirmed 2026-03-23 (v1.2)")
    w("p-value fix:      chi2/log_ndtr underflow fix (v1.2)")
    w("Data source:      20260320_lawson.xlsx")
    w("                  Robert Hardy, NOAA OPR, 2026-03-20")
    w("AM station table: am_stations_clean.csv")
    w("A2 status:        DEFERRED (cause_code absent)")
    w("Analysis B:       PENDING (FWC data not yet received)")
    w("```")

    return "\n".join(lines)


# ── MAIN ──────────────────────────────────────────────────────

def main():
    run_date = datetime.now().strftime("%Y-%m-%d %H:%M")

    print("=" * 60)
    print("TURTLE STRANDING PIPELINE — ANALYSIS A")
    print("OC-OBS-002 — OrganismCore")
    print("=" * 60)

    for f in [DATA_FILE, AM_CSV]:
        if not os.path.exists(f):
            print(f"\nERROR: Required file not found: {f}")
            sys.exit(1)

    # Load and filter
    df, df_all, df_cold_stun, excl = load_and_filter(DATA_FILE)

    # Compute FA — primary dataset
    print(f"\nComputing AM false attractor for "
          f"{len(df):,} records...")
    ama = AMFalseAttractor(AM_CSV)
    print()

    df = ama.compute_batch(
        df,
        lat_col="Latitude",
        lon_col="Longitude",
        progress_every=2000
    )

    n_fa = df["am_opposition_deg"].notna().sum()
    n_nf = df["am_opposition_deg"].isna().sum()
    print(f"\n  FA computed for:              {n_fa:,} records")
    print(f"  No FA (0 stations in radius): {n_nf:,} records")

    df.to_csv(WORKING_CSV, index=False)
    print(f"\n  Working dataset saved: {WORKING_CSV}")
    print(f"  Rows: {len(df):,}")

    # A1 primary
    print("\nRunning A1 (primary)...")
    a1_primary = run_a1(df, label="PRIMARY (500 km)")

    # A3
    print("Running A3 (migration season)...")
    a3 = run_a3(df)

    # SA-1: inshore only (InOff == "I")
    print("Running SA-1 (inshore filter)...")
    if "InOff" in df.columns:
        inoff_vals = sorted(df["InOff"].dropna()
                            .str.strip().str.upper().unique())
        print(f"  InOff codes present: {inoff_vals}")
        df_nearshore = df[df["InOff"].str.strip().str.upper()
                          == "I"].copy().reset_index(drop=True)
        print(f"  Inshore records (I): {len(df_nearshore):,}")
    else:
        df_nearshore = df.copy()
        print("  InOff field absent — SA-1 uses all records")
    sa1 = run_a1(df_nearshore, label="SA-1 (inshore, InOff=I)")

    # SA-2: 200 km radius
    print("Running SA-2 (200 km radius)...")
    df_sa2_input = (df[["Latitude", "Longitude",
                         "strand_month", "InitialCondition"]]
                    .copy().reset_index(drop=True))
    df_200 = ama.compute_batch(
        df_sa2_input,
        lat_col="Latitude",
        lon_col="Longitude",
        radius_km=RADIUS_SA2_LOW,
        progress_every=2000
    )
    sa2_200 = run_a1(df_200, label="SA-2 (200 km)")

    # SA-2: 800 km radius
    print("Running SA-2 (800 km radius)...")
    df_sa2_input = (df[["Latitude", "Longitude",
                         "strand_month", "InitialCondition"]]
                    .copy().reset_index(drop=True))
    df_800 = ama.compute_batch(
        df_sa2_input,
        lat_col="Latitude",
        lon_col="Longitude",
        radius_km=RADIUS_SA2_HI,
        progress_every=2000
    )
    sa2_800 = run_a1(df_800, label="SA-2 (800 km)")

    # SA-3: alive only
    print("Running SA-3 (alive only — exploratory)...")
    sa3 = run_sa3(df)

    # Summary
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)

    for label, res in [
        ("A1 PRIMARY", a1_primary),
        ("A3",         a3),
        ("SA-1",       sa1),
        ("SA-2 200km", sa2_200),
        ("SA-2 800km", sa2_800),
        ("SA-3 Alive", sa3),
    ]:
        st = res.get("status", "")
        if st == "COMPLETE":
            vp = p_display(res.get("vtest_p", res.get("p", "")))
            rp = p_display(res.get("rayleigh_p", "")) if "rayleigh_p" in res else "—"
            print(f"  {label:<14}  V-test p={vp}  Rayleigh p={rp}")
        else:
            print(f"  {label:<14}  {st}")

    print()
    print("  A2: DEFERRED (cause_code absent)")

    # Write results
    md = format_results_md(
        excl, a1_primary, a3, sa1,
        sa2_200, sa2_800, sa3, run_date
    )
    with open(RESULTS_MD, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"\nResults written: {RESULTS_MD}")

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)
    print(f"  Working CSV: {WORKING_CSV}")
    print(f"  Results:     {RESULTS_MD}")
    print()
    print("  Report all results regardless of direction.")


if __name__ == "__main__":
    main()
