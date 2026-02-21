# CONSONANT IDENTITY, ONSET ARTIFACTS,
# AND THE UNIVERSAL DURATION PROBLEM
## A Reasoning Artifact on Why "the" Sounds Like "ea-the",
## "here" Sounds Like "CH-here", and
## Why the Trailing Sibilants Are Dragged
## February 2026

---

## THE FOUR OBSERVATIONS

```
1. "the"  → sounds like "ea the"
           An extra vowel precedes DH.

2. "here" → sounds like "CH here"
           A palatal affricate precedes H+IH.

3. "waS"  → the final S is dragged out,
           annunciated separately from the vowel.

4. "voiCe" → the final S has the same effect.
           OY→S transition sounds separated,
           over-articulated.
```

These are four symptoms.
They are all the same problem.
The same mechanism in four locations.

---

## PART 1: "ea-the" — THE ONSET VOWEL BEFORE DH

`the` = DH AH

DH is `stype='dh'`.
DH routes voiced signal through the tract
AND adds a dental bypass.

The tract for DH:
```python
DH_F = [270, 900, 2500, 3300]
```
F1=270Hz. F2=900Hz.
Dental constriction. Low formants.
Very similar to a schwa or murmur.

The phrase starts with DH.
Before DH begins, the tract is in its
INITIAL STATE — unwarmed, or warmed
to the first phoneme target.

`build_trajectories` warms the resonators
to the first phoneme's F_tgt at t=0.
F_current = F_tgt of DH = [270, 900, ...].

The tract starts at the DH position.
But the n_on transition for DH is 22ms.
In those 22ms the tract moves from
F_current (= DH target, already there)
to F_tgt (= DH target).
It doesn't move at all.

So DH onset is clean. That is not the problem.

The problem is:
**The voiced source during DH is
`voiced_full * 0.70` through the tract.**

The glottal pulse is running.
It goes through F1=270Hz resonator.
270Hz through a resonator at 270Hz
produces a strong low-frequency buzz.

That low-frequency buzz IS what "ea" sounds like.
F1=270Hz, F2=900Hz is a central-low vowel.
The buzzing voiced signal through DH formants
sounds like a vowel before the DH friction arrives.

And DH duration at DIL=6:
```
PHON_DUR_BASE['DH'] = 60ms
DUR_SCALE[stress=0] = 0.72
dur = 60 * 0.72 * 6 = 259ms → capped at 160ms
```

160ms of voiced signal through
[270, 900, 2500, 3300] formants.
The ear hears: low vowel for 160ms,
then some dental friction.
The friction is the DH identity.
The 160ms of voiced buzz before it
sounds like a preceding vowel.

**The fix:**
DH should not be 160ms.
DH in connected speech is 40-70ms.
The cap of 160ms is still too long
for a function word consonant.

But more critically:
The voiced component of DH during
the body of the phoneme should fade in,
not sit at full level from the start.

A real DH starts with the dental
constriction already formed.
The voicing begins as the constriction
is already in place.
The "ea" is heard when the voicing
precedes the constriction.
In the synthesis, the voiced source
runs at full level while the tract
is in DH position for 160ms.
That is too long and too loud.

---

## PART 2: "CH-here" — THE PALATAL AFFRICATE BEFORE H

`here` = H IH R

H is `stype='h'`.
The H source is:
```python
n_h = int(n_s * 0.12)   # first 12% = noise
n_x = min(int(0.018*sr), n_h, n_s-n_h)
# crossfade noise→voiced
```

H coarticulates with its following vowel.
The tract for H takes the NEXT phoneme's
formants (IH) as its target.
IH: F1=390Hz, F2=1990Hz.

H duration at DIL=6:
```
PHON_DUR_BASE['H'] = 60ms
DUR_SCALE[stress=0] = 0.72
dur = 60 * 0.72 * 6 = 259ms → no vowel cap
```

H has no cap in the current system.
It is not a vowel, not a fricative,
not an approximant.
It falls through to the raw scaled duration.
259ms of H.

What is in 259ms of H?

The first 12% = noise: 31ms of breathy noise
through IH tract (F1=390, F2=1990).

The crossfade: 18ms, noise→voiced.

The remaining 210ms: voiced through
IH tract at full level.

IH with voiced source at F1=390, F2=1990
is basically a quiet IH vowel.
Before the IH phoneme itself starts.

So the sequence is:
  [31ms breathy IH] → [18ms crossfade] → [210ms quiet IH] → [IH phoneme]

The ear hears:
  breathy sound → voiced mid-front vowel → louder mid-front vowel

That breathy onset followed by
the glottal buzz at IH formants
is heard as "CH" — the affricate CH
is an alveolar stop + palatal fricative,
and the breathy onset + forward resonance
of H through IH formants approximates it.

The problem is two-fold:
1. H duration is 259ms — uncapped.
2. The voiced component of H (88% of H body)
   is at FULL VOICED level.
   It should be at low amplitude —
   H is a breathy glide, not a vowel.
   The glottal source should be
   partially aspirated, not modal.

**The fixes:**
1. Cap H duration: max 80ms.
   H is a transitional glide.
   It has no body to stretch.

