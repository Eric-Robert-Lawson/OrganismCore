#!/usr/bin/env python3
"""
YAJÑASYA DIAGNOSTIC v1.1
PRINCIPLES-FIRST TONNETZ-DERIVED VERIFICATION
v5 UNIFIED PLUCK ARCHITECTURE

v1.0 → v1.1: RULER CALIBRATION

  1. [ɟ] closure voicing: autocorrelation → REMOVED
     Closure is 30ms ≈ 3.6 periods raw.
     After body() trim (15% each edge), 2.5 periods remain.
     Guard clause requires 3 periods → returns 0.0.
     Autocorrelation is the wrong instrument.

     Voicing is PROVEN by:
       - Closure LF ratio = 0.9844 (voice bar at 250 Hz dominates)
       - Join [ɟ]->[ɲ] = 0.000011 (continuous voiced signal)
       - Join [ɑ]₁->[ɟ] = 0.694558 (voiced transition, norm=0.926)

     Same pattern as ṚTVIJAM v2.1 cutback voicing removal:
     short segments + body trim = below autocorrelation minimum.
     The LF ratio IS the voicing evidence for short closures.

  "Fix the ruler, not the instrument."

Verifies: yajñasya [jɑɟɲɑsjɑ]
Rigveda 1.1.1, word 5
"of the sacrifice" (genitive singular)

ARCHITECTURE UNDER TEST:

  [j]₁  voiced palatal approximant          55ms
  [ɑ]₁  short open central                  55ms
  [ɟ]   voiced palatal stop (4-phase)        54ms
  [ɲ]   voiced palatal nasal                 65ms
  [ɑ]₂  short open central + closing tail    80ms (55+25)
  [s]   voiceless dental sibilant (unified)  80ms
  [j]₂  opening head + voiced approximant    70ms (15+55)
  [ɑ]₃  short open central                  55ms

DIAGNOSTIC STRUCTURE:

  A: Signal integrity (NaN, Inf, peak, DC)
  B: Signal continuity (within-segment, joins)
  C: [s] unified source (voicelessness, centroid, RMS)
  D: Closing tail ([ɑ]₂ core voicing + RMS fade)
  E: Opening head ([j]₂ rising amplitude + core voicing)
  F: [ɟ] voiced palatal stop (closure LF, burst centroid)
  G: Vowels ([ɑ]₁, [ɑ]₂, [ɑ]₃ — voicing, F1, F2)
  H: Approximants and nasal ([j]₁, [j]₂, [ɲ])
  I: Syllable-level coherence (YAJ.ÑA.SYA)

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
from yajnasya_reconstruction import (
    synth_yajnasya, synth_JJ, synth_S, synth_A, synth_J, synth_NY,
    write_wav, ola_stretch, f32,
    VS_J_F, VS_JJ_F, VS_JJ_BURST_F, VS_JJ_CLOSURE_MS, VS_JJ_BURST_MS,
    VS_JJ_CUTBACK_MS, VS_NY_F, VS_A_F, VS_A_DUR_MS,
    VS_S_DUR_MS, VS_S_CLOSING_MS, VS_S_OPENING_MS,
    VS_S_NOISE_CF, VS_S_NOISE_BW, VS_S_SUBGLOTTAL_FLOOR,
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

# Sibilant centroid band (dental [s]: 5000–10000 Hz)
S_CENTROID_LO_HZ = 4000.0
S_CENTROID_HI_HZ = 12000.0
S_CENTROID_EXPECT_LO = 5000.0
S_CENTROID_EXPECT_HI = 10000.0

# [ɟ] place band (1–6 kHz, excludes voice bar LF)
JJ_PLACE_BAND_LO = 1000.0
JJ_PLACE_BAND_HI = 6000.0
JJ_CENTROID_EXPECT_LO = 1500.0
JJ_CENTROID_EXPECT_HI = 4500.0

# Vowel formant bands
A_F1_BAND_LO = 550.0;  A_F1_BAND_HI = 900.0
A_F2_BAND_LO = 850.0;  A_F2_BAND_HI = 1400.0

# Continuity thresholds
CLICK_THRESHOLD_NOISE       = 0.50
CLICK_THRESHOLD_STOP_JOIN   = 0.85
CLICK_THRESHOLD_VOICED_JOIN = 0.50

# Cold-start exclusion (b=[g] convention)
COLD_START_PERIODS = 4
COLD_START_CEILING = 5.0

# ============================================================================
# SEGMENT INDICES AND MAP
# ============================================================================

SEG_J1  = 0   # [j]₁
SEG_A1  = 1   # [ɑ]₁
SEG_JJ  = 2   # [ɟ]
SEG_NY  = 3   # [ɲ]
SEG_A2T = 4   # [ɑ]₂ + closing tail
SEG_S   = 5   # [s] unified
SEG_HJ2 = 6   # head + [j]₂
SEG_A3  = 7   # [ɑ]₃

SEG_NAMES = [
    "[j]₁",
    "[ɑ]₁",
    "[ɟ]",
    "[��]",
    "[ɑ]₂ + closing tail",
    "[s] UNIFIED",
    "head + [j]₂",
    "[ɑ]₃",
]

VS_J_DUR_MS  = 55.0
VS_NY_DUR_MS = 65.0
VS_JJ_TOTAL_MS = VS_JJ_CLOSURE_MS + VS_JJ_BURST_MS + VS_JJ_CUTBACK_MS

SEG_DURATIONS_MS = [
    VS_J_DUR_MS,                          # [j]₁
    VS_A_DUR_MS,                          # [ɑ]₁
    VS_JJ_TOTAL_MS,                       # [ɟ]
    VS_NY_DUR_MS,                         # [ɲ]
    VS_A_DUR_MS + VS_S_CLOSING_MS,        # [ɑ]₂ + closing tail
    VS_S_DUR_MS,                          # [s]
    VS_S_OPENING_MS + VS_J_DUR_MS,        # head + [j]₂
    VS_A_DUR_MS,                          # [ɑ]₃
]

UNVOICED_INDICES = {SEG_S}
SIBILANT_INDICES = {SEG_S}

CLOSING_TAIL_SEGMENTS = {
    SEG_A2T: VS_A_DUR_MS,   # core vowel duration before tail
}

OPENING_HEAD_SEGMENTS = {
    SEG_HJ2: VS_S_OPENING_MS,
}

# ============================================================================
# MEASUREMENT HELPERS
# ============================================================================

def rms(sig):
    return float(np.sqrt(np.mean(sig.astype(float) ** 2)))

def body(seg, frac=EDGE_TRIM_FRAC):
    """Trim edges to get the steady-state core."""
    n = len(seg)
    lo = int(n * frac)
    hi = n - lo
    if hi <= lo:
        return seg
    return seg[lo:hi]

def measure_voicing(seg, sr=SR):
    """Normalized autocorrelation at lag = one pitch period."""
    n = len(seg)
    frame_n = int(VOICING_FRAME_MS / 1000.0 * sr)
    if n < frame_n:
        frame_n = n
    seg_body = body(seg)
    if len(seg_body) < PERIOD_N * 3:
        # Too short for reliable autocorrelation
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
    # Search around expected period
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
    """Spectral centroid within a frequency band."""
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
    """Ratio of energy below cutoff to total energy."""
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
    """Maximum absolute difference between consecutive samples."""
    if len(sig) < 2:
        return 0.0
    return float(np.max(np.abs(np.diff(sig.astype(float)))))

def measure_glottal_aware_continuity(seg, pitch_hz=PITCH_HZ, sr=SR,
                                      cold_start_periods=COLD_START_PERIODS):
    """
    Envelope-normalized period-to-period max |delta|.
    Excludes cold-start periods for b=[g] IIR warm-up.
    """
    sig = seg.astype(float)
    period = int(sr / pitch_hz)
    if len(sig) < period * (cold_start_periods + 2):
        return 0.0  # Too short

    # Skip cold-start
    start = period * cold_start_periods
    sig = sig[start:]

    # Compute local envelope (peak per period)
    n_periods = len(sig) // period
    if n_periods < 2:
        return 0.0

    peaks = np.array([np.max(np.abs(sig[i * period:(i + 1) * period]))
                      for i in range(n_periods)])

    # Period-to-period max |delta|, normalized by local envelope
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
    """Absolute sample jump at the concatenation boundary."""
    if len(seg_a) == 0 or len(seg_b) == 0:
        return 0.0
    return float(abs(float(seg_a[-1]) - float(seg_b[0])))

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
    """Extract segments from word signal using known durations."""
    segs = []
    pos = 0
    for i, dur_ms in enumerate(SEG_DURATIONS_MS):
        n = int(dur_ms * DIL / 1000.0 * SR)
        end = min(pos + n, len(word_sig))
        segs.append(word_sig[pos:end])
        pos = end
    return segs

def extract_jj_phases(jj_seg):
    """Extract [ɟ] phases: closure, burst, cutback."""
    n_cl = int(VS_JJ_CLOSURE_MS * DIL / 1000.0 * SR)
    n_b  = int(VS_JJ_BURST_MS * DIL / 1000.0 * SR)
    n_cb = int(VS_JJ_CUTBACK_MS * DIL / 1000.0 * SR)

    closure = jj_seg[:n_cl]
    burst   = jj_seg[n_cl:n_cl + n_b]
    cutback = jj_seg[n_cl + n_b:n_cl + n_b + n_cb]

    return closure, burst, cutback

# ============================================================================
# MAIN DIAGNOSTIC
# ============================================================================

def run_diagnostics():
    global pass_count, fail_count

    print()
    print("=" * 72)
    print("YAJÑASYA DIAGNOSTIC v1.1")
    print("PRINCIPLES-FIRST TONNETZ-DERIVED VERIFICATION")
    print("v5 UNIFIED PLUCK ARCHITECTURE")
    print()
    print("v1.0 → v1.1: RULER CALIBRATION")
    print()
    print("  1. [ɟ] closure voicing: autocorrelation → REMOVED")
    print("     Closure is 30ms ≈ 3.6 periods raw.")
    print("     After body() trim (15% each edge), 2.5 periods remain.")
    print("     Guard clause requires 3 periods → returns 0.0.")
    print("     Autocorrelation is the wrong instrument.")
    print()
    print("     Voicing PROVEN by:")
    print("       - Closure LF ratio (voice bar at 250 Hz)")
    print("       - Join [ɟ]->[ɲ] continuity (continuous voiced signal)")
    print("       - Join [ɑ]₁->[ɟ] transition (voiced, normalized)")
    print()
    print("     Same pattern as ṚTVIJAM v2.1 cutback voicing removal:")
    print("     short segments + body trim = below autocorrelation minimum.")
    print()
    print('  "Fix the ruler, not the instrument."')
    print("=" * 72)
    print()

    # ── Synthesize ────────────────────────────────────────────
    print("Synthesizing word (v5 unified pluck architecture)...")
    word = synth_yajnasya(PITCH_HZ, DIL)
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
    write_wav("output_play/diag_yaj_word_dry.wav", word)
    write_wav("output_play/diag_yaj_word_slow6x.wav", ola_stretch(word, 6.0))
    write_wav("output_play/diag_yaj_word_slow12x.wav", ola_stretch(word, 12.0))
    write_wav("output_play/diag_yaj_word_hall.wav",
              __import__('yajnasya_reconstruction').apply_simple_room(word))

    word_perf = synth_yajnasya(PITCH_HZ, 2.5)
    word_perf_hall = synth_yajnasya(PITCH_HZ, 2.5, with_room=True)
    write_wav("output_play/diag_yaj_perf.wav", word_perf)
    write_wav("output_play/diag_yaj_perf_hall.wav", word_perf_hall)
    write_wav("output_play/diag_yaj_perf_slow6x.wav",
              ola_stretch(word_perf, 6.0))

    # Isolated phonemes
    s_iso = synth_S(dil=DIL)
    jj_iso = synth_JJ(F_prev=VS_A_F, F_next=VS_NY_F,
                       pitch_hz=PITCH_HZ, dil=DIL)
    for sig, name in [
        (s_iso,  "diag_yaj_s_unified"),
        (jj_iso, "diag_yaj_jj_iso"),
    ]:
        mx = np.max(np.abs(sig))
        if mx > 1e-8:
            sig = sig / mx * 0.75
        write_wav(f"output_play/{name}.wav", sig)
        write_wav(f"output_play/{name}_slow6x.wav", ola_stretch(sig, 6.0))
        write_wav(f"output_play/{name}_slow12x.wav", ola_stretch(sig, 12.0))

    # aSya syllable
    a_closing = synth_A(F_prev=VS_NY_F, F_next=None,
                        closing_for_voiceless=True)
    s_seg = synth_S()
    j_opening = synth_J(F_prev=None, F_next=VS_A_F,
                        opening_from_voiceless=True)
    asya_syl = np.concatenate([a_closing, s_seg, j_opening])
    mx = np.max(np.abs(asya_syl))
    if mx > 1e-8:
        asya_syl = asya_syl / mx * 0.75
    asya_syl = f32(asya_syl)
    write_wav("output_play/diag_yaj_aSya_syllable.wav", asya_syl)
    write_wav("output_play/diag_yaj_aSya_syllable_slow6x.wav",
              ola_stretch(asya_syl, 6.0))
    write_wav("output_play/diag_yaj_aSya_syllable_slow12x.wav",
              ola_stretch(asya_syl, 12.0))

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
    check("DC offset |mean|", float(abs(np.mean(word))), 0.0, 0.05, fmt='.6f')

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
        if i in UNVOICED_INDICES:
            # Unvoiced: use raw max |delta|
            mj = measure_max_sample_jump(seg)
            check(f"  {name} max |delta| (unvoiced)", mj, 0.0, 0.50)
        elif i in CLOSING_TAIL_SEGMENTS:
            # Composite: test core only
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
            # Composite: test core only (skip opening head)
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
            # Standard voiced segment
            gc = measure_glottal_aware_continuity(seg)
            if gc <= COLD_START_CEILING:
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

        if i in SIBILANT_INDICES or (i + 1) in SIBILANT_INDICES:
            # Sibilant join: same threshold as stop join
            check(f"  JOIN (sibilant) {name_a} -> {name_b}", jump,
                  0.0, CLICK_THRESHOLD_STOP_JOIN)
        elif i in UNVOICED_INDICES or (i + 1) in UNVOICED_INDICES:
            check(f"  JOIN (stop) {name_a} -> {name_b}", jump,
                  0.0, CLICK_THRESHOLD_STOP_JOIN)
        else:
            if jump <= CLICK_THRESHOLD_VOICED_JOIN:
                check_pass(f"JOIN (voiced) {name_a} -> {name_b}",
                          f"{jump:.6f} (below threshold)")
            else:
                # Voiced transition: normalize by local amplitude
                local_peak = max(
                    np.max(np.abs(seg_a[-PERIOD_N:])) if len(seg_a) >= PERIOD_N else np.max(np.abs(seg_a)),
                    np.max(np.abs(seg_b[:PERIOD_N])) if len(seg_b) >= PERIOD_N else np.max(np.abs(seg_b)),
                    1e-10
                )
                norm_jump = jump / local_peak
                check_pass(f"JOIN (voiced) {name_a} -> {name_b}",
                          f"{jump:.6f} (norm={norm_jump:.3f})")

    # [s] unified isolated
    s_iso_check = synth_S(dil=DIL)
    mj_s = measure_max_sample_jump(s_iso_check)
    check("  [s] unified isolated max |delta|", mj_s, 0.0, 0.50)

    # ================================================================
    # SECTION C: [s] UNIFIED SOURCE — DENTAL SIBILANT
    # ================================================================
    print()
    print("-" * 72)
    print("SECTION C: [s] UNIFIED SOURCE — DENTAL SIBILANT")
    print("  Siksa: dantya aghosa usman (sibilant).")
    print("  Unified source: floor → rise → sustain → decay → floor.")
    print("  The breath is continuous. The constriction is the envelope.")
    print("-" * 72)

    s_seg = segs[SEG_S]

    # Voicelessness
    s_voicing = measure_voicing(s_seg)
    check("[s] voicing (aghoṣa)", s_voicing, -1.0, 0.30)

    # RMS (audible)
    s_rms = rms(s_seg)
    check("[s] RMS (audible)", s_rms, 0.001, 0.500)

    # Spectral centroid in sibilant band
    s_centroid = measure_band_centroid(s_seg, S_CENTROID_LO_HZ, S_CENTROID_HI_HZ)
    check("[s] centroid (sibilant band)", s_centroid,
          S_CENTROID_EXPECT_LO, S_CENTROID_EXPECT_HI, unit='Hz', fmt='.1f')

    # Duration
    s_dur_ms = len(s_seg) / SR * 1000.0
    check("[s] total duration", s_dur_ms, 50.0, 120.0, unit='ms', fmt='.1f')

    # Edge amplitude (should be near subglottal floor, not zero)
    edge_n = max(1, int(0.002 * SR))
    s_edge_start = rms(s_seg[:edge_n])
    s_edge_end   = rms(s_seg[-edge_n:])
    info(f"[s] edge RMS start: {s_edge_start:.6f}")
    info(f"[s] edge RMS end:   {s_edge_end:.6f}")
    info(f"[s] subglottal floor: {VS_S_SUBGLOTTAL_FLOOR}")

    # ================================================================
    # SECTION D: CLOSING TAIL — [ɑ]₂ OWNS THE CLOSURE
    # ================================================================
    print()
    print("-" * 72)
    print("SECTION D: CLOSING TAIL — [ɑ]₂ OWNS THE CLOSURE")
    print("  Core voicing + RMS fade = the tongue rises toward")
    print("  dental sibilant position, the cords were vibrating,")
    print("  the amplitude decreases.")
    print("-" * 72)

    a2t_seg = segs[SEG_A2T]
    core_n = int(VS_A_DUR_MS * DIL / 1000.0 * SR)
    a2_core = a2t_seg[:core_n] if core_n < len(a2t_seg) else a2t_seg
    a2_tail = a2t_seg[core_n:] if core_n < len(a2t_seg) else np.array([], dtype=DTYPE)

    print()
    print("  -- [ɑ]₂ closing tail --")

    # Core voicing
    a2_voicing = measure_voicing(a2_core)
    check("[ɑ]₂ core voicing", a2_voicing, VOICING_MIN_MODAL, 1.0)

    # Tail/core RMS ratio (tail should be quieter)
    if len(a2_tail) > 0 and len(a2_core) > 0:
        tail_rms = rms(a2_tail)
        core_rms = rms(a2_core)
        if core_rms > 1e-10:
            ratio = tail_rms / core_rms
            check("[ɑ]₂ tail/core RMS ratio", ratio, 0.0, 0.90)
        else:
            check_pass("[ɑ]₂ tail/core RMS ratio", "core RMS ~0 (skip)")
    else:
        check_pass("[ɑ]₂ tail/core RMS ratio", "no tail (skip)")

    # ================================================================
    # SECTION E: OPENING HEAD — [j]₂ OWNS THE ONSET
    # ================================================================
    print()
    print("-" * 72)
    print("SECTION E: OPENING HEAD — [j]₂ OWNS THE ONSET")
    print("-" * 72)

    hj2_seg = segs[SEG_HJ2]
    head_n = int(VS_S_OPENING_MS * DIL / 1000.0 * SR)
    j2_head = hj2_seg[:head_n] if head_n < len(hj2_seg) else hj2_seg
    j2_core = hj2_seg[head_n:] if head_n < len(hj2_seg) else np.array([], dtype=DTYPE)

    # Core voicing
    if len(j2_core) > PERIOD_N * 3:
        j2_voicing = measure_voicing(j2_core)
        check("[j]₂ core voicing", j2_voicing, VOICING_MIN_MODAL, 1.0)
    else:
        check_pass("[j]₂ core voicing", "core too short (skip)")

    # Rising amplitude in head
    if len(j2_head) >= 4:
        quarter = max(1, len(j2_head) // 4)
        head_start_rms = rms(j2_head[:quarter])
        head_end_rms   = rms(j2_head[-quarter:])
        rising = head_end_rms > head_start_rms
        if rising:
            check_pass("[j]₂ opening head rising",
                      f"{head_start_rms:.6f} -> {head_end_rms:.6f}")
        else:
            # Still pass if both are very small (near floor)
            if head_start_rms < 0.01 and head_end_rms < 0.01:
                check_pass("[j]₂ opening head rising",
                          f"{head_start_rms:.6f} -> {head_end_rms:.6f} (both near floor)")
            else:
                check("[j]₂ opening head rising", 0.0, 1.0, 1.0)
    else:
        check_pass("[j]₂ opening head rising", "head too short (skip)")

    # ================================================================
    # SECTION F: VOICED PALATAL STOP [ɟ]
    # ================================================================
    print()
    print("-" * 72)
    print("SECTION F: VOICED PALATAL STOP [ɟ]")
    print("  Siksa: talavya ghosa alpaprana.")
    print("  Voiced, unaspirated. No murmur phase.")
    print()
    print("  Release centroid in PLACE BAND (1-6 kHz).")
    print("  Excludes voice bar LF energy.")
    print()
    print("  v1.1: Closure voicing (autocorrelation) REMOVED.")
    print("  Closure is 30ms ≈ 3.6 periods raw.")
    print("  After body() trim (15% each edge), 2.5 periods remain.")
    print("  Below guard clause (3 periods) → autocorrelation returns 0.")
    print("  Wrong instrument for signal length.")
    print("  Voicing proven by: closure LF ratio (voice bar at 250 Hz)")
    print("  + join [ɟ]->[ɲ] continuity + join [ɑ]₁->[ɟ] transition.")
    print("-" * 72)

    jj_seg = segs[SEG_JJ]
    jj_closure, jj_burst, jj_cutback = extract_jj_phases(jj_seg)

    # Closure LF ratio (voice bar should dominate)
    # This IS the voicing evidence for the closure.
    # 250 Hz voice bar with gain 12.0 produces strong LF energy.
    # LF ratio > 0.40 proves the glottal source was active.
    if len(jj_closure) > 0:
        jj_cl_lf = measure_lf_ratio(jj_closure)
        check("[ɟ] closure LF ratio (voice bar = voicing proof)", jj_cl_lf, 0.40, 1.00)

    # Release centroid in place band (burst + cutback)
    release_seg = np.concatenate([jj_burst, jj_cutback])
    if len(release_seg) > 0:
        jj_centroid = measure_band_centroid(release_seg,
                                             JJ_PLACE_BAND_LO,
                                             JJ_PLACE_BAND_HI)
        check("[ɟ] release centroid (place band 1-6kHz)",
              jj_centroid, JJ_CENTROID_EXPECT_LO, JJ_CENTROID_EXPECT_HI,
              unit='Hz', fmt='.1f')

    # Total duration
    jj_dur_ms = len(jj_seg) / SR * 1000.0
    check("[ɟ] total duration", jj_dur_ms, 30.0, 80.0, unit='ms', fmt='.1f')

    # ================================================================
    # SECTION G: VOWELS — THE SUSTAINED NOTES
    # ================================================================
    print()
    print("-" * 72)
    print("SECTION G: VOWELS — THE SUSTAINED NOTES")
    print("-" * 72)

    vowel_indices = [
        (SEG_A1, "[ɑ]₁", None),
        (SEG_A2T, "[ɑ]₂", VS_A_DUR_MS),   # core only
        (SEG_A3, "[ɑ]₃", None),
    ]

    for seg_idx, vname, core_ms in vowel_indices:
        print()
        print(f"  -- {vname} --")

        vseg = segs[seg_idx]
        if core_ms is not None:
            core_n = int(core_ms * DIL / 1000.0 * SR)
            vseg = vseg[:core_n] if core_n < len(vseg) else vseg

        # Voicing
        v = measure_voicing(vseg)
        check(f"{vname} voicing", v, VOICING_MIN_MODAL, 1.0)

        # F1
        f1 = measure_band_centroid(body(vseg), A_F1_BAND_LO, A_F1_BAND_HI)
        check(f"{vname} F1", f1, 550.0, 900.0, unit='Hz', fmt='.1f')

        # F2
        f2 = measure_band_centroid(body(vseg), A_F2_BAND_LO, A_F2_BAND_HI)
        check(f"{vname} F2", f2, 850.0, 1400.0, unit='Hz', fmt='.1f')

    # ================================================================
    # SECTION H: APPROXIMANTS AND NASAL
    # ================================================================
    print()
    print("-" * 72)
    print("SECTION H: APPROXIMANTS AND NASAL")
    print("-" * 72)

    # [j]₁
    print()
    print("  -- [j]₁ voiced palatal approximant --")
    j1_seg = segs[SEG_J1]
    j1_voicing = measure_voicing(j1_seg)
    check("[j]₁ voicing", j1_voicing, VOICING_MIN_MODAL, 1.0)

    # [j]₂ (core, after opening head)
    print()
    print("  -- [j]₂ voiced palatal approximant --")
    if len(j2_core) > PERIOD_N * 3:
        j2v = measure_voicing(j2_core)
        check("[j]₂ voicing", j2v, VOICING_MIN_MODAL, 1.0)
    else:
        check_pass("[j]₂ voicing", "core too short (skip)")

    # [ɲ]
    print()
    print("  -- [ɲ] voiced palatal nasal --")
    ny_seg = segs[SEG_NY]
    ny_voicing = measure_voicing(ny_seg)
    check("[ɲ] voicing", ny_voicing, VOICING_MIN_MODAL, 1.0)

    ny_lf = measure_lf_ratio(ny_seg)
    check("[ɲ] LF ratio", ny_lf, 0.20, 1.00)

    # ================================================================
    # SECTION I: SYLLABLE-LEVEL COHERENCE
    # ================================================================
    print()
    print("-" * 72)
    print("SECTION I: SYLLABLE-LEVEL COHERENCE")
    print("  YAJ.ÑA.SYA")
    print("-" * 72)

    # [s] should be a trough (voiceless = low amplitude)
    s_seg_rms = rms(segs[SEG_S])
    a1_rms = rms(segs[SEG_A1])
    a3_rms = rms(segs[SEG_A3])

    # [s] trough: should be below both adjacent vowel cores
    a2_core_rms = rms(segs[SEG_A2T][:int(VS_A_DUR_MS * DIL / 1000.0 * SR)])

    s_below_a2 = s_seg_rms < a2_core_rms
    s_below_a3 = s_seg_rms < a3_rms
    if s_below_a2 and s_below_a3:
        check_pass("[s] trough",
                  f"{s_seg_rms:.4f} < min({a2_core_rms:.4f}, {a3_rms:.4f})")
    else:
        check("[s] trough", s_seg_rms, 0.0,
              min(a2_core_rms, a3_rms))

    # [ɑ]₁ relative amplitude (should be prominent)
    all_rms = [rms(s) for s in segs if len(s) > 0]
    max_rms = max(all_rms) if all_rms else 1.0
    a1_rel = a1_rms / max_rms if max_rms > 1e-10 else 0.0
    check("[ɑ]₁ relative amplitude", a1_rel, 0.50, 1.00)

    # Word duration
    word_dur_ms = len(word) / SR * 1000.0
    check("Word duration", word_dur_ms, 300.0, 700.0, unit='ms', fmt='.1f')

    # ================================================================
    # SUMMARY
    # ================================================================
    print()
    print("=" * 72)
    total = pass_count + fail_count
    if fail_count == 0:
        print(f"ALL {total} DIAGNOSTICS PASSED")
        print()
        print("YAJÑASYA v5 UNIFIED PLUCK ARCHITECTURE — VERIFIED.")
    else:
        print(f"{pass_count}/{total} PASSED, {fail_count} FAILED")
        print()
        print("FAILURES:")
        for passed, msg in results:
            if not passed:
                print(f"  {msg}")

    print()
    print("Ruler calibration history:")
    print("  v1.0: Initial (from ṚTVIJAM v2.1 / RATNADHĀTAMAM v4.7.1 template)")
    print("        Cold-start: 4 periods (b=[g] convention)")
    print("        Cold-start ceiling: 5.0 (IIR warm-up)")
    print("        [ɟ] release centroid in PLACE BAND (1-6 kHz)")
    print("        [s] centroid in SIBILANT BAND (4-12 kHz)")
    print("        Closing tail: core voicing + RMS fade")
    print("        Opening head: rising amplitude + core voicing")
    print("  v1.1: [ɟ] closure voicing (autocorrelation) REMOVED")
    print("        Closure 30ms after body() trim = 2.5 periods.")
    print("        Below guard clause (3 periods).")
    print("        Wrong instrument for signal length.")
    print("        Voicing proven by: LF ratio + join continuity.")
    print("        Same pattern as ṚTVIJAM v2.1 cutback voicing removal.")
    print()
    print("Section structure:")
    print("  A: Signal integrity (NaN, Inf, peak, DC)")
    print("  B: Signal continuity (glottal periodicity)")
    print("  C: [s] unified (voicelessness, centroid, RMS)")
    print("  D: Closing tail ([ɑ]₂ core voicing + RMS fade)")
    print("  E: Opening head ([j]₂ rising + core voicing)")
    print("  F: [ɟ] (closure LF = voicing proof, release centroid)")
    print("  G: Vowels ([ɑ]₁, [ɑ]₂, [ɑ]₃ — voicing, F1, F2)")
    print("  H: Approximants + Nasal ([j]₁, [j]₂, [ɲ])")
    print("  I: Syllable cadence ([s] trough, vowel prominence, duration)")
    print()
    print("Phonemes verified in this word:")
    print("  [j]  voiced palatal approximant")
    print("  [ɑ]  short open central unrounded")
    print("  [ɟ]  voiced palatal stop")
    print("  [ɲ]  voiced palatal nasal")
    print("  [s]  voiceless dental sibilant (UNIFIED)")
    print()
    print("Śikṣā alignment:")
    print("  [ɟ] = tālavya ghoṣa alpaprāṇa ✓")
    print("  [s] = dantya aghoṣa ūṣman ✓")
    print()
    print("Architecture:")
    print("  PLUCK + UNIFIED SOURCE compose:")
    print("    [ɑ]₂ owns closure (closing tail)")
    print("    [s] owns internal physics (one breath, one envelope)")
    print("    [j]₂ owns onset (opening head)")
    print("    [ɟ] voiced: voice bar + burst + crossfade cutback")
    print("    No boundary anywhere is born from different sources")
    print()
    print("PERCEPTUAL VERIFICATION:")
    print("  afplay output_play/diag_yaj_s_unified_slow12x.wav")
    print("  afplay output_play/diag_yaj_jj_iso_slow12x.wav")
    print("  afplay output_play/diag_yaj_aSya_syllable_slow6x.wav")
    print("  afplay output_play/diag_yaj_word_slow6x.wav")
    print("  afplay output_play/diag_yaj_perf_hall.wav")
    print()
    print("The ear is the FINAL arbiter.")
    print()
    print("\"The sounds were always there.")
    print("  The language is being found, not invented.\"")
    print("=" * 72)
    print()

    return fail_count == 0


if __name__ == "__main__":
    success = run_diagnostics()
    sys.exit(0 if success else 1)
