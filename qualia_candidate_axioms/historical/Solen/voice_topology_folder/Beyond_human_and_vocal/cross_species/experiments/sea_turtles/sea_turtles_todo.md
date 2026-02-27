# SEA TURTLE ANALYSIS — TODO
## Status Tracker and Action Queue
## OC-OBS-002
## February 27, 2026

---

## CURRENT STATUS

```
Pre-registration:    COMPLETE ✅
  pre_registration_analysis.md
  v1.1 (Amendment 1 appended)
  GitHub commit timestamp =
  pre-registration record of
  authority. Data not yet received.

Data requests:       SENT ⏳
  FWC:   mtp@myfwc.com
         Sent Feb 27, 2026
         No bounce. Awaiting response.
  NOAA:  nmfs.opr.stssn@noaa.gov
         Sent Feb 27, 2026
         Awaiting response.
  NOTE:  stssn@noaa.gov — bounced
           550 5.7.1 Feb 27, 2026
         wendy.teas@noaa.gov — bounced
           550 5.7.1 Feb 27, 2026

Analysis code:       NOT YET WRITTEN
  am_false_attractor_computation.py
    — not yet written
  turtle_stranding_pipeline.py
    — not yet written
  turtle_cohort_analysis.py
    — not yet written

Data in hand:        NONE
  NOAA STSSN: not yet received
  FWC nesting records: not yet received
  Movebank: not yet queried
  am_stations_clean.csv: READY ✅
  cable_landing_stations.csv: READY ✅
```

---

## BLOCKING ITEMS
## (nothing proceeds until resolved)

```
BLOCK 1 — NOAA STSSN DATA:
  Required for: Analysis A (primary)
  Blocked on: data access approval
  Current contact: nmfs.opr.stssn@noaa.gov
  Fallback if no response by
  March 14, 2026:
    NOAA SEFSC web contact form:
    https://www.fisheries.noaa.gov/
    contact/southeast-fisheries-
    science-center
  Fallback 2 if still no response
  by March 28, 2026:
    Check NOAA InPort item 3742
    for updated POC:
    https://www.fisheries.noaa.gov/
    inport/item/3742

BLOCK 2 — FWC NESTING DATA:
  Required for: Analysis B (primary)
  Blocked on: data access approval
  Current contact: mtp@myfwc.com
  Fallback if no response by
  March 14, 2026:
    FWC Fish and Wildlife Research
    Institute main line:
    850-487-3796
```

---

## WHEN NOAA DATA ARRIVES

```
□ STEP 1 — LOG DATA RECEIPT
  Record date received in this
  file under DATA RECEIPT LOG
  section below.
  Confirm pre-registration commit
  timestamp predates receipt date.

□ STEP 2 — WRITE
  am_false_attractor_computation.py
  Inputs: am_stations_clean.csv,
    stranding lat/lon from STSSN
  Outputs: FA bearing, geo bearing,
    opposition angle per stranding
  Method: per pre_registration_
    analysis.md Part III exactly

□ STEP 3 — WRITE
  turtle_stranding_pipeline.py
  Full Analysis A pipeline:
  - Load STSSN data
  - Apply pre-specified exclusions:
      cold-stun events excluded
      (or lat > 35°N in Nov-Feb
      if cold-stun field absent)
      coordinate precision > 10km
      excluded
      pre-1990 records excluded
  - Compute opposition angle
    per record using
    am_false_attractor_computation.py
  - Run Rayleigh test
  - Run V-test (expected dir = 0°)
  - Run A2: unknown-cause vs
    known-cause Mann-Whitney U
  - Run A3: migration-season vs
    non-migration-season Mann-Whitney U
  - Run sensitivity analyses
    SA-1, SA-2, SA-3
  - Output: full numerical record
    + figures

□ STEP 4 — RUN PIPELINE
  Do not modify pre-specified
  exclusions or tests after
  seeing data. If deviation
  is required, document as
  amendment before running.

□ STEP 5 — WRITE
  turtle_stranding_results.md
  Report ALL of:
    N strandings included/excluded
    Mean opposition angle
    Circular SD
    Rayleigh R and p
    V-test statistic and p
    A2 result
    A3 result
    All SA results
    Direction consistent with
    prediction: yes/no
  Report regardless of direction.

□ STEP 6 — RUN SENSITIVITY
  ANALYSES SA-1, SA-2, SA-3
  as pre-specified.
  SA-3 (nesting females only)
  only if sex field present
  in STSSN data.
```

---

## WHEN FWC DATA ARRIVES

```
□ STEP 1 — LOG DATA RECEIPT
  Record date received in this
  file under DATA RECEIPT LOG.

□ STEP 2 — WRITE
  turtle_cohort_analysis.py
  Inputs: FWC nesting records,
    cable_landing_stations.csv
  Pipeline:
  - Load individual nesting records
  - Apply installation year filter:
    only cables installed before
    estimated frenzy swim year
    of each turtle
  - Classify: cable cohort
    (first nest within 1 km),
    control cohort (first nest
    > 5 km), intermediate (excluded)
  - Compute spread_km per individual
    (≥ 3 records required)
  - Mann-Whitney U test (one-tailed)
  - Effect size: rank-biserial r
  - B2: Rayleigh + V-test on
    displacement bearings
  - B3: Spearman cable anomaly
    vs spread (if ≥ 3 cables,
    ≥ 5 turtles each)
  - SA-4: re-run at 500m and 2km
  - SA-5: monotonic proximity test
  - SA-6: Florida Atlantic coast
    restricted

□ STEP 3 — RUN PIPELINE
  Same constraint as Analysis A:
  no post-hoc modification of
  pre-specified tests.

□ STEP 4 — WRITE
  turtle_nesting_results.md
  Report ALL of:
    N per cohort (cable, control,
    intermediate excluded)
    Median spread per cohort
    IQR per cohort
    U statistic and p
    Rank-biserial r
    B2 result (if run)
    B3 result (if run / if deferred)
    All SA results
  Report regardless of direction.

□ STEP 5 — COMBINED ANALYSIS C1
  Only if BOTH A1 and B1 are
  significant. Otherwise skip.
  Exploratory — no pre-specified
  direction.
```

