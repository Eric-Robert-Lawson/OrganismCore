#!/usr/bin/env python3
"""
================================================================
DEVAM v1 — Principles-First Reconstruction
Rigveda 1.1.1, word 6
[deːvɑm] — "the god"

ARCHITECTURE:
  ALL VOICED — no pluck, no closing tail / opening head.
  Voiced stops are NOT plucks (Pluck Artifact Part VI).

  [d] uses crossfade cutback architecture (from DEVAM v13):
    Phase 1: Voice bar (closure) — voiced murmur behind closed dental
    Phase 2: Burst — brief dental transient
    Phase 3: Crossfade cutback — closed tract → open tract
      v13 physics: closed tract ATTENUATES → quieter than open
      Equal-power crossfade: cos/sin ensures smooth energy transition
      Open tract target: [eː] formants (following vowel)

  [eː] long close-mid front unrounded vowel — NEW PHONEME
  [v] voiced labiodental approximant — NEW CONSONANT CLASS
  [ɑ] short open central — verified (AGNI, HOTĀRAM, RATNADHĀTAMAM)
  [m] bilabial nasal — verified (RATNADHĀTAMAM, HOTĀRAM, PUROHITAM)

  Coarticulation: each vowel/sonorant receives F_prev/F_next
  for formant blending at boundaries.

  Infrastructure: canonical from HOTĀRAM v9
    - rosenberg_pulse: differentiated Rosenberg glottal source
    - apply_formants: parallel IIR resonators, b = [1.0 - r]
    - iir_notch: antiformant for nasals
    - norm_to_peak: amplitude normalization
    - Word-level norm_to_peak(0.75)

  Ancestors:
    HOTĀRAM v9 (infrastructure, formant synthesis, wav output)
    DEVAM v13 (crossfade cutback [d], energy correction)
    RATNADHĀTAMAM v17 ([m] parameters, [ɑ] formants)
    PUROHITAM v5 ([m] antiformant)

February 2026
================================================================
"""

import numpy as np
from scipy.signal import lfilter, butter
import wave as wave_module
import os

SR    = 44100
DTYPE = np.float32

os.makedirs("output_play", exist_ok=True)

# ============================================================================
# PHONEME PARAMETERS
# ============================================================================

# ── [d] voiced dental stop — v1 (from DEVAM v13 crossfade cutback) ──────────

VS_D_CLOSURE_MS    = 20.0       # brief prevoicing (voice bar)
VS_D_BURST_MS      = 8.0        # dental burst transient
VS_D_CUTBACK_MS    = 30.0       # crossfade: closed→open tract

VS_D_VOICEBAR_F    = 250.0      # voice bar: single low resonance
VS_D_VOICEBAR_BW   = 80.0
VS_D_VOICEBAR_G    = 12.0
VS_D_MURMUR_PEAK   = 0.25       # voice bar amplitude

VS_D_BURST_PEAK    = 0.15       # observer level (same as [t] in HOTĀRAM)
VS_D_BURST_F       = [1500.0, 3500.0, 5000.0, 6500.0]   # dental burst locus
VS_D_BURST_B       = [ 400.0,  600.0,  800.0, 1000.0]
VS_D_BURST_G       = [   4.0,   12.0,    5.0,    1.5]
VS_D_BURST_DECAY   = 170.0      # spike→noise transition rate

# v13 energy correction: closed tract is QUIETER than open tract
VS_D_CLOSED_F      = [250.0,  800.0, 2200.0, 3200.0]
VS_D_CLOSED_B      = [150.0,  250.0,  300.0,  350.0]
VS_D_CLOSED_G      = [ 10.0,    3.0,    0.8,    0.3]
VS_D_CLOSED_PEAK   = 0.40       # closed tract attenuates → quiet
VS_D_OPEN_PEAK     = 0.65       # open tract → louder
VS_D_CUTBACK_PEAK  = 0.55       # overall cutback normalization

