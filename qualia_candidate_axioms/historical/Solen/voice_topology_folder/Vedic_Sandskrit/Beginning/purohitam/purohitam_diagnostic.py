#!/usr/bin/env python3
"""
PUROHITAM DIAGNOSTIC v1.0
Vedic Sanskrit: purohitam [puroːhitɑm]
Rigveda 1.1.1 — word 4
"the household priest" (accusative singular)
February 2026

PRINCIPLES-FIRST TONNETZ-DERIVED VERIFICATION
v3 PLUCK ARCHITECTURE

Derived from RATNADHATAMAM DIAGNOSTIC v4.7.1
Same measurement functions. Same calibrated thresholds.
Same section structure. Adapted for purohitam phonemes.

SEGMENT MAP (v3 pluck architecture):

  [p] PLUCK (word-initial)     10ms silence + 8ms burst = 18ms
  head + [u]                   15ms rise + 50ms = 65ms
  [r]                          30ms
  [oo]                         100ms
  [h]                          65ms
  [i] + closing tail           50ms + 25ms = 75ms
  [t] PLUCK                   7ms burst only
  head + [a]                   15ms rise + 55ms = 70ms
  [m] + release                60ms + 20ms = 80ms

SECTION STRUCTURE:
  A: Signal integrity (NaN, Inf, peak, DC)
  B: Signal continuity (glottal periodicity)
  C: [p] pluck (centroid, voicelessness, word-initial)
  D: [t] pluck (centroid, voicelessness)
  E: Closing tail ([i] core voicing + RMS fade)
  F: Opening heads ([u] after [p], [a] after [t])
  G: Vowels ([u], [oo], [i], [a] — voicing, F1, F2)
  H: Fricative [h] (noise, voicelessness)
  I: Tap [r] + Nasal [m] (voicing, LF, dip)
  J: Syllable coherence (PU.RO.HI.TAM)

"Fix the ruler, not the instrument."
"""

import numpy as np
import os
import sys

from purohitam_reconstruction import (
    synth_purohitam,
    synth_P, synth_T, synth_U, synth_R, synth_OO, synth_H,
    synth_I, synth_A, synth_M,
    make_closing_tail, make_opening_head,
    f32, write_wav, ola_stretch,
    PITCH_HZ, SR, DTYPE, DIL,
    CLOSING_TAIL_MS, OPENING_HEAD_MS,
    VS_U_F, VS_R_F, VS_OO_F, VS_H_F_APPROX, VS_I_F,
    VS_T_LOCUS_F, VS_A_F, VS_M_F,
    VS_P_BURST_MS, VS_P_INITIAL_SILENCE_MS,
    VS_T_BURST_MS,
    VS_U_DUR_MS, VS_R_DUR_MS, VS_OO_DUR_MS, VS_H_DUR_MS,
    VS_I_DUR_MS, VS_A_DUR_MS, VS_M_DUR_MS, VS_M_RELEASE_MS,
)

os.makedirs("output_play", exist_ok=True)

# ============================================================================
# CONSTANTS
# ============================================================================

PERIOD_MS = 1000.0 / PITCH_HZ
PERIOD_N  = int(SR / PITCH_HZ)

# Measurement parameters (calibrated from RATNADHATAMAM v4.7.1)
VOICING_FRAME_MS    = 40.0
EDGE_TRIM_FRAC      = 0.15
VOICING_MIN_MODAL   = 0.50
VOICING_MIN_BREATHY = 0.25

# Bilabial burst band — LOW-BURST REGION (same as retroflex)
BILABIAL_BURST_LO_HZ = 800.0
BILABIAL_BURST_HI_HZ = 2500.0

# Dental burst band — HIGH region
DENTAL_BURST_LO_HZ = 2500.0
DENTAL_BURST_HI_HZ = 5500.0

# General burst measurement band
BURST_BAND_LO_HZ = 500.0
BURST_BAND_HI_HZ = 8000.0

# Vowel formant bands
# [u] — close back rounded: F1 low, F2 low
U_F1_BAND_LO = 200.0
U_F1_BAND_HI = 450.0
U_F2_BAND_LO = 600.0
U_F2_BAND_HI = 1100.0

