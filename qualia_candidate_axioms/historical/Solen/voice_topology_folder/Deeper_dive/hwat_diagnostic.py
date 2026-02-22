"""
HWÆT DIAGNOSTIC — v7
February 2026

CHANGES FROM v6:

  FIX R: LPC order corrected.
    Was hardcoded at 14.
    Standard formula: order = 2 + sr/1000.
    At SR=44100: order = 46, capped at 40.
    Order 14 at 44100 Hz allocates only
    7 pole pairs. A signal with strong F1
    at 780 Hz uses multiple poles to track
    that resonance plus its interaction with
    the Rosenberg harmonics at 145, 290 Hz.
    With only 14 poles, no poles remain for
    F2 at 1850 Hz.
    Order 40 gives 20 pole pairs — more than
    sufficient to resolve F1, F2, F3, F4
    plus harmonic structure.

    The single peak at 280 Hz was the
    Levinson-Durbin fitting the dominant
    low-frequency content of the signal
    (Rosenberg fundamental at 145 Hz +
    the interaction of order-14 LPC with
    a 780 Hz resonance producing a single
    composite pole near the harmonic centroid).

  FIX S: find_peaks height threshold
    lowered from max*0.05 to max*0.02.
    With correct LPC order, F2 at 1850 Hz
    may still be 3–10x weaker than F1 at
    780 Hz in the LPC spectrum (because
    AE_GAINS[0]=20 vs AE_GAINS[1]=4).
    Threshold 0.05 could miss F2 if F2
    peak is 4% of F1 peak height.
    Threshold 0.02 catches it.

  No changes to reconstruction.
  No changes to D1, D3, D4, D5.
"""

import numpy as np
from scipy.signal import (
    lfilter, butter, find_peaks)
import wave as wave_module
import os
import sys

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


# ============================================================
# OLA TIME STRETCH
# ============================================================

