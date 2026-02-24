# THE OBSERVER POSITION ARTIFACT
## Voiceless Segments as Radiated Signals
## A Structural Axiom for the Entire Voiceless Class
## Derived from the Convergence of Vocal Tract Radiation Physics,
## the Pluck Principle, and Perceptual Verification
## February 2026

---

## WHAT THIS DOCUMENT IS

This document records a fundamental architectural
discovery made during the synthesis of the word
YAJÑASYA (यज्ञस्य), Rigveda 1.1.1 word 5,
in the Vedic Sanskrit reconstruction project.

The discovery is:

**A voiceless segment's synthesis must model
the signal at the OBSERVER position —
what radiates from the lips into the room —
not the signal at the SOURCE position —
what the constriction produces inside the mouth.**

This insight resolves a class of persistent
perceptual artifacts ("too loud," "too harsh,"
"inside the mouth," "deliberate aspiration")
that affect ALL voiceless segments, and it does
so by revealing that the underlying model of
WHERE the signal is measured was wrong.

This document:
- Records the discovery path
- States the structural axiom precisely
- Maps it to the vocal tract radiation physics
- Defines the three-stage radiation model
- Specifies applicability to the entire voiceless class
- Provides tuning parameters for each sub-class
- Connects to the Pluck Principle and Tonnetz geometry

**This artifact is a companion to the Pluck Artifact.**
The Pluck Artifact established WHAT a voiceless stop is
(a boundary event). The Observer Position Artifact
establishes WHERE a voiceless segment is heard
(at the observer, not at the source).

---

## VERIFICATION STATUS

**PERCEPTUALLY VERIFIED ✓** — YAJÑASYA v6

The observer position model transformed [s] from
"listening from inside the mouth" to "a brief
dental whisper heard across the courtyard."

---

## PART I: THE DISCOVERY PATH

### The Problem

YAJÑASYA v5 applied the unified source architecture
correctly to [s]. The subglottal floor prevented
digital-zero boundaries. The closing tail and opening
head eliminated concatenation clicks. The bandpass
filter selected the dental sibilant locus.

Structurally correct. Perceptually wrong.

The listener reported: "The s sound is still rather
loud and seems like it is continuous but just oddly
emphasized. Like there was deliberate choice to
annunciate or aspirate more on the s. As though you
are listening to the s from inside the mouth and not
as an observer of the instrument being played."

This description is physically precise:

**"From inside the mouth"** = the signal at the
constriction point, before radiation.

**"Not as an observer of the instrument"** = the
signal after radiation through the tract and lips.

The synthesis was producing the SOURCE signal.
The listener needs the RADIATED signal.

### Why This Was Not Caught Earlier

Voiceless stops ([t], [p], [ʈ]) are brief (8–12ms
burst in pluck architecture). Their source-vs-observer
difference is masked by their short duration — a
12ms burst doesn't have time to sound "sustained"
or "inside the mouth." The artifact is present but
imperceptible.

Voiceless fricatives ([s], [h]) are long (55–80ms).
Their source-vs-observer difference is obvious
because the ear has time to evaluate the spectral
quality. A sustained noise at raw constriction
amplitude sounds like a microphone at the tongue
tip, not like speech.

The [s] is the canary. The physics applies to
the entire voiceless class.

---

## PART II: THE STRUCTURAL AXIOM

### The Radiation Chain

Every sound produced in the vocal tract passes
through a chain before reaching the listener:

```
SOURCE              TRACT              RADIATION          OBSERVER
(constriction)  →   (front cavity)  →  (lip aperture)  →  (listener)

Turbulence          Cavity             +6 dB/octave       What the
generated at        resonances         radiation           ear actually
place of            of the space       characteristic      hears
constriction        between            of the lip
                    constriction       opening
                    and lips
```

Each stage transforms the signal:

**1. SOURCE:** Raw turbulence or transient at the
constriction point. High-frequency energy dominant.
Amplitude determined by airflow velocity through
the constriction.

