#!/usr/bin/env python3
"""
HOTĀRAM v6 — Revert to AGNI verified parameters
Rigveda 1.1.1, word 8

ITERATION v5→v6:
  Problem: F2 measuring low across all iterations (v1-v5)
           Isolated [ɑ] F2=762 Hz vs target 1100 Hz
           BUT: AGNI verified [ɑ] F2=1106 Hz with SAME parameters
  
  Diagnosis: MEASUREMENT PROBLEM, not synthesis problem
           - Diagnostic F2 band starts at 700 Hz (captures F1 tail)
           - AGNI F2 band starts at 850 Hz (excludes F1 tail)
           - F1 gain (16.0) dominates centroid calculation
           - Measured centroid pulled down by F1 energy
  
  Fix: REVERT to AGNI verified parameters
       NO synthesis changes needed
       Parameters were correct all along
       Diagnostic will be fixed separately
  
  Ancestor directive: "The synthesis is correct. Fix the ruler."

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
# PHONEME PARAMETERS (v6 - AGNI VERIFIED VALUES RESTORED)
# ============================================================================

# [h] voiceless glottal fricative — VERIFIED PUROHITAM
VS_H_F_APPROX = [500.0, 1500.0, 2500.0, 3500.0]
VS_H_B        = [200.0,  300.0,  400.0,  500.0]
VS_H_GAINS    = [  0.3,    0.2,    0.15,   0.1]
VS_H_DUR_MS    = 65.0
VS_H_COART_ON  = 0.30
VS_H_COART_OFF = 0.30

# [oː] long close-mid back rounded — VERIFIED PUROHITAM
VS_OO_F      = [430.0,  800.0, 2500.0, 3200.0]
VS_OO_B      = [110.0,  130.0,  200.0,  270.0]
VS_OO_GAINS  = [ 15.0,    8.0,    1.5,    0.5]
VS_OO_DUR_MS = 100.0
VS_OO_COART_ON  = 0.10
VS_OO_COART_OFF = 0.10

# [t] voiceless dental stop — VERIFIED PUROHITAM
VS_T_CLOSURE_MS = 25.0
VS_T_BURST_F    = 3500.0
VS_T_BURST_BW   = 1500.0
VS_T_BURST_MS   = 7.0
VS_T_VOT_MS     = 15.0
VS_T_BURST_GAIN = 0.38
VS_T_LOCUS_F    = [700.0, 1800.0, 2500.0, 3500.0]

# [aː] long open central unrounded — PENDING (this word)
# v6: RESTORED to AGNI verified values
VS_AA_F      = [700.0, 1100.0, 2550.0, 3400.0]  # AGNI original
VS_AA_B      = [130.0,  160.0,  220.0,  280.0]  # AGNI original
VS_AA_GAINS  = [ 16.0,    6.0,    1.5,    0.5]
VS_AA_DUR_MS = 110.0
VS_AA_COART_ON  = 0.10
VS_AA_COART_OFF = 0.10

# [ɾ] alveolar tap — VERIFIED PUROHITAM
VS_R_F = [300.0, 1900.0, 2700.0, 3300.0]
VS_R_B = [120.0,  200.0,  250.0,  300.0]
VS_R_GAINS = [ 12.0,    6.0,    1.5,    0.4]
VS_R_DUR_MS = 30.0
VS_R_DIP_DEPTH = 0.35
VS_R_DIP_WIDTH = 0.40
VS_R_COART_ON  = 0.15
VS_R_COART_OFF = 0.15

# [ɑ] short open central unrounded — VERIFIED AGNI
# v6: RESTORED to AGNI verified values
VS_A_F      = [700.0, 1100.0, 2550.0, 3400.0]  # AGNI original
VS_A_B      = [130.0,  160.0,  220.0,  280.0]  # AGNI original
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

def synth_H(F_next=None, pitch_hz=PITCH_HZ, dil=1.0):
    """[h] voiceless glottal fricative (VERIFIED PUROHITAM)"""
    n = int(VS_H_DUR_MS * dil / 1000.0 * SR)
    noise = np.random.randn(n)
    
    f_ctx = list(VS_H_F_APPROX)
    if F_next is not None:
        for k in range(min(len(F_next), len(f_ctx))):
            f_ctx[k] = f_ctx[k] * (1.0 - VS_H_COART_OFF) + F_next[k] * VS_H_COART_OFF
    
    out = apply_formants(noise, f_ctx, VS_H_B, VS_H_GAINS)
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.45
    return f32(out)

def synth_OO(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=1.0):
    """[oː] long close-mid back rounded (VERIFIED PUROHITAM)"""
    n = int(VS_OO_DUR_MS * dil / 1000.0 * SR)
    src = rosenberg_pulse(n, pitch_hz)
    
    f_mean = list(VS_OO_F)
    if F_prev is not None:
        for k in range(min(len(F_prev), len(VS_OO_F))):
            f_mean[k] = F_prev[k] * VS_OO_COART_ON + VS_OO_F[k] * (1.0 - VS_OO_COART_ON)
    if F_next is not None:
        for k in range(min(len(F_next), len(VS_OO_F))):
            f_mean[k] = f_mean[k] * (1.0 - VS_OO_COART_OFF) + F_next[k] * VS_OO_COART_OFF
    
    out = apply_formants(src, f_mean, VS_OO_B, VS_OO_GAINS)
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
    vot = apply_formants(vot_src, VS_T_LOCUS_F, VS_AA_B, [g*0.3 for g in VS_AA_GAINS])
    vot = f32(vot * vot_env * 0.12)
    
    out = np.concatenate([closure, burst, vot])
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.55
    return f32(out)

def synth_AA(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=1.0):
    """
    [aː] long open central unrounded (PENDING this word)
    v6: AGNI verified parameters restored
    Identical to [ɑ] except 2× duration
    """
    n = int(VS_AA_DUR_MS * dil / 1000.0 * SR)
    src = rosenberg_pulse(n, pitch_hz)
    
    f_mean = list(VS_AA_F)
    if F_prev is not None:
        for k in range(min(len(F_prev), len(VS_AA_F))):
            f_mean[k] = F_prev[k] * VS_AA_COART_ON + VS_AA_F[k] * (1.0 - VS_AA_COART_ON)
    if F_next is not None:
        for k in range(min(len(F_next), len(VS_AA_F))):
            f_mean[k] = f_mean[k] * (1.0 - VS_AA_COART_OFF) + F_next[k] * VS_AA_COART_OFF
    
    out = apply_formants(src, f_mean, VS_AA_B, VS_AA_GAINS)
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.72
    return f32(out)

def synth_R(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=1.0):
    """[ɾ] alveolar tap (VERIFIED PUROHITAM)"""
    n = int(VS_R_DUR_MS * dil / 1000.0 * SR)
    src = rosenberg_pulse(n, pitch_hz)
    
    env = np.ones(n, dtype=float)
    dip_center = n // 2
    dip_width_samp = int(n * VS_R_DIP_WIDTH / 2)
    for i in range(n):
        dist = abs(i - dip_center)
        if dist < dip_width_samp:
            gaussian = np.exp(-4.0 * (dist / dip_width_samp) ** 2)
            env[i] = 1.0 - VS_R_DIP_DEPTH * gaussian
    src *= env
    
    f_mean = list(VS_R_F)
    if F_prev is not None:
        for k in range(min(len(F_prev), len(VS_R_F))):
            f_mean[k] = F_prev[k] * VS_R_COART_ON + VS_R_F[k] * (1.0 - VS_R_COART_ON)
    if F_next is not None:
        for k in range(min(len(F_next), len(VS_R_F))):
            f_mean[k] = f_mean[k] * (1.0 - VS_R_COART_OFF) + F_next[k] * VS_R_COART_OFF
    
    out = apply_formants(src, f_mean, VS_R_B, VS_R_GAINS)
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.62
    return f32(out)

def synth_A(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=1.0):
    """
    [ɑ] short open central unrounded (VERIFIED AGNI)
    v6: AGNI verified parameters (unchanged)
    """
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

def synth_hotaram(pitch_hz=PITCH_HZ, dil=1.0):
    """HOTĀRAM [hoːtaːrɑm] v6 - AGNI parameters restored"""
    segs = [
        synth_H(F_next=VS_OO_F, pitch_hz=pitch_hz, dil=dil),
        synth_OO(F_prev=VS_H_F_APPROX, F_next=VS_T_LOCUS_F, pitch_hz=pitch_hz, dil=dil),
        synth_T(pitch_hz=pitch_hz, dil=dil),
        synth_AA(F_prev=VS_T_LOCUS_F, F_next=VS_R_F, pitch_hz=pitch_hz, dil=dil),
        synth_R(F_prev=VS_AA_F, F_next=VS_A_F, pitch_hz=pitch_hz, dil=dil),
        synth_A(F_prev=VS_R_F, F_next=VS_M_F, pitch_hz=pitch_hz, dil=dil),
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
    print("HOTĀRAM v6 — AGNI parameters restored")
    print("=" * 70)
    print()
    print("ITERATION v5→v6:")
    print("  Diagnosis: Measurement problem, not synthesis")
    print("             AGNI verified [ɑ] F2=1106 Hz with these parameters")
    print("             HOTĀRAM measuring F2=810 Hz with SAME parameters")
    print("             Difference is in diagnostic F2 band boundaries")
    print("  Action: REVERT to AGNI verified parameters")
    print("          NO synthesis changes needed")
    print("          Diagnostic will be fixed separately")
    print()
    print("  VS_AA_F = VS_A_F = [700, 1100, 2550, 3400] Hz")
    print("  VS_AA_B = VS_A_B = [130, 160, 220, 280] Hz")
    print()
    print("  Ancestor: 'The synthesis is correct. Fix the ruler.'")
    print()
    
    word_dry = synth_hotaram(PITCH_HZ, 1.0)
    word_perf = synth_hotaram(PITCH_HZ, 2.5)
    word_slow = ola_stretch(word_dry, 6.0)
    
    write_wav("output_play/hotaram_dry.wav", word_dry)
    write_wav("output_play/hotaram_performance.wav", word_perf)
    write_wav("output_play/hotaram_slow.wav", word_slow)
    
    print()
    print("=" * 70)
    print("v6 synthesis complete.")
    print("Run hotaram_diagnostic.py v2 (fixed measurement bands)")
    print("=" * 70)
    print()
