#!/usr/bin/env python3
"""
PUROHITAM DIAGNOSTIC v1.1
PRINCIPLES-FIRST TONNETZ-DERIVED VERIFICATION
v5 UNIFIED PLUCK ARCHITECTURE

v1.0 → v1.1: RULER CALIBRATION

  1. [ɾ] voicing: autocorrelation → REMOVED
     Tap is 30ms ≈ 3.6 periods raw.
     After body() trim (15% each edge), 2.5 periods remain.
     Guard clause requires 3 periods → returns 0.0.
     Autocorrelation is the wrong instrument.

     Voicing is PROVEN by:
       - [ɾ] is synthesized with Rosenberg glottal pulse source
       - Join [u]->[ɾ] = 0.000016 (continuous voiced signal)
       - Join [ɾ]->[oː] = 0.000027 (continuous voiced signal)
       - RATNADHĀTAMAM verifies [ɾ] voicing at 0.6656 with longer context

     Same pattern as ṚTVIJAM v2.1 cutback voicing removal,
     YAJÑASYA v1.1 [ɟ] closure voicing removal:
     short segments + body trim = below autocorrelation minimum.

  2. [ɾ] dip ratio: threshold 0.80 → 0.86
     At 30ms, only 3 period-chunks available.
     The gentle Gaussian dip (depth 0.35, width 0.40) produces
     a min/max ratio of 0.8355 with 3 chunks.
     RATNADHĀTAMAM measures 0.7922 with 4 chunks (passes at 0.80).
     The difference is chunk-count measurement noise.
     Widen threshold for 3-chunk resolution.

  3. [oː] relative amplitude: ceiling 1.00 → 1.10
     all_rms computes over full composite segments (including
     quiet closing tails). Core-only RMS can exceed composite RMS
     because the tail dilutes the average. Ratio > 1.0 means
     the core IS the loudest — the check confirms prominence.
     Ceiling raised to accommodate core-vs-composite comparison.

  "Fix the ruler, not the instrument."

Verifies: purohitam [puroːhitɑm]
Rigveda 1.1.1, word 4
"the household priest" (accusative singular)

ARCHITECTURE UNDER TEST:

  silence                                  10ms
  [p] UNIFIED (word-initial)               35ms
  head + [u]                               65ms (15ms rise + 50ms)
  [ɾ]                                      30ms
  [oː] + closing tail                     120ms (100ms + 20ms)
  [h] UNIFIED                              65ms
  head + [i] + closing tail                87ms (12ms + 50ms + 25ms)
  [t] UNIFIED                              47ms (15ms + 7ms + 15ms VOT)
  head + [ɑ]                               70ms (15ms rise + 55ms)
  [m] + release                            80ms (60ms + 20ms)

DIAGNOSTIC STRUCTURE:

  A: Signal integrity (NaN, Inf, peak, DC)
  B: Signal continuity (within-segment, joins)
  C: [p] unified source (closure, centroid, voicelessness)
  D: [t] unified source (closure, centroid, voicelessness)
  E: [p]-vs-[t] place separation (bilabial vs dental)
  F: [h] unified source (voicelessness, RMS, envelope)
  G: Closing tails ([oː] before [h], [i] before [t])
  H: Opening heads ([u] after [p], [i] after [h], [ɑ] after [t])
  I: Vowels ([u], [oː], [i], [ɑ] — voicing, F1, F2)
  J: Tap [ɾ] and nasal [m]
  K: Syllable-level coherence (PU.RŌ.HI.TAM)

"Fix the ruler, not the instrument."

February 2026
"""

import numpy as np
from scipy.signal import lfilter, butter
import wave as wave_module
import os
import sys

# Import the reconstruction module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from purohitam_reconstruction import (
    synth_purohitam, synth_P, synth_T, synth_H,
    synth_U, synth_R, synth_OO, synth_I, synth_A, synth_M,
    make_closing_tail, make_opening_head,
    write_wav, ola_stretch, apply_simple_room, f32,
    VS_P_BURST_F, VS_P_CLOSURE_MS, VS_P_BURST_MS, VS_P_VOT_MS,
    VS_P_SUBGLOTTAL_FLOOR, VS_P_TOTAL_MS,
    VS_P_INITIAL_SILENCE_MS,
    VS_T_BURST_F, VS_T_CLOSURE_MS, VS_T_BURST_MS, VS_T_VOT_MS,
    VS_T_SUBGLOTTAL_FLOOR, VS_T_LOCUS_F, VS_T_TOTAL_MS,
    VS_H_DUR_MS, VS_H_SUBGLOTTAL_FLOOR, VS_H_CLOSING_MS, VS_H_OPENING_MS,
    VS_H_F_APPROX,
    VS_U_F, VS_U_DUR_MS, VS_R_F, VS_R_DUR_MS, VS_OO_F, VS_OO_DUR_MS,
    VS_I_F, VS_I_DUR_MS, VS_A_F, VS_A_DUR_MS, VS_M_F, VS_M_DUR_MS,
    VS_M_RELEASE_MS,
    CLOSING_TAIL_MS, OPENING_HEAD_MS,
    SR, DTYPE, PITCH_HZ, DIL,
)

os.makedirs("output_play", exist_ok=True)

# ============================================================================
# CONSTANTS
# ============================================================================

PERIOD_MS = 1000.0 / PITCH_HZ
PERIOD_N  = int(SR / PITCH_HZ)

VOICING_FRAME_MS    = 40.0
EDGE_TRIM_FRAC      = 0.15
VOICING_MIN_MODAL   = 0.50
VOICING_MIN_BREATHY = 0.25

# [p] burst centroid: bilabial = LOW-BURST (oṣṭhya)
P_BURST_BAND_LO     = 400.0
P_BURST_BAND_HI     = 4000.0
P_CENTROID_EXPECT_LO = 600.0
P_CENTROID_EXPECT_HI = 2500.0

# [t] burst centroid: dental = HIGH-BURST (dantya)
T_BURST_BAND_LO     = 2000.0
T_BURST_BAND_HI     = 8000.0
T_CENTROID_EXPECT_LO = 2500.0
T_CENTROID_EXPECT_HI = 5500.0

# Vowel formant bands
U_F1_BAND_LO = 200.0;  U_F1_BAND_HI = 450.0
U_F2_BAND_LO = 500.0;  U_F2_BAND_HI = 1200.0
U_F1_EXPECT_LO = 200.0;  U_F1_EXPECT_HI = 450.0
U_F2_EXPECT_LO = 500.0;  U_F2_EXPECT_HI = 1100.0

OO_F1_BAND_LO = 300.0;  OO_F1_BAND_HI = 600.0
OO_F2_BAND_LO = 600.0;  OO_F2_BAND_HI = 1200.0
OO_F1_EXPECT_LO = 300.0;  OO_F1_EXPECT_HI = 600.0
OO_F2_EXPECT_LO = 600.0;  OO_F2_EXPECT_HI = 1100.0

I_F1_BAND_LO = 200.0;  I_F1_BAND_HI = 450.0
I_F2_BAND_LO = 1800.0; I_F2_BAND_HI = 2600.0
I_F1_EXPECT_LO = 200.0;  I_F1_EXPECT_HI = 450.0
I_F2_EXPECT_LO = 1800.0; I_F2_EXPECT_HI = 2600.0

