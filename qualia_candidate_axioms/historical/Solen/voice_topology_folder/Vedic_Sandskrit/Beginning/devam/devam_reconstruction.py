"""
DEVAM RECONSTRUCTION v13
Vedic Sanskrit: devam  [devɑm]
Rigveda 1.1.1 — word 5
February 2026

v13 UPDATE (CUTBACK ENERGY REDUCTION):
  v12: sounds like [d], 14/14 passed. Crossfade architecture correct.
  But: too much energy in middle-to-end of [d] articulation.
  The closed-tract signal at peak 0.70 is too loud.
  Equal-power crossfade sums to ~1.0 in the middle = energy bump.
  
  v13 fix:
    1. sig_closed peak: 0.70 → 0.40 (muffled = quieter)
    2. sig_open peak: 0.70 → 0.65 (vowel is louder than closed tract)
    3. Cutback overall peak: 0.60 → 0.55
    4. cb_env ramp: 0.5→1.0 changed to 0.6→1.0 (less dramatic ramp)
    
  Physics: the closed tract ATTENUATES sound. It should be quieter
  than the open tract, not equal. When the tongue releases, amplitude
  INCREASES as the tract opens. The crossfade should reflect this:
  quiet closed → louder open. Not equal → equal.

  All other phonemes UNCHANGED.
"""

import numpy as np
from scipy.signal import lfilter, butter
import wave as wave_module
import os

SR    = 44100
DTYPE = np.float32

os.makedirs("output_play", exist_ok=True)

NEUTRAL_ALVEOLAR_F3_HZ = 2700.0
DANTYA_BURST_LO_HZ     = 3000.0
DANTYA_BURST_HI_HZ     = 4500.0

VS_T_BURST_HZ    = 3764.0
VS_G_BURST_HZ    = 2594.0
VS_P_BURST_HZ    = 1204.0
VS_JJ_BURST_HZ   = 3223.0
VS_M_F2_HZ       =  552.0
VS_N_F2_HZ       =  900.0
VS_J_F2_HZ       = 2028.0

VS_EE_F          = [420.0, 1750.0, 2650.0, 3350.0]
VS_EE_B          = [100.0,  140.0,  200.0,  260.0]
VS_EE_GAINS      = [ 14.0,    8.0,    1.5,    0.5]
VS_EE_DUR_MS     = 90.0

VS_A_F           = [700.0, 1100.0, 2550.0, 3400.0]
VS_A_B           = [130.0,  160.0,  220.0,  280.0]
VS_A_GAINS       = [ 16.0,    6.0,    1.5,    0.5]
VS_A_DUR_MS      = 55.0

VS_M_F           = [250.0,  900.0, 2200.0, 3000.0]
VS_M_B           = [100.0,  200.0,  300.0,  350.0]
VS_M_GAINS       = [  8.0,    2.5,    0.5,    0.2]
VS_M_DUR_MS      = 60.0
VS_M_ANTI_F      = 800.0
VS_M_ANTI_BW     = 200.0

# ── [d] v13 — CUTBACK ENERGY FIX ─────────────────────

VS_D_CLOSURE_MS    = 20.0
VS_D_BURST_MS      = 8.0
VS_D_CUTBACK_MS    = 30.0

VS_D_VOICEBAR_F    = 250.0
VS_D_VOICEBAR_BW   = 80.0
VS_D_VOICEBAR_G    = 12.0

VS_D_MURMUR_PEAK   = 0.25
VS_D_BURST_PEAK    = 0.15

# v13: closed tract is QUIETER than open tract
VS_D_CLOSED_F      = [250.0,  800.0, 2200.0, 3200.0]
VS_D_CLOSED_B      = [150.0,  250.0,  300.0,  350.0]
VS_D_CLOSED_G      = [ 10.0,    3.0,    0.8,    0.3]
VS_D_CLOSED_PEAK   = 0.40      # v13: was 0.70 — closed tract attenuates
VS_D_OPEN_PEAK     = 0.65      # v13: was 0.70 — open tract is louder
VS_D_CUTBACK_PEAK  = 0.55      # v13: was 0.60

VS_D_BURST_F     = [1500.0, 3500.0, 5000.0, 6500.0]
VS_D_BURST_B     = [ 400.0,  600.0,  800.0, 1000.0]
VS_D_BURST_G     = [   4.0,   12.0,    5.0,    1.5]
VS_D_BURST_DECAY = 170.0