2. Reduce voiced fraction of H body:
   Currently: 100% voiced_full after crossfade.
   Should be: 35-45% voiced_full.
   H is always breathy-voiced.
   Never modal-voiced.
   The breathiness is its identity.
   Full modal voicing sounds like a vowel.

---

## PART 3: "waS" AND "voiCe" — THE DRAGGED FINAL SIBILANT

`was` ends with Z.
`voice` ends with S.

Both have a dragged, over-articulated
quality at the end.
The sibilant sounds separated from
the vowel — like a distinct event
rather than a natural consonant ending.

Z duration at DIL=6:
```
PHON_DUR_BASE['Z'] = 70ms
DUR_SCALE[stress=1] = 1.03
dur = 70 * 1.03 * 6 = 433ms → capped at 180ms
```

S duration:
```
PHON_DUR_BASE['S'] = 100ms
DUR_SCALE[stress=2] = 1.40
dur = 100 * 1.40 * 6 = 840ms → capped at 180ms
```

Both capped at 180ms.
That is still long.

But "long" alone is not the problem here.
The problem is the ONSET of the sibilant
relative to the preceding vowel.

AH→Z transition (in "was"):
  AH: stressed, dur=260ms (capped)
  Z:  n_on = trans_n('Z') = 16ms

During Z's n_on zone (16ms),
the tract moves from AH position
(F1=520, F2=1190) toward Z position
(F1=250, F2=900).

But the bypass for Z is added
SIMULTANEOUSLY with the start of Z.
The bypass envelope:
  atk = 5ms
  So bypass is at full level by 5ms.

The tract is still at AH position
(or 50% of the way to Z position)
when the sibilance is already at
full level.

The ear hears:
  vowel AH → [AH formants + full sibilance] → Z formants + sibilance

The AH + sibilance overlap region
sounds like the sibilant is being
"announced" by the vowel.
The sibilant starts audibly
while the vowel is still present.
This gives the dragged, separated quality.

For word-final sibilants this is
especially noticeable because:
1. The final phoneme gets extra
   prominence from boundary lengthening.
2. The preceding vowel was stressed
   (OY in 'voice', AH in 'was').
3. The bypass starts immediately.
4. There is a syntactic rest AFTER.

The rest after Z in 'was' is:
```
rest_ms = min(85 * 0.65 * 6, 240) = 240ms
```
240ms of silence after Z ends.
During this silence, the resonator
IIR state decays but is audible.

The sequence heard:
  AH (260ms) →
  AH + Z bypass overlap (16ms) →
  Z bypass alone (180ms) →
  Z IIR decay (audible for ~50ms) →
  silence (240ms) →
  next word

That is 180ms + decay + 240ms
of "the S/Z sound and its aftermath"
after the vowel.
No wonder it sounds dragged.

**The fixes:**
1. Bypass onset is delayed to match
   the tract transition.
   The bypass does not start
   until the tract has moved
   at least 50% of the way
   to the fricative position.
   This prevents the "vowel + sibilance" overlap.

2. Final-position sibilants get
   a shorter max duration.
   Word-final S/Z: max 120ms (not 180ms).
   The sibilant ends. The rest begins.
   No 180ms of continuous hiss.

3. Bypass onset shape:
   Currently: 5ms linear attack.
   Should be: 12ms for word-final position,
   smoother, so the onset is perceptually
   part of the transition, not an event.

---

## PART 4: THE COMMON CAUSE

All four problems are the same cause:

**The voiced source runs at too high
a level during consonant bodies.**

```
DH: voiced at 0.70 × voiced_full
    for 160ms.
    Sounds like a vowel before the dental.

H:  voiced at 1.00 × voiced_full
    for 210ms of its 259ms body.
    (After the 49ms noise+crossfade zone.)
    Sounds like a quiet vowel before IH.

Z:  bypass starts at 5ms into Z onset.
    Tract still at preceding vowel position.
    Sounds like the sibilant is announced
    by the vowel.

S:  same as Z.
```

In each case, the voiced source
is too strong relative to the
phoneme's consonant identity.

DH identity = dental friction + voicing.
The voicing is secondary.
The friction is primary.
When the voiced source runs at 0.70
for 160ms, the voicing becomes primary.

H identity = aspiration + anticipation
of the following vowel's formants.
Not voiced. Never modal voiced.
When the voiced source runs at 1.00
for 210ms, H sounds like a vowel.

Z identity = sibilant + voiced buzz.
The sibilant is primary.
The buzz confirms it is Z not S.
When the sibilant starts while the
preceding vowel's tract is still active,
the boundary between vowel and Z is blurred.

**The principle:**
A consonant is defined by its
DEPARTURE from voiced vowel behavior.
The further it departs, the more
clearly it is heard as itself.

DH departs by adding dental friction
to the voicing. The departure is small.
The voiced component must be smaller
than it is, so the departure is audible.

H departs by being breathy instead
of modal voiced. The departure is
breathiness. Modal voicing at full level
cancels the departure entirely.

