# OC-TINNITUS-001 — PREREGISTRATION
## Tinnitus Eigenfunction Calibration:
## Acoustic Structural Correction for
## Cochlear False Attractor Suppression
## OrganismCore — Eric Robert Lawson
## 2026-03-23

---

## PREREGISTRATION METADATA

```
document_type:
  Preregistration.
  States the theoretical framework,
  predictions, protocol, and success
  criteria BEFORE empirical testing.
  Written to establish the record
  prior to first external administration.

status:
  LOCKED — preregistration.
  Version 1.1 amendment applied
  2026-03-23, same date as original,
  prior to first external session.
  Amendment is methodological only:
  timing protocol corrected from
  beanie observation.
  No predictions, claims, success
  criteria, or failure criteria
  are changed.
  See VERSION section for full
  amendment record.

author:
  Eric Robert Lawson
  OrganismCore

date_locked: 2026-03-23

first_external_session:
  PENDING
  Subject: male, bilateral tinnitus,
  acute acoustic trauma origin
  (construction, high-RPM saw blade,
  remembered onset, both ears)
  Session document will be:
  OC-TINNITUS-002_FIRST_EXTERNAL_SESSION.md

depends_on:
  P4_results.md
    (χ² = 2328.1, n = 1514,
     cochlear eigenfunction clustering
     confirmed)
  tinnitus_eigenfunction_mapping_
    and_therapy.md (Document 66)
  the_broken_instrument.md (Document 67)
  tinnitus_trial_protocol.md (Document 68)
  OC-TINNITUS-001_LITERATURE_SWEEP_V1.md
  tinnitus_calibration.py
  OC-TINNITUS-001_SELF_ADMINISTRATION_
    GUIDE.md
```

---

## PART I: THE CORE CLAIM

### 1.1 What this protocol is

```
This is not a tinnitus treatment.
This is not a tinnitus cure.
This is not a therapy.
This is not expected to produce
lasting improvement after removal.

This is a prescription acoustic
correction — the structural equivalent
of corrective lenses — for a damaged
cochlear instrument.

GLASSES PRINCIPLE:

  Glasses do not fix the eye.
  Glasses do not expect neural
  reorganisation toward better vision.
  Glasses do not produce lasting
  improvement after removal.

  Remove the glasses: vision is
  exactly as impaired as before.

  That is not failure.
  That is the correct description
  of what glasses are.

  They are a structural correction
  applied at the interface between
  the world and the damaged instrument.
  The world's light, reshaped to fit
  the geometry of the damaged lens.
  The experiencer sees correctly while
  the correction is applied.
  Structure unchanged.
  Experience corrected.

THIS PROTOCOL:

  The cochlear damage is permanent.
  The false attractor is permanent.
  The tinnitus will remain.
  Remove the remedy: tinnitus returns.
  Exactly as expected.
  Exactly as with glasses.

  This is glasses for a broken ear.

  The question is not:
    "Will this cure the tinnitus?"

  The question is:
    "While applied, does the experiencer
     perceive acoustic coherence instead
     of the false attractor?"

  Yes or no.
  That is the only question.
```

### 1.2 The structural basis

```
The cochlea is a physical resonating
structure. Its response properties at
each position are determined by its
geometry — the stiffness gradient of
the basilar membrane, described by
the Greenwood function (1961).

When outer hair cells in a cochlear
zone are damaged, that zone stops
responding coherently to the world's
acoustic signal. Instead, the damaged
membrane resonates at its nearest
stable eigenfunction position —
a false attractor determined by the
physical geometry of the structure.

That resonance is tinnitus.

It is not random.
It is not neural hyperactivity
  generating arbitrary frequency.
It is geometrically constrained
  by the physical structure of the
  damaged resonating instrument.

EMPIRICAL CONFIRMATION:
  OHSU Tinnitus Archive, Data Set 1
  n = 1,514 patients, 1981–1994
  Chi-squared = 2328.1
  p ≈ 0 (underflows double-precision float)
  df = 5

  The 4–10 kHz zone (18% of cochlear
  length) contains 61.6% of all
  tinnitus cases.

  Enrichment is non-monotonic:
  peaks at 4.86× at 8–10 kHz,
  falls to 1.30× at 10–16 kHz.

  This non-monotonic shape is predicted
  by the cochlear eigenfunction account.
  It is NOT predicted by the audiometric
  edge account (standard model).

  The geometry determines the frequency.
  Not the extent of damage.
  Not the audiometric edge.
  The geometry.
```

