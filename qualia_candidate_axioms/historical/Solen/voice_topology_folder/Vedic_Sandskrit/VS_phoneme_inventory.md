# VEDIC SANSKRIT PHONEME INVENTORY
## Rigveda Reconstruction — Master Reference
## February 2026

---

## WHAT THIS DOCUMENT IS

This is the master phoneme inventory for the Vedic Sanskrit (VS) reconstruction project. It documents every phoneme verified through synthesis and diagnostic testing, along with the synthesis parameters, acoustic measurements, and diagnostic thresholds used to confirm each phoneme.

**Scope:** Rigveda phonological system as reconstructed from:
- Śikṣā treatises (Pāṇinīya Śikṣā, Taittirīya Prātiśākhya)
- Comparative Indo-European phonology
- Acoustic phonetics principles
- Living Vedic recitation traditions
- VS-internal consistency (all references from verified VS phonemes)

**This is VS-isolated.** No borrowing from other language reconstruction projects. All parameters derived from physics, Śikṣā, and VS-internal measurements.

---

## ARCHITECTURE NOTE

**This document describes the current state of synthesis architecture as verified through iterative testing.**

Key architectural discoveries:
- **v6 stop burst architecture** (spike + turbulence + boundary fix) — canonical for voiceless stops
- **v7 stop burst architecture** (spike + turbulence, no boundary fix) — canonical for voiced stops
- **Antastha tap architecture** (single Gaussian amplitude dip)
- **Nasal antiresonance model** (IIR notch at ~800 Hz)
- **Retroflex F3 depression** (sublingual cavity acoustic marker)
- **Aspiration architecture** (breathy voicing + post-murmur noise burst)

**Housecleaning status (February 2026):**
- ṚTVIJAM [ʈ]: v6 verified (canonical reference) ✓
- ṚTVIJAM [ɟ]: v7 verified (voiced reference) ✓
- PUROHITAM [p][t]: v2 updated to v6 ✓
- YAJÑASYA [ɟ]: v3 NEXT (v7 update pending)

**All voiceless stops will eventually use v6 architecture. All voiced stops will eventually use v7 architecture.**

---

## METHODOLOGICAL FOUNDATION

**Principles-first synthesis:**

1. **Physics of the vocal tract** determines possible sounds
2. **Śikṣā classification** guides articulatory targets
3. **Synthesis from parameters** generates acoustic output
4. **Diagnostic measurement** confirms acoustic targets
5. **Perceptual verification** validates naturalness
6. **Iteration when needed** to converge on correct parameters

**Not spectrographic analysis of existing recordings.** Not machine learning from corpus data. Not parameter copying from other projects.

**From principles to sound.** The convergence of physics, Śikṣā, and perception validates the reconstruction.

---

## HOW TO USE THIS DOCUMENT

**For synthesis:**
- Locate phoneme in tables below
- Copy verified synthesis parameters
- Use synthesis architecture described in relevant section
- Apply coarticulation rules when phoneme appears in context

**For diagnostic:**
- Use thresholds from DIAGNOSTIC THRESHOLDS section
- Compare measurements to ranges in phoneme tables
- Cross-reference with VS-internal verified values
- Check perceptual criteria if numeric checks pass

**For new phoneme introduction:**
- Follow NEW PHONEME INTRODUCTION WORKFLOW
- Use closest verified phoneme as starting point
- Scale parameters based on Śikṣā class and physics
- Iterate until diagnostic and perceptual criteria met

---

## SYNTHESIS ARCHITECTURE

### Source

**Rosenberg pulse train for voiced phonemes:**
```python
def rosenberg_pulse(n_samples, pitch_hz, oq=0.65, sr=44100):
    period = int(sr / pitch_hz)
    pulse = np.zeros(period, dtype=float)
    t1 = int(period * oq * 0.6)
    t2 = int(period * oq)
    
    # Rising phase (open quotient)
    for i in range(t1):
        pulse[i] = 0.5 * (1.0 - np.cos(np.pi * i / t1))
    
    # Falling phase
    for i in range(t1, t2):
        pulse[i] = np.cos(np.pi * (i - t1) / (2.0 * (t2 - t1)))
    
    # Differentiate to get glottal flow derivative
    d_pulse = np.diff(pulse, prepend=pulse[0])
    
    # Repeat to fill duration
    n_reps = (n_samples // period) + 2
    repeated = np.tile(d_pulse, n_reps)
    
    return repeated[:n_samples]
```

**Open quotient (oq) = 0.65** is standard for modal voicing. Lower oq (0.50-0.60) produces pressed/tense voice. Higher oq (0.70-0.80) produces breathy voice (used for murmur in aspirated stops).

**Pitch:** 120 Hz baseline for male Vedic recitation. Modulated by pitch accent (not yet implemented).

---

### Formant filter

**Resonator bank implementation:**
```python
def apply_formants(src, freqs, bws, gains, sr=44100):
    out = np.zeros(len(src), dtype=float)
    nyq = sr / 2.0
    
    for f, bw, g in zip(freqs, bws, gains):
        if f > 0 and f < nyq:
            # Second-order resonator
            r = np.exp(-np.pi * bw / sr)
            cosf = 2.0 * np.cos(2.0 * np.pi * f / sr)
            
            # Transfer function H(z) = (1-r) / (1 - r*cosf*z^-1 + r^2*z^-2)
            a = [1.0, -r * cosf, r * r]
            b = [1.0 - r]
            
            res = lfilter(b, a, src)
            out += res * g
    
    return out
```

**Formant frequency (f):** Center frequency of resonance (Hz)
**Formant bandwidth (bw):** Width of resonance (Hz) — narrower = more peaked
**Formant gain (g):** Amplitude contribution — higher = more prominent

**Typical formant counts:**
- Vowels: 4 formants (F1-F4)
- Consonants: 3-4 formants depending on place
- Nasals: 3-4 formants + antiresonance

---

### Retroflex F3 dip model

**Mūrdhanya (retroflex) phonemes have sublingual cavity that depresses F3.**

```python
def iir_notch(sig, fc, bw=200.0, sr=44100):
    w0 = 2.0 * np.pi * fc / sr
    r = max(0.0, min(0.999, 1.0 - np.pi * bw / sr))
    
    # Notch filter transfer function
    b_n = [1.0, -2.0 * np.cos(w0), 1.0]
    a_n = [1.0, -2.0 * r * np.cos(w0), r * r]
    
    return lfilter(b_n, a_n, sig)
```

**Applied after formant synthesis for [ɻ̩], [ɭ], [ʈ], [ɖ], [ɳ].**

**Notch frequency:** 2200 Hz (sublingual cavity resonance)
**Notch bandwidth:** 300 Hz
**Effect:** F3 drops from ~2700 Hz (neutral) to ~2200-2400 Hz

**Diagnostic signature:** F3 < 2500 Hz with depression ≥ 200 Hz vs neutral 2700 Hz.

---

### Stop burst architecture — UPDATED v6

**v6 architecture (voiceless stops) — CANONICAL:**

Three-component burst model:

**1. Pre-burst noise (3ms, amplitude 0.002):**
```python
ramp_n = min(int(0.003 * sr), n_closure // 4)
if ramp_n > 0:
    closure[-ramp_n:] = np.random.randn(ramp_n) * 0.002
```
- Masks silence-to-burst boundary
- Nearly inaudible (60 dB below burst peak)
- Prevents click artifact at boundary

**2. Spike + turbulence:**
```python
# Pressure release spike (68 µs at 44.1 kHz)
spike = np.zeros(max(n_burst, 16), dtype=float)
spike[0:3] = [1.0, 0.6, 0.3]

# Formant-filtered turbulence
turbulence = np.random.randn(len(spike))
turbulence_filt = apply_formants(turbulence, BURST_F, BURST_B, BURST_G)

# Time-varying exponential mix
t_b = np.arange(len(spike)) / sr
mix_env = np.exp(-t_b * BURST_DECAY)
burst = spike * mix_env + turbulence_filt * (1.0 - mix_env) * 0.30
```
- Spike dominates t=0-2ms (pressure equalization transient)
- Turbulence dominates t>2ms (airflow through constriction)
- Exponential decay envelope
- Correct physics of stop release

**3. Onset ramp (1ms):**
```python
onset_n = min(int(0.001 * sr), len(burst) // 4)
if onset_n > 0:
    burst[:onset_n] *= np.linspace(0.0, 1.0, onset_n)
```
- Smooths leading edge
- Additional boundary smoothing

**Formant parameters vary by place:**
- **[p] oṣṭhya:** F=[600, 1300, 2100, 3000] Hz, G=[6, 16, 4, 1.5], decay=130
- **[t] dantya:** F=[1500, 3500, 5000, 6500] Hz, G=[4, 14, 6, 2], decay=170
- **[ʈ] mūrdhanya:** F=[500, 1300, 2200, 3100] Hz, G=[8, 12, 3, 1], decay=150

**Decay rate:** Higher frequency → faster decay (physics of radiation/absorption)

**Reference implementation:** [ʈ] ṚTVIJAM v6 (1194 Hz verified)

**Housecleaning status:**
- ṚTVIJAM [ʈ]: v6 verified (canonical reference) ✓
- PUROHITAM [p][t]: v2 updated to v6 ✓
- Future: all voiceless stops will use v6

---

**v7 architecture (voiced stops):**

Same spike + turbulence method, **WITHOUT boundary fix** (pre-burst noise and onset ramp not needed).

**Why no boundary fix for voiced stops:**
- Voiced closure has murmur (low-frequency voicing)
- Murmur provides smooth transition from closure to burst
- No silence-to-burst discontinuity
- No click artifact

**Components:**
```python
# Voiced closure murmur
src_closure = rosenberg_pulse(n_closure, pitch_hz)
b_lp, a_lp = butter(2, 500.0 / (sr/2.0), btype='low')
murmur = lfilter(b_lp, a_lp, src_closure) * MURMUR_GAIN

# Spike + turbulence (same as v6)
spike = np.zeros(n_burst, dtype=float)
spike[0:3] = [1.0, 0.6, 0.3]
turbulence_filt = apply_formants(turbulence, BURST_F, BURST_B, BURST_G)
mix_env = np.exp(-t_b * BURST_DECAY)
burst = spike * mix_env + turbulence_filt * (1.0 - mix_env) * 0.30

# No pre-burst noise, no onset ramp
```

**Reference implementation:** [ɟ] ṚTVIJAM v7 (3223 Hz verified)

**Housecleaning status:**
- ṚTVIJAM [ɟ]: v7 verified ✓
- YAJÑASYA [ɟ]: v3 NEXT (v7 update pending)
- Future: all voiced stops will use v7

---

**OLD v1 architecture (bandpass noise burst) — DEPRECATED:**

```python
# Bandpass-filtered white noise (incomplete physics)
noise = np.random.randn(n_burst)
b_bp, a_bp = butter(2, [lo_hz / nyq, hi_hz / nyq], btype='band')
burst = lfilter(b_bp, a_bp, noise) * GAIN
```

**Problems:**
- Models turbulence only, misses pressure release spike
- Creates click at silence-to-burst boundary (voiceless stops)
- Temporal profile sounds "soft" compared to real stops

