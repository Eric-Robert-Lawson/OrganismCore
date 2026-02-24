#!/usr/bin/env python3
"""
RATNADHĀTAMAM v17
Vedic Sanskrit: ratnadhātamam [rɑtnɑdʰaːtɑmɑm]
Rigveda 1.1.1 — word 9
"having jewels as best wealth"

v16→v17 CHANGES:

  1. [t] UNIFIED SOURCE + PLUCK ARCHITECTURE COMPOSED

     v16 had unified source for [t] (ONE noise buffer,
     ONE envelope, subglottal floor). This eliminated
     internal boundaries inside the stop.

     But v16 was MISSING the pluck principle at the word level:
     the vowels before [t] had no closing tails, and the segments
     after [t] had no opening heads. The [t] still concatenated
     directly against the adjacent voiced segments.

     The problem: the [t] unified source starts at subglottal
     floor (0.001) — good. But the preceding vowel ends at
     full amplitude (~0.45). That amplitude jump is still audible.

     v17 COMPOSES BOTH PRINCIPLES (from PUROHITAM v4):

       PLUCK: vowels own transitions
         [ɑ]₁ and [aː] get closing tails (last 25ms fades)
         [n] and [ɑ]₃ get opening heads (first 15ms rises)

       UNIFIED SOURCE: [t] has no internal boundaries
         ONE noise buffer, ONE envelope, spike rides on noise,
         subglottal floor at edges.

     The two principles compose:
       [...vowel → closing tail → 0.00] + [0.001 → [t] unified → 0.001] + [0.00 → opening head → voiced...]

     All join boundaries at near-zero amplitude.

  2. FACTORED _synth_unified_voiceless_stop()
     Generalized helper (from PUROHITAM v4) replaces
     the inline synth_T(). Cleaner, reusable.

  3. make_closing_tail() / make_opening_head()
     Pluck helpers (from PUROHITAM v4 / ṚTVIJAM v9).

  4. [dʰ] UNCHANGED — v14 4-phase architecture.
     Voiced stops don't need pluck (continuous glottal source).

  5. ALL OTHER PHONEMES — unchanged.

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

# ── [ɾ] alveolar tap — VERIFIED PUROHITAM ──────────────────────
VS_R_F         = [300.0, 1900.0, 2700.0, 3300.0]
VS_R_B         = [120.0,  200.0,  250.0,  300.0]
VS_R_GAINS     = [ 12.0,    6.0,    1.5,    0.4]
VS_R_DUR_MS    = 30.0
VS_R_DIP_DEPTH = 0.35
VS_R_DIP_WIDTH = 0.40
VS_R_COART_ON  = 0.15
VS_R_COART_OFF = 0.15

# ── [ɑ] short open central — VERIFIED AGNI ─────────────────────
VS_A_F      = [700.0, 1100.0, 2550.0, 3400.0]
VS_A_B      = [130.0,  160.0,  220.0,  280.0]
VS_A_GAINS  = [ 16.0,    6.0,    1.5,    0.5]
VS_A_DUR_MS = 55.0
VS_A_COART_ON  = 0.12
VS_A_COART_OFF = 0.12

# ── [t] voiceless dental stop — v17 UNIFIED SOURCE + PLUCK ─────
VS_T_CLOSURE_MS  = 25.0
VS_T_BURST_MS    = 7.0
VS_T_VOT_MS      = 15.0

VS_T_BURST_F     = [1500.0, 3500.0, 5000.0, 6500.0]
VS_T_BURST_B     = [ 400.0,  600.0,  800.0, 1000.0]
VS_T_BURST_G     = [   4.0,   14.0,    6.0,    2.0]
VS_T_BURST_DECAY = 170.0

VS_T_BURST_GAIN  = 0.15
VS_T_PREBURST_MS   = 5.0
VS_T_PREBURST_AMP  = 0.008

# subglottal floor — the breath never truly stops
# ~-60dB relative to burst peak: inaudible but prevents digital zero
VS_T_SUBGLOTTAL_FLOOR = 0.001

VS_T_LOCUS_F     = [700.0, 1800.0, 2500.0, 3500.0]

# ── [n] dental nasal — VERIFIED AGNI ───────────────────────────
VS_N_F       = [250.0,  900.0, 2000.0, 3000.0]
VS_N_B       = [100.0,  200.0,  300.0,  350.0]
VS_N_GAINS   = [  8.0,    2.5,    0.5,    0.2]
VS_N_DUR_MS  = 60.0
VS_N_ANTI_F  = 800.0
VS_N_ANTI_BW = 200.0
VS_N_COART_ON  = 0.15
VS_N_COART_OFF = 0.15

# ── [dʰ] voiced dental aspirated — v14 ARCHITECTURE ────────────
VS_DH_CLOSURE_MS   = 28.0
VS_DH_BURST_MS     = 8.0
VS_DH_MURMUR_MS    = 50.0
VS_DH_CUTBACK_MS   = 25.0

VS_DH_VOICEBAR_F   = 250.0
VS_DH_VOICEBAR_BW  = 80.0
VS_DH_VOICEBAR_G   = 12.0
VS_DH_MURMUR_PEAK  = 0.25

VS_DH_BURST_F      = [1500.0, 3500.0, 5000.0, 6500.0]
VS_DH_BURST_B      = [ 400.0,  600.0,  800.0, 1000.0]
VS_DH_BURST_G      = [   4.0,   12.0,    5.0,    1.5]
VS_DH_BURST_DECAY  = 170.0
VS_DH_BURST_PEAK   = 0.15

VS_DH_MURMUR_GAIN  = 0.70
VS_DH_OQ           = 0.55
VS_DH_BW_MULT      = 1.5

VS_DH_CLOSED_F     = [250.0,  800.0, 2200.0, 3200.0]
VS_DH_CLOSED_B     = [150.0,  250.0,  300.0,  350.0]
VS_DH_CLOSED_G     = [ 10.0,    3.0,    0.8,    0.3]
VS_DH_CLOSED_PEAK  = 0.40
VS_DH_OPEN_PEAK    = 0.65
VS_DH_CUTBACK_PEAK = 0.55

# ── [aː] long open central — VERIFIED HOTĀRAM ──────────────────
VS_AA_F      = [700.0, 1100.0, 2550.0, 3400.0]
VS_AA_B      = [130.0,  160.0,  220.0,  280.0]
VS_AA_GAINS  = [ 16.0,    6.0,    1.5,    0.5]
VS_AA_DUR_MS = 110.0
VS_AA_COART_ON  = 0.12
VS_AA_COART_OFF = 0.12

# ── [m] bilabial nasal — VERIFIED PUROHITAM ────────────────────
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
    """Rosenberg glottal pulse model."""
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
    """Formant filter bank (IIR resonators) — b=[g] convention."""
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
    """Nasal antiresonance notch."""
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
    """Time-stretch via overlap-add."""
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
    """Temple courtyard reverb."""
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
# PLUCK HELPERS — CLOSING TAIL / OPENING HEAD
# ============================================================================

def make_closing_tail(voiced_seg, tail_ms=CLOSING_TAIL_MS, sr=SR):
    """
    The vowel OWNS the closure.

    Append a closing tail: the last tail_ms of voiced signal
    continues from the same Rosenberg source but with amplitude
    fading as the articulator moves toward constriction.

    The signal never jumps to zero — it decays smoothly from
    the vowel's own resonance. The concatenation boundary after
    this tail will be at near-zero amplitude.
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
    The next segment OWNS the VOT / onset.

    Prepend an opening head: the first head_ms of voiced signal
    rises from near-zero as voicing resumes after a voiceless
    segment.

    The concatenation boundary before this head matches the
    near-zero end of the voiceless segment.
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
# (factored into reusable helper in PUROHITAM v4)
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
    env[:n_cl] = subglottal_floor

    # Phase B: Pre-burst crescendo (last preburst_ms of closure)
    n_pre = int(preburst_ms * dil / 1000.0 * SR)
    if n_pre > 0 and n_cl > n_pre:
        t_pre = np.linspace(0.0, 1.0, n_pre)
        crescendo = subglottal_floor + (preburst_amp - subglottal_floor) * (
            1.0 - np.exp(-3.0 * t_pre))
        env[n_cl - n_pre:n_cl] = crescendo

    # Phase C+D: Burst peak + decay
    if n_b > 0:
        t_burst = np.arange(n_b) / SR
        burst_env = burst_gain * np.exp(-t_burst * burst_decay)
        burst_env = np.maximum(burst_env, subglottal_floor)
        env[n_cl:n_cl + n_b] = burst_env

    # Phase D continued: VOT decay
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

    # ── SPIKE IMPULSE (RIDES ON NOISE) ────────────────────
    spike_raw = np.zeros(n_total, dtype=float)
    if n_cl < n_total:
        spike_len = min(3, n_total - n_cl)
        spike_vals = [1.0, 0.6, 0.3][:spike_len]
        spike_raw[n_cl:n_cl + spike_len] = spike_vals

    spike_filt = apply_formants(f32(spike_raw), burst_f, burst_b, burst_g)
    spike_env = np.zeros(n_total, dtype=float)
    if n_b > 0:
        t_se = np.arange(n_b) / SR
        spike_env[n_cl:n_cl + n_b] = np.exp(-t_se * burst_decay)
    spike_out = f32(spike_filt * spike_env * burst_gain)

    # ── PHASE E: VOICED COMPONENT (FADES IN DURING VOT) ──
    f_vot = list(vot_locus_f)
    if F_next is not None:
        for k in range(min(len(F_next), len(f_vot))):
            f_vot[k] = vot_locus_f[k] * 0.7 + F_next[k] * 0.3

    vot_voiced = np.zeros(n_total, dtype=float)
    if n_v > 0:
        src_vot = rosenberg_pulse(n_v, pitch_hz)
        vot_filt = apply_formants(src_vot, f_vot, vot_vowel_b, vot_vowel_gains)
        fade_in = np.linspace(0.0, 1.0, n_v)
        vot_filt = vot_filt * fade_in * 0.12
        vot_voiced[n_cl + n_b:n_cl + n_b + n_v] = vot_filt[:n_v]

    # ── COMBINE ───────────────────────────────────────────
    out = noise_out + spike_out + vot_voiced

    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.55
    return f32(out)