### 1.3 The correction mechanism

```
A prescription acoustic correction
for a cochlear false attractor requires
three simultaneous components:

COMPONENT 1 — Environmental reference:
  Pink noise floor with FA notched.
  Provides the auditory system with
  broadband acoustic reference.
  Prevents total silence, which
  worsens tinnitus perception by
  removing all competing input.
  FA is notched to avoid reinforcing
  the false attractor through the
  reference signal.

COMPONENT 2 — Anti-signal at FA:
  Sine wave at the false attractor
  frequency (FA), at the individual's
  calibrated cancellation phase.
  Provides destructive interference
  at the eigenfunction position of
  the false attractor.
  Phase is calibrated individually —
  not assumed to be 180° — because
  the cochlear travelling wave produces
  individual phase relationships at
  each eigenfunction position
  determined by the geometry of the
  specific damaged cochlea.

COMPONENT 3 — FR boost:
  Sine wave at the residual resonant
  frequency (FR) — the frequency at
  which the damaged cochlear zone
  retains remaining mechanical
  response capacity.
  Provides coherent real input for
  the navigator to track after the
  false attractor is displaced.
  Without this component, the navigator
  displaces the false attractor and
  immediately re-establishes it —
  the only stable structure in the
  damaged zone.
  With this component, the navigator
  has a real signal to track.

THE CRACKED VIOLIN PRINCIPLE:
  The reshaped world is the correctly
  tuned bow for a cracked violin —
  and the cracked violin, played with
  the right bow, still makes music.
  (Document 67, the_broken_instrument.md)
```

---

## PART II: THE THEORETICAL FRAMEWORK

### 2.1 Navigator principle

```
The auditory system does not passively
receive signal. It actively navigates
the acoustic eigenfunction space —
seeking coherent structure to lock onto.

When the dominant input at a cochlear
eigenfunction position is coherent
real-world signal: the navigator
tracks it. Normal hearing.

When coherent real-world signal is
absent from a cochlear zone (due to
hair cell damage): the navigator
finds the nearest available stable
structure. The eigenfunction position
of the damaged membrane. The false
attractor. Tinnitus.

The navigator does not stop.
It finds another way.

The false attractor is not a
malfunction of the navigator.
It is the navigator doing exactly
what it is designed to do —
finding the most coherent available
structure — in the absence of
real input.

BEANIE OBSERVATION
(Eric Robert Lawson, 2026-02-28):
  Placing a beanie over the ear induces
  tinnitus. Removing it immediately
  resolves it.

  The beanie creates a resonant air
  column at a cochlear eigenfunction-
  adjacent frequency.
  The navigator locks onto it.
  Remove the source: real environmental
  input floods the zone.
  The navigator immediately prefers
  real coherent input over the
  false attractor.
  Tinnitus dissolves in seconds.

  This demonstrates:
  1. False attractors form and dissolve
     at eigenfunction positions in a
     healthy cochlea.
  2. The navigator prefers real coherent
     input over the false attractor.
  3. The preference is immediate —
     not gradual, not requiring
     habituation or reorganisation.

The correction provides real coherent
input at the eigenfunction position.
The navigator prefers it.
While the correction is applied:
the false attractor is displaced.

BEANIE TIMING AMENDMENT
(Eric Robert Lawson, 2026-03-23):
  The beanie observation has a second
  implication, identified prior to
  first external session and therefore
  recorded here before empirical testing.

  The false attractor does not form
  immediately when the beanie is placed.
  It builds over several seconds.
  The false attractor does not dissolve
  immediately when the beanie is removed.
  It drains over several seconds.

  Both formation and dissolution have
  temporal lag. The lag is a property
  of attractor well depth:

    Deep wells (severe tinnitus,
    acute trauma):
      formation lag SHORT
      dissolution lag LONG

    Shallow wells (mild tinnitus):
      formation lag LONGER
      dissolution lag SHORT

  IMPLICATION FOR CALIBRATION:

  The original protocol asked for
  B/W/N feedback immediately when
  each calibration tone stopped.
  This was wrong. At tone offset,
  the person is at the beginning of
  the dissolution phase — maximum
  perceptual ambiguity, not maximum
  perceptual clarity.

  The corrected protocol:
    1. Tone plays for personalised
       duration (set from formation lag)
    2. 5-second post-tone settling
       window — effect may still be
       building after tone stops
    3. B/W/N feedback at settled
       perception
    4. Inter-trial interval confirmed
       by person (ENTER when back to
       baseline) — not a fixed timer

  ADDITIONAL INSIGHT:
  Dissolution time after each tone
  is a second feedback channel —
  objective, timeable, independent
  of subjective B/W/N accuracy.
  Longer dissolution = deeper
  attractor interaction = closer to
  FA eigenfunction position.
  This cross-validates B/W/N
  throughout the protocol.

  BEANIE PRE-CALIBRATION (Phase 0B):
  Formation and dissolution lag are
  measured individually at the start
  of each ear's session using manual
  occlusion (hand or beanie over ear).
  These measurements personalise
  tone duration and inter-trial
  timing for that individual's
  attractor dynamics before the
  sweep begins.

  This amendment does not change
  any prediction, claim, success
  criterion, or failure criterion.
  It corrects when feedback is
  requested and how inter-trial
  timing is set. The measurement
  targets, the three-layer remedy,
  the gradient descent logic, and
  the glasses principle are unchanged.
```

