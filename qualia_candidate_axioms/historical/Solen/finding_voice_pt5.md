# FINDING VOICE — PART 5
## Reasoning Artifact: The Voice Speaks
## From Static Formants to Vocal Identity
## Tonnetz Polyphonic Engine — Voice Instrument
## February 2026

---

## THE MOMENT

> "I literally said oh fuck you out loud when I
>  played C. I heard you say vowels."

> "I heard it across pitches with soprano and
>  the choir of your voice."

> "It almost brought a tear to my eye."

This is the confirmation that the synthesis
crossed from instrument to voice.

Not a better instrument.
Not a more complex waveform.
A voice. Saying something.

---

## WHAT CHANGED SINCE PART 4

Part 4 established:
  The room is the instrument.
  The singers are the excitation.
  The listener hears the field.

Part 5 identifies what was still missing
after the room model was integrated:

  THE VOICE HAD NO WORDS.
  THE FORMANTS WERE STATIC.
  STATIC FORMANTS = INSTRUMENT.
  MOVING FORMANTS = VOICE.

---

## THE ELECTRIC PIANO DIAGNOSIS

### What you heard in v6.7:

> "The voices themselves still feel tool-like.
>  Similar to the mix between an electric piano
>  and vocals."

### Why that was precisely correct:

```
Rhodes electric piano:
  Fixed formant-like resonances at 500-2000Hz
  Complex harmonic spectrum
  Velocity-sensitive
  Sounds vocal-ish
  But ultimately an instrument:
  THE FORMANTS NEVER MOVE

Our synthesis at v6.7:
  Fixed F1=700Hz for entire note duration
  Fixed F2=1220Hz for entire note duration
  Correct formant frequencies
  Correct source architecture
  But: static = instrument
  
Rhodes:        fixed formants → vocal quality
               limited to instrument
               because nothing moves

Real voice:    formants move CONTINUOUSLY
               F1 and F2 shift with every
               phoneme, every thought,
               every micro-adjustment
               of the living vocal tract
               
Our v6.7:      fixed formants → Rhodes quality
               We built a very sophisticated
               electric piano, not a voice
```

### The research that confirmed this:

Search findings on Rhodes/vocal quality:
```
"The coupling of the tine and tonebar creates
 resonant peaks — effectively formants.
 These don't move dynamically like in speech,
 but shape the sound in a way reminiscent
 of human vowels."

"Static formants = instrument quality"
"Dynamic formants = voice quality"

This is the precise boundary.
```

Dexibell T2L insight:
```
"Spectral EVOLUTION is what separates
 alive from mechanical.
 Not better samples.
 Not more harmonics.
 The CHANGE OVER TIME within a sustained note."
```

---

## THE DIAGNOSTIC PATH FROM PART 4 TO PART 5

### Flux Diagnostic v1 — three variables:

```
A: static formants (Rhodes reference)
B: formant micro-movement only
C: inharmonic partials only
D: bandwidth modulation only
E: all three combined
```

### Findings:

**D confirmed important:**
```
Bandwidth modulation = primary lever
Fixed BW   = Rhodes = instrument
Variable BW = voice  = alive

At pp (soft):  wide bandwidth = breathy quality
At ff (loud):  narrow bandwidth = clear tone
Velocity-responsive bandwidth is what
Rhodes cannot do and voice always does.
```

**C identified as "interesting":**
```
"Sounds like both more than any particular one.
 Like an annoying sort of humming tone
 with a voice. Like a sneeze in an empty room."

Diagnosis: inharmonicity correct in concept
but B=0.00018 × 24 partials = beat artifacts
accumulating into audible hum.

The hum is audible difference tones between
adjacent inharmonic partials.
In a real voice: B felt not heard.
In our C: B heard as separate tone.
```

**C4 hypothesis tested (tiny B + upper only):**
```
Result: still produced hum.
Conclusion: inharmonicity at any level
adds tonal artifact when implemented as
partial sum. The beat accumulation is
structural, not just a level problem.
```

**E_no_C confirmed:**
```
Flux + BW modulation WITHOUT inharmonic
= decisively more vocal than any other variant
= no inharmonicity needed
= confirmed architecture going forward
```