def ola_stretch(sig, factor=4.0, sr=SR):
    win_ms   = 40.0
    win_n    = int(win_ms / 1000.0 * sr)
    if win_n % 2 == 1:
        win_n += 1
    hop_in   = win_n // 4
    hop_out  = int(hop_in * factor)
    window   = np.hanning(win_n).astype(DTYPE)
    n_in     = len(sig)
    n_frames = max(1,
                   (n_in - win_n) // hop_in + 1)
    n_out    = hop_out * n_frames + win_n
    out      = np.zeros(n_out, dtype=DTYPE)
    norm     = np.zeros(n_out, dtype=DTYPE)
    for i in range(n_frames):
        in_pos  = i * hop_in
        out_pos = i * hop_out
        if in_pos + win_n > n_in:
            break
        frame = (sig[in_pos:in_pos+win_n]
                 * window)
        out [out_pos:out_pos+win_n] += frame
        norm[out_pos:out_pos+win_n] += window
    safe       = norm > 1e-8
    out[safe] /= norm[safe]
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.75
    return f32(out)


# ============================================================
# ACOUSTIC MEASUREMENTS
# ============================================================

def measure_voicing(seg, sr=SR):
    """
    Autocorrelation peak in F0 range
    80–400 Hz. Uses middle 50% of segment.
    """
    if len(seg) < 256:
        return 0.0
    n    = len(seg)
    core = seg[n//4: 3*n//4].astype(float)
    core -= np.mean(core)
    if np.max(np.abs(core)) < 1e-8:
        return 0.0
    acorr  = np.correlate(core, core,
                           mode='full')
    acorr  = acorr[len(acorr)//2:]
    acorr /= (acorr[0] + 1e-12)
    lo = int(sr / 400)
    hi = min(int(sr / 80),
             len(acorr) - 1)
    if lo >= hi:
        return 0.0
    return float(np.clip(
        np.max(acorr[lo:hi]), 0.0, 1.0))


def measure_sibilance_ratio(seg, sr=SR):
    if len(seg) < 64:
        return 0.0
    try:
        b, a = safe_bp(
            4000.0,
            min(14000.0, sr * 0.48), sr)
        sib  = lfilter(b, a,
                        seg.astype(float))
    except Exception:
        return 0.0
    e_tot = float(np.mean(
        seg.astype(float)**2))
    e_sib = float(np.mean(sib**2))
    if e_tot < 1e-12:
        return 0.0
    return float(np.clip(
        e_sib / e_tot, 0.0, 1.0))


def measure_low_freq_dominance(seg, sr=SR):
    if len(seg) < 64:
        return 0.0
    try:
        b, a = safe_lp(800.0, sr)
        lo   = lfilter(b, a,
                        seg.astype(float))
    except Exception:
        return 0.0
    e_tot = float(np.mean(
        seg.astype(float)**2))
    e_lo  = float(np.mean(lo**2))
    if e_tot < 1e-12:
        return 0.0
    return float(np.clip(
        e_lo / e_tot, 0.0, 1.0))


def estimate_f1_f2(seg, sr=SR,
                    verbose_fail=False):
    """
    LPC formant estimation.

    FIX R: LPC order = min(2 + sr//1000,
           len(seg)//4, 40).
    At SR=44100: order = min(46, n//4, 40)
    = 40 (for segments > 160 samples).
    Previous hardcoded order=14 was
    insufficient — left no poles for F2
    after F1 and harmonics consumed them.

    FIX S: find_peaks height=max*0.02
    (was 0.05). F2 can be 3–10x weaker
    than F1 in the LPC spectrum when
    AE_GAINS[0] >> AE_GAINS[1].

    FIX Q (v6, preserved): normalize
    input to unit peak before LPC.

    Pre-emphasis α=0.50 (v3).
    Voicing gate=0.18 (v4).

    Returns (f1_hz, f2_hz, peak_list).
    """
    # FIX R: correct order formula
    order = min(
        int(2 + sr // 1000),  # = 46 at 44100
        len(seg) // 4,
        40)                    # practical cap
    if order < 4:
        return None, None, []

    if len(seg) < order * 4:
        return None, None, []

    vr = measure_voicing(seg, sr=sr)
    if vr < 0.18:
        if verbose_fail:
            print(f"      [LPC gate] voicing="
                  f"{vr:.3f} < 0.18")
        return None, None, []

    # FIX Q: normalize to unit peak
    seg_f = seg.astype(float)
    mx    = np.max(np.abs(seg_f))
    if mx < 1e-8:
        return None, None, []
    seg_f = seg_f / mx

    # Pre-emphasis α=0.50
    alpha = 0.50
    pre   = np.zeros(len(seg_f), dtype=float)
    pre[0] = seg_f[0]
    for i in range(1, len(seg_f)):
        pre[i] = (seg_f[i]
                  - alpha * seg_f[i-1])
    pre -= np.mean(pre)
    if np.max(np.abs(pre)) < 1e-8:
        return None, None, []

    n = len(pre)
    try:
        r = np.array([
            np.dot(pre[:n-k], pre[k:])
            for k in range(order+1)])
        if abs(r[0]) < 1e-10:
            return None, None, []
        a   = np.zeros(order, dtype=float)
        err = r[0]
        for i in range(order):
            lam = r[i+1]
            for j in range(i):
                lam -= a[j] * r[i-j]
            k_i   = lam / (err + 1e-12)
            k_i   = float(np.clip(
                k_i, -0.9999, 0.9999))
            a_new = a[:i] - k_i * a[:i][::-1]
            a[:i] = a_new
            a[i]  = k_i
            err  *= (1 - k_i**2 + 1e-12)
            if err < 1e-15:
                break
    except Exception as e:
        if verbose_fail:
            print(f"      [LPC except] {e}")
        return None, None, []

    n_fft  = 2048
    coeffs = np.concatenate([[1.0], -a])
    H      = np.fft.rfft(coeffs, n=n_fft)
    spec   = 1.0 / (np.abs(H)**2 + 1e-12)
    freqs  = np.fft.rfftfreq(
        n_fft, d=1.0/sr)

    mask = (freqs >= 200) & (freqs <= 5000)
    s_m  = spec[mask]
    f_m  = freqs[mask]
    if len(s_m) < 3:
        return None, None, []

    bin_hz   = float(freqs[1] - freqs[0]) \
               if len(freqs) > 1 else 1.0
    min_dist = max(1, int(80.0 / bin_hz))

    # FIX S: lower height threshold
    peaks, _ = find_peaks(
        s_m,
        height=np.max(s_m) * 0.02,
        distance=min_dist)

    if len(peaks) < 1:
        return None, None, []

    f_peaks = sorted(
        [float(f_m[p]) for p in peaks])

    # Filter out sub-300 Hz peaks that are
    # pitch harmonics, not formants.
    # F1 of any vowel is >= 250 Hz.
    # Rosenberg fundamental is 145 Hz.
    # Harmonic 2 is 290 Hz — can alias into
    # LPC spectrum. Skip anything < 300 Hz
    # as a first formant candidate only if
    # a peak >= 500 Hz also exists.
    f_vowel = [p for p in f_peaks
               if p >= 300.0]
    if len(f_vowel) == 0:
        f_vowel = f_peaks  # fallback

    f1 = f_vowel[0] if len(f_vowel) > 0 \
         else None
    f2 = f_vowel[1] if len(f_vowel) > 1 \
         else None

    return f1, f2, f_peaks


# ============================================================
# PASS / FAIL REPORTER
# ============================================================

def check(label, value, lo, hi,
           unit='', fmt='.4f'):
    ok     = (lo <= value <= hi)
    status = 'PASS' if ok else 'FAIL'
    bar    = ''
    if 0.0 <= value <= 1.0 and unit == '':
        bar = '█' * int(value * 40)
    val_str = format(value, fmt)
    print(f"    [{status}] {label}: "
          f"{val_str}{unit}  "
          f"target [{lo:{fmt}}–{hi:{fmt}}]"
          f"  {bar}")
    return ok


def check_warn(label, value, lo, hi,
                warn_hi=None,
                unit='', fmt='.4f'):
    if value <= hi:
        ok = True; status = 'PASS'
    elif warn_hi is not None \
            and value <= warn_hi:
        ok = False; status = 'WARN'
    else:
        ok = False; status = 'FAIL'
    bar = ''
    if 0.0 <= value <= 1.0 and unit == '':
        bar = '█' * int(value * 40)
    val_str = format(value, fmt)
    tgt = (f"[{lo:{fmt}}–{hi:{fmt}}]"
           if warn_hi is None
           else f"[{lo:{fmt}}–{hi:{fmt}}]"
                f"  warn<{warn_hi:{fmt}}")
    print(f"    [{status}] {label}: "
          f"{val_str}{unit}  "
          f"target {tgt}  {bar}")
    return ok


# ============================================================
# ACOUSTIC TARGETS — v7
# ============================================================

TARGETS = {
    'HW': {
        'voicing_hard':  0.30,
        'voicing_warn':  0.45,
        'sibilance_max': 0.20,
        'low_freq_min':  0.30,
        'rms_min':       0.010,
    },
    'AE': {
        'voicing_min':   0.55,
        'sibilance_max': 0.10,
        'f1_lo':  650.0, 'f1_hi':  900.0,
        'f2_lo': 1650.0, 'f2_hi': 2100.0,
        'rms_min': 0.020,
        'rms_max': 5.0,
    },
    'T': {
        'voicing_max':  0.25,
        'clos_rms_max': 0.005,
        'rms_min':      0.002,
    },
    'HWAT': {
        'rms_min':  0.015,
        'rms_max':  0.90,
        'hw_vmax':  0.35,
        'ae_vmin':  0.55,
        't_vmax':   0.35,
    },
}


# ============================================================
# FALLBACK SYNTHESIZERS
# ============================================================

def _synth_W_approx(F_next, dur_ms=55.0,
                     pitch_hz=145.0, sr=SR):
    n_s = max(4, int(dur_ms / 1000.0 * sr))
    T   = 1.0 / sr
    W_F = [300.0, 610.0, 2200.0, 3300.0]
    W_B = [ 80.0,  90.0,  210.0,  310.0]
    W_G = [0.5, 0.65, 0.30, 0.15]
    phase = 0.0; oq = 0.65
    src   = np.zeros(n_s, dtype=DTYPE)
    for i in range(n_s):
        phase += pitch_hz * T
        if phase >= 1.0: phase -= 1.0
        src[i] = ((phase/oq)*(2-phase/oq)
                  if phase < oq
                  else 1-(phase-oq)/(
                      1-oq+1e-9))
    src = f32(np.diff(src, prepend=src[0]))
    src = calibrate(src, 0.07)
    n_atk = int(0.010 * sr)
    if 0 < n_atk < n_s:
        src[:n_atk] *= np.linspace(
            0.0, 1.0, n_atk)
    result = np.zeros(n_s, dtype=DTYPE)
    for fi in range(4):
        f_arr = np.linspace(
            float(W_F[fi]),
            float(F_next[fi]),
            n_s, dtype=DTYPE)
        y1 = y2 = 0.0
        out = np.zeros(n_s, dtype=DTYPE)
        for i in range(n_s):
            fc  = max(20.0, min(sr*0.48,
                               float(f_arr[i])))
            bw  = float(W_B[fi])
            a2  = -np.exp(-2*np.pi*bw*T)
            a1  =  2*np.exp(-np.pi*bw*T) * \
                   np.cos(2*np.pi*fc*T)
            b0  = 1.0 - a1 - a2
            y   = (b0*float(src[i])
                   + a1*y1 + a2*y2)
            y2 = y1; y1 = y
            out[i] = y
        result += out * W_G[fi]
    return f32(result)


def _synth_AH(dur_ms=160.0,
               pitch_hz=145.0, sr=SR):
    n_s  = max(4, int(dur_ms / 1000.0 * sr))
    T    = 1.0 / sr
    AH_F = [700.0, 1220.0, 2600.0, 3200.0]
    AH_B = [130.0,  110.0,  180.0,  220.0]
    AH_G = [6.0, 4.5, 1.8, 0.7]
    phase = 0.0; oq = 0.65
    src   = np.zeros(n_s, dtype=DTYPE)
    for i in range(n_s):
        phase += pitch_hz * T
        if phase >= 1.0: phase -= 1.0
        src[i] = ((phase/oq)*(2-phase/oq)
                  if phase < oq
                  else 1-(phase-oq)/(
                      1-oq+1e-9))
    src = f32(np.diff(src, prepend=src[0]))
    n_atk = min(int(0.020*sr), n_s//4)
    n_rel = min(int(0.040*sr), n_s//4)
    env   = np.ones(n_s, dtype=DTYPE)
    if n_atk < n_s:
        env[:n_atk] = np.linspace(
            0.5, 1.0, n_atk)
    if n_rel < n_s:
        env[-n_rel:] = np.linspace(
            1.0, 0.0, n_rel)
    src = f32(src * env)
    src = calibrate(src, 0.08)
    result = np.zeros(n_s, dtype=DTYPE)
    for fi in range(4):
        y1 = y2 = 0.0
        out = np.zeros(n_s, dtype=DTYPE)
        fc  = float(AH_F[fi])
        bw  = float(AH_B[fi])
        for i in range(n_s):
            a2  = -np.exp(-2*np.pi*bw*T)
            a1  =  2*np.exp(-np.pi*bw*T) * \
                   np.cos(2*np.pi*fc*T)
            b0  = 1.0 - a1 - a2
            y   = (b0*float(src[i])
                   + a1*y1 + a2*y2)
            y2 = y1; y1 = y
            out[i] = y
        result += out * AH_G[fi]
    return f32(result)


# ============================================================
# IMPORT MODULES
# ============================================================

def _import_reconstruction():
    try:
        import hwat_reconstruction as rec
        return rec, True, None
    except ImportError as e:
        return None, False, str(e)

def _import_v17():
    try:
        from voice_physics_v17 import synth_phrase
        return synth_phrase, True, None
    except ImportError as e:
        return None, False, str(e)


# ============================================================
# DIAGNOSTIC RUNNER
# ============================================================

def run_diagnostics():

    print("=" * 60)
    print("HWÆT DIAGNOSTIC v7")
    print("Self-referential acoustic analysis")
    print("Old English [ʍæt] — Beowulf line 1")
    print("=" * 60)
    print()

    rec, rec_ok, rec_err = \
        _import_reconstruction()
    if not rec_ok:
        print(f"  hwat_reconstruction.py: "
              f"IMPORT FAILED\n  {rec_err}")
        return False
    print("  hwat_reconstruction.py: OK")

    v17_synth, v17_ok, _ = _import_v17()
    print(f"  voice_physics_v17.py:    "
          f"{'OK' if v17_ok else 'not found'}")
    print()

    AE_F         = rec.AE_F
    HW_F         = rec.HW_F
    HW_B         = rec.HW_B
    HW_NOISE_LO  = getattr(
        rec, 'HW_NOISE_LO', 100.0)
    T_LOCUS_F    = rec.T_LOCUS_F
    AE_COART_ON  = rec.AE_COART_ON
    AE_COART_OFF = rec.AE_COART_OFF
    T_TRANS_MS   = rec.T_TRANS_MS
    T_CLOSURE_MS = rec.T_CLOSURE_MS

    # Compute LPC order that will be used
    lpc_order = min(
        int(2 + SR // 1000), 40)

    all_pass = True
    pause    = np.zeros(
        int(0.35*SR), dtype=DTYPE)
    lp       = np.zeros(
        int(0.50*SR), dtype=DTYPE)

    # ══════════════════════════════════════════
    # D1 — HW ONSET
    # ══════════════════════════════════════════

    print("─" * 60)
    print("DIAGNOSTIC 1 — HW ONSET [ʍ]")
    print()
    print(f"  Noise pre-filter: "
          f"{HW_NOISE_LO:.0f}–6000 Hz")
    print(f"  HW_B: "
          f"{[f'{b:.0f}' for b in HW_B]}")
    print()

    hw        = rec.synth_HW(
        F_next=AE_F, dur_ms=80.0, sr=SR)
    n_hw      = len(hw)
    n_stable  = int(n_hw * 0.60)
    hw_stable = hw[:n_stable]

    print(f"  HW: {n_hw} samples"
          f" ({n_hw/SR*1000:.0f} ms)"
          f"  stable zone [0:{n_stable}]")
    print()

    vr  = measure_voicing(hw_stable, sr=SR)
    sib = measure_sibilance_ratio(hw, sr=SR)
    lf  = measure_low_freq_dominance(hw, sr=SR)
    r   = rms(hw)

    t  = TARGETS['HW']
    p1 = check_warn(
        'voicing (stable zone)', vr,
        0.0, t['voicing_hard'],
        warn_hi=t['voicing_warn'])
    p2 = check('sibilance ratio', sib,
                0.0, t['sibilance_max'])
    p3 = check('low-freq dominance', lf,
                t['low_freq_min'], 1.0)
    p4 = check('RMS level', r,
                t['rms_min'], 1.0)
    d1 = p1 and p2 and p3 and p4
    all_pass &= d1

    hw_n    = f32(hw / (
        np.max(np.abs(hw))+1e-8) * 0.75)
    write_wav(
        "output_play/diag_hw_onset.wav",
        hw_n, SR)
    write_wav(
        "output_play/diag_hw_onset_slow.wav",
        ola_stretch(hw_n, 4.0), SR)
    w_seg   = _synth_W_approx(
        AE_F, 80.0, 145.0, SR)
    w_n     = f32(w_seg / (
        np.max(np.abs(w_seg))+1e-8) * 0.75)
    hw_vs_w = np.concatenate([
        hw_n, pause, w_n, pause,
        hw_n, pause, w_n])
    write_wav(
        "output_play/diag_hw_vs_w.wav",
        f32(hw_vs_w / (
            np.max(np.abs(hw_vs_w))
            +1e-8) * 0.80), SR)

    print()
    print("  diag_hw_onset_slow.wav")
    print("  diag_hw_vs_w.wav")
    print(f"  {'PASSED' if d1 else 'WARN/FAILED'}")
    print()

    # ══════════════════════════════════════════
    # D2 — Æ VOWEL
    # ══════════════════════════════════════════

    print("─" * 60)
    print("DIAGNOSTIC 2 — Æ VOWEL [æ]")
    print()
    print(f"  LPC order: {lpc_order}"
          f"  (FIX R: was 14)")
    print(f"  Peak threshold: 0.02"
          f"  (FIX S: was 0.05)")
    print()

    ae    = rec.synth_AE_ash(
        F_prev=HW_F, F_next=T_LOCUS_F,
        dur_ms=160.0, pitch_hz=145.0, sr=SR)
    n_ae  = len(ae)

    n_on_skip  = int(AE_COART_ON  * n_ae)
    n_off_skip = int(AE_COART_OFF * n_ae)
    body_start = n_on_skip
    body_end   = n_ae - n_off_skip
    ae_body    = ae[body_start:body_end]

    print(f"  Æ: {n_ae} samples"
          f" ({n_ae/SR*1000:.0f} ms)")
    print(f"  Body: [{body_start}:{body_end}]"
          f" ({(body_end-body_start)/SR*1000:.0f} ms)")
    print()

    vr     = measure_voicing(ae_body, sr=SR)
    sib    = measure_sibilance_ratio(
        ae_body, sr=SR)
    r      = rms(ae)
    f1, f2, peaks = estimate_f1_f2(
        ae_body, sr=SR, verbose_fail=True)

    t  = TARGETS['AE']
    p1 = check('voicing (body zone)', vr,
                t['voicing_min'], 1.0)
    p2 = check('sibilance ratio', sib,
                0.0, t['sibilance_max'])
    p3 = check('RMS level', r,
                t['rms_min'],
                t.get('rms_max', 5.0))
    p4 = p5 = True

    # Always print peak list in D2
    # so formant structure is visible
    print(f"  LPC peaks (all, ≥200 Hz):")
    if peaks:
        for p in peaks:
            marker = ''
            if 650 <= p <= 900:
                marker = ' ← F1 target'
            elif 1650 <= p <= 2100:
                marker = ' ← F2 target'
            elif p < 300:
                marker = ' ← sub-F1 (harmonic?)'
            print(f"    {p:.0f} Hz{marker}")
    else:
        print("    (none found)")
    print()

    if f1 is not None:
        p4 = check(
            f'F1 ({f1:.0f} Hz)', f1,
            t['f1_lo'], t['f1_hi'],
            unit=' Hz', fmt='.1f')
        if not p4:
            print(f"      F1={f1:.0f} Hz out of"
                  f" [650–900]")
            if f1 < 300:
                print(f"      Sub-300 Hz root.")
                print(f"      Pitch harmonic leak.")
                print(f"      Raise lower freq mask")
                print(f"      in estimate_f1_f2")
                print(f"      from 200 → 400 Hz.")
            elif f1 < 650:
                print(f"      Root between 300–650.")
                print(f"      Intermediate harmonic.")
                print(f"      Raise AE_GAINS[0]"
                      f" above 20.")
    else:
        p4 = False
        print(f"    [FAIL] F1: not found")
        print(f"      voicing = {vr:.3f}")

    if f2 is not None:
        p5 = check(
            f'F2 ({f2:.0f} Hz)', f2,
            t['f2_lo'], t['f2_hi'],
            unit=' Hz', fmt='.1f')
        if not p5:
            print(f"      F2={f2:.0f} Hz"
                  f" out of [1650–2100]")
    else:
        p5 = False
        if f1 is not None:
            print(f"    [FAIL] F2: not found")
            print(f"      F1={f1:.0f} Hz found,")
            print(f"      no second peak above it")
            print(f"      in vowel range.")
            print(f"      Check AE_GAINS[1]=4.0")

    d2 = p1 and p2 and p3 and p4 and p5
    all_pass &= d2

    ae_n  = f32(ae / (
        np.max(np.abs(ae))+1e-8) * 0.75)
    write_wav(
        "output_play/diag_ae_vowel.wav",
        ae_n, SR)
    write_wav(
        "output_play/diag_ae_vowel_slow.wav",
        ola_stretch(ae_n, 4.0), SR)
    ah    = _synth_AH(160.0, 145.0, SR)
    ah_n  = f32(ah / (
        np.max(np.abs(ah))+1e-8) * 0.75)
    avsah = np.concatenate([
        ae_n, pause, ah_n, pause,
        ae_n, pause, ah_n])
    write_wav(
        "output_play/diag_ae_vs_ah.wav",
        f32(avsah / (
            np.max(np.abs(avsah))
            +1e-8) * 0.80), SR)

    print()
    print("  diag_ae_vowel_slow.wav")
    print("  diag_ae_vs_ah.wav")
    print(f"  {'PASSED' if d2 else 'FAILED'}")
    print()

    # ══════════════════════════════════════════
    # D3 — T CODA
    # ══════════════════════════════════════════

    print("─" * 60)
    print("DIAGNOSTIC 3 — T CODA [t]")
    print()

    t_result = rec.synth_T_coda(
        F_prev=AE_F, dur_ms=90.0, sr=SR)
    if isinstance(t_result, tuple):
        t_coda, t_bounds = t_result
    else:
        t_coda, t_bounds = t_result, None

    n_t = len(t_coda)
    if t_bounds is not None:
        trans_end = t_bounds['trans_end']
        clos_end  = t_bounds['clos_end']
        n_clos    = t_bounds['n_clos']
    else:
        trans_end = int(T_TRANS_MS/1000.0*SR)
        clos_end  = trans_end + int(
            T_CLOSURE_MS/1000.0*SR)
        n_clos    = clos_end - trans_end

    print(f"  voiced [{0}:{trans_end}]"
          f"  closure [{trans_end}:{clos_end}]")
    print()

    vr = measure_voicing(t_coda, sr=SR)
    r  = rms(t_coda)
    t_ = TARGETS['T']
    p1 = check('voicing fraction', vr,
                0.0, t_['voicing_max'])
    p2 = check('RMS level', r,
                t_['rms_min'], 1.0)
    p3 = True
    if clos_end <= n_t and trans_end < clos_end:
        crms = rms(t_coda[trans_end:clos_end])
        p3   = check(
            f'closure RMS '
            f'[{trans_end}:{clos_end}]',
            crms, 0.0, t_['clos_rms_max'],
            fmt='.6f')
    else:
        print("    [WARN] closure window"
              " out of range")
        p3 = False

    d3 = p1 and p2 and p3
    all_pass &= d3

    t_n = f32(t_coda / (
        np.max(np.abs(t_coda))+1e-8) * 0.75)
    write_wav(
        "output_play/diag_t_coda.wav",
        t_n, SR)
    write_wav(
        "output_play/diag_t_coda_slow.wav",
        ola_stretch(t_n, 4.0), SR)

    print()
    print("  diag_t_coda_slow.wav")
    print(f"  {'PASSED' if d3 else 'FAILED'}")
    print()

    # ══════════════════════════════════════════
    # D4 — FULL WORD
    # ══════════════════════════════════════════

    print("─" * 60)
    print("DIAGNOSTIC 4 — FULL WORD [ʍæt]")
    print()

    hwat_dry  = rec.synth_hwat(
        pitch_hz=145.0, dil=1.0,
        add_room=False, sr=SR)
    hwat_hall = rec.synth_hwat(
        pitch_hz=145.0, dil=1.0,
        add_room=True, sr=SR)

    r  = rms(hwat_dry)
    t_ = TARGETS['HWAT']
    p1 = check('full-word RMS', r,
                t_['rms_min'], t_['rms_max'])

    n_hw_s = int(0.080 * SR)
    n_ae_s = int(0.160 * SR)
    n_ae_on  = int(AE_COART_ON  * n_ae_s)
    n_ae_off = int(AE_COART_OFF * n_ae_s)
    w_ae_s   = n_hw_s + n_ae_on
    w_ae_e   = n_hw_s + n_ae_s - n_ae_off
    w_t_s    = n_hw_s + n_ae_s
    w_t_e    = len(hwat_dry)

    print(f"  {len(hwat_dry)} samples"
          f" ({len(hwat_dry)/SR*1000:.0f} ms)")
    print(f"  HW[0:{n_hw_s}]"
          f"  Æ[{w_ae_s}:{w_ae_e}]"
          f"  T[{w_t_s}:{w_t_e}]")
    print()

    def sw(sig, s, e):
        s = max(0, s)
        e = min(len(sig), e)
        return sig[s:e] if e > s \
               else sig[:10]

    vr_hw = measure_voicing(
        sw(hwat_dry, 0, n_hw_s), SR)
    vr_ae = measure_voicing(
        sw(hwat_dry, w_ae_s, w_ae_e), SR)
    vr_t  = measure_voicing(
        sw(hwat_dry, w_t_s, w_t_e), SR)

    p2 = check('HW zone voicing', vr_hw,
                0.0, t_['hw_vmax'])
    p3 = check('Æ body voicing',  vr_ae,
                t_['ae_vmin'], 1.0)
    p4 = check('T zone voicing',  vr_t,
                0.0, t_['t_vmax'])

    d4 = p1 and p2 and p3 and p4
    all_pass &= d4

    write_wav(
        "output_play/diag_hwat_full.wav",
        hwat_dry, SR)
    write_wav(
        "output_play/diag_hwat_full_hall.wav",
        hwat_hall, SR)
    write_wav(
        "output_play/diag_hwat_slow.wav",
        ola_stretch(hwat_dry, 4.0), SR)

    print()
    print("  diag_hwat_full.wav")
    print("  diag_hwat_full_hall.wav")
    print("  diag_hwat_slow.wav")
    print(f"  {'PASSED' if d4 else 'FAILED'}")
    print()

    # ══════════════════════════════════════════
    # D5 — PERCEPTUAL CONTRAST
    # ══════════════════════════════════════════

    print("─" * 60)
    print("DIAGNOSTIC 5 — [ʍæt] vs [wɑt]")
    print()

    v17_local = False
    if v17_ok:
        try:
            what_raw = f32(v17_synth(
                [('what', ['W','AH','T'])],
                punctuation='.',
                add_ghost=False))
            print("  Modern 'what': v17 engine")
            v17_local = True
        except Exception as ex:
            print(f"  v17 failed: {ex}")

    if not v17_local:
        AH_F = [700.0, 1220.0, 2600.0, 3200.0]
        t_w  = rec.synth_T_coda(
            F_prev=AH_F, dur_ms=80.0, sr=SR)
        t_w  = t_w[0] \
               if isinstance(t_w, tuple) \
               else t_w
        what_raw = np.concatenate([
            _synth_W_approx(
                AH_F, 55.0, 145.0, SR),
            _synth_AH(160.0, 145.0, SR),
            t_w])
        print("  Modern 'what': fallback")

    what_n    = f32(what_raw / (
        np.max(np.abs(what_raw))+1e-8) * 0.75)
    what_hall = rec.apply_simple_room(
        what_n, rt60=2.8,
        direct_ratio=0.42, sr=SR)
    hwat_h5   = rec.synth_hwat(
        pitch_hz=145.0, dil=1.0,
        add_room=True, sr=SR)
    hwat_d5   = rec.synth_hwat(
        pitch_hz=145.0, dil=1.0,
        add_room=False, sr=SR)

    write_wav(
        "output_play/diag_what_modern.wav",
        what_hall, SR)
    comp = np.concatenate([
        hwat_h5, pause, what_hall, pause,
        hwat_h5, pause, what_hall])
    write_wav(
        "output_play/diag_hwat_vs_what.wav",
        f32(comp / (
            np.max(np.abs(comp))+1e-8)
            * 0.80), SR)

    hw_a  = rec.synth_HW(
        F_next=AE_F, dur_ms=80.0, sr=SR)
    hw_an = f32(hw_a / (
        np.max(np.abs(hw_a))+1e-8) * 0.75)
    w_a   = _synth_W_approx(
        AE_F, 80.0, 145.0, SR)
    w_an  = f32(w_a / (
        np.max(np.abs(w_a))+1e-8) * 0.75)
    onset_slow = np.concatenate([
        ola_stretch(hw_an, 4.0), lp,
        ola_stretch(w_an,  4.0), lp,
        ola_stretch(hw_an, 4.0), lp,
        ola_stretch(w_an,  4.0)])
    write_wav(
        "output_play/diag_onset_axis_slow.wav",
        f32(onset_slow / (
            np.max(np.abs(onset_slow))
            +1e-8) * 0.80), SR)

    ae_a  = rec.synth_AE_ash(
        F_prev=HW_F, F_next=T_LOCUS_F,
        dur_ms=160.0, pitch_hz=145.0, sr=SR)
    ae_an = f32(ae_a / (
        np.max(np.abs(ae_a))+1e-8) * 0.75)
    ah_a  = _synth_AH(160.0, 145.0, SR)
    ah_an = f32(ah_a / (
        np.max(np.abs(ah_a))+1e-8) * 0.75)
    vowel_slow = np.concatenate([
        ola_stretch(ae_an, 4.0), lp,
        ola_stretch(ah_an, 4.0), lp,
        ola_stretch(ae_an, 4.0), lp,
        ola_stretch(ah_an, 4.0)])
    write_wav(
        "output_play/diag_vowel_axis_slow.wav",
        f32(vowel_slow / (
            np.max(np.abs(vowel_slow))
            +1e-8) * 0.80), SR)

    what_dry = what_n
    if v17_local:
        try:
            what_dry = f32(v17_synth(
                [('what', ['W','AH','T'])],
                punctuation='.',
                add_ghost=False,
                add_breath=False))
        except Exception:
            pass
    slow_cmp = np.concatenate([
        ola_stretch(hwat_d5, 4.0), lp,
        ola_stretch(f32(what_dry), 4.0)])
    write_wav(
        "output_play/diag_comparison_slow.wav",
        f32(slow_cmp / (
            np.max(np.abs(slow_cmp))
            +1e-8) * 0.80), SR)

    print()
    print("  PLAY ORDER:")
    print("  afplay output_play/"
          "diag_onset_axis_slow.wav")
    print("  afplay output_play/"
          "diag_vowel_axis_slow.wav")
    print("  afplay output_play/"
          "diag_hwat_slow.wav")
    print("  afplay output_play/"
          "diag_hwat_vs_what.wav")
    print("  afplay output_play/"
          "diag_hwat_full_hall.wav")
    print()

    # ══════════════════════════════════════════
    # SUMMARY
    # ══════════════════════════════════════════

    print("=" * 60)
    print("SUMMARY")
    print()
    rows = [
        ("D1 HW onset",  d1),
        ("D2 Æ vowel",   d2),
        ("D3 T coda",    d3),
        ("D4 Full word", d4),
    ]
    for lbl, ok in rows:
        sym = "✓ PASS" if ok else "✗ FAIL"
        print(f"  {lbl:22s}  {sym}")
    print(f"  {'D5 Perceptual':22s}  LISTEN")
    print()

    if all_pass:
        print("  ALL NUMERIC CHECKS PASSED")
        print()
        print("  afplay output_play/"
              "hwæt_hall.wav")
        print("  afplay output_play/"
              "hwæt_slow.wav")
    else:
        failed = [l for l, ok in rows
                  if not ok]
        print(f"  FAILED: {', '.join(failed)}")
        print()
        if not d2:
            if peaks:
                low = [p for p in peaks
                       if p < 300]
                mid = [p for p in peaks
                       if 300 <= p < 650]
                tgt = [p for p in peaks
                       if 650 <= p <= 900]
                print(f"  D2 LPC peaks:")
                print(f"    sub-300: {low}")
                print(f"    300–650: {mid}")
                print(f"    F1 zone: {tgt}")
                if tgt:
                    print(f"    F1 present."
                          f" Check F2 zone.")
                elif mid:
                    print(f"    Root in 300–650.")
                    print(f"    Raise AE_GAINS[0].")
                else:
                    print(f"    No root ≥300 Hz.")
                    print(f"    Raise freq floor in")
                    print(f"    estimate_f1_f2"
                          f" mask from 200→400 Hz.")
            if not d1:
                print(f"  D1: HW_NOISE_LO"
                      f"={HW_NOISE_LO:.0f}"
                      f" must be 500 Hz")

    print()
    print("=" * 60)
    return all_pass


if __name__ == "__main__":
    print()
    passed = run_diagnostics()
    sys.exit(0 if passed else 1)