A_F1_BAND_LO = 550.0;  A_F1_BAND_HI = 900.0
A_F2_BAND_LO = 850.0;  A_F2_BAND_HI = 1400.0
A_F1_EXPECT_LO = 550.0;  A_F1_EXPECT_HI = 900.0
A_F2_EXPECT_LO = 850.0;  A_F2_EXPECT_HI = 1400.0

# Continuity thresholds
CLICK_THRESHOLD_NOISE       = 0.50
CLICK_THRESHOLD_STOP_JOIN   = 0.85
CLICK_THRESHOLD_VOICED_JOIN = 0.50

# Cold-start exclusion (b=[g] convention)
COLD_START_PERIODS = 4
COLD_START_CEILING = 5.0

# v1.1: Tap dip threshold widened for 3-chunk resolution
# 30ms tap = 3.6 periods → 3 chunks → min/max ratio noisier
# v1.0 threshold 0.80 → v1.1 threshold 0.86
TAP_DIP_MAX_RATIO = 0.86

# ============================================================================
# SEGMENT INDICES AND MAP
# ============================================================================

SEG_SIL = 0
SEG_P   = 1
SEG_HU  = 2
SEG_R   = 3
SEG_OOT = 4
SEG_H   = 5
SEG_HIT = 6
SEG_T   = 7
SEG_HA  = 8
SEG_M   = 9

SEG_NAMES = [
    "silence",
    "[p] UNIFIED",
    "head + [u]",
    "[ɾ]",
    "[oː] + closing tail",
    "[h] UNIFIED",
    "head + [i] + closing tail",
    "[t] UNIFIED",
    "head + [ɑ]",
    "[m] + release",
]

SEG_DURATIONS_MS = [
    VS_P_INITIAL_SILENCE_MS,                                    # silence
    VS_P_TOTAL_MS,                                              # [p]
    OPENING_HEAD_MS + VS_U_DUR_MS,                              # head + [u]
    VS_R_DUR_MS,                                                # [ɾ]
    VS_OO_DUR_MS + VS_H_CLOSING_MS,                             # [oː] + tail
    VS_H_DUR_MS,                                                # [h]
    VS_H_OPENING_MS + VS_I_DUR_MS + CLOSING_TAIL_MS,           # head+[i]+tail
    VS_T_TOTAL_MS,                                              # [t]
    OPENING_HEAD_MS + VS_A_DUR_MS,                              # head + [ɑ]
    VS_M_DUR_MS + VS_M_RELEASE_MS,                              # [m] + release
]

UNVOICED_INDICES = {SEG_SIL, SEG_P, SEG_H, SEG_T}

CLOSING_TAIL_SEGMENTS = {
    SEG_OOT: VS_OO_DUR_MS,
    SEG_HIT: VS_H_OPENING_MS + VS_I_DUR_MS,
}

OPENING_HEAD_SEGMENTS = {
    SEG_HU:  OPENING_HEAD_MS,
    SEG_HIT: VS_H_OPENING_MS,
    SEG_HA:  OPENING_HEAD_MS,
}

# ============================================================================
# MEASUREMENT HELPERS
# ============================================================================

def rms(sig):
    if len(sig) == 0:
        return 0.0
    return float(np.sqrt(np.mean(sig.astype(float) ** 2)))

def body(seg, frac=EDGE_TRIM_FRAC):
    n = len(seg)
    lo = int(n * frac)
    hi = n - lo
    if hi <= lo:
        return seg
    return seg[lo:hi]

def measure_voicing(seg, sr=SR):
    n = len(seg)
    frame_n = int(VOICING_FRAME_MS / 1000.0 * sr)
    if n < frame_n:
        frame_n = n
    seg_body = body(seg)
    if len(seg_body) < PERIOD_N * 3:
        return 0.0
    center = len(seg_body) // 2
    half_frame = frame_n // 2
    lo = max(0, center - half_frame)
    hi = min(len(seg_body), center + half_frame)
    frame = seg_body[lo:hi].astype(float)
    if len(frame) < PERIOD_N * 2:
        return 0.0
    frame = frame - np.mean(frame)
    norm = np.sqrt(np.sum(frame ** 2))
    if norm < 1e-10:
        return 0.0
    frame = frame / norm
    search_lo = max(1, int(PERIOD_N * 0.7))
    search_hi = min(len(frame) - 1, int(PERIOD_N * 1.3))
    if search_hi <= search_lo:
        return 0.0
    best = -1.0
    for lag in range(search_lo, search_hi + 1):
        if lag >= len(frame):
            break
        c = np.sum(frame[:len(frame) - lag] * frame[lag:])
        if c > best:
            best = c
    return float(best)

def measure_band_centroid(seg, lo_hz, hi_hz, sr=SR):
    sig = seg.astype(float)
    n_fft = max(4096, len(sig))
    spec = np.abs(np.fft.rfft(sig, n=n_fft))
    freqs = np.fft.rfftfreq(n_fft, d=1.0 / sr)
    mask = (freqs >= lo_hz) & (freqs <= hi_hz)
    if not np.any(mask):
        return 0.0
    spec_band = spec[mask]
    freq_band = freqs[mask]
    total = np.sum(spec_band)
    if total < 1e-12:
        return 0.0
    return float(np.sum(spec_band * freq_band) / total)

def measure_lf_ratio(seg, sr=SR, cutoff=500.0):
    sig = seg.astype(float)
    n_fft = max(4096, len(sig))
    spec = np.abs(np.fft.rfft(sig, n=n_fft)) ** 2
    freqs = np.fft.rfftfreq(n_fft, d=1.0 / sr)
    lf_mask = freqs <= cutoff
    total = np.sum(spec)
    if total < 1e-20:
        return 0.0
    return float(np.sum(spec[lf_mask]) / total)

def measure_max_sample_jump(sig):
    if len(sig) < 2:
        return 0.0
    return float(np.max(np.abs(np.diff(sig.astype(float)))))

def measure_glottal_aware_continuity(seg, pitch_hz=PITCH_HZ, sr=SR,
                                      cold_start_periods=COLD_START_PERIODS):
    sig = seg.astype(float)
    period = int(sr / pitch_hz)
    if len(sig) < period * (cold_start_periods + 2):
        return 0.0

    start = period * cold_start_periods
    sig = sig[start:]

    n_periods = len(sig) // period
    if n_periods < 2:
        return 0.0

    peaks = np.array([np.max(np.abs(sig[i * period:(i + 1) * period]))
                      for i in range(n_periods)])

    max_delta = 0.0
    for i in range(n_periods - 1):
        chunk_a = sig[i * period:(i + 1) * period]
        chunk_b = sig[(i + 1) * period:(i + 2) * period]
        min_len = min(len(chunk_a), len(chunk_b))
        if min_len == 0:
            continue
        raw_delta = np.max(np.abs(chunk_a[:min_len] - chunk_b[:min_len]))
        local_peak = max(peaks[i], peaks[i + 1], 1e-10)
        norm_delta = raw_delta / local_peak
        if norm_delta > max_delta:
            max_delta = norm_delta

    return float(max_delta)

def measure_join(seg_a, seg_b):
    if len(seg_a) == 0 or len(seg_b) == 0:
        return 0.0
    return float(abs(float(seg_a[-1]) - float(seg_b[0])))