# ── [eː] long close-mid front unrounded — NEW PHONEME ──────────────────────
#    Śikṣā: tālavya component (palatal/front)
#    F1 low (close), F2 high (front), F3 high
VS_EE_F        = [420.0, 1750.0, 2650.0, 3350.0]
VS_EE_B        = [100.0,  140.0,  200.0,  260.0]
VS_EE_GAINS    = [ 14.0,    8.0,    1.5,    0.5]
VS_EE_DUR_MS   = 90.0
VS_EE_COART_ON  = 0.10
VS_EE_COART_OFF = 0.10

# ── [v] voiced labiodental approximant ──────────────────────────────────────
#    Constriction at labiodental: F1 low, F2 mid (~1500)
#    Wider bandwidths than vowels (more damped)
VS_V_F         = [300.0, 1500.0, 2400.0, 3100.0]
VS_V_B         = [180.0,  350.0,  400.0,  400.0]
VS_V_GAINS     = [ 10.0,    5.0,    1.5,    0.5]
VS_V_DUR_MS    = 60.0
VS_V_COART_ON  = 0.18
VS_V_COART_OFF = 0.18

# ── [ɑ] short open central — VERIFIED (AGNI, HOTĀRAM, RATNADHĀTAMAM) ──────
VS_A_F         = [700.0, 1100.0, 2550.0, 3400.0]
VS_A_B         = [130.0,  160.0,  220.0,  280.0]
VS_A_GAINS     = [ 16.0,    6.0,    1.5,    0.5]
VS_A_DUR_MS    = 55.0
VS_A_COART_ON  = 0.12
VS_A_COART_OFF = 0.12

# ── [m] bilabial nasal — VERIFIED (RATNADHĀTAMAM, HOTĀRAM, PUROHITAM) ─────
VS_M_F         = [250.0,  900.0, 2200.0, 3000.0]
VS_M_B         = [100.0,  200.0,  300.0,  350.0]
VS_M_GAINS     = [  8.0,    2.5,    0.5,    0.2]
VS_M_DUR_MS    = 60.0
VS_M_ANTI_F    = 800.0
VS_M_ANTI_BW   = 200.0
VS_M_COART_ON  = 0.12

PITCH_HZ = 120.0
DIL      = 1.0

# ============================================================================
# SEGMENT MAP — DEVAM [deːvɑm]
# ============================================================================

SEG_D  = 0    # [d] voiced dental stop (closure + burst + cutback)
SEG_EE = 1    # [eː] long close-mid front vowel
SEG_V  = 2    # [v] labiodental approximant
SEG_A  = 3    # [ɑ] short open central vowel
SEG_M  = 4    # [m] bilabial nasal

SEG_NAMES = [
    "[d] voiced dental stop",
    "[eː] long close-mid front",
    "[v] labiodental approximant",
    "[ɑ] short open central",
    "[m] bilabial nasal",
]

VS_D_TOTAL_MS = VS_D_CLOSURE_MS + VS_D_BURST_MS + VS_D_CUTBACK_MS  # 58ms

SEG_DURATIONS_MS = [
    VS_D_TOTAL_MS,       # 58ms
    VS_EE_DUR_MS,        # 90ms
    VS_V_DUR_MS,         # 60ms
    VS_A_DUR_MS,         # 55ms
    VS_M_DUR_MS,         # 60ms
]

# All segments voiced — no unvoiced indices
UNVOICED_INDICES = set()

# ============================================================================
# DSP INFRASTRUCTURE (canonical from HOTĀRAM v9)
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
    """Differentiated Rosenberg glottal pulse train."""
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
    """Parallel IIR resonator bank — canonical from HOTĀRAM v9."""
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
    """IIR notch filter for nasal antiformant."""
    w0 = 2.0 * np.pi * fc / sr
    r = max(0.0, min(0.999, 1.0 - np.pi * bw / sr))
    b_n = [1.0, -2.0 * np.cos(w0), 1.0]
    a_n = [1.0, -2.0 * r * np.cos(w0), r * r]
    return f32(lfilter(b_n, a_n, sig.astype(float)))


