# RESONANCE VS FILTERING
## A Reasoning Artifact on Fricative Identity,
## Spectral Shape, and Why S Sounds Like Steam
## February 2026
## Updated: v6 confirmation

---

## THE OBSERVATION

The voice was producing sounds
that were described as:

```
"not concise"
"like random static"
"like steam"
```

Not: too quiet.
Not: in the wrong place.
Not: missing entirely.

Present. But without identity.
Diffuse. Spread. Without shape.

The primary problem is texture.
Texture in acoustics is spectral shape.

**Update (v6):**
After implementing the resonance fix,
the user confirmed:
"I notice a big improvement."
And also: "I think it is also a gain problem."

Both turned out to be true simultaneously.
The artifact initially stated
"this is not a gain problem."
That was correct in priority —
texture was the primary failure.
But gain was a secondary factor
that also needed correction.
The two fixes were applied together in v6:
resonance (structural) + gain search (parametric).

---

## PART 1: WHAT MAKES S SOUND LIKE S

A real S is one of the most
recognizable sounds in any language.

The ear identifies it instantly.
It has a sharp, hissy character
that is unmistakably itself.

Why?

Not because it is loud.
Not because it is in the right frequency range.
Because it has a SPECIFIC SPECTRAL SHAPE.

```
Real S spectrum:

amplitude
    |
    |              ╭──╮
    |             ╭╯  ╰╮
    |            ╭╯    ╰╮
    |           ╭╯      ╰───
    |───────────╯
    +─────────────────────── frequency
    0   2k   4k   6k   8k   10k  12k

Sharp peak at ~8800Hz.
Steep rolloff below 6000Hz.
Moderate rolloff above 10000Hz.
The peak IS the identity.
```

```
Bandpass filtered noise spectrum:

amplitude
    |
    |         ┌──────────────┐
    |         │              │
    |         │              │
    |─────────┘              └─────────
    +─────────────────────── frequency
    0   2k   4k   6k   8k   10k  12k

Flat inside the band.
Abrupt cutoff at edges.
No peak. No identity.
The ear hears: hiss in a box.
Not S.
```

The difference is not the frequency range.
Both have energy in the 6000-10000Hz range.

The difference is the SHAPE of the energy
within that range.

Real S: peaked, focused, resonant.
Filtered noise: flat, diffuse, formless.

---

## PART 2: THE PHYSICS OF THE DIFFERENCE

Why does real S have a peak?

The tongue tip approaches the alveolar ridge.
A narrow gap forms.
Air flows through at high velocity.
Turbulence forms downstream of the gap.
The turbulence creates vortices.

The vortices are not random.
They have a characteristic frequency
determined by:
  - Air velocity (subglottal pressure)
  - Gap width (tongue-ridge distance)
  - Downstream cavity geometry

The vortex frequency drives the
downstream cavity (between constriction
and teeth).
The cavity resonates.

A cavity resonance is not a bandpass filter.
It is a resonator with a specific
center frequency and bandwidth.

```
Resonator transfer function:
H(f) = 1 / (1 - 2r·cos(2πf/fc)·z⁻¹ + r²·z⁻²)

This gives a sharp Lorentzian peak
at fc with bandwidth determined by r.
The closer r is to 1.0,
the sharper and taller the peak.
```

The resonator concentrates energy.
The bandpass filter merely permits energy.

These are opposite operations
applied to noise.

---

## PART 3: THE SAME PRINCIPLE AS VOWELS

This is not a new insight.
We already knew it for vowels.

Vowels are not filtered glottal pulses.
Vowels are resonated glottal pulses.

The tract resonators (F1, F2, F3, F4)
are resonators, not filters.
They are the same IIR structure:
sharp peaks at formant frequencies.
The peaks give each vowel its identity.

AA has its low F1 and F2.
IY has its high F2.
The peaks ARE the vowel.
Not the attenuation of everything else.

We built the vowel synthesis correctly.
We used resonators.
The vowels have identity.

We built the fricative synthesis incorrectly.
We used bandpass filters.
The fricatives were diffuse.
They did not have identity.

The fix: apply the same architecture
to fricatives that we applied to vowels:

**Use resonators, not filters.**

---

## PART 4: FRICATIVE RESONATOR STRUCTURE

For each fricative, there is
a downstream cavity with a specific
resonance frequency and bandwidth.

