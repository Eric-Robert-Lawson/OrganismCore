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
    Ghost duration detection at syllable
    boundaries.
    Tonnetz position recovery per nucleus vowel.
    Rhyme convergence check between phrases.

RARFL self-correction loop:
  Synthesize → Measure → Compare →
  Adjust → Re-synthesize → Converge.

HOW TO RUN:
  From the directory containing
  voice_physics_v17.py:

    python phonetic_self_reference.py

  Or with explicit path:

    python phonetic_self_reference.py \
        --engine-path /path/to/voice/files

  Or from another directory:

    import sys
    sys.path.insert(0, '/path/to/voice/files')
    from phonetic_self_reference import (
        PhoneticSelfRef,
    )
"""

import numpy as np
from scipy.signal import (
    butter, lfilter, find_peaks,
)
import os
import sys
import argparse

SR    = 44100
DTYPE = np.float32

def f32(x):
    return np.asarray(x, dtype=DTYPE)


# ============================================================
# PATH RESOLUTION
#
# The voice physics files are a chain:
#   v17 → v16 → v15 → v14 → v13 → ...
# They must all be in the same directory,
# and that directory must be on sys.path
# before any import is attempted.
#
# This block resolves the path from:
#   1. --engine-path CLI argument
#   2. VOICE_ENGINE_PATH environment variable
#   3. The directory of this script
#   4. The current working directory
#
# The first path where voice_physics_v17.py
# exists wins.
# ============================================================

def _resolve_engine_path(explicit=None):
    """
    Find the directory containing
    voice_physics_v17.py.

    Returns the path string, or None
    if not found.
    """
    candidates = []

    if explicit:
        candidates.append(
            os.path.abspath(explicit))

    env = os.environ.get(
        'VOICE_ENGINE_PATH')
    if env:
        candidates.append(
            os.path.abspath(env))

    # Directory of this script
    candidates.append(
        os.path.dirname(
            os.path.abspath(__file__)))

    # Current working directory
    candidates.append(
        os.path.abspath(os.getcwd()))

    for c in candidates:
        probe = os.path.join(
            c, 'voice_physics_v17.py')
        if os.path.isfile(probe):
            return c

    return None


def _add_engine_path(path):
    """
    Add engine path to sys.path
    if not already present.
    """
    if path and path not in sys.path:
        sys.path.insert(0, path)


# ============================================================
# LEVEL 1: ACOUSTIC IDENTITY TARGETS
# ============================================================

PHONEME_TARGETS = {
    # ── Vowels ──────────────────────────────
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
        'f3': (1550, 1820),
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
    # ── Nasals ───────────────────────────────
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
        'f3': (1550, 1820),
        'hnr_min': 8.0,
        'sibilance_max': 0.05,
    },
    'L': {
        'voiced': True,
        'f2': (800,  1200),
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
# ============================================================

LOCUS_TARGETS = {
    'bilabial':      (580,  860),
    'labiodental':   (900,  1300),
    'dental':        (1400, 1800),
    'alveolar':      (1600, 2000),
    'lateral_dark':  (800,  1200),
    'lateral_onset': (1600, 2000),
    'postalveolar':  (1900, 2300),
    'palatal':       (2100, 2500),
    'velar_front':   (2700, 3200),
    'velar_mid':     (2200, 2700),
    'velar_back':    (1700, 2200),
    'glottal':       (300,  700),
    'rhotic':        (600,  1000),
}

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
    r1 = float(np.sum(
        seg[:n - T0] * seg[T0:]))
    if r0 < 1e-12:
        return 0.0
    ratio = np.clip(r1 / r0, -0.999, 0.999)
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
        order = min(
            int(2 + sr / 1000),
            n // 3, 40)

    pre = np.append(
        seg[0],
        seg[1:] - 0.97 * seg[:-1])

    try:
        R = np.array([
            float(np.dot(
                pre[:n - k], pre[k:]))
            for k in range(order + 1)])
        if abs(R[0]) < 1e-10:
            return [0.0] * n_formants

        a   = np.zeros(order)
        err = R[0]
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
            np.append([1.0], -a),
            n=n_fft)
        spec  = 1.0 / (
            np.abs(H) ** 2 + 1e-10)
        freqs = np.fft.rfftfreq(
            n_fft, d=1.0 / sr)

        mask  = (freqs > 100) & \
                (freqs < 5500)
        s_m   = spec[mask]
        f_m   = freqs[mask]
        if len(s_m) == 0:
            return [0.0] * n_formants

        dist = max(1, int(
            80.0 / max(
                freqs[1] - freqs[0],
                0.1)))
        peaks, _ = find_peaks(
            s_m,
            height=np.max(s_m) * 0.08,
            distance=dist)

        formants = sorted([
            float(f_m[p])
            for p in peaks])
        while len(formants) < n_formants:
            formants.append(0.0)
        return formants[:n_formants]

    except Exception:
        return [0.0] * n_formants


def measure_f2_trajectory(
        seg, sr=SR, n_frames=8):
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
        fmts = estimate_formants(
            seg, sr=sr)
        f2 = fmts[1]
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
        best_f0 = 0.0
        best_r  = 0.0
        for hz in range(pitch_lo,
                         pitch_hi, 5):
            lag = int(sr / hz)
            if lag >= len(frs):
                continue
            r  = float(np.sum(
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

    idxs   = [i for i, v in voiced]
    vals   = [v for i, v in voiced]
    slope  = ((vals[-1] - vals[0]) /
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

    Returns list of
      (start_ms, end_ms, duration_ms, amp)
    """
    seg       = f32(seg)
    n         = len(seg)
    frame_ms  = 5.0
    frame_n   = int(frame_ms / 1000 * sr)
    if frame_n < 2:
        return []

    n_frames  = n // frame_n
    energy    = np.array([
        float(np.mean(
            seg[i*frame_n:
                (i+1)*frame_n]**2))
        for i in range(n_frames)])
    if len(energy) == 0:
        return []

    e_norm = energy / (
        np.max(energy) + 1e-10)

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
           i > 0 and \
           e_norm[i-1] > \
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
                amp  = float(np.sqrt(
                    np.mean(
                        energy[
                            ghost_start:i])))
                ghosts.append((
                    s_ms, e_ms,
                    e_ms - s_ms, amp))
            in_ghost = False

    return ghosts


