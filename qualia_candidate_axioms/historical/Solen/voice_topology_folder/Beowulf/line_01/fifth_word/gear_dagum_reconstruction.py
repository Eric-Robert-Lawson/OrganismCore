"""
GĒAR-DAGUM RECONSTRUCTION
Old English: gēar-dagum
Meaning: in days of yore (dative plural)
IPA: [ɡeːɑrdɑɡum]
Beowulf: Line 1, Word 5
February 2026

CHANGE LOG:
  v1 — initial parameters
  v2 — M nasal fix:
    M_GAINS[1] 2.0→12.0
    M_B[1] 250→350 Hz
    Root cause: [m] murmur was a single
    spike at 129 Hz (Rosenberg fundamental).
    Second resonator at 1000 Hz had gain 2.0
    — too weak to produce murmur energy above
    400 Hz. Real [m] has broad energy
    200–800 Hz from nasal tract resonance.
    Widening M_B[1] and raising M_GAINS[1]
    fills the murmur region so the 1000 Hz
    antiformant is a dip within the spectrum
    rather than a cliff at the edge of it.
"""

import numpy as np
from scipy.signal import lfilter, butter
import wave as wave_module
import os

SR    = 44100
DTYPE = np.float32

os.makedirs("output_play", exist_ok=True)


# ============================================================
# PARAMETERS — v2
# ============================================================

G1_F          = [250.0, 2200.0, 3000.0, 3500.0]
G1_B          = [200.0,  250.0,  300.0,  350.0]
G1_CLOSURE_MS = 50.0
G1_BURST_MS   = 12.0
G1_BURST_CF   = 1500.0

EE_F      = [390.0, 2100.0, 2800.0, 3300.0]
EE_B      = [ 80.0,  120.0,  160.0,  220.0]
EE_GAINS  = [ 20.0,    8.0,    1.5,    0.5]
EE_DUR_MS = 160.0
EE_COART_ON  = 0.10
EE_COART_OFF = 0.10

A_F      = [840.0, 1150.0, 2500.0, 3300.0]
A_B      = [180.0,  120.0,  200.0,  280.0]
A_GAINS  = [ 16.0,    5.0,    1.2,    0.4]
A_DUR_MS = 65.0
A_COART_ON  = 0.12
A_COART_OFF = 0.12

R_F          = [450.0, 1350.0, 1690.0, 3200.0]
R_B          = [100.0,  150.0,  200.0,  280.0]
R_GAINS      = [ 15.0,    4.0,    2.0,    0.5]
R_CLOSURE_MS = 35.0
R_OPEN_MS    = 20.0
R_N_CLOSURES = 2

D_F          = [250.0, 1800.0, 2600.0, 3400.0]
D_B          = [200.0,  220.0,  280.0,  320.0]
D_CLOSURE_MS = 45.0
D_BURST_MS   = 10.0
D_BURST_CF   = 3500.0

G2_F          = [250.0, 1000.0, 2600.0, 3200.0]
G2_B          = [200.0,  220.0,  280.0,  330.0]
G2_CLOSURE_MS = 50.0
G2_BURST_MS   = 12.0
G2_BURST_CF   = 1200.0

U_F      = [300.0,  700.0, 2200.0, 3100.0]
U_B      = [ 80.0,  100.0,  200.0,  280.0]
U_GAINS  = [ 16.0,   12.0,    1.0,    0.3]
U_DUR_MS = 60.0
U_COART_ON  = 0.15
U_COART_OFF = 0.15

# FIX v2: M_GAINS[1] 2.0→12.0, M_B[1] 250→350
M_F       = [250.0, 1000.0, 2200.0, 3000.0]
M_B       = [120.0,  350.0,  350.0,  400.0]
M_GAINS   = [  8.0,   12.0,    1.0,    0.2]
M_DUR_MS  = 60.0
M_ANTI_F  = 1000.0
M_ANTI_BW = 200.0

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

def synth_G(F_next, burst_cf,
             closure_ms, burst_ms,
             G_F, G_B,
             pitch_hz=PITCH_HZ,
             dil=DIL, sr=SR):
    n_cl  = max(4, int(
        closure_ms * dil / 1000.0 * sr))
    n_bst = max(4, int(
        burst_ms * dil / 1000.0 * sr))
    src_cl = rosenberg_pulse(
        n_cl, pitch_hz, oq=0.65, sr=sr)
    b, a   = safe_lp(400.0, sr)
    bar    = f32(lfilter(
        b, a, src_cl.astype(float)) * 0.05)
    noise  = f32(np.random.randn(n_bst) * 0.15)
    b2, a2 = safe_bp(
        burst_cf - 300.0,
        burst_cf + 300.0, sr)
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