# ============================================================================
# PHONEME SYNTHESIS FUNCTIONS
# ============================================================================

def synth_R(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=DIL):
    """[ɾ] alveolar tap (VERIFIED PUROHITAM)."""
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
    n_dip = int(n * VS_R_DIP_WIDTH)
    dip_start = (n - n_dip) // 2
    if n_dip > 0 and dip_start >= 0:
        dip_env = np.ones(n, dtype=float)
        dip = 1.0 - VS_R_DIP_DEPTH * np.hanning(n_dip)
        dip_env[dip_start:dip_start + n_dip] = dip
        out = f32(out * dip_env)

    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.55
    return f32(out)


def synth_A(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=DIL,
            closing_for_stop=False):
    """
    [ɑ] short open central (VERIFIED AGNI).

    closing_for_stop=True: append closing tail.
    The vowel owns the transition into the stop.
    The last 25ms fades as the tongue moves toward seal position.
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

    if closing_for_stop:
        out = make_closing_tail(f32(out), CLOSING_TAIL_MS)

    return f32(out)


def synth_T(F_next=None, pitch_hz=PITCH_HZ, dil=DIL):
    """
    [t] voiceless dental stop — v17 UNIFIED SOURCE

    The breath is continuous. The tongue is the envelope.
    ONE noise buffer. ONE amplitude envelope.
    The spike rides on the noise floor.

    Uses the factored _synth_unified_voiceless_stop() helper.
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
        vot_vowel_b=VS_A_B,
        vot_vowel_gains=[g * 0.3 for g in VS_A_GAINS],
        pitch_hz=pitch_hz,
        dil=dil,
    )


