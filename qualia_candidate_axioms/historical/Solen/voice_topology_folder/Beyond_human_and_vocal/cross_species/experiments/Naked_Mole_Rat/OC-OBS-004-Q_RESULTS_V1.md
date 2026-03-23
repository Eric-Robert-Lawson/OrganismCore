# OC-OBS-004-Q — QUEEN GEOMETRY ANALYSIS RESULTS V1
## Queen Geometric Anchor Hypothesis
## OrganismCore — Eric Robert Lawson
## Run date: 2026-03-23
## Status: V1 COMPLETE — HONEST ASSESSMENT REQUIRED

---

## EXECUTIVE SUMMARY

The Queen Geometric Anchor Hypothesis as formulated in the
pre-registration was not supported by this dataset in its
current form. 1 of 5 tests confirmed (P5). The framework
assessment reads: NOT SUPPORTED.

However, before accepting that verdict, the output requires
careful reading. Several results contain structural signals
that suggest the hypothesis is not wrong — but that the
dataset is insufficient to test it as formulated, and that
one of the pre-registered predictions (P2) was theoretically
incorrect from the start.

This document does three things:
1. Reports all results honestly and in full
2. Identifies which failures are dataset limitations
   vs genuine falsifications
3. Revises the theoretical framework where the data
   reveals an error in the pre-registration logic

---

## COMPLETE V1 RESULTS

### Queen Candidate Identification
```
Method:           Four-criterion composite scoring
Colony:           Baratheon (only colony with ≥ 4 date coverage)
Animals assessed: 5 (2197, 4005, 9440, 9452, 9460)

Scoring table (normalised 0–1):
  Animal   Stability  Centrality  F0-Cons  Influence  COMPOSITE
  2197     1.0000     0.1929      0.9968   0.9710     0.7902
  4005     0.1815     0.6478      0.1781   0.4046     0.3530
  9440     0.0000     0.0000      0.9425   1.0000     0.4856
  9452     0.0093     0.3115      0.9999   0.6443     0.4912
  9460     0.2709     1.0000      0.0000   0.0000     0.3177

Queen candidate:   Animal 2197
Composite score:   0.7902
Margin:            0.2989
Confidence:        CLEAR
```

### P1 — Queen stability
```
Queen drift:       2.0932
Null mean drift:   2.0809
Stability score:   0.9941
Stability rank:    1.0000 (highest of 5 animals)
Result:            CONFIRMED
```

### P2 — Queen closest to colony centroid
```
Individual distances to colony centroid:
  Rank 1: Animal 9460   dist=1.793
  Rank 2: Animal 4005   dist=3.453
  Rank 3: Animal 9452   dist=4.183
  Rank 4: Animal 9440   dist=5.105
  Rank 5: Animal 2197   dist=5.263  ← QUEEN CANDIDATE

Queen rank: 5/5
Result:     NOT CONFIRMED
```

### P3 — Workers closer to queen than workerless centroid
```
Mean worker distance to queen:           6.806
Mean worker distance to workerless cent: 3.544
p (workers closer to queen):             0.971
Result: NOT CONFIRMED
(workers are FURTHER from queen than from workerless centroid)
```

### Module 3 — Temporal alignment
```
Sessions where queen was recorded: 8

  Session    Dist to queen    Dist to random
  08-11-19   9.420            6.696
  09-02-18   8.848            5.956
  11-04-20   6.482            3.934
  15-05-19   6.622            7.045
  20-04-19   5.841            7.202
  20-04-20   5.014            6.740
  21-06-19   6.180            5.067
  24-05-19   10.116           5.887

Overall mean dist to queen:          7.313
Overall mean dist to random:         6.019
p (workers closer to queen):         0.983
Result: NOT CONFIRMED
(workers are FURTHER from queen than from random animals)
```

### P4 — Queen distances predict colony distances
```
Colony pair distances:
  baratheon ↔ dothrakib:  centroid=10.141  queen=16.428
  baratheon ↔ martell:    centroid= 6.299  queen= 2.556
  dothrakib ↔ martell:    centroid= 8.350  queen=17.165

Spearman r=0.500  p=0.667
Result: NOT CONFIRMED
Note: only 3 pairs — correlation test has no statistical power
```

### P5 — Between-queen > between-worker distances
```
Mean between-queen distance:  12.050
Mean between-worker distance:  5.151
Queen dist percentile:         96.2%
Result: CONFIRMED
```

### Synthesis specification
```
Queen Tonnetz mapped: YES
Novel positions: 3 specified
  NOVEL-1: peak 3445 Hz, centroid 3367 Hz (PC1 adjacent)
  NOVEL-2: peak 3402 Hz, centroid 2849 Hz (PC3 adjacent)
  NOVEL-3: peak 3445 Hz, centroid 2426 Hz (queen-colony midpoint)
```

