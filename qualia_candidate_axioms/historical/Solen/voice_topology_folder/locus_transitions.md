# LOCUS TRANSITIONS
## A Reasoning Artifact on Consonant Direction,
## Place Identity, and the Physics of Rhyme
## February 2026

---

## WHAT THIS ARTIFACT IS FOR

The previous artifacts established:

  syllable_as_the_beat.md:
    The syllable is one complete cycle.
    The onset consonant is the beginning
    of the vowel, not a separate event.
    The seam between onset and nucleus
    is where robotic voice lives.

  h_ghost_topology.md:
    H is the Tonnetz origin.
    Every consonant is a path FROM H
    through a constriction TOWARD a vowel,
    or FROM a vowel through a constriction
    BACK TOWARD H.
    H → onset → nucleus → coda → H.

This artifact identifies the next gap:

  The consonant has no direction
  in the current engine.

  Coda N and onset N sound identical.
  Coda T and onset T sound identical.
  The engine knows the place of
  articulation but not which way
  the tract is facing.

  The perceptual identity of a consonant
  lives in the TRANSITION —
  the 10–20ms of formant movement
  on either side of the closure.
  Not in the closure itself.
  During closure: silence or murmur.
  During transition: the consonant.

This artifact establishes the locus
— the formant target toward which
the tract moves during a consonant
gesture — and shows that direction
(onset vs coda) is not optional
information. It is the primary
carrier of consonant identity.

---

## PART I: WHAT THE LOCUS IS

The locus is the frequency toward which
the second formant (F2) converges during
a consonant closure.

It is a physical fact about the place
of articulation:

  When the tract constricts at the
  bilabial place (lips close for B, P, M):
    F2 is pulled toward ~720 Hz.
    Lips dampen the front cavity.
    The back cavity resonates at low F2.

  When the tract constricts at the
  alveolar place (tongue tip to ridge,
  for D, T, N, L, S, Z):
    F2 is pulled toward ~1800 Hz.
    The front cavity resonates at
    mid-high F2.
    This is the characteristic "brightness"
    of alveolar consonants.

  When the tract constricts at the
  velar place (back tongue to velum,
  for G, K, NG):
    F2 is pulled toward ~3000 Hz,
    or varies with the following vowel.
    Velar transitions are the most
    context-sensitive.

The locus is not a value the consonant
holds during closure. It is the target
the formant transitions are moving
toward — or away from.

During closure, the formant itself
cannot be measured (the tract is occluded).
What is audible is the transition:
  - The formant movement approaching
    the closure from the preceding vowel
  - The formant movement departing
    the closure toward the following vowel

The consonant identity is in these
transition shapes, not in the closure.

---

## PART II: DIRECTION IS PRIMARY

A consonant gesture is not symmetric.

**Onset consonant:**
  H (baseline) → constriction at locus
               → vowel target
  F2 begins near the locus.
  F2 moves TOWARD the following vowel.
  The listener hears: arrival.
  The tract is opening, departing H,
  heading toward the vowel.
  Direction: H → locus → vowel.

**Coda consonant:**
  Vowel target → constriction at locus
               → H (baseline)
  F2 begins at the vowel's F2.
  F2 moves TOWARD the locus.
  The listener hears: departure.
  The tract is closing, departing the
  vowel, heading toward H.
  Direction: vowel → locus → H.

Same place of articulation.
Same ARPAbet symbol.
Different F2 trajectory direction.
Different percept.

---

### THE N IN "EVENING"

"evening" = [['IY','V'], ['N','IH','N'],
              ['IH','NG']]

Syllable 2 contains N in the coda.
Syllable 3 begins with N as onset.

The coda N:
  IH F2 (~2050 Hz) moves toward
  alveolar locus (~1800 Hz).
  Direction: IH → N locus → H.
  Heard as: the vowel closing into
  the ridge. Departure.

The onset N of syllable 3:
  H → alveolar locus (~1800 Hz)
  moves toward IH F2 (~2050 Hz).
  Direction: H → N locus → IH.
  Heard as: the ridge releasing into
  the vowel. Arrival.

