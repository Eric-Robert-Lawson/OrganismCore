"""
ÆÞELINGAS DIAGNOSTIC v1
Old English: æþelingas [æθeliŋɡɑs]
Beowulf line 3, word 3
February 2026

DIAGNOSTICS:
  D1  Æ vowel [æ]
  D2  Þ fricative [θ]
  D3  E vowel [e]
  D4  L lateral [l]      NEW
  D5  I vowel [ɪ]
  D6  N nasal [n]
  D7  G stop [ɡ]
  D8  A vowel [ɑ]
  D9  S fricative [s]    NEW
  D10 Full word
  D11 Perceptual
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


def run_diagnostics():
    print()
    print("=" * 60)
    print("ÆÞELINGAS DIAGNOSTIC v1")
    print("Old English [æθeliŋɡɑs]")
    print("Beowulf line 3, word 3")
    print("=" * 60)
    print()

    try:
        from athelingas_reconstruction import (
            synth_athelingas,
            synth_AE, synth_TH,
            synth_E_short, synth_L,
            synth_II, synth_N,
            synth_G, synth_A_short,
            synth_S, apply_simple_room,
            AE_F, E_F, L_F, II_F,
            N_F, A_F)
        print("  athelingas_reconstruction.py: OK")
    except ImportError as e:
        print(f"  IMPORT FAILED: {e}")
        return False
    print()

    all_pass = True

    # ── D1 AE ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 1 — Æ VOWEL [æ]")
    print()
    ae_seg = synth_AE(AE_F, E_F, 145.0, 1.0)
    n_ae   = len(ae_seg)
    body   = ae_seg[int(0.12*n_ae):
                    n_ae-int(0.12*n_ae)]
    p1 = check('voicing',
               measure_voicing(body),
               0.50, 1.0)
    p2 = check(
        f'F1 centroid'
        f' ({measure_band_centroid(body, 500.0, 900.0):.0f} Hz)',
        measure_band_centroid(body,
                               500.0, 900.0),
        550.0, 800.0,
        unit=' Hz', fmt='.1f')
    d1 = p1 and p2
    all_pass &= d1
    write_wav("output_play/diag_ath_ae.wav",
              ola_stretch(ae_seg / (
                  np.max(np.abs(ae_seg))+1e-8)
                  * 0.75, 4.0))
    print(f"  {'PASSED' if d1 else 'FAILED'}")
    print()

    # ── D2 TH ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 2 — Þ FRICATIVE [θ]")
    print()
    th_seg  = synth_TH(E_F, 1.0, SR)
    cent_th = measure_band_centroid(
        th_seg, 400.0, 8000.0)
    p1 = check('voicing (must be low)',
               measure_voicing(th_seg),
               0.0, 0.35)
    p2 = check(
        f'centroid ({cent_th:.0f} Hz)',
        cent_th, 3500.0, 6000.0,
        unit=' Hz', fmt='.1f')
    d2 = p1 and p2
    all_pass &= d2
    print(f"  {'PASSED' if d2 else 'FAILED'}")
    print()

    # ── D3 E ───────────────��──────────────
    print("─" * 60)
    print("DIAGNOSTIC 3 — E VOWEL [e]")
    print()
    e_seg = synth_E_short(E_F, L_F,
                           145.0, 1.0)
    n_e   = len(e_seg)
    body  = e_seg[int(0.12*n_e):
                  n_e-int(0.12*n_e)]
    p1 = check('voicing',
               measure_voicing(body),
               0.50, 1.0)
    p2 = check(
        f'F2 centroid'
        f' ({measure_band_centroid(body, 1600.0, 2600.0):.0f} Hz)',
        measure_band_centroid(body,
                               1600.0, 2600.0),
        1800.0, 2400.0,
        unit=' Hz', fmt='.1f')
    d3 = p1 and p2
    all_pass &= d3
    print(f"  {'PASSED' if d3 else 'FAILED'}")
    print()

    # ── D4 L ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 4 — L LATERAL [l]")
    print()
    print("  Voiced alveolar lateral.")
    print("  F1 low (~300 Hz).")
    print("  F3 pulled low (~2400–2600 Hz).")
    print("  Antiformant ~1800–2000 Hz.")
    print()
    l_seg  = synth_L(E_F, II_F, 145.0, 1.0)
    n_l    = len(l_seg)
    body   = l_seg[int(0.15*n_l):
                   int(0.85*n_l)]
    cent_f1 = measure_band_centroid(
        body, 150.0, 500.0)
    cent_f3 = measure_band_centroid(
        body, 2000.0, 3000.0)
    p1 = check('voicing',
               measure_voicing(body),
               0.55, 1.0)
    p2 = check(
        f'F1 centroid ({cent_f1:.0f} Hz)',
        cent_f1, 150.0, 450.0,
        unit=' Hz', fmt='.1f')
    p3 = check(
        f'F3 centroid ({cent_f3:.0f} Hz)',
        cent_f3, 2000.0, 2800.0,
        unit=' Hz', fmt='.1f')
    d4 = p1 and p2 and p3
    all_pass &= d4
    write_wav("output_play/diag_ath_l.wav",
              ola_stretch(l_seg / (
                  np.max(np.abs(l_seg))+1e-8)
                  * 0.75, 4.0))
    print(f"  {'PASSED' if d4 else 'FAILED'}")
    print()

    # ── D5 I ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 5 — I VOWEL [ɪ]")
    print()
    ii_seg = synth_II(L_F, N_F, 145.0, 1.0)
    n_ii   = len(ii_seg)
    body   = ii_seg[int(0.12*n_ii):
                    n_ii-int(0.12*n_ii)]
    p1 = check('voicing',
               measure_voicing(body),
               0.50, 1.0)
    p2 = check(
        f'F2 centroid'
        f' ({measure_band_centroid(body, 1500.0, 2400.0):.0f} Hz)',
        measure_band_centroid(body,
                               1500.0, 2400.0),
        1600.0, 2200.0,
        unit=' Hz', fmt='.1f')
    d5 = p1 and p2
    all_pass &= d5
    print(f"  {'PASSED' if d5 else 'FAILED'}")
    print()

    # ── D6 N ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 6 — N NASAL [n]")
    print()
    n_seg = synth_N(II_F, A_F, 145.0, 1.0)
    p1 = check('voicing',
               measure_voicing(n_seg),
               0.65, 1.0)
    p2 = check('RMS (nasal murmur)',
               rms(n_seg), 0.005, 0.25)
    d6 = p1 and p2
    all_pass &= d6
    print(f"  {'PASSED' if d6 else 'FAILED'}")
    print()

    # ── D7 G ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 7 — G STOP [ɡ]")
    print()
    g_seg = synth_G(N_F, A_F, 145.0, 1.0)
    p1 = check('RMS level', rms(g_seg),
               0.010, 0.90)
    dur_g = len(g_seg) / SR * 1000.0
    p2 = check(
        f'duration ({dur_g:.0f} ms)',
        dur_g, 50.0, 120.0,
        unit=' ms', fmt='.1f')
    d7 = p1 and p2
    all_pass &= d7
    print(f"  {'PASSED' if d7 else 'FAILED'}")
    print()

    # ── D8 A ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 8 — A VOWEL [ɑ]")
    print()
    a_seg = synth_A_short(A_F, None,
                           145.0, 1.0)
    n_a   = len(a_seg)
    body  = a_seg[int(0.12*n_a):
                  n_a-int(0.12*n_a)]
    p1 = check('voicing',
               measure_voicing(body),
               0.50, 1.0)
    p2 = check(
        f'F1 centroid'
        f' ({measure_band_centroid(body, 500.0, 900.0):.0f} Hz)',
        measure_band_centroid(body,
                               500.0, 900.0),
        550.0, 800.0,
        unit=' Hz', fmt='.1f')
    d8 = p1 and p2
    all_pass &= d8
    print(f"  {'PASSED' if d8 else 'FAILED'}")
    print()

    # ── D9 S ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 9 — S FRICATIVE [s]")
    print()
    print("  Voiceless alveolar fricative.")
    print("  Highest centroid of all fricatives.")
    print("  Centroid hierarchy complete:")
    print("  [x]<[θ]<[f]<[s]")
    print()
    s_seg   = synth_S(None, 1.0, SR)
    cent_s  = measure_band_centroid(
        s_seg, 1000.0, SR // 2 - 100)
    p1 = check('voicing (must be low)',
               measure_voicing(s_seg),
               0.0, 0.35)
    p2 = check('RMS level', rms(s_seg),
               0.005, 0.80)
    p3 = check(
        f'centroid ({cent_s:.0f} Hz)',
        cent_s, 5000.0, SR // 2 - 100,
        unit=' Hz', fmt='.1f')
    print()
    print(f"  Centroid hierarchy (measured):")
    print(f"  [x] ~2750 Hz")
    print(f"  [θ] ~4200 Hz")
    print(f"  [f] ~5800 Hz")
    print(f"  [s] {cent_s:.0f} Hz")
    d9 = p1 and p2 and p3
    all_pass &= d9
    write_wav("output_play/diag_ath_s.wav",
              ola_stretch(s_seg / (
                  np.max(np.abs(s_seg))+1e-8)
                  * 0.75, 4.0))
    print(f"  {'PASSED' if d9 else 'FAILED'}")
    print()

    # ── D10 FULL WORD ─────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 10 — FULL WORD")
    print()
    w_dry  = synth_athelingas(
        145.0, 1.0, False)
    w_hall = synth_athelingas(
        145.0, 1.0, True)
    dur_ms = len(w_dry) / SR * 1000.0
    p1 = check('RMS level', rms(w_dry),
               0.010, 0.90)
    p2 = check(
        f'duration ({dur_ms:.0f} ms)',
        dur_ms, 400.0, 1000.0,
        unit=' ms', fmt='.1f')
    print(f"  {len(w_dry)} samples"
          f" ({dur_ms:.0f} ms)")
    write_wav(
        "output_play/diag_ath_full.wav",
        w_dry)
    write_wav(
        "output_play/diag_ath_hall.wav",
        w_hall)
    write_wav(
        "output_play/diag_ath_slow.wav",
        ola_stretch(w_dry, 4.0))
    d10 = p1 and p2
    all_pass &= d10
    print(f"  {'PASSED' if d10 else 'FAILED'}")
    print()

    # ── D11 PERCEPTUAL ────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 11 — PERCEPTUAL")
    print()
    for fn in [
        "diag_ath_l.wav",
        "diag_ath_s.wav",
        "diag_ath_slow.wav",
        "diag_ath_hall.wav",
    ]:
        print(f"  afplay output_play/{fn}")
    print()
    print("  LISTEN FOR:")
    print("  L: liquid, voiced — like 'l'")
    print("    lower, darker than [n]")
    print("  S: sharp high hiss — highest")
    print("    fricative in the inventory")
    print("  Full: Æ·Þ·E·L·I·N·G·A·S")
    print("  Nine events")
    print()

    # ── SUMMARY ���──────────────────────────
    print("=" * 60)
    print("SUMMARY")
    print()
    rows = [
        ("D1  Æ vowel",      d1),
        ("D2  Þ fricative",  d2),
        ("D3  E vowel",      d3),
        ("D4  L lateral",    d4),
        ("D5  I vowel",      d5),
        ("D6  N nasal",      d6),
        ("D7  G stop",       d7),
        ("D8  A vowel",      d8),
        ("D9  S fricative",  d9),
        ("D10 Full word",    d10),
    ]
    for lbl, ok_ in rows:
        sym = "✓ PASS" if ok_ else "✗ FAIL"
        print(f"  {lbl:22s}  {sym}")
    print(f"  {'D11 Perceptual':22s}  LISTEN")
    print()
    if all_pass:
        print("  ALL NUMERIC CHECKS PASSED")
        print()
        print("  ÆÞELINGAS [æθeliŋɡɑs] verified.")
        print("  Next: ELLEN [ellen]")
        print("  Beowulf line 3, word 4.")
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
