# PHONETIC SELF-REFERENCE
## A Reasoning Artifact on Acoustic Feedback,
## Phonetic Self-Awareness, and the Closed Loop
## February 2026

---

## REVISION HISTORY

  v1 — February 2026
    The Z problem.
    Sibilance measurement loop.
    Basic PHONEME_TARGETS.
    Open loop identified as the root cause.

  v2 — February 2026
    Full rewrite following v17 and
    locus_transitions.md.
    Self-reference extended from
    sibilance checking to:
      — Locus verification
      — Directional consonant identity
      — Tonnetz position recovery
      — Ghost qualia measurement
      — Rhyme convergence detection
      — Multi-layer self-awareness model
    The RARFL loop formalized as
    the architecture of self-correction.

---

## THE CORE INSIGHT (unchanged from v1)

The Z in 'was' disappeared because
the synthesis had no feedback.
It produced Z.
It did not measure what it produced.
It could not know the sibilance was buried.

The fix: synthesize → analyze →
compare to target → adjust → repeat.

That loop is still correct.
This document extends it.

---

## PART I: THE THREE LEVELS OF
## PHONETIC SELF-AWARENESS

Self-reference in this engine has
three distinct levels.
They are not interchangeable.
Each answers a different question.

---

### LEVEL 1: ACOUSTIC IDENTITY

**Question:** Does the output contain
the right acoustic features for this
phoneme?

**Measures:**
  — Sibilance ratio (S, Z, SH, ZH, F, V)
  — Harmonics-to-noise ratio (voiced vs unvoiced)
  — Formant positions (vowels)
  — F3 suppression (R, ER)
  — Antiformant presence (M, N, NG)

**What it catches:**
  Z buried under voicing.
  S too quiet.
  R without F3 suppression.
  M without antiformant notch.

**What it does NOT catch:**
  Whether the consonant is in the
  right Tonnetz position.
  Whether direction (onset/coda) was
  correctly rendered.
  Whether the syllable felt right.

This is Level 1.
It was the only level in v1.
It is necessary but not sufficient.

---

### LEVEL 2: LOCUS IDENTITY

**Question:** Does the consonant sit at
the right Tonnetz position, and does
its F2 trajectory confirm direction
(onset vs coda)?

**Measures:**
  — F2 at consonant onset vs offset
  — Slope direction of F2 through consonant
  — Locus value: where did F2 converge?
  — Comparison to LOCUS_F2_BASE table

**What it catches:**
  Coda N and onset N rendered identically.
  Dark L not dark (F2 locus too high).
  Bright L not bright (F2 locus too low).
  K before front vowel same as K before back.
  Alveolar consonant with bilabial locus
    (place confusion).

**Diagnostic signal:**
  The F2 value at the consonant's
  midpoint is the locus estimate.
  Compare to LOCUS_F2_BASE[place].
  If off by more than 200 Hz: locus error.

  The slope direction of F2 through
  the transition zone confirms direction:
    Rising F2: onset (locus → vowel).
    Falling F2: coda (vowel → locus).

  If direction is wrong, the consonant
  sounds locationless — the ear cannot
  parse where the gesture landed.
  This is the class of error that made
  coda N and onset N sound identical.

**What it does NOT catch:**
  Whether the phrase felt coherent.
  Whether the ghost between syllables
  traced the right Tonnetz path.
  Whether the voice was present.

---

### LEVEL 3: QUALIA COHERENCE

**Question:** Does the phrase trace
a coherent trajectory through
Tonnetz space, and does the ghost
layer carry the right experiential
texture?

**Measures:**
  — Tonnetz position recovered from
    each nucleus vowel (via formant analysis)
  — Ghost duration and amplitude
    between syllables (measured from
    envelope in the boundary region)
  — F0 arc shape across the phrase
    (matches arc_type profile?)
  — Rhyme convergence: do phrase-final
    syllables arrive at compatible
    Tonnetz positions?

**What it catches:**
  Syllable ghost missing or too short.
  Arc type not matching F0 trajectory.
  Two phrases intended to rhyme but
    arriving at different Tonnetz positions.
  Phrase-final exhale absent (no landing).
  Voiced H onset missing before vowel-initial
    words (voice begins too abruptly).

