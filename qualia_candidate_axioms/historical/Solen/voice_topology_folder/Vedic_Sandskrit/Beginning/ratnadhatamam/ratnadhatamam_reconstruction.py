#!/usr/bin/env python3
"""
RATNADHĀTAMAM v16
Vedic Sanskrit: ratnadhātamam [rɑtnɑdʰaːtɑmɑm]
Rigveda 1.1.1 — word 9

v15→v16 CHANGES:

  1. [t] UNIFIED SOURCE ARCHITECTURE — THE BREATH IS CONTINUOUS

     v15 concatenated three separate arrays (closure, burst, vot).
     The click lived at the array boundary — closure[-1] ≈ 0.008,
     burst[0] = 0.0. No amount of ramping fixes a concatenation
     boundary between arrays born from different sources.

     The lesson from DEVAM [d] v13 crossfade: voiced stops don't
     click because ONE continuous source is filtered and shaped.
     There is no concatenation boundary. The signal is born continuous.

     v16 INSIGHT: The breath is continuous. The diaphragm pushes air
     through the vocal tract as a steady stream. During closure, the
     tongue seal pressurizes the tract — the airflow doesn't stop,
     it builds pressure. The seal modulates what escapes, but the
     source is always there.

     The noise buffer IS the breath. The envelope IS the tongue.

     v16 SOLUTION: Generate ONE continuous noise buffer spanning the
     entire stop duration. Shape it with ONE continuous amplitude
     envelope that models the physics:

       Phase A: Near-silence (closure — tongue sealed, pressure builds)
                NOT digital zero — subglottal pressure transmits a
                floor-level signal through the tract walls (~-60dB)
       Phase B: Exponential crescendo (pre-burst leak, 5ms — air
                begins escaping through weakening seal)
       Phase C: Burst peak (release transient at dental locus ~3764Hz)
       Phase D: Burst decay into aspiration noise (VOT region)
       Phase E: Voiced component fades in additively (replaces noise)

     Because the noise source is continuous and the envelope is
     continuous, there is NO sample-level discontinuity anywhere.

     The spike impulse is ADDED to the continuous noise at burst
     onset — it rides on top of the noise floor rather than
     emerging from silence.

  2. [m] FINAL RELEASE — unchanged from v15 (20ms fadeout)

  3. ALL OTHER PHONEMES — unchanged from v15

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

# ── [t] voiceless dental stop — v16 UNIFIED SOURCE ─────────────
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

# v16: subglottal floor — the breath never truly stops
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
    """Nasal antiresonance"""
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
# PHONEME SYNTHESIS FUNCTIONS
# ============================================================================

def synth_R(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=DIL):
    """[ɾ] alveolar tap (VERIFIED PUROHITAM)"""
    n = int(VS_R_DUR_MS * dil / 1000.0 * SR)
    src = rosenberg_pulse(n, pitch_hz)

    f_mean = list(VS_R_F)
    if F_prev is not None:
        for k in range(min(len(F_prev), len(VS_R_F))):
            f_mean[k] = F_prev[k] * VS_R_COART_ON + VS_R_F[k] * (1.0 - VS_R_COART_ON)
    if F_next is not None:
        for k in range(min(len(F_next), len(VS_R_F))):
            f_mean[k] = f_mean[k] * (1.0 - VS_R_COART_OFF) + F_next[k] * VS_R_COART_OFF

    out = apply_formants(src, f_mean, VS_R_B, VS_R_GAINS)

    # Tap dip
    t = np.linspace(0, 1, n)
    dip_env = 1.0 - VS_R_DIP_DEPTH * np.exp(-((t - 0.5) / VS_R_DIP_WIDTH) ** 2 * 10.0)
    out = out * dip_env

    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.65
    return f32(out)


def synth_A(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=DIL):
    """[ɑ] short open central (VERIFIED AGNI)"""
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


def synth_T(F_next=None, pitch_hz=PITCH_HZ, dil=DIL):
    """
    [t] voiceless dental stop — v16 UNIFIED SOURCE

    THE BREATH IS CONTINUOUS. The diaphragm pushes air through the
    vocal tract as a steady stream. During closure, the tongue seal
    pressurizes the tract — the airflow doesn't stop, it builds
    pressure behind the seal. The seal modulates what escapes, but
    the source (subglottal pressure, airflow) is always there.

    The noise buffer IS the breath. The envelope IS the tongue.

    v16 generates ONE continuous noise buffer spanning the entire
    stop. ONE continuous amplitude envelope shapes it:

      Phase A: Subglottal floor (~-60dB) — not digital zero.
               The body is producing pressure. The tract walls
               transmit some energy. The signal is never truly zero.
      Phase B: Exponential crescendo (pre-burst leak, 5ms) — air
               begins escaping through the weakening dental seal as
               intraoral pressure overcomes closure force.
      Phase C: Burst peak — release transient at dental locus.
               Spike impulse ADDED to continuous noise (rides on top).
      Phase D: Burst decay into aspiration noise (VOT region).
      Phase E: Voiced component fades in additively (glottal source
               replaces turbulence as the vocal folds close).

    Because the noise source is continuous and the envelope is
    continuous, there is NO sample-level discontinuity anywhere.

    This is the same architectural principle as DEVAM [d] v13
    crossfade: one continuous source, shaped continuously.
    The difference: [d] has a voiced (periodic) source throughout;
    [t] has a noise (aperiodic) source throughout closure+burst,
    with voicing fading in additively during VOT.
    """
    n_cl = int(VS_T_CLOSURE_MS / 1000.0 * SR)
    n_b  = int(VS_T_BURST_MS / 1000.0 * SR)
    n_v  = int(VS_T_VOT_MS / 1000.0 * SR)
    n_total = n_cl + n_b + n_v

    # ── UNIFIED NOISE SOURCE ──────────────────────────────
    # One continuous buffer. No boundaries. This IS the breath.
    noise_source = np.random.randn(n_total).astype(float)

    # ── CONTINUOUS AMPLITUDE ENVELOPE ─────────────────────
    # This IS the tongue. It modulates the breath.
    env = np.zeros(n_total, dtype=float)

    # Phase A: Subglottal floor during closure
    # NOT digital zero — the body transmits pressure through
    # tract walls even during complete oral closure.
    # This eliminates any digital-silence-to-noise transition.
    silence_n = n_cl - min(int(VS_T_PREBURST_MS / 1000.0 * SR), n_cl)
    preburst_n = n_cl - silence_n

    env[0:silence_n] = VS_T_SUBGLOTTAL_FLOOR

    # Phase B: Exponential crescendo (pre-burst leak)
    # Intraoral pressure overcomes closure force. Air begins
    # leaking through the weakening seal. Crescendo into release.
    if preburst_n > 0:
        t_pre = np.linspace(0.0, 1.0, preburst_n)
        # exp(-3) ≈ 0.05 at start, 1.0 at end
        crescendo = VS_T_SUBGLOTTAL_FLOOR + \
            (VS_T_PREBURST_AMP - VS_T_SUBGLOTTAL_FLOOR) * np.exp(3.0 * (t_pre - 1.0))
        env[silence_n : n_cl] = crescendo

    # Phase C: Burst (dental locus resonance)
    # Sharp attack, exponential decay. The tongue releases the seal.
    # Compressed air escapes through the small dantya cavity.
    burst_start = n_cl
    burst_end   = n_cl + n_b
    t_burst = np.arange(n_b, dtype=float) / SR
    burst_env = VS_T_BURST_GAIN * np.exp(-t_burst * VS_T_BURST_DECAY)
    env[burst_start : burst_end] = burst_env

    # Smooth the closure→burst transition: the envelope must be
    # continuous. The crescendo peak should meet the burst onset.
    # Use a short cosine blend across the junction so there is
    # no slope discontinuity (kink) in the envelope.
    blend_n = min(int(0.001 * SR), preburst_n, n_b)  # 1ms
    if blend_n > 1:
        left_val  = env[burst_start - 1] if burst_start > 0 else VS_T_SUBGLOTTAL_FLOOR
        right_val = env[burst_start]
        # Cosine interpolation for smooth derivative at junction
        t_blend = np.linspace(0.0, np.pi, blend_n)
        blend_curve = left_val + (right_val - left_val) * 0.5 * (1.0 - np.cos(t_blend))
        half = blend_n // 2
        start_idx = max(0, burst_start - half)
        end_idx = start_idx + blend_n
        if end_idx <= n_total:
            env[start_idx : end_idx] = blend_curve

    # Phase D: Burst decay into VOT aspiration
    # Aspiration noise decays as the tract opens and voicing begins.
    vot_start = burst_end
    vot_end   = n_total
    if n_v > 0:
        t_vot = np.linspace(0.0, 1.0, n_v)
        # Decay from burst tail level to subglottal floor
        burst_tail = burst_env[-1] if n_b > 0 else VS_T_BURST_GAIN * 0.1
        aspiration_decay = burst_tail * np.exp(-t_vot * 3.0)
        # Floor: don't decay below subglottal level
        aspiration_decay = np.maximum(aspiration_decay, VS_T_SUBGLOTTAL_FLOOR)
        env[vot_start : vot_end] = aspiration_decay

    # ── APPLY DENTAL LOCUS FORMANTS ──────────────────────
    # ONE filter pass across the entire buffer. No filter restarts,
    # no frame boundaries. The formant resonances shape the noise
    # continuously — the same cavity is resonating throughout.
    noise_shaped = apply_formants(
        noise_source,
        VS_T_BURST_F, VS_T_BURST_B, VS_T_BURST_G)

    # Apply the continuous envelope
    noise_out = f32(noise_shaped * env)

    # ── ADD SPIKE TRANSIENT AT BURST ONSET ────────────────
    # The spike models the initial pressure release transient —
    # the moment the tongue seal breaks and compressed air explodes.
    # It is ADDED to the continuous noise, not concatenated.
    # It rides on top of the noise floor — no boundary.
    spike = np.zeros(n_total, dtype=float)
    spike_len = min(3, n_b)
    spike_vals = [1.0, 0.6, 0.3][:spike_len]
    for i, sv in enumerate(spike_vals):
        if burst_start + i < n_total:
            spike[burst_start + i] = sv

    spike_env = np.zeros(n_total, dtype=float)
    if n_b > 0:
        spike_env[burst_start:burst_end] = np.exp(
            -np.arange(n_b, dtype=float) / SR * VS_T_BURST_DECAY)
    spike_out = f32(spike * spike_env * VS_T_BURST_GAIN * 0.5)

    # ── PHASE E: VOICED COMPONENT (FADES IN DURING VOT) ──
    # The glottal source (Rosenberg pulses) replaces the noise
    # source as the vocal folds close after the voiceless stop.
    # This is additive — voicing fades in as aspiration fades out.
    f_vot = list(VS_T_LOCUS_F)
    if F_next is not None:
        for k in range(min(len(F_next), len(f_vot))):
            f_vot[k] = VS_T_LOCUS_F[k] * 0.7 + F_next[k] * 0.3

    vot_voiced = np.zeros(n_total, dtype=float)
    if n_v > 0:
        src_voiced = rosenberg_pulse(n_v, pitch_hz)
        # Voicing fades in as aspiration fades out
        voicing_env = np.linspace(0.0, 1.0, n_v)
        vot_filt = apply_formants(
            src_voiced, f_vot,
            VS_A_B,
            [g * 0.4 for g in VS_A_GAINS])
        vot_voiced[vot_start:vot_end] = f32(vot_filt * voicing_env * 0.15)

    # ── COMBINE ───────────────────────────────────────────
    # Three components, all born from continuous sources,
    # all shaped by continuous envelopes, all additive.
    # No concatenation boundaries anywhere.
    out = noise_out + spike_out + vot_voiced

    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.55
    return f32(out)


def synth_N(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=DIL):
    """[n] dental nasal (VERIFIED AGNI)"""
    n = int(VS_N_DUR_MS * dil / 1000.0 * SR)
    src = rosenberg_pulse(n, pitch_hz)

    f_mean = list(VS_N_F)
    if F_prev is not None:
        for k in range(min(len(F_prev), len(VS_N_F))):
            f_mean[k] = F_prev[k] * VS_N_COART_ON + VS_N_F[k] * (1.0 - VS_N_COART_ON)
    if F_next is not None:
        for k in range(min(len(F_next), len(VS_N_F))):
            f_mean[k] = f_mean[k] * (1.0 - VS_N_COART_OFF) + F_next[k] * VS_N_COART_OFF

    out = apply_formants(src, f_mean, VS_N_B, VS_N_GAINS)
    out = iir_notch(out, VS_N_ANTI_F, VS_N_ANTI_BW)

    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.42
    return f32(out)


def synth_DH(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=DIL):
    """
    [dʰ] voiced dental aspirated stop — v14 ARCHITECTURE (unchanged)

    Phase 1: Voice bar closure (250 Hz, BW 80)
    Phase 2: v7 spike+turbulence burst at dantya locus
    Phase 3: v11 murmur (OQ 0.55, BW×1.5)
    Phase 4: Crossfade cutback closed→open
    """
    n_cl = int(VS_DH_CLOSURE_MS * dil / 1000.0 * SR)
    n_b = int(VS_DH_BURST_MS * dil / 1000.0 * SR)
    n_m = int(VS_DH_MURMUR_MS * dil / 1000.0 * SR)
    n_cb = int(VS_DH_CUTBACK_MS * dil / 1000.0 * SR)

    f_next = F_next if F_next is not None else VS_AA_F

    # Phase 1: Voice bar
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

    # Phase 2: v7 burst (no boundary fix needed — voiced)
    spike = np.zeros(max(n_b, 16), dtype=float)
    spike[0:3] = [1.0, 0.6, 0.3]
    turbulence = np.random.randn(len(spike))
    turbulence_filt = apply_formants(
        turbulence, VS_DH_BURST_F, VS_DH_BURST_B, VS_DH_BURST_G)
    t_b = np.arange(len(spike)) / SR
    mix_env = np.exp(-t_b * VS_DH_BURST_DECAY)
    burst_raw = spike * mix_env + turbulence_filt * (1.0 - mix_env) * 0.30
    burst = norm_to_peak(f32(burst_raw), VS_DH_BURST_PEAK)

    # Phase 3: v11 murmur (OQ 0.55, BW×1.5)
    murmur_pulse = rosenberg_pulse(n_m, pitch_hz, oq=VS_DH_OQ)
    murmur_bws = [bw * VS_DH_BW_MULT for bw in VS_AA_B]
    murmur_filtered = apply_formants(
        murmur_pulse, VS_AA_F, murmur_bws, VS_AA_GAINS)
    attack = int(n_m * 0.15)
    env_m = np.ones(n_m, dtype=float)
    if attack > 0:
        env_m[:attack] = np.linspace(0.5, 1.0, attack)
        env_m[-attack:] = np.linspace(1.0, 0.9, attack)
    murmur = f32(murmur_filtered * env_m * VS_DH_MURMUR_GAIN)

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
        fade_in = np.sin(t_fade).astype(DTYPE)
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


def synth_AA(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=DIL):
    """[aː] long open central (VERIFIED HOTĀRAM)"""
    n = int(VS_AA_DUR_MS * dil / 1000.0 * SR)
    src = rosenberg_pulse(n, pitch_hz)

    f_mean = list(VS_AA_F)
    if F_prev is not None:
        for k in range(min(len(F_prev), len(VS_AA_F))):
            f_mean[k] = F_prev[k] * VS_AA_COART_ON + VS_AA_F[k] * (1.0 - VS_AA_COART_ON)
    if F_next is not None:
        for k in range(min(len(F_next), len(VS_AA_F))):
            f_mean[k] = f_mean[k] * (1.0 - VS_AA_COART_OFF) + F_next[k] * VS_AA_COART_OFF

    out = apply_formants(src, f_mean, VS_AA_B, VS_AA_GAINS)

    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.72
    return f32(out)


def synth_M(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=DIL,
            word_final=False):
    """
    [m] bilabial nasal (VERIFIED PUROHITAM)

    v15: word_final=True adds 20ms release tail.
    The lips open, the nasal resonance fades.
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

    # Word-final release: gentle fadeout over last n_release samples
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

