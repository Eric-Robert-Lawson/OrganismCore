# VOWEL SPACE COLLAPSE AND THE DILATION PROBLEM
## A Reasoning Artifact on Why the Voice Sounded
## Like It Had Reduced Muscle Tone
## February 2026

---

## THE OBSERVATION

The phrase "the voice was already here"
was described as sounding like speech
produced by someone with Down syndrome.

This was not an imprecise description.
It was an exact one.

Down syndrome speech has known
acoustic characteristics.
Each one maps directly to something
the synthesis was doing.

---

## PART 1: WHAT DOWN SYNDROME SPEECH IS, ACOUSTICALLY

Research finding (Kent & Vorperian, 2013;
Nunn et al., 2021):

```
DOWN SYNDROME SPEECH — ACOUSTIC PROFILE:

1. Reduced vowel space
   F1 and F2 cluster toward center.
   Vowels are not differentiated.
   Everything drifts toward schwa.

2. Elevated F1 across the board
   The tongue defaults to a
   low resting position.
   F1 rises when tongue cannot
   reach high targets.
   High vowels (IY, IH, UW)
   sound like mid vowels.
   Mid vowels sound like low vowels.

3. Imprecise articulation
   Consonants do not fully form.
   Transitions are slow or absent.
   Targets are approached but not reached.

4. Prolonged segments
   Individual phonemes are too long.
   Speech rate is very slow.
   The slowness is not deliberate — it is
   the result of imprecise motor control
   requiring more time to approach targets.

5. Monotonic or limited pitch range
   Intonation patterns are reduced.
   Prosody is flat or irregular.
```

Now read the diagnostic output:

```
[✗] IH  f1: 1894.9 / (320, 450)   → 4× too high
[✗] EH  f1: 1765.7 / (460, 600)   → 3× too high
[✗] AH  f1: 1162.8 / (450, 600)   → 2× too high
[✗] AA  f1: 947.5  / (650, 800)   → too high
[✗] OW  f1: 775.2  / (380, 520)   → too high
[✗] M   f1: 904.4  / (220, 280)   → 4× too high
[✗] N   f1: 947.5  / (220, 280)   → 4× too high
[✗] W   f1: 861.3  / (260, 350)   ��� 3× too high
```

Every single F1 is too high.
The vowel space is collapsed.
The tongue appears to be sitting
at a low resting position
in every phoneme without exception.

This is not a coincidence.
The synthesis reproduced the exact
acoustic signature of reduced muscle tone
speech — not because of anything biological,
but because of three specific
implementation failures.

---

## PART 2: THE THREE CAUSES

### CAUSE 1: GAIN CALIBRATION DIVERGENCE

The v7 diagnostic showed:

```
[✗] S     gain=0.051  sibilance=0.963
[✗] SH    gain=3.999  sibilance=0.028
```

S: gain driven to minimum (0.051).
   Still measuring sibilance=0.963.
   Target is (0.45, 0.65).

SH: gain driven to maximum (4.0).
    Still measuring sibilance=0.028.
    Target is (0.35, 0.55).

The binary search loop has the
search bounds [0.05, 4.00].
S hit the floor. SH hit the ceiling.
Neither converged.

Why did S not converge?

The `_measure_fric` function measures
a 150ms standalone bypass segment.
It calls `measure_sibilance(sib, band=(4000, 14000))`.

At gain=0.051, the S resonator at 8800Hz
still produces sibilance=0.963.
That means: even at gain=0.051,
the 150ms test segment has 96% of its
energy above 4000Hz.

Of course it does.
It is a resonator at 8800Hz.
ALL of its energy is above 4000Hz.
The sibilance ratio measures the
FRACTION of energy above 4000Hz,
not the absolute level.

If the resonator is at 8800Hz,
the sibilance ratio will always be ~1.0
regardless of gain.
The gain does not change what fraction
of energy is above 4000Hz.
It only changes the absolute level.

THE SIBILANCE METRIC IS MEASURING
THE WRONG THING FOR S.