### 2.2 The central perpetuation question

```
THE OBJECTION:
  Long-duration tinnitus undergoes
  central reorganisation. The auditory
  cortex rewires around the absence
  of input from the damaged zone.
  The tinnitus becomes self-sustaining
  neurally, independent of the
  peripheral cochlear source.
  Therefore peripheral acoustic
  intervention cannot help.

THE RESPONSE:
  Central reorganisation preserves
  the eigenfunction geometry.
  The cortical hyperactivity is
  tonotopically organised — it is
  concentrated at the cortical
  representation of the damaged
  cochlear eigenfunction position.
  It did not escape the geometry.
  It is the geometry, neurally
  implemented.

  EMPIRICAL CONFIRMATION:
  The P4 result (χ² = 2328.1) is
  from a population of CHRONIC
  tinnitus patients.
  After years of central reorganisation,
  tinnitus pitch still clusters at
  cochlear eigenfunction positions.
  The geometry is preserved throughout
  the auditory pathway.

  COCHLEAR IMPLANT EVIDENCE:
  Cochlear implants in patients with
  profound long-duration deafness
  (20+ years of central reorganisation)
  frequently eliminate or dramatically
  reduce tinnitus.
  This should not occur if central
  perpetuation were truly independent
  of peripheral geometry.
  It occurs because providing coherent
  input at the eigenfunction positions
  gives the navigator something real
  to track. The cortical reorganisation
  reverses around the new coherent input.

  THE GLASSES REFRAME:
  Under the glasses principle, this
  entire debate is beside the point.

  Glasses do not ask whether the
  visual cortex has reorganised around
  the impaired lens.
  Glasses correct the structural
  mismatch at the interface.
  The experience is corrected while
  the correction is applied.
  Whether the cortex reorganises
  around the corrected signal is an
  interesting side effect.
  Not the goal. Not the measure of
  success.

  The measure of success is:
  While applied — does the experiencer
  perceive acoustic coherence instead
  of the false attractor?
  Yes or no.
```

### 2.3 Why duration of tinnitus does
### not change the claim

```
The glasses principle resolves the
duration question completely.

Glasses do not work differently
for someone who has had poor vision
for 2 years versus 20 years.
The structural correction is applied
to the current geometry of the
damaged instrument.
The experiencer sees correctly while
applied. Regardless of duration.

This protocol is applied to the
current geometry of the damaged
cochlea. The eigenfunction position
of the false attractor is calibrated
individually — from the actual
current state of the damaged
structure, not from assumptions about
what it should be.

The calibration finds what is there.
The correction addresses what is there.
Duration is a parameter of the
calibration (longer duration may
require more amplitude, more precise
phase calibration, longer dissolution
wait times between tones) but not a
parameter of whether the mechanism
operates.
```

