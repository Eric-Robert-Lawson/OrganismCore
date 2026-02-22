"""
MONGUM DIAGNOSTIC v1
Old English: mongum [moŋɡum]
Beowulf line 6, word 1
February 2026

DIAGNOSTICS:
  D1  M nasal initial [m]
  D2  O vowel [o]
  D3  NG nasal [ŋ]
  D4  G stop medial [ɡ]
  D5  U vowel [u]
  D6  M nasal final [m]
  D7  Full word
  D8  Perceptual

Zero new phonemes — pure assembly.
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
    print("MONGUM DIAGNOSTIC v1")
    print("Old English [moŋɡum]")
    print("Beowulf line 6, word 1")
    print("=" * 60)
    print()

    try:
        from mongum_reconstruction import (
            synth_mongum,
            synth_M, synth_O,
            synth_NG, synth_G_medial,
            synth_U,
            apply_simple_room,
            M_F, O_F, NG_F, U_F)
        print("  mongum_reconstruction.py: OK")
    except ImportError as e:
        print(f"  IMPORT FAILED: {e}")
        return False
    print()

    all_pass = True

    # ── D1 M INITIAL ──────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 1 — M NASAL initial [m]")
    print()
    m1_seg = synth_M(None, O_F,
                      145.0, 1.0, SR)
    p1 = check('voicing',
               measure_voicing(m1_seg),
               0.65, 1.0)
    p2 = check('RMS (nasal murmur)',
               rms(m1_seg), 0.005, 0.25)
    d1 = p1 and p2
    all_pass &= d1
    print(f"  {'PASSED' if d1 else 'FAILED'}")
    print()

    # ── D2 O ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 2 — O VOWEL [o]")
    print()
    o_seg  = synth_O(M_F, NG_F,
                      145.0, 1.0, SR)
    n_o    = len(o_seg)
    body_o = o_seg[int(0.12*n_o):
                   n_o-int(0.12*n_o)]
    p1 = check('voicing',
               measure_voicing(body_o),
               0.50, 1.0)
    cent_o = measure_band_centroid(
        body_o, 550.0, 1100.0)
    p2 = check(
        f'F2 centroid ({cent_o:.0f} Hz)',
        cent_o, 600.0, 1000.0,
        unit=' Hz', fmt='.1f')
    d2 = p1 and p2
    all_pass &= d2
    print(f"  {'PASSED' if d2 else 'FAILED'}")
    print()

    # ── D3 NG ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 3 — NG NASAL [ŋ]")
    print()
    ng_seg = synth_NG(O_F, None,
                       145.0, 1.0, SR)
    p1 = check('voicing',
               measure_voicing(ng_seg),
               0.65, 1.0)
    p2 = check('RMS (nasal murmur)',
               rms(ng_seg), 0.005, 0.25)
    d3 = p1 and p2
    all_pass &= d3
    print(f"  {'PASSED' if d3 else 'FAILED'}")
    print()

    # ── D4 G MEDIAL ───────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 4 — G STOP medial [ɡ]")
    print()
    g_seg = synth_G_medial(NG_F, U_F,
                            145.0, 1.0, SR)
    p1 = check('RMS level', rms(g_seg),
               0.005, 0.70)
    dur_g = len(g_seg) / SR * 1000.0
    p2 = check(
        f'duration ({dur_g:.0f} ms)',
        dur_g, 40.0, 100.0,
        unit=' ms', fmt='.1f')
    d4 = p1 and p2
    all_pass &= d4
    print(f"  {'PASSED' if d4 else 'FAILED'}")
    print()

    # ── D5 U ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 5 — U VOWEL [u]")
    print()
    u_seg  = synth_U(U_F, M_F,
                      145.0, 1.0, SR)
    n_u    = len(u_seg)
    body_u = u_seg[int(0.12*n_u):
                   n_u-int(0.12*n_u)]
    p1 = check('voicing',
               measure_voicing(body_u),
               0.50, 1.0)
    cent_u = measure_band_centroid(
        body_u, 500.0, 1200.0)
    p2 = check(
        f'F2 centroid ({cent_u:.0f} Hz)',
        cent_u, 550.0, 1100.0,
        unit=' Hz', fmt='.1f')
    d5 = p1 and p2
    all_pass &= d5
    print(f"  {'PASSED' if d5 else 'FAILED'}")
    print()

    # ── D6 M FINAL ────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 6 — M NASAL final [m]")
    print()
    m2_seg = synth_M(U_F, None,
                      145.0, 1.0, SR)
    p1 = check('voicing',
               measure_voicing(m2_seg),
               0.65, 1.0)
    p2 = check('RMS (nasal murmur)',
               rms(m2_seg), 0.005, 0.25)
    d6 = p1 and p2
    all_pass &= d6
    print(f"  {'PASSED' if d6 else 'FAILED'}")
    print()

    # ── D7 FULL WORD ──────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 7 — FULL WORD [moŋɡum]")
    print()
    w_dry  = synth_mongum(145.0, 1.0, False)
    w_hall = synth_mongum(145.0, 1.0, True)
    dur_ms = len(w_dry) / SR * 1000.0
    p1 = check('RMS level', rms(w_dry),
               0.010, 0.90)
    p2 = check(
        f'duration ({dur_ms:.0f} ms)',
        dur_ms, 330.0, 560.0,
        unit=' ms', fmt='.1f')
    print(f"  {len(w_dry)} samples"
          f" ({dur_ms:.0f} ms)")
    write_wav(
        "output_play/diag_mongum_full.wav",
        w_dry)
    write_wav(
        "output_play/diag_mongum_hall.wav",
        w_hall)
    write_wav(
        "output_play/diag_mongum_slow.wav",
        ola_stretch(w_dry, 4.0))
    d7 = p1 and p2
    all_pass &= d7
    print(f"  {'PASSED' if d7 else 'FAILED'}")
    print()

    # ── D8 PERCEPTUAL ─────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 8 — PERCEPTUAL")
    print()
    for fn in [
        "diag_mongum_slow.wav",
        "diag_mongum_hall.wav",
    ]:
        print(f"  afplay output_play/{fn}")
    print()
    print("  LISTEN FOR:")
    print("  M onset — nasal hum")
    print("  O — back rounded vowel")
    print("  NG+G — velar nasal then")
    print("    velar stop — both sound")
    print("    not bare English 'ng'")
    print("  UM — back vowel + nasal close")
    print("  Full: M·O·NG·G·U·M")
    print("  Rhymes with 'long-goom'")
    print("  approximately.")
    print()

    # ── SUMMARY ───────────────────────────
    print("=" * 60)
    print("SUMMARY")
    print()
    rows = [
        ("D1  M nasal initial",  d1),
        ("D2  O vowel",          d2),
        ("D3  NG nasal",         d3),
        ("D4  G stop medial",    d4),
        ("D5  U vowel",          d5),
        ("D6  M nasal final",    d6),
        ("D7  Full word",        d7),
    ]
    for lbl, ok_ in rows:
        sym = "✓ PASS" if ok_ else "✗ FAIL"
        print(f"  {lbl:22s}  {sym}")
    print(f"  {'D8 Perceptual':22s}  LISTEN")
    print()
    if all_pass:
        print("  ALL NUMERIC CHECKS PASSED")
        print()
        print("  MONGUM [moŋɡum] verified.")
        print("  Zero new phonemes.")
        print("  32 phonemes verified.")
        print()
        print("  Next: MǢGÞUM [mæːɣθum]")
        print("  Beowulf line 6, word 2.")
        print("  NEW PHONEMES: [æː] [ɣ]")
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
