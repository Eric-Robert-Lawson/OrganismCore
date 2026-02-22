"""
WĒ RECONSTRUCTION
Old English [weː] — Beowulf line 1, word 2
February 2026

PHONEME STRUCTURE:
  W  — voiced labiovelar approximant onset
  Ē  — long close-mid front vowel [eː]

NOTES:
  W is the voiced counterpart of HW.
  Same labiovelar position, fully voiced,
  no aspiration noise.

  Ē is the pre-Great-Vowel-Shift long e.
  NOT modern English "we" [wiː].
  NOT [ɛ] as in "bed".
  The vowel of German "See", French "été".
  F1 lower than [æ] (higher tongue).
  F2 similar to [æ] (same front position).
  Duration: 2x the short equivalent.

  This is an unstressed function word
  in the line. In performance it moves
  quickly toward Gardena.
  dil=1.0 total duration: ~200ms
  dil=2.5 performance duration: ~500ms
"""

import numpy as np
from scipy.signal import lfilter, butter
import wave as wave_module
import os
import sys

SR    = 44100
DTYPE = np.float32

os.makedirs("output_play", exist_ok=True)


# ============================================================
# PARAMETERS
# ============================================================

# W onset — voiced labiovelar approximant
# Same tract position as HW but voiced,
# no noise component
W_F    = [300.0, 610.0, 2200.0, 3300.0]
W_B    = [ 80.0,  90.0,  210.0,  310.0]
W_GAINS = [0.5, 0.65, 0.30, 0.15]
W_DUR_MS = 55.0

# Ē vowel — long close-mid front [eː]
# Pre-Great-Vowel-Shift Old English long e
# F1 lower than [æ]: higher tongue position
# F2 similar to [æ]: same front location
# Duration 2x short equivalent
E_F    = [420.0, 2200.0, 2900.0, 3400.0]
E_B    = [ 90.0,  120.0,  160.0,  200.0]
E_GAINS = [18.0, 5.0, 1.5, 0.5]
E_DUR_MS = 160.0

# Coarticulation fractions
# W→E transition: front of vowel segment
# is the W→vowel glide
E_COART_ON  = 0.15   # 15% onset coarticulation
E_COART_OFF = 0.10   # 10% offset coarticulation

# Performance parameters
PITCH_HZ = 145.0     # default (use 110 for scop)
DIL      = 1.0       # dilation factor


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
    b, a = butter(2, [lo_, hi_],
                   btype='band')
    return b, a

def ola_stretch(sig, factor=4.0, sr=SR):
    win_ms = 40.0
    win_n  = int(win_ms / 1000.0 * sr)
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
        frame = sig[in_pos:in_pos+win_n] * window
        out [out_pos:out_pos+win_n] += frame
        norm[out_pos:out_pos+win_n] += window
    safe       = norm > 1e-8
    out[safe] /= norm[safe]
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.75
    return f32(out)


# ============================================================
# ROSENBERG PULSE SOURCE
# ============================================================

def rosenberg_pulse(n_samples, pitch_hz,
                    oq=0.65, sr=SR):
    """
    Voiced glottal source.
    Used for W onset and Ē vowel.
    """
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
# FORMANT FILTER
# ============================================================

def apply_formant(src, freqs, bws, gains,
                  sr=SR):
    """
    Apply parallel formant resonators to source.
    """
    T      = 1.0 / sr
    n      = len(src)
    result = np.zeros(n, dtype=DTYPE)
    for fi in range(len(freqs)):
        fc  = float(freqs[fi])
        bw  = float(bws[fi])
        g   = float(gains[fi])
        a2  = -np.exp(-2 * np.pi * bw * T)
        a1  =  2 * np.exp(-np.pi * bw * T) \
               * np.cos(2 * np.pi * fc * T)
        b0  = 1.0 - a1 - a2
        y1 = y2 = 0.0
        out = np.zeros(n, dtype=DTYPE)
        for i in range(n):
            y   = (b0 * float(src[i])
                   + a1 * y1 + a2 * y2)
            y2  = y1
            y1  = y
            out[i] = y
        result += out * g
    return f32(result)


