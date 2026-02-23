#!/usr/bin/env python3
"""
RATNADHĀTAMAM v13 — Complete pre/de-emphasis pipeline
Vedic Sanskrit: ratnadhātamam [rɑtnɑdʰaːtɑmɑm]
Rigveda 1.1.1 — word 9

CRITICAL FIX (v12→v13):
Add de-emphasis AFTER formant filtering

v12 problem: Pre-emphasis only → suppressed H1 even more
             Murmur amplitude dropped 74%
             H1-H2 got WORSE (-0.88 → -3.04 dB)

v13 solution: Complete pre/de-emphasis pipeline
              1. Pre-emphasis BEFORE formants (flatten spectrum)
              2. Formant filtering (add resonances)
              3. De-emphasis AFTER formants (restore low freq)

This is standard Klatt/HMM-TTS pipeline.

De-emphasis = inverse of pre-emphasis:
  Pre:  y[n] = x[n] - 0.97×x[n-1]  (high-pass)
  De:   y[n] = x[n] + 0.97×y[n-1]  (low-pass)

Result: Formant peaks at F1/F2/F3, BUT H1 preserved at low frequency

Expected: H1-H2 = 10-14 dB

February 2026
"""

import numpy as np
from scipy.signal import lfilter, butter
import wave as wave_module
import os

SR = 44100
DTYPE = np.float32

os.makedirs("output_play", exist_ok=True)

# Phoneme parameters
VS_R_F = [300.0, 1900.0, 2700.0, 3300.0]
VS_R_B = [120.0, 200.0, 250.0, 300.0]
VS_R_GAINS = [12.0, 6.0, 1.5, 0.4]
VS_R_DUR_MS = 30.0

VS_A_F = [700.0, 1100.0, 2550.0, 3400.0]
VS_A_B = [130.0, 160.0, 220.0, 280.0]
VS_A_GAINS = [16.0, 6.0, 1.5, 0.5]
VS_A_DUR_MS = 55.0

VS_T_CLOSURE_MS = 25.0
VS_T_BURST_F = 3500.0
VS_T_BURST_BW = 1500.0
VS_T_BURST_MS = 7.0
VS_T_VOT_MS = 15.0
VS_T_BURST_GAIN = 0.38

VS_N_F = [250.0, 900.0, 2000.0, 3000.0]
VS_N_B = [100.0, 200.0, 300.0, 350.0]
VS_N_GAINS = [8.0, 2.5, 0.5, 0.2]
VS_N_DUR_MS = 60.0
VS_N_ANTI_F = 800.0

VS_DH_CLOSURE_MS = 28.0
VS_DH_BURST_F = 3500.0
VS_DH_BURST_BW = 1500.0
VS_DH_BURST_MS = 8.0
VS_DH_BURST_GAIN = 0.20
VS_DH_MURMUR_MS = 50.0
VS_DH_MURMUR_GAIN = 0.70

VS_AA_F = [700.0, 1100.0, 2550.0, 3400.0]
VS_AA_B = [130.0, 160.0, 220.0, 280.0]
VS_AA_GAINS = [16.0, 6.0, 1.5, 0.5]
VS_AA_DUR_MS = 110.0

VS_M_F = [250.0, 900.0, 2200.0, 3000.0]
VS_M_B = [100.0, 200.0, 300.0, 350.0]
VS_M_GAINS = [8.0, 2.5, 0.5, 0.2]
VS_M_DUR_MS = 60.0
VS_M_ANTI_F = 800.0

PITCH_HZ = 120.0

def f32(x):
    return np.asarray(x, dtype=DTYPE)

