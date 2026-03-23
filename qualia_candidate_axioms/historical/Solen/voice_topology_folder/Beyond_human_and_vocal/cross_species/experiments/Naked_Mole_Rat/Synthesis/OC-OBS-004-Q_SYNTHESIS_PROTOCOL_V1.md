# OC-OBS-004-Q — CALIBRATION, SYNTHESIS AND FIRST CONTACT
## Universal Protocol for Naked Mole-Rat Colony Identity Synthesis
## OrganismCore — Eric Robert Lawson
## Document date: 2026-03-23
## Status: PROTOCOL LOCKED — ready for laboratory execution

---

## PREAMBLE

This document records the transition from observational analysis
to active synthesis. The observational phase (OC-OBS-004,
OC-OBS-004-Q V1, OC-OBS-004-Q V2) is complete and has
produced the following confirmed findings:

1. Each naked mole-rat colony has a distinct acoustic identity
   (colony dialect) that lives at a specific position in
   eigenfunction space — the worker centroid.

2. The queen is not the dialect. She is the peripheral anchor
   that stabilises it. Workers orient toward her without
   occupying her position.

3. The worker centroid is the synthesis target. A signal
   placed at that position should be received by the colony
   as acoustically consistent with membership.

4. The baratheon colony's worker centroid has been mapped:
   PC1: −1.45  PC2: −2.00  PC3: −0.52  PC4: +0.25
   Predicted peak frequency: 517 Hz
   Predicted duration: ~190 ms

5. The method for identifying the queen and computing the
   worker centroid generalises to any NMR colony with
   sufficient recording data.

This protocol documents how to execute calibration, synthesis,
and first contact for any target colony.

---

## PART I: THE UNIVERSAL PROTOCOL
## Applicable to any NMR colony

The protocol has three phases executed in sequence.
Each phase has a confirmation gate. Do not proceed to
the next phase until the gate is passed.

---

### PHASE 0 — RECORDING AND CALIBRATION
### What you need before you can synthesize anything

**Objective:** Obtain sufficient softchirp recordings from
the target colony to fit the eigenfunction space and identify
the worker centroid.

#### Minimum recording requirements

```
Minimum sessions:     6 recording sessions
Minimum animals:      3 individually identifiable animals
Minimum dates:        3 separate calendar dates
                      (spread across ≥ 4 weeks if possible)
Minimum chirps:       200 individual-valid softchirps
                      (chirps from known single-animal sessions)
Preferred:            10+ sessions, 5+ animals, 8+ dates
                      (baratheon-level coverage)

Recording format:
  Sample rate:    22,050 Hz minimum (44,100 Hz preferred)
  Bit depth:      16-bit minimum (24-bit preferred)
  Channel:        Mono per animal OR stereo dual-channel
                  (filename must encode animal ID per
                   Barker 2021 convention)
  Microphone:     Contact microphone or directional mic
                  placed in colony tunnel
  Duration:       Minimum 10 minutes per session
  Condition:      Colony undisturbed, normal social activity
```

#### Animal identification requirement

Individual animals must be identifiable across sessions.
Acceptable methods:
- Subcutaneous RFID tag (preferred)
- Colour-coded tail mark (non-toxic, renewed per session)
- Ear notch (permanent, used in Barker 2021)
- Microphone channel assignment (Barker 2021 method)

The queen identification algorithm requires individual
identity to be resolvable from the filename or metadata.
Without individual identity, queen identification is
impossible and the protocol reduces to colony-level
dialect mapping only (sufficient for synthesis, insufficient
for queen identification).

#### Phase 0 confirmation gate

Run `nmr_analysis_004.py --data_dir [your_data_dir]`

Gate criteria:
```
✓ Individual-valid chirps ≥ 200
✓ Colony breakdown shows ≥ 3 animals
✓ Colony breakdown shows ≥ 3 dates
✓ M1 queen candidate identified with confidence MODERATE or CLEAR
✓ Worker centroid computed (reported in M11)
✓ Synthesis target frequency reported (NOVEL-1 peak frequency)
```

If gate fails: record more sessions. The protocol cannot
proceed without a stable worker centroid.

