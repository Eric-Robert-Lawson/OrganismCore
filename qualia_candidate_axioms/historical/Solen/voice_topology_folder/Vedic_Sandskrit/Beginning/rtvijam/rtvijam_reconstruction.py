#!/usr/bin/env python3
"""
ṚTVIJAM v1 — First synthesis with retroflex [ʈ]
Rigveda 1.1.1, word 7

Word: ṛtvijam (ऋत्विजम्)
Translation: "minister of sacrifice, officiant" (accusative)
IPA: [ɻ̩tviɟɑm]

NEW PHONEME: [ʈ] voiceless retroflex stop
Śikṣā: mūrdhanya (retroflex/cerebral)

CRITICAL PREDICTION:
  Burst centroid ~1300 Hz (BELOW oṣṭhya [p] 1204 Hz)
  Counter-intuitive but physically correct:
  - Tongue tip curled back creates LARGE anterior cavity
  - Large cavity = LOW resonance frequency
  - This will be the LOWEST burst in the hierarchy

Expected hierarchy after verification:
  mūrdhanya [ʈ]  ~1300 Hz  ← NEW (lowest)
  oṣṭhya    [p]   1204 Hz
  kaṇṭhya   [g]   2594 Hz
  tālavya   [ɟ]   3223 Hz
  dantya    [t]   3764 Hz  (highest)

February 2026
"""

import numpy as np
from scipy.signal import lfilter, butter
import wave as wave_module
import os

SR = 44100
DTYPE = np.float32

os.makedirs("output_play", exist_ok=True)

# ============================================================================
# PHONEME PARAMETERS
# ============================================================================

# [ɻ̩] syllabic retroflex approximant — VERIFIED ṚG
VS_RV_F      = [420.0, 1300.0, 2200.0, 3100.0]
VS_RV_B      = [150.0,  200.0,  280.0,  300.0]
VS_RV_GAINS  = [ 14.0,    7.0,    1.5,    0.4]
VS_RV_DUR_MS = 60.0
VS_RV_F3_NOTCH    = 2200.0
VS_RV_F3_NOTCH_BW = 300.0
VS_RV_COART_ON    = 0.15
VS_RV_COART_OFF   = 0.15

# [ʈ] voiceless retroflex stop — NEW (this word)
# Śikṣā: mūrdhanya row 1 (voiceless unaspirated)
VS_TT_CLOSURE_MS  = 30.0
VS_TT_BURST_F     = 1300.0  # PREDICTED: below [p] 1204 Hz
VS_TT_BURST_BW    = 800.0
VS_TT_BURST_MS    = 8.0
VS_TT_VOT_MS      = 20.0
VS_TT_BURST_GAIN  = 0.40
VS_TT_F3_NOTCH    = 2200.0  # Retroflex F3 depression
VS_TT_F3_NOTCH_BW = 300.0
VS_TT_LOCUS_F     = [420.0, 1300.0, 2200.0, 3100.0]  # Same as [ɻ̩]

# [v] voiced labio-dental approximant — VERIFIED DEVAM
VS_V_F      = [300.0, 1500.0, 2400.0, 3100.0]
VS_V_B      = [180.0,  350.0,  400.0,  400.0]
VS_V_GAINS  = [ 10.0,    5.0,    1.5,    0.5]
VS_V_DUR_MS = 60.0
VS_V_COART_ON  = 0.18
VS_V_COART_OFF = 0.18

# [i] short close front unrounded — VERIFIED AGNI
VS_I_F      = [280.0, 2200.0, 2900.0, 3400.0]
VS_I_B      = [ 80.0,  130.0,  180.0,  250.0]
VS_I_GAINS  = [ 12.0,    8.0,    1.5,    0.5]
VS_I_DUR_MS = 50.0
VS_I_COART_ON  = 0.12
VS_I_COART_OFF = 0.12

# [ɟ] voiced palatal stop — VERIFIED YAJÑASYA
VS_JJ_F      = [280.0, 2100.0, 2800.0, 3300.0]
VS_JJ_B      = [100.0,  200.0,  300.0,  350.0]
VS_JJ_GAINS  = [ 10.0,    6.0,    1.5,    0.5]
VS_JJ_CLOSURE_MS  = 30.0
VS_JJ_BURST_F     = 3200.0
VS_JJ_BURST_BW    = 1500.0
VS_JJ_BURST_MS    = 9.0
VS_JJ_VOT_MS      = 10.0
VS_JJ_MURMUR_GAIN = 0.70
VS_JJ_BURST_GAIN  = 0.32

