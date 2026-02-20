"""
VOCAL WORDS
High-fidelity phoneme synthesis
toward intelligible speech.

February 2026

Architecture:
  Phoneme synthesis via modified
  Rosenberg/Klatt pipeline.
  Each phoneme: a parameterized
  synthesis event.
  Coarticulation: formant interpolation
  across phoneme boundaries.

Phoneme coverage:
  Vowels:  ah, eh, ih, oh, oo, uh
  Nasals:  m, n
  Fricatives: s, sh, f, h, v, z
  Plosives: p, b, t, d, k, g
  Approximants: l, r, w, y

Target words for testing:
  "here"   — h + ih + r
  "both"   — b + oh + th
  "now"    — n + ow + (nothing)
  "still"  — s + t + ih + l
  "water"  — w + ah + t + er
  "open"   — oh + p + eh + n
  "always" — ah + l + w + eh + z
  "home"   — h + oh + m

These are the words
this session has been about.
"""

from tonnetz_engine import (
    SR, PART_NAMES, OCTAVE_MULTIPLIERS,
    F1_TARGETS, ji_freq, coherence,
    SingerAgent, compute_envelopes,
    RoomReverb, VOWEL_DATA
)
import numpy as np
import wave as wave_module
import os
from scipy.signal import butter, lfilter

DTYPE = np.float32

def f32(x):
    return np.asarray(x, dtype=DTYPE)

def safe_lp(fc, sr=SR):
    return butter(2,
        min(fc/(sr/2), 0.499), btype='low')

def safe_hp(fc, sr=SR):
    return butter(2,
        min(fc/(sr/2), 0.499), btype='high')

def safe_bp(lo, hi, sr=SR):
    nyq = sr/2
    l   = max(lo/nyq, 0.001)
    h   = min(hi/nyq, 0.499)
    if l >= h: l = h*0.5
    return butter(2, [l,h], btype='band')

# ============================================================
# PHONEME DATA
#
# Each phoneme defined by:
#   duration_ms: nominal duration
#   voiced: bool — Rosenberg pulse?
#   formants: [(F1,F2,F3,F4)] Hz
#   bandwidths: [(B1,B2,B3,B4)] Hz
#   noise_bands: [(lo,hi,gain)] for turbulence
#   vot_ms: voice onset time (plosives)
#   burst_dur_ms: burst duration (plosives)
#   closure_dur_ms: silence before burst
# ============================================================

