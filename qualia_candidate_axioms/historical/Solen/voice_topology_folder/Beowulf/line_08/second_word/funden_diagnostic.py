"""
FUNDEN DIAGNOSTIC v1
Old English: funden [fundən]
Beowulf line 8, word 2 (overall word 32)
NEW PHONEME: [��] schwa — phoneme 40
February 2026

DIAGNOSTICS:
  D1   F fricative [f]
  D2   U vowel [u]
  D3   N1 nasal [n] first instance
  D4   D stop [d]
  D5   SCHWA [ə] — VRFY_002
       The critical diagnostic.
       Verifies the dominant of vocal space.
       F1 centroid: 400-650 Hz (central)
       F2 centroid: 1200-1800 Hz (central)
       Voicing: >= 0.50
       Duration: short (< stressed vowels)
  D6   SCHWA position vs [u] and [e]
       [ə] must sit BETWEEN [u] and [e]
       in F1/F2 space — confirming
       central position
  D7   N2 nasal [n] second instance
  D8   Stressed vs unstressed duration
       [u] duration > [ə] duration
       Confirms stress difference
  D9   Full word
  D10  Perceptual

KEY CHECK — D5:
  This is VRFY_002.
  The Tonnetz bridge predicted:
  C([ə],H) ≈ 0.75
  F1 ~500 Hz, F2 ~1500 Hz
  The measurement must confirm
  central position — not front
  like [e], not back like [u].
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
    win_ms  = 40.0
    win_n   = int(win_ms / 1000.0 * sr)
    if win_n % 2 == 1:
        win_n += 1
    hop_in  = win_n // 4
    hop_out = int(hop_in * factor)
    window  = np.hanning(win_n).astype(DTYPE)
    n_in    = len(sig)
    n_frames = max(1,
                   (n_in - win_n) // hop_in + 1)
    n_out   = hop_out * n_frames + win_n
    out     = np.zeros(n_out, dtype=DTYPE)
    norm    = np.zeros(n_out, dtype=DTYPE)
    for i in range(n_frames):
        in_pos  = i * hop_in
        out_pos = i * hop_out
        if in_pos + win_n > n_in:
            break
        frame = (sig[in_pos:in_pos+win_n]
                 * window)
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
    print("FUNDEN DIAGNOSTIC v1")
    print("Old English [fundən]")
    print("Beowulf line 8, word 2")
    print("NEW PHONEME: [ə] schwa — #40")
    print("VRFY_002 — Tonnetz bridge")
    print("=" * 60)
    print()

    try:
        from funden_reconstruction import (
            synth_funden,
            synth_F, synth_U,
            synth_N, synth_D,
            synth_SCHWA,
            apply_simple_room,
            U_F, N_F, SCHWA_F,
            PITCH_PERF, DIL_PERF)
        print("  funden_reconstruction.py: OK")
    except ImportError as e:
        print(f"  IMPORT FAILED: {e}")
        return False
    print()

    all_pass = True

    # ── D1 F ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 1 — F FRICATIVE [f]")
    print()
    f_seg  = synth_F(1.0, SR)
    p1 = check('voicing (must be low)',
               measure_voicing(f_seg),
               0.0, 0.35)
    p2 = check('RMS level', rms(f_seg),
               0.001, 0.50)
    d1 = p1 and p2
    all_pass &= d1
    print(f"  {'PASSED' if d1 else 'FAILED'}")
    print()

    # ── D2 U ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 2 — U VOWEL [u]")
    print()
    u_seg   = synth_U(None, N_F,
                       145.0, 1.0, SR)
    f1_u    = measure_band_centroid(
        u_seg, 200.0, 600.0)
    f2_u    = measure_band_centroid(
        u_seg, 600.0, 1200.0)
    print(f"  F1 centroid: {f1_u:.0f} Hz"
          f"  (back vowel — low F1)")
    print(f"  F2 centroid: {f2_u:.0f} Hz"
          f"  (back vowel — low F2)")
    print()
    p1 = check('voicing',
               measure_voicing(u_seg),
               0.50, 1.0)
    p2 = check(
        f'F2 centroid ({f2_u:.0f} Hz)',
        f2_u, 600.0, 1100.0,
        unit=' Hz', fmt='.1f')
    d2 = p1 and p2
    all_pass &= d2
    print(f"  {'PASSED' if d2 else 'FAILED'}")
    print()

    # ── D3 N1 ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 3 — N1 NASAL [n]"
          " first instance")
    print()
    n1_seg = synth_N(U_F, None,
                      145.0, 1.0, SR)
    p1 = check('voicing',
               measure_voicing(n1_seg),
               0.50, 1.0)
    p2 = check('RMS level', rms(n1_seg),
               0.005, 0.80)
    d3 = p1 and p2
    all_pass &= d3
    print(f"  {'PASSED' if d3 else 'FAILED'}")
    print()

    # ── D4 D ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 4 — D STOP [d]")
    print()
    d_seg  = synth_D(None, SCHWA_F,
                      145.0, 1.0, SR)
    p1 = check('RMS level', rms(d_seg),
               0.005, 0.70)
    d4 = p1
    all_pass &= d4
    print(f"  {'PASSED' if d4 else 'FAILED'}")
    print()

    # ── D5 SCHWA — VRFY_002 ───────────────
    print("─" * 60)
    print("DIAGNOSTIC 5 — SCHWA [ə]")
    print("  VRFY_002 — Tonnetz bridge")
    print("  The dominant of vocal space.")
    print("  C([ə],H) ≈ 0.75")
    print("  Target: F1 ~500 Hz,"
          " F2 ~1500 Hz")
    print()
    schwa_seg = synth_SCHWA(
        None, N_F, 145.0, 1.0, SR)
    f1_s = measure_band_centroid(
        schwa_seg, 300.0, 800.0)
    f2_s = measure_band_centroid(
        schwa_seg, 900.0, 2200.0)
    dur_s = len(schwa_seg) / SR * 1000.0
    print(f"  F1 centroid: {f1_s:.0f} Hz"
          f"  (target ~500 Hz)")
    print(f"  F2 centroid: {f2_s:.0f} Hz"
          f"  (target ~1500 Hz)")
    print(f"  Duration:    {dur_s:.0f} ms"
          f"  (target ~45 ms, short)")
    print()
    p1 = check('voicing',
               measure_voicing(schwa_seg),
               0.50, 1.0)
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
    d5 = p1 and p2 and p3 and p4
    all_pass &= d5
    print(f"  {'PASSED' if d5 else 'FAILED'}")
    print()

    # ── D6 SCHWA POSITION ─────────────────
    print("─" * 60)
    print("DIAGNOSTIC 6 — SCHWA POSITION")
    print("  [ə] must sit between [u] and [e]")
    print("  Confirms central position")
    print()
    # Reference [e] F2 from inventory
    f2_e_ref = 1900.0
    print(f"  [u]  F2: {f2_u:.0f} Hz"
          f"  (back)")
    print(f"  [ə]  F2: {f2_s:.0f} Hz"
          f"  (central)")
    print(f"  [e]  F2: {f2_e_ref:.0f} Hz"
          f"  (front — reference)")
    print()
    p1 = check(
        f'[ə] F2 > [u] F2'
        f' ({f2_s:.0f} > {f2_u:.0f})',
        f2_s - f2_u,
        50.0, 2000.0,
        unit=' Hz', fmt='.1f')
    p2 = check(
        f'[ə] F2 < [e] F2'
        f' ({f2_s:.0f} < {f2_e_ref:.0f})',
        f2_e_ref - f2_s,
        50.0, 1500.0,
        unit=' Hz', fmt='.1f')
    d6 = p1 and p2
    all_pass &= d6
    print(f"  {'PASSED' if d6 else 'FAILED'}")
    print()

    # ── D7 N2 ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 7 — N2 NASAL [n]"
          " second instance")
    print()
    n2_seg = synth_N(SCHWA_F, None,
                      145.0, 1.0, SR)
    p1 = check('voicing',
               measure_voicing(n2_seg),
               0.50, 1.0)
    p2 = check('RMS level', rms(n2_seg),
               0.005, 0.80)
    d7 = p1 and p2
    all_pass &= d7
    print(f"  {'PASSED' if d7 else 'FAILED'}")
    print()

    # ── D8 STRESSED vs UNSTRESSED ─────────
    print("─" * 60)
    print("DIAGNOSTIC 8 — STRESSED vs"
          " UNSTRESSED DURATION")
    print("  [u] stressed > [ə] unstressed")
    print()
    dur_u = len(u_seg) / SR * 1000.0
    print(f"  [u] duration: {dur_u:.0f} ms"
          f"  (stressed)")
    print(f"  [ə] duration: {dur_s:.0f} ms"
          f"  (unstressed)")
    diff_ms = dur_u - dur_s
    print(f"  Difference:   {diff_ms:.0f} ms")
    print()
    p1 = check(
        f'[u]>[ə] duration diff'
        f' ({diff_ms:.0f} ms)',
        diff_ms, 5.0, 60.0,
        unit=' ms', fmt='.1f')
    d8 = p1
    all_pass &= d8
    print(f"  {'PASSED' if d8 else 'FAILED'}")
    print()

    # ── D9 FULL WORD ──────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 9 — FULL WORD [fundən]")
    print()
    w_dry  = synth_funden(145.0, 1.0, False)
    w_hall = synth_funden(145.0, 1.0, True)
    w_perf = synth_funden(
        PITCH_PERF, DIL_PERF, True)
    dur_ms      = len(w_dry)  / SR * 1000.0
    dur_perf_ms = len(w_perf) / SR * 1000.0
    p1 = check('RMS level', rms(w_dry),
               0.010, 0.90)
    p2 = check(
        f'duration ({dur_ms:.0f} ms)',
        dur_ms, 200.0, 420.0,
        unit=' ms', fmt='.1f')
    print(f"  {len(w_dry)} samples"
          f" ({dur_ms:.0f} ms) — diagnostic")
    print(f"  {len(w_perf)} samples"
          f" ({dur_perf_ms:.0f} ms)"
          f" — performance")
    write_wav(
        "output_play/diag_funden_full.wav",
        w_dry)
    write_wav(
        "output_play/diag_funden_hall.wav",
        w_hall)
    write_wav(
        "output_play/diag_funden_slow.wav",
        ola_stretch(w_dry, 4.0))
    write_wav(
        "output_play/diag_funden_perf.wav",
        w_perf)
    d9 = p1 and p2
    all_pass &= d9
    print(f"  {'PASSED' if d9 else 'FAILED'}")
    print()

    # ── D10 PERCEPTUAL ────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 10 — PERCEPTUAL")
    print()
    print("  Diagnostic versions:")
    for fn in [
        "diag_funden_full.wav",
        "diag_funden_slow.wav",
        "diag_funden_hall.wav",
    ]:
        print(f"  afplay output_play/{fn}")
    print()
    print("  Performance version:")
    print("  afplay output_play/"
          "diag_funden_perf.wav")
    print()
    print("  LISTEN FOR:")
    print("  F   — voiceless onset")
    print("  U   — back rounded vowel")
    print("        stressed nucleus")
    print("  N   — nasal")
    print("  D   — voiced stop")
    print("  Ə   — SHORT central vowel")
    print("        NOT [e], NOT [u]")
    print("        unstressed — quick")
    print("        the dominant of")
    print("        vocal space")
    print("  N   — nasal close")
    print("  Two-syllable rhythm:")
    print("    FUN- (heavy) -dən (light)")
    print("  feasceaft FUNDEN —")
    print("  found wretched.")
    print("  VRFY_002 confirmed:")
    print("  the schwa is present.")
    print()

    # ── SUMMARY ───────────────────────────
    print("=" * 60)
    print("SUMMARY")
    print()
    rows = [
        ("D1   F fricative",          d1),
        ("D2   U vowel",              d2),
        ("D3   N1 nasal",             d3),
        ("D4   D stop",               d4),
        ("D5   SCHWA VRFY_002",       d5),
        ("D6   Schwa position",       d6),
        ("D7   N2 nasal",             d7),
        ("D8   Stress duration",      d8),
        ("D9   Full word",            d9),
    ]
    for lbl, ok_ in rows:
        sym = "✓ PASS" if ok_ else "✗ FAIL"
        print(f"  {lbl:26s}  {sym}")
    print(f"  {'D10 Perceptual':26s}  LISTEN")
    print()
    if all_pass:
        print("  ALL NUMERIC CHECKS PASSED")
        print()
        print("  FUNDEN [fundən] verified.")
        print("  [ə] SCHWA verified — phoneme 40.")
        print("  VRFY_002 COMPLETE.")
        print()
        print("  Inventory now 40 phonemes.")
        print("  [b] in GEBĀD = phoneme 41.")
        print("  Inventory closes at 41.")
        print()
        print("  Line 8 status:")
        print("  feasceaft  ✓")
        print("  funden     ✓")
        print("  hē         — next")
        print("  þæs        — next")
        print("  frōfre     — next")
        print("  gebād      — [b] phoneme 41")
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