**Status:** Superseded by v6/v7. Preserved in v1 files as reference.

---

### Aspirated stop architecture

**Voiced aspirated stops ([gʰ], [ɟʰ], [ɖʰ], [dʰ], [bʰ]):**

Three-phase architecture:

**1. Voiced closure:**
- Rosenberg pulse source through formant bank
- Duration: 25-35 ms
- Murmur gain: 0.50-0.70 (sustained low-level voicing)

**2. Burst:**
- v7 spike + turbulence (no boundary fix needed)
- Duration: 7-10 ms
- Formant-filtered by place (velar/palatal/retroflex/dental/labial)

**3. Post-burst murmur (breathy voicing):**
- Rosenberg pulse with **high open quotient** (oq=0.75-0.80)
- Produces breathy voice quality (H1-H2 > 5 dB)
- Duration: 40-60 ms
- Formant transition from burst locus to following vowel
- Envelope: exponential rise from burst level to full voice

```python
# High OQ source for breathy voicing
murmur_src = rosenberg_pulse(n_murmur, pitch_hz, oq=0.78)

# Transition formants from burst locus to vowel
f_start = BURST_LOCUS_F
f_end = VOWEL_F
for i in range(n_murmur):
    alpha = i / n_murmur
    f_interp = [(1-alpha)*fs + alpha*fe for fs, fe in zip(f_start, f_end)]
    # Apply formants at each time step

# Exponential rise envelope
murmur_env = 1.0 - np.exp(-t_murmur * 80.0)
murmur = murmur * murmur_env
```

**Key insight:** Aspiration in voiced stops is breathy voicing (high OQ glottal source), NOT voiceless aspiration noise. The term "aspirated" is misleading — it's "breathy voiced" or "murmured".

**Diagnostic:** H1-H2 > 5 dB during murmur phase, voicing ratio > 0.60.

**Reference:** [dʰ] RATNADHĀTAMAM verified.

---

**Voiceless aspirated stops ([kʰ], [cʰ], [ʈʰ], [tʰ], [pʰ]):**

**NOT YET VERIFIED.** Expected architecture:

Three-phase:
1. Voiceless closure (v6 pre-burst noise)
2. v6 spike + turbulence burst
3. Post-burst aspiration noise (60-100 ms)
   - Broadband noise filtered by vocal tract
   - No voicing
   - Long VOT distinguishes from plain stops

**Diagnostic prediction:** VOT 60-100 ms (vs 15-20 ms for plain stops), voicing < 0.20 during aspiration.

---

### Nasal antiresonance model

**All nasals have antiresonance (acoustic zero) at ~800 Hz due to nasal side branch.**

```python
def iir_notch(sig, fc=800.0, bw=200.0, sr=44100):
    w0 = 2.0 * np.pi * fc / sr
    r = max(0.0, min(0.999, 1.0 - np.pi * bw / sr))
    b_n = [1.0, -2.0 * np.cos(w0), 1.0]
    a_n = [1.0, -2.0 * r * np.cos(w0), r * r]
    return lfilter(b_n, a_n, sig)

# Apply after formant synthesis
nasal_sig = apply_formants(src, F, B, G)
nasal_sig = iir_notch(nasal_sig, fc=800.0, bw=200.0)
```

**Antiresonance frequency is constant across all nasal places** — determined by nasal cavity geometry, not oral constriction place.

**Verified nasals:**
- [m] oṣṭhya: anti-ratio 0.0046 (PUROHITAM)
- [n] dantya: anti-ratio 0.0018 (AGNI)
- [ɲ] tālavya: anti-ratio 0.0014 (YAJÑASYA)

**Measurement:** Energy ratio between notch band (600-1000 Hz) and neighboring bands (200-600 Hz, 1000-1600 Hz). Ratio < 0.60 confirms nasal.

---

### Tap architecture — [ɾ]

**Single Gaussian amplitude dip:**

```python
def synth_tap(F, B, G, dur_ms=30.0, dip_depth=0.35, dip_width=0.40, pitch_hz=120.0):
    n = int(dur_ms / 1000.0 * sr)
    src = rosenberg_pulse(n, pitch_hz)
    out = apply_formants(src, F, B, G)
    
    # Single Gaussian dip at midpoint
    t = np.linspace(0, 1, n)
    center = 0.50
    width = dip_width * 0.5
    dip_env = 1.0 - dip_depth * np.exp(-((t - center) / width) ** 2)
    
    out = out * dip_env
    return out
```

**Parameters:**
- Duration: 20-40 ms (shortest phoneme in inventory)
- Dip depth: 0.30-0.40 (amplitude reduction at contact)
- Dip width: 0.35-0.45 (fraction of duration for dip)
- F2 dantya-adjacent: 1700-2200 Hz
- F3 neutral (no retroflex): 2400-3100 Hz

**Distinguishes tap [ɾ] from:**
- Trill [r]: multiple periodic dips (6+ minima in 5ms-smoothed envelope)
- Approximant [ɹ]: no dip (sustained constriction)

**Diagnostic:** Amplitude dip count 1-3 (single contact event detected as 2 minima in smoothed envelope due to rising/falling edges).

**Verified:** [ɾ] PUROHITAM (dip count 2, F2 1897 Hz, F3 2643 Hz, duration 30 ms).

---

### Approximant dip detector calibration

**Method for distinguishing sonorants:**

```python
def measure_amplitude_dip_count(seg, sr=44100):
    # Smooth envelope over ~5 ms windows
    env = np.abs(seg)
    k = max(1, int(0.005 * sr))
    kernel = np.ones(k) / k
    env_smooth = np.convolve(env, kernel, mode='same')
    
    # Find local minima
    from scipy.signal import argrelmin
    minima = argrelmin(env_smooth, order=k)[0]
    
    # Filter: only significant minima (below 65% of peak)
    threshold = np.max(env_smooth) * 0.65
    sig_minima = [m for m in minima if env_smooth[m] < threshold]
    
    return len(sig_minima)
```

**Classification:**
- **0 dips:** Approximant (sustained constriction, no contact)
- **1-3 dips:** Tap (single ballistic contact, 2 minima from dip edges)
- **4+ dips:** Trill (multiple periodic contacts)

**Calibration:**
- Smoothing window: 5 ms (220 samples at 44.1 kHz)
- Threshold: 65% of peak amplitude
- Order parameter: k samples (prevents spurious minima)

---

### Pitch accent F0 modulation

**NOT YET IMPLEMENTED.**

Vedic has three-way pitch accent (udātta/anudātta/svarita). F0 modulation will be added when accent is introduced.

Expected implementation:
- Udātta (high): +20-30 Hz from baseline
- Anudātta (low): -10-15 Hz from baseline
- Svarita (falling): high→low glide over syllable

---

### Coarticulation model

**Formant interpolation at phoneme boundaries:**

```python
def apply_coarticulation(F_current, F_prev, F_next, coart_on=0.15, coart_off=0.15):
    f_mean = list(F_current)
    
    # Onset coarticulation (influence from previous phoneme)
    if F_prev is not None:
        for k in range(min(len(F_prev), len(F_current))):
            f_mean[k] = F_prev[k] * coart_on + F_current[k] * (1.0 - coart_on)
    
    # Offset coarticulation (influence toward next phoneme)
    if F_next is not None:
        for k in range(min(len(F_next), len(F_current))):
            f_mean[k] = f_mean[k] * (1.0 - coart_off) + F_next[k] * coart_off
    
    return f_mean
```

**Coarticulation strength varies by phoneme:**
- Stops: 0.10-0.15 (moderate — locus determines burst, following vowel influences VOT)
- Vowels: 0.10-0.15 (moderate — steady-state important for identity)
- Sonorants: 0.15-0.20 (higher — continuous articulation, more blending)
- [h] glottal fricative: 0.30 (very high — acoustically transparent, takes color from neighbors)

**Lesson:** Coarticulation is essential for natural sound. Phonemes in isolation sound "citation form". Connected speech requires formant transitions.

---

### Room simulation

**Simple FIR convolution reverb:**

```python
def apply_simple_room(sig, rt60=1.5, direct_ratio=0.55, sr=44100):
    n_rev = int(rt60 * sr)
    ir = np.zeros(n_rev, dtype=float)
    
    # Direct sound
    ir[0] = 1.0
    
    # Exponential decay noise (diffuse reflections)
    decay = np.exp(-6.908 * np.arange(n_rev) / (rt60 * sr))
    noise_ir = np.random.randn(n_rev) * decay
    
    # Mix direct and reverb
    ir = direct_ratio * ir + (1.0 - direct_ratio) * noise_ir
    ir = ir / (np.max(np.abs(ir)) + 1e-12)
    
    # Convolve (truncate for efficiency)
    out = np.convolve(sig, ir[:min(n_rev, 4096)])
    out = out[:len(sig)]
    
    return out
```

**Standard parameters:**
- RT60: 1.5 seconds (temple courtyard)
- Direct ratio: 0.55 (balance between dry and wet)

**Used for "hall" versions of output files. Dry versions used for diagnostic measurement.**

---

### Time stretching

**Overlap-add (OLA) method for slow versions:**

```python
def ola_stretch(sig, factor=6.0, sr=44100):
    win_ms = 40.0
    win_n = int(win_ms / 1000.0 * sr)
    if win_n % 2 == 1:
        win_n += 1
    
    hop_in = win_n // 4
    hop_out = int(hop_in * factor)
    window = np.hanning(win_n)
    
    n_in = len(sig)
    n_frames = max(1, (n_in - win_n) // hop_in + 1)
    n_out = hop_out * n_frames + win_n
    
    out = np.zeros(n_out, dtype=float)
    norm = np.zeros(n_out, dtype=float)
    
    for i in range(n_frames):
        in_pos = i * hop_in
        out_pos = i * hop_out
        if in_pos + win_n > n_in:
            break
        
        frame = sig[in_pos:in_pos + win_n] * window
        out[out_pos:out_pos + win_n] += frame
        norm[out_pos:out_pos + win_n] += window
    
    nz = norm > 1e-8
    out[nz] /= norm[nz]
    
    # Normalize
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.75
    
    return out
```

**Standard factors:**
- 4× for initial diagnostic listening
- 6× for detailed phonetic analysis

**Window:** 40 ms Hanning (smooth spectral characteristics)
**Hop ratio:** input hop = window/4, output hop = input_hop × factor

**Preserves pitch (no formant shifting). Used for diagnostic slow versions.**

---

## DIAGNOSTIC THRESHOLDS

### Voicing

**Autocorrelation method:**

```python
def measure_voicing(seg, sr=44100):
    n = len(seg)
    core = seg[n//4 : 3*n//4]  # Central 50% to avoid edges
    core -= np.mean(core)
    
    if np.max(np.abs(core)) < 1e-8:
        return 0.0
    
    acorr = np.correlate(core, core, mode='full')
    acorr = acorr[len(acorr)//2:]  # Keep positive lags
    acorr /= (acorr[0] + 1e-12)  # Normalize
    
    # Search for peak in F0 range 80-400 Hz
    lo = int(sr / 400)
    hi = min(int(sr / 80), len(acorr) - 1)
    
    if lo >= hi:
        return 0.0
    
    return float(np.clip(np.max(acorr[lo:hi]), 0.0, 1.0))
```

