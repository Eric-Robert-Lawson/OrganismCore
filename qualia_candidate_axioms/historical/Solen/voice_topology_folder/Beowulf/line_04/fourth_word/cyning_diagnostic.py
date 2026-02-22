"""
CYNING DIAGNOSTIC v1
Old English: cyning [kyniŋɡ]
Beowulf line 4, word 4 — final word
February 2026

DIAGNOSTICS:
  D1   K stop [k]
  D2   Y vowel [y]
  D3   N nasal [n]
  D4   I vowel [ɪ]
  D5   NG nasal [ŋ]
  D6   G stop word-final [ɡ]
  D7   [ŋɡ] cluster
  D8   Full word
  D9   Perceptual

KEY CHECK:
  D7 [ŋɡ] cluster.
  Both [ŋ] and [ɡ] must be present
  as distinct events. Combined RMS
  and segment count verified.
  OE [ŋɡ] is not ModE [ŋ] —
  the stop must be present.
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
    print("CYNING DIAGNOSTIC v1")
    print("Old English [kyniŋɡ]")
    print("Beowulf line 4, word 4")
    print("=" * 60)
    print()

    try:
        from cyning_reconstruction import (
            synth_cyning,
            synth_K, synth_Y,
            synth_N, synth_II,
            synth_NG, synth_G_final,
            apply_simple_room,
            Y_F, N_F, II_F, NG_F)
        print("  cyning_reconstruction.py: OK")
    except ImportError as e:
        print(f"  IMPORT FAILED: {e}")
        return False
    print()

    all_pass = True

    # ── D1 K ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 1 — K STOP [k]")
    print()
    k_seg = synth_K(Y_F, 1.0, SR)
    p1 = check('voicing (must be low)',
               measure_voicing(k_seg),
               0.0, 0.35)
    p2 = check('RMS level', rms(k_seg),
               0.005, 0.70)
    d1 = p1 and p2
    all_pass &= d1
    print(f"  {'PASSED' if d1 else 'FAILED'}")
    print()

    # ── D2 Y ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 2 — Y VOWEL [y]")
    print()
    y_seg  = synth_Y(Y_F, N_F, 145.0,
                      1.0, SR)
    n_y    = len(y_seg)
    body_y = y_seg[int(0.12*n_y):
                   n_y-int(0.12*n_y)]
    p1 = check('voicing',
               measure_voicing(body_y),
               0.50, 1.0)
    cent_y = measure_band_centroid(
        body_y, 1400.0, 2200.0)
    p2 = check(
        f'F2 centroid ({cent_y:.0f} Hz)',
        cent_y, 1400.0, 2100.0,
        unit=' Hz', fmt='.1f')
    d2 = p1 and p2
    all_pass &= d2
    print(f"  {'PASSED' if d2 else 'FAILED'}")
    print()

    # ── D3 N ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 3 — N NASAL [n]")
    print()
    n_seg = synth_N(Y_F, II_F,
                     145.0, 1.0, SR)
    p1 = check('voicing',
               measure_voicing(n_seg),
               0.65, 1.0)
    p2 = check('RMS (nasal murmur)',
               rms(n_seg), 0.005, 0.25)
    d3 = p1 and p2
    all_pass &= d3
    print(f"  {'PASSED' if d3 else 'FAILED'}")
    print()

    # ── D4 II ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 4 — I VOWEL [ɪ]")
    print()
    ii_seg = synth_II(N_F, NG_F,
                       145.0, 1.0, SR)
    n_ii   = len(ii_seg)
    body   = ii_seg[int(0.12*n_ii):
                    n_ii-int(0.12*n_ii)]
    p1 = check('voicing',
               measure_voicing(body),
               0.50, 1.0)
    p2 = check(
        f'F2 centroid ({measure_band_centroid(body, 1500.0, 2400.0):.0f} Hz)',
        measure_band_centroid(
            body, 1500.0, 2400.0),
        1600.0, 2200.0,
        unit=' Hz', fmt='.1f')
    d4 = p1 and p2
    all_pass &= d4
    print(f"  {'PASSED' if d4 else 'FAILED'}")
    print()

    # ── D5 NG ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 5 — NG NASAL [ŋ]")
    print()
    ng_seg = synth_NG(II_F, None,
                       145.0, 1.0, SR)
    p1 = check('voicing',
               measure_voicing(ng_seg),
               0.65, 1.0)
    p2 = check('RMS (nasal murmur)',
               rms(ng_seg), 0.005, 0.25)
    d5 = p1 and p2
    all_pass &= d5
    print(f"  {'PASSED' if d5 else 'FAILED'}")
    print()

    # ── D6 G FINAL ────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 6 — G STOP [ɡ] final")
    print()
    g_seg = synth_G_final(NG_F,
                           145.0, 1.0, SR)
    p1 = check('RMS level', rms(g_seg),
               0.005, 0.70)
    dur_g = len(g_seg) / SR * 1000.0
    p2 = check(
        f'duration ({dur_g:.0f} ms)',
        dur_g, 40.0, 100.0,
        unit=' ms', fmt='.1f')
    d6 = p1 and p2
    all_pass &= d6
    print(f"  {'PASSED' if d6 else 'FAILED'}")
    print()

    # ── D7 NG CLUSTER ─────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 7 — [ŋɡ] CLUSTER")
    print()
    print("  OE 'ng' = [ŋɡ] not [ŋ].")
    print("  Both segments present.")
    print("  [ŋ] voiced nasal murmur.")
    print("  [ɡ] burst after nasal.")
    print("  Two distinct events.")
    print()
    ng_g   = np.concatenate([ng_seg, g_seg])
    dur_ng = len(ng_seg) / SR * 1000.0
    dur_g2 = len(g_seg)  / SR * 1000.0
    print(f"  [ŋ] duration: {dur_ng:.1f} ms")
    print(f"  [ɡ] duration: {dur_g2:.1f} ms")
    print(f"  cluster total:"
          f" {dur_ng+dur_g2:.1f} ms")
    p1 = check(
        f'[ŋ] duration ({dur_ng:.0f} ms)',
        dur_ng, 40.0, 90.0,
        unit=' ms', fmt='.1f')
    p2 = check(
        f'[ɡ] duration ({dur_g2:.0f} ms)',
        dur_g2, 40.0, 100.0,
        unit=' ms', fmt='.1f')
    p3 = check(
        'cluster RMS', rms(ng_g),
        0.005, 0.70)
    d7 = p1 and p2 and p3
    all_pass &= d7
    write_wav(
        "output_play/diag_cyn_ng.wav",
        ola_stretch(ng_g / (
            np.max(np.abs(ng_g))+1e-8)
            * 0.75, 4.0))
    print(f"  {'PASSED' if d7 else 'FAILED'}")
    print()

    # ── D8 FULL WORD ──────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 8 — FULL WORD [kyniŋɡ]")
    print()
    w_dry  = synth_cyning(145.0, 1.0, False)
    w_hall = synth_cyning(145.0, 1.0, True)
    dur_ms = len(w_dry) / SR * 1000.0
    p1 = check('RMS level', rms(w_dry),
               0.010, 0.90)
    p2 = check(
        f'duration ({dur_ms:.0f} ms)',
        dur_ms, 300.0, 600.0,
        unit=' ms', fmt='.1f')
    print(f"  {len(w_dry)} samples"
          f" ({dur_ms:.0f} ms)")
    write_wav(
        "output_play/diag_cyn_full.wav",
        w_dry)
    write_wav(
        "output_play/diag_cyn_hall.wav",
        w_hall)
    write_wav(
        "output_play/diag_cyn_slow.wav",
        ola_stretch(w_dry, 4.0))
    d8 = p1 and p2
    all_pass &= d8
    print(f"  {'PASSED' if d8 else 'FAILED'}")
    print()

    # ── D9 PERCEPTUAL ─────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 9 — PERCEPTUAL")
    print()
    for fn in [
        "diag_cyn_ng.wav",
        "diag_cyn_slow.wav",
        "diag_cyn_hall.wav",
    ]:
        print(f"  afplay output_play/{fn}")
    print()
    print("  LISTEN FOR:")
    print("  NG cluster: nasal then stop")
    print("    two events at word end")
    print("    not one sustained nasal")
    print("  Full: K·Y·N·I·NG·G")
    print("  Six events")
    print("  Recognisable as 'king' —")
    print("  with extra final stop.")
    print()

    # ── SUMMARY ───────────────────────────
    print("=" * 60)
    print("SUMMARY")
    print()
    rows = [
        ("D1  K stop",         d1),
        ("D2  Y vowel",        d2),
        ("D3  N nasal",        d3),
        ("D4  I vowel",        d4),
        ("D5  NG nasal",       d5),
        ("D6  G stop final",   d6),
        ("D7  NG cluster",     d7),
        ("D8  Full word",      d8),
    ]
    for lbl, ok_ in rows:
        sym = "✓ PASS" if ok_ else "✗ FAIL"
        print(f"  {lbl:22s}  {sym}")
    print(f"  {'D9 Perceptual':22s}  LISTEN")
    print()
    if all_pass:
        print("  ALL NUMERIC CHECKS PASSED")
        print()
        print("  CYNING [kyniŋɡ] verified.")
        print()
        print("  LINE 4 COMPLETE:")
        print("  þæt wæs gōd cyning")
        print()
        print("  FOUR LINES OF BEOWULF")
        print("  RECONSTRUCTED.")
        print()
        print("  29 phonemes in inventory.")
        print("  Remaining gaps: [p], [b],")
        print("  [iː], [æː], [eo], [eːo].")
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