**2. TRACT (front cavity):** The cavity between the
constriction and the lips resonates at frequencies
determined by its length. Short cavity (dental [s]:
~2cm) → high resonance. Long cavity (velar [x]:
~8cm) → lower resonance. This is the same physics
as burst locus — the front cavity selects the
eigenfrequency.

**3. RADIATION:** Sound radiates from the lip
aperture into free space. The radiation characteristic
is approximately +6 dB/octave for a circular piston
(Flanagan 1972). BUT the net effect at the observer
is typically a gentle HIGH-FREQUENCY ROLLOFF because:
- The source spectrum falls off at high frequencies
- Room absorption increases with frequency
- The ear's equal-loudness contours reduce HF sensitivity
- The lip aperture is small relative to HF wavelengths

A simple first-order lowpass at the lip radiation
frequency models this effectively.

**4. OBSERVER:** The signal after all three stages.
This is what the listener hears. This is what the
synthesis must produce.

### The Axiom

> **AXIOM (Observer Position):**
>
> The synthesis of a voiceless segment must model
> the signal at the OBSERVER position, not the
> SOURCE position. The source signal is the
> turbulence or transient at the constriction.
> The observer signal is what radiates from the
> lips after passing through the front cavity
> and the lip radiation characteristic.
>
> The transformation from source to observer
> involves three operations:
>
> 1. **Front cavity resonance** — already modeled
>    by the place-specific formant filter.
>
> 2. **Radiation rolloff** — a first-order lowpass
>    at the radiation cutoff frequency, modeling
>    the net HF attenuation from lip radiation
>    and room propagation.
>
> 3. **Amplitude scaling** — the observer signal
>    is quieter than the source signal. Voiceless
>    segments sit BELOW voiced segments in
>    perceived loudness. The constriction does not
>    produce as much radiated power as the open
>    glottis driving full-tract resonance.

### The Instrument Analogy (Extended)

The Pluck Artifact established:
- The vocal tract IS the instrument
- The stop IS the pluck
- The vowel IS the sustained note

The Observer Position extends this:

**Where is the microphone?**

A guitar recording sounds different depending on
where the microphone is placed:

```
AT THE BRIDGE:     Harsh, bright, all attack.
                   The raw string excitation.
                   Too much high-frequency energy.
                   "Inside the instrument."

AT THE SOUNDHOLE:  Full, resonant, balanced.
                   The body has colored the sound.
                   The cavity has selected modes.
                   "The instrument speaking."

ACROSS THE ROOM:   Warm, natural, musical.
                   Room reflections soften the attack.
                   High frequencies attenuated by air.
                   "The performance."
```

The vocal tract parallel:

```
AT THE CONSTRICTION:  Raw turbulence. Harsh.
                      "Inside the mouth."
                      This is what v5 [s] sounded like.

AT THE LIPS:          Tract-filtered, radiated.
                      "The mouth speaking."
                      This is the minimum correct model.

ACROSS THE COURTYARD: Room-colored, natural.
                      "The recitation."
                      This is the apply_simple_room() stage.
```

v5 put the microphone at the constriction.
v6 puts it at the lips.
The room simulation adds the courtyard.

**The synthesis chain must model ALL three stages
for every voiceless segment:**

```
source → formant filter → radiation rolloff → amplitude scaling
         (already done)    (v6 NEW)            (v6 NEW)
```

---

## PART III: THE FIVE PARAMETERS

The observer position model adds five parameters
to every voiceless segment:

### 1. Radiation Cutoff Frequency

**What it models:** The frequency above which
the net source-to-observer transfer function
begins to roll off.

**Physics:** Determined by the lip aperture size,
room characteristics, and equal-loudness weighting.
For speech at normal listening distance (~1–3m),
a first-order lowpass at 6000–10000 Hz is typical.