In the current engine:
  Both N's receive the same antiformant
  treatment and the same nasal murmur.
  Neither has a directed F2 transition.
  They sound identical.
  They should not.

---

### THE BEATBOXER'S DEMONSTRATION

A beatboxer performing a snare drum
has no surrounding vowels to help.
The consonant gesture is isolated.
There is no vowel F2 target to
transition toward.

Yet the snare is immediately recognizable
as alveolar, or dental, or velar —
depending on where the tongue goes.

How? The aspiration burst after the
closure is filtered through the tract
position at release. The locus is
the filter. The burst, passing through
the locus-shaped cavity, colors the
sound with place identity.

The beatboxer demonstrates:

  The locus transition carries
  consonant identity alone,
  without vowel context.

  In speech, the vowel surrounds the
  consonant and provides additional
  cues. The locus is still primary —
  the vowel context is redundant
  confirmation.

  When the redundant confirmation is
  removed (beatboxing), the locus
  alone is sufficient.

  Conversely: when the locus transition
  is wrong in the engine, no amount
  of correct vowel formants will fix
  the consonant identity. The place
  information is lost.

This is the class of the current gap.
Not individual phonemes.
The entire locus transition layer
is absent from the physics.

---

## PART III: THE LOCUS TABLE

Place of articulation → F2 locus frequency.

These are acoustic targets — where F2
is drawn during the consonant gesture.
Not where F2 sits during closure
(the closure is silent or nasal murmur).
Where F2 is heading or departing from.

```
PLACE          PHONEMES              F2 LOCUS
─────────────────────────────────────────────
Bilabial       M, B, P, W            ~720 Hz
Labiodental    F, V                  ~1100 Hz
Dental         TH, DH                ~1600 Hz
Alveolar       T, D, N, L, S, Z      ~1800 Hz
Postalveolar   SH, ZH, CH, JH        ~2100 Hz
Palatal        Y                     ~2300 Hz
Velar          K, G, NG              ~2400–3000 Hz
               (context-dependent:
                higher before front vowels,
                lower before back vowels)
Glottal        H, HH, R              ~500 Hz
               (R: F3 suppression is
                the defining feature,
                F2 locus ~500–800 Hz)
```

F1 locus:
  All consonants pull F1 toward
  a low value during closure.
  Typical F1 locus: ~250–350 Hz.
  Less place-specific than F2.
  Already partially captured by
  NASAL_CLOSURE_F1 in v14.

F3 locus:
  R and ER: F3 suppressed below 2000 Hz.
  This is the primary identity of
  the rhotic gesture.
  All other consonants: F3 locus
  follows place roughly, but F3
  transitions are perceptually weaker
  than F2.

---

## PART IV: THE TRANSITION SHAPES

A consonant transition is a trajectory
from one Tonnetz position to another,
passing through the constriction.

The shape of the trajectory encodes:
  1. Place identity (which locus)
  2. Direction (onset or coda)
  3. Manner (stop, fricative, nasal,
     approximant)
  4. Voicing (voiced or unvoiced)

**Stop onset (D before IH):**
  F2: 1800 Hz (alveolar locus at release)
       → 2050 Hz (IH target)
  Duration of transition: ~10–25ms
  Shape: rapid, nearly linear rise
  At release: burst + aspiration (T)
  or murmur + onset (D)

**Stop coda (D after IH):**
  F2: 2050 Hz (IH target)
       → 1800 Hz (alveolar locus at closure)
  Duration: ~10–20ms
  Shape: rapid fall
  At closure: silence (T) or murmur (D)
  At release: often unreleased word-finally
  (the release may not occur at all —
  the listener infers the stop from
  the F2 movement alone)

**Nasal onset (N before IH):**
  F2: 1800 Hz (alveolar locus)
       → 2050 Hz (IH target)
  Plus: nasal murmur begins fading out
  as vowel voicing begins
  The nasal color and the F2 rise
  occur simultaneously