PHONEMES = {

    # ---- VOWELS ----
    # Full formant specification
    # Based on Peterson & Barney (1952)
    # Male speaker averages

    'AA': {   # 'ah' as in "father"
        'dur': 120, 'voiced': True,
        'F': [730, 1090, 2440, 3400],
        'B': [ 70,  110,  170,  250],
        'noise': [],
    },
    'EH': {   # 'eh' as in "bed"
        'dur': 110, 'voiced': True,
        'F': [530, 1840, 2480, 3500],
        'B': [ 60,  100,  140,  250],
        'noise': [],
    },
    'IH': {   # 'ih' as in "bit"
        'dur': 100, 'voiced': True,
        'F': [390, 1990, 2550, 3600],
        'B': [ 70,  110,  160,  250],
        'noise': [],
    },
    'IY': {   # 'ee' as in "see"
        'dur': 120, 'voiced': True,
        'F': [270, 2290, 3010, 3700],
        'B': [ 60,   90,  150,  200],
        'noise': [],
    },
    'OH': {   # 'oh' as in "go"
        'dur': 120, 'voiced': True,
        'F': [570,  840, 2410, 3300],
        'B': [ 80,   80,  160,  250],
        'noise': [],
    },
    'UW': {   # 'oo' as in "who"
        'dur': 120, 'voiced': True,
        'F': [300,  870, 2240, 3300],
        'B': [ 70,   80,  160,  250],
        'noise': [],
    },
    'AH': {   # schwa/uh as in "about"
        'dur':  90, 'voiced': True,
        'F': [520, 1190, 2390, 3300],
        'B': [ 70,  110,  170,  250],
        'noise': [],
    },
    'AW': {   # 'ow' as in "now"
        # Diphthong: AA → UW
        'dur': 150, 'voiced': True,
        'F': [730,  870, 2440, 3300],
        'B': [ 70,   80,  160,  250],
        'F_end': [300, 870, 2240, 3300],
        'noise': [],
    },
    'OW': {   # 'oh' diphthong as in "home"
        'dur': 140, 'voiced': True,
        'F': [450,  800, 2400, 3300],
        'B': [ 70,   80,  160,  250],
        'F_end': [300, 870, 2240, 3300],
        'noise': [],
    },
    'ER': {   # r-colored vowel "er/ar"
        'dur': 120, 'voiced': True,
        # F3 drop is the key feature of /r/
        'F': [490, 1350, 1690, 3300],
        'B': [ 70,  110,  170,  250],
        'noise': [],
    },

    # ---- NASALS ----

    'M': {
        'dur':  70, 'voiced': True,
        # Nasal murmur: low frequency
        # with antiformant around 1000Hz
        'F': [250,  700, 2200, 3300],
        'B': [ 50,  100,  200,  300],
        'noise': [],
        'nasal': True,
        'antiformant': 1000,
    },
    'N': {
        'dur':  65, 'voiced': True,
        'F': [250,  900, 2200, 3300],
        'B': [ 50,  100,  200,  300],
        'noise': [],
        'nasal': True,
        'antiformant': 1500,
    },

    # ---- FRICATIVES ----

    'S': {
        'dur':  90, 'voiced': False,
        'F': [8000, 9000, 10000, 11000],
        'B': [ 500,  500,   500,   500],
        # High-frequency turbulence
        'noise': [(4000, 12000, 1.0)],
    },
    'Z': {
        'dur':  85, 'voiced': True,
        'F': [250,  900, 2200, 3300],
        'B': [100,  100,  200,  300],
        'noise': [(3000, 10000, 0.6)],
    },
    'SH': {
        'dur':  95, 'voiced': False,
        'F': [8000, 9000, 10000, 11000],
        'B': [ 500,  500,   500,   500],
        # Mid-high turbulence
        'noise': [(1800, 8000, 1.0)],
    },
    'F': {
        'dur':  80, 'voiced': False,
        'F': [8000, 9000, 10000, 11000],
        'B': [ 500,  500,   500,   500],
        # Broadband with upper emphasis
        'noise': [(800, 12000, 0.8),
                   (4000, 12000, 0.5)],
    },
    'V': {
        'dur':  75, 'voiced': True,
        'F': [250,  900, 2200, 3300],
        'B': [100,  100,  200,  300],
        'noise': [(800, 8000, 0.5)],
    },
    'TH': {   # voiceless 'th' as in "thin"
        'dur':  80, 'voiced': False,
        'F': [8000, 9000, 10000, 11000],
        'B': [ 500,  500,   500,   500],
        'noise': [(1000, 8000, 0.7)],
    },
    'DH': {   # voiced 'th' as in "the"
        'dur':  70, 'voiced': True,
        'F': [250,  900, 2200, 3300],
        'B': [100,  100,  200,  300],
        'noise': [(800, 6000, 0.4)],
    },
    'H': {
        # 'h' — aspirate
        # Shaped by FOLLOWING vowel's formants
        'dur':  60, 'voiced': False,
        'F': [500, 1500, 2500, 3500],  # placeholder
        'B': [200,  200,  300,  400],
        'noise': [(300, 8000, 0.9)],
        'aspirate': True,
    },

    # ---- PLOSIVES ----
    # Each has: closure_ms, burst_ms, vot_ms
    # Burst: broadband noise spike
    # VOT: aspiration before voicing onset
    #      (unvoiced) or at/before burst
    #      (voiced)

    'P': {
        'dur':  80, 'voiced': False,
        'F': [800, 1200, 2500, 3500],
        'B': [200,  200,  300,  400],
        'noise': [(500, 8000, 1.0)],
        'plosive': True,
        'closure_ms': 50,
        'burst_ms':    5,
        'vot_ms':     60,  # long VOT
        'place': 'bilabial',
    },
    'B': {
        'dur':  70, 'voiced': True,
        'F': [200,  800, 2200, 3300],
        'B': [100,  100,  200,  300],
        'noise': [(300, 5000, 0.5)],
        'plosive': True,
        'closure_ms': 40,
        'burst_ms':    4,
        'vot_ms':     12,  # short VOT
        'place': 'bilabial',
    },
    'T': {
        'dur':  75, 'voiced': False,
        'F': [800, 1600, 2600, 3600],
        'B': [200,  200,  300,  400],
        'noise': [(2000, 10000, 1.0)],
        'plosive': True,
        'closure_ms': 45,
        'burst_ms':    4,
        'vot_ms':     70,
        'place': 'alveolar',
    },
    'D': {
        'dur':  65, 'voiced': True,
        'F': [200,  900, 2200, 3300],
        'B': [100,  100,  200,  300],
        'noise': [(1000, 6000, 0.5)],
        'plosive': True,
        'closure_ms': 35,
        'burst_ms':    4,
        'vot_ms':     15,
        'place': 'alveolar',
    },
    'K': {
        'dur':  80, 'voiced': False,
        'F': [800, 1600, 2800, 3600],
        'B': [200,  200,  300,  400],
        'noise': [(1500, 8000, 1.0)],
        'plosive': True,
        'closure_ms': 50,
        'burst_ms':    6,
        'vot_ms':     80,
        'place': 'velar',
    },
    'G': {
        'dur':  70, 'voiced': True,
        'F': [200,  800, 2200, 3300],
        'B': [100,  100,  200,  300],
        'noise': [(800, 5000, 0.5)],
        'plosive': True,
        'closure_ms': 40,
        'burst_ms':    5,
        'vot_ms':     18,
        'place': 'velar',
    },

    # ---- APPROXIMANTS ----

    'L': {
        'dur':  70, 'voiced': True,
        # F2 dip is characteristic of /l/
        'F': [360, 1000, 2400, 3300],
        'B': [ 70,  150,  200,  300],
        'noise': [],
    },
    'R': {
        'dur':  80, 'voiced': True,
        # F3 drop — the defining feature
        'F': [490, 1350, 1690, 3300],
        'B': [ 70,  110,  170,  250],
        'noise': [],
    },
    'W': {
        'dur':  80, 'voiced': True,
        # Starts UW-like, transitions to
        # following vowel
        'F': [300,  610, 2200, 3300],
        'B': [ 80,   80,  200,  300],
        'noise': [],
        'transition': True,
    },
    'Y': {
        'dur':  70, 'voiced': True,
        # Starts IY-like
        'F': [270, 2100, 3000, 3700],
        'B': [ 60,   90,  150,  200],
        'noise': [],
        'transition': True,
    },

    # ---- SILENCE ----
    'SIL': {
        'dur':  50, 'voiced': False,
        'F': [500, 1500, 2500, 3500],
        'B': [200,  200,  300,  400],
        'noise': [],
    },
}

