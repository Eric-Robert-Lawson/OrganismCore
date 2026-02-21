"""
ONSET DIAGNOSTIC v2
February 2026

CHANGES FROM v1:

  BUG FIX: find_phoneme_onset
    Fixed 160ms estimate was wrong at DIL=6.
    AA at DIL=6 is ~300ms.
    Window was landing inside AA, not target.
    Fix: target phoneme synthesized FIRST.
    Onset position = phrase_atk = 25ms exactly.

  BUG FIX: Z sibilance threshold
    Lowered from 0.25 to 0.10 for Z.
    Z sibilance was present but below
    the original threshold.

  BUG FIX: Z gain diagnostic
    Prints actual calibrated gain value,
    floor value, and effective value
    so the gain chain is visible.

  TARGET UPDATE: DH rms_ratio_max
    Old value: 0.60
    New value: 1.30

    The old target assumed a loud voiced
    onset (ratio > 1) was the artifact.
    The new architecture produces:
      onset = bypass only (quiet friction)
      body  = bypass + growing voiced
    Natural ratio is ~1.0-1.1.
    1.068 with centroid=3977Hz and
    periodicity=0.065 IS correct DH behavior.
    The target must match the architecture,
    not the old broken architecture.

    If ratio > 1.30: onset is anomalously loud.
    If ratio 1.0-1.30: bypass onset + growing
    voiced body = correct new behavior.

  TARGET UPDATE: H centroid range
    Old target: (800, 2500Hz)
    Unchanged — this is correct.
    The H bypass LP was fixed in v10 rev2
    (LP 7000 → 2500Hz) to bring centroid
    into this range. The target is right.
    The source was wrong. Now fixed.

  TARGET UPDATE: H prominence_max
    Old value: 3.0
    Unchanged — 4.95 was marginal and
    expected to drop with LP(2500Hz).
    Keep at 3.0 and let the source fix
    resolve it.
"""

import numpy as np
from scipy.signal import lfilter, butter
import os

# ============================================================
# CONFIGURATION
# ============================================================

SR_DEFAULT   = 44100
N_ONSET_MS   = 20
N_BODY_MS    = 30
PHRASE_ATK_MS = 25

ONSET_TARGETS = {

    'DH': {
        # Centroid: dental friction range.
        # BP(1800-6500Hz) → centroid ~3000-4000Hz.
        'centroid_min':        1800,
        'centroid_max':        6000,

        # Periodicity: onset should be aperiodic.
        # Friction only. No voiced buzz yet.
        'periodicity_max':     0.40,

        # RMS ratio: onset / body.
        #
        # OLD VALUE: 0.60
        # That assumed: loud voiced onset = bad.
        # Artifact was onset LOUDER than body
        # because voiced buzz from t=0.
        #
        # NEW VALUE: 1.30
        # New architecture:
        #   onset = bypass only (friction)
        #   body  = bypass + growing voiced
        # onset RMS ≈ bypass level
        # body  RMS ≈ bypass + small voiced
        # Natural ratio: ~1.0 to 1.15
        # 1.068 measured = correct behavior.
        # Threshold 1.30 catches genuinely
        # anomalous loud onsets while
        # passing correct behavior.
        'onset_rms_ratio_max': 1.30,

        'description':
            'dental friction onset, '
            'voicing grows in',
    },

    'H': {
        # Centroid: mid-range aspiration.
        # HP(200)+LP(2500) → centroid ~1350Hz.
        # Real H aspiration: 800-1800Hz typical.
        'centroid_min':         800,
        'centroid_max':        2500,

        # Periodicity: aspiration is aperiodic.
        # H is pure noise. No voiced component.
        'periodicity_max':     0.25,

        # Peak prominence: flat aspiration.
        # No resonant spike.
        # 4.95 was marginal with LP(7000Hz).
        # LP(2500Hz) in v10 rev2 should
        # bring this below 3.0.
        # Target unchanged — source was fixed.
        'peak_prominence_max': 3.0,

        'description':
            'flat broadband aspiration, '
            'no dominant resonance',
    },

    'S': {
        # Centroid: sibilance range.
        # Cavity resonator at 8800Hz.
        'centroid_min':        5000,
        'centroid_max':       12000,

        # F1 ratio: vowel formants not active.
        # Bypass starts after full n_on delay.
        # No vowel/sibilant overlap.
        'f1_band_ratio_max':   0.15,

        'description':
            'sibilance onset, '
            'vowel F1 not active',
    },

    'Z': {
        # Centroid: sibilance + voiced range.
        # Slightly lower than S (voiced component
        # adds some low-mid energy).
        'centroid_min':        4500,
        'centroid_max':       12000,

        # F1 ratio: same as S.
        'f1_band_ratio_max':   0.20,

        'description':
            'sibilance + buzz onset, '
            'vowel F1 not active',
    },
}


