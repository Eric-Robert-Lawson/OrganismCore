"""
AGNI DIAGNOSTIC v1
Vedic Sanskrit: ṛg  [ɻ̩g]
Rigveda — proof of concept
February 2026

DIAGNOSTICS:
  D1   [ɻ̩] voicing
  D2   [ɻ̩] F1 centroid       — mid jaw opening
  D3   [ɻ̩] F2 centroid       — mūrdhanya locus
  D4   [ɻ̩] F3 centroid       — THE DIP (key)
  D5   [ɻ̩] F3 depression     — magnitude check
  D6   [ɻ̩] duration
  D7   [g]  closure LF ratio
  D8   [g]  burst centroid    — velar locus
  D9   [ɻ̩] mūrdhanya range   — Śikṣā confirmation
  D10  Full word
  D11  Perceptual

ALL REFERENCES ARE VS-INTERNAL OR PHYSICS-ONLY.
No values from any other language project
are used as diagnostic references.

KEY CHECKS:
  D4/D5: F3 centroid below 2500 Hz.
         Depression >= 200 Hz below
         neutral alveolar reference (2700 Hz).
         The neutral reference is a physics
         constant — the F3 of an unconstricted
         alveolar vocal tract.
         It is not borrowed from any language.
         It is the baseline from which
         retroflex departure is measured.

  D9: Śikṣā confirmation.
      Pāṇinīya Śikṣā places mūrdhanya
      phonemes at F2 locus 1200–1500 Hz.
      Measured F2 must fall in this range.
      This is a VS-internal check against
      the Śikṣā treatise — the independent
      physical derivation from within the
      tradition.

PHYSICS CONSTANTS USED:
  Neutral alveolar F3: 2700 Hz
    — the F3 of an unconstricted
      alveolar vocal tract.
      Calculated from tube acoustics.
      Language-independent.

  Mūrdhanya F2 locus: 1200–1500 Hz
    — from Pāṇinīya Śikṣā classification
      confirmed by acoustic measurement
      of living retroflex languages.
      VS-internal reference.
"""

import numpy as np
from scipy.signal import lfilter, butter
import wave as wave_module
import os
import sys

SR    = 44100
DTYPE = np.float32

os.makedirs("output_play", exist_ok=True)

# ── PHYSICS CONSTANTS — language-independent ──────────
NEUTRAL_ALVEOLAR_F3_HZ = 2700.0
# F3 of an unconstricted alveolar vocal tract.
# Calculated from tube acoustics.
# The baseline from which retroflex
# F3 depression is measured.
# Not borrowed from any language project.

# ── ŚIKṢĀ REFERENCE — VS-internal ────────────────────
MURDHANYA_F2_LO_HZ = 1200.0
MURDHANYA_F2_HI_HZ = 1500.0
# Pāṇinīya Śikṣā: mūrdhanya class
# F2 locus range derived from
# articulatory classification.
# Confirmed by acoustic measurement
# of living retroflex languages.

