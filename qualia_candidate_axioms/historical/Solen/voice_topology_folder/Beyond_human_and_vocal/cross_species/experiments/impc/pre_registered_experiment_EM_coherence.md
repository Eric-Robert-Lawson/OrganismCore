# PRE-REGISTERED EXPERIMENT
# THE ELECTROMAGNETIC COHERENCE
# HYPOTHESIS: FARADAY CAGE TEST
# IN C57BL/6N MICE
## OrganismCore Experimental
## Protocol Document 1
## February 27, 2026

---

## REGISTRATION METADATA

```
protocol_id:
  OC-EXP-001

series:
  OrganismCore Electromagnetic
  Navigation Series

relationship_to_prior_work:
  This experiment is the primary
  experimental test of the
  coherence framework developed
  from IMPC Analysis 3
  (Desk Analysis Documents 8-10,
  February 27, 2026).

  Prior work established:
    Observational correlation:
    Wildtype C57BL/6N thigmotaxis
    proportion correlates negatively
    with facility ELF score across
    6 IMPC centers.
    Spearman r=-0.886, p=0.019.
    N=16,161 wildtype animals.

  The observational result has
  two competing explanations:

    DOSE EXPLANATION:
      High chronic ELF has a
      direct anxiolytic effect
      on mouse neurobiology.
      ELF acts on the animal.

    COHERENCE EXPLANATION:
      Animals born into stable
      EM environments incorporate
      that environment into their
      self-model. Confidence in
      spatial navigation derives
      from model coherence, not
      from ELF dose. The effect
      is not ELF acting on the
      animal — it is the animal
      using ELF as reference.

  These two explanations make
  opposite predictions about
  what happens when the ELF
  environment is removed.
  This experiment tests that
  prediction.

registration_target:
  Open Science Framework (OSF)
  Pre-registration prior to
  data collection.
  All analyses specified before
  any data are observed.

pre_registration_deadline:
  This document must be lodged
  on OSF before any animals
  are assigned to conditions.
  Any analysis not specified
  here is exploratory and will
  be labeled as such in any
  resulting publication.

author:
  Eric Robert Lawson
  OrganismCore

status:
  DRAFT — ready for OSF submission
  pending identification of
  collaborating IMPC center.

ideal_collaborating_center:
  BCM (Baylor College of Medicine)
  Houston, TX.
  ELF score: 94 (highest in
  IMPC dataset).
  Texas Medical Center location.
  Established IMPC OFD pipeline.
  Wildtype thigmotaxis proportion
  in IMPC DR23: 58.3% —
  the lowest of any center,
  consistent with the coherence
  hypothesis prediction.
```

---

## PART I: THEORETICAL BACKGROUND

### The coherence hypothesis

```
The coherence hypothesis holds
that persistent, stable ambient
electromagnetic fields — including
the ELF (50/60 Hz) fields generated
by power line infrastructure and
building wiring — are incorporated
into an organism's self-model
during development.

The self-model is the nervous
system's continuous predictive
representation of the organism's
body and environment. It is built
from sensory input that is:
  — Persistent across development
  — Stable (not randomly varying)
  — Spatially structured

A signal meeting these criteria
is not experienced as a
perturbation. It is experienced
as reference — part of the
expected background against
which deviations are measured.

Consequence for behavior:
  An animal whose self-model
  was built in a stable, high-ELF
  environment has incorporated
  that field as a spatial reference.
  In a familiar or spatially
  predictable environment, the
  model and the environment match.
  Prediction error is low.
  Behavioral confidence is high.
  This manifests as low thigmotaxis
  in the open field — the animal
  explores rather than hugs walls
  because it knows, in a functional
  sense, where it is.

  If that reference signal is
  removed — by placing the animal
  in a Faraday-shielded enclosure
  that attenuates the ambient ELF
  field — the self-model no longer
  matches the environment.
  Prediction error increases.
  Behavioral confidence decreases.
  Thigmotaxis should increase.

  This prediction is the opposite
  of what the dose hypothesis
  predicts. The dose hypothesis
  holds that removing ELF should
  reduce disruption and therefore
  reduce anxiety-like behavior.

The two hypotheses are
experimentally dissociable.
This experiment dissociates them.
```

### The naked mole rat analogy

```
Queen death in a naked mole rat
colony produces rapid behavioral
collapse: increased conflict,
loss of coordinated foraging,
reproductive disorganization,
individual spatial disorientation.

The queen's pheromone is not a
nutrient or a toxin. It is an
organizing signal — a persistent,
stable, colony-wide reference
that each member uses to model
its social and spatial environment.

When the reference is removed,
the model becomes incoherent.
Behavior degrades not from damage
but from the loss of reference.

The ambient ELF field in a research
facility is the physical analog
of the queen's pheromone for
a colony-housed mouse:
  — Persistent from birth
  — Stable (infrastructure-sourced,
    not fluctuating)
  — Spatially structured within
    the facility
  — Available as a low-level
    sensory reference via
    magnetoreceptive or
    electrically-sensitive
    sensory channels

Removing it should produce the
same class of behavioral effect
as removing the queen:
not damage, but incoherence.
```

### Why this matters beyond mice