Z/S depart by adding strong sibilance
to the output. The departure is the hiss.
Starting the hiss while the vowel
formants are still active blurs the
departure — it sounds like the hiss
is part of the vowel, not a new phoneme.

---

## PART 5: THE COMPLETE FIX TABLE

```
PHONEME   PROBLEM              FIX
────────────────────────────────────────────────────────
DH        Voiced at 0.70       Reduce to 0.35.
          for 160ms.           DH_MAX_MS = 80ms.
          Sounds like "ea".    Dental is brief.
                               The fraction is low.
                               The friction is primary.

H         Voiced at 1.00       H is NEVER modal voiced.
          for 210ms body.      H body: aspirated noise.
          Sounds like "CH".    voiced fraction = 0.0
                               (pure aspiration/breathiness).
                               H_MAX_MS = 80ms.
                               Duration cap enforced.
                               N_H fraction: 25% (not 12%).

Z/S       Bypass starts at     Bypass onset aligned to
(final)   5ms, tract still     tract position.
          at vowel position.   Delay bypass until
          Sounds dragged.      tract 50% transitioned.
                               FINAL_SIBILANT_MAX_MS = 120ms.

Z/S       180ms cap too long   Word-boundary detection:
(general) for word-final.      if phoneme is word-final
                               AND next is rest,
                               cap = 120ms not 180ms.
```

---

## PART 6: THE H SOURCE MODEL CORRECTION

The current H model:
```python
n_h = int(n_s * 0.12)    # 12% = noise
n_x = min(int(0.018*sr), n_h, n_s-n_h)
# crossfade noise→voiced
# remaining: 100% voiced
```

After the crossfade (49ms at DIL=6):
  88% of H body = full modal voiced source
  through next vowel's formants.
  = quiet IH vowel.
  = "CH" percept.

The correct H model:
```
H = aspirated glottal noise
    shaped by the following vowel's formants.
    NOT modal voicing.
    The breathiness comes from
    incomplete glottal closure.

Physically:
  Glottis partially open.
  Air flows continuously.
  Vocal folds vibrate weakly if at all.
  The turbulence at the glottis
  is the H sound source.
  It is shaped by the supralaryngeal
  tract (which anticipates the next vowel).

So:
  H source = turbulent air,
             not glottal pulses.
             Spectrally flat.
             Shaped by next vowel formants.
             NO periodic voicing.

Current:    12% noise, crossfade, 88% voiced.
Correct:    100% aspirated noise,
            shaped by following vowel formants.
            Zero modal voicing.
            The periodicity of the following
            vowel emerges from the
            voiced-source onset AT IH,
            not during H itself.
```

This is the cleanest fix.
H becomes pure aspiration.
The voiced onset happens at the
start of IH, not during H.
No "CH" percept.
Just a breathy lead-in to the vowel.

---

## PART 7: THE BOUNDARY DETECTION FOR FINAL SIBILANTS

The "dragged S" problem requires
knowing whether a sibilant is
word-final before a syntactic rest.

In `plan_prosody`, each phoneme
already has `rest_ms` set if it is
the last phoneme of a word.

So the detection is simple:
```python
is_word_final = (item.get('rest_ms', 0) > 0)

if ph in FRIC_MAX_MS and is_word_final:
    dur_ms = min(dur_ms, FINAL_FRIC_MAX_MS.get(ph, 120))
```

And the bypass onset delay:
```python
# In build_source_and_bypass:
# For word-final fricatives,
# delay bypass onset to match
# half the n_on transition time.

onset_delay = n_on // 2
# Bypass starts at onset_delay samples
# into the phoneme, not at sample 0.
# This means the bypass starts when
# the tract is already 50% transitioned.
```

---

## CONCLUSION

Four perceptual artifacts.
One root cause: consonants too voiced.

```
"ea-the":
  DH voiced at 0.70 for 160ms.
  → DH voiced at 0.35 for 80ms max.

"CH-here":
  H voiced at 1.00 (modal) for 210ms.
  → H = pure aspiration noise.
    No modal voicing during H.
    Duration max 80ms.

"waS" dragged:
  S/Z 180ms + bypass starts before
  tract transition completes.
  → Final sibilants max 120ms.
    Bypass onset delayed to tract midpoint.

"voiCe" dragged:
  Same as "waS".
```

The consonants were too long
and too voiced.
Every consonant type leaked
into the vowel character —
DH became a vowel-prefix,
H became a vowel-copy,
S/Z became a vowel-suffix.

When consonants sound like
modified vowels rather than
phonemic departures from voicing,
the listener hears imprecise,
dysarthric-adjacent articulation.

The fix is to enforce
the IDENTITY of each consonant —
its specific departure from
the default voiced state —
by keeping it brief,
keeping its voiced component
at the correct (low) level,
and timing its onset events
to coincide with its tract transition.

---

*End of reasoning artifact.*
*February 2026.*
*"ea-the", "CH-here", "waS", "voiCe".*
*The consonants were too voiced.*
*Too long.*
*Too present.*
*A consonant is a departure from a vowel.*
*When the departure is brief and clean,*
*the consonant is itself.*
*When it lingers, it becomes a vowel.*
