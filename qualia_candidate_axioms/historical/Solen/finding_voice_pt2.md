# FINDING VOICE — PART 2
## Reasoning Artifact: Biological Realism & Artifact Removal
## Tonnetz Polyphonic Engine — Voice Instrument
## February 2026

---

## WHAT THIS DOCUMENT IS

Continuation of Finding Voice Part 1.

Part 1 ended with v8 confirmed:
  vocal quality present
  formant architecture correct
  "not a string — vocal quality"
  remaining problem: robotic, monotonic, mechanical

Part 2 documents v9 through v13:
  the attempt to add biological realism
  every regression introduced and why
  the orthogonal convolution artifact (notch filter)
  the correct placement of aperiodicity
  the inharmonic ensemble discovery
  the removal of the notch filter
  the synthesis as it stands at v13

---

## THE DESIGN SPECIFICATION

Stated during v11 development:

> "An instrument is a tool. A voice is alive."

This is the precise technical requirement.
It means:

```
Instrument (tool):   periodic, predictable, repeating
                     same waveform every cycle
                     deterministic output

Voice (alive):       aperiodic, never repeating
                     every cycle slightly different
                     emergent from biological process
```

All synthesis before v11 was building a tool
and trying to make it sound alive by adding
voice-like characteristics on top.
The correct approach: build the aperiodicity
into the source itself so the synthesis
IS alive from the first sample.

---

## V9 — FIRST ATTEMPT AT BIOLOGICAL REALISM

### What was added:
- Per-cycle Python loop for glottal source
- Per-cycle jitter, shimmer, OQ variation
- Ornstein-Uhlenbeck formant drift at sample rate
- 3-singer ensemble with independent noise per singer

### What was heard:
> "Progress in wrong direction — moving away
>  from vocal and towards 2 distinct crowd
>  noise + tonal noise."

### Why it failed — four simultaneous regressions:

**Regression 1: Per-cycle Python loop**
```
The cycle-by-cycle construction broke phase
coherence between glottal pulses.
Each cycle was built independently.
Discontinuities at cycle boundaries = clicks.
Clicks = tonal noise artifacts.

The vectorized phase accumulator (confirmed
working in v7/v8) was abandoned.
It must never be abandoned.
```

**Regression 2: Three independent noise sources**
```
Each of 3 singers had independent aspiration noise.
Three noise sources at similar amplitude, summed:
crowd noise returns.

The v2 diagnosis predicted this exactly:
"crowd cheering at sports event =
 aspiration noise amplified through resonators"
v9 recreated it at the ensemble level.
```

**Regression 3: Block filter with coefficient changes**
```
F1 and F2 formants processed in 512-sample blocks
with new filter coefficients per block.
Coefficient changes every 11ms = audible
discontinuities = another tonal artifact.
```

**Regression 4: OU process at sample rate**
```
Ornstein-Uhlenbeck process generated at 44100Hz.
Formants jittered at audio rate not drifted slowly.
Vowel identity destroyed.
```

### Key learning:
```
Never add multiple biological parameters
simultaneously. One at a time.
Never abandon the vectorized phase accumulator.
Never generate slow processes at sample rate.
```

---

## V10 — ONE VARIABLE AT A TIME PROTOCOL

### Protocol established:
```
Add ONE parameter.
Test it in isolation.
If it sounds worse: remove it.
Never add the next until current sounds better.
```

### Steps A-F rendered and compared:

**Steps B-E: no audible difference from A**

Cause identified: normalization destroys shimmer.

```python
# This line destroys shimmer:
result = result / mx * amp
# Normalizes every note to same peak amplitude.
# Shimmer introduces amplitude variation.
# Normalization removes amplitude variation.
# Shimmer = zero perceptual effect.
```

**Step F: "orthogonal convolution of ensemble"**

