"""
ELLEN DIAGNOSTIC v1
Old English: ellen [ellen]
Beowulf line 3, word 4
February 2026

DIAGNOSTICS:
  D1  E1 vowel [e]
  D2  LL geminate [lː]
  D3  E2 vowel [e]
  D4  N nasal [n]
  D5  Geminate ratio [lː]/[l]
  D6  Full word
  D7  Perceptual

KEY CHECK:
  D5 geminate ratio.
  [lː] duration must be >= 1.7×
  singleton [l] duration.
  This is the phonemic distinction.
  Target ratio: 1.7–2.5×
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
    print("ELLEN DIAGNOSTIC v1")
    print("Old English [ellen]")
    print("Beowulf line 3, word 4")
    print("=" * 60)
    print()

    try:
        from ellen_reconstruction import (
            synth_ellen,
            synth_E_short,
            synth_L,
            synth_N_final,
            apply_simple_room,
            E_F, L_F, N_F,
            L_DUR_MS, LL_DUR_MS)
        print("  ellen_reconstruction.py: OK")
    except ImportError as e:
        print(f"  IMPORT FAILED: {e}")
        return False
    print()

    all_pass = True

    # ── D1 E1 ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 1 — E1 VOWEL [e]")
    print()
    e1_seg = synth_E_short(E_F, L_F,
                            145.0, 1.0)
    n_e1   = len(e1_seg)
    body   = e1_seg[int(0.12*n_e1):
                    n_e1-int(0.12*n_e1)]
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
    d1 = p1 and p2
    all_pass &= d1
    print(f"  {'PASSED' if d1 else 'FAILED'}")
    print()

    # ── D2 LL ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 2 — LL GEMINATE [lː]")
    print()
    print("  Geminate lateral.")
    print("  Same formant targets as [l].")
    print("  Duration 2× singleton.")
    print("  Voicing and F3 same as [l].")
    print()
    ll_seg  = synth_L(E_F, E_F,
                       145.0, 1.0, SR,
                       geminate=True)
    n_ll    = len(ll_seg)
    body_ll = ll_seg[int(0.15*n_ll):
                     int(0.85*n_ll)]
    dur_ll  = n_ll / SR * 1000.0
    cent_f1 = measure_band_centroid(
        body_ll, 150.0, 500.0)
    cent_f3 = measure_band_centroid(
        body_ll, 2000.0, 3000.0)
    p1 = check('voicing',
               measure_voicing(body_ll),
               0.55, 1.0)
    p2 = check(
        f'F1 centroid ({cent_f1:.0f} Hz)',
        cent_f1, 150.0, 450.0,
        unit=' Hz', fmt='.1f')
    p3 = check(
        f'F3 centroid ({cent_f3:.0f} Hz)',
        cent_f3, 2000.0, 2800.0,
        unit=' Hz', fmt='.1f')
    p4 = check(
        f'duration ({dur_ll:.0f} ms)',
        dur_ll, 110.0, 160.0,
        unit=' ms', fmt='.1f')
    d2 = p1 and p2 and p3 and p4
    all_pass &= d2
    write_wav(
        "output_play/diag_ellen_ll.wav",
        ola_stretch(ll_seg / (
            np.max(np.abs(ll_seg))+1e-8)
            * 0.75, 4.0))
    print(f"  {'PASSED' if d2 else 'FAILED'}")
    print()

    # ── D3 E2 ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 3 — E2 VOWEL [e]")
    print()
    e2_seg = synth_E_short(L_F, N_F,
                            145.0, 1.0)
    n_e2   = len(e2_seg)
    body   = e2_seg[int(0.12*n_e2):
                    n_e2-int(0.12*n_e2)]
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

    # ── D4 N ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 4 — N NASAL [n]")
    print()
    n_seg = synth_N_final(E_F, 145.0, 1.0)
    p1 = check('voicing',
               measure_voicing(n_seg),
               0.60, 1.0)
    p2 = check('RMS (nasal murmur)',
               rms(n_seg), 0.005, 0.25)
    d4 = p1 and p2
    all_pass &= d4
    print(f"  {'PASSED' if d4 else 'FAILED'}")
    print()

    # ── D5 GEMINATE RATIO ─────────────────
    print("─" * 60)
    print("DIAGNOSTIC 5 — GEMINATE RATIO")
    print()
    print("  The phonemic test.")
    print("  [lː] must be >= 1.7× [l].")
    print("  This is what distinguishes")
    print("  geminate from singleton in OE.")
    print()
    l_seg   = synth_L(E_F, E_F,
                       145.0, 1.0, SR,
                       geminate=False)
    dur_l   = len(l_seg)  / SR * 1000.0
    dur_ll2 = len(ll_seg) / SR * 1000.0
    ratio   = dur_ll2 / (dur_l + 1e-9)
    print(f"  [l]  singleton: {dur_l:.1f} ms"
          f"  ({len(l_seg)} samples)")
    print(f"  [lː] geminate:  {dur_ll2:.1f} ms"
          f"  ({len(ll_seg)} samples)")
    p1 = check(
        f'geminate ratio ({ratio:.2f}×)',
        ratio, 1.7, 2.5,
        unit='×', fmt='.2f')
    d5 = p1
    all_pass &= d5
    print(f"  {'PASSED' if d5 else 'FAILED'}")
    print()

    # ── D6 FULL WORD ──────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 6 — FULL WORD [ellen]")
    print()
    w_dry  = synth_ellen(145.0, 1.0, False)
    w_hall = synth_ellen(145.0, 1.0, True)
    dur_ms = len(w_dry) / SR * 1000.0
    p1 = check('RMS level', rms(w_dry),
               0.010, 0.90)
    p2 = check(
        f'duration ({dur_ms:.0f} ms)',
        dur_ms, 250.0, 500.0,
        unit=' ms', fmt='.1f')
    print(f"  {len(w_dry)} samples"
          f" ({dur_ms:.0f} ms)")
    write_wav(
        "output_play/diag_ellen_full.wav",
        w_dry)
    write_wav(
        "output_play/diag_ellen_hall.wav",
        w_hall)
    write_wav(
        "output_play/diag_ellen_slow.wav",
        ola_stretch(w_dry, 4.0))
    d6 = p1 and p2
    all_pass &= d6
    print(f"  {'PASSED' if d6 else 'FAILED'}")
    print()

    # ── D7 PERCEPTUAL ─────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 7 — PERCEPTUAL")
    print()
    for fn in [
        "diag_ellen_ll.wav",
        "diag_ellen_slow.wav",
        "diag_ellen_hall.wav",
    ]:
        print(f"  afplay output_play/{fn}")
    print()
    print("  LISTEN FOR:")
    print("  LL: longer than any previous [l]")
    print("    the lateral holds, does not")
    print("    release quickly")
    print("  Full: E·LL·E·N — four events")
    print("  The LL dominates duration")
    print()

    # ── SUMMARY ───────────────────────────
    print("=" * 60)
    print("SUMMARY")
    print()
    rows = [
        ("D1  E1 vowel",       d1),
        ("D2  LL geminate",    d2),
        ("D3  E2 vowel",       d3),
        ("D4  N nasal",        d4),
        ("D5  Geminate ratio", d5),
        ("D6  Full word",      d6),
    ]
    for lbl, ok_ in rows:
        sym = "✓ PASS" if ok_ else "✗ FAIL"
        print(f"  {lbl:22s}  {sym}")
    print(f"  {'D7 Perceptual':22s}  LISTEN")
    print()
    if all_pass:
        print("  ALL NUMERIC CHECKS PASSED")
        print()
        print("  ELLEN [ellen] verified.")
        print("  Geminate [lː] documented.")
        print("  Next: FREMEDON [fremedon]")
        print("  Beowulf line 3, word 5.")
        print("  Line 3 final word.")
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