```
The coherence hypothesis, if
supported, has implications for:

  1. LABORATORY REPRODUCIBILITY:
     Behavioral phenotyping results
     may vary systematically across
     facilities not because of
     differences in animal husbandry,
     experimenter behavior, or
     genetic drift — but because
     of differences in the ambient
     EM environment in which animals
     were raised.

     This is a previously unrecognized
     source of between-facility
     variance in behavioral data.

  2. ANIMAL WELFARE:
     If animals use the ambient EM
     environment as spatial reference,
     then introducing them to novel
     EM environments — as occurs in
     any facility transfer — produces
     a period of genuine spatial
     disorientation beyond ordinary
     relocation stress. This has
     welfare implications for animal
     transport protocols.

  3. HUMAN HEALTH:
     If the coherence framework
     applies across mammals, chronic
     changes in ambient EM environment
     (moving to a new city, changing
     workplace, long-distance travel)
     may produce transient spatial
     disorientation and anxiety
     through the same mechanism —
     model-environment mismatch —
     not through any direct biological
     damage.

  4. NAVIGATION SCIENCE:
     The framework connects to the
     broader question of how animals
     use environmental EM fields for
     navigation. The coherence
     hypothesis extends this beyond
     compass use (directional
     navigation) to spatial
     confidence (exploratory behavior)
     — suggesting that EM reference
     is used not just to know which
     way to go but to know where
     one is.
```

---

## PART II: HYPOTHESES

### Primary hypothesis

```
H1 (COHERENCE HYPOTHESIS):
  Wildtype C57BL/6N mice born
  and raised in a high-ELF
  facility (BCM, ELF score 94)
  will show a SIGNIFICANT INCREASE
  in open field thigmotaxis
  proportion after transfer to
  a Faraday-shielded housing
  environment compared to
  sham-transferred controls.

  Operationally:
    Thigmotaxis proportion at
    day 14 post-transfer will be
    significantly higher in the
    Faraday group than in the
    sham group.

  This is the coherence prediction:
    Removing the familiar EM
    reference → model incoherence
    → increased spatial anxiety
    → increased thigmotaxis.
```

### Null hypothesis

```
H0:
  Faraday shielding will produce
  no significant change in
  thigmotaxis proportion compared
  to sham transfer.

  Operationally:
    No significant difference
    in thigmotaxis proportion
    between Faraday and sham
    groups at day 14.
```

### Competing hypothesis

```
H2 (DOSE HYPOTHESIS):
  Wildtype C57BL/6N mice born
  and raised in a high-ELF
  facility will show a SIGNIFICANT
  DECREASE in thigmotaxis
  proportion after transfer to
  a Faraday-shielded environment.

  This is the dose prediction:
    Removing the ELF dose →
    reduced biological disruption
    → reduced anxiety →
    decreased thigmotaxis.

  H2 is directionally opposite
  to H1. The experiment
  distinguishes them cleanly.
```

### Secondary hypotheses

```
H3 (TIME COURSE):
  The thigmotaxis increase in
  the Faraday group will be
  maximal at day 7 and will
  begin to decline by day 28
  as animals recalibrate their
  self-model to the shielded
  environment.

  Rationale: the coherence
  framework predicts that
  model recalibration occurs
  given sufficient time in
  the new environment. The
  animal learns the new EM
  baseline. Thigmotaxis should
  return toward original levels
  as recalibration completes.

H4 (RECOVERY):
  Animals returned from the
  Faraday cage to the standard
  facility environment at day 28
  will show a SECOND thigmotaxis
  increase — a recovery disruption
  — as they re-encounter the
  high-ELF environment that
  no longer matches their
  recalibrated model.

  The recovery disruption
  magnitude should be smaller
  than the initial disruption
  (partial recalibration
  occurred) but detectable.

H5 (SEX DIFFERENCE):
  If sex differences in
  magnetoreception or spatial
  navigation exist in C57BL/6N
  mice, male and female animals
  may show different magnitudes
  of thigmotaxis change.
  This is exploratory — no
  directional prediction is
  pre-registered for sex
  differences.

H6 (SHAM CONTROL STABILITY):
  Sham-transferred animals
  (handled and temporarily
  displaced but returned to
  standard caging) will show
  no significant change in
  thigmotaxis proportion from
  baseline across the 28-day
  observation period.

  Rationale: confirms that
  handling stress and temporary
  displacement alone do not
  produce sustained thigmotaxis
  changes.
```

---

## PART III: METHODS

### Animals

```
Species:    Mus musculus
Strain:     C57BL/6N
  (same sub-strain as used
   by the facility in its
   IMPC pipeline to ensure
   continuity with the
   observational dataset)
Sex:        Equal numbers male
            and female
Age:        8-10 weeks at start
            of experiment
            (post-weaning, pre-
            senescence, standard
            behavioral testing
            window)
Housing:    Group housed, 4 per
            cage, same-sex groups
            maintained throughout
            to minimize social
            disruption confound
Source:     Bred in-house at
            the collaborating
            facility (BCM ideal).
            Animals must have
            been born and raised
            at the facility.
            No animals imported
            from external sources
            for this experiment.

CRITICAL INCLUSION CRITERION:
  All animals must have been
  born at the facility and
  spent their entire lives
  (from conception) in the
  facility's standard ambient
  EM environment.

  Animals imported from other
  facilities must not be used.
  They will not have developed
  their self-model in the
  target ELF environment and
  the coherence prediction
  will not apply to them.
```

### Sample size justification

