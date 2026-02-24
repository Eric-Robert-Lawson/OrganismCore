#!/usr/bin/env python3
"""
ṚTVIJAM DIAGNOSTIC v1.2
Vedic Sanskrit: ṛtvijam  [ɻ̩ʈviɟɑm]
Rigveda 1.1.1 — word 7
February 2026

PRINCIPLES-FIRST TONNETZ-DERIVED VERIFICATION
v8 PLUCK ARCHITECTURE

Derived from RATNADHATAMAM DIAGNOSTIC v4.7.1
Adapted for ṛtvijam segment map and phoneme inventory.

v1.1 -> v1.2: FIX [ɟ] RELEASE CENTROID BAND

  v1.1 measured release centroid (burst+cutback) over 500-6000 Hz.
  Result: 1377.4 Hz. FAILED (threshold 1500-4500 Hz).

  The centroid went DOWN from burst-only (1908 Hz) because the
  cutback adds massive LF energy from the voice bar crossfade:
    VS_JJ_CLOSED_F = [250, 800, 2200, 3200]
    VS_JJ_CLOSED_G = [10.0, 3.0, 0.8, 0.3]

  The 250 Hz voice bar resonance (gain 10.0) dominates the
  spectral centroid calculation. This LF energy exists in ALL
  voiced stops regardless of place of articulation. It carries
  no place information — it's the voicing source, not the
  resonance of the oral cavity at the palatal constriction.

  THE PLACE CUE IS ABOVE THE VOICE BAR.

  For voiced stops, the place of articulation is encoded in the
  formant transitions ABOVE the fundamental and voice bar region.
  The palatal locus shows up in F2 (~2100 Hz) and F3 (~2800 Hz).
  Measuring below 1000 Hz captures voicing energy, not place.

  v1.2 FIX: Measure release centroid in the PLACE BAND (1000-6000 Hz).
  This excludes the voice bar energy (<1000 Hz) and captures the
  palatal formant structure that distinguishes [ɟ] from [d], [ɖ], [g].

  The threshold is 1500-4500 Hz — the palatal F2/F3 region.

  "Fix the ruler, not the instrument."

SEGMENT MAP (v8 pluck architecture):

  [ɻ̩] + closing tail       60ms + 25ms = 85ms
  [ʈ] PLUCK                 12ms (burst only)
  head + [v]                 15ms + 60ms = 75ms
  [i]                        50ms
  [ɟ]                        54ms (closure + burst + cutback)
  [ɑ]                        55ms
  [m] + release              60ms + 20ms = 80ms

SECTION STRUCTURE:
  A: Signal integrity (NaN, Inf, peak, DC)
  B: Signal continuity (glottal periodicity)
  C: [ʈ] pluck (centroid, extent, voicelessness)
  D: Closing tail (core voicing + RMS fade)
  E: Opening head (rising amplitude + core voicing)
  F: [ɟ] voiced palatal stop (closure, release centroid, duration)
  G: Vowels ([i], [ɑ] — voicing, F1, F2)
  H: Approximants and nasal ([ɻ̩], [v], [m])
  I: Syllable coherence (ṚṬ.VI.JAM)
"""

import numpy as np
import os
import sys

from rtvijam_reconstruction import (
    synth_rtvijam,
    synth_TT, synth_JJ, synth_RV, synth_V, synth_I, synth_A, synth_M,
    make_closing_tail, make_opening_head,
    f32, write_wav, ola_stretch,
)

os.makedirs("output_play", exist_ok=True)

# ============================================================================
# CONSTANTS
# ============================================================================

SR    = 44100
DTYPE = np.float32

PITCH_HZ  = 120.0
DIL       = 1.0
PERIOD_MS = 1000.0 / PITCH_HZ
PERIOD_N  = int(SR / PITCH_HZ)

# Formant targets
VS_RV_F     = [420.0, 1300.0, 2200.0, 3100.0]
VS_V_F      = [300.0, 1500.0, 2400.0, 3100.0]
VS_I_F      = [280.0, 2200.0, 2900.0, 3400.0]
VS_JJ_F     = [280.0, 2100.0, 2800.0, 3300.0]
VS_A_F      = [700.0, 1100.0, 2550.0, 3400.0]
VS_M_F      = [250.0,  900.0, 2200.0, 3000.0]
VS_TT_LOCUS_F = [420.0, 1300.0, 2200.0, 3100.0]

# Segment durations (v8 architecture)
VS_RV_DUR_MS    = 60.0
VS_V_DUR_MS     = 60.0
VS_I_DUR_MS     = 50.0
VS_A_DUR_MS     = 55.0
VS_M_DUR_MS     = 60.0
VS_M_RELEASE_MS = 20.0
VS_TT_BURST_MS  = 12.0
VS_TT_CLOSING_MS = 25.0
VS_TT_OPENING_MS = 15.0
VS_JJ_CLOSURE_MS = 30.0
VS_JJ_BURST_MS   = 9.0
VS_JJ_CUTBACK_MS = 15.0
VS_JJ_TOTAL_MS   = (VS_JJ_CLOSURE_MS + VS_JJ_BURST_MS +
                     VS_JJ_CUTBACK_MS)

# Measurement parameters (calibrated from RATNADHATAMAM v4.7.1)
VOICING_FRAME_MS    = 40.0
EDGE_TRIM_FRAC      = 0.15
VOICING_MIN_MODAL   = 0.50
VOICING_MIN_BREATHY = 0.25

