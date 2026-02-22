"""
SCEAÞENA RECONSTRUCTION
Old English: sceaþena
Meaning: of enemies (genitive plural)
IPA: [ʃeɑθenɑ]
Beowulf: Line 5, Word 3 (overall word 20)
February 2026

PHONEME STRUCTURE:
  SC  [ʃ]   voiceless postalveolar fric. — verified SCYLD
  EA  [eɑ]  short front-back diphthong   — NEW
  Þ   [θ]   voiceless dental fricative   — verified ÞĒOD-CYNINGA
  E   [e]   short close-mid front        — verified GĀR-DENA
  N   [n]   voiced alveolar nasal        — verified
  A   [ɑ]   short open back              — verified GĀR-DENA

NEW PHONEMES:
  [eɑ]: short front-back diphthong.
        OE digraph 'ea'.
        Tongue starts at [e]:
          F1 ~450 Hz, F2 ~1900 Hz
        Moves toward [ɑ]:
          F1 ~700 Hz, F2 ~1100 Hz
        Falling diphthong —
        energy front-loaded.
        Duration 80 ms total.
        The movement IS the phoneme —
        both onset and offglide
        must be present.
        Distinct from:
          [e]  — no movement
          [ɑ]  — no movement
          [eː] — long, no movement
          [eɑ] — moving, short
        Extremely frequent in OE:
        eald (old), earm (arm),
        heard (hard), bearn (child),
        feall (fall), weald (forest).
        All use these parameters.

DIPHTHONG INVENTORY UPDATE:
  Previously listed as [eo]/[eːo].
  Corrected — OE has two diphthong
  pairs:
    ea/ēa: [eɑ] / [eːɑ]
    eo/ēo: [eo] / [eːo]
  All four remain in gaps.
  This word adds [eɑ] only.
  Remaining after this word: 8.

MORPHOLOGICAL NOTE:
  sceaþena — genitive plural of
  sceaþa (enemy, injurer, harmer).
  The -ena suffix marks gen. plural
  in OE a-stem masculines.
  Meaning: of enemies, of scathers.
  Modern English 'scathe' survives
  in 'unscathed' — unhurt.
  sceaþena þreatum = in troops
  of enemies — describing the
  terror Scyld Scefing imposed.

CHANGE LOG:
  v1 — initial parameters
"""

import numpy as np
from scipy.signal import lfilter, butter
import wave as wave_module
import os

SR    = 44100
DTYPE = np.float32

os.makedirs("output_play", exist_ok=True)


# ============================================================
# PARAMETERS
# ============================================================

# SH — voiceless postalveolar fricative [ʃ]
SH_DUR_MS   = 80.0
SH_NOISE_CF = 3800.0
SH_NOISE_BW = 2400.0
SH_GAIN     = 0.30
SH_SEC_CF   = 6000.0
SH_SEC_BW   = 2000.0
SH_SEC_GAIN = 0.20

# EA — short front-back diphthong [eɑ]
# Onset [e]: F1 450, F2 1900
# Offset [ɑ]: F1 700, F2 1100
EA_DUR_MS  = 80.0
EA_F_ON    = [450.0, 1900.0, 2600.0, 3300.0]
EA_F_OFF   = [700.0, 1100.0, 2400.0, 3000.0]
EA_B       = [100.0,  130.0,  200.0,  280.0]
EA_GAINS   = [ 16.0,    8.0,    1.5,    0.5]
# Transition starts at 30% of duration
# reaches [ɑ] by 90% — glide is gradual
EA_TRANS_ON  = 0.30
EA_TRANS_OFF = 0.90

# TH — voiceless dental fricative [θ]
TH_DUR_MS   = 75.0
TH_NOISE_CF = 5000.0
TH_NOISE_BW = 3000.0
TH_GAIN     = 0.18

# E — short close-mid front [e]
E_F      = [450.0, 1900.0, 2600.0, 3300.0]
E_B      = [100.0,  130.0,  200.0,  280.0]
E_GAINS  = [ 16.0,    8.0,    1.5,    0.5]
E_DUR_MS = 55.0
E_COART_ON  = 0.12
E_COART_OFF = 0.12