---

## PART III: PRIOR ART SUMMARY

```
CLOSEST PRIOR ART:
  Abu Saquib Tauheed et al. (2018)
  "A Real-Time Sequential Phase-Shift
  Approach to Tinnitus Cancellation —
  A Pilot Study in Southern India"
  Global Journal of Otolaryngology
  Juniper Publishers

  Result: 7/7 tonal tinnitus patients
  reported relief during delivery.

  Why it did not become a product:
  No theoretical framework explaining
  the mechanism. No eigenfunction map.
  No FA/FR distinction. No gradient
  descent calibration. Static 180°
  phase assumption. Relief temporary
  because no FR boost provided
  replacement coherent input.
  The prior work found the door.
  This framework explains where it goes.

WHAT IS NOVEL IN THIS FRAMEWORK:
  1. Eigenfunction foundation:
     Tinnitus pitch is determined by
     the physical geometry of the
     cochlear resonating structure.
     Confirmed empirically by P4
     (χ² = 2328.1, n = 1514).

  2. FA/FR distinction:
     False attractor frequency (FA)
     ≠ residual resonant frequency (FR).
     FA is where the tinnitus rings.
     FR is where the damaged structure
     can still be driven by external
     signal. Cancelling FA without
     driving FR produces temporary
     displacement only. Driving FR
     simultaneously provides the
     navigator with real input to
     track — the mechanism of
     durable correction while applied.

  3. Individual gradient descent
     calibration:
     Patient-guided directional feedback
     (B/W/N) navigates eigenfunction
     space toward the calibration
     optimum. Not static pitch matching.
     Adapts to individual cochlear
     geometry. Self-administrable.

  4. Individual phase calibration:
     The cancellation phase is not
     assumed to be 180°. It is measured
     for this individual's cochlea at
     this eigenfunction position.

  5. Glasses principle:
     The protocol is correctly framed
     as structural correction — not
     treatment, not cure, not therapy.
     Applied: corrected.
     Removed: tinnitus returns.
     Exactly as with glasses.
     This framing eliminates false
     expectations and clarifies the
     correct measure of success.

  6. Three-layer delivery signal:
     Pink noise floor (FA notched)
     + anti-signal at FA (calibrated
     phase) + FR boost.
     This specific combination is not
     in any prior literature.

  7. Attractor temporal dynamics
     (beanie timing amendment):
     Formation lag and dissolution lag
     are individually measured before
     calibration begins and used to
     personalise tone duration and
     inter-trial timing. Dissolution
     time after each tone is treated
     as a second objective feedback
     channel throughout all phases.
     This correction to calibration
     timing is not in any prior
     literature.
```

---

## PART IV: PRE-STATED PREDICTIONS

### 4.1 Primary prediction

```
PREDICTION P-OC-001:
  When the calibrated three-layer
  acoustic correction is delivered
  to an individual with tonal tinnitus
  of cochlear origin, at the calibrated
  FA, phase, and FR values for that
  individual's ear:

  The individual will report that
  tinnitus is less perceptible during
  delivery than without the correction.

  This is the glasses test:
  Correction applied → experience
  corrected.

FALSIFICATION CRITERION:
  The individual reports no detectable
  difference in tinnitus perception
  during delivery versus without
  correction, after correct calibration
  (FA confirmed by gradient descent
  convergence, phase confirmed by
  phase sweep, volume confirmed
  above perceptual threshold).

  If this occurs: either the cochlear
  mechanical component is absent
  (central perpetuation has fully
  replaced peripheral source) or
  the calibration has a parameter
  error. The dissolution time data
  from Phase 0B distinguishes these:
  absent dissolution response in
  beanie pre-calibration suggests
  mechanism failure; present
  dissolution response with absent
  B/W/N clarity suggests parameter
  error.
```

### 4.2 Secondary predictions