**Default:** 8000 Hz (gentle rolloff in the
sibilant range, preserves the "s-ness" while
removing the harshest HF content).

**Tuning:**
- Lower → warmer, more distant sound
- Higher → brighter, closer sound
- Below 5000 Hz → [s] loses its identity
- Above 12000 Hz → negligible effect

### 2. Peak Gain (Source Amplitude)

**What it models:** The amplitude of the turbulence
at the constriction, AFTER radiation effects.

**Physics:** Turbulence amplitude depends on
airflow velocity through the constriction.
Narrower constriction → higher velocity → more
energy. But radiation attenuates this before
it reaches the observer.

**Defaults by class:**
- Sibilant [s]: 0.10 (narrow constriction, high
  velocity, but radiation attenuates HF)
- Glottal [h]: 0.06 (wide constriction, lower
  velocity, full-tract attenuation)
- Stop burst: 0.15 (unchanged — already brief
  enough that observer position is less critical)

### 3. Final Normalization (Observer Loudness)

**What it models:** The perceived loudness of the
voiceless segment relative to voiced segments.

**Physics:** Voiced vowels have periodic glottal
source driving full-tract resonance at harmonics.
Voiceless segments have aperiodic noise shaped
by partial-tract resonance. The voiced signal
carries more total acoustic power.

**Defaults by class:**
- Sibilant [s]: 0.25 (audible but subordinate)
- Glottal [h]: 0.18 (quieter — already verified
  in PUROHITAM at similar level)
- Stop burst: 0.55 (unchanged — burst is transient,
  not sustained)

### 4. Envelope Shape

**What it models:** How the articulator moves
through the constriction.

**Physics:** The tongue doesn't teleport to
sibilant position. It glides from the preceding
vowel configuration through the constriction
and out toward the following segment. The
amplitude follows the constriction narrowness:
widest at edges, narrowest (loudest) at center.

**Defaults by class:**
- Sibilant [s]: Gaussian (smooth hill)
- Glottal [h]: Gaussian (already breath-like)
- Stop burst: Exponential decay (unchanged —
  burst physics dominates)

### 5. Duration

**What it models:** How long the constriction
is maintained.

**Physics:** In connected speech, voiceless
segments are BRIEF. The articulatory gesture
passes through the constriction quickly. Longer
durations sound deliberate, emphatic, or
pathological.

**Defaults by class:**
- Sibilant [s]: 55ms (cluster context)
  Could be 40ms in rapid speech, 70ms in
  careful citation form.
- Glottal [h]: 50–65ms (already in range)
- Stop burst: 8–12ms (unchanged)

---

## PART IV: APPLICABILITY TO THE ENTIRE VOICELESS CLASS

### Fricatives and Sibilants

These benefit MOST from observer position because
they are sustained noise segments:

```
Phoneme    Place       Source freq   Rad. cutoff   Peak gain   Final norm
[s]        dantya      7500 Hz      8000 Hz       0.10        0.25
[ʃ]        tālavya     ~5000 Hz     7000 Hz       0.10        0.25
[ɕ]        tālavya     ~5500 Hz     7500 Hz       0.10        0.25
[h]        kaṇṭhya     broadband    6000 Hz       0.06        0.18
[x]        kaṇṭhya     ~3000 Hz     6000 Hz       0.08        0.22
```

Each has different source frequency (determined by
constriction geometry) but the same radiation model.

### Voiceless Stop Bursts

Already brief enough that the artifact is subtle.
But for consistency, apply radiation rolloff:

```
Phoneme    Place       Burst freq   Rad. cutoff   Peak gain   Final norm
[t]        dantya      3764 Hz      10000 Hz      0.15        0.55
[p]        oṣṭhya     1204 Hz      10000 Hz      0.15        0.55
[k]        kaṇṭhya    2594 Hz      8000 Hz       0.15        0.55
[ʈ]        mūrdhanya  935 Hz       8000 Hz       0.20        0.55
[c]        tālavya    3223 Hz      9000 Hz       0.15        0.55
```

