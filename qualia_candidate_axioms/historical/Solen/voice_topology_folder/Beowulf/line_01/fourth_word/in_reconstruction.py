"""
IN RECONSTRUCTION
Old English: in
Meaning: in
IPA: [ɪn]
Beowulf: Line 1, Word 4
February 2026

PHONEME STRUCTURE:
  I   [ɪ]   short near-close near-front vowel
  N   [n]   voiced alveolar nasal

NOTES:
  [ɪ] is the lax high front vowel.
  Not [iː] (too high, too tense).
  Not [e] (too open).
  Not [ɛ] (too open).
  The vowel of Modern English 'bit', 'sit'.
  F1 low (~400 Hz) — near-close height.
  F2 high (~1800 Hz) — front, but lax,
  so lower than tense [iː] (~2300 Hz).
  Short duration — unstressed function word.

  [n] word-final nasal.
  Same phoneme as N in DENA.
  Slightly shorter — word-final position.
  No following vowel — nasal releases
  into silence, not into a vowel.
  Velum lowers during the vowel [ɪ]
  in anticipation of the nasal —
  the vowel will show slight nasalization
  in the final portion.

  IN as a function word:
  Unstressed in the line.
  Citation form reconstructed here.
  Connected-speech reduction handled
  when assembling the full line.

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
# PARAMETERS — v1
# ============================================================

# I vowel — short near-close near-front [ɪ]
# F1 low (~400 Hz) — near-close height
# F2 high (~1800 Hz) — front, lax
# Compare: [iː] F1=300, F2=2300 (tense, higher)
#          [e]  F1=370, F2=2200 (more open)
#          [ɪ]  F1=400, F2=1800 (lax, central)
I_F      = [400.0, 1800.0, 2600.0, 3300.0]
I_B      = [ 80.0,  120.0,  180.0,  250.0]
I_GAINS  = [ 18.0,   10.0,    1.5,    0.5]
I_DUR_MS = 65.0    # short — unstressed

I_COART_ON  = 0.15  # onset from silence/prev
I_COART_OFF = 0.20  # offset into nasal

# N nasal — voiced alveolar nasal [n]
# Word-final: slightly shorter than medial N
# Same formant/antiformant as DENA N
# but releases into silence
N_F       = [250.0,  1800.0, 2600.0, 3300.0]
N_B       = [100.0,   200.0,  300.0,  350.0]
N_GAINS   = [  8.0,    2.0,    0.5,    0.2]
N_DUR_MS  = 55.0   # shorter than medial (70ms)
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
# I — SHORT NEAR-CLOSE FRONT VOWEL [ɪ]
# ============================================================

def synth_I_short(F_prev=None, F_next=None,
                   pitch_hz=PITCH_HZ,
                   dil=DIL, sr=SR):
    """
    Short near-close near-front vowel [ɪ].

    F1 = 400 Hz — near-close height.
    F2 = 1800 Hz — front but lax.
      Lower than tense [iː] (2300 Hz).
      Lower than [e] (2200 Hz).
      The laxness of [ɪ] shows in F2.

    Word-initial onset from silence:
      Brief amplitude ramp, no preceding
      formant context — starts at I_F targets.
    Word-internal offset into nasal:
      F2 begins moving toward N_F[1]=1800 Hz
      in the final I_COART_OFF fraction.
      F2 of [ɪ] is already at 1800 Hz so
      the transition into N is smooth —
      F2 barely moves. F1 moves from
      400 Hz toward N_F[0]=250 Hz.
    """
    dur_ms = I_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    T      = 1.0 / sr

    src = rosenberg_pulse(n_s, pitch_hz,
                          oq=0.65, sr=sr)

    # Onset ramp
    n_atk = min(int(0.015 * sr), n_s // 4)
    # Offset: slight velum-lowering pre-nasal
    n_rel = min(int(0.020 * sr), n_s // 4)
    env   = np.ones(n_s, dtype=DTYPE)
    if n_atk < n_s:
        env[:n_atk] = np.linspace(
            0.3, 1.0, n_atk)
    if n_rel < n_s:
        env[-n_rel:] = np.linspace(
            1.0, 0.7, n_rel)
    src = f32(src * env)

    n_on  = int(I_COART_ON  * n_s)
    n_off = int(I_COART_OFF * n_s)

    # F_prev: if None, start at I_F
    # F_next: if None, end at I_F
    f_prev = F_prev if F_prev is not None \
             else I_F
    f_next = F_next if F_next is not None \
             else N_F  # default: into N

    result = np.zeros(n_s, dtype=DTYPE)
    for fi in range(len(I_F)):
        f_s   = (float(f_prev[fi])
                 if fi < len(f_prev)
                 else float(I_F[fi]))
        f_e   = (float(f_next[fi])
                 if fi < len(f_next)
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
        result = f32(result / mx * 0.70)
    return f32(result)


# ============================================================
# N — VOICED ALVEOLAR NASAL [n] (word-final)
# ============================================================

def synth_N_final(F_prev=None,
                   pitch_hz=PITCH_HZ,
                   dil=DIL, sr=SR):
    """
    Word-final voiced alveolar nasal [n].

    Shorter than medial N (55 ms vs 70 ms).
    Releases into silence — no following vowel.
    The release is a gentle amplitude decay
    rather than a formant transition.

    Antiformant at 800 Hz via IIR notch —
    same as medial N, same bandwidth 200 Hz.
    """
    dur_ms = N_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    T      = 1.0 / sr

    src = rosenberg_pulse(n_s, pitch_hz,
                          oq=0.65, sr=sr)

    # Word-final: onset from vowel, release
    # into silence
    n_tr = min(int(0.015 * sr), n_s // 4)
    # Longer decay at end — nasal murmur
    # fades into silence
    n_dec = min(int(0.040 * sr), n_s // 2)
    env   = np.ones(n_s, dtype=DTYPE)
    if n_tr < n_s:
        env[:n_tr] = np.linspace(
            0.4, 1.0, n_tr)
    if n_dec < n_s:
        env[-n_dec:] = np.linspace(
            1.0, 0.0, n_dec)
    src = f32(src * env)

    result = apply_formants(
        src, N_F, N_B, N_GAINS, sr=sr)
    result = iir_notch(
        result,
        fc=N_ANTI_F,
        bw=N_ANTI_BW,
        sr=sr)

    mx = np.max(np.abs(result))
    if mx > 1e-8:
        result = f32(result / mx * 0.50)
    return f32(result)


# ============================================================
# APPLY ROOM
# ============================================================

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

def synth_in(pitch_hz=PITCH_HZ,
              dil=DIL,
              add_room=False,
              sr=SR):
    """
    Synthesize Old English 'in' [ɪn].
    Word-initial onset from silence.
    Word-final nasal into silence.
    """
    i_seg = synth_I_short(
        F_prev=None,
        F_next=N_F,
        pitch_hz=pitch_hz,
        dil=dil, sr=sr)
    n_seg = synth_N_final(
        F_prev=I_F,
        pitch_hz=pitch_hz,
        dil=dil, sr=sr)

    word = np.concatenate([i_seg, n_seg])
    mx   = np.max(np.abs(word))
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
    print("IN RECONSTRUCTION v1")
    print("Old English [ɪn]")
    print("Beowulf line 1, word 4")
    print()

    in_dry = synth_in(
        pitch_hz=145.0, dil=1.0,
        add_room=False)
    write_wav("output_play/in_dry.wav",
              in_dry, SR)
    print(f"  in_dry.wav"
          f"  ({len(in_dry)/SR*1000:.0f} ms)")

    in_hall = synth_in(
        pitch_hz=145.0, dil=1.0,
        add_room=True)
    write_wav("output_play/in_hall.wav",
              in_hall, SR)
    print("  in_hall.wav")

    in_slow = ola_stretch(in_dry, 4.0)
    write_wav("output_play/in_slow.wav",
              in_slow, SR)
    print("  in_slow.wav")

    in_perf = synth_in(
        pitch_hz=110.0, dil=2.5,
        add_room=True)
    write_wav("output_play/in_performance.wav",
              in_perf, SR)
    print(f"  in_performance.wav"
          f"  ({len(in_perf)/SR*1000:.0f} ms)")

    i_iso = synth_I_short(
        F_prev=None, F_next=N_F,
        pitch_hz=145.0, dil=1.0, sr=SR)
    write_wav("output_play/in_i_isolated.wav",
              ola_stretch(i_iso, 4.0), SR)
    print("  in_i_isolated.wav  (I vowel 4x slow)")

    print()
    print("  afplay output_play/in_dry.wav")
    print("  afplay output_play/in_slow.wav")
    print("  afplay output_play/in_hall.wav")
    print("  afplay output_play/"
          "in_performance.wav")
    print()
