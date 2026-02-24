#!/usr/bin/env python3
"""
ṚTVIJAM v9 — UNIFIED PLUCK ARCHITECTURE
Vedic Sanskrit: ṛtvijam [ɻ̩ʈviɟɑm]
Rigveda 1.1.1 — word 7
"priest" (accusative singular)

v8 → v9 CHANGES:

  1. [ʈ] — UNIFIED PLUCK ARCHITECTURE

     v8 used burst-only pluck (12ms). The closing tail on [ɻ̩]
     and opening head on [v] handled the transitions. This worked
     because all join boundaries were at near-zero amplitude.

     But PUROHITAM v4 proved that the unified source principle
     (from RATNADHATAMAM v16) composes with the pluck principle
     to produce a better result:

       PLUCK:          The stop is a boundary event.
                       The vowel owns the closure.
                       The following segment owns the VOT.

       UNIFIED SOURCE: The breath is continuous.
                       ONE noise buffer. ONE envelope.
                       No internal boundaries.

     v9 applies the same composition:
       [ɻ̩] + closing tail → [ʈ] unified source → head + [v]

     The unified source inside [ʈ] spans closure+burst+VOT as
     ONE continuous signal with subglottal floor, pre-burst
     crescendo, burst at retroflex locus, aspiration decay,
     and voicing fade-in. The F3 notch at 2200 Hz gives the
     retroflex coloring throughout.

  2. [ɟ] — VOICE BAR + BURST + CROSSFADE CUTBACK

     v8 used 4-phase (voice bar + burst + cutback). This is
     the correct architecture for voiced stops — they are
     "muted strings," not plucks. The glottal source is
     continuous through the closure.

     v9 updates to the b=[g] formant convention (canonical)
     and adds the cutback crossfade from the [dʰ] v14
     architecture (without the murmur phase — [ɟ] is
     alpaprāṇa, not mahāprāṇa).

  3. [m] — WORD-FINAL RELEASE (20ms fadeout)

  4. FORMANT FILTER: b=[g] convention throughout (canonical)

  5. CLOSING TAIL on [ɻ̩]: The [ɻ̩] extends with a 25ms
     closing tail that fades the retroflex resonance as the
     tongue moves toward the [ʈ] seal position. The closing
     tail is generated from the [ɻ̩]'s own resonance, not
     from a generic fade.

  6. OPENING HEAD on [v]: The [v] prepends a 15ms rising
     head modeling the vocal folds resuming vibration after
     the voiceless [ʈ] release.

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

# ── [ʈ] voiceless retroflex stop — v9 UNIFIED PLUCK ─────────────
VS_TT_CLOSURE_MS  = 15.0
VS_TT_BURST_MS    = 12.0
VS_TT_VOT_MS      = 15.0
VS_TT_BURST_F     = [500.0, 1300.0, 2200.0, 3100.0]
VS_TT_BURST_B     = [250.0,  350.0,  450.0,  500.0]
VS_TT_BURST_G     = [  8.0,   12.0,    3.0,    1.0]
VS_TT_BURST_DECAY = 150.0
VS_TT_BURST_GAIN  = 0.20
VS_TT_PREBURST_MS   = 4.0
VS_TT_PREBURST_AMP  = 0.006
VS_TT_SUBGLOTTAL_FLOOR = 0.001
VS_TT_F3_NOTCH    = 2200.0
VS_TT_F3_NOTCH_BW = 300.0
VS_TT_LOCUS_F     = [420.0, 1300.0, 2200.0, 3100.0]

# ── [v] voiced labio-dental approximant — VERIFIED DEVAM ────────
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

# ── [ɟ] voiced palatal stop — v9 VOICE BAR + CROSSFADE CUTBACK ──
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
    The vowel OWNS the closure.
    The last tail_ms fades as the articulator seals.
    Tiles the last pitch period with squared fade.
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
    The following segment OWNS the VOT.
    The first head_ms rises from near-zero.
    Tiles the first pitch period with squared rise.
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
# ============================================================================

def _synth_unified_voiceless_stop(
    closure_ms, burst_ms, vot_ms,
    burst_f, burst_b, burst_g, burst_decay, burst_gain,
    preburst_ms, preburst_amp, subglottal_floor,
    vot_locus_f, F_next,
    vot_vowel_b, vot_vowel_gains,
    f3_notch=None, f3_notch_bw=None,
    pitch_hz=PITCH_HZ, dil=DIL,
):
    """
    Unified source architecture for voiceless stops.
    ONE continuous noise buffer. ONE continuous envelope.
    Spike rides on the noise. No boundaries.

    Optional F3 notch for retroflex (mūrdhanya) class.
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

    # Phase C: Burst peak
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

    # Phase D: Aspiration decay
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

    # Apply F3 notch if retroflex
    if f3_notch is not None:
        noise_shaped = iir_notch(noise_shaped, f3_notch,
                                 f3_notch_bw if f3_notch_bw else 300.0)

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
        if f3_notch is not None:
            vot_filt = iir_notch(vot_filt, f3_notch,
                                 f3_notch_bw if f3_notch_bw else 300.0)
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

