"""
CONTINUITY DIAGNOSTIC — rev2
February 2026

FIXES FROM rev1 RESULTS:

  BUG 1: Boundary detection found phrase
  attack fade-in instead of AA→ph boundary.
  All AA→ph measurements were empty.
  Fix: search for boundaries only AFTER
  phrase_atk + 50ms. The fade-in is
  over by then. The first real phoneme
  boundary is somewhere after that.

  BUG 2: Periodicity target was 0.70
  for vowels. Rosenberg pulse with harmonics
  measures 0.3-0.5 by autocorrelation.
  Target was calibrated for pure tones.
  Fix: lower vowel periodicity targets
  to 0.40. Consonant targets adjusted
  proportionally.

  BUG 3: IS threshold was 2.0.
  Real phoneme boundaries measure 100-10000.
  Within-phoneme IS is ~1-10.
  Fix: compute a BASELINE IS within the
  AA body itself, then express boundary
  IS as a ratio: boundary_IS / baseline_IS.
  A ratio > 10 = perceptibly discontinuous.
  A ratio < 5  = continuous enough.
  This is self-referential: the system
  calibrates its own continuity threshold
  against its own voiced output quality.

  BUG 4: amplitude_continuity returned nan
  when before-segment was empty.
  Fix: guard against empty segments.
"""

import numpy as np
from scipy.signal import lfilter, butter
import os

try:
    from voice_physics_v10 import (
        synth_phrase,
        PITCH, DIL, SR, f32,
    )
    print("  Loaded voice_physics_v10.")
except ImportError as e:
    print(f"  Import failed: {e}")
    raise

SR_D = SR

# ============================================================
# IDENTITY TARGETS — rev2
#
# Periodicity targets lowered to match
# Rosenberg pulse autocorrelation reality.
# ============================================================

PHONEME_IDENTITY_TARGETS = {

    'DH': {
        'centroid_hz':    2000,
        'centroid_tol':   1000,
        'periodicity':    0.30,
        'periodicity_tol': 0.20,
        'f1_ratio':       0.15,
        'f1_ratio_tol':   0.12,
        'notes': (
            'DH: partially voiced dental noise. '
            'Centroid 1000-3000Hz. '
            'Periodicity 0.1-0.5. '
            'Low F1 (not a vowel). '
            'centroid < 800Hz = tract dominating.'
        ),
    },

    'H': {
        'centroid_hz':    1200,
        'centroid_tol':    600,
        'periodicity':    0.05,
        'periodicity_tol': 0.10,
        'f1_ratio':       0.25,
        'f1_ratio_tol':   0.18,
        'notes': (
            'H: aperiodic aspiration. '
            'Centroid 600-1800Hz. '
            'Near-zero periodicity. '
            'periodicity > 0.15 = voiced leaking in.'
        ),
    },

    'S': {
        'centroid_hz':    7000,
        'centroid_tol':   2500,
        'periodicity':    0.02,
        'periodicity_tol': 0.08,
        'f1_ratio':       0.02,
        'f1_ratio_tol':   0.04,
        'notes': (
            'S: high-freq noise 5000-9000Hz. '
            'Near-zero periodicity. '
            'periodicity > 0.10 = voiced leaking.'
        ),
    },

    'Z': {
        'centroid_hz':    5000,
        'centroid_tol':   2500,
        'periodicity':    0.25,
        'periodicity_tol': 0.20,
        'f1_ratio':       0.08,
        'f1_ratio_tol':   0.08,
        'notes': (
            'Z: voiced sibilance. '
            'Centroid 2500-7500Hz. '
            'Mixed periodicity 0.1-0.45. '
            'centroid < 2000Hz = buzz dominating.'
        ),
    },

    'V': {
        'centroid_hz':    1500,
        'centroid_tol':   1000,
        'periodicity':    0.30,
        'periodicity_tol': 0.20,
        'f1_ratio':       0.20,
        'f1_ratio_tol':   0.15,
        'notes': (
            'V: voiced labiodental. '
            'Lower centroid than F. '
            'Moderate periodicity.'
        ),
    },

    # Vowels — periodicity target 0.40
    # (Rosenberg pulse with harmonics
    #  measures ~0.35-0.55 by lag-T0
    #  autocorrelation)
    'AH': {
        'centroid_hz':    900,
        'centroid_tol':   500,
        'periodicity':    0.40,
        'periodicity_tol': 0.20,
        'f1_ratio':       0.35,
        'f1_ratio_tol':   0.20,
        'notes': 'Mid-central vowel.',
    },
    'IH': {
        'centroid_hz':    1200,
        'centroid_tol':    600,
        'periodicity':    0.40,
        'periodicity_tol': 0.25,
        'f1_ratio':       0.20,
        'f1_ratio_tol':   0.18,
        'notes': 'High front vowel.',
    },
    'OY': {
        'centroid_hz':     800,
        'centroid_tol':    500,
        'periodicity':    0.40,
        'periodicity_tol': 0.20,
        'f1_ratio':       0.40,
        'f1_ratio_tol':   0.20,
        'notes': 'Diphthong.',
    },
    'AA': {
        'centroid_hz':     900,
        'centroid_tol':    500,
        'periodicity':    0.40,
        'periodicity_tol': 0.20,
        'f1_ratio':       0.45,
        'f1_ratio_tol':   0.20,
        'notes': 'Low back vowel.',
    },
    'AE': {
        'centroid_hz':    1000,
        'centroid_tol':    500,
        'periodicity':    0.40,
        'periodicity_tol': 0.20,
        'f1_ratio':       0.40,
        'f1_ratio_tol':   0.20,
        'notes': 'Low front vowel.',
    },
    'EH': {
        'centroid_hz':    1100,
        'centroid_tol':    600,
        'periodicity':    0.40,
        'periodicity_tol': 0.25,
        'f1_ratio':       0.30,
        'f1_ratio_tol':   0.20,
        'notes': 'Mid front vowel.',
    },
    'IY': {
        'centroid_hz':    1400,
        'centroid_tol':    700,
        'periodicity':    0.40,
        'periodicity_tol': 0.25,
        'f1_ratio':       0.15,
        'f1_ratio_tol':   0.15,
        'notes': 'High front vowel.',
    },
}

