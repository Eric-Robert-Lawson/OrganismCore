"""
ĪḶE RECONSTRUCTION v1
Vedic Sanskrit: īḷe  [iːɭe]
Rigveda 1.1.1 — word 2
February 2026

PHONEMES:
  [iː] long close front unrounded  — length variant of verified [i]
  [ɭ]  retroflex lateral approximant — NEW (mūrdhanya + lateral)
  [eː] long close-mid front unrounded — NEW (tālavya mid)

SYLLABLE STRUCTURE:
  Ī  — [iː] — long vowel, heavy syllable
  ḶE — [ɭe] — retroflex lateral + mid vowel

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
  [iː] — tālavya (palatal)
          Same position as verified [i].
          Duration is the only distinction.
          Śikṣā does not distinguish short
          and long by quality — only by
          quantity. Same tongue position.
          Same formant targets. Longer hold.

  [ɭ]  — mūrdhanya (retroflex/cerebral)
          + lateral manner
          Tongue tip retroflexed to post-
          alveolar region. Lateral airflow
          around the sides of the tongue.
          Two simultaneous constraints:
            Retroflex: F3 depressed < 2500 Hz
            Lateral:   F2 reduced ~1000–1200 Hz
          The first VS phoneme in two
          Śikṣā classes simultaneously.

  [eː] — tālavya (palatal)
          Mid front vowel. Between [i] and [ɑ]
          in both F1 and F2. Sanskrit [e] is
          always long — no short counterpart.
          Tālavya because the tongue body
          is raised toward the palate,
          though not as high as for [i].

NEW ARCHITECTURE:
  [ɭ]: lateral approximant synthesis.
       Rosenberg source through formant bank
       at lateral targets. The lateral
       configuration reduces F2 relative to
       central vowels at the same F1.
       Additionally: iir_notch() at F3 for
       the mūrdhanya marker. The F3 dip
       must be present — otherwise the
       tongue is not curled and the phoneme
       is a plain [l], not [ɭ].

  [iː]: same synthesiser as [i].
        Duration parameter doubled.
        No new architecture required.

  [eː]: new formant targets. Tālavya mid.
        F1 between [i] and [ɑ].
        F2 between [i] and [ɑ].

COARTICULATION:
  [iː] → [ɭ]: long close front into
              retroflex lateral.
              F2 drops from ~2200 Hz
              to ~1100 Hz through transition.
              F3 drops as tongue curls back.
  [ɭ]  → [eː]: retroflex lateral into
               mid front vowel.
               F2 rises from ~1100 Hz
               to ~1700 Hz.
               F3 rises back toward neutral
               as tongue uncurls.

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
# The baseline from which retroflex
# F3 depression is measured.


# ── ŚIKṢĀ REFERENCES — VS-internal ───────────────────

MURDHANYA_F3_DEPRESSION_MIN_HZ = 200.0
# Mūrdhanya F3 depression minimum.
# Established in ṚG: [ɻ̩] depression 345 Hz.
# Same criterion applies to all
# mūrdhanya phonemes including [ɭ].

MURDHANYA_F2_LO_HZ = 1000.0
MURDHANYA_F2_HI_HZ = 1500.0
# Mūrdhanya lateral F2 range.
# Lower than central mūrdhanya [ɻ̩]
# because lateral airflow further
# reduces F2 relative to central
# approximants at the same place.

TALAVYA_F2_MID_LO_HZ = 1500.0
TALAVYA_F2_MID_HI_HZ = 2000.0
# Tālavya mid vowel [eː] F2 range.
# Below [i] (2124 Hz — AGNI verified).
# Above [ɑ] (1106 Hz — AGNI verified).

TALAVYA_F1_MID_LO_HZ = 380.0
TALAVYA_F1_MID_HI_HZ = 550.0
# [eː] F1 range. Mid height.
# Above [i] (~280 Hz).
# Below [ɑ] (631 Hz — AGNI verified).


# ── VS-INTERNAL VERIFIED REFERENCES ──────────────────

VS_I_F2_HZ   = 2124.0
VS_I_DUR_MS  = 50.0
# [i] verified AGNI — February 2026.

VS_RV_F2_HZ  = 1212.0
VS_RV_F3_HZ  = 2355.0
# [ɻ̩] verified ṚG — February 2026.

VS_A_F1_HZ   = 631.0
VS_A_F2_HZ   = 1106.0
# [ɑ] verified AGNI — February 2026.


# ── PHONEME PARAMETERS ────────────────────────────────

# [iː] — long close front unrounded — ई
# Śikṣā: tālavya
# Same position as verified [i].
# Duration >= 1.7× VS_I_DUR_MS = 85 ms.
VS_II_F      = [280.0, 2200.0, 2900.0, 3400.0]
VS_II_B      = [ 80.0,  130.0,  180.0,  250.0]
VS_II_GAINS  = [ 12.0,    8.0,    1.5,    0.5]
VS_II_DUR_MS = 100.0    # long: 2.0× [i] at 50 ms
VS_II_COART_ON  = 0.10
VS_II_COART_OFF = 0.10

# [ɭ] — retroflex lateral approximant — ळ
# Śikṣā: mūrdhanya + lateral
# Two simultaneous constraints:
#   Retroflex: F3 < 2500 Hz (mūrdhanya marker)
#   Lateral:   F2 ~1100 Hz (reduced by lateral flow)
# The F3 dip is the primary diagnostic.
# If F3 is not depressed, the tongue
# is not curled — the phoneme is wrong.
VS_LL_F      = [400.0, 1100.0, 2100.0, 3000.0]
VS_LL_B      = [200.0,  350.0,  400.0,  400.0]
VS_LL_GAINS  = [ 10.0,    5.0,    1.5,    0.4]
VS_LL_DUR_MS = 70.0
VS_LL_F3_NOTCH    = 2100.0
VS_LL_F3_NOTCH_BW = 350.0
VS_LL_COART_ON    = 0.15
VS_LL_COART_OFF   = 0.15

# [eː] — long close-mid front unrounded — ए
# Śikṣā: tālavya
# Sanskrit [e] is always long.
# No short counterpart in the Sanskrit system.
# Mid front — between [i] and [ɑ].
VS_EE_F      = [420.0, 1750.0, 2650.0, 3350.0]
VS_EE_B      = [100.0,  140.0,  200.0,  260.0]
VS_EE_GAINS  = [ 14.0,    8.0,    1.5,    0.5]
VS_EE_DUR_MS = 90.0
VS_EE_COART_ON  = 0.10
VS_EE_COART_OFF = 0.10

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
    d_pulse  = np.diff(pulse,
                       prepend=pulse[0])
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
    """
    IIR notch filter.
    Used for mūrdhanya F3 depression.
    fc: centre frequency of the zero.
    bw: bandwidth of the notch.
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

