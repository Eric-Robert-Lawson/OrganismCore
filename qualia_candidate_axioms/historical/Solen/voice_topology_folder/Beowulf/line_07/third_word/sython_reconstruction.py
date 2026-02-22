"""
SYÞÐAN RECONSTRUCTION
Old English: syþðan
Meaning: since, after, when (conjunction)
IPA: [syθðɑn]
Beowulf: Line 7, Word 3 (overall word 28)
February 2026

PHONEME STRUCTURE:
  S   [s]    voiceless alveolar fric.   — verified ÆÞELINGAS
  Y   [y]    short close front rounded  — verified ÞĒOD-CYNINGA
  Þ   [θ]    voiceless dental fricative — verified ÞĒOD-CYNINGA
  Ð   [ð]    voiced dental fricative    — verified ÐĀ
  A   [ɑ]    short open back            — verified GĀR-DENA
  N   [n]    voiced alveolar nasal      — verified GĀR-DENA

NEW PHONEMES: none.
Pure assembly.

NOTE ON [θð] CLUSTER:
  Voiceless dental → voiced dental.
  Same place — tongue tip at upper teeth.
  Same manner — fricative.
  Only laryngeal setting changes.
  Tongue does not move at boundary.
  Vocal folds start vibrating
  at the [θ]→[ð] transition.
  The transition is purely laryngeal —
  the most minimal possible change
  between two consonants.
  Diagnostic: [θ] voicing <= 0.35,
  [ð] voicing >= 0.35. Separation
  confirmed across the boundary.

NOTE ON [sy] ONSET:
  Word-initial [s]→[y].
  Voiceless fricative into close
  front rounded vowel.
  The lip rounding of [y] begins
  during the [s] — anticipatory
  rounding. The [s] here may have
  slight lip rounding colouring
  at its offset. Not modelled
  explicitly — noted.

ETYMOLOGY:
  syþþan / siþþan — since, after.
  Compound: sið (journey, time) +
  þan (instrumental case marker).
  'from that journey/time'.
  Extremely frequent in OE poetry —
  the word that marks the before/after
  boundary of every narrative event.
  ModE 'since' from OE 'siþþan'
  via contraction and sound change.

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

# S — voiceless alveolar fricative [s]
S_DUR_MS   = 65.0
S_NOISE_CF = 7500.0
S_NOISE_BW = 4000.0
S_GAIN     = 0.55

# Y — short close front rounded [y]
Y_F      = [300.0, 1500.0, 2100.0, 3100.0]
Y_B      = [ 80.0,  120.0,  200.0,  260.0]
Y_GAINS  = [ 16.0,    8.0,    1.5,    0.5]
Y_DUR_MS = 55.0
Y_COART_ON  = 0.12
Y_COART_OFF = 0.12

# TH — voiceless dental fricative [θ]
TH_DUR_MS   = 70.0
TH_NOISE_CF = 5000.0
TH_NOISE_BW = 3000.0
TH_GAIN     = 0.18

# DH — voiced dental fricative [ð]
DH_DUR_MS   = 70.0
DH_F        = [400.0, 1200.0, 2600.0]
DH_B        = [350.0,  450.0,  550.0]
DH_GAINS    = [  5.0,    2.5,    0.8]
DH_AM_RATE  = 80.0
DH_AM_DEPTH = 0.25

# A — short open back [ɑ]
A_F      = [700.0, 1100.0, 2500.0, 3200.0]
A_B      = [120.0,  150.0,  200.0,  280.0]
A_GAINS  = [ 16.0,    8.0,    1.5,    0.5]
A_DUR_MS = 55.0
A_COART_ON  = 0.12
A_COART_OFF = 0.12

# N — voiced alveolar nasal [n]
N_F      = [250.0, 1700.0, 2500.0, 3200.0]
N_B      = [100.0,  200.0,  300.0,  350.0]
N_GAINS  = [  8.0,    2.0,    0.5,    0.2]
N_DUR_MS = 60.0
N_ANTI_F = 1500.0
N_ANTI_BW= 200.0

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
# IIR NOTCH
# ============================================================

def iir_notch(sig, fc, bw=200.0, sr=SR):
    T  = 1.0 / sr
    wc = 2 * np.pi * fc * T
    r  = float(np.clip(
        1.0 - np.pi * bw * T, 0.1, 0.999))
    b1 = -2.0 * np.cos(wc)
    b2 =  1.0
    a1 = -2.0 * r * np.cos(wc)
    a2 =  r * r
    gain_dc = abs((1 + b1 + b2)
                  / (1 + a1 + a2 + 1e-12))
    if gain_dc > 1e-6:
        b1_n = b1 / gain_dc
        b2_n = b2 / gain_dc
    else:
        b1_n = b1
        b2_n = b2
    b0  = 1.0
    n   = len(sig)
    out = np.zeros(n, dtype=DTYPE)
    x   = sig.astype(float)
    y1 = y2 = x1 = x2 = 0.0
    for i in range(n):
        xi     = x[i]
        yi     = (b0 * xi + b1_n * x1
                  + b2_n * x2
                  - a1 * y1 - a2 * y2)
        x2     = x1
        x1     = xi
        y2     = y1
        y1     = yi
        out[i] = yi
    return f32(out)


# ============================================================
# PHONEME SYNTHESIZERS
# ============================================================

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
            1.0, 0.5, n_dec)
    fric   = f32(fric * env * S_GAIN)
    mx     = np.max(np.abs(fric))
    if mx > 1e-8:
        fric = f32(fric / mx * 0.55)
    return f32(fric)


def synth_Y(F_prev=None, F_next=None,
             pitch_hz=PITCH_HZ,
             dil=DIL, sr=SR):
    """
    Short close front rounded [y].
    Post-[s] position here.
    Same parameters as ÞĒOD-CYNINGA.
    F1 low (~300 Hz) — close height.
    F2 mid (~1500 Hz) — front but
    pulled down by rounding relative
    to unrounded [i] (~2300 Hz).
    Lip rounding is the key feature.
    """
    dur_ms = Y_DUR_MS * dil
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
    n_on   = int(Y_COART_ON  * n_s)
    n_off  = int(Y_COART_OFF * n_s)
    f_prev = F_prev if F_prev is not None \
             else Y_F
    f_next = F_next if F_next is not None \
             else Y_F
    result = np.zeros(n_s, dtype=DTYPE)
    for fi in range(len(Y_F)):
        f_s   = (float(f_prev[fi])
                 if fi < len(f_prev)
                 else float(Y_F[fi]))
        f_e   = (float(f_next[fi])
                 if fi < len(f_next)
                 else float(Y_F[fi]))
        f_b   = float(Y_F[fi])
        f_arr = np.full(n_s, f_b, dtype=DTYPE)
        if n_on > 0:
            f_arr[:n_on] = np.linspace(
                f_s, f_b, n_on)
        if n_off > 0:
            f_arr[-n_off:] = np.linspace(
                f_b, f_e, n_off)
        bw  = float(Y_B[fi])
        g   = float(Y_GAINS[fi])
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
        result = f32(result / mx * 0.65)
    return f32(result)


def synth_TH(F_prev=None, F_next=None,
              dil=DIL, sr=SR):
    """
    Voiceless dental fricative [θ].
    Pre-[ð] position — the [θð] cluster.
    Same parameters as all previous
    instances. Tongue tip at upper teeth,
    voiceless airflow through dental gap.
    """
    dur_ms = TH_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    noise  = np.random.randn(n_s).astype(float)
    lo_    = max(TH_NOISE_CF - TH_NOISE_BW/2,
                 200.0)
    hi_    = min(TH_NOISE_CF + TH_NOISE_BW/2,
                 SR * 0.48)
    b_bp, a_bp = safe_bp(lo_, hi_, SR)
    fric   = lfilter(b_bp, a_bp, noise)
    n_atk  = min(int(0.010 * sr), n_s // 4)
    n_dec  = min(int(0.015 * sr), n_s // 4)
    env    = np.ones(n_s, dtype=float)
    if n_atk < n_s:
        env[:n_atk] = np.linspace(
            0.0, 1.0, n_atk)
    if n_dec < n_s:
        env[-n_dec:] = np.linspace(
            1.0, 0.0, n_dec)
    fric   = f32(fric * env * TH_GAIN)
    mx     = np.max(np.abs(fric))
    if mx > 1e-8:
        fric = f32(fric / mx * 0.35)
    return f32(fric)


def synth_DH(F_prev=None, F_next=None,
              pitch_hz=PITCH_HZ,
              dil=DIL, sr=SR):
    """
    Voiced dental fricative [ð].
    Post-[θ] position — [θð] cluster.
    Same strategy as [v] and [ɣ]:
    pure voiced source, AM modulation,
    no noise. Dental constriction band.
    Tongue position identical to [θ] —
    only voicing changes at boundary.
    AM rate 80 Hz — turbulence flutter.
    """
    dur_ms = DH_DUR_MS * dil
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
    am     = (1.0 - DH_AM_DEPTH
              + DH_AM_DEPTH
              * np.sin(2 * np.pi
                       * DH_AM_RATE
                       * t_arr))
    src    = f32(src * am.astype(DTYPE))
    result = apply_formants(
        src, DH_F, DH_B, DH_GAINS, sr=sr)
    mx     = np.max(np.abs(result))
    if mx > 1e-8:
        result = f32(result / mx * 0.52)
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


def synth_N(F_prev=None, F_next=None,
             pitch_hz=PITCH_HZ,
             dil=DIL, sr=SR):
    dur_ms = N_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    src    = rosenberg_pulse(n_s, pitch_hz,
                              oq=0.65, sr=sr)
    n_tr   = min(int(0.020 * sr), n_s // 4)
    env    = np.ones(n_s, dtype=DTYPE)
    if n_tr < n_s:
        env[:n_tr]  = np.linspace(
            0.3, 1.0, n_tr)
        env[-n_tr:] = np.linspace(
            1.0, 0.0, n_tr)
    src    = f32(src * env)
    result = apply_formants(
        src, N_F, N_B, N_GAINS, sr=sr)
    result = iir_notch(
        result, fc=N_ANTI_F,
        bw=N_ANTI_BW, sr=sr)
    mx = np.max(np.abs(result))
    if mx > 1e-8:
        result = f32(result / mx * 0.50)
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

def synth_sython(pitch_hz=PITCH_HZ,
                  dil=DIL,
                  add_room=False,
                  sr=SR):
    """[s·y·θ·ð·ɑ·n]"""
    s_seg  = synth_S(
        F_prev=None, F_next=Y_F,
        dil=dil, sr=sr)
    y_seg  = synth_Y(
        F_prev=Y_F, F_next=None,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    th_seg = synth_TH(
        F_prev=Y_F, F_next=None,
        dil=dil, sr=sr)
    dh_seg = synth_DH(
        F_prev=None, F_next=A_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    a_seg  = synth_A(
        F_prev=A_F, F_next=N_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    n_seg  = synth_N(
        F_prev=A_F, F_next=None,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    word   = np.concatenate([
        s_seg,  y_seg,  th_seg,
        dh_seg, a_seg,  n_seg])
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
    print("SYÞÐAN RECONSTRUCTION v1")
    print("Old English [syθðɑn]")
    print("Beowulf line 7, word 3")
    print()

    w_dry = synth_sython(
        pitch_hz=145.0, dil=1.0,
        add_room=False)
    write_wav(
        "output_play/sython_dry.wav",
        w_dry, SR)
    print(f"  sython_dry.wav"
          f"  ({len(w_dry)/SR*1000:.0f} ms)")

    w_hall = synth_sython(
        pitch_hz=145.0, dil=1.0,
        add_room=True)
    write_wav(
        "output_play/sython_hall.wav",
        w_hall, SR)
    print("  sython_hall.wav")

    w_slow = ola_stretch(w_dry, 4.0)
    write_wav(
        "output_play/sython_slow.wav",
        w_slow, SR)
    print("  sython_slow.wav")

    # [θð] cluster isolated
    th_seg = synth_TH(Y_F, None, 1.0, SR)
    dh_seg = synth_DH(None, A_F,
                       145.0, 1.0, SR)
    cluster = np.concatenate([th_seg, dh_seg])
    mx_c    = np.max(np.abs(cluster))
    if mx_c > 1e-8:
        cluster = f32(cluster / mx_c * 0.75)
    write_wav(
        "output_play/sython_thDH_only.wav",
        ola_stretch(cluster, 4.0), SR)
    print("  sython_thDH_only.wav  (4x slow)")

    print()
    print("  afplay output_play/"
          "sython_thDH_only.wav")
    print("  afplay output_play/"
          "sython_dry.wav")
    print("  afplay output_play/"
          "sython_slow.wav")
    print()
    print("  Line 7 in progress:")
    print("  egsode eorlas,"
          " syþðan ǣrest wearð")
    print()
