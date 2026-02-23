"""
GEBĀD RECONSTRUCTION
Old English: gebād
Meaning: waited, experienced (past tense of gebīdan)
IPA: [gəbaːd]
Beowulf: Line 8, word 6 (overall word 36)
February 2026

PHONEME STRUCTURE:
  G     [g]   voiced velar stop              — verified
  SCHWA [ə]   mid central vowel              — verified (phoneme 40)
  B     [b]   voiced bilabial stop           — NEW PHONEME 41
  AY    [aː]  long open back unrounded       — [ɑ] at long duration
  D     [d]   voiced alveolar stop           — verified

NEW PHONEME: [b] — voiced bilabial stop — phoneme 41
  The last phoneme in the OE inventory.
  The inventory closes at this word.

SYLLABLE STRUCTURE:
  Syllable 1: [gə]   — unstressed — ge- prefix
  Syllable 2: [baːd] — stressed   — heavy

[b] — VOICED BILABIAL STOP — PHONEME 41:
  Three-phase architecture:
    Phase 1: closure   — lips sealed
                         Rosenberg pulse
                         low-pass filtered at 800 Hz
                         murmur gain 0.85
    Phase 2: burst     — bilabial release
                         band-filtered noise ~1000 Hz
                         (bilabial locus — lowest stop)
    Phase 3: VOT       — voiced onset
                         gain <= 0.10
  v2 changes from v1:
    LP cutoff raised: 500 Hz → 800 Hz
    Murmur gain raised: 0.65 → 0.85
    Both changes address murmur voicing
    detection in autocorrelation measure.

[aː] — LONG OPEN BACK UNROUNDED:
  Same formant targets as verified [ɑ]:
    F1 700, F2 1100, F3 2500, F4 3200
  Duration: 110 ms (long — 2× short)
  No change from v1.
  Diagnostic band fix in v2 diagnostic.

CHANGE LOG:
  v1 — initial parameters
       [b] murmur voicing FAIL (0.2456 < 0.60)
       [aː] F2 centroid FAIL (822 < 900 Hz)
  v2 — [b] LP cutoff 500→800 Hz, murmur gain 0.65→0.85
       [aː] diagnostic band fix (in diagnostic file)
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

# G — voiced velar stop [g]
G_DUR_MS      = 60.0
G_CLOSURE_MS  = 35.0
G_BURST_F     = 2500.0
G_BURST_BW    = 1200.0
G_BURST_MS    = 8.0
G_VOT_MS      = 5.0
G_BURST_GAIN  = 0.35
G_VOT_GAIN    = 0.08
G_VOICING_MS  = 20.0

# SCHWA — mid central vowel [ə] — phoneme 40
SCHWA_F     = [500.0, 1500.0, 2500.0, 3200.0]
SCHWA_B     = [150.0,  200.0,  280.0,  320.0]
SCHWA_GAINS = [ 14.0,    7.0,    1.5,    0.4]
SCHWA_DUR_MS    = 45.0
SCHWA_COART_ON  = 0.15
SCHWA_COART_OFF = 0.15

# B — voiced bilabial stop [b] — NEW PHONEME 41
# v2: LP cutoff raised 500→800 Hz
#     murmur gain raised 0.65→0.85
B_DUR_MS       = 65.0
B_CLOSURE_MS   = 35.0
B_BURST_F      = 1000.0
B_BURST_BW     = 800.0
B_BURST_MS     = 8.0
B_VOT_MS       = 5.0
B_BURST_GAIN   = 0.35
B_VOT_GAIN     = 0.08
B_VOICING_MS   = 20.0
B_MURMUR_GAIN  = 0.85    # v2: raised from 0.65
B_LP_CUTOFF_HZ = 800.0   # v2: raised from 500 Hz

# AY — long open back unrounded [aː]
AY_F     = [700.0, 1100.0, 2500.0, 3200.0]
AY_B     = [120.0,  150.0,  200.0,  280.0]
AY_GAINS = [ 16.0,    8.0,    1.5,    0.5]
AY_DUR_MS    = 110.0
AY_COART_ON  = 0.10
AY_COART_OFF = 0.10

# D — voiced alveolar stop [d]
D_DUR_MS      = 60.0
D_CLOSURE_MS  = 35.0
D_BURST_F     = 3500.0
D_BURST_BW    = 1500.0
D_BURST_MS    = 8.0
D_VOT_MS      = 5.0
D_BURST_GAIN  = 0.35
D_VOT_GAIN    = 0.10
D_VOICING_MS  = 20.0

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

def synth_G(F_next=None, pitch_hz=PITCH_HZ,
             dil=DIL, sr=SR):
    """Voiced velar stop [g]."""
    dur_ms     = G_DUR_MS * dil
    n_s        = max(4, int(dur_ms / 1000.0 * sr))
    n_closure  = max(2, int(G_CLOSURE_MS / 1000.0 * sr))
    n_burst    = max(2, int(G_BURST_MS   / 1000.0 * sr))
    n_vot      = max(2, int(G_VOT_MS     / 1000.0 * sr))
    n_voicing  = max(2, int(G_VOICING_MS / 1000.0 * sr))
    src_v      = rosenberg_pulse(n_voicing, pitch_hz,
                                  oq=0.65, sr=sr)
    env_v      = np.linspace(0.15, 0.0,
                              n_voicing).astype(DTYPE)
    voiced_cl  = apply_formants(
        f32(src_v * env_v),
        [250.0], [300.0], [4.0], sr=sr)
    silence    = np.zeros(
        max(0, n_closure - n_voicing), dtype=DTYPE)
    closure    = np.concatenate(
        [voiced_cl, silence])[:n_closure]
    noise_b    = np.random.randn(n_burst).astype(float)
    b_bp, a_bp = safe_bp(
        G_BURST_F - G_BURST_BW / 2,
        G_BURST_F + G_BURST_BW / 2, sr)
    burst      = f32(lfilter(b_bp, a_bp, noise_b)
                     * G_BURST_GAIN)
    env_bu     = np.linspace(1.0, 0.1,
                              n_burst).astype(DTYPE)
    burst      = f32(burst * env_bu)
    noise_v2   = np.random.randn(n_vot).astype(float)
    b_vp, a_vp = safe_bp(500.0, 6000.0, sr)
    vot        = f32(lfilter(b_vp, a_vp, noise_v2)
                     * G_VOT_GAIN)
    env_vo     = np.linspace(0.3, 0.0,
                              n_vot).astype(DTYPE)
    vot        = f32(vot * env_vo)
    seg        = np.concatenate([closure, burst, vot])
    n_pad      = max(0, n_s - len(seg))
    seg        = np.concatenate(
        [seg, np.zeros(n_pad, dtype=DTYPE)])
    seg        = f32(seg[:n_s])
    mx         = np.max(np.abs(seg))
    if mx > 1e-8:
        seg = f32(seg / mx * 0.50)
    return f32(seg)


def synth_SCHWA(F_prev=None, F_next=None,
                 pitch_hz=PITCH_HZ,
                 dil=DIL, sr=SR):
    """Mid central vowel [ə] — phoneme 40. Third appearance."""
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


def synth_B(F_next=None, pitch_hz=PITCH_HZ,
             dil=DIL, sr=SR):
    """
    Voiced bilabial stop [b] — PHONEME 41.
    v2: LP cutoff 800 Hz, murmur gain 0.85.
    Bilabial locus ~1000 Hz — lowest stop.
    """
    dur_ms     = B_DUR_MS * dil
    n_s        = max(4, int(dur_ms / 1000.0 * sr))
    n_closure  = max(2, int(B_CLOSURE_MS / 1000.0 * sr))
    n_burst    = max(2, int(B_BURST_MS   / 1000.0 * sr))
    n_vot      = max(2, int(B_VOT_MS     / 1000.0 * sr))
    n_voicing  = max(2, int(B_VOICING_MS / 1000.0 * sr))
    src_v      = rosenberg_pulse(n_voicing, pitch_hz,
                                  oq=0.65, sr=sr)
    env_v      = np.linspace(
        B_MURMUR_GAIN, 0.0,
        n_voicing).astype(DTYPE)
    # v2: LP cutoff raised to 800 Hz
    nyq        = sr / 2.0
    lp_        = min(B_LP_CUTOFF_HZ / nyq, 0.499)
    b_lp, a_lp = butter(2, lp_, btype='low')
    voiced_cl  = f32(lfilter(
        b_lp, a_lp,
        (src_v * env_v).astype(float)))
    silence    = np.zeros(
        max(0, n_closure - n_voicing), dtype=DTYPE)
    closure    = np.concatenate(
        [voiced_cl, silence])[:n_closure]
    noise_b    = np.random.randn(n_burst).astype(float)
    b_bp, a_bp = safe_bp(
        B_BURST_F - B_BURST_BW / 2,
        B_BURST_F + B_BURST_BW / 2, sr)
    burst      = f32(lfilter(b_bp, a_bp, noise_b)
                     * B_BURST_GAIN)
    env_bu     = np.linspace(1.0, 0.1,
                              n_burst).astype(DTYPE)
    burst      = f32(burst * env_bu)
    noise_v2   = np.random.randn(n_vot).astype(float)
    b_vp, a_vp = safe_bp(500.0, 6000.0, sr)
    vot        = f32(lfilter(b_vp, a_vp, noise_v2)
                     * B_VOT_GAIN)
    env_vo     = np.linspace(0.3, 0.0,
                              n_vot).astype(DTYPE)
    vot        = f32(vot * env_vo)
    seg        = np.concatenate([closure, burst, vot])
    n_pad      = max(0, n_s - len(seg))
    seg        = np.concatenate(
        [seg, np.zeros(n_pad, dtype=DTYPE)])
    seg        = f32(seg[:n_s])
    mx         = np.max(np.abs(seg))
    if mx > 1e-8:
        seg = f32(seg / mx * 0.50)
    return f32(seg)


def synth_AY(F_prev=None, F_next=None,
              pitch_hz=PITCH_HZ,
              dil=DIL, sr=SR):
    """Long open back unrounded [aː]. F1 700, F2 1100, dur 110 ms."""
    dur_ms = AY_DUR_MS * dil
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
    n_on   = int(AY_COART_ON  * n_s)
    n_off  = int(AY_COART_OFF * n_s)
    fp     = F_prev if F_prev is not None else AY_F
    fn     = F_next if F_next is not None else AY_F
    result = np.zeros(n_s, dtype=DTYPE)
    for fi in range(len(AY_F)):
        f_s   = float(fp[fi]) if fi < len(fp) \
                else float(AY_F[fi])
        f_e   = float(fn[fi]) if fi < len(fn) \
                else float(AY_F[fi])
        f_b   = float(AY_F[fi])
        f_arr = np.full(n_s, f_b, dtype=DTYPE)
        if n_on > 0:
            f_arr[:n_on]  = np.linspace(
                f_s, f_b, n_on)
        if n_off > 0:
            f_arr[-n_off:] = np.linspace(
                f_b, f_e, n_off)
        bw  = float(AY_B[fi])
        g   = float(AY_GAINS[fi])
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


def synth_D(F_prev=None, F_next=None,
             pitch_hz=PITCH_HZ,
             dil=DIL, sr=SR):
    """Voiced alveolar stop [d]."""
    dur_ms     = D_DUR_MS * dil
    n_s        = max(4, int(dur_ms / 1000.0 * sr))
    n_closure  = max(2, int(D_CLOSURE_MS / 1000.0 * sr))
    n_burst    = max(2, int(D_BURST_MS   / 1000.0 * sr))
    n_vot      = max(2, int(D_VOT_MS     / 1000.0 * sr))
    n_voicing  = max(2, int(D_VOICING_MS / 1000.0 * sr))
    src_v      = rosenberg_pulse(n_voicing, pitch_hz,
                                  oq=0.65, sr=sr)
    env_v      = np.linspace(0.15, 0.0,
                              n_voicing).astype(DTYPE)
    voiced_cl  = apply_formants(
        f32(src_v * env_v),
        [250.0], [300.0], [4.0], sr=sr)
    silence    = np.zeros(
        max(0, n_closure - n_voicing), dtype=DTYPE)
    closure    = np.concatenate(
        [voiced_cl, silence])[:n_closure]
    noise_b    = np.random.randn(n_burst).astype(float)
    b_bp, a_bp = safe_bp(
        D_BURST_F - D_BURST_BW / 2,
        D_BURST_F + D_BURST_BW / 2, sr)
    burst      = f32(lfilter(b_bp, a_bp, noise_b)
                     * D_BURST_GAIN)
    env_bu     = np.linspace(1.0, 0.1,
                              n_burst).astype(DTYPE)
    burst      = f32(burst * env_bu)
    noise_v2   = np.random.randn(n_vot).astype(float)
    b_vp, a_vp = safe_bp(500.0, 6000.0, sr)
    vot        = f32(lfilter(b_vp, a_vp, noise_v2)
                     * D_VOT_GAIN)
    env_vo     = np.linspace(0.3, 0.0,
                              n_vot).astype(DTYPE)
    vot        = f32(vot * env_vo)
    seg        = np.concatenate([closure, burst, vot])
    n_pad      = max(0, n_s - len(seg))
    seg        = np.concatenate(
        [seg, np.zeros(n_pad, dtype=DTYPE)])
    seg        = f32(seg[:n_s])
    mx         = np.max(np.abs(seg))
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
    rev = np.zeros(len(sig) + d3 + 1, dtype=float)
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

def synth_gebad(pitch_hz=PITCH_HZ,
                 dil=DIL,
                 add_room=False,
                 sr=SR):
    """[g · ə · b · aː · d]"""
    g_seg     = synth_G(
        F_next=SCHWA_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    schwa_seg = synth_SCHWA(
        F_prev=None, F_next=None,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    b_seg     = synth_B(
        F_next=AY_F,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    ay_seg    = synth_AY(
        F_prev=AY_F, F_next=None,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    d_seg     = synth_D(
        F_prev=AY_F, F_next=None,
        pitch_hz=pitch_hz, dil=dil, sr=sr)
    word      = np.concatenate([
        g_seg, schwa_seg, b_seg,
        ay_seg, d_seg])
    mx        = np.max(np.abs(word))
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
    print("GEBĀD RECONSTRUCTION v2")
    print("Old English [gəbaːd]")
    print("Beowulf line 8, word 6")
    print("NEW PHONEME: [b] — phoneme 41")
    print("v2: [b] LP cutoff 800 Hz,"
          " murmur gain 0.85")
    print()

    w_dry = synth_gebad(PITCH_HZ, DIL, False)
    write_wav("output_play/gebad_dry.wav", w_dry, SR)
    print(f"  gebad_dry.wav"
          f"  ({len(w_dry)/SR*1000:.0f} ms)")

    w_hall = synth_gebad(PITCH_HZ, DIL, True)
    write_wav("output_play/gebad_hall.wav", w_hall, SR)
    print("  gebad_hall.wav")

    w_slow = ola_stretch(w_dry, 4.0)
    write_wav("output_play/gebad_slow.wav", w_slow, SR)
    print("  gebad_slow.wav")

    w_perf = synth_gebad(PITCH_PERF, DIL_PERF, True)
    write_wav("output_play/gebad_perf.wav", w_perf, SR)
    print(f"  gebad_perf.wav"
          f"  ({len(w_perf)/SR*1000:.0f} ms)"
          f"  [110 Hz, dil 2.5, hall]")
    print()
    print("  afplay output_play/gebad_dry.wav")
    print("  afplay output_play/gebad_slow.wav")
    print("  afplay output_play/gebad_hall.wav")
    print("  afplay output_play/gebad_perf.wav")
    print()
    print("  hē þæs frōfre gebād —")
    print("  he of-that comfort waited.")
    print()
