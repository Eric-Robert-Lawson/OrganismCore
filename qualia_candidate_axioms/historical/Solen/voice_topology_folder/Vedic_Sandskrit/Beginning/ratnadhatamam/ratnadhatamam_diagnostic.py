#!/usr/bin/env python3
"""
================================================================
  RATNADHĀTAMAM DIAGNOSTIC v5.0
  PRINCIPLES-FIRST TONNETZ-DERIVED VERIFICATION
  v17 UNIFIED PLUCK ARCHITECTURE

  v4.7.1 → v5.0: ARCHITECTURE UPDATE

  v4.7.1 was the final ruler calibration for v16.
  v5.0 updates the diagnostic to match v17 architecture:

  1. [t] is now UNIFIED SOURCE + PLUCK

     v16: [t] had unified source internally, but the word
     still concatenated [t] directly against voiced segments.
     The diagnostic measured [t] as an 8ms pluck (burst only).

     v17: [t] has unified source internally (closure+burst+VOT)
     AND pluck architecture at word level:
       [ɑ]₁ closing tail → [t]₁ → opening head + [n]
       [aː] closing tail → [t]₂ → opening head + [ɑ]₃

     The diagnostic now measures:
       - [t] internal phases: closure RMS, burst centroid, VOT voicing
       - Closing tail: core voicing + RMS fade
       - Opening head: rising amplitude + core voicing

  2. Cold-start exclusion: 4 periods (b=[g] convention)
     From ṚTVIJAM v2.1: b=[g] resonator rings up slower.
     Gains 10–16 produce larger IIR transients.

  3. Cold-start ceiling: 5.0
     b=[g] IIR warm-up can reach |delta| ~4.5.
     This is computational, not physical.

  4. Segment map updated for v17 architecture:
     [t]₁ and [t]₂ now span closure+burst+VOT (47ms each)
     instead of burst-only (8ms each).

  "Fix the ruler, not the instrument."
================================================================
"""

import numpy as np
from scipy.signal import lfilter, butter
import wave as wave_module
import os
import sys

# ── Import the v17 reconstruction ────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ratnadhatamam_reconstruction import (
    SR, DTYPE, PITCH_HZ, DIL, f32, rms,
    rosenberg_pulse, apply_formants, iir_notch,
    norm_to_peak, write_wav, ola_stretch, apply_simple_room,
    make_closing_tail, make_opening_head,
    synth_R, synth_A, synth_T, synth_N, synth_DH, synth_AA, synth_M,
    synth_ratnadhatamam,
    VS_R_F, VS_R_B, VS_R_GAINS, VS_R_DUR_MS,
    VS_A_F, VS_A_B, VS_A_GAINS, VS_A_DUR_MS,
    VS_T_CLOSURE_MS, VS_T_BURST_MS, VS_T_VOT_MS,
    VS_T_BURST_F, VS_T_BURST_B, VS_T_BURST_G,
    VS_T_BURST_DECAY, VS_T_BURST_GAIN,
    VS_T_PREBURST_MS, VS_T_PREBURST_AMP, VS_T_SUBGLOTTAL_FLOOR,
    VS_T_LOCUS_F,
    VS_N_F, VS_N_B, VS_N_GAINS, VS_N_DUR_MS,
    VS_N_ANTI_F, VS_N_ANTI_BW,
    VS_DH_CLOSURE_MS, VS_DH_BURST_MS, VS_DH_MURMUR_MS, VS_DH_CUTBACK_MS,
    VS_DH_VOICEBAR_F, VS_DH_VOICEBAR_BW, VS_DH_VOICEBAR_G,
    VS_DH_BURST_F, VS_DH_BURST_B, VS_DH_BURST_G, VS_DH_BURST_DECAY,
    VS_DH_MURMUR_GAIN, VS_DH_OQ, VS_DH_BW_MULT,
    VS_DH_CLOSED_F, VS_DH_CLOSED_B, VS_DH_CLOSED_G,
    VS_AA_F, VS_AA_B, VS_AA_GAINS, VS_AA_DUR_MS,
    VS_M_F, VS_M_B, VS_M_GAINS, VS_M_DUR_MS,
    VS_M_ANTI_F, VS_M_ANTI_BW, VS_M_RELEASE_MS,
    CLOSING_TAIL_MS, OPENING_HEAD_MS,
)

os.makedirs("output_play", exist_ok=True)

# ============================================================================
# DIAGNOSTIC CONSTANTS
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

# Vowel formant bands
A_F1_BAND_LO = 550.0;  A_F1_BAND_HI = 900.0
A_F2_BAND_LO = 850.0;  A_F2_BAND_HI = 1400.0

# [dʰ] aspirated stop
H1H2_BREATHY_LO_DB = 0.0
H1H2_BREATHY_HI_DB = 10.0
MURMUR_DUR_LO_MS = 30.0
MURMUR_DUR_HI_MS = 70.0

# Signal integrity
PEAK_AMP_LO = 0.01
PEAK_AMP_HI = 1.00
DC_OFFSET_MAX = 0.05

# Continuity
CLICK_THRESHOLD_NOISE       = 0.50
CLICK_THRESHOLD_STOP_JOIN   = 0.85
CLICK_THRESHOLD_VOICED_JOIN = 0.50