**Interpretation:**
- **> 0.70:** Strongly voiced (vowels, voiced consonants in steady state)
- **0.50-0.70:** Moderately voiced (coarticulated vowels, sonorants)
- **0.35-0.50:** Weakly voiced (edge of voicing threshold)
- **< 0.35:** Voiceless (stops, [h], sibilants)

**For diagnostic:**
- Voiced phonemes: target ≥ 0.50
- Voiceless phonemes: target ≤ 0.35
- [h] special case: target ≤ 0.35 but residual voicing expected in intervocalic position

---

### VOT edge effects

**VOT measurement requires excluding burst itself:**

```python
# WRONG: includes burst in VOT measurement
vot_seg = stop_seg[n_closure + n_burst :]  # This is correct VOT region
vot_voicing = measure_voicing(vot_seg)

# But if VOT is short (15-20 ms), measurement is unstable
# Solution: use central 50% of VOT only
n_vot = len(vot_seg)
vot_core = vot_seg[n_vot//4 : 3*n_vot//4]
vot_voicing = measure_voicing(vot_core)
```

**Lesson from RATNADHĀTAMAM:** Short VOT requires core extraction to avoid edge effects from burst decay and vowel onset.

---

### Formant centroid bands

**Band selection for formant measurement:**

| Formant | Typical range | Measurement band | Notes |
|---------|---------------|------------------|-------|
| F1 | 250-900 Hz | 200-1000 Hz | Vowel height |
| F2 | 700-2500 Hz | 500-2800 Hz | Vowel frontness/backness |
| F3 | 2000-3500 Hz | 1800-3800 Hz | Retroflex marker, rhoticity |
| F4 | 3000-4500 Hz | 2800-5000 Hz | Voice quality, rarely diagnostic |

**Centroid measurement:**

```python
def measure_band_centroid(seg, lo_hz, hi_hz, sr=44100):
    spec = np.abs(np.fft.rfft(seg, n=2048)) ** 2
    freqs = np.fft.rfftfreq(2048, d=1.0/sr)
    
    mask = (freqs >= lo_hz) & (freqs <= hi_hz)
    total = np.sum(spec[mask])
    
    if total < 1e-12:
        return 0.0
    
    centroid = np.sum(freqs[mask] * spec[mask]) / total
    return float(centroid)
```

**Use central 50% of phoneme to avoid coarticulation effects (unless measuring transitions).**

**Lesson from PUROHITAM:** Band selection affects measurement. Too narrow → misses energy. Too wide → includes adjacent formants. Choose band appropriate for target formant.

---

### H1-H2 measurement

**NOT YET IMPLEMENTED in standard diagnostics.**

Expected method for aspirated stop verification:

```python
def measure_h1_h2(seg, pitch_hz, sr=44100):
    # Find fundamental and second harmonic in spectrum
    spec = np.abs(np.fft.rfft(seg, n=4096))
    freqs = np.fft.rfftfreq(4096, d=1.0/sr)
    
    # H1: energy at F0 ± 20 Hz
    h1_mask = (freqs >= pitch_hz - 20) & (freqs <= pitch_hz + 20)
    h1_energy = np.max(spec[h1_mask])
    
    # H2: energy at 2*F0 ± 20 Hz
    h2_mask = (freqs >= 2*pitch_hz - 20) & (freqs <= 2*pitch_hz + 20)
    h2_energy = np.max(spec[h2_mask])
    
    # Return difference in dB
    if h1_energy < 1e-12 or h2_energy < 1e-12:
        return 0.0
    
    h1_db = 20 * np.log10(h1_energy)
    h2_db = 20 * np.log10(h2_energy)
    
    return h1_db - h2_db
```

**Interpretation:**
- **H1-H2 > 5 dB:** Breathy voicing (aspirated stops, [ɦ] if verified)
- **H1-H2 = 0-5 dB:** Modal voicing (normal vowels, voiced consonants)
- **H1-H2 < 0 dB:** Pressed voicing (not expected in VS)

---

### Voiced stop closure

**Voiced stops have low-level murmur during closure:**

Target: voicing 0.40-0.70 during closure
Below 0.40: too quiet, sounds voiceless
Above 0.70: too loud, sounds like vowel

**Murmur is low-pass filtered voicing (F < 500 Hz) at reduced amplitude.**

---

### Voiceless stop closure

**Voiceless stops must have near-total silence during closure:**

Target: voicing ≤ 0.20 during closure
Measured voicing 0.0000 is ideal
Above 0.30: sounds partially voiced

**Exception:** Pre-burst noise (v6 architecture) adds 0.002 amplitude in final 3ms, but this is below measurement threshold.

---

### Nasal antiresonance

**Energy ratio method:**

```python
def measure_nasal_antiresonance(seg, sr=44100):
    spec = np.abs(np.fft.rfft(seg, n=2048)) ** 2
    freqs = np.fft.rfftfreq(2048, d=1.0/sr)
    
    # Notch band (expected zero)
    notch_mask = (freqs >= 600.0) & (freqs <= 1000.0)
    notch_energy = np.sum(spec[notch_mask])
    
    # Neighbor bands (reference)
    lower_mask = (freqs >= 200.0) & (freqs < 600.0)
    upper_mask = (freqs > 1000.0) & (freqs <= 1600.0)
    
    lower_energy = np.sum(spec[lower_mask])
    upper_energy = np.sum(spec[upper_mask])
    neighbor_energy = (lower_energy + upper_energy) / 2.0
    
    if neighbor_energy < 1e-12:
        return 1.0
    
    ratio = notch_energy / neighbor_energy
    return float(ratio)
```

**Interpretation:**
- **< 0.10:** Strong nasal (confirmed antiresonance)
- **0.10-0.60:** Moderate nasal (acceptable)
- **> 0.60:** Weak or absent nasal (fail)

**Verified nasals:**
- [n] dantya: 0.0018 (AGNI)
- [ɲ] tālavya: 0.0014 (YAJÑASYA)
- [m] oṣṭhya: 0.0046 (PUROHITAM)

---

### Tap criterion

**Amplitude dip count = 1-3 (single contact):**

See "Approximant dip detector calibration" above.

**Additional criteria:**
- Duration: 20-45 ms
- F2 dantya-adjacent: 1700-2200 Hz
- F3 neutral (no retroflex): 2400-3100 Hz
- Voicing throughout: > 0.35

**All four criteria must hold for antastha tap classification.**

---

### Approximant criterion

**Amplitude dip count = 0 (sustained constriction):**

Approximants have continuous articulation with no contact events.

**Additional criteria:**
- Duration: typically 40-80 ms (longer than tap)
- Voicing throughout: > 0.50
- Formant structure appropriate to place

**Verified approximants:**
- [j] tālavya: F2 ~2200 Hz (YAJÑASYA)
- [v] dantya: F2 ~1500 Hz (DEVAM)

---

### Duration

**Typical phoneme durations at dil=1.0 (diagnostic speed):**

| Class | Duration range | Examples |
|-------|----------------|----------|
| Short vowels | 45-60 ms | [a] [i] [u] |
| Long vowels | 80-120 ms | [aː] [iː] [uː] [eː] [oː] |
| Stops (total) | 45-65 ms | [p] [t] [k] [g] [d] [b] |
| — Closure | 25-35 ms | |
| — Burst | 7-12 ms | |
| — VOT | 10-20 ms | |
| Aspirated stops (total) | 85-135 ms | [pʰ] [tʰ] [kʰ] [gʰ] [dʰ] [bʰ] |
| — Murmur | 40-60 ms | |
| Nasals | 50-70 ms | [m] [n] [ɲ] |
| Tap | 20-40 ms | [ɾ] (shortest phoneme) |
| Approximants | 40-80 ms | [j] [v] |
| Fricatives | 50-80 ms | [s] [ɕ] [ʂ] [h] |
| Laterals | 50-70 ms | [l] [ɭ] |

**Performance speed (dil=2.5):** Multiply by 2.5 for natural recitation pace.

---

### Burst centroid hierarchy — UPDATED WITH ṚTVIJAM/PUROHITAM

**Five-place hierarchy COMPLETE:**

| Place | Phoneme | v1/v6 burst | v2 burst | Architecture | Source |
|-------|---------|-------------|----------|--------------|--------|
| mūrdhanya | [ʈ] | 1194 Hz | 1194 Hz | v6 verified | ṚTVIJAM |
| oṣṭhya | [p] | 1297 Hz | 1288 Hz | v6 updated | PUROHITAM v2 |
| kaṇṭhya | [g] | 2594 Hz | 2594 Hz | v1 (voiced) | ṚG/AGNI |
| tālavya | [ɟ] | 3223 Hz | 3223 Hz | v7 verified | ṚTVIJAM v7 |
| dantya | [t] | 3006 Hz | 3013 Hz | v6 updated | PUROHITAM v2 |

**Ordering:** mūrdhanya ≈ oṣṭhya << kaṇṭhya < tālavya ≈ dantya

**Low-burst region (800-1600 Hz):**
- [ʈ] mūrdhanya: 1194 Hz
- [p] oṣṭhya: 1288 Hz
- Separation: 94 Hz (within measurement variance)
- Distinguished by **F3 depression:** [ʈ] has retroflex F3 dip (424 Hz depression), [p] does not

**Physics:** Burst centroid inversely proportional to anterior cavity size.
- [p] bilabial: no anterior cavity (lips are boundary) → ~1288 Hz
- [ʈ] retroflex: no anterior cavity + sublingual cavity → ~1194 Hz
- [g] velar: small anterior cavity (lips to velum) → ~2594 Hz
- [ɟ] palatal: medium anterior cavity → ~3223 Hz
- [t] dental: minimal anterior cavity (lips to teeth) → ~3013 Hz

**Śikṣā ordering confirmed:** The ancient phoneticians classified by articulation place. The spectrograph ranks by burst frequency. Both orderings reflect the same underlying physics.

**Architecture status:**
- Voiceless stops [ʈ][p][t]: v6 canonical ✓
- Voiced stops [g][ɟ]: v1/v7 (murmur, no boundary fix)

---

### VS-internal separation

**Phonemes must be acoustically distinct from all other verified phonemes.**

Key separations:
- [ɾ] tap vs [ɻ̩] retroflex: F3 2643 Hz vs 2355 Hz (288 Hz separation) ✓
- [ɾ] tap vs [l] lateral: F2 1897 Hz vs ~1200 Hz (700 Hz separation) ✓
- [u] close back vs [oː] mid back: F1 300 Hz vs 382 Hz (82 Hz separation) ✓
- [m] oṣṭhya vs [n] dantya: F2 552 Hz vs ~900 Hz (348 Hz separation) ✓
- [ʈ] retroflex vs [p] bilabial: F3 depression 424 Hz vs 0 Hz (distinguishing feature) ✓

**Minimum separation threshold:** ~100 Hz for adjacent phonemes in same dimension. Smaller separations require secondary distinguishing feature (e.g., F3 depression for [ʈ] vs [p]).

---