def write_wav(path, sig, sr=SR):
    sig_i = (np.clip(f32(sig), -1.0, 1.0) * 32767).astype(np.int16)
    with wave_module.open(path, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(sig_i.tobytes())
    print(f"Wrote {path}")

def rosenberg_pulse(n_samples, pitch_hz, oq=0.65, sr=SR):
    """Rosenberg glottal pulse model"""
    period = int(sr / pitch_hz)
    pulse = np.zeros(period, dtype=float)
    t1 = int(period * oq * 0.6)
    t2 = int(period * oq)
    for i in range(t1):
        pulse[i] = 0.5 * (1.0 - np.cos(np.pi * i / t1))
    for i in range(t1, t2):
        pulse[i] = np.cos(np.pi * (i - t1) / (2.0 * (t2 - t1)))
    d_pulse = np.diff(pulse, prepend=pulse[0])
    n_reps = (n_samples // period) + 2
    repeated = np.tile(d_pulse, n_reps)
    return f32(repeated[:n_samples])

def apply_formants(src, freqs, bws, gains, sr=SR):
    """Formant filter bank (IIR resonators)"""
    out = np.zeros(len(src), dtype=float)
    nyq = sr / 2.0
    for f, bw, g in zip(freqs, bws, gains):
        if f > 0 and f < nyq:
            r = np.exp(-np.pi * bw / sr)
            cosf = 2.0 * np.cos(2.0 * np.pi * f / sr)
            a = [1.0, -r * cosf, r * r]
            b = [1.0 - r]
            res = lfilter(b, a, src.astype(float))
            out += res * g
    return f32(out)

def iir_notch(sig, fc, bw=200.0, sr=SR):
    """Nasal antiresonance"""
    w0 = 2.0 * np.pi * fc / sr
    r = max(0.0, min(0.999, 1.0 - np.pi * bw / sr))
    b_n = [1.0, -2.0 * np.cos(w0), 1.0]
    a_n = [1.0, -2.0 * r * np.cos(w0), r * r]
    return f32(lfilter(b_n, a_n, sig.astype(float)))

def ola_stretch(sig, factor=6.0, sr=SR):
    """Time-stretch via overlap-add"""
    win_ms = 40.0
    win_n = int(win_ms / 1000.0 * sr)
    if win_n % 2 == 1:
        win_n += 1
    hop_in = win_n // 4
    hop_out = int(hop_in * factor)
    window = np.hanning(win_n).astype(DTYPE)
    n_in = len(sig)
    n_frames = max(1, (n_in - win_n) // hop_in + 1)
    n_out = hop_out * n_frames + win_n
    out = np.zeros(n_out, dtype=DTYPE)
    norm = np.zeros(n_out, dtype=DTYPE)
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
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.75
    return f32(out)

def synth_R(pitch_hz=PITCH_HZ, dil=1.0):
    """[ɾ] alveolar tap (VERIFIED PUROHITAM)"""
    n = int(VS_R_DUR_MS * dil / 1000.0 * SR)
    src = rosenberg_pulse(n, pitch_hz)
    env = np.ones(n)
    env[int(n*0.3):int(n*0.7)] *= 0.35
    src *= env
    out = apply_formants(src, VS_R_F, VS_R_B, VS_R_GAINS)
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.62
    return f32(out)

def synth_A(pitch_hz=PITCH_HZ, dil=1.0):
    """[ɑ] short open central (VERIFIED AGNI)"""
    n = int(VS_A_DUR_MS * dil / 1000.0 * SR)
    src = rosenberg_pulse(n, pitch_hz)
    out = apply_formants(src, VS_A_F, VS_A_B, VS_A_GAINS)
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.72
    return f32(out)

def synth_T(pitch_hz=PITCH_HZ, dil=1.0):
    """[t] voiceless dental stop (VERIFIED PUROHITAM)"""
    n_cl = int(VS_T_CLOSURE_MS / 1000.0 * SR)
    n_b = int(VS_T_BURST_MS / 1000.0 * SR)
    n_v = int(VS_T_VOT_MS / 1000.0 * SR)
    
    closure = np.zeros(n_cl, dtype=DTYPE)
    
    burst_noise = np.random.randn(max(n_b, 4))
    b_, a_ = butter(2, [VS_T_BURST_F - VS_T_BURST_BW/2, 
                        VS_T_BURST_F + VS_T_BURST_BW/2], 
                   btype='band', fs=SR)
    burst = lfilter(b_, a_, burst_noise)
    if len(burst) > 1:
        burst = burst * np.hanning(len(burst))
    burst = f32(burst * VS_T_BURST_GAIN)
    
    vot_src = rosenberg_pulse(n_v, pitch_hz)
    vot_env = np.linspace(0.0, 1.0, n_v)
    vot = apply_formants(vot_src, VS_A_F, VS_A_B, [g*0.3 for g in VS_A_GAINS])
    vot = f32(vot * vot_env * 0.12)
    
    out = np.concatenate([closure, burst, vot])
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.55
    return f32(out)

def synth_N(pitch_hz=PITCH_HZ, dil=1.0):
    """[n] dental nasal (VERIFIED AGNI)"""
    n = int(VS_N_DUR_MS * dil / 1000.0 * SR)
    src = rosenberg_pulse(n, pitch_hz)
    out = apply_formants(src, VS_N_F, VS_N_B, VS_N_GAINS)
    out = iir_notch(out, VS_N_ANTI_F, 200.0)
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.42
    return f32(out)

def synth_DH(pitch_hz=PITCH_HZ, dil=1.0):
    """
    [dʰ] — voiced dental aspirated stop
    v13: Complete pre/de-emphasis pipeline
    
    v12 FAILURE: Pre-emphasis only → H1 suppressed → H1-H2 = -3.04 dB (worse)
    
    v13 SOLUTION: Full pipeline (standard speech synthesis)
    
    STEP 1: PRE-EMPHASIS before formants
            y[n] = x[n] - 0.97×x[n-1]
            High-pass filter, +6 dB/octave
            Flattens Rosenberg spectral slope
    
    STEP 2: FORMANT FILTERING
            IIR resonators at F1/F2/F3/F4
            Adds vocal tract resonances
            BUT: suppresses frequencies far from formant centers
    
    STEP 3: DE-EMPHASIS after formants
            y[n] = x[n] + 0.97×y[n-1]
            Low-pass filter, inverse of pre-emphasis
            Restores low-frequency energy (including H1)
    
    Net result:
    - Formant peaks at F1/F2/F3 (vocal tract shape)
    - H1 preserved at 120 Hz (voicing fundamental)
    - H2+ attenuated (slight breathiness from OQ 0.55)
    - H1-H2 ratio: 10-14 dB
    
    This is standard Klatt/HMM-TTS/vocoder pipeline.
    """
    n_cl = int(VS_DH_CLOSURE_MS / 1000.0 * SR)
    n_b = int(VS_DH_BURST_MS / 1000.0 * SR)
    n_m = int(VS_DH_MURMUR_MS * dil / 1000.0 * SR)
    
    # Phase 1: Voiced closure (same as [d])
    src_cl = rosenberg_pulse(n_cl, pitch_hz, oq=0.65)
    b_lp, a_lp = butter(2, 500.0 / (SR/2.0), btype='low')
    murmur_cl = lfilter(b_lp, a_lp, src_cl.astype(float))
    closure = f32(murmur_cl * 0.70)
    
    # Phase 2: Burst (same as [d] and [t] — dantya locus)
    burst_noise = np.random.randn(max(n_b, 4))
    b_bp, a_bp = butter(2, [VS_DH_BURST_F - VS_DH_BURST_BW/2, 
                             VS_DH_BURST_F + VS_DH_BURST_BW/2], 
                        btype='band', fs=SR)
    burst = lfilter(b_bp, a_bp, burst_noise)
    if len(burst) > 1:
        burst = burst * np.hanning(len(burst))
    burst = f32(burst * VS_DH_BURST_GAIN)
    
    # Phase 3: MURMUR (v13 — complete pre/de-emphasis pipeline)
    
    # Generate slightly-breathy Rosenberg pulse (OQ 0.55)
    murmur_pulse = rosenberg_pulse(n_m, pitch_hz, oq=0.55)
    
    # STEP 1: PRE-EMPHASIS (high-pass, flatten spectrum)
    pre_emph_coef = 0.97
    murmur_preemph = np.zeros_like(murmur_pulse)
    murmur_preemph[0] = murmur_pulse[0]
    murmur_preemph[1:] = murmur_pulse[1:] - pre_emph_coef * murmur_pulse[:-1]
    
    # STEP 2: FORMANT FILTERING (add vocal tract resonances)
    murmur_bws = [bw * 1.5 for bw in VS_AA_B]
    murmur_filtered = apply_formants(murmur_preemph, VS_AA_F, murmur_bws, VS_AA_GAINS)
    
    # STEP 3: DE-EMPHASIS (low-pass, restore low frequencies)
    # IIR filter: y[n] = x[n] + α×y[n-1]
    # This is the INVERSE of pre-emphasis
    # Restores H1 energy that was suppressed by formant filtering
    murmur_deemph = lfilter([1.0], [1.0, -pre_emph_coef], murmur_filtered.astype(float))
    
    # Envelope (starts at 0.5 for voicing continuity)
    attack = int(n_m * 0.15)
    env = np.ones(n_m, dtype=float)
    if attack > 0:
        env[:attack] = np.linspace(0.5, 1.0, attack)
        env[-attack:] = np.linspace(1.0, 0.9, attack)
    
    murmur = f32(murmur_deemph * env * VS_DH_MURMUR_GAIN)
    
    # Concatenate all phases
    out = np.concatenate([closure, burst, murmur])
    
    # Per-phoneme normalization
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.60
    
    return f32(out)

def synth_AA(pitch_hz=PITCH_HZ, dil=1.0):
    """[aː] long open central (PENDING)"""
    n = int(VS_AA_DUR_MS * dil / 1000.0 * SR)
    src = rosenberg_pulse(n, pitch_hz)
    out = apply_formants(src, VS_AA_F, VS_AA_B, VS_AA_GAINS)
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.72
    return f32(out)

def synth_M(pitch_hz=PITCH_HZ, dil=1.0):
    """[m] bilabial nasal (VERIFIED PUROHITAM)"""
    n = int(VS_M_DUR_MS * dil / 1000.0 * SR)
    src = rosenberg_pulse(n, pitch_hz)
    out = apply_formants(src, VS_M_F, VS_M_B, VS_M_GAINS)
    out = iir_notch(out, VS_M_ANTI_F, 200.0)
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.42
    return f32(out)

def synth_ratnadhatamam(pitch_hz=PITCH_HZ, dil=1.0):
    """
    Synthesize: ratnadhātamam [rɑtnɑdʰaːtɑmɑm]
    Syllables: RAT-NA-DHĀ-TA-MAM
    """
    segs = [
        synth_R(pitch_hz, dil),
        synth_A(pitch_hz, dil),
        synth_T(pitch_hz, dil),
        synth_N(pitch_hz, dil),
        synth_A(pitch_hz, dil),
        synth_DH(pitch_hz, dil),  # ← v13 pre/de-emphasis
        synth_AA(pitch_hz, dil),
        synth_T(pitch_hz, dil),
        synth_A(pitch_hz, dil),
        synth_M(pitch_hz, dil),
        synth_A(pitch_hz, dil),
        synth_M(pitch_hz, dil)
    ]
    
    word = np.concatenate(segs)
    mx = np.max(np.abs(word))
    if mx > 1e-8:
        word = word / mx * 0.75
    return f32(word)

if __name__ == "__main__":
    print("=" * 70)
    print("RATNADHĀTAMAM v13 (Complete pre/de-emphasis pipeline)")
    print("=" * 70)
    print()
    print("v13 fix:")
    print("  Complete standard speech synthesis pipeline:")
    print("  1. Pre-emphasis (flatten spectrum)")
    print("  2. Formant filtering (add resonances)")
    print("  3. De-emphasis (restore low frequencies)")
    print()
    print("v12 problem:")
    print("  Pre-emphasis only → suppressed H1 → worse H1-H2")
    print()
    print("v13 solution:")
    print("  De-emphasis after filtering → restores H1")
    print()
    print("Expected:")
    print("  H1-H2: 10-14 dB (H1 preserved)")
    print("  Voicing: 0.50+ (clean Rosenberg)")
    print("  Perceptual: Clear pitch + formant resonances")
    print()
    
    word_dry = synth_ratnadhatamam(PITCH_HZ, 1.0)
    word_perf = synth_ratnadhatamam(PITCH_HZ, 2.5)
    word_slow = ola_stretch(word_dry, 6.0)
    
    write_wav("output_play/ratnadhatamam_dry.wav", word_dry)
    write_wav("output_play/ratnadhatamam_performance.wav", word_perf)
    write_wav("output_play/ratnadhatamam_slow.wav", word_slow)
    
    print()
    print("=" * 70)
    print("v13 complete. Run ratnadhatamam_diagnostic.py v2.4")
    print()
    print("Expected: D5 and D6 should PASS")
    print("=" * 70)