def synth_N(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=DIL,
            opening_from_stop=False):
    """
    [n] dental nasal (VERIFIED AGNI).

    opening_from_stop=True: prepend opening head.
    The nasal owns the onset after the voiceless stop.
    The first 15ms rises from near-zero as voicing resumes.
    """
    n = int(VS_N_DUR_MS * dil / 1000.0 * SR)
    src = rosenberg_pulse(n, pitch_hz)

    f_mean = list(VS_N_F)
    if F_prev is not None:
        for k in range(min(len(F_prev), len(VS_N_F))):
            f_mean[k] = (F_prev[k] * VS_N_COART_ON +
                         VS_N_F[k] * (1.0 - VS_N_COART_ON))
    if F_next is not None:
        for k in range(min(len(F_next), len(VS_N_F))):
            f_mean[k] = (f_mean[k] * (1.0 - VS_N_COART_OFF) +
                         F_next[k] * VS_N_COART_OFF)

    out = apply_formants(src, f_mean, VS_N_B, VS_N_GAINS)
    out = iir_notch(out, VS_N_ANTI_F, VS_N_ANTI_BW)

    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.42

    if opening_from_stop:
        out = make_opening_head(f32(out), OPENING_HEAD_MS)

    return f32(out)


def synth_DH(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=DIL):
    """
    [dʰ] voiced dental aspirated stop — v14 ARCHITECTURE

    Śikṣā: dantya ghoṣa mahāprāṇa
    Voiced, aspirated, dental.

    Phase 1: Voice bar closure (250 Hz, BW 80)
    Phase 2: Burst at dental locus
    Phase 3: Breathy murmur (OQ 0.55, BW 1.5×)
    Phase 4: Crossfade cutback (murmur → open)

    Voiced stops don't need pluck — continuous glottal source.
    """
    n_cl = int(VS_DH_CLOSURE_MS * dil / 1000.0 * SR)
    n_b  = int(VS_DH_BURST_MS * dil / 1000.0 * SR)
    n_mu = int(VS_DH_MURMUR_MS * dil / 1000.0 * SR)
    n_cb = int(VS_DH_CUTBACK_MS * dil / 1000.0 * SR)

    f_next = F_next if F_next is not None else VS_AA_F

    # Phase 1: Voice bar closure
    if n_cl > 0:
        src_cl = rosenberg_pulse(n_cl, pitch_hz, oq=0.65)
        murmur_cl = apply_formants(
            src_cl,
            [VS_DH_VOICEBAR_F],
            [VS_DH_VOICEBAR_BW],
            [VS_DH_VOICEBAR_G])
        env_cl = np.ones(n_cl, dtype=float)
        ramp_n = max(1, int(0.3 * n_cl))
        env_cl[:ramp_n] = np.linspace(0.3, 1.0, ramp_n)
        murmur_cl = f32(murmur_cl * env_cl)
        closure = norm_to_peak(murmur_cl, VS_DH_MURMUR_PEAK)
    else:
        closure = np.array([], dtype=DTYPE)

    # Phase 2: Burst
    spike = np.zeros(max(n_b, 16), dtype=float)
    spike[0:3] = [1.0, 0.6, 0.3]

    turbulence = np.random.randn(len(spike))
    turbulence_filt = apply_formants(
        turbulence, VS_DH_BURST_F, VS_DH_BURST_B, VS_DH_BURST_G)

    t_b = np.arange(len(spike)) / SR
    mix_env = np.exp(-t_b * VS_DH_BURST_DECAY)
    burst_raw = spike * mix_env + turbulence_filt * (1.0 - mix_env) * 0.30
    burst = norm_to_peak(f32(burst_raw), VS_DH_BURST_PEAK)

    # Phase 3: Breathy murmur
    if n_mu > 0:
        src_mu = rosenberg_pulse(n_mu, pitch_hz, oq=VS_DH_OQ)
        bws_mu = [bw * VS_DH_BW_MULT for bw in VS_DH_BURST_B]
        gains_mu = [g * VS_DH_MURMUR_GAIN for g in VS_DH_BURST_G]
        murmur = apply_formants(src_mu, VS_DH_BURST_F, bws_mu, gains_mu)

        mx_mu = np.max(np.abs(murmur))
        if mx_mu > 1e-8:
            murmur = murmur / mx_mu * VS_DH_MURMUR_PEAK
        murmur = f32(murmur)
    else:
        murmur = np.array([], dtype=DTYPE)

    # Phase 4: Crossfade cutback
    if n_cb > 0:
        src_cb = rosenberg_pulse(n_cb, pitch_hz)
        sig_closed = apply_formants(
            src_cb, VS_DH_CLOSED_F, VS_DH_CLOSED_B, VS_DH_CLOSED_G)
        sig_closed = norm_to_peak(sig_closed, VS_DH_CLOSED_PEAK)

        sig_open = apply_formants(
            src_cb, list(f_next),
            [100.0, 140.0, 200.0, 260.0],
            [14.0, 8.0, 1.5, 0.5])
        sig_open = norm_to_peak(sig_open, VS_DH_OPEN_PEAK)

        t_fade = np.linspace(0.0, np.pi / 2.0, n_cb)
        fade_out = np.cos(t_fade).astype(DTYPE)
        fade_in  = np.sin(t_fade).astype(DTYPE)
        cutback = f32(sig_closed * fade_out + sig_open * fade_in)
        cb_env = np.linspace(0.6, 1.0, n_cb).astype(DTYPE)
        cutback = f32(cutback * cb_env)
        cutback = norm_to_peak(cutback, VS_DH_CUTBACK_PEAK)
    else:
        cutback = np.array([], dtype=DTYPE)

    out = np.concatenate([closure, burst, murmur, cutback])
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.60
    return f32(out)