## RE-VERIFICATION QUEUE

**Phonemes requiring housecleaning updates:**

| Phoneme | Word | Current version | Target version | Priority |
|---------|------|-----------------|----------------|----------|
| [ɟ] | YAJÑASYA | v1 (bandpass) | v7 (spike+turbulence) | HIGH |
| [c] | (future) | — | v6 | PENDING |
| [k] | (future) | — | v6 | PENDING |

**Policy:** When new architecture is discovered and verified (e.g., v6 for voiceless stops), previously verified phonemes using old architecture are queued for housecleaning. Original v1 parameters and measurements preserved as reference. Updated versions must maintain acoustic equivalence (burst centroids within 100 Hz) while improving perceptual quality.

**Completed housecleaning:**
- ṚTVIJAM [ʈ]: v6 verified (first implementation) ✓
- ṚTVIJAM [ɟ]: v7 verified (first implementation) ✓
- PUROHITAM [p][t]: v2 updated to v6 ✓

---

## PHONEME TABLES

### NOTATION SYSTEM

**Status codes:**
- ✓ VERIFIED: Passed all diagnostic checks, perceptually validated
- ⧗ PENDING: Synthesis exists, diagnostic not yet run
- ◯ PLANNED: Parameters estimated, not yet synthesized
- — NOT APPLICABLE: Phoneme does not exist in VS

**Architecture codes:**
- v1: Original bandpass noise burst (deprecated for stops)
- v6: Spike + turbulence + boundary fix (canonical for voiceless stops)
- v7: Spike + turbulence, no boundary fix (canonical for voiced stops)

**Sources:**
- Word name indicates first verification
- Multiple words indicate cross-verification

---

### VOWELS — SHORT

#### [a] — short open central unrounded — अ

**Status:** ✓ VERIFIED
**Architecture:** Standard formant synthesis
**Source word:** AGNI (अग्नि) — 1.1.1 word 1

| Parameter | Value | Unit |
|-----------|-------|------|
| F1 | 700 Hz | formant frequency |
| F2 | 1100 Hz | formant frequency |
| F3 | 2550 Hz | formant frequency |
| F4 | 3400 Hz | formant frequency |
| B1 | 130 Hz | formant bandwidth |
| B2 | 160 Hz | formant bandwidth |
| B3 | 220 Hz | formant bandwidth |
| B4 | 280 Hz | formant bandwidth |
| G1 | 16.0 | formant gain |
| G2 | 6.0 | formant gain |
| G3 | 1.5 | formant gain |
| G4 | 0.5 | formant gain |
| Duration | 55 ms | base duration |

**Measured values (AGNI):**
- F1 centroid: 631 Hz (target 600-750 Hz) ✓
- F2 centroid: 1106 Hz (target 900-1300 Hz) ✓
- Voicing: 0.8240 (target ≥ 0.50) ✓

**Śikṣā class:** kaṇṭhya (velar) — articulated with back of tongue near velum
**Position in vowel space:** Open central — lowest F1, mid F2

---

#### [aː] — long open central unrounded — आ

**Status:** ✓ VERIFIED
**Architecture:** Standard formant synthesis
**Source word:** HOTĀRAM (होतारम्) — 1.1.1 word 8

| Parameter | Value | Unit |
|-----------|-------|------|
| F1-F4 | Same as [a] | |
| B1-B4 | Same as [a] | |
| G1-G4 | Same as [a] | |
| Duration | 110 ms | base duration (2× short [a]) |

**Length distinction only.** Formant values identical to short [a].

**Measured values (HOTĀRAM):**
- Duration ratio [aː]/[a]: 2.0 (target 1.8-2.2) ✓
- Formants match short [a] within measurement variance ✓

---

#### [i] — short close front unrounded — इ

**Status:** ✓ VERIFIED
**Architecture:** Standard formant synthesis
**Source word:** AGNI (अग्नि) — 1.1.1 word 1

| Parameter | Value | Unit |
|-----------|-------|------|
| F1 | 280 Hz | formant frequency |
| F2 | 2200 Hz | formant frequency |
| F3 | 2900 Hz | formant frequency |
| F4 | 3400 Hz | formant frequency |
| B1 | 80 Hz | formant bandwidth |
| B2 | 130 Hz | formant bandwidth |
| B3 | 180 Hz | formant bandwidth |
| B4 | 250 Hz | formant bandwidth |
| G1 | 12.0 | formant gain |
| G2 | 8.0 | formant gain |
| G3 | 1.5 | formant gain |
| G4 | 0.5 | formant gain |
| Duration | 50 ms | base duration |

**Measured values (AGNI):**
- F1 centroid: 278 Hz (target 250-350 Hz) ✓
- F2 centroid: 2124 Hz (target 2000-2400 Hz) ✓
- Voicing: 0.7483 (target ≥ 0.50) ✓

**Śikṣā class:** tālavya (palatal) — articulated with front of tongue near hard palate
**Position in vowel space:** Close front — lowest F1, highest F2

---

#### [iː] — long close front unrounded — ई

**Status:** ✓ VERIFIED
**Architecture:** Standard formant synthesis
**Source word:** ĪḶE (ईळे) — 1.1.1 word 2

| Parameter | Value | Unit |
|-----------|-------|------|
| F1-F4 | Same as [i] | |
| B1-B4 | Same as [i] | |
| G1-G4 | Same as [i] | |
| Duration | 100 ms | base duration (2× short [i]) |

**Length distinction only.** Formant values identical to short [i].

**Measured values (ĪḶE):**
- Duration ratio [iː]/[i]: 2.0 (target 1.8-2.2) ✓
- F2 centroid: 2096 Hz (matches short [i] 2124 Hz within variance) ✓

---

#### [u] — short close back rounded — उ

**Status:** ✓ VERIFIED
**Architecture:** Standard formant synthesis
**Source word:** PUROHITAM (पुरोहितम्) — 1.1.1 word 3

| Parameter | Value | Unit |
|-----------|-------|------|
| F1 | 300 Hz | formant frequency |
| F2 | 750 Hz | formant frequency |
| F3 | 2300 Hz | formant frequency |
| F4 | 3100 Hz | formant frequency |
| B1 | 90 Hz | formant bandwidth |
| B2 | 120 Hz | formant bandwidth |
| B3 | 200 Hz | formant bandwidth |
| B4 | 260 Hz | formant bandwidth |
| G1 | 14.0 | formant gain |
| G2 | 8.0 | formant gain |
| G3 | 1.5 | formant gain |
| G4 | 0.5 | formant gain |
| Duration | 50 ms | base duration |
| Coart onset | 0.12 | fraction |
| Coart offset | 0.12 | fraction |

**Measured values (PUROHITAM):**
- F1 centroid: ~300 Hz (target 250-350 Hz) ✓
- F2 centroid: 742 Hz (target 600-950 Hz) ✓
- F2 below [ɑ] F2: 364 Hz margin (target ≥ 100 Hz) ✓
- Voicing: 0.5035 (target ≥ 0.50) ✓

**Śikṣā class:** oṣṭhya (labial) — articulated with rounded lips
**Position in vowel space:** Close back rounded — low F1, lowest F2 (back corner)

---

#### [uː] — long close back rounded — ऊ

**Status:** ◯ PLANNED
**Architecture:** Standard formant synthesis
**Source word:** (future)

| Parameter | Value | Unit |
|-----------|-------|------|
| F1-F4 | Same as [u] | |
| B1-B4 | Same as [u] | |
| G1-G4 | Same as [u] | |
| Duration | 100 ms | base duration (2× short [u]) |

**Length distinction only.** Formant values identical to short [u].

---

#### [ɻ̩] — syllabic retroflex approximant — ऋ

**Status:** ✓ VERIFIED
**Architecture:** Retroflex F3 dip model
**Source word:** ṚG (ऋग्) — proof of concept

| Parameter | Value | Unit |
|-----------|-------|------|
| F1 | 420 Hz | formant frequency |
| F2 | 1300 Hz | formant frequency |
| F3 | 2200 Hz | formant frequency (before notch) |
| F4 | 3100 Hz | formant frequency |
| B1 | 150 Hz | formant bandwidth |
| B2 | 200 Hz | formant bandwidth |
| B3 | 280 Hz | formant bandwidth |
| B4 | 300 Hz | formant bandwidth |
| G1 | 14.0 | formant gain |
| G2 | 7.0 | formant gain |
| G3 | 1.5 | formant gain |
| G4 | 0.4 | formant gain |
| Duration | 60 ms | base duration |
| F3 notch freq | 2200 Hz | retroflex marker |
| F3 notch BW | 300 Hz | notch bandwidth |

**Measured values (ṚG):**
- F3 centroid: 2355 Hz (target < 2500 Hz) ✓
- F3 depression: 345 Hz vs neutral 2700 Hz (target ≥ 200 Hz) ✓
- Voicing: 0.6215 (target ≥ 0.50) ✓

**Śikṣā class:** mūrdhanya (retroflex) — articulated with tongue tip curled back
**Physics:** Sublingual cavity creates F3 depression (acoustic signature of retroflex)

---

#### [ɻ̩ː] — long syllabic retroflex — ॠ

**Status:** ◯ PLANNED
**Architecture:** Retroflex F3 dip model
**Source word:** (future)

| Parameter | Value | Unit |
|-----------|-------|------|
| F1-F4 | Same as [ɻ̩] | |
| All other params | Same as [ɻ̩] | |
| Duration | 120 ms | base duration (2× short [ɻ̩]) |

**Length distinction only.** All other parameters identical to short [ɻ̩].

---

#### [ḷ] — syllabic lateral approximant — ऌ

**Status:** — NOT APPLICABLE
**Note:** Exists in Devanāgarī orthography but extremely rare in Vedic corpus. Not yet encountered in reconstruction.

---

### VOWELS — LONG MONOPHTHONGS

#### [eː] — long close-mid front — ए

**Status:** ✓ VERIFIED
**Architecture:** Standard formant synthesis
**Source word:** ĪḶE (ईळे) — 1.1.1 word 2

| Parameter | Value | Unit |
|-----------|-------|------|
| F1 | 380 Hz | formant frequency |
| F2 | 1900 Hz | formant frequency |
| F3 | 2600 Hz | formant frequency |
| F4 | 3300 Hz | formant frequency |
| B1 | 100 Hz | formant bandwidth |
| B2 | 150 Hz | formant bandwidth |
| B3 | 200 Hz | formant bandwidth |
| B4 | 280 Hz | formant bandwidth |
| G1 | 14.0 | formant gain |
| G2 | 8.0 | formant gain |
| G3 | 1.5 | formant gain |
| G4 | 0.5 | formant gain |
| Duration | 100 ms | base duration |

**Measured values (ĪḶE):**
- F1 centroid: 403 Hz (target 350-480 Hz) ✓
- F2 centroid: 1659 Hz (target 1500-2100 Hz) ✓
- Voicing: 0.7644 (target ≥ 0.50) ✓

**Śikṣā class:** tālavya (palatal) — articulated with front of tongue near hard palate
**Position in vowel space:** Close-mid front — mid F1, high F2
**Note:** Sanskrit [e] is always long. No short [e] exists.