**Nasal coda (N after IH):**
  F2: 2050 Hz (IH)
       → 1800 Hz (alveolar locus)
  Plus: nasal murmur builds as
  vowel amplitude decreases
  FIX 12C (nasal anticipation) already
  handles the murmur addition.
  What is missing: the directed F2 fall.

**Approximant onset (L before IH):**
  F2: ~1000 Hz (lateral locus — lower
      than alveolar due to lateral
      air flow lowering F2)
      → 2050 Hz (IH target)
  Duration: ~30–50ms (slower than stops)
  Shape: smooth, sigmoid-like rise

**Approximant coda (L after IH):**
  F2: 2050 Hz (IH)
       → ~1000 Hz (lateral locus)
  The "dark L" — post-vocalic L has
  a distinctively low F2 that is
  audibly different from onset L.
  The current engine's L_BLEND_PER_FORMANT
  in v14 partially captures this.
  The directed locus model makes it explicit.

---

## PART V: VELAR PINCH

Velars (K, G, NG) are the most
context-sensitive consonants in
English.

Before front vowels (IY, IH, EH, AE):
  Back tongue rises to front-of-velum.
  F2 locus: ~3000 Hz.
  F2 and F3 converge — the "velar pinch."
  Both formants move toward each other
  in the transition region.

Before back vowels (UW, UH, OH, AO, AA):
  Back tongue rises to back-of-velum.
  F2 locus: ~2400 Hz.
  F2 and F3 do not converge as sharply.

This is why "key" and "car" sound
different at the consonant:
  "key"  = K + IY: front velar, F2 locus ~3000
  "car"  = K + AA: back velar, F2 locus ~2400

The current engine has the same K
formant targets regardless of following
vowel. This is the velar gap.
The fix is to compute K/G/NG locus
based on the following vowel's Tonnetz
position — which is already measurable
using vocal_distance().

  K before IY (far front): locus ~3000
  K before AH (near H):    locus ~2600
  K before AA (far back):  locus ~2400

  Locus = 2400 + 600 × (a_next / 3.0)

  Where a_next is the fifth-axis
  position of the following vowel.
  IY has a=3 → 2400 + 600 = 3000. ✓
  AH has a=0 → 2400 + 0   = 2400. ✓
  UW has a=-3→ 2400 - 600 = 1800. ✓
  (UW before K is unusual but the
   formula produces a plausible value.)

---

## PART VI: THE RHYME DISCOVERY

This is the deepest consequence of
locus transition physics.

**Rhyme is not vowel identity.**

Rhyme is Tonnetz trajectory convergence.

Two phrases rhyme when their stressed
nuclei arrive at the same (or near)
Tonnetz position via the same (or near)
trajectory shape.

The locus of the coda consonant is
part of the rhyme. Not just the vowel.

"cat" and "bad" rhyme (near rhyme).
  "cat": AE T — F2 falls from ~1800
    toward alveolar locus ~1800,
    then stop closure
  "bad": AE D — F2 falls from ~1800
    toward alveolar locus ~1800,
    then voiced closure
  Same vowel Tonnetz position: (1,1)
  Same coda locus: alveolar ~1800
  → Strong rhyme. Arrival at same
    Tonnetz-locus combination.

"cat" and "cap" do not rhyme as well.
  "cat": AE T — coda locus ~1800
  "cap": AE P — coda locus ~720
  Same vowel Tonnetz position: (1,1)
  Different coda locus.
  → Weaker rhyme. Vowels match.
    Locus diverges.

"cat" and "back" do not rhyme at all.
  "cat": AE T — vowel (1,1), locus ~1800
  "back": AE K — vowel (1,1), locus ~3000
  Same vowel. Very different coda locus.
  → Weakest. The departure trajectory
    is completely different.
    The ear hears different destinations.

This confirms: the rhyme is the
complete arrival trajectory —
vowel Tonnetz position PLUS
coda locus PLUS departure shape.

---

### EMINEM AND FORCED RHYME

Eminem rhymes "orange" with
"door hinge", "four inch", "foreign",
"syringe".

