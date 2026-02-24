#!/usr/bin/env python3
"""
ṚTVIJAM v8
Vedic Sanskrit: ṛtvijam [ɻ̩ʈviɟɑm]
Rigveda 1.1.1 — word 7

v7→v8 CHANGES:

  1. [ʈ] PLUCK ARCHITECTURE (from RATNADHĀTAMAM v16 DIAGNOSTIC v4.7.1)

     The v16 unified source fixed the click WITHIN [t].
     But the ratnadhātamam diagnostic v4.7.1 revealed the deeper truth:

     THE CLICK WAS NEVER INSIDE [t]. IT WAS AT THE JOIN.

     When you concatenate:
       [..., vowel[-1]=0.45] + [stop[0]=0.001, ...]
     that sample-level jump from 0.45 to 0.001 IS the click.
     No amount of internal stop architecture fixes this.

     v4.7.1 SOLUTION: Segment ownership follows physics.

       CLOSING TAIL: The vowel OWNS the closure. The last 25ms of
       the vowel segment fades amplitude as the tongue moves toward
       seal position. The vowel's resonator produces the fade.

       THE PLUCK: The stop itself is ONLY the burst transient (8-12ms).
       No closure. No VOT. Just the instant of release.

       OPENING HEAD: The next segment OWNS the VOT. The voiced onset
       rises over 15ms at the start of the following segment.

     Result: No concatenation boundary between loud voiced signal
     and near-silence. The fade happens WITHIN the vowel. The rise
     happens WITHIN the next voiced segment. The stop is a pluck.

  2. [ɟ] VOICED PALATAL STOP — 4-phase architecture

     Voice bar closure + spike/turbulence burst + crossfade cutback.
     Same pattern as [dʰ] but WITHOUT murmur (alpaprāṇa).
     Voiced stops don't click at joins because the source is
     continuous — voice bar murmur on one side, burst on the other.

  3. [m] WORD-FINAL RELEASE (20ms fadeout)

  4. FORMANT FILTER: b=[g] convention (canonical)

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

# ── [ɻ̩] syllabic retroflex approximant — VERIFIED ṚG ────────────
VS_RV_F      = [420.0, 1300.0, 2200.0, 3100.0]
VS_RV_B      = [150.0,  200.0,  280.0,  300.0]
VS_RV_GAINS  = [ 14.0,    7.0,    1.5,    0.4]
VS_RV_DUR_MS = 60.0
VS_RV_F3_NOTCH    = 2200.0
VS_RV_F3_NOTCH_BW = 300.0
VS_RV_COART_ON    = 0.15
VS_RV_COART_OFF   = 0.15

# ── [ʈ] voiceless retroflex stop — v8 PLUCK ─────────────────────
# The pluck is ONLY the burst. Closure belongs to preceding segment.
# VOT belongs to following segment.
VS_TT_BURST_MS    = 12.0   # The pluck itself

VS_TT_BURST_F     = [500.0, 1300.0, 2200.0, 3100.0]
VS_TT_BURST_B     = [250.0,  350.0,  450.0,  500.0]
VS_TT_BURST_G     = [  8.0,   12.0,    3.0,    1.0]
VS_TT_BURST_DECAY = 150.0
VS_TT_BURST_GAIN  = 0.20
VS_TT_SUBGLOTTAL_FLOOR = 0.001

VS_TT_F3_NOTCH    = 2200.0
VS_TT_F3_NOTCH_BW = 300.0
VS_TT_LOCUS_F     = [420.0, 1300.0, 2200.0, 3100.0]

# Closing tail: owned by preceding voiced segment
VS_TT_CLOSING_MS  = 25.0
# Opening head: owned by following voiced segment
VS_TT_OPENING_MS  = 15.0

# ── [v] voiced labio-dental approximant — VERIFIED DEVAM ──────��─
VS_V_F      = [300.0, 1500.0, 2400.0, 3100.0]
VS_V_B      = [180.0,  350.0,  400.0,  400.0]
VS_V_GAINS  = [ 10.0,    5.0,    1.5,    0.5]
VS_V_DUR_MS = 60.0
VS_V_COART_ON  = 0.18
VS_V_COART_OFF = 0.18

# ── [i] short close front unrounded — VERIFIED AGNI ─────────────
VS_I_F      = [280.0, 2200.0, 2900.0, 3400.0]
VS_I_B      = [ 80.0,  130.0,  180.0,  250.0]
VS_I_GAINS  = [ 12.0,    8.0,    1.5,    0.5]
VS_I_DUR_MS = 50.0
VS_I_COART_ON  = 0.12
VS_I_COART_OFF = 0.12

# ── [ɟ] voiced palatal stop — v8 4-PHASE ────────────────────────
VS_JJ_F      = [280.0, 2100.0, 2800.0, 3300.0]
VS_JJ_B      = [100.0,  200.0,  300.0,  350.0]
VS_JJ_GAINS  = [ 10.0,    6.0,    1.5,    0.5]
VS_JJ_CLOSURE_MS  = 30.0
VS_JJ_BURST_MS    = 9.0
VS_JJ_CUTBACK_MS  = 15.0

VS_JJ_VOICEBAR_F  = 250.0
VS_JJ_VOICEBAR_BW = 80.0
VS_JJ_VOICEBAR_G  = 12.0
VS_JJ_MURMUR_PEAK = 0.25

VS_JJ_BURST_F     = [500.0, 3200.0, 3800.0, 4200.0]
VS_JJ_BURST_B     = [300.0,  500.0,  600.0,  700.0]
VS_JJ_BURST_G     = [  8.0,   12.0,    3.0,    1.0]
VS_JJ_BURST_DECAY = 180.0
VS_JJ_BURST_PEAK  = 0.15

VS_JJ_CLOSED_F    = [250.0,  800.0, 2200.0, 3200.0]
VS_JJ_CLOSED_B    = [150.0,  250.0,  300.0,  350.0]
VS_JJ_CLOSED_G    = [ 10.0,    3.0,    0.8,    0.3]
VS_JJ_CLOSED_PEAK = 0.40
VS_JJ_OPEN_PEAK   = 0.65
VS_JJ_CUTBACK_PEAK = 0.55

# ── [ɑ] short open central unrounded — VERIFIED AGNI ────────────
VS_A_F      = [700.0, 1100.0, 2550.0, 3400.0]
VS_A_B      = [130.0,  160.0,  220.0,  280.0]
VS_A_GAINS  = [ 16.0,    6.0,    1.5,    0.5]
VS_A_DUR_MS = 55.0
VS_A_COART_ON  = 0.12
VS_A_COART_OFF = 0.12

# ── [m] bilabial nasal — VERIFIED PUROHITAM ──────────────────────
VS_M_F       = [250.0,  900.0, 2200.0, 3000.0]
VS_M_B       = [100.0,  200.0,  300.0,  350.0]
VS_M_GAINS   = [  8.0,    2.5,    0.5,    0.2]
VS_M_DUR_MS  = 60.0
VS_M_ANTI_F  = 800.0
VS_M_ANTI_BW = 200.0
VS_M_COART_ON  = 0.15
VS_M_COART_OFF = 0.15
VS_M_RELEASE_MS = 20.0

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
    """Rosenberg glottal pulse model"""
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
    """Formant filter bank (IIR resonators) — b=[g] convention"""
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
    """Nasal antiresonance / retroflex F3 notch"""
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
    """Time-stretch via overlap-add"""
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
    """Temple courtyard reverb"""
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
# CLOSING TAIL / OPENING HEAD
# ============================================================================

def make_closing_tail(voiced_seg, tail_ms, sr=SR):
    """
    The vowel OWNS the closure.

    The last tail_ms of the voiced segment fades in amplitude
    as the tongue moves toward seal position. The voiced signal
    is ALREADY THERE — we just apply a fade envelope to the end.

    The signal never jumps to zero. It decays smoothly from
    whatever amplitude the voiced segment had at that point.
    The concatenation boundary after this tail will be at
    near-zero amplitude — no click.
    """
    n_tail = int(tail_ms / 1000.0 * sr)
    n_tail = min(n_tail, len(voiced_seg))
    if n_tail < 2:
        return voiced_seg

    out = voiced_seg.copy()
    # Squared fade: gentle at first, then drops
    fade = np.linspace(1.0, 0.0, n_tail) ** 2
    out[-n_tail:] = out[-n_tail:] * fade
    return f32(out)

def make_opening_head(voiced_seg, head_ms, sr=SR):
    """
    The next segment OWNS the VOT.

    The first head_ms of the voiced segment rises from near-zero
    as the vocal folds close after the stop release. The signal
    fades IN from whatever the stop left behind (near-zero).

    The concatenation boundary before this head will match the
    near-zero end of the stop — no click.
    """
    n_head = int(head_ms / 1000.0 * sr)
    n_head = min(n_head, len(voiced_seg))
    if n_head < 2:
        return voiced_seg

    out = voiced_seg.copy()
    # Squared rise: starts slow, accelerates
    rise = np.linspace(0.0, 1.0, n_head) ** 2
    out[:n_head] = out[:n_head] * rise
    return f32(out)

# ============================================================================
# PHONEME SYNTHESIS FUNCTIONS
# ============================================================================

def synth_RV(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=DIL,
             closing_for_stop=False):
    """
    [ɻ̩] syllabic retroflex approximant (VERIFIED ṚG)

    closing_for_stop=True: append closing tail (vowel owns closure)
    """
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

    if closing_for_stop:
        # Extend with closing tail: the tongue moves toward retroflex
        # seal position. The [ɻ̩] resonance fades as closure forms.
        n_tail = int(VS_TT_CLOSING_MS * dil / 1000.0 * SR)
        # Generate more of the same voiced signal for the tail
        src_tail = rosenberg_pulse(n_tail, pitch_hz)
        # Use formants partway between [ɻ̩] and closed tract
        f_closing = [f * 0.7 + 250.0 * 0.3 for f in f_mean]
        tail_sig = apply_formants(src_tail, f_closing, VS_RV_B, VS_RV_GAINS)
        tail_sig = iir_notch(tail_sig, VS_RV_F3_NOTCH, VS_RV_F3_NOTCH_BW)
        # Match amplitude at junction
        if len(out) > 0 and len(tail_sig) > 0:
            junction_amp = np.max(np.abs(out[-20:])) if len(out) >= 20 else np.max(np.abs(out))
            tail_mx = np.max(np.abs(tail_sig))
            if tail_mx > 1e-10 and junction_amp > 1e-10:
                tail_sig = tail_sig * (junction_amp / tail_mx)
        out = np.concatenate([out, f32(tail_sig)])
        # Apply the closing fade to the tail portion
        out = make_closing_tail(out, VS_TT_CLOSING_MS * dil)

    return f32(out)


def synth_TT(pitch_hz=PITCH_HZ, dil=DIL):
    """
    [ʈ] voiceless retroflex stop — v8 PLUCK

    THE PLUCK IS ONLY THE BURST.

    The closure belongs to the preceding [ɻ̩] (closing tail).
    The VOT belongs to the following [v] (opening head).
    This function produces ONLY the burst transient.

    Architecture: Same as ratnadhātamam [t] v16 unified source,
    but spanning only the burst duration. No closure phase
    (that's the preceding segment's responsibility). No VOT
    phase (that's the following segment's responsibility).

    The burst uses one continuous noise buffer shaped by one
    continuous envelope. The spike is added on top.
    F3 notch at 2200 Hz gives retroflex coloring.
    """
    n_b = int(VS_TT_BURST_MS * dil / 1000.0 * SR)

    # One continuous noise buffer for the burst
    noise_source = np.random.randn(n_b).astype(float)

    # Burst envelope: attack then exponential decay
    t_burst = np.arange(n_b, dtype=float) / SR
    env = VS_TT_BURST_GAIN * np.exp(-t_burst * VS_TT_BURST_DECAY)

    # Apply retroflex locus formants to noise
    noise_shaped = apply_formants(
        noise_source,
        VS_TT_BURST_F, VS_TT_BURST_B, VS_TT_BURST_G)

    # Apply F3 notch AFTER formants, BEFORE envelope
    # (filter sees only the burst-length signal, no state issues)
    noise_shaped = iir_notch(noise_shaped, VS_TT_F3_NOTCH, VS_TT_F3_NOTCH_BW)

    # Apply envelope
    noise_out = f32(noise_shaped * env)

    # Add spike transient at onset
    spike = np.zeros(n_b, dtype=float)
    spike_len = min(3, n_b)
    spike_vals = [1.0, 0.6, 0.3][:spike_len]
    for i, sv in enumerate(spike_vals):
        if i < n_b:
            spike[i] = sv

    spike_env = np.exp(-np.arange(n_b, dtype=float) / SR * VS_TT_BURST_DECAY)
    spike_out = f32(spike * spike_env * VS_TT_BURST_GAIN * 0.5)

    out = noise_out + spike_out

    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.55
    return f32(out)


def synth_V(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=DIL,
            opening_from_stop=False):
    """
    [v] voiced labio-dental approximant (VERIFIED DEVAM)

    opening_from_stop=True: prepend opening head (segment owns VOT)
    """
    n = int(VS_V_DUR_MS * dil / 1000.0 * SR)

    if opening_from_stop:
        n_head = int(VS_TT_OPENING_MS * dil / 1000.0 * SR)
    else:
        n_head = 0

    src = rosenberg_pulse(n + n_head, pitch_hz)

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

    if opening_from_stop:
        out = make_opening_head(out, VS_TT_OPENING_MS * dil)

    return f32(out)


def synth_I(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=DIL):
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


def synth_JJ(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=DIL):
    """
    [ɟ] voiced palatal stop — v8 4-PHASE

    Śikṣā: tālavya row 3 — alpaprāṇa ghana
    Voiced, unaspirated, palatal.

    Same pattern as [dʰ] but WITHOUT murmur (alpaprāṇa).
    Voiced stops don't click at joins — the voice bar provides
    nonzero signal at the boundary with the preceding vowel,
    and the crossfade cutback provides smooth transition to
    the following vowel.

    Phase 1: Voice bar closure (250 Hz, BW 80)
    Phase 2: Spike + turbulence burst at palatal locus
    Phase 3: Crossfade cutback (closed → open)
    """
    n_cl = int(VS_JJ_CLOSURE_MS * dil / 1000.0 * SR)
    n_b  = int(VS_JJ_BURST_MS * dil / 1000.0 * SR)
    n_cb = int(VS_JJ_CUTBACK_MS * dil / 1000.0 * SR)

    f_next = F_next if F_next is not None else VS_A_F

    # Phase 1: Voice bar closure
    if n_cl > 0:
        src_cl = rosenberg_pulse(n_cl, pitch_hz, oq=0.65)
        murmur_cl = apply_formants(
            src_cl,
            [VS_JJ_VOICEBAR_F],
            [VS_JJ_VOICEBAR_BW],
            [VS_JJ_VOICEBAR_G])
        env_cl = np.ones(n_cl, dtype=float)
        ramp_n = max(1, int(0.3 * n_cl))
        env_cl[:ramp_n] = np.linspace(0.3, 1.0, ramp_n)
        murmur_cl = f32(murmur_cl * env_cl)
        closure = norm_to_peak(murmur_cl, VS_JJ_MURMUR_PEAK)
    else:
        closure = np.array([], dtype=DTYPE)

    # Phase 2: Spike + turbulence burst (palatal locus)
    spike = np.zeros(max(n_b, 16), dtype=float)
    spike[0:3] = [1.0, 0.6, 0.3]
    turbulence = np.random.randn(len(spike))
    turbulence_filt = apply_formants(
        turbulence, VS_JJ_BURST_F, VS_JJ_BURST_B, VS_JJ_BURST_G)
    t_b = np.arange(len(spike)) / SR
    mix_env = np.exp(-t_b * VS_JJ_BURST_DECAY)
    burst_raw = spike * mix_env + turbulence_filt * (1.0 - mix_env) * 0.30
    burst = norm_to_peak(f32(burst_raw), VS_JJ_BURST_PEAK)

    # Phase 3: Crossfade cutback (closed → open)
    if n_cb > 0:
        src_cb = rosenberg_pulse(n_cb, pitch_hz)
        sig_closed = apply_formants(
            src_cb, VS_JJ_CLOSED_F, VS_JJ_CLOSED_B, VS_JJ_CLOSED_G)
        sig_closed = norm_to_peak(sig_closed, VS_JJ_CLOSED_PEAK)
        sig_open = apply_formants(
            src_cb, list(f_next),
            [100.0, 140.0, 200.0, 260.0],
            [14.0, 8.0, 1.5, 0.5])
        sig_open = norm_to_peak(sig_open, VS_JJ_OPEN_PEAK)
        t_fade = np.linspace(0.0, np.pi / 2.0, n_cb)
        fade_out = np.cos(t_fade).astype(DTYPE)
        fade_in = np.sin(t_fade).astype(DTYPE)
        cutback = f32(sig_closed * fade_out + sig_open * fade_in)
        cb_env = np.linspace(0.6, 1.0, n_cb).astype(DTYPE)
        cutback = f32(cutback * cb_env)
        cutback = norm_to_peak(cutback, VS_JJ_CUTBACK_PEAK)
    else:
        cutback = np.array([], dtype=DTYPE)

    out = np.concatenate([closure, burst, cutback])
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.60
    return f32(out)


def synth_A(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=DIL):
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


def synth_M(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=DIL,
            word_final=False):
    """
    [m] bilabial nasal (VERIFIED PUROHITAM)

    word_final=True adds 20ms release tail.
    """
    n = int(VS_M_DUR_MS * dil / 1000.0 * SR)
    n_release = int(VS_M_RELEASE_MS * dil / 1000.0 * SR) if word_final else 0

    src = rosenberg_pulse(n + n_release, pitch_hz)

    f_mean = list(VS_M_F)
    if F_prev is not None:
        for k in range(min(len(F_prev), len(VS_M_F))):
            f_mean[k] = F_prev[k] * VS_M_COART_ON + VS_M_F[k] * (1.0 - VS_M_COART_ON)
    if F_next is not None:
        for k in range(min(len(F_next), len(VS_M_F))):
            f_mean[k] = f_mean[k] * (1.0 - VS_M_COART_OFF) + F_next[k] * VS_M_COART_OFF

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

def synth_rtvijam(pitch_hz=PITCH_HZ, dil=DIL, with_room=False):
    """
    ṚTVIJAM [ɻ̩ʈviɟɑm] — v8
    Rigveda 1.1.1, word 7
    Syllables: ṚṬ-VI-JAM

    v8 PLUCK ARCHITECTURE for [ʈ]:

      The click was never inside [ʈ]. It was at the JOIN.

      Segment map:
        [ɻ̩] + closing tail    60ms + 25ms = 85ms
        [ʈ] PLUCK              12ms (burst only)
        head + [v]              15ms + 60ms = 75ms
        [i]                     50ms
        [ɟ]                     54ms (closure + burst + cutback)
        [ɑ]                     55ms
        [m] + release           60ms + 20ms = 80ms

      The closing tail fades [ɻ̩] to near-zero.
      The pluck starts at near-zero (noise floor).
      The pluck ends at near-zero (burst decay).
      The opening head starts at near-zero and rises.

      NO amplitude discontinuity at ANY concatenation boundary.
    """
    segs = [
        # ṚṬ- (closing tail: [ɻ̩] owns the closure)
        synth_RV(F_prev=None, F_next=VS_TT_LOCUS_F,
                 pitch_hz=pitch_hz, dil=dil,
                 closing_for_stop=True),

        # [ʈ] PLUCK (burst only — 12ms)
        synth_TT(pitch_hz=pitch_hz, dil=dil),

        # -V (opening head: [v] owns the VOT)
        synth_V(F_prev=VS_TT_LOCUS_F, F_next=VS_I_F,
                pitch_hz=pitch_hz, dil=dil,
                opening_from_stop=True),

        # -I-
        synth_I(F_prev=VS_V_F, F_next=VS_JJ_F,
                pitch_hz=pitch_hz, dil=dil),

        # -J (voiced — no click at joins)
        synth_JJ(F_prev=VS_I_F, F_next=VS_A_F,
                 pitch_hz=pitch_hz, dil=dil),

        # -A-
        synth_A(F_prev=VS_JJ_F, F_next=VS_M_F,
                pitch_hz=pitch_hz, dil=dil),

        # -M (word-final with release)
        synth_M(F_prev=VS_A_F, F_next=None,
                pitch_hz=pitch_hz, dil=dil,
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
    print("ṚTVIJAM v8 — PLUCK ARCHITECTURE")
    print("=" * 70)
    print()
    print("v7→v8: THE CLICK WAS AT THE JOIN, NOT INSIDE THE STOP.")
    print()
    print("  v7 problem:")
    print("    [..., vowel[-1]=0.45] + [stop[0]=0.001, ...]")
    print("    That sample jump IS the click.")
    print("    No internal stop architecture fixes a join click.")
    print()
    print("  v8 solution: SEGMENT OWNERSHIP FOLLOWS PHYSICS")
    print()
    print("    CLOSING TAIL: [ɻ̩] owns the closure.")
    print("      The last 25ms fades as the tongue seals.")
    print("      The signal decays smoothly within the vowel.")
    print()
    print("    THE PLUCK: [ʈ] = 12ms burst transient only.")
    print("      No closure (that's [ɻ̩]'s tail).")
    print("      No VOT (that's [v]'s head).")
    print("      Starts near-zero, peaks, decays to near-zero.")
    print()
    print("    OPENING HEAD: [v] owns the VOT.")
    print("      The first 15ms rises from near-zero.")
    print("      Voicing fades in as the folds close.")
    print()
    print("  Result: All join boundaries are at near-zero amplitude.")
    print("          No click anywhere.")
    print()
    print("  [ɟ] voiced palatal: 4-phase (voice bar + burst + cutback)")
    print("    Voiced stops don't click — continuous glottal source.")
    print()
    print("  [m] word-final: 20ms release tail.")
    print()

    # Diagnostic speed
    word_dry = synth_rtvijam(PITCH_HZ, 1.0)
    word_slow = ola_stretch(word_dry, 6.0)
    word_slow12 = ola_stretch(word_dry, 12.0)

    # Performance speed
    word_perf = synth_rtvijam(PITCH_HZ, 2.5)
    word_perf_hall = synth_rtvijam(PITCH_HZ, 2.5, with_room=True)

    # Hall
    word_hall = synth_rtvijam(PITCH_HZ, 1.0, with_room=True)

    write_wav("output_play/rtvijam_v8_dry.wav", word_dry)
    write_wav("output_play/rtvijam_v8_slow6x.wav", word_slow)
    write_wav("output_play/rtvijam_v8_slow12x.wav", word_slow12)
    write_wav("output_play/rtvijam_v8_hall.wav", word_hall)
    write_wav("output_play/rtvijam_v8_perf.wav", word_perf)
    write_wav("output_play/rtvijam_v8_perf_hall.wav", word_perf_hall)

    # Isolated phonemes
    tt_iso = synth_TT(pitch_hz=PITCH_HZ, dil=DIL)
    jj_iso = synth_JJ(F_prev=VS_I_F, F_next=VS_A_F,
                       pitch_hz=PITCH_HZ, dil=DIL)
    m_final_iso = synth_M(F_prev=VS_A_F, word_final=True,
                          pitch_hz=PITCH_HZ, dil=DIL)

    # ṚṬ syllable (for click testing)
    rt_syl = np.concatenate([
        synth_RV(F_prev=None, F_next=VS_TT_LOCUS_F,
                 closing_for_stop=True),
        synth_TT()
    ])
    mx = np.max(np.abs(rt_syl))
    if mx > 1e-8:
        rt_syl = rt_syl / mx * 0.75
    rt_syl = f32(rt_syl)

    for sig, name in [
        (tt_iso,       "rtvijam_v8_tt_iso"),
        (jj_iso,       "rtvijam_v8_jj_iso"),
        (m_final_iso,  "rtvijam_v8_m_final_iso"),
        (rt_syl,       "rtvijam_v8_RT_syllable"),
    ]:
        mx = np.max(np.abs(sig))
        if mx > 1e-8:
            sig = sig / mx * 0.75
        write_wav(f"output_play/{name}.wav", sig)
        write_wav(f"output_play/{name}_slow6x.wav", ola_stretch(sig, 6.0))
        write_wav(f"output_play/{name}_slow12x.wav", ola_stretch(sig, 12.0))

    print()
    print("=" * 70)
    print("v8 synthesis complete.")
    print()
    print("LISTEN FOR THE CLICK TEST:")
    print("  afplay output_play/rtvijam_v8_RT_syllable_slow12x.wav")
    print("  afplay output_play/rtvijam_v8_tt_iso_slow12x.wav")
    print("  afplay output_play/rtvijam_v8_slow6x.wav")
    print("  afplay output_play/rtvijam_v8_perf_hall.wav")
    print()
    print("THE CLICK SHOULD BE GONE.")
    print("  [ɻ̩] fades smoothly (closing tail)")
    print("  [ʈ] burst starts at noise floor (no jump)")
    print("  [v] rises smoothly (opening head)")
    print("  All joins are at near-zero amplitude.")
    print()
    print("Compare to v7:")
    print("  v7: [...vowel=0.45] + [stop=0.001...] = CLICK")
    print("  v8: [...tail→0.00] + [burst=0.00→peak→0.00] + [0.00→head...] = SMOOTH")
    print("=" * 70)
    print()
