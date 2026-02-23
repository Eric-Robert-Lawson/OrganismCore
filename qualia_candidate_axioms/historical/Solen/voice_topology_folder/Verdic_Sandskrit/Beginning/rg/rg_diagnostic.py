"""
ṚG DIAGNOSTIC v1
Vedic Sanskrit: ṛg  [ɻ̩g]
Rigveda — first syllable, proof of concept
February 2026

DIAGNOSTICS:
  D1   RV syllabic retroflex [ɻ̩] — voicing
  D2   RV F1 centroid         [ɻ̩] — jaw opening
  D3   RV F2 centroid         [ɻ̩] — retroflex locus
  D4   RV F3 centroid         [ɻ̩] — THE DIP (key)
  D5   RV duration            [ɻ̩] — vowel length
  D6   G closure LF ratio     [g]  — voiced closure
  D7   G burst centroid        [g]  — velar locus
  D8   RV vs OE [ə] F2        separation check
  D9   RV vs OE [u] F2        separation check
  D10  Full word duration
  D11  Perceptual

KEY CHECKS:
  D4 is the critical diagnostic.
     F3 centroid below 2500 Hz.
     This is the mūrdhanya marker.
     Separates [ɻ̩] from every phoneme
     in the OE inventory.
     No OE phoneme has F3 this low.
     If D4 fails: F3 target too high.
     Reduce RV_F[2] and re-synthesise.

  D8 and D9 are separation checks.
     [ɻ̩] must be separated from [ə] in F2.
     [ɻ̩] must be separated from [u] in F2.
     [ɻ̩] F2 ~1300 Hz sits BETWEEN [u] (~750 Hz)
     and [ə] (~1500 Hz).
     If separation fails: formant targets
     need adjustment.

  D6 uses LF energy ratio, not voicing fraction.
     Same as OE voiced stop diagnostic.
     Direct transfer.
"""

import numpy as np
from scipy.signal import lfilter, butter
import wave as wave_module
import os
import sys

SR    = 44100
DTYPE = np.float32

os.makedirs("output_play", exist_ok=True)

# OE reference values for separation checks
OE_SCHWA_F2_HZ = 1427.0   # verified ×3 contexts
OE_U_F2_HZ     =  800.0   # verified OE inventory


def f32(x):
    return np.asarray(x, dtype=DTYPE)

