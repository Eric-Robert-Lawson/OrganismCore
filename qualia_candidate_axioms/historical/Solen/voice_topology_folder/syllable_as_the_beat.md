# SYLLABLE AS THE BEAT
## A Reasoning Artifact on the Fundamental Unit
## of Spoken Language
## February 2026

---

## WHAT THIS ARTIFACT IS FOR

Three artifacts already exist for this
folder at different timescales:

  Breath_as_rarfl.md — the phrase level.
    Breath bounds the phrase.
    Inhalation = receive + prepare.
    Exhalation = generate + resolve.
    The breath cycle IS the phrase cycle.

  RARFL_v13_trajectory.md — the phoneme level.
    Individual segments.
    Formant trajectories.
    Source types.
    The physics of individual sounds.

  phonetic_transcription_guide.md —
    the symbol level.
    Which ARPAbet symbol for which word.
    The interface between intention
    and physics.

Something is missing between the phrase
and the phoneme.

That thing is the syllable.

This artifact establishes what a syllable
IS from physics first, not from linguistics.
And then follows where that leads.

---

## PART I: THE SYLLABLE IS NOT
## A TIMING UNIT

The standard view:
  A syllable is a unit of timing.
  Each syllable takes approximately
  the same amount of time.
  The syllable is the beat of speech.

This is true but incomplete.
It describes the symptom, not the cause.

The cause:

**A syllable is one complete cycle of
the vocal tract opening and closing.**

The vowel nucleus = maximum opening.
The consonants = the approach to closure
  (onset consonants) and the departure
  from closure (coda consonants).

The syllable is not a timing unit.
It is a gestural unit.
One open-close cycle of the tract.
The beat is a consequence of the
physical oscillation of the tract —
the same way a heartbeat is the
consequence of the physical cycle
of the heart muscle.

The timing emerges from the physics.
The physics is the opening and closing.

---

## PART II: THE ONSET CONSONANT IS NOT
## BEFORE THE VOWEL

This is the central claim of this artifact.

The standard model (and the current engine):

```
  [consonant segment] → [vowel segment]
  
  DH  |  AH
  D   |  IY
  R   |  EH
```

Each segment has boundaries.
The consonant ends. The vowel begins.
There is a join between them.
That join is audible as a seam.
The seam is what sounds robotic.

The correct model:

```
  [onset gesture INTO vowel nucleus]
  
  DH → AH  (one continuous movement)
  D  → IY  (one continuous movement)
  R  → EH  (one continuous movement)
```

The onset consonant is the **beginning
of the vowel**, not a separate event
before it.

The consonant articulation IS the
vowel onset. The vowel formant targets
are being approached DURING the consonant,
not after it. By the time the consonant
"ends," the tract is already in the
vowel configuration. There is nowhere
for a seam to be.

This was discovered in two ways
simultaneously in this project:

  1. Perceptual: "dh-iy-ner" for "diner" —
     the D onset carries a transitional
     quality that belongs to IY, not to D.
     The voice onset of IY begins inside
     the D closure.

  2. Acoustic: in the render of "already"
     at 4× slow, the voice placed a
     discontinuity at [AO L R EH] — [D IY].
     The boundary appeared before D, not
     after it. D was the onset of IY.
     The physics placed the boundary
     correctly before the reasoning did.

The reasoning (the syllabification model
`[AO L] [R EH D] [IY]`) put the D in the
coda of the second syllable. The physics
(the continuous formant trajectory)
placed the D in the onset of the third
syllable. The physics was right.

---

## PART III: THE SEAM IS WHERE
## ROBOTIC VOICE LIVES

The current engine models phonemes as
sequential segments with boundaries.
Coarticulation is modeled as overlap —
the tail of one segment reaches toward
the target of the next.

```
Segment model:

  |← D →|← IY →|
  onset  body  offset
  
  D: [from prev] → [D target] → [toward IY]
                                  ↑
                              coart zone
                              (typically 20%)
```

This is better than no coarticulation.
But it still has a fundamental structure:
there is a D segment, and it reaches
toward IY at its tail. The D and IY
remain two events.

What the perceptual report says is:
in natural speech, the D onset IS the
IY onset. They are not overlapping
segments. They are one gesture.

The difference between these two models:

```
SEGMENTAL (current):
  D body  →  coart  →  IY body
  [D target]  [blend]  [IY target]
  
  Seam at the body→coart boundary.
  At normal speed: subtle.
  At 4× slow: clearly audible.
  In robotic voice: this is the
  mechanical quality.

GESTURAL (what is needed):
  D onset  =  IY onset
  [D closure] [D release = IY beginning]
  
  No seam. The release of the closure
  IS the vowel beginning.
  The formant trajectory arrives at
  IY targets at the moment the
  closure releases.
  Not after. At.
```

