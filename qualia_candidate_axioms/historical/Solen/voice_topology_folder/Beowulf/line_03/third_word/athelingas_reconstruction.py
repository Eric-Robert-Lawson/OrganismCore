"""
ÆÞELINGAS RECONSTRUCTION
Old English: æþelingas
Meaning: princes, noblemen (nom. plural)
IPA: [æθeliŋɡɑs]
Beowulf: Line 3, Word 3 (overall word 11)
February 2026

PHONEME STRUCTURE:
  Æ   [æ]   open front unrounded      — verified HWÆT
  Þ   [θ]   voiceless dental fric.    — verified ÞĒOD-CYNINGA
  E   [e]   short close-mid front     — verified GĀR-DENA
  L   [l]   voiced alveolar lateral   — NEW
  I   [ɪ]   short near-close front    — verified IN
  N   [n]   voiced alveolar nasal     — verified
  G   [ɡ]   voiced velar stop         — verified GĀR-DENA
  A   [ɑ]   short open back           — verified
  S   [s]   voiceless alveolar fric.  — NEW

NEW PHONEMES:
  [l]: voiced alveolar lateral approximant.
       Tongue tip at alveolar ridge.
       Air flows around sides of tongue.
       Fully voiced — no frication, no burst.
       Acoustic signature:
         F1 low (~300–350 Hz)
         F2 mid (~900–1100 Hz) — lower than
           most vowels
         F3 low (~2400–2600 Hz) — pulled
           down from typical ~3000 Hz
         Antiformant ~1800–2000 Hz from
           lateral air path geometry
       Duration ~65 ms.
       Modern English [l] is identical.

  [s]: voiceless alveolar fricative.
       Tongue tip near alveolar ridge.
       Narrow groove, high-velocity air.
       Highest centroid of all fricatives
       — ~6000–8000 Hz.
       Shortest front cavity of any
       fricative — most anterior
       constriction → highest resonance.
       Centroid hierarchy complete:
       [x] < [θ] < [f] < [s]
       velar < dental < labiodental
         < alveolar
       Duration ~80 ms word-final.
       No voicing.

REUSED PHONEMES:
  [æ]:  HWÆT
  [θ]:  ÞĒOD-CYNINGA, ÞRYM
  [e]:  GĀR-DENA, GEFRŪNON
  [ɪ]:  IN, GĒAR-DAGUM
  [n]:  multiple
  [ɡ]:  GĀR-DENA, GĒAR-DAGUM
  [ɑ]:  multiple

MORPHOLOGICAL NOTE:
  æþeling — nobleman, prince
  Root: æþel — noble, ancestral
  -ing suffix: one who belongs to
  -as suffix: nominative plural
  æþelingas: the princes (subject form)
  The word survives as the place name
  Athelney (OE æþelingas-ēg —
  island of the princes) where
  Alfred the Great hid from the Vikings.

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

# AE — open front unrounded [æ]
AE_F      = [700.0, 1700.0, 2600.0, 3300.0]
AE_B      = [130.0,  120.0,  200.0,  280.0]
AE_GAINS  = [ 18.0,    8.0,    1.5,    0.5]
AE_DUR_MS = 65.0
AE_COART_ON  = 0.12
AE_COART_OFF = 0.12

# TH — voiceless dental fricative [θ]
TH_DUR_MS   = 70.0
TH_NOISE_CF = 4200.0
TH_NOISE_BW = 2500.0
TH_GAIN     = 0.28

# E — short close-mid front [e]
E_F      = [370.0, 2100.0, 2800.0, 3300.0]
E_B      = [ 80.0,  120.0,  170.0,  240.0]
E_GAINS  = [ 18.0,    9.0,    1.5,    0.5]
E_DUR_MS = 60.0
E_COART_ON  = 0.12
E_COART_OFF = 0.12

# L — voiced alveolar lateral [l]
# Tongue tip at alveolar ridge.
# Air around sides — lateral formant
# pattern: low F1, mid F2, low F3,
# antiformant ~1900 Hz.
L_F       = [300.0,  950.0, 2500.0, 3200.0]
L_B       = [100.0,  200.0,  300.0,  350.0]
L_GAINS   = [ 10.0,    6.0,    2.0,    0.5]
L_DUR_MS  = 65.0
L_ANTI_F  = 1900.0   # lateral antiformant
L_ANTI_BW = 300.0

# II — short near-close front [ɪ]
II_F      = [390.0, 1900.0, 2500.0, 3200.0]
II_B      = [ 90.0,  120.0,  180.0,  250.0]
II_GAINS  = [ 16.0,    8.0,    1.5,    0.5]
II_DUR_MS = 55.0
II_COART_ON  = 0.12
II_COART_OFF = 0.12

# N — voiced alveolar nasal [n]
N_F       = [250.0, 1800.0, 2600.0, 3300.0]
N_B       = [100.0,  200.0,  300.0,  350.0]
N_GAINS   = [  8.0,    2.0,    0.5,    0.2]
N_DUR_MS  = 65.0
N_ANTI_F  = 800.0
N_ANTI_BW = 200.0

# G — voiced velar stop [ɡ]
G_DUR_MS  = 75.0
G_BURST_F = 1400.0
G_BURST_BW= 600.0
G_BURST_MS= 12.0
G_VOT_MS  = 8.0

# A — short open back [ɑ]
A_F      = [700.0, 1100.0, 2500.0, 3300.0]
A_B      = [130.0,  120.0,  200.0,  280.0]
A_GAINS  = [ 16.0,    6.0,    1.2,    0.4]
A_DUR_MS = 65.0
A_COART_ON  = 0.12
A_COART_OFF = 0.12

# S — voiceless alveolar fricative [s]
# Highest centroid of all fricatives.
# Narrow groove at alveolar ridge.
# Shortest front cavity — highest resonance.
S_DUR_MS   = 80.0
S_NOISE_CF = 7000.0   # high alveolar centroid
S_NOISE_BW = 4000.0   # broad high-freq noise
S_GAIN     = 0.32
# Alveolar groove resonance:
S_GROOVE_CF = 8000.0
S_GROOVE_BW = 3000.0

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
# ROSENBERG PULSES
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

def apply_formants_trajectory(src,
                               f_start, f_end,
                               bws, gains,
                               sr=SR):
    T   = 1.0 / sr
    n   = len(src)
    result = np.zeros(n, dtype=DTYPE)
    for fi in range(len(f_start)):
        f_arr = np.linspace(
            float(f_start[fi]),
            float(f_end[fi]),
            n, dtype=DTYPE)
        bw = float(bws[fi])
        g  = float(gains[fi])
        y1 = y2 = 0.0
        out = np.zeros(n, dtype=DTYPE)
        for i in range(n):
            fc  = max(20.0, min(
                sr * 0.48, float(f_arr[i])))
            a2  = -np.exp(-2*np.pi*bw*T)
            a1  =  2*np.exp(-np.pi*bw*T) \
                   * np.cos(2*np.pi*fc*T)
            b0  = 1.0 - a1 - a2
            y   = (b0 * float(src[i])
                   + a1 * y1 + a2 * y2)
            y2  = y1
            y1  = y
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

def synth_AE(F_prev=None, F_next=None,
              pitch_hz=PITCH_HZ,
              dil=DIL, sr=SR):
    dur_ms = AE_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    T      = 1.0 / sr
    src    = rosenberg_pulse(n_s, pitch_hz,
                              oq=0.65, sr=sr)
    n_atk  = min(int(0.012 * sr), n_s // 4)
    n_rel  = min(int(0.020 * sr), n_s // 4)
    env    = np.ones(n_s, dtype=DTYPE)
    if n_atk < n_s:
        env[:n_atk] = np.linspace(
            0.4, 1.0, n_atk)
    if n_rel < n_s:
        env[-n_rel:] = np.linspace(
            1.0, 0.5, n_rel)
    src    = f32(src * env)
    n_on   = int(AE_COART_ON  * n_s)
    n_off  = int(AE_COART_OFF * n_s)
    f_prev = F_prev if F_prev is not None \
             else AE_F
    f_next = F_next if F_next is not None \
             else AE_F
    result = np.zeros(n_s, dtype=DTYPE)
    for fi in range(len(AE_F)):
        f_s   = (float(f_prev[fi])
                 if fi < len(f_prev)
                 else float(AE_F[fi]))
        f_e   = (float(f_next[fi])
                 if fi < len(f_next)
                 else float(AE_F[fi]))
        f_b   = float(AE_F[fi])
        f_arr = np.full(n_s, f_b, dtype=DTYPE)
        if n_on > 0:
            f_arr[:n_on] = np.linspace(
                f_s, f_b, n_on)
        if n_off > 0:
            f_arr[-n_off:] = np.linspace(
                f_b, f_e, n_off)
        bw  = float(AE_B[fi])
        g   = float(AE_GAINS[fi])
        y1 = y2 = 0.0
        out = np.zeros(n_s, dtype=DTYPE)
        for i in range(n_s):
            fc  = max(20.0, min(
                sr * 0.48, float(f_arr[i])))
            a2  = -np.exp(-2*np.pi*bw*T)
            a1  =  2*np.exp(-np.pi*bw*T) \
                   * np.cos(2*np.pi*fc*T)
            b0  = 1.0 - a1 - a2
            y   = (b0 * float(src[i])
                   + a1 * y1 + a2 * y2)
            y2  = y1
            y1  = y
            out[i] = y
        result += out * g
    mx = np.max(np.abs(result))
    if mx > 1e-8:
        result = f32(result / mx * 0.70)
    return f32(result)


def synth_TH(F_next=None, dil=DIL, sr=SR):
    dur_ms = TH_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    noise  = np.random.randn(n_s).astype(float)
    b, a   = safe_bp(
        TH_NOISE_CF - TH_NOISE_BW / 2,
        min(TH_NOISE_CF + TH_NOISE_BW / 2,
            sr * 0.48), sr)
    fric   = lfilter(b, a, noise)
    n_atk  = min(int(0.015 * sr), n_s // 4)
    n_dec  = min(int(0.015 * sr), n_s // 4)
    env    = np.ones(n_s, dtype=float)
    if n_atk < n_s:
        env[:n_atk] = np.linspace(
            0.0, 1.0, n_atk)
    if n_dec < n_s:
        env[-n_dec:] = np.linspace(
            1.0, 0.3, n_dec)
    fric   = f32(fric * env * TH_GAIN)
    mx     = np.max(np.abs(fric))
    if mx > 1e-8:
        fric = f32(fric / mx * 0.42)
    return f32(fric)


def synth_E_short(F_prev=None, F_next=None,
                   pitch_hz=PITCH_HZ,
                   dil=DIL, sr=SR):
    dur_ms = E_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    T      = 1.0 / sr
    src    = rosenberg_pulse(n_s, pitch_hz,
                              oq=0.65, sr=sr)
    n_atk  = min(int(0.012 * sr), n_s // 4)
    n_rel  = min(int(0.020 * sr), n_s // 4)
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
            a2  = -np.exp(-2*np.pi*bw*T)
            a1  =  2*np.exp(-np.pi*bw*T) \
                   * np.cos(2*np.pi*fc*T)
            b0  = 1.0 - a1 - a2
            y   = (b0 * float(src[i])
                   + a1 * y1 + a2 * y2)
            y2  = y1
            y1  = y
            out[i] = y
        result += out * g
    mx = np.max(np.abs(result))
    if mx > 1e-8:
        result = f32(result / mx * 0.70)
    return f32(result)


def synth_L(F_prev=None, F_next=None,
             pitch_hz=PITCH_HZ,
             dil=DIL, sr=SR):
    """
    Voiced alveolar lateral approximant [l].
    Tongue tip at alveolar ridge.
    Air flows around sides.
    Lateral antiformant ~1900 Hz.
    F3 pulled low (~2500 Hz).
    """
    dur_ms = L_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    T      = 1.0 / sr
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
        src, L_F, L_B, L_GAINS, sr=sr)
    # Lateral antiformant — air path geometry
    result = iir_notch(
        result, fc=L_ANTI_F,
        bw=L_ANTI_BW, sr=sr)
    mx = np.max(np.abs(result))
    if mx > 1e-8:
        result = f32(result / mx * 0.60)
    return f32(result)


def synth_II(F_prev=None, F_next=None,
              pitch_hz=PITCH_HZ,
              dil=DIL, sr=SR):
    dur_ms = II_DUR_MS * dil
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
    n_on   = int(II_COART_ON  * n_s)
    n_off  = int(II_COART_OFF * n_s)
    f_prev = F_prev if F_prev is not None \
             else II_F
    f_next = F_next if F_next is not None \
             else II_F
    result = np.zeros(n_s, dtype=DTYPE)
    for fi in range(len(II_F)):
        f_s   = (float(f_prev[fi])
                 if fi < len(f_prev)
                 else float(II_F[fi]))
        f_e   = (float(f_next[fi])
                 if fi < len(f_next)
                 else float(II_F[fi]))
        f_b   = float(II_F[fi])
        f_arr = np.full(n_s, f_b, dtype=DTYPE)
        if n_on > 0:
            f_arr[:n_on] = np.linspace(
                f_s, f_b, n_on)
        if n_off > 0:
            f_arr[-n_off:] = np.linspace(
                f_b, f_e, n_off)
        bw  = float(II_B[fi])
        g   = float(II_GAINS[fi])
        y1 = y2 = 0.0
        out = np.zeros(n_s, dtype=DTYPE)
        for i in range(n_s):
            fc  = max(20.0, min(
                sr * 0.48, float(f_arr[i])))
            a2  = -np.exp(-2*np.pi*bw*T)
            a1  =  2*np.exp(-np.pi*bw*T) \
                   * np.cos(2*np.pi*fc*T)
            b0  = 1.0 - a1 - a2
            y   = (b0 * float(src[i])
                   + a1 * y1 + a2 * y2)
            y2  = y1
            y1  = y
            out[i] = y
        result += out * g
    mx = np.max(np.abs(result))
    if mx > 1e-8:
        result = f32(result / mx * 0.65)
    return f32(result)


def synth_N(F_prev=None, F_next=None,
             pitch_hz=PITCH_HZ,
             dil=DIL, sr=SR):
    dur_ms = N_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    T      = 1.0 / sr
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


def synth_G(F_prev=None, F_next=None,
             pitch_hz=PITCH_HZ,
             dil=DIL, sr=SR):
    dur_ms    = G_DUR_MS * dil
    n_s       = max(4, int(dur_ms / 1000.0 * sr))
    n_burst   = max(2, int(G_BURST_MS / 1000.0 * sr))
    n_vot     = max(2, int(G_VOT_MS   / 1000.0 * sr))
    n_closure = max(2, n_s - n_burst - n_vot)
    T         = 1.0 / sr
    # Closure — voiced murmur
    src_c  = rosenberg_pulse(
        n_closure, pitch_hz, oq=0.65, sr=sr)
    env_c  = np.linspace(0.1, 0.3,
                          n_closure).astype(DTYPE)
    b_lp, a_lp = safe_lp(300.0, sr)
    murmur = f32(lfilter(b_lp, a_lp,
                          src_c.astype(float))
                 * env_c * 0.3)
    # Burst
    noise  = np.random.randn(n_burst).astype(float)
    b_bp, a_bp = safe_bp(
        G_BURST_F - G_BURST_BW / 2,
        G_BURST_F + G_BURST_BW / 2, sr)
    burst  = f32(lfilter(b_bp, a_bp, noise)
                 * 0.6)
    # VOT — short voiced transition
    src_v  = rosenberg_pulse(
        n_vot, pitch_hz, oq=0.65, sr=sr)
    vot    = apply_formants(
        src_v,
        F_next if F_next is not None else A_F,
        [100.0, 150.0, 200.0, 280.0],
        [14.0, 7.0, 1.2, 0.4], sr=sr)
    vot    = f32(vot * 0.5)
    seg    = np.concatenate([murmur, burst, vot])
    mx     = np.max(np.abs(seg))
    if mx > 1e-8:
        seg = f32(seg / mx * 0.65)
    return f32(seg)


def synth_A_short(F_prev=None, F_next=None,
                   pitch_hz=PITCH_HZ,
                   dil=DIL, sr=SR):
    dur_ms = A_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    T      = 1.0 / sr
    src    = rosenberg_pulse(n_s, pitch_hz,
                              oq=0.65, sr=sr)
    n_atk  = min(int(0.012 * sr), n_s // 4)
    n_rel  = min(int(0.020 * sr), n_s // 4)
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
            a2  = -np.exp(-2*np.pi*bw*T)
            a1  =  2*np.exp(-np.pi*bw*T) \
                   * np.cos(2*np.pi*fc*T)
            b0  = 1.0 - a1 - a2
            y   = (b0 * float(src[i])
                   + a1 * y1 + a2 * y2)
            y2  = y1
            y1  = y
            out[i] = y
        result += out * g
    mx = np.max(np.abs(result))
    if mx > 1e-8:
        result = f32(result / mx * 0.68)
    return f32(result)


def synth_S(F_next=None, dil=DIL, sr=SR):
    """
    Voiceless alveolar fricative [s].
    Highest centroid of all fricatives.
    Narrow groove at alveolar ridge.
    Word-final position.
    """
    dur_ms = S_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    noise  = np.random.randn(n_s).astype(float)
    # Main high-freq alveolar band
    b, a   = safe_bp(
        S_NOISE_CF - S_NOISE_BW / 2,
        min(S_NOISE_CF + S_NOISE_BW / 2,
            sr * 0.48), sr)
    fric   = lfilter(b, a, noise)
    # Groove resonance — very high
    hi_lim = min(S_GROOVE_CF + S_GROOVE_BW / 2,
                 sr * 0.48)
    lo_lim = max(S_GROOVE_CF - S_GROOVE_BW / 2,
                 100.0)
    if lo_lim < hi_lim:
        b2, a2 = safe_bp(lo_lim, hi_lim, sr)
        fric  += lfilter(b2, a2, noise) * 0.4
    n_atk  = min(int(0.010 * sr), n_s // 4)
    n_dec  = min(int(0.030 * sr), n_s // 3)
    env    = np.ones(n_s, dtype=float)
    if n_atk < n_s:
        env[:n_atk] = np.linspace(
            0.0, 1.0, n_atk)
    if n_dec < n_s:
        env[-n_dec:] = np.linspace(
            1.0, 0.0, n_dec)
    fric   = f32(fric * env * S_GAIN)
    mx     = np.max(np.abs(fric))
    if mx > 1e-8:
        fric = f32(fric / mx * 0.45)
    return f32(fric)


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

def synth_athelingas(pitch_hz=PITCH_HZ,
                      dil=DIL,
                      add_room=False,
                      sr=SR):
    """[æ·θ·e·l·ɪ·n·ɡ·ɑ·s]"""
    ae_seg = synth_AE(
        F_prev=AE_F, F_next=E_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    th_seg = synth_TH(
        F_next=E_F, dil=dil, sr=sr)
    e_seg  = synth_E_short(
        F_prev=E_F, F_next=L_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    l_seg  = synth_L(
        F_prev=E_F, F_next=II_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    ii_seg = synth_II(
        F_prev=L_F, F_next=N_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    n_seg  = synth_N(
        F_prev=II_F, F_next=A_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    g_seg  = synth_G(
        F_prev=N_F, F_next=A_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    a_seg  = synth_A_short(
        F_prev=A_F, F_next=None,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    s_seg  = synth_S(
        F_next=None, dil=dil, sr=sr)
    word = np.concatenate([
        ae_seg, th_seg, e_seg, l_seg,
        ii_seg, n_seg, g_seg, a_seg, s_seg])
    mx = np.max(np.abs(word))
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
    print("ÆÞELINGAS RECONSTRUCTION v1")
    print("Old English [æθeliŋɡɑs]")
    print("Beowulf line 3, word 3")
    print()

    w_dry = synth_athelingas(
        pitch_hz=145.0, dil=1.0,
        add_room=False)
    write_wav(
        "output_play/athelingas_dry.wav",
        w_dry, SR)
    print(f"  athelingas_dry.wav"
          f"  ({len(w_dry)/SR*1000:.0f} ms)")

    w_hall = synth_athelingas(
        pitch_hz=145.0, dil=1.0,
        add_room=True)
    write_wav(
        "output_play/athelingas_hall.wav",
        w_hall, SR)
    print("  athelingas_hall.wav")

    w_slow = ola_stretch(w_dry, 4.0)
    write_wav(
        "output_play/athelingas_slow.wav",
        w_slow, SR)
    print("  athelingas_slow.wav")

    w_perf = synth_athelingas(
        pitch_hz=110.0, dil=2.5,
        add_room=True)
    write_wav(
        "output_play/athelingas_performance.wav",
        w_perf, SR)
    print(f"  athelingas_performance.wav"
          f"  ({len(w_perf)/SR*1000:.0f} ms)")

    for name, seg in [
        ("l", synth_L(E_F, II_F,
                      145.0, 1.0, SR)),
        ("s", synth_S(None, 1.0, SR)),
    ]:
        write_wav(
            f"output_play/"
            f"athelingas_{name}_isolated.wav",
            ola_stretch(seg / (
                np.max(np.abs(seg))+1e-8)
                * 0.75, 4.0), SR)
        print(f"  athelingas_{name}"
              f"_isolated.wav  (4x slow)")

    print()
    print("  afplay output_play/"
          "athelingas_l_isolated.wav")
    print("  afplay output_play/"
          "athelingas_s_isolated.wav")
    print("  afplay output_play/"
          "athelingas_dry.wav")
    print("  afplay output_play/"
          "athelingas_slow.wav")
    print("  afplay output_play/"
          "athelingas_hall.wav")
    print()