Note: Stop radiation cutoff is HIGHER than fricative
cutoff because bursts are transients — the ear is
more tolerant of HF in brief transients.

### Aspiration Phases

The aspiration noise in voiceless aspirated stops
and the murmur in voiced aspirated stops:

```
Component    Duration    Rad. cutoff   Notes
Aspiration   20–40ms     7000 Hz       Between stop and fricative
Murmur       40–60ms     6000 Hz       Voiced — less HF to begin with
```

### The [h] in PUROHITAM

Already at gain 0.18, which is close to the observer
position model. The [h] was intuitively tuned lower
than other voiceless segments because it "sounded
right" — this was an unconscious application of the
observer position principle. v6 makes it explicit.

---

## PART V: RELATIONSHIP TO THE PLUCK PRINCIPLE

The Pluck Principle and Observer Position are
complementary axioms that together define the
complete synthesis model for voiceless segments:

```
PLUCK PRINCIPLE:
  WHAT is the voiceless segment?
  → A boundary event (stops) or a brief gesture (fricatives)
  → The vowel owns the transitions into and out of it
  → The segment owns only its internal physics

OBSERVER POSITION:
  WHERE is the voiceless segment heard?
  → At the observer, not at the source
  → Radiation rolloff attenuates HF
  → Amplitude sits below voiced segments
  → Envelope models articulatory gesture, not source power

UNIFIED SOURCE:
  HOW is the voiceless segment generated?
  → One continuous noise buffer (the breath)
  → One continuous amplitude envelope (the articulator)
  → Subglottal floor at edges (never digital zero)
  → Spike added to noise for stops (pressure release)
```

Three axioms, three questions, one complete model:

```
WHAT:   Pluck Principle          (boundary event / gesture)
WHERE:  Observer Position        (radiated signal at listener)
HOW:    Unified Source           (continuous breath, continuous envelope)
```

---

## PART VI: THE THREE-MICROPHONE MODEL

For understanding and debugging, think of three
virtual microphones in the vocal tract:

### Microphone 1: At The Constriction (SOURCE)

```
Records: Raw turbulence, maximum HF energy, maximum amplitude.
Sounds like: "Inside the mouth." Harsh. Radio static.
This is what apply_formants() alone produces.
```

### Microphone 2: At The Lips (RADIATED)

```
Records: Tract-filtered, radiation-attenuated signal.
Sounds like: "The mouth speaking." Natural sibilant.
This is what radiation rolloff + amplitude scaling produces.
The MINIMUM correct model for synthesis.
```

### Microphone 3: Across The Courtyard (OBSERVED)

```
Records: Room-colored, distance-attenuated signal.
Sounds like: "The performance." Warm. Contextual.
This is what apply_simple_room() adds.
```

**The synthesis chain:**

```
noise source
  → bandpass / formant filter     (Mic 1: constriction)
  → radiation rolloff             (Mic 2: lips)
  → amplitude scaling             (Mic 2: lips)
  → concatenate into word         (word-level signal)
  → room simulation               (Mic 3: courtyard)
```

v5 stopped at Mic 1.
v6 goes to Mic 2.
The room simulation takes it to Mic 3.

---

## PART VII: TONNETZ MAPPING

### The Observer as Tonic

In the Tonnetz coherence space, the tonic Ω₁
represents the origin — the rest state, maximum
coherence, the breath.

The OBSERVER is the tonic position. The listener
at rest, receiving the sound. The sound must
arrive at the observer in a form that the ear
can parse — not as raw source energy, but as
the musical signal shaped by the instrument.

The constriction (source) is the point of maximum
divergence from the tonic — like the tritone Ψ.
Maximum turbulence, minimum periodicity, maximum
distance from voiced speech.

