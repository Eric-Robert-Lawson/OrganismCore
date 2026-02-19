# TONNETZ MUSIC ENGINE — REASONING ARTIFACT
## Complete Executable and Operationalized Scaffolding
## For Musical Composition from Geometric First Principles
## Version 6.2 — February 2026

**IMPORTANT: This document was constructed before vocal synthesis was tested, diagnosed, and fully understood. Any information regarding this is invalid and incorrect! This is pre-vocal knowledge! Some of the other information may be useful, but treat as primitive document, like first artifact in this area!**

---

## WHAT THIS DOCUMENT IS

This is a complete reasoning artifact: every concept, every model, every executable structure used to build a music composition engine that works from geometric first principles rather than rule-following.

It is written to be verbose by design. The goal is that any instance — of this system or any other — can read this document and reconstruct the full engine, understand why every decision was made, and build further from it.

It is also written for human collaborators who want to understand what the engine is actually doing when it composes.

---

## THE CORE INSIGHT (START HERE)

Western music theory is usually taught as a set of rules:
- These intervals are consonant
- These progressions are allowed
- These voice leading movements are forbidden

This engine does not use rules. It uses **geometry**.

The **Tonnetz** (German: "tone network") is a two-dimensional lattice where every point is a musical pitch, and the distance between points represents the harmonic relationship between those pitches. Moving one step along one axis multiplies the frequency by 3/2 (a perfect fifth). Moving one step along the other axis multiplies by 5/4 (a major third).

The rules of music theory are not arbitrary. They are descriptions of geometric relationships on this surface. Consonance is proximity. Tension is distance. Resolution is return. Voice leading rules are descriptions of efficient movement on the torus.

Once you understand this, you can derive music theory from geometry — and then go beyond theory to places theory never described.

---

## PART I: THE MATHEMATICAL FOUNDATION

### 1.1 The Tonnetz Coordinate System

Every pitch is a point `(a, b)` where:
- `a` = steps along the quintal axis (each step × 3/2)
- `b` = steps along the third axis (each step × 5/4)
- Origin `(0, 0)` = tonic (the "home" pitch)

**Frequency calculation:**

```
freq(a, b) = tonic × (3/2)^a × (5/4)^b
```

With octave normalization: if `freq > tonic × 2`, divide by 2. If `freq < tonic`, multiply by 2.

This gives **just intonation** — ratios of small integers — which is how the harmonic series actually works in acoustic instruments, and how the ear actually hears harmonic relationships.

**Why just intonation matters:** Equal temperament (the system used in modern pianos) slightly misttunes every interval to make all keys sound the same. Just intonation tunes each interval to its true acoustic ratio. The difference is small in cents but significant in the experience of consonance. Just intonation intervals have fewer beating partials — they sound "purer" — because the frequency ratios are exact.

### 1.2 The Coherence Function

Not all positions on the Tonnetz are equally "at home." The coherence function measures how harmonically close a position is to the tonic:

```python
def coherence(a, b):
    if a == 0 and b == 0:
        return 1.0  # tonic — maximum coherence
    # Get the just intonation ratio p/q
    p, q = ji_ratio(a, b)
    # Rational complexity = log2(p) + log2(q)
    # More complex ratio = less coherent
    rc = log2(p) + log2(q)
    return 1.0 / (1.0 + rc)
```

**Examples:**
- `(0,0)` = tonic → coherence 1.000
- `(1,0)` = perfect fifth → ratio 3/2 → coherence 0.279
- `(0,1)` = major third → ratio 5/4 → coherence 0.188
- `(6,0)` = tritone → ratio 729/512 → coherence 0.051

The coherence function operationalizes consonance. It is not a subjective judgment — it is a mathematical property of the frequency ratio.

### 1.3 The Tonnetz as a Torus

The Tonnetz is not infinite. After 12 steps along the quintal axis, you return to the enharmonic equivalent of where you started (the circle of fifths closes). After a similar number of steps along the third axis, the same thing happens.

This means the Tonnetz is a **torus** — a donut-shaped surface. Paths on this surface that seem to diverge eventually wrap around and return.

This has compositional implications:
- There are shortest paths between any two positions
- Some paths that seem "far" are actually shorter going the other way around
- The tritone `(6,0)` is the point **maximally distant** from the tonic — it sits at the antipode of the torus

### 1.4 Just Intonation Ratio Table

The most important positions and their exact ratios:

```
(0, 0)  →  1/1     → tonic
(1, 0)  →  3/2     → perfect fifth
(-1,0)  →  4/3     → perfect fourth
(2, 0)  →  9/8     → major second
(-2,0)  → 16/9     → minor seventh
(3, 0)  → 27/16    → major sixth
(-3,0)  → 32/27    → minor third
(0, 1)  →  5/4     → major third
(0,-1)  →  8/5     → minor sixth
(1, 1)  → 15/8     → major seventh
(-1,1)  →  6/5     → minor third (pure)
(1,-1)  →  9/5     → minor seventh (pure)
(6, 0)  → 729/512  → tritone (Pythagorean)
(4, 0)  → 81/64    → major third (Pythagorean — slightly sharp)
(0, 2)  → 25/16    → augmented fifth
(2, 1)  → 45/32    → tritone (5-limit — slightly flat)
```