def synth_ratnadhatamam(pitch_hz=PITCH_HZ, dil=DIL, with_room=False):
    """
    RATNADHĀTAMAM [rɑtnɑdʰaːtɑmɑm] — v16
    Rigveda 1.1.1, word 9
    Syllables: RAT-NA-DHĀ-TA-MAM

    v16 changes from v15:
      [t] ×2: UNIFIED SOURCE ARCHITECTURE
              One continuous noise buffer + one continuous envelope.
              No array concatenation boundaries.
              The breath is continuous. The tongue is the envelope.
      All other phonemes unchanged from v15.

    Segment sequence:
      r   [ɾ]   tap              → [ɑ]
      a   [ɑ]   short open       ← [ɾ] → [t]
      t₁  [t]   voiceless dental ← . → [n]
      n   [n]   dental nasal     ← [t] → [ɑ]
      a   [ɑ]   short open       ← [n] → [dʰ]
      dh  [dʰ]  voiced asp.      ← [ɑ] → [aː]
      ā   [aː]  long open        ← [dʰ] → [t]
      t₂  [t]   voiceless dental ← . → [ɑ]
      a   [ɑ]   short open       ← [t] → [m]
      m₁  [m]   bilabial nasal   ← [ɑ] → [ɑ]
      a   [ɑ]   short open       ← [m] → [m]
      m₂  [m]   bilabial nasal   ← [ɑ] → . (word-final, release tail)
    """
    segs = [
        # RAT-
        synth_R(F_prev=None, F_next=VS_A_F,
                pitch_hz=pitch_hz, dil=dil),
        synth_A(F_prev=VS_R_F, F_next=VS_T_LOCUS_F,
                pitch_hz=pitch_hz, dil=dil),
        synth_T(F_next=VS_N_F,
                pitch_hz=pitch_hz, dil=dil),

        # -NA-
        synth_N(F_prev=VS_T_LOCUS_F, F_next=VS_A_F,
                pitch_hz=pitch_hz, dil=dil),
        synth_A(F_prev=VS_N_F, F_next=None,
                pitch_hz=pitch_hz, dil=dil),

        # -DHĀ-
        synth_DH(F_prev=VS_A_F, F_next=VS_AA_F,
                 pitch_hz=pitch_hz, dil=dil),
        synth_AA(F_prev=None, F_next=VS_T_LOCUS_F,
                 pitch_hz=pitch_hz, dil=dil),

        # -TA-
        synth_T(F_next=VS_A_F,
                pitch_hz=pitch_hz, dil=dil),
        synth_A(F_prev=VS_T_LOCUS_F, F_next=VS_M_F,
                pitch_hz=pitch_hz, dil=dil),

        # -MAM
        synth_M(F_prev=VS_A_F, F_next=VS_A_F,
                pitch_hz=pitch_hz, dil=dil,
                word_final=False),
        synth_A(F_prev=VS_M_F, F_next=VS_M_F,
                pitch_hz=pitch_hz, dil=dil),
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
    print("RATNADHĀTAMAM v16 — UNIFIED SOURCE ARCHITECTURE")
    print("=" * 70)
    print()
    print("v15→v16 CHANGES:")
    print()
    print("  [t] UNIFIED SOURCE ARCHITECTURE:")
    print("    ONE continuous noise buffer (the breath)")
    print("    ONE continuous amplitude envelope (the tongue)")
    print("    NO array concatenation boundaries")
    print("    Subglottal floor: 0.001 (~-60dB) — never digital zero")
    print("    Pre-burst crescendo rides on subglottal floor")
    print("    Spike ADDED to continuous noise (not concatenated)")
    print("    Dental locus formants applied to entire buffer")
    print()
    print("    The breath is continuous. The tongue is the envelope.")
    print("    Same principle as DEVAM [d] v13 crossfade:")
    print("    one source, shaped continuously, no boundaries.")
    print()
    print("  All other phonemes unchanged from v15.")
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

    write_wav("output_play/ratnadhatamam_v16_dry.wav", word_dry)
    write_wav("output_play/ratnadhatamam_v16_slow6x.wav", word_slow)
    write_wav("output_play/ratnadhatamam_v16_slow12x.wav", word_slow12)
    write_wav("output_play/ratnadhatamam_v16_hall.wav", word_hall)
    write_wav("output_play/ratnadhatamam_v16_perf.wav", word_perf)
    write_wav("output_play/ratnadhatamam_v16_perf_hall.wav", word_perf_hall)

    # Isolated phonemes for diagnostic
    dh_iso = synth_DH(F_prev=VS_A_F, F_next=VS_AA_F)
    t1_iso = synth_T(F_next=VS_N_F)
    t2_iso = synth_T(F_next=VS_A_F)
    m_final_iso = synth_M(F_prev=VS_A_F, word_final=True)

    for sig, name in [
        (dh_iso, "ratnadhatamam_v16_dh_iso"),
        (t1_iso, "ratnadhatamam_v16_t1_iso"),
        (t2_iso, "ratnadhatamam_v16_t2_iso"),
        (m_final_iso, "ratnadhatamam_v16_m_final_iso"),
    ]:
        mx = np.max(np.abs(sig))
        if mx > 1e-8:
            sig = sig / mx * 0.75
        write_wav(f"output_play/{name}.wav", sig)
        write_wav(f"output_play/{name}_slow6x.wav", ola_stretch(sig, 6.0))
        write_wav(f"output_play/{name}_slow12x.wav", ola_stretch(sig, 12.0))

    print()
    print("=" * 70)
    print("v16 synthesis complete.")
    print()
    print("LISTEN:")
    print("  afplay output_play/ratnadhatamam_v16_t1_iso_slow6x.wav")
    print("  afplay output_play/ratnadhatamam_v16_t1_iso_slow12x.wav")
    print("  afplay output_play/ratnadhatamam_v16_t2_iso_slow6x.wav")
    print("  afplay output_play/ratnadhatamam_v16_slow6x.wav")
    print("  afplay output_play/ratnadhatamam_v16_perf_hall.wav")
    print()
    print("LISTEN FOR:")
    print("  [t] — THE CLICK SHOULD BE GONE.")
    print("        No concatenation boundaries exist.")
    print("        The burst emerges from the continuous noise floor.")
    print("        Compare v16_t1_iso vs v15_t1_iso at 12x slow.")
    print()
    print("  If the [t] is too quiet or too noisy:")
    print("    VS_T_BURST_GAIN controls burst loudness (currently 0.15)")
    print("    VS_T_SUBGLOTTAL_FLOOR controls closure noise (currently 0.001)")
    print("    VS_T_PREBURST_AMP controls leak crescendo peak (currently 0.008)")
    print()
    print("  The architecture is now correct. Only tuning remains.")
    print("=" * 70)
    print()
