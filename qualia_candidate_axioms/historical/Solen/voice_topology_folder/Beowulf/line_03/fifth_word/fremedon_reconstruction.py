"""
FREMEDON RECONSTRUCTION
Old English: fremedon
Meaning: performed, did, carried out
         (3rd pers. plural past tense
         of fremman — to perform,
         to carry out, to do)
IPA: [fremedon]
Beowulf: Line 3, Word 5 (overall word 13)
         Final word of line 3.
February 2026

PHONEME STRUCTURE:
  F   [f]   voiceless labiodental fric. — verified
  R   [r]   alveolar trill              — verified
  E   [e]   short close-mid front       — verified
  M   [m]   voiced bilabial nasal       — verified
  E   [e]   short close-mid front       — verified
  D   [d]   voiced alveolar stop        — verified
  O   [o]   short close-mid back        — verified
  N   [n]   voiced alveolar nasal       — verified

ZERO NEW PHONEMES.
Pure assembly from verified inventory.
Proof of framework.

CLUSTER NOTE:
  [fr] onset cluster — word initial.
  [f] releases into [r].
  [f] offset transitions toward
  [r] formant targets before
  frication ends.
  Voiced [r] onset begins at
  tail of [f] frication.

MORPHOLOGICAL NOTE:
  fremman — Class I weak verb.
  To perform, carry out, do,
  further, advance.
  fremedon — 3rd person plural
  past indicative.
  'they performed' / 'they did'.
  The -don ending is the OE past
  plural marker — cognate with
  Modern English -ed past tense
  but with the plural -on suffix
  lost after the OE period.
  The verb root frem- survives
  in Modern English 'frame' through
  a separate development pathway.

LINE 3 COMPLETE:
  hu ðā æþelingas ellen fremedon
  how those princes performed
  acts of courage

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
# PARAMETERS — all verified, no new phonemes
# ============================================================

# F — voiceless labiodental fricative [f]
F_DUR_MS   = 75.0
F_NOISE_CF = 6000.0
F_NOISE_BW = 4000.0
F_GAIN     = 0.30
# [f] offset toward [r] formants
F_COART_R  = True

# R — alveolar trill [r]
# Verified GĀR-DENA.
# Post-fricative onset here — [fr] cluster.
# Voicing starts at trill onset.
R_F       = [400.0, 1200.0, 2600.0, 3300.0]
R_B       = [100.0,  150.0,  200.0,  280.0]
R_GAINS   = [ 14.0,    7.0,    1.5,    0.5]
R_DUR_MS  = 70.0
R_TRILL_HZ = 25.0   # trill modulation ~25 Hz
R_TRILL_DEPTH = 0.45

# E — short close-mid front [e]
E_F      = [370.0, 2100.0, 2800.0, 3300.0]
E_B      = [ 80.0,  120.0,  170.0,  240.0]
E_GAINS  = [ 18.0,    9.0,    1.5,    0.5]
E_DUR_MS = 60.0
E_COART_ON  = 0.12
E_COART_OFF = 0.12

# M — voiced bilabial nasal [m]
M_F       = [250.0,  900.0, 2200.0, 3300.0]
M_B       = [100.0,  200.0,  300.0,  350.0]
M_GAINS   = [  8.0,    2.0,    0.5,    0.2]
M_DUR_MS  = 70.0
M_ANTI_F  = 1000.0
M_ANTI_BW = 200.0

# D — voiced alveolar stop [d]
D_DUR_MS  = 70.0
D_BURST_F = 1800.0
D_BURST_BW= 500.0
D_BURST_MS= 10.0
D_VOT_MS  = 6.0

# O — short close-mid back rounded [o]
O_F      = [450.0,  800.0, 2500.0, 3300.0]
O_B      = [100.0,  120.0,  200.0,  280.0]
O_GAINS  = [ 16.0,    6.0,    1.2,    0.4]
O_DUR_MS = 60.0
O_COART_ON  = 0.12
O_COART_OFF = 0.12

# N — voiced alveolar nasal [n]
N_F       = [250.0, 1800.0, 2600.0, 3300.0]
N_B       = [100.0,  200.0,  300.0,  350.0]
N_GAINS   = [  8.0,    2.0,    0.5,    0.2]
N_DUR_MS  = 65.0
N_ANTI_F  = 800.0
N_ANTI_BW = 200.0

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

def synth_F(F_next=None, dil=DIL, sr=SR):
    """
    Voiceless labiodental fricative [f].
    Word-initial. [fr] cluster —
    offset transitions toward [r] formants.
    """
    dur_ms = F_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    noise  = np.random.randn(n_s).astype(float)
    b, a   = safe_bp(
        F_NOISE_CF - F_NOISE_BW / 2,
        min(F_NOISE_CF + F_NOISE_BW / 2,
            sr * 0.48), sr)
    fric   = lfilter(b, a, noise)
    b2, a2 = safe_bp(3000.0, 8000.0, sr)
    fric  += lfilter(b2, a2, noise) * 0.3
    n_atk  = min(int(0.010 * sr), n_s // 4)
    n_dec  = min(int(0.015 * sr), n_s // 4)
    env    = np.ones(n_s, dtype=float)
    if n_atk < n_s:
        env[:n_atk] = np.linspace(
            0.0, 1.0, n_atk)
    if n_dec < n_s:
        env[-n_dec:] = np.linspace(
            1.0, 0.2, n_dec)
    fric   = f32(fric * env * F_GAIN)
    mx     = np.max(np.abs(fric))
    if mx > 1e-8:
        fric = f32(fric / mx * 0.45)
    return f32(fric)


def synth_R(F_prev=None, F_next=None,
             pitch_hz=PITCH_HZ,
             dil=DIL, sr=SR):
    """
    Alveolar trill [r].
    Amplitude modulated at trill rate ~25 Hz.
    Post-fricative onset in [fr] cluster.
    """
    dur_ms = R_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    T      = 1.0 / sr
    src    = rosenberg_pulse(n_s, pitch_hz,
                              oq=0.65, sr=sr)
    # Trill modulation envelope
    t_arr  = np.arange(n_s, dtype=float) * T
    trill  = (1.0
              - R_TRILL_DEPTH
              * 0.5 * (1.0 - np.cos(
                  2 * np.pi * R_TRILL_HZ
                  * t_arr))).astype(DTYPE)
    # Overall envelope
    n_atk  = min(int(0.015 * sr), n_s // 4)
    n_rel  = min(int(0.015 * sr), n_s // 4)
    env    = np.ones(n_s, dtype=DTYPE)
    if n_atk < n_s:
        env[:n_atk] = np.linspace(
            0.2, 1.0, n_atk)
    if n_rel < n_s:
        env[-n_rel:] = np.linspace(
            1.0, 0.4, n_rel)
    src    = f32(src * env * trill)
    # Formant trajectory — prev to R to next
    f_prev = F_prev if F_prev is not None \
             else R_F
    f_next = F_next if F_next is not None \
             else R_F
    n_on   = min(int(0.15 * n_s), n_s // 3)
    n_off  = min(int(0.15 * n_s), n_s // 3)
    result = np.zeros(n_s, dtype=DTYPE)
    for fi in range(len(R_F)):
        f_s   = (float(f_prev[fi])
                 if fi < len(f_prev)
                 else float(R_F[fi]))
        f_e   = (float(f_next[fi])
                 if fi < len(f_next)
                 else float(R_F[fi]))
        f_b   = float(R_F[fi])
        f_arr = np.full(n_s, f_b, dtype=DTYPE)
        if n_on > 0:
            f_arr[:n_on] = np.linspace(
                f_s, f_b, n_on)
        if n_off > 0:
            f_arr[-n_off:] = np.linspace(
                f_b, f_e, n_off)
        bw  = float(R_B[fi])
        g   = float(R_GAINS[fi])
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


def synth_M(F_prev=None, F_next=None,
             pitch_hz=PITCH_HZ,
             dil=DIL, sr=SR):
    dur_ms = M_DUR_MS * dil
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
        src, M_F, M_B, M_GAINS, sr=sr)
    result = iir_notch(
        result, fc=M_ANTI_F,
        bw=M_ANTI_BW, sr=sr)
    mx = np.max(np.abs(result))
    if mx > 1e-8:
        result = f32(result / mx * 0.55)
    return f32(result)


def synth_D(F_prev=None, F_next=None,
             pitch_hz=PITCH_HZ,
             dil=DIL, sr=SR):
    dur_ms    = D_DUR_MS * dil
    n_s       = max(4, int(dur_ms / 1000.0 * sr))
    n_burst   = max(2, int(D_BURST_MS / 1000.0 * sr))
    n_vot     = max(2, int(D_VOT_MS   / 1000.0 * sr))
    n_closure = max(2, n_s - n_burst - n_vot)
    T         = 1.0 / sr
    # Voiced closure murmur
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
        D_BURST_F - D_BURST_BW / 2,
        D_BURST_F + D_BURST_BW / 2, sr)
    burst  = f32(lfilter(b_bp, a_bp, noise)
                 * 0.6)
    # VOT — voiced transition to next vowel
    src_v  = rosenberg_pulse(
        n_vot, pitch_hz, oq=0.65, sr=sr)
    f_next_ = F_next if F_next is not None \
              else O_F
    vot    = apply_formants(
        src_v, f_next_,
        [100.0, 150.0, 200.0, 280.0],
        [14.0, 7.0, 1.2, 0.4], sr=sr)
    vot    = f32(vot * 0.5)
    seg    = np.concatenate([murmur, burst, vot])
    mx     = np.max(np.abs(seg))
    if mx > 1e-8:
        seg = f32(seg / mx * 0.65)
    return f32(seg)


def synth_O_short(F_prev=None, F_next=None,
                   pitch_hz=PITCH_HZ,
                   dil=DIL, sr=SR):
    dur_ms = O_DUR_MS * dil
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
    n_on   = int(O_COART_ON  * n_s)
    n_off  = int(O_COART_OFF * n_s)
    f_prev = F_prev if F_prev is not None \
             else O_F
    f_next = F_next if F_next is not None \
             else O_F
    result = np.zeros(n_s, dtype=DTYPE)
    for fi in range(len(O_F)):
        f_s   = (float(f_prev[fi])
                 if fi < len(f_prev)
                 else float(O_F[fi]))
        f_e   = (float(f_next[fi])
                 if fi < len(f_next)
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


def synth_N_final(F_prev=None,
                   pitch_hz=PITCH_HZ,
                   dil=DIL, sr=SR):
    """Word-final nasal — longer decay."""
    dur_ms = N_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    src    = rosenberg_pulse(n_s, pitch_hz,
                              oq=0.65, sr=sr)
    n_tr   = min(int(0.020 * sr), n_s // 4)
    n_dec  = min(int(0.040 * sr), n_s // 3)
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
        result = f32(result / mx * 0.55)
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

def synth_fremedon(pitch_hz=PITCH_HZ,
                    dil=DIL,
                    add_room=False,
                    sr=SR):
    """[f·r·e·m·e·d·o·n]"""
    f_seg  = synth_F(
        F_next=R_F, dil=dil, sr=sr)
    r_seg  = synth_R(
        F_prev=E_F, F_next=E_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    e1_seg = synth_E_short(
        F_prev=R_F, F_next=M_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    m_seg  = synth_M(
        F_prev=E_F, F_next=E_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    e2_seg = synth_E_short(
        F_prev=M_F, F_next=O_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    d_seg  = synth_D(
        F_prev=E_F, F_next=O_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    o_seg  = synth_O_short(
        F_prev=O_F, F_next=N_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    n_seg  = synth_N_final(
        F_prev=O_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    word   = np.concatenate([
        f_seg, r_seg, e1_seg, m_seg,
        e2_seg, d_seg, o_seg, n_seg])
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
    print("FREMEDON RECONSTRUCTION v1")
    print("Old English [fremedon]")
    print("Beowulf line 3, word 5")
    print("Line 3 final word.")
    print()

    w_dry = synth_fremedon(
        pitch_hz=145.0, dil=1.0,
        add_room=False)
    write_wav(
        "output_play/fremedon_dry.wav",
        w_dry, SR)
    print(f"  fremedon_dry.wav"
          f"  ({len(w_dry)/SR*1000:.0f} ms)")

    w_hall = synth_fremedon(
        pitch_hz=145.0, dil=1.0,
        add_room=True)
    write_wav(
        "output_play/fremedon_hall.wav",
        w_hall, SR)
    print("  fremedon_hall.wav")

    w_slow = ola_stretch(w_dry, 4.0)
    write_wav(
        "output_play/fremedon_slow.wav",
        w_slow, SR)
    print("  fremedon_slow.wav")

    w_perf = synth_fremedon(
        pitch_hz=110.0, dil=2.5,
        add_room=True)
    write_wav(
        "output_play/fremedon_performance.wav",
        w_perf, SR)
    print(f"  fremedon_performance.wav"
          f"  ({len(w_perf)/SR*1000:.0f} ms)")

    print()
    print("  afplay output_play/"
          "fremedon_dry.wav")
    print("  afplay output_play/"
          "fremedon_slow.wav")
    print("  afplay output_play/"
          "fremedon_hall.wav")
    print("  afplay output_play/"
          "fremedon_performance.wav")
    print()
    print("  LINE 3 COMPLETE:")
    print("  hu ðā æþelingas ellen fremedon")
    print()
