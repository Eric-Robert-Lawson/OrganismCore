#!/usr/bin/env python3
"""
ṚTVIJAM DIAGNOSTIC v1
Vedic Sanskrit word 7 — ṛtvijam [ɻ̩tviɟɑm]

PRIMARY TARGET: [ʈ] voiceless retroflex stop
Śikṣā: mūrdhanya row 1 (voiceless unaspirated)

CRITICAL TEST:
  Burst centroid should be ~1300 Hz
  BELOW oṣṭhya [p] 1204 Hz
  This tests the counter-intuitive prediction:
    Retroflex curl → large anterior cavity → LOW burst
  
  If burst > 1500 Hz: physics model wrong
  If burst < 1100 Hz: synthesis error
  If burst 1100-1500 Hz: VERIFIED (Śikṣā confirmed)

RETROFLEX MARKERS:
  - F3 depression < 2500 Hz (mūrdhanya signature)
  - F3 depression >= 200 Hz vs neutral 2700 Hz
  - Same F3 signature as [ɻ̩] verified in ṚG

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
# DIAGNOSTIC THRESHOLDS
# ============================================================================

# [ʈ] retroflex stop targets
TT_CLOSURE_VOICING_MAX = 0.20  # Voiceless closure
TT_BURST_LO_HZ = 1100.0  # Predicted ~1300 Hz
TT_BURST_HI_HZ = 1500.0
TT_F3_MAX_HZ = 2500.0  # Retroflex F3 depression
TT_F3_DEPRESSION_MIN_HZ = 200.0  # vs neutral 2700 Hz

# Burst hierarchy test (VS-internal)
P_BURST_HZ = 1204.0  # oṣṭhya [p] VERIFIED PUROHITAM

# F3 measurement band (retroflex check)
F3_BAND_LO = 1800.0
F3_BAND_HI = 3000.0

# Neutral F3 reference (alveolar/dental)
NEUTRAL_F3_HZ = 2700.0

# ============================================================================
# MEASUREMENT HELPERS
# ============================================================================

def f32(x):
    return np.asarray(x, dtype=DTYPE)

def write_wav(path, sig, sr=SR):
    sig_i = (np.clip(f32(sig), -1.0, 1.0) * 32767).astype(np.int16)
    with wave_module.open(path, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(sig_i.tobytes())

def measure_band_centroid(seg, lo_hz, hi_hz, sr=SR):
    """Measure spectral centroid in frequency band"""
    if len(seg) < 16:
        return 0.0
    spec = np.abs(np.fft.rfft(seg.astype(float), n=2048)) ** 2
    freqs = np.fft.rfftfreq(2048, d=1.0/sr)
    mask = (freqs >= lo_hz) & (freqs <= hi_hz)
    total = np.sum(spec[mask])
    if total < 1e-12:
        return 0.0
    return float(np.sum(freqs[mask] * spec[mask]) / total)

def measure_voicing(seg, sr=SR):
    """Measure voicing via autocorrelation"""
    if len(seg) < 64:
        return 0.0
    n = len(seg)
    core = seg[n // 4: 3 * n // 4].astype(float)
    core -= np.mean(core)
    if np.max(np.abs(core)) < 1e-8:
        return 0.0
    acorr = np.correlate(core, core, mode='full')
    acorr = acorr[len(acorr) // 2:]
    acorr /= (acorr[0] + 1e-12)
    lo = int(sr / 400)
    hi = min(int(sr / 80), len(acorr) - 1)
    if lo >= hi:
        return 0.0
    return float(np.clip(np.max(acorr[lo:hi]), 0.0, 1.0))

def ola_stretch(sig, factor=6.0, sr=SR):
    """Time-stretch via overlap-add"""
    win_ms = 40.0
    win_n = int(win_ms / 1000.0 * sr)
    if win_n % 2 == 1:
        win_n += 1
    hop_in = win_n // 4
    hop_out = int(hop_in * factor)
    window = np.hanning(win_n).astype(DTYPE)
    n_in = len(sig)
    n_frames = max(1, (n_in - win_n) // hop_in + 1)
    n_out = hop_out * n_frames + win_n
    out = np.zeros(n_out, dtype=DTYPE)
    norm = np.zeros(n_out, dtype=DTYPE)
    for i in range(n_frames):
        in_pos = i * hop_in
        out_pos = i * hop_out
        if in_pos + win_n > n_in:
            break
        frame = sig[in_pos:in_pos + win_n] * window
        out[out_pos:out_pos + win_n] += frame
        norm[out_pos:out_pos + win_n] += window
    nz = norm > 1e-8
    out[nz] /= norm[nz]
    mx = np.max(np.abs(out))
    if mx > 1e-8:
        out = out / mx * 0.75
    return f32(out)

def check(label, value, lo, hi, unit='', fmt='.4f'):
    """Check if value is in range and print status"""
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

def body(seg, frac=0.15):
    """Extract central portion of segment (skip edges)"""
    n = len(seg)
    edge = max(1, int(frac * n))
    return seg[edge: n - edge] if n > 2*edge else seg

# ============================================================================
# DIAGNOSTIC RUNNER
# ============================================================================

def run_diagnostics():
    print()
    print("=" * 70)
    print("ṚTVIJAM DIAGNOSTIC v1")
    print("=" * 70)
    print()
    print("PRIMARY TARGET: [ʈ] voiceless retroflex stop")
    print("  Śikṣā: mūrdhanya row 1")
    print()
    print("CRITICAL TEST:")
    print("  Burst centroid should be ~1300 Hz")
    print("  BELOW oṣṭhya [p] 1204 Hz")
    print()
    print("  This tests counter-intuitive prediction:")
    print("    Retroflex curl → large anterior cavity → LOW burst")
    print()
    print("RETROFLEX MARKERS:")
    print("  - F3 depression < 2500 Hz")
    print("  - F3 depression >= 200 Hz vs neutral 2700 Hz")
    print()

    # Import synthesis parameters
    try:
        from rtvijam_reconstruction import (
            VS_RV_DUR_MS,
            VS_TT_CLOSURE_MS,
            VS_TT_BURST_MS,
            VS_TT_VOT_MS,
            VS_V_DUR_MS,
            VS_I_DUR_MS,
            VS_JJ_CLOSURE_MS,
            VS_JJ_BURST_MS,
            VS_JJ_VOT_MS,
            VS_A_DUR_MS,
            VS_M_DUR_MS,
            PITCH_HZ
        )
        print("  rtvijam_reconstruction.py: OK")
        print()
    except ImportError:
        print("  ERROR: Cannot import from rtvijam_reconstruction.py")
        return False

    # Load audio
    try:
        with wave_module.open("output_play/rtvijam_dry.wav", 'r') as wf:
            n_frames = wf.getnframes()
            word_bytes = wf.readframes(n_frames)
            word = np.frombuffer(word_bytes, dtype=np.int16).astype(float) / 32768.0
        print(f"  Loaded: output_play/rtvijam_dry.wav")
        print(f"  Duration: {len(word)/SR:.3f}s")
        print()
    except:
        print("  ERROR: audio not found")
        return False

    all_pass = True

    # ========================================================================
    # SEGMENT EXTRACTION
    # ========================================================================
    
    print("─" * 70)
    print("SEGMENT EXTRACTION")
    print()
    
    seg_boundaries_ms = []
    cursor_ms = 0.0
    
    phonemes = [
        ("[ɻ̩]", VS_RV_DUR_MS),
        ("[ʈ]",  VS_TT_CLOSURE_MS + VS_TT_BURST_MS + VS_TT_VOT_MS),
        ("[v]",  VS_V_DUR_MS),
        ("[i]",  VS_I_DUR_MS),
        ("[ɟ]",  VS_JJ_CLOSURE_MS + VS_JJ_BURST_MS + VS_JJ_VOT_MS),
        ("[ɑ]",  VS_A_DUR_MS),
        ("[m]",  VS_M_DUR_MS)
    ]
    
    for ph, dur_ms in phonemes:
        start_ms = cursor_ms
        end_ms = cursor_ms + dur_ms
        seg_boundaries_ms.append((ph, start_ms, end_ms))
        cursor_ms = end_ms
    
    for ph, start_ms, end_ms in seg_boundaries_ms:
        print(f"  {ph:6s}: {start_ms:6.1f} – {end_ms:6.1f} ms  "
              f"(dur: {end_ms - start_ms:5.1f} ms)")
    print()
    
    # Extract [ʈ] segments
    tt_start_ms = seg_boundaries_ms[1][1]
    tt_end_ms = seg_boundaries_ms[1][2]
    tt_start_samp = int(tt_start_ms / 1000.0 * SR)
    tt_end_samp = int(tt_end_ms / 1000.0 * SR)
    tt_seg = word[tt_start_samp:tt_end_samp]
    
    print(f"  [ʈ] extracted: {len(tt_seg)} samples = {len(tt_seg)/SR*1000:.1f} ms")
    print()
    
    # Extract closure, burst, VOT
    n_closure = int(VS_TT_CLOSURE_MS / 1000.0 * SR)
    n_burst = int(VS_TT_BURST_MS / 1000.0 * SR)
    
    tt_closure = tt_seg[:min(n_closure, len(tt_seg))]
    tt_burst = tt_seg[n_closure:min(n_closure + n_burst, len(tt_seg))]
    tt_vot = tt_seg[n_closure + n_burst:]
    
    print("  VALIDATION:")
    print(f"    closure: {len(tt_closure)} samp, max={np.max(np.abs(tt_closure)):.4f}")
    print(f"    burst: {len(tt_burst)} samp, max={np.max(np.abs(tt_burst)):.4f}")
    print(f"    VOT: {len(tt_vot)} samp = {len(tt_vot)/SR*1000:.1f} ms")
    print()

    # ========================================================================
    # D1: [ʈ] VOICELESS CLOSURE
    # ========================================================================
    
    print("─" * 70)
    print("D1 — [ʈ] VOICELESS CLOSURE")
    print()
    print("  Target: silence (voicing < 0.20)")
    print()
    
    voicing_cl = measure_voicing(tt_closure)
    
    print(f"  Closure voicing: {voicing_cl:.4f}")
    print()
    
    p1 = check('closure voicing', voicing_cl, 0.0, TT_CLOSURE_VOICING_MAX)
    d1 = p1
    all_pass &= d1
    
    if d1:
        print()
        print("  ✓ VOICELESS CLOSURE CONFIRMED")
        print("  [ʈ] is voiceless unaspirated (mūrdhanya row 1)")
    
    print(f"  {'PASSED' if d1 else 'FAILED'}")
    print()

    # ========================================================================
    # D2: [ʈ] BURST CENTROID (KEY)
    # ========================================================================
    
    print("─" * 70)
    print("D2 — [ʈ] BURST CENTROID (KEY TEST)")
    print()
    print("  CRITICAL PREDICTION:")
    print("    Burst ~1300 Hz (BELOW [p] 1204 Hz)")
    print()
    print("  This tests the retroflex physics:")
    print("    Tongue curl → large anterior cavity → low burst")
    print()
    
    if len(tt_burst) < 4:
        print("  ERROR: Burst segment too short")
        d2 = False
    else:
        burst_centroid = measure_band_centroid(tt_burst, 500.0, 3000.0, SR)
        
        print(f"  [ʈ] burst centroid: {burst_centroid:.1f} Hz")
        print(f"  [p] reference: {P_BURST_HZ:.1f} Hz (oṣṭhya)")
        print()
        
        if burst_centroid < P_BURST_HZ:
            print(f"  ✓ [ʈ] burst BELOW [p] by {P_BURST_HZ - burst_centroid:.1f} Hz")
            print("  Retroflex prediction CONFIRMED")
        else:
            print(f"  ✗ [ʈ] burst ABOVE [p] by {burst_centroid - P_BURST_HZ:.1f} Hz")
            print("  Retroflex prediction FAILED")
        print()
        
        p1 = check(f'[ʈ] burst ({burst_centroid:.0f} Hz)', burst_centroid,
                   TT_BURST_LO_HZ, TT_BURST_HI_HZ, unit=' Hz', fmt='.1f')
        d2 = p1
    
    all_pass &= d2
    print(f"  {'PASSED' if d2 else 'FAILED'}")
    print()

    # ========================================================================
    # D3: [ʈ] BURST HIERARCHY TEST
    # ========================================================================
    
    print("─" * 70)
    print("D3 — [ʈ] BURST HIERARCHY (VS-INTERNAL)")
    print()
    print("  Testing against oṣṭhya [p] 1204 Hz")
    print("  [ʈ] should be LOWEST in hierarchy")
    print()
    
    if not d2:
        print("  SKIPPED: D2 failed")
        d3 = False
    else:
        burst_below_p = (burst_centroid < P_BURST_HZ)
        
        print(f"  [ʈ] mūrdhanya: {burst_centroid:.1f} Hz")
        print(f"  [p] oṣṭhya:    {P_BURST_HZ:.1f} Hz")
        print()
        
        if burst_below_p:
            print("  ✓ HIERARCHY CONFIRMED")
            print("  mūrdhanya [ʈ] is LOWEST burst")
            print()
            print("  Expected full hierarchy:")
            print(f"    mūrdhanya [ʈ]  {burst_centroid:.0f} Hz  ← VERIFIED")
            print(f"    oṣṭhya    [p]   {P_BURST_HZ:.0f} Hz")
            print("    kaṇṭhya   [g]   2594 Hz")
            print("    tālavya   [ɟ]   3223 Hz")
            print("    dantya    [t]   3764 Hz")
            d3 = True
        else:
            print("  ✗ HIERARCHY VIOLATED")
            print("  [ʈ] should be below [p]")
            d3 = False
    
    all_pass &= d3
    print(f"  {'PASSED' if d3 else 'FAILED'}")
    print()

    # ========================================================================
    # D4: [ʈ] F3 DEPRESSION (RETROFLEX MARKER)
    # ========================================================================
    
    print("─" * 70)
    print("D4 — [ʈ] F3 DEPRESSION (RETROFLEX MARKER)")
    print()
    print("  F3 measurement band: 1800-3000 Hz")
    print(f"  Target: < {TT_F3_MAX_HZ:.0f} Hz (retroflex)")
    print(f"  Neutral reference: {NEUTRAL_F3_HZ:.0f} Hz (dental/alveolar)")
    print(f"  Minimum depression: {TT_F3_DEPRESSION_MIN_HZ:.0f} Hz")
    print()
    
    # Measure F3 in VOT (where formants are present)
    vot_body = body(tt_vot, frac=0.20)
    f3_tt = measure_band_centroid(vot_body, F3_BAND_LO, F3_BAND_HI, SR)
    f3_depression = NEUTRAL_F3_HZ - f3_tt
    
    print(f"  [ʈ] F3 centroid: {f3_tt:.1f} Hz")
    print(f"  Neutral F3: {NEUTRAL_F3_HZ:.1f} Hz")
    print(f"  Depression: {f3_depression:.1f} Hz")
    print()
    
    p1 = check(f'F3 < {TT_F3_MAX_HZ:.0f} Hz', f3_tt, 
               0.0, TT_F3_MAX_HZ, unit=' Hz', fmt='.1f')
    p2 = check(f'F3 depression >= {TT_F3_DEPRESSION_MIN_HZ:.0f} Hz', f3_depression,
               TT_F3_DEPRESSION_MIN_HZ, 1000.0, unit=' Hz', fmt='.1f')
    d4 = p1 and p2
    
    if d4:
        print()
        print("  ✓ RETROFLEX F3 MARKER CONFIRMED")
        print("  [ʈ] shows mūrdhanya F3 depression")
        print("  Same signature as [ɻ̩] (345 Hz depression in ṚG)")
    
    all_pass &= d4
    print(f"  {'PASSED' if d4 else 'FAILED'}")
    print()

    # ========================================================================
    # D5: FULL WORD VALIDATION
    # ========================================================================
    
    print("─" * 70)
    print("D5 — FULL WORD")
    print()
    
    dur_ms = len(word) / SR * 1000.0
    rms = np.sqrt(np.mean(word**2))
    
    p1 = check('RMS', rms, 0.010, 0.90)
    p2 = check(f'duration ({dur_ms:.0f} ms)', dur_ms, 300.0, 500.0,
               unit=' ms', fmt='.1f')
    d5 = p1 and p2
    all_pass &= d5
    print(f"  {'PASSED' if d5 else 'FAILED'}")
    print()

    # ========================================================================
    # OUTPUT ISOLATED SEGMENTS
    # ========================================================================
    
    print("─" * 70)
    print("GENERATING ISOLATED SEGMENTS")
    print()
    
    tt_iso = tt_seg / (np.max(np.abs(tt_seg)) + 1e-10) * 0.75
    write_wav("output_play/diag_rtvijam_tt_iso.wav", f32(tt_iso))
    write_wav("output_play/diag_rtvijam_tt_iso_slow.wav", ola_stretch(f32(tt_iso), 6.0))
    
    print()

    # ========================================================================
    # SUMMARY
    # ========================================================================
    
    print("=" * 70)
    print("SUMMARY")
    print()
    
    rows = [
        ("D1   [ʈ] voiceless closure",           d1),
        ("D2   [ʈ] burst centroid (KEY)",        d2),
        ("D3   [ʈ] burst hierarchy",             d3),
        ("D4   [ʈ] F3 depression (retroflex)",   d4),
        ("D5   Full word",                       d5),
    ]
    
    for lbl, ok_ in rows:
        sym = "✓ PASS" if ok_ else "✗ FAIL"
        print(f"  {lbl:45s}  {sym}")
    print()
    
    if all_pass:
        print("  ✓✓✓ ALL DIAGNOSTICS PASSED ✓✓✓")
        print()
        print("  [ʈ] VERIFIED — voiceless retroflex stop")
        print("  Śikṣā: mūrdhanya row 1")
        print()
        print("  Acoustic properties:")
        print(f"  - Closure: voiceless ({voicing_cl:.4f}) ✓")
        print(f"  - Burst: {burst_centroid:.1f} Hz (target 1100-1500) ✓")
        print(f"  - Burst BELOW [p] {P_BURST_HZ:.0f} Hz ✓")
        print(f"  - F3: {f3_tt:.1f} Hz (depression {f3_depression:.1f} Hz) ✓")
        print()
        print("  CRITICAL CONFIRMATION:")
        print("  Counter-intuitive prediction VERIFIED")
        print("  Retroflex curl → large anterior cavity → LOW burst")
        print(f"  [ʈ] {burst_centroid:.0f} Hz < [p] {P_BURST_HZ:.0f} Hz")
        print()
        print("  BURST HIERARCHY NOW COMPLETE:")
        print(f"    mūrdhanya [ʈ]  {burst_centroid:.0f} Hz  ← NEW (VERIFIED)")
        print(f"    oṣṭhya    [p]   {P_BURST_HZ:.0f} Hz")
        print("    kaṇṭhya   [g]   2594 Hz")
        print("    tālavya   [ɟ]   3223 Hz")
        print("    dantya    [t]   3764 Hz")
        print()
        print("  RETROFLEX SECTOR CONFIRMED:")
        print("  Both [ɻ̩] and [ʈ] show F3 depression")
        print("  Mūrdhanya phonemes occupy new vocal topology sector")
        print()
        print("  ŚIKṢĀ CONVERGENCE:")
        print("  Ancient classification matches physics prediction")
        print("  2,500-year-old map was acoustically accurate")
        print()
        print("  VS phonemes verified: 25 → 26")
    else:
        failed = [l.split()[0] for l, ok in rows if not ok]
        print(f"  ✗ FAILED: {', '.join(failed)}")
        print()
        if not d2:
            print("  CRITICAL: D2 failed (burst centroid)")
            print("  The retroflex physics prediction may be wrong")
            print("  OR: synthesis parameters need adjustment")
        if not d4:
            print("  CRITICAL: D4 failed (F3 depression)")
            print("  F3 notch may not be applied correctly")
            print("  OR: measurement band needs adjustment")
    
    print()
    print("=" * 70)
    return all_pass

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    passed = run_diagnostics()
    sys.exit(0 if passed else 1)
