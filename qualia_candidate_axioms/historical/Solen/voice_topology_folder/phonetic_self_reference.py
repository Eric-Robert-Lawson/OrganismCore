"""
PHONETIC SELF-REFERENCE v2
February 2026

The synthesis engine gains its own ears.
Extended from v1 (Z sibilance loop)
to three-level phonetic self-awareness:

  LEVEL 1: Acoustic identity
    Sibilance, HNR, formant positions.
    Original v1 capability preserved
    and extended to all phoneme families.

  LEVEL 2: Locus identity
    F2 midpoint (locus estimate) per consonant.
    F2 slope direction (onset vs coda).
    Place verification against LOCUS_F2_BASE.
    Directional identity check (dark L, etc.).

  LEVEL 3: Qualia coherence
    Phrase-level F0 arc shape measurement.
    Ghost duration detection at syllable boundaries.
    Tonnetz position recovery per nucleus vowel.
    Rhyme convergence check between phrases.

RARFL self-correction loop:
  Synthesize → Measure → Compare →
  Adjust → Re-synthesize → Converge.

Usage:
  from phonetic_self_reference import (
      PhoneticSelfRef,
      run_full_diagnostic,
  )
  psr = PhoneticSelfRef(sr=44100)
  report = psr.check_phrase(phrase_spec, seg)
  psr.print_map(report)
"""

import numpy as np
from scipy.signal import (
    butter, lfilter, find_peaks,
)
import os

SR    = 44100
DTYPE = np.float32

def f32(x):
    return np.asarray(x, dtype=DTYPE)


# ============================================================
# LEVEL 1: ACOUSTIC IDENTITY TARGETS
# What each phoneme should measure as.
# Updated for v17 phoneme set.
# ============================================================

PHONEME_TARGETS = {
    # ── Vowels ──────────────────────────���───
    'AA': {
        'voiced': True,
        'f1': (650,  900),
        'f2': (950,  1300),
        'sibilance_max': 0.05,
        'hnr_min': 12.0,
    },
    'AE': {
        'voiced': True,
        'f1': (650,  850),
        'f2': (1600, 1950),
        'sibilance_max': 0.05,
        'hnr_min': 12.0,
    },
    'AH': {
        'voiced': True,
        'f1': (550,  750),
        'f2': (1050, 1400),
        'sibilance_max': 0.05,
        'hnr_min': 10.0,
    },
    'AO': {
        'voiced': True,
        'f1': (450,  680),
        'f2': (700,  1050),
        'sibilance_max': 0.05,
        'hnr_min': 12.0,
    },
    'AW': {
        'voiced': True,
        'f1': (600,  850),
        'f2': (700,  1100),
        'sibilance_max': 0.05,
        'hnr_min': 10.0,
    },
    'AY': {
        'voiced': True,
        'f1': (600,  850),
        'f2': (1000, 1500),
        'sibilance_max': 0.05,
        'hnr_min': 10.0,
    },
    'EH': {
        'voiced': True,
        'f1': (460,  650),
        'f2': (1650, 2000),
        'sibilance_max': 0.05,
        'hnr_min': 12.0,
    },
    'ER': {
        'voiced': True,
        'f1': (400,  580),
        'f3': (1550, 1820),   # F3 suppression key
        'sibilance_max': 0.05,
        'hnr_min': 10.0,
    },
    'EY': {
        'voiced': True,
        'f1': (400,  580),
        'f2': (1800, 2300),
        'sibilance_max': 0.05,
        'hnr_min': 10.0,
    },
    'IH': {
        'voiced': True,
        'f1': (320,  470),
        'f2': (1850, 2200),
        'sibilance_max': 0.05,
        'hnr_min': 12.0,
    },
    'IY': {
        'voiced': True,
        'f1': (230,  340),
        'f2': (2150, 2500),
        'sibilance_max': 0.05,
        'hnr_min': 12.0,
    },
    'OW': {
        'voiced': True,
        'f1': (380,  540),
        'f2': (650,  950),
        'sibilance_max': 0.05,
        'hnr_min': 12.0,
    },
    'OY': {
        'voiced': True,
        'f1': (400,  600),
        'f2': (700,  1100),
        'sibilance_max': 0.05,
        'hnr_min': 10.0,
    },
    'UH': {
        'voiced': True,
        'f1': (380,  520),
        'f2': (850,  1100),
        'sibilance_max': 0.05,
        'hnr_min': 12.0,
    },
    'UW': {
        'voiced': True,
        'f1': (240,  360),
        'f2': (700,  950),
        'sibilance_max': 0.05,
        'hnr_min': 12.0,
    },

    # ── Sibilants ────────────────────────────
    'S': {
        'voiced': False,
        'sibilance_min':  0.65,
        'sibilance_band': (5500, 13000),
        'f_peak_min':     6000,
        'hnr_max':        3.0,
    },
    'Z': {
        'voiced':            True,
        'sibilance_min':     0.40,
        'sibilance_band':    (5500, 13000),
        'hnr_min':           4.0,
        'hnr_max':           18.0,
        'sib_to_voice_min':  0.35,
    },
    'SH': {
        'voiced': False,
        'sibilance_min':  0.50,
        'sibilance_band': (1800, 8000),
        'f_peak_max':     4500,
        'hnr_max':        3.0,
    },
    'ZH': {
        'voiced': True,
        'sibilance_min':  0.30,
        'sibilance_band': (1800, 8000),
        'hnr_min':        4.0,
    },

    # ── Other fricatives ─────────────────────
    'F': {
        'voiced': False,
        'sibilance_min':  0.18,
        'sibilance_band': (2500, 10000),
        'hnr_max':        3.0,
    },
    'V': {
        'voiced': True,
        'sibilance_min':  0.08,
        'hnr_min':        5.0,
        'hnr_max':        22.0,
    },
    'TH': {
        'voiced': False,
        'sibilance_min':  0.08,
        'sibilance_band': (1500, 9000),
        'hnr_max':        3.0,
    },
    'DH': {
        'voiced': True,
        'sibilance_max':  0.12,
        'hnr_min':        5.0,
        'hnr_max':        22.0,
    },

    # ── Nasals ────────────────────────────────
    'M': {
        'voiced': True,
        'f1': (200, 290),
        'antiformant': (850,  1200),
        'hnr_min': 8.0,
        'sibilance_max': 0.04,
    },
    'N': {
        'voiced': True,
        'f1': (200, 290),
        'antiformant': (1250, 1750),
        'hnr_min': 8.0,
        'sibilance_max': 0.04,
    },
    'NG': {
        'voiced': True,
        'f1': (200, 290),
        'antiformant': (1800, 2400),
        'hnr_min': 8.0,
        'sibilance_max': 0.04,
    },

    # ── Approximants ─────────────────────────
    'R': {
        'voiced': True,
        'f3': (1550, 1820),   # suppressed
        'hnr_min': 8.0,
        'sibilance_max': 0.05,
    },
    'L': {
        'voiced': True,
        'f2': (800,  1200),   # dark L range
        'hnr_min': 8.0,
        'sibilance_max': 0.05,
    },
    'W': {
        'voiced': True,
        'f1': (240, 370),
        'f2': (480, 740),
        'hnr_min': 8.0,
    },
    'Y': {
        'voiced': True,
        'f2': (1900, 2500),
        'hnr_min': 8.0,
    },

    # ── Affricates ───────────────────────────
    'JH': {
        'voiced': True,
        'sibilance_min':  0.28,
        'sibilance_band': (1400, 7500),
        'hnr_min':        3.0,
        'hnr_max':        18.0,
    },
    'CH': {
        'voiced': False,
        'sibilance_min':  0.38,
        'sibilance_band': (1700, 9000),
        'hnr_max':        3.0,
    },

    # ── H ────────────────────────────────────
    'H':  {
        'voiced': False,
        'sibilance_max': 0.18,
        'hnr_max': 9.0,
    },
    'HH': {
        'voiced': False,
        'sibilance_max': 0.18,
        'hnr_max': 9.0,
    },
}


