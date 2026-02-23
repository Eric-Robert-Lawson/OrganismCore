"""
ĪḶE DIAGNOSTIC v1
Vedic Sanskrit: īḷe  [iːɭe]
Rigveda 1.1.1 — word 2
February 2026

VS-ISOLATED.
All references are VS-internal or
physics/Śikṣā constants only.
No values from any other language
reconstruction project.

DIAGNOSTICS:
  D1   [iː] voicing
  D2   [iː] F2 centroid         — tālavya: same as [i]
  D3   [iː] duration            — long: >= 1.7× [i]
  D4   [iː] length ratio        — VS-internal: vs verified [i]
  D5   [iː] Śikṣā confirmation  — tālavya ordering
  D6   [ɭ]  voicing
  D7   [ɭ]  F2 centroid         — lateral: reduced F2
  D8   [ɭ]  F3 centroid         — mūrdhanya: must be < 2500 Hz
  D9   [ɭ]  F3 depression       — magnitude vs neutral (KEY)
  D10  [ɭ]  Śikṣā confirmation  — mūrdhanya + lateral
  D11  [eː] voicing
  D12  [eː] F1 centroid         — tālavya mid: between [i] and [ɑ]
  D13  [eː] F2 centroid         — tālavya mid: between [i] and [ɑ]
  D14  [eː] Śikṣā confirmation  — tālavya ordering VS-internal
  D15  Full word
  D16  Perceptual

PHYSICS CONSTANTS:
  NEUTRAL_ALVEOLAR_F3_HZ = 2700 Hz
  (language-independent tube acoustics)

ŚIKṢĀ REFERENCES — VS-internal:
  Mūrdhanya: F3 depression >= 200 Hz
             (established ṚG: [ɻ̩] 345 Hz)
  Tālavya:   F2 > mūrdhanya F2
             (established AGNI: [i] 2124 Hz)

VS-INTERNAL VERIFIED REFERENCES:
  [i]  F2:  2124 Hz, dur: 50 ms  (AGNI)
  [ɻ̩]  F2:  1212 Hz, F3: 2355 Hz (ṚG)
  [ɑ]  F1:   631 Hz, F2: 1106 Hz (AGNI)
  All verified within this project.

KEY CHECKS:
  D3/D4: [iː] must be >= 1.7× [i] duration.
         [i] verified at 50 ms (AGNI).
         [iː] target 100 ms.
         Length is the phonemic distinction.
         Formant quality must be identical.

  D8/D9: [ɭ] F3 depression.
         The mūrdhanya marker.
         Same physics as [ɻ̩] in ṚG.
         Different manner — lateral not central —
         but same place: tongue tip retroflexed.
         F3 must be below 2500 Hz.
         Depression must be >= 200 Hz.
         If this fails: the tongue is not
         curled. Increase VS_LL_F3_NOTCH_BW
         or lower VS_LL_F3_NOTCH in
         ile_reconstruction.py and re-run.

  D12/D13: [eː] must sit between verified
           [i] and [ɑ] in both F1 and F2.
           VS-internal triangle check.
           All three reference points
           verified within this project.
"""

import numpy as np
from scipy.signal import lfilter, butter
import wave as wave_module
import os
import sys

SR    = 44100
DTYPE = np.float32

os.makedirs("output_play", exist_ok=True)

# ── PHYSICS CONSTANTS ─────────────────────────────────
NEUTRAL_ALVEOLAR_F3_HZ         = 2700.0
MURDHANYA_F3_DEPRESSION_MIN_HZ =  200.0

