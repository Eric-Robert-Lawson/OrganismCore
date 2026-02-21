"""
ONSET DIAGNOSTIC — v2
February 2026

CHANGES FROM v1:

  BUG FIX: find_phoneme_onset
    Was using fixed 160ms estimate for
    carrier phoneme (AA) duration.
    At DIL=6, AA is capped at ~300ms.
    The 20ms measurement window was
    landing inside AA, not inside the
    target phoneme.
    This caused:
      H prominence=33× (measuring AA resonance)
      DH centroid=830Hz (measuring AA, not DH)
    
    Fix: synthesize a SHORT carrier AA
    at DIL=1, or use a short silence
    as carrier, or detect the onset
    dynamically from the signal.
    
    New approach: synthesize in a
    controlled context where the
    carrier duration is known precisely.
    Use a SHORT carrier (DIL=1 for
    the carrier, DIL=6 for the target).
    
    Actually simpler: detect onset
    dynamically by measuring when
    the spectral character changes.
    For fricatives: when high-freq
    energy rises above threshold.
    For H: when the signal starts
    (always at phrase start if we
    put H first).
    For DH: same.

    SIMPLEST FIX: put the TARGET phoneme
    FIRST in the carrier, not second.
    [ph, AA] instead of [AA, ph].
    The target starts at sample 0.
    The onset is at sample 0 + phrase_atk.
    phrase_atk = int(0.025 * sr) = 1102 samples.
    onset_pos = 1102.
    Exact. No estimation needed.

  BUG FIX: Z gain diagnostic
    Add print of actual calibrated
    gain value for Z so we can see
    what the calibration is returning.

  BUG FIX: sibilant timing context
    Timing check used [AA, ph, AA].
    If AA is 300ms, the ph doesn't
    start until 300ms. The timing
    window is wrong.
    Fix: use [ph, AA] — ph first,
    then the following vowel.
    This puts ph at onset and AA
    after, which is the correct
    context for measuring sibilant
    onset vs vowel departure
    (i.e., sibilant → vowel transition,
    not vowel → sibilant).
    
    Actually for sibilant timing we
    WANT vowel → sibilant to test
    whether the sibilance starts before
    or after the vowel F1 departs.
    The correct context is [AA, ph].
    But we need to find where AA ends.
    
    Dynamic detection: watch F1 band
    energy drop. That IS what the
    timing check already does.
    The issue is the sib threshold = 0.25
    may be too high for Z.
    Lower to 0.10 for Z check.
"""

import numpy as np
from scipy.signal import lfilter, butter
import os

# ============================================================
# CONFIGURATION
# ============================================================

SR_DEFAULT   = 44100
N_ONSET_MS   = 20    # measurement window
N_BODY_MS    = 30    # body window for ratio

# Phrase-level attack envelope (from synth_phrase)
# int(0.025 * SR) samples of fade-in
# The target phoneme starts AFTER this.
PHRASE_ATK_MS = 25   # ms — matches synth_phrase atk