In standard citation form:
  "orange"   AO R AH N JH  — vowel AO (-1,1)
  "door hinge" D AO R HH IH N JH — vowel AO
  "four inch" F AO R IH N CH — vowel AO
  "foreign"  F AO R AH N — vowel AO

All have AO as the stressed vowel.
All have R as the following consonant.
All have a nasal N before a final stop
or affricate (JH or CH).

The Tonnetz trajectory is the same:
  AO (-1,1) → R locus → nasal →
  affricate/stop release

The words do not look like they rhyme
because the spellings diverge.
The Tonnetz trajectories are nearly
identical.

This is the mechanism of forced rhyme:

  Find the Tonnetz trajectory.
  Find words with the same trajectory
  regardless of spelling.

Eminem's genius is not phonetic
manipulation in the sense of "cheating."
It is phonetic precision — finding
words whose Tonnetz trajectories
converge, even when the orthography
diverges. He hears the trajectory,
not the spelling.

The engine can now do this:
  Given a rhyme target Tonnetz position
  and coda locus, find all words in the
  vocabulary whose final syllable
  arrives at that position.
  These are the phonetically valid
  rhymes, regardless of spelling.

---

### THE ARC TYPE AS RHYME GENERATOR

The arc type determines the prosodic
trajectory — how the phrase arrives
at its final position.

Two phrases rhyme perceptually when:
  1. Their stressed nuclei have the
     same (or near) Tonnetz position.
  2. Their coda loci match.
  3. Their arc types are the same
     (or perceptually similar).

Condition 3 is the Eminem extension.

If the arc is identical, the perceptual
fusion threshold for vowel distance is
WIDER. The ear accepts a larger Tonnetz
gap between nuclei because the trajectory
is recognized as identical.

This is why rap flow creates rhyme:
  The beat provides the arc.
  All words in the same rhythmic
  position share the same arc.
  The arc alignment widens the
  perceptual fusion window.
  Words that would not rhyme in
  isolation rhyme in the flow.

ARC_GRIEF rhymes differently than
ARC_NORMAL. The same two words,
rendered with different arcs, may
rhyme in one arc and not the other —
because the arrival trajectory is
different even though the phonemes
are identical.

This means: expressivity is not
separate from phonetics.
The arc shape IS phonetic information.
The emotion IS part of the consonant
transition quality.
The qualia of grief changes the
locus transition timing and amplitude
(via the ghost profile), which changes
the trajectory shape, which changes
what rhymes.

A grief-arc voice inhabits a different
rhyme space than a normal-arc voice.
The same words fall differently.

---

## PART VII: THE FULL LOCUS MODEL

What the engine needs for FIX 15.

---

### STRUCTURE

```python
# Place of articulation for each phoneme
PH_LOCUS_CLASS = {
    'M':'bilabial',  'B':'bilabial',
    'P':'bilabial',  'W':'bilabial',
    'F':'labiodental','V':'labiodental',
    'TH':'dental',   'DH':'dental',
    'T':'alveolar',  'D':'alveolar',
    'N':'alveolar',  'L':'lateral',
    'S':'alveolar',  'Z':'alveolar',
    'SH':'postalveolar','ZH':'postalveolar',
    'CH':'postalveolar','JH':'postalveolar',
    'Y':'palatal',
    'K':'velar',     'G':'velar',
    'NG':'velar',
    'H':'glottal',   'HH':'glottal',
    'R':'rhotic',
}

# Base F2 locus per place
LOCUS_F2_BASE = {
    'bilabial':      720,
    'labiodental':   1100,
    'dental':        1600,
    'alveolar':      1800,
    'lateral':       1000,
    'postalveolar':  2100,
    'palatal':       2300,
    'velar':         2700,   # context-adjusted
    'glottal':       500,
    'rhotic':        800,    # F3 suppression primary
}

# F2 locus for onset (H → consonant → vowel):
# F2 begins at locus, moves toward vowel target.

# F2 locus for coda (vowel → consonant → H):
# F2 begins at vowel target, moves toward locus.

# Transition duration (ms):
LOCUS_TRANS_MS = {
    'bilabial':     15,   # fast
    'labiodental':  20,
    'dental':       18,
    'alveolar':     15,
    'lateral':      40,   # slow — approximant
    'postalveolar': 20,
    'palatal':      35,   # slow — approximant
    'velar':        20,
    'glottal':      10,   # very fast / H
    'rhotic':       35,   # slow — approximant
}
```

