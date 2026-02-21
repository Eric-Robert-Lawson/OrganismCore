# SLOWING DOWN FOR DIAGNOSTICS
## A Reasoning Artifact on Why DIL Does Not Work
## and How OLA Time-Stretch Does
## February 2026

---

## THE PROBLEM

When an artifact is present in synthesized
speech and you need to locate it precisely,
the natural instinct is to slow the audio down.

The first attempt was:

```python
SLOW_DIL = DIL * 4
sig = synth_phrase(words, dil=SLOW_DIL)
```

This produced output that was the same
length or shorter than normal.
Not slower.

---

## WHY DIL DOES NOT SLOW DOWN OUTPUT

DIL is a duration scaling factor.
It multiplies the base duration of each phoneme:

```
dur_ms = PHON_DUR_BASE[ph] × DUR_SCALE[stress] × DIL
```

At DIL=6 (the normal value), most phonemes
are already at or near their duration caps:

```python
VOWEL_MAX_MS     = 300
FRIC_MAX_MS      = 180
APPROX_MAX_MS    = 200
DH_MAX_MS        = 160
H_MAX_MS         = 200
REST_MAX_MS      = 240
```

At DIL=6:
  AA base = 100ms × 1.03 × 6 = 618ms → capped at 300ms
  S  base =  55ms × 1.00 × 6 = 330ms → capped at 180ms

Multiplying DIL by 4 (DIL=24):
  AA = 100ms × 1.03 × 24 = 2472ms → still capped at 300ms
  S  = 55ms  × 1.00 × 24 = 1320ms → still capped at 180ms

The caps do not move.
The output does not get longer.
DIL × N only works in the regime
where phonemes are below their caps.
At DIL=6 everything is already at the caps.

**DIL is the wrong tool for diagnostic slowdown.**

---

## THE RIGHT TOOL: OLA TIME-STRETCH

OLA = Overlap-Add.

It is a time-domain signal processing method
that makes a signal longer without changing
its pitch or spectral character.

### What it does

Takes the output signal as-is.
Chops it into short overlapping windows.
Reassembles those windows with larger gaps
between them.
The gaps are filled by the overlap
between adjacent windows.
The result is the same signal,
stretched in time.

```
INPUT:
  [window 0][window 1][window 2][window 3]
  Each hop_in apart.

OUTPUT:
  [window 0]          [window 1]          [window 2]
  Each hop_out apart.
  hop_out = hop_in × FACTOR

  The windows overlap at their edges.
  Hann weighting ensures smooth joins.
```

### What is preserved

- Pitch: unchanged. The signal content
  within each window is identical to the
  input. No resampling. No pitch shift.

- Spectral character: unchanged.
  Each window has the same spectrum
  as the corresponding part of the input.
  Formants, fricative noise, sibilance
  — all preserved.

- Artifacts: preserved and stretched.
  If a 5ms artifact exists in the input,
  it becomes a 20ms artifact in the 4×
  stretched output.
  4× longer = 4× easier to hear and locate.

### What is NOT perfectly preserved

- Phase coherence on voiced content.
  OLA does not align the phases of
  adjacent windows.
  On voiced (periodic) signals this
  produces slight phasiness or roughness.
  This is acceptable for diagnostic use.
  We are listening for artifact position
  and texture, not voice quality.

---

## THE IMPLEMENTATION

```python
def ola_stretch(sig, factor,
                win_ms=25, sr=44100):
    """
    OLA time stretch.
    factor=4.0 → 4× longer, same pitch.
    win_ms: window size in ms.
    """
    sig   = np.array(sig, dtype=np.float32)
    n_in  = len(sig)
    win_n = int(win_ms / 1000.0 * sr)
    if win_n % 2 != 0:
        win_n += 1

    hop_in  = win_n // 4       # 75% overlap
    hop_out = int(hop_in * factor)

    n_frames = max(1,
        (n_in - win_n) // hop_in + 1)
    n_out    = hop_out * (n_frames - 1) \
               + win_n

    out    = np.zeros(n_out, dtype=np.float64)
    norm   = np.zeros(n_out, dtype=np.float64)
    window = np.hanning(win_n)

    for i in range(n_frames):
        in_start  = i * hop_in
        in_end    = in_start + win_n

        if in_end > n_in:
            frame        = np.zeros(win_n)
            avail        = n_in - in_start
            if avail > 0:
                frame[:avail] = sig[
                    in_start:in_start+avail]
        else:
            frame = sig[in_start:in_end]\
                    .astype(np.float64)

        out_start = i * hop_out
        out_end   = out_start + win_n

        out[out_start:out_end]  += \
            frame * window
        norm[out_start:out_end] += \
            window

    norm = np.where(norm < 1e-8, 1.0, norm)
    out  = out / norm

    return np.array(out, dtype=np.float32)
```

