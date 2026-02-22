"""
MǢGÞUM RECONSTRUCTION
Old English: mǣgþum
Meaning: kinship groups, tribes (dative plural)
IPA: [mæːɣθum]
Beowulf: Line 6, Word 2 (overall word 23)
February 2026

PHONEME STRUCTURE:
  M   [m]    voiced bilabial nasal      — verified GĒAR-DAGUM
  Ǣ   [æː]   long open front unrounded  — NEW
  G   [ɣ]    voiced velar fricative     — NEW
  Þ   [θ]    voiceless dental fricative — verified ÞĒOD-CYNINGA
  U   [u]    short close back rounded   — verified GĒAR-DAGUM
  M   [m]    voiced bilabial nasal      — verified GĒAR-DAGUM

NEW PHONEMES:
  [æː]: long open front unrounded.
        Long version of [æ] (verified HWÆT).
        Same quality — same tongue position:
          F1 ~800 Hz  (open)
          F2 ~1700 Hz (front)
        Duration doubled vs [æ]:
          [æ]  short ~50 ms
          [æː] long  ~100 ms
        Length is the sole distinction.
        OE spelling: ǣ (ae with macron).
        Extremely frequent in OE:
        mǣg (kinsman), dǣd (deed),
        sǣ (sea), hǣl (health/hale),
        wǣpn (weapon), stǣnen (stone adj).

  [ɣ]: voiced velar fricative.
       Voiced counterpart of [x]
       (verified HU).
       Same place — tongue dorsum
       raised toward velum.
       Same manner — fricative,
       constriction without closure.
       Voicing added — vocal folds
       vibrating throughout.
       Centroid similar to [x]
       (~2500–4000 Hz) but with
       strong low-frequency voicing
       component below 500 Hz.
       Strategy: same as [v] —
       pure voiced source filtered
       through velar constriction
       bandpass. No noise component.
       AM modulation at 80 Hz
       simulates turbulence flutter.
       Intervocalic here: [æː]→[ɣ]→[θ]
       Full voicing expected.
       OE spelling: 'g' between
       voiced segments.
       Also appears in:
       monig [monɪɣ], dragan [draɣan],
       boga [boɣa], maga [maɣa].

REUSED PHONEMES:
  [m]:  GĒAR-DAGUM (×2 here)
  [æː]: long — new this word
  [θ]:  ÞĒOD-CYNINGA (×7 instances)
  [u]:  GĒAR-DAGUM
  [m]:  GĒAR-DAGUM

NOTE ON [ɣ] vs [x]:
  [x] verified HU — voiceless velar fric.
  [ɣ] is its voiced pair.
  Same filter parameters — velar
  constriction band ~800–4000 Hz.
  Distinction: voicing only.
  [x] voicing score ~0.10 (verified).
  [ɣ] target voicing >= 0.35.
  Same diagnostic structure as
  [v]/[f] distinction in SCEFING.

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

# M — voiced bilabial nasal [m]
M_F      = [250.0, 1000.0, 2500.0, 3200.0]
M_B      = [100.0,  200.0,  300.0,  350.0]
M_GAINS  = [  8.0,    2.0,    0.5,    0.2]
M_DUR_MS = 65.0
M_ANTI_F = 1000.0
M_ANTI_BW= 200.0

# AE_LONG — long open front unrounded [æː]
# Same quality as [æ] — doubled duration.
# F1 ~800 Hz (open), F2 ~1700 Hz (front).
AEL_F      = [800.0, 1700.0, 2500.0, 3200.0]
AEL_B      = [120.0,  130.0,  200.0,  280.0]
AEL_GAINS  = [ 16.0,    8.0,    1.5,    0.5]
AEL_DUR_MS = 100.0   # long — ~2× short [æ]
AEL_COART_ON  = 0.10
AEL_COART_OFF = 0.10

# GH — voiced velar fricative [ɣ]
# Pure voiced source — no noise.
# Same strategy as [v] in SCEFING v3.
# Velar constriction band: 800–4000 Hz.
# AM modulation at 80 Hz.
GH_DUR_MS   = 70.0
GH_F        = [500.0, 1500.0, 2800.0]
GH_B        = [400.0,  500.0,  600.0]
GH_GAINS    = [  6.0,    3.0,    1.0]
GH_AM_RATE  = 80.0
GH_AM_DEPTH = 0.25

# TH — voiceless dental fricative [θ]
TH_DUR_MS   = 75.0
TH_NOISE_CF = 5000.0
TH_NOISE_BW = 3000.0
TH_GAIN     = 0.18

# U — short close back rounded [u]
U_F      = [300.0,  800.0, 2300.0, 3100.0]
U_B      = [ 80.0,  120.0,  200.0,  260.0]
U_GAINS  = [ 16.0,    8.0,    1.5,    0.5]
U_DUR_MS = 55.0
U_COART_ON  = 0.12
U_COART_OFF = 0.12

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

def synth_M(F_prev=None, F_next=None,
             pitch_hz=PITCH_HZ,
             dil=DIL, sr=SR):
    dur_ms = M_DUR_MS * dil
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
        src, M_F, M_B, M_GAINS, sr=sr)
    result = iir_notch(
        result, fc=M_ANTI_F,
        bw=M_ANTI_BW, sr=sr)
    mx = np.max(np.abs(result))
    if mx > 1e-8:
        result = f32(result / mx * 0.50)
    return f32(result)


def synth_AEL(F_prev=None, F_next=None,
               pitch_hz=PITCH_HZ,
               dil=DIL, sr=SR):
    """
    Long open front unrounded [æː].
    Long version of [æ] (verified HWÆT).
    Same formant targets — doubled duration.
    F1 ~800 Hz (open jaw position).
    F2 ~1700 Hz (front tongue body).
    The length is the phonemic distinction
    from short [æ]. Quality identical.
    """
    dur_ms = AEL_DUR_MS * dil
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
            1.0, 0.6, n_rel)
    src    = f32(src * env)
    n_on   = int(AEL_COART_ON  * n_s)
    n_off  = int(AEL_COART_OFF * n_s)
    f_prev = F_prev if F_prev is not None \
             else AEL_F
    f_next = F_next if F_next is not None \
             else AEL_F
    result = np.zeros(n_s, dtype=DTYPE)
    for fi in range(len(AEL_F)):
        f_s   = (float(f_prev[fi])
                 if fi < len(f_prev)
                 else float(AEL_F[fi]))
        f_e   = (float(f_next[fi])
                 if fi < len(f_next)
                 else float(AEL_F[fi]))
        f_b   = float(AEL_F[fi])
        f_arr = np.full(n_s, f_b, dtype=DTYPE)
        if n_on > 0:
            f_arr[:n_on] = np.linspace(
                f_s, f_b, n_on)
        if n_off > 0:
            f_arr[-n_off:] = np.linspace(
                f_b, f_e, n_off)
        bw  = float(AEL_B[fi])
        g   = float(AEL_GAINS[fi])
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
        result = f32(result / mx * 0.70)
    return f32(result)


def synth_GH(F_prev=None, F_next=None,
              pitch_hz=PITCH_HZ,
              dil=DIL, sr=SR):
    """
    Voiced velar fricative [ɣ].
    Voiced counterpart of [x] (verified HU).
    Pure voiced source — no noise.
    Same strategy as [v] in SCEFING v3:
    Rosenberg pulse filtered through
    velar constriction band formants.
    AM modulation at 80 Hz — flutter.
    Intervocalic here — full voicing.
    Tongue dorsum raised toward velum —
    constriction without full closure.
    Broad bandwidth formants model the
    distributed velar constriction.
    """
    dur_ms = GH_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    T      = 1.0 / sr
    src    = rosenberg_pulse(n_s, pitch_hz,
                              oq=0.65, sr=sr)
    # Onset/offset envelope
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
    # AM modulation — velar flutter
    t_arr  = np.arange(n_s) * T
    am     = (1.0 - GH_AM_DEPTH
              + GH_AM_DEPTH
              * np.sin(2 * np.pi
                       * GH_AM_RATE
                       * t_arr))
    src    = f32(src * am.astype(DTYPE))
    # Filter through velar constriction
    result = apply_formants(
        src, GH_F, GH_B, GH_GAINS, sr=sr)
    mx     = np.max(np.abs(result))
    if mx > 1e-8:
        result = f32(result / mx * 0.55)
    return f32(result)


def synth_TH(F_prev=None, F_next=None,
              dil=DIL, sr=SR):
    dur_ms = TH_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    noise  = np.random.randn(n_s).astype(float)
    lo_    = max(TH_NOISE_CF - TH_NOISE_BW/2,
                 200.0)
    hi_    = min(TH_NOISE_CF + TH_NOISE_BW/2,
                 sr * 0.48)
    b_bp, a_bp = safe_bp(lo_, hi_, sr)
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


def synth_U(F_prev=None, F_next=None,
             pitch_hz=PITCH_HZ,
             dil=DIL, sr=SR):
    dur_ms = U_DUR_MS * dil
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

def synth_maegthum(pitch_hz=PITCH_HZ,
                    dil=DIL,
                    add_room=False,
                    sr=SR):
    """[m·æː·ɣ·θ·u·m]"""
    m1_seg  = synth_M(
        F_prev=None, F_next=AEL_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    ael_seg = synth_AEL(
        F_prev=M_F, F_next=GH_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    gh_seg  = synth_GH(
        F_prev=AEL_F, F_next=None,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    th_seg  = synth_TH(
        F_prev=None, F_next=U_F,
        dil=dil, sr=sr)
    u_seg   = synth_U(
        F_prev=U_F, F_next=M_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    m2_seg  = synth_M(
        F_prev=U_F, F_next=None,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    word    = np.concatenate([
        m1_seg, ael_seg, gh_seg,
        th_seg, u_seg,   m2_seg])
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
    print("MǢGÞUM RECONSTRUCTION v1")
    print("Old English [mæːɣθum]")
    print("Beowulf line 6, word 2")
    print()

    w_dry = synth_maegthum(
        pitch_hz=145.0, dil=1.0,
        add_room=False)
    write_wav(
        "output_play/maegthum_dry.wav",
        w_dry, SR)
    print(f"  maegthum_dry.wav"
          f"  ({len(w_dry)/SR*1000:.0f} ms)")

    w_hall = synth_maegthum(
        pitch_hz=145.0, dil=1.0,
        add_room=True)
    write_wav(
        "output_play/maegthum_hall.wav",
        w_hall, SR)
    print("  maegthum_hall.wav")

    w_slow = ola_stretch(w_dry, 4.0)
    write_wav(
        "output_play/maegthum_slow.wav",
        w_slow, SR)
    print("  maegthum_slow.wav")

    # [ɣ] isolated
    gh_seg = synth_GH(AEL_F, None,
                       145.0, 1.0, SR)
    write_wav(
        "output_play/maegthum_gh_only.wav",
        ola_stretch(gh_seg / (
            np.max(np.abs(gh_seg))+1e-8)
            * 0.75, 4.0), SR)
    print("  maegthum_gh_only.wav  (4x slow)")

    # [æː] isolated
    ael_seg = synth_AEL(M_F, GH_F,
                         145.0, 1.0, SR)
    write_wav(
        "output_play/maegthum_ael_only.wav",
        ola_stretch(ael_seg / (
            np.max(np.abs(ael_seg))+1e-8)
            * 0.75, 4.0), SR)
    print("  maegthum_ael_only.wav  (4x slow)")
    print()
    print("  afplay output_play/"
          "maegthum_ael_only.wav")
    print("  afplay output_play/"
          "maegthum_gh_only.wav")
    print("  afplay output_play/"
          "maegthum_dry.wav")
    print("  afplay output_play/"
          "maegthum_slow.wav")
    print()
    print("  Line 6 in progress:")
    print("  mongum mǣgþum"
          " meodosetla ofteah")
    print()