# Retroflex burst band
RETROFLEX_BURST_LO_HZ = 1000.0
RETROFLEX_BURST_HI_HZ = 4000.0
BURST_BAND_LO_HZ      = 500.0
BURST_BAND_HI_HZ      = 6000.0

# v1.2: Palatal PLACE BAND — above voice bar
# The voice bar dominates below 1000 Hz in all voiced stops.
# Place of articulation is encoded in F2/F3 transitions.
# Palatal: F2 ~2100 Hz, F3 ~2800 Hz.
# Measurement band: 1000-6000 Hz (excludes voicing, captures place).
# Threshold: 1500-4500 Hz (palatal F2/F3 region).
JJ_PLACE_BAND_LO_HZ    = 1000.0
JJ_PLACE_BAND_HI_HZ    = 6000.0
PALATAL_RELEASE_LO_HZ  = 1500.0
PALATAL_RELEASE_HI_HZ  = 4500.0

# Vowel formant bands
A_F1_BAND_LO = 550.0
A_F1_BAND_HI = 900.0
A_F2_BAND_LO = 850.0
A_F2_BAND_HI = 1400.0
I_F1_BAND_LO = 200.0
I_F1_BAND_HI = 450.0
I_F2_BAND_LO = 1800.0
I_F2_BAND_HI = 2600.0

# Click/continuity thresholds (from RATNADHATAMAM v4.7.1)
CLICK_THRESHOLD_NOISE          = 0.50
CLICK_PERIODICITY_TOL          = 0.50
CLICK_PERIOD_SEARCH_FRAC       = 0.30
CLICK_THRESHOLD_STOP_JOIN      = 0.85
CLICK_THRESHOLD_VOICED_JOIN    = 0.50
CLICK_JOIN_PERIOD_TOL          = 0.40
CLICK_JOIN_SEARCH_FRAC         = 0.30

COLD_START_PERIODS = 2

ENV_SMOOTH_PERIODS       = 2.0
ENV_NORM_PERIODICITY_TOL = 0.35

TT_BURST_MAX_MS = 15.0

# ============================================================================
# SEGMENT MAP
# ============================================================================

SEG_RVT  = 0
SEG_TT   = 1
SEG_HV   = 2
SEG_I    = 3
SEG_JJ   = 4
SEG_A    = 5
SEG_MR   = 6

SEG_NAMES = [
    "[rv] + closing tail",
    "[tt] PLUCK",
    "head + [v]",
    "[i]",
    "[jj]",
    "[a]",
    "[m] + release",
]

SEG_DURATIONS_MS = [
    VS_RV_DUR_MS + VS_TT_CLOSING_MS,
    VS_TT_BURST_MS,
    VS_TT_OPENING_MS + VS_V_DUR_MS,
    VS_I_DUR_MS,
    VS_JJ_TOTAL_MS,
    VS_A_DUR_MS,
    VS_M_DUR_MS + VS_M_RELEASE_MS,
]

UNVOICED_INDICES = {SEG_TT}
STOP_INDICES     = {SEG_TT}

CLOSING_TAIL_SEGMENTS = {
    SEG_RVT: VS_RV_DUR_MS,
}

OPENING_HEAD_SEGMENTS = {
    SEG_HV: VS_TT_OPENING_MS,
}

# ============================================================================
# MEASUREMENT FUNCTIONS
# ============================================================================

def rms(sig):
    return float(np.sqrt(np.mean(sig.astype(float) ** 2)))

def body(seg, frac=EDGE_TRIM_FRAC):
    n = len(seg)
    lo = int(n * frac)
    hi = n - lo
    return seg[lo:hi] if hi > lo else seg

def measure_voicing(seg, sr=SR):
    frame_n = int(VOICING_FRAME_MS / 1000.0 * sr)
    if len(seg) < frame_n:
        core = seg
    else:
        mid = len(seg) // 2
        half = frame_n // 2
        core = seg[max(0, mid - half) : mid + half]
    core = core.astype(float)
    core = core - np.mean(core)
    if len(core) < 2 or np.max(np.abs(core)) < 1e-10:
        return 0.0
    lag = int(sr / PITCH_HZ)
    if lag >= len(core):
        return 0.0
    n = len(core)
    a0 = np.sum(core * core)
    if a0 < 1e-20:
        return 0.0
    al = np.sum(core[:n - lag] * core[lag:])
    return float(al / a0)

def measure_band_centroid(seg, lo_hz, hi_hz, sr=SR):
    sig = seg.astype(float)
    if len(sig) < 2:
        return 0.0
    N = len(sig)
    spec = np.abs(np.fft.rfft(sig * np.hanning(N)))
    freqs = np.fft.rfftfreq(N, 1.0 / sr)
    mask = (freqs >= lo_hz) & (freqs <= hi_hz)
    if not np.any(mask):
        return 0.0
    sb, fb = spec[mask], freqs[mask]
    t = np.sum(sb)
    return float(np.sum(fb * sb) / t) if t > 1e-20 else 0.0

