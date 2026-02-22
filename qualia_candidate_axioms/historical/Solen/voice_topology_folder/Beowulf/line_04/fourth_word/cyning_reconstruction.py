"""
CYNING RECONSTRUCTION
Old English: cyning
Meaning: king
IPA: [kyniŋɡ]
Beowulf: Line 4, Word 4 (overall word 17)
         Final word of line 4.
February 2026

PHONEME STRUCTURE:
  C   [k]   voiceless velar stop      — verified ÞĒOD-CYNINGA
  Y   [y]   short close front rounded — verified ÞĒOD-CYNINGA
  N   [n]   voiced alveolar nasal     — verified
  I   [ɪ]   short near-close front    — verified IN
  NG  [ŋ]   voiced velar nasal        — verified ÞĒOD-CYNINGA
  G   [ɡ]   voiced velar stop         — verified GĀR-DENA

NEW PHONEMES: none.
Pure assembly. All six from inventory.

[ŋɡ] CLUSTER NOTE:
  OE 'ng' is always [ŋɡ] — velar nasal
  followed by voiced velar stop.
  Never bare [ŋ] as in ModE 'king'.
  The [ɡ] was lost post-[ŋ] in Middle
  English. In OE it is present and
  must be synthesised as a distinct
  event after the nasal.
  [ŋ] offset → [ɡ] closure → burst.
  Two distinct segments, one cluster.

MORPHOLOGICAL NOTE:
  cyning — masculine a-stem noun.
  Nominative singular: cyning (king).
  The root word.
  Previously appeared as cyninga
  (genitive plural: of kings) in
  ÞĒOD-CYNINGA (line 2).
  Here as subject of the sentence:
  þæt wæs gōd cyning —
  that was a good king.
  This closes line 4 and the entire
  opening movement of the poem.
  The first complete evaluative
  verdict. After 17 words of
  subordinate clauses and description,
  the narrator delivers judgment:
  that was a good king.
  Simple. Four words. Final.

  cyning → Modern English 'king':
  [k] — unchanged
  [y] → [ɪ] — rounded front lost
  [n] — unchanged
  [ɪ] — unchanged
  [ŋɡ] → [ŋ] — stop lost post-nasal
  The word survives. The rounded
  vowel and the final stop do not.

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

# K — voiceless velar stop [k]
K_DUR_MS   = 70.0
K_BURST_F  = 1500.0
K_BURST_BW = 700.0
K_BURST_MS = 10.0
K_ASPIR_MS = 15.0   # word-initial aspiration

# Y — short close front rounded [y]
Y_F      = [300.0, 1700.0, 2100.0, 3000.0]
Y_B      = [ 80.0,  120.0,  180.0,  250.0]
Y_GAINS  = [ 16.0,    8.0,    2.0,    0.5]
Y_DUR_MS = 55.0
Y_COART_ON  = 0.12
Y_COART_OFF = 0.12

# N — voiced alveolar nasal [n]
N_F      = [250.0, 1800.0, 2600.0, 3300.0]
N_B      = [100.0,  200.0,  300.0,  350.0]
N_GAINS  = [  8.0,    2.0,    0.5,    0.2]
N_DUR_MS = 65.0
N_ANTI_F = 800.0
N_ANTI_BW= 200.0

# II — short near-close front [ɪ]
II_F      = [390.0, 1900.0, 2500.0, 3200.0]
II_B      = [ 90.0,  120.0,  180.0,  250.0]
II_GAINS  = [ 16.0,    8.0,    1.5,    0.5]
II_DUR_MS = 55.0
II_COART_ON  = 0.12
II_COART_OFF = 0.12

# NG — voiced velar nasal [ŋ]
NG_F      = [280.0, 2200.0, 2800.0, 3300.0]
NG_B      = [100.0,  250.0,  300.0,  350.0]
NG_GAINS  = [  8.0,    1.5,    0.4,    0.2]
NG_DUR_MS = 60.0
NG_ANTI_F = 2000.0
NG_ANTI_BW= 300.0

# G — voiced velar stop [ɡ] word-final
# Shorter than word-initial — light burst,
# no VOT ramp needed, may be unreleased.
G_DUR_MS   = 65.0
G_BURST_F  = 1400.0
G_BURST_BW = 600.0
G_BURST_MS = 10.0
G_VOT_MS   = 5.0    # minimal VOT word-final

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

def synth_K(F_next=None, dil=DIL, sr=SR):
    """
    Voiceless velar stop [k] word-initial.
    Closure + burst + aspiration.
    """
    dur_ms    = K_DUR_MS * dil
    n_s       = max(4, int(dur_ms
                           / 1000.0 * sr))
    n_burst   = max(2, int(K_BURST_MS
                           / 1000.0 * sr))
    n_aspir   = max(2, int(K_ASPIR_MS
                           / 1000.0 * sr))
    n_closure = max(2,
                    n_s - n_burst - n_aspir)
    # Closure — silence
    closure   = np.zeros(n_closure,
                          dtype=DTYPE)
    # Burst — velar
    noise_b   = np.random.randn(
        n_burst).astype(float)
    b_bp, a_bp = safe_bp(
        K_BURST_F - K_BURST_BW / 2,
        K_BURST_F + K_BURST_BW / 2, sr)
    burst     = f32(lfilter(
        b_bp, a_bp, noise_b) * 0.70)
    env_bu    = np.linspace(
        1.0, 0.3, n_burst).astype(DTYPE)
    burst     = f32(burst * env_bu)
    # Aspiration — breathy noise into vowel
    noise_a   = np.random.randn(
        n_aspir).astype(float)
    b_lp, a_lp = safe_lp(4000.0, sr)
    aspir     = f32(lfilter(
        b_lp, a_lp, noise_a) * 0.25)
    env_as    = np.linspace(
        0.5, 0.0, n_aspir).astype(DTYPE)
    aspir     = f32(aspir * env_as)
    seg       = np.concatenate([
        closure, burst, aspir])
    mx        = np.max(np.abs(seg))
    if mx > 1e-8:
        seg = f32(seg / mx * 0.55)
    return f32(seg)


def synth_Y(F_prev=None, F_next=None,
             pitch_hz=PITCH_HZ,
             dil=DIL, sr=SR):
    """
    Short close front rounded [y].
    High front vowel, lips rounded.
    F1 low (~300 Hz), F2 high-mid
    (~1700 Hz) — front quality but
    with lip rounding pulling F2
    slightly lower than [iː].
    """
    dur_ms = Y_DUR_MS * dil
    n_s    = max(4, int(dur_ms
                        / 1000.0 * sr))
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
        result = f32(result / mx * 0.65)
    return f32(result)


def synth_N(F_prev=None, F_next=None,
             pitch_hz=PITCH_HZ,
             dil=DIL, sr=SR):
    dur_ms = N_DUR_MS * dil
    n_s    = max(4, int(dur_ms
                        / 1000.0 * sr))
    src    = rosenberg_pulse(n_s, pitch_hz,
                              oq=0.65, sr=sr)
    n_tr   = min(int(0.020 * sr), n_s // 4)
    env    = np.ones(n_s, dtype=DTYPE)
    if n_tr < n_s:
        env[:n_tr]  = np.linspace(
            0.3, 1.0, n_tr)
        env[-n_tr:] = np.linspace(
            1.0, 0.3, n_tr)
    src    = f32(src * env)
    result = apply_formants(
        src, N_F, N_B, N_GAINS, sr=sr)
    result = iir_notch(
        result, fc=N_ANTI_F,
        bw=N_ANTI_BW, sr=sr)
    mx = np.max(np.abs(result))
    if mx > 1e-8:
        result = f32(result / mx * 0.55)
    return f32(result)


def synth_II(F_prev=None, F_next=None,
              pitch_hz=PITCH_HZ,
              dil=DIL, sr=SR):
    dur_ms = II_DUR_MS * dil
    n_s    = max(4, int(dur_ms
                        / 1000.0 * sr))
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
    n_on   = int(II_COART_ON  * n_s)
    n_off  = int(II_COART_OFF * n_s)
    f_prev = F_prev if F_prev is not None \
             else II_F
    f_next = F_next if F_next is not None \
             else II_F
    result = np.zeros(n_s, dtype=DTYPE)
    for fi in range(len(II_F)):
        f_s   = (float(f_prev[fi])
                 if fi < len(f_prev)
                 else float(II_F[fi]))
        f_e   = (float(f_next[fi])
                 if fi < len(f_next)
                 else float(II_F[fi]))
        f_b   = float(II_F[fi])
        f_arr = np.full(n_s, f_b, dtype=DTYPE)
        if n_on > 0:
            f_arr[:n_on] = np.linspace(
                f_s, f_b, n_on)
        if n_off > 0:
            f_arr[-n_off:] = np.linspace(
                f_b, f_e, n_off)
        bw  = float(II_B[fi])
        g   = float(II_GAINS[fi])
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
        result = f32(result / mx * 0.65)
    return f32(result)


def synth_NG(F_prev=None, F_next=None,
              pitch_hz=PITCH_HZ,
              dil=DIL, sr=SR):
    """
    Voiced velar nasal [ŋ].
    Velar closure — back of tongue
    against soft palate.
    Antiformant ~2000 Hz —
    higher than alveolar nasal [n]
    (~800 Hz) reflecting longer
    oral cavity behind velar closure.
    """
    dur_ms = NG_DUR_MS * dil
    n_s    = max(4, int(dur_ms
                        / 1000.0 * sr))
    src    = rosenberg_pulse(n_s, pitch_hz,
                              oq=0.65, sr=sr)
    n_tr   = min(int(0.020 * sr), n_s // 4)
    env    = np.ones(n_s, dtype=DTYPE)
    if n_tr < n_s:
        env[:n_tr]  = np.linspace(
            0.3, 1.0, n_tr)
        env[-n_tr:] = np.linspace(
            1.0, 0.3, n_tr)
    src    = f32(src * env)
    result = apply_formants(
        src, NG_F, NG_B, NG_GAINS, sr=sr)
    result = iir_notch(
        result, fc=NG_ANTI_F,
        bw=NG_ANTI_BW, sr=sr)
    mx = np.max(np.abs(result))
    if mx > 1e-8:
        result = f32(result / mx * 0.52)
    return f32(result)


def synth_G_final(F_prev=None,
                   pitch_hz=PITCH_HZ,
                   dil=DIL, sr=SR):
    """
    Voiced velar stop [ɡ] word-final.
    After [ŋ] — minimal VOT.
    Short closure + light burst.
    The [ŋ] provides voiced lead-in —
    the closure is already velar,
    so the transition is brief.
    """
    dur_ms    = G_DUR_MS * dil
    n_s       = max(4, int(dur_ms
                           / 1000.0 * sr))
    n_burst   = max(2, int(G_BURST_MS
                           / 1000.0 * sr))
    n_vot     = max(2, int(G_VOT_MS
                           / 1000.0 * sr))
    n_closure = max(2,
                    n_s - n_burst - n_vot)
    T         = 1.0 / sr
    # Voiced closure — continuation
    # of [ŋ] voicing
    src_c  = rosenberg_pulse(
        n_closure, pitch_hz,
        oq=0.65, sr=sr)
    env_c  = np.linspace(
        0.2, 0.1, n_closure).astype(DTYPE)
    b_lp, a_lp = safe_lp(300.0, sr)
    murmur = f32(lfilter(
        b_lp, a_lp,
        src_c.astype(float))
                 * env_c * 0.25)
    # Light burst — word-final
    noise  = np.random.randn(
        n_burst).astype(float)
    b_bp, a_bp = safe_bp(
        G_BURST_F - G_BURST_BW / 2,
        G_BURST_F + G_BURST_BW / 2, sr)
    burst  = f32(lfilter(
        b_bp, a_bp, noise) * 0.45)
    env_bu = np.linspace(
        1.0, 0.0, n_burst).astype(DTYPE)
    burst  = f32(burst * env_bu)
    # Minimal VOT — word-final
    src_v  = rosenberg_pulse(
        n_vot, pitch_hz, oq=0.65, sr=sr)
    vot    = f32(src_v * 0.15)
    seg    = np.concatenate([
        murmur, burst, vot])
    mx     = np.max(np.abs(seg))
    if mx > 1e-8:
        seg = f32(seg / mx * 0.50)
    return f32(seg)


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

def synth_cyning(pitch_hz=PITCH_HZ,
                  dil=DIL,
                  add_room=False,
                  sr=SR):
    """[k·y·n·ɪ·ŋ·ɡ]"""
    k_seg  = synth_K(
        F_next=Y_F, dil=dil, sr=sr)
    y_seg  = synth_Y(
        F_prev=Y_F, F_next=N_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    n_seg  = synth_N(
        F_prev=Y_F, F_next=II_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    ii_seg = synth_II(
        F_prev=N_F, F_next=NG_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    ng_seg = synth_NG(
        F_prev=II_F, F_next=None,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    g_seg  = synth_G_final(
        F_prev=NG_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    word   = np.concatenate([
        k_seg, y_seg, n_seg,
        ii_seg, ng_seg, g_seg])
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
    print("CYNING RECONSTRUCTION v1")
    print("Old English [kyniŋɡ]")
    print("Beowulf line 4, word 4")
    print("Final word of line 4.")
    print()

    w_dry = synth_cyning(
        pitch_hz=145.0, dil=1.0,
        add_room=False)
    write_wav(
        "output_play/cyning_dry.wav",
        w_dry, SR)
    print(f"  cyning_dry.wav"
          f"  ({len(w_dry)/SR*1000:.0f} ms)")

    w_hall = synth_cyning(
        pitch_hz=145.0, dil=1.0,
        add_room=True)
    write_wav(
        "output_play/cyning_hall.wav",
        w_hall, SR)
    print("  cyning_hall.wav")

    w_slow = ola_stretch(w_dry, 4.0)
    write_wav(
        "output_play/cyning_slow.wav",
        w_slow, SR)
    print("  cyning_slow.wav")

    w_perf = synth_cyning(
        pitch_hz=110.0, dil=2.5,
        add_room=True)
    write_wav(
        "output_play/cyning_performance.wav",
        w_perf, SR)
    print(f"  cyning_performance.wav"
          f"  ({len(w_perf)/SR*1000:.0f} ms)")

    # [ŋɡ] cluster isolated
    ng_seg = synth_NG(II_F, None,
                       145.0, 1.0, SR)
    g_seg  = synth_G_final(NG_F,
                            145.0, 1.0, SR)
    ng_g   = np.concatenate([ng_seg, g_seg])
    mx_ng  = np.max(np.abs(ng_g))
    if mx_ng > 1e-8:
        ng_g = f32(ng_g / mx_ng * 0.75)
    write_wav(
        "output_play/cyning_ng_cluster.wav",
        ola_stretch(ng_g, 4.0), SR)
    print("  cyning_ng_cluster.wav  (4x slow)")
    print()
    print("  afplay output_play/"
          "cyning_ng_cluster.wav")
    print("  afplay output_play/"
          "cyning_dry.wav")
    print("  afplay output_play/"
          "cyning_slow.wav")
    print("  afplay output_play/"
          "cyning_hall.wav")
    print()
    print("  LINE 4 COMPLETE:")
    print("  þæt wæs gōd cyning")
    print()
    print("  FOUR LINES OF BEOWULF")
    print("  RECONSTRUCTED.")
    print()
