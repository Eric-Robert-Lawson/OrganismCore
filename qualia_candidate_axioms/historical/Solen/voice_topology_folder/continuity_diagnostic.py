"""
CONTINUITY DIAGNOSTIC
February 2026

WHAT THIS MEASURES:

  The onset diagnostic measured whether
  each phoneme STARTED correctly.
  It passed. The starts are now correct.

  This diagnostic measures something
  different:

    1. PHONEME IDENTITY
       Does the phoneme sound like itself?
       Measured by comparing the spectral
       centroid, F1/F2 energy ratios, and
       periodicity of the phoneme body
       against known acoustic targets for
       that phoneme class.

    2. SPECTRAL CONTINUITY
       Is the phoneme spectrally continuous
       with its neighbors?
       Measured by computing the spectral
       distance between the END of the
       preceding phoneme and the START
       of the target phoneme, and between
       the END of the target phoneme and
       the START of the following phoneme.
       A large spectral distance = discontinuity
       = the artifact you are hearing.

    3. AMPLITUDE CONTINUITY
       Does the RMS envelope change smoothly
       across the phoneme boundary?
       A sudden drop to near-zero followed
       by a sudden rise = the "three objects"
       problem you identified.

THE RAINBOW CONNECTION:

  The rainbow passage was the original
  self-referential test. The system
  synthesized "the rainbow" and measured
  whether its own output matched acoustic
  targets derived from that specific text.

  This is the same principle:
    - Synthesize a known carrier
    - Measure the output against targets
    - The targets are derived from what
      the output SHOULD sound like
    - Report distance from target
    - Report pass/fail per phoneme

  The system tests itself.
  No external reference needed.
  The targets ARE the specification.

SPECTRAL DISTANCE METRIC:

  We use the Itakura-Saito divergence
  between adjacent 20ms spectral frames.
  This is a perceptually motivated metric
  — large IS distance = perceptually
  discontinuous. Small IS distance =
  smooth transition.

  IS(P||Q) = sum( P(f)/Q(f) - log(P(f)/Q(f)) - 1 )

  where P = spectrum of frame at boundary
        Q = spectrum of frame just before/after

  A perfectly continuous signal has IS ≈ 0.
  A discontinuous boundary has IS >> 1.
  Threshold for perceptible discontinuity: ~2.0

  We also use simple spectral centroid
  distance as a secondary metric because
  it is interpretable:
  |centroid_A - centroid_B| in Hz.
  > 1000Hz jump at a boundary is audible.

PHONEME IDENTITY TARGETS:

  These are acoustic targets for the
  body of each phoneme, derived from
  established formant tables and
  spectral characteristics.
  The system measures its own output
  against these targets and reports
  how far it is from being the
  correct phoneme.
"""

import numpy as np
from scipy.signal import lfilter, butter
import os

# ============================================================
# IMPORTS
# ============================================================

try:
    from voice_physics_v10 import (
        synth_phrase,
        PITCH, DIL, SR, f32,
    )
    print("  Loaded voice_physics_v10.")
except ImportError as e:
    print(f"  Import failed: {e}")
    raise

os.makedirs("output_play/diag", exist_ok=True)

SR_D = SR


# ============================================================
# PHONEME IDENTITY TARGETS
#
# What each phoneme body SHOULD measure.
# Derived from acoustic phonetics literature
# and the Hillenbrand et al. 1995 formant
# tables for American English.
#
# Each entry:
#   centroid_hz:   expected spectral centroid
#                  of the phoneme body in Hz
#   centroid_tol:  acceptable deviation in Hz
#   periodicity:   expected autocorrelation
#                  periodicity (0=noise, 1=voiced)
#   periodicity_tol: acceptable deviation
#   f1_ratio:      expected fraction of energy
#                  in F1 band (80-600Hz)
#   f1_ratio_tol:  acceptable deviation
#   notes:         what to look for
# ============================================================