```
Primary analysis:
  Two-group comparison of
  thigmotaxis proportion at
  day 14 (Faraday vs sham).

Effect size estimate:
  From IMPC DR23 observational
  data, the between-facility
  range in wildtype thigmotaxis
  proportion spans 36 percentage
  points (58.3% to 94.3%).

  The within-facility change
  predicted by the coherence
  hypothesis is not the full
  between-facility range —
  that range reflects lifetime
  development. The predicted
  acute disruption effect is
  conservatively estimated at
  30-50% of the between-facility
  range, giving an expected
  effect of 10-18 percentage
  points.

  Cohen's d estimate:
    Expected difference: 12 pp
    Within-group SD from IMPC
    DR23 OFD data: ~15 pp
    Estimated d = 12/15 = 0.80
    (large effect)

Power calculation:
  Alpha = 0.05 (two-tailed)
  Power = 0.90
  Effect size d = 0.80
  Required N per group: 34

  Rounding up for attrition:
  N = 40 per group

Total animals:
  Faraday group:    40
  Sham group:       40
  Total:            80

  Sex balance:
  20 male + 20 female per group
  = 40 male + 40 female total

  Cage allocation:
  4 animals per cage
  = 10 cages per group
  = 20 cages total

Sequential cohort option:
  If resource constraints require
  it, the experiment may be run
  in two sequential cohorts of
  N=20 per group, with the second
  cohort added only after the
  first cohort data are reviewed
  for quality (not for results —
  result-blind sequential addition
  only). A Bonferroni correction
  for the two looks will be applied
  if sequential design is used.
```

### Faraday cage construction

```
Requirement:
  Attenuate ambient ELF fields
  (50/60 Hz) within animal
  housing space by ≥20 dB
  (>90% field reduction).

Specification:
  Material: mu-metal or
    high-permeability silicon
    steel sheet, minimum
    0.5mm thickness.
  Geometry: fully enclosed
    box with gasketed door.
    No gaps >1mm.
  Ventilation: conductive
    mesh screen (wire diameter
    <0.5mm, mesh spacing <2mm)
    covering ventilation ports.
    Mesh continuity with main
    enclosure maintained.
  Dimensions: sufficient to
    house 10 standard mouse
    cages (40 animals) with
    appropriate spacing.
  Grounding: enclosure grounded
    to facility earth ground.

Verification:
  Field attenuation must be
  measured before experiment
  begins and at weekly intervals
  throughout.

  Measurement instrument:
    Calibrated ELF magnetometer
    (e.g., Sypris Model 1000B
    or equivalent).
    Sensitivity: <1 nT.
    Frequency range: 5-1000 Hz.

  Measurement protocol:
    Measure field at 9 positions
    within the Faraday enclosure
    (3×3 grid) and at matched
    positions in the standard
    facility room.
    Record all three axes (X, Y, Z).
    Report total field magnitude.

  Acceptance criterion:
    Mean field inside Faraday
    enclosure ≤ 10% of mean
    field in standard facility
    room at 50 or 60 Hz.
    If this criterion is not met,
    the enclosure must be repaired
    before the experiment begins.

  Field measurements will be
  reported in full in any
  resulting publication.
  This is the first experiment
  in this series to use actual
  measured field values rather
  than estimated ELF scores.

Internal environment matching:
  All non-EM aspects of the
  Faraday cage environment must
  match the standard facility
  environment as closely as
  possible:
    Temperature: ±0.5°C of
      standard room temperature
    Humidity: ±5% of standard
    Light cycle: identical
      (12h/12h, same lux level)
    Bedding: identical material
      and change schedule
    Food and water: identical
      ad libitum access
    Sound: acoustic dampening
      should not be applied
      beyond what the enclosure
      walls provide incidentally.
      Sound is not the variable
      being tested.
    Odor: Faraday cage should
      be cleaned with identical
      products on identical
      schedule to standard cages.
```

### Sham control condition

```
The sham condition controls for:
  — Handling stress
  — Temporary displacement
    from home cage
  — Novel cage exposure
  — Experimenter contact

Sham protocol:
  Sham animals are removed from
  their home cages, carried to
  a holding room, placed in a
  temporary cage for 30 minutes,
  then returned to their original
  home cage in the standard
  facility room.

  This procedure is performed
  on the same day as Faraday
  transfer and at matched times
  of day.

  Sham animals remain in standard
  facility housing for the entire
  28-day observation period.

  They receive open field testing
  on the same schedule as Faraday
  animals (see below).

What the sham does NOT control:
  — Prolonged housing in a
    genuinely novel environment
  — Loss of familiar EM reference

  The sham controls for acute
  handling effects only. It is
  not a perfect control for the
  slow, sustained EM change
  experienced by the Faraday
  group. This limitation is
  acknowledged and documented.

  A more complete control would
  be a second facility with
  matched ELF — but this requires
  cross-center transfer and
  introduces additional confounds.
  The sham is the best single-
  facility control available.
```

### Experimental timeline

```
Day -14 to Day 0 (Baseline period):
  All animals housed in standard
  facility conditions.
  No experimental procedures.
  Animals habituate to their
  final home cage compositions
  (groups of 4 established at
  day -14 and not changed).

Day -7:
  Baseline open field test 1.
  All animals tested.
  This is the first of two
  baseline measurements.

Day -1:
  Baseline open field test 2.
  All animals tested.
  Two baseline tests allow
  assessment of test-retest
  reliability and identification
  of animals with unusually
  variable baselines.

Day 0 (Transfer day):
  FARADAY GROUP:
    Moved with their home cages
    into the Faraday enclosure.
    No other changes.
  SHAM GROUP:
    Sham procedure performed.
    Returned to standard housing.

Day 1:
  No behavioral testing.
  Allow acute transfer stress
  to resolve.

Day 3:
  Open field test.
  First post-transfer measure.
  Expected to show acute
  disruption if H1 is correct.

Day 7:
  Open field test.
  Expected to show maximal
  disruption (H3 prediction).

Day 14:
  Open field test.
  PRIMARY OUTCOME MEASURE.
  Pre-registered primary
  analysis is performed on
  this time point.

Day 21:
  Open field test.
  Expected to show beginning
  of recalibration (H3).

Day 28:
  Open field test.
  Expected to show partial
  recovery toward baseline (H3).

  AFTER Day 28 test:
  FARADAY GROUP SPLIT:
    Half (N=20) returned to
    standard facility housing.
    → Recovery disruption test (H4)
    Half (N=20) remain in Faraday.
    → Extended observation

Day 35:
  Open field test.
  Return subgroup: tests H4
    (recovery disruption after
    re-exposure to high-ELF).
  Remain subgroup: continued
    monitoring of recalibration.

Day 42:
  Final open field test.
  All groups.
  Experiment ends.
```

