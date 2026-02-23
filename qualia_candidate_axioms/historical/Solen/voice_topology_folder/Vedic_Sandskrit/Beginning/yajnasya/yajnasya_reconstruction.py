#!/usr/bin/env python3
"""
YAJÑASYA RECONSTRUCTION v3
Vedic Sanskrit: yajñasya  [jɑɟɲɑsjɑ]
Rigveda 1.1.1 — word 4

ARCHITECTURE UPDATE v1→v3:
  v1: [ɟ] used OLD bandpass noise burst
  v3: [ɟ] uses v7 (spike + turbulence, no boundary fix)
  
  REFERENCE: [ɟ] ṚTVIJAM v7 (3223 Hz verified)
  
  v7 architecture for voiced stops:
    - Voiced closure murmur (low-pass filtered Rosenberg)
    - Spike + turbulence burst (correct physics)
    - NO boundary fix (murmur masks transition)
    - Voiced VOT into following phoneme
  
  Target: preserve v1 burst centroid (~3223 Hz) while
  using correct physical model.

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

# [j] voiced palatal approximant — UNCHANGED from v1
VS_J_F         = [280.0, 2100.0, 2800.0, 3300.0]
VS_J_B         = [100.0,  200.0,  300.0,  350.0]
VS_J_GAINS     = [ 10.0,    6.0,    1.5,    0.5]
VS_J_DUR_MS    = 55.0
VS_J_COART_ON  = 0.18
VS_J_COART_OFF = 0.18

# [ɟ] voiced palatal stop — v3 UPDATED (v7 architecture)
VS_JJ_CLOSURE_MS  = 30.0
VS_JJ_BURST_MS    = 9.0
VS_JJ_VOT_MS      = 10.0
VS_JJ_MURMUR_GAIN = 0.70

# v3 NEW: spike + turbulence parameters (from ṚTVIJAM v7)
VS_JJ_BURST_F     = [500.0, 3200.0, 3800.0, 4200.0]  # Palatal locus
VS_JJ_BURST_B     = [300.0,  500.0,  600.0,  700.0]
VS_JJ_BURST_G     = [  8.0,   12.0,    3.0,    1.0]  # F2 dominant
VS_JJ_BURST_DECAY = 180.0  # Higher frequency = faster decay
VS_JJ_BURST_GAIN  = 0.15   # Voiced burst (quieter than voiceless)

# [ɲ] voiced palatal nasal — UNCHANGED from v1
VS_NY_F        = [250.0, 2000.0, 2800.0, 3300.0]
VS_NY_B        = [120.0,  180.0,  250.0,  300.0]
VS_NY_GAINS    = [  8.0,    4.0,    1.2,    0.4]
VS_NY_DUR_MS   = 65.0
VS_NY_ANTI_F   = 1200.0
VS_NY_ANTI_BW  = 250.0
VS_NY_COART_ON  = 0.15
VS_NY_COART_OFF = 0.15

# [s] voiceless dental sibilant — UNCHANGED from v1
VS_S_NOISE_CF  = 7500.0
VS_S_NOISE_BW  = 3000.0
VS_S_GAIN      = 0.22
VS_S_DUR_MS    = 80.0

# [ɑ] short open central — VS-verified AGNI
VS_A_F     = [700.0, 1100.0, 2550.0, 3400.0]
VS_A_B     = [130.0,  160.0,  220.0,  280.0]
VS_A_GAINS = [ 16.0,    6.0,    1.5,    0.5]
VS_A_DUR_MS = 55.0
VS_A_COART = 0.12

PITCH_HZ = 120.0
DIL = 1.0

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

def synth_J(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=1.0):
    """[j] voiced palatal approximant (UNCHANGED from v1)"""
    n = int(VS_J_DUR_MS * dil / 1000.0 * SR)
    src = rosenberg_pulse(n, pitch_hz)
    
    f_mean = list(VS_J_F)
    if F_prev is not None:
        for k in range(min(len(F_prev), len(VS_J_F))):
            f_mean[k] = F_prev[k] * VS_J_COART_ON + VS_J_F[k] * (1.0 - VS_J_COART_ON)
    if F_next is not None:
        for k in range(min(len(F_next), len(VS_J_F))):
            f_mean[k] = f_mean[k] * (1.0 - VS_J_COART_OFF) + F_next[k] * VS_J_COART_OFF
    
    out = apply_formants(src, f_mean, VS_J_B, VS_J_GAINS)
    
    # Smooth envelope (no dip - distinguishes from tap)
    env = np.ones(n, dtype=float)
    atk = min(int(0.012 * SR), n // 4)
    rel = min(int(0.012 * SR), n // 4)
    if atk > 0:
        env[:atk] = np.linspace(0.0, 1.0, atk)
    if rel > 0:
        env[-rel:] = np.linspace(1.0, 0.0, rel)
    out = f32(out * env)
    
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.65
    return f32(out)

def synth_JJ(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=1.0):
    """
    [ɟ] voiced palatal stop — v3 UPDATED (v7 architecture)
    
    CANONICAL v7 ARCHITECTURE (spike + turbulence, no boundary fix)
    Based on ṚTVIJAM [ɟ] v7 verified implementation
    
    Voiced stop = NO boundary fix needed (murmur masks discontinuity)
    But burst method MUST be correct physics:
      - Spike (pressure release)
      - Turbulence (formant-filtered)
      - Time-varying mix
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
    
    # Use following phoneme formants if available
    f_vot = F_next if F_next is not None else VS_NY_F
    vot = apply_formants(vot_src, f_vot, 
                        [100, 200, 300, 350],
                        [g*0.4 for g in [10, 6, 1.5, 0.5]])
    vot = f32(vot * vot_env * 0.15)
    
    out = np.concatenate([closure, burst, vot])
    
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.60
    return f32(out)