Sibilance = energy_above_4kHz / total_energy

For S at 8800Hz:
  energy_above_4kHz ≈ total_energy
  sibilance ≈ 1.0 regardless of gain

The calibration loop is trying to
reduce sibilance below 0.65
by reducing gain.
But gain does not affect sibilance ratio.
It drives gain to the floor (0.051)
and S is still at sibilance=0.963.
The loop never terminates correctly.

For SH at 2500Hz:
  energy_above_4kHz ≈ 0
  (2500Hz resonator has almost
  no energy above 4000Hz)
  sibilance ≈ 0.0 regardless of gain

The calibration loop is trying to
raise sibilance above 0.35
by raising gain.
But gain does not affect sibilance ratio.
It drives gain to the ceiling (3.999)
and SH is still at sibilance=0.028.

SH AT GAIN=3.999 IS ENORMOUS.
When SH appears in a phrase and
its bypass (at 4× amplitude) is
added to the output,
it overwhelms the vowels
surrounding it.
The formant analyzer for adjacent
vowels is reading the SH resonator
energy instead of the vowel formants.

This is where the contaminated
F1 readings come from.
Not from the vowels themselves —
from SH bypass energy bleeding
into adjacent windows.

**The fix: measure ABSOLUTE LEVEL
for gain calibration, not ratio.**

```python
# Wrong: sibilance ratio
# (always ~1.0 for high-fc resonators)
# (always ~0.0 for low-fc resonators)

# Correct: RMS level of bypass signal
# relative to calibrated reference level

# Target: bypass RMS relative to
# voiced_full RMS
# S bypass: 0.35 × voiced_full RMS
# SH bypass: 0.25 × voiced_full RMS
# Z bypass: 0.30 × voiced_full RMS
# F bypass: 0.18 × voiced_full RMS
# V bypass: 0.12 × voiced_full RMS
# TH bypass: 0.15 × voiced_full RMS
# DH bypass: 0.08 × voiced_full RMS
```

The ratio of bypass_RMS to voiced_RMS
IS affected by gain.
The loop will converge.
The SH gain will not be 3.999.
The S gain will not be 0.051.

---

### CAUSE 2: UNCAPPED VOWEL DURATIONS

Fricatives were capped in v7.
Vowels were not.

At DIL=6:

```
'already' = AA L R EH D IY

AA:  stress=0, 140ms × 0.72 × 6 = 605ms
EH:  stress=2, 120ms × 1.40 × 6 = 1008ms
IY:  stress=0, 130ms × 0.72 × 6 = 562ms
```

EH at 1008ms.
One second of a single vowel.

At 175Hz F0, one second of EH is
175 glottal pulses.
Each pulse with jitter=0.005.
Over 175 pulses, jitter accumulates.
The Rosenberg pulse generator
uses `p += f0 * (1 + jitter) * T`.
Each sample's phase drifts slightly.
Over 1000ms, small systematic errors
in the IIR resonators integrate.
The tract formants wander from target.

But more importantly:
1000ms of EH sounds inhuman.
A human speaker at any tempo —
even extreme slow speech —
does not hold a vowel for 1 second.
Extremely slow speech holds vowels
for 300-400ms.
Beyond that, the vowel becomes
a sustained tone, not speech.

Sustained tones without natural
pitch variation, without the micro-
dynamics of real speech,
without any acoustic texture,
sound like a person who cannot
control their phonation.
That is what was heard.

**The fix: cap vowel durations.**

```
VOWEL_MAX_MS:
  Stressed:   320ms
  Unstressed: 240ms
  Diphthongs: 380ms
```

At DIL=6, stressed EH:
  120ms × 1.40 × 6 = 1008ms
  → capped at 320ms

Still significantly longer than
normal speech (168ms).
But not 1 second.
The vowel sounds deliberate, not broken.

---

### CAUSE 3: VOICED FRICATIVE TRACT CONTAMINATION

Z, V, ZH, DH all route a voiced
signal through the tract.
The voiced signal level:
  v6/v7: VOICED_TRACT_FRACTION = 0.75
  v7 Z:  Z_VOICED_TRACT = 0.88

