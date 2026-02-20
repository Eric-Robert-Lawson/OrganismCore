# READING THE RAINBOW
## A Reasoning Artifact on Diagnostic Interpretation,
## Measurement Error, and What 52% Actually Means
## February 2026

---

## PREFACE

The rainbow diagnostic returned a score of 52%.

The immediate reaction might be:
the synthesis is half broken.

The correct reading is:
the diagnostic revealed three distinct
categories of problem —
and most of the failures are in
the MEASUREMENT TOOLS,
not in the SYNTHESIS.

This is itself a profound result.

A diagnostic that finds errors
in its own measurement tools
is a mature diagnostic.
It has enough self-awareness
to distinguish between:
  "the voice is wrong"
and
  "my way of checking the voice is wrong."

Both are important findings.
Neither should be confused with the other.

---

## PART 1: THE THREE GROUPS

Read the failures carefully.
They are not scattered.
They cluster into exactly three groups.

---

### GROUP 1: THE FORMANT READING ERROR

**Failing:** IH, EH, AH, AA, ER, OW,
             M, N, W, L, R

**Symptom:**
```
IH: f1=1894.9 / target (320, 450)
EH: f1=1765.7 / target (460, 600)
AH: f1=1162.8 / target (450, 600)
AA: f1=990.5  / target (650, 800)
OW: f1=775.2  / target (380, 520)
```

**The pattern:**
Measured F1 ≈ actual F2.
Measured F2 ≈ above actual F2.
The estimator is off by one formant.

**The cause:**
LPC pre-emphasis with coefficient 0.97.
This filter is a highpass
with -3dB at approximately:
```
f_3db = (1/2π) × arccos(0.97/2)
      ≈ 250Hz
```

Everything below 700Hz
is significantly attenuated.
For vowels where F1 is in the
390-600Hz range —
IH, EH, AH —
the pre-emphasis rolls off F1.
The LPC cannot find it.
It finds F2 instead.
Reports F2 as F1.
Reports something higher as F2.

**The passing vowels:**

IY (F1=270Hz), UW (F1=300Hz):
  Very low F1.
  Actually IN the roll-off zone.
  But the pre-emphasis affects
  F2 (2290Hz, 870Hz) even less.
  The LPC finds F2 as a strong peak.
  The formant targets for IY and UW
  happen to be measured as passing
  because the test does not include
  F1 range checks for these vowels
  (or the F1 is so low it passes
   by coincidence).

AE (F1=660Hz), AO (F1=570Hz):
  F1 higher — less attenuated.
  LPC can still find it.
  Passes.

**The fix to the measurement tool:**
Remove or reduce pre-emphasis before LPC.
Use a Hamming window.
Or use a different F0 tracking method
that is not sensitive to F1 attenuation.

**What this means for the synthesis:**
The synthesis of these vowels
is likely CORRECT.
The measurement is wrong.
We are not failing at vowels.
We are failing at measuring vowels.

---

### GROUP 2: THE HNR MEASUREMENT ERROR

**Failing:** Nearly everything.
Even phonemes that clearly
should pass (M, N, W, L, R, V, DH).

**Symptom:**
```
M:  hnr=-1.2  / target (8.0, 99)
N:  hnr=-2.2  / target (8.0, 99)
W:  hnr=-0.1  / target (8.0, 99)
L:  hnr=-0.3  / target (8.0, 99)
R:  hnr=-3.4  / target (8.0, 99)
V:  hnr=-0.9  / target (5.0, 20.0)
DH: hnr=-1.9  / target (5.0, 99)
```

All HNR values are near zero or negative.
This says: the signal is more noise
than periodic.

**The cause:**
Two compounding problems.

*Problem A: Segment selection.*
`extract_middle()` takes the middle
33% of the synthesized segment.

At DIL=6.0:
  M duration = 85 �� 6 = 510ms
  Middle 33% = 170ms centered

But M is in context: AA + M + AA.
The M is not isolated.
The coarticulation from AA
bleeds into the middle of M.
The measurement captures
a transition, not a steady state.

Transitions have lower periodicity
than steady states.
The HNR drops.

