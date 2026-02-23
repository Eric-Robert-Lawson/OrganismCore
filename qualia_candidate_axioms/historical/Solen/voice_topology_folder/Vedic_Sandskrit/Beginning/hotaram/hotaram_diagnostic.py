#!/usr/bin/env python3
"""
HOTĀRAM DIAGNOSTIC v1
Vedic Sanskrit word 8 — hotāram [hoːtaːrɑm]

PRIMARY TARGET: [aː] long vowel verification
- F1/F2 centroids should match [ɑ] (VERIFIED AGNI: F1=631Hz, F2=1106Hz)
- Duration ratio [aː]/[ɑ] should be ≥ 1.7× (long vowel distinction)
- Expected ratio: ~2.0× (110ms / 55ms)
- Voicing continuous throughout

SECONDARY: Full word validation
- All other phonemes already VERIFIED in previous words
- Word-level sanity checks

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

# [aː] targets (from physics derivation)
AA_F1_LO_HZ = 620.0
AA_F1_HI_HZ = 800.0
AA_F2_LO_HZ = 900.0
AA_F2_HI_HZ = 1300.0
AA_DUR_MIN_MS = 93.5  # 1.7× [ɑ] 55ms
AA_VOICING_MIN = 0.50

# Duration ratio
DUR_RATIO_MIN = 1.7  # minimum for "long" distinction

# Reference values from AGNI [ɑ]
A_F1_MEASURED_HZ = 631.0
A_F2_MEASURED_HZ = 1106.0
A_DUR_MS = 55.0

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
    print("HOTĀRAM DIAGNOSTIC v1")
    print("=" * 70)
    print()
    print("PRIMARY TARGET: [aː] long vowel verification")
    print("  - F1/F2 centroids match [ɑ]")
    print("  - Duration ratio [aː]/[ɑ] ≥ 1.7×")
    print("  - Continuous voicing")
    print()

    # Import synthesis parameters
    try:
        from hotaram_reconstruction import (
            VS_H_DUR_MS,
            VS_OO_DUR_MS,
            VS_T_CLOSURE_MS,
            VS_T_BURST_MS,
            VS_T_VOT_MS,
            VS_AA_DUR_MS,
            VS_R_DUR_MS,
            VS_A_DUR_MS,
            VS_M_DUR_MS,
            PITCH_HZ
        )
        print("  hotaram_reconstruction.py: OK")
        print()
    except ImportError:
        print("  ERROR: Cannot import from hotaram_reconstruction.py")
        return False

    # Load audio
    try:
        with wave_module.open("output_play/hotaram_dry.wav", 'r') as wf:
            n_frames = wf.getnframes()
            word_bytes = wf.readframes(n_frames)
            word = np.frombuffer(word_bytes, dtype=np.int16).astype(float) / 32768.0
        print(f"  Loaded: output_play/hotaram_dry.wav")
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
    
    # Calculate segment boundaries based on synthesis durations
    seg_boundaries_ms = []
    cursor_ms = 0.0
    
    phonemes = [
        ("[h]",  VS_H_DUR_MS),
        ("[oː]", VS_OO_DUR_MS),
        ("[t]",  VS_T_CLOSURE_MS + VS_T_BURST_MS + VS_T_VOT_MS),
        ("[aː]", VS_AA_DUR_MS),
        ("[ɾ]",  VS_R_DUR_MS),
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
    
    # Extract [aː] segment (4th phoneme)
    aa_start_ms = seg_boundaries_ms[3][1]
    aa_end_ms = seg_boundaries_ms[3][2]
    aa_start_samp = int(aa_start_ms / 1000.0 * SR)
    aa_end_samp = int(aa_end_ms / 1000.0 * SR)
    aa_seg = word[aa_start_samp:aa_end_samp]
    
    # Extract [ɑ] segment (6th phoneme)
    a_start_ms = seg_boundaries_ms[5][1]
    a_end_ms = seg_boundaries_ms[5][2]
    a_start_samp = int(a_start_ms / 1000.0 * SR)
    a_end_samp = int(a_end_ms / 1000.0 * SR)
    a_seg = word[a_start_samp:a_end_samp]
    
    print(f"  [aː] extracted: {len(aa_seg)} samples = {len(aa_seg)/SR*1000:.1f} ms")
    print(f"  [ɑ]  extracted: {len(a_seg)} samples = {len(a_seg)/SR*1000:.1f} ms")
    print()

    # ========================================================================
    # D1: [aː] F1 CENTROID
    # ========================================================================
    
    print("─" * 70)
    print("D1 — [aː] F1 CENTROID (should match [ɑ])")
    print()
    
    aa_body = body(aa_seg, frac=0.20)
    f1_aa = measure_band_centroid(aa_body, 300.0, 1200.0, SR)
    
    print(f"  [aː] F1 centroid: {f1_aa:.1f} Hz")
    print(f"  [ɑ]  F1 reference: {A_F1_MEASURED_HZ:.1f} Hz (AGNI)")
    print(f"  Difference: {abs(f1_aa - A_F1_MEASURED_HZ):.1f} Hz")
    print()
    
    p1 = check(f'[aː] F1 ({f1_aa:.0f} Hz)', f1_aa, 
               AA_F1_LO_HZ, AA_F1_HI_HZ, unit=' Hz', fmt='.1f')
    d1 = p1
    all_pass &= d1
    print(f"  {'PASSED' if d1 else 'FAILED'}")
    print()

    # ========================================================================
    # D2: [aː] F2 CENTROID
    # ========================================================================
    
    print("─" * 70)
    print("D2 — [aː] F2 CENTROID (should match [ɑ])")
    print()
    
    f2_aa = measure_band_centroid(aa_body, 700.0, 1800.0, SR)
    
    print(f"  [aː] F2 centroid: {f2_aa:.1f} Hz")
    print(f"  [ɑ]  F2 reference: {A_F2_MEASURED_HZ:.1f} Hz (AGNI)")
    print(f"  Difference: {abs(f2_aa - A_F2_MEASURED_HZ):.1f} Hz")
    print()
    
    p1 = check(f'[aː] F2 ({f2_aa:.0f} Hz)', f2_aa,
               AA_F2_LO_HZ, AA_F2_HI_HZ, unit=' Hz', fmt='.1f')
    d2 = p1
    all_pass &= d2
    print(f"  {'PASSED' if d2 else 'FAILED'}")
    print()

    # ========================================================================
    # D3: [aː] ABSOLUTE DURATION
    # ========================================================================
    
    print("─" * 70)
    print("D3 — [aː] ABSOLUTE DURATION")
    print()
    
    aa_dur_ms = len(aa_seg) / SR * 1000.0
    
    print(f"  [aː] measured: {aa_dur_ms:.1f} ms")
    print(f"  Target: ≥ {AA_DUR_MIN_MS:.1f} ms")
    print()
    
    p1 = check(f'[aː] duration ({aa_dur_ms:.1f} ms)', aa_dur_ms,
               AA_DUR_MIN_MS, 150.0, unit=' ms', fmt='.1f')
    d3 = p1
    all_pass &= d3
    print(f"  {'PASSED' if d3 else 'FAILED'}")
    print()

    # ========================================================================
    # D4: DURATION RATIO [aː]/[ɑ]
    # ========================================================================
    
    print("─" * 70)
    print("D4 — DURATION RATIO [aː]/[ɑ] (KEY)")
    print()
    
    a_dur_ms = len(a_seg) / SR * 1000.0
    ratio = aa_dur_ms / a_dur_ms if a_dur_ms > 0 else 0.0
    
    print(f"  [aː] duration: {aa_dur_ms:.1f} ms")
    print(f"  [ɑ]  duration: {a_dur_ms:.1f} ms")
    print(f"  Ratio: {ratio:.2f}×")
    print()
    print(f"  Expected ratio: ~2.0× (110ms / 55ms)")
    print(f"  Minimum ratio for 'long' distinction: {DUR_RATIO_MIN:.1f}×")
    print()
    
    p1 = check(f'[aː]/[ɑ] ratio ({ratio:.2f}×)', ratio,
               DUR_RATIO_MIN, 3.0, unit='×', fmt='.2f')
    d4 = p1
    all_pass &= d4
    print(f"  {'PASSED' if d4 else 'FAILED'}")
    print()

    # ========================================================================
    # D5: [aː] CONTINUOUS VOICING
    # ========================================================================
    
    print("─" * 70)
    print("D5 — [aː] CONTINUOUS VOICING")
    print()
    
    # Measure voicing in overlapping windows
    win_ms = 20.0
    win_samp = int(win_ms / 1000.0 * SR)
    voicing_scores = []
    
    for i in range(0, len(aa_seg) - win_samp, win_samp // 2):
        frame = aa_seg[i:i+win_samp]
        v = measure_voicing(frame)
        voicing_scores.append(v)
    
    if voicing_scores:
        min_voicing = min(voicing_scores)
        avg_voicing = np.mean(voicing_scores)
        print(f"  Min voicing: {min_voicing:.4f}")
        print(f"  Avg voicing: {avg_voicing:.4f}")
        print()
        
        p1 = check('minimum voicing', min_voicing, AA_VOICING_MIN, 1.0)
        d5 = p1
    else:
        d5 = False
    
    all_pass &= d5
    print(f"  {'PASSED' if d5 else 'FAILED'}")
    print()

    # ========================================================================
    # D6: [ɑ] COMPARISON (sanity check)
    # ========================================================================
    
    print("─" * 70)
    print("D6 — [ɑ] SANITY CHECK (should match AGNI reference)")
    print()
    
    a_body = body(a_seg, frac=0.20)
    f1_a = measure_band_centroid(a_body, 300.0, 1200.0, SR)
    f2_a = measure_band_centroid(a_body, 700.0, 1800.0, SR)
    
    print(f"  [ɑ] F1: {f1_a:.1f} Hz  (AGNI: {A_F1_MEASURED_HZ:.1f} Hz)")
    print(f"  [ɑ] F2: {f2_a:.1f} Hz  (AGNI: {A_F2_MEASURED_HZ:.1f} Hz)")
    print(f"  [ɑ] duration: {a_dur_ms:.1f} ms  (expected: ~{A_DUR_MS:.1f} ms)")
    print()
    
    # This is informational only, not a pass/fail test
    print("  (Informational only — verifies [ɑ] is consistent)")
    d6 = True
    print()

    # ========================================================================
    # D7: FULL WORD VALIDATION
    # ========================================================================
    
    print("─" * 70)
    print("D7 — FULL WORD")
    print()
    
    dur_ms = len(word) / SR * 1000.0
    rms = np.sqrt(np.mean(word**2))
    
    p1 = check('RMS', rms, 0.010, 0.90)
    p2 = check(f'duration ({dur_ms:.0f} ms)', dur_ms, 300.0, 600.0,
               unit=' ms', fmt='.1f')
    d7 = p1 and p2
    all_pass &= d7
    print(f"  {'PASSED' if d7 else 'FAILED'}")
    print()

    # ========================================================================
    # OUTPUT ISOLATED SEGMENTS
    # ========================================================================
    
    print("���" * 70)
    print("GENERATING ISOLATED SEGMENTS")
    print()
    
    # [aː] isolated
    aa_iso = aa_seg / (np.max(np.abs(aa_seg)) + 1e-10) * 0.75
    write_wav("output_play/diag_hotaram_aa_iso.wav", f32(aa_iso))
    write_wav("output_play/diag_hotaram_aa_iso_slow.wav", ola_stretch(f32(aa_iso), 6.0))
    
    # [ɑ] isolated
    a_iso = a_seg / (np.max(np.abs(a_seg)) + 1e-10) * 0.75
    write_wav("output_play/diag_hotaram_a_iso.wav", f32(a_iso))
    write_wav("output_play/diag_hotaram_a_iso_slow.wav", ola_stretch(f32(a_iso), 6.0))
    
    print()

    # ========================================================================
    # SUMMARY
    # ========================================================================
    
    print("=" * 70)
    print("SUMMARY")
    print()
    
    rows = [
        ("D1   [aː] F1 centroid",           d1),
        ("D2   [aː] F2 centroid",           d2),
        ("D3   [aː] absolute duration",     d3),
        ("D4   [aː]/[ɑ] ratio (KEY)",       d4),
        ("D5   [aː] continuous voicing",    d5),
        ("D6   [ɑ] sanity check",           d6),
        ("D7   Full word",                  d7),
    ]
    
    for lbl, ok_ in rows:
        sym = "✓ PASS" if ok_ else "✗ FAIL"
        print(f"  {lbl:40s}  {sym}")
    print()
    
    if all_pass:
        print("  ✓✓✓ ALL DIAGNOSTICS PASSED ✓✓✓")
        print()
        print("  [aː] VERIFIED — long open central unrounded")
        print("  - Formants match [ɑ] (same articulation)")
        print(f"  - Duration ratio: {ratio:.2f}× (long vowel confirmed)")
        print("  - Continuous voicing throughout")
        print()
        print("  VS phonemes verified: 24")
        print("  Status: PARTIAL → VERIFIED")
    else:
        failed = [l.split()[0] for l, ok in rows if not ok]
        print(f"  ✗ FAILED: {', '.join(failed)}")
        print()
        print("  Review synthesis parameters")
        print("  Check segment extraction boundaries")
        print("  Run perceptual verification")
    
    print()
    print("=" * 70)
    return all_pass

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    passed = run_diagnostics()
    sys.exit(0 if passed else 1)