---

#### [oː] — long close-mid back — ओ

**Status:** ✓ VERIFIED
**Architecture:** Standard formant synthesis
**Source word:** PUROHITAM (पुरोहितम्) — 1.1.1 word 3

| Parameter | Value | Unit |
|-----------|-------|------|
| F1 | 430 Hz | formant frequency |
| F2 | 800 Hz | formant frequency |
| F3 | 2500 Hz | formant frequency |
| F4 | 3200 Hz | formant frequency |
| B1 | 110 Hz | formant bandwidth |
| B2 | 130 Hz | formant bandwidth |
| B3 | 200 Hz | formant bandwidth |
| B4 | 270 Hz | formant bandwidth |
| G1 | 15.0 | formant gain |
| G2 | 8.0 | formant gain |
| G3 | 1.5 | formant gain |
| G4 | 0.5 | formant gain |
| Duration | 100 ms | base duration |
| Coart onset | 0.10 | fraction |
| Coart offset | 0.10 | fraction |

**Measured values (PUROHITAM):**
- F1 centroid: 382 Hz (target 350-550 Hz) ✓
- F2 centroid: 757 Hz (target 700-1050 Hz) ✓
- F1 between [u] ~300 Hz and [ɑ] 631 Hz ✓
- F2 between [u] 742 Hz and [ɑ] 1106 Hz ✓
- Voicing: 0.7546 (target ≥ 0.50) ✓

**Śikṣā class:** kaṇṭhya + oṣṭhya (compound) — velar constriction + lip rounding
**Position in vowel space:** Close-mid back rounded — mid F1, low F2 (back mirror of [eː])
**Note:** Sanskrit [o] is always long. No short [o] exists.

---

### VOWELS — DIPHTHONGS

#### [ai] — diphthong — ऐ

**Status:** ◯ PLANNED
**Architecture:** Formant interpolation [a]→[i]
**Source word:** (future)

Expected implementation:
- Start with [a] formants (700/1100/2550/3400 Hz)
- End with [i] formants (280/2200/2900/3400 Hz)
- Duration: ~120 ms total (60 ms per component)
- Smooth exponential transition in F1 and F2

---

#### [au] — diphthong — औ

**Status:** ◯ PLANNED
**Architecture:** Formant interpolation [a]→[u]
**Source word:** (future)

Expected implementation:
- Start with [a] formants (700/1100/2550/3400 Hz)
- End with [u] formants (300/750/2300/3100 Hz)
- Duration: ~120 ms total (60 ms per component)
- Smooth exponential transition in F1 and F2

---

### CONSONANTS — STOPS

### THE FIVE-ROW SYSTEM

The Śikṣā organizes stops in five rows (places of articulation) and five columns (manner: voiceless unaspirated, voiceless aspirated, voiced unaspirated, voiced aspirated, nasal).

**Five places (sthāna):**
1. **kaṇṭhya** (velar) — velum
2. **tālavya** (palatal) — hard palate
3. **mūrdhanya** (retroflex) — post-alveolar with curl
4. **dantya** (dental) — upper teeth
5. **oṣṭhya** (labial) — lips

**Five manners (prayatna):**
1. Voiceless unaspirated (aghoṣa alpaprāṇa)
2. Voiceless aspirated (aghoṣa mahāprāṇa)
3. Voiced unaspirated (ghoṣa alpaprāṇa)
4. Voiced aspirated (ghoṣa mahāprāṇa)
5. Nasal (anunāsika ghoṣa)

---

#### VELAR ROW — kaṇṭhya

##### [k] — voiceless velar stop — क

**Status:** ◯ PLANNED
**Architecture:** v6 (spike + turbulence + boundary fix)
**Source word:** (future)

Expected parameters (scaled from [g] 2594 Hz):
- Burst formants: [1000, 2600, 3800, 5000] Hz
- Burst gains: [5, 14, 6, 2]
- Burst decay: 160 Hz
- VOT: 15-20 ms

---

##### [kʰ] — voiceless velar aspirated — ख

**Status:** ◯ PLANNED
**Architecture:** v6 + aspiration noise (60-100 ms VOT)
**Source word:** (future)

---

##### [g] — voiced velar stop — ग

**Status:** ✓ VERIFIED
**Architecture:** v1 (voiced murmur, bandpass burst) — v7 update pending
**Source word:** ṚG (ऋग्) / AGNI (अग्नि) — proof of concept / 1.1.1 word 1

| Parameter | Value | Unit |
|-----------|-------|------|
| Closure duration | 30 ms | voiced closure |
| Burst duration | 10 ms | burst phase |
| VOT duration | 12 ms | voice onset time |
| Murmur gain | 0.60 | closure voicing level |
| Burst center freq | 2500 Hz | bandpass (v1) |
| Burst bandwidth | 1200 Hz | bandpass (v1) |

**Measured values (ṚG, AGNI):**
- Burst centroid: 2577-2611 Hz (mean 2594 Hz) ✓
- Closure voicing: 0.45-0.65 ✓
- Target burst range: 2000-3200 Hz ✓

**Note:** v7 update pending (spike + turbulence, no boundary fix). Will maintain burst centroid ~2594 Hz.

---

##### [gʰ] — voiced velar aspirated — घ

**Status:** ◯ PLANNED
**Architecture:** v7 + breathy voicing (OQ 0.75-0.80, 40-60 ms murmur)
**Source word:** (future)

---

##### [ŋ] — voiced velar nasal — ङ

**Status:** ◯ PLANNED
**Architecture:** Nasal with antiresonance at 800 Hz
**Source word:** (future)

Expected parameters:
- F1-F4: [250, 1200, 2400, 3200] Hz (velar nasal locus)
- Antiresonance: 800 Hz, BW 200 Hz
- Duration: 50-70 ms

---

#### PALATAL ROW — tālavya

##### [c] — voiceless palatal stop — च

**Status:** ◯ PLANNED
**Architecture:** v6 (spike + turbulence + boundary fix)
**Source word:** (future)

Expected parameters (scaled from [ɟ] 3223 Hz):
- Burst formants: [1500, 3200, 4500, 6000] Hz
- Burst gains: [4, 14, 6, 2]
- Burst decay: 165 Hz
- VOT: 15-20 ms

---

##### [cʰ] — voiceless palatal aspirated — छ

**Status:** ◯ PLANNED
**Architecture:** v6 + aspiration noise (60-100 ms VOT)
**Source word:** (future)

---

##### [ɟ] — voiced palatal stop — ज

**Status:** ✓ VERIFIED (v7 in ṚTVIJAM, v1 in YAJÑASYA — v3 update pending)
**Architecture:** v7 (spike + turbulence, no boundary fix) — ṚTVIJAM reference
**Source word:** YAJÑASYA (यज्ञस्य) v1 / ṚTVIJAM (ऋत्विजम्) v7

**v7 parameters (ṚTVIJAM — CANONICAL):**

| Parameter | Value | Unit |
|-----------|-------|------|
| Closure duration | 30 ms | voiced closure |
| Burst duration | 9 ms | burst phase |
| VOT duration | 10 ms | voice onset time |
| Murmur gain | 0.70 | closure voicing level |
| Burst formants | [500, 3200, 3800, 4200] Hz | palatal locus |
| Burst bandwidths | [300, 500, 600, 700] Hz | |
| Burst gains | [8, 12, 3, 1] | F2 dominant |
| Burst decay | 180 Hz | faster (high frequency) |
| Burst gain | 0.15 | voiced burst (quieter) |

**Measured values (ṚTVIJAM v7):**
- Burst centroid: 3223 Hz (target 2800-3800 Hz) ✓
- Architecture: spike + turbulence ✓
- No boundary fix (voiced, murmur masks transition) ✓
- Perceptually natural ✓

**Measured values (YAJÑASYA v1):**
- Burst centroid: 3223 Hz ✓
- Architecture: bandpass noise (OLD)
- v3 update pending to v7

**Note:** YAJÑASYA v3 housecleaning will update [ɟ] from v1 bandpass to v7 spike+turbulence. Burst centroid will be preserved.

---

##### [ɟʰ] — voiced palatal aspirated — झ

**Status:** ◯ PLANNED
**Architecture:** v7 + breathy voicing (OQ 0.75-0.80, 40-60 ms murmur)
**Source word:** (future)

---

##### [ɲ] — voiced palatal nasal — ञ

**Status:** ✓ VERIFIED
**Architecture:** Nasal with antiresonance at 800 Hz
**Source word:** YAJÑASYA (यज्ञस्य) — 1.1.1 word 4

| Parameter | Value | Unit |
|-----------|-------|------|
| F1 | 250 Hz | formant frequency |
| F2 | 1800 Hz | formant frequency |
| F3 | 2600 Hz | formant frequency |
| F4 | 3400 Hz | formant frequency |
| B1-B4 | 100/200/300/350 Hz | formant bandwidths |
| G1-G4 | 8/3/0.5/0.2 | formant gains |
| Duration | 65 ms | base duration |
| Antiresonance | 800 Hz, BW 200 Hz | nasal zero |

**Measured values (YAJÑASYA):**
- Antiresonance ratio: 0.0014 (target < 0.60) ✓
- F2 palatal locus: 1800 Hz region ✓
- Voicing: > 0.60 ✓

---

#### RETROFLEX ROW — mūrdhanya

##### [ʈ] — voiceless retroflex stop — ट

**Status:** ✓ VERIFIED
**Architecture:** v6 (spike + turbulence + boundary fix) — CANONICAL REFERENCE
**Source word:** ṚTVIJAM (ऋत्विजम्) — 1.1.1 word 7

| Parameter | Value | Unit |
|-----------|-------|------|
| Closure duration | 30 ms | voiceless closure |
| Burst duration | 12 ms | burst phase |
| VOT duration | 20 ms | voice onset time |
| Burst formants | [500, 1300, 2200, 3100] Hz | retroflex locus |
| Burst bandwidths | [250, 350, 450, 500] Hz | |
| Burst gains | [8, 12, 3, 1] | F2 dominant |
| Burst decay | 150 Hz | intermediate |
| Burst gain | 0.20 | |
| F3 notch freq | 2200 Hz | retroflex marker |
| F3 notch BW | 300 Hz | |
| Locus formants | [420, 1300, 2200, 3100] Hz | VOT target |

**Measured values (ṚTVIJAM v6):**
- Closure voicing: 0.0000 (target ≤ 0.20) ✓
- Burst centroid: 1194 Hz (target 800-1600 Hz, LOW-BURST REGION) ✓
- F3 depression: 424 Hz (target ≥ 200 Hz, RETROFLEX MARKER) ✓
- F3 measured: 2276 Hz (target < 2500 Hz) ✓

**Physics:** [ʈ] and [p] share LOW-BURST REGION (both ~1200 Hz). Distinguished by F3 depression: [ʈ] has sublingual cavity → F3 dip, [p] does not.

**This is the CANONICAL v6 reference implementation for all voiceless stops.**

---

##### [ʈʰ] — voiceless retroflex aspirated — ठ

**Status:** ◯ PLANNED
**Architecture:** v6 + aspiration noise (60-100 ms VOT) + F3 notch
**Source word:** (future)

