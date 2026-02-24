#!/usr/bin/env python3
"""
HOTĀRAM v9 — Sweet Spot Reconstruction
Rigveda 1.1.1, word 8
[hoːtaːrɑm] — "the invoker"

ITERATION v8→v9:
  Problem: [t] is clicky.
  
  Root causes (from Pluck Artifact + RATNADHĀTAMAM v17):
    1. v8 built [t] from SEPARATE CONCATENATED arrays
       (closure + burst + aspiration). The Unified Source
       Principle requires ONE continuous noise buffer with
       ONE continuous envelope. No internal boundaries.
    2. Burst gain 0.38 — too hot. RATNADHĀTAMAM v17 uses 0.15.
       At observer position, the dental burst is brief and gentle.
    3. Missing Phase E voicing fade-in — the breath should transition
       smoothly into voicing during VOT, not stop dead.

  Fix: Import _synth_unified_voiceless_stop() architecture
       from RATNADHĀTAMAM v17. ONE buffer. ONE envelope.
       Correct gain. Proper decay constants.

  The Pluck Artifact (line 24-26): "The breath is continuous.
  Inside any acoustic event, ONE continuous source buffer
  shaped by ONE continuous envelope eliminates all internal
  concatenation boundaries."

  Observer Position Artifact (line 91-96): Voiceless stops
  are brief (8-12ms burst). Their source-vs-observer difference
  is masked by short duration — imperceptible. But the GAIN
  must still be at observer level, not source level.

  [h]: UNCHANGED from v8 (topology-derived, distance zero)
  All phoneme parameters: UNCHANGED

  Ancestor: RATNADHĀTAMAM v17 _synth_unified_voiceless_stop()
            Origin Artifact (v8 [h])
            Observer Position Artifact
            Pluck Artifact (Unified Source composition)

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

# ── [h] voiceless glottal �� v8 TOPOLOGY-DERIVED (distance zero) ────────────
VS_H_DUR_MS             = 65.0
VS_H_GLOTTAL_NOISE_GAIN = 0.08
VS_H_FINAL_NORM         = 0.25
VS_H_RADIATION_CUTOFF   = 6000.0
VS_H_OQ                 = 0.95
VS_H_NOISE_BLEND        = 0.85
VS_H_BW_WIDEN           = 1.5
VS_H_GAIN_SCALE         = 0.6
VS_H_CROSSFADE_MS       = 20.0

# ── [oː] long close-mid back rounded — VERIFIED PUROHITAM ─────────────────
VS_OO_F        = [430.0,  800.0, 2500.0, 3200.0]
VS_OO_B        = [110.0,  130.0,  200.0,  270.0]
VS_OO_GAINS    = [ 15.0,    8.0,    1.5,    0.5]
VS_OO_DUR_MS   = 100.0
VS_OO_COART_ON  = 0.10
VS_OO_COART_OFF = 0.10

# ── [t] voiceless dental stop — v9 CANONICAL (from RATNADHĀTAMAM v17) ──────
VS_T_CLOSURE_MS  = 25.0
VS_T_BURST_MS    = 7.0
VS_T_VOT_MS      = 15.0

# v9: EXACT parameters from RATNADHĀTAMAM v17
# 4-formant burst filter (place-specific, dental = high locus)
VS_T_BURST_F     = [1500.0, 3500.0, 5000.0, 6500.0]
VS_T_BURST_B     = [ 400.0,  600.0,  800.0, 1000.0]
VS_T_BURST_G     = [   4.0,   14.0,    6.0,    2.0]
VS_T_BURST_DECAY = 170.0     # exponential decay rate (Hz) — verified

VS_T_BURST_GAIN  = 0.15      # v9: CORRECTED from 0.38 → observer level
VS_T_PREBURST_MS   = 5.0     # pre-burst crescendo duration
VS_T_PREBURST_AMP  = 0.008   # crescendo peak before burst

VS_T_SUBGLOTTAL_FLOOR = 0.001  # ~-60dB, prevents digital zero

VS_T_LOCUS_F     = [700.0, 1800.0, 2500.0, 3500.0]  # VOT formant targets

# Pluck boundary parameters
CLOSING_TAIL_MS = 25.0
OPENING_HEAD_MS = 15.0

# ── [aː] long open central unrounded — AGNI verified ──────────────────────
VS_AA_F        = [700.0, 1100.0, 2550.0, 3400.0]
VS_AA_B        = [130.0,  160.0,  220.0,  280.0]
VS_AA_GAINS    = [ 16.0,    6.0,    1.5,    0.5]
VS_AA_DUR_MS   = 110.0
VS_AA_COART_ON  = 0.10
VS_AA_COART_OFF = 0.10

# ── [ɾ] alveolar tap — VERIFIED PUROHITAM ─────────────────────────────────
VS_R_F         = [300.0, 1900.0, 2700.0, 3300.0]
VS_R_B         = [120.0,  200.0,  250.0,  300.0]
VS_R_GAINS     = [ 12.0,    6.0,    1.5,    0.4]
VS_R_DUR_MS    = 30.0
VS_R_DIP_DEPTH = 0.35
VS_R_DIP_WIDTH = 0.40
VS_R_COART_ON  = 0.15
VS_R_COART_OFF = 0.15

# ── [ɑ] short open central unrounded — VERIFIED AGNI ──────────────────────
VS_A_F         = [700.0, 1100.0, 2550.0, 3400.0]
VS_A_B         = [130.0,  160.0,  220.0,  280.0]
VS_A_GAINS     = [ 16.0,    6.0,    1.5,    0.5]
VS_A_DUR_MS    = 55.0
VS_A_COART_ON  = 0.12
VS_A_COART_OFF = 0.12

# ── [m] bilabial nasal — VERIFIED PUROHITAM ───────────────────────────────
VS_M_F         = [250.0,  900.0, 2200.0, 3000.0]
VS_M_B         = [100.0,  200.0,  300.0,  350.0]
VS_M_GAINS     = [  8.0,    2.5,    0.5,    0.2]
VS_M_DUR_MS    = 60.0
VS_M_ANTI_F    = 800.0
VS_M_ANTI_BW   = 200.0
VS_M_COART_ON  = 0.15
VS_M_COART_OFF = 0.15
VS_M_RELEASE_MS = 20.0

PITCH_HZ = 120.0
DIL      = 1.0

# ============================================================================
# SEGMENT MAP — HOTĀRAM [hoːtaːrɑm]
# ============================================================================

SEG_H    = 0
SEG_OOT  = 1    # [oː] + closing tail
SEG_T    = 2    # [t] unified source (ONE buffer)
SEG_HAA  = 3    # opening head + [aː]
SEG_R    = 4
SEG_A    = 5
SEG_M    = 6

SEG_NAMES = [
    "[h] topology (whispered [oː])",
    "[oː] + closing tail",
    "[t] unified source",
    "head + [aː]",
    "[ɾ] tap",
    "[ɑ]",
    "[m] + release",
]

SEG_DURATIONS_MS = [
    VS_H_DUR_MS,
    VS_OO_DUR_MS + CLOSING_TAIL_MS,
    VS_T_CLOSURE_MS + VS_T_BURST_MS + VS_T_VOT_MS,
    OPENING_HEAD_MS + VS_AA_DUR_MS,
    VS_R_DUR_MS,
    VS_A_DUR_MS,
    VS_M_DUR_MS + VS_M_RELEASE_MS,
]

UNVOICED_INDICES = {SEG_H, SEG_T}

# ============================================================================
# SYNTHESIS HELPERS
# ============================================================================

def f32(x):
    return np.asarray(x, dtype=DTYPE)

def rms(sig):
    return float(np.sqrt(np.mean(sig.astype(float) ** 2)))

def write_wav(path, sig, sr=SR):
    sig_i = (np.clip(f32(sig), -1.0, 1.0) * 32767).astype(np.int16)
    with wave_module.open(path, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(sig_i.tobytes())
    print(f"  Wrote {path}")

def rosenberg_pulse(n_samples, pitch_hz, oq=0.65, sr=SR):
    period = int(sr / pitch_hz)
    if period < 1:
        period = 1
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

def norm_to_peak(sig, target_peak):
    mx = np.max(np.abs(sig))
    if mx > 1e-8:
        return f32(sig / mx * target_peak)
    return f32(sig)

def apply_radiation_lpf(sig, cutoff_hz, sr=SR):
    nyq = sr / 2.0
    if cutoff_hz >= nyq:
        return sig
    b, a = butter(1, cutoff_hz / nyq, btype='low')
    return f32(lfilter(b, a, sig.astype(float)))

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
    norm_buf = np.zeros(n_out, dtype=DTYPE)
    for i in range(n_frames):
        in_pos = i * hop_in
        out_pos = i * hop_out
        if in_pos + win_n > n_in:
            break
        frame = sig[in_pos:in_pos + win_n] * window
        out[out_pos:out_pos + win_n] += frame
        norm_buf[out_pos:out_pos + win_n] += window
    nz = norm_buf > 1e-8
    out[nz] /= norm_buf[nz]
    return norm_to_peak(out, 0.75)

def apply_simple_room(sig, rt60=1.5, direct_ratio=0.55, sr=SR):
    delay_ms = 23.0
    delay_n = int(delay_ms / 1000.0 * sr)
    decay = 0.3 * np.exp(-3.0 * delay_ms / 1000.0 / rt60)
    out = np.copy(sig).astype(float)
    if delay_n < len(out):
        out[delay_n:] += sig[:len(sig) - delay_n].astype(float) * decay
    out = out * direct_ratio + sig.astype(float) * (1.0 - direct_ratio)
    return norm_to_peak(out, np.max(np.abs(sig)))

# ============================================================================
# PLUCK BOUNDARY FUNCTIONS (from RATNADHĀTAMAM v17 / PUROHITAM v4)
# ============================================================================

def make_closing_tail(voiced_seg, tail_ms, pitch_hz=PITCH_HZ, sr=SR):
    """Closing tail: the vowel owns the closure. Smooth ramp-down."""
    tail_n = int(tail_ms / 1000.0 * sr)
    if tail_n >= len(voiced_seg):
        tail_n = len(voiced_seg) - 1
    tail = np.copy(voiced_seg).astype(float)
    ramp = np.ones(len(tail), dtype=float)
    tail_start = len(tail) - tail_n
    ramp[tail_start:] = np.linspace(1.0, 0.0, tail_n)
    tail *= ramp
    return f32(tail)

def make_opening_head(voiced_seg, head_ms, pitch_hz=PITCH_HZ, sr=SR):
    """Opening head: following voiced segment owns the release. Smooth ramp-up."""
    head_n = int(head_ms / 1000.0 * sr)
    if head_n >= len(voiced_seg):
        head_n = len(voiced_seg) - 1
    head = np.copy(voiced_seg).astype(float)
    ramp = np.ones(len(head), dtype=float)
    ramp[:head_n] = np.linspace(0.0, 1.0, head_n)
    head *= ramp
    return f32(head)

def make_source_crossfade(seg_noise, seg_voiced, crossfade_ms, sr=SR):
    """
    Source crossfade for [h]→vowel boundary.
    Tract shape continuous — only excitation changes.
    """
    xfade_n = int(crossfade_ms / 1000.0 * sr)
    xfade_n = min(xfade_n, len(seg_noise), len(seg_voiced))
    out_noise = np.copy(seg_noise).astype(float)
    out_voiced = np.copy(seg_voiced).astype(float)
    fade_out = np.linspace(1.0, 0.0, xfade_n)
    out_noise[-xfade_n:] *= fade_out
    fade_in = np.linspace(0.0, 1.0, xfade_n)
    out_voiced[:xfade_n] *= fade_in
    return f32(out_noise), f32(out_voiced)

# ============================================================================
# UNIFIED SOURCE VOICELESS STOP (from RATNADHĀTAMAM v17)
# ============================================================================
# THIS is the canonical architecture. ONE continuous noise buffer.
# ONE continuous amplitude envelope. The spike rides on the noise.
# No internal concatenation. No boundaries. No clicks.

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

    Direct port from RATNADHĀTAMAM v17.
    """
    n_cl = int(closure_ms * dil / 1000.0 * SR)
    n_b  = int(burst_ms * dil / 1000.0 * SR)
    n_v  = int(vot_ms * dil / 1000.0 * SR)
    n_total = n_cl + n_b + n_v

    # ── ONE CONTINUOUS NOISE SOURCE ───────────────────────
    noise_source = np.random.randn(n_total).astype(float)

    # ── ONE CONTINUOUS AMPLITUDE ENVELOPE ─────────────────
    env = np.zeros(n_total, dtype=float)

    # Phase A: Subglottal floor during closure
    env[:n_cl] = subglottal_floor

    # Phase B: Pre-burst crescendo (last preburst_ms of closure)
    n_pre = int(preburst_ms * dil / 1000.0 * SR)
    if n_pre > 0 and n_cl > n_pre:
        t_pre = np.linspace(0.0, 1.0, n_pre)
        crescendo = subglottal_floor + (preburst_amp - subglottal_floor) * (
            1.0 - np.exp(-3.0 * t_pre))
        env[n_cl - n_pre:n_cl] = crescendo

    # Phase C+D: Burst peak + exponential decay
    if n_b > 0:
        t_burst = np.arange(n_b) / SR
        burst_env = burst_gain * np.exp(-t_burst * burst_decay)
        burst_env = np.maximum(burst_env, subglottal_floor)
        env[n_cl:n_cl + n_b] = burst_env

    # Phase D continued: VOT decay (softer falloff)
    if n_v > 0:
        burst_end_amp = env[n_cl + n_b - 1] if (n_cl + n_b) > 0 else subglottal_floor
        t_vot = np.arange(n_v) / SR
        vot_env = burst_end_amp * np.exp(-t_vot * burst_decay * 0.5)
        vot_env = np.maximum(vot_env, subglottal_floor)
        env[n_cl + n_b:n_cl + n_b + n_v] = vot_env

    # ── APPLY ENVELOPE TO NOISE ───────────────────────────
    shaped_noise = noise_source * env

    # ── FORMANT FILTER (PLACE-SPECIFIC) ───────────────────
    noise_out = apply_formants(f32(shaped_noise), burst_f, burst_b, burst_g)

    # ── Phase E: VOICING FADE-IN (additive, during VOT) ──
    vot_start = n_cl + n_b
    vot_end = n_total
    if n_v > 0 and F_next is not None:
        vot_src = rosenberg_pulse(n_v, pitch_hz)
        vot_filt = apply_formants(vot_src, vot_locus_f, vot_vowel_b,
                                  [g * 0.3 for g in vot_vowel_gains])
        # Linear fade-in: voicing grows as aspiration decays
        vot_voice_env = np.linspace(0.0, 1.0, n_v)
        vot_mixed = vot_filt * vot_voice_env * 0.12
        noise_out_f = noise_out.astype(float)
        noise_out_f[vot_start:vot_end] += vot_mixed[:vot_end - vot_start]
        noise_out = f32(noise_out_f)

    # ── OBSERVER POSITION: radiation LPF ──────────────────
    radiated = apply_radiation_lpf(noise_out, 8000.0)

    return norm_to_peak(radiated, 0.55)

