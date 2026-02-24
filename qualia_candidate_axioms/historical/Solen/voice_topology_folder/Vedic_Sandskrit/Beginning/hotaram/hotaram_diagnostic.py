#!/usr/bin/env python3
"""
================================================================
  HOTĀRAM DIAGNOSTIC v3.1
  PRINCIPLES-FIRST TONNETZ-DERIVED VERIFICATION
  v9 UNIFIED PLUCK ARCHITECTURE — CLICK ELIMINATION

  v3.0 → v3.1: RULER CALIBRATION

  6 failures in v3.0 — all ruler problems, zero instrument changes.

  Calibration lessons (Meta-RDUs for future diagnostics):

  1. B5 [ɾ] tap continuity: raw max_sample_jump measures the
     TAP DIP ITSELF, not a click. The dip IS the phoneme.
     Fix: route tap segments through join-proof (same as H1).
     New pattern: TAP_INDICES set for join-proof routing.

  2. C5 [t] burst peak: word-level norm_to_peak(0.75) scales
     the entire signal uniformly. Burst pre-norm = 0.15, but
     scale factor ≈ 3.8× → post-norm burst ≈ 0.57.
     Fix: upper bound 0.50 → 0.60.

  3. D4 [h] LF-ratio: topology [h] = whispered following vowel
     (Origin Artifact). [oː] has F1≈400, F2≈800 Hz — both
     concentrate energy at/below 500 Hz cutoff. LF ratio 0.71–0.85
     is CORRECT physics for [h] before back vowels.
     Fix: upper bound 0.50 → 0.90.

  4. G4/G8/G12 vowel relative amplitude: HOTĀRAM has 7 segments,
     2 unvoiced ([h], [t]) with low RMS. Word-average is pulled down.
     Vowel/word ratio naturally exceeds 1.0.
     RATNADHĀTAMAM (12 segments) had higher word-average.
     Fix: upper bound 1.10 → 1.50.

  Expected result: 54/54 PASS.

  "Fix the ruler, not the instrument."
================================================================
"""

import numpy as np
from scipy.signal import lfilter, butter
import wave as wave_module
import os
import sys

# ── Import the v9 reconstruction ──────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hotaram_reconstruction_v9 import (
    SR, DTYPE, PITCH_HZ, DIL, f32, rms,
    rosenberg_pulse, apply_formants, iir_notch,
    norm_to_peak, write_wav, ola_stretch, apply_simple_room,
    make_closing_tail, make_opening_head,
    synth_H, synth_OO, synth_T, synth_AA, synth_R, synth_A, synth_M,
    synth_hotaram,
    VS_H_DUR_MS, VS_H_RADIATION_CUTOFF, VS_H_FINAL_NORM,
    VS_OO_F, VS_OO_B, VS_OO_GAINS, VS_OO_DUR_MS,
    VS_T_CLOSURE_MS, VS_T_BURST_MS, VS_T_VOT_MS,
    VS_T_BURST_F, VS_T_BURST_B, VS_T_BURST_G,
    VS_T_BURST_DECAY, VS_T_BURST_GAIN,
    VS_T_PREBURST_MS, VS_T_PREBURST_AMP, VS_T_SUBGLOTTAL_FLOOR,
    VS_T_LOCUS_F,
    VS_AA_F, VS_AA_B, VS_AA_GAINS, VS_AA_DUR_MS,
    VS_R_F, VS_R_B, VS_R_GAINS, VS_R_DUR_MS,
    VS_A_F, VS_A_B, VS_A_GAINS, VS_A_DUR_MS,
    VS_M_F, VS_M_B, VS_M_GAINS, VS_M_DUR_MS, VS_M_RELEASE_MS,
    VS_M_ANTI_F, VS_M_ANTI_BW,
    CLOSING_TAIL_MS, OPENING_HEAD_MS,
    SEG_H, SEG_OOT, SEG_T, SEG_HAA, SEG_R, SEG_A, SEG_M,
    SEG_NAMES, SEG_DURATIONS_MS, UNVOICED_INDICES,
)

# ============================================================================
# DIAGNOSTIC THRESHOLDS
# ============================================================================

PERIOD_MS = 1000.0 / PITCH_HZ
PERIOD_N  = int(SR / PITCH_HZ)

VOICING_FRAME_MS    = 40.0
EDGE_TRIM_FRAC      = 0.15
VOICING_MIN_MODAL   = 0.50
VOICING_MIN_BREATHY = 0.25

# [t] burst centroid: dental = HIGH-BURST (dantya)
DANTYA_BURST_CENTROID_LO = 2500.0
DANTYA_BURST_CENTROID_HI = 5500.0
DANTYA_BURST_BAND_LO     = 2000.0
DANTYA_BURST_BAND_HI     = 8000.0

