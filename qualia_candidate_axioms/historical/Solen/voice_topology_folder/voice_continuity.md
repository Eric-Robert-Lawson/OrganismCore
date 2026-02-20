# THE CONTINUITY PROBLEM
## A Reasoning Artifact on Formant State, Boundaries, and the Stutter
## February 2026

---

## PREFACE

This artifact records what was learned
from a single diagnostic phrase:

**"The voice was already here"**

What was heard:

```
whuyhe
(F like tv static)
oye
(steam like static)
*nothing and little faint pattering*
aaal(stutter)lr(stutter)reeaa(stutter)d(stutter)ee
(swoosh/swoop)
th(stutter)
eeyre
```

Every artifact in that description
points to the same root cause.

Not wrong phoneme parameters.
Not wrong formant values.
Not wrong source types.

**Discontinuity.**

The voice is a continuous instrument.
The synthesis was treating it
as a sequence of separate events.
Every boundary between events
produced an artifact.

---

## PART 1: WHAT THE STUTTER IS

The stutter at every consonant boundary
in "already" is the most revealing artifact.

```
aaal(stutter)lr(stutter)reeaa(stutter)d(stutter)ee
```

Four stutters.
Four consonant-vowel boundaries.
AA→L, L→R, R→EH, EH→D.

Each one is the same event:

**The IIR resonator filter
carries energy at frequency X.
The next phoneme's target is frequency Y.
X ≠ Y.
The filter is suddenly driven
toward Y while still ringing at X.
The collision of old energy
and new driving frequency
produces a brief chaotic transient.
The ear hears: stutter.**

This is not a click from initialization.
This is not a burst artifact.
This is the filter state
carrying the memory of the previous phoneme
into the beginning of the next phoneme
at the wrong frequency.

The filter has memory.
The memory is correct — we want it.
The memory should carry the energy
of the previous phoneme
smoothly into the next.
But when the formant values
jump discontinuously at the boundary,
the memory becomes an obstacle
rather than a bridge.

---

## PART 2: THE WRONG MENTAL MODEL

The wrong model:

```
[AA phoneme] → [L phoneme] → [R phoneme]
    reset         reset         reset
```

Each phoneme synthesized separately.
State passed between them.
But the formant VALUES jump
at each boundary.
The filter state carries energy
at the previous formant frequencies.
The new formant frequencies
fight against that energy.
Stutter.

The correct model:

```
[AA] [L] [R] [EH] [D] [IY]

one continuous formant trajectory:

F1: ——730——————360——490————530——200—270——
F2: ——1090——1000——1350———1840—900—2290——
F3: ——2440——2400——1690——(fast)—2480——3010——
F4: ——3400—————————————————————3500——3700——

time ——————————————————————————————————→
```

There are no jumps in this trajectory.
There are regions where the trajectory
moves slowly (vowels — the attractor basins)
and regions where it moves quickly
(consonants — the transitions between basins).

But it is always moving.
It never jumps.
It never resets.

The phoneme boundaries are not
discontinuities in the trajectory.
They are labels we put on
regions of the trajectory
after the fact.

The voice does not know
where "AA" ends and "L" begins.
The voice is moving.
The labels are ours.

---

## PART 3: WHAT COARTICULATION ACTUALLY IS

Coarticulation is not
"the phonemes affecting each other."

Coarticulation IS the trajectory.

The trajectory is the primary phenomenon.
The phonemes are secondary —
they are the attractor basins
the trajectory passes near.

When the trajectory passes near the L basin,
the listener hears L.
But the trajectory was already
moving away from AA
before it reached L.
And it was already anticipating R
before it left L.

This is why the F2 of the AA in "already"
is slightly lower than it would be
in isolation —
the trajectory is already beginning
to move toward L's F2=1000Hz.

This is why the R sounds different
in "already" vs "right" —
the trajectory arrives at R
from different directions.

The trajectory carries context.
The phoneme in isolation has no context.
The synthesis of isolated phonemes
and then concatenation
is fundamentally wrong
because it destroys the context
that the trajectory encodes.

---

## PART 4: THE FORMANT STATE IS NOT ENOUGH