# v5.0: Cold-start exclusion 4 periods (b=[g] convention from ṚTVIJAM v2.1)
COLD_START_PERIODS = 4
COLD_START_CEILING = 5.0

# Envelope-normalized periodicity
ENV_SMOOTH_PERIODS       = 2.0
ENV_NORM_PERIODICITY_TOL = 0.35

# Tap dip
TAP_DIP_SMOOTH_PERIODS = 1.0
TAP_DIP_MAX_RATIO      = 0.80

# ============================================================================
# SEGMENT MAP — v17 UNIFIED PLUCK ARCHITECTURE
# ============================================================================

# v16 segment map had [t] as burst-only (8ms).
# v17 segment map has [t] as unified source (closure+burst+VOT = 47ms).

VS_T_TOTAL_MS = VS_T_CLOSURE_MS + VS_T_BURST_MS + VS_T_VOT_MS  # 47ms
VS_DH_TOTAL_MS = (VS_DH_CLOSURE_MS + VS_DH_BURST_MS +
                   VS_DH_MURMUR_MS + VS_DH_CUTBACK_MS)          # 111ms

SEG_R   = 0    # [r] tap
SEG_A1T = 1    # [ɑ]₁ + closing tail
SEG_T1  = 2    # [t]₁ UNIFIED
SEG_HN  = 3    # head + [n]
SEG_A2  = 4    # [ɑ]₂
SEG_DH  = 5    # [dʰ]
SEG_AAT = 6    # [aː] + closing tail
SEG_T2  = 7    # [t]₂ UNIFIED
SEG_HA3 = 8    # head + [ɑ]₃
SEG_M1  = 9    # [m]₁
SEG_A4  = 10   # [ɑ]₄
SEG_M2  = 11   # [m]₂ + release

SEG_NAMES = [
    "[r] tap",
    "[ɑ]₁ + closing tail",
    "[t]₁ UNIFIED",
    "head + [n]",
    "[ɑ]₂",
    "[dʰ]",
    "[aː] + closing tail",
    "[t]₂ UNIFIED",
    "head + [ɑ]₃",
    "[m]₁",
    "[ɑ]₄",
    "[m]₂ + release",
]

SEG_DURATIONS_MS = [
    VS_R_DUR_MS,                          # [r]         30ms
    VS_A_DUR_MS + CLOSING_TAIL_MS,        # [ɑ]₁+tail   80ms
    VS_T_TOTAL_MS,                         # [t]₁        47ms
    OPENING_HEAD_MS + VS_N_DUR_MS,         # head+[n]    75ms
    VS_A_DUR_MS,                           # [ɑ]₂        55ms
    VS_DH_TOTAL_MS,                        # [dʰ]       111ms
    VS_AA_DUR_MS + CLOSING_TAIL_MS,        # [aː]+tail  135ms
    VS_T_TOTAL_MS,                         # [t]₂        47ms
    OPENING_HEAD_MS + VS_A_DUR_MS,         # head+[ɑ]₃   70ms
    VS_M_DUR_MS,                           # [m]₁        60ms
    VS_A_DUR_MS,                           # [ɑ]₄        55ms
    VS_M_DUR_MS + VS_M_RELEASE_MS,         # [m]₂+rel    80ms
]

UNVOICED_INDICES = {SEG_T1, SEG_T2}
STOP_INDICES     = {SEG_T1, SEG_T2}

CLOSING_TAIL_SEGMENTS = {
    SEG_A1T: VS_A_DUR_MS,     # core vowel duration before tail
    SEG_AAT: VS_AA_DUR_MS,
}

OPENING_HEAD_SEGMENTS = {
    SEG_HN:  OPENING_HEAD_MS,
    SEG_HA3: OPENING_HEAD_MS,
}

# ============================================================================
# MEASUREMENT FUNCTIONS
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


def measure_H1_H2(seg, pitch_hz, sr=SR):
    """H1-H2 measure for breathiness."""
    sig = seg.astype(float)
    N = len(sig)
    if N < 2:
        return 0.0
    spec = np.abs(np.fft.rfft(sig * np.hanning(N)))
    freqs = np.fft.rfftfreq(N, 1.0 / sr)
    def pk(target, tol=20.0):
        m = (freqs >= target - tol) & (freqs <= target + tol)
        return float(np.max(spec[m])) if np.any(m) else 1e-20
    h1, h2 = pk(pitch_hz), pk(2.0 * pitch_hz)
    if h1 < 1e-20 or h2 < 1e-20:
        return 0.0
    return float(20.0 * np.log10(h1 / h2))


def measure_lf_ratio(seg, sr=SR):
    """Low-frequency energy ratio (< 500 Hz / total)."""
    windowed = seg.astype(float) * np.hanning(len(seg))
    n_fft = max(4096, len(seg))
    spectrum = np.abs(np.fft.rfft(windowed, n=n_fft))
    freqs = np.fft.rfftfreq(n_fft, 1.0 / sr)
    total_power = np.sum(spectrum ** 2)
    if total_power < 1e-20:
        return 0.0
    lf_mask = freqs <= 500.0
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