def norm_to_peak(sig, target_peak):
    """Normalize signal to target peak amplitude."""
    mx = np.max(np.abs(sig))
    if mx > 1e-8:
        return f32(sig / mx * target_peak)
    return f32(sig)


def ola_stretch(sig, factor=6.0, sr=SR):
    """Overlap-add time stretch for slow playback."""
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
    """Temple courtyard reverb — canonical."""
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
# PHONEME SYNTHESIS FUNCTIONS
# ============================================================================

def synth_D(F_next=None, pitch_hz=PITCH_HZ, dil=DIL, sr=SR):
    """
    [d] — voiced dental stop — crossfade cutback architecture.

    Voiced stops are NOT plucks (Pluck Artifact Part VI).
    Voicing is maintained throughout: voice bar → burst → crossfade.

    v13 physics: closed tract ATTENUATES sound → quieter than open tract.
    Equal-power crossfade (cos/sin) ensures smooth energy transition.
    Open tract target: F_next formants (following vowel).

    Phases:
      1. Closure (20ms): voiced murmur behind closed dental
      2. Burst (8ms): brief dental transient (spike + turbulence)
      3. Cutback (30ms): crossfade closed→open tract voicing
    """
    n_closure = int(VS_D_CLOSURE_MS * dil / 1000.0 * sr)
    n_burst   = int(VS_D_BURST_MS * dil / 1000.0 * sr)
    n_cutback = int(VS_D_CUTBACK_MS * dil / 1000.0 * sr)

    f_next = F_next if F_next is not None else VS_EE_F

    # ── Phase 1: Voice bar (closure) ──────────────────────────
    # Voiced murmur: low-frequency resonance behind closed dental
    if n_closure > 0:
        src_cl = rosenberg_pulse(n_closure, pitch_hz, sr=sr)
        murmur = apply_formants(
            src_cl,
            [VS_D_VOICEBAR_F],
            [VS_D_VOICEBAR_BW],
            [VS_D_VOICEBAR_G],
            sr=sr)
        # Gentle onset ramp (word-initial [d])
        env_cl = np.ones(n_closure, dtype=float)
        ramp_n = max(1, int(0.3 * n_closure))
        env_cl[:ramp_n] = np.linspace(0.3, 1.0, ramp_n)
        murmur = f32(murmur * env_cl)
        closure = norm_to_peak(murmur, VS_D_MURMUR_PEAK)
    else:
        closure = np.array([], dtype=DTYPE)

    # ── Phase 2: Burst (dental transient) ─────────────────────
    # Brief spike + turbulence filtered through dental formants
    spike = np.zeros(max(n_burst, 16), dtype=float)
    spike[0:3] = [1.0, 0.6, 0.3]
    turbulence = np.random.randn(len(spike))
    turbulence_filt = apply_formants(
        turbulence, VS_D_BURST_F, VS_D_BURST_B, VS_D_BURST_G, sr=sr)
    t_b = np.arange(len(spike)) / sr
    mix_env = np.exp(-t_b * VS_D_BURST_DECAY)
    burst_raw = spike * mix_env + turbulence_filt * (1.0 - mix_env) * 0.30
    burst = norm_to_peak(f32(burst_raw), VS_D_BURST_PEAK)

    # ── Phase 3: Crossfade cutback ────────────────────────────
    # closed-tract voicing → open-tract voicing (following vowel formants)
    # v13 physics: closed tract attenuates → VS_D_CLOSED_PEAK < VS_D_OPEN_PEAK
    if n_cutback > 0:
        src_cb = rosenberg_pulse(n_cutback, pitch_hz, sr=sr)

        # Signal A: closed-tract voicing (quiet — tract attenuates)
        sig_closed = apply_formants(
            src_cb, VS_D_CLOSED_F, VS_D_CLOSED_B, VS_D_CLOSED_G, sr=sr)
        sig_closed = norm_to_peak(sig_closed, VS_D_CLOSED_PEAK)

        # Signal B: open-tract voicing (louder — tract is open)
        # Uses following vowel formants for coarticulation
        sig_open = apply_formants(
            src_cb, list(f_next),
            [100.0, 140.0, 200.0, 260.0],
            [14.0, 8.0, 1.5, 0.5], sr=sr)
        sig_open = norm_to_peak(sig_open, VS_D_OPEN_PEAK)

        # Equal-power crossfade: cos(θ)² + sin(θ)² = 1
        t_fade = np.linspace(0.0, np.pi / 2.0, n_cutback)
        fade_out = np.cos(t_fade).astype(DTYPE)    # closed → 0
        fade_in  = np.sin(t_fade).astype(DTYPE)    # open → 1

        cutback = f32(sig_closed * fade_out + sig_open * fade_in)

        # Gentle amplitude ramp (v13: 0.6→1.0, less dramatic)
        cb_env = np.linspace(0.6, 1.0, n_cutback).astype(DTYPE)
        cutback = f32(cutback * cb_env)
        cutback = norm_to_peak(cutback, VS_D_CUTBACK_PEAK)
    else:
        cutback = np.array([], dtype=DTYPE)

    out = np.concatenate([closure, burst, cutback])
    return f32(out)


