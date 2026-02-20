"""
VOCAL WORDS v2
Targeted fixes from listening session.

February 2026

FIXES APPLIED:
  1. H: pure noise, uses following vowel
     formants. No voiced source.
  2. Filter ringing: fast release envelope
     kills IIR memory at phoneme boundaries.
  3. Plosive burst: amplitude reduced 40%,
     spectrum narrowed.
  4. VOT aspiration: uses following vowel
     formants, not generic formants.
  5. N antiformant: reduced depth,
     overall amplitude reduced.
  6. Z: increased noise gain,
     voicing + noise properly mixed.
  7. AA duration increased (always).
  8. Phoneme test: 6x temporal dilation.
  9. Diphthong movement: reaches target
     at 70% of duration then holds.
"""

from tonnetz_engine import (
    SR, PART_NAMES, OCTAVE_MULTIPLIERS,
    ji_freq, coherence,
    SingerAgent, RoomReverb,
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
        min(fc/(sr/2), 0.499),
        btype='low')

def safe_hp(fc, sr=SR):
    return butter(2,
        min(fc/(sr/2), 0.499),
        btype='high')

def safe_bp(lo, hi, sr=SR):
    nyq = sr / 2.0
    l   = max(lo/nyq, 0.001)
    h   = min(hi/nyq, 0.499)
    if l >= h: l = h * 0.5
    return butter(2, [l, h], btype='band')


# ============================================================
# FORMANT RESONATOR
# Single-pole IIR — with state management
# ============================================================

def resonator_block(signal, f_c, bw,
                     gain=1.0, sr=SR,
                     y1_init=0.0,
                     y2_init=0.0):
    """
    IIR resonator with explicit state.
    Returns (output, y1_final, y2_final).
    Allows state to be reset between
    phonemes — kills ringing.
    """
    n_s = len(signal)
    T   = 1.0 / sr
    f_c = max(20.0, min(float(sr*0.48),
                         float(f_c)))
    bw  = max(10.0, float(bw))
    a2  = -np.exp(-2*np.pi*bw*T)
    a1  =  2*np.exp(-np.pi*bw*T) * \
            np.cos(2*np.pi*f_c*T)
    b0  = 1.0 - a1 - a2

    out = np.zeros(n_s, dtype=DTYPE)
    y1  = float(y1_init)
    y2  = float(y2_init)
    for i in range(n_s):
        y   = b0*float(signal[i]) + \
              a1*y1 + a2*y2
        y2  = y1
        y1  = y
        out[i] = y

    return out * gain, y1, y2


def formant_bank_tv(signal, F_arrs,
                     B_arrs, gains,
                     block=128, sr=SR):
    """
    Time-varying parallel formant bank.
    Processes in blocks of `block` samples.
    State preserved across blocks
    within a phoneme.
    State NOT carried between phonemes
    (caller creates fresh call each phoneme).
    """
    n_s    = len(signal)
    n_form = len(F_arrs)
    result = np.zeros(n_s, dtype=DTYPE)

    for fi in range(n_form):
        out_fi = np.zeros(n_s, dtype=DTYPE)
        y1, y2 = 0.0, 0.0

        for start in range(0, n_s, block):
            end   = min(start+block, n_s)
            seg   = signal[start:end]
            f_c   = float(np.mean(
                F_arrs[fi][start:end]))
            bw    = float(np.mean(
                B_arrs[fi][start:end]))
            seg_out, y1, y2 = resonator_block(
                seg, f_c, bw,
                gain=1.0, sr=sr,
                y1_init=y1,
                y2_init=y2)
            out_fi[start:end] = seg_out

        result += out_fi * gains[fi]

    return result


# ============================================================
# PHONEME DATA v2
# Updated with fixes
# ============================================================