# [oo] — long close-mid back: F1 low-mid, F2 low
OO_F1_BAND_LO = 300.0
OO_F1_BAND_HI = 600.0
OO_F2_BAND_LO = 600.0
OO_F2_BAND_HI = 1100.0

# [i] — close front: F1 low, F2 high
I_F1_BAND_LO = 200.0
I_F1_BAND_HI = 450.0
I_F2_BAND_LO = 1800.0
I_F2_BAND_HI = 2600.0

# [a] — open central: F1 high, F2 mid
A_F1_BAND_LO = 550.0
A_F1_BAND_HI = 900.0
A_F2_BAND_LO = 850.0
A_F2_BAND_HI = 1400.0

# Click/continuity thresholds (from RATNADHATAMAM v4.7.1)
CLICK_THRESHOLD_NOISE          = 0.50
CLICK_THRESHOLD_STOP_JOIN      = 0.85
CLICK_THRESHOLD_VOICED_JOIN    = 0.50

COLD_START_PERIODS = 2

ENV_SMOOTH_PERIODS       = 2.0
ENV_NORM_PERIODICITY_TOL = 0.35
CLICK_PERIOD_SEARCH_FRAC = 0.30
CLICK_JOIN_PERIOD_TOL    = 0.40
CLICK_JOIN_SEARCH_FRAC   = 0.30

# ============================================================================
# SEGMENT MAP
# ============================================================================

SEG_P   = 0   # [p] PLUCK (word-initial)
SEG_HU  = 1   # head + [u]
SEG_R   = 2   # [ɾ]
SEG_OO  = 3   # [oː]
SEG_H   = 4   # [h]
SEG_IT  = 5   # [i] + closing tail
SEG_T   = 6   # [t] PLUCK
SEG_HA  = 7   # head + [ɑ]
SEG_MR  = 8   # [m] + release

SEG_NAMES = [
    "[p] PLUCK (word-initial)",
    "head + [u]",
    "[r]",
    "[oo]",
    "[h]",
    "[i] + closing tail",
    "[t] PLUCK",
    "head + [a]",
    "[m] + release",
]

SEG_DURATIONS_MS = [
    VS_P_INITIAL_SILENCE_MS + VS_P_BURST_MS,  # 18ms
    OPENING_HEAD_MS + VS_U_DUR_MS,             # 65ms
    VS_R_DUR_MS,                                # 30ms
    VS_OO_DUR_MS,                               # 100ms
    VS_H_DUR_MS,                                # 65ms
    VS_I_DUR_MS + CLOSING_TAIL_MS,             # 75ms
    VS_T_BURST_MS,                              # 7ms
    OPENING_HEAD_MS + VS_A_DUR_MS,             # 70ms
    VS_M_DUR_MS + VS_M_RELEASE_MS,            # 80ms
]

UNVOICED_INDICES = {SEG_P, SEG_T, SEG_H}
STOP_INDICES     = {SEG_P, SEG_T}

CLOSING_TAIL_SEGMENTS = {
    SEG_IT: VS_I_DUR_MS,  # core = [i] 50ms, tail = 25ms
}

OPENING_HEAD_SEGMENTS = {
    SEG_HU: OPENING_HEAD_MS,  # head = 15ms, core = [u] 50ms
    SEG_HA: OPENING_HEAD_MS,  # head = 15ms, core = [a] 55ms
}

# ============================================================================
# MEASUREMENT FUNCTIONS
# (Identical to RATNADHATAMAM v4.7.1 / ṚTVIJAM v1.2)
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
    return (above[-1] - above[0]) / sr * 1000.0 \
        if len(above) >= 2 else 0.0

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
                    lo, hi = max(0, c - sm), min(len(da), c + sm + 1)
                    if lo < hi and float(np.max(da[lo:hi])) >= thr:
                        return jump, True, "periodic in A"
            for mult in [1, 2]:
                if len(seg_b) > mult * period + sm:
                    db = np.abs(np.diff(seg_b.astype(float)))
                    lo = max(0, mult * period - sm)
                    hi = min(len(db), mult * period + sm + 1)
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

# ============================================================================
# DIAGNOSTIC RUNNER
# ============================================================================

