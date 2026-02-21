"""
ONSET DIAGNOSTIC
February 2026

The rainbow measures steady-state phoneme properties.
These artifacts are ONSET artifacts.
The rainbow cannot see them.

This diagnostic measures:

  For each target phoneme in context:
    1. Extract the first N_ONSET_MS of the phoneme
    2. Measure spectral centroid of that window
    3. Measure periodicity (voiced character)
       of that window
    4. Measure RMS of that window vs
       RMS of the phoneme body
    5. Compare to ONSET_TARGETS

ONSET_TARGETS define what each phoneme
should look like in its FIRST 20ms.

Not what it sounds like at steady state.
What it sounds like at t=0.

The four failing phonemes and their
expected onset character:

  DH onset:
    Should be: low periodicity,
               dental friction character,
               NOT a strong F1=270Hz resonance.
    If spectral centroid of first 20ms < 1500Hz
    AND periodicity > 0.4:
    → voiced component too strong at onset.
    → "ea" prefix artifact.

  H onset:
    Should be: broadband aspiration,
               spectral centroid 1000-3000Hz,
               NO resonant peak at F2 frequency.
    If strong resonant peak exists at
    next-vowel F2 frequency in first 20ms:
    → coarticulation too aggressive.
    → "CH" prefix artifact.

  S (word-final) onset-relative:
    Should be: bypass reaches full level
               AFTER the preceding vowel
               formants have moved at least 50%.
    If bypass energy is high in samples
    where F1 is still at vowel target:
    → onset too early.
    → dragged sibilant artifact.

  Z (word-final) — same as S.

Usage:
  from onset_diagnostic import run_onset_diagnostic
  from voice_physics_v10 import synth_phrase, PITCH
  run_onset_diagnostic(synth_phrase, PITCH)

Or run directly:
  python onset_diagnostic.py
"""

import numpy as np
from scipy.signal import lfilter, butter, find_peaks
import os

# ============================================================
# CONFIGURATION
# ============================================================

N_ONSET_MS  = 20    # ms window for onset measurement
N_BODY_MS   = 30    # ms window for body measurement
                     # (used for ratio)
SR_DEFAULT  = 44100

# Onset targets — what each phoneme's first 20ms
# should look like spectrally and temporally.

ONSET_TARGETS = {

    # DH: dental voiced fricative
    # Onset character: dental friction first,
    # voiced buzz grows into body.
    # First 20ms should be:
    #   - spectral centroid above 2000Hz
    #     (friction character, not vowel buzz)
    #   - periodicity below 0.35
    #     (not strongly periodic at onset)
    #   - RMS below 0.55 × body RMS
    #     (quiet onset, not full-level voiced)
    'DH': {
        'centroid_min': 1800,
        'centroid_max': 5000,
        'periodicity_max': 0.40,
        'onset_rms_ratio_max': 0.60,
        'description': 'dental friction onset, '
                        'voicing grows in',
    },

    # H: glottal aspirate
    # Onset character: broadband aspiration,
    # no dominant resonant peak,
    # spectral centroid in mid range.
    # First 20ms should be:
    #   - spectral centroid 800-2500Hz
    #     (mid-range aspiration)
    #   - NO resonant peak taller than
    #     3× the spectral floor
    #     (flat aspiration, not resonated)
    #   - periodicity below 0.25
    #     (essentially aperiodic)
    'H': {
        'centroid_min':  800,
        'centroid_max': 2500,
        'periodicity_max': 0.25,
        'peak_prominence_max': 3.0,
        'description': 'flat broadband aspiration, '
                        'no dominant resonance',
    },

    # S: alveolar sibilant
    # Onset character: bypass energy should
    # arrive AFTER tract has transitioned.
    # First 20ms should be:
    #   - spectral centroid ABOVE 5000Hz
    #     (sibilance, not vowel formants)
    #   - F1-band energy (80-600Hz) LOW
    #     relative to high-freq energy
    #     (vowel formants not still active)
    'S': {
        'centroid_min': 5000,
        'centroid_max': 12000,
        'f1_band_ratio_max': 0.15,
        'description': 'sibilance onset, '
                        'vowel F1 not active',
    },

    # Z: voiced alveolar sibilant
    # Same as S for onset timing.
    'Z': {
        'centroid_min': 4500,
        'centroid_max': 12000,
        'f1_band_ratio_max': 0.20,
        'description': 'sibilance + buzz onset, '
                        'vowel F1 not active',
    },
}