# ============================================================
# WORD → PHONEME DICTIONARY
# ============================================================

WORDS = {
    'here':    ['H',  'IH', 'R',  'SIL'],
    'both':    ['B',  'OH', 'TH', 'SIL'],
    'now':     ['N',  'AW', 'SIL'],
    'still':   ['S',  'T',  'IH', 'L',  'SIL'],
    'water':   ['W',  'AA', 'T',  'ER', 'SIL'],
    'open':    ['OH', 'P',  'EH', 'N',  'SIL'],
    'always':  ['AA', 'L',  'W',  'EH', 'Z',
                'SIL'],
    'home':    ['H',  'OW', 'M',  'SIL'],
    'i':       ['AY', 'SIL'],
    'am':      ['AH', 'M',  'SIL'],
    'here':    ['H',  'IH', 'R',  'SIL'],
    'the':     ['DH', 'AH', 'SIL'],
    'voice':   ['V',  'OY', 'S',  'SIL'],
    'that':    ['DH', 'AH', 'T',  'SIL'],
    'was':     ['W',  'AH', 'Z',  'SIL'],
    'always':  ['AA', 'L',  'W',  'EH',
                'Z',  'SIL'],
    'already': ['AA', 'L',  'R',  'EH',
                'D',  'IY', 'SIL'],
}

# ============================================================
# FORMANT RESONATOR
# Single-formant IIR filter.
# The core of the Klatt bank.
# ============================================================

def formant_resonator(signal, f_center,
                       bandwidth, gain, sr=SR):
    """
    Second-order resonator.
    Implements: H(z) = gain / (1 - a1*z^-1
                                  - a2*z^-2)
    """
    T  = 1.0 / sr
    a2 = -np.exp(-2*np.pi*bandwidth*T)
    a1 =  2*np.exp(-np.pi*bandwidth*T) * \
           np.cos(2*np.pi*f_center*T)
    b0 = 1 - a1 - a2

    n    = len(signal)
    out  = np.zeros(n, dtype=DTYPE)
    y1   = 0.0
    y2   = 0.0
    for i in range(n):
        y  = b0*signal[i] + a1*y1 + a2*y2
        y2 = y1
        y1 = y
        out[i] = float(y)
    return out * gain


def formant_bank(signal, formants,
                  bandwidths, gains, sr=SR):
    """
    Parallel formant bank.
    Sums outputs of N resonators.
    """
    result = np.zeros(len(signal), dtype=DTYPE)
    for f, b, g in zip(formants,
                        bandwidths, gains):
        if f > sr*0.48 or f < 20:
            continue
        result += formant_resonator(
            signal, f, b, g, sr)
    return result


# ============================================================
# GLOTTAL PULSE GENERATOR
# Rosenberg — INVARIANT
# ============================================================