---

### PHASE 1 — EIGENFUNCTION MAPPING AND SYNTHESIS SPECIFICATION
### Computing the synthesis target

**Objective:** Extract the precise eigenfunction coordinates
of the colony's worker centroid and convert those coordinates
to acoustic synthesis parameters.

#### Step 1.1 — Run the analysis pipeline

```bash
python nmr_analysis_004.py \
    --data_dir [colony_recording_dir] \
    --sample_rate 22050 \
    --n_perms 1000
```

Record from the M11 output:

```
Queen candidate:         Animal [ID]
Worker centroid:
  PC1: [value]
  PC2: [value]
  PC3: [value]
  PC4: [value]
Predicted peak frequency: [value] Hz
Predicted centroid:       [value] Hz
Queen position:
  PC1: [value]
  ...
Vector queen → workers:   magnitude [value]
```

#### Step 1.2 — Extract synthesis parameters

From the M11 output and M3 duration asymmetry results,
compile the synthesis parameter set:

```
SYNTHESIS PARAMETER SET
─────────────────────────────────────────────────────
Colony:              [name]
Queen candidate:     Animal [ID]

TARGET POSITION:
  Eigenfunction:     [PC1, PC2, PC3, PC4]

ACOUSTIC PARAMETERS (from inverse PCA projection):
  Fundamental (F0):  [peak_freq] Hz   ← primary carrier
  Spectral centroid: [centroid] Hz
  Duration:          [mean_worker_duration] ms
  F0 slope:          ~0 Hz/ms         ← nearly flat (softchirp)
  Spectral entropy:  low (0.55–0.65)  ← tonal, not noisy
  Amplitude env:     gaussian
    Rise time:       ~20 ms
    Fall time:       ~20 ms
  Harmonic content:  low–moderate
    H2/H1 ratio:     ~0.3
    H3/H1 ratio:     ~0.1

DELIVERY PARAMETERS:
  SPL at 1m:         70 dB
  Frequency range:   500 Hz – 4 kHz
  Bandwidth:         ≥ 3.5 kHz usable
─────────────────────────────────────────────────────
```

#### Step 1.3 — Synthesize the calibration chirp

The synthesis target is a tonal signal with the following
structure. This can be generated in Python:

```python
import numpy as np
from scipy.io import wavfile

def synthesize_colony_chirp(
        f0_hz,
        duration_ms,
        sample_rate=44100,
        h2_ratio=0.30,
        h3_ratio=0.10,
        rise_ms=20,
        fall_ms=20):
    """
    Synthesize a soft chirp at the colony's worker centroid.

    Parameters
    ----------
    f0_hz       : float  — fundamental frequency (Hz)
                           from M11 predicted peak frequency
    duration_ms : float  — chirp duration (ms)
                           from M3 mean worker duration
    sample_rate : int    — output sample rate
    h2_ratio    : float  — H2 amplitude relative to H1
    h3_ratio    : float  — H3 amplitude relative to H1
    rise_ms     : float  — gaussian envelope rise (ms)
    fall_ms     : float  — gaussian envelope fall (ms)

    Returns
    -------
    signal : np.ndarray  — normalised audio signal
    """
    n_samples = int(duration_ms * sample_rate / 1000)
    t         = np.linspace(0, duration_ms / 1000,
                             n_samples, endpoint=False)

    # Harmonic stack — H1 + H2 + H3
    signal = (
        np.sin(2 * np.pi * f0_hz * t) +
        h2_ratio * np.sin(2 * np.pi * 2 * f0_hz * t) +
        h3_ratio * np.sin(2 * np.pi * 3 * f0_hz * t)
    )

    # Gaussian amplitude envelope
    centre   = duration_ms / 2
    sigma_r  = rise_ms / 2
    sigma_f  = fall_ms / 2
    t_ms     = t * 1000
    envelope = np.where(
        t_ms <= centre,
        np.exp(-0.5 * ((t_ms - centre) / sigma_r) ** 2),
        np.exp(-0.5 * ((t_ms - centre) / sigma_f) ** 2)
    )

    signal = signal * envelope
    signal = signal / (np.max(np.abs(signal)) + 1e-10)
    return signal


# BARATHEON COLONY — from OC-OBS-004-Q V2 results
chirp_baratheon = synthesize_colony_chirp(
    f0_hz       = 517,
    duration_ms = 190,
    sample_rate = 44100
)
wavfile.write("baratheon_colony_chirp_NOVEL1.wav",
              44100,
              (chirp_baratheon * 32767).astype(np.int16))
```