---

##### [ɖ] — voiced retroflex stop — ड

**Status:** ◯ PLANNED
**Architecture:** v7 + F3 notch
**Source word:** (future)

---

##### [ɖʰ] — voiced retroflex aspirated — ढ

**Status:** ◯ PLANNED
**Architecture:** v7 + breathy voicing + F3 notch
**Source word:** (future)

---

##### [ɳ] — voiced retroflex nasal — ण

**Status:** ◯ PLANNED
**Architecture:** Nasal + antiresonance + F3 notch
**Source word:** (future)

---

#### DENTAL ROW — dantya

##### [t] — voiceless dental stop — त

**Status:** ✓ VERIFIED (v2 updated to v6)
**Architecture:** v6 (spike + turbulence + boundary fix)
**Source word:** PUROHITAM (पुरोहितम्) — 1.1.1 word 3

**v1 parameters (bandpass noise — DEPRECATED):**

| Parameter | Value | Unit |
|-----------|-------|------|
| Closure duration | 25 ms | voiceless closure |
| Burst center freq | 3500 Hz | bandpass |
| Burst bandwidth | 1500 Hz | bandpass |
| Burst duration | 7 ms | burst phase |
| VOT duration | 15 ms | voice onset time |
| Burst gain | 0.38 | |

**v1 measured:** Burst centroid 3006 Hz ✓

**v2 parameters (v6 — CURRENT):**

| Parameter | Value | Unit |
|-----------|-------|------|
| Closure duration | 25 ms | voiceless closure |
| Burst duration | 7 ms | burst phase |
| VOT duration | 15 ms | voice onset time |
| Burst formants | [1500, 3500, 5000, 6500] Hz | dental locus |
| Burst bandwidths | [400, 600, 800, 1000] Hz | |
| Burst gains | [4, 14, 6, 2] | F2 dominant |
| Burst decay | 170 Hz | fast (high frequency) |
| Burst gain | 0.20 | |
| Locus formants | [700, 1800, 2500, 3500] Hz | VOT target |

**v2 measured (PUROHITAM v2):**
- Closure voicing: 0.0000 (target ≤ 0.30) ✓
- Burst centroid: 3013 Hz (v1: 3006 Hz, diff 7 Hz) ✓
- Perceptual: clean release, no click ✓

**Architecture:** v6 three-component burst (pre-burst noise + spike + turbulence + onset ramp). Formants calibrated to match v1 spectral profile (2750-4250 Hz). Burst centroid preserved within 7 Hz.

**Śikṣā class:** dantya (dental) — tongue tip to upper teeth
**Physics:** Highest burst centroid (minimal anterior cavity)

---

##### [tʰ] — voiceless dental aspirated — थ

**Status:** ◯ PLANNED
**Architecture:** v6 + aspiration noise (60-100 ms VOT)
**Source word:** (future)

---

##### [d] — voiced dental stop — द

**Status:** ✓ VERIFIED
**Architecture:** v1 (voiced murmur, bandpass burst) — v7 update pending
**Source word:** DEVAM (देवम्) — 1.1.1 word 5

| Parameter | Value | Unit |
|-----------|-------|------|
| Closure duration | 28 ms | voiced closure |
| Burst duration | 9 ms | burst phase |
| VOT duration | 11 ms | voice onset time |
| Murmur gain | 0.65 | closure voicing level |
| Burst center freq | 3400 Hz | bandpass (v1) |
| Burst bandwidth | 1400 Hz | bandpass (v1) |

**Note:** v7 update pending (spike + turbulence, no boundary fix).

---

##### [dʰ] — voiced dental aspirated — ध

**Status:** ✓ VERIFIED
**Architecture:** v7 + breathy voicing
**Source word:** RATNADHĀTAMAM (रत्नधातमम्) — 1.1.1 word 9

| Parameter | Value | Unit |
|-----------|-------|------|
| Closure duration | 30 ms | voiced closure |
| Burst duration | 9 ms | burst phase |
| Murmur duration | 50 ms | breathy voicing phase |
| Murmur OQ | 0.78 | high (breathy) |
| H1-H2 | > 5 dB | breathy marker |

**Reference implementation for all voiced aspirated stops.**

---

##### [n] — voiced dental nasal — न

**Status:** ✓ VERIFIED
**Architecture:** Nasal with antiresonance at 800 Hz
**Source word:** AGNI (अग्नि) — 1.1.1 word 1

| Parameter | Value | Unit |
|-----------|-------|------|
| F1 | 250 Hz | formant frequency |
| F2 | 1500 Hz | formant frequency |
| F3 | 2500 Hz | formant frequency |
| F4 | 3200 Hz | formant frequency |
| B1-B4 | 100/180/250/300 Hz | formant bandwidths |
| G1-G4 | 8/3/0.5/0.2 | formant gains |
| Duration | 60 ms | base duration |
| Antiresonance | 800 Hz, BW 200 Hz | nasal zero |

**Measured values (AGNI):**
- Antiresonance ratio: 0.0018 (target < 0.60) ✓
- F2 dental locus: ~900 Hz ✓
- Voicing: > 0.60 ✓

---

#### LABIAL ROW — oṣṭhya

##### [p] — voiceless bilabial stop — प

**Status:** ✓ VERIFIED (v2 updated to v6)
**Architecture:** v6 (spike + turbulence + boundary fix)
**Source word:** PUROHITAM (पुरोहितम्) — 1.1.1 word 3

**v1 parameters (bandpass noise — DEPRECATED):**

| Parameter | Value | Unit |
|-----------|-------|------|
| Closure duration | 28 ms | voiceless closure |
| Burst center freq | 1100 Hz | bandpass |
| Burst bandwidth | 800 Hz | bandpass |
| Burst duration | 8 ms | burst phase |
| VOT duration | 18 ms | voice onset time |
| Burst gain | 0.38 | |

**v1 measured:** Burst centroid 1297 Hz ✓

**v2 parameters (v6 — CURRENT):**

| Parameter | Value | Unit |
|-----------|-------|------|
| Closure duration | 28 ms | voiceless closure |
| Burst duration | 8 ms | burst phase |
| VOT duration | 18 ms | voice onset time |
| Burst formants | [600, 1300, 2100, 3000] Hz | bilabial locus |
| Burst bandwidths | [300, 300, 400, 500] Hz | |
| Burst gains | [6, 16, 4, 1.5] | F2 dominant |
| Burst decay | 130 Hz | slow (low frequency) |
| Burst gain | 0.20 | |

**v2 measured (PUROHITAM v2):**
- Closure voicing: 0.0000 (target ≤ 0.30) ✓
- Burst centroid: 1288 Hz (v1: 1297 Hz, diff 9 Hz) ✓
- Perceptual: clean release, no click ✓

**Architecture:** v6 three-component burst (pre-burst noise + spike + turbulence + onset ramp). Formants based on ṚTVIJAM [ʈ] verified architecture (1194 Hz) scaled for labial position. Burst centroid preserved within 9 Hz.

**Śikṣā class:** oṣṭhya (labial) — bilabial closure at lips
**Physics:** Lowest burst centroid (no anterior cavity — lips are front boundary)

---

##### [pʰ] — voiceless bilabial aspirated — फ

**Status:** ◯ PLANNED
**Architecture:** v6 + aspiration noise (60-100 ms VOT)
**Source word:** (future)

---

##### [b] — voiced bilabial stop — ब

**Status:** ◯ PLANNED
**Architecture:** v7 (spike + turbulence, no boundary fix)
**Source word:** (future)

Expected parameters (scaled from [p] v2):
- Murmur gain: 0.65
- Burst formants: [600, 1300, 2100, 3000] Hz (same as [p])
- No boundary fix (voiced)

---

##### [bʰ] — voiced bilabial aspirated — भ

**Status:** ◯ PLANNED
**Architecture:** v7 + breathy voicing (OQ 0.75-0.80, 40-60 ms murmur)
**Source word:** (future)

---

##### [m] — voiced bilabial nasal — म

**Status:** ✓ VERIFIED
**Architecture:** Nasal with antiresonance at 800 Hz
**Source word:** PUROHITAM (पुरोहितम्) — 1.1.1 word 3

| Parameter | Value | Unit |
|-----------|-------|------|
| F1 | 250 Hz | formant frequency |
| F2 | 900 Hz | formant frequency |
| F3 | 2200 Hz | formant frequency |
| F4 | 3000 Hz | formant frequency |
| B1-B4 | 100/200/300/350 Hz | formant bandwidths |
| G1-G4 | 8/2.5/0.5/0.2 | formant gains |
| Duration | 60 ms | base duration |
| Antiresonance | 800 Hz, BW 200 Hz | nasal zero |
| Coart onset | 0.15 | fraction |
| Coart offset | 0.15 | fraction |

**Measured values (PUROHITAM):**
- Antiresonance ratio: 0.0046 (target < 0.60) ✓
- F2 labial: 552 Hz (target 400-850 Hz) ✓
- F2 below [n] F2 ~900 Hz: 348 Hz separation ✓
- Voicing: 0.5978 (target ≥ 0.50) ✓

**Śikṣā class:** oṣṭhya (labial) — bilabial nasal
**Physics:** Lowest nasal F2 (bilabial position)

---

### CONSONANTS — SIBILANTS

#### [s] — voiceless dental sibilant — स

**Status:** ✓ VERIFIED
**Architecture:** Formant-filtered noise
**Source word:** YAJÑASYA (यज्ञस्य) — 1.1.1 word 4

| Parameter | Value | Unit |
|-----------|-------|------|
| Center frequency | 5500 Hz | dominant energy |
| Bandwidth | 3000 Hz | noise spread |
| Duration | 70 ms | base duration |
| Voicing | < 0.20 | voiceless |

**Measured values (YAJÑASYA):**
- Centroid: 5500-6000 Hz region ✓
- Voicing: < 0.20 ✓
- Dental sibilant (not palatal ~7000 Hz, not retroflex ~4000 Hz) ✓

---

#### [ɕ] — voiceless palatal sibilant — श

**Status:** ◯ PLANNED
**Architecture:** Formant-filtered noise
**Source word:** (future)

Expected parameters:
- Center frequency: 7000 Hz (highest of three sibilants)
- Bandwidth: 3000 Hz
- Duration: 70 ms

---

#### [ʂ] — voiceless retroflex sibilant — ष

**Status:** ◯ PLANNED
**Architecture:** Formant-filtered noise
**Source word:** (future)

Expected parameters:
- Center frequency: 4000 Hz (lowest of three sibilants)
- Bandwidth: 2500 Hz
- Duration: 70 ms

---

### CONSONANTS — SONORANTS

#### [ɾ] — alveolar tap — र

**Status:** ✓ VERIFIED
**Architecture:** Single Gaussian amplitude dip
**Source word:** PUROHITAM (पुरोहितम्) — 1.1.1 word 3

