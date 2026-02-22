"""
ĒAGE RECONSTRUCTION
Old English: ēage
Meaning: eye
IPA: [eːɑɣe]
Purpose: Verify [eːɑ] — long front-back diphthong
Inventory completion series — word 2 of 4
February 2026

PHONEME STRUCTURE:
  EY  [eː]   long close-mid front       — verified WĒ
  EA  [eːɑ]  long front-back diphthong  — NEW
  GH  [ɣ]    voiced velar fricative     — verified MǢGÞUM
  E   [e]    short close-mid front      — verified GĀR-DENA

NEW PHONEMES:
  [eːɑ]: long front-back diphthong.
         Long counterpart of [eɑ].
         Onset [eː]: F1 ~450, F2 ~1900 Hz
         Offset [ɑ]: F1 ~700, F2 ~1100 Hz
         Duration ~150 ms — long diphthong.
         ~double short [eɑ] duration (80 ms).

         Distinct from [eɑ] by duration only —
         the trajectory is identical.
         Same F1 rise: 450 → 700 Hz
         Same F2 fall: 1900 → 1100 Hz
         Duration is the sole distinction.

         Distinct from [eo] long/short:
           [eɑ]: F1 rises (opens)
                 F2 falls moderately
                 target is open back [ɑ]
           [eːɑ]: same trajectory, longer
           [eo]:  F1 stable
                  F2 falls steeply
                  target is mid back [o]

WORD STRUCTURE:
  ē-a-ge — two syllables.
  [eːɑ] is the first syllable nucleus.
  [ɣe] is the second syllable.
  The [ɣ] is intervocalic —
  between diphthong offset [ɑ]
  and final [e].

ETYMOLOGY:
  ēage — eye.
  ModE 'eye' direct descendant.
  OE [eːɑɣe] → ME [eːe] → ModE [aɪ]
  The [ɣ] was lost in ME.
  The [eːɑ] diphthong monophthongised
  then underwent Great Vowel Shift.
  'eye' and 'wife' both end in [aɪ] —
  both started as long high/mid
  front vowels in OE.

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

# EYA — long front-back diphthong [eːɑ]
# NEW PHONEME
# Long counterpart of [eɑ].
# Same trajectory — double duration.
# Onset: F1 450, F2 1900 Hz
# Offset: F1 700, F2 1100 Hz
EYA_DUR_MS   = 150.0
EYA_F_ON     = [450.0, 1900.0, 2600.0, 3300.0]
EYA_F_OFF    = [700.0, 1100.0, 2400.0, 3000.0]
EYA_B        = [100.0,  130.0,  200.0,  280.0]
EYA_GAINS    = [ 16.0,    8.0,    1.5,    0.5]
EYA_TRANS_ON  = 0.30
EYA_TRANS_OFF = 0.90

# GH — voiced velar fricative [ɣ]
GH_F        = [300.0,  900.0, 2200.0, 3000.0]
GH_B        = [350.0,  400.0,  500.0,  550.0]
GH_GAINS    = [  5.0,    2.5,    0.8,    0.3]
GH_AM_RATE  = 80.0
GH_AM_DEPTH = 0.25
GH_DUR_MS   = 65.0

# E — short close-mid front [e]
E_F      = [450.0, 1900.0, 2600.0, 3300.0]
E_B      = [100.0,  130.0,  200.0,  280.0]
E_GAINS  = [ 16.0,    8.0,    1.5,    0.5]
E_DUR_MS = 55.0
E_COART_ON  = 0.12
E_COART_OFF = 0.12

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

def synth_EYA(F_prev=None, F_next=None,
               pitch_hz=PITCH_HZ,
               dil=DIL, sr=SR):
    """
    Long front-back diphthong [eːɑ].
    NEW PHONEME.
    Long counterpart of short [eɑ].
    Identical trajectory — double duration.
    Onset: F1 450, F2 1900 Hz
    Offset: F1 700, F2 1100 Hz
    F1 rises — jaw opens.
    F2 falls — tongue retracts.
    Duration 150 ms — long diphthong.
    """
    dur_ms = EYA_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    T      = 1.0 / sr
    src    = rosenberg_pulse(n_s, pitch_hz,
                              oq=0.65, sr=sr)
    n_atk  = min(int(0.010 * sr), n_s // 4)
    n_rel  = min(int(0.020 * sr), n_s // 4)
    env    = np.ones(n_s, dtype=DTYPE)
    if n_atk < n_s:
        env[:n_atk] = np.linspace(
            0.4, 1.0, n_atk)
    if n_rel < n_s:
        env[-n_rel:] = np.linspace(
            1.0, 0.6, n_rel)
    src    = f32(src * env)
    i_ton  = int(EYA_TRANS_ON  * n_s)
    i_toff = int(EYA_TRANS_OFF * n_s)
    n_trans= max(1, i_toff - i_ton)
    result = np.zeros(n_s, dtype=DTYPE)
    for fi in range(len(EYA_F_ON)):
        f_on  = float(EYA_F_ON[fi])
        f_off = float(EYA_F_OFF[fi])
        bw    = float(EYA_B[fi])
        g     = float(EYA_GAINS[fi])
        f_arr = np.full(n_s, f_on,
                         dtype=DTYPE)
        if i_ton > 0:
            f_arr[:i_ton] = f_on
        if i_toff <= n_s:
            f_arr[i_ton:i_toff] = \
                np.linspace(f_on, f_off,
                             n_trans)
        if i_toff < n_s:
            f_arr[i_toff:] = f_off
        y1 = y2 = 0.0
        out = np.zeros(n_s, dtype=DTYPE)
        for i in range(n_s):
            fc  = max(20.0, min(
                sr * 0.48,
                float(f_arr[i])))
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
        result = f32(result / mx * 0.68)
    return f32(result)


def synth_GH(F_prev=None, F_next=None,
              pitch_hz=PITCH_HZ,
              dil=DIL, sr=SR):
    dur_ms = GH_DUR_MS * dil
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
    t_arr  = np.arange(n_s) * T
    am     = (1.0 - GH_AM_DEPTH
              + GH_AM_DEPTH
              * np.sin(2 * np.pi
                       * GH_AM_RATE
                       * t_arr))
    src    = f32(src * am.astype(DTYPE))
    result = apply_formants(
        src, GH_F, GH_B, GH_GAINS, sr=sr)
    mx     = np.max(np.abs(result))
    if mx > 1e-8:
        result = f32(result / mx * 0.55)
    return f32(result)


def synth_E(F_prev=None, F_next=None,
             pitch_hz=PITCH_HZ,
             dil=DIL, sr=SR):
    dur_ms = E_DUR_MS * dil
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

def synth_eage(pitch_hz=PITCH_HZ,
                dil=DIL,
                add_room=False,
                sr=SR):
    """[eːɑ·ɣ·e]"""
    eya_seg = synth_EYA(
        F_prev=EYA_F_ON, F_next=GH_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    gh_seg  = synth_GH(
        F_prev=EYA_F_OFF, F_next=E_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    e_seg   = synth_E(
        F_prev=GH_F, F_next=None,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    word    = np.concatenate([
        eya_seg, gh_seg, e_seg])
    mx      = np.max(np.abs(word))
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
    print("ĒAGE RECONSTRUCTION v1")
    print("Old English [eːɑɣe]")
    print("Inventory completion — word 2 of 4")
    print("New phoneme: [eːɑ]")
    print()

    w_dry = synth_eage(
        pitch_hz=145.0, dil=1.0,
        add_room=False)
    write_wav(
        "output_play/eage_dry.wav",
        w_dry, SR)
    print(f"  eage_dry.wav"
          f"  ({len(w_dry)/SR*1000:.0f} ms)")

    w_hall = synth_eage(
        pitch_hz=145.0, dil=1.0,
        add_room=True)
    write_wav(
        "output_play/eage_hall.wav",
        w_hall, SR)
    print("  eage_hall.wav")

    w_slow = ola_stretch(w_dry, 4.0)
    write_wav(
        "output_play/eage_slow.wav",
        w_slow, SR)
    print("  eage_slow.wav")

    eya_seg = synth_EYA(EYA_F_ON, GH_F,
                         145.0, 1.0, SR)
    write_wav(
        "output_play/eage_eya_only.wav",
        ola_stretch(eya_seg / (
            np.max(np.abs(eya_seg))+1e-8)
            * 0.75, 4.0), SR)
    print("  eage_eya_only.wav  (4x slow)")
    print()
    print("  afplay output_play/"
          "eage_eya_only.wav")
    print("  afplay output_play/"
          "eage_dry.wav")
    print("  afplay output_play/"
          "eage_slow.wav")
    print()
    print("  Inventory completion progress:")
    print("  [iː]  ✓ DONE — WĪF")
    print("  [eːɑ] — pending verification")
    print("  [eːo] — pending — ÞĒOD")
    print("  [p]   — pending — PÆÞ")
    print("  [b]   — pending — line 8")
    print()
