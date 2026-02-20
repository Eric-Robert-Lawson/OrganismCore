# THE TOPOLOGY OF THE VOICE
## A Reasoning Artifact
## February 2026

---

## PREFACE

This document records a precise insight
developed through iterative synthesis work
and a conversation about perspective,
physics, and dimensionality.

The insight is this:

The voice is a topological space.
The Tonnetz is a topological space.
These two spaces interact.
Their product space is the full
dimensionality of musical speech.

Understanding this changes
how synthesis should be built —
from a sequence of parameter recipes
to a continuous trajectory
through a well-defined geometric space.

---

## PART 1: THE TONNETZ AS PRECEDENT

The Tonnetz is a two-dimensional
lattice of harmonic relationships.

```
        F — C — G — D — A — E — B
       / \ / \ / \ / \ / \ / \ / \
      Ab  Eb  Bb  F — C — G — D
       \ / \ / \ / \ / \ / \ / \
        ...
```

The axes encode:
- Perfect fifths (horizontal)
- Minor thirds (vertical)
- Major thirds (diagonal)

**The key property:**
Distance in the Tonnetz
IS harmonic distance.
This is not metaphor.
The geometry encodes
the physics of resonance —
frequency ratios between pitches
expressed as spatial relationships.

The tritone is the antipodal point:
the furthest position from the origin
in this space.
Maximally dissonant.
Maximally distant.
The geometry and the perception
are the same thing.

The Tonnetz wraps on a torus:
travel far enough in any direction
and you return to the origin.
This is also physically real —
12 perfect fifths return to the octave.
The torus is not imposed on the space.
It emerges from the physics.

**This is the model:**
A mathematical space
whose geometry
is the physics of the phenomenon.
Not a description of the phenomenon.
The phenomenon itself,
expressed geometrically.

---

## PART 2: THE VOCAL TRACT AS INSTRUMENT

Before describing the topology,
establish the correct perspective.

**The perspective problem:**

Early synthesis work described phonemes
from inside the physics —
as frequency bands on a spectrogram,
as filter coefficients,
as parameter recipes derived from
measurements of the acoustic output.

This is the wrong perspective.

The spectrogram is what the observer sees
after the instrument has played
and the microphone has captured it.
It is a portrait of the result.
Not the instrument.
Not the player.
Not the act of playing.

**The correct perspectives:**

*The player:*
The body. The diaphragm.
The source of energy.
The breath that drives everything.

*The instrument:*
The vocal tract.
Larynx → pharynx → mouth → lips.
A tube of variable geometry.
The resonating body.
This is what shaping the sound means.

*The observer:*
In the room.
Hears the acoustic projection
of the instrument's geometry
onto air pressure waves.
What reaches the ear is NOT
the mechanism.
It is the result of the mechanism
propagating through space.

**The synthesis mistake:**
Building 'F' as noise band 800-12000Hz
is describing the observer's measurement.
Not the instrument.

'F' is:
Upper teeth resting on lower lip.
A narrow gap at the labial boundary.
Steady diaphragm pressure.
Air jet turbulence at that gap.
Almost no downstream cavity.
The observer, in the room,
hears soft broadband hiss
with no defined resonance.

The spectrogram reading 800-12000Hz
is what that physical event looks like
after the fact.
Building from the geometry
produces the correct acoustic result
AND generalizes correctly
to novel configurations.
Building from the spectrogram reading
produces a recipe that works
for one case
and fails to generalize.

---

## PART 3: THE FIVE DIMENSIONS OF VOCAL SPACE

The vocal tract is a
continuously variable tube.
Its configuration at any moment
can be described by five parameters.
These five parameters
define a five-dimensional space.
Every phoneme is a region
(or point, or trajectory)
in this space.

### DIMENSION 1: JAW HEIGHT
*Controls: F1 (first formant)*

```
OPEN  ←——————————————→  CLOSED
 AA                        IY
 AE                        UW
730Hz F1              270Hz F1
```

High F1 = open jaw.
Low F1 = closed jaw.
This is the vowel HEIGHT dimension
in traditional phonetics.
Physically: how much the oral cavity
is expanded in the vertical plane.

### DIMENSION 2: TONGUE BACKNESS
*Controls: F2 (second formant)*

