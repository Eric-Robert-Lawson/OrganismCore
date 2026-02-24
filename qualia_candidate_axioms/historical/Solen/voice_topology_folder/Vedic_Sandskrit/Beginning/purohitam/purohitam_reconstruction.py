#!/usr/bin/env python3
"""
PUROHITAM v4 — UNIFIED SOURCE ARCHITECTURE
Vedic Sanskrit: purohitam [puroːhitɑm]
Rigveda 1.1.1, word 4
"the household priest" (accusative singular)

v3 → v4 CHANGES:

  1. [t] AND [p] — UNIFIED SOURCE ARCHITECTURE
     (from RATNADHATAMAM v16)

     v3 used pluck architecture: burst-only arrays with
     closing tails and opening heads on adjacent vowels.
     The burst was a bare spike+turbulence array.

     PROBLEM: The spike [1.0, 0.6, 0.3] at full amplitude
     in a 7-8ms burst array is too harsh. The burst emerges
     from the closing tail's fade-to-zero, then the spike
     hits at maximum amplitude. Even though the closing tail
     is smooth and the opening head is smooth, the burst
     itself is aggressive because it's a naked transient
     with no continuous noise substrate to soften it.

     v4 SOLUTION (from RATNADHATAMAM v16):
     The breath is continuous. Generate ONE noise buffer
     spanning closure + burst + VOT. Shape with ONE continuous
     envelope. The spike RIDES ON TOP of continuous noise.
     No digital silence. No concatenation boundaries.

     But we KEEP the pluck principle for the word-level
     architecture: the preceding vowel still owns its closing
     tail, the following vowel still owns its opening head.
     The unified source is INSIDE the stop phoneme — it
     replaces the bare burst array with a properly shaped
     continuous signal.

     THE TWO PRINCIPLES COMPOSE:
       Pluck architecture: vowels own transitions
       Unified source: the stop itself has no internal boundaries

  2. CLOSING TAILS AND OPENING HEADS — unchanged from v3.
     The vowels still own their transitions.

  3. ALL OTHER PHONEMES — unchanged from v3.

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

# [p] voiceless bilabial stop — v4 UNIFIED SOURCE
VS_P_CLOSURE_MS  = 15.0   # Short closure (word-initial silence)
VS_P_BURST_MS    = 8.0
VS_P_VOT_MS      = 12.0
VS_P_BURST_F     = [600.0, 1300.0, 2100.0, 3000.0]
VS_P_BURST_B     = [300.0,  300.0,  400.0,  500.0]
VS_P_BURST_G     = [  6.0,   16.0,    4.0,    1.5]
VS_P_BURST_DECAY = 130.0
VS_P_BURST_GAIN  = 0.15
VS_P_PREBURST_MS   = 3.0
VS_P_PREBURST_AMP  = 0.006
VS_P_SUBGLOTTAL_FLOOR = 0.001
VS_P_INITIAL_SILENCE_MS = 10.0  # word-initial only

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

# [t] voiceless dental stop — v4 UNIFIED SOURCE
VS_T_CLOSURE_MS  = 15.0   # Short closure (inside unified source)
VS_T_BURST_MS    = 7.0
VS_T_VOT_MS      = 15.0
VS_T_BURST_F     = [1500.0, 3500.0, 5000.0, 6500.0]
VS_T_BURST_B     = [ 400.0,  600.0,  800.0, 1000.0]
VS_T_BURST_G     = [   4.0,   14.0,    6.0,    2.0]
VS_T_BURST_DECAY = 170.0
VS_T_BURST_GAIN  = 0.15
VS_T_PREBURST_MS   = 5.0
VS_T_PREBURST_AMP  = 0.008
VS_T_SUBGLOTTAL_FLOOR = 0.001
VS_T_LOCUS_F     = [700.0, 1800.0, 2500.0, 3500.0]

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
VS_M_RELEASE_MS = 20.0

# Pluck architecture parameters (closing tail / opening head)
CLOSING_TAIL_MS = 25.0
OPENING_HEAD_MS = 15.0

PITCH_HZ = 120.0
DIL      = 1.0

# ============================================================================
# SYNTHESIS HELPERS
# ============================================================================

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
# PLUCK HELPERS
# ============================================================================

def make_closing_tail(voiced_seg, tail_ms=CLOSING_TAIL_MS, sr=SR):
    """
    Append a closing tail to a voiced segment.
    The tail models the articulator closing for a stop.
    Core voicing + RMS fade.
    """
    n_tail = int(tail_ms / 1000.0 * sr)
    if n_tail < 1:
        return voiced_seg

    period = int(sr / PITCH_HZ)
    if len(voiced_seg) >= period:
        template = voiced_seg[-period:]
        n_reps = (n_tail // period) + 2
        tail_src = np.tile(template, n_reps)[:n_tail]
    else:
        tail_src = np.zeros(n_tail, dtype=DTYPE)

    fade = np.linspace(1.0, 0.0, n_tail) ** 2
    tail = f32(tail_src * fade)

    return f32(np.concatenate([voiced_seg, tail]))

def make_opening_head(voiced_seg, head_ms=OPENING_HEAD_MS, sr=SR):
    """
    Prepend an opening head to a voiced segment.
    Models the vocal folds resuming vibration after a voiceless stop.
    Squared amplitude rise.
    """
    n_head = int(head_ms / 1000.0 * sr)
    if n_head < 1:
        return voiced_seg

    period = int(sr / PITCH_HZ)
    if len(voiced_seg) >= period:
        template = voiced_seg[:period]
        n_reps = (n_head // period) + 2
        head_src = np.tile(template, n_reps)[:n_head]
    else:
        head_src = np.zeros(n_head, dtype=DTYPE)

    rise = np.linspace(0.0, 1.0, n_head) ** 2
    head = f32(head_src * rise)

    return f32(np.concatenate([head, voiced_seg]))

# ============================================================================
# UNIFIED SOURCE STOP SYNTHESIS
# (from RATNADHATAMAM v16 — the breath is continuous)
# ============================================================================

def _synth_unified_voiceless_stop(
    closure_ms, burst_ms, vot_ms,
    burst_f, burst_b, burst_g, burst_decay, burst_gain,
    preburst_ms, preburst_amp, subglottal_floor,
    vot_locus_f, F_next,
    vot_vowel_b, vot_vowel_gains,
    pitch_hz=PITCH_HZ, dil=DIL,
):
    """
    Unified source architecture for voiceless stops.
    ONE continuous noise buffer. ONE continuous envelope.
    The spike rides on the noise. No boundaries.

    From RATNADHATAMAM v16 synth_T(), generalized for any
    voiceless stop place (dental, bilabial, etc.).
    """
    n_cl = int(closure_ms * dil / 1000.0 * SR)
    n_b  = int(burst_ms * dil / 1000.0 * SR)
    n_v  = int(vot_ms * dil / 1000.0 * SR)
    n_total = n_cl + n_b + n_v

    # ── UNIFIED NOISE SOURCE ──────────────────────────────
    noise_source = np.random.randn(n_total).astype(float)

    # ── CONTINUOUS AMPLITUDE ENVELOPE ─────────────────────
    env = np.zeros(n_total, dtype=float)

    # Phase A: Subglottal floor during closure
    silence_n = n_cl - min(int(preburst_ms / 1000.0 * SR), n_cl)
    preburst_n = n_cl - silence_n

    env[0:silence_n] = subglottal_floor

    # Phase B: Exponential crescendo (pre-burst leak)
    if preburst_n > 0:
        t_pre = np.linspace(0.0, 1.0, preburst_n)
        crescendo = subglottal_floor + \
            (preburst_amp - subglottal_floor) * np.exp(3.0 * (t_pre - 1.0))
        env[silence_n : n_cl] = crescendo

    # Phase C: Burst (place-specific resonance)
    burst_start = n_cl
    burst_end   = n_cl + n_b
    t_burst = np.arange(n_b, dtype=float) / SR
    burst_env = burst_gain * np.exp(-t_burst * burst_decay)
    env[burst_start : burst_end] = burst_env

    # Smooth closure→burst transition (1ms cosine blend)
    blend_n = min(int(0.001 * SR), preburst_n, n_b)
    if blend_n > 1:
        left_val  = env[burst_start - 1] if burst_start > 0 \
            else subglottal_floor
        right_val = env[burst_start]
        t_blend = np.linspace(0.0, np.pi, blend_n)
        blend_curve = left_val + (right_val - left_val) * \
            0.5 * (1.0 - np.cos(t_blend))
        half = blend_n // 2
        start_idx = max(0, burst_start - half)
        end_idx = start_idx + blend_n
        if end_idx <= n_total:
            env[start_idx : end_idx] = blend_curve

    # Phase D: Burst decay into VOT aspiration
    vot_start = burst_end
    vot_end   = n_total
    if n_v > 0:
        t_vot = np.linspace(0.0, 1.0, n_v)
        burst_tail = burst_env[-1] if n_b > 0 else burst_gain * 0.1
        aspiration_decay = burst_tail * np.exp(-t_vot * 3.0)
        aspiration_decay = np.maximum(aspiration_decay, subglottal_floor)
        env[vot_start : vot_end] = aspiration_decay

    # ── APPLY PLACE-SPECIFIC FORMANTS ─────────────────────
    noise_shaped = apply_formants(noise_source, burst_f, burst_b, burst_g)
    noise_out = f32(noise_shaped * env)

    # ── ADD SPIKE TRANSIENT AT BURST ONSET ────────────────
    spike = np.zeros(n_total, dtype=float)
    spike_len = min(3, n_b)
    spike_vals = [1.0, 0.6, 0.3][:spike_len]
    for i, sv in enumerate(spike_vals):
        if burst_start + i < n_total:
            spike[burst_start + i] = sv

    spike_env = np.zeros(n_total, dtype=float)
    if n_b > 0:
        spike_env[burst_start:burst_end] = np.exp(
            -np.arange(n_b, dtype=float) / SR * burst_decay)
    spike_out = f32(spike * spike_env * burst_gain * 0.5)

    # ── PHASE E: VOICED COMPONENT (FADES IN DURING VOT) ──
    f_vot = list(vot_locus_f)
    if F_next is not None:
        for k in range(min(len(F_next), len(f_vot))):
            f_vot[k] = vot_locus_f[k] * 0.7 + F_next[k] * 0.3

    vot_voiced = np.zeros(n_total, dtype=float)
    if n_v > 0:
        src_voiced = rosenberg_pulse(n_v, pitch_hz)
        voicing_env = np.linspace(0.0, 1.0, n_v)
        vot_filt = apply_formants(
            src_voiced, f_vot,
            vot_vowel_b,
            [g * 0.4 for g in vot_vowel_gains])
        vot_voiced[vot_start:vot_end] = f32(
            vot_filt * voicing_env * 0.15)

    # ── COMBINE ───────────────────────────────────────────
    out = noise_out + spike_out + vot_voiced

    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.55
    return f32(out)

# ============================================================================
# PHONEME SYNTHESIS FUNCTIONS
# ============================================================================

def synth_P(F_next=None, pitch_hz=PITCH_HZ, dil=DIL,
            word_initial=True):
    """
    [p] voiceless bilabial stop — v4 UNIFIED SOURCE

    Word-initial: 10ms silence prepended (the word begins from
    nothing — lips closed, no preceding sound).

    The unified source inside the stop spans closure+burst+VOT
    as one continuous signal. No concatenation boundaries.
    """
    stop_sig = _synth_unified_voiceless_stop(
        closure_ms=VS_P_CLOSURE_MS,
        burst_ms=VS_P_BURST_MS,
        vot_ms=VS_P_VOT_MS,
        burst_f=VS_P_BURST_F,
        burst_b=VS_P_BURST_B,
        burst_g=VS_P_BURST_G,
        burst_decay=VS_P_BURST_DECAY,
        burst_gain=VS_P_BURST_GAIN,
        preburst_ms=VS_P_PREBURST_MS,
        preburst_amp=VS_P_PREBURST_AMP,
        subglottal_floor=VS_P_SUBGLOTTAL_FLOOR,
        vot_locus_f=[600.0, 1300.0, 2100.0, 3000.0],
        F_next=F_next if F_next is not None else VS_U_F,
        vot_vowel_b=VS_U_B,
        vot_vowel_gains=VS_U_GAINS,
        pitch_hz=pitch_hz,
        dil=dil,
    )

    if word_initial:
        n_sil = int(VS_P_INITIAL_SILENCE_MS * dil / 1000.0 * SR)
        silence = np.zeros(n_sil, dtype=DTYPE)
        return f32(np.concatenate([silence, stop_sig]))

    return stop_sig


def synth_U(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=DIL,
            closing_for_stop=False):
    """[u] short close back rounded (VERIFIED PUROHITAM v1)"""
    n = int(VS_U_DUR_MS * dil / 1000.0 * SR)
    src = rosenberg_pulse(n, pitch_hz)

    f_mean = list(VS_U_F)
    if F_prev is not None:
        for k in range(min(len(F_prev), len(VS_U_F))):
            f_mean[k] = (F_prev[k] * VS_U_COART_ON +
                         VS_U_F[k] * (1.0 - VS_U_COART_ON))
    if F_next is not None:
        for k in range(min(len(F_next), len(VS_U_F))):
            f_mean[k] = (f_mean[k] * (1.0 - VS_U_COART_OFF) +
                         F_next[k] * VS_U_COART_OFF)

    out = apply_formants(src, f_mean, VS_U_B, VS_U_GAINS)

    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.70

    if closing_for_stop:
        out = make_closing_tail(f32(out), CLOSING_TAIL_MS)

    return f32(out)


def synth_R(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=DIL):
    """[ɾ] alveolar tap (VERIFIED PUROHITAM v1)"""
    n = int(VS_R_DUR_MS * dil / 1000.0 * SR)
    src = rosenberg_pulse(n, pitch_hz)

    f_mean = list(VS_R_F)
    if F_prev is not None:
        for k in range(min(len(F_prev), len(VS_R_F))):
            f_mean[k] = (F_prev[k] * VS_R_COART_ON +
                         VS_R_F[k] * (1.0 - VS_R_COART_ON))
    if F_next is not None:
        for k in range(min(len(F_next), len(VS_R_F))):
            f_mean[k] = (f_mean[k] * (1.0 - VS_R_COART_OFF) +
                         F_next[k] * VS_R_COART_OFF)

    out = apply_formants(src, f_mean, VS_R_B, VS_R_GAINS)

    t = np.linspace(0, 1, n)
    dip_env = 1.0 - VS_R_DIP_DEPTH * np.exp(
        -((t - 0.5) / VS_R_DIP_WIDTH) ** 2 * 10.0)
    out = out * dip_env

    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.65
    return f32(out)


def synth_OO(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=DIL):
    """[oː] long close-mid back (VERIFIED PUROHITAM v1)"""
    n = int(VS_OO_DUR_MS * dil / 1000.0 * SR)
    src = rosenberg_pulse(n, pitch_hz)

    f_mean = list(VS_OO_F)
    if F_prev is not None:
        for k in range(min(len(F_prev), len(VS_OO_F))):
            f_mean[k] = (F_prev[k] * VS_OO_COART_ON +
                         VS_OO_F[k] * (1.0 - VS_OO_COART_ON))
    if F_next is not None:
        for k in range(min(len(F_next), len(VS_OO_F))):
            f_mean[k] = (f_mean[k] * (1.0 - VS_OO_COART_OFF) +
                         F_next[k] * VS_OO_COART_OFF)

    out = apply_formants(src, f_mean, VS_OO_B, VS_OO_GAINS)

    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.72
    return f32(out)


def synth_H(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=DIL):
    """[h] voiceless glottal fricative (VERIFIED PUROHITAM v1)"""
    n = int(VS_H_DUR_MS * dil / 1000.0 * SR)

    noise = np.random.randn(n)

    f_mean = list(VS_H_F_APPROX)
    if F_next is not None:
        for k in range(min(len(F_next), len(VS_H_F_APPROX))):
            f_mean[k] = (VS_H_F_APPROX[k] * (1.0 - VS_H_COART_OFF) +
                         F_next[k] * VS_H_COART_OFF)

    out = apply_formants(noise, f_mean, VS_H_B, VS_H_GAINS)

    env = np.linspace(0.3, 1.0, n)
    out = out * env

    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.18
    return f32(out)


def synth_I(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=DIL,
            closing_for_stop=False):
    """[i] short close front unrounded (VERIFIED AGNI)"""
    n = int(VS_I_DUR_MS * dil / 1000.0 * SR)
    src = rosenberg_pulse(n, pitch_hz)

    f_mean = list(VS_I_F)
    if F_prev is not None:
        for k in range(min(len(F_prev), len(VS_I_F))):
            f_mean[k] = (F_prev[k] * VS_I_COART_ON +
                         VS_I_F[k] * (1.0 - VS_I_COART_ON))
    if F_next is not None:
        for k in range(min(len(F_next), len(VS_I_F))):
            f_mean[k] = (f_mean[k] * (1.0 - VS_I_COART_OFF) +
                         F_next[k] * VS_I_COART_OFF)

    out = apply_formants(src, f_mean, VS_I_B, VS_I_GAINS)

    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.70

    if closing_for_stop:
        out = make_closing_tail(f32(out), CLOSING_TAIL_MS)

    return f32(out)


def synth_T(F_next=None, pitch_hz=PITCH_HZ, dil=DIL):
    """
    [t] voiceless dental stop — v4 UNIFIED SOURCE
    (from RATNADHATAMAM v16)

    The breath is continuous. The tongue is the envelope.
    ONE noise buffer. ONE amplitude envelope.
    The spike rides on the noise floor.
    """
    return _synth_unified_voiceless_stop(
        closure_ms=VS_T_CLOSURE_MS,
        burst_ms=VS_T_BURST_MS,
        vot_ms=VS_T_VOT_MS,
        burst_f=VS_T_BURST_F,
        burst_b=VS_T_BURST_B,
        burst_g=VS_T_BURST_G,
        burst_decay=VS_T_BURST_DECAY,
        burst_gain=VS_T_BURST_GAIN,
        preburst_ms=VS_T_PREBURST_MS,
        preburst_amp=VS_T_PREBURST_AMP,
        subglottal_floor=VS_T_SUBGLOTTAL_FLOOR,
        vot_locus_f=VS_T_LOCUS_F,
        F_next=F_next if F_next is not None else VS_A_F,
        vot_vowel_b=VS_A_B,
        vot_vowel_gains=VS_A_GAINS,
        pitch_hz=pitch_hz,
        dil=dil,
    )


def synth_A(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=DIL,
            opening_from_stop=False):
    """[ɑ] short open central unrounded (VERIFIED AGNI)"""
    n = int(VS_A_DUR_MS * dil / 1000.0 * SR)
    src = rosenberg_pulse(n, pitch_hz)

    f_mean = list(VS_A_F)
    if F_prev is not None:
        for k in range(min(len(F_prev), len(VS_A_F))):
            f_mean[k] = (F_prev[k] * VS_A_COART_ON +
                         VS_A_F[k] * (1.0 - VS_A_COART_ON))
    if F_next is not None:
        for k in range(min(len(F_next), len(VS_A_F))):
            f_mean[k] = (f_mean[k] * (1.0 - VS_A_COART_OFF) +
                         F_next[k] * VS_A_COART_OFF)

    out = apply_formants(src, f_mean, VS_A_B, VS_A_GAINS)

    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.72

    if opening_from_stop:
        out = make_opening_head(f32(out), OPENING_HEAD_MS)

    return f32(out)


def synth_M(F_prev=None, pitch_hz=PITCH_HZ, dil=DIL,
            word_final=False):
    """[m] bilabial nasal (VERIFIED PUROHITAM v1)"""
    n = int(VS_M_DUR_MS * dil / 1000.0 * SR)
    n_release = int(VS_M_RELEASE_MS * dil / 1000.0 * SR) \
        if word_final else 0

    src = rosenberg_pulse(n + n_release, pitch_hz)

    f_mean = list(VS_M_F)
    if F_prev is not None:
        for k in range(min(len(F_prev), len(VS_M_F))):
            f_mean[k] = (F_prev[k] * VS_M_COART_ON +
                         VS_M_F[k] * (1.0 - VS_M_COART_ON))

    out = apply_formants(src, f_mean, VS_M_B, VS_M_GAINS)
    out = iir_notch(out, VS_M_ANTI_F, VS_M_ANTI_BW)

    if word_final and n_release > 0:
        env = np.ones(len(out), dtype=float)
        env[-n_release:] = np.linspace(1.0, 0.0, n_release) ** 2
        out = f32(out * env)

    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.42
    return f32(out)


# ============================================================================
# WORD SYNTHESIS
# ============================================================================

def synth_purohitam(pitch_hz=PITCH_HZ, dil=DIL, with_room=False):
    """
    PUROHITAM [puroːhitɑm] — v4 UNIFIED SOURCE ARCHITECTURE
    Rigveda 1.1.1, word 4
    Syllables: PU-RŌ-HI-TAM

    v4 composes TWO architectural principles:

      1. PLUCK: Vowels own their transitions (closing tails,
         opening heads). The stop does not own what happens
         before or after it.

      2. UNIFIED SOURCE: Inside the stop, ONE continuous noise
         buffer + ONE continuous envelope. No concatenation
         boundaries. The breath is continuous.

    The [i] closing tail fades the voicing. Then the [t] unified
    source begins with subglottal floor (never digital zero),
    crescendos through pre-burst leak, bursts at dental locus,
    decays through aspiration, and voicing fades in. Then the [ɑ]
    opening head rises.

    No boundary anywhere is a concatenation of arrays born from
    different sources.

    Segment map (v4):
      [p] UNIFIED (word-initial)  10ms silence + 35ms unified = 45ms
      head + [u]                  15ms rise + 50ms = 65ms
      [ɾ]                         30ms
      [oː]                        100ms
      [h]                          65ms
      [i] + closing tail           50ms + 25ms = 75ms
      [t] UNIFIED                  37ms (15ms closure + 7ms burst + 15ms VOT)
      head + [ɑ]                   15ms rise + 55ms = 70ms
      [m] + release                60ms + 20ms = 80ms
    """
    segs = [
        # PU-
        synth_P(F_next=VS_U_F,
                pitch_hz=pitch_hz, dil=dil, word_initial=True),
        make_opening_head(
            synth_U(F_prev=None, F_next=VS_R_F,
                    pitch_hz=pitch_hz, dil=dil),
            OPENING_HEAD_MS),

        # -RŌ-
        synth_R(F_prev=VS_U_F, F_next=VS_OO_F,
                pitch_hz=pitch_hz, dil=dil),
        synth_OO(F_prev=VS_R_F, F_next=VS_H_F_APPROX,
                 pitch_hz=pitch_hz, dil=dil),

        # -HI-
        synth_H(F_prev=VS_OO_F, F_next=VS_I_F,
                pitch_hz=pitch_hz, dil=dil),
        synth_I(F_prev=VS_H_F_APPROX, F_next=VS_T_LOCUS_F,
                pitch_hz=pitch_hz, dil=dil,
                closing_for_stop=True),

        # -TAM
        synth_T(F_next=VS_A_F,
                pitch_hz=pitch_hz, dil=dil),
        synth_A(F_prev=VS_T_LOCUS_F, F_next=VS_M_F,
                pitch_hz=pitch_hz, dil=dil,
                opening_from_stop=True),
        synth_M(F_prev=VS_A_F, pitch_hz=pitch_hz, dil=dil,
                word_final=True),
    ]

    word = np.concatenate(segs)
    mx = np.max(np.abs(word))
    if mx > 1e-8:
        word = word / mx * 0.75

    if with_room:
        word = apply_simple_room(word, rt60=1.5, direct_ratio=0.55)

    return f32(word)


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print()
    print("=" * 70)
    print("PUROHITAM v4 — UNIFIED SOURCE ARCHITECTURE")
    print("=" * 70)
    print()
    print("v3→v4 CHANGES:")
    print()
    print("  [t] and [p] — UNIFIED SOURCE (from RATNADHATAMAM v16):")
    print("    ONE continuous noise buffer (the breath)")
    print("    ONE continuous amplitude envelope (the tongue)")
    print("    NO concatenation boundaries inside the stop")
    print("    Subglottal floor: 0.001 (~-60dB) — never digital zero")
    print("    Pre-burst crescendo rides on subglottal floor")
    print("    Spike ADDED to continuous noise (not concatenated)")
    print("    Place-specific formants applied to entire buffer")
    print()
    print("  PLUCK + UNIFIED SOURCE compose:")
    print("    Vowels own transitions (closing tails, opening heads)")
    print("    Stop owns its internal physics (breath + tongue)")
    print("    No boundary anywhere is born from different sources")
    print()
    print("  [p] bilabial: F2 1300 Hz, decay 130, gain 0.15")
    print("  [t] dental:   F2 3500 Hz, decay 170, gain 0.15")
    print()
    print("  All other phonemes unchanged from v3.")
    print()

    # Diagnostic speed
    word_dry = synth_purohitam(PITCH_HZ, 1.0)
    word_slow = ola_stretch(word_dry, 6.0)
    word_slow12 = ola_stretch(word_dry, 12.0)

    # Performance speed
    word_perf = synth_purohitam(PITCH_HZ, 2.5)
    word_perf_hall = synth_purohitam(PITCH_HZ, 2.5, with_room=True)

    # Hall
    word_hall = synth_purohitam(PITCH_HZ, 1.0, with_room=True)

    write_wav("output_play/purohitam_v4_dry.wav", word_dry)
    write_wav("output_play/purohitam_v4_slow6x.wav", word_slow)
    write_wav("output_play/purohitam_v4_slow12x.wav", word_slow12)
    write_wav("output_play/purohitam_v4_hall.wav", word_hall)
    write_wav("output_play/purohitam_v4_perf.wav", word_perf)
    write_wav("output_play/purohitam_v4_perf_hall.wav", word_perf_hall)

    # Isolated phonemes for diagnostic
    p_iso = synth_P(F_next=VS_U_F, word_initial=True)
    t_iso = synth_T(F_next=VS_A_F)

    for sig, name in [
        (p_iso, "purohitam_v4_p_iso"),
        (t_iso, "purohitam_v4_t_iso"),
    ]:
        mx = np.max(np.abs(sig))
        if mx > 1e-8:
            sig = sig / mx * 0.75
        write_wav(f"output_play/{name}.wav", sig)
        write_wav(f"output_play/{name}_slow6x.wav",
                  ola_stretch(sig, 6.0))
        write_wav(f"output_play/{name}_slow12x.wav",
                  ola_stretch(sig, 12.0))

    print()
    print("=" * 70)
    print("v4 synthesis complete.")
    print()
    print("LISTEN:")
    print("  afplay output_play/purohitam_v4_slow6x.wav")
    print("  afplay output_play/purohitam_v4_slow12x.wav")
    print("  afplay output_play/purohitam_v4_perf_hall.wav")
    print("  afplay output_play/purohitam_v4_t_iso_slow12x.wav")
    print("  afplay output_play/purohitam_v4_p_iso_slow12x.wav")
    print()
    print("LISTEN FOR:")
    print("  [t] — The burst should be softer, not harsh.")
    print("        It emerges from the continuous noise floor.")
    print("        No spike-from-silence attack.")
    print("        Compare v4 to v3 at 12x slow.")
    print()
    print("  [p] — Same improvement. The lips release compressed")
    print("        air that was always there (subglottal floor).")
    print("        The burst rides on the noise, not on silence.")
    print()
    print("  The two principles compose:")
    print("    Pluck: vowels own transitions")
    print("    Unified source: stop owns its physics")
    print("    No boundary is born from different sources.")
    print("=" * 70)
    print()