| Parameter | Value | Unit |
|-----------|-------|------|
| F1 | 300 Hz | formant frequency |
| F2 | 1900 Hz | formant frequency |
| F3 | 2700 Hz | formant frequency |
| F4 | 3300 Hz | formant frequency |
| B1-B4 | 120/200/250/300 Hz | formant bandwidths |
| G1-G4 | 12/6/1.5/0.4 | formant gains |
| Duration | 30 ms | base duration (shortest phoneme) |
| Dip depth | 0.35 | amplitude reduction |
| Dip width | 0.40 | fraction of duration |
| Coart onset | 0.15 | fraction |
| Coart offset | 0.15 | fraction |

**Measured values (PUROHITAM):**
- Voicing: 0.4727 (target ≥ 0.35) ✓
- F2 centroid: 1897 Hz (target 1700-2200 Hz, dantya-adjacent) ✓
- F3 centroid: 2643 Hz (target 2400-3100 Hz, no retroflex) ✓
- F3 above [ɻ̩] F3: 288 Hz (confirms not retroflex) ✓
- Amplitude dip count: 2 (target 1-3, single contact) ✓
- Duration: 30 ms (target 20-45 ms) ✓

**Śikṣā class:** antastha (semivowel) — "standing in between"
**Physics:** Single ballistic tongue contact (not trill, not approximant)
**The antastha tap criterion:** Single dip, 20-40 ms, F2 dantya, F3 neutral

---

#### [ɭ] — voiced retroflex lateral — ळ

**Status:** ✓ VERIFIED
**Architecture:** Lateral + F3 notch
**Source word:** ĪḶE (ईळे) — 1.1.1 word 2

| Parameter | Value | Unit |
|-----------|-------|------|
| F1 | 350 Hz | formant frequency |
| F2 | 1150 Hz | formant frequency |
| F3 | 2200 Hz | formant frequency (before notch) |
| F4 | 3200 Hz | formant frequency |
| B1-B4 | 120/180/250/300 Hz | formant bandwidths |
| G1-G4 | 10/5/1.2/0.4 | formant gains |
| Duration | 60 ms | base duration |
| F3 notch freq | 2200 Hz | retroflex marker |
| F3 notch BW | 300 Hz | |

**Measured values (ĪḶE):**
- F2 centroid: 1158 Hz (lateral low F2) ✓
- F3 centroid: 2413 Hz (retroflex F3 depression) ✓
- F3 depression: 287 Hz vs neutral 2700 Hz ✓
- Voicing: > 0.60 ✓

**Śikṣā class:** mūrdhanya (retroflex) lateral
**Physics:** Lateral airflow + sublingual cavity → F3 depression

---

#### [l] — voiced dental lateral — ल

**Status:** ◯ PLANNED
**Architecture:** Lateral formant structure
**Source word:** (future)

Expected parameters:
- F1: 350 Hz
- F2: 1200 Hz (low F2 characteristic of laterals)
- F3: 2700 Hz (neutral, no retroflex)
- Duration: 60 ms

**Distinguishes from [ɭ] by F3:** [l] neutral ~2700 Hz, [ɭ] depressed ~2400 Hz

---

#### [j] — voiced palatal approximant — य

**Status:** ✓ VERIFIED
**Architecture:** High F2 approximant
**Source word:** YAJÑASYA (यज्ञस्य) — 1.1.1 word 4

| Parameter | Value | Unit |
|-----------|-------|------|
| F1 | 280 Hz | formant frequency |
| F2 | 2200 Hz | formant frequency (palatal) |
| F3 | 2900 Hz | formant frequency |
| F4 | 3400 Hz | formant frequency |
| B1-B4 | 90/140/200/270 Hz | formant bandwidths |
| G1-G4 | 12/8/1.5/0.5 | formant gains |
| Duration | 50 ms | base duration |

**Measured values (YAJÑASYA):**
- F2 centroid: ~2200 Hz (palatal approximant locus) ✓
- Amplitude dip count: 0 (sustained constriction, not contact) ✓
- Voicing: > 0.60 ✓

**Śikṣā class:** antastha (semivowel) — palatal approximant
**Distinguishes from [i] by:** Lower intensity, shorter duration, higher coarticulation

---

#### [v] — voiced labio-dental approximant — व

**Status:** ✓ VERIFIED
**Architecture:** Labio-dental approximant
**Source word:** DEVAM (देवम्) — 1.1.1 word 5

| Parameter | Value | Unit |
|-----------|-------|------|
| F1 | 300 Hz | formant frequency |
| F2 | 1500 Hz | formant frequency |
| F3 | 2400 Hz | formant frequency |
| F4 | 3100 Hz | formant frequency |
| B1-B4 | 180/350/400/400 Hz | formant bandwidths |
| G1-G4 | 10/5/1.5/0.5 | formant gains |
| Duration | 60 ms | base duration |
| Coart onset | 0.18 | fraction |
| Coart offset | 0.18 | fraction |

**Measured values (DEVAM):**
- F2 centroid: ~1500 Hz (labio-dental locus) ✓
- Amplitude dip count: 0 (sustained constriction) ✓
- Voicing: > 0.60 ✓

**Śikṣā class:** antastha (semivowel) — labio-dental approximant
**Physics:** Lip-teeth approximation with frication component

---

#### [h] — voiceless glottal fricative — ह

**Status:** ✓ VERIFIED
**Architecture:** Broadband aspiration noise (acoustically transparent)
**Source word:** PUROHITAM (पुरोहितम्) — 1.1.1 word 3

| Parameter | Value | Unit |
|-----------|-------|------|
| Formants (approx) | [500, 1500, 2500, 3500] Hz | shaped by context |
| Bandwidths | [200, 300, 400, 500] Hz | |
| Gains | [0.3, 0.2, 0.15, 0.1] | low intensity |
| Duration | 65 ms | base duration |
| Coart onset | 0.30 | high (transparent) |
| Coart offset | 0.30 | high (transparent) |

**Measured values (PUROHITAM):**
- Voicing: 0.0996 (target ≤ 0.35, lowest non-stop voicing) ✓
- RMS: 0.0996 (aspiration present) ✓
- Low-band centroid: 1840 Hz (interpolated between [oː] and [i]) ✓

**Śikṣā class:** kaṇṭhya (glottal)
**H origin confirmed:** C(h,H) ≈ 0.30 (closest phoneme to H in coherence space)
**Physics:** Glottal turbulence with open vocal tract — takes formant shape from adjacent vowels

---

### SPECIAL PHONOLOGICAL ELEMENTS

#### Anusvāra — nasalisation — ं

**Status:** ◯ PLANNED
**Implementation:** Nasalization of preceding vowel (lower velum, add nasal formants)

NOT a distinct phoneme — represents nasalization feature on vowels.

---

#### Visarga — voiceless release — ः

**Status:** ◯ PLANNED
**Implementation:** Voiceless aspiration echo of preceding vowel

Realized as brief (30-40 ms) voiceless version of preceding vowel's formant structure.

---

## COMPLETE INVENTORY — QUICK REFERENCE

### Verification status by class

| Class | Verified | Pending | Total | Progress |
|-------|----------|---------|-------|----------|
| Short vowels | 4/4 | 0 | 4 | 100% |
| Long monophthongs | 4/4 | 0 | 4 | 100% |
| Diphthongs | 0/2 | 2 | 2 | 0% |
| Voiceless stops | 3/10 | 7 | 10 | 30% |
| Voiced stops | 2/10 | 8 | 10 | 20% |
| Aspirated stops | 1/10 | 9 | 10 | 10% |
| Nasals | 3/5 | 2 | 5 | 60% |
| Sibilants | 1/3 | 2 | 3 | 33% |
| Sonorants | 5/6 | 1 | 6 | 83% |
| **TOTAL** | **23/54** | **31** | **54** | **43%** |

---

### All verified phonemes

**Vowels (8):**
[a] [aː] [i] [iː] [u] [ɻ̩] [eː] [oː]

**Stops (6):**
[p] [t] [ʈ] [g] [ɟ] [d]

**Aspirated stops (1):**
[dʰ]

**Nasals (3):**
[m] [n] [ɲ]

**Sibilants (1):**
[s]

**Sonorants (5):**
[ɾ] [ɭ] [j] [v] [h]

**Total: 24 phonemes verified** (including [ʈ] from ṚTVIJAM, counting [ɟ] as verified in ṚTVIJAM v7 though YAJÑASYA v3 update pending)

---

## VS VOWEL AND APPROXIMANT F2 MAP

**F2 ordering (front to back):**

| Phoneme | F2 | Class | Position |
|---------|-----|-------|----------|
| [i] / [iː] | 2096-2124 Hz | vowel | close front |
| [j] | ~2200 Hz | approximant | palatal |
| [ɾ] | 1897 Hz | tap | dantya-adjacent |
| [eː] | 1659 Hz | vowel | mid front |
| [v] | ~1500 Hz | approximant | labio-dental |
| [ɻ̩] | 1212 Hz | vowel | retroflex |
| [ɭ] | 1158 Hz | lateral | retroflex |
| [ɑ] | 1106 Hz | vowel | open central |
| [m] | 552 Hz | nasal | bilabial |
| [oː] | 757 Hz | vowel | mid back |
| [u] | 742 Hz | vowel | close back |

**F2 distinguishes front/back and consonant place throughout inventory.**

---

## NASAL INVENTORY — CURRENT STATE

| Nasal | Place | Śikṣā | F2 | Anti-ratio | Status |
|-------|-------|-------|-----|------------|--------|
| [m] | bilabial | oṣṭhya | 552 Hz | 0.0046 | VERIFIED (PUROHITAM) |
| [n] | dental | dantya | ~900 Hz | 0.0018 | VERIFIED (AGNI) |
| [ɲ] | palatal | tālavya | ~1800 Hz | 0.0014 | VERIFIED (YAJÑASYA) |
| [ɳ] | retroflex | mūrdhanya | ~1300 Hz | — | PLANNED |
| [ŋ] | velar | kaṇṭhya | ~1200 Hz | — | PLANNED |

**All verified nasals show antiresonance ~800 Hz (nasal cavity acoustic zero — place-independent).**

**F2 ordering confirms Śikṣā place ordering:** oṣṭhya < kaṇṭhya < mūrdhanya < dantya < tālavya

---

## STOP BURST HIERARCHY — CURRENT STATE

**Five-place hierarchy COMPLETE (voiceless + voiced sample):**

| Place | Voiceless | Burst | Voiced | Burst | Architecture |
|-------|-----------|-------|--------|-------|--------------|
| mūrdhanya | [ʈ] | 1194 Hz | — | — | v6 ✓ |
| oṣṭhya | [p] | 1288 Hz (v2) | — | — | v6 ✓ |
| kaṇṭhya | — | — | [g] | 2594 Hz | v1 |
| tālavya | — | — | [ɟ] | 3223 Hz | v7 ✓ |
| dantya | [t] | 3013 Hz (v2) | [d] | ~3400 Hz | v6 ✓ / v1 |

**Low-burst region (800-1600 Hz):**
- [ʈ] and [p] both occupy this region (~1200-1300 Hz)
- Distinguished by F3 depression: [ʈ] 424 Hz depression (retroflex), [p] 0 Hz (no curl)

**Ordering:** mūrdhanya ≈ oṣṭhya << kaṇṭhya < tālavya ≈ dantya

**Physics:** Smaller anterior cavity → higher burst frequency