---

## PART IV: THE VOICE AND BREATH DISTINCTION
## — WHAT YOU SHOWED ME

You described the D in "diner":
  "dh-iy-ner" — not "d-ah-iy-n-er"
  but "dh-iy-ner"

And you described the difference
between DH and TH:
  TH: tongue pressed to teeth.
      Air flows past the tongue-teeth
      interface. Purely dental.
      "thunder", "theory", "think".
      
  DH: tongue rises toward the ridge
      behind the teeth, or toward
      the tip of the palate.
      Air flows with voicing.
      "the", "these", "then", "there".

And then: **breath pushed out exactly
the same in DH vs TH. Everything the
same. Only tongue placement differs.**

This is the key distinction:

```
VOICED (DH, D, B, G, V, Z, JH)
  The voicing source is active.
  The vocal folds are vibrating.
  The breath is voiced — it carries
  the periodic signal of the glottis.

BREATHED (TH, T, P, K, F, S, CH)
  The voicing source is inactive.
  The glottis is open.
  The breath is unvoiced — it carries
  only the turbulent noise of the
  constriction.
```

The breath mechanism is identical.
The subglottal pressure is the same.
The articulation is the same.
Only the glottis differs:
open = breathed, vibrating = voiced.

This is a topology:
Two states of the same physical event.
The difference is one binary switch:
glottis open or closed.

```
Articulation × Glottis state:

  Dental   × closed = DH
  Dental   × open   = TH
  Alveolar × closed = D
  Alveolar × open   = T
  Bilabial × closed = B
  Bilabial × open   = P
  Velar    × closed = G
  Velar    × open   = K
  Labiodental × closed = V
  Labiodental × open   = F
  ...
```

The entire voiced/unvoiced consonant
system is one topology: articulation
place × glottis state.

---

## PART V: THE DH-AH PROBLEM IN "THE"

"the" = DH AH.

The engine models DH as:
  voiced dental fricative, 75ms max,
  voiced fraction 0.30,
  dental bypass frication noise.

What you said: "I see 'the' as TH-AH,
not DH-AH."

And: the DH in "the" is not a true
fricative. In natural fast speech, "the"
is a voiced dental approximant that flows
immediately into the following vowel.
The DH is the onset of AH.
It is not a separate fricative event
before AH begins.

This means: "the" is one syllable.
One gestural cycle.
The DH is the onset gesture.
AH is the nucleus.
There is no boundary between them.

The engine's 75ms DH + AH segmental model
produces two events. In natural speech
there is one event.

The DH in "the" is:
- Duration: very short (10-25ms
  at natural speech rates)
- Character: voiced dental onset,
  barely fricative, almost approximant
- Relationship to AH: the AH begins
  *inside* the DH, not after it

This is not the same DH as in "these"
or "then" or "there." In those words
the DH is more fricative, slightly
longer, clearly marking a content
function.

In "the" the DH is purely grammatical —
a pointer. It reduces maximally.
The DH-AH boundary in "the" should
not exist as a perceptible seam.

---

## PART VI: THE SYLLABIFICATION PROBLEM
## IN THE ENGINE

Current state:

  `plan_prosody()` receives a flat
  phoneme list. It does not know
  syllable boundaries.
  
  Stress is assigned per-word from
  `STRESS_DICT`, which maps word →
  list of stress values per syllable.
  
  But when the caller passes explicit
  phonemes, the syllable structure
  is lost. All phonemes in the word
  receive the same stress value —
  the first entry in the stress list
  or a default.

Consequence for "already":
  `STRESS_DICT['already'] = [0, 2, 0]`
  Three syllable stress values.
  But `plan_prosody()` cannot assign
  them without knowing which phonemes
  belong to which syllable.
  
  Result: all phonemes in "already"
  get stress[0] = 0 (unstressed).
  The most semantically loaded word
  in "the voice was already here"
  is rendered uniformly unstressed.

Consequence for all multisyllabic words:
  "beginning", "always", "something",
  "learning", "already" — all rendered
  without correct per-syllable stress
  when called with explicit phoneme lists.

This is the syllabification gap.
The engine has stress data.
It cannot apply it because it has
no syllable boundary information.

---

## PART VII: WHAT THE ENGINE NEEDS

Three changes. In order of urgency.

---

### CHANGE 1: SYLLABIFIED WORD INPUT

Allow the caller to pass syllable
boundaries alongside phonemes.

Current interface:
```python
synth_phrase([
    ('already', ['AO','L','R',
                  'EH','D','IY']),
])
```