# ============================================================
# IS CONTINUITY THRESHOLD
#
# Expressed as a ratio over the
# within-AA baseline IS.
# AA body IS (frame-to-frame) is
# computed first as the baseline.
# Boundary IS / baseline IS:
#   < 5   = continuous
#   5-10  = marginal
#   > 10  = discontinuous
# ============================================================

IS_RATIO_THRESHOLD    = 10.0
AMPLITUDE_DB          = 6.0
CENTROID_JUMP_HZ      = 1500
PHRASE_ATK_MS         = 25


# ============================================================
# SPECTRAL UTILITIES
# ============================================================

def get_spectrum(seg, sr=SR_D):
    seg = f32(seg)
    n   = len(seg)
    if n < 32:
        return None, None
    n_fft = max(512, n)
    spec  = np.abs(
        np.fft.rfft(seg, n=n_fft))**2
    freqs = np.fft.rfftfreq(
        n_fft, d=1.0/sr)
    return spec, freqs


def spectral_centroid(seg, sr=SR_D):
    spec, freqs = get_spectrum(seg, sr)
    if spec is None:
        return 0.0
    total = float(np.sum(spec))
    if total < 1e-12:
        return 0.0
    return float(
        np.sum(freqs * spec) / total)


def periodicity_measure(seg,
                         pitch_hz=175,
                         sr=SR_D):
    seg = f32(seg)
    n   = len(seg)
    T0  = int(sr / max(pitch_hz, 50))
    if T0 >= n or n < 32:
        return 0.0
    r0 = float(np.sum(seg**2))
    r1 = float(np.sum(
        seg[:n-T0] * seg[T0:]))
    if r0 < 1e-12:
        return 0.0
    return max(0.0, min(1.0, r1/r0))


def f1_band_ratio(seg, sr=SR_D,
                   lo=80, hi=600):
    spec, freqs = get_spectrum(seg, sr)
    if spec is None:
        return 0.0
    total = float(np.sum(spec))
    if total < 1e-12:
        return 0.0
    mask = (freqs >= lo) & (freqs <= hi)
    return float(
        np.sum(spec[mask])) / total


