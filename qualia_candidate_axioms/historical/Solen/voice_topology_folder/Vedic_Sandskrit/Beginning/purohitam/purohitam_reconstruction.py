#!/usr/bin/env python3
"""
PUROHITAM v3 — PLUCK ARCHITECTURE
Vedic Sanskrit: purohitam [puroːhitɑm]
Rigveda 1.1.1, word 4
"the household priest" (accusative singular)

v2 → v3 CHANGES:

  1. [p] AND [t] — PLUCK ARCHITECTURE

     v2 used v6 architecture: closure (silence + pre-burst noise) +
     burst (spike + turbulence + onset ramp) + VOT (voicing fade-in).
     Three concatenated arrays. The pre-burst noise and onset ramp
     were patches to mask the concatenation boundary.

     v3 INSIGHT (from RATNADHATAMAM v16 → ṚTVIJAM v8):
     A voiceless stop is not three separate arrays concatenated.
     It is a moment of release between two continuous voiced segments.

     The preceding vowel owns the closure — its closing tail models
     the articulatory gesture (lips closing for [p], tongue rising
     for [t]). Core voicing + RMS fade proves the vocal folds were
     vibrating as the articulator closed.

     The following segment owns the VOT — its opening head models
     the vocal folds resuming vibration after the voiceless release.
     Rising amplitude proves the opening.

     The stop itself is only the burst — the pluck. The instant
     compressed air is released through the constriction.

     No silent closure array. No VOT array. No pre-burst noise.
     No onset ramp. No concatenation boundaries to patch.

  2. CLOSING TAILS AND OPENING HEADS

     Vowels and sonorants adjacent to stops get composite segments:
       [u] + closing tail (25ms fade before [ɾ] — NOT before a stop)
       [oː] + closing tail (25ms fade before [h] — NOT before a stop)
       NOTE: [u] is NOT before a stop, [oː] is NOT before a stop

     Wait — in purohitam [puroːhitɑm]:
       [p] is word-initial (no preceding segment)
       [t] is preceded by [i]
       
     So the closing tails are:
       [i] + closing tail (25ms fade) → [t] PLUCK
       
     And the opening heads are:
       [p] PLUCK → head + [u] (opening head 15ms rise)
       [t] PLUCK → head + [ɑ] (opening head 15ms rise)

  3. [h] VOICELESS GLOTTAL FRICATIVE

     [h] is not a stop. It has no burst, no closure, no pluck.
     It is noise shaped by the following vowel's formants.
     Unchanged from v2.

  4. WORD-INITIAL [p]

     [p] is the first phoneme. There is no preceding segment to
     own the closure. The closure is silence — the word begins
     from nothing. This is the one case where the stop includes
     a brief silent onset (10ms) before the burst. This is not
     a concatenation boundary — it's the physical reality of a
     word-initial voiceless stop.

  5. ALL OTHER PHONEMES — unchanged from v2.

SEGMENT MAP (v3 pluck architecture):

  [p] PLUCK (word-initial)   10ms silence + 8ms burst = 18ms
  head + [u]                 15ms rise + 50ms = 65ms
  [ɾ]                        30ms
  [oː]                       100ms
  [h]                         65ms
  [i] + closing tail          50ms + 25ms = 75ms
  [t] PLUCK                   7ms burst only
  head + [ɑ]                  15ms rise + 55ms = 70ms
  [m]                          60ms + 20ms release = 80ms

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

# [p] voiceless bilabial stop — v3 PLUCK
VS_P_BURST_MS    = 8.0
VS_P_BURST_F     = [600.0, 1300.0, 2100.0, 3000.0]
VS_P_BURST_B     = [300.0,  300.0,  400.0,  500.0]
VS_P_BURST_G     = [  6.0,   16.0,    4.0,    1.5]
VS_P_BURST_DECAY = 130.0
VS_P_BURST_GAIN  = 0.20
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

# [t] voiceless dental stop — v3 PLUCK
VS_T_BURST_MS   = 7.0
VS_T_BURST_F     = [1500.0, 3500.0, 5000.0, 6500.0]
VS_T_BURST_B     = [ 400.0,  600.0,  800.0, 1000.0]
VS_T_BURST_G     = [   4.0,   14.0,    6.0,    2.0]
VS_T_BURST_DECAY = 170.0
VS_T_BURST_GAIN  = 0.20
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

# Pluck architecture parameters
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
    The closing tail is the last tail_ms of the segment's voicing,
    faded to near-zero. Models the articulator closing for a stop.
    
    Returns the composite: voiced_seg + closing_tail.
    The core is the original segment. The tail is new.
    """
    n_tail = int(tail_ms / 1000.0 * sr)
    if n_tail < 1:
        return voiced_seg

    # Generate tail from the same source as the segment's end
    # Use the last pitch period as template, faded
    period = int(sr / PITCH_HZ)
    if len(voiced_seg) >= period:
        # Repeat the last period, fading
        template = voiced_seg[-period:]
        n_reps = (n_tail // period) + 2
        tail_src = np.tile(template, n_reps)[:n_tail]
    else:
        tail_src = np.zeros(n_tail, dtype=DTYPE)

    # Squared fade envelope (smooth, no click)
    fade = np.linspace(1.0, 0.0, n_tail) ** 2
    tail = f32(tail_src * fade)

    return f32(np.concatenate([voiced_seg, tail]))

def make_opening_head(voiced_seg, head_ms=OPENING_HEAD_MS, sr=SR):
    """
    Prepend an opening head to a voiced segment.
    The opening head models the vocal folds resuming vibration
    after a voiceless stop. Squared amplitude rise.
    
    Returns the composite: opening_head + voiced_seg.
    The head is new. The core is the original segment.
    """
    n_head = int(head_ms / 1000.0 * sr)
    if n_head < 1:
        return voiced_seg

    # Generate head from the segment's beginning source
    period = int(sr / PITCH_HZ)
    if len(voiced_seg) >= period:
        template = voiced_seg[:period]
        n_reps = (n_head // period) + 2
        head_src = np.tile(template, n_reps)[:n_head]
    else:
        head_src = np.zeros(n_head, dtype=DTYPE)

    # Squared rise envelope
    rise = np.linspace(0.0, 1.0, n_head) ** 2
    head = f32(head_src * rise)

    return f32(np.concatenate([head, voiced_seg]))

# ============================================================================
# PHONEME SYNTHESIS FUNCTIONS
# ============================================================================

def synth_P(pitch_hz=PITCH_HZ, dil=DIL, word_initial=True):
    """
    [p] voiceless bilabial stop — v3 PLUCK

    Word-initial: 10ms silence + 8ms burst.
    The silence is not a concatenation patch — it is the physical
    reality that the word begins from nothing. The lips are closed,
    there is no preceding sound, then they release.

    Non-word-initial: burst only (8ms). The preceding segment's
    closing tail handles the closure.
    """
    n_b = int(VS_P_BURST_MS * dil / 1000.0 * SR)

    # Spike + turbulence burst (bilabial locus)
    spike = np.zeros(max(n_b, 16), dtype=float)
    spike[0:3] = [1.0, 0.6, 0.3]

    turbulence = np.random.randn(len(spike))
    turbulence_filt = apply_formants(turbulence, VS_P_BURST_F,
                                     VS_P_BURST_B, VS_P_BURST_G)

    t_b = np.arange(len(spike)) / SR
    mix_env = np.exp(-t_b * VS_P_BURST_DECAY)
    burst = spike * mix_env + turbulence_filt * (1.0 - mix_env) * 0.30

    burst = f32(burst * VS_P_BURST_GAIN)

    if word_initial:
        n_sil = int(VS_P_INITIAL_SILENCE_MS * dil / 1000.0 * SR)
        silence = np.zeros(n_sil, dtype=DTYPE)
        out = np.concatenate([silence, burst])
    else:
        out = burst

    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.55
    return f32(out)


def synth_U(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=DIL,
            closing_for_stop=False):
    """
    [u] short close back rounded (VERIFIED PUROHITAM v1)

    closing_for_stop=True: append 25ms closing tail.
    """
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

    # Tap dip
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
    """
    [i] short close front unrounded (VERIFIED AGNI)

    closing_for_stop=True: append 25ms closing tail.
    """
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


def synth_T(pitch_hz=PITCH_HZ, dil=DIL):
    """
    [t] voiceless dental stop — v3 PLUCK

    Burst only (7ms). No closure, no VOT.
    The preceding [i] closing tail owns the closure.
    The following [ɑ] opening head owns the VOT.
    """
    n_b = int(VS_T_BURST_MS * dil / 1000.0 * SR)

    # Spike + turbulence burst (dental locus)
    spike = np.zeros(max(n_b, 16), dtype=float)
    spike[0:3] = [1.0, 0.6, 0.3]

    turbulence = np.random.randn(len(spike))
    turbulence_filt = apply_formants(turbulence, VS_T_BURST_F,
                                     VS_T_BURST_B, VS_T_BURST_G)

    t_b = np.arange(len(spike)) / SR
    mix_env = np.exp(-t_b * VS_T_BURST_DECAY)
    burst = spike * mix_env + turbulence_filt * (1.0 - mix_env) * 0.30

    burst = f32(burst * VS_T_BURST_GAIN)

    mx = np.max(np.abs(burst))
    if mx > 1e-8:
        burst = burst / mx * 0.55
    return f32(burst)


def synth_A(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=DIL,
            opening_from_stop=False):
    """
    [ɑ] short open central unrounded (VERIFIED AGNI)

    opening_from_stop=True: prepend 15ms opening head.
    """
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
    """
    [m] bilabial nasal (VERIFIED PUROHITAM v1)

    word_final=True: adds 20ms release tail (lips open, nasal fades).
    """
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
    PUROHITAM [puroːhitɑm] — v3 PLUCK ARCHITECTURE
    Rigveda 1.1.1, word 4
    Syllables: PU-RŌ-HI-TAM

    v3 segment map:
      [p] PLUCK (word-initial)    10ms silence + 8ms burst = 18ms
      head + [u]                  15ms rise + 50ms = 65ms
      [ɾ]                         30ms
      [oː]                        100ms
      [h]                          65ms
      [i] + closing tail           50ms + 25ms = 75ms
      [t] PLUCK                    7ms burst only
      head + [ɑ]                   15ms rise + 55ms = 70ms
      [m] + release                60ms + 20ms = 80ms

    Coarticulation context:
      [p] → [u] → [ɾ] → [oː] → [h] → [i] → [t] → [ɑ] → [m]
    """
    segs = [
        # PU-
        synth_P(pitch_hz=pitch_hz, dil=dil, word_initial=True),
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
        synth_T(pitch_hz=pitch_hz, dil=dil),
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
    print("PUROHITAM v3 — PLUCK ARCHITECTURE")
    print("=" * 70)
    print()
    print("v2→v3 CHANGES:")
    print()
    print("  [p] and [t] — PLUCK ARCHITECTURE:")
    print("    The stop is a moment of release, not three arrays.")
    print("    Preceding vowel owns the closure (closing tail).")
    print("    Following vowel owns the VOT (opening head).")
    print("    The stop itself is only the burst — the pluck.")
    print()
    print("  Segment map:")
    print("    [p] PLUCK (word-initial)  10ms silence + 8ms burst")
    print("    head + [u]               15ms rise + 50ms")
    print("    [ɾ]                       30ms")
    print("    [oː]                      100ms")
    print("    [h]                        65ms")
    print("    [i] + closing tail         50ms + 25ms")
    print("    [t] PLUCK                  7ms burst only")
    print("    head + [ɑ]                 15ms rise + 55ms")
    print("    [m] + release              60ms + 20ms")
    print()
    print("  Word-initial [p]:")
    print("    10ms silence before burst.")
    print("    The word begins from nothing. The lips are closed.")
    print("    No preceding segment → no closing tail.")
    print("    This is not a patch. It is the physics.")
    print()
    print("  All other phonemes unchanged from v2.")
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

    write_wav("output_play/purohitam_v3_dry.wav", word_dry)
    write_wav("output_play/purohitam_v3_slow6x.wav", word_slow)
    write_wav("output_play/purohitam_v3_slow12x.wav", word_slow12)
    write_wav("output_play/purohitam_v3_hall.wav", word_hall)
    write_wav("output_play/purohitam_v3_perf.wav", word_perf)
    write_wav("output_play/purohitam_v3_perf_hall.wav", word_perf_hall)

    # Isolated phonemes for diagnostic
    p_iso = synth_P(word_initial=True)
    t_iso = synth_T()

    for sig, name in [
        (p_iso, "purohitam_v3_p_iso"),
        (t_iso, "purohitam_v3_t_iso"),
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
    print("v3 synthesis complete.")
    print()
    print("LISTEN:")
    print("  afplay output_play/purohitam_v3_slow6x.wav")
    print("  afplay output_play/purohitam_v3_slow12x.wav")
    print("  afplay output_play/purohitam_v3_perf_hall.wav")
    print("  afplay output_play/purohitam_v3_p_iso_slow12x.wav")
    print("  afplay output_play/purohitam_v3_t_iso_slow12x.wav")
    print()
    print("LISTEN FOR:")
    print("  [p] — Word-initial burst. Clean onset from silence.")
    print("        No pre-burst noise patch. No onset ramp.")
    print("        The burst emerges from the silence of closed lips.")
    print()
    print("  [t] — Between [i] and [ɑ]. The [i] fades (closing tail),")
    print("        the burst plucks, the [ɑ] rises (opening head).")
    print("        No concatenation boundaries.")
    print()
    print("  The architecture is correct. The stops are plucks.")
    print("=" * 70)
    print()
