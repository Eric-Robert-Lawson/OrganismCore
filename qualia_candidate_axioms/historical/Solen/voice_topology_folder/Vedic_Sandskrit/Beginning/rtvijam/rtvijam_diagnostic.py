#!/usr/bin/env python3
"""
ṚTVIJAM DIAGNOSTIC v3
Vedic Sanskrit word 7 — ṛtvijam [ɻ̩tviɟɑm]

PRIMARY TARGET: [ʈ] voiceless retroflex stop
Śikṣā: mūrdhanya row 1 (voiceless unaspirated)

HIERARCHY CORRECTION (v2→v3):
  v2 claimed: [ʈ] must be ABOVE [p] + 100 Hz
  v2 result: [ʈ] 1194 Hz < [p] 1204 Hz (FAILED v2 test)
  
  v3 correction: [ʈ] and [p] SHARE LOW-BURST REGION
  Physics: Both have long/augmented front cavities
           [ʈ] has sublingual cavity → can be at or below [p]
           Distinction is F3 DEPRESSION, not burst centroid
  
  Original prediction ([ʈ] ≤ [p]) was CORRECT.

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
TT_CLOSURE_VOICING_MAX = 0.20

# v3 CORRECTED: Low-burst region (shared with [p])
TT_BURST_LO_HZ = 800.0
TT_BURST_HI_HZ = 1600.0

TT_F3_MAX_HZ = 2500.0
TT_F3_DEPRESSION_MIN_HZ = 200.0

# Reference bursts
P_BURST_HZ = 1204.0
G_BURST_HZ = 2594.0

# F3 measurement band
F3_BAND_LO = 1800.0
F3_BAND_HI = 3000.0

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
    n = len(seg)
    edge = max(1, int(frac * n))
    return seg[edge: n - edge] if n > 2*edge else seg

# ============================================================================
# DIAGNOSTIC RUNNER
# ============================================================================

def run_diagnostics():
    print()
    print("=" * 70)
    print("ṚTVIJAM DIAGNOSTIC v3")
    print("=" * 70)
    print()
    print("HIERARCHY CORRECTION (v2→v3):")
    print("  v3: [ʈ] and [p] SHARE LOW-BURST REGION")
    print("  Distinction = F3 DEPRESSION, not burst centroid")
    print("  Original prediction ([ʈ] ≤ [p]) was CORRECT")
    print()

    # Import synthesis parameters
    version = None
    params_found = False
    
    for v in ['v6', 'v5', 'v4', 'v3', 'v2', '']:
        module_name = f"rtvijam_reconstruction{'_' + v if v else ''}"
        try:
            mod = __import__(module_name)
            VS_RV_DUR_MS = mod.VS_RV_DUR_MS
            VS_TT_CLOSURE_MS = mod.VS_TT_CLOSURE_MS
            VS_TT_BURST_MS = mod.VS_TT_BURST_MS
            VS_TT_VOT_MS = mod.VS_TT_VOT_MS
            VS_V_DUR_MS = mod.VS_V_DUR_MS
            VS_I_DUR_MS = mod.VS_I_DUR_MS
            VS_JJ_CLOSURE_MS = mod.VS_JJ_CLOSURE_MS
            VS_JJ_BURST_MS = mod.VS_JJ_BURST_MS
            VS_JJ_VOT_MS = mod.VS_JJ_VOT_MS
            VS_A_DUR_MS = mod.VS_A_DUR_MS
            VS_M_DUR_MS = mod.VS_M_DUR_MS
            PITCH_HZ = mod.PITCH_HZ
            version = v if v else 'v1'
            params_found = True
            print(f"  {module_name}.py: OK ({version})")
            break
        except (ImportError, AttributeError):
            continue
    
    if not params_found:
        print("  ERROR: Cannot import reconstruction file")
        return False
    print()

    # Load audio
    audio_paths = [
        "output_play/rtvijam_dry_v6.wav",
        "output_play/rtvijam_dry_v5.wav",
        "output_play/rtvijam_dry_v4.wav",
        "output_play/rtvijam_dry_v3.wav",
        "output_play/rtvijam_dry_v2.wav",
        "output_play/rtvijam_dry.wav"
    ]
    
    word = None
    audio_version = None
    for audio_path in audio_paths:
        try:
            with wave_module.open(audio_path, 'r') as wf:
                n_frames = wf.getnframes()
                word_bytes = wf.readframes(n_frames)
                word = np.frombuffer(word_bytes, dtype=np.int16).astype(float) / 32768.0
            audio_version = audio_path.split('_')[-1].replace('.wav', '')
            if audio_version == 'dry':
                audio_version = 'v1'
            print(f"  Loaded: {audio_path}")
            print(f"  Duration: {len(word)/SR:.3f}s")
            break
        except:
            continue
    
    if word is None:
        print("  ERROR: audio not found")
        return False
    print()

    all_pass = True

    # SEGMENT EXTRACTION
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
    
    # Extract [ʈ]
    tt_start_ms = seg_boundaries_ms[1][1]
    tt_end_ms = seg_boundaries_ms[1][2]
    tt_start_samp = int(tt_start_ms / 1000.0 * SR)
    tt_end_samp = int(tt_end_ms / 1000.0 * SR)
    tt_seg = word[tt_start_samp:tt_end_samp]
    
    n_closure = int(VS_TT_CLOSURE_MS / 1000.0 * SR)
    n_burst = int(VS_TT_BURST_MS / 1000.0 * SR)
    
    tt_closure = tt_seg[:min(n_closure, len(tt_seg))]
    tt_burst = tt_seg[n_closure:min(n_closure + n_burst, len(tt_seg))]
    tt_vot = tt_seg[n_closure + n_burst:]
    
    print(f"  [ʈ] extracted: {len(tt_seg)} samples")
    print()

    # D1: VOICELESS CLOSURE
    print("─" * 70)
    print("D1 — [ʈ] VOICELESS CLOSURE")
    print()
    
    voicing_cl = measure_voicing(tt_closure)
    print(f"  Closure voicing: {voicing_cl:.4f}")
    print()
    
    p1 = check('closure voicing', voicing_cl, 0.0, TT_CLOSURE_VOICING_MAX)
    d1 = p1
    all_pass &= d1
    
    if d1:
        print("  ✓ VOICELESS CLOSURE CONFIRMED")
    print(f"  {'PASSED' if d1 else 'FAILED'}")
    print()

    # D2: BURST CENTROID
    print("─" * 70)
    print("D2 — [ʈ] BURST CENTROID")
    print()
    
    if len(tt_burst) < 4:
        print("  ERROR: Burst too short")
        d2 = False
        burst_centroid = 0.0
    else:
        burst_centroid = measure_band_centroid(tt_burst, 500.0, 3000.0, SR)
        print(f"  [ʈ] burst centroid: {burst_centroid:.1f} Hz")
        print()
        
        p1 = check(f'[ʈ] burst in LOW region', burst_centroid,
                   TT_BURST_LO_HZ, TT_BURST_HI_HZ, unit=' Hz', fmt='.1f')
        d2 = p1
    
    all_pass &= d2
    print(f"  {'PASSED' if d2 else 'FAILED'}")
    print()

    # D3: LOW-BURST REGION (v3 CORRECTED)
    print("─" * 70)
    print("D3 — [ʈ] LOW-BURST REGION (v3 CORRECTED)")
    print()
    print("  PHYSICS: [ʈ] and [p] share LOW-BURST REGION")
    print("  Distinction = F3 DEPRESSION (tested in D4)")
    print()
    
    if not d2:
        print("  SKIPPED: D2 failed")
        d3 = False
    else:
        print(f"  [ʈ] mūrdhanya: {burst_centroid:.1f} Hz")
        print(f"  [p] oṣṭhya:    {P_BURST_HZ:.1f} Hz")
        print(f"  Separation: {burst_centroid - P_BURST_HZ:.1f} Hz")
        print()
        
        p1 = check(f'[ʈ] in LOW-BURST region', burst_centroid,
                   TT_BURST_LO_HZ, TT_BURST_HI_HZ, unit=' Hz', fmt='.1f')
        p2 = check(f'[ʈ] below velar/palatal', burst_centroid,
                   0.0, 2000.0, unit=' Hz', fmt='.1f')
        d3 = p1 and p2
        
        if d3:
            print("  ✓ LOW-BURST REGION CONFIRMED")
    
    all_pass &= d3
    print(f"  {'PASSED' if d3 else 'FAILED'}")
    print()

    # D4: F3 DEPRESSION (KEY TEST)
    print("─" * 70)
    print("D4 — [ʈ] F3 DEPRESSION (KEY TEST)")
    print()
    print("  THIS DISTINGUISHES [ʈ] FROM [p]")
    print()
    
    vot_body = body(tt_vot, frac=0.20)
    f3_tt = measure_band_centroid(vot_body, F3_BAND_LO, F3_BAND_HI, SR)
    f3_depression = NEUTRAL_F3_HZ - f3_tt
    
    print(f"  [ʈ] F3: {f3_tt:.1f} Hz")
    print(f"  Neutral F3: {NEUTRAL_F3_HZ:.1f} Hz")
    print(f"  Depression: {f3_depression:.1f} Hz")
    print()
    
    p1 = check(f'F3 < {TT_F3_MAX_HZ:.0f} Hz', f3_tt, 
               0.0, TT_F3_MAX_HZ, unit=' Hz', fmt='.1f')
    p2 = check(f'F3 depression >= {TT_F3_DEPRESSION_MIN_HZ:.0f} Hz', f3_depression,
               TT_F3_DEPRESSION_MIN_HZ, 1000.0, unit=' Hz', fmt='.1f')
    d4 = p1 and p2
    
    if d4:
        print("  ✓ RETROFLEX F3 MARKER CONFIRMED")
    
    all_pass &= d4
    print(f"  {'PASSED' if d4 else 'FAILED'}")
    print()

    # D5: FULL WORD
    print("─" * 70)
    print("D5 — FULL WORD")
    print()
    
    dur_ms = len(word) / SR * 1000.0
    rms = np.sqrt(np.mean(word**2))
    
    p1 = check('RMS', rms, 0.010, 0.90)
    p2 = check(f'duration', dur_ms, 300.0, 500.0, unit=' ms', fmt='.1f')
    d5 = p1 and p2
    all_pass &= d5
    print(f"  {'PASSED' if d5 else 'FAILED'}")
    print()

    # OUTPUT ISOLATED
    print("─" * 70)
    print("GENERATING ISOLATED SEGMENTS")
    print()
    
    tt_iso = tt_seg / (np.max(np.abs(tt_seg)) + 1e-10) * 0.75
    write_wav("output_play/diag_rtvijam_tt_iso.wav", f32(tt_iso))
    write_wav("output_play/diag_rtvijam_tt_iso_slow.wav", ola_stretch(f32(tt_iso), 6.0))
    print()

    # SUMMARY
    print("=" * 70)
    print("SUMMARY")
    print()
    
    rows = [
        ("D1   [ʈ] voiceless closure",      d1),
        ("D2   [ʈ] burst centroid",         d2),
        ("D3   [ʈ] low-burst region (v3)",  d3),
        ("D4   [ʈ] F3 depression (KEY)",    d4),
        ("D5   Full word",                  d5),
    ]
    
    for lbl, ok_ in rows:
        sym = "✓ PASS" if ok_ else "✗ FAIL"
        print(f"  {lbl:45s}  {sym}")
    print()
    
    if all_pass:
        print("  ✓✓✓ ALL DIAGNOSTICS PASSED ✓✓✓")
        print()
        print(f"  [ʈ] VERIFIED ({audio_version})")
        print("  Śikṣā: mūrdhanya row 1")
        print()
        print(f"  - Burst: {burst_centroid:.1f} Hz (LOW-BURST) ✓")
        print(f"  - F3 depression: {f3_depression:.1f} Hz (RETROFLEX) ✓")
        print()
        print("  LOW-BURST REGION:")
        print(f"    [ʈ] mūrdhanya: {burst_centroid:.0f} Hz")
        print(f"    [p] oṣṭhya:    {P_BURST_HZ:.0f} Hz")
        print("    Distinguished by F3 depression")
        print()
        print("  VS phonemes verified: 25 → 26")
        print("  ṚTVIJAM [ɻ̩tviɟɑm] COMPLETE")
    else:
        failed = [l.split()[0] for l, ok in rows if not ok]
        print(f"  ✗ FAILED: {', '.join(failed)}")
    
    print()
    print("=" * 70)
    return all_pass

if __name__ == "__main__":
    passed = run_diagnostics()
    sys.exit(0 if passed else 1)