# ── VS-INTERNAL VERIFIED REFERENCES ──────────────────
VS_I_F2_HZ   = 2124.0
VS_I_DUR_MS  =   50.0
VS_RV_F2_HZ  = 1212.0
VS_RV_F3_HZ  = 2355.0
VS_A_F1_HZ   =  631.0
VS_A_F2_HZ   = 1106.0


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
    print("ĪḶE DIAGNOSTIC v1")
    print("Vedic Sanskrit [iːɭe]")
    print("Rigveda 1.1.1 — word 2")
    print("VS-isolated. Physics and Śikṣā only.")
    print("=" * 60)
    print()

    try:
        from ile_reconstruction import (
            synth_ile,
            synth_II, synth_LL, synth_EE,
            apply_simple_room,
            VS_II_F, VS_LL_F, VS_EE_F,
            VS_II_DUR_MS, DIL)
        print("  ile_reconstruction.py: OK")
    except ImportError as e:
        print(f"  IMPORT FAILED: {e}")
        return False
    print()

    all_pass = True

    # ── ISOLATE SEGMENTS ──────────────────
    ii_seg = synth_II(F_prev=None,
                      F_next=VS_LL_F)
    ll_seg = synth_LL(F_prev=VS_II_F,
                      F_next=VS_EE_F)
    ee_seg = synth_EE(F_prev=VS_LL_F,
                      F_next=None)

    def body(seg, frac=0.15):
        n    = len(seg)
        edge = max(1, int(frac * n))
        return seg[edge: n - edge]

    ii_body = body(ii_seg)
    ll_body = body(ll_seg)
    ee_body = body(ee_seg)

    # ── D1 [iː] VOICING ──────────────────
    print("─" * 60)
    print("DIAGNOSTIC 1 — [iː] VOICING")
    print()
    voic_ii = measure_voicing(ii_body)
    p1 = check('voicing', voic_ii,
               0.50, 1.0)
    d1 = p1
    all_pass &= d1
    print(f"  {'PASSED' if d1 else 'FAILED'}")
    print()

    # ── D2 [iː] F2 ───────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 2 — [iː] F2 CENTROID")
    print()
    print("  Tālavya. Same target as [i].")
    print(f"  [i] F2 verified: {VS_I_F2_HZ:.0f} Hz (AGNI)")
    print("  Quality must be identical.")
    print()
    cent_ii_f2 = measure_band_centroid(
        ii_body, 1800.0, 2600.0)
    p1 = check(
        f'F2 centroid ({cent_ii_f2:.0f} Hz)',
        cent_ii_f2, 1900.0, 2500.0,
        unit=' Hz', fmt='.1f')
    d2 = p1
    all_pass &= d2
    print(f"  {'PASSED' if d2 else 'FAILED'}")
    print()

    # ── D3 [iː] DURATION ─────────────────
    print("─" * 60)
    print("DIAGNOSTIC 3 — [iː] DURATION")
    print()
    print("  Must be long: >= 85 ms.")
    print(f"  [i] verified: {VS_I_DUR_MS:.0f} ms (AGNI)")
    print()
    dur_ii_ms = len(ii_seg) / SR * 1000.0
    p1 = check(
        f'duration ({dur_ii_ms:.0f} ms)',
        dur_ii_ms, 85.0, 140.0,
        unit=' ms', fmt='.1f')
    d3 = p1
    all_pass &= d3
    print(f"  {'PASSED' if d3 else 'FAILED'}")
    print()

    # ── D4 [iː] LENGTH RATIO ─────────────
    print("─" * 60)
    print("DIAGNOSTIC 4 — [iː] LENGTH RATIO")
    print()
    print("  VS-internal length distinction.")
    print(f"  [i]  verified: {VS_I_DUR_MS:.0f} ms (AGNI)")
    print(f"  [iː] measured: {dur_ii_ms:.0f} ms")
    ratio = dur_ii_ms / VS_I_DUR_MS
    print(f"  ratio: {ratio:.2f}×"
          f"  (target >= 1.70×)")
    print()
    p1 = check(
        f'length ratio ({ratio:.2f}×)',
        ratio, 1.70, 3.50,
        unit='×', fmt='.2f')
    d4 = p1
    all_pass &= d4
    if d4:
        print()
        print("  Length distinction confirmed.")
        print("  [iː] is measurably longer than [i].")
        print("  Phonemic quantity contrast: active.")
    print(f"  {'PASSED' if d4 else 'FAILED'}")
    print()

    # ── D5 [iː] ŚIKṢĀ CONFIRMATION ───────
    print("─" * 60)
    print("DIAGNOSTIC 5 — [iː] ŚIKṢĀ"
          " CONFIRMATION")
    print()
    print("  Tālavya class.")
    print("  [iː] F2 must match [i] F2.")
    print("  Long and short differ in duration,")
    print("  not in quality. Same tongue position.")
    print()
    f2_diff = abs(cent_ii_f2 - VS_I_F2_HZ)
    print(f"  [iː] F2: {cent_ii_f2:.0f} Hz")
    print(f"  [i]  F2: {VS_I_F2_HZ:.0f} Hz (AGNI)")
    print(f"  Difference: {f2_diff:.0f} Hz"
          f"  (target <= 200 Hz)")
    print()
    p1 = check(
        f'F2 quality match ({f2_diff:.0f} Hz diff)',
        f2_diff, 0.0, 200.0,
        unit=' Hz', fmt='.1f')
    d5 = p1
    all_pass &= d5
    if d5:
        print()
        print("  Tālavya confirmed.")
        print("  [iː] quality = [i] quality.")
        print("  Quantity distinction only.")
    print(f"  {'PASSED' if d5 else 'FAILED'}")
    print()

    # ── D6 [ɭ] VOICING ───────────────────
    print("─" * 60)
    print("DIAGNOSTIC 6 — [ɭ] VOICING")
    print()
    print("  Voiced lateral approximant.")
    print("  Sustained. No closure.")
    print()
    voic_ll = measure_voicing(ll_body)
    p1 = check('voicing', voic_ll,
               0.50, 1.0)
    d6 = p1
    all_pass &= d6
    print(f"  {'PASSED' if d6 else 'FAILED'}")
    print()

    # ── D7 [ɭ] F2 ────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 7 — [ɭ] F2 CENTROID")
    print()
    print("  Lateral + mūrdhanya.")
    print("  F2 reduced by lateral airflow.")
    print("  Lower than central [ɻ̩]"
          f" ({VS_RV_F2_HZ:.0f} Hz — ṚG).")
    print("  Target: 1000–1500 Hz")
    print()
    cent_ll_f2 = measure_band_centroid(
        ll_body, 800.0, 1600.0)
    p1 = check(
        f'F2 centroid ({cent_ll_f2:.0f} Hz)',
        cent_ll_f2, 1000.0, 1500.0,
        unit=' Hz', fmt='.1f')
    d7 = p1
    all_pass &= d7
    if not d7:
        print()
        print("  *** D7 FAILED ***")
        print("  F2 out of lateral range.")
        print("  Adjust VS_LL_F[1] in")
        print("  ile_reconstruction.py.")
    print(f"  {'PASSED' if d7 else 'FAILED'}")
    print()

    # ── D8 [ɭ] F3 CENTROID ───────────────
    print("─" * 60)
    print("DIAGNOSTIC 8 — [ɭ] F3 CENTROID")
    print()
    print("  THE MŪRDHANYA MARKER.")
    print("  F3 must be BELOW 2500 Hz.")
    print(f"  Neutral alveolar F3:"
          f" {NEUTRAL_ALVEOLAR_F3_HZ:.0f} Hz"
          " (physics constant)")
    print(f"  [ɻ̩] F3 verified:"
          f" {VS_RV_F3_HZ:.0f} Hz (ṚG)")
    print()
    cent_ll_f3 = measure_band_centroid(
        ll_body, 1800.0, 3200.0)
    p1 = check(
        f'F3 centroid ({cent_ll_f3:.0f} Hz)',
        cent_ll_f3, 1800.0, 2499.0,
        unit=' Hz', fmt='.1f')
    d8 = p1
    all_pass &= d8
    if not d8:
        print()
        print("  *** D8 FAILED ***")
        print("  F3 too high. Tongue not curled.")
        print("  Lower VS_LL_F3_NOTCH or increase")
        print("  VS_LL_F3_NOTCH_BW in")
        print("  ile_reconstruction.py.")
    print(f"  {'PASSED' if d8 else 'FAILED'}")
    print()

    # ── D9 [ɭ] F3 DEPRESSION ─────────────
    print("─" * 60)
    print("DIAGNOSTIC 9 — [ɭ] F3 DEPRESSION")
    print()
    print("  Magnitude of mūrdhanya marker.")
    print(f"  Neutral: {NEUTRAL_ALVEOLAR_F3_HZ:.0f} Hz"
          " (physics constant)")
    print(f"  [ɻ̩] depression: 345 Hz (ṚG)")
    print(f"  Minimum required:"
          f" {MURDHANYA_F3_DEPRESSION_MIN_HZ:.0f} Hz")
    print()
    ll_depression = (NEUTRAL_ALVEOLAR_F3_HZ
                     - cent_ll_f3)
    print(f"  Measured depression: "
          f"{ll_depression:.0f} Hz")
    p1 = check(
        f'F3 depression ({ll_depression:.0f} Hz)',
        ll_depression,
        MURDHANYA_F3_DEPRESSION_MIN_HZ,
        1000.0,
        unit=' Hz', fmt='.1f')
    d9 = p1
    all_pass &= d9
    if d9:
        print()
        print("  Tongue curl confirmed.")
        print("  Mūrdhanya class active.")
    print(f"  {'PASSED' if d9 else 'FAILED'}")
    print()

    # ── D10 [ɭ] ŚIKṢĀ CONFIRMATION ───────
    print("─" * 60)
    print("DIAGNOSTIC 10 — [ɭ] ŚIKṢĀ"
          " CONFIRMATION")
    print()
    print("  Mūrdhanya + lateral.")
    print("  Both constraints must hold:")
    print("  1. F3 depression >= 200 Hz")
    print("     (mūrdhanya confirmed D9)")
    print("  2. F2 < [ɻ̩] F2")
    print("     (lateral reduces F2 below")
    print("      central at same place)")
    print()
    f2_below_rv = VS_RV_F2_HZ - cent_ll_f2
    print(f"  [ɭ]  F2: {cent_ll_f2:.0f} Hz")
    print(f"  [ɻ̩]  F2: {VS_RV_F2_HZ:.0f} Hz (ṚG)")
    print(f"  [ɭ] below [ɻ̩]: {f2_below_rv:.0f} Hz"
          f"  (target >= 0 Hz)")
    print()
    p1 = check(
        f'mūrdhanya depression'
        f' ({ll_depression:.0f} Hz)',
        ll_depression,
        MURDHANYA_F3_DEPRESSION_MIN_HZ,
        1000.0,
        unit=' Hz', fmt='.1f')
    p2 = check(
        f'lateral F2 < [ɻ̩] F2'
        f' (margin {f2_below_rv:.0f} Hz)',
        f2_below_rv, 0.0, 800.0,
        unit=' Hz', fmt='.1f')
    d10 = p1 and p2
    all_pass &= d10
    if d10:
        print()
        print("  Śikṣā confirmed.")
        print("  Mūrdhanya: tongue curled.")
        print("  Lateral: F2 reduced.")
        print("  Both constraints active.")
        print("  [ɭ] is not [l].")
        print("  [ɭ] is not [ɻ̩].")
        print("  [ɭ] is both.")
    print(f"  {'PASSED' if d10 else 'FAILED'}")
    print()

    # ── D11 [eː] VOICING ─────────────────
    print("─" * 60)
    print("DIAGNOSTIC 11 — [eː] VOICING")
    print()
    voic_ee = measure_voicing(ee_body)
    p1 = check('voicing', voic_ee,
               0.50, 1.0)
    d11 = p1
    all_pass &= d11
    print(f"  {'PASSED' if d11 else 'FAILED'}")
    print()

    # ── D12 [eː] F1 ──────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 12 — [eː] F1 CENTROID")
    print()
    print("  Tālavya mid.")
    print("  F1 must sit between [i] and [ɑ].")
    print(f"  [i]  F1: ~280 Hz  (AGNI)")
    print(f"  [ɑ]  F1: {VS_A_F1_HZ:.0f} Hz (AGNI)")
    print("  [eː] target: 380–550 Hz")
    print()
    cent_ee_f1 = measure_band_centroid(
        ee_body, 300.0, 650.0)
    p1 = check(
        f'F1 centroid ({cent_ee_f1:.0f} Hz)',
        cent_ee_f1, 380.0, 550.0,
        unit=' Hz', fmt='.1f')
    d12 = p1
    all_pass &= d12
    if not d12:
        print()
        print("  *** D12 FAILED ***")
        print("  [eː] F1 out of mid range.")
        print("  Adjust VS_EE_F[0] in")
        print("  ile_reconstruction.py.")
    print(f"  {'PASSED' if d12 else 'FAILED'}")
    print()

    # ── D13 [eː] F2 ──────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 13 — [eː] F2 CENTROID")
    print()
    print("  Tālavya mid.")
    print("  F2 must sit between [i] and [ɑ].")
    print(f"  [i]  F2: {VS_I_F2_HZ:.0f} Hz (AGNI)")
    print(f"  [ɑ]  F2: {VS_A_F2_HZ:.0f} Hz (AGNI)")
    print("  [eː] target: 1500–2000 Hz")
    print()
    cent_ee_f2 = measure_band_centroid(
        ee_body, 1300.0, 2200.0)
    p1 = check(
        f'F2 centroid ({cent_ee_f2:.0f} Hz)',
        cent_ee_f2, 1500.0, 2000.0,
        unit=' Hz', fmt='.1f')
    d13 = p1
    all_pass &= d13
    if not d13:
        print()
        print("  *** D13 FAILED ***")
        print("  [eː] F2 out of mid range.")
        print("  Adjust VS_EE_F[1] in")
        print("  ile_reconstruction.py.")
    print(f"  {'PASSED' if d13 else 'FAILED'}")
    print()

    # ── D14 [eː] ŚIKṢĀ CONFIRMATION ──────
    print("─" * 60)
    print("DIAGNOSTIC 14 — [eː] ŚIKṢĀ"
          " CONFIRMATION")
    print()
    print("  Tālavya mid.")
    print("  [eː] must be between [i] and [ɑ]")
    print("  in both F1 and F2.")
    print("  VS-internal. All three verified.")
    print()
    f1_above_i  = cent_ee_f1 - 280.0
    f1_below_a  = VS_A_F1_HZ - cent_ee_f1
    f2_below_i  = VS_I_F2_HZ - cent_ee_f2
    f2_above_a  = cent_ee_f2 - VS_A_F2_HZ

    print(f"  F1: [i] ~280 < [eː] {cent_ee_f1:.0f}"
          f" < [ɑ] {VS_A_F1_HZ:.0f}")
    print(f"  F2: [ɑ] {VS_A_F2_HZ:.0f} < [eː]"
          f" {cent_ee_f2:.0f} < [i] {VS_I_F2_HZ:.0f}")
    print()
    p1 = check(
        f'[eː] F1 above [i] ~280 Hz'
        f' ({f1_above_i:.0f} Hz)',
        f1_above_i, 80.0, 400.0,
        unit=' Hz', fmt='.1f')
    p2 = check(
        f'[eː] F1 below [ɑ] {VS_A_F1_HZ:.0f} Hz'
        f' ({f1_below_a:.0f} Hz)',
        f1_below_a, 50.0, 400.0,
        unit=' Hz', fmt='.1f')
    p3 = check(
        f'[eː] F2 below [i] {VS_I_F2_HZ:.0f} Hz'
        f' ({f2_below_i:.0f} Hz)',
        f2_below_i, 100.0, 800.0,
        unit=' Hz', fmt='.1f')
    p4 = check(
        f'[eː] F2 above [ɑ] {VS_A_F2_HZ:.0f} Hz'
        f' ({f2_above_a:.0f} Hz)',
        f2_above_a, 100.0, 1000.0,
        unit=' Hz', fmt='.1f')
    d14 = p1 and p2 and p3 and p4
    all_pass &= d14
    if d14:
        print()
        print("  Tālavya mid confirmed.")
        print("  [eː] sits between [i] and [ɑ]")
        print("  in both F1 and F2.")
        print("  VS vowel space extended.")
    print(f"  {'PASSED' if d14 else 'FAILED'}")
    print()

    # ── D15 FULL WORD ─────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 15 — FULL WORD [iːɭe]")
    print()
    w_dry  = synth_ile(with_room=False)
    w_hall = synth_ile(with_room=True)
    dur_ms = len(w_dry) / SR * 1000.0
    p1 = check('RMS level', rms(w_dry),
               0.010, 0.90)
    p2 = check(
        f'duration ({dur_ms:.0f} ms)',
        dur_ms, 200.0, 380.0,
        unit=' ms', fmt='.1f')
    write_wav(
        "output_play/diag_ile_dry.wav",
        w_dry)
    write_wav(
        "output_play/diag_ile_hall.wav",
        w_hall)
    write_wav(
        "output_play/diag_ile_slow.wav",
        ola_stretch(w_dry, 4.0))
    for sig, name in [
        (synth_II(F_prev=None, F_next=None),
         "diag_ile_ii_iso"),
        (synth_LL(F_prev=None, F_next=None),
         "diag_ile_ll_iso"),
        (synth_EE(F_prev=None, F_next=None),
         "diag_ile_ee_iso"),
    ]:
        mx = np.max(np.abs(sig))
        if mx > 1e-8:
            sig = sig / mx * 0.75
        write_wav(
            f"output_play/{name}.wav", sig)
        write_wav(
            f"output_play/{name}_slow.wav",
            ola_stretch(sig, 4.0))
    d15 = p1 and p2
    all_pass &= d15
    print(f"  {'PASSED' if d15 else 'FAILED'}")
    print()

    # ── D16 PERCEPTUAL ────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 16 — PERCEPTUAL")
    print()
    print("  Listen in this order:")
    for fn in [
        "diag_ile_ii_iso_slow.wav",
        "diag_ile_ll_iso_slow.wav",
        "diag_ile_ee_iso_slow.wav",
        "diag_ile_slow.wav",
        "diag_ile_hall.wav",
    ]:
        print(f"  afplay output_play/{fn}")
    print()
    print("  LISTEN FOR:")
    print()
    print("  ii_iso_slow:")
    print("    Long bright EE.")
    print("    Same quality as AGNI [i].")
    print("    Noticeably held longer.")
    print()
    print("  ll_iso_slow:")
    print("    The retroflex lateral.")
    print("    Not English L.")
    print("    Darker than English L —")
    print("    that darkness is the curl.")
    print("    F3 is low. You can hear it.")
    print("    Lateral airflow around")
    print("    a retroflexed tongue tip.")
    print()
    print("  ee_iso_slow:")
    print("    Sanskrit mid front vowel.")
    print("    Between EE and AH.")
    print("    Not English 'ay' (diphthong).")
    print("    One steady mid vowel.")
    print()
    print("  ile_slow:")
    print("    EE·Ḷ·E at 4× speed.")
    print("    Long bright vowel.")
    print("    Dark lateral with curl.")
    print("    Mid front vowel at end.")
    print()
    print("  ile_hall:")
    print("    Full word. Temple courtyard.")
    print("    Rigveda 1.1.1, word 2.")
    print("    I praise.")
    print()

    # ── F3 DIP REPORT — [ɭ] ──────────────
    print("─" * 60)
    print("F3 DIP REPORT — [ɭ] MŪRDHANYA"
          " MARKER")
    print()
    print(f"  Neutral F3 (physics): "
          f"{NEUTRAL_ALVEOLAR_F3_HZ:.0f} Hz")
    print(f"  [ɻ̩] F3 (ṚG verified): "
          f"{VS_RV_F3_HZ:.0f} Hz  depression"
          f" {NEUTRAL_ALVEOLAR_F3_HZ - VS_RV_F3_HZ:.0f} Hz")
    print(f"  [ɭ]  F3 (measured):   "
          f"{cent_ll_f3:.0f} Hz  depression"
          f" {ll_depression:.0f} Hz")
    print()
    if ll_depression >= MURDHANYA_F3_DEPRESSION_MIN_HZ:
        print("  MŪRDHANYA CONFIRMED.")
        print("  Both [ɻ̩] and [ɭ] show F3 depression.")
        print("  Same place. Different manner.")
        print("  The tongue curl is the constant.")
    else:
        print("  MŪRDHANYA NOT CONFIRMED.")
        print("  Increase VS_LL_F3_NOTCH_BW.")
    print()

    # ── VS VOWEL SPACE REPORT ─────────────
    print("─" * 60)
    print("VS VOWEL SPACE — CURRENT STATE")
    print()
    print("  All VS-internal verified values:")
    print()
    print(f"  [i]  tālavya close  "
          f"F1 ~280  F2 {VS_I_F2_HZ:.0f}  (AGNI)")
    print(f"  [iː] tālavya close  "
          f"F1 ~280  F2 {cent_ii_f2:.0f}  (this word)")
    print(f"  [eː] tālavya mid    "
          f"F1 {cent_ee_f1:.0f}   F2 {cent_ee_f2:.0f}  (this word)")
    print(f"  [ɻ̩]  mūrdhanya      "
          f"F1 385   F2 {VS_RV_F2_HZ:.0f}  (ṚG)")
    print(f"  [ɭ]  mūrdhanya lat  "
          f"F1 ~400  F2 {cent_ll_f2:.0f}  (this word)")
    print(f"  [ɑ]  kaṇṭhya open   "
          f"F1 {VS_A_F1_HZ:.0f}   F2 {VS_A_F2_HZ:.0f}  (AGNI)")
    print()

    # ── SUMMARY ───────────────────────────
    print("=" * 60)
    print("SUMMARY")
    print()
    rows = [
        ("D1   [iː] voicing",               d1),
        ("D2   [iː] F2 — tālavya",          d2),
        ("D3   [iː] duration",              d3),
        ("D4   [iː] length ratio (KEY)",    d4),
        ("D5   [iː] Śikṣā confirmation",    d5),
        ("D6   [ɭ]  voicing",               d6),
        ("D7   [ɭ]  F2 — lateral",          d7),
        ("D8   [ɭ]  F3 centroid (KEY)",     d8),
        ("D9   [ɭ]  F3 depression (KEY)",   d9),
        ("D10  [ɭ]  Śikṣā confirmation",    d10),
        ("D11  [eː] voicing",               d11),
        ("D12  [eː] F1 — mid",              d12),
        ("D13  [eː] F2 — mid",              d13),
        ("D14  [eː] Śikṣā confirmation",    d14),
        ("D15  Full word",                  d15),
    ]
    for lbl, ok_ in rows:
        sym = "✓ PASS" if ok_ else "✗ FAIL"
        print(f"  {lbl:32s}  {sym}")
    print(f"  {'D16  Perceptual':32s}  LISTEN")
    print()
    if all_pass:
        print("  ALL NUMERIC CHECKS PASSED")
        print()
        print("  ĪḶE [iːɭe] verified.")
        print("  [iː] length distinction: CONFIRMED.")
        print("  [ɭ]  mūrdhanya lateral:  CONFIRMED.")
        print("  [eː] tālavya mid:        CONFIRMED.")
        print("  VS vowel space extended.")
        print()
        print("  VS phonemes verified:")
        print("  [ɻ̩] [g] [ɑ] [n] [i]"
              " [iː] [ɭ] [eː]")
        print()
        print("  Next: PUROHITAM [puroːhitɑm]")
        print("  Rigveda 1.1.1, word 3.")
        print("  NEW: [p] [uː] [oː] [h]")
    else:
        failed = [l for l, ok_ in rows
                  if not ok_]
        print(f"  FAILED: {', '.join(failed)}")
        if not d8 or not d9:
            print()
            print("  D8/D9: lower VS_LL_F3_NOTCH")
            print("  or increase VS_LL_F3_NOTCH_BW.")
        if not d12 or not d13:
            print()
            print("  D12/D13: adjust VS_EE_F[0]"
                  " and VS_EE_F[1].")
        if not d4:
            print()
            print("  D4: increase VS_II_DUR_MS.")
    print()
    print("=" * 60)
    return all_pass


if __name__ == "__main__":
    passed = run_diagnostics()
    sys.exit(0 if passed else 1)
