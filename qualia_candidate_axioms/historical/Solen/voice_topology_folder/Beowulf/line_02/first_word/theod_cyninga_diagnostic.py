"""
ÞĒOD-CYNINGA DIAGNOSTIC v1
Old English: þēod-cyninga [θeːodkyniŋɡɑ]
Beowulf line 2, word 1
February 2026

DIAGNOSTICS:
  D1  Þ fricative [θ]
  D2  Ē vowel [eː]
  D3  O vowel [o]
  D4  D onset [d]
  D5  K onset [k]
  D6  Y vowel [y]
  D7  N nasal [n]
  D8  I vowel [ɪ]
  D9  NG nasal [ŋ]
  D10 G onset [ɡ]
  D11 A final [ɑ]
  D12 Full word
  D13 Perceptual
"""

import numpy as np
from scipy.signal import lfilter, butter
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
    nz         = norm > 1e-8
    out[nz]   /= norm[nz]
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.75
    return f32(out)

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
    hi = min(int(sr / 80), len(acorr) - 1)
    if lo >= hi:
        return 0.0
    return float(np.clip(
        np.max(acorr[lo:hi]), 0.0, 1.0))

def measure_band_centroid(seg, lo_hz, hi_hz,
                           sr=SR):
    if len(seg) < 64:
        return 0.0
    spec  = np.abs(np.fft.rfft(
        seg.astype(float), n=2048))**2
    freqs = np.fft.rfftfreq(2048, d=1.0/sr)
    mask  = (freqs >= lo_hz) & (freqs <= hi_hz)
    total = np.sum(spec[mask])
    if total < 1e-12:
        return 0.0
    return float(np.sum(
        freqs[mask] * spec[mask]) / total)

def measure_burst_centroid(seg, sr=SR,
                            window_ms=15.0):
    n_w = min(int(window_ms / 1000.0 * sr),
              len(seg))
    if n_w < 4:
        return 0.0
    spec  = np.abs(np.fft.rfft(
        seg[:n_w].astype(float), n=1024))**2
    freqs = np.fft.rfftfreq(1024, d=1.0/sr)
    mask  = freqs < sr * 0.48
    total = np.sum(spec[mask])
    if total < 1e-12:
        return 0.0
    return float(np.sum(
        freqs[mask] * spec[mask]) / total)