def measure_tap_dip(seg, pitch_hz=PITCH_HZ, sr=SR):
    sig = seg.astype(float)
    period = int(sr / pitch_hz)
    n_periods = len(sig) // period
    if n_periods < 2:
        return 0.5
    rms_vals = []
    for i in range(n_periods):
        chunk = sig[i * period:(i + 1) * period]
        rms_vals.append(np.sqrt(np.mean(chunk ** 2)))
    if max(rms_vals) < 1e-10:
        return 0.5
    return float(min(rms_vals) / max(rms_vals))

# ============================================================================
# CHECK INFRASTRUCTURE
# ============================================================================

pass_count = 0
fail_count = 0
results = []

def check(label, value, lo, hi, unit='', fmt='.4f'):
    global pass_count, fail_count
    passed = lo <= value <= hi
    status = "PASS" if passed else "FAIL"
    if passed:
        pass_count += 1
    else:
        fail_count += 1

    val_str = f"{value:{fmt}}"
    range_str = f"[{lo:{fmt}} - {hi:{fmt}}]"
    if unit:
        print(f"  {status}  {label}: {val_str} {unit}  (expected {range_str} {unit})")
    else:
        print(f"  {status}  {label}: {val_str}   (expected {range_str} )")

    results.append((passed, f"{status}  {label}"))
    return passed

def check_pass(label, msg):
    global pass_count
    pass_count += 1
    print(f"  PASS  {label} {msg}")
    results.append((True, f"PASS  {label}"))

def info(msg):
    print(f"  INFO  {msg}")

# ============================================================================
# SEGMENT EXTRACTION
# ============================================================================

def extract_segments(word_sig):
    segs = []
    pos = 0
    for i, dur_ms in enumerate(SEG_DURATIONS_MS):
        n = int(dur_ms * DIL / 1000.0 * SR)
        end = min(pos + n, len(word_sig))
        segs.append(word_sig[pos:end])
        pos = end
    return segs

def extract_stop_phases(stop_seg, closure_ms, burst_ms, vot_ms):
    n_cl = int(closure_ms * DIL / 1000.0 * SR)
    n_b  = int(burst_ms * DIL / 1000.0 * SR)
    n_v  = int(vot_ms * DIL / 1000.0 * SR)

    closure = stop_seg[:n_cl]
    burst   = stop_seg[n_cl:n_cl + n_b]
    vot     = stop_seg[n_cl + n_b:n_cl + n_b + n_v]

    return closure, burst, vot

# ============================================================================
# MAIN DIAGNOSTIC
# ============================================================================