### Open field test protocol

```
Apparatus:
  Standard IMPC open field arena.
  IMPC_OFD_001 protocol.
  Same arena dimensions and
  zone definitions as used in
  the facility's standard
  IMPC pipeline.

  CRITICAL: The zone definitions
  must be identical to those
  used in the IMPC DR23 data
  collection. This ensures
  comparability between the
  experimental results and the
  observational dataset.

Test duration:
  60 minutes.
  (matching BCM's confirmed
  protocol duration from
  IMPC DR23 analysis)

Parameters recorded:
  PRIMARY:
    IMPC_OFD_010_001
    Time in periphery (seconds)
    → converted to proportion:
      thigmotaxis_proportion =
        periphery_time / 3600

  SECONDARY:
    IMPC_OFD_009_001
    Time in center (seconds)

    IMPC_OFD_008_001
    Center entries (count)

    IMPC_OFD_013_001
    Rearing count

    Total distance traveled (cm)
    → locomotion control

Testing conditions:
  Time of day: same 2-hour window
    for all tests throughout the
    experiment (controls for
    circadian effects on thigmotaxis)
  Lighting: standard IMPC protocol
  Experimenter: same experimenter
    for all tests where possible.
    If multiple experimenters,
    counterbalanced across groups.
  Arena cleaning: 70% ethanol
    between animals, allowed to
    fully dry before next animal.

Blinding:
  The experimenter performing
  the open field test should be
  blind to group assignment
  (Faraday vs sham) where
  logistically feasible.
  Full blinding is difficult
  given the physical separation
  of housing conditions.
  Partial blinding (scorer blind
  to group during video analysis)
  should be maintained for any
  manual scoring components.
  Automated tracking software
  is preferred and eliminates
  scorer bias in zone calculation.

Order effects:
  Testing order within each
  session should be randomized
  across groups. Animals from
  Faraday and sham groups should
  be interleaved in the testing
  order, not tested in blocks.
```

---

## PART IV: PRIMARY ANALYSIS

### Pre-registered primary test

```
ANALYSIS 1 — PRIMARY:

  Test: Mann-Whitney U test
    (non-parametric, appropriate
    for behavioral proportions
    which are typically non-normal)

  Groups:
    Faraday (N=40)
    Sham (N=40)

  Dependent variable:
    Thigmotaxis proportion at
    Day 14 (post-transfer)

  Alpha: 0.05 (two-tailed)

  Hypothesis direction:
    H1 predicts Faraday > Sham
    H2 predicts Faraday < Sham
    H0 predicts no difference

  Both H1 and H2 are directional.
  The test is two-tailed to
  allow either direction to
  be detected without bias.

  Reporting:
    Regardless of outcome,
    the full result (U statistic,
    p-value, effect size r,
    median and IQR for each group)
    will be reported.

    If p < 0.05 AND direction
    matches H1 (Faraday > Sham):
      Coherence hypothesis supported.
      Dose hypothesis disconfirmed.

    If p < 0.05 AND direction
    matches H2 (Faraday < Sham):
      Dose hypothesis supported.
      Coherence hypothesis disconfirmed.

    If p ≥ 0.05:
      Neither hypothesis confirmed.
      Effect size reported.
      Secondary time-course analysis
      examined for interpretive
      context.
```

### Pre-registered secondary analyses

```
ANALYSIS 2 — BASELINE COMPARISON:

  Verify that Faraday and sham
  groups do not differ at baseline
  before transfer.

  Test: Mann-Whitney U
  Groups: Faraday vs Sham
  DV: mean thigmotaxis proportion
      across Day -7 and Day -1
  Alpha: 0.05

  If groups differ significantly
  at baseline, the randomization
  has failed and the primary
  analysis must be re-examined
  with baseline as a covariate.

ANALYSIS 3 — TIME COURSE:

  Tests H3: maximal disruption
  at Day 7, beginning recovery
  by Day 28.

  Test: Mixed-model ANOVA
    (or equivalent non-parametric:
    Friedman test within each group,
    followed by Wilcoxon signed-rank
    for pairwise time comparisons)

  Within-subject factor: Time
    (Day -7, -1, 3, 7, 14, 21, 28)
  Between-subject factor: Group
    (Faraday, Sham)
  DV: Thigmotaxis proportion

  Pre-registered contrasts:
    Day 14 vs Day -1 within Faraday
      (primary disruption test)
    Day 28 vs Day 14 within Faraday
      (partial recovery test)
    Faraday vs Sham at each time
      point separately (exploratory)

ANALYSIS 4 — RECOVERY DISRUPTION:

  Tests H4: second disruption
  peak when Faraday animals are
  returned to standard housing.

  Test: Wilcoxon signed-rank
  Group: Return subgroup (N=20)
  Comparison: Day 35 vs Day 28
  DV: Thigmotaxis proportion
  Alpha: 0.05

  This is a within-group test
  on the return subgroup only.

ANALYSIS 5 — SEX DIFFERENCE:

  Exploratory (not primary).

  Test: Three-way mixed model
    Group × Sex × Time
  DV: Thigmotaxis proportion
  Report interaction terms.
  No directional prediction.
  Alpha: 0.05 with explicit
  acknowledgment that this
  is exploratory.

ANALYSIS 6 — LOCOMOTION CONTROL:

  Total distance traveled in
  OFD is analyzed identically
  to thigmotaxis proportion.

  If the Faraday group shows
  significantly different total
  distance (not just zone
  preference), the thigmotaxis
  result may reflect locomotion
  change rather than anxiety
  change. Reporting both is
  required. A result where
  thigmotaxis changes but total
  distance does not is the
  cleaner anxiety-specific
  interpretation.
```

