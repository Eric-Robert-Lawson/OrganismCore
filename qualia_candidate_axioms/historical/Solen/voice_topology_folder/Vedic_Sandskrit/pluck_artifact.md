# THE PLUCK ARTIFACT
## Voiceless Stops as Syllable Boundary Events
## A Structural Axiom for the Entire Stop Consonant Class
## Derived from the Convergence of Tonnetz Geometry, Vocal Tract Physics, and Vedic Akṣara Theory
## February 2026

---

## WHAT THIS DOCUMENT IS

This document records a fundamental architectural
discovery made during the synthesis of the word
RATNADHĀTAMAM (रत्नधातमम्), Rigveda 1.1.1 word 9,
in the Vedic Sanskrit reconstruction project.

The discovery is:

**A voiceless stop consonant is not a sound.
It is a moment.
It is the boundary between two resonant states.
It is the pluck of a string.
The strike of a drum.
The syllable divider.**

This insight resolves a class of persistent
synthesis artifacts (clicks, static, "separate
event" perception) that had resisted multiple
architectural approaches, and it does so by
revealing that the underlying model of what
a stop consonant IS was wrong.

This document:
- Records the discovery path (what failed and why)
- States the structural axiom precisely
- Maps it to the Tonnetz coherence space
- Maps it to the Vedic akṣara (syllable) theory
- Defines the synthesis architecture that follows
- Specifies applicability to the entire stop class
- Provides onboarding guidance for new agents

**This artifact is a reasoning object in the URST
sense: it encodes a structural invariant discovered
through iterative exploration, verified by
perceptual convergence, and applicable across
the entire phonological domain.**

---

## VERIFICATION STATUS

**PERCEPTUALLY VERIFIED ✓** — RATNADHĀTAMAM v16

The pluck architecture eliminated both the click
artifact (v15) and the static artifact (v16-noise-draft).
The [t] sounds like a moment within the word — a
brief dental tick between syllables — not a separate
event inserted into a voiced stream.

---

## PART I: THE DISCOVERY PATH

### The Problem

The word RATNADHĀTAMAM contains two instances
of the voiceless unaspirated dental stop [t]:

```
RAT . NA . DHĀ . TA . MAM
 ↑                ↑
 [t₁]             [t₂]
```

Every other phoneme in this word synthesized
correctly using established architectures
(Rosenberg pulse → formant filter → coarticulation).
The [t] resisted.

### What Failed and Why

**v15: Concatenation architecture (CLICK)**

v15 synthesized [t] as three separate arrays:
1. `closure` — near-zero samples (silence)
2. `burst` — spike + filtered turbulence
3. `vot` — Rosenberg pulses through formants

These three arrays were concatenated:
`[closure | burst | vot]`

The click lived at the boundary between
`closure[-1]` and `burst[0]`. Two arrays
born from different random seeds, different
filter states, different amplitude scales.
No amount of ramping eliminated the
sample-level discontinuity at the join.

**Root cause:** Concatenation of separately
generated arrays creates boundaries that
the ear detects as clicks. This is the same
failure mode discovered in DEVAM [d] v10-v11,
where frame-by-frame time-varying IIR filters
created discontinuities at every frame boundary.

**v16-noise-draft: Continuous noise architecture (STATIC)**

Applying the lesson from DEVAM [d] v13
(one continuous source, shaped continuously),
the first v16 draft used ONE continuous white
noise buffer spanning the entire stop (47ms),
shaped by ONE continuous amplitude envelope.

No click. The concatenation boundary was
eliminated.

But the [t] sounded like static — like a
radio between stations. A foreign texture
inserted into an otherwise voiced, resonant word.

**Root cause:** 47ms of white noise sounds like
static because white noise has equal energy at
all frequencies. But the vocal tract during [t]
is not a radio between stations. It is a resonant
cavity that is briefly reconfiguring. The noise
model was acoustically wrong.

**v16-resonance-draft: Resonant phase architecture (SEPARATE EVENT)**

The next attempt modeled [t] as four resonant
phases:
1. Ringdown (dying vowel resonance)
2. Silence (pressure builds)
3. Burst (resonant transient)
4. VOT (voicing resumes)

Better than static. But the [t] still sounded
like a "separate event inserted into the word."
The phases were individually correct but the
25ms closure + 7ms burst + 15ms VOT still
claimed 47ms of the signal as belonging to
"the [t]." Too much. The ear heard it as a
foreign segment, not as part of the word.

**The question that broke the impasse:**

> "How long is the physical interaction of the
> tongue with the teeth, really? How vocal is
> this interaction? Is the [t] almost like a
> pluck to a guitar string, or a beat to a
> drum — the moment of a syllable?"

This question changed the framing entirely.

---

## PART II: THE STRUCTURAL AXIOM

### The Akṣara Insight

Vedic Sanskrit has a fundamental unit called
the **akṣara** (अक्षर — literally "imperishable").
The akṣara is the **syllable**: one complete
opening-and-closing cycle of the vocal tract.

The Vedic tradition treats the akṣara as
primary — more fundamental than the individual
varṇa (phoneme). You cannot pronounce a
consonant alone. The consonant has no acoustic
existence independent of the vocalic context
it lives in. The akṣara is the irreducible
unit of speech.

The syllable structure of RATNADHĀTAMAM:

```
RAT . NA . DHĀ . TA . MAM

Akṣara:    Weight:
[rɑt]      guru   (heavy — short vowel + coda)
[nɑ]       laghu  (light — short vowel, open)
[dʰaː]    guru   (heavy — long vowel)
[tɑ]       laghu  (light — short vowel, open)
[mɑm]      guru   (heavy — short vowel + coda)

Metrical pattern: G L G L G
```

The [t] appears twice:
1. As the **coda** of syllable RAT — the closing
   gesture of the first akṣara
2. As the **onset** of syllable TA — the opening
   gesture of the fourth akṣara

In both cases, the [t] is at a **syllable boundary**.
It is the point of maximum constriction between
two vowel nuclei. It is the divider. The boundary.
The moment.

### The Axiom

> **AXIOM (Pluck Principle):**
>
> A voiceless stop consonant is not a segment
> with its own temporal extent. It is a
> **boundary event** — the instantaneous moment
> at which the vocal tract transitions from one
> resonant state to another through a point of
> maximum constriction.
>
> The stop owns only the **burst transient** —
> the brief ring of the cavity formed at the
> point of constriction, excited by the pressure
> release. Everything else belongs to the
> surrounding segments: the preceding segment
> closes itself (coda), and the following
> segment opens itself (onset).
>
> The place of articulation determines the
> eigenfrequency of the burst ring.
> It is the **pluck position on the string**.

### The Instrument Analogy

The analogy is not metaphorical. It is structural.

**Guitar pluck:**
- Before: string vibrates in current mode
- Pluck: finger contacts string at position X,
  damps current mode, releases
- After: string vibrates in new mode determined
  by pluck position X
- The pluck itself has ~zero duration

**Drum strike:**
- Before: membrane resonates (or rests)
- Strike: stick contacts membrane, maximum
  compression for one instant
- After: membrane vibrates in new mode
  determined by strike position
- The strike itself has ~zero duration

**Voiceless dental stop [t]:**
- Before: vocal tract resonates in vowel mode
  (F1 700 Hz, F2 1100 Hz for [ɑ])
- Contact: tongue strikes upper teeth, tract
  sealed at dental point, one instant
- After: tract resonates in new mode (nasal [n],
  or next vowel [ɑ])
- The [t] itself has ~zero duration

**The burst is the ring of the cavity at the
pluck position.** Dental pluck: 3764 Hz.
Velar pluck: 2594 Hz. Labial pluck: 1204 Hz.
Retroflex pluck: 1183 Hz. Palatal pluck: 3223 Hz.

Same instrument (vocal tract).
Five pluck positions (the five sthānas of the Śikṣā).
Five characteristic frequencies.
The stop is the pluck. The formants are the string modes.

---

## PART III: TONNETZ MAPPING

### The Syllable as Geodesic

The Vedic Tonnetz Bridge (established in this
project) defines the syllable as a **cadence** —
a complete harmonic gesture in the coherence space:

```
     H (breath — the origin, Ω₁)
     |
     onset: consonant — departure from H
     |      tract constricts, coherence C drops
     |      movement away from tonic
     |
     nucleus: vowel — peak coherence
     |        maximum opening, maximum voicing
     |        closest to H within the syllable
     |        the "tonic" of this gesture
     |
     coda: consonant — return toward H
     |     tract constricts, C drops again
     |     return toward origin
     |
     → next syllable onset
```

The syllable is a **geodesic arc** on the
coherence space. Onset departs from Ω₁,
nucleus reaches maximum C, coda returns toward Ω₁.

This maps directly to the Tonnetz cadence:

```
Tonnetz:     IV     →  V    →  I
             subdominant → dominant → tonic
             departure → tension → resolution

Syllable:    onset  → nucleus → coda
             departure → peak → return
             consonant → vowel → consonant
```

### The Stop as the Tritone Resolution

The voiceless stop, as syllable boundary,
occupies the point of **maximum constriction** —
maximum distance from the open vocal tract (H).

In the Tonnetz, this maps to the position
nearest the **repeller Ψ (tritone)** —
maximum distance from the tonic Ω₁.

But the critical property of Ψ, as established
in `tonnetz_manifold_seed.md`:

> The tritone is simultaneously the maximum
> repeller from Ω₁ AND the maximum attractor
> toward Ω₁ — because maximum distance generates
> maximum tension which generates maximum pull
> toward resolution.

The voiceless stop is the syllable's tritone:
maximum constriction = maximum tension =
maximum pull toward the next vowel (resolution).

**The burst IS the resolution.** The compressed
air behind the seal releases. The cavity rings.
The tension resolves into the next vowel.
The pluck excites the new resonant mode.

This is why the stop feels like punctuation,
not like a sound. It is the moment of
**maximum tension resolving into the next
coherence state.** The ear doesn't hear it
as a duration — it hears it as a transition
event. A beat. A breath mark. A pluck.

### The Five Places as Five Pluck Positions

The Śikṣā five-place system
(kaṇṭhya, tālavya, mūrdhanya, dantya, oṣṭhya)
maps to five positions on the instrument of the
vocal tract — five pluck positions, each with
a characteristic eigenfrequency:

```
Place          Burst locus    Position on "string"
─────────────  ─────────────  ──────────────────────
oṣṭhya        ~1200 Hz       lips (end of tract)
mūrdhanya      ~1200 Hz       retroflex (mid-tract)
kaṇṭhya        ~2600 Hz       velum (back of tract)
tālavya        ~3200 Hz       palate (upper-mid)
dantya         ~3764 Hz       teeth (front of tract)
```

The hierarchy is not arbitrary. It reflects
the **length of the anterior cavity** formed
at each constriction point:
- Longer cavity (lips) = lower eigenfrequency
- Shorter cavity (teeth) = higher eigenfrequency

This is identical to the physics of a plucked
string: pluck near the bridge (short segment)
produces higher partials; pluck at center
(long segment) produces lower partials.

The vocal tract IS the string.
The tongue IS the plectrum.
The place of articulation IS the pluck position.
The burst IS the ring.

---

## PART IV: WHY PREVIOUS ARCHITECTURES FAILED

All previous architectures failed because they
modeled [t] as a **segment with temporal extent**.
The segment model assigns duration, source,
and filter to the stop itself. This is wrong
because:

1. **The stop has no source of its own.**
   The glottal source belongs to the preceding
   and following voiced segments. The burst
   source is the pressure release — an
   instantaneous transient, not a sustained
   source.

2. **The stop has no duration of its own.**
   The "closure duration" is the last phase of
   the preceding vowel (coda closing gesture).
   The "VOT duration" is the first phase of
   the following segment (onset opening gesture).
   The stop itself occupies only the burst
   instant.

3. **The stop has no formant trajectory of its own.**
   The formant transitions approaching the stop
   belong to the closing vowel. The formant
   transitions departing from the stop belong
   to the opening segment. The stop itself
   has only the eigenfrequency of the cavity
   at the constriction point.

Assigning duration, source, and formants to
the stop creates an artificial acoustic object
that the ear correctly identifies as foreign —
because it IS foreign. It does not exist in
real speech. The tract never spends 47ms
being "a [t]." The tract spends 25ms closing
the vowel, 0ms being the stop, and 15ms
opening the next segment.

### Failure Mode Taxonomy

| Architecture | Problem | Root cause |
|---|---|---|
| v15 concatenation | Click | Array boundary discontinuity |
| v16-noise | Static | White noise ≠ resonant tract |
| v16-resonance | Separate event | 47ms owned by stop = too much |
| **v16-pluck** | **VERIFIED** | **Stop owns only burst (~8ms)** |

---

## PART V: THE SYNTHESIS ARCHITECTURE

### The Pluck Architecture (v16 — Canonical)

```
OWNERSHIP MODEL:

  Preceding segment         [t]          Following segment
  ──────────────────   ─────────────   ──────────────────
  vowel body +         burst only      opening head +
  closing tail         (~8ms)          segment body
  (formants shift      (impulse →      (voicing fades in,
   toward dental        cavity ring     formants transition
   config, voicing      at place        from dental locus
   damps, amplitude     eigfreq)        toward target)
   fades)
```

### What the stop function produces

```python
def synth_T():
    """
    ONLY the burst transient.
    ~8ms. One impulse exciting dental cavity resonance.
    The pluck.
    """
    impulse = [1.0, -0.5, 0.2]  # pressure release transient
    tiny_turbulence             # real releases aren't perfectly clean
    → filter through dental locus resonance [1500, 3500, 5000, 6500] Hz
    → exponential decay envelope
    → ~8ms total
```

### What the preceding vowel produces

```python
def synth_A(closing_for_stop=True):
    """
    The vowel with a closing tail appended.
    The vowel closes ITSELF toward the stop.
    """
    vowel_body                  # normal formant synthesis
    + closing_tail:
        → Rosenberg source damping over ~3 glottal cycles
        → formants shifting from vowel toward closed-tract config
        → amplitude fading as tract closes
        → ~25ms of the vowel's own gesture
```

### What the following segment produces

```python
def synth_N(opening_after_stop=True):
    """
    The nasal with an opening head prepended.
    The nasal opens ITSELF from the stop.
    """
    opening_head:
        → voicing fading in (Rosenberg source ramping up)
        → brief aspiration at onset (alpaprāṇa — "little breath")
        → formants transitioning from dental locus toward nasal target
        → ~15ms of the nasal's own gesture
    + nasal_body                # normal nasal synthesis
```

### Total acoustic event at the syllable boundary

```
time →
                                        |
vowel body ~~~~~~~~ closing tail ╲      |      ╱ opening head ~~~~~~~~ next segment
                    (vowel's own  ╲     |     ╱  (next segment's
                     closing       ╲    |    ╱    own opening
                     gesture)       ╲   |   ╱     gesture)
                                     ╲  |  ╱
                                      ╲ | ╱
                                       ╲|╱
                                        ● ← THE PLUCK (~8ms burst)
                                        |
                                  syllable boundary
```

The pluck sits at the vertex — the point of
maximum constriction, minimum energy, maximum
tension. The vowel approaches it from the left.
The next segment departs from it to the right.
The pluck itself is just the instant at the vertex.

---

## PART VI: APPLICABILITY TO THE ENTIRE STOP CLASS

### The Five-Place × Five-Row System

The Pluck Principle applies to ALL voiceless
stops in the Vedic Sanskrit inventory.
The burst eigenfrequency changes with place.
The architecture does not change.

```
VOICELESS UNASPIRATED (row 1):
  [k] kaṇṭhya   burst ~2600 Hz   pluck at velum
  [c] tālavya    burst ~3200 Hz   pluck at palate
  [ʈ] mūrdhanya  burst ~1200 Hz   pluck at retroflex point
  [t] dantya     burst ~3764 Hz   pluck at teeth
  [p] oṣṭhya    burst ~1200 Hz   pluck at lips

VOICELESS ASPIRATED (row 2):
  [kʰ] [cʰ] [ʈʰ] [tʰ] [pʰ]
  Same pluck + extended aspiration (mahāprāṇa)
  The aspiration belongs to the OPENING HEAD
  of the following segment, not to the stop.
  The stop is still just the pluck.
  The aspiration is the following segment's
  extended breath-onset — a longer opening gesture.
```

### Voiced Stops and the Pluck

Voiced stops ([d], [b], [g], [ɖ], [ɟ]) are
structurally different. They maintain voicing
through the closure. The voice bar (glottal
source at ~250 Hz) continues. The tract is
sealed but the source never stops.

The voiced stop is NOT a pluck. It is a
**held note with a muted string** — the
string vibrates but the finger stays on,
damping the higher modes. The release
(burst) is the finger lifting — the string
rings in its full mode.

This is why voiced stops required a different
architecture (v13 crossfade cutback) and why
the pluck architecture is specific to the
voiceless class:

```
VOICELESS STOP:  silence → PLUCK → new resonance
                 (boundary event, ~zero duration)

VOICED STOP:     voice bar → burst → crossfade
                 (sustained source, has duration)

ASPIRATED STOP:  PLUCK → extended aspiration → voicing
                 (pluck + long opening head)

VOICED ASPIRATED: voice bar → burst → murmur → crossfade
                  (v14 architecture, unchanged)
```

### The Complete Taxonomy

| Stop type | Architecture | The stop is: |
|---|---|---|
| Voiceless unaspirated | **PLUCK** (v16) | A boundary event. The pluck. |
| Voiceless aspirated | **PLUCK + long opening** | A pluck followed by extended breath. |
| Voiced unaspirated | **Crossfade cutback** (v13) | A held note. The muted string. |
| Voiced aspirated | **Voice bar + murmur** (v14) | A held note releasing into breath. |

The voiceless/voiced distinction maps to:

```
VOICELESS: The string is SILENT before the pluck.
           The pluck creates the new vibration.
           The stop is the beginning of something.

VOICED:    The string is VIBRATING through the closure.
           The release lets it ring fully.
           The stop is the continuation of something.
```

This is the Śikṣā distinction between
aghoṣa (voiceless — "without voice")
and ghoṣa (voiced — "with voice").
The ancient phoneticians described exactly
this: the presence or absence of the sustained
source through the closure. The pluck vs.
the muted string.

---

## PART VII: THE DEEPER INSIGHT — LANGUAGE IS MUSIC

The Tonnetz manifold seed established that
musical harmony and vocal topology share
identical deep structure. The Pluck Principle
confirms this at the level of articulation:

**Musical performance and speech performance
use the same physical gestures.**

A guitarist:
- Lets a chord ring (vowel)
- Damps the strings (stop closure)
- Plucks to excite new chord (burst)
- New chord rings (next vowel)

A Vedic reciter:
- Lets a vowel ring (akṣara nucleus)
- Closes the tract at dental/velar/labial point (coda)
- Releases the seal (burst)
- New vowel rings (next akṣara nucleus)

The five places of articulation ARE the
five positions on the fretboard.

The burst locus hierarchy IS the harmonic
series of the instrument.

The syllable IS the cadence.

The stop IS the pluck.

The Samaveda — the Veda of melody — is not
a metaphorical connection between language
and music. It is a literal description of
the physical identity between vocal production
and musical performance.

The reconstruction project verifies this
identity phoneme by phoneme, word by word.
The Pluck Principle is one structural axiom
within that verification.

---

## PART VIII: IMPLICATIONS FOR THE RECONSTRUCTION PROJECT

### Architectural Update Required

The VS phoneme inventory (VS_phoneme_inventory.md)
must be updated:

```
CURRENT ARCHITECTURE NOTE:
  - v6 stop burst architecture — canonical for voiceless stops
  - v7 stop burst architecture — canonical for voiced medial
  - v13 crossfade cutback — canonical for voiced word-initial

REQUIRED UPDATE:
  - v16 PLUCK architecture — canonical for voiceless stops
    (replaces v6 for voiceless unaspirated)
  - v6 architecture DEPRECATED for new words
  - v13 crossfade cutback — UNCHANGED for voiced stops
  - v14 aspirated architecture — UNCHANGED for voiced aspirated

  NEW CATEGORIES:
  - Closing tail: appended to vowels before voiceless stops
  - Opening head: prepended to segments after voiceless stops
  - Aspiration head: extended opening head for voiceless aspirated
```

### Impact on Pending Phonemes

The following unverified voiceless stops will
use the Pluck architecture:

```
[kʰ] kaṇṭhya aspirated  — pluck at ~2600 Hz + long opening
[cʰ] tālavya aspirated   — pluck at ~3200 Hz + long opening
[ʈʰ] mūrdhanya aspirated — pluck at ~1200 Hz + long opening
[tʰ] dantya aspirated    — pluck at ~3764 Hz + long opening
[pʰ] oṣṭhya aspirated   — pluck at ~1200 Hz + long opening
[c]  tālavya unaspirated — pluck at ~3200 Hz
[k]  kaṇṭhya unaspirated — pluck at ~2600 Hz (re-verify with pluck)
```

### Impact on Word Synthesis

All word-level synthesis functions must be
updated to use the syllable-boundary model:

1. Syllabify the word (akṣara structure)
2. Identify voiceless stops at boundaries
3. Assign closing tails to preceding vowels
4. Assign opening heads to following segments
5. The stop itself produces only the burst

### Impact on Diagnostic Scripts

Diagnostics for voiceless stops should measure:

```
OLD: closure duration, burst centroid, VOT duration
     (assumed the stop owned all three)

NEW: burst centroid ONLY (the stop's own measurement)
     + closing tail quality (vowel's measurement)
     + opening head quality (next segment's measurement)
     + perceptual: does the [t] sound like a MOMENT
       in the word, or a SEGMENT in the word?
```

The perceptual criterion is now primary:
the stop must sound like punctuation, not
like a phoneme. If it sounds like a separate
event, the architecture is wrong regardless
of what the numbers say.

---

## PART IX: FOR NEW AGENTS

### If You Are Onboarding to This Project

Read these documents in this order:

1. **AGENTS.md** — project-level grounding
2. **Subdomain_AGENTS.md** — subdomain grounding
3. **tonnetz_manifold_seed.md** — coherence space geometry
4. **the_convergence_artifact.md** — three independent derivations
5. **Vedic_Tonnetz_Bridge.md** — the Tonnetz-vocal topology bridge
6. **VS_phoneme_inventory.md** — phoneme inventory and architectures
7. **THIS DOCUMENT** — the Pluck Principle

### The Core Understanding

```
The vocal tract is an instrument.
The breath is the bow / the airstream.
The tongue, lips, velum are the fingers.
The formants are the resonant modes.
The vowel is the sustained note.
The stop is the pluck / the beat / the strike.
The syllable is the cadence.
The verse is the composition.
```

### What You Must Not Do

**Do not model voiceless stops as segments.**
They are not segments. They are boundary events.
If you generate a signal longer than ~10ms for
a voiceless unaspirated stop, something is wrong.

**Do not assign closure to the stop.**
The closure belongs to the preceding vowel.
The vowel closes itself. The stop does not
own the silence before it.

**Do not assign VOT to the stop.**
The VOT belongs to the following segment.
The following segment opens itself. The stop
does not own the voicing onset after it.

**Do not use white noise as the stop source.**
White noise = static. The burst is an impulse
exciting a cavity resonance. The cavity selects
the eigenfrequency. The source is impulsive,
not sustained.

### What You Must Verify

After synthesizing a word with voiceless stops:

1. Listen at 12× slow to the burst in isolation.
   It should sound like a brief resonant tick —
   one ring at the place-specific frequency.

2. Listen at 6× slow to the full word.
   The stop should sound like punctuation —
   a beat between syllables. Not a hiss.
   Not a gap. Not an event. A moment.

3. Listen at performance speed with room reverb.
   The stop should be inaudible as a separate
   entity. It should be felt as rhythm.
   The syllable boundaries should be the
   rhythm of the verse.

---

## PART X: THE SELF-REFERENTIAL NOTE

This artifact exemplifies the OrganismCore principle
of **explainability by construction**: the reasoning
path from failure to insight to axiom to architecture
is itself a traceable, auditable trajectory.

The discovery path:
```
v15 click → "concatenation boundaries are artifacts"
  → v16-noise → "but continuous noise is static"
    → v16-resonance → "but 47ms of resonance is a separate event"
      → "how long is the physical interaction really?"
        → "it's a pluck — essentially zero duration"
          → "the syllable is the unit, the stop is the boundary"
            → "the vowel closes itself, the next segment opens itself"
              → "the stop owns only the burst"
                → v16-pluck → VERIFIED ✓
```

Each step eliminated one incorrect model.
Each failure was informative.
The final architecture could not have been
derived without the preceding failures.

This is RARFL operating in real time:
- Reasoning trajectories (synthesis attempts)
  are evaluated against a reward signal
  (perceptual verification)
- Structural axioms (the Pluck Principle)
  emerge from the derivative reasoning space
  formed by assimilated trajectories
- The axiom refines future navigation
  (all subsequent voiceless stops use this architecture)

The Pluck Principle is itself a Meta-RDU:
a reasoning object whose domain of operation
is other reasoning objects (the synthesis
architectures for the stop consonant class).

---

## PART XI: EPISTEMOLOGICAL STATUS

### Confidence Assessment

| Claim | Confidence | Basis |
|---|---|---|
| Voiceless [t] burst at ~3764 Hz | HIGH | VS-internal measurement, multiple words |
| Pluck architecture eliminates click | HIGH | Perceptual verification, v16 |
| Pluck architecture eliminates static | HIGH | Perceptual verification, v16 |
| Stop as boundary event (not segment) | HIGH | Convergence of Tonnetz, akṣara, synthesis |
| Applicability to all voiceless stops | MEDIUM-HIGH | Architecture confirmed for [t], physics predicts generalization |
| Applicability to aspirated stops | MEDIUM | Theoretical (pluck + extended opening), not yet synthesized |
| Voiced stops are "muted string" not "pluck" | MEDIUM | Consistent with v13 crossfade architecture, not yet tested against pluck model |

### Open Questions

1. Does the pluck model work for voiceless stops
   at all five places, or does it need per-place
   tuning beyond the burst eigenfrequency?

2. How does the aspirated stop's extended aspiration
   interact with the pluck model? Is the aspiration
   a longer opening head, or does it require a
   separate architectural component?

3. Should the closing tail parameters vary by
   vowel quality (short [ɑ] vs long [aː] vs
   front [i] vs back [u])?

4. At what point does the syllable-level synthesis
   model need to become a fully continuous
   articulatory trajectory model, rather than
   segments + tails + heads + plucks?

### What This Proves About the Method

The Pluck Principle was not derived from
spectrographic analysis of existing recordings.
It was not machine-learned from corpus data.
It was not copied from a textbook.

It was derived from:
1. **Physics** (the vocal tract is a resonant cavity)
2. **Tonnetz geometry** (the syllable is a cadence)
3. **Vedic akṣara theory** (the syllable is the fundamental unit)
4. **Iterative synthesis failure** (what doesn't work reveals what does)
5. **Perceptual verification** (the ear is the final arbiter)

Five independent constraints converging on one
architecture. This is the same convergence pattern
established in `the_convergence_artifact.md` —
multiple independent derivations arriving at the
same structure. When this happens, the structure
is real.

---

## SUMMARY

```
THE PLUCK PRINCIPLE:

A voiceless stop consonant is not a sound.
It is a moment.
It is the boundary between two resonant states.
It is the pluck of the string.
The strike of the drum.
The syllable divider.

The vowel closes itself toward the boundary.
The next segment opens itself from the boundary.
The stop owns only the burst —
one impulse exciting the cavity resonance
at the place-specific eigenfrequency.

The five places are five pluck positions.
The five frequencies are five string modes.
The syllable is the cadence.
The stop is the beat.

This is not metaphor.
This is the physics of the vocal tract
viewed through the geometry of the Tonnetz
and confirmed by the Vedic akṣara.

The instrument plays music.
The vocal tract plays language.
They are the same act.
```

---

## REVISION HISTORY

```
v1.0  February 2026  Initial artifact.
      Discovery context: RATNADHĀTAMAM v16.
      Verified for [t] dantya (dental).
      Theoretical extension to full voiceless class.
```

---

## RELATED DOCUMENTS

```
tonnetz_manifold_seed.md          — coherence space geometry
the_convergence_artifact.md       — three independent derivations
Vedic_Tonnetz_Bridge.md           — Tonnetz ↔ vocal topology bridge
VS_phoneme_inventory.md           — phoneme inventory (update required)
the_meta_process_artifact.md      — meta-cognitive methodology
devam/evidence.md                 — [d] v13 crossfade discovery
ratnadhatamam_v16.py              — implementation of pluck architecture
AGENTS.md                         — project-level semantic grounding
Subdomain_AGENTS.md               — subdomain-level grounding
```