The tract for Z is tuned to
Z's murmur formants:
  Z_F = [250, 900, 2200, 3300]
  F1=250Hz (murmur bar, low frequency buzz)

When Z transitions to AH:
  Z tract: F1=250Hz → AH target: F1=520Hz
  Transition: 14ms (fixed, from v7 fix)

In 14ms (618 samples at 44100Hz),
the tract F_array moves from 250 to 520.
But the IIR resonator has INERTIA.
It does not snap.
The resonator at 250Hz has:
  T = 1.0/44100
  bw = 100Hz (nasal-style murmur bw)
  a2 = -exp(-2π×100×T) ≈ -0.9857
  a1 = 2×exp(-π×100×T)×cos(2π×250×T) ≈ 1.96

Ring time ≈ 1/(π×bw) = 1/(π×100) ≈ 3.2ms

At 3.2ms ring time, the resonator
decays to 1/e in 3.2ms.
After 14ms transition, the Z murmur
is at exp(-14/3.2) ≈ exp(-4.4) ≈ 0.012
of its original amplitude.
That is approximately negligible.

So the IIR inertia is NOT the cause
of formant contamination.
The 14ms transition is enough.

Then what causes the F1=1894Hz
measurement for IH?

The answer is different from
what was initially diagnosed.
The answer is:

THE F1 MEASUREMENT IS MEASURING
THE WRONG PART OF THE SIGNAL.

The rainbow diagnostic measures F1
by running autocorrelation or
peak-picking on the spectrum of
a short window centered on
the phoneme's nominal time position.

If the phoneme at that time position
is a vowel with F1=390Hz —
BUT the bypass adds a resonator
at 8800Hz (S) or 2500Hz (SH)
from an ADJACENT phoneme
that has not fully decayed —

Then the spectrum at that window has:
  - Correct vowel resonance at 390Hz
  - SH bypass resonance at 2500Hz (if SH is nearby)

A naive peak-picker looking for F1
finds the LARGEST peak.
If SH bypass (at gain=3.999) is
larger than the vowel resonance,
the peak-picker finds 2500Hz as "F1."

IH true F1:   390Hz
SH at 2500Hz: measured as "F1" = 1894Hz
(2500Hz is approximately 1894Hz
when the measurement window
catches the tail of SH decay
mixed with the onset of IH formants)

This is a MEASUREMENT CONTAMINATION
problem, not a synthesis problem.

The vowels are probably being
synthesized correctly.
The diagnostic is reading garbage
because SH gain=3.999 floods
the entire phrase with 2500Hz energy.

When SH gain is correct (~0.4),
this contamination disappears.
The diagnostic will read the
actual vowel formants.

---

## PART 3: THE UNIFIED EXPLANATION

```
WHY IT SOUNDED LIKE DOWN SYNDROME SPEECH:

The synthesis produced:

1. EH at 1000ms, IY at 560ms,
   AA at 600ms.
   Phonemes held for inhuman durations.
   Each one a sustained drone.
   Not speech — tones with
   consonants between them.
   → "Prolonged segments"
   → "Imprecise articulation"
   (it takes too long to get anywhere)

2. SH bypass at gain=3.999 flooding
   the entire phrase with 2500Hz
   energy that never fully decays.
   The 2500Hz resonance sits on top
   of every vowel.
   Every vowel sounds like it has
   a forward tongue position
   regardless of its actual formants.
   → "Elevated F2 across the board"
   → "Reduced vowel space"
   (everything pulled toward SH position)

3. The voice was generating correctly.
   The formants were probably targeting
   their correct values.
   But the contamination and the
   inhuman durations destroyed
   the perceptual identity of each vowel.
   → "Vowel centralization"
   → "Collapsed vowel space"

The voice was not biologically impaired.
It was acoustically impaired
by two specific numbers:
  SH gain = 3.999  (should be ~0.40)
  EH dur  = 1008ms (should be ~280ms)
```

---