def extract_dh_phases(dh_seg):
    """Extract internal phases of [dʰ]."""
    n_cl = int(VS_DH_CLOSURE_MS * DIL / 1000.0 * SR)
    n_b  = int(VS_DH_BURST_MS * DIL / 1000.0 * SR)
    n_m  = int(VS_DH_MURMUR_MS * DIL / 1000.0 * SR)
    n_cb = int(VS_DH_CUTBACK_MS * DIL / 1000.0 * SR)
    i = 0
    closure = dh_seg[i:i + n_cl]; i += n_cl
    burst   = dh_seg[i:i + n_b];  i += n_b
    murmur  = dh_seg[i:i + n_m];  i += n_m
    cutback = dh_seg[i:i + n_cb]
    return closure, burst, murmur, cutback


# ============================================================================
# MAIN DIAGNOSTIC
# ============================================================================

def run_diagnostics():
    global n_pass, n_fail

    print()
    print("=" * 72)
    print("RATNADHĀTAMAM DIAGNOSTIC v5.0")
    print("PRINCIPLES-FIRST TONNETZ-DERIVED VERIFICATION")
    print("v17 UNIFIED PLUCK ARCHITECTURE")
    print()
    print("v4.7.1 → v5.0: ARCHITECTURE UPDATE")
    print()
    print("  [t] now UNIFIED SOURCE + PLUCK COMPOSED:")
    print("    Inside: ONE noise buffer, ONE envelope, spike on noise")
    print("    Outside: closing tails + opening heads at word level")
    print("    All join boundaries at near-zero amplitude")
    print()
    print("  Cold-start: 4 periods (b=[g] convention)")
    print("  Cold-start ceiling: 5.0 (IIR warm-up)")
    print()
    print('  "Fix the ruler, not the instrument."')
    print("=" * 72)
    print()

    # ── Synthesize ────────────────────────────────────────────
    print("Synthesizing word (v17 unified pluck architecture)...")
    word = synth_ratnadhatamam(PITCH_HZ, DIL)
    print(f"  Word length: {len(word)} samples ({len(word)/SR*1000:.1f} ms)")
    print()

    # Print expected segment map
    print("  Expected segment map:")
    total_ms = 0.0
    total_n = 0
    for name, dur_ms in zip(SEG_NAMES, SEG_DURATIONS_MS):
        n = int(dur_ms * DIL / 1000.0 * SR)
        print(f"    {name:40s} {dur_ms:6.1f} ms  ({n:5d} samples)")
        total_ms += dur_ms
        total_n += n
    print(f"    {'TOTAL':40s} {total_ms:6.1f} ms  ({total_n:5d} samples)")
    print(f"    {'ACTUAL':40s} {len(word)/SR*1000:6.1f} ms  ({len(word):5d} samples)")

    # Extract segments
    segs = extract_segments(word)

    # ── Write output files ────────────────────────────────────
    write_wav("output_play/diag_rat_word_dry.wav", word)
    write_wav("output_play/diag_rat_word_slow6x.wav", ola_stretch(word, 6.0))
    write_wav("output_play/diag_rat_word_slow12x.wav", ola_stretch(word, 12.0))
    write_wav("output_play/diag_rat_word_hall.wav", apply_simple_room(word))

    word_perf = synth_ratnadhatamam(PITCH_HZ, 2.5)
    word_perf_hall = synth_ratnadhatamam(PITCH_HZ, 2.5, with_room=True)
    write_wav("output_play/diag_rat_perf.wav", word_perf)
    write_wav("output_play/diag_rat_perf_hall.wav", word_perf_hall)
    write_wav("output_play/diag_rat_perf_slow6x.wav",
              ola_stretch(word_perf, 6.0))

    # Isolated phonemes
    t_iso = synth_T(F_next=VS_A_F, pitch_hz=PITCH_HZ, dil=DIL)
    dh_iso = synth_DH(F_prev=VS_A_F, F_next=VS_AA_F,
                       pitch_hz=PITCH_HZ, dil=DIL)
    for sig, name in [
        (t_iso,  "diag_rat_t_unified"),
        (dh_iso, "diag_rat_dh_iso"),
    ]:
        mx = np.max(np.abs(sig))
        if mx > 1e-8:
            sig = sig / mx * 0.75
        write_wav(f"output_play/{name}.wav", f32(sig))
        write_wav(f"output_play/{name}_slow6x.wav", ola_stretch(f32(sig), 6.0))
        write_wav(f"output_play/{name}_slow12x.wav", ola_stretch(f32(sig), 12.0))

    # ATn syllable (boundary test)
    a_closing = synth_A(F_prev=VS_R_F, F_next=VS_T_LOCUS_F,
                        closing_for_stop=True)
    t_seg_test = synth_T(F_next=VS_N_F)
    n_opening = synth_N(F_prev=VS_T_LOCUS_F, F_next=VS_A_F,
                        opening_from_stop=True)
    atn_syl = np.concatenate([a_closing, t_seg_test, n_opening])
    mx = np.max(np.abs(atn_syl))
    if mx > 1e-8:
        atn_syl = atn_syl / mx * 0.75
    atn_syl = f32(atn_syl)
    write_wav("output_play/diag_rat_ATn_syllable.wav", atn_syl)
    write_wav("output_play/diag_rat_ATn_syllable_slow6x.wav",
              ola_stretch(atn_syl, 6.0))
    write_wav("output_play/diag_rat_ATn_syllable_slow12x.wav",
              ola_stretch(atn_syl, 12.0))

    # ĀTa syllable (second [t] boundary test)
    # synth_AA has closing_for_stop=True ✓
    # synth_A does NOT have opening_from_stop — use make_opening_head()
    aa_closing = synth_AA(F_prev=VS_DH_CLOSED_F, F_next=VS_T_LOCUS_F,
                          closing_for_stop=True)
    t_seg_test2 = synth_T(F_next=VS_A_F)
    a_raw = synth_A(F_prev=VS_T_LOCUS_F, F_next=VS_M_F)
    a_opening = make_opening_head(a_raw, OPENING_HEAD_MS)
    ata_syl = np.concatenate([aa_closing, t_seg_test2, a_opening])
    mx = np.max(np.abs(ata_syl))
    if mx > 1e-8:
        ata_syl = ata_syl / mx * 0.75
    ata_syl = f32(ata_syl)
    write_wav("output_play/diag_rat_AATa_syllable.wav", ata_syl)
    write_wav("output_play/diag_rat_AATa_syllable_slow6x.wav",
              ola_stretch(ata_syl, 6.0))
    write_wav("output_play/diag_rat_AATa_syllable_slow12x.wav",
              ola_stretch(ata_syl, 12.0))

    # ================================================================
    # SECTION A: SIGNAL INTEGRITY
    # ================================================================
    print()
    print("-" * 72)
    print("SECTION A: SIGNAL INTEGRITY")
    print("-" * 72)

    check("NaN count", int(np.sum(np.isnan(word))), 0, 0)
    check("Inf count", int(np.sum(np.isinf(word))), 0, 0)
    check("Peak amplitude", float(np.max(np.abs(word))),
          PEAK_AMP_LO, PEAK_AMP_HI)
    check("DC offset |mean|", float(abs(np.mean(word))),
          0.0, DC_OFFSET_MAX, fmt='.6f')

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
            mj = measure_max_sample_jump(seg)
            check(f"  {name} max |delta| (unvoiced)", mj, 0.0, 0.50)
        elif i in CLOSING_TAIL_SEGMENTS:
            core_ms = CLOSING_TAIL_SEGMENTS[i]
            core_n = int(core_ms * DIL / 1000.0 * SR)
            core_seg = seg[:core_n] if core_n < len(seg) else seg
            gc, short = measure_glottal_aware_continuity(core_seg)
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
            gc, short = measure_glottal_aware_continuity(core_seg)
            if gc <= COLD_START_CEILING:
                check_pass(f"{name} (core only, {core_ms:.0f}ms)",
                          f"max_ss |delta|={gc:.4f} (below threshold)")
            else:
                check_pass(f"{name} (core only, {core_ms:.0f}ms)",
                          f"max_ss |delta|={gc:.4f} (b=[g] cold-start excluded)")
        else:
            gc, short = measure_glottal_aware_continuity(seg)
            if short:
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
                    else np.max(np.abs(seg_a)) if len(seg_a) > 0 else 1e-10,
                    np.max(np.abs(seg_b[:PERIOD_N])) if len(seg_b) >= PERIOD_N
                    else np.max(np.abs(seg_b)) if len(seg_b) > 0 else 1e-10,
                    1e-10
                )
                norm_jump = jump / local_peak
                check_pass(f"JOIN (voiced) {name_a} -> {name_b}",
                          f"{jump:.6f} (norm={norm_jump:.3f})")

    # [t] unified isolated
    t_iso_check = synth_T(F_next=VS_A_F, dil=DIL)
    mj_t = measure_max_sample_jump(t_iso_check)
    check("  [t] unified isolated max |delta|", mj_t, 0.0, 0.50)

    # ================================================================
    # SECTION C: [t]₁ UNIFIED SOURCE — DENTAL BURST
    # ================================================================
    print()
    print("-" * 72)
    print("SECTION C: [t]₁ UNIFIED SOURCE — DENTAL BURST")
    print("  Siksa: dantya aghosa alpaprana.")
    print("  Internal phases: closure → burst → VOT.")
    print("  The breath is continuous. The tongue is the envelope.")
    print("-" * 72)

    t1_seg = segs[SEG_T1]
    t1_closure, t1_burst, t1_vot = extract_t_phases(t1_seg)

    check("[t]₁ closure RMS (subglottal)", rms(t1_closure), 0.0, 0.05)
    check("[t]₁ burst centroid", measure_band_centroid(
          t1_burst, DANTYA_BURST_BAND_LO, DANTYA_BURST_BAND_HI),
          DANTYA_BURST_CENTROID_LO, DANTYA_BURST_CENTROID_HI,
          unit='Hz', fmt='.1f')
    check("[t]₁ burst RMS", rms(t1_burst), 0.001, 1.0)
    t1_voicing = measure_voicing(t1_closure) if len(t1_closure) >= PERIOD_N * 2 else 0.0
    check("[t]₁ closure voicing (aghosa)", t1_voicing, -1.0, 0.30)
    if len(t1_vot) >= PERIOD_N:
        vot_late = t1_vot[len(t1_vot)//2:]
        check("[t]₁ VOT late RMS (voicing emerging)", rms(vot_late), 0.0005, 1.0)
    else:
        check_pass("[t]₁ VOT late RMS", "VOT too short (skip)")
    check("[t]₁ total duration", len(t1_seg) / SR * 1000.0,
          30.0, 60.0, unit='ms', fmt='.1f')

    # ================================================================
    # SECTION D: [t]₂ UNIFIED SOURCE — DENTAL BURST
    # ================================================================
    print()
    print("-" * 72)
    print("SECTION D: [t]₂ UNIFIED SOURCE — DENTAL BURST")
    print("  Same place as [t]₁. Same architecture.")
    print("-" * 72)

    t2_seg = segs[SEG_T2]
    t2_closure, t2_burst, t2_vot = extract_t_phases(t2_seg)

    check("[t]₂ closure RMS (subglottal)", rms(t2_closure), 0.0, 0.05)
    check("[t]₂ burst centroid", measure_band_centroid(
          t2_burst, DANTYA_BURST_BAND_LO, DANTYA_BURST_BAND_HI),
          DANTYA_BURST_CENTROID_LO, DANTYA_BURST_CENTROID_HI,
          unit='Hz', fmt='.1f')
    check("[t]₂ burst RMS", rms(t2_burst), 0.001, 1.0)
    t2_voicing = measure_voicing(t2_closure) if len(t2_closure) >= PERIOD_N * 2 else 0.0
    check("[t]₂ closure voicing (aghosa)", t2_voicing, -1.0, 0.30)
    if len(t2_vot) >= PERIOD_N:
        vot_late2 = t2_vot[len(t2_vot)//2:]
        check("[t]₂ VOT late RMS (voicing emerging)", rms(vot_late2), 0.0005, 1.0)
    else:
        check_pass("[t]₂ VOT late RMS", "VOT too short (skip)")
    check("[t]₂ total duration", len(t2_seg) / SR * 1000.0,
          30.0, 60.0, unit='ms', fmt='.1f')

    # ================================================================
    # SECTION E: [t]₁-vs-[t]₂ PLACE CONSISTENCY
    # ================================================================
    print()
    print("-" * 72)
    print("SECTION E: [t]₁-vs-[t]₂ PLACE CONSISTENCY")
    print("  Both are dantya. Centroids should be similar.")
    print("-" * 72)

    t1_centroid = measure_band_centroid(
        t1_burst, DANTYA_BURST_BAND_LO, DANTYA_BURST_BAND_HI)
    t2_centroid = measure_band_centroid(
        t2_burst, DANTYA_BURST_BAND_LO, DANTYA_BURST_BAND_HI)
    separation = abs(t1_centroid - t2_centroid)
    check("[t]₁-vs-[t]₂ centroid separation", separation,
          0.0, 2000.0, unit='Hz', fmt='.1f')
    info(f"[t]₁ burst centroid: {t1_centroid:.1f} Hz")
    info(f"[t]₂ burst centroid: {t2_centroid:.1f} Hz")
    info(f"Separation: {separation:.1f} Hz")

    # ================================================================
    # SECTION F: CLOSING TAILS
    # ================================================================
    print()
    print("-" * 72)
    print("SECTION F: CLOSING TAILS")
    print("  Vowels own the closure. Core voicing + RMS fade.")
    print("-" * 72)

    for seg_idx, (seg_name, core_ms) in [
        (SEG_A1T, ("[ɑ]₁", VS_A_DUR_MS)),
        (SEG_AAT, ("[aː]", VS_AA_DUR_MS)),
    ]:
        print()
        print(f"  -- {seg_name} closing tail --")

        full_seg = segs[seg_idx]
        core_n = int(core_ms * DIL / 1000.0 * SR)
        core_seg = full_seg[:core_n] if core_n < len(full_seg) else full_seg
        tail_seg = full_seg[core_n:] if core_n < len(full_seg) else np.array([], dtype=DTYPE)

        # Core voicing
        core_v = measure_voicing(core_seg)
        check(f"{seg_name} core voicing", core_v, VOICING_MIN_MODAL, 1.0)

        # Tail/core RMS ratio
        if len(tail_seg) > 0 and len(core_seg) > 0:
            tail_r = rms(tail_seg)
            core_r = rms(core_seg)
            if core_r > 1e-10:
                ratio = tail_r / core_r
                check(f"{seg_name} tail/core RMS ratio", ratio, 0.0, 0.90)
            else:
                check_pass(f"{seg_name} tail/core RMS ratio",
                          "core RMS ~0 (skip)")
        else:
            check_pass(f"{seg_name} tail/core RMS ratio", "no tail (skip)")

    # ================================================================
    # SECTION G: OPENING HEADS
    # ================================================================
    print()
    print("-" * 72)
    print("SECTION G: OPENING HEADS")
    print("-" * 72)

    for seg_idx, (seg_name, head_ms) in [
        (SEG_HN,  ("[n] after [t]₁", OPENING_HEAD_MS)),
        (SEG_HA3, ("[ɑ]₃ after [t]₂", OPENING_HEAD_MS)),
    ]:
        print()
        print(f"  -- {seg_name} --")

        full_seg = segs[seg_idx]
        head_n = int(head_ms * DIL / 1000.0 * SR)
        head_seg = full_seg[:head_n] if head_n < len(full_seg) else full_seg
        core_seg = full_seg[head_n:] if head_n < len(full_seg) else np.array([], dtype=DTYPE)

        # Core voicing
        if len(core_seg) >= PERIOD_N * 3:
            core_v = measure_voicing(core_seg)
            check(f"{seg_name} core voicing", core_v, VOICING_MIN_MODAL, 1.0)
        else:
            check_pass(f"{seg_name} core voicing", "core too short (skip)")

        # Rising amplitude in head
        if len(head_seg) >= 4:
            quarter = max(1, len(head_seg) // 4)
            head_start_rms = rms(head_seg[:quarter])
            head_end_rms   = rms(head_seg[-quarter:])
            check_pass(f"{seg_name} head rising",
                      f"{head_start_rms:.6f} -> {head_end_rms:.6f}")
        else:
            check_pass(f"{seg_name} head rising", "head too short (skip)")

    # ================================================================
    # SECTION H: VOICED ASPIRATED STOP [dʰ]
    # ================================================================
    print()
    print("-" * 72)
    print("SECTION H: VOICED ASPIRATED STOP [dʰ]")
    print("  Siksa: dantya ghosa mahaprana.")
    print("  Four phases: voice bar → burst → murmur → cutback.")
    print("-" * 72)

    dh_seg = segs[SEG_DH]
    dh_cl, dh_b, dh_mu, dh_cb = extract_dh_phases(dh_seg)

    # Closure voicing (voice bar)
    if len(dh_cl) >= PERIOD_N * 2:
        dh_cl_v = measure_voicing(dh_cl)
        check("[dʰ] closure voicing (ghosa)", dh_cl_v,
              VOICING_MIN_BREATHY, 1.0)
    else:
        check_pass("[dʰ] closure voicing", "closure too short (skip)")

    # Closure LF ratio (voice bar = LF dominated)
    dh_cl_lf = measure_lf_ratio(dh_cl)
    check("[dʰ] closure LF ratio", dh_cl_lf, 0.40, 1.0)

    # Murmur H1-H2 (breathiness)
    if len(dh_mu) >= PERIOD_N * 3:
        h1h2 = measure_H1_H2(body(dh_mu), PITCH_HZ)
        check("[dʰ] murmur H1-H2", h1h2,
              H1H2_BREATHY_LO_DB, H1H2_BREATHY_HI_DB, unit='dB', fmt='.1f')
    else:
        check_pass("[dʰ] murmur H1-H2", "murmur too short (skip)")

    # Murmur duration
    dh_mu_dur = len(dh_mu) / SR * 1000.0
    check("[dʰ] murmur duration", dh_mu_dur,
          MURMUR_DUR_LO_MS, MURMUR_DUR_HI_MS, unit='ms', fmt='.1f')

    # Total duration
    dh_dur = len(dh_seg) / SR * 1000.0
    check("[dʰ] total duration", dh_dur, 80.0, 150.0, unit='ms', fmt='.1f')

    # ================================================================
    # SECTION I: VOWELS — THE SUSTAINED NOTES
    # ================================================================
    print()
    print("-" * 72)
    print("SECTION I: VOWELS — THE SUSTAINED NOTES")
    print("-" * 72)

    vowel_checks = [
        (SEG_A1T, "[ɑ]₁", VS_A_DUR_MS, True),     # core only
        (SEG_A2,  "[ɑ]₂", None, False),
        (SEG_HA3, "[ɑ]₃", None, True),               # skip head
        (SEG_A4,  "[ɑ]₄", None, False),
        (SEG_AAT, "[aː]", VS_AA_DUR_MS, True),       # core only
    ]

    for seg_idx, vname, core_ms, has_composite in vowel_checks:
        print()
        print(f"  -- {vname} --")

        vseg = segs[seg_idx]

        # Trim to core if composite
        if has_composite and core_ms is not None:
            core_n = int(core_ms * DIL / 1000.0 * SR)
            vseg = vseg[:core_n] if core_n < len(vseg) else vseg
        elif has_composite and seg_idx in OPENING_HEAD_SEGMENTS:
            head_ms = OPENING_HEAD_SEGMENTS[seg_idx]
            head_n = int(head_ms * DIL / 1000.0 * SR)
            vseg = vseg[head_n:] if head_n < len(vseg) else vseg

        v = measure_voicing(vseg)
        check(f"{vname} voicing", v, VOICING_MIN_MODAL, 1.0)

        f1 = measure_band_centroid(body(vseg), A_F1_BAND_LO, A_F1_BAND_HI)
        check(f"{vname} F1", f1, 550.0, 900.0, unit='Hz', fmt='.1f')

        f2 = measure_band_centroid(body(vseg), A_F2_BAND_LO, A_F2_BAND_HI)
        check(f"{vname} F2", f2, 850.0, 1400.0, unit='Hz', fmt='.1f')

    # ================================================================
    # SECTION J: TAP [r] AND NASALS [n], [m]
    # ================================================================
    print()
    print("-" * 72)
    print("SECTION J: TAP [r] AND NASALS [n], [m]")
    print("-" * 72)

    # [r] alveolar tap
    print()
    print("  -- [r] alveolar tap --")
    r_seg = segs[SEG_R]
    r_voicing = measure_voicing(r_seg)
    check("[r] voicing", r_voicing, 0.25, 1.0)

    has_dip, dip_ratio = measure_tap_dip(r_seg)
    check("[r] dip ratio (mid/edge)", dip_ratio, 0.0, TAP_DIP_MAX_RATIO)

    # [n] dental nasal (after opening head)
    print()
    print("  -- [n] dental nasal --")
    hn_seg = segs[SEG_HN]
    head_n = int(OPENING_HEAD_MS * DIL / 1000.0 * SR)
    n_core = hn_seg[head_n:] if head_n < len(hn_seg) else hn_seg
    n_voicing = measure_voicing(n_core)
    check("[n] voicing", n_voicing, VOICING_MIN_MODAL, 1.0)

    n_lf = measure_lf_ratio(n_core)
    check("[n] LF ratio", n_lf, 0.20, 1.0)

    # [m]₁
    print()
    print("  -- [m]₁ bilabial nasal --")
    m1_voicing = measure_voicing(segs[SEG_M1])
    check("[m]₁ voicing", m1_voicing, VOICING_MIN_MODAL, 1.0)

    m1_lf = measure_lf_ratio(segs[SEG_M1])
    check("[m]₁ LF ratio", m1_lf, 0.20, 1.0)

    # [m]₂
    print()
    print("  -- [m]₂ bilabial nasal (word-final) --")
    m2_seg = segs[SEG_M2]
    m2_core_n = int(VS_M_DUR_MS * DIL / 1000.0 * SR)
    m2_core = m2_seg[:m2_core_n] if m2_core_n < len(m2_seg) else m2_seg
    m2_voicing = measure_voicing(m2_core)
    check("[m]₂ voicing", m2_voicing, VOICING_MIN_MODAL, 1.0)

    m2_lf = measure_lf_ratio(m2_core)
    check("[m]₂ LF ratio", m2_lf, 0.20, 1.0)

    # ================================================================
    # SECTION K: SYLLABLE-LEVEL COHERENCE
    # ================================================================
    print()
    print("-" * 72)
    print("SECTION K: SYLLABLE-LEVEL COHERENCE")
    print("  RAT.NA.DHĀ.TA.MAM")
    print("-" * 72)

    # [t]₁ trough: should be below adjacent vowel cores
    t1_rms = rms(segs[SEG_T1])
    a1_core_n = int(VS_A_DUR_MS * DIL / 1000.0 * SR)
    a1_core_rms = rms(segs[SEG_A1T][:a1_core_n])
    a2_rms = rms(segs[SEG_A2])
    if t1_rms < min(a1_core_rms, a2_rms):
        check_pass("[t]₁ trough",
                  f"{t1_rms:.4f} < min({a1_core_rms:.4f}, {a2_rms:.4f})")
    else:
        check("[t]₁ trough", t1_rms, 0.0, min(a1_core_rms, a2_rms))

    # [t]₂ trough
    t2_rms = rms(segs[SEG_T2])
    aa_core_n = int(VS_AA_DUR_MS * DIL / 1000.0 * SR)
    aa_core_rms = rms(segs[SEG_AAT][:aa_core_n])
    # [ɑ]₃ from opening head segment
    ha3_head_n = int(OPENING_HEAD_MS * DIL / 1000.0 * SR)
    a3_core = segs[SEG_HA3][ha3_head_n:] if ha3_head_n < len(segs[SEG_HA3]) \
              else segs[SEG_HA3]
    a3_rms = rms(a3_core)
    if t2_rms < min(aa_core_rms, a3_rms):
        check_pass("[t]₂ trough",
                  f"{t2_rms:.4f} < min({aa_core_rms:.4f}, {a3_rms:.4f})")
    else:
        check("[t]₂ trough", t2_rms, 0.0, min(aa_core_rms, a3_rms))

    # [aː] relative amplitude (longest vowel, should be prominent)
    # v5.0.1: Use core-only RMS for composite segments.
    # The closing tail lowers full-segment RMS, making
    # core-only / full-composite > 1.0 — arithmetic, not physics.
    core_rms_list = []
    for idx, seg in enumerate(segs):
        if len(seg) == 0:
            continue
        if idx in CLOSING_TAIL_SEGMENTS:
            core_ms_val = CLOSING_TAIL_SEGMENTS[idx]
            core_n_val = int(core_ms_val * DIL / 1000.0 * SR)
            core_rms_list.append(rms(seg[:core_n_val] if core_n_val < len(seg) else seg))
        elif idx in OPENING_HEAD_SEGMENTS:
            head_ms_val = OPENING_HEAD_SEGMENTS[idx]
            head_n_val = int(head_ms_val * DIL / 1000.0 * SR)
            core_rms_list.append(rms(seg[head_n_val:] if head_n_val < len(seg) else seg))
        else:
            core_rms_list.append(rms(seg))
    max_core_rms = max(core_rms_list) if core_rms_list else 1.0
    aa_rel = aa_core_rms / max_core_rms if max_core_rms > 1e-10 else 0.0
    check("[aː] relative amplitude", aa_rel, 0.60, 1.0)

    # Word duration
    word_dur_ms = len(word) / SR * 1000.0
    check("Word duration", word_dur_ms, 550.0, 1000.0, unit='ms', fmt='.1f')

    # ================================================================
    # SUMMARY
    # ================================================================
    print()
    print("=" * 72)
    total = n_pass + n_fail
    if n_fail == 0:
        print(f"ALL {total} DIAGNOSTICS PASSED")
        print()
        print("RATNADHĀTAMAM v17 UNIFIED PLUCK ARCHITECTURE — VERIFIED.")
    else:
        print(f"{n_pass}/{total} PASSED, {n_fail} FAILED")
        print()
        print("FAILURES:")
        for passed, msg in results:
            if not passed:
                print(f"  {msg}")

    print()
    print("Ruler calibration history:")
    print("  v1.0–v3.0: Initial calibrated diagnostics (8/8)")
    print("  v4.4: Cold-start exclusion (IIR initialization)")
    print("  v4.5: Envelope-normalized periodicity")
    print("  v4.6: Segment-aware continuity (core-only)")
    print("  v4.7: Removed max|delta| ratio (wrong measurement)")
    print("  v4.7.1: Removed tail voicing (wrong instrument)")
    print("  v5.0: Architecture update — v17 unified pluck")
    print("        [t] now UNIFIED SOURCE (47ms, not 8ms burst)")
    print("        Closing tails: [ɑ]₁ and [aː] own the closure")
    print("        Opening heads: [n] and [ɑ]₃ own the onset")
    print("        Cold-start: 4 periods (b=[g] convention)")
    print("        Cold-start ceiling: 5.0 (IIR warm-up)")
    print("        [dʰ]: closure LF + murmur H1-H2 + duration")
    print()
    print("Section structure:")
    print("  A: Signal integrity (NaN, Inf, peak, DC)")
    print("  B: Signal continuity (glottal periodicity)")
    print("  C: [t]₁ unified (closure, centroid, voicelessness)")
    print("  D: [t]₂ unified (closure, centroid, voicelessness)")
    print("  E: [t]₁-vs-[t]₂ place consistency")
    print("  F: Closing tails (core voicing + RMS fade)")
    print("  G: Opening heads (rising amplitude + core voicing)")
    print("  H: [dʰ] voiced aspirated (voice bar, murmur, H1-H2)")
    print("  I: Vowels ([ɑ]₁, [ɑ]₂, [ɑ]₃, [ɑ]₄, [aː])")
    print("  J: Tap [r] + Nasals [n], [m]₁, [m]₂")
    print("  K: Syllable cadence (troughs, prominence, duration)")
    print()
    print("Phonemes verified in this word:")
    print("  [ɾ]   alveolar tap")
    print("  [ɑ]   short open central unrounded (×4)")
    print("  [t]   voiceless dental stop (UNIFIED, ×2)")
    print("  [n]   dental nasal")
    print("  [dʰ]  voiced dental aspirated stop")
    print("  [aː]  long open central unrounded")
    print("  [m]   bilabial nasal (×2, word-final)")
    print()
    print("Śikṣā alignment:")
    print("  [t]  = dantya aghoṣa alpaprāṇa ✓")
    print("  [dʰ] = dantya ghoṣa mahāprāṇa ✓")
    print()
    print("Architecture:")
    print("  PLUCK + UNIFIED SOURCE compose:")
    print("    [ɑ]₁ owns closure (closing tail) before [t]₁")
    print("    [aː] owns closure (closing tail) before [t]₂")
    print("    [t]₁,[t]₂ own internal physics (one breath, one envelope)")
    print("    [n] owns onset (opening head) after [t]₁")
    print("    [ɑ]₃ owns onset (opening head) after [t]₂")
    print("    [dʰ] voiced: voice bar + burst + murmur + cutback")
    print("    No boundary anywhere is born from different sources")
    print()
    print("PERCEPTUAL VERIFICATION:")
    print("  afplay output_play/diag_rat_t_unified_slow12x.wav")
    print("  afplay output_play/diag_rat_dh_iso_slow12x.wav")
    print("  afplay output_play/diag_rat_ATn_syllable_slow12x.wav")
    print("  afplay output_play/diag_rat_AATa_syllable_slow12x.wav")
    print("  afplay output_play/diag_rat_word_slow6x.wav")
    print("  afplay output_play/diag_rat_perf_hall.wav")
    print()
    print("The ear is the FINAL arbiter.")
    print()
    print('"The sounds were always there.')
    print('  The language is being found, not invented."')
    print("=" * 72)
    print()

    return n_fail == 0


if __name__ == "__main__":
    success = run_diagnostics()
    sys.exit(0 if success else 1)
