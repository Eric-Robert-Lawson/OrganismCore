"""
AGNI RECONSTRUCTION v1
Vedic Sanskrit: agni  [ɑgni]
Rigveda 1.1.1 — word 1
February 2026

PHONEMES:
  [ɑ]  short open back unrounded    — NEW
  [g]  voiced velar stop            — VS-verified (ṚG)
  [n]  voiced alveolar nasal        — NEW (first VS nasal)
  [i]  short close front unrounded  — NEW

SYLLABLE STRUCTURE:
  AG — [ɑg] — closed syllable, heavy
  NI — [ni] — open syllable, light

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
  [ɑ] — kaṇṭhya   (guttural/velar)
         The maximally open vocal tract.
         Śikṣā places the open vowel [a]
         in the velar class because the
         constriction, such as it is,
         is at the posterior of the
         vocal tract. High F1 — wide jaw.
  [g] — kaṇṭhya   — verified ṚG
  [n] — dantya    (dental/alveolar)
         Tongue tip at alveolar ridge.
         Nasal side branch open.
         Antiresonance at ~800 Hz.
  [i] — tālavya   (palatal)
         Tongue body raised toward
         the hard palate. High F2.
         Low F1 — close jaw.

NEW ARCHITECTURE:
  [n]: nasal murmur with antiresonance.
       iir_notch() at ~800 Hz models
       the acoustic zero from the
       nasal side branch.
       This is the first VS nasal.
       The antiresonance is the
       diagnostic signature of the
       nasal class.

COARTICULATION:
  [ɑ] → [g]: open back vowel into
             velar closure.
             F2 rises toward velar locus.
  [g] → [n]: velar burst into alveolar
             nasal. F2 drops from ~2500 Hz
             to nasal murmur position.
             First [gn] cluster in VS.
  [n] → [i]: nasal release into close
             front vowel. F2 rises sharply
             from nasal murmur to ~2200 Hz.

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
# F3 of an unconstricted alveolar vocal tract.
# Calculated from tube acoustics.
# Language-independent physics constant.

# ── ŚIKṢĀ REFERENCES — VS-internal ───────────���───────

KANTHHYA_BURST_LO_HZ   = 1800.0
KANTHHYA_BURST_HI_HZ   = 3200.0
# Kaṇṭhya (velar) burst locus range.
# Confirmed in ṚG: burst centroid 2577 Hz.

DANTYA_ANTI_F_HZ       = 800.0
# Dantya (dental/alveolar) nasal antiresonance.
# Alveolar nasal zero ~800 Hz.
# Derived from Śikṣā dantya classification
# and tube acoustics of the nasal side branch.

TALAVYA_F2_LO_HZ       = 1900.0
TALAVYA_F2_HI_HZ       = 2500.0
# Tālavya (palatal) F2 range.
# Tongue body raised to hard palate.
# High F2 — front constriction.


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
# VS-verified in ṚG.
# Parameters confirmed: LF 0.9703,
# burst centroid 2577 Hz.
VS_G_F           = [300.0, 1900.0, 2500.0, 3200.0]
VS_G_B           = [120.0,  200.0,  280.0,  350.0]
VS_G_GAINS       = [ 14.0,    6.0,    1.5,    0.4]
VS_G_CLOSURE_MS  = 30.0
VS_G_BURST_F     = 2500.0
VS_G_BURST_BW    = 1200.0
VS_G_BURST_MS    = 8.0
VS_G_VOT_MS      = 10.0
VS_G_MURMUR_GAIN = 0.70
VS_G_BURST_GAIN  = 0.30

# [n] — voiced alveolar nasal — न
# Śikṣā: dantya
# First VS nasal.
# Sustained voiced murmur.
# Antiresonance (zero) at ~800 Hz —
# the nasal side branch absorbs
# energy at this frequency.
# This is the dantya nasal marker.
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

def ola_stretch(sig, factor=4.0, sr=SR):
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
    """
    Rosenberg glottal pulse model.
    oq: open quotient — 0.65 male voice.
    Differentiated for formant filtering.
    """
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
    d_pulse  = np.diff(pulse,
                       prepend=pulse[0])
    n_reps   = (n_samples // period) + 2
    repeated = np.tile(d_pulse, n_reps)
    return f32(repeated[:n_samples])

def apply_formants(src, freqs, bws, gains,
                   sr=SR):
    """
    IIR resonator bank — four formants.
    """
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
    """
    IIR notch filter.
    Models the acoustic zero (antiresonance)
    produced by the nasal side branch.
    fc: centre frequency of the zero.
    bw: bandwidth of the notch.
    The notch depth confirms the nasal
    side branch is acoustically active.
    """
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

def synth_A(F_prev=None, F_next=None,
            pitch_hz=PITCH_HZ,
            dil=DIL, sr=SR):
    """
    [ɑ] — short open back unrounded.
    Śikṣā: kaṇṭhya.
    Sanskrit phonological default.
    High F1. Mid-back F2.
    """
    n_ms  = VS_A_DUR_MS * dil
    n     = int(n_ms / 1000.0 * sr)
    src   = rosenberg_pulse(n, pitch_hz,
                            oq=0.65, sr=sr)
    on_n  = int(VS_A_COART_ON * n)
    off_n = int(VS_A_COART_OFF * n)

    f_mean = list(VS_A_F)
    if F_prev is not None and on_n > 0:
        for k in range(min(len(F_prev),
                           len(VS_A_F))):
            f_mean[k] = (F_prev[k] * 0.12
                         + VS_A_F[k] * 0.88)
    if F_next is not None and off_n > 0:
        for k in range(min(len(F_next),
                           len(VS_A_F))):
            f_mean[k] = (f_mean[k] * 0.88
                         + F_next[k] * 0.12)

    out = apply_formants(src, f_mean,
                         VS_A_B, VS_A_GAINS,
                         sr=sr)
    mx  = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.72
    return f32(out)


def synth_G(F_prev=None, F_next=None,
            pitch_hz=PITCH_HZ,
            dil=DIL, sr=SR):
    """
    [g] — voiced velar stop.
    Śikṣā: kaṇṭhya.
    VS-verified in ṚG.
    Three-phase: closure / burst / VOT.
    """
    n_closure = int(
        VS_G_CLOSURE_MS * dil / 1000.0 * sr)
    n_burst   = int(
        VS_G_BURST_MS   * dil / 1000.0 * sr)
    n_vot     = int(
        VS_G_VOT_MS     * dil / 1000.0 * sr)

    src_cl = rosenberg_pulse(
        n_closure, pitch_hz, sr=sr)
    b_lp, a_lp = safe_lp(800.0, sr)
    if b_lp is not None:
        murmur = lfilter(b_lp, a_lp,
                         src_cl.astype(float))
    else:
        murmur = src_cl.astype(float)
    murmur = f32(murmur * VS_G_MURMUR_GAIN)

    noise  = np.random.randn(n_burst)
    b_bp, a_bp = safe_bp(
        VS_G_BURST_F - VS_G_BURST_BW / 2,
        VS_G_BURST_F + VS_G_BURST_BW / 2,
        sr)
    if b_bp is not None:
        burst = lfilter(b_bp, a_bp, noise)
    else:
        burst = noise
    burst = f32(burst * VS_G_BURST_GAIN)

    if n_vot > 0:
        src_vot = rosenberg_pulse(
            n_vot, pitch_hz, sr=sr)
        f_vot   = (F_next if F_next is not None
                   else VS_G_F)
        vot     = apply_formants(
            src_vot, f_vot,
            VS_G_B, VS_G_GAINS, sr=sr)
        vot     = f32(vot * 0.10)
    else:
        vot = np.array([], dtype=DTYPE)

    out = np.concatenate([murmur, burst, vot])
    mx  = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.65
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
    The antiresonance is the acoustic
    consequence of the nasal side
    branch — the velum is lowered,
    allowing airflow through the nasal
    cavity, which creates a zero in
    the transfer function.
    """
    n_ms  = VS_N_DUR_MS * dil
    n     = int(n_ms / 1000.0 * sr)
    src   = rosenberg_pulse(n, pitch_hz,
                            oq=0.65, sr=sr)
    on_n  = int(VS_N_COART_ON * n)
    off_n = int(VS_N_COART_OFF * n)

    f_mean = list(VS_N_F)
    if F_prev is not None and on_n > 0:
        for k in range(min(len(F_prev),
                           len(VS_N_F))):
            f_mean[k] = (F_prev[k] * 0.15
                         + VS_N_F[k] * 0.85)
    if F_next is not None and off_n > 0:
        for k in range(min(len(F_next),
                           len(VS_N_F))):
            f_mean[k] = (f_mean[k] * 0.85
                         + F_next[k] * 0.15)

    out = apply_formants(src, f_mean,
                         VS_N_B, VS_N_GAINS,
                         sr=sr)
    # Apply antiresonance — the nasal zero
    out = iir_notch(out,
                    VS_N_ANTI_F,
                    VS_N_ANTI_BW, sr=sr)
    mx  = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.40
    return f32(out)


