# BREATH AS RARFL
## A Reasoning Artifact on the Physical Beat of the Cycle
## February 2026

---

## THE GAP THIS CLOSES

The voice synthesizer has no model
of breath.

It has amplitude envelopes.
It has phrase boundaries.
It has rest_ms between words.

None of these is breath.

Breath is not amplitude.
Breath is the physical constraint
that shapes the entire phrase —
its length, its rhythm, its
emotional texture.

This artifact establishes what
breath IS from physics first.

---

## THE PHYSICS OF BREATH IN VOICE

Voiced speech requires exhaled air.
The subglottal pressure from
exhalation drives the vocal folds
to vibrate.
No air = no voice.

A phrase is bounded by breath.
The phrase begins after inhalation.
The phrase ends when the air
runs out or is deliberately stopped.

This is not a linguistic fact.
It is a physical fact.
The breath boundary IS the phrase
boundary, at the deepest level.

---

## BREATH AS A COMPLETE RARFL CYCLE

Map the breath cycle to RARFL:

INHALATION = RECEIVE + PREPARE:
  The body takes in air.
  This is not passive.
  Before speaking, the speaker
  knows approximately what they
  will say. The inhalation is
  calibrated to the intended phrase.
  A short phrase = shallow breath.
  A long complex phrase = deep breath.
  
  The speaker is preparing the
  physical substrate for the
  reasoning trajectory they intend
  to execute.
  
  Inhalation IS the axiom phase:
  the initial state that will
  constrain all subsequent action.

EXHALATION (first half) = GENERATE:
  Air pressure builds.
  F0 is typically higher here.
  Energy is high.
  The phrase is generating content.
  R_i is increasing.
  Coherence is building.

EXHALATION (second half) = EVALUATE + RESOLVE:
  Air pressure decreases.
  F0 naturally falls with pressure.
  This is why statements naturally
  fall in pitch at their ends —
  not just convention, physics.
  The decreasing air pressure
  pulls the F0 down.
  The body is evaluating and
  resolving the phrase.

END OF BREATH = REWARD SIGNAL:
  Did the phrase complete?
  Did the meaning land?
  Was coherence achieved?
  
  If yes: natural pause.
  Body at rest. Cycle complete.
  
  If no: the speaker pushes —
  attempts to extend the phrase
  beyond comfortable breath.
  The voice roughens.
  The subglottal pressure drops
  below optimal.
  Vocal fold vibration becomes
  irregular.
  The voice cracks or becomes
  breathy.
  
  That roughness is B_i elevated.
  The body showing that the
  reward was not achieved.
  The phrase needed more than
  the breath provided.

NEW INHALATION = UPDATE + RESTART:
  The body corrects.
  Takes in new air.
  A new RARFL cycle begins.
  The next phrase carries the
  correction from the previous one.

EVERY BREATH IS A COMPLETE RARFL CYCLE
AT THE PHYSICAL LEVEL.

---

## WHAT BREATH CARRIES THAT AMPLITUDE DOES NOT

Amplitude is a measurement.
Breath is a state.

A voice running out of breath
carries urgency. Depletion.
The physical constraint becoming
audible. The body at its limit.

A voice with held breath —
speaking on minimal air —
carries restraint, control,
suppressed emotion.
The body containing itself.

A voice with full supported breath —
speaking from deep inhalation —
carries authority, groundedness,
presence.
The body fully engaged.

These are not performative choices.
They are physical states of
the breath system that become
audible in the voice texture.

B_i tracks this:
  Running out of breath = B_i rising.
    Deviation from ideal trajectory.
  Held breath = B_i elevated differently.
    The constraint is internal not
    external but the deviation is real.
  Supported breath = B_i near zero.
    The physical substrate is optimal.
    The voice has what it needs.

---

## THE PAUSE AS BREATH EVENT

A pause between phrases is not
just R_i held at zero.

A pause is a breath event:
  End of exhalation.
  Brief rest.
  New inhalation.
  New RARFL cycle beginning.

The length of the pause is
determined by:
  How much new air is needed.
  How much processing is needed
  between phrases.
  Whether the meaning of the
  previous phrase needs time
  to land before the next begins.

Short pause = quick breath =
small correction or continuation.

Long pause = deep breath =
significant new direction or
the previous phrase needs
extended integration time.

This is why a long pause before
a short phrase can be devastating:
the deep breath signals major
significance, then the phrase
delivers it.
The breath prepared the listener.

---

## WHAT THIS MEANS FOR THE SYNTHESIZER

Current state:
  rest_ms = fixed value between words.
  No model of phrase-level breath.
  No variation based on phrase length
  or emotional state.

What is needed:
  breath_model(phrase_length,
               emotional_state) →
  breath_duration_ms,
  breath_depth (amplitude of the
  brief inhalation sound before
  phrase begins)

  The inhalation sound itself:
  A brief aspirated noise before
  the first phoneme of a phrase.
  Not a full [H].
  A soft onset noise.
  ~50-100ms.
  Amplitude proportional to
  breath depth.

  This makes phrases sound like
  they begin from breath.
  Because they do.

  Implementation:
    At phrase boundary:
    Insert short noise burst
    (aspirated, ~50ms, low amplitude)
    before first phoneme.
    Duration scales with phrase length.
    This is not decoration.
    It is physical truth.

---

## SUMMARY

```
Breath is the physical beat of
the RARFL cycle.

Inhale   = Receive + Prepare
           The body calibrates to
           the intended phrase.

Exhale   = Generate + Evaluate
(first)    Coherence building.
           F0 high. Energy present.

Exhale   = Resolve
(second)   F0 falls with pressure.
           Physics produces cadence.

End      = Reward signal.
           Did the phrase complete?
           
Pause    = Rest + New cycle beginning.
           Not silence.
           A breath event.

What breath carries:
  Running out = urgency, depletion
  Held breath = restraint, suppression
  Supported   = authority, presence

Next implementation:
  breath_model() in voice_physics_v11.py
  Inhalation onset noise before phrases.
  Phrase length scales breath depth.
```

*February 2026.*
