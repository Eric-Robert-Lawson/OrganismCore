"""
ÞÆET DIAGNOSTIC v1
Old English: þæt [θæt]
Beowulf line 4, word 1
February 2026

DIAGNOSTICS:
  D1  Þ fricative [θ]
  D2  Æ vowel [æ]
  D3  T stop word-final [t]
  D4  Full word
  D5  Perceptual

NOTE on word-final [t]:
  No aspiration in OE word-final stops.
  Voicing check on closure must be low.
  Burst brief and sharp.
  Compare to word-initial [t] in HWÆT —
  here the stop closes the word rather
  than opening it. Same burst parameters,
  no VOT ramp after burst.
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
    print("ÞÆET DIAGNOSTIC v1")
    print("Old English [θæt]")
    print("Beowulf line 4, word 1")
    print("=" * 60)
    print()

    try:
        from thaet_reconstruction import (
            synth_thaet,
            synth_TH, synth_AE,
            synth_T_final,
            apply_simple_room,
            AE_F)
        print("  thaet_reconstruction.py: OK")
    except ImportError as e:
        print(f"  IMPORT FAILED: {e}")
        return False
    print()

    all_pass = True

    # ── D1 TH ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 1 — Þ FRICATIVE [θ]")
    print()
    th_seg  = synth_TH(AE_F, 1.0, SR)
    cent_th = measure_band_centroid(
        th_seg, 400.0, 8000.0)
    p1 = check('voicing (must be low)',
               measure_voicing(th_seg),
               0.0, 0.35)
    p2 = check(
        f'centroid ({cent_th:.0f} Hz)',
        cent_th, 3500.0, 6000.0,
        unit=' Hz', fmt='.1f')
    d1 = p1 and p2
    all_pass &= d1
    print(f"  {'PASSED' if d1 else 'FAILED'}")
    print()

    # ── D2 AE ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 2 — Æ VOWEL [æ]")
    print()
    ae_seg = synth_AE(AE_F, None,
                       145.0, 1.0)
    n_ae   = len(ae_seg)
    body   = ae_seg[int(0.12*n_ae):
                    n_ae-int(0.12*n_ae)]
    p1 = check('voicing',
               measure_voicing(body),
               0.50, 1.0)
    p2 = check(
        f'F1 centroid ({measure_band_centroid(body, 500.0, 900.0):.0f} Hz)',
        measure_band_centroid(
            body, 500.0, 900.0),
        550.0, 800.0,
        unit=' Hz', fmt='.1f')
    d2 = p1 and p2
    all_pass &= d2
    print(f"  {'PASSED' if d2 else 'FAILED'}")
    print()

    # ── D3 T ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 3 — T STOP [t] word-final")
    print()
    print("  Voiceless alveolar stop.")
    print("  Word-final — no aspiration.")
    print("  Closure + brief burst only.")
    print()
    t_seg = synth_T_final(AE_F, 1.0, SR)
    p1 = check('voicing (must be low)',
               measure_voicing(t_seg),
               0.0, 0.35)
    p2 = check('RMS level', rms(t_seg),
               0.005, 0.70)
    dur_t = len(t_seg) / SR * 1000.0
    p3 = check(
        f'duration ({dur_t:.0f} ms)',
        dur_t, 40.0, 100.0,
        unit=' ms', fmt='.1f')
    d3 = p1 and p2 and p3
    all_pass &= d3
    print(f"  {'PASSED' if d3 else 'FAILED'}")
    print()

    # ── D4 FULL WORD ──────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 4 — FULL WORD [θæt]")
    print()
    w_dry  = synth_thaet(145.0, 1.0, False)
    w_hall = synth_thaet(145.0, 1.0, True)
    dur_ms = len(w_dry) / SR * 1000.0
    p1 = check('RMS level', rms(w_dry),
               0.010, 0.90)
    p2 = check(
        f'duration ({dur_ms:.0f} ms)',
        dur_ms, 150.0, 350.0,
        unit=' ms', fmt='.1f')
    print(f"  {len(w_dry)} samples"
          f" ({dur_ms:.0f} ms)")
    write_wav(
        "output_play/diag_thaet_full.wav",
        w_dry)
    write_wav(
        "output_play/diag_thaet_hall.wav",
        w_hall)
    write_wav(
        "output_play/diag_thaet_slow.wav",
        ola_stretch(w_dry, 4.0))
    d4 = p1 and p2
    all_pass &= d4
    print(f"  {'PASSED' if d4 else 'FAILED'}")
    print()

    # ── D5 PERCEPTUAL ─────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 5 — PERCEPTUAL")
    print()
    for fn in [
        "diag_thaet_slow.wav",
        "diag_thaet_hall.wav",
    ]:
        print(f"  afplay output_play/{fn}")
    print()
    print("  LISTEN FOR:")
    print("  Þ: dental hiss at onset")
    print("  Æ: open front vowel — 'ah'")
    print("    with front quality")
    print("  T: clean stop closure — no")
    print("    aspiration after burst")
    print("  Full: Þ·Æ·T — three events")
    print("  Sounds like Modern English")
    print("  'that' — because it is.")
    print()

    # ── SUMMARY ───────────────────────────
    print("=" * 60)
    print("SUMMARY")
    print()
    rows = [
        ("D1  Þ fricative",    d1),
        ("D2  Æ vowel",        d2),
        ("D3  T stop final",   d3),
        ("D4  Full word",      d4),
    ]
    for lbl, ok_ in rows:
        sym = "✓ PASS" if ok_ else "✗ FAIL"
        print(f"  {lbl:22s}  {sym}")
    print(f"  {'D5 Perceptual':22s}  LISTEN")
    print()
    if all_pass:
        print("  ALL NUMERIC CHECKS PASSED")
        print()
        print("  ÞÆET [θæt] verified.")
        print("  Next: WÆS [wæs]")
        print("  Beowulf line 4, word 2.")
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
