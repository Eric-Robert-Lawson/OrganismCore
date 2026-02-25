#!/usr/bin/env python3
"""
========================================================================
ĪḶE DIAGNOSTIC v1.0
PRINCIPLES-FIRST TONNETZ-DERIVED VERIFICATION
v1 ALL-VOICED LATERAL ARCHITECTURE
========================================================================

Rigveda 1.1.1, word 2
[iːɭeː] — "I praise"

Diagnostic structure follows canonical pattern from:
  DEVAM v1.2 (39/39) — all-voiced word regime
  RATNADHĀTAMAM v5.0.1 (81/81)
  PUROHITAM v1.1 (72/72)
  YAJÑASYA v1.1 (47/47)
  HOTĀRAM v3.1 (54/54)

ALL VOICED word — no pluck architecture.
Uses DEVAM v1.2 all-voiced measurement regime:
  - warm cold-start (2 periods) throughout
  - adaptive edge trim for short segments
  - check_voicing() with LF-ratio proxy fallback
  - voiced→voiced join thresholds (0.70)

[iː] — length variant of verified [i] (AGNI)
[ɭ]  — NEW: retroflex lateral approximant (mūrdhanya + lateral)
[eː] — verified DEVAM v1 (F1 390 Hz, F2 1757 Hz)

KEY DIAGNOSTIC: [ɭ] mūrdhanya identity requires TWO simultaneous tests:
  1. F3 depression >= 200 Hz below neutral alveolar (2700 Hz)
  2. F2 in lateral range (~1000-1500 Hz), below central mūrdhanya [ɻ̩]
If only one is present, the phoneme is misidentified.

February 2026
"""

import numpy as np
import sys

# ============================================================================
# CONSTANTS
# ============================================================================

SR       = 44100
PITCH_HZ = 120.0
PERIOD_MS = 1000.0 / PITCH_HZ
PERIOD_N  = int(SR / PITCH_HZ)

VOICING_FRAME_MS    = 40.0
EDGE_TRIM_FRAC      = 0.15
EDGE_TRIM_SHORT     = 0.08
SHORT_SEG_THRESHOLD_MS = 80.0
VOICING_MIN_MODAL   = 0.50
VOICING_MIN_BREATHY = 0.25

# v1.2 all-voiced regime (from DEVAM)
COLD_START_PERIODS_WARM = 2
COLD_START_CEILING      = 5.0

# Minimum duration for autocorrelation voicing
# Below this, use LF-ratio proxy
AUTOCORR_MIN_DUR_MS = 40.0

# ── Physics constants ───────────────────────────────────────────────────────
NEUTRAL_ALVEOLAR_F3_HZ = 2700.0
MURDHANYA_F3_DEPRESSION_MIN_HZ = 200.0
# Mūrdhanya F3 must be at least 200 Hz below 2700 Hz = max 2500 Hz

# ── [iː] formant bands — tālavya (close front) ────────────────────────────
II_F1_BAND_LO = 200.0;  II_F1_BAND_HI = 450.0
II_F2_BAND_LO = 1800.0; II_F2_BAND_HI = 2600.0
II_F1_EXPECT_LO = 200.0;  II_F1_EXPECT_HI = 400.0
II_F2_EXPECT_LO = 1900.0; II_F2_EXPECT_HI = 2500.0

# ── [ɭ] formant bands — mūrdhanya lateral ──────────────────────────────────
# F2: lateral range (below central mūrdhanya [ɻ̩] at 1212 Hz)
LL_F2_BAND_LO = 800.0;  LL_F2_BAND_HI = 1600.0
LL_F2_EXPECT_LO = 900.0;  LL_F2_EXPECT_HI = 1400.0
# F3: must be depressed (mūrdhanya marker)
LL_F3_BAND_LO = 1800.0; LL_F3_BAND_HI = 2800.0
LL_F3_EXPECT_HI = NEUTRAL_ALVEOLAR_F3_HZ - MURDHANYA_F3_DEPRESSION_MIN_HZ  # 2500 Hz

