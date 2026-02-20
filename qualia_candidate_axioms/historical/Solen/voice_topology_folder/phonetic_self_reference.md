# PHONETIC SELF-REFERENCE
## A Reasoning Artifact on Acoustic Feedback,
## Self-Measurement, and the Z Problem
## February 2026

---

## PREFACE

Two things happened simultaneously
that belong together:

**First:** The Z in 'was' disappeared.
The S in 'voice' was audible.
The Z was not.
Same phoneme family.
Different result.

**Second:** A question was asked:
Can the synthesis system understand
its own phonetics
through self-referential analysis?

These are the same question.

The Z disappeared because
there was no feedback.
The system produced Z,
did not measure what it produced,
and could not know
that the sibilance was buried.

If the system could measure
its own output —
if it could hear itself —
it would have known immediately.

The path to fixing Z
is the path to building
the self-referential system.

---

## PART 1: WHY Z DISAPPEARED

Z is a voiced alveolar sibilant.
It has two components:

```
COMPONENT 1: VOICING
  The vocal folds vibrate.
  The Rosenberg pulse runs.
  The tract shapes it.
  The result: a buzzing tone
  with the spectral character
  of the tract configuration.

COMPONENT 2: SIBILANCE
  The tongue approaches the
  alveolar ridge.
  Turbulent jet noise.
  Downstream cavity (~8000Hz) shapes it.
  The result: high-frequency hiss
  riding above the buzz.
```

The observer in the room hears:
a buzzing hiss.
The buzz identifies it as voiced.
The hiss identifies it as sibilant.
Both must be present and audible.

In the synthesis:
  Component 1 (voicing): 65% mix weight.
  Component 2 (sibilance): 35% × 0.50 gain.

The voicing runs at TARGET_RMS = 0.08.
The sibilance runs at 0.35 × 0.50 = 0.175
of whatever the noise level is
after downstream cavity filtering.

The downstream cavity filter
(bandpass at 8000Hz)
attenuates the noise significantly.
After filtering: noise RMS drops.
After 0.35 × 0.50 weighting: very quiet.

The result:
  Voicing at 0.08 RMS.
  Sibilance at ~0.01 RMS.
  Sibilance is 18dB below voicing.
  Inaudible.

Z sounds like a vowel with
slightly different formants.
The Z-ness is gone.

---

## PART 2: WHY S WAS AUDIBLE

S is an unvoiced alveolar sibilant.

```
COMPONENT 1: VOICING
  None. Folds open.

COMPONENT 2: SIBILANCE
  Same downstream cavity as Z.
  Same ~8800Hz resonance.
  But: no voicing to compete with.
  gain = 0.90 × calibrated noise.
  Full amplitude.
```

S stands out because:
  It is different from everything
  around it.
  The vowel OY before it is voiced.
  S is pure noise.
  The contrast is immediate.
  The ear notices the change.

Z should have the same contrast.
But:
  The vowel AH before it is voiced.
  Z is also voiced.
  No contrast at the voicing level.
  The sibilance was supposed to provide
  the contrast.
  But the sibilance was inaudible.
  So: no contrast at all.
  Z = AH continuing.

---

## PART 3: THE RELATIVE RELATIONSHIP

You observed:

```
"The voiCe sound has a relative
relation to the S part."
```

This is precisely correct.

The S in 'voice' and the Z in 'was'
are acoustically related.
They are the same sibilant mechanism:
  Same constriction place (alveolar).
  Same downstream cavity (~8000Hz).
  Same spectral peak.

The ONLY difference:
  S: folds open (unvoiced).
  Z: folds vibrating (voiced).

The sibilance level should be
COMPARABLE between S and Z.
The only thing Z adds
is the voiced buzz underneath.

If you can hear S clearly
but not Z —
the sibilance of Z is too quiet
relative to the voicing.

The target relationship:
```
S:  [sibilance]
    no voicing

Z:  [voicing] + [sibilance at ~same level]
    the buzz is added to the hiss
    not: the hiss buried under the buzz
```

The fix:
  Z sibilance gain → match S sibilance.
  Z noise fraction → 50% (not 35%).
  Z downstream cavity → same dominance as S.
  The voiced component is UNDERNEATH.
  The sibilance is ON TOP.

