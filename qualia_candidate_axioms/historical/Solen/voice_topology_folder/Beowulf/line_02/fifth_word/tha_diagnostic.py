"""
ÐĀ DIAGNOSTIC v1
Old English: ðā [ðɑː]
Beowulf line 3, word 2
February 2026

DIAGNOSTICS:
  D1  Ð fricative [ð]
  D2  Ā long vowel [ɑː]
  D3  Full word
  D4  Perceptual

VOICING FLOORS (established framework):
  Long vowel (>80 ms):              0.65
  Short vowel internal (≤80 ms):    0.50
  Short vowel word-final (≤80 ms):  0.45

[ð] VOICING CHECK:
  [ð] is a voiced fricative.
  Voicing score target: > 0.40
  Lower than a vowel — frication noise
  competes with the periodic voicing
  and reduces autocorrelation peak.
  But clearly above the voiceless
  threshold of 0.35 used for [θ], [f], [x].
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

def safe_bp(lo, hi, sr=SR):
    nyq = sr / 2.0
    lo_ = max(lo / nyq, 0.001)
    hi_ = min(hi / nyq, 0.499)
    if lo_ >= hi_:
        lo_ = max(lo_ - 0.01, 0.001)
        hi_ = min(lo_ + 0.02, 0.499)
    b, a = butter(2, [lo_, hi_], btype='band')
    return b, a

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

def measure_band_centroid(seg, lo_hz, hi_hz,
                           sr=SR):
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
    print("ÐĀ DIAGNOSTIC v1")
    print("Old English [ðɑː]")
    print("Beowulf line 3, word 2")
    print("=" * 60)
    print()

    try:
        from tha_reconstruction import (
            synth_tha, synth_DH,
            synth_AA_long,
            apply_simple_room,
            AA_F)
        print("  tha_reconstruction.py: OK")
    except ImportError as e:
        print(f"  IMPORT FAILED: {e}")
        return False
    print()

    all_pass = True

    # ── D1 DH ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 1 — Ð FRICATIVE [ð]")
    print()
    print("  Voiced dental fricative.")
    print("  'th' in 'the', 'this', 'that'.")
    print("  Voiced — voicing score > 0.40.")
    print("  Centroid lower than [θ] because")
    print("  voicing pulls energy downward.")
    print()
    print("  [θ] vs [ð] distinction:")
    print("  [θ] voicing: < 0.35  (voiceless)")
    print("  [ð] voicing: > 0.40  (voiced)")
    print()
    dh_seg  = synth_DH(AA_F, 145.0, 1.0, SR)
    cent_dh = measure_band_centroid(
        dh_seg, 400.0, 8000.0)
    v_dh    = measure_voicing(dh_seg)
    p1 = check('voicing (must be > 0.40)',
               v_dh, 0.40, 1.0)
    p2 = check('RMS level', rms(dh_seg),
               0.005, 0.80)
    p3 = check(
        f'frication centroid ({cent_dh:.0f} Hz)',
        cent_dh, 800.0, 4000.0,
        unit=' Hz', fmt='.1f')
    print()
    print(f"  [θ] centroid for reference:"
          f" ~4200 Hz")
    print(f"  [ð] centroid measured:"
          f" {cent_dh:.0f} Hz")
    if cent_dh < 4200:
        print(f"  Centroid pulled lower by"
              f" voicing — correct.")
    d1 = p1 and p2 and p3
    all_pass &= d1
    write_wav("output_play/diag_tha_dh.wav",
              ola_stretch(dh_seg / (
                  np.max(np.abs(dh_seg))+1e-8)
                  * 0.75, 4.0))
    print(f"  {'PASSED' if d1 else 'FAILED'}")
    print()

    # ── D2 AA ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 2 — Ā LONG VOWEL [ɑː]")
    print()
    print("  Long open back.")
    print("  Same parameters as GĀR-DENA.")
    print("  Duration target: 120–200 ms.")
    print("  Word-final — longer decay.")
    print()
    aa_seg  = synth_AA_long(AA_F, None,
                             145.0, 1.0)
    dur_aa  = len(aa_seg) / SR * 1000.0
    n_aa    = len(aa_seg)
    body_aa = aa_seg[int(0.10*n_aa):
                     int(0.55*n_aa)]
    cent_aa = measure_band_centroid(
        body_aa, 600.0, 1400.0)
    p1 = check('voicing',
               measure_voicing(body_aa),
               0.65, 1.0)
    p2 = check(
        f'duration ({dur_aa:.0f} ms)',
        dur_aa, 120.0, 200.0,
        unit=' ms', fmt='.1f')
    p3 = check(
        f'F1+F2 centroid ({cent_aa:.0f} Hz)',
        cent_aa, 750.0, 1050.0,
        unit=' Hz', fmt='.1f')
    d2 = p1 and p2 and p3
    all_pass &= d2
    write_wav("output_play/diag_tha_aa.wav",
              ola_stretch(aa_seg / (
                  np.max(np.abs(aa_seg))+1e-8)
                  * 0.75, 4.0))
    print(f"  {'PASSED' if d2 else 'FAILED'}")
    print()

    # ── D3 FULL WORD ──────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 3 — FULL WORD [ðɑː]")
    print()
    tha_dry  = synth_tha(145.0, 1.0, False)
    tha_hall = synth_tha(145.0, 1.0, True)
    dur_ms   = len(tha_dry) / SR * 1000.0
    p1 = check('RMS level', rms(tha_dry),
               0.010, 0.90)
    p2 = check(
        f'duration ({dur_ms:.0f} ms)',
        dur_ms, 150.0, 400.0,
        unit=' ms', fmt='.1f')
    print(f"  {len(tha_dry)} samples"
          f" ({dur_ms:.0f} ms)")
    write_wav(
        "output_play/diag_tha_full.wav",
        tha_dry)
    write_wav(
        "output_play/diag_tha_hall.wav",
        tha_hall)
    write_wav(
        "output_play/diag_tha_slow.wav",
        ola_stretch(tha_dry, 4.0))
    d3 = p1 and p2
    all_pass &= d3
    print(f"  {'PASSED' if d3 else 'FAILED'}")
    print()

    # ── D4 PERCEPTUAL ─────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 4 — PERCEPTUAL")
    print()
    for fn in [
        "diag_tha_dh.wav",
        "diag_tha_aa.wav",
        "diag_tha_slow.wav",
        "diag_tha_hall.wav",
    ]:
        print(f"  afplay output_play/{fn}")
    print()
    print("  LISTEN FOR:")
    print("  Ð: buzzy 'th' — like 'the'")
    print("    voiced hiss, not clean noise")
    print("  Ā: long open 'ah' — held")
    print("  Full: Ð·Ā — two events")
    print("  The Ð should sound clearly")
    print("  different from Þ in ÞRYM —")
    print("  buzzier, lower, voiced")
    print()

    # ── SUMMARY ───────────────────────────
    print("=" * 60)
    print("SUMMARY")
    print()
    rows = [
        ("D1 Ð fricative",  d1),
        ("D2 Ā long vowel", d2),
        ("D3 Full word",    d3),
    ]
    for lbl, ok_ in rows:
        sym = "✓ PASS" if ok_ else "✗ FAIL"
        print(f"  {lbl:22s}  {sym}")
    print(f"  {'D4 Perceptual':22s}  LISTEN")
    print()
    if all_pass:
        print("  ALL NUMERIC CHECKS PASSED")
        print()
        print("  ÐĀ [ðɑː] verified.")
        print("  Next: ÆÞELINGAS [æθeliŋɡɑs]")
        print("  Beowulf line 3, word 3.")
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