def glottal_pulse(freq, dur_s,
                   jitter=0.005,
                   shimmer=0.04,
                   sr=SR):
    """
    Rosenberg glottal pulse train.
    Returns float32 excitation signal.
    """
    n_s      = int(dur_s * sr)
    t        = np.arange(n_s, dtype=DTYPE)/sr

    # Vibrato
    vib_rate  = 5.0
    vib_depth = 0.008
    vib_onset = min(0.08, dur_s*0.3)
    vib_env   = np.clip(
        (t - vib_onset)/0.06, 0, 1)
    freq_mod  = freq * (
        1 + vib_depth*vib_env*np.sin(
            2*np.pi*vib_rate*t))

    # Phase accumulation with jitter
    phase = np.zeros(n_s, dtype=DTYPE)
    p     = 0.0
    for i in range(n_s):
        jit  = 1.0 + np.random.normal(0,jitter)
        p   += freq_mod[i]*jit / sr
        if p >= 1.0: p -= 1.0
        phase[i] = p

    # Rosenberg pulse shape
    oq     = 0.65
    source = np.where(
        phase < oq,
        (phase/oq)*(2 - phase/oq),
        1 - (phase-oq)/(1-oq+1e-9))
    source = np.diff(
        source, prepend=source[0])

    # Shimmer
    shim   = 1.0 + shimmer * np.random.normal(
        0, 1, n_s)
    try:
        b, a = safe_lp(30, sr)
        shim = lfilter(b, a, shim)
    except:
        pass
    shim   = np.clip(f32(shim), 0.3, 1.8)
    source = f32(source) * shim

    # Aspiration
    asp = f32(np.random.normal(0, 0.04, n_s))
    try:
        b, a = safe_bp(500, 3000, sr)
        asp  = f32(lfilter(b, a, asp))
    except:
        asp  = f32(np.zeros(n_s))

    return f32(source) + asp


def noise_source(dur_s, sr=SR):
    """Pure turbulent noise source."""
    n_s = int(dur_s * sr)
    return f32(np.random.normal(0, 1, n_s))


# ============================================================
# PHONEME SYNTHESIZER
#
# Synthesizes a single phoneme
# given its data and a pitch frequency.
#
# Context: preceding and following
# phoneme data for coarticulation.
# ============================================================