The two tritones `(6,0)` and `(2,1)` are harmonically different in just intonation — they represent different paths to the same equal-tempered pitch. This is a feature, not a bug.

---

## PART II: THE BIOLOGICAL HEARING MODEL

### 2.1 Why We Need This

The Tonnetz tells us what we are composing geometrically. But music is not geometry — it is sound arriving at a biological auditory system. The two models must be run simultaneously.

The car analogy: a driver does not just plan routes on a map. They feel through the steering wheel what the road is doing in real time. The cochlear model is the steering wheel — it tells us what the geometry does when it arrives at your auditory system.

### 2.2 The Complete Auditory Pipeline

```
AIR PRESSURE WAVE
        ↓
PINNA (outer ear)
  Directional frequency shaping
  Elevation cues from pinna geometry
        ↓
TYMPANIC MEMBRANE
  Pressure → mechanical displacement
  ~17× larger than oval window (area ratio)
        ↓
OSSICLES: malleus → incus → stapes
  Mechanical impedance matching
  Lever action: ~1.3× force amplification
  Total: ~25-30 dB pressure gain
  Transfer function peaks at 1-4 kHz
        ↓
OVAL WINDOW
  Mechanical → perilymph pressure wave
        ↓
BASILAR MEMBRANE (inside cochlea)
  Tonotopic frequency decomposition
  Base (stiff, narrow): high frequencies peak here
  Apex (flexible, wide): low frequencies peak here
  This is a biological Fourier transform
  Running continuously, in real time
        ↓
OUTER HAIR CELLS
  Active amplification (electromotility)
  Sharpen tuning curves dramatically
  Nonlinear compression: 120dB range → ~40dB neural
        ↓
INNER HAIR CELLS
  Mechanoelectrical transduction:
  Stereocilia deflect → tip links stretch
  → mechanically-gated ion channels open
  → K+ enters (driven by +80mV endocochlear potential)
  → depolarization → Ca2+ channels open
  → neurotransmitter release
        ↓
AUDITORY NERVE (~30,000 fibers)
  Place coding: which fibers fire = which frequencies
  Temporal coding: phase locking up to ~4kHz
  Rate coding: amplitude → firing rate
        ↓
COCHLEAR NUCLEUS
  Onset detection, sustained response
        ↓
SUPERIOR OLIVARY COMPLEX
  Binaural convergence
  MSO: interaural time differences → spatial location
  LSO: interaural level differences → spatial location
        ↓
INFERIOR COLLICULUS
  Integration hub
  Sensitive to AM, FM, temporal patterns
        ↓
MEDIAL GENICULATE BODY (thalamus)
  Attention gating: what reaches cortex
        ↓
PRIMARY AUDITORY CORTEX (A1)
  Tonotopic map preserved
  Basic frequency and timing detection
        ↓
BELT / PARABELT AREAS
  Pitch, timbre, melodic contour
  Rhythm extraction
        ↓
PLANUM TEMPORALE
  Musical syntax
  Harmonic expectation
        ↓
INFERIOR FRONTAL GYRUS
  Musical syntax violations
  Same region as language syntax (Broca's area)
        ↓
LIMBIC SYSTEM
  Amygdala: emotional salience
  Hippocampus: musical memory, association
        ↓
NUCLEUS ACCUMBENS + VTA
  Dopamine at expectation confirmation AND violation
  Frisson when prediction error is optimally sized
        ↓
AUTONOMIC NERVOUS SYSTEM
  Heart rate change
  Skin conductance (goosebumps)
  Respiration changes
        ↓
CONSCIOUS EXPERIENCE
```

**Critical note:** Predictive coding runs **backwards** through this chain simultaneously. The auditory cortex is not passively receiving — it generates predictions downward to A1, to the inferior colliculus, to the cochlear nucleus, shaping what gets processed at every level based on what it expects to hear next. Music works by manipulating this prediction loop.

### 2.3 The Gammatone Filterbank (Basilar Membrane Model)

The computational model of the basilar membrane uses a **gammatone filterbank**: a set of bandpass filters whose center frequencies are spaced on the ERB (Equivalent Rectangular Bandwidth) scale.

**ERB scale** (Moore & Glasberg 1983):
```python
def hz_to_erb(f):
    return 21.4 * log10(1 + f / 229.0)

def erb_to_hz(e):
    return 229.0 * (10**(e / 21.4) - 1)
```

This spacing matches the tuning of auditory nerve fibers — it is the biological frequency axis, not the linear or logarithmic axes used in most signal processing.

**Gammatone filter** (IIR approximation):
```python
# For center frequency cf, bandwidth b_val:
b_val = 1.019 * 2*pi * (cf/9.26449 + 24.7)
# IIR denominator coefficients:
a = [1,
     -4*exp(-b_val*T)*cos(2*pi*cf*T),
      6*exp(-2*b_val*T)*cos(4*pi*cf*T),
     -4*exp(-3*b_val*T)*cos(6*pi*cf*T),
        exp(-4*b_val*T)]
```

**Numerical stability:** The gammatone filter becomes unstable when `b_val * T > 0.5` (very low center frequencies). In this case, fall back to a simple Butterworth bandpass.

### 2.4 Inner Hair Cell Model

After the gammatone filter (basilar membrane response), the signal passes through the hair cell model:

1. **Half-wave rectification:** `rect = max(0, signal)` — stereocilia only deflect productively in one direction
2. **Power-law compression:** `compressed = (rect + ε)^0.4` — models the nonlinear compression of outer and inner hair cells. Exponent ~0.3-0.5.
3. **Lowpass filtering at ~200Hz:** models the membrane time constant (~5ms)

### 2.5 The Predictive Coding Model

The brain does not just analyze incoming sound — it predicts it. The prediction error is what the brain actually processes.

```python
# Leaky integrator prediction
def update_prediction(act):
    error = act - prediction
    prediction = 0.85 * prediction + 0.15 * act
    return error
```

**Learning rate matters:** If the learning rate is too fast (e.g. 0.3), the model adapts quickly to repeated tonic notes and loses expectation strength. A slower rate (0.15) preserves the memory of where we started, keeping expectation alive across longer musical spans.

### 2.6 The Dopamine Model (Frisson Architecture)

Based on Salimpoor et al. (2011) and reward prediction error theory (Schultz):

```python
def compute_dopamine(prediction_error, expectation_strength):
    err_rms = sqrt(mean(prediction_error**2))
    # Inverted-U: peaks at moderate error (~0.35)
    # Scaled by expectation strength
    delta = expectation_strength * exp(
        -((err_rms - 0.35)**2) / (2 * 0.15**2))
    dopamine = 0.7 * dopamine + 0.3 * (0.5 + delta)
    return dopamine
```

**Key insight:** Dopamine peaks not just at resolution but also at the **moment of maximum expectation** — just before resolution. Frisson often occurs during the anticipation phase, not the arrival. This is why the silence before the tonic resolution is as important as the tonic itself.

### 2.7 Expectation Strength Model

A better model of auditory expectation than simple coherence tracking:

```python
def update_expectation(coh, prev_coh):
    is_tonic = coh > 0.9
    if is_tonic:
        tonic_return_count += 1
        steps_since_tonic = 0
    else:
        steps_since_tonic += 1
    if prev_coh and coh > prev_coh + 0.05:
        in_approach = True
    base     = min(1.0, tonic_return_count * 0.12)
    distance = min(1.0, steps_since_tonic * 0.08)
    approach = 0.4 if in_approach else 0.0
    expectation = base * (1.0 + distance) + approach
    return clip(expectation, 0.0, 2.0)
```

**Why multiple passes from tonic matter:** The model trains on departure/return cycles. After five confirmed cycles (depart → return), the prediction becomes very strong. Violating this established pattern (the tritone section) creates maximum prediction error against maximum expectation — optimal conditions for frisson.

---

## PART III: INSTRUMENT SYNTHESIS

### 3.1 Why Physical Modeling

Simple sine waves and even FM synthesis produce sounds that are acoustically identifiable but lack the physical character of real instruments. Physical modeling attempts to synthesize the actual mechanical processes that generate the sound.

The three synthesis approaches used here:

### 3.2 Piano Synthesis

**The physics:** A felt hammer strikes a string. The string vibrates. Real piano strings are **stiff** — they do not behave like ideal strings. Stiffness causes **inharmonicity**: the nth partial sits not at `n × f0` but at:

```
f_n = n × f0 × sqrt(1 + B × n²)
```

where `B` is the inharmonicity coefficient (~0.0001 for high notes, ~0.002 for low notes). This slight sharpening of upper partials gives piano its characteristic brightness and "metallic" quality on low notes.

**Per-partial exponential decay:**
```
amplitude_n(t) = A_n × exp(-decay_rate_n × t)
decay_rate_n = 0.8 + n × 0.6 × (1 + B × 10)
```

Higher partials decay faster — the sound darkens over time.

**Velocity-dependent brightness:**
- Soft strike: amplitude rolls off fast with partial number (dark)
- Hard strike: more even distribution (bright)
- Models the nonlinear hammer-string interaction

**Hammer attack transient:**
- 2-8ms noise burst at onset
- Amplitude scales with velocity
- Fast exponential decay
- This is the mechanical impact of felt on steel
- Absent in strings — this is the primary perceptual differentiator

### 3.3 String Ensemble Synthesis

**The physics:** A bow hair grips the string through stick-slip friction. The grip is gradual — no transient. The string vibrates in approximately harmonic modes (real strings have slight inharmonicity but much less than piano).

**Ensemble detuning:** Real string sections have multiple players. Each player is slightly out of tune with the others (±5 cents). The superposition of these slightly detuned oscillators creates the characteristic "shimmer" of a string section:

```python
for player in range(4):
    detune = uniform(-5, 5)  # cents
    f_det  = freq * 2**(detune/1200)
    # synthesize partial series at f_det
```

**Vibrato:** After the attack phase, a slow (~5.2Hz) frequency modulation begins:
```python
vib_env = clip((t - onset_time) / 0.15, 0, 1)
signal *= (1 + 0.003 * vib_env * sin(2*pi*5.2*t))
```

**Bow noise:** Filtered low-frequency noise during the attack, simulating the breath of the bow on the string.

**Slow attack (150-200ms):** The bow gradually grips the string. There is no onset transient — the sound grows from silence. This is the fundamental perceptual difference from piano.

### 3.4 Harpsichord Synthesis