def synth_I(F_prev=None, F_next=None,
            pitch_hz=PITCH_HZ,
            dil=DIL, sr=SR):
    """
    [i] — short close front unrounded.
    Śikṣā: tālavya.
    Low F1 — close jaw.
    High F2 — tongue body to hard palate.
    Front corner of the VS vowel triangle.
    """
    n_ms  = VS_I_DUR_MS * dil
    n     = int(n_ms / 1000.0 * sr)
    src   = rosenberg_pulse(n, pitch_hz,
                            oq=0.65, sr=sr)
    on_n  = int(VS_I_COART_ON * n)
    off_n = int(VS_I_COART_OFF * n)

    f_mean = list(VS_I_F)
    if F_prev is not None and on_n > 0:
        for k in range(min(len(F_prev),
                           len(VS_I_F))):
            f_mean[k] = (F_prev[k] * 0.12
                         + VS_I_F[k] * 0.88)
    if F_next is not None and off_n > 0:
        for k in range(min(len(F_next),
                           len(VS_I_F))):
            f_mean[k] = (f_mean[k] * 0.88
                         + F_next[k] * 0.12)

    out = apply_formants(src, f_mean,
                         VS_I_B, VS_I_GAINS,
                         sr=sr)
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
    VS default. Outdoor ritual or
    open stone space.
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
    The fire priest. The invocation.

    Syllable structure: AG — NI

    Coarticulation chain:
      A:  word-initial, F_prev=None
          coarticulates toward VS_G_F
      G:  coarticulates from VS_A_F
          coarticulates toward VS_N_F
      N:  coarticulates from VS_G_F
          coarticulates toward VS_I_F
      I:  coarticulates from VS_N_F
          word-final, F_next=None
    """
    a_seg = synth_A(F_prev=None,
                    F_next=VS_G_F,
                    pitch_hz=pitch_hz,
                    dil=dil, sr=sr)
    g_seg = synth_G(F_prev=VS_A_F,
                    F_next=VS_N_F,
                    pitch_hz=pitch_hz,
                    dil=dil, sr=sr)
    n_seg = synth_N(F_prev=VS_G_F,
                    F_next=VS_I_F,
                    pitch_hz=pitch_hz,
                    dil=dil, sr=sr)
    i_seg = synth_I(F_prev=VS_N_F,
                    F_next=None,
                    pitch_hz=pitch_hz,
                    dil=dil, sr=sr)

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
    print("Synthesising AGNI [ɑgni]...")

    dry  = synth_agni(with_room=False)
    hall = synth_agni(with_room=True)
    slow = ola_stretch(dry, 4.0)

    write_wav("output_play/agni_dry.wav",  dry)
    write_wav("output_play/agni_hall.wav", hall)
    write_wav("output_play/agni_slow.wav", slow)

    # Isolated phonemes for triangle check
    a_iso = synth_A(F_prev=None, F_next=None)
    i_iso = synth_I(F_prev=None, F_next=None)
    n_iso = synth_N(F_prev=None, F_next=None)

    for sig, name in [
        (a_iso, "agni_a_isolated"),
        (i_iso, "agni_i_isolated"),
        (n_iso, "agni_n_isolated"),
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
    print("  output_play/agni_dry.wav")
    print("  output_play/agni_hall.wav")
    print("  output_play/agni_slow.wav")
    print("  output_play/agni_a_isolated.wav")
    print("  output_play/agni_a_isolated_slow.wav")
    print("  output_play/agni_i_isolated.wav")
    print("  output_play/agni_i_isolated_slow.wav")
    print("  output_play/agni_n_isolated.wav")
    print("  output_play/agni_n_isolated_slow.wav")
    print()
    print("Run agni_diagnostic.py to verify.")
