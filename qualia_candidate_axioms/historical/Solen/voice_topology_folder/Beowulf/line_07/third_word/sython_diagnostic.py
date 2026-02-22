"""
SYÞÐAN DIAGNOSTIC v1
Old English: syþðan [syθðɑn]
Beowulf line 7, word 3
February 2026

DIAGNOSTICS:
  D1  S fricative [s]
  D2  Y vowel [y]
  D3  TH fricative [θ]
  D4  DH fricative [ð]
  D5  [θð] voicing transition
  D6  A vowel [ɑ]
  D7  N nasal [n]
  D8  Full word
  D9  Perceptual

Zero new phonemes — pure assembly.

KEY CHECK:
  D5 [θð] transition:
     [θ] voicing <= 0.35
     [ð] voicing >= 0.35
     Separation confirmed.
     Same place — tongue does not move.
     Only voicing changes.
     Most minimal consonant contrast
     in the inventory.
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
    print("SYÞÐAN DIAGNOSTIC v1")
    print("Old English [syθðɑn]")
    print("Beowulf line 7, word 3")
    print("=" * 60)
    print()

    try:
        from sython_reconstruction import (
            synth_sython,
            synth_S,  synth_Y,
            synth_TH, synth_DH,
            synth_A,  synth_N,
            apply_simple_room,
            Y_F, A_F, N_F)
        print("  sython_reconstruction.py: OK")
    except ImportError as e:
        print(f"  IMPORT FAILED: {e}")
        return False
    print()

    all_pass = True

    # ── D1 S ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 1 — S FRICATIVE [s]")
    print()
    s_seg  = synth_S(None, Y_F, 1.0, SR)
    cent_s = measure_band_centroid(
        s_seg, 4000.0, 12000.0)
    p1 = check('voicing (must be low)',
               measure_voicing(s_seg),
               0.0, 0.35)
    p2 = check(
        f'centroid ({cent_s:.0f} Hz)',
        cent_s, 5000.0, 10000.0,
        unit=' Hz', fmt='.1f')
    d1 = p1 and p2
    all_pass &= d1
    print(f"  {'PASSED' if d1 else 'FAILED'}")
    print()

    # ── D2 Y ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 2 — Y VOWEL [y]")
    print()
    y_seg  = synth_Y(Y_F, None,
                      145.0, 1.0, SR)
    n_y    = len(y_seg)
    body_y = y_seg[int(0.12*n_y):
                   n_y-int(0.12*n_y)]
    p1 = check('voicing',
               measure_voicing(body_y),
               0.50, 1.0)
    cent_y = measure_band_centroid(
        body_y, 1000.0, 2000.0)
    p2 = check(
        f'F2 centroid ({cent_y:.0f} Hz)',
        cent_y, 1100.0, 1900.0,
        unit=' Hz', fmt='.1f')
    d2 = p1 and p2
    all_pass &= d2
    print(f"  {'PASSED' if d2 else 'FAILED'}")
    print()

    # ── D3 TH ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 3 — TH FRICATIVE [θ]")
    print()
    th_seg  = synth_TH(Y_F, None, 1.0, SR)
    voic_th = measure_voicing(th_seg)
    p1 = check('voicing (must be low)',
               voic_th, 0.0, 0.35)
    p2 = check('RMS level', rms(th_seg),
               0.001, 0.50)
    d3 = p1 and p2
    all_pass &= d3
    print(f"  {'PASSED' if d3 else 'FAILED'}")
    print()

    # ── D4 DH ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 4 — DH FRICATIVE [ð]")
    print()
    dh_seg  = synth_DH(None, A_F,
                        145.0, 1.0, SR)
    voic_dh = measure_voicing(dh_seg)
    p1 = check('voicing (must be high)',
               voic_dh, 0.35, 1.0)
    p2 = check('RMS level', rms(dh_seg),
               0.005, 0.80)
    d4 = p1 and p2
    all_pass &= d4
    print(f"  {'PASSED' if d4 else 'FAILED'}")
    print()

    # ── D5 THETA-DH TRANSITION ────────────
    print("─" * 60)
    print("DIAGNOSTIC 5 — [θð] VOICING"
          " TRANSITION")
    print()
    print("  Same place — tongue at teeth.")
    print("  Only voicing changes.")
    print("  Most minimal contrast"
          " in inventory.")
    print()
    print(f"  [θ] voicing: {voic_th:.4f}")
    print(f"  [ð] voicing: {voic_dh:.4f}")
    separation = voic_dh - voic_th
    print(f"  separation:  {separation:.4f}")
    print()
    p1 = check(
        f'[θ] voiceless ({voic_th:.4f})',
        voic_th, 0.0, 0.35)
    p2 = check(
        f'[ð] voiced ({voic_dh:.4f})',
        voic_dh, 0.35, 1.0)
    p3 = check(
        f'separation ({separation:.4f})',
        separation, 0.10, 1.0)
    d5 = p1 and p2 and p3
    all_pass &= d5
    print(f"  {'PASSED' if d5 else 'FAILED'}")
    print()

    # ── D6 A ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 6 — A VOWEL [ɑ]")
    print()
    a_seg  = synth_A(A_F, N_F,
                      145.0, 1.0, SR)
    n_a    = len(a_seg)
    body_a = a_seg[int(0.12*n_a):
                   n_a-int(0.12*n_a)]
    p1 = check('voicing',
               measure_voicing(body_a),
               0.50, 1.0)
    cent_a = measure_band_centroid(
        body_a, 800.0, 1500.0)
    p2 = check(
        f'F2 centroid ({cent_a:.0f} Hz)',
        cent_a, 900.0, 1400.0,
        unit=' Hz', fmt='.1f')
    d6 = p1 and p2
    all_pass &= d6
    print(f"  {'PASSED' if d6 else 'FAILED'}")
    print()

    # ── D7 N ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 7 — N NASAL [n]")
    print()
    n_seg  = synth_N(A_F, None,
                      145.0, 1.0, SR)
    p1 = check('voicing',
               measure_voicing(n_seg),
               0.65, 1.0)
    p2 = check('RMS (nasal murmur)',
               rms(n_seg), 0.005, 0.25)
    d7 = p1 and p2
    all_pass &= d7
    print(f"  {'PASSED' if d7 else 'FAILED'}")
    print()

    # ── D8 FULL WORD ──────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 8 — FULL WORD [syθðɑn]")
    print()
    w_dry  = synth_sython(145.0, 1.0, False)
    w_hall = synth_sython(145.0, 1.0, True)
    dur_ms = len(w_dry) / SR * 1000.0
    p1 = check('RMS level', rms(w_dry),
               0.010, 0.90)
    p2 = check(
        f'duration ({dur_ms:.0f} ms)',
        dur_ms, 340.0, 560.0,
        unit=' ms', fmt='.1f')
    print(f"  {len(w_dry)} samples"
          f" ({dur_ms:.0f} ms)")
    write_wav(
        "output_play/diag_sython_full.wav",
        w_dry)
    write_wav(
        "output_play/diag_sython_hall.wav",
        w_hall)
    write_wav(
        "output_play/diag_sython_slow.wav",
        ola_stretch(w_dry, 4.0))
    th_seg2 = synth_TH(Y_F, None, 1.0, SR)
    dh_seg2 = synth_DH(None, A_F,
                        145.0, 1.0, SR)
    cluster = np.concatenate(
        [th_seg2, dh_seg2])
    mx_c = np.max(np.abs(cluster))
    if mx_c > 1e-8:
        cluster = f32(cluster / mx_c * 0.75)
    write_wav(
        "output_play/diag_sython_thDH.wav",
        ola_stretch(cluster, 4.0))
    d8 = p1 and p2
    all_pass &= d8
    print(f"  {'PASSED' if d8 else 'FAILED'}")
    print()

    # ── D9 PERCEPTUAL ─────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 9 — PERCEPTUAL")
    print()
    for fn in [
        "diag_sython_thDH.wav",
        "diag_sython_slow.wav",
        "diag_sython_hall.wav",
    ]:
        print(f"  afplay output_play/{fn}")
    print()
    print("  LISTEN FOR:")
    print("  S  — sharp voiceless onset")
    print("  Y  — rounded front vowel")
    print("    like German 'ü'")
    print("  TH — voiceless dental")
    print("  DH — voiced dental")
    print("    same tongue position")
    print("    voice switches on")
    print("  A  — open back vowel")
    print("  N  — nasal close")
    print("  Full: S·Y·TH·DH·A·N")
    print("  Six events.")
    print("  'sü-th-dhan'")
    print("  approximately.")
    print()

    # ── SUMMARY ───────────────────────────
    print("=" * 60)
    print("SUMMARY")
    print()
    rows = [
        ("D1  S fricative",       d1),
        ("D2  Y vowel",           d2),
        ("D3  TH fricative",      d3),
        ("D4  DH fricative",      d4),
        ("D5  THDH transition",   d5),
        ("D6  A vowel",           d6),
        ("D7  N nasal",           d7),
        ("D8  Full word",         d8),
    ]
    for lbl, ok_ in rows:
        sym = "✓ PASS" if ok_ else "✗ FAIL"
        print(f"  {lbl:24s}  {sym}")
    print(f"  {'D9 Perceptual':24s}  LISTEN")
    print()
    if all_pass:
        print("  ALL NUMERIC CHECKS PASSED")
        print()
        print("  SYÞÐAN [syθðɑn] verified.")
        print("  Zero new phonemes.")
        print("  35 phonemes verified.")
        print()
        print("  Next: ǢREST [æːrest]")
        print("  Beowulf line 7, word 4.")
        print("  Zero new phonemes.")
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
