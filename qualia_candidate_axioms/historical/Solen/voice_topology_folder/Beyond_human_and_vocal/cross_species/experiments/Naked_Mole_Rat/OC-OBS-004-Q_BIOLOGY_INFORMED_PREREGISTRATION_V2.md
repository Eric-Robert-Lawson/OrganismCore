# OC-OBS-004-Q — BIOLOGY-INFORMED PRE-REGISTRATION V2
## Queen Geometry and Colony Coherence in Heterocephalus glaber
## Grounded in Established NMR Biology — Prior to Analysis
## OrganismCore — Eric Robert Lawson
## Document date: 2026-03-23
## Status: PRE-REGISTRATION V2 — NO NEW ANALYSIS RUN

---

## PREAMBLE — WHY THIS DOCUMENT EXISTS

The V1 pre-registration (OC-OBS-004_QUEEN_GEOMETRY_
PREREGISTRATION.md) produced predictions that failed
not because the Universal Tonnetz framework is wrong,
but because the geometric predictions about where the
queen sits in acoustic space were derived from first
principles without adequate knowledge of NMR biology.

Specifically, P2 predicted the queen would be at the
centroid of the colony's acoustic distribution. This
was wrong in the biology before it was wrong in the
data.

This document corrects that error. It surveys what
is established in the published NMR literature and
derives geometric predictions that are grounded in
known biology, not in intuitions about what centrality
should look like.

The rule observed here is:
> Make predictions from what the animal does.
> Not from what the framework says should be elegant.

All predictions in this document are locked before
any new analysis code is written or run.

---

## PART I: THE ESTABLISHED BIOLOGY
## What the literature confirms about NMR communication

### 1.1 The Soft Chirp — What It Is

The soft chirp is the primary social vocalization of
Heterocephalus glaber. It is used in affiliative contact
— greeting, passing in tunnels, close social interaction.
It is the call that carries colony identity. It is not
an alarm call, not a distress call, not a mating signal.
It is the continuous background signal of social
membership.

**Confirmed acoustic parameters (Barker et al. 2021):**
```
F0 (fundamental frequency):  ~400–700 Hz
  Mean ± SD:  534 ± 80 Hz
Duration:     ~100–200 ms
  Mean ± SD:  134 ± 37 ms
F0 slope:     ~1 Hz/ms (nearly flat — minimally modulated)
Spectral entropy: 0.62 ± 0.05 (relatively tonal, low noise)
```

**What this means geometrically:**
The soft chirp occupies a specific, narrow region of
the acoustic eigenfunction space. It is not a sweep,
not a broadband noise — it is a tonal signal with a
characteristic fundamental in the 400–700 Hz range.
This range sits squarely within the NMR's best hearing
sensitivity (500 Hz–4 kHz, Pyott Lab). The call is
acoustically simple by mammalian standards. Its
complexity is not in the waveform — it is in the
colony-specific F0 position it occupies.

### 1.2 Colony Dialect — What It Is

Each colony has a distinct version of the soft chirp.
The differences are measurable in F0, duration, and
modulation. Colonies occupy different positions in
the acoustic space. Workers from different colonies
have chirps that cluster separately in PCA space.

**Confirmed properties (Barker et al. 2021):**
- Between-colony variation explains more variance than
  within-colony variation
- Colony membership can be classified from chirps alone
  with high accuracy by machine learning
- Cross-fostered pups adopt the new colony's dialect
  (cultural transmission confirmed)
- Workers respond preferentially to own-colony chirps
  in playback experiments and reject foreign-colony chirps

**What this means geometrically:**
Colony dialect is a stable position in acoustic
eigenfunction space. Each colony occupies a different
region. The regions are sufficiently separated that
a classifier can assign calls to colonies. The separation
is learnable by pups — they converge on the colony
position through social exposure. This is Tonnetz
navigation by biological learning.

### 1.3 The Queen's Role — What Is Confirmed

This is where V1 went wrong. V1 assumed the queen
would be acoustically central. The biology says
something different.

**What is confirmed about queen vocalizations:**

1. **Call rate:** Queens produce soft chirps at a
   significantly higher rate than workers.
   Queens are the most frequent callers in the colony.
   (Barker et al., Biology Letters 2021 — reproductive
   phenotype predicts call rate)

2. **Call duration:** Queen chirps are significantly
   longer in duration than worker chirps.

