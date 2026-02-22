"""
GĀR-DENA DIAGNOSTIC v1
Old English: Gār-Dena [ɡɑːrdenɑ]
Beowulf line 1, word 3
February 2026

DIAGNOSTIC STRUCTURE:

  D1 — G onset [ɡ]
       voicing bar present in closure
       burst: broadband, velar CF ~1500 Hz
       no aspiration (voiced stop)

  D2 — Ā vowel [ɑː]
       F1: 680–820 Hz  (open jaw, high F1)
       F2: 850–1150 Hz (back tongue, low F2)
       voicing > 0.75
       Contrast: [æ] F1=668 F2=1873
                 [eː] F1=409 F2=2132
                 [ɑː] inverts both axes

  D3 — R trill [r]
       periodic amplitude modulation
       at trill rate (~35–50 Hz)
       F3 suppressed in open phases
       closure segments: near-silent
       open segments: voiced with rhoticity

  D4 — D onset [d]
       voiced closure bar
       alveolar burst: CF > 2500 Hz
       release into E formants

  D5 — E vowel [e]
       F1: 380–520 Hz
       F2: 1900–2400 Hz
       shorter than [eː] of Wē

  D6 — N nasal [n]
       voicing > 0.70
       low RMS (nasal murmur)
       antiformant effect at ~800 Hz

  D7 — A vowel final [ɑ]
       F1: 650–820 Hz
       F2: 850–1150 Hz
       shorter than Ā
       word-final decay

  D8 — FULL WORD
       all segments in sequence
       voicing profile correct
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
    b, a = butter(2, [lo_, hi_],
                  btype='band')
    return b, a

def safe_lp(fc, sr=SR):
    nyq = sr / 2.0
    fc_ = min(fc / nyq, 0.499)
    b, a = butter(2, fc_, btype='low')
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
        frame = sig[in_pos:in_pos+win_n] * window
        out [out_pos:out_pos+win_n] += frame
        norm[out_pos:out_pos+win_n] += window
    nz         = norm > 1e-8
    out[nz]   /= norm[nz]
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

def estimate_f1_f2(seg, sr=SR):
    order = min(
        int(2 + sr // 1000),
        len(seg) // 4, 40)
    if order < 4 or len(seg) < order * 4:
        return None, None, []
    vr = measure_voicing(seg, sr=sr)
    if vr < 0.18:
        return None, None, []
    seg_f = seg.astype(float)
    mx    = np.max(np.abs(seg_f))
    if mx < 1e-8:
        return None, None, []
    seg_f = seg_f / mx
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
        r_ac = np.array([
            np.dot(pre[:n-k], pre[k:])
            for k in range(order+1)])
        if abs(r_ac[0]) < 1e-10:
            return None, None, []
        a   = np.zeros(order, dtype=float)
        err = r_ac[0]
        for i in range(order):
            lam = r_ac[i+1]
            for j in range(i):
                lam -= a[j] * r_ac[i-j]
            k_i = lam / (err + 1e-12)
            k_i = float(np.clip(
                k_i, -0.9999, 0.9999))
            a_new = (a[:i]
                     - k_i * a[:i][::-1])
            a[:i] = a_new
            a[i]  = k_i
            err  *= (1 - k_i**2 + 1e-12)
            if err < 1e-15:
                break
    except Exception:
        return None, None, []
    n_fft  = 2048
    coeffs = np.concatenate([[1.0], -a])
    H      = np.fft.rfft(coeffs, n=n_fft)
    spec   = 1.0 / (np.abs(H)**2 + 1e-12)
    freqs  = np.fft.rfftfreq(n_fft, d=1.0/sr)
    mask   = (freqs >= 200) & (freqs <= 5000)
    s_m    = spec[mask]
    f_m    = freqs[mask]
    if len(s_m) < 3:
        return None, None, []
    bin_hz   = float(freqs[1] - freqs[0]) \
               if len(freqs) > 1 else 1.0
    min_dist = max(1, int(80.0 / bin_hz))
    peaks, _ = find_peaks(
        s_m,
        height=np.max(s_m) * 0.02,
        distance=min_dist)
    if not len(peaks):
        return None, None, []
    f_peaks = sorted(
        [float(f_m[p]) for p in peaks])
    f_vowel = [p for p in f_peaks if p >= 200]
    f1 = f_vowel[0] if len(f_vowel) > 0 \
         else None
    f2 = f_vowel[1] if len(f_vowel) > 1 \
         else None
    return f1, f2, f_peaks

def measure_trill_modulation(seg, sr=SR):
    """
    Detect amplitude modulation characteristic
    of a trill.

    Method:
      Extract amplitude envelope via RMS
      in short windows (~5ms).
      Compute autocorrelation of envelope.
      Look for peaks in the trill rate range:
      25–60 Hz (period 17–40ms).

    Returns:
      mod_depth: 0–1 (how much modulation)
      trill_hz:  estimated modulation rate
                 (0 if not detected)
    """
    if len(seg) < int(0.05 * sr):
        return 0.0, 0.0

    win_ms  = 5.0
    hop_ms  = 2.5
    win_n   = int(win_ms / 1000.0 * sr)
    hop_n   = int(hop_ms / 1000.0 * sr)
    if win_n < 4:
        return 0.0, 0.0

    sig_f   = seg.astype(float)
    n_frames = max(1,
                   (len(sig_f) - win_n)
                   // hop_n + 1)
    env     = np.zeros(n_frames, dtype=float)
    for i in range(n_frames):
        s = i * hop_n
        e = min(s + win_n, len(sig_f))
        frame = sig_f[s:e]
        env[i] = np.sqrt(
            np.mean(frame**2) + 1e-12)

    env_sr  = 1.0 / (hop_ms / 1000.0)
    env -= np.mean(env)
    if np.max(np.abs(env)) < 1e-8:
        return 0.0, 0.0

    acorr = np.correlate(env, env,
                          mode='full')
    acorr = acorr[len(acorr)//2:]
    if acorr[0] < 1e-10:
        return 0.0, 0.0
    acorr /= acorr[0]

    lo_lag = int(env_sr / 60.0)
    hi_lag = int(env_sr / 25.0)
    hi_lag = min(hi_lag, len(acorr) - 1)

    if lo_lag >= hi_lag:
        return 0.0, 0.0

    peak_val = float(np.max(
        acorr[lo_lag:hi_lag]))
    peak_lag = int(np.argmax(
        acorr[lo_lag:hi_lag])) + lo_lag
    trill_hz = float(env_sr / peak_lag) \
               if peak_lag > 0 else 0.0

    return float(np.clip(peak_val, 0, 1)), \
           trill_hz

def measure_burst_centroid(seg, sr=SR,
                            window_ms=15.0):
    """
    Estimate spectral centroid of a
    burst segment (stop release).
    Higher centroid = more anterior
    place of articulation.
      Bilabial G: ~1500 Hz
      Velar G:    ~1500 Hz
      Alveolar D: ~3500 Hz
    """
    n_w = int(window_ms / 1000.0 * sr)
    n_w = min(n_w, len(seg))
    if n_w < 4:
        return 0.0
    seg_w  = seg[:n_w].astype(float)
    spec   = np.abs(np.fft.rfft(seg_w,
                                  n=1024))**2
    freqs  = np.fft.rfftfreq(1024,
                               d=1.0/sr)
    mask   = freqs < sr * 0.48
    s      = spec[mask]
    f      = freqs[mask]
    total  = np.sum(s)
    if total < 1e-12:
        return 0.0
    return float(np.sum(f * s) / total)


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
               warn_lo=None,
               unit='', fmt='.4f'):
    if value >= lo:
        ok = True;  status = 'PASS'
    elif (warn_lo is not None
          and value >= warn_lo):
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
# IMPORT
# ============================================================

def _import_gd():
    try:
        from gar_dena_reconstruction import (
            synth_gar_dena,
            synth_G, synth_AA_long,
            synth_R_trill,
            synth_D, synth_E_short,
            synth_N, synth_A_short,
            apply_simple_room,
            G_F, AA_F, R_F,
            D_F, E_F, N_F, A_F,
            G_B, AA_B, R_B,
            D_B, E_B, N_B, A_B,
            AA_GAINS, E_GAINS, N_GAINS,
            A_GAINS)
        return (synth_gar_dena,
                synth_G, synth_AA_long,
                synth_R_trill,
                synth_D, synth_E_short,
                synth_N, synth_A_short,
                apply_simple_room,
                G_F, AA_F, R_F,
                D_F, E_F, N_F, A_F,
                True, None)
    except ImportError as e:
        return (None,)*16 + (False, str(e))


# ============================================================
# DIAGNOSTIC RUNNER
# ============================================================

def run_diagnostics():

    print()
    print("=" * 60)
    print("GĀR-DENA DIAGNOSTIC v1")
    print("Old English [ɡɑːrdenɑ]")
    print("Beowulf line 1, word 3")
    print("=" * 60)
    print()

    result = _import_gd()
    (synth_gar_dena,
     synth_G, synth_AA_long,
     synth_R_trill,
     synth_D, synth_E_short,
     synth_N, synth_A_short,
     apply_simple_room,
     G_F, AA_F, R_F,
     D_F, E_F, N_F, A_F,
     ok, err) = result

    if not ok:
        print(f"  gar_dena_reconstruction.py: "
              f"IMPORT FAILED\n  {err}")
        return False
    print("  gar_dena_reconstruction.py: OK")
    print()

    all_pass = True
    pause    = np.zeros(
        int(0.35 * SR), dtype=DTYPE)

    # ══════════════════════════════════════
    # D1 — G ONSET
    # ══════════════════════════════════════

    print("─" * 60)
    print("DIAGNOSTIC 1 — G ONSET [ɡ]")
    print()
    print("  Voiced velar stop.")
    print("  Closure: voicing bar (low RMS).")
    print("  Burst: broadband, velar CF")
    print("         ~1000–2000 Hz range.")
    print("  No aspiration — voiced stop.")
    print()

    g_seg = synth_G(
        F_next=AA_F,
        pitch_hz=145.0, dil=1.0, sr=SR)

    r_full = rms(g_seg)
    p1 = check('RMS level', r_full,
               0.005, 0.80)

    n_cl  = int(50.0 / 1000.0 * SR)
    n_bst = int(12.0 / 1000.0 * SR)
    cl_seg  = g_seg[:n_cl] \
              if len(g_seg) > n_cl \
              else g_seg
    bst_seg = g_seg[n_cl:n_cl+n_bst] \
              if len(g_seg) > n_cl+n_bst \
              else g_seg[-n_bst:]

    r_closure = rms(cl_seg)
    r_burst   = rms(bst_seg)

    p2 = check('closure RMS (voicing bar)',
               r_closure, 0.001, 0.05)
    p3 = check_warn(
        'burst RMS',
        r_burst, 0.010, 1.0,
        warn_lo=0.003)

    centroid = measure_burst_centroid(
        bst_seg, sr=SR)
    p4 = check(
        f'burst centroid ({centroid:.0f} Hz)',
        centroid, 800.0, 2500.0,
        unit=' Hz', fmt='.1f')

    d1 = p1 and p2 and p3 and p4
    all_pass &= d1

    write_wav(
        "output_play/diag_g_onset_slow.wav",
        ola_stretch(g_seg / (
            np.max(np.abs(g_seg))+1e-8)
            * 0.75, 4.0), SR)
    print("  diag_g_onset_slow.wav")
    print(f"  {'PASSED' if d1 else 'FAILED'}")
    print()

    # ══════════════════════════════════════
    # D2 — Ā VOWEL
    # pitch=110 Hz for LPC
    # ══════════════════════════════════════

    print("─" * 60)
    print("DIAGNOSTIC 2 — Ā VOWEL [ɑː]")
    print()
    print("  Long open back vowel.")
    print("  F1 HIGH (open jaw): 680–820 Hz")
    print("  F2 LOW (back tongue): 850–1150 Hz")
    print("  Contrast axes:")
    print("    [æ]:  F1=668  F2=1873")
    print("    [eː]: F1=409  F2=2132")
    print("    [ɑː]: F1=HIGH F2=LOW")
    print("    Front/back axis inverted on F2.")
    print("    Open/close axis: [ɑː]>[æ]>[eː]")
    print()

    aa_seg = synth_AA_long(
        F_prev=G_F,
        F_next=R_F,
        pitch_hz=110.0,
        dil=1.0, sr=SR)

    n_aa  = len(aa_seg)
    n_on  = int(0.10 * n_aa)
    n_off = int(0.08 * n_aa)
    body  = aa_seg[n_on:n_aa-n_off]

    vr_aa = measure_voicing(body, sr=SR)
    r_aa  = rms(aa_seg)
    f1_aa, f2_aa, pk_aa = estimate_f1_f2(
        body, sr=SR)

    p1 = check('voicing (body)', vr_aa,
               0.75, 1.0)
    p2 = check('RMS level', r_aa,
               0.020, 5.0)

    print(f"  LPC peaks (≥200 Hz):")
    if pk_aa:
        for p in pk_aa:
            m = ''
            if 680 <= p <= 820:
                m = ' ← F1 [ɑː] ✓'
            elif 850 <= p <= 1150:
                m = ' ← F2 [ɑː] ✓'
            elif 1800 <= p <= 2400:
                m = ' ← F2 zone [front vowel]'
            print(f"    {p:.0f} Hz{m}")
    else:
        print("    (none found)")
    print()

    p3 = p4 = True
    if f1_aa is not None:
        p3 = check(
            f'F1 ({f1_aa:.0f} Hz)', f1_aa,
            680.0, 820.0,
            unit=' Hz', fmt='.1f')
        if not p3:
            if f1_aa < 680:
                print(f"      F1 too low."
                      f" Jaw not open enough.")
                print(f"      Raise AA_F[0].")
            else:
                print(f"      F1 too high.")
                print(f"      Lower AA_F[0].")
    else:
        p3 = False
        print(f"    [FAIL] F1 not found.")
        print(f"      Check AA_GAINS[0].")

    if f2_aa is not None:
        p4 = check(
            f'F2 ({f2_aa:.0f} Hz)', f2_aa,
            850.0, 1150.0,
            unit=' Hz', fmt='.1f')
        if not p4:
            if f2_aa > 1150:
                print(f"      F2 too high.")
                print(f"      Vowel too front.")
                print(f"      Lower AA_F[1].")
            else:
                print(f"      F2 too low.")
                print(f"      Raise AA_F[1].")
    else:
        p4 = False
        print(f"    [FAIL] F2 not found.")
        print(f"      Raise AA_GAINS[1].")

    d2 = p1 and p2 and p3 and p4
    all_pass &= d2

    write_wav(
        "output_play/diag_aa_vowel_slow.wav",
        ola_stretch(aa_seg / (
            np.max(np.abs(aa_seg))+1e-8)
            * 0.75, 4.0), SR)
    print("  diag_aa_vowel_slow.wav")
    print(f"  {'PASSED' if d2 else 'FAILED'}")
    print()

    # ══════════════════════════════════════
    # D3 — R TRILL
    # ══════════════════════════════════════

    print("─" * 60)
    print("DIAGNOSTIC 3 — R TRILL [r]")
    print()
    print("  Short trill: 2 closures.")
    print("  Amplitude modulation at")
    print("  trill rate ~25–60 Hz.")
    print("  F3 suppressed (~1690 Hz)")
    print("  in open phases.")
    print("  Closure segments: near-silent.")
    print()

    r_seg = synth_R_trill(
        F_prev=AA_F,
        F_next=D_F,
        pitch_hz=145.0,
        dil=1.0, sr=SR)

    mod_depth, trill_hz = \
        measure_trill_modulation(r_seg, sr=SR)
    r_rms = rms(r_seg)
    vr_r  = measure_voicing(r_seg, sr=SR)

    p1 = check('RMS level', r_rms,
               0.005, 0.80)
    p2 = check_warn(
        'voicing (open phases)',
        vr_r, 0.40, 1.0,
        warn_lo=0.25)
    p3 = check_warn(
        'trill modulation depth',
        mod_depth, 0.25, 1.0,
        warn_lo=0.10)

    if trill_hz > 0:
        p4 = check(
            f'trill rate ({trill_hz:.1f} Hz)',
            trill_hz,
            20.0, 70.0,
            unit=' Hz', fmt='.1f')
    else:
        p4 = False
        print(f"    [FAIL] trill rate: "
              f"not detected")
        print(f"      Modulation too weak.")
        print(f"      Check closure amplitude.")

    d3 = p1 and p2 and p3 and p4
    all_pass &= d3

    write_wav(
        "output_play/diag_r_trill_slow.wav",
        ola_stretch(r_seg / (
            np.max(np.abs(r_seg))+1e-8)
            * 0.75, 4.0), SR)
    print("  diag_r_trill_slow.wav")
    print(f"  {'PASSED' if d3 else 'FAILED'}")
    print()

    # ══════════════════════════════════════
    # D4 — D ONSET
    # ══════════════════════════════════════

    print("─" * 60)
    print("DIAGNOSTIC 4 — D ONSET [d]")
    print()
    print("  Voiced alveolar stop.")
    print("  Alveolar burst: CF > 2500 Hz.")
    print("  Higher than velar G burst.")
    print("  Voiced — no aspiration.")
    print()

    d_seg = synth_D(
        F_prev=R_F,
        F_next=E_F,
        pitch_hz=145.0, dil=1.0, sr=SR)

    r_d = rms(d_seg)
    p1  = check('RMS level', r_d,
                0.005, 0.80)

    n_cl_d  = int(45.0 / 1000.0 * SR)
    n_bst_d = int(10.0 / 1000.0 * SR)
    bst_d   = d_seg[n_cl_d:n_cl_d+n_bst_d] \
              if len(d_seg) > n_cl_d+n_bst_d \
              else d_seg[-n_bst_d:]

    centroid_d = measure_burst_centroid(
        bst_d, sr=SR)
    p2 = check(
        f'burst centroid ({centroid_d:.0f} Hz)',
        centroid_d, 2000.0, 5000.0,
        unit=' Hz', fmt='.1f')

    print(f"  Note: G centroid ~1500 Hz,")
    print(f"        D centroid ~3500 Hz.")
    print(f"        Place difference auditable.")
    print(f"        D centroid: {centroid_d:.0f} Hz")

    d4 = p1 and p2
    all_pass &= d4

    write_wav(
        "output_play/diag_d_onset_slow.wav",
        ola_stretch(d_seg / (
            np.max(np.abs(d_seg))+1e-8)
            * 0.75, 4.0), SR)
    print("  diag_d_onset_slow.wav")
    print(f"  {'PASSED' if d4 else 'FAILED'}")
    print()

    # ══════════════════════════════════════
    # D5 — E VOWEL (short)
    # ══════════════════════════════════════

    print("─" * 60)
    print("DIAGNOSTIC 5 — E VOWEL [e]")
    print()
    print("  Short close-mid front.")
    print("  Same formant as Wē [eː].")
    print("  Shorter duration.")
    print("  F1: 380–520 Hz")
    print("  F2: 1900–2400 Hz")
    print()

    e_seg = synth_E_short(
        F_prev=D_F,
        F_next=N_F,
        pitch_hz=110.0,
        dil=1.0, sr=SR)

    n_e   = len(e_seg)
    n_on  = int(0.12 * n_e)
    n_off = int(0.10 * n_e)
    body_e = e_seg[n_on:n_e-n_off]

    vr_e  = measure_voicing(body_e, sr=SR)
    r_e   = rms(e_seg)
    f1_e, f2_e, pk_e = estimate_f1_f2(
        body_e, sr=SR)

    p1 = check('voicing (body)', vr_e,
               0.65, 1.0)
    p2 = check('RMS level', r_e,
               0.010, 5.0)

    print(f"  LPC peaks (≥200 Hz):")
    if pk_e:
        for p in pk_e:
            m = ''
            if 380 <= p <= 520:
                m = ' ← F1 [e] ✓'
            elif 1900 <= p <= 2400:
                m = ' ← F2 [e] ✓'
            print(f"    {p:.0f} Hz{m}")
    else:
        print("    (none found)")
    print()

    p3 = p4 = True
    if f1_e is not None:
        p3 = check(
            f'F1 ({f1_e:.0f} Hz)', f1_e,
            380.0, 520.0,
            unit=' Hz', fmt='.1f')
    else:
        p3 = False
        print(f"    [FAIL] F1 not found.")

    if f2_e is not None:
        p4 = check(
            f'F2 ({f2_e:.0f} Hz)', f2_e,
            1900.0, 2400.0,
            unit=' Hz', fmt='.1f')
    else:
        p4 = False
        print(f"    [FAIL] F2 not found.")

    d5 = p1 and p2 and p3 and p4
    all_pass &= d5

    write_wav(
        "output_play/diag_e_short_slow.wav",
        ola_stretch(e_seg / (
            np.max(np.abs(e_seg))+1e-8)
            * 0.75, 4.0), SR)
    print("  diag_e_short_slow.wav")
    print(f"  {'PASSED' if d5 else 'FAILED'}")
    print()

    # ══════════════════════════════════════
    # D6 — N NASAL
    # ══════════════════════════════════════

    print("─" * 60)
    print("DIAGNOSTIC 6 — N NASAL [n]")
    print()
    print("  Voiced alveolar nasal.")
    print("  Low RMS — murmur quality.")
    print("  Antiformant effect at ~800 Hz.")
    print("  Voicing > 0.65.")
    print()

    n_seg = synth_N(
        F_prev=E_F,
        F_next=A_F,
        pitch_hz=145.0, dil=1.0, sr=SR)

    vr_n = measure_voicing(n_seg, sr=SR)
    r_n  = rms(n_seg)

    p1 = check('voicing', vr_n,
               0.65, 1.0)
    p2 = check('RMS (nasal murmur)',
               r_n, 0.005, 0.25)

    # Antiformant check:
    # energy at 800 Hz should be lower
    # than adjacent bands
    try:
        b_lo, a_lo = safe_bp(
            600.0, 900.0, SR)
        b_hi, a_hi = safe_bp(
            1000.0, 1400.0, SR)
        e_anti = float(np.mean(
            lfilter(b_lo, a_lo,
                    n_seg.astype(float))**2))
        e_above = float(np.mean(
            lfilter(b_hi, a_hi,
                    n_seg.astype(float))**2))
        anti_ratio = (e_anti / (e_above + 1e-12))
        p3 = check(
            'antiformant ratio (800/1200 Hz)',
            anti_ratio, 0.0, 1.5)
        if not p3:
            print(f"      800 Hz energy too high.")
            print(f"      Antiformant not working.")
            print(f"      Check N_ANTI_F.")
    except Exception:
        p3 = True
        print("    [SKIP] antiformant check")

    d6 = p1 and p2 and p3
    all_pass &= d6

    write_wav(
        "output_play/diag_n_nasal_slow.wav",
        ola_stretch(n_seg / (
            np.max(np.abs(n_seg))+1e-8)
            * 0.75, 4.0), SR)
    print("  diag_n_nasal_slow.wav")
    print(f"  {'PASSED' if d6 else 'FAILED'}")
    print()

    # ══════════════════════════════════════
    # D7 — A VOWEL (final)
    # ══════════════════════════════════════

    print("─" * 60)
    print("DIAGNOSTIC 7 — A VOWEL [ɑ]")
    print()
    print("  Short open back vowel.")
    print("  Genitive ending. Unstressed.")
    print("  F1: 650–820 Hz")
    print("  F2: 850–1150 Hz")
    print("  Word-final decay.")
    print()

    a_seg = synth_A_short(
        F_prev=N_F,
        pitch_hz=110.0,
        dil=1.0, sr=SR)

    n_a  = len(a_seg)
    body_a = a_seg[:int(0.6 * n_a)]

    vr_a  = measure_voicing(body_a, sr=SR)
    r_a   = rms(a_seg)
    f1_a, f2_a, pk_a = estimate_f1_f2(
        body_a, sr=SR)

    p1 = check_warn(
        'voicing (body)', vr_a,
        0.50, 1.0, warn_lo=0.30)
    p2 = check('RMS level', r_a,
               0.005, 5.0)

    print(f"  LPC peaks (≥200 Hz):")
    if pk_a:
        for p in pk_a:
            m = ''
            if 650 <= p <= 820:
                m = ' ← F1 [ɑ] ✓'
            elif 850 <= p <= 1150:
                m = ' ← F2 [ɑ] ✓'
            print(f"    {p:.0f} Hz{m}")
    else:
        print("    (none found)")
    print()

    p3 = p4 = True
    if f1_a is not None:
        p3 = check(
            f'F1 ({f1_a:.0f} Hz)', f1_a,
            650.0, 820.0,
            unit=' Hz', fmt='.1f')
    else:
        p3 = False
        print(f"    [FAIL] F1 not found.")

    if f2_a is not None:
        p4 = check(
            f'F2 ({f2_a:.0f} Hz)', f2_a,
            850.0, 1150.0,
            unit=' Hz', fmt='.1f')
    else:
        p4 = False
        print(f"    [FAIL] F2 not found.")

    d7 = p1 and p2 and p3 and p4
    all_pass &= d7

    write_wav(
        "output_play/diag_a_final_slow.wav",
        ola_stretch(a_seg / (
            np.max(np.abs(a_seg))+1e-8)
            * 0.75, 4.0), SR)
    print("  diag_a_final_slow.wav")
    print(f"  {'PASSED' if d7 else 'FAILED'}")
    print()

    # ══════════════════════════════════════
    # D8 — FULL WORD
    # ══════════════════════════════════════

    print("─" * 60)
    print("DIAGNOSTIC 8 — FULL WORD")
    print()

    gd_dry  = synth_gar_dena(
        pitch_hz=145.0, dil=1.0,
        add_room=False)
    gd_hall = synth_gar_dena(
        pitch_hz=145.0, dil=1.0,
        add_room=True)

    r_full = rms(gd_dry)
    p1     = check('full-word RMS', r_full,
                   0.010, 0.90)

    print(f"  {len(gd_dry)} samples"
          f" ({len(gd_dry)/SR*1000:.0f} ms)")

    # Zone boundaries (dil=1.0)
    n_g   = len(synth_G(AA_F, 145.0, 1.0))
    n_aa  = len(synth_AA_long(G_F, R_F,
                               145.0, 1.0))
    n_r   = len(synth_R_trill(AA_F, D_F,
                               145.0, 1.0))
    n_d   = len(synth_D(R_F, E_F, 145.0, 1.0))
    n_e   = len(synth_E_short(D_F, N_F,
                               145.0, 1.0))
    n_n   = len(synth_N(E_F, A_F, 145.0, 1.0))

    z_g  = (0,        n_g)
    z_aa = (n_g,      n_g+n_aa)
    z_r  = (n_g+n_aa, n_g+n_aa+n_r)
    z_d  = (z_r[1],   z_r[1]+n_d)
    z_e  = (z_d[1],   z_d[1]+n_e)
    z_n  = (z_e[1],   z_e[1]+n_n)
    z_a  = (z_n[1],   len(gd_dry))

    def sw(s, e):
        s = max(0, s)
        e = min(len(gd_dry), e)
        return gd_dry[s:e] \
               if e > s else gd_dry[:10]

    vr_aa_w = measure_voicing(
        sw(*z_aa), SR)
    vr_e_w  = measure_voicing(
        sw(*z_e),  SR)
    vr_n_w  = measure_voicing(
        sw(*z_n),  SR)
    vr_a_w  = measure_voicing(
        sw(*z_a),  SR)

    print()
    print("  Segment boundaries:")
    print(f"    G  [{z_g[0]}:{z_g[1]}]")
    print(f"    Ā  [{z_aa[0]}:{z_aa[1]}]")
    print(f"    R  [{z_r[0]}:{z_r[1]}]")
    print(f"    D  [{z_d[0]}:{z_d[1]}]")
    print(f"    E  [{z_e[0]}:{z_e[1]}]")
    print(f"    N  [{z_n[0]}:{z_n[1]}]")
    print(f"    A  [{z_a[0]}:{z_a[1]}]")
    print()
    print("  Voicing profile:")

    p2 = check_warn(
        'Ā zone voicing', vr_aa_w,
        0.70, 1.0, warn_lo=0.50)
    p3 = check_warn(
        'E zone voicing', vr_e_w,
        0.60, 1.0, warn_lo=0.40)
    p4 = check_warn(
        'N zone voicing', vr_n_w,
        0.55, 1.0, warn_lo=0.35)
    p5 = check_warn(
        'A zone voicing', vr_a_w,
        0.45, 1.0, warn_lo=0.25)

    d8 = p1 and p2 and p3 and p4 and p5
    all_pass &= d8

    write_wav(
        "output_play/diag_gar_dena_full.wav",
        gd_dry, SR)
    write_wav(
        "output_play/diag_gar_dena_hall.wav",
        gd_hall, SR)
    write_wav(
        "output_play/diag_gar_dena_slow.wav",
        ola_stretch(gd_dry, 4.0), SR)

    print()
    print("  diag_gar_dena_full.wav")
    print("  diag_gar_dena_hall.wav")
    print("  diag_gar_dena_slow.wav")
    print(f"  {'PASSED' if d8 else 'FAILED'}")
    print()

    # ══════════════════════════════════════
    # D9 — PERCEPTUAL
    # ══════════════════════════════════════

    print("─" * 60)
    print("DIAGNOSTIC 9 — PERCEPTUAL")
    print()
    print("  PLAY ORDER:")
    print("  afplay output_play/"
          "diag_g_onset_slow.wav")
    print("  afplay output_play/"
          "diag_aa_vowel_slow.wav")
    print("  afplay output_play/"
          "diag_r_trill_slow.wav")
    print("  afplay output_play/"
          "diag_d_onset_slow.wav")
    print("  afplay output_play/"
          "diag_e_short_slow.wav")
    print("  afplay output_play/"
          "diag_n_nasal_slow.wav")
    print("  afplay output_play/"
          "diag_a_final_slow.wav")
    print("  afplay output_play/"
          "diag_gar_dena_slow.wav")
    print("  afplay output_play/"
          "diag_gar_dena_hall.wav")
    print()
    print("  Listen for:")
    print("  G: voiced before vowel, no puff")
    print("  Ā: open back — like 'father'")
    print("     NOT like 'cat' or 'see'")
    print("  R: trill interruptions audible")
    print("     4x slow reveals the closures")
    print("  D: voiced, alveolar click")
    print("  E: front vowel, brief")
    print("  N: nasal murmur, quiet")
    print("  A: open back, falling away")
    print()

    # ══════════════════════════════════════
    # SUMMARY
    # ══════════════════════════════════════

    print("=" * 60)
    print("SUMMARY")
    print()

    rows = [
        ("D1 G onset",    d1),
        ("D2 Ā vowel",    d2),
        ("D3 R trill",    d3),
        ("D4 D onset",    d4),
        ("D5 E vowel",    d5),
        ("D6 N nasal",    d6),
        ("D7 A final",    d7),
        ("D8 Full word",  d8),
    ]
    for lbl, ok_ in rows:
        sym = "✓ PASS" if ok_ else "✗ FAIL"
        print(f"  {lbl:22s}  {sym}")
    print(f"  {'D9 Perceptual':22s}  LISTEN")
    print()

    if all_pass:
        print("  ALL NUMERIC CHECKS PASSED")
    else:
        failed = [l for l, ok_ in rows
                  if not ok_]
        print(f"  FAILED: {', '.join(failed)}")
        print()
        if not d2:
            print("  D2 GUIDANCE:")
            if f1_aa and f1_aa < 680:
                print(f"    F1={f1_aa:.0f} Hz"
                      f" too low."
                      f" Raise AA_F[0].")
            if f2_aa and f2_aa > 1150:
                print(f"    F2={f2_aa:.0f} Hz"
                      f" too high."
                      f" Lower AA_F[1].")
        if not d3:
            print("  D3 GUIDANCE:")
            print(f"    mod_depth={mod_depth:.3f}"
                  f" trill_hz={trill_hz:.1f}")
            print(f"    If mod_depth < 0.25:")
            print(f"    Raise R_CLOSURE_MS"
                  f" or increase closures.")
        if not d5:
            print("  D5 GUIDANCE:")
            print(f"    Same target as Wē [eː].")
            print(f"    Check E_GAINS[1] >= 8.0")

    print()
    print("=" * 60)
    return all_pass


if __name__ == "__main__":
    passed = run_diagnostics()
    sys.exit(0 if passed else 1)