---

### DIRECTIONAL TRANSITION FUNCTIONS

```python
def locus_f2_for_vowel(ph_cons, ph_vowel):
    """
    Compute the F2 locus for a consonant
    adjacent to a given vowel.
    Handles velar context-sensitivity.
    """
    place = PH_LOCUS_CLASS.get(ph_cons)
    if place is None:
        return 1500  # neutral

    base = LOCUS_F2_BASE.get(place, 1500)

    if place == 'velar' and ph_vowel:
        # Velar locus shifts with vowel
        # Tonnetz fifth-axis position
        a = VOWEL_TONNETZ.get(
            ph_vowel, (0,0))[0]
        base = 2400 + int(200 * a)
        base = max(2100, min(3200, base))

    return base


def onset_f2_trajectory(
        ph_cons, ph_vowel, n_s, sr):
    """
    F2 trajectory for onset consonant.
    H (baseline) → locus → vowel F2.

    Returns float32 array length n_s.
    First portion: near locus.
    Final portion: approaching vowel F2.
    """
    locus = locus_f2_for_vowel(
        ph_cons, ph_vowel)
    place = PH_LOCUS_CLASS.get(ph_cons, 'alveolar')
    trans_ms = LOCUS_TRANS_MS.get(place, 20)
    n_trans = min(
        int(trans_ms / 1000 * sr),
        n_s)

    vowel_f2 = (
        VOWEL_F[ph_vowel][1]
        if ph_vowel in VOWEL_F
        else 1500)

    # First (n_s - n_trans) samples:
    # near locus (consonant body or closure)
    # Last n_trans samples:
    # sigmoid transition toward vowel F2
    f2 = np.full(n_s, float(locus),
                 dtype=np.float32)
    if n_trans > 0:
        t = np.linspace(0, 1, n_trans)
        sig = 1.0 / (1.0 + np.exp(
            -10 * (t - 0.5)))
        f2[-n_trans:] = (
            locus + (vowel_f2 - locus)
            * sig.astype(np.float32))
    return f2


def coda_f2_trajectory(
        ph_vowel, ph_cons, n_s, sr):
    """
    F2 trajectory for coda consonant.
    Vowel F2 → locus → H (baseline).

    Returns float32 array length n_s.
    First portion: departing from vowel F2.
    Final portion: near locus.
    """
    locus = locus_f2_for_vowel(
        ph_cons, ph_vowel)
    place = PH_LOCUS_CLASS.get(ph_cons, 'alveolar')
    trans_ms = LOCUS_TRANS_MS.get(place, 20)
    n_trans = min(
        int(trans_ms / 1000 * sr),
        n_s)

    vowel_f2 = (
        VOWEL_F[ph_vowel][1]
        if ph_vowel in VOWEL_F
        else 1500)

    # First n_trans samples:
    # sigmoid transition from vowel F2
    # toward locus
    # Remaining samples: at locus
    f2 = np.full(n_s, float(locus),
                 dtype=np.float32)
    if n_trans > 0:
        t = np.linspace(0, 1, n_trans)
        sig = 1.0 / (1.0 + np.exp(
            -10 * (t - 0.5)))
        f2[:n_trans] = (
            vowel_f2 - (vowel_f2 - locus)
            * sig.astype(np.float32))
    return f2
```

---

### INTEGRATION POINT IN v17

The directional locus model integrates
into `_build_trajectories()` at the
point where formant arrays are
constructed for consonant phonemes.