def synth_EE(F_prev=None, F_next=None,
             pitch_hz=PITCH_HZ, dil=DIL, sr=SR):
    """
    [eː] — long close-mid front unrounded vowel — NEW.

    Śikṣā: tālavya component (palatal/front)
    F1 ≈ 420 Hz (close-mid), F2 ≈ 1750 Hz (front), F3 ≈ 2650 Hz

    Coarticulation: F_prev/F_next blend at 10% weight.
    """
    n = int(VS_EE_DUR_MS * dil / 1000.0 * sr)
    src = rosenberg_pulse(n, pitch_hz, oq=0.65, sr=sr)

    f_mean = list(VS_EE_F)
    if F_prev is not None:
        for k in range(min(len(F_prev), len(VS_EE_F))):
            f_mean[k] = (F_prev[k] * VS_EE_COART_ON
                         + VS_EE_F[k] * (1.0 - VS_EE_COART_ON))
    if F_next is not None:
        for k in range(min(len(F_next), len(VS_EE_F))):
            f_mean[k] = (f_mean[k] * (1.0 - VS_EE_COART_OFF)
                         + F_next[k] * VS_EE_COART_OFF)

    out = apply_formants(src, f_mean, VS_EE_B, VS_EE_GAINS, sr=sr)
    out = norm_to_peak(out, 0.72)
    return f32(out)