**Architecture status:**
- Voiceless [ʈ][p][t]: v6 canonical ✓
- Voiced [g][ɟ][d]: v1 or v7 (murmur, no boundary fix)

---

## APPROXIMANT CLASS — CURRENT STATE

| Phoneme | Type | F2 | Dip count | Duration | Status |
|---------|------|-----|-----------|----------|--------|
| [j] | palatal | ~2200 Hz | 0 | 50 ms | VERIFIED |
| [v] | labio-dental | ~1500 Hz | 0 | 60 ms | VERIFIED |
| [ɾ] | tap | 1897 Hz | 2 (single) | 30 ms | VERIFIED |

**Dip count distinguishes:**
- **0 dips:** Approximant (sustained constriction)
- **1-3 dips:** Tap (single ballistic contact)
- **4+ dips:** Trill (multiple periodic contacts)

**[ɾ] is antastha tap, not approximant.** Dip count 2 represents single contact (rising + falling edges detected as 2 minima in 5ms-smoothed envelope).

---

## ASPIRATION MODEL — CANONICAL IMPLEMENTATION

**Reference:** [dʰ] RATNADHĀTAMAM verified

### Architecture (voiced aspirated):

**Three phases:**

1. **Voiced closure (25-35 ms):**
   - Rosenberg pulse through formant bank
   - Murmur gain 0.50-0.70
   - Low-level sustained voicing

2. **Burst (7-10 ms):**
   - v7 spike + turbulence (no boundary fix needed)
   - Formant-filtered by place
   - Natural transition from murmur

3. **Post-burst murmur / breathy voicing (40-60 ms):**
   - Rosenberg pulse with HIGH open quotient (OQ 0.75-0.80)
   - Produces breathy voice quality
   - Formants transition from burst locus to following vowel
   - Exponential rise envelope from burst level to full voice
   - H1-H2 > 5 dB (diagnostic marker)

### Key insights:

1. **Aspiration = breathy voicing, NOT voiceless aspiration**
   - The term "aspirated" is misleading for voiced series
   - Correct term: "breathy voiced" or "murmured"
   - High OQ glottal source, not turbulence noise

2. **The murmur is voiced throughout**
   - Voicing ratio > 0.60 during entire murmur phase
   - H1-H2 > 5 dB distinguishes from modal voicing
   - Fundamental frequency traceable through murmur

3. **Formant transition is continuous**
   - From burst locus → target vowel over murmur duration
   - No abrupt changes
   - Smooth acoustic trajectory

### Diagnostic calibration for aspirated stops:

| Measure | Target | Method |
|---------|--------|--------|
| Closure voicing | 0.50-0.70 | Autocorrelation on closure |
| Burst centroid | Place-appropriate | FFT centroid on burst |
| Murmur voicing | > 0.60 | Autocorrelation on murmur |
| Murmur H1-H2 | > 5 dB | Harmonic amplitude ratio |
| Murmur duration | 40-60 ms | Time-domain measurement |

### Applies to:

- [gʰ] kaṇṭhya (velar)
- [ɟʰ] tālavya (palatal)
- [ɖʰ] mūrdhanya (retroflex)
- [dʰ] dantya (dental) — VERIFIED
- [bʰ] oṣṭhya (labial)

---

## DIAGNOSTIC METHODOLOGY LESSONS

### Lesson 1: Fix the Ruler (RATNADHĀTAMAM pattern)

**Problem:** [dʰ] measured as failed voicing despite sounding perfectly voiced.

**Diagnosis:** The ruler was broken. Measurement window included burst and silence → artificially lowered voicing score.

**Solution:** Measure murmur phase separately from burst and closure. Each phase has different voicing target.

**Principle:** When diagnostic fails but perception passes, check the diagnostic first. The ear is often right.

---

### Lesson 2: VOT Edge Effects

**Problem:** Short VOT (15-20 ms) measurements unstable. Including burst tail or vowel onset skews result.

**Solution:** Use central 50% of VOT only. Exclude edges.

**Principle:** Edge effects dominate when measurement window is small. Core extraction essential for short segments.

---

### Lesson 3: Voicing Frame Size

**Problem:** Different frame sizes give different voicing scores for same segment.

**Standard:** Use central 50% of segment (n//4 to 3n//4) for all voicing measurements unless specifically measuring onset/offset.

**Principle:** Consistent measurement protocol essential for cross-phoneme comparison.

---

### Lesson 4: Formant Band Selection

**Problem:** Too-narrow band misses formant energy. Too-wide band includes adjacent formants.

**Solution:** Choose band appropriate to target formant. See DIAGNOSTIC THRESHOLDS → Formant centroid bands.

**Principle:** F2 measurement for [u] (600-950 Hz target) requires different band than F2 for [i] (2000-2400 Hz target).

---

### Lesson 5: Post-Formant vs Glottal

**Problem:** H1-H2 intended to measure glottal source, but post-formant filtering can alter harmonic amplitudes.

**Solution:** Measure on segment with minimal formant coloring, OR use inverse filtering to recover glottal source.

**Status:** Not yet fully implemented. Currently using perceptual verification for breathiness.

---

### Lesson 6: Coarticulation Is Essential

**Problem:** Isolated phonemes sound "citation form" — unnatural, robotic.

**Solution:** Formant interpolation at phoneme boundaries (coart_on, coart_off parameters).

**Principle:** Natural speech requires continuous articulatory trajectory. Abrupt formant jumps sound artificial.

---

### Lesson 7: The Ear Is Final Arbiter

**Problem:** All numeric diagnostics pass, but word sounds wrong.

**Solution:** Listen. If it sounds wrong, it IS wrong. Find what the diagnostics missed.

**Principle:** The goal is perceptually accurate reconstruction, not numerically correct parameters. Perception trumps measurement.

---

### Lesson 8: The Click Was At The Boundary (ṚTVIJAM/PUROHITAM)

**Discovery:** Six ṚTVIJAM [ʈ] iterations (v1-v5) attempted to fix click by modifying burst synthesis. All failed. v6 realized click was at silence-to-burst **boundary**, not in burst itself.

**Physics:** Voiceless closure = total silence (no glottal vibration). Burst onset = sudden high-amplitude transient. Discontinuity at boundary = audible click.

**Solution (v6):** Pre-burst noise (3ms, amplitude 0.002) + onset ramp (1ms) masks boundary discontinuity. Click eliminated.

**Application:** PUROHITAM v2 applied v6 architecture to [p] and [t]:
- [p] v1 1297 Hz → v2 1288 Hz (8 Hz difference) ✓
- [t] v1 3006 Hz → v2 3013 Hz (6 Hz difference) ✓
- Perceptual: clicks eliminated, quality improved ✓

**Principle:** When iterating on a problem, consider that the problem may not be where you think it is. Six iterations changed burst synthesis. Zero iterations fixed the click. The click was at the boundary, not in the burst. v6 fixed the boundary. Click gone.

**This applies to ALL voiceless stops:** [k], [c], [ʈ], [t], [p] and aspirated [kʰ], [cʰ], [ʈʰ], [tʰ], [pʰ].

**Does NOT apply to voiced stops:** [g], [ɟ], [ɖ], [d], [b] and aspirated [gʰ], [ɟʰ], [ɖʰ], [dʰ], [bʰ] have murmur during closure — no silence-to-burst discontinuity, no boundary fix needed.

**Housecleaning status:**
- ṚTVIJAM [ʈ]: v6 verified (first implementation, canonical reference) ✓
- PUROHITAM [p][t]: v2 updated to v6 ✓
- Future: all voiceless stops will use v6

---

## HOUSECLEANING LOG

**Architecture updates to existing phonemes:**

| Word | Phonemes updated | Version | Change | Result |
|------|------------------|---------|--------|--------|
| ṚTVIJAM | [ʈ] [ɟ] | v6/v7 | First implementation of v6 (voiceless) and v7 (voiced) spike+turbulence architecture | ✓ VERIFIED |
| PUROHITAM | [p] [t] | v2 | Updated [p] and [t] from v1 bandpass noise to v6 spike+turbulence+boundary fix | ✓ VERIFIED |
| YAJÑASYA | [ɟ] | v3 NEXT | Update [��] from v1 bandpass noise to v7 spike+turbulence (voiced, no boundary fix) | PENDING |

**Policy:** When new architecture is discovered and verified (e.g., v6 for voiceless stops), previously verified phonemes using old architecture are queued for housecleaning. Original v1 parameters and measurements are preserved as reference. Updated versions maintain acoustic equivalence (burst centroids within 100 Hz) while improving perceptual quality.

**Completed housecleaning:**
- ṚTVIJAM [ʈ]: v6 verified (canonical reference) ✓
- ṚTVIJAM [ɟ]: v7 verified (voiced reference) ✓
- PUROHITAM [p][t]: v2 updated to v6 ✓

**Pending housecleaning:**
- YAJÑASYA [ɟ]: v3 update to v7 (HIGH priority)
- Future voiceless stops [k][c]: v6 when verified
- Future voiced stops [b][ɖ][etc]: v7 when verified

---

## OPEN INVENTORY POLICY

This inventory is open and growing. New phonemes added as they are verified through diagnostic testing. Parameter refinement ongoing.

**Current verified count: 24 phonemes**
**Target (full Rigveda inventory): ~54 phonemes**
**Progress: 43%**

**Next priorities:**
1. YAJÑASYA v3 housecleaning ([ɟ] update to v7)
2. Remaining voiceless stops [k] [c] (v6 architecture)
3. Diphthongs [ai] [au]
4. Remaining sibilants [ɕ] [ʂ]
5. Voiceless aspirated stops [kʰ] [cʰ] [ʈʰ] [tʰ] [pʰ]

---

## NEW PHONEME INTRODUCTION WORKFLOW

1. **Identify phoneme in source text** (Rigveda word)
2. **Determine Śikṣā classification** (place, manner, voicing, aspiration)
3. **Estimate parameters from physics and Śikṣā**:
   - Start with closest verified phoneme
   - Scale formants based on place
   - Adjust durations based on manner
4. **Synthesize initial version** using appropriate architecture (v6/v7/standard)
5. **Run diagnostic**:
   - Measure all relevant acoustic parameters
   - Compare to thresholds and VS-internal references
   - Check VS-internal separation from all verified phonemes
6. **Perceptual verification**:
   - Listen to isolated phoneme (normal + slow)
   - Listen to full word
   - Confirm naturalness and distinctiveness
7. **Iterate if needed**:
   - Adjust parameters based on diagnostic failures
   - Re-synthesize and re-test
   - Repeat until all criteria met
8. **Document in inventory**:
   - Add phoneme entry with verified parameters
   - Update hierarchy tables
   - Update verification status
   - Document iteration history in evidence file

---

## LINE STATUS

**Document version:** February 2026
**Total phonemes documented:** 54
**Verified phonemes:** 24
**Completion:** 43%

**Last major update:** PUROHITAM v2 housecleaning ([p] and [t] updated to v6 architecture)

**Next update:** YAJÑASYA v3 housecleaning ([ɟ] update to v7 architecture)

---

*End of Vedic Sanskrit Phoneme Inventory*
*February 2026*