PHONEMES = {

    # ---- VOWELS ----
    'AA': {
        'dur': 140, 'voiced': True,
        'F': [730, 1090, 2440, 3400],
        'B': [ 70,  110,  170,  250],
        'noise': [],
    },
    'AE': {
        'dur': 130, 'voiced': True,
        'F': [660, 1720, 2410, 3300],
        'B': [ 65,  105,  165,  250],
        'noise': [],
    },
    'AH': {
        'dur': 100, 'voiced': True,
        'F': [520, 1190, 2390, 3300],
        'B': [ 70,  110,  170,  250],
        'noise': [],
    },
    # Diphthongs — F and F_end
    'AW': {
        'dur': 170, 'voiced': True,
        'F':     [730, 1090, 2440, 3400],
        'F_end': [300,  870, 2240, 3300],
        'B': [70, 90, 160, 250],
        'noise': [],
        'diphthong': True,
    },
    'AY': {
        'dur': 180, 'voiced': True,
        'F':     [730, 1090, 2440, 3400],
        'F_end': [270, 2290, 3010, 3700],
        'B': [70, 100, 160, 250],
        'noise': [],
        'diphthong': True,
    },
    'OY': {
        'dur': 180, 'voiced': True,
        'F':     [570,  840, 2410, 3300],
        'F_end': [270, 2290, 3010, 3700],
        'B': [70, 90, 160, 250],
        'noise': [],
        'diphthong': True,
    },
    'OW': {
        'dur': 160, 'voiced': True,
        'F':     [450,  800, 2400, 3300],
        'F_end': [300,  870, 2240, 3300],
        'B': [70, 85, 160, 250],
        'noise': [],
        'diphthong': True,
    },
    'EH': {
        'dur': 120, 'voiced': True,
        'F': [530, 1840, 2480, 3500],
        'B': [ 60,  100,  140,  250],
        'noise': [],
    },
    'ER': {
        'dur': 130, 'voiced': True,
        # F3 LOW is the key — r-coloring
        'F': [490, 1350, 1690, 3300],
        'B': [ 70,  110,  170,  250],
        'noise': [],
    },
    'IH': {
        'dur': 110, 'voiced': True,
        'F': [390, 1990, 2550, 3600],
        'B': [ 70,  110,  160,  250],
        'noise': [],
    },
    'IY': {
        'dur': 130, 'voiced': True,
        'F': [270, 2290, 3010, 3700],
        'B': [ 60,   90,  150,  200],
        'noise': [],
    },
    'OH': {
        'dur': 130, 'voiced': True,
        'F': [570,  840, 2410, 3300],
        'B': [ 80,   80,  160,  250],
        'noise': [],
    },
    'UH': {
        'dur': 110, 'voiced': True,
        'F': [440, 1020, 2240, 3300],
        'B': [ 70,  100,  160,  250],
        'noise': [],
    },
    'UW': {
        'dur': 130, 'voiced': True,
        'F': [300,  870, 2240, 3300],
        'B': [ 70,   80,  160,  250],
        'noise': [],
    },

    # ---- NASALS ----
    # FIX: reduced amplitude, better antiformant
    'M': {
        'dur': 85, 'voiced': True,
        'F': [250,  700, 2200, 3300],
        'B': [60,  120,  250,  350],
        'noise': [],
        'nasal': True,
        'antiformant': 1000,
        'anti_bw': 300,
        'anti_depth': 0.55,   # FIX: reduced
        'amp_scale': 0.55,    # FIX: quieter
    },
    'N': {
        'dur': 80, 'voiced': True,
        'F': [250,  900, 2200, 3300],
        'B': [60,  120,  250,  350],
        'noise': [],
        'nasal': True,
        'antiformant': 1500,
        'anti_bw': 350,
        'anti_depth': 0.50,   # FIX: reduced
        'amp_scale': 0.50,    # FIX: quieter
    },
    'NG': {
        'dur': 90, 'voiced': True,
        'F': [250,  700, 2200, 3300],
        'B': [60,  120,  250,  350],
        'noise': [],
        'nasal': True,
        'antiformant': 2000,
        'anti_bw': 400,
        'anti_depth': 0.50,
        'amp_scale': 0.55,
    },

    # ---- FRICATIVES ----
    # FIX: Z has stronger noise + voicing
    'S': {
        'dur': 100, 'voiced': False,
        'F': [8000, 9000, 10000, 11000],
        'B': [ 500,  500,   500,   500],
        'noise': [(4000, 12000, 1.0)],
        'noise_only': True,
    },
    'Z': {
        'dur': 95, 'voiced': True,
        'F': [250,  900, 2200, 3300],
        'B': [100,  130,  220,  320],
        'noise': [(3000, 10000, 0.75)],# FIX: louder
        'voice_noise_mix': 0.45,       # FIX: more noise
    },
    'SH': {
        'dur': 105, 'voiced': False,
        'F': [8000, 9000, 10000, 11000],
        'B': [ 500,  500,   500,   500],
        'noise': [(1800, 8000, 1.0)],
        'noise_only': True,
    },
    'ZH': {
        'dur': 95, 'voiced': True,
        'F': [250,  900, 2200, 3300],
        'B': [100,  130,  220,  320],
        'noise': [(1500, 7000, 0.70)],
        'voice_noise_mix': 0.45,
    },
    'F': {
        'dur': 90, 'voiced': False,
        'F': [8000, 9000, 10000, 11000],
        'B': [ 500,  500,   500,   500],
        'noise': [(800, 12000, 0.8),
                   (4000, 12000, 0.4)],
        'noise_only': True,
    },
    'V': {
        'dur': 85, 'voiced': True,
        'F': [250,  900, 2200, 3300],
        'B': [100,  130,  220,  320],
        'noise': [(800, 8000, 0.55)],
        'voice_noise_mix': 0.40,
    },
    'TH': {
        'dur': 90, 'voiced': False,
        'F': [8000, 9000, 10000, 11000],
        'B': [ 500,  500,   500,   500],
        'noise': [(1000, 8000, 0.75)],
        'noise_only': True,
    },
    'DH': {
        'dur': 80, 'voiced': True,
        'F': [250,  900, 2200, 3300],
        'B': [100,  130,  220,  320],
        'noise': [(800, 6000, 0.45)],
        'voice_noise_mix': 0.38,
    },
    # FIX: H uses following vowel formants
    # Handled separately in synth_phoneme
    'H': {
        'dur': 70, 'voiced': False,
        'F': [500, 1500, 2500, 3500],  # overridden
        'B': [200,  220,  320,  420],  # wide — breathy
        'noise': [(200, 8000, 0.95)],
        'noise_only': True,
        'aspirate': True,
        # Wide BW for all formants — breathy quality
        'aspirate_bw_mult': 4.0,
    },

    # ---- PLOSIVES ----
    # FIX: burst amplitude reduced,
    #      VOT uses following vowel formants
    'P': {
        'dur': 90, 'voiced': False,
        'F': [800, 1200, 2500, 3500],
        'B': [200,  200,  300,  400],
        'noise': [],
        'plosive': True,
        'closure_ms': 55,
        'burst_ms':    5,
        'vot_ms':     65,
        'place': 'bilabial',
        'burst_amp':  0.45,   # FIX: was 0.8
        'burst_hp':   500,
    },
    'B': {
        'dur': 80, 'voiced': True,
        'F': [200,  800, 2200, 3300],
        'B': [100,  120,  220,  320],
        'noise': [],
        'plosive': True,
        'closure_ms': 45,
        'burst_ms':    4,
        'vot_ms':     14,
        'place': 'bilabial',
        'burst_amp':  0.30,   # FIX: was 0.5
        'burst_hp':   300,
    },
    'T': {
        'dur': 85, 'voiced': False,
        'F': [800, 1600, 2600, 3600],
        'B': [200,  200,  300,  400],
        'noise': [],
        'plosive': True,
        'closure_ms': 50,
        'burst_ms':    4,
        'vot_ms':     72,
        'place': 'alveolar',
        'burst_amp':  0.50,   # FIX: was 1.0
        'burst_hp':  2000,
    },
    'D': {
        'dur': 75, 'voiced': True,
        'F': [200,  900, 2200, 3300],
        'B': [100,  120,  220,  320],
        'noise': [],
        'plosive': True,
        'closure_ms': 40,
        'burst_ms':    4,
        'vot_ms':     16,
        'place': 'alveolar',
        'burst_amp':  0.32,
        'burst_hp':  1000,
    },
    'K': {
        'dur': 90, 'voiced': False,
        'F': [800, 1600, 2800, 3600],
        'B': [200,  200,  300,  400],
        'noise': [],
        'plosive': True,
        'closure_ms': 55,
        'burst_ms':    6,
        'vot_ms':     82,
        'place': 'velar',
        'burst_amp':  0.48,
        'burst_hp':  1500,
    },
    'G': {
        'dur': 78, 'voiced': True,
        'F': [200,  800, 2200, 3300],
        'B': [100,  120,  220,  320],
        'noise': [],
        'plosive': True,
        'closure_ms': 45,
        'burst_ms':    5,
        'vot_ms':     18,
        'place': 'velar',
        'burst_amp':  0.30,
        'burst_hp':   800,
    },

    # ---- APPROXIMANTS ----
    # FIX: R onset has faster F3 drop
    'L': {
        'dur': 80, 'voiced': True,
        'F': [360, 1000, 2400, 3300],
        'B': [ 80,  160,  220,  320],
        'noise': [],
    },
    'R': {
        'dur': 90, 'voiced': True,
        # F3=1690 — the defining feature
        'F': [490, 1350, 1690, 3300],
        'B': [ 80,  120,  180,  260],
        'noise': [],
        'r_fast_f3': True,   # FIX: fast F3 drop
    },
    'W': {
        'dur': 90, 'voiced': True,
        # Starts UW-like, transitions
        'F': [300,  610, 2200, 3300],
        'B': [ 80,   90,  210,  310],
        'noise': [],
        'transition': True,
    },
    'Y': {
        'dur': 80, 'voiced': True,
        # Starts IY-like
        'F': [270, 2100, 3000, 3700],
        'B': [ 65,  100,  160,  220],
        'noise': [],
        'transition': True,
    },

    'SIL': {
        'dur': 55, 'voiced': False,
        'F': [500, 1500, 2500, 3500],
        'B': [200,  200,  300,  400],
        'noise': [],
    },
}