def synth_NY(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=1.0):
    """[ɲ] voiced palatal nasal (UNCHANGED from v1)"""
    n = int(VS_NY_DUR_MS * dil / 1000.0 * SR)
    src = rosenberg_pulse(n, pitch_hz)
    
    f_mean = list(VS_NY_F)
    if F_prev is not None:
        for k in range(min(len(F_prev), len(VS_NY_F))):
            f_mean[k] = F_prev[k] * VS_NY_COART_ON + VS_NY_F[k] * (1.0 - VS_NY_COART_ON)
    if F_next is not None:
        for k in range(min(len(F_next), len(VS_NY_F))):
            f_mean[k] = f_mean[k] * (1.0 - VS_NY_COART_OFF) + F_next[k] * VS_NY_COART_OFF
    
    out = apply_formants(src, f_mean, VS_NY_B, VS_NY_GAINS)
    out = iir_notch(out, VS_NY_ANTI_F, VS_NY_ANTI_BW)
    
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.42
    return f32(out)

def synth_S(F_prev=None, F_next=None, dil=1.0):
    """[s] voiceless dental sibilant (UNCHANGED from v1)"""
    n = int(VS_S_DUR_MS * dil / 1000.0 * SR)
    
    noise = np.random.randn(n)
    
    # Bandpass filter
    lo = max(VS_S_NOISE_CF - VS_S_NOISE_BW / 2, 20.0)
    hi = min(VS_S_NOISE_CF + VS_S_NOISE_BW / 2, SR/2.0 - 20.0)
    
    if lo < hi:
        b_bp, a_bp = butter(2, [lo / (SR/2.0), hi / (SR/2.0)], btype='band')
        out = lfilter(b_bp, a_bp, noise.astype(float))
    else:
        out = noise
    
    # Amplitude envelope
    atk = min(int(0.010 * SR), n // 4)
    rel = min(int(0.015 * SR), n // 4)
    env = np.ones(n, dtype=float)
    if atk > 0:
        env[:atk] = np.linspace(0.0, 1.0, atk)
    if rel > 0:
        env[-rel:] = np.linspace(1.0, 0.0, rel)
    out = out * env * VS_S_GAIN
    
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.42
    return f32(out)

def synth_A_vs(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=1.0):
    """[ɑ] short open central (VS-verified AGNI)"""
    n = int(VS_A_DUR_MS * dil / 1000.0 * SR)
    src = rosenberg_pulse(n, pitch_hz)
    
    f_mean = list(VS_A_F)
    if F_prev is not None:
        for k in range(min(len(F_prev), len(VS_A_F))):
            f_mean[k] = F_prev[k] * VS_A_COART + VS_A_F[k] * (1.0 - VS_A_COART)
    if F_next is not None:
        for k in range(min(len(F_next), len(VS_A_F))):
            f_mean[k] = f_mean[k] * (1.0 - VS_A_COART) + F_next[k] * VS_A_COART
    
    out = apply_formants(src, f_mean, VS_A_B, VS_A_GAINS)
    
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.72
    return f32(out)

# ============================================================================
# ROOM SIMULATION
# ============================================================================

def apply_simple_room(sig, rt60=1.5, direct_ratio=0.55, sr=SR):
    n_rev = int(rt60 * sr)
    ir = np.zeros(n_rev, dtype=float)
    ir[0] = 1.0
    decay = np.exp(-6.908 * np.arange(n_rev) / (rt60 * sr))
    noise_ir = np.random.randn(n_rev) * decay
    ir = direct_ratio * ir + (1.0 - direct_ratio) * noise_ir
    ir = ir / (np.max(np.abs(ir)) + 1e-12)
    out = np.convolve(sig.astype(float), ir[:min(n_rev, 4096)])
    out = out[:len(sig)]
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.75
    return f32(out)

# ============================================================================
# WORD SYNTHESIS
# ============================================================================

def synth_yajnasya(pitch_hz=PITCH_HZ, dil=1.0, with_room=False):
    """
    YAJÑASYA [jɑɟɲɑsjɑ] v3
    
    v1: [ɟ] bandpass noise burst ✓ VERIFIED
    v3: [ɟ] v7 spike + turbulence ✓ UPDATED
    
    ALL voiced stops now use correct physics.
    """
    segs = [
        synth_J(F_next=VS_A_F, pitch_hz=pitch_hz, dil=dil),
        synth_A_vs(F_prev=VS_J_F, F_next=VS_JJ_BURST_F, pitch_hz=pitch_hz, dil=dil),
        synth_JJ(F_prev=VS_A_F, F_next=VS_NY_F, pitch_hz=pitch_hz, dil=dil),
        synth_NY(F_prev=VS_JJ_BURST_F, F_next=VS_A_F, pitch_hz=pitch_hz, dil=dil),
        synth_A_vs(F_prev=VS_NY_F, pitch_hz=pitch_hz, dil=dil),
        synth_S(dil=dil),
        synth_J(F_next=VS_A_F, pitch_hz=pitch_hz, dil=dil),
        synth_A_vs(F_prev=VS_J_F, pitch_hz=pitch_hz, dil=dil),
    ]
    
    word = np.concatenate(segs)
    mx = np.max(np.abs(word))
    if mx > 1e-8:
        word = word / mx * 0.75
    
    if with_room:
        word = apply_simple_room(word, rt60=1.5, direct_ratio=0.55)
    
    return f32(word)

# Expose for diagnostic
VS_JJ_BURST_F_VAL = VS_JJ_BURST_F[1]  # F2 frequency for reference
VS_S_NOISE_CF_VAL = VS_S_NOISE_CF

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print()
    print("=" * 70)
    print("YAJÑASYA v3 — UPDATE [ɟ] TO v7")
    print("=" * 70)
    print()
    print("ARCHITECTURE UPDATE (v1→v3):")
    print()
    print("  v1 status:")
    print("    [ɟ] voiced palatal: OLD bandpass noise ✗")
    print()
    print("  v3 fix:")
    print("    [ɟ] voiced palatal: spike + turbulence ✓")
    print("    NO boundary fix (voiced - murmur masks discontinuity)")
    print("    Burst method MUST be correct physics")
    print()
    print("  Reference:")
    print("    [ɟ] ṚTVIJAM v7 (3223 Hz verified)")
    print()
    print("  Result:")
    print("    [ɟ] now uses correct v7 architecture")
    print("    All other phonemes unchanged")
    print()
    
    word_dry = synth_yajnasya(PITCH_HZ, 1.0, with_room=False)
    word_perf = synth_yajnasya(PITCH_HZ, 2.5, with_room=False)
    word_slow = ola_stretch(word_dry, 6.0)
    
    write_wav("output_play/yajnasya_dry_v3.wav", word_dry)
    write_wav("output_play/yajnasya_performance_v3.wav", word_perf)
    write_wav("output_play/yajnasya_slow_v3.wav", word_slow)
    
    print()
    print("=" * 70)
    print("v3 synthesis complete")
    print()
    print("DIAGNOSTIC:")
    print("  Run: python yajnasya_diagnostic_v3.py")
    print()
    print("EXPECTED RESULT:")
    print("  [ɟ] burst centroid: ~3223 Hz ± 100 Hz (v1 reference)")
    print("  Perceptual: cleaner (correct physics)")
    print()
    print("=" * 70)
    print()