### Decision tree for interpretation

```
                  ┌─────────────────┐
                  │ Day 14 primary  │
                  │ analysis result │
                  └────────┬────────┘
                           │
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
    Faraday > Sham    No difference    Faraday < Sham
    p < 0.05          p ≥ 0.05         p < 0.05
           │               │               │
           ▼               ▼               ▼
   COHERENCE H1        EXAMINE          DOSE H2
   SUPPORTED           TIME COURSE      SUPPORTED
           │               │               │
           ▼               ▼               ▼
   Check: is         If time course   Check: is
   locomotion        shows transient  locomotion
   unchanged?        early increase   increased?
   YES → clean       that resolved:   YES → general
   anxiety result    coherence        activation
   NO → examine      with fast        effect
   locomotion        recalibration    NO → examine
   confound          documented       further
           │
           ▼
   Check H4:
   recovery disruption
   at Day 35?
   YES → strong
   coherence support
   (two-direction
   prediction met)
   NO → coherence
   supported but
   recalibration
   faster than
   predicted
```

---

## PART V: WHAT EACH OUTCOME
## MEANS FOR THE SERIES

### If H1 is supported
### (Faraday > Sham, p < 0.05)

```
Immediate implications:

  1. The IMPC observational
     correlation (r=-0.886,
     p=0.019) is given a causal
     mechanism. The between-
     facility behavioral differences
     are not explained by uncontrolled
     husbandry confounds — they
     are replicated in a controlled
     within-facility manipulation.

  2. The coherence framework is
     supported over the dose
     framework. The direction
     (removal of ELF increases
     anxiety) is the opposite of
     what dose predicts and is
     the specific prediction of
     the coherence framework.

  3. The between-facility variance
     in IMPC behavioral data is
     partially attributable to
     EM environment differences.
     This is a methodological
     finding with implications
     for all IMPC-dependent
     research using behavioral
     endpoints.

  4. The framework extends:
     If mice use ambient ELF as
     spatial reference, other
     mammals including humans
     may do the same. The
     implications for human
     health and neuroscience
     are substantive and
     require investigation.

  5. The monarch analysis is
     contextualized: the same
     framework that explains
     mouse thigmotaxis explains
     monarch bearing deviation —
     not as direct compass
     disruption but as
     incoherence between the
     animal's EM model and
     the EM landscape it is
     navigating through.

Publication pathway:
  Primary target: Nature Neuroscience
    or eLife (experimental
    neuroscience).
  Secondary: Proceedings of the
    Royal Society B (if framed
    as comparative/ecological).
  Pre-print: bioRxiv immediately
    upon completion, regardless
    of journal submission status.
```

### If H0 is supported
### (no difference, p ≥ 0.05)

```
  The coherence hypothesis is
  not supported in this form.

  This does not mean the IMPC
  observational result is wrong.
  It means the Faraday
  manipulation at this time
  scale does not produce
  detectable thigmotaxis change.

  Possible explanations:
    1. Effect size smaller than
       estimated — experiment
       was underpowered.
       (check: was observed effect
        in predicted direction even
        if not significant?)

    2. Developmental critical
       window hypothesis: 8-10
       week old mice have already
       completed the sensitive
       period during which EM
       signals are incorporated
       into the self-model.
       Removing ELF at adulthood
       does not disrupt a model
       that was already consolidated.
       → Design the developmental
         shielding experiment (H3
         in the full series).

    3. The Faraday cage does not
       attenuate the relevant
       frequency or field component.
       ELF attenuation was confirmed,
       but if the biologically
       relevant signal is at a
       different frequency (RF,
       static field, or a higher
       harmonic), the manipulation
       did not work as intended.
       → Measure full spectrum.

    4. The IMPC observational
       correlation reflects a
       different confound entirely.
       The between-facility variance
       is due to something that
       co-varies with ELF score
       but is not ELF.
       → Coherence hypothesis for
         mice is not supported.
         Document honestly.

  Reporting:
    All of the above will be
    reported in full. A null
    result in a pre-registered
    experiment is a result.
    It will be published.
```

### If H2 is supported
### (Faraday < Sham, p < 0.05)