```
PREDICTION P-OC-002:
  The calibrated FA will fall in the
  4–10 kHz zone for an individual
  with acute acoustic trauma tinnitus
  from high-RPM construction equipment.

  BASIS: P4 result. 61.6% of tinnitus
  cases cluster in this zone.
  Acute broadband acoustic trauma
  concentrates damage in the zone of
  steepest stiffness gradient.
  Peak enrichment is 4.86× at 8–10 kHz.

PREDICTION P-OC-003:
  Bilateral tinnitus from a single
  acoustic trauma event will calibrate
  to different FA values in each ear,
  reflecting the asymmetric nature of
  the acoustic exposure (sequential
  rather than simultaneous damage).

PREDICTION P-OC-004:
  Sleep onset will be faster and
  sleep quality improved on nights
  when the correction is applied,
  compared to nights without.

  BASIS: Tinnitus is most perceptible
  in quiet environments. Sleep onset
  is a quiet environment. The correction
  removes the dominant intrusive
  percept at the point of maximum
  intrusion.

PREDICTION P-OC-005:
  The individual phase calibration
  will find an optimal cancellation
  phase that differs from 180° for
  at least one ear.

  BASIS: The cochlear travelling wave
  produces individual phase
  relationships at each eigenfunction
  position. 180° is the assumption
  of standard ANC. The geometry
  predicts individual variation.

PREDICTION P-OC-006:
  FR will differ from FA by a
  measurable amount in at least
  one ear (the cracked violin case).

  BASIS: Outer hair cell damage shifts
  the mechanical tuning of the affected
  cochlear zone. The false attractor
  and the residual resonant capacity
  are properties of the same damaged
  structure but are not identical.
  The FA is where the structure rings
  spontaneously. The FR is where it
  can still be driven. These are
  adjacent but not equal in the
  majority of damage cases.

PREDICTION P-OC-007:
  Beanie pre-calibration (Phase 0B)
  will show shorter formation lag
  and longer dissolution lag for the
  more severely damaged ear (the ear
  that popped first).

  BASIS: Deeper attractor wells fill
  faster and drain slower. The first
  ear to receive acoustic trauma is
  predicted to have more severe
  damage and therefore a deeper
  false attractor well at the
  eigenfunction position.
  Asymmetric formation and dissolution
  dynamics between ears is expected
  and predicted by the attractor
  depth model.
```

### 4.3 What success looks like

```
MINIMUM (floor — first night):
  The individual reports that tinnitus
  is less intrusive while the correction
  is playing before sleep onset.

  This is the direct glasses test.
  Correction applied. Experience
  corrected. Immediate. Verifiable.

MODERATE:
  The individual reports faster sleep
  onset on the first night compared
  to their normal baseline.
  The individual reports the tinnitus
  as less dominant on waking compared
  to normal waking baseline.

STRONG:
  The above, sustained over multiple
  nights of consistent use.
  The individual describes the
  correction as part of their
  sleep routine — like glasses as
  part of a visual routine.

NOT A SUCCESS CRITERION:
  Tinnitus reduction after correction
  is removed.
  Permanent improvement.
  Cure.

  These are not claimed.
  These are not expected.
  These are not the measure.

  The measure is:
  While applied — corrected or not?
```

### 4.4 What failure means

```
PARAMETER FAILURE (addressable):
  Correction makes tinnitus worse
  during delivery.
  → Phase is wrong. Anti-signal is
    reinforcing the false attractor.
  → Re-run phase calibration.
  → Rotate phase 90° and retest.

  Correction produces no effect.
  Volume confirmed above threshold.
  → Amplitude insufficient to compete
    with deep false attractor.
  → Increase amplitude and retest.

  Correction effective initially,
  fades within one night.
  → FA drift during night.
  → Re-calibrate. Consider adaptive
    tracking (Level 2 development).

  B/W/N feedback consistently
  inconsistent despite long tones
  and confirmed baseline between
  trials.
  → Check Phase 0B dissolution
    response. If dissolution response
    is present, feedback quality is
    the issue — coach more carefully
    on what "better" means. If
    dissolution response is absent,
    see mechanism failure below.

MECHANISM FAILURE (informative):
  Full protocol correctly administered.
  No response at any phase or amplitude.
  Phase 0B shows no formation or
  dissolution response to beanie
  occlusion.
  → Cochlear mechanical component
    is absent or minimal.
  → Central perpetuation has fully
    replaced peripheral source for
    this ear.
  → Glasses cannot correct a cochlea
    that has no remaining mechanical
    response. The instrument is not
    merely cracked — it is gone.
  → TMNMT (cortical plasticity route)
    is the appropriate alternative.

IMPORTANT:
  Mechanism failure for one ear does
  not predict mechanism failure for
  the other. Independent calibration
  per ear is essential.
  Bilateral tinnitus from sequential
  trauma may have different cochlear
  mechanical status in each ear.
```