def synth_AA(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=DIL,
             closing_for_stop=False):
    """
    [aː] long open central (VERIFIED HOTĀRAM).

    closing_for_stop=True: append closing tail.
    The vowel owns the transition into the stop.
    """
    n = int(VS_AA_DUR_MS * dil / 1000.0 * SR)
    src = rosenberg_pulse(n, pitch_hz)

    f_mean = list(VS_AA_F)
    if F_prev is not None:
        for k in range(min(len(F_prev), len(VS_AA_F))):
            f_mean[k] = (F_prev[k] * VS_AA_COART_ON +
                         VS_AA_F[k] * (1.0 - VS_AA_COART_ON))
    if F_next is not None:
        for k in range(min(len(F_next), len(VS_AA_F))):
            f_mean[k] = (f_mean[k] * (1.0 - VS_AA_COART_OFF) +
                         F_next[k] * VS_AA_COART_OFF)

    out = apply_formants(src, f_mean, VS_AA_B, VS_AA_GAINS)

    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.72

    if closing_for_stop:
        out = make_closing_tail(f32(out), CLOSING_TAIL_MS)

    return f32(out)


def synth_M(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=DIL,
            word_final=False):
    """[m] bilabial nasal (VERIFIED PUROHITAM)."""
    n = int(VS_M_DUR_MS * dil / 1000.0 * SR)
    src = rosenberg_pulse(n, pitch_hz)

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

    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.42

    if word_final:
        n_rel = int(VS_M_RELEASE_MS * dil / 1000.0 * SR)
        if n_rel > 0:
            release = np.zeros(n_rel, dtype=DTYPE)
            if len(out) > 0:
                tail_amp = abs(float(out[-1]))
                release[:min(3, n_rel)] = tail_amp * np.array(
                    [0.5, 0.2, 0.05])[:min(3, n_rel)]
            fade = np.exp(-np.linspace(0, 5.0, n_rel))
            release = f32(release * fade)
            out = f32(np.concatenate([out, release]))

    return f32(out)


