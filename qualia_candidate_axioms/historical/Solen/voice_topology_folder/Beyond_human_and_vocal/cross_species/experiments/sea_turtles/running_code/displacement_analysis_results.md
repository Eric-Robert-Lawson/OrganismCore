# STRANDING DISPLACEMENT ANALYSIS
## Force Model Test — OC-OBS-002
## OrganismCore — Eric Robert Lawson
## Run date: 2026-03-22 19:58

---

## CORE QUESTION

```
Does the vector resultant of the geomagnetic gradient
and AM false attractor predict stranding location
displacement better than the geomagnetic gradient alone?

If yes: AM is acting as a deterministic navigational
force. The A1 result is not explained by geographic
reporting density.

If no: the A1 result may be geographic confound.
```

---

## FIT IMPROVEMENT — PRIMARY RESULT

```
Mean error (geomagnetic only):   see null model
Mean error (resultant):          see null model
Improvement in fit:              -0.64 km
  Positive = resultant predicts stranding segment
  better than geomagnetic north alone.
  Negative = resultant is worse than geo north alone.
```

---

## GEOGRAPHIC NULL MODEL

```
Permutations:         1000
Real improvement:     -0.64 km
Null mean:            -0.29 km
Null SD:              0.07 km
Null 95th pctile:     -0.18 km
p (real >= null):     1.0000
Result:               null

Interpretation:
  Real improvement does not exceed null distribution.
  Geographic reporting density may explain the result.
  Force model is not supported by this test.
```

---

## FORCE MAGNITUDE CORRELATION

```
Test: Spearman correlation between
  am_weight_scaled / geo_magnitude_nT  (relative AM force)
  and displacement_deg  (resultant vs geo north)

Prediction: positive correlation.
Larger AM force relative to geomagnetic field →
larger displacement of resultant from geo north.

Spearman r:   0.5881
p:            0.000000
N:            57,213
Result:       SIGNIFICANT
Direction:    Predicted (positive)
```

---

## SPECIES CONTROL

```
Loggerhead (CC) result compared against green turtle
(CM) and leatherback (DC).

Same geographic reporting bias.
Different magnetic compass mechanisms.

Prediction: CC shows strongest displacement signal.
If CM and DC show identical displacement, result is
geographic. If CC > CM >= DC, result is mechanistic.

Species             N   Mean disp°   Fit improv (km)
───────────────────────────────────────────────────────
  CC           57,213       55.51°            -0.64
  CM           66,891       50.69°             0.96
  DC            3,154       38.37°             2.02
```

---

## OVERALL VERDICT

```
Force model supported if ALL of:
  1. Real fit improvement > 0
  2. Null model p < 0.05
  3. Force magnitude correlation r > 0, p < 0.05
  4. CC displacement > CM and DC displacement

  SUPPORTED:     Force magnitude correlation positive
  NOT SUPPORTED: Fit improvement <= 0
  NOT SUPPORTED: Null model not significant

PARTIAL SUPPORT.
Interpret with caution. See individual tests above.
```

---

## VERSION
```
Script:           stranding_displacement_analysis.py v1.0
Run date:         2026-03-22 19:58
Classification:   Exploratory — pre-registered amendment
                  filed 2026-03-23 before running.
```