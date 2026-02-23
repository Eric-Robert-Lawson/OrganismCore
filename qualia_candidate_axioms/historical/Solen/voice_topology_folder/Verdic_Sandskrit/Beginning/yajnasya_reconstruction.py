"""
YAJÑASYA RECONSTRUCTION v1
Vedic Sanskrit: yajñasya  [jɑɟɲɑsjɑ]
Rigveda 1.1.1 — word 4
February 2026

PHONEMES:
  [j]  voiced palatal approximant    — NEW (tālavya antastha)
  [ɑ]  short open central            — VS-verified AGNI ×3
  [ɟ]  voiced palatal stop           — NEW (tālavya row 3)
  [ɲ]  voiced palatal nasal          — NEW (tālavya row 5)
  [s]  voiceless dental sibilant     — NEW (dantya)

SYLLABLE STRUCTURE:
  YAJ — ÑA — SYA
  [jɑɟ] — [ɲɑ] — [sjɑ]

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
  [j]  — tālavya (palatal)
          Śikṣā: antastha — ya ra la va
          Tongue body raised toward hard palate.
          Sustained constriction. No closure.
          F2 high (~2100 Hz) — palatal sector.
          NOT a stop. NOT a tap.
          An approximant: the palate approached
          but not contacted.
          Pāṇinīya Śikṣā places ya with ra la va
          in the antastha (semivowel) class.
          Architecture: Rosenberg pulse through
          palatal formant bank. No amplitude dip.
          No burst. Sustained voiced constriction.

  [ɟ]  — tālavya (palatal)
          Row 3 of the palatal stop column.
          Tongue body contact with hard palate.
          Voiced closure — LF ratio.
          Burst at palatal locus ~3200 Hz.
          Voiced stop: same three-phase
          architecture as [g] and [d] but
          at palatal burst frequency.
          The second new burst locus
          after [p] and [t].
          The palatal burst locus must slot
          between [g] kaṇṭhya (2594 Hz)
          and [t] dantya (3764 Hz).

  [ɲ]  — tālavya (palatal)
          Row 5 of the palatal column.
          Tongue body to hard palate.
          Voiced. Velum open.
          Nasal side branch active.
          High F2 nasal: ~2000 Hz.
          Antiresonance at ~1200 Hz —
          higher than [n] and [m] because
          the palatal nasal side branch
          is shorter than dental or bilabial.
          Shorter tube = higher resonance
          in the nasal side branch.
          Same physics as stop burst hierarchy
          but for the nasal zero.

  [s]  — dantya (dental)
          Voiceless dental sibilant.
          No Rosenberg source.
          Band-filtered noise at high CF.
          Dental constriction: turbulent
          jet directed against upper teeth.
          Minimal anterior cavity.
          High CF: ~7500 Hz.
          Highest-frequency phoneme
          in the VS inventory so far.
          Voiceless throughout.

KEY TRANSITION — [ɟ] → [ɲ]:
  Both tālavya. Same place of articulation.
  Stop (row 3) → nasal (row 5).
  The burst of [ɟ] releases into [ɲ].
  F2 locus does not move — both are
  palatal (~3200 Hz locus territory).
  What changes: the velum opens for [ɲ].
  Acoustically: the nasal antiresonance
  appears as the velum opens.
  The F2 formant is continuous across
  the [ɟ]→[ɲ] boundary. The nasal
  zero is the only new acoustic event.
  This transition tests the architecture
  of the nasal coupling model.

KEY TRANSITION — [s] → [j]:
  Voiceless fricative → voiced approximant.
  Noise source → Rosenberg source.
  The voicing onset at the [s]→[j] boundary
  is one of the sharpest transitions
  in the word. CF drops from ~7500 Hz
  to formant structure. F2 rises from
  sibilant band to palatal ~2100 Hz.

COARTICULATION:
  [j]  → [ɑ]:  palatal approximant into open vowel.
               F2 falls from 2100 Hz toward 1106 Hz.
               The glide is the coarticulation.
  [ɑ]  → [ɟ]:  open vowel into palatal stop closure.
               F2 rises toward palatal burst locus
               through the closure transition.
  [ɟ]  → [ɲ]:  palatal stop burst into palatal nasal.
               F2 locus constant (same place).
               Velum opens — nasal coupling appears.
  [ɲ]  → [ɑ]:  palatal nasal into open vowel.
               F2 falls from 2000 Hz toward 1106 Hz.
               Nasal coupling closes — modal voice.
  [ɑ]  → [s]:  open vowel into voiceless sibilant.
               Voicing ends. Noise begins.
               F2 transitions into sibilant band.
  [s]  → [j]:  sibilant into palatal approximant.
               Noise ends. Voicing begins.
               F2 rises toward palatal 2100 Hz.
  [j]  → [ɑ]:  same as first [j]→[ɑ] transition.

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

NEUTRAL_ALVEOLAR_F3_HZ  = 2700.0
# Physics constant. Language-independent.

DANTYA_SIBILANT_CF_HZ   = 7500.0
# Dental sibilant: turbulent jet against
# teeth. Minimal anterior cavity.
# High CF. Physics of dental constriction.

PALATAL_BURST_F_HZ      = 3200.0
# Palatal burst locus: between kaṇṭhya
# (2594 Hz) and dantya (3764 Hz).
# Tongue body to hard palate.


# ── ŚIKṢĀ REFERENCES — VS-internal ───────────────────

TALAVYA_BURST_LO_HZ   = 2800.0
TALAVYA_BURST_HI_HZ   = 4000.0
# Palatal burst window.
# Higher than kaṇṭhya (1800–3200),
# overlapping with dantya (3000–4500)
# but distinct F2 locus approach.

TALAVYA_F2_LO_HZ      = 1800.0
TALAVYA_F2_HI_HZ      = 2400.0
# Palatal approximant and nasal F2 range.

PALATAL_NASAL_ANTI_LO  =  900.0
PALATAL_NASAL_ANTI_HI  = 1500.0
# Palatal nasal antiresonance zone.
# Higher than [n] and [m] (~800 Hz)
# because palatal nasal side branch
# is shorter.

DANTYA_SIBILANT_LO_HZ  = 5000.0
DANTYA_SIBILANT_HI_HZ  = 11000.0
# Dental sibilant noise band.
# Highest CF in VS inventory.


# ── VS-INTERNAL VERIFIED REFERENCES ──────────────────

VS_A_F2_HZ       = 1106.0   # AGNI verified
VS_A_F1_HZ       =  631.0   # AGNI verified
VS_A_F            = [700.0, 1100.0, 2550.0, 3400.0]
VS_G_BURST_HZ    = 2594.0   # ṚG/AGNI verified
VS_T_BURST_HZ    = 3764.0   # PUROHITAM verified
VS_P_BURST_HZ    = 1204.0   # PUROHITAM verified
VS_N_ANTI_RATIO  =  0.0018  # AGNI verified
VS_M_ANTI_RATIO  =  0.0046  # PUROHITAM verified
VS_N_F2_HZ       =  900.0   # AGNI params
VS_M_F2_HZ       =  552.0   # PUROHITAM verified
VS_RV_F3_HZ      = 2355.0   # ṚG verified
VS_I_F2_HZ       = 2124.0   # AGNI verified


# ── PHONEME PARAMETERS ────────────────────────────────

# [j] — voiced palatal approximant — य
# Śikṣā: tālavya (antastha — semivowel)
# Tongue body raised toward hard palate.
# Sustained constriction. No closure.
# No amplitude dip — NOT a tap.
# No burst — NOT a stop.
# Rosenberg pulse through palatal formant bank.
# High F2 (~2100 Hz) — tālavya sector.
VS_J_F         = [280.0, 2100.0, 2800.0, 3300.0]
VS_J_B         = [100.0,  200.0,  300.0,  350.0]
VS_J_GAINS     = [ 10.0,    6.0,    1.5,    0.5]
VS_J_DUR_MS    = 55.0
VS_J_COART_ON  = 0.18   # longer coart — glide
VS_J_COART_OFF = 0.18

# [ɟ] — voiced palatal stop — ज
# Śikṣā: tālavya (row 3 — voiced unaspirated)
# Tongue body to hard palate.
# Voiced closure: LF ratio >= 0.40.
# Burst at palatal locus ~3200 Hz.
# Same three-phase architecture as [g].
VS_JJ_CLOSURE_MS  = 30.0
VS_JJ_BURST_F     = 3200.0
VS_JJ_BURST_BW    = 1500.0
VS_JJ_BURST_MS    = 9.0
VS_JJ_VOT_MS      = 10.0
VS_JJ_MURMUR_GAIN = 0.70
VS_JJ_BURST_GAIN  = 0.32

# [ɲ] — voiced palatal nasal — ञ
# Śikṣā: tālavya (row 5 — nasal)
# Tongue body to hard palate.
# Velum open. Nasal coupling active.
# High F2: ~2000 Hz — palatal position.
# Antiresonance at ~1200 Hz — higher than
# [n]/[m] because shorter nasal side branch.
VS_NY_F        = [250.0, 2000.0, 2800.0, 3300.0]
VS_NY_B        = [120.0,  180.0,  250.0,  300.0]
VS_NY_GAINS    = [  8.0,    4.0,    1.2,    0.4]
VS_NY_DUR_MS   = 65.0
VS_NY_ANTI_F   = 1200.0
VS_NY_ANTI_BW  = 250.0
VS_NY_COART_ON  = 0.15
VS_NY_COART_OFF = 0.15

# [s] — voiceless dental sibilant — स
# Śikṣā: dantya
# Turbulent jet against upper teeth.
# Minimal anterior cavity.
# High CF: ~7500 Hz.
# No Rosenberg source.
VS_S_NOISE_CF  = 7500.0
VS_S_NOISE_BW  = 3000.0
VS_S_GAIN      = 0.22
VS_S_DUR_MS    = 80.0

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
    mx       = np.max(np.abs(out))
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

def synth_J(F_prev=None, F_next=None,
            pitch_hz=PITCH_HZ,
            dil=DIL, sr=SR):
    """
    [j] — voiced palatal approximant.
    Śikṣā: tālavya (antastha — semivowel).
    Pāṇinīya Śikṣā: ya ra la va.
    Sustained palatal constriction.
    No closure. No amplitude dip.
    Not a stop. Not a tap.
    Rosenberg pulse through palatal
    formant bank. High F2 (~2100 Hz).
    F3 neutral — no retroflex curl.
    Longer coarticulation window (0.18)
    because the glide quality IS the
    coarticulation — the transition
    through the palatal position IS [j].
    """
    n_ms  = VS_J_DUR_MS * dil
    n     = int(n_ms / 1000.0 * sr)
    src   = rosenberg_pulse(n, pitch_hz,
                            oq=0.65, sr=sr)
    on_n  = int(VS_J_COART_ON  * n)
    off_n = int(VS_J_COART_OFF * n)

    f_mean = list(VS_J_F)
    if F_prev is not None and on_n > 0:
        for k in range(min(len(F_prev),
                           len(VS_J_F))):
            f_mean[k] = (F_prev[k] * 0.18
                         + VS_J_F[k] * 0.82)
    if F_next is not None and off_n > 0:
        for k in range(min(len(F_next),
                           len(VS_J_F))):
            f_mean[k] = (f_mean[k] * 0.82
                         + F_next[k] * 0.18)

    out = apply_formants(src, f_mean,
                         VS_J_B, VS_J_GAINS,
                         sr=sr)
    # Smooth amplitude envelope — no dip
    # This distinguishes [j] from [ɾ] tap
    env = np.ones(n, dtype=float)
    atk = min(int(0.012 * sr), n // 4)
    rel = min(int(0.012 * sr), n // 4)
    if atk > 0:
        env[:atk] = np.linspace(0.0, 1.0, atk)
    if rel > 0:
        env[-rel:] = np.linspace(1.0, 0.0, rel)
    out = f32(out * env)

    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.65
    return f32(out)


def synth_JJ(F_prev=None, F_next=None,
             dil=DIL, sr=SR):
    """
    [ɟ] — voiced palatal stop.
    Śikṣā: tālavya (row 3 — voiced unasp.).
    Three-phase architecture:
      Phase 1: voiced closure murmur
      Phase 2: palatal burst ~3200 Hz
      Phase 3: short voiced VOT
    Same architecture as [g] but at
    palatal burst locus.
    LF ratio confirms voiced closure.
    Burst centroid must be in palatal
    window: between [g] 2594 Hz and
    [t] 3764 Hz.
    """
    n_closure = int(
        VS_JJ_CLOSURE_MS * dil / 1000.0 * sr)
    n_burst   = int(
        VS_JJ_BURST_MS   * dil / 1000.0 * sr)
    n_vot     = int(
        VS_JJ_VOT_MS     * dil / 1000.0 * sr)

    # Phase 1: voiced closure murmur
    if n_closure > 0:
        src_cl  = rosenberg_pulse(
            n_closure, PITCH_HZ, sr=sr)
        b_lp, a_lp = butter(
            2, 500.0 / (sr / 2.0),
            btype='low')
        murmur  = lfilter(
            b_lp, a_lp,
            src_cl.astype(float))
        closure = f32(murmur
                      * VS_JJ_MURMUR_GAIN)
    else:
        closure = np.array([], dtype=DTYPE)

    # Phase 2: palatal burst
    noise = np.random.randn(
        max(n_burst, 4)).astype(float)
    b_bp, a_bp = safe_bp(
        VS_JJ_BURST_F - VS_JJ_BURST_BW / 2,
        VS_JJ_BURST_F + VS_JJ_BURST_BW / 2,
        sr)
    if b_bp is not None:
        burst = lfilter(b_bp, a_bp, noise)
    else:
        burst = noise
    if len(burst) > 1:
        env_b = np.hanning(len(burst))
        burst = burst * env_b
    burst = f32(burst * VS_JJ_BURST_GAIN)

    # Phase 3: voiced VOT into following vowel
    if n_vot > 0:
        src_vot = rosenberg_pulse(
            n_vot, PITCH_HZ, sr=sr)
        f_vot   = (F_next if F_next is not None
                   else VS_A_F)
        vot_env = np.linspace(0.0, 1.0, n_vot)
        vot     = apply_formants(
            src_vot, f_vot,
            [120.0, 160.0, 200.0, 280.0],
            [14.0, 6.0, 1.5, 0.4], sr=sr)
        vot     = f32(vot * vot_env * 0.12)
    else:
        vot = np.array([], dtype=DTYPE)

    out = np.concatenate([closure, burst, vot])
    mx  = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.58
    return f32(out)


def synth_NY(F_prev=None, F_next=None,
             pitch_hz=PITCH_HZ,
             dil=DIL, sr=SR):
    """
    [ɲ] — voiced palatal nasal.
    Śikṣā: tālavya (row 5 — nasal).
    Tongue body to hard palate.
    Velum open. Nasal coupling active.
    High F2 (~2000 Hz) — palatal position.
    Antiresonance at ~1200 Hz.
    Higher antiresonance than [n] and [m]
    because the palatal nasal side branch
    (from velum to palate) is shorter
    than dental or bilabial branches.
    Shorter branch = higher nasal zero.
    Same physics as stop burst hierarchy:
    place determines frequency.
    Applied via iir_notch.
    """
    n_ms  = VS_NY_DUR_MS * dil
    n     = int(n_ms / 1000.0 * sr)
    src   = rosenberg_pulse(n, pitch_hz,
                            oq=0.65, sr=sr)
    on_n  = int(VS_NY_COART_ON  * n)
    off_n = int(VS_NY_COART_OFF * n)

    f_mean = list(VS_NY_F)
    if F_prev is not None and on_n > 0:
        for k in range(min(len(F_prev),
                           len(VS_NY_F))):
            f_mean[k] = (F_prev[k] * 0.15
                         + VS_NY_F[k] * 0.85)
    if F_next is not None and off_n > 0:
        for k in range(min(len(F_next),
                           len(VS_NY_F))):
            f_mean[k] = (f_mean[k] * 0.85
                         + F_next[k] * 0.15)

    out = apply_formants(src, f_mean,
                         VS_NY_B, VS_NY_GAINS,
                         sr=sr)
    out = iir_notch(out,
                    VS_NY_ANTI_F,
                    VS_NY_ANTI_BW, sr=sr)
    mx  = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.42
    return f32(out)


def synth_S(F_prev=None, F_next=None,
            dil=DIL, sr=SR):
    """
    [s] — voiceless dental sibilant.
    Śikṣā: dantya.
    No Rosenberg source — voiceless.
    Band-filtered noise at dental CF.
    CF ~7500 Hz — highest frequency
    phoneme in the VS inventory.
    The turbulent jet strikes the teeth.
    Minimal anterior cavity.
    Physics of dental constriction:
    the same cavity-size principle
    that places [t] burst at 3764 Hz
    (dantya stop) here produces
    the sibilant CF at ~7500 Hz.
    The sibilant is higher than the stop
    because the constriction is narrower
    and the turbulence is finer.
    """
    n_ms  = VS_S_DUR_MS * dil
    n     = int(n_ms / 1000.0 * sr)

    noise = np.random.randn(n).astype(float)
    b_bp, a_bp = safe_bp(
        VS_S_NOISE_CF - VS_S_NOISE_BW / 2,
        VS_S_NOISE_CF + VS_S_NOISE_BW / 2,
        sr)
    if b_bp is not None:
        out = lfilter(b_bp, a_bp, noise)
    else:
        out = noise

    # Amplitude envelope
    atk = min(int(0.010 * sr), n // 4)
    rel = min(int(0.015 * sr), n // 4)
    env = np.ones(n, dtype=float)
    if atk > 0:
        env[:atk] = np.linspace(0.0, 1.0, atk)
    if rel > 0:
        env[-rel:] = np.linspace(1.0, 0.0, rel)
    out = out * env * VS_S_GAIN

    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.42
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


# ── ROOM MODEL ────────────────────────────────────────

def apply_simple_room(sig, rt60=1.5,
                      direct_ratio=0.55,
                      sr=SR):
    n_rev    = int(rt60 * sr)
    ir       = np.zeros(n_rev, dtype=float)
    ir[0]    = 1.0
    decay    = np.exp(
        -6.908 * np.arange(n_rev) /
        (rt60 * sr))
    noise_ir = np.random.randn(n_rev) * decay
    ir       = (direct_ratio * ir
                + (1.0 - direct_ratio)
                * noise_ir)
    ir       = ir / (np.max(np.abs(ir))
                     + 1e-12)
    out = np.convolve(
        sig.astype(float),
        ir[:min(n_rev, 4096)])
    out = out[:len(sig)]
    mx  = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.75
    return f32(out)


# ── WORD SYNTHESISER ──────────────────────────────────

def synth_yajnasya(pitch_hz=PITCH_HZ,
                   dil=DIL,
                   with_room=False,
                   sr=SR):
    """
    YAJÑASYA [jɑɟɲɑsjɑ]
    Rigveda 1.1.1, word 4.
    Of the sacrifice.

    Segment sequence:
      J1  [j]  word-initial palatal approximant
      A1  [ɑ]  short open central (×1)
      JJ  [ɟ]  voiced palatal stop
      NY  [ɲ]  voiced palatal nasal
      A2  [ɑ]  short open central (×2)
      S   [s]  voiceless dental sibilant
      J2  [j]  palatal approximant (second)
      A3  [ɑ]  short open central (×3)

    Coarticulation chain:
      J1: word-initial, into [ɑ]
      A1: from [j], into [ɟ]
      JJ: from [ɑ], into [ɲ]
      NY: from [ɟ], into [ɑ]
      A2: from [ɲ], into [s]
      S:  from [ɑ], into [j]
      J2: from [s], into [ɑ]
      A3: from [j], word-final
    """
    A_F  = [700.0, 1100.0, 2550.0, 3400.0]

    j1_seg = synth_J(F_prev=None,
                     F_next=A_F,
                     pitch_hz=pitch_hz,
                     dil=dil, sr=sr)
    a1_seg = synth_A_vs(F_prev=VS_J_F,
                        F_next=VS_JJ_BURST_F
                        and A_F,
                        pitch_hz=pitch_hz,
                        dil=dil, sr=sr)
    jj_seg = synth_JJ(F_prev=A_F,
                      F_next=VS_NY_F,
                      dil=dil, sr=sr)
    ny_seg = synth_NY(F_prev=VS_JJ_BURST_F
                      and VS_NY_F,
                      F_next=A_F,
                      pitch_hz=pitch_hz,
                      dil=dil, sr=sr)
    a2_seg = synth_A_vs(F_prev=VS_NY_F,
                        F_next=None,
                        pitch_hz=pitch_hz,
                        dil=dil, sr=sr)
    s_seg  = synth_S(F_prev=A_F,
                     F_next=VS_J_F,
                     dil=dil, sr=sr)
    j2_seg = synth_J(F_prev=None,
                     F_next=A_F,
                     pitch_hz=pitch_hz,
                     dil=dil, sr=sr)
    a3_seg = synth_A_vs(F_prev=VS_J_F,
                        F_next=None,
                        pitch_hz=pitch_hz,
                        dil=dil, sr=sr)

    word = np.concatenate([
        j1_seg, a1_seg, jj_seg, ny_seg,
        a2_seg, s_seg,  j2_seg, a3_seg])

    mx = np.max(np.abs(word))
    if mx > 1e-8:
        word = word / mx * 0.75

    if with_room:
        word = apply_simple_room(
            word, rt60=1.5,
            direct_ratio=0.55, sr=sr)

    return f32(word)


# expose for diagnostic import
VS_JJ_BURST_F_VAL = VS_JJ_BURST_F
VS_S_NOISE_CF_VAL = VS_S_NOISE_CF


# ── MAIN ──────────────────────────────────────────────

if __name__ == "__main__":
    print("Synthesising YAJÑASYA [jɑɟɲɑsjɑ]...")

    dry  = synth_yajnasya(with_room=False)
    hall = synth_yajnasya(with_room=True)
    slow = ola_stretch(dry, 4.0)

    write_wav("output_play/yajnasya_dry.wav",  dry)
    write_wav("output_play/yajnasya_hall.wav", hall)
    write_wav("output_play/yajnasya_slow.wav", slow)

    # Isolated new phonemes
    for sig, name in [
        (synth_J(),  "yajnasya_j_iso"),
        (synth_JJ(), "yajnasya_jj_iso"),
        (synth_NY(), "yajnasya_ny_iso"),
        (synth_S(),  "yajnasya_s_iso"),
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
    print("  output_play/yajnasya_dry.wav")
    print("  output_play/yajnasya_hall.wav")
    print("  output_play/yajnasya_slow.wav")
    print("  Isolated: j, jj, ny, s")
    print()
    print("Run yajnasya_diagnostic.py to verify.")