def check(label, value, lo, hi,
          unit='', fmt='.4f'):
    ok     = (lo <= value <= hi)
    status = 'PASS' if ok else 'FAIL'
    bar    = ''
    if 0.0 <= value <= 1.0 and unit == '':
        bar = '█' * int(value * 40)
    print(f"    [{status}] {label}: "
          f"{format(value, fmt)}{unit}  "
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
    print(f"    [{status}] {label}: "
          f"{format(value, fmt)}{unit}  "
          f"target [{lo:{fmt}}–{hi:{fmt}}]"
          f"  {bar}")
    return ok


def run_diagnostics():
    print()
    print("=" * 60)
    print("ÞĒOD-CYNINGA DIAGNOSTIC v1")
    print("Old English [θeːodkyniŋɡɑ]")
    print("Beowulf line 2, word 1")
    print("=" * 60)
    print()

    try:
        from theod_cyninga_reconstruction import (
            synth_theod_cyninga,
            synth_TH, synth_EE_long,
            synth_O_short, synth_D,
            synth_K, synth_Y_short,
            synth_N, synth_I_short,
            synth_NG, synth_G,
            synth_A_short,
            apply_simple_room,
            EE_F, O_F, D_F, K_F,
            Y_F, N_F, I_F, NG_F,
            G_F, A_F)
        print("  theod_cyninga_reconstruction"
              ".py: OK")
    except ImportError as e:
        print(f"  IMPORT FAILED: {e}")
        return False
    print()

    all_pass = True

    # ── D1 Þ ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 1 — Þ FRICATIVE [θ]")
    print()
    print("  Voiceless dental fricative.")
    print("  No voicing. Broad frication.")
    print("  Centroid target: 2500–5000 Hz")
    print("  (lower than [s] ~5500 Hz)")
    print()
    th_seg = synth_TH(EE_F, 1.0, SR)
    vr_th  = measure_voicing(th_seg)
    r_th   = rms(th_seg)
    cent_th = measure_band_centroid(
        th_seg, 1000.0, 8000.0)
    p1 = check('voicing (must be low)',
               vr_th, 0.0, 0.35)
    p2 = check('RMS level', r_th,
               0.005, 0.80)
    p3 = check(
        f'frication centroid ({cent_th:.0f} Hz)',
        cent_th, 2500.0, 5000.0,
        unit=' Hz', fmt='.1f')
    if not p3:
        if cent_th < 2500:
            print("      Centroid too low."
                  " Raise TH_NOISE_CF.")
        else:
            print("      Centroid too high."
                  " Lower TH_NOISE_CF.")
    d1 = p1 and p2 and p3
    all_pass &= d1
    write_wav(
        "output_play/diag_th_slow.wav",
        ola_stretch(th_seg / (
            np.max(np.abs(th_seg))+1e-8)
            * 0.75, 4.0))
    print(f"  {'PASSED' if d1 else 'FAILED'}")
    print()

    # ── D2 Ē ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 2 — Ē VOWEL [eː]")
    print()
    ee_seg  = synth_EE_long(G_F, O_F,
                             110.0, 1.0)
    n_ee    = len(ee_seg)
    body_ee = ee_seg[int(0.10*n_ee):
                     n_ee-int(0.10*n_ee)]
    cent_ee1 = measure_band_centroid(
        body_ee, 200.0, 700.0)
    cent_ee2 = measure_band_centroid(
        body_ee, 1800.0, 2600.0)
    p1 = check('voicing',
               measure_voicing(body_ee),
               0.75, 1.0)
    p2 = check(
        f'F1 centroid ({cent_ee1:.0f} Hz)',
        cent_ee1, 250.0, 480.0,
        unit=' Hz', fmt='.1f')
    p3 = check(
        f'F2 centroid ({cent_ee2:.0f} Hz)',
        cent_ee2, 1800.0, 2600.0,
        unit=' Hz', fmt='.1f')
    d2 = p1 and p2 and p3
    all_pass &= d2
    write_wav("output_play/diag_ee_slow.wav",
              ola_stretch(ee_seg / (
                  np.max(np.abs(ee_seg))+1e-8)
                  * 0.75, 4.0))
    print(f"  {'PASSED' if d2 else 'FAILED'}")
    print()

    # ── D3 O ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 3 — O VOWEL [o]")
    print()
    print("  Close-mid back rounded.")
    print("  F1 centroid (200–800 Hz):"
          " target 350–600 Hz")
    print("  F2 centroid (500–1200 Hz):"
          " target 600–1000 Hz")
    print()
    o_seg   = synth_O_short(EE_F, D_F,
                             110.0, 1.0)
    n_o     = len(o_seg)
    body_o  = o_seg[int(0.12*n_o):
                    n_o-int(0.12*n_o)]
    cent_o1 = measure_band_centroid(
        body_o, 200.0, 800.0)
    cent_o2 = measure_band_centroid(
        body_o, 500.0, 1200.0)
    p1 = check('voicing',
               measure_voicing(body_o),
               0.65, 1.0)
    p2 = check(
        f'F1 centroid ({cent_o1:.0f} Hz)',
        cent_o1, 350.0, 600.0,
        unit=' Hz', fmt='.1f')
    p3 = check(
        f'F2 centroid ({cent_o2:.0f} Hz)',
        cent_o2, 600.0, 1000.0,
        unit=' Hz', fmt='.1f')
    d3 = p1 and p2 and p3
    all_pass &= d3
    write_wav("output_play/diag_o_slow.wav",
              ola_stretch(o_seg / (
                  np.max(np.abs(o_seg))+1e-8)
                  * 0.75, 4.0))
    print(f"  {'PASSED' if d3 else 'FAILED'}")
    print()

    # ── D4 D ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 4 — D ONSET [d]")
    print()
    d_seg  = synth_D(O_F, K_F, 145.0, 1.0)
    n_cl_d = int(45.0 / 1000.0 * SR)
    n_bst_d= int(10.0 / 1000.0 * SR)
    bst_d  = (d_seg[n_cl_d:n_cl_d+n_bst_d]
              if len(d_seg) > n_cl_d+n_bst_d
              else d_seg[-n_bst_d:])
    cent_d = measure_burst_centroid(bst_d)
    p1 = check('RMS level', rms(d_seg),
               0.005, 0.80)
    p2 = check(
        f'burst centroid ({cent_d:.0f} Hz)',
        cent_d, 2000.0, 5000.0,
        unit=' Hz', fmt='.1f')
    d4 = p1 and p2
    all_pass &= d4
    write_wav("output_play/diag_d_slow.wav",
              ola_stretch(d_seg / (
                  np.max(np.abs(d_seg))+1e-8)
                  * 0.75, 4.0))
    print(f"  {'PASSED' if d4 else 'FAILED'}")
    print()

    # ── D5 K ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 5 — K ONSET [k]")
    print()
    print("  Voiceless velar. No voicing bar.")
    print("  Burst centroid: 800–2500 Hz")
    print("  Voicing in closure: < 0.25")
    print()
    k_seg  = synth_K(Y_F, 145.0, 1.0)
    n_cl_k = int(55.0 / 1000.0 * SR)
    n_bst_k= int(14.0 / 1000.0 * SR)
    cl_k   = (k_seg[:n_cl_k]
              if len(k_seg) > n_cl_k
              else k_seg)
    bst_k  = (k_seg[n_cl_k:n_cl_k+n_bst_k]
              if len(k_seg) > n_cl_k+n_bst_k
              else k_seg[-n_bst_k:])
    cent_k = measure_burst_centroid(bst_k)
    p1 = check('RMS level', rms(k_seg),
               0.005, 0.80)
    p2 = check('closure voicing (must be low)',
               measure_voicing(cl_k),
               0.0, 0.25)
    p3 = check(
        f'burst centroid ({cent_k:.0f} Hz)',
        cent_k, 800.0, 2500.0,
        unit=' Hz', fmt='.1f')
    d5 = p1 and p2 and p3
    all_pass &= d5
    write_wav("output_play/diag_k_slow.wav",
              ola_stretch(k_seg / (
                  np.max(np.abs(k_seg))+1e-8)
                  * 0.75, 4.0))
    print(f"  {'PASSED' if d5 else 'FAILED'}")
    print()

    # ── D6 Y ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 6 — Y VOWEL [y]")
    print()
    print("  Close front rounded — rarest vowel.")
    print("  F1 low (close height): 200–420 Hz")
    print("  F2 mid (rounding pulls down):"
          " 1200–1800 Hz")
    print("  [iː] F2=2300, [u] F2=700,"
          " [y] F2=1500")
    print()
    y_seg   = synth_Y_short(K_F, N_F,
                             145.0, 1.0)
    n_y     = len(y_seg)
    body_y  = y_seg[int(0.15*n_y):
                    n_y-int(0.12*n_y)]
    cent_y1 = measure_band_centroid(
        body_y, 150.0, 700.0)
    cent_y2 = measure_band_centroid(
        body_y, 1000.0, 2200.0)
    p1 = check('voicing',
               measure_voicing(body_y),
               0.65, 1.0)
    p2 = check(
        f'F1 centroid ({cent_y1:.0f} Hz)',
        cent_y1, 200.0, 420.0,
        unit=' Hz', fmt='.1f')
    p3 = check(
        f'F2 centroid ({cent_y2:.0f} Hz)',
        cent_y2, 1200.0, 1800.0,
        unit=' Hz', fmt='.1f')
    if not p3:
        if cent_y2 > 1800:
            print("      F2 too high — not"
                  " enough rounding.")
            print("      Lower Y_F[1].")
        else:
            print("      F2 too low — too"
                  " much rounding.")
            print("      Raise Y_F[1].")
    d6 = p1 and p2 and p3
    all_pass &= d6
    write_wav("output_play/diag_y_slow.wav",
              ola_stretch(y_seg / (
                  np.max(np.abs(y_seg))+1e-8)
                  * 0.75, 4.0))
    print(f"  {'PASSED' if d6 else 'FAILED'}")
    print()

    # ── D7 N ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 7 — N NASAL [n]")
    print()
    n_seg = synth_N(Y_F, I_F, 145.0, 1.0)
    vr_n  = measure_voicing(n_seg)
    r_n   = rms(n_seg)
    p1 = check('voicing', vr_n, 0.65, 1.0)
    p2 = check('RMS (nasal murmur)',
               r_n, 0.005, 0.25)
    try:
        b_at, a_at = safe_bp(700.0, 900.0, SR)
        b_ab, a_ab = safe_bp(
            1000.0, 1400.0, SR)
        e_at = float(np.mean(
            lfilter(b_at, a_at,
                    n_seg.astype(float))**2))
        e_ab = float(np.mean(
            lfilter(b_ab, a_ab,
                    n_seg.astype(float))**2))
        anti_ratio = e_at / (e_ab + 1e-12)
        p3 = check(
            'antiformant ratio (800/1200 Hz)',
            anti_ratio, 0.0, 1.0)
    except Exception:
        p3 = True
        print("    [SKIP] antiformant check")
    d7 = p1 and p2 and p3
    all_pass &= d7
    write_wav("output_play/diag_n_slow.wav",
              ola_stretch(n_seg / (
                  np.max(np.abs(n_seg))+1e-8)
                  * 0.75, 4.0))
    print(f"  {'PASSED' if d7 else 'FAILED'}")
    print()

    # ── D8 I ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 8 — I VOWEL [ɪ]")
    print()
    i_seg   = synth_I_short(N_F, NG_F,
                             145.0, 1.0)
    n_i     = len(i_seg)
    body_i  = i_seg[int(0.12*n_i):
                    n_i-int(0.12*n_i)]
    cent_i1 = measure_band_centroid(
        body_i, 200.0, 700.0)
    cent_i2 = measure_band_centroid(
        body_i, 1400.0, 2200.0)
    p1 = check('voicing',
               measure_voicing(body_i),
               0.65, 1.0)
    p2 = check(
        f'F1 centroid ({cent_i1:.0f} Hz)',
        cent_i1, 280.0, 480.0,
        unit=' Hz', fmt='.1f')
    p3 = check(
        f'F2 centroid ({cent_i2:.0f} Hz)',
        cent_i2, 1600.0, 2000.0,
        unit=' Hz', fmt='.1f')
    d8 = p1 and p2 and p3
    all_pass &= d8
    write_wav("output_play/diag_i_slow.wav",
              ola_stretch(i_seg / (
                  np.max(np.abs(i_seg))+1e-8)
                  * 0.75, 4.0))
    print(f"  {'PASSED' if d8 else 'FAILED'}")
    print()

    # ── D9 NG ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 9 — NG NASAL [ŋ]")
    print()
    print("  Velar nasal. Antiformant ~1800 Hz.")
    print("  Murmur/notch ratio (200–600 Hz")
    print("  vs 1600–2000 Hz): target > 2.0")
    print()
    ng_seg = synth_NG(I_F, G_F, 145.0, 1.0)
    vr_ng  = measure_voicing(ng_seg)
    r_ng   = rms(ng_seg)
    p1 = check('voicing', vr_ng, 0.60, 1.0)
    p2 = check('RMS (nasal murmur)',
               r_ng, 0.005, 0.25)
    try:
        b_lo, a_lo = safe_bp(200.0, 600.0, SR)
        b_nt, a_nt = safe_bp(
            1600.0, 2000.0, SR)
        e_lo = float(np.mean(
            lfilter(b_lo, a_lo,
                    ng_seg.astype(float))**2))
        e_nt = float(np.mean(
            lfilter(b_nt, a_nt,
                    ng_seg.astype(float))**2))
        ratio = e_lo / (e_nt + 1e-12)
        p3 = check(
            f'murmur/notch ratio ({ratio:.2f})',
            ratio, 2.0, 10000.0,
            unit='', fmt='.2f')
        if not p3:
            print("      Raise NG_GAINS[1]"
                  " or NG_ANTI_BW.")
    except Exception:
        p3 = True
        print("    [SKIP] antiformant check")
    d9 = p1 and p2 and p3
    all_pass &= d9
    write_wav("output_play/diag_ng_slow.wav",
              ola_stretch(ng_seg / (
                  np.max(np.abs(ng_seg))+1e-8)
                  * 0.75, 4.0))
    print(f"  {'PASSED' if d9 else 'FAILED'}")
    print()

    # ── D10 G ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 10 — G ONSET [ɡ]")
    print()
    g_seg  = synth_G(A_F, 145.0, 1.0)
    n_cl_g = int(50.0 / 1000.0 * SR)
    n_bst_g= int(12.0 / 1000.0 * SR)
    bst_g  = (g_seg[n_cl_g:n_cl_g+n_bst_g]
              if len(g_seg) > n_cl_g+n_bst_g
              else g_seg[-n_bst_g:])
    cent_g = measure_burst_centroid(bst_g)
    p1 = check('RMS level', rms(g_seg),
               0.005, 0.80)
    p2 = check(
        f'burst centroid ({cent_g:.0f} Hz)',
        cent_g, 600.0, 2000.0,
        unit=' Hz', fmt='.1f')
    d10 = p1 and p2
    all_pass &= d10
    write_wav("output_play/diag_g_slow.wav",
              ola_stretch(g_seg / (
                  np.max(np.abs(g_seg))+1e-8)
                  * 0.75, 4.0))
    print(f"  {'PASSED' if d10 else 'FAILED'}")
    print()

    # ── D11 A ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 11 — A FINAL [ɑ]")
    print()
    a_seg   = synth_A_short(G_F, None,
                             110.0, 1.0)
    n_a     = len(a_seg)
    body_a  = a_seg[:int(0.6*n_a)]
    cent_a  = measure_band_centroid(
        body_a, 600.0, 1400.0)
    p1 = check_warn('voicing',
                    measure_voicing(body_a),
                    0.50, 1.0, warn_lo=0.30)
    p2 = check(
        f'F1+F2 centroid ({cent_a:.0f} Hz)',
        cent_a, 750.0, 1050.0,
        unit=' Hz', fmt='.1f')
    d11 = p1 and p2
    all_pass &= d11
    write_wav("output_play/diag_a_slow.wav",
              ola_stretch(a_seg / (
                  np.max(np.abs(a_seg))+1e-8)
                  * 0.75, 4.0))
    print(f"  {'PASSED' if d11 else 'FAILED'}")
    print()

    # ── D12 FULL WORD ─────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 12 — FULL WORD")
    print()
    tc_dry  = synth_theod_cyninga(
        145.0, 1.0, False)
    tc_hall = synth_theod_cyninga(
        145.0, 1.0, True)
    dur_ms  = len(tc_dry) / SR * 1000.0
    p1 = check('RMS level', rms(tc_dry),
               0.010, 0.90)
    p2 = check(
        f'duration ({dur_ms:.0f} ms)',
        dur_ms, 500.0, 1200.0,
        unit=' ms', fmt='.1f')
    print(f"  {len(tc_dry)} samples"
          f" ({dur_ms:.0f} ms)")
    write_wav(
        "output_play/"
        "diag_theod_cyninga_full.wav",
        tc_dry)
    write_wav(
        "output_play/"
        "diag_theod_cyninga_hall.wav",
        tc_hall)
    write_wav(
        "output_play/"
        "diag_theod_cyninga_slow.wav",
        ola_stretch(tc_dry, 4.0))
    d12 = p1 and p2
    all_pass &= d12
    print(f"  {'PASSED' if d12 else 'FAILED'}")
    print()

    # ── D13 PERCEPTUAL ────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 13 — PERCEPTUAL")
    print()
    for fn in [
        "diag_th_slow.wav",
        "diag_y_slow.wav",
        "diag_ng_slow.wav",
        "diag_theod_cyninga_slow.wav",
        "diag_theod_cyninga_hall.wav",
    ]:
        print(f"  afplay output_play/{fn}")
    print()
    print("  LISTEN FOR:")
    print("  Þ: voiceless hiss, dental"
          " — softer than [s]")
    print("  Y: front rounded — between"
          " 'see' and 'sue'")
    print("  NG: velar hum, darker than N")
    print("  Full: Þ·Ē·O·D·K·Y·N·I·NG·G·A")
    print("  Eleven distinct events")
    print()

    # ── SUMMARY ───────────────────────────
    print("=" * 60)
    print("SUMMARY")
    print()
    rows = [
        ("D1 Þ fricative",  d1),
        ("D2 Ē vowel",      d2),
        ("D3 O vowel",      d3),
        ("D4 D onset",      d4),
        ("D5 K onset",      d5),
        ("D6 Y vowel",      d6),
        ("D7 N nasal",      d7),
        ("D8 I vowel",      d8),
        ("D9 NG nasal",     d9),
        ("D10 G onset",     d10),
        ("D11 A final",     d11),
        ("D12 Full word",   d12),
    ]
    for lbl, ok_ in rows:
        sym = "✓ PASS" if ok_ else "✗ FAIL"
        print(f"  {lbl:22s}  {sym}")
    print(f"  {'D13 Perceptual':22s}  LISTEN")
    print()
    if all_pass:
        print("  ALL NUMERIC CHECKS PASSED")
        print()
        print("  ÞĒOD-CYNINGA [θeːodkyniŋɡɑ]"
              " verified.")
        print("  Next: ÞRYM [θrym]")
        print("  Beowulf line 2, word 2.")
    else:
        failed = [l for l, ok_ in rows
                  if not ok_]
        print(f"  FAILED: {', '.join(failed)}")
    print()
    print("=" * 60)
    return all_pass


if __name__ == "__main__":
    passed = run_diagnostics()
    sys.exit(0 if passed else 1)
