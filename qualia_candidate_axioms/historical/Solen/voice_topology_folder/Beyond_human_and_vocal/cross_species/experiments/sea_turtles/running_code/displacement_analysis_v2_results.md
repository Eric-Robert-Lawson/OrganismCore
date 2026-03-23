# STRANDING DISPLACEMENT ANALYSIS v2
## Force Model Test — Corrected Projection
## OC-OBS-002 — OrganismCore — Eric Robert Lawson
## Run date: 2026-03-22 20:51

---

## CORRECTIONS FROM v1

```
1. Projection direction: BACKWARD (corrected)
   v1: forward from stranding along resultant bearing
   v2: backward from stranding along RECIPROCAL
       of resultant bearing → offshore origin corridor

2. Fit metric: origin corridor clustering (corrected)
   v1: segment of projected landfall vs actual segment
   v2: within-segment clustering of offshore origin
       points — tighter = better prediction

3. Resolution: multi-resolution (corrected)
   v1: 0.45° (~50 km) only
   v2: 0.10° (~11 km) primary, 0.20°, 0.45° sensitivity
```

---

## MULTI-RESOLUTION FIT IMPROVEMENT

```
Resolution     Seg size    Geo score    Res score   Improvement
─────────────────────────────────────────────────────────────────
  10km             0.10°        3.52km       32.86km       -29.34km ← PRIMARY
  22km             0.20°        6.94km       48.59km       -41.66km
  50km             0.45°       14.93km       77.65km       -62.73km
```

---

## GEOGRAPHIC NULL MODEL
## Resolution: 10km (~11 km segments)

```
Permutations:         1000
Geo score:            3.52 km
Resultant score:      32.86 km
Real improvement:     -29.34 km
Null mean:            -236.60 km
Null SD:              0.17 km
Null 95th pctile:     -236.31 km
p (real >= null):     0.0000
Result:               SIGNIFICANT

Resultant origin clustering exceeds null.
Geographic reporting density does not explain
the improvement. Force model supported.
```

---

## FORCE MAGNITUDE CORRELATION

```
Spearman r:   0.5881
p:            0.000000
N:            57,213
Result:       SIGNIFICANT
Direction:    Predicted (positive)
```

---

## SPECIES CONTROL

```
Species             N   Mean disp°   Geo score   Res score  Improv (km)
────────────────────────────────────────────────────────────────────────
  CC           57,213       55.51°       3.52km      32.86km      -29.34km
  CM           66,891       50.69°       3.21km      28.41km      -25.21km
  DC            3,154       38.37°       3.81km      22.59km      -18.78km
```

---

## 2026 MIGRATION SEASON RISK MAP
## Top 20 coastal segments by risk score
## Migration window: April–June, August–November

```
Rank      Lat      Lon   N mig   Disp°    Opp°   Approach     Risk
─────────────────────────────────────────────────────────────────
  1     29.20   -81.00     918   91.9°   96.7°     78.2°    937.8
  2     28.40   -80.60    1030   78.1°   86.7°     92.2°    893.3
  3     29.00   -80.90     825   96.2°  104.6°     73.4°    881.7
  4     29.10   -80.90     593  120.5°  129.9°     49.6°    794.3
  5     29.30   -81.00     502  116.8°  122.1°     53.3°    651.3
  6     31.10   -81.40     515   78.8°   94.6°     90.8°    451.1
  7     30.80   -81.50     290  130.3°  137.8°     39.5°    419.7
  8     30.90   -81.40     415   87.8°  103.5°     81.9°    404.9
  9     28.30   -80.60     579   62.0°   68.8°    108.3°    398.8
  10    27.30   -80.20     377   87.0°  101.3°     83.5°    364.6
  11    30.40   -81.40     317   96.0°  103.7°     73.8°    338.2
  12    30.70   -81.50     200  151.6°  154.1°     17.2°    336.8
  13    30.30   -81.40     388   72.0°   77.7°     98.1°    310.2
  14    30.70   -81.40     267  102.9°  105.4°     66.1°    305.2
  15    28.10   -80.60     415   65.6°   73.9°    105.2°    302.3
  16    29.10   -81.00     306   87.5°   98.5°     82.6°    297.5
  17    27.20   -80.20     312   81.6°  100.2°     88.9°    283.0
  18    30.80   -81.40     229  106.7°  119.3°     63.0°    271.5
  19    31.00   -81.40     312   77.4°   92.9°     92.3°    268.3
  20    37.10   -76.00     373   61.4°   78.3°    105.9°    254.5

Approach bearing = direction FROM which turtles are
predicted to arrive at each segment.
Deploy boat/drone coverage along this bearing
offshore of each high-risk segment.
```

---

## VERSION
```
Script:    stranding_displacement_analysis_v2.py
Run date:  2026-03-22 20:51
Input:     stssn_with_resultant.csv
Status:    Exploratory — amendment filed 2026-03-23
```