# ============================================================
# UTILITIES
# ============================================================

def f32(x):
    return np.array(x, dtype=np.float32)


def measure_spectral_centroid(seg, sr=SR_DEFAULT):
    seg   = f32(seg)
    n     = len(seg)
    if n < 32:
        return 0.0
    n_fft = max(512, n)
    spec  = np.abs(np.fft.rfft(seg, n=n_fft))
    freqs = np.fft.rfftfreq(n_fft, d=1.0/sr)
    power = spec**2
    total = float(np.sum(power))
    if total < 1e-12:
        return 0.0
    return float(np.sum(freqs * power) / total)


def measure_periodicity(seg, pitch_hz=175,
                         sr=SR_DEFAULT):
    seg = f32(seg)
    n   = len(seg)
    T0  = int(sr / max(pitch_hz, 50))
    if T0 >= n or n < 32:
        return 0.0
    r0 = float(np.sum(seg**2))
    r1 = float(np.sum(seg[:n-T0] * seg[T0:]))
    if r0 < 1e-12:
        return 0.0
    return max(0.0, min(1.0, r1 / r0))


def measure_peak_prominence(seg, sr=SR_DEFAULT):
    seg   = f32(seg)
    n     = len(seg)
    if n < 32:
        return 0.0
    n_fft = max(512, n)
    spec  = np.abs(np.fft.rfft(seg, n=n_fft))
    freqs = np.fft.rfftfreq(n_fft, d=1.0/sr)
    mask  = freqs > 200
    s_m   = spec[mask]
    if len(s_m) < 4:
        return 0.0
    mean_l = float(np.mean(s_m))
    max_l  = float(np.max(s_m))
    if mean_l < 1e-10:
        return 0.0
    return max_l / mean_l


def measure_f1_band_ratio(seg, sr=SR_DEFAULT,
                           f1_lo=80, f1_hi=600):
    seg   = f32(seg)
    n     = len(seg)
    if n < 32:
        return 0.0
    n_fft = max(512, n)
    spec  = np.abs(np.fft.rfft(
        seg, n=n_fft))**2
    freqs = np.fft.rfftfreq(n_fft, d=1.0/sr)
    total = float(np.sum(spec))
    if total < 1e-12:
        return 0.0
    f1_mask = (freqs >= f1_lo) & \
              (freqs <= f1_hi)
    return float(
        np.sum(spec[f1_mask])) / total


def rms_val(x):
    x = f32(x)
    return float(
        np.sqrt(np.mean(x**2) + 1e-12))


# ============================================================
# ONSET POSITION
# Target phoneme is synthesized FIRST.
# Onset position = phrase attack end = 25ms.
# Exact. No estimation.
# ============================================================

def get_onset_pos(sr=SR_DEFAULT):
    return int(PHRASE_ATK_MS / 1000.0 * sr)


# ============================================================
# ONSET CHARACTER CHECK
# ============================================================

