"""
WĒ DIAGNOSTIC
Old English [weː] — Beowulf line 1, word 2
February 2026

DIAGNOSTIC STRUCTURE:
  D1 — W onset [w]
       voicing fraction > 0.60
       sibilance ratio  < 0.05
       low-freq dominance > 0.50
       (compare: HW had voicing 0.1797
        W should be clearly voiced)

  D2 — Ē vowel [eː]
       voicing > 0.75
       F1: 380–520 Hz
           (higher tongue than [æ]'s 650–900)
       F2: 1900–2400 Hz
           (front position, same as [æ])

  D3 — Full word voicing profile
       Both zones voiced: HIGH → HIGH
       (first all-voiced word in reconstruction)

  D4 — Contrast: Wē vs modern "we" [wiː]
       F1 comparison: [eː] ~420 Hz vs [iː] ~300 Hz
       Perceptual: sounds like German "See" not English "we"
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
        frame = sig[in_pos:in_pos+win_n] * window
        out [out_pos:out_pos+win_n] += frame
        norm[out_pos:out_pos+win_n] += window
    safe       = norm > 1e-8
    out[safe] /= norm[safe]
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.75
    return f32(out)


# ============================================================
# MEASUREMENTS
# ============================================================

def measure_voicing(seg, sr=SR):
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

def measure_sibilance(seg, sr=SR):
    if len(seg) < 64:
        return 0.0
    try:
        b, a = safe_bp(
            4000.0,
            min(14000.0, sr * 0.48), sr)
        sib = lfilter(b, a,
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

def measure_low_freq(seg, sr=SR):
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
                    verbose=False):
    order = min(
        int(2 + sr // 1000),
        len(seg) // 4,
        40)
    if order < 4:
        return None, None, []
    if len(seg) < order * 4:
        return None, None, []
    vr = measure_voicing(seg, sr=sr)
    if vr < 0.18:
        if verbose:
            print(f"      [LPC gate] "
                  f"voicing={vr:.3f} < 0.18")
        return None, None, []
    seg_f = seg.astype(float)
    mx    = np.max(np.abs(seg_f))
    if mx < 1e-8:
        return None, None, []
    seg_f = seg_f / mx
    alpha = 0.50
    pre   = np.zeros(len(seg_f),
                     dtype=float)
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
            k_i = lam / (err + 1e-12)
            k_i = float(np.clip(
                k_i, -0.9999, 0.9999))
            a_new = a[:i] - k_i * a[:i][::-1]
            a[:i] = a_new
            a[i]  = k_i
            err  *= (1 - k_i**2 + 1e-12)
            if err < 1e-15:
                break
    except Exception as e:
        if verbose:
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
    peaks, _ = find_peaks(
        s_m,
        height=np.max(s_m) * 0.02,
        distance=min_dist)
    if len(peaks) < 1:
        return None, None, []
    f_peaks = sorted(
        [float(f_m[p]) for p in peaks])
    f_vowel = [p for p in f_peaks
               if p >= 300.0]
    if len(f_vowel) == 0:
        f_vowel = f_peaks
    f1 = f_vowel[0] if len(f_vowel) > 0 \
         else None
    f2 = f_vowel[1] if len(f_vowel) > 1 \
         else None
    return f1, f2, f_peaks


# ============================================================
# CHECK HELPERS
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
    if value >= lo:
        ok = True; status = 'PASS'
    elif warn_hi is not None \
            and value >= warn_hi:
        ok = False; status = 'WARN'
    else:
        ok = False; status = 'FAIL'
    bar = ''
    if 0.0 <= value <= 1.0 and unit == '':
        bar = '█' * int(value * 40)
    val_str = format(value, fmt)
    print(f"    [{status}] {label}: "
          f"{val_str}{unit}  "
          f"target [{lo:{fmt}}–{hi:{fmt}}]"
          f"  {bar}")
    return ok


# ============================================================
# IMPORT RECONSTRUCTION
# ============================================================

def _import_we():
    try:
        from we_reconstruction import (
            synth_we,
            synth_W_onset,
            synth_E_long,
            apply_simple_room,
            W_F, W_B,
            E_F, E_B,
            E_COART_ON, E_COART_OFF)
        return (synth_we, synth_W_onset,
                synth_E_long,
                apply_simple_room,
                W_F, W_B, E_F, E_B,
                E_COART_ON, E_COART_OFF,
                True, None)
    except ImportError as e:
        return (None,)*10 + (False, str(e))


# ============================================================
# DIAGNOSTIC RUNNER
# ============================================================

def run_diagnostics():

    print()
    print("=" * 60)
    print("WĒ DIAGNOSTIC")
    print("Old English [weː]")
    print("Beowulf line 1, word 2")
    print("=" * 60)
    print()

    (synth_we, synth_W_onset,
     synth_E_long, apply_simple_room,
     W_F, W_B, E_F, E_B,
     E_COART_ON, E_COART_OFF,
     ok, err) = _import_we()

    if not ok:
        print(f"  we_reconstruction.py: "
              f"IMPORT FAILED\n  {err}")
        return False
    print("  we_reconstruction.py: OK")
    print()

    all_pass = True
    pause    = np.zeros(
        int(0.35 * SR), dtype=DTYPE)

    # ══════════════════════════════════════
    # D1 — W ONSET
    # ══════════════════════════════════════

    print("─" * 60)
    print("DIAGNOSTIC 1 — W ONSET [w]")
    print()
    print("  Voiced labiovelar approximant.")
    print("  Contrast target with HW onset:")
    print("    HW voicing was: 0.1797 (voiceless)")
    print("    W  voicing target: > 0.60 (voiced)")
    print()

    w_seg = synth_W_onset(
        F_next=E_F,
        pitch_hz=145.0,
        dil=1.0, sr=SR)

    n_w      = len(w_seg)
    n_stable = int(n_w * 0.50)
    w_stable = w_seg[:n_stable]

    print(f"  W onset: {n_w} samples"
          f" ({n_w/SR*1000:.0f} ms)")
    print(f"  Stable zone: [0:{n_stable}]")
    print()

    vr  = measure_voicing(w_stable, sr=SR)
    sib = measure_sibilance(w_seg, sr=SR)
    lf  = measure_low_freq(w_seg, sr=SR)
    r   = rms(w_seg)

    p1 = check_warn(
        'voicing (stable zone)', vr,
        0.60, 1.0,
        warn_hi=0.45)
    p2 = check('sibilance ratio', sib,
                0.0, 0.05)
    p3 = check('low-freq dominance', lf,
                0.50, 1.0)
    p4 = check('RMS level', r,
                0.010, 1.0)
    d1 = p1 and p2 and p3 and p4
    all_pass &= d1

    w_n = f32(w_seg / (
        np.max(np.abs(w_seg))+1e-8) * 0.75)
    write_wav(
        "output_play/diag_w_onset_slow.wav",
        ola_stretch(w_n, 4.0), SR)

    # Contrast file: W vs HW
    try:
        sys.path.insert(0, '..')
        from word_01_hwat.hwat_reconstruction \
            import synth_HW, AE_F
        hw_seg = synth_HW(
            F_next=AE_F,
            dur_ms=80.0, sr=SR)
        hw_n = f32(hw_seg / (
            np.max(np.abs(hw_seg))+1e-8) * 0.75)
        contrast = np.concatenate([
            hw_n, pause, w_n, pause,
            hw_n, pause, w_n])
        write_wav(
            "output_play/diag_w_vs_hw.wav",
            f32(contrast / (
                np.max(np.abs(contrast))
                +1e-8) * 0.80), SR)
        print()
        print("  diag_w_onset_slow.wav")
        print("  diag_w_vs_hw.wav  "
              "(W vs HW — voiced vs voiceless)")
    except ImportError:
        print()
        print("  diag_w_onset_slow.wav")
        print("  (diag_w_vs_hw.wav — "
              "hwat_reconstruction not found)")

    print(f"  {'PASSED' if d1 else 'FAILED'}")
    print()

    # ══════════════════════════════════════
    # D2 — Ē VOWEL
    # ══════════════════════════════════════

    print("─" * 60)
    print("DIAGNOSTIC 2 — Ē VOWEL [eː]")
    print()
    print("  Long close-mid front vowel.")
    print("  Pre-Great-Vowel-Shift Old English.")
    print("  Compare to [æ] in HWÆT:")
    print("    [æ] F1 was: 667.5 Hz (low jaw)")
    print("    [eː] F1 target: 380–520 Hz"
          " (higher tongue)")
    print("    F2 similar: both front vowels")
    print()
    print(f"  LPC order: "
          f"{min(int(2 + SR//1000), 40)}")
    print()

    e_seg  = synth_E_long(
        F_prev=W_F,
        pitch_hz=145.0,
        dil=1.0, sr=SR)
    n_e    = len(e_seg)
    n_on   = int(E_COART_ON  * n_e)
    n_off  = int(E_COART_OFF * n_e)
    body_s = n_on
    body_e = n_e - n_off
    e_body = e_seg[body_s:body_e]

    print(f"  Ē: {n_e} samples"
          f" ({n_e/SR*1000:.0f} ms)")
    print(f"  Body: [{body_s}:{body_e}]"
          f" ({(body_e-body_s)/SR*1000:.0f} ms)")
    print()

    vr  = measure_voicing(e_body, sr=SR)
    sib = measure_sibilance(e_body, sr=SR)
    r   = rms(e_seg)
    f1, f2, peaks = estimate_f1_f2(
        e_body, sr=SR, verbose=True)

    p1 = check('voicing (body zone)', vr,
                0.75, 1.0)
    p2 = check('sibilance ratio', sib,
                0.0, 0.05)
    p3 = check('RMS level', r,
                0.020, 5.0)

    print(f"  LPC peaks (all, ≥200 Hz):")
    if peaks:
        for p in peaks:
            marker = ''
            if 380 <= p <= 520:
                marker = ' ← F1 target [eː]'
            elif 650 <= p <= 900:
                marker = ' ← F1 zone [æ]'
                marker += ' (too low for [eː])'
            elif 1900 <= p <= 2400:
                marker = ' ← F2 target [eː]'
            elif p < 300:
                marker = ' ← sub-F1 (harmonic?)'
            print(f"    {p:.0f} Hz{marker}")
    else:
        print("    (none found)")
    print()

    p4 = p5 = True
    if f1 is not None:
        p4 = check(
            f'F1 ({f1:.0f} Hz)', f1,
            380.0, 520.0,
            unit=' Hz', fmt='.1f')
        if not p4:
            if f1 > 520:
                print(f"      F1={f1:.0f} Hz"
                      f" too high.")
                print(f"      Vowel too open.")
                print(f"      Raise E_F[0]"
                      f" above 420 Hz.")
                print(f"      Or reduce E_GAINS[0].")
            elif f1 < 380:
                print(f"      F1={f1:.0f} Hz"
                      f" too low.")
                print(f"      Vowel too closed.")
                print(f"      Lower E_F[0]"
                      f" below 420 Hz.")
    else:
        p4 = False
        print(f"    [FAIL] F1: not found")

    if f2 is not None:
        p5 = check(
            f'F2 ({f2:.0f} Hz)', f2,
            1900.0, 2400.0,
            unit=' Hz', fmt='.1f')
        if not p5:
            print(f"      F2={f2:.0f} Hz"
                  f" out of [1900–2400]")
            if f2 < 1900:
                print(f"      Too back.")
                print(f"      Raise E_F[1].")
            elif f2 > 2400:
                print(f"      Too front/high.")
                print(f"      Lower E_F[1].")
    else:
        p5 = False
        if f1 is not None:
            print(f"    [FAIL] F2: not found")

    d2 = p1 and p2 and p3 and p4 and p5
    all_pass &= d2

    e_n = f32(e_seg / (
        np.max(np.abs(e_seg))+1e-8) * 0.75)
    write_wav(
        "output_play/diag_e_vowel_slow.wav",
        ola_stretch(e_n, 4.0), SR)

    print()
    print("  diag_e_vowel_slow.wav")
    print(f"  {'PASSED' if d2 else 'FAILED'}")
    print()

    # ══════════════════════════════════════
    # D3 — FULL WORD
    # ══════════════════════════════════════

    print("─" * 60)
    print("DIAGNOSTIC 3 — FULL WORD [weː]")
    print()

    we_dry = synth_we(
        pitch_hz=145.0,
        dil=1.0,
        add_room=False)
    we_hall = synth_we(
        pitch_hz=145.0,
        dil=1.0,
        add_room=True)

    r = rms(we_dry)
    p1 = check('full-word RMS', r,
                0.015, 0.90)

    n_w_s = int(55.0 / 1000.0 * SR)
    n_e_s = len(we_dry) - n_w_s

    def sw(sig, s, e):
        s = max(0, s)
        e = min(len(sig), e)
        return sig[s:e] if e > s \
               else sig[:10]

    vr_w = measure_voicing(
        sw(we_dry, 0, n_w_s), SR)
    vr_e = measure_voicing(
        sw(we_dry, n_w_s, len(we_dry)), SR)

    print(f"  {len(we_dry)} samples"
          f" ({len(we_dry)/SR*1000:.0f} ms)")
    print(f"  W[0:{n_w_s}]"
          f"  Ē[{n_w_s}:{len(we_dry)}]")
    print()
    print("  Voicing profile: both zones voiced")
    print("  (first all-voiced word"
          " in reconstruction)")
    print()

    p2 = check_warn(
        'W zone voicing', vr_w,
        0.55, 1.0)
    p3 = check_warn(
        'Ē zone voicing', vr_e,
        0.75, 1.0)

    d3 = p1 and p2 and p3
    all_pass &= d3

    write_wav(
        "output_play/diag_we_full.wav",
        we_dry, SR)
    write_wav(
        "output_play/diag_we_hall.wav",
        we_hall, SR)
    write_wav(
        "output_play/diag_we_slow.wav",
        ola_stretch(we_dry, 4.0), SR)

    print()
    print("  diag_we_full.wav")
    print("  diag_we_hall.wav")
    print("  diag_we_slow.wav")
    print(f"  {'PASSED' if d3 else 'FAILED'}")
    print()

    # ══════════════════════════════════════
    # D4 — PERCEPTUAL CONTRAST
    # ══════════════════════════════════════

    print("─" * 60)
    print("DIAGNOSTIC 4 — [weː] vs modern [wiː]")
    print()

    # Synthesize modern "we" [wiː] for contrast
    # using v17 if available
    modern_we = None
    try:
        from voice_physics_v17 import \
            synth_phrase
        modern_raw = f32(synth_phrase(
            [('we', ['W', 'IY'])],
            punctuation='.'))
        modern_we = f32(modern_raw / (
            np.max(np.abs(modern_raw))
            +1e-8) * 0.75)
        print("  Modern 'we': v17 engine")
    except ImportError:
        print("  Modern 'we': not available")
        print("  (install voice_physics_v17)")

    we_n = f32(we_dry / (
        np.max(np.abs(we_dry))+1e-8) * 0.75)

    if modern_we is not None:
        contrast = np.concatenate([
            we_n, pause, modern_we, pause,
            we_n, pause, modern_we])
        write_wav(
            "output_play/diag_we_vs_modern.wav",
            f32(contrast / (
                np.max(np.abs(contrast))
                +1e-8) * 0.80), SR)
        print("  diag_we_vs_modern.wav")
        print("  Old English [weː] vs"
              " modern English [wiː]")
        print("  Listen for: F1 difference")
        print("    [eː] should sound more open")
        print("    than modern 'we'")
        print("    Like German 'See' not"
              " English 'see'")

    print()
    print("  PLAY ORDER:")
    print("  afplay output_play/"
          "diag_w_onset_slow.wav")
    print("  afplay output_play/"
          "diag_e_vowel_slow.wav")
    print("  afplay output_play/"
          "diag_we_slow.wav")
    if modern_we is not None:
        print("  afplay output_play/"
              "diag_we_vs_modern.wav")
    print("  afplay output_play/"
          "diag_we_hall.wav")
    print()

    # ══════════════════════════════════════
    # SUMMARY
    # ══════════════════════════════════════

    print("=" * 60)
    print("SUMMARY")
    print()
    rows = [
        ("D1 W onset",    d1),
        ("D2 Ē vowel",    d2),
        ("D3 Full word",  d3),
    ]
    for lbl, ok_ in rows:
        sym = "✓ PASS" if ok_ else "✗ FAIL"
        print(f"  {lbl:22s}  {sym}")
    print(f"  {'D4 Perceptual':22s}  LISTEN")
    print()

    if all_pass:
        print("  ALL NUMERIC CHECKS PASSED")
        print()
        print("  afplay output_play/we_hall.wav")
        print("  afplay output_play/we_slow.wav")
        print("  afplay output_play/"
              "we_performance.wav")
    else:
        failed = [l for l, ok_ in rows
                  if not ok_]
        print(f"  FAILED: {', '.join(failed)}")
        if not d2:
            print()
            print("  D2 GUIDANCE:")
            if peaks:
                low = [p for p in peaks
                       if p < 380]
                tgt = [p for p in peaks
                       if 380 <= p <= 520]
                hi_ = [p for p in peaks
                       if p > 520]
                print(f"    sub-380: {low}")
                print(f"    F1 zone: {tgt}")
                print(f"    above-520: {hi_}")
                if not tgt:
                    if hi_:
                        print(f"    F1 too high"
                              f" ({hi_[0]:.0f} Hz)")
                        print(f"    Raise E_F[0]"
                              f" toward 420 Hz")
                    elif low:
                        print(f"    F1 too low"
                              f" ({low[0]:.0f} Hz)")
                        print(f"    Lower E_F[0]"
                              f" toward 420 Hz")
        if not d1:
            print()
            print("  D1 GUIDANCE:")
            print("  W voicing too low.")
            print("  Check Rosenberg source"
                  " is active.")
            print("  W_GAINS[0] may need raising.")

    print()
    print("=" * 60)
    return all_pass


if __name__ == "__main__":
    print()
    passed = run_diagnostics()
    import sys
    sys.exit(0 if passed else 1)
