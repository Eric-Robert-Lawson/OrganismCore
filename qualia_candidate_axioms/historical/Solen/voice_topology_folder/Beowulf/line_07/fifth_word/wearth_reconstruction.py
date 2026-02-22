"""
WEARÐ RECONSTRUCTION
Old English: wearð
Meaning: became, came to be
IPA: [weɑrθ]
Beowulf: Line 7, word 5 (overall word 30)
February 2026

PHONEME STRUCTURE:
  W   [w]    voiced labio-velar approximant — verified WĒ
  EA  [eɑ]   short front-back diphthong     — verified SCEAÞENA
  R   [r]    alveolar trill                 — verified GĀR-DENA
  TH  [θ]    voiceless dental fricative     — verified ÞĒOD-CYNINGA

NEW PHONEMES: none.
Pure assembly. Four phonemes. All verified.

NOTES:
  [r] trill depth: using R_TRILL_DEPTH 0.40
    from the outset — v2 verified value
    from ǢREST. Post-diphthong context
    here ([eɑ]→[r]) vs post-long-vowel
    in ǢREST ([æː]→[r]).
    Cautious — 0.40 known good.

  [eɑ]→[r]: diphthong into trill.
    [eɑ] offset F1 ~700, F2 ~1100 Hz.
    [r] F1 ~300, F2 ~900 Hz.
    Transition: F1 falls, F2 stable-ish.

  [r]→[θ]: trill into voiceless dental.
    Voiced → voiceless.
    [r] envelope decays into silence,
    [θ] noise onset.
    No place overlap — alveolar to dental.
    Small place change, large voicing change.

  [θ] word-final — same as PÆÞ.
    Known limitation: centroid sits high.
    Passes diagnostics. Noted.

CONTEXT:
  syþðan ǣrest wearð —
  since first it came to be.
  The verb that closes line 7.
  The becoming at the origin of time.

  wearð closes the alliterative unit:
  syþðan ǢREST WEARÐ —
  ǣ- and w- do not alliterate.
  The alliteration in this half-line
  is on the stressed syllables:
  ǣrest / wearð — not a standard
  alliterative pair. The alliteration
  in line 7 is egsode / ǣrest
  (both vowel-initial — OE vowels
  alliterate with each other).
  wearð is the metrically weak close.

CHANGE LOG:
  v1 — initial parameters
       R_TRILL_DEPTH 0.40 from the outset
"""

import numpy as np
from scipy.signal import lfilter, butter
import wave as wave_module
import os

SR    = 44100
DTYPE = np.float32

os.makedirs("output_play", exist_ok=True)


# ============================================================
# PARAMETERS — all from verified inventory
# ============================================================

# W — voiced labio-velar approximant [w]
W_F      = [300.0,  700.0, 2200.0, 3000.0]
W_B      = [100.0,  150.0,  250.0,  300.0]
W_GAINS  = [ 14.0,    6.0,    1.5,    0.4]
W_DUR_MS     = 55.0
W_COART_ON   = 0.15
W_COART_OFF  = 0.15

# EA — short front-back diphthong [eɑ]
EA_DUR_MS    = 80.0
EA_F_ON      = [450.0, 1900.0, 2600.0, 3300.0]
EA_F_OFF     = [700.0, 1100.0, 2400.0, 3000.0]
EA_B         = [100.0,  130.0,  200.0,  280.0]
EA_GAINS     = [ 16.0,    8.0,    1.5,    0.5]
EA_TRANS_ON  = 0.25
EA_TRANS_OFF = 0.85

# R — alveolar trill [r]
# R_TRILL_DEPTH 0.40 — v2 verified value
# from ǢREST. Using from the outset.
R_F           = [300.0,  900.0, 2000.0, 3200.0]
R_B           = [100.0,  150.0,  250.0,  300.0]
R_GAINS       = [ 14.0,    7.0,    2.0,    0.5]
R_DUR_MS      = 65.0
R_TRILL_RATE  = 28.0
R_TRILL_DEPTH = 0.40

# TH — voiceless dental fricative [θ]
TH_DUR_MS   = 70.0
TH_NOISE_CF = 5000.0
TH_NOISE_BW = 3000.0
TH_GAIN     = 0.18

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