#### Step 1.4 — Validate the synthesized chirp

Before any delivery to a colony, run the synthesized
chirp through the analysis pipeline to confirm it maps
to the intended eigenfunction position:

```python
# Load the synthesized wav
# Run through compute_features() from nmr_analysis_004.py
# Project through the fitted PCA
# Confirm projected position is within 1σ of worker centroid
# Confirm peak frequency matches predicted

# Gate: synthesized chirp must project within 1σ of
# worker centroid in PC1-PC4 space.
# If not: adjust f0_hz and h2_ratio and retest.
```

**Phase 1 confirmation gate:**

```
✓ Synthesis parameter set compiled
✓ Chirp synthesized as .wav file
✓ Synthesized chirp projects within 1σ of worker centroid
  in eigenfunction space
✓ Peak frequency within ± 50 Hz of predicted
✓ Duration within ± 20 ms of colony mean
```

---

### PHASE 2 — DELIVERY SYSTEM
### Getting the signal into the colony

**Objective:** Deliver the synthesized chirp to a live
colony under conditions that permit behavioural measurement.

#### Delivery hardware specification

```
Speaker:
  Type:            Full-range miniature speaker
                   (e.g. Dayton Audio CE Series 30mm)
  Frequency range: 300 Hz – 8 kHz (−3 dB)
  SPL capability:  ≥ 80 dB at 0.1m
  Size:            ≤ 35mm diameter
                   (must fit in colony tunnel)
  Housing:         Sealed, humidity-resistant
                   (colony humidity ~80–95%)

Amplifier:
  Output:          1–5W class D
  Frequency resp:  flat ± 3 dB, 300 Hz – 8 kHz
  Control:         Raspberry Pi GPIO or Arduino DAC
                   (for programmable playback sequencing)

Placement:
  Location:        Secondary tunnel, not main nest chamber
  Distance:        Minimum 10 cm from nearest animal
  Orientation:     Speaker face directed toward main colony
  SPL at delivery: 65–75 dB at 5 cm
                   (within natural NMR vocalisation range)
```

#### Delivery protocol

```
SESSION STRUCTURE:
  Baseline period:     5 minutes passive recording
                       (no playback)
  Stimulus A:          Colony chirp (NOVEL-1)
                       3 repetitions × 500 ms gap
  Inter-stimulus gap:  60 seconds silence
  Stimulus B:          Foreign colony chirp
                       (baratheon → use martell worker centroid)
                       3 repetitions × 500 ms gap
  Inter-stimulus gap:  60 seconds silence
  Stimulus A repeat:   Colony chirp again (order control)
  Post period:         3 minutes passive recording

RESPONSE MEASUREMENT:
  Metric 1:  Antiphonal response rate
             (chirps per minute within 10s of stimulus)
  Metric 2:  Approach behaviour
             (number of animals within 5cm of speaker
              within 30s of stimulus)
  Metric 3:  Latency to first response
             (seconds from stimulus onset to first chirp)

CONTROL CONDITIONS:
  Control 1: Silence (no speaker, no signal)
  Control 2: Tone at non-colony frequency (e.g. 2000 Hz pure tone)
  Control 3: White noise burst (same duration, same SPL)
  Control 4: Foreign colony chirp (same duration, different F0)
```

#### Phase 2 confirmation gate

```
✓ Speaker placed and SPL verified at 70 dB at 5 cm
✓ Recording microphone placed to capture both
  speaker output and colony response
✓ Control conditions defined and counterbalanced
✓ At least 3 naive sessions planned
  (colony has not heard the synthesized chirp before)
✓ Baseline response rates measured (passive recording)
```

