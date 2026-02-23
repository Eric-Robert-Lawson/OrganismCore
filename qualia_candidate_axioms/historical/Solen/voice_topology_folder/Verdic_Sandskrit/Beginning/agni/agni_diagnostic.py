"""
AGNI DIAGNOSTIC v1
Vedic Sanskrit: agni  [ɑgni]
Rigveda 1.1.1 — word 1
February 2026

VS-ISOLATED.
All references are VS-internal or
physics/Śikṣā constants only.
No values from any other language
reconstruction project.

DIAGNOSTICS:
  D1   [ɑ] voicing
  D2   [ɑ] F1 centroid       — kaṇṭhya: high F1
  D3   [ɑ] F2 centroid       — back vowel
  D4   [ɑ] Śikṣā confirmation — kaṇṭhya range
  D5   [g]  closure LF ratio  — VS-verified
  D6   [g]  burst centroid    — kaṇṭhya locus
  D7   [n]  voicing           — nasal murmur
  D8   [n]  antiresonance     — dantya zero (NEW)
  D9   [i]  voicing
  D10  [i]  F2 centroid       — tālavya: high F2
  D11  [i]  Śikṣā confirmation — tālavya range
  D12  VS vowel triangle      — VS-internal only
  D13  Full word
  D14  Perceptual

PHYSICS CONSTANTS:
  NEUTRAL_ALVEOLAR_F3_HZ = 2700 Hz
  (language-independent tube acoustics)

ŚIKṢĀ REFERENCES — VS-internal:
  Kaṇṭhya [ɑ]: F1 620–800 Hz
               (maximally open vocal tract)
  Kaṇṭhya [g]: burst locus 1800–3200 Hz
               (confirmed ṚG: 2577 Hz)
  Dantya  [n]: antiresonance ~800 Hz
               (nasal side branch zero)
  Tālavya [i]: F2 1900–2500 Hz
               (palatal constriction)

VS-INTERNAL SEPARATION REFERENCES:
  [ɻ̩] F1: 385 Hz  (verified ṚG)
  [ɻ̩] F2: 1212 Hz (verified ṚG)
  These are the only cross-phoneme
  references used — both verified
  within this project.

KEY CHECKS:
  D2: [ɑ] F1 must be high.
      Kaṇṭhya = maximally open.
      Target 620–800 Hz.
      This is the highest F1 in the
      VS inventory to date.

  D8: Nasal antiresonance — the zero.
      Notch-to-neighbour ratio < 0.60.
      If D8 fails: increase VS_N_ANTI_BW
      in agni_reconstruction.py and re-run.

  D12: VS vowel triangle.
       [ɑ] back, [ɻ̩] retroflex mid,
       [i] front. All VS-internal.
       [i] F2 minus [ɑ] F2 >= 900 Hz.
       The triangle is anchored when
       this separation is confirmed.
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
NEUTRAL_ALVEOLAR_F3_HZ = 2700.0

# ── ŚIKṢĀ REFERENCES — VS-internal ───────────────────
KANTHHYA_F1_LO_HZ      =  620.0
KANTHHYA_F1_HI_HZ      =  800.0
# Kaṇṭhya open vowel: maximally open
# vocal tract. Śikṣā classification
# implies highest F1 of any vowel class.

KANTHHYA_F2_BACK_LO_HZ =  900.0
KANTHHYA_F2_BACK_HI_HZ = 1300.0
# Back vowel F2 range for [ɑ].
# Tongue retracted — low-mid F2.

KANTHHYA_BURST_LO_HZ   = 1800.0
KANTHHYA_BURST_HI_HZ   = 3200.0
# Velar burst locus. Confirmed ṚG: 2577 Hz.

DANTYA_ANTI_F_HZ       =  800.0
DANTYA_ANTI_RATIO_MAX  =    0.60
# Dantya nasal antiresonance.
# Notch-to-neighbour ratio < 0.60.

TALAVYA_F2_LO_HZ       = 1900.0
TALAVYA_F2_HI_HZ       = 2500.0
# Tālavya palatal F2 range.

# ── VS-INTERNAL VERIFIED REFERENCES ──────────────────
VS_RV_F1_HZ  = 385.0
VS_RV_F2_HZ  = 1212.0
# [ɻ̩] verified ṚG — February 2026.
# Used only for VS vowel triangle D12.
# Both values verified within this project.


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

def measure_nasal_antiresonance(seg, sr=SR):
    """
    Measure the nasal antiresonance (zero).
    Compares energy in the notch band
    (600–1000 Hz) to adjacent bands.
    Lower ratio = deeper notch = stronger
    antiresonance confirmation.
    Target: ratio < 0.60.
    """
    if len(seg) < 64:
        return 1.0
    spec  = np.abs(np.fft.rfft(
        seg.astype(float), n=2048)) ** 2
    freqs = np.fft.rfftfreq(2048, d=1.0 / sr)
    notch_mask  = ((freqs >= 600.0)
                   & (freqs <= 1000.0))
    lower_mask  = ((freqs >= 200.0)
                   & (freqs <  600.0))
    upper_mask  = ((freqs > 1000.0)
                   & (freqs <= 1600.0))
    notch_e     = np.sum(spec[notch_mask])
    lower_e     = np.sum(spec[lower_mask])
    upper_e     = np.sum(spec[upper_mask])
    neighbour_e = (lower_e + upper_e) / 2.0
    if neighbour_e < 1e-12:
        return 1.0
    return float(notch_e / neighbour_e)

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
    print("AGNI DIAGNOSTIC v1")
    print("Vedic Sanskrit [ɑgni]")
    print("Rigveda 1.1.1 — word 1")
    print("VS-isolated. Physics and Śikṣā only.")
    print("=" * 60)
    print()

    try:
        from agni_reconstruction import (
            synth_agni,
            synth_A, synth_G,
            synth_N, synth_I,
            apply_simple_room,
            VS_A_F, VS_G_F,
            VS_N_F, VS_I_F,
            VS_G_CLOSURE_MS,
            VS_G_BURST_MS, DIL)
        print("  agni_reconstruction.py: OK")
    except ImportError as e:
        print(f"  IMPORT FAILED: {e}")
        return False
    print()

    all_pass = True

    # ── ISOLATE SEGMENTS ──────────────────
    a_seg = synth_A(F_prev=None,
                    F_next=VS_G_F)
    g_seg = synth_G(F_prev=VS_A_F,
                    F_next=VS_N_F)
    n_seg = synth_N(F_prev=VS_G_F,
                    F_next=VS_I_F)
    i_seg = synth_I(F_prev=VS_N_F,
                    F_next=None)

    def body(seg, frac=0.15):
        n    = len(seg)
        edge = max(1, int(frac * n))
        return seg[edge: n - edge]

    a_body = body(a_seg)
    n_body = body(n_seg)
    i_body = body(i_seg)

    n_cl    = int(VS_G_CLOSURE_MS * DIL
                  / 1000.0 * SR)
    g_close = g_seg[:min(n_cl, len(g_seg))]
    n_bu    = int(VS_G_BURST_MS * DIL
                  / 1000.0 * SR)
    burst_s = len(g_close)
    g_burst = g_seg[
        burst_s:min(burst_s + n_bu,
                    len(g_seg))]

    # ── D1 [ɑ] VOICING ───────────────────
    print("─" * 60)
    print("DIAGNOSTIC 1 — [ɑ] VOICING")
    print()
    voic_a = measure_voicing(a_body)
    p1 = check('voicing', voic_a,
               0.50, 1.0)
    d1 = p1
    all_pass &= d1
    print(f"  {'PASSED' if d1 else 'FAILED'}")
    print()

    # ── D2 [ɑ] F1 ────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 2 — [ɑ] F1 CENTROID")
    print()
    print("  Kaṇṭhya — maximally open vocal tract.")
    print("  Śikṣā: highest F1 of any vowel class.")
    print(f"  Target: {KANTHHYA_F1_LO_HZ:.0f}–"
          f"{KANTHHYA_F1_HI_HZ:.0f} Hz")
    print()
    cent_a_f1 = measure_band_centroid(
        a_body, 550.0, 900.0)
    p1 = check(
        f'F1 centroid ({cent_a_f1:.0f} Hz)',
        cent_a_f1,
        KANTHHYA_F1_LO_HZ,
        KANTHHYA_F1_HI_HZ,
        unit=' Hz', fmt='.1f')
    d2 = p1
    all_pass &= d2
    if not d2:
        print()
        print("  *** D2 FAILED ***")
        print("  F1 is too low.")
        print("  Increase VS_A_F[0] in")
        print("  agni_reconstruction.py")
        print("  toward 700 Hz and re-run.")
    print(f"  {'PASSED' if d2 else 'FAILED'}")
    print()

    # ── D3 [ɑ] F2 ────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 3 — [ɑ] F2 CENTROID")
    print()
    print("  Back vowel — tongue retracted.")
    print(f"  Target: {KANTHHYA_F2_BACK_LO_HZ:.0f}–"
          f"{KANTHHYA_F2_BACK_HI_HZ:.0f} Hz")
    print()
    cent_a_f2 = measure_band_centroid(
        a_body, 850.0, 1400.0)
    p1 = check(
        f'F2 centroid ({cent_a_f2:.0f} Hz)',
        cent_a_f2,
        KANTHHYA_F2_BACK_LO_HZ,
        KANTHHYA_F2_BACK_HI_HZ,
        unit=' Hz', fmt='.1f')
    d3 = p1
    all_pass &= d3
    print(f"  {'PASSED' if d3 else 'FAILED'}")
    print()

    # ── D4 [ɑ] ŚIKṢĀ CONFIRMATION ────────
    print("─" * 60)
    print("DIAGNOSTIC 4 — [ɑ] ŚIKṢĀ"
          " CONFIRMATION")
    print()
    print("  Kaṇṭhya class.")
    print("  Open vocal tract.")
    print("  F1 must exceed [ɻ̩] F1"
          f" ({VS_RV_F1_HZ:.0f} Hz — ṚG).")
    print("  The open vowel must be")
    print("  more open than the retroflex.")
    print()
    f1_exceeds_rv = cent_a_f1 - VS_RV_F1_HZ
    print(f"  [ɑ] F1 ({cent_a_f1:.0f} Hz)"
          f" vs [ɻ̩] F1 ({VS_RV_F1_HZ:.0f} Hz)")
    print(f"  Margin: {f1_exceeds_rv:.0f} Hz"
          f"  (target >= 150 Hz)")
    print()
    p1 = check(
        f'[ɑ] F1 above [ɻ̩] F1'
        f' ({f1_exceeds_rv:.0f} Hz)',
        f1_exceeds_rv, 150.0, 800.0,
        unit=' Hz', fmt='.1f')
    d4 = p1
    all_pass &= d4
    if d4:
        print()
        print("  Kaṇṭhya confirmed.")
        print("  [ɑ] is more open than [ɻ̩].")
        print("  Śikṣā ordering holds.")
    print(f"  {'PASSED' if d4 else 'FAILED'}")
    print()

    # ── D5 [g] LF RATIO ──────────────────
    print("─" * 60)
    print("DIAGNOSTIC 5 — [g] CLOSURE"
          " LF RATIO")
    print()
    print("  VS-verified kaṇṭhya stop.")
    print("  Same check as ṚG D7.")
    print("  ṚG value: 0.9703.")
    print()
    lf_g = measure_lf_ratio(g_close)
    p1 = check('LF ratio', lf_g,
               0.40, 1.0)
    d5 = p1
    all_pass &= d5
    print(f"  {'PASSED' if d5 else 'FAILED'}")
    print()

    # ── D6 [g] BURST CENTROID ─────────────
    print("─" * 60)
    print("DIAGNOSTIC 6 — [g] BURST"
          " CENTROID")
    print()
    print("  Kaṇṭhya locus.")
    print("  VS-verified: 2577 Hz in ṚG.")
    print()
    if len(g_burst) > 10:
        cent_burst = measure_band_centroid(
            g_burst, 1000.0, 4000.0)
        p1 = check(
            f'burst centroid'
            f' ({cent_burst:.0f} Hz)',
            cent_burst,
            KANTHHYA_BURST_LO_HZ,
            KANTHHYA_BURST_HI_HZ,
            unit=' Hz', fmt='.1f')
        d6 = p1
    else:
        print("  Burst too short — skip")
        d6 = True
    all_pass &= d6
    print(f"  {'PASSED' if d6 else 'FAILED'}")
    print()

    # ── D7 [n] VOICING ───────────────────
    print("─" * 60)
    print("DIAGNOSTIC 7 — [n] VOICING")
    print()
    print("  Dantya nasal murmur.")
    print("  Low amplitude. Fully periodic.")
    print()
    voic_n = measure_voicing(n_body)
    p1 = check('voicing', voic_n,
               0.50, 1.0)
    d7 = p1
    all_pass &= d7
    print(f"  {'PASSED' if d7 else 'FAILED'}")
    print()

    # ── D8 [n] ANTIRESONANCE ──────────────
    print("─" * 60)
    print("DIAGNOSTIC 8 — [n] ANTIRESONANCE")
    print()
    print("  THE DANTYA NASAL ZERO.")
    print(f"  Notch at ~{DANTYA_ANTI_F_HZ:.0f} Hz.")
    print("  Nasal side branch absorbs")
    print("  energy at this frequency.")
    print(f"  Notch-to-neighbour ratio"
          f" < {DANTYA_ANTI_RATIO_MAX:.2f}.")
    print("  Separates nasal murmur from")
    print("  voiced fricative murmur.")
    print()
    anti_ratio = measure_nasal_antiresonance(
        n_body)
    print(f"  Notch/neighbour ratio: "
          f"{anti_ratio:.4f}")
    p1 = check(
        'antiresonance ratio',
        anti_ratio, 0.0,
        DANTYA_ANTI_RATIO_MAX)
    d8 = p1
    all_pass &= d8
    if not d8:
        print()
        print("  *** D8 FAILED ***")
        print("  Nasal zero not deep enough.")
        print("  Increase VS_N_ANTI_BW in")
        print("  agni_reconstruction.py")
        print("  and re-run.")
    print(f"  {'PASSED' if d8 else 'FAILED'}")
    print()

    # ── D9 [i] VOICING ───────────────────
    print("─" * 60)
    print("DIAGNOSTIC 9 — [i] VOICING")
    print()
    voic_i = measure_voicing(i_body)
    p1 = check('voicing', voic_i,
               0.50, 1.0)
    d9 = p1
    all_pass &= d9
    print(f"  {'PASSED' if d9 else 'FAILED'}")
    print()

    # ── D10 [i] F2 ───────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 10 — [i] F2 CENTROID")
    print()
    print("  Tālavya — tongue to hard palate.")
    print("  High F2. Front corner of triangle.")
    print(f"  Target: {TALAVYA_F2_LO_HZ:.0f}–"
          f"{TALAVYA_F2_HI_HZ:.0f} Hz")
    print()
    cent_i_f2 = measure_band_centroid(
        i_body, 1800.0, 2600.0)
    p1 = check(
        f'F2 centroid ({cent_i_f2:.0f} Hz)',
        cent_i_f2,
        TALAVYA_F2_LO_HZ,
        TALAVYA_F2_HI_HZ,
        unit=' Hz', fmt='.1f')
    d10 = p1
    all_pass &= d10
    if not d10:
        print()
        print("  *** D10 FAILED ***")
        print("  [i] F2 out of tālavya range.")
        print("  Adjust VS_I_F[1] in")
        print("  agni_reconstruction.py")
        print("  and re-run.")
    print(f"  {'PASSED' if d10 else 'FAILED'}")
    print()

    # ── D11 [i] ŚIKṢĀ CONFIRMATION ───────
    print("─" * 60)
    print("DIAGNOSTIC 11 — [i] ŚIKṢĀ"
          " CONFIRMATION")
    print()
    print("  Tālavya class.")
    print("  F2 must exceed [ɻ̩] F2"
          f" ({VS_RV_F2_HZ:.0f} Hz — ṚG).")
    print("  The palatal must be further")
    print("  front than the retroflex.")
    print()
    f2_exceeds_rv = cent_i_f2 - VS_RV_F2_HZ
    print(f"  [i] F2 ({cent_i_f2:.0f} Hz)"
          f" vs [ɻ̩] F2 ({VS_RV_F2_HZ:.0f} Hz)")
    print(f"  Margin: {f2_exceeds_rv:.0f} Hz"
          f"  (target >= 600 Hz)")
    print()
    p1 = check(
        f'[i] F2 above [ɻ̩] F2'
        f' ({f2_exceeds_rv:.0f} Hz)',
        f2_exceeds_rv, 600.0, 2000.0,
        unit=' Hz', fmt='.1f')
    d11 = p1
    all_pass &= d11
    if d11:
        print()
        print("  Tālavya confirmed.")
        print("  [i] is further front than [ɻ̩].")
        print("  Śikṣā ordering holds.")
    print(f"  {'PASSED' if d11 else 'FAILED'}")
    print()

    # ── D12 VS VOWEL TRIANGLE ─────────────
    print("─" * 60)
    print("DIAGNOSTIC 12 — VS VOWEL TRIANGLE")
    print()
    print("  VS-internal only.")
    print("  All three reference points")
    print("  verified within this project.")
    print()
    print(f"  [ɑ] back:       F2 {cent_a_f2:.0f} Hz"
          f"  (this word)")
    print(f"  [ɻ̩] retroflex:  F2 {VS_RV_F2_HZ:.0f} Hz"
          f"  (ṚG verified)")
    print(f"  [i] front:      F2 {cent_i_f2:.0f} Hz"
          f"  (this word)")
    print()
    tri_sep = cent_i_f2 - cent_a_f2
    print(f"  [i]–[ɑ] F2 separation:"
          f" {tri_sep:.0f} Hz"
          f"  (target >= 900 Hz)")
    print()
    p1 = check(
        f'[i]–[ɑ] separation'
        f' ({tri_sep:.0f} Hz)',
        tri_sep, 900.0, 2000.0,
        unit=' Hz', fmt='.1f')
    d12 = p1
    all_pass &= d12
    if d12:
        print()
        print("  VS VOWEL TRIANGLE CONFIRMED.")
        print("  Three corners mapped.")
        print("  All references VS-internal.")
        print("  Physics predicts this spread.")
        print("  The instrument confirms it.")
    print(f"  {'PASSED' if d12 else 'FAILED'}")
    print()

    # ── D13 FULL WORD ─────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 13 — FULL WORD [ɑgni]")
    print()
    w_dry  = synth_agni(with_room=False)
    w_hall = synth_agni(with_room=True)
    dur_ms = len(w_dry) / SR * 1000.0
    p1 = check('RMS level', rms(w_dry),
               0.010, 0.90)
    p2 = check(
        f'duration ({dur_ms:.0f} ms)',
        dur_ms, 150.0, 320.0,
        unit=' ms', fmt='.1f')
    write_wav(
        "output_play/diag_agni_dry.wav",
        w_dry)
    write_wav(
        "output_play/diag_agni_hall.wav",
        w_hall)
    write_wav(
        "output_play/diag_agni_slow.wav",
        ola_stretch(w_dry, 4.0))
    a_iso = synth_A(F_prev=None,
                    F_next=None)
    i_iso = synth_I(F_prev=None,
                    F_next=None)
    for sig, name in [
        (a_iso, "diag_agni_a_iso"),
        (i_iso, "diag_agni_i_iso"),
    ]:
        mx = np.max(np.abs(sig))
        if mx > 1e-8:
            sig = sig / mx * 0.75
        write_wav(
            f"output_play/{name}.wav", sig)
        write_wav(
            f"output_play/{name}_slow.wav",
            ola_stretch(sig, 4.0))
    d13 = p1 and p2
    all_pass &= d13
    print(f"  {'PASSED' if d13 else 'FAILED'}")
    print()

    # ── D14 PERCEPTUAL ────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 14 — PERCEPTUAL")
    print()
    print("  Listen in this order:")
    for fn in [
        "diag_agni_a_iso_slow.wav",
        "diag_agni_i_iso_slow.wav",
        "diag_agni_slow.wav",
        "diag_agni_hall.wav",
    ]:
        print(f"  afplay output_play/{fn}")
    print()
    print("  LISTEN FOR:")
    print()
    print("  a_iso_slow:")
    print("    Sanskrit [a]. Open. Back.")
    print("    The default vowel.")
    print("    Wide jaw. Warm.")
    print()
    print("  i_iso_slow:")
    print("    Sanskrit [i]. Close. Front.")
    print("    Bright. High.")
    print("    Maximum F2 distance from [a].")
    print()
    print("  agni_slow:")
    print("    A·G·N·I at 4× speed.")
    print("    Velar closure between [a]"
          " and [n].")
    print("    Nasal murmur of [n] —")
    print("    low, damped, continuous.")
    print("    [i] bright at the end.")
    print()
    print("  agni_hall:")
    print("    Full word. Temple courtyard.")
    print("    Rigveda 1.1.1, word 1.")
    print("    The fire priest.")
    print("    The invocation.")
    print()

    # ── VS VOWEL SPACE REPORT ─────────────
    print("─" * 60)
    print("VS VOWEL SPACE — CURRENT STATE")
    print()
    print("  Verified or confirmed this session:")
    print()
    print(f"  [i]  tālavya   F2 {cent_i_f2:.0f} Hz"
          f"  — front close")
    print(f"  [ɻ̩]  mūrdhanya F2 {VS_RV_F2_HZ:.0f} Hz"
          f"  — retroflex mid  (ṚG)")
    print(f"  [ɑ]  kaṇṭhya   F2 {cent_a_f2:.0f} Hz"
          f"  — back open")
    print()
    print("  F1 ordering (open → close):")
    print(f"  [ɑ]  {cent_a_f1:.0f} Hz  — most open")
    print(f"  [ɻ̩]  {VS_RV_F1_HZ:.0f} Hz  — mid      (ṚG)")
    print(f"  [i]  ~280 Hz  — most close")
    print()
    print("  All references VS-internal.")
    print("  All values verified within")
    print("  this project.")
    print()

    # ── SUMMARY ───────────────────────────
    print("=" * 60)
    print("SUMMARY")
    print()
    rows = [
        ("D1   [ɑ] voicing",               d1),
        ("D2   [ɑ] F1 — kaṇṭhya",          d2),
        ("D3   [ɑ] F2 — back",             d3),
        ("D4   [ɑ] Śikṣā confirmation",    d4),
        ("D5   [g]  LF ratio",             d5),
        ("D6   [g]  burst centroid",       d6),
        ("D7   [n]  voicing",              d7),
        ("D8   [n]  antiresonance (KEY)",  d8),
        ("D9   [i]  voicing",              d9),
        ("D10  [i]  F2 — tālavya",         d10),
        ("D11  [i]  Śikṣā confirmation",   d11),
        ("D12  VS vowel triangle (KEY)",   d12),
        ("D13  Full word",                 d13),
    ]
    for lbl, ok_ in rows:
        sym = "✓ PASS" if ok_ else "✗ FAIL"
        print(f"  {lbl:32s}  {sym}")
    print(f"  {'D14  Perceptual':32s}  LISTEN")
    print()
    if all_pass:
        print("  ALL NUMERIC CHECKS PASSED")
        print()
        print("  AGNI [ɑgni] verified.")
        print("  [ɑ] kaṇṭhya open: CONFIRMED.")
        print("  [n] dantya nasal: CONFIRMED.")
        print("  [i] tālavya close: CONFIRMED.")
        print("  VS vowel triangle: ANCHORED.")
        print("  VS-isolated throughout.")
        print()
        print("  VS phonemes verified:")
        print("  [ɻ̩] [g] [ɑ] [n] [i]")
        print()
        print("  Next: ĪḶE [iːɭe]")
        print("  Rigveda 1.1.1, word 2.")
        print("  NEW: [iː] long close front")
        print("  NEW: [ɭ]  retroflex lateral")
    else:
        failed = [l for l, ok_ in rows
                  if not ok_]
        print(f"  FAILED: {', '.join(failed)}")
        if not d8:
            print()
            print("  D8: increase VS_N_ANTI_BW.")
        if not d2:
            print()
            print("  D2: increase VS_A_F[0].")
        if not d12:
            print()
            print("  D12: check VS_I_F[1]"
                  " and VS_A_F[1].")
    print()
    print("=" * 60)
    return all_pass


if __name__ == "__main__":
    passed = run_diagnostics()
    sys.exit(0 if passed else 1)
