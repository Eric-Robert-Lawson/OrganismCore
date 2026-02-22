"""
SCYLD DIAGNOSTIC v1
Old English: Scyld [ʃyld]
Beowulf line 5, word 1
February 2026

DIAGNOSTICS:
  D1  SH fricative [ʃ]     NEW
  D2  Y vowel [y]
  D3  L lateral [l]
  D4  D stop [d]
  D5  [ʃ] vs [s] distinction
  D6  Full word
  D7  Perceptual

KEY CHECK:
  D5 [ʃ] vs [s] centroid distinction.
  [ʃ] centroid must be LOWER than [s].
  [s] verified ~7500 Hz.
  [ʃ] target 2500–5500 Hz.
  The distinction is the primary
  perceptual cue separating the
  two sibilants.
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
    print("SCYLD DIAGNOSTIC v1")
    print("Old English [ʃyld]")
    print("Beowulf line 5, word 1")
    print("=" * 60)
    print()

    try:
        from scyld_reconstruction import (
            synth_scyld,
            synth_SH, synth_Y,
            synth_L, synth_D,
            apply_simple_room,
            Y_F, L_F)
        print("  scyld_reconstruction.py: OK")
    except ImportError as e:
        print(f"  IMPORT FAILED: {e}")
        return False
    print()

    all_pass = True

    # ── D1 SH ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 1 — SH FRICATIVE [ʃ]")
    print()
    print("  Voiceless postalveolar.")
    print("  OE 'sc' spelling.")
    print("  Centroid lower than [s].")
    print("  Broader noise band.")
    print()
    sh_seg  = synth_SH(Y_F, 1.0, SR)
    cent_sh = measure_band_centroid(
        sh_seg, 1000.0, 10000.0)
    p1 = check('voicing (must be low)',
               measure_voicing(sh_seg),
               0.0, 0.35)
    p2 = check('RMS level', rms(sh_seg),
               0.005, 0.80)
    p3 = check(
        f'centroid ({cent_sh:.0f} Hz)',
        cent_sh, 2500.0, 5500.0,
        unit=' Hz', fmt='.1f')
    d1 = p1 and p2 and p3
    all_pass &= d1
    print(f"  {'PASSED' if d1 else 'FAILED'}")
    print()

    # ── D2 Y ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 2 — Y VOWEL [y]")
    print()
    y_seg  = synth_Y(Y_F, L_F, 145.0,
                      1.0, SR)
    n_y    = len(y_seg)
    body_y = y_seg[int(0.12*n_y):
                   n_y-int(0.12*n_y)]
    p1 = check('voicing',
               measure_voicing(body_y),
               0.50, 1.0)
    cent_y = measure_band_centroid(
        body_y, 1400.0, 2200.0)
    p2 = check(
        f'F2 centroid ({cent_y:.0f} Hz)',
        cent_y, 1400.0, 2100.0,
        unit=' Hz', fmt='.1f')
    d2 = p1 and p2
    all_pass &= d2
    print(f"  {'PASSED' if d2 else 'FAILED'}")
    print()

    # ── D3 L ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 3 — L LATERAL [l]")
    print()
    l_seg  = synth_L(Y_F, None,
                      145.0, 1.0, SR)
    n_l    = len(l_seg)
    body_l = l_seg[int(0.15*n_l):
                   int(0.85*n_l)]
    p1 = check('voicing',
               measure_voicing(body_l),
               0.45, 1.0)
    p2 = check('RMS level', rms(l_seg),
               0.005, 0.80)
    d3 = p1 and p2
    all_pass &= d3
    print(f"  {'PASSED' if d3 else 'FAILED'}")
    print()

    # ── D4 D ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 4 — D STOP [d]")
    print()
    d_seg = synth_D(L_F, None, 145.0,
                     1.0, SR)
    p1 = check('RMS level', rms(d_seg),
               0.010, 0.90)
    dur_d = len(d_seg) / SR * 1000.0
    p2 = check(
        f'duration ({dur_d:.0f} ms)',
        dur_d, 50.0, 120.0,
        unit=' ms', fmt='.1f')
    d4 = p1 and p2
    all_pass &= d4
    print(f"  {'PASSED' if d4 else 'FAILED'}")
    print()

    # ── D5 SH vs S DISTINCTION ────────────
    print("─" * 60)
    print("DIAGNOSTIC 5 — [ʃ] vs [s]"
          " DISTINCTION")
    print()
    print("  [ʃ] centroid must be lower")
    print("  than [s] centroid.")
    print("  [s] verified ~7609 Hz.")
    print("  [ʃ] target 2500–5500 Hz.")
    print("  Perceptual distinction")
    print("  depends on this separation.")
    print()
    s_ref_hz = 7609.0
    print(f"  [s] reference: {s_ref_hz:.0f} Hz"
          f" (verified WÆS)")
    print(f"  [ʃ] measured:  {cent_sh:.0f} Hz")
    diff = s_ref_hz - cent_sh
    p1 = check(
        f'[ʃ] centroid ({cent_sh:.0f} Hz)',
        cent_sh, 2500.0, 5500.0,
        unit=' Hz', fmt='.1f')
    p2 = check(
        f'separation ({diff:.0f} Hz)',
        diff, 2000.0, 6000.0,
        unit=' Hz', fmt='.1f')
    d5 = p1 and p2
    all_pass &= d5
    print(f"  {'PASSED' if d5 else 'FAILED'}")
    print()

    # ── D6 FULL WORD ──────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 6 — FULL WORD [ʃyld]")
    print()
    w_dry  = synth_scyld(145.0, 1.0, False)
    w_hall = synth_scyld(145.0, 1.0, True)
    dur_ms = len(w_dry) / SR * 1000.0
    p1 = check('RMS level', rms(w_dry),
               0.010, 0.90)
    p2 = check(
        f'duration ({dur_ms:.0f} ms)',
        dur_ms, 200.0, 420.0,
        unit=' ms', fmt='.1f')
    print(f"  {len(w_dry)} samples"
          f" ({dur_ms:.0f} ms)")
    write_wav(
        "output_play/diag_scyld_full.wav",
        w_dry)
    write_wav(
        "output_play/diag_scyld_hall.wav",
        w_hall)
    write_wav(
        "output_play/diag_scyld_slow.wav",
        ola_stretch(w_dry, 4.0))
    write_wav(
        "output_play/diag_scyld_sh.wav",
        ola_stretch(sh_seg / (
            np.max(np.abs(sh_seg))+1e-8)
            * 0.75, 4.0))
    d6 = p1 and p2
    all_pass &= d6
    print(f"  {'PASSED' if d6 else 'FAILED'}")
    print()

    # ── D7 PERCEPTUAL ─────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 7 — PERCEPTUAL")
    print()
    for fn in [
        "diag_scyld_sh.wav",
        "diag_scyld_slow.wav",
        "diag_scyld_hall.wav",
    ]:
        print(f"  afplay output_play/{fn}")
    print()
    print("  LISTEN FOR:")
    print("  SH: lower, broader hiss")
    print("    than [s] — not sharp")
    print("    more 'sh' than 'ss'")
    print("  Full: SH·Y·L·D")
    print("  Four events")
    print("  Sounds like 'shield' —")
    print("  because it means shield.")
    print()

    # ── SUMMARY ───────────────────────────
    print("=" * 60)
    print("SUMMARY")
    print()
    rows = [
        ("D1  SH fricative",    d1),
        ("D2  Y vowel",         d2),
        ("D3  L lateral",       d3),
        ("D4  D stop",          d4),
        ("D5  SH/S distinction",d5),
        ("D6  Full word",       d6),
    ]
    for lbl, ok_ in rows:
        sym = "✓ PASS" if ok_ else "✗ FAIL"
        print(f"  {lbl:22s}  {sym}")
    print(f"  {'D7 Perceptual':22s}  LISTEN")
    print()
    if all_pass:
        print("  ALL NUMERIC CHECKS PASSED")
        print()
        print("  SCYLD [ʃyld] verified.")
        print("  [ʃ] added to inventory.")
        print("  30 phonemes verified.")
        print()
        print("  Next: SCEFING [ʃeviŋɡ]")
        print("  Beowulf line 5, word 2.")
        print("  NEW PHONEME: [v]")
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
