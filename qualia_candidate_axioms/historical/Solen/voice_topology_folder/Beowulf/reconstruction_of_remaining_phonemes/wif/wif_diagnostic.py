"""
WĪF DIAGNOSTIC v1
Old English: wīf [wiːf]
Inventory completion — word 1 of 4
New phoneme: [iː]
February 2026

DIAGNOSTICS:
  D1  W approximant [w]
  D2  IY vowel [iː] — NEW
  D3  IY duration — long vowel
  D4  IY F2 height — highest in inventory
  D5  IY vs [ɪ] distinction
  D6  IY vs [y] distinction
  D7  F fricative [f]
  D8  Full word
  D9  Perceptual

KEY CHECKS:
  D3: duration >= 90 ms (long vowel)
  D4: F2 >= 2000 Hz (highest in inventory)
  D5: [iː] F2 ~2300 vs [ɪ] F2 ~1700
      delta >= 400 Hz
  D6: [iː] F2 ~2300 vs [y] F2 ~1500
      delta >= 600 Hz
      rounding is the distinction
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

def measure_band_centroid(seg, lo_hz,
                           hi_hz, sr=SR):
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
    print("WĪF DIAGNOSTIC v1")
    print("Old English [wiːf]")
    print("Inventory completion — word 1 of 4")
    print("New phoneme: [iː]")
    print("=" * 60)
    print()

    try:
        from wif_reconstruction import (
            synth_wif,
            synth_W, synth_IY, synth_F,
            apply_simple_room,
            W_F, IY_F)
        print("  wif_reconstruction.py: OK")
    except ImportError as e:
        print(f"  IMPORT FAILED: {e}")
        return False
    print()

    all_pass = True

    # ── D1 W ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 1 — W APPROXIMANT [w]")
    print()
    w_seg  = synth_W(None, IY_F,
                      145.0, 1.0, SR)
    p1 = check('voicing',
               measure_voicing(w_seg),
               0.50, 1.0)
    p2 = check('RMS level', rms(w_seg),
               0.005, 0.80)
    d1 = p1 and p2
    all_pass &= d1
    print(f"  {'PASSED' if d1 else 'FAILED'}")
    print()

    # ── D2 IY BASIC ───────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 2 — IY VOWEL [iː] basic")
    print()
    iy_seg = synth_IY(W_F, None,
                       145.0, 1.0, SR)
    n_iy   = len(iy_seg)
    body   = iy_seg[int(0.10*n_iy):
                    n_iy-int(0.10*n_iy)]
    p1 = check('voicing',
               measure_voicing(body),
               0.50, 1.0)
    p2 = check('RMS level', rms(body),
               0.010, 0.90)
    d2 = p1 and p2
    all_pass &= d2
    print(f"  {'PASSED' if d2 else 'FAILED'}")
    print()

    # ── D3 IY DURATION ────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 3 — [iː] DURATION"
          " — long vowel")
    print()
    dur_iy = n_iy / SR * 1000.0
    print(f"  Duration: {dur_iy:.0f} ms")
    print(f"  Long vowel target: >= 90 ms")
    print(f"  Short vowel reference: ~55 ms")
    print(f"  Ratio: {dur_iy/55.0:.2f}x")
    print()
    p1 = check(
        f'duration ({dur_iy:.0f} ms)',
        dur_iy, 90.0, 150.0,
        unit=' ms', fmt='.1f')
    d3 = p1
    all_pass &= d3
    print(f"  {'PASSED' if d3 else 'FAILED'}")
    print()

    # ── D4 IY F2 HEIGHT ───────────────────
    print("─" * 60)
    print("DIAGNOSTIC 4 — [iː] F2 HEIGHT"
          " — highest in inventory")
    print()
    f2_iy = measure_band_centroid(
        body, 1800.0, 3000.0)
    print(f"  [iː] F2: {f2_iy:.0f} Hz")
    print(f"  Reference values:")
    print(f"    [e]  F2: ~1875 Hz")
    print(f"    [y]  F2: ~1418 Hz")
    print(f"    [ɪ]  F2: ~1700 Hz (est)")
    print(f"    [iː] F2: target ~2300 Hz")
    print()
    p1 = check(
        f'F2 ({f2_iy:.0f} Hz)',
        f2_iy, 2000.0, 2800.0,
        unit=' Hz', fmt='.1f')
    d4 = p1
    all_pass &= d4
    print(f"  {'PASSED' if d4 else 'FAILED'}")
    print()

    # ── D5 IY vs SHORT I ──────────────────
    print("─" * 60)
    print("DIAGNOSTIC 5 — [iː] vs [ɪ]"
          " DISTINCTION")
    print()
    f2_short_i = 1700.0
    delta_i    = f2_iy - f2_short_i
    print(f"  [iː] F2: {f2_iy:.0f} Hz")
    print(f"  [ɪ]  F2: {f2_short_i:.0f} Hz"
          f" (reference)")
    print(f"  Delta:   {delta_i:.0f} Hz")
    print()
    p1 = check(
        f'F2 delta vs [ɪ] ({delta_i:.0f} Hz)',
        delta_i, 400.0, 900.0,
        unit=' Hz', fmt='.1f')
    d5 = p1
    all_pass &= d5
    print(f"  {'PASSED' if d5 else 'FAILED'}")
    print()

    # ── D6 IY vs Y ────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 6 — [iː] vs [y]"
          " ROUNDING DISTINCTION")
    print()
    f2_y    = 1418.0
    delta_y = f2_iy - f2_y
    print(f"  [iː] F2: {f2_iy:.0f} Hz"
          f" (unrounded)")
    print(f"  [y]  F2: {f2_y:.0f} Hz"
          f" (rounded — verified)")
    print(f"  Delta:   {delta_y:.0f} Hz")
    print(f"  Rounding effect: ~800 Hz"
          f" F2 lowering")
    print()
    p1 = check(
        f'F2 delta vs [y] ({delta_y:.0f} Hz)',
        delta_y, 600.0, 1100.0,
        unit=' Hz', fmt='.1f')
    d6 = p1
    all_pass &= d6
    print(f"  {'PASSED' if d6 else 'FAILED'}")
    print()

    # ── D7 F ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 7 — F FRICATIVE [f]")
    print()
    f_seg  = synth_F(IY_F, None, 1.0, SR)
    p1 = check('voicing (must be low)',
               measure_voicing(f_seg),
               0.0, 0.35)
    p2 = check('RMS level', rms(f_seg),
               0.001, 0.50)
    d7 = p1 and p2
    all_pass &= d7
    print(f"  {'PASSED' if d7 else 'FAILED'}")
    print()

    # ── D8 FULL WORD ──────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 8 — FULL WORD [wiːf]")
    print()
    w_dry  = synth_wif(145.0, 1.0, False)
    w_hall = synth_wif(145.0, 1.0, True)
    dur_ms = len(w_dry) / SR * 1000.0
    p1 = check('RMS level', rms(w_dry),
               0.010, 0.90)
    p2 = check(
        f'duration ({dur_ms:.0f} ms)',
        dur_ms, 180.0, 310.0,
        unit=' ms', fmt='.1f')
    print(f"  {len(w_dry)} samples"
          f" ({dur_ms:.0f} ms)")
    write_wav(
        "output_play/diag_wif_full.wav",
        w_dry)
    write_wav(
        "output_play/diag_wif_hall.wav",
        w_hall)
    write_wav(
        "output_play/diag_wif_slow.wav",
        ola_stretch(w_dry, 4.0))
    write_wav(
        "output_play/diag_wif_iy.wav",
        ola_stretch(iy_seg / (
            np.max(np.abs(iy_seg))+1e-8)
            * 0.75, 4.0))
    d8 = p1 and p2
    all_pass &= d8
    print(f"  {'PASSED' if d8 else 'FAILED'}")
    print()

    # ── D9 PERCEPTUAL ─────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 9 — PERCEPTUAL")
    print()
    for fn in [
        "diag_wif_iy.wav",
        "diag_wif_slow.wav",
        "diag_wif_hall.wav",
    ]:
        print(f"  afplay output_play/{fn}")
    print()
    print("  LISTEN FOR:")
    print("  W  — voiced labio-velar")
    print("  IY — long, high, front")
    print("    highest pitch-like quality")
    print("    brightest vowel in inventory")
    print("    distinctly longer than [ɪ]")
    print("    no rounding — compare [y]")
    print("  F  — voiceless close")
    print("  Full: W·IY·F")
    print("  ModE 'wife' — same word.")
    print("  OE [wiːf] → ModE [waɪf]")
    print("  Great Vowel Shift audible.")
    print()

    # ── SUMMARY ───────────────────────────
    print("=" * 60)
    print("SUMMARY")
    print()
    rows = [
        ("D1  W approximant",       d1),
        ("D2  IY vowel basic",      d2),
        ("D3  IY duration",         d3),
        ("D4  IY F2 height",        d4),
        ("D5  IY vs short-I",       d5),
        ("D6  IY vs Y rounding",    d6),
        ("D7  F fricative",         d7),
        ("D8  Full word",           d8),
    ]
    for lbl, ok_ in rows:
        sym = "✓ PASS" if ok_ else "✗ FAIL"
        print(f"  {lbl:26s}  {sym}")
    print(f"  {'D9 Perceptual':26s}  LISTEN")
    print()
    if all_pass:
        print("  ALL NUMERIC CHECKS PASSED")
        print()
        print("  WĪF [wiːf] verified.")
        print("  [iː] added to inventory.")
        print("  36 phonemes verified.")
        print()
        print("  Inventory completion:")
        print("  [iː]  ✓ DONE")
        print("  [eːɑ] pending — ĒAGE")
        print("  [eːo] pending — ÞĒOD")
        print("  [p]   pending — PÆÞ")
        print("  [b]   pending — line 8")
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
