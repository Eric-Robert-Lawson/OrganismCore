"""
EORLAS RECONSTRUCTION
Old English: eorlas
Meaning: warriors, noblemen, earls (nominative plural)
IPA: [eorlas]
Beowulf: Line 7, Word 2 (overall word 27)
February 2026

PHONEME STRUCTURE:
  EO  [eo]   short front-mid diphthong  — verified MEODOSETLA
  R   [r]    alveolar trill             — verified GĀR-DENA
  L   [l]    voiced alveolar lateral    — verified ÆÞELINGAS
  A   [ɑ]    short open back            — verified GĀR-DENA
  S   [s]    voiceless alveolar fric.   — verified ÆÞELINGAS

NEW PHONEMES: none.
Pure assembly.

NOTE ON WORD-INITIAL [eo]:
  Second instance of [eo].
  First was post-nasal [m]→[eo]
  in MEODOSETLA.
  Here [eo] is word-initial —
  onset from silence.
  F_prev set to EO_F_ON itself —
  no coarticulation pull from
  preceding context.
  F2 onset should be closer to
  target 1900 Hz than MEODOSETLA
  instance (which measured 1833 Hz
  due to [m] coarticulation).

NOTE ON [rl] CLUSTER:
  Alveolar trill into lateral.
  Both voiced. Both alveolar.
  Same place of articulation.
  The [r] tap/trill releases
  directly into the lateral
  approximant position.
  Smooth voiced transition —
  no voicing gap.

ETYMOLOGY:
  eorl — warrior, nobleman of rank.
  ModE 'earl' — same word.
  One of few OE rank terms surviving.
  Originally not hereditary title
  but descriptor of a warrior-noble.
  Scyld egsode eorlas —
  Scyld terrified men of rank.
  Not common soldiers. Earls.

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

# EO — short front-mid diphthong [eo]
EO_DUR_MS  = 75.0
EO_F_ON    = [450.0, 1900.0, 2600.0, 3300.0]
EO_F_OFF   = [450.0,  800.0, 2400.0, 3000.0]
EO_B       = [100.0,  130.0,  200.0,  280.0]
EO_GAINS   = [ 16.0,    8.0,    1.5,    0.5]
EO_TRANS_ON  = 0.25
EO_TRANS_OFF = 0.85

# R — alveolar trill [r]
R_F      = [300.0,  900.0, 2000.0, 3200.0]
R_B      = [100.0,  150.0,  250.0,  300.0]
R_GAINS  = [ 14.0,    7.0,    2.0,    0.5]
R_DUR_MS = 65.0
R_TRILL_RATE = 28.0
R_TRILL_DEPTH= 0.55

# L — voiced alveolar lateral [l]
L_F      = [350.0, 1100.0, 2700.0, 3300.0]
L_B      = [100.0,  150.0,  250.0,  300.0]
L_GAINS  = [ 14.0,    6.0,    1.5,    0.4]
L_DUR_MS = 60.0
L_COART_ON  = 0.15
L_COART_OFF = 0.15

# A — short open back [ɑ]
A_F      = [700.0, 1100.0, 2500.0, 3200.0]
A_B      = [120.0,  150.0,  200.0,  280.0]
A_GAINS  = [ 16.0,    8.0,    1.5,    0.5]
A_DUR_MS = 55.0
A_COART_ON  = 0.12
A_COART_OFF = 0.12

# S — voiceless alveolar fricative [s]
S_DUR_MS   = 65.0
S_NOISE_CF = 7500.0
S_NOISE_BW = 4000.0
S_GAIN     = 0.55

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
        norm[out_pos:out_pos+win_n] += frame * 0 + window
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

def synth_EO(F_prev=None, F_next=None,
              pitch_hz=PITCH_HZ,
              dil=DIL, sr=SR):
    """
    Short front-mid diphthong [eo].
    Word-initial here — onset from silence.
    F_prev = EO_F_ON — no coarticulation
    pull from preceding context.
    F2 onset should be closer to 1900 Hz
    than MEODOSETLA instance (1833 Hz)
    which had [m] coarticulation pulling
    F2 onset slightly lower.
    """
    dur_ms = EO_DUR_MS * dil
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
    i_ton  = int(EO_TRANS_ON  * n_s)
    i_toff = int(EO_TRANS_OFF * n_s)
    n_trans= max(1, i_toff - i_ton)
    result = np.zeros(n_s, dtype=DTYPE)
    for fi in range(len(EO_F_ON)):
        f_on  = float(EO_F_ON[fi])
        f_off = float(EO_F_OFF[fi])
        bw    = float(EO_B[fi])
        g     = float(EO_GAINS[fi])
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


def synth_R(F_prev=None, F_next=None,
             pitch_hz=PITCH_HZ,
             dil=DIL, sr=SR):
    """
    Alveolar trill [r].
    AM modulation at trill rate simulates
    tongue tip contact interruptions.
    Fully voiced — periodic source.
    Post-diphthong position.
    """
    dur_ms = R_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    T      = 1.0 / sr
    src    = rosenberg_pulse(n_s, pitch_hz,
                              oq=0.65, sr=sr)
    t_arr  = np.arange(n_s) * T
    am     = (1.0 - R_TRILL_DEPTH
              + R_TRILL_DEPTH
              * np.abs(np.sin(
                  np.pi * R_TRILL_RATE
                  * t_arr)))
    src    = f32(src * am.astype(DTYPE))
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
    result = apply_formants(
        src, R_F, R_B, R_GAINS, sr=sr)
    mx     = np.max(np.abs(result))
    if mx > 1e-8:
        result = f32(result / mx * 0.62)
    return f32(result)


def synth_L(F_prev=None, F_next=None,
             pitch_hz=PITCH_HZ,
             dil=DIL, sr=SR):
    dur_ms = L_DUR_MS * dil
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
    n_on   = int(L_COART_ON  * n_s)
    n_off  = int(L_COART_OFF * n_s)
    f_prev = F_prev if F_prev is not None \
             else L_F
    f_next = F_next if F_next is not None \
             else L_F
    result = np.zeros(n_s, dtype=DTYPE)
    for fi in range(len(L_F)):
        f_s   = (float(f_prev[fi])
                 if fi < len(f_prev)
                 else float(L_F[fi]))
        f_e   = (float(f_next[fi])
                 if fi < len(f_next)
                 else float(L_F[fi]))
        f_b   = float(L_F[fi])
        f_arr = np.full(n_s, f_b, dtype=DTYPE)
        if n_on > 0:
            f_arr[:n_on] = np.linspace(
                f_s, f_b, n_on)
        if n_off > 0:
            f_arr[-n_off:] = np.linspace(
                f_b, f_e, n_off)
        bw  = float(L_B[fi])
        g   = float(L_GAINS[fi])
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


def synth_A(F_prev=None, F_next=None,
             pitch_hz=PITCH_HZ,
             dil=DIL, sr=SR):
    dur_ms = A_DUR_MS * dil
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
    n_on   = int(A_COART_ON  * n_s)
    n_off  = int(A_COART_OFF * n_s)
    f_prev = F_prev if F_prev is not None \
             else A_F
    f_next = F_next if F_next is not None \
             else A_F
    result = np.zeros(n_s, dtype=DTYPE)
    for fi in range(len(A_F)):
        f_s   = (float(f_prev[fi])
                 if fi < len(f_prev)
                 else float(A_F[fi]))
        f_e   = (float(f_next[fi])
                 if fi < len(f_next)
                 else float(A_F[fi]))
        f_b   = float(A_F[fi])
        f_arr = np.full(n_s, f_b, dtype=DTYPE)
        if n_on > 0:
            f_arr[:n_on] = np.linspace(
                f_s, f_b, n_on)
        if n_off > 0:
            f_arr[-n_off:] = np.linspace(
                f_b, f_e, n_off)
        bw  = float(A_B[fi])
        g   = float(A_GAINS[fi])
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


def synth_S(F_prev=None, F_next=None,
             dil=DIL, sr=SR):
    dur_ms = S_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    noise  = np.random.randn(n_s).astype(float)
    lo_    = max(S_NOISE_CF - S_NOISE_BW/2,
                 200.0)
    hi_    = min(S_NOISE_CF + S_NOISE_BW/2,
                 SR * 0.48)
    b_bp, a_bp = safe_bp(lo_, hi_, SR)
    fric   = lfilter(b_bp, a_bp, noise)
    n_atk  = min(int(0.008 * sr), n_s // 4)
    n_dec  = min(int(0.010 * sr), n_s // 4)
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
        fric = f32(fric / mx * 0.55)
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

def synth_eorlas(pitch_hz=PITCH_HZ,
                  dil=DIL,
                  add_room=False,
                  sr=SR):
    """[eo·r·l·ɑ·s]"""
    eo_seg = synth_EO(
        F_prev=EO_F_ON, F_next=R_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    r_seg  = synth_R(
        F_prev=EO_F_OFF, F_next=L_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    l_seg  = synth_L(
        F_prev=R_F, F_next=A_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    a_seg  = synth_A(
        F_prev=L_F, F_next=None,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    s_seg  = synth_S(
        F_prev=A_F, F_next=None,
        dil=dil, sr=sr)
    word   = np.concatenate([
        eo_seg, r_seg, l_seg,
        a_seg,  s_seg])
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
    print("EORLAS RECONSTRUCTION v1")
    print("Old English [eorlas]")
    print("Beowulf line 7, word 2")
    print()

    w_dry = synth_eorlas(
        pitch_hz=145.0, dil=1.0,
        add_room=False)
    write_wav(
        "output_play/eorlas_dry.wav",
        w_dry, SR)
    print(f"  eorlas_dry.wav"
          f"  ({len(w_dry)/SR*1000:.0f} ms)")

    w_hall = synth_eorlas(
        pitch_hz=145.0, dil=1.0,
        add_room=True)
    write_wav(
        "output_play/eorlas_hall.wav",
        w_hall, SR)
    print("  eorlas_hall.wav")

    w_slow = ola_stretch(w_dry, 4.0)
    write_wav(
        "output_play/eorlas_slow.wav",
        w_slow, SR)
    print("  eorlas_slow.wav")

    w_perf = synth_eorlas(
        pitch_hz=110.0, dil=2.5,
        add_room=True)
    write_wav(
        "output_play/eorlas_performance.wav",
        w_perf, SR)
    print(f"  eorlas_performance.wav"
          f"  ({len(w_perf)/SR*1000:.0f} ms)")

    print()
    print("  afplay output_play/"
          "eorlas_dry.wav")
    print("  afplay output_play/"
          "eorlas_slow.wav")
    print("  afplay output_play/"
          "eorlas_hall.wav")
    print()
    print("  Line 7 in progress:")
    print("  egsode eorlas,"
          " syþðan ǣrest wearð")
    print()
