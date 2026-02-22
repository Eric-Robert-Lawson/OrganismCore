"""
WEARÐ DIAGNOSTIC v1
Old English: wearð [weɑrθ]
Beowulf line 7, word 5
Zero new phonemes — pure assembly
February 2026

DIAGNOSTICS:
  D1  W approximant [w]
  D2  EA diphthong [eɑ] — F2 movement
  D3  EA F1 movement — jaw opens
  D4  R trill [r]
  D5  TH fricative [θ]
  D6  Full word
  D7  Perceptual

KEY CHECKS:
  D2: F2 falls — onset ~1850, offset ~1100
  D3: F1 rises — jaw opens
      confirms [eɑ] not [eo]
  D4: voicing >= 0.50
      R_TRILL_DEPTH 0.40 from outset
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
    print("WEARÐ DIAGNOSTIC v1")
    print("Old English [weɑrθ]")
    print("Beowulf line 7, word 5")
    print("Zero new phonemes — pure assembly")
    print("=" * 60)
    print()

    try:
        from wearth_reconstruction import (
            synth_wearth,
            synth_W, synth_EA,
            synth_R, synth_TH,
            apply_simple_room,
            W_F, EA_F_ON, EA_F_OFF,
            R_F, PITCH_PERF, DIL_PERF)
        print("  wearth_reconstruction.py: OK")
    except ImportError as e:
        print(f"  IMPORT FAILED: {e}")
        return False
    print()

    all_pass = True

    # ── D1 W ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 1 — W APPROXIMANT [w]")
    print()
    w_seg  = synth_W(None, EA_F_ON,
                      145.0, 1.0, SR)
    p1 = check('voicing',
               measure_voicing(w_seg),
               0.50, 1.0)
    p2 = check('RMS level', rms(w_seg),
               0.005, 0.80)
    d1 = p1 and p2
    all_pass &= d1
    print(f"  {'PASSED' if d1 else 'FAILED'}")
    print()

    # ── D2 EA F2 MOVEMENT ─────────────────
    print("─" * 60)
    print("DIAGNOSTIC 2 — EA DIPHTHONG [eɑ]"
          " F2 movement")
    print()
    ea_seg = synth_EA(W_F, R_F,
                       145.0, 1.0, SR)
    n_ea   = len(ea_seg)
    onset  = ea_seg[:int(0.25 * n_ea)]
    offset = ea_seg[int(0.85 * n_ea):]
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
    p1 = check('voicing',
               measure_voicing(ea_seg),
               0.50, 1.0)
    p2 = check(
        f'F2 onset ({f2_on:.0f} Hz)',
        f2_on, 1500.0, 2200.0,
        unit=' Hz', fmt='.1f')
    p3 = check(
        f'F2 offset ({f2_off:.0f} Hz)',
        f2_off, 800.0, 1400.0,
        unit=' Hz', fmt='.1f')
    p4 = check(
        f'F2 delta ({delta_f2:.0f} Hz)',
        delta_f2, 400.0, 1000.0,
        unit=' Hz', fmt='.1f')
    d2 = p1 and p2 and p3 and p4
    all_pass &= d2
    print(f"  {'PASSED' if d2 else 'FAILED'}")
    print()

    # ── D3 EA F1 MOVEMENT ─────────────────
    print("─" * 60)
    print("DIAGNOSTIC 3 — EA F1 MOVEMENT"
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
    print(f"  Confirms [eɑ] not [eo]")
    print()
    p1 = check(
        f'F1 delta ({delta_f1:.0f} Hz)',
        delta_f1, 100.0, 400.0,
        unit=' Hz', fmt='.1f')
    d3 = p1
    all_pass &= d3
    print(f"  {'PASSED' if d3 else 'FAILED'}")
    print()

    # ── D4 R ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 4 — R TRILL [r]")
    print("  TRILL_DEPTH 0.40 from outset")
    print()
    r_seg  = synth_R(EA_F_OFF, None,
                      145.0, 1.0, SR)
    p1 = check('voicing',
               measure_voicing(r_seg),
               0.50, 1.0)
    p2 = check('RMS level', rms(r_seg),
               0.005, 0.80)
    d4 = p1 and p2
    all_pass &= d4
    print(f"  {'PASSED' if d4 else 'FAILED'}")
    print()

    # ── D5 TH ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 5 — TH FRICATIVE [θ]")
    print()
    th_seg = synth_TH(R_F, None, 1.0, SR)
    p1 = check('voicing (must be low)',
               measure_voicing(th_seg),
               0.0, 0.35)
    p2 = check('RMS level', rms(th_seg),
               0.001, 0.50)
    d5 = p1 and p2
    all_pass &= d5
    print(f"  {'PASSED' if d5 else 'FAILED'}")
    print()

    # ── D6 FULL WORD ──────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 6 — FULL WORD [weɑrθ]")
    print()
    w_dry  = synth_wearth(145.0, 1.0, False)
    w_hall = synth_wearth(145.0, 1.0, True)
    w_perf = synth_wearth(
        PITCH_PERF, DIL_PERF, True)
    dur_ms      = len(w_dry)  / SR * 1000.0
    dur_perf_ms = len(w_perf) / SR * 1000.0
    p1 = check('RMS level', rms(w_dry),
               0.010, 0.90)
    p2 = check(
        f'duration ({dur_ms:.0f} ms)',
        dur_ms, 220.0, 380.0,
        unit=' ms', fmt='.1f')
    print(f"  {len(w_dry)} samples"
          f" ({dur_ms:.0f} ms) — diagnostic")
    print(f"  {len(w_perf)} samples"
          f" ({dur_perf_ms:.0f} ms)"
          f" — performance")
    write_wav(
        "output_play/diag_wearth_full.wav",
        w_dry)
    write_wav(
        "output_play/diag_wearth_hall.wav",
        w_hall)
    write_wav(
        "output_play/diag_wearth_slow.wav",
        ola_stretch(w_dry, 4.0))
    write_wav(
        "output_play/diag_wearth_perf.wav",
        w_perf)
    d6 = p1 and p2
    all_pass &= d6
    print(f"  {'PASSED' if d6 else 'FAILED'}")
    print()

    # ── D7 PERCEPTUAL ─────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 7 — PERCEPTUAL")
    print()
    print("  Diagnostic versions:")
    for fn in [
        "diag_wearth_full.wav",
        "diag_wearth_slow.wav",
        "diag_wearth_hall.wav",
    ]:
        print(f"  afplay output_play/{fn}")
    print()
    print("  Performance version:")
    print("  afplay output_play/"
          "diag_wearth_perf.wav")
    print(f"  [{PITCH_PERF} Hz,"
          f" dil {DIL_PERF},"
          f" hall RT60=2.0s]")
    print()
    print("  LISTEN FOR:")
    print("  W  — voiced labio-velar onset")
    print("  EA — diphthong")
    print("    front onset moves back")
    print("    jaw opens — F1 rises")
    print("    same diphthong as SCEAÞENA")
    print("  R  — trill")
    print("  TH — voiceless dental close")
    print("  Full: W·EA·R·TH")
    print("  ModE 'worth/ward' — same root")
    print("  weorþan — to become")
    print("  syþðan ǣrest wearð —")
    print("  since first it came to be")
    print("  LINE 7 COMPLETE")
    print()

    # ── SUMMARY ───────────────────────────
    print("=" * 60)
    print("SUMMARY")
    print()
    rows = [
        ("D1  W approximant",       d1),
        ("D2  EA F2 movement",      d2),
        ("D3  EA F1 movement",      d3),
        ("D4  R trill",             d4),
        ("D5  TH fricative",        d5),
        ("D6  Full word",           d6),
    ]
    for lbl, ok_ in rows:
        sym = "✓ PASS" if ok_ else "✗ FAIL"
        print(f"  {lbl:26s}  {sym}")
    print(f"  {'D7 Perceptual':26s}  LISTEN")
    print()
    if all_pass:
        print("  ALL NUMERIC CHECKS PASSED")
        print()
        print("  WEARÐ [weɑrθ] verified.")
        print("  Zero new phonemes.")
        print("  39 phonemes verified.")
        print()
        print("  LINE 7 COMPLETE:")
        print("  egsode  ✓")
        print("  eorlas  ✓")
        print("  syþðan  ✓")
        print("  ǣrest   ✓")
        print("  wearð   ✓")
        print()
        print("  Next: line 8")
        print("  feasceaft funden,")
        print("  hē þæs frōfre gebād")
        print("  [b] arrives — GEBĀD")
        print("  40th phoneme.")
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
