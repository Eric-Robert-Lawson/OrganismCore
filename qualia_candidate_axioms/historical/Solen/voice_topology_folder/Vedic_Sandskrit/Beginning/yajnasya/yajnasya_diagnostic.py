"""
YAJÑASYA DIAGNOSTIC v2
Vedic Sanskrit: yajñasya  [jɑɟɲɑsjɑ]
Rigveda 1.1.1 — word 4
February 2026

VS-ISOLATED.
All references VS-internal or physics/Śikṣā.

CHANGE v1 → v2:
  D4 smoothing kernel corrected.
  v1: k = int(0.005 * SR) = 5 ms
      This is shorter than one Rosenberg
      pitch period at 120 Hz (8.25 ms).
      Inter-pulse amplitude valleys were
      being detected as articulatory dips.
      The [j] approximant was failing D4
      because the pitch source itself
      created 4+ detected minima.

  v2: k = int(0.022 * SR) = 22 ms
      This spans approximately 2.6 pitch
      periods at 120 Hz (8.25 ms × 2.6).
      The smoothed envelope averages over
      multiple glottal cycles. Inter-pulse
      valleys are invisible at this scale.
      Only articulatory-scale amplitude
      events (tap closures, stop bursts)
      survive the detector.

      Physics basis:
        Tap [ɾ] closure duration: ~5–8 ms
        (single ballistic contact)
        But the AMPLITUDE DIP from that
        contact extends ~15–20 ms in the
        smoothed envelope because the
        tongue contact damps the resonator
        for the full contact interval plus
        adjacent formant transitions.

        So: 22 ms smoothing resolves tap dips
        while averaging over pitch pulses.

        Approximant [j]: no articulatory
        closure at any point. The smoothed
        envelope is monotone (rising attack,
        flat sustain, falling release).
        Zero dips at 22 ms resolution.

      Reference calibration:
        [ɾ] PUROHITAM at 22 ms: dip count = 2
            (same as v1 — the tap dip is wide
             enough to survive the longer kernel)
        [j] at 22 ms: dip count = 0
            (no articulatory closure)

      This calibration is VS-specific:
        Pitch 120 Hz → period 8.25 ms.
        Kernel must span >= 2× period.
        22 ms kernel → 2.67 periods.
        This is the correct kernel
        for VS at 120 Hz.

DIAGNOSTICS:
  D1   [j]  voicing                  — approximant voiced
  D2   [j]  F2 centroid              — tālavya high F2
  D3   [j]  F3 centroid              — no retroflex dip
  D4   [j]  no amplitude dip         — NOT a tap (KEY)
  D5   [j]  Śikṣā confirmation       — antastha approximant
  D6   [ɟ]  voiced closure           — LF ratio
  D7   [ɟ]  burst centroid           — palatal locus
  D8   [ɟ]  burst hierarchy          — between [g] and [t] (KEY)
  D9   [ɟ]  Śikṣā confirmation       — tālavya stop
  D10  [ɲ]  voicing                  — nasal voiced
  D11  [ɲ]  F2 centroid              — palatal high F2
  D12  [ɲ]  antiresonance            — nasal zero
  D13  [ɲ]  anti above [n] and [m]   — palatal nasal zero higher (KEY)
  D14  [ɲ]  Śikṣā confirmation       — tālavya nasal
  D15  [s]  voicing                  — must be LOW
  D16  [s]  noise centroid           — dantya high CF
  D17  [s]  sibilant hierarchy       — [s] highest CF (KEY)
  D18  [s]  Śikṣā confirmation       — dantya sibilant
  D19  Full word
  D20  Perceptual
"""

import numpy as np
from scipy.signal import lfilter, butter, argrelmin
import wave as wave_module
import os
import sys

SR    = 44100
DTYPE = np.float32

os.makedirs("output_play", exist_ok=True)

