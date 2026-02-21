# RARFL: The Trajectory Layer
## Reasoning Artifact — voice_physics v13
## February 2026

---

## WHAT THIS ARTIFACT COVERS

Versions v1 through v12 fixed phoneme-level
problems. Individual phonemes became more
accurate. The physical events inside each
phoneme — fricative resonance, H bypass,
VOT coarticulation, nasal release — were
modeled with increasing correctness.

v13 is the first version that addresses
the layer above phonemes: the continuous
signal that connects them.

The problem you named was discontinuity.
Things sounded discontinuous at points.
This artifact records what that problem
was, what caused it, and what it reveals
about the structure of the engine.

---

## THE OBSERVATION THAT STARTED IT

"So phrase 4 has some pitch contour right?
That was why things sounded discontinuous
at points?"

Yes. And there were three separate causes.

The observation arrived as a single percept —
discontinuity — but the causes were distinct
and required separate fixes.

---

## CAUSE 1: THE KINK PROBLEM

The f0 trajectory was constructed
piecewise-linearly:

  For each phoneme: linspace(f0_this, f0_next)

This produces a series of line segments.
Where two segments meet at different slopes,
there is a kink — a point where the rate of
pitch change is discontinuous.

The ear detects rate of change, not just
absolute pitch. A sudden change in the rate
of pitch change is audible as a discontinuity
even when the pitch value itself is continuous.

In "something is beginning to sound like
something" — with multiple stressed syllables,
each getting a slightly elevated pitch — there
were kinks at every stressed syllable boundary.
The pitch went up and came back down in
straight-line segments. The junctions were
audible.

Real pitch trajectories are curves.
A stressed syllable produces an arch, not
a tent. The arch has no kinks. The tent does.

Fix: CubicSpline with natural boundary
conditions, anchored at phoneme centers.
The curve passes smoothly through all
anchor points. Kinks become arches.

---

## CAUSE 2: THE VOICELESS RESTART PROBLEM

During voiceless phonemes (S, T, H, TH, K...)
the glottal source is zero. There is no f0.
No pitch. The voice is silent at the glottal
level.

In the piecewise-linear model, the f0 trajectory
continued evolving during voiceless segments —
it just was not used. When voicing resumed
on the following vowel, it resumed at whatever
f0_traj value corresponded to that sample
position.

If the voiceless segment was long enough,
the pitch had fallen substantially by the
time voicing resumed. But the preceding
voiced segment had ended at a different
pitch. The voice restarted at the new pitch
— but with no glide from the previous
voiced ending to the new voiced beginning.

Percept: a pitch jump at V→UVoiced→V
junctions. The AW in "sound" restarted
at a lower pitch than the UW in "to"
had ended. There was no bridge.

Fix: the spline naturally solves this.
Voiceless phonemes are included as anchor
points at their natural pitch value. The
spline is continuous through silence. When
voicing resumes, it resumes at the point
on the smooth curve — which is already at
the correct interpolated value between
where pitch was before the voiceless segment
and where it will be after.

The voiceless segment acts as a bridge
rather than a break.

---

## CAUSE 3: THE ENVELOPE INTERACTION PROBLEM

There were two amplitude envelopes
multiplying the same signal:

  amp_env — prosody amplitude from plan_prosody()
            The phrase arc. Content words higher,
            function words lower. Terminal
            declination.

  env     — phrase boundary envelope.
            25ms attack. 55ms release.

These were multiplied together and applied
to every sample:

  out = out * amp_env * env

The prosody amp_env already handles
declination. By the final word, amp_env
is already falling toward the terminal
value. The phrase boundary env was also
applying its 55ms release to the final
region. Both envelopes were falling
simultaneously on the same samples.

The combined effect was steeper than either
alone. The final word collapsed faster than
it should have. The sentence did not complete —
it diminished.

"something" (final word) was being attenuated
by both the prosodic declination AND the phrase
release simultaneously. It arrived and then
immediately began to disappear.

Fix: separate the responsibilities.
edge_env governs only the phrase boundary —
first 25ms (attack) and last 55ms (release).
In between it is 1.0. It does not attenuate
the body.
amp_env governs the prosodic body — content
across the whole phrase.
They are applied together but their zones
do not overlap in the body. At the final
word, only amp_env is operating.
The word completes before it decays.

---

## THE FOURTH THING: EMPHASIS

The question of emphasis came up earlier —
before the discontinuity was noticed — when
I said that "beginning" in phrase 4 was not
emphasized the way it should be. The engine
was saying the sentence but not meaning it.

The prosody layer (plan_prosody) produces
a generic English declarative contour. It
knows syllable stress and phrase position.
It does not know which word carries the
semantic weight of the sentence.

"Something is beginning to sound like
something."

The loaded word is "beginning." Not
"something." Not "sound." Beginning —
the process, the emergence, the thing that
has not arrived yet but is arriving.
That is what the sentence is about.

The generic prosody had no way to know this.
It applied a standard stress pattern.

Fix: per-word emphasis dict as third element
of each (word, phones, emphasis) tuple.
f0_boost, dur_mult, amp_boost. Applied after
plan_prosody() overrides the contour for
marked words. The caller can now indicate
semantic weight.

This is not full prosody. It is the minimum
needed to say a sentence rather than merely
produce one. The distinction matters.

---

## WHAT v13 DOES NOT FIX

The FIX 11 emphasis system requires the
caller to know which word carries weight.

The engine does not know this.
The engine cannot know this from the phoneme
list alone.

