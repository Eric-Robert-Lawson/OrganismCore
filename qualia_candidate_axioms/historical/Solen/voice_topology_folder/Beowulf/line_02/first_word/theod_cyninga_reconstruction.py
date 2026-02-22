"""
ÞĒOD-CYNINGA RECONSTRUCTION
Old English: þēod-cyninga
Meaning: of the people-kings (genitive plural)
IPA: [θeːodkyniŋɡɑ]
Beowulf: Line 2, Word 1 (overall word 6)
February 2026

CHANGE LOG:
  v1 — initial parameters, all verified
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

TH_DUR_MS   = 80.0
TH_NOISE_CF = 3800.0
TH_NOISE_BW = 3000.0
TH_GAIN     = 0.35

EE_F      = [390.0, 2100.0, 2800.0, 3300.0]
EE_B      = [ 80.0,  120.0,  160.0,  220.0]
EE_GAINS  = [ 20.0,    8.0,    1.5,    0.5]
EE_DUR_MS = 150.0
EE_COART_ON  = 0.10
EE_COART_OFF = 0.10

O_F      = [500.0,  800.0, 2400.0, 3200.0]
O_B      = [100.0,  120.0,  200.0,  280.0]
O_GAINS  = [ 18.0,   10.0,    1.2,    0.4]
O_DUR_MS = 70.0
O_COART_ON  = 0.12
O_COART_OFF = 0.12

D_F          = [250.0, 1800.0, 2600.0, 3400.0]
D_B          = [200.0,  220.0,  280.0,  320.0]
D_CLOSURE_MS = 45.0
D_BURST_MS   = 10.0
D_BURST_CF   = 3500.0

K_F          = [250.0, 1800.0, 2800.0, 3400.0]
K_B          = [200.0,  250.0,  300.0,  350.0]
K_CLOSURE_MS = 55.0
K_BURST_MS   = 14.0
K_ASP_MS     = 25.0
K_BURST_CF   = 1500.0

Y_F      = [300.0, 1500.0, 2400.0, 3200.0]
Y_B      = [ 80.0,  130.0,  200.0,  270.0]
Y_GAINS  = [ 16.0,   12.0,    1.5,    0.5]
Y_DUR_MS = 65.0
Y_COART_ON  = 0.15
Y_COART_OFF = 0.12

N_F       = [250.0, 1800.0, 2600.0, 3300.0]
N_B       = [100.0,  200.0,  300.0,  350.0]
N_GAINS   = [  8.0,    2.0,    0.5,    0.2]
N_DUR_MS  = 65.0
N_ANTI_F  = 800.0
N_ANTI_BW = 200.0

I_F      = [400.0, 1800.0, 2600.0, 3300.0]
I_B      = [ 80.0,  120.0,  180.0,  250.0]
I_GAINS  = [ 18.0,   10.0,    1.5,    0.5]
I_DUR_MS = 60.0
I_COART_ON  = 0.12
I_COART_OFF = 0.12

NG_F       = [250.0,  900.0, 2200.0, 3000.0]
NG_B       = [120.0,  300.0,  350.0,  400.0]
NG_GAINS   = [  8.0,   10.0,    0.8,    0.2]
NG_DUR_MS  = 65.0
NG_ANTI_F  = 1800.0
NG_ANTI_BW = 250.0

G_F          = [250.0, 1000.0, 2600.0, 3200.0]
G_B          = [200.0,  220.0,  280.0,  330.0]
G_CLOSURE_MS = 50.0
G_BURST_MS   = 12.0
G_BURST_CF   = 1200.0

A_F      = [840.0, 1150.0, 2500.0, 3300.0]
A_B      = [180.0,  120.0,  200.0,  280.0]
A_GAINS  = [ 16.0,    5.0,    1.2,    0.4]
A_DUR_MS = 70.0
A_COART_ON  = 0.10
A_COART_OFF = 0.15

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

def synth_TH(F_next=None, dil=DIL, sr=SR):
    dur_ms = TH_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    noise  = np.random.randn(n_s).astype(float)
    b, a   = safe_bp(
        TH_NOISE_CF - TH_NOISE_BW / 2,
        min(TH_NOISE_CF + TH_NOISE_BW / 2,
            sr * 0.45), sr)
    fric   = lfilter(b, a, noise)
    b2, a2 = safe_bp(800.0, 3000.0, sr)
    fric  += lfilter(b2, a2, noise) * 0.3
    n_atk  = min(int(0.020 * sr), n_s // 4)
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
        fric = f32(fric / mx * 0.45)
    return f32(fric)


def synth_EE_long(F_prev, F_next,
                   pitch_hz=PITCH_HZ,
                   dil=DIL, sr=SR):
    dur_ms = EE_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    T      = 1.0 / sr
    src    = rosenberg_pulse(n_s, pitch_hz,
                              oq=0.65, sr=sr)
    n_atk  = min(int(0.020 * sr), n_s // 4)
    n_rel  = min(int(0.040 * sr), n_s // 4)
    env    = np.ones(n_s, dtype=DTYPE)
    if n_atk < n_s:
        env[:n_atk] = np.linspace(
            0.4, 1.0, n_atk)
    if n_rel < n_s:
        env[-n_rel:] = np.linspace(
            1.0, 0.3, n_rel)
    src    = f32(src * env)
    n_on   = int(EE_COART_ON  * n_s)
    n_off  = int(EE_COART_OFF * n_s)
    result = np.zeros(n_s, dtype=DTYPE)
    for fi in range(len(EE_F)):
        f_s   = (float(F_prev[fi])
                 if fi < len(F_prev)
                 else float(EE_F[fi]))
        f_e   = (float(F_next[fi])
                 if fi < len(F_next)
                 else float(EE_F[fi]))
        f_b   = float(EE_F[fi])
        f_arr = np.full(n_s, f_b, dtype=DTYPE)
        if n_on > 0:
            f_arr[:n_on] = np.linspace(
                f_s, f_b, n_on)
        if n_off > 0:
            f_arr[-n_off:] = np.linspace(
                f_b, f_e, n_off)
        bw  = float(EE_B[fi])
        g   = float(EE_GAINS[fi])
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
        result = f32(result / mx * 0.75)
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
        result = f32(result / mx * 0.70)
    return f32(result)


def synth_D(F_prev, F_next,
             pitch_hz=PITCH_HZ,
             dil=DIL, sr=SR):
    n_cl  = max(4, int(
        D_CLOSURE_MS * dil / 1000.0 * sr))
    n_bst = max(4, int(
        D_BURST_MS * dil / 1000.0 * sr))
    src_cl = rosenberg_pulse(
        n_cl, pitch_hz, oq=0.65, sr=sr)
    b, a   = safe_lp(400.0, sr)
    bar    = f32(lfilter(
        b, a, src_cl.astype(float)) * 0.04)
    noise  = f32(np.random.randn(n_bst) * 0.12)
    b2, a2 = safe_bp(
        D_BURST_CF - 400.0,
        D_BURST_CF + 400.0, sr)
    burst  = f32(lfilter(
        b2, a2, noise.astype(float)))
    n_rel   = max(4, int(0.025 * dil * sr))
    src_rel = rosenberg_pulse(
        n_rel, pitch_hz, oq=0.65, sr=sr)
    release = apply_formants_trajectory(
        src_rel, D_F, F_next, D_B,
        [1.0, 0.6, 0.3, 0.1], sr=sr)
    seg = np.concatenate([bar, burst, release])
    mx  = np.max(np.abs(seg))
    if mx > 1e-8:
        seg = f32(seg / mx * 0.55)
    return f32(seg)


def synth_K(F_next, pitch_hz=PITCH_HZ,
             dil=DIL, sr=SR):
    n_cl  = max(4, int(
        K_CLOSURE_MS * dil / 1000.0 * sr))
    n_bst = max(4, int(
        K_BURST_MS * dil / 1000.0 * sr))
    n_asp = max(4, int(
        K_ASP_MS * dil / 1000.0 * sr))
    closure   = np.zeros(n_cl, dtype=DTYPE)
    noise     = np.random.randn(n_bst).astype(
        float)
    b, a      = safe_bp(
        K_BURST_CF - 400.0,
        K_BURST_CF + 400.0, sr)
    burst     = f32(lfilter(b, a, noise) * 0.55)
    asp_noise = np.random.randn(n_asp).astype(
        float)
    b2, a2    = safe_bp(1000.0, 4000.0, sr)
    asp       = f32(lfilter(b2, a2, asp_noise)
                    * np.linspace(0.8, 0.1, n_asp)
                    * 0.15)
    n_rel     = max(4, int(0.025 * dil * sr))
    src_rel   = rosenberg_pulse(
        n_rel, pitch_hz, oq=0.65, sr=sr)
    release   = apply_formants_trajectory(
        src_rel, K_F, F_next, K_B,
        [1.0, 0.5, 0.3, 0.1], sr=sr)
    seg = np.concatenate([
        closure, burst, asp, release])
    mx  = np.max(np.abs(seg))
    if mx > 1e-8:
        seg = f32(seg / mx * 0.60)
    return f32(seg)


def synth_Y_short(F_prev, F_next,
                   pitch_hz=PITCH_HZ,
                   dil=DIL, sr=SR):
    dur_ms = Y_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    T      = 1.0 / sr
    src    = rosenberg_pulse(n_s, pitch_hz,
                              oq=0.65, sr=sr)
    n_atk  = min(int(0.012 * sr), n_s // 4)
    n_rel  = min(int(0.018 * sr), n_s // 4)
    env    = np.ones(n_s, dtype=DTYPE)
    if n_atk < n_s:
        env[:n_atk] = np.linspace(
            0.3, 1.0, n_atk)
    if n_rel < n_s:
        env[-n_rel:] = np.linspace(
            1.0, 0.5, n_rel)
    src    = f32(src * env)
    n_on   = int(Y_COART_ON  * n_s)
    n_off  = int(Y_COART_OFF * n_s)
    result = np.zeros(n_s, dtype=DTYPE)
    for fi in range(len(Y_F)):
        f_s   = (float(F_prev[fi])
                 if fi < len(F_prev)
                 else float(Y_F[fi]))
        f_e   = (float(F_next[fi])
                 if fi < len(F_next)
                 else float(Y_F[fi]))
        f_b   = float(Y_F[fi])
        f_arr = np.full(n_s, f_b, dtype=DTYPE)
        if n_on > 0:
            f_arr[:n_on] = np.linspace(
                f_s, f_b, n_on)
        if n_off > 0:
            f_arr[-n_off:] = np.linspace(
                f_b, f_e, n_off)
        bw  = float(Y_B[fi])
        g   = float(Y_GAINS[fi])
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


def synth_I_short(F_prev, F_next,
                   pitch_hz=PITCH_HZ,
                   dil=DIL, sr=SR):
    dur_ms = I_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    T      = 1.0 / sr
    src    = rosenberg_pulse(n_s, pitch_hz,
                              oq=0.65, sr=sr)
    n_atk  = min(int(0.012 * sr), n_s // 4)
    n_rel  = min(int(0.015 * sr), n_s // 4)
    env    = np.ones(n_s, dtype=DTYPE)
    if n_atk < n_s:
        env[:n_atk] = np.linspace(
            0.4, 1.0, n_atk)
    if n_rel < n_s:
        env[-n_rel:] = np.linspace(
            1.0, 0.6, n_rel)
    src    = f32(src * env)
    n_on   = int(I_COART_ON  * n_s)
    n_off  = int(I_COART_OFF * n_s)
    result = np.zeros(n_s, dtype=DTYPE)
    for fi in range(len(I_F)):
        f_s   = (float(F_prev[fi])
                 if fi < len(F_prev)
                 else float(I_F[fi]))
        f_e   = (float(F_next[fi])
                 if fi < len(F_next)
                 else float(I_F[fi]))
        f_b   = float(I_F[fi])
        f_arr = np.full(n_s, f_b, dtype=DTYPE)
        if n_on > 0:
            f_arr[:n_on] = np.linspace(
                f_s, f_b, n_on)
        if n_off > 0:
            f_arr[-n_off:] = np.linspace(
                f_b, f_e, n_off)
        bw  = float(I_B[fi])
        g   = float(I_GAINS[fi])
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


def synth_NG(F_prev, F_next,
              pitch_hz=PITCH_HZ,
              dil=DIL, sr=SR):
    dur_ms = NG_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    T      = 1.0 / sr
    src    = rosenberg_pulse(n_s, pitch_hz,
                              oq=0.65, sr=sr)
    n_tr   = min(int(0.015 * sr), n_s // 4)
    env    = np.ones(n_s, dtype=DTYPE)
    if n_tr < n_s:
        env[:n_tr]  = np.linspace(
            0.3, 1.0, n_tr)
        env[-n_tr:] = np.linspace(
            1.0, 0.3, n_tr)
    src    = f32(src * env)
    result = apply_formants(
        src, NG_F, NG_B, NG_GAINS, sr=sr)
    result = iir_notch(
        result, fc=NG_ANTI_F,
        bw=NG_ANTI_BW, sr=sr)
    mx = np.max(np.abs(result))
    if mx > 1e-8:
        result = f32(result / mx * 0.55)
    return f32(result)


def synth_G(F_next, pitch_hz=PITCH_HZ,
             dil=DIL, sr=SR):
    n_cl  = max(4, int(
        G_CLOSURE_MS * dil / 1000.0 * sr))
    n_bst = max(4, int(
        G_BURST_MS * dil / 1000.0 * sr))
    src_cl = rosenberg_pulse(
        n_cl, pitch_hz, oq=0.65, sr=sr)
    b, a   = safe_lp(400.0, sr)
    bar    = f32(lfilter(
        b, a, src_cl.astype(float)) * 0.05)
    noise  = f32(np.random.randn(n_bst) * 0.15)
    b2, a2 = safe_bp(
        G_BURST_CF - 300.0,
        G_BURST_CF + 300.0, sr)
    burst  = f32(lfilter(
        b2, a2, noise.astype(float)))
    src_bst = rosenberg_pulse(
        n_bst, pitch_hz, oq=0.65, sr=sr)
    burst  += apply_formants(
        src_bst, G_F, G_B,
        [g * 0.3 for g in
         [1.0, 0.5, 0.3, 0.1]], sr=sr) * 0.4
    n_rel   = max(4, int(0.030 * dil * sr))
    src_rel = rosenberg_pulse(
        n_rel, pitch_hz, oq=0.65, sr=sr)
    release = apply_formants_trajectory(
        src_rel, G_F, F_next, G_B,
        [1.0, 0.5, 0.3, 0.1], sr=sr)
    seg = np.concatenate([bar, burst, release])
    mx  = np.max(np.abs(seg))
    if mx > 1e-8:
        seg = f32(seg / mx * 0.60)
    return f32(seg)


def synth_A_short(F_prev, F_next,
                   pitch_hz=PITCH_HZ,
                   dil=DIL, sr=SR):
    dur_ms = A_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    T      = 1.0 / sr
    src    = rosenberg_pulse(n_s, pitch_hz,
                              oq=0.65, sr=sr)
    n_atk  = min(int(0.012 * sr), n_s // 4)
    n_rel  = min(int(0.060 * sr), n_s // 3)
    env    = np.ones(n_s, dtype=DTYPE)
    if n_atk < n_s:
        env[:n_atk] = np.linspace(
            0.4, 1.0, n_atk)
    if n_rel < n_s:
        env[-n_rel:] = np.linspace(
            1.0, 0.0, n_rel)
    src    = f32(src * env)
    n_on   = int(A_COART_ON  * n_s)
    result = np.zeros(n_s, dtype=DTYPE)
    for fi in range(len(A_F)):
        f_s   = (float(F_prev[fi])
                 if fi < len(F_prev)
                 else float(A_F[fi]))
        f_b   = float(A_F[fi])
        f_arr = np.full(n_s, f_b, dtype=DTYPE)
        if n_on > 0:
            f_arr[:n_on] = np.linspace(
                f_s, f_b, n_on)
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
        result = f32(result / mx * 0.60)
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


def synth_theod_cyninga(pitch_hz=PITCH_HZ,
                         dil=DIL,
                         add_room=False,
                         sr=SR):
    th_seg = synth_TH(
        F_next=EE_F, dil=dil, sr=sr)
    ee_seg = synth_EE_long(
        F_prev=G_F, F_next=O_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    o_seg  = synth_O_short(
        F_prev=EE_F, F_next=D_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    d_seg  = synth_D(
        F_prev=O_F, F_next=K_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    k_seg  = synth_K(
        F_next=Y_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    y_seg  = synth_Y_short(
        F_prev=K_F, F_next=N_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    n_seg  = synth_N(
        F_prev=Y_F, F_next=I_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    i_seg  = synth_I_short(
        F_prev=N_F, F_next=NG_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    ng_seg = synth_NG(
        F_prev=I_F, F_next=G_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    g_seg  = synth_G(
        F_next=A_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    a_seg  = synth_A_short(
        F_prev=G_F, F_next=None,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    word = np.concatenate([
        th_seg, ee_seg, o_seg, d_seg,
        k_seg, y_seg, n_seg, i_seg,
        ng_seg, g_seg, a_seg])
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
    print("ÞĒOD-CYNINGA RECONSTRUCTION v1")
    print("Old English [θeːodkyniŋɡɑ]")
    print("Beowulf line 2, word 1")
    print()

    tc_dry = synth_theod_cyninga(
        pitch_hz=145.0, dil=1.0,
        add_room=False)
    write_wav(
        "output_play/theod_cyninga_dry.wav",
        tc_dry, SR)
    print(f"  theod_cyninga_dry.wav"
          f"  ({len(tc_dry)/SR*1000:.0f} ms)")

    tc_hall = synth_theod_cyninga(
        pitch_hz=145.0, dil=1.0,
        add_room=True)
    write_wav(
        "output_play/theod_cyninga_hall.wav",
        tc_hall, SR)
    print("  theod_cyninga_hall.wav")

    tc_slow = ola_stretch(tc_dry, 4.0)
    write_wav(
        "output_play/theod_cyninga_slow.wav",
        tc_slow, SR)
    print("  theod_cyninga_slow.wav")

    tc_perf = synth_theod_cyninga(
        pitch_hz=110.0, dil=2.5,
        add_room=True)
    write_wav(
        "output_play/"
        "theod_cyninga_performance.wav",
        tc_perf, SR)
    print(f"  theod_cyninga_performance.wav"
          f"  ({len(tc_perf)/SR*1000:.0f} ms)")

    for name, seg in [
        ("th", synth_TH(EE_F, 1.0, SR)),
        ("y",  synth_Y_short(
            K_F, N_F, 145.0, 1.0, SR)),
        ("ng", synth_NG(
            I_F, G_F, 145.0, 1.0, SR)),
        ("o",  synth_O_short(
            EE_F, D_F, 145.0, 1.0, SR)),
    ]:
        write_wav(
            f"output_play/"
            f"theod_cyninga_{name}"
            f"_isolated.wav",
            ola_stretch(seg / (
                np.max(np.abs(seg))+1e-8)
                * 0.75, 4.0), SR)
        print(f"  theod_cyninga_{name}"
              f"_isolated.wav  (4x slow)")

    print()
    print("  afplay output_play/"
          "theod_cyninga_th_isolated.wav")
    print("  afplay output_play/"
          "theod_cyninga_y_isolated.wav")
    print("  afplay output_play/"
          "theod_cyninga_ng_isolated.wav")
    print("  afplay output_play/"
          "theod_cyninga_dry.wav")
    print("  afplay output_play/"
          "theod_cyninga_performance.wav")
    print("  afplay output_play/"
          "theod_cyninga_hall.wav")
    print()