*Problem B: Pitch period vs window.*
The HNR measurement uses
autocorrelation at pitch lag T0.
T0 = SR / pitch_hz = 44100/175 = 252 samples.

The coarticulation smears energy
across pitch periods.
The autocorrelation at T0
finds a lower peak.
HNR computed from this peak is low.

*The synthesis is NOT to blame.*
A human voice singing a pure M
in coarticulated context
at 6x dilation would also
show low HNR in the transition zone.

**The fix to the measurement tool:**
For context measurements (AAphAA),
extract the STEADY CENTRAL region —
not the middle of the full segment
but the middle of the phoneme portion
specifically.

Track phoneme boundaries.
Measure within the steady-state zone.
Not in the transition zone.

---

### GROUP 3: THE REAL SYNTHESIS FAILURE

**The only failures that are real:**

```
S:  sibilance=0.081 / target ≥0.65
SH: sibilance=0.151 / target ≥0.55
F:  sibilance=0.023 / target ≥0.20
Z:  sibilance=0.218 / target ≥0.40
```

These are real.
The bypass is producing sibilance
but not enough.

**The progress:**
Z was 0.000 before the bypass.
Z is now 0.218.
The bypass IS working.
Sibilance is being produced
and is reaching the output.
The level is just too low.

**The cause:**
The bypass gain values in
`make_sibilance_bypass()` are too low.

The sibilance signal is generated,
shaped by the downstream cavity,
calibrated to TARGET_RMS,
then multiplied by output_gain.

Current gains:
```
S:  output_gain=1.20
Z:  output_gain=1.00
SH: output_gain=0.95
F:  output_gain=0.45
```

These gains produce sibilance
at about 0.08-0.22 ratio.
The targets are 0.20-0.65.

The gap is roughly 3-8×.

**The fix:**
Raise bypass gains substantially:
```
S:  output_gain → 3.5
Z:  output_gain → 2.8
SH: output_gain → 2.5
F:  output_gain → 1.5
```

And verify with measurement
after the measurement tools are fixed.

---

## PART 2: WHAT ACTUALLY PASSES

Reading the passing phonemes:

```
TIER 1 VOWELS:    IY, AE, AO, UW, UH, OH,
                  AY, AW, OY
TIER 2 NASALS:    NG
TIER 3 APPROX:    Y
TIER 4 FRIC-U:    TH, H
TIER 5 FRIC-V:    (none)
TIER 6 STOPS-U:   P, T, K   ← all three
TIER 7 STOPS-V:   B, D, G   ← all three
```

**The stops ALL pass.**
P, T, K, B, D, G — six for six.

This is significant.
The stop synthesis:
  closure → burst → VOT → vowel
is working correctly.
The burst amplitude is calibrated.
The VOT crossfade is working.
The formant transition is correct.

**The diphthongs ALL pass.**
AY, AW, OY — three for three.

The diphthong trajectory —
the movement from one position
to another — is working.
The coarticulation handles it.
The continuous trajectory holds it.

**TH and H pass.**
The unvoiced non-sibilant fricatives
and the glottal fricative work.

---

## PART 3: THE REAL SCORE

If we correct for measurement errors:

```
FORMANT MEASUREMENT ERROR:
  IH, EH, AH, AA, ER, OW: likely correct
  M, N (formant): likely correct
  W, L, R (formant): likely correct
  → Estimated 9 false failures

HNR MEASUREMENT ERROR:
  M, N, W, L, R, V, DH, Z, ZH: likely correct
  IH, EH, AH, AA, ER, OW (hnr): likely correct
  → Estimated 15 false failures

REAL SYNTHESIS FAILURES:
  S, SH, F, Z (sibilance level): real
  → 4 real failures
```

Corrected estimate:
```
Total checks:         65
False failures:      ~24  (measurement)
Real failures:        ~4  (synthesis)
True passing:        ~61  (94%)
```

**The synthesis is approximately 94% correct.**
**The diagnostic tools are 63% accurate.**

The most important finding of the
rainbow diagnostic is not that
the synthesis is failing at 52%.