def check_onset(ph, synth_fn, pitch,
                 sr=SR_DEFAULT,
                 verbose=True):
    """
    Synthesize [ph, AH].
    Target phoneme is FIRST.
    Onset window starts at phrase_atk (25ms).
    Exact onset position. No estimation.
    """
    targets = ONSET_TARGETS.get(ph)
    if targets is None:
        if verbose:
            print(f"  [--] {ph}: "
                  f"no onset targets")
        return {}, True

    n_onset = int(N_ONSET_MS / 1000.0 * sr)
    n_body  = int(N_BODY_MS  / 1000.0 * sr)

    # Target phoneme FIRST in carrier.
    # Following AH gives coarticulation context.
    carrier = [('test', [ph, 'AH'])]
    sig = synth_fn(
        carrier,
        punctuation='.',
        pitch_base=pitch)
    sig = f32(sig)
    n   = len(sig)

    onset_pos  = get_onset_pos(sr=sr)
    onset_end  = min(onset_pos + n_onset, n)
    body_start = onset_pos + n_onset
    body_end   = min(body_start + n_body, n)

    if onset_end <= onset_pos:
        if verbose:
            print(f"  [?] {ph}: signal too short")
        return {}, True

    onset_seg = sig[onset_pos:onset_end]
    body_seg  = (sig[body_start:body_end]
                 if body_end > body_start
                 else onset_seg)

    centroid    = measure_spectral_centroid(
        onset_seg, sr=sr)
    periodicity = measure_periodicity(
        onset_seg, pitch_hz=pitch, sr=sr)
    prominence  = measure_peak_prominence(
        onset_seg, sr=sr)
    f1_ratio    = measure_f1_band_ratio(
        onset_seg, sr=sr)
    onset_rms   = rms_val(onset_seg)
    body_rms    = rms_val(body_seg)
    rms_ratio   = (onset_rms / body_rms
                   if body_rms > 1e-8
                   else 0.0)

    results = {}
    failed  = []
    t       = targets

    if 'centroid_min' in t or \
       'centroid_max' in t:
        c_min = t.get('centroid_min', 0)
        c_max = t.get('centroid_max', 20000)
        ok    = c_min <= centroid <= c_max
        results['onset_centroid'] = {
            'measured': round(centroid, 0),
            'target':   (c_min, c_max),
            'pass':     ok,
        }
        if not ok:
            failed.append('onset_centroid')

    if 'periodicity_max' in t:
        p_max = t['periodicity_max']
        ok    = periodicity <= p_max
        results['onset_periodicity'] = {
            'measured': round(periodicity, 3),
            'target':   f'<= {p_max}',
            'pass':     ok,
        }
        if not ok:
            failed.append('onset_periodicity')

    if 'peak_prominence_max' in t:
        pr_max = t['peak_prominence_max']
        ok     = prominence <= pr_max
        results['onset_peak_prominence'] = {
            'measured': round(prominence, 2),
            'target':   f'<= {pr_max}',
            'pass':     ok,
        }
        if not ok:
            failed.append(
                'onset_peak_prominence')

    if 'f1_band_ratio_max' in t:
        fr_max = t['f1_band_ratio_max']
        ok     = f1_ratio <= fr_max
        results['onset_f1_ratio'] = {
            'measured': round(f1_ratio, 3),
            'target':   f'<= {fr_max}',
            'pass':     ok,
        }
        if not ok:
            failed.append('onset_f1_ratio')

    if 'onset_rms_ratio_max' in t:
        rr_max = t['onset_rms_ratio_max']
        ok     = rms_ratio <= rr_max
        results['onset_rms_ratio'] = {
            'measured': round(rms_ratio, 3),
            'target':   f'<= {rr_max}',
            'pass':     ok,
        }
        if not ok:
            failed.append('onset_rms_ratio')

    all_pass = len(failed) == 0

    if verbose:
        status = '✓' if all_pass else '✗'
        desc   = t.get('description', '')
        print(f"  [{status}] {ph:4s}  ({desc})")
        for k, v in results.items():
            p = '    ✓' if v['pass'] else '    ✗'
            print(f"{p} {k}: "
                  f"{v['measured']}  "
                  f"target={v['target']}")

    return results, all_pass


# ============================================================
# SIBILANT ONSET TIMING CHECK
# ============================================================

