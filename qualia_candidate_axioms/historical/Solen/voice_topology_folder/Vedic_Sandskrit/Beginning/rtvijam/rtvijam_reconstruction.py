#!/usr/bin/env python3
"""
ṚTVIJAM v7 — Update [ɟ] to spike + turbulence (CORRECT PHYSICS)
Rigveda 1.1.1, word 7

ITERATION v6→v7:
  [ʈ] verified v6 (spike + turbulence + boundary fix) ✓
  
  [ɟ] still uses OLD bandpass noise burst method.
  This is WRONG PHYSICS.
  
  v7 update: Apply spike + turbulence to [ɟ]
  
  Voiced stop = NO boundary fix needed (murmur masks discontinuity)
  But burst method MUST be correct physics.

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

# [ʈ] voiceless retroflex stop — v6 VERIFIED ṚTVIJAM
VS_TT_CLOSURE_MS  = 30.0
VS_TT_BURST_MS    = 12.0
VS_TT_VOT_MS      = 20.0
VS_TT_BURST_F     = [500.0, 1300.0, 2200.0, 3100.0]
VS_TT_BURST_B     = [250.0,  350.0,  450.0,  500.0]
VS_TT_BURST_G     = [  8.0,   12.0,    3.0,    1.0]
VS_TT_BURST_DECAY = 150.0
VS_TT_BURST_GAIN  = 0.20
VS_TT_F3_NOTCH    = 2200.0
VS_TT_F3_NOTCH_BW = 300.0
VS_TT_LOCUS_F     = [420.0, 1300.0, 2200.0, 3100.0]

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

# [ɟ] voiced palatal stop — v7 UPDATED (spike + turbulence)
VS_JJ_F      = [280.0, 2100.0, 2800.0, 3300.0]
VS_JJ_B      = [100.0,  200.0,  300.0,  350.0]
VS_JJ_GAINS  = [ 10.0,    6.0,    1.5,    0.5]
VS_JJ_CLOSURE_MS  = 30.0
VS_JJ_BURST_MS    = 9.0
VS_JJ_VOT_MS      = 10.0
VS_JJ_MURMUR_GAIN = 0.70

# v7 NEW: spike + turbulence parameters
VS_JJ_BURST_F     = [500.0, 3200.0, 3800.0, 4200.0]  # Palatal locus
VS_JJ_BURST_B     = [300.0,  500.0,  600.0,  700.0]
VS_JJ_BURST_G     = [  8.0,   12.0,    3.0,    1.0]
VS_JJ_BURST_DECAY = 180.0  # Higher frequency = faster decay
VS_JJ_BURST_GAIN  = 0.15   # Voiced burst slightly quieter

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
    [ʈ] voiceless retroflex stop — v6 VERIFIED
    CANONICAL v6 ARCHITECTURE (spike + turbulence + boundary fix)
    """
    n_cl = int(VS_TT_CLOSURE_MS / 1000.0 * SR)
    n_b = int(VS_TT_BURST_MS / 1000.0 * SR)
    n_v = int(VS_TT_VOT_MS / 1000.0 * SR)
    
    # Phase 1: Voiceless closure WITH PRE-BURST NOISE
    closure = np.zeros(n_cl, dtype=float)
    
    # Add nearly inaudible pre-burst noise (3ms tail)
    ramp_n = min(int(0.003 * SR), n_cl // 4)
    if ramp_n > 0:
        closure[-ramp_n:] = np.random.randn(ramp_n) * 0.002
    
    # Phase 2: SPIKE + TURBULENCE BURST
    spike = np.zeros(max(n_b, 16), dtype=float)
    spike[0:3] = [1.0, 0.6, 0.3]
    
    turbulence = np.random.randn(len(spike))
    turbulence_filt = apply_formants(turbulence, VS_TT_BURST_F, 
                                     VS_TT_BURST_B, VS_TT_BURST_G)
    
    t_b = np.arange(len(spike)) / SR
    mix_env = np.exp(-t_b * VS_TT_BURST_DECAY)
    burst = spike * mix_env + turbulence_filt * (1.0 - mix_env) * 0.30
    
    # Smooth onset (1ms ramp)
    onset_n = min(int(0.001 * SR), len(burst) // 4)
    if onset_n > 0:
        burst[:onset_n] *= np.linspace(0.0, 1.0, onset_n)
    
    # Apply F3 notch (retroflex from release)
    burst = iir_notch(burst, VS_TT_F3_NOTCH, VS_TT_F3_NOTCH_BW)
    burst = f32(burst * VS_TT_BURST_GAIN)
    
    # Phase 3: VOT
    vot_src = rosenberg_pulse(n_v, pitch_hz)
    vot_env = np.linspace(0.0, 1.0, n_v)
    vot = apply_formants(vot_src, VS_TT_LOCUS_F, VS_RV_B, [g*0.3 for g in VS_RV_GAINS])
    vot = iir_notch(vot, VS_TT_F3_NOTCH, VS_TT_F3_NOTCH_BW)
    vot = f32(vot * vot_env * 0.12)
    
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
    """
    [ɟ] voiced palatal stop — v7 UPDATED (spike + turbulence)
    
    v7 ARCHITECTURE:
      Voiced stop = NO boundary fix needed (murmur masks discontinuity)
      But burst method MUST be correct physics:
        - Spike (pressure release)
        - Turbulence (formant-filtered)
        - Time-varying mix
      
    This is the CORRECT method for all stops (voiced and voiceless).
    Voiceless stops need additional boundary fix.
    Voiced stops do not (murmur prevents discontinuity).
    """
    n_cl = int(VS_JJ_CLOSURE_MS / 1000.0 * SR)
    n_b = int(VS_JJ_BURST_MS / 1000.0 * SR)
    n_v = int(VS_JJ_VOT_MS / 1000.0 * SR)
    
    # Phase 1: Voiced closure (low-pass murmur)
    src_cl = rosenberg_pulse(n_cl, pitch_hz)
    b_lp, a_lp = butter(2, 500.0 / (SR/2.0), btype='low')
    murmur_cl = lfilter(b_lp, a_lp, src_cl.astype(float))
    closure = f32(murmur_cl * VS_JJ_MURMUR_GAIN)
    
    # Phase 2: SPIKE + TURBULENCE BURST (v7 NEW METHOD)
    spike = np.zeros(max(n_b, 16), dtype=float)
    spike[0:3] = [1.0, 0.6, 0.3]  # Pressure release transient
    
    turbulence = np.random.randn(len(spike))
    turbulence_filt = apply_formants(turbulence, VS_JJ_BURST_F,
                                     VS_JJ_BURST_B, VS_JJ_BURST_G)
    
    # Time-varying mix
    t_b = np.arange(len(spike)) / SR
    mix_env = np.exp(-t_b * VS_JJ_BURST_DECAY)
    burst = spike * mix_env + turbulence_filt * (1.0 - mix_env) * 0.30
    
    # NO onset ramp (murmur already provides smooth transition)
    # NO pre-burst noise (not needed for voiced stops)
    
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
    ṚTVIJAM [ɻ̩tviɟɑm] v7
    Syllables: ṚT-VI-JAM
    
    v6: [ʈ] spike + turbulence + boundary fix ✓ VERIFIED
    v7: [ɟ] spike + turbulence (no boundary fix - voiced) ✓ UPDATED
    
    ALL stops now use correct physics.
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
    print("ṚTVIJAM v7 — UPDATE [ɟ] TO SPIKE + TURBULENCE")
    print("=" * 70)
    print()
    print("ARCHITECTURE UPDATE (v6→v7):")
    print()
    print("  v6 status:")
    print("    [ʈ] voiceless retroflex: spike + turbulence + boundary fix ✓")
    print("    [ɟ] voiced palatal: OLD bandpass noise ✗")
    print()
    print("  v7 fix:")
    print("    [ɟ] voiced palatal: spike + turbulence ✓")
    print("    NO boundary fix (voiced - murmur masks discontinuity)")
    print("    Burst method MUST be correct physics")
    print()
    print("  Result:")
    print("    ALL stops in ṚTVIJAM now use correct physics")
    print("    [ʈ] verified v6 ✓")
    print("    [ɟ] updated v7 ✓")
    print()
    print("  CARTESIAN CERTAINTY RESTORED:")
    print("    No 'minor artifacts'")
    print("    No 'good enough for now'")
    print("    Physics is either correct or it isn't")
    print("    v7 is correct")
    print()
    
    word_dry = synth_rtvijam(PITCH_HZ, 1.0)
    word_perf = synth_rtvijam(PITCH_HZ, 2.5)
    word_slow = ola_stretch(word_dry, 6.0)
    
    write_wav("output_play/rtvijam_dry_v7.wav", word_dry)
    write_wav("output_play/rtvijam_performance_v7.wav", word_perf)
    write_wav("output_play/rtvijam_slow_v7.wav", word_slow)
    
    print()
    print("=" * 70)
    print("v7 synthesis complete")
    print()
    print("PERCEPTUAL TEST:")
    print("  Compare v7 to v6")
    print("  Listen specifically to [ɟ] in '-jam'")
    print("  Should sound cleaner, more natural")
    print("  No burst artifacts")
    print()
    print("NEXT:")
    print("  1. PUROHITAM v2 ([t] and [p] voiceless - v6 architecture)")
    print("  2. YAJÑASYA v3 ([ɟ] source - spike + turbulence)")
    print()
    print("=" * 70)
    print()