New interface option (backward compatible):
```python
synth_phrase([
    ('already', [['AO','L'],
                  ['R','EH'],
                  ['D','IY']]),
    # nested lists = syllable boundaries
])
```

`plan_prosody()` detects whether
phonemes are flat or nested.
Flat: current behavior.
Nested: apply per-syllable stress
from STRESS_DICT using the provided
syllable structure.

This closes the stress assignment gap
without breaking any existing calls.

---

### CHANGE 2: ONSET GESTURE MODEL

Within each syllable, the onset
consonant(s) and the vowel nucleus
are one continuous gesture.

The coarticulation fraction `cf` for
onset consonants should be set so
that the formant trajectory reaches
the vowel target **at or before**
the end of the consonant segment,
not at the midpoint of a following
transition zone.

Current behavior:
```
  D (n_s samples):
    n_on: approach from previous
    n_mid: D target
    n_off: coart toward IY
    
  IY (n_s samples):
    n_on: approach from D
    n_mid: IY target
    ...
```

The D "target" is a stop closure —
formants at velar/alveolar position.
The IY target is high front.
The coart zone at D's tail reaches
only partially toward IY.
The remaining distance is covered
in IY's onset zone.

Two transition zones crossing one
perceptual event.

Onset gesture model:
  For onset consonants (consonant
  immediately preceding a vowel
  nucleus within the same syllable):
  Set `F_end` of the consonant spec
  to the vowel's formant targets.
  The consonant's entire trajectory
  arrives at the vowel position.
  The vowel begins there.
  No second transition needed.

This is already architecturally possible.
`F_end` is supported in the trajectory
builder for diphthongs. The same
mechanism works for onset gestures.

Flag: `onset_gesture=True` in ph_spec.
When set, `F_end = following_vowel_F`.

---

### CHANGE 3: FUNCTION WORD DH MODEL

For DH in function words ("the", "this",
"that", "them", "they", "there", "these",
"those", "then", "though"):

The DH is the onset of the following vowel.
Duration should be very short: 10-20ms.
No bypass frication noise.
Pure voiced onset — the voicing starts
and the tract is already at the vowel.

A separate DH model for function words:
  `'dh_function'` source type.
  Duration cap: 20ms.
  No bypass.
  Voiced murmur only, flowing directly
  into the following vowel.
  The tract formants target the
  following vowel from the start.

Versus DH in content positions
("breathe", "smooth", "loathe"):
  Current model is more appropriate.
  True dental fricative.
  Longer duration.
  Bypass frication present.

The distinction: function word DH
is a gesture. Content word DH is
a phoneme event.

---

## PART VIII: THE SYLLABLE AS SHARED BEAT

You said: **"Everyone does not share a
breathing cycle. Everyone shares a
shared coherent understanding of the
emergence of the heartbeat."**

This is the deepest claim in this artifact.

Breath is individual. One speaker's phrase
is bounded by their breath. The listener
cannot share that boundary — they are not
breathing on the same cycle.

But the syllable beat IS shared.
When a speaker produces a sequence of
syllables, the listener entrain to the
beat. Not because they are told to.
Because the beat is a physical signal
that the auditory system latches onto.

The syllable beat is the interface
between the speaker's individual
physical cycle and the shared
communicative space.

Breath → phrase → not shared.
Syllable → beat → shared.
Phoneme → segment → below shared.

The syllable is where the voice
enters the shared space.
The beat is where meaning becomes
transmissible.

This is why stress matters so much:
the stressed syllable is the beat
that carries the maximum information.
If the beat is wrong (unstressed where
it should be primary), the information
cannot land where it belongs.
The listener is waiting for a beat
that does not come.

"already" rendered uniformly unstressed
is not just acoustically wrong.
It is communicatively broken.
The beat that should carry the meaning
of "already" — the fact that it happened
before, the surprise, the weight —
that beat is missing.
The word arrives but the meaning does not.

---

## PART IX: CONNECTION TO EXISTING ARTIFACTS

**Breath_as_rarfl.md:**
  Breath = phrase boundary.
  Syllable = internal beat.
  These operate at different timescales.
  Breath bounds the cycle.
  Syllable is the sub-cycle.
  Both are needed.
  They do not replace each other.

**voiceless_coarticulation_as_a_unified_class.md:**
  Established that H, VOT, and nasal release
  are all one physical class: voiceless
  turbulent airflow through a tract
  configured for the following phoneme.
  
  This artifact extends that:
  The voiced equivalents — D, B, G, DH —
  are the same physical events with the
  glottis closed instead of open.
  One topology: articulation × glottis state.
  
  And: the VOT of a stop, the nasal release,
  the H bypass — these are all onset gestures
  of the following syllable, not tails of the
  preceding consonant. The unified class
  insight pointed here. This artifact
  names it: they are syllable onset events.