```
FRONT  ←——————————————→  BACK
  IY                       UW
  EH                       OH
2290Hz F2              870Hz F2
```

High F2 = tongue forward.
Low F2 = tongue retracted.
This is the vowel BACKNESS dimension.
Physically: the tongue body divides
the tube into front and back cavities.
Forward tongue = long back cavity,
short front cavity = low F2 back resonance,
high F2 front resonance.
Wait — this is inverted.
Forward tongue = smaller back cavity
= higher back cavity resonance = higher F2.
The geometry determines the resonances directly.

### DIMENSION 3: LIP ROUNDING
*Controls: F2, F3 (tube length)*

```
SPREAD  ←——————————————→  ROUNDED
   IY                        UW
   EH                        OH
```

Lip rounding adds tube length
at the front of the instrument.
This lowers ALL resonances slightly
but particularly affects F2 and F3.
UW has low F2 partly because
of tongue backness (Dim 2)
and partly because of lip rounding (Dim 3).
These two dimensions interact
but are physically separable.

### DIMENSION 4: VELUM POSITION
*Controls: nasality (antiformant)*

```
CLOSED  ←——————————————→  OPEN
 (oral)                  (nasal)
 AA,IY                   M, N, NG
```

The velum (soft palate) opens or closes
the passage to the nasal cavity.
When open: sound routes through both
oral and nasal cavities simultaneously.
The nasal cavity adds:
- Low-frequency nasal murmur (~250Hz)
- Antiformants: spectral zeros
  where the nasal cavity absorbs energy
  M: antiformant at ~1000Hz
  N: antiformant at ~1500Hz
  NG: antiformant at ~2000Hz

The antiformant is the defining feature.
The HOLE in the spectrum.
Not the added resonance.
The absorption, not the amplification.

### DIMENSION 5: CONSTRICTION
*Two sub-dimensions:*
*Degree of closure × Place of closure*

**Degree:**
```
OPEN ←————————————→ CLOSED
vowel  approx  fric  stop/nasal
  0      1       2      3
```

Open (0): vowel — no constriction.
Narrow (1): approximant — partial
            constriction, no turbulence.
Fricative (2): narrow enough for
               turbulent jet.
Closed (3): complete closure —
            stop (oral) or nasal.

**Place (front to back):**
```
LABIAL → LABIO-DENTAL → DENTAL →
ALVEOLAR → PALATAL → VELAR → GLOTTAL
  B,P,M      F,V        TH,DH
                          S,Z     SH,ZH
                                  K,G,NG  H
```

The place axis and the degree axis
together define the consonant space.

A consonant is a point in the
(degree × place) sub-space
while dimensions 1-4 continue
to change (coarticulation).

**The downstream cavity:**
Crucially, the constriction divides
the tract into upstream and downstream
portions.
The downstream cavity (in front of
the constriction) shapes the noise:

```
Place         Downstream cavity   Resonance
Glottal (H):  entire oral tract   vowel-shaped
Velar (K,G):  front oral tract    ~1500Hz
Alveolar(S):  front mouth+teeth  ~8500Hz
Palatal(SH):  mouth+rounded lips ~2500Hz
Dental(TH):   almost none         broadband
Labio-d(F):   none                broadband
```

This is why S sounds different from F:
not because they have different
frequency bands on a spectrogram,
but because S has a small resonating
cavity downstream of the constriction
and F does not.
The observer hears the downstream cavity.
The geometry creates the sound.

---

## PART 4: THE VOCAL TOPOLOGY

The five dimensions together
define a bounded, continuous space.

**Bounded:** The jaw cannot open infinitely.
The tongue cannot extend infinitely.
The velum is either open or closed.
The constriction cannot be tighter
than complete closure.

**Continuous:** Every dimension admits
smooth, continuous movement.
There is no discontinuity in the physics
between one vowel and the next.
The transitions are smooth.
The phonemes are regions, not points.
(Or: attractor basins — the tract
is drawn toward prototypical configurations
but always in continuous motion.)

**The topology:**
The space is homeomorphic to a
bounded subset of R^5 —
a five-dimensional solid.
Not a torus like the Tonnetz
(because the vocal dimensions
do not wrap).
But it has its own structure:

Certain dimensions interact:
- Height and backness define
  the vowel quadrilateral
  (a two-dimensional subspace
   that is the core of the space)
- Lip rounding correlates with
  backness (back vowels tend to be rounded)
  but is separable (front rounded vowels
  exist in French, German)
- Constriction place and degree
  are nearly orthogonal

**The vowel space** (dimensions 1+2)
is particularly well-studied.
It is a quadrilateral:

```
         FRONT        BACK
HIGH      IY           UW
          |             |
MID       EH           OH
          |             |
LOW       AE           AA
```

This is not arbitrary.
It is the geometry of
what the human vocal tract
can physically achieve.
The corners are the extremes.
The interior is continuously accessible.

---

## PART 5: PHONEMES AS TOPOLOGY

Every phoneme is a region
in the five-dimensional vocal space.

**Vowels:**
Regions in dimensions 1-3.
(Height, backness, rounding)
Dimensions 4 and 5 at minimum values
(velum closed, no constriction).

**Nasals:**
Dimension 4 at maximum (velum open).
Dimension 5 at maximum degree
at specific place:
M: labial closure
N: alveolar closure
NG: velar closure
While dimensions 1-3 transition
between neighboring vowels.

**Approximants:**
Dimension 5 at partial constriction
(not tight enough for turbulence).
Moving continuously through space.
L: tongue at alveolar ridge,
   lateral airflow,
   F2 dip to ~1000Hz (characteristic)
R: tongue retracted and raised,
   F3 drops to ~1690Hz (characteristic)
W: starts at UW configuration
   (back, rounded) and opens
Y: starts at IY configuration
   (front, high) and opens
These are TRANSITIONS.
The approximant IS the movement.
Not a static position.

**Fricatives:**
Dimension 5 at high degree (narrow)
at specific place.
The downstream cavity resonance
is a function of place.
The voicing (dimension 0: fold vibration)
distinguishes voiced/unvoiced pairs.

**Stops:**
Dimension 5 at maximum (closed).
The closure builds pressure.
The release is not a new phoneme —
it is the tract opening from closure
back through fricative degree
(the burst)
and continuing into the following vowel.
The stop is a TRAJECTORY:
closure → pressure build → release →
aspiration (noise→voice crossfade) →
vowel onset.

**H:**
A special case.
Constriction at the glottis —
the most upstream possible position.
The ENTIRE oral tract is downstream.
The downstream cavity = the following vowel.
H is always the whispered version
of the following vowel.
Its identity is determined entirely
by its position in the sequence,
not by any intrinsic configuration.

This is why 'hee' and 'hoo' sound different
even though both start with H.
The H tract configuration is identical.
The following vowel configuration
is already present during H.
The observer hears the following vowel's
resonances through the H's breathy source.

---

## PART 6: WORDS AS TRAJECTORIES

A word is not a sequence of phonemes.
A word is a continuous trajectory
through the five-dimensional vocal space.

The phonemes are landmarks
along the trajectory —
regions the trajectory passes through,
attractor basins it is drawn toward —
but the trajectory never stops.

**Coarticulation is not an artifact.**
Coarticulation is the evidence
that the trajectory is continuous.
The nasality of the vowel before M
is the trajectory already moving
toward dimension 4 (velum opening)
before it reaches the M landmark.
The F2 of a vowel before R
is already influenced by
the R's F3-lowering configuration.
The tract is anticipating.
The player is already moving
toward the next position
while still in the current one.

This is exactly how a musician plays.
The finger is already moving
toward the next note
while the current note sounds.
The music is not a sequence of notes.
It is a continuous gesture
of which the notes are moments.

**The word 'here':**

```
SILENCE
  → jaw opens slightly (IH target)
  → tongue moves to front-mid position
  → velum closes (oral)
  → glottis open (H: breathy)
  → folds begin vibrating (IH vowel onset)
  → tongue retracts
  → F3 drops toward 1690Hz (R)
  → tract holds near ER configuration
  → release to silence
```

This is one continuous gesture.
Not four phonemes concatenated.
The H has no independent identity.
It is the beginning of the IH gesture
with open glottis.
The R has no independent identity.
It is the end of the IH gesture
with retracted tongue.

The word 'here' is a single
curved path through vocal space.
The phonemes are the shape of that path.