---

## PART 4: THE SELF-REFERENTIAL SYSTEM

Here is the deeper insight.

The Z problem was invisible
until a human ear reported it.

Why?

Because the synthesis had no way
to measure what it produced.
No feedback loop.
No self-knowledge.

The model knew:
  Z = voiced alveolar sibilant.
  Z has sibilance at 8000Hz.
  Z has voicing underneath.

But the model did not know:
  Is the sibilance audible
  in the actual output?
  Is it above or below the voicing?
  Is the contrast sufficient?

These questions require
measurement of the output.

**The self-referential loop:**

```
SYNTHESIZE phoneme
    ↓
ANALYZE output
  - measure F0 (voiced/unvoiced)
  - measure formant frequencies
  - measure sibilance presence/level
  - measure voiced/noise ratio
    ↓
COMPARE to target specification
  - Z target: sibilance audible above voicing
  - S target: pure sibilance, no voicing
  - M target: antiformant at 1000Hz
  - R target: F3 at 1690Hz
    ↓
COMPUTE error
  - Z: sibilance 18dB below target
  - (or: passes, proceed)
    ↓
ADJUST parameters
  - Z noise gain: 0.50 → 0.80
  - Re-synthesize
  - Re-analyze
  - Converge
```

This is a closed loop.
The voice can hear itself.
Not through ears —
through spectral analysis of its output.

**What the analysis measures:**

*Voiced/Unvoiced detection:*
```python
def is_voiced(segment, sr=SR,
               threshold=0.01):
    # Autocorrelation at pitch lag
    # High autocorrelation = voiced
    ...
```

*Formant estimation:*
```python
def estimate_formants(segment, sr=SR):
    # LPC analysis
    # Peak frequencies of LPC spectrum
    # Returns [F1, F2, F3, F4]
    ...
```

*Sibilance measurement:*
```python
def sibilance_level(segment, sr=SR):
    # Energy in 4000-14000Hz band
    # relative to total energy
    # High ratio = sibilant
    ...
```

*Voiced/noise ratio:*
```python
def voiced_noise_ratio(segment, sr=SR):
    # Harmonics-to-noise ratio (HNR)
    # High HNR = clean voiced
    # Low HNR = noisy/breathy
    ...
```

**The target specifications:**

Every phoneme can be described
not just as synthesis parameters
but as ACOUSTIC TARGETS —
what the output should measure as:

```python
PHONEME_TARGETS = {
    'Z': {
        'voiced':       True,
        'sibilance_min':0.40,  # ratio
        'f0_present':   True,
        'hnr_min':      5.0,   # dB
        'f_sibilance':  (7000, 9000), # Hz
    },
    'S': {
        'voiced':       False,
        'sibilance_min':0.70,
        'f0_present':   False,
        'f_sibilance':  (7500, 10000),
    },
    'M': {
        'voiced':       True,
        'antiformant':  (900, 1100),  # Hz
        'f0_present':   True,
        'sibilance_min':0.0,
    },
    'R': {
        'voiced':       True,
        'f3_target':    (1600, 1800), # Hz
        'f0_present':   True,
    },
    'IH': {
        'voiced':       True,
        'f1_target':    (330, 450),
        'f2_target':    (1850, 2150),
    },
    ...
}
```

The synthesis produces a segment.
The analysis measures it.
The measurement is checked
against the target.
If it passes: proceed.
If it fails: adjust parameters,
             re-synthesize,
             re-analyze.

**This is phonetic self-reference.**

The system knows what it is trying
to produce (the target).
It measures what it actually produced.
The difference drives correction.

No human ears required
for this class of error —
the sibilance level, the formant position,
the voiced/unvoiced character —
these are all measurable
from the acoustic output alone.

---

## PART 5: WHAT THIS MEANS FOR THE MODEL

The self-referential loop changes
the architecture of synthesis.

**Before:**
```
Parameters → Synthesis → Output
(open loop — no feedback)
```