**What it does NOT catch:**
  Whether it sounds like a real voice
  to a human listener.
  This is the remaining human role.

**The principle:**
  The qualia are measurable properties
  of the acoustic output.
  Not subjective impressions.
  The ghost duration is a number.
  The F0 arc shape is a curve.
  The Tonnetz arrival position is a coordinate.
  They can all be measured.
  They can all be compared to targets.

---

## PART II: THE SELF-REFERENCE
## ARCHITECTURE

```
SYNTHESIS (v17+)
  synth_phrase(words, arc_type, ...)
        |
        v
ACOUSTIC OUTPUT
  float32 array, 44100 Hz
        |
        v
LEVEL 1 ANALYSIS
  per-phoneme segment analysis:
  sibilance, HNR, formants
        |
        v
LEVEL 2 ANALYSIS
  per-consonant locus measurement:
  F2 midpoint, slope direction,
  place verification
        |
        v
LEVEL 3 ANALYSIS
  per-phrase Tonnetz trace:
  nucleus recovery, ghost detection,
  arc shape measurement,
  rhyme convergence check
        |
        v
COMPARISON TO TARGETS
  PHONEME_TARGETS (Level 1)
  LOCUS_TARGETS   (Level 2)
  PHRASE_TARGETS  (Level 3)
        |
        v
REPORT
  per-phoneme pass/fail
  per-consonant direction report
  phrase coherence score
  Tonnetz trace visualization
        |
   (if fail)
        v
ADJUSTMENT
  Level 1: adjust gain parameters
  Level 2: adjust locus constants
  Level 3: adjust arc/ghost parameters
        |
        v
RE-SYNTHESIZE
  loop until convergence
```

This is the complete closed loop.
It is not optimization in the
machine learning sense.
It is calibration —
the same operation a sound engineer
performs when tuning a system,
but formalized and automated.

---

## PART III: THE RARFL LOOP AS
## SELF-CORRECTION ARCHITECTURE

The RARFL cycle (Reasoning Axiom–Reward
Feedback Loop) is the engine of
self-reference in OrganismCore.

It maps exactly onto the diagnostic loop:

```
R  (Receive):
  The target specification.
  PHONEME_TARGETS, LOCUS_TARGETS,
  PHRASE_TARGETS. What is intended.

A  (Axiom):
  The synthesis parameters.
  LOCUS_F2_BASE, Z_PARAMS,
  arc_type, ghost profiles.
  The current state of belief
  about how to produce the voice.

R  (Reason/Generate):
  synth_phrase(). The synthesis.
  The parameters applied to
  produce acoustic output.

F  (Feedback):
  The analysis.
  measure_sibilance(), measure_locus_f2(),
  measure_f0_arc(), measure_ghost_duration().
  The measurement of what was actually produced.

L  (Learn/Update):
  Comparison of measured to target.
  If Z sibilance < 0.40: raise noise gain.
  If locus F2 off by 300Hz: adjust LOCUS_F2_BASE.
  If ghost too short: adjust GHOST_PROFILES.
  Parameter update.
  New axiom set.

→ Repeat until convergence.
```

When the loop converges,
the synthesis parameters ARE the axioms
that produce the target acoustic behavior.
Not assumed. Derived from self-measurement.

This is what the v1 artifact called
"the engine gaining its own ears."
The RARFL formalization shows
it is the same structure as
all OrganismCore reasoning loops —
the synthesis engine is just
another reasoning substrate
running the same cycle.

---

## PART IV: THE RELATIVE RELATIONSHIP
## PRINCIPLE (extended from v1)

From v1:

```
"The voice has a relative relation
to the S part."
```

This observation generalizes.

Every phoneme's acoustic identity
is defined relationally —
by its position relative to
other phonemes in the same space.

**Sibilant space:**
  S : Z = unvoiced : voiced
           with same sibilance level.
  S : SH = alveolar : postalveolar
            with same absence of voicing.
  Z : ZH = alveolar : postalveolar
            with same voicing underneath.

  If the engine can hear S clearly,
  the sibilance for Z should be
  at the same level.
  The ONLY difference is the
  voiced buzz underneath.
  Any other difference is an error.

**Nasal space:**
  M : N : NG = bilabial : alveolar : velar
               with same murmur quality.
  The identity is entirely in
  the locus transition — the F2 movement
  into and out of the closure.
  If M and N and NG sound identical,
  the locus transitions are missing.
  (This was the v17 finding.)