def itakura_saito(spec_p, spec_q):
    p = np.maximum(
        np.array(spec_p, dtype=np.float64),
        1e-10)
    q = np.maximum(
        np.array(spec_q, dtype=np.float64),
        1e-10)
    r = p / q
    return float(np.mean(r - np.log(r) - 1))


def rms_val(seg):
    seg = f32(seg)
    if len(seg) == 0:
        return 0.0
    return float(np.sqrt(
        np.mean(seg**2) + 1e-12))


# ============================================================
# BASELINE IS
#
# Compute the typical IS divergence
# WITHIN the AA body — frame to frame.
# This is the natural floor.
# All boundary measurements are
# expressed as multiples of this floor.
# ============================================================

_baseline_is_cache = {}

def get_baseline_is(sr=SR_D):
    if sr in _baseline_is_cache:
        return _baseline_is_cache[sr]

    # Synthesize AA alone
    sig = synth_phrase(
        [('b', ['AA', 'AA'])],
        punctuation='.',
        pitch_base=PITCH,
        dil=DIL, sr=sr)
    sig = f32(sig)
    n   = len(sig)

    atk_n    = int(PHRASE_ATK_MS/1000.0*sr)
    frame_n  = int(0.020 * sr)
    hop_n    = int(0.010 * sr)

    # Measure IS between adjacent frames
    # inside the AA body
    is_vals = []
    pos = atk_n + frame_n
    while pos + frame_n < n - frame_n:
        seg_a = sig[pos-frame_n : pos]
        seg_b = sig[pos : pos+frame_n]
        sp_a, _ = get_spectrum(seg_a, sr)
        sp_b, _ = get_spectrum(seg_b, sr)
        if sp_a is not None and \
           sp_b is not None:
            n_min = min(len(sp_a), len(sp_b))
            v = itakura_saito(
                sp_a[:n_min],
                sp_b[:n_min])
            if np.isfinite(v):
                is_vals.append(v)
        pos += hop_n

    if not is_vals:
        baseline = 1.0
    else:
        baseline = float(np.median(is_vals))
        baseline = max(baseline, 0.1)

    _baseline_is_cache[sr] = baseline
    print(f"  IS baseline (AA body): "
          f"{baseline:.3f}")
    return baseline


# ============================================================
# BOUNDARY DETECTION — rev2
#
# Fixed: skip phrase_atk zone.
# Search starts at atk_n + 50ms.
# ============================================================

def find_boundaries(sig, sr=SR_D):
    """
    Find AA→ph and ph→AA boundary positions.

    Strategy:
      Compute RMS envelope.
      Skip the phrase attack zone.
      Find the peak RMS in the first
      third of the signal (= AA body).
      Find where RMS drops to < 50%
      of that peak = AA→ph boundary.
      Find where RMS recovers to > 50%
      of the FINAL AA peak = ph→AA boundary.

    Returns:
      b1: AA→ph boundary sample
      b2: ph→AA boundary sample
      valid: bool
    """
    sig    = f32(sig)
    n      = len(sig)
    hop_ms = 5
    hop_n  = int(hop_ms / 1000.0 * sr)

    # Skip phrase attack
    atk_n    = int(
        PHRASE_ATK_MS / 1000.0 * sr)
    skip_n   = atk_n + int(0.050 * sr)

    # RMS envelope
    env    = []
    frames = []
    i      = 0
    while i + hop_n <= n:
        seg = sig[i:i+hop_n]
        env.append(rms_val(seg))
        frames.append(i)
        i += hop_n
    env    = np.array(env)
    frames = np.array(frames)

    if len(env) < 4:
        return n//3, 2*n//3, False

    # First third = AA region
    first_third = len(env) // 3
    skip_frame  = 0
    for fi, fs in enumerate(frames):
        if fs >= skip_n:
            skip_frame = fi
            break

    aa_env = env[skip_frame:first_third]
    if len(aa_env) == 0:
        aa_env = env[skip_frame:]
    if len(aa_env) == 0:
        return n//3, 2*n//3, False

    aa_peak = float(np.max(aa_env))
    if aa_peak < 1e-8:
        return n//3, 2*n//3, False

    threshold = aa_peak * 0.50

    # Find b1: first drop below threshold
    # after skip_frame
    b1_frame = None
    for fi in range(skip_frame, len(env)):
        if env[fi] < threshold:
            b1_frame = fi
            break

    # Last third = final AA region
    last_third_start = 2 * len(env) // 3
    final_aa_env = env[last_third_start:]
    if len(final_aa_env) == 0:
        final_aa_peak = aa_peak
    else:
        final_aa_peak = float(
            np.max(final_aa_env))
    final_threshold = (
        max(final_aa_peak, aa_peak) * 0.50)

    # Find b2: last point below threshold
    # before the final AA recovery
    b2_frame = None
    for fi in range(len(env)-1,
                     last_third_start, -1):
        if env[fi] < final_threshold:
            b2_frame = fi
            break

    if b1_frame is None:
        b1 = n // 3
    else:
        b1 = int(frames[b1_frame])

    if b2_frame is None:
        b2 = 2 * n // 3
    else:
        b2 = int(frames[b2_frame])

    if b1 >= b2:
        b1 = n // 3
        b2 = 2 * n // 3

    return b1, b2, True