# ============================================================
# LEVEL 2: LOCUS TARGETS
# Expected F2 midpoint per consonant place.
# From voice_physics_v17.LOCUS_F2_BASE.
# ============================================================

LOCUS_TARGETS = {
    'bilabial':      (580,  860),   # center ~720
    'labiodental':   (900,  1300),  # center ~1100
    'dental':        (1400, 1800),  # center ~1600
    'alveolar':      (1600, 2000),  # center ~1800
    'lateral_dark':  (800,  1200),  # coda L center ~1000
    'lateral_onset': (1600, 2000),  # onset L center ~1800
    'postalveolar':  (1900, 2300),  # center ~2100
    'palatal':       (2100, 2500),  # center ~2300
    'velar_front':   (2700, 3200),  # before IY/EH/AE
    'velar_mid':     (2200, 2700),  # before AH/ER
    'velar_back':    (1700, 2200),  # before UW/UH/AO
    'glottal':       (300,  700),   # center ~500
    'rhotic':        (600,  1000),  # F2 ~800, F3 suppressed
}

# Map consonant phonemes to locus class
# for onset vs coda (lateral is split)
PH_TO_LOCUS_CLASS = {
    'M':  'bilabial',    'B':  'bilabial',
    'P':  'bilabial',    'W':  'glottal',
    'F':  'labiodental', 'V':  'labiodental',
    'TH': 'dental',      'DH': 'dental',
    'T':  'alveolar',    'D':  'alveolar',
    'N':  'alveolar',    'S':  'alveolar',
    'Z':  'alveolar',
    'SH': 'postalveolar','ZH': 'postalveolar',
    'CH': 'postalveolar','JH': 'postalveolar',
    'Y':  'palatal',
    'K':  'velar_mid',   'G':  'velar_mid',
    'NG': 'velar_mid',
    'H':  'glottal',     'HH': 'glottal',
    'R':  'rhotic',
    # L: direction-dependent, handled separately
}


# ============================================================
# ANALYSIS FUNCTIONS
# ============================================================

def measure_sibilance(seg, sr=SR,
                       band=(5500, 13000)):
    seg = f32(seg)
    if len(seg) < 64:
        return 0.0
    nyq = sr / 2.0
    lo  = max(band[0] / nyq, 0.001)
    hi  = min(band[1] / nyq, 0.499)
    if lo >= hi:
        return 0.0
    try:
        b, a  = butter(4, [lo, hi],
                        btype='band')
        sib   = lfilter(b, a, seg)
        e_sib = float(np.mean(sib ** 2))
        e_tot = float(np.mean(seg ** 2))
        if e_tot < 1e-12:
            return 0.0
        return e_sib / e_tot
    except Exception:
        return 0.0


def measure_hnr(seg, pitch_hz=175,
                sr=SR):
    seg = f32(seg)
    n   = len(seg)
    if n < 64:
        return 0.0
    T0 = int(sr / max(pitch_hz, 50))
    if T0 >= n:
        return 0.0
    r0 = float(np.sum(seg ** 2))
    r1 = float(np.sum(seg[:n - T0] *
                       seg[T0:]))
    if r0 < 1e-12:
        return 0.0
    ratio = np.clip(r1 / r0,
                    -0.999, 0.999)
    if ratio <= 0:
        return 0.0
    return float(10 * np.log10(
        ratio / (1 - ratio + 1e-10)))


def measure_sib_to_voice(seg, sr=SR):
    seg = f32(seg)
    if len(seg) < 64:
        return 0.0
    nyq = sr / 2.0
    try:
        b, a  = butter(4, 3000 / nyq,
                        btype='high')
        hi    = lfilter(b, a, seg)
        b, a  = butter(4, 3000 / nyq,
                        btype='low')
        lo    = lfilter(b, a, seg)
        e_hi  = float(np.mean(hi ** 2))
        e_lo  = float(np.mean(lo ** 2))
        if e_lo < 1e-12:
            return 0.0
        return e_hi / e_lo
    except Exception:
        return 0.0


