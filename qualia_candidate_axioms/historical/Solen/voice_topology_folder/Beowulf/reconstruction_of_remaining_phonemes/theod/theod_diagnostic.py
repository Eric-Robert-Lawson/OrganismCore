"""
ÞĒOD DIAGNOSTIC v1
Old English: þēod [θeːod]
Inventory completion — word 3 of 4
New phoneme: [eːo]
February 2026

DIAGNOSTICS:
  D1  EYO diphthong [eːo] basic
  D2  EYO duration — long diphthong
  D3  EYO F2 movement — steep fall
  D4  EYO F1 stability — jaw stays
  D5  EYO vs short [eo] — duration only
  D6  EYO vs [eːɑ] — F1 distinction
  D7  TH fricative [θ]
  D8  D stop [d]
  D9  Full word
  D10 Perceptual

KEY CHECKS:
  D2: duration >= 120 ms (long diphthong)
  D3: F2 falls steeply
      onset ~1900, offset ~800
      delta >= 800 Hz
      steeper than [eːɑ] (737 Hz)
  D4: F1 stable — delta <= 100 Hz
      this is the critical check
      distinguishes [eːo] from [eːɑ]
  D6: [eːo] F1 delta <= 100 Hz
      [eːɑ] F1 delta  = 281 Hz
      separation >= 150 Hz
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
    print("ÞĒOD DIAGNOSTIC v1")
    print("Old English [θeːod]")
    print("Inventory completion — word 3 of 4")
    print("New phoneme: [eːo]")
    print("=" * 60)
    print()

    try:
        from theod_reconstruction import (
            synth_theod,
            synth_TH, synth_EYO, synth_D,
            apply_simple_room,
            EYO_F_ON, EYO_F_OFF)
        print("  theod_reconstruction.py: OK")
    except ImportError as e:
        print(f"  IMPORT FAILED: {e}")
        return False
    print()

    all_pass = True

    eyo_seg = synth_EYO(EYO_F_ON, None,
                         145.0, 1.0, SR)
    n_eyo   = len(eyo_seg)

    # ── D1 EYO BASIC ──────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 1 — EYO DIPHTHONG"
          " [eːo] basic")
    print()
    p1 = check('voicing',
               measure_voicing(eyo_seg),
               0.50, 1.0)
    p2 = check('RMS level', rms(eyo_seg),
               0.010, 0.90)
    d1 = p1 and p2
    all_pass &= d1
    print(f"  {'PASSED' if d1 else 'FAILED'}")
    print()

    # ── D2 EYO DURATION ───────────────────
    print("─" * 60)
    print("DIAGNOSTIC 2 — [eːo] DURATION"
          " — long diphthong")
    print()
    dur_eyo = n_eyo / SR * 1000.0
    dur_eo  = 75.0
    ratio   = dur_eyo / dur_eo
    print(f"  [eːo] duration: {dur_eyo:.0f} ms")
    print(f"  [eo]  duration: {dur_eo:.0f} ms"
          f" (reference)")
    print(f"  Ratio: {ratio:.2f}x")
    print()
    p1 = check(
        f'duration ({dur_eyo:.0f} ms)',
        dur_eyo, 120.0, 180.0,
        unit=' ms', fmt='.1f')
    p2 = check(
        f'ratio vs short ({ratio:.2f}x)',
        ratio, 1.5, 2.5,
        fmt='.2f')
    d2 = p1 and p2
    all_pass &= d2
    print(f"  {'PASSED' if d2 else 'FAILED'}")
    print()

    # ── D3 EYO F2 MOVEMENT ────────────────
    print("─" * 60)
    print("DIAGNOSTIC 3 — [eːo] F2 MOVEMENT"
          " — steep fall")
    print()
    onset  = eyo_seg[:int(0.25 * n_eyo)]
    offset = eyo_seg[int(0.85 * n_eyo):]
    f2_on  = measure_band_centroid(
        onset,  1200.0, 2500.0)
    f2_off = measure_band_centroid(
        offset,  500.0, 1200.0)
    delta_f2 = f2_on - f2_off
    print(f"  F2 onset:  {f2_on:.0f} Hz")
    print(f"  F2 offset: {f2_off:.0f} Hz")
    print(f"  Delta:     {delta_f2:.0f} Hz"
          f" (falling)")
    print(f"  [eːɑ] F2 delta: 737 Hz"
          f" (reference)")
    print(f"  [eːo] steeper — target [o]"
          f" more back than [ɑ]")
    print()
    p1 = check(
        f'F2 onset ({f2_on:.0f} Hz)',
        f2_on, 1400.0, 2200.0,
        unit=' Hz', fmt='.1f')
    p2 = check(
        f'F2 offset ({f2_off:.0f} Hz)',
        f2_off, 500.0, 1100.0,
        unit=' Hz', fmt='.1f')
    p3 = check(
        f'F2 delta ({delta_f2:.0f} Hz)',
        delta_f2, 800.0, 1500.0,
        unit=' Hz', fmt='.1f')
    d3 = p1 and p2 and p3
    all_pass &= d3
    print(f"  {'PASSED' if d3 else 'FAILED'}")
    print()

    # ── D4 EYO F1 STABILITY ───────────────
    print("─" * 60)
    print("DIAGNOSTIC 4 — [eːo] F1 STABILITY"
          " — jaw stays")
    print()
    f1_on  = measure_band_centroid(
        onset,  200.0, 700.0)
    f1_off = measure_band_centroid(
        offset, 200.0, 700.0)
    delta_f1 = abs(f1_off - f1_on)
    print(f"  F1 onset:  {f1_on:.0f} Hz")
    print(f"  F1 offset: {f1_off:.0f} Hz")
    print(f"  Delta:     {delta_f1:.0f} Hz"
          f" (must be small)")
    print()
    print("  [eːo]: F1 stable — jaw stays")
    print("  [eːɑ]: F1 delta 281 Hz — jaw opens")
    print("  This check is the key distinction.")
    print()
    p1 = check(
        f'F1 onset ({f1_on:.0f} Hz)',
        f1_on, 300.0, 600.0,
        unit=' Hz', fmt='.1f')
    p2 = check(
        f'F1 delta ({delta_f1:.0f} Hz)'
        f' — must be small',
        delta_f1, 0.0, 100.0,
        unit=' Hz', fmt='.1f')
    d4 = p1 and p2
    all_pass &= d4
    print(f"  {'PASSED' if d4 else 'FAILED'}")
    print()

    # ── D5 EYO vs SHORT EO ────────────────
    print("─" * 60)
    print("DIAGNOSTIC 5 — [eːo] vs [eo]"
          " DURATION DISTINCTION")
    print()
    print(f"  [eːo]: {dur_eyo:.0f} ms")
    print(f"  [eo]:  {dur_eo:.0f} ms")
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

    # ── D6 EYO vs EYA F1 DISTINCTION ─────
    print("─" * 60)
    print("DIAGNOSTIC 6 — [eːo] vs [eːɑ]"
          " F1 DISTINCTION")
    print()
    eya_f1_delta = 281.0
    separation   = eya_f1_delta - delta_f1
    print(f"  [eːo] F1 delta: {delta_f1:.0f} Hz"
          f" (stable)")
    print(f"  [eːɑ] F1 delta: {eya_f1_delta:.0f}"
          f" Hz (rising — verified ĒAGE)")
    print(f"  Separation: {separation:.0f} Hz")
    print()
    p1 = check(
        f'[eːo] F1 stable ({delta_f1:.0f} Hz)',
        delta_f1, 0.0, 100.0,
        unit=' Hz', fmt='.1f')
    p2 = check(
        f'separation vs [eːɑ]'
        f' ({separation:.0f} Hz)',
        separation, 150.0, 400.0,
        unit=' Hz', fmt='.1f')
    d6 = p1 and p2
    all_pass &= d6
    print(f"  {'PASSED' if d6 else 'FAILED'}")
    print()

    # ── D7 TH ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 7 — TH FRICATIVE [θ]")
    print()
    th_seg  = synth_TH(None, EYO_F_ON,
                        1.0, SR)
    p1 = check('voicing (must be low)',
               measure_voicing(th_seg),
               0.0, 0.35)
    p2 = check('RMS level', rms(th_seg),
               0.001, 0.50)
    d7 = p1 and p2
    all_pass &= d7
    print(f"  {'PASSED' if d7 else 'FAILED'}")
    print()

    # ── D8 D ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 8 — D STOP [d]")
    print()
    d_seg = synth_D(EYO_F_OFF, None,
                     145.0, 1.0, SR)
    p1 = check('RMS level', rms(d_seg),
               0.005, 0.70)
    dur_d = len(d_seg) / SR * 1000.0
    p2 = check(
        f'duration ({dur_d:.0f} ms)',
        dur_d, 30.0, 90.0,
        unit=' ms', fmt='.1f')
    d8 = p1 and p2
    all_pass &= d8
    print(f"  {'PASSED' if d8 else 'FAILED'}")
    print()

    # ── D9 FULL WORD ──────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 9 — FULL WORD [θeːod]")
    print()
    w_dry  = synth_theod(145.0, 1.0, False)
    w_hall = synth_theod(145.0, 1.0, True)
    dur_ms = len(w_dry) / SR * 1000.0
    p1 = check('RMS level', rms(w_dry),
               0.010, 0.90)
    p2 = check(
        f'duration ({dur_ms:.0f} ms)',
        dur_ms, 230.0, 380.0,
        unit=' ms', fmt='.1f')
    print(f"  {len(w_dry)} samples"
          f" ({dur_ms:.0f} ms)")
    write_wav(
        "output_play/diag_theod_full.wav",
        w_dry)
    write_wav(
        "output_play/diag_theod_hall.wav",
        w_hall)
    write_wav(
        "output_play/diag_theod_slow.wav",
        ola_stretch(w_dry, 4.0))
    write_wav(
        "output_play/diag_theod_eyo.wav",
        ola_stretch(eyo_seg / (
            np.max(np.abs(eyo_seg))+1e-8)
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
        "diag_theod_eyo.wav",
        "diag_theod_slow.wav",
        "diag_theod_hall.wav",
    ]:
        print(f"  afplay output_play/{fn}")
    print()
    print("  LISTEN FOR:")
    print("  TH  — voiceless dental onset")
    print("  EYO — long diphthong")
    print("    front onset moves back")
    print("    jaw stays — F1 stable")
    print("    compare ĒAGE [eːɑ]:")
    print("    ĒAGE jaw opens, this stays")
    print("    noticeably longer than")
    print("    short [eo] in MEODOSETLA")
    print("  D   — voiced alveolar close")
    print("  Full: TH·EYO·D")
    print("  ModE 'Dutch/Deutsch' — same root.")
    print()

    # ── SUMMARY ───────────────────────────
    print("=" * 60)
    print("SUMMARY")
    print()
    rows = [
        ("D1  EYO basic",            d1),
        ("D2  EYO duration",         d2),
        ("D3  EYO F2 movement",      d3),
        ("D4  EYO F1 stability",     d4),
        ("D5  EYO vs short EO",      d5),
        ("D6  EYO vs EYA F1",        d6),
        ("D7  TH fricative",         d7),
        ("D8  D stop",               d8),
        ("D9  Full word",            d9),
    ]
    for lbl, ok_ in rows:
        sym = "✓ PASS" if ok_ else "✗ FAIL"
        print(f"  {lbl:26s}  {sym}")
    print(f"  {'D10 Perceptual':26s}  LISTEN")
    print()
    if all_pass:
        print("  ALL NUMERIC CHECKS PASSED")
        print()
        print("  ÞĒOD [θeːod] verified.")
        print("  [eːo] added to inventory.")
        print("  38 phonemes verified.")
        print()
        print("  Inventory completion:")
        print("  [iː]  ✓ DONE — WĪF")
        print("  [eːɑ] ✓ DONE — ĒAGE")
        print("  [eːo] ✓ DONE — ÞĒOD")
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