def synth_W(F_prev=None, F_next=None,
             pitch_hz=PITCH_HZ,
             dil=DIL, sr=SR):
    """Voiced labio-velar approximant [w].
    Verified WĒ."""
    dur_ms = W_DUR_MS * dil
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
            1.0, 0.7, n_rel)
    src    = f32(src * env)
    n_on   = int(W_COART_ON  * n_s)
    n_off  = int(W_COART_OFF * n_s)
    f_prev = F_prev if F_prev is not None \
             else W_F
    f_next = F_next if F_next is not None \
             else W_F
    result = np.zeros(n_s, dtype=DTYPE)
    for fi in range(len(W_F)):
        f_s   = (float(f_prev[fi])
                 if fi < len(f_prev)
                 else float(W_F[fi]))
        f_e   = (float(f_next[fi])
                 if fi < len(f_next)
                 else float(W_F[fi]))
        f_b   = float(W_F[fi])
        f_arr = np.full(n_s, f_b, dtype=DTYPE)
        if n_on > 0:
            f_arr[:n_on] = np.linspace(
                f_s, f_b, n_on)
        if n_off > 0:
            f_arr[-n_off:] = np.linspace(
                f_b, f_e, n_off)
        bw  = float(W_B[fi])
        g   = float(W_GAINS[fi])
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
        result = f32(result / mx * 0.62)
    return f32(result)


def synth_EA(F_prev=None, F_next=None,
              pitch_hz=PITCH_HZ,
              dil=DIL, sr=SR):
    """Short front-back diphthong [eɑ].
    Verified SCEAÞENA."""
    dur_ms = EA_DUR_MS * dil
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


def synth_R(F_prev=None, F_next=None,
             pitch_hz=PITCH_HZ,
             dil=DIL, sr=SR):
    """Alveolar trill [r].
    R_TRILL_DEPTH 0.40 — v2 verified value."""
    dur_ms = R_DUR_MS * dil
    n_s    = max(4, int(dur_ms / 1000.0 * sr))
    T      = 1.0 / sr
    src    = rosenberg_pulse(n_s, pitch_hz,
                              oq=0.65, sr=sr)
    t_arr  = np.arange(n_s) * T
    am     = (1.0 - R_TRILL_DEPTH
              + R_TRILL_DEPTH
              * np.sin(2 * np.pi
                       * R_TRILL_RATE
                       * t_arr))
    src    = f32(src * am.astype(DTYPE))
    n_tr   = min(int(0.015 * sr), n_s // 4)
    env    = np.ones(n_s, dtype=DTYPE)
    if n_tr < n_s:
        env[:n_tr]  = np.linspace(
            0.3, 1.0, n_tr)
        env[-n_tr:] = np.linspace(
            1.0, 0.3, n_tr)
    src    = f32(src * env)
    result = apply_formants(
        src, R_F, R_B, R_GAINS, sr=sr)
    mx     = np.max(np.abs(result))
    if mx > 1e-8:
        result = f32(result / mx * 0.60)
    return f32(result)


def synth_TH(F_prev=None, F_next=None,
              dil=DIL, sr=SR):
    """Voiceless dental fricative [θ].
    Verified ÞĒOD-CYNINGA."""
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

def synth_wearth(pitch_hz=PITCH_HZ,
                  dil=DIL,
                  add_room=False,
                  sr=SR):
    """[w·eɑ·r·θ]"""
    w_seg  = synth_W(
        F_prev=None, F_next=EA_F_ON,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    ea_seg = synth_EA(
        F_prev=W_F, F_next=R_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    r_seg  = synth_R(
        F_prev=EA_F_OFF, F_next=None,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    th_seg = synth_TH(
        F_prev=R_F, F_next=None,
        dil=dil, sr=sr)
    word   = np.concatenate([
        w_seg, ea_seg, r_seg, th_seg])
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
    print("WEARÐ RECONSTRUCTION v1")
    print("Old English [weɑrθ]")
    print("Beowulf line 7, word 5")
    print("Zero new phonemes — pure assembly")
    print()

    w_dry = synth_wearth(
        pitch_hz=145.0, dil=1.0,
        add_room=False)
    write_wav(
        "output_play/wearth_dry.wav",
        w_dry, SR)
    print(f"  wearth_dry.wav"
          f"  ({len(w_dry)/SR*1000:.0f} ms)")

    w_hall = synth_wearth(
        pitch_hz=145.0, dil=1.0,
        add_room=True)
    write_wav(
        "output_play/wearth_hall.wav",
        w_hall, SR)
    print("  wearth_hall.wav")

    w_slow = ola_stretch(w_dry, 4.0)
    write_wav(
        "output_play/wearth_slow.wav",
        w_slow, SR)
    print("  wearth_slow.wav")

    w_perf = synth_wearth(
        pitch_hz=PITCH_PERF,
        dil=DIL_PERF,
        add_room=True)
    write_wav(
        "output_play/wearth_perf.wav",
        w_perf, SR)
    print(f"  wearth_perf.wav"
          f"  ({len(w_perf)/SR*1000:.0f} ms)"
          f"  [110 Hz, dil 2.5, hall]")
    print()
    print("  afplay output_play/wearth_dry.wav")
    print("  afplay output_play/wearth_slow.wav")
    print("  afplay output_play/wearth_hall.wav")
    print("  afplay output_play/wearth_perf.wav")
    print()
    print("  Line 7 complete after verification:")
    print("  egsode ✓ eorlas ✓ syþðan ✓"
          " ǣrest ✓ wearð —")
    print()
