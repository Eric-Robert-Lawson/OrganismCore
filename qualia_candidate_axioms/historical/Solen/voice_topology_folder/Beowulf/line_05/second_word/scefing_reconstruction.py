"""
SCEFING RECONSTRUCTION
Old English: Scefing
Meaning: son of Scēaf (patronymic)
IPA: [ʃeviŋɡ]
Beowulf: Line 5, Word 2 (overall word 19)
February 2026

PHONEME STRUCTURE:
  SC  [ʃ]   voiceless postalveolar fric. — verified SCYLD
  E   [e]   short close-mid front        — verified GĀR-DENA
  F   [v]   voiced labiodental fric.     — NEW
  I   [ɪ]   short near-close front       — verified
  NG  [ŋ]   voiced velar nasal           — verified
  G   [ɡ]   voiced velar stop            — verified

NEW PHONEMES:
  [v]: voiced labiodental fricative.
       Allophone of /f/ between voiced
       segments in Old English.
       Intervocalic 'f' → [v].
       Spelling unchanged — manuscript
       writes 'f' — sound is [v].
       Same labiodental constriction
       as [f]: upper teeth, lower lip.
       Same turbulent airflow.
       Vocal folds vibrating throughout.
       Centroid similar to [f] but
       voicing gives buzzing undertone.
       [v] here: between [e] and [ɪ] —
       fully intervocalic — full voicing.

       Same process:
       OE 'ofer' [over] → ModE 'over'
       OE 'heofon' → ModE 'heaven'
       OE 'seofon' → ModE 'seven'
       The [v] spelling in Modern English
       descends from OE intervocalic [f].

REUSED PHONEMES:
  [ʃ]:  SCYLD
  [e]:  GĀR-DENA (×2)
  [ɪ]:  IN, GĒAR-DAGUM, ÆÞELINGAS,
        CYNING
  [ŋ]:  ÞĒOD-CYNINGA (×2), CYNING
  [ɡ]:  GĀR-DENA, GĒAR-DAGUM,
        GEFRŪNON, ÆÞELINGAS,
        FREMEDON, GŌD, CYNING (×2)

NOTE ON [v] SYNTHESIS:
  [f] parameters:
    noise CF ~4500 Hz
    noise BW ~3000 Hz
    voiceless
  [v] parameters:
    same noise CF and BW
    voicing added — Rosenberg pulse
    filtered through labiodental
    constriction noise
    mixed: voiced source + frication
    voicing fraction ~0.4
    frication fraction ~0.6
  The mix gives voiced fricative
  character — buzz under hiss.

MORPHOLOGICAL NOTE:
  Scefing — patronymic suffix -ing.
  Meaning: of Scēaf, son of Scēaf.
  Scēaf = sheaf (of grain).
  Legendary figure — arrived by
  boat as a child with a sheaf,
  became a king, founded a line.
  The suffix -ing is productive in OE:
  Ēadwining = son of Eadwine.
  Scylding = of the Scyld dynasty.
  It survives in Modern English
  place names: Reading, Worthing,
  Hastings — all 'people of X'.

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

# SH — voiceless postalveolar fricative [ʃ]
SH_DUR_MS   = 80.0
SH_NOISE_CF = 3800.0
SH_NOISE_BW = 2400.0
SH_GAIN     = 0.30
SH_SEC_CF   = 6000.0
SH_SEC_BW   = 2000.0
SH_SEC_GAIN = 0.20

# E — short close-mid front [e]
E_F      = [450.0, 1900.0, 2600.0, 3300.0]
E_B      = [100.0,  130.0,  200.0,  280.0]
E_GAINS  = [ 16.0,    8.0,    1.5,    0.5]
E_DUR_MS = 55.0
E_COART_ON  = 0.12
E_COART_OFF = 0.12

# V — voiced labiodental fricative [v]
V_DUR_MS    = 70.0
V_NOISE_CF  = 4500.0
V_NOISE_BW  = 3000.0
V_FRIC_GAIN = 0.22
V_VOICE_MIX = 0.40   # voiced source fraction
V_FRIC_MIX  = 0.60   # frication fraction

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
G_DUR_MS   = 65.0
G_BURST_F  = 1400.0
G_BURST_BW = 600.0
G_BURST_MS = 10.0
G_VOT_MS   = 5.0

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

def synth_SH(F_next=None, dil=DIL, sr=SR):
    dur_ms = SH_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    noise  = np.random.randn(n_s).astype(float)
    lo1    = max(SH_NOISE_CF - SH_NOISE_BW/2,
                 200.0)
    hi1    = min(SH_NOISE_CF + SH_NOISE_BW/2,
                 sr * 0.48)
    b1, a1 = safe_bp(lo1, hi1, sr)
    fric1  = lfilter(b1, a1, noise)
    lo2    = max(SH_SEC_CF - SH_SEC_BW/2,
                 200.0)
    hi2    = min(SH_SEC_CF + SH_SEC_BW/2,
                 sr * 0.48)
    b2, a2 = safe_bp(lo2, hi2, sr)
    fric2  = lfilter(b2, a2, noise)
    fric   = (fric1 * SH_GAIN
              + fric2 * SH_SEC_GAIN)
    n_atk  = min(int(0.012 * sr), n_s // 4)
    n_dec  = min(int(0.020 * sr), n_s // 4)
    env    = np.ones(n_s, dtype=float)
    if n_atk < n_s:
        env[:n_atk] = np.linspace(
            0.0, 1.0, n_atk)
    if n_dec < n_s:
        env[-n_dec:] = np.linspace(
            1.0, 0.3, n_dec)
    fric   = f32(fric * env)
    mx     = np.max(np.abs(fric))
    if mx > 1e-8:
        fric = f32(fric / mx * 0.45)
    return f32(fric)


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


def synth_V(F_prev=None, F_next=None,
             pitch_hz=PITCH_HZ,
             dil=DIL, sr=SR):
    """
    Voiced labiodental fricative [v].
    Intervocalic position — full voicing.
    Mixed source: Rosenberg pulse
    (voiced component) + bandpass noise
    (frication component).
    Upper teeth against lower lip.
    Same constriction geometry as [f]
    but vocal folds vibrating.
    """
    dur_ms = V_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    T      = 1.0 / sr
    # Voiced source
    src_v  = rosenberg_pulse(n_s, pitch_hz,
                              oq=0.65, sr=sr)
    # Frication noise — same band as [f]
    noise  = np.random.randn(n_s).astype(float)
    lo_    = max(V_NOISE_CF - V_NOISE_BW/2,
                 200.0)
    hi_    = min(V_NOISE_CF + V_NOISE_BW/2,
                 sr * 0.48)
    b_bp, a_bp = safe_bp(lo_, hi_, sr)
    fric   = lfilter(b_bp, a_bp, noise)
    # Envelope — full voicing onset/offset
    # intervocalic — no silence boundaries
    n_atk  = min(int(0.010 * sr), n_s // 4)
    n_rel  = min(int(0.010 * sr), n_s // 4)
    env_v  = np.ones(n_s, dtype=DTYPE)
    env_f  = np.ones(n_s, dtype=DTYPE)
    if n_atk < n_s:
        env_v[:n_atk] = np.linspace(
            0.3, 1.0, n_atk)
        env_f[:n_atk] = np.linspace(
            0.0, 1.0, n_atk)
    if n_rel < n_s:
        env_v[-n_rel:] = np.linspace(
            1.0, 0.3, n_rel)
        env_f[-n_rel:] = np.linspace(
            1.0, 0.0, n_rel)
    # Filter voiced source through
    # labiodental approximation
    b_lp, a_lp = safe_lp(3000.0, sr)
    voiced = f32(lfilter(b_lp, a_lp,
                          src_v.astype(float))
                 * env_v)
    fric   = f32(fric * env_f * V_FRIC_GAIN)
    # Mix voiced + frication
    mix    = (voiced * V_VOICE_MIX
              + fric  * V_FRIC_MIX)
    mx     = np.max(np.abs(mix))
    if mx > 1e-8:
        mix = f32(mix / mx * 0.60)
    return f32(mix)


def synth_II(F_prev=None, F_next=None,
              pitch_hz=PITCH_HZ,
              dil=DIL, sr=SR):
    dur_ms = II_DUR_MS * dil
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


def synth_NG(F_prev=None, F_next=None,
              pitch_hz=PITCH_HZ,
              dil=DIL, sr=SR):
    dur_ms = NG_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
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

def synth_scefing(pitch_hz=PITCH_HZ,
                   dil=DIL,
                   add_room=False,
                   sr=SR):
    """[ʃ·e·v·ɪ·ŋ·ɡ]"""
    sh_seg = synth_SH(
        F_next=E_F, dil=dil, sr=sr)
    e_seg  = synth_E(
        F_prev=E_F, F_next=None,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    v_seg  = synth_V(
        F_prev=E_F, F_next=II_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    ii_seg = synth_II(
        F_prev=None, F_next=NG_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    ng_seg = synth_NG(
        F_prev=II_F, F_next=None,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    g_seg  = synth_G_final(
        F_prev=NG_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    word   = np.concatenate([
        sh_seg, e_seg, v_seg,
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
    print("SCEFING RECONSTRUCTION v1")
    print("Old English [ʃeviŋɡ]")
    print("Beowulf line 5, word 2")
    print()

    w_dry = synth_scefing(
        pitch_hz=145.0, dil=1.0,
        add_room=False)
    write_wav(
        "output_play/scefing_dry.wav",
        w_dry, SR)
    print(f"  scefing_dry.wav"
          f"  ({len(w_dry)/SR*1000:.0f} ms)")

    w_hall = synth_scefing(
        pitch_hz=145.0, dil=1.0,
        add_room=True)
    write_wav(
        "output_play/scefing_hall.wav",
        w_hall, SR)
    print("  scefing_hall.wav")

    w_slow = ola_stretch(w_dry, 4.0)
    write_wav(
        "output_play/scefing_slow.wav",
        w_slow, SR)
    print("  scefing_slow.wav")

    w_perf = synth_scefing(
        pitch_hz=110.0, dil=2.5,
        add_room=True)
    write_wav(
        "output_play/scefing_performance.wav",
        w_perf, SR)
    print(f"  scefing_performance.wav"
          f"  ({len(w_perf)/SR*1000:.0f} ms)")

    # [v] vs [f] comparison
    v_seg  = synth_V(E_F, II_F,
                      145.0, 1.0, SR)
    write_wav(
        "output_play/scefing_v_only.wav",
        ola_stretch(v_seg / (
            np.max(np.abs(v_seg))+1e-8)
            * 0.75, 4.0), SR)
    print("  scefing_v_only.wav  (4x slow)")
    print()
    print("  afplay output_play/"
          "scefing_v_only.wav")
    print("  afplay output_play/"
          "scefing_dry.wav")
    print("  afplay output_play/"
          "scefing_slow.wav")
    print("  afplay output_play/"
          "scefing_hall.wav")
    print()
    print("  Line 5 in progress:")
    print("  Scyld Scefing"
          " sceaþena þreatum")
    print()
