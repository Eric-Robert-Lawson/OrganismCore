"""
HĒ DIAGNOSTIC v1
Old English: hē [heː]
Beowulf line 8, word 3 (overall word 33)
No new phonemes — pure assembly
February 2026

DIAGNOSTICS:
  D1   H fricative [h]
       voicing must be low — voiceless
       onset shaped by following [eː]
  D2   EY long vowel [eː]
       voicing >= 0.50
       duration >= 90 ms (long vowel)
       F2 centroid 1600–2300 Hz
  D3   Long vs short distinction
       [eː] duration vs [e] reference
       must be >= 90 ms
  D4   Full word
       RMS, duration
  D5   Perceptual

KEY CHECKS:
  [h] voicing <= 0.35 — voiceless onset
  [eː] voicing ~0.84 — long vowel inflates
  [eː] duration >= 90 ms — confirms length
  [eː] F2 ~1875 Hz — front vowel confirmed
  Word duration ~170 ms at dil=1.0
  (60 ms [h] + 110 ms [eː])
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
    n_frames = max(1, (n_in - win_n) // hop_in + 1)
    n_out   = hop_out * n_frames + win_n
    out     = np.zeros(n_out, dtype=DTYPE)
    norm    = np.zeros(n_out, dtype=DTYPE)
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
    print("HĒ DIAGNOSTIC v1")
    print("Old English [heː]")
    print("Beowulf line 8, word 3")
    print("Pure assembly — no new phonemes")
    print("=" * 60)
    print()

    try:
        from he_reconstruction import (
            synth_he,
            synth_H,
            synth_EY,
            apply_simple_room,
            EY_F,
            PITCH_PERF, DIL_PERF)
        print("  he_reconstruction.py: OK")
    except ImportError as e:
        print(f"  IMPORT FAILED: {e}")
        return False
    print()

    all_pass = True

    # ── D1 H ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 1 — H FRICATIVE [h]")
    print("  Voiceless glottal.")
    print("  Shaped by following [eː].")
    print("  No place of its own.")
    print("  C([h],H) ≈ 0.90 — near H.")
    print()
    h_seg = synth_H(F_next=EY_F,
                     dil=1.0, sr=SR)
    v_h   = measure_voicing(h_seg)
    r_h   = rms(h_seg)
    dur_h = len(h_seg) / SR * 1000.0
    print(f"  Duration: {dur_h:.0f} ms")
    print()
    p1 = check('voicing (must be low)',
               v_h, 0.0, 0.35)
    p2 = check('RMS level', r_h,
               0.001, 0.50)
    d1 = p1 and p2
    all_pass &= d1
    print(f"  {'PASSED' if d1 else 'FAILED'}")
    print()

    # ── D2 EY ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 2 — EY LONG VOWEL [eː]")
    print("  Long close-mid front unrounded.")
    print("  Duration >= 90 ms.")
    print("  F2 ~1875 Hz.")
    print()
    ey_seg  = synth_EY(
        F_prev=None, F_next=None,
        pitch_hz=145.0, dil=1.0, sr=SR)
    v_ey    = measure_voicing(ey_seg)
    f2_ey   = measure_band_centroid(
        ey_seg, 1400.0, 2400.0)
    dur_ey  = len(ey_seg) / SR * 1000.0
    print(f"  Duration:    {dur_ey:.0f} ms"
          f"  (target >= 90 ms)")
    print(f"  F2 centroid: {f2_ey:.0f} Hz"
          f"  (target 1600–2300 Hz)")
    print()
    p1 = check('voicing',
               v_ey, 0.50, 1.0)
    p2 = check(
        f'duration ({dur_ey:.0f} ms)',
        dur_ey, 90.0, 160.0,
        unit=' ms', fmt='.1f')
    p3 = check(
        f'F2 centroid ({f2_ey:.0f} Hz)',
        f2_ey, 1600.0, 2300.0,
        unit=' Hz', fmt='.1f')
    d2 = p1 and p2 and p3
    all_pass &= d2
    print(f"  {'PASSED' if d2 else 'FAILED'}")
    print()

    # ── D3 LONG vs SHORT ──────────────────
    print("─" * 60)
    print("DIAGNOSTIC 3 — LONG VOWEL"
          " DISTINCTION")
    print("  [eː] must be >= 90 ms.")
    print("  Distinguishes from short [e]"
          " (55 ms).")
    print()
    e_short_ref = 55.0
    diff_ms = dur_ey - e_short_ref
    print(f"  [e]  reference: {e_short_ref:.0f} ms"
          f"  (short)")
    print(f"  [eː] measured:  {dur_ey:.0f} ms"
          f"  (long)")
    print(f"  Difference:     {diff_ms:.0f} ms")
    print()
    p1 = check(
        f'[eː] >= 90 ms ({dur_ey:.0f} ms)',
        dur_ey, 90.0, 160.0,
        unit=' ms', fmt='.1f')
    p2 = check(
        f'long/short diff ({diff_ms:.0f} ms)',
        diff_ms, 40.0, 120.0,
        unit=' ms', fmt='.1f')
    d3 = p1 and p2
    all_pass &= d3
    print(f"  {'PASSED' if d3 else 'FAILED'}")
    print()

    # ── D4 FULL WORD ──────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 4 — FULL WORD [heː]")
    print()
    w_dry  = synth_he(145.0, 1.0, False)
    w_hall = synth_he(145.0, 1.0, True)
    w_perf = synth_he(PITCH_PERF,
                       DIL_PERF, True)
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
        dur_ms, 140.0, 220.0,
        unit=' ms', fmt='.1f')
    d4 = p1 and p2
    all_pass &= d4
    write_wav("output_play/diag_he_full.wav",
               w_dry)
    write_wav("output_play/diag_he_hall.wav",
               w_hall)
    write_wav("output_play/diag_he_slow.wav",
               ola_stretch(w_dry, 4.0))
    write_wav("output_play/diag_he_perf.wav",
               w_perf)
    print(f"  {'PASSED' if d4 else 'FAILED'}")
    print()

    # ── D5 PERCEPTUAL ─────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 5 — PERCEPTUAL")
    print()
    print("  Diagnostic versions:")
    for fn in [
        "diag_he_full.wav",
        "diag_he_slow.wav",
        "diag_he_hall.wav",
    ]:
        print(f"  afplay output_play/{fn}")
    print()
    print("  Performance version:")
    print("  afplay output_play/diag_he_perf.wav")
    print()
    print("  LISTEN FOR:")
    print("  H   — voiceless aspiration onset")
    print("        no place of its own")
    print("        shaped by the [eː] that follows")
    print("        brief — 60 ms")
    print("  EY  — long front vowel")
    print("        clearly LONGER than short [e]")
    print("        front position — high F2")
    print("        sustained — 110 ms")
    print("  Word-final ghost:")
    print("        brief return toward H")
    print("        the breath before ÞÆS")
    print()
    print("  CONTEXT:")
    print("  feasceaft funden, HĒ þæs frōfre gebād")
    print("  The pronoun. The turn.")
    print("  The scop centres a person.")
    print()

    # ── SUMMARY ───────────────────────────
    print("=" * 60)
    print("SUMMARY")
    print()
    rows = [
        ("D1   H fricative",          d1),
        ("D2   EY long vowel",         d2),
        ("D3   Long/short distinction", d3),
        ("D4   Full word",             d4),
    ]
    for lbl, ok_ in rows:
        sym = "✓ PASS" if ok_ else "✗ FAIL"
        print(f"  {lbl:30s}  {sym}")
    print(f"  {'D5   Perceptual':30s}  LISTEN")
    print()
    if all_pass:
        print("  ALL NUMERIC CHECKS PASSED")
        print()
        print("  HĒ [heː] verified.")
        print("  Pure assembly — both phonemes")
        print("  from verified inventory.")
        print()
        print("  Line 8 status:")
        print("  feasceaft  ✓")
        print("  funden     ✓")
        print("  hē         ✓")
        print("  þæs        — next")
        print("  frōfre     —")
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