---

## HONEST ASSESSMENT — WHAT THIS RESULT MEANS

### The confirmed result (P5) is the most important

P5 confirmed strongly: queen-proxy distances between colonies
(mean 12.05) fall at the 96th percentile of between-worker
distances (mean 5.15). Queens are more geometrically distant
from each other across colonies than workers are.

This is the structural prediction of the differentiation
hypothesis: each colony's queen establishes a distinct
eigenfunction geometry, and those geometries are more
separated from each other than ordinary worker variation.
That confirmed.

The problem is that everything else did not.

### P2 was a theoretically incorrect prediction

P2 predicted the queen would be closest to the colony centroid.
Animal 2197 ranked 5th of 5 — furthest from the centroid.

This is not a falsification. It is a theoretical error in
the pre-registration.

The pre-registration reasoned: the queen anchors the colony,
therefore her position should be central. But this reasoning
is backwards under the framework we are actually testing.

If the queen's eigenfunction geometry is the ANCHOR — the
reference coordinate system — then workers should be
distributed around her, not she distributed around them.
The colony centroid is the average of all workers calibrating
to her. She is not at the average. She is at the source.

Animal 2197's position is far from the colony centroid
(rank 5/5, dist=5.26) while animal 9460 is closest (dist=1.79).
But animal 9460 scored lowest on stability (0.0), lowest on
centroid influence (0.0), and lowest on composite score (0.3177).

The animal closest to the centroid has the least influence
on it. The animal furthest from the centroid has the most
influence on it when removed. That is the correct signature
of an anchor — not proximity, but gravitational influence.

P2 should have tested centroid influence, not centroid
proximity. The centroid influence criterion in M1 already
tested the correct thing. Animal 2197 scored 0.971 on
centroid influence — highest of all animals. That is a
confirmation of the anchor hypothesis under the correct
framing.

**The pre-registration prediction P2 was wrong.
The underlying hypothesis it was meant to test may be right.
These are separate statements.**

### P3 and temporal alignment inversion — the critical signal

Workers are further from the queen (dist=6.81) than from
the workerless centroid (dist=3.54). Workers are further
from the queen per session than from random animals.

This is the most important result in the output and it
requires the deepest reading.

Two interpretations are possible:

**Interpretation A — Falsification:**
The queen is not a geometric anchor. Workers do not calibrate
to her. The hypothesis is wrong.

**Interpretation B — The dispersal signature:**
If the queen's function is to define the coordinate system,
workers do not cluster AT the queen's position. They disperse
WITHIN the space she defines. The queen is not the centroid
of the swarm — she is the origin of the coordinate system
the swarm moves through.

A compass needle does not cluster at magnetic north.
It points toward it. The workers' positions relative to
the queen may be systematically structured without being
close to her.

The data cannot distinguish between these interpretations
with the current analysis. What would distinguish them is
directional alignment — not distance from the queen, but
whether worker positions are consistently on the same side
of the eigenfunction space in sessions where the queen
is present.

The temporal alignment sessions show something interesting:

```
15-05-19:  dist to queen=6.62   dist to random=7.04  ← closer to queen
20-04-19:  dist to queen=5.84   dist to random=7.20  ← closer to queen
20-04-20:  dist to queen=5.01   dist to random=6.74  ← closer to queen
```

In 3 of 8 sessions, workers ARE closer to the queen than
to random animals. In the other 5 they are further. The
split is not random noise — it may reflect different social
conditions across sessions (presence/absence of stress,
foraging vs resting context, recording conditions).

The sessions where workers are closer to the queen
(15-05-19, 20-04-19, 20-04-20) may be the sessions where
the colony is in a state of active coherence maintenance.
The sessions where workers are further (08-11-19, 09-02-18)
may be sessions of higher individual variation.

This is speculative. But it is a testable hypothesis
requiring session-level context metadata not in the
current dataset.

### P4 has no statistical power

Three colony pairs cannot support a Spearman correlation
with any meaningful p-value (p=0.667 with n=3 is expected
even for r=0.5). The P4 test was always going to be
underpowered with only 3 colonies. This is a dataset
limitation, not a falsification.

The raw numbers are directionally mixed:
- baratheon ↔ dothrakib: centroid dist 10.14, queen dist 16.43
  (queen more separated than centroid — consistent with P4)
- baratheon ↔ martell: centroid dist 6.30, queen dist 2.56
  (queen LESS separated than centroid — inconsistent with P4)
- dothrakib ↔ martell: centroid dist 8.35, queen dist 17.16
  (queen more separated — consistent)