# [ɑ] short open central unrounded — VERIFIED AGNI
VS_A_F      = [700.0, 1100.0, 2550.0, 3400.0]
VS_A_B      = [130.0,  160.0,  220.0,  280.0]
VS_A_GAINS  = [ 16.0,    6.0,    1.5,    0.5]
VS_A_DUR_MS = 55.0
VS_A_COART_ON  = 0.12
VS_A_COART_OFF = 0.12

# [m] bilabial nasal — VERIFIED PUROHITAM
VS_M_F       = [250.0,  900.0, 2200.0, 3000.0]
VS_M_B       = [100.0,  200.0,  300.0,  350.0]
VS_M_GAINS   = [  8.0,    2.5,    0.5,    0.2]
VS_M_DUR_MS  = 60.0
VS_M_ANTI_F  = 800.0
VS_M_ANTI_BW = 200.0
VS_M_COART_ON  = 0.15
VS_M_COART_OFF = 0.15

PITCH_HZ = 120.0

# ============================================================================
# SYNTHESIS HELPERS
# ============================================================================

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
    w0 = 2.0 * np.pi * fc / sr
    r = max(0.0, min(0.999, 1.0 - np.pi * bw / sr))
    b_n = [1.0, -2.0 * np.cos(w0), 1.0]
    a_n = [1.0, -2.0 * r * np.cos(w0), r * r]
    return f32(lfilter(b_n, a_n, sig.astype(float)))

def ola_stretch(sig, factor=6.0, sr=SR):
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

# ============================================================================
# PHONEME SYNTHESIS FUNCTIONS
# ============================================================================

def synth_RV(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=1.0):
    """[ɻ̩] syllabic retroflex approximant (VERIFIED ṚG)"""
    n = int(VS_RV_DUR_MS * dil / 1000.0 * SR)
    src = rosenberg_pulse(n, pitch_hz)
    
    f_mean = list(VS_RV_F)
    if F_prev is not None:
        for k in range(min(len(F_prev), len(VS_RV_F))):
            f_mean[k] = F_prev[k] * VS_RV_COART_ON + VS_RV_F[k] * (1.0 - VS_RV_COART_ON)
    if F_next is not None:
        for k in range(min(len(F_next), len(VS_RV_F))):
            f_mean[k] = f_mean[k] * (1.0 - VS_RV_COART_OFF) + F_next[k] * VS_RV_COART_OFF
    
    out = apply_formants(src, f_mean, VS_RV_B, VS_RV_GAINS)
    out = iir_notch(out, VS_RV_F3_NOTCH, VS_RV_F3_NOTCH_BW)
    
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.72
    return f32(out)

def synth_TT(pitch_hz=PITCH_HZ, dil=1.0):
    """
    [ʈ] voiceless retroflex stop — NEW (this word)
    Śikṣā: mūrdhanya row 1 (voiceless unaspirated)
    
    KEY PREDICTION:
      Burst ~1300 Hz (below [p] 1204 Hz)
      Counter-intuitive: retroflex curl creates large anterior cavity
      Large cavity = low burst frequency
      
    Architecture:
      - Closure (voiceless, silent)
      - Burst at retroflex locus (~1300 Hz)
      - VOT with gradual voicing onset
      - Apply F3 notch (retroflex marker)
    """
    n_cl = int(VS_TT_CLOSURE_MS / 1000.0 * SR)
    n_b = int(VS_TT_BURST_MS / 1000.0 * SR)
    n_v = int(VS_TT_VOT_MS / 1000.0 * SR)
    
    # Phase 1: Voiceless closure (silence)
    closure = np.zeros(n_cl, dtype=DTYPE)
    
    # Phase 2: Burst at retroflex locus
    burst_noise = np.random.randn(max(n_b, 4))
    b_, a_ = butter(2, [VS_TT_BURST_F - VS_TT_BURST_BW/2, 
                        VS_TT_BURST_F + VS_TT_BURST_BW/2], 
                   btype='band', fs=SR)
    burst = lfilter(b_, a_, burst_noise)
    if len(burst) > 1:
        burst = burst * np.hanning(len(burst))
    burst = f32(burst * VS_TT_BURST_GAIN)
    
    # Phase 3: VOT with gradual voicing onset
    vot_src = rosenberg_pulse(n_v, pitch_hz)
    vot_env = np.linspace(0.0, 1.0, n_v)
    vot = apply_formants(vot_src, VS_TT_LOCUS_F, VS_RV_B, [g*0.3 for g in VS_RV_GAINS])
    
    # Apply F3 notch to VOT (retroflex marker)
    vot = iir_notch(vot, VS_TT_F3_NOTCH, VS_TT_F3_NOTCH_BW)
    vot = f32(vot * vot_env * 0.12)
    
    # Concatenate
    out = np.concatenate([closure, burst, vot])
    
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.55
    return f32(out)