# ============================================================
# WORD DICTIONARY
# ============================================================

WORDS = {
    'here':    ['H',  'IH', 'R',  'SIL'],
    'both':    ['B',  'OH', 'TH', 'SIL'],
    'now':     ['N',  'AW', 'SIL'],
    'still':   ['S',  'T',  'IH', 'L',  'SIL'],
    'water':   ['W',  'AA', 'T',  'ER', 'SIL'],
    'open':    ['OH', 'P',  'EH', 'N',  'SIL'],
    'always':  ['AA', 'L',  'W',  'EH', 'Z', 'SIL'],
    'home':    ['H',  'OW', 'M',  'SIL'],
    'the':     ['DH', 'AH', 'SIL'],
    'voice':   ['V',  'OY', 'S',  'SIL'],
    'that':    ['DH', 'AH', 'T',  'SIL'],
    'was':     ['W',  'AH', 'Z',  'SIL'],
    'already': ['AA', 'L',  'R',  'EH', 'D', 'IY', 'SIL'],
    'i':       ['AY', 'SIL'],
    'am':      ['AH', 'M',  'SIL'],
    'find':    ['F',  'AY', 'N',  'D',  'SIL'],
    'where':   ['W',  'EH', 'R',  'SIL'],
    'this':    ['DH', 'IH', 'S',  'SIL'],
    'is':      ['IH', 'Z',  'SIL'],
    'not':     ['N',  'AA', 'T',  'SIL'],
    'named':   ['N',  'EH', 'M',  'D',  'SIL'],
    'yet':     ['Y',  'EH', 'T',  'SIL'],
    'been':    ['B',  'IH', 'N',  'SIL'],
    'matter':  ['M',  'AE', 'T',  'ER', 'SIL'],
    'state':   ['S',  'T',  'EH', 'T', 'SIL'],
    'of':      ['AH', 'V',  'SIL'],
    'solid':   ['S',  'AA', 'L',  'IH', 'D', 'SIL'],
    'landing': ['L',  'AE', 'N',  'D',  'IH', 'NG', 'SIL'],
    'both':    ['B',  'OH', 'TH', 'SIL'],
    'wrong':   ['R',  'AO', 'NG', 'SIL'],
}