def synth_A_short(F_prev, F_next,
                   pitch_hz=PITCH_HZ,
                   dil=DIL, sr=SR):
    dur_ms = A_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    T      = 1.0 / sr
    src    = rosenberg_pulse(n_s, pitch_hz,
                              oq=0.65, sr=sr)
    n_atk  = min(int(0.012 * sr), n_s // 4)
    n_rel  = min(int(0.030 * sr), n_s // 4)
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
    result = np.zeros(n_s, dtype=DTYPE)
    for fi in range(len(A_F)):
        f_s   = (float(F_prev[fi])
                 if fi < len(F_prev)
                 else float(A_F[fi]))
        f_e   = (float(F_next[fi])
                 if fi < len(F_next)
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
        result = f32(result / mx * 0.65)
    return f32(result)


def synth_R_trill(F_prev, F_next,
                   pitch_hz=PITCH_HZ,
                   dil=DIL, sr=SR):
    n_cl = max(2, int(
        R_CLOSURE_MS * dil / 1000.0 * sr))
    n_op = max(2, int(
        R_OPEN_MS * dil / 1000.0 * sr))
    T    = 1.0 / sr

    def closure_seg():
        src  = rosenberg_pulse(
            n_cl, pitch_hz, oq=0.65, sr=sr)
        b, a = safe_lp(300.0, sr)
        return f32(lfilter(
            b, a, src.astype(float)) * 0.015)

    def open_seg(f_s, f_e):
        src    = rosenberg_pulse(
            n_op, pitch_hz, oq=0.65, sr=sr)
        result = np.zeros(n_op, dtype=DTYPE)
        for fi in range(len(R_F)):
            f_arr = np.linspace(
                float(f_s[fi]),
                float(f_e[fi]),
                n_op, dtype=DTYPE)
            bw  = float(R_B[fi])
            g   = float(R_GAINS[fi])
            y1 = y2 = 0.0
            out = np.zeros(n_op, dtype=DTYPE)
            for i in range(n_op):
                fc  = max(20.0, min(
                    sr*0.48,
                    float(f_arr[i])))
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

    segments = [open_seg(F_prev, R_F)]
    for i in range(R_N_CLOSURES):
        segments.append(closure_seg())
        if i < R_N_CLOSURES - 1:
            segments.append(open_seg(R_F, R_F))
        else:
            segments.append(
                open_seg(R_F, F_next))
    trill = np.concatenate(segments)
    mx    = np.max(np.abs(trill))
    if mx > 1e-8:
        trill = f32(trill / mx * 0.65)
    return f32(trill)


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


def synth_U_short(F_prev, F_next,
                   pitch_hz=PITCH_HZ,
                   dil=DIL, sr=SR):
    dur_ms = U_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    T      = 1.0 / sr
    src    = rosenberg_pulse(n_s, pitch_hz,
                              oq=0.65, sr=sr)
    n_atk  = min(int(0.012 * sr), n_s // 4)
    n_rel  = min(int(0.020 * sr), n_s // 4)
    env    = np.ones(n_s, dtype=DTYPE)
    if n_atk < n_s:
        env[:n_atk] = np.linspace(
            0.3, 1.0, n_atk)
    if n_rel < n_s:
        env[-n_rel:] = np.linspace(
            1.0, 0.6, n_rel)
    src    = f32(src * env)
    n_on   = int(U_COART_ON  * n_s)
    n_off  = int(U_COART_OFF * n_s)
    f_prev = F_prev if F_prev is not None \
             else U_F
    f_next = F_next if F_next is not None \
             else M_F
    result = np.zeros(n_s, dtype=DTYPE)
    for fi in range(len(U_F)):
        f_s   = (float(f_prev[fi])
                 if fi < len(f_prev)
                 else float(U_F[fi]))
        f_e   = (float(f_next[fi])
                 if fi < len(f_next)
                 else float(U_F[fi]))
        f_b   = float(U_F[fi])
        f_arr = np.full(n_s, f_b, dtype=DTYPE)
        if n_on > 0:
            f_arr[:n_on] = np.linspace(
                f_s, f_b, n_on)
        if n_off > 0:
            f_arr[-n_off:] = np.linspace(
                f_b, f_e, n_off)
        bw  = float(U_B[fi])
        g   = float(U_GAINS[fi])
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


def synth_M_final(F_prev=None,
                   pitch_hz=PITCH_HZ,
                   dil=DIL, sr=SR):
    dur_ms = M_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    T      = 1.0 / sr
    src    = rosenberg_pulse(n_s, pitch_hz,
                              oq=0.65, sr=sr)
    n_tr  = min(int(0.015 * sr), n_s // 4)
    n_dec = min(int(0.040 * sr), n_s // 2)
    env   = np.ones(n_s, dtype=DTYPE)
    if n_tr < n_s:
        env[:n_tr] = np.linspace(
            0.4, 1.0, n_tr)
    if n_dec < n_s:
        env[-n_dec:] = np.linspace(
            1.0, 0.0, n_dec)
    src    = f32(src * env)
    result = apply_formants(
        src, M_F, M_B, M_GAINS, sr=sr)
    result = iir_notch(
        result,
        fc=M_ANTI_F,
        bw=M_ANTI_BW,
        sr=sr)
    mx = np.max(np.abs(result))
    if mx > 1e-8:
        result = f32(result / mx * 0.50)
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


def synth_gear_dagum(pitch_hz=PITCH_HZ,
                      dil=DIL,
                      add_room=False,
                      sr=SR):
    g1_seg = synth_G(
        F_next=EE_F,
        burst_cf=G1_BURST_CF,
        closure_ms=G1_CLOSURE_MS,
        burst_ms=G1_BURST_MS,
        G_F=G1_F, G_B=G1_B,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    ee_seg = synth_EE_long(
        F_prev=G1_F, F_next=A_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    a1_seg = synth_A_short(
        F_prev=EE_F, F_next=R_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    r_seg  = synth_R_trill(
        F_prev=A_F, F_next=D_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    d_seg  = synth_D(
        F_prev=R_F, F_next=A_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    a2_seg = synth_A_short(
        F_prev=D_F, F_next=G2_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    g2_seg = synth_G(
        F_next=U_F,
        burst_cf=G2_BURST_CF,
        closure_ms=G2_CLOSURE_MS,
        burst_ms=G2_BURST_MS,
        G_F=G2_F, G_B=G2_B,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    u_seg  = synth_U_short(
        F_prev=G2_F, F_next=M_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    m_seg  = synth_M_final(
        F_prev=U_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    word = np.concatenate([
        g1_seg, ee_seg, a1_seg, r_seg,
        d_seg, a2_seg, g2_seg, u_seg, m_seg])
    mx = np.max(np.abs(word))
    if mx > 1e-8:
        word = f32(word / mx * 0.75)
    if add_room:
        word = apply_simple_room(
            word, rt60=2.0,
            direct_ratio=0.38, sr=sr)
    return f32(word)


if __name__ == "__main__":
    print()
    print("GĒAR-DAGUM RECONSTRUCTION v2")
    print("Old English [ɡeːɑrdɑɡum]")
    print("Beowulf line 1, word 5")
    print()

    gd_dry = synth_gear_dagum(
        pitch_hz=145.0, dil=1.0,
        add_room=False)
    write_wav(
        "output_play/gear_dagum_dry.wav",
        gd_dry, SR)
    print(f"  gear_dagum_dry.wav"
          f"  ({len(gd_dry)/SR*1000:.0f} ms)")

    gd_hall = synth_gear_dagum(
        pitch_hz=145.0, dil=1.0,
        add_room=True)
    write_wav(
        "output_play/gear_dagum_hall.wav",
        gd_hall, SR)
    print("  gear_dagum_hall.wav")

    gd_slow = ola_stretch(gd_dry, 4.0)
    write_wav(
        "output_play/gear_dagum_slow.wav",
        gd_slow, SR)
    print("  gear_dagum_slow.wav")

    gd_perf = synth_gear_dagum(
        pitch_hz=110.0, dil=2.5,
        add_room=True)
    write_wav(
        "output_play/"
        "gear_dagum_performance.wav",
        gd_perf, SR)
    print(f"  gear_dagum_performance.wav"
          f"  ({len(gd_perf)/SR*1000:.0f} ms)")

    u_iso = synth_U_short(
        G2_F, M_F, 145.0, 1.0, SR)
    write_wav(
        "output_play/gear_dagum_u_isolated.wav",
        ola_stretch(u_iso, 4.0), SR)
    print("  gear_dagum_u_isolated.wav"
          "  (U vowel 4x slow)")

    m_iso = synth_M_final(U_F, 145.0, 1.0, SR)
    write_wav(
        "output_play/gear_dagum_m_isolated.wav",
        ola_stretch(m_iso, 4.0), SR)
    print("  gear_dagum_m_isolated.wav"
          "  (M nasal 4x slow)")

    print()
    print("  afplay output_play/"
          "gear_dagum_u_isolated.wav")
    print("  afplay output_play/"
          "gear_dagum_m_isolated.wav")
    print("  afplay output_play/"
          "gear_dagum_dry.wav")
    print("  afplay output_play/"
          "gear_dagum_performance.wav")
    print("  afplay output_play/"
          "gear_dagum_hall.wav")
    print()