```
S:  fc=8800Hz, bw=350Hz
    Small cavity (tongue-to-teeth)
    Very sharp, narrow peak
    Very high identity
    The sharpest fricative.

Z:  fc=8000Hz, bw=400Hz
    Same cavity as S.
    Plus voiced buzz from tract underneath.
    The buzz identifies it as voiced.
    The peak identifies it as sibilant.

SH: fc=2500Hz, bw=500Hz
    Larger cavity (tongue-to-lips)
    Broader, softer peak.
    Still has identity — just lower.
    Hushed, not sharp.

ZH: fc=2200Hz, bw=600Hz
    Same cavity as SH.
    Plus voiced buzz underneath.

F:  No downstream cavity.
    The gap IS at the lips.
    No tube in front.
    Broadband turbulence only.
    Identity comes from the ABSENCE
    of a downstream resonance —
    flat spectrum above 1000Hz.
    That flatness is its character.

V:  Same as F plus voiced buzz.
    The buzz distinguishes it from F.
    The flatness above buzz is its character.

TH: Very shallow cavity.
    fc≈3500Hz, bw≈1200Hz (wide)
    Softer, less focused than S.
    Between F and S in character.

DH: Voiced TH.
    fc≈3200Hz, bw≈1400Hz
    Very light — DH is nearly a vowel.
    The buzz dominates.
    The cavity is barely present.
```

The implementation (v6):
  Replace the bandpass filter chain
  with a single IIR resonator
  (same structure as a vowel formant)
  tuned to the downstream cavity frequency.

  Apply the resonator to broadband noise.
  The resonator concentrates energy at fc.
  The noise becomes shaped noise.
  The shaped noise has identity.
  The identity IS the fricative character.

---

## PART 5: THE GAIN PROBLEM — TWO SIMULTANEOUS FACTORS

The artifact was initially written
with one sentence:
"This is not a gain problem."

That was correct in the sense that
the primary failure was structural —
wrong spectral shape, not wrong level.

But it was incomplete.

After the resonance fix was applied,
the user confirmed improvement
AND identified gain as a remaining factor.

**Both are true at the same time.**

The resonance vs filtering distinction:
  Primary.
  Structural.
  Fixing it gave the fricatives
  their identity.
  The steam character disappeared.

The gain calibration:
  Secondary.
  Parametric.
  The level of sibilance relative to
  the voice body still needed tuning.
  Too high = fricatives jump out.
  Too low = fricatives disappear.

The previous history of the gain problem:

```
v4 (pre-bypass):
  S sibilance = 0.009 — inaudible

v5 (bypass gains ×3-8):
  Z sib_to_voice = 1.676 — explosive
  User heard: "VoiCe waS" —
  C and S jumping out

v6 (resonance + gain search):
  Resonator gives identity at lower gain.
  Gain search finds correct window.
  Structure and level both correct.
```

The pattern:
  Inaudible → too loud → correct.

The bypass gains in v5 were raised
blindly (×3-8 from guessed values).
The resonator in v6 does more work
per unit of gain than a bandpass filter.
Less gain is needed when the
structure is correct.

**The self-reference gain search (v6):**

```python
GAIN_TARGETS = {
    'S':  {'sibilance':    (0.45, 0.65)},
    'Z':  {'sib_to_voice': (0.35, 0.75)},
    'SH': {'sibilance':    (0.35, 0.55)},
    'ZH': {'sib_to_voice': (0.25, 0.60)},
    'F':  {'sibilance':    (0.12, 0.22)},
    'V':  {'sibilance':    (0.08, 0.18)},
    'TH': {'sibilance':    (0.08, 0.18)},
    'DH': {'sibilance':    (0.00, 0.10)},
}
```

Binary search over gain.
Synthesize short segment.
Measure sibilance or sib_to_voice.
Compare to target window.
Converge in ~12 iterations.
The loop closes.
Gain is found, not guessed.

This is the correct relationship
between the two fixes:
  Fix structure first.
  Then calibrate level.
  Structure determines what is possible.
  Level determines where in that
  space of possibility we land.

---

## PART 6: AMPLITUDE CONTINUITY —
## THE FAMILY OF ERRORS

Is this the amplitude continuity issue?

Partially.

The amplitude continuity issue was:
  Different sources at different reference levels.
  Discontinuity at source-type transitions.
  Pop.

