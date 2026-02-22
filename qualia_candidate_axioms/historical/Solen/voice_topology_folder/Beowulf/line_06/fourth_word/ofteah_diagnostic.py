"""
OFTEAH DIAGNOSTIC v1
Old English: ofteah [ofteɑx]
Beowulf line 6, word 4
Line 6 final word.
February 2026

DIAGNOSTICS:
  D1  O vowel [o]
  D2  F fricative [f]
  D3  T stop [t]
  D4  EA diphthong [eɑ]
  D5  EA F2 movement
  D6  X fricative [x]
  D7  [x] voicelessness confirmed
  D8  Full word
  D9  Perceptual

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
    print("OFTEAH DIAGNOSTIC v1")
    print("Old English [ofteɑx]")
    print("Beowulf line 6, word 4")
    print("Line 6 final word.")
    print("=" * 60)
    print()

    try:
        from ofteah_reconstruction import (
            synth_ofteah,
            synth_O, synth_F,
            synth_T, synth_EA,
            synth_X,
            apply_simple_room,
            O_F, EA_F_ON, EA_F_OFF)
        print("  ofteah_reconstruction.py: OK")
    except ImportError as e:
        print(f"  IMPORT FAILED: {e}")
        return False
    print()

    all_pass = True

    # ── D1 O ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 1 — O VOWEL [o]")
    print()
    o_seg  = synth_O(None, None,
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
    d1 = p1 and p2
    all_pass &= d1
    print(f"  {'PASSED' if d1 else 'FAILED'}")
    print()

    # ── D2 F ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 2 — F FRICATIVE [f]")
    print()
    f_seg  = synth_F(O_F, None, 1.0, SR)
    p1 = check('voicing (must be low)',
               measure_voicing(f_seg),
               0.0, 0.35)
    p2 = check('RMS level', rms(f_seg),
               0.001, 0.50)
    d2 = p1 and p2
    all_pass &= d2
    print(f"  {'PASSED' if d2 else 'FAILED'}")
    print()

    # ── D3 T ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 3 — T STOP [t]")
    print()
    t_seg = synth_T(None, EA_F_ON,
                     1.0, SR)
    p1 = check('voicing (must be low)',
               measure_voicing(t_seg),
               0.0, 0.35)
    p2 = check('RMS level', rms(t_seg),
               0.005, 0.80)
    d3 = p1 and p2
    all_pass &= d3
    print(f"  {'PASSED' if d3 else 'FAILED'}")
    print()

    # ── D4 EA ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 4 — EA DIPHTHONG [eɑ]")
    print()
    ea_seg = synth_EA(None, None,
                       145.0, 1.0, SR)
    p1 = check('voicing',
               measure_voicing(ea_seg),
               0.50, 1.0)
    p2 = check('RMS level', rms(ea_seg),
               0.010, 0.90)
    d4 = p1 and p2
    all_pass &= d4
    print(f"  {'PASSED' if d4 else 'FAILED'}")
    print()

    # ── D5 EA MOVEMENT ────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 5 — [eɑ] F2 MOVEMENT")
    print()
    n_ea   = len(ea_seg)
    onset  = ea_seg[:int(0.30 * n_ea)]
    offset = ea_seg[int(0.80 * n_ea):]
    f2_on  = measure_band_centroid(
        onset,  1200.0, 2500.0)
    f2_off = measure_band_centroid(
        offset,  800.0, 1800.0)
    delta  = f2_on - f2_off
    print(f"  F2 onset:  {f2_on:.0f} Hz")
    print(f"  F2 offset: {f2_off:.0f} Hz")
    print(f"  Delta:     {delta:.0f} Hz"
          f" (falling)")
    print()
    p1 = check(
        f'F2 onset ({f2_on:.0f} Hz)',
        f2_on, 1500.0, 2200.0,
        unit=' Hz', fmt='.1f')
    p2 = check(
        f'F2 offset ({f2_off:.0f} Hz)',
        f2_off, 800.0, 1500.0,
        unit=' Hz', fmt='.1f')
    p3 = check(
        f'F2 delta ({delta:.0f} Hz)',
        delta, 400.0, 1200.0,
        unit=' Hz', fmt='.1f')
    d5 = p1 and p2 and p3
    all_pass &= d5
    print(f"  {'PASSED' if d5 else 'FAILED'}")
    print()

    # ── D6 X ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 6 — X FRICATIVE [x]")
    print()
    x_seg   = synth_X(EA_F_OFF, None,
                       1.0, SR)
    voic_x  = measure_voicing(x_seg)
    cent_x  = measure_band_centroid(
        x_seg, 1000.0, 8000.0)
    p1 = check('voicing (must be low)',
               voic_x, 0.0, 0.35)
    p2 = check(
        f'centroid ({cent_x:.0f} Hz)',
        cent_x, 1500.0, 5000.0,
        unit=' Hz', fmt='.1f')
    p3 = check('RMS level', rms(x_seg),
               0.001, 0.50)
    d6 = p1 and p2 and p3
    all_pass &= d6
    print(f"  {'PASSED' if d6 else 'FAILED'}")
    print()

    # ── D7 X vs GH DISTINCTION ────────────
    print("─" * 60)
    print("DIAGNOSTIC 7 — [x] vs [ɣ]"
          " VOICELESSNESS")
    print()
    print("  [x] voicing must be <= 0.35")
    print("  [ɣ] voicing 0.7607"
          " (verified MǢGÞUM)")
    print()
    print(f"  [x] measured: {voic_x:.4f}")
    print(f"  [ɣ] reference: 0.7607")
    print()
    p1 = check(
        '[x] voicing (must be low)',
        voic_x, 0.0, 0.35)
    d7 = p1
    all_pass &= d7
    print(f"  {'PASSED' if d7 else 'FAILED'}")
    print()

    # ── D8 FULL WORD ──────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 8 — FULL WORD [ofteɑx]")
    print()
    w_dry  = synth_ofteah(145.0, 1.0, False)
    w_hall = synth_ofteah(145.0, 1.0, True)
    dur_ms = len(w_dry) / SR * 1000.0
    p1 = check('RMS level', rms(w_dry),
               0.010, 0.90)
    p2 = check(
        f'duration ({dur_ms:.0f} ms)',
        dur_ms, 290.0, 500.0,
        unit=' ms', fmt='.1f')
    print(f"  {len(w_dry)} samples"
          f" ({dur_ms:.0f} ms)")
    write_wav(
        "output_play/diag_ofteah_full.wav",
        w_dry)
    write_wav(
        "output_play/diag_ofteah_hall.wav",
        w_hall)
    write_wav(
        "output_play/diag_ofteah_slow.wav",
        ola_stretch(w_dry, 4.0))
    d8 = p1 and p2
    all_pass &= d8
    print(f"  {'PASSED' if d8 else 'FAILED'}")
    print()

    # ── D9 PERCEPTUAL ─────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 9 — PERCEPTUAL")
    print()
    for fn in [
        "diag_ofteah_slow.wav",
        "diag_ofteah_hall.wav",
    ]:
        print(f"  afplay output_play/{fn}")
    print()
    print("  LISTEN FOR:")
    print("  O — back rounded vowel")
    print("  FT — voiceless cluster")
    print("    fricative then stop")
    print("    no voicing between them")
    print("  EA — diphthong front→back")
    print("  X — velar fricative close")
    print("    like Scottish 'loch'")
    print("    word ends on this")
    print("  Full: O·F·T·EA·X")
    print("  Five events.")
    print("  'off-tay-akh'")
    print("  approximately.")
    print()

    # ── SUMMARY ───────────────────────────
    print("=" * 60)
    print("SUMMARY")
    print()
    rows = [
        ("D1  O vowel",          d1),
        ("D2  F fricative",      d2),
        ("D3  T stop",           d3),
        ("D4  EA diphthong",     d4),
        ("D5  EA F2 movement",   d5),
        ("D6  X fricative",      d6),
        ("D7  X/GH distinction", d7),
        ("D8  Full word",        d8),
    ]
    for lbl, ok_ in rows:
        sym = "✓ PASS" if ok_ else "✗ FAIL"
        print(f"  {lbl:24s}  {sym}")
    print(f"  {'D9 Perceptual':24s}  LISTEN")
    print()
    if all_pass:
        print("  ALL NUMERIC CHECKS PASSED")
        print()
        print("  OFTEAH [ofteɑx] verified.")
        print("  Zero new phonemes.")
        print("  35 phonemes verified.")
        print()
        print("  LINE 6 COMPLETE:")
        print("  mongum mǣgþum"
              " meodosetla ofteah")
        print()
        print("  Next: line 7.")
        print("  egsode eorlas,"
              " syþðan ǣrest wearð")
        print("  NEW PHONEMES: [iː] [p] [b]")
        print("  Three gaps closing.")
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
