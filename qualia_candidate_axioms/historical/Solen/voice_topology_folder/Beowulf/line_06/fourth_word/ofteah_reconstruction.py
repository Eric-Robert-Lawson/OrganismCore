"""
OFTEAH RECONSTRUCTION
Old English: ofteah
Meaning: deprived, took away (past tense)
IPA: [ofteɑx]
Beowulf: Line 6, Word 4 (overall word 25)
Line 6 final word.
February 2026

PHONEME STRUCTURE:
  O   [o]    short close-mid back        — verified ÞĒOD-CYNINGA
  F   [f]    voiceless labiodental fric. — verified GEFRŪNON
  T   [t]    voiceless alveolar stop     — verified HWÆT
  EA  [eɑ]   short front-back diphthong — verified SCEAÞENA
  H   [x]    voiceless velar fricative   — verified HU

NEW PHONEMES: none.
Pure assembly. Line 6 final word.

NOTE ON [ft] CLUSTER:
  [f]→[t] — voiceless labiodental
  fricative into voiceless alveolar
  stop. Both voiceless. Clean
  transition — no voicing change.
  The [f] offset feeds directly
  into [t] closure with no VOT gap.

NOTE ON [eɑx] SEQUENCE:
  Diphthong into voiceless velar
  fricative. The [eɑ] offset is
  back [ɑ] — the tongue is already
  near velar position. The [x]
  onset follows naturally from the
  back vowel configuration.
  The sequence [ɑx] is acoustically
  coherent — back vowel into back
  fricative.

ETYMOLOGY:
  of- + tēon (to draw, pull)
  ModE 'tow' from same root.
  Scyld drew the mead-benches
  away from enemy warriors.
  Past tense: ofteah.

LINE 6 COMPLETE after this word:
  mongum mǣgþum meodosetla ofteah
  [to] many tribes mead-benches
  deprived

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

# O — short close-mid back rounded [o]
O_F      = [450.0,  800.0, 2500.0, 3200.0]
O_B      = [100.0,  120.0,  200.0,  280.0]
O_GAINS  = [ 16.0,    8.0,    1.5,    0.5]
O_DUR_MS = 55.0
O_COART_ON  = 0.12
O_COART_OFF = 0.12

# F — voiceless labiodental fricative [f]
F_DUR_MS   = 70.0
F_NOISE_CF = 7000.0
F_NOISE_BW = 5000.0
F_GAIN     = 0.28

# T — voiceless alveolar stop [t]
T_DUR_MS   = 60.0
T_BURST_F  = 4000.0
T_BURST_BW = 2000.0
T_BURST_MS = 12.0
T_ASP_MS   = 25.0
T_ASP_CF   = 4500.0
T_ASP_BW   = 3000.0

# EA — short front-back diphthong [eɑ]
EA_DUR_MS  = 80.0
EA_F_ON    = [450.0, 1900.0, 2600.0, 3300.0]
EA_F_OFF   = [700.0, 1100.0, 2400.0, 3000.0]
EA_B       = [100.0,  130.0,  200.0,  280.0]
EA_GAINS   = [ 16.0,    8.0,    1.5,    0.5]
EA_TRANS_ON  = 0.30
EA_TRANS_OFF = 0.90

# X — voiceless velar fricative [x]
X_DUR_MS   = 75.0
X_NOISE_CF = 3000.0
X_NOISE_BW = 2500.0
X_GAIN     = 0.22
X_SEC_CF   = 6000.0
X_SEC_BW   = 2000.0
X_SEC_GAIN = 0.08

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


def synth_F(F_prev=None, F_next=None,
             dil=DIL, sr=SR):
    dur_ms = F_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    noise  = np.random.randn(n_s).astype(float)
    lo_    = max(F_NOISE_CF - F_NOISE_BW/2,
                 200.0)
    hi_    = min(F_NOISE_CF + F_NOISE_BW/2,
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
            1.0, 0.5, n_dec)
    fric   = f32(fric * env * F_GAIN)
    mx     = np.max(np.abs(fric))
    if mx > 1e-8:
        fric = f32(fric / mx * 0.40)
    return f32(fric)


def synth_T(F_prev=None, F_next=None,
             dil=DIL, sr=SR):
    dur_ms  = T_DUR_MS * dil
    n_s     = max(4, int(dur_ms / 1000.0 * sr))
    n_burst = max(2, int(T_BURST_MS
                         / 1000.0 * sr))
    n_asp   = max(2, int(T_ASP_MS
                         / 1000.0 * sr))
    n_clos  = max(2, n_s - n_burst - n_asp)
    closure = np.zeros(n_clos, dtype=DTYPE)
    noise_b = np.random.randn(
        n_burst).astype(float)
    b_bp, a_bp = safe_bp(
        T_BURST_F - T_BURST_BW / 2,
        T_BURST_F + T_BURST_BW / 2, SR)
    burst   = f32(lfilter(b_bp, a_bp,
                           noise_b) * 0.70)
    env_b   = np.linspace(
        1.0, 0.3, n_burst).astype(DTYPE)
    burst   = f32(burst * env_b)
    noise_a = np.random.randn(
        n_asp).astype(float)
    b_ap, a_ap = safe_bp(
        T_ASP_CF - T_ASP_BW / 2,
        T_ASP_CF + T_ASP_BW / 2, SR)
    asp     = f32(lfilter(b_ap, a_ap,
                           noise_a) * 0.35)
    env_a   = np.linspace(
        0.6, 0.0, n_asp).astype(DTYPE)
    asp     = f32(asp * env_a)
    seg     = np.concatenate([
        closure, burst, asp])
    mx      = np.max(np.abs(seg))
    if mx > 1e-8:
        seg = f32(seg / mx * 0.65)
    return f32(seg)


def synth_EA(F_prev=None, F_next=None,
              pitch_hz=PITCH_HZ,
              dil=DIL, sr=SR):
    dur_ms = EA_DUR_MS * dil
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
    i_ton  = int(EA_TRANS_ON  * n_s)
    i_toff = int(EA_TRANS_OFF * n_s)
    n_trans= max(1, i_toff - i_ton)
    result = np.zeros(n_s, dtype=DTYPE)
    for fi in range(len(EA_F_ON)):
        f_on  = float(EA_F_ON[fi])
        f_off = float(EA_F_OFF[fi])
        bw    = float(EA_B[fi])
        g     = float(EA_GAINS[fi])
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


def synth_X(F_prev=None, F_next=None,
             dil=DIL, sr=SR):
    """
    Voiceless velar fricative [x].
    Word-final position here.
    Same parameters as HU instance.
    Decay to silence at end.
    Post-diphthong — follows [ɑ]
    offset of [eɑ]. The back vowel
    configuration of [ɑ] transitions
    naturally into the velar
    constriction of [x].
    """
    dur_ms = X_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    noise  = np.random.randn(n_s).astype(float)
    lo1    = max(X_NOISE_CF - X_NOISE_BW/2,
                 200.0)
    hi1    = min(X_NOISE_CF + X_NOISE_BW/2,
                 sr * 0.48)
    b1, a1 = safe_bp(lo1, hi1, sr)
    fric1  = lfilter(b1, a1, noise)
    lo2    = max(X_SEC_CF - X_SEC_BW/2,
                 200.0)
    hi2    = min(X_SEC_CF + X_SEC_BW/2,
                 sr * 0.48)
    b2, a2 = safe_bp(lo2, hi2, sr)
    fric2  = lfilter(b2, a2, noise)
    fric   = (fric1 * X_GAIN
              + fric2 * X_SEC_GAIN)
    n_atk  = min(int(0.010 * sr), n_s // 4)
    n_dec  = min(int(0.025 * sr), n_s // 4)
    env    = np.ones(n_s, dtype=float)
    if n_atk < n_s:
        env[:n_atk] = np.linspace(
            0.0, 1.0, n_atk)
    if n_dec < n_s:
        env[-n_dec:] = np.linspace(
            1.0, 0.0, n_dec)
    fric   = f32(fric * env)
    mx     = np.max(np.abs(fric))
    if mx > 1e-8:
        fric = f32(fric / mx * 0.42)
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

def synth_ofteah(pitch_hz=PITCH_HZ,
                  dil=DIL,
                  add_room=False,
                  sr=SR):
    """[o·f·t·eɑ·x]"""
    o_seg  = synth_O(
        F_prev=None, F_next=None,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    f_seg  = synth_F(
        F_prev=O_F, F_next=None,
        dil=dil, sr=sr)
    t_seg  = synth_T(
        F_prev=None, F_next=EA_F_ON,
        dil=dil, sr=sr)
    ea_seg = synth_EA(
        F_prev=None, F_next=None,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    x_seg  = synth_X(
        F_prev=EA_F_OFF, F_next=None,
        dil=dil, sr=sr)
    word   = np.concatenate([
        o_seg, f_seg, t_seg,
        ea_seg, x_seg])
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
    print("OFTEAH RECONSTRUCTION v1")
    print("Old English [ofteɑx]")
    print("Beowulf line 6, word 4")
    print("Line 6 final word.")
    print()

    w_dry = synth_ofteah(
        pitch_hz=145.0, dil=1.0,
        add_room=False)
    write_wav(
        "output_play/ofteah_dry.wav",
        w_dry, SR)
    print(f"  ofteah_dry.wav"
          f"  ({len(w_dry)/SR*1000:.0f} ms)")

    w_hall = synth_ofteah(
        pitch_hz=145.0, dil=1.0,
        add_room=True)
    write_wav(
        "output_play/ofteah_hall.wav",
        w_hall, SR)
    print("  ofteah_hall.wav")

    w_slow = ola_stretch(w_dry, 4.0)
    write_wav(
        "output_play/ofteah_slow.wav",
        w_slow, SR)
    print("  ofteah_slow.wav")

    w_perf = synth_ofteah(
        pitch_hz=110.0, dil=2.5,
        add_room=True)
    write_wav(
        "output_play/ofteah_performance.wav",
        w_perf, SR)
    print(f"  ofteah_performance.wav"
          f"  ({len(w_perf)/SR*1000:.0f} ms)")

    print()
    print("  afplay output_play/"
          "ofteah_dry.wav")
    print("  afplay output_play/"
          "ofteah_slow.wav")
    print("  afplay output_play/"
          "ofteah_hall.wav")
    print()
    print("  LINE 6 COMPLETE:")
    print("  mongum mǣgþum"
          " meodosetla ofteah")
    print()
