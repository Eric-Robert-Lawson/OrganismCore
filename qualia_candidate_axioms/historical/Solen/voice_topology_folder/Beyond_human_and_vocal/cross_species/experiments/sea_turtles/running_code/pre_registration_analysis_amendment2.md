---

## AMENDMENT 2
## DATA STRUCTURE ADAPTATION
## March 22, 2026
## Filed upon first examination of STSSN data structure.
## No values examined. No analysis run.

### AMENDMENT METADATA
- Document: pre_registration_analysis.md
- Version: 1.2 (Amendment 2 appended)
- Filed: 2026-03-22
- Reason: STSSN data received 2026-03-22 from Robert Hardy,
  NOAA Office of Protected Resources. Structural diagnostic
  run prior to any value examination. Amendment filed to
  document field name remapping and one absent field before
  pipeline code is written.

### SECTION A — FIELD NAME REMAPPING

The STSSN data file (20260320_lawson.xlsx, Sheet1,
136,768 rows, 11 columns) uses different column names
from those assumed in the pre-registration. The following
remapping is confirmed and applied in all pipeline scripts:

| Pre-registration name | Actual NOAA column |
|---|---|
| strand_date | ReportDate |
| strand_lat | Latitude |
| strand_lon | Longitude |
| condition | InitialCondition |
| species | Species |
| state | State |
| county | County |

All pipeline scripts use the actual NOAA column names.
No pre-specified analysis is affected by this remapping.

### SECTION B — CAUSE_CODE FIELD ABSENT

The pre-registration specified use of a cause_code field
to stratify strandings into unknown-cause and known-cause
groups for Analysis A2 (secondary test: unknown-cause
strandings show stronger opposition angle signal than
known-cause strandings).

The STSSN data as provided does not contain a cause_code
field or any equivalent column. The 11 columns present are:
STSSNID, ReportDate, Species, InitialCondition, State,
County, Week, Zone, InOff, Latitude, Longitude.

**Adaptation for Analysis A2:**
Analysis A2 as pre-specified cannot be run as written.
Two options are documented here. Option selected must be
confirmed before pipeline code is written.

Option 1 — DEFER A2:
  Analysis A2 is deferred. Primary analysis A1 (Rayleigh
  test and V-test on full loggerhead dataset after
  pre-specified exclusions) proceeds as pre-registered.
  A2 is noted as deferred pending cause_code data which
  may be obtainable by follow-up request to Robert Hardy.

Option 2 — SUBSTITUTE A2 USING InitialCondition:
  InitialCondition has 6 codes: Alive, Dried carcass,
  Fresh dead or mildly decomposed, Moderately decomposed,
  Severely decomposed, Skeletal.
  A proxy stratification is possible: Alive strandings
  may represent a functionally different population
  (disorientation events) vs. dead strandings (mortality
  events). This is not equivalent to cause_code
  stratification and is explicitly exploratory.
  If used, this substitution is labelled as a
  post-hoc exploratory analysis in all results documents,
  not as the pre-registered A2 test.

**Selected option: [CONFIRM BEFORE PIPELINE RUNS]**

### SECTION C — COLD-STUN FIELD ABSENT

No cold-stun field is present in the data. The pre-
registration todo file documented this contingency and
specified the fallback exclusion rule:

  Exclude records where:
    Latitude > 35.0 (degrees N)
    AND strand_month IN (11, 12, 1, 2)

This fallback is confirmed and will be applied in the
pipeline as pre-specified. No amendment to the analysis
is required — this contingency was already documented.

### SECTION D — COORDINATE MISSINGNESS

6,530 records (4.8%) are missing Latitude.
6,532 records (4.8%) are missing Longitude.
These records will be excluded from all analyses requiring
opposition angle computation. Exclusion is pre-specified
(coordinate precision requirement) and requires no
amendment. The 2-record asymmetry will be documented
in the results file.

### SECTION E — ADDITIONAL FIELDS PRESENT

Three fields are present that were not in the
pre-registration: Week (int), Zone (float, 0.2% null),
InOff (object, 0.1% null).

These fields are not used in any pre-specified analysis.
Zone may be used in sensitivity analysis SA-3 (geographic
restriction) if it encodes regions consistent with the
pre-specified geographic scope. Any such use will be
labelled exploratory.

### VERSION
v1.2 — 2026-03-22 — Amendment 2 appended.