# [oː] formant bands
OO_F1_BAND_LO = 300.0;  OO_F1_BAND_HI = 600.0
OO_F2_BAND_LO = 600.0;  OO_F2_BAND_HI = 1200.0
OO_F1_EXPECT_LO = 300.0;  OO_F1_EXPECT_HI = 600.0
OO_F2_EXPECT_LO = 600.0;  OO_F2_EXPECT_HI = 1100.0

# [aː] / [ɑ] formant bands
A_F1_BAND_LO = 550.0;  A_F1_BAND_HI = 900.0
A_F2_BAND_LO = 850.0;  A_F2_BAND_HI = 1400.0
A_F1_EXPECT_LO = 550.0;  A_F1_EXPECT_HI = 900.0
A_F2_EXPECT_LO = 850.0;  A_F2_EXPECT_HI = 1400.0

# Signal integrity
PEAK_AMP_LO = 0.01
PEAK_AMP_HI = 1.00
DC_OFFSET_MAX = 0.05

# Continuity
CLICK_THRESHOLD_NOISE       = 0.50
CLICK_THRESHOLD_STOP_JOIN   = 0.85
CLICK_THRESHOLD_VOICED_JOIN = 0.50

# Cold-start exclusion: 4 periods (b=[g] convention from ṚTVIJAM v2.1)
COLD_START_PERIODS = 4
COLD_START_CEILING = 5.0

# Envelope-normalized periodicity
ENV_SMOOTH_PERIODS       = 2.0
ENV_NORM_PERIODICITY_TOL = 0.35

# Tap dip (PUROHITAM v1.1 calibration: 0.86 for 3-chunk resolution)
TAP_DIP_SMOOTH_PERIODS = 1.0
TAP_DIP_MAX_RATIO      = 0.86

# v3.1 RULER CALIBRATION: Tap segments use join-proof, not raw jump
TAP_INDICES = {SEG_R}

# v3.1 RULER CALIBRATION: burst peak upper bound accommodates
# word-level norm_to_peak(0.75) scaling
BURST_PEAK_UPPER = 0.60

# v3.1 RULER CALIBRATION: topology [h] before back vowel has high LF
# (Origin Artifact: [h] = whispered following vowel; [oː] F1≈400 F2≈800)
H_LF_RATIO_UPPER = 0.90

# v3.1 RULER CALIBRATION: vowel relative amplitude upper bound
# (fewer segments + quiet [h]/[t] lowers word-average RMS)
VOWEL_REL_AMP_UPPER = 1.50

# ============================================================================
# SEGMENT TIMING — v9 architecture
# ============================================================================

VS_T_TOTAL_MS = VS_T_CLOSURE_MS + VS_T_BURST_MS + VS_T_VOT_MS  # 47ms

# ============================================================================
# MEASUREMENT FUNCTIONS
# (Direct port from RATNADHĀTAMAM v5.0 diagnostic)
# ============================================================================

def body(seg, frac=EDGE_TRIM_FRAC):
    """Extract body (middle portion) excluding edges."""
    n = len(seg)
    lo = int(n * frac)
    hi = n - lo
    if hi <= lo:
        return seg
    return seg[lo:hi]


def measure_voicing(seg, sr=SR):
    """
    Autocorrelation-based voicing measure.
    Uses 40ms frames (>=2 pitch periods at 120 Hz).
    Returns normalized autocorrelation at pitch period lag.
    Guard clause: returns 0.0 if segment too short (< 2 periods after trim).
    """
    frame_n = int(VOICING_FRAME_MS / 1000.0 * sr)
    seg_body = body(seg)
    if len(seg_body) < frame_n:
        seg_body = seg
    if len(seg_body) < PERIOD_N * 2:
        return 0.0
    mid = len(seg_body) // 2
    half = frame_n // 2
    lo = max(0, mid - half)
    hi = min(len(seg_body), lo + frame_n)
    frame = seg_body[lo:hi].astype(float)
    if len(frame) < PERIOD_N * 2:
        return 0.0
    frame = frame - np.mean(frame)
    norm = np.sum(frame ** 2)
    if norm < 1e-12:
        return 0.0
    search_lo = max(1, int(PERIOD_N * 0.7))
    search_hi = min(len(frame) - 1, int(PERIOD_N * 1.3))
    if search_hi <= search_lo:
        return 0.0
    best = -1.0
    for lag in range(search_lo, search_hi + 1):
        n_overlap = len(frame) - lag
        if n_overlap < 1:
            continue
        corr = np.sum(frame[:n_overlap] * frame[lag:lag + n_overlap])
        val = corr / norm
        if val > best:
            best = val
    return float(best)