def measure_tonnetz_position(
        seg, sr=SR,
        vowel_f=None,
        vowel_tonnetz=None):
    """
    Estimate the Tonnetz position of
    the dominant vowel in a segment.

    Returns:
      (phoneme_symbol, (a,b), f1, f2)
    """
    fmts = estimate_formants(seg, sr=sr)
    f1   = fmts[0]
    f2   = fmts[1]

    if f1 < 50 or f2 < 200:
        return (None, (0, 0), f1, f2)

    if vowel_f is None:
        try:
            from voice_physics_v3 import \
                VOWEL_F as vf
            vowel_f = vf
        except ImportError:
            return (None, (0,0), f1, f2)

    if vowel_tonnetz is None:
        try:
            from tonnetz_engine import \
                VOWEL_TONNETZ as vt
            vowel_tonnetz = vt
        except ImportError:
            vowel_tonnetz = {}

    best_ph   = None
    best_dist = float('inf')
    for ph, data in vowel_f.items():
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
        dist = ((f1-tf1)**2 +
                (f2-tf2)**2)**0.5
        if dist < best_dist:
            best_dist = dist
            best_ph   = ph

    tn = vowel_tonnetz.get(
        best_ph, (0, 0)) \
        if best_ph else (0, 0)
    return (best_ph, tn, f1, f2)