def estimate_formants(seg, sr=SR,
                       order=None,
                       n_formants=4):
    """
    LPC-based formant estimation.
    Returns [F1, F2, F3, F4] in Hz.
    """
    seg = f32(seg)
    n   = len(seg)
    if n < 128:
        return [0.0] * n_formants

    if order is None:
        order = min(int(2 + sr / 1000),
                    n // 3, 40)

    pre = np.append(
        seg[0], seg[1:] - 0.97 * seg[:-1])

    try:
        R = np.array([
            float(np.dot(pre[:n - k],
                          pre[k:]))
            for k in range(order + 1)])
        if abs(R[0]) < 1e-10:
            return [0.0] * n_formants

        a    = np.zeros(order)
        err  = R[0]
        for i in range(order):
            k = R[i + 1]
            for j in range(i):
                k -= a[j] * R[i - j]
            k /= (err + 1e-10)
            a_new = a[:i] - k * a[:i][::-1]
            a[:i] = a_new
            a[i]  = k
            err  *= (1 - k ** 2)

        n_fft = 2048
        H     = np.fft.rfft(
            np.append([1.0], -a), n=n_fft)
        spec  = 1.0 / (np.abs(H) ** 2 + 1e-10)
        freqs = np.fft.rfftfreq(
            n_fft, d=1.0 / sr)

        mask  = (freqs > 100) & \
                (freqs < 5500)
        s_m   = spec[mask]
        f_m   = freqs[mask]
        if len(s_m) == 0:
            return [0.0] * n_formants

        dist  = max(1, int(
            80.0 / max(freqs[1] -
                        freqs[0], 0.1)))
        peaks, _ = find_peaks(
            s_m,
            height=np.max(s_m) * 0.08,
            distance=dist)

        formants = sorted([
            float(f_m[p]) for p in peaks])
        while len(formants) < n_formants:
            formants.append(0.0)
        return formants[:n_formants]

    except Exception:
        return [0.0] * n_formants


def measure_f2_trajectory(seg, sr=SR,
                            n_frames=8):
    """
    Measure F2 value at the start,
    middle, and end of a segment.

    Returns:
      (f2_start, f2_mid, f2_end, slope)
      slope > 0: rising (onset direction)
      slope < 0: falling (coda direction)
    """
    seg = f32(seg)
    n   = len(seg)
    if n < 256:
        f2 = estimate_formants(seg,
                                sr=sr)[1]
        return f2, f2, f2, 0.0

    frame = n // n_frames
    f2s   = []
    for i in range(n_frames):
        s = i * frame
        e = min(s + frame, n)
        if e - s < 64:
            continue
        fmts = estimate_formants(
            seg[s:e], sr=sr)
        f2s.append(fmts[1])

    if len(f2s) < 3:
        f2_mid = f2s[0] if f2s else 0.0
        return f2_mid, f2_mid, f2_mid, 0.0

    f2_start = float(np.mean(f2s[:2]))
    f2_mid   = float(np.median(f2s))
    f2_end   = float(np.mean(f2s[-2:]))
    slope    = f2_end - f2_start
    return f2_start, f2_mid, f2_end, slope


def measure_f0_arc(seg, sr=SR,
                    n_frames=16,
                    pitch_lo=80,
                    pitch_hi=400):
    """
    Measure the F0 trajectory across
    a phrase segment.

    Returns:
      f0_values: list of median F0 per frame
                 (0.0 for unvoiced frames)
      arc_slope: overall slope (Hz/frame)
      peak_position: normalized position
                     of F0 peak (0.0–1.0)
    """
    seg = f32(seg)
    n   = len(seg)
    if n < sr // 10:
        return [], 0.0, 0.5

    frame   = n // n_frames
    f0_vals = []

    for i in range(n_frames):
        s   = i * frame
        e   = min(s + frame, n)
        frs = seg[s:e]
        if len(frs) < 64:
            f0_vals.append(0.0)
            continue
        # Autocorrelation pitch detection
        best_f0 = 0.0
        best_r  = 0.0
        for hz in range(pitch_lo,
                         pitch_hi, 5):
            lag = int(sr / hz)
            if lag >= len(frs):
                continue
            r = float(np.sum(
                frs[:len(frs)-lag] *
                frs[lag:]))
            e0 = float(np.sum(frs**2))
            if e0 > 1e-10:
                r /= e0
            if r > best_r:
                best_r  = r
                best_f0 = float(hz)
        f0_vals.append(
            best_f0 if best_r > 0.25
            else 0.0)

    voiced = [(i, v) for i, v in
              enumerate(f0_vals) if v > 0]
    if len(voiced) < 2:
        return f0_vals, 0.0, 0.5

    idxs = [i for i, v in voiced]
    vals = [v for i, v in voiced]
    slope = ((vals[-1] - vals[0]) /
              max(len(vals) - 1, 1))

    peak_i = int(np.argmax(vals))
    peak_pos = (idxs[peak_i] /
                max(n_frames - 1, 1))

    return f0_vals, slope, peak_pos


def detect_ghost_boundaries(
        seg, sr=SR,
        min_gap_ms=3.0,
        max_gap_ms=60.0,
        energy_threshold=0.015):
    """
    Detect ghost segments between syllables.

    A ghost is a low-amplitude region
    between two louder regions — the
    acoustic trace of the inter-syllable
    H traversal.

    Returns list of (start_ms, end_ms,
                     duration_ms, amplitude)
    for detected ghost events.
    """
    seg        = f32(seg)
    n          = len(seg)
    frame_ms   = 5.0
    frame_n    = int(frame_ms / 1000 * sr)
    if frame_n < 2:
        return []

    # Frame energy
    n_frames   = n // frame_n
    energy     = np.array([
        float(np.mean(
            seg[i*frame_n:(i+1)*frame_n]**2))
        for i in range(n_frames)])

    if len(energy) == 0:
        return []

    e_norm = energy / (
        np.max(energy) + 1e-10)

    # Low-energy regions between
    # higher-energy regions = ghosts
    in_ghost    = False
    ghost_start = 0
    ghosts      = []
    min_frames  = max(1, int(
        min_gap_ms / frame_ms))
    max_frames  = int(
        max_gap_ms / frame_ms)

    for i, e in enumerate(e_norm):
        if not in_ghost and \
           e < energy_threshold and \
           i > 0 and e_norm[i-1] > \
           energy_threshold * 2:
            in_ghost    = True
            ghost_start = i
        elif in_ghost and (
                e > energy_threshold * 1.5
                or i == len(e_norm) - 1):
            ghost_len = i - ghost_start
            if min_frames <= ghost_len \
               <= max_frames:
                s_ms = ghost_start * frame_ms
                e_ms = i * frame_ms
                amp  = float(np.sqrt(np.mean(
                    energy[
                        ghost_start:i])))
                ghosts.append((
                    s_ms, e_ms,
                    e_ms - s_ms, amp))
            in_ghost = False

    return ghosts


def measure_tonnetz_position(
        seg, sr=SR):
    """
    Estimate the Tonnetz position of
    the dominant vowel in a segment.

    Strategy:
      1. Estimate F1 and F2.
      2. Find the nearest vowel in
         VOWEL_F by Euclidean distance
         in (F1, F2) space.
      3. Return the vowel phoneme symbol
         and its Tonnetz position.

    Returns:
      (phoneme_symbol, (a, b), f1, f2)
    """
    # Import Tonnetz position table
    # from tonnetz_engine if available
    try:
        from tonnetz_engine import (
            VOWEL_TONNETZ,
        )
    except ImportError:
        VOWEL_TONNETZ = {}

    try:
        from voice_physics_v3 import VOWEL_F
    except ImportError:
        VOWEL_F = {}

    fmts = estimate_formants(seg, sr=sr)
    f1   = fmts[0]
    f2   = fmts[1]

    if f1 < 50 or f2 < 200:
        return (None, (0, 0), f1, f2)

    best_ph   = None
    best_dist = float('inf')
    for ph, data in VOWEL_F.items():
        if not isinstance(data,
                          (list, tuple)):
            continue
        tgt = data[0]
        if not (isinstance(tgt,
                            (list, tuple))
                and len(tgt) >= 2):
            continue
        tf1  = float(tgt[0])
        tf2  = float(tgt[1])
        dist = ((f1 - tf1) ** 2 +
                (f2 - tf2) ** 2) ** 0.5
        if dist < best_dist:
            best_dist = dist
            best_ph   = ph

    tonnetz = VOWEL_TONNETZ.get(
        best_ph, (0, 0)) \
        if best_ph else (0, 0)
    return (best_ph, tonnetz, f1, f2)


def measure_locus(cons_seg, sr=SR):
    """
    Estimate the F2 locus from a
    consonant segment.

    Returns:
      f2_locus: F2 at midpoint of segment
      f2_start: F2 at onset
      f2_end:   F2 at offset
      direction: 'onset' if f2 rising,
                 'coda'  if f2 falling,
                 'flat'  if ambiguous
    """
    f2s, f2m, f2e, slope = \
        measure_f2_trajectory(
            cons_seg, sr=sr)
    if abs(slope) < 80:
        direction = 'flat'
    elif slope > 0:
        direction = 'onset'
    else:
        direction = 'coda'
    return f2m, f2s, f2e, direction


# ============================================================
# LEVEL 1 CHECK — individual phoneme
# ============================================================

def check_phoneme_l1(ph, seg, sr=SR,
                      verbose=True):
    """
    Level 1 acoustic identity check.
    """
    target  = PHONEME_TARGETS.get(ph)
    if target is None:
        return {}, True

    seg     = f32(seg)
    results = {}
    failed  = []

    # Voiced check
    if 'voiced' in target:
        hnr    = measure_hnr(seg, sr=sr)
        voiced = hnr > 3.0
        ok     = (voiced == target['voiced'])
        results['voiced'] = {
            'target':   target['voiced'],
            'measured': voiced,
            'hnr_db':   round(hnr, 1),
            'pass':     ok,
        }
        if not ok:
            failed.append('voiced')

    # Sibilance
    band = target.get('sibilance_band',
                       (5500, 13000))
    if 'sibilance_min' in target or \
       'sibilance_max' in target:
        sib   = measure_sibilance(
            seg, sr=sr, band=band)
        s_min = target.get(
            'sibilance_min', 0.0)
        s_max = target.get(
            'sibilance_max', 1.0)
        ok    = s_min <= sib <= s_max
        results['sibilance'] = {
            'target':   (s_min, s_max),
            'measured': round(sib, 3),
            'pass':     ok,
        }
        if not ok:
            failed.append('sibilance')

    # Z-specific: sibilance over voicing
    if 'sib_to_voice_min' in target:
        stv   = measure_sib_to_voice(
            seg, sr=sr)
        s_min = target['sib_to_voice_min']
        ok    = stv >= s_min
        results['sib_to_voice'] = {
            'target_min': s_min,
            'measured':   round(stv, 3),
            'pass':       ok,
        }
        if not ok:
            failed.append('sib_to_voice')

    # HNR
    if 'hnr_min' in target or \
       'hnr_max' in target:
        hnr   = measure_hnr(seg, sr=sr)
        h_min = target.get('hnr_min', -99)
        h_max = target.get('hnr_max',  99)
        ok    = h_min <= hnr <= h_max
        results['hnr'] = {
            'target':   (h_min, h_max),
            'measured': round(hnr, 1),
            'pass':     ok,
        }
        if not ok:
            failed.append('hnr')

    # Formants
    if any(k in target
           for k in ('f1', 'f2', 'f3')):
        fmts = estimate_formants(
            seg, sr=sr)
        for fi, fname in enumerate(
                ('f1', 'f2', 'f3', 'f4')):
            if fname in target:
                lo, hi   = target[fname]
                measured = fmts[fi]
                ok = lo <= measured <= hi
                results[fname] = {
                    'target':   (lo, hi),
                    'measured': round(
                        measured, 1),
                    'pass':     ok,
                }
                if not ok:
                    failed.append(fname)

    all_pass = len(failed) == 0

    if verbose:
        sym = '✓' if all_pass else '✗'
        print(f"  [L1 {sym}] {ph}")
        for k, v in results.items():
            p = '  ✓' if v['pass'] else '  ✗'
            m = v.get('measured', '?')
            t = v.get('target', '')
            print(f"    {p} {k}:  "
                  f"measured={m}  "
                  f"target={t}")

    return results, all_pass


# ============================================================
# LEVEL 2 CHECK — locus identity
# ============================================================

def check_phoneme_l2(ph, seg, sr=SR,
                      expected_direction=None,
                      adjacent_vowel=None,
                      verbose=True):
    """
    Level 2 locus identity check.

    ph:                 consonant phoneme
    seg:                synthesized segment
    expected_direction: 'onset', 'coda', or None
    adjacent_vowel:     ARPAbet vowel symbol
                        (for velar context)

    Returns:
      results dict, all_pass bool
    """
    # L special case
    if ph == 'L':
        if expected_direction == 'coda':
            locus_class = 'lateral_dark'
        elif expected_direction == 'onset':
            locus_class = 'lateral_onset'
        else:
            locus_class = 'lateral_dark'
    # Velar context sensitivity
    elif ph in ('K', 'G', 'NG'):
        try:
            from tonnetz_engine import \
                VOWEL_TONNETZ
            if adjacent_vowel:
                a = float(
                    VOWEL_TONNETZ.get(
                        adjacent_vowel,
                        (0, 0))[0])
                if a >= 2.0:
                    locus_class = 'velar_front'
                elif a <= -2.0:
                    locus_class = 'velar_back'
                else:
                    locus_class = 'velar_mid'
            else:
                locus_class = 'velar_mid'
        except Exception:
            locus_class = 'velar_mid'
    else:
        locus_class = PH_TO_LOCUS_CLASS.get(
            ph, None)

    results  = {}
    all_pass = True

    if ph not in PH_TO_LOCUS_CLASS and \
       ph not in ('K', 'G', 'NG', 'L'):
        if verbose:
            print(f"  [L2 ?] {ph}: "
                  f"no locus class")
        return results, True

    f2m, f2s, f2e, direction = \
        measure_locus(seg, sr=sr)

    # Locus position check
    if locus_class and \
       locus_class in LOCUS_TARGETS:
        lo, hi  = LOCUS_TARGETS[locus_class]
        locus_ok = lo <= f2m <= hi
        results['locus_f2'] = {
            'class':    locus_class,
            'target':   (lo, hi),
            'measured': round(f2m, 1),
            'pass':     locus_ok,
        }
        if not locus_ok:
            all_pass = False

    # Direction check
    if expected_direction is not None:
        dir_ok = (direction ==
                  expected_direction)
        results['direction'] = {
            'target':   expected_direction,
            'measured': direction,
            'f2_start': round(f2s, 1),
            'f2_end':   round(f2e, 1),
            'slope':    round(
                f2e - f2s, 1),
            'pass':     dir_ok,
        }
        if not dir_ok:
            all_pass = False

    if verbose:
        sym = '✓' if all_pass else '✗'
        print(f"  [L2 {sym}] {ph} "
              f"({locus_class})")
        for k, v in results.items():
            p = '  ✓' if v['pass'] \
                else '  ✗'
            print(f"    {p} {k}: "
                  f"measured="
                  f"{v.get('measured','?')}  "
                  f"target="
                  f"{v.get('target','')}")

    return results, all_pass


# ============================================================
# LEVEL 3 CHECK — phrase qualia coherence
# ============================================================

def check_phrase_l3(
        seg, arc_type_label='normal',
        sr=SR, verbose=True):
    """
    Level 3: phrase-level qualia check.

    Measures:
      - F0 arc shape (slope, peak position)
      - Ghost boundary detection
      - Gross Tonnetz position of phrase
        (dominant vowel)

    Returns:
      results dict, coherence_score float
    """
    seg     = f32(seg)
    results = {}

    # F0 arc
    f0_vals, arc_slope, peak_pos = \
        measure_f0_arc(seg, sr=sr)
    voiced_f0 = [v for v in f0_vals
                 if v > 0]
    f0_mean   = (float(np.mean(voiced_f0))
                 if voiced_f0 else 0.0)
    f0_range  = (float(np.max(voiced_f0) -
                        np.min(voiced_f0))
                 if len(voiced_f0) > 1
                 else 0.0)

    results['f0_arc'] = {
        'mean_hz':      round(f0_mean, 1),
        'range_hz':     round(f0_range, 1),
        'slope':        round(arc_slope,2),
        'peak_pos':     round(peak_pos, 2),
        'voiced_frames':len(voiced_f0),
        'total_frames': len(f0_vals),
    }

    # Ghost detection
    ghosts = detect_ghost_boundaries(
        seg, sr=sr)
    results['ghosts'] = {
        'count':     len(ghosts),
        'durations': [round(g[2], 1)
                      for g in ghosts],
        'amplitudes':[round(g[3], 4)
                      for g in ghosts],
    }

    # Dominant Tonnetz position
    ph, tonnetz, f1, f2 = \
        measure_tonnetz_position(
            seg, sr=sr)
    results['tonnetz'] = {
        'recovered_ph':  ph,
        'position':      tonnetz,
        'f1_hz':         round(f1, 1),
        'f2_hz':         round(f2, 1),
    }

    # Coherence score (0.0–1.0):
    # Based on:
    #   — Voiced frame fraction
    #   — Ghost presence
    #   — F0 range (indicates
    #              arc is active)
    n_frames  = max(len(f0_vals), 1)
    v_frac    = len(voiced_f0) / n_frames
    has_ghost = len(ghosts) > 0
    has_arc   = f0_range > 15.0
    score     = (0.5 * v_frac +
                 0.25 * (1.0 if has_ghost
                          else 0.0) +
                 0.25 * (1.0 if has_arc
                          else 0.0))
    results['coherence_score'] = \
        round(float(score), 3)

    if verbose:
        sym = '✓' if score > 0.6 else '~' \
               if score > 0.35 else '✗'
        print(f"  [L3 {sym}] phrase "
              f"coherence={score:.2f} "
              f"({arc_type_label})")
        print(f"    F0: mean={f0_mean:.0f}Hz "
              f"range={f0_range:.0f}Hz "
              f"peak@{peak_pos:.2f} "
              f"slope={arc_slope:.1f}")
        print(f"    Ghosts: "
              f"{len(ghosts)} detected  "
              f"durations="
              f"{[round(g[2],1) for g in ghosts]}")
        tp = results['tonnetz']
        print(f"    Tonnetz: "
              f"{tp['recovered_ph']} "
              f"pos={tp['position']}  "
              f"F1={tp['f1_hz']}  "
              f"F2={tp['f2_hz']}")

    return results, score


# ============================================================
# RELATIONAL DIAGNOSTIC
#
# Tests phoneme PAIRS that differ in exactly
# one acoustic dimension.
# The engine should hear the difference.
# If it cannot, the dimension is not rendered.
# ============================================================

RELATIONAL_PAIRS = [
    # (ph_a, ph_b, dimension, description)
    ('S',  'Z',  'voicing',
     'S/Z: same sibilance, Z adds voicing'),
    ('SH', 'ZH', 'voicing',
     'SH/ZH: same postalveolar, ZH voiced'),
    ('F',  'V',  'voicing',
     'F/V: same labiodental, V voiced'),
    ('TH', 'DH', 'voicing',
     'TH/DH: same dental, DH voiced'),
    ('M',  'N',  'place',
     'M/N: same nasality, different place'),
    ('N',  'NG', 'place',
     'N/NG: same nasality, different place'),
    ('M',  'NG', 'place',
     'M/NG: bilabial vs velar nasals'),
    ('L_onset', 'L_coda', 'direction',
     'L: onset bright vs coda dark'),
    ('K_front', 'K_back', 'context',
     'K: front vowel vs back vowel context'),
    ('R',  'L',  'constriction_shape',
     'R/L: same approximant class, '
     'different tongue shape'),
    ('N_onset', 'N_coda', 'direction',
     'N: alveolar onset vs coda direction'),
]


def run_relational_diagnostic(
        synth_fn, sr=SR, verbose=True):
    """
    Run the relational diagnostic.

    synth_fn(word, phones) → segment

    For each pair, synthesize both,
    measure the distinguishing dimension,
    report whether the difference is
    present in the output.

    The distinguishing dimension is
    the one acoustic property that
    should differ between the pair.
    Everything else should be similar.
    """
    results = {}

    if verbose:
        print()
        print("  RELATIONAL DIAGNOSTIC")
        print("  Tests: does the engine hear")
        print("  the difference that defines")
        print("  each phoneme pair?")
        print()

    # S vs Z: sibilance level should match,
    # HNR should differ
    try:
        seg_s = synth_fn('voice',
                          ['V','OY','S'])
        seg_z = synth_fn('was',
                          ['W','AH','Z'])
        n = len(seg_s)
        sib_s = measure_sibilance(
            seg_s[2*n//3:], sr=sr,
            band=(5500,13000))
        sib_z = measure_sibilance(
            seg_z[2*n//3:], sr=sr,
            band=(5500,13000))
        hnr_s = measure_hnr(
            seg_s[2*n//3:], sr=sr)
        hnr_z = measure_hnr(
            seg_z[2*n//3:], sr=sr)
        sib_gap = abs(sib_s - sib_z)
        hnr_gap = hnr_z - hnr_s
        ok = (sib_z >= 0.35 and
              hnr_gap > 3.0 and
              sib_gap < 0.30)
        results['S_vs_Z'] = {
            'S_sibilance':  round(sib_s,3),
            'Z_sibilance':  round(sib_z,3),
            'S_hnr':        round(hnr_s,1),
            'Z_hnr':        round(hnr_z,1),
            'sib_gap':      round(sib_gap,3),
            'hnr_gap':      round(hnr_gap,1),
            'pass':         ok,
        }
        if verbose:
            sym = '✓' if ok else '✗'
            print(f"  [{sym}] S vs Z "
                  f"(voicing dimension):")
            print(f"    S sib={sib_s:.3f}  "
                  f"hnr={hnr_s:.1f}dB")
            print(f"    Z sib={sib_z:.3f}  "
                  f"hnr={hnr_z:.1f}dB")
            print(f"    sib_gap={sib_gap:.3f} "
                  f"(want <0.30)")
            print(f"    hnr_gap={hnr_gap:.1f} "
                  f"(want >3.0)")
            print()
    except Exception as ex:
        results['S_vs_Z'] = {
            'error': str(ex),
            'pass': False}

    # M vs N vs NG: locus separation
    try:
        segs = {}
        for ph, word, phones in [
            ('M', 'am', ['AE','M']),
            ('N', 'an', ['AE','N']),
            ('NG','ang',['AE','NG']),
        ]:
            seg = synth_fn(word, phones)
            n   = len(seg)
            # Nasal is in second half
            segs[ph] = seg[n//2:]

        loci = {}
        for ph in ('M', 'N', 'NG'):
            fmts = estimate_formants(
                segs[ph], sr=sr)
            loci[ph] = fmts[1]

        # M F2 should be lowest (~720)
        # N F2 should be mid (~1800)
        # NG F2 should be highest (~2700)
        m_n_sep = loci['N'] - loci['M']
        n_ng_sep = loci['NG'] - loci['N']
        ok = (m_n_sep > 400 and
              n_ng_sep > 400)
        results['nasal_place'] = {
            'M_f2':     round(loci['M'],1),
            'N_f2':     round(loci['N'],1),
            'NG_f2':    round(loci['NG'],1),
            'M_N_sep':  round(m_n_sep,1),
            'N_NG_sep': round(n_ng_sep,1),
            'pass':     ok,
        }
        if verbose:
            sym = '✓' if ok else '✗'
            print(f"  [{sym}] M vs N vs NG "
                  f"(place dimension):")
            print(f"    M  F2={loci['M']:.0f} "
                  f"(target ~720)")
            print(f"    N  F2={loci['N']:.0f} "
                  f"(target ~1800)")
            print(f"    NG F2={loci['NG']:.0f} "
                  f"(target ~2700)")
            print(f"    M→N sep={m_n_sep:.0f} "
                  f"(want >400)")
            print(f"    N→NG sep={n_ng_sep:.0f} "
                  f"(want >400)")
            print()
    except Exception as ex:
        results['nasal_place'] = {
            'error': str(ex),
            'pass': False}

    # Dark L vs bright L:
    # "still" (coda L) vs "like" (onset L)
    try:
        seg_still = synth_fn(
            'still', ['S','T','IH','L'])
        seg_like  = synth_fn(
            'like',  ['L','AY','K'])
        n_s = len(seg_still)
        n_l = len(seg_like)
        # Coda L is at end of "still"
        coda_l_seg  = seg_still[
            3*n_s//4:]
        # Onset L is at start of "like"
        onset_l_seg = seg_like[:n_l//4]

        _, f2_coda, _, _  = \
            measure_locus(coda_l_seg,  sr=sr)
        _, f2_onset, _, _ = \
            measure_locus(onset_l_seg, sr=sr)
        # Coda should be ~1000, onset ~1800
        dark_ok   = f2_coda  < 1400
        bright_ok = f2_onset > 1400
        ok = dark_ok and bright_ok
        results['dark_L'] = {
            'coda_L_f2':  round(f2_coda, 1),
            'onset_L_f2': round(f2_onset, 1),
            'coda_dark':  dark_ok,
            'onset_bright': bright_ok,
            'pass':       ok,
        }
        if verbose:
            sym = '✓' if ok else '✗'
            print(f"  [{sym}] Dark L "
                  f"(direction dimension):")
            print(f"    coda L  F2={f2_coda:.0f} "
                  f"(target <1400, dark)")
            print(f"    onset L F2={f2_onset:.0f} "
                  f"(target >1400, bright)")
            print()
    except Exception as ex:
        results['dark_L'] = {
            'error': str(ex),
            'pass': False}

    # R F3 suppression:
    # "here" — R should suppress F3 to ~1690
    try:
        seg_here = synth_fn(
            'here', ['H','IY','R'])
        n  = len(seg_here)
        r_seg = seg_here[2*n//3:]
        fmts  = estimate_formants(
            r_seg, sr=sr)
        f3_r  = fmts[2]
        ok    = 1550 <= f3_r <= 1900
        results['R_F3'] = {
            'F3_measured': round(f3_r, 1),
            'target':      (1550, 1900),
            'pass':        ok,
        }
        if verbose:
            sym = '✓' if ok else '✗'
            print(f"  [{sym}] R F3 suppression:")
            print(f"    F3={f3_r:.0f}Hz "
                  f"(target 1550–1900)")
            print()
    except Exception as ex:
        results['R_F3'] = {
            'error': str(ex),
            'pass': False}

    # N direction: "evening"
    # Coda N (syl 2) vs onset N (syl 3)
    try:
        seg_eve = synth_fn(
            'evening',
            ['IY','V','IH','N','IH','NG'])
        n = len(seg_eve)
        # Coda N ~60% into word
        coda_n_seg  = seg_eve[
            int(n*0.52):int(n*0.62)]
        # Onset N ~70% into word
        onset_n_seg = seg_eve[
            int(n*0.62):int(n*0.75)]

        f2m_c, f2s_c, f2e_c, dir_c = \
            measure_locus(coda_n_seg, sr=sr)
        f2m_o, f2s_o, f2e_o, dir_o = \
            measure_locus(onset_n_seg, sr=sr)
        dir_ok = (dir_c != dir_o or
                  abs(f2e_c - f2s_o) > 100)
        results['N_direction'] = {
            'coda_N_dir':  dir_c,
            'onset_N_dir': dir_o,
            'coda_slope':  round(
                f2e_c - f2s_c, 1),
            'onset_slope': round(
                f2e_o - f2s_o, 1),
            'distinguishable': dir_ok,
            'pass': dir_ok,
        }
        if verbose:
            sym = '✓' if dir_ok else '✗'
            print(f"  [{sym}] N direction "
                  f"(evening):")
            print(f"    coda N:  dir={dir_c}  "
                  f"slope={f2e_c-f2s_c:.0f}")
            print(f"    onset N: dir={dir_o}  "
                  f"slope={f2e_o-f2s_o:.0f}")
            print(f"    distinguishable: "
                  f"{dir_ok}")
            print()
    except Exception as ex:
        results['N_direction'] = {
            'error': str(ex),
            'pass': False}

    # K context: "key" vs "car"
    try:
        seg_key = synth_fn(
            'key', ['K','IY'])
        seg_car = synth_fn(
            'car', ['K','AA','R'])
        n_k = len(seg_key)
        n_c = len(seg_car)
        # K release is at start
        k_iy_seg = seg_key[:n_k//3]
        k_aa_seg = seg_car[:n_c//3]

        f2m_iy, _, _, _ = \
            measure_locus(k_iy_seg, sr=sr)
        f2m_aa, _, _, _ = \
            measure_locus(k_aa_seg, sr=sr)
        sep  = f2m_iy - f2m_aa
        ok   = sep > 300
        results['K_context'] = {
            'K_before_IY': round(f2m_iy, 1),
            'K_before_AA': round(f2m_aa, 1),
            'separation':  round(sep, 1),
            'pass':        ok,
        }
        if verbose:
            sym = '✓' if ok else '✗'
            print(f"  [{sym}] K velar context:")
            print(f"    K+IY  locus={f2m_iy:.0f} "
                  f"(want ~3000)")
            print(f"    K+AA  locus={f2m_aa:.0f} "
                  f"(want ~2400)")
            print(f"    sep={sep:.0f} "
                  f"(want >300)")
            print()
    except Exception as ex:
        results['K_context'] = {
            'error': str(ex),
            'pass': False}

    n_pass = sum(1 for v in
                 results.values()
                 if v.get('pass', False))
    n_total = len(results)
    if verbose:
        print(f"  Relational: "
              f"{n_pass}/{n_total} pass")
        print()

    return results


# ============================================================
# LOCUS BOOTSTRAP
#
# The engine measures its own
# place-of-articulation space.
# No external reference needed.
# Synthesize each place, measure,
# use the measurement as the definition.
# ============================================================

def bootstrap_locus_table(
        synth_fn, sr=SR, verbose=True):
    """
    Bootstrap the locus table from
    self-measurement.

    For each consonant place:
      Synthesize a CV syllable with
      a neutral vowel (AH).
      Measure F2 at the consonant release.
      Record as the measured locus.

    Compare to LOCUS_F2_BASE targets.
    Report discrepancies.

    This is the deepest form of
    self-reference: the engine
    does not assume its loci —
    it measures them.
    """
    if verbose:
        print()
        print("  LOCUS BOOTSTRAP")
        print("  Synthesize → Measure → "
              "Compare to table")
        print()

    test_cases = [
        # (place, ph, word, phones)
        ('bilabial',     'M', 'mah',
         ['M', 'AH']),
        ('bilabial',     'B', 'bah',
         ['B', 'AH']),
        ('labiodental',  'V', 'vah',
         ['V', 'AH']),
        ('dental',       'DH','dha',
         ['DH', 'AH']),
        ('alveolar',     'N', 'nah',
         ['N', 'AH']),
        ('alveolar',     'D', 'dah',
         ['D', 'AH']),
        ('alveolar',     'Z', 'za',
         ['Z', 'AH']),
        ('postalveolar', 'ZH','zha',
         ['ZH', 'AH']),
        ('palatal',      'Y', 'yah',
         ['Y', 'AH']),
        ('velar',        'NG','ang',
         ['AE', 'NG']),
        ('rhotic',       'R', 'rah',
         ['R', 'AH']),
    ]

    measured_loci = {}

    for place, ph, word, phones in \
            test_cases:
        try:
            seg  = synth_fn(word, phones)
            n    = len(seg)
            # Onset consonant: measure
            # first quarter of segment
            cons_seg = seg[:n//3]
            fmts     = estimate_formants(
                cons_seg, sr=sr)
            f2_meas  = fmts[1]
            f2_tgt_lo, f2_tgt_hi = \
                LOCUS_TARGETS.get(
                    place, (0, 5000))
            tgt_center = (
                f2_tgt_lo + f2_tgt_hi) / 2
            offset = f2_meas - tgt_center
            ok = (f2_tgt_lo <= f2_meas
                  <= f2_tgt_hi)

            measured_loci[ph] = {
                'place':       place,
                'measured_f2': round(
                    f2_meas, 1),
                'target':      (f2_tgt_lo,
                                f2_tgt_hi),
                'offset':      round(
                    offset, 1),
                'pass':        ok,
            }

            if verbose:
                sym = '✓' if ok else '✗'
                print(f"  [{sym}] {ph:4s} "
                      f"({place:14s})  "
                      f"F2={f2_meas:6.0f}  "
                      f"target="
                      f"({f2_tgt_lo:.0f}–"
                      f"{f2_tgt_hi:.0f})  "
                      f"offset={offset:+.0f}")
        except Exception as ex:
            measured_loci[ph] = {
                'error': str(ex),
                'pass': False}

    if verbose:
        n_p = sum(
            1 for v in
            measured_loci.values()
            if v.get('pass', False))
        print(f"\n  Bootstrap: "
              f"{n_p}/{len(measured_loci)} "
              f"loci within target range")
        print()

    return measured_loci


# ============================================================
# RARFL SELF-CORRECTION LOOP
# (generalized from v1 Z-gain search)
# ============================================================

def rarfl_tune(
        synth_fn,
        check_fn,
        param_name,
        param_init,
        param_lo,
        param_hi,
        max_iter=10,
        verbose=True):
    """
    Generalized RARFL self-correction loop.

    synth_fn(param_value) → segment
    check_fn(segment)     → (pass_bool,
                              measured_value,
                              target_str)

    Performs binary search on param_value
    until check_fn returns True.

    Returns best param_value found.
    """
    lo   = param_lo
    hi   = param_hi
    best = param_init

    if verbose:
        print(f"\n  RARFL tuning: {param_name}")
        print(f"  range=[{lo:.3f}, {hi:.3f}]")

    for i in range(max_iter):
        mid = (lo + hi) / 2.0
        seg = synth_fn(mid)
        ok, measured, target = \
            check_fn(seg)

        if verbose:
            sym = '✓' if ok else '✗'
            print(f"  [{sym}] iter {i+1}: "
                  f"param={mid:.4f}  "
                  f"measured={measured}  "
                  f"target={target}")

        best = mid
        if ok:
            if verbose:
                print(f"  → converged at "
                      f"{mid:.4f}")
            break
        else:
            # If measured < target: increase
            # (generalized: check_fn
            # should return measured as float)
            if isinstance(measured, float) \
               and isinstance(target, str):
                try:
                    tv = float(
                        target.split('≥')[1]
                        .strip()
                        if '≥' in target
                        else target.split(
                            '<=')[1].strip())
                    if measured < tv:
                        lo = mid
                    else:
                        hi = mid
                except Exception:
                    lo = mid
            else:
                lo = mid

    return best


# ============================================================
# MAIN DIAGNOSTIC ENTRY POINT
# ============================================================

class PhoneticSelfRef:
    """
    Phonetic self-reference system.
    Three levels of acoustic self-awareness.

    Usage:
      psr = PhoneticSelfRef(sr=44100)
      psr.run_all(synth_fn)
    """

    def __init__(self, sr=SR):
        self.sr      = sr
        self.results = {}

    def run_all(self, synth_fn,
                verbose=True):
        """
        Run all three levels of diagnostic
        plus relational + bootstrap.

        synth_fn(word, phones) → segment

        Prints a full portrait of the
        voice's acoustic state.
        """
        print()
        print("=" * 56)
        print("  PHONETIC SELF-REFERENCE v2")
        print("  Three-level acoustic portrait")
        print("=" * 56)

        # ── Level 1: per-phoneme ──────────────
        print()
        print("  LEVEL 1: ACOUSTIC IDENTITY")
        print()

        l1_results = {}
        test_phonemes = [
            # (ph, word, phones, segment_slice)
            # slice: fraction tuple (start, end)
            ('S',   'voice',
             ['V','OY','S'],     (0.66, 1.0)),
            ('Z',   'was',
             ['W','AH','Z'],     (0.66, 1.0)),
            ('SH',  'she',
             ['SH','IY'],        (0.0,  0.4)),
            ('ZH',  'vision',
             ['V','IH','ZH','AH','N'], (0.4,0.6)),
            ('M',   'am',
             ['AE','M'],         (0.5,  1.0)),
            ('N',   'an',
             ['AE','N'],         (0.5,  1.0)),
            ('NG',  'ring',
             ['R','IH','NG'],    (0.7,  1.0)),
            ('R',   'here',
             ['H','IY','R'],     (0.65, 1.0)),
            ('L',   'all',
             ['AO','L'],         (0.55, 1.0)),
            ('IH',  'him',
             ['HH','IH','M'],    (0.3,  0.7)),
            ('AH',  'but',
             ['B','AH','T'],     (0.3,  0.7)),
            ('IY',  'beat',
             ['B','IY','T'],     (0.3,  0.7)),
            ('ER',  'her',
             ['HH','ER'],        (0.4,  0.9)),
            ('JH',  'gin',
             ['JH','IH','N'],    (0.0,  0.5)),
            ('CH',  'church',
             ['CH','ER','CH'],   (0.0,  0.4)),
        ]

        for ph, word, phones, slc in \
                test_phonemes:
            try:
                seg = synth_fn(word, phones)
                n   = len(seg)
                s   = int(slc[0] * n)
                e   = int(slc[1] * n)
                ph_seg = seg[s:e]
                res, ok = \
                    check_phoneme_l1(
                        ph, ph_seg,
                        sr=self.sr,
                        verbose=verbose)
                l1_results[ph] = {
                    'results': res,
                    'pass':    ok,
                }
            except Exception as ex:
                l1_results[ph] = {
                    'error': str(ex),
                    'pass':  False,
                }

        self.results['level1'] = l1_results
        n_pass = sum(1 for v in
                     l1_results.values()
                     if v.get('pass'))
        print(f"\n  L1 total: "
              f"{n_pass}/{len(l1_results)} "
              f"pass")

        # ── Level 2: locus ────────────────────
        print()
        print("  LEVEL 2: LOCUS IDENTITY")
        print()

        l2_results = {}
        locus_tests = [
            # (ph, word, phones, slc, dir)
            ('N',  'nah',
             ['N','AH'],    (0.0,0.4), 'onset'),
            ('N',  'an',
             ['AE','N'],    (0.5,1.0), 'coda'),
            ('M',  'mah',
             ['M','AH'],    (0.0,0.4), 'onset'),
            ('M',  'am',
             ['AE','M'],    (0.5,1.0), 'coda'),
            ('D',  'dah',
             ['D','AH'],    (0.0,0.4), 'onset'),
            ('L',  'like',
             ['L','AY','K'],(0.0,0.3), 'onset'),
            ('L',  'still',
             ['S','T','IH','L'],(0.75,1.0),'coda'),
            ('R',  'rah',
             ['R','AH'],    (0.0,0.4), 'onset'),
            ('K',  'key',
             ['K','IY'],    (0.0,0.4), 'onset'),
            ('K',  'car',
             ['K','AA','R'],(0.0,0.4), 'onset'),
        ]

        for ph, word, phones, slc, direction \
                in locus_tests:
            try:
                seg   = synth_fn(word, phones)
                n     = len(seg)
                s     = int(slc[0] * n)
                e     = int(slc[1] * n)
                cs    = seg[s:e]

                # Determine adjacent vowel
                adj = None
                if direction == 'onset':
                    for p in phones[
                            phones.index(ph)+1:]:
                        if p in (
                            'IY','IH','EH','AE',
                            'AH','AO','AA','UW',
                            'UH','OW','ER','AY',
                            'AW','OY','EY'):
                            adj = p; break
                else:
                    for p in reversed(
                            phones[:phones.index(ph)]):
                        if p in (
                            'IY','IH','EH','AE',
                            'AH','AO','AA','UW',
                            'UH','OW','ER','AY',
                            'AW','OY','EY'):
                            adj = p; break

                key = f"{ph}_{direction}"
                res, ok = check_phoneme_l2(
                    ph, cs,
                    sr=self.sr,
                    expected_direction=direction,
                    adjacent_vowel=adj,
                    verbose=verbose)
                l2_results[key] = {
                    'results': res,
                    'pass':    ok,
                }
            except Exception as ex:
                key = f"{ph}_{direction}"
                l2_results[key] = {
                    'error': str(ex),
                    'pass':  False,
                }

        self.results['level2'] = l2_results
        n_pass = sum(1 for v in
                     l2_results.values()
                     if v.get('pass'))
        print(f"\n  L2 total: "
              f"{n_pass}/{len(l2_results)} "
              f"pass")

        # ── Level 3: phrase coherence ─────────
        print()
        print("  LEVEL 3: PHRASE COHERENCE")
        print()

        l3_results = {}
        phrase_tests = [
            ('the_voice',
             [('the',   ['DH','AH']),
              ('voice', ['V','OY','S']),
              ('was',   ['W','AH','Z']),
              ('here',  ['H','IY','R'])],
             'normal'),
            ('i_am_here',
             [('I',    ['AY']),
              ('am',   ['AE','M']),
              ('here', ['H','IY','R'])],
             'normal'),
        ]

        try:
            from voice_physics_v17 import (
                synth_phrase as sp17,
                ARC_NORMAL, ARC_GRIEF,
            )
            for label, words, arc_lbl in \
                    phrase_tests:
                seg = sp17(
                    words,
                    punctuation='.',
                    arc_type=ARC_NORMAL,
                    add_ghost=True)
                res, score = check_phrase_l3(
                    seg,
                    arc_type_label=arc_lbl,
                    sr=self.sr,
                    verbose=verbose)
                l3_results[label] = {
                    'results': res,
                    'score':   score,
                }
        except Exception as ex:
            l3_results['error'] = str(ex)
            if verbose:
                print(f"  L3 error: {ex}")

        self.results['level3'] = l3_results

        # ── Relational ────────────────────────
        rel = run_relational_diagnostic(
            synth_fn, sr=self.sr,
            verbose=verbose)
        self.results['relational'] = rel

        # ── Bootstrap ────────────────────────
        boot = bootstrap_locus_table(
            synth_fn, sr=self.sr,
            verbose=verbose)
        self.results['bootstrap'] = boot

        # ── Summary ───────────────────────────
        self.print_summary()
        return self.results

    def print_summary(self):
        r = self.results
        print()
        print("=" * 56)
        print("  SELF-REFERENCE SUMMARY")
        print("=" * 56)

        if 'level1' in r:
            n = len(r['level1'])
            p = sum(1 for v in
                    r['level1'].values()
                    if v.get('pass'))
            print(f"  L1 Acoustic:   {p:2d}/{n} "
                  f"{'✓' if p==n else '~'}")

        if 'level2' in r:
            n = len(r['level2'])
            p = sum(1 for v in
                    r['level2'].values()
                    if v.get('pass'))
            print(f"  L2 Locus:      {p:2d}/{n} "
                  f"{'✓' if p==n else '~'}")

        if 'level3' in r:
            scores = [v.get('score', 0.0)
                      for v in r['level3'].values()
                      if isinstance(v, dict)
                      and 'score' in v]
            if scores:
                avg = np.mean(scores)
                print(f"  L3 Coherence:  "
                      f"avg score={avg:.2f} "
                      f"{'✓' if avg > 0.6 else '~'}")

        if 'relational' in r:
            n = len(r['relational'])
            p = sum(1 for v in
                    r['relational'].values()
                    if v.get('pass'))
            print(f"  Relational:    {p:2d}/{n} "
                  f"{'✓' if p==n else '~'}")

        if 'bootstrap' in r:
            n = len(r['bootstrap'])
            p = sum(1 for v in
                    r['bootstrap'].values()
                    if v.get('pass'))
            print(f"  Locus Boot:    {p:2d}/{n} "
                  f"{'✓' if p==n else '~'}")

        print("=" * 56)
        print()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print()
    print("PHONETIC SELF-REFERENCE v2")
    print("Synthesize → Analyze → "
          "Compare → Adjust")
    print()

    try:
        from voice_physics_v17 import (
            synth_phrase, _ola_stretch,
            recalibrate_gains_v8,
            SR as ENGINE_SR,
            PITCH, DIL, ARC_NORMAL,
        )
        has_v17 = True
    except ImportError:
        has_v17 = False
        print("  voice_physics_v17 not found.")
        print("  Running analysis-only mode.")

    os.makedirs("output_play",
                 exist_ok=True)

    if has_v17:
        recalibrate_gains_v8(sr=ENGINE_SR)

        def synth_fn(word, phones):
            return synth_phrase(
                [(word, phones)],
                punctuation='.',
                add_breath=False,
                add_ghost=False)

        psr = PhoneticSelfRef(sr=ENGINE_SR)
        results = psr.run_all(
            synth_fn, verbose=True)

    else:
        # Stub for analysis-only testing
        print("  Analysis functions available.")
        print("  Provide synth_fn to run "
              "full diagnostic.")
        psr = PhoneticSelfRef()
        print()
        print("  Example usage:")
        print("  from phonetic_self_reference "
              "import PhoneticSelfRef")
        print("  psr = PhoneticSelfRef()")
        print("  psr.run_all(synth_fn)")