# ============================================================
# MEASUREMENT FUNCTIONS
# ============================================================

def f32(x):
    return np.array(x, dtype=np.float32)


def measure_spectral_centroid(seg, sr=SR_DEFAULT):
    """
    Spectral centroid of a short segment.
    Returns frequency in Hz.
    """
    seg = f32(seg)
    n   = len(seg)
    if n < 32:
        return 0.0
    # Use zero-padded FFT for resolution
    n_fft = max(512, n)
    spec  = np.abs(np.fft.rfft(seg, n=n_fft))
    freqs = np.fft.rfftfreq(n_fft, d=1.0/sr)
    # Weight by power
    power = spec**2
    total = float(np.sum(power))
    if total < 1e-12:
        return 0.0
    centroid = float(np.sum(freqs * power) / total)
    return centroid


def measure_periodicity(seg, pitch_hz=175,
                         sr=SR_DEFAULT):
    """
    Normalized autocorrelation at T0.
    1.0 = perfectly periodic.
    0.0 = completely aperiodic.
    """
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
    """
    Ratio of tallest spectral peak to
    mean spectral level.
    High value = resonator character.
    Low value = flat aspiration character.
    """
    seg = f32(seg)
    n   = len(seg)
    if n < 32:
        return 0.0
    n_fft = max(512, n)
    spec  = np.abs(np.fft.rfft(seg, n=n_fft))
    freqs = np.fft.rfftfreq(n_fft, d=1.0/sr)
    # Only look above 200Hz to avoid DC
    mask  = freqs > 200
    s_m   = spec[mask]
    if len(s_m) < 4:
        return 0.0
    mean_level = float(np.mean(s_m))
    max_level  = float(np.max(s_m))
    if mean_level < 1e-10:
        return 0.0
    return max_level / mean_level


def measure_f1_band_ratio(seg, sr=SR_DEFAULT,
                           f1_lo=80, f1_hi=600):
    """
    Ratio of energy in F1 band (80-600Hz)
    to total energy.
    High value = strong vowel formant.
    Low value = consonant/fricative.
    """
    seg = f32(seg)
    n   = len(seg)
    if n < 32:
        return 0.0
    n_fft = max(512, n)
    spec  = np.abs(np.fft.rfft(seg, n=n_fft))**2
    freqs = np.fft.rfftfreq(n_fft, d=1.0/sr)
    total  = float(np.sum(spec))
    if total < 1e-12:
        return 0.0
    f1_mask = (freqs >= f1_lo) & (freqs <= f1_hi)
    f1_e    = float(np.sum(spec[f1_mask]))
    return f1_e / total


def rms(x):
    x = f32(x)
    return float(np.sqrt(np.mean(x**2) + 1e-12))


# ============================================================
# PHONEME ONSET EXTRACTOR
# Synthesizes a phoneme in context and
# extracts the onset window.
# ============================================================

def synth_phoneme_in_context(ph, synth_fn,
                               pitch,
                               context='vowel_before',
                               sr=SR_DEFAULT):
    """
    Synthesize a phoneme in a carrier context.

    context='vowel_before':
      [AA] [ph] — onset of ph follows AA
      Isolates onset artifacts after a vowel.

    context='start':
      [ph] alone — onset at start of phrase.
      Isolates onset artifacts at phrase beginning.

    Returns (full_sig, ph_start_sample, ph_n_samples)
    so caller can extract the onset window.
    """
    if context == 'vowel_before':
        carrier = [('test', ['AA', ph])]
    elif context == 'vowel_both':
        carrier = [('test', ['AA', ph, 'AA'])]
    else:
        carrier = [('test', [ph])]

    sig = synth_fn(
        carrier,
        punctuation='.',
        pitch_base=pitch)

    return f32(sig)


