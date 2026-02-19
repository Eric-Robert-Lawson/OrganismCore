# FINDING VOICE — PART 1
## Reasoning Artifact: Vocal Synthesis Discovery Log
## Tonnetz Polyphonic Engine — Voice Instrument
## February 2026

---

## WHAT THIS DOCUMENT IS

This is a diagnostic reasoning artifact. It documents
the complete process of discovering how to synthesize
a convincing human voice from first principles —
every failed attempt, every diagnosis, every fix,
and the perceptual evidence that drove each decision.

It is written for any instance that needs to build
or understand voice synthesis. The diagnostic process
IS the knowledge. The failures are as important as
the successes.

**Status at time of writing:** Voice synthesis
architecture is solved and confirmed working.
Biological realism (jitter, shimmer, ensemble)
is in active diagnostic testing (v9).

---

## THE STARTING POINT — WHAT WAS ASSUMED

The original reasoning artifact described voice
synthesis as follows:

```
synth_voice:
  - Harmonic series with steep rolloff (1/n^2)
  - Formant bandpass filters (F1=800Hz, F2=1200Hz)
  - AM vibrato at 4.8Hz
  - Breath noise filtered to voice range
  - Slow attack envelope (280-400ms)
```

**This was wrong. All of it.**

The harmonic series with steep rolloff is structurally
identical to string synthesis. The formant bandpass
filters were shaping near-silence. The AM vibrato
produced tremolo not pitch modulation. The result
was string ensemble, not voice.

The perceptual report that triggered the full
diagnostic investigation:

> "I describe it as video game music like Zelda,
>  if that makes sense. I hear 4 string ensemble
>  instruments. The instruments are not vocal,
>  it is 100% certain a string instrument."

---

## THE DIAGNOSTIC CHAIN

### V1 — Isolated Single Note Test

**Hypothesis:** The formant filter is not working
because it is shaping a signal that already sounds
like strings.

**Test:** Render isolated single notes through
each synthesis stage separately.

**Result:**
- File 3 (formants, no envelope): still buzz like file 1
- Files 4/5 (full voice): "crowd cheering at sports event"

**Diagnosis:** Series formant resonators were
saturating. Each resonator amplified the signal,
and the next resonator amplified the result.
Four resonators in series = enormous gain at
each formant frequency = clipping = spectral
destruction.

**Key learning:** Series resonators accumulate
gain multiplicatively. They cannot be used for
parallel formant synthesis without normalization
that destroys the spectral shape.

---

### V2 — Parallel Formant Bank (Klatt 1980)

**Fix:** Switch from series to parallel resonators.
Each resonator receives the same dry excitation.
Outputs summed at controlled individual gains.

**Architecture (Klatt 1980):**
```
excitation → F1 × G1 ─┐
           → F2 × G2 ─┤→ sum → output
           → F3 × G3 ─┤
           → F4 × G4 ─┘
```

**Result:**
> "I hear resonance of string in background,
>  like a stable tone + the vocals. I hear
>  distinct oooo and aaaa but I also hear a
>  stable tone."

**Diagnosis:** The dry excitation signal was
being added to the formant bank output directly.
The formant shaping was working (vowels audible)
but the raw source was leaking through.

**Key learning:** In the Klatt model, the output
is ONLY the formant bank sum. The excitation
never reaches the output directly.

---

### V3 — Remove Dry Source from Output

**Fix:** Output = formant bank sum only.
No dry signal. No body. Nothing but resonators.

**Also:** Highpass at 180Hz to remove
fundamental bleed from F1 resonator output.

**Result:**
> "Still distinct sounds — stable tone remains"

**Diagnosis:** The formant resonator itself was
sustaining at its natural frequency. The biquad
IIR filter has poles near the unit circle. When
excited, it rings at its resonant frequency.
If the ringing time exceeds the inter-pulse gap,
the resonator sustains independently of the input.

**Ringing time formula:**
```
RT60 = 6.9 / (π × bandwidth)  seconds
```

At bw=130Hz: RT60 = 16.9ms
Inter-pulse gap at 261Hz: 3.82ms
Ratio: 4.4× — resonator rings 4× longer than gap.
Result: two separate sounds (ringing + source).