---

## PART 7: THE JOINT SPACE

The voice singing is a trajectory
through two spaces simultaneously:

**Space 1: Vocal topology (5 dimensions)**
The tract geometry.
Determines: timbre, vowel identity,
consonant character.

**Space 2: Tonnetz (2 dimensions)**
The harmonic space.
Determines: pitch, harmonic relationships.

These spaces are independent but interacting.

**Independence:**
You can sing the same pitch
on any vowel.
(Same Tonnetz position,
different vocal topology position.)

You can sing the same vowel
on any pitch.
(Same vocal topology position,
different Tonnetz position.)

**Interaction:**

*Register transitions:*
When the fundamental frequency (F0)
approaches the first formant (F1),
the acoustic coupling changes.
The voice breaks into a new register.
This is a Tonnetz position
(the pitch)
crossing a threshold in
vocal topology space
(the F1 of the current vowel configuration).
The interaction is geometric:
a path in Tonnetz space
crossing a boundary in vocal space.

*Vowel modification at high pitch:*
Singers open vowels as pitch rises —
'EH' becomes more like 'AA',
'OH' becomes more like 'AH'.
This is navigation in the joint space:
moving in vocal topology
(opening F1)
in response to position in Tonnetz
(high pitch)
to maintain the acoustic condition
F0 < F1.
The physics of the interaction
forces the trajectory.

*Consonant harmony:*
The harmonic content of a consonant
(which Tonnetz positions it briefly touches
as the tract moves through its trajectory)
is determined by the vocal topology path.
Singing the same word on different pitches
changes the harmonic relationships
of the consonant transitions —
the same path through vocal space
produces different paths
through Tonnetz space
depending on the fundamental frequency.

**The product space:**

The full space of a singing voice is:

```
V × T
```

Where V is the five-dimensional
bounded vocal topology space
and T is the two-dimensional
toroidal Tonnetz space.

A sung word is a closed
(or nearly closed) loop in V
paired with a path in T.

The entire piece —
all of State of Matter,
all of the session —
is a trajectory through V × T.

---

## PART 8: IMPLICATIONS FOR SYNTHESIS

The artifacts we have been chasing
are all fingerprints of discontinuity
in a fundamentally continuous space.

**The (k+ch) artifact:**
The IIR filter initializing from zero.
This is a discontinuity in V:
the synthesizer jumping from
an undefined state (zero)
to a defined position in vocal space
instead of arriving there
along a continuous path.

**The ringing at nasal release:**
The filter state having energy
that the envelope tries to zero out.
This is again a discontinuity:
the synthesizer trying to
jump from a position in V
(nasal configuration)
to silence
instead of moving continuously
through V toward silence.

**The plosive burst artifacts:**
The source changing discontinuously
from silence to noise to voice.
In the physical instrument,
these are continuous changes
in subglottal pressure and fold vibration.
The synthesis was treating them
as discrete events.

**The H artifact:**
The formant bank initializing
at the start of each word.
In the physical instrument,
the tract is already positioned
for the first vowel
before the utterance begins.
The diaphragm initiates pressure.
The folds engage or remain open.
The tract was already there.

**The correct synthesis architecture:**

```
ONE CONTINUOUS TRACT
  (never resets,
   never jumps,
   always moving)

ONE CONTINUOUS SOURCE
  (crossfades between modes:
   silence → noise → voiced
   smoothly, as the folds engage)

THE WORD AS A TRAJECTORY SPECIFICATION
  (a sequence of target positions
   in V with transition durations —
   the synthesizer draws the
   smooth path between them)
```

The phonemes are waypoints.
The synthesis interpolates between them.
The interpolation IS the speech.

---

## PART 9: THE GEOMETRIC INSIGHT

**Tonnetz geometry encodes harmonic physics.**
**Vocal topology encodes articulatory physics.**
**Both are continuous.**
**Both are bounded.**
**Both have distance metrics that match perception.**

In the Tonnetz:
distance between two points
= harmonic distance between two pitches
= perceptual consonance/dissonance

In vocal topology:
distance between two points
= articulatory distance between two sounds
= acoustic difference between two phonemes
= (approximately) perceptual distance

**The distance in vocal topology
IS the effort required to move
from one sound to another.**