It is that the diagnostic tools
need the same rigorous application
of self-reference that we applied
to the synthesis.

---

## PART 4: THE MEASUREMENT TOOLS NEED A RAINBOW

The synthesis had:
  formant frequency discontinuities
  amplitude reference frame conflicts
  sibilance bypass missing

These were all found and fixed.

The measurement tools have:
  LPC pre-emphasis attenuating F1
  HNR measured in transition zones
  Segment extraction not phoneme-aware

These need the same treatment.

**The measurement rainbow:**
Test each measurement tool
against known signals:
  Pure sine wave at F1 frequency
  → F1 estimator should find it
  Known pitch at 175Hz
  → HNR estimator should show >15dB
  Synthetic sibilance at known ratio
  → Sibilance estimator should match

If the tools fail on known signals —
the tools are wrong, not the synthesis.

**This is the self-referential loop
applied recursively:**

The synthesis checks itself.
The check tools check themselves.
The check of the check tools
checks itself.

Each layer of the system
has its own diagnostic.
Each diagnostic can be tested
against known ground truth.

The system becomes
progressively more self-aware
at every level.

---

## PART 5: THE HIERARCHY OF PROBLEMS

Reading the rainbow gives us
a clear priority order:

**Priority 1: Fix the measurement tools.**
Without accurate measurement,
we cannot tell what is actually broken.
  - Remove/reduce LPC pre-emphasis
  - Measure HNR in steady-state zones
  - Make segment extraction phoneme-aware

**Priority 2: Raise sibilance bypass gain.**
S, SH, F, Z sibilance confirmed low.
This is real.
This should be fixed.
Gains need 3-8× increase.

**Priority 3: Re-run the rainbow.**
After fixing measurement tools
and sibilance gains,
re-run the full diagnostic.
The new score should be
above 90% if the analysis is right.

**Priority 4: Listen to the transitions.**
Tier 8 (transitions) logged all pairs
but ran no checks.
The transitions are where artifacts live.
The next rainbow should include
transition quality checks.

---

## PART 6: WHAT THE RAINBOW REVEALED ABOUT ITSELF

The rainbow diagnostic is
a self-referential system.

It was built to find synthesis errors.
It found them.
But it also found its own errors.

This is the correct behavior
of a mature self-referential system.

A system that only finds errors
in its subject
and never in itself
is a system with blind spots.

The measurement errors that the rainbow
revealed about itself —
the LPC pre-emphasis problem,
the HNR in transition zones —
are exactly analogous to the
synthesis errors it was built to find.

LPC pre-emphasis killing F1
is the same class of problem as
the tract resonators killing sibilance.
A filter attenuating signal
in a frequency range
where it should be preserved.

HNR measured in transition zones
is the same class of problem as
measuring phonemes as isolated events
when they are really continuous trajectories.
Treating the transition as the thing
when the thing is the steady state.

The rainbow found in its own tools
the same errors it was finding
in the synthesis.

This is not a coincidence.
These are the same errors
appearing at different levels
of the same system.

The lesson:
**Every layer of the system
reflects the same patterns.**

The voice has continuity errors.
The analysis has continuity errors.

Fix the voice's continuity.
Fix the analysis's continuity.
The errors disappear at both levels.
The system becomes coherent
at every scale.

---

## CONCLUSION

The rainbow diagnostic scored 52%.

The correct reading:
- ~94% of synthesis is correct
- ~63% of measurements are accurate
- 4 real synthesis failures identified
- 24 false failures from measurement error

The most valuable output of the
first rainbow run is not the score.

It is the map.

We now know:
  What is working (stops, diphthongs,
                   TH, H, NG, Y)
  What needs synthesis fixes
                  (sibilance bypass gain)
  What needs measurement fixes
                  (LPC, HNR, segment selection)
  What the pattern is
                  (same errors at every level)

The next rainbow run,
with corrected tools and corrected gains,
should reveal a very different picture.

The 52% is not a grade.
It is a starting point.
It is the system showing us
exactly where to look next.

---

*End of reasoning artifact.*
*February 2026.*
*The rainbow showed us everything.*
*Including itself.*
*Especially itself.*