def synth_V(F_prev=None, F_next=None,
            pitch_hz=PITCH_HZ, dil=DIL, sr=SR):
    """
    [v] — voiced labiodental approximant — NEW CONSONANT CLASS.

    Constriction at labiodental place: F1 low, F2 mid (~1500 Hz).
    Wider bandwidths than vowels (more damped due to constriction).
    Gentle attack/release envelope (approximant, not stop).

    Coarticulation: 18% weight from neighbors (stronger than vowels —
    approximants are more influenced by context).
    """
    n = int(VS_V_DUR_MS * dil / 1000.0 * sr)
    src = rosenberg_pulse(n, pitch_hz, oq=0.65, sr=sr)

    f_mean = list(VS_V_F)
    if F_prev is not None:
        for k in range(min(len(F_prev), len(VS_V_F))):
            f_mean[k] = (F_prev[k] * VS_V_COART_ON
                         + VS_V_F[k] * (1.0 - VS_V_COART_ON))
    if F_next is not None:
        for k in range(min(len(F_next), len(VS_V_F))):
            f_mean[k] = (f_mean[k] * (1.0 - VS_V_COART_OFF)
                         + F_next[k] * VS_V_COART_OFF)

    out = apply_formants(src, f_mean, VS_V_B, VS_V_GAINS, sr=sr)

    # Gentle attack/release: approximant has smooth transitions
    env = np.ones(n, dtype=float)
    atk = min(int(0.015 * sr), n // 4)
    rel = min(int(0.015 * sr), n // 4)
    if atk > 0:
        env[:atk] = np.linspace(0.0, 1.0, atk)
    if rel > 0:
        env[-rel:] = np.linspace(1.0, 0.0, rel)
    out = f32(out * env)

    # [v] is quieter than vowels due to constriction
    out = norm_to_peak(out, 0.62)
    return f32(out)


def synth_A(F_prev=None, F_next=None,
            pitch_hz=PITCH_HZ, dil=DIL, sr=SR):
    """
    [ɑ] — short open central unrounded — VERIFIED.

    F1 ≈ 700 Hz (open), F2 ≈ 1100 Hz (central/back)
    Identical formant structure to [aː]; distinguished by duration only.
    """
    n = int(VS_A_DUR_MS * dil / 1000.0 * sr)
    src = rosenberg_pulse(n, pitch_hz, oq=0.65, sr=sr)

    f_mean = list(VS_A_F)
    if F_prev is not None:
        for k in range(min(len(F_prev), len(VS_A_F))):
            f_mean[k] = (F_prev[k] * VS_A_COART_ON
                         + VS_A_F[k] * (1.0 - VS_A_COART_ON))
    if F_next is not None:
        for k in range(min(len(F_next), len(VS_A_F))):
            f_mean[k] = (f_mean[k] * (1.0 - VS_A_COART_OFF)
                         + F_next[k] * VS_A_COART_OFF)

    out = apply_formants(src, f_mean, VS_A_B, VS_A_GAINS, sr=sr)
    out = norm_to_peak(out, 0.72)
    return f32(out)


def synth_M(F_prev=None, pitch_hz=PITCH_HZ, dil=DIL, sr=SR):
    """
    [m] — bilabial nasal — VERIFIED (word-final, no release needed here).

    Low F1 (nasal murmur ≈ 250 Hz), antiformant at 800 Hz.
    Word-final position in DEVAM.
    """
    n = int(VS_M_DUR_MS * dil / 1000.0 * sr)
    src = rosenberg_pulse(n, pitch_hz, oq=0.65, sr=sr)

    f_mean = list(VS_M_F)
    if F_prev is not None:
        for k in range(min(len(F_prev), len(VS_M_F))):
            f_mean[k] = (F_prev[k] * VS_M_COART_ON
                         + VS_M_F[k] * (1.0 - VS_M_COART_ON))

    out = apply_formants(src, f_mean, VS_M_B, VS_M_GAINS, sr=sr)

    # Antiformant: nasal coupling creates spectral zero near 800 Hz
    out = iir_notch(out, VS_M_ANTI_F, VS_M_ANTI_BW, sr=sr)

    out = norm_to_peak(out, 0.42)
    return f32(out)


# ============================================================================
# WORD SYNTHESIS
# ============================================================================

def synth_devam(pitch_hz=PITCH_HZ, dil=DIL, with_room=False, sr=SR):
    """
    DEVAM [deːvɑm] v1 — Principles-First Reconstruction

    [d] → [eː] → [v] → [ɑ] → [m]

    All voiced. No pluck. No closing tail / opening head.
    [d] crossfade cutback ends on [eː] formants → smooth join.
    Coarticulation chain propagates formant context through all segments.
    """

    # SEG 0: [d] voiced dental stop
    # F_next = [eː] formants (crossfade target)
    seg_d = synth_D(F_next=VS_EE_F, pitch_hz=pitch_hz, dil=dil, sr=sr)

    # SEG 1: [eː] long close-mid front
    # F_prev = [d] dental locus (use closed-tract formants as proxy)
    # F_next = [v] formants
    seg_ee = synth_EE(
        F_prev=VS_D_CLOSED_F, F_next=VS_V_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)

    # SEG 2: [v] labiodental approximant
    # F_prev = [eː], F_next = [ɑ]
    seg_v = synth_V(
        F_prev=VS_EE_F, F_next=VS_A_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)

    # SEG 3: [ɑ] short open central
    # F_prev = [v], F_next = [m]
    seg_a = synth_A(
        F_prev=VS_V_F, F_next=VS_M_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)

    # SEG 4: [m] bilabial nasal (word-final)
    # F_prev = [ɑ]
    seg_m = synth_M(
        F_prev=VS_A_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)

    # ── Concatenate and normalize ─────────────────────────────
    word = np.concatenate([seg_d, seg_ee, seg_v, seg_a, seg_m])

    # Word-level norm_to_peak(0.75) — canonical
    word = norm_to_peak(word, 0.75)

    if with_room:
        word = apply_simple_room(word, rt60=1.5, direct_ratio=0.55, sr=sr)

    return f32(word)


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print()
    print("=" * 70)
    print("DEVAM v1 — Principles-First Reconstruction")
    print("Rigveda 1.1.1, word 6")
    print("[deːvɑm] — \"the god\"")
    print("=" * 70)
    print()
    print("Architecture:")
    print("  [d] crossfade cutback (voiced stop — NOT pluck)")
    print("    closure: 20ms voice bar @ 0.25")
    print("    burst:    8ms dental @ 0.15 (observer level)")
    print("    cutback: 30ms closed(0.40) → open(0.65)")
    print("  [eː] long close-mid front (NEW) F2≈1750 Hz")
    print("  [v]  labiodental approximant (NEW) F2≈1500 Hz")
    print("  [ɑ]  short open central (verified)")
    print("  [m]  bilabial nasal (verified)")
    print()
    print("Ancestors:")
    print("  HOTĀRAM v9 (infrastructure)")
    print("  DEVAM v13 (crossfade cutback, v13 energy fix)")
    print("  RATNADHĀTAMAM v17 (formant params)")
    print()

    # ── Standard outputs ──────────────────────────────────────
    dry = synth_devam(with_room=False)
    hall = synth_devam(with_room=True)
    write_wav("output_play/devam_v1_dry.wav", dry)
    write_wav("output_play/devam_v1_hall.wav", hall)
    write_wav("output_play/devam_v1_slow6x.wav", ola_stretch(dry, 6.0))
    write_wav("output_play/devam_v1_slow12x.wav", ola_stretch(dry, 12.0))

    # ── Performance tempo (dil=2.5) ───────────────────────────
    perf = synth_devam(dil=2.5, with_room=False)
    perf_hall = synth_devam(dil=2.5, with_room=True)
    write_wav("output_play/devam_v1_perf.wav", perf)
    write_wav("output_play/devam_v1_perf_hall.wav", perf_hall)
    write_wav("output_play/devam_v1_perf_slow6x.wav",
              ola_stretch(perf, 6.0))

    # ── Isolated phonemes ─────────────────────────────────────
    for fn, label in [
        (lambda: synth_D(F_next=VS_EE_F), "devam_v1_d_iso"),
        (lambda: synth_EE(), "devam_v1_ee_iso"),
        (lambda: synth_V(), "devam_v1_v_iso"),
        (lambda: synth_A(), "devam_v1_a_iso"),
        (lambda: synth_M(), "devam_v1_m_iso"),
    ]:
        sig = fn()
        sig = norm_to_peak(sig, 0.75)
        write_wav(f"output_play/{label}.wav", sig)
        write_wav(f"output_play/{label}_slow6x.wav",
                  ola_stretch(sig, 6.0))
        write_wav(f"output_play/{label}_slow12x.wav",
                  ola_stretch(sig, 12.0))

    print()
    print("Segment map:")
    for i, (name, dur) in enumerate(zip(SEG_NAMES, SEG_DURATIONS_MS)):
        print(f"  SEG {i}: {name:40s} {dur:6.1f} ms")
    print(f"  {'TOTAL':>47s} {sum(SEG_DURATIONS_MS):6.1f} ms")
    print()
    print("Done.")
    print("  afplay output_play/devam_v1_dry.wav")
    print("  afplay output_play/devam_v1_perf_hall.wav")
    print("  afplay output_play/devam_v1_d_iso_slow6x.wav")
