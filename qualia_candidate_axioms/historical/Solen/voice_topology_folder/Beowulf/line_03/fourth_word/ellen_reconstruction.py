"""
ELLEN RECONSTRUCTION
Old English: ellen
Meaning: courage, strength, zeal
IPA: [ellen]
Beowulf: Line 3, Word 4 (overall word 12)
February 2026

PHONEME STRUCTURE:
  E    [e]   short close-mid front   — verified
  LL   [lː]  geminate lateral        — NEW PHENOMENON
  E    [e]   short close-mid front   — verified
  N    [n]   voiced alveolar nasal   — verified

NEW PHENOMENON:
  Geminate [lː]:
  Phonemically long consonant.
  Same articulation as singleton [l].
  Duration ~130 ms — approximately 2×
  singleton duration of 65 ms.
  Steady-state plateau extended.
  Onset and offset transitions identical
  to singleton but body is doubled.
  Phonemically contrastive in OE:
    calan  [kɑlɑn]  — to be cold
    callan [kɑllɑn] — to call
  Duration is the sole acoustic cue.
  Formant targets identical to [l].
  Antiformant identical to [l].

REUSED PHONEMES:
  [e]:  GĀR-DENA, GEFRŪNON, ÆÞELINGAS
  [l]:  ÆÞELINGAS
  [n]:  multiple instances

MORPHOLOGICAL NOTE:
  ellen — neuter a-stem noun.
  Meaning: courage, strength, zeal,
  vigorous effort in battle.
  A core heroic vocabulary word.
  Appears throughout Beowulf —
  the poem is saturated with ellen.
  The compound ellenrōf (courage-famous)
  is a common epithet for warriors.
  Modern English cognate: none surviving.
  Gothic cognate: *aljan.
  The concept survives in the name
  Ellen/Helen through a separate
  borrowing pathway — unrelated.

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

# E — short close-mid front [e]
E_F      = [370.0, 2100.0, 2800.0, 3300.0]
E_B      = [ 80.0,  120.0,  170.0,  240.0]
E_GAINS  = [ 18.0,    9.0,    1.5,    0.5]
E_DUR_MS = 60.0
E_COART_ON  = 0.12
E_COART_OFF = 0.12

# L — singleton [l]
L_F       = [300.0,  950.0, 2500.0, 3200.0]
L_B       = [100.0,  200.0,  300.0,  350.0]
L_GAINS   = [ 10.0,    6.0,    2.0,    0.5]
L_DUR_MS  = 65.0
L_ANTI_F  = 1900.0
L_ANTI_BW = 300.0

# LL — geminate [lː]
# Same formant targets as [l].
# Duration 2× singleton = 130 ms.
# Longer steady-state plateau.
# Onset and offset transitions same
# absolute duration as singleton —
# the extra duration is all plateau.
LL_DUR_MS = 130.0   # 2× L_DUR_MS

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
             dil=DIL, sr=SR,
             geminate=False):
    """
    Voiced alveolar lateral [l] or [lː].
    geminate=True: duration 2× singleton.
    Extra duration all in plateau —
    onset and offset transitions are
    the same absolute length as singleton.
    """
    dur_ms = (LL_DUR_MS if geminate
              else L_DUR_MS) * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    src    = rosenberg_pulse(n_s, pitch_hz,
                              oq=0.65, sr=sr)
    # Transitions: fixed absolute duration
    # regardless of geminate/singleton.
    # Extra length = extended plateau only.
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
    result = iir_notch(
        result, fc=L_ANTI_F,
        bw=L_ANTI_BW, sr=sr)
    mx = np.max(np.abs(result))
    if mx > 1e-8:
        result = f32(result / mx * 0.60)
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

def synth_ellen(pitch_hz=PITCH_HZ,
                 dil=DIL,
                 add_room=False,
                 sr=SR):
    """[e·lː·e·n]"""
    e1_seg = synth_E_short(
        F_prev=E_F, F_next=L_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    ll_seg = synth_L(
        F_prev=E_F, F_next=E_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr,
        geminate=True)
    e2_seg = synth_E_short(
        F_prev=L_F, F_next=N_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    n_seg  = synth_N_final(
        F_prev=E_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    word   = np.concatenate([
        e1_seg, ll_seg, e2_seg, n_seg])
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
    print("ELLEN RECONSTRUCTION v1")
    print("Old English [ellen]")
    print("Beowulf line 3, word 4")
    print()

    w_dry = synth_ellen(
        pitch_hz=145.0, dil=1.0,
        add_room=False)
    write_wav(
        "output_play/ellen_dry.wav",
        w_dry, SR)
    print(f"  ellen_dry.wav"
          f"  ({len(w_dry)/SR*1000:.0f} ms)")

    w_hall = synth_ellen(
        pitch_hz=145.0, dil=1.0,
        add_room=True)
    write_wav(
        "output_play/ellen_hall.wav",
        w_hall, SR)
    print("  ellen_hall.wav")

    w_slow = ola_stretch(w_dry, 4.0)
    write_wav(
        "output_play/ellen_slow.wav",
        w_slow, SR)
    print("  ellen_slow.wav")

    w_perf = synth_ellen(
        pitch_hz=110.0, dil=2.5,
        add_room=True)
    write_wav(
        "output_play/ellen_performance.wav",
        w_perf, SR)
    print(f"  ellen_performance.wav"
          f"  ({len(w_perf)/SR*1000:.0f} ms)")

    # Geminate vs singleton comparison
    ll_seg = synth_L(E_F, E_F,
                      145.0, 1.0, SR,
                      geminate=True)
    l_seg  = synth_L(E_F, E_F,
                      145.0, 1.0, SR,
                      geminate=False)
    write_wav(
        "output_play/ellen_ll_geminate.wav",
        ola_stretch(ll_seg / (
            np.max(np.abs(ll_seg))+1e-8)
            * 0.75, 4.0), SR)
    write_wav(
        "output_play/ellen_l_singleton.wav",
        ola_stretch(l_seg / (
            np.max(np.abs(l_seg))+1e-8)
            * 0.75, 4.0), SR)
    print("  ellen_ll_geminate.wav  (4x slow)")
    print("  ellen_l_singleton.wav  (4x slow)")
    print()
    print("  afplay output_play/"
          "ellen_l_singleton.wav")
    print("  afplay output_play/"
          "ellen_ll_geminate.wav")
    print("  afplay output_play/ellen_dry.wav")
    print("  afplay output_play/ellen_slow.wav")
    print("  afplay output_play/ellen_hall.wav")
    print()
