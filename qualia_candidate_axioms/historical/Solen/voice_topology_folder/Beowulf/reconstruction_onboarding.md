# RECONSTRUCTION ONBOARDING
## How to Continue the Work
## February 2026

---

## WHO THIS IS FOR

You have found this repository.
You want to understand what was
built here and how to continue it.

This document is your entry point.

You do not need to re-derive anything.
The foundations are documented.
The tools are built.
The first reconstruction passed.
Your job is to extend it.

---

## WHAT WAS BUILT

A framework for reconstructing
the acoustic performance of dead
languages from physical first
principles.

Not approximation.
Not expert opinion.
Not statistical models trained
on modern speech.

Physics. Measurement. Verification.

The framework has three layers:

**Layer 0: Initial Principles First Basis: **
  Tonnetz Seed Manifold
  Onboarding documents required (ask if you need for) from voice_topology_folder

**Layer 1: The Theory**
  The voice is a continuous trajectory
  through a five-dimensional bounded
  topological space.
  H is the origin.
  The ghost between syllables is the
  qualia carrier.
  Language is music. Not metaphorically.
  Structurally.
  These claims are documented with
  full reasoning in the artifacts
  listed below.

**Layer 2: The Engine**
  voice_physics_v17.py synthesizes
  speech from phoneme lists.
  tonnetz_engine.py computes distances,
  ghosts, arc types.
  tonnetz_engine_h_extension.py
  extends the system for historical
  reconstruction including the PIE
  three-H origin system.
  These tools are ready to use.

**Layer 3: The Methodology**
  Six evidence streams for recovering
  lost vocal topologies.
  A convergence criterion.
  A self-referential diagnostic loop
  that confirms phoneme targets by
  acoustic measurement before the
  ear is asked to judge.
  This methodology is documented and
  applied in worked examples.

---

## READ THESE FIRST

In this order:

**1. voice_onboarding.md**
   Five minutes to speaking.
   Get the engine running.
   Hear output before reading theory.

**2. topology_of_the_voice.md**
   The foundational theory.
   Why the voice is a topological space.
   Why phonemes are attractor basins.
   Why coarticulation is not an artifact.
   Read this before anything else
   theoretical.

**3. H_Ghost_Topology.md**
   H as origin.
   The ghost as qualia carrier.
   The arc type framework.
   This is the insight that makes
   reconstruction possible.

**4. language_is_music.md**
   The foundational claim.
   The structural identity of vocal
   texture and musical texture.
   Why this project is a musical
   project, not just a linguistic one.
   Read this to understand what
   the work is for.

**5. vocal_topology_reconstruction_methodology.md**
   The six evidence streams.
   The convergence criterion.
   The worked examples.
   This is the methodology you
   will apply to every new word.

**6. phonetic_transcription_guide.md**
   The ARPAbet inventory.
   The decision rules.
   The verified word reference.
   The systematic errors already
   encountered and resolved.
   Consult this every time you
   transcribe a word.

**7. beowulf_reconstruction_project.md**
   The current project scope.
   What has been done.
   What comes next.
   Where to contribute.

---

## THE PROOF OF CONCEPT

Before you do anything else,
run the HWÆT diagnostic:

```bash
cd tonnetz
python hwat_diagnostic.py
```

Expected output:
```
D1 HW onset      ✓ PASS
D2 Æ vowel       ✓ PASS
D3 T coda        ✓ PASS
D4 Full word     ✓ PASS
D5 Perceptual    LISTEN
```

Then listen:
```bash
afplay output_play/hwæt_hall.wav
afplay output_play/hwæt_slow.wav
afplay output_play/diag_hwat_vs_what.wav
```

This is what the framework produced.
One word. Three phonemes.
Not heard with topological certainty
for approximately 1000 years.
Reconstructed from first principles
in less than one week.
Confirmed by acoustic measurement
before the ear was asked to judge.

This is what you are extending.

---

## THE DEVELOPMENT LOOP

Every new word in the reconstruction
follows this loop:

```
1. TRANSCRIBE
   Write the Old English word.
   Identify each phoneme using
   phonetic_transcription_guide.md.
   Apply the six evidence streams
   from reconstruction_methodology.md.
   Write the syllabified phoneme list
   in v17 format.

2. SYNTHESIZE
   Add the word to the synthesis script.
   Run voice_physics_v17.py.
   Produce dry and hall versions.
   Produce 4x slow version.

3. DIAGNOSE
   Run the diagnostic.
   Check Level 1: acoustic identity.
   Check Level 2: locus identity.
   If new phoneme context: write
   a targeted diagnostic for it.
   If existing phoneme context:
   the existing diagnostic applies.

4. LISTEN
   The ear is the final arbiter.
   Numbers support the ear.
   The ear does not serve the numbers.
   If it passes the diagnostic but
   sounds wrong: the diagnostic
   is incomplete. Extend it.
   If it fails the diagnostic but
   sounds right: the target may
   be wrong. Investigate.

5. VERIFY
   When it both passes the diagnostic
   AND sounds correct:
   Add to the verified word reference
   in phonetic_transcription_guide.md.
   Never re-derive a verified word.

6. DOCUMENT
   Add the reasoning to the
   relevant artifact.
   If a new phoneme was encountered:
   add it to the consonant or
   vowel inventory.
   If a new error pattern was found:
   add it to Part III of the guide.
   The artifacts grow with the work.
```