---

## WHEN BOTH DATASETS ARE IN HAND

```
□ WRITE turtle_synthesis.md
  The definitive summary document
  for OC-OBS-002.
  Contains:
  - Complete numerical record
    (both analyses)
  - Honest interpretation of
    each outcome against the
    pre-registered prediction
    tree in Part VI of
    pre_registration_analysis.md
  - Position in the series
    (alongside DR23, EUMODIC,
    Monarch, Faraday cage)
  - What the result means for
    the unified framework
  - Next steps specific to
    whichever outcome occurred

□ UPDATE pre_registration_analysis.md
  Add Amendment 2 recording:
  - Actual data receipt dates
  - Any deviations from pre-
    specified protocol (if any)
    with documented rationale
  - Confirmed commit hash as
    pre-registration timestamp

□ DECIDE publication pathway
  Both significant (A1 + B1):
    Nature Communications or
    Conservation Biology.
    Preprint: bioRxiv immediately.
  A1 only:
    PLOS ONE or Marine Ecology
    Progress Series.
  B1 only:
    Conservation Biology or
    Biological Conservation.
  Both null:
    PLOS ONE null results track
    or similar. Pre-registration
    ensures publishability.
```

---

## PARALLEL ACTIONS
## (do not wait for turtle data)

```
These run independently while
turtle data requests are pending:

□ DR24 QUERY
  Robert Wilson (EBI) confirmed
  DR24 releasing imminently.
  When it releases:
  Query IMPC_OFD_001 open field
  data for new centers.
  Same procedure as DR23.
  Extend the ELF gradient.
  Status: WAITING FOR RELEASE ⏳

□ JAX FOLLOW-UP
  If no substantive response
  from JAX by end of business
  February 28, 2026:
  Contact: komp@jax.org
  Case reference: 03428362
  Status: PENDING ⏳

□ MONARCH WATCH
  Recovery data request sent.
  No action needed until response.
  Follow-up if no response by:
  March 14, 2026
  Status: WAITING ⏳

□ FARADAY CAGE (OC-EXP-001)
  Proceed toward IACUC submission.
  Requires: facility identification,
  PI sponsor identification.
  Does not depend on turtle data.
  Status: ACTIVE — no blocking ⏳

□ HMGU GMC INQUIRY
  Email sent to GMC team Feb 27,
  2026 re: GMCII construction
  timeline and testing room
  ELF environment.
  Follow-up if no response by:
  March 14, 2026
  Status: WAITING ⏳
```

---

## FOLLOW-UP DATE TRACKER

```
February 28, 2026:
  □ JAX follow-up if no response
    (komp@jax.org, case 03428362)

March 14, 2026:
  □ FWC follow-up if no response
    Phone: 850-487-3796
  □ NOAA follow-up if no response
    Web form: fisheries.noaa.gov/
    contact/southeast-fisheries-
    science-center
  □ Monarch Watch follow-up
  □ HMGU GMC follow-up

March 28, 2026:
  □ NOAA escalation if web form
    unanswered: check InPort item
    3742 for updated POC
    https://www.fisheries.noaa.gov/
    inport/item/3742
```

---

## DATA RECEIPT LOG
## (fill in when data arrives)

```
NOAA STSSN data:
  Date received: [not yet received]
  Contact who provided: —
  Format: —
  N records: —
  Date range covered: —
  Fields confirmed present:
    species: —
    strand_date: —
    strand_lat: —
    strand_lon: —
    condition: —
    cause_code: —
    cold_stun_field: — (present/absent)

FWC nesting data:
  Date received: [not yet received]
  Contact who provided: —
  Format: —
  N individual turtles: —
  N nesting records: —
  Date range covered: —
  Fields confirmed present:
    turtle_id (anonymized): —
    nest_date: —
    nest_lat: —
    nest_lon: —
    species: —
    beach_segment_code: —

Movebank:
  Queried: [not yet]
  Date queried: —
  N individuals: —
  N tracking days: —
```

---

## FILE INVENTORY

```
EXISTING:
  pre_registration_analysis.md
    v1.1 (Amendment 1 appended)
    Status: COMPLETE ✅

  SEA_TURTLE_TODO.md
    This file.
    Status: ACTIVE ✅

PENDING — write before data access:
  am_false_attractor_computation.py
  turtle_stranding_pipeline.py
  turtle_cohort_analysis.py

PENDING — write after analysis:
  turtle_stranding_results.md
  turtle_nesting_results.md
  turtle_synthesis.md

PUBLIC DATA ALREADY IN HAND:
  am_stations_clean.csv
    FCC AM transmitter database
    530-1700 kHz, cleaned
  cable_landing_stations.csv
    TeleGeography power cable
    landing stations, filtered
    (capacity_mw > 0)
```

---

## VERSION

```
v1.0 — February 27, 2026
  Initial TODO.
  Data requests sent.
  Awaiting responses.
  All analysis code pending.
  No data in hand.
  Pre-registration complete.
```