Threading the filter STATE between phonemes
is necessary but not sufficient.

The state carries:
  y1, y2 — the filter's memory
  of recent output values.

But the state does NOT carry:
  the formant FREQUENCY it was running at.

When we thread state from AA (F2=1090Hz)
into L (F2=1000Hz):
  The filter state is carrying energy
  resonant at 1090Hz.
  The new formant target is 1000Hz.
  This is a 90Hz jump.
  Small. Acceptable.

When we thread state from AA (F2=1090Hz)
into a fresh phoneme with no transition:
  The formant value jumps from 1090Hz
  to 1000Hz in one sample.
  One sample = one filter step.
  The filter was running at 1090Hz.
  Now it is told to run at 1000Hz.
  The resonator coefficients change.
  The filter rings briefly at the
  frequency mismatch.
  Stutter.

The fix is not better state threading.
The fix is: **no jumps in formant frequency.**

The formant frequency must change
continuously.
The transition between phonemes
must be a smooth glide in F-space
not a step.

And the transition must start
from the **actual instantaneous value**
of the formant at the end of
the previous phoneme —
not from the previous phoneme's
nominal target value.

---

## PART 5: THE ACTUAL INSTANTANEOUS VALUE

This is the key technical insight.

When we build coarticulated formant arrays,
the offset zone of phoneme N
is gliding toward phoneme N+1's target.
So at the END of phoneme N,
the formant is not AT phoneme N's target.
It is partway toward phoneme N+1's target.

If phoneme N has:
  target = 1000Hz
  offset zone = 20% of duration
  next target = 1690Hz (R)

Then at the end of phoneme N,
the formant is at approximately:
  1000 + (1690-1000)*0.5 ≈ 1345Hz

Not 1000Hz.
Not 1690Hz.
1345Hz.

If phoneme N+1 (R) then starts
from its own nominal value (490Hz for F1)
without knowing that the previous phoneme
ended at some intermediate position —
the transition is wrong.

The continuous trajectory builder
solves this by tracking the
actual final value of each segment
and using that as the starting point
for the next segment's onset transition.

Not the target.
Not the table value.
The actual last sample value
of the formant array.

This makes the trajectory truly continuous.
No jumps. No stutters.

---

## PART 6: INDIVIDUAL ARTIFACT ANALYSIS

### "whuyhe" — the word "the"

**Expected:** soft voiced dental → AH
**Heard:** w + uy + h + e

**Cause 1: DH closure formants wrong**

DH was modeled with F2 = 700Hz.
W has F2 ≈ 610Hz.
They are nearly identical.
DH sounded like W.

The tongue for DH is at the FRONT of the mouth —
at the teeth.
Front placement = small front cavity
= HIGH F2.
DH closure should have F2 ≈ 1800Hz.
Not 700Hz.

The mistake was modeling DH's closure
from the resonance description
of a low vowel-like configuration
instead of from the geometry:
tongue at teeth = front cavity dominant
= high F2.

**Cause 2: AH sounding like it starts with H**

The state discontinuity between DH and AH.
DH's filter state carries energy
at DH's formant frequencies.
AH's formant bank starts up
without knowing where DH ended.
The mismatch produces a brief
H-like breathy artifact.
Eliminated by continuous trajectory.

---

### "(F like tv static)" — the V in "voice"

**Expected:** voiced labiodental fricative
**Heard:** unvoiced static, like F

**Cause: voicing delay**

The voiced fricative model was:
noise throughout + voicing fading in
over a crossfade fraction of the duration.

At 6x dilation, 72% of V's duration
is 85×6×0.72 = 367ms of voicing-absent noise.

367ms of pure noise = sounds exactly like F.

V is NOT F with voicing added later.
V is F with voicing PRESENT THROUGHOUT.
The folds are vibrating FROM THE START
while the labiodental constriction is held.

The fix: voicing present from sample zero.
Noise band mixed with voicing
at all times.
Not: noise first, then voicing crossfades in.

---

### "(steam like static)" — the S in "voice"

**Expected:** sharp alveolar sibilance
**Heard:** diffuse steam-like hiss