```
  The dose hypothesis is supported.
  The coherence hypothesis is
  disconfirmed in its strong form.

  Implication: removing ambient
  ELF reduces anxiety-like
  behavior. High chronic ELF
  produces mild but genuine
  biological disruption that
  manifests as anxiety. Lower
  ELF = calmer animals.

  This means the between-facility
  IMPC correlation is still real
  and ELF-driven, but the mechanism
  is a direct biological effect,
  not model coherence.

  Implication for the series:
  The monarch analysis would need
  to be reframed around dose-
  dependent compass disruption,
  and the static opposition angle
  (not the path coherence score)
  would be the primary variable
  of interest.

  The dose framework would be
  partially rehabilitated for
  mammals. The coherence framework
  would remain relevant for
  navigation but would not apply
  to the anxiety/exploration
  behavioral domain.

  Reporting:
    Full result reported.
    Coherence hypothesis
    disconfirmed explicitly.
    Dose hypothesis supported
    explicitly.
    Implications restated.
```

---

## PART VI: EXTENDED EXPERIMENT
## DESIGNS (NOT PRE-REGISTERED
## HERE — FOR FUTURE PROTOCOLS)

```
These experiments are described
for completeness and theoretical
context. They are NOT part of
the current pre-registration.
Each requires a separate
pre-registration before data
collection.

EXPERIMENT 2:
BIDIRECTIONAL FACILITY RELOCATION

  Transfer BCM mice to UC Davis
  and UC Davis mice to BCM.
  Test thigmotaxis at 1, 7, 28,
  90 days post-transfer.

  Coherence prediction:
    Both directions show short-
    term thigmotaxis increase.
    Long-term endpoint differs:
    BCM→UCD converges to UCD
    baseline (~92%); UCD→BCM
    converges to BCM baseline
    (~58%).

  This is the strongest possible
  test of the coherence framework
  because it requires a symmetric
  short-term prediction (both
  directions increase) that the
  dose framework cannot produce
  (dose predicts asymmetric
  response: UCD→BCM should
  increase, BCM→UCD should
  decrease).

EXPERIMENT 3:
DEVELOPMENTAL WINDOW

  Pregnant BCM dams transferred
  to Faraday shielding at
  gestational day 1.
  Offspring born and raised in
  shielded environment.
  Compare thigmotaxis at P21,
  P45, P90 to BCM-born controls.

  Coherence prediction:
    Shielded offspring show
    higher thigmotaxis than
    BCM-born controls throughout
    life — they built their
    self-model without the
    high-ELF scaffold.

  Critical window sub-experiment:
    Compare shielding from GD1
    vs from P21 vs from P60.
    If the critical window closes
    early, later shielding should
    have progressively smaller
    effects.

EXPERIMENT 4:
WITHIN-FACILITY GRADIENT

  Within a single large facility
  (BCM or equivalent), identify
  rooms with measurably different
  ELF levels (near vs far from
  transformer rooms, MRI suites,
  or high-current equipment).

  Measure thigmotaxis in animals
  born and raised in high-ELF
  vs low-ELF rooms within the
  same facility.

  Controls for all facility-level
  confounds except EM environment.
  The tightest possible
  observational test.

EXPERIMENT 5:
FIELD REINTRODUCTION

  After 28 days in Faraday cage
  (assuming H1 supported and
  recalibration occurring):
  introduce a controlled ELF
  source inside the Faraday cage
  at a field strength matching
  the standard facility level.

  Coherence prediction:
    Reintroduction of the familiar
    signal reverses the thigmotaxis
    increase. Animals recognize
    and incorporate the familiar
    reference.

    If a different field strength
    is introduced (not matching
    the original BCM level),
    the animal cannot recognize
    it as the familiar reference
    and thigmotaxis does not
    recover.

  This experiment directly tests
  whether the behavioral effect
  is specific to the familiar
  signal (coherence) or non-
  specific to any ELF signal
  (dose).
```

---

## PART VII: RELATIONSHIP TO
## FULL SERIES

```
This experiment is the primary
experimental test of the
coherence framework developed
from the observational analyses
in the OrganismCore series.

Position in series:

  Analysis 1 (Monarchs):
    Tests whether FM landscape
    spatial coherence predicts
    migration bearing accuracy.
    Observational. V-test pending.
    Coherence metric computed
    and waiting for recovery data.

  Analysis 3 (IMPC):
    Established the observational
    correlation between facility
    ELF and wildtype thigmotaxis.
    r=-0.886, p=0.019. N=6.
    Fragile. Requires experimental
    confirmation.

  OC-EXP-001 (This experiment):
    First controlled experimental
    test of the coherence framework.
    Distinguishes coherence from
    dose hypothesis directly.
    If H1 supported: provides
    mechanistic explanation for
    IMPC observational result and
    contextualizes monarch analysis.
    If H0: null published, design
    revised toward developmental
    window experiment.
    If H2: dose framework supported,
    series reframed accordingly.

  All outcomes are informative.
  All outcomes will be published.
  The pre-registration ensures
  this commitment is recorded
  before data are collected.
```

---

## PART VIII: DATA MANAGEMENT

```
DATA COLLECTION:
  All raw tracking data retained
  in original format from the
  automated tracking software.
  No data points removed without
  pre-specified exclusion criteria
  (see below).

PRE-SPECIFIED EXCLUSION CRITERIA:
  Animals will be excluded from
  analysis if:
    1. Body weight loss >20%
       during the experiment
       (health criterion)
    2. Open field total distance
       <100cm in a 60-minute
       session (immobility —
       indicates illness or
       sedation, not anxiety)
    3. Open field total distance
       >15,000cm (extreme outlier
       — indicates distressed
       hyperactivity, not anxiety)
    4. Death or humane endpoint
       during the experiment

  All exclusions will be reported
  with reasons. Animals excluded
  for criterion 3 will be
  analyzed separately to determine
  if hyperactivity distribution
  differs between groups.

  No exclusions based on
  thigmotaxis value are permitted.
  The dependent variable cannot
  be used to exclude animals
  from the analysis of that
  same variable.

DATA STORAGE:
  Raw data: facility server,
    backed up weekly.
  Analysis-ready CSV: OSF
    project, uploaded at end of
    experiment before analysis.
  Analysis scripts: OSF project,
    uploaded with pre-registration.
  Results: reported in full
    regardless of outcome.

OPEN DATA:
  All data will be made publicly
  available on OSF at the time
  of pre-print submission.
  No embargo.

ANALYSIS CODE:
  All analysis code will be
  published with the data.
  Python (scipy, pandas, numpy,
  matplotlib) consistent with
  the OrganismCore series
  analytical pipeline.
```

