"""
HU DIAGNOSTIC v1
Old English: hu [xu]
Beowulf line 3, word 1
February 2026

DIAGNOSTICS:
  D1  X fricative [x]
  D2  U vowel [u]
  D3  Full word
  D4  Perceptual
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
    print("HU DIAGNOSTIC v1")
    print("Old English [xu]")
    print("Beowulf line 3, word 1")
    print("=" * 60)
    print()

    try:
        from hu_reconstruction import (
            synth_hu, synth_X,
            synth_U_short,
            apply_simple_room,
            U_F)
        print("  hu_reconstruction.py: OK")
    except ImportError as e:
        print(f"  IMPORT FAILED: {e}")
        return False
    print()

    all_pass = True

    # ── D1 X ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 1 — X FRICATIVE [x]")
    print()
    print("  Voiceless velar fricative.")
    print("  Scottish 'loch', German 'Bach'.")
    print("  Centroid lower than [f] and [θ]")
    print("  — velar place, longer front cavity.")
    print()
    print("  Fricative centroid hierarchy:")
    print("  [x] < [θ] < [f]")
    print("  velar < dental < labiodental")
    print()
    print("  Target: 800–3500 Hz")
    print()
    x_seg  = synth_X(U_F, 1.0, SR)
    cent_x = measure_band_centroid(
        x_seg, 400.0, 8000.0)
    p1 = check('voicing (must be low)',
               measure_voicing(x_seg),
               0.0, 0.35)
    p2 = check('RMS level', rms(x_seg),
               0.005, 0.80)
    p3 = check(
        f'frication centroid ({cent_x:.0f} Hz)',
        cent_x, 800.0, 3500.0,
        unit=' Hz', fmt='.1f')
    if not p3:
        if cent_x > 3500:
            print("      Centroid too high.")
            print("      Lower X_NOISE_CF.")
            print("      Raise X_FRONT_BW.")
        else:
            print("      Centroid too low.")
            print("      Raise X_NOISE_CF.")
    d1 = p1 and p2 and p3
    all_pass &= d1
    write_wav("output_play/diag_hu_x.wav",
              ola_stretch(x_seg / (
                  np.max(np.abs(x_seg))+1e-8)
                  * 0.75, 4.0))
    print(f"  {'PASSED' if d1 else 'FAILED'}")
    print()

    # ── D2 U ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 2 — U VOWEL [u]")
    print()
    print("  Short close back rounded.")
    print("  Word-final — longer decay.")
    print("  Same formant targets as")
    print("  GĒAR-DAGUM [u].")
    print()
    u_seg  = synth_U_short(U_F, None,
                            145.0, 1.0)
    n_u    = len(u_seg)
    body_u = u_seg[int(0.15*n_u):
                   int(0.55*n_u)]
    cent_u1 = measure_band_centroid(
        body_u, 100.0, 500.0)
    cent_u2 = measure_band_centroid(
        body_u, 400.0, 1000.0)
    p1 = check('voicing',
               measure_voicing(body_u),
               0.50, 1.0)
    p2 = check(
        f'F1 centroid ({cent_u1:.0f} Hz)',
        cent_u1, 180.0, 380.0,
        unit=' Hz', fmt='.1f')
    p3 = check(
        f'F2 centroid ({cent_u2:.0f} Hz)',
        cent_u2, 500.0, 900.0,
        unit=' Hz', fmt='.1f')
    d2 = p1 and p2 and p3
    all_pass &= d2
    write_wav("output_play/diag_hu_u.wav",
              ola_stretch(u_seg / (
                  np.max(np.abs(u_seg))+1e-8)
                  * 0.75, 4.0))
    print(f"  {'PASSED' if d2 else 'FAILED'}")
    print()

    # ── D3 FULL WORD ──────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 3 — FULL WORD [xu]")
    print()
    hu_dry  = synth_hu(145.0, 1.0, False)
    hu_hall = synth_hu(145.0, 1.0, True)
    dur_ms  = len(hu_dry) / SR * 1000.0
    p1 = check('RMS level', rms(hu_dry),
               0.010, 0.90)
    p2 = check(
        f'duration ({dur_ms:.0f} ms)',
        dur_ms, 100.0, 300.0,
        unit=' ms', fmt='.1f')
    print(f"  {len(hu_dry)} samples"
          f" ({dur_ms:.0f} ms)")
    write_wav(
        "output_play/diag_hu_full.wav",
        hu_dry)
    write_wav(
        "output_play/diag_hu_hall.wav",
        hu_hall)
    write_wav(
        "output_play/diag_hu_slow.wav",
        ola_stretch(hu_dry, 4.0))
    d3 = p1 and p2
    all_pass &= d3
    print(f"  {'PASSED' if d3 else 'FAILED'}")
    print()

    # ── D4 PERCEPTUAL ─────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 4 — PERCEPTUAL")
    print()
    for fn in [
        "diag_hu_x.wav",
        "diag_hu_u.wav",
        "diag_hu_slow.wav",
        "diag_hu_hall.wav",
    ]:
        print(f"  afplay output_play/{fn}")
    print()
    print("  LISTEN FOR:")
    print("  X: deeper scraping sound than [f]")
    print("    or [θ] — further back in throat")
    print("    Scottish 'loch' quality")
    print("  U: short dark rounded vowel")
    print("  Full: X·U — two events")
    print("  Shorter than any word so far")
    print()

    # ── SUMMARY ───────────────────────────
    print("=" * 60)
    print("SUMMARY")
    print()
    rows = [
        ("D1 X fricative", d1),
        ("D2 U vowel",     d2),
        ("D3 Full word",   d3),
    ]
    for lbl, ok_ in rows:
        sym = "✓ PASS" if ok_ else "✗ FAIL"
        print(f"  {lbl:22s}  {sym}")
    print(f"  {'D4 Perceptual':22s}  LISTEN")
    print()
    if all_pass:
        print("  ALL NUMERIC CHECKS PASSED")
        print()
        print("  HU [xu] verified.")
        print("  Next: ÐĀ [ðɑː]")
        print("  Beowulf line 3, word 2.")
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
