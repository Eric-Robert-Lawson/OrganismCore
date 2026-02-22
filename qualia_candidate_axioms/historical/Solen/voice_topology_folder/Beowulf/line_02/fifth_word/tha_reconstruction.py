"""
ÐĀ RECONSTRUCTION
Old English: ðā
Meaning: then, at that time / those (dem. pronoun)
IPA: [ðɑː]
Beowulf: Line 3, Word 2 (overall word 10)
February 2026

PHONEME STRUCTURE:
  Ð   [ð]   voiced dental fricative
  Ā   [ɑː]  long open back vowel

NEW PHONEMES:
  [ð]: voiced dental fricative.
       Same place as [θ] — tongue tip
       at upper teeth — but voiced.
       Voicing bar present throughout.
       Lower centroid than [θ] because
       voicing adds strong low-frequency
       energy that pulls the centroid down.
       The 'th' in Modern English:
       'the', 'this', 'that', 'there'.
       OE [ð] survived unchanged into
       Modern English in these function
       words. One of the few sounds
       that did not shift.
       Duration: ~70 ms word-initial.

REUSED PHONEMES:
  [ɑː]: verified GĀR-DENA D2.
        F1=840 Hz, F2=1150 Hz.
        Duration 150 ms — phonemically long.

CONTRAST NOTE:
  [θ] vs [ð]:
  Both dental fricatives.
  [θ]: voiceless — no voicing bar,
       centroid ~4200 Hz
  [ð]: voiced — voicing bar present,
       centroid pulled lower by voicing
       energy, ~2500–3500 Hz
  The only distinction is voicing.
  Same place, same manner, opposite voicing.

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

# DH — voiced dental fricative [ð]
# Same constriction as [θ].
# Voicing bar throughout — periodic
# low-frequency energy from vocal fold
# vibration underneath the frication noise.
DH_DUR_MS   = 70.0
DH_NOISE_CF = 3800.0   # same as [θ]
DH_NOISE_BW = 2500.0   # slightly narrower —
                        # voicing competes
DH_NOISE_GAIN = 0.22   # lower noise gain —
                        # voicing dominates
# Voicing component: low-pass filtered
# Rosenberg pulse mixed with frication
DH_VOICE_GAIN = 0.45
DH_VOICE_LP   = 800.0  # low-pass for voicing bar

# AA_LONG — long open back [ɑː]
# Same as GĀR-DENA
AA_F      = [840.0, 1150.0, 2500.0, 3300.0]
AA_B      = [180.0,  120.0,  200.0,  280.0]
AA_GAINS  = [ 16.0,    5.0,    1.2,    0.4]
AA_DUR_MS = 150.0
AA_COART_ON  = 0.08
AA_COART_OFF = 0.15   # longer — word-final

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

def synth_DH(F_next=None,
              pitch_hz=PITCH_HZ,
              dil=DIL, sr=SR):
    """
    Voiced dental fricative [ð].
    'th' in 'the', 'this', 'that'.
    Frication noise at dental constriction
    mixed with voiced source (Rosenberg pulse
    low-pass filtered to produce voicing bar).
    The voicing bar is the primary acoustic
    cue distinguishing [ð] from [θ].
    """
    dur_ms = DH_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    noise  = np.random.randn(n_s).astype(float)

    # Frication component — dental noise
    b, a   = safe_bp(
        DH_NOISE_CF - DH_NOISE_BW / 2,
        min(DH_NOISE_CF + DH_NOISE_BW / 2,
            sr * 0.48), sr)
    fric   = lfilter(b, a, noise)
    b2, a2 = safe_bp(800.0, 3000.0, sr)
    fric  += lfilter(b2, a2, noise) * 0.3
    fric   = fric * DH_NOISE_GAIN

    # Voicing bar component — LP filtered pulse
    src_v  = rosenberg_pulse(n_s, pitch_hz,
                              oq=0.65, sr=sr)
    b_lp, a_lp = safe_lp(DH_VOICE_LP, sr)
    voice  = lfilter(b_lp, a_lp,
                     src_v.astype(float))
    voice  = voice * DH_VOICE_GAIN

    # Mix frication + voicing
    sig    = f32(fric + voice)

    # Amplitude envelope
    n_atk  = min(int(0.015 * sr), n_s // 4)
    n_dec  = min(int(0.015 * sr), n_s // 4)
    env    = np.ones(n_s, dtype=float)
    if n_atk < n_s:
        env[:n_atk] = np.linspace(
            0.0, 1.0, n_atk)
    if n_dec < n_s:
        env[-n_dec:] = np.linspace(
            1.0, 0.4, n_dec)
    sig    = f32(sig * env)
    mx     = np.max(np.abs(sig))
    if mx > 1e-8:
        sig = f32(sig / mx * 0.55)
    return f32(sig)


def synth_AA_long(F_prev=None, F_next=None,
                   pitch_hz=PITCH_HZ,
                   dil=DIL, sr=SR):
    """
    Long open back [ɑː].
    Same parameters as GĀR-DENA.
    Word-final — longer decay.
    """
    dur_ms = AA_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    T      = 1.0 / sr
    src    = rosenberg_pulse(n_s, pitch_hz,
                              oq=0.65, sr=sr)
    n_atk  = min(int(0.015 * sr), n_s // 4)
    n_rel  = min(int(0.060 * sr), n_s // 3)
    env    = np.ones(n_s, dtype=DTYPE)
    if n_atk < n_s:
        env[:n_atk] = np.linspace(
            0.3, 1.0, n_atk)
    if n_rel < n_s:
        env[-n_rel:] = np.linspace(
            1.0, 0.0, n_rel)
    src    = f32(src * env)
    n_on   = int(AA_COART_ON  * n_s)
    n_off  = int(AA_COART_OFF * n_s)
    f_prev = F_prev if F_prev is not None \
             else AA_F
    f_next = F_next if F_next is not None \
             else AA_F
    result = np.zeros(n_s, dtype=DTYPE)
    for fi in range(len(AA_F)):
        f_s   = (float(f_prev[fi])
                 if fi < len(f_prev)
                 else float(AA_F[fi]))
        f_e   = (float(f_next[fi])
                 if fi < len(f_next)
                 else float(AA_F[fi]))
        f_b   = float(AA_F[fi])
        f_arr = np.full(n_s, f_b, dtype=DTYPE)
        if n_on > 0:
            f_arr[:n_on] = np.linspace(
                f_s, f_b, n_on)
        if n_off > 0:
            f_arr[-n_off:] = np.linspace(
                f_b, f_e, n_off)
        bw  = float(AA_B[fi])
        g   = float(AA_GAINS[fi])
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
        result = f32(result / mx * 0.72)
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

def synth_tha(pitch_hz=PITCH_HZ,
               dil=DIL,
               add_room=False,
               sr=SR):
    """[ð·ɑː]"""
    dh_seg = synth_DH(
        F_next=AA_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    aa_seg = synth_AA_long(
        F_prev=AA_F, F_next=None,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    word   = np.concatenate([dh_seg, aa_seg])
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
    print("ÐĀ RECONSTRUCTION v1")
    print("Old English [ðɑː]")
    print("Beowulf line 3, word 2")
    print()

    tha_dry = synth_tha(
        pitch_hz=145.0, dil=1.0,
        add_room=False)
    write_wav(
        "output_play/tha_dry.wav",
        tha_dry, SR)
    print(f"  tha_dry.wav"
          f"  ({len(tha_dry)/SR*1000:.0f} ms)")

    tha_hall = synth_tha(
        pitch_hz=145.0, dil=1.0,
        add_room=True)
    write_wav(
        "output_play/tha_hall.wav",
        tha_hall, SR)
    print("  tha_hall.wav")

    tha_slow = ola_stretch(tha_dry, 4.0)
    write_wav(
        "output_play/tha_slow.wav",
        tha_slow, SR)
    print("  tha_slow.wav")

    tha_perf = synth_tha(
        pitch_hz=110.0, dil=2.5,
        add_room=True)
    write_wav(
        "output_play/tha_performance.wav",
        tha_perf, SR)
    print(f"  tha_performance.wav"
          f"  ({len(tha_perf)/SR*1000:.0f} ms)")

    dh_seg = synth_DH(AA_F, 145.0, 1.0, SR)
    write_wav(
        "output_play/tha_dh_isolated.wav",
        ola_stretch(dh_seg / (
            np.max(np.abs(dh_seg))+1e-8)
            * 0.75, 4.0), SR)
    print("  tha_dh_isolated.wav  (4x slow)")

    print()
    print("  afplay output_play/"
          "tha_dh_isolated.wav")
    print("  afplay output_play/tha_dry.wav")
    print("  afplay output_play/tha_slow.wav")
    print("  afplay output_play/"
          "tha_performance.wav")
    print("  afplay output_play/tha_hall.wav")
    print()
