"""
ÞÆS RECONSTRUCTION
Old English: þæs
Meaning: of that (genitive singular demonstrative)
IPA: [θæs]
Beowulf: Line 8, word 4 (overall word 34)
February 2026

PHONEME STRUCTURE:
  TH  [θ]   voiceless dental fricative    — verified
  AE  [æ]   open front unrounded          — verified
  S   [s]   voiceless alveolar fricative  — verified

NEW PHONEMES: none
Pure assembly. All three phonemes from verified inventory.

SYLLABLE STRUCTURE:
  Monosyllabic: [θæs]
  Stressed — genitive pronoun in performance position.

COARTICULATION NOTES:
  [θ] → [æ]:
    Dental fricative into open front vowel.
    F_next for [θ] = AE_F.
    Tongue tip at upper teeth for [θ],
    then drops to open position for [æ].
    F1 rises sharply at transition.

  [æ] → [s]:
    Open front vowel into alveolar fricative.
    F_next for [æ] = high-frequency noise target.
    Tongue tip rises from open to alveolar
    position. F2 maintained through transition
    (both [æ] and [s] are front-of-mouth
    articulations — F2 stays high).

  [s] word-final:
    F_prev = AE_F.
    Alveolar sibilant close.
    High centroid — voiceless.
    Word boundary after [s].

FRICATION CONTRAST:
  [θ] centroid: ~3000–5500 Hz (dental)
  [s] centroid: ~7500 Hz (alveolar)
  Two voiceless fricatives in the same word.
  Onset and coda both voiceless.
  Nucleus [æ] voiced between them.
  The word is a voiced island between
  two voiceless shores.

CONTEXT:
  feasceaft funden, hē þæs frōfre gebād
  he of-that comfort waited
  þæs is the genitive object of gebād —
  waited for that, expected that.
  It refers back: that comfort, that relief,
  the thing that was coming.
  The genitive links the waiting to what
  is waited for. The grammar carries
  the anticipation.

PERFORMANCE PARAMETERS:
  pitch_hz     = 110.0
  dil          = 2.5
  rt60         = 2.0
  direct_ratio = 0.38

CHANGE LOG:
  v1 — initial parameters
       pure assembly — no new phonemes
"""

import numpy as np
from scipy.signal import lfilter, butter
import wave as wave_module
import os

SR    = 44100
DTYPE = np.float32

os.makedirs("output_play", exist_ok=True)


# ============================================================
# PARAMETERS — from verified inventory
# ============================================================

# TH — voiceless dental fricative [θ]
TH_DUR_MS   = 70.0
TH_NOISE_CF = 4500.0
TH_NOISE_BW = 3000.0
TH_GAIN     = 0.30

# AE — open front unrounded [æ]
AE_F     = [700.0, 1700.0, 2600.0, 3300.0]
AE_B     = [120.0,  150.0,  200.0,  280.0]
AE_GAINS = [ 16.0,    8.0,    1.5,    0.5]
AE_DUR_MS    = 60.0
AE_COART_ON  = 0.12
AE_COART_OFF = 0.12

# S — voiceless alveolar fricative [s]
S_DUR_MS   = 65.0
S_NOISE_CF = 7500.0
S_NOISE_BW = 4000.0
S_GAIN     = 0.40

PITCH_HZ   = 145.0
PITCH_PERF = 110.0
DIL        = 1.0
DIL_PERF   = 2.5


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