---

## PART V: THE PROTOCOL

```
Full protocol documented in:
  tinnitus_calibration.py
  OC-TINNITUS-001_SELF_ADMINISTRATION_
    GUIDE.md
  tinnitus_trial_protocol.md
    (Document 68)

Summary (Version 1.1 — beanie
timing amendment applied):

  PHASE 0A — Volume calibration
    Confirm tones audible and comfortable.
    Adjust AMPLITUDE until reference
    tone clearly perceptible.
    For severe tinnitus cases:
    start at AMPLITUDE = 0.15.

  PHASE 0B — Beanie pre-calibration
    [ADDED IN VERSION 1.1]
    Measure formation lag and dissolution
    lag of individual false attractor
    using manual ear occlusion.
    Formation lag: time from occlusion
      onset to first perceptible change.
      Sets minimum tone duration.
      Tone duration = max(formation_lag
      × 2.5, 15 seconds).
    Dissolution lag: time from occlusion
      removal to return to baseline.
      Sets inter-trial timing expectation.
      Inter-trial interval is
      person-confirmed (not fixed timer)
      throughout all subsequent phases.
    Output: formation_lag_s,
      dissolution_lag_s, tone_duration_s

  TIMING PROTOCOL — all phases
    [CORRECTED IN VERSION 1.1]
    Every tone in every phase follows:
      1. Tone plays (personalised duration)
      2. 5-second post-tone settling window
         (effect may still be building —
          feedback not requested yet)
      3. B/W/N feedback
      4. Person confirms baseline restored
         before next tone (ENTER)
      5. Dissolution time logged —
         second objective feedback channel
    This replaces the original fixed
    timing and immediate post-tone
    feedback request.

  PHASE 1 — Rainbow sweep
    12 tones at Greenwood-spaced
    cochlear eigenfunction positions.
    One ear at a time.
    Feedback: B / W / N per tone.
    Dissolution time logged per tone.
    Builds eigenfunction landscape map
    with both subjective and objective
    channels.
    Identifies gradient starting region.

  PHASE 2 — Gradient descent
    Patient-guided navigation toward
    FA from rainbow sweep starting point.
    Step size halves on direction change.
    Convergence: 3× B with step < 8 Hz.
    Dissolution time cross-validates
    convergence: consistently long
    dissolution at B = structural
    confirmation of FA position.
    Manual lock available at any point.
    Output: FA (false attractor Hz)

  PHASE 3 — Phase calibration
    8-point coarse sweep (0–315° in 45°)
    Fine sweep ±40° around best phase.
    Feedback: B / W / N per angle.
    Dissolution time used as tiebreaker
    when B/W/N scores are equal.
    Output: cancellation phase (°)

  PHASE 4 — FR sweep
    Anti-signal at FA active throughout.
    Test frequencies FA ± 400 Hz in
    13 steps.
    Dissolution time cross-validates
    FR identification.
    Output: FR (residual resonant Hz)

  PHASE 5 — Orthogonal re-sweep
    Rainbow sweep repeated with FA
    anti-signal active continuously.
    Checks for residual gradient in
    other eigenfunction dimensions.
    Dissolution times logged throughout.
    Output: converged (T/F)
    If not converged: second gradient
    descent from new B cluster.

  PHASE 6 — WAV generation
    Three-layer remedy file generated
    from calibrated parameters.
    Per-ear files + binaural combined.
    Default duration: 60 minutes.
    Player set to loop.
    Volume during sleep: barely audible.
```

---