def synth_RV(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=DIL,
             closing_for_stop=False):
    """
    [ɻ̩] syllabic retroflex approximant (VERIFIED ṚG)

    closing_for_stop=True: append 25ms closing tail.
    The [ɻ̩] closes ITSELF toward the [ʈ] seal position.
    """
    n = int(VS_RV_DUR_MS * dil / 1000.0 * SR)
    src = rosenberg_pulse(n, pitch_hz)

    f_mean = list(VS_RV_F)
    if F_prev is not None:
        for k in range(min(len(F_prev), len(VS_RV_F))):
            f_mean[k] = (F_prev[k] * VS_RV_COART_ON +
                         VS_RV_F[k] * (1.0 - VS_RV_COART_ON))
    if F_next is not None:
        for k in range(min(len(F_next), len(VS_RV_F))):
            f_mean[k] = (f_mean[k] * (1.0 - VS_RV_COART_OFF) +
                         F_next[k] * VS_RV_COART_OFF)

    out = apply_formants(src, f_mean, VS_RV_B, VS_RV_GAINS)
    out = iir_notch(out, VS_RV_F3_NOTCH, VS_RV_F3_NOTCH_BW)

    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.72

    if closing_for_stop:
        out = make_closing_tail(f32(out), CLOSING_TAIL_MS)

    return f32(out)


def synth_TT(F_next=None, pitch_hz=PITCH_HZ, dil=DIL):
    """
    [ʈ] voiceless retroflex stop — v9 UNIFIED PLUCK

    Unified source architecture with retroflex F3 notch.
    ONE noise buffer spanning closure+burst+VOT.
    ONE continuous envelope. Spike rides on noise.
    F3 notch at 2200 Hz throughout (mūrdhanya marker).

    The breath is continuous.
    The tongue is the envelope.
    The F3 notch is the sublingual cavity.
    """
    return _synth_unified_voiceless_stop(
        closure_ms=VS_TT_CLOSURE_MS,
        burst_ms=VS_TT_BURST_MS,
        vot_ms=VS_TT_VOT_MS,
        burst_f=VS_TT_BURST_F,
        burst_b=VS_TT_BURST_B,
        burst_g=VS_TT_BURST_G,
        burst_decay=VS_TT_BURST_DECAY,
        burst_gain=VS_TT_BURST_GAIN,
        preburst_ms=VS_TT_PREBURST_MS,
        preburst_amp=VS_TT_PREBURST_AMP,
        subglottal_floor=VS_TT_SUBGLOTTAL_FLOOR,
        vot_locus_f=VS_TT_LOCUS_F,
        F_next=F_next if F_next is not None else VS_V_F,
        vot_vowel_b=VS_V_B,
        vot_vowel_gains=VS_V_GAINS,
        f3_notch=VS_TT_F3_NOTCH,
        f3_notch_bw=VS_TT_F3_NOTCH_BW,
        pitch_hz=pitch_hz,
        dil=dil,
    )


def synth_V(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=DIL,
            opening_from_stop=False):
    """
    [v] voiced labio-dental approximant (VERIFIED DEVAM)

    opening_from_stop=True: prepend 15ms opening head.
    The [v] opens ITSELF from the [ʈ] release.
    """
    n = int(VS_V_DUR_MS * dil / 1000.0 * SR)
    src = rosenberg_pulse(n, pitch_hz)

    f_mean = list(VS_V_F)
    if F_prev is not None:
        for k in range(min(len(F_prev), len(VS_V_F))):
            f_mean[k] = (F_prev[k] * VS_V_COART_ON +
                         VS_V_F[k] * (1.0 - VS_V_COART_ON))
    if F_next is not None:
        for k in range(min(len(F_next), len(VS_V_F))):
            f_mean[k] = (f_mean[k] * (1.0 - VS_V_COART_OFF) +
                         F_next[k] * VS_V_COART_OFF)

    out = apply_formants(src, f_mean, VS_V_B, VS_V_GAINS)

    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.68

    if opening_from_stop:
        out = make_opening_head(f32(out), OPENING_HEAD_MS)

    return f32(out)