def ola_stretch(sig, factor=4.0, sr=SR):
    win_ms   = 40.0
    win_n    = int(win_ms / 1000.0 * sr)
    if win_n % 2 == 1:
        win_n += 1
    hop_in   = win_n // 4
    hop_out  = int(hop_in * factor)
    window   = np.hanning(win_n).astype(DTYPE)
    n_in     = len(sig)
    n_frames = max(1, (n_in - win_n) // hop_in + 1)
    n_out    = hop_out * n_frames + win_n
    out      = np.zeros(n_out, dtype=DTYPE)
    norm     = np.zeros(n_out, dtype=DTYPE)
    for i in range(n_frames):
        in_pos  = i * hop_in
        out_pos = i * hop_out
        if in_pos + win_n > n_in:
            break
        frame = sig[in_pos:in_pos+win_n] * window
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
            src[i] = (phase / oq) * (2 - phase / oq)
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

def synth_TH(F_next=None, dil=DIL, sr=SR):
    """
    Voiceless dental fricative [θ].
    Tongue tip at upper teeth.
    Broad, diffuse noise — lower centroid
    than [s], higher than [x].
    Centroid target: 3000–5500 Hz.
    """
    dur_ms = TH_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    noise  = np.random.randn(n_s).astype(float)
    lo_    = max(TH_NOISE_CF - TH_NOISE_BW / 2,
                 200.0)
    hi_    = min(TH_NOISE_CF + TH_NOISE_BW / 2,
                 sr * 0.48)
    b_bp, a_bp = safe_bp(lo_, hi_, sr)
    fric   = lfilter(b_bp, a_bp, noise)
    n_atk  = min(int(0.010 * sr), n_s // 4)
    n_dec  = min(int(0.015 * sr), n_s // 4)
    env    = np.ones(n_s, dtype=float)
    if n_atk < n_s:
        env[:n_atk]  = np.linspace(0.0, 1.0, n_atk)
    if n_dec < n_s:
        env[-n_dec:] = np.linspace(1.0, 0.3, n_dec)
    fric   = f32(fric * env * TH_GAIN)
    mx     = np.max(np.abs(fric))
    if mx > 1e-8:
        fric = f32(fric / mx * 0.38)
    return f32(fric)


def synth_AE(F_prev=None, F_next=None,
              pitch_hz=PITCH_HZ,
              dil=DIL, sr=SR):
    """
    Open front unrounded [æ].
    High F1 (700 Hz) — wide jaw opening.
    Mid-high F2 (1700 Hz) — front position.
    First verified phoneme — HWÆT.
    """
    dur_ms = AE_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    T      = 1.0 / sr
    src    = rosenberg_pulse(n_s, pitch_hz,
                              oq=0.65, sr=sr)
    n_atk  = min(int(0.010 * sr), n_s // 4)
    n_rel  = min(int(0.015 * sr), n_s // 4)
    env    = np.ones(n_s, dtype=DTYPE)
    if n_atk < n_s:
        env[:n_atk]  = np.linspace(0.4, 1.0, n_atk)
    if n_rel < n_s:
        env[-n_rel:] = np.linspace(1.0, 0.6, n_rel)
    src    = f32(src * env)
    n_on   = int(AE_COART_ON  * n_s)
    n_off  = int(AE_COART_OFF * n_s)
    fp     = F_prev if F_prev is not None else AE_F
    fn     = F_next if F_next is not None else AE_F
    result = np.zeros(n_s, dtype=DTYPE)
    for fi in range(len(AE_F)):
        f_s   = float(fp[fi]) if fi < len(fp) \
                else float(AE_F[fi])
        f_e   = float(fn[fi]) if fi < len(fn) \
                else float(AE_F[fi])
        f_b   = float(AE_F[fi])
        f_arr = np.full(n_s, f_b, dtype=DTYPE)
        if n_on > 0:
            f_arr[:n_on]  = np.linspace(
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
        result = f32(result / mx * 0.70)
    return f32(result)


def synth_S(F_prev=None, dil=DIL, sr=SR):
    """
    Voiceless alveolar fricative [s].
    Highest centroid in the inventory.
    Target: ~7500 Hz.
    Place distinction from [θ]: ~4000+ Hz
    separation. Alveolar clearly above dental.
    """
    dur_ms = S_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    noise  = np.random.randn(n_s).astype(float)
    lo_    = max(S_NOISE_CF - S_NOISE_BW / 2,
                 200.0)
    hi_    = min(S_NOISE_CF + S_NOISE_BW / 2,
                 sr * 0.48)
    b_bp, a_bp = safe_bp(lo_, hi_, sr)
    fric   = lfilter(b_bp, a_bp, noise)
    n_atk  = min(int(0.008 * sr), n_s // 4)
    n_dec  = min(int(0.015 * sr), n_s // 4)
    env    = np.ones(n_s, dtype=float)
    if n_atk < n_s:
        env[:n_atk]  = np.linspace(0.0, 1.0, n_atk)
    if n_dec < n_s:
        env[-n_dec:] = np.linspace(1.0, 0.2, n_dec)
    fric   = f32(fric * env * S_GAIN)
    mx     = np.max(np.abs(fric))
    if mx > 1e-8:
        fric = f32(fric / mx * 0.50)
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

def synth_þæs(pitch_hz=PITCH_HZ,
               dil=DIL,
               add_room=False,
               sr=SR):
    """
    [θ · æ · s]
    Monosyllabic. Stressed.
    Two voiceless fricatives framing
    one voiced open front vowel.
    [θ] dental onset — diffuse noise
    [æ] voiced island — high F1, mid-high F2
    [s] alveolar coda — sharp high noise
    """
    th_seg = synth_TH(
        F_next=AE_F,
        dil=dil, sr=sr)
    ae_seg = synth_AE(
        F_prev=None,
        F_next=None,   # word boundary → H
        pitch_hz=pitch_hz,
        dil=dil, sr=sr)
    s_seg  = synth_S(
        F_prev=AE_F,
        dil=dil, sr=sr)
    word   = np.concatenate([th_seg, ae_seg, s_seg])
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
    print("ÞÆS RECONSTRUCTION v1")
    print("Old English [θæs]")
    print("Beowulf line 8, word 4")
    print("Pure assembly — no new phonemes")
    print()

    w_dry = synth_þæs(
        pitch_hz=PITCH_HZ, dil=DIL,
        add_room=False)
    write_wav("output_play/þæs_dry.wav",
               w_dry, SR)
    print(f"  þæs_dry.wav"
          f"  ({len(w_dry)/SR*1000:.0f} ms)")

    w_hall = synth_þæs(
        pitch_hz=PITCH_HZ, dil=DIL,
        add_room=True)
    write_wav("output_play/þæs_hall.wav",
               w_hall, SR)
    print("  þæs_hall.wav")

    w_slow = ola_stretch(w_dry, 4.0)
    write_wav("output_play/þæs_slow.wav",
               w_slow, SR)
    print("  þæs_slow.wav")

    w_perf = synth_þæs(
        pitch_hz=PITCH_PERF,
        dil=DIL_PERF,
        add_room=True)
    write_wav("output_play/þæs_perf.wav",
               w_perf, SR)
    print(f"  þæs_perf.wav"
          f"  ({len(w_perf)/SR*1000:.0f} ms)"
          f"  [110 Hz, dil 2.5, hall]")
    print()
    print("  afplay output_play/þæs_dry.wav")
    print("  afplay output_play/þæs_slow.wav")
    print("  afplay output_play/þæs_hall.wav")
    print("  afplay output_play/þæs_perf.wav")
    print()
    print("  hē þæs —")
    print("  he of-that —")
    print()
