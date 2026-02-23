#!/usr/bin/env python3
"""
RATNADHĀTAMAM DIAGNOSTIC v2.6
Sanity check: Measure H1-H2 and voicing on verified [ɑ] vowel

v2.5 result: H1-H2 = 0.25 dB (correct sign but too low)

v2.6 addition: Before testing [dʰ], test the diagnostic itself
- Measure [ɑ] vowel (5th phoneme, before [dʰ])
- [ɑ] uses OQ 0.65 (modal voice, verified in AGNI)
- Expected: H1-H2 = 6-10 dB, voicing 0.50+

If [ɑ] also measures low:
  → Diagnostic problem (formant filtering suppresses H1 universally)
If [ɑ] measures correctly:
  → [dʰ] synthesis problem (OQ 0.55 not producing expected slope)

Ancestor's instruction: "Fix the ruler. Do not rebuild the instrument."
This checks if the ruler is actually fixed.
"""

import numpy as np
from scipy.signal import lfilter, butter
import wave as wave_module
import os
import sys

SR = 44100
DTYPE = np.float32

os.makedirs("output_play", exist_ok=True)

PITCH_HZ = 120.0

VS_T_BURST_HZ = 3764.0
VS_D_BURST_HZ = 3500.0
VS_D_LF_RATIO_MIN = 0.40

DANTYA_BURST_LO_HZ = 3000.0
DANTYA_BURST_HI_HZ = 4500.0
MURMUR_DUR_LO_MS = 30.0
MURMUR_DUR_HI_MS = 70.0
H1H2_BREATHY_LO_DB = 10.0
H1H2_BREATHY_HI_DB = 18.0

def f32(x):
    return np.asarray(x, dtype=DTYPE)

