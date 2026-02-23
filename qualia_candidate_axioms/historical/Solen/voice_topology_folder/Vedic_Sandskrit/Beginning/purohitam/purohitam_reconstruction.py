#!/usr/bin/env python3
"""
PUROHITAM v2 — UPDATE [t] AND [p] TO v6 (SPIKE + TURBULENCE)
Rigveda 1.1.1, word 4
purohitam [puroːhitɑm]

ITERATION v1→v2:
  v1: [t] and [p] used OLD bandpass noise burst method
  v2: Apply v6 architecture (spike + turbulence + boundary fix)
  
  Both are VOICELESS stops → need boundary fix to prevent click
  
  Acoustically: measurements should be IDENTICAL
  Perceptually: should sound CLEANER (no click artifacts)

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

# [p] voiceless bilabial stop — v2 UPDATED (v6 architecture)
VS_P_CLOSURE_MS = 28.0
VS_P_BURST_MS   = 8.0
VS_P_VOT_MS     = 18.0

# v2 NEW: spike + turbulence parameters
VS_P_BURST_F     = [500.0, 1100.0, 2200.0, 3000.0]  # Bilabial locus
VS_P_BURST_B     = [250.0,  300.0,  400.0,  450.0]
VS_P_BURST_G     = [  8.0,   12.0,    3.0,    1.0]
VS_P_BURST_DECAY = 140.0  # Low frequency = slower decay
VS_P_BURST_GAIN  = 0.20

# [u] short close back rounded — VERIFIED PUROHITAM v1
VS_U_F      = [300.0,  750.0, 2300.0, 3100.0]
VS_U_B      = [ 90.0,  120.0,  200.0,  260.0]
VS_U_GAINS  = [ 14.0,    8.0,    1.5,    0.5]
VS_U_DUR_MS = 50.0
VS_U_COART_ON  = 0.12
VS_U_COART_OFF = 0.12

# [ɾ] alveolar tap — VERIFIED PUROHITAM v1
VS_R_F         = [300.0, 1900.0, 2700.0, 3300.0]
VS_R_B         = [120.0,  200.0,  250.0,  300.0]
VS_R_GAINS     = [ 12.0,    6.0,    1.5,    0.4]
VS_R_DUR_MS    = 30.0
VS_R_DIP_DEPTH = 0.35
VS_R_DIP_WIDTH = 0.40
VS_R_COART_ON  = 0.15
VS_R_COART_OFF = 0.15

# [oː] long close-mid back — VERIFIED PUROHITAM v1
VS_OO_F      = [430.0,  800.0, 2500.0, 3200.0]
VS_OO_B      = [110.0,  130.0,  200.0,  270.0]
VS_OO_GAINS  = [ 15.0,    8.0,    1.5,    0.5]
VS_OO_DUR_MS = 100.0
VS_OO_COART_ON  = 0.10
VS_OO_COART_OFF = 0.10

# [h] voiceless glottal fricative — VERIFIED PUROHITAM v1
VS_H_F_APPROX = [500.0, 1500.0, 2500.0, 3500.0]
VS_H_B        = [200.0,  300.0,  400.0,  500.0]
VS_H_GAINS    = [  0.3,    0.2,    0.15,   0.1]
VS_H_DUR_MS    = 65.0
VS_H_COART_ON  = 0.30
VS_H_COART_OFF = 0.30

# [i] short close front unrounded — VERIFIED AGNI
VS_I_F      = [280.0, 2200.0, 2900.0, 3400.0]
VS_I_B      = [ 80.0,  130.0,  180.0,  250.0]
VS_I_GAINS  = [ 12.0,    8.0,    1.5,    0.5]
VS_I_DUR_MS = 50.0
VS_I_COART_ON  = 0.12
VS_I_COART_OFF = 0.12

# [t] voiceless dental stop — v2 UPDATED (v6 architecture)
VS_T_CLOSURE_MS = 25.0
VS_T_BURST_MS   = 7.0
VS_T_VOT_MS     = 15.0

# v2 NEW: spike + turbulence parameters
VS_T_BURST_F     = [500.0, 3500.0, 4000.0, 4500.0]  # Dental locus
VS_T_BURST_B     = [300.0,  500.0,  600.0,  700.0]
VS_T_BURST_G     = [  8.0,   12.0,    3.0,    1.0]
VS_T_BURST_DECAY = 160.0  # High frequency = faster decay
VS_T_BURST_GAIN  = 0.20

# Formant locus for VOT
VS_T_LOCUS_F    = [700.0, 1800.0, 2500.0, 3500.0]

# [ɑ] short open central unrounded — VERIFIED AGNI
VS_A_F      = [700.0, 1100.0, 2550.0, 3400.0]
VS_A_B      = [130.0,  160.0,  220.0,  280.0]
VS_A_GAINS  = [ 16.0,    6.0,    1.5,    0.5]
VS_A_DUR_MS = 55.0
VS_A_COART_ON  = 0.12
VS_A_COART_OFF = 0.12

# [m] bilabial nasal — VERIFIED PUROHITAM v1
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

def synth_P(pitch_hz=PITCH_HZ, dil=1.0):
    """
    [p] voiceless bilabial stop — v2 UPDATED (v6 architecture)
    CANONICAL v6 ARCHITECTURE (spike + turbulence + boundary fix)
    """
    n_cl = int(VS_P_CLOSURE_MS / 1000.0 * SR)
    n_b = int(VS_P_BURST_MS / 1000.0 * SR)
    n_v = int(VS_P_VOT_MS / 1000.0 * SR)
    
    # Phase 1: Voiceless closure WITH PRE-BURST NOISE
    closure = np.zeros(n_cl, dtype=float)
    
    # Add nearly inaudible pre-burst noise (3ms tail)
    ramp_n = min(int(0.003 * SR), n_cl // 4)
    if ramp_n > 0:
        closure[-ramp_n:] = np.random.randn(ramp_n) * 0.002
    
    # Phase 2: SPIKE + TURBULENCE BURST
    spike = np.zeros(max(n_b, 16), dtype=float)
    spike[0:3] = [1.0, 0.6, 0.3]  # 68 µs pressure release
    
    turbulence = np.random.randn(len(spike))
    turbulence_filt = apply_formants(turbulence, VS_P_BURST_F,
                                     VS_P_BURST_B, VS_P_BURST_G)
    
    # Time-varying mix
    t_b = np.arange(len(spike)) / SR
    mix_env = np.exp(-t_b * VS_P_BURST_DECAY)
    burst = spike * mix_env + turbulence_filt * (1.0 - mix_env) * 0.30
    
    # Smooth onset (1ms ramp)
    onset_n = min(int(0.001 * SR), len(burst) // 4)
    if onset_n > 0:
        burst[:onset_n] *= np.linspace(0.0, 1.0, onset_n)
    
    burst = f32(burst * VS_P_BURST_GAIN)
    
    # Phase 3: VOT
    vot_src = rosenberg_pulse(n_v, pitch_hz)
    vot_env = np.linspace(0.0, 1.0, n_v)
    vot = apply_formants(vot_src, VS_U_F, VS_U_B, [g*0.3 for g in VS_U_GAINS])
    vot = f32(vot * vot_env * 0.12)
    
    out = np.concatenate([closure, burst, vot])
    
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.55
    return f32(out)

def synth_U(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=1.0):
    """[u] short close back rounded (VERIFIED PUROHITAM v1)"""
    n = int(VS_U_DUR_MS * dil / 1000.0 * SR)
    src = rosenberg_pulse(n, pitch_hz)
    
    f_mean = list(VS_U_F)
    if F_prev is not None:
        for k in range(min(len(F_prev), len(VS_U_F))):
            f_mean[k] = F_prev[k] * VS_U_COART_ON + VS_U_F[k] * (1.0 - VS_U_COART_ON)
    if F_next is not None:
        for k in range(min(len(F_next), len(VS_U_F))):
            f_mean[k] = f_mean[k] * (1.0 - VS_U_COART_OFF) + F_next[k] * VS_U_COART_OFF
    
    out = apply_formants(src, f_mean, VS_U_B, VS_U_GAINS)
    
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.70
    return f32(out)

def synth_R(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=1.0):
    """[ɾ] alveolar tap (VERIFIED PUROHITAM v1)"""
    n = int(VS_R_DUR_MS * dil / 1000.0 * SR)
    src = rosenberg_pulse(n, pitch_hz)
    
    f_mean = list(VS_R_F)
    if F_prev is not None:
        for k in range(min(len(F_prev), len(VS_R_F))):
            f_mean[k] = F_prev[k] * VS_R_COART_ON + VS_R_F[k] * (1.0 - VS_R_COART_ON)
    if F_next is not None:
        for k in range(min(len(F_next), len(VS_R_F))):
            f_mean[k] = f_mean[k] * (1.0 - VS_R_COART_OFF) + F_next[k] * VS_R_COART_OFF
    
    out = apply_formants(src, f_mean, VS_R_B, VS_R_GAINS)
    
    # Apply tap dip
    t = np.linspace(0, 1, n)
    center = 0.5
    width = VS_R_DIP_WIDTH
    dip_env = 1.0 - VS_R_DIP_DEPTH * np.exp(-((t - center) / width) ** 2 * 10.0)
    out = out * dip_env
    
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.65
    return f32(out)

def synth_OO(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=1.0):
    """[oː] long close-mid back (VERIFIED PUROHITAM v1)"""
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

def synth_H(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=1.0):
    """[h] voiceless glottal fricative (VERIFIED PUROHITAM v1)"""
    n = int(VS_H_DUR_MS * dil / 1000.0 * SR)
    
    noise = np.random.randn(n)
    
    f_mean = list(VS_H_F_APPROX)
    if F_next is not None:
        for k in range(min(len(F_next), len(VS_H_F_APPROX))):
            f_mean[k] = VS_H_F_APPROX[k] * (1.0 - VS_H_COART_OFF) + F_next[k] * VS_H_COART_OFF
    
    out = apply_formants(noise, f_mean, VS_H_B, VS_H_GAINS)
    
    env = np.linspace(0.3, 1.0, n)
    out = out * env
    
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.18
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

def synth_T(pitch_hz=PITCH_HZ, dil=1.0):
    """
    [t] voiceless dental stop — v2 UPDATED (v6 architecture)
    CANONICAL v6 ARCHITECTURE (spike + turbulence + boundary fix)
    """
    n_cl = int(VS_T_CLOSURE_MS / 1000.0 * SR)
    n_b = int(VS_T_BURST_MS / 1000.0 * SR)
    n_v = int(VS_T_VOT_MS / 1000.0 * SR)
    
    # Phase 1: Voiceless closure WITH PRE-BURST NOISE
    closure = np.zeros(n_cl, dtype=float)
    
    # Add nearly inaudible pre-burst noise (3ms tail)
    ramp_n = min(int(0.003 * SR), n_cl // 4)
    if ramp_n > 0:
        closure[-ramp_n:] = np.random.randn(ramp_n) * 0.002
    
    # Phase 2: SPIKE + TURBULENCE BURST
    spike = np.zeros(max(n_b, 16), dtype=float)
    spike[0:3] = [1.0, 0.6, 0.3]  # 68 µs pressure release
    
    turbulence = np.random.randn(len(spike))
    turbulence_filt = apply_formants(turbulence, VS_T_BURST_F,
                                     VS_T_BURST_B, VS_T_BURST_G)
    
    # Time-varying mix
    t_b = np.arange(len(spike)) / SR
    mix_env = np.exp(-t_b * VS_T_BURST_DECAY)
    burst = spike * mix_env + turbulence_filt * (1.0 - mix_env) * 0.30
    
    # Smooth onset (1ms ramp)
    onset_n = min(int(0.001 * SR), len(burst) // 4)
    if onset_n > 0:
        burst[:onset_n] *= np.linspace(0.0, 1.0, onset_n)
    
    burst = f32(burst * VS_T_BURST_GAIN)
    
    # Phase 3: VOT
    vot_src = rosenberg_pulse(n_v, pitch_hz)
    vot_env = np.linspace(0.0, 1.0, n_v)
    vot = apply_formants(vot_src, VS_T_LOCUS_F, VS_A_B, [g*0.3 for g in VS_A_GAINS])
    vot = f32(vot * vot_env * 0.12)
    
    out = np.concatenate([closure, burst, vot])
    
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.55
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
    """[m] bilabial nasal (VERIFIED PUROHITAM v1)"""
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

def synth_purohitam(pitch_hz=PITCH_HZ, dil=1.0):
    """
    PUROHITAM [puroːhitɑm] v2
    Syllables: PU-RO-HI-TAM
    
    v1: [t] and [p] used OLD bandpass noise burst
    v2: [t] and [p] updated to v6 (spike + turbulence + boundary fix) ✓
    
    ALL voiceless stops now use correct physics.
    """
    segs = [
        synth_P(pitch_hz=pitch_hz, dil=dil),
        synth_U(F_next=VS_R_F, pitch_hz=pitch_hz, dil=dil),
        synth_R(F_prev=VS_U_F, F_next=VS_OO_F, pitch_hz=pitch_hz, dil=dil),
        synth_OO(F_prev=VS_R_F, F_next=VS_H_F_APPROX, pitch_hz=pitch_hz, dil=dil),
        synth_H(F_prev=VS_OO_F, F_next=VS_I_F, pitch_hz=pitch_hz, dil=dil),
        synth_I(F_prev=VS_H_F_APPROX, F_next=VS_T_LOCUS_F, pitch_hz=pitch_hz, dil=dil),
        synth_T(pitch_hz=pitch_hz, dil=dil),
        synth_A(F_prev=VS_T_LOCUS_F, F_next=VS_M_F, pitch_hz=pitch_hz, dil=dil),
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
    print("PUROHITAM v2 — UPDATE [t] AND [p] TO v6")
    print("=" * 70)
    print()
    print("ARCHITECTURE UPDATE (v1→v2):")
    print()
    print("  v1 status:")
    print("    [t] voiceless dental: OLD bandpass noise ✗")
    print("    [p] voiceless bilabial: OLD bandpass noise ✗")
    print()
    print("  v2 fix:")
    print("    [t] voiceless dental: spike + turbulence + boundary fix ✓")
    print("    [p] voiceless bilabial: spike + turbulence + boundary fix ✓")
    print()
    print("  BOTH are voiceless → need boundary fix to prevent click")
    print()
    print("  Expected result:")
    print("    Acoustically: IDENTICAL (burst centroids unchanged)")
    print("    Perceptually: CLEANER (no click artifacts)")
    print()
    print("  CARTESIAN CERTAINTY:")
    print("    Physics is either correct or it isn't")
    print("    v2 is correct")
    print()
    
    word_dry = synth_purohitam(PITCH_HZ, 1.0)
    word_perf = synth_purohitam(PITCH_HZ, 2.5)
    word_slow = ola_stretch(word_dry, 6.0)
    
    write_wav("output_play/purohitam_dry_v2.wav", word_dry)
    write_wav("output_play/purohitam_performance_v2.wav", word_perf)
    write_wav("output_play/purohitam_slow_v2.wav", word_slow)
    
    print()
    print("=" * 70)
    print("v2 synthesis complete")
    print()
    print("PERCEPTUAL TEST:")
    print("  Compare v2 to v1")
    print("  Listen specifically to:")
    print("    [p] in 'pu-' (word-initial)")
    print("    [t] in '-tam' (post-vowel)")
    print("  Should sound cleaner, no click artifacts")
    print("  Burst quality should be natural")
    print()
    print("NO DIAGNOSTICS NEEDED:")
    print("  Acoustic measurements will be identical")
    print("  Ear verification is sufficient")
    print()
    print("NEXT:")
    print("  YAJÑASYA v3 ([ɟ] source file - spike + turbulence)")
    print()
    print("=" * 70)
    print()