def synth_V(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=1.0):
    """[v] voiced labio-dental approximant (VERIFIED DEVAM)"""
    n = int(VS_V_DUR_MS * dil / 1000.0 * SR)
    src = rosenberg_pulse(n, pitch_hz)
    
    f_mean = list(VS_V_F)
    if F_prev is not None:
        for k in range(min(len(F_prev), len(VS_V_F))):
            f_mean[k] = F_prev[k] * VS_V_COART_ON + VS_V_F[k] * (1.0 - VS_V_COART_ON)
    if F_next is not None:
        for k in range(min(len(F_next), len(VS_V_F))):
            f_mean[k] = f_mean[k] * (1.0 - VS_V_COART_OFF) + F_next[k] * VS_V_COART_OFF
    
    out = apply_formants(src, f_mean, VS_V_B, VS_V_GAINS)
    
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.68
    return f32(out)

def synth_I(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=1.0):
    """[i] short close front unrounded (VERIFIED AGNI)"""
    n = int(VS_I_DUR_MS * dil / 1000.0 * SR)
    src = rosenberg_pulse(n, pitch_hz)
    
    f_mean = list(VS_I_F)
    if F_prev is not None:
        for k in range(min(len(F_prev), len(VS_I_F))):
            f_mean[k] = F_prev[k] * VS_I_COART_ON + VS_I_F[k] * (1.0 - VS_I_COART_ON)
    if F_next is not None:
        for k in range(min(len(F_next), len(VS_I_F))):
            f_mean[k] = f_mean[k] * (1.0 - VS_I_COART_OFF) + F_next[k] * VS_I_COART_OFF
    
    out = apply_formants(src, f_mean, VS_I_B, VS_I_GAINS)
    
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.70
    return f32(out)

def synth_JJ(pitch_hz=PITCH_HZ, dil=1.0):
    """[ɟ] voiced palatal stop (VERIFIED YAJÑASYA)"""
    n_cl = int(VS_JJ_CLOSURE_MS / 1000.0 * SR)
    n_b = int(VS_JJ_BURST_MS / 1000.0 * SR)
    n_v = int(VS_JJ_VOT_MS / 1000.0 * SR)
    
    # Phase 1: Voiced closure
    src_cl = rosenberg_pulse(n_cl, pitch_hz)
    b_lp, a_lp = butter(2, 500.0 / (SR/2.0), btype='low')
    murmur_cl = lfilter(b_lp, a_lp, src_cl.astype(float))
    closure = f32(murmur_cl * VS_JJ_MURMUR_GAIN)
    
    # Phase 2: Burst
    burst_noise = np.random.randn(max(n_b, 4))
    b_, a_ = butter(2, [VS_JJ_BURST_F - VS_JJ_BURST_BW/2, 
                        VS_JJ_BURST_F + VS_JJ_BURST_BW/2], 
                   btype='band', fs=SR)
    burst = lfilter(b_, a_, burst_noise)
    if len(burst) > 1:
        burst = burst * np.hanning(len(burst))
    burst = f32(burst * VS_JJ_BURST_GAIN)
    
    # Phase 3: VOT
    vot_src = rosenberg_pulse(n_v, pitch_hz)
    vot_env = np.linspace(0.5, 1.0, n_v)
    vot = apply_formants(vot_src, VS_JJ_F, VS_JJ_B, [g*0.4 for g in VS_JJ_GAINS])
    vot = f32(vot * vot_env * 0.15)
    
    out = np.concatenate([closure, burst, vot])
    
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.60
    return f32(out)

def synth_A(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=1.0):
    """[ɑ] short open central unrounded (VERIFIED AGNI)"""
    n = int(VS_A_DUR_MS * dil / 1000.0 * SR)
    src = rosenberg_pulse(n, pitch_hz)
    
    f_mean = list(VS_A_F)
    if F_prev is not None:
        for k in range(min(len(F_prev), len(VS_A_F))):
            f_mean[k] = F_prev[k] * VS_A_COART_ON + VS_A_F[k] * (1.0 - VS_A_COART_ON)
    if F_next is not None:
        for k in range(min(len(F_next), len(VS_A_F))):
            f_mean[k] = f_mean[k] * (1.0 - VS_A_COART_OFF) + F_next[k] * VS_A_COART_OFF
    
    out = apply_formants(src, f_mean, VS_A_B, VS_A_GAINS)
    
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.72
    return f32(out)