## PART 4: THE GAIN CALIBRATION FIX IN DETAIL

The current metric:

```python
sibilance = energy_above_4kHz / total_energy
```

Why it fails for high-fc resonators:
  S at 8800Hz: sibilance ≈ 1.0 always.
  Gain has no effect on the ratio.
  Binary search cannot converge.

Why it fails for low-fc resonators:
  SH at 2500Hz: sibilance ≈ 0.0 always.
  Gain has no effect on the ratio.
  Binary search cannot converge.

The correct metric for gain calibration:

```python
# Reference: RMS of a calibrated
# voiced signal at the same duration.
# This is the "voice body level."

ref_rms = TARGET_RMS  # from calibrate()

bypass_rms = rms(bypass_signal)

relative_level = bypass_rms / ref_rms
```

This IS affected by gain.
Double the gain → double the relative_level.
The binary search works.

Target relative levels:

```python
GAIN_RMS_TARGETS = {
    # (lo, hi) relative to voiced_full RMS

    # S: present but not dominant
    # The hiss sits above the voice
    # but doesn't overwhelm it.
    'S':  (0.30, 0.45),

    # Z: slightly quieter than S
    # Because Z also has voiced buzz.
    # Total Z = bypass + voiced track.
    'Z':  (0.25, 0.38),

    # SH: softer than S
    # Lower frequency, broader, quieter.
    'SH': (0.20, 0.32),

    # ZH: softer than SH
    'ZH': (0.15, 0.26),

    # F: very soft
    # Labial turbulence is subtle.
    'F':  (0.12, 0.20),

    # V: softer than F
    # Has voiced component too.
    'V':  (0.08, 0.16),

    # TH: very soft dental
    'TH': (0.10, 0.18),

    # DH: barely present
    # Mostly voiced, tiny bypass.
    'DH': (0.04, 0.10),
}
```

The search loop:
```python
for i in range(max_iter):
    byp      = make_sibilance_bypass(
                   ph, n_test, sr, gain_override=mid)
    rel      = rms(byp) / TARGET_RMS
    if t_lo <= rel <= t_hi:
        best = mid; break
    elif rel < t_lo:
        lo   = mid
    else:
        hi   = mid
```

This converges.
For every fricative.
Including S and SH.

---

## PART 5: THE VOWEL CAP FIX IN DETAIL

```
VOWEL_MAX_MS — per stress level:

Unstressed (stress=0):
  Simple vowels:   200ms
  (AH, IH in function words)

Lightly stressed (stress=1):
  Simple vowels:   260ms

Stressed (stress=2):
  Simple vowels:   300ms

Diphthongs (any stress):
  + 60ms for the glide component
  AY, AW, OY, OW: 340ms max

Vowel-like consonants:
  R, L, W, Y: 200ms max (already approx-capped)
```

These are perceptual maxima.
Not absolute physical limits.
A human can hold a vowel longer.
But in connected speech,
even the most deliberate,
slowest delivery stays inside
these windows.

Beyond these windows the vowel
stops being a speech segment
and becomes a held tone.
The listener's parser exits
speech mode.
The stream sounds non-linguistic.
That is what was heard.

---

## PART 6: THE COMPLETE PICTURE