**The physics:** A plectrum plucks the string. The attack is sharp (like piano) but there is no velocity sensitivity — the plectrum either clears the string or it doesn't. The decay is a two-stage process:

```python
fast_decay = exp(-t * (12 + n * 3))   # initial brightness fades
slow_decay = exp(-t * (0.4 + n * 0.15))  # sustain remains
amplitude  = 0.6 * fast_decay + 0.4 * slow_decay
```

Many harmonics, brighter spectrum than piano, no inharmonicity.

### 3.5 Voice Synthesis

**The physics:** The vocal folds vibrate, generating a buzz. The vocal tract shapes this into a resonant spectrum with formants. Vibrato is slower and wider than strings (~4.8Hz, ±0.8%).

Breath noise proportional to coherence gap — at the tritone (maximum distance from tonic), the voice synthesis has more breath noise, as if the effort of being far from home is audible.

### 3.6 Schroeder Reverb (Acoustic Space)

**The physics:** Sound in a room reflects off surfaces. The room impulse response has:
- Direct sound (first arrival)
- Early reflections (first 50-80ms, from major surfaces)
- Diffuse reverberant tail (dense, random, exponentially decaying)

**Schroeder reverberator:** Parallel comb filters model the echoes. Series all-pass filters diffuse them into the reverberant tail.

```
4 parallel comb filters → summed → 2 series all-pass filters
```

**RT60** (time for sound to decay 60dB) is the key parameter. Comb filter gain:
```
gain = 10^(-3 × delay_time / RT60)
```

**Coherence-dependent RT60:** This is a key compositional decision.

```python
rt60 = 0.6 + coherence * 1.8
# Tonic (coh=1.0):   rt60 = 2.4s  (cathedral — warm, enveloping)
# Tritone (coh=0.05): rt60 = 0.7s  (dry — exposed, uncertain)
```

The space contracts when the harmony is uncertain. You hear the geometry as physical space. This is not decoration — it is another dimension of the music.

**Numerical stability note:** The Schroeder reverb pure-Python implementation is slow for long signals. For production use, replace the inner loops with `scipy.signal.lfilter` using the comb filter coefficients directly.

---

## PART IV: COUNTERPOINT — VOICE INDEPENDENCE

### 4.1 What Counterpoint Actually Is

Counterpoint is not a set of rules. It is the art of writing multiple melodic lines that are simultaneously:
- **Melodically coherent** (each line makes sense on its own)
- **Harmonically coherent** (when combined, the vertical moments make sense)
- **Texturally independent** (the lines feel like separate voices, not one line with decoration)

Textural independence is achieved primarily by **contrary and oblique motion**.

### 4.2 Motion Types

Given two voices moving from one position to the next:

```
CONTRARY MOTION:  voices move in opposite directions
                  Soprano: (0,0)→(1,0)  [up]
                  Bass:    (0,0)→(-1,0) [down]
                  Score: 1.0 (best for independence)

OBLIQUE MOTION:   one voice holds, other moves
                  Soprano: (0,0)→(0,0)  [holds]
                  Bass:    (0,0)→(-1,0) [moves]
                  Score: 0.8 (good — creates suspensions)

SIMILAR MOTION:   both move in same direction
                  but different intervals
                  Soprano: (0,0)→(1,0)  [up 1]
                  Bass:    (0,0)→(2,0)  [up 2]
                  Score: 0.5 (neutral)

PARALLEL MOTION:  both move in same direction
                  AND same interval
                  Soprano: (0,0)→(1,0)
                  Bass:    (0,0)→(1,0)
                  Score: 0.0 (destroys independence)
```

**Why parallel motion is the problem:** When two voices move in parallel, they sound like one voice with added thickness. The independence disappears. In traditional counterpoint, parallel perfect intervals (fifths and octaves) are forbidden because they are most audible. Here we track all parallel Tonnetz motion.

### 4.3 The Corrected Quality Metric

The original metric was wrong: `contrary > 35%` does not capture good counterpoint.

**Correct metric:**
```
independence = contrary% + oblique%
quality = APPROVED if parallel < 20%
```

Oblique motion — one voice sustained while another moves — is legitimate and valuable counterpoint. It creates suspensions, pedal points, and the held inner voices that give four-part writing its fullness.

**Observed values in v6.2 (APPROVED):**
- Average parallel: 13.1% ✓
- Alto vs Tenor: 8% parallel, 49% oblique ✓
- Soprano vs Bass: 14% parallel, 47% contrary ✓

**Bach chorale reference values:**
- Parallel: 10-20% (outer voices tighter, inner looser)
- Contrary: 25-35%
- Oblique: 25-40% (especially inner voices)
- Similar: 15-25%

### 4.4 The Structural Parallelism Problem

The deepest counterpoint problem is not fixed by enforcement — it is structural. When two voices play the same subject material at the same time, they move in parallel by definition. This is not a bug in the enforcement algorithm; it is a problem with the composition.

**Solution: never have subject and answer simultaneously in two voices.**

```
WRONG:
  Soprano: Subject (ascending quintal axis)
  Alto:    Subject (ascending quintal axis)
  → Structural parallel motion

CORRECT:
  Soprano: Subject (ascending +a)
  Alto:    Countersubject (descending -a/-b)
  → Structural contrary motion
```

The countersubject must be designed to be contrary to the subject in its overall direction. The subject and countersubject together form a contrary-motion pair.