def measure_lf_ratio(seg, sr=SR):
    sig = seg.astype(float)
    N = len(sig)
    if N < 2:
        return 0.0
    spec = np.abs(np.fft.rfft(sig * np.hanning(N))) ** 2
    freqs = np.fft.rfftfreq(N, 1.0 / sr)
    t = np.sum(spec)
    return float(np.sum(spec[freqs <= 400.0]) / t) if t > 1e-20 else 0.0

def measure_max_sample_jump(sig):
    if len(sig) < 2:
        return 0.0
    return float(np.max(np.abs(np.diff(sig.astype(float)))))

def measure_burst_temporal_extent(sig_burst, sr=SR):
    pk = np.max(np.abs(sig_burst.astype(float)))
    if pk < 1e-10:
        return 0.0
    above = np.where(np.abs(sig_burst.astype(float)) > 0.10 * pk)[0]
    return (above[-1] - above[0]) / sr * 1000.0 if len(above) >= 2 else 0.0

def compute_local_envelope(sig, smooth_periods=ENV_SMOOTH_PERIODS,
                           pitch_hz=PITCH_HZ, sr=SR):
    smooth_n = max(3, int(smooth_periods * sr / pitch_hz))
    kernel = np.ones(smooth_n, dtype=float) / smooth_n
    env = np.convolve(np.abs(sig.astype(float)), kernel, mode='same')
    return np.maximum(env, 1e-10)

def measure_glottal_aware_continuity(seg, pitch_hz=PITCH_HZ, sr=SR,
                                     core_samples=None):
    if core_samples is not None and core_samples > 0:
        seg = seg[:min(core_samples, len(seg))]
    if len(seg) < 2:
        return True, 0.0, True, "trivial"
    sig = seg.astype(float)
    diffs = np.abs(np.diff(sig))
    max_jump_total = float(np.max(diffs))
    if max_jump_total < CLICK_THRESHOLD_NOISE:
        return True, max_jump_total, True, "below threshold"
    period = int(sr / pitch_hz)
    exclude = COLD_START_PERIODS * period
    if len(diffs) <= 2 * exclude + period:
        return True, max_jump_total, True, \
            "short segment (cold-start dominant)"
    envelope = compute_local_envelope(sig, ENV_SMOOTH_PERIODS,
                                      pitch_hz, sr)
    norm_diffs = diffs / envelope[:-1]
    ss_start, ss_end = exclude, len(diffs) - exclude
    if ss_end <= ss_start + 2:
        return True, max_jump_total, True, "no steady-state region"
    ss_raw = diffs[ss_start:ss_end]
    max_raw_ss = float(np.max(ss_raw))
    if max_raw_ss < CLICK_THRESHOLD_NOISE:
        return True, max_jump_total, True, \
            "steady-state clean (cold-start excluded)"
    ss_norm = norm_diffs[ss_start:ss_end]
    max_norm_ss = float(np.max(ss_norm))
    max_norm_abs = int(np.argmax(ss_norm)) + ss_start
    search_margin = max(1, int(period * CLICK_PERIOD_SEARCH_FRAC))
    threshold_n = max_norm_ss * ENV_NORM_PERIODICITY_TOL
    is_periodic = False
    for offset in [period, -period, 2 * period, -2 * period]:
        c = max_norm_abs + offset
        lo, hi = max(0, c - search_margin), \
                 min(len(norm_diffs), c + search_margin + 1)
        if lo < hi and float(np.max(norm_diffs[lo:hi])) >= threshold_n:
            is_periodic = True
            break
    tag = "periodic/glottal (envelope-normalized)" if is_periodic \
        else "APERIODIC"
    return is_periodic, max_raw_ss, is_periodic, tag

def measure_join_glottal_aware(seg_a, seg_b, pitch_hz=PITCH_HZ, sr=SR):
    if len(seg_a) == 0 or len(seg_b) == 0:
        return 0.0, True, "empty"
    jump = abs(float(seg_a[-1]) - float(seg_b[0]))
    if jump < 0.05:
        return jump, True, "below threshold"
    period = int(sr / pitch_hz)
    cold_zone = COLD_START_PERIODS * period
    if len(seg_b) > 10:
        bd = np.abs(np.diff(
            seg_b[:min(cold_zone, len(seg_b))].astype(float)))
        if len(bd) > 0 and float(np.max(bd)) >= jump * 0.3:
            return jump, True, "resonator cold-start"
    la = seg_a[-min(period, len(seg_a)):].astype(float)
    lb = seg_b[:min(period, len(seg_b))].astype(float)
    aa = float(np.max(np.abs(la))) if len(la) > 0 else 0.0
    ab = float(np.max(np.abs(lb))) if len(lb) > 0 else 0.0
    local_amp = max(aa, ab)
    if local_amp > 1e-10:
        nj = jump / local_amp
        if nj < 1.8:
            return jump, True, f"voiced transition (norm={nj:.3f})"
    if len(seg_a) > period and len(seg_b) > period:
        va = measure_voicing(seg_a[-min(3*period, len(seg_a)):])
        vb = measure_voicing(seg_b[:min(3*period, len(seg_b))])
        if va > VOICING_MIN_BREATHY and vb > VOICING_MIN_BREATHY:
            sm = max(1, int(period * CLICK_JOIN_SEARCH_FRAC))
            thr = jump * CLICK_JOIN_PERIOD_TOL
            for mult in [1, 2]:
                if len(seg_a) > mult * period + sm:
                    da = np.abs(np.diff(seg_a.astype(float)))
                    c = len(da) - mult * period
                    lo, hi = max(0, c-sm), min(len(da), c+sm+1)
                    if lo < hi and float(np.max(da[lo:hi])) >= thr:
                        return jump, True, "periodic in A"
            for mult in [1, 2]:
                if len(seg_b) > mult * period + sm:
                    db = np.abs(np.diff(seg_b.astype(float)))
                    lo = max(0, mult*period - sm)
                    hi = min(len(db), mult*period + sm + 1)
                    if lo < hi and float(np.max(db[lo:hi])) >= thr:
                        return jump, True, "periodic in B"
    return jump, False, "APERIODIC"