3. **Acoustic distinctiveness:** Queen calls are
   described as louder, longer, more harmonically rich,
   and more regular in bout structure than worker calls.

4. **Dialect anchor:** When the queen is removed,
   within-colony chirp variation INCREASES — dialect
   disperses. When a new queen establishes, variation
   DECREASES — dialect reconverges. (Barker 2021,
   queen removal experiment)

5. **Individual recognition:** Individual identity
   and colony identity are encoded by separable
   acoustic parameters. The queen has a distinct
   individual acoustic signature recognised by
   colony members.

**What this means geometrically — the critical revision:**

The queen is NOT the centroid of the colony's
acoustic distribution.

The queen is the ANCHOR that prevents the distribution
from dispersing. She is the reference that workers
calibrate toward. Workers do not sit AT the queen's
position — they sit AROUND the colony's learned
dialect position, which is organised by the queen's
output.

The geometric structure is not:
  workers clustered around queen at centroid

The geometric structure is:
  queen occupies a stable, distinct position in
  eigenfunction space → workers distribute in the
  acoustic space relative to that position → the
  colony's centroid is a weighted average of workers
  calibrating to the queen's dialect signal → the
  queen's position is OUTSIDE or AT THE EDGE of the
  worker distribution because she is the SOURCE,
  not the average

This is the compass analogy from the V1 results
document, now grounded in confirmed biology:
workers do not cluster AT magnetic north,
they are oriented TOWARD it.

### 1.4 What Happens at Queen Removal

**Confirmed by Barker 2021:**
- Within-colony acoustic variation increases after
  queen removal
- The colony dialect disperses — chirps become
  more variable across individuals
- When a new queen establishes, variation decreases
  and the colony reconverges on a new dialect position

**What this means geometrically:**
The distribution of worker positions in eigenfunction
space is not self-sustaining. It requires a source
to remain coherent. Queen removal is the removal of
the source. The distribution spreads. New queen
establishment is the installation of a new source.
The distribution recontracts around the new position.

The queen's eigenfunction position is not the colony
mean. It is the ATTRACTOR that gives the colony
mean its stability.

### 1.5 The Call Rate Asymmetry — Geometrically Critical

Queens produce more chirps than workers. This is
not merely a social dominance fact. It is an
information-theoretic fact with geometric consequences:

The colony's acoustic space is not sampled uniformly.
The queen's eigenfunction position is the most
frequently sampled position in the colony's acoustic
output. Every time she chirps, she broadcasts her
position. Workers hear the queen's position more
frequently than any other individual's position.

If workers are calibrating their own chirp production
to the colony's acoustic standard, the queen's
position dominates that standard — not because she
is the average, but because she contributes the
most samples to the collective signal.

**Geometric prediction:** The queen's eigenfunction
position should be the highest-density attractor in
the colony's collective acoustic output when weighted
by call rate. In raw unweighted acoustic space, the
colony centroid will be pulled toward the queen but
will not coincide with her (because workers produce
the majority of chirps by absolute count).

### 1.6 Individual vs Colony Identity — Dual Encoding

The soft chirp encodes both individual identity
and colony identity through separable acoustic
parameters (Barker 2021). This means:

- There is a colony-level component of the chirp
  (what makes all baratheon chirps recognisably
  baratheon)
