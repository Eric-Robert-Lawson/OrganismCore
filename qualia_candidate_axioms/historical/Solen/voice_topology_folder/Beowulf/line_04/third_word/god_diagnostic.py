"""
GŌD DIAGNOSTIC v1
Old English: gōd [ɡoːd]
Beowulf line 4, word 3
February 2026

DIAGNOSTICS:
  D1  G stop [ɡ]
  D2  Ō long vowel [oː]      NEW
  D3  D stop [d]
  D4  Long/short ratio [oː]/[o]
  D5  Full word
  D6  Perceptual

KEY CHECK:
  D4 duration ratio.
  [oː] must be >= 1.7× short [o]
  duration target (65 ms).
  Same ratio test as geminate —
  duration is the phonemic cue.
  Target: [oː] >= 110 ms.
  Set at 150 ms — ratio 2.31×.
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
    print("GŌD DIAGNOSTIC v1")
    print("Old English [ɡoːd]")
    print("Beowulf line 4, word 3")
    print("=" * 60)
    print()

    try:
        from god_reconstruction import (
            synth_god,
            synth_G, synth_OO, synth_D,
            apply_simple_room,
            OO_F, OO_DUR_MS)
        print("  god_reconstruction.py: OK")
    except ImportError as e:
        print(f"  IMPORT FAILED: {e}")
        return False
    print()

    all_pass = True

    # ── D1 G ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 1 — G STOP [ɡ]")
    print()
    g_seg = synth_G(None, OO_F, 145.0,
                     1.0, SR)
    p1 = check('RMS level', rms(g_seg),
               0.010, 0.90)
    dur_g = len(g_seg) / SR * 1000.0
    p2 = check(
        f'duration ({dur_g:.0f} ms)',
        dur_g, 50.0, 120.0,
        unit=' ms', fmt='.1f')
    d1 = p1 and p2
    all_pass &= d1
    print(f"  {'PASSED' if d1 else 'FAILED'}")
    print()

    # ── D2 OO ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 2 — Ō LONG VOWEL [oː]")
    print()
    print("  Long close-mid back rounded.")
    print("  Same formants as short [o].")
    print("  Duration 150 ms — long vowel.")
    print("  Pure monophthong — no offglide.")
    print()
    oo_seg  = synth_OO(OO_F, OO_F,
                        145.0, 1.0, SR)
    n_oo    = len(oo_seg)
    body    = oo_seg[int(0.15*n_oo):
                     int(0.85*n_oo)]
    dur_oo  = n_oo / SR * 1000.0
    cent_f2 = measure_band_centroid(
        body, 500.0, 1000.0)
    p1 = check('voicing',
               measure_voicing(body),
               0.60, 1.0)
    p2 = check(
        f'duration ({dur_oo:.0f} ms)',
        dur_oo, 120.0, 200.0,
        unit=' ms', fmt='.1f')
    p3 = check(
        f'F2 centroid ({cent_f2:.0f} Hz)',
        cent_f2, 550.0, 850.0,
        unit=' Hz', fmt='.1f')
    d2 = p1 and p2 and p3
    all_pass &= d2
    write_wav(
        "output_play/diag_god_oo.wav",
        ola_stretch(oo_seg / (
            np.max(np.abs(oo_seg))+1e-8)
            * 0.75, 4.0))
    print(f"  {'PASSED' if d2 else 'FAILED'}")
    print()

    # ── D3 D ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 3 — D STOP [d]")
    print()
    d_seg = synth_D(OO_F, None, 145.0,
                     1.0, SR)
    p1 = check('RMS level', rms(d_seg),
               0.010, 0.90)
    dur_d = len(d_seg) / SR * 1000.0
    p2 = check(
        f'duration ({dur_d:.0f} ms)',
        dur_d, 50.0, 120.0,
        unit=' ms', fmt='.1f')
    d3 = p1 and p2
    all_pass &= d3
    print(f"  {'PASSED' if d3 else 'FAILED'}")
    print()

    # ── D4 LONG/SHORT RATIO ───────────────
    print("─" * 60)
    print("DIAGNOSTIC 4 — LONG/SHORT RATIO")
    print()
    print("  Duration must be >= 1.7×")
    print("  short [o] target (65 ms).")
    print("  Duration is the phonemic")
    print("  cue for vowel length in OE.")
    print()
    short_o_ms = 65.0
    dur_oo2    = len(oo_seg) / SR * 1000.0
    ratio      = dur_oo2 / short_o_ms
    print(f"  [o]  short target: {short_o_ms:.1f} ms")
    print(f"  [oː] measured:     {dur_oo2:.1f} ms")
    p1 = check(
        f'length ratio ({ratio:.2f}×)',
        ratio, 1.7, 3.0,
        unit='×', fmt='.2f')
    d4 = p1
    all_pass &= d4
    print(f"  {'PASSED' if d4 else 'FAILED'}")
    print()

    # ── D5 FULL WORD ──────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 5 — FULL WORD [ɡoːd]")
    print()
    w_dry  = synth_god(145.0, 1.0, False)
    w_hall = synth_god(145.0, 1.0, True)
    dur_ms = len(w_dry) / SR * 1000.0
    p1 = check('RMS level', rms(w_dry),
               0.010, 0.90)
    p2 = check(
        f'duration ({dur_ms:.0f} ms)',
        dur_ms, 200.0, 450.0,
        unit=' ms', fmt='.1f')
    print(f"  {len(w_dry)} samples"
          f" ({dur_ms:.0f} ms)")
    write_wav(
        "output_play/diag_god_full.wav",
        w_dry)
    write_wav(
        "output_play/diag_god_hall.wav",
        w_hall)
    write_wav(
        "output_play/diag_god_slow.wav",
        ola_stretch(w_dry, 4.0))
    d5 = p1 and p2
    all_pass &= d5
    print(f"  {'PASSED' if d5 else 'FAILED'}")
    print()

    # ── D6 PERCEPTUAL ─────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 6 — PERCEPTUAL")
    print()
    for fn in [
        "diag_god_oo.wav",
        "diag_god_slow.wav",
        "diag_god_hall.wav",
    ]:
        print(f"  afplay output_play/{fn}")
    print()
    print("  LISTEN FOR:")
    print("  Ō: long back rounded vowel")
    print("    pure — no diphthong")
    print("    held — clearly longer than")
    print("    any previous short vowel")
    print("  Full: G·Ō·D — three events")
    print("  The Ō dominates duration")
    print("  Recognisable as 'good' —")
    print("  the ancestor of that word.")
    print()

    # ── SUMMARY ───────────────────────────
    print("=" * 60)
    print("SUMMARY")
    print()
    rows = [
        ("D1  G stop",          d1),
        ("D2  Ō long vowel",    d2),
        ("D3  D stop",          d3),
        ("D4  Long/short ratio",d4),
        ("D5  Full word",       d5),
    ]
    for lbl, ok_ in rows:
        sym = "✓ PASS" if ok_ else "✗ FAIL"
        print(f"  {lbl:22s}  {sym}")
    print(f"  {'D6 Perceptual':22s}  LISTEN")
    print()
    if all_pass:
        print("  ALL NUMERIC CHECKS PASSED")
        print()
        print("  GŌD [ɡoːd] verified.")
        print("  [oː] added to inventory.")
        print("  Next: CYNING [kyniŋɡ]")
        print("  Beowulf line 4, word 4.")
        print("  Zero new phonemes.")
        print("  Line 4 final word.")
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
