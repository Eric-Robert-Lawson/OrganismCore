"""
PUROHITAM RECONSTRUCTION v1
Vedic Sanskrit: purohitam  [puroːhitɑm]
Rigveda 1.1.1 — word 3
February 2026

PHONEMES:
  [p]  voiceless bilabial stop         — NEW (oṣṭhya)
  [u]  short close back rounded        — NEW (oṣṭhya)
  [ɾ]  alveolar tap                    — NEW (antastha/dantya)
  [oː] long close-mid back rounded     — NEW (kaṇṭhya+oṣṭhya)
  [h]  voiceless glottal fricative     — NEW (kaṇṭhya)
  [i]  short close front unrounded     — VS-verified AGNI
  [t]  voiceless dental stop           — NEW (dantya)
  [ɑ]  short open central              — VS-verified AGNI
  [m]  voiced bilabial nasal           — NEW (oṣṭhya)

SYLLABLE STRUCTURE:
  PU — RO — HI — TAM
  [pu] — [ɾoː] — [hi] — [tɑm]

SYNTHESIS ENGINE: voice_physics_vs.py architecture.
VS-specific. No imports from any other
language reconstruction project.

ALL PARAMETERS derived from:
  1. Physics of the vocal tract
  2. Śikṣā treatise classification
  3. Vedic orthographic record
  4. Comparative Indo-European evidence
  5. Acoustic measurement of living
     cognate languages and reciters

ŚIKṢĀ CLASSIFICATION:
  [p]  — oṣṭhya (labial)
          Lip closure. Lowest burst locus
          of any stop class. ~1000–1200 Hz.
          Plain voiceless — no aspiration.
          Sanskrit distinguishes [p] from [pʰ].
          This is row 1 of the labial column.

  [u]  — oṣṭhya (labial)
          Lip rounding. Back close vowel.
          Low F1 (close jaw).
          Low F2 (back + rounded).
          Back corner of the vowel triangle.

  [ɾ]  — antastha (semivowel) / dantya adjacent
          Alveolar tap. Single ballistic contact.
          NOT a trill. NOT an approximant.
          Pāṇinīya Śikṣā: ya ra la va together —
          antastha class — standing in between.
          Taittirīya Prātiśākhya confirms.
          Living Vedic recitation: tap normative.
          Duration 20–40 ms. Single amplitude dip.
          F2 dantya locus ~1800–2000 Hz.
          F3 neutral — no retroflex curl.

  [oː] — kaṇṭhya + oṣṭhya (compound)
          Velar + labial. Mid back rounded.
          Sanskrit [o] is always long.
          No short counterpart.
          The back mirror of [eː].
          F1 between [u] and [ɑ].
          F2 low — back + rounded.

  [h]  — kaṇṭhya (glottal)
          Voiceless glottal fricative.
          H origin. C(h,H) ≈ 0.30.
          Closest phoneme to H in the
          coherence space after silence.
          Synthesised as broadband aspiration
          noise shaped by adjacent vowel
          formant context. No vocal fold
          vibration. The glottis is turbulent.
          The tract is open.

  [i]  — tālavya — VS-verified AGNI
  [t]  — dantya (dental)
          Tongue tip to upper teeth.
          Voiceless. No aspiration.
          Burst locus highest of the
          dental/alveolar class: ~3500 Hz.
          Plain dental — row 1 of dental column.

  [ɑ]  — kaṇṭhya — VS-verified AGNI
  [m]  — oṣṭhya (labial)
          Voiced bilabial nasal.
          Lip closure. Nasal side branch open.
          Antiresonance at ~800 Hz —
          same as [n] (both are coronals
          with nasal side branch opening
          at the same frequency class).
          F2 lower than [n] — bilabial
          nasal position pulls F2 down.

NEW ARCHITECTURE:
  [ɾ]: single Gaussian amplitude dip.
       NOT periodic AM (that is a trill).
       NOT sustained constriction (approximant).
       Rosenberg pulse through dantya formant
       bank with one amplitude envelope dip
       at the midpoint of the tap duration.
       Duration 30 ms. Dip depth 0.35.
       This is the antastha architecture.

  [h]: aspiration noise shaped by vowel context.
       Broadband noise filtered through
       formant bank of the preceding vowel [i].
       Voicing = 0. No Rosenberg source.
       The tract shape is the [i] configuration
       but the source is turbulent air,
       not vocal fold vibration.

  [p]: three-phase stop.
       Same architecture as [g] but at
       oṣṭhya locus — labial burst ~1100 Hz.
       Voiceless — no murmur in closure.
       Short VOT: 15–20 ms.

  [t]: three-phase stop.
       Dantya locus — burst ~3500 Hz.
       Voiceless. Short VOT: 15–20 ms.
       Highest burst centroid in the
       dantya/dental class.

  [m]: nasal murmur with antiresonance.
       Same iir_notch architecture as [n].
       Antiresonance at ~800 Hz.
       F2 lower than [n] — bilabial position.

COARTICULATION:
  [p]  → [u]:  labial burst releases into
               back rounded vowel.
               F2 rises from labial ~1100 Hz
               toward [u] ~750 Hz.
               (labial burst is above [u] F2 —
                F2 falls into [u])
  [u]  → [ɾ]:  back rounded vowel into tap.
               F2 rises from ~750 Hz toward
               dantya locus ~1900 Hz through tap.
  [ɾ]  → [oː]: tap releases into mid back vowel.
               F2 falls from dantya ~1900 Hz
               toward [oː] ~800 Hz.
  [oː] → [h]:  mid back vowel into glottal fric.
               [h] inherits formant context
               of adjacent vowel — here [i]
               follows, so [h] transitions
               toward [i] formants.
  [h]  → [i]:  aspiration releases into
               close front vowel.
               F2 rises from [oː]-context
               through [h] toward [i] 2200 Hz.
  [i]  → [t]:  close front vowel into
               dental closure.
               F2 falls from 2200 Hz toward
               dental locus ~3500 Hz through
               the closure transition.
  [t]  → [ɑ]:  dental burst releases into
               open central vowel.
               F2 falls from ~3500 Hz toward
               [ɑ] ~1100 Hz.
  [ɑ]  → [m]:  open central vowel into
               bilabial nasal.
               F2 falls from ~1100 Hz toward
               [m] nasal murmur position.

PERFORMANCE PARAMETERS:
  pitch_hz:     120.0  (Vedic recitation)
  dil:          1.0    (diagnostic)
  rt60:         1.5    (temple courtyard)
  direct_ratio: 0.55
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
# Language-independent tube acoustics constant.


# ── ŚIKṢĀ REFERENCES — VS-internal ───────────────────

OSTHHYA_BURST_LO_HZ   =  900.0
OSTHHYA_BURST_HI_HZ   = 1400.0
# Oṣṭhya (labial) burst locus.
# Lowest of all stop classes.
# Bilabial closure releases at low frequency
# because the oral cavity anterior to the
# closure is absent — lips are the front wall.

DANTYA_BURST_LO_HZ    = 3000.0
DANTYA_BURST_HI_HZ    = 4500.0
# Dantya (dental) burst locus.
# Tongue tip to upper teeth.
# High frequency — small anterior cavity.

DANTYA_TAP_F2_LO_HZ   = 1700.0
DANTYA_TAP_F2_HI_HZ   = 2200.0
# Antastha tap F2 locus — dantya adjacent.
# Single contact. Alveolar position.

NASAL_ANTI_F_HZ       =  800.0
# Both [n] (dantya) and [m] (oṣṭhya)
# have nasal side branch antiresonance
# in this range. Physics of the nasal
# cavity determines this, not lip position.


# ── VS-INTERNAL VERIFIED REFERENCES ──────────────────

VS_I_F2_HZ   = 2124.0   # AGNI verified
VS_I_F        = [280.0, 2200.0, 2900.0, 3400.0]
VS_A_F2_HZ   = 1106.0   # AGNI verified
VS_A_F        = [700.0, 1100.0, 2550.0, 3400.0]
VS_RV_F3_HZ  = 2355.0   # ṚG verified
VS_EE_F2_HZ  = 1659.0   # ĪḶE verified


# ── PHONEME PARAMETERS ────────────────────────────────

# [p] — voiceless bilabial stop — प
# Śikṣā: oṣṭhya
# Lip closure. No voicing during closure.
# Burst at labial locus — lowest burst
# frequency of any stop in the inventory.
VS_P_CLOSURE_MS = 28.0
VS_P_BURST_F    = 1100.0
VS_P_BURST_BW   = 800.0
VS_P_BURST_MS   = 8.0
VS_P_VOT_MS     = 18.0
VS_P_BURST_GAIN = 0.38

# [u] — short close back rounded — उ
# Śikṣā: oṣṭhya
# Low F1 (close jaw). Low F2 (back + rounded).
# Back corner of the vowel triangle.
VS_U_F      = [300.0,  750.0, 2300.0, 3100.0]
VS_U_B      = [ 90.0,  120.0,  200.0,  260.0]
VS_U_GAINS  = [ 14.0,    8.0,    1.5,    0.5]
VS_U_DUR_MS = 50.0
VS_U_COART_ON  = 0.12
VS_U_COART_OFF = 0.12

# [ɾ] — alveolar tap — antastha
# Pāṇinīya Śikṣā: antastha — semivowel class.
# Single ballistic tongue contact.
# NOT a trill (no periodic AM).
# NOT an approximant (too brief, has dip).
# Duration 30 ms. One amplitude dip.
# F2 dantya-adjacent locus ~1900 Hz.
# F3 neutral — no retroflex curl.
VS_R_F         = [300.0, 1900.0, 2700.0, 3300.0]
VS_R_B         = [120.0,  200.0,  250.0,  300.0]
VS_R_GAINS     = [ 12.0,    6.0,    1.5,    0.4]
VS_R_DUR_MS    = 30.0
VS_R_DIP_DEPTH = 0.35   # amplitude reduction at contact
VS_R_DIP_WIDTH = 0.40   # fraction of duration for dip

# [oː] — long close-mid back rounded — ओ
# Śikṣā: kaṇṭhya + oṣṭhya (compound)
# Sanskrit [o] is always long — no short [o].
# Mid back rounded. Between [u] and [ɑ].
# F1 between [u] (~300 Hz) and [ɑ] (~700 Hz).
# F2 low — back + rounded — above [u] F2.
VS_OO_F      = [430.0,  800.0, 2500.0, 3200.0]
VS_OO_B      = [110.0,  130.0,  200.0,  270.0]
VS_OO_GAINS  = [ 15.0,    8.0,    1.5,    0.5]
VS_OO_DUR_MS = 100.0
VS_OO_COART_ON  = 0.10
VS_OO_COART_OFF = 0.10

# [h] — voiceless glottal fricative — ह
# Śikṣā: kaṇṭhya (glottal)
# H origin. C(h,H) ≈ 0.30.
# No Rosenberg source — no vocal fold vibration.
# Broadband aspiration noise shaped by
# adjacent vowel formant context.
# Preceding context: [oː] → [h] → [i]
# The [h] transitions formant shape
# from [oː] toward [i] through its duration.
VS_H_DUR_MS    = 65.0
VS_H_NOISE_CF  = 3000.0   # shaped by vowel context
VS_H_NOISE_BW  = 4000.0   # broadband
VS_H_GAIN      = 0.22
VS_H_COART_ON  = 0.30     # longer coart — H is transparent
VS_H_COART_OFF = 0.30

# [t] — voiceless dental stop — त
# Śikṣā: dantya
# Tongue tip to upper teeth.
# Highest burst locus of dantya class.
# Voiceless — no murmur in closure.
# Plain dental — no aspiration.
VS_T_CLOSURE_MS = 25.0
VS_T_BURST_F    = 3500.0
VS_T_BURST_BW   = 1500.0
VS_T_BURST_MS   = 7.0
VS_T_VOT_MS     = 15.0
VS_T_BURST_GAIN = 0.38

# [m] — voiced bilabial nasal — म
# Śikṣā: oṣṭhya
# Lip closure sustained.
# Nasal side branch open — velum lowered.
# Antiresonance at ~800 Hz (nasal zero).
# F2 lower than [n] — bilabial position.
VS_M_F       = [250.0,  900.0, 2200.0, 3000.0]
VS_M_B       = [100.0,  200.0,  300.0,  350.0]
VS_M_GAINS   = [  8.0,    2.5,    0.5,    0.2]
VS_M_DUR_MS  = 60.0
VS_M_ANTI_F  = 800.0
VS_M_ANTI_BW = 200.0
VS_M_COART_ON  = 0.15
VS_M_COART_OFF = 0.15

PITCH_HZ = 120.0
DIL      = 1.0


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

def safe_hp(fc, sr=SR):
    nyq = sr / 2.0
    fc  = max(fc, 20.0)
    fc  = min(fc, nyq - 20.0)
    return butter(2, fc / nyq, btype='high')

def ola_stretch(sig, factor=4.0, sr=SR):
    win_ms   = 40.0
    win_n    = int(win_ms / 1000.0 * sr)
    if win_n % 2 == 1:
        win_n += 1
    hop_in   = win_n // 4
    hop_out  = int(hop_in * factor)
    window   = np.hanning(win_n).astype(DTYPE)
    n_in     = len(sig)
    n_frames = max(1,
                   (n_in - win_n) // hop_in + 1)
    n_out    = hop_out * n_frames + win_n
    out      = np.zeros(n_out, dtype=DTYPE)
    norm     = np.zeros(n_out, dtype=DTYPE)
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
    period = int(sr / pitch_hz)
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
    d_pulse  = np.diff(pulse, prepend=pulse[0])
    n_reps   = (n_samples // period) + 2
    repeated = np.tile(d_pulse, n_reps)
    return f32(repeated[:n_samples])

def apply_formants(src, freqs, bws, gains,
                   sr=SR):
    out = np.zeros(len(src), dtype=float)
    nyq = sr / 2.0
    for f0, bw, g in zip(freqs, bws, gains):
        if f0 <= 0 or f0 >= nyq:
            continue
        r    = np.exp(-np.pi * bw / sr)
        cosf = 2.0 * np.cos(
            2.0 * np.pi * f0 / sr)
        a    = [1.0, -r * cosf, r * r]
        b_   = [1.0 - r]
        res  = lfilter(b_, a,
                       src.astype(float))
        out += res * g
    return f32(out)

def iir_notch(sig, fc, bw=200.0, sr=SR):
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


# ── PHONEME SYNTHESISERS ──────────────────────────────

def synth_P(F_prev=None, F_next=None,
            dil=DIL, sr=SR):
    """
    [p] — voiceless bilabial stop.
    Śikṣā: oṣṭhya.
    Three phases: closure / burst / VOT.
    No Rosenberg source during closure —
    voiceless, no murmur.
    Burst at labial locus ~1100 Hz —
    lowest burst centroid in VS inventory.
    Short VOT: 18 ms.
    """
    n_closure = int(
        VS_P_CLOSURE_MS * dil / 1000.0 * sr)
    n_burst   = int(
        VS_P_BURST_MS   * dil / 1000.0 * sr)
    n_vot     = int(
        VS_P_VOT_MS     * dil / 1000.0 * sr)

    # Closure: silence
    silence = np.zeros(n_closure, dtype=DTYPE)

    # Burst: band-filtered noise at labial locus
    noise = np.random.randn(
        max(n_burst, 4)).astype(float)
    b_bp, a_bp = safe_bp(
        VS_P_BURST_F - VS_P_BURST_BW / 2,
        VS_P_BURST_F + VS_P_BURST_BW / 2,
        sr)
    if b_bp is not None:
        burst = lfilter(b_bp, a_bp, noise)
    else:
        burst = noise
    # Envelope burst
    if len(burst) > 1:
        env_b = np.hanning(len(burst))
        burst = burst * env_b
    burst = f32(burst * VS_P_BURST_GAIN)

    # VOT: voiced onset into following vowel
    if n_vot > 0:
        src_vot = rosenberg_pulse(
            n_vot, PITCH_HZ, sr=sr)
        f_vot   = (F_next if F_next is not None
                   else VS_U_F)
        vot_env = np.linspace(0.0, 1.0, n_vot)
        vot     = apply_formants(
            src_vot, f_vot,
            VS_U_B, VS_U_GAINS, sr=sr)
        vot     = f32(vot * vot_env * 0.12)
    else:
        vot = np.array([], dtype=DTYPE)

    out = np.concatenate([silence, burst, vot])
    mx  = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.55
    return f32(out)


def synth_U(F_prev=None, F_next=None,
            pitch_hz=PITCH_HZ,
            dil=DIL, sr=SR):
    """
    [u] — short close back rounded.
    Śikṣā: oṣṭhya.
    Low F1 (close jaw).
    Low F2 (back + rounded) ~750 Hz.
    Back corner of the VS vowel triangle.
    """
    n_ms  = VS_U_DUR_MS * dil
    n     = int(n_ms / 1000.0 * sr)
    src   = rosenberg_pulse(n, pitch_hz,
                            oq=0.65, sr=sr)
    on_n  = int(VS_U_COART_ON * n)
    off_n = int(VS_U_COART_OFF * n)

    f_mean = list(VS_U_F)
    if F_prev is not None and on_n > 0:
        for k in range(min(len(F_prev),
                           len(VS_U_F))):
            f_mean[k] = (F_prev[k] * 0.12
                         + VS_U_F[k] * 0.88)
    if F_next is not None and off_n > 0:
        for k in range(min(len(F_next),
                           len(VS_U_F))):
            f_mean[k] = (f_mean[k] * 0.88
                         + F_next[k] * 0.12)

    out = apply_formants(src, f_mean,
                         VS_U_B, VS_U_GAINS,
                         sr=sr)
    mx  = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.68
    return f32(out)


def synth_R(F_prev=None, F_next=None,
            pitch_hz=PITCH_HZ,
            dil=DIL, sr=SR):
    """
    [ɾ] — alveolar tap.
    Śikṣā: antastha (semivowel).
    Pāṇinīya Śikṣā: ya ra la va — standing
    in between vowel and consonant.
    Taittirīya Prātiśākhya: confirms.
    Living Vedic recitation: tap normative.

    Architecture: Rosenberg pulse through
    dantya formant bank with single Gaussian
    amplitude dip at midpoint.

    The dip models the single ballistic
    tongue contact — not closure, not
    sustained constriction, one touch.
    One departure from H. One return.
    The antastha enacts departure and
    return within a single gesture.

    NOT periodic AM (trill).
    NOT sustained constriction (approximant).
    """
    n_ms = VS_R_DUR_MS * dil
    n    = max(4, int(n_ms / 1000.0 * sr))
    src  = rosenberg_pulse(n, pitch_hz,
                           oq=0.65, sr=sr)

    # Coarticulation — interpolate through tap
    f_mean = list(VS_R_F)
    if F_prev is not None:
        for k in range(min(len(F_prev),
                           len(VS_R_F))):
            f_mean[k] = (F_prev[k] * 0.20
                         + VS_R_F[k] * 0.80)
    if F_next is not None:
        for k in range(min(len(F_next),
                           len(VS_R_F))):
            f_mean[k] = (f_mean[k] * 0.80
                         + F_next[k] * 0.20)

    out = apply_formants(src, f_mean,
                         VS_R_B, VS_R_GAINS,
                         sr=sr)

    # Single Gaussian amplitude dip — the tap
    t      = np.linspace(0.0, 1.0, n)
    center = 0.50
    width  = VS_R_DIP_WIDTH * 0.5
    dip    = (1.0 - VS_R_DIP_DEPTH
              * np.exp(-((t - center) ** 2)
                       / (2.0 * width ** 2)))
    out    = f32(out * dip.astype(DTYPE))

    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.62
    return f32(out)


def synth_OO(F_prev=None, F_next=None,
             pitch_hz=PITCH_HZ,
             dil=DIL, sr=SR):
    """
    [oː] — long close-mid back rounded.
    Śikṣā: kaṇṭhya + oṣṭhya (compound).
    Sanskrit [o] is always long — no short [o].
    The back mirror of verified [eː].
    F1 between [u] and [ɑ].
    F2 low — back + rounded.
    """
    n_ms  = VS_OO_DUR_MS * dil
    n     = int(n_ms / 1000.0 * sr)
    src   = rosenberg_pulse(n, pitch_hz,
                            oq=0.65, sr=sr)
    on_n  = int(VS_OO_COART_ON * n)
    off_n = int(VS_OO_COART_OFF * n)

    f_mean = list(VS_OO_F)
    if F_prev is not None and on_n > 0:
        for k in range(min(len(F_prev),
                           len(VS_OO_F))):
            f_mean[k] = (F_prev[k] * 0.10
                         + VS_OO_F[k] * 0.90)
    if F_next is not None and off_n > 0:
        for k in range(min(len(F_next),
                           len(VS_OO_F))):
            f_mean[k] = (f_mean[k] * 0.90
                         + F_next[k] * 0.10)

    out = apply_formants(src, f_mean,
                         VS_OO_B, VS_OO_GAINS,
                         sr=sr)
    mx  = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.70
    return f32(out)


def synth_H(F_prev=None, F_next=None,
            dil=DIL, sr=SR):
    """
    [h] — voiceless glottal fricative.
    Śikṣā: kaṇṭhya (glottal).
    H origin. C(h,H) ≈ 0.30.
    No vocal fold vibration.
    Broadband aspiration noise shaped
    by the vowel context formants.
    The tract is in [i] configuration
    (following vowel context dominant).
    No Rosenberg source.
    """
    n_ms  = VS_H_DUR_MS * dil
    n     = int(n_ms / 1000.0 * sr)

    # Broadband noise source
    noise = np.random.randn(n).astype(float)

    # Shape by interpolation between
    # preceding and following vowel context
    # H is acoustically transparent —
    # it takes on the colour of its
    # vowel environment. Here [oː]→[h]→[i].
    f_on  = (F_prev if F_prev is not None
             else VS_OO_F)
    f_off = (F_next if F_next is not None
             else VS_I_F)

    on_n  = int(VS_H_COART_ON  * n)
    off_n = int(VS_H_COART_OFF * n)

    # Build smoothly varying formant array
    result = np.zeros(n, dtype=float)
    for fi in range(4):
        f_start = (float(f_on[fi])
                   if fi < len(f_on)
                   else 2500.0)
        f_end   = (float(f_off[fi])
                   if fi < len(f_off)
                   else 2500.0)
        bw      = 400.0
        g       = [1.5, 1.0, 0.5, 0.3][fi]
        f_arr   = np.linspace(f_start,
                               f_end, n)
        T       = 1.0 / sr
        y1 = y2 = 0.0
        out_fi  = np.zeros(n, dtype=float)
        for i in range(n):
            fc  = max(20.0,
                      min(sr * 0.48,
                          float(f_arr[i])))
            a2_ = -np.exp(-2*np.pi*bw*T)
            a1_ =  2*np.exp(-np.pi*bw*T) \
                   * np.cos(2*np.pi*fc*T)
            b0_ = 1.0 - a1_ - a2_
            yy  = (b0_ * noise[i]
                   + a1_ * y1 + a2_ * y2)
            y2  = y1
            y1  = yy
            out_fi[i] = yy
        result += out_fi * g

    # Amplitude envelope
    atk = min(int(0.015 * sr), n // 4)
    rel = min(int(0.020 * sr), n // 4)
    env = np.ones(n, dtype=float)
    if atk > 0:
        env[:atk] = np.linspace(0.0, 1.0, atk)
    if rel > 0:
        env[-rel:] = np.linspace(1.0, 0.0, rel)
    result = result * env * VS_H_GAIN

    mx = np.max(np.abs(result))
    if mx > 1e-8:
        result = result / mx * 0.38
    return f32(result)


def synth_I_vs(F_prev=None, F_next=None,
               pitch_hz=PITCH_HZ,
               dil=DIL, sr=SR):
    """
    [i] — VS-verified AGNI.
    Direct synthesis — same parameters.
    """
    I_F     = [280.0, 2200.0, 2900.0, 3400.0]
    I_B     = [ 80.0,  130.0,  180.0,  250.0]
    I_GAINS = [ 12.0,    8.0,    1.5,    0.5]
    DUR_MS  = 50.0
    COART   = 0.12

    n_ms  = DUR_MS * dil
    n     = int(n_ms / 1000.0 * sr)
    src   = rosenberg_pulse(n, pitch_hz,
                            oq=0.65, sr=sr)
    on_n  = int(COART * n)
    off_n = int(COART * n)

    f_mean = list(I_F)
    if F_prev is not None and on_n > 0:
        for k in range(min(len(F_prev),
                           len(I_F))):
            f_mean[k] = (F_prev[k] * 0.12
                         + I_F[k] * 0.88)
    if F_next is not None and off_n > 0:
        for k in range(min(len(F_next),
                           len(I_F))):
            f_mean[k] = (f_mean[k] * 0.88
                         + F_next[k] * 0.12)

    out = apply_formants(src, f_mean,
                         I_B, I_GAINS, sr=sr)
    mx  = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.70
    return f32(out)


def synth_T(F_prev=None, F_next=None,
            dil=DIL, sr=SR):
    """
    [t] — voiceless dental stop.
    Śikṣā: dantya.
    Tongue tip to upper teeth.
    Voiceless — silence during closure.
    Burst at dantya locus ~3500 Hz —
    highest burst centroid in VS inventory.
    Short VOT: 15 ms.
    """
    n_closure = int(
        VS_T_CLOSURE_MS * dil / 1000.0 * sr)
    n_burst   = int(
        VS_T_BURST_MS   * dil / 1000.0 * sr)
    n_vot     = int(
        VS_T_VOT_MS     * dil / 1000.0 * sr)

    silence = np.zeros(n_closure, dtype=DTYPE)

    noise = np.random.randn(
        max(n_burst, 4)).astype(float)
    b_bp, a_bp = safe_bp(
        VS_T_BURST_F - VS_T_BURST_BW / 2,
        VS_T_BURST_F + VS_T_BURST_BW / 2,
        sr)
    if b_bp is not None:
        burst = lfilter(b_bp, a_bp, noise)
    else:
        burst = noise
    if len(burst) > 1:
        env_b = np.hanning(len(burst))
        burst = burst * env_b
    burst = f32(burst * VS_T_BURST_GAIN)

    if n_vot > 0:
        src_vot = rosenberg_pulse(
            n_vot, PITCH_HZ, sr=sr)
        f_vot   = (F_next if F_next is not None
                   else VS_A_F)
        vot_env = np.linspace(0.0, 1.0, n_vot)
        vot     = apply_formants(
            src_vot, f_vot,
            [130.0, 150.0, 200.0, 280.0],
            [16.0, 8.0, 1.5, 0.5], sr=sr)
        vot     = f32(vot * vot_env * 0.10)
    else:
        vot = np.array([], dtype=DTYPE)

    out = np.concatenate([silence, burst, vot])
    mx  = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.52
    return f32(out)


def synth_A_vs(F_prev=None, F_next=None,
               pitch_hz=PITCH_HZ,
               dil=DIL, sr=SR):
    """
    [ɑ] — VS-verified AGNI.
    Direct synthesis — same parameters.
    """
    A_F     = [700.0, 1100.0, 2550.0, 3400.0]
    A_B     = [130.0,  160.0,  220.0,  280.0]
    A_GAINS = [ 16.0,    6.0,    1.5,    0.5]
    DUR_MS  = 55.0
    COART   = 0.12

    n_ms  = DUR_MS * dil
    n     = int(n_ms / 1000.0 * sr)
    src   = rosenberg_pulse(n, pitch_hz,
                            oq=0.65, sr=sr)
    on_n  = int(COART * n)
    off_n = int(COART * n)

    f_mean = list(A_F)
    if F_prev is not None and on_n > 0:
        for k in range(min(len(F_prev),
                           len(A_F))):
            f_mean[k] = (F_prev[k] * 0.12
                         + A_F[k] * 0.88)
    if F_next is not None and off_n > 0:
        for k in range(min(len(F_next),
                           len(A_F))):
            f_mean[k] = (f_mean[k] * 0.88
                         + F_next[k] * 0.12)

    out = apply_formants(src, f_mean,
                         A_B, A_GAINS, sr=sr)
    mx  = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.72
    return f32(out)


def synth_M(F_prev=None, F_next=None,
            pitch_hz=PITCH_HZ,
            dil=DIL, sr=SR):
    """
    [m] — voiced bilabial nasal.
    Śikṣā: oṣṭhya.
    Lip closure sustained.
    Nasal side branch open.
    Antiresonance at ~800 Hz.
    F2 lower than [n] — bilabial position.
    Same iir_notch architecture as [n].
    """
    n_ms  = VS_M_DUR_MS * dil
    n     = int(n_ms / 1000.0 * sr)
    src   = rosenberg_pulse(n, pitch_hz,
                            oq=0.65, sr=sr)
    on_n  = int(VS_M_COART_ON * n)
    off_n = int(VS_M_COART_OFF * n)

    f_mean = list(VS_M_F)
    if F_prev is not None and on_n > 0:
        for k in range(min(len(F_prev),
                           len(VS_M_F))):
            f_mean[k] = (F_prev[k] * 0.15
                         + VS_M_F[k] * 0.85)
    if F_next is not None and off_n > 0:
        for k in range(min(len(F_next),
                           len(VS_M_F))):
            f_mean[k] = (f_mean[k] * 0.85
                         + F_next[k] * 0.15)

    out = apply_formants(src, f_mean,
                         VS_M_B, VS_M_GAINS,
                         sr=sr)
    out = iir_notch(out,
                    VS_M_ANTI_F,
                    VS_M_ANTI_BW, sr=sr)
    mx  = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.40
    return f32(out)


# ── ROOM MODEL ────────────────────────────────────────

def apply_simple_room(sig, rt60=1.5,
                      direct_ratio=0.55,
                      sr=SR):
    n_rev = int(rt60 * sr)
    ir    = np.zeros(n_rev, dtype=float)
    ir[0] = 1.0
    decay = np.exp(
        -6.908 * np.arange(n_rev) /
        (rt60 * sr))
    noise_ir = np.random.randn(n_rev) * decay
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

def synth_purohitam(pitch_hz=PITCH_HZ,
                    dil=DIL,
                    with_room=False,
                    sr=SR):
    """
    PUROHITAM [puroːhitɑm]
    Rigveda 1.1.1, word 3.
    The household priest.
    Literally: one placed in front.

    Syllables: PU — RO — HI — TAM

    Coarticulation chain:
      P:  word-initial, into [u]
      U:  from [p], into [ɾ]
      R:  from [u], into [oː]
      OO: from [ɾ], into [h]
      H:  from [oː], into [i]
      I:  from [h], into [t]
      T:  from [i], into [ɑ]
      A:  from [t], into [m]
      M:  from [ɑ], word-final
    """
    p_seg  = synth_P(F_prev=None,
                     F_next=VS_U_F,
                     dil=dil, sr=sr)
    u_seg  = synth_U(F_prev=None,
                     F_next=VS_R_F,
                     pitch_hz=pitch_hz,
                     dil=dil, sr=sr)
    r_seg  = synth_R(F_prev=VS_U_F,
                     F_next=VS_OO_F,
                     pitch_hz=pitch_hz,
                     dil=dil, sr=sr)
    oo_seg = synth_OO(F_prev=VS_R_F,
                      F_next=VS_I_F,
                      pitch_hz=pitch_hz,
                      dil=dil, sr=sr)
    h_seg  = synth_H(F_prev=VS_OO_F,
                     F_next=VS_I_F,
                     dil=dil, sr=sr)
    i_seg  = synth_I_vs(F_prev=VS_OO_F,
                        F_next=VS_T_BURST_F
                        and VS_A_F,
                        pitch_hz=pitch_hz,
                        dil=dil, sr=sr)
    t_seg  = synth_T(F_prev=VS_I_F,
                     F_next=VS_A_F,
                     dil=dil, sr=sr)
    a_seg  = synth_A_vs(F_prev=VS_A_F,
                        F_next=VS_M_F,
                        pitch_hz=pitch_hz,
                        dil=dil, sr=sr)
    m_seg  = synth_M(F_prev=VS_A_F,
                     F_next=None,
                     pitch_hz=pitch_hz,
                     dil=dil, sr=sr)

    word = np.concatenate([
        p_seg, u_seg, r_seg, oo_seg,
        h_seg, i_seg, t_seg, a_seg, m_seg])

    mx = np.max(np.abs(word))
    if mx > 1e-8:
        word = word / mx * 0.75

    if with_room:
        word = apply_simple_room(
            word, rt60=1.5,
            direct_ratio=0.55, sr=sr)

    return f32(word)


# expose for diagnostic import
VS_T_BURST_F_VAL = VS_T_BURST_F


# ── MAIN ──────────────────────────────────────────────

if __name__ == "__main__":
    print("Synthesising PUROHITAM [puroːhitɑm]...")

    dry  = synth_purohitam(with_room=False)
    hall = synth_purohitam(with_room=True)
    slow = ola_stretch(dry, 4.0)

    write_wav("output_play/purohitam_dry.wav",  dry)
    write_wav("output_play/purohitam_hall.wav", hall)
    write_wav("output_play/purohitam_slow.wav", slow)

    # Isolated new phonemes
    for sig, name in [
        (synth_U(),  "purohitam_u_iso"),
        (synth_R(),  "purohitam_r_iso"),
        (synth_OO(), "purohitam_oo_iso"),
        (synth_H(),  "purohitam_h_iso"),
        (synth_M(),  "purohitam_m_iso"),
    ]:
        mx = np.max(np.abs(sig))
        if mx > 1e-8:
            sig = sig / mx * 0.75
        write_wav(
            f"output_play/{name}.wav", sig)
        write_wav(
            f"output_play/{name}_slow.wav",
            ola_stretch(sig, 4.0))

    print("Written:")
    print("  output_play/purohitam_dry.wav")
    print("  output_play/purohitam_hall.wav")
    print("  output_play/purohitam_slow.wav")
    print("  Isolated: u, r, oo, h, m")
    print()
    print("Run purohitam_diagnostic.py to verify.")