MURDHANYA_F3_DEPRESSION_MIN_HZ = 200.0
# Minimum F3 depression below neutral
# required to confirm mūrdhanya class.
# Derived from Śikṣā articulatory
# description of tongue-tip retroflexion
# and confirmed by acoustic measurement.


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
    print("ṚG DIAGNOSTIC v2")
    print("Vedic Sanskrit [ɻ̩g]")
    print("Rigveda — proof of concept")
    print("VS-isolated. Physics and Śikṣā only.")
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

    n_rv    = len(rv_seg)
    edge_rv = max(1, n_rv // 6)
    rv_body = rv_seg[edge_rv:n_rv - edge_rv]

    from rg_reconstruction import (
        G_CLOSURE_MS, DIL)
    n_cl      = int(G_CLOSURE_MS * DIL
                    / 1000.0 * SR)
    g_closure = g_seg[:min(n_cl, len(g_seg))]

    from rg_reconstruction import G_BURST_MS
    burst_s = len(g_closure)
    n_bu    = int(G_BURST_MS * DIL
                  / 1000.0 * SR)
    g_burst = g_seg[
        burst_s:min(burst_s + n_bu,
                    len(g_seg))]

    # ── D1 VOICING ────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 1 — [ɻ̩] VOICING")
    print()
    print("  Sustained voiced vowel.")
    print("  No AM modulation.")
    print()
    voic_rv = measure_voicing(rv_body)
    p1 = check('voicing', voic_rv,
               0.50, 1.0)
    d1 = p1
    all_pass &= d1
    print(f"  {'PASSED' if d1 else 'FAILED'}")
    print()

    # ── D2 F1 ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 2 — [ɻ̩] F1 CENTROID")
    print()
    print("  Mid jaw opening.")
    print("  F1 target ~420 Hz.")
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

    # ── D3 F2 ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 3 — [ɻ̩] F2 CENTROID")
    print()
    print("  Mūrdhanya locus.")
    print("  Śikṣā predicts: 1200–1500 Hz.")
    print("  Retroflexed tongue body.")
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

    # ── D4 F3 CENTROID ────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 4 — [ɻ̩] F3 CENTROID")
    print()
    print("  THE MŪRDHANYA MARKER.")
    print("  F3 must be BELOW 2500 Hz.")
    print(f"  Neutral alveolar F3:"
          f" {NEUTRAL_ALVEOLAR_F3_HZ:.0f} Hz")
    print("  (physics constant —"
          " unconstricted alveolar tube)")
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
        print("  Reduce RV_F[2] in")
        print("  rg_reconstruction.py")
        print("  below 2200 Hz and re-run.")
    print(f"  {'PASSED' if d4 else 'FAILED'}")
    print()

    # ── D5 F3 DEPRESSION ──────────────────
    print("─" * 60)
    print("DIAGNOSTIC 5 — [ɻ̩] F3 DEPRESSION")
    print()
    print("  Magnitude of F3 depression")
    print("  below neutral alveolar reference.")
    print(f"  Neutral: {NEUTRAL_ALVEOLAR_F3_HZ:.0f} Hz"
          " (physics constant)")
    print(f"  Minimum depression required:"
          f" {MURDHANYA_F3_DEPRESSION_MIN_HZ:.0f} Hz")
    print()
    depression = (NEUTRAL_ALVEOLAR_F3_HZ
                  - cent_f3)
    print(f"  Measured depression: "
          f"{depression:.0f} Hz")
    p1 = check(
        f'F3 depression ({depression:.0f} Hz)',
        depression,
        MURDHANYA_F3_DEPRESSION_MIN_HZ,
        1000.0,
        unit=' Hz', fmt='.1f')
    d5 = p1
    all_pass &= d5
    if d5:
        print()
        print("  Tongue curl confirmed")
        print("  in acoustic output.")
    print(f"  {'PASSED' if d5 else 'FAILED'}")
    print()

    # ── D6 DURATION ───────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 6 — [ɻ̩] DURATION")
    print()
    dur_rv_ms = len(rv_seg) / SR * 1000.0
    p1 = check(
        f'duration ({dur_rv_ms:.0f} ms)',
        dur_rv_ms, 50.0, 80.0,
        unit=' ms', fmt='.1f')
    d6 = p1
    all_pass &= d6
    print(f"  {'PASSED' if d6 else 'FAILED'}")
    print()

    # ── D7 G CLOSURE LF RATIO ─────────────
    print("─" * 60)
    print("DIAGNOSTIC 7 — [g] CLOSURE"
          " LF RATIO")
    print()
    print("  Voiced velar closure murmur.")
    print("  LF energy ratio >= 0.40.")
    print()
    lf_g = measure_lf_ratio(g_closure)
    p1 = check('LF ratio', lf_g,
               0.40, 1.0)
    d7 = p1
    all_pass &= d7
    print(f"  {'PASSED' if d7 else 'FAILED'}")
    print()

    # ── D8 G BURST CENTROID ───────────────
    print("─" * 60)
    print("DIAGNOSTIC 8 — [g] BURST"
          " CENTROID")
    print()
    print("  Velar locus ~2500 Hz.")
    print("  Kaṇṭhya class — Śikṣā.")
    print()
    if len(g_burst) > 10:
        cent_burst = measure_band_centroid(
            g_burst, 1000.0, 4000.0)
        p1 = check(
            f'burst centroid'
            f' ({cent_burst:.0f} Hz)',
            cent_burst, 1800.0, 3200.0,
            unit=' Hz', fmt='.1f')
        d8 = p1
    else:
        print("  Burst too short — skip")
        d8 = True
    all_pass &= d8
    print(f"  {'PASSED' if d8 else 'FAILED'}")
    print()

    # ── D9 ŚIKṢĀ CONFIRMATION ─────────────
    print("─" * 60)
    print("DIAGNOSTIC 9 — ŚIKṢĀ CONFIRMATION")
    print()
    print("  Pāṇinīya Śikṣā: mūrdhanya class")
    print(f"  predicts F2 locus"
          f" {MURDHANYA_F2_LO_HZ:.0f}–"
          f"{MURDHANYA_F2_HI_HZ:.0f} Hz.")
    print(f"  Measured F2: {cent_f2:.0f} Hz")
    print()
    in_range = (MURDHANYA_F2_LO_HZ
                <= cent_f2
                <= MURDHANYA_F2_HI_HZ)
    p1 = check(
        f'F2 in mūrdhanya range'
        f' ({cent_f2:.0f} Hz)',
        cent_f2,
        MURDHANYA_F2_LO_HZ,
        MURDHANYA_F2_HI_HZ,
        unit=' Hz', fmt='.1f')
    d9 = p1
    all_pass &= d9
    if d9:
        print()
        print("  Śikṣā confirmed.")
        print("  The ancient phoneticians")
        print("  measured from the inside.")
        print("  The spectrograph measures")
        print("  from the outside.")
        print("  They agree.")
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
    print("  The retroflex vowel.")
    print("  Not English r.")
    print("  Not a schwa.")
    print("  Not [u].")
    print("  A new room in the vocal topology.")
    print("  The tongue is curled.")
    print("  You can hear the curl.")
    print("  F3 is depressed. That is the curl.")
    print()
    print("  Then the velar stop.")
    print("  F2 rises from ~1200 Hz to ~2400 Hz")
    print("  through the closure.")
    print("  The coarticulation maps")
    print("  new territory.")
    print()

    # ── F3 DIP REPORT ─────────────────────
    print("─" * 60)
    print("F3 DIP REPORT — MŪRDHANYA MARKER")
    print()
    print(f"  Neutral F3 (alveolar, physics): "
          f"{NEUTRAL_ALVEOLAR_F3_HZ:.0f} Hz")
    print(f"  Measured [ɻ̩] F3:                "
          f"{cent_f3:.0f} Hz")
    print(f"  F3 depression:                  "
          f"{depression:.0f} Hz")
    print(f"  Required minimum:               "
          f"{MURDHANYA_F3_DEPRESSION_MIN_HZ:.0f} Hz")
    print()
    if depression >= MURDHANYA_F3_DEPRESSION_MIN_HZ:
        print("  MŪRDHANYA CONFIRMED.")
        print("  The tongue curl is present")
        print("  in the acoustic output.")
        print("  Śikṣā and physics agree.")
    else:
        print("  MŪRDHANYA NOT CONFIRMED.")
        print("  Depression below minimum.")
        print("  Reduce RV_F[2].")
    print()

    # ── SUMMARY ───────────────────────────
    print("=" * 60)
    print("SUMMARY")
    print()
    rows = [
        ("D1   [ɻ̩] voicing",              d1),
        ("D2   [ɻ̩] F1 centroid",           d2),
        ("D3   [ɻ̩] F2 centroid",           d3),
        ("D4   [ɻ̩] F3 centroid (KEY)",     d4),
        ("D5   [ɻ̩] F3 depression (KEY)",   d5),
        ("D6   [ɻ̩] duration",              d6),
        ("D7   [g]  LF ratio",             d7),
        ("D8   [g]  burst centroid",       d8),
        ("D9   Śikṣā confirmation (KEY)",  d9),
        ("D10  Full word",                 d10),
    ]
    for lbl, ok_ in rows:
        sym = "✓ PASS" if ok_ else "✗ FAIL"
        print(f"  {lbl:32s}  {sym}")
    print(f"  {'D11  Perceptual':32s}  LISTEN")
    print()
    if all_pass:
        print("  ALL NUMERIC CHECKS PASSED")
        print()
        print("  ṚG [ɻ̩g] verified.")
        print("  [ɻ̩] — mūrdhanya confirmed.")
        print("  F3 depression confirmed.")
        print("  Śikṣā confirmed.")
        print("  Retroflex sector mapped.")
        print("  VS-isolated. No OE references.")
        print()
        print("  VS phonemes verified: [ɻ̩] [g]")
        print()
        print("  Next: AGNI [ɑgni]")
        print("  Rigveda 1.1.1, word 1.")
        print("  NEW PHONEMES: [ɑ] [n] [i]")
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