---

## PART IX: ETHICAL STATEMENT

```
Animal use justification:
  This experiment requires
  live animals because the
  hypothesis concerns a
  behavioral response to an
  environmental manipulation.
  No in vitro or computational
  substitute exists for the
  primary behavioral endpoint.

  The IMPC observational dataset
  (851,255 existing observations)
  was used to develop the
  hypothesis and compute power.
  No additional animals were
  used in the observational phase.

  The number of animals (N=80)
  is the minimum required to
  achieve 90% power at the
  estimated effect size. It
  is not inflated beyond what
  the power calculation requires.

Welfare considerations:
  The Faraday cage manipulation
  is a passive housing condition.
  No painful procedures are
  applied as part of the EM
  manipulation itself.

  Open field testing causes
  mild, transient stress. It
  is a standard procedure with
  established welfare acceptability
  in laboratory mouse research.

  If the coherence hypothesis
  is correct and Faraday housing
  produces genuine spatial
  disorientation, this constitutes
  a welfare impact that must be
  monitored. Animals showing
  signs of sustained distress
  (weight loss, barbering,
  stereotypy, wound infliction)
  will be removed from the
  Faraday condition and the
  incident reported.

  The irony that this experiment
  may cause the distress it is
  designed to detect is noted
  explicitly. It is managed by
  the health monitoring criteria
  above and by limiting the
  experiment duration to 42 days.

Regulatory approval:
  Full IACUC (or equivalent
  national authority) approval
  required before experiment
  begins. This protocol document
  will be submitted as part of
  the IACUC application.
  No data collection before
  approval is received and
  documented.
```

---

## VERSION AND SIGNATURES

```
Protocol version:  1.0
Date drafted:      February 27, 2026
Drafted by:        Eric Robert Lawson
                   OrganismCore

OSF pre-registration:
  To be submitted prior to
  IACUC application.
  OSF registration ID to be
  added here upon submission.

Amendment policy:
  Any change to this protocol
  after OSF registration must
  be documented as a numbered
  amendment with date and
  rationale. Amendments made
  after data collection begins
  will be flagged in any
  resulting publication and
  their impact on interpretation
  discussed explicitly.

Conflict of interest:
  The author developed the
  coherence hypothesis being
  tested. This creates a
  potential confirmation bias.
  Pre-registration, open data,
  and full reporting of all
  outcomes regardless of
  direction are the primary
  safeguards against this bias.

Acknowledgment:
  This protocol was developed
  from analyses conducted with
  GitHub Copilot (Microsoft/OpenAI)
  as analytical assistant,
  February 27, 2026.
  All theoretical claims,
  experimental design decisions,
  and interpretations are the
  responsibility of the author.
```

---

## AMENDMENT 1
## SHAM ENCLOSURE CONTROL
## February 27, 2026
## Filed prior to OSF registration
## and prior to any data collection

---

### REASON FOR AMENDMENT

```
The original sham condition
specified in Part III was:

  Sham animals are removed from
  their home cages, carried to
  a holding room, placed in a
  temporary cage for 30 minutes,
  then returned to their original
  home cage in the standard
  facility room.

This sham controls for:
  — Handling stress
  — Temporary displacement
  — Acute novelty exposure

It does NOT control for:

  The Faraday enclosure itself
  being a perceptibly novel
  housing environment.

If mice can detect — through
any available sensory channel
(visual, acoustic, olfactory,
thermal) — that they are housed
in a different kind of enclosure,
then any increase in thigmotaxis
in the Faraday group is
uninterpretable.

It could be caused by:
  (a) Loss of EM reference
      (the coherence hypothesis)
  OR
  (b) General novelty anxiety
      from being in a perceptibly
      different enclosure

These two causes produce
identical behavioral outcomes
and are indistinguishable
without a sham enclosure control.

This confound was identified
prior to OSF registration and
prior to any data collection.
This amendment corrects it.
```

---

### CHANGE TO SHAM CONDITION

```
The original sham condition
(handling and temporary
displacement only) is REPLACED
by a SHAM ENCLOSURE condition.

SHAM ENCLOSURE SPECIFICATION:

  The sham enclosure is physically
  identical to the Faraday
  enclosure in all respects
  except electromagnetic shielding:

    Material: identical outer
      structure and dimensions
    Ventilation: identical geometry
      and mesh specification
    Door: identical gasketed design
    Grounding: identical ground
      connection (connected but
      no shielding layer)
    Interior: identical layout,
      same cage type, same
      bedding, same light level
    Cleaning: identical products
      on identical schedule
    Temperature: matched to
      ±0.5°C of Faraday enclosure
      interior — both monitored
      continuously

  THE ONLY DIFFERENCE:
    Faraday enclosure: mu-metal
      or silicon steel shielding
      layer present.
      EM field attenuated ≥20 dB.

    Sham enclosure: no shielding
      layer.
      EM field present at ambient
      facility level.

WHAT THIS CONTROLS:

  Animals in both groups are
  housed inside an enclosure.
  Both enclosures look, sound,
  smell, and feel identical
  to the animal.

  The mice are blind to the
  EM manipulation.

  The only variable that differs
  between the two groups is
  the electromagnetic field
  level inside the enclosure.

  All enclosure novelty effects
  are matched across groups.
  Any difference in thigmotaxis
  between groups is attributable
  to the EM variable, not to
  enclosure novelty.
```

