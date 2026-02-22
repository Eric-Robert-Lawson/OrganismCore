"""
WÆS RECONSTRUCTION
Old English: wæs
Meaning: was (3rd person singular past tense
         of wesan — to be)
IPA: [wæs]
Beowulf: Line 4, Word 2 (overall word 15)
February 2026

PHONEME STRUCTURE:
  W   [w]   voiced labio-velar approximant — verified WĒ
  Æ   [æ]   open front unrounded          — verified
  S   [s]   voiceless alveolar fricative  — verified ÆÞELINGAS

NEW PHONEMES: none.
Fourth pure assembly word in a row.

BOUNDARY NOTE:
  [æ]→[s] boundary:
  Voicing cuts as tongue moves to
  alveolar groove for [s].
  Vowel offset coarticulates toward
  [s] — F2 rises slightly toward
  alveolar place before voicing ends.
  [s] onset has very brief (~5 ms)
  amplitude ramp from silence.

MORPHOLOGICAL NOTE:
  wesan — to be (suppletive verb).
  wæs — 3rd person singular past.
  One of the most frequent words
  in all of Old English.
  Appears ~170 times in Beowulf.
  Direct ancestor of Modern English
  'was' — unchanged in function,
  minimally changed in form.
  [w] unchanged.
  [æ]→[ɒ] in ModE (vowel shift).
  [s] unchanged.

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

# W — voiced labio-velar approximant [w]
W_F      = [300.0,  610.0, 2200.0, 3100.0]
W_B      = [100.0,  150.0,  200.0,  280.0]
W_GAINS  = [ 10.0,    5.0,    1.5,    0.4]
W_DUR_MS = 55.0
W_COART_ON  = 0.20
W_COART_OFF = 0.20

# AE — open front unrounded [æ]
AE_F      = [700.0, 1700.0, 2600.0, 3300.0]
AE_B      = [130.0,  120.0,  200.0,  280.0]
AE_GAINS  = [ 18.0,    8.0,    1.5,    0.5]
AE_DUR_MS = 65.0
AE_COART_ON  = 0.12
AE_COART_OFF = 0.15   # slightly longer
                       # toward [s] offset

# S — voiceless alveolar fricative [s]
S_DUR_MS   = 80.0
S_NOISE_CF = 7000.0
S_NOISE_BW = 4000.0
S_GAIN     = 0.32
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
# PHONEME SYNTHESIZERS
# ============================================================

def synth_W(F_prev=None, F_next=None,
             pitch_hz=PITCH_HZ,
             dil=DIL, sr=SR):
    """
    Voiced labio-velar approximant [w].
    Word-initial — onset from silence.
    Glide toward [æ] formant targets.
    """
    dur_ms = W_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    T      = 1.0 / sr
    src    = rosenberg_pulse(n_s, pitch_hz,
                              oq=0.65, sr=sr)
    n_atk  = min(int(0.015 * sr), n_s // 4)
    n_rel  = min(int(0.015 * sr), n_s // 4)
    env    = np.ones(n_s, dtype=DTYPE)
    if n_atk < n_s:
        env[:n_atk] = np.linspace(
            0.2, 1.0, n_atk)
    if n_rel < n_s:
        env[-n_rel:] = np.linspace(
            1.0, 0.5, n_rel)
    src    = f32(src * env)
    n_on   = int(W_COART_ON  * n_s)
    n_off  = int(W_COART_OFF * n_s)
    f_prev = F_prev if F_prev is not None \
             else W_F
    f_next = F_next if F_next is not None \
             else W_F
    result = np.zeros(n_s, dtype=DTYPE)
    for fi in range(len(W_F)):
        f_s   = (float(f_prev[fi])
                 if fi < len(f_prev)
                 else float(W_F[fi]))
        f_e   = (float(f_next[fi])
                 if fi < len(f_next)
                 else float(W_F[fi]))
        f_b   = float(W_F[fi])
        f_arr = np.full(n_s, f_b, dtype=DTYPE)
        if n_on > 0:
            f_arr[:n_on] = np.linspace(
                f_s, f_b, n_on)
        if n_off > 0:
            f_arr[-n_off:] = np.linspace(
                f_b, f_e, n_off)
        bw  = float(W_B[fi])
        g   = float(W_GAINS[fi])
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


def synth_S(F_next=None, dil=DIL, sr=SR):
    """
    Voiceless alveolar fricative [s].
    Word-final position.
    Brief onset ramp from vowel offset.
    """
    dur_ms = S_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    noise  = np.random.randn(n_s).astype(float)
    b, a   = safe_bp(
        S_NOISE_CF - S_NOISE_BW / 2,
        min(S_NOISE_CF + S_NOISE_BW / 2,
            sr * 0.48), sr)
    fric   = lfilter(b, a, noise)
    hi_lim = min(S_GROOVE_CF
                 + S_GROOVE_BW / 2,
                 sr * 0.48)
    lo_lim = max(S_GROOVE_CF
                 - S_GROOVE_BW / 2,
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

def synth_waes(pitch_hz=PITCH_HZ,
                dil=DIL,
                add_room=False,
                sr=SR):
    """[w·æ·s]"""
    w_seg  = synth_W(
        F_prev=W_F, F_next=AE_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    ae_seg = synth_AE(
        F_prev=W_F, F_next=None,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    s_seg  = synth_S(
        F_next=None, dil=dil, sr=sr)
    word   = np.concatenate([
        w_seg, ae_seg, s_seg])
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
    print("WÆS RECONSTRUCTION v1")
    print("Old English [wæs]")
    print("Beowulf line 4, word 2")
    print()

    w_dry = synth_waes(
        pitch_hz=145.0, dil=1.0,
        add_room=False)
    write_wav(
        "output_play/waes_dry.wav",
        w_dry, SR)
    print(f"  waes_dry.wav"
          f"  ({len(w_dry)/SR*1000:.0f} ms)")

    w_hall = synth_waes(
        pitch_hz=145.0, dil=1.0,
        add_room=True)
    write_wav(
        "output_play/waes_hall.wav",
        w_hall, SR)
    print("  waes_hall.wav")

    w_slow = ola_stretch(w_dry, 4.0)
    write_wav(
        "output_play/waes_slow.wav",
        w_slow, SR)
    print("  waes_slow.wav")

    w_perf = synth_waes(
        pitch_hz=110.0, dil=2.5,
        add_room=True)
    write_wav(
        "output_play/waes_performance.wav",
        w_perf, SR)
    print(f"  waes_performance.wav"
          f"  ({len(w_perf)/SR*1000:.0f} ms)")

    print()
    print("  afplay output_play/waes_dry.wav")
    print("  afplay output_play/waes_slow.wav")
    print("  afplay output_play/waes_hall.wav")
    print()
    print("  Line 4 in progress:")
    print("  þæt wæs gōd cyning")
    print()