### Key parameters

```
win_ms = 25ms
  Window size. Controls the time resolution
  of the stretch.
  Shorter windows = less phasiness on voiced
  content but more roughness at joins.
  Longer windows = smoother but more phasiness.
  25ms is the standard starting point.
  For diagnostic use, 20-30ms all work.

hop_in = win_n // 4
  75% overlap between input windows.
  Standard for OLA.
  More overlap = smoother output.

hop_out = hop_in × factor
  The stretched hop size.
  At factor=4: output hops are 4× the
  input hops. Signal is 4× longer.

Hann window
  Tapers each frame to zero at edges.
  Prevents clicks at window boundaries.
  The norm array accumulates the sum of
  all Hann windows and divides the output
  by it, preventing amplitude variation
  at window boundaries.
```

---

## THE CORRECT DIAGNOSTIC PATTERN

```python
# WRONG — hits duration caps immediately:
sig = synth_phrase(words, dil=DIL * 4)

# CORRECT — synthesize normal, then stretch:
sig = synth_phrase(words, dil=DIL)
sig = ola_stretch(sig, factor=4.0)
```

The correct pattern in full:

```python
def make_slow(words_phonemes,
               punctuation='.',
               pitch=PITCH,
               room=True,
               factor=4.0):
    """
    Synthesize at normal speed.
    OLA-stretch by factor.
    Apply room after stretch.
    """
    # Step 1: normal synthesis
    sig = synth_phrase(
        words_phonemes,
        punctuation=punctuation,
        pitch_base=pitch,
        dil=DIL,
        sr=SR)

    # Step 2: time-stretch
    # This is where the slowdown happens.
    # NOT in synth_phrase.
    sig = ola_stretch(
        sig,
        factor=factor,
        win_ms=25,
        sr=SR)

    # Step 3: room reverb
    # Apply after stretch so the reverb
    # tail is also stretched proportionally.
    if room:
        sig = apply_room(
            sig, rt60=1.5,
            dr=0.50, sr=SR)

    return sig
```

---

## WHY ROOM IS APPLIED AFTER STRETCH

If room reverb is applied before stretching,
the reverb tail is also stretched.
A 1.5s RT60 becomes a 6s RT60.
This is undesirable — the room becomes
unrealistically large and the artifact
may be obscured by the stretched reverb.

Apply room AFTER stretching.
The room characteristics reflect the
stretched signal in a natural space,
not a stretched version of a natural space.

---

## WHAT TO LISTEN FOR

The diagnostic slowdown is not for
listening to voice quality.
It is for locating artifacts.

When listening to a slowed diagnostic file:

```
The signal is 4× longer.
An artifact that was 5ms is now 20ms.
An artifact that was 20ms is now 80ms.

Locate the artifact by position:
  "beginning of the file" = onset of phoneme
  "middle of the file"    = body of phoneme
  "end of the file"       = offset/transition

Locate the artifact by texture:
  "high pitched tone" = resonator ringing
                        at a high frequency
  "low pitched hum"   = resonator ringing
                        at a low frequency
  "roughness/crunch"  = two spectral sources
                        beating against each other
  "click"             = amplitude discontinuity
  "brush/friction"    = noise onset too fast

Report the file name, position, and texture.
That is sufficient to identify the
root cause.
```

---

## WHEN OLA IS NOT SUFFICIENT

OLA is sufficient for locating artifacts
in the time domain.

If the artifact is very short (< 5ms)
and you cannot hear it even at 4×,
increase the factor:

```python
sig = ola_stretch(sig, factor=8.0)
```

Or reduce win_ms to improve time resolution:

```python
sig = ola_stretch(sig, factor=4.0,
                  win_ms=10)
```

Smaller win_ms = better time resolution
but more phase artifacts on voiced content.
10ms is near the lower useful limit.
Below 10ms the Hann windows are too narrow
to capture one full pitch period at 175Hz
(T0 = 5.7ms) and the output becomes
incoherent.

---

## SUMMARY

```
Diagnostic slowdown requires post-synthesis
time stretching, not synthesis parameter
adjustment.

DIL × N: does not work at normal DIL.
         Phonemes are already at duration caps.
         No slowdown occurs.

OLA × N: works correctly.
         Synthesize at normal DIL.
         Stretch the output signal.
         Pitch unchanged.
         Spectral character unchanged.
         Artifacts stretched proportionally.
         4× stretch = 4× easier to locate.
```

---

*End of reasoning artifact.*
*February 2026.*
*"The caps do not move.*
*DIL is the wrong tool.*
*Stretch the output, not the input."*
