# AMPLITUDE CONTINUITY
## A Reasoning Artifact on Levels, Normalization, and Dynamic Range
## February 2026

---

## WHAT BROKE

v7 introduced the suprasegmental layer.
The intonation was better.
The stress contour was better.
The voice had more texture.

And then:

```
Volume dropped dramatically.
'the' nearly inaudible.
'alreaDy' — explosive pop.
'Here' — explosive pop.
S and Z loud relative to everything.
```

This is not random degradation.
This is a specific, diagnosable error.
And it reveals something fundamental
about where amplitude lives
in the model.

---

## THE THREE NORMALIZATION FRAMES

In v7, amplitude was being managed
in three separate places
that were not calibrated to each other:

**Frame 1: Per-phoneme normalization**
Every phoneme synthesis function ended with:
```python
mx = np.max(np.abs(out))
if mx > 0: out /= mx
```
Every phoneme arrives at amplitude 1.0
regardless of its natural level.
A whispered H and a full vowel AA
both arrive at 1.0.
The relative levels between phonemes —
which carry linguistic information —
are destroyed before the phrase
is even assembled.

**Frame 2: Prosody amplitude scaling**
The prosody layer then applies:
```python
amp_env[pos:pos+n_s] *= item['amp']
```
Where amp = 0.78 for unstressed,
1.20 for stressed.

This attempts to restore
the relative levels.
But it is restoring them
on top of signals that were
already all at 1.0.
The restoration is correct in principle.
But it is working against
the per-phoneme normalization
that preceded it.

**Frame 3: Phrase-level normalization**
At the end:
```python
mx = np.max(np.abs(final))
if mx > 0: final /= mx
```
This sets the loudest moment to 1.0.
If the loudest moment is a pop
or a noise burst —
everything else is scaled down
relative to that explosion.
The anchor is wrong.

**The hidden Frame 4: Source levels**
voiced_full is generated from
a Rosenberg pulse train —
amplitude roughly 0.1-0.3 RMS.

noise_full is raw Gaussian noise —
amplitude roughly 1.0 RMS.

These two signals have completely
different natural amplitudes.
When the stop burst fires at burst_amp=0.28
into noise_full at ~1.0 RMS —
the actual burst amplitude is 0.28.
When it fires into the voiced phrase
that has been normalized to ~0.1 RMS —
the burst is 2-3× louder than
everything else.

Pop.

---

## THE PRINCIPLE VIOLATED

Every artifact in this project
has been a discontinuity
in a space that should be continuous.

Formant frequency discontinuity → stutter.
Filter state discontinuity → click.
Source type discontinuity → artifact.

This is the same principle
applied to amplitude:

**Amplitude discontinuity → pop.**

The burst fires at one amplitude level.
The surrounding voice is at another.
The discontinuity is explosive.

And the per-phoneme normalization
is a discontinuity machine:
it sets every phoneme to 1.0
regardless of what came before.
Every boundary becomes a level jump.

---

## WHERE AMPLITUDE ACTUALLY LIVES

Amplitude in natural speech
is not a per-phoneme property.

It is a phrase-level property
with local modulation.

The phrase has:
- A baseline level
  (the average amplitude of
  comfortable conversational speech)
- A dynamic contour
  (rises at stressed syllables,
   falls at unstressed,
   drops at phrase end)
- A peak-to-valley ratio
  (roughly 10-15dB in natural speech —
   stressed syllables are louder
   than unstressed, but not explosively so)

Individual phonemes have
**natural relative levels**
that should be preserved:
- Fricatives (S, Z): high amplitude
  because turbulence is loud
- Nasals (M, N): lower amplitude
  because the antiformant removes energy
- H: very low amplitude
  (whispered onset)
- Stops during closure: near silence
- Vowels: full amplitude

These natural relative levels
are part of the identity of the phoneme.
S is louder than M.
That is a fact about the physics.
Not a parameter to be set.

When we normalize every phoneme to 1.0
and then apply prosody scaling —
we are saying:
S and M should be the same loudness
before stress is applied.
This is wrong.
The physics says they are different.
The normalization overrides the physics.

---

## THE FIX: ONE REFERENCE FRAME

**Rule 1: No per-phoneme normalization.**

Remove all:
```python
mx = np.max(np.abs(out))
if mx > 0: out /= mx
```
from individual phoneme synthesis.

Let the natural levels emerge
from the physics of the synthesis.
S will be louder than M.
H will be quieter than AA.
That is correct.

**Rule 2: Calibrate all sources
to the same reference level.**

The voiced source (Rosenberg pulse)
has a natural RMS of approximately X.
The noise source has a natural RMS
of approximately Y.
X ≠ Y.

