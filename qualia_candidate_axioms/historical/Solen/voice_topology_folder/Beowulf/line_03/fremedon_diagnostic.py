"""
FREMEDON DIAGNOSTIC v1
Old English: fremedon [fremedon]
Beowulf line 3, word 5 — final word
February 2026

DIAGNOSTICS:
  D1   F fricative [f]
  D2   R trill [r]
  D3   E1 vowel [e]
  D4   M nasal [m]
  D5   E2 vowel [e]
  D6   D stop [d]
  D7   O vowel [o]
  D8   N nasal [n]
  D9   Full word
  D10  Perceptual

FRAMEWORK PROOF:
  Zero new phonemes.
  All eight from verified inventory.
  If D9 passes: the synthesis engine
  can produce any arbitrary OE word
  from the existing 28-item inventory.
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
    print("FREMEDON DIAGNOSTIC v1")
    print("Old English [fremedon]")
    print("Beowulf line 3, word 5")
    print("=" * 60)
    print()

    try:
        from fremedon_reconstruction import (
            synth_fremedon,
            synth_F, synth_R,
            synth_E_short, synth_M,
            synth_D, synth_O_short,
            synth_N_final,
            apply_simple_room,
            R_F, E_F, M_F,
            O_F, N_F)
        print("  fremedon_reconstruction.py: OK")
    except ImportError as e:
        print(f"  IMPORT FAILED: {e}")
        return False
    print()

    all_pass = True

    # ── D1 F ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 1 — F FRICATIVE [f]")
    print()
    f_seg   = synth_F(R_F, 1.0, SR)
    cent_f  = measure_band_centroid(
        f_seg, 400.0, 8000.0)
    p1 = check('voicing (must be low)',
               measure_voicing(f_seg),
               0.0, 0.35)
    p2 = check('RMS level', rms(f_seg),
               0.005, 0.80)
    p3 = check(
        f'centroid ({cent_f:.0f} Hz)',
        cent_f, 4500.0, 8000.0,
        unit=' Hz', fmt='.1f')
    d1 = p1 and p2 and p3
    all_pass &= d1
    print(f"  {'PASSED' if d1 else 'FAILED'}")
    print()

    # ── D2 R ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 2 — R TRILL [r]")
    print()
    print("  Post-fricative position [fr].")
    print("  Voicing onset from [f].")
    print()
    r_seg  = synth_R(R_F, E_F, 145.0,
                      1.0, SR)
    n_r    = len(r_seg)
    body_r = r_seg[int(0.25*n_r):
                   int(0.75*n_r)]
    p1 = check('voicing',
               measure_voicing(body_r),
               0.40, 1.0)
    p2 = check('RMS level', rms(r_seg),
               0.005, 0.80)
    d2 = p1 and p2
    all_pass &= d2
    print(f"  {'PASSED' if d2 else 'FAILED'}")
    print()

    # ── D3 E1 ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 3 — E1 VOWEL [e]")
    print()
    e1_seg = synth_E_short(R_F, M_F,
                            145.0, 1.0)
    n_e1   = len(e1_seg)
    body   = e1_seg[int(0.12*n_e1):
                    n_e1-int(0.12*n_e1)]
    p1 = check('voicing',
               measure_voicing(body),
               0.50, 1.0)
    p2 = check(
        f'F2 centroid ({measure_band_centroid(body, 1600.0, 2600.0):.0f} Hz)',
        measure_band_centroid(
            body, 1600.0, 2600.0),
        1800.0, 2400.0,
        unit=' Hz', fmt='.1f')
    d3 = p1 and p2
    all_pass &= d3
    print(f"  {'PASSED' if d3 else 'FAILED'}")
    print()

    # ── D4 M ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 4 — M NASAL [m]")
    print()
    m_seg = synth_M(E_F, E_F, 145.0, 1.0)
    p1 = check('voicing',
               measure_voicing(m_seg),
               0.65, 1.0)
    p2 = check('RMS (nasal murmur)',
               rms(m_seg), 0.005, 0.25)
    d4 = p1 and p2
    all_pass &= d4
    print(f"  {'PASSED' if d4 else 'FAILED'}")
    print()

    # ── D5 E2 ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 5 — E2 VOWEL [e]")
    print()
    e2_seg = synth_E_short(M_F, O_F,
                            145.0, 1.0)
    n_e2   = len(e2_seg)
    body   = e2_seg[int(0.12*n_e2):
                    n_e2-int(0.12*n_e2)]
    p1 = check('voicing',
               measure_voicing(body),
               0.50, 1.0)
    p2 = check(
        f'F2 centroid ({measure_band_centroid(body, 1600.0, 2600.0):.0f} Hz)',
        measure_band_centroid(
            body, 1600.0, 2600.0),
        1800.0, 2400.0,
        unit=' Hz', fmt='.1f')
    d5 = p1 and p2
    all_pass &= d5
    print(f"  {'PASSED' if d5 else 'FAILED'}")
    print()

    # ── D6 D ────────────────────��─────────
    print("─" * 60)
    print("DIAGNOSTIC 6 — D STOP [d]")
    print()
    d_seg = synth_D(E_F, O_F, 145.0, 1.0)
    p1 = check('RMS level', rms(d_seg),
               0.010, 0.90)
    dur_d = len(d_seg) / SR * 1000.0
    p2 = check(
        f'duration ({dur_d:.0f} ms)',
        dur_d, 50.0, 120.0,
        unit=' ms', fmt='.1f')
    d6 = p1 and p2
    all_pass &= d6
    print(f"  {'PASSED' if d6 else 'FAILED'}")
    print()

    # ── D7 O ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 7 — O VOWEL [o]")
    print()
    o_seg = synth_O_short(O_F, N_F,
                           145.0, 1.0)
    n_o   = len(o_seg)
    body  = o_seg[int(0.12*n_o):
                  n_o-int(0.12*n_o)]
    p1 = check('voicing',
               measure_voicing(body),
               0.50, 1.0)
    p2 = check(
        f'F2 centroid ({measure_band_centroid(body, 500.0, 1000.0):.0f} Hz)',
        measure_band_centroid(
            body, 500.0, 1000.0),
        550.0, 850.0,
        unit=' Hz', fmt='.1f')
    d7 = p1 and p2
    all_pass &= d7
    print(f"  {'PASSED' if d7 else 'FAILED'}")
    print()

    # ── D8 N ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 8 — N NASAL [n]")
    print()
    n_seg = synth_N_final(O_F, 145.0, 1.0)
    p1 = check('voicing',
               measure_voicing(n_seg),
               0.60, 1.0)
    p2 = check('RMS (nasal murmur)',
               rms(n_seg), 0.005, 0.25)
    d8 = p1 and p2
    all_pass &= d8
    print(f"  {'PASSED' if d8 else 'FAILED'}")
    print()

    # ── D9 FULL WORD ──────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 9 — FULL WORD")
    print()
    print("  Framework proof.")
    print("  Zero new phonemes.")
    print("  Pure assembly from inventory.")
    print()
    w_dry  = synth_fremedon(
        145.0, 1.0, False)
    w_hall = synth_fremedon(
        145.0, 1.0, True)
    dur_ms = len(w_dry) / SR * 1000.0
    p1 = check('RMS level', rms(w_dry),
               0.010, 0.90)
    p2 = check(
        f'duration ({dur_ms:.0f} ms)',
        dur_ms, 350.0, 700.0,
        unit=' ms', fmt='.1f')
    print(f"  {len(w_dry)} samples"
          f" ({dur_ms:.0f} ms)")
    write_wav(
        "output_play/diag_frem_full.wav",
        w_dry)
    write_wav(
        "output_play/diag_frem_hall.wav",
        w_hall)
    write_wav(
        "output_play/diag_frem_slow.wav",
        ola_stretch(w_dry, 4.0))
    d9 = p1 and p2
    all_pass &= d9
    print(f"  {'PASSED' if d9 else 'FAILED'}")
    print()

    # ── D10 PERCEPTUAL ────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 10 — PERCEPTUAL")
    print()
    for fn in [
        "diag_frem_slow.wav",
        "diag_frem_hall.wav",
    ]:
        print(f"  afplay output_play/{fn}")
    print()
    print("  LISTEN FOR:")
    print("  FR: fricative into trill")
    print("    two distinct events at onset")
    print("  Full: F·R·E·M·E·D·O·N")
    print("  Eight events")
    print("  The syntax resolves here —")
    print("  this verb closes the clause")
    print("  that opened with HU")
    print()

    # ── SUMMARY ───────────────────────────
    print("=" * 60)
    print("SUMMARY")
    print()
    rows = [
        ("D1  F fricative",  d1),
        ("D2  R trill",      d2),
        ("D3  E1 vowel",     d3),
        ("D4  M nasal",      d4),
        ("D5  E2 vowel",     d5),
        ("D6  D stop",       d6),
        ("D7  O vowel",      d7),
        ("D8  N nasal",      d8),
        ("D9  Full word",    d9),
    ]
    for lbl, ok_ in rows:
        sym = "✓ PASS" if ok_ else "✗ FAIL"
        print(f"  {lbl:22s}  {sym}")
    print(f"  {'D10 Perceptual':22s}  LISTEN")
    print()
    if all_pass:
        print("  ALL NUMERIC CHECKS PASSED")
        print()
        print("  FREMEDON [fremedon] verified.")
        print("  Framework proof: PASSED.")
        print()
        print("  LINE 3 COMPLETE:")
        print("  hu ðā æþelingas"
              " ellen fremedon")
        print()
        print("  THREE LINES OF BEOWULF")
        print("  RECONSTRUCTED.")
        print()
        print("  Inventory: 28 phonemes.")
        print("  Proceed to line 4")
        print("  to complete inventory.")
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