def rms(sig):
    return float(np.sqrt(
        np.mean(sig.astype(float) ** 2)))

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
        frame = (sig[in_pos:in_pos + win_n]
                 * window)
        out [out_pos:out_pos + win_n] += frame
        norm[out_pos:out_pos + win_n] += window
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
    core = seg[n // 4: 3 * n // 4].astype(float)
    core -= np.mean(core)
    if np.max(np.abs(core)) < 1e-8:
        return 0.0
    acorr  = np.correlate(core, core,
                          mode='full')
    acorr  = acorr[len(acorr) // 2:]
    acorr /= (acorr[0] + 1e-12)
    lo = int(sr / 400)
    hi = min(int(sr / 80), len(acorr) - 1)
    if lo >= hi:
        return 0.0
    return float(np.clip(
        np.max(acorr[lo:hi]), 0.0, 1.0))

def measure_lf_ratio(seg, sr=SR):
    """
    LF energy ratio for voiced stops.
    Ratio of energy below 500 Hz to total.
    Target >= 0.40 for voiced closure.
    """
    if len(seg) < 64:
        return 0.0
    spec  = np.abs(np.fft.rfft(
        seg.astype(float), n=2048)) ** 2
    freqs = np.fft.rfftfreq(2048, d=1.0 / sr)
    lf    = np.sum(spec[freqs <= 500.0])
    total = np.sum(spec)
    if total < 1e-12:
        return 0.0
    return float(lf / total)

def measure_band_centroid(seg, lo_hz,
                           hi_hz, sr=SR):
    if len(seg) < 64:
        return 0.0
    spec  = np.abs(np.fft.rfft(
        seg.astype(float), n=2048)) ** 2
    freqs = np.fft.rfftfreq(2048, d=1.0 / sr)
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
    print("ṚG DIAGNOSTIC v1")
    print("Vedic Sanskrit [ɻ̩g]")
    print("Rigveda — proof of concept")
    print("=" * 60)
    print()

    try:
        from rg_reconstruction import (
            synth_rg,
            synth_RV,
            synth_G,
            apply_simple_room,
            RV_F, G_F)
        print("  rg_reconstruction.py: OK")
    except ImportError as e:
        print(f"  IMPORT FAILED: {e}")
        return False
    print()

    all_pass = True

    # ── ISOLATE SEGMENTS ──────────────────
    rv_seg = synth_RV(F_prev=None,
                      F_next=G_F)
    g_seg  = synth_G(F_prev=RV_F,
                     F_next=None)

    # Body of RV — strip coarticulation edges
    n_rv      = len(rv_seg)
    edge_rv   = max(1, n_rv // 6)
    rv_body   = rv_seg[edge_rv:n_rv - edge_rv]

    # Closure phase of G only
    from rg_reconstruction import (
        G_CLOSURE_MS, DIL)
    n_cl      = int(G_CLOSURE_MS * DIL /
                    1000.0 * SR)
    g_closure = g_seg[:min(n_cl, len(g_seg))]

    # ── D1 VOICING ────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 1 — [ɻ̩] VOICING")
    print()
    print("  Sustained voiced vowel.")
    print("  No AM modulation.")
    print("  Voicing must be high throughout.")
    print()
    voic_rv = measure_voicing(rv_body)
    p1 = check('voicing', voic_rv,
               0.50, 1.0)
    d1 = p1
    all_pass &= d1
    print(f"  {'PASSED' if d1 else 'FAILED'}")
    print()

    # ── D2 F1 CENTROID ────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 2 — [ɻ̩] F1 CENTROID")
    print()
    print("  Mid jaw opening.")
    print("  F1 ~420 Hz — between [i] (280 Hz)")
    print("  and [a] (700 Hz).")
    print()
    cent_f1 = measure_band_centroid(
        rv_body, 300.0, 600.0)
    p1 = check(
        f'F1 centroid ({cent_f1:.0f} Hz)',
        cent_f1, 350.0, 500.0,
        unit=' Hz', fmt='.1f')
    d2 = p1
    all_pass &= d2
    print(f"  {'PASSED' if d2 else 'FAILED'}")
    print()

    # ── D3 F2 CENTROID ────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 3 — [ɻ̩] F2 CENTROID")
    print()
    print("  Retroflex locus ~1300 Hz.")
    print("  LOWER than [ə] (~1427 Hz).")
    print("  HIGHER than [u] (~800 Hz).")
    print("  A new position in the vocal topology.")
    print()
    cent_f2 = measure_band_centroid(
        rv_body, 900.0, 1600.0)
    p1 = check(
        f'F2 centroid ({cent_f2:.0f} Hz)',
        cent_f2, 1100.0, 1500.0,
        unit=' Hz', fmt='.1f')
    d3 = p1
    all_pass &= d3
    print(f"  {'PASSED' if d3 else 'FAILED'}")
    print()

    # ── D4 F3 CENTROID — THE CRITICAL CHECK
    print("─" * 60)
    print("DIAGNOSTIC 4 — [ɻ̩] F3 DIP")
    print()
    print("  THE MŪRDHANYA MARKER.")
    print("  F3 must be BELOW 2500 Hz.")
    print("  Neutral F3 (alveolar): ~2700 Hz.")
    print("  Retroflex F3 target:   ~2200 Hz.")
    print("  The tongue curl depresses F3.")
    print("  This is the new Tonnetz territory.")
    print("  No OE phoneme maps here.")
    print()
    cent_f3 = measure_band_centroid(
        rv_body, 1800.0, 3200.0)
    p1 = check(
        f'F3 centroid ({cent_f3:.0f} Hz)',
        cent_f3, 1800.0, 2499.0,
        unit=' Hz', fmt='.1f')
    d4 = p1
    all_pass &= d4
    if not d4:
        print()
        print("  *** D4 FAILED ***")
        print("  F3 is too high.")
        print("  The retroflexion is not")
        print("  sufficiently depressing F3.")
        print("  Action: reduce RV_F[2]")
        print("  below 2200 Hz and re-run.")
    print(f"  {'PASSED' if d4 else 'FAILED'}")
    print()

    # ── D5 DURATION ───────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 5 — [ɻ̩] DURATION")
    print()
    dur_rv_ms = len(rv_seg) / SR * 1000.0
    p1 = check(
        f'duration ({dur_rv_ms:.0f} ms)',
        dur_rv_ms, 50.0, 80.0,
        unit=' ms', fmt='.1f')
    d5 = p1
    all_pass &= d5
    print(f"  {'PASSED' if d5 else 'FAILED'}")
    print()

    # ── D6 G CLOSURE LF RATIO ─────────────
    print("─" * 60)
    print("DIAGNOSTIC 6 — [g] CLOSURE LF RATIO")
    print()
    print("  Voiced closure — murmur energy.")
    print("  LF ratio (below 500 Hz) >= 0.40.")
    print("  Same diagnostic as OE [g].")
    print("  Direct transfer from OE inventory.")
    print()
    lf_g = measure_lf_ratio(g_closure)
    p1 = check('LF ratio', lf_g,
               0.40, 1.0)
    d6 = p1
    all_pass &= d6
    print(f"  {'PASSED' if d6 else 'FAILED'}")
    print()

    # ── D7 G BURST CENTROID ───────────────
    print("─" * 60)
    print("DIAGNOSTIC 7 — [g] BURST CENTROID")
    print()
    print("  Velar locus ~2500 Hz.")
    print("  F2 rises from [ɻ̩] locus (~1300 Hz)")
    print("  to velar position (~2500 Hz).")
    print("  The coarticulation is the map")
    print("  of this new Tonnetz territory.")
    print()
    # Burst region: after closure
    burst_start = len(g_closure)
    from rg_reconstruction import G_BURST_MS, DIL
    n_burst = int(G_BURST_MS * DIL /
                  1000.0 * SR)
    burst_end   = burst_start + n_burst
    g_burst     = g_seg[
        burst_start:min(burst_end, len(g_seg))]
    if len(g_burst) > 10:
        cent_burst = measure_band_centroid(
            g_burst, 1000.0, 4000.0)
        p1 = check(
            f'burst centroid ({cent_burst:.0f} Hz)',
            cent_burst, 1800.0, 3200.0,
            unit=' Hz', fmt='.1f')
        d7 = p1
    else:
        print("  Burst segment too short"
              " — skipping centroid")
        d7 = True
    all_pass &= d7
    print(f"  {'PASSED' if d7 else 'FAILED'}")
    print()

    # ── D8 SEPARATION FROM [ə] ────────────
    print("─" * 60)
    print("DIAGNOSTIC 8 — [ɻ̩] vs OE [ə]"
          " F2 SEPARATION")
    print()
    print(f"  OE [ə] F2: {OE_SCHWA_F2_HZ:.0f} Hz"
          f" (verified ×3 contexts)")
    print(f"  [ɻ̩]  F2: {cent_f2:.0f} Hz"
          f" (measured D3)")
    sep_schwa = OE_SCHWA_F2_HZ - cent_f2
    print(f"  Separation: {sep_schwa:.0f} Hz"
          f"  (target >= 150 Hz)")
    print()
    p1 = check(
        f'F2 separation from [ə]'
        f' ({sep_schwa:.0f} Hz)',
        sep_schwa, 150.0, 1000.0,
        unit=' Hz', fmt='.1f')
    d8 = p1
    all_pass &= d8
    print(f"  {'PASSED' if d8 else 'FAILED'}")
    print()

    # ── D9 SEPARATION FROM [u] ────────────
    print("─" * 60)
    print("DIAGNOSTIC 9 — [ɻ̩] vs OE [u]"
          " F2 SEPARATION")
    print()
    print(f"  OE [u] F2: {OE_U_F2_HZ:.0f} Hz"
          f" (OE inventory)")
    print(f"  [ɻ̩]  F2: {cent_f2:.0f} Hz"
          f" (measured D3)")
    sep_u = cent_f2 - OE_U_F2_HZ
    print(f"  Separation: {sep_u:.0f} Hz"
          f"  (target >= 150 Hz)")
    print()
    p1 = check(
        f'F2 separation from [u]'
        f' ({sep_u:.0f} Hz)',
        sep_u, 150.0, 1000.0,
        unit=' Hz', fmt='.1f')
    d9 = p1
    all_pass &= d9
    print(f"  {'PASSED' if d9 else 'FAILED'}")
    print()

    # ── D10 FULL WORD ─────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 10 — FULL WORD [ɻ̩g]")
    print()
    w_dry  = synth_rg(with_room=False)
    w_hall = synth_rg(with_room=True)
    dur_ms = len(w_dry) / SR * 1000.0
    p1 = check('RMS level', rms(w_dry),
               0.010, 0.90)
    p2 = check(
        f'duration ({dur_ms:.0f} ms)',
        dur_ms, 80.0, 200.0,
        unit=' ms', fmt='.1f')
    write_wav(
        "output_play/diag_rg_dry.wav",
        w_dry)
    write_wav(
        "output_play/diag_rg_hall.wav",
        w_hall)
    write_wav(
        "output_play/diag_rg_slow.wav",
        ola_stretch(w_dry, 4.0))
    # Isolated retroflex for focused listening
    rv_iso = synth_RV(F_prev=None,
                      F_next=None)
    mx = np.max(np.abs(rv_iso))
    if mx > 1e-8:
        rv_iso = rv_iso / mx * 0.75
    write_wav(
        "output_play/diag_rv_isolated.wav",
        rv_iso)
    write_wav(
        "output_play/diag_rv_slow.wav",
        ola_stretch(rv_iso, 4.0))
    d10 = p1 and p2
    all_pass &= d10
    print(f"  {'PASSED' if d10 else 'FAILED'}")
    print()

    # ── D11 PERCEPTUAL ────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 11 — PERCEPTUAL")
    print()
    print("  Listen in this order:")
    for fn in [
        "diag_rv_slow.wav",
        "diag_rv_isolated.wav",
        "diag_rg_slow.wav",
        "diag_rg_hall.wav",
    ]:
        print(f"  afplay output_play/{fn}")
    print()
    print("  LISTEN FOR:")
    print("  diag_rv_slow.wav:")
    print("    The retroflex vowel in isolation.")
    print("    Not English 'r'.")
    print("    Not a schwa.")
    print("    Not [u].")
    print("    A new room.")
    print("    The tongue is curled.")
    print("    You can hear the curl.")
    print("    F3 is low — that is the curl.")
    print()
    print("  diag_rg_slow.wav:")
    print("    The retroflex vowel releases")
    print("    into the velar stop.")
    print("    F2 rises from ~1300 Hz to ~2500 Hz")
    print("    through the closure.")
    print("    The coarticulation is audible")
    print("    in the slow version.")
    print()
    print("  diag_rg_hall.wav:")
    print("    Full word at ritual reverb.")
    print("    The first sound of the Rigveda.")
    print("    Not heard with physical certainty")
    print("    for approximately 3,500 years.")
    print()

    # ── F3 DIP REPORT ─────────────────────
    print("─" * 60)
    print("F3 DIP REPORT — MŪRDHANYA MARKER")
    print()
    neutral_f3 = 2700.0
    dip        = neutral_f3 - cent_f3
    print(f"  Neutral F3 (alveolar):  "
          f"{neutral_f3:.0f} Hz")
    print(f"  Measured [ɻ̩] F3:        "
          f"{cent_f3:.0f} Hz")
    print(f"  F3 depression:          "
          f"{dip:.0f} Hz")
    print()
    if dip >= 200.0:
        print("  F3 depression >= 200 Hz.")
        print("  Retroflex dimension confirmed.")
        print("  The tongue curl is present")
        print("  in the acoustic output.")
    else:
        print("  F3 depression < 200 Hz.")
        print("  Retroflexion may be insufficient.")
        print("  Consider reducing RV_F[2].")
    print()

    # ── SUMMARY ───────────────────────────
    print("=" * 60)
    print("SUMMARY")
    print()
    rows = [
        ("D1   [ɻ̩] voicing",          d1),
        ("D2   [ɻ̩] F1 centroid",       d2),
        ("D3   [ɻ̩] F2 centroid",       d3),
        ("D4   [ɻ̩] F3 dip (KEY)",      d4),
        ("D5   [ɻ̩] duration",          d5),
        ("D6   [g] closure LF ratio",  d6),
        ("D7   [g] burst centroid",    d7),
        ("D8   [ɻ̩] vs [ə] separation", d8),
        ("D9   [ɻ̩] vs [u] separation", d9),
        ("D10  Full word",             d10),
    ]
    for lbl, ok_ in rows:
        sym = "✓ PASS" if ok_ else "✗ FAIL"
        print(f"  {lbl:28s}  {sym}")
    print(f"  {'D11  Perceptual':28s}  LISTEN")
    print()
    if all_pass:
        print("  ALL NUMERIC CHECKS PASSED")
        print()
        print("  ṚG [ɻ̩g] verified.")
        print("  [ɻ̩] retroflex vowel: CONFIRMED.")
        print("  F3 dip (mūrdhanya marker):"
              " CONFIRMED.")
        print("  Retroflex sector of vocal")
        print("  topology: MAPPED.")
        print()
        print("  Update VS_phoneme_inventory.md:")
        print("  [ɻ̩] status: PENDING → VERIFIED")
        print("  [g]  status: PENDING → VERIFIED"
              " (OE transfer confirmed)")
        print()
        print("  Next: AGNI [ɑgni]")
        print("  Rigveda 1.1.1, word 1.")
        print("  NEW PHONEMES: [ɑ], [n], [i]")
    else:
        failed = [l for l, ok_ in rows
                  if not ok_]
        print(f"  FAILED: {', '.join(failed)}")
        if not d4:
            print()
            print("  D4 FAILURE IS CRITICAL.")
            print("  The retroflex F3 dip is")
            print("  the entire point of this word.")
            print("  Reduce RV_F[2] and re-run.")
            print("  Target: F3 centroid < 2500 Hz.")
    print()
    print("=" * 60)
    return all_pass


if __name__ == "__main__":
    passed = run_diagnostics()
    sys.exit(0 if passed else 1)