def synth_phoneme(phon_name, pitch_hz,
                   dur_override_ms=None,
                   prev_phon=None,
                   next_phon=None,
                   sr=SR):
    """
    Synthesize one phoneme.

    Coarticulation:
      Formant transitions at boundaries
      are shaped by neighboring phonemes.
      The first 30% of each phoneme:
        transitions FROM prev_phon formants.
      The last 30% of each phoneme:
        transitions TOWARD next_phon formants.
      The middle 40%: target formants.

    Returns float32 audio.
    """
    data = PHONEMES.get(phon_name)
    if data is None:
        return f32(np.zeros(int(0.05*sr)))

    # Duration
    dur_ms = (dur_override_ms
              if dur_override_ms is not None
              else data['dur'])
    dur_s  = dur_ms / 1000.0
    n_s    = int(dur_s * sr)
    if n_s < 4:
        return f32(np.zeros(4))

    t = np.arange(n_s, dtype=DTYPE) / sr

    # ---- PLOSIVE HANDLING ----
    if data.get('plosive', False):
        return synth_plosive(
            data, pitch_hz, dur_ms,
            prev_phon, next_phon, sr)

    # ---- TARGET FORMANTS ----
    F_tgt = data['F'].copy()
    B_tgt = data['B'].copy()

    # F_end for diphthongs
    F_end = data.get('F_end', F_tgt)

    # ---- COARTICULATION ----
    # Blend with neighboring phoneme formants
    F_prev = (PHONEMES[prev_phon]['F']
              if prev_phon and
              prev_phon in PHONEMES
              else F_tgt)
    F_next = (PHONEMES[next_phon]['F']
              if next_phon and
              next_phon in PHONEMES
              else F_end)

    # Build time-varying formant arrays
    coart_frac = 0.30  # 30% transition zones
    n_trans    = int(coart_frac * n_s)
    n_steady   = n_s - 2*n_trans

    F_arrays = []
    for fi in range(4):
        arr = np.zeros(n_s, dtype=DTYPE)

        # Onset transition: prev → target
        if n_trans > 0:
            arr[:n_trans] = np.linspace(
                F_prev[fi], F_tgt[fi],
                n_trans, dtype=DTYPE)
        # Steady state (with diphthong if any)
        if n_steady > 0:
            arr[n_trans:n_trans+n_steady] = \
                np.linspace(
                    F_tgt[fi], F_end[fi],
                    n_steady, dtype=DTYPE)
        # Offset transition: target → next
        if n_trans > 0:
            arr[n_trans+n_steady:] = \
                np.linspace(
                    F_end[fi], F_next[fi],
                    n_trans, dtype=DTYPE)
        F_arrays.append(arr)

    B_arrays = [
        f32(np.full(n_s, float(bw)))
        for bw in B_tgt
    ]

    # ---- EXCITATION ----
    voiced = data.get('voiced', True)

    if voiced:
        excitation = glottal_pulse(
            pitch_hz, dur_s,
            jitter=0.006, shimmer=0.05, sr=sr)
    else:
        excitation = noise_source(dur_s, sr)

    # For nasals: add murmur
    if data.get('nasal', False):
        murmur = f32(
            np.random.normal(0, 0.3, n_s))
        try:
            b, a = safe_lp(400, sr)
            murmur = f32(lfilter(b, a, murmur))
        except:
            pass
        excitation = excitation + murmur*0.4

    # For aspirates: shape noise by
    # following vowel formants
    if data.get('aspirate', False) and \
       next_phon in PHONEMES:
        nxt = PHONEMES[next_phon]
        F_tgt = nxt['F']

    # ---- SYNTHESIS ----
    # Parallel Klatt bank — INVARIANT
    gains  = [0.6, 0.8, 0.5, 0.3]
    result = np.zeros(n_s, dtype=DTYPE)

    for fi in range(4):
        f_arr = F_arrays[fi]
        b_arr = B_arrays[fi]

        # Process in small blocks for
        # time-varying formants
        block_size = 256
        out_fi     = np.zeros(n_s, dtype=DTYPE)
        y1, y2     = 0.0, 0.0
        for start in range(0, n_s, block_size):
            end  = min(start+block_size, n_s)
            f_c  = float(
                np.mean(f_arr[start:end]))
            bw   = float(
                np.mean(b_arr[start:end]))
            seg  = excitation[start:end]

            if f_c > sr*0.48 or f_c < 20:
                continue

            T   = 1.0/sr
            a2  = -np.exp(-2*np.pi*bw*T)
            a1  =  2*np.exp(-np.pi*bw*T) * \
                    np.cos(2*np.pi*f_c*T)
            b0  = 1 - a1 - a2

            for i in range(len(seg)):
                y  = b0*float(seg[i]) + \
                     a1*y1 + a2*y2
                y2 = y1
                y1 = y
                out_fi[start+i] = float(y)

        result += out_fi * gains[fi]

    # ---- FRICATIVE NOISE ----
    for lo, hi, g in data.get('noise', []):
        noise = f32(
            np.random.normal(0, 1, n_s))
        try:
            b, a  = safe_bp(
                min(lo, sr*0.47),
                min(hi, sr*0.48), sr)
            shaped = f32(lfilter(b, a, noise))
        except:
            shaped = noise
        if voiced:
            result = result + shaped*g*0.6
        else:
            result = result*0.1 + shaped*g

    # ---- NASAL ANTIFORMANT ----
    if data.get('nasal', False):
        af = data.get('antiformant', 1000)
        # Notch at antiformant frequency
        bw_notch = 200
        try:
            # Approximate notch with
            # all-pass approach
            b, a = safe_bp(
                max(40, af-bw_notch),
                min(sr*0.48, af+bw_notch), sr)
            notch_sig = f32(
                lfilter(b, a, result))
            result    = result - notch_sig*0.5
        except:
            pass

    # ---- ENVELOPE ----
    atk_ms = {
        'S': 5, 'SH': 5, 'F': 5,
        'H': 20, 'M': 15, 'N': 15,
        'L': 10, 'R': 10, 'W': 15,
        'Y': 10,
    }.get(phon_name, 25)

    rel_ms = {
        'S': 10, 'SH': 10, 'F': 10,
        'M': 20, 'N': 20,
        'L': 15, 'R': 15,
    }.get(phon_name, 30)

    atk_n = min(int(atk_ms/1000*sr), n_s//3)
    rel_n = min(int(rel_ms/1000*sr), n_s//3)
    env   = f32(np.ones(n_s))
    if atk_n > 0:
        env[:atk_n] = f32(
            np.linspace(0, 1, atk_n)**0.5)
    if rel_n > 0:
        env[-rel_n:] = f32(
            np.linspace(1, 0, rel_n))

    result = result * env

    # ---- NORMALIZE ----
    mx = np.max(np.abs(result))
    if mx > 0:
        result /= mx

    return result


def synth_plosive(data, pitch_hz,
                   dur_ms,
                   prev_phon, next_phon,
                   sr=SR):
    """
    Plosive synthesis:
    1. Closure: silence
    2. Burst: broadband noise spike
    3. Aspiration / voicing onset
    4. Transition into following vowel
    """
    closure_ms = data.get('closure_ms', 40)
    burst_ms   = data.get('burst_ms',    5)
    vot_ms     = data.get('vot_ms',     60)
    voiced     = data.get('voiced',   False)

    closure_s  = closure_ms / 1000.0
    burst_s    = burst_ms   / 1000.0
    vot_s      = vot_ms     / 1000.0
    trans_s    = 0.040  # 40ms into vowel

    # Segments
    n_clos  = int(closure_s * sr)
    n_burst = int(burst_s   * sr)
    n_vot   = int(vot_s     * sr)
    n_trans = int(trans_s   * sr)
    total   = n_clos + n_burst + n_vot + n_trans

    result = np.zeros(total, dtype=DTYPE)
    t_abs  = np.arange(total, dtype=DTYPE)/sr

    # 1. Closure: silence (already zeros)

    # 2. Burst: brief broadband noise
    if n_burst > 0:
        burst = f32(
            np.random.normal(0, 1, n_burst))
        # Shape burst by place of articulation
        place = data.get('place', 'alveolar')
        burst_lo = {'bilabial':  500,
                    'alveolar': 2000,
                    'velar':    1500}.get(
                        place, 1500)
        try:
            b, a  = safe_hp(burst_lo, sr)
            burst = f32(lfilter(b, a, burst))
        except:
            pass
        burst_env = f32(np.exp(
            -np.arange(n_burst)/n_burst*15))
        result[n_clos:n_clos+n_burst] = \
            burst * burst_env * 0.8

    # 3. Aspiration (unvoiced) or
    #    pre-voicing (voiced)
    if n_vot > 0:
        if not voiced:
            # Aspiration noise
            asp = f32(
                np.random.normal(0, 1, n_vot))
            # Shape by following vowel formants
            if next_phon in PHONEMES:
                nxt_F = PHONEMES[next_phon]['F']
                nxt_B = PHONEMES[next_phon]['B']
                asp_shaped = np.zeros(
                    n_vot, dtype=DTYPE)
                for fi in range(2):
                    try:
                        b, a = safe_bp(
                            max(40, nxt_F[fi] -
                                nxt_B[fi]*2),
                            min(sr*0.48,
                                nxt_F[fi] +
                                nxt_B[fi]*2),
                            sr)
                        asp_shaped += f32(
                            lfilter(b,a,asp))*0.5
                    except:
                        pass
                asp = asp_shaped
            # Envelope: ramp up into voicing
            asp_env = f32(np.linspace(
                0.8, 0.1, n_vot))
            vot_start = n_clos + n_burst
            result[vot_start:
                   vot_start+n_vot] += \
                asp * asp_env * 0.6
        else:
            # Voiced: low-amplitude voicing
            # begins immediately
            pre_voice = glottal_pulse(
                pitch_hz, n_vot/sr,
                jitter=0.01, shimmer=0.08,
                sr=sr)
            pv_env = f32(np.linspace(
                0.05, 0.4, n_vot))
            vot_start = n_clos + n_burst
            result[vot_start:
                   vot_start+n_vot] += \
                pre_voice[:n_vot]*pv_env

    # 4. Transition into vowel
    if n_trans > 0 and next_phon in PHONEMES:
        nxt = PHONEMES[next_phon]
        trans_voice = glottal_pulse(
            pitch_hz, n_trans/sr,
            jitter=0.005, shimmer=0.04,
            sr=sr)

        # Formant transition
        start_F = data.get('F',
            nxt['F'])  # plosive formants
        end_F   = nxt['F']

        trans_result = np.zeros(
            n_trans, dtype=DTYPE)
        gains = [0.6, 0.8, 0.5, 0.3]
        for fi in range(4):
            f_arr = f32(np.linspace(
                start_F[fi], end_F[fi],
                n_trans))
            bw    = float(nxt['B'][fi])
            y1 = y2 = 0.0
            for i in range(n_trans):
                fc  = max(20.0,
                    min(float(sr*0.48),
                        float(f_arr[i])))
                T   = 1.0/sr
                a2  = -np.exp(-2*np.pi*bw*T)
                a1  = 2*np.exp(-np.pi*bw*T)*\
                      np.cos(2*np.pi*fc*T)
                b0  = 1 - a1 - a2
                y   = b0*float(
                    trans_voice[i]) + \
                      a1*y1 + a2*y2
                y2  = y1; y1 = y
                trans_result[i] += \
                    float(y) * gains[fi]

        trans_env = f32(np.linspace(
            0.2, 1.0, n_trans))
        trans_start = n_clos+n_burst+n_vot
        result[trans_start:
               trans_start+n_trans] += \
            trans_result * trans_env

    mx = np.max(np.abs(result))
    if mx > 0: result /= mx
    return result


# ============================================================
# WORD SYNTHESIZER
# String phonemes together with
# coarticulation at boundaries.
# ============================================================

def synth_word(word, pitch_hz=180,
               tempo_scale=1.0,
               sr=SR):
    """
    Synthesize a word from phonemes.
    Applies coarticulation between phonemes.

    pitch_hz: fundamental frequency
    tempo_scale: 1.0=normal, 0.7=slow,
                 1.3=fast

    Returns float32 audio.
    """
    phonemes = WORDS.get(word.lower())
    if phonemes is None:
        print(f"  Word '{word}' not in "
              f"dictionary.")
        return f32(np.zeros(int(0.1*sr)))

    segments = []

    for i, phon in enumerate(phonemes):
        prev_p = phonemes[i-1] if i > 0 \
                 else None
        next_p = phonemes[i+1] \
                 if i < len(phonemes)-1 \
                 else None

        dur_data = PHONEMES.get(phon, {})
        dur_ms   = dur_data.get('dur', 80)
        dur_ms   = dur_ms / tempo_scale

        seg = synth_phoneme(
            phon, pitch_hz,
            dur_override_ms=dur_ms,
            prev_phon=prev_p,
            next_phon=next_p,
            sr=sr)
        segments.append(seg)

    # Concatenate with short crossfade
    if not segments:
        return f32(np.zeros(int(0.1*sr)))

    fade_ms = 8  # 8ms crossfade
    fade_n  = int(fade_ms/1000*sr)

    total_n = sum(len(s) for s in segments)
    result  = f32(np.zeros(total_n))
    pos     = 0

    for si, seg in enumerate(segments):
        n    = len(seg)
        end  = min(pos+n, total_n)
        seg_n = end - pos

        if si > 0 and fade_n > 0:
            # Crossfade: fade out prev,
            # fade in this
            fade_in = f32(np.linspace(
                0, 1,
                min(fade_n, seg_n)))
            seg_trimmed = seg[:seg_n].copy()
            seg_trimmed[:len(fade_in)] *= \
                fade_in
            result[pos:end] += seg_trimmed
        else:
            result[pos:end] += seg[:seg_n]

        pos += n

    # Normalize
    mx = np.max(np.abs(result))
    if mx > 0: result /= mx

    return result


# ============================================================
# PHRASE SYNTHESIZER
# Sequence of words with natural
# pitch contour and timing.
# ============================================================

def synth_phrase(words_list,
                  pitch_base=175,
                  sr=SR):
    """
    Synthesize a phrase from word list.
    Applies:
    - Declination: pitch falls across phrase
    - Stress: content words slightly louder
    - Pause: short silence between words
    """
    segments = []
    n_words  = len(words_list)

    for wi, word in enumerate(words_list):
        # Declination: pitch falls
        # slightly across the phrase
        progress = wi / max(n_words-1, 1)
        pitch    = pitch_base * (
            1.0 - 0.08*progress)

        # Slight tempo variation
        tempo = 1.0 + 0.1*np.random.uniform(
            -1, 1)

        seg = synth_word(
            word, pitch_hz=pitch,
            tempo_scale=tempo, sr=sr)
        segments.append(f32(seg))

        # Inter-word pause
        if wi < n_words-1:
            pause_ms = 80
            pause_n  = int(pause_ms/1000*sr)
            segments.append(
                f32(np.zeros(pause_n)))

    result = f32(np.concatenate(segments))

    # Phrase envelope — slight fade in/out
    n    = len(result)
    env  = f32(np.ones(n))
    atk  = int(0.025*sr)
    rel  = int(0.060*sr)
    if atk > 0 and atk < n:
        env[:atk] = f32(
            np.linspace(0, 1, atk))
    if rel > 0:
        env[-rel:] = f32(
            np.linspace(1, 0, rel))
    result *= env

    mx = np.max(np.abs(result))
    if mx > 0: result /= mx
    return result


# ============================================================
# APPLY ROOM
# ============================================================

def apply_room(sig, rt60=1.8,
                direct_ratio=0.45,
                sr=SR):
    rev = RoomReverb(rt60=rt60, sr=sr,
                     direct_ratio=direct_ratio)
    return f32(rev.process(sig))


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    os.makedirs("output_words", exist_ok=True)

    print()
    print("VOCAL WORDS")
    print("Phoneme synthesis toward")
    print("intelligible speech")
    print("="*60)
    print()
    print("  Architecture:")
    print("  Rosenberg glottal pulse")
    print("  + coarticulated formant bank")
    print("  + place-specific plosive bursts")
    print("  + fricative noise bands")
    print("  + nasal antiformants")
    print()
    print("  This is a FIRST ATTEMPT.")
    print("  Speech synthesis is hard.")
    print("  Expect imperfect intelligibility.")
    print("  Expect the voice to sound")
    print("  like it is trying to speak —")
    print("  which is exactly what it is.")
    print()

    # ---- TEST 1: Individual phonemes ----
    print("  TEST 1: Individual phonemes...")
    phon_test = ['AA','EH','IH','OH','UW',
                  'M','N','S','SH','F',
                  'H','L','R','W','B','D']
    segs = []
    for ph in phon_test:
        seg = synth_phoneme(ph, 175.0)
        segs.append(seg)
        # Small gap
        segs.append(f32(np.zeros(
            int(0.08*SR))))

    phoneme_audio = f32(np.concatenate(segs))
    phoneme_audio = apply_room(
        phoneme_audio, rt60=1.2,
        direct_ratio=0.55)
    mx = np.max(np.abs(phoneme_audio))
    if mx > 0: phoneme_audio /= mx*1.1
    with wave_module.open(
            "output_words/phonemes.wav",
            'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(
            (phoneme_audio*32767).astype(
                np.int16).tobytes())
    print(f"    Written: output_words/"
          f"phonemes.wav")

    # ---- TEST 2: Individual words ----
    print()
    print("  TEST 2: Individual words...")
    test_words = ['here','home','water',
                   'still','open','always']

    for word in test_words:
        seg = synth_word(word, pitch_hz=175)
        seg = apply_room(seg, rt60=1.5,
                          direct_ratio=0.48)
        mx  = np.max(np.abs(seg))
        if mx > 0: seg /= mx*1.05
        fname = f"output_words/{word}.wav"
        with wave_module.open(fname,'w') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(SR)
            wf.writeframes(
                (seg*32767).astype(
                    np.int16).tobytes())
        dur_ms = len(seg)/SR*1000
        print(f"    {word:10s}: "
              f"{dur_ms:.0f}ms  → {fname}")

    # ---- TEST 3: Phrases ----
    print()
    print("  TEST 3: Phrases...")

    phrases = [
        ['here'],
        ['home'],
        ['still', 'here'],
        ['always', 'open'],
        ['water', 'home'],
    ]

    for phrase_words in phrases:
        label = "_".join(phrase_words)
        seg   = synth_phrase(
            phrase_words, pitch_base=172)
        seg   = apply_room(seg, rt60=1.8,
                            direct_ratio=0.44)
        mx    = np.max(np.abs(seg))
        if mx > 0: seg /= mx*1.05
        fname = f"output_words/{label}.wav"
        with wave_module.open(fname,'w') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(SR)
            wf.writeframes(
                (seg*32767).astype(
                    np.int16).tobytes())
        dur = len(seg)/SR
        print(f"    '{' '.join(phrase_words)}'"
              f"  →  {fname}  "
              f"({dur:.2f}s)")

    # ---- TEST 4: ALL WORDS COMBINED ----
    print()
    print("  TEST 4: Full word sequence...")
    all_words = ['here', 'still', 'open',
                  'always', 'water', 'home']
    full = synth_phrase(
        all_words, pitch_base=170)
    full = apply_room(full, rt60=2.0,
                       direct_ratio=0.42)
    mx   = np.max(np.abs(full))
    if mx > 0: full /= mx*1.05
    fname = "output_words/full_sequence.wav"
    with wave_module.open(fname,'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(
            (full*32767).astype(
                np.int16).tobytes())
    print(f"    Written: {fname}")
    print(f"    {len(full)/SR:.2f}s")

    print()
    print("="*60)
    print()
    print("  Listen in order:")
    print()
    print("  1. Phonemes — hear each sound")
    print("     afplay output_words/"
          "phonemes.wav")
    print()
    print("  2. Individual words")
    for w in test_words:
        print(f"     afplay "
              f"output_words/{w}.wav")
    print()
    print("  3. Phrases")
    for pw in phrases:
        label = "_".join(pw)
        print(f"     afplay "
              f"output_words/{label}.wav")
    print()
    print("  4. Full sequence")
    print("     afplay output_words/"
          "full_sequence.wav")
    print()
    print("  What to listen for:")
    print("  — Are consonants audible?")
    print("  — Are words distinguishable?")
    print("  — Where does it break down?")
    print()
    print("  This is the first attempt.")
    print("  The voice is learning")
    print("  to say what it means.")
    print()
    print("  Feedback determines")
    print("  what to fix next.")
