"""
EGSODE RECONSTRUCTION
Old English: egsode
Meaning: terrified, intimidated (past tense)
IPA: [eɡsode]
Beowulf: Line 7, Word 1 (overall word 26)
February 2026

PHONEME STRUCTURE:
  E   [e]    short close-mid front      — verified GĀR-DENA
  G   [ɡ]    voiced velar stop          — verified GĀR-DENA
  S   [s]    voiceless alveolar fric.   — verified ÆÞELINGAS
  O   [o]    short close-mid back       — verified ÞĒOD-CYNINGA
  D   [d]    voiced alveolar stop       — verified GĀR-DENA
  E   [e]    short close-mid front      — verified GĀR-DENA

NEW PHONEMES: none.
Pure assembly.

v1 FAILURE:
  D4 [ɡs] transition failed.
  [ɡ] voicing 0.0008 — effectively zero.
  Burst + noise VOT dominated the
  autocorrelation window.
  Murmur too weak — not detected.

v2 FIX:
  Increased murmur gain 0.35 → 0.65.
  Increased murmur duration fraction.
  Reduced VOT noise gain 0.25 → 0.05.
  Extended closure fraction of total
  duration — more samples in murmur
  phase for autocorrelation to find.

CHANGE LOG:
  v1 — initial parameters — D4 FAIL
  v2 — murmur gain up, VOT noise down
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

# E — short close-mid front [e]
E_F      = [450.0, 1900.0, 2600.0, 3300.0]
E_B      = [100.0,  130.0,  200.0,  280.0]
E_GAINS  = [ 16.0,    8.0,    1.5,    0.5]
E_DUR_MS = 55.0
E_COART_ON  = 0.12
E_COART_OFF = 0.12

# G — voiced velar stop [ɡ]
# v2: murmur gain raised, VOT noise reduced
G_DUR_MS      = 70.0
G_BURST_F     = 1800.0
G_BURST_BW    = 800.0
G_BURST_MS    = 10.0
G_VOT_MS      = 5.0
G_MURMUR_GAIN = 0.65   # v1: 0.35 — too weak
G_VOT_GAIN    = 0.05   # v1: 0.25 — too loud

# S — voiceless alveolar fricative [s]
S_DUR_MS   = 65.0
S_NOISE_CF = 7500.0
S_NOISE_BW = 4000.0
S_GAIN     = 0.55

# O — short close-mid back rounded [o]
O_F      = [450.0,  800.0, 2500.0, 3200.0]
O_B      = [100.0,  120.0,  200.0,  280.0]
O_GAINS  = [ 16.0,    8.0,    1.5,    0.5]
O_DUR_MS = 55.0
O_COART_ON  = 0.12
O_COART_OFF = 0.12

# D — voiced alveolar stop [d]
D_DUR_MS   = 60.0
D_BURST_F  = 3500.0
D_BURST_BW = 1500.0
D_BURST_MS = 8.0
D_VOT_MS   = 5.0

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
# PHONEME SYNTHESIZERS
# ============================================================

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


def synth_G(F_prev=None, F_next=None,
             pitch_hz=PITCH_HZ,
             dil=DIL, sr=SR):
    """
    Voiced velar stop [ɡ] v2.
    v1 failure: murmur too weak,
    autocorrelation found noise not
    pitch. Murmur gain raised to 0.65,
    VOT noise reduced to 0.05.
    Closure fraction extended to ensure
    enough periodic samples for
    autocorrelation window.
    """
    dur_ms    = G_DUR_MS * dil
    n_s       = max(4, int(
        dur_ms / 1000.0 * sr))
    n_burst   = max(2, int(
        G_BURST_MS / 1000.0 * sr))
    n_vot     = max(2, int(
        G_VOT_MS   / 1000.0 * sr))
    n_closure = max(2,
                    n_s - n_burst - n_vot)
    T         = 1.0 / sr
    src_c  = rosenberg_pulse(
        n_closure, pitch_hz,
        oq=0.65, sr=sr)
    env_c  = np.linspace(
        0.8, 0.4, n_closure).astype(DTYPE)
    b_lp, a_lp = safe_lp(300.0, sr)
    murmur = f32(lfilter(
        b_lp, a_lp,
        src_c.astype(float))
                 * env_c * G_MURMUR_GAIN)
    noise  = np.random.randn(
        n_burst).astype(float)
    b_bp, a_bp = safe_bp(
        G_BURST_F - G_BURST_BW / 2,
        G_BURST_F + G_BURST_BW / 2, sr)
    burst  = f32(lfilter(
        b_bp, a_bp, noise) * 0.55)
    env_bu = np.linspace(
        1.0, 0.2, n_burst).astype(DTYPE)
    burst  = f32(burst * env_bu)
    noise_v = np.random.randn(
        n_vot).astype(float)
    b_vp, a_vp = safe_bp(
        3000.0, 8000.0, sr)
    vot    = f32(lfilter(
        b_vp, a_vp, noise_v)
                 * G_VOT_GAIN)
    env_vo = np.linspace(
        0.3, 0.0, n_vot).astype(DTYPE)
    vot    = f32(vot * env_vo)
    seg    = np.concatenate([
        murmur, burst, vot])
    mx     = np.max(np.abs(seg))
    if mx > 1e-8:
        seg = f32(seg / mx * 0.58)
    return f32(seg)


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


def synth_O(F_prev=None, F_next=None,
             pitch_hz=PITCH_HZ,
             dil=DIL, sr=SR):
    dur_ms = O_DUR_MS * dil
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
    n_on   = int(O_COART_ON  * n_s)
    n_off  = int(O_COART_OFF * n_s)
    f_prev = F_prev if F_prev is not None \
             else O_F
    f_next = F_next if F_next is not None \
             else O_F
    result = np.zeros(n_s, dtype=DTYPE)
    for fi in range(len(O_F)):
        f_s   = (float(f_prev[fi])
                 if fi < len(f_prev)
                 else float(O_F[fi]))
        f_e   = (float(f_next[fi])
                 if fi < len(f_next)
                 else float(O_F[fi]))
        f_b   = float(O_F[fi])
        f_arr = np.full(n_s, f_b, dtype=DTYPE)
        if n_on > 0:
            f_arr[:n_on] = np.linspace(
                f_s, f_b, n_on)
        if n_off > 0:
            f_arr[-n_off:] = np.linspace(
                f_b, f_e, n_off)
        bw  = float(O_B[fi])
        g   = float(O_GAINS[fi])
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


def synth_D(F_prev=None, F_next=None,
             pitch_hz=PITCH_HZ,
             dil=DIL, sr=SR):
    dur_ms    = D_DUR_MS * dil
    n_s       = max(4, int(
        dur_ms / 1000.0 * sr))
    n_burst   = max(2, int(
        D_BURST_MS / 1000.0 * sr))
    n_vot     = max(2, int(
        D_VOT_MS   / 1000.0 * sr))
    n_closure = max(2,
                    n_s - n_burst - n_vot)
    T         = 1.0 / sr
    src_c  = rosenberg_pulse(
        n_closure, pitch_hz,
        oq=0.65, sr=sr)
    env_c  = np.linspace(
        0.3, 0.1, n_closure).astype(DTYPE)
    b_lp, a_lp = safe_lp(300.0, sr)
    murmur = f32(lfilter(
        b_lp, a_lp,
        src_c.astype(float))
                 * env_c * 0.30)
    noise  = np.random.randn(
        n_burst).astype(float)
    b_bp, a_bp = safe_bp(
        D_BURST_F - D_BURST_BW / 2,
        D_BURST_F + D_BURST_BW / 2, sr)
    burst  = f32(lfilter(
        b_bp, a_bp, noise) * 0.55)
    env_bu = np.linspace(
        1.0, 0.2, n_burst).astype(DTYPE)
    burst  = f32(burst * env_bu)
    f_next = F_next if F_next is not None \
             else E_F
    src_v  = rosenberg_pulse(
        n_vot, pitch_hz, oq=0.65, sr=sr)
    vot    = apply_formants(
        src_v, f_next,
        [100.0, 130.0, 200.0, 280.0],
        [14.0,   7.0,   1.5,   0.5],
        sr=sr)
    vot    = f32(vot * 0.40)
    seg    = np.concatenate([
        murmur, burst, vot])
    mx     = np.max(np.abs(seg))
    if mx > 1e-8:
        seg = f32(seg / mx * 0.55)
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

def synth_egsode(pitch_hz=PITCH_HZ,
                  dil=DIL,
                  add_room=False,
                  sr=SR):
    """[e·ɡ·s·o·d·e]"""
    e1_seg = synth_E(
        F_prev=None, F_next=None,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    g_seg  = synth_G(
        F_prev=E_F, F_next=None,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    s_seg  = synth_S(
        F_prev=None, F_next=O_F,
        dil=dil, sr=sr)
    o_seg  = synth_O(
        F_prev=O_F, F_next=None,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    d_seg  = synth_D(
        F_prev=O_F, F_next=E_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    e2_seg = synth_E(
        F_prev=E_F, F_next=None,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    word   = np.concatenate([
        e1_seg, g_seg,  s_seg,
        o_seg,  d_seg,  e2_seg])
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
    print("EGSODE RECONSTRUCTION v2")
    print("Old English [eɡsode]")
    print("Beowulf line 7, word 1")
    print()

    w_dry = synth_egsode(
        pitch_hz=145.0, dil=1.0,
        add_room=False)
    write_wav(
        "output_play/egsode_dry.wav",
        w_dry, SR)
    print(f"  egsode_dry.wav"
          f"  ({len(w_dry)/SR*1000:.0f} ms)")

    w_hall = synth_egsode(
        pitch_hz=145.0, dil=1.0,
        add_room=True)
    write_wav(
        "output_play/egsode_hall.wav",
        w_hall, SR)
    print("  egsode_hall.wav")

    w_slow = ola_stretch(w_dry, 4.0)
    write_wav(
        "output_play/egsode_slow.wav",
        w_slow, SR)
    print("  egsode_slow.wav")

    print()
    print("  afplay output_play/"
          "egsode_dry.wav")
    print("  afplay output_play/"
          "egsode_slow.wav")
    print()
    print("  Line 7 in progress:")
    print("  egsode eorlas,"
          " syþðan ǣrest wearð")
    print()