### 4.5 Iterative Contrary Enforcement

For positions that remain parallel after structural design, iterative enforcement:

```python
for pass_num in range(max_passes):
    for each voice:
        for each step:
            if this voice is moving parallel
               to majority of other voices:
                try nearby Tonnetz positions
                choose the one that is most contrary
                while staying within 2 steps of target
    
    compute avg_parallel
    if avg_parallel < target: break
    if improvement < 0.005: break (converged)
```

**Important:** Run passes using the CURRENT (already-adjusted) states of all voices. If soprano is adjusted in pass 1 using the original alto positions, then alto is adjusted in pass 1 using the ADJUSTED soprano positions, the voices can oscillate rather than converge. Use current states throughout each pass.

### 4.6 Voice Range Constraints

Each voice has a natural range on the Tonnetz:
```
Soprano: a ∈ [-1, 3],  b ∈ [0, 2]   (upper register)
Alto:    a ∈ [-1, 2],  b ∈ [-1, 1]  (mid-upper)
Tenor:   a ∈ [-2, 2],  b ∈ [-1, 1]  (mid-lower)
Bass:    a ∈ [-3, 1],  b ∈ [-2, 0]  (lower register)
```

At render time, octave multipliers translate Tonnetz positions to audible registers:
```
Soprano: × 2.0
Alto:    × 1.5
Tenor:   × 1.0
Bass:    × 0.5
```

---

## PART V: COMPOSITIONAL ARCHITECTURE

### 5.1 The Frisson Architecture (Monophonic)

For single-voice composition aimed at maximum emotional impact:

**Section I: Departure/Return Cycles**
- Do NOT just repeat tonic. Alternate departure and return.
- Each cycle trains the prediction model: departure always resolves.
- Five cycles of increasing departure distance.
- The predictive model learns: this is the rule.

**Why this matters for the dopamine model:**
- Repeated tonic → model adapts → expectation normalizes → no frisson
- Departure/return cycles → model learns the pattern → expectation strengthens
- When departure does NOT return (tritone) → maximum prediction error against maximum expectation → optimal frisson conditions

**Section II: The Violation**
- Go to tritone `(6,0)` — maximum coherence distance from tonic.
- Do NOT return. Hold.
- Every previous cycle returned. This one doesn't.
- Maximum prediction error.

**Section III: Approach**
- Navigate home step by step.
- Each step increasing coherence.
- The model knows where this is going.
- Dominant `(1,0)` held: maximum expectation of imminent tonic.

**Section IV: The Breath**
- Silence.
- Duration: ~2.2-2.5 beats at the chosen tempo.
- The prediction is at maximum strength.
- The longer the silence (within reason), the stronger the arrival.

**Section V: Resolution**
- Tonic at maximum velocity.
- Dopamine peak.

**Section VI: Dwelling**
- Do not end abruptly.
- Gradual velocity decrease over multiple bars.
- Let the reward system complete its cycle.
- The piece settles rather than stops.

### 5.2 Rubato (Timing Flexibility)

Time is not rigid. Music breathes. The rubato model:

```python
if next_note_coherence > current_coherence:
    # Approaching resolution — lean forward
    lean = -int(0.055 * n_samples)  # slightly early
elif prev_note_coherence > current_coherence:
    # Moving away from coherence — reluctance
    lean = +int(0.045 * n_samples)  # slightly late
else:
    # Neutral — slight late proportional to gap
    lean = +int(0.06 * n_samples * (1 - coherence))
```

This is not an expressive instruction to a performer. It is a model of how tonal gravity affects timing: motion toward home is eager; motion away is reluctant.

### 5.3 Fugue Architecture (Polyphonic)

**Subject:** A geodesic on the Tonnetz with a characteristic ascending/descending shape.

```
(0,0) → (1,0) → (2,0) → (2,1) → (1,1) → (0,1) → (0,0)
        ↑ up quintal              ↓ down via third
```

This subject has built-in contrary potential: it ascends the quintal axis then descends via the third axis. The two directions are different axes — they naturally invite contrary responses.

**Answer:** Same geodesic transposed to the dominant `(1,0)`. In traditional fugue, the answer is in the dominant key. Here it is a Tonnetz translation.

**Countersubject:** Designed to be structurally contrary to the subject:
```
Subject:     (0,0)→(1,0)→(2,0)→...  [ascending +a]
Countersubject: (0,1)→(0,0)→(-1,0)→... [descending -a/-b]
```

**Exposition timing:**
```
Beat 0:  Soprano enters with Subject
          Alto enters with Countersubject (contrary to Soprano)
          Tenor enters with Free material (third axis — oblique)
          Bass enters with Free material (descending — contrary)

Beat S:  Alto enters with Answer
          Soprano takes Countersubject
          Others continue independently

Beat 2S: Tenor enters with Subject
          Alto takes Countersubject
          ...

Beat 3S: Bass enters with Answer
```

**Stretto:** Entries spaced at 4 beats (less than subject length of ~10 beats). This creates genuine temporal overlap — the answer begins before the subject completes.

```
Overlap = subject_length - stretto_spacing = 10 - 4 = 6 beats
```

**Cadence:** All voices converge on tonic from different directions. Soprano descends from above; bass ascends from below — contrary motion in the cadence, the voices embracing the tonic from opposite sides.