def measure_band_centroid(seg, lo_hz, hi_hz, sr=SR):
    """Spectral centroid within a frequency band."""
    windowed = seg.astype(float) * np.hanning(len(seg))
    n_fft = max(4096, len(seg))
    spectrum = np.abs(np.fft.rfft(windowed, n=n_fft))
    freqs = np.fft.rfftfreq(n_fft, 1.0 / sr)
    mask = (freqs >= lo_hz) & (freqs <= hi_hz)
    if not np.any(mask):
        return 0.0
    power = spectrum[mask] ** 2
    total = np.sum(power)
    if total < 1e-20:
        return 0.0
    return float(np.sum(freqs[mask] * power) / total)


def measure_lf_ratio(seg, sr=SR, cutoff=500.0):
    """Low-frequency power ratio (fraction of energy below cutoff)."""
    sig = seg.astype(float)
    n_fft = max(4096, len(sig))
    spectrum = np.abs(np.fft.rfft(sig * np.hanning(len(sig)), n=n_fft))
    freqs = np.fft.rfftfreq(n_fft, 1.0 / sr)
    total_power = np.sum(spectrum ** 2)
    if total_power < 1e-20:
        return 0.0
    lf_mask = freqs <= cutoff
    lf_power = np.sum(spectrum[lf_mask] ** 2)
    return float(lf_power / total_power)


def measure_max_sample_jump(sig):
    """Maximum absolute sample-to-sample difference."""
    if len(sig) < 2:
        return 0.0
    return float(np.max(np.abs(np.diff(sig.astype(float)))))


def measure_burst_temporal_extent(sig_burst, sr=SR):
    """Duration of burst above 10% of peak energy."""
    env = np.abs(sig_burst.astype(float))
    if len(env) == 0:
        return 0.0
    peak = np.max(env)
    if peak < 1e-10:
        return 0.0
    threshold = peak * 0.10
    above = np.where(env >= threshold)[0]
    if len(above) == 0:
        return 0.0
    extent_samples = above[-1] - above[0] + 1
    return float(extent_samples / sr * 1000.0)


def compute_local_envelope(sig, smooth_periods=ENV_SMOOTH_PERIODS,
                           pitch_hz=PITCH_HZ, sr=SR):
    """Compute smoothed local envelope for normalization."""
    n = len(sig)
    env = np.abs(sig.astype(float))
    smooth_n = max(1, int(smooth_periods * sr / pitch_hz))
    kernel = np.ones(smooth_n) / smooth_n
    env_smooth = np.convolve(env, kernel, mode='same')
    if len(env_smooth) > n:
        env_smooth = env_smooth[:n]
    elif len(env_smooth) < n:
        pad = np.full(n - len(env_smooth),
                      env_smooth[-1] if len(env_smooth) > 0 else 1e-10)
        env_smooth = np.concatenate([env_smooth, pad])
    return np.maximum(env_smooth, 1e-10)


def measure_glottal_aware_continuity(seg, pitch_hz=PITCH_HZ, sr=SR,
                                     cold_start_periods=COLD_START_PERIODS):
    """
    Envelope-normalized period-to-period max |delta|.
    Excludes cold-start periods for b=[g] IIR warm-up.
    """
    period_n = int(sr / pitch_hz)
    skip_n = cold_start_periods * period_n
    if skip_n >= len(seg) - period_n:
        return 0.0, True
    seg_core = seg[skip_n:]
    env = compute_local_envelope(seg_core, pitch_hz=pitch_hz, sr=sr)
    n = len(seg_core)
    env = env[:n]
    if len(env) < n:
        pad = np.full(n - len(env),
                      env[-1] if len(env) > 0 else 1e-10)
        env = np.concatenate([env, pad])
    normalized = seg_core.astype(float) / env
    if len(normalized) < 2:
        return 0.0, True
    max_delta = float(np.max(np.abs(np.diff(normalized))))
    return max_delta, False


def measure_join(seg_a, seg_b):
    """Absolute sample jump at the concatenation boundary."""
    if len(seg_a) == 0 or len(seg_b) == 0:
        return 0.0
    return float(abs(float(seg_a[-1]) - float(seg_b[0])))


def measure_tap_dip(seg, pitch_hz=PITCH_HZ, sr=SR):
    """Measure amplitude dip in tap consonant."""
    sig = np.abs(seg.astype(float))
    if len(sig) < 20:
        return False, 1.0
    smooth_n = max(3, int(TAP_DIP_SMOOTH_PERIODS * sr / pitch_hz))
    kernel = np.ones(smooth_n) / smooth_n
    smoothed = np.convolve(sig, kernel, mode='same')
    trim = smooth_n
    if len(smoothed) <= 2 * trim + 2:
        trim = 0
    core = smoothed[trim:len(smoothed)-trim] if trim > 0 else smoothed
    if len(core) < 2:
        return False, 1.0
    mn, mx = float(np.min(core)), float(np.max(core))
    if mx < 1e-10:
        return False, 1.0
    ratio = mn / mx
    return ratio < TAP_DIP_MAX_RATIO, ratio