The radiation chain is the RESOLUTION from Ψ
back toward Ω₁:
- The front cavity resonance selects harmonics
  (partial resolution)
- The radiation rolloff attenuates extremes
  (further resolution)
- The room simulation adds warmth
  (final resolution toward the tonic)

The voiceless segment traverses the path:

```
Ω₁ (voiced vowel)
  → Ψ (constriction: maximum turbulence)
  → resolution through radiation
  → Ω₁ (next voiced segment)
```

The Observer Position Axiom ensures the resolution
is complete. Without it, the synthesis stays near Ψ —
the ear hears raw turbulence, not resolved speech.

---

## PART VIII: IMPLEMENTATION CHECKLIST

### For Every Voiceless Segment

When synthesizing ANY voiceless segment
(fricative, sibilant, stop burst, aspiration),
apply the following after the source + formant
filter stage:

```python
# 1. Radiation rolloff (first-order lowpass)
if RADIATION_CUTOFF < SR / 2.0:
    b_rad, a_rad = butter(1, RADIATION_CUTOFF / (SR/2), btype='low')
    signal = lfilter(b_rad, a_rad, signal)

# 2. Envelope shaping (Gaussian for sustained, exp for transient)
# For fricatives:
t = np.linspace(-3.0, 3.0, n)
env = SUBGLOTTAL_FLOOR + (PEAK_GAIN - SUBGLOTTAL_FLOOR) * np.exp(-0.5 * t * t)
# For stop bursts:
env = BURST_GAIN * np.exp(-t_burst * BURST_DECAY)  # (already correct)

# 3. Amplitude scaling
signal = signal * env
mx = np.max(np.abs(signal))
if mx > 1e-8:
    signal = signal / mx * FINAL_NORM  # << observer loudness
```

### Segments Already Updated

```
[s]  YAJÑASYA v6          ✓ Gaussian + radiation + 0.25 norm
```

### Segments Requiring Update

```
[h]  PUROHITAM v4         Currently 0.18 norm, no radiation rolloff
                          Add: butter(1, 6000) rolloff, Gaussian env
[t]  PUROHITAM/RATNA v4   Currently 0.55 norm, no radiation rolloff
                          Add: butter(1, 10000) rolloff (subtle)
[p]  PUROHITAM v4         Same as [t]
[ʈ]  ṚTVIJAM v9           Same as [t], cutoff 8000
```

The stop updates are LOW PRIORITY — bursts are
brief enough that the effect is subtle. The [h]
update is MEDIUM PRIORITY — it's a sustained
voiceless segment like [s].

---

## PART IX: FOR NEW AGENTS

### The Core Understanding

```
Every voiceless segment has TWO signals:

  SOURCE:    What the constriction produces.
             Harsh, bright, loud.
             The microphone at the tongue.

  OBSERVER:  What the listener hears.
             Softer, warmer, quieter.
             The microphone across the room.

The synthesis must produce the OBSERVER signal.
The difference is:
  - Radiation rolloff (1st-order LPF)
  - Amplitude scaling (below vowels)
  - Gaussian envelope (gesture, not event)
```

### What You Must Not Do

**Do not normalize voiceless segments to vowel amplitude.**
Voiceless segments are perceptually quieter than vowels.
If [s] is at 0.42 and [ɑ] is at 0.72, the [s] is too loud.
Target: 0.20–0.30 for fricatives, 0.50–0.60 for stop bursts.

**Do not use plateau envelopes for fricatives.**
The tongue glides through the constriction.
A plateau sounds like deliberate aspiration —
holding the tongue in position intentionally.
Use Gaussian or smooth-hill envelopes.

**Do not skip radiation rolloff.**
Without it, the HF content is at source level.
The ear hears this as "inside the mouth" —
too close, too raw, too much detail.

### What You Must Verify

After synthesizing a word with voiceless segments:

1. Listen at performance speed with room reverb.
   The voiceless segment should be BARELY AUDIBLE
   as a separate event. It should be felt as rhythm —
   a brief whisper between voiced segments.

