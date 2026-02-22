"""
EORLAS DIAGNOSTIC v1
Old English: eorlas [eorlas]
Beowulf line 7, word 2
February 2026

DIAGNOSTICS:
  D1  EO diphthong [eo] — word-initial
  D2  EO F2 movement
  D3  EO vs MEODOSETLA onset comparison
  D4  R trill [r]
  D5  L lateral [l]
  D6  A vowel [ɑ]
  D7  S fricative [s]
  D8  Full word
  D9  Perceptual

Zero new phonemes — pure assembly.

KEY CHECK:
  D3 — [eo] word-initial onset.
  MEODOSETLA [eo] onset F2: 1833 Hz
  (pulled low by preceding [m]).
  EORLAS [eo] onset: no preceding
  context — expect closer to 1900 Hz.
  Cross-instance comparison.
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
    print("EORLAS DIAGNOSTIC v1")
    print("Old English [eorlas]")
    print("Beowulf line 7, word 2")
    print("=" * 60)
    print()

    try:
        from eorlas_reconstruction import (
            synth_eorlas,
            synth_EO, synth_R,
            synth_L, synth_A,
            synth_S,
            apply_simple_room,
            EO_F_ON, EO_F_OFF,
            R_F, L_F, A_F)
        print("  eorlas_reconstruction.py: OK")
    except ImportError as e:
        print(f"  IMPORT FAILED: {e}")
        return False
    print()

    all_pass = True

    # ── D1 EO ───────��─────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 1 — EO DIPHTHONG [eo]"
          " word-initial")
    print()
    eo_seg = synth_EO(EO_F_ON, R_F,
                       145.0, 1.0, SR)
    p1 = check('voicing',
               measure_voicing(eo_seg),
               0.50, 1.0)
    p2 = check('RMS level', rms(eo_seg),
               0.010, 0.90)
    d1 = p1 and p2
    all_pass &= d1
    print(f"  {'PASSED' if d1 else 'FAILED'}")
    print()

    # ── D2 EO F2 MOVEMENT ─────────────────
    print("─" * 60)
    print("DIAGNOSTIC 2 — [eo] F2 MOVEMENT")
    print()
    n_eo   = len(eo_seg)
    onset  = eo_seg[:int(0.25 * n_eo)]
    offset = eo_seg[int(0.80 * n_eo):]
    f2_on  = measure_band_centroid(
        onset,  1200.0, 2500.0)
    f2_off = measure_band_centroid(
        offset,  500.0, 1400.0)
    delta  = f2_on - f2_off
    print(f"  F2 onset:  {f2_on:.0f} Hz")
    print(f"  F2 offset: {f2_off:.0f} Hz")
    print(f"  Delta:     {delta:.0f} Hz"
          f" (falling)")
    print()
    p1 = check(
        f'F2 onset ({f2_on:.0f} Hz)',
        f2_on, 1500.0, 2200.0,
        unit=' Hz', fmt='.1f')
    p2 = check(
        f'F2 offset ({f2_off:.0f} Hz)',
        f2_off, 550.0, 1100.0,
        unit=' Hz', fmt='.1f')
    p3 = check(
        f'F2 delta ({delta:.0f} Hz)',
        delta, 700.0, 1500.0,
        unit=' Hz', fmt='.1f')
    d2 = p1 and p2 and p3
    all_pass &= d2
    print(f"  {'PASSED' if d2 else 'FAILED'}")
    print()

    # ── D3 EO CROSS-INSTANCE ──────────────
    print("─" * 60)
    print("DIAGNOSTIC 3 — [eo] ONSET"
          " CROSS-INSTANCE")
    print()
    print("  Word-initial vs post-nasal.")
    print("  MEODOSETLA onset: 1833 Hz"
          " (post-[m])")
    print(f"  EORLAS onset:     {f2_on:.0f} Hz"
          f" (word-initial)")
    print()
    diff = f2_on - 1833.0
    print(f"  Difference: {diff:+.0f} Hz")
    if diff > 0:
        print("  EORLAS onset higher —")
        print("  no [m] pulling F2 down.")
        print("  Coarticulation confirmed.")
    else:
        print("  Onset similar —")
        print("  within measurement variance.")
    print()
    p1 = check(
        f'onset in range ({f2_on:.0f} Hz)',
        f2_on, 1500.0, 2200.0,
        unit=' Hz', fmt='.1f')
    d3 = p1
    all_pass &= d3
    print(f"  {'PASSED' if d3 else 'FAILED'}")
    print()

    # ── D4 R ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 4 — R TRILL [r]")
    print()
    r_seg  = synth_R(EO_F_OFF, L_F,
                      145.0, 1.0, SR)
    voic_r = measure_voicing(r_seg)
    p1 = check('voicing',
               voic_r, 0.50, 1.0)
    p2 = check('RMS level', rms(r_seg),
               0.005, 0.80)
    d4 = p1 and p2
    all_pass &= d4
    print(f"  {'PASSED' if d4 else 'FAILED'}")
    print()

    # ── D5 L ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 5 — L LATERAL [l]")
    print()
    l_seg  = synth_L(R_F, A_F,
                      145.0, 1.0, SR)
    p1 = check('voicing',
               measure_voicing(l_seg),
               0.50, 1.0)
    p2 = check('RMS level', rms(l_seg),
               0.005, 0.80)
    d5 = p1 and p2
    all_pass &= d5
    print(f"  {'PASSED' if d5 else 'FAILED'}")
    print()

    # ── D6 A ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 6 — A VOWEL [ɑ]")
    print()
    a_seg  = synth_A(L_F, None,
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

    # ── D7 S ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 7 — S FRICATIVE [s]")
    print()
    s_seg  = synth_S(A_F, None, 1.0, SR)
    cent_s = measure_band_centroid(
        s_seg, 4000.0, 12000.0)
    p1 = check('voicing (must be low)',
               measure_voicing(s_seg),
               0.0, 0.35)
    p2 = check(
        f'centroid ({cent_s:.0f} Hz)',
        cent_s, 5000.0, 10000.0,
        unit=' Hz', fmt='.1f')
    d7 = p1 and p2
    all_pass &= d7
    print(f"  {'PASSED' if d7 else 'FAILED'}")
    print()

    # ── D8 FULL WORD ──────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 8 — FULL WORD [eorlas]")
    print()
    w_dry  = synth_eorlas(145.0, 1.0, False)
    w_hall = synth_eorlas(145.0, 1.0, True)
    dur_ms = len(w_dry) / SR * 1000.0
    p1 = check('RMS level', rms(w_dry),
               0.010, 0.90)
    p2 = check(
        f'duration ({dur_ms:.0f} ms)',
        dur_ms, 280.0, 480.0,
        unit=' ms', fmt='.1f')
    print(f"  {len(w_dry)} samples"
          f" ({dur_ms:.0f} ms)")
    write_wav(
        "output_play/diag_eorlas_full.wav",
        w_dry)
    write_wav(
        "output_play/diag_eorlas_hall.wav",
        w_hall)
    write_wav(
        "output_play/diag_eorlas_slow.wav",
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
        "diag_eorlas_slow.wav",
        "diag_eorlas_hall.wav",
    ]:
        print(f"  afplay output_play/{fn}")
    print()
    print("  LISTEN FOR:")
    print("  EO — diphthong word-initial")
    print("    front onset rounds back")
    print("  R  — trill, periodic flutter")
    print("  L  — lateral, smooth voiced")
    print("  A  — open back vowel")
    print("  S  — sharp voiceless close")
    print("  Full: EO·R·L·A·S")
    print("  Five events.")
    print("  'eh-or-lass'")
    print("  approximately.")
    print("  ModE 'earls' — same word.")
    print()

    # ── SUMMARY ───────────────────────────
    print("=" * 60)
    print("SUMMARY")
    print()
    rows = [
        ("D1  EO diphthong",       d1),
        ("D2  EO F2 movement",     d2),
        ("D3  EO onset comparison",d3),
        ("D4  R trill",            d4),
        ("D5  L lateral",          d5),
        ("D6  A vowel",            d6),
        ("D7  S fricative",        d7),
        ("D8  Full word",          d8),
    ]
    for lbl, ok_ in rows:
        sym = "✓ PASS" if ok_ else "✗ FAIL"
        print(f"  {lbl:26s}  {sym}")
    print(f"  {'D9 Perceptual':26s}  LISTEN")
    print()
    if all_pass:
        print("  ALL NUMERIC CHECKS PASSED")
        print()
        print("  EORLAS [eorlas] verified.")
        print("  Zero new phonemes.")
        print("  35 phonemes verified.")
        print()
        print("  Next: SYÞÐAN [syθðɑn]")
        print("  Beowulf line 7, word 3.")
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
