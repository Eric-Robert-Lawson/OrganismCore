"""
================================================================
AGNI v5 — Principles-First Reconstruction
Rigveda 1.1.1, word 1
[ɑgni] — "O fire"

ARCHITECTURE:
  ALL VOICED — no pluck, no closing tail / opening head.
  Voiced stops are NOT plucks (Pluck Artifact Part VI).

  [g] uses crossfade cutback architecture (from DEVAM v13):
    v1 BROKEN architecture:
      LP-filtered murmur / random noise burst / independent VOT
      Three independent sources. Two phase resets.
      The burst is np.random.randn() — stochastic noise
      spliced between periodic signals. Click artifact.
      This is the architecture DEVAM proved wrong in v1-v4.

    v5 CORRECT architecture:
      ONE continuous Rosenberg source for entire [g].
      Phase 1: Voice bar — source through low resonator (200 Hz)
      Phase 2: Burst — source through burst-locus formants + transient
      Phase 3: Cutback — equal-power crossfade closed→open tract
      Continuous voicing. No phase resets. One instrument.

  v5 FIXES (cumulative):
    v2: crossfade cutback replaces noise burst
    v3: word-boundary laryngeal onset/offset envelopes
    v4: amplitude hierarchy ([g] 0.45 vs vowels 0.70-0.72)
    v5: continuous voicing source through all [g] phases

  [ɑ] short open back unrounded — kaṇṭhya (VERIFIED)
  [n] voiced alveolar nasal — dantya (VERIFIED)
  [i] short close front unrounded — tālavya (VERIFIED)

  Coarticulation: each vowel/sonorant receives F_prev/F_next
  for formant blending at boundaries.

  Infrastructure: canonical from HOTĀRAM v9
    - rosenberg_pulse: differentiated Rosenberg glottal source
    - apply_formants: parallel IIR resonators, b = [1.0 - r]
    - iir_notch: antiformant for nasals
    - norm_to_peak: amplitude normalization
    - Word-level norm_to_peak(0.75)

  ARTIFACT REVIEW:
    Pluck Artifact:           NOT APPLICABLE — all voiced
    Observer Position:        NOT APPLICABLE — no voiceless segments
    Origin Artifact:          NOT APPLICABLE — no [h]
    Crossfade Cutback (v13): APPLIED — [g] canonical

  Ancestors:
    AGNI v1 (phoneme parameters, infrastructure)
    DEVAM v1 (crossfade cutback architecture for voiced stops)
    HOTĀRAM v9 (canonical infrastructure)
    ṚG (original [g] verification)

  PERFORMANCE:
    dil=1.0  — diagnostic speed (measurement)
    dil=2.5  — performance speed (listening)
    OLA 6×   — standard slow analysis
    OLA 12×  — deep slow analysis

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


# ── PHYSICS CONSTANTS ─────────────────────────────────

NEUTRAL_ALVEOLAR_F3_HZ = 2700.0
# F3 of an unconstricted alveolar vocal tract.
# Calculated from tube acoustics.
# Language-independent physics constant.

# Laryngeal offset: the glottis closes gradually
# at end of phonation. ~15-25ms for the vocal folds
# to stop vibrating. Models the natural decay of
# voicing at word boundary.
WORD_FINAL_FADE_MS = 20.0


# ── ŚIKṢĀ REFERENCES — VS-internal ───────────────────

KANTHHYA_BURST_LO_HZ   = 1800.0
KANTHHYA_BURST_HI_HZ   = 3200.0
# Kaṇṭhya (velar) burst locus range.
# Confirmed in ṚG: burst centroid 2577 Hz.

DANTYA_ANTI_F_HZ       = 800.0
# Dantya (dental/alveolar) nasal antiresonance.
# Alveolar nasal zero ~800 Hz.

TALAVYA_F2_LO_HZ       = 1900.0
TALAVYA_F2_HI_HZ       = 2500.0
# Tālavya (palatal) F2 range.


# ── PHONEME PARAMETERS ────────────────────────────────

# [ɑ] — short open back unrounded — अ
# Śikṣā: kaṇṭhya
# Maximally open vocal tract.
# High F1 — wide jaw opening.
# Mid-back F2 — tongue body retracted.
# The phonological default of Sanskrit.
VS_A_F      = [700.0, 1100.0, 2550.0, 3400.0]
VS_A_B      = [130.0,  160.0,  220.0,  280.0]
VS_A_GAINS  = [ 16.0,    6.0,    1.5,    0.5]
VS_A_DUR_MS = 55.0
VS_A_COART_ON  = 0.12
VS_A_COART_OFF = 0.12

# [g] — voiced velar stop — ग
# Śikṣā: kaṇṭhya
# v5: continuous voicing, crossfade cutback.
#
# TONGUE TOPOLOGY:
#   The tongue body is the largest oral articulator.
#   When it presses against the velum, the cavity
#   BEHIND the constriction (pharynx + larynx) is
#   at its maximum length. This means:
#     - Voice bar resonance is low (~200 Hz)
#     - Burst centroid is mid-range (~2500 Hz)
#     - Burst is inherently diffuse (large release area)
#     - Release is slow (large mass, large area)
#
# AMPLITUDE HIERARCHY (v4):
#   The tongue body seals against the velum.
#   The oral tract is CLOSED. Sound must radiate
#   through the flesh of the throat and cheeks.
#   This attenuates by 20-30 dB relative to
#   open-tract vowel radiation.
#
#   Hierarchy:
#     [ɑ] open vowel:     0.72  (full tract resonance)
#     [i] close vowel:    0.70  (full tract resonance)
#     [n] nasal:          0.60  (nasal bypass — reduced)
#     [g] cutback end:    ~0.55 (opening toward vowel)
#     [g] cutback start:  ~0.20 (still mostly closed)
#     [g] burst:          0.08  (brief transient)
#     [g] voice bar:      0.12  (sealed tract — very quiet)
#
VS_G_CLOSURE_MS   = 30.0       # voice bar duration
VS_G_BURST_MS     = 10.0       # velar burst — longer than dental (8ms)
                                # because tongue body releases slowly
VS_G_CUTBACK_MS   = 25.0       # crossfade: closed → open tract

VS_G_VOICEBAR_F   = 200.0      # voice bar: lower than dental (250)
                                # because velar back cavity is longest
VS_G_VOICEBAR_BW  = 100.0      # wider BW than dental — more damped
VS_G_VOICEBAR_G   = 10.0
VS_G_MURMUR_PEAK  = 0.12       # sealed tract — very quiet

VS_G_BURST_PEAK   = 0.08       # lower than dental (0.15) —
                                # large tongue body, less pressure
VS_G_BURST_F      = [1200.0, 2500.0, 3800.0, 5000.0]
                                # velar burst formants — lower centroid
VS_G_BURST_B      = [ 500.0,  700.0,  900.0, 1100.0]
                                # wider bandwidths — more diffuse
VS_G_BURST_G      = [   3.0,   10.0,    4.0,    1.0]
                                # F2 region dominant (velar locus ~2500)
VS_G_BURST_DECAY  = 120.0      # slower decay than dental (170)

# Closed tract voicing during cutback
VS_G_CLOSED_F     = [200.0,  700.0, 2000.0, 3000.0]
VS_G_CLOSED_B     = [150.0,  250.0,  350.0,  400.0]
VS_G_CLOSED_G     = [  8.0,    2.5,    0.6,    0.2]
VS_G_CLOSED_PEAK  = 0.20       # closed tract quiet
VS_G_OPEN_PEAK    = 0.55       # below vowel level
VS_G_CUTBACK_PEAK = 0.40       # average of transition
VS_G_FINAL_NORM   = 0.45       # well below vowels

# [n] — voiced alveolar nasal — न
# Śikṣā: dantya
# First VS nasal.
# Sustained voiced murmur.
# Antiresonance (zero) at ~800 Hz —
# the nasal side branch absorbs
# energy at this frequency.
VS_N_F       = [250.0,  900.0, 2000.0, 3000.0]
VS_N_B       = [100.0,  200.0,  300.0,  350.0]
VS_N_GAINS   = [  8.0,    2.5,    0.5,    0.2]
VS_N_DUR_MS  = 60.0
VS_N_ANTI_F  = 800.0
VS_N_ANTI_BW = 200.0
VS_N_COART_ON  = 0.15
VS_N_COART_OFF = 0.15

# [i] — short close front unrounded — इ
# Śikṣā: tālavya
# Close jaw — low F1.
# Tongue body raised to hard palate —
# high F2. Front corner of vowel triangle.
VS_I_F      = [280.0, 2200.0, 2900.0, 3400.0]
VS_I_B      = [ 80.0,  130.0,  180.0,  250.0]
VS_I_GAINS  = [ 12.0,    8.0,    1.5,    0.5]
VS_I_DUR_MS = 50.0
VS_I_COART_ON  = 0.12
VS_I_COART_OFF = 0.12

PITCH_HZ = 120.0
DIL      = 1.0

VS_G_TOTAL_MS = VS_G_CLOSURE_MS + VS_G_BURST_MS + VS_G_CUTBACK_MS


# ── UTILITIES ─────────────────────────────────────────

def f32(x):
    return np.asarray(x, dtype=DTYPE)

def rms(sig):
    return float(np.sqrt(
        np.mean(sig.astype(float) ** 2)))

def write_wav(path, sig, sr=SR):
    sig_i = (np.clip(f32(sig),
                     -1.0, 1.0) * 32767
             ).astype(np.int16)
    with wave_module.open(path, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(sig_i.tobytes())
    print(f"  Wrote {path}")

def safe_bp(lo, hi, sr=SR):
    nyq = sr / 2.0
    lo  = max(lo, 20.0)
    hi  = min(hi, nyq - 20.0)
    if lo >= hi:
        return None, None
    return butter(2, [lo / nyq, hi / nyq],
                  btype='band')

def safe_lp(fc, sr=SR):
    nyq = sr / 2.0
    fc  = min(fc, nyq - 20.0)
    return butter(2, fc / nyq, btype='low')

def ola_stretch(sig, factor=6.0, sr=SR):
    """OLA time-stretch. VS standard: 6× analysis, 12× deep."""
    win_ms  = 40.0
    win_n   = int(win_ms / 1000.0 * sr)
    if win_n % 2 == 1:
        win_n += 1
    hop_in  = win_n // 4
    hop_out = int(hop_in * factor)
    window  = np.hanning(win_n).astype(DTYPE)
    n_in    = len(sig)
    n_frames = max(1,
                   (n_in - win_n) // hop_in + 1)
    n_out   = hop_out * n_frames + win_n
    out     = np.zeros(n_out, dtype=DTYPE)
    norm    = np.zeros(n_out, dtype=DTYPE)
    for i in range(n_frames):
        in_pos  = i * hop_in
        out_pos = i * hop_out
        if in_pos + win_n > n_in:
            break
        frame = (sig[in_pos:in_pos + win_n]
                 * window)
        out [out_pos:out_pos + win_n] += frame
        norm[out_pos:out_pos + win_n] += window
    nz       = norm > 1e-8
    out[nz] /= norm[nz]
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.75
    return f32(out)

def rosenberg_pulse(n_samples, pitch_hz,
                    oq=0.65, sr=SR):
    """Differentiated Rosenberg glottal pulse train."""
    period = int(sr / pitch_hz)
    if period < 1:
        period = 1
    pulse  = np.zeros(period, dtype=float)
    t1     = int(period * oq * 0.6)
    t2     = int(period * oq)
    for i in range(t1):
        pulse[i] = (0.5 * (1.0
                    - np.cos(np.pi * i / t1)))
    for i in range(t1, t2):
        pulse[i] = np.cos(
            np.pi * (i - t1) /
            (2.0 * (t2 - t1)))
    d_pulse  = np.diff(pulse,
                       prepend=pulse[0])
    n_reps   = (n_samples // period) + 2
    repeated = np.tile(d_pulse, n_reps)
    return f32(repeated[:n_samples])

def apply_formants(src, freqs, bws, gains,
                   sr=SR):
    """Parallel IIR resonator bank — canonical from HOTĀRAM v9."""
    out = np.zeros(len(src), dtype=float)
    nyq = sr / 2.0
    for f, bw, g in zip(freqs, bws, gains):
        if f > 0 and f < nyq:
            r    = np.exp(-np.pi * bw / sr)
            cosf = 2.0 * np.cos(
                2.0 * np.pi * f / sr)
            a    = [1.0, -r * cosf, r * r]
            b_   = [1.0 - r]
            res  = lfilter(b_, a,
                           src.astype(float))
            out += res * g
    return f32(out)

def iir_notch(sig, fc, bw=200.0, sr=SR):
    """IIR notch filter — antiformant for nasals."""
    nyq  = sr / 2.0
    fc   = min(max(fc, 20.0), nyq - 20.0)
    w0   = 2.0 * np.pi * fc / sr
    r    = 1.0 - np.pi * bw / sr
    r    = np.clip(r, 0.0, 0.999)
    b_n  = [1.0, -2.0 * np.cos(w0), 1.0]
    a_n  = [1.0,
            -2.0 * r * np.cos(w0),
            r * r]
    return f32(lfilter(b_n, a_n,
                       sig.astype(float)))

def norm_to_peak(sig, target_peak):
    """Normalize signal to target peak amplitude."""
    mx = np.max(np.abs(sig))
    if mx > 1e-12:
        return f32(sig * (target_peak / mx))
    return f32(sig)

def apply_vowel_envelope(sig, word_initial=False,
                         word_final=False,
                         fade_ms=WORD_FINAL_FADE_MS,
                         sr=SR):
    """
    Laryngeal onset/offset envelope for vowels.

    Physics:
      Word-initial: glottis opens gradually (~20ms).
        Vocal folds begin vibrating from rest.
      Word-final: glottis closes gradually (~20ms).
        Vocal folds stop vibrating.
      Word-medial: no envelope (voicing continuous).

    This is NOT a closing tail (that's for
    vowel→voiceless transitions in the Pluck
    architecture). This is the laryngeal
    onset/offset gesture.
    """
    n = len(sig)
    env = np.ones(n, dtype=float)
    fade_n = int(fade_ms / 1000.0 * sr)
    fade_n = min(fade_n, n // 3)

    if word_initial and fade_n > 0:
        env[:fade_n] = np.linspace(
            0.0, 1.0, fade_n)

    if word_final and fade_n > 0:
        env[-fade_n:] = np.linspace(
            1.0, 0.0, fade_n)

    return f32(sig * env)


# ── PHONEME SYNTHESISERS ──────────────────────────────

def synth_A(F_prev=None, F_next=None,
            pitch_hz=PITCH_HZ,
            dil=DIL,
            word_initial=False,
            word_final=False,
            sr=SR):
    """
    [ɑ] — short open back unrounded.
    Śikṣā: kaṇṭhya.
    Maximally open vocal tract.
    """
    n_ms  = VS_A_DUR_MS * dil
    n     = int(n_ms / 1000.0 * sr)
    src   = rosenberg_pulse(n, pitch_hz,
                            oq=0.65, sr=sr)

    f_mean = list(VS_A_F)
    if F_prev is not None:
        for k in range(min(len(F_prev),
                           len(VS_A_F))):
            f_mean[k] = (F_prev[k] * VS_A_COART_ON
                         + VS_A_F[k] * (1.0 - VS_A_COART_ON))
    if F_next is not None:
        for k in range(min(len(F_next),
                           len(VS_A_F))):
            f_mean[k] = (f_mean[k] * (1.0 - VS_A_COART_OFF)
                         + F_next[k] * VS_A_COART_OFF)

    out = apply_formants(src, f_mean,
                         VS_A_B, VS_A_GAINS,
                         sr=sr)
    out = apply_vowel_envelope(
        out, word_initial=word_initial,
        word_final=word_final, sr=sr)
    mx  = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.72
    return f32(out)


def synth_G(F_prev=None, F_next=None,
            pitch_hz=PITCH_HZ,
            dil=DIL, sr=SR):
    """
    [g] — voiced velar stop — v5 continuous voicing
    crossfade cutback.
    Śikṣā: kaṇṭhya.

    v1 BROKEN: LP filter murmur + random noise burst + VOT.
    v5 CORRECT: one continuous Rosenberg source, three
    filter phases, crossfade cutback.

    ONE continuous glottal source for the entire [g].
    The vocal folds vibrate continuously through
    closure, burst, and cutback. The tongue moves.
    The larynx does not stop. One instrument.

    Phase 1 (closure):  source → voice bar filter (200 Hz)
    Phase 2 (burst):    source → burst-locus formants + transient
    Phase 3 (cutback):  source → crossfade closed→open filters

    The source is sliced from one continuous pulse train.
    No phase resets. No discontinuities.
    """
    n_closure = int(VS_G_CLOSURE_MS * dil / 1000.0 * sr)
    n_burst   = int(VS_G_BURST_MS * dil / 1000.0 * sr)
    n_cutback = int(VS_G_CUTBACK_MS * dil / 1000.0 * sr)
    n_total   = n_closure + n_burst + n_cutback

    f_next = F_next if F_next is not None else VS_N_F

    # ── ONE continuous glottal source ─────────────────
    src_all = rosenberg_pulse(
        n_total, pitch_hz, oq=0.65, sr=sr)

    # Slice the continuous source into phase windows
    src_closure = src_all[:n_closure]
    src_burst   = src_all[n_closure:n_closure + n_burst]
    src_cutback = src_all[n_closure + n_burst:]

    # ── Phase 1: Voice bar (closure) ──────────────────
    # Tongue body sealed against velum.
    # Only the voice bar resonance escapes (~200 Hz).
    # This is the quietest part of the word.
    if n_closure > 0:
        murmur = apply_formants(
            src_closure,
            [VS_G_VOICEBAR_F],
            [VS_G_VOICEBAR_BW],
            [VS_G_VOICEBAR_G],
            sr=sr)
        # Gentle onset ramp
        env_cl = np.ones(n_closure, dtype=float)
        ramp_n = max(1, int(0.2 * n_closure))
        env_cl[:ramp_n] = np.linspace(
            0.5, 1.0, ramp_n)
        murmur = f32(murmur * env_cl)
        closure = norm_to_peak(murmur,
                               VS_G_MURMUR_PEAK)
    else:
        closure = np.array([], dtype=DTYPE)

    # ── Phase 2: Burst (velar release) ────────────────
    # The tongue body begins to release.
    # The voicing is PRESENT during the burst —
    # this is a voiced stop. The burst rides ON TOP
    # of the continuous glottal oscillation.
    # The burst is SOFTER and MORE DIFFUSE than dental:
    #   - Large release area → less pressure buildup
    #   - Lower centroid (2500 Hz vs 3500 Hz)
    #   - Slower decay (cavity rings longer)
    if n_burst > 0:
        burst_n = max(n_burst, 16)

        # Voiced component: source through burst-locus filter
        voiced_burst = apply_formants(
            src_burst[:burst_n],
            VS_G_BURST_F, VS_G_BURST_B,
            VS_G_BURST_G, sr=sr)

        # Transient component: brief pressure release
        spike = np.zeros(burst_n, dtype=float)
        spike[0:4] = [0.6, 0.4, 0.2, 0.1]
        t_b = np.arange(burst_n) / sr
        spike_env = np.exp(-t_b * VS_G_BURST_DECAY)
        transient = f32(spike * spike_env)

        # Mix: voiced voicing + brief transient
        # The voicing is primary. The transient rides on it.
        burst_raw = (voiced_burst * 0.6
                     + transient * 0.4)
        burst = norm_to_peak(f32(burst_raw),
                             VS_G_BURST_PEAK)
    else:
        burst = np.array([], dtype=DTYPE)

    # ── Phase 3: Crossfade cutback ────────────────────
    # Equal-power crossfade: closed (quiet) → open (loud).
    # SAME continuous source, two different filters.
    # The amplitude RISES through this phase.
    if n_cutback > 0:
        closed = apply_formants(
            src_cutback, VS_G_CLOSED_F,
            VS_G_CLOSED_B, VS_G_CLOSED_G,
            sr=sr)
        closed = norm_to_peak(closed,
                              VS_G_CLOSED_PEAK)

        open_f = list(f_next)
        open_b = [130.0, 160.0, 220.0, 280.0]
        open_g = [14.0, 6.0, 1.5, 0.4]
        opened = apply_formants(
            src_cutback, open_f, open_b,
            open_g, sr=sr)
        opened = norm_to_peak(opened,
                              VS_G_OPEN_PEAK)

        # Equal-power crossfade: cos (closed → 0)
        #                        sin (open → 1)
        t_xf = np.linspace(0.0, np.pi / 2.0,
                           n_cutback)
        xf_out = (closed * np.cos(t_xf).astype(DTYPE)
                  + opened * np.sin(t_xf).astype(DTYPE))
        cutback = norm_to_peak(f32(xf_out),
                               VS_G_CUTBACK_PEAK)
    else:
        cutback = np.array([], dtype=DTYPE)

    out = np.concatenate([closure, burst, cutback])
    mx  = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * VS_G_FINAL_NORM
    return f32(out)


def synth_N(F_prev=None, F_next=None,
            pitch_hz=PITCH_HZ,
            dil=DIL, sr=SR):
    """
    [n] — voiced alveolar nasal.
    Śikṣā: dantya.
    First VS nasal.
    Sustained voiced murmur with
    antiresonance at ~800 Hz.
    """
    n_ms  = VS_N_DUR_MS * dil
    n     = int(n_ms / 1000.0 * sr)
    src   = rosenberg_pulse(n, pitch_hz,
                            oq=0.65, sr=sr)

    f_mean = list(VS_N_F)
    if F_prev is not None:
        for k in range(min(len(F_prev),
                           len(VS_N_F))):
            f_mean[k] = (F_prev[k] * VS_N_COART_ON
                         + VS_N_F[k] * (1.0 - VS_N_COART_ON))
    if F_next is not None:
        for k in range(min(len(F_next),
                           len(VS_N_F))):
            f_mean[k] = (f_mean[k] * (1.0 - VS_N_COART_OFF)
                         + F_next[k] * VS_N_COART_OFF)

    # Gentle onset/offset envelope
    env = np.ones(n, dtype=DTYPE)
    n_tr = min(int(0.020 * sr), n // 4)
    if n_tr > 0 and n_tr < n:
        env[:n_tr]  = np.linspace(
            0.3, 1.0, n_tr).astype(DTYPE)
        env[-n_tr:] = np.linspace(
            1.0, 0.3, n_tr).astype(DTYPE)
    src = f32(src * env)

    out = apply_formants(src, f_mean,
                         VS_N_B, VS_N_GAINS,
                         sr=sr)
    out = iir_notch(out, VS_N_ANTI_F,
                    VS_N_ANTI_BW, sr=sr)
    mx  = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.60
    return f32(out)


def synth_I(F_prev=None, F_next=None,
            pitch_hz=PITCH_HZ,
            dil=DIL,
            word_initial=False,
            word_final=False,
            sr=SR):
    """
    [i] — short close front unrounded.
    Śikṣā: tālavya.
    Close jaw, high F2.

    v3: word_final=True applies offset fade
    to prevent abrupt cutoff at end of word.
    """
    n_ms  = VS_I_DUR_MS * dil
    n     = int(n_ms / 1000.0 * sr)
    src   = rosenberg_pulse(n, pitch_hz,
                            oq=0.65, sr=sr)

    f_mean = list(VS_I_F)
    if F_prev is not None:
        for k in range(min(len(F_prev),
                           len(VS_I_F))):
            f_mean[k] = (F_prev[k] * VS_I_COART_ON
                         + VS_I_F[k] * (1.0 - VS_I_COART_ON))
    if F_next is not None:
        for k in range(min(len(F_next),
                           len(VS_I_F))):
            f_mean[k] = (f_mean[k] * (1.0 - VS_I_COART_OFF)
                         + F_next[k] * VS_I_COART_OFF)

    out = apply_formants(src, f_mean,
                         VS_I_B, VS_I_GAINS,
                         sr=sr)
    out = apply_vowel_envelope(
        out, word_initial=word_initial,
        word_final=word_final, sr=sr)
    mx  = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.70
    return f32(out)


# ── ROOM MODEL ────────────────────────────────────────

def apply_simple_room(sig, rt60=1.5,
                      direct_ratio=0.55,
                      sr=SR):
    """
    Schroeder reverb approximation.
    rt60 = 1.5 s — temple courtyard.
    VS default.
    """
    n_rev = int(rt60 * sr)
    ir    = np.zeros(n_rev, dtype=float)
    ir[0] = 1.0
    decay = np.exp(
        -6.908 * np.arange(n_rev) /
        (rt60 * sr))
    noise_ir = (np.random.randn(n_rev)
                * decay)
    ir       = (direct_ratio * ir
                + (1.0 - direct_ratio)
                * noise_ir)
    ir       = ir / (np.max(np.abs(ir))
                     + 1e-12)
    out = np.convolve(sig.astype(float),
                      ir[:min(n_rev, 4096)])
    out = out[:len(sig)]
    mx  = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.75
    return f32(out)


# ── WORD SYNTHESISER ──────────────────────────────────

def synth_agni(pitch_hz=PITCH_HZ,
               dil=DIL,
               with_room=False,
               sr=SR):
    """
    AGNI [ɑgni]
    Rigveda 1.1.1, word 1.
    "O fire."

    Syllable structure: AG — NI

    Coarticulation chain:
      A:  word-initial (onset fade), F_prev=None
          F_next=VS_G_CLOSED_F
      G:  F_prev=VS_A_F, F_next=VS_N_F
      N:  F_prev=VS_G_CLOSED_F, F_next=VS_I_F
      I:  F_prev=VS_N_F, word-final (offset fade)

    Amplitude hierarchy:
      [ɑ] 0.72  — vowel (loudest)
      [g] 0.45  — stop (quietest, continuous voicing)
      [n] 0.60  — nasal (medium)
      [i] 0.70  — vowel (with final fade)
    """
    a_seg = synth_A(F_prev=None,
                    F_next=VS_G_CLOSED_F,
                    pitch_hz=pitch_hz,
                    dil=dil,
                    word_initial=True,
                    word_final=False,
                    sr=sr)
    g_seg = synth_G(F_prev=VS_A_F,
                    F_next=VS_N_F,
                    pitch_hz=pitch_hz,
                    dil=dil, sr=sr)
    n_seg = synth_N(F_prev=VS_G_CLOSED_F,
                    F_next=VS_I_F,
                    pitch_hz=pitch_hz,
                    dil=dil, sr=sr)
    i_seg = synth_I(F_prev=VS_N_F,
                    F_next=None,
                    pitch_hz=pitch_hz,
                    dil=dil,
                    word_initial=False,
                    word_final=True,
                    sr=sr)

    word = np.concatenate(
        [a_seg, g_seg, n_seg, i_seg])

    mx = np.max(np.abs(word))
    if mx > 1e-8:
        word = word / mx * 0.75

    if with_room:
        word = apply_simple_room(
            word, rt60=1.5,
            direct_ratio=0.55, sr=sr)

    return f32(word)


# ── MAIN ──────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("  AGNI [ɑgni] v5")
    print("  Crossfade Cutback [g]")
    print("  Continuous Voicing Source")
    print("  Word Boundary Envelopes")
    print("  Amplitude Hierarchy")
    print("=" * 60)
    print()

    # ── Diagnostic speed (dil=1.0) ────────────────────
    print("  Diagnostic (dil=1.0):")
    dry = synth_agni(dil=1.0, with_room=False)
    write_wav("output_play/agni_dry.wav", dry)

    slow6  = ola_stretch(dry, factor=6.0)
    slow12 = ola_stretch(dry, factor=12.0)
    write_wav("output_play/agni_slow6x.wav",  slow6)
    write_wav("output_play/agni_slow12x.wav", slow12)

    dur_diag = len(dry) / SR * 1000.0
    print(f"    Duration: {dur_diag:.1f} ms")
    print()

    # ── Performance speed (dil=2.5) ───────────────────
    print("  Performance (dil=2.5):")
    perf_dry  = synth_agni(dil=2.5, with_room=False)
    perf_hall = synth_agni(dil=2.5, with_room=True)
    write_wav("output_play/agni_perf.wav",      perf_dry)
    write_wav("output_play/agni_perf_hall.wav",  perf_hall)

    perf_slow6  = ola_stretch(perf_dry, factor=6.0)
    perf_slow12 = ola_stretch(perf_dry, factor=12.0)
    write_wav("output_play/agni_perf_slow6x.wav",  perf_slow6)
    write_wav("output_play/agni_perf_slow12x.wav", perf_slow12)

    dur_perf = len(perf_dry) / SR * 1000.0
    print(f"    Duration: {dur_perf:.1f} ms")
    print()

    # ── Isolated phonemes (dil=1.0) ───────────────────
    print("  Isolated phonemes:")
    a_iso = synth_A(F_prev=None, F_next=None,
                    word_initial=True, word_final=True)
    g_iso = synth_G(F_prev=None, F_next=None)
    n_iso = synth_N(F_prev=None, F_next=None)
    i_iso = synth_I(F_prev=None, F_next=None,
                    word_initial=True, word_final=True)

    for sig, name in [
        (a_iso, "agni_a_isolated"),
        (g_iso, "agni_g_isolated"),
        (n_iso, "agni_n_isolated"),
        (i_iso, "agni_i_isolated"),
    ]:
        mx = np.max(np.abs(sig))
        if mx > 1e-8:
            sig = sig / mx * 0.75
        write_wav(
            f"output_play/{name}.wav", sig)
        write_wav(
            f"output_play/{name}_slow6x.wav",
            ola_stretch(sig, factor=6.0))
        write_wav(
            f"output_play/{name}_slow12x.wav",
            ola_stretch(sig, factor=12.0))

    # ── Summary ───────────────────────────────────────
    print()
    print("  " + "─" * 50)
    print(f"  Segments: [ɑ]={VS_A_DUR_MS}ms "
          f"[g]={VS_G_TOTAL_MS}ms "
          f"[n]={VS_N_DUR_MS}ms "
          f"[i]={VS_I_DUR_MS}ms")
    print(f"  Diagnostic (dil=1.0): {dur_diag:.1f} ms")
    print(f"  Performance (dil=2.5): {dur_perf:.1f} ms")
    print()
    print("  v5 architecture:")
    print("    [g] crossfade cutback (DEVAM v13 canonical)")
    print("    [g] ONE continuous Rosenberg source")
    print("    [g] voiced burst (source + transient)")
    print("    [g] amplitude 0.45 (vowels 0.70-0.72)")
    print("    [ɑ] word-initial onset fade (20ms)")
    print("    [i] word-final offset fade (20ms)")
    print("    OLA 6×/12× standard")
    print()
    print("  v1 bugs FIXED:")
    print("    ✗ LP filter murmur → ✓ voice bar resonator")
    print("    ✗ np.random.randn burst → ✓ voiced burst")
    print("    ✗ three independent sources → ✓ one continuous")
    print("    ✗ phase resets at boundaries → ✓ no resets")
    print("    ✗ [g] at 0.65 (too loud) → ✓ [g] at 0.45")
    print("    ✗ [i] abrupt cutoff → ✓ offset fade")
    print("    ✗ OLA 4× → ✓ OLA 6×/12×")
    print()
    print("  Run agni_diagnostic.py to verify.")