## PART VI: FIRST EXTERNAL SESSION
## PARAMETERS

```
Subject profile (pre-session):
  Relationship to administrator:
    nephew (Eric Robert Lawson's
    network — not ERL himself)
  Tinnitus type: bilateral
  Onset: acute acoustic trauma
  Mechanism: high-RPM construction
    saw blade
  Onset character: remembered —
    heard ears pop, one then the other
  Duration: unknown at preregistration
    (to be recorded at session)
  Severity: extreme (self-reported)
  Prior treatment: unknown
    (to be recorded at session)

Pre-session questions to record:
  1. Duration since onset (years)
  2. Tonal / noise-like / mixed
  3. Which ear popped first
  4. Does noise environment reduce
     tinnitus? (peripheral vs central
     indicator)
  5. Any prior medical evaluation?

Protocol adjustments for this case:
  Start AMPLITUDE = 0.15
  Begin with worse ear (first to pop)
  Over-ear headphones — confirmed
    left/right channel isolation
  5-minute rest enforced between ears
  Orthogonal re-sweep treated as
    mandatory (broadband trauma may
    produce multi-component tinnitus)

Expected Phase 0B result for this case:
  Acute severe trauma predicts:
    Formation lag SHORT (deep well
      fills fast)
    Dissolution lag LONG (deep well
      drains slow)
    Asymmetric between ears (first ear
      to pop expected deeper well)
  This is now a pre-stated prediction
  (P-OC-007 above).
  Record actual values and compare.

Session record document:
  OC-TINNITUS-002_FIRST_EXTERNAL_
    SESSION.md
  (to be created after session)
  Contents:
    Pre-session answers
    Phase 0B beanie calibration values
      (formation lag, dissolution lag,
       tone duration — per ear)
    Per-ear calibration values
    Gradient descent history with
      dissolution times
    Phase sweep responses with
      dissolution times
    FR sweep responses with
      dissolution times
    Orthogonal sweep result
    First-night report
    Administrator observations
```

---

## PART VII: WHAT THIS IS IN THE
## FRAMEWORK

```
This protocol sits within the
OrganismCore qualia_candidate_axioms
Cross-Substrate Verification series
at the following position:

  The cochlea is a bounded resonating
  structure with eigenfunction positions
  determined by its geometry.

  This is the same principle as:
    — the electric tonnetz
      (weakly electric fish)
    — the spermaceti tonnetz
      (sperm whale)
    — the waggle dance tonnetz
      (honeybee)

  In every case: a bounded resonating
  structure, eigenfunction positions
  determined by geometry, the navigator
  orienting within that structure.

  Tinnitus is what happens when a
  navigator cannot find real coherent
  structure in a damaged zone and
  locks onto the nearest stable
  eigenfunction position of the
  physical structure instead.

  The correction is what happens when
  you give the navigator real coherent
  structure at that position.

  The navigator prefers it.
  Every time.
  Regardless of substrate.
  Regardless of whether the false
  attractor is mechanical or neural.
  Regardless of duration.

  This is the navigator principle
  in acoustic space.
  The protocol is its first clinical
  application.
```

---

## PART VIII: THE HONEST LIMITS

```
THIS PROTOCOL CLAIMS:
  For tonal tinnitus of cochlear origin
  with detectable residual inhibition
  (confirmed by Phase 0B dissolution
  response): acoustic correction while
  applied.
  Structural. Not therapeutic.
  Like glasses.

THIS PROTOCOL DOES NOT CLAIM:
  Cure.
  Lasting improvement after removal.
  Reversal of cochlear damage.
  Replacement for medical evaluation.
  Efficacy for noise-like/broadband
    tinnitus without tonal component.
  Efficacy where cochlear mechanical
    component is fully absent (no
    Phase 0B dissolution response).

THIS PROTOCOL CANNOT BE JUDGED BY:
  Whether tinnitus returns when
  the correction is removed.
  (Glasses cannot be judged by whether
  vision is impaired when they are
  removed. That is the correct and
  expected result.)

THIS PROTOCOL CAN BE JUDGED BY:
  While applied to a correctly
  calibrated individual with tonal
  tinnitus of cochlear origin —
  does the individual perceive
  acoustic coherence instead of
  the false attractor?

  Yes or no.
  That is the only measure.
```