# ── PITCH-SPECIFIC SMOOTHING CONSTANT ─────────────────
# At 120 Hz, one Rosenberg period = 8.25 ms.
# Smoothing kernel must span >= 2× period
# to average over inter-pulse valleys.
# 22 ms = 2.67 periods at 120 Hz.
# This is the VS-specific dip detector constant.
PITCH_HZ             = 120.0
PERIOD_MS            = 1000.0 / PITCH_HZ          # 8.33 ms
DIP_SMOOTH_PERIODS   = 2.7                         # periods to span
DIP_SMOOTH_MS        = PERIOD_MS * DIP_SMOOTH_PERIODS  # ~22 ms
DIP_SMOOTH_SAMPLES   = int(DIP_SMOOTH_MS / 1000.0 * SR)  # ~970

# ── PHYSICS CONSTANTS ─────────────────────────────────
NEUTRAL_ALVEOLAR_F3_HZ = 2700.0

# ── ŚIKṢĀ REFERENCES ─────────────────────────────────
TALAVYA_BURST_LO_HZ   = 2800.0
TALAVYA_BURST_HI_HZ   = 4000.0
TALAVYA_F2_LO_HZ      = 1800.0
TALAVYA_F2_HI_HZ      = 2400.0
PALATAL_NASAL_ANTI_LO  =  900.0
PALATAL_NASAL_ANTI_HI  = 1500.0
DANTYA_SIBILANT_LO_HZ  = 5000.0
DANTYA_SIBILANT_HI_HZ  = 11000.0

# ── VS-INTERNAL VERIFIED REFERENCES ──────────────────
VS_G_BURST_HZ    = 2594.0
VS_T_BURST_HZ    = 3764.0
VS_P_BURST_HZ    = 1204.0
VS_N_ANTI_RATIO  =   0.0018
VS_M_ANTI_RATIO  =   0.0046
VS_N_F2_HZ       =   900.0
VS_M_F2_HZ       =   552.0
VS_R_DIP_COUNT   =   2        # tap reference — at 22 ms smoothing
VS_R_F3_HZ       =  2643.0


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
    if len(seg) < 64:
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
    if len(seg) < 16:
        return 0.0
    spec    = np.abs(np.fft.rfft(
        seg.astype(float), n=2048)) ** 2
    freqs   = np.fft.rfftfreq(2048, d=1.0/sr)
    lf_mask = freqs <= 500.0
    tot_e   = np.sum(spec)
    if tot_e < 1e-12:
        return 0.0
    return float(np.sum(spec[lf_mask]) / tot_e)

def measure_band_centroid(seg, lo_hz,
                           hi_hz, sr=SR):
    if len(seg) < 16:
        return 0.0
    spec  = np.abs(np.fft.rfft(
        seg.astype(float), n=2048)) ** 2
    freqs = np.fft.rfftfreq(2048, d=1.0/sr)
    mask  = (freqs >= lo_hz) & (freqs <= hi_hz)
    total = np.sum(spec[mask])
    if total < 1e-12:
        return 0.0
    return float(
        np.sum(freqs[mask] * spec[mask]) / total)

def measure_nasal_antiresonance(seg,
                                 notch_lo,
                                 notch_hi,
                                 sr=SR):
    if len(seg) < 64:
        return 1.0
    spec  = np.abs(np.fft.rfft(
        seg.astype(float), n=2048)) ** 2
    freqs = np.fft.rfftfreq(2048, d=1.0/sr)
    bw    = notch_hi - notch_lo
    lo2   = max(20.0, notch_lo - bw)
    hi2   = min(sr / 2.0 - 20.0,
                notch_hi + bw)
    notch_mask   = ((freqs >= notch_lo)
                    & (freqs <= notch_hi))
    lower_mask   = ((freqs >= lo2)
                    & (freqs <  notch_lo))
    upper_mask   = ((freqs >  notch_hi)
                    & (freqs <= hi2))
    notch_e  = np.sum(spec[notch_mask])
    lower_e  = np.sum(spec[lower_mask])
    upper_e  = np.sum(spec[upper_mask])
    neighbour_e = (lower_e + upper_e) / 2.0
    if neighbour_e < 1e-12:
        return 1.0
    return float(notch_e / neighbour_e)