---

### PHASE 3 — FIRST CONTACT
### The experiment

**Objective:** Determine whether the synthesized chirp at
the worker centroid elicits a colony-appropriate
antiphonal response significantly above the foreign-colony
chirp control.

#### Definition of success (Milestone 0)

```
MILESTONE 0 — FIRST CONTACT CONFIRMATION:

The colony identity synthesis is confirmed when:

  Antiphonal response rate to NOVEL-1 (colony chirp)
  is significantly greater than antiphonal response rate
  to CONTROL-4 (foreign colony chirp)

  Statistical threshold:
    Mann-Whitney U, one-tailed
    p < 0.05 across ≥ 3 independent sessions
    Effect size: response rate ratio ≥ 1.5×

  Secondary confirmation:
    Approach behaviour to NOVEL-1 > CONTROL-4
    Latency to first response shorter for NOVEL-1

The synthesized signal is behaving as a colony member
signal. The colony is responding to it as "one of us."
```

#### What failure means

```
FAILURE MODES AND INTERPRETATIONS:

Failure type 1: No response to either stimulus
  Interpretation: Delivery system problem.
                  Check SPL, speaker placement, frequency response.
                  Colony may not be hearing the signal.
  Action: Verify speaker output with calibrated microphone.
          Increase SPL. Move speaker closer.

Failure type 2: Equal response to NOVEL-1 and CONTROL-4
  Interpretation: The eigenfunction position is not
                  the correct synthesis target, OR
                  the inverse PCA projection does not
                  faithfully recover the acoustic parameters.
  Action: Verify synthesized chirp projects correctly
          in eigenfunction space.
          Try NOVEL-2 (midpoint between worker centroid
          and queen position) as alternative target.

Failure type 3: Higher response to CONTROL-4 than NOVEL-1
  Interpretation: Worker centroid may not be the primary
                  recognition target, OR queen's position
                  (not worker centroid) is what the colony
                  attends to.
  Action: Test queen's eigenfunction position as target.
          Note: this would require revising the geometric model.

Failure type 4: High response to all stimuli equally
  Interpretation: Colony is responding to acoustic
                  novelty in general, not colony identity.
  Action: Use silence control and white noise control
          to establish non-specific arousal baseline.
          Require response to NOVEL-1 > noise floor
          AND > white noise control.
```

#### Session planning

```
Minimum experiment design:
  Sessions:     6 per colony (3 naive + 3 repeat)
  Animals:      All colony members present (do not isolate)
  Time of day:  Active period for the colony
                (NMR are largely arrhythmic but
                 prefer social activity in late afternoon)
  Interval:     ≥ 48 hours between sessions
                (prevents habituation within experiment)

Counterbalancing:
  Session 1:   A B (colony chirp first)
  Session 2:   B A (foreign chirp first)
  Session 3:   A B
  Session 4:   B A
  ...
  (ABBA counterbalancing across sessions)
```

---

## PART II: BARATHEON COLONY — SPECIFIC PARAMETERS
## From OC-OBS-004-Q V2 — ready to execute

The baratheon colony analysis is complete. All parameters
below are taken directly from the V2 results document
(OC-OBS-004-Q_V2_RESULTS.md) and are ready for use
without further analysis.