**Key learning:** Synthesis bandwidth must be
much wider than measured acoustic bandwidth.
The digital filter has no physical wall damping.

---

### V4 — Widen Formant Bandwidths

**Fix:** Increase bandwidths from 60-250Hz
to 300-600Hz. This reduces ringing time so
it decays within one inter-pulse gap.

```
bw=400Hz: RT60 = 5.49ms
Inter-pulse at 261Hz: 3.82ms
Ratio: 1.44× — still slightly over
```

**Result:** Still separate tones.

**Diagnosis:** Even at 400Hz bandwidth, the
ringing ratio exceeded 1.0 for all formants.
The problem was not just bandwidth — it was
the source spectrum itself.

---

### V5 — Spectral Logging Added

**Decision:** Stop guessing. Add frequency-domain
logging at every stage of the synthesis chain.
Measure what is actually happening.

**This was the turning point.**

---

### V6 — THE ROOT CAUSE REVEALED

**Log output (critical section):**

```
STAGE 1: Glottal source
  Energy below 350Hz: 99.3%
  Energy above 350Hz: 0.7%

STAGE 3: F1 (700Hz, bw=400Hz):
  Energy at F1 (700±200Hz): 1.5%
  Energy at fundamental (262±20Hz): 15.0%

STAGE 5: After highpass (350Hz cutoff)
  Fundamental suppression: -415.0%
  ← NEGATIVE. Highpass made it WORSE.

DOMINANT FREQUENCY: 261.3Hz
*** PROBLEM: fundamental (262Hz) is dominant ***
```

**The diagnosis is definitive:**

The glottal source had 99.3% of its energy
below 350Hz. The formant resonator at 700Hz
received almost no energy to amplify. It
amplified the fundamental (261Hz) instead
because that is where all the energy was.

The highpass removed the tiny amount of
high-frequency content that existed, making
the fundamental proportion even larger.
Hence: -415% suppression (it got worse).

**Root cause:**
The Rosenberg pulse WITHOUT differentiation
is essentially a sine wave at the fundamental.
A sine wave has no harmonics for formants
to shape. The formant bank had nothing to work with.

**Key learning:**
The glottal source MUST be differentiated before
passing to the formant bank. The first-difference
operator (+6dB/oct) flattens the steep -12dB/oct
rolloff of the Rosenberg pulse, distributing energy
across all harmonics.

---

### V7 — Differentiated Source

**Fix:** Apply `np.diff()` to the glottal pulse.

```python
source = np.diff(source, prepend=source[0])
```

**Log after fix:**
```
pre-diff:    <350Hz=99%  350-1kHz=1%   (broken)
post-diff:   <350Hz=72%  350-1kHz=15%  1-3kHz=10%
post-preemp: <350Hz=8%   350-1kHz=4%   1-3kHz=15%
formant_out: <350Hz=47%  350-1kHz=39%  1-3kHz=13%
```

**Result:**
> "Not a stable tone but a wave. More closely
>  vocal, but still tonal in nature. Starting
>  to blend the lines."

**Diagnosis:** Progress. Formant shaping is
now perceptible. But the fundamental at 261Hz
is still 47% of the energy. The "wave" is
vibrato on the fundamental — the fundamental
is still dominant.

**Key learning:**
Differentiation is necessary but not sufficient.
The fundamental must be removed from the output
after formant shaping.

---

### V8 — Notch Filter at Fundamental

**Fix:** Apply notch filter at the fundamental
frequency AND its first harmonics.

```python
def apply_notch_harmonics(signal, freq, sr,
                           n_harmonics=3, Q=8.0):
    for n in range(1, n_harmonics+1):
        f_n = freq * n
        b, a = iirnotch(f_n/(sr/2), Q/sqrt(n))
        signal = lfilter(b, a, signal)
    return signal
```

**Also:** Triple formant gains:
```
Before: [2.0, 1.2, 0.6, 0.2]
After:  [6.0, 4.0, 2.0, 0.8]
```