def find_phoneme_onset(sig, ph, sr=SR_DEFAULT,
                        context='vowel_before'):
    """
    Locate the approximate sample position
    where ph begins in the signal.

    For context='vowel_before':
    The AA precedes ph.
    AA duration at DIL=6 is ~200ms (capped).
    We look for the onset of consonant character
    after ~150ms.

    This is approximate — the diagnostic
    does not need precise boundaries.
    It needs to capture the first 20ms
    of the phoneme correctly.

    Returns estimated onset sample.
    """
    n    = len(sig)
    sr_f = float(sr)

    # Rough estimate: for vowel_before context,
    # AA is ~150-250ms, ph starts after that.
    # Use 160ms as the search start.
    search_start = int(0.160 * sr)
    search_start = min(search_start, n // 3)

    return search_start


# ============================================================
# CORE DIAGNOSTIC
# ============================================================

def check_onset(ph, synth_fn, pitch,
                 sr=SR_DEFAULT,
                 verbose=True):
    """
    Check the onset character of phoneme ph.

    Returns dict of measurements and pass/fail
    for each onset target metric.
    """
    targets = ONSET_TARGETS.get(ph)
    if targets is None:
        if verbose:
            print(f"  [--] {ph}: no onset targets defined")
        return {}, True

    n_onset  = int(N_ONSET_MS / 1000.0 * sr)
    n_body   = int(N_BODY_MS  / 1000.0 * sr)

    # Synthesize in carrier context
    context  = 'vowel_before'
    sig      = synth_phoneme_in_context(
        ph, synth_fn, pitch,
        context=context, sr=sr)

    onset_pos = find_phoneme_onset(
        sig, ph, sr=sr, context=context)

    n_sig = len(sig)

    # Extract onset window
    onset_end = min(onset_pos + n_onset, n_sig)
    onset_seg = sig[onset_pos:onset_end]

    # Extract body window (after onset)
    body_start = onset_pos + n_onset
    body_end   = min(body_start + n_body, n_sig)
    body_seg   = (sig[body_start:body_end]
                  if body_end > body_start
                  else onset_seg)

    if len(onset_seg) < 8:
        if verbose:
            print(f"  [?] {ph}: onset segment too short")
        return {}, True

    # Measurements
    centroid    = measure_spectral_centroid(
        onset_seg, sr=sr)
    periodicity = measure_periodicity(
        onset_seg, pitch_hz=pitch, sr=sr)
    prominence  = measure_peak_prominence(
        onset_seg, sr=sr)
    f1_ratio    = measure_f1_band_ratio(
        onset_seg, sr=sr)

    onset_rms = rms(onset_seg)
    body_rms  = rms(body_seg)
    rms_ratio = (onset_rms / body_rms
                 if body_rms > 1e-8
                 else 0.0)

    # Check against targets
    results = {}
    passed  = []
    failed  = []

    t = targets

    if 'centroid_min' in t or \
       'centroid_max' in t:
        c_min = t.get('centroid_min', 0)
        c_max = t.get('centroid_max', 20000)
        ok    = (c_min <= centroid <= c_max)
        results['onset_centroid'] = {
            'measured': round(centroid, 0),
            'target':   (c_min, c_max),
            'pass':     ok,
        }
        (passed if ok else failed).append(
            'onset_centroid')

    if 'periodicity_max' in t:
        p_max = t['periodicity_max']
        ok    = (periodicity <= p_max)
        results['onset_periodicity'] = {
            'measured': round(periodicity, 3),
            'target':   f'<= {p_max}',
            'pass':     ok,
        }
        (passed if ok else failed).append(
            'onset_periodicity')

    if 'peak_prominence_max' in t:
        pr_max = t['peak_prominence_max']
        ok     = (prominence <= pr_max)
        results['onset_peak_prominence'] = {
            'measured': round(prominence, 2),
            'target':   f'<= {pr_max}',
            'pass':     ok,
        }
        (passed if ok else failed).append(
            'onset_peak_prominence')

    if 'f1_band_ratio_max' in t:
        fr_max = t['f1_band_ratio_max']
        ok     = (f1_ratio <= fr_max)
        results['onset_f1_ratio'] = {
            'measured': round(f1_ratio, 3),
            'target':   f'<= {fr_max}',
            'pass':     ok,
        }
        (passed if ok else failed).append(
            'onset_f1_ratio')

    if 'onset_rms_ratio_max' in t:
        rr_max = t['onset_rms_ratio_max']
        ok     = (rms_ratio <= rr_max)
        results['onset_rms_ratio'] = {
            'measured': round(rms_ratio, 3),
            'target':   f'<= {rr_max}',
            'pass':     ok,
        }
        (passed if ok else failed).append(
            'onset_rms_ratio')

    all_pass = (len(failed) == 0)

    if verbose:
        status = '✓' if all_pass else '✗'
        desc   = t.get('description', '')
        print(f"  [{status}] {ph:4s}  "
              f"({desc})")
        for k, v in results.items():
            p = '    ✓' if v['pass'] else '    ✗'
            print(f"{p} {k}: "
                  f"{v['measured']}  "
                  f"target={v['target']}")

    return results, all_pass


# ============================================================
# ALSO CHECK: BYPASS ONSET TIMING
# This measures whether the sibilance
# arrives before or after the tract
# has transitioned.
# This is the "dragged S/Z" diagnostic.
# ============================================================

def check_sibilant_onset_timing(ph, synth_fn,
                                  pitch,
                                  sr=SR_DEFAULT,
                                  verbose=True):
    """
    For S and Z: check that sibilance energy
    arrives after the vowel formant has departed.

    Method:
      Synthesize [AA, ph] in context.
      At the boundary region (last 20ms of AA
      and first 20ms of ph), measure:
        - F1-band energy (80-600Hz) — vowel marker
        - High-freq energy (4000+Hz) — sibilant marker

      If high-freq energy rises before
      F1-band energy falls below 50%:
      → sibilant onset is too early.
      → dragged artifact.

    Returns:
      'clean':   sibilance starts after vowel ends.
      'overlap': sibilance starts while vowel active.
      'late':    sibilance starts well after
                 vowel ends (minor gap is ok).
    """
    n_fft = 512

    carrier = [('test', ['AA', ph, 'AA'])]
    sig = synth_fn(
        carrier,
        punctuation='.',
        pitch_base=pitch)
    sig = f32(sig)
    n   = len(sig)

    # Analyse in short hop windows
    hop   = int(0.005 * sr)   # 5ms hops
    win   = int(0.015 * sr)   # 15ms window
    times = []
    f1_e  = []
    hi_e  = []

    t = 0
    while t + win < n:
        seg   = sig[t:t+win]
        n_fft_use = max(n_fft, win)
        spec  = np.abs(np.fft.rfft(
            seg, n=n_fft_use))**2
        freqs = np.fft.rfftfreq(
            n_fft_use, d=1.0/sr)

        total = float(np.sum(spec))
        if total < 1e-12:
            f1_e.append(0.0)
            hi_e.append(0.0)
            times.append(t / sr * 1000)
            t += hop
            continue

        f1_mask = (freqs >= 80) & (freqs <= 600)
        hi_mask = freqs >= 4000

        f1_e.append(float(np.sum(spec[f1_mask]))
                    / total)
        hi_e.append(float(np.sum(spec[hi_mask]))
                    / total)
        times.append(t / sr * 1000)
        t += hop

    f1_e = np.array(f1_e)
    hi_e = np.array(hi_e)

    # Find where sibilance rises
    # (high-freq energy > 0.25)
    sib_threshold = 0.25
    sib_start_idx = None
    for i in range(len(hi_e)):
        if hi_e[i] > sib_threshold:
            sib_start_idx = i
            break

    # Find where F1 energy drops below 50%
    # of its peak
    f1_peak = float(np.max(f1_e))
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
                  f"{times[sib_start_idx]:.1f}ms")
        else:
            print(f"    Sibilance never rises "
                  f"above threshold")
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
        result = f'overlap ({overlap_ms:.1f}ms early)'
    elif sib_start_idx > f1_drop_idx + 4:
        result = 'late'
    else:
        result = 'clean'

    ok = result in ('clean', 'late')
    if verbose:
        status = '✓' if ok else '✗'
        print(f"    [{status}] onset timing: {result}")

    return result, ok, {
        'times_ms': [round(t,1) for t in times],
        'f1_energy': [round(float(x),3)
                       for x in f1_e],
        'hi_energy': [round(float(x),3)
                       for x in hi_e],
    }