VS_V_F           = [300.0, 1500.0, 2400.0, 3100.0]
VS_V_B           = [180.0,  350.0,  400.0,  400.0]
VS_V_GAINS       = [ 10.0,    5.0,    1.5,    0.5]
VS_V_DUR_MS      = 60.0
VS_V_COART_ON    = 0.18
VS_V_COART_OFF   = 0.18

PITCH_HZ = 120.0
DIL      = 1.0


def f32(x):
    return np.asarray(x, dtype=DTYPE)

def rms(sig):
    return float(np.sqrt(np.mean(sig.astype(float) ** 2)))

def write_wav(path, sig, sr=SR):
    sig_i = np.clip(sig * 32767.0, -32768, 32767).astype(np.int16)
    with wave_module.open(path, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(sig_i.tobytes())

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
    for f0, bw, g in zip(freqs, bws, gains):
        if f0 <= 0 or f0 >= nyq:
            continue
        r = np.exp(-np.pi * bw / sr)
        cosf = 2.0 * np.cos(2.0 * np.pi * f0 / sr)
        a = [1.0, -r * cosf, r * r]
        b = [g]
        filt = lfilter(b, a, src.astype(float))
        out += filt
    return f32(out)

def iir_notch(sig, fc, bw=200.0, sr=SR):
    w0 = 2.0 * np.pi * fc / sr
    r = max(0.0, min(0.999, 1.0 - np.pi * bw / sr))
    b_n = [1.0, -2.0 * np.cos(w0), 1.0]
    a_n = [1.0, -2.0 * r * np.cos(w0), r * r]
    return f32(lfilter(b_n, a_n, sig.astype(float)))

def norm_to_peak(sig, target_peak):
    mx = np.max(np.abs(sig))
    if mx > 1e-10:
        return f32(sig * (target_peak / mx))
    return f32(sig)


def synth_D(F_prev=None, F_next=None, dil=DIL, sr=SR):
    """
    [d] — voiced dental stop — v13 (cutback energy fix).
    
    v12 crossfade architecture + reduced closed-tract energy.
    Closed tract is QUIETER than open tract (physics: closure attenuates).
    """
    n_closure = int(VS_D_CLOSURE_MS * dil / 1000.0 * sr)
    n_burst = int(VS_D_BURST_MS * dil / 1000.0 * sr)
    n_cutback = int(VS_D_CUTBACK_MS * dil / 1000.0 * sr)

    f_next = F_next if F_next is not None else VS_EE_F

    # Phase 1: brief prevoicing — voice bar
    if n_closure > 0:
        src_cl = rosenberg_pulse(n_closure, PITCH_HZ, sr=sr)
        murmur = apply_formants(
            src_cl,
            [VS_D_VOICEBAR_F],
            [VS_D_VOICEBAR_BW],
            [VS_D_VOICEBAR_G],
            sr=sr)
        env_cl = np.ones(n_closure, dtype=float)
        ramp_n = max(1, int(0.3 * n_closure))
        env_cl[:ramp_n] = np.linspace(0.3, 1.0, ramp_n)
        murmur = f32(murmur * env_cl)
        closure = norm_to_peak(murmur, VS_D_MURMUR_PEAK)
    else:
        closure = np.array([], dtype=DTYPE)

    # Phase 2: burst at dental locus
    spike = np.zeros(max(n_burst, 16), dtype=float)
    spike[0:3] = [1.0, 0.6, 0.3]
    turbulence = np.random.randn(len(spike))
    turbulence_filt = apply_formants(
        turbulence, VS_D_BURST_F, VS_D_BURST_B, VS_D_BURST_G, sr=sr)
    t_b = np.arange(len(spike)) / sr
    mix_env = np.exp(-t_b * VS_D_BURST_DECAY)
    burst_raw = spike * mix_env + turbulence_filt * (1.0 - mix_env) * 0.30
    burst = norm_to_peak(f32(burst_raw), VS_D_BURST_PEAK)

    # Phase 3: CROSSFADE CUTBACK
    if n_cutback > 0:
        src_cb = rosenberg_pulse(n_cutback, PITCH_HZ, sr=sr)

        # Signal A: closed-tract voicing (quiet — tract attenuates)
        sig_closed = apply_formants(
            src_cb, VS_D_CLOSED_F, VS_D_CLOSED_B, VS_D_CLOSED_G, sr=sr)
        sig_closed = norm_to_peak(sig_closed, VS_D_CLOSED_PEAK)

        # Signal B: open-tract voicing (louder — tract is open)
        sig_open = apply_formants(
            src_cb, list(f_next),
            [100.0, 140.0, 200.0, 260.0],
            [14.0, 8.0, 1.5, 0.5], sr=sr)
        sig_open = norm_to_peak(sig_open, VS_D_OPEN_PEAK)

        # Equal-power crossfade
        t_fade = np.linspace(0.0, np.pi / 2.0, n_cutback)
        fade_out = np.cos(t_fade).astype(DTYPE)
        fade_in = np.sin(t_fade).astype(DTYPE)

        cutback = f32(sig_closed * fade_out + sig_open * fade_in)

        # Gentle amplitude ramp
        cb_env = np.linspace(0.6, 1.0, n_cutback).astype(DTYPE)
        cutback = f32(cutback * cb_env)
        cutback = norm_to_peak(cutback, VS_D_CUTBACK_PEAK)
    else:
        cutback = np.array([], dtype=DTYPE)

    out = np.concatenate([closure, burst, cutback])
    return f32(out)


def synth_V(F_prev=None, F_next=None,
            pitch_hz=PITCH_HZ, dil=DIL, sr=SR):
    """[v] — UNCHANGED."""
    n = int(VS_V_DUR_MS * dil / 1000.0 * sr)
    src = rosenberg_pulse(n, pitch_hz, oq=0.65, sr=sr)
    f_mean = list(VS_V_F)
    if F_prev is not None:
        for k in range(min(len(F_prev), len(VS_V_F))):
            f_mean[k] = F_prev[k] * 0.18 + VS_V_F[k] * 0.82
    if F_next is not None:
        for k in range(min(len(F_next), len(VS_V_F))):
            f_mean[k] = f_mean[k] * 0.82 + F_next[k] * 0.18
    out = apply_formants(src, f_mean, VS_V_B, VS_V_GAINS, sr=sr)
    env = np.ones(n, dtype=float)
    atk = min(int(0.015 * sr), n // 4)
    rel = min(int(0.015 * sr), n // 4)
    if atk > 0:
        env[:atk] = np.linspace(0.0, 1.0, atk)
    if rel > 0:
        env[-rel:] = np.linspace(1.0, 0.0, rel)
    out = f32(out * env)
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.62
    return f32(out)

def synth_EE_vs(F_prev=None, F_next=None,
                pitch_hz=PITCH_HZ, dil=DIL, sr=SR):
    """[eː] — UNCHANGED."""
    n = int(VS_EE_DUR_MS * dil / 1000.0 * sr)
    src = rosenberg_pulse(n, pitch_hz, oq=0.65, sr=sr)
    f_mean = list(VS_EE_F)
    if F_prev is not None:
        for k in range(min(len(F_prev), len(VS_EE_F))):
            f_mean[k] = F_prev[k] * 0.10 + VS_EE_F[k] * 0.90
    if F_next is not None:
        for k in range(min(len(F_next), len(VS_EE_F))):
            f_mean[k] = f_mean[k] * 0.90 + F_next[k] * 0.10
    out = apply_formants(src, f_mean, VS_EE_B, VS_EE_GAINS, sr=sr)
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.72
    return f32(out)

def synth_A_vs(F_prev=None, F_next=None,
               pitch_hz=PITCH_HZ, dil=DIL, sr=SR):
    """[ɑ] — UNCHANGED."""
    n = int(VS_A_DUR_MS * dil / 1000.0 * sr)
    src = rosenberg_pulse(n, pitch_hz, oq=0.65, sr=sr)
    f_mean = list(VS_A_F)
    if F_prev is not None:
        for k in range(min(len(F_prev), len(VS_A_F))):
            f_mean[k] = F_prev[k] * 0.12 + VS_A_F[k] * 0.88
    if F_next is not None:
        for k in range(min(len(F_next), len(VS_A_F))):
            f_mean[k] = f_mean[k] * 0.88 + F_next[k] * 0.12
    out = apply_formants(src, f_mean, VS_A_B, VS_A_GAINS, sr=sr)
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.72
    return f32(out)

def synth_M_vs(F_prev=None, F_next=None,
               pitch_hz=PITCH_HZ, dil=DIL, sr=SR):
    """[m] — UNCHANGED."""
    n = int(VS_M_DUR_MS * dil / 1000.0 * sr)
    src = rosenberg_pulse(n, pitch_hz, oq=0.65, sr=sr)
    f_mean = list(VS_M_F)
    if F_prev is not None:
        for k in range(min(len(F_prev), len(VS_M_F))):
            f_mean[k] = F_prev[k] * 0.12 + VS_M_F[k] * 0.88
    if F_next is not None:
        for k in range(min(len(F_next), len(VS_M_F))):
            f_mean[k] = f_mean[k] * 0.88 + F_next[k] * 0.12
    out = apply_formants(src, f_mean, VS_M_B, VS_M_GAINS, sr=sr)
    out = iir_notch(out, VS_M_ANTI_F, VS_M_ANTI_BW, sr=sr)
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.42
    return f32(out)

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

def synth_devam(pitch_hz=PITCH_HZ, dil=DIL,
                with_room=False, sr=SR):
    """DEVAM [devɑm] — Rigveda 1.1.1, word 5."""
    d_seg = synth_D(F_prev=None, F_next=VS_EE_F, dil=dil, sr=sr)
    e_seg = synth_EE_vs(F_prev=None, F_next=VS_V_F,
                        pitch_hz=pitch_hz, dil=dil, sr=sr)
    v_seg = synth_V(F_prev=VS_EE_F, F_next=VS_A_F,
                    pitch_hz=pitch_hz, dil=dil, sr=sr)
    a_seg = synth_A_vs(F_prev=VS_V_F, F_next=VS_M_F,
                       pitch_hz=pitch_hz, dil=dil, sr=sr)
    m_seg = synth_M_vs(F_prev=VS_A_F, F_next=None,
                       pitch_hz=pitch_hz, dil=dil, sr=sr)

    word = np.concatenate([d_seg, e_seg, v_seg, a_seg, m_seg])
    mx = np.max(np.abs(word))
    if mx > 1e-8:
        word = word / mx * 0.75
    if with_room:
        word = apply_simple_room(word, rt60=1.5, direct_ratio=0.55, sr=sr)
    return f32(word)

VS_D_BURST_F_VAL  = VS_D_BURST_F[1]
VS_V_F2_VAL       = VS_V_F[1]
VS_D_CLOSURE_MS_V = VS_D_CLOSURE_MS
VS_D_BURST_MS_V   = VS_D_BURST_MS

if __name__ == "__main__":
    print("Synthesising DEVAM [devɑm] v13...")
    print("  [d] v13: closed peak 0.40, open peak 0.65")
    print("  Closed tract quieter than open (physics correct)")
    print()

    dry = synth_devam(with_room=False)
    hall = synth_devam(with_room=True)
    write_wav("output_play/devam_v13_dry.wav", dry)
    write_wav("output_play/devam_v13_hall.wav", hall)
    write_wav("output_play/devam_v13_slow6x.wav", ola_stretch(dry, 6.0))
    write_wav("output_play/devam_v13_slow12x.wav", ola_stretch(dry, 12.0))

    perf = synth_devam(dil=2.5, with_room=False)
    perf_hall = synth_devam(dil=2.5, with_room=True)
    write_wav("output_play/devam_v13_perf.wav", perf)
    write_wav("output_play/devam_v13_perf_hall.wav", perf_hall)
    write_wav("output_play/devam_v13_perf_slow6x.wav", ola_stretch(perf, 6.0))

    for sig, name in [
        (synth_D(), "devam_v13_d_iso"),
        (synth_V(), "devam_v13_v_iso"),
    ]:
        mx = np.max(np.abs(sig))
        if mx > 1e-8:
            sig = sig / mx * 0.75
        write_wav(f"output_play/{name}.wav", sig)
        write_wav(f"output_play/{name}_slow6x.wav", ola_stretch(sig, 6.0))
        write_wav(f"output_play/{name}_slow12x.wav", ola_stretch(sig, 12.0))

    print("Done.")
    print("  afplay output_play/devam_v13_d_iso_slow6x.wav")
    print("  afplay output_play/devam_v13_perf_hall.wav")
    print("  The [d] should be gentler now — less energy in the transition.")