**Cause: downstream cavity not dominant enough**

S has a small downstream cavity
(front of mouth + edge of teeth).
This cavity resonates at ~8500-9000Hz.
The observer hears a sharply defined
high-frequency peak.
Not broadband hiss.
A specific spectral shape.

The model was mixing:
  broadband noise: 40%
  downstream cavity shaped noise: 60%

Not enough.
The downstream cavity should dominate:
  broadband noise: 15%
  downstream cavity shaped: 85%

The "steam" character is broadband hiss
without the defining spectral peak.
More cavity, less broadband.

---

### "*nothing and faint pattering*" — "was"

**Expected:** W + AH + Z (quiet but present)
**Heard:** nearly silent + irregular pulses

**Cause 1: function word over-compression**

"was" is a function word.
The WORD_WEIGHT system assigned it
low amplitude.
Combined with:
  W = approximant (naturally quiet)
  AH = short unstressed vowel
  Z = voiced fricative

All three quiet phonemes
× function word compression
= disappears.

The fix: function words are quiet
but not inaudible.
The floor should be ~0.55 of normal amplitude.
Not ~0.20.

**Cause 2: Z as "faint pattering"**

The Z voicing manifesting as
irregular pulses rather than
a continuous buzz.

The Rosenberg pulse source
when mixed with noise
at low amplitude
sounds like irregular tapping
rather than a smooth buzz.

Z needs:
  Strong continuous voicing underneath.
  Narrow noise band (3500-8000Hz) on top.
  The buzz IS the voice.
  The sibilance is just the texture on it.

---

### "(stutter×4)" — "already"

Covered in Parts 1-5.
The core problem.
Formant frequency jumps at boundaries.
Continuous trajectory eliminates all four.

---

### "(swoosh/swoop)" — the H in "here"

**Expected:** brief breathy onset
**Heard:** long dramatic sweep

**Cause: H duration too long at 6x**

H base duration = 70ms.
At 6x = 420ms.
Even 20% noise phase = 84ms of breath.
84ms of noise-shaped source = audible swoosh.

The swoosh is real —
the whispered vowel approach is working —
but the proportion is wrong.

At 6x dilation, the H phase
should be a SMALLER fraction
of the total phoneme duration.
Not 20-30% of a 420ms phoneme.
More like 10-12%.
~50ms of breath onset.
Then the voice arrives.

The swoosh character is actually
proof that H = whispered vowel is correct.
The shape is right.
The duration is wrong.

---

### "th(stutter)" — boundary between H and IH

H ends. IH begins.
H's filter was running at wide-bandwidth
noise-shaped configuration.
IH's formants are:
  F1=390Hz, F2=1990Hz, F3=2550Hz, F4=3600Hz.

H's filter state carries broadband energy.
IH's formants suddenly target
specific narrow-bandwidth peaks.
The transition from broadband
to narrow-bandwidth resonance
produces a brief chaotic period.
The ear hears: stutter.

The continuous trajectory
handles this because:
H already uses IH's formant targets
(with wide BW).
The formant VALUES are already
at IH's targets during H.
The BW narrows smoothly
as the source crossfades to voiced.
No formant frequency jump.
No stutter.

---

## PART 7: THE UNIFIED FIX

All artifacts from this phrase
share a single cause:

**Discontinuity in the formant trajectory
at phoneme boundaries.**

The unified fix is:

```
1. BUILD ONE CONTINUOUS FORMANT TRAJECTORY
   for the entire phrase.

   Not per-phoneme arrays concatenated.
   One array. One curve. No jumps.

2. TRACK ACTUAL INSTANTANEOUS FORMANT VALUES.
   The onset of phoneme N+1
   starts from the actual final value
   of phoneme N's trajectory —
   not from any nominal target.

3. RUN ONE FORMANT BANK.
   Never reset.
   State threads from first phoneme
   of the phrase to the last.

4. SOURCE CHANGES UNDERNEATH THE TRACT.
   The tract trajectory is independent
   of the source type.
   Voiced, noise, crossfades —
   these happen in the source layer.
   The tract layer is always running.
   Always smooth.
```