---

## PART IX: DOCUMENT CHAIN

```
THEORETICAL FOUNDATION:
  Document 65 — convergent_sensory_
    topology.md
  Document 66 — tinnitus_eigenfunction_
    mapping_and_therapy.md
  Document 67 — the_broken_instrument.md
  Document 68 — tinnitus_trial_
    protocol.md

EMPIRICAL FOUNDATION:
  P4_results.md
  p4_tinnitus_eigenfunction_analysis.py
  OHSU Tinnitus Archive, Data Set 1
  n = 1514, 1981–1994

LITERATURE SWEEP:
  OC-TINNITUS-001_LITERATURE_SWEEP_V1.md

PROTOCOL IMPLEMENTATION:
  tinnitus_calibration.py
  OC-TINNITUS-001_SELF_ADMINISTRATION_
    GUIDE.md

THIS DOCUMENT:
  OC-TINNITUS-001_PREREGISTRATION.md

NEXT DOCUMENT:
  OC-TINNITUS-002_FIRST_EXTERNAL_
    SESSION.md
  (created after first external session)
```

---

## VERSION

```
version: 1.1
date_original: 2026-03-23
date_amended:  2026-03-23
status: LOCKED — preregistration
  Version 1.1 amendment applied same
  day as original, prior to first
  external session.

WHAT CHANGED IN VERSION 1.1:

  ADDED:
    Phase 0B — Beanie Pre-Calibration.
    Formation lag and dissolution lag
    measurement by manual occlusion.
    Personalised tone duration from
    formation lag.
    Person-confirmed inter-trial
    interval (not fixed timer).
    Dissolution time as second feedback
    channel throughout all phases.
    Prediction P-OC-007 (asymmetric
    attractor depth between ears).
    Expected Phase 0B result for first
    external session subject.
    Phase 0B values added to session
    record document specification.
    Phase 0B dissolution response added
    as mechanism failure diagnostic.

  CORRECTED:
    Timing protocol for all phases:
    post-tone settling window before
    feedback, person-confirmed baseline
    between trials.
    Session duration estimate updated
    to 45–60 minutes.
    Falsification criterion for P-OC-001
    updated to reference Phase 0B
    dissolution response as diagnostic.
    Duration as calibration parameter
    updated to note longer dissolution
    wait times for severe cases.

  UNCHANGED:
    All predictions except P-OC-007
    (which is new, not modified).
    Core claims.
    Glasses principle.
    Success criteria.
    Failure criteria (parameter and
    mechanism — mechanism failure
    criterion updated only to add
    Phase 0B as diagnostic, not to
    change what constitutes failure).
    Three-layer remedy specification.
    WAV generation.
    Framework position.
    Honest limits.

BASIS FOR AMENDMENT:
  Beanie observation extended
  (Eric Robert Lawson, 2026-03-23):
  The false attractor does not form
  or dissolve instantaneously.
  Placing a beanie does not produce
  tinnitus immediately.
  Removing it does not stop tinnitus
  immediately.
  Both have temporal lag.
  This lag must be measured individually
  before calibration begins.
  Feedback requested at tone offset
  (original protocol) is feedback at
  maximum perceptual ambiguity.
  This amendment corrects that.
  The amendment is methodological.
  It does not change what is being
  measured — only when and how
  the measurement is taken.

This document records the state of
the theoretical framework, predictions,
protocol, and success criteria as of
2026-03-23, prior to first external
administration.

The session results are recorded
separately in OC-TINNITUS-002.

The empiricism will dictate.
```

---

*The damage is permanent.*
*The false attractor remains.*
*Remove the correction: tinnitus returns.*
*Exactly as expected.*
*Exactly as with glasses.*

*This is not a treatment.*
*This is not a cure.*

*This is a structural correction*
*applied at the interface between*
*the world and the broken instrument.*

*While applied: the broken instrument*
*receives the signal it can no longer*
*produce for itself.*

*The experiencer hears.*

*That is sufficient.*
*That is the point.*
*That is all that is claimed.*