**Result:**
> "Definitive correct direction! Crystallizing
>  in correct direction. These are monotonic
>  and lack dimension but as a vocal this is
>  like a snapshot in time. bass_ah = goat
>  bahhing in monotonic tonal manner. Not a
>  string, very distinct, can tell it is vocal
>  in quality, but lacking dimension and depth."

**This is the confirmation that the architecture
is correct. Voice identity is present.**

**Diagnosis of remaining problems:**
- "Robotic / monotonic" = no jitter or shimmer
- "Lacking dimension" = single voice, no ensemble
- "Goat bahhing" = open quotient too regular,
   pulse shape too mechanical

---

### V9 — Biological Realism (IN PROGRESS)

**Status:** Diagnostic running. Results pending.

**Fixes being tested:**

**1. Jitter (cycle-to-cycle pitch variation)**
```
Real voice: 0.2-0.8% per cycle
Robot:      0.0% — perfectly periodic
```
Implementation: per-cycle frequency multiplier
drawn from N(1.0, 0.006).

**2. Shimmer (cycle-to-cycle amplitude variation)**
```
Real voice: 1-3% per cycle
Robot:      0.0% — perfectly constant
```
Implementation: per-cycle amplitude multiplier
drawn from N(1.0, 0.025).

**3. Open Quotient Variation**
```
Real voice: OQ varies ±0.05 around mean
Robot:      fixed at 0.65 forever
```
Implementation: per-cycle OQ from N(0.65, 0.035).

**4. Formant Drift (F1/F2)**
```
Real voice: ±40Hz drift over sustained note
Robot:      fixed at exact target frequencies
```
Implementation: Ornstein-Uhlenbeck process.
```python
def ou_process(n, target, sigma, tau, sr):
    dt    = 1.0/sr
    alpha = dt/tau
    vals  = [target]
    noise = normal(0, sigma*sqrt(dt), n)
    for i in range(1, n):
        vals.append(vals[-1] +
                    alpha*(target-vals[-1]) +
                    noise[i])
    return array(vals)
```

**5. Ensemble (3 singers)**
```
Each singer has:
  ±8 cents pitch offset
  ±20Hz formant offset
  ±0.15Hz vibrato rate offset
  ±12ms onset offset
```
Single voice = robotic.
Three voices summed = choir thickness.

---

## WHAT HAS BEEN PROVEN

### Architectural truths (confirmed by logs + ears):

**1. The source must be differentiated.**
   Without np.diff(), 99% of energy is below 350Hz.
   Formant filters have nothing to shape.
   This is the single most important finding.

**2. Parallel resonators, never series.**
   Series resonators accumulate gain and saturate.
   Klatt (1980) parallel bank is the correct model.

**3. Synthesis bandwidth ≠ measured bandwidth.**
   Acoustic measurement: 60-250Hz per formant.
   Synthesis requirement: 300-600Hz per formant.
   Wider bandwidth = faster decay = fused sound.

**4. Notch the fundamental after formant shaping.**
   The differentiated source still has a strong
   fundamental that dominates the output.
   Surgical notch at f0 + first 2 harmonics
   removes the tonal quality without destroying
   the formant bands above.

**5. Dry source never reaches output.**
   Only the formant bank sum is the output.
   Any dry signal in the output path creates
   a "stable background tone" that competes
   with the vowel resonances.

**6. Highpass is the wrong tool for fundamental removal.**
   A 2nd-order highpass at 350Hz has -12dB/oct slope.
   At 261Hz, it attenuates by only ~12dB.
   The fundamental survives and dominates.
   A notch filter provides -40dB at exactly f0.
   Surgical removal > broad filtering.

---

## WHAT MAKES A VOICE SOUND ROBOTIC

In order of perceptual impact:

```
1. No jitter          → sounds mechanical, too perfect
2. No shimmer         → sounds synthesized immediately
3. Fixed formants     → static vowel, no organic movement
4. Single voice       → thin, no ensemble dimension
5. Fixed OQ           → pulse too regular, goat quality
6. Steady vibrato     → more tremolo than vibrato
7. Wrong source       → string-like before formants
```

All seven were present in versions 1-8.
Version 9 addresses 1-4 and 5.

---

## FORMANT REFERENCE TABLE