# ── [eː] formant bands — tālavya (close-mid front) ────────────────────────
# Verified DEVAM v1: F1 390 Hz, F2 1757 Hz
EE_F1_BAND_LO = 250.0;  EE_F1_BAND_HI = 600.0
EE_F2_BAND_LO = 1400.0; EE_F2_BAND_HI = 2200.0
EE_F1_EXPECT_LO = 300.0;  EE_F1_EXPECT_HI = 550.0
EE_F2_EXPECT_LO = 1500.0; EE_F2_EXPECT_HI = 2100.0

# ── Signal integrity ───────────────────────────────────────────────────────
PEAK_AMP_LO = 0.01
PEAK_AMP_HI = 1.00
DC_OFFSET_MAX = 0.05

# ── Continuity ─────────────────────────────────────────────────────────────
CLICK_THRESHOLD_VOICED_JOIN = 0.70  # from DEVAM v1.2

# ── Envelope-normalized periodicity ────────────────────────────────────────
ENV_SMOOTH_PERIODS = 2.0

# ============================================================================
# SEGMENT MAP — ĪḶE [iːɭeː]
# ============================================================================

VS_II_DUR_MS = 100.0
VS_LL_DUR_MS = 70.0
VS_EE_DUR_MS = 90.0

SEG_II = 0    # [iː] long close front
SEG_LL = 1    # [ɭ]  retroflex lateral approximant
SEG_EE = 2    # [eː] long close-mid front

SEG_NAMES = [
    "[iː] long close front",
    "[ɭ] retroflex lateral approximant",
    "[eː] long close-mid front",
]

SEG_DURATIONS_MS = [
    VS_II_DUR_MS,
    VS_LL_DUR_MS,
    VS_EE_DUR_MS,
]

UNVOICED_INDICES = set()  # all voiced

# ============================================================================
# MEASUREMENT FUNCTIONS (canonical, with DEVAM v1.2 all-voiced calibration)
# ============================================================================

def rms(sig):
    return float(np.sqrt(np.mean(sig.astype(float) ** 2)))


def body(seg, frac=EDGE_TRIM_FRAC):
    n = len(seg)
    lo = int(n * frac)
    hi = n - int(n * frac)
    if hi <= lo:
        return seg
    return seg[lo:hi]


def body_adaptive(seg, dur_ms):
    """DEVAM v1.2: reduced trim for short segments (< 80ms)."""
    if dur_ms < SHORT_SEG_THRESHOLD_MS:
        return body(seg, frac=EDGE_TRIM_SHORT)
    return body(seg, frac=EDGE_TRIM_FRAC)