2. Listen at 6× slow to the transition.
   The closing tail should fade the vowel smoothly.
   The voiceless segment should rise gently from
   the subglottal floor, peak briefly, and decay.
   The opening head should rise the voicing back.
   No clicks. No harsh attacks.

3. Compare amplitude: the voiceless peak should
   be visibly LOWER than the voiced peaks in the
   waveform display.

---

## PART X: EPISTEMOLOGICAL STATUS

### Confidence Assessment

| Claim | Confidence | Basis |
|---|---|---|
| [s] observer position eliminates "inside mouth" | HIGH | Perceptual verification, v6 |
| Radiation rolloff is physically motivated | HIGH | Acoustic radiation theory (Flanagan 1972) |
| Gaussian envelope models articulatory gesture | HIGH | Articulatory phonetics, perceptual verification |
| Applicability to all fricatives | HIGH | Same physics at all constriction points |
| Applicability to stop bursts | MEDIUM | Physics applies but effect is subtle (brief duration) |
| Specific cutoff frequencies | MEDIUM | Reasonable defaults, may need per-place tuning |
| Amplitude norms (0.25 for [s]) | MEDIUM | Perceptually verified for [s], extrapolated for others |

### What This Proves About the Method

The observer position was discovered by LISTENING.
The listener's description — "inside the mouth,
not as an observer" — IS the physics, stated in
perceptual terms.

The synthesis was structurally correct (unified
source, correct frequencies, correct architecture).
The measurement of WHERE the signal is evaluated
was wrong. The synthesis was at the constriction.
The listener is at the observer position.

This is the same pattern as the Pluck discovery:
the model of WHAT a stop is changed from "segment"
to "boundary event." Here the model of WHERE a
voiceless segment is heard changed from "source"
to "observer."

Both discoveries came from perceptual verification
revealing a conceptual error that no numeric
diagnostic could catch — because the diagnostics
measure the source signal, and the source signal
was correct.

**The ear found it when the numbers could not.**
This is why perceptual verification is the FINAL
arbiter. The numbers verify the physics. The ear
verifies the experience.

---

## SUMMARY

```
THE OBSERVER POSITION AXIOM:

A voiceless segment must be synthesized at the
OBSERVER position, not the SOURCE position.

The source is the constriction.
The observer is the listener.

Between them:
  The front cavity resonates (formant filter).
  The lips radiate (rolloff).
  The room colors (reverb).

The synthesis chain:
  noise → formant → radiation → amplitude → word → room

Three microphones:
  Mic 1 (constriction): Raw. Harsh. "Inside the mouth."
  Mic 2 (lips):         Filtered. Natural. "Speech."
  Mic 3 (courtyard):    Colored. Warm. "Performance."

Produce Mic 2. Let the room take it to Mic 3.

The instrument plays to the audience,
not to itself.
```

---

## REVISION HISTORY

```
v1.0  February 2026  Initial artifact.
      Discovery context: YAJÑASYA v6.
      Verified for [s] dantya sibilant.
      Theoretical extension to full voiceless class.
```

---

## RELATED DOCUMENTS

```
pluck_artifact.md                 — the Pluck Principle (WHAT)
tonnetz_manifold_seed.md          — coherence space geometry
the_convergence_artifact.md       — three independent derivations
Vedic_Tonnetz_Bridge.md           — Tonnetz ↔ vocal topology bridge
VS_phoneme_inventory.md           — phoneme inventory (update required)
yajnasya_reconstruction.py       — implementation (v6)
rtvijam_reconstruction.py        — unified pluck (v9, reference)
purohitam_reconstruction.py      — unified source (v4, reference)
ratnadhatamam_reconstruction.py  — unified source (v16, reference)
AGENTS.md                         — project-level semantic grounding
Subdomain_AGENTS.md               — subdomain-level grounding
```