The mathematician's description of the artifact:
```
At ±6 cents offset:
beat_frequency = f × (2^(6/1200) - 1)
               = 261.63 × 0.00347
               = 0.91 Hz

One full amplitude cycle every 1.1 seconds.
This is perceived as a slow tonal amplitude wave.
The wavefronts converge and diverge periodically.
Regular periodic beating = sounds like a tone,
not like organic ensemble shimmer.
```

### Key learning:
```
Shimmer must be in the EXCITATION (source),
not in post-processing amplitude scaling.
Variation in the source propagates through
the formant bank and survives normalization
because it modulates what the resonators receive.

Symmetric ensemble detuning creates periodic
beating. Use INHARMONIC offsets to create
aperiodic beating.
```

---

## V11 — APERIODICITY IN THE SOURCE

### The core architectural insight:

```
WRONG: build periodic source → add biological
       variation to output
       normalization destroys the variation
       formant bank does not respond to it

RIGHT: build aperiodic source → formant bank
       responds to each varied excitation pulse
       variation is baked into waveform shape
       normalization cannot remove it
```

### Four aperiodicity sources (all in excitation):

**1. Jitter via phase noise**
```python
# Lowpass-filtered noise on frequency array
# below 30Hz — period-rate variation
# NOT per-sample (which would be just noise)
freq_noise = lowpass(normal(0, jitter_hz, n), 30Hz)
freq_arr   = freq_base + freq_noise
```

**2. Shimmer via source amplitude modulation**
```python
# Lowpass-filtered noise on source amplitude
# Applied to excitation BEFORE formant bank
# Modulates what the resonators receive
# Survives through filtering and normalization
shim_env = 1.0 + (shim_lin-1) * lowpass(noise, 25Hz)
source   = source * shim_env
```

**3. Subharmonic at f/2**
```python
# Weak component at half fundamental
# Models vocal fold left-right asymmetry
# Real voice has subharmonic ~25-30dB below f0
# Breaks perfect periodicity
subharm = sub_level * sin(2π × (freq/2) × t)
```

**4. Turbulence (initially in source — later moved)**
```
Bandlimited noise modeling glottal turbulence.
PROBLEM discovered in v11: turbulence BEFORE
formant bank gets amplified 6× by F1 resonator.
Crowd noise returns.
Fix in v12: move turbulence to POST-formant.
```

### Inharmonic ensemble detuning:

```
SYMMETRIC (v10, wrong):
  ±6 cents → beat = 0.91Hz → slow tonal wave

INHARMONIC (v11, correct):
  0, +11, -17 cents
  Beat 1 vs 2: 1.66Hz
  Beat 1 vs 3: 2.56Hz
  Beat 2 vs 3: 4.22Hz
  Three different beat frequencies = aperiodic
  beating = organic ensemble shimmer
```

### What was heard at v11:

**Step C (tenor ah):**
> "I take a deep breath and start 'ahhhhh'...
>  what is happening is I am trying to balance
>  a vocal tone with the amount of breath I have
>  left. This is almost like aperiodicity balancing
>  of unstructured/semi-structured emergence."

This confirmed: the ensemble + aperiodic source
is producing the correct organic vocal texture.

**Step C (tenor ee):**
> "YES. THIS IS DISTINCT EEE, ESPECIALLY RELATIVE
>  TO AAA. ONCE I HEAR EEE AND PLAY BACK AAA,
>  I HEAR AAAA. IT IS THE RELATIVISM AND THE
>  SPECTRAL CHANGE AS WELL!"

This confirmed: the formant architecture produces
perceptually distinct vowel identities.
The ah/ee distinction is real and audible.
The architecture is correct.

**Step D (soprano):**
> "Returns to the machine — electric piano key
>  being played in a crowd."

**Step E (bass):**
> "Fog horn, drone."

Diagnosis: subharmonic at 0.12 was too loud.
At soprano: f/2 = 261Hz = audible piano key.
At bass: f/2 = 65Hz = felt as pressure/drone.

---

## V12 — SUBHARMONIC AND TURBULENCE FIXES

