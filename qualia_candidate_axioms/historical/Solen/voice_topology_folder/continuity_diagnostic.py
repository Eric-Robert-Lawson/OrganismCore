"""
CONTINUITY DIAGNOSTIC — rev3
February 2026

FIXES FROM rev2 RESULTS:

  BUG: ph→AA boundary was measuring
  the phrase-level release envelope
  (55ms fade-out at end of signal),
  not the actual phoneme→vowel transition.
  Result: every ph→AA IS_ratio was 200-8000×.
  Even AA→AA measured 540×.
  All were measuring silence, not transitions.

  FIX: Two separate synthesis calls
  per phoneme.

    For AA→ph boundary:
      Synthesize [AA, ph]
      ph is last. AA→ph boundary is
      in the middle of the signal.
      Measure here.

    For ph→AA boundary:
      Synthesize [ph, AA]
      ph is first. ph→AA boundary is
      in the middle of the signal.
      Measure here.

  Neither boundary is near the phrase
  release envelope (55ms at end).
  The measurements are clean.

  Everything else from rev2 preserved.
"""

import numpy as np
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
# IDENTITY TARGETS
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
            'periodicity > 0.15 = voiced leaking.'
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
            'Near-zero periodicity.'
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
            'V: voiced labiodental friction. '
            'Centroid 500-2500Hz. '
            'Moderate periodicity. '
            'f1_ratio > 0.5 = pure vowel, '
            'no friction = wrong.'
        ),
    },
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
        'notes': 'High front vowel. High F2.',
    },
}

PHRASE_ATK_MS      = 25
IS_RATIO_THRESHOLD = 10.0
AMPLITUDE_DB       = 6.0
CENTROID_JUMP_HZ   = 1500


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
    v = float(np.mean(r - np.log(r) - 1))
    return v if np.isfinite(v) else 999.0


def rms_val(seg):
    seg = f32(seg)
    if len(seg) == 0:
        return 0.0
    return float(np.sqrt(
        np.mean(seg**2) + 1e-12))


# ============================================================
# IS BASELINE
# ============================================================

_baseline_cache = {}

def get_baseline_is(sr=SR_D):
    if sr in _baseline_cache:
        return _baseline_cache[sr]

    sig = synth_phrase(
        [('b', ['AA', 'AA'])],
        punctuation='.',
        pitch_base=PITCH,
        dil=DIL, sr=sr)
    sig = f32(sig)
    n   = len(sig)

    atk_n   = int(PHRASE_ATK_MS/1000.0*sr)
    frame_n = int(0.020 * sr)
    hop_n   = int(0.010 * sr)

    is_vals = []
    pos = atk_n + frame_n
    while pos + frame_n < n - int(0.060*sr):
        seg_a = sig[pos-frame_n:pos]
        seg_b = sig[pos:pos+frame_n]
        sp_a, _ = get_spectrum(seg_a, sr)
        sp_b, _ = get_spectrum(seg_b, sr)
        if sp_a is not None and \
           sp_b is not None:
            n_min = min(len(sp_a),
                        len(sp_b))
            v = itakura_saito(
                sp_a[:n_min],
                sp_b[:n_min])
            if np.isfinite(v) and v < 900:
                is_vals.append(v)
        pos += hop_n

    baseline = float(np.median(is_vals)) \
               if is_vals else 1.0
    baseline = max(baseline, 0.1)
    _baseline_cache[sr] = baseline

    print(f"  IS baseline (AA body): "
          f"{baseline:.3f}")
    return baseline


# ============================================================
# FIND SINGLE BOUNDARY
#
# Used when the signal is [X, Y].
# Returns the sample position of the
# X→Y transition.
# Searches from phrase_atk+50ms to
# avoid the attack envelope.
# Stops before the last 60ms to avoid
# the release envelope.
# ============================================================

