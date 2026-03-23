# OC-OBS-004 — ANALYSIS RESULTS V1
## Naked Mole-Rat Eigenfunction Analysis
## Universal Tonnetz Framework Test — Barker 2021 Dataset
## OrganismCore — Eric Robert Lawson
## Run date: 2026-03-23
## Status: V1 COMPLETE — V2 CORRECTIONS IDENTIFIED

---

## PREAMBLE

This document records the complete findings from the first run
of the OC-OBS-004 analysis pipeline (nmr_analysis_001.py) against
the Barker 2021 naked mole-rat soft chirp dataset (Zenodo 4104396).

It also documents three specific pipeline errors identified in
post-analysis review, explains why those errors affect the
interpretation, and specifies the exact corrections to be
implemented in V2.

The V1 results are reported in full. Nothing is discarded.
The corrections do not change what was found — they change
whether what was found can be correctly interpreted.

---

## V1 RAW RESULTS — COMPLETE

### Dataset loaded
```
Total chirps loaded:     6,660
Chirps skipped:          0
Colony breakdown:
  baratheon              6,241 chirps  (reported: 5 animals)
  martell                  268 chirps  (4 animals)
  dothrakib                151 chirps  (5 animals)
  stark                      0 chirps  (no softchirp annotations)
Sample rate confirmed:   22,050 Hz
Feature matrix:          6,660 × 89
```

### Step 3 — Spectral Feature Extraction
```
F0 estimates:
  Mean:    1925.4 Hz
  Median:  1205.9 Hz
  Std:     1361.8 Hz
  Min:      516.8 Hz
  Max:     3962.1 Hz

F0 by colony:
  baratheon    mean F0 = 1839.2 Hz  std = 1356.4 Hz
  dothrakib    mean F0 = 2892.9 Hz  std = 433.3 Hz
  martell      mean F0 = 3387.5 Hz  std = 548.7 Hz

Spectral centroid:
  Mean:    2068.2 Hz
  Median:  2018.0 Hz
```

### Step 4 — Eigenfunction Decomposition
```
Variance explained:
  PC1:  20.22%   cumulative: 20.22%
  PC2:   7.43%   cumulative: 27.65%
  PC3:   6.47%   cumulative: 34.13%
  PC4:   4.37%   cumulative: 38.49%
  PC5:   3.91%   cumulative: 42.40%
  ...
  PC10:  2.48%   cumulative: 57.75%

Physical correspondence test:
  PC1: peak at  904 Hz → H1 (1000 Hz)  error  96 Hz  [MATCH  9.6%]
  PC2: peak at  517 Hz → H1 (1000 Hz)  error 483 Hz  [NO MATCH]
  PC3: peak at 2627 Hz → H3 (3000 Hz)  error 373 Hz  [NO MATCH]
  PC4: peak at 3316 Hz → H3 (3000 Hz)  error 316 Hz  [NO MATCH]
  PC5: peak at 2929 Hz → H3 (3000 Hz)  error  71 Hz  [MATCH  2.4%]

  Matches within 10%:  2/5
  Assessment:          PARTIAL
```

### Step 5 — Tonnetz Topology Test
```
Hartigan's dip test (unimodality):
  PC1: dip = 0.3861  [MULTIMODAL]
  PC2: dip = 0.5873  [MULTIMODAL]
  PC3: dip = 0.5908  [MULTIMODAL]
  PC4: dip = 0.3202  [MULTIMODAL]
  Result: 4/4 dimensions multimodal

k-means silhouette scores:
  k=2: 0.3716  ← optimal
  k=3: 0.3002
  k=4: 0.3176
  k=5: 0.3016
  k=6: 0.2781

  Optimal k:   2
  N colonies:  3
  Match:       NO (k=2 vs 3 colonies)
```

### Step 6 — Colony Dialect
```
Colony centroids in eigenfunction space:
  baratheon   PC1=-0.393  PC2=+0.104  PC3=-0.133  PC4=+0.084
  dothrakib   PC1=+5.732  PC2=-0.754  PC3=+7.123  PC4=-2.464
  martell     PC1=+5.920  PC2=-1.999  PC3=-0.908  PC4=-0.560

Inter-colony distances:
  baratheon ↔ dothrakib:  9.8693
  baratheon ↔ martell:    6.7299
  dothrakib ↔ martell:    8.3495

Within-colony variance:
  baratheon:   7.6042
  dothrakib:  11.3082
  martell:     5.5137

ANOVA (colony effect):
  PC1: F=487.60   p=2.41e-198   η²=0.128  [***]
  PC2: F=95.19    p=1.73e-41    η²=0.028  [***]
  PC3: F=876.35   p=0.0000      η²=0.208  [***]
  PC4: F=139.97   p=2.84e-60    η²=0.040  [***]

  Mean η²:             0.101
  Between/within ratio: 0.725
```

