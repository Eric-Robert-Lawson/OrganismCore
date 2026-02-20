"""
VOCAL WORDS v4

February 2026

CORE INSIGHT FROM DIAGNOSTIC H v4:
  /h/ = whispered vowel → voiced vowel
  Source crossfades: noise → glottal
  through ONE formant bank.
  The formant bank never resets.
  The source changes underneath it.

SAME PRINCIPLE APPLIED TO:

  ALL VOICED FRICATIVES (z, v, dh, zh):
    = whispered fricative → voiced fricative
    source crossfades: shaped_noise → glottal
    noise band stays throughout
    voicing fades IN under the noise
    (not: voicing + noise mixed flat —
     but: noise leading, voicing arriving)

  ALL PLOSIVES:
    The closure is NOT silence.
    During closure:
      voiced (b,d,g): quiet voicing runs
                      through closed vocal
                      tract (low-freq rumble)
      unvoiced (p,t,k): silence truly
    The burst: source spike, NOT filter reset.
    The VOT: noise → glottal crossfade
             exactly like /h/ but shorter.
    One formant bank throughout.
    No resets.

  NASALS (m, n):
    = voiced sonorant with antiformant
    source: glottal throughout (no change)
    formant bank: nasal tract formants
    transition IN from previous vowel
    transition OUT into following vowel
    while maintaining nasal murmur
    Hard gate at release: preserved.

  APPROXIMANTS (l, r, w, y):
    = voiced transitions
    source: glottal throughout
    formant bank moves continuously
    from prev vowel → through target →
    toward next vowel
    NO separate phoneme synthesis —
    pure formant trajectory.

THE UNIFYING PRINCIPLE:
  Every phoneme is a source event
  filtered through a continuously
  moving vocal tract.
  The vocal tract never stops.
  The source changes underneath it.
  Initialization transients
  are impossible
  when the filter never resets.
"""

