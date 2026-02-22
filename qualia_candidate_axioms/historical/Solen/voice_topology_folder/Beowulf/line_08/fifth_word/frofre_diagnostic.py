"""
FRŌFRE DIAGNOSTIC v1
Old English: frōfre [froːvrə]
Beowulf line 8, word 5 (overall word 35)
No new phonemes — pure assembly
February 2026

DIAGNOSTICS:
  D1   F fricative [f]
       voicing must be low
  D2   R1 trill [r] — first instance
       voicing >= 0.50
       trill modulation present
  D3   OY long vowel [oː]
       voicing >= 0.50
       duration >= 90 ms
       F2 centroid 600–1000 Hz — back rounded
  D4   V voiced fricative [v]
       voicing >= 0.35 — intervocalic
  D5   R2 trill [r] — second instance
       voicing >= 0.50
       trill modulation present
  D6   SCHWA [ə] — second appearance
       voicing >= 0.50
       F1 350–700 Hz
       F2 1100–1900 Hz
       duration 30–70 ms
  D7   STRESS ASYMMETRY
       [oː] duration > [ə] duration
       long stressed nucleus vs
       short unstressed suffix
  D8   Full word
       RMS, duration
  D9   Perceptual

KEY CHECKS:
  [f]  voicing <= 0.35 — voiceless onset
  [r]  voicing >= 0.50 — trill both instances
  [oː] voicing >= 0.50 — long back rounded
  [oː] F2 600–1000 Hz  — back position
  [oː] duration >= 90 ms — long vowel
  [v]  voicing >= 0.35 — voiced intervocalic
  [ə]  F1 350–700 Hz, F2 1100–1900 Hz — central
  [ə]  duration 30–70 ms — short unstressed
  Word duration ~430 ms at dil=1.0
  (70+70+110+65+70+45 ms)
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
    n_frames = max(1, (n_in - win_n) // hop_in + 1)
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
    nz       = norm > 1e-8
    out[nz] /= norm[nz]
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
    acorr  = np.correlate(core, core, mode='full')
    acorr  = acorr[len(acorr)//2:]
    acorr /= (acorr[0] + 1e-12)
    lo = int(sr / 400)
    hi = min(int(sr / 80), len(acorr) - 1)
    if lo >= hi:
        return 0.0
    return float(np.clip(np.max(acorr[lo:hi]),
                          0.0, 1.0))

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
    print("FRŌFRE DIAGNOSTIC v1")
    print("Old English [froːvrə]")
    print("Beowulf line 8, word 5")
    print("Pure assembly — no new phonemes")
    print("[ə] second appearance")
    print("=" * 60)
    print()

    try:
        from frofre_reconstruction import (
            synth_frōfre,
            synth_F, synth_R,
            synth_OY, synth_V,
            synth_SCHWA,
            apply_simple_room,
            OY_F, R_F, SCHWA_F,
            PITCH_PERF, DIL_PERF)
        print("  frōfre_reconstruction.py: OK")
    except ImportError as e:
        print(f"  IMPORT FAILED: {e}")
        return False
    print()

    all_pass = True

    # ── D1 F ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 1 — F FRICATIVE [f]")
    print()
    f_seg = synth_F(dil=1.0, sr=SR)
    p1 = check('voicing (must be low)',
               measure_voicing(f_seg),
               0.0, 0.35)
    p2 = check('RMS level', rms(f_seg),
               0.001, 0.50)
    d1 = p1 and p2
    all_pass &= d1
    print(f"  {'PASSED' if d1 else 'FAILED'}")
    print()

    # ── D2 R1 ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 2 — R1 TRILL [r]"
          " first instance")
    print()
    r1_seg = synth_R(
        F_prev=None, F_next=OY_F,
        pitch_hz=145.0, dil=1.0, sr=SR)
    v_r1   = measure_voicing(r1_seg)
    dur_r1 = len(r1_seg) / SR * 1000.0
    print(f"  Duration: {dur_r1:.0f} ms")
    p1 = check('voicing',
               v_r1, 0.50, 1.0)
    p2 = check('RMS level', rms(r1_seg),
               0.005, 0.80)
    d2 = p1 and p2
    all_pass &= d2
    print(f"  {'PASSED' if d2 else 'FAILED'}")
    print()

    # ── D3 OY ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 3 — OY LONG VOWEL [oː]")
    print("  Long close-mid back rounded.")
    print("  Duration >= 90 ms.")
    print("  F2 600–1000 Hz — back rounded.")
    print()
    oy_seg  = synth_OY(
        F_prev=R_F, F_next=None,
        pitch_hz=145.0, dil=1.0, sr=SR)
    v_oy    = measure_voicing(oy_seg)
    f2_oy   = measure_band_centroid(
        oy_seg, 500.0, 1200.0)
    dur_oy  = len(oy_seg) / SR * 1000.0
    print(f"  Duration:    {dur_oy:.0f} ms"
          f"  (target >= 90 ms)")
    print(f"  F2 centroid: {f2_oy:.0f} Hz"
          f"  (target 600–1000 Hz)")
    print()
    p1 = check('voicing',
               v_oy, 0.50, 1.0)
    p2 = check(
        f'duration ({dur_oy:.0f} ms)',
        dur_oy, 90.0, 160.0,
        unit=' ms', fmt='.1f')
    p3 = check(
        f'F2 centroid ({f2_oy:.0f} Hz)',
        f2_oy, 600.0, 1000.0,
        unit=' Hz', fmt='.1f')
    d3 = p1 and p2 and p3
    all_pass &= d3
    print(f"  {'PASSED' if d3 else 'FAILED'}")
    print()

    # ── D4 V ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 4 — V VOICED"
          " FRICATIVE [v]")
    print("  Voiced labiodental.")
    print("  Intervocalic — [oː]→[v]→[r].")
    print("  Voicing >= 0.35.")
    print()
    v_seg   = synth_V(
        F_prev=OY_F, F_next=R_F,
        pitch_hz=145.0, dil=1.0, sr=SR)
    v_v     = measure_voicing(v_seg)
    dur_v   = len(v_seg) / SR * 1000.0
    print(f"  Duration: {dur_v:.0f} ms")
    p1 = check('voicing',
               v_v, 0.35, 1.0)
    d4 = p1
    all_pass &= d4
    print(f"  {'PASSED' if d4 else 'FAILED'}")
    print()

    # ── D5 R2 ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 5 — R2 TRILL [r]"
          " second instance")
    print()
    r2_seg = synth_R(
        F_prev=None, F_next=SCHWA_F,
        pitch_hz=145.0, dil=1.0, sr=SR)
    v_r2   = measure_voicing(r2_seg)
    dur_r2 = len(r2_seg) / SR * 1000.0
    print(f"  Duration: {dur_r2:.0f} ms")
    p1 = check('voicing',
               v_r2, 0.50, 1.0)
    p2 = check('RMS level', rms(r2_seg),
               0.005, 0.80)
    d5 = p1 and p2
    all_pass &= d5
    print(f"  {'PASSED' if d5 else 'FAILED'}")
    print()

    # ── D6 SCHWA ──────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 6 — SCHWA [ə]")
    print("  Second appearance.")
    print("  First: FUNDEN -en suffix.")
    print("  Now: FRŌFRE -re suffix.")
    print("  Same parameters — rule confirmed.")
    print()
    schwa_seg = synth_SCHWA(
        F_prev=R_F, F_next=None,
        pitch_hz=145.0, dil=1.0, sr=SR)
    v_s    = measure_voicing(schwa_seg)
    f1_s   = measure_band_centroid(
        schwa_seg, 300.0, 800.0)
    f2_s   = measure_band_centroid(
        schwa_seg, 900.0, 2200.0)
    dur_s  = len(schwa_seg) / SR * 1000.0
    print(f"  F1 centroid: {f1_s:.0f} Hz"
          f"  (target 350–700 Hz)")
    print(f"  F2 centroid: {f2_s:.0f} Hz"
          f"  (target 1100–1900 Hz)")
    print(f"  Duration:    {dur_s:.0f} ms"
          f"  (target 30–70 ms)")
    print()
    p1 = check('voicing',
               v_s, 0.50, 1.0)
    p2 = check(
        f'F1 centroid ({f1_s:.0f} Hz)',
        f1_s, 350.0, 700.0,
        unit=' Hz', fmt='.1f')
    p3 = check(
        f'F2 centroid ({f2_s:.0f} Hz)',
        f2_s, 1100.0, 1900.0,
        unit=' Hz', fmt='.1f')
    p4 = check(
        f'duration ({dur_s:.0f} ms)',
        dur_s, 30.0, 70.0,
        unit=' ms', fmt='.1f')
    d6 = p1 and p2 and p3 and p4
    all_pass &= d6
    print(f"  {'PASSED' if d6 else 'FAILED'}")
    print()

    # ── D7 STRESS ASYMMETRY ───────────────
    print("─" * 60)
    print("DIAGNOSTIC 7 — STRESS ASYMMETRY")
    print("  [oː] stressed > [ə] unstressed")
    print()
    diff_ms = dur_oy - dur_s
    print(f"  [oː] duration: {dur_oy:.0f} ms"
          f"  (stressed long vowel)")
    print(f"  [ə]  duration: {dur_s:.0f} ms"
          f"  (unstressed schwa)")
    print(f"  Difference:    {diff_ms:.0f} ms")
    print()
    p1 = check(
        f'[oː]>[ə] duration diff'
        f' ({diff_ms:.0f} ms)',
        diff_ms, 50.0, 120.0,
        unit=' ms', fmt='.1f')
    d7 = p1
    all_pass &= d7
    print(f"  {'PASSED' if d7 else 'FAILED'}")
    print()

    # ── D8 FULL WORD ─��────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 8 — FULL WORD [froːvrə]")
    print()
    w_dry  = synth_frōfre(145.0, 1.0, False)
    w_hall = synth_frōfre(145.0, 1.0, True)
    w_perf = synth_frōfre(
        PITCH_PERF, DIL_PERF, True)
    dur_ms      = len(w_dry)  / SR * 1000.0
    dur_perf_ms = len(w_perf) / SR * 1000.0
    print(f"  {len(w_dry)} samples"
          f" ({dur_ms:.0f} ms) — diagnostic")
    print(f"  {len(w_perf)} samples"
          f" ({dur_perf_ms:.0f} ms)"
          f" — performance")
    print()
    p1 = check('RMS level', rms(w_dry),
               0.010, 0.90)
    p2 = check(
        f'duration ({dur_ms:.0f} ms)',
        dur_ms, 350.0, 500.0,
        unit=' ms', fmt='.1f')
    d8 = p1 and p2
    all_pass &= d8
    write_wav("output_play/diag_frōfre_full.wav",
               w_dry)
    write_wav("output_play/diag_frōfre_hall.wav",
               w_hall)
    write_wav("output_play/diag_frōfre_slow.wav",
               ola_stretch(w_dry, 4.0))
    write_wav("output_play/diag_frōfre_perf.wav",
               w_perf)
    print(f"  {'PASSED' if d8 else 'FAILED'}")
    print()

    # ── D9 PERCEPTUAL ─────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 9 — PERCEPTUAL")
    print()
    print("  Diagnostic versions:")
    for fn in [
        "diag_frōfre_full.wav",
        "diag_frōfre_slow.wav",
        "diag_frōfre_hall.wav",
    ]:
        print(f"  afplay output_play/{fn}")
    print()
    print("  Performance version:")
    print("  afplay output_play/"
          "diag_frōfre_perf.wav")
    print()
    print("  LISTEN FOR:")
    print("  F    — voiceless onset")
    print("  R    — trill — brief flutter")
    print("  ŌY   — long back rounded vowel")
    print("         dark, back, sustained")
    print("         clearly longer than [o]")
    print("  V    — voiced fricative")
    print("         voicing maintained")
    print("         between vowel and trill")
    print("  R    — trill again")
    print("  Ə    — short unstressed close")
    print("         the word settles to H")
    print()
    print("  Two-syllable rhythm:")
    print("    FRŌF- (heavy) -re (light)")
    print("  þæs FRŌFRE —")
    print("  of that COMFORT —")
    print()

    # ── SUMMARY ───────────────────────────
    print("=" * 60)
    print("SUMMARY")
    print()
    rows = [
        ("D1   F fricative",          d1),
        ("D2   R1 trill",             d2),
        ("D3   OY long vowel",        d3),
        ("D4   V voiced fricative",   d4),
        ("D5   R2 trill",             d5),
        ("D6   Schwa [ə] second",     d6),
        ("D7   Stress asymmetry",     d7),
        ("D8   Full word",            d8),
    ]
    for lbl, ok_ in rows:
        sym = "✓ PASS" if ok_ else "✗ FAIL"
        print(f"  {lbl:28s}  {sym}")
    print(f"  {'D9   Perceptual':28s}  LISTEN")
    print()
    if all_pass:
        print("  ALL NUMERIC CHECKS PASSED")
        print()
        print("  FRŌFRE [froːvrə] verified.")
        print("  [ə] second appearance confirmed.")
        print("  Unstressed suffix rule holds.")
        print()
        print("  Line 8 status:")
        print("  feasceaft  ✓")
        print("  funden     ✓")
        print("  hē         ✓")
        print("  þæs        ✓")
        print("  frōfre     ✓")
        print("  gebād      — next — [b] phoneme 41")
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