def measure_locus(cons_seg, sr=SR):
    """
    Estimate F2 locus from a consonant
    segment.

    Returns:
      f2_locus, f2_start, f2_end, direction
      direction: 'onset'|'coda'|'flat'
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
# LEVEL 1 CHECK
# ============================================================

def check_phoneme_l1(ph, seg, sr=SR,
                      verbose=True):
    target  = PHONEME_TARGETS.get(ph)
    if target is None:
        return {}, True

    seg     = f32(seg)
    results = {}
    failed  = []

    # Voiced
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
    band = target.get(
        'sibilance_band', (5500, 13000))
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

    # Z: sibilance over voicing
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
            p = '  ✓' if v['pass'] \
                else '  ✗'
            m = v.get('measured', '?')
            t = v.get('target', '')
            print(f"    {p} {k}:  "
                  f"measured={m}  "
                  f"target={t}")

    return results, all_pass


# ============================================================
# LEVEL 2 CHECK
# ============================================================

def check_phoneme_l2(
        ph, seg, sr=SR,
        expected_direction=None,
        adjacent_vowel=None,
        verbose=True):
    """
    Level 2 locus identity check.
    """
    # Determine locus class
    if ph == 'L':
        if expected_direction == 'coda':
            locus_class = 'lateral_dark'
        elif expected_direction == 'onset':
            locus_class = 'lateral_onset'
        else:
            locus_class = 'lateral_dark'
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

    if locus_class is None:
        if verbose:
            print(f"  [L2 ?] {ph}: "
                  f"no locus class")
        return results, True

    f2m, f2s, f2e, direction = \
        measure_locus(seg, sr=sr)

    if locus_class in LOCUS_TARGETS:
        lo, hi   = LOCUS_TARGETS[locus_class]
        locus_ok = lo <= f2m <= hi
        results['locus_f2'] = {
            'class':    locus_class,
            'target':   (lo, hi),
            'measured': round(f2m, 1),
            'pass':     locus_ok,
        }
        if not locus_ok:
            all_pass = False

    if expected_direction is not None:
        dir_ok = (direction ==
                  expected_direction)
        results['direction'] = {
            'target':   expected_direction,
            'measured': direction,
            'f2_start': round(f2s, 1),
            'f2_end':   round(f2e, 1),
            'slope':    round(f2e - f2s, 1),
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
# LEVEL 3 CHECK
# ============================================================

def check_phrase_l3(
        seg,
        arc_type_label='normal',
        sr=SR,
        verbose=True):
    """
    Level 3: phrase-level qualia check.
    """
    seg     = f32(seg)
    results = {}

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
        'mean_hz':       round(f0_mean, 1),
        'range_hz':      round(f0_range, 1),
        'slope':         round(arc_slope, 2),
        'peak_pos':      round(peak_pos, 2),
        'voiced_frames': len(voiced_f0),
        'total_frames':  len(f0_vals),
    }

    ghosts = detect_ghost_boundaries(
        seg, sr=sr)
    results['ghosts'] = {
        'count':      len(ghosts),
        'durations':  [round(g[2], 1)
                       for g in ghosts],
        'amplitudes': [round(g[3], 4)
                       for g in ghosts],
    }

    ph, tonnetz, f1, f2 = \
        measure_tonnetz_position(
            seg, sr=sr)
    results['tonnetz'] = {
        'recovered_ph': ph,
        'position':     tonnetz,
        'f1_hz':        round(f1, 1),
        'f2_hz':        round(f2, 1),
    }

    n_frames = max(len(f0_vals), 1)
    v_frac   = len(voiced_f0) / n_frames
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
        sym = ('✓' if score > 0.6
               else '~' if score > 0.35
               else '✗')
        print(f"  [L3 {sym}] phrase "
              f"coherence={score:.2f} "
              f"({arc_type_label})")
        print(f"    F0: "
              f"mean={f0_mean:.0f}Hz "
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
# ============================================================

def run_relational_diagnostic(
        synth_fn, sr=SR, verbose=True):
    """
    Tests phoneme pairs that differ in
    exactly one dimension.
    """
    results = {}

    if verbose:
        print()
        print("  RELATIONAL DIAGNOSTIC")
        print()

    # S vs Z
    try:
        seg_s = synth_fn(
            'voice', ['V','OY','S'])
        seg_z = synth_fn(
            'was',   ['W','AH','Z'])
        n_s   = len(seg_s)
        n_z   = len(seg_z)
        sib_s = measure_sibilance(
            seg_s[2*n_s//3:], sr=sr,
            band=(5500, 13000))
        sib_z = measure_sibilance(
            seg_z[2*n_z//3:], sr=sr,
            band=(5500, 13000))
        hnr_s = measure_hnr(
            seg_s[2*n_s//3:], sr=sr)
        hnr_z = measure_hnr(
            seg_z[2*n_z//3:], sr=sr)
        sib_gap = abs(sib_s - sib_z)
        hnr_gap = hnr_z - hnr_s
        ok = (sib_z >= 0.35 and
              hnr_gap > 3.0 and
              sib_gap < 0.30)
        results['S_vs_Z'] = {
            'S_sib':  round(sib_s, 3),
            'Z_sib':  round(sib_z, 3),
            'S_hnr':  round(hnr_s, 1),
            'Z_hnr':  round(hnr_z, 1),
            'sib_gap':round(sib_gap, 3),
            'hnr_gap':round(hnr_gap, 1),
            'pass':   ok,
        }
        if verbose:
            sym = '✓' if ok else '✗'
            print(f"  [{sym}] S vs Z "
                  f"(voicing dimension):")
            print(f"    S sib={sib_s:.3f}  "
                  f"hnr={hnr_s:.1f}dB")
            print(f"    Z sib={sib_z:.3f}  "
                  f"hnr={hnr_z:.1f}dB")
            print(f"    sib_gap="
                  f"{sib_gap:.3f} (<0.30)")
            print(f"    hnr_gap="
                  f"{hnr_gap:.1f} (>3.0)")
            print()
    except Exception as ex:
        results['S_vs_Z'] = {
            'error': str(ex), 'pass': False}
        if verbose:
            print(f"  [✗] S vs Z: {ex}")

    # M vs N vs NG place
    try:
        segs = {}
        for ph, word, phones in [
            ('M',  'am',  ['AE', 'M']),
            ('N',  'an',  ['AE', 'N']),
            ('NG', 'ang', ['AE', 'NG']),
        ]:
            seg = synth_fn(word, phones)
            n   = len(seg)
            segs[ph] = seg[n//2:]

        loci = {}
        for ph in ('M', 'N', 'NG'):
            fmts    = estimate_formants(
                segs[ph], sr=sr)
            loci[ph] = fmts[1]

        m_n_sep  = loci['N']  - loci['M']
        n_ng_sep = loci['NG'] - loci['N']
        ok = (m_n_sep > 400 and
              n_ng_sep > 400)
        results['nasal_place'] = {
            'M_f2':     round(loci['M'],  1),
            'N_f2':     round(loci['N'],  1),
            'NG_f2':    round(loci['NG'], 1),
            'M_N_sep':  round(m_n_sep,    1),
            'N_NG_sep': round(n_ng_sep,   1),
            'pass':     ok,
        }
        if verbose:
            sym = '✓' if ok else '✗'
            print(f"  [{sym}] M vs N vs NG "
                  f"(place dimension):")
            for ph in ('M', 'N', 'NG'):
                print(f"    {ph}  "
                      f"F2={loci[ph]:.0f}")
            print(f"    M→N sep="
                  f"{m_n_sep:.0f} (>400)")
            print(f"    N→NG sep="
                  f"{n_ng_sep:.0f} (>400)")
            print()
    except Exception as ex:
        results['nasal_place'] = {
            'error': str(ex), 'pass': False}
        if verbose:
            print(f"  [✗] nasal place: {ex}")

    # Dark L vs onset L
    try:
        seg_still = synth_fn(
            'still', ['S','T','IH','L'])
        seg_like  = synth_fn(
            'like',  ['L','AY','K'])
        n_s = len(seg_still)
        n_l = len(seg_like)
        coda_l  = seg_still[3*n_s//4:]
        onset_l = seg_like[:n_l//4]

        _, f2_coda, _, _  = measure_locus(
            coda_l,  sr=sr)
        _, f2_onset, _, _ = measure_locus(
            onset_l, sr=sr)
        dark_ok   = f2_coda  < 1400
        bright_ok = f2_onset > 1400
        ok = dark_ok and bright_ok
        results['dark_L'] = {
            'coda_L_f2':    round(f2_coda,  1),
            'onset_L_f2':   round(f2_onset, 1),
            'coda_dark':    dark_ok,
            'onset_bright': bright_ok,
            'pass':         ok,
        }
        if verbose:
            sym = '✓' if ok else '✗'
            print(f"  [{sym}] Dark L:")
            print(f"    coda L  "
                  f"F2={f2_coda:.0f} (<1400)")
            print(f"    onset L "
                  f"F2={f2_onset:.0f} (>1400)")
            print()
    except Exception as ex:
        results['dark_L'] = {
            'error': str(ex), 'pass': False}
        if verbose:
            print(f"  [✗] dark L: {ex}")

    # R F3 suppression
    try:
        seg_here = synth_fn(
            'here', ['H','IY','R'])
        n        = len(seg_here)
        r_seg    = seg_here[2*n//3:]
        fmts     = estimate_formants(
            r_seg, sr=sr)
        f3_r     = fmts[2]
        ok       = 1550 <= f3_r <= 1900
        results['R_F3'] = {
            'F3_measured': round(f3_r, 1),
            'target':      (1550, 1900),
            'pass':        ok,
        }
        if verbose:
            sym = '✓' if ok else '✗'
            print(f"  [{sym}] R F3 "
                  f"suppression:")
            print(f"    F3={f3_r:.0f}Hz "
                  f"(target 1550–1900)")
            print()
    except Exception as ex:
        results['R_F3'] = {
            'error': str(ex), 'pass': False}
        if verbose:
            print(f"  [✗] R F3: {ex}")

    # N direction in "evening"
    try:
        seg_eve = synth_fn(
            'evening',
            ['IY','V','IH','N',
             'IH','NG'])
        n    = len(seg_eve)
        cn_s = seg_eve[int(n*0.52):
                       int(n*0.62)]
        on_s = seg_eve[int(n*0.62):
                       int(n*0.75)]
        _, f2s_c, f2e_c, dir_c = \
            measure_locus(cn_s, sr=sr)
        _, f2s_o, f2e_o, dir_o = \
            measure_locus(on_s, sr=sr)
        dir_ok = (dir_c != dir_o or
                  abs(f2e_c - f2s_o) > 100)
        results['N_direction'] = {
            'coda_dir':    dir_c,
            'onset_dir':   dir_o,
            'coda_slope':  round(
                f2e_c - f2s_c, 1),
            'onset_slope': round(
                f2e_o - f2s_o, 1),
            'pass':        dir_ok,
        }
        if verbose:
            sym = '✓' if dir_ok else '✗'
            print(f"  [{sym}] N direction "
                  f"(evening):")
            print(f"    coda N:  "
                  f"dir={dir_c}  "
                  f"slope="
                  f"{f2e_c-f2s_c:.0f}")
            print(f"    onset N: "
                  f"dir={dir_o}  "
                  f"slope="
                  f"{f2e_o-f2s_o:.0f}")
            print()
    except Exception as ex:
        results['N_direction'] = {
            'error': str(ex), 'pass': False}
        if verbose:
            print(f"  [✗] N direction: {ex}")

    # K context
    try:
        seg_key = synth_fn(
            'key', ['K','IY'])
        seg_car = synth_fn(
            'car', ['K','AA','R'])
        n_k = len(seg_key)
        n_c = len(seg_car)
        f2m_iy, _, _, _ = measure_locus(
            seg_key[:n_k//3], sr=sr)
        f2m_aa, _, _, _ = measure_locus(
            seg_car[:n_c//3], sr=sr)
        sep  = f2m_iy - f2m_aa
        ok   = sep > 300
        results['K_context'] = {
            'K_IY': round(f2m_iy, 1),
            'K_AA': round(f2m_aa, 1),
            'sep':  round(sep, 1),
            'pass': ok,
        }
        if verbose:
            sym = '✓' if ok else '✗'
            print(f"  [{sym}] K context:")
            print(f"    K+IY={f2m_iy:.0f} "
                  f"K+AA={f2m_aa:.0f} "
                  f"sep={sep:.0f} (>300)")
            print()
    except Exception as ex:
        results['K_context'] = {
            'error': str(ex), 'pass': False}
        if verbose:
            print(f"  [✗] K context: {ex}")

    n_pass = sum(
        1 for v in results.values()
        if v.get('pass', False))
    if verbose:
        print(f"  Relational: "
              f"{n_pass}/{len(results)} pass")
    return results


# ============================================================
# LOCUS BOOTSTRAP
# ============================================================

def bootstrap_locus_table(
        synth_fn, sr=SR, verbose=True):
    """
    Synthesize each place, measure F2,
    use measurement as locus definition.
    """
    if verbose:
        print()
        print("  LOCUS BOOTSTRAP")
        print()

    test_cases = [
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
            fmts = estimate_formants(
                seg[:n//3], sr=sr)
            f2   = fmts[1]

            # Map place to LOCUS_TARGETS key
            lk = (place if place in
                  LOCUS_TARGETS else
                  'velar_mid'
                  if place == 'velar'
                  else place)
            lo_t, hi_t = LOCUS_TARGETS.get(
                lk, (0, 5000))
            center = (lo_t + hi_t) / 2
            offset = f2 - center
            ok     = lo_t <= f2 <= hi_t

            measured_loci[ph] = {
                'place':    place,
                'f2_meas':  round(f2, 1),
                'target':   (lo_t, hi_t),
                'offset':   round(offset, 1),
                'pass':     ok,
            }
            if verbose:
                sym = '✓' if ok else '✗'
                print(f"  [{sym}] "
                      f"{ph:4s} "
                      f"({place:14s})  "
                      f"F2={f2:6.0f}  "
                      f"target="
                      f"({lo_t:.0f}–"
                      f"{hi_t:.0f})  "
                      f"offset={offset:+.0f}")
        except Exception as ex:
            measured_loci[ph] = {
                'error': str(ex),
                'pass':  False}
            if verbose:
                print(f"  [✗] {ph}: {ex}")

    if verbose:
        n_p = sum(
            1 for v in
            measured_loci.values()
            if v.get('pass', False))
        print(f"\n  Bootstrap: "
              f"{n_p}/{len(measured_loci)} "
              f"within range")
    return measured_loci


# ============================================================
# MAIN CLASS
# ============================================================

class PhoneticSelfRef:

    def __init__(self, sr=SR):
        self.sr      = sr
        self.results = {}

    def run_all(self, synth_fn,
                verbose=True):

        print()
        print("=" * 56)
        print("  PHONETIC SELF-REFERENCE v2")
        print("=" * 56)

        # ── Level 1 ───────────────────────────
        print()
        print("  LEVEL 1: ACOUSTIC IDENTITY")
        print()

        l1 = {}
        tests_l1 = [
            ('S',   'voice',
             ['V','OY','S'],      (0.66,1.0)),
            ('Z',   'was',
             ['W','AH','Z'],      (0.66,1.0)),
            ('SH',  'she',
             ['SH','IY'],         (0.0, 0.4)),
            ('M',   'am',
             ['AE','M'],          (0.5, 1.0)),
            ('N',   'an',
             ['AE','N'],          (0.5, 1.0)),
            ('NG',  'ring',
             ['R','IH','NG'],     (0.7, 1.0)),
            ('R',   'here',
             ['H','IY','R'],      (0.65,1.0)),
            ('L',   'all',
             ['AO','L'],          (0.55,1.0)),
            ('IH',  'him',
             ['HH','IH','M'],     (0.3, 0.7)),
            ('IY',  'beat',
             ['B','IY','T'],      (0.3, 0.7)),
            ('AH',  'but',
             ['B','AH','T'],      (0.3, 0.7)),
            ('ER',  'her',
             ['HH','ER'],         (0.4, 0.9)),
            ('JH',  'gin',
             ['JH','IH','N'],     (0.0, 0.5)),
            ('CH',  'church',
             ['CH','ER','CH'],    (0.0, 0.4)),
            ('DH',  'the',
             ['DH','AH'],         (0.0, 0.4)),
            ('V',   'voice',
             ['V','OY','S'],      (0.0, 0.25)),
        ]

        for ph, word, phones, slc in \
                tests_l1:
            try:
                seg = synth_fn(word, phones)
                n   = len(seg)
                s   = int(slc[0] * n)
                e   = int(slc[1] * n)
                res, ok = check_phoneme_l1(
                    ph, seg[s:e],
                    sr=self.sr,
                    verbose=verbose)
                l1[ph] = {
                    'results': res,
                    'pass':    ok,
                }
            except Exception as ex:
                l1[ph] = {
                    'error': str(ex),
                    'pass':  False,
                }
                if verbose:
                    print(f"  [L1 ✗] "
                          f"{ph}: {ex}")

        self.results['level1'] = l1
        n_p = sum(
            1 for v in l1.values()
            if v.get('pass'))
        print(f"\n  L1 total: "
              f"{n_p}/{len(l1)} pass")

        # ── Level 2 ───────────────────────────
        print()
        print("  LEVEL 2: LOCUS IDENTITY")
        print()

        l2 = {}
        tests_l2 = [
            ('N',  'nah',
             ['N','AH'],            (0.0,0.4),
             'onset', None),
            ('N',  'an',
             ['AE','N'],            (0.5,1.0),
             'coda',  'AE'),
            ('M',  'mah',
             ['M','AH'],            (0.0,0.4),
             'onset', None),
            ('M',  'am',
             ['AE','M'],            (0.5,1.0),
             'coda',  'AE'),
            ('L',  'like',
             ['L','AY','K'],        (0.0,0.3),
             'onset', 'AY'),
            ('L',  'still',
             ['S','T','IH','L'],    (0.75,1.0),
             'coda',  'IH'),
            ('R',  'rah',
             ['R','AH'],            (0.0,0.4),
             'onset', None),
            ('K',  'key',
             ['K','IY'],            (0.0,0.4),
             'onset', 'IY'),
            ('K',  'car',
             ['K','AA','R'],        (0.0,0.4),
             'onset', 'AA'),
            ('D',  'dah',
             ['D','AH'],            (0.0,0.4),
             'onset', None),
        ]

        for (ph, word, phones,
             slc, direction, adj) in \
                tests_l2:
            key = f"{ph}_{direction}"
            try:
                seg   = synth_fn(
                    word, phones)
                n     = len(seg)
                s     = int(slc[0] * n)
                e     = int(slc[1] * n)
                res, ok = check_phoneme_l2(
                    ph, seg[s:e],
                    sr=self.sr,
                    expected_direction=\
                        direction,
                    adjacent_vowel=adj,
                    verbose=verbose)
                l2[key] = {
                    'results': res,
                    'pass':    ok,
                }
            except Exception as ex:
                l2[key] = {
                    'error': str(ex),
                    'pass':  False,
                }
                if verbose:
                    print(f"  [L2 ✗] "
                          f"{key}: {ex}")

        self.results['level2'] = l2
        n_p = sum(
            1 for v in l2.values()
            if v.get('pass'))
        print(f"\n  L2 total: "
              f"{n_p}/{len(l2)} pass")

        # ── Level 3 ───────────────────────────
        print()
        print("  LEVEL 3: PHRASE COHERENCE")
        print()

        l3 = {}
        try:
            from voice_physics_v17 import (
                synth_phrase as sp17,
                ARC_NORMAL, ARC_GRIEF,
            )
            phrase_tests = [
                ('the_voice',
                 [('the',   ['DH','AH']),
                  ('voice', ['V','OY','S']),
                  ('was',   ['W','AH','Z']),
                  ('here',  ['H','IY','R'])],
                 ARC_NORMAL, 'normal'),
                ('i_am_here',
                 [('I',    ['AY']),
                  ('am',   ['AE','M']),
                  ('here', ['H','IY','R'])],
                 ARC_NORMAL, 'normal'),
                ('i_am_here_grief',
                 [('I',    ['AY']),
                  ('am',   ['AE','M']),
                  ('here', ['H','IY','R'])],
                 ARC_GRIEF, 'grief'),
            ]
            for label, words, arc, arc_lbl \
                    in phrase_tests:
                try:
                    seg = sp17(
                        words,
                        punctuation='.',
                        arc_type=arc,
                        add_ghost=True)
                    res, score = \
                        check_phrase_l3(
                            seg,
                            arc_type_label=\
                                arc_lbl,
                            sr=self.sr,
                            verbose=verbose)
                    l3[label] = {
                        'results': res,
                        'score':   score,
                    }
                except Exception as ex:
                    l3[label] = {
                        'error': str(ex),
                        'score': 0.0,
                    }
                    if verbose:
                        print(f"  [L3 ✗] "
                              f"{label}: "
                              f"{ex}")
        except ImportError as e:
            if verbose:
                print(f"  L3 skip: {e}")

        self.results['level3'] = l3

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

        self._print_summary()
        return self.results

    def _print_summary(self):
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
            sym = '✓' if p == n else '~'
            print(f"  L1 Acoustic:   "
                  f"{p:2d}/{n}  {sym}")

        if 'level2' in r:
            n = len(r['level2'])
            p = sum(1 for v in
                    r['level2'].values()
                    if v.get('pass'))
            sym = '✓' if p == n else '~'
            print(f"  L2 Locus:      "
                  f"{p:2d}/{n}  {sym}")

        if 'level3' in r:
            scores = [
                v.get('score', 0.0)
                for v in
                r['level3'].values()
                if isinstance(v, dict)
                and 'score' in v]
            if scores:
                avg = float(np.mean(scores))
                sym = ('✓' if avg > 0.6
                       else '~')
                print(f"  L3 Coherence:  "
                      f"avg={avg:.2f}  {sym}")

        if 'relational' in r:
            n = len(r['relational'])
            p = sum(1 for v in
                    r['relational'].values()
                    if v.get('pass'))
            sym = '✓' if p == n else '~'
            print(f"  Relational:    "
                  f"{p:2d}/{n}  {sym}")

        if 'bootstrap' in r:
            n = len(r['bootstrap'])
            p = sum(1 for v in
                    r['bootstrap'].values()
                    if v.get('pass'))
            sym = '✓' if p == n else '~'
            print(f"  Locus Boot:    "
                  f"{p:2d}/{n}  {sym}")

        print("=" * 56)
        print()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    # ── CLI argument for engine path ──────────
    parser = argparse.ArgumentParser(
        description=(
            "Phonetic self-reference "
            "diagnostic v2"))
    parser.add_argument(
        '--engine-path',
        default=None,
        help=(
            "Directory containing "
            "voice_physics_v17.py "
            "(default: same dir as "
            "this script)"))
    args, _ = parser.parse_known_args()

    # ── Resolve and add engine path ───────────
    engine_path = _resolve_engine_path(
        explicit=args.engine_path)

    if engine_path is None:
        print()
        print("  ERROR: voice_physics_v17.py "
              "not found.")
        print()
        print("  Searched:")
        for c in [
            args.engine_path,
            os.environ.get('VOICE_ENGINE_PATH'),
            os.path.dirname(
                os.path.abspath(__file__)),
            os.path.abspath(os.getcwd()),
        ]:
            if c:
                print(f"    {c}")
        print()
        print("  Solutions:")
        print("  1. Run from the directory "
              "containing voice_physics_v17.py:")
        print("       cd /path/to/tonnetz")
        print("       python "
              "phonetic_self_reference.py")
        print()
        print("  2. Pass the path explicitly:")
        print("       python "
              "phonetic_self_reference.py "
              "--engine-path "
              "/path/to/tonnetz")
        print()
        print("  3. Set environment variable:")
        print("       export VOICE_ENGINE_PATH"
              "=/path/to/tonnetz")
        print("       python "
              "phonetic_self_reference.py")
        print()
        sys.exit(1)

    _add_engine_path(engine_path)
    print()
    print(f"  Engine path: {engine_path}")

    # ── Import engine ─────────────────────────
    try:
        from voice_physics_v17 import (
            synth_phrase,
            recalibrate_gains_v8,
            SR as ENGINE_SR,
            PITCH, DIL, ARC_NORMAL,
        )
    except ImportError as e:
        print(f"\n  Import failed: {e}")
        print(f"  Path added:    "
              f"{engine_path}")
        print(f"  Files present:")
        for f in sorted(
                os.listdir(engine_path)):
            if f.endswith('.py'):
                print(f"    {f}")
        print()
        sys.exit(1)

    recalibrate_gains_v8(sr=ENGINE_SR)
    os.makedirs("output_play",
                 exist_ok=True)

    def synth_fn(word, phones):
        return synth_phrase(
            [(word, phones)],
            punctuation='.',
            add_breath=False,
            add_ghost=False)

    psr     = PhoneticSelfRef(
        sr=ENGINE_SR)
    results = psr.run_all(
        synth_fn, verbose=True)