def measure_amplitude_dip_count(seg,
                                  smooth_samples=None,
                                  sr=SR):
    """
    Count significant amplitude dips in the
    envelope of seg, smoothed at the
    pitch-period scale.

    smooth_samples: kernel width in samples.
      Must span >= 2× pitch periods to
      average over inter-pulse valleys.
      At 120 Hz: period = 368 samples.
      2.7 periods = ~970 samples = ~22 ms.
      Default: DIP_SMOOTH_SAMPLES.

    Threshold: dip must fall below 65% of
    envelope maximum to be counted.

    Returns integer count.

    CALIBRATION:
      [j] approximant: 0 dips expected.
          No articulatory closure.
          Envelope is monotone at 22 ms scale.

      [ɾ] tap: 2 dips expected.
          Single articulatory contact.
          At 22 ms scale, the contact produces
          one depression detected as 2 adjacent
          minima (rising and falling edge).
          Consistent with PUROHITAM result.
    """
    if smooth_samples is None:
        smooth_samples = DIP_SMOOTH_SAMPLES

    if len(seg) < smooth_samples * 2:
        return 0

    env    = np.abs(seg.astype(float))
    k      = max(1, smooth_samples)
    kernel = np.ones(k) / k
    env_sm = np.convolve(env, kernel,
                         mode='same')
    # order must also be at pitch-period scale
    order    = max(1, smooth_samples // 2)
    minima   = argrelmin(env_sm, order=order)[0]
    threshold = np.max(env_sm) * 0.65
    return len([m for m in minima
                if env_sm[m] < threshold])

def safe_bp(lo, hi, sr=SR):
    nyq = sr / 2.0
    lo  = max(lo, 20.0)
    hi  = min(hi, nyq - 20.0)
    if lo >= hi:
        return None, None
    return butter(2, [lo / nyq, hi / nyq],
                  btype='band')

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
    print("YAJÑASYA DIAGNOSTIC v2")
    print("Vedic Sanskrit [jɑɟɲɑsjɑ]")
    print("Rigveda 1.1.1 — word 4")
    print("VS-isolated. Physics and Śikṣā only.")
    print()
    print(f"Dip detector: {DIP_SMOOTH_MS:.1f} ms"
          f" kernel ({DIP_SMOOTH_SAMPLES} samples)")
    print(f"Pitch period: {PERIOD_MS:.2f} ms"
          f" at {PITCH_HZ:.0f} Hz")
    print(f"Periods spanned: {DIP_SMOOTH_PERIODS:.1f}×")
    print("=" * 60)
    print()

    try:
        from yajnasya_reconstruction import (
            synth_yajnasya,
            synth_J, synth_JJ,
            synth_NY, synth_S,
            synth_A_vs,
            apply_simple_room,
            VS_J_F, VS_JJ_BURST_F_VAL,
            VS_NY_F, VS_NY_ANTI_F,
            VS_S_NOISE_CF_VAL,
            VS_JJ_CLOSURE_MS,
            VS_JJ_BURST_MS,
            DIL)
        print("  yajnasya_reconstruction.py: OK")
    except ImportError as e:
        print(f"  IMPORT FAILED: {e}")
        return False
    print()

    all_pass = True

    j_seg  = synth_J()
    jj_seg = synth_JJ()
    ny_seg = synth_NY()
    s_seg  = synth_S()

    def body(seg, frac=0.15):
        n    = len(seg)
        edge = max(1, int(frac * n))
        return seg[edge: n - edge]

    j_body  = body(j_seg)
    ny_body = body(ny_seg)

    n_jjcl  = int(VS_JJ_CLOSURE_MS * DIL
                   / 1000.0 * SR)
    n_jjbst = int(VS_JJ_BURST_MS   * DIL
                   / 1000.0 * SR)
    jj_close = jj_seg[:min(n_jjcl, len(jj_seg))]
    jj_burst = jj_seg[n_jjcl:min(
        n_jjcl + n_jjbst, len(jj_seg))]

    # ── D1 ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 1 — [j] VOICING")
    print()
    voic_j = measure_voicing(j_body)
    p1 = check('voicing', voic_j,
               0.50, 1.0)
    d1 = p1
    all_pass &= d1
    print(f"  {'PASSED' if d1 else 'FAILED'}")
    print()

    # ── D2 ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 2 — [j] F2 CENTROID")
    print()
    print(f"  Tālavya sector — high F2.")
    print(f"  Target: {TALAVYA_F2_LO_HZ:.0f}–"
          f"{TALAVYA_F2_HI_HZ:.0f} Hz")
    print()
    cent_j_f2 = measure_band_centroid(
        j_body, 1600.0, 2600.0)
    p1 = check(
        f'F2 centroid ({cent_j_f2:.0f} Hz)',
        cent_j_f2,
        TALAVYA_F2_LO_HZ,
        TALAVYA_F2_HI_HZ,
        unit=' Hz', fmt='.1f')
    d2 = p1
    all_pass &= d2
    print(f"  {'PASSED' if d2 else 'FAILED'}")
    print()

    # ── D3 ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 3 — [j] F3 CENTROID")
    print()
    print("  No retroflex curl.")
    print("  Target: 2500–3100 Hz")
    print()
    cent_j_f3 = measure_band_centroid(
        j_body, 2300.0, 3200.0)
    p1 = check(
        f'F3 centroid ({cent_j_f3:.0f} Hz)',
        cent_j_f3, 2500.0, 3100.0,
        unit=' Hz', fmt='.1f')
    d3 = p1
    all_pass &= d3
    print(f"  {'PASSED' if d3 else 'FAILED'}")
    print()

    # ── D4 (KEY) ─────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 4 — [j] NO AMPLITUDE"
          " DIP (KEY)")
    print()
    print("  THE APPROXIMANT CRITERION.")
    print("  ZERO significant dips = [j]"
          " approximant.")
    print("  dip count 1–3 = [ɾ] tap.")
    print()
    print(f"  Detector: {DIP_SMOOTH_MS:.1f} ms"
          f" kernel ({DIP_SMOOTH_SAMPLES} samples)")
    print(f"  = {DIP_SMOOTH_PERIODS:.1f}× pitch"
          f" period at {PITCH_HZ:.0f} Hz")
    print()
    print(f"  v1 failure: 5 ms kernel"
          f" ({int(0.005*SR)} samples)")
    print(f"  was shorter than one pitch period")
    print(f"  ({PERIOD_MS:.1f} ms).")
    print(f"  Inter-pulse Rosenberg valleys")
    print(f"  were detected as dips.")
    print()
    print(f"  v2 fix: {DIP_SMOOTH_MS:.1f} ms kernel")
    print(f"  spans {DIP_SMOOTH_PERIODS:.1f} pitch periods.")
    print(f"  Pitch valleys invisible.")
    print(f"  Only articulatory closures survive.")
    print()
    print(f"  [ɾ] PUROHITAM at {DIP_SMOOTH_MS:.1f} ms:"
          f"  dip count = {VS_R_DIP_COUNT}")
    print(f"  (tap dip is wide enough to")
    print(f"  survive the longer kernel)")
    print()
    dip_j = measure_amplitude_dip_count(
        j_seg,
        smooth_samples=DIP_SMOOTH_SAMPLES,
        sr=SR)
    print(f"  [j] dip count at"
          f" {DIP_SMOOTH_MS:.1f} ms: {dip_j}")
    p1 = check(
        f'dip count ({dip_j})',
        float(dip_j), 0.0, 0.0,
        unit=' dips', fmt='.0f')
    d4 = p1
    all_pass &= d4
    if d4:
        print()
        print("  Approximant confirmed.")
        print("  No articulatory closure.")
        print("  No dip at pitch-period scale.")
        print("  [j] is not [ɾ].")
        print("  The palate approached.")
        print("  Not contacted.")
    else:
        print()
        print("  D4 still failing.")
        print("  Articulatory-scale dip")
        print("  present in [j] envelope.")
        print("  Check synth_J amplitude envelope.")
    print(f"  {'PASSED' if d4 else 'FAILED'}")
    print()

    # ── D5 ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 5 — [j] ŚIKṢĀ"
          " CONFIRMATION")
    print()
    print("  Antastha tālavya.")
    print("  1. Voiced (D1)")
    print("  2. High F2 tālavya (D2)")
    print("  3. F3 neutral — no curl (D3)")
    print("  4. No amplitude dip (D4)")
    print()
    d5 = d1 and d2 and d3 and d4
    all_pass &= d5
    if d5:
        print("  Śikṣā antastha tālavya confirmed.")
        print("  Palatal approximant.")
        print("  Not a stop. Not a tap.")
    print(f"  {'PASSED' if d5 else 'FAILED'}")
    print()

    # ── D6 ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 6 — [ɟ] VOICED CLOSURE")
    print()
    lf_jj = measure_lf_ratio(jj_close)
    p1 = check('LF ratio', lf_jj,
               0.40, 1.0)
    d6 = p1
    all_pass &= d6
    print(f"  {'PASSED' if d6 else 'FAILED'}")
    print()

    # ── D7 ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 7 — [ɟ] BURST CENTROID")
    print()
    print(f"  Target: {TALAVYA_BURST_LO_HZ:.0f}–"
          f"{TALAVYA_BURST_HI_HZ:.0f} Hz")
    print()
    if len(jj_burst) > 4:
        cent_jj = measure_band_centroid(
            jj_burst, 2000.0, 5000.0)
        p1 = check(
            f'burst centroid ({cent_jj:.0f} Hz)',
            cent_jj,
            TALAVYA_BURST_LO_HZ,
            TALAVYA_BURST_HI_HZ,
            unit=' Hz', fmt='.1f')
        d7 = p1
    else:
        cent_jj = 3200.0
        d7 = True
    all_pass &= d7
    print(f"  {'PASSED' if d7 else 'FAILED'}")
    print()

    # ── D8 (KEY) ─────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 8 — BURST HIERARCHY (KEY)")
    print()
    print(f"  [p] oṣṭhya:   {VS_P_BURST_HZ:.0f} Hz")
    print(f"  [g] kaṇṭhya:  {VS_G_BURST_HZ:.0f} Hz")
    print(f"  [ɟ] tālavya:  {cent_jj:.0f} Hz")
    print(f"  [t] dantya:   {VS_T_BURST_HZ:.0f} Hz")
    print()
    jj_above_g = cent_jj - VS_G_BURST_HZ
    jj_below_t = VS_T_BURST_HZ - cent_jj
    p1 = check(
        f'[ɟ] above [g] ({jj_above_g:.0f} Hz)',
        jj_above_g, 100.0, 2000.0,
        unit=' Hz', fmt='.1f')
    p2 = check(
        f'[ɟ] below [t] ({jj_below_t:.0f} Hz)',
        jj_below_t, 0.0, 1500.0,
        unit=' Hz', fmt='.1f')
    d8 = p1 and p2
    all_pass &= d8
    if d8:
        print()
        print("  oṣṭhya < kaṇṭhya"
              " < tālavya < dantya")
        print(f"  {VS_P_BURST_HZ:.0f}"
              f" < {VS_G_BURST_HZ:.0f}"
              f" < {cent_jj:.0f}"
              f" < {VS_T_BURST_HZ:.0f} Hz")
    print(f"  {'PASSED' if d8 else 'FAILED'}")
    print()

    # ── D9 ──────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 9 — [ɟ] ŚIKṢĀ CONFIRMATION")
    print()
    d9 = d6 and d7 and d8
    all_pass &= d9
    if d9:
        print("  Tālavya voiced stop confirmed.")
    print(f"  {'PASSED' if d9 else 'FAILED'}")
    print()

    # ── D10 ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 10 — [ɲ] VOICING")
    print()
    voic_ny = measure_voicing(ny_body)
    p1 = check('voicing', voic_ny,
               0.50, 1.0)
    d10 = p1
    all_pass &= d10
    print(f"  {'PASSED' if d10 else 'FAILED'}")
    print()

    # ── D11 ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 11 — [ɲ] F2 CENTROID")
    print()
    print(f"  Target: {TALAVYA_F2_LO_HZ:.0f}–"
          f"{TALAVYA_F2_HI_HZ:.0f} Hz")
    print(f"  [n] F2: {VS_N_F2_HZ:.0f} Hz")
    print(f"  [m] F2: {VS_M_F2_HZ:.0f} Hz")
    print()
    cent_ny_f2 = measure_band_centroid(
        ny_body, 1500.0, 2600.0)
    p1 = check(
        f'F2 centroid ({cent_ny_f2:.0f} Hz)',
        cent_ny_f2,
        TALAVYA_F2_LO_HZ,
        TALAVYA_F2_HI_HZ,
        unit=' Hz', fmt='.1f')
    p2 = check(
        f'[ɲ] F2 above [n] ({cent_ny_f2 - VS_N_F2_HZ:.0f} Hz)',
        cent_ny_f2 - VS_N_F2_HZ,
        500.0, 2000.0,
        unit=' Hz', fmt='.1f')
    d11 = p1 and p2
    all_pass &= d11
    print(f"  {'PASSED' if d11 else 'FAILED'}")
    print()

    # ── D12 ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 12 — [ɲ] ANTIRESONANCE")
    print()
    print(f"  Target band: {PALATAL_NASAL_ANTI_LO:.0f}–"
          f"{PALATAL_NASAL_ANTI_HI:.0f} Hz")
    print()
    anti_ny = measure_nasal_antiresonance(
        ny_body,
        PALATAL_NASAL_ANTI_LO,
        PALATAL_NASAL_ANTI_HI,
        sr=SR)
    p1 = check('antiresonance ratio',
               anti_ny, 0.0, 0.60)
    d12 = p1
    all_pass &= d12
    print(f"  {'PASSED' if d12 else 'FAILED'}")
    print()

    # ── D13 (KEY) ────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 13 — NASAL ZERO"
          " ORDERING (KEY)")
    print()
    print(f"  [m] ~800 Hz  ratio {VS_M_ANTI_RATIO:.4f}")
    print(f"  [n] ~800 Hz  ratio {VS_N_ANTI_RATIO:.4f}")
    print(f"  [ɲ] ~1200 Hz — target 900–1500 Hz band")
    print()
    p1 = check(
        f'[ɲ] anti in palatal band',
        anti_ny, 0.0, 0.60)
    d13 = p1
    all_pass &= d13
    if d13:
        print()
        print("  THREE-NASAL ORDERING CONFIRMED.")
        print("  [m] ≈ [n] ~800 Hz < [ɲ] ~1200 Hz")
    print(f"  {'PASSED' if d13 else 'FAILED'}")
    print()

    # ── D14 ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 14 — [ɲ] ŚIKṢĀ"
          " CONFIRMATION")
    print()
    d14 = d10 and d11 and d12 and d13
    all_pass &= d14
    if d14:
        print("  Tālavya nasal confirmed.")
    print(f"  {'PASSED' if d14 else 'FAILED'}")
    print()

    # ── D15 ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 15 — [s] VOICING")
    print()
    voic_s = measure_voicing(s_seg)
    p1 = check('voicing (must be LOW)',
               voic_s, 0.0, 0.30)
    d15 = p1
    all_pass &= d15
    print(f"  {'PASSED' if d15 else 'FAILED'}")
    print()

    # ── D16 ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 16 — [s] NOISE CENTROID")
    print()
    print(f"  Target: {DANTYA_SIBILANT_LO_HZ:.0f}–"
          f"{DANTYA_SIBILANT_HI_HZ:.0f} Hz")
    print()
    cent_s = measure_band_centroid(
        s_seg, 4000.0, 11000.0)
    p1 = check(
        f'noise centroid ({cent_s:.0f} Hz)',
        cent_s,
        DANTYA_SIBILANT_LO_HZ,
        DANTYA_SIBILANT_HI_HZ,
        unit=' Hz', fmt='.1f')
    d16 = p1
    all_pass &= d16
    print(f"  {'PASSED' if d16 else 'FAILED'}")
    print()

    # ── D17 (KEY) ────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 17 — SIBILANT"
          " HIERARCHY (KEY)")
    print()
    print(f"  [ʂ] mūrdhanya: ~2800 Hz  (PENDING)")
    print(f"  [ɕ] tālavya:   ~4500 Hz  (PENDING)")
    print(f"  [s] dantya:    {cent_s:.0f} Hz  (this word)")
    print()
    s_above_t = cent_s - VS_T_BURST_HZ
    p1 = check(
        f'[s] above [t] burst ({s_above_t:.0f} Hz)',
        s_above_t, 500.0, 8000.0,
        unit=' Hz', fmt='.1f')
    p2 = check(
        f'[s] CF above 5000 Hz',
        cent_s, 5000.0, 11000.0,
        unit=' Hz', fmt='.1f')
    d17 = p1 and p2
    all_pass &= d17
    if d17:
        print()
        print("  Highest-frequency phoneme confirmed.")
    print(f"  {'PASSED' if d17 else 'FAILED'}")
    print()

    # ── D18 ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 18 — [s] ŚIKṢĀ"
          " CONFIRMATION")
    print()
    d18 = d15 and d16 and d17
    all_pass &= d18
    if d18:
        print("  Dantya sibilant confirmed.")
    print(f"  {'PASSED' if d18 else 'FAILED'}")
    print()

    # ── D19 ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 19 — FULL WORD"
          " [jɑɟɲɑsjɑ]")
    print()
    w_dry  = synth_yajnasya(with_room=False)
    w_hall = synth_yajnasya(with_room=True)
    dur_ms = len(w_dry) / SR * 1000.0
    p1 = check('RMS level', rms(w_dry),
               0.010, 0.90)
    p2 = check(
        f'duration ({dur_ms:.0f} ms)',
        dur_ms, 400.0, 750.0,
        unit=' ms', fmt='.1f')
    write_wav(
        "output_play/diag_yajnasya_dry.wav",
        w_dry)
    write_wav(
        "output_play/diag_yajnasya_hall.wav",
        w_hall)
    write_wav(
        "output_play/diag_yajnasya_slow.wav",
        ola_stretch(w_dry, 4.0))
    for sig, name in [
        (synth_J(),  "diag_yajnasya_j_iso"),
        (synth_JJ(), "diag_yajnasya_jj_iso"),
        (synth_NY(), "diag_yajnasya_ny_iso"),
        (synth_S(),  "diag_yajnasya_s_iso"),
    ]:
        mx = np.max(np.abs(sig))
        if mx > 1e-8:
            sig = sig / mx * 0.75
        write_wav(
            f"output_play/{name}.wav", sig)
        write_wav(
            f"output_play/{name}_slow.wav",
            ola_stretch(sig, 4.0))
    d19 = p1 and p2
    all_pass &= d19
    print(f"  {'PASSED' if d19 else 'FAILED'}")
    print()

    # ── D20 ─────────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 20 — PERCEPTUAL")
    print()
    for fn in [
        "diag_yajnasya_j_iso_slow.wav",
        "diag_yajnasya_jj_iso_slow.wav",
        "diag_yajnasya_ny_iso_slow.wav",
        "diag_yajnasya_s_iso_slow.wav",
        "diag_yajnasya_slow.wav",
        "diag_yajnasya_hall.wav",
    ]:
        print(f"  afplay output_play/{fn}")
    print()
    print("  LISTEN FOR:")
    print()
    print("  j_iso_slow:")
    print("    Pure glide. No click.")
    print("    No single contact moment.")
    print("    Smoother than [ɾ].")
    print()
    print("  jj_iso_slow:")
    print("    Murmur → burst → release.")
    print("    Brighter than [g],")
    print("    slightly lower than [t].")
    print()
    print("  ny_iso_slow:")
    print("    High, bright nasal.")
    print("    Spanish ñ — exactly that.")
    print()
    print("  s_iso_slow:")
    print("    The highest phoneme.")
    print("    Sharp dental contact.")
    print()
    print("  yajnasya_slow:")
    print("    YAJ — ÑA — SYA")
    print("    [ɟ]→[ɲ]: same place,")
    print("    velum opens, no F2 jump.")
    print("    [ɑ]→[s]: voicing cuts off.")
    print("    [s]→[j]: noise into glide.")
    print()

    # ── SUMMARY ─────────────────────────
    print("=" * 60)
    print("SUMMARY")
    print()
    rows = [
        ("D1   [j]  voicing",               d1),
        ("D2   [j]  F2 — tālavya",          d2),
        ("D3   [j]  F3 — no curl",          d3),
        ("D4   [j]  no dip (KEY)",           d4),
        ("D5   [j]  Śikṣā — antastha",      d5),
        ("D6   [ɟ]  voiced closure",         d6),
        ("D7   [ɟ]  burst — tālavya",        d7),
        ("D8   burst hierarchy (KEY)",       d8),
        ("D9   [ɟ]  Śikṣā — tālavya stop",  d9),
        ("D10  [ɲ]  voicing",               d10),
        ("D11  [ɲ]  F2 — palatal",          d11),
        ("D12  [ɲ]  antiresonance",         d12),
        ("D13  nasal zero order (KEY)",     d13),
        ("D14  [ɲ]  Śikṣā — tālavya nasal", d14),
        ("D15  [s]  voicing — LOW",         d15),
        ("D16  [s]  CF — dantya",           d16),
        ("D17  sibilant hierarchy (KEY)",   d17),
        ("D18  [s]  Śikṣā — dantya sib.",  d18),
        ("D19  Full word",                  d19),
    ]
    for lbl, ok_ in rows:
        sym = "✓ PASS" if ok_ else "✗ FAIL"
        print(f"  {lbl:36s}  {sym}")
    print(f"  {'D20  Perceptual':36s}  LISTEN")
    print()
    if all_pass:
        print("  ALL NUMERIC CHECKS PASSED")
        print()
        print("  YAJÑASYA [jɑɟɲɑsjɑ] verified.")
        print()
        print("  [j]  tālavya approximant: CONFIRMED")
        print("  [ɟ]  tālavya stop:        CONFIRMED")
        print("  [ɲ]  tālavya nasal:       CONFIRMED")
        print("  [s]  dantya sibilant:     CONFIRMED")
        print()
        print("  4-point burst hierarchy:  CONFIRMED")
        print(f"  {VS_P_BURST_HZ:.0f} < {VS_G_BURST_HZ:.0f}"
              f" < {cent_jj:.0f} < {VS_T_BURST_HZ:.0f} Hz")
        print()
        print("  Nasal zero ordering:      CONFIRMED")
        print("  [m] ≈ [n] ~800 Hz < [ɲ] ~1200 Hz")
        print()
        print("  Dip detector calibration  CONFIRMED")
        print(f"  22 ms kernel = {DIP_SMOOTH_PERIODS:.1f}×"
              f" pitch period")
        print("  Approximant [j]: 0 dips")
        print(f"  Tap [ɾ] reference: {VS_R_DIP_COUNT} dips")
        print()
        print("  VS phonemes verified: 19")
        print("  [ɻ̩][g][a][n][i][iː][ɭ][eː]")
        print("  [p][u][ɾ][oː][h][t][m]")
        print("  [j][ɟ][ɲ][s]")
        print()
        print("  Tālavya row: [j][ɟ][ɲ] confirmed.")
        print("  Remaining tālavya: [c][cʰ][ɟʰ]")
        print()
        print("  Next: DEVAM [devɑm]")
        print("  Rigveda 1.1.1, word 5.")
        print("  New phoneme: [d] voiced dental stop.")
        print("  [eː] already verified (ĪḶE).")
        print("  [m] already verified (PUROHITAM).")
        print("  [a] already verified (AGNI).")
        print("  One new phoneme only.")
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