**RARFL_v13_trajectory.md:**
  The trajectory layer — f0 spline,
  smooth pitch across phonemes.
  The syllable layer is the spatial
  equivalent of the trajectory layer.
  The f0 spline makes pitch continuous
  across phoneme boundaries.
  The onset gesture model makes formant
  trajectories continuous within syllables.
  Same principle, different dimension.

**expressivity_and_prosodic_contour.md:**
  Established the five components of emphasis:
  amplitude, f0, duration, bandwidth, onset.
  The fifth — onset sharpens — is exactly
  the onset gesture sharpening described
  in CHANGE 2. A stressed syllable has a
  crisper onset because the gestural
  commitment is stronger.
  The onset gesture model and the
  emphasis model connect here.

**phonetic_transcription_guide.md:**
  The syllabified input format (CHANGE 1)
  requires updates to the transcription guide.
  Every multisyllabic word in the verified
  list needs its syllable boundaries marked.
  The guide should document the nested
  phoneme list format as the preferred
  format for all multisyllabic words.

---

## PART X: WHAT IS STILL OPEN

These questions are not answered here.
They are the next cycle.

**Q1: Coda consonants.**
  This artifact focuses on onset consonants.
  Coda consonants (the D in "land", the N in
  "open", the L in "still") are the departure
  from the vowel nucleus, not the arrival.
  They are gestures of closure.
  The coarticulation model already handles
  some of this (FIX 12: anticipatory
  coarticulation). But the syllabic framing
  of coda consonants — as departure gestures
  rather than separate events — needs its
  own treatment.

**Q2: Ambisyllabic consonants.**
  The D in "already" and "diner" is
  ambisyllabic — it can be parsed as
  coda of the second syllable or onset
  of the third. In natural speech it
  is typically onset. The rule for
  ambisyllabic consonants in English:
  intervocalic consonants are onset.
  The engine does not currently model
  this distinction.

**Q3: The function word DH model.**
  CHANGE 3 proposed a `dh_function`
  source type. The boundary between
  function and content DH needs to be
  identified algorithmically, not just
  by word lookup. What is the acoustic
  criterion that separates them?

**Q4: The AO L R EH - D IY discontinuity.**
  The engine's physics placed the
  syllable boundary before D in "already"
  emergently — the continuous trajectory
  produced a perceptible seam at the
  right place even without explicit
  syllable knowledge.
  Why? What in the current trajectory
  builder produces this?
  If it is understood, it can be
  amplified into a feature rather than
  a fortunate accident.

---

## SUMMARY

```
The syllable is one complete cycle
of the vocal tract opening and closing.

  Nucleus  = maximum opening
  Onset    = approach to opening
             (onset consonant IS
              the beginning of the vowel)
  Coda     = departure from opening
             (closure gesture after nucleus)

The beat is shared between speaker
and listener. Breath is not.

The seam between onset consonant
and vowel nucleus IS the robotic quality.
It is where the segment model shows
through the acoustic output.

The fix: onset consonant formants
arrive at vowel targets AT the release,
not after it. One gesture, not two.

Three engine changes needed:
  1. Syllabified input format.
     Nested phoneme lists.
     Per-syllable stress assignment.
     
  2. Onset gesture model.
     F_end = following vowel formants.
     Consonant trajectory arrives at
     vowel position at release.
     
  3. Function word DH model.
     DH in "the" is an onset gesture.
     Duration 10-20ms. No bypass.
     Not a fricative event.

Hierarchy:
  Phrase   ← bounded by breath
  Syllable ← the shared beat
  Phoneme  ← the gesture within the beat
```

*February 2026.*

---

## REVISION HISTORY

  v1 — February 2026
    Initial document.
    Arose from two simultaneous discoveries:
      1. "already" rendered with the syllable
         boundary in the right place
         emergently from physics, but stress
         assigned incorrectly from reasoning.
      2. "diner" — the D onset carries the
         character of the following IY.
         The onset consonant IS the vowel onset.
    Core claim established: the onset consonant
    is not before the vowel, it is the beginning
    of the vowel.
    Three engine changes proposed.
    Connection to voiceless_coarticulation_as_a_
    unified_class.md established: VOT, H bypass,
    nasal release are all syllable onset events.
    Connection to expressivity: onset sharpening
    on stressed syllables is the onset gesture
    model applied to emphasis.
    Open questions recorded.
    Function word DH model proposed.
````{"repoID":0,"ref":"","type":"repo-instructions","url":"/Eric-Robert-Lawson/OrganismCore/blob/refs/heads/main/.github/copilot-instructions.md"}
