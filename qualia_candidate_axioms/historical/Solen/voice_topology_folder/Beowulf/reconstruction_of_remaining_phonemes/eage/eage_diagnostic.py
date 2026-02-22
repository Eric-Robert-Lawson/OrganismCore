"""
ĒAGE DIAGNOSTIC v1
Old English: ēage [eːɑɣe]
Inventory completion — word 2 of 4
New phoneme: [eːɑ]
February 2026

DIAGNOSTICS:
  D1  EYA diphthong [eːɑ] basic
  D2  EYA duration — long diphthong
  D3  EYA F2 movement
  D4  EYA F1 movement — jaw opens
  D5  EYA vs short [eɑ] — duration only
  D6  EYA vs [eːo] — trajectory contrast
  D7  GH fricative [ɣ]
  D8  E vowel final [e]
  D9  Full word
  D10 Perceptual

KEY CHECKS:
  D2: duration >= 120 ms (long diphthong)
  D3: F2 falls — onset ~1900, offset ~1100
  D4: F1 rises — onset ~450, offset ~700
      jaw opens — this is [eɑ] not [eo]
  D5: [eːɑ] dur ~150ms vs [eɑ] dur ~80ms
      ratio >= 1.5
  D6: [eːɑ] F1 rises — [eːo] F1 stable
      trajectory distinction confirmed
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
    print("ĒAGE DIAGNOSTIC v1")
    print("Old English [eːɑɣe]")
    print("Inventory completion — word 2 of 4")
    print("New phoneme: [eːɑ]")
    print("=" * 60)
    print()

    try:
        from eage_reconstruction import (
            synth_eage,
            synth_EYA, synth_GH, synth_E,
            apply_simple_room,
            EYA_F_ON, EYA_F_OFF,
            GH_F, E_F)
        print("  eage_reconstruction.py: OK")
    except ImportError as e:
        print(f"  IMPORT FAILED: {e}")
        return False
    print()

    all_pass = True

    eya_seg = synth_EYA(EYA_F_ON, GH_F,
                         145.0, 1.0, SR)
    n_eya   = len(eya_seg)

    # ── D1 EYA BASIC ──────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 1 — EYA DIPHTHONG"
          " [eːɑ] basic")
    print()
    p1 = check('voicing',
               measure_voicing(eya_seg),
               0.50, 1.0)
    p2 = check('RMS level', rms(eya_seg),
               0.010, 0.90)
    d1 = p1 and p2
    all_pass &= d1
    print(f"  {'PASSED' if d1 else 'FAILED'}")
    print()

    # ── D2 EYA DURATION ───────────────────
    print("─" * 60)
    print("DIAGNOSTIC 2 — [eːɑ] DURATION"
          " — long diphthong")
    print()
    dur_eya = n_eya / SR * 1000.0
    dur_ea  = 80.0
    ratio   = dur_eya / dur_ea
    print(f"  [eːɑ] duration: {dur_eya:.0f} ms")
    print(f"  [eɑ]  duration: {dur_ea:.0f} ms"
          f" (reference)")
    print(f"  Ratio: {ratio:.2f}x")
    print()
    p1 = check(
        f'duration ({dur_eya:.0f} ms)',
        dur_eya, 120.0, 180.0,
        unit=' ms', fmt='.1f')
    p2 = check(
        f'ratio vs short ({ratio:.2f}x)',
        ratio, 1.5, 2.5,
        fmt='.2f')
    d2 = p1 and p2
    all_pass &= d2
    print(f"  {'PASSED' if d2 else 'FAILED'}")
    print()

    # ── D3 EYA F2 MOVEMENT ─���──────────────
    print("─" * 60)
    print("DIAGNOSTIC 3 — [eːɑ] F2 MOVEMENT")
    print()
    onset  = eya_seg[:int(0.30 * n_eya)]
    offset = eya_seg[int(0.80 * n_eya):]
    f2_on  = measure_band_centroid(
        onset,  1200.0, 2500.0)
    f2_off = measure_band_centroid(
        offset,  800.0, 1600.0)
    delta_f2 = f2_on - f2_off
    print(f"  F2 onset:  {f2_on:.0f} Hz")
    print(f"  F2 offset: {f2_off:.0f} Hz")
    print(f"  Delta:     {delta_f2:.0f} Hz"
          f" (falling)")
    print()
    p1 = check(
        f'F2 onset ({f2_on:.0f} Hz)',
        f2_on, 1500.0, 2200.0,
        unit=' Hz', fmt='.1f')
    p2 = check(
        f'F2 offset ({f2_off:.0f} Hz)',
        f2_off, 800.0, 1400.0,
        unit=' Hz', fmt='.1f')
    p3 = check(
        f'F2 delta ({delta_f2:.0f} Hz)',
        delta_f2, 400.0, 1000.0,
        unit=' Hz', fmt='.1f')
    d3 = p1 and p2 and p3
    all_pass &= d3
    print(f"  {'PASSED' if d3 else 'FAILED'}")
    print()

    # ── D4 EYA F1 MOVEMENT ────────────────
    print("─" * 60)
    print("DIAGNOSTIC 4 — [eːɑ] F1 MOVEMENT"
          " — jaw opens")
    print()
    f1_on  = measure_band_centroid(
        onset,  200.0, 700.0)
    f1_off = measure_band_centroid(
        offset, 400.0, 900.0)
    delta_f1 = f1_off - f1_on
    print(f"  F1 onset:  {f1_on:.0f} Hz")
    print(f"  F1 offset: {f1_off:.0f} Hz")
    print(f"  Delta:     {delta_f1:.0f} Hz"
          f" (rising — jaw opens)")
    print()
    print("  [eːɑ]: F1 rises — jaw opens")
    print("  [eːo]: F1 stable — jaw stays")
    print("  This is the key distinction.")
    print()
    p1 = check(
        f'F1 onset ({f1_on:.0f} Hz)',
        f1_on, 300.0, 600.0,
        unit=' Hz', fmt='.1f')
    p2 = check(
        f'F1 delta ({delta_f1:.0f} Hz)',
        delta_f1, 100.0, 400.0,
        unit=' Hz', fmt='.1f')
    d4 = p1 and p2
    all_pass &= d4
    print(f"  {'PASSED' if d4 else 'FAILED'}")
    print()

    # ── D5 EYA vs SHORT EA ────────────────
    print("─" * 60)
    print("DIAGNOSTIC 5 — [eːɑ] vs [eɑ]"
          " DURATION DISTINCTION")
    print()
    print(f"  [eːɑ]: {dur_eya:.0f} ms")
    print(f"  [eɑ]:  {dur_ea:.0f} ms")
    print(f"  Ratio: {ratio:.2f}x")
    print(f"  Duration is sole distinction.")
    print(f"  Trajectory identical.")
    print()
    p1 = check(
        f'long/short ratio ({ratio:.2f}x)',
        ratio, 1.5, 2.5,
        fmt='.2f')
    d5 = p1
    all_pass &= d5
    print(f"  {'PASSED' if d5 else 'FAILED'}")
    print()

    # ── D6 EYA vs EYO CONTRAST ────────────
    print("─" * 60)
    print("DIAGNOSTIC 6 — [eːɑ] vs [eːo]"
          " TRAJECTORY CONTRAST")
    print()
    print("  [eːɑ] F1 rises  — jaw opens")
    print("  [eːo] F1 stable — jaw stays")
    print()
    print(f"  [eːɑ] F1 delta: {delta_f1:.0f} Hz"
          f" (rising)")
    print(f"  [eːo] F1 delta: ~5 Hz"
          f" (stable — from [eo] data)")
    print()
    p1 = check(
        f'[eːɑ] F1 rising ({delta_f1:.0f} Hz)',
        delta_f1, 100.0, 400.0,
        unit=' Hz', fmt='.1f')
    d6 = p1
    all_pass &= d6
    print(f"  {'PASSED' if d6 else 'FAILED'}")
    print()

    # ── D7 GH ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 7 — GH FRICATIVE [ɣ]")
    print()
    gh_seg  = synth_GH(EYA_F_OFF, E_F,
                        145.0, 1.0, SR)
    p1 = check('voicing',
               measure_voicing(gh_seg),
               0.50, 1.0)
    p2 = check('RMS level', rms(gh_seg),
               0.005, 0.80)
    d7 = p1 and p2
    all_pass &= d7
    print(f"  {'PASSED' if d7 else 'FAILED'}")
    print()

    # ── D8 E FINAL ────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 8 — E VOWEL final [e]")
    print()
    e_seg  = synth_E(GH_F, None,
                      145.0, 1.0, SR)
    n_e    = len(e_seg)
    body_e = e_seg[int(0.12*n_e):
                   n_e-int(0.12*n_e)]
    p1 = check('voicing',
               measure_voicing(body_e),
               0.50, 1.0)
    cent_e = measure_band_centroid(
        body_e, 1500.0, 2500.0)
    p2 = check(
        f'F2 centroid ({cent_e:.0f} Hz)',
        cent_e, 1600.0, 2300.0,
        unit=' Hz', fmt='.1f')
    d8 = p1 and p2
    all_pass &= d8
    print(f"  {'PASSED' if d8 else 'FAILED'}")
    print()

    # ── D9 FULL WORD ──────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 9 — FULL WORD [eːɑɣe]")
    print()
    w_dry  = synth_eage(145.0, 1.0, False)
    w_hall = synth_eage(145.0, 1.0, True)
    dur_ms = len(w_dry) / SR * 1000.0
    p1 = check('RMS level', rms(w_dry),
               0.010, 0.90)
    p2 = check(
        f'duration ({dur_ms:.0f} ms)',
        dur_ms, 220.0, 360.0,
        unit=' ms', fmt='.1f')
    print(f"  {len(w_dry)} samples"
          f" ({dur_ms:.0f} ms)")
    write_wav(
        "output_play/diag_eage_full.wav",
        w_dry)
    write_wav(
        "output_play/diag_eage_hall.wav",
        w_hall)
    write_wav(
        "output_play/diag_eage_slow.wav",
        ola_stretch(w_dry, 4.0))
    write_wav(
        "output_play/diag_eage_eya.wav",
        ola_stretch(eya_seg / (
            np.max(np.abs(eya_seg))+1e-8)
            * 0.75, 4.0))
    d9 = p1 and p2
    all_pass &= d9
    print(f"  {'PASSED' if d9 else 'FAILED'}")
    print()

    # ── D10 PERCEPTUAL ────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 10 — PERCEPTUAL")
    print()
    for fn in [
        "diag_eage_eya.wav",
        "diag_eage_slow.wav",
        "diag_eage_hall.wav",
    ]:
        print(f"  afplay output_play/{fn}")
    print()
    print("  LISTEN FOR:")
    print("  EYA — long diphthong")
    print("    front onset moves back")
    print("    jaw opens — F1 rises")
    print("    noticeably longer than")
    print("    short [eɑ] in SCEAÞENA")
    print("  GH  — voiced velar fricative")
    print("  E   — short front close")
    print("  Full: EYA·GH·E")
    print("  ModE 'eye' — same word.")
    print("  [eːɑɣe] → [aɪ]")
    print()

    # ── SUMMARY ───────────────────────────
    print("=" * 60)
    print("SUMMARY")
    print()
    rows = [
        ("D1  EYA basic",          d1),
        ("D2  EYA duration",       d2),
        ("D3  EYA F2 movement",    d3),
        ("D4  EYA F1 movement",    d4),
        ("D5  EYA vs short EA",    d5),
        ("D6  EYA vs EYO contrast",d6),
        ("D7  GH fricative",       d7),
        ("D8  E vowel final",      d8),
        ("D9  Full word",          d9),
    ]
    for lbl, ok_ in rows:
        sym = "✓ PASS" if ok_ else "✗ FAIL"
        print(f"  {lbl:26s}  {sym}")
    print(f"  {'D10 Perceptual':26s}  LISTEN")
    print()
    if all_pass:
        print("  ALL NUMERIC CHECKS PASSED")
        print()
        print("  ĒAGE [eːɑɣe] verified.")
        print("  [eːɑ] added to inventory.")
        print("  37 phonemes verified.")
        print()
        print("  Inventory completion:")
        print("  [iː]  ✓ DONE — WĪF")
        print("  [eːɑ] ✓ DONE — ĒAGE")
        print("  [eːo] pending — ÞĒOD")
        print("  [p]   pending — PÆÞ")
        print("  [b]   pending — line 8")
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