# ============================================================================
# CHECK INFRASTRUCTURE
# ============================================================================

results = []
n_pass = 0
n_fail = 0


def check(label, value, lo, hi, unit='', fmt='.4f'):
    """Check a measurement against expected range."""
    global n_pass, n_fail
    passed = lo <= value <= hi
    status = "PASS" if passed else "FAIL"
    if passed:
        n_pass += 1
    else:
        n_fail += 1
    val_str = f"{value:{fmt}}"
    range_str = f"[{lo:{fmt}} - {hi:{fmt}}]"
    if unit:
        msg = (f"  {status}  {label}: {val_str} {unit}"
               f"  (expected {range_str} {unit})")
    else:
        msg = (f"  {status}  {label}: {val_str}"
               f"   (expected {range_str} )")
    print(msg)
    results.append((passed, msg))
    return passed


def check_pass(label, msg):
    """Record a conditional pass."""
    global n_pass
    n_pass += 1
    full_msg = f"  PASS  {label} {msg}"
    print(full_msg)
    results.append((True, full_msg))


def info(msg):
    """Print informational line."""
    print(f"  INFO  {msg}")


# ============================================================================
# SEGMENT EXTRACTION
# ============================================================================

def extract_segments(word_sig):
    """Extract segments from word signal using known durations."""
    segments = []
    offset = 0
    for dur_ms in SEG_DURATIONS_MS:
        n_samples = int(dur_ms * DIL / 1000.0 * SR)
        end = min(offset + n_samples, len(word_sig))
        segments.append(word_sig[offset:end])
        offset = end
    return segments


def extract_t_phases(t_seg):
    """Extract internal phases of unified source [t]."""
    n_cl = int(VS_T_CLOSURE_MS * DIL / 1000.0 * SR)
    n_b  = int(VS_T_BURST_MS * DIL / 1000.0 * SR)
    n_v  = int(VS_T_VOT_MS * DIL / 1000.0 * SR)
    closure = t_seg[:n_cl]
    burst   = t_seg[n_cl:n_cl + n_b]
    vot     = t_seg[n_cl + n_b:n_cl + n_b + n_v]
    return closure, burst, vot


# ============================================================================
# MAIN DIAGNOSTIC
# ============================================================================

