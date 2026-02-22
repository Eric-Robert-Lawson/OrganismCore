"""
HWÆT RECONSTRUCTION — v6
February 2026

[ʍæt] — Old English opening of Beowulf.

DIAGNOSIS FROM v5:

  D1 WARN 0.344. HW_B already [400,420,500,550].
  FIX L applied and confirmed. The residual
  autocorrelation is coming from the bandpass
  pre-filter low-frequency pass. safe_bp(100,6000)
  passes energy down to ~30 Hz. Noise bandlimited
  to 30 Hz has correlation time 1/(2×30) = 17ms =
  740 samples — inside search range 110–551.
  FIX O: raise pre-filter high-pass corner
  from 100 Hz → 500 Hz. No energy below 500 Hz
  in the noise source. Correlation time of noise
  bandlimited at 500 Hz = 1/(2×500) = 1ms = 44
  samples — below search range lo=110.

  Perceptual note on FIX O:
  Raising the noise floor to 500 Hz removes
  the very low rumble from the aspiration.
  The W-tract formants at F1=300 Hz will
  still shape the output because the resonator
  runs on the filtered noise — but the input
  noise itself no longer contains 300 Hz energy
  to excite the F1 resonator directly.
  This makes [ʍ] sound slightly less warm but
  more correctly breathy. The low-frequency
  energy in the output will come only from
  resonator amplification of noise near 500 Hz,
  which is acoustically correct for [h]-type
  aspiration.

  D2 FAIL — two distinct bugs:

  BUG 1: RMS = 1.147 > target max 1.0.
  synth_AE_ash() returns unnormalized output.
  AE_GAINS[0]=20 produces large amplitude.
  The RMS check in the diagnostic measured
  the raw output. The target [0.02, 1.0] was
  designed for post-normalized signals.
  FIX P: normalize synth_AE_ash() output
  to peak=0.75 before returning, matching
  what synth_hwat() does to the full word.
  The gains still control the RELATIVE
  balance between formants; the overall
  level is set by normalization.

  BUG 2: LPC returns None despite voicing=0.779.
  The voicing gate passed. But estimate_f1_f2
  hit the except clause in Levinson-Durbin.
  The autocorrelation values with raw RMS>1.0
  are on the order of n×RMS^2 = 7056 × 1.3 ≈
  9000. With order=14, the recursion involves
  differences of large numbers. The k_i values
  approach ±1, err approaches 0, and k_i^2
  produces NaN via the subtraction (1 - k_i^2)
  when k_i is computed from imprecise large
  numbers.
  FIX Q (in diagnostic): normalize the
  segment to unit peak BEFORE LPC estimation.
  This is done inside estimate_f1_f2() —
  add one line before pre-emphasis.
  LPC is scale-invariant by definition;
  normalizing the input does not change
  the formant frequencies.
"""

import numpy as np
from scipy.signal import lfilter, butter
import wave as wave_module
import os

SR    = 44100
DTYPE = np.float32

os.makedirs("output_play", exist_ok=True)


def f32(x):
    return np.asarray(x, dtype=DTYPE)

def calibrate(sig, target=0.08):
    mx = np.max(np.abs(sig))
    if mx > 1e-8:
        return f32(sig / mx * target)
    return f32(sig)

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
    nyq = sr / 2.0
    lo_ = max(lo / nyq, 0.001)
    hi_ = min(hi / nyq, 0.499)
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

def safe_hp(fc, sr=SR):
    nyq = sr / 2.0
    fc_ = max(min(fc / nyq, 0.499), 0.001)
    b, a = butter(2, fc_, btype='high')
    return b, a


# ============================================================
# RESONATOR
# ============================================================