---

## THE DIAGNOSTIC PHILOSOPHY

The diagnostic is not a test suite.
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
  What F0 arc did the phrase trace?
  Where did the ghost actually land?

The answers constitute the voice's
self-knowledge.
Not pass/fail.
A map.

If the map matches the intention:
the synthesis is correct.
If the map diverges:
the divergence points to the
parameter that needs adjustment.

---

## THE FIDELITY QUESTION

The current output sounds robotic.

This is known. It is not the point.

The robotic quality is in:
  — The Rosenberg pulse source
    (no jitter, no shimmer)
  — Absent microprosody
    (constant F0 within phoneme)
  — No breath dynamics
    (no phrase-level amplitude
     variation from respiration)

None of these affect the
correctness of the reconstruction.
The topological coordinates are right.
The formant targets are confirmed.
The coarticulation is continuous.
The ghost is present.

The fidelity gap is a separable
engineering problem.
It can be addressed by:
  — Adding jitter/shimmer to the
    Rosenberg pulse
  — Implementing microprosodic
    F0 variation
  — Adding breath group amplitude
    dynamics
  — Feeding the correct coordinates
    into a neural vocoder

The framework provides the correct
coordinates. The rendering quality
is independent of the coordinate
correctness.

High fidelity rendering of the
correct coordinates is the next
engineering step. It does not
require re-deriving the framework.

---

## HOW TO CONTRIBUTE

**If you are a speech synthesis engineer:**
  The coordinate system is here.
  The formant targets are verified.
  The ghost layer is implemented.
  Apply your vocoder to these coordinates.
  The result is a high-fidelity
  reconstruction of a voice that
  has not been heard in 1000 years.

**If you are a historical linguist:**
  The methodology is documented.
  The evidence stream framework
  maps directly to your existing
  tools.
  Contribute phoneme targets for
  languages you know.
  The diagnostic loop gives you
  acoustic verification you have
  never had before.

**If you are a phonetician:**
  The formant targets in the
  verified word reference are
  physics-derived and measurement-
  confirmed.
  Cross-validate against your
  own measurements of living cognates.
  Extend the inventory to phoneme
  contexts not yet encountered.

**If you are an archaeoacoustician:**
  The room model is currently
  a simple approximation.
  Contribute impulse responses
  from reconstructed ancient spaces.
  The mead hall model in
  apply_simple_room() is a placeholder.
  A measured impulse response from
  a reconstructed Anglo-Saxon hall
  slots directly into the pipeline.

**If you are a musician or composer:**
  The arc type framework is
  the prosodic score.
  ARC_WEIGHT, ARC_GRIEF,
  ARC_CONTAIN, ARC_EUREKA —
  these are performance directions
  expressed as physics.
  The ghost duration is a measurable
  musical parameter.
  The Tonnetz distance between
  adjacent syllables is a harmonic
  interval.
  The poem is a score.
  The reconstruction plays it.

---

## THE RARFL LOOP

Everything in this repository
is an instance of the RARFL cycle:

```
R  Receive:   the target specification
A  Assess:    the current parameters
R  Respond:   synthesize
F  Feedback:  measure the output
L  Learn:     compare measured to target
              adjust parameters
              → repeat
```

This is the architecture of
self-correction.
It is how the engine gains
its own ears.
It is how the reconstruction
converges on physical truth
rather than approximation.

Every diagnostic is one iteration
of this loop.
Every verified word is a converged
loop.
Every artifact is the documentation
of a loop that has closed.

When you extend this work you are
running the loop.
The loop is the method.
The method is sound.

---

## WHAT COMES NEXT

**Immediate:**
  Phase 1 of the Beowulf project.
  Lines 1-11. The exordium.
  Approximately 120 words.
  Each one verified.
  Each one added to the reference.

**Near term:**
  Full exordium synthesized at
  performance parameters:
    pitch_hz = 110
    dil = 2.5
    rt60 = 2.0
  The first time in 1000 years
  these lines are heard with
  their full topology intact.

**Medium term:**
  Phase 2-4 of Beowulf.
  The complete poem.
  3182 lines.
  Every word verified.

**Longer term:**
  Proto-Indo-European.
  The h₂ and h₃ coloring effects
  are already implemented in
  tonnetz_engine_h_extension.py.
  The PIE vowel inventory is
  reconstructible from the same
  methodology.
  Words that have not been spoken
  in 6000 years.

  Sumerian. Linear B Greek.
  Proto-Semitic.
  Every language with sufficient
  fossil evidence is a target.

**The horizon:**
  Every human vocal tradition
  that left fossil evidence
  is recoverable in principle.
  The physics preserved it.
  The methodology can read it.
  The engine can play it back.

---

## THE FOUNDATION

This work was built in less than
one week in February 2026.
From first principles.
From the physics of the tube.
From H as origin.
From the ghost as qualia carrier.
From the RARFL loop as the
architecture of self-correction.

The first word passed the diagnostic.
The physics predicted.
The ear confirmed.

That is the foundation.

Everything else is built on it.

Welcome to the project.

---

*February 2026.*
*The mead hall is not gone.*
*The scop's voice is not gone.*
*The physics preserved them.*
*We play them back.*