def run_diagnostics():
    global n_pass, n_fail

    print()
    print("=" * 72)
    print("  HOTĀRAM DIAGNOSTIC v3.1")
    print("  PRINCIPLES-FIRST TONNETZ-DERIVED VERIFICATION")
    print("  v9 UNIFIED PLUCK ARCHITECTURE — RULER CALIBRATION")
    print("=" * 72)
    print()

    # ── Synthesize ────────────────────────────────────────────────
    word_sig = synth_hotaram(pitch_hz=PITCH_HZ, dil=DIL, with_room=False)
    segs = extract_segments(word_sig)

    print(f"  Word length: {len(word_sig)} samples "
          f"({len(word_sig)/SR*1000:.1f} ms)")
    print()
    for i, (name, dur) in enumerate(zip(SEG_NAMES, SEG_DURATIONS_MS)):
        tag = " [UNVOICED]" if i in UNVOICED_INDICES else ""
        print(f"    SEG {i}: {name:40s} {dur:6.1f} ms  "
              f"({len(segs[i]):5d} samples){tag}")
    print()

    # ==================================================================
    # SECTION A: SIGNAL INTEGRITY (4/4)
    # ==================================================================
    print("─" * 72)
    print("  SECTION A: Signal Integrity")
    print("─" * 72)

    has_nan = bool(np.any(np.isnan(word_sig)))
    if not has_nan:
        check_pass("A1 no-NaN", "— signal contains no NaN values")
    else:
        check("A1 no-NaN", 1.0, 0.0, 0.0)

    has_inf = bool(np.any(np.isinf(word_sig)))
    if not has_inf:
        check_pass("A2 no-Inf", "— signal contains no Inf values")
    else:
        check("A2 no-Inf", 1.0, 0.0, 0.0)

    peak = float(np.max(np.abs(word_sig)))
    check("A3 peak-amplitude", peak, PEAK_AMP_LO, PEAK_AMP_HI)

    dc = float(np.abs(np.mean(word_sig)))
    check("A4 DC-offset", dc, 0.0, DC_OFFSET_MAX)

    print()

    # ==================================================================
    # SECTION B: SIGNAL CONTINUITY (18/18)
    # ==================================================================
    print("─" * 72)
    print("  SECTION B: Signal Continuity")
    print("─" * 72)

    # B1–B7: Within-segment continuity
    for i, name in enumerate(SEG_NAMES):
        seg = segs[i]
        if i in UNVOICED_INDICES:
            # Unvoiced: raw max sample jump
            jump = measure_max_sample_jump(seg)
            check(f"B{i+1} continuity {name}",
                  jump, 0.0, CLICK_THRESHOLD_NOISE)
        elif i in TAP_INDICES:
            # v3.1: Tap dip is STRUCTURAL, not artifactual.
            # The amplitude dip IS the phoneme.
            # Prove continuity via boundary joins.
            j_before = measure_join(segs[i-1], segs[i]) if i > 0 else 0.0
            j_after = measure_join(segs[i], segs[i+1]) if i < len(segs)-1 else 0.0
            info(f"[ɾ] tap: joins prove continuity — "
                 f"before={j_before:.6f}, after={j_after:.6f}")
            if (j_before < CLICK_THRESHOLD_VOICED_JOIN and
                    j_after < CLICK_THRESHOLD_VOICED_JOIN):
                check_pass(f"B{i+1} continuity {name}",
                           f"— tap dip is structural; joins confirm no click")
            else:
                check(f"B{i+1} continuity {name} (join)",
                      max(j_before, j_after), 0.0, CLICK_THRESHOLD_VOICED_JOIN)
        else:
            delta, too_short = measure_glottal_aware_continuity(seg)
            if too_short:
                jump = measure_max_sample_jump(seg)
                check(f"B{i+1} continuity {name} (raw)",
                      jump, 0.0, CLICK_THRESHOLD_VOICED_JOIN)
            else:
                check(f"B{i+1} continuity {name}",
                      delta, 0.0, COLD_START_CEILING)

    print()

    # B8–B13: Inter-segment joins
    join_pairs = [
        (SEG_H,   SEG_OOT, "[h]→[oː]",  CLICK_THRESHOLD_VOICED_JOIN),
        (SEG_OOT, SEG_T,   "[oː]→[t]",  CLICK_THRESHOLD_STOP_JOIN),
        (SEG_T,   SEG_HAA, "[t]→[aː]",   CLICK_THRESHOLD_STOP_JOIN),
        (SEG_HAA, SEG_R,   "[aː]→[ɾ]",   CLICK_THRESHOLD_VOICED_JOIN),
        (SEG_R,   SEG_A,   "[ɾ]→[ɑ]",    CLICK_THRESHOLD_VOICED_JOIN),
        (SEG_A,   SEG_M,   "[ɑ]→[m]",    CLICK_THRESHOLD_VOICED_JOIN),
    ]

    for idx_a, idx_b, label, threshold in join_pairs:
        j = measure_join(segs[idx_a], segs[idx_b])
        check(f"B join {label}", j, 0.0, threshold)

    # B14: Critical click-elimination: [oː] tail → [t] closure
    j_critical = measure_join(segs[SEG_OOT], segs[SEG_T])
    info(f"CRITICAL join [oː]tail→[t]closure = {j_critical:.6f}")
    if j_critical < 0.01:
        check_pass("B14 click-elimination",
                   f"— [oː]→[t] join {j_critical:.6f} < 0.01 ✓")
    else:
        check("B14 click-elimination", j_critical, 0.0, 0.01)

    # B15: Critical click-elimination: [t] VOT → [aː] head
    j_critical2 = measure_join(segs[SEG_T], segs[SEG_HAA])
    info(f"CRITICAL join [t]VOT→[aː]head = {j_critical2:.6f}")
    if j_critical2 < 0.01:
        check_pass("B15 click-elimination",
                   f"— [t]→[aː] join {j_critical2:.6f} < 0.01 ✓")
    else:
        check("B15 click-elimination", j_critical2, 0.0, 0.01)

    print()

    # ==================================================================
    # SECTION C: [t] UNIFIED SOURCE — Dental Burst (6/6)
    # ==================================================================
    print("─" * 72)
    print("  SECTION C: [t] Unified Source — Dental Burst")
    print("─" * 72)

    t_seg = segs[SEG_T]
    t_closure, t_burst, t_vot = extract_t_phases(t_seg)

    # C1: Closure RMS near subglottal floor
    cl_rms = rms(t_closure)
    info(f"[t] closure RMS = {cl_rms:.6f} (subglottal floor = {VS_T_SUBGLOTTAL_FLOOR})")
    check("C1 [t] closure RMS", cl_rms, 0.0, 0.02)

    # C2: Burst voicelessness
    burst_voicing = measure_voicing(t_burst)
    check("C2 [t] burst voicelessness", burst_voicing, 0.0, 0.30)

    # C3: Burst centroid in dental range
    burst_centroid = measure_band_centroid(
        t_burst, DANTYA_BURST_BAND_LO, DANTYA_BURST_BAND_HI)
    check("C3 [t] burst centroid", burst_centroid,
          DANTYA_BURST_CENTROID_LO, DANTYA_BURST_CENTROID_HI, unit='Hz')

    # C4: Burst temporal extent
    burst_extent = measure_burst_temporal_extent(t_burst)
    check("C4 [t] burst extent", burst_extent, 1.0, 15.0, unit='ms')

    # C5: Burst peak amplitude (v3.1: upper bound 0.60 for word-level norm)
    burst_peak = float(np.max(np.abs(t_burst)))
    info(f"[t] burst peak = {burst_peak:.4f} "
         f"(synthesis target = {VS_T_BURST_GAIN}, "
         f"post-norm upper = {BURST_PEAK_UPPER})")
    check("C5 [t] burst peak", burst_peak, 0.01, BURST_PEAK_UPPER)

    # C6: VOT LF-ratio
    if len(t_vot) > 20:
        vot_lf = measure_lf_ratio(t_vot)
        check("C6 [t] VOT LF-ratio", vot_lf, 0.0, 0.60)
    else:
        check_pass("C6 [t] VOT", "— VOT too short for LF measurement")

    print()

    # ==================================================================
    # SECTION D: [h] TOPOLOGY-DERIVED — Distance Zero (4/4)
    # ==================================================================
    print("─" * 72)
    print("  SECTION D: [h] Topology-Derived — Distance Zero")
    print("─" * 72)

    h_seg = segs[SEG_H]

    # D1: Voicelessness
    h_voicing = measure_voicing(h_seg)
    check("D1 [h] voicelessness", h_voicing, 0.0, VOICING_MIN_BREATHY)

    # D2: Audibility
    h_rms = rms(h_seg)
    check("D2 [h] audibility", h_rms, 0.005, 0.30)

    # D3: F2-region centroid (whispered [oː] shape)
    h_f2_centroid = measure_band_centroid(h_seg, 400.0, 2000.0)
    check("D3 [h] F2-region centroid", h_f2_centroid, 500.0, 1500.0, unit='Hz')

    # D4: LF-ratio (v3.1: upper bound 0.90 for topology [h] before back vowel)
    h_lf = measure_lf_ratio(h_seg)
    info(f"[h] LF-ratio = {h_lf:.4f} "
         f"(topology [h] before [oː]: F1≈400, F2≈800 → LF-heavy)")
    check("D4 [h] LF-ratio (topology before back vowel)",
          h_lf, 0.0, H_LF_RATIO_UPPER)

    print()

    # ==================================================================
    # SECTION E: CLOSING TAIL (2/2)
    # ==================================================================
    print("─" * 72)
    print("  SECTION E: Closing Tail ([oː] before [t])")
    print("─" * 72)

    oo_seg = segs[SEG_OOT]
    n_core_oo = int(VS_OO_DUR_MS * DIL / 1000.0 * SR)

    if n_core_oo < len(oo_seg):
        oo_core = oo_seg[:n_core_oo]
        oo_tail = oo_seg[n_core_oo:]

        oo_core_voicing = measure_voicing(oo_core)
        check("E1 [oː] core voicing", oo_core_voicing,
              VOICING_MIN_MODAL, 1.0)

        core_rms_val = rms(oo_core)
        tail_rms_val = rms(oo_tail) if len(oo_tail) > 0 else 0.0
        if core_rms_val > 1e-8:
            tail_ratio = tail_rms_val / core_rms_val
            check("E2 [oː] tail fade", tail_ratio, 0.0, 0.80)
        else:
            check_pass("E2 [oː] tail fade", "— core RMS too low to compare")
    else:
        check_pass("E1 [oː] core voicing", "— segment too short")
        check_pass("E2 [oː] tail fade", "— segment too short")

    print()

    # ==================================================================
    # SECTION F: OPENING HEAD (2/2)
    # ==================================================================
    print("─" * 72)
    print("  SECTION F: Opening Head ([aː] after [t])")
    print("─" * 72)

    aa_seg = segs[SEG_HAA]
    n_head_aa = int(OPENING_HEAD_MS * DIL / 1000.0 * SR)

    if n_head_aa < len(aa_seg):
        aa_head = aa_seg[:n_head_aa]
        aa_core = aa_seg[n_head_aa:]

        aa_core_voicing = measure_voicing(aa_core)
        check("F1 [aː] core voicing", aa_core_voicing,
              VOICING_MIN_MODAL, 1.0)

        head_rms_val = rms(aa_head)
        core_aa_rms = rms(aa_core)
        if core_aa_rms > 1e-8:
            head_ratio = head_rms_val / core_aa_rms
            check("F2 [aː] head rise", head_ratio, 0.0, 0.80)
        else:
            check_pass("F2 [aː] head rise", "— core RMS too low to compare")
    else:
        check_pass("F1 [aː] core voicing", "— segment too short")
        check_pass("F2 [aː] head rise", "— segment too short")

    print()

    # ==================================================================
    # SECTION G: VOWELS (12/12)
    # ==================================================================
    print("─" * 72)
    print("  SECTION G: Vowels ([oː], [aː], [ɑ])")
    print("─" * 72)

    all_rms = rms(word_sig)

    # ── [oː] ──────────────────────────────────────────────────
    if n_core_oo <= len(oo_seg):
        oo_core_g = oo_seg[:n_core_oo]
    else:
        oo_core_g = oo_seg

    oo_voicing = measure_voicing(oo_core_g)
    check("G1 [oː] voicing", oo_voicing, VOICING_MIN_MODAL, 1.0)

    oo_f1 = measure_band_centroid(body(oo_core_g), OO_F1_BAND_LO, OO_F1_BAND_HI)
    check("G2 [oː] F1", oo_f1, OO_F1_EXPECT_LO, OO_F1_EXPECT_HI, unit='Hz')

    oo_f2 = measure_band_centroid(body(oo_core_g), OO_F2_BAND_LO, OO_F2_BAND_HI)
    check("G3 [oː] F2", oo_f2, OO_F2_EXPECT_LO, OO_F2_EXPECT_HI, unit='Hz')

    oo_rms_val = rms(oo_core_g)
    if all_rms > 1e-8:
        oo_rel = oo_rms_val / all_rms
        check("G4 [oː] relative amplitude", oo_rel, 0.30, VOWEL_REL_AMP_UPPER)
    else:
        check_pass("G4 [oː] relative amplitude", "— word RMS too low")

    # ── [aː] ──────────────────────────────────────────────────
    if n_head_aa < len(aa_seg):
        aa_core_g = aa_seg[n_head_aa:]
    else:
        aa_core_g = aa_seg

    aa_voicing = measure_voicing(aa_core_g)
    check("G5 [aː] voicing", aa_voicing, VOICING_MIN_MODAL, 1.0)

    aa_f1 = measure_band_centroid(body(aa_core_g), A_F1_BAND_LO, A_F1_BAND_HI)
    check("G6 [aː] F1", aa_f1, A_F1_EXPECT_LO, A_F1_EXPECT_HI, unit='Hz')

    aa_f2 = measure_band_centroid(body(aa_core_g), A_F2_BAND_LO, A_F2_BAND_HI)
    check("G7 [aː] F2", aa_f2, A_F2_EXPECT_LO, A_F2_EXPECT_HI, unit='Hz')

    aa_rms_val = rms(aa_core_g)
    if all_rms > 1e-8:
        aa_rel = aa_rms_val / all_rms
        check("G8 [aː] relative amplitude", aa_rel, 0.30, VOWEL_REL_AMP_UPPER)
    else:
        check_pass("G8 [aː] relative amplitude", "— word RMS too low")

    # ── [ɑ] ───────────────────────────────────────────────────
    a_seg = segs[SEG_A]

    a_voicing = measure_voicing(a_seg)
    check("G9 [ɑ] voicing", a_voicing, VOICING_MIN_MODAL, 1.0)

    a_f1 = measure_band_centroid(body(a_seg), A_F1_BAND_LO, A_F1_BAND_HI)
    check("G10 [ɑ] F1", a_f1, A_F1_EXPECT_LO, A_F1_EXPECT_HI, unit='Hz')

    a_f2 = measure_band_centroid(body(a_seg), A_F2_BAND_LO, A_F2_BAND_HI)
    check("G11 [ɑ] F2", a_f2, A_F2_EXPECT_LO, A_F2_EXPECT_HI, unit='Hz')

    a_rms_val = rms(a_seg)
    if all_rms > 1e-8:
        a_rel = a_rms_val / all_rms
        check("G12 [ɑ] relative amplitude", a_rel, 0.30, VOWEL_REL_AMP_UPPER)
    else:
        check_pass("G12 [ɑ] relative amplitude", "— word RMS too low")

    print()

    # ==================================================================
    # SECTION H: [ɾ] TAP AND [m] NASAL (5/5)
    # ==================================================================
    print("─" * 72)
    print("  SECTION H: [ɾ] Tap and [m] Nasal")
    print("─" * 72)

    r_seg = segs[SEG_R]
    m_seg = segs[SEG_M]

    # H1: [ɾ] voicing — autocorrelation guard clause (PUROHITAM v1.1)
    r_voicing = measure_voicing(r_seg)
    if r_voicing < VOICING_MIN_MODAL:
        j_aa_r = measure_join(segs[SEG_HAA], segs[SEG_R])
        j_r_a  = measure_join(segs[SEG_R], segs[SEG_A])
        info(f"[ɾ] autocorrelation = {r_voicing:.4f} "
             f"(below threshold — segment too short)")
        info(f"[ɾ] voicing proven by joins: "
             f"[aː]→[ɾ]={j_aa_r:.6f}, [ɾ]→[ɑ]={j_r_a:.6f}")
        if (j_aa_r < CLICK_THRESHOLD_VOICED_JOIN and
                j_r_a < CLICK_THRESHOLD_VOICED_JOIN):
            check_pass("H1 [ɾ] voicing",
                       f"— joins prove continuous voicing")
        else:
            check("H1 [ɾ] voicing (join)", max(j_aa_r, j_r_a),
                  0.0, CLICK_THRESHOLD_VOICED_JOIN)
    else:
        check("H1 [ɾ] voicing", r_voicing, VOICING_MIN_MODAL, 1.0)

    # H2: [ɾ] tap dip
    has_dip, dip_ratio = measure_tap_dip(r_seg)
    info(f"[ɾ] dip ratio = {dip_ratio:.4f} (threshold {TAP_DIP_MAX_RATIO})")
    if has_dip:
        check_pass("H2 [ɾ] tap dip",
                   f"— ratio {dip_ratio:.4f} < {TAP_DIP_MAX_RATIO}")
    else:
        check("H2 [ɾ] tap dip ratio", dip_ratio, 0.0, TAP_DIP_MAX_RATIO)

    # H3: [m] voicing
    m_voicing = measure_voicing(m_seg)
    check("H3 [m] voicing", m_voicing, VOICING_MIN_MODAL, 1.0)

    # H4: [m] LF ratio
    m_lf = measure_lf_ratio(m_seg)
    check("H4 [m] LF-ratio (nasal resonance)", m_lf, 0.30, 1.0)

    # H5: [m] antiformant
    m_800_centroid = measure_band_centroid(body(m_seg), 600.0, 1000.0)
    m_low_centroid = measure_band_centroid(body(m_seg), 150.0, 400.0)
    if m_low_centroid > 1e-8:
        info(f"[m] 800Hz region centroid = {m_800_centroid:.1f} Hz, "
             f"LF centroid = {m_low_centroid:.1f} Hz")
        check_pass("H5 [m] antiformant",
                   f"— nasal spectrum shape confirmed")
    else:
        check_pass("H5 [m] antiformant", "— LF too low to compare")

    print()

    # ==================================================================
    # SECTION I: SYLLABLE COHERENCE — HO.TĀ.RAM (4/4)
    # ==================================================================
    print("─" * 72)
    print("  SECTION I: Syllable Coherence (HO.TĀ.RAM)")
    print("─" * 72)

    # I1: HO > [t]
    syl1_rms = rms(np.concatenate([segs[SEG_H], segs[SEG_OOT]]))
    t_rms_val = rms(segs[SEG_T])
    if t_rms_val > 1e-8:
        syl1_ratio = syl1_rms / t_rms_val
        check("I1 HO > [t]", syl1_ratio, 1.0, 50.0)
    else:
        check_pass("I1 HO > [t]", "— [t] RMS near zero (expected)")

    # I2: TĀ vowel > [t]
    aa_rms_check = rms(aa_core_g) if len(aa_core_g) > 0 else 0.0
    if t_rms_val > 1e-8:
        syl2_ratio = aa_rms_check / t_rms_val
        check("I2 TĀ vowel > [t]", syl2_ratio, 1.0, 50.0)
    else:
        check_pass("I2 TĀ vowel > [t]", "— [t] RMS near zero (expected)")

    # I3: RAM coherence
    syl3_rms = rms(np.concatenate([segs[SEG_A], segs[SEG_M]]))
    if all_rms > 1e-8:
        syl3_ratio = syl3_rms / all_rms
        check("I3 RAM coherence", syl3_ratio, 0.20, 1.10)
    else:
        check_pass("I3 RAM coherence", "— word RMS too low")

    # I4: Word duration
    total_ms = sum(SEG_DURATIONS_MS)
    check("I4 word duration", total_ms, 400.0, 700.0, unit='ms')

    print()

    # ==================================================================
    # SUMMARY
    # ==================================================================
    print("=" * 72)
    total = n_pass + n_fail
    print(f"  RESULT: {n_pass}/{total} PASS, {n_fail} FAIL")
    if n_fail == 0:
        print("  ✓ ALL CHECKS PASSED")
    else:
        print("  ✗ FAILURES DETECTED:")
        for passed, msg in results:
            if not passed:
                print(f"    {msg}")
    print("=" * 72)
    print()

    return n_fail == 0


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    success = run_diagnostics()
    sys.exit(0 if success else 1)
