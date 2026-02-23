#!/usr/bin/env python3
"""
YAJÑASYA DIAGNOSTIC v3
Vedic Sanskrit: yajñasya  [jɑɟɲɑsjɑ]
Rigveda 1.1.1 — word 4

ARCHITECTURE UPDATE v1→v3:
  v1: [ɟ] used OLD bandpass noise burst
  v3: [ɟ] uses v7 (spike + turbulence, no boundary fix)
  
  COMPARISON TEST:
    Compare v1 vs v3 burst centroids
    Target: within 100 Hz of v1 measurement
    Perceptual: improved naturalness

February 2026
"""

import numpy as np
from scipy.signal import lfilter, butter, argrelmin
import wave as wave_module
import os
import sys

SR = 44100
DTYPE = np.float32

os.makedirs("output_play", exist_ok=True)

# ── CONSTANTS ─────────────────────────────────────────
PITCH_HZ = 120.0
PERIOD_MS = 1000.0 / PITCH_HZ
DIP_SMOOTH_PERIODS = 2.7
DIP_SMOOTH_MS = PERIOD_MS * DIP_SMOOTH_PERIODS
DIP_SMOOTH_SAMPLES = int(DIP_SMOOTH_MS / 1000.0 * SR)

TALAVYA_BURST_LO_HZ = 2800.0
TALAVYA_BURST_HI_HZ = 4000.0

VS_G_BURST_HZ = 2594.0
VS_T_BURST_HZ = 3764.0

def f32(x):
    return np.asarray(x, dtype=DTYPE)