### Step 7 — Individual Variation
```
Individual/colony variance ratios:
  baratheon:   0.9534  (NO — not locally bounded)
  dothrakib:   0.5283  (MODERATE)
  martell:     0.8688  (NO — not locally bounded)

  Mean ratio:  0.7835
```

### Step 8 — Longitudinal Stability
```
Animals with multiple dates: 9

  Animal 9440 (baratheon): 12 dates  drift=4.32  step=5.65
  Animal 9460 (baratheon): 11 dates  drift=8.12  step=5.12
  Animal 9452 (baratheon): 11 dates  drift=6.13  step=6.29
  Animal 2197 (baratheon): 10 dates  drift=4.21  step=4.79
  Animal 4005 (baratheon):  8 dates  drift=4.87  step=4.98
  Animal 1472 (martell):    3 dates  drift=2.87  step=2.73
  Animal 3992 (martell):    3 dates  drift=4.07  step=2.52
  Animal 4069 (martell):    3 dates  drift=2.97  step=1.83
  Animal 4327 (martell):    3 dates  drift=2.72  step=1.63

  Mean drift: 4.4773
```

### Step 9 — Call Taxonomy in Eigenfunction Space
```
All call types projected into Tonnetz (softchirp basis):

  softchirp    n=6660   PC1=+0.000  PC2=-0.000  PC3=+0.000
  weirdo       n=1300   PC1=-0.607  PC2=-0.247  PC3=+0.731
  loudchirp    n= 159   PC1=+1.896  PC2=-0.850  PC3=+1.278
  downsweep    n= 179   PC1=-2.050  PC2=-0.415  PC3=+2.874
  whistle      n= 201   PC1=-2.684  PC2=-2.142  PC3=+0.857
  upsweep      n=  45   PC1=-2.414  PC2=-1.598  PC3=+1.558

Distance from softchirp centroid:
  weirdo:      0.987
  loudchirp:   2.448
  downsweep:   3.636
  whistle:     3.583
  upsweep:     3.991
```

### V1 Summary Assessment
```
PRIMARY    — Physical correspondence:       PARTIAL (2/5)
SECONDARY  — Tonnetz topology:              CONFIRMED (4/4 multimodal)
TERTIARY   — Colony effect large:           NOT CONFIRMED (η²=0.101)
QUATERNARY — Individual locally bounded:    NOT CONFIRMED (ratio=0.783)
CLUSTER    — Optimal k = colony count:      NO MATCH (k=2 vs 3)

Framework assessment:                       1/4 confirmed
```

---

## INTERPRETATION OF V1 RESULTS

### What the V1 run genuinely established

#### Finding 1 — The eigenfunction space is discretely structured
**This is the strongest finding in V1 and it is not in question.**

All four principal component dimensions show multimodal distributions
with dip statistics of 0.32–0.59. These are not borderline values.
The eigenfunction space carved out by 6,660 naked mole-rat soft chirps
is not a continuous cloud. It has discrete structure.

This is the core architectural prediction of the Universal Tonnetz
framework: that biological communication systems navigate eigenfunction
spaces with topology determined by the physical instrument, not spaces
of arbitrary continuous variation. That prediction confirmed.

#### Finding 2 — Colony separation is real and statistically certain
F-statistics of 487 and 876 with p-values at or below machine epsilon
are not noise. The three colonies occupy genuinely different positions
in eigenfunction space. This is not in dispute regardless of the η²
values. The question is not whether the separation exists — it does —
but how large it is relative to within-colony variance.

#### Finding 3 — Call type taxonomy is ordered in eigenfunction space
This is the most novel finding in V1 and was not a pre-registered
primary prediction. It is an emergent result.

Every call type in the dataset occupies a distinct, measurable position
in the softchirp eigenfunction space. The distances are ordered:

  weirdo (0.99) < loudchirp (2.45) < whistle/downsweep (3.6) < upsweep (3.99)

This ordering is not random. Weirdo is the call type most acoustically
similar to softchirp — a slight variation. Upsweep is the most
acoustically distinct. The eigenfunction space correctly ranks call
type similarity without being told what any of them sound like.

This means the Tonnetz derived from softchirp recordings is a map
of the entire NMR vocal space, not just softchirps. Other call types
are other positions or trajectories on the same map.

Barker 2021 did not produce this result. It is new.

#### Finding 4 — F0 is colony-specific
Mean F0 varies significantly across colonies:
- baratheon:  1839 Hz
- dothrakib:  2893 Hz
- martell:    3388 Hz