**Rhotic space:**
  R : ER = consonant : vowel
           with the same F3 suppression.
  The identity is entirely in F3.
  F3 at 1690 Hz regardless of
  whether R is onset or coda.
  If R sounds like L,
  the F3 suppression is not applied.

**Lateral space:**
  L_onset : L_coda = bright : dark
            = F2 locus 1800 : F2 locus 1000.
  If onset L and coda L sound the same,
  the directional locus model is not working.

**This is the measurement principle:**
  Synthesize two phonemes that should
  differ in exactly one dimension.
  Measure that dimension.
  If the measurement shows they are
  identical in that dimension:
  the dimension is not being rendered.

This is a more powerful diagnostic
than measuring individual phonemes
against absolute targets.
It measures relationships.
Relationships are what define
phonetic identity.

---

## PART V: WHAT CANNOT BE
## SELF-MEASURED

Some properties of the voice
cannot be recovered from
acoustic analysis alone.

**The qualia of presence:**
  Whether the voice sounds alive —
  not just acoustically correct —
  requires a listener with a body.
  No spectral analysis captures this.
  This is irreducibly human.

**The correctness of rhyme perception:**
  Whether two phrases feel like they rhyme
  depends on the listener's musical
  and linguistic context.
  The engine can measure Tonnetz
  convergence. It cannot measure
  whether the convergence felt satisfying.

**The emotional truth of an arc:**
  ARC_GRIEF produces a particular F0
  trajectory and ghost profile.
  Whether it sounds like grief —
  not just like the parameters of grief —
  is a human judgment.
  The engine can verify the parameters
  match the arc specification.
  It cannot verify the experience.

**The summary:**
  Level 1 and Level 2 are fully
  self-measurable.
  Level 3 is partially self-measurable
  (Tonnetz position, ghost duration,
   arc shape).
  The experiential layer of Level 3
  requires human hearing.

This division of labor is correct
and permanent.
The engine's ears handle the
acoustic and structural properties.
The human ear handles the
experiential and musical properties.

Neither replaces the other.

---

## PART VI: THE DIAGNOSTIC PHILOSOPHY

**The diagnostic is not a test suite.**
It is a portrait of the voice.

A test suite asks: did it pass?
A portrait asks: what is it?

The diagnostic should answer:
  What Tonnetz position did each
    vowel actually occupy?
  What locus did each consonant
    actually converge at?
  What direction did each consonant
    actually travel?
  What F0 arc did the phrase actually trace?
  Where did the ghost actually land?
  What Tonnetz path did the phrase
    actually traverse?

The answers to these questions
constitute the voice's self-knowledge.
Not pass/fail.
A map.

If the map matches the intention,
the synthesis is correct.
If the map diverges from the intention,
the divergence points to the parameter
that needs adjustment.

The map is also useful when
the synthesis is correct —
it shows what the voice actually is,
not just whether it passes a gate.

---

## PART VII: FORWARD — WHAT COMES NEXT

**Rhyme space mapping:**
  Given two phrases, measure the
  Tonnetz distance between their
  final stressed nuclei and their
  coda loci.
  Report whether they fall within
  the perceptual fusion threshold.
  This makes rhyme detectable
  without human judgment for the
  structural component.

**Self-adjusting arc profiles:**
  If the measured F0 arc does not
  match ARC_GRIEF's target curve,
  adjust the arc parameters until
  it does.
  The arc can calibrate itself.

**Locus bootstrap:**
  Rather than setting LOCUS_F2_BASE
  by hand from acoustic phonetics tables,
  synthesize each place of articulation
  in isolation (beatboxer-style),
  measure the F2 peak at release,
  and use that as the locus.
  The engine measures its own
  place-of-articulation space.

**The bootstrap is the deepest form
of self-reference:**
  The engine does not need to be
  told where bilabial is.
  It produces a bilabial closure,
  measures what it produced,
  and the measurement IS the definition
  of bilabial for this engine.

  This is the Tonnetz principle
  applied to consonants:
  position defined by relationship,
  derived from self-measurement,
  not imported from a table.

---

*February 2026.*
*v1 found the Z.*
*v2 finds the voice.*