# N — voiced alveolar nasal [n]
N_F      = [250.0, 1800.0, 2600.0, 3300.0]
N_B      = [100.0,  200.0,  300.0,  350.0]
N_GAINS  = [  8.0,    2.0,    0.5,    0.2]
N_DUR_MS = 65.0
N_ANTI_F = 800.0
N_ANTI_BW= 200.0

# A — short open back [ɑ]
A_F      = [700.0, 1100.0, 2500.0, 3200.0]
A_B      = [120.0,  150.0,  200.0,  280.0]
A_GAINS  = [ 16.0,    8.0,    1.5,    0.5]
A_DUR_MS = 55.0
A_COART_ON  = 0.12
A_COART_OFF = 0.12

PITCH_HZ = 145.0
DIL      = 1.0


# ============================================================
# UTILITIES
# ============================================================

def f32(x):
    return np.asarray(x, dtype=DTYPE)

def rms(sig):
    return float(np.sqrt(
        np.mean(sig.astype(float)**2)))

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
    nyq  = sr / 2.0
    lo_  = max(lo / nyq, 0.001)
    hi_  = min(hi / nyq, 0.499)
    if lo_ >= hi_:
        lo_ = max(lo_ - 0.01, 0.001)
        hi_ = min(lo_ + 0.02, 0.499)
    b, a = butter(2, [lo_, hi_], btype='band')
    return b, a

def safe_lp(fc, sr=SR):
    nyq = sr / 2.0
    fc_ = min(fc / nyq, 0.499)
    b, a = butter(2, fc_, btype='low')
    return b, a

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
        frame = (sig[in_pos:in_pos+win_n]
                 * window)
        out [out_pos:out_pos+win_n] += frame
        norm[out_pos:out_pos+win_n] += window
    nz       = norm > 1e-8
    out[nz] /= norm[nz]
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.75
    return f32(out)


# ============================================================
# ROSENBERG PULSE
# ============================================================

def rosenberg_pulse(n_samples, pitch_hz,
                    oq=0.65, sr=SR):
    T     = 1.0 / sr
    phase = 0.0
    src   = np.zeros(n_samples, dtype=DTYPE)
    for i in range(n_samples):
        phase += pitch_hz * T
        if phase >= 1.0:
            phase -= 1.0
        if phase < oq:
            src[i] = ((phase / oq)
                      * (2 - phase / oq))
        else:
            src[i] = (1 - (phase - oq)
                      / (1 - oq + 1e-9))
    return f32(np.diff(src, prepend=src[0]))


# ============================================================
# FORMANT FILTERS
# ============================================================

def apply_formants(src, freqs, bws, gains,
                   sr=SR):
    T      = 1.0 / sr
    n      = len(src)
    result = np.zeros(n, dtype=DTYPE)
    for fi in range(len(freqs)):
        fc = float(freqs[fi])
        bw = float(bws[fi])
        g  = float(gains[fi])
        a2 = -np.exp(-2 * np.pi * bw * T)
        a1 =  2 * np.exp(-np.pi * bw * T) \
               * np.cos(2 * np.pi * fc * T)
        b0 = 1.0 - a1 - a2
        y1 = y2 = 0.0
        out = np.zeros(n, dtype=DTYPE)
        for i in range(n):
            y      = (b0 * float(src[i])
                      + a1 * y1 + a2 * y2)
            y2     = y1
            y1     = y
            out[i] = y
        result += out * g
    return f32(result)


# ============================================================
# IIR NOTCH
# ============================================================

def iir_notch(sig, fc, bw=200.0, sr=SR):
    T  = 1.0 / sr
    wc = 2 * np.pi * fc * T
    r  = float(np.clip(
        1.0 - np.pi * bw * T, 0.1, 0.999))
    b1 = -2.0 * np.cos(wc)
    b2 =  1.0
    a1 = -2.0 * r * np.cos(wc)
    a2 =  r * r
    gain_dc = abs((1 + b1 + b2)
                  / (1 + a1 + a2 + 1e-12))
    if gain_dc > 1e-6:
        b1_n = b1 / gain_dc
        b2_n = b2 / gain_dc
    else:
        b1_n = b1
        b2_n = b2
    b0  = 1.0
    n   = len(sig)
    out = np.zeros(n, dtype=DTYPE)
    x   = sig.astype(float)
    y1 = y2 = x1 = x2 = 0.0
    for i in range(n):
        xi     = x[i]
        yi     = (b0 * xi + b1_n * x1
                  + b2_n * x2
                  - a1 * y1 - a2 * y2)
        x2     = x1
        x1     = xi
        y2     = y1
        y1     = yi
        out[i] = yi
    return f32(out)