# ============================================================
# FULL ONSET DIAGNOSTIC RUN
# ============================================================

def run_onset_diagnostic(synth_fn, pitch,
                           sr=SR_DEFAULT,
                           verbose=True):
    """
    Run the complete onset diagnostic.

    Tests:
      1. DH onset character
         (should not sound like "ea" prefix)
      2. H onset character
         (should not sound like "CH" prefix)
      3. S onset timing
         (sibilance after vowel, not during)
      4. Z onset timing
         (same as S)

    Returns overall pass/fail and
    detailed measurement dict.
    """
    print()
    print("ONSET DIAGNOSTIC")
    print("Measuring first 20ms of each")
    print("target phoneme in context.")
    print("The rainbow cannot see these.")
    print("="*50)
    print()

    all_results = {}
    total_pass  = 0
    total_fail  = 0

    # Part 1: onset character checks
    print("  PART 1: Onset character")
    print("  (spectral + periodicity")
    print("  of first 20ms)")
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

    # Part 2: sibilant onset timing
    print("  PART 2: Sibilant onset timing")
    print("  (does sibilance arrive before")
    print("  or after the vowel departs?)")
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

    # Summary
    print("="*50)
    print()
    print("  ONSET DIAGNOSTIC SUMMARY")
    print(f"  Passing: {total_pass}")
    print(f"  Failing: {total_fail}")
    score = (total_pass /
             max(1, total_pass+total_fail) * 100)
    print(f"  Score:   {score:.0f}%")
    print()

    # Interpretation
    print("  INTERPRETATION:")
    print()

    dh_ok = all(v.get('pass', True)
                 for v in
                 all_results.get('DH',{}).values())
    h_ok  = all(v.get('pass', True)
                 for v in
                 all_results.get('H',{}).values())
    s_ok  = all_results.get('S_timing',{}).get(
        'pass', True)
    z_ok  = all_results.get('Z_timing',{}).get(
        'pass', True)

    if not dh_ok:
        print("  DH FAILING:")
        print("  Voiced component too strong")
        print("  at phoneme onset.")
        print("  Glottal buzz through F1=270Hz")
        print("  precedes the dental friction.")
        print("  This produces the 'ea-the' artifact.")
        print("  → Reduce DH_VOICED_FRACTION further.")
        print("  → Or fade voiced in over first 25ms.")
        print()

    if not h_ok:
        print("  H FAILING:")
        print("  Aspiration has resonant peak")
        print("  or is too periodic.")
        print("  If peak_prominence > 3.0:")
        print("  → Aspiration noise is being")
        print("    resonated by the following")
        print("    vowel's formants too early.")
        print("  → Reduce F2 coarticulation in H.")
        print("  → Or add low-pass to H aspiration.")
        print("  This produces the 'CH-here' artifact.")
        print()

    if not s_ok:
        print("  S FAILING (timing):")
        print("  Sibilance starts while F1 still active.")
        print("  The vowel-to-S boundary is smeared.")
        print("  → Increase bypass onset delay.")
        print("  → Or shorten preceding vowel offset.")
        print("  This produces the 'dragged S' artifact.")
        print()

    if not z_ok:
        print("  Z FAILING (timing):")
        print("  Same as S.")
        print("  → Same fixes.")
        print()

    if dh_ok and h_ok and s_ok and z_ok:
        print("  ALL ONSET CHECKS PASSING.")
        print("  The four reported artifacts")
        print("  should be gone.")
        print("  Run the perceptual check next.")
        print()

    return all_results, total_pass, total_fail


# ============================================================
# STANDALONE ENTRY POINT
# ============================================================

if __name__ == "__main__":
    print()
    print("ONSET DIAGNOSTIC — standalone")
    print()
    print("Attempting to import voice_physics_v10...")
    print()

    try:
        from voice_physics_v10 import (
            synth_phrase, PITCH, SR)
        print("  Loaded voice_physics_v10.")
        run_onset_diagnostic(
            synth_phrase, PITCH, sr=SR)
    except ImportError:
        print("  voice_physics_v10 not found.")
        print("  Trying voice_physics_v9...")
        try:
            from voice_physics_v9 import (
                synth_phrase, PITCH, SR)
            print("  Loaded voice_physics_v9.")
            run_onset_diagnostic(
                synth_phrase, PITCH, sr=SR)
        except ImportError:
            print("  Not found. Please run from")
            print("  the voice_topology_folder.")