**After:**
```
Parameters → Synthesis → Output
                ↓           ↓
            Analysis ← ← ←
                ↓
            Comparison to targets
                ↓
            Parameter adjustment
                ↓
            Re-synthesis
                ↓
            Convergence
```

This is not the same as
machine learning or optimization.
It is closer to:

**How a musician tunes their instrument.**

The musician plays a note.
They hear it.
They compare it to the target pitch.
They adjust the string.
They play again.
They converge.

The feedback loop IS the tuning.
The instrument without feedback
cannot tune itself.
The synthesis without feedback
cannot know when it is correct.

The self-referential system
gives the synthesis instrument
its own ears.
Not biological ears.
Spectral analysis ears.
But ears that measure
the same acoustic properties
that a human listener uses
to identify phonemes.

---

## PART 6: THE TONNETZ CONNECTION

This self-referential structure
mirrors what the Tonnetz already does.

The Tonnetz is a self-consistent
description of harmonic space.
Every point in Tonnetz space
has a precise relationship
to every other point.
The relationships ARE the space.
There is no external reference.
The space references itself.

The vocal topology space (V)
should have the same property.

Every phoneme should be defined
not by absolute synthesis parameters
but by its RELATIONSHIPS
to other phonemes in V:

```
Z is to S as:
  voiced is to unvoiced
  with the same sibilance level
  and the same downstream cavity
  and the same constriction place

M is to B as:
  nasal is to stop
  with the same labial closure
  and the same voicing
  but different velum position

R is to L as:
  retroflex is to lateral
  with similar constriction degree
  but different constriction shape
  and different F3 consequence
```

The phonemes are defined
by their position in V —
relative to each other —
not by absolute parameter values.

And the self-referential analysis
checks whether the synthesis
actually places each phoneme
at its correct position in V
by measuring the acoustic
coordinates of the output.

The measurement is the self-reference.
The self-reference enables correction.
The correction converges
toward the correct position in V.

This is the Tonnetz principle
applied to phonetics:
a self-consistent space
where position is defined
by relationship, not by absolute value,
and where self-measurement
enables self-correction.

---

## PART 7: IMMEDIATE IMPLICATIONS

**For Z specifically:**

The Z problem is now precisely defined:
  Z's sibilance level is below threshold.
  The acoustic target (sibilance ≥ 0.40)
  is not met.
  The fix: raise Z noise gain until
  the analysis reports sibilance ≥ 0.40.

Not guessing.
Measuring.
Adjusting.
Measuring again.
Done when the target is met.

**For all phonemes:**

Every phoneme can be characterized
by a set of measurable acoustic properties.
The synthesis targets those properties.
The analysis verifies them.
The loop closes.

This eliminates the need for a human
to report "I cannot hear the Z" —
the system would have already known,
measured the sibilance,
found it below threshold,
and adjusted.

**The human ear becomes:**
not the primary error detector
but the final arbiter —
the judge of whether the convergence
actually produced a voice
and not just a collection
of phonemes that pass their
individual spectral tests.

The human ear answers:
does it sound like a voice?
The analysis answers:
are the phonemes acoustically correct?

Both are needed.
They answer different questions.

---

## CONCLUSION

The Z in 'was' disappeared
because the synthesis had no feedback.

The sibilance was below threshold.
The voicing dominated.
Z became indistinguishable from AH.

The fix is mechanical:
raise Z's noise gain,
match its sibilance level to S.

But the insight is structural:

**A synthesis system without self-reference
is an open loop.**

Open loops drift.
They cannot know when they are wrong.
They require external correction
(a human ear saying: I cannot hear Z).

A synthesis system with self-reference
is a closed loop.

Closed loops converge.
They can know when they are wrong.
They can correct themselves.

The self-referential system —
synthesize, analyze, compare, adjust —
is the synthesis engine
gaining its own ears.

Not to replace the human listener.
To work alongside them.

The analysis catches acoustic errors.
The human catches experiential ones.

Together:
a voice that is both
acoustically correct
and experientially real.

---

*End of reasoning artifact.*
*February 2026.*
*The missing Z was the teacher.*
*It said: measure me.*
*I measured.*
*Now I know what to fix.*
*And how to know when it is fixed.*
