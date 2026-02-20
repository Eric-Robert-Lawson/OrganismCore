# RESONANCE VS FILTERING
## A Reasoning Artifact on Fricative Identity,
## Spectral Shape, and Why S Sounds Like Steam
## February 2026

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

This is not a gain problem.
This is a texture problem.
And texture in acoustics
is spectral shape.

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
The fricatives are diffuse.
They do not have identity.

The fix is to apply the same architecture
to fricatives that we applied to vowels:

**Use resonators, not filters.**

---

## PART 4: FRICATIVE RESONATOR STRUCTURE

For each fricative, there is
a downstream cavity with a specific
resonance frequency and bandwidth.

```
S:  fc=8800Hz, bw=400Hz
    Small cavity (tongue-to-teeth)
    Sharp, narrow peak
    Very high identity

Z:  fc=8000Hz, bw=500Hz
    Same cavity as S
    Plus voiced buzz underneath

SH: fc=2500Hz, bw=600Hz
    Larger cavity (tongue-to-lips)
    Broader, softer peak
    Still has identity — just lower

ZH: fc=2200Hz, bw=700Hz
    Same cavity as SH

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
    fc≈3500Hz, bw≈1500Hz (wide)
    Softer, less focused than S.
    Between F and S in character.
```

The implementation:
  Replace the bandpass filter chain
  with a parallel resonator
  (same as the vowel tract resonator)
  tuned to the downstream cavity frequency.

  Apply the resonator to the broadband noise.
  The resonator concentrates energy at fc.
  The noise becomes shaped noise.
  The shaped noise has identity.
  The identity IS the fricative character.

---

## PART 5: THE GAIN OVERSHOOT

The rainbow diagnostic showed:

```
Z sib_to_voice = 1.676
Target: ≥ 0.35
```

We aimed for 0.35.
We landed at 1.676.
Nearly 5× overshoot.

This happened because:
  We raised bypass gains ×3-8.
  The sibilance became loud.
  But because the spectral shape was wrong
  (filtered, not resonated)
  the loudness did not translate
  to identity.
  It translated to volume.

  MORE FILTERED NOISE ≠ MORE S CHARACTER.
  It just means more hiss.

When the spectral shape is correct —
when the resonator gives the noise
its proper Lorentzian peak —
the identity comes from shape, not volume.

The correct gain will be much lower
than the overshot value.
The resonator does the work
that gain was compensating for.

The self-reference system needs
an upper bound on sib_to_voice:

```python
PHONEME_TARGETS['Z']['sib_to_voice_max'] = 0.80
# Sibilance present but not drowning voice.
# Voice is the primary signal.
# Sibilance identifies the fricative.
# 0.35 ≤ sib_to_voice ≤ 0.80
```

---

## PART 6: AMPLITUDE CONTINUITY — SAME PRINCIPLE?

Is this the amplitude continuity issue?

Partially.

The amplitude continuity issue was:
  Different sources at different reference levels.
  Discontinuity at source-type transitions.
  Pop.

This is related but different:
  The source has the wrong spectral shape.
  Not the wrong level.
  The level is approximately right now.
  The shape is wrong.

They share the same family of cause:
  Both come from treating the synthesis
  as a collection of separate technical
  operations rather than as a unified
  physical model.

Amplitude continuity:
  Treated sources as independent.
  Fixed by: one reference frame.

Resonance vs filtering:
  Treating fricative identity as
  "noise in the right frequency range."
  Fixed by: resonator gives identity,
            not just frequency range.

The principle underneath both:
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

  The voice is not built from
  correct numbers.
  It is built from correct structures.

---

## PART 7: THE COMPLETE FRICATIVE MODEL

After this fix, the fricative model:

```
UNVOICED FRICATIVE (S, SH, F, TH):

  Broadband noise
       ↓
  Resonator at fc (downstream cavity)
  (NOT a bandpass filter)
       ↓
  Bypass (never enters tract)
       ↓
  Output

VOICED FRICATIVE (Z, ZH, V, DH):

  Broadband noise                Rosenberg pulse
       ↓                               ↓
  Resonator at fc             Vocal tract resonators
  (downstream cavity)          (F1, F2, F3, F4)
       ↓                               ↓
  Sibilance bypass           Voiced component
       ↓                               ↓
       └──────────────────────────────┘
                    ↓
                  Output

The two streams are independent.
They have different characters.
They combine at the output.
Neither corrupts the other.
The resonators give each stream
its specific identity.
```

---

## CONCLUSION

The sounds were described as
"not concise — like random static
or steam."

The diagnosis:
Fricative sibilance was generated by
bandpass filtering noise.
Bandpass filtered noise is flat
inside the band.
Flat-spectrum noise has no identity.
It sounds like steam.

The fix:
Replace the bandpass filter
with a resonator tuned to the
downstream cavity frequency.
The resonator concentrates energy
at a specific frequency.
The concentrated energy has identity.
S sounds like S, not like steam.

This is the same principle
that makes vowels sound like vowels.
Resonators, not filters.
The resonance IS the identity.

The architecture was correct.
The implementation was wrong.
The fix is structural, not parametric.
Changing the gain would not have
fixed the steam character.
Only changing the structure
from filter to resonator
will give the fricatives
their concise identity.

---

*End of reasoning artifact.*
*February 2026.*
*"Not like random static or steam."*
*That sentence described the difference*
*between filtering and resonating.*
*The ear knew.*
*The physics confirms it.*