def resonator(source, f_arr, bw, sr=SR):
    n_s = len(source)
    T   = 1.0 / sr
    out = np.zeros(n_s, dtype=DTYPE)
    y1 = y2 = 0.0
    f_is_array = hasattr(f_arr, '__len__')
    for i in range(n_s):
        fc  = max(20.0,
                  min(sr * 0.48,
                      float(f_arr[i])
                      if f_is_array
                      else float(f_arr)))
        bw_ = max(10.0, float(bw))
        a2  = -np.exp(-2 * np.pi * bw_ * T)
        a1  =  2 * np.exp(-np.pi * bw_ * T) * \
               np.cos(2 * np.pi * fc * T)
        b0  = 1.0 - a1 - a2
        y   = (b0 * float(source[i])
               + a1 * y1 + a2 * y2)
        y2  = y1
        y1  = y
        out[i] = y
    return f32(out)


# ============================================================
# PHONEME CONSTANTS
# ============================================================

# HW onset [ʍ] — voiceless labiovelar
HW_F = [300.0,  550.0, 2200.0, 3300.0]

# FIX L (v5, preserved): wide bandwidths.
# Ring time 35 samples < search lo 110.
HW_B = [400.0, 420.0, 500.0, 550.0]

HW_GAINS    = [4.0, 3.5, 0.8, 0.3]
HW_ASP_GAIN = 0.10

# FIX O: noise pre-filter raised 100→500 Hz.
# Correlation time of 500 Hz bandlimited noise
# = 1/(2×500) = 1ms = 44 samples.
# 44 < search lo 110 → no autocorrelation peak
# in voiced range.
HW_NOISE_LO = 500.0   # was 100.0
HW_NOISE_HI = 6000.0

# Æ vowel [æ] — low front unrounded
AE_F = [780.0, 1850.0, 2700.0, 3500.0]

# FIX N (v5, preserved): BW widened 110→140
AE_B = [140.0, 90.0, 160.0, 220.0]

# FIX raised gain for F1 dominance
# (overall level controlled by normalization
#  in FIX P — gain only sets relative balance)
AE_GAINS = [20.0, 4.0, 1.2, 0.4]

# Coarticulation fractions
AE_COART_ON  = 0.12
AE_COART_OFF = 0.10

# T locus [t] — alveolar
T_LOCUS_F = [300.0, 1800.0, 2600.0, 3500.0]
T_LOCUS_B = [200.0,  200.0,  280.0,  380.0]

T_TRANS_MS   = 18.0
T_CLOSURE_MS = 35.0
T_BURST_MS   =  6.0
T_VOT_MS     = 25.0


# ============================================================
# HW ONSET [ʍ]
# ============================================================