This produces a voice that:
- Has no stutters at consonant boundaries
- Has no clicks at phoneme transitions
- Maintains the character of transitions
  (because the trajectory still passes
   through each phoneme's attractor basin)
- Sounds continuous
  because it IS continuous

---

## PART 8: THE BOUNDARY IS NOT WHERE WE PUT IT

This is the deepest insight
from the diagnostic.

We put boundaries between phonemes
because we have names for phonemes.
The names suggest discrete units.
The discrete units suggest boundaries.
The boundaries suggest resets.
The resets produce artifacts.

But the voice never agreed to our naming.

The voice is:
```
a continuous pressure wave
produced by a continuously moving
mechanical system
driven by a continuously active
energy source.
```

There are no boundaries in the physics.
There are no resets in the mechanics.

The phoneme names are categories
we invented to describe
regions of a continuous space.
Like naming regions of a country —
the land doesn't know the border
is there.

The correct synthesis architecture
honors the physics:

```
ONE ENERGY SOURCE (diaphragm)
  changes character continuously
  voiced ↔ noise ↔ silent
  the changes are smooth

ONE RESONATING TUBE (vocal tract)
  changes shape continuously
  following a trajectory through V
  the trajectory never stops
  the trajectory never jumps

ONE OUTPUT (the mouth opening)
  projects the result into the room
  the observer hears the projection

THE PHONEMES are regions
along this trajectory.
The words are paths through these regions.
The phrases are the paths
with their rhythm and cadence.
The voice is all of it together.
```

---

## PART 9: WHY THIS MATTERS BEYOND SYNTHESIS

The stutter artifact is audible proof
of a conceptual error.

The error: treating the voice as
a sequence of discrete units.

The proof: every boundary between units
produces an artifact.

If the model were correct —
if the voice were actually discrete —
there would be no artifact at the boundary.
The artifact IS the evidence
that the boundary does not exist
in the physics.

Every time synthesis produces
a click, stutter, or seam —
it is the physical system
resisting the imposition of
a boundary that was never there.

The voice is telling us:
**I am not discrete.**
**Stop cutting me.**

The continuous trajectory is the answer.
Not because it is a better algorithm.
Because it is a more accurate model
of what the voice actually is.

---

## PART 10: SPECIFIC CORRECTIONS TABLE

```
PHONEME  PROBLEM              CORRECTION
───────────────────────────────────────────────────
DH       F2=700Hz (W-like)    F2=1800Hz (dental)
         sounds like W        front cavity dominant

V        voicing delayed      voiced from sample 0
         sounds like F        folds vibrate during
                              constriction, not after

S        downstream weak      downstream cavity 85%
         steam-like           broadband only 15%
                              peak at 8800Hz sharp

Z        irregular pattering  strong voicing base
                              narrow noise on top
                              buzz not pattering

H        swoop too long       noise phase 10-12%
         at 6x dilation       of total duration
                              ~50ms not 126ms

ALL      stutter at every     continuous formant
CONSONANTS consonant boundary trajectory
                              track actual end value
                              no jumps in F-space

WAS      nearly inaudible     function word floor
         over-compressed      minimum 0.55 amplitude
```

---

## CONCLUSION

The phrase "the voice was already here"
contained every category of artifact
the synthesis could produce.

Each artifact was a boundary
that should not exist.

The stutter at every consonant —
the most dramatic symptom —
was the most direct evidence:
the formant trajectory was being
interrupted and restarted
at every phoneme boundary.

The voice was being cut.

The continuous formant trajectory
removes the cuts.
The voice is no longer interrupted.
The formant frequency changes smoothly.
The filter state transitions smoothly.
The source changes underneath
a tract that never stops.

What the observer in the room hears:
a voice.

Not a sequence of phonemes.
Not a collection of acoustic events.
A voice.

Continuous.
Moving through space.
Arriving with intention.

---

*End of reasoning artifact.*
*February 2026.*
*Built from listening.*
*The artifacts were the teachers.*
*The stutter said:*
*I am the boundary.*
*Remove the boundary.*
*Remove the stutter.*