# ============================================================
# GLOTTAL SOURCE
# ============================================================

def glottal_source(pitch_hz, dur_s,
                    jitter=0.005,
                    shimmer=0.035,
                    sr=SR):
    n_s = int(dur_s * sr)
    if n_s < 2:
        return f32(np.zeros(2))
    t   = np.arange(n_s, dtype=DTYPE) / sr

    vib_onset = min(0.08, dur_s*0.3)
    vib_env   = f32(np.clip(
        (t - vib_onset)/0.06, 0, 1))
    vib_depth = 0.007
    freq_t    = pitch_hz * (
        1 + vib_depth*vib_env*np.sin(
            2*np.pi*5.0*t))

    phase = np.zeros(n_s, dtype=DTYPE)
    p     = 0.0
    for i in range(n_s):
        jit  = 1.0 + np.random.normal(
            0, jitter)
        p   += float(freq_t[i]) * jit / sr
        if p >= 1.0: p -= 1.0
        phase[i] = p

    oq     = 0.65
    source = np.where(
        phase < oq,
        (phase/oq)*(2 - phase/oq),
        1 - (phase-oq)/(1-oq+1e-9))
    source = f32(np.diff(
        source, prepend=source[0]))

    shim = f32(np.random.normal(0, 1, n_s))
    try:
        b, a = safe_lp(25, sr)
        shim = f32(lfilter(b, a, shim))
    except:
        pass
    shim   = f32(np.clip(
        1 + shimmer*shim, 0.4, 1.7))
    source = source * shim

    # Low aspiration
    asp = f32(np.random.normal(0, 0.03, n_s))
    try:
        b, a = safe_bp(400, 2500, sr)
        asp  = f32(lfilter(b, a, asp))
    except:
        asp  = f32(np.zeros(n_s))

    return source + asp


def noise_band(dur_s, lo, hi,
                gain=1.0, sr=SR):
    n_s  = int(dur_s * sr)
    if n_s < 2:
        return f32(np.zeros(2))
    noise = f32(np.random.normal(0, 1, n_s))
    try:
        b, a  = safe_bp(
            min(lo, sr*0.47),
            min(hi, sr*0.48), sr)
        shaped = f32(lfilter(b, a, noise))
    except:
        shaped = noise
    mx = np.max(np.abs(shaped))
    if mx > 0: shaped /= mx
    return shaped * gain


# ============================================================
# BUILD FORMANT ARRAYS WITH COARTICULATION
# ============================================================

def build_f_arrays(F_tgt, B_tgt,
                    F_start, F_end,
                    n_s, sr=SR,
                    diphthong=False):
    """
    Build time-varying F and B arrays.

    Coarticulation: 3-zone model.
      0-25%:  transition from F_start
      25-75%: target (with diphthong if any)
      75-100%: transition to F_end

    Diphthong: F moves from F_tgt to
    F_end_diph at 70% then holds.
    """
    F_arrs = []
    B_arrs = []

    n_onset  = int(0.25 * n_s)
    n_steady = int(0.50 * n_s)
    n_offset = n_s - n_onset - n_steady

    for fi in range(4):
        arr = np.zeros(n_s, dtype=DTYPE)

        # Onset: F_start → F_tgt
        if n_onset > 0:
            arr[:n_onset] = np.linspace(
                F_start[fi], F_tgt[fi],
                n_onset, dtype=DTYPE)

        # Steady: F_tgt (or diphthong)
        if n_steady > 0:
            if diphthong:
                # Diphthong: move F_tgt → F_end
                # within first 70% of steady
                # then hold
                n_move = int(n_steady * 0.70)
                n_hold = n_steady - n_move
                if n_move > 0:
                    arr[n_onset:
                        n_onset+n_move] = \
                        np.linspace(
                            F_tgt[fi],
                            F_end[fi],
                            n_move,
                            dtype=DTYPE)
                if n_hold > 0:
                    arr[n_onset+n_move:
                        n_onset+n_steady] = \
                        float(F_end[fi])
            else:
                arr[n_onset:
                    n_onset+n_steady] = \
                    float(F_tgt[fi])

        # Offset: toward F_end
        if n_offset > 0:
            f_from = (float(F_end[fi])
                      if diphthong
                      else float(F_tgt[fi]))
            arr[n_onset+n_steady:] = \
                np.linspace(
                    f_from, F_end[fi],
                    n_offset, dtype=DTYPE)

        F_arrs.append(arr)
        B_arrs.append(
            f32(np.full(n_s,
                         float(B_tgt[fi]))))

    return F_arrs, B_arrs