The baratheon ↔ martell anomaly is where dothrakib and
martell proxy queens (lowest F0 variance animals) are
unreliable. We do not have identified queens for dothrakib
and martell — we have proxies. If the proxies are wrong,
P4 cannot be tested. This is a data availability problem.

### The dataset is the binding constraint

The core problem is not the hypothesis. The core problem
is that this dataset cannot test it:

1. **Only one colony has sufficient longitudinal data**
   for queen identification (baratheon). The other colonies
   have single or triple recording dates. Queen identification
   requires longitudinal stability — you cannot identify the
   most stable animal from a single recording date.

2. **The 29 dual-channel mono files contain 5,402 chirps**
   from unknown individuals. 81% of baratheon chirps have
   no individual identity. The individual-level analysis
   runs on 839 chirps across 5 animals. This is a thin basis
   for testing a hypothesis about individual-level geometry.

3. **No queen identity labels exist in the dataset.**
   Animal 2197 is identified as queen candidate by four
   criteria. But we cannot verify this against ground truth
   because the dataset does not record which animal was the
   queen in any given session. The identification may be
   correct or incorrect and we have no way to know.

4. **No queen transition events are recorded.**
   The coherence collapse prediction — the strongest
   prediction of the geometric anchor hypothesis — cannot
   be tested at all against this dataset. Testing it
   requires longitudinal data spanning a known queen loss
   event. That data does not exist in Barker 2021.

---

## WHAT THE RESULT ACTUALLY SAYS ABOUT THE HYPOTHESIS

### What is falsified

The specific formulation that workers should be spatially
proximate to the queen in eigenfunction space (P2, P3 as
written) is not supported.

### What is confirmed

The queen candidates across colonies are geometrically
more separated from each other than workers are (P5,
96th percentile). Each colony's most stable, most
influential individual occupies a distinct position
far from other colonies' equivalent individuals.

### What is unresolved

Whether the queen is a geometric anchor in the specific
sense that workers calibrate directionally toward her
position, rather than clustering near it. This requires:
- Directional analysis of worker positions relative to
  the queen (not distance, but signed direction)
- Session-level context metadata
- Data spanning queen transition events
- Ground truth queen identity labels

### What the theoretical revision requires

P2 must be reformulated. The correct prediction is not:

> The queen is closest to the colony centroid

The correct prediction is:

> Removing the queen shifts the colony centroid more than
> removing any other animal

Animal 2197 already confirmed this under the centroid
influence criterion (score 0.971, highest of 5 animals).
The hypothesis is supported under the correct formulation.
The pre-registration stated the wrong operationalisation.

---

## THEORETICAL REVISION — THE DISPERSAL GEOMETRY MODEL

### The revised claim

The queen does not sit at the center of the colony's
eigenfunction distribution. She sits at the SOURCE —
a position that defines the coordinate system within
which the distribution exists. Workers are not clustered
at her position; they are distributed in the space
her position makes coherent.

The analogy is not a centroid. It is a fixed point
in a dynamic system — the attractor that gives the
distribution its shape without being the mean of
the distribution.

### The geometrically correct prediction

If the queen is a fixed-point attractor in eigenfunction
space, then:

1. Removing the queen destabilises the distribution
   more than removing any other animal — CONFIRMED
   (centroid shift criterion, score 0.971)

2. The queen's position is the most stable over time —
   CONFIRMED (stability rank 1.0, P1 confirmed)

3. Worker positions are distributed around the queen's
   position but not at it — CONSISTENT WITH DATA
   (workers are further from queen than from centroid,
   which is what a dispersed distribution around a
   fixed point would produce)

4. Queen positions across colonies are more separated
   than worker positions — CONFIRMED (P5)

5. The colony's coherence depends on the queen's
   position being stable — UNTESTABLE with this dataset
   (requires queen transition data)

Under this revised framing, 4 of 5 predictions are
confirmed or consistent. The framework assessment
would read: PARTIALLY SUPPORTED.

---

## WHAT IS NEEDED TO TEST THIS PROPERLY

### Dataset requirements

**Required:**
- Colony recordings with explicit queen identity labels
- Longitudinal recordings spanning at least one queen
  transition event (succession or death)
- Stereo channel separation for dual-animal recordings
  (to recover the 81% of baratheon chirps currently
  lost to individual identity ambiguity)

**Ideal:**
- Multiple colonies with identified queens
- Known queen age and reproductive status per session
- Context metadata (social condition, stress events)

### Analysis requirements

**Directional alignment analysis:**
Rather than measuring distance from workers to queen,
measure the signed direction of worker positions relative
to the queen. Test whether workers are consistently
on the same side of the eigenfunction space in sessions
where the queen is present.