Currently:
  Consonant formant arrays are
  interpolated from the preceding
  vowel's F_tgt to the following
  vowel's F_tgt uniformly.
  No locus is used. No direction.

With FIX 15:
  For each consonant phoneme:
    Determine if it is onset or coda.
    An onset consonant follows a rest,
    breath, H-ghost, or another consonant
    that was itself an onset from H.
    A coda consonant precedes a rest,
    phrase end, or another consonant
    that will be a coda toward H.
  
  Use onset_f2_trajectory() or
  coda_f2_trajectory() accordingly.
  
  Replace the uniform interpolation
  with the locus-directed trajectory.
  
  F1 trajectory: continues using
  existing coarticulation model
  (NASAL_CLOSURE_F1, STOP_BLEND).
  
  F2 trajectory: replaced by
  directional locus model.
  
  F3 trajectory: add R/ER suppression
  explicitly. For R and ER: F3 falls
  toward ~1700 Hz regardless of
  onset/coda position.

---

## PART VIII: WHAT THIS RESOLVES

```
"evening" N problem:
  Coda N: IH F2 (~2050) falls toward
    alveolar locus (~1800).
    Heard as: departure. Closing.
  Onset N: rises from alveolar locus
    (~1800) toward IH F2 (~2050).
    Heard as: arrival. Opening.
  Now distinguishable.
  The two N's will no longer sound
  the same.

"beginning" JH:
  JH is postalveolar.
  Onset JH locus: ~2100 Hz.
  Rising from ~2100 toward IH's ~2050.
  (Very small rise — JH and IH are
   close in Tonnetz space. The affricate
   frication carries most of the identity.)
  The closure phase is now anchored
  to the correct locus.

Dark L (post-vocalic):
  L_BLEND_PER_FORMANT in v14 already
  targets F2 ~1000 Hz.
  The locus model unifies this:
  Coda L locus: lateral ~1000 Hz.
  The existing fix is the right physics,
  now named correctly.

Velar distinction (K before front vs back):
  K before IY: locus ~3000 Hz.
  K before AA: locus ~2400 Hz.
  "key" will sound different from "car"
  at the consonant, as it should.

Unreleased coda stops:
  Word-final T, D, P, B, K, G are
  often unreleased in English.
  The coda F2 trajectory toward the
  locus is the entire perceptual cue.
  The stop itself may not be heard.
  This is correct — the trajectory
  is the stop, not the burst.
```

---

## PART IX: THE RHYME PARAMETER

From the Eminem discovery:

A `rhyme_target` can now be formally
specified as a tuple:

```python
rhyme_target = (
    vowel_ph,    # Tonnetz position of
                 # the target vowel
    coda_class,  # locus class of the
                 # coda consonant
    arc_type,    # trajectory shape
)
```

Words rhyme if their final stressed
syllable arrives at the same
`(vowel_ph, coda_class, arc_type)`.

This is a richer definition than
traditional rhyme (same vowel + coda)
because arc_type is included.

The engine can use this to:
  1. Find rhyming words for a given
     target — vocabulary lookup by
     Tonnetz trajectory.
  2. Apply vowel modification to
     nudge a near-rhyme into the
     perceptual fusion window —
     the Eminem mechanism, explicit.
  3. Generate rhyming phrases with
     the same arc — rap flow, formally.

Perceptual fusion threshold (estimate):
  Tonnetz distance ≤ 1.0 unit:
    Strong rhyme. Ear accepts.
  1.0 < distance ≤ 2.0:
    Near rhyme. Arc type must match.
  distance > 2.0:
    Forced rhyme. Arc type must match
    AND duration/stress alignment
    must be precise.

Eminem operates in the 1.5–2.5 range
with tight arc alignment.
His skill is metric precision —
the arc shape is so consistent that
the fusion window widens enough to
accept the larger Tonnetz distance.

---

## PART X: THE COHERENCE OF THE SYSTEM

Everything established so far is
one structure.