PHONEME_IDENTITY_TARGETS = {

    # ── Voiced dental fricative ────────────
    'DH': {
        'centroid_hz':      2000,
        'centroid_tol':     1000,
        'periodicity':      0.35,
        'periodicity_tol':  0.20,
        'f1_ratio':         0.15,
        'f1_ratio_tol':     0.10,
        'notes': (
            'DH should be partially voiced '
            'noise centered ~1500-3000Hz. '
            'Periodicity 0.2-0.5 (mixed). '
            'Low F1 ratio (not a vowel). '
            'If periodicity < 0.1: '
            'pure noise, no voicing = wrong. '
            'If centroid < 800Hz: '
            'tract resonance dominating = wrong.'
        ),
    },

    # ── Aspirated glottal ─────────────────
    'H': {
        'centroid_hz':      1200,
        'centroid_tol':      600,
        'periodicity':      0.05,
        'periodicity_tol':  0.08,
        'f1_ratio':         0.25,
        'f1_ratio_tol':     0.15,
        'notes': (
            'H should be aperiodic aspiration '
            'shaped by following vowel formants. '
            'Centroid 800-1800Hz. '
            'Very low periodicity (pure noise). '
            'Moderate F1 ratio because the '
            'following vowel formants shape '
            'the aspiration. '
            'If centroid > 3000Hz: '
            'aspiration too bright = wrong. '
            'If f1_ratio < 0.05: '
            'aspiration not vowel-shaped = wrong.'
        ),
    },

    # ── Alveolar sibilant ─────────────────
    'S': {
        'centroid_hz':      7000,
        'centroid_tol':     2000,
        'periodicity':      0.02,
        'periodicity_tol':  0.05,
        'f1_ratio':         0.02,
        'f1_ratio_tol':     0.03,
        'notes': (
            'S should be high-frequency noise '
            'centered 5000-9000Hz. '
            'Near-zero periodicity (pure noise). '
            'Near-zero F1 ratio (no low energy). '
            'If centroid < 4000Hz: '
            'S sounds like SH = wrong. '
            'If periodicity > 0.1: '
            'voiced harmonic leaking into S.'
        ),
    },

    # ── Voiced alveolar sibilant ──────────
    'Z': {
        'centroid_hz':      5000,
        'centroid_tol':     2000,
        'periodicity':      0.25,
        'periodicity_tol':  0.15,
        'f1_ratio':         0.08,
        'f1_ratio_tol':     0.06,
        'notes': (
            'Z should be voiced sibilance: '
            'noise at 5000-7000Hz PLUS '
            'voiced buzz below 1000Hz. '
            'Periodicity 0.15-0.40 (mixed). '
            'Small but nonzero F1 ratio. '
            'If periodicity < 0.05: '
            'Z sounds like S = wrong. '
            'If centroid < 3000Hz: '
            'buzz dominating, no sibilance.'
        ),
    },

    # ── Voiced labiodental ────────────────
    'V': {
        'centroid_hz':      1500,
        'centroid_tol':      800,
        'periodicity':      0.30,
        'periodicity_tol':  0.15,
        'f1_ratio':         0.20,
        'f1_ratio_tol':     0.12,
        'notes': (
            'V is voiced labiodental friction. '
            'Lower centroid than F. '
            'Moderate periodicity. '
        ),
    },

    # ── Vowels ────────────────────────────
    'AH': {
        'centroid_hz':       900,
        'centroid_tol':      400,
        'periodicity':      0.70,
        'periodicity_tol':  0.15,
        'f1_ratio':         0.35,
        'f1_ratio_tol':     0.15,
        'notes': 'Mid-central vowel. High periodicity.',
    },
    'IH': {
        'centroid_hz':      1200,
        'centroid_tol':      500,
        'periodicity':      0.70,
        'periodicity_tol':  0.15,
        'f1_ratio':         0.20,
        'f1_ratio_tol':     0.12,
        'notes': 'High front vowel. High periodicity.',
    },
    'OY': {
        'centroid_hz':       800,
        'centroid_tol':      400,
        'periodicity':      0.70,
        'periodicity_tol':  0.15,
        'f1_ratio':         0.40,
        'f1_ratio_tol':     0.15,
        'notes': 'Diphthong. High periodicity.',
    },
    'AA': {
        'centroid_hz':       900,
        'centroid_tol':      400,
        'periodicity':      0.70,
        'periodicity_tol':  0.15,
        'f1_ratio':         0.45,
        'f1_ratio_tol':     0.15,
        'notes': 'Low back vowel. High F1.',
    },
    'AE': {
        'centroid_hz':      1000,
        'centroid_tol':      400,
        'periodicity':      0.70,
        'periodicity_tol':  0.15,
        'f1_ratio':         0.40,
        'f1_ratio_tol':     0.15,
        'notes': 'Low front vowel.',
    },
    'EH': {
        'centroid_hz':      1100,
        'centroid_tol':      500,
        'periodicity':      0.70,
        'periodicity_tol':  0.15,
        'f1_ratio':         0.30,
        'f1_ratio_tol':     0.15,
        'notes': 'Mid front vowel.',
    },
    'IY': {
        'centroid_hz':      1400,
        'centroid_tol':      600,
        'periodicity':      0.70,
        'periodicity_tol':  0.15,
        'f1_ratio':         0.15,
        'f1_ratio_tol':     0.12,
        'notes': 'High front vowel. High F2.',
    },
}


