"""
ÞÆS DIAGNOSTIC v1
Old English: þæs [θæs]
Beowulf line 8, word 4 (overall word 34)
No new phonemes — pure assembly
February 2026

DIAGNOSTICS:
  D1   TH dental fricative [θ]
       voicing must be low — voiceless
       centroid 2500–6000 Hz — dental
  D2   AE vowel [æ]
       voicing >= 0.50
       F2 centroid 1400–2000 Hz
  D3   S alveolar fricative [s]
       voicing must be low — voiceless
       centroid > 5000 Hz — alveolar
  D4   FRICATION CONTRAST
       [s] centroid >> [θ] centroid
       separation >= 1500 Hz
       alveolar clearly above dental
  D5   Full word
       RMS, duration
  D6   Perceptual

KEY CHECKS:
  [θ] voicing <= 0.35 — voiceless onset
  [θ] centroid 2500–6000 Hz — dental place
  [æ] voicing >= 0.50 — voiced nucleus
  [æ] F2 ~1684 Hz — front open vowel
  [s] voicing <= 0.35 — voiceless coda
  [s] centroid > 5000 Hz — alveolar place
  [s] centroid >> [θ] centroid — place distinct
  Word duration ~195 ms at dil=1.0
  (70 ms [θ] + 60 ms [æ] + 65 ms [s])
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
    n_frames = max(1, (n_in - win_n) // hop_in + 1)
    n_out    = hop_out * n_frames + win_n
    out      = np.zeros(n_out, dtype=DTYPE)
    norm     = np.zeros(n_out, dtype=DTYPE)
    for i in range(n_frames):
        in_pos  = i * hop_in
        out_pos = i * hop_out
        if in_pos + win_n > n_in:
            break
        frame = sig[in_pos:in_pos+win_n] * window
        out [out_pos:out_pos+win_n] += frame
        norm[out_pos:out_pos+win_n] += window
    nz       = norm > 1e-8
    out[nz] /= norm[nz]
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
    acorr  = np.correlate(core, core, mode='full')
    acorr  = acorr[len(acorr)//2:]
    acorr /= (acorr[0] + 1e-12)
    lo = int(sr / 400)
    hi = min(int(sr / 80), len(acorr) - 1)
    if lo >= hi:
        return 0.0
    return float(np.clip(np.max(acorr[lo:hi]),
                          0.0, 1.0))

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
    print("ÞÆS DIAGNOSTIC v1")
    print("Old English [θæs]")
    print("Beowulf line 8, word 4")
    print("Pure assembly — no new phonemes")
    print("=" * 60)
    print()

    try:
        from thaes_reconstruction import (
            synth_þæs,
            synth_TH,
            synth_AE,
            synth_S,
            apply_simple_room,
            AE_F,
            PITCH_PERF, DIL_PERF)
        print("  þæs_reconstruction.py: OK")
    except ImportError as e:
        print(f"  IMPORT FAILED: {e}")
        return False
    print()

    all_pass = True

    # ── D1 TH ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 1 — TH DENTAL"
          " FRICATIVE [θ]")
    print("  Voiceless dental.")
    print("  Broad diffuse noise.")
    print("  Centroid 2500–6000 Hz.")
    print()
    th_seg  = synth_TH(F_next=AE_F,
                        dil=1.0, sr=SR)
    v_th    = measure_voicing(th_seg)
    c_th    = measure_band_centroid(
        th_seg, 1000.0, 10000.0)
    dur_th  = len(th_seg) / SR * 1000.0
    print(f"  Duration:  {dur_th:.0f} ms")
    print(f"  Centroid:  {c_th:.0f} Hz")
    print()
    p1 = check('voicing (must be low)',
               v_th, 0.0, 0.35)
    p2 = check(
        f'centroid ({c_th:.0f} Hz)',
        c_th, 2500.0, 6000.0,
        unit=' Hz', fmt='.1f')
    d1 = p1 and p2
    all_pass &= d1
    print(f"  {'PASSED' if d1 else 'FAILED'}")
    print()

    # ── D2 AE ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 2 — AE VOWEL [æ]")
    print("  Open front unrounded.")
    print("  High F1 — wide jaw opening.")
    print("  F2 ~1684 Hz — front position.")
    print()
    ae_seg  = synth_AE(
        F_prev=None, F_next=None,
        pitch_hz=145.0, dil=1.0, sr=SR)
    v_ae    = measure_voicing(ae_seg)
    f2_ae   = measure_band_centroid(
        ae_seg, 1200.0, 2200.0)
    dur_ae  = len(ae_seg) / SR * 1000.0
    print(f"  Duration:    {dur_ae:.0f} ms")
    print(f"  F2 centroid: {f2_ae:.0f} Hz"
          f"  (target 1400–2000 Hz)")
    print()
    p1 = check('voicing',
               v_ae, 0.50, 1.0)
    p2 = check(
        f'F2 centroid ({f2_ae:.0f} Hz)',
        f2_ae, 1400.0, 2000.0,
        unit=' Hz', fmt='.1f')
    d2 = p1 and p2
    all_pass &= d2
    print(f"  {'PASSED' if d2 else 'FAILED'}")
    print()

    # ── D3 S ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 3 — S ALVEOLAR"
          " FRICATIVE [s]")
    print("  Voiceless alveolar.")
    print("  Highest centroid in inventory.")
    print("  Target: > 5000 Hz.")
    print()
    s_seg   = synth_S(F_prev=AE_F,
                       dil=1.0, sr=SR)
    v_s     = measure_voicing(s_seg)
    c_s     = measure_band_centroid(
        s_seg, 3000.0, 20000.0)
    dur_s   = len(s_seg) / SR * 1000.0
    print(f"  Duration:  {dur_s:.0f} ms")
    print(f"  Centroid:  {c_s:.0f} Hz")
    print()
    p1 = check('voicing (must be low)',
               v_s, 0.0, 0.35)
    p2 = check(
        f'centroid ({c_s:.0f} Hz)',
        c_s, 5000.0, 20000.0,
        unit=' Hz', fmt='.1f')
    d3 = p1 and p2
    all_pass &= d3
    print(f"  {'PASSED' if d3 else 'FAILED'}")
    print()

    # ── D4 FRICATION CONTRAST ─────────────
    print("─" * 60)
    print("DIAGNOSTIC 4 — FRICATION CONTRAST")
    print("  [s] centroid >> [θ] centroid")
    print("  Alveolar clearly above dental.")
    print("  Separation >= 1500 Hz.")
    print()
    sep = c_s - c_th
    print(f"  [θ] centroid: {c_th:.0f} Hz"
          f"  (dental)")
    print(f"  [s] centroid: {c_s:.0f} Hz"
          f"  (alveolar)")
    print(f"  Separation:   {sep:.0f} Hz")
    print()
    p1 = check(
        f'[s]>[θ] separation ({sep:.0f} Hz)',
        sep, 1500.0, 20000.0,
        unit=' Hz', fmt='.1f')
    d4 = p1
    all_pass &= d4
    print(f"  {'PASSED' if d4 else 'FAILED'}")
    print()

    # ── D5 FULL WORD ──────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 5 — FULL WORD [θæs]")
    print()
    w_dry  = synth_þæs(145.0, 1.0, False)
    w_hall = synth_þæs(145.0, 1.0, True)
    w_perf = synth_þæs(PITCH_PERF,
                        DIL_PERF, True)
    dur_ms      = len(w_dry)  / SR * 1000.0
    dur_perf_ms = len(w_perf) / SR * 1000.0
    print(f"  {len(w_dry)} samples"
          f" ({dur_ms:.0f} ms) — diagnostic")
    print(f"  {len(w_perf)} samples"
          f" ({dur_perf_ms:.0f} ms)"
          f" — performance")
    print()
    p1 = check('RMS level', rms(w_dry),
               0.010, 0.90)
    p2 = check(
        f'duration ({dur_ms:.0f} ms)',
        dur_ms, 160.0, 240.0,
        unit=' ms', fmt='.1f')
    d5 = p1 and p2
    all_pass &= d5
    write_wav("output_play/diag_þæs_full.wav",
               w_dry)
    write_wav("output_play/diag_þæs_hall.wav",
               w_hall)
    write_wav("output_play/diag_þæs_slow.wav",
               ola_stretch(w_dry, 4.0))
    write_wav("output_play/diag_þæs_perf.wav",
               w_perf)
    print(f"  {'PASSED' if d5 else 'FAILED'}")
    print()

    # ── D6 PERCEPTUAL ─────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 6 — PERCEPTUAL")
    print()
    print("  Diagnostic versions:")
    for fn in [
        "diag_þæs_full.wav",
        "diag_þæs_slow.wav",
        "diag_þæs_hall.wav",
    ]:
        print(f"  afplay output_play/{fn}")
    print()
    print("  Performance version:")
    print("  afplay output_play/"
          "diag_þæs_perf.wav")
    print()
    print("  LISTEN FOR:")
    print("  TH  — voiceless dental onset")
    print("        diffuse, soft noise")
    print("        lower than [s]")
    print("        tongue tip at teeth")
    print("  AE  — open front vowel")
    print("        wide jaw opening")
    print("        the voiced island")
    print("        between two fricatives")
    print("  S   — voiceless alveolar coda")
    print("        sharp, bright noise")
    print("        clearly higher than [θ]")
    print("        the word closes hard")
    print()
    print("  FRICATION CONTRAST:")
    print("  [θ] → [æ] → [s]")
    print("  soft → voiced → sharp")
    print("  dental → open → alveolar")
    print()
    print("  CONTEXT:")
    print("  hē ÞÆS frōfre gebād")
    print("  he OF-THAT comfort waited")
    print("  The genitive of anticipation.")
    print()

    # ── SUMMARY ───────────────────────────
    print("=" * 60)
    print("SUMMARY")
    print()
    rows = [
        ("D1   TH dental fricative",    d1),
        ("D2   AE vowel",               d2),
        ("D3   S alveolar fricative",   d3),
        ("D4   Frication contrast",     d4),
        ("D5   Full word",              d5),
    ]
    for lbl, ok_ in rows:
        sym = "✓ PASS" if ok_ else "✗ FAIL"
        print(f"  {lbl:30s}  {sym}")
    print(f"  {'D6   Perceptual':30s}  LISTEN")
    print()
    if all_pass:
        print("  ALL NUMERIC CHECKS PASSED")
        print()
        print("  ÞÆS [θæs] verified.")
        print("  Pure assembly — [θ], [æ], [s]")
        print("  from verified inventory.")
        print()
        print("  Line 8 status:")
        print("  feasceaft  ✓")
        print("  funden     ✓")
        print("  hē         ✓")
        print("  þæs        ✓")
        print("  frōfre     — next")
        print("  gebād      — [b] phoneme 41")
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