def find_single_boundary(sig, sr=SR_D):
    """
    Find the single transition point
    in a two-phoneme signal [A, B].

    Returns:
      boundary_sample: int
      valid: bool
    """
    sig   = f32(sig)
    n     = len(sig)
    hop_n = int(0.005 * sr)

    # Safe search region:
    # skip attack + 50ms at start
    # skip release + 10ms at end
    search_start = int(
        PHRASE_ATK_MS/1000.0*sr) + \
        int(0.050 * sr)
    search_end   = n - int(0.070 * sr)

    if search_start >= search_end:
        return n // 2, False

    # RMS envelope within search region
    env    = []
    frames = []
    i      = search_start
    while i + hop_n <= search_end:
        seg = sig[i:i+hop_n]
        env.append(rms_val(seg))
        frames.append(i)
        i += hop_n

    if not env:
        return n // 2, False

    env    = np.array(env)
    frames = np.array(frames)

    # Peak in the first half of the
    # search region = first phoneme body
    half   = len(env) // 2
    if half < 1:
        half = 1
    peak   = float(np.max(env[:half]))
    if peak < 1e-8:
        return n // 2, False

    threshold = peak * 0.50

    # Find where signal crosses threshold
    # (either up or down) = boundary
    # Look for the largest RMS change
    # between adjacent frames
    diffs  = np.abs(np.diff(env))
    if len(diffs) == 0:
        return n // 2, False

    max_idx = int(np.argmax(diffs))
    b_sample = int(frames[max_idx])

    return b_sample, True


# ============================================================
# MEASURE AT BOUNDARY
# ============================================================

def measure_at_boundary(sig, pos,
                         baseline_is,
                         sr=SR_D,
                         frame_ms=20):
    sig     = f32(sig)
    n       = len(sig)
    frame_n = int(frame_ms/1000.0*sr)

    seg_b = sig[max(0, pos-frame_n):pos]
    seg_a = sig[pos:min(n, pos+frame_n)]

    if len(seg_b) < 32 or len(seg_a) < 32:
        return None, None, None

    sp_b, _ = get_spectrum(seg_b, sr)
    sp_a, _ = get_spectrum(seg_a, sr)
    if sp_b is None or sp_a is None:
        return None, None, None

    n_min  = min(len(sp_b), len(sp_a))
    raw_is = itakura_saito(
        sp_b[:n_min], sp_a[:n_min])
    is_ratio = raw_is / max(baseline_is,
                             0.001)

    c_jump = abs(
        spectral_centroid(seg_a, sr) -
        spectral_centroid(seg_b, sr))

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
            print(f"  [--] {ph}")
        return {}, True

    # ph first, AH following
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
    body_e = min(body_e, n)
    if body_e <= body_s:
        body_e = min(body_s+int(0.020*sr), n)

    body = sig[body_s:body_e]

    c  = spectral_centroid(body, sr)
    p  = periodicity_measure(
        body, pitch_hz=PITCH, sr=sr)
    f1 = f1_band_ratio(body, sr=sr)

    results = {}
    failed  = []

    for key, measured, tgt, tol in [
        ('centroid',    c,  target['centroid_hz'],
                            target['centroid_tol']),
        ('periodicity', p,  target['periodicity'],
                            target['periodicity_tol']),
        ('f1_ratio',    f1, target['f1_ratio'],
                            target['f1_ratio_tol']),
    ]:
        ok = abs(measured - tgt) <= tol
        results[key] = {
            'measured':  round(measured, 3),
            'target':    tgt,
            'tolerance': tol,
            'distance':  round(
                abs(measured-tgt), 3),
            'pass':      ok,
        }
        if not ok:
            failed.append(key)

    all_pass = len(failed) == 0

    if verbose:
        st = '✓' if all_pass else '✗'
        print(f"  [{st}] {ph}")
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
# CONTINUITY CHECK — rev3
#
# Two separate synthesis calls.
# AA→ph: synthesize [AA, ph]
#        find boundary in middle.
# ph→AA: synthesize [ph, AA]
#        find boundary in middle.
# Neither boundary near phrase envelope.
# ============================================================