# ============================================================
# SPECTRAL UTILITIES
# ============================================================

def get_spectrum(seg, sr=SR_D):
    seg   = f32(seg)
    n     = len(seg)
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


def periodicity(seg, pitch_hz=175,
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
    """
    Itakura-Saito divergence.
    Perceptually motivated spectral
    distance. Large value = discontinuous.
    Both spectra must be same length
    and positive.
    """
    p = np.array(spec_p, dtype=np.float64)
    q = np.array(spec_q, dtype=np.float64)
    # Floor to prevent log(0)
    p = np.maximum(p, 1e-10)
    q = np.maximum(q, 1e-10)
    r = p / q
    return float(np.mean(
        r - np.log(r) - 1.0))


def spectral_distance_at_boundary(
        sig, boundary_sample,
        frame_ms=20, sr=SR_D):
    """
    Measure spectral discontinuity
    at a boundary sample position.

    Computes:
      frame_before: the frame_ms window
                    ending at boundary_sample
      frame_after:  the frame_ms window
                    starting at boundary_sample

    Returns:
      is_div:      Itakura-Saito divergence
      centroid_jump: |centroid_before -
                      centroid_after| in Hz
    """
    sig    = f32(sig)
    n      = len(sig)
    n_frame = int(frame_ms / 1000.0 * sr)

    before_start = max(0,
        boundary_sample - n_frame)
    before_end   = boundary_sample
    after_start  = boundary_sample
    after_end    = min(n,
        boundary_sample + n_frame)

    if (before_end <= before_start or
            after_end <= after_start):
        return 999.0, 999.0

    seg_b = sig[before_start:before_end]
    seg_a = sig[after_start:after_end]

    spec_b, _ = get_spectrum(seg_b, sr)
    spec_a, _ = get_spectrum(seg_a, sr)

    if spec_b is None or spec_a is None:
        return 999.0, 999.0

    # Align lengths
    n_min = min(len(spec_b), len(spec_a))
    spec_b = spec_b[:n_min]
    spec_a = spec_a[:n_min]

    is_div = itakura_saito(spec_b, spec_a)

    c_b = spectral_centroid(seg_b, sr)
    c_a = spectral_centroid(seg_a, sr)
    c_jump = abs(c_a - c_b)

    return is_div, c_jump


def rms_envelope(sig, hop_ms=5,
                  sr=SR_D):
    """
    RMS envelope of signal.
    Returns array of RMS values,
    one per hop_ms window.
    """
    sig   = f32(sig)
    hop_n = int(hop_ms / 1000.0 * sr)
    n     = len(sig)
    out   = []
    i     = 0
    while i + hop_n <= n:
        seg = sig[i:i+hop_n]
        out.append(float(np.sqrt(
            np.mean(seg**2) + 1e-12)))
        i += hop_n
    return np.array(out)


def amplitude_continuity(
        sig, boundary_sample,
        frame_ms=20, sr=SR_D):
    """
    Measure amplitude discontinuity
    at boundary_sample.
    Returns ratio of RMS after/before.
    1.0 = perfectly continuous.
    >> 1 or << 1 = discontinuous.
    We express as dB deviation from 1.0:
    0dB = continuous.
    Large magnitude = discontinuous.
    """
    sig    = f32(sig)
    n      = len(sig)
    n_frame = int(frame_ms / 1000.0 * sr)

    before = sig[
        max(0, boundary_sample-n_frame):
        boundary_sample]
    after  = sig[
        boundary_sample:
        min(n, boundary_sample+n_frame)]

    rms_b = float(np.sqrt(
        np.mean(before**2) + 1e-12))
    rms_a = float(np.sqrt(
        np.mean(after**2) + 1e-12))

    if rms_b < 1e-8:
        return 999.0
    ratio = rms_a / rms_b
    db    = 20 * np.log10(
        max(ratio, 1e-6))
    return db


# ============================================================
# PHONEME BODY EXTRACTOR
#
# Synthesizes [AA, ph, AA] and
# estimates where the ph body is.
# Uses the same method as the onset
# diagnostic: ph is synthesized FIRST
# so its onset is at phrase_atk.
# Then the body is measured.
# ============================================================

PHRASE_ATK_MS = 25  # matches synth_phrase

def get_phoneme_body(ph, sr=SR_D,
                      body_start_ms=None,
                      body_end_ms=None):
    """
    Synthesize [ph, AH] with ph first.
    Extract the body segment.
    body_start_ms: ms after phrase_atk
                   where body begins.
                   Default: 20ms (onset end).
    body_end_ms:   ms after phrase_atk
                   where body ends.
                   Default: 60ms.
    Returns:
      sig:         full signal
      body:        body segment
      body_s:      body start sample
      body_e:      body end sample
    """
    sig = synth_phrase(
        [('test', [ph, 'AH'])],
        punctuation='.',
        pitch_base=PITCH,
        dil=DIL,
        sr=sr)
    sig = f32(sig)
    n   = len(sig)

    onset_s = int(
        PHRASE_ATK_MS / 1000.0 * sr)

    if body_start_ms is None:
        body_start_ms = 20.0
    if body_end_ms is None:
        body_end_ms   = 60.0

    body_s = onset_s + int(
        body_start_ms / 1000.0 * sr)
    body_e = onset_s + int(
        body_end_ms   / 1000.0 * sr)
    body_s = min(body_s, n-1)
    body_e = min(body_e, n)

    if body_e <= body_s:
        body_e = min(body_s + int(
            0.020*sr), n)

    return sig, sig[body_s:body_e], \
           body_s, body_e


# ============================================================
# PHONEME IDENTITY CHECK
# ============================================================

def check_phoneme_identity(
        ph, sr=SR_D, verbose=True):
    """
    Synthesize ph and measure whether
    it sounds like itself.
    Compare body measurements against
    PHONEME_IDENTITY_TARGETS.
    """
    target = PHONEME_IDENTITY_TARGETS.get(ph)
    if target is None:
        if verbose:
            print(f"  [--] {ph}: "
                  f"no identity targets")
        return {}, True

    sig, body, body_s, body_e = \
        get_phoneme_body(ph, sr=sr)

    c  = spectral_centroid(body, sr)
    p  = periodicity(body,
                     pitch_hz=PITCH, sr=sr)
    f1 = f1_band_ratio(body, sr=sr)

    results = {}
    failed  = []

    # Centroid
    c_tgt = target['centroid_hz']
    c_tol = target['centroid_tol']
    c_ok  = abs(c - c_tgt) <= c_tol
    results['centroid'] = {
        'measured': round(c, 0),
        'target':   c_tgt,
        'tolerance': c_tol,
        'distance': round(abs(c-c_tgt), 0),
        'pass':     c_ok,
    }
    if not c_ok:
        failed.append('centroid')

    # Periodicity
    p_tgt = target['periodicity']
    p_tol = target['periodicity_tol']
    p_ok  = abs(p - p_tgt) <= p_tol
    results['periodicity'] = {
        'measured': round(p, 3),
        'target':   p_tgt,
        'tolerance': p_tol,
        'distance': round(abs(p-p_tgt), 3),
        'pass':     p_ok,
    }
    if not p_ok:
        failed.append('periodicity')

    # F1 ratio
    f_tgt = target['f1_ratio']
    f_tol = target['f1_ratio_tol']
    f_ok  = abs(f1 - f_tgt) <= f_tol
    results['f1_ratio'] = {
        'measured': round(f1, 3),
        'target':   f_tgt,
        'tolerance': f_tol,
        'distance': round(abs(f1-f_tgt), 3),
        'pass':     f_ok,
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
            print(f"{ps} {k}: "
                  f"{v['measured']}  "
                  f"target={v['target']} "
                  f"±{v['tolerance']}  "
                  f"dist={v['distance']}")
        if not all_pass:
            print(f"       {target['notes']}")

    return results, all_pass


# ============================================================
# CONTINUITY CHECK
#
# Synthesize [AA, ph, AA].
# Find the boundary positions.
# Measure spectral and amplitude
# discontinuity at each boundary.
# ============================================================

# Thresholds for perceptible discontinuity
IS_THRESHOLD        = 2.0   # Itakura-Saito
CENTROID_JUMP_HZ    = 1000  # Hz
AMPLITUDE_DB        = 6.0   # dB


def check_continuity(
        ph, sr=SR_D, verbose=True):
    """
    Synthesize [AA, ph, AA].
    Measure continuity at:
      boundary 1: AA → ph
      boundary 2: ph → AA

    Reports:
      Spectral IS divergence at each boundary
      Spectral centroid jump at each boundary
      Amplitude RMS jump at each boundary

    A phoneme is continuous if all three
    measures are below threshold at both
    boundaries.
    """
    # Synthesize carrier
    sig = synth_phrase(
        [('test', ['AA', ph, 'AA'])],
        punctuation='.',
        pitch_base=PITCH,
        dil=DIL,
        sr=sr)
    sig = f32(sig)
    n   = len(sig)

    # Estimate boundary positions.
    # Use the RMS envelope to find where
    # amplitude changes significantly.
    # AA is voiced and loud.
    # If ph is noise/fricative it will
    # have a different amplitude.
    # Find the two transitions.

    hop_ms   = 5
    hop_n    = int(hop_ms / 1000.0 * sr)
    env      = rms_envelope(
        sig, hop_ms=hop_ms, sr=sr)
    n_frames = len(env)

    # Peak RMS (in AA region)
    peak_rms = float(np.max(env))

    # Find first dip below 50% of peak
    # = AA → ph transition
    b1_frame = None
    for i in range(n_frames):
        if env[i] < peak_rms * 0.50:
            b1_frame = i
            break

    # Find last dip below 50% of peak
    # = ph → AA transition
    b2_frame = None
    for i in range(n_frames-1, -1, -1):
        if env[i] < peak_rms * 0.50:
            b2_frame = i
            break

    # Convert to samples
    phrase_atk_n = int(
        PHRASE_ATK_MS / 1000.0 * sr)

    if b1_frame is None:
        b1_sample = n // 3
    else:
        b1_sample = b1_frame * hop_n

    if b2_frame is None:
        b2_sample = 2 * n // 3
    else:
        b2_sample = b2_frame * hop_n

    # Fallback: use fixed estimates
    # if RMS detection fails (e.g. for
    # phonemes with no amplitude dip)
    if b1_sample >= b2_sample:
        b1_sample = n // 3
        b2_sample = 2 * n // 3

    # Measure at boundary 1 (AA → ph)
    is1, cj1 = spectral_distance_at_boundary(
        sig, b1_sample, sr=sr)
    amp1 = amplitude_continuity(
        sig, b1_sample, sr=sr)

    # Measure at boundary 2 (ph → AA)
    is2, cj2 = spectral_distance_at_boundary(
        sig, b2_sample, sr=sr)
    amp2 = amplitude_continuity(
        sig, b2_sample, sr=sr)

    results = {
        'AA_to_ph': {
            'is_divergence':   round(is1, 3),
            'centroid_jump_hz': round(cj1, 0),
            'amplitude_db':    round(amp1, 1),
            'is_pass':
                is1  <= IS_THRESHOLD,
            'centroid_pass':
                cj1  <= CENTROID_JUMP_HZ,
            'amplitude_pass':
                abs(amp1) <= AMPLITUDE_DB,
        },
        'ph_to_AA': {
            'is_divergence':   round(is2, 3),
            'centroid_jump_hz': round(cj2, 0),
            'amplitude_db':    round(amp2, 1),
            'is_pass':
                is2  <= IS_THRESHOLD,
            'centroid_pass':
                cj2  <= CENTROID_JUMP_HZ,
            'amplitude_pass':
                abs(amp2) <= AMPLITUDE_DB,
        },
    }

    b1_pass = (
        results['AA_to_ph']['is_pass'] and
        results['AA_to_ph']['centroid_pass'] and
        results['AA_to_ph']['amplitude_pass'])
    b2_pass = (
        results['ph_to_AA']['is_pass'] and
        results['ph_to_AA']['centroid_pass'] and
        results['ph_to_AA']['amplitude_pass'])
    all_pass = b1_pass and b2_pass

    if verbose:
        status = '✓' if all_pass else '✗'
        print(f"  [{status}] {ph} "
              f"continuity")
        for bname, bdata in results.items():
            bp = ('✓' if
                  (bdata['is_pass'] and
                   bdata['centroid_pass'] and
                   bdata['amplitude_pass'])
                  else '✗')
            arrow = ('AA→ph'
                     if bname == 'AA_to_ph'
                     else 'ph→AA')
            print(f"    [{bp}] {arrow}")
            ip = '✓' if bdata['is_pass'] \
                 else '✗'
            cp = '✓' if bdata[
                'centroid_pass'] else '✗'
            ap = '✓' if bdata[
                'amplitude_pass'] else '✗'
            print(
                f"      [{ip}] "
                f"IS={bdata['is_divergence']}"
                f"  target<={IS_THRESHOLD}")
            print(
                f"      [{cp}] "
                f"centroid_jump="
                f"{bdata['centroid_jump_hz']}Hz"
                f"  target<={CENTROID_JUMP_HZ}")
            print(
                f"      [{ap}] "
                f"amp={bdata['amplitude_db']}dB"
                f"  target±{AMPLITUDE_DB}dB")

    return results, all_pass


# ============================================================
# FULL DIAGNOSTIC RUN
# ============================================================

def run_continuity_diagnostic(
        sr=SR_D, verbose=True):

    print()
    print("CONTINUITY DIAGNOSTIC")
    print("Self-referential: system tests itself.")
    print("="*50)

    # Phonemes to test
    TEST_PHS = list(
        PHONEME_IDENTITY_TARGETS.keys())

    total_id   = 0
    pass_id    = 0
    total_cont = 0
    pass_cont  = 0

    all_id_results   = {}
    all_cont_results = {}

    # ── PART 1: Identity ──────────────────
    print()
    print("  PART 1: Phoneme identity")
    print("  Does each phoneme sound like itself?")
    print()

    for ph in TEST_PHS:
        r, ok = check_phoneme_identity(
            ph, sr=sr, verbose=verbose)
        all_id_results[ph] = r
        total_id += 1
        if ok:
            pass_id += 1
        if verbose:
            print()

    # ── PART 2: Continuity ────────────────
    print()
    print("  PART 2: Boundary continuity")
    print("  Is each phoneme continuous")
    print("  with its neighbors?")
    print()

    for ph in TEST_PHS:
        r, ok = check_continuity(
            ph, sr=sr, verbose=verbose)
        all_cont_results[ph] = r
        total_cont += 1
        if ok:
            pass_cont += 1
        if verbose:
            print()

    # ── SUMMARY ───────────────────────────
    print("="*50)
    print()
    print("  CONTINUITY DIAGNOSTIC SUMMARY")
    print()
    print(f"  Identity:    "
          f"{pass_id}/{total_id}")
    print(f"  Continuity:  "
          f"{pass_cont}/{total_cont}")
    print()

    # Identify the worst offenders
    print("  IDENTITY FAILURES:")
    any_id_fail = False
    for ph, r in all_id_results.items():
        fails = [k for k, v in r.items()
                 if not v.get('pass', True)]
        if fails:
            any_id_fail = True
            dists = {
                k: r[k]['distance']
                for k in fails}
            print(f"    {ph}: {fails}")
            for k, d in dists.items():
                print(f"      {k} "
                      f"distance={d}")
    if not any_id_fail:
        print("    All passing.")
    print()

    print("  CONTINUITY FAILURES:")
    any_cont_fail = False
    for ph, r in all_cont_results.items():
        for bname, bdata in r.items():
            b_fails = []
            if not bdata['is_pass']:
                b_fails.append(
                    f"IS="
                    f"{bdata['is_divergence']}")
            if not bdata['centroid_pass']:
                b_fails.append(
                    f"jump="
                    f"{bdata['centroid_jump_hz']}"
                    f"Hz")
            if not bdata['amplitude_pass']:
                b_fails.append(
                    f"amp="
                    f"{bdata['amplitude_db']}"
                    f"dB")
            if b_fails:
                any_cont_fail = True
                arrow = ('AA→ph'
                         if bname == 'AA_to_ph'
                         else 'ph→AA')
                print(f"    {ph} {arrow}: "
                      f"{', '.join(b_fails)}")
    if not any_cont_fail:
        print("    All passing.")
    print()

    return (all_id_results,
            all_cont_results,
            pass_id, total_id,
            pass_cont, total_cont)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    run_continuity_diagnostic(sr=SR)