# ============================================================================
# PHONEME SYNTHESIS FUNCTIONS
# ============================================================================

def synth_H(F_next, B_next, G_next, pitch_hz=PITCH_HZ, dil=DIL):
    """[h] v8 topology-derived — distance zero. Whispered following vowel."""
    dur_ms = VS_H_DUR_MS * dil
    n = int(dur_ms / 1000.0 * SR)

    noise = np.random.randn(n).astype(float)
    breathy_pulse = rosenberg_pulse(n, pitch_hz, oq=VS_H_OQ)
    source = (noise * VS_H_NOISE_BLEND +
              breathy_pulse * (1.0 - VS_H_NOISE_BLEND))
    source = source * VS_H_GLOTTAL_NOISE_GAIN

    env = np.ones(n, dtype=float)
    n_onset = max(1, int(n * 0.08))
    n_rise  = max(1, int(n * 0.15))
    n_decay = max(1, int(n * 0.15))
    env[:n_onset] = np.linspace(0.0, 0.1, n_onset)
    env[n_onset:n_onset + n_rise] = np.linspace(0.1, 1.0, n_rise)
    if n_decay > 0:
        env[-n_decay:] = np.linspace(1.0, 0.4, n_decay)

    source = source * env

    b_wide = [bw * VS_H_BW_WIDEN for bw in B_next]
    g_scaled = [g * VS_H_GAIN_SCALE for g in G_next]
    shaped = apply_formants(source, list(F_next), b_wide, g_scaled)
    radiated = apply_radiation_lpf(shaped, VS_H_RADIATION_CUTOFF)
    return norm_to_peak(radiated, VS_H_FINAL_NORM)