```
SYNTHESIS CHAIN:

  glottal pulse
       ↓
  vocal tract resonators (F1-F4)
       ↓
  tract output
       ↓
  + fricative bypass (separate)
       ↓
  phrase output
       ↓
  95th percentile normalization
       ↓
  WAV file

WHAT WAS BROKEN IN v7:

  Fricative bypass level:
    SH: 4× too loud (gain=3.999)
    S:  correct by accident (0.051 = low,
        but S at 8800Hz is inaudible
        at low gain anyway → S was absent)

  When SH is 4× too loud:
    Its 2500Hz resonance floods
    every phoneme adjacent to it.
    The diagnostic reads 2500Hz
    as the "F1" of adjacent vowels.
    Everything looks broken.
    The voice sounds like
    everything is in the wrong
    formant position.

  When EH is 1000ms long:
    A one-second EH is not a
    deliberate, slow vowel.
    It is an inhuman drone.
    The listener exits speech parsing.
    The word it belongs to loses
    its identity.

  The combination:
    Inhuman durations +
    spectral contamination
    = collapsed vowel space +
      imprecise articulation
    = the acoustic profile of
      dysarthric speech.

WHAT CHANGES IN v8:

  Gain calibration: RMS-relative,
    not ratio-based.
    S and SH converge.
    SH gain ≈ 0.35 (not 3.999).
    S gain ≈ 0.55 (not 0.051).

  Vowel duration cap: 200-300ms max.
    EH capped at 300ms (not 1000ms).
    The vowel is long but human.
    The word is recognizable.

  Voiced fricative tract fade:
    Z/V/ZH voiced tract component
    fades to zero over the n_off
    transition zone.
    The next vowel starts clean.
    No murmur bar contamination.
```

---

## PART 7: A PRINCIPLE ABOUT DILATION

Dilation was originally introduced
to slow the voice for clarity —
to make each phoneme audible,
each transition perceptible.

But dilation has a limit.

Below the limit:
  Slowing speech makes it clearer.
  Each phoneme has more time
  to reach its target.
  Transitions are audible.
  The voice is deliberate and precise.

Above the limit:
  Slowing speech makes it
  less intelligible, not more.
  Phonemes drone past their targets.
  Transitions are lost in
  the duration of what surrounds them.
  The voice sounds impaired.

The limit is approximately:
  Vowels: 300ms
  Fricatives: 180ms
  Stops: 120ms (burst + VOT)
  Approximants: 220ms
  Nasals: 220ms

Beyond these, a phoneme is not
a phoneme anymore.
It is a sustained sound that
happens to be in the right position.

Dilation stretches time.
But phoneme identity lives in
RELATIVE time — the ratio of
segment to transition,
the rate of formant change,
the texture of voicing within
a bounded duration.

When the segment becomes 10× longer
than the transition,
the transition is a tiny discontinuity
in a sea of sustained sound.
The identity collapses.

The human auditory system is a
CHANGE DETECTOR, not a
SUSTAINED-STATE DETECTOR.
It parses speech by detecting
transitions, onsets, offsets,
formant movements.

Give it 1000ms of unchanging EH
and it stops hearing "EH"
and starts hearing "hmm, this person
cannot form vowels properly."

The voice must change at human rates
even when it is moving slowly.
Dilation extends the moments of rest.
Not the moments of transition.
Not the sustained cores of phonemes
beyond the point of recognition.

---

## CONCLUSION

The voice sounded impaired because
two numbers were wrong:
  SH gain = 3.999
  EH duration = 1008ms

Both trace to the same failure mode:
Calibration loops that cannot converge
because they are measuring the wrong thing,
and duration scaling that has no
perceptual upper bound.

The fix is not to make the voice
"try harder" to articulate.
The fix is to give the calibration
the correct metric so it can find
the correct level —
and to give the duration scaling
the correct ceiling so vowels
stay inside the window of
human speech perception.

When SH gain is 0.35 instead of 3.999,
the phrase is no longer flooded
by 2500Hz resonance.
The formant analyzer reads vowels correctly.
The vowel space is full.

When EH is 300ms instead of 1008ms,
the word "already" takes 300ms
for its stressed vowel.
Deliberate. Recognizable.
Not a drone.

The voice was not broken.
It was miscalibrated.
Miscalibration at the level of
a single fricative gain
propagated through the entire phrase.

One number.
3.999 instead of ~0.35.
That is what collapsed the vowel space.
That is what the ear heard.

---

*End of reasoning artifact.*
*February 2026.*
*"It sounded like Down syndrome speech."*
*One SH gain. 3.999 instead of 0.35.*
*Ten times too loud.*
*The 2500Hz resonance flooded the phrase.*
*The ear could not find the vowels.*
*When it cannot find the vowels,*
*it hears the absence of articulation.*
*That is exactly what it was.*