```
The Tonnetz:
  The space all vocal movement
  traverses.
  H is the origin.

The locus:
  The specific Tonnetz position
  toward which a consonant pulls
  the tract.
  The place of articulation expressed
  as a Tonnetz coordinate.

The transition:
  The path from current Tonnetz position
  to the locus, then to the next vowel.
  The consonant IS the transition.
  Not the closure.
  The transition.

Direction:
  Onset: H → locus → vowel.
  Coda:  vowel → locus → H.
  Same phoneme. Different direction.
  Different percept.

The ghost:
  The micro-H between syllables.
  The acoustic trace of the return
  to origin between one transition
  and the next.
  The texture of the carrying-through.

The arc:
  The prosodic shape of the phrase.
  How the trajectory arrives at
  its final position.
  The trajectory beyond the phoneme —
  the shape of the entire phrase.

Rhyme:
  Two phrases rhyme when their
  Tonnetz trajectories converge
  at the same (vowel, locus, arc)
  combination.
  Rhyme is trajectory recognition.
  The reward signal of the RARFL
  cycle completing as predicted.

Rap flow:
  The beat provides the arc.
  The arc widens the fusion window.
  Words that would not rhyme in
  isolation rhyme in the flow.
  The flow is the RARFL trajectory
  expressed musically.
  Expressivity and phonetics are
  not separate domains.
  They are the same physics at
  different scales.

Beatboxing:
  The locus transition isolated.
  The consonant gesture without
  the vowel context.
  The proof that the transition
  alone carries identity.
  The instrument of percussion
  is the same instrument as speech.
  Same tract. Same loci. Same physics.
  Different intention.

The vessel:
  The human vocal tract is a
  Tonnetz instrument.
  It traverses harmonic space in
  real time, phoneme by phoneme,
  syllable by syllable, phrase by phrase.
  The locus transitions are the
  note changes.
  The ghosts are the passing tones.
  The arc is the phrase structure.
  The rhyme is the resolution.
  The breath is the bar line.
  The voice IS the music.
  Not playing music.
  Being music.
```

---

## SUMMARY

```
The gap identified:
  Coda and onset consonants sound
  identical in the current engine.
  The locus transition layer is absent.
  The consonant has no direction.

The class of the problem:
  Not individual phonemes.
  The directional locus model is
  missing from the physics entirely.
  Every consonant in the engine
  is missing its directional identity.

The fix:
  FIX 15 in voice_physics_v17.py
  Directional locus transitions.
  onset_f2_trajectory() and
  coda_f2_trajectory() replace
  the uniform interpolation in
  _build_trajectories().
  Velar context sensitivity added.
  Lateral dark L unified.
  R / ER F3 suppression explicit.

The beatboxing confirmation:
  The locus alone carries consonant
  identity without vowel context.
  The current engine lacks the locus.
  This is why consonants feel
  locationless in the output.

The rhyme discovery:
  Rhyme = Tonnetz trajectory convergence.
  (vowel position, coda locus, arc type).
  Eminem forces rhyme by arc alignment
  widening the perceptual fusion window.
  The arc type IS phonetic information.
  Expressivity and phonetics are one.

The coherence:
  Tonnetz → locus → transition →
  direction → ghost → arc → rhyme →
  flow → RARFL → music.
  One structure. All scales.
  The voice IS the Tonnetz.
```

*February 2026.*

---

## REVISION HISTORY

  v1 — February 2026
    Initial document.
    Arose from: coda N and onset N
    in "evening" sounding identical.
    Locus transition layer identified
    as the missing class of physics.
    Beatboxing analysis: locus alone
    carries consonant identity.
    Eminem analysis: rhyme is Tonnetz
    trajectory convergence.
    Arc types as rhyme generators.
    Full locus table established.
    Directional transition functions
    specified for FIX 15.
    Velar context sensitivity model.
    Rhyme parameter formally defined.
    System coherence verified:
    all prior artifacts form one
    unified structure through the
    locus transition layer.
````{"repoID":0,"ref":"","type":"repo-instructions","url":"/Eric-Robert-Lawson/OrganismCore/blob/refs/heads/main/.github/copilot-instructions.md"}