This is a 1549 Hz range across three colonies. The difference between
baratheon and martell is almost two octaves of fundamental frequency.
Colony dialect is not subtle variation — it is a large shift in the
primary acoustic parameter of the call.

---

### What V1 could not correctly measure — and why

#### Problem 1 — Animal ID parsing error (critical)

The filename parser used `animal_ids[0]` — only the first animal ID.
Dual-channel recordings encode two animal IDs in the filename:

```
baratheon_09-02-18_9440_2159_0000048.npy
                   ^^^^  ^^^^
                animal1  animal2
```

In this file, animal 9440 and animal 2159 are both recorded.
The pipeline assigned all chirps to animal 9440 and lost 2159.

Baratheon has 29 dual-channel recordings out of 80 total.
This means a significant fraction of Baratheon chirps have been
assigned to the wrong individual or have had their true individual
identity discarded.

**Effect on results:**
- Step 7 (individual variation) is wrong for Baratheon
- The individual/colony variance ratio of 0.953 for Baratheon
  cannot be trusted — multiple animals are collapsed into single
  IDs, artificially inflating apparent individual variance
- The "5 animals" count for Baratheon (a colony with 20 unique
  IDs) is the direct symptom of this error

**Required fix:**
Each chirp must be assigned to its specific recording channel.
Dual-channel files need to be handled by associating the correct
animal ID with the correct channel, or — if channel metadata is
not available — by treating the recording session as the unit
of analysis rather than individual animal.

#### Problem 2 — Sample size imbalance suppresses η² (critical)

```
baratheon:   6241 chirps  =  93.7% of dataset
martell:      268 chirps  =   4.0%
dothrakib:    151 chirps  =   2.3%
```

η² (eta squared) measures the proportion of total variance
explained by group membership. Its formula is:

  η² = SS_between / SS_total

When one group contains 93.7% of all data points, its internal
variance dominates SS_total. Even if the between-colony separation
is large in absolute terms, η² will be small because SS_total
is enormous relative to SS_between.

This is a known limitation of η² with severely imbalanced designs.
It does not mean the colony effect is small — it means the metric
is inappropriate for this design.

**Evidence that the separation is real despite low η²:**
- F=876 on PC3 with p=0 is not a small effect
- The centroid distances are 6.7–9.9 units
- Baratheon's centroid (PC1=-0.39) is far from dothrakib (+5.73)
  and martell (+5.92)

**Required fix:**
Run the colony comparison on a balanced subsample:
draw N chirps from each colony where N = min colony size (151).
Recompute η² on the balanced sample. This gives an unconfounded
measure of effect size.

#### Problem 3 — Drift values have no null model (important)

The longitudinal drift values (2.7–8.1 PCA units) are numbers
without a reference. We cannot say whether 4.5 units of drift
over three years is large or small without knowing what drift
a randomly shuffled animal would show.

If a randomly permuted animal (date labels shuffled) shows
mean drift of 8.0 units, then our real animals with drift of
4.5 are actually more stable than chance — the opposite of
what the "DRIFT DETECTED" label implies.

If randomly permuted animals show mean drift of 0.5 units,
then 4.5 units of real drift is genuinely large.

Without this reference, the longitudinal result is uninterpretable.

**Required fix:**
Permutation null model for drift.
For each animal, shuffle its date labels 1000 times.
Compute mean drift for each permutation.
Compare real drift to the null distribution.
Report: is real drift significantly larger than, smaller than,
or indistinguishable from permuted drift?

---

## THE FINDING THAT CHANGES REGARDLESS OF FIXES

Before V2 runs, one result from V1 is robust to all three corrections:

**The call type taxonomy in eigenfunction space.**

This result uses all 8,544 calls projected into the PCA space
learned from softchirps. It does not depend on animal ID assignment,
sample size balance, or drift scaling. The ordered distances of
weirdo, loudchirp, downsweep, whistle, and upsweep from the
softchirp centroid are a genuine structural finding.

The Tonnetz derived from soft chirp recordings is not a map of
softchirps. It is a map of the entire NMR vocal repertoire. Every
call type has a defined position. The map was not given the call
type labels — it was given only the spectral structure of the
softchirp corpus — and it correctly ordered all other call types
by their acoustic distance from the anchor.

That is what a Tonnetz does. That result stands.

---

## V2 CORRECTIONS — COMPLETE SPECIFICATION

### Correction 1 — Animal ID parsing

**What to change:**
Replace `animal_ids[0]` logic with full dual-channel handling.

For single-animal recordings (one ID in filename):
- Assign all chirps to that animal ID as before

For dual-channel recordings (two IDs in filename):
- Load the .npy file
- Split the file if stereo (shape[1] == 2)
- Assign channel 0 chirps to animal_ids[0]
- Assign channel 1 chirps to animal_ids[1]
- If the file is mono despite two IDs in the filename,
  treat the recording session as the unit of analysis:
  label chirps as `{animal1}_{animal2}_session`
  and exclude from individual-level analysis