def synth_HW(F_next=None,
              dur_ms=80.0,
              sr=SR):
    """
    [ʍ] voiceless labiovelar fricative.

    FIX O: noise pre-filter high-pass
    corner raised from 100 Hz to 500 Hz.

    With corner at 100 Hz, noise has
    energy down to ~30 Hz (2nd-order
    Butterworth rolloff). This low-freq
    content autocorrelates at lags up to
    740 samples — inside voiced search
    range 110–551 — and scores as 0.34.

    With corner at 500 Hz, minimum noise
    energy is ~250 Hz. Correlation time
    = 1/(2×500) = 44 samples < 110.
    Autocorrelation cannot find a peak
    in voiced range.

    Perceptual effect: slightly less warm
    aspiration, more correctly breathy.
    The W-tract resonators still shape
    the output at their center frequencies.
    """
    dur_ms = max(dur_ms, 80.0)
    n_s    = max(4, int(dur_ms / 1000.0 * sr))

    noise = f32(np.random.normal(0, 1, n_s))
    try:
        # FIX O: 500 Hz high-pass corner
        b, a  = safe_bp(HW_NOISE_LO,
                         HW_NOISE_HI, sr)
        noise = f32(lfilter(b, a, noise))
        b, a  = safe_lp(4000.0, sr)
        noise = f32(lfilter(b, a, noise))
    except Exception:
        pass
    noise = calibrate(noise, target=HW_ASP_GAIN)

    F_end    = (list(F_next)
                if F_next is not None
                else list(HW_F))
    n_stable = int(n_s * 0.75)
    n_glide  = n_s - n_stable

    result = np.zeros(n_s, dtype=DTYPE)
    for fi in range(4):
        f_arr = np.zeros(n_s, dtype=DTYPE)
        f_arr[:n_stable] = float(HW_F[fi])
        if n_glide > 0:
            f_arr[n_stable:] = np.linspace(
                float(HW_F[fi]),
                float(F_end[fi]),
                n_glide, dtype=DTYPE)
        out    = resonator(noise, f_arr,
                            HW_B[fi], sr=sr)
        result += out * HW_GAINS[fi]

    n_atk = min(int(0.030 * sr), n_s // 3)
    n_rel = min(int(0.020 * sr), n_s // 4)
    env   = np.ones(n_s, dtype=DTYPE)
    if n_atk > 0:
        env[:n_atk] = np.linspace(
            0.0, 1.0, n_atk)
    if n_rel > 0:
        env[-n_rel:] = np.linspace(
            1.0, 0.0, n_rel)
    result *= env

    return f32(result)


# ============================================================
# Æ VOWEL [æ]
# ============================================================

def synth_AE_ash(F_prev=None,
                  F_next=None,
                  dur_ms=160.0,
                  pitch_hz=145.0,
                  sr=SR):
    """
    [æ] Old English ash vowel.

    FIX P: output normalized to peak=0.75
    before returning. This makes the
    isolated phoneme behave like the
    normalized full-word output.
    The formant gains (AE_GAINS) control
    relative spectral balance only.
    Overall amplitude is set here.

    FIX M (v5, preserved): envelope onset
    ramp = int(AE_COART_ON × n_s) so body
    zone starts at exactly full amplitude.

    FIX N (v5, preserved): AE_B[0]=140 Hz,
    AE_GAINS[0]=20.

    FIX A (v3, preserved): calibrate()
    after envelope.
    """
    n_s = max(4, int(dur_ms / 1000.0 * sr))
    T   = 1.0 / sr

    # Rosenberg pulse
    phase = 0.0; oq = 0.65
    src   = np.zeros(n_s, dtype=DTYPE)
    for i in range(n_s):
        phase += pitch_hz * T
        if phase >= 1.0:
            phase -= 1.0
        src[i] = ((phase / oq) * (2 - phase / oq)
                  if phase < oq
                  else 1 - (phase - oq) / (
                      1 - oq + 1e-9))
    src = f32(np.diff(src, prepend=src[0]))

    # Reduced breathiness
    breath = f32(np.random.normal(0, 0.006, n_s))
    try:
        b, a   = safe_bp(400.0, 2200.0, sr)
        breath = f32(lfilter(b, a, breath))
    except Exception:
        pass
    src = f32(src + breath)

    # FIX M: ramp length matches coart onset
    n_atk = min(int(AE_COART_ON * n_s),
                n_s // 4)
    n_rel = min(int(AE_COART_OFF * n_s),
                n_s // 4)
    env   = np.ones(n_s, dtype=DTYPE)
    if n_atk > 0:
        env[:n_atk] = np.linspace(
            0.0, 1.0, n_atk)
    if n_rel > 0:
        env[-n_rel:] = np.linspace(
            1.0, 0.0, n_rel)
    src *= env

    # Calibrate AFTER envelope (FIX A)
    src = calibrate(src, target=0.08)

    # Coarticulation formant arrays
    F_s = (list(F_prev) if F_prev is not None
           else list(AE_F))
    F_e = (list(F_next) if F_next is not None
           else list(AE_F))

    n_on  = min(int(AE_COART_ON  * n_s),
                n_s // 4)
    n_off = min(int(AE_COART_OFF * n_s),
                n_s // 4)
    n_mid = n_s - n_on - n_off
    if n_mid < 1:
        n_mid = 1
        n_on  = (n_s - 1) // 2
        n_off = n_s - 1 - n_on

    result = np.zeros(n_s, dtype=DTYPE)
    for fi in range(4):
        f_arr = np.zeros(n_s, dtype=DTYPE)
        if n_on > 0:
            f_arr[:n_on] = np.linspace(
                float(F_s[fi]),
                float(AE_F[fi]),
                n_on, dtype=DTYPE)
        if n_mid > 0:
            f_arr[n_on:n_on + n_mid] = \
                float(AE_F[fi])
        if n_off > 0:
            f_arr[n_on + n_mid:] = np.linspace(
                float(AE_F[fi]),
                float(F_e[fi]),
                n_off, dtype=DTYPE)
        out    = resonator(src, f_arr,
                            AE_B[fi], sr=sr)
        result += out * AE_GAINS[fi]

    # FIX P: normalize before returning
    mx = np.max(np.abs(result))
    if mx > 1e-8:
        result = f32(result / mx * 0.75)

    return f32(result)


# ============================================================
# T CODA [t]
# ============================================================

def synth_T_coda(F_prev=None,
                  dur_ms=90.0,
                  sr=SR):
    """
    [t] alveolar stop coda.
    Returns (signal, boundaries).
    """
    T_   = 1.0 / sr
    n_trans = min(
        int(T_TRANS_MS   / 1000.0 * sr),
        max(4, int(dur_ms / 1000.0 * sr) // 5))
    n_clos  = max(4,
                  int(T_CLOSURE_MS / 1000.0 * sr))
    n_burst = max(2,
                  int(T_BURST_MS   / 1000.0 * sr))
    n_vot   = max(4,
                  int(T_VOT_MS     / 1000.0 * sr))
    n_total = n_trans + n_clos + n_burst + n_vot
    result  = np.zeros(n_total, dtype=DTYPE)

    F_start = (list(F_prev) if F_prev is not None
               else list(AE_F))

    if n_trans > 0:
        phase    = 0.0; oq = 0.65
        pitch_hz = 145.0
        vsrc     = np.zeros(n_trans, dtype=DTYPE)
        for i in range(n_trans):
            phase += pitch_hz * T_
            if phase >= 1.0:
                phase -= 1.0
            vsrc[i] = ((phase/oq)*(2-phase/oq)
                       if phase < oq
                       else 1-(phase-oq)/(
                           1-oq+1e-9))
        vsrc = f32(np.diff(vsrc, prepend=vsrc[0]))
        vsrc = calibrate(vsrc, target=0.08)
        n_fade = min(n_trans, int(0.012 * sr))
        if n_fade > 0:
            fade = np.ones(n_trans, dtype=DTYPE)
            fade[-n_fade:] = np.linspace(
                1.0, 0.0, n_fade)
            vsrc *= fade
        gains_t = [6.0, 3.5, 1.0, 0.4]
        for fi in range(4):
            f_arr = np.linspace(
                float(F_start[fi]),
                float(T_LOCUS_F[fi]),
                n_trans, dtype=DTYPE)
            out = resonator(vsrc, f_arr,
                             T_LOCUS_B[fi], sr=sr)
            result[:n_trans] += out * gains_t[fi]

    if n_burst > 0:
        s_b = n_trans + n_clos
        e_b = s_b + n_burst
        burst = f32(np.random.normal(
            0, 1, n_burst))
        try:
            b, a  = safe_hp(2500.0, sr)
            burst = f32(lfilter(b, a, burst))
        except Exception:
            pass
        b_env = f32(np.exp(
            -np.arange(n_burst)
            / max(1, n_burst) * 20.0))
        result[s_b:e_b] = burst * b_env * 0.22

    if n_vot > 0:
        s_v = n_trans + n_clos + n_burst
        e_v = s_v + n_vot
        ghost = f32(np.random.normal(
            0, 1, n_vot))
        try:
            b, a  = safe_bp(1200.0, 8000.0, sr)
            ghost = f32(lfilter(b, a, ghost))
        except Exception:
            pass
        ghost   = calibrate(ghost, target=0.04)
        vot_env = f32(np.linspace(
            0.8, 0.0, n_vot))
        result[s_v:e_v] = ghost * vot_env

    boundaries = {
        'trans_end': n_trans,
        'clos_end':  n_trans + n_clos,
        'burst_end': n_trans + n_clos + n_burst,
        'n_trans':   n_trans,
        'n_clos':    n_clos,
        'n_burst':   n_burst,
        'n_vot':     n_vot,
    }
    return f32(result), boundaries


# ============================================================
# ROOM
# ============================================================

def apply_simple_room(sig,
                       rt60=2.8,
                       direct_ratio=0.42,
                       sr=SR):
    n   = len(sig)
    out = np.zeros(n, dtype=np.float64)
    out += sig.astype(float) * direct_ratio
    decay_per_sample = 10 ** (
        -3.0 / (rt60 * sr))
    delays = [int(0.0297*sr), int(0.0371*sr),
              int(0.0411*sr), int(0.0437*sr)]
    comb_gain = (1.0 - direct_ratio) / 4.0
    for d in delays:
        buf = np.zeros(d, dtype=np.float64)
        idx = 0
        g   = decay_per_sample ** d
        co  = np.zeros(n, dtype=np.float64)
        for i in range(n):
            delayed  = buf[idx]
            buf[idx] = float(sig[i]) + delayed*g
            co[i]    = delayed
            idx = (idx + 1) % d
        out += co * comb_gain
    ap_d   = int(0.005 * sr)
    g_ap   = 0.5
    buf_ap = np.zeros(ap_d, dtype=np.float64)
    idx_ap = 0
    for i in range(n):
        x  = out[i]
        w  = x - g_ap * buf_ap[idx_ap]
        out[i] = buf_ap[idx_ap] + g_ap * w
        buf_ap[idx_ap] = w
        idx_ap = (idx_ap + 1) % ap_d
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.72
    return f32(out)


# ============================================================
# FULL WORD
# ============================================================

def synth_hwat(pitch_hz=145.0,
               dil=1.0,
               add_room=True,
               sr=SR):
    """
    Complete word [ʍæt].
    FIX P: synth_AE_ash now returns
    normalized output, so the concatenated
    word has balanced segment levels before
    the final normalization here.
    """
    ae_dur = max(120.0, 160.0 * dil)
    hw_dur = 80.0

    hw_seg = synth_HW(
        F_next=AE_F, dur_ms=hw_dur, sr=sr)
    ae_seg = synth_AE_ash(
        F_prev=HW_F, F_next=T_LOCUS_F,
        dur_ms=ae_dur, pitch_hz=pitch_hz, sr=sr)
    t_result = synth_T_coda(
        F_prev=AE_F, dur_ms=90.0, sr=sr)
    t_seg = t_result[0] \
            if isinstance(t_result, tuple) \
            else t_result

    word = np.concatenate([hw_seg, ae_seg, t_seg])
    mx   = np.max(np.abs(word))
    if mx > 1e-8:
        word = f32(word / mx * 0.75)
    if add_room:
        word = apply_simple_room(
            f32(word), rt60=2.8,
            direct_ratio=0.42, sr=sr)
    return f32(word)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print()
    print("HWÆT — v6")
    print("[ʍæt]  Beowulf line 1")
    print()

    hall = synth_hwat(pitch_hz=145.0,
                      dil=1.0, add_room=True)
    write_wav("output_play/hwæt_hall.wav",
              hall, SR)
    print(f"  hwæt_hall.wav  {len(hall)/SR:.2f}s")

    dry = synth_hwat(pitch_hz=145.0,
                     dil=1.0, add_room=False)
    write_wav("output_play/hwæt_dry.wav", dry, SR)

    try:
        from hwat_diagnostic import ola_stretch
        slow = ola_stretch(dry, factor=4.0)
        write_wav("output_play/hwæt_slow.wav",
                  slow, SR)
        print(f"  hwæt_slow.wav  {len(slow)/SR:.2f}s")
    except Exception as e:
        print(f"  (OLA: {e})")

    print()
    print("  afplay output_play/hwæt_hall.wav")
    print("  afplay output_play/hwæt_slow.wav")
    print()
    print("  THREE PHASES TO HEAR:")
    print("  1. [ʍ] breath — airy, diffuse,")
    print("     no tonal quality")
    print("  2. [æ] vowel — 'bat', immediate")
    print("  3. [t] stop — gap → burst → ghost")
    print()