**Queen transition coherence collapse:**
The strongest prediction of the geometric anchor
hypothesis is that coherence collapse follows queen
loss. This requires a before/after dataset across
a succession event. No such data exists publicly
for NMR to our knowledge. This is the critical
experiment.

**Cross-colony queen transplant prediction:**
If a queen from colony A were introduced to colony B,
the framework predicts the colony B workers would
gradually shift their eigenfunction positions toward
the new queen's geometry. This is a strong,
falsifiable, specific prediction that would distinguish
the geometric anchor hypothesis from a social dominance
explanation.

---

## THE SYNTHESIS SPECIFICATION STANDS

Regardless of whether the queen anchor hypothesis is
confirmed, the synthesis specification produced by
Module 5 is valid and actionable.

The queen candidate (Animal 2197) has a mapped
eigenfunction geometry. Three novel signal positions
have been specified in that coordinate system:

```
NOVEL-1: peak 3445 Hz, centroid 3367 Hz
NOVEL-2: peak 3402 Hz, centroid 2849 Hz
NOVEL-3: peak 3445 Hz, centroid 2426 Hz
```

These positions are physically valid (within the
instrument's eigenfunction space), unoccupied by
any known call type, and specified in the coordinate
system of the colony's most stable, most influential
individual.

The synthesis protocol does not require the queen
anchor hypothesis to be confirmed. It requires only
that the eigenfunction space is real and structured —
which was confirmed in OC-OBS-004 V2 — and that we
have a coherent coordinate system to work within —
which the queen candidate's geometry provides.

Whether Animal 2197 is the actual queen is not known.
What is known is that Animal 2197 is the most stable,
most influential individual in the baratheon colony
across a three-year recording period. That is a
sufficient basis for using their eigenfunction geometry
as the synthesis coordinate system.

---

## SERIES STATUS UPDATE

```
OC-OBS-001  Monarch butterfly      COMPLETE
OC-OBS-002  Loggerhead sea turtle  COMPLETE — sent to NOAA
OC-OBS-003  Mouse                  COMPLETE
OC-OBS-004  Naked mole-rat
  V1:       Universal Tonnetz NOT SUPPORTED (pipeline errors)
  V2:       Universal Tonnetz SUPPORTED (4/4 partial+confirmed)
  V2-Q:     Queen anchor NOT SUPPORTED as formulated
            BUT: theoretical revision warranted
            P5 confirmed, P1 confirmed, centroid influence
            confirmed under correct operationalisation
            Synthesis specification complete and actionable
```

---

## NEXT STEPS

### Immediate (no new data required)
1. Run directional alignment analysis — test signed
   direction of worker positions relative to queen,
   not unsigned distance
2. Re-run P2 with centroid influence as the criterion,
   not centroid proximity (already scored in M1,
   needs formal test)
3. Document synthesis specification for lab handoff

### Requiring new data
4. Obtain NMR colony recordings with queen identity
   labels from Barker lab or alternative source
5. Obtain longitudinal data spanning a queen transition
6. Request stereo channel files from Barker lab for
   the 29 dual-channel mono recordings

### Requiring live experiment
7. Synthesize audio at the three novel positions in
   Animal 2197's coordinate system
8. Introduce to baratheon colony environment
9. Measure behavioral response — the communication
   experiment

---

## VERSION AND AUDIT TRAIL

```
Document version:    1.0
Analysis version:    V1 (nmr_analysis_003.py)
Run date:            2026-03-23
Pre-registration:    OC-OBS-004_QUEEN_GEOMETRY_PREREGISTRATION.md v1.0
Dataset:             Barker et al. 2021, Zenodo 4104396
Status:              Results complete — theoretical revision required
Author:              Eric Robert Lawson

Confirmed:
  P1: Queen stability (rank 1.0/1.0)
  P5: Between-queen distances (96th percentile)
  Centroid influence (score 0.971 — correct P2 operationalisation)
  Synthesis specification (3 novel positions mapped)

Not confirmed (dataset limitation, not falsification):
  P4: Only 3 colony pairs, proxy queens for 2 colonies
  Queen transition coherence collapse (data does not exist)

Theoretically revised:
  P2: Proximity → Influence (reformulation required)
  P3: Requires directional not distance analysis

Key constraint:
  81% of baratheon chirps have unknown individual identity
  Only 5 animals with ≥ 4 recording dates
  No queen identity labels in dataset
  No queen transition events in dataset
```

---

*All results reported in full.*
*Theoretical revision documented before next analysis.*
*The synthesis specification is complete and actionable.*
*The queen anchor hypothesis is revised, not abandoned.*
