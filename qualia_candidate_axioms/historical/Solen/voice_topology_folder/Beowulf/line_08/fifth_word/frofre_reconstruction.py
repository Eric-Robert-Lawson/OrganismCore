"""
FRŌFRE RECONSTRUCTION
Old English: frōfre
Meaning: comfort, consolation (genitive singular)
IPA: [froːvrə]
Beowulf: Line 8, word 5 (overall word 35)
February 2026

PHONEME STRUCTURE:
  F    [f]   voiceless labiodental fricative — verified
  R1   [r]   alveolar trill                  — verified
  OY   [oː]  long close-mid back rounded     — verified
  V    [v]   voiced labiodental fricative    — verified
  R2   [r]   alveolar trill (second)         — verified
  SCHWA [ə]  mid central vowel               — verified (phoneme 40)

NEW PHONEMES: none
Pure assembly. All six phonemes from verified inventory.

SYLLABLE STRUCTURE:
  Syllable 1: [froːv]  — stressed — heavy
    F + R + long OY + V
  Syllable 2: [rə]     — unstressed — light
    R + SCHWA

COARTICULATION NOTES:
  [f] → [r]:
    Voiceless labiodental into alveolar trill.
    F_next for [f] = R formants.
    Lip release from fricative into trill.

  [r] → [oː]:
    Alveolar trill into long back rounded vowel.
    F_prev for [oː] = R formants.
    Tongue tip drops from alveolar to back
    rounded position. F2 falls sharply.

  [oː] → [v]:
    Long back rounded vowel into voiced
    labiodental fricative.
    Voicing maintained through transition.
    F_next for [oː] = V noise band.
    Lip constriction forms during final
    portion of [oː].

  [v] → [r]:
    Voiced labiodental into alveolar trill.
    Both voiced — voicing continuous.
    Lip releases, tongue tip rises to
    alveolar position.

  [r] → [ə]:
    Alveolar trill into unstressed schwa.
    F_prev for [ə] = R formants.
    Tongue tip drops, jaw settles to
    central rest position.
    The minimum-effort syllable closes
    the word.

NOTABLE FEATURES:
  1. VOICED SEQUENCE [oː]→[v]→[r]→[ə]:
     Three consecutive voiced segments
     after the stressed nucleus. Voicing
     unbroken from [r1] through to [ə].
     The word is predominantly voiced
     after the initial [f].

  2. [ə] SECOND APPEARANCE:
     First in FUNDEN (unstressed -en).
     Now in FRŌFRE (unstressed -re).
     Different orthographic suffix,
     same phonological realisation.
     The rule holds: all OE unstressed
     syllables → [ə] in performance.
     This is the second confirmation.

  3. LONG VOWEL [oː] IN STRESSED SYLLABLE:
     The macron on Ō marks length.
     Duration 110 ms * dil.
     The long back rounded vowel is the
     acoustic centre of gravity of the word.
     F2 ~800 Hz — the back rounded position.

  4. INTERVOCALIC [v]:
     [v] sits between [oː] and [r].
     Both flanking segments are voiced.
     The voiced labiodental fricative
     is confirmed in voiced context.
     Voicing fraction target >= 0.35.

CONTEXT:
  hē þæs frōfre gebād
  he of-that comfort waited
  frōfre is the genitive noun —
  the comfort that was waited for.
  The word that names the relief.
  After feasceaft (destitute) and funden
  (found), frōfre is the turn —
  what the finding brought.

PERFORMANCE PARAMETERS:
  pitch_hz     = 110.0
  dil          = 2.5
  rt60         = 2.0
  direct_ratio = 0.38

CHANGE LOG:
  v1 — initial parameters
       pure assembly — no new phonemes
       [ə] second appearance confirmed
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

# F — voiceless labiodental fricative [f]
F_DUR_MS   = 70.0
F_NOISE_CF = 7000.0
F_NOISE_BW = 5000.0
F_GAIN     = 0.28

# R — alveolar trill [r]
R_F           = [400.0, 1200.0, 1800.0, 2800.0]
R_B           = [150.0,  200.0,  250.0,  300.0]
R_GAINS       = [ 12.0,    6.0,    1.2,    0.4]
R_DUR_MS      = 70.0
R_TRILL_RATE  = 25.0
R_TRILL_DEPTH = 0.40
R_COART_ON    = 0.15
R_COART_OFF   = 0.15

# OY — long close-mid back rounded [oː]
OY_F     = [450.0,  800.0, 2500.0, 3200.0]
OY_B     = [100.0,  120.0,  200.0,  280.0]
OY_GAINS = [ 16.0,    8.0,    1.5,    0.5]
OY_DUR_MS    = 110.0
OY_COART_ON  = 0.10
OY_COART_OFF = 0.10

# V — voiced labiodental fricative [v]
V_DUR_MS       = 65.0
V_AM_RATE      = 80.0
V_AM_DEPTH     = 0.25
V_NOISE_CF     = 6000.0
V_NOISE_BW     = 4000.0
V_VOICING_FRAC = 0.75

# SCHWA — mid central vowel [ə]
SCHWA_F     = [500.0, 1500.0, 2500.0, 3200.0]
SCHWA_B     = [150.0,  200.0,  280.0,  320.0]
SCHWA_GAINS = [ 14.0,    7.0,    1.5,    0.4]
SCHWA_DUR_MS    = 45.0
SCHWA_COART_ON  = 0.15
SCHWA_COART_OFF = 0.15

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

def synth_F(dil=DIL, sr=SR):
    """Voiceless labiodental fricative [f]."""
    dur_ms = F_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    noise  = np.random.randn(n_s).astype(float)
    lo_    = max(F_NOISE_CF - F_NOISE_BW / 2, 200.0)
    hi_    = min(F_NOISE_CF + F_NOISE_BW / 2, sr * 0.48)
    b_bp, a_bp = safe_bp(lo_, hi_, sr)
    fric   = lfilter(b_bp, a_bp, noise)
    n_atk  = min(int(0.010 * sr), n_s // 4)
    n_dec  = min(int(0.015 * sr), n_s // 4)
    env    = np.ones(n_s, dtype=float)
    if n_atk < n_s:
        env[:n_atk]  = np.linspace(0.0, 1.0, n_atk)
    if n_dec < n_s:
        env[-n_dec:] = np.linspace(1.0, 0.3, n_dec)
    fric   = f32(fric * env * F_GAIN)
    mx     = np.max(np.abs(fric))
    if mx > 1e-8:
        fric = f32(fric / mx * 0.45)
    return f32(fric)


def synth_R(F_prev=None, F_next=None,
             pitch_hz=PITCH_HZ,
             dil=DIL, sr=SR):
    """
    Alveolar trill [r].
    Amplitude modulated at trill rate.
    Trill depth 0.40 (verified).
    """
    dur_ms = R_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    T      = 1.0 / sr
    src    = rosenberg_pulse(n_s, pitch_hz,
                              oq=0.65, sr=sr)
    # trill modulation
    t_arr  = np.arange(n_s) * T
    trill  = (1.0 - R_TRILL_DEPTH
              + R_TRILL_DEPTH
              * np.sin(2 * np.pi
                       * R_TRILL_RATE
                       * t_arr))
    src    = f32(src * trill.astype(DTYPE))
    n_atk  = min(int(0.010 * sr), n_s // 4)
    n_rel  = min(int(0.015 * sr), n_s // 4)
    env    = np.ones(n_s, dtype=DTYPE)
    if n_atk < n_s:
        env[:n_atk]  = np.linspace(0.3, 1.0, n_atk)
    if n_rel < n_s:
        env[-n_rel:] = np.linspace(1.0, 0.3, n_rel)
    src    = f32(src * env)
    n_on   = int(R_COART_ON  * n_s)
    n_off  = int(R_COART_OFF * n_s)
    fp     = F_prev if F_prev is not None else R_F
    fn     = F_next if F_next is not None else R_F
    result = np.zeros(n_s, dtype=DTYPE)
    for fi in range(len(R_F)):
        f_s   = float(fp[fi]) if fi < len(fp) \
                else float(R_F[fi])
        f_e   = float(fn[fi]) if fi < len(fn) \
                else float(R_F[fi])
        f_b   = float(R_F[fi])
        f_arr = np.full(n_s, f_b, dtype=DTYPE)
        if n_on > 0:
            f_arr[:n_on]  = np.linspace(
                f_s, f_b, n_on)
        if n_off > 0:
            f_arr[-n_off:] = np.linspace(
                f_b, f_e, n_off)
        bw  = float(R_B[fi])
        g   = float(R_GAINS[fi])
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
        result = f32(result / mx * 0.60)
    return f32(result)


def synth_OY(F_prev=None, F_next=None,
              pitch_hz=PITCH_HZ,
              dil=DIL, sr=SR):
    """
    Long close-mid back rounded [oː].
    Duration 110 ms * dil.
    F1 450, F2 800 — back rounded position.
    Low F2 — the most back vowel in stressed
    position in the reconstruction.
    """
    dur_ms = OY_DUR_MS * dil
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
    n_on   = int(OY_COART_ON  * n_s)
    n_off  = int(OY_COART_OFF * n_s)
    fp     = F_prev if F_prev is not None else OY_F
    fn     = F_next if F_next is not None else OY_F
    result = np.zeros(n_s, dtype=DTYPE)
    for fi in range(len(OY_F)):
        f_s   = float(fp[fi]) if fi < len(fp) \
                else float(OY_F[fi])
        f_e   = float(fn[fi]) if fi < len(fn) \
                else float(OY_F[fi])
        f_b   = float(OY_F[fi])
        f_arr = np.full(n_s, f_b, dtype=DTYPE)
        if n_on > 0:
            f_arr[:n_on]  = np.linspace(
                f_s, f_b, n_on)
        if n_off > 0:
            f_arr[-n_off:] = np.linspace(
                f_b, f_e, n_off)
        bw  = float(OY_B[fi])
        g   = float(OY_GAINS[fi])
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


def synth_V(F_prev=None, F_next=None,
             pitch_hz=PITCH_HZ,
             dil=DIL, sr=SR):
    """
    Voiced labiodental fricative [v].
    Rosenberg pulse source — voiced.
    AM modulation at 80 Hz, depth 0.25.
    Voicing fraction >= 0.35 target.
    Intervocalic context: [oː]→[v]→[r].
    Voicing continuous through transition.
    """
    dur_ms = V_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    T      = 1.0 / sr
    src    = rosenberg_pulse(n_s, pitch_hz,
                              oq=0.65, sr=sr)
    t_arr  = np.arange(n_s) * T
    am     = (1.0 - V_AM_DEPTH
              + V_AM_DEPTH
              * np.sin(2 * np.pi
                       * V_AM_RATE * t_arr))
    src    = f32(src * am.astype(DTYPE))
    n_atk  = min(int(0.008 * sr), n_s // 4)
    n_rel  = min(int(0.012 * sr), n_s // 4)
    env    = np.ones(n_s, dtype=DTYPE)
    if n_atk < n_s:
        env[:n_atk]  = np.linspace(0.3, 1.0, n_atk)
    if n_rel < n_s:
        env[-n_rel:] = np.linspace(1.0, 0.3, n_rel)
    src    = f32(src * env)
    # labiodental band shaping
    lo_    = max(V_NOISE_CF - V_NOISE_BW / 2, 200.0)
    hi_    = min(V_NOISE_CF + V_NOISE_BW / 2, sr * 0.48)
    b_bp, a_bp = safe_bp(lo_, hi_, sr)
    shaped = f32(lfilter(b_bp, a_bp,
                          src.astype(float)))
    result = f32(src * V_VOICING_FRAC
                 + shaped * (1.0 - V_VOICING_FRAC))
    mx     = np.max(np.abs(result))
    if mx > 1e-8:
        result = f32(result / mx * 0.55)
    return f32(result)


def synth_SCHWA(F_prev=None, F_next=None,
                 pitch_hz=PITCH_HZ,
                 dil=DIL, sr=SR):
    """
    Mid central vowel [ə] — phoneme 40.
    Second appearance in reconstruction.
    First: FUNDEN unstressed -en.
    Now: FRŌFRE unstressed -re.
    Same parameters — rule confirmed.
    C([ə],H) ≈ 0.75. One step from home.
    """
    dur_ms = SCHWA_DUR_MS * dil
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
    n_on   = int(SCHWA_COART_ON  * n_s)
    n_off  = int(SCHWA_COART_OFF * n_s)
    fp     = F_prev if F_prev is not None else SCHWA_F
    fn     = F_next if F_next is not None else SCHWA_F
    result = np.zeros(n_s, dtype=DTYPE)
    for fi in range(len(SCHWA_F)):
        f_s   = float(fp[fi]) if fi < len(fp) \
                else float(SCHWA_F[fi])
        f_e   = float(fn[fi]) if fi < len(fn) \
                else float(SCHWA_F[fi])
        f_b   = float(SCHWA_F[fi])
        f_arr = np.full(n_s, f_b, dtype=DTYPE)
        if n_on > 0:
            f_arr[:n_on]  = np.linspace(
                f_s, f_b, n_on)
        if n_off > 0:
            f_arr[-n_off:] = np.linspace(
                f_b, f_e, n_off)
        bw  = float(SCHWA_B[fi])
        g   = float(SCHWA_GAINS[fi])
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

def synth_frōfre(pitch_hz=PITCH_HZ,
                  dil=DIL,
                  add_room=False,
                  sr=SR):
    """
    [f · r · oː · v · r · ə]
    Syllable 1: [froːv]  — stressed — heavy
    Syllable 2: [rə]     — unstressed — light
    """
    f_seg    = synth_F(dil=dil, sr=sr)
    r1_seg   = synth_R(
        F_prev=None,
        F_next=OY_F,
        pitch_hz=pitch_hz,
        dil=dil, sr=sr)
    oy_seg   = synth_OY(
        F_prev=R_F,
        F_next=None,
        pitch_hz=pitch_hz,
        dil=dil, sr=sr)
    v_seg    = synth_V(
        F_prev=OY_F,
        F_next=R_F,
        pitch_hz=pitch_hz,
        dil=dil, sr=sr)
    r2_seg   = synth_R(
        F_prev=None,
        F_next=SCHWA_F,
        pitch_hz=pitch_hz,
        dil=dil, sr=sr)
    schwa_seg = synth_SCHWA(
        F_prev=R_F,
        F_next=None,   # word boundary → H
        pitch_hz=pitch_hz,
        dil=dil, sr=sr)
    word     = np.concatenate([
        f_seg, r1_seg, oy_seg,
        v_seg, r2_seg, schwa_seg])
    mx       = np.max(np.abs(word))
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
    print("FRŌFRE RECONSTRUCTION v1")
    print("Old English [froːvrə]")
    print("Beowulf line 8, word 5")
    print("Pure assembly — no new phonemes")
    print("[ə] second appearance")
    print()

    w_dry = synth_frōfre(
        pitch_hz=PITCH_HZ, dil=DIL,
        add_room=False)
    write_wav("output_play/frōfre_dry.wav",
               w_dry, SR)
    print(f"  frōfre_dry.wav"
          f"  ({len(w_dry)/SR*1000:.0f} ms)")

    w_hall = synth_frōfre(
        pitch_hz=PITCH_HZ, dil=DIL,
        add_room=True)
    write_wav("output_play/frōfre_hall.wav",
               w_hall, SR)
    print("  frōfre_hall.wav")

    w_slow = ola_stretch(w_dry, 4.0)
    write_wav("output_play/frōfre_slow.wav",
               w_slow, SR)
    print("  frōfre_slow.wav")

    w_perf = synth_frōfre(
        pitch_hz=PITCH_PERF,
        dil=DIL_PERF,
        add_room=True)
    write_wav("output_play/frōfre_perf.wav",
               w_perf, SR)
    print(f"  frōfre_perf.wav"
          f"  ({len(w_perf)/SR*1000:.0f} ms)"
          f"  [110 Hz, dil 2.5, hall]")
    print()
    print("  afplay output_play/frōfre_dry.wav")
    print("  afplay output_play/frōfre_slow.wav")
    print("  afplay output_play/frōfre_hall.wav")
    print("  afplay output_play/frōfre_perf.wav")
    print()
    print("  þæs frōfre —")
    print("  of that comfort —")
    print()