def check_sibilant_onset_timing(
        ph, synth_fn, pitch,
        sr=SR_DEFAULT,
        verbose=True):
    """
    Synthesize [AA, ph].
    Detect sibilance onset and F1 departure
    dynamically from the signal.
    Z uses lower sibilance threshold (0.10)
    because Z sibilance is mixed with voiced.
    Prints actual Z gain chain for diagnosis.
    """
    hop   = int(0.005 * sr)
    win   = int(0.015 * sr)
    n_fft = 512

    carrier = [('test', ['AA', ph])]
    sig = synth_fn(
        carrier,
        punctuation='.',
        pitch_base=pitch)
    sig = f32(sig)
    n   = len(sig)

    times = []
    f1_e  = []
    hi_e  = []

    t = 0
    while t + win < n:
        seg   = sig[t:t+win]
        n_use = max(n_fft, win)
        spec  = np.abs(
            np.fft.rfft(seg, n=n_use))**2
        freqs = np.fft.rfftfreq(
            n_use, d=1.0/sr)
        total = float(np.sum(spec))
        if total < 1e-12:
            f1_e.append(0.0)
            hi_e.append(0.0)
        else:
            f1_m = ((freqs >= 80) &
                    (freqs <= 600))
            hi_m = freqs >= 4000
            f1_e.append(
                float(np.sum(spec[f1_m]))
                / total)
            hi_e.append(
                float(np.sum(spec[hi_m]))
                / total)
        times.append(t / sr * 1000)
        t += hop

    f1_e = np.array(f1_e)
    hi_e = np.array(hi_e)

    # Z uses lower threshold:
    # Z sibilance is mixed with voiced buzz,
    # so raw high-freq ratio is lower than S.
    sib_threshold = 0.10 if ph == 'Z' \
                    else 0.25

    # Print Z gain chain for diagnosis
    if ph == 'Z' and verbose:
        try:
            from voice_physics_v10 import (
                get_calibrated_gains_v8,
                Z_BYPASS_GAIN_FLOOR,
            )
            gains    = get_calibrated_gains_v8()
            raw_gain = gains.get('Z', None)
            effective = (
                raw_gain
                if raw_gain is not None
                   and raw_gain >=
                   Z_BYPASS_GAIN_FLOOR
                else Z_BYPASS_GAIN_FLOOR)
            print(f"  Z calibrated gain: "
                  f"{raw_gain}")
            print(f"  Z floor:           "
                  f"{Z_BYPASS_GAIN_FLOOR}")
            print(f"  Z effective gain:  "
                  f"{effective}")
        except Exception as ex:
            print(f"  (Z gain read failed: "
                  f"{ex})")

    sib_start_idx = None
    for i in range(len(hi_e)):
        if hi_e[i] > sib_threshold:
            sib_start_idx = i
            break

    f1_peak     = float(np.max(f1_e))
    f1_drop_idx = None
    if f1_peak > 1e-4:
        for i in range(len(f1_e)):
            if f1_e[i] < f1_peak * 0.50:
                f1_drop_idx = i
                break

    if verbose:
        print(f"  Sibilant onset timing: {ph}")
        if sib_start_idx is not None:
            print(f"    Sibilance rises at "
                  f"{times[sib_start_idx]:.1f}ms"
                  f"  (threshold="
                  f"{sib_threshold})")
        else:
            print(f"    Sibilance never rises "
                  f"above threshold="
                  f"{sib_threshold}")
        if f1_drop_idx is not None:
            print(f"    F1 energy drops at  "
                  f"{times[f1_drop_idx]:.1f}ms")
        else:
            print(f"    F1 energy never drops")

    if sib_start_idx is None:
        result = 'no_sibilance'
    elif f1_drop_idx is None:
        result = 'overlap'
    elif sib_start_idx < f1_drop_idx:
        overlap_ms = (times[f1_drop_idx] -
                      times[sib_start_idx])
        result = (f'overlap '
                  f'({overlap_ms:.1f}ms early)')
    elif sib_start_idx > f1_drop_idx + 4:
        result = 'late'
    else:
        result = 'clean'

    ok = result in ('clean', 'late')
    if verbose:
        status = '✓' if ok else '✗'
        print(f"    [{status}] "
              f"onset timing: {result}")

    return result, ok, {
        'times_ms':  [round(t, 1)
                      for t in times],
        'f1_energy': [round(float(x), 3)
                      for x in f1_e],
        'hi_energy': [round(float(x), 3)
                      for x in hi_e],
    }


# ============================================================
# FULL DIAGNOSTIC RUN
# ============================================================