from tonnetz_engine import (
    SR, PART_NAMES,
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
    nyq = sr/2.0
    l   = max(lo/nyq,  0.001)
    h   = min(hi/nyq,  0.499)
    if l >= h: l = h*0.5
    return butter(2, [l,h], btype='band')

# ============================================================
# PHONEME DATA
# ============================================================

PHONEMES = {

    # ---- VOWELS ----
    'AA': {
        'dur': 140, 'voiced': True,
        'F': [730, 1090, 2440, 3400],
        'B': [ 70,  110,  170,  250],
    },
    'AE': {
        'dur': 130, 'voiced': True,
        'F': [660, 1720, 2410, 3300],
        'B': [ 65,  105,  165,  250],
    },
    'AH': {
        'dur': 100, 'voiced': True,
        'F': [520, 1190, 2390, 3300],
        'B': [ 70,  110,  170,  250],
    },
    'AO': {
        'dur': 130, 'voiced': True,
        'F': [570,  840, 2410, 3300],
        'B': [ 80,   80,  160,  250],
    },
    'AW': {
        'dur': 170, 'voiced': True,
        'F':     [730, 1090, 2440, 3400],
        'F_end': [300,  870, 2240, 3300],
        'B': [70, 90, 160, 250],
        'diphthong': True,
    },
    'AY': {
        'dur': 180, 'voiced': True,
        'F':     [730, 1090, 2440, 3400],
        'F_end': [270, 2290, 3010, 3700],
        'B': [70, 100, 160, 250],
        'diphthong': True,
    },
    'OY': {
        'dur': 180, 'voiced': True,
        'F':     [570,  840, 2410, 3300],
        'F_end': [270, 2290, 3010, 3700],
        'B': [70, 90, 160, 250],
        'diphthong': True,
    },
    'OW': {
        'dur': 160, 'voiced': True,
        'F':     [450,  800, 2400, 3300],
        'F_end': [300,  870, 2240, 3300],
        'B': [70, 85, 160, 250],
        'diphthong': True,
    },
    'EH': {
        'dur': 120, 'voiced': True,
        'F': [530, 1840, 2480, 3500],
        'B': [ 60,  100,  140,  250],
    },
    'ER': {
        'dur': 130, 'voiced': True,
        'F': [490, 1350, 1690, 3300],
        'B': [ 70,  110,  170,  250],
        'r_fast_f3': True,
    },
    'IH': {
        'dur': 110, 'voiced': True,
        'F': [390, 1990, 2550, 3600],
        'B': [ 70,  110,  160,  250],
    },
    'IY': {
        'dur': 130, 'voiced': True,
        'F': [270, 2290, 3010, 3700],
        'B': [ 60,   90,  150,  200],
    },
    'OH': {
        'dur': 130, 'voiced': True,
        'F': [570,  840, 2410, 3300],
        'B': [ 80,   80,  160,  250],
    },
    'UH': {
        'dur': 110, 'voiced': True,
        'F': [440, 1020, 2240, 3300],
        'B': [ 70,  100,  160,  250],
    },
    'UW': {
        'dur': 130, 'voiced': True,
        'F': [300,  870, 2240, 3300],
        'B': [ 70,   80,  160,  250],
    },

    # ---- NASALS ----
    'M': {
        'dur': 85, 'voiced': True,
        'F': [250,  700, 2200, 3300],
        'B': [ 60,  120,  250,  350],
        'nasal': True,
        'antiformant': 1000,
        'anti_bw':      300,
        'anti_depth':   0.50,
        'amp_scale':    0.52,
        'hard_gate_ms': 14,
    },
    'N': {
        'dur': 80, 'voiced': True,
        'F': [250,  900, 2200, 3300],
        'B': [ 60,  120,  250,  350],
        'nasal': True,
        'antiformant': 1500,
        'anti_bw':      350,
        'anti_depth':   0.48,
        'amp_scale':    0.50,
        'hard_gate_ms': 12,
    },
    'NG': {
        'dur': 90, 'voiced': True,
        'F': [250,  700, 2200, 3300],
        'B': [ 60,  120,  250,  350],
        'nasal': True,
        'antiformant': 2000,
        'anti_bw':      400,
        'anti_depth':   0.48,
        'amp_scale':    0.52,
        'hard_gate_ms': 14,
    },

    # ---- FRICATIVES UNVOICED ----
    'S': {
        'dur': 100, 'voiced': False,
        'noise_bands': [(4000, 10000, 1.0)],
        'F': [6000, 8000, 10000, 11000],
        'B': [ 500,  500,   500,   500],
        'noise_only': True,
    },
    'SH': {
        'dur': 105, 'voiced': False,
        'noise_bands': [(1800, 7000, 1.0)],
        'F': [6000, 8000, 10000, 11000],
        'B': [ 500,  500,   500,   500],
        'noise_only': True,
    },
    'F_c': {   # 'F' consonant
        'dur': 90, 'voiced': False,
        'noise_bands': [(1000, 10000, 0.7),
                         (4000, 12000, 0.4)],
        'F': [6000, 8000, 10000, 11000],
        'B': [ 500,  500,   500,   500],
        'noise_only': True,
    },
    'TH': {
        'dur': 90, 'voiced': False,
        'noise_bands': [(1000, 7000, 0.75)],
        'F': [6000, 8000, 10000, 11000],
        'B': [ 500,  500,   500,   500],
        'noise_only': True,
    },

    # ---- FRICATIVES VOICED ----
    # whispered-fricative → voiced
    # same principle as H
    'Z': {
        'dur': 95, 'voiced': True,
        'noise_bands': [(3500, 8000, 0.80)],
        'F': [250,  900, 2200, 3300],
        'B': [100,  130,  220,  320],
        'voice_crossfade_frac': 0.45,
        'voiced_fric': True,
    },
    'ZH': {
        'dur': 95, 'voiced': True,
        'noise_bands': [(1500, 6500, 0.70)],
        'F': [250,  900, 2200, 3300],
        'B': [100,  130,  220,  320],
        'voice_crossfade_frac': 0.45,
        'voiced_fric': True,
    },
    'V': {
        'dur': 85, 'voiced': True,
        'noise_bands': [(800, 7000, 0.60)],
        'F': [250,  900, 2200, 3300],
        'B': [100,  130,  220,  320],
        'voice_crossfade_frac': 0.40,
        'voiced_fric': True,
    },
    'DH': {
        'dur': 80, 'voiced': True,
        'noise_bands': [(800, 5500, 0.50)],
        'F': [250,  900, 2200, 3300],
        'B': [100,  130,  220,  320],
        'voice_crossfade_frac': 0.40,
        'voiced_fric': True,
    },

    # ---- H ----
    # whispered vowel → voiced vowel
    # using following vowel formants
    'H': {
        'dur': 70, 'voiced': False,
        'h_phoneme': True,
        'F': [500, 1500, 2500, 3500],
        'B': [200,  220,  320,  420],
    },

    # ---- PLOSIVES ----
    'P': {
        'dur': 90, 'voiced': False,
        'plosive': True,
        'closure_ms': 55,
        'burst_ms':    2,
        'vot_ms':     62,
        'place': 'bilabial',
        'burst_amp':   0.35,
        'burst_hp':     500,
        'F': [800, 1200, 2500, 3500],
        'B': [200,  200,  300,  400],
    },
    'B': {
        'dur': 80, 'voiced': True,
        'plosive': True,
        'closure_ms': 45,
        'burst_ms':    2,
        'vot_ms':     14,
        'place': 'bilabial',
        'burst_amp':   0.22,
        'burst_hp':     300,
        'F': [200,  800, 2200, 3300],
        'B': [100,  120,  220,  320],
    },
    'T': {
        'dur': 85, 'voiced': False,
        'plosive': True,
        'closure_ms': 50,
        'burst_ms':    2,
        'vot_ms':     70,
        'place': 'alveolar',
        'burst_amp':   0.38,
        'burst_hp':   2000,
        'F': [800, 1600, 2600, 3600],
        'B': [200,  200,  300,  400],
    },
    'D': {
        'dur': 75, 'voiced': True,
        'plosive': True,
        'closure_ms': 40,
        'burst_ms':    2,
        'vot_ms':     15,
        'place': 'alveolar',
        'burst_amp':   0.22,
        'burst_hp':   1000,
        'F': [200,  900, 2200, 3300],
        'B': [100,  120,  220,  320],
    },
    'K': {
        'dur': 90, 'voiced': False,
        'plosive': True,
        'closure_ms': 55,
        'burst_ms':    3,
        'vot_ms':     80,
        'place': 'velar',
        'burst_amp':   0.36,
        'burst_hp':   1500,
        'F': [800, 1600, 2800, 3600],
        'B': [200,  200,  300,  400],
    },
    'G': {
        'dur': 78, 'voiced': True,
        'plosive': True,
        'closure_ms': 45,
        'burst_ms':    2,
        'vot_ms':     16,
        'place': 'velar',
        'burst_amp':   0.20,
        'burst_hp':    800,
        'F': [200,  800, 2200, 3300],
        'B': [100,  120,  220,  320],
    },

    # ---- APPROXIMANTS ----
    'L': {
        'dur': 80, 'voiced': True,
        'F': [360, 1000, 2400, 3300],
        'B': [ 80,  160,  220,  320],
    },
    'R': {
        'dur': 90, 'voiced': True,
        'F': [490, 1350, 1690, 3300],
        'B': [ 80,  120,  180,  260],
        'r_fast_f3': True,
    },
    'W': {
        'dur': 90, 'voiced': True,
        'F': [300,  610, 2200, 3300],
        'B': [ 80,   90,  210,  310],
    },
    'Y': {
        'dur': 80, 'voiced': True,
        'F': [270, 2100, 3000, 3700],
        'B': [ 65,  100,  160,  220],
    },

    'SIL': {
        'dur': 55, 'voiced': False,
        'F': [500, 1500, 2500, 3500],
        'B': [200,  200,  300,  400],
    },
}

# Map 'F' consonant symbol in word dict
# to 'F_c' in phoneme dict
PHON_ALIAS = {'F': 'F_c'}

# ============================================================
# WORD DICTIONARY
# ============================================================

WORDS = {
    'here':    ['H',  'IH', 'R',  'SIL'],
    'home':    ['H',  'OW', 'M',  'SIL'],
    'both':    ['B',  'OH', 'TH', 'SIL'],
    'now':     ['N',  'AW', 'SIL'],
    'still':   ['S',  'T',  'IH', 'L',  'SIL'],
    'water':   ['W',  'AA', 'T',  'ER', 'SIL'],
    'open':    ['OH', 'P',  'EH', 'N',  'SIL'],
    'always':  ['AA', 'L',  'W',  'EH', 'Z', 'SIL'],
    'the':     ['DH', 'AH', 'SIL'],
    'voice':   ['V',  'OY', 'S',  'SIL'],
    'that':    ['DH', 'AH', 'T',  'SIL'],
    'was':     ['W',  'AH', 'Z',  'SIL'],
    'already': ['AA', 'L',  'R',  'EH',
                'D',  'IY', 'SIL'],
    'i':       ['AY', 'SIL'],
    'am':      ['AH', 'M',  'SIL'],
    'find':    ['F',  'AY', 'N',  'D',  'SIL'],
    'where':   ['W',  'EH', 'R',  'SIL'],
    'this':    ['DH', 'IH', 'S',  'SIL'],
    'is':      ['IH', 'Z',  'SIL'],
    'not':     ['N',  'AA', 'T',  'SIL'],
    'matter':  ['M',  'AE', 'T',  'ER', 'SIL'],
    'state':   ['S',  'T',  'EH', 'T', 'SIL'],
    'of':      ['AH', 'V',  'SIL'],
    'solid':   ['S',  'AA', 'L',  'IH',
                'D',  'SIL'],
    'landing': ['L',  'AE', 'N',  'D',
                'IH', 'NG', 'SIL'],
    'named':   ['N',  'EH', 'M',  'D',  'SIL'],
    'yet':     ['Y',  'EH', 'T',  'SIL'],
    'been':    ['B',  'IH', 'N',  'SIL'],
    'wrong':   ['R',  'AO', 'NG', 'SIL'],
}

# ============================================================
# CORE SYNTHESIS ENGINE
# One formant bank. Never resets.
# Source changes underneath.
# ============================================================

T_GLOBAL = 1.0 / SR  # avoid recomputing

def resonator_sample(x, fc, bw,
                      y1, y2, T):
    """
    Single sample resonator.
    Called inside per-phoneme loops.
    """
    fc  = max(20.0, min(float(SR*0.48), fc))
    bw  = max(10.0, bw)
    a2  = -np.exp(-2*np.pi*bw*T)
    a1  =  2*np.exp(-np.pi*bw*T) * \
            np.cos(2*np.pi*fc*T)
    b0  = 1.0 - a1 - a2
    y   = b0*x + a1*y1 + a2*y2
    return y, y, float(a2)  # y, new_y1, new_y2


def warm_resonator(fc, bw, warm_n, T):
    """
    Pre-charge a single resonator.
    Returns (y1, y2) warm state.
    """
    y1 = y2 = 0.0
    fc  = max(20.0, min(float(SR*0.48),
                         float(fc)))
    bw  = max(10.0, float(bw))
    a2  = -np.exp(-2*np.pi*bw*T)
    a1  =  2*np.exp(-np.pi*bw*T)*\
            np.cos(2*np.pi*float(fc)*T)
    b0  = 1.0 - a1 - a2
    for _ in range(warm_n):
        x  = np.random.normal(0, 0.0004)
        y  = b0*x + a1*y1 + a2*y2
        y2 = y1
        y1 = y
    return y1, y2


def run_formant_bank(source,
                      F_arrs, B_arrs,
                      gains,
                      init_states=None,
                      warm_n=352):
    """
    Run parallel formant bank.
    source: float32 array, length n
    F_arrs: list of 4 float32 arrays len n
    B_arrs: list of 4 float32 arrays len n
    gains: list of 4 floats
    init_states: list of (y1,y2) or None
    warm_n: samples to pre-warm if no state

    Returns (output float32 len n,
             final_states list of (y1,y2))
    """
    n      = len(source)
    T      = T_GLOBAL
    result = np.zeros(n, dtype=DTYPE)
    final_states = []

    for fi in range(4):
        fa   = F_arrs[fi]
        ba   = B_arrs[fi]
        gain = gains[fi]

        if init_states is not None:
            y1, y2 = init_states[fi]
        else:
            y1, y2 = warm_resonator(
                fa[0], ba[0], warm_n, T)

        out = np.zeros(n, dtype=DTYPE)
        for i in range(n):
            fc  = max(20.0, min(
                float(SR*0.48),
                float(fa[i])))
            bw  = max(10.0, float(ba[i]))
            a2  = -np.exp(-2*np.pi*bw*T)
            a1  =  2*np.exp(-np.pi*bw*T)*\
                    np.cos(2*np.pi*fc*T)
            b0  = 1.0 - a1 - a2
            y   = b0*float(source[i]) + \
                  a1*y1 + a2*y2
            y2  = y1
            y1  = y
            out[i] = y

        result += out * gain
        final_states.append((y1, y2))

    return result, final_states


# ============================================================
# GLOTTAL SOURCE
# ============================================================

def glottal_source(pitch_hz, n_samples,
                    jitter=0.005,
                    shimmer=0.030,
                    sr=SR):
    n_s = int(n_samples)
    if n_s < 2:
        return f32(np.zeros(2))
    T   = 1.0/sr
    t   = np.arange(n_s, dtype=DTYPE)/sr

    vib = f32(np.clip((t-0.05)/0.05,0,1))
    ft  = pitch_hz*(1+0.007*vib*np.sin(
        2*np.pi*5.0*t))

    ph  = np.zeros(n_s, dtype=DTYPE)
    p   = 0.0
    for i in range(n_s):
        p += float(ft[i])*(
            1+np.random.normal(0,jitter))/sr
        if p >= 1.0: p -= 1.0
        ph[i] = p

    oq  = 0.65
    src = np.where(ph<oq,
        (ph/oq)*(2-ph/oq),
        1-(ph-oq)/(1-oq+1e-9))
    src = f32(np.diff(
        src, prepend=src[0]))

    try:
        b,a = safe_lp(20, sr)
        sh  = f32(np.random.normal(0,1,n_s))
        sh  = f32(lfilter(b,a,sh))
    except:
        sh  = f32(np.ones(n_s))
    sh  = f32(np.clip(1+shimmer*sh,0.4,1.6))
    src = src*sh

    asp = f32(np.random.normal(0,0.022,n_s))
    try:
        b,a = safe_bp(400, 2200, sr)
        asp = f32(lfilter(b,a,asp))
    except:
        asp = f32(np.zeros(n_s))

    return src + asp


def shaped_noise_seg(n_samples, bands,
                      sr=SR):
    """
    Noise shaped by bandpass filter sum.
    Exactly n_samples long.
    """
    n_s    = int(n_samples)
    noise  = f32(np.random.normal(0,1,n_s))
    result = np.zeros(n_s, dtype=DTYPE)
    for lo, hi, g in bands:
        try:
            b,a = safe_bp(
                min(lo, sr*0.47),
                min(hi, sr*0.48), sr)
            result += f32(
                lfilter(b,a,noise))*g
        except:
            pass
    mx = np.max(np.abs(result))
    if mx > 0: result /= mx
    return result


# ============================================================
# FORMANT ARRAY BUILDERS
# ============================================================

def constant_f_arrays(F, B, n):
    """All formants at fixed value."""
    return (
        [f32(np.full(n, float(f)))
         for f in F],
        [f32(np.full(n, float(b)))
         for b in B]
    )


def interpolated_f_arrays(F_from, B_from,
                            F_to, B_to, n):
    """Linear interpolation F_from→F_to."""
    return (
        [f32(np.linspace(float(F_from[i]),
                          float(F_to[i]),
                          n))
         for i in range(4)],
        [f32(np.linspace(float(B_from[i]),
                          float(B_to[i]),
                          n))
         for i in range(4)]
    )


def coarticulated_f_arrays(F_tgt, B_tgt,
                             F_prev, F_next,
                             n_s,
                             F_end=None,
                             diphthong=False,
                             r_fast_f3=False):
    """
    3-zone coarticulation.
    20% onset from F_prev
    60% steady (or diphthong movement)
    20% toward F_next
    """
    F_end_ = F_end if F_end else F_tgt
    n_on   = int(0.20*n_s)
    n_off  = int(0.20*n_s)
    n_mid  = n_s - n_on - n_off

    F_arrs = []
    B_arrs = []

    for fi in range(4):
        arr = np.zeros(n_s, dtype=DTYPE)

        if n_on > 0:
            arr[:n_on] = np.linspace(
                float(F_prev[fi]),
                float(F_tgt[fi]),
                n_on, dtype=DTYPE)

        if n_mid > 0:
            if diphthong:
                n_mv = int(n_mid*0.72)
                n_hd = n_mid - n_mv
                if n_mv > 0:
                    arr[n_on:n_on+n_mv] = \
                        np.linspace(
                            float(F_tgt[fi]),
                            float(F_end_[fi]),
                            n_mv, dtype=DTYPE)
                if n_hd > 0:
                    arr[n_on+n_mv:
                        n_on+n_mid] = \
                        float(F_end_[fi])
            else:
                arr[n_on:n_on+n_mid] = \
                    float(F_tgt[fi])

        if n_off > 0:
            f_from = (float(F_end_[fi])
                      if diphthong
                      else float(F_tgt[fi]))
            arr[n_on+n_mid:] = np.linspace(
                f_from,
                float(F_next[fi]),
                n_off, dtype=DTYPE)

        # R: fast F3 drop in first 30ms
        if r_fast_f3 and fi == 2:
            n_drop   = min(int(0.030*SR), n_s)
            f3_start = float(F_prev[2])
            arr[:n_drop] = np.linspace(
                f3_start, 1690.0,
                n_drop, dtype=DTYPE)
            arr[n_drop:] = 1690.0

        F_arrs.append(arr)
        B_arrs.append(f32(np.full(
            n_s, float(B_tgt[fi]))))

    return F_arrs, B_arrs


# ============================================================
# PHONEME SYNTHESIS — UNIFIED ENGINE
# Source changes. Filter continues.
# ============================================================

def synth_phoneme(phon, pitch_hz,
                   dur_ms=None,
                   prev_phon=None,
                   next_phon=None,
                   prev_states=None,
                   sr=SR):
    """
    Synthesize one phoneme.

    prev_states: list of (y1,y2) per formant
    from the previous phoneme's final state.
    When provided: NO warm-up needed.
    The filter continues.

    Returns: (audio float32, final_states)
    """
    phon   = PHON_ALIAS.get(phon, phon)
    data   = PHONEMES.get(phon)

    if data is None:
        n = int((dur_ms or 50)/1000*sr)
        dummy = f32(np.zeros(max(n,2)))
        dummy_st = [(0.0,0.0)]*4
        return dummy, dummy_st

    d_ms  = dur_ms if dur_ms is not None \
            else data['dur']
    n_s   = max(4, int(d_ms/1000.0*sr))

    # Silence
    if phon == 'SIL':
        out = f32(np.zeros(n_s))
        st  = prev_states if prev_states \
              else [(0.0,0.0)]*4
        return out, st

    # Context formants
    F_tgt  = data['F']
    B_tgt  = data['B']
    F_diph = data.get('F_end', F_tgt)

    F_prev_f = (PHONEMES[prev_phon]['F']
                if prev_phon and
                prev_phon in PHONEMES
                else F_tgt)
    F_next_f = (PHONEMES[next_phon]['F']
                if next_phon and
                next_phon in PHONEMES
                else F_diph)

    # Route to specialised synths
    if data.get('h_phoneme', False):
        return synth_H(
            data, pitch_hz, n_s,
            next_phon, prev_states, sr)

    if data.get('plosive', False):
        return synth_plosive(
            phon, data, pitch_hz, n_s,
            F_prev_f, F_next_f,
            prev_states, sr)

    if data.get('noise_only', False):
        return synth_fric_unvoiced(
            data, n_s,
            prev_states, sr)

    if data.get('voiced_fric', False):
        return synth_fric_voiced(
            data, pitch_hz, n_s,
            F_prev_f, F_next_f,
            prev_states, sr)

    # Sonorant (vowel, nasal, approximant)
    return synth_sonorant(
        phon, data, pitch_hz, n_s,
        F_prev_f, F_next_f,
        F_diph, prev_states, sr)


# ============================================================
# H — whispered vowel → voiced vowel
# Exact port of diagnostic H v4
# ============================================================

def synth_H(data, pitch_hz, n_s,
             next_phon, prev_states, sr=SR):

    T = 1.0/sr

    # Following vowel formants
    if next_phon and next_phon in PHONEMES:
        nxt   = PHONEMES[next_phon]
        F_use = nxt['F']
        # Wide BW = breathy
        B_use = [min(float(b)*3.5, 550.0)
                 for b in nxt['B']]
        F_end = nxt.get('F_end', F_use)
    else:
        F_use = [500, 1500, 2500, 3500]
        B_use = [200,  220,  350,  450]
        F_end = F_use

    # Crossfade sizes — integer arithmetic
    n_h     = int(n_s * 0.45)
    n_v     = n_s - n_h
    n_cross = int(min(
        0.025*sr,
        n_h*0.4,
        n_v*0.4))

    # Sources — both exactly n_s
    noise_src = f32(
        np.random.normal(0, 1, n_s))
    glot_src  = glottal_source(
        pitch_hz, n_s,
        jitter=0.005, shimmer=0.030,
        sr=sr)

    # Crossfade envelopes
    noise_env = np.zeros(n_s, dtype=DTYPE)
    glot_env  = np.zeros(n_s, dtype=DTYPE)
    cs        = n_h - n_cross

    if cs > 0:
        noise_env[:cs] = 1.0
    if n_cross > 0:
        fo = f32(np.linspace(1.0,0.0,n_cross))
        fi = 1.0 - fo
        noise_env[cs:cs+n_cross] = fo
        glot_env[cs:cs+n_cross]  = fi
    vs = cs + n_cross
    if vs < n_s:
        glot_env[vs:] = 1.0

    source = f32(noise_src*noise_env +
                  glot_src*glot_env)

    # Formant arrays — hold F during H,
    # diphthong if vowel has F_end
    n_diph_start = n_h + int(n_v*0.30)
    F_arrs = []
    B_arrs = []
    for fi in range(4):
        fa = np.zeros(n_s, dtype=DTYPE)
        fa[:n_diph_start] = float(F_use[fi])
        if n_diph_start < n_s:
            n_mv = n_s - n_diph_start
            fa[n_diph_start:] = np.linspace(
                float(F_use[fi]),
                float(F_end[fi]),
                n_mv, dtype=DTYPE)
        F_arrs.append(fa)
        B_arrs.append(f32(np.full(
            n_s, float(B_use[fi]))))

    gains = [0.55, 0.75, 0.45, 0.25]
    result, final_states = run_formant_bank(
        source, F_arrs, B_arrs, gains,
        init_states=prev_states,
        warm_n=int(0.008*sr))

    # Amplitude: /h/ quiet → vowel full
    amp_env = np.zeros(n_s, dtype=DTYPE)
    if n_h > 0:
        amp_env[:n_h] = np.linspace(
            0.0, 0.45, n_h, dtype=DTYPE)
    if n_h < n_s:
        amp_env[n_h:] = np.linspace(
            0.45, 1.0,
            n_s-n_h, dtype=DTYPE)
    rel_n = int(0.022*sr)
    if rel_n > 0 and rel_n < n_s:
        amp_env[-rel_n:] *= f32(
            np.linspace(1.0,0.0,rel_n))

    result = result * f32(amp_env)
    mx = np.max(np.abs(result))
    if mx > 0: result /= mx
    return f32(result), final_states


# ============================================================
# UNVOICED FRICATIVE — shaped noise only
# ============================================================

def synth_fric_unvoiced(data, n_s,
                         prev_states,
                         sr=SR):
    bands  = data.get('noise_bands', [])
    result = shaped_noise_seg(n_s, bands, sr)

    atk_n = int(min(0.006, 0.1)*sr)
    rel_n = int(min(0.008, 0.1)*sr)
    env   = f32(np.ones(n_s))
    if atk_n > 0:
        env[:atk_n] = f32(
            np.linspace(0,1,atk_n))
    if rel_n > 0:
        env[-rel_n:] = f32(
            np.linspace(1,0,rel_n))
    result = result*env
    mx = np.max(np.abs(result))
    if mx > 0: result /= mx
    # Carry state through (unchanged)
    st = prev_states if prev_states \
         else [(0.0,0.0)]*4
    return f32(result), st


# ============================================================
# VOICED FRICATIVE
# Same principle as H:
# noise → voiced crossfade
# through ONE formant bank
# ============================================================

def synth_fric_voiced(data, pitch_hz,
                       n_s,
                       F_prev, F_next,
                       prev_states,
                       sr=SR):
    F_tgt  = data['F']
    B_tgt  = data['B']
    bands  = data.get('noise_bands', [])
    vcf    = data.get(
        'voice_crossfade_frac', 0.40)

    # Sources — both exactly n_s
    noise_src = shaped_noise_seg(
        n_s, bands, sr)
    glot_src  = glottal_source(
        pitch_hz, n_s,
        jitter=0.005, shimmer=0.030,
        sr=sr)

    # Crossfade: noise leads, voicing arrives
    n_cross = int(vcf * n_s)
    noise_env = np.ones(n_s, dtype=DTYPE)
    glot_env  = np.zeros(n_s, dtype=DTYPE)
    if n_cross > 0:
        glot_env[:n_cross] = f32(
            np.linspace(0.0, 1.0, n_cross))
        # Noise stays at full throughout —
        # voicing adds underneath
    source = f32(noise_src*noise_env +
                  glot_src*glot_env)

    # Formant arrays — coarticulated
    F_arrs, B_arrs = coarticulated_f_arrays(
        F_tgt, B_tgt,
        F_prev, F_next,
        n_s)

    gains = [0.55, 0.75, 0.45, 0.25]
    result, final_states = run_formant_bank(
        source, F_arrs, B_arrs, gains,
        init_states=prev_states)

    atk_n = int(0.018*sr)
    rel_n = int(0.014*sr)
    env   = f32(np.ones(n_s))
    if atk_n > 0 and atk_n < n_s:
        env[:atk_n] = f32(
            np.linspace(0,1,atk_n)**0.5)
    if rel_n > 0:
        env[-rel_n:] = f32(
            np.linspace(1,0,rel_n))
    result = result*env
    mx = np.max(np.abs(result))
    if mx > 0: result /= mx
    return f32(result), final_states


# ============================================================
# PLOSIVE
# closure: voiced plosives hum quietly
#          unvoiced: true silence
# burst:   brief spike
# VOT:     noise→glottal crossfade (like H)
# trans:   F2 locus into vowel
# ONE formant bank throughout
# ============================================================

def synth_plosive(phon, data, pitch_hz,
                   n_s_total,
                   F_prev, F_next,
                   prev_states, sr=SR):

    closure_ms = data.get('closure_ms', 45)
    burst_ms   = data.get('burst_ms',   2)
    vot_ms     = data.get('vot_ms',    60)
    voiced     = data.get('voiced',  False)
    burst_amp  = data.get('burst_amp', 0.35)
    burst_hp   = data.get('burst_hp', 1500)
    place      = data.get('place','alveolar')

    n_clos  = int(closure_ms/1000*sr)
    n_burst = int(burst_ms/1000*sr)
    n_vot   = int(vot_ms/1000*sr)
    n_trans = int(0.042*sr)
    n_total = n_clos+n_burst+n_vot+n_trans

    F2_LOCUS = {
        'bilabial':  720,
        'alveolar': 1800,
        'velar':    3000,
    }
    locus  = F2_LOCUS.get(place, 1800)

    nxt_data = PHONEMES.get(
        PHON_ALIAS.get(F_next[0]
            if isinstance(F_next,list)
            else '', ''),
        None)
    # F_next is already formant array
    # use it directly
    F_vow  = F_next
    B_vow  = data.get('B', [200]*4)
    # Try to get proper B from next phoneme
    # F_next is passed as formant list
    # so we use data['B'] as approximation

    # Build per-segment formant arrays
    # for each phase of the plosive

    # Segment 1: CLOSURE
    # Formants: neutral/closed
    F_clos = [300, 800, 2200, 3300]
    B_clos = [100, 100, 200, 300]

    # Segment 2: BURST
    F_burst_start = data.get('F', F_clos)

    # Segment 3: VOT / aspiration
    # Formants: move from burst toward vowel
    # with wide BW (breathy)
    F_vot_start = F_burst_start
    F_vot_end   = F_vow
    B_vot       = [min(float(b)*3.0, 500)
                   for b in B_vow]

    # Segment 4: TRANSITION
    # F2 from locus → vowel target
    F_trans_start = [
        400,      # F1 neutral
        locus,    # F2 locus — KEY
        float(F_vow[2]),
        float(F_vow[3]),
    ]

    # Build full-length arrays
    fa_list = [np.zeros(n_total, dtype=DTYPE)
               for _ in range(4)]
    ba_list = [np.zeros(n_total, dtype=DTYPE)
               for _ in range(4)]

    for fi in range(4):
        # Closure zone
        if n_clos > 0:
            fa_list[fi][:n_clos] = \
                float(F_clos[fi])
            ba_list[fi][:n_clos] = \
                float(B_clos[fi])

        # Burst zone
        s = n_clos
        e = n_clos+n_burst
        if n_burst > 0:
            fa_list[fi][s:e] = \
                float(F_burst_start[fi])
            ba_list[fi][s:e] = 300.0

        # VOT zone — formants drift
        # toward vowel, BW wide
        s = n_clos+n_burst
        e = s+n_vot
        if n_vot > 0:
            fa_list[fi][s:e] = np.linspace(
                float(F_vot_start[fi]),
                float(F_vot_end[fi]),
                n_vot, dtype=DTYPE)
            ba_list[fi][s:e] = B_vot[fi]

        # Transition zone — F2 locus
        s = n_clos+n_burst+n_vot
        e = s+n_trans
        if n_trans > 0:
            fa_list[fi][s:e] = np.linspace(
                float(F_trans_start[fi]),
                float(F_vow[fi]),
                n_trans, dtype=DTYPE)
            ba_list[fi][s:e] = \
                float(B_vow[fi])

    fa_list = [f32(a) for a in fa_list]
    ba_list = [f32(a) for a in ba_list]

    # Build source array
    source = np.zeros(n_total, dtype=DTYPE)

    # Closure: voiced plosives have
    # quiet voicing; unvoiced: silence
    if voiced and n_clos > 0:
        hum = glottal_source(
            pitch_hz, n_clos,
            jitter=0.015, shimmer=0.10,
            sr=sr)
        source[:n_clos] = hum * 0.06

    # Burst: noise spike
    if n_burst > 0:
        burst = f32(
            np.random.normal(0,1,n_burst))
        try:
            b,a   = safe_hp(burst_hp, sr)
            burst = f32(lfilter(b,a,burst))
        except:
            pass
        b_env = f32(np.exp(
            -np.arange(n_burst)/
            n_burst*20))
        s = n_clos
        source[s:s+n_burst] = \
            burst*b_env*burst_amp

    # VOT + transition:
    # noise → glottal crossfade (like H)
    n_vot_trans = n_vot + n_trans
    if n_vot_trans > 0:
        noise_vt = shaped_noise_seg(
            n_vot_trans,
            [(200, 8000, 0.9)], sr)
        glot_vt  = glottal_source(
            pitch_hz, n_vot_trans,
            jitter=0.005, shimmer=0.030,
            sr=sr)

        # Crossfade: noise → glottal
        # over VOT duration
        ne = np.ones(n_vot_trans, dtype=DTYPE)
        ge = np.zeros(n_vot_trans, dtype=DTYPE)
        if n_vot > 0:
            ne[:n_vot] = f32(
                np.linspace(1.0, 0.0, n_vot))
            ge[:n_vot] = f32(
                np.linspace(0.0, 1.0, n_vot))
        if n_trans > 0:
            ne[n_vot:] = 0.0
            ge[n_vot:] = 1.0

        s = n_clos+n_burst
        source[s:s+n_vot_trans] = \
            f32(noise_vt*ne + glot_vt*ge)

    gains = [0.55, 0.75, 0.45, 0.25]
    result, final_states = run_formant_bank(
        source, fa_list, ba_list, gains,
        init_states=prev_states)

    # Amplitude envelope
    env = np.zeros(n_total, dtype=DTYPE)
    # Silence during closure
    if n_clos > 0 and voiced:
        env[:n_clos] = 0.06
    # Ramp up from burst onset
    ramp_start = n_clos
    ramp_end   = n_total
    ramp_n     = ramp_end - ramp_start
    if ramp_n > 0:
        env[ramp_start:] = np.linspace(
            0.0, 1.0, ramp_n, dtype=DTYPE)
    rel_n = int(0.018*sr)
    if rel_n > 0 and rel_n < n_total:
        env[-rel_n:] *= f32(
            np.linspace(1,0,rel_n))

    result = result * f32(env)
    mx = np.max(np.abs(result))
    if mx > 0: result /= mx
    return f32(result), final_states


# ============================================================
# SONORANT (vowel, nasal, approximant)
# ============================================================

def synth_sonorant(phon, data, pitch_hz,
                    n_s, F_prev, F_next,
                    F_diph, prev_states,
                    sr=SR):

    F_tgt    = data['F']
    B_tgt    = data['B']
    is_diph  = data.get('diphthong', False)
    r_f3     = data.get('r_fast_f3', False)

    F_arrs, B_arrs = coarticulated_f_arrays(
        F_tgt, B_tgt,
        F_prev, F_next,
        n_s,
        F_end=F_diph,
        diphthong=is_diph,
        r_fast_f3=r_f3)

    source = glottal_source(
        pitch_hz, n_s,
        jitter=0.005, shimmer=0.030,
        sr=sr)

    gains = [0.55, 0.75, 0.45, 0.25]
    result, final_states = run_formant_bank(
        source, F_arrs, B_arrs, gains,
        init_states=prev_states)

    # Nasal antiformant
    if data.get('nasal', False):
        af    = float(data.get(
            'antiformant', 1000))
        af_bw = float(data.get('anti_bw',300))
        depth = data.get('anti_depth', 0.50)
        T     = 1.0/sr
        # Anti-resonator: subtract resonated
        anti  = np.zeros(n_s, dtype=DTYPE)
        y1 = y2 = 0.0
        for i in range(n_s):
            fc  = af
            bw  = af_bw
            a2  = -np.exp(-2*np.pi*bw*T)
            a1  =  2*np.exp(-np.pi*bw*T)*\
                    np.cos(2*np.pi*fc*T)
            b0  = 1.0-a1-a2
            y   = b0*float(result[i])+a1*y1+a2*y2
            y2  = y1; y1 = y
            anti[i] = y
        result = result - f32(anti)*depth
        result *= data.get('amp_scale', 0.52)
        # Hard gate
        hg_n = min(int(
            data.get('hard_gate_ms',12)
            /1000*sr), n_s//4)
        if hg_n > 0:
            result[-hg_n:] = 0.0

    # Envelope
    atk_ms = {'M':18,'N':16,'NG':18,
               'L':12,'R':12,'W':18,
               'Y':12,'ER':15}.get(phon,22)
    rel_ms = {'M':15,'N':14,'NG':15,
               'L':14,'R':14}.get(phon,24)
    atk_n  = min(int(atk_ms/1000*sr),n_s//3)
    rel_n  = min(int(rel_ms/1000*sr),n_s//3)
    env    = f32(np.ones(n_s))
    if atk_n > 0:
        env[:atk_n] = f32(
            np.linspace(0,1,atk_n)**0.45)
    if rel_n > 0:
        env[-rel_n:] = f32(
            np.linspace(1,0,rel_n)**0.5)
    result = result*env

    mx = np.max(np.abs(result))
    if mx > 0: result /= mx
    return f32(result), final_states


# ============================================================
# WORD SYNTHESIZER
# State threads through all phonemes.
# The vocal tract never stops.
# ============================================================

def synth_word(word, pitch_hz=175,
               tempo_scale=1.0,
               sr=SR):
    """
    Synthesizes word by threading
    resonator state across phonemes.
    No resets between phonemes.
    """
    raw_phonemes = WORDS.get(word.lower())
    if raw_phonemes is None:
        print(f"  '{word}' not in dict")
        return f32(np.zeros(int(0.1*sr)))

    phonemes = [PHON_ALIAS.get(p,p)
                for p in raw_phonemes]

    segments     = []
    active_state = None   # threads through

    for i, phon in enumerate(phonemes):
        prev_p = phonemes[i-1] if i>0 \
                 else None
        next_p = phonemes[i+1] \
                 if i<len(phonemes)-1 \
                 else None
        d_ms   = PHONEMES.get(
            phon,{}).get('dur',80)
        d_ms  /= tempo_scale

        seg, active_state = synth_phoneme(
            phon, pitch_hz,
            dur_ms=d_ms,
            prev_phon=prev_p,
            next_phon=next_p,
            prev_states=active_state,
            sr=sr)
        segments.append(f32(seg))

    if not segments:
        return f32(np.zeros(int(0.1*sr)))

    # Direct concatenation —
    # no crossfade needed because
    # the filter state is continuous
    result = f32(np.concatenate(segments))
    mx = np.max(np.abs(result))
    if mx > 0: result /= mx
    return result


def synth_phrase(word_list,
                  pitch_base=175,
                  sr=SR):
    segs = []
    nw   = len(word_list)
    for wi, word in enumerate(word_list):
        prog  = wi/max(nw-1,1)
        pitch = pitch_base*(1-0.08*prog)
        tempo = 1.0+0.06*float(
            np.random.uniform(-1,1))
        seg   = synth_word(
            word, pitch_hz=pitch,
            tempo_scale=tempo, sr=sr)
        segs.append(f32(seg))
        if wi < nw-1:
            segs.append(f32(np.zeros(
                int(0.080*sr))))
    result = f32(np.concatenate(segs))
    n   = len(result)
    env = f32(np.ones(n))
    atk = int(0.018*sr)
    rel = int(0.050*sr)
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


def apply_room(sig, rt60=1.5,
                dr=0.50, sr=SR):
    rev = RoomReverb(rt60=rt60, sr=sr,
                     direct_ratio=dr)
    return f32(rev.process(sig))


def write_wav(path, sig, sr=SR):
    sig = f32(sig)
    mx  = np.max(np.abs(sig))
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
    print("VOCAL WORDS v4")
    print("="*60)
    print()
    print("  Core principle:")
    print("  The vocal tract never stops.")
    print("  The source changes underneath.")
    print("  No filter resets.")
    print("  No initialization transients.")
    print()
    print("  H  = whispered vowel → voiced")
    print("  Z  = noise → voiced crossfade")
    print("  V  = noise → voiced crossfade")
    print("  DH = noise → voiced crossfade")
    print("  P/T/K = silence + burst + ")
    print("          noise→glottal (like H)")
    print("  B/D/G = quiet hum + burst +")
    print("          noise→glottal (like H)")
    print()

    pitch = 175.0

    # ---- PHONEME GROUPS 6x ----
    print("  Writing phoneme groups (6x)...")

    GROUPS = [
        ("vowels",
         ['AA','AE','AH','EH','ER',
          'IH','IY','OH','UH','UW']),
        ("diphthongs",
         ['AW','AY','OW','OY']),
        ("nasals",
         ['M','N','NG']),
        ("fric_unvoiced",
         ['S','SH','F_c','TH']),
        ("H_and_voiced_fric",
         ['H','Z','V','DH','ZH']),
        ("plosives_unvoiced",
         ['P','T','K']),
        ("plosives_voiced",
         ['B','D','G']),
        ("approximants",
         ['L','R','W','Y']),
    ]

    for gname, plist in GROUPS:
        segs = []
        for ph in plist:
            base = PHONEMES.get(
                ph,{}).get('dur',80)
            dil  = base*6.0
            seg, _ = synth_phoneme(
                ph, pitch,
                dur_ms=dil,
                prev_phon='AA',
                next_phon='AA',
                prev_states=None,
                sr=SR)
            segs.append(f32(seg))
            segs.append(f32(np.zeros(
                int(0.22*SR))))
        audio = f32(np.concatenate(segs))
        audio = apply_room(
            audio, rt60=1.1, dr=0.60)
        fname = (f"output_words/"
                 f"phon_{gname}_6x.wav")
        write_wav(fname, audio)
        print(f"    {fname}")

    # ---- TARGET WORDS ----
    print()
    print("  Writing target words...")
    targets = [
        'here','home','water',
        'still','open','always',
        'both','now','voice',
        'matter','landing','state',
    ]

    for word in targets:
        seg   = synth_word(
            word, pitch_hz=pitch)
        seg   = apply_room(
            seg, rt60=1.5, dr=0.50)
        fname = f"output_words/{word}.wav"
        write_wav(fname, seg)
        print(f"    {word}")

    # ---- SLOW WORDS ----
    print()
    print("  Writing slow words (0.55x)...")
    for word in targets:
        seg   = synth_word(
            word, pitch_hz=pitch,
            tempo_scale=0.55)
        seg   = apply_room(
            seg, rt60=1.5, dr=0.50)
        fname = (f"output_words/"
                 f"{word}_slow.wav")
        write_wav(fname, seg)
    print("    done.")

    # ---- PHRASES ----
    print()
    print("  Writing phrases...")
    phrases = [
        ['here'],
        ['home'],
        ['still','here'],
        ['always','open'],
        ['the','voice'],
        ['water','home'],
        ['always','home'],
    ]
    for pw in phrases:
        label = "_".join(pw)
        seg   = synth_phrase(
            pw, pitch_base=172)
        seg   = apply_room(
            seg, rt60=1.8, dr=0.46)
        fname = (f"output_words/"
                 f"{label}.wav")
        write_wav(fname, seg)
        dur   = len(seg)/SR
        print(f"    '{' '.join(pw)}' "
              f"({dur:.2f}s)")

    print()
    print("="*60)
    print()
    print("  Listen in order:")
    print()
    print("  1. H and voiced fricatives")
    print("     (the most changed group)")
    print("  afplay output_words/"
          "phon_H_and_voiced_fric_6x.wav")
    print()
    print("  2. Plosives")
    print("  afplay output_words/"
          "phon_plosives_unvoiced_6x.wav")
    print("  afplay output_words/"
          "phon_plosives_voiced_6x.wav")
    print()
    print("  3. Slow words")
    for w in ['here','home','water',
               'still','open','always']:
        print(f"  afplay output_words/"
              f"{w}_slow.wav")
    print()
    print("  4. Normal words")
    for w in ['here','home','water',
               'still','open','always']:
        print(f"  afplay output_words/"
              f"{w}.wav")
    print()
    print("  WHAT CHANGED:")
    print()
    print("  H:  no artifact possible —")
    print("      filter never resets")
    print("  Z:  buzzes from the start —")
    print("      voicing fades in under noise")
    print("  P/T/K: cleaner burst —")
    print("         VOT is noise→glottal")
    print("         same as H")
    print("  B/D/G: pre-voicing audible")
    print("         place clear via F2 locus")
    print()