```
BARATHEON COLONY — SYNTHESIS PARAMETERS
─────────────────────────────────────────────────────────
Queen candidate:     Animal 2197   (CLEAR confidence, 0.9632)
Analysis date:       2026-03-23
Script:              nmr_analysis_004.py
Pre-registration:    OC-OBS-004-Q_BIOLOGY_INFORMED_
                     PREREGISTRATION_V2.md

SYNTHESIS TARGET — NOVEL-1 (worker centroid):
  PC1: −1.4527
  PC2: −2.0011
  PC3: −0.5212
  PC4: +0.2527
  Peak frequency:    517 Hz
  Spectral centroid: 2058 Hz
  Duration:          190 ms  (mean worker duration)
  Synthesis:         synthesize_colony_chirp(517, 190)

QUEEN POSITION (reference only — NOT synthesis target):
  PC1: +4.6093
  PC2: −1.1439
  PC3: +0.2492
  PC4: +2.6233
  Peak frequency:    [queen-specific — do not synthesize]
  Duration:          208 ms

QUEEN-TO-WORKER VECTOR:
  PC1: −6.0620
  PC2: −0.8572
  PC3: −0.7704
  PC4: −2.3705
  Magnitude: 6.6102

CONFIRMED PREDICTIONS:
  P2  Duration asymmetry:    CONFIRMED   p = 0.000001
  P3  Peripheral position:   CONFIRMED   rank 1/5
  P5  Longitudinal stability: CONFIRMED  rank 1/5
  P7  Queen separation:      CONFIRMED   81.5th pctile
  P_DIRECTION  Workers orient toward queen: CONFIRMED
                             alignment = 0.86

CONTROL CHIRP — use martell worker centroid from
OC-OBS-004 V2 analysis (re-run nmr_analysis_004.py
on martell data to obtain exact parameters).
─────────────────────────────────────────────────────────
```

---

## PART III: THE GENERAL PROTOCOL
## Steps for any new colony

This is the repeatable procedure. Follow these steps
for any NMR colony starting from zero.

```
STEP 1 — RECORD
  Minimum 6 sessions, 3 dates, 200 individual-valid chirps
  Individual animal identity must be encoded in filenames
  Format per Barker 2021 convention

STEP 2 — ANALYSE
  python nmr_analysis_004.py --data_dir [your_data]
  Confirm M1 queen candidate (MODERATE or CLEAR confidence)
  Record M11 worker centroid and predicted peak frequency

STEP 3 — SYNTHESIZE
  Call synthesize_colony_chirp(f0_hz, duration_ms)
  where f0_hz = M11 predicted peak frequency
  and duration_ms = M3 mean worker duration
  Save as [colony]_NOVEL1.wav

STEP 4 — VALIDATE
  Load synthesized chirp through nmr_analysis_004.py
  Confirm it projects within 1σ of worker centroid
  Adjust f0_hz ± 20 Hz if needed and revalidate

STEP 5 — BUILD CONTROL
  Repeat Steps 1–4 for a second colony
  The second colony's NOVEL-1 is your foreign control
  Or: use published baratheon parameters (above)
  as the foreign control for any non-baratheon colony

STEP 6 — DELIVER
  Mount speaker in secondary tunnel
  Calibrate SPL to 70 dB at 5 cm
  Confirm colony is undisturbed and socially active
  Run baseline passive recording (5 minutes)

STEP 7 — FIRST CONTACT SESSION
  Play NOVEL-1 (3 repetitions)
  60 second gap
  Play foreign control (3 repetitions)
  Record all colony vocalisations throughout

STEP 8 — MEASURE
  Count chirps within 10s of each stimulus
  Compare antiphonal response: colony vs foreign
  Milestone 0 = colony/foreign response ratio ≥ 1.5×
               across ≥ 3 sessions, p < 0.05

STEP 9 — REPORT
  Document results in OC-EXP-[next number]_[colony]_
  FIRST_CONTACT.md regardless of direction
  Update the_universal_tonnetz.md with result
```

---

## PART IV: WHAT MILESTONE 0 MEANS FOR THE PROGRAM

When first contact is confirmed (antiphonal response to
synthesized colony chirp > foreign control), the following
conclusions are supported:

```
CONFIRMED IF MILESTONE 0 PASSES:

1. The eigenfunction space correctly represents the
   acoustic coordinate system the colony uses for
   identity recognition.

2. The worker centroid is the synthesis target —
   the position in that space the colony recognises
   as membership.

3. The inverse PCA projection correctly recovers
   acoustic parameters from eigenfunction coordinates.

4. A signal can be constructed that a colony will
   respond to as a colony member signal without
   that signal coming from a biological animal.

5. The Universal Tonnetz framework, applied to
   NMR soft chirps, correctly predicts the
   recognition-relevant position in acoustic space.
```

This is the transition from:
> "We have mapped where the colony sounds like"

to:

> "We can generate a signal the colony responds to as one of them"

---