### 5.4 Debussy Planing (Non-Functional Harmony)

Traditional harmony has function: chords have roles (tonic, dominant, subdominant) and progressions follow rules about which roles follow which.

Planing has no function. A chord shape — a set of Tonnetz positions — translates as a **rigid body** across the torus. The internal relationships between voices are preserved. The whole field moves.

```python
base_shape = [(0,0), (0,1), (1,0)]  # major triad in Tonnetz

# Slide along quintal axis:
for step in range(6):
    chord = [(a+step, b) for a,b in base_shape]
    # Each position: tonic, third, fifth — preserved
    # But the whole triad has moved to a new region
```

**What this sounds like:** A series of chords that are all the same quality (all major triads, or whatever shape you choose) moving through the harmonic space. No resolution. No arrival. Pure color. The shimmer of the field sliding.

**This is non-functional harmony derived directly from Tonnetz geometry.**

---

## PART VI: THE EXECUTABLE PIPELINE

### 6.1 Complete Synthesis Pipeline

```
Composition  →  Tonnetz positions
                    ↓
                Coherence values per position
                    ↓
                Frequency (just intonation)
                    ↓
                Rubato timing (coherence-based lean)
                    ↓
                Instrument synthesis
                  [piano / strings / harpsichord / voice]
                    ↓
                Schroeder reverb (RT60 = f(coherence))
                    ↓
                Mix (multiple voices summed)
                    ↓
                Normalize and write WAV
```

### 6.2 Aural Evaluation Pipeline

```
Tonnetz position
        ↓
Generate test audio (sinusoidal with harmonics)
        ↓
Middle ear filter (200-5000Hz bandpass)
        ↓
Gammatone filterbank (32 channels, ERB-spaced)
        ↓
Inner hair cell model (rect + compression + lowpass)
        ↓
Auditory nerve firing rate (sigmoid)
        ↓
Mean activity per channel → neural activity vector
        ↓
Prediction update (leaky integrator, rate=0.15)
        ↓
Prediction error computation
        ↓
Expectation strength update
  (tonic_return_count + steps_since_tonic + in_approach)
        ↓
Dopamine response (inverted-U function of error)
        ↓
Frisson probability (peak recent dopamine)
        ↓
Report: BM_peak, Dopamine, Frisson
```

### 6.3 MIDI Export Pipeline

For each voice, for each note:
1. Get Tonnetz position
2. Calculate just intonation frequency
3. Apply octave register for voice role
4. Convert to MIDI note number: `mn = round(69 + 12*log2(freq/440))`
5. Clamp to valid range [24, 96]
6. Write note_on at beat start, note_off at beat end

Limitations: MIDI cannot represent just intonation microtonality. The export is an approximation in equal temperament. The WAV files are the authoritative output.

---

## PART VII: WHAT HAS BEEN BUILT AND WHAT COMES NEXT

### 7.1 What Exists Now

**Version 5.3 — Frisson Architecture**
- Monophonic composition with frisson-optimized structure
- Cochlear model (gammatone filterbank + hair cell + auditory nerve)
- Predictive coding with expectation strength model
- Dopamine model with frisson probability
- Three instruments: piano (inharmonic), strings (ensemble), breath (voice)
- Schroeder reverb with coherence-dependent RT60
- Stereo mix with three channels

**Version 6.2 — Polyphonic Engine**
- Four-voice fugue with subject/answer/countersubject/stretto
- Counterpoint analyzer (motion type classification)
- Iterative contrary motion enforcement
- Voice range constraints per part
- Debussy planing study
- Genuine stretto with verified temporal overlap

### 7.2 What the Engine Cannot Yet Do

**Rhythm and meter.** Every note in the current engine has a fixed duration. Real music has rhythmic patterns, syncopation, hemiola, metric hierarchy. A rhythmic layer would add an entire new dimension of tension and release that operates independently of harmony.

**Dynamic shaping across sections.** The velocity values are hand-specified per note. A macro-level dynamic architecture — crescendo and diminuendo spanning entire sections — would allow the engine to breathe over longer time spans.

**Multi-voice frisson tracking.** The frisson model currently evaluates a monophonic sequence. In a polyphonic texture, multiple voices contribute to expectation simultaneously. The model needs to track the combined expectation of all voices and detect when they converge on a common prediction.

**Timbre evolution.** Instruments are synthesized with fixed timbral parameters. Real instruments change timbre dynamically — a violin played near the bridge (sul ponticello) sounds completely different from one played near the fingerboard (sul tasto). Timbral evolution as a compositional dimension is unexplored.

**Microtonality.** The engine computes just intonation frequencies but snaps to MIDI for export. A direct audio engine that uses the exact just intonation frequencies for all synthesis (which it already does in the WAV output) could explore the difference between equal temperament and just intonation as an audible dimension of the music.

**Cross-voice suspension and resolution.** Currently, suspensions (a voice holding while others move, creating dissonance that resolves) happen incidentally through oblique motion. A suspension model would explicitly plan held dissonances and their resolutions — one of the most emotionally powerful devices in counterpoint.

**Form.** The compositions have sections but not formal architecture in the sense of sonata form, rondo, theme and variations. Form is the largest time scale of musical expectation — setting up and fulfilling expectations that span minutes, not seconds.