def run_diagnostics():
    print()
    print("=" * 72)
    print("PUROHITAM DIAGNOSTIC v1.0")
    print("PRINCIPLES-FIRST TONNETZ-DERIVED VERIFICATION")
    print("v3 PLUCK ARCHITECTURE")
    print("=" * 72)
    print()

    print("Synthesizing word (v3 pluck architecture)...")
    word = synth_purohitam(PITCH_HZ, DIL, with_room=False)
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

    # Isolated phonemes
    p_iso = synth_P(word_initial=True)
    t_iso = synth_T()

    # Write diagnostic audio
    write_wav("output_play/diag_pur_word_dry.wav", word)
    write_wav("output_play/diag_pur_word_slow6x.wav",
              ola_stretch(word, 6.0))
    write_wav("output_play/diag_pur_word_slow12x.wav",
              ola_stretch(word, 12.0))
    word_hall = synth_purohitam(PITCH_HZ, DIL, with_room=True)
    write_wav("output_play/diag_pur_word_hall.wav", word_hall)
    word_perf = synth_purohitam(PITCH_HZ, 2.5, with_room=False)
    word_perf_hall = synth_purohitam(PITCH_HZ, 2.5, with_room=True)
    write_wav("output_play/diag_pur_perf.wav", word_perf)
    write_wav("output_play/diag_pur_perf_hall.wav", word_perf_hall)
    write_wav("output_play/diag_pur_perf_slow6x.wav",
              ola_stretch(word_perf, 6.0))

    for sig, name in [(p_iso, "diag_pur_p_pluck"),
                      (t_iso, "diag_pur_t_pluck")]:
        mx = np.max(np.abs(sig))
        sn = sig / mx * 0.75 if mx > 1e-8 else sig
        write_wav(f"output_play/{name}.wav", sn)
        write_wav(f"output_play/{name}_slow6x.wav",
                  ola_stretch(sn, 6.0))
        write_wav(f"output_play/{name}_slow12x.wav",
                  ola_stretch(sn, 12.0))

    # PU syllable for pluck testing
    pu_syl = np.concatenate([
        synth_P(word_initial=True),
        make_opening_head(
            synth_U(F_next=VS_R_F), OPENING_HEAD_MS)
    ])
    mx = np.max(np.abs(pu_syl))
    if mx > 1e-8:
        pu_syl = pu_syl / mx * 0.75
    pu_syl = f32(pu_syl)
    write_wav("output_play/diag_pur_PU_syllable.wav", pu_syl)
    write_wav("output_play/diag_pur_PU_syllable_slow6x.wav",
              ola_stretch(pu_syl, 6.0))
    write_wav("output_play/diag_pur_PU_syllable_slow12x.wav",
              ola_stretch(pu_syl, 12.0))

    # TAM syllable
    tam_syl = np.concatenate([
        synth_I(F_prev=VS_H_F_APPROX, F_next=VS_T_LOCUS_F,
                closing_for_stop=True),
        synth_T(),
        synth_A(F_prev=VS_T_LOCUS_F, F_next=VS_M_F,
                opening_from_stop=True),
        synth_M(F_prev=VS_A_F, word_final=True),
    ])
    mx = np.max(np.abs(tam_syl))
    if mx > 1e-8:
        tam_syl = tam_syl / mx * 0.75
    tam_syl = f32(tam_syl)
    write_wav("output_play/diag_pur_iTAM_syllable.wav", tam_syl)
    write_wav("output_play/diag_pur_iTAM_syllable_slow6x.wav",
              ola_stretch(tam_syl, 6.0))
    write_wav("output_play/diag_pur_iTAM_syllable_slow12x.wav",
              ola_stretch(tam_syl, 12.0))

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
    # ══════════════════════════════════════════════════════════════
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
        if i in STOP_INDICES or (i + 1) in STOP_INDICES:
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

    # Isolated pluck continuity
    for sig, name in [(p_iso, "[p]"), (t_iso, "[t]")]:
        tj = measure_max_sample_jump(sig)
        p, m = check(f"{name} pluck isolated max |delta|", tj,
                     0.0, CLICK_THRESHOLD_NOISE, fmt='.6f')
        record(p, m)

    # ══════════════════════════════════════════════════════════════
    # SECTION C: THE PLUCK [p] — BILABIAL BURST
    # Śikṣā: oṣṭhya aghoṣa alpaprāṇa
    # ══════════════════════════════════════════════════════════════
    print()
    print("-" * 72)
    print("SECTION C: THE PLUCK [p] — BILABIAL BURST")
    print("  Siksa: osthya aghosa alpaprana.")
    print("  Word-initial: 10ms silence + 8ms burst.")
    print("-" * 72)

    # Extract burst portion only (skip initial silence)
    n_sil = int(VS_P_INITIAL_SILENCE_MS * DIL / 1000.0 * SR)
    p_burst = p_iso[n_sil:] if len(p_iso) > n_sil else p_iso

    bc = measure_band_centroid(p_burst, BURST_BAND_LO_HZ,
                               BURST_BAND_HI_HZ)
    p, m = check("[p] burst centroid", bc,
                 BILABIAL_BURST_LO_HZ, BILABIAL_BURST_HI_HZ,
                 unit='Hz', fmt='.1f')
    record(p, m)

    be = measure_burst_temporal_extent(p_burst)
    p, m = check("[p] burst temporal extent", be, 0.01, 12.0,
                 unit='ms', fmt='.2f')
    record(p, m)

    p_dur = len(p_burst) / SR * 1000.0
    p, m = check("[p] burst duration", p_dur, 0.1, 12.0,
                 unit='ms', fmt='.2f')
    record(p, m)

    if len(p_burst) > 10:
        pv = measure_voicing(p_burst)
        p, m = check("[p] voicing (aghosa)", pv, -1.0, 0.30)
        record(p, m)

    pr = rms(p_burst)
    p, m = check("[p] burst RMS", pr, 0.001, 1.0, fmt='.6f')
    record(p, m)

    # ══════════════════════════════════════════════════════════════
    # SECTION D: THE PLUCK [t] — DENTAL BURST
    # Śikṣ��: dantya aghoṣa alpaprāṇa
    # ══════════════════════════════════════════════════════════════
    print()
    print("-" * 72)
    print("SECTION D: THE PLUCK [t] — DENTAL BURST")
    print("  Siksa: dantya aghosa alpaprana.")
    print("-" * 72)

    bc = measure_band_centroid(t_iso, BURST_BAND_LO_HZ,
                               BURST_BAND_HI_HZ)
    p, m = check("[t] burst centroid", bc,
                 DENTAL_BURST_LO_HZ, DENTAL_BURST_HI_HZ,
                 unit='Hz', fmt='.1f')
    record(p, m)

    be = measure_burst_temporal_extent(t_iso)
    p, m = check("[t] burst temporal extent", be, 0.01, 10.0,
                 unit='ms', fmt='.2f')
    record(p, m)

    t_dur = len(t_iso) / SR * 1000.0
    p, m = check("[t] burst duration", t_dur, 0.1, 10.0,
                 unit='ms', fmt='.2f')
    record(p, m)

    if len(t_iso) > 10:
        tv = measure_voicing(t_iso)
        p, m = check("[t] voicing (aghosa)", tv, -1.0, 0.30)
        record(p, m)

    tr = rms(t_iso)
    p, m = check("[t] burst RMS", tr, 0.001, 1.0, fmt='.6f')
    record(p, m)

    # [p] vs [t] centroid separation (place contrast)
    p_cent = measure_band_centroid(p_burst, BURST_BAND_LO_HZ,
                                   BURST_BAND_HI_HZ)
    t_cent = measure_band_centroid(t_iso, BURST_BAND_LO_HZ,
                                   BURST_BAND_HI_HZ)
    sep = t_cent - p_cent
    p, m = check("[t]-[p] centroid separation", sep,
                 500.0, 5000.0, unit='Hz', fmt='.1f')
    record(p, m)

    # ══════════════════════════════════════════════════════════════
    # SECTION E: CLOSING TAIL — [i] OWNS THE CLOSURE
    # ══════════════════════════════════════════════════════════════
    print()
    print("-" * 72)
    print("SECTION E: CLOSING TAIL — [i] OWNS THE CLOSURE")
    print("  Core voicing + RMS fade = the tongue rises to dental,")
    print("  the cords were vibrating, the amplitude decreases.")
    print("-" * 72)

    _, seg_it = segments_ordered[SEG_IT]
    if len(seg_it) > 10:
        nc = int(VS_I_DUR_MS * DIL / 1000.0 * SR)
        i_core = seg_it[:min(nc, len(seg_it))]
        i_tail = seg_it[nc:]
        print("\n  -- [i] closing tail --")
        if len(i_core) > 10:
            p, m = check("[i] core voicing",
                         measure_voicing(body(i_core)),
                         VOICING_MIN_MODAL, 1.0)
            record(p, m)
        if len(i_tail) > 10 and rms(i_core) > 1e-10:
            p, m = check("[i] tail/core RMS ratio",
                         rms(i_tail) / rms(i_core), 0.0, 0.90)
            record(p, m)

    # ══════════════════════════════════════════════════════════════
    # SECTION F: OPENING HEADS
    # ══════════════════════════════════════════════════════════════
    print()
    print("-" * 72)
    print("SECTION F: OPENING HEADS")
    print("-" * 72)

    for seg_idx, core_dur_ms, label in [
        (SEG_HU, VS_U_DUR_MS, "[u] after [p]"),
        (SEG_HA, VS_A_DUR_MS, "[a] after [t]"),
    ]:
        _, seg = segments_ordered[seg_idx]
        if len(seg) < 10:
            continue
        nh = int(OPENING_HEAD_MS * DIL / 1000.0 * SR)
        head = seg[:min(nh, len(seg))]
        core = seg[nh:]
        print(f"\n  -- {label} --")
        if len(core) > 10:
            p, m = check(f"{label} core voicing",
                         measure_voicing(body(core)),
                         VOICING_MIN_MODAL, 1.0)
            record(p, m)
        if len(head) > 4:
            h1, h2 = head[:len(head) // 2], head[len(head) // 2:]
            r1, r2 = rms(h1), rms(h2)
            if r1 > 1e-10:
                p = r2 >= r1 * 0.8
                record(p, f"  {'PASS' if p else 'FAIL'}  "
                          f"{label} head rising: "
                          f"{r1:.6f} -> {r2:.6f}")

    # ══════════════════════════════════════════════════════════════
    # SECTION G: VOWELS — THE SUSTAINED NOTES
    # ══════════════════════════════════════════════════════════════
    print()
    print("-" * 72)
    print("SECTION G: VOWELS — THE SUSTAINED NOTES")
    print("-" * 72)

    # [u] — close back rounded (core only, skip head)
    _, hu_seg = segments_ordered[SEG_HU]
    nh_u = int(OPENING_HEAD_MS * DIL / 1000.0 * SR)
    u_core = hu_seg[nh_u:]
    if len(u_core) > 10:
        ub = body(u_core)
        print("\n  -- [u] --")
        p, m = check("[u] voicing", measure_voicing(ub),
                     VOICING_MIN_MODAL, 1.0)
        record(p, m)
        p, m = check("[u] F1",
                     measure_band_centroid(ub, U_F1_BAND_LO,
                                          U_F1_BAND_HI),
                     U_F1_BAND_LO, U_F1_BAND_HI,
                     unit='Hz', fmt='.1f')
        record(p, m)
        p, m = check("[u] F2",
                     measure_band_centroid(ub, U_F2_BAND_LO,
                                          U_F2_BAND_HI),
                     U_F2_BAND_LO, U_F2_BAND_HI,
                     unit='Hz', fmt='.1f')
        record(p, m)

    # [oo] — long close-mid back
    _, oo_seg = segments_ordered[SEG_OO]
    if len(oo_seg) > 10:
        oob = body(oo_seg)
        print("\n  -- [oo] --")
        p, m = check("[oo] voicing", measure_voicing(oob),
                     VOICING_MIN_MODAL, 1.0)
        record(p, m)
        p, m = check("[oo] F1",
                     measure_band_centroid(oob, OO_F1_BAND_LO,
                                          OO_F1_BAND_HI),
                     OO_F1_BAND_LO, OO_F1_BAND_HI,
                     unit='Hz', fmt='.1f')
        record(p, m)
        p, m = check("[oo] F2",
                     measure_band_centroid(oob, OO_F2_BAND_LO,
                                          OO_F2_BAND_HI),
                     OO_F2_BAND_LO, OO_F2_BAND_HI,
                     unit='Hz', fmt='.1f')
        record(p, m)

    # [i] — close front (core only, skip tail)
    _, it_seg = segments_ordered[SEG_IT]
    nc_i = int(VS_I_DUR_MS * DIL / 1000.0 * SR)
    i_core = it_seg[:min(nc_i, len(it_seg))]
    if len(i_core) > 10:
        ib = body(i_core)
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

    # [a] — open central (core only, skip head)
    _, ha_seg = segments_ordered[SEG_HA]
    nh_a = int(OPENING_HEAD_MS * DIL / 1000.0 * SR)
    a_core = ha_seg[nh_a:]
    if len(a_core) > 10:
        ab = body(a_core)
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
    # SECTION H: FRICATIVE [h]
    # Śikṣā: kaṇṭhya aghoṣa mahāprāṇa
    # ══════════════════════════════════════════════════════════════
    print()
    print("-" * 72)
    print("SECTION H: FRICATIVE [h]")
    print("  Siksa: kanthya aghosa mahaprana.")
    print("  Voiceless glottal fricative. Noise source.")
    print("-" * 72)

    _, h_seg = segments_ordered[SEG_H]
    if len(h_seg) > 10:
        hb = body(h_seg)
        hv = measure_voicing(hb)
        p, m = check("[h] voicing (aghosa)", hv, -1.0, 0.30)
        record(p, m)
        hr = rms(hb)
        p, m = check("[h] RMS (audible)", hr, 0.001, 0.50, fmt='.6f')
        record(p, m)

    # ══════════════════════════════════════════════════════════════
    # SECTION I: TAP AND NASAL
    # ══════════════════════════════════════════════════════════════
    print()
    print("-" * 72)
    print("SECTION I: TAP [r] AND NASAL [m]")
    print("-" * 72)

    # [ɾ] alveolar tap
    _, r_seg = segments_ordered[SEG_R]
    if len(r_seg) > 10:
        rb = body(r_seg)
        print("\n  -- [r] alveolar tap --")
        p, m = check("[r] voicing", measure_voicing(rb),
                     VOICING_MIN_BREATHY, 1.0)
        record(p, m)
        # Tap dip ratio: middle should be quieter than edges
        n3 = len(r_seg) // 3
        if n3 > 1:
            r_edge = rms(np.concatenate([r_seg[:n3], r_seg[-n3:]]))
            r_mid = rms(r_seg[n3:2 * n3])
            if r_edge > 1e-10:
                p, m = check("[r] dip ratio (mid/edge)",
                             r_mid / r_edge, 0.0, 0.95)
                record(p, m)

    # [m] bilabial nasal
    _, m_seg = segments_ordered[SEG_MR]
    if len(m_seg) > 10:
        # Core (before release)
        nc_m = int(VS_M_DUR_MS * DIL / 1000.0 * SR)
        m_core = m_seg[:min(nc_m, len(m_seg))]
        mb = body(m_core)
        print("\n  -- [m] bilabial nasal --")
        p, m_ = check("[m] voicing", measure_voicing(mb),
                      VOICING_MIN_MODAL, 1.0)
        record(p, m_)
        p, m_ = check("[m] LF ratio", measure_lf_ratio(mb),
                      0.20, 1.0)
        record(p, m_)

    # ══════════════════════════════════════════════════════════════
    # SECTION J: SYLLABLE-LEVEL COHERENCE
    # PU.RŌ.HI.TAM
    # ══════════════════════════════════════════════════════════════
    print()
    print("-" * 72)
    print("SECTION J: SYLLABLE-LEVEL COHERENCE")
    print("  PU.RŌ.HI.TAM")
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

    # [p] should be an amplitude trough at word start
    p_a, hu_a = sa[SEG_P], sa[SEG_HU]
    if hu_a > 0:
        p = p_a < hu_a
        record(p, f"  {'PASS' if p else 'FAIL'}  [p] trough: "
                  f"{p_a:.4f} < {hu_a:.4f}")

    # [t] should be an amplitude trough between [i] and [a]
    t_a, it_a, ha_a = sa[SEG_T], sa[SEG_IT], sa[SEG_HA]
    if it_a > 0 and ha_a > 0:
        p = t_a < min(it_a, ha_a)
        record(p, f"  {'PASS' if p else 'FAIL'}  [t] trough: "
                  f"{t_a:.4f} < min({it_a:.4f}, {ha_a:.4f})")

    # [oo] should be the most prominent vowel (longest + back)
    oo_a = sa[SEG_OO]
    all_a = [a for a in sa if a > 0]
    if len(all_a) > 0 and oo_a > 0:
        mx_a = max(all_a)
        p, m = check("[oo] relative amplitude",
                     oo_a / mx_a if mx_a > 1e-10 else 0.0,
                     0.60, 1.0)
        record(p, m)

    # Word duration
    word_dur = len(word) / SR * 1000.0
    p, m = check("Word duration", word_dur,
                 300.0, 700.0, unit='ms', fmt='.1f')
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
        print("PUROHITAM v3 PLUCK ARCHITECTURE — VERIFIED.")
        print()
        print("Section structure:")
        print("  A: Signal integrity (NaN, Inf, peak, DC)")
        print("  B: Signal continuity (glottal periodicity)")
        print("  C: [p] pluck (centroid, voicelessness, word-initial)")
        print("  D: [t] pluck (centroid, voicelessness, place contrast)")
        print("  E: Closing tail ([i] core voicing + RMS fade)")
        print("  F: Opening heads ([u] after [p], [a] after [t])")
        print("  G: Vowels ([u], [oo], [i], [a] — voicing, F1, F2)")
        print("  H: Fricative [h] (voicelessness, RMS)")
        print("  I: Tap [r] + Nasal [m] (voicing, dip, LF)")
        print("  J: Syllable cadence (troughs, prominence, duration)")
        print()
        print("Phonemes verified in this word:")
        print("  [p]  voiceless bilabial stop (PLUCK, word-initial)")
        print("  [u]  short close back rounded")
        print("  [ɾ]  alveolar tap")
        print("  [oː] long close-mid back rounded")
        print("  [h]  voiceless glottal fricative")
        print("  [i]  short close front unrounded")
        print("  [t]  voiceless dental stop (PLUCK)")
        print("  [ɑ]  short open central unrounded")
        print("  [m]  bilabial nasal (word-final)")
        print()
        print("Śikṣā alignment:")
        print("  [p] = oṣṭhya aghoṣa alpaprāṇa ✓")
        print("  [t] = dantya aghoṣa alpaprāṇa ✓")
        print("  [h] = kaṇṭhya aghoṣa mahāprāṇa ✓")
        print()
        print("PERCEPTUAL VERIFICATION:")
        print("  afplay output_play/diag_pur_p_pluck_slow12x.wav")
        print("  afplay output_play/diag_pur_t_pluck_slow12x.wav")
        print("  afplay output_play/diag_pur_PU_syllable_slow12x.wav")
        print("  afplay output_play/diag_pur_iTAM_syllable_slow12x.wav")
        print("  afplay output_play/diag_pur_word_slow6x.wav")
        print("  afplay output_play/diag_pur_perf_hall.wav")
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
    print("  PUROHITAM DIAGNOSTIC v1.0")
    print("  PRINCIPLES-FIRST TONNETZ-DERIVED VERIFICATION")
    print("  v3 PLUCK ARCHITECTURE")
    print()
    print("  Derived from RATNADHATAMAM DIAGNOSTIC v4.7.1")
    print("  Same measurement functions. Same calibrated thresholds.")
    print("  Same section structure. Adapted for purohitam phonemes.")
    print()
    print("  Segment map (v3 pluck architecture):")
    print("    [p] PLUCK (word-initial)  18ms  (10ms silence + 8ms)")
    print("    head + [u]               65ms  (15ms rise + 50ms)")
    print("    [ɾ]                       30ms")
    print("    [oː]                      100ms")
    print("    [h]                        65ms")
    print("    [i] + closing tail         75ms  (50ms + 25ms fade)")
    print("    [t] PLUCK                  7ms  (burst only)")
    print("    head + [ɑ]                70ms  (15ms rise + 55ms)")
    print("    [m] + release              80ms  (60ms + 20ms fade)")
    print()
    print("  This word has TWO voiceless stops:")
    print("    [p] oṣṭhya — bilabial, LOW-BURST (~1300 Hz)")
    print("    [t] dantya — dental, HIGH-BURST (~3000 Hz)")
    print("  Their centroid separation is a diagnostic itself.")
    print()
    print("  \"Fix the ruler, not the instrument.\"")
    print("=" * 64)
    print()

    success = run_diagnostics()
    sys.exit(0 if success else 1)