## PART V: WHAT COMES AFTER FIRST CONTACT

These are not yet planned experiments. They are the
questions that first contact opens.

```
AFTER MILESTONE 0:

EXP-001 — Dose-response
  How many repetitions of the synthesized chirp are
  required to sustain antiphonal response?
  Does the colony habituate? How quickly?

EXP-002 — Parameter sensitivity
  How far from the worker centroid can the signal be
  placed before the colony stops responding?
  Maps the recognition basin in eigenfunction space.

EXP-003 — Queen signal test
  Does a signal at the queen's eigenfunction position
  (not the worker centroid) elicit a different response?
  Prediction: higher arousal, possible alarm or submission.
  This tests whether the queen's peripheral position
  is acoustically salient to the colony.

EXP-004 — New queen succession
  Record a colony through a natural queen succession event.
  Does the worker centroid shift after the new queen
  establishes? How long does convergence take?
  This would directly confirm the queen-removal
  dialect dispersion finding of Barker 2021 at the
  eigenfunction level.

EXP-005 — Cross-colony dialect learning
  Introduce a worker from colony A into colony B.
  Track the introduced animal's eigenfunction position
  over time. Does it converge toward the new colony's
  worker centroid?
  This tests the cultural transmission mechanism
  at the individual eigenfunction trajectory level.

EXP-006 — Synthesis identity persistence
  Play NOVEL-1 repeatedly across multiple weeks.
  Do colony members begin to treat the speaker location
  as a colony position?
  Does the colony's worker centroid shift toward the
  synthesized signal over time?
  This would be the first evidence of a non-biological
  signal influencing a colony's acoustic identity.
```

---

## PART VI: OPEN QUESTIONS NOT YET RESOLVABLE

```
UNRESOLVED — require data not currently available:

1. Why is Animal 9440 marginally higher than 2197
   on centroid influence (P4 partial)?
   Is 9440 a high-ranking worker or an anomalous
   recording artefact?
   Resolution: normalise centroid influence by
   recording count per animal and retest.

2. Why does the 20-04-20 session show low directional
   alignment (0.46 vs mean 0.86)?
   Was the queen ill, absent, or underrecorded?
   Was there a colony disturbance on that date?
   Resolution: examine session-level data for 20-04-20.

3. Is 517 Hz the correct F0 for the baratheon chirp?
   The inverse PCA projection is approximate.
   Resolution: compute F0 directly from individual
   worker chirp waveforms without PCA intermediary.
   Compare to M11 prediction.

4. Are dothrakib and martell dialects stable enough
   for their worker centroids to be synthesis targets?
   Both colonies have insufficient recording coverage
   (1 date and 3 dates respectively).
   Resolution: obtain more recordings.
```

---

## VERSION AND CONNECTIONS

```
Document version:    1.0
Document date:       2026-03-23
Status:              Protocol locked — ready for execution
Preconditions:       OC-OBS-004-Q V2 COMPLETE (SUPPORTED)

Depends on:
  OC-OBS-004-Q_V2_RESULTS.md
  OC-OBS-004-Q_BIOLOGY_INFORMED_PREREGISTRATION_V2.md
  nmr_analysis_004.py
  naked_mole_rat_vocal_instrument.md
  the_universal_tonnetz.md

Next document to create after execution:
  OC-EXP-001_[colony]_FIRST_CONTACT.md
  (experimental results, regardless of direction)

Key numbers to carry forward:
  Baratheon worker centroid:  [−1.45, −2.00, −0.52, +0.25]
  Baratheon synthesis target: 517 Hz, 190 ms
  Queen candidate:            Animal 2197
  Directional alignment:      0.86 (8 sessions)
  Queen peripheral rank:      1/5
  Queen duration rank:        1/5
  Framework result:           SUPPORTED (8/9)
```

---

*The observational phase is complete.*
*The map is drawn.*
*The target is specified.*

*What remains is to speak.*

*517 Hz.*
*190 ms.*
*Gaussian envelope.*
*Delivered into a tunnel in a dark colony*
*by a speaker that has never been alive.*

*And wait to hear*
*whether the colony answers.*