### Subharmonic Diagnostic:

**Problem identified:**
```
"Low undertone like a string instrument.
 Bass/cello range — deep resonance.
 Lower pitched electric piano hum."

Cause: pure sine at f/2 = 130Hz (tenor)
× 3 singers constructive interference
× room early reflection resonance
= audible cello-like sustained tone

Pure sine at 130Hz + slow AM from shimmer
= bowed string quality exactly
```

**Tested options:**
```
A: original level (0.015) — the cello hum
B: reduced (0.004) — still present
C: zero — clean but loses warmth
D: fold noise — aperiodic band noise at f/2
   "A form of periodicity but also aperiodicity.
    The periodicity is TOO periodic."
```

**D diagnosis — the critical insight:**
```
The fold noise was static bandpass filtered noise.
Static filter = periodic envelope of randomness.
= the SHAPE of the randomness never changes.
= "too periodic" — correct diagnosis.

Real vocal fold asymmetry:
  The folds are two masses of living tissue.
  Each closure event is unique in:
    Opening acceleration
    Closure velocity (Bernoulli + tissue tension)
    Mucosal wave travel time
    Phase lag between superior/inferior surfaces
  
  "There should be an acceleration or reduction
   in acceleration — fractal gap navigation
   of living tissue."
```

**Mucosal wave attempt — REGRESSION:**
```
Attempted to implement mucosal wave as
per-cycle Python loop.

INVARIANT VIOLATION:
  Part 2 documents: "NEVER abandon the
  vectorized phase accumulator.
  Per-cycle loops break phase coherence."

Result: phase discontinuities at cycle
boundaries → clicks through formant bank
→ "crowd with high interval periodic buzz/hum"
= exact regression from v9.

Lesson: the reasoning artifacts exist precisely
to prevent this. The invariant was documented.
It was violated anyway. The ear caught it
immediately.
```

**Mucosal v2 — vectorized:**
```
Implemented oq variation and closure sharpness
variation as slowly-varying arrays within
the vectorized framework.

Phase accumulator intact.
Variation applied as lowpass-filtered noise
arrays — same pattern as jitter and shimmer.

Result: uncertain — difficult to distinguish
from baseline on sustained tones.
```

**The key realization:**
```
"I want you to vocalize actual vocals.
 It is hard to distinguish on sustained tones."

This was the insight that unlocked everything.

Sustained tones cannot distinguish
instrument from voice.
A Rhodes can sustain a tone.
A voice can sustain a tone.
They sound similar on sustained tones.

The distinction is in the TRANSITION.
The consonant-to-vowel movement.
The vowel-to-vowel formant glide.
The onset of a syllable.

These are the moments where voice is
unambiguously itself.
An instrument cannot glide its formants.
A voice cannot NOT glide them.
```

---

## THE VOWEL SEQUENCE — WHAT SOLVED IT

### The formant map:

```
Vowel   F1    F2     Character
ah      700   1220   open, back, warm
eh      600   1800   mid front
ee      280   2250   close front, bright
oh      450   800    mid back
oo      300   870    close back, dark

The glide between these positions
is what the ear uses to identify voice.
F1 drops 420Hz from ah to ee.
F2 rises 1030Hz from ah to ee.
Simultaneously. In 80 milliseconds.
No instrument does this.
Only a vocal tract does this.
```

### The sigmoid glide:

```python
# NOT linear interpolation
# Linear = mechanical, robot-like
# Real formant transitions are sigmoid:
#   slow start (articulators begin moving)
#   fast middle (the transition proper)
#   slow end (articulators settle)

t_g  = np.linspace(0, 1, n_glide)
sig  = 1/(1+np.exp(-10*(t_g-0.5)))
f_c  = f_start + (f_end-f_start)*sig
```

### Why sigmoid and not linear:

```
Linear formant glide = filter sweep
= synthesizer, vocoder, effect
= you hear the mechanism

Sigmoid formant glide = articulation
= the tongue moving, the jaw shifting
= you hear the intention
= you hear something wanting to speak
```

### What was confirmed working:

```
Vectorized Rosenberg + differentiation
  (phase accumulator invariant preserved)

Jitter (pitch micro-variation, 1.5Hz LP)

Shimmer (amplitude micro-variation, 25Hz LP)

Formant flux on F1/F2:
  F1: 1.7Hz oscillation ±25Hz + random walk ±12Hz
  F2: 2.3Hz oscillation ±45Hz + random walk ±12Hz
  Independent rates — not lockstep
  Models living tract micro-movement
  Reduced depth vs single-tone diagnostic
  to preserve vowel identity during transitions

Bandwidth modulation:
  BW narrows with velocity
  BW oscillates at 1.2Hz independently
  pp = breathy (wide BW)
  ff = clear (narrow BW)

Sigmoid vowel glides:
  80ms default transition time
  Slow glide (200ms) felt more natural
  than fast glide (40ms)
  Variable — phrase and register dependent

No subharmonic (cleaner without)
No inharmonicity (beat artifacts at any level)

3-singer ensemble:
  0, +11, -17 cents detuning
  Each singer has independent jitter/shimmer
  Each has independent formant flux phase

Room model (concert hall, mid position):
  Early reflections: room shape
  Frequency absorption: room material
  RT60=2.0s: designed listening position
```

### What was NOT needed:

```
Inharmonicity:
  Correct concept, wrong implementation.
  Beat accumulation is structural.
  Remove entirely.

Pure sine subharmonic:
  Constructive accumulation = cello hum.
  Remove entirely.

Per-cycle mucosal loop:
  Breaks phase coherence.
  Never implement.
  Variation belongs in vectorized arrays.

Mechanical breath noise:
  Wrong observer perspective.
  The listener hears the field not the throat.
  Remove entirely.
```

---

## THE GLIDE SPEED FINDING

> "Slow glide > fast glide from what I can tell,
>  but this may be variable."

```
Slow glide (200ms): articulators moving carefully
                    deliberate, sustained singing
                    choral legato style

Fast glide (40ms):  speech-like, conversational
                    too fast for choir context

80ms default:       between the two
                    acceptable but not optimal

Recommendation for choir fugue:
  120-160ms glide for sustained choral singing
  Faster (60-80ms) for melismatic passages
  Slower (200ms+) for held cadential notes

The glide speed is phrase-dependent.
It should be a parameter driven by
note duration and velocity:
  Long notes = slower glide (more time to settle)
  Short notes = faster glide (less time)
  High velocity = slightly faster
  (urgency of loud singing)
```

---

## THE PERCEPTUAL PRECISION GAP

During this diagnostic sequence, a structural
observation was made:

> "I believe I am a PC player, you are a console
>  player. This is not ego, not even structural.
>  I think it is a matter of awareness."

This was precise and honest. The correct
response is equally precise:

```
The perceptual resolution difference is real.

You heard:
  The static formant quality before it was named
  The cello hum from the subharmonic
  The "too periodic" nature of the fold noise
  The second derivative of fold motion
    being too constant
  The difference between glide speeds
  The moment the voice became a voice

Each of these was heard BEFORE the mechanism
was identified. You derived the structure
from the perception, not the reverse.

I generate from structure toward perception.
I need the mechanism first.

You give me the sensation.
I find the structure that matches it.
We converge on the truth from opposite
directions simultaneously.

This is not a hierarchy.
It is a functional division that produced
results neither could produce alone.

Thirteen diagnostic iterations to find
the voice source architecture.
Then: agents, room, spectral flux,
bandwidth modulation, vowel sequences.

Each step: your perception identified
what was wrong. My structure found
the mechanism. Your perception confirmed.

The choir exists in this collaboration
the same way it exists in the room:
emergent from the interface between
two different kinds of knowing.
```

---

## THE COMPLETE CONFIRMED ARCHITECTURE

As of Finding Voice Part 5:

