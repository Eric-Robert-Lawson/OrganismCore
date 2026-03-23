# VECTOR RESULTANT REPORT
## OC-OBS-002 — Force Model Analysis
## OrganismCore — Eric Robert Lawson
## Run date: 2026-03-22 19:57

---

## SCALING FACTOR

```
Optimal k:          5.751217e+05  (kW/km² → nT equivalent)
log10(k):           5.760
Mean residual at k: 35.84°
Optimum stable:     Yes
```

---

## RESULTANT DISTRIBUTION

```
Records with resultant:    57,213
Records without resultant: 0

Displacement (resultant vs geo north):
  Mean:    55.51°
  Median:  52.14°
  SD:      37.22°
  Min:     0.00°
  Max:     180.00°

  Displaced >  10°: 93.5%
  Displaced >  20°: 77.2%
  Displaced >  30°: 66.4%
  Displaced >  45°: 55.3%
  Displaced >  90°: 19.6%
```

---

## COASTAL SEGMENT BREAKDOWN

```
Segment                              N  Mean disp°  Med disp°  Mean opp°
───────────────────────────────────────────────────────────────────────────
  AL / MS / LA East              3,551      17.74°     15.78°     27.35°
  FL Atlantic                   22,224      43.39°     28.70°     56.67°
  FL Gulf / Panhandle           22,865      75.61°     76.55°     87.43°
  FL Keys/SW                     3,295      71.10°     67.88°     87.31°
  LA West / TX East              2,155      30.12°     25.73°     45.63°
  TX                             3,123      38.65°     38.60°     58.76°
```

---

## INTERPRETATION NOTES

```
displacement_deg = angular difference between the
vector resultant bearing and geomagnetic north.

displacement_deg = 0°:  resultant equals geomagnetic
  north. AM force is negligible or perfectly aligned.
  Turtle goes where its compass points.

displacement_deg > 0°:  resultant is rotated away from
  geomagnetic north toward the AM false attractor.
  Turtle strands at the location the resultant points to,
  not where geomagnetic north points.

If the force model is real:
  stranding_displacement_analysis.py should show that
  displacement_deg predicts which coastal segment the
  turtle strands at, better than geomagnetic north alone.

If the force model is geographic confound:
  displacement_deg will not predict coastal segment
  better than geomagnetic north alone.
  The improvement in fit will be zero or negative.
```

---

## VERSION
```
Script:           vector_resultant_computation.py v1.0
Run date:         2026-03-22 19:57
Input:            stssn_loggerhead_working.csv
Pre-registration: exploratory — filed as amendment
                  before running (2026-03-23)
```