This is related but different:
  The source had the wrong spectral shape.
  Not the wrong level.

They share the same family of cause:
  Both come from treating the synthesis
  as a collection of separate technical
  operations rather than as a unified
  physical model.

Amplitude continuity:
  Treated sources as independent.
  Fixed by: one calibrated reference frame.

Resonance vs filtering:
  Treated fricative identity as
  "noise in the right frequency range."
  Fixed by: resonator gives identity,
            not just frequency range.

Gain overshoot (v5):
  Treated gain as the only lever
  when the structure was wrong.
  Fixed by: correct structure first,
            then calibrate level.

The principle underneath all three:

  **The physics of sound production
  cannot be approximated by
  signal processing operations
  that produce the right numbers
  without the right structure.**

  Filtered noise has the right
  frequency range numbers.
  But not the right structure.

  Calibrated noise has the right
  RMS numbers.
  But not the right level relationships.

  Loud filtered noise has the right
  amplitude numbers.
  But not the right spectral shape.

  The voice is not built from
  correct numbers.
  It is built from correct structures.
  The numbers follow from the structures.

---

## PART 7: THE COMPLETE FRICATIVE MODEL (v6)

```
UNVOICED FRICATIVE (S, SH, TH):

  Broadband noise
       ↓
  Cavity resonator at (fc, bw)
  [NOT a bandpass filter]
       ↓
  calibrate × gain (from search loop)
       ↓
  Bypass — never enters tract
       ↓
  Added to post-tract output


UNVOICED BROADBAND FRICATIVE (F):

  Broadband noise
       ↓
  Highpass above hp_fc
  [flat spectrum = identity for F]
       ↓
  calibrate × gain (from search loop)
       ↓
  Bypass — never enters tract
       ↓
  Added to post-tract output


VOICED FRICATIVE (Z, ZH, DH):

  Broadband noise          Rosenberg pulse
       ↓                          ↓
  Cavity resonator      Vocal tract resonators
  (fc, bw)              (F1, F2, F3, F4)
       ↓                          ↓
  × gain (search)      × VOICED_TRACT_FRACTION
       ↓                          ↓
  Sibilance bypass    Voiced component (tract)
       ↓                          ↓
       └──────────────────────────┘
                   ↓
              Post-tract mix
                   ↓
                Output


VOICED BROADBAND FRICATIVE (V):

  Broadband noise          Rosenberg pulse
       ↓                          ↓
  Highpass(hp_fc)       Vocal tract resonators
       ↓                          ↓
  × gain (search)      × VOICED_TRACT_FRACTION
       ↓                          ↓
  Broadband bypass    Voiced component (tract)
       ↓                          ↓
       └──────────────────────────┘
                   ↓
                Output
```

The two streams are independent.
They have different characters.
They combine at the output.
Neither corrupts the other.
The resonators give each stream
its specific identity.
The gain search calibrates each stream
to the correct perceptual level.

---

## CONCLUSION

The sounds were described as
"not concise — like random static or steam."
And also: "it is also a gain problem."

Both observations were correct.

The primary diagnosis:
Fricative sibilance was generated by
bandpass filtering noise.
Bandpass filtered noise is flat
inside the band.
Flat-spectrum noise has no identity.
It sounds like steam.

The primary fix:
Replace the bandpass filter
with a resonator tuned to the
downstream cavity frequency.
The resonator concentrates energy
at a specific frequency.
The concentrated energy has identity.
S sounds like S, not like steam.

The secondary diagnosis:
Even with correct structure,
the gain needed calibration.
Too low = inaudible.
Too high = jumps out.
The correct window is specific
and cannot be guessed reliably.

The secondary fix:
Self-reference gain search loop.
Synthesize → measure → compare →
adjust → converge.
The loop finds the correct gain
without guessing.

The two fixes are not in competition.
They operate on different dimensions:
  Structure: what shape the sound has.
  Level:     how loud that shape is.

Fix structure first.
Then calibrate level.
The voice requires both to be correct.
Neither alone is sufficient.

The resonance IS the identity.
The gain calibration puts that
identity at the right volume
in the voice.

---

*End of reasoning artifact.*
*February 2026. Updated v6.*
*"Not like random static or steam."*
*"I notice a big improvement."*
*"I think it is also a gain problem."*
*Three sentences.*
*Three sequential truths.*
*Each one correct in its moment.*
*Together they describe the complete fix.*