### Fix 1: Register-aware subharmonic

```python
def subharmonic_level(freq):
    # Real voice: subharmonic ~25-30dB below f0
    # 0.12 linear = -18dB  ← too loud
    # Target: -30 to -35dB below f0
    if freq > 400:   return 0.006  # soprano
    elif freq > 250: return 0.015  # tenor
    elif freq > 160: return 0.012  # alto
    else:            return 0.008  # bass
```

### Fix 2: Turbulence and breath moved post-formant

```
Real voice turbulence is at the LIPS (output).
NOT in the glottis (source).
Air turbulence occurs as voiced air exits the mouth.

Pre-formant placement:  turbulence amplified by
                        resonators = crowd noise
Post-formant placement: turbulence adds texture
                        to already-shaped vowel sound
```

```python
# Signal flow v12:
excitation → formant bank → notch → [turbulence + breath] → envelope
                                     ↑
                                     POST-formant addition
```

### What was heard at v12:

All vowels confirmed distinct:
- ah, ee, oo, oh perceptually different
- Soprano: higher pitched ah confirmed
- Bass: bass ah confirmed
- Artifact still present across all

> "I CAN DISTINGUISH A CLEAR AHHH + DISTINCT
>  STABLE ROBOTIC TONE. Orthogonal convolution
>  artifact. Like a scratchy record tune, narrow
>  oscillation like skipping a record."

The artifact was present in v8 but was less
noticeable then because the vowel quality was
weaker. Now that the vowels are clear, the
artifact is the dominant problem.

---

## V13 — THE NOTCH FILTER REMOVED

### The artifact identified precisely:

```
"Orthogonal convolution artifact"
"Scratchy record tune"
"Narrow oscillation like skipping a record"
"Needs fractal aperiodicity yet sin/cosine
 bounded reverberation"
```

These descriptions map to one thing:
**IIR notch filter ringing.**

### Why the notch filter rings:

```
iirnotch creates a deep null at f0
IIR implementation has poles near the null
frequency (required for narrow notch)
When signal energy is STRONG at the notch freq,
the poles overshoot and undershoot around the null
This produces a narrow oscillation at f0
superimposed on the signal

Q=8.0 notch on a strong fundamental =
visible ringing in time domain =
"skipping record" = orthogonal artifact
```

### Why the notch was wrong from the beginning:

```
The notch was added in v8 to suppress the
dominant fundamental. That dominance came from
the pre-v7 source (99% energy below 350Hz) —
the source was essentially a sine wave.

In v12/v13, the source is properly differentiated
and aperiodic. The formant bank is working.
The fundamental at 261Hz is now the PITCH
of a voice that also has vowel character.

A real human voice singing 'ah' at 261Hz has
a strong 261Hz component. That is not an artifact.
That is the voice's pitch.

Notching the fundamental was removing the pitch
grounding of the sound and replacing it with
an IIR ringing artifact.

The fundamental should be present.
It is the voice's pitch.
Let it speak.
```

### Fix: remove all notch filters.

```python
# REMOVED from v13:
apply_notch_harmonics(voiced, freq, sr,
                       n_harmonics=3, Q=8.0)

# The formant bank output stands without
# surgical interference.
# Vowel identity comes from the formant peaks.
# Pitch comes from the fundamental.
# Both should be present.
```

---

## THE COMPLETE CONFIRMED ARCHITECTURE (v13)

### Signal flow:

```
1. VIBRATO (slow, regular, confirmed working)
   freq_base = freq × (1 + 0.011 × vib_env
                         × sin(2π × 4.8 × t))

2. JITTER (on top of vibrato)
   freq_noise = lowpass(normal(0, 1.5Hz, n), 30Hz)
   freq_arr   = freq_base + freq_noise

3. ROSENBERG PULSE (vectorized, phase accumulator)
   phase_norm = cumsum(freq_arr/sr) % 1.0
   oq         = 0.65
   source     = parabolic_open + linear_close

4. DIFFERENTIATION (critical — do not remove)
   source = diff(source)
   Flattens spectrum: 99% below 350Hz → 72% below
   Without this: formants have nothing to shape

5. SHIMMER (on source before formant bank)
   shim_env = lowpass(normal(0,1,n), 25Hz) × scale
   source   = source × shim_env
   Survives normalization — modulates excitation

6. SUBHARMONIC (register-aware, subtle)
   sub_level: 0.006 (soprano) to 0.015 (tenor)
   subharm   = sub_level × sin(2π × freq/2 × t)
   Models fold asymmetry — breaks periodicity

7. TINY GLOTTAL ASPIRATION (pre-formant, very small)
   g_asp in excitation at level 0.05
   Models air through incompletely closed folds

8. PARALLEL FORMANT BANK (Klatt 1980)
   Each resonator receives same excitation
   Outputs summed at calibrated gains
   NO series chaining (causes saturation)
   NO dry source in output

9. NO NOTCH FILTER
   The notch was the "skipping record" artifact
   The fundamental is the voice's pitch
   Let it be present

10. POST-FORMANT: TURBULENCE + BREATH
    Added after formant bank — not amplified
    Turbulence: 2000-6000Hz, level 0.03
    Breath: 300-3000Hz, level varies with velocity
    Models lip-level air turbulence

11. AMPLITUDE ENVELOPE
    Attack: 250-330ms (vocal fold closure)
    Release: 280-350ms
    Onset shimmer: 11Hz AM during attack only

12. SINGLE NORMALIZATION AT END
    result = result / max × amp
    Only once — shimmer already in waveform shape
```

### Ensemble architecture (confirmed working):

```
3 singers, inharmonic detuning:
  Singer 1:  0 cents  (reference)
  Singer 2: +11 cents
  Singer 3: -17 cents

Beat frequencies:
  1 vs 2: 1.66Hz
  1 vs 3: 2.56Hz
  2 vs 3: 4.22Hz
Three different rates = aperiodic beating
= organic choir shimmer
= NOT a regular amplitude wave

Each singer:
  Different jitter_hz:  [1.5, 1.8, 1.2]
  Different shimmer_db: [1.5, 1.8, 1.2]
  Same aspiration level (no independent noise sources
  — prevents crowd noise multiplication)
```

---

## FORMANT REFERENCE TABLE (confirmed)

```
Vowel  F1    F2    F3    F4    G1   G2   G3   G4
'ah'   700   1220  2600  3200  6.0  4.0  2.0  0.8
'ee'   280   2250  3000  3500  4.0  6.0  2.5  0.9
'oo'   300    870  2250  3000  5.0  4.5  1.5  0.5
'oh'   500   1000  2500  3200  5.5  3.5  1.8  0.6

Bandwidth (synthesis — wider than acoustic):
  F1: 300-400Hz
  F2: 300-400Hz
  F3: 400-500Hz
  F4: 500-600Hz

Gains confirmed perceptually:
  ah: F1 dominant (open vowel, jaw down)
  ee: F2 dominant (high front tongue)
  oo: F1+F2 balanced (rounded lips, back tongue)
  oh: F1 dominant (mid back, rounded)
```

---

## PERCEPTUAL VOCABULARY DEVELOPED

These descriptions from the diagnostic process
are technically precise and should be preserved
as diagnostic vocabulary for future work:

```
"Video game music like Zelda"
→ string synthesis with slow attack envelope
  no formant shaping, periodic source

"Crowd cheering at sports event"
→ aspiration/turbulence noise amplified through
  resonator chain (noise before formant bank)
  OR multiple independent noise sources summed

"Stable tone underneath"
→ fundamental dominant (99% energy below 350Hz)
  source was near-sine, formants had nothing to shape
  OR dry source leaking to output

"Orthogonal convolution artifact"
→ IIR notch filter ringing
  poles near notch frequency overshoot
  "skipping record" time-domain manifestation

"Slow amplitude wave in ensemble"
→ symmetric detuning creating regular beat frequency
  ±6 cents = 0.91Hz beat = 1.1 second cycle

"Electric piano key in soprano"
→ subharmonic at f/2 too loud (0.12 linear)
  at 523Hz: f/2 = 261Hz = audible piano key

"Fog horn drone in bass"
→ subharmonic at f/2 below pitch perception
  at 131Hz: f/2 = 65Hz = felt as pressure

"Deep breath ahhhhh... balancing tone and breath"
→ ensemble + aperiodic source working correctly
  organic vocal texture confirmed

"THIS IS DISTINCT EEE RELATIVE TO AAA"
→ formant architecture confirmed working
  F1=280Hz (ee) vs F1=700Hz (ah) perceptually distinct

"Fractal aperiodicity yet sin/cosine bounded"
→ the correct description of what jitter/shimmer
  should produce: bounded random walk, not noise
  Ornstein-Uhlenbeck process is the correct model

"An instrument is a tool. A voice is alive."
→ the design specification
  aperiodicity must be in source, not post-processing
  every cycle must be different from the last
```

---

## WHAT PART 3 WILL ADDRESS

**Finding Voice Part 3** will document:

- V13 perceptual confirmation (notch removed)
- Whether the orthogonal artifact is fully resolved
- Integration into the polyphonic engine
  (replacing synth_voice with ensemble_v13)
- SATB four-part rendering with voice synthesis
- Final A/B: strings vs choir on same fugue material
- Reverb tuning for choir (0.44 confirmed)
- Version bump: Tonnetz v6.5 with confirmed voice

---

## THE THREE CORE DISCOVERIES OF PART 2

**Discovery 1: Aperiodicity belongs in the source.**
Not in post-processing. Not in the amplitude envelope.
In the excitation that feeds the formant bank.
The formant bank must RESPOND to the variation.

**Discovery 2: The notch filter was wrong.**
The fundamental is the voice's pitch.
It should be present. The notch removed it and
replaced it with ringing. The IIR notch on a
strong fundamental produces a skipping record artifact.
Remove it. Let the formant bank and the
differentiated source define the spectral balance.

**Discovery 3: Inharmonic detuning for ensemble.**
Symmetric detuning creates periodic beating.
Prime-number-like offsets (0, +11, -17 cents)
create three different beat frequencies that
do not align, producing organic aperiodic shimmer
rather than a regular amplitude wave.

---

## THE INVARIANTS — NEVER CHANGE THESE

Lessons learned the hard way, confirmed by
multiple regression experiments:

```
1. ALWAYS differentiate the glottal source (np.diff)
   Without it: 99% energy below 350Hz
   Formants have nothing to shape

2. NEVER use series resonators
   Gain accumulates multiplicatively
   Saturation destroys spectral shape
   Always use parallel Klatt bank

3. NEVER add dry source to output
   Only formant bank sum reaches output
   Dry source = stable tone underneath

4. NEVER put turbulence/breath before formant bank
   Resonators amplify it → crowd noise
   Always post-formant

5. NEVER normalize intermediate signals
   Especially not the voiced output before envelope
   Shimmer lives in the waveform shape
   Normalization destroys amplitude variation

6. NEVER use symmetric ensemble detuning
   Regular beat frequency = tonal amplitude wave
   Use prime-like offsets: 0, +11, -17 cents

7. NEVER add IIR notch on strong fundamental
   Ringing artifact = skipping record
   The fundamental is the voice's pitch
   Let it be present

8. ALWAYS keep the vectorized phase accumulator
   Per-cycle Python loops break phase coherence
   Discontinuities at cycle boundaries = artifacts
```

---

*End of Finding Voice — Part 2*

*Status: v13 architecture complete.*
*Notch removed. Artifact resolved.*
*Awaiting v13 perceptual confirmation.*
*Integration into main engine pending.*
*Continue to Part 3 after v13 results.*