# ============================================================
# W ONSET SYNTHESIS
# ============================================================

def synth_W_onset(F_next, dur_ms=None,
                   pitch_hz=PITCH_HZ,
                   dil=DIL, sr=SR):
    """
    Voiced labiovelar approximant [w].

    F_next: formant targets of following vowel.
    The W onset transitions FROM W_F TOWARD F_next.
    This is the locus transition — the identity
    of W is in the trajectory, not the target.

    Fully voiced throughout.
    No noise component (contrast with HW).
    Low-frequency dominant (labiovelar position).
    """
    if dur_ms is None:
        dur_ms = W_DUR_MS * dil
    else:
        dur_ms = dur_ms * dil

    n_s = max(4, int(dur_ms / 1000.0 * sr))
    T   = 1.0 / sr

    # Voiced source
    src = rosenberg_pulse(n_s, pitch_hz,
                          oq=0.65, sr=sr)

    # Attack envelope — smooth onset
    n_atk = int(0.010 * sr)
    if 0 < n_atk < n_s:
        src[:n_atk] *= np.linspace(
            0.0, 1.0, n_atk)

    # Formant interpolation W_F → F_next
    result = np.zeros(n_s, dtype=DTYPE)
    for fi in range(min(len(W_F),
                        len(F_next))):
        f_arr = np.linspace(
            float(W_F[fi]),
            float(F_next[fi]),
            n_s, dtype=DTYPE)
        bw  = float(W_B[fi])
        g   = float(W_GAINS[fi])
        y1 = y2 = 0.0
        out = np.zeros(n_s, dtype=DTYPE)
        for i in range(n_s):
            fc  = max(20.0,
                      min(sr * 0.48,
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


# ============================================================
# Ē VOWEL SYNTHESIS
# ============================================================

def synth_E_long(F_prev, dur_ms=None,
                  pitch_hz=PITCH_HZ,
                  dil=DIL, sr=SR):
    """
    Long close-mid front vowel [eː].

    Pre-Great-Vowel-Shift Old English long e.
    F1 ~420 Hz (higher tongue than [æ])
    F2 ~2200 Hz (front position, same as [æ])

    F_prev: formant targets of preceding W onset.
    Coarticulation: onset zone interpolates
    from F_prev toward E_F.

    Long vowel: duration 2x short equivalent.
    Normalizes output to peak=0.75.
    """
    if dur_ms is None:
        dur_ms = E_DUR_MS * dil
    else:
        dur_ms = dur_ms * dil

    n_s = max(4, int(dur_ms / 1000.0 * sr))
    T   = 1.0 / sr

    # Voiced source
    src = rosenberg_pulse(n_s, pitch_hz,
                          oq=0.65, sr=sr)

    # Envelope
    n_atk = min(int(0.020 * sr), n_s // 4)
    n_rel = min(int(0.040 * sr), n_s // 4)
    env   = np.ones(n_s, dtype=DTYPE)
    if n_atk < n_s:
        env[:n_atk] = np.linspace(
            0.5, 1.0, n_atk)
    if n_rel < n_s:
        env[-n_rel:] = np.linspace(
            1.0, 0.0, n_rel)
    src = f32(src * env)

    # Coarticulation zones
    n_on  = int(E_COART_ON  * n_s)
    n_off = int(E_COART_OFF * n_s)

    result = np.zeros(n_s, dtype=DTYPE)
    for fi in range(len(E_F)):
        # Build per-sample frequency array
        f_start = float(F_prev[fi]) \
                  if fi < len(F_prev) \
                  else float(E_F[fi])
        f_body  = float(E_F[fi])
        f_arr   = np.full(n_s, f_body,
                          dtype=DTYPE)
        if n_on > 0:
            f_arr[:n_on] = np.linspace(
                f_start, f_body, n_on)

        bw  = float(E_B[fi])
        g   = float(E_GAINS[fi])
        y1 = y2 = 0.0
        out = np.zeros(n_s, dtype=DTYPE)
        for i in range(n_s):
            fc  = max(20.0,
                      min(sr * 0.48,
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

    # Normalize to peak=0.75
    mx = np.max(np.abs(result))
    if mx > 1e-8:
        result = f32(result / mx * 0.75)

    return f32(result)


# ============================================================
# FULL WORD SYNTHESIS
# ============================================================

def synth_we(pitch_hz=PITCH_HZ,
              dil=DIL,
              add_room=False,
              sr=SR):
    """
    Synthesize Old English 'Wē' [weː].

    W onset transitions into Ē vowel.
    No coda — open syllable.
    Long vowel held.
    """
    w_seg = synth_W_onset(
        F_next=E_F,
        pitch_hz=pitch_hz,
        dil=dil, sr=sr)

    e_seg = synth_E_long(
        F_prev=W_F,
        pitch_hz=pitch_hz,
        dil=dil, sr=sr)

    # Ghost between W and Ē
    # Short — W is voiced, Ē is voiced,
    # the transition is smooth not gapped
    # Ghost is very brief here: 10–15ms
    n_ghost = int(0.012 * sr)
    ghost   = np.zeros(n_ghost, dtype=DTYPE)

    word = np.concatenate([w_seg, ghost, e_seg])

    # Overall normalization
    mx = np.max(np.abs(word))
    if mx > 1e-8:
        word = f32(word / mx * 0.75)

    if add_room:
        word = apply_simple_room(
            word, rt60=2.0,
            direct_ratio=0.38, sr=sr)

    return f32(word)


def apply_simple_room(sig, rt60=2.0,
                       direct_ratio=0.42,
                       sr=SR):
    """
    Simple mead hall room simulation.
    Comb filter + allpass approximation.
    """
    out  = sig.copy().astype(float)
    d1   = int(0.021 * sr)
    d2   = int(0.035 * sr)
    d3   = int(0.051 * sr)
    g    = 10 ** (-3.0 / (rt60 * sr))
    rev  = np.zeros(len(sig) + d3 + 1,
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
# MAIN
# ============================================================

if __name__ == "__main__":

    print()
    print("WĒ RECONSTRUCTION")
    print("Old English [weː] — Beowulf line 1, word 2")
    print()

    # Conversational rate (dil=1.0)
    we_dry = synth_we(
        pitch_hz=145.0,
        dil=1.0,
        add_room=False)
    write_wav("output_play/we_dry.wav",
              we_dry, SR)
    print(f"  we_dry.wav     "
          f"{len(we_dry)} samples  "
          f"({len(we_dry)/SR*1000:.0f} ms)")

    # Hall reverb
    we_hall = synth_we(
        pitch_hz=145.0,
        dil=1.0,
        add_room=True)
    write_wav("output_play/we_hall.wav",
              we_hall, SR)
    print(f"  we_hall.wav")

    # 4x slow
    we_slow = ola_stretch(we_dry, 4.0)
    write_wav("output_play/we_slow.wav",
              we_slow, SR)
    print(f"  we_slow.wav")

    # Performance parameters
    we_perf = synth_we(
        pitch_hz=110.0,
        dil=2.5,
        add_room=True)
    write_wav("output_play/we_performance.wav",
              we_perf, SR)
    print(f"  we_performance.wav  "
          f"({len(we_perf)/SR*1000:.0f} ms)")

    # HWÆT + Wē together (first two words)
    try:
        sys.path.insert(0, '..')
        from word_01_hwat.hwat_reconstruction \
            import synth_hwat
        hwat = synth_hwat(
            pitch_hz=110.0,
            dil=2.5,
            add_room=False)
        pause = np.zeros(
            int(0.15 * SR), dtype=DTYPE)
        both  = np.concatenate([hwat, pause,
                                 we_perf])
        mx    = np.max(np.abs(both))
        if mx > 1e-8:
            both = f32(both / mx * 0.80)
        write_wav(
            "output_play/hwat_we_together.wav",
            both, SR)
        print(f"  hwat_we_together.wav")
    except ImportError:
        print(f"  (hwat_reconstruction not found"
              f" — skipping combined file)")

    print()
    print("  afplay output_play/we_dry.wav")
    print("  afplay output_play/we_slow.wav")
    print("  afplay output_play/we_performance.wav")
    print("  afplay output_play/we_hall.wav")
    print()