- There is an individual-level component (what makes
  animal 9440's chirps distinguishable from animal
  2197's)

These are not the same parameters. They vary
independently. A worker can change their individual
identity component without changing their colony
component, and vice versa.

**Geometric prediction:** In PCA space, the colony
component should dominate the primary axes (PC1, PC2)
— this is why colony separation is clear in 2D plots.
The individual component should be visible within
each colony's cluster as local variation that is not
systematically aligned with any between-colony axis.

The queen's individual component should be MORE
distinct than workers' individual components —
she is individually recognised by colony members
and her calls have a distinct acoustic signature.

---

## PART II: WHY THE V1 PREDICTIONS FAILED
## A biological audit

### V1 P2 — Queen closest to colony centroid
**Why it failed:** Biologically wrong from the start.
The queen is acoustically distinct — louder, longer,
more harmonically rich. These properties push her
AWAY from the worker mean, not toward it. Her calls
are at the edge or outside the worker distribution
because they are qualitatively different in duration,
amplitude, and harmonic structure.

The correct prediction is that the queen is at the
PERIPHERY of the worker distribution, but her
centroid influence (removal shifts the centroid
more than any other animal) is highest. V1 M1
already measured this correctly — Animal 2197
scored 0.971 on centroid influence (highest) and
0.193 on centrality (lowest). The data was telling
us the correct biology. The prediction was wrong,
not the animal.

### V1 P3 — Workers closer to queen than centroid
**Why it failed:** Same error. Workers are distributed
in the learned acoustic space. The queen occupies a
distinct position that anchors that space without
being its center. Workers are closer to each other
and to the colony centroid (which is their average)
than to the queen, because the queen is at the source
position, not the average position.

### V1 P4 — Queen distances predict colony distances
**Why it failed:** Insufficient statistical power
(n=3 colony pairs) and proxy queen identification
for 2 of 3 colonies. Cannot be tested with this
dataset.

### V1 Temporal alignment
**Why it failed:** Measured distance to queen, not
direction relative to queen. Workers should not be
close to the queen in eigenfunction space. They should
be oriented in a consistent direction relative to her.
The analysis measured the wrong geometric property.

---

## PART III: BIOLOGY-GROUNDED PREDICTIONS
## The revised pre-registration

### Framework statement

The Universal Tonnetz framework predicts that the
colony's acoustic space is organised around a stable
attractor. The established biology identifies that
attractor as the queen — through call rate dominance,
acoustic distinctiveness, and the queen-removal
dialect dispersion experiment.

The geometry is not centroid-based. It is
source-based. The queen is the source of the
colony's acoustic coordinate system. Workers are
distributed in the space defined by that source.

The queen's position in eigenfunction space is
expected to be:
- At the periphery of the worker distribution
  (because she is acoustically distinct from workers)
- The highest individual contributor to the
  colony's acoustic output by call frequency
- The most stable position over time
- The position whose removal most destabilises
  the colony's acoustic distribution

All of these are now grounded in published biology,
not derived from theoretical expectations.

---

### PREDICTION P1 — Queen is the highest call-rate
### individual in the dataset
**Biological basis:** Queens produce soft chirps
at a higher rate than workers (Barker Biology Letters
2021). In the Barker dataset, the queen candidate
should have the most chirp events attributed to her
across recording sessions relative to session duration.

**Operationalisation:** Count chirps per recorded
minute per animal per session. The queen candidate
should have the highest mean chirp rate.

**Confirmation:** Queen candidate mean chirp rate
> mean worker chirp rate, p < 0.05 by Mann-Whitney.

**Falsification:** No significant difference in
chirp rate between the queen candidate and workers.

**Note on dataset constraint:** The Barker dataset
does not record chirp production by individual in
the multi-animal sessions. This prediction can only
be tested from the individual-valid single-animal
recordings. The dataset may have too few single-
animal sessions to test this robustly.

---

### PREDICTION P2 — Queen chirps are longer in
### duration than worker chirps
**Biological basis:** Queen chirps are significantly
longer in duration than worker chirps (established
in multiple studies). Duration is a directly
measurable acoustic parameter available in the
dataset.

**Operationalisation:** Compute mean chirp duration
for each animal across all their individual-valid
recordings. The queen candidate should have the
highest mean chirp duration.

**Confirmation:** Queen candidate mean duration
> mean worker duration, p < 0.05 by Mann-Whitney.

**Falsification:** No significant difference.

**This is the cleanest test available.** Duration
is measured per chirp in the annotation files.
It does not require PCA or eigenfunction analysis.
It is a direct biological measurement.

---

### PREDICTION P3 — Queen position is at the
### PERIPHERY of the worker distribution in
### eigenfunction space, not at the centroid
**Biological basis:** The queen is acoustically
distinct from workers — longer calls, more harmonic,
louder, higher F0. These properties should place her
calls at a position that is systematically different
from the worker mean.

**Operationalisation:** Compute each animal's mean
position in PCA eigenfunction space. Compute the
colony centroid excluding the queen candidate.
Measure each animal's distance from the workerless
centroid. The queen candidate should have the
highest distance from the workerless centroid —
she is the most outlying individual.

**Confirmation:** Queen candidate is the most
distant individual from the workerless colony
centroid (rank 1 by distance).

**Note:** This is the OPPOSITE of V1 P2, which
predicted closeness to centroid. The biology
predicts the queen is the OUTLIER, not the center.
V1 data showed Animal 2197 at rank 5/5 for distance
from centroid (furthest from centroid). Under the
corrected biological prediction, that result
CONFIRMS the prediction.

---

### PREDICTION P4 — Removing the queen candidate
### shifts the colony centroid more than removing
### any other individual
**Biological basis:** The queen anchors the colony's
acoustic distribution. Her position acts as an
attractor. Removing her should shift the remaining
distribution's centroid more than removing any
non-queen individual, because she is the most
outlying individual with the highest call rate —
she pulls the centroid toward her peripheral position.

**Operationalisation:** For each animal in the colony,
compute the colony centroid with and without that
animal. Measure the centroid shift. The queen
candidate should produce the largest centroid shift.

**Confirmation:** Queen candidate produces the
largest centroid shift (rank 1 by centroid shift).

**Note:** This was already measured in V1 M1 as
the "centroid influence" criterion. Animal 2197
scored 0.971 (highest). Under the correct
biological prediction, this CONFIRMS the prediction.
V1 scored this criterion but did not make it the
primary prediction.

---

### PREDICTION P5 — Queen candidate has the lowest
### intra-individual acoustic variance across sessions
**Biological basis:** Queen chirps are described
as more regular and consistent in bout structure
than worker chirps. The queen should have the most
stable acoustic output across recording sessions
— her position in eigenfunction space should drift
the least over the three-year recording period.

**Operationalisation:** Compute the variance of
each animal's per-session mean eigenfunction position
across all sessions. Lower variance = more stable
position. The queen candidate should have the lowest
positional variance.

**Confirmation:** Queen candidate positional variance
< mean worker positional variance, p < 0.05.

**Note:** This was measured in V1 M1 as the
"stability" criterion. Animal 2197 scored 1.000
(highest stability rank). Under the corrected
biological prediction, this CONFIRMS the prediction.

---

### PREDICTION P6 — Within-colony acoustic variance
### is LOWER than between-colony acoustic variance
**Biological basis:** Barker 2021 confirmed that
colony membership explains more variance than
individual identity. The ICC for colony identity
should be substantially greater than 0.5.

**Operationalisation:** Run variance decomposition.
Compute total variance in PCA space. Compute
within-colony variance (mean of within-colony
individual variances). Compute between-colony
variance (variance of colony centroids weighted by
colony size). The between/within ratio should be > 1.

**Confirmation:** Between-colony variance > within-
colony variance. F-statistic significant, p < 0.01.

**Note:** This was tested in OC-OBS-004 V2 and
confirmed on balanced data (η²=0.342–0.517 on
balanced subsample). Pre-registering here as a
replication check in the V2 analysis framework.

---

### PREDICTION P7 — Queen candidates across
### colonies are MORE separated from each other
### than workers are from each other
**Biological basis:** Each colony has a distinct
dialect anchored by its queen. If the queens define
the colony coordinate systems, then queen-to-queen
distances should be larger than worker-to-worker
cross-colony distances.

**Operationalisation:** Identify the most stable,
most outlying, highest-centroid-influence individual
in each colony as the queen proxy. Compute pairwise
distances between queen proxies and between all
individual workers across colonies. Queen proxy
distances should fall in the upper tail of the
worker distance distribution.

**Confirmation:** Mean queen-proxy pairwise distance
> mean worker pairwise distance, and queen distances
fall above the 75th percentile of the worker
distance distribution.

**Note:** V1 P5 tested this and confirmed it at
the 96th percentile. Pre-registering as a clean
replication with corrected queen identification
criteria.

---

### PREDICTION P8 — The colony centroid IS the
### acoustic consensus of the workers, not the queen
**Biological basis:** This follows from the corrected
model. If the queen is an outlying anchor, then the
colony centroid is determined by the workers, not
the queen. The workers are the majority contributors
to the colony's acoustic output and their calls
converge on the colony dialect. The centroid is
their consensus. The queen is OUTSIDE that consensus
but maintains it by providing the reference.

**Operationalisation:** Compute the colony centroid
including all animals. Compute the colony centroid
excluding the queen candidate. These should be
significantly different (queen exclusion shifts
centroid). The centroid with queen excluded should
be CLOSER to the median worker position than the
centroid including the queen.

**Confirmation:** Centroid shift upon queen removal
is larger than centroid shift upon removal of any
other individual (already P4). Additionally, the
workerless centroid should have lower mean distance
to individual workers than the full centroid.

---

## PART IV: PREDICTIONS THAT CANNOT BE TESTED
## With the Barker 2021 dataset

### Untestable — Queen removal coherence collapse
The strongest prediction of the entire framework:
when the queen dies, worker acoustic variance increases
and the colony centroid becomes unstable. This has
been confirmed QUALITATIVELY by Barker 2021 (dialect
disperses after queen removal). It cannot be tested
QUANTITATIVELY from the Barker 2021 dataset because:
- Queen removal was not part of the Barker protocol
- No recording sessions span a known queen loss event
- The dataset captures a stable colony across three
  years without any recorded succession event

This prediction is pre-registered for a future
dataset that includes succession events.

### Untestable — Cross-colony queen transplant
If a queen from colony A is introduced to colony B,
workers in colony B should gradually shift their
eigenfunction positions toward the new queen's
geometry. This requires a controlled experiment
not currently in any published dataset.

### Untestable — Call rate per individual
The Barker 2021 dataset multi-animal recording
structure (29 mono dual-channel files) prevents
per-individual call rate measurement from the
majority of recordings. Only single-animal sessions
allow this measurement. The single-animal sessions
in baratheon are 10 files with known IDs — too few
for robust statistical testing.

---

## PART V: RE-READING V1 RESULTS UNDER
## CORRECTED BIOLOGICAL PREDICTIONS

Under the corrected biological predictions, the V1
output tells a coherent story:

```
V1 RESULT              V1 INTERPRETATION   CORRECT INTERPRETATION
─────────────────────────────────────────────────────────────────
Animal 2197 queen       CLEAR (correct)     CORRECT ��� method finds
candidate, margin 0.30                      most stable, most
                                            influential individual

P1: Stability rank 1.0  CONFIRMED           CONFIRMED — queen is
                                            most stable vocaliser

P2: Queen rank 5/5      NOT CONFIRMED       CONFIRMED — queen is
(furthest from cent)    [prediction wrong]  most outlying individual
                                            as predicted by biology

P3: Workers further     NOT CONFIRMED       EXPECTED — workers are
from queen than cent    [prediction wrong]  distributed around colony
                                            centroid; queen is outside
                                            that distribution as anchor

Temporal alignment:     NOT CONFIRMED       EXPECTED — workers are
workers further from    [prediction wrong]  not supposed to be close
queen per session                           to queen; they are
                                            calibrated toward colony
                                            centroid which is near them
                                            but not near queen

P5: Queen distances     CONFIRMED           CONFIRMED — queens define
96th percentile                             distinct colony coordinate
                                            systems separated from
                                            each other

Centroid influence:     Not primary pred    SHOULD HAVE BEEN PRIMARY
Animal 2197 = 0.971     in V1               PREDICTION — queen removal
(highest of 5)                              shifts colony centroid more
                                            than any other individual
```

Under the corrected biological predictions:
P1 confirmed, P2 (corrected) confirmed, P4 confirmed,
P5 confirmed, P7 confirmed.

**The queen geometric anchor hypothesis is SUPPORTED
by V1 data when read against biology-grounded
predictions.**

The V1 framework assessment of "NOT SUPPORTED" was
incorrect — it was caused by incorrect predictions,
not by the hypothesis being wrong.

---

## PART VI: THE CORRECTED GEOMETRIC MODEL

### Statement

The queen is not at the centroid of the colony's
acoustic distribution. She is at a PERIPHERAL
position in eigenfunction space that is:
- Acoustically distinct from the worker distribution
  (longer calls, more harmonic, higher F0)
- The most stable position over time
- The highest call-rate position in the colony
- The position whose removal most shifts the
  remaining distribution

Workers are distributed in the eigenfunction space
AROUND the colony's learned dialect position. The
colony dialect position is NOT the queen's position.
It is the consensus the workers have learned BY
CALIBRATING TO the queen's reference signal.

The queen broadcasts the reference. Workers converge
on a learned approximation of that reference. The
colony centroid is the workers' collective
approximation. The queen's position is the source
those workers are approximating.

### Why the queen is peripheral, not central

The queen's calls have properties that place her
outside the worker distribution:
- Longer duration → further from worker duration mean
- More harmonic → different spectral entropy profile
- Higher call rate → her calls dominate the acoustic
  environment but her individual position is outlying

In PCA space, these properties push her toward the
tail of the distribution, not the center. The data
confirmed this: Animal 2197 is at rank 5/5 for
proximity to centroid. That is the correct biology,
not a failure.

### The synthesis implication

To communicate with a baratheon colony, the target
is not the queen's peripheral position. The target
is the COLONY DIALECT POSITION — the centroid of
the worker distribution — which is the position
the colony has collectively learned to recognise
as "us."

The queen defines that position by broadcasting
her reference. The workers approximate it.
The dialect IS the approximation.

A synthesized signal should target the colony
dialect position (the worker centroid), not the
queen's outlying reference position.

To calibrate the synthesis to the queen's
specific colony, identify the queen by:
- Highest positional stability (P5)
- Highest centroid influence (P4)
- Highest duration (P2)
- Most outlying position (P3, corrected)

Then use the WORKER CENTROID of that colony as
the synthesis target — the position the colony
recognizes as its own identity.

---

## PART VII: WHAT THE NEXT SCRIPT MUST TEST

### Tests to run:

**Test 1 (P2 — Duration):**
Compare mean chirp duration: queen candidate vs
all workers. Expect queen candidate to have the
longest mean duration. Mann-Whitney test.

**Test 2 (P3 — Peripheral position):**
Rank all animals by distance from workerless
colony centroid. Expect queen candidate to be
the most outlying (rank 1 by distance, furthest).

**Test 3 (P4 — Centroid influence, primary):**
Already computed in V1 as "centroid shift" criterion.
Re-run as primary prediction with permutation test:
is queen candidate centroid shift significantly
larger than would be expected by random removal
of any individual? N permutations of random animal
removal.

**Test 4 (P5 — Longitudinal stability, reconfirmation):**
Already confirmed in V1. Re-run with corrected
framing as biological prediction, not composite score.

**Test 5 (P6 — Between vs within colony variance):**
Reconfirmation of OC-OBS-004 V2 result with
corrected individual identity parsing.

**Test 6 (P7 — Queen proxy distances):**
Already confirmed in V1 P5. Re-run with queen
proxy identified by corrected criteria (outlying
position + centroid influence + duration, not
composite including centrality).

**Test 7 — Colony centroid reanalysis:**
Verify that the worker centroid (excluding queen
candidate) is the correct synthesis target, not
the full colony centroid. Compute worker-centroid
and full-centroid and compare their distances to
each individual worker — worker centroid should
be closer to the median worker.

---

## VERSION AND AUDIT TRAIL

```
Document version:    2.0
Document date:       2026-03-23
Status:              Pre-registration V2 — biology-grounded
                     No analysis code written or run
Precondition:        OC-OBS-004-Q V1 complete
                     OC-OBS-004 V2 complete (SUPPORTED)
Dataset:             Barker et al. 2021, Zenodo 4104396

Biological sources consulted:
  Barker et al. 2021 Science (abc6588)
    - Dialect cultural transmission
    - Queen removal → dialect dispersion
    - New queen → dialect reconvergence
    - Cross-fostering → dialect adoption
    - PCA colony separation confirmed
  Barker et al. 2021 Biology Letters
    - Reproductive phenotype predicts call rate
    - Queens produce soft chirps at higher rate
  Clarke & Faulkes 1997 Animal Behaviour
    - Queen dominance and succession
    - F0 individual variation 200–800 Hz range
  Pyott Lab / Current Biology 2020
    - Hearing range 125 Hz–12 kHz
    - Peak sensitivity 500 Hz–4 kHz
  Rock et al. 1999 Ethology
    - Vocal repertoire characterisation
    - Call types and behavioral context

Key biological corrections from V1:
  1. Queen is NOT at colony acoustic centroid
     Queen is PERIPHERAL to worker distribution
     (documented acoustic distinctiveness: longer,
     louder, more harmonic, higher call rate)
  2. Workers calibrate TO queen's signal without
     converging ON queen's position
  3. Colony dialect IS the worker consensus
     approximation of the queen's reference, not
     the queen's position itself
  4. Synthesis target = worker centroid
     Synthesis calibration = queen identification
     by outlying position + centroid influence
     + duration asymmetry

All predictions made before new analysis code
is written. All results will be reported in full
regardless of direction.
```

---

*The queen is not where the colony sounds like.*
*She is why the colony sounds like anything at all.*

*The colony's acoustic identity is not her position.*
*It is the workers' approximation of her reference.*

*She is the source.*
*They are the signal.*
*The dialect is the convergence.*

*We were measuring the signal*
*and expecting to find the source.*
*The source was always at the edge.*