def measure_boundary(sig, pos,
                      baseline_is,
                      sr=SR_D,
                      frame_ms=20):
    """
    Measure spectral and amplitude
    discontinuity at pos.
    Returns IS ratio, centroid jump, amp dB.
    """
    sig     = f32(sig)
    n       = len(sig)
    frame_n = int(frame_ms/1000.0*sr)

    b_start = max(0, pos - frame_n)
    b_end   = pos
    a_start = pos
    a_end   = min(n, pos + frame_n)

    seg_b = sig[b_start:b_end]
    seg_a = sig[a_start:a_end]

    if len(seg_b) < 32 or len(seg_a) < 32:
        return None, None, None

    sp_b, _ = get_spectrum(seg_b, sr)
    sp_a, _ = get_spectrum(seg_a, sr)
    if sp_b is None or sp_a is None:
        return None, None, None

    n_min  = min(len(sp_b), len(sp_a))
    raw_is = itakura_saito(
        sp_b[:n_min], sp_a[:n_min])

    if not np.isfinite(raw_is):
        return None, None, None

    is_ratio = raw_is / max(baseline_is,
                             0.001)

    c_b = spectral_centroid(seg_b, sr)
    c_a = spectral_centroid(seg_a, sr)
    c_jump = abs(c_a - c_b)

    rms_b = rms_val(seg_b)
    rms_a = rms_val(seg_a)
    if rms_b < 1e-8:
        amp_db = None
    else:
        amp_db = 20 * np.log10(
            max(rms_a/rms_b, 1e-6))

    return is_ratio, c_jump, amp_db


# ============================================================
# PHONEME IDENTITY CHECK
# ============================================================

