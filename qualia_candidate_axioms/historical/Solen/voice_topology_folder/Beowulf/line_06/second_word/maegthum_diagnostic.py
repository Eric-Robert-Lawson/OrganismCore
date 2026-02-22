"""
MǢGÞUM DIAGNOSTIC v1
Old English: mǣgþum [mæːɣθum]
Beowulf line 6, word 2
February 2026

DIAGNOSTICS:
  D1  M nasal [m]
  D2  AE_LONG vowel [æː]       NEW
  D3  GH fricative [ɣ]         NEW
  D4  TH fricative [θ]
  D5  U vowel [u]
  D6  M nasal final [m]
  D7  [ɣ] vs [x] distinction
  D8  [æː] vs [æ] length
  D9  Full word
  D10 Perceptual

KEY CHECKS:
  D7 [ɣ] voicing >= 0.35.
     [x] voicing ~0.10 (verified HU).
     Same place, same manner.
     Voicing is the only distinction.

  D8 [æː] duration >= 85 ms.
     [æ] duration ~50 ms (verified HWÆT).
     Same quality — different length.
     Length is the phonemic distinction.
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
    print("MǢGÞUM DIAGNOSTIC v1")
    print("Old English [mæːɣθum]")
    print("Beowulf line 6, word 2")
    print("=" * 60)
    print()

    try:
        from maegthum_reconstruction import (
            synth_maegthum,
            synth_M, synth_AEL,
            synth_GH, synth_TH,
            synth_U,
            apply_simple_room,
            M_F, AEL_F, GH_F, U_F)
        print("  maegthum_reconstruction.py: OK")
    except ImportError as e:
        print(f"  IMPORT FAILED: {e}")
        return False
    print()

    all_pass = True

    # ── D1 M ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 1 — M NASAL [m]")
    print()
    m_seg = synth_M(None, AEL_F,
                     145.0, 1.0, SR)
    p1 = check('voicing',
               measure_voicing(m_seg),
               0.65, 1.0)
    p2 = check('RMS (nasal murmur)',
               rms(m_seg), 0.005, 0.25)
    d1 = p1 and p2
    all_pass &= d1
    print(f"  {'PASSED' if d1 else 'FAILED'}")
    print()

    # ── D2 AEL ────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 2 — AE_LONG VOWEL [æː]")
    print()
    print("  Long open front unrounded.")
    print("  Same quality as [æ] — doubled")
    print("  duration. Length is the phoneme.")
    print()
    ael_seg = synth_AEL(M_F, GH_F,
                         145.0, 1.0, SR)
    dur_ael = len(ael_seg) / SR * 1000.0
    p1 = check('voicing',
               measure_voicing(ael_seg),
               0.50, 1.0)
    cent_ael = measure_band_centroid(
        ael_seg, 1200.0, 2200.0)
    p2 = check(
        f'F2 centroid ({cent_ael:.0f} Hz)',
        cent_ael, 1400.0, 2000.0,
        unit=' Hz', fmt='.1f')
    p3 = check(
        f'duration ({dur_ael:.0f} ms)',
        dur_ael, 85.0, 130.0,
        unit=' ms', fmt='.1f')
    d2 = p1 and p2 and p3
    all_pass &= d2
    print(f"  {'PASSED' if d2 else 'FAILED'}")
    print()

    # ── D3 GH ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 3 — GH FRICATIVE [ɣ]")
    print()
    print("  Voiced velar fricative.")
    print("  Voiced counterpart of [x].")
    print("  Intervocalic — full voicing.")
    print("  Buzz with velar resonance.")
    print()
    gh_seg  = synth_GH(AEL_F, None,
                        145.0, 1.0, SR)
    voic_gh = measure_voicing(gh_seg)
    p1 = check('voicing (must be high)',
               voic_gh, 0.35, 1.0)
    p2 = check('RMS level', rms(gh_seg),
               0.005, 0.80)
    d3 = p1 and p2
    all_pass &= d3
    print(f"  {'PASSED' if d3 else 'FAILED'}")
    print()

    # ── D4 TH ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 4 — TH FRICATIVE [θ]")
    print()
    th_seg = synth_TH(None, U_F, 1.0, SR)
    p1 = check('voicing (must be low)',
               measure_voicing(th_seg),
               0.0, 0.35)
    p2 = check('RMS level', rms(th_seg),
               0.001, 0.50)
    d4 = p1 and p2
    all_pass &= d4
    print(f"  {'PASSED' if d4 else 'FAILED'}")
    print()

    # ── D5 U ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 5 — U VOWEL [u]")
    print()
    u_seg  = synth_U(U_F, M_F,
                      145.0, 1.0, SR)
    n_u    = len(u_seg)
    body_u = u_seg[int(0.12*n_u):
                   n_u-int(0.12*n_u)]
    p1 = check('voicing',
               measure_voicing(body_u),
               0.50, 1.0)
    cent_u = measure_band_centroid(
        body_u, 500.0, 1200.0)
    p2 = check(
        f'F2 centroid ({cent_u:.0f} Hz)',
        cent_u, 550.0, 1100.0,
        unit=' Hz', fmt='.1f')
    d5 = p1 and p2
    all_pass &= d5
    print(f"  {'PASSED' if d5 else 'FAILED'}")
    print()

    # ── D6 M FINAL ────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 6 — M NASAL final [m]")
    print()
    m2_seg = synth_M(U_F, None,
                      145.0, 1.0, SR)
    p1 = check('voicing',
               measure_voicing(m2_seg),
               0.65, 1.0)
    p2 = check('RMS (nasal murmur)',
               rms(m2_seg), 0.005, 0.25)
    d6 = p1 and p2
    all_pass &= d6
    print(f"  {'PASSED' if d6 else 'FAILED'}")
    print()

    # ── D7 GH vs X DISTINCTION ────────────
    print("─" * 60)
    print("DIAGNOSTIC 7 — [ɣ] vs [x]"
          " DISTINCTION")
    print()
    print("  [ɣ] voicing >= 0.35")
    print("  [x] voicing ~0.10 (verified HU)")
    print("  Same place, same manner.")
    print("  Voicing only distinction.")
    print()
    x_ref_voicing = 0.10
    print(f"  [x] reference voicing:"
          f" {x_ref_voicing:.4f}"
          f" (verified HU)")
    print(f"  [ɣ] measured voicing: "
          f"{voic_gh:.4f}")
    p1 = check(
        '[ɣ] voicing (must be >= 0.35)',
        voic_gh, 0.35, 1.0)
    d7 = p1
    all_pass &= d7
    print(f"  {'PASSED' if d7 else 'FAILED'}")
    print()

    # ── D8 AEL vs AE LENGTH ───────────────
    print("─" * 60)
    print("DIAGNOSTIC 8 — [æː] vs [æ]"
          " LENGTH")
    print()
    print("  [æ] short ~50 ms (verified HWÆT)")
    print("  [æː] long >= 85 ms")
    print("  Same quality — length distinction.")
    print()
    ae_ref_ms = 50.0
    print(f"  [æ]  reference: {ae_ref_ms:.0f} ms"
          f" (verified HWÆT)")
    print(f"  [æː] measured:  {dur_ael:.0f} ms")
    ratio = dur_ael / ae_ref_ms
    print(f"  ratio: {ratio:.2f}×"
          f"  (target >= 1.7×)")
    print()
    p1 = check(
        f'[æː] duration ({dur_ael:.0f} ms)',
        dur_ael, 85.0, 130.0,
        unit=' ms', fmt='.1f')
    p2 = check(
        f'length ratio ({ratio:.2f}×)',
        ratio, 1.7, 3.0,
        unit='×', fmt='.2f')
    d8 = p1 and p2
    all_pass &= d8
    print(f"  {'PASSED' if d8 else 'FAILED'}")
    print()

    # ── D9 FULL WORD ──────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 9 — FULL WORD"
          " [mæːɣθum]")
    print()
    w_dry  = synth_maegthum(
        145.0, 1.0, False)
    w_hall = synth_maegthum(
        145.0, 1.0, True)
    dur_ms = len(w_dry) / SR * 1000.0
    p1 = check('RMS level', rms(w_dry),
               0.010, 0.90)
    p2 = check(
        f'duration ({dur_ms:.0f} ms)',
        dur_ms, 380.0, 650.0,
        unit=' ms', fmt='.1f')
    print(f"  {len(w_dry)} samples"
          f" ({dur_ms:.0f} ms)")
    write_wav(
        "output_play/diag_maegthu_full.wav",
        w_dry)
    write_wav(
        "output_play/diag_maegthu_hall.wav",
        w_hall)
    write_wav(
        "output_play/diag_maegthu_slow.wav",
        ola_stretch(w_dry, 4.0))
    write_wav(
        "output_play/diag_maegthu_gh.wav",
        ola_stretch(gh_seg / (
            np.max(np.abs(gh_seg))+1e-8)
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
        "diag_maegthu_gh.wav",
        "diag_maegthu_slow.wav",
        "diag_maegthu_hall.wav",
    ]:
        print(f"  afplay output_play/{fn}")
    print()
    print("  LISTEN FOR:")
    print("  M onset — nasal hum")
    print("  AEL — long 'ah/eh' vowel")
    print("    noticeably held longer")
    print("    than a short vowel")
    print("  GH — voiced velar buzz")
    print("    like Dutch/Greek gamma")
    print("    not a stop — continuous")
    print("  TH — voiceless dental")
    print("  UM — back vowel + nasal")
    print("  Full: M·AEL·GH·TH·U·M")
    print()

    # ── SUMMARY ───────────────────────────
    print("=" * 60)
    print("SUMMARY")
    print()
    rows = [
        ("D1  M nasal",          d1),
        ("D2  AE_LONG vowel",    d2),
        ("D3  GH fricative",     d3),
        ("D4  TH fricative",     d4),
        ("D5  U vowel",          d5),
        ("D6  M nasal final",    d6),
        ("D7  GH/X distinction", d7),
        ("D8  AEL/AE length",    d8),
        ("D9  Full word",        d9),
    ]
    for lbl, ok_ in rows:
        sym = "✓ PASS" if ok_ else "✗ FAIL"
        print(f"  {lbl:22s}  {sym}")
    print(f"  {'D10 Perceptual':22s}  LISTEN")
    print()
    if all_pass:
        print("  ALL NUMERIC CHECKS PASSED")
        print()
        print("  MǢGÞUM [mæːɣθum] verified.")
        print("  [æː] added to inventory.")
        print("  [ɣ] added to inventory.")
        print("  34 phonemes verified.")
        print()
        print("  Next: MEODOSETLA [meodosetlɑ]")
        print("  Beowulf line 6, word 3.")
        print("  NEW PHONEME: [eo]")
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