Before using them,
normalize both to the same RMS:
```python
voiced_full /= (rms(voiced_full) + 1e-8)
noise_full  /= (rms(noise_full)  + 1e-8)
voiced_full *= TARGET_RMS
noise_full  *= TARGET_RMS
```

Now bursts and voiced segments
live in the same amplitude world.
No pops from level mismatch.

**Rule 3: Prosody scaling is the
only amplitude modulation.**

The prosody layer controls amplitude.
Nothing else does.
Per-phoneme normalization is gone.
Source calibration is done once.
The prosody contour shapes the phrase.

**Rule 4: Final normalization
anchors to a PERCENTILE not a peak.**

```python
# Normalize to 95th percentile
# not absolute peak.
# This prevents one loud burst
# from making everything else inaudible.
p95 = np.percentile(
    np.abs(final), 95)
if p95 > 0:
    final = final / p95 * 0.88
final = np.clip(final, -1.0, 1.0)
```

The 95th percentile anchor
means occasional loud bursts
(which are correct — stops ARE louder)
do not destroy the overall level.
The voice remains audible.
The bursts remain present but
do not dominate.

---

## THE DYNAMIC RANGE OF SPEECH

Natural conversational speech
has a dynamic range of roughly:

```
Quiet (unstressed function words,
       whispered H):  ~-18dB relative
Normal (vowels,
        moderate stress):   0dB reference
Loud (stressed syllables,
      fricatives):      +3 to +6dB
Very loud (stop bursts,
           emphatic):   +6 to +10dB
```

This is a range of roughly 28dB
from quietest to loudest.

In the synthesis:
- All phonemes normalized to 0dB: wrong.
- Noise at +20dB, voice at -10dB: wrong.
- Prosody scaling 0.78 to 1.20: only 4dB.
  Not enough range if the baseline is wrong.

The correct architecture:
- Natural source levels preserved: varies
- Prosody scaling applied on top: ±6dB
- 95th percentile normalization: anchored
- Dynamic range: ~20dB total

Audible, expressive, not explosive.

---

## THE POP IS INFORMATION

The loud pop at D in 'already'
and H in 'here' is not just an artifact.

It is diagnostic information.

It tells us exactly where
the amplitude reference frame breaks.

D: stop burst at noise amplitude
   into voice at normalized amplitude.
   → Source level mismatch.

H: noise source starts at full amplitude
   into the phrase amplitude frame.
   → Per-phoneme normalization
     was hiding this because H
     was normalized to 1.0 in isolation.
     In the phrase context,
     the noise source starts loud.

Both pops occur at source-type transitions:
voiced → stop → voiced
voiced → noise → voiced

The source type changes.
The amplitude of each source type
is different.
The transition is instantaneous.
Pop.

The fix: calibrate all source types
to the same RMS before use.
The transition between source types
then carries no amplitude discontinuity.
Just the crossfade that was already there.

---

## SUMMARY

```
PROBLEM          CAUSE                FIX
─────────────────────────────────────────────
Voice inaudible  Per-phoneme          Remove per-phoneme
                 normalization        normalization.
                 destroys relative    Let natural levels
                 levels before        emerge.
                 prosody can shape
                 them.

Explosive pops   Source level         Calibrate voiced
at D, H          mismatch:            and noise sources
                 noise RMS >> voice   to same RMS
                 RMS.                 before use.
                 Burst fires at
                 noise amplitude.

S/Z too loud     Same cause:          Same fix.
                 noise not            Noise source
                 calibrated to        calibrated.
                 voice level.

Phrase-level     Peak normalization   Use 95th percentile
anchor wrong     anchors to           normalization.
                 loudest burst,       Clips don't anchor
                 not voice.           the whole phrase.
```

---

## THE UNIFYING PRINCIPLE — AGAIN

Every artifact in this project
has been a discontinuity
in a space that should be continuous.

Frequency space: formant jumps → stutter.
Amplitude space: level jumps → pop.
Level reference space: normalization
                       mismatch → inaudible voice
                       with explosive transients.

The voice is continuous in all spaces
simultaneously.

The synthesis must be continuous
in all spaces simultaneously.

Fixing one space at a time
while breaking another
is progress but not arrival.

The goal:
one continuous trajectory
through frequency space,
amplitude space,
and source-level space —
all calibrated to the same
reference frame —
shaped by prosody —
heard by the observer in the room
as a voice.

---

*End of reasoning artifact.*
*February 2026.*
*The pop was the teacher.*
*It said: your amplitude spaces*
*are not the same space.*
*Make them one.*