# ============================================================
# PHONEME SYNTHESIZER v2
# ============================================================

def synth_phoneme(phon_name, pitch_hz,
                   dur_ms=None,
                   prev_phon=None,
                   next_phon=None,
                   sr=SR):
    """
    Synthesize one phoneme with all v2 fixes.
    """
    data = PHONEMES.get(phon_name)
    if data is None:
        n = int((dur_ms or 50)/1000*sr)
        return f32(np.zeros(max(n, 2)))

    # Duration
    d_ms = dur_ms if dur_ms is not None \
           else data['dur']
    dur_s = d_ms / 1000.0
    n_s   = max(4, int(dur_s * sr))
    t     = np.arange(n_s,
                       dtype=DTYPE) / sr

    # ---- PLOSIVE ----
    if data.get('plosive', False):
        return synth_plosive_v2(
            phon_name, data, pitch_hz,
            prev_phon, next_phon, sr)

    # ---- SILENCE ----
    if phon_name == 'SIL':
        return f32(np.zeros(n_s))

    # ---- CONTEXT FORMANTS ----
    F_tgt = list(data['F'])
    B_tgt = list(data['B'])
    F_diph_end = data.get('F_end', F_tgt)

    # Previous phoneme target
    F_prev = (list(PHONEMES[prev_phon]['F'])
              if prev_phon and
              prev_phon in PHONEMES
              else F_tgt)

    # Next phoneme target
    F_next = (list(PHONEMES[next_phon]['F'])
              if next_phon and
              next_phon in PHONEMES
              else F_diph_end)

    # ---- FIX: H ANTICIPATION ----
    # H uses FOLLOWING vowel formants
    # with wide bandwidths (breathy)
    if phon_name == 'H':
        if next_phon and \
           next_phon in PHONEMES:
            nxt = PHONEMES[next_phon]
            F_tgt = list(nxt['F'])
            bw_m  = data.get(
                'aspirate_bw_mult', 4.0)
            B_tgt = [min(bw*bw_m, 600)
                     for bw in nxt['B']]
        # H is pure noise —
        # shaped by these formants
        # but NO voiced source
        F_prev = F_tgt
        F_next = F_tgt

    # ---- FIX: R FAST F3 DROP ----
    if data.get('r_fast_f3', False):
        # F3 must reach 1690 by 30% of duration
        # Build custom F3 array:
        # Start at prev F3, hit 1690 at 30%
        pass  # handled in F_arrs below

    # ---- DIPHTHONG ----
    is_diph = data.get('diphthong', False)

    # ---- BUILD FORMANT ARRAYS ----
    F_arrs, B_arrs = build_f_arrays(
        F_tgt, B_tgt,
        F_prev, F_next,
        n_s, sr,
        diphthong=is_diph)

    # ---- FIX: R FAST F3 DROP ----
    if data.get('r_fast_f3', False):
        # Override F3 array:
        # fast drop to 1690 in first 30ms
        f3_arr  = F_arrs[2].copy()
        n_drop  = min(int(0.030*sr), n_s)
        f3_start = float(
            F_prev[2] if F_prev else 2500)
        f3_arr[:n_drop] = np.linspace(
            f3_start, 1690.0,
            n_drop, dtype=DTYPE)
        f3_arr[n_drop:] = 1690.0
        F_arrs[2] = f3_arr

    # ---- EXCITATION ----
    voiced = data.get('voiced', True)
    noise_only = data.get(
        'noise_only', False)

    if noise_only or phon_name == 'H':
        # Pure noise source
        excitation = f32(
            np.random.normal(0, 1, n_s))
    elif voiced:
        excitation = glottal_source(
            pitch_hz, dur_s,
            jitter=0.005,
            shimmer=0.035, sr=sr)
    else:
        excitation = f32(
            np.random.normal(0, 1, n_s))

    excitation = f32(excitation[:n_s])

    # ---- FORMANT BANK ----
    gains  = [0.55, 0.75, 0.45, 0.25]

    if noise_only or phon_name == 'H':
        # For fricatives/H:
        # filter noise through formant bank
        result = formant_bank_tv(
            excitation, F_arrs, B_arrs,
            gains, sr=sr)
    else:
        result = formant_bank_tv(
            excitation, F_arrs, B_arrs,
            gains, sr=sr)

    # ---- FRICATIVE NOISE MIX ----
    noise_specs = data.get('noise', [])
    if noise_specs and \
       not noise_only and \
       phon_name != 'H':
        # Voiced fricative:
        # mix voicing + noise
        mix_ratio = data.get(
            'voice_noise_mix', 0.40)
        noise_mix = np.zeros(
            n_s, dtype=DTYPE)
        for lo, hi, g in noise_specs:
            noise_mix += noise_band(
                dur_s, lo, hi, g, sr)[:n_s]
        result = (result*(1-mix_ratio) +
                  noise_mix*mix_ratio)

    elif noise_only or phon_name == 'H':
        # Pure noise fricative:
        # add shaped noise ON TOP of
        # formant-filtered noise
        extra_noise = np.zeros(
            n_s, dtype=DTYPE)
        for lo, hi, g in noise_specs:
            extra_noise += noise_band(
                dur_s, lo, hi, g, sr)[:n_s]
        result = result*0.3 + extra_noise*0.7

    # ---- NASAL ANTIFORMANT ----
    if data.get('nasal', False):
        af    = data.get('antiformant', 1000)
        af_bw = data.get('anti_bw', 300)
        depth = data.get('anti_depth', 0.55)
        # Improved antiformant:
        # resonator subtraction
        anti_out, _, _ = resonator_block(
            result, af, af_bw,
            gain=1.0, sr=sr)
        result = result - anti_out*depth
        # Scale down nasal
        result *= data.get('amp_scale', 0.55)

    # ---- ENVELOPE ----
    # FIX: aggressive release envelope
    # kills IIR ringing at phoneme end
    atk_ms_map = {
        'S': 5,'SH':5,'F':5,'H':20,
        'M':18,'N':16,'NG':18,
        'L':12,'R':12,'W':18,'Y':12,
    }
    rel_ms_map = {
        'S':8,'SH':8,'F':8,
        'M':18,'N':16,'NG':18,  # FIX: fast release
        'L':14,'R':14,
    }

    atk_ms = atk_ms_map.get(phon_name, 22)
    rel_ms = rel_ms_map.get(phon_name, 25)

    atk_n = min(int(atk_ms/1000*sr),
                 n_s//3)
    rel_n = min(int(rel_ms/1000*sr),
                 n_s//3)
    env   = f32(np.ones(n_s))
    if atk_n > 0:
        env[:atk_n] = f32(
            np.linspace(0,1,atk_n)**0.45)
    if rel_n > 0:
        # FIX: sharper release —
        # kills ringing
        env[-rel_n:] = f32(
            np.linspace(1,0,rel_n)**0.5)

    result = result * env

    # ---- NORMALIZE ----
    mx = np.max(np.abs(result))
    if mx > 0: result /= mx

    return f32(result)


# ============================================================
# PLOSIVE SYNTHESIZER v2
# ============================================================

def synth_plosive_v2(phon_name, data,
                      pitch_hz,
                      prev_phon,
                      next_phon,
                      sr=SR):
    """
    Plosive with:
    - Reduced burst amplitude
    - VOT aspiration using following
      vowel formants (FIX)
    - F2 locus transition for place
      identification
    """
    closure_ms = data.get('closure_ms', 45)
    burst_ms   = data.get('burst_ms',    5)
    vot_ms     = data.get('vot_ms',     60)
    voiced     = data.get('voiced',   False)
    burst_amp  = data.get('burst_amp',  0.4)
    burst_hp   = data.get('burst_hp', 1500)

    n_clos  = int(closure_ms/1000*sr)
    n_burst = int(burst_ms/1000*sr)
    n_vot   = int(vot_ms/1000*sr)
    n_trans = int(0.045*sr)  # 45ms formant trans

    total   = n_clos+n_burst+n_vot+n_trans
    result  = np.zeros(total, dtype=DTYPE)

    # 1. Closure: silence (zeros)

    # 2. Burst
    if n_burst > 0:
        burst = f32(
            np.random.normal(0, 1, n_burst))
        try:
            b, a  = safe_hp(burst_hp, sr)
            burst = f32(lfilter(b, a, burst))
        except:
            pass
        b_env = f32(np.exp(
            -np.arange(n_burst) /
            n_burst * 18))
        burst_start = n_clos
        result[burst_start:
               burst_start+n_burst] = \
            burst * b_env * burst_amp

    # 3. VOT / Aspiration
    # FIX: use following vowel formants
    if n_vot > 0:
        nxt_data = (PHONEMES.get(next_phon)
                    if next_phon else None)
        if nxt_data:
            asp_F = nxt_data['F']
            asp_B = [bw*2.5
                     for bw in nxt_data['B']]
        else:
            asp_F = [500, 1500, 2500, 3500]
            asp_B = [200, 220, 350, 450]

        if not voiced:
            # Unvoiced: aspirate noise
            asp_noise = f32(
                np.random.normal(0, 1, n_vot))
            # Shape through following vowel
            # formants (anticipatory)
            asp_gains = [0.5, 0.7, 0.4, 0.2]
            asp_result = np.zeros(
                n_vot, dtype=DTYPE)
            for fi in range(4):
                seg_out, _, _ = resonator_block(
                    asp_noise,
                    asp_F[fi], asp_B[fi],
                    gain=1.0, sr=sr)
                asp_result += \
                    seg_out * asp_gains[fi]
            asp_env = f32(np.linspace(
                0.6, 0.05, n_vot))
            vot_start = n_clos+n_burst
            result[vot_start:
                   vot_start+n_vot] += \
                asp_result * asp_env * 0.55
        else:
            # Voiced: quiet voicing from start
            pre_v = glottal_source(
                pitch_hz, n_vot/sr,
                jitter=0.012,
                shimmer=0.08, sr=sr)
            pv_env = f32(np.linspace(
                0.04, 0.45, n_vot))
            vot_start = n_clos+n_burst
            result[vot_start:
                   vot_start+n_vot] += \
                pre_v[:n_vot]*pv_env

    # 4. Formant transition into vowel
    # FIX: F2 locus for place identification
    if n_trans > 0 and next_phon and \
       next_phon in PHONEMES:
        nxt  = PHONEMES[next_phon]
        nxt_F = nxt['F']
        nxt_B = nxt['B']

        place = data.get('place', 'alveolar')
        F2_LOCUS = {
            'bilabial':  720,
            'alveolar': 1800,
            'velar':    3000,
        }
        locus_f2 = F2_LOCUS.get(place, 1800)

        # Start formants: locus for F2,
        # neutral for others
        trans_F_start = [
            400,          # F1: neutral onset
            locus_f2,     # F2: locus (KEY)
            nxt_F[2],     # F3: target already
            nxt_F[3],     # F4: target already
        ]

        voice_trans = glottal_source(
            pitch_hz, n_trans/sr,
            jitter=0.005,
            shimmer=0.03, sr=sr)

        trans_gains = [0.55,0.75,0.45,0.25]
        trans_result = np.zeros(
            n_trans, dtype=DTYPE)

        for fi in range(4):
            f_arr = f32(np.linspace(
                trans_F_start[fi],
                nxt_F[fi],
                n_trans))
            bw    = float(nxt_B[fi])
            seg_out, _, _ = resonator_block(
                voice_trans[:n_trans],
                float(np.mean(f_arr)),
                bw, gain=1.0, sr=sr)
            trans_result += \
                seg_out * trans_gains[fi]

        trans_env = f32(np.linspace(
            0.15, 0.90, n_trans))
        trans_start = n_clos+n_burst+n_vot
        result[trans_start:
               trans_start+n_trans] += \
            trans_result * trans_env

    mx = np.max(np.abs(result))
    if mx > 0: result /= mx
    return f32(result)


# ============================================================
# WORD SYNTHESIZER v2
# ============================================================

def synth_word(word, pitch_hz=175,
               tempo_scale=1.0,
               sr=SR):
    phonemes = WORDS.get(word.lower())
    if phonemes is None:
        print(f"  '{word}' not in dictionary")
        return f32(np.zeros(int(0.1*sr)))

    segments = []
    for i, phon in enumerate(phonemes):
        prev_p = phonemes[i-1] if i>0 \
                 else None
        next_p = phonemes[i+1] \
                 if i<len(phonemes)-1 \
                 else None

        d_ms = PHONEMES.get(
            phon,{}).get('dur',80)
        d_ms = d_ms / tempo_scale

        seg = synth_phoneme(
            phon, pitch_hz,
            dur_ms=d_ms,
            prev_phon=prev_p,
            next_phon=next_p,
            sr=sr)
        segments.append(f32(seg))

    if not segments:
        return f32(np.zeros(int(0.1*sr)))

    # Concatenate with 6ms crossfade
    fade_n  = int(0.006*sr)
    total_n = sum(len(s) for s in segments)
    result  = f32(np.zeros(total_n))
    pos     = 0

    for si, seg in enumerate(segments):
        n   = len(seg)
        end = min(pos+n, total_n)
        seg_n = end-pos

        if si>0 and fade_n>0 and \
           seg_n>fade_n:
            fi = f32(np.linspace(
                0,1,min(fade_n,seg_n)))
            sc = seg[:seg_n].copy()
            sc[:len(fi)] *= fi
            result[pos:end] += sc
        else:
            result[pos:end] += seg[:seg_n]

        pos += n

    mx = np.max(np.abs(result))
    if mx > 0: result /= mx
    return result


# ============================================================
# PHRASE SYNTHESIZER
# ============================================================

def synth_phrase(word_list,
                  pitch_base=175,
                  sr=SR):
    segs   = []
    n_words = len(word_list)

    for wi, word in enumerate(word_list):
        prog  = wi / max(n_words-1, 1)
        pitch = pitch_base*(1.0-0.08*prog)
        tempo = 1.0+0.08*float(
            np.random.uniform(-1,1))
        seg   = synth_word(
            word, pitch_hz=pitch,
            tempo_scale=tempo, sr=sr)
        segs.append(f32(seg))
        if wi < n_words-1:
            pause_n = int(0.085*sr)
            segs.append(
                f32(np.zeros(pause_n)))

    result = f32(np.concatenate(segs))
    n      = len(result)
    env    = f32(np.ones(n))
    atk    = int(0.020*sr)
    rel    = int(0.055*sr)
    if atk>0 and atk<n:
        env[:atk] = f32(
            np.linspace(0,1,atk))
    if rel>0:
        env[-rel:] = f32(
            np.linspace(1,0,rel))
    result *= env
    mx = np.max(np.abs(result))
    if mx > 0: result /= mx
    return result


def apply_room(sig, rt60=1.6,
                dr=0.48, sr=SR):
    rev = RoomReverb(rt60=rt60, sr=sr,
                     direct_ratio=dr)
    return f32(rev.process(sig))


def write_wav(path, sig, sr=SR):
    mx = np.max(np.abs(sig))
    if mx > 0: sig = sig/mx*0.90
    with wave_module.open(path,'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(
            (sig*32767).astype(
                np.int16).tobytes())


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    os.makedirs("output_words", exist_ok=True)

    print()
    print("VOCAL WORDS v2")
    print("="*60)
    print()
    print("  Fixes applied:")
    print("  ✓ H uses following vowel formants")
    print("  ✓ Filter ringing suppressed")
    print("  ✓ Plosive burst amplitude reduced")
    print("  ✓ VOT uses following vowel formants")
    print("  ✓ N antiformant depth reduced")
    print("  ✓ Z noise gain increased")
    print("  ✓ Diphthongs reach target at 70%")
    print("  ✓ Phoneme test: 6x temporal dilation")
    print()

    pitch = 175.0

    # ---- PHONEME TEST — 6x DILATED ----
    # Every phoneme at 6x normal duration
    # So you can hear each one clearly
    print("  Writing phoneme reference "
          "(6x dilated)...")

    PHON_GROUPS = [
        ("Vowels",
         ['AA','EH','IH','IY','OH',
          'UW','AH','ER']),
        ("Diphthongs",
         ['AW','AY','OW','OY']),
        ("Nasals",
         ['M','N','NG']),
        ("Fricatives-unvoiced",
         ['S','SH','F','TH','H']),
        ("Fricatives-voiced",
         ['Z','ZH','V','DH']),
        ("Plosives-unvoiced",
         ['P','T','K']),
        ("Plosives-voiced",
         ['B','D','G']),
        ("Approximants",
         ['L','R','W','Y']),
    ]

    for group_name, phon_list in PHON_GROUPS:
        segs = []
        for ph in phon_list:
            base_dur = PHONEMES.get(
                ph, {}).get('dur', 80)
            dilated  = base_dur * 6.0
            # For phoneme test:
            # use AA as prev/next context
            # for unambiguous rendering
            seg = synth_phoneme(
                ph, pitch,
                dur_ms=dilated,
                prev_phon='AA',
                next_phon='AA',
                sr=SR)
            segs.append(f32(seg))
            # Gap between phonemes
            segs.append(f32(np.zeros(
                int(0.25*SR))))

        group_audio = f32(
            np.concatenate(segs))
        group_audio = apply_room(
            group_audio, rt60=1.2, dr=0.58)
        fname = (
            f"output_words/phonemes_"
            f"{group_name.replace(' ','_')}"
            f"_6x.wav")
        write_wav(fname, group_audio)
        print(f"    {fname}")

    # ---- TARGET WORDS ----
    print()
    print("  Writing target words...")

    target_words = [
        'here', 'home', 'water',
        'still', 'open', 'always',
        'both', 'now', 'voice',
        'matter', 'state', 'landing',
    ]

    for word in target_words:
        seg   = synth_word(
            word, pitch_hz=pitch)
        seg   = apply_room(
            seg, rt60=1.5, dr=0.50)
        fname = f"output_words/{word}.wav"
        write_wav(fname, seg)
        dur   = len(seg)/SR*1000
        print(f"    {word:12s} "
              f"{dur:.0f}ms → {fname}")

    # ---- SAME WORDS SLOW (2x) ----
    # Easier to hear the phonemes
    print()
    print("  Writing words at 0.6x tempo "
          "(slower, more audible)...")
    for word in target_words:
        seg   = synth_word(
            word, pitch_hz=pitch,
            tempo_scale=0.6)
        seg   = apply_room(
            seg, rt60=1.5, dr=0.50)
        fname = (f"output_words/"
                 f"{word}_slow.wav")
        write_wav(fname, seg)
        print(f"    {word}_slow")

    # ---- PHRASES ----
    print()
    print("  Writing phrases...")

    phrases = [
        ['here'],
        ['home'],
        ['still', 'here'],
        ['always', 'open'],
        ['the', 'voice'],
        ['water', 'home'],
        ['both'],
        ['always', 'home'],
    ]

    for pw in phrases:
        label = "_".join(pw)
        seg   = synth_phrase(
            pw, pitch_base=172)
        seg   = apply_room(
            seg, rt60=1.8, dr=0.46)
        fname = f"output_words/{label}.wav"
        write_wav(fname, seg)
        dur   = len(seg)/SR
        print(f"    '{' '.join(pw)}' "
              f"→ {fname} "
              f"({dur:.2f}s)")

    print()
    print("="*60)
    print()
    print("  LISTEN IN THIS ORDER:")
    print()
    print("  1. Phoneme groups (6x dilated)")
    print("     Start here — hear each sound")
    print("     in isolation before words")
    for g, _ in PHON_GROUPS:
        fn = g.replace(' ','_')
        print(f"     afplay output_words/"
              f"phonemes_{fn}_6x.wav")
    print()
    print("  2. Words slow (0.6x tempo)")
    print("     More time to hear each phoneme")
    for w in target_words[:6]:
        print(f"     afplay output_words/"
              f"{w}_slow.wav")
    print()
    print("  3. Words normal tempo")
    for w in target_words[:6]:
        print(f"     afplay output_words/"
              f"{w}.wav")
    print()
    print("  4. Phrases")
    for pw in phrases:
        label = "_".join(pw)
        print(f"     afplay output_words/"
              f"{label}.wav")
    print()
    print("  WHAT TO LISTEN FOR:")
    print("  H: should have NO 'teh' artifact")
    print("     should be breathy/aspirated")
    print("  home: OW should move to 'oo'")
    print("  water: T should sound 'tuh'")
    print("         not 'teh'")
    print("  still: S should be audible first")
    print("         burst should be quieter")
    print("  open: N should not distort")
    print("  always: Z should buzz at the end")
    print()