---

### UPDATED SAMPLE SIZE

```
ORIGINAL DESIGN:
  Faraday group:  40
  Sham group:     40
  Total:          80

AMENDED DESIGN:
  Faraday enclosure group:  40
  Sham enclosure group:     40
  Total:                    80

Sample size is unchanged.
The sham enclosure group
replaces the handling-only
sham group on a 1:1 basis.

Power calculation is unchanged:
  Alpha = 0.05 (two-tailed)
  Power = 0.90
  Effect size d = 0.80
  N = 40 per group
```

---

### UPDATED BLINDING STATEMENT

```
ORIGINAL:
  "The experimenter performing
  the open field test should be
  blind to group assignment
  (Faraday vs sham) where
  logistically feasible. Full
  blinding is difficult given
  the physical separation of
  housing conditions."

AMENDED:
  Because both groups are housed
  in physically identical
  enclosures, full experimenter
  blinding during behavioral
  testing is now achievable.

  The experimenter performing
  the open field test MUST be
  blind to group assignment
  (Faraday enclosure vs sham
  enclosure).

  The enclosures are labeled
  with codes only — no labels
  indicating Faraday or sham
  status visible to the
  experimenter retrieving
  animals for testing.

  Code-breaking occurs only
  after all behavioral data
  are collected and the
  analysis-ready dataset
  is finalized.

  This is a stronger blinding
  condition than the original
  protocol and is now feasible
  because the enclosures are
  perceptually identical.
```

---

### UPDATED H6

```
ORIGINAL H6 (SHAM STABILITY):
  Sham-transferred animals
  (handled and temporarily
  displaced but returned to
  standard caging) will show
  no significant change in
  thigmotaxis proportion from
  baseline across the 28-day
  observation period.

AMENDED H6 (SHAM ENCLOSURE
STABILITY):
  Animals housed in the sham
  enclosure (identical structure,
  no EM shielding) will show
  no significant change in
  thigmotaxis proportion from
  baseline across the 28-day
  observation period.

  Rationale: if the sham
  enclosure group shows a
  thigmotaxis increase, the
  enclosure itself — not the
  EM manipulation — is driving
  behavior, and the primary
  analysis is uninterpretable.

  If BOTH Faraday and sham
  enclosure groups show
  thigmotaxis increases:
    Enclosure novelty is the
    cause. EM variable is not
    isolable in this design.
    Experiment reported as
    inconclusive on the EM
    hypothesis. Redesign required.

  If ONLY the Faraday group
  shows a thigmotaxis increase:
    Enclosure novelty is ruled
    out. EM removal is the
    isolable cause.
    H1 supported.
```

---

### VERIFICATION REQUIREMENT
### ADDED

```
Before animals are placed in
either enclosure, the following
must be confirmed and documented:

  1. ACOUSTIC VERIFICATION:
     Sound level measurement
     inside both enclosures
     must confirm they are
     within 3 dB of each other
     at all frequencies from
     20 Hz to 20 kHz.
     Any acoustic difference
     between enclosures must
     be corrected before use.

  2. OLFACTORY VERIFICATION:
     Both enclosures must be
     operated empty for minimum
     14 days prior to animal
     placement to allow off-
     gassing of any construction
     materials.
     Air exchange rate inside
     both enclosures measured
     and matched to within 10%
     of each other.

  3. THERMAL VERIFICATION:
     Temperature logged at 1-hour
     intervals inside both
     enclosures for minimum 7
     days prior to animal
     placement.
     Both enclosures must remain
     within ±0.5°C of each other
     and within ±0.5°C of the
     standard facility room
     temperature throughout.

  4. EM VERIFICATION:
     Confirmed in original
     protocol. Unchanged.
     Faraday enclosure: ≤10%
     of ambient field.
     Sham enclosure: 95-105%
     of ambient field (within
     normal facility variation).

  All verification measurements
  will be reported in full
  in any resulting publication.
  Failure to meet any criterion
  delays animal placement until
  the criterion is met.
  No exceptions.
```

---

### AMENDMENT METADATA

```
Amendment number:  1
Protocol version:  1.0 → 1.1
Amendment date:    February 27, 2026

Filed:
  Prior to OSF registration.
  Prior to any animal assignment.
  Prior to enclosure construction.

Reason summary:
  Sham enclosure control required
  to isolate EM variable from
  enclosure novelty confound.
  Identified prior to registration.
  Corrected prior to registration.
  Documented as amendment for
  full transparency of protocol
  development history.

Effect on hypotheses:
  H1, H2, H0: unchanged in
    direction and operationalization.
  H6: updated to reflect sham
    enclosure rather than
    handling-only sham.
  All other hypotheses: unchanged.

Effect on primary analysis:
  Unchanged. Mann-Whitney U,
  Day 14, Faraday vs sham
  enclosure, alpha 0.05.

Effect on sample size:
  Unchanged. N=40 per group.

Effect on blinding:
  Strengthened. Full blinding
  now achievable and required.

Drafted by:
  Eric Robert Lawson
  OrganismCore
  February 27, 2026
```