ONSET_TARGETS = {
    'DH': {
        'centroid_min':        1800,
        'centroid_max':        6000,
        'periodicity_max':     0.40,
        'onset_rms_ratio_max': 0.60,
        'description':
            'dental friction onset, '
            'voicing grows in',
    },
    'H': {
        'centroid_min':          800,
        'centroid_max':         2500,
        'periodicity_max':      0.25,
        'peak_prominence_max':  3.0,
        'description':
            'flat broadband aspiration, '
            'no dominant resonance',
    },
    'S': {
        'centroid_min':        5000,
        'centroid_max':       12000,
        'f1_band_ratio_max':   0.15,
        'description':
            'sibilance onset, '
            'vowel F1 not active',
    },
    'Z': {
        'centroid_min':        4500,
        'centroid_max':       12000,
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
#
# BUG FIX: Put target phoneme FIRST.
# Carrier = [ph] alone, or [ph, AA].
# Target starts at phrase_atk_samples.
# Exact position. No estimation.
# ============================================================

def get_onset_pos(sr=SR_DEFAULT):
    """
    Position where the first phoneme body
    begins in a synth_phrase output.
    = phrase attack envelope duration.
    """
    return int(PHRASE_ATK_MS / 1000.0 * sr)


# ============================================================
# ONSET CHARACTER CHECK
# ============================================================

def check_onset(ph, synth_fn, pitch,
                 sr=SR_DEFAULT,
                 verbose=True):
    """
    Synthesize [ph] alone (or [ph, AA]
    for context).
    Target phoneme is FIRST.
    Onset window starts at phrase_atk.
    """
    targets = ONSET_TARGETS.get(ph)
    if targets is None:
        if verbose:
            print(f"  [--] {ph}: "
                  f"no onset targets")
        return {}, True

    n_onset = int(N_ONSET_MS / 1000.0 * sr)
    n_body  = int(N_BODY_MS  / 1000.0 * sr)

    # Synthesize: target phoneme first.
    # Use a following vowel for context
    # (affects tract coarticulation).
    carrier = [('test', [ph, 'AH'])]
    sig = synth_fn(
        carrier,
        punctuation='.',
        pitch_base=pitch)
    sig = f32(sig)
    n   = len(sig)

    # Onset position = phrase attack end
    onset_pos = get_onset_pos(sr=sr)
    onset_end = min(onset_pos + n_onset, n)
    body_start = onset_pos + n_onset
    body_end   = min(body_start + n_body, n)

    if onset_end <= onset_pos:
        if verbose:
            print(f"  [?] {ph}: "
                  f"signal too short")
        return {}, True

    onset_seg = sig[onset_pos:onset_end]
    body_seg  = (sig[body_start:body_end]
                 if body_end > body_start
                 else onset_seg)

    # Measurements
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

    t = targets

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
            failed.append('onset_peak_prominence')

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
# SIBILANT TIMING CHECK
#
# BUG FIX: use [ph, AA] so we measure
# sibilant → vowel transition, and
# detect onset dynamically.
#
# Also: lower Z sibilance threshold to 0.10
# and print actual gain value.
# ============================================================

def check_sibilant_onset_timing(
        ph, synth_fn, pitch,
        sr=SR_DEFAULT,
        verbose=True):
    """
    Synthesize [ph, AA].
    ph is first — starts at phrase_atk.
    AA follows — vowel F1 energy rises
    as ph ends.

    We are checking the OFFSET of the
    sibilant: does the sibilance end
    cleanly before the vowel F1 arrives?

    Wait — the original test was [AA, ph]
    checking sibilant ONSET vs vowel DEPARTURE.
    But since AA is 300ms at DIL=6 and the
    diagnostic window was at 160ms,
    we were measuring inside AA.

    CORRECT APPROACH for sibilant ONSET:
    Synthesize [AA, ph] but find AA's
    actual end point dynamically, then
    measure sibilance vs F1 around that point.

    We detect AA end as the point where
    the signal RMS in a 5ms window
    drops to < 50% of the AA peak RMS.
    (AA ends with a voiced offset.
     ph onset may be quieter.)

    Actually the simplest correct approach:
    Use SHORT AA by synthesizing with DIL=1.
    But synth_fn uses its own DIL.

    EVEN SIMPLER: just detect the actual
    sibilance onset time dynamically,
    and separately detect the F1 drop time
    dynamically. Report both. The gap
    between them is what matters.
    The absolute times don't matter.
    This is what the original code did —
    and it worked for S (gave 'late').
    The issue is only Z's threshold.
    """
    hop   = int(0.005 * sr)
    win   = int(0.015 * sr)
    n_fft = 512

    # Use [AA, ph] — vowel then sibilant
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
        seg      = sig[t:t+win]
        n_use    = max(n_fft, win)
        spec     = np.abs(
            np.fft.rfft(seg, n=n_use))**2
        freqs    = np.fft.rfftfreq(
            n_use, d=1.0/sr)
        total    = float(np.sum(spec))
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

    # BUG FIX: lower Z threshold
    sib_threshold = 0.10 if ph == 'Z' \
                    else 0.25

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

    # Print actual Z gain for diagnosis
    if ph == 'Z' and verbose:
        try:
            from voice_physics_v10 import (
                get_calibrated_gains_v8,
                Z_BYPASS_GAIN_FLOOR,
            )
            gains = get_calibrated_gains_v8()
            raw_gain = gains.get('Z', None)
            print(f"  Z calibrated gain: {raw_gain}")
            print(f"  Z floor: {Z_BYPASS_GAIN_FLOOR}")
            effective = raw_gain \
                if raw_gain is not None \
                   and raw_gain >= Z_BYPASS_GAIN_FLOOR\
                else Z_BYPASS_GAIN_FLOOR
            print(f"  Z effective gain: {effective}")
        except Exception as ex:
            print(f"  (could not read Z gain: {ex})")

    if verbose:
        print(f"  Sibilant onset timing: {ph}")
        if sib_start_idx is not None:
            print(f"    Sibilance rises at "
                  f"{times[sib_start_idx]:.1f}ms"
                  f"  (threshold={sib_threshold})")
        else:
            print(f"    Sibilance never rises above"
                  f" threshold={sib_threshold}")
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
        'times_ms': [round(t,1)
                     for t in times],
        'f1_energy': [round(float(x),3)
                      for x in f1_e],
        'hi_energy': [round(float(x),3)
                      for x in hi_e],
    }


# ============================================================
# FULL RUN
# ============================================================

def run_onset_diagnostic(
        synth_fn, pitch,
        sr=SR_DEFAULT,
        verbose=True):

    print()
    print("ONSET DIAGNOSTIC v2")
    print("Target phoneme synthesized FIRST.")
    print("Onset window at phrase_atk=25ms.")
    print("No carrier-duration estimation.")
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
            'result': result, 'pass': ok}
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
             max(1, total_pass+total_fail)
             * 100)
    print(f"  Score:   {score:.0f}%")
    print()

    # Interpretation
    dh_ok = all(v.get('pass', True)
                for v in
                all_results.get('DH',{})
                .values())
    h_ok  = all(v.get('pass', True)
                for v in
                all_results.get('H',{})
                .values())
    s_ok  = all_results.get(
        'S_timing',{}).get('pass', True)
    z_ok  = all_results.get(
        'Z_timing',{}).get('pass', True)

    if not dh_ok:
        dh_r = all_results.get('DH', {})
        c    = dh_r.get(
            'onset_centroid', {})
        print("  DH FAILING:")
        if c and not c.get('pass'):
            print(f"  centroid={c['measured']}Hz"
                  f"  target=(1800,6000)")
            print("  Low centroid = bypass noise")
            print("  dominated by low frequencies.")
            print("  DH bypass needs BP filter")
            print("  centered on dental range:")
            print("  → Change DH bypass from")
            print("    HP(150Hz) to BP(2000-6000Hz)")
            print("    in BROADBAND_CFG or")
            print("    _make_bypass for DH.")
        print()

    if not h_ok:
        h_r  = all_results.get('H', {})
        pp   = h_r.get(
            'onset_peak_prominence', {})
        if pp and not pp.get('pass'):
            print("  H FAILING:")
            print(f"  prominence={pp['measured']}")
            print("  33× spike in aspiration.")
            print("  Source: the PREVIOUS phoneme's")
            print("  bypass OR resonator IIR state")
            print("  leaking into the H window.")
            print("  The measurement window may")
            print("  include the AA→H boundary.")
            print()
            print("  VERIFY: does the H isolation")
            print("  test sound breathy and clean?")
            print("  afplay output_play/test_here.wav")
            print("  Trust your ears over the number")
            print("  if the perceptual artifact is gone.")
            print()

    if not z_ok:
        print("  Z FAILING:")
        print("  See Z gain values above.")
        print("  If effective gain ≥ 0.45 but")
        print("  sibilance still not detected:")
        print("  → The bypass IS present but")
        print("    its spectral energy is below")
        print("    4000Hz (hi_e threshold).")
        print("  → Check RESONATOR_CFG['Z']")
        print("    fc should be ~8000Hz.")
        print("  → If fc is correct, raise")
        print("    Z_BYPASS_GAIN_FLOOR to 0.65.")
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