def synth_I(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=DIL):
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
    return f32(out)


def synth_JJ(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=DIL):
    """
    [ɟ] voiced palatal stop — v9 VOICE BAR + CROSSFADE CUTBACK

    Śikṣā: tālavya row 3 — alpaprāṇa ghana
    Voiced, unaspirated, palatal.

    Same architecture as [dʰ] v14 but WITHOUT murmur
    (alpaprāṇa — no extended breathy phase).

    Phase 1: Voice bar closure (250 Hz, BW 80)
    Phase 2: Spike + turbulence burst at palatal locus
    Phase 3: Crossfade cutback (closed → open)

    Voiced stops are NOT plucks — they are muted strings.
    The glottal source is continuous through the closure.
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
        fade_in  = np.sin(t_fade).astype(DTYPE)
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
    return f32(out)


def synth_M(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=DIL,
            word_final=False):
    """
    [m] bilabial nasal (VERIFIED PUROHITAM)
    word_final=True adds 20ms release tail.
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
    if F_next is not None:
        for k in range(min(len(F_next), len(VS_M_F))):
            f_mean[k] = (f_mean[k] * (1.0 - VS_M_COART_OFF) +
                         F_next[k] * VS_M_COART_OFF)

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
    ṚTVIJAM [ɻ̩ʈviɟɑm] — v9 UNIFIED PLUCK
    Rigveda 1.1.1, word 7
    Syllables: ṚṬ-VI-JAM

    v9 UNIFIED PLUCK ARCHITECTURE for [ʈ]:

      Two principles composed:
        PLUCK: [ɻ̩] owns the closure (closing tail).
               [v] owns the VOT (opening head).
               [ʈ] is the boundary event.
        UNIFIED SOURCE: Inside [ʈ], ONE noise buffer,
               ONE envelope, subglottal floor, F3 notch.
               The breath is continuous.

      Segment map:
        [rv] + closing tail       60ms + 25ms = 85ms
        [tt] UNIFIED              42ms (15cl + 12burst + 15vot)
        head + [v]                15ms + 60ms = 75ms
        [i]                       50ms
        [jj]                      54ms (closure + burst + cutback)
        [a]                       55ms
        [m] + release             60ms + 20ms = 80ms

    [ɟ] uses voice bar + crossfade cutback (voiced stops
    are muted strings, not plucks).
    """
    segs = [
        # ṚṬ- (closing tail: [ɻ̩] owns the closure)
        synth_RV(F_prev=None, F_next=VS_TT_LOCUS_F,
                 pitch_hz=pitch_hz, dil=dil,
                 closing_for_stop=True),

        # [ʈ] UNIFIED PLUCK
        synth_TT(F_next=VS_V_F,
                 pitch_hz=pitch_hz, dil=dil),

        # -V (opening head: [v] owns the VOT)
        synth_V(F_prev=VS_TT_LOCUS_F, F_next=VS_I_F,
                pitch_hz=pitch_hz, dil=dil,
                opening_from_stop=True),

        # -I-
        synth_I(F_prev=VS_V_F, F_next=VS_JJ_F,
                pitch_hz=pitch_hz, dil=dil),

        # -J (voiced — muted string, not pluck)
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
    print("ṚTVIJAM v9 — UNIFIED PLUCK ARCHITECTURE")
    print("=" * 70)
    print()
    print("v8→v9 CHANGES:")
    print()
    print("  [ʈ] — UNIFIED PLUCK (from PUROHITAM v4 / RATNADHATAMAM v16):")
    print("    TWO principles composed:")
    print("      PLUCK: [ɻ̩] owns closure, [v] owns VOT, [ʈ] is the pluck")
    print("      UNIFIED SOURCE: ONE noise buffer, ONE envelope")
    print("    Subglottal floor: 0.001 (~-60dB)")
    print("    Pre-burst crescendo: 4ms, 0.006 peak")
    print("    F3 notch at 2200 Hz throughout (mūrdhanya marker)")
    print("    Closure 15ms + burst 12ms + VOT 15ms = 42ms unified")
    print()
    print("  [ɟ] — VOICE BAR + CROSSFADE CUTBACK (canonical):")
    print("    Voiced stops are muted strings, not plucks")
    print("    Voice bar (250 Hz) + burst + closed→open crossfade")
    print("    b=[g] formant convention")
    print()
    print("  [m] — WORD-FINAL RELEASE (20ms fadeout)")
    print()
    print("  FORMANTS: b=[g] convention throughout")
    print()
    print("  Segment map:")
    print("    [ɻ̩] + closing tail   85ms  (60ms + 25ms fade)")
    print("    [ʈ] UNIFIED          42ms  (15cl + 12burst + 15vot)")
    print("    head + [v]           75ms  (15ms rise + 60ms)")
    print("    [i]                  50ms")
    print("    [ɟ]                  54ms  (30cl + 9burst + 15cutback)")
    print("    [ɑ]                  55ms")
    print("    [m] + release        80ms  (60ms + 20ms fade)")
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

    write_wav("output_play/rtvijam_v9_dry.wav", word_dry)
    write_wav("output_play/rtvijam_v9_slow6x.wav", word_slow)
    write_wav("output_play/rtvijam_v9_slow12x.wav", word_slow12)
    write_wav("output_play/rtvijam_v9_hall.wav", word_hall)
    write_wav("output_play/rtvijam_v9_perf.wav", word_perf)
    write_wav("output_play/rtvijam_v9_perf_hall.wav", word_perf_hall)

    # Isolated phonemes
    tt_iso = synth_TT(F_next=VS_V_F)
    jj_iso = synth_JJ(F_prev=VS_I_F, F_next=VS_A_F)

    for sig, name in [
        (tt_iso, "rtvijam_v9_tt_unified"),
        (jj_iso, "rtvijam_v9_jj_iso"),
    ]:
        mx = np.max(np.abs(sig))
        if mx > 1e-8:
            sig = sig / mx * 0.75
        write_wav(f"output_play/{name}.wav", sig)
        write_wav(f"output_play/{name}_slow6x.wav",
                  ola_stretch(sig, 6.0))
        write_wav(f"output_play/{name}_slow12x.wav",
                  ola_stretch(sig, 12.0))

    # ṚṬ syllable (for join testing)
    rt_syl = np.concatenate([
        synth_RV(F_next=VS_TT_LOCUS_F, closing_for_stop=True),
        synth_TT(F_next=VS_V_F)
    ])
    mx = np.max(np.abs(rt_syl))
    if mx > 1e-8:
        rt_syl = rt_syl / mx * 0.75
    rt_syl = f32(rt_syl)
    write_wav("output_play/rtvijam_v9_RT_syllable.wav", rt_syl)
    write_wav("output_play/rtvijam_v9_RT_syllable_slow6x.wav",
              ola_stretch(rt_syl, 6.0))
    write_wav("output_play/rtvijam_v9_RT_syllable_slow12x.wav",
              ola_stretch(rt_syl, 12.0))

    print()
    print("=" * 70)
    print("v9 synthesis complete.")
    print()
    print("LISTEN:")
    print("  afplay output_play/rtvijam_v9_tt_unified_slow12x.wav")
    print("  afplay output_play/rtvijam_v9_RT_syllable_slow12x.wav")
    print("  afplay output_play/rtvijam_v9_jj_iso_slow12x.wav")
    print("  afplay output_play/rtvijam_v9_slow6x.wav")
    print("  afplay output_play/rtvijam_v9_perf_hall.wav")
    print()
    print("LISTEN FOR:")
    print("  [ʈ] — Should be softer than v8 burst-only.")
    print("        The burst emerges from continuous noise floor.")
    print("        F3 notch gives retroflex 'darkness'.")
    print("        Compare v9 to v8 at 12x slow.")
    print()
    print("  [ɟ] — Voice bar provides continuous signal.")
    print("        Crossfade cutback transitions to [ɑ].")
    print("        No click at any join.")
    print()
    print("  The architecture is canonical.")
    print("  All three words now use unified pluck for voiceless stops.")
    print("=" * 70)
    print()