def check_continuity(
        ph, baseline_is,
        sr=SR_D, verbose=True):

    # ── AA → ph ───────────────────────────
    sig_in = synth_phrase(
        [('t', ['AA', ph])],
        punctuation='.',
        pitch_base=PITCH,
        dil=DIL, sr=sr)
    sig_in = f32(sig_in)

    b_in, valid_in = find_single_boundary(
        sig_in, sr=sr)
    isr1, cj1, adb1 = measure_at_boundary(
        sig_in, b_in, baseline_is, sr=sr)

    # ── ph → AA ───────────────────────────
    sig_out = synth_phrase(
        [('t', [ph, 'AA'])],
        punctuation='.',
        pitch_base=PITCH,
        dil=DIL, sr=sr)
    sig_out = f32(sig_out)

    b_out, valid_out = find_single_boundary(
        sig_out, sr=sr)
    isr2, cj2, adb2 = measure_at_boundary(
        sig_out, b_out, baseline_is, sr=sr)

    def make_r(isr, cj, adb):
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
            'centroid_jump_hz': round(cj, 0),
            'amplitude_db': round(adb, 1)
                if adb is not None else None,
            'is_pass': isr <= IS_RATIO_THRESHOLD,
            'centroid_pass':
                cj <= CENTROID_JUMP_HZ,
            'amplitude_pass':
                (abs(adb) <= AMPLITUDE_DB
                 if adb is not None
                 else False),
        }

    results = {
        'AA_to_ph': make_r(isr1, cj1, adb1),
        'ph_to_AA': make_r(isr2, cj2, adb2),
    }

    b1p = (results['AA_to_ph']['is_pass']
           and results['AA_to_ph']
           ['centroid_pass'])
    b2p = (results['ph_to_AA']['is_pass']
           and results['ph_to_AA']
           ['centroid_pass'])
    all_pass = b1p and b2p

    if verbose:
        st = '✓' if all_pass else '✗'
        vi = '✓' if valid_in else '?'
        vo = '✓' if valid_out else '?'
        print(f"  [{st}] {ph} continuity  "
              f"[in={vi} out={vo}]")
        for bname, bdata in results.items():
            arrow = ('AA→ph'
                     if bname == 'AA_to_ph'
                     else 'ph→AA')
            if bdata.get('error'):
                print(f"    [✗] {arrow}: "
                      f"measurement failed")
                continue
            bp = '✓' if (
                bdata['is_pass'] and
                bdata['centroid_pass']
            ) else '✗'
            print(f"    [{bp}] {arrow}")
            ip = '✓' if bdata['is_pass'] \
                 else '✗'
            cp = '✓' if bdata[
                'centroid_pass'] else '✗'
            ap = '✓' if bdata[
                'amplitude_pass'] else '✗'
            print(
                f"      [{ip}] IS_ratio="
                f"{bdata['is_ratio']}  "
                f"target<={IS_RATIO_THRESHOLD}")
            print(
                f"      [{cp}] centroid_jump="
                f"{bdata['centroid_jump_hz']}"
                f"Hz  target<={CENTROID_JUMP_HZ}")
            print(
                f"      [{ap}] amp="
                f"{bdata['amplitude_db']}dB"
                f"  target±{AMPLITUDE_DB}dB")

    return results, all_pass


# ============================================================
# FULL RUN
# ============================================================

def run_continuity_diagnostic(
        sr=SR_D, verbose=True):

    print()
    print("CONTINUITY DIAGNOSTIC rev3")
    print("Two synthesis calls per phoneme.")
    print("[AA,ph] for AA→ph boundary.")
    print("[ph,AA] for ph→AA boundary.")
    print("No phrase-envelope contamination.")
    print("="*50)

    TEST_PHS = list(
        PHONEME_IDENTITY_TARGETS.keys())

    print()
    print("  Computing IS baseline...")
    baseline_is = get_baseline_is(sr=sr)
    print(
        f"  Threshold = baseline × "
        f"{IS_RATIO_THRESHOLD} = "
        f"{baseline_is*IS_RATIO_THRESHOLD:.3f}")
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
    print(f"  Identity:   {pass_id}/{total_id}")
    print(f"  Continuity: {pass_ct}/{total_ct}")
    print()

    print("  IDENTITY FAILURES:")
    any_fail = False
    for ph, r in all_id.items():
        fails = [k for k, v in r.items()
                 if not v.get('pass', True)]
        if fails:
            any_fail = True
            print(f"    {ph}:")
            for k in fails:
                print(
                    f"      {k}: "
                    f"measured={r[k]['measured']}"
                    f"  target={r[k]['target']}"
                    f"  dist={r[k]['distance']}")
    if not any_fail:
        print("    All passing.")
    print()

    print("  CONTINUITY FAILURES:")
    any_fail = False
    for ph, r in all_ct.items():
        for bname, bdata in r.items():
            if bdata.get('error'):
                any_fail = True
                arrow = ('AA→ph'
                         if bname == 'AA_to_ph'
                         else 'ph→AA')
                print(f"    {ph} {arrow}: "
                      f"measurement failed")
                continue
            if bdata is None:
                continue
            fails = []
            if not bdata.get('is_pass', True):
                fails.append(
                    f"IS_ratio="
                    f"{bdata['is_ratio']}")
            if not bdata.get(
                    'centroid_pass', True):
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