def check_phoneme_identity(
        ph, sr=SR_D, verbose=True):

    target = PHONEME_IDENTITY_TARGETS.get(ph)
    if target is None:
        if verbose:
            print(f"  [--] {ph}: "
                  f"no identity targets")
        return {}, True

    # Synthesize ph first, AH following
    sig = synth_phrase(
        [('t', [ph, 'AH'])],
        punctuation='.',
        pitch_base=PITCH,
        dil=DIL, sr=sr)
    sig = f32(sig)
    n   = len(sig)

    atk_n  = int(PHRASE_ATK_MS/1000.0*sr)
    body_s = atk_n + int(0.020*sr)
    body_e = atk_n + int(0.060*sr)
    body_s = min(body_s, n-1)
    body_e = min(body_e, n)
    if body_e <= body_s:
        body_e = min(body_s + int(0.020*sr), n)

    body = sig[body_s:body_e]

    c  = spectral_centroid(body, sr)
    p  = periodicity_measure(
        body, pitch_hz=PITCH, sr=sr)
    f1 = f1_band_ratio(body, sr=sr)

    results = {}
    failed  = []

    c_tgt = target['centroid_hz']
    c_tol = target['centroid_tol']
    c_ok  = abs(c - c_tgt) <= c_tol
    results['centroid'] = {
        'measured':  round(c, 0),
        'target':    c_tgt,
        'tolerance': c_tol,
        'distance':  round(abs(c-c_tgt), 0),
        'pass':      c_ok,
    }
    if not c_ok:
        failed.append('centroid')

    p_tgt = target['periodicity']
    p_tol = target['periodicity_tol']
    p_ok  = abs(p - p_tgt) <= p_tol
    results['periodicity'] = {
        'measured':  round(p, 3),
        'target':    p_tgt,
        'tolerance': p_tol,
        'distance':  round(abs(p-p_tgt), 3),
        'pass':      p_ok,
    }
    if not p_ok:
        failed.append('periodicity')

    f_tgt = target['f1_ratio']
    f_tol = target['f1_ratio_tol']
    f_ok  = abs(f1 - f_tgt) <= f_tol
    results['f1_ratio'] = {
        'measured':  round(f1, 3),
        'target':    f_tgt,
        'tolerance': f_tol,
        'distance':  round(abs(f1-f_tgt), 3),
        'pass':      f_ok,
    }
    if not f_ok:
        failed.append('f1_ratio')

    all_pass = len(failed) == 0

    if verbose:
        status = '✓' if all_pass else '✗'
        print(f"  [{status}] {ph}")
        for k, v in results.items():
            ps = '    ✓' if v['pass'] \
                 else '    ✗'
            print(
                f"{ps} {k}: "
                f"{v['measured']}  "
                f"target={v['target']}"
                f"±{v['tolerance']}  "
                f"dist={v['distance']}")
        if not all_pass:
            print(f"       "
                  f"{target['notes']}")

    return results, all_pass


# ============================================================
# CONTINUITY CHECK
# ============================================================

def check_continuity(
        ph, baseline_is,
        sr=SR_D, verbose=True):

    sig = synth_phrase(
        [('t', ['AA', ph, 'AA'])],
        punctuation='.',
        pitch_base=PITCH,
        dil=DIL, sr=sr)
    sig = f32(sig)

    b1, b2, valid = find_boundaries(
        sig, sr=sr)

    isr1, cj1, adb1 = measure_boundary(
        sig, b1, baseline_is, sr=sr)
    isr2, cj2, adb2 = measure_boundary(
        sig, b2, baseline_is, sr=sr)

    def make_result(isr, cj, adb):
        if isr is None:
            return {
                'is_ratio': None,
                'centroid_jump_hz': None,
                'amplitude_db': None,
                'is_pass': False,
                'centroid_pass': False,
                'amplitude_pass': False,
                'error': 'measurement_failed',
            }
        return {
            'is_ratio': round(isr, 2),
            'centroid_jump_hz':
                round(cj, 0) if cj else None,
            'amplitude_db':
                round(adb, 1)
                if adb is not None else None,
            'is_pass':
                isr <= IS_RATIO_THRESHOLD,
            'centroid_pass':
                (cj <= CENTROID_JUMP_HZ
                 if cj is not None else False),
            'amplitude_pass':
                (abs(adb) <= AMPLITUDE_DB
                 if adb is not None else False),
        }

    results = {
        'AA_to_ph': make_result(
            isr1, cj1, adb1),
        'ph_to_AA': make_result(
            isr2, cj2, adb2),
        'boundary_valid': valid,
    }

    b1_pass = (
        results['AA_to_ph']['is_pass'] and
        results['AA_to_ph']['centroid_pass'])
    b2_pass = (
        results['ph_to_AA']['is_pass'] and
        results['ph_to_AA']['centroid_pass'])
    all_pass = b1_pass and b2_pass

    if verbose:
        status = '✓' if all_pass else '✗'
        bv     = '✓' if valid else '?'
        print(f"  [{status}] {ph} "
              f"continuity  "
              f"[boundary_detect={bv}]")
        for bname, bdata in results.items():
            if bname == 'boundary_valid':
                continue
            arrow = ('AA→ph'
                     if bname == 'AA_to_ph'
                     else 'ph→AA')
            if bdata.get('error'):
                print(f"    [✗] {arrow}: "
                      f"measurement failed")
                continue
            bp = '✓' if (
                bdata['is_pass'] and
                bdata['centroid_pass']) \
                else '✗'
            print(f"    [{bp}] {arrow}")
            ip = '✓' if bdata['is_pass'] \
                 else '✗'
            cp = '✓' if bdata[
                'centroid_pass'] else '✗'
            ap = '✓' if bdata[
                'amplitude_pass'] else '✗'
            print(
                f"      [{ip}] "
                f"IS_ratio="
                f"{bdata['is_ratio']}  "
                f"target<={IS_RATIO_THRESHOLD}")
            print(
                f"      [{cp}] "
                f"centroid_jump="
                f"{bdata['centroid_jump_hz']}"
                f"Hz  "
                f"target<={CENTROID_JUMP_HZ}")
            print(
                f"      [{ap}] "
                f"amp="
                f"{bdata['amplitude_db']}dB"
                f"  target±{AMPLITUDE_DB}dB")

    return results, all_pass