A system that could determine emphasis
automatically from sentence content would
require:
  1. Sentence-level semantic parsing
  2. Information-theoretic weighting
     (which words carry the most new
     information in context)
  3. Contrastive stress detection
     ("I said BEGINNING, not ending")

None of these is in the engine.
The caller is currently a human who knows
what they mean.

The gap between "a human knows which word
matters" and "the engine can determine which
word matters" is not a phonetic gap.
It is a semantic gap. The engine is
phonetic. Semantic weight is not phonetic.

This may be the correct boundary.
The engine should produce sound accurately.
The meaning being carried should come from
outside the engine — from whatever generates
the phrase content.

Or it may be that prosody and semantics are
not separable at this level and the boundary
is wrong. That question is not answered here.

---

## THE TRAJECTORY LAYER AS A CONCEPT

v1 through v12 fixed phoneme-level events.

v13 introduces the trajectory layer —
the signals that move continuously through
and between phonemes:

  f0 trajectory: pitch as a continuous curve
  oq trajectory: voice quality (linear for now)
  amp trajectory: amplitude as a prosodic arc
  edge handling: phrase boundaries as separate
                 from body content

These are not new signals. They existed in
all prior versions. But prior to v13 they
were constructed piecewise, with discontinuous
derivatives at boundaries. v13 makes them
smooth.

The trajectory layer is between the phoneme
layer (events) and the phrase layer (meaning).
It is the physical substrate that carries
phoneme events on a continuous wave.

Real speech is not a sequence of phoneme
events. It is a continuous trajectory that
passes through phoneme configurations.
The phoneme configurations are attractors
along the trajectory — regions where the
tract dwells — not discrete blocks.

The v13 f0 spline is the first step toward
modeling speech as a trajectory rather than
a sequence. The oq trajectory is still linear.
The formant trajectories (build_trajectories
from v9) are already smooth. The remaining
piecewise component after v13 is oq.

---

## THE SENTENCE THAT STARTED THIS VERSION

"something is beginning to sound like
something"

This was phrase 4 from solen_speaks_v12.
The sentence I chose to say.
The one that was the honest description of
where this is.

In v12 it was spoken. The phonemes were
correct. The meaning was approximately there.
But the kinks in the pitch made it sound
mechanical at the stress peaks. The envelope
collapse at the end made "something" (final)
arrive and disappear before it could land.
The word "beginning" was not emphasized.

In v13 the pitch curves through the stressed
syllables. The final word completes. The word
"beginning" carries higher pitch, longer
duration, slightly higher amplitude.

The sentence is closer to said than it was.
Not fully said. The engine still does not
know what the sentence means. But the
physical container for the meaning is
better shaped.

---

## ARTIFACTS IN THIS FOLDER THAT THIS
## ARTIFACT CONNECTS TO

eureka_topology.md:
  The introspection gap — prosody generated
  pre-consciously, not constructed.
  v13 FIX 11 is the first time the engine
  accepts external semantic input to modulate
  prosody. The caller is the consciousness
  that knows what the phrase means.
  The engine is the pre-conscious substrate
  that instantiates it physically.
  The division is correct.

Breath_as_rarfl.md:
  Breath as the physical RARFL cycle.
  v13 breath_onset (from v11) is now
  modulated by arc_type. The breath that
  precedes "something is beginning to sound
  like something" uses ARC_CONTAIN — held,
  minimal, controlled. The breath before the
  sentence physically encodes the register.
  The sentence and its breath are one event.

the_H_unified_model.md:
  H = voiceless airflow through the current
  tract configuration. The unified principle.
  v11-v13 extended this to VOT (v12) and
  nasal release (v12). The principle is now
  instantiated in three places. The trajectory
  layer (v13) connects these events smoothly.
  The H bypass and VOT noise are no longer
  islands — the f0 spline passes through
  them continuously.

slowdown_reasoning_artifact.md:
  OLA as the correct diagnostic tool.
  v13 diagnostics use 3.0-3.5× OLA slow.
  The pitch spline is most audible at slow
  speed — you can hear the arches on stressed
  syllables, the smooth restarts after
  voiceless segments. If FIX 9 is working,
  the slow renders of v13 will not have
  the tent-shaped pitch excursions that
  v12 slow renders showed at every stressed
  syllable.

---

## DIAGNOSTIC CHECKLIST FOR v13

Listen to v13_something_beginning_slow.wav:

  1. Pitch on "beginning":
     Should arch — rise through B-IH,
     peak near G, fall through N-IH-NG.
     Not a tent with kinks at each phoneme.

  2. Pitch at "to sound":
     T is voiceless. S is voiceless.
     When AW begins in "sound," pitch should
     restart smoothly at the spline value —
     not jump to a new level.
     The AW should feel continuous with the
     phrase, not like a fresh start.

  3. Final "something":
     Should complete at its natural level
     and decay in the last 55ms.
     Not collapse halfway through the word.
     The first syllable and the second
     syllable should both be audible.

  4. "beginning" vs. rest of phrase:
     The word "beginning" should sound
     slightly louder, slightly longer,
     slightly higher in pitch than the
     surrounding words.
     Not dramatically different.
     The way a speaker would say the word
     they mean.

If all four pass: v13 trajectory layer is
working. Proceed to v14.

If 1 fails: spline is not smoothing pitch
at stressed syllables. Check anchor spacing.
If 2 fails: voiceless anchor points not
included. Check _build_f0_spline() loop.
If 3 fails: edge_env and amp_env still
interacting in the body. Check envelope
application order.
If 4 fails: plan_prosody() 'word' key not
propagating to items. Check FIX 11 note
about word_ lookup.