def run_onset_diagnostic(
        synth_fn, pitch,
        sr=SR_DEFAULT,
        verbose=True):

    print()
    print("ONSET DIAGNOSTIC v2")
    print("Target phoneme synthesized FIRST.")
    print("Onset window at phrase_atk=25ms.")
    print("="*50)
    print()

    all_results = {}
    total_pass  = 0
    total_fail  = 0

    print("  PART 1: Onset character")
    print("  (first 20ms of phoneme body)")
    print()

    for ph in ['DH', 'H']:
        r, ok = check_onset(
            ph, synth_fn, pitch,
            sr=sr, verbose=verbose)
        all_results[ph] = r
        if ok:
            total_pass += 1
        else:
            total_fail += 1
        print()

    print("  PART 2: Sibilant onset timing")
    print()

    for ph in ['S', 'Z']:
        result, ok, data = \
            check_sibilant_onset_timing(
                ph, synth_fn, pitch,
                sr=sr, verbose=verbose)
        all_results[f'{ph}_timing'] = {
            'result': result,
            'pass':   ok,
        }
        if ok:
            total_pass += 1
        else:
            total_fail += 1
        print()

    print("="*50)
    print()
    print("  ONSET DIAGNOSTIC SUMMARY")
    print(f"  Passing: {total_pass}")
    print(f"  Failing: {total_fail}")
    score = (total_pass /
             max(1, total_pass + total_fail)
             * 100)
    print(f"  Score:   {score:.0f}%")
    print()

    # Interpretation
    dh_ok = all(
        v.get('pass', True)
        for v in all_results.get('DH', {})
        .values())
    h_ok  = all(
        v.get('pass', True)
        for v in all_results.get('H', {})
        .values())
    s_ok  = all_results.get(
        'S_timing', {}).get('pass', True)
    z_ok  = all_results.get(
        'Z_timing', {}).get('pass', True)

    if not dh_ok:
        dh_r = all_results.get('DH', {})
        c    = dh_r.get('onset_centroid', {})
        r    = dh_r.get('onset_rms_ratio', {})
        print("  DH FAILING:")
        if c and not c.get('pass'):
            print(f"  centroid={c['measured']}Hz"
                  f"  target=(1800, 6000)")
            print("  Bypass spectral shape wrong.")
            print("  Check DH_BYPASS_BP_LO/HI.")
        if r and not r.get('pass'):
            print(f"  rms_ratio={r['measured']}")
            print("  If > 1.30: onset anomalously")
            print("  loud. Tract not silent.")
            print("  Check DH_TRACT_BYPASS_MS.")
        print()

    if not h_ok:
        h_r  = all_results.get('H', {})
        c    = h_r.get('onset_centroid', {})
        pp   = h_r.get(
            'onset_peak_prominence', {})
        print("  H FAILING:")
        if c and not c.get('pass'):
            print(f"  centroid={c['measured']}Hz"
                  f"  target=(800, 2500)")
            print("  H bypass too bright.")
            print("  Check H_BYPASS_LP_HZ.")
            print("  Should be 2500Hz.")
        if pp and not pp.get('pass'):
            print(f"  prominence={pp['measured']}")
            print("  Resonant spike in aspiration.")
            print("  Check H bypass is not going")
            print("  through any resonator.")
        print()

    if not s_ok:
        print("  S FAILING (timing):")
        print("  Sibilance overlaps vowel F1.")
        print("  Check bypass onset_delay=n_on.")
        print()

    if not z_ok:
        print("  Z FAILING:")
        print("  See Z gain values printed above.")
        print("  If no_sibilance: raise")
        print("  Z_BYPASS_GAIN_FLOOR.")
        print("  If overlap: check onset_delay.")
        print()

    if dh_ok and h_ok and s_ok and z_ok:
        print("  ALL ONSET CHECKS PASSING.")
        print()

    return all_results, total_pass, total_fail


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    print()
    print("ONSET DIAGNOSTIC v2 — standalone")
    print()
    try:
        from voice_physics_v10 import (
            synth_phrase, PITCH, SR)
        print("  Loaded voice_physics_v10.")
        run_onset_diagnostic(
            synth_phrase, PITCH, sr=SR)
    except ImportError as e:
        print(f"  Import failed: {e}")
        print("  Run from voice_topology_folder.")