def synth_II(F_prev=None, F_next=None,
             pitch_hz=PITCH_HZ,
             dil=DIL, sr=SR):
    """
    [iː] — long close front unrounded.
    Śikṣā: tālavya.
    Same formant targets as verified [i].
    Duration is the phonemic distinction.
    Length >= 1.7× [i] duration (50 ms).
    Target: 100 ms.
    """
    n_ms  = VS_II_DUR_MS * dil
    n     = int(n_ms / 1000.0 * sr)
    src   = rosenberg_pulse(n, pitch_hz,
                            oq=0.65, sr=sr)
    on_n  = int(VS_II_COART_ON * n)
    off_n = int(VS_II_COART_OFF * n)

    f_mean = list(VS_II_F)
    if F_prev is not None and on_n > 0:
        for k in range(min(len(F_prev),
                           len(VS_II_F))):
            f_mean[k] = (F_prev[k] * 0.10
                         + VS_II_F[k] * 0.90)
    if F_next is not None and off_n > 0:
        for k in range(min(len(F_next),
                           len(VS_II_F))):
            f_mean[k] = (f_mean[k] * 0.90
                         + F_next[k] * 0.10)

    out = apply_formants(src, f_mean,
                         VS_II_B, VS_II_GAINS,
                         sr=sr)
    mx  = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.70
    return f32(out)


def synth_LL(F_prev=None, F_next=None,
             pitch_hz=PITCH_HZ,
             dil=DIL, sr=SR):
    """
    [ɭ] — retroflex lateral approximant.
    Śikṣā: mūrdhanya + lateral.

    Two simultaneous constraints:
      1. Mūrdhanya: F3 depression >= 200 Hz
         below neutral alveolar (2700 Hz).
         The tongue tip is retroflexed.
         iir_notch() at VS_LL_F3_NOTCH
         models the acoustic zero from
         the retroflexed tongue position.

      2. Lateral: F2 reduced to ~1100 Hz.
         Lateral airflow around the tongue
         sides lowers F2 relative to central
         approximants at the same place.
         The formant bank targets model this.

    Both must be present simultaneously.
    If only the lateral: plain [l], not [ɭ].
    If only the retroflex: [ɻ̩], not [ɭ].
    The combination is the phoneme.
    """
    n_ms  = VS_LL_DUR_MS * dil
    n     = int(n_ms / 1000.0 * sr)
    src   = rosenberg_pulse(n, pitch_hz,
                            oq=0.65, sr=sr)
    on_n  = int(VS_LL_COART_ON * n)
    off_n = int(VS_LL_COART_OFF * n)

    f_mean = list(VS_LL_F)
    if F_prev is not None and on_n > 0:
        for k in range(min(len(F_prev),
                           len(VS_LL_F))):
            f_mean[k] = (F_prev[k] * 0.15
                         + VS_LL_F[k] * 0.85)
    if F_next is not None and off_n > 0:
        for k in range(min(len(F_next),
                           len(VS_LL_F))):
            f_mean[k] = (f_mean[k] * 0.85
                         + F_next[k] * 0.15)

    out = apply_formants(src, f_mean,
                         VS_LL_B, VS_LL_GAINS,
                         sr=sr)
    # Apply mūrdhanya F3 notch
    # The retroflex tongue curl depresses F3.
    # This is the same physics as [ɻ̩] —
    # different manner (lateral vs central)
    # but same place (mūrdhanya).
    out = iir_notch(out,
                    VS_LL_F3_NOTCH,
                    VS_LL_F3_NOTCH_BW,
                    sr=sr)
    mx  = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.65
    return f32(out)