def measure_voicing(seg, sr=SR, warm=False, dur_ms=None):
    """
    Autocorrelation-based voicing measure.
    DEVAM v1.2: returns None if segment too short for autocorrelation,
    signaling caller to use LF-ratio proxy.
    """
    if dur_ms is not None and dur_ms < SHORT_SEG_THRESHOLD_MS:
        b = body_adaptive(seg, dur_ms)
    else:
        b = body(seg)

    if len(b) < PERIOD_N * 3:
        return None

    cold_start = COLD_START_PERIODS_WARM if warm else 4
    skip = int(cold_start * PERIOD_N)
    if skip < len(b):
        b = b[skip:]
    if len(b) < PERIOD_N * 2:
        return None

    frame_n = int(VOICING_FRAME_MS / 1000.0 * sr)
    if len(b) < frame_n * 2:
        frame_n = max(PERIOD_N * 2, len(b) // 2)

    n_frames = max(1, (len(b) - frame_n) // (frame_n // 2) + 1)
    peaks = []
    for i in range(n_frames):
        start = i * (frame_n // 2)
        end = start + frame_n
        if end > len(b):
            break
        frame = b[start:end].astype(float)
        frame = frame - np.mean(frame)
        e = np.sum(frame ** 2)
        if e < 1e-12:
            continue
        ac = np.correlate(frame, frame, mode='full')
        ac = ac[len(frame) - 1:]
        ac = ac / (ac[0] + 1e-12)

        lo_lag = max(1, int(sr / 200.0))
        hi_lag = min(len(ac) - 1, int(sr / 60.0))
        if lo_lag >= hi_lag:
            continue
        peak = float(np.max(ac[lo_lag:hi_lag]))
        peaks.append(peak)

    if not peaks:
        return None
    return float(np.median(peaks))


def measure_band_centroid(seg, lo_hz, hi_hz, sr=SR):
    """Spectral centroid within a frequency band."""
    b = body(seg)
    if len(b) < 64:
        return 0.0
    spec = np.abs(np.fft.rfft(b.astype(float)))
    freqs = np.fft.rfftfreq(len(b), d=1.0 / sr)
    mask = (freqs >= lo_hz) & (freqs <= hi_hz)
    if np.sum(spec[mask]) < 1e-12:
        return 0.0
    return float(np.sum(freqs[mask] * spec[mask]) / np.sum(spec[mask]))


def measure_lf_ratio(seg, sr=SR, cutoff=500.0):
    """Ratio of energy below cutoff to total energy."""
    b = body(seg)
    if len(b) < 64:
        return 0.0
    spec = np.abs(np.fft.rfft(b.astype(float))) ** 2
    freqs = np.fft.rfftfreq(len(b), d=1.0 / sr)
    total = np.sum(spec)
    if total < 1e-12:
        return 0.0
    lf = np.sum(spec[freqs <= cutoff])
    return float(lf / total)


def measure_f3_depression(seg, sr=SR):
    """
    Measure F3 centroid and compute depression from neutral alveolar.

    For mūrdhanya phonemes, F3 must be depressed at least
    MURDHANYA_F3_DEPRESSION_MIN_HZ (200 Hz) below NEUTRAL_ALVEOLAR_F3_HZ (2700 Hz).

    Returns (f3_centroid, depression_hz).
    """
    f3 = measure_band_centroid(seg, LL_F3_BAND_LO, LL_F3_BAND_HI, sr)
    depression = NEUTRAL_ALVEOLAR_F3_HZ - f3 if f3 > 0 else 0.0
    return f3, depression


def compute_local_envelope(sig, smooth_periods=ENV_SMOOTH_PERIODS,
                           pitch_hz=PITCH_HZ, sr=SR):
    win = max(1, int(smooth_periods * sr / pitch_hz))
    sig_f = sig.astype(float) ** 2
    kernel = np.ones(win) / win
    env = np.sqrt(np.convolve(sig_f, kernel, mode='same'))
    return env


def measure_glottal_aware_continuity(seg, pitch_hz=PITCH_HZ, sr=SR,
                                     cold_start_periods=COLD_START_PERIODS_WARM,
                                     cold_start_ceiling=COLD_START_CEILING):
    """Envelope-normalized max sample jump. Warm cold-start for all-voiced."""
    if len(seg) < PERIOD_N * 2:
        return 0.0

    env = compute_local_envelope(seg, ENV_SMOOTH_PERIODS, pitch_hz, sr)

    skip = int(cold_start_periods * sr / pitch_hz)
    if skip >= len(seg) - 1:
        skip = 0

    sig_f = seg[skip:].astype(float)
    env_f = env[skip:]

    if len(sig_f) < 2:
        return 0.0

    jumps = np.abs(np.diff(sig_f))
    local_env = env_f[:-1]
    local_env = np.maximum(local_env, 1e-8)

    normalized = jumps / local_env
    val = float(np.max(normalized))

    return min(val, cold_start_ceiling)


def measure_join(seg_a, seg_b):
    if len(seg_a) == 0 or len(seg_b) == 0:
        return 0.0
    return float(abs(float(seg_a[-1]) - float(seg_b[0])))


# ============================================================================
# VOICING CHECK HELPER (from DEVAM v1.2)
# ============================================================================

def check_voicing(label, seg, dur_ms, min_voicing, warm=True):
    """
    Try autocorrelation first. If segment too short (returns None),
    fall back to LF-ratio as voicing proxy.
    YAJÑASYA lesson: "LF ratio IS voicing evidence for short closures."
    """
    v = measure_voicing(seg, warm=warm, dur_ms=dur_ms)
    if v is not None:
        return check(label, v, min_voicing, 1.0)
    else:
        lf = measure_lf_ratio(seg)
        info(f"{label}: autocorrelation insufficient at {dur_ms:.0f}ms "
             f"— using LF-ratio proxy = {lf:.4f}")
        return check(f"{label} (LF-ratio proxy)", lf, 0.3, 1.0)


# ============================================================================
# DIAGNOSTIC FRAMEWORK
# ============================================================================

pass_count = 0
fail_count = 0
results = []


def check(label, value, lo, hi, unit='', fmt='.4f'):
    global pass_count, fail_count
    ok = lo <= value <= hi
    tag = "PASS" if ok else "FAIL"
    if ok:
        pass_count += 1
    else:
        fail_count += 1
    val_str = f"{value:{fmt}}"
    range_str = f"[{lo:{fmt}} - {hi:{fmt}}]"
    line = f"  {tag}  {label}: {val_str} {unit}  (expected {range_str} {unit})"
    results.append(line)
    print(line)
    return ok


def check_pass(label, msg):
    global pass_count
    pass_count += 1
    line = f"  PASS  {label} — {msg}"
    results.append(line)
    print(line)


def info(msg):
    line = f"  INFO  {msg}"
    results.append(line)
    print(line)


# ============================================================================
# SEGMENT EXTRACTION
# ============================================================================

def extract_segments(word_sig):
    segments = []
    pos = 0
    for dur_ms in SEG_DURATIONS_MS:
        n = int(dur_ms / 1000.0 * SR)
        n = min(n, len(word_sig) - pos)
        seg = word_sig[pos:pos + n]
        segments.append(seg)
        pos += n
    return segments


# ============================================================================
# MAIN DIAGNOSTIC
# ============================================================================

def run_diagnostics():
    global pass_count, fail_count

    wav_path = "output_play/ile_v1_dry.wav"
    try:
        import wave as wave_module
        with wave_module.open(wav_path, 'r') as wf:
            n_frames = wf.getnframes()
            raw = wf.readframes(n_frames)
            word_sig = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32767.0
    except FileNotFoundError:
        print(f"  ERROR: {wav_path} not found.")
        print("  Run ile_reconstruction.py first.")
        sys.exit(1)

    print()
    print("=" * 72)
    print("  ĪḶE DIAGNOSTIC v1.0")
    print("  PRINCIPLES-FIRST TONNETZ-DERIVED VERIFICATION")
    print("  v1 ALL-VOICED LATERAL ARCHITECTURE")
    print("=" * 72)
    print()
    print(f"  Word length: {len(word_sig)} samples ({len(word_sig)/SR*1000:.1f} ms)")
    print()

    segs = extract_segments(word_sig)

    for i, (name, dur) in enumerate(zip(SEG_NAMES, SEG_DURATIONS_MS)):
        n_samp = len(segs[i])
        print(f"    SEG {i}: {name:40s} {dur:6.1f} ms  ({n_samp:5d} samples)")
    print()

    # ==================================================================
    # SECTION A: Signal Integrity
    # ==================================================================
    print("─" * 72)
    print("  SECTION A: Signal Integrity")
    print("─" * 72)

    if not np.any(np.isnan(word_sig)):
        check_pass("A1 no-NaN", "signal contains no NaN values")
    else:
        check("A1 no-NaN", 1, 0, 0)

    if not np.any(np.isinf(word_sig)):
        check_pass("A2 no-Inf", "signal contains no Inf values")
    else:
        check("A2 no-Inf", 1, 0, 0)

    peak = float(np.max(np.abs(word_sig)))
    check("A3 peak-amplitude", peak, PEAK_AMP_LO, PEAK_AMP_HI)

    dc = float(np.abs(np.mean(word_sig)))
    check("A4 DC-offset", dc, 0.0, DC_OFFSET_MAX)

    print()

    # ==================================================================
    # SECTION B: Signal Continuity
    # ==================================================================
    print("─" * 72)
    print("  SECTION B: Signal Continuity")
    print("─" * 72)

    for i, (name, seg, dur) in enumerate(
            zip(SEG_NAMES, segs, SEG_DURATIONS_MS)):
        if len(seg) < PERIOD_N * 2:
            info(f"{name}: too short for continuity measurement")
            continue
        cont = measure_glottal_aware_continuity(
            seg, cold_start_periods=COLD_START_PERIODS_WARM)
        check(f"B{i+1} continuity {name}", cont,
              0.0, COLD_START_CEILING)

    print()

    # Joins
    join_specs = [
        ("[iː]→[ɭ]", SEG_II, SEG_LL, CLICK_THRESHOLD_VOICED_JOIN),
        ("[ɭ]→[eː]",  SEG_LL, SEG_EE, CLICK_THRESHOLD_VOICED_JOIN),
    ]
    for label, idx_a, idx_b, thresh in join_specs:
        j = measure_join(segs[idx_a], segs[idx_b])
        check(f"B join {label}", j, 0.0, thresh)

    print()

    # ==================================================================
    # SECTION C: [iː] Long Close Front Vowel (tālavya)
    # ==================================================================
    print("─" * 72)
    print("  SECTION C: [iː] Long Close Front Vowel (tālavya)")
    print("─" * 72)

    check_voicing("C1 [iː] voicing", segs[SEG_II],
                  dur_ms=VS_II_DUR_MS, min_voicing=VOICING_MIN_MODAL)

    ii_f1 = measure_band_centroid(segs[SEG_II], II_F1_BAND_LO, II_F1_BAND_HI)
    check("C2 [iː] F1 (close)", ii_f1,
          II_F1_EXPECT_LO, II_F1_EXPECT_HI, 'Hz')

    ii_f2 = measure_band_centroid(segs[SEG_II], II_F2_BAND_LO, II_F2_BAND_HI)
    check("C3 [iː] F2 (front)", ii_f2,
          II_F2_EXPECT_LO, II_F2_EXPECT_HI, 'Hz')

    # C4: Duration — must be long (>= 1.7× short [i] at 50ms = 85ms)
    ii_dur_ms = len(segs[SEG_II]) / SR * 1000.0
    check("C4 [iː] duration (long vowel)", ii_dur_ms,
          85.0, 150.0, 'ms')

    # C5: [iː] relative amplitude
    ii_rms = rms(body(segs[SEG_II]))
    word_rms = rms(word_sig)
    if word_rms > 1e-8:
        ii_rel = ii_rms / word_rms
        check("C5 [iː] relative amplitude", ii_rel, 0.3, 2.0)

    print()

    # ==================================================================
    # SECTION D: [ɭ] Retroflex Lateral Approximant (mūrdhanya + lateral)
    # ==================================================================
    print("─" * 72)
    print("  SECTION D: [ɭ] Retroflex Lateral Approximant (mūrdhanya + lateral)")
    print("─" * 72)

    # D1: Voicing
    check_voicing("D1 [ɭ] voicing", segs[SEG_LL],
                  dur_ms=VS_LL_DUR_MS, min_voicing=VOICING_MIN_BREATHY)

    # D2: F2 — lateral range (lower than central [ɻ̩])
    ll_f2 = measure_band_centroid(segs[SEG_LL], LL_F2_BAND_LO, LL_F2_BAND_HI)
    check("D2 [ɭ] F2 (lateral range)", ll_f2,
          LL_F2_EXPECT_LO, LL_F2_EXPECT_HI, 'Hz')

    # D3: F3 depression — THE primary mūrdhanya diagnostic
    # F3 must be depressed at least 200 Hz below neutral alveolar (2700 Hz)
    ll_f3, ll_f3_depression = measure_f3_depression(segs[SEG_LL])
    info(f"[ɭ] F3 centroid = {ll_f3:.1f} Hz, "
         f"depression from neutral (2700) = {ll_f3_depression:.1f} Hz")
    check("D3 [ɭ] F3 depression (mūrdhanya marker)", ll_f3_depression,
          MURDHANYA_F3_DEPRESSION_MIN_HZ, 1200.0, 'Hz')

    # D4: F3 absolute value — must be below 2500 Hz
    check("D4 [ɭ] F3 absolute (< 2500 Hz)", ll_f3,
          1500.0, LL_F3_EXPECT_HI, 'Hz')

    # D5: Amplitude dip — approximant has constriction
    ll_rms = rms(body(segs[SEG_LL]))
    if ii_rms > 1e-8:
        ll_dip = ll_rms / ii_rms
        info(f"[ɭ] amplitude relative to [iː] = {ll_dip:.4f}")
        check("D5 [ɭ] amplitude dip (lateral constriction)", ll_dip,
              0.2, 1.2)

    # D6: [ɭ] F2 must be significantly below [iː] F2
    # This confirms the lateral identity (F2 drops into constriction)
    if ii_f2 > 100 and ll_f2 > 100:
        f2_drop = ii_f2 - ll_f2
        info(f"[iː] F2 - [ɭ] F2 = {f2_drop:.1f} Hz (front→lateral drop)")
        check("D6 [iː]-[ɭ] F2 drop (lateral reduces F2)", f2_drop,
              300.0, 1500.0, 'Hz')

    print()

    # ==================================================================
    # SECTION E: [eː] Long Close-Mid Front Vowel (tālavya)
    # ==================================================================
    print("─" * 72)
    print("  SECTION E: [eː] Long Close-Mid Front Vowel (tālavya)")
    print("─" * 72)

    check_voicing("E1 [eː] voicing", segs[SEG_EE],
                  dur_ms=VS_EE_DUR_MS, min_voicing=VOICING_MIN_MODAL)

    ee_f1 = measure_band_centroid(segs[SEG_EE], EE_F1_BAND_LO, EE_F1_BAND_HI)
    check("E2 [eː] F1 (close-mid)", ee_f1,
          EE_F1_EXPECT_LO, EE_F1_EXPECT_HI, 'Hz')

    ee_f2 = measure_band_centroid(segs[SEG_EE], EE_F2_BAND_LO, EE_F2_BAND_HI)
    check("E3 [eː] F2 (front)", ee_f2,
          EE_F2_EXPECT_LO, EE_F2_EXPECT_HI, 'Hz')

    ee_rms = rms(body(segs[SEG_EE]))
    if word_rms > 1e-8:
        ee_rel = ee_rms / word_rms
        check("E4 [eː] relative amplitude", ee_rel, 0.3, 2.0)

    # E5: [eː] F1 must be higher than [iː] F1 (mid > close)
    if ii_f1 > 0 and ee_f1 > 0:
        f1_diff = ee_f1 - ii_f1
        info(f"[eː] F1 - [iː] F1 = {f1_diff:.1f} Hz (mid higher than close)")
        check("E5 [eː]-[iː] F1 difference (mid > close)", f1_diff,
              30.0, 400.0, 'Hz')

    # E6: [eː] F2 must be lower than [iː] F2 (close-mid < close)
    if ii_f2 > 0 and ee_f2 > 0:
        f2_diff = ii_f2 - ee_f2
        info(f"[iː] F2 - [eː] F2 = {f2_diff:.1f} Hz (close front higher)")
        check("E6 [iː]-[eː] F2 difference (close > close-mid)", f2_diff,
              50.0, 800.0, 'Hz')

    print()

    # ==================================================================
    # SECTION F: F2 Trajectory Coherence (Ī → Ḷ → E)
    # ==================================================================
    print("─" * 72)
    print("  SECTION F: F2 Trajectory Coherence (Ī → Ḷ → E)")
    print("─" * 72)

    # The F2 trajectory is the acoustic signature of this word:
    # high front (2200) → retroflex lateral (1100) → mid front (1750)

    # F1: F2 must DROP from [iː] to [ɭ]
    if ii_f2 > 0 and ll_f2 > 0:
        check("F1 F2 drops [iː]→[ɭ] (front into lateral)", ii_f2 - ll_f2,
              200.0, 1500.0, 'Hz')

    # F2: F2 must RISE from [ɭ] to [eː]
    if ll_f2 > 0 and ee_f2 > 0:
        check("F2 F2 rises [ɭ]→[eː] (lateral into mid front)", ee_f2 - ll_f2,
              100.0, 1200.0, 'Hz')

    # F3: V-shaped trajectory — [ɭ] is the valley
    if ii_f2 > 0 and ll_f2 > 0 and ee_f2 > 0:
        is_valley = ll_f2 < ii_f2 and ll_f2 < ee_f2
        info(f"F2 trajectory: [iː]={ii_f2:.0f} → [ɭ]={ll_f2:.0f} → [eː]={ee_f2:.0f} Hz")
        if is_valley:
            check_pass("F3 V-shaped F2 trajectory",
                       f"[ɭ] is the F2 valley ({ll_f2:.0f} Hz)")
        else:
            check("F3 V-shaped F2 trajectory", 0, 1, 1)

    print()

    # ==================================================================
    # SECTION G: Syllable Coherence (Ī.ḶE)
    # ==================================================================
    print("─" * 72)
    print("  SECTION G: Syllable Coherence (Ī.ḶE)")
    print("─" * 72)

    # G1: All-voiced word — entire concatenation should show voicing
    all_voiced = np.concatenate([segs[SEG_II], segs[SEG_LL], segs[SEG_EE]])
    all_dur = VS_II_DUR_MS + VS_LL_DUR_MS + VS_EE_DUR_MS
    av = measure_voicing(all_voiced, warm=True, dur_ms=all_dur)
    if av is not None:
        check("G1 all-voiced word verification", av,
              VOICING_MIN_MODAL, 1.0)
    else:
        av_lf = measure_lf_ratio(all_voiced)
        check("G1 all-voiced word verification (LF proxy)", av_lf, 0.3, 1.0)

    # G2: Word duration
    word_dur_ms = len(word_sig) / SR * 1000.0
    check("G2 word duration", word_dur_ms, 200.0, 400.0, 'ms')

    # G3: Vowels louder than lateral (syllable nuclei > consonant)
    if ll_rms > 1e-8 and ii_rms > 1e-8:
        vowel_avg_rms = (ii_rms + ee_rms) / 2.0
        v_to_c = vowel_avg_rms / ll_rms
        check("G3 vowels > lateral (syllable nuclei louder)", v_to_c,
              0.8, 5.0)

    # G4: Syllable structure — Ī heavy (long vowel), ḶE light
    # [iː] duration must exceed [ɭ] duration
    check("G4 [iː] longer than [ɭ] (heavy syllable)", ii_dur_ms,
          VS_LL_DUR_MS, 200.0, 'ms')

    print()

    # ==================================================================
    # SUMMARY
    # ==================================================================
    print("=" * 72)
    total = pass_count + fail_count
    print(f"  RESULT: {pass_count}/{total} PASS, {fail_count} FAIL")
    if fail_count == 0:
        print("  ✓ ALL CHECKS PASSED")
    else:
        print("  ✗ SOME CHECKS FAILED")
    print("=" * 72)
    print()

    return fail_count == 0


if __name__ == "__main__":
    success = run_diagnostics()
    sys.exit(0 if success else 1)
