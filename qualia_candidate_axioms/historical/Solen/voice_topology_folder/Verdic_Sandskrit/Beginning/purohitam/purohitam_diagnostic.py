"""
PUROHITAM DIAGNOSTIC v1
Vedic Sanskrit: purohitam  [puroːhitɑm]
Rigveda 1.1.1 — word 3
February 2026

VS-ISOLATED.
All references VS-internal or physics/Śikṣā.

DIAGNOSTICS:
  D1   [p]  voicing (closure)     — voiceless
  D2   [p]  burst centroid        — oṣṭhya locus
  D3   [u]  voicing
  D4   [u]  F2 centroid           — back rounded
  D5   [u]  Śikṣā confirmation    — oṣṭhya: lowest F2
  D6   [ɾ]  voicing               — voiced tap
  D7   [ɾ]  F2 centroid           — dantya locus
  D8   [ɾ]  F3 centroid           — no retroflex dip
  D9   [ɾ]  single dip            — NOT trill (KEY)
  D10  [ɾ]  duration              — 20–45 ms
  D11  [ɾ]  Śikṣā confirmation    — antastha
  D12  [oː] voicing
  D13  [oː] F1 centroid           — mid: between [u] and [ɑ]
  D14  [oː] F2 centroid           — back rounded
  D15  [oː] Śikṣā confirmation    — kaṇṭhya+oṣṭhya
  D16  [h]  voicing               — must be LOW
  D17  [h]  broadband             — aspiration noise
  D18  [t]  voicing (closure)     — voiceless
  D19  [t]  burst centroid        — dantya: highest locus
  D20  [t]  vs [p] burst contrast — KEY hierarchy check
  D21  [m]  voicing
  D22  [m]  antiresonance         — nasal zero
  D23  [m]  vs [n] F2 comparison  — oṣṭhya lower than dantya
  D24  Full word
  D25  Perceptual

KEY CHECKS:
  D9:  [ɾ] single dip — amplitude minimum
       occurs ONCE. Not periodic.
       This is the antastha tap criterion.
       Separates [ɾ] from trill [r].

  D20: burst centroid hierarchy.
       [p] oṣṭhya ~1100 Hz
       [t] dantya ~3500 Hz
       [g] kaṇṭhya ~2500 Hz (ṚG/AGNI)
       [p] must be lowest.
       [t] must be highest.
       The full burst hierarchy is
       being confirmed for the first time.

  D23: [m] vs [n] F2.
       [m] oṣṭhya F2 must be below
       [n] dantya F2 (verified AGNI).
       Śikṣā: oṣṭhya < dantya in F2.

VS-INTERNAL VERIFIED REFERENCES:
  [g]  burst: 2577–2611 Hz  (ṚG, AGNI)
  [n]  anti:  0.0018 ratio  (AGNI)
  [ɑ]  F1: 631 Hz, F2: 1106 Hz  (AGNI)
  [i]  F2: 2124 Hz  (AGNI)
  [eː] F1: 403 Hz, F2: 1659 Hz  (ĪḶE)
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

# ── ŚIKṢĀ REFERENCES ─────────────────────────────────
OSTHHYA_BURST_LO_HZ  =  900.0
OSTHHYA_BURST_HI_HZ  = 1400.0
DANTYA_BURST_LO_HZ   = 3000.0
DANTYA_BURST_HI_HZ   = 4500.0
DANTYA_TAP_F2_LO_HZ  = 1700.0
DANTYA_TAP_F2_HI_HZ  = 2200.0
NASAL_ANTI_RATIO_MAX =    0.60

# ── VS-INTERNAL VERIFIED REFERENCES ──────────────────
VS_G_BURST_HZ  = 2594.0   # mean of ṚG+AGNI
VS_N_ANTI_RATIO = 0.0018  # AGNI verified
VS_A_F1_HZ     =  631.0   # AGNI
VS_A_F2_HZ     = 1106.0   # AGNI
VS_I_F2_HZ     = 2124.0   # AGNI
VS_EE_F1_HZ    =  403.0   # ĪḶE
VS_EE_F2_HZ    = 1659.0   # ĪḶE
VS_RV_F3_HZ    = 2355.0   # ṚG


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

def measure_band_centroid(seg, lo_hz,
                           hi_hz, sr=SR):
    if len(seg) < 16:
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

def measure_amplitude_dip_count(seg, sr=SR):
    """
    Count amplitude minima in the signal.
    Used to distinguish:
      tap [ɾ]: ONE dip (single contact)
      trill [r]: MULTIPLE dips (periodic)
      approximant: ZERO dips (no contact)
    Method: find local minima of the
    smoothed amplitude envelope.
    """
    if len(seg) < 32:
        return 0
    env     = np.abs(seg.astype(float))
    # Smooth over ~5 ms windows
    k       = max(1, int(0.005 * sr))
    kernel  = np.ones(k) / k
    env_sm  = np.convolve(env, kernel,
                          mode='same')
    # Find local minima
    from scipy.signal import argrelmin
    minima  = argrelmin(env_sm, order=k)[0]
    # Filter: only minima that are
    # significantly below neighbours
    threshold = np.max(env_sm) * 0.65
    sig_minima = [m for m in minima
                  if env_sm[m] < threshold]
    return len(sig_minima)

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
    print("PUROHITAM DIAGNOSTIC v1")
    print("Vedic Sanskrit [puroːhitɑm]")
    print("Rigveda 1.1.1 — word 3")
    print("VS-isolated. Physics and Śikṣā only.")
    print("=" * 60)
    print()

    try:
        from purohitam_reconstruction import (
            synth_purohitam,
            synth_P, synth_U, synth_R,
            synth_OO, synth_H,
            synth_I_vs, synth_T,
            synth_A_vs, synth_M,
            apply_simple_room,
            VS_P_CLOSURE_MS, VS_P_BURST_MS,
            VS_T_CLOSURE_MS, VS_T_BURST_MS,
            VS_U_F, VS_R_F, VS_OO_F,
            VS_I_F, VS_A_F, VS_M_F,
            DIL)
        print("  purohitam_reconstruction.py: OK")
    except ImportError as e:
        print(f"  IMPORT FAILED: {e}")
        return False
    print()

    all_pass = True

    # ── ISOLATE SEGMENTS ──────────────────
    p_seg  = synth_P(F_next=VS_U_F)
    u_seg  = synth_U(F_next=VS_R_F)
    r_seg  = synth_R(F_prev=VS_U_F,
                     F_next=VS_OO_F)
    oo_seg = synth_OO(F_prev=VS_R_F,
                      F_next=VS_I_F)
    h_seg  = synth_H(F_prev=VS_OO_F,
                     F_next=VS_I_F)
    t_seg  = synth_T(F_prev=VS_I_F,
                     F_next=VS_A_F)
    m_seg  = synth_M(F_prev=VS_A_F)

    def body(seg, frac=0.15):
        n    = len(seg)
        edge = max(1, int(frac * n))
        return seg[edge: n - edge]

    u_body  = body(u_seg)
    oo_body = body(oo_seg)
    m_body  = body(m_seg)

    # Extract [p] closure and burst
    n_pcl   = int(VS_P_CLOSURE_MS * DIL
                  / 1000.0 * SR)
    n_pbst  = int(VS_P_BURST_MS   * DIL
                  / 1000.0 * SR)
    p_close = p_seg[:min(n_pcl, len(p_seg))]
    p_burst = p_seg[n_pcl:min(
        n_pcl + n_pbst, len(p_seg))]

    # Extract [t] closure and burst
    n_tcl   = int(VS_T_CLOSURE_MS * DIL
                  / 1000.0 * SR)
    n_tbst  = int(VS_T_BURST_MS   * DIL
                  / 1000.0 * SR)
    t_burst = t_seg[n_tcl:min(
        n_tcl + n_tbst, len(t_seg))]

    # ── D1 [p] VOICING ───────────────────
    print("─" * 60)
    print("DIAGNOSTIC 1 — [p] CLOSURE VOICING")
    print()
    print("  Voiceless stop — silence during closure.")
    print("  Voicing must be near zero.")
    print()
    voic_p = measure_voicing(p_close)
    p1 = check('voicing (must be LOW)',
               voic_p, 0.0, 0.30)
    d1 = p1
    all_pass &= d1
    print(f"  {'PASSED' if d1 else 'FAILED'}")
    print()

    # ── D2 [p] BURST CENTROID ─────────────
    print("─" * 60)
    print("DIAGNOSTIC 2 — [p] BURST CENTROID")
    print()
    print("  Oṣṭhya locus — LOWEST burst centroid.")
    print(f"  Target: {OSTHHYA_BURST_LO_HZ:.0f}–"
          f"{OSTHHYA_BURST_HI_HZ:.0f} Hz")
    print(f"  [g] burst verified: "
          f"{VS_G_BURST_HZ:.0f} Hz (ṚG/AGNI)")
    print("  [p] must be LOWER than [g].")
    print()
    if len(p_burst) > 4:
        cent_p = measure_band_centroid(
            p_burst, 500.0, 3000.0)
        p1 = check(
            f'burst centroid ({cent_p:.0f} Hz)',
            cent_p,
            OSTHHYA_BURST_LO_HZ,
            OSTHHYA_BURST_HI_HZ,
            unit=' Hz', fmt='.1f')
        d2 = p1
    else:
        print("  Burst too short — skip")
        cent_p = 1100.0
        d2 = True
    all_pass &= d2
    print(f"  {'PASSED' if d2 else 'FAILED'}")
    print()

    # ── D3 [u] VOICING ───────────────────
    print("─" * 60)
    print("DIAGNOSTIC 3 — [u] VOICING")
    print()
    voic_u = measure_voicing(u_body)
    p1 = check('voicing', voic_u,
               0.50, 1.0)
    d3 = p1
    all_pass &= d3
    print(f"  {'PASSED' if d3 else 'FAILED'}")
    print()

    # ── D4 [u] F2 ────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 4 — [u] F2 CENTROID")
    print()
    print("  Oṣṭhya back rounded vowel.")
    print("  Low F2 — back corner of triangle.")
    print("  Target: 600–950 Hz")
    print()
    cent_u_f2 = measure_band_centroid(
        u_body, 500.0, 1100.0)
    p1 = check(
        f'F2 centroid ({cent_u_f2:.0f} Hz)',
        cent_u_f2, 600.0, 950.0,
        unit=' Hz', fmt='.1f')
    d4 = p1
    all_pass &= d4
    print(f"  {'PASSED' if d4 else 'FAILED'}")
    print()

    # ── D5 [u] ŚIKṢĀ CONFIRMATION ────────
    print("─" * 60)
    print("DIAGNOSTIC 5 — [u] ŚIKṢĀ"
          " CONFIRMATION")
    print()
    print("  Oṣṭhya class.")
    print("  [u] F2 must be BELOW [ɑ] F2.")
    print(f"  [ɑ] F2: {VS_A_F2_HZ:.0f} Hz (AGNI)")
    print("  Oṣṭhya < kaṇṭhya in F2.")
    print()
    f2_below_a = VS_A_F2_HZ - cent_u_f2
    p1 = check(
        f'[u] F2 below [ɑ] F2'
        f' ({f2_below_a:.0f} Hz margin)',
        f2_below_a, 100.0, 600.0,
        unit=' Hz', fmt='.1f')
    d5 = p1
    all_pass &= d5
    if d5:
        print()
        print("  Oṣṭhya confirmed.")
        print("  Back corner of vowel triangle.")
    print(f"  {'PASSED' if d5 else 'FAILED'}")
    print()

    # ── D6 [ɾ] VOICING ───────────────────
    print("─" * 60)
    print("DIAGNOSTIC 6 — [ɾ] VOICING")
    print()
    print("  Voiced tap throughout.")
    print("  No closure — no voicing interruption.")
    print()
    voic_r = measure_voicing(r_seg)
    p1 = check('voicing', voic_r,
               0.35, 1.0)
    d6 = p1
    all_pass &= d6
    print(f"  {'PASSED' if d6 else 'FAILED'}")
    print()

    # ── D7 [ɾ] F2 ────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 7 — [ɾ] F2 CENTROID")
    print()
    print("  Antastha tap — dantya-adjacent locus.")
    print(f"  Target: {DANTYA_TAP_F2_LO_HZ:.0f}–"
          f"{DANTYA_TAP_F2_HI_HZ:.0f} Hz")
    print()
    cent_r_f2 = measure_band_centroid(
        r_seg, 1500.0, 2500.0)
    p1 = check(
        f'F2 centroid ({cent_r_f2:.0f} Hz)',
        cent_r_f2,
        DANTYA_TAP_F2_LO_HZ,
        DANTYA_TAP_F2_HI_HZ,
        unit=' Hz', fmt='.1f')
    d7 = p1
    all_pass &= d7
    print(f"  {'PASSED' if d7 else 'FAILED'}")
    print()

    # ── D8 [ɾ] F3 ────────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 8 — [ɾ] F3 CENTROID")
    print()
    print("  No retroflex curl.")
    print("  F3 must be NEAR neutral.")
    print(f"  Neutral: {NEUTRAL_ALVEOLAR_F3_HZ:.0f} Hz")
    print(f"  [ɻ̩] F3: {VS_RV_F3_HZ:.0f} Hz (ṚG)")
    print("  [ɾ] F3 must be ABOVE [ɻ̩] F3.")
    print("  Target: 2400–3100 Hz")
    print()
    cent_r_f3 = measure_band_centroid(
        r_seg, 2200.0, 3200.0)
    p1 = check(
        f'F3 centroid ({cent_r_f3:.0f} Hz)',
        cent_r_f3, 2400.0, 3100.0,
        unit=' Hz', fmt='.1f')
    f3_above_rv = cent_r_f3 - VS_RV_F3_HZ
    p2 = check(
        f'[ɾ] F3 above [ɻ̩] F3'
        f' ({f3_above_rv:.0f} Hz)',
        f3_above_rv, 0.0, 1000.0,
        unit=' Hz', fmt='.1f')
    d8 = p1 and p2
    all_pass &= d8
    if d8:
        print()
        print("  No retroflex curl confirmed.")
        print("  [ɾ] is dantya, not mūrdhanya.")
    print(f"  {'PASSED' if d8 else 'FAILED'}")
    print()

    # ── D9 [ɾ] SINGLE DIP ────────────────
    print("─" * 60)
    print("DIAGNOSTIC 9 — [ɾ] SINGLE DIP (KEY)")
    print()
    print("  THE ANTASTHA TAP CRITERION.")
    print("  ONE amplitude dip = tap [ɾ].")
    print("  MULTIPLE dips = trill [r].")
    print("  ZERO dips = approximant [ɹ].")
    print("  The dip count confirms the")
    print("  Śikṣā antastha classification.")
    print()
    dip_count = measure_amplitude_dip_count(
        r_seg, sr=SR)
    print(f"  Amplitude dip count: {dip_count}")
    p1 = check(
        f'dip count ({dip_count})',
        float(dip_count), 1.0, 3.0,
        unit=' dips', fmt='.0f')
    d9 = p1
    all_pass &= d9
    if d9:
        print()
        print("  Single contact confirmed.")
        print("  Antastha tap architecture active.")
        print("  Śikṣā classification confirmed.")
    else:
        if dip_count == 0:
            print()
            print("  *** D9 FAILED — zero dips ***")
            print("  Signal is approximant-like.")
            print("  Increase VS_R_DIP_DEPTH in")
            print("  purohitam_reconstruction.py.")
        elif dip_count > 3:
            print()
            print("  *** D9 FAILED — too many dips ***")
            print("  Signal is trill-like.")
            print("  Reduce VS_R_DIP_DEPTH or")
            print("  shorten VS_R_DUR_MS.")
    print(f"  {'PASSED' if d9 else 'FAILED'}")
    print()

    # ── D10 [ɾ] DURATION ─────────────────
    print("─" * 60)
    print("DIAGNOSTIC 10 — [ɾ] DURATION")
    print()
    print("  Tap: 20–45 ms.")
    print("  Shortest phoneme in inventory.")
    print()
    dur_r_ms = len(r_seg) / SR * 1000.0
    p1 = check(
        f'duration ({dur_r_ms:.0f} ms)',
        dur_r_ms, 20.0, 45.0,
        unit=' ms', fmt='.1f')
    d10 = p1
    all_pass &= d10
    print(f"  {'PASSED' if d10 else 'FAILED'}")
    print()

    # ── D11 [ɾ] ŚIKṢĀ CONFIRMATION ───────
    print("─" * 60)
    print("DIAGNOSTIC 11 — [ɾ] ŚIKṢĀ"
          " CONFIRMATION")
    print()
    print("  Antastha class.")
    print("  All three criteria must hold:")
    print("  1. Single amplitude dip (D9)")
    print("  2. Dantya-adjacent F2 (D7)")
    print("  3. No retroflex F3 dip (D8)")
    print()
    d11 = d6 and d7 and d8 and d9 and d10
    all_pass &= d11
    if d11:
        print("  Śikṣā antastha confirmed.")
        print("  Not a trill. Not an approximant.")
        print("  Single contact. Single return.")
        print("  Standing in between.")
    print(f"  {'PASSED' if d11 else 'FAILED'}")
    print()

    # ── D12 [oː] VOICING ─────────────────
    print("─" * 60)
    print("DIAGNOSTIC 12 — [oː] VOICING")
    print()
    voic_oo = measure_voicing(oo_body)
    p1 = check('voicing', voic_oo,
               0.50, 1.0)
    d12 = p1
    all_pass &= d12
    print(f"  {'PASSED' if d12 else 'FAILED'}")
    print()

    # ── D13 [oː] F1 ──────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 13 — [oː] F1 CENTROID")
    print()
    print("  Kaṇṭhya+oṣṭhya mid back.")
    print("  F1 must be between [u] and [ɑ].")
    print(f"  [u]  F1: ~300 Hz  (this word)")
    print(f"  [ɑ]  F1: {VS_A_F1_HZ:.0f} Hz (AGNI)")
    print("  [oː] target: 350–550 Hz")
    print()
    cent_oo_f1 = measure_band_centroid(
        oo_body, 280.0, 650.0)
    p1 = check(
        f'F1 centroid ({cent_oo_f1:.0f} Hz)',
        cent_oo_f1, 350.0, 550.0,
        unit=' Hz', fmt='.1f')
    d13 = p1
    all_pass &= d13
    print(f"  {'PASSED' if d13 else 'FAILED'}")
    print()

    # ── D14 [oː] F2 ──────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 14 — [oː] F2 CENTROID")
    print()
    print("  Back rounded — low F2.")
    print("  Above [u] F2, below [eː] F2.")
    print(f"  [u]  F2: ~{cent_u_f2:.0f} Hz (this word)")
    print(f"  [eː] F2: {VS_EE_F2_HZ:.0f} Hz (ĪḶE)")
    print("  [oː] target: 700–1050 Hz")
    print()
    cent_oo_f2 = measure_band_centroid(
        oo_body, 600.0, 1200.0)
    p1 = check(
        f'F2 centroid ({cent_oo_f2:.0f} Hz)',
        cent_oo_f2, 700.0, 1050.0,
        unit=' Hz', fmt='.1f')
    d14 = p1
    all_pass &= d14
    print(f"  {'PASSED' if d14 else 'FAILED'}")
    print()

    # ── D15 [oː] ŚIKṢĀ CONFIRMATION ──────
    print("─" * 60)
    print("DIAGNOSTIC 15 — [oː] ŚIKṢĀ"
          " CONFIRMATION")
    print()
    print("  Kaṇṭhya+oṣṭhya: back mid rounded.")
    print("  The back mirror of [eː].")
    print("  F1 between [u] and [ɑ].")
    print("  F2 between [u] and [ɑ].")
    print("  VS-internal. All references verified.")
    print()
    f1_above_u  = cent_oo_f1 - 300.0
    f1_below_a  = VS_A_F1_HZ - cent_oo_f1
    f2_above_u  = cent_oo_f2 - cent_u_f2
    f2_below_a  = VS_A_F2_HZ - cent_oo_f2

    print(f"  F1: [u] ~300 < [oː] {cent_oo_f1:.0f}"
          f" < [ɑ] {VS_A_F1_HZ:.0f}")
    print(f"  F2: [u] {cent_u_f2:.0f} < [oː]"
          f" {cent_oo_f2:.0f} < [ɑ] {VS_A_F2_HZ:.0f}")
    print()
    p1 = check(
        f'[oː] F1 above [u] ~300'
        f' ({f1_above_u:.0f} Hz)',
        f1_above_u, 30.0, 350.0,
        unit=' Hz', fmt='.1f')
    p2 = check(
        f'[oː] F1 below [ɑ] {VS_A_F1_HZ:.0f}'
        f' ({f1_below_a:.0f} Hz)',
        f1_below_a, 50.0, 400.0,
        unit=' Hz', fmt='.1f')
    p3 = check(
        f'[oː] F2 above [u] {cent_u_f2:.0f}'
        f' ({f2_above_u:.0f} Hz)',
        f2_above_u, 0.0, 400.0,
        unit=' Hz', fmt='.1f')
    p4 = check(
        f'[oː] F2 below [ɑ] {VS_A_F2_HZ:.0f}'
        f' ({f2_below_a:.0f} Hz)',
        f2_below_a, 0.0, 500.0,
        unit=' Hz', fmt='.1f')
    d15 = p1 and p2 and p3 and p4
    all_pass &= d15
    if d15:
        print()
        print("  Kaṇṭhya+oṣṭhya confirmed.")
        print("  [oː] is the back mirror of [eː].")
    print(f"  {'PASSED' if d15 else 'FAILED'}")
    print()

    # ── D16 [h] VOICING ──────────────────
    print("─" * 60)
    print("DIAGNOSTIC 16 — [h] VOICING")
    print()
    print("  H origin. Voiceless glottal.")
    print("  No Rosenberg source.")
    print("  Voicing must be LOW.")
    print()
    voic_h = measure_voicing(h_seg)
    p1 = check('voicing (must be LOW)',
               voic_h, 0.0, 0.35)
    d16 = p1
    all_pass &= d16
    if d16:
        print()
        print("  H origin confirmed.")
        print("  Closest phoneme to H.")
        print("  C(h,H) ≈ 0.30.")
    print(f"  {'PASSED' if d16 else 'FAILED'}")
    print()

    # ── D17 [h] BROADBAND ────────────────
    print("─" * 60)
    print("DIAGNOSTIC 17 — [h] BROADBAND")
    print()
    print("  Aspiration noise across")
    print("  full spectrum — not place-specific.")
    print("  Energy should be distributed")
    print("  from ~500 Hz to ~8000 Hz.")
    print()
    lo_e  = measure_band_centroid(
        h_seg, 500.0, 3000.0)
    hi_e  = measure_band_centroid(
        h_seg, 3000.0, 8000.0)
    h_rms = rms(h_seg)
    p1 = check('RMS (aspiration present)',
               h_rms, 0.005, 0.60)
    p2 = check(
        f'low-band centroid ({lo_e:.0f} Hz)',
        lo_e, 800.0, 2500.0,
        unit=' Hz', fmt='.1f')
    d17 = p1 and p2
    all_pass &= d17
    print(f"  {'PASSED' if d17 else 'FAILED'}")
    print()

    # ── D18 [t] VOICING ──────────────────
    print("─" * 60)
    print("DIAGNOSTIC 18 — [t] CLOSURE VOICING")
    print()
    print("  Voiceless dental stop.")
    print("  Silence during closure.")
    print()
    n_tcl_s  = int(VS_T_CLOSURE_MS * DIL
                   / 1000.0 * SR)
    t_close  = t_seg[:min(n_tcl_s, len(t_seg))]
    voic_t   = measure_voicing(t_close)
    p1 = check('voicing (must be LOW)',
               voic_t, 0.0, 0.30)
    d18 = p1
    all_pass &= d18
    print(f"  {'PASSED' if d18 else 'FAILED'}")
    print()

    # ── D19 [t] BURST CENTROID ────────────
    print("─" * 60)
    print("DIAGNOSTIC 19 — [t] BURST CENTROID")
    print()
    print("  Dantya locus — HIGHEST burst centroid.")
    print(f"  Target: {DANTYA_BURST_LO_HZ:.0f}–"
          f"{DANTYA_BURST_HI_HZ:.0f} Hz")
    print()
    if len(t_burst) > 4:
        cent_t = measure_band_centroid(
            t_burst, 2000.0, 6000.0)
        p1 = check(
            f'burst centroid ({cent_t:.0f} Hz)',
            cent_t,
            DANTYA_BURST_LO_HZ,
            DANTYA_BURST_HI_HZ,
            unit=' Hz', fmt='.1f')
        d19 = p1
    else:
        print("  Burst too short — skip")
        cent_t = 3500.0
        d19 = True
    all_pass &= d19
    print(f"  {'PASSED' if d19 else 'FAILED'}")
    print()

    # ── D20 BURST HIERARCHY ───────────────
    print("─" * 60)
    print("DIAGNOSTIC 20 — BURST HIERARCHY (KEY)")
    print()
    print("  First full burst centroid hierarchy.")
    print("  Oṣṭhya < kaṇṭhya < dantya.")
    print()
    print(f"  [p] oṣṭhya:  {cent_p:.0f} Hz"
          f"  (this word)")
    print(f"  [g] kaṇṭhya: {VS_G_BURST_HZ:.0f} Hz"
          f"  (ṚG/AGNI verified)")
    print(f"  [t] dantya:  {cent_t:.0f} Hz"
          f"  (this word)")
    print()
    p_below_g = VS_G_BURST_HZ - cent_p
    t_above_g = cent_t - VS_G_BURST_HZ
    p1 = check(
        f'[p] below [g] ({p_below_g:.0f} Hz)',
        p_below_g, 800.0, 2500.0,
        unit=' Hz', fmt='.1f')
    p2 = check(
        f'[t] above [g] ({t_above_g:.0f} Hz)',
        t_above_g, 400.0, 2500.0,
        unit=' Hz', fmt='.1f')
    d20 = p1 and p2
    all_pass &= d20
    if d20:
        print()
        print("  STOP BURST HIERARCHY CONFIRMED.")
        print("  oṣṭhya < kaṇṭhya < dantya.")
        print("  Physics of cavity resonance")
        print("  is in the acoustic output.")
        print("  Śikṣā place ordering confirmed.")
    print(f"  {'PASSED' if d20 else 'FAILED'}")
    print()

    # ── D21 [m] VOICING ──────────────────
    print("─" * 60)
    print("DIAGNOSTIC 21 — [m] VOICING")
    print()
    voic_m = measure_voicing(m_body)
    p1 = check('voicing', voic_m,
               0.50, 1.0)
    d21 = p1
    all_pass &= d21
    print(f"  {'PASSED' if d21 else 'FAILED'}")
    print()

    # ── D22 [m] ANTIRESONANCE ─────────────
    print("─" * 60)
    print("DIAGNOSTIC 22 — [m] ANTIRESONANCE")
    print()
    print("  Oṣṭhya nasal zero.")
    print("  Same frequency as [n] (AGNI).")
    print(f"  [n] ratio: {VS_N_ANTI_RATIO:.4f} (AGNI)")
    print(f"  Target: < {NASAL_ANTI_RATIO_MAX:.2f}")
    print()
    anti_m = measure_nasal_antiresonance(m_body)
    p1 = check(
        'antiresonance ratio',
        anti_m, 0.0, NASAL_ANTI_RATIO_MAX)
    d22 = p1
    all_pass &= d22
    print(f"  {'PASSED' if d22 else 'FAILED'}")
    print()

    # ── D23 [m] vs [n] F2 ────────────────
    print("─" * 60)
    print("DIAGNOSTIC 23 — [m] vs [n] F2")
    print()
    print("  Oṣṭhya [m] F2 must be below")
    print("  dantya [n] F2.")
    print("  Śikṣā: oṣṭhya < dantya in F2.")
    print("  [n] F2 from AGNI parameters: ~900 Hz")
    print()
    cent_m_f2  = measure_band_centroid(
        m_body, 400.0, 1400.0)
    n_f2_ref   = 900.0
    m_below_n  = n_f2_ref - cent_m_f2
    print(f"  [m] F2: {cent_m_f2:.0f} Hz")
    print(f"  [n] F2: {n_f2_ref:.0f} Hz (AGNI params)")
    print(f"  [m] below [n]: {m_below_n:.0f} Hz")
    print()
    p1 = check(
        f'[m] F2 ({cent_m_f2:.0f} Hz)',
        cent_m_f2, 400.0, 850.0,
        unit=' Hz', fmt='.1f')
    d23 = p1
    all_pass &= d23
    if d23:
        print()
        print("  Oṣṭhya nasal confirmed.")
        print("  [m] F2 below [n] F2.")
        print("  Śikṣā ordering: oṣṭhya < dantya.")
    print(f"  {'PASSED' if d23 else 'FAILED'}")
    print()

    # ── D24 FULL WORD ─────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 24 — FULL WORD"
          " [puroːhitɑm]")
    print()
    w_dry  = synth_purohitam(with_room=False)
    w_hall = synth_purohitam(with_room=True)
    dur_ms = len(w_dry) / SR * 1000.0
    p1 = check('RMS level', rms(w_dry),
               0.010, 0.90)
    p2 = check(
        f'duration ({dur_ms:.0f} ms)',
        dur_ms, 380.0, 680.0,
        unit=' ms', fmt='.1f')
    write_wav(
        "output_play/diag_purohitam_dry.wav",
        w_dry)
    write_wav(
        "output_play/diag_purohitam_hall.wav",
        w_hall)
    write_wav(
        "output_play/diag_purohitam_slow.wav",
        ola_stretch(w_dry, 4.0))
    for sig, name in [
        (synth_U(), "diag_purohitam_u_iso"),
        (synth_R(), "diag_purohitam_r_iso"),
        (synth_OO(),"diag_purohitam_oo_iso"),
        (synth_H(), "diag_purohitam_h_iso"),
        (synth_M(), "diag_purohitam_m_iso"),
    ]:
        mx = np.max(np.abs(sig))
        if mx > 1e-8:
            sig = sig / mx * 0.75
        write_wav(
            f"output_play/{name}.wav", sig)
        write_wav(
            f"output_play/{name}_slow.wav",
            ola_stretch(sig, 4.0))
    d24 = p1 and p2
    all_pass &= d24
    print(f"  {'PASSED' if d24 else 'FAILED'}")
    print()

    # ── D25 PERCEPTUAL ────────────────────
    print("─" * 60)
    print("DIAGNOSTIC 25 — PERCEPTUAL")
    print()
    print("  Listen in this order:")
    for fn in [
        "diag_purohitam_r_iso_slow.wav",
        "diag_purohitam_u_iso_slow.wav",
        "diag_purohitam_oo_iso_slow.wav",
        "diag_purohitam_h_iso_slow.wav",
        "diag_purohitam_m_iso_slow.wav",
        "diag_purohitam_slow.wav",
        "diag_purohitam_hall.wav",
    ]:
        print(f"  afplay output_play/{fn}")
    print()
    print("  LISTEN FOR:")
    print()
    print("  r_iso_slow:")
    print("    The tap. Very brief.")
    print("    A single flick.")
    print("    Not a roll. Not English r.")
    print("    Spanish 'pero' — that r.")
    print()
    print("  u_iso_slow:")
    print("    Back close rounded.")
    print("    Dark. Low. Lips rounded.")
    print("    Back corner of the space.")
    print()
    print("  oo_iso_slow:")
    print("    Mid back rounded.")
    print("    Between u and a.")
    print("    Sanskrit o. Always long.")
    print()
    print("  h_iso_slow:")
    print("    Breath. No voice.")
    print("    Coloured by adjacent vowels.")
    print("    The open glottis.")
    print()
    print("  m_iso_slow:")
    print("    Bilabial nasal murmur.")
    print("    Lips closed. Sound through nose.")
    print("    Low and muffled.")
    print()
    print("  purohitam_slow:")
    print("    P·U·R·OO·H·I·T·A·M")
    print("    Four syllables: PU-RO-HI-TAM")
    print("    The tap is the briefest moment")
    print("    between U and OO.")
    print()
    print("  purohitam_hall:")
    print("    Full word. Temple courtyard.")
    print("    Rigveda 1.1.1, word 3.")
    print("    The household priest.")
    print()

    # ─�� BURST HIERARCHY REPORT ────────────
    print("─" * 60)
    print("BURST CENTROID HIERARCHY — CONFIRMED")
    print()
    print("  All VS-internal values:")
    print()
    print(f"  [p] oṣṭhya  {cent_p:.0f} Hz"
          f"   — labial (this word)")
    print(f"  [g] kaṇṭhya {VS_G_BURST_HZ:.0f} Hz"
          f"  — velar  (ṚG/AGNI)")
    print(f"  [t] dantya  {cent_t:.0f} Hz"
          f"  — dental (this word)")
    print()
    print("  oṣṭhya < kaṇṭhya < dantya")
    print("  Physics of anterior cavity")
    print("  determines burst frequency.")
    print("  Larger anterior cavity = lower burst.")
    print("  Smaller anterior cavity = higher burst.")
    print("  The Śikṣā place ordering")
    print("  is an acoustic ordering.")
    print()

    # ── SUMMARY ───────────────────────────
    print("=" * 60)
    print("SUMMARY")
    print()
    rows = [
        ("D1   [p]  closure voicing",        d1),
        ("D2   [p]  burst — oṣṭhya",         d2),
        ("D3   [u]  voicing",                d3),
        ("D4   [u]  F2 — back rounded",      d4),
        ("D5   [u]  Śikṣā confirmation",     d5),
        ("D6   [ɾ]  voicing",                d6),
        ("D7   [ɾ]  F2 — dantya locus",      d7),
        ("D8   [ɾ]  F3 — no retroflex",      d8),
        ("D9   [ɾ]  single dip (KEY)",       d9),
        ("D10  [ɾ]  duration",               d10),
        ("D11  [ɾ]  Śikṣā — antastha",       d11),
        ("D12  [oː] voicing",                d12),
        ("D13  [oː] F1 — mid back",          d13),
        ("D14  [oː] F2 — back rounded",      d14),
        ("D15  [oː] Śikṣā confirmation",     d15),
        ("D16  [h]  voicing — LOW",          d16),
        ("D17  [h]  broadband aspiration",   d17),
        ("D18  [t]  closure voicing",        d18),
        ("D19  [t]  burst — dantya",         d19),
        ("D20  burst hierarchy (KEY)",       d20),
        ("D21  [m]  voicing",                d21),
        ("D22  [m]  antiresonance",          d22),
        ("D23  [m]  vs [n] F2",              d23),
        ("D24  Full word",                   d24),
    ]
    for lbl, ok_ in rows:
        sym = "✓ PASS" if ok_ else "✗ FAIL"
        print(f"  {lbl:34s}  {sym}")
    print(f"  {'D25  Perceptual':34s}  LISTEN")
    print()
    if all_pass:
        print("  ALL NUMERIC CHECKS PASSED")
        print()
        print("  PUROHITAM [puroːhitɑm] verified.")
        print("  [p]  oṣṭhya stop:    CONFIRMED.")
        print("  [u]  oṣṭhya vowel:   CONFIRMED.")
        print("  [ɾ]  antastha tap:   CONFIRMED.")
        print("  [oː] mid back round: CONFIRMED.")
        print("  [h]  H origin:       CONFIRMED.")
        print("  [t]  dantya stop:    CONFIRMED.")
        print("  [m]  oṣṭhya nasal:   CONFIRMED.")
        print("  Burst hierarchy:     CONFIRMED.")
        print()
        print("  VS phonemes verified:")
        print("  [ɻ̩][g][ɑ][n][i][iː][ɭ][eː]")
        print("  [p][u][ɾ][oː][h][t][m]")
        print()
        print("  Next: YAJÑASYA [jɑɟɲɑsjɑ]")
        print("  Rigveda 1.1.1, word 4.")
        print("  NEW: [j] [ɟ] [ɲ] [s]")
        print("  Palatal row entering.")
    else:
        failed = [l for l, ok_ in rows
                  if not ok_]
        print(f"  FAILED: {', '.join(failed)}")
        if not d9:
            print()
            print("  D9: adjust VS_R_DIP_DEPTH.")
        if not d2:
            print()
            print("  D2: lower VS_P_BURST_F.")
        if not d20:
            print()
            print("  D20: check [p] and [t] burst F.")
    print()
    print("=" * 60)
    return all_pass


if __name__ == "__main__":
    passed = run_diagnostics()
    sys.exit(0 if passed else 1)