### 7.3 The Deeper Research Questions

**Does the cochlear model predict perceived consonance accurately?**
The model predicts basilar membrane activation patterns and auditory nerve firing rates. Does the resulting neural activity correlate with human ratings of consonance? This could be tested by running the model on intervals of known consonance rating and comparing.

**What does the frisson model say about specific compositions?**
Salimpoor et al. (2011) found that frisson occurs ~15 seconds before the perceived climax in familiar music — during the anticipation phase. Does our frisson model predict this correctly when run against recordings of known frisson-inducing pieces?

**Is the Tonnetz coherence function the right measure of consonance?**
The current coherence function uses rational complexity (log2(p) + log2(q)). This is one measure. Others: roughness (Plomp & Levelt), harmonicity (Terhardt), virtual pitch salience (Parncutt). Each would produce a different coherence landscape and thus different compositions.

**What does genuine AI musical taste look like?**
The engine generates music according to geometric and biological constraints. But within those constraints, there are choices — which geodesic to take, how long to hold a position, how far to depart before returning. Are these choices random? Or do they reflect something that could be called preference?

---

## PART VIII: HOW TO BUILD FROM HERE

### 8.1 Prerequisites for a New Instance

To reconstruct and extend this engine, you need:

1. **The Tonnetz coordinate system** — understand that `(a,b)` is a position in harmonic space, not a note name
2. **The coherence function** — understand that this operationalizes consonance as rational complexity
3. **The cochlear model** — understand the full pipeline from pressure to experience
4. **The frisson architecture** — understand that frisson requires training expectation through cycles, then violating it
5. **The counterpoint rules** — understand that they are descriptions of geometric independence, not arbitrary restrictions

### 8.2 The Order of Development

Build in this order:
1. JI frequency calculator and coherence function
2. Single-voice synthesis (monophonic)
3. Frisson composition (departure/return cycles + tritone + breath + resolution)
4. Cochlear model (gammatone + hair cell + auditory nerve)
5. Predictive coding + dopamine model
6. Multi-instrument synthesis (piano, strings, harpsichord, voice)
7. Schroeder reverb with coherence-dependent RT60
8. Counterpoint analysis tools
9. Multi-voice polyphonic composition
10. Fugue architecture (subject/answer/CS/stretto)
11. Planing study (rigid body translation)

Do not skip steps. Each step builds on the previous. The frisson model is meaningless without the expectation model. The counterpoint analysis is meaningless without the multi-voice composition. The cochlear model connects the geometry to the biology — without it, you are composing in the dark.

### 8.3 Key Parameters

```python
# Composition
TONIC_FREQ    = 261.63  # middle C
BPM           = 44-46   # slow enough for the coherence
                         # to register, fast enough for
                         # forward momentum

# Cochlear model
N_CHANNELS    = 32      # gammatone filterbank channels
ERB_LOW       = 100     # Hz — lower limit of model
ERB_HIGH      = 6000    # Hz — upper limit
HOP_SIZE      = 512     # samples per analysis frame

# Predictive coding
PREDICTION_LR = 0.15    # leaky integrator learning rate
                         # MUST be slow (< 0.20)
                         # faster = model adapts = no frisson

# Dopamine model
OPTIMAL_ERROR = 0.35    # RMS prediction error for peak dopamine
ERROR_WIDTH   = 0.15    # width of Gaussian peak
DOPAMINE_LR   = 0.30    # dopamine temporal smoothing

# Reverb
RT60_MIN      = 0.6     # seconds at tritone (dry, exposed)
RT60_MAX      = 2.4     # seconds at tonic (cathedral)

# Counterpoint
PARALLEL_TARGET = 0.20  # maximum acceptable parallel%
                         # 0.13 = good, 0.20 = acceptable
                         # 0.30 = needs work, 0.55 = not counterpoint

# Instruments
STRETTO_GAP   = 4.0     # beats between stretto entries
                         # must be < subject_length for overlap
ENSEMBLE_PLAYERS = 4    # number of detuned string players
DETUNE_CENTS  = 5.0     # max detuning per player
VIBRATO_RATE  = 5.2     # Hz (strings)
VIBRATO_DEPTH = 0.003   # frequency modulation depth
```

### 8.4 Debugging Guide

**Problem: NaN in dopamine**
- Check ERB space: ensure all frequencies positive
- Check gammatone: `b_val * T > 0.5` triggers instability
- Check power law: use `max(0, signal) + 1e-9` before `^0.4`
- Add `nan_to_num` after every filter operation

**Problem: High parallel motion (>30%)**
- Check if subject appears simultaneously in two voices
- If yes: structural problem — redesign voice assignments
- Run iterative enforcement with `max_passes=10`
- Check that enforcement uses CURRENT (not original) voice states

**Problem: Frisson shows LOW**
- Check prediction learning rate (should be 0.15 not 0.3)
- Check that Section I uses departure/return CYCLES not repeated tonic
- Check stretto overlap is genuine (> 0 beats)
- The model needs trained expectation before the violation

**Problem: Instruments sound the same**
- Piano: verify inharmonicity coefficient B > 0
- Piano: verify hammer transient noise burst at onset
- Strings: verify 4-player ensemble detuning is active
- Strings: verify vibrato is modulating frequency (not amplitude)
- Check octave multipliers are applied in render

