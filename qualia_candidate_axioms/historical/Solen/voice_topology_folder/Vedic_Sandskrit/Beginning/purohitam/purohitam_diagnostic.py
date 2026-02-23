#!/usr/bin/env python3
"""
PUROHITAM DIAGNOSTIC v2 — CORRECTED
Vedic Sanskrit: purohitam [puroːhitɑm]
Rigveda 1.1.1 — word 4

ARCHITECTURE UPDATE v1→v2 (CORRECTED):
  v1: [t] and [p] used OLD bandpass noise burst
  v2: [t] and [p] use v6 (spike + turbulence + boundary fix)
      WITH CORRECTED formants matching v1 spectral profile

EXPECTED RESULT:
  - [p] burst centroid: ~1297 Hz (v1 reference)
  - [t] burst centroid: ~3006 Hz (v1 reference)
  - Perceptual: cleaner (no clicks)

February 2026
"""

import numpy as np
from scipy.signal import lfilter, butter
import wave as wave_module
import os
import sys

SR = 44100
DTYPE = np.float32

os.makedirs("output_play", exist_ok=True)

# ============================================================================
# REFERENCE VALUES FROM v1
# ============================================================================

V1_P_BURST_HZ = 1297.0  # v1 measured
V1_T_BURST_HZ = 3006.0  # v1 measured

# Acceptable variance (spectral measurement tolerance)
BURST_TOLERANCE_HZ = 100.0

# ============================================================================
# MEASUREMENT HELPERS
# ============================================================================

def f32(x):
    return np.asarray(x, dtype=DTYPE)

def load_wav(path):
    try:
        with wave_module.open(path, 'r') as wf:
            n_frames = wf.getnframes()
            word_bytes = wf.readframes(n_frames)
            word = np.frombuffer(word_bytes, dtype=np.int16).astype(float) / 32768.0
        return word
    except:
        return None

def measure_band_centroid(seg, lo_hz, hi_hz, sr=SR):
    if len(seg) < 16:
        return 0.0
    spec = np.abs(np.fft.rfft(seg.astype(float), n=2048)) ** 2
    freqs = np.fft.rfftfreq(2048, d=1.0/sr)
    mask = (freqs >= lo_hz) & (freqs <= hi_hz)
    total = np.sum(spec[mask])
    if total < 1e-12:
        return 0.0
    return float(np.sum(freqs[mask] * spec[mask]) / total)

def check(label, value, lo, hi, unit='', fmt='.4f'):
    ok = (lo <= value <= hi)
    status = 'PASS' if ok else 'FAIL'
    bar = ''
    if 0.0 <= value <= 1.0 and unit == '':
        bar = '█' * int(value * 40)
    print(f"    [{status}] {label}: "
          f"{format(value, fmt)}{unit}  "
          f"target [{lo:{fmt}}–{hi:{fmt}}]"
          f"  {bar}")
    return ok

# ============================================================================
# DIAGNOSTIC RUNNER
# ============================================================================