def write_wav(path, sig, sr=SR):
    sig_i = (np.clip(f32(sig), -1.0, 1.0) * 32767).astype(np.int16)
    with wave_module.open(path, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(sig_i.tobytes())

def ola_stretch(sig, factor=4.0, sr=SR):
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

def run_diagnostics():
    print()
    print("=" * 70)
    print("YAJÑASYA DIAGNOSTIC v3 — CORRECTED")
    print("=" * 70)
    print()
    print("ARCHITECTURE UPDATE (v1→v3):")
    print()
    print("  v1: [ɟ] used OLD bandpass noise burst")
    print("  v3: [ɟ] uses v7 (spike + turbulence, no boundary fix)")
    print("      WITH formants matching v1 spectral profile")
    print()
    print("  [ɟ] v1 burst: measured from v1 output")
    print("  [ɟ] v3 target: preserve v1 centroid ± 100 Hz")
    print()
    
    # Import v3 reconstruction
    version = None
    params_found = False
    
    try:
        from yajnasya_reconstruction_v3 import (
            VS_JJ_CLOSURE_MS, VS_JJ_BURST_MS, DIL
        )
        version = 'v3'
        params_found = True
        print("  yajnasya_reconstruction_v3.py: OK (v3)")
    except ImportError:
        try:
            from yajnasya_reconstruction import (
                VS_JJ_CLOSURE_MS, VS_JJ_BURST_MS, DIL
            )
            version = 'v1'
            params_found = True
            print("  yajnasya_reconstruction.py: OK (v1 - old method)")
        except ImportError as e:
            print(f"  ERROR: Cannot import reconstruction file: {e}")
            return False
    print()
    
    # Load v1 reference
    v1_word = None
    v1_audio_paths = [
        "output_play/diag_yajnasya_dry.wav",
        "output_play/yajnasya_dry.wav"
    ]
    
    for audio_path in v1_audio_paths:
        try:
            with wave_module.open(audio_path, 'r') as wf:
                n_frames = wf.getnframes()
                word_bytes = wf.readframes(n_frames)
                v1_word = np.frombuffer(word_bytes, dtype=np.int16).astype(float) / 32768.0
            print(f"  v1 loaded: {audio_path}")
            print(f"  Duration: {len(v1_word)/SR:.3f}s")
            break
        except:
            continue
    
    if v1_word is None:
        print("  ERROR: v1 audio not found")
        return False
    
    # Load v3
    v3_word = None
    v3_audio_paths = [
        "output_play/yajnasya_dry_v3.wav"
    ]
    
    for audio_path in v3_audio_paths:
        try:
            with wave_module.open(audio_path, 'r') as wf:
                n_frames = wf.getnframes()
                word_bytes = wf.readframes(n_frames)
                v3_word = np.frombuffer(word_bytes, dtype=np.int16).astype(float) / 32768.0
            print(f"  v3 loaded: {audio_path}")
            print(f"  Duration: {len(v3_word)/SR:.3f}s")
            break
        except:
            continue
    
    if v3_word is None:
        print("  ERROR: v3 audio not found - run yajnasya_reconstruction_v3.py first")
        return False
    print()
    
    all_pass = True
    
    # ── DURATION COMPARISON ──────────────────────────────
    print("─" * 70)
    print("DURATION COMPARISON")
    print()
    
    dur_v1_ms = len(v1_word) / SR * 1000.0
    dur_v3_ms = len(v3_word) / SR * 1000.0
    dur_diff = abs(dur_v3_ms - dur_v1_ms)
    
    print(f"  v1 duration: {dur_v1_ms:.1f} ms")
    print(f"  v3 duration: {dur_v3_ms:.1f} ms")
    print(f"  Difference:  {dur_diff:.1f} ms")
    print()
    
    p1 = check('Duration match (within 5ms)', dur_diff, 0.0, 5.0, unit=' ms', fmt='.1f')
    all_pass &= p1
    
    if p1:
        print("  ✓ Durations match (within 5ms)")
    print()
    
    # ── RMS COMPARISON ───────────────────────────────────
    print("─" * 70)
    print("RMS COMPARISON")
    print()
    
    rms_v1 = np.sqrt(np.mean(v1_word ** 2))
    rms_v3 = np.sqrt(np.mean(v3_word ** 2))
    rms_ratio = rms_v3 / (rms_v1 + 1e-12)
    
    print(f"  v1 RMS: {rms_v1:.4f}")
    print(f"  v3 RMS: {rms_v3:.4f}")
    print(f"  Ratio:  {rms_ratio:.4f}")
    print()
    
    p1 = check('RMS similar (within 10%)', rms_ratio, 0.90, 1.10, fmt='.4f')
    all_pass &= p1
    
    if p1:
        print("  ✓ RMS levels similar (within 10%)")
    print()
    
    # ── [ɟ] BURST CENTROID — PRIMARY TEST ────────────────
    print("─" * 70)
    print("[ɟ] BURST CENTROID — PRIMARY TEST")
    print()
    print("  v1 reference: bandpass noise (measured from v1 output)")
    print("  v3 target: v7 formants matching v1 spectral profile")
    print("  Expected: v3 ≈ v1 within 100 Hz")
    print()
    
    # Extract [ɟ] burst from both versions
    # Approximate position: after [j][ɑ], ~110-150ms into word
    # Burst duration: ~9ms
    
    jj_start_ms_v1 = 110.0
    jj_start_samp_v1 = int(jj_start_ms_v1 / 1000.0 * SR)
    jj_closure_samp = int(VS_JJ_CLOSURE_MS * DIL / 1000.0 * SR)
    jj_burst_samp = int(VS_JJ_BURST_MS * DIL / 1000.0 * SR)
    
    jj_burst_v1 = v1_word[jj_start_samp_v1 + jj_closure_samp:
                          jj_start_samp_v1 + jj_closure_samp + jj_burst_samp]
    
    jj_start_ms_v3 = 110.0  # Same position
    jj_start_samp_v3 = int(jj_start_ms_v3 / 1000.0 * SR)
    jj_burst_v3 = v3_word[jj_start_samp_v3 + jj_closure_samp:
                          jj_start_samp_v3 + jj_closure_samp + jj_burst_samp]
    
    if len(jj_burst_v1) < 4 or len(jj_burst_v3) < 4:
        print("  ERROR: Burst segments too short")
        return False
    
    cent_v1 = measure_band_centroid(jj_burst_v1, 2000.0, 5000.0, SR)
    cent_v3 = measure_band_centroid(jj_burst_v3, 2000.0, 5000.0, SR)
    diff_hz = abs(cent_v3 - cent_v1)
    
    print(f"  v1 [ɟ] burst: {cent_v1:.1f} Hz")
    print(f"  v3 [ɟ] burst: {cent_v3:.1f} Hz")
    print(f"  Difference:   {diff_hz:.1f} Hz")
    print()
    
    p1 = check(f'[ɟ] v3 matches v1 ({cent_v1:.0f} Hz)', cent_v3,
               cent_v1 - 100.0, cent_v1 + 100.0, unit=' Hz', fmt='.1f')
    all_pass &= p1
    
    if p1:
        print("  ✓ [ɟ] BURST CENTROID PRESERVED")
        print("  v7 formants match v1 spectral profile")
    else:
        print("  ✗ [ɟ] BURST CENTROID CHANGED")
        print(f"  Expected: {cent_v1:.0f} ± 100 Hz")
        print(f"  Measured: {cent_v3:.0f} Hz")
        print()
        print("  INVESTIGATE:")
        print("  - Check VS_JJ_BURST_F formants")
        print("  - Check VS_JJ_BURST_G gains")
        print("  - F2 should dominate at ~3200 Hz")
    print()
    
    # ── BURST HIERARCHY ──────────────────────────────────
    print("─" * 70)
    print("BURST HIERARCHY CONFIRMATION")
    print()
    print("  VS-internal verified burst centroids:")
    print()
    print(f"  [g] kaṇṭhya {VS_G_BURST_HZ:.0f} Hz  — velar  (ṚG/AGNI)")
    print(f"  [ɟ] tālavya {cent_v3:.0f} Hz  — palatal (v3 UPDATED)")
    print(f"  [t] dantya  {VS_T_BURST_HZ:.0f} Hz  — dental (PUROHITAM)")
    print()
    print("  kaṇṭhya < tālavya < dantya")
    print("  Physics of anterior cavity determines burst frequency.")
    print()
    
    jj_above_g = cent_v3 - VS_G_BURST_HZ
    jj_below_t = VS_T_BURST_HZ - cent_v3
    
    p2 = check(f'[ɟ] above [g] (kaṇṭhya < tālavya)', jj_above_g,
               100.0, 2000.0, unit=' Hz', fmt='.1f')
    p3 = check(f'[ɟ] below [t] (tālavya < dantya)', jj_below_t,
               0.0, 1500.0, unit=' Hz', fmt='.1f')
    
    hierarchy_ok = p2 and p3
    all_pass &= hierarchy_ok
    
    if hierarchy_ok:
        print()
        print("  ✓ [ɟ] slots correctly in hierarchy")
        print(f"  {VS_G_BURST_HZ:.0f} < {cent_v3:.0f} < {VS_T_BURST_HZ:.0f} Hz")
    print()
    
    # ── PERCEPTUAL VERIFICATION ──────────────────────────
    print("─" * 70)
    print("PERCEPTUAL VERIFICATION")
    print()
    print("Acoustic measurements confirm spectral equivalence.")
    print("LISTEN to verify v7 architecture is working correctly.")
    print()
    print("COMPARISON TEST:")
    print()
    print("  1. Listen to v1:")
    print("     afplay output_play/diag_yajnasya_dry.wav")
    print()
    print("  2. Listen to v3:")
    print("     afplay output_play/yajnasya_dry_v3.wav")
    print()
    print("  FOCUS ON:")
    print()
    print("    [ɟ] in 'YAJ-' (after [ɑ], before [ɲ])")
    print("      v1: may have subtle artifact at burst")
    print("      v3: should be clean, natural release")
    print()
    print("    Overall sound quality")
    print("      v3: should sound equal or CLEANER than v1")
    print("      Same spectral character, smoother burst")
    print()
    print("  ✓ PASS CRITERIA:")
    print("    - Natural stop burst quality")
    print("    - Spectral character matches v1")
    print("    - Word sounds clean and natural")
    print()
    print("  ✗ FAIL CRITERIA:")
    print("    - Unnatural burst quality")
    print("    - Spectral character changed")
    print("    - Word quality degraded")
    print()
    
    # ── SUMMARY ���─────────────────────────────────────────
    print("=" * 70)
    print("SUMMARY")
    print()
    
    rows = [
        ("Duration match", dur_diff <= 5.0),
        ("RMS similar", 0.90 <= rms_ratio <= 1.10),
        ("[ɟ] burst preserved", p1),
        ("Burst hierarchy", hierarchy_ok),
        ("Perceptual verification", None),
    ]
    
    for lbl, ok_ in rows:
        if ok_ is None:
            sym = "REQUIRED"
        else:
            sym = "✓ PASS" if ok_ else "✗ FAIL"
        print(f"  {lbl:30s}  {sym}")
    print()
    
    if all_pass:
        print("  ✓✓✓ ACOUSTIC CHECKS PASSED ✓✓✓")
        print()
        print("  v7 architecture implemented correctly.")
        print(f"  [ɟ] burst centroid preserved: {cent_v3:.0f} Hz")
        print(f"  (v1 reference: {cent_v1:.0f} Hz, diff {diff_hz:.0f} Hz)")
        print()
        print("  NEXT STEP: PERCEPTUAL VERIFICATION")
        print("  Listen to both versions and confirm:")
        print("    - v3 sounds cleaner or equal to v1")
        print("    - [ɟ] burst sounds natural")
        print()
        print("  If perceptual test passes:")
        print("    - [ɟ] confirmed v7 architecture ✓")
        print("    - YAJÑASYA v3 VERIFIED ✓")
        print("    - Update inventory: mark [ɟ] as v7")
        print("    - Update evidence file: add v3 note")
        print()
        print("  HOUSECLEANING COMPLETE:")
        print("    - YAJÑASYA v3: [ɟ] updated ✓")
        print()
        print("  ALL VOICED STOPS NOW USE v7:")
        print("    - [ɟ] YAJÑASYA v3 ✓")
        print("    - [ɟ] ṚTVIJAM v7 ✓")
        print("    - [g] (v1, v7 update pending)")
        print("    - [d] (v1, v7 update pending)")
    else:
        failed = [l for l, ok in rows if ok is not None and not ok]
        print(f"  ✗ FAILED: {', '.join(failed)}")
        print()
        print("  Re-run after adjustments.")
    
    print()
    print("=" * 70)
    return all_pass

if __name__ == "__main__":
    passed = run_diagnostics()
    sys.exit(0 if passed else 1)
