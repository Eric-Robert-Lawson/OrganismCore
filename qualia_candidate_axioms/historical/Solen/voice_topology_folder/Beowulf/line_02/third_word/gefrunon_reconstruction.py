"""
GEFRŪNON RECONSTRUCTION
Old English: gefrūnon
Meaning: have heard, learned (3pl perfect)
IPA: [jefrуːnon]
Beowulf: Line 2, Word 3 (overall word 8)
February 2026

PHONEME STRUCTURE:
  G   [j]   palatal approximant (glide)
  E   [e]   short close-mid front vowel
  F   [f]   voiceless labiodental fricative
  Ū   [uː]  long close back rounded vowel
  N1  [n]   voiced alveolar nasal
  O   [o]   short close-mid back rounded
  N2  [n]   voiced alveolar nasal (word-final)

NEW PHONEMES:
  [j]: palatal approximant.
       OE 'g' before front vowels = [j].
       F1 very low (~250 Hz).
       F2 very high (~2500 Hz).
       Short duration (~50 ms).
       Rapid F2 transition into following [e].
       No closure — a glide, not a stop.

  [f]: voiceless labiodental fricative.
       Lower lip to upper teeth.
       Frication centroid ~5000–6500 Hz.
       Higher than [θ] (~4000 Hz) —
       smaller, more anterior constriction.
       No voicing.

  [uː]: long close back rounded vowel.
        Same place as [u], twice the duration.
        F1 ~280 Hz, F2 ~650 Hz.
        Duration ~150 ms (phonemically long).
        Short [u] = 60 ms.
        Length distinction is phonemic in OE.

REUSED PHONEMES:
  [e]:  GĀR-DENA
  [n]:  GĀR-DENA, ÞĒOD-CYNINGA, multiple
  [o]:  ÞĒOD-CYNINGA

MORPHOLOGICAL NOTE:
  ge- prefix: perfective/completive marker.
  Root: frignan — to ask, inquire, learn.
  gefrūnon: they have learned (by asking/hearing).
  The ū is the strong verb ablaut grade —
  the root vowel changes with tense class.

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

# J — palatal approximant [j]
# OE 'g' before front vowel.
# Glide — no closure, rapid F2 transition.
# F2 starts very high, sweeps into [e].
J_F_START = [250.0, 2500.0, 3000.0, 3500.0]
J_F_END   = [370.0, 2100.0, 2800.0, 3300.0]  # → [e]
J_B       = [ 80.0,  150.0,  200.0,  280.0]
J_GAINS   = [ 12.0,    8.0,    1.5,    0.5]
J_DUR_MS  = 50.0

# E — short close-mid front [e]
# Same as GĀR-DENA
E_F      = [370.0, 2100.0, 2800.0, 3300.0]
E_B      = [ 80.0,  120.0,  170.0,  240.0]
E_GAINS  = [ 18.0,    9.0,    1.5,    0.5]
E_DUR_MS = 60.0
E_COART_ON  = 0.12
E_COART_OFF = 0.12

# F — voiceless labiodental fricative [f]
# Lower lip to upper teeth.
# Centroid higher than [θ]: smaller constriction
# at labiodental vs dental place.
F_DUR_MS   = 70.0
F_NOISE_CF = 5500.0
F_NOISE_BW = 3000.0
F_GAIN     = 0.30

# UU — long close back rounded [uː]
# Same place as [u], 2.5× duration.
# Slightly more peripheral than short [u]:
# F1 slightly lower, F2 slightly lower.
UU_F      = [280.0,  650.0, 2200.0, 3100.0]
UU_B      = [ 80.0,  100.0,  200.0,  280.0]
UU_GAINS  = [ 16.0,   12.0,    1.0,    0.3]
UU_DUR_MS = 150.0   # phonemically long
UU_COART_ON  = 0.08
UU_COART_OFF = 0.08

# N — voiced alveolar nasal [n]
# Same as all previous instances
N_F       = [250.0, 1800.0, 2600.0, 3300.0]
N_B       = [100.0,  200.0,  300.0,  350.0]
N_GAINS   = [  8.0,    2.0,    0.5,    0.2]
N_DUR_MS  = 65.0
N_ANTI_F  = 800.0
N_ANTI_BW = 200.0

# O — short close-mid back rounded [o]
# Same as ÞĒOD-CYNINGA
O_F      = [500.0,  800.0, 2400.0, 3200.0]
O_B      = [100.0,  120.0,  200.0,  280.0]
O_GAINS  = [ 18.0,   10.0,    1.2,    0.4]
O_DUR_MS = 65.0
O_COART_ON  = 0.12
O_COART_OFF = 0.12

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
        xi    = x[i]
        yi    = (b0 * xi + b1_n * x1
                 + b2_n * x2
                 - a1 * y1 - a2 * y2)
        x2    = x1
        x1    = xi
        y2    = y1
        y1    = yi
        out[i] = yi
    return f32(out)


# ============================================================
# PHONEME SYNTHESIZERS
# ============================================================

def synth_J(F_next=None,
             pitch_hz=PITCH_HZ,
             dil=DIL, sr=SR):
    """
    Palatal approximant [j].
    OE 'g' before front vowel.
    A glide — formants sweep rapidly
    from palatal position into the
    following vowel. No closure.
    F2 starts very high (~2500 Hz)
    and transitions toward [e] F2
    (~2100 Hz) over 50 ms.
    """
    dur_ms = J_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    T      = 1.0 / sr
    src    = rosenberg_pulse(n_s, pitch_hz,
                              oq=0.65, sr=sr)
    n_atk  = min(int(0.010 * sr), n_s // 4)
    env    = np.ones(n_s, dtype=DTYPE)
    if n_atk < n_s:
        env[:n_atk] = np.linspace(
            0.2, 1.0, n_atk)
    src    = f32(src * env)
    f_end  = F_next if F_next is not None \
             else J_F_END
    result = apply_formants_trajectory(
        src, J_F_START, f_end,
        J_B, J_GAINS, sr=sr)
    mx = np.max(np.abs(result))
    if mx > 1e-8:
        result = f32(result / mx * 0.65)
    return f32(result)


def synth_E_short(F_prev, F_next,
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
    result = np.zeros(n_s, dtype=DTYPE)
    for fi in range(len(E_F)):
        f_s   = (float(F_prev[fi])
                 if fi < len(F_prev)
                 else float(E_F[fi]))
        f_e   = (float(F_next[fi])
                 if fi < len(F_next)
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


def synth_F(F_next=None, dil=DIL, sr=SR):
    """
    Voiceless labiodental fricative [f].
    Lower lip to upper teeth.
    Frication centroid ~5500 Hz —
    higher than dental [θ] (~4000 Hz).
    No voicing.
    """
    dur_ms = F_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    noise  = np.random.randn(n_s).astype(float)
    b, a   = safe_bp(
        F_NOISE_CF - F_NOISE_BW / 2,
        min(F_NOISE_CF + F_NOISE_BW / 2,
            sr * 0.48), sr)
    fric   = lfilter(b, a, noise)
    b2, a2 = safe_bp(2000.0, 5000.0, sr)
    fric  += lfilter(b2, a2, noise) * 0.25
    n_atk  = min(int(0.015 * sr), n_s // 4)
    n_dec  = min(int(0.015 * sr), n_s // 4)
    env    = np.ones(n_s, dtype=float)
    if n_atk < n_s:
        env[:n_atk] = np.linspace(
            0.0, 1.0, n_atk)
    if n_dec < n_s:
        env[-n_dec:] = np.linspace(
            1.0, 0.3, n_dec)
    fric   = f32(fric * env * F_GAIN)
    mx     = np.max(np.abs(fric))
    if mx > 1e-8:
        fric = f32(fric / mx * 0.42)
    return f32(fric)


def synth_UU_long(F_prev, F_next,
                   pitch_hz=PITCH_HZ,
                   dil=DIL, sr=SR):
    """
    Long close back rounded [uː].
    Same place as short [u].
    Duration 150 ms — phonemically long.
    Slightly more peripheral than [u]:
    F1 280 Hz (vs 300), F2 650 Hz (vs 700).
    The length is the primary cue.
    """
    dur_ms = UU_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    T      = 1.0 / sr
    src    = rosenberg_pulse(n_s, pitch_hz,
                              oq=0.65, sr=sr)
    n_atk  = min(int(0.015 * sr), n_s // 4)
    n_rel  = min(int(0.030 * sr), n_s // 4)
    env    = np.ones(n_s, dtype=DTYPE)
    if n_atk < n_s:
        env[:n_atk] = np.linspace(
            0.3, 1.0, n_atk)
    if n_rel < n_s:
        env[-n_rel:] = np.linspace(
            1.0, 0.4, n_rel)
    src    = f32(src * env)
    n_on   = int(UU_COART_ON  * n_s)
    n_off  = int(UU_COART_OFF * n_s)
    result = np.zeros(n_s, dtype=DTYPE)
    for fi in range(len(UU_F)):
        f_s   = (float(F_prev[fi])
                 if fi < len(F_prev)
                 else float(UU_F[fi]))
        f_e   = (float(F_next[fi])
                 if fi < len(F_next)
                 else float(UU_F[fi]))
        f_b   = float(UU_F[fi])
        f_arr = np.full(n_s, f_b, dtype=DTYPE)
        if n_on > 0:
            f_arr[:n_on] = np.linspace(
                f_s, f_b, n_on)
        if n_off > 0:
            f_arr[-n_off:] = np.linspace(
                f_b, f_e, n_off)
        bw  = float(UU_B[fi])
        g   = float(UU_GAINS[fi])
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


def synth_N(F_prev, F_next,
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


def synth_N_final(F_prev=None,
                   pitch_hz=PITCH_HZ,
                   dil=DIL, sr=SR):
    """Word-final [n] — longer decay."""
    dur_ms = N_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    T      = 1.0 / sr
    src    = rosenberg_pulse(n_s, pitch_hz,
                              oq=0.65, sr=sr)
    n_tr   = min(int(0.015 * sr), n_s // 4)
    n_dec  = min(int(0.040 * sr), n_s // 2)
    env    = np.ones(n_s, dtype=DTYPE)
    if n_tr < n_s:
        env[:n_tr]  = np.linspace(
            0.3, 1.0, n_tr)
    if n_dec < n_s:
        env[-n_dec:] = np.linspace(
            1.0, 0.0, n_dec)
    src    = f32(src * env)
    result = apply_formants(
        src, N_F, N_B, N_GAINS, sr=sr)
    result = iir_notch(
        result, fc=N_ANTI_F,
        bw=N_ANTI_BW, sr=sr)
    mx = np.max(np.abs(result))
    if mx > 1e-8:
        result = f32(result / mx * 0.50)
    return f32(result)


def synth_O_short(F_prev, F_next,
                   pitch_hz=PITCH_HZ,
                   dil=DIL, sr=SR):
    dur_ms = O_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    T      = 1.0 / sr
    src    = rosenberg_pulse(n_s, pitch_hz,
                              oq=0.65, sr=sr)
    n_atk  = min(int(0.012 * sr), n_s // 4)
    n_rel  = min(int(0.025 * sr), n_s // 4)
    env    = np.ones(n_s, dtype=DTYPE)
    if n_atk < n_s:
        env[:n_atk] = np.linspace(
            0.4, 1.0, n_atk)
    if n_rel < n_s:
        env[-n_rel:] = np.linspace(
            1.0, 0.5, n_rel)
    src    = f32(src * env)
    n_on   = int(O_COART_ON  * n_s)
    n_off  = int(O_COART_OFF * n_s)
    result = np.zeros(n_s, dtype=DTYPE)
    for fi in range(len(O_F)):
        f_s   = (float(F_prev[fi])
                 if fi < len(F_prev)
                 else float(O_F[fi]))
        f_e   = (float(F_next[fi])
                 if fi < len(F_next)
                 else float(O_F[fi]))
        f_b   = float(O_F[fi])
        f_arr = np.full(n_s, f_b, dtype=DTYPE)
        if n_on > 0:
            f_arr[:n_on] = np.linspace(
                f_s, f_b, n_on)
        if n_off > 0:
            f_arr[-n_off:] = np.linspace(
                f_b, f_e, n_off)
        bw  = float(O_B[fi])
        g   = float(O_GAINS[fi])
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

def synth_gefrunon(pitch_hz=PITCH_HZ,
                    dil=DIL,
                    add_room=False,
                    sr=SR):
    """[j·e·f·uː·n·o·n]"""
    j_seg  = synth_J(
        F_next=E_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    e_seg  = synth_E_short(
        F_prev=J_F_START, F_next=None,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    f_seg  = synth_F(
        F_next=UU_F, dil=dil, sr=sr)
    uu_seg = synth_UU_long(
        F_prev=UU_F, F_next=N_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    n1_seg = synth_N(
        F_prev=UU_F, F_next=O_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    o_seg  = synth_O_short(
        F_prev=N_F, F_next=N_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    n2_seg = synth_N_final(
        F_prev=O_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    word = np.concatenate([
        j_seg, e_seg, f_seg, uu_seg,
        n1_seg, o_seg, n2_seg])
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
    print("GEFRŪNON RECONSTRUCTION v1")
    print("Old English [jefrуːnon]")
    print("Beowulf line 2, word 3")
    print()

    gf_dry = synth_gefrunon(
        pitch_hz=145.0, dil=1.0,
        add_room=False)
    write_wav(
        "output_play/gefrunon_dry.wav",
        gf_dry, SR)
    print(f"  gefrunon_dry.wav"
          f"  ({len(gf_dry)/SR*1000:.0f} ms)")

    gf_hall = synth_gefrunon(
        pitch_hz=145.0, dil=1.0,
        add_room=True)
    write_wav(
        "output_play/gefrunon_hall.wav",
        gf_hall, SR)
    print("  gefrunon_hall.wav")

    gf_slow = ola_stretch(gf_dry, 4.0)
    write_wav(
        "output_play/gefrunon_slow.wav",
        gf_slow, SR)
    print("  gefrunon_slow.wav")

    gf_perf = synth_gefrunon(
        pitch_hz=110.0, dil=2.5,
        add_room=True)
    write_wav(
        "output_play/gefrunon_performance.wav",
        gf_perf, SR)
    print(f"  gefrunon_performance.wav"
          f"  ({len(gf_perf)/SR*1000:.0f} ms)")

    for name, seg in [
        ("j",  synth_J(E_F, 145.0, 1.0, SR)),
        ("f",  synth_F(UU_F, 1.0, SR)),
        ("uu", synth_UU_long(
            UU_F, N_F, 145.0, 1.0, SR)),
    ]:
        write_wav(
            f"output_play/"
            f"gefrunon_{name}_isolated.wav",
            ola_stretch(seg / (
                np.max(np.abs(seg))+1e-8)
                * 0.75, 4.0), SR)
        print(f"  gefrunon_{name}"
              f"_isolated.wav  (4x slow)")

    print()
    print("  afplay output_play/"
          "gefrunon_j_isolated.wav")
    print("  afplay output_play/"
          "gefrunon_f_isolated.wav")
    print("  afplay output_play/"
          "gefrunon_uu_isolated.wav")
    print("  afplay output_play/"
          "gefrunon_dry.wav")
    print("  afplay output_play/"
          "gefrunon_performance.wav")
    print("  afplay output_play/"
          "gefrunon_hall.wav")
    print()