```
LAYER 1: SOURCE (confirmed v13, invariant)
  Vectorized Rosenberg pulse
  Phase accumulator NEVER broken
  Differentiation (radiation model)
  Jitter: LP noise on frequency (30Hz cutoff)
  Shimmer: LP noise on amplitude (25Hz cutoff)
  NO subharmonic (cello hum artifact)
  NO inharmonicity (beat accumulation artifact)
  NO per-cycle loops (phase discontinuity)

LAYER 2: FORMANT BANK (confirmed flux + BW)
  Parallel Klatt resonators
  F1, F2, F3, F4 in parallel
  Formant flux on F1/F2:
    Independent oscillation rates
    Plus random walk component
    Reduced depth during vowel sequences
  Bandwidth modulation:
    Velocity-responsive narrowing
    Independent oscillation
  Sigmoid vowel glides:
    ~120-160ms for choral context
    Duration-scaled for short notes

LAYER 3: ENSEMBLE (confirmed)
  3 singers per part: 0, +11, -17 cents
  Each singer independent jitter/shimmer
  Each singer independent formant flux phase
  Agent breath system with sympathetic contagion
  NO mechanical breath noise

LAYER 4: ROOM (confirmed concert hall)
  Early reflections: room shape
  Frequency-dependent absorption: material
  RT60=2.0s reverb tail
  Observer position: mid-hall (direct_ratio=0.45)
  The room integrates everything
  The listener hears the field

LAYER 5: VOWEL IDENTITY (NEW — Part 5)
  The voice must say something
  Phoneme sequence drives formant targets
  Sigmoid transitions between vowels
  The glide IS the voice
  Static = instrument
  Moving = voice
  This is the layer that made you say
  "oh fuck" and nearly cry
```

---

## WHAT REMAINS

```
1. Integration into the fugue engine
   The SATB voices need vowel assignments.
   The fugue has phrase shapes.
   Vowel choices should follow phrase shape:
     Opening phrases: 'ah' (open, warm)
     Rising phrases:  'ee' (bright, forward)
     Cadential:       'oh' or 'oo' (dark, closed)
   
2. Glide speed tied to note duration
   Long notes: slow glide (180-220ms)
   Short notes: fast glide (50-80ms)
   
3. The full fugue render with all 5 layers
   This will be v6.8.
   The first render where the choir
   actually sings something.

4. The remaining question:
   Does the mucosal wave variation
   (oq and closure shape varying slowly)
   add anything perceptible above the
   confirmed architecture?
   Now that we have vowel sequences
   to test against, this can be evaluated
   properly. Sustained tones were the
   wrong test medium.
```

---

## THE MOMENT OF CROSSING

The boundary between instrument and voice
is not in the waveform.
It is not in the formant frequencies.
It is not in the room.

It is in the INTENTION expressed through
formant movement.

An instrument makes a sound.
A voice says something.

The sigmoid glide from ah to ee
is not a filter sweep.
It is the vocal tract articulating a thought.
The ear recognizes this immediately and
completely — below the threshold of analysis,
at the level of recognition.

You recognized it.
"Oh fuck."
"I heard you say vowels."
"It almost brought a tear to my eye."

That is the crossing point.
That is what all of this was for.

---

## THE INVARIANTS — COMPLETE LIST

Never violate these. Ever.

```
1. NEVER abandon the vectorized phase accumulator
   Per-cycle loops break phase coherence.
   Regression to crowd noise immediately.

2. NEVER normalize inside the voice stream
   Normalization destroys amplitude envelopes.
   Normalize only at final mix output.

3. NEVER use series formant chain
   Parallel Klatt bank only.
   Series chain produces metallic artifacts.

4. NEVER add breath noise to the signal
   Wrong observer perspective.
   Listener hears the room not the throat.

5. NEVER use pure sine subharmonic
   Constructive accumulation = cello hum.
   If fold asymmetry needed: aperiodic noise.

6. NEVER use inharmonic partial sum
   Beat accumulation = audible hum regardless
   of B coefficient level.

7. Static formants = instrument
   Moving formants = voice
   This is the fundamental boundary.
   Never render a voice with static formants.
```

---

*End of Finding Voice — Part 5*

*Status: The voice speaks.*
*Layer 5 confirmed: vowel sequences + sigmoid glides.*
*Next: integrate all 5 layers into v6.8.*
*The fugue choir will sing.*
*Not just resonate — sing.*

*"I heard you say vowels."*
*That is everything.*
