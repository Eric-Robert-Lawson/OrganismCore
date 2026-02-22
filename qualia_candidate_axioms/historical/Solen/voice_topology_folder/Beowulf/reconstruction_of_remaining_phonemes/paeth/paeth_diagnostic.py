"""
PÆÞ DIAGNOSTIC v1
Old English: pæþ [pæθ]
Inventory completion — word 4 of 4
New phoneme: [p]
February 2026

DIAGNOSTICS:
  D1  P stop [p] — voicelessness
  D2  P stop [p] — burst frequency
  D3  P vs T vs K — place distinction
  D4  AE vowel [æ]
  D5  TH fricative [θ]
  D6  Full word
  D7  Perceptual

KEY CHECKS:
  D1: voicing must be low — no murmur
  D2: burst centroid ~800 Hz
      bilabial is lowest of the stops
  D3: [p] burst ~800 Hz
      [t] burst ~3500 Hz (verified)
      [k] burst ~1800 Hz (verified)
      place encoded in burst frequency
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
    print("PÆÞ DIAGNOSTIC v1")
    print("Old English [pæθ]")
    print("Inventory completion — word 4 of 4")
    print("New phoneme: [p]")
    print("=" * 60)
    print()

    try:
        from paeth_reconstruction import (
            synth_paeth,
            synth_P, synth_AE, synth_TH,
            apply_simple_room,
            AE_F, P_BURST_F)
        print("  paeth_reconstruction.py: OK")
    except ImportError as e:
        print(f"  IMPORT FAILED: {e}")
        return False
    print()

    all_pass = True

    p_seg  = synth_P(None, AE_F, 1.0, SR)

    # ── D1 P VOICELESSNESS ────────────────
    print("─" * 60)
    print("DIAGNOSTIC 1 — P STOP [p]"
          " voicelessness")
    print()
    voic_p = measure_voicing(p_seg)
    p1 = check('voicing (must be low)',
               voic_p, 0.0, 0.35)
    p2 = check('RMS level', rms(p_seg),
               0.005, 0.70)
    d1 = p1 and p2
    all_pass &= d1
    print(f"  {'PASSED' if d1 else 'FAILED'}")
    print()

    # ── D2 P BURST FREQUENCY ──────────────
    print("─" * 60)
    print("DIAGNOSTIC 2 — P BURST FREQUENCY"
          " — bilabial ~800 Hz")
    print()
    burst_cent = measure_band_centroid(
        p_seg, 200.0, 3000.0)
    print(f"  [p] burst centroid: "
          f"{burst_cent:.0f} Hz")
    print(f"  Bilabial target: ~800 Hz")
    print(f"  Alveolar [t] ref: ~3500 Hz")
    print(f"  Velar    [k] ref: ~1800 Hz")
    print()
    p1 = check(
        f'burst centroid ({burst_cent:.0f} Hz)',
        burst_cent, 400.0, 1400.0,
        unit=' Hz', fmt='.1f')
    d2 = p1
    all_pass &= d2
    print(f"  {'PASSED' if d2 else 'FAILED'}")
    print()

    # ── D3 PLACE DISTINCTION ──────────────
    print("─" * 60)
    print("DIAGNOSTIC 3 — STOP PLACE"
          " DISTINCTION")
    print()
    t_burst  = 3500.0
    k_burst  = 1800.0
    print("  Burst centroid by place:")
    print(f"  [p] bilabial: "
          f"{burst_cent:.0f} Hz  ← measured")
    print(f"  [k] velar:    "
          f"{k_burst:.0f} Hz  (reference)")
    print(f"  [t] alveolar: "
          f"{t_burst:.0f} Hz  (reference)")
    print()
    sep_pk = k_burst - burst_cent
    sep_pt = t_burst - burst_cent
    print(f"  [p]→[k] separation: "
          f"{sep_pk:.0f} Hz")
    print(f"  [p]→[t] separation: "
          f"{sep_pt:.0f} Hz")
    print()
    p1 = check(
        f'[p] below [k] ({sep_pk:.0f} Hz gap)',
        sep_pk, 200.0, 2000.0,
        unit=' Hz', fmt='.1f')
    p2 = check(
        f'[p] below [t] ({sep_pt:.0f} Hz gap)',
        sep_pt, 1000.0, 4000.0,
        unit=' Hz', fmt='.1f')
    d3 = p1 and p2
    all_pass &= d3
    print(f"  {'PASSED' if d3 else 'FAILED'}")
    print()

    # ── D4 AE ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 4 — AE VOWEL [æ]")
    print()
    ae_seg = synth_AE(AE_F, None,
                       145.0, 1.0, SR)
    n_ae   = len(ae_seg)
    body_ae= ae_seg[int(0.12*n_ae):
                    n_ae-int(0.12*n_ae)]
    p1 = check('voicing',
               measure_voicing(body_ae),
               0.50, 1.0)
    cent_ae = measure_band_centroid(
        body_ae, 1200.0, 2200.0)
    p2 = check(
        f'F2 centroid ({cent_ae:.0f} Hz)',
        cent_ae, 1400.0, 2000.0,
        unit=' Hz', fmt='.1f')
    d4 = p1 and p2
    all_pass &= d4
    print(f"  {'PASSED' if d4 else 'FAILED'}")
    print()

    # ── D5 TH ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 5 — TH FRICATIVE [θ]")
    print()
    th_seg = synth_TH(AE_F, None, 1.0, SR)
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
    print("DIAGNOSTIC 6 — FULL WORD [pæθ]")
    print()
    w_dry  = synth_paeth(145.0, 1.0, False)
    w_hall = synth_paeth(145.0, 1.0, True)
    dur_ms = len(w_dry) / SR * 1000.0
    p1 = check('RMS level', rms(w_dry),
               0.010, 0.90)
    p2 = check(
        f'duration ({dur_ms:.0f} ms)',
        dur_ms, 150.0, 280.0,
        unit=' ms', fmt='.1f')
    print(f"  {len(w_dry)} samples"
          f" ({dur_ms:.0f} ms)")
    write_wav(
        "output_play/diag_paeth_full.wav",
        w_dry)
    write_wav(
        "output_play/diag_paeth_hall.wav",
        w_hall)
    write_wav(
        "output_play/diag_paeth_slow.wav",
        ola_stretch(w_dry, 4.0))
    write_wav(
        "output_play/diag_paeth_p.wav",
        ola_stretch(p_seg / (
            np.max(np.abs(p_seg))+1e-8)
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
        "diag_paeth_p.wav",
        "diag_paeth_slow.wav",
        "diag_paeth_hall.wav",
    ]:
        print(f"  afplay output_play/{fn}")
    print()
    print("  LISTEN FOR:")
    print("  P  — silent closure")
    print("    then low pop/burst")
    print("    bilabial — lips release")
    print("    lower thud than [t] or [k]")
    print("  AE — open front vowel")
    print("    bright and open")
    print("  TH — voiceless dental close")
    print("  Full: P·AE·TH")
    print("  ModE 'path' — same word.")
    print("  [pæθ] → [pɑːθ] (RP)")
    print("         → [pæθ]  (GA)")
    print("  GA preserved the [æ].")
    print("  RP lengthened and backed it.")
    print()

    # ── SUMMARY ────────────────────��──────
    print("=" * 60)
    print("SUMMARY")
    print()
    rows = [
        ("D1  P voicelessness",     d1),
        ("D2  P burst frequency",   d2),
        ("D3  Stop place distinc.", d3),
        ("D4  AE vowel",            d4),
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
        print("  PÆÞ [pæθ] verified.")
        print("  [p] added to inventory.")
        print("  39 phonemes verified.")
        print()
        print("  Inventory completion series:")
        print("  [iː]  ✓ DONE — WĪF")
        print("  [eːɑ] ✓ DONE — ĒAGE")
        print("  [eːo] ✓ DONE — ÞĒOD")
        print("  [p]   ✓ DONE — PÆÞ")
        print()
        print("  One gap remaining:")
        print("  [b] — line 8 GEBĀD")
        print()
        print("  39 of 40 phonemes verified.")
        print("  Return to line 8.")
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