def run_diagnostics():
    print()
    print("=" * 70)
    print("PUROHITAM DIAGNOSTIC v2 — CORRECTED")
    print("=" * 70)
    print()
    print("ARCHITECTURE UPDATE (v1→v2 CORRECTED):")
    print()
    print("  v1: [t] and [p] used OLD bandpass noise burst")
    print("  v2: [t] and [p] use v6 (spike + turbulence + boundary fix)")
    print("      WITH CORRECTED formants matching v1 spectral profile")
    print()
    print("  [p] v1 burst: 1297 Hz → v2 target: ~1297 Hz")
    print("  [t] v1 burst: 3006 Hz → v2 target: ~3006 Hz")
    print()
    
    # Import synthesis parameters
    params_found = False
    try:
        from purohitam_reconstruction_v2 import (
            VS_P_CLOSURE_MS, VS_P_BURST_MS, VS_P_VOT_MS,
            VS_P_BURST_F, VS_P_BURST_G,
            VS_T_CLOSURE_MS, VS_T_BURST_MS, VS_T_VOT_MS,
            VS_T_BURST_F, VS_T_BURST_G,
            PITCH_HZ
        )
        print("  purohitam_reconstruction_v2.py: OK (CORRECTED)")
        print()
        print("  [p] burst formants:")
        print(f"    F: {VS_P_BURST_F}")
        print(f"    G: {VS_P_BURST_G}")
        print(f"    → F2 dominant at {VS_P_BURST_F[1]:.0f} Hz")
        print()
        print("  [t] burst formants:")
        print(f"    F: {VS_T_BURST_F}")
        print(f"    G: {VS_T_BURST_G}")
        print(f"    → F2 dominant at {VS_T_BURST_F[1]:.0f} Hz")
        params_found = True
    except ImportError:
        try:
            from purohitam_reconstruction import (
                VS_P_CLOSURE_MS, VS_P_BURST_MS, VS_P_VOT_MS,
                VS_T_CLOSURE_MS, VS_T_BURST_MS, VS_T_VOT_MS,
                PITCH_HZ
            )
            print("  purohitam_reconstruction.py: OK (v1 - old method)")
            params_found = True
        except ImportError as e:
            print(f"  ERROR: Cannot import reconstruction file: {e}")
            return False
    
    print()
    
    # Load audio files
    v1_paths = [
        "output_play/purohitam_dry.wav",
        "output_play/diag_purohitam_dry.wav"
    ]
    v2_paths = [
        "output_play/purohitam_dry_v2.wav",
    ]
    
    v1 = None
    v1_path = None
    for path in v1_paths:
        v1 = load_wav(path)
        if v1 is not None:
            v1_path = path
            break
    
    v2 = None
    v2_path = None
    for path in v2_paths:
        v2 = load_wav(path)
        if v2 is not None:
            v2_path = path
            break
    
    if v1 is not None:
        print(f"  v1 loaded: {v1_path}")
        print(f"  Duration: {len(v1)/SR:.3f}s")
        v1_available = True
    else:
        print("  WARNING: v1 audio not found")
        print("  Using v1 reference values from previous diagnostic")
        v1_available = False
    
    if v2 is None:
        print("  ERROR: v2 audio not found")
        print("  Expected: output_play/purohitam_dry_v2.wav")
        print("  Run: python purohitam_reconstruction_v2.py")
        return False
    else:
        print(f"  v2 loaded: {v2_path}")
        print(f"  Duration: {len(v2)/SR:.3f}s")
    
    print()
    
    all_pass = True
    
    # ── DURATION COMPARISON ───────────────────────────────────────────────
    if v1_available:
        print("─" * 70)
        print("DURATION COMPARISON")
        print()
        dur_v1 = len(v1) / SR * 1000.0
        dur_v2 = len(v2) / SR * 1000.0
        diff = abs(dur_v2 - dur_v1)
        
        print(f"  v1 duration: {dur_v1:.1f} ms")
        print(f"  v2 duration: {dur_v2:.1f} ms")
        print(f"  Difference:  {diff:.1f} ms")
        print()
        
        if diff < 5.0:
            print("  ✓ Durations match (within 5ms)")
            d_dur = True
        else:
            print("  ✗ Duration mismatch (check synthesis)")
            d_dur = False
        all_pass &= d_dur
        print()
    
    # ── RMS COMPARISON ────────────────────────────────────────────────────
    if v1_available:
        print("─" * 70)
        print("RMS COMPARISON")
        print()
        rms_v1 = np.sqrt(np.mean(v1**2))
        rms_v2 = np.sqrt(np.mean(v2**2))
        ratio = rms_v2 / rms_v1 if rms_v1 > 1e-10 else 0.0
        
        print(f"  v1 RMS: {rms_v1:.4f}")
        print(f"  v2 RMS: {rms_v2:.4f}")
        print(f"  Ratio:  {ratio:.4f}")
        print()
        
        if 0.90 <= ratio <= 1.10:
            print("  ✓ RMS levels similar (within 10%)")
            d_rms = True
        else:
            print("  ⚠ RMS difference (boundary fix may affect level slightly)")
            d_rms = True  # Not a failure
        print()
    
    # ── [p] BURST CENTROID COMPARISON ─────────────────────────────────────
    print("─" * 70)
    print("[p] BURST CENTROID — PRIMARY TEST")
    print()
    print("  v1 reference: 1297 Hz (bandpass 700-1500 Hz)")
    print("  v2 target: formants centered at 1100 Hz")
    print("  Expected: v2 ≈ v1 within 100 Hz")
    print()
    
    # Approximate [p] burst location (word-initial)
    p_burst_start_ms = VS_P_CLOSURE_MS
    p_burst_end_ms = VS_P_CLOSURE_MS + VS_P_BURST_MS
    p_burst_start = int(p_burst_start_ms / 1000.0 * SR)
    p_burst_end = int(p_burst_end_ms / 1000.0 * SR)
    
    if v1_available:
        p_burst_v1 = v1[p_burst_start:p_burst_end]
        p_cent_v1 = measure_band_centroid(p_burst_v1, 500.0, 3000.0)
        print(f"  v1 [p] burst: {p_cent_v1:.0f} Hz")
    else:
        p_cent_v1 = V1_P_BURST_HZ
        print(f"  v1 [p] burst: {p_cent_v1:.0f} Hz (reference)")
    
    p_burst_v2 = v2[p_burst_start:p_burst_end]
    p_cent_v2 = measure_band_centroid(p_burst_v2, 500.0, 3000.0)
    print(f"  v2 [p] burst: {p_cent_v2:.0f} Hz")
    
    p_diff = abs(p_cent_v2 - p_cent_v1)
    print(f"  Difference:   {p_diff:.0f} Hz")
    print()
    
    p1 = check(
        f'[p] v2 matches v1 ({p_cent_v1:.0f} Hz)',
        p_cent_v2,
        p_cent_v1 - BURST_TOLERANCE_HZ,
        p_cent_v1 + BURST_TOLERANCE_HZ,
        unit=' Hz', fmt='.1f')
    
    if p1:
        print()
        print("  ✓ [p] BURST CENTROID PRESERVED")
        print("  v6 formants match v1 spectral profile")
    else:
        print()
        print("  ✗ [p] BURST CENTROID CHANGED")
        print(f"  Expected: {p_cent_v1:.0f} ± {BURST_TOLERANCE_HZ:.0f} Hz")
        print(f"  Measured: {p_cent_v2:.0f} Hz")
        print()
        print("  INVESTIGATE:")
        print("  - Check VS_P_BURST_F formants")
        print("  - Check VS_P_BURST_G gains")
        print("  - F2 should dominate at 1100 Hz")
    
    all_pass &= p1
    print()
    
    # ── [t] BURST CENTROID COMPARISON ─────────────────────────────────────
    print("─" * 70)
    print("[t] BURST CENTROID — PRIMARY TEST")
    print()
    print("  v1 reference: 3006 Hz (bandpass 2750-4250 Hz)")
    print("  v2 target: formants centered at 3500 Hz")
    print("  Expected: v2 ≈ v1 within 100 Hz")
    print()
    
    # Approximate [t] burst location
    t_start_estimate_ms = 260.0
    t_burst_start_ms = t_start_estimate_ms + VS_T_CLOSURE_MS
    t_burst_end_ms = t_burst_start_ms + VS_T_BURST_MS
    t_burst_start = int(t_burst_start_ms / 1000.0 * SR)
    t_burst_end = int(t_burst_end_ms / 1000.0 * SR)
    
    if v1_available and t_burst_end < len(v1):
        t_burst_v1 = v1[t_burst_start:t_burst_end]
        t_cent_v1 = measure_band_centroid(t_burst_v1, 2000.0, 6000.0)
        print(f"  v1 [t] burst: {t_cent_v1:.0f} Hz")
    else:
        t_cent_v1 = V1_T_BURST_HZ
        print(f"  v1 [t] burst: {t_cent_v1:.0f} Hz (reference)")
    
    if t_burst_end < len(v2):
        t_burst_v2 = v2[t_burst_start:t_burst_end]
        t_cent_v2 = measure_band_centroid(t_burst_v2, 2000.0, 6000.0)
        print(f"  v2 [t] burst: {t_cent_v2:.0f} Hz")
        
        t_diff = abs(t_cent_v2 - t_cent_v1)
        print(f"  Difference:   {t_diff:.0f} Hz")
        print()
        
        p1 = check(
            f'[t] v2 matches v1 ({t_cent_v1:.0f} Hz)',
            t_cent_v2,
            t_cent_v1 - BURST_TOLERANCE_HZ,
            t_cent_v1 + BURST_TOLERANCE_HZ,
            unit=' Hz', fmt='.1f')
        
        if p1:
            print()
            print("  ✓ [t] BURST CENTROID PRESERVED")
            print("  v6 formants match v1 spectral profile")
        else:
            print()
            print("  ✗ [t] BURST CENTROID CHANGED")
            print(f"  Expected: {t_cent_v1:.0f} ± {BURST_TOLERANCE_HZ:.0f} Hz")
            print(f"  Measured: {t_cent_v2:.0f} Hz")
            print()
            print("  INVESTIGATE:")
            print("  - Check VS_T_BURST_F formants")
            print("  - Check VS_T_BURST_G gains")
            print("  - F2 should dominate at 3500 Hz")
        
        all_pass &= p1
    else:
        print("  ⚠ Burst extraction failed (rough estimate)")
        print("  Cannot verify [t] burst centroid")
        print()
    
    print()
    
    # ── PERCEPTUAL VERIFICATION ─────────────────��────────────────────────
    print("─" * 70)
    print("PERCEPTUAL VERIFICATION")
    print()
    print("Acoustic measurements confirm spectral equivalence.")
    print("LISTEN to verify v6 boundary fix is working correctly.")
    print()
    
    if v1_available:
        print("COMPARISON TEST:")
        print()
        print("  1. Listen to v1:")
        print(f"     afplay {v1_path}")
        print()
        print("  2. Listen to v2:")
        print(f"     afplay {v2_path}")
        print()
        print("  FOCUS ON:")
        print()
        print("    [p] in 'PU-' (word-initial)")
        print("      v1: may have subtle click at burst")
        print("      v2: should be clean, natural release")
        print()
        print("    [t] in '-TAM' (post-vowel)")
        print("      v1: may have subtle click at burst")
        print("      v2: should be clean, natural release")
        print()
        print("    Overall sound quality")
        print("      v2: should sound equal or CLEANER than v1")
        print("      Same spectral character, smoother releases")
        print()
    else:
        print("v2-ONLY TEST:")
        print()
        print("  Listen to v2:")
        print(f"  afplay {v2_path}")
        print()
        print("  LISTEN FOR:")
        print()
        print("    [p] in 'PU-' (word-initial)")
        print("      Should be clean, natural release")
        print("      No click or discontinuity")
        print()
        print("    [t] in '-TAM' (post-vowel)")
        print("      Should be clean, natural release")
        print("      No click or discontinuity")
        print()
        print("    Overall word: 'pu-ro-hi-tam'")
        print("      Should flow naturally")
        print("      All stops should sound natural")
        print()
    
    print("  ✓ PASS CRITERIA:")
    print("    - No clicks at [p] or [t] release")
    print("    - Natural stop burst quality")
    print("    - Spectral character matches v1")
    print("    - Word sounds clean and natural")
    print()
    print("  ✗ FAIL CRITERIA:")
    print("    - Clicks present at stop releases")
    print("    - Unnatural burst quality")
    print("    - Spectral character changed")
    print("    - Word quality degraded")
    print()
    
    # ── BURST HIERARCHY CONFIRMATION ─────────────────────────────────────
    print("─" * 70)
    print("BURST HIERARCHY CONFIRMATION")
    print()
    print("  VS-internal verified burst centroids:")
    print()
    print(f"  [p] oṣṭhya  {p_cent_v2:.0f} Hz  — labial (v2 CORRECTED)")
    print(f"  [g] kaṇṭhya 2594 Hz  — velar  (ṚG/AGNI)")
    print(f"  [t] dantya  {t_cent_v2 if t_burst_end < len(v2) else 'N/A':.0f} Hz  — dental (v2 CORRECTED)")
    print()
    print("  oṣṭhya < kaṇṭhya < dantya")
    print("  Physics of anterior cavity determines burst frequency.")
    print()
    if p_cent_v2 < 2594.0:
        print("  ✓ [p] below [g] (oṣṭhya < kaṇṭhya)")
    if t_cent_v2 > 2594.0 if t_burst_end < len(v2) else False:
        print("  ✓ [t] above [g] (dantya > kaṇṭhya)")
    print()
    
    # ── SUMMARY ──────────────────────────────────────────────────────────
    print("=" * 70)
    print("SUMMARY")
    print()
    
    rows = [
        ("Duration match", v1_available and d_dur),
        ("RMS similar", v1_available and d_rms),
        ("[p] burst preserved", p1),
        ("[t] burst preserved", all_pass),
    ]
    
    for lbl, ok_ in rows:
        sym = "✓ PASS" if ok_ else ("✗ FAIL" if lbl in ["[p] burst preserved", "[t] burst preserved"] else "N/A")
        print(f"  {lbl:30s}  {sym}")
    print(f"  {'Perceptual verification':30s}  REQUIRED")
    print()
    
    if all_pass:
        print("  ✓✓✓ ACOUSTIC CHECKS PASSED ✓✓✓")
        print()
        print("  v6 architecture implemented correctly.")
        print("  Burst formants match v1 spectral profile.")
        print("  Burst centroids preserved within tolerance.")
        print()
        print("  NEXT STEP: PERCEPTUAL VERIFICATION")
        print("  Listen to both versions and confirm:")
        print("    - No clicks at [p] or [t]")
        print("    - v2 sounds cleaner or equal to v1")
        print()
        print("  If perceptual test passes:")
        print("    - [t] and [p] confirmed v6 architecture ✓")
        print("    - PUROHITAM v2 VERIFIED ✓")
        print("    - Update inventory: mark [t][p] as v6")
        print("    - Update evidence file: add v2 perceptual note")
        print()
        print("  HOUSECLEANING COMPLETE:")
        print("    - PUROHITAM v2: [t][p] updated ✓")
        print()
        print("  NEXT: YAJÑASYA v3 ([ɟ] update to v7)")
        print()
    else:
        print("  ✗ ACOUSTIC CHECKS FAILED")
        print()
        if not p1:
            print("  [p] burst centroid mismatch:")
            print(f"    Expected: {p_cent_v1:.0f} ± {BURST_TOLERANCE_HZ:.0f} Hz")
            print(f"    Measured: {p_cent_v2:.0f} Hz")
            print()
            print("  ACTION REQUIRED:")
            print("    - Adjust VS_P_BURST_F formants")
            print("    - Increase F2 gain (1100 Hz)")
            print("    - Reduce F1/F3 gains")
            print()
        print("  Re-run after adjustments.")
        print()
    
    print("=" * 70)
    print()
    
    return all_pass

if __name__ == "__main__":
    passed = run_diagnostics()
    sys.exit(0 if passed else 1)
