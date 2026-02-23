#!/usr/bin/env python3
"""RATNADHĀTAMAM v5 — Following DEVAM template"""

import numpy as np
from scipy.signal import lfilter, butter
import wave as wave_module
import os

SR = 44100
DTYPE = np.float32
os.makedirs("output_play", exist_ok=True)

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
VS_DH_BURST_GAIN = 0.28
VS_DH_MURMUR_MS = 50.0
VS_DH_MURMUR_GAIN = 0.35

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
    win_n = int(win_ms / 1000.0 * SR)
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
    n = int(VS_A_DUR_MS * dil / 1000.0 * SR)
    src = rosenberg_pulse(n, pitch_hz)
    out = apply_formants(src, VS_A_F, VS_A_B, VS_A_GAINS)
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.72
    return f32(out)

def synth_T(pitch_hz=PITCH_HZ, dil=1.0):
    n_cl = int(VS_T_CLOSURE_MS / 1000.0 * SR)
    n_b = int(VS_T_BURST_MS / 1000.0 * SR)
    n_v = int(VS_T_VOT_MS / 1000.0 * SR)
    closure = np.zeros(n_cl, dtype=DTYPE)
    b_, a_ = butter(2, [VS_T_BURST_F - VS_T_BURST_BW/2, VS_T_BURST_F + VS_T_BURST_BW/2], btype='band', fs=SR)
    burst_noise = np.random.randn(max(n_b, 4))
    burst = lfilter(b_, a_, burst_noise)
    if len(burst) > 1:
        burst = burst * np.hanning(len(burst))  # ← HANNING
    burst = f32(burst * VS_T_BURST_GAIN)
    vot_src = rosenberg_pulse(n_v, pitch_hz)
    vot_env = np.linspace(0.0, 1.0, n_v)  # ← RAMP
    vot = apply_formants(vot_src, VS_A_F, VS_A_B, [g*0.3 for g in VS_A_GAINS])
    vot = f32(vot * vot_env * 0.12)
    out = np.concatenate([closure, burst, vot])
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.55
    return f32(out)

def synth_N(pitch_hz=PITCH_HZ, dil=1.0):
    n = int(VS_N_DUR_MS * dil / 1000.0 * SR)
    src = rosenberg_pulse(n, pitch_hz)
    out = apply_formants(src, VS_N_F, VS_N_B, VS_N_GAINS)
    out = iir_notch(out, VS_N_ANTI_F, 200.0)
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.42
    return f32(out)

def synth_DH(pitch_hz=PITCH_HZ, dil=1.0):
    """v5: DEVAM template for voiced aspirated stop"""
    n_cl = int(VS_DH_CLOSURE_MS / 1000.0 * SR)
    n_b = int(VS_DH_BURST_MS / 1000.0 * SR)
    n_m = int(VS_DH_MURMUR_MS * dil / 1000.0 * SR)
    
    # Phase 1: Voiced closure (like [d])
    src_cl = rosenberg_pulse(n_cl, pitch_hz, oq=0.65)
    b_lp, a_lp = butter(2, 500.0 / (SR/2.0), btype='low')
    murmur_cl = lfilter(b_lp, a_lp, src_cl.astype(float))
    closure = f32(murmur_cl * 0.70)
    
    # Phase 2: Burst (like [d])
    burst_noise = np.random.randn(max(n_b, 4))
    b_bp, a_bp = butter(2, [VS_DH_BURST_F - VS_DH_BURST_BW/2, VS_DH_BURST_F + VS_DH_BURST_BW/2], btype='band', fs=SR)
    burst = lfilter(b_bp, a_bp, burst_noise)
    if len(burst) > 1:
        burst = burst * np.hanning(len(burst))  # ← HANNING
    burst = f32(burst * VS_DH_BURST_GAIN)
    
    # Phase 3: BREATHY MURMUR (like [d] VOT but breathy + longer)
    # Source: Rosenberg at lower OQ + noise
    murmur_periodic = rosenberg_pulse(n_m, pitch_hz, oq=0.45)  # Lower OQ
    murmur_noise = np.random.randn(n_m) * 0.5  # 50% noise
    murmur_src = murmur_periodic + murmur_noise
    
    # Ramp envelope (like VOT)
    murmur_env = np.linspace(0.0, 1.0, n_m)
    
    # Apply formants with WIDE bandwidths
    murmur_bws = [bw * 3.5 for bw in VS_AA_B]
    murmur = apply_formants(murmur_src, VS_AA_F, murmur_bws, [g*0.6 for g in VS_AA_GAINS])
    murmur = f32(murmur * murmur_env * VS_DH_MURMUR_GAIN)
    
    out = np.concatenate([closure, burst, murmur])
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.55
    return f32(out)

def synth_AA(pitch_hz=PITCH_HZ, dil=1.0):
    n = int(VS_AA_DUR_MS * dil / 1000.0 * SR)
    src = rosenberg_pulse(n, pitch_hz)
    out = apply_formants(src, VS_AA_F, VS_AA_B, VS_AA_GAINS)
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.72
    return f32(out)

def synth_M(pitch_hz=PITCH_HZ, dil=1.0):
    n = int(VS_M_DUR_MS * dil / 1000.0 * SR)
    src = rosenberg_pulse(n, pitch_hz)
    out = apply_formants(src, VS_M_F, VS_M_B, VS_M_GAINS)
    out = iir_notch(out, VS_M_ANTI_F, 200.0)
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.42
    return f32(out)

def synth_ratnadhatamam(pitch_hz=PITCH_HZ, dil=1.0):
    segs = [
        synth_R(pitch_hz, dil), synth_A(pitch_hz, dil), synth_T(pitch_hz, dil),
        synth_N(pitch_hz, dil), synth_A(pitch_hz, dil), synth_DH(pitch_hz, dil),
        synth_AA(pitch_hz, dil), synth_T(pitch_hz, dil), synth_A(pitch_hz, dil),
        synth_M(pitch_hz, dil), synth_A(pitch_hz, dil), synth_M(pitch_hz, dil)
    ]
    word = np.concatenate(segs)
    mx = np.max(np.abs(word))
    if mx > 1e-8:
        word = word / mx * 0.75
    return f32(word)

if __name__ == "__main__":
    print("RATNADHĀTAMAM v5 (DEVAM template)")
    word_dry = synth_ratnadhatamam(PITCH_HZ, 1.0)
    word_slow = ola_stretch(word_dry, 6.0)
    write_wav("output_play/ratnadhatamam_dry.wav", word_dry)
    write_wav("output_play/ratnadhatamam_slow.wav", word_slow)
    print("v5 complete. Run diagnostic.")
