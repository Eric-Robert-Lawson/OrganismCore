# TURTLE STRANDING RESULTS
## Analysis A — AM False Attractor
## OC-OBS-002
## OrganismCore — Eric Robert Lawson
## Run date: 2026-03-22 19:38

---

## EXCLUSION LOG

```
Raw STSSN records:              136,768
After species filter (CC):       63,335  (Caretta caretta only)
After date filter (>=1990):      63,335
After scope filter:              61,946  (Atlantic/Gulf coast states)
After coordinate filter:         58,833  (drop null lat/lon)
Cold-stun excluded:               1,620  (lat>35 N, Nov-Feb)
PRIMARY ANALYSIS N:              57,213
```

---

## ANALYSIS A1 — PRIMARY

```
N opposition angles:    57,213
Mean opposition angle:  64.46°
Circular SD:            40.15°

Rayleigh test (chi-squared formulation):
  R (mean resultant):   0.8007
  p:                    < 1e-300
  Result:               SIGNIFICANT

V-test (expected mean direction = 0°):
  V:                    17312.4182
  p:                    < 1e-2277
  Result:               SIGNIFICANT

Mean < 90° (predicted direction): Yes
```

---

## ANALYSIS A2 — DEFERRED

```
Analysis A2 is deferred.
Cause_code field absent in the STSSN data as received
(20260320_lawson.xlsx, 11 columns, no cause_code).
Amendment 2 filed 2026-03-22.
Deferral confirmed 2026-03-23.

A2 remains pre-registered.
Follow-up request to Robert Hardy (NOAA OPR) pending.
A2 will be run when/if cause_code data is obtained.
```

---

## ANALYSIS A3 — MIGRATION SEASON

```
N migration season:     42,181  (months: Apr-Jun, Aug-Nov)
N non-migration:        15,032
Median opp° migration:  67.41°
Median opp° non-mig:    69.24°
Mann-Whitney U:         309986751.0
p (one-tailed):         2.537e-05
Result:                 SIGNIFICANT
Migration < non-mig (predicted): Yes
```

---

## SENSITIVITY ANALYSES

### SA-1 (inshore only, InOff=I)
```
N:                14,758
Mean opp°:        54.4°
Rayleigh R:       0.809
Rayleigh p:       < 1e-300
V-test p:         < 1e-1029
Rayleigh:         SIGNIFICANT
V-test:           SIGNIFICANT
Mean < 90°:       Yes
```

### SA-2 (200 km radius)
```
N:                57,210
Mean opp°:        65.14°
Rayleigh R:       0.7892
Rayleigh p:       < 1e-300
V-test p:         < 1e-2169
Rayleigh:         SIGNIFICANT
V-test:           SIGNIFICANT
Mean < 90°:       Yes
```

### SA-2 (800 km radius)
```
N:                57,213
Mean opp°:        63.81°
Rayleigh R:       0.8046
Rayleigh p:       < 1e-300
V-test p:         < 1e-2381
Rayleigh:         SIGNIFICANT
V-test:           SIGNIFICANT
Mean < 90°:       Yes
```

### SA-3 (Alive only — exploratory)
```
N:                13,216
Mean opp°:        73.32°
Rayleigh R:       0.7873
Rayleigh p:       < 1e-300
V-test p:         0.0
Rayleigh:         SIGNIFICANT
V-test:           SIGNIFICANT
Mean < 90°:       Yes
NOTE: SA-3 uses Alive InitialCondition as a proxy. This is NOT the pre-registered A2 test. A2 requires cause_code which is absent in this dataset. SA-3 is exploratory and labelled as such.
```

---

## VERSION
```
Pipeline version: 1.2
Run date:         2026-03-22 19:38
Pre-registration: pre_registration_analysis.md v1.1
Amendment:        Amendment 2, 2026-03-22
Species code fix: CC confirmed 2026-03-23 (v1.1)
SA-1 fix:         InOff == 'I' confirmed 2026-03-23 (v1.2)
p-value fix:      chi2/log_ndtr underflow fix (v1.2)
Data source:      20260320_lawson.xlsx
                  Robert Hardy, NOAA OPR, 2026-03-20
AM station table: am_stations_clean.csv
A2 status:        DEFERRED (cause_code absent)
Analysis B:       PENDING (FWC data not yet received)
```