def synth_EE(F_prev=None, F_next=None,
             pitch_hz=PITCH_HZ,
             dil=DIL, sr=SR):
    """
    [eː] — long close-mid front unrounded.
    Śikṣā: tālavya.
    Sanskrit [e] is always long.
    Mid front — between [i] and [ɑ].
    F1 above [i], below [ɑ].
    F2 below [i], above [ɑ].
    """
    n_ms  = VS_EE_DUR_MS * dil
    n     = int(n_ms / 1000.0 * sr)
    src   = rosenberg_pulse(n, pitch_hz,
                            oq=0.65, sr=sr)
    on_n  = int(VS_EE_COART_ON * n)
    off_n = int(VS_EE_COART_OFF * n)

    f_mean = list(VS_EE_F)
    if F_prev is not None and on_n > 0:
        for k in range(min(len(F_prev),
                           len(VS_EE_F))):
            f_mean[k] = (F_prev[k] * 0.10
                         + VS_EE_F[k] * 0.90)
    if F_next is not None and off_n > 0:
        for k in range(min(len(F_next),
                           len(VS_EE_F))):
            f_mean[k] = (f_mean[k] * 0.90
                         + F_next[k] * 0.10)

    out = apply_formants(src, f_mean,
                         VS_EE_B, VS_EE_GAINS,
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


# ── WORD SYNTHESISER ────────────────────────��─────────

def synth_ile(pitch_hz=PITCH_HZ,
              dil=DIL,
              with_room=False,
              sr=SR):
    """
    ĪḶE [iːɭe]
    Rigveda 1.1.1, word 2.
    "I praise."

    Syllable structure: Ī — ḶE

    Coarticulation chain:
      II:  word-initial, F_prev=None
           coarticulates toward VS_LL_F
      LL:  coarticulates from VS_II_F
           coarticulates toward VS_EE_F
      EE:  coarticulates from VS_LL_F
           word-final, F_next=None
    """
    ii_seg = synth_II(F_prev=None,
                      F_next=VS_LL_F,
                      pitch_hz=pitch_hz,
                      dil=dil, sr=sr)
    ll_seg = synth_LL(F_prev=VS_II_F,
                      F_next=VS_EE_F,
                      pitch_hz=pitch_hz,
                      dil=dil, sr=sr)
    ee_seg = synth_EE(F_prev=VS_LL_F,
                      F_next=None,
                      pitch_hz=pitch_hz,
                      dil=dil, sr=sr)

    word = np.concatenate(
        [ii_seg, ll_seg, ee_seg])

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
    print("Synthesising ĪḶE [iːɭe]...")

    dry  = synth_ile(with_room=False)
    hall = synth_ile(with_room=True)
    slow = ola_stretch(dry, 4.0)

    write_wav("output_play/ile_dry.wav",  dry)
    write_wav("output_play/ile_hall.wav", hall)
    write_wav("output_play/ile_slow.wav", slow)

    # Isolated phonemes
    ii_iso = synth_II(F_prev=None,
                      F_next=None)
    ll_iso = synth_LL(F_prev=None,
                      F_next=None)
    ee_iso = synth_EE(F_prev=None,
                      F_next=None)

    for sig, name in [
        (ii_iso, "ile_ii_isolated"),
        (ll_iso, "ile_ll_isolated"),
        (ee_iso, "ile_ee_isolated"),
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
    print("  output_play/ile_dry.wav")
    print("  output_play/ile_hall.wav")
    print("  output_play/ile_slow.wav")
    print("  output_play/ile_ii_isolated.wav")
    print("  output_play/ile_ii_isolated_slow.wav")
    print("  output_play/ile_ll_isolated.wav")
    print("  output_play/ile_ll_isolated_slow.wav")
    print("  output_play/ile_ee_isolated.wav")
    print("  output_play/ile_ee_isolated_slow.wav")
    print()
    print("Run ile_diagnostic.py to verify.")