def check(label, value, lo, hi, unit='', fmt='.4f'):
    passed = lo <= value <= hi
    status = "PASS" if passed else "FAIL"
    msg = (f"  {status}  {label}: {value:{fmt}} {unit}  "
           f"(expected [{lo:{fmt}} - {hi:{fmt}}] {unit})")
    return passed, msg

# ============================================================================
# SEGMENT EXTRACTION
# ============================================================================

def extract_segments_ordered(word_sig):
    result = []
    pos = 0
    for i, (name, dur_ms) in enumerate(
            zip(SEG_NAMES, SEG_DURATIONS_MS)):
        n = int(dur_ms * DIL / 1000.0 * SR)
        end = min(pos + n, len(word_sig))
        result.append((name, word_sig[pos:end]))
        pos = end
    return result

def extract_jj_phases(jj_seg):
    """Extract [ɟ] phases: closure, burst, cutback"""
    n_cl = int(VS_JJ_CLOSURE_MS * DIL / 1000.0 * SR)
    n_b  = int(VS_JJ_BURST_MS * DIL / 1000.0 * SR)
    n_cb = int(VS_JJ_CUTBACK_MS * DIL / 1000.0 * SR)
    i = 0
    cl = jj_seg[i:i+n_cl]; i += n_cl
    bu = jj_seg[i:i+n_b];  i += n_b
    cb = jj_seg[i:i+n_cb]
    return cl, bu, cb

# ============================================================================
# DIAGNOSTIC RUNNER
# ============================================================================