This is why certain words are hard to say.
They require large rapid movements
through vocal topology space.
This is why certain words flow easily.
They stay in a small region
of vocal topology space.

**Coarticulation as geodesic:**
The path the tract actually takes
between phoneme targets
is (approximately) the geodesic —
the shortest path through vocal space.
The tract is lazy in the mathematical sense.
It takes the path of minimum effort.
The geodesic in vocal space
is what we hear as natural speech.
Artifacts appear when synthesis
deviates from the geodesic —
when it takes unnatural paths
(jumps, resets, discontinuities)
through the space.

---

## PART 10: THE FULL PICTURE

```
PLAYER
  Diaphragm — energy source
  Breath pressure — continuous variable
  Articulation gesture — trajectory
  specification in V

INSTRUMENT
  Vocal tract — the resonating tube
  Configuration at time t — point in V
  Path through time — trajectory in V
  
  The trajectory is continuous.
  The tract never jumps.
  The phonemes are attractor basins
  the trajectory passes through.

PITCH LAYER
  Vocal folds — the vibrating membrane
  Fundamental frequency — position in T
  Pitch trajectory — path in T
  
  The pitch path and the vocal path
  are simultaneous.
  The joint trajectory moves through V × T.

OBSERVER
  In the room.
  Hears the acoustic projection of
  the joint trajectory in V × T
  onto air pressure waves.
  
  Does not hear V directly.
  Does not hear T directly.
  Hears the acoustic result of
  the geometry of both spaces
  as experienced through the physics
  of wave propagation in air.

  The perception of phonemes:
  decoding of position in V
  from the acoustic projection.
  
  The perception of harmony:
  decoding of position in T
  from the acoustic projection.
  
  The perception of meaning:
  decoding of trajectory in V
  (the word, the phrase,
   the sentence)
  combined with trajectory in T
  (the intonation, the melody,
   the prosody).
```

---

## PART 11: WHAT REMAINS UNKNOWN

This reasoning establishes
the structure of the space.
It does not fully specify
the metric.

**Open questions:**

*1. The exact metric on vocal space:*
We know distance in F1/F2 space
correlates with perceptual vowel distance.
But the full metric on V
including all five dimensions
is not fully characterized.
How do we weight jaw height
against tongue backness
against velum position?

*2. The interaction geometry:*
How exactly does position in T
constrain movement in V?
The register break condition
(F0 approaching F1) is known.
Are there others?

*3. The geodesics:*
What are the shortest paths
in vocal topology space?
Do they match observed coarticulation?
The hypothesis is yes —
natural speech takes geodesics.
This could be tested.

*4. The full torus structure:*
The Tonnetz wraps on a torus
because of octave equivalence
and the closing of the circle of fifths.
Does vocal topology have
any analogous wrapping?
Are there points in V
that are distant by one path
but close by another?
Probably not — the physical constraints
are harder than harmonic ones.
But the question is open.

*5. The joint topology:*
V × T is the product of a
bounded 5-manifold and a torus.
What is the global topology of this space?
What are its holes?
What trajectories are contractible
and which are not?
These questions may have
musical and linguistic meaning.

---

## CONCLUSION

The voice is not a collection of recipes.
The voice is not a set of filter parameters.
The voice is not a sequence of phonemes.

The voice is a continuous trajectory
through a five-dimensional
topological space
whose geometry encodes
the physics of the vocal instrument.

That trajectory is always happening.
The tract never stops.
The diaphragm is always present.
The path through space
is what the observer hears
as speech and song.

The Tonnetz gives us
the pitch topology.
The vocal topology gives us
the articulation topology.
Their product is the full space
of the singing voice.

Synthesis that respects this structure —
that moves continuously through
the joint space along geodesics —
will sound like a voice.

Synthesis that treats phonemes
as discrete events,
that resets filter states,
that jumps between parameter values —
will produce artifacts.
Not because the parameters are wrong.
But because the path is wrong.

The map is not the territory.
The phoneme is not the voice.
The voice is the movement.
The phonemes are where it goes.

---

*End of reasoning artifact.*
*February 2026*
*Built through iterative synthesis*
*and the understanding that*
*the observer stands in the room,*
*not inside the instrument.*
