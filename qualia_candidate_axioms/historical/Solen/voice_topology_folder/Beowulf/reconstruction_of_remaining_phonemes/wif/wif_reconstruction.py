"""
WĪF RECONSTRUCTION
Old English: wīf
Meaning: woman, wife
IPA: [wiːf]
Purpose: Verify [iː] — long close front unrounded
Inventory completion series — word 1 of 4
February 2026

PHONEME STRUCTURE:
  W   [w]    voiced labio-velar approx.  — verified WĒ
  Ī   [iː]   long close front unrounded  — NEW
  F   [f]    voiceless labiodental fric. — verified GEFRŪNON

NEW PHONEMES:
  [iː]: long close front unrounded.
        Tongue maximum height,
        maximum front position.
        Lips spread or neutral.
        F1 very low:  ~300 Hz
        F2 very high: ~2300 Hz
        Highest F2 in inventory.
        Duration ~110 ms — long vowel.
        ~double short vowel duration.

        Distinct from [ɪ]:
          [ɪ]: F1 ~400, F2 ~1700 Hz
               near-close, short
          [iː]: F1 ~300, F2 ~2300 Hz
               fully close, long

        Distinct from [y]:
          [y]: F1 ~300, F2 ~1500 Hz
               close front ROUNDED
          [iː]: F1 ~300, F2 ~2300 Hz
               close front UNROUNDED
          Rounding pulls F2 down
          ~800 Hz. F2 is the
          rounding diagnostic.

        Great Vowel Shift:
          OE [iː] → ME [iː] → ModE [aɪ]
          [wiːf] → [waɪf]
          Highest vowel had nowhere
          to go but diphthongise.

ETYMOLOGY:
  wīf — woman, wife.
  One of oldest Germanic words.
  ModE 'wife' direct descendant.
  Also: 'woman' from 'wīf-mann'.
  The [iː] → [aɪ] shift is the
  Great Vowel Shift in one word.

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
W_F      = [300.0,  700.0, 2200.0, 3000.0]
W_B      = [100.0,  150.0,  250.0,  300.0]
W_GAINS  = [ 14.0,    6.0,    1.5,    0.4]
W_DUR_MS = 55.0
W_COART_ON  = 0.15
W_COART_OFF = 0.15

# IY — long close front unrounded [iː]
# NEW PHONEME
# F1 very low ~300 Hz — maximum close
# F2 very high ~2300 Hz — maximum front
# Duration ~110 ms — long vowel
# Lips spread/neutral — no rounding
IY_F      = [300.0, 2300.0, 3000.0, 3500.0]
IY_B      = [ 80.0,  120.0,  200.0,  260.0]
IY_GAINS  = [ 16.0,    8.0,    1.5,    0.5]
IY_DUR_MS = 110.0
IY_COART_ON  = 0.10
IY_COART_OFF = 0.10

# F — voiceless labiodental fricative [f]
F_DUR_MS   = 70.0
F_NOISE_CF = 7000.0
F_NOISE_BW = 5000.0
F_GAIN     = 0.28

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
    dur_ms = W_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    T      = 1.0 / sr
    src    = rosenberg_pulse(n_s, pitch_hz,
                              oq=0.65, sr=sr)
    n_atk  = min(int(0.010 * sr), n_s // 4)
    n_rel  = min(int(0.010 * sr), n_s // 4)
    env    = np.ones(n_s, dtype=DTYPE)
    if n_atk < n_s:
        env[:n_atk] = np.linspace(
            0.3, 1.0, n_atk)
    if n_rel < n_s:
        env[-n_rel:] = np.linspace(
            1.0, 0.3, n_rel)
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
        result = f32(result / mx * 0.58)
    return f32(result)


def synth_IY(F_prev=None, F_next=None,
              pitch_hz=PITCH_HZ,
              dil=DIL, sr=SR):
    """
    Long close front unrounded [iː].
    NEW PHONEME.
    F1 ~300 Hz — maximum close height.
    F2 ~2300 Hz — maximum front position.
    Highest F2 in the inventory.
    Duration 110 ms — long vowel.
    No lip rounding — lips spread
    or neutral.

    Contrast with [ɪ]:
      [ɪ]: F1 ~400, F2 ~1700 — near-close
      [iː]: F1 ~300, F2 ~2300 — fully close
      Both duration and F2 differ.

    Contrast with [y]:
      [y]: F1 ~300, F2 ~1500 — rounded
      [iː]: F1 ~300, F2 ~2300 — unrounded
      F2 difference ~800 Hz = rounding.
    """
    dur_ms = IY_DUR_MS * dil
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
    n_on   = int(IY_COART_ON  * n_s)
    n_off  = int(IY_COART_OFF * n_s)
    f_prev = F_prev if F_prev is not None \
             else IY_F
    f_next = F_next if F_next is not None \
             else IY_F
    result = np.zeros(n_s, dtype=DTYPE)
    for fi in range(len(IY_F)):
        f_s   = (float(f_prev[fi])
                 if fi < len(f_prev)
                 else float(IY_F[fi]))
        f_e   = (float(f_next[fi])
                 if fi < len(f_next)
                 else float(IY_F[fi]))
        f_b   = float(IY_F[fi])
        f_arr = np.full(n_s, f_b, dtype=DTYPE)
        if n_on > 0:
            f_arr[:n_on] = np.linspace(
                f_s, f_b, n_on)
        if n_off > 0:
            f_arr[-n_off:] = np.linspace(
                f_b, f_e, n_off)
        bw  = float(IY_B[fi])
        g   = float(IY_GAINS[fi])
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


def synth_F(F_prev=None, F_next=None,
             dil=DIL, sr=SR):
    dur_ms = F_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    noise  = np.random.randn(n_s).astype(float)
    lo_    = max(F_NOISE_CF - F_NOISE_BW/2,
                 200.0)
    hi_    = min(F_NOISE_CF + F_NOISE_BW/2,
                 sr * 0.48)
    b_bp, a_bp = safe_bp(lo_, hi_, sr)
    fric   = lfilter(b_bp, a_bp, noise)
    n_atk  = min(int(0.008 * sr), n_s // 4)
    n_dec  = min(int(0.015 * sr), n_s // 4)
    env    = np.ones(n_s, dtype=float)
    if n_atk < n_s:
        env[:n_atk] = np.linspace(
            0.0, 1.0, n_atk)
    if n_dec < n_s:
        env[-n_dec:] = np.linspace(
            1.0, 0.0, n_dec)
    fric   = f32(fric * env * F_GAIN)
    mx     = np.max(np.abs(fric))
    if mx > 1e-8:
        fric = f32(fric / mx * 0.40)
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

def synth_wif(pitch_hz=PITCH_HZ,
               dil=DIL,
               add_room=False,
               sr=SR):
    """[w·iː·f]"""
    w_seg  = synth_W(
        F_prev=None, F_next=IY_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    iy_seg = synth_IY(
        F_prev=W_F, F_next=None,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    f_seg  = synth_F(
        F_prev=IY_F, F_next=None,
        dil=dil, sr=sr)
    word   = np.concatenate([
        w_seg, iy_seg, f_seg])
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
    print("WĪF RECONSTRUCTION v1")
    print("Old English [wiːf]")
    print("Inventory completion — word 1 of 4")
    print("New phoneme: [iː]")
    print()

    w_dry = synth_wif(
        pitch_hz=145.0, dil=1.0,
        add_room=False)
    write_wav(
        "output_play/wif_dry.wav",
        w_dry, SR)
    print(f"  wif_dry.wav"
          f"  ({len(w_dry)/SR*1000:.0f} ms)")

    w_hall = synth_wif(
        pitch_hz=145.0, dil=1.0,
        add_room=True)
    write_wav(
        "output_play/wif_hall.wav",
        w_hall, SR)
    print("  wif_hall.wav")

    w_slow = ola_stretch(w_dry, 4.0)
    write_wav(
        "output_play/wif_slow.wav",
        w_slow, SR)
    print("  wif_slow.wav")

    iy_seg = synth_IY(W_F, None,
                       145.0, 1.0, SR)
    write_wav(
        "output_play/wif_iy_only.wav",
        ola_stretch(iy_seg / (
            np.max(np.abs(iy_seg))+1e-8)
            * 0.75, 4.0), SR)
    print("  wif_iy_only.wav  (4x slow)")
    print()
    print("  afplay output_play/"
          "wif_iy_only.wav")
    print("  afplay output_play/"
          "wif_dry.wav")
    print("  afplay output_play/"
          "wif_slow.wav")
    print()
    print("  Inventory completion progress:")
    print("  [iː] — pending verification")
    print("  [eːɑ] — pending")
    print("  [eːo] — pending")
    print("  [p]   — pending")
    print("  [b]   — pending (line 8)")
    print()