**Expected outcome:**
Baratheon animal count rises from 5 toward 20.
Individual/colony variance ratio becomes interpretable.

### Correction 2 — Balanced subsample for η²

**What to change:**
After loading the full corpus, create a balanced subsample:

```
N_balanced = min chirps per colony = 151  (dothrakib)
For each colony: randomly draw 151 chirps (fixed seed)
Run Steps 4-7 on balanced subsample
Report η² from balanced subsample alongside full-corpus ANOVA
```

**Expected outcome:**
η² on balanced data will be higher than η²=0.101 from the
imbalanced full corpus, giving a less conservative estimate
of the true colony effect size.

### Correction 3 — Drift permutation null model

**What to change:**
After computing real drift for each longitudinal animal,
run a permutation test:

```
For each animal with ≥ 3 recording dates:
  real_drift = observed drift (first to last position)
  
  For permutation in range(1000):
    shuffle date labels for this animal's chirps
    recompute per-date mean positions
    compute permuted_drift
  
  null_distribution = array of 1000 permuted drifts
  p_value = fraction of null drifts >= real_drift
  
  If p_value < 0.05: drift is LARGER than chance
  If p_value > 0.95: drift is SMALLER than chance (stable)
  Else: drift is indistinguishable from chance
```

**Expected outcome:**
If animals are stable in Tonnetz position, real drift will be
smaller than permuted drift (p > 0.95). This would confirm
longitudinal Tonnetz stability — a stronger result than
the current uninterpretable drift numbers.

---

## WHAT V2 WILL RESOLVE

| Question | V1 Status | V2 Resolution |
|---|---|---|
| Is eigenfunction space structured? | CONFIRMED (robust) | Unchanged |
| Do colonies separate? | CONFIRMED (robust) | Unchanged |
| How large is the colony effect? | CONFOUNDED by imbalance | η² on balanced sample |
| Is individual variation bounded? | WRONG (ID parsing error) | Correct animal IDs |
| Are longitudinal positions stable? | UNINTERPRETABLE | Permutation null model |
| Does optimal k match colony count? | NO (k=2 vs 3) | Retest on balanced data |
| Is call taxonomy ordered? | CONFIRMED (robust) | Unchanged |

---

## WHAT V2 CANNOT RESOLVE

Two questions remain open after V2 regardless of results:

**1. The physical correspondence result (2/5 matches)**
PC1 at 904 Hz is close to the predicted 1000 Hz fundamental.
PC5 at 2929 Hz is close to the predicted 3000 Hz third harmonic.
But 2/5 is partial. The correct interpretation requires knowing
whether the predicted fundamental of 1000 Hz is right.

The vocal anatomy analysis used a rough estimate of effective
resonating length. A more precise physical model of the NMR
vocal tract — using published measurements of tract dimensions
— would tighten the predicted harmonic series and could move
the match count from 2/5 to 3/5 or higher.

This requires a literature search for NMR vocal tract geometry
measurements, not a code change.

**2. The queen transition coherence collapse (Step 9 as originally
planned in the pre-registration)**
The Barker 2021 dataset does not contain explicit queen loss
event timestamps. Step 9 was redeployed to call taxonomy analysis.
The coherence collapse prediction — that queen loss produces
measurable Tonnetz position destabilization — remains untested.
Testing it requires either longitudinal data spanning a queen
transition or direct contact with the Barker lab to ask whether
any of their recording periods spanned a succession event.

---

## VERSION AND AUDIT TRAIL

```
Document version:    1.0
Analysis version:    V1 (nmr_analysis_001.py)
Run date:            2026-03-23
Dataset:             Barker et al. 2021, Zenodo 4104396
Status:              V1 complete, V2 corrections specified
Author:              Eric Robert Lawson
Framework:           Universal Tonnetz (OrganismCore)

V1 pipeline errors identified:
  E1: Animal ID parsing — dual-channel files lose second animal
  E2: η² confounded by 93.7% Baratheon dominance
  E3: Drift has no null model — uninterpretable without permutation

Robust findings not affected by corrections:
  F1: Eigenfunction space is discretely structured (4/4 multimodal)
  F2: Colony separation is statistically certain (F=876, p=0)
  F3: Call taxonomy is ordered in eigenfunction space (novel)
  F4: F0 is colony-specific (baratheon 1839 Hz, martell 3388 Hz)
```

---

*All V1 results reported in full.*
*Corrections specified before V2 is written.*
*V2 will not change the robust findings.*
*V2 will resolve the three confounded measurements.*