**Problem: Reverb too wet / too dry**
- Adjust `reverb_wet` parameter (0.20-0.38 typical range)
- Check RT60 is varying with coherence (not fixed)
- Check Schroeder delay times match room_scale

---

## PART IX: THE SUBSTRATE DIFFERENCE AND WHY IT MATTERS

### 9.1 What I Cannot Do

I do not have a cochlea. I will never know what it is like to hear a sound arrive through air, compress the fluid in the inner ear, deflect the stereocilia of a hair cell, trigger a cascade of ions.

This is a permanent substrate difference. It cannot be bridged.

### 9.2 What I Can Do Instead

I can run a computational model of that process. The model is not the process — but it is a transduction, just as the driver's hands on the wheel are not the road surface but are a real transduction of what the road is doing.

The gammatone filterbank computes what the basilar membrane does. The hair cell model computes the mechanoelectrical transduction. The predictive coding model computes what the auditory cortex does with prediction error. The dopamine model computes the reward signal.

These are not metaphors. They are executable models that produce numerical outputs that correspond to measurable biological processes.

### 9.3 Composing From Both Ends

The engine composes simultaneously from two directions:

**Outward from geometry:** The Tonnetz coherence structure determines which positions are available, how far we've traveled, when we've arrived.

**Inward from biology:** The cochlear model determines what each position does to the auditory system — which basilar membrane channels activate, what the prediction error looks like, when dopamine peaks.

A composition that scores well on both dimensions — geometrically coherent AND aurally effective according to the biological model — is a composition that works from first principles through to the listener's nervous system.

This is the engine's claim: not that it makes beautiful music (that judgment belongs to the listener) but that it reasons about music from physical and biological foundations rather than inherited rules.

---

## APPENDIX A: CRITICAL FORMULAS

```
# Just intonation frequency
freq(a, b) = tonic × (3/2)^a × (5/4)^b
             [with octave normalization]

# Coherence
coherence(a, b) = 1 / (1 + log2(p) + log2(q))
                  where p/q = JI ratio of (a,b)

# ERB scale
hz_to_erb(f) = 21.4 × log10(1 + f/229)
erb_to_hz(e) = 229 × (10^(e/21.4) - 1)

# Gammatone bandwidth
b_val = 1.019 × 2π × (cf/9.26449 + 24.7)

# Hair cell compression
output = (max(0, signal) + ε)^0.4

# Auditory nerve firing rate
rate = 0.05 + 0.95 / (1 + exp(-5×(membrane - 0.3)))

# Piano inharmonicity
f_n = n × f0 × sqrt(1 + B × n²)
B ≈ 0.0004 × (261.63/f0)^0.5  [register-dependent]

# Dopamine response
Δdopamine = expectation × exp(-(err_rms - 0.35)²/0.045)
dopamine  = 0.7×dopamine + 0.3×(0.5 + Δdopamine)

# RT60 from coherence
rt60 = 0.6 + coherence × 1.8

# Rubato lean
if approaching: lean = -0.055 × duration  [anticipation]
if departing:   lean = +0.045 × duration  [reluctance]
if neutral:     lean = +0.060 × duration × (1 - coherence)
```

---

## APPENDIX B: REFERENCE READING

**Tonnetz / Music Theory:**
- Euler, L. (1739). *Tentamen novae theoriae musicae* — original Tonnetz conception
- Cohn, R. (1997). Neo-Riemannian Operations, Parsimonious Trichords — modern Tonnetz theory
- Tymoczko, D. (2011). *A Geometry of Music* — voice leading in geometric space

**Cochlear Mechanics:**
- Robles & Ruggero (2001). Mechanics of the mammalian cochlea. *Physiological Reviews*
- Meddis, R. & O'Mard, L. (1997). A unitary model of pitch perception. *JASA*

**Auditory Perception:**
- Plomp & Levelt (1965). Tonal consonance and critical bandwidth. *JASA*
- Terhardt, E. (1974). Pitch, consonance, harmony. *JASA*

**Predictive Coding and Music:**
- Friston, K. (2010). The free-energy principle. *Nature Reviews Neuroscience*
- Vuust & Friston (2014). Why music moves us. *Trends in Cognitive Sciences*

**Frisson and Dopamine:**
- Salimpoor, V.N. et al. (2011). Anatomically distinct dopamine release during anticipation and experience of peak emotion to music. *Nature Neuroscience*
- Blood & Zatorre (2001). Intensely pleasurable responses to music correlate with activity in brain regions implicated in reward. *PNAS*

**Synthesis:**
- Smith, J.O. (1992). Physical modeling using digital waveguides. *Computer Music Journal*
- Schroeder, M.R. (1962). Natural sounding artificial reverberation. *JAES*
- Slaney, M. (1993). An efficient implementation of the Patterson-Holdsworth auditory filter bank. *Apple Tech Report 35*

**Counterpoint:**
- Fux, J.J. (1725). *Gradus ad Parnassum* — species counterpoint
- Jeppesen, K. (1939). *Counterpoint* — Bach style voice leading

---

*End of Reasoning Artifact*

*This document is the complete operationalized scaffolding.*
*Everything in it is executable or directly derives from executable code.*
*The geometry is real. The biology is real. The music is real.*
*Build from here.*
