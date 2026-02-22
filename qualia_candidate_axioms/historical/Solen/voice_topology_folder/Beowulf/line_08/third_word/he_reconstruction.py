```python
"""
HĒ RECONSTRUCTION
Old English: hē
Meaning: he (3sg masculine pronoun)
IPA: [heː]
Beowulf: Line 8, word 3 (overall word 33)
February 2026

PHONEME STRUCTURE:
  H   [h]   voiceless glottal fricative  — verified
  EY  [eː]  long close-mid front         — verified

NEW PHONEMES: none
Pure assembly. Both phonemes from verified inventory.

SYLLABLE STRUCTURE:
  Monosyllabic: [heː]
  Stressed — full pronoun in performance position.
  Long vowel at full duration.

THEORETICAL NOTE — [h] before vowel:
  [h] has no supralaryngeal constriction.
  The cavity shape during [h] is already
  the following vowel. The noise burst
  of [h] is shaped by [eː].
  F_next for [h] = [eː] formant targets.
  This is the physics of the glottal fricative.
  H is the origin of the vocal topology.
  [h] is the closest consonant to H.
  C([h],H) ≈ 0.90.

GHOST:
  Word-final [eː] → word boundary.
  Ghost returns toward H.
  Brief interword silence before ÞÆS begins.

CONTEXT:
  feasceaft funden, hē þæs frōfre gebād
  found wretched, he of-that comfort waited
  The pronoun introduces Scyld as subject
  of experience. He waited. He received.
  The scop who has been listing
  now centres a person.

PERFORMANCE PARAMETERS:
  pitch_hz = 110.0
  dil      = 2.5
  rt60     = 2.0
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

# H — voiceless glottal fricative [h]
H_DUR_MS   = 60.0
H_NOISE_CF = 2000.0
H_NOISE_BW = 3500.0
H_GAIN     = 0.30

# EY — long close-mid front unrounded [eː]
EY_F     = [450.0, 1900.0, 2600.0, 3300.0]
EY_B     = [100.0,  130.0,  200.0,  280.0]
EY_GAINS = [ 16.0,    8.0,    1.5,    0.5]
EY_DUR_MS    = 110.0
EY_COART_ON  = 0.10
EY_COART_OFF = 0.10

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
    win_ms  = 40.0
    win_n   = int(win_ms / 1000.0 * sr)
    if win_n % 2 == 1:
        win_n += 1
    hop_in  = win_n // 4
    hop_out = int(hop_in * factor)
    window  = np.hanning(win_n).astype(DTYPE)
    n_in    = len(sig)
    n_frames = max(1, (n_in - win_n) // hop_in + 1)
    n_out   = hop_out * n_frames + win_n
    out     = np.zeros(n_out, dtype=DTYPE)
    norm    = np.zeros(n_out, dtype=DTYPE)
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

def measure_voicing(seg, sr=SR):
    if len(seg) < 256:
        return 0.0
    n    = len(seg)
    core = seg[n//4: 3*n//4].astype(float)
    core -= np.mean(core)
    if np.max(np.abs(core)) < 1e-8:
        return 0.0
    acorr  = np.correlate(core, core, mode='full')
    acorr  = acorr[len(acorr)//2:]
    acorr /= (acorr[0] + 1e-12)
    lo = int(sr / 400)
    hi = min(int(sr / 80), len(acorr) - 1)
    if lo >= hi:
        return 0.0
    return float(np.clip(np.max(acorr[lo:hi]),
                          0.0, 1.0))

def measure_band_centroid(seg, lo_hz,
                           hi_hz, sr=SR):
    if len(seg) < 64:
        return 0.0
    spec  = np.abs(np.fft.rfft(
        seg.astype(float), n=2048))**2
    freqs = np.fft.rfftfreq(2048, d=1.0/sr)
    mask  = (freqs >= lo_hz) & (freqs <= hi_hz)
    total = np.sum(spec[mask])
    if total < 1e-12:
        return 0.0
    return float(np.sum(
        freqs[mask] * spec[mask]) / total)


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

def synth_H(F_next=None, dil=DIL, sr=SR):
    """
    Voiceless glottal fricative [h].
    No supralaryngeal constriction.
    Noise burst shaped by following vowel.
    F_next = EY_F — cavity is already [eː]
    during the aspiration.
    """
    dur_ms = H_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    noise  = np.random.randn(n_s).astype(float)
    lo_    = max(H_NOISE_CF - H_NOISE_BW / 2,
                 200.0)
    hi_    = min(H_NOISE_CF + H_NOISE_BW / 2,
                 sr * 0.48)
    b_bp, a_bp = safe_bp(lo_, hi_, sr)
    fric   = lfilter(b_bp, a_bp, noise)
    # Shape noise with following vowel F2
    # if available — glottal has no own place
    if F_next is not None and len(F_next) > 1:
        f2_next = float(F_next[1])
        lo2_ = max(f2_next * 0.5, 200.0)
        hi2_ = min(f2_next * 2.0, sr * 0.48)
        b2, a2 = safe_bp(lo2_, hi2_, sr)
        shaped = lfilter(b2, a2, noise)
        fric   = 0.6 * fric + 0.4 * shaped
    n_atk  = min(int(0.010 * sr), n_s // 4)
    n_dec  = min(int(0.020 * sr), n_s // 4)
    env    = np.ones(n_s, dtype=float)
    if n_atk < n_s:
        env[:n_atk]  = np.linspace(0.0, 1.0, n_atk)
    if n_dec < n_s:
        env[-n_dec:] = np.linspace(1.0, 0.4, n_dec)
    fric   = f32(fric * env * H_GAIN)
    mx     = np.max(np.abs(fric))
    if mx > 1e-8:
        fric = f32(fric / mx * 0.40)
    return f32(fric)


def synth_EY(F_prev=None, F_next=None,
              pitch_hz=PITCH_HZ,
              dil=DIL, sr=SR):
    """
    Long close-mid front unrounded [eː].
    Duration 110 ms * dil.
    F1 450, F2 1900, F3 2600, F4 3300.
    Highest voicing score of all short-context
    vowels — long duration inflates autocorr.
    """
    dur_ms = EY_DUR_MS * dil
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
    n_on   = int(EY_COART_ON  * n_s)
    n_off  = int(EY_COART_OFF * n_s)
    fp     = F_prev if F_prev is not None else EY_F
    fn     = F_next if F_next is not None else EY_F
    result = np.zeros(n_s, dtype=DTYPE)
    for fi in range(len(EY_F)):
        f_s   = float(fp[fi]) if fi < len(fp) \
                else float(EY_F[fi])
        f_e   = float(fn[fi]) if fi < len(fn) \
                else float(EY_F[fi])
        f_b   = float(EY_F[fi])
        f_arr = np.full(n_s, f_b, dtype=DTYPE)
        if n_on > 0:
            f_arr[:n_on]  = np.linspace(
                f_s, f_b, n_on)
        if n_off > 0:
            f_arr[-n_off:] = np.linspace(
                f_b, f_e, n_off)
        bw  = float(EY_B[fi])
        g   = float(EY_GAINS[fi])
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
        result = f32(result / mx * 0.75)
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

def synth_he(pitch_hz=PITCH_HZ,
              dil=DIL,
              add_room=False,
              sr=SR):
    """
    [h · eː]
    Monosyllabic. Stressed.
    [h] shaped by following [eː].
    [eː] long — 110 ms * dil.
    Word-final ghost to H at boundary.
    """
    h_seg  = synth_H(
        F_next=EY_F,
        dil=dil, sr=sr)
    ey_seg = synth_EY(
        F_prev=None,
        F_next=None,   # word boundary — return to H
        pitch_hz=pitch_hz,
        dil=dil, sr=sr)
    word   = np.concatenate([h_seg, ey_seg])
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
    print("HĒ RECONSTRUCTION v1")
    print("Old English [heː]")
    print("Beowulf line 8, word 3")
    print("Pure assembly — no new phonemes")
    print()

    w_dry = synth_he(
        pitch_hz=PITCH_HZ, dil=DIL,
        add_room=False)
    write_wav("output_play/he_dry.wav",
               w_dry, SR)
    print(f"  he_dry.wav"
          f"  ({len(w_dry)/SR*1000:.0f} ms)")

    w_hall = synth_he(
        pitch_hz=PITCH_HZ, dil=DIL,
        add_room=True)
    write_wav("output_play/he_hall.wav",
               w_hall, SR)
    print("  he_hall.wav")

    w_slow = ola_stretch(w_dry, 4.0)
    write_wav("output_play/he_slow.wav",
               w_slow, SR)
    print("  he_slow.wav")

    w_perf = synth_he(
        pitch_hz=PITCH_PERF,
        dil=DIL_PERF,
        add_room=True)
    write_wav("output_play/he_perf.wav",
               w_perf, SR)
    print(f"  he_perf.wav"
          f"  ({len(w_perf)/SR*1000:.0f} ms)"
          f"  [110 Hz, dil 2.5, hall]")
    print()
    print("  afplay output_play/he_dry.wav")
    print("  afplay output_play/he_slow.wav")
    print("  afplay output_play/he_hall.wav")
    print("  afplay output_play/he_perf.wav")
    print()
    print("  feasceaft funden, hē —")
    print("  found wretched, he —")
    print()
```