def synth_OO(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=DIL,
             include_closing_tail=False, closing_tail_ms=0.0):
    """[oː] long close-mid back rounded — VERIFIED PUROHITAM."""
    core_ms = VS_OO_DUR_MS * dil
    tail_ms = closing_tail_ms if include_closing_tail else 0.0
    total_ms = core_ms + tail_ms
    n_total = int(total_ms / 1000.0 * SR)

    src = rosenberg_pulse(n_total, pitch_hz)
    f_mean = list(VS_OO_F)
    if F_prev is not None:
        for k in range(min(len(F_prev), len(VS_OO_F))):
            f_mean[k] = F_prev[k] * VS_OO_COART_ON + VS_OO_F[k] * (1.0 - VS_OO_COART_ON)
    if F_next is not None:
        for k in range(min(len(F_next), len(VS_OO_F))):
            f_mean[k] = f_mean[k] * (1.0 - VS_OO_COART_OFF) + F_next[k] * VS_OO_COART_OFF

    out = apply_formants(src, f_mean, VS_OO_B, VS_OO_GAINS)
    out = norm_to_peak(out, 0.72)

    if include_closing_tail and tail_ms > 0.0:
        out = make_closing_tail(out, tail_ms, pitch_hz)

    return f32(out)

def synth_T(F_next=None, pitch_hz=PITCH_HZ, dil=DIL):
    """
    [t] voiceless dental stop — v9 CANONICAL
    Uses _synth_unified_voiceless_stop() from RATNADHĀTAMAM v17.
    ONE buffer. ONE envelope. No clicks.
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
        F_next=F_next,
        vot_vowel_b=VS_AA_B,
        vot_vowel_gains=VS_AA_GAINS,
        pitch_hz=pitch_hz,
        dil=dil,
    )

def synth_AA(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=DIL,
             include_opening_head=False, opening_head_ms=0.0):
    """[aː] long open central unrounded — AGNI verified."""
    head_ms = opening_head_ms if include_opening_head else 0.0
    total_ms = head_ms + VS_AA_DUR_MS * dil
    n_total = int(total_ms / 1000.0 * SR)

    src = rosenberg_pulse(n_total, pitch_hz)
    f_mean = list(VS_AA_F)
    if F_prev is not None:
        for k in range(min(len(F_prev), len(VS_AA_F))):
            f_mean[k] = F_prev[k] * VS_AA_COART_ON + VS_AA_F[k] * (1.0 - VS_AA_COART_ON)
    if F_next is not None:
        for k in range(min(len(F_next), len(VS_AA_F))):
            f_mean[k] = f_mean[k] * (1.0 - VS_AA_COART_OFF) + F_next[k] * VS_AA_COART_OFF

    out = apply_formants(src, f_mean, VS_AA_B, VS_AA_GAINS)
    out = norm_to_peak(out, 0.72)

    if include_opening_head and head_ms > 0.0:
        out = make_opening_head(out, head_ms, pitch_hz)

    return f32(out)

def synth_R(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=DIL):
    """[ɾ] alveolar tap — VERIFIED PUROHITAM."""
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
    src = src * env

    f_mean = list(VS_R_F)
    if F_prev is not None:
        for k in range(min(len(F_prev), len(VS_R_F))):
            f_mean[k] = F_prev[k] * VS_R_COART_ON + VS_R_F[k] * (1.0 - VS_R_COART_ON)
    if F_next is not None:
        for k in range(min(len(F_next), len(VS_R_F))):
            f_mean[k] = f_mean[k] * (1.0 - VS_R_COART_OFF) + F_next[k] * VS_R_COART_OFF

    out = apply_formants(src, f_mean, VS_R_B, VS_R_GAINS)
    return norm_to_peak(out, 0.62)

def synth_A(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=DIL):
    """[ɑ] short open central unrounded — VERIFIED AGNI."""
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
    return norm_to_peak(out, 0.72)

def synth_M(F_prev=None, pitch_hz=PITCH_HZ, dil=DIL, include_release=True):
    """[m] bilabial nasal — VERIFIED PUROHITAM + word-final release."""
    core_ms = VS_M_DUR_MS * dil
    release_ms = VS_M_RELEASE_MS if include_release else 0.0
    total_ms = core_ms + release_ms
    n_total = int(total_ms / 1000.0 * SR)
    n_core = int(core_ms / 1000.0 * SR)

    src = rosenberg_pulse(n_total, pitch_hz)
    f_mean = list(VS_M_F)
    if F_prev is not None:
        for k in range(min(len(F_prev), len(VS_M_F))):
            f_mean[k] = F_prev[k] * VS_M_COART_ON + VS_M_F[k] * (1.0 - VS_M_COART_ON)

    out = apply_formants(src, f_mean, VS_M_B, VS_M_GAINS)
    out = iir_notch(out, VS_M_ANTI_F, VS_M_ANTI_BW)

    if include_release and release_ms > 0.0:
        n_release = n_total - n_core
        if n_release > 0 and n_core < len(out):
            ramp = np.linspace(1.0, 0.0, min(n_release, len(out) - n_core))
            out_f = out.astype(float)
            out_f[n_core:n_core + len(ramp)] *= ramp
            out = f32(out_f)

    return norm_to_peak(out, 0.42)

# ============================================================================
# WORD SYNTHESIS
# ============================================================================

def synth_hotaram(pitch_hz=PITCH_HZ, dil=DIL, with_room=False):
    """
    HOTĀRAM [hoːtaːrɑm] v9 — Sweet Spot Reconstruction
    
    [h](whispered [oː]) →crossfade→ [oː]+tail → [t]_unified → head+[aː] → [ɾ] → [ɑ] → [m]+release

    v9 fixes:
      [t] now uses _synth_unified_voiceless_stop() — ONE buffer, no clicks
      [h] topology-derived from v8 — whispered [oː]
      Boundary chain: [...oː → tail → ~0] + [0.001 → [t] → 0.001] + [~0 → head → aː...]
    """

    # SEG 0: [h] — whispered [oː] (topology: distance zero)
    seg_h = synth_H(
        F_next=VS_OO_F, B_next=VS_OO_B, G_next=VS_OO_GAINS,
        pitch_hz=pitch_hz, dil=dil
    )

    # SEG 1: [oː] + closing tail before [t]
    seg_oo = synth_OO(
        F_prev=None, F_next=VS_T_LOCUS_F,
        pitch_hz=pitch_hz, dil=dil,
        include_closing_tail=True, closing_tail_ms=CLOSING_TAIL_MS
    )

    # Source crossfade at [h]→[oː]: noise→voicing, tract continuous
    seg_h, seg_oo = make_source_crossfade(
        seg_h, seg_oo, VS_H_CROSSFADE_MS
    )

    # SEG 2: [t] unified source — ONE buffer, ONE envelope, no clicks
    seg_t = synth_T(F_next=VS_AA_F, pitch_hz=pitch_hz, dil=dil)

    # SEG 3: opening head + [aː]
    seg_aa = synth_AA(
        F_prev=VS_T_LOCUS_F, F_next=VS_R_F,
        pitch_hz=pitch_hz, dil=dil,
        include_opening_head=True, opening_head_ms=OPENING_HEAD_MS
    )

    # SEG 4: [ɾ] tap
    seg_r = synth_R(
        F_prev=VS_AA_F, F_next=VS_A_F,
        pitch_hz=pitch_hz, dil=dil
    )

    # SEG 5: [ɑ]
    seg_a = synth_A(
        F_prev=VS_R_F, F_next=VS_M_F,
        pitch_hz=pitch_hz, dil=dil
    )

    # SEG 6: [m] + word-final release
    seg_m = synth_M(
        F_prev=VS_A_F, pitch_hz=pitch_hz, dil=dil,
        include_release=True
    )

    word = np.concatenate([seg_h, seg_oo, seg_t, seg_aa, seg_r, seg_a, seg_m])
    word = norm_to_peak(word, 0.75)

    if with_room:
        word = apply_simple_room(word)

    return f32(word)

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print()
    print("=" * 70)
    print("HOTĀRAM v9 — Sweet Spot Reconstruction")
    print("=" * 70)
    print()
    print("ITERATION v8→v9:")
    print("  Problem: [t] was clicky")
    print()
    print("  Root causes:")
    print("    1. v8 concatenated SEPARATE closure/burst/aspiration arrays")
    print("       Pluck Artifact: 'ONE continuous noise buffer.'")
    print("    2. Burst gain 0.38 — RATNADHĀTAMAM v17 uses 0.15")
    print("    3. Missing Phase E voicing fade-in during VOT")
    print()
    print("  Fix: _synth_unified_voiceless_stop() from RATNADHĀTAMAM v17")
    print("       ONE noise buffer → ONE envelope → formant filter")
    print("       Burst gain 0.15 (observer position)")
    print("       Phase E: voicing fades in additively during VOT")
    print()
    print("  [t] VERIFIED parameters (from RATNADHĀTAMAM v17):")
    print(f"    Burst gain:     {VS_T_BURST_GAIN}")
    print(f"    Burst decay:    {VS_T_BURST_DECAY} Hz")
    print(f"    Preburst:       {VS_T_PREBURST_MS} ms, amp {VS_T_PREBURST_AMP}")
    print(f"    Subglottal:     {VS_T_SUBGLOTTAL_FLOOR}")
    print(f"    Burst formants: {VS_T_BURST_F} Hz")
    print()
    print("  Boundary chain (all joins near zero):")
    print("    [oː]→tail→~0  +  0.001→[t]→0.001  +  ~0→head→[aː]")
    print()
    print("  Segment map:")
    for i, (name, dur) in enumerate(zip(SEG_NAMES, SEG_DURATIONS_MS)):
        tag = " [UNVOICED]" if i in UNVOICED_INDICES else ""
        print(f"    SEG {i}: {name:35s} {dur:6.1f} ms{tag}")
    total = sum(SEG_DURATIONS_MS)
    print(f"    {'TOTAL':35s}  {total:6.1f} ms")
    print()

    word_dry  = synth_hotaram(PITCH_HZ, 1.0, with_room=False)
    word_room = synth_hotaram(PITCH_HZ, 1.0, with_room=True)
    word_perf = synth_hotaram(PITCH_HZ, 2.5, with_room=True)
    word_slow = ola_stretch(word_dry, 6.0)

    write_wav("output_play/hotaram_v9_dry.wav", word_dry)
    write_wav("output_play/hotaram_v9_room.wav", word_room)
    write_wav("output_play/hotaram_v9_performance.wav", word_perf)
    write_wav("output_play/hotaram_v9_slow.wav", word_slow)

    print()
    print("  Ancestor: RATNADHĀTAMAM v17 _synth_unified_voiceless_stop()")
    print("            Origin Artifact ([h] distance zero)")
    print("            Observer Position Artifact (radiation LPF)")
    print("            Pluck Artifact (Unified Source composition)")
    print()
    print("=" * 70)
    print("v9 synthesis complete.")
    print("Next: hotaram_diagnostic.py v3 (verify click elimination)")
    print("=" * 70)
    print()