# ============================================================================
# WORD SYNTHESIS
# ============================================================================

def synth_ratnadhatamam(pitch_hz=PITCH_HZ, dil=DIL, with_room=False):
    """
    RATNADHĀTAMAM [rɑtnɑdʰaːtɑmɑm] — v17
    Rigveda 1.1.1, word 9
    Syllables: RAT.NA.DHĀ.TA.MAM

    v17 UNIFIED PLUCK ARCHITECTURE:

      [t] unified source (ONE buffer, ONE envelope, spike on noise)
        Internal phases: closure → preburst → burst → VOT
        Subglottal floor at edges. No internal boundaries.

      PLUCK architecture at word level:
        [ɑ]₁ closing tail → [t]₁ → opening head + [n]
        [aː] closing tail → [t]₂ → opening head + [ɑ]₃

      [dʰ] voiced: voice bar → burst → murmur → cutback
        Continuous glottal source. No pluck needed.

    Segment map:
      [r]                             30ms   alveolar tap
      [ɑ]₁ + closing tail            80ms   55ms vowel + 25ms fade
      [t]₁ UNIFIED                   47ms   closure + burst + VOT
      head + [n]                     75ms   15ms rise + 60ms nasal
      [ɑ]₂                           55ms   short open central
      [dʰ]                          111ms   voice bar + burst + murmur + cutback
      [aː] + closing tail           135ms   110ms vowel + 25ms fade
      [t]₂ UNIFIED                   47ms   closure + burst + VOT
      head + [ɑ]₃                    70ms   15ms rise + 55ms vowel
      [m]₁                           60ms   bilabial nasal
      [ɑ]₄                           55ms   short open central
      [m]₂ + release                 80ms   60ms nasal + 20ms release

    All voiced-to-voiceless transitions use closing tails.
    All voiceless-to-voiced transitions use opening heads.
    All voiceless stops use unified source (subglottal floor).
    No boundary anywhere is born from different sources.
    """
    segs = [
        # [r]
        synth_R(F_prev=None, F_next=VS_A_F,
                pitch_hz=pitch_hz, dil=dil),

        # [ɑ]₁ with closing tail (vowel owns closure before [t]₁)
        synth_A(F_prev=VS_R_F, F_next=VS_T_LOCUS_F,
                pitch_hz=pitch_hz, dil=dil,
                closing_for_stop=True),

        # [t]₁ UNIFIED SOURCE
        synth_T(F_next=VS_N_F,
                pitch_hz=pitch_hz, dil=dil),

        # [n] with opening head (nasal owns onset after [t]₁)
        synth_N(F_prev=VS_T_LOCUS_F, F_next=VS_A_F,
                pitch_hz=pitch_hz, dil=dil,
                opening_from_stop=True),

        # [ɑ]₂
        synth_A(F_prev=VS_N_F, F_next=VS_DH_CLOSED_F,
                pitch_hz=pitch_hz, dil=dil),

        # [dʰ] (voiced — no pluck needed)
        synth_DH(F_prev=VS_A_F, F_next=VS_AA_F,
                 pitch_hz=pitch_hz, dil=dil),

        # [aː] with closing tail (vowel owns closure before [t]₂)
        synth_AA(F_prev=VS_DH_CLOSED_F, F_next=VS_T_LOCUS_F,
                 pitch_hz=pitch_hz, dil=dil,
                 closing_for_stop=True),

        # [t]₂ UNIFIED SOURCE
        synth_T(F_next=VS_A_F,
                pitch_hz=pitch_hz, dil=dil),

        # [ɑ]₃ with opening head (vowel owns onset after [t]₂)
        synth_A(F_prev=VS_T_LOCUS_F, F_next=VS_M_F,
                pitch_hz=pitch_hz, dil=dil,
                closing_for_stop=False),

        # [m]₁
        synth_M(F_prev=VS_A_F, F_next=VS_A_F,
                pitch_hz=pitch_hz, dil=dil),

        # [ɑ]₄
        synth_A(F_prev=VS_M_F, F_next=VS_M_F,
                pitch_hz=pitch_hz, dil=dil),

        # [m]₂ + release (word-final)
        synth_M(F_prev=VS_A_F, F_next=None,
                pitch_hz=pitch_hz, dil=dil,
                word_final=True),
    ]

    # [ɑ]₃ needs opening head prepended
    # (synth_A doesn't have opening_from_stop, so we do it here)
    segs[8] = make_opening_head(segs[8], OPENING_HEAD_MS)

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
    print("RATNADHĀTAMAM v17 — UNIFIED SOURCE + PLUCK ARCHITECTURE")
    print("=" * 70)
    print()
    print("v16→v17 CHANGES:")
    print()
    print("  TWO PRINCIPLES COMPOSED:")
    print()
    print("  1. UNIFIED SOURCE (from v16):")
    print("     [t] has ONE noise buffer, ONE envelope, spike on noise.")
    print("     No internal boundaries. Subglottal floor at edges.")
    print()
    print("  2. PLUCK ARCHITECTURE (from PUROHITAM v4):")
    print("     Vowels own transitions into/out of voiceless stops.")
    print("     [ɑ]₁ closing tail → [t]₁ → opening head + [n]")
    print("     [aː] closing tail → [t]₂ → opening head + [ɑ]₃")
    print()
    print("  RESULT: All join boundaries at near-zero amplitude.")
    print("     [...vowel → tail → 0.00] + [0.001 → [t] → 0.001]")
    print("                               + [0.00 → head → voiced...]")
    print()

    # Diagnostic speed
    word_dry = synth_ratnadhatamam(PITCH_HZ, 1.0)
    word_slow = ola_stretch(word_dry, 6.0)
    word_slow12 = ola_stretch(word_dry, 12.0)

    # Performance speed
    word_perf = synth_ratnadhatamam(PITCH_HZ, 2.5)
    word_perf_hall = synth_ratnadhatamam(PITCH_HZ, 2.5, with_room=True)

    # Hall
    word_hall = synth_ratnadhatamam(PITCH_HZ, 1.0, with_room=True)

    write_wav("output_play/ratnadhatamam_v17_dry.wav", word_dry)
    write_wav("output_play/ratnadhatamam_v17_slow6x.wav", word_slow)
    write_wav("output_play/ratnadhatamam_v17_slow12x.wav", word_slow12)
    write_wav("output_play/ratnadhatamam_v17_hall.wav", word_hall)
    write_wav("output_play/ratnadhatamam_v17_perf.wav", word_perf)
    write_wav("output_play/ratnadhatamam_v17_perf_hall.wav", word_perf_hall)

    # Isolated [t] unified
    t_iso = synth_T(F_next=VS_A_F, pitch_hz=PITCH_HZ, dil=DIL)
    mx = np.max(np.abs(t_iso))
    if mx > 1e-8:
        t_iso = t_iso / mx * 0.75
    t_iso = f32(t_iso)

    write_wav("output_play/ratnadhatamam_v17_t_unified.wav", t_iso)
    write_wav("output_play/ratnadhatamam_v17_t_unified_slow6x.wav",
              ola_stretch(t_iso, 6.0))
    write_wav("output_play/ratnadhatamam_v17_t_unified_slow12x.wav",
              ola_stretch(t_iso, 12.0))

    # AT syllable (boundary test)
    a_closing = synth_A(F_prev=VS_R_F, F_next=VS_T_LOCUS_F,
                        closing_for_stop=True)
    t_seg = synth_T(F_next=VS_N_F)
    n_opening = synth_N(F_prev=VS_T_LOCUS_F, F_next=VS_A_F,
                        opening_from_stop=True)
    at_syl = np.concatenate([a_closing, t_seg, n_opening])
    mx = np.max(np.abs(at_syl))
    if mx > 1e-8:
        at_syl = at_syl / mx * 0.75
    at_syl = f32(at_syl)

    write_wav("output_play/ratnadhatamam_v17_ATn_syllable.wav", at_syl)
    write_wav("output_play/ratnadhatamam_v17_ATn_syllable_slow6x.wav",
              ola_stretch(at_syl, 6.0))
    write_wav("output_play/ratnadhatamam_v17_ATn_syllable_slow12x.wav",
              ola_stretch(at_syl, 12.0))

    print()
    n_word = len(word_dry)
    print(f"  Word length: {n_word} samples ({n_word/SR*1000:.1f} ms)")
    print()
    print("=" * 70)
    print("v17 synthesis complete.")
    print()
    print("LISTEN FOR BOUNDARY TEST:")
    print("  afplay output_play/ratnadhatamam_v17_ATn_syllable_slow12x.wav")
    print("  afplay output_play/ratnadhatamam_v17_t_unified_slow6x.wav")
    print("  afplay output_play/ratnadhatamam_v17_slow6x.wav")
    print("  afplay output_play/ratnadhatamam_v17_perf_hall.wav")
    print()
    print("THE [t] SHOULD SOUND NATURAL — NOT TOO HARSH:")
    print("  v16: [t] unified source but no closing tails / opening heads")
    print("  v17: [t] unified source + closing tails + opening heads")
    print("       The [t] is now a pluck between smooth transitions")
    print("       All joins at near-zero amplitude")
    print("=" * 70)
    print()
