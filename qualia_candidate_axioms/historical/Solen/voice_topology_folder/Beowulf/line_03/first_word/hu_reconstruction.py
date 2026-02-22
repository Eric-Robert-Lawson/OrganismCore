"""
HU RECONSTRUCTION
Old English: hu
Meaning: how
IPA: [xu]
Beowulf: Line 3, Word 1 (overall word 9)
February 2026

PHONEME STRUCTURE:
  H   [x]   voiceless velar fricative
  U   [u]   short close back rounded vowel

NEW PHONEMES:
  [x]: voiceless velar fricative.
       Back of tongue to velum.
       Frication at velar constriction.
       No voicing. No lip rounding.
       Centroid ~1500–3500 Hz — lower than
       [f] (~5800 Hz) and [θ] (~4200 Hz)
       because the velar constriction is
       further back. The longer front cavity
       in front of the constriction acts as
       a resonator that pulls frication
       energy toward lower frequencies.
       OE 'h' before back vowels = [x].
       Modern English 'how' descends from
       this word — the [x] weakened to [h]
       after the OE period.
       Duration: ~80 ms word-initial.

REUSED PHONEMES:
  [u]: verified GĒAR-DAGUM D8.
       F1=300 Hz, F2=700 Hz, 60 ms.

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

# X — voiceless velar fricative [x]
# Frication at velum — further back than
# any previous fricative.
# Lower centroid than [f] or [θ].
# Broad frication, no voicing.
X_DUR_MS   = 80.0
X_NOISE_CF = 2500.0   # velar frication center
X_NOISE_BW = 2000.0   # broad
X_GAIN     = 0.38
# Additional resonance from front cavity:
# the oral cavity in front of the velar
# constriction is a Helmholtz resonator
# that shapes the frication noise.
X_FRONT_CF = 1200.0
X_FRONT_BW = 800.0

# U — short close back rounded [u]
# Same as GĒAR-DAGUM
U_F      = [300.0,  700.0, 2200.0, 3100.0]
U_B      = [ 80.0,  100.0,  200.0,  280.0]
U_GAINS  = [ 16.0,   12.0,    1.0,    0.3]
U_DUR_MS = 65.0
U_COART_ON  = 0.15
U_COART_OFF = 0.20   # longer offset —
                      # word-final vowel

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
# PHONEME SYNTHESIZERS
# ============================================================

def synth_X(F_next=None, dil=DIL, sr=SR):
    """
    Voiceless velar fricative [x].
    Scottish 'loch', German 'Bach'.
    Frication at velar constriction.
    Lower centroid than [f] or [θ] —
    velar place is further back,
    the front cavity resonance pulls
    frication energy toward lower
    frequencies.
    No voicing. No lip rounding.
    """
    dur_ms = X_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    noise  = np.random.randn(n_s).astype(float)
    # Main velar frication band
    b, a   = safe_bp(
        X_NOISE_CF - X_NOISE_BW / 2,
        min(X_NOISE_CF + X_NOISE_BW / 2,
            sr * 0.48), sr)
    fric   = lfilter(b, a, noise)
    # Front cavity resonance below constriction
    b2, a2 = safe_bp(
        X_FRONT_CF - X_FRONT_BW / 2,
        X_FRONT_CF + X_FRONT_BW / 2, sr)
    fric  += lfilter(b2, a2, noise) * 0.5
    # Amplitude envelope
    n_atk  = min(int(0.020 * sr), n_s // 4)
    n_dec  = min(int(0.025 * sr), n_s // 4)
    env    = np.ones(n_s, dtype=float)
    if n_atk < n_s:
        env[:n_atk] = np.linspace(
            0.0, 1.0, n_atk)
    if n_dec < n_s:
        env[-n_dec:] = np.linspace(
            1.0, 0.2, n_dec)
    fric   = f32(fric * env * X_GAIN)
    mx     = np.max(np.abs(fric))
    if mx > 1e-8:
        fric = f32(fric / mx * 0.48)
    return f32(fric)


def synth_U_short(F_prev=None, F_next=None,
                   pitch_hz=PITCH_HZ,
                   dil=DIL, sr=SR):
    """
    Short close back rounded [u].
    Same parameters as GĒAR-DAGUM.
    Word-final here — longer offset decay.
    """
    dur_ms = U_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    T      = 1.0 / sr
    src    = rosenberg_pulse(n_s, pitch_hz,
                              oq=0.65, sr=sr)
    n_atk  = min(int(0.012 * sr), n_s // 4)
    n_rel  = min(int(0.040 * sr), n_s // 3)
    env    = np.ones(n_s, dtype=DTYPE)
    if n_atk < n_s:
        env[:n_atk] = np.linspace(
            0.3, 1.0, n_atk)
    if n_rel < n_s:
        env[-n_rel:] = np.linspace(
            1.0, 0.0, n_rel)
    src    = f32(src * env)
    n_on   = int(U_COART_ON  * n_s)
    n_off  = int(U_COART_OFF * n_s)
    f_prev = F_prev if F_prev is not None \
             else U_F
    f_next = F_next if F_next is not None \
             else U_F
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

def synth_hu(pitch_hz=PITCH_HZ,
              dil=DIL,
              add_room=False,
              sr=SR):
    """[x·u]"""
    x_seg = synth_X(
        F_next=U_F, dil=dil, sr=sr)
    u_seg = synth_U_short(
        F_prev=U_F, F_next=None,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    word  = np.concatenate([x_seg, u_seg])
    mx    = np.max(np.abs(word))
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
    print("HU RECONSTRUCTION v1")
    print("Old English [xu]")
    print("Beowulf line 3, word 1")
    print()

    hu_dry = synth_hu(
        pitch_hz=145.0, dil=1.0,
        add_room=False)
    write_wav(
        "output_play/hu_dry.wav",
        hu_dry, SR)
    print(f"  hu_dry.wav"
          f"  ({len(hu_dry)/SR*1000:.0f} ms)")

    hu_hall = synth_hu(
        pitch_hz=145.0, dil=1.0,
        add_room=True)
    write_wav(
        "output_play/hu_hall.wav",
        hu_hall, SR)
    print("  hu_hall.wav")

    hu_slow = ola_stretch(hu_dry, 4.0)
    write_wav(
        "output_play/hu_slow.wav",
        hu_slow, SR)
    print("  hu_slow.wav")

    hu_perf = synth_hu(
        pitch_hz=110.0, dil=2.5,
        add_room=True)
    write_wav(
        "output_play/hu_performance.wav",
        hu_perf, SR)
    print(f"  hu_performance.wav"
          f"  ({len(hu_perf)/SR*1000:.0f} ms)")

    x_seg = synth_X(U_F, 1.0, SR)
    write_wav(
        "output_play/hu_x_isolated.wav",
        ola_stretch(x_seg / (
            np.max(np.abs(x_seg))+1e-8)
            * 0.75, 4.0), SR)
    print("  hu_x_isolated.wav  (4x slow)")

    print()
    print("  afplay output_play/"
          "hu_x_isolated.wav")
    print("  afplay output_play/hu_dry.wav")
    print("  afplay output_play/hu_slow.wav")
    print("  afplay output_play/"
          "hu_performance.wav")
    print("  afplay output_play/hu_hall.wav")
    print()