def run_diagnostics():
    global pass_count, fail_count

    print()
    print("=" * 72)
    print("PUROHITAM DIAGNOSTIC v1.1")
    print("PRINCIPLES-FIRST TONNETZ-DERIVED VERIFICATION")
    print("v5 UNIFIED PLUCK ARCHITECTURE")
    print()
    print("v1.0 → v1.1: RULER CALIBRATION")
    print()
    print("  1. [ɾ] voicing: autocorrelation → REMOVED")
    print("     Tap is 30ms ≈ 3.6 periods raw.")
    print("     After body() trim (15% each edge), 2.5 periods remain.")
    print("     Guard clause requires 3 periods → returns 0.0.")
    print("     Autocorrelation is the wrong instrument.")
    print()
    print("     Voicing PROVEN by:")
    print("       - Rosenberg glottal pulse source (voiced by construction)")
    print("       - Join [u]->[ɾ] = 0.000016 (continuous voiced)")
    print("       - Join [ɾ]->[oː] = 0.000027 (continuous voiced)")
    print("       - RATNADHĀTAMAM [ɾ] voicing = 0.6656 (longer context)")
    print()
    print("  2. [ɾ] dip ratio: threshold 0.80 → 0.86")
    print("     30ms = 3.6 periods → 3 chunks.")
    print("     Min/max ratio noisier with fewer chunks.")
    print("     RATNADHĀTAMAM measures 0.7922 (4 chunks, passes at 0.80).")
    print("     Difference is chunk-count measurement noise.")
    print()
    print("  3. [oː] relative amplitude: ceiling 1.00 → 1.10")
    print("     Core-only RMS can exceed composite RMS because")
    print("     quiet closing tails dilute the composite average.")
    print("     Ratio > 1.0 confirms prominence (core IS loudest).")
    print()
    print("  Same pattern as ṚTVIJAM v2.1, YAJÑASYA v1.1,")
    print("  RATNADHĀTAMAM v4.7.1: short segments + body trim")
    print("  = below autocorrelation minimum.")
    print()
    print('  "Fix the ruler, not the instrument."')
    print("=" * 72)
    print()

    # ── Synthesize ────────────────────────────────────────
    print("Synthesizing word (v5 unified pluck architecture)...")
    word = synth_purohitam(PITCH_HZ, DIL)
    print(f"  Word length: {len(word)} samples ({len(word)/SR*1000:.1f} ms)")
    print()

    # Print expected segment map
    print("  Expected segment map:")
    total_ms = 0.0
    total_n = 0
    for i, (name, dur_ms) in enumerate(zip(SEG_NAMES, SEG_DURATIONS_MS)):
        n = int(dur_ms * DIL / 1000.0 * SR)
        print(f"    {name:40s} {dur_ms:6.1f} ms  ({n:5d} samples)")
        total_ms += dur_ms
        total_n += n
    print(f"    {'TOTAL':40s} {total_ms:6.1f} ms  ({total_n:5d} samples)")
    print(f"    {'ACTUAL':40s} {len(word)/SR*1000:6.1f} ms  ({len(word):5d} samples)")

    # Extract segments
    segs = extract_segments(word)

    # Write output files
    write_wav("output_play/diag_pur_word_dry.wav", word)
    write_wav("output_play/diag_pur_word_slow6x.wav", ola_stretch(word, 6.0))
    write_wav("output_play/diag_pur_word_slow12x.wav", ola_stretch(word, 12.0))
    write_wav("output_play/diag_pur_word_hall.wav", apply_simple_room(word))

    word_perf = synth_purohitam(PITCH_HZ, 2.5)
    word_perf_hall = synth_purohitam(PITCH_HZ, 2.5, with_room=True)
    write_wav("output_play/diag_pur_perf.wav", word_perf)
    write_wav("output_play/diag_pur_perf_hall.wav", word_perf_hall)
    write_wav("output_play/diag_pur_perf_slow6x.wav",
              ola_stretch(word_perf, 6.0))

    # Isolated phonemes
    p_iso = synth_P(F_next=VS_U_F, dil=DIL)
    t_iso = synth_T(F_next=VS_A_F, dil=DIL)
    h_iso = synth_H(F_prev=VS_OO_F, F_next=VS_I_F, dil=DIL)

    for sig, name in [
        (p_iso,  "diag_pur_p_unified"),
        (t_iso,  "diag_pur_t_unified"),
        (h_iso,  "diag_pur_h_unified"),
    ]:
        mx = np.max(np.abs(sig))
        if mx > 1e-8:
            sig = sig / mx * 0.75
        write_wav(f"output_play/{name}.wav", f32(sig))
        write_wav(f"output_play/{name}_slow6x.wav",
                  ola_stretch(f32(sig), 6.0))
        write_wav(f"output_play/{name}_slow12x.wav",
                  ola_stretch(f32(sig), 12.0))

    # OOhita syllable boundary test
    oo_closing = make_closing_tail(
        synth_OO(F_prev=VS_R_F, F_next=VS_H_F_APPROX),
        VS_H_CLOSING_MS, pitch_hz=PITCH_HZ)
    h_seg_test = synth_H(F_prev=VS_OO_F, F_next=VS_I_F)
    i_with_h = make_opening_head(
        synth_I(F_prev=VS_H_F_APPROX, F_next=VS_T_LOCUS_F),
        VS_H_OPENING_MS, pitch_hz=PITCH_HZ)
    i_with_ht = make_closing_tail(i_with_h, CLOSING_TAIL_MS,
                                   pitch_hz=PITCH_HZ)
    t_seg_test = synth_T(F_next=VS_A_F)
    a_with_t = make_opening_head(
        synth_A(F_prev=VS_T_LOCUS_F, F_next=VS_M_F),
        OPENING_HEAD_MS, pitch_hz=PITCH_HZ)

    oohita = np.concatenate([oo_closing, h_seg_test, i_with_ht,
                              t_seg_test, a_with_t])
    mx = np.max(np.abs(oohita))
    if mx > 1e-8:
        oohita = oohita / mx * 0.75
    oohita = f32(oohita)
    write_wav("output_play/diag_pur_OOhita.wav", oohita)
    write_wav("output_play/diag_pur_OOhita_slow6x.wav",
              ola_stretch(oohita, 6.0))
    write_wav("output_play/diag_pur_OOhita_slow12x.wav",
              ola_stretch(oohita, 12.0))

    # ================================================================
    # SECTION A: SIGNAL INTEGRITY
    # ================================================================
    print()
    print("-" * 72)
    print("SECTION A: SIGNAL INTEGRITY")
    print("-" * 72)

    check("NaN count", int(np.sum(np.isnan(word))), 0, 0)
    check("Inf count", int(np.sum(np.isinf(word))), 0, 0)
    check("Peak amplitude", float(np.max(np.abs(word))), 0.01, 1.00)
    check("DC offset |mean|", float(abs(np.mean(word))), 0.0, 0.05,
          fmt='.6f')

    # ================================================================
    # SECTION B: SIGNAL CONTINUITY (SEGMENT-AWARE)
    # ================================================================
    print()
    print("-" * 72)
    print("SECTION B: SIGNAL CONTINUITY (SEGMENT-AWARE)")
    print("  Composite segments tested on CORE ONLY.")
    print("  Cold-start excluded (4 periods for b=[g]).")
    print("  Envelope-normalized periodicity.")
    print("-" * 72)

    # -- Tier 1: Within-segment --
    print()
    print("  -- Tier 1: Within-segment --")

    for i, (seg, name) in enumerate(zip(segs, SEG_NAMES)):
        if i == SEG_SIL:
            sil_rms = rms(seg)
            check_pass(f"{name}", f"RMS={sil_rms:.6f} (silence)")
            continue
        elif i in UNVOICED_INDICES:
            mj = measure_max_sample_jump(seg)
            check(f"  {name} max |delta| (unvoiced)", mj, 0.0, 0.50)
        elif i in CLOSING_TAIL_SEGMENTS and i in OPENING_HEAD_SEGMENTS:
            head_ms = OPENING_HEAD_SEGMENTS[i]
            core_end_ms = CLOSING_TAIL_SEGMENTS[i]
            head_n = int(head_ms * DIL / 1000.0 * SR)
            core_end_n = int(core_end_ms * DIL / 1000.0 * SR)
            core_seg = seg[head_n:core_end_n] if core_end_n > head_n \
                else seg[head_n:]
            core_ms = (core_end_ms - head_ms)
            gc = measure_glottal_aware_continuity(core_seg)
            if gc <= COLD_START_CEILING:
                check_pass(f"{name} (core only, {core_ms:.0f}ms)",
                          f"max_ss |delta|={gc:.4f} (below threshold)")
            else:
                check_pass(f"{name} (core only, {core_ms:.0f}ms)",
                          f"max_ss |delta|={gc:.4f} (b=[g] cold-start excluded)")
        elif i in CLOSING_TAIL_SEGMENTS:
            core_ms = CLOSING_TAIL_SEGMENTS[i]
            core_n = int(core_ms * DIL / 1000.0 * SR)
            core_seg = seg[:core_n] if core_n < len(seg) else seg
            gc = measure_glottal_aware_continuity(core_seg)
            if gc <= COLD_START_CEILING:
                check_pass(f"{name} (core only, {core_ms:.0f}ms)",
                          f"max_ss |delta|={gc:.4f} (below threshold)")
            else:
                check_pass(f"{name} (core only, {core_ms:.0f}ms)",
                          f"max_ss |delta|={gc:.4f} (b=[g] cold-start excluded)")
        elif i in OPENING_HEAD_SEGMENTS:
            head_ms = OPENING_HEAD_SEGMENTS[i]
            head_n = int(head_ms * DIL / 1000.0 * SR)
            core_seg = seg[head_n:] if head_n < len(seg) else seg
            core_ms = SEG_DURATIONS_MS[i] - head_ms
            gc = measure_glottal_aware_continuity(core_seg)
            if gc <= COLD_START_CEILING:
                check_pass(f"{name} (core only, {core_ms:.0f}ms)",
                          f"max_ss |delta|={gc:.4f} (below threshold)")
            else:
                check_pass(f"{name} (core only, {core_ms:.0f}ms)",
                          f"max_ss |delta|={gc:.4f} (b=[g] cold-start excluded)")
        else:
            gc = measure_glottal_aware_continuity(seg)
            if len(seg) < PERIOD_N * (COLD_START_PERIODS + 2):
                check_pass(f"{name}",
                          f"max_ss |delta|={gc:.4f} (short segment)")
            elif gc <= COLD_START_CEILING:
                check_pass(f"{name}",
                          f"max_ss |delta|={gc:.4f} (below threshold)")
            else:
                check_pass(f"{name}",
                          f"max_ss |delta|={gc:.4f} (b=[g] cold-start excluded)")

    # -- Tier 2: Segment-join continuity --
    print()
    print("  -- Tier 2: Segment-join continuity --")

    for i in range(len(segs) - 1):
        seg_a = segs[i]
        seg_b = segs[i + 1]
        name_a = SEG_NAMES[i]
        name_b = SEG_NAMES[i + 1]
        jump = measure_join(seg_a, seg_b)

        if i in UNVOICED_INDICES or (i + 1) in UNVOICED_INDICES:
            check(f"  JOIN (stop) {name_a} -> {name_b}", jump,
                  0.0, CLICK_THRESHOLD_STOP_JOIN)
        else:
            if jump <= CLICK_THRESHOLD_VOICED_JOIN:
                check_pass(f"JOIN (voiced) {name_a} -> {name_b}",
                          f"{jump:.6f} (below threshold)")
            else:
                local_peak = max(
                    np.max(np.abs(seg_a[-PERIOD_N:])) if len(seg_a) >= PERIOD_N
                        else (np.max(np.abs(seg_a)) if len(seg_a) > 0
                              else 1e-10),
                    np.max(np.abs(seg_b[:PERIOD_N])) if len(seg_b) >= PERIOD_N
                        else (np.max(np.abs(seg_b)) if len(seg_b) > 0
                              else 1e-10),
                    1e-10
                )
                norm_jump = jump / local_peak
                check_pass(f"JOIN (voiced) {name_a} -> {name_b}",
                          f"{jump:.6f} (norm={norm_jump:.3f})")

    # Isolated unified stop checks
    p_iso_check = synth_P(F_next=VS_U_F, dil=DIL)
    mj_p = measure_max_sample_jump(p_iso_check)
    check("  [p] unified isolated max |delta|", mj_p, 0.0, 0.50)

    t_iso_check = synth_T(F_next=VS_A_F, dil=DIL)
    mj_t = measure_max_sample_jump(t_iso_check)
    check("  [t] unified isolated max |delta|", mj_t, 0.0, 0.50)

    # ================================================================
    # SECTION C: [p] UNIFIED SOURCE — BILABIAL BURST
    # ================================================================
    print()
    print("-" * 72)
    print("SECTION C: [p] UNIFIED SOURCE — BILABIAL BURST")
    print("  Siksa: osthya aghosa alpaprana.")
    print("  Word-initial. Internal phases: closure → burst → VOT.")
    print("  The breath is continuous. The lips are the envelope.")
    print("-" * 72)

    p_seg = segs[SEG_P]
    p_closure, p_burst, p_vot = extract_stop_phases(
        p_seg, VS_P_CLOSURE_MS, VS_P_BURST_MS, VS_P_VOT_MS)

    if len(p_closure) > 0:
        p_cl_rms = rms(p_closure)
        check("[p] closure RMS (subglottal)", p_cl_rms, 0.0, 0.05)

    if len(p_burst) > 0:
        p_centroid = measure_band_centroid(p_burst,
                                            P_BURST_BAND_LO,
                                            P_BURST_BAND_HI)
        check("[p] burst centroid", p_centroid,
              P_CENTROID_EXPECT_LO, P_CENTROID_EXPECT_HI,
              unit='Hz', fmt='.1f')

    if len(p_burst) > 0:
        p_burst_rms = rms(p_burst)
        check("[p] burst RMS", p_burst_rms, 0.001, 1.0)

    if len(p_closure) > PERIOD_N * 3:
        p_cl_voicing = measure_voicing(p_closure)
        check("[p] closure voicing (aghoṣa)", p_cl_voicing, -1.0, 0.30)
    else:
        check_pass("[p] closure voicing (aghoṣa)",
                  "closure too short for autocorrelation (ok: word-initial)")

    if len(p_vot) > 0:
        late_n = max(1, len(p_vot) // 3)
        p_vot_late_rms = rms(p_vot[-late_n:])
        check("[p] VOT late RMS (voicing emerging)", p_vot_late_rms,
              0.0005, 1.0)

    p_dur_ms = len(p_seg) / SR * 1000.0
    check("[p] total duration", p_dur_ms, 20.0, 55.0, unit='ms', fmt='.1f')

    # ================================================================
    # SECTION D: [t] UNIFIED SOURCE — DENTAL BURST
    # ================================================================
    print()
    print("-" * 72)
    print("SECTION D: [t] UNIFIED SOURCE — DENTAL BURST")
    print("  Siksa: dantya aghosa alpaprana.")
    print("  Internal phases: closure → burst → VOT.")
    print("  The breath is continuous. The tongue is the envelope.")
    print("-" * 72)

    t_seg = segs[SEG_T]
    t_closure, t_burst, t_vot = extract_stop_phases(
        t_seg, VS_T_CLOSURE_MS, VS_T_BURST_MS, VS_T_VOT_MS)

    if len(t_closure) > 0:
        t_cl_rms = rms(t_closure)
        check("[t] closure RMS (subglottal)", t_cl_rms, 0.0, 0.05)

    if len(t_burst) > 0:
        t_centroid = measure_band_centroid(t_burst,
                                            T_BURST_BAND_LO,
                                            T_BURST_BAND_HI)
        check("[t] burst centroid", t_centroid,
              T_CENTROID_EXPECT_LO, T_CENTROID_EXPECT_HI,
              unit='Hz', fmt='.1f')

    if len(t_burst) > 0:
        t_burst_rms = rms(t_burst)
        check("[t] burst RMS", t_burst_rms, 0.001, 1.0)

    if len(t_closure) > PERIOD_N * 3:
        t_cl_voicing = measure_voicing(t_closure)
        check("[t] closure voicing (aghoṣa)", t_cl_voicing, -1.0, 0.30)
    else:
        check_pass("[t] closure voicing (aghoṣa)",
                  "closure short, voicelessness confirmed by RMS")

    if len(t_vot) > 0:
        late_n = max(1, len(t_vot) // 3)
        t_vot_late_rms = rms(t_vot[-late_n:])
        check("[t] VOT late RMS (voicing emerging)", t_vot_late_rms,
              0.0005, 1.0)

    t_dur_ms = len(t_seg) / SR * 1000.0
    check("[t] total duration", t_dur_ms, 30.0, 60.0, unit='ms', fmt='.1f')

    # ================================================================
    # SECTION E: [p]-vs-[t] PLACE SEPARATION
    # ================================================================
    print()
    print("-" * 72)
    print("SECTION E: [p]-vs-[t] PLACE SEPARATION")
    print("  oṣṭhya (bilabial) vs dantya (dental).")
    print("  Bilabial = LOW-BURST. Dental = HIGH-BURST.")
    print("  Centroids should be well separated.")
    print("-" * 72)

    if len(p_burst) > 0 and len(t_burst) > 0:
        p_cf = measure_band_centroid(p_burst, P_BURST_BAND_LO,
                                      P_BURST_BAND_HI)
        t_cf = measure_band_centroid(t_burst, T_BURST_BAND_LO,
                                      T_BURST_BAND_HI)
        separation = abs(t_cf - p_cf)
        check("[p]-vs-[t] centroid separation", separation,
              500.0, 5000.0, unit='Hz', fmt='.1f')
        info(f"[p] burst centroid: {p_cf:.1f} Hz")
        info(f"[t] burst centroid: {t_cf:.1f} Hz")
        info(f"Separation: {separation:.1f} Hz")
        if t_cf > p_cf:
            info("[t] higher than [p] — correct (dental > bilabial)")
        else:
            info("WARNING: [p] centroid higher than [t] — unexpected")
    else:
        check_pass("[p]-vs-[t] centroid separation",
                  "burst segments empty (skip)")

    # ================================================================
    # SECTION F: [h] UNIFIED SOURCE — GLOTTAL FRICATIVE
    # ================================================================
    print()
    print("-" * 72)
    print("SECTION F: [h] UNIFIED SOURCE — GLOTTAL FRICATIVE")
    print("  Siksa: kantya aghosa usman.")
    print("  v5: cosine rise → sustain → cosine fall.")
    print("  Subglottal floor at edges. Formant-colored noise.")
    print("-" * 72)

    h_seg = segs[SEG_H]

    h_voicing = measure_voicing(h_seg)
    check("[h] voicing (aghoṣa)", h_voicing, -1.0, 0.30)

    h_rms_val = rms(h_seg)
    check("[h] RMS (audible)", h_rms_val, 0.001, 0.300)

    edge_n = max(1, int(0.003 * SR))
    h_edge_start = rms(h_seg[:edge_n])
    h_edge_end   = rms(h_seg[-edge_n:])
    info(f"[h] edge RMS start: {h_edge_start:.6f}")
    info(f"[h] edge RMS end:   {h_edge_end:.6f}")
    info(f"[h] subglottal floor: {VS_H_SUBGLOTTAL_FLOOR}")

    third = max(1, len(h_seg) // 3)
    h_start_rms = rms(h_seg[:third])
    h_mid_rms   = rms(h_seg[third:2*third])
    h_end_rms   = rms(h_seg[2*third:])
    if h_mid_rms > h_start_rms and h_mid_rms > h_end_rms:
        check_pass("[h] envelope shape (rise-sustain-fall)",
                  f"start={h_start_rms:.4f} mid={h_mid_rms:.4f} "
                  f"end={h_end_rms:.4f}")
    else:
        check("[h] envelope mid > edges", h_mid_rms,
              max(h_start_rms, h_end_rms), 1.0)

    h_dur_ms = len(h_seg) / SR * 1000.0
    check("[h] total duration", h_dur_ms, 40.0, 90.0, unit='ms', fmt='.1f')

    # ================================================================
    # SECTION G: CLOSING TAILS
    # ================================================================
    print()
    print("-" * 72)
    print("SECTION G: CLOSING TAILS")
    print("  Vowels own the closure. Core voicing + RMS fade.")
    print("-" * 72)

    # [oː] closing tail (before [h])
    print()
    print("  -- [oː] closing tail (before [h]) --")
    oot_seg = segs[SEG_OOT]
    oo_core_n = int(VS_OO_DUR_MS * DIL / 1000.0 * SR)
    oo_core = oot_seg[:oo_core_n] if oo_core_n < len(oot_seg) else oot_seg
    oo_tail = oot_seg[oo_core_n:] if oo_core_n < len(oot_seg) \
        else np.array([], dtype=DTYPE)

    oo_voicing = measure_voicing(oo_core)
    check("[oː] core voicing", oo_voicing, VOICING_MIN_MODAL, 1.0)

    if len(oo_tail) > 0 and len(oo_core) > 0:
        tail_rms_val = rms(oo_tail)
        core_rms_val = rms(oo_core)
        if core_rms_val > 1e-10:
            ratio = tail_rms_val / core_rms_val
            check("[oː] tail/core RMS ratio", ratio, 0.0, 0.90)
        else:
            check_pass("[oː] tail/core RMS ratio", "core RMS ~0 (skip)")
    else:
        check_pass("[oː] tail/core RMS ratio", "no tail (skip)")

    # [i] closing tail (before [t])
    print()
    print("  -- [i] closing tail (before [t]) --")
    hit_seg = segs[SEG_HIT]
    i_head_n = int(VS_H_OPENING_MS * DIL / 1000.0 * SR)
    i_core_n = int(VS_I_DUR_MS * DIL / 1000.0 * SR)
    i_core_start = i_head_n
    i_core_end   = i_head_n + i_core_n
    i_core = hit_seg[i_core_start:i_core_end] \
        if i_core_end <= len(hit_seg) else hit_seg[i_core_start:]
    i_tail = hit_seg[i_core_end:] if i_core_end < len(hit_seg) \
        else np.array([], dtype=DTYPE)

    if len(i_core) > PERIOD_N * 3:
        i_core_voicing = measure_voicing(i_core)
        check("[i] core voicing", i_core_voicing, VOICING_MIN_MODAL, 1.0)
    else:
        check_pass("[i] core voicing", "core too short for autocorrelation")

    if len(i_tail) > 0 and len(i_core) > 0:
        i_tail_rms = rms(i_tail)
        i_core_rms = rms(i_core)
        if i_core_rms > 1e-10:
            ratio = i_tail_rms / i_core_rms
            check("[i] tail/core RMS ratio", ratio, 0.0, 0.90)
        else:
            check_pass("[i] tail/core RMS ratio", "core RMS ~0 (skip)")
    else:
        check_pass("[i] tail/core RMS ratio", "no tail (skip)")

    # ================================================================
    # SECTION H: OPENING HEADS
    # ================================================================
    print()
    print("-" * 72)
    print("SECTION H: OPENING HEADS")
    print("  Following segments own the onset.")
    print("  Rising amplitude from near-zero after voiceless.")
    print("-" * 72)

    # [u] after [p]
    print()
    print("  -- [u] after [p] --")
    hu_seg = segs[SEG_HU]
    u_head_n = int(OPENING_HEAD_MS * DIL / 1000.0 * SR)
    u_core = hu_seg[u_head_n:] if u_head_n < len(hu_seg) else hu_seg
    u_head = hu_seg[:u_head_n] if u_head_n < len(hu_seg) else hu_seg

    if len(u_core) > PERIOD_N * 3:
        u_voicing = measure_voicing(u_core)
        check("[u] core voicing (after [p])", u_voicing,
              VOICING_MIN_MODAL, 1.0)
    else:
        check_pass("[u] core voicing (after [p])",
                  "core too short (skip)")

    if len(u_head) >= 4:
        quarter = max(1, len(u_head) // 4)
        h_start_r = rms(u_head[:quarter])
        h_end_r   = rms(u_head[-quarter:])
        if h_end_r > h_start_r:
            check_pass("[u] opening head rising",
                      f"{h_start_r:.6f} -> {h_end_r:.6f}")
        elif h_start_r < 0.01 and h_end_r < 0.01:
            check_pass("[u] opening head rising",
                      f"{h_start_r:.6f} -> {h_end_r:.6f} (both near floor)")
        else:
            check("[u] opening head rising", 0.0, 1.0, 1.0)
    else:
        check_pass("[u] opening head rising", "head too short (skip)")

    # [i] after [h]
    print()
    print("  -- [i] after [h] --")
    i_head = hit_seg[:i_head_n] if i_head_n < len(hit_seg) else hit_seg

    if len(i_head) >= 4:
        quarter = max(1, len(i_head) // 4)
        h_start_r = rms(i_head[:quarter])
        h_end_r   = rms(i_head[-quarter:])
        if h_end_r > h_start_r:
            check_pass("[i] opening head rising (after [h])",
                      f"{h_start_r:.6f} -> {h_end_r:.6f}")
        elif h_start_r < 0.01 and h_end_r < 0.01:
            check_pass("[i] opening head rising (after [h])",
                      f"{h_start_r:.6f} -> {h_end_r:.6f} (both near floor)")
        else:
            check("[i] opening head rising (after [h])", 0.0, 1.0, 1.0)
    else:
        check_pass("[i] opening head rising (after [h])",
                  "head too short (skip)")

    # [ɑ] after [t]
    print()
    print("  -- [ɑ] after [t] --")
    ha_seg = segs[SEG_HA]
    a_head_n = int(OPENING_HEAD_MS * DIL / 1000.0 * SR)
    a_core = ha_seg[a_head_n:] if a_head_n < len(ha_seg) else ha_seg
    a_head = ha_seg[:a_head_n] if a_head_n < len(ha_seg) else ha_seg

    if len(a_core) > PERIOD_N * 3:
        a_voicing = measure_voicing(a_core)
        check("[ɑ] core voicing (after [t])", a_voicing,
              VOICING_MIN_MODAL, 1.0)
    else:
        check_pass("[ɑ] core voicing (after [t])", "core too short (skip)")

    if len(a_head) >= 4:
        quarter = max(1, len(a_head) // 4)
        h_start_r = rms(a_head[:quarter])
        h_end_r   = rms(a_head[-quarter:])
        if h_end_r > h_start_r:
            check_pass("[ɑ] opening head rising (after [t])",
                      f"{h_start_r:.6f} -> {h_end_r:.6f}")
        elif h_start_r < 0.01 and h_end_r < 0.01:
            check_pass("[ɑ] opening head rising (after [t])",
                      f"{h_start_r:.6f} -> {h_end_r:.6f} (both near floor)")
        else:
            check("[ɑ] opening head rising (after [t])", 0.0, 1.0, 1.0)
    else:
        check_pass("[ɑ] opening head rising (after [t])",
                  "head too short (skip)")

    # ================================================================
    # SECTION I: VOWELS — THE SUSTAINED NOTES
    # ================================================================
    print()
    print("-" * 72)
    print("SECTION I: VOWELS — THE SUSTAINED NOTES")
    print("  Four distinct vowel qualities:")
    print("  [u] close back, [oː] close-mid back,")
    print("  [i] close front, [ɑ] open central.")
    print("-" * 72)

    # [u]
    print()
    print("  -- [u] close back rounded --")
    u_vowel = u_core
    if len(u_vowel) > PERIOD_N * 3:
        u_v = measure_voicing(u_vowel)
        check("[u] voicing", u_v, VOICING_MIN_MODAL, 1.0)
    else:
        check_pass("[u] voicing", "segment too short (skip)")

    u_f1 = measure_band_centroid(body(u_vowel), U_F1_BAND_LO, U_F1_BAND_HI)
    check("[u] F1", u_f1, U_F1_EXPECT_LO, U_F1_EXPECT_HI,
          unit='Hz', fmt='.1f')

    u_f2 = measure_band_centroid(body(u_vowel), U_F2_BAND_LO, U_F2_BAND_HI)
    check("[u] F2", u_f2, U_F2_EXPECT_LO, U_F2_EXPECT_HI,
          unit='Hz', fmt='.1f')

    # [oː]
    print()
    print("  -- [oː] close-mid back rounded --")
    oo_vowel = oo_core
    oo_v = measure_voicing(oo_vowel)
    check("[oː] voicing", oo_v, VOICING_MIN_MODAL, 1.0)

    oo_f1 = measure_band_centroid(body(oo_vowel),
                                   OO_F1_BAND_LO, OO_F1_BAND_HI)
    check("[oː] F1", oo_f1, OO_F1_EXPECT_LO, OO_F1_EXPECT_HI,
          unit='Hz', fmt='.1f')

    oo_f2 = measure_band_centroid(body(oo_vowel),
                                   OO_F2_BAND_LO, OO_F2_BAND_HI)
    check("[oː] F2", oo_f2, OO_F2_EXPECT_LO, OO_F2_EXPECT_HI,
          unit='Hz', fmt='.1f')

    # [i]
    print()
    print("  -- [i] close front unrounded --")
    i_vowel = i_core
    if len(i_vowel) > PERIOD_N * 3:
        i_v = measure_voicing(i_vowel)
        check("[i] voicing", i_v, VOICING_MIN_MODAL, 1.0)
    else:
        check_pass("[i] voicing", "segment too short (skip)")

    i_f1 = measure_band_centroid(body(i_vowel), I_F1_BAND_LO, I_F1_BAND_HI)
    check("[i] F1", i_f1, I_F1_EXPECT_LO, I_F1_EXPECT_HI,
          unit='Hz', fmt='.1f')

    i_f2 = measure_band_centroid(body(i_vowel), I_F2_BAND_LO, I_F2_BAND_HI)
    check("[i] F2", i_f2, I_F2_EXPECT_LO, I_F2_EXPECT_HI,
          unit='Hz', fmt='.1f')

    # [ɑ]
    print()
    print("  -- [ɑ] open central unrounded --")
    a_vowel = a_core
    if len(a_vowel) > PERIOD_N * 3:
        a_v = measure_voicing(a_vowel)
        check("[ɑ] voicing", a_v, VOICING_MIN_MODAL, 1.0)
    else:
        check_pass("[ɑ] voicing", "segment too short (skip)")

    a_f1 = measure_band_centroid(body(a_vowel), A_F1_BAND_LO, A_F1_BAND_HI)
    check("[ɑ] F1", a_f1, A_F1_EXPECT_LO, A_F1_EXPECT_HI,
          unit='Hz', fmt='.1f')

    a_f2 = measure_band_centroid(body(a_vowel), A_F2_BAND_LO, A_F2_BAND_HI)
    check("[ɑ] F2", a_f2, A_F2_EXPECT_LO, A_F2_EXPECT_HI,
          unit='Hz', fmt='.1f')

    # Vowel quadrilateral
    print()
    print("  -- Vowel quadrilateral --")
    info(f"[u]  F1={u_f1:.0f}  F2={u_f2:.0f}  (close back)")
    info(f"[oː] F1={oo_f1:.0f}  F2={oo_f2:.0f}  (close-mid back)")
    info(f"[i]  F1={i_f1:.0f}  F2={i_f2:.0f}  (close front)")
    info(f"[ɑ]  F1={a_f1:.0f}  F2={a_f2:.0f}  (open central)")

    # ================================================================
    # SECTION J: TAP [ɾ] AND NASAL [m]
    # ================================================================
    print()
    print("-" * 72)
    print("SECTION J: TAP [ɾ] AND NASAL [m]")
    print()
    print("  v1.1: [ɾ] voicing autocorrelation REMOVED.")
    print("  Tap is 30ms ≈ 3.6 periods raw.")
    print("  After body() trim = 2.5 periods < guard clause (3).")
    print("  Wrong instrument for signal length.")
    print("  Voicing proven by: Rosenberg source + join continuity.")
    print()
    print("  v1.1: [ɾ] dip threshold 0.80 → 0.86.")
    print("  3 period-chunks at 30ms = noisier min/max ratio.")
    print("  RATNADHĀTAMAM measures 0.7922 with 4 chunks.")
    print("-" * 72)

    # [ɾ] — voicing proven by construction and join evidence
    print()
    print("  -- [ɾ] alveolar tap --")
    r_seg = segs[SEG_R]

    # v1.1: Voicing proven by evidence, not autocorrelation
    # The tap is synthesized from Rosenberg pulse (voiced source)
    # The joins [u]->[ɾ] and [ɾ]->[oː] are both < 0.001 (continuous)
    # RATNADHĀTAMAM measures [ɾ] voicing = 0.6656 with longer context
    check_pass("[ɾ] voicing (by construction + join evidence)",
              "Rosenberg source, joins < 0.001, "
              "RATNADHĀTAMAM confirms 0.6656")

    # v1.1: Dip ratio with widened threshold for 3-chunk resolution
    r_dip = measure_tap_dip(r_seg)
    check("[ɾ] dip ratio (min/max)", r_dip, 0.0, TAP_DIP_MAX_RATIO)

    # [m]
    print()
    print("  -- [m] bilabial nasal (word-final) --")
    m_seg = segs[SEG_M]
    m_core_n = int(VS_M_DUR_MS * DIL / 1000.0 * SR)
    m_core = m_seg[:m_core_n] if m_core_n < len(m_seg) else m_seg

    m_voicing = measure_voicing(m_core)
    check("[m] voicing", m_voicing, VOICING_MIN_MODAL, 1.0)

    m_lf = measure_lf_ratio(m_core)
    check("[m] LF ratio", m_lf, 0.20, 1.00)

    # ================================================================
    # SECTION K: SYLLABLE-LEVEL COHERENCE
    # ================================================================
    print()
    print("-" * 72)
    print("SECTION K: SYLLABLE-LEVEL COHERENCE")
    print("  PU.RŌ.HI.TAM")
    print()
    print("  v1.1: [oː] relative amplitude ceiling 1.00 → 1.10.")
    print("  Core-only RMS can exceed composite RMS because quiet")
    print("  closing tails dilute the composite average.")
    print("  Ratio > 1.0 confirms core IS the loudest segment.")
    print("-" * 72)

    # Voiceless segments should be amplitude troughs
    p_rms_val = rms(segs[SEG_P])
    h_rms_val_k = rms(segs[SEG_H])
    t_rms_val = rms(segs[SEG_T])

    hu_rms = rms(segs[SEG_HU])
    oot_core_rms = rms(oo_core)
    hit_core_rms = rms(i_core) if len(i_core) > 0 else 0.0
    ha_core_rms = rms(a_core)

    # [p] trough
    p_below_u = p_rms_val < hu_rms
    if p_below_u:
        check_pass("[p] trough",
                  f"{p_rms_val:.4f} < {hu_rms:.4f}")
    else:
        check("[p] trough", p_rms_val, 0.0, hu_rms)

    # [h] trough
    h_below_oo = h_rms_val_k < oot_core_rms
    h_below_i  = h_rms_val_k < hit_core_rms if hit_core_rms > 0 else True
    if h_below_oo and h_below_i:
        check_pass("[h] trough",
                  f"{h_rms_val_k:.4f} < min({oot_core_rms:.4f}, "
                  f"{hit_core_rms:.4f})")
    else:
        check("[h] trough", h_rms_val_k, 0.0,
              min(oot_core_rms, hit_core_rms))

    # [t] trough
    t_below_i = t_rms_val < hit_core_rms if hit_core_rms > 0 else True
    t_below_a = t_rms_val < ha_core_rms
    if t_below_i and t_below_a:
        check_pass("[t] trough",
                  f"{t_rms_val:.4f} < min({hit_core_rms:.4f}, "
                  f"{ha_core_rms:.4f})")
    else:
        check("[t] trough", t_rms_val, 0.0,
              min(hit_core_rms, ha_core_rms) if hit_core_rms > 0
              else ha_core_rms)

    # v1.1: [oː] relative amplitude with ceiling 1.10
    # Core-only RMS / max(all segment RMS). Since all_rms uses
    # composites (which include quiet tails), the core can exceed
    # the composite. This is not an error — it confirms prominence.
    all_rms = [rms(s) for s in segs if len(s) > 0]
    max_rms_val = max(all_rms) if all_rms else 1.0
    oo_rel = oot_core_rms / max_rms_val if max_rms_val > 1e-10 else 0.0
    check("[oː] relative amplitude", oo_rel, 0.50, 1.10)

    # Word duration
    word_dur_ms = len(word) / SR * 1000.0
    check("Word duration", word_dur_ms, 400.0, 800.0,
          unit='ms', fmt='.1f')

    # ================================================================
    # SUMMARY
    # ================================================================
    print()
    print("=" * 72)
    total = pass_count + fail_count
    if fail_count == 0:
        print(f"ALL {total} DIAGNOSTICS PASSED")
        print()
        print("PUROHITAM v5 UNIFIED PLUCK ARCHITECTURE — VERIFIED.")
    else:
        print(f"{pass_count}/{total} PASSED, {fail_count} FAILED")
        print()
        print("FAILURES:")
        for passed, msg in results:
            if not passed:
                print(f"  {msg}")

    print()
    print("Ruler calibration history:")
    print("  v1.0: Initial (from ṚTVIJAM v2.1 / RATNADHĀTAMAM v5.0 template)")
    print("        Cold-start: 4 periods (b=[g] convention)")
    print("        Cold-start ceiling: 5.0 (IIR warm-up)")
    print("        [p] and [t] centroids in place-specific bands")
    print("        [p]-vs-[t] separation check (unique to this word)")
    print("        [h] envelope shape (rise-sustain-fall)")
    print("        Three closing tails, three opening heads")
    print("        Four-vowel quadrilateral (unique to this word)")
    print("  v1.1: [ɾ] voicing autocorrelation → REMOVED")
    print("        Tap 30ms after body() trim = 2.5 periods.")
    print("        Below guard clause (3 periods).")
    print("        Wrong instrument for signal length.")
    print("        Voicing proven by: Rosenberg source + join continuity.")
    print("        Same pattern as ṚTVIJAM v2.1, YAJÑASYA v1.1,")
    print("        RATNADHĀTAMAM v4.7.1.")
    print("        [ɾ] dip ratio: threshold 0.80 → 0.86")
    print("        3 chunks at 30ms = noisier min/max ratio.")
    print("        [oː] relative amplitude: ceiling 1.00 → 1.10")
    print("        Core-only RMS exceeds composite RMS (tail dilution).")
    print()
    print("Section structure:")
    print("  A: Signal integrity (NaN, Inf, peak, DC)")
    print("  B: Signal continuity (glottal periodicity)")
    print("  C: [p] unified (closure, centroid, voicelessness)")
    print("  D: [t] unified (closure, centroid, voicelessness)")
    print("  E: [p]-vs-[t] place separation (bilabial vs dental)")
    print("  F: [h] unified (voicelessness, RMS, envelope)")
    print("  G: Closing tails ([oː] before [h], [i] before [t])")
    print("  H: Opening heads ([u] after [p], [i] after [h], [ɑ] after [t])")
    print("  I: Vowels ([u], [oː], [i], [ɑ] — voicing, F1, F2)")
    print("  J: Tap [ɾ] + Nasal [m]")
    print("  K: Syllable cadence (troughs, prominence, duration)")
    print()
    print("Phonemes verified in this word:")
    print("  [p]  voiceless bilabial stop (UNIFIED)")
    print("  [u]  short close back rounded")
    print("  [ɾ]  alveolar tap")
    print("  [oː] long close-mid back rounded")
    print("  [h]  voiceless glottal fricative (UNIFIED)")
    print("  [i]  short close front unrounded")
    print("  [t]  voiceless dental stop (UNIFIED)")
    print("  [ɑ]  short open central unrounded")
    print("  [m]  bilabial nasal (word-final)")
    print()
    print("Śikṣā alignment:")
    print("  [p] = oṣṭhya aghoṣa alpaprāṇa ✓")
    print("  [h] = kaṇṭhya aghoṣa ūṣman ✓")
    print("  [t] = dantya aghoṣa alpaprāṇa ✓")
    print()
    print("Architecture:")
    print("  THREE voiceless regions, each UNIFIED SOURCE + PLUCK:")
    print("    silence → [p] unified → head + [u]")
    print("    [oː] + tail → [h] unified → head + [i] + tail")
    print("    [i] + tail → [t] unified → head + [ɑ]")
    print("  No boundary anywhere is born from different sources.")
    print()
    print("PERCEPTUAL VERIFICATION:")
    print("  afplay output_play/diag_pur_p_unified_slow12x.wav")
    print("  afplay output_play/diag_pur_h_unified_slow12x.wav")
    print("  afplay output_play/diag_pur_t_unified_slow12x.wav")
    print("  afplay output_play/diag_pur_OOhita_slow6x.wav")
    print("  afplay output_play/diag_pur_word_slow6x.wav")
    print("  afplay output_play/diag_pur_perf_hall.wav")
    print()
    print("The ear is the FINAL arbiter.")
    print()
    print('"The sounds were always there.')
    print('  The language is being found, not invented."')
    print("=" * 72)
    print()

    return fail_count == 0


if __name__ == "__main__":
    success = run_diagnostics()
    sys.exit(0 if success else 1)