def synth_M(F_prev=None, pitch_hz=PITCH_HZ, dil=1.0):
    """[m] bilabial nasal (VERIFIED PUROHITAM)"""
    n = int(VS_M_DUR_MS * dil / 1000.0 * SR)
    src = rosenberg_pulse(n, pitch_hz)
    
    f_mean = list(VS_M_F)
    if F_prev is not None:
        for k in range(min(len(F_prev), len(VS_M_F))):
            f_mean[k] = F_prev[k] * VS_M_COART_ON + VS_M_F[k] * (1.0 - VS_M_COART_ON)
    
    out = apply_formants(src, f_mean, VS_M_B, VS_M_GAINS)
    out = iir_notch(out, VS_M_ANTI_F, VS_M_ANTI_BW)
    
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.42
    return f32(out)

# ============================================================================
# WORD SYNTHESIS
# ============================================================================

def synth_rtvijam(pitch_hz=PITCH_HZ, dil=1.0):
    """
    ṚTVIJAM [ɻ̩tviɟɑm]
    Syllables: ṚT-VI-JAM
    
    NEW: [ʈ] voiceless retroflex stop
    First word to enter the mūrdhanya consonant sector
    """
    segs = [
        synth_RV(F_next=VS_TT_LOCUS_F, pitch_hz=pitch_hz, dil=dil),
        synth_TT(pitch_hz=pitch_hz, dil=dil),
        synth_V(F_prev=VS_TT_LOCUS_F, F_next=VS_I_F, pitch_hz=pitch_hz, dil=dil),
        synth_I(F_prev=VS_V_F, F_next=VS_JJ_F, pitch_hz=pitch_hz, dil=dil),
        synth_JJ(pitch_hz=pitch_hz, dil=dil),
        synth_A(F_prev=VS_JJ_F, F_next=VS_M_F, pitch_hz=pitch_hz, dil=dil),
        synth_M(F_prev=VS_A_F, pitch_hz=pitch_hz, dil=dil),
    ]
    
    word = np.concatenate(segs)
    mx = np.max(np.abs(word))
    if mx > 1e-8:
        word = word / mx * 0.75
    return f32(word)

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print()
    print("=" * 70)
    print("ṚTVIJAM v1 — First synthesis with retroflex [ʈ]")
    print("=" * 70)
    print()
    print("NEW PHONEME: [ʈ] voiceless retroflex stop")
    print("  Śikṣā: mūrdhanya row 1")
    print()
    print("CRITICAL PREDICTION:")
    print("  Burst centroid ~1300 Hz")
    print("  BELOW oṣ���hya [p] 1204 Hz")
    print()
    print("  Counter-intuitive but physically correct:")
    print("  - Tongue tip curled back = large anterior cavity")
    print("  - Large cavity = low resonance frequency")
    print()
    print("  This will be the LOWEST burst in hierarchy:")
    print("    mūrdhanya [ʈ]  ~1300 Hz  ← NEW (lowest)")
    print("    oṣṭhya    [p]   1204 Hz")
    print("    kaṇṭhya   [g]   2594 Hz")
    print("    tālavya   [ɟ]   3223 Hz")
    print("    dantya    [t]   3764 Hz  (highest)")
    print()
    print("RETROFLEX MARKERS:")
    print("  - F3 notch applied (~2200 Hz)")
    print("  - F3 depression is mūrdhanya signature")
    print("  - Same F3 signature as [ɻ̩] in ṚG")
    print()
    
    word_dry = synth_rtvijam(PITCH_HZ, 1.0)
    word_perf = synth_rtvijam(PITCH_HZ, 2.5)
    word_slow = ola_stretch(word_dry, 6.0)
    
    write_wav("output_play/rtvijam_dry.wav", word_dry)
    write_wav("output_play/rtvijam_performance.wav", word_perf)
    write_wav("output_play/rtvijam_slow.wav", word_slow)
    
    print()
    print("=" * 70)
    print("v1 synthesis complete.")
    print("Run rtvijam_diagnostic.py to verify [ʈ]")
    print("=" * 70)
    print()