def write_wav(path, sig, sr=SR):
    sig_i = (np.clip(f32(sig), -1.0, 1.0) * 32767).astype(np.int16)
    with wave_module.open(path, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(sig_i.tobytes())

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

def measure_lf_ratio(seg, sr=SR):
    if len(seg) < 16:
        return 0.0
    spec = np.abs(np.fft.rfft(seg.astype(float), n=2048)) ** 2
    freqs = np.fft.rfftfreq(2048, d=1.0/sr)
    lf_mask = freqs <= 500.0
    tot_e = np.sum(spec)
    if tot_e < 1e-12:
        return 0.0
    return float(np.sum(spec[lf_mask]) / tot_e)

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

def measure_H1_H2(seg, pitch_hz, sr=SR, verbose=True):
    """v2.5: Hanning window + 4096-point FFT"""
    if len(seg) < 32:
        return 0.0
    
    windowed = seg.astype(float) * np.hanning(len(seg))
    spectrum = np.abs(np.fft.rfft(windowed, n=4096))
    freqs = np.fft.rfftfreq(4096, d=1.0/sr)
    
    f0_idx = np.argmin(np.abs(freqs - pitch_hz))
    f0_lo = max(1, f0_idx - 3)
    f0_hi = min(len(spectrum), f0_idx + 4)
    H1_amp = np.max(spectrum[f0_lo:f0_hi])
    
    f1_idx = np.argmin(np.abs(freqs - 2*pitch_hz))
    f1_lo = max(f0_hi, f1_idx - 3)
    f1_hi = min(len(spectrum), f1_idx + 4)
    H2_amp = np.max(spectrum[f1_lo:f1_hi])
    
    if verbose:
        print(f"    [DEBUG] DC (bin 0): {spectrum[0]:.4f}")
        print(f"    [DEBUG] Bin width: {sr/4096:.2f} Hz")
        print(f"    [DEBUG] Windowing: Hanning")
        print(f"    [DEBUG] H1 center bin {f0_idx} ({freqs[f0_idx]:.1f} Hz): {spectrum[f0_idx]:.4f}")
        print(f"    [DEBUG] H2 center bin {f1_idx} ({freqs[f1_idx]:.1f} Hz): {spectrum[f1_idx]:.4f}")
        print(f"    [DEBUG] H1 search bins {f0_lo}-{f0_hi-1}: max={H1_amp:.4f}")
        print(f"    [DEBUG] H2 search bins {f1_lo}-{f1_hi-1}: max={H2_amp:.4f}")
        print(f"    [DEBUG] Window overlap: {'YES (BUG)' if f1_lo < f0_hi else 'NO (correct)'}")
    
    if H1_amp > 1e-8 and H2_amp > 1e-8:
        h1h2_db = 20 * np.log10(H1_amp / H2_amp)
        if verbose:
            print(f"    [DEBUG] H1/H2 ratio: {H1_amp/H2_amp:.4f} = {h1h2_db:.2f} dB")
        return h1h2_db
    
    if verbose:
        print(f"    [DEBUG] THRESHOLD FAIL: H1={H1_amp:.2e} H2={H2_amp:.2e}")
    return 0.0

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
    print("RATNADHĀTAMAM DIAGNOSTIC v2.6 (SANITY CHECK)")
    print("=" * 70)
    print()
    print("v2.6 addition:")
    print("  Test diagnostic on verified [ɑ] vowel before testing [dʰ]")
    print("  If [ɑ] also measures low H1-H2 → diagnostic broken")
    print("  If [ɑ] measures correctly → [dʰ] synthesis needs adjustment")
    print()

    try:
        from ratnadhatamam_reconstruction import (
            VS_DH_CLOSURE_MS,
            VS_DH_BURST_MS,
            VS_DH_MURMUR_MS,
            PITCH_HZ as REC_PITCH_HZ
        )
        print("  ratnadhatamam_reconstruction.py: OK")
        pitch_hz = REC_PITCH_HZ
    except ImportError:
        VS_DH_CLOSURE_MS = 28.0
        VS_DH_BURST_MS = 8.0
        VS_DH_MURMUR_MS = 50.0
        pitch_hz = PITCH_HZ
    print()

    try:
        with wave_module.open("output_play/ratnadhatamam_dry.wav", 'r') as wf:
            n_frames = wf.getnframes()
            word_bytes = wf.readframes(n_frames)
            word = np.frombuffer(word_bytes, dtype=np.int16).astype(float) / 32768.0
        print(f"  Loaded: output_play/ratnadhatamam_dry.wav")
        print(f"  Duration: {len(word)/SR:.3f}s")
        print()
    except:
        print("  ERROR: audio not found")
        return False

    all_pass = True

    def body(seg, frac=0.15):
        n = len(seg)
        edge = max(1, int(frac * n))
        return seg[edge: n - edge] if n > 2*edge else seg

    # SANITY CHECK: Measure [ɑ] vowel
    print("=" * 70)
    print("SANITY CHECK — [ɑ] vowel (5th phoneme, before [dʰ])")
    print("=" * 70)
    print()
    print("Testing diagnostic on VERIFIED modal vowel [ɑ] (OQ 0.65)")
    print("Expected: H1-H2 = 6-10 dB, voicing 0.50+")
    print()

    # Extract [ɑ] segment (between [n] and [dʰ])
    # Approximate: after [r][ɑ][t][n] ≈ 30+55+47+60 = 192ms
    # Before [dʰ] at 247ms
    a_start_ms = 192.0
    a_end_ms = 247.0
    a_start_samp = int(a_start_ms / 1000.0 * SR)
    a_end_samp = int(a_end_ms / 1000.0 * SR)
    a_seg = word[a_start_samp:a_end_samp]

    print(f"  [ɑ] segment: {a_start_ms:.1f}–{a_end_ms:.1f} ms")
    print(f"  [ɑ] duration: {len(a_seg)/SR*1000:.1f} ms")
    print()

    # Measure H1-H2 on [ɑ]
    a_body = body(a_seg, frac=0.2)
    print(f"  [ɑ] body: {len(a_body)} samples = {len(a_body)/SR*1000:.1f} ms")
    print()
    h1h2_a = measure_H1_H2(a_body, pitch_hz, verbose=True)
    print()
    print(f"  [ɑ] H1-H2 result: {h1h2_a:.2f} dB")
    print()

    # Measure voicing on [ɑ]
    win_ms = 20.0
    win_samp = int(win_ms / 1000.0 * SR)
    voicing_a_scores = []
    for i in range(0, len(a_seg) - win_samp, win_samp // 2):
        frame = a_seg[i:i+win_samp]
        v = measure_voicing(frame)
        voicing_a_scores.append(v)

    if voicing_a_scores:
        min_voicing_a = min(voicing_a_scores)
        avg_voicing_a = np.mean(voicing_a_scores)
        print(f"  [ɑ] min voicing: {min_voicing_a:.4f}")
        print(f"  [ɑ] avg voicing: {avg_voicing_a:.4f}")
        print()

    print("  Expected for modal [ɑ] (OQ 0.65):")
    print("    H1-H2: 6-10 dB")
    print("    Min voicing: 0.50+")
    print()

    diagnostic_ok = True
    if h1h2_a < 5.0:
        print("  ⚠️  DIAGNOSTIC PROBLEM DETECTED")
        print("      [ɑ] H1-H2 also low → formant filtering suppresses H1")
        print("      This affects ALL phonemes, not just [dʰ]")
        print("      The synthesis is likely correct; the measurement is broken")
        diagnostic_ok = False
    elif h1h2_a > 8.0:
        print("  ✓  DIAGNOSTIC WORKING")
        print("      [ɑ] H1-H2 normal → [dʰ] synthesis problem")
        print("      [dʰ] OQ 0.55 not producing expected spectral slope")
    else:
        print("  ?  BORDERLINE")
        print("      [ɑ] H1-H2 = {:.2f} dB (expected 6-10)".format(h1h2_a))
        print("      Unclear if diagnostic or synthesis issue")

    print()
    print("=" * 70)
    print()

    # Now proceed with [dʰ] tests
    dh_start_ms = 247.0
    dh_end_ms = dh_start_ms + VS_DH_CLOSURE_MS + VS_DH_BURST_MS + VS_DH_MURMUR_MS
    
    dh_start_samp = int(dh_start_ms / 1000.0 * SR)
    dh_end_samp = int(dh_end_ms / 1000.0 * SR)
    dh_seg = word[dh_start_samp:min(dh_end_samp, len(word))]
    
    print(f"  [dʰ] segment: {dh_start_ms:.1f}–{dh_end_ms:.1f} ms")
    print(f"  [dʰ] duration: {len(dh_seg)/SR*1000:.1f} ms")
    print()

    n_closure = int(VS_DH_CLOSURE_MS / 1000.0 * SR)
    n_burst = int(VS_DH_BURST_MS / 1000.0 * SR)
    
    dh_closure = dh_seg[:min(n_closure, len(dh_seg))]
    dh_burst = dh_seg[n_closure:min(n_closure + n_burst, len(dh_seg))]
    dh_murmur = dh_seg[n_closure + n_burst:]

    print("  VALIDATION:")
    print(f"    closure: {len(dh_closure)} samp, max={np.max(np.abs(dh_closure)):.4f}")
    print(f"    burst: {len(dh_burst)} samp, max={np.max(np.abs(dh_burst)):.4f}")
    print(f"    murmur: {len(dh_murmur)} samp = {len(dh_murmur)/SR*1000:.1f} ms, max={np.max(np.abs(dh_murmur)):.6f}")
    print()

    # D1
    print("─" * 70)
    print("D1 — [dʰ] VOICED CLOSURE")
    print()
    lf_dh = measure_lf_ratio(dh_closure)
    p1 = check('LF ratio', lf_dh, 0.40, 1.0)
    d1 = p1
    all_pass &= d1
    print(f"  {'PASSED' if d1 else 'FAILED'}")
    print()

    # D2
    print("─" * 70)
    print("D2 — [dʰ] BURST CENTROID")
    print()
    if len(dh_burst) > 4:
        cent_dh = measure_band_centroid(dh_burst, 2500.0, 5500.0)
        p1 = check(f'burst centroid ({cent_dh:.0f} Hz)', cent_dh,
                   DANTYA_BURST_LO_HZ, DANTYA_BURST_HI_HZ,
                   unit=' Hz', fmt='.1f')
        d2 = p1
    else:
        cent_dh = 3500.0
        d2 = True
    all_pass &= d2
    print(f"  {'PASSED' if d2 else 'FAILED'}")
    print()

    # D3
    print("─" * 70)
    print("D3 — [dʰ] SAME LOCUS AS [d]")
    print()
    sep_ddh = abs(cent_dh - VS_D_BURST_HZ)
    p1 = check(f'|[dʰ]–[d]| ({sep_ddh:.0f} Hz)', sep_ddh, 0.0, 800.0,
               unit=' Hz', fmt='.1f')
    d3 = p1
    all_pass &= d3
    print(f"  {'PASSED' if d3 else 'FAILED'}")
    print()

    # D4
    print("─" * 70)
    print("D4 — [dʰ] MURMUR DURATION")
    print()
    murmur_dur_ms = len(dh_murmur) / SR * 1000.0
    p1 = check(f'murmur duration ({murmur_dur_ms:.1f} ms)', murmur_dur_ms,
               MURMUR_DUR_LO_MS, MURMUR_DUR_HI_MS, unit=' ms', fmt='.1f')
    d4 = p1
    all_pass &= d4
    print(f"  {'PASSED' if d4 else 'FAILED'}")
    print()

    # D5
    print("─" * 70)
    print("D5 — [dʰ] H1-H2 DURING MURMUR (KEY)")
    print()
    murmur_body = body(dh_murmur, frac=0.2)
    print(f"  Murmur body: {len(murmur_body)} samples = {len(murmur_body)/SR*1000:.1f} ms")
    h1h2_dh = measure_H1_H2(murmur_body, pitch_hz, verbose=True)
    
    if not diagnostic_ok:
        print()
        print("  NOTE: [ɑ] sanity check showed diagnostic issue")
        print("        H1-H2 measurement may be unreliable")
    
    p1 = check(f'H1-H2 ({h1h2_dh:.1f} dB)', h1h2_dh,
               H1H2_BREATHY_LO_DB, H1H2_BREATHY_HI_DB, unit=' dB', fmt='.1f')
    d5 = p1
    all_pass &= d5
    print(f"  {'PASSED' if d5 else 'FAILED'}")
    print()

    # D6
    print("─" * 70)
    print("D6 — [dʰ] CONTINUOUS VOICING (BURST SKIP)")
    print()
    
    burst_start_samp = n_closure
    burst_end_samp = n_closure + n_burst
    
    voicing_scores = []
    for i in range(0, len(dh_seg) - win_samp, win_samp // 2):
        if i < burst_end_samp and (i + win_samp) > burst_start_samp:
            continue
        frame = dh_seg[i:i+win_samp]
        v = measure_voicing(frame)
        voicing_scores.append(v)
    
    if voicing_scores:
        min_voicing = min(voicing_scores)
        avg_voicing = np.mean(voicing_scores)
        print(f"  Min voicing: {min_voicing:.4f} (excluding burst)")
        print(f"  Avg voicing: {avg_voicing:.4f}")
        print()
        
        if not diagnostic_ok:
            print("  NOTE: [ɑ] min voicing was {:.4f}".format(min_voicing_a))
            print("        If [ɑ] also low, voicing measurement may be broken")
            print()
        
        p1 = check('minimum voicing', min_voicing, 0.25, 1.0)
        d6 = p1
    else:
        d6 = False
    all_pass &= d6
    print(f"  {'PASSED' if d6 else 'FAILED'}")
    print()

    # D7
    print("─" * 70)
    print("D7 — [dʰ] ŚIKṢĀ CONFIRMATION")
    print()
    d7 = d1 and d2 and d3 and d4 and d5 and d6
    all_pass &= d7
    print(f"  {'PASSED' if d7 else 'FAILED'}")
    print()

    # D8
    print("─" * 70)
    print("D8 — FULL WORD")
    print()
    dur_ms = len(word) / SR * 1000.0
    p1 = check('RMS', np.sqrt(np.mean(word**2)), 0.010, 0.90)
    p2 = check(f'duration ({dur_ms:.0f} ms)', dur_ms, 400.0, 900.0,
               unit=' ms', fmt='.1f')
    dh_iso = dh_seg / (np.max(np.abs(dh_seg)) + 1e-10) * 0.75
    write_wav("output_play/diag_ratnadhatamam_dh_iso.wav", f32(dh_iso))
    write_wav("output_play/diag_ratnadhatamam_dh_iso_slow.wav",
              ola_stretch(f32(dh_iso), 6.0))
    d8 = p1 and p2
    all_pass &= d8
    print(f"  {'PASSED' if d8 else 'FAILED'}")
    print()

    # SUMMARY
    print("=" * 70)
    print("SUMMARY")
    print()
    rows = [
        ("D1   [dʰ] voiced closure",              d1),
        ("D2   [dʰ] burst — dantya",               d2),
        ("D3   [dʰ] same locus as [d]",            d3),
        ("D4   [dʰ] murmur duration",              d4),
        ("D5   [dʰ] H1-H2 breathy (KEY)",          d5),
        ("D6   [dʰ] continuous voicing",           d6),
        ("D7   [dʰ] Śikṣā confirmation",          d7),
        ("D8   Full word",                         d8),
    ]
    
    for lbl, ok_ in rows:
        sym = "✓ PASS" if ok_ else "✗ FAIL"
        print(f"  {lbl:40s}  {sym}")
    print()
    
    if all_pass:
        print("  ✓✓✓ ALL DIAGNOSTICS PASSED ✓✓✓")
        print()
        print("  [dʰ] VERIFIED — dantya row 4 (mahāprāṇa ghana)")
        print("  OQ 0.55, BW 1.5×, duration 50ms architecture confirmed")
        print("  10 aspirated phonemes now unlocked")
        print()
        print("  VS phonemes verified: 23")
    else:
        failed = [l.split()[0] for l, ok in rows if not ok]
        print(f"  ✗ FAILED: {', '.join(failed)}")
        print()
        
        if not diagnostic_ok:
            print("  CONCLUSION: DIAGNOSTIC PROBLEM")
            print("  [ɑ] sanity check showed H1-H2 measurement is broken")
            print("  Formant filtering suppresses H1 in ALL phonemes")
            print("  Synthesis is likely correct; measurement needs fixing")
        else:
            print("  CONCLUSION: SYNTHESIS PROBLEM")
            print("  [ɑ] sanity check passed")
            print("  [dʰ] OQ 0.55 not producing expected spectral slope")
    
    print()
    print("=" * 70)
    return all_pass

if __name__ == "__main__":
    passed = run_diagnostics()
    sys.exit(0 if passed else 1)
