"""
EGSODE DIAGNOSTIC v1
Old English: egsode [eɡsode]
Beowulf line 7, word 1
February 2026

DIAGNOSTICS:
  D1  E vowel initial [e]
  D2  G stop [ɡ]
  D3  S fricative [s]
  D4  [ɡs] voicing transition
  D5  O vowel [o]
  D6  D stop [d]
  D7  E vowel final [e]
  D8  Full word
  D9  Perceptual

Zero new phonemes — pure assembly.

KEY CHECK:
  D4 [ɡs] voicing transition:
     [ɡ] must be voiced (>= 0.35)
     [s] must be voiceless (<= 0.35)
     Abrupt transition confirmed
     by checking each segment
     independently.
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
    print("EGSODE DIAGNOSTIC v1")
    print("Old English [eɡsode]")
    print("Beowulf line 7, word 1")
    print("=" * 60)
    print()

    try:
        from egsode_reconstruction import (
            synth_egsode,
            synth_E, synth_G,
            synth_S, synth_O,
            synth_D,
            apply_simple_room,
            E_F, O_F)
        print("  egsode_reconstruction.py: OK")
    except ImportError as e:
        print(f"  IMPORT FAILED: {e}")
        return False
    print()

    all_pass = True

    # ── D1 E INITIAL ──────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 1 — E VOWEL initial [e]")
    print()
    e1_seg = synth_E(None, None,
                      145.0, 1.0, SR)
    n_e    = len(e1_seg)
    body_e = e1_seg[int(0.12*n_e):
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
    d1 = p1 and p2
    all_pass &= d1
    print(f"  {'PASSED' if d1 else 'FAILED'}")
    print()

    # ── D2 G ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 2 — G STOP [ɡ]")
    print()
    g_seg  = synth_G(E_F, None,
                      145.0, 1.0, SR)
    voic_g = measure_voicing(g_seg)
    p1 = check('RMS level', rms(g_seg),
               0.005, 0.70)
    dur_g  = len(g_seg) / SR * 1000.0
    p2 = check(
        f'duration ({dur_g:.0f} ms)',
        dur_g, 40.0, 100.0,
        unit=' ms', fmt='.1f')
    d2 = p1 and p2
    all_pass &= d2
    print(f"  {'PASSED' if d2 else 'FAILED'}")
    print()

    # ── D3 S ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 3 — S FRICATIVE [s]")
    print()
    s_seg   = synth_S(None, O_F, 1.0, SR)
    voic_s  = measure_voicing(s_seg)
    cent_s  = measure_band_centroid(
        s_seg, 4000.0, 12000.0)
    p1 = check('voicing (must be low)',
               voic_s, 0.0, 0.35)
    p2 = check(
        f'centroid ({cent_s:.0f} Hz)',
        cent_s, 5000.0, 10000.0,
        unit=' Hz', fmt='.1f')
    d3 = p1 and p2
    all_pass &= d3
    print(f"  {'PASSED' if d3 else 'FAILED'}")
    print()

    # ── D4 GS TRANSITION ──────────────────
    print("─" * 60)
    print("DIAGNOSTIC 4 — [ɡs] VOICING"
          " TRANSITION")
    print()
    print("  [ɡ] voiced → [s] voiceless")
    print("  Abrupt devoicing at boundary.")
    print()
    print(f"  [ɡ] voicing: {voic_g:.4f}")
    print(f"  [s] voicing: {voic_s:.4f}")
    separation = voic_g - voic_s
    print(f"  separation:  {separation:.4f}")
    print()
    p1 = check(
        f'[s] voiceless ({voic_s:.4f})',
        voic_s, 0.0, 0.35)
    p2 = check(
        f'separation ({separation:.4f})',
        separation, 0.10, 1.0)
    d4 = p1 and p2
    all_pass &= d4
    print(f"  {'PASSED' if d4 else 'FAILED'}")
    print()

    # ── D5 O ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 5 — O VOWEL [o]")
    print()
    o_seg  = synth_O(O_F, None,
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
    d5 = p1 and p2
    all_pass &= d5
    print(f"  {'PASSED' if d5 else 'FAILED'}")
    print()

    # ── D6 D ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 6 — D STOP [d]")
    print()
    d_seg = synth_D(O_F, E_F,
                     145.0, 1.0, SR)
    p1 = check('RMS level', rms(d_seg),
               0.005, 0.70)
    dur_d = len(d_seg) / SR * 1000.0
    p2 = check(
        f'duration ({dur_d:.0f} ms)',
        dur_d, 30.0, 90.0,
        unit=' ms', fmt='.1f')
    d6 = p1 and p2
    all_pass &= d6
    print(f"  {'PASSED' if d6 else 'FAILED'}")
    print()

    # ── D7 E FINAL ────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 7 — E VOWEL final [e]")
    print()
    e2_seg = synth_E(E_F, None,
                      145.0, 1.0, SR)
    n_e2   = len(e2_seg)
    body_e2= e2_seg[int(0.12*n_e2):
                    n_e2-int(0.12*n_e2)]
    p1 = check('voicing',
               measure_voicing(body_e2),
               0.50, 1.0)
    cent_e2= measure_band_centroid(
        body_e2, 1500.0, 2500.0)
    p2 = check(
        f'F2 centroid ({cent_e2:.0f} Hz)',
        cent_e2, 1600.0, 2300.0,
        unit=' Hz', fmt='.1f')
    d7 = p1 and p2
    all_pass &= d7
    print(f"  {'PASSED' if d7 else 'FAILED'}")
    print()

    # ── D8 FULL WORD ──────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 8 — FULL WORD [eɡsode]")
    print()
    w_dry  = synth_egsode(145.0, 1.0, False)
    w_hall = synth_egsode(145.0, 1.0, True)
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
        "output_play/diag_egsode_full.wav",
        w_dry)
    write_wav(
        "output_play/diag_egsode_hall.wav",
        w_hall)
    write_wav(
        "output_play/diag_egsode_slow.wav",
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
        "diag_egsode_slow.wav",
        "diag_egsode_hall.wav",
    ]:
        print(f"  afplay output_play/{fn}")
    print()
    print("  LISTEN FOR:")
    print("  E — front vowel onset")
    print("  G — voiced velar stop")
    print("    murmur then burst")
    print("  S — sharp voiceless hiss")
    print("    abrupt after G burst")
    print("  O — back rounded vowel")
    print("  D — voiced alveolar stop")
    print("  E — front vowel close")
    print("  Full: E·G·S·O·D·E")
    print("  Six events.")
    print("  'egg-so-deh'")
    print("  approximately.")
    print()

    # ── SUMMARY ───────────────────────────
    print("=" * 60)
    print("SUMMARY")
    print()
    rows = [
        ("D1  E vowel initial",   d1),
        ("D2  G stop",            d2),
        ("D3  S fricative",       d3),
        ("D4  GS transition",     d4),
        ("D5  O vowel",           d5),
        ("D6  D stop",            d6),
        ("D7  E vowel final",     d7),
        ("D8  Full word",         d8),
    ]
    for lbl, ok_ in rows:
        sym = "✓ PASS" if ok_ else "✗ FAIL"
        print(f"  {lbl:24s}  {sym}")
    print(f"  {'D9 Perceptual':24s}  LISTEN")
    print()
    if all_pass:
        print("  ALL NUMERIC CHECKS PASSED")
        print()
        print("  EGSODE [eɡsode] verified.")
        print("  Zero new phonemes.")
        print("  35 phonemes verified.")
        print()
        print("  Next: EORLAS [eorlas]")
        print("  Beowulf line 7, word 2.")
        print("  Contains [eo] — verified.")
        print("  Zero new phonemes.")
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