# ============================================================
# FULL RUN
# ============================================================

def run_continuity_diagnostic(
        sr=SR_D, verbose=True):

    print()
    print("CONTINUITY DIAGNOSTIC rev2")
    print("Self-referential.")
    print("IS threshold relative to "
          "AA body baseline.")
    print("="*50)

    TEST_PHS = list(
        PHONEME_IDENTITY_TARGETS.keys())

    # Compute baseline IS first
    print()
    print("  Computing IS baseline...")
    baseline_is = get_baseline_is(sr=sr)
    print(f"  Threshold = baseline × "
          f"{IS_RATIO_THRESHOLD} = "
          f"{baseline_is * IS_RATIO_THRESHOLD:.3f}")
    print()

    total_id = pass_id = 0
    total_ct = pass_ct = 0
    all_id   = {}
    all_ct   = {}

    print("  PART 1: Phoneme identity")
    print()
    for ph in TEST_PHS:
        r, ok = check_phoneme_identity(
            ph, sr=sr, verbose=verbose)
        all_id[ph] = r
        total_id += 1
        if ok:
            pass_id += 1
        if verbose:
            print()

    print("  PART 2: Boundary continuity")
    print()
    for ph in TEST_PHS:
        r, ok = check_continuity(
            ph, baseline_is,
            sr=sr, verbose=verbose)
        all_ct[ph] = r
        total_ct += 1
        if ok:
            pass_ct += 1
        if verbose:
            print()

    print("="*50)
    print()
    print("  SUMMARY")
    print(f"  Identity:   "
          f"{pass_id}/{total_id}")
    print(f"  Continuity: "
          f"{pass_ct}/{total_ct}")
    print()

    print("  IDENTITY FAILURES:")
    any_fail = False
    for ph, r in all_id.items():
        fails = [
            k for k, v in r.items()
            if not v.get('pass', True)]
        if fails:
            any_fail = True
            print(f"    {ph}:")
            for k in fails:
                print(
                    f"      {k}: "
                    f"measured="
                    f"{r[k]['measured']}  "
                    f"target="
                    f"{r[k]['target']}  "
                    f"dist="
                    f"{r[k]['distance']}")
    if not any_fail:
        print("    All passing.")
    print()

    print("  CONTINUITY FAILURES:")
    any_fail = False
    for ph, r in all_ct.items():
        for bname, bdata in r.items():
            if bname == 'boundary_valid':
                continue
            if bdata.get('error'):
                any_fail = True
                arrow = ('AA→ph'
                         if bname == 'AA_to_ph'
                         else 'ph→AA')
                print(f"    {ph} {arrow}: "
                      f"measurement failed")
                continue
            fails = []
            if not bdata['is_pass']:
                fails.append(
                    f"IS_ratio="
                    f"{bdata['is_ratio']}")
            if not bdata['centroid_pass']:
                fails.append(
                    f"jump="
                    f"{bdata['centroid_jump_hz']}"
                    f"Hz")
            if fails:
                any_fail = True
                arrow = ('AA→ph'
                         if bname == 'AA_to_ph'
                         else 'ph→AA')
                print(f"    {ph} {arrow}: "
                      f"{', '.join(fails)}")
    if not any_fail:
        print("    All passing.")
    print()

    return (all_id, all_ct,
            pass_id, total_id,
            pass_ct, total_ct)


if __name__ == "__main__":
    run_continuity_diagnostic(sr=SR)