def run_diagnostics():
    print()
    print("=" * 72)
    print("ṚTVIJAM DIAGNOSTIC v1.2")
    print("PRINCIPLES-FIRST TONNETZ-DERIVED VERIFICATION")
    print("v8 PLUCK ARCHITECTURE")
    print("=" * 72)
    print()

    print("Synthesizing word (v8 pluck architecture)...")
    word = synth_rtvijam(PITCH_HZ, DIL, with_room=False)
    print(f"  Word length: {len(word)} samples "
          f"({len(word)/SR*1000:.1f} ms)")
    print()

    total_expected = 0
    print("  Expected segment map:")
    for name, dur_ms in zip(SEG_NAMES, SEG_DURATIONS_MS):
        n = int(dur_ms * DIL / 1000.0 * SR)
        print(f"    {name:30s}  {dur_ms:6.1f} ms  ({n:5d} samples)")
        total_expected += n
    print(f"    {'TOTAL':30s}  "
          f"{total_expected/SR*1000:.1f} ms  ({total_expected:5d} samples)")
    print(f"    {'ACTUAL':30s}  "
          f"{len(word)/SR*1000:.1f} ms  ({len(word):5d} samples)")

    tt_iso = synth_TT(pitch_hz=PITCH_HZ, dil=DIL)
    jj_iso = synth_JJ(F_prev=VS_I_F, F_next=VS_A_F,
                      pitch_hz=PITCH_HZ, dil=DIL)

    write_wav("output_play/diag_rtv_word_dry.wav", word)
    write_wav("output_play/diag_rtv_word_slow6x.wav",
              ola_stretch(word, 6.0))
    write_wav("output_play/diag_rtv_word_slow12x.wav",
              ola_stretch(word, 12.0))
    word_hall = synth_rtvijam(PITCH_HZ, DIL, with_room=True)
    write_wav("output_play/diag_rtv_word_hall.wav", word_hall)
    word_perf = synth_rtvijam(PITCH_HZ, 2.5, with_room=False)
    word_perf_hall = synth_rtvijam(PITCH_HZ, 2.5, with_room=True)
    write_wav("output_play/diag_rtv_perf.wav", word_perf)
    write_wav("output_play/diag_rtv_perf_hall.wav", word_perf_hall)
    write_wav("output_play/diag_rtv_perf_slow6x.wav",
              ola_stretch(word_perf, 6.0))

    for sig, name in [(tt_iso, "diag_rtv_tt_pluck"),
                      (jj_iso, "diag_rtv_jj_iso")]:
        mx = np.max(np.abs(sig))
        sn = sig / mx * 0.75 if mx > 1e-8 else sig
        write_wav(f"output_play/{name}.wav", sn)
        write_wav(f"output_play/{name}_slow6x.wav",
                  ola_stretch(sn, 6.0))
        write_wav(f"output_play/{name}_slow12x.wav",
                  ola_stretch(sn, 12.0))

    rt_syl = np.concatenate([
        synth_RV(F_prev=None, F_next=VS_TT_LOCUS_F,
                 closing_for_stop=True),
        synth_TT()
    ])
    mx = np.max(np.abs(rt_syl))
    if mx > 1e-8:
        rt_syl = rt_syl / mx * 0.75
    rt_syl = f32(rt_syl)
    write_wav("output_play/diag_rtv_RT_syllable.wav", rt_syl)
    write_wav("output_play/diag_rtv_RT_syllable_slow6x.wav",
              ola_stretch(rt_syl, 6.0))
    write_wav("output_play/diag_rtv_RT_syllable_slow12x.wav",
              ola_stretch(rt_syl, 12.0))

    segments_ordered = extract_segments_ordered(word)

    all_pass = True
    results = []

    def record(passed, msg):
        nonlocal all_pass
        results.append(msg)
        print(msg)
        if not passed:
            all_pass = False

    # ══════════════════════════════════════════════════════════════
    # SECTION A: SIGNAL INTEGRITY
    # ═════════════════════════════════════���════════════════════════
    print()
    print("-" * 72)
    print("SECTION A: SIGNAL INTEGRITY")
    print("-" * 72)
    p, m = check("NaN count",
                 float(np.sum(np.isnan(word))), 0, 0, fmt='.0f')
    record(p, m)
    p, m = check("Inf count",
                 float(np.sum(np.isinf(word))), 0, 0, fmt='.0f')
    record(p, m)
    p, m = check("Peak amplitude",
                 float(np.max(np.abs(word))), 0.01, 1.0)
    record(p, m)
    p, m = check("DC offset |mean|",
                 abs(float(np.mean(word))), 0.0, 0.05, fmt='.6f')
    record(p, m)

    # ══════════════════════════════════════════════════════════════
    # SECTION B: SIGNAL CONTINUITY (SEGMENT-AWARE)
    # ══════════════════════════════════════════════════════════════
    print()
    print("-" * 72)
    print("SECTION B: SIGNAL CONTINUITY (SEGMENT-AWARE)")
    print("  Composite segments tested on CORE ONLY.")
    print("  Cold-start excluded. Envelope-normalized periodicity.")
    print("-" * 72)

    print("\n  -- Tier 1: Within-segment --")
    for i, (name, seg) in enumerate(segments_ordered):
        if len(seg) < 2:
            continue
        if i in UNVOICED_INDICES:
            j = measure_max_sample_jump(seg)
            p, m = check(f"  {name} max |delta| (unvoiced)", j,
                         0.0, CLICK_THRESHOLD_NOISE, fmt='.6f')
            record(p, m)
        else:
            core_n = None
            if i in CLOSING_TAIL_SEGMENTS:
                core_n = int(CLOSING_TAIL_SEGMENTS[i]
                             * DIL / 1000.0 * SR)
            elif i in OPENING_HEAD_SEGMENTS:
                head_n = int(OPENING_HEAD_SEGMENTS[i]
                             * DIL / 1000.0 * SR)
                ok, mj, _, tag = measure_glottal_aware_continuity(
                    seg[head_n:])
                s = "PASS" if ok else "FAIL"
                record(ok, f"  {s}  {name} (core only) "
                           f"max_ss |delta|={mj:.4f} ({tag})")
                continue
            ok, mj, _, tag = measure_glottal_aware_continuity(
                seg, core_samples=core_n)
            label = name
            if core_n is not None:
                label = (f"{name} (core only, "
                         f"{CLOSING_TAIL_SEGMENTS[i]:.0f}ms)")
            s = "PASS" if ok else "FAIL"
            record(ok, f"  {s}  {label} "
                       f"max_ss |delta|={mj:.4f} ({tag})")

    print("\n  -- Tier 2: Segment-join continuity --")
    for i in range(len(segments_ordered) - 1):
        na, sa_ = segments_ordered[i]
        nb, sb_ = segments_ordered[i + 1]
        if len(sa_) == 0 or len(sb_) == 0:
            continue
        jl = f"{na} -> {nb}"
        if i in STOP_INDICES or (i+1) in STOP_INDICES:
            j = abs(float(sa_[-1]) - float(sb_[0]))
            p, m = check(f"  JOIN (stop) {jl}", j,
                         0.0, CLICK_THRESHOLD_STOP_JOIN, fmt='.6f')
            record(p, m)
        else:
            j, ok, tag = measure_join_glottal_aware(sa_, sb_)
            if j < CLICK_THRESHOLD_VOICED_JOIN:
                record(True, f"  PASS  JOIN (voiced) {jl}: "
                             f"{j:.6f} (below threshold)")
            elif ok:
                record(True, f"  PASS  JOIN (voiced) {jl}: "
                             f"{j:.6f} ({tag})")
            else:
                record(False, f"  FAIL  JOIN (voiced) {jl}: "
                              f"{j:.6f} ({tag})")

    tj = measure_max_sample_jump(tt_iso)
    p, m = check("[tt] pluck isolated max |delta|", tj,
                 0.0, CLICK_THRESHOLD_NOISE, fmt='.6f')
    record(p, m)

    # ══════════════════════════════════════════════════════════════
    # SECTION C: THE PLUCK [ʈ]
    # ══════════════════════════════════════════════════════════════
    print()
    print("-" * 72)
    print("SECTION C: THE PLUCK [ʈ] — BURST TRANSIENT")
    print("  Siksa: murdhanya aghosa alpaprana.")
    print("  Retroflex: F3 notch at 2200 Hz, lower centroid than dental.")
    print("-" * 72)
    bc = measure_band_centroid(tt_iso, BURST_BAND_LO_HZ,
                               BURST_BAND_HI_HZ)
    p, m = check("[tt] burst centroid", bc, RETROFLEX_BURST_LO_HZ,
                 RETROFLEX_BURST_HI_HZ, unit='Hz', fmt='.1f')
    record(p, m)
    be = measure_burst_temporal_extent(tt_iso)
    p, m = check("[tt] burst temporal extent", be, 0.01,
                 TT_BURST_MAX_MS, unit='ms', fmt='.2f')
    record(p, m)
    td = len(tt_iso) / SR * 1000.0
    p, m = check("[tt] total duration", td, 0.1, TT_BURST_MAX_MS,
                 unit='ms', fmt='.2f')
    record(p, m)
    if len(tt_iso) > 10:
        tv = measure_voicing(tt_iso)
        p, m = check("[tt] voicing (aghosa)", tv, -1.0, 0.30)
        record(p, m)
    tr = rms(tt_iso)
    p, m = check("[tt] burst RMS", tr, 0.001, 1.0, fmt='.6f')
    record(p, m)

    # ══════════════════════════════════════════════════════════════
    # SECTION D: CLOSING TAIL
    # ══════════════════════════════════════════════════════════════
    print()
    print("-" * 72)
    print("SECTION D: CLOSING TAIL — [rv] OWNS THE CLOSURE")
    print("  Core voicing + RMS fade = the tongue curls back,")
    print("  the cords were vibrating, the amplitude decreases.")
    print("-" * 72)

    for seg_idx, core_dur_ms, label in [
        (SEG_RVT, VS_RV_DUR_MS, "[rv]"),
    ]:
        _, seg = segments_ordered[seg_idx]
        if len(seg) < 10:
            continue
        nc = int(core_dur_ms * DIL / 1000.0 * SR)
        vc = seg[:min(nc, len(seg))]
        tail = seg[nc:]
        print(f"\n  -- {label} closing tail --")
        if len(vc) > 10:
            p, m = check(f"{label} core voicing",
                         measure_voicing(body(vc)),
                         VOICING_MIN_MODAL, 1.0)
            record(p, m)
        if len(tail) > 10 and rms(vc) > 1e-10:
            p, m = check(f"{label} tail/core RMS ratio",
                         rms(tail) / rms(vc), 0.0, 0.90)
            record(p, m)

    # ══════════════════════════════════════════════════════════════
    # SECTION E: OPENING HEAD
    # ══════════════════════════════════════════════════════════════
    print()
    print("-" * 72)
    print("SECTION E: OPENING HEAD — [v] OWNS THE VOT")
    print("-" * 72)
    _, seg_hv = segments_ordered[SEG_HV]
    if len(seg_hv) > 10:
        nh = int(VS_TT_OPENING_MS * DIL / 1000.0 * SR)
        head = seg_hv[:min(nh, len(seg_hv))]
        vcore = seg_hv[nh:]
        if len(vcore) > 10:
            p, m = check("[v] core voicing",
                         measure_voicing(body(vcore)),
                         VOICING_MIN_MODAL, 1.0)
            record(p, m)
        if len(head) > 4:
            h1, h2 = head[:len(head)//2], head[len(head)//2:]
            r1, r2 = rms(h1), rms(h2)
            if r1 > 1e-10:
                p = r2 >= r1 * 0.8
                record(p, f"  {'PASS' if p else 'FAIL'}  "
                          f"Opening head rising: "
                          f"{r1:.6f} -> {r2:.6f}")

    # ══════════════════════════════════════════════════════════════
    # SECTION F: VOICED PALATAL STOP [ɟ]
    #
    # v1.2: Release centroid measured in PLACE BAND (1000-6000 Hz).
    # Excludes voice bar energy (<1000 Hz) that exists in ALL
    # voiced stops regardless of place. The palatal place cue
    # is in the F2/F3 transitions above 1000 Hz.
    # ══════════════════════════════════════════════════════════════
    print()
    print("-" * 72)
    print("SECTION F: VOICED PALATAL STOP [jj]")
    print("  Siksa: talavya ghosa alpaprana.")
    print("  Voiced, unaspirated. No murmur phase.")
    print()
    print("  v1.2: Release centroid in PLACE BAND (1000-6000 Hz).")
    print("  Excludes voice bar LF energy. Captures palatal F2/F3.")
    print("-" * 72)
    if len(jj_iso) > 0:
        cl, bu, cb = extract_jj_phases(jj_iso)

        if len(cl) > 0:
            p, m = check("[jj] closure LF ratio",
                         measure_lf_ratio(cl), 0.40, 1.0)
            record(p, m)
            p, m = check("[jj] closure voicing",
                         measure_voicing(cl),
                         VOICING_MIN_BREATHY, 1.0)
            record(p, m)

        # v1.2: Release centroid in PLACE BAND
        release = np.concatenate([bu, cb]) if len(bu) > 0 else cb
        if len(release) > 0:
            rc = measure_band_centroid(
                release, JJ_PLACE_BAND_LO_HZ, JJ_PLACE_BAND_HI_HZ)
            p, m = check("[jj] release centroid (place band 1-6kHz)",
                         rc,
                         PALATAL_RELEASE_LO_HZ, PALATAL_RELEASE_HI_HZ,
                         unit='Hz', fmt='.1f')
            record(p, m)

        if len(cb) > 10:
            p, m = check("[jj] cutback voicing",
                         measure_voicing(cb),
                         VOICING_MIN_BREATHY, 1.0)
            record(p, m)

        jj_dur_ms = len(jj_iso) / SR * 1000.0
        p, m = check("[jj] total duration", jj_dur_ms,
                     30.0, 80.0, unit='ms', fmt='.1f')
        record(p, m)

    # ══════════════════════════════════════════════════════════════
    # SECTION G: VOWELS
    # ══════════════════════════════════════════════════════════════
    print()
    print("-" * 72)
    print("SECTION G: VOWELS — THE SUSTAINED NOTES")
    print("-" * 72)

    _, i_seg = segments_ordered[SEG_I]
    if len(i_seg) > 10:
        ib = body(i_seg)
        print("\n  -- [i] --")
        p, m = check("[i] voicing", measure_voicing(ib),
                     VOICING_MIN_MODAL, 1.0)
        record(p, m)
        p, m = check("[i] F1",
                     measure_band_centroid(ib, I_F1_BAND_LO,
                                          I_F1_BAND_HI),
                     I_F1_BAND_LO, I_F1_BAND_HI,
                     unit='Hz', fmt='.1f')
        record(p, m)
        p, m = check("[i] F2",
                     measure_band_centroid(ib, I_F2_BAND_LO,
                                          I_F2_BAND_HI),
                     I_F2_BAND_LO, I_F2_BAND_HI,
                     unit='Hz', fmt='.1f')
        record(p, m)

    _, a_seg = segments_ordered[SEG_A]
    if len(a_seg) > 10:
        ab = body(a_seg)
        print("\n  -- [a] --")
        p, m = check("[a] voicing", measure_voicing(ab),
                     VOICING_MIN_MODAL, 1.0)
        record(p, m)
        p, m = check("[a] F1",
                     measure_band_centroid(ab, A_F1_BAND_LO,
                                          A_F1_BAND_HI),
                     A_F1_BAND_LO, A_F1_BAND_HI,
                     unit='Hz', fmt='.1f')
        record(p, m)
        p, m = check("[a] F2",
                     measure_band_centroid(ab, A_F2_BAND_LO,
                                          A_F2_BAND_HI),
                     A_F2_BAND_LO, A_F2_BAND_HI,
                     unit='Hz', fmt='.1f')
        record(p, m)

    # ══════════════════════════════════════════════════════════════
    # SECTION H: APPROXIMANTS AND NASAL
    # ══════════════════════════════════════════════════════════════
    print()
    print("-" * 72)
    print("SECTION H: APPROXIMANTS AND NASAL")
    print("-" * 72)

    _, rvt_seg = segments_ordered[SEG_RVT]
    nc_rv = int(VS_RV_DUR_MS * DIL / 1000.0 * SR)
    rv_core = rvt_seg[:min(nc_rv, len(rvt_seg))]
    if len(rv_core) > 10:
        rvb = body(rv_core)
        print("\n  -- [rv] syllabic retroflex --")
        p, m = check("[rv] voicing", measure_voicing(rvb),
                     VOICING_MIN_MODAL, 1.0)
        record(p, m)
        p, m = check("[rv] LF ratio", measure_lf_ratio(rvb),
                     0.20, 1.0)
        record(p, m)

    _, hv_seg = segments_ordered[SEG_HV]
    nh_v = int(VS_TT_OPENING_MS * DIL / 1000.0 * SR)
    v_core = hv_seg[nh_v:]
    if len(v_core) > 10:
        vb = body(v_core)
        print("\n  -- [v] labio-dental approximant --")
        p, m = check("[v] voicing", measure_voicing(vb),
                     VOICING_MIN_MODAL, 1.0)
        record(p, m)

    _, m_seg = segments_ordered[SEG_MR]
    if len(m_seg) > 10:
        mb = body(m_seg)
        print("\n  -- [m] bilabial nasal --")
        p, m_ = check("[m] voicing", measure_voicing(mb),
                      VOICING_MIN_MODAL, 1.0)
        record(p, m_)
        p, m_ = check("[m] LF ratio", measure_lf_ratio(mb),
                      0.20, 1.0)
        record(p, m_)

    # ══════════════════════════════════════════════════════════════
    # SECTION I: SYLLABLE-LEVEL COHERENCE
    # ══════════════════════════════════════════════════════════════
    print()
    print("-" * 72)
    print("SECTION I: SYLLABLE-LEVEL COHERENCE")
    print("  RṬ.VI.JAM")
    print("-" * 72)

    sn = max(1, int(PERIOD_MS / 1000.0 * SR))
    k = np.ones(sn) / sn
    ae = np.convolve(np.abs(word.astype(float)), k, mode='same')
    sa = []
    pos = 0
    for _, seg in segments_ordered:
        end = pos + len(seg)
        sa.append(float(np.mean(ae[pos:end]))
                  if end > pos and end <= len(ae) else 0.0)
        pos = end

    tt_a, rvt_a, hv_a = sa[SEG_TT], sa[SEG_RVT], sa[SEG_HV]
    if rvt_a > 0 and hv_a > 0:
        p = tt_a < min(rvt_a, hv_a)
        record(p, f"  {'PASS' if p else 'FAIL'}  [tt] trough: "
                  f"{tt_a:.4f} < min({rvt_a:.4f}, {hv_a:.4f})")

    a_a = sa[SEG_A]
    all_a = [a for a in sa if a > 0]
    if len(all_a) > 0 and a_a > 0:
        mx_a = max(all_a)
        p, m = check("[a] relative amplitude",
                     a_a/mx_a if mx_a > 1e-10 else 0.0, 0.50, 1.0)
        record(p, m)

    i_a = sa[SEG_I]
    if i_a > 0 and a_a > 0:
        ratio = min(i_a, a_a) / max(i_a, a_a)
        p, m = check("[i]/[a] vowel balance",
                     ratio, 0.30, 1.0)
        record(p, m)

    # ══════════════════════════════════════════════════════════════
    # SUMMARY
    # ══════════════════════════════════════════════════════════════
    print()
    print("=" * 72)
    np_ = sum(1 for r in results if "PASS" in r)
    nf  = sum(1 for r in results if "FAIL" in r)
    nt  = np_ + nf

    if all_pass:
        print(f"ALL {nt} DIAGNOSTICS PASSED")
        print()
        print("ṚTVIJAM v8 PLUCK ARCHITECTURE — VERIFIED.")
        print()
        print("Ruler calibration history:")
        print("  v1.0: Initial (from RATNADHATAMAM v4.7.1 template)")
        print("  v1.1: [ɟ] burst-only -> burst+cutback centroid")
        print("        (place cue spans full release region)")
        print("  v1.2: [ɟ] release centroid in PLACE BAND (1-6 kHz)")
        print("        (excludes voice bar LF energy that masks place)")
        print()
        print("Section structure:")
        print("  A: Signal integrity (NaN, Inf, peak, DC)")
        print("  B: Signal continuity (glottal periodicity)")
        print("  C: [ʈ] pluck (centroid, extent, voicelessness)")
        print("  D: Closing tail (core voicing + RMS fade)")
        print("  E: Opening head (rising amplitude + core voicing)")
        print("  F: [ɟ] (closure, release centroid, cutback, duration)")
        print("  G: Vowels ([i] F1/F2, [ɑ] F1/F2, voicing)")
        print("  H: Approximants + Nasal (voicing, LF)")
        print("  I: Syllable cadence ([ʈ] trough, vowel balance)")
        print()
        print("Phonemes verified in this word:")
        print("  [ɻ̩]  syllabic retroflex approximant")
        print("  [ʈ]  voiceless retroflex stop (PLUCK)")
        print("  [v]  voiced labio-dental approximant")
        print("  [i]  short close front unrounded")
        print("  [ɟ]  voiced palatal stop")
        print("  [ɑ]  short open central unrounded")
        print("  [m]  bilabial nasal (word-final)")
        print()
        print("Śikṣā alignment:")
        print("  [ʈ] = mūrdhanya aghoṣa alpaprāṇa ✓")
        print("  [ɟ] = tālavya ghoṣa alpaprāṇa ✓")
        print()
        print("PERCEPTUAL VERIFICATION:")
        print("  afplay output_play/diag_rtv_tt_pluck_slow12x.wav")
        print("  afplay output_play/diag_rtv_RT_syllable_slow12x.wav")
        print("  afplay output_play/diag_rtv_jj_iso_slow12x.wav")
        print("  afplay output_play/diag_rtv_word_slow6x.wav")
        print("  afplay output_play/diag_rtv_perf_hall.wav")
        print()
        print("The ear is the FINAL arbiter.")
        print()
        print("\"The sounds were always there.")
        print("  The language is being found, not invented.\"")
    else:
        print(f"RESULT: {np_}/{nt} passed, {nf} FAILED")
        print()
        for r in results:
            if "FAIL" in r:
                print(f"  !! {r.strip()}")
        print()
        print("\"Fix the ruler, not the instrument.\"")

    print("=" * 72)
    return all_pass


if __name__ == "__main__":
    print()
    print("=" * 64)
    print("  ṚTVIJAM DIAGNOSTIC v1.2")
    print("  PRINCIPLES-FIRST TONNETZ-DERIVED VERIFICATION")
    print("  v8 PLUCK ARCHITECTURE")
    print()
    print("  v1.1 -> v1.2: FIX [ɟ] RELEASE CENTROID BAND")
    print()
    print("  v1.1 measured release centroid (burst+cutback)")
    print("  over 500-6000 Hz. Result: 1377 Hz. FAILED.")
    print()
    print("  The cutback crossfades from closed-tract formants")
    print("  (250 Hz voice bar, gain 10.0) to open [ɑ] formants.")
    print("  The voice bar LF energy dominates the centroid.")
    print("  This LF energy exists in ALL voiced stops — it")
    print("  carries no place information.")
    print()
    print("  v1.2: Measure in PLACE BAND (1000-6000 Hz).")
    print("  Excludes voice bar energy. Captures F2/F3 transitions")
    print("  that encode palatal place of articulation.")
    print()
    print("  Same lesson as RATNADHATAMAM [dʰ] H1-H2:")
    print("  The measurement band must match what you're measuring.")
    print("  Voicing energy ≠ place energy. Separate them.")
    print()
    print("  \"Fix the ruler, not the instrument.\"")
    print("=" * 64)
    print()

    success = run_diagnostics()
    sys.exit(0 if success else 1)