# ============================================================
# PHONEME SYNTHESIZERS
# ============================================================

def synth_SH(F_next=None, dil=DIL, sr=SR):
    dur_ms = SH_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    noise  = np.random.randn(n_s).astype(float)
    lo1    = max(SH_NOISE_CF - SH_NOISE_BW/2,
                 200.0)
    hi1    = min(SH_NOISE_CF + SH_NOISE_BW/2,
                 sr * 0.48)
    b1, a1 = safe_bp(lo1, hi1, sr)
    fric1  = lfilter(b1, a1, noise)
    lo2    = max(SH_SEC_CF - SH_SEC_BW/2,
                 200.0)
    hi2    = min(SH_SEC_CF + SH_SEC_BW/2,
                 sr * 0.48)
    b2, a2 = safe_bp(lo2, hi2, sr)
    fric2  = lfilter(b2, a2, noise)
    fric   = (fric1 * SH_GAIN
              + fric2 * SH_SEC_GAIN)
    n_atk  = min(int(0.012 * sr), n_s // 4)
    n_dec  = min(int(0.020 * sr), n_s // 4)
    env    = np.ones(n_s, dtype=float)
    if n_atk < n_s:
        env[:n_atk] = np.linspace(
            0.0, 1.0, n_atk)
    if n_dec < n_s:
        env[-n_dec:] = np.linspace(
            1.0, 0.3, n_dec)
    fric   = f32(fric * env)
    mx     = np.max(np.abs(fric))
    if mx > 1e-8:
        fric = f32(fric / mx * 0.45)
    return f32(fric)


def synth_EA(F_prev=None, F_next=None,
              pitch_hz=PITCH_HZ,
              dil=DIL, sr=SR):
    """
    Short front-back diphthong [eɑ].
    OE digraph 'ea'.
    Formants move continuously from
    [e] onset to [ɑ] offset.
    Transition begins at 30% duration,
    completes at 90% duration.
    The movement is the phoneme —
    onset and offglide both required.
    Distinct from pure [e] (no movement)
    and pure [ɑ] (no movement).

    F2 trajectory:
      onset:  ~1900 Hz  (front [e])
      offset: ~1100 Hz  (back [ɑ])
      delta:  ~800 Hz falling

    F1 trajectory:
      onset:  ~450 Hz   (mid-close)
      offset: ~700 Hz   (open)
      delta:  ~250 Hz rising
    """
    dur_ms = EA_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    T      = 1.0 / sr
    src    = rosenberg_pulse(n_s, pitch_hz,
                              oq=0.65, sr=sr)
    # Amplitude envelope
    n_atk  = min(int(0.010 * sr), n_s // 4)
    n_rel  = min(int(0.020 * sr), n_s // 4)
    env    = np.ones(n_s, dtype=DTYPE)
    if n_atk < n_s:
        env[:n_atk] = np.linspace(
            0.4, 1.0, n_atk)
    if n_rel < n_s:
        env[-n_rel:] = np.linspace(
            1.0, 0.6, n_rel)
    src    = f32(src * env)
    # Transition indices
    i_trans_on  = int(EA_TRANS_ON  * n_s)
    i_trans_off = int(EA_TRANS_OFF * n_s)
    n_trans     = max(1,
                      i_trans_off - i_trans_on)
    result = np.zeros(n_s, dtype=DTYPE)
    for fi in range(len(EA_F_ON)):
        f_on  = float(EA_F_ON[fi])
        f_off = float(EA_F_OFF[fi])
        bw    = float(EA_B[fi])
        g     = float(EA_GAINS[fi])
        # Build per-sample formant trajectory
        f_arr = np.full(n_s, f_on, dtype=DTYPE)
        # Steady onset up to transition
        # start
        if i_trans_on > 0:
            f_arr[:i_trans_on] = f_on
        # Linear transition
        if i_trans_off <= n_s:
            f_arr[i_trans_on:i_trans_off] = \
                np.linspace(f_on, f_off,
                             n_trans)
        # Steady offset after transition
        if i_trans_off < n_s:
            f_arr[i_trans_off:] = f_off
        # Apply time-varying formant filter
        y1 = y2 = 0.0
        out = np.zeros(n_s, dtype=DTYPE)
        for i in range(n_s):
            fc  = max(20.0, min(
                sr * 0.48,
                float(f_arr[i])))
            a2_ = -np.exp(-2*np.pi*bw*T)
            a1_ =  2*np.exp(-np.pi*bw*T) \
                   * np.cos(2*np.pi*fc*T)
            b0_ = 1.0 - a1_ - a2_
            yy  = (b0_ * float(src[i])
                   + a1_ * y1 + a2_ * y2)
            y2  = y1
            y1  = yy
            out[i] = yy
        result += out * g
    mx = np.max(np.abs(result))
    if mx > 1e-8:
        result = f32(result / mx * 0.68)
    return f32(result)


def synth_TH(F_prev=None, F_next=None,
              dil=DIL, sr=SR):
    """
    Voiceless dental fricative [θ].
    Tongue tip at upper teeth.
    Low-amplitude diffuse noise.
    Centroid ~5000 Hz — between
    [s] (~7600) and [ʃ] (~4700).
    """
    dur_ms = TH_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    noise  = np.random.randn(n_s).astype(float)
    lo_    = max(TH_NOISE_CF - TH_NOISE_BW/2,
                 200.0)
    hi_    = min(TH_NOISE_CF + TH_NOISE_BW/2,
                 sr * 0.48)
    b_bp, a_bp = safe_bp(lo_, hi_, sr)
    fric   = lfilter(b_bp, a_bp, noise)
    n_atk  = min(int(0.010 * sr), n_s // 4)
    n_dec  = min(int(0.015 * sr), n_s // 4)
    env    = np.ones(n_s, dtype=float)
    if n_atk < n_s:
        env[:n_atk] = np.linspace(
            0.0, 1.0, n_atk)
    if n_dec < n_s:
        env[-n_dec:] = np.linspace(
            1.0, 0.0, n_dec)
    fric   = f32(fric * env * TH_GAIN)
    mx     = np.max(np.abs(fric))
    if mx > 1e-8:
        fric = f32(fric / mx * 0.35)
    return f32(fric)


def synth_E(F_prev=None, F_next=None,
             pitch_hz=PITCH_HZ,
             dil=DIL, sr=SR):
    dur_ms = E_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    T      = 1.0 / sr
    src    = rosenberg_pulse(n_s, pitch_hz,
                              oq=0.65, sr=sr)
    n_atk  = min(int(0.010 * sr), n_s // 4)
    n_rel  = min(int(0.015 * sr), n_s // 4)
    env    = np.ones(n_s, dtype=DTYPE)
    if n_atk < n_s:
        env[:n_atk] = np.linspace(
            0.4, 1.0, n_atk)
    if n_rel < n_s:
        env[-n_rel:] = np.linspace(
            1.0, 0.5, n_rel)
    src    = f32(src * env)
    n_on   = int(E_COART_ON  * n_s)
    n_off  = int(E_COART_OFF * n_s)
    f_prev = F_prev if F_prev is not None \
             else E_F
    f_next = F_next if F_next is not None \
             else E_F
    result = np.zeros(n_s, dtype=DTYPE)
    for fi in range(len(E_F)):
        f_s   = (float(f_prev[fi])
                 if fi < len(f_prev)
                 else float(E_F[fi]))
        f_e   = (float(f_next[fi])
                 if fi < len(f_next)
                 else float(E_F[fi]))
        f_b   = float(E_F[fi])
        f_arr = np.full(n_s, f_b, dtype=DTYPE)
        if n_on > 0:
            f_arr[:n_on] = np.linspace(
                f_s, f_b, n_on)
        if n_off > 0:
            f_arr[-n_off:] = np.linspace(
                f_b, f_e, n_off)
        bw  = float(E_B[fi])
        g   = float(E_GAINS[fi])
        y1 = y2 = 0.0
        out = np.zeros(n_s, dtype=DTYPE)
        for i in range(n_s):
            fc  = max(20.0, min(
                sr * 0.48, float(f_arr[i])))
            a2_ = -np.exp(-2*np.pi*bw*T)
            a1_ =  2*np.exp(-np.pi*bw*T) \
                   * np.cos(2*np.pi*fc*T)
            b0_ = 1.0 - a1_ - a2_
            yy  = (b0_ * float(src[i])
                   + a1_ * y1 + a2_ * y2)
            y2  = y1
            y1  = yy
            out[i] = yy
        result += out * g
    mx = np.max(np.abs(result))
    if mx > 1e-8:
        result = f32(result / mx * 0.68)
    return f32(result)


def synth_N(F_prev=None, F_next=None,
             pitch_hz=PITCH_HZ,
             dil=DIL, sr=SR):
    dur_ms = N_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    src    = rosenberg_pulse(n_s, pitch_hz,
                              oq=0.65, sr=sr)
    n_tr   = min(int(0.020 * sr), n_s // 4)
    env    = np.ones(n_s, dtype=DTYPE)
    if n_tr < n_s:
        env[:n_tr]  = np.linspace(
            0.3, 1.0, n_tr)
        env[-n_tr:] = np.linspace(
            1.0, 0.3, n_tr)
    src    = f32(src * env)
    result = apply_formants(
        src, N_F, N_B, N_GAINS, sr=sr)
    result = iir_notch(
        result, fc=N_ANTI_F,
        bw=N_ANTI_BW, sr=sr)
    mx = np.max(np.abs(result))
    if mx > 1e-8:
        result = f32(result / mx * 0.55)
    return f32(result)


def synth_A(F_prev=None, F_next=None,
             pitch_hz=PITCH_HZ,
             dil=DIL, sr=SR):
    dur_ms = A_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    T      = 1.0 / sr
    src    = rosenberg_pulse(n_s, pitch_hz,
                              oq=0.65, sr=sr)
    n_atk  = min(int(0.010 * sr), n_s // 4)
    n_rel  = min(int(0.015 * sr), n_s // 4)
    env    = np.ones(n_s, dtype=DTYPE)
    if n_atk < n_s:
        env[:n_atk] = np.linspace(
            0.4, 1.0, n_atk)
    if n_rel < n_s:
        env[-n_rel:] = np.linspace(
            1.0, 0.5, n_rel)
    src    = f32(src * env)
    n_on   = int(A_COART_ON  * n_s)
    n_off  = int(A_COART_OFF * n_s)
    f_prev = F_prev if F_prev is not None \
             else A_F
    f_next = F_next if F_next is not None \
             else A_F
    result = np.zeros(n_s, dtype=DTYPE)
    for fi in range(len(A_F)):
        f_s   = (float(f_prev[fi])
                 if fi < len(f_prev)
                 else float(A_F[fi]))
        f_e   = (float(f_next[fi])
                 if fi < len(f_next)
                 else float(A_F[fi]))
        f_b   = float(A_F[fi])
        f_arr = np.full(n_s, f_b, dtype=DTYPE)
        if n_on > 0:
            f_arr[:n_on] = np.linspace(
                f_s, f_b, n_on)
        if n_off > 0:
            f_arr[-n_off:] = np.linspace(
                f_b, f_e, n_off)
        bw  = float(A_B[fi])
        g   = float(A_GAINS[fi])
        y1 = y2 = 0.0
        out = np.zeros(n_s, dtype=DTYPE)
        for i in range(n_s):
            fc  = max(20.0, min(
                sr * 0.48, float(f_arr[i])))
            a2_ = -np.exp(-2*np.pi*bw*T)
            a1_ =  2*np.exp(-np.pi*bw*T) \
                   * np.cos(2*np.pi*fc*T)
            b0_ = 1.0 - a1_ - a2_
            yy  = (b0_ * float(src[i])
                   + a1_ * y1 + a2_ * y2)
            y2  = y1
            y1  = yy
            out[i] = yy
        result += out * g
    mx = np.max(np.abs(result))
    if mx > 1e-8:
        result = f32(result / mx * 0.68)
    return f32(result)


def apply_simple_room(sig, rt60=2.0,
                       direct_ratio=0.42,
                       sr=SR):
    d1  = int(0.021 * sr)
    d2  = int(0.035 * sr)
    d3  = int(0.051 * sr)
    g   = 10 ** (-3.0 / (rt60 * sr))
    rev = np.zeros(len(sig) + d3 + 1,
                   dtype=float)
    for i, s in enumerate(sig.astype(float)):
        rev[i] += s
        if i + d1 < len(rev):
            rev[i+d1] += s * g * 0.6
        if i + d2 < len(rev):
            rev[i+d2] += s * g * 0.4
        if i + d3 < len(rev):
            rev[i+d3] += s * g * 0.25
    rev = rev[:len(sig)]
    mix = (direct_ratio * sig.astype(float)
           + (1 - direct_ratio) * rev)
    mx  = np.max(np.abs(mix))
    if mx > 1e-8:
        mix = mix / mx * 0.75
    return f32(mix)


# ============================================================
# FULL WORD
# ============================================================

def synth_sceathena(pitch_hz=PITCH_HZ,
                     dil=DIL,
                     add_room=False,
                     sr=SR):
    """[ʃ·eɑ·θ·e·n·ɑ]"""
    sh_seg = synth_SH(
        F_next=EA_F_ON, dil=dil, sr=sr)
    ea_seg = synth_EA(
        F_prev=None, F_next=None,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    th_seg = synth_TH(
        F_prev=EA_F_OFF, F_next=E_F,
        dil=dil, sr=sr)
    e_seg  = synth_E(
        F_prev=E_F, F_next=N_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    n_seg  = synth_N(
        F_prev=E_F, F_next=A_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    a_seg  = synth_A(
        F_prev=N_F, F_next=None,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    word   = np.concatenate([
        sh_seg, ea_seg, th_seg,
        e_seg,  n_seg,  a_seg])
    mx     = np.max(np.abs(word))
    if mx > 1e-8:
        word = f32(word / mx * 0.75)
    if add_room:
        word = apply_simple_room(
            word, rt60=2.0,
            direct_ratio=0.38, sr=sr)
    return f32(word)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print()
    print("SCEAÞENA RECONSTRUCTION v1")
    print("Old English [ʃeɑθenɑ]")
    print("Beowulf line 5, word 3")
    print()

    w_dry = synth_sceathena(
        pitch_hz=145.0, dil=1.0,
        add_room=False)
    write_wav(
        "output_play/sceathena_dry.wav",
        w_dry, SR)
    print(f"  sceathena_dry.wav"
          f"  ({len(w_dry)/SR*1000:.0f} ms)")

    w_hall = synth_sceathena(
        pitch_hz=145.0, dil=1.0,
        add_room=True)
    write_wav(
        "output_play/sceathena_hall.wav",
        w_hall, SR)
    print("  sceathena_hall.wav")

    w_slow = ola_stretch(w_dry, 4.0)
    write_wav(
        "output_play/sceathena_slow.wav",
        w_slow, SR)
    print("  sceathena_slow.wav")

    w_perf = synth_sceathena(
        pitch_hz=110.0, dil=2.5,
        add_room=True)
    write_wav(
        "output_play/sceathena_performance.wav",
        w_perf, SR)
    print(f"  sceathena_performance.wav"
          f"  ({len(w_perf)/SR*1000:.0f} ms)")

    # EA diphthong isolated
    ea_seg = synth_EA(None, None,
                       145.0, 1.0, SR)
    write_wav(
        "output_play/sceathena_ea_only.wav",
        ola_stretch(ea_seg / (
            np.max(np.abs(ea_seg))+1e-8)
            * 0.75, 4.0), SR)
    print("  sceathena_ea_only.wav  (4x slow)")
    print()
    print("  afplay output_play/"
          "sceathena_ea_only.wav")
    print("  afplay output_play/"
          "sceathena_dry.wav")
    print("  afplay output_play/"
          "sceathena_slow.wav")
    print("  afplay output_play/"
          "sceathena_hall.wav")
    print()
    print("  Line 5 in progress:")
    print("  Scyld Scefing"
          " sceaþena þreatum")
    print()
