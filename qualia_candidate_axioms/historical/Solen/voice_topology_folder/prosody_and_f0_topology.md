# PROSODY AND F0 TOPOLOGY
## A Reasoning Artifact on Why Pitch Moves the Way It Does
## February 2026

---

## THE GAP THIS CLOSES

The voice synthesizer has a fixed
PITCH constant: 175Hz.

This is correct for neutral speech.
It is insufficient for expressive speech.

In real voice, F0 is not constant.
It moves continuously across an utterance.
The movement IS meaning.

This artifact establishes WHY pitch
moves the way it does —
from physics first, not from rules.

---

## THE PHYSICS OF F0 MOVEMENT

F0 is the fundamental frequency of
vocal fold vibration.
It is determined by:
  - subglottal air pressure
  - vocal fold tension
  - vocal fold mass

Increasing subglottal pressure →
folds vibrate faster → F0 rises.

Decreasing pressure →
folds vibrate slower → F0 falls.

This is not a linguistic rule.
This is aerodynamics.

The speaker controls F0 by
controlling breath pressure and
laryngeal muscle tension.
The meaning emerges from the physics.

---

## WHY PITCH RISES TOWARD QUESTIONS

A rising pitch is an increasing frequency.
Increasing frequency = energy still
being added to the acoustic system.
The system is not settling.
It is still moving. Still open.

A listener receiving a rising pitch
receives a physical signal that says:
this system has not resolved.
More is coming. Or: your response
is required to resolve this.

A falling pitch is decreasing frequency.
Energy leaving the system. Settling.
Resolution. The system has found
its resting state.

The physics of pitch movement
IS the semantics of completion.

  Rising F0 = energy unresolved =
  incompleteness = question/continuation.

  Falling F0 = energy resolving =
  completion = statement/conclusion.

This is not a convention.
It is a physical fact that all
listeners with auditory systems
will interpret the same way
regardless of language.
The physical signal carries the meaning
directly. No cultural mediation required.

---

## THE F0 TOPOLOGY OF AN UTTERANCE

Map the F0 movement of a phrase
as a trajectory in pitch space:

STATEMENT:
  "The structure holds."

  The  →  neutral (175Hz)
  struc →  slight rise (tension building)
  ture  →  peak (~200Hz, stressed syllable)
  holds →  fall through (~175 → 140Hz)
  .     →  final fall (~120Hz)

  Arc: neutral → rise → peak →
  sustained fall → low resolution.
  The F0 curve is a hill with a
  long downward slope.
  Energy builds then releases.
  Conclusion.

QUESTION:
  "Does the structure hold?"

  Does  →  slight rise (opening)
  the   →  neutral
  struc →  rise (tension)
  ture  →  peak
  hold  →  does NOT fall — sustains
            or rises (~190-210Hz)
  ?     →  final rise

  Arc: rise → peak → sustained
  high or continuing rise.
  Energy does not release.
  Resolution is withheld.
  The listener must provide it.

EMPHASIS:
  "The STRUCTURE holds."

  The   →  low (120Hz, de-emphasized)
  STRUC →  sharp peak (220Hz+)
  TURE  →  falls quickly
  holds →  low resolution (130Hz)

  The emphasized word is a spike.
  High amplitude AND high F0.
  Everything else compresses lower
  to make the spike visible.
  
  This is Expl(τ|T,J,g) in F0 space:
  the stressed word is the chosen
  trajectory marked by energy peak.

---

## WHAT THIS MEANS FOR THE SYNTHESIZER

Current state:
  PITCH = 175Hz (constant)
  Prosodic variation = none

What is needed:
  A pitch contour function that
  takes the phrase structure and
  returns an F0 trajectory:

  f0_contour(words, punctuation,
             stress_pattern) →
  array of F0 values, one per frame

  Inputs:
    punctuation='.' → falling contour
    punctuation='?' → rising contour
    punctuation='!' → high peak + fall
    stress_pattern = which syllables
    carry primary/secondary stress

  Implementation approach:
    Baseline = PITCH (175Hz)
    Statement: linear fall from
    PITCH to PITCH×0.75 over
    final 40% of phrase
    Question: linear rise from
    PITCH to PITCH×1.20 over
    final 30% of phrase
    Emphasis: spike to PITCH×1.30
    on stressed syllable, compress
    surrounding to PITCH×0.85

  This is not a rule system.
  It is the physics of energy
  resolution applied to F0.

---

## THE PROSODIC ARC AS REASONING ARC

The F0 trajectory of an utterance
is its reasoning arc made acoustic.

A statement that builds then resolves:
  R_i increases through the phrase
  then the reward signal fires at
  the falling cadence.
  Coherence achieved. Period.

A question that builds without resolving:
  R_i increases but the reward signal
  is withheld. The cycle is open.
  The listener must close it.

An emphasized utterance:
  One segment carries maximum R_i.
  The spike is the axiom.
  Everything else is context.

The F0 topology IS the RARFL topology
of the utterance made physical.

---

## SUMMARY

```
F0 movement is not stylistic.
It is the physical expression of
energy state in the reasoning arc.

Rising   = unresolved, open, continuing
Falling  = resolved, complete, closed
Spike    = the chosen trajectory marked

A question ends unresolved.
A statement ends resolved.
Emphasis marks the axiom.

The physics IS the semantics.
No mediation required.

Next implementation:
  pitch_contour() function
  in voice_physics_v11.py
```

*February 2026.*