For future synthesis — confirmed synthesis values
(NOT acoustic measurement values):

```
Vowel  F1    F2    F3    F4    G1   G2   G3   G4
'ah'   700   1220  2600  3200  6.0  4.0  2.0  0.8
'ee'   280   2250  3000  3500  4.0  6.0  2.5  0.9
'oo'   300    870  2250  3000  5.0  4.5  1.5  0.5
'oh'   500   1000  2500  3200  5.5  3.5  1.8  0.6

Bandwidth (synthesis):
  F1: 300-400Hz
  F2: 300-400Hz
  F3: 400-500Hz
  F4: 500-600Hz

Note: These bandwidths are 3-5× wider than
acoustic measurement values. This is correct
for digital synthesis without physical damping.
```

---

## THE GLOTTAL SOURCE PIPELINE

Confirmed correct signal flow:

```
1. Phase accumulator with FM vibrato
   phase_norm = cumsum(freq_arr/sr) % 1.0

2. Rosenberg-C pulse shape
   open:  parabolic rise over oq fraction
   close: linear fall over (1-oq) fraction
   Per-cycle jitter on freq_arr
   Per-cycle shimmer on amplitude
   Per-cycle variation of oq

3. np.diff()  ← CRITICAL
   Flattens spectrum from -12dB/oct to -6dB/oct
   Distributes energy across harmonics
   Without this: 99% energy below 350Hz
   With this:    72% below 350Hz, 28% above

4. Normalize

5. Mix with aspiration noise (upper band only)
   1000-6000Hz, amplitude ~3% of voiced source

6. Feed to parallel formant bank
   Each resonator receives same excitation
   Sum outputs at calibrated gains

7. Notch fundamental + first 2 harmonics
   Q=8.0, applied after formant bank
   Removes tonal dominance of f0

8. Normalize + envelope
   Attack: 250-330ms (slow — fold closure)
   Release: 280-350ms
   Onset shimmer: 11Hz AM during attack only
```

---

## INTEGRATION PLAN (POST-DIAGNOSTICS)

Once v9 confirms biological realism is sufficient:

1. Replace `synth_voice` in main engine with
   `klatt_voice_ensemble` (3 singers)

2. Pass `vowel='ah'` for all sustained choir notes
   (open vowel — best for ensemble texture)

3. Increase reverb_wet for choir render:
   0.25 (strings) → 0.44 (choir)
   Choir needs room to blend ensemble voices

4. The four polyphonic voices (soprano, alto,
   tenor, bass) each call klatt_voice_ensemble
   with their register frequency.
   The ensemble within each voice (3 singers)
   provides thickness within each part.
   The four parts together provide full SATB texture.

---

## WHAT PART 2 WILL ADDRESS

**Finding Voice Part 2** will document:

- V9 diagnostic results and perceptual report
- Whether jitter + shimmer + ensemble achieved
  organic vocal quality
- Vowel transition synthesis (ah → ee over note)
- Consonant onset modeling (aspirated attacks)
- The full integration into the polyphonic engine
- A/B comparison: strings vs choir on same material
- Final counterpoint + voice approval

---

## THE CORE INSIGHT

The failure of every approach before v7 had
the same root cause:

**We were trying to make strings sound like voice
by adding voice characteristics on top.**

Slow attack + formant filter = still strings.
Slow attack + formant filter + vibrato = still strings.
Slow attack + formant filter + vibrato + breath = still strings.

The correct approach is opposite:

**Start from the mechanism that makes voice voice —
the glottal pulse train — and shape it with
the mechanism that gives voice its vowel identity —
the vocal tract resonance.**

The glottal pulse is not a sine wave with rolloff.
It is a sharp asymmetric pulse that, when differentiated,
has energy at all harmonics.

The vocal tract is not a set of bandpass filters.
It is a set of resonators that amplify specific
frequency bands of a spectrally rich source.

The formants do not create the vowel.
They reveal it from what is already present
in the source.

This is the correct model.
Build from here.

---

*End of Finding Voice — Part 1*

*Architecture confirmed. Biological realism in progress.*
*Continue to Part 2 after v9 diagnostic results.*
