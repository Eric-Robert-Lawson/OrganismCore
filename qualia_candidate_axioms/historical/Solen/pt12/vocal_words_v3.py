"""
VOCAL WORDS v3

February 2026

ROOT CAUSE IDENTIFIED:
  IIR resonator filter initialization
  from zero state causes click/chirp
  transient at start of every phoneme.
  This is the (k+ch) artifact
  heard throughout.

FIXES IN v3:

  FIX 1: RESONATOR WARM-UP
    Before synthesizing each phoneme,
    run the formant bank for 8ms
    of low-amplitude noise
    to charge the filter state.
    Then discard those samples.
    The filter starts 'warm' —
    no initialization transient.

  FIX 2: H BYPASS FORMANT BANK
    H should be:
    - Noise bandpass filtered directly
    - NO resonator involvement
    - Just: noise → broadband shaping
    - The following vowel formants
      used only for the spectral tilt
      not for resonator filtering.

  FIX 3: PLOSIVE BURST SHORTENED
    Burst duration: 2-3ms maximum.
    Current 4-6ms is too long.
    Real plosive bursts are extremely brief.
    The VOT then carries the identity.

  FIX 4: Z FIXED
    Z noise band: 3500-8000Hz (narrower).
    Voicing: full amplitude underneath.
    Mix: 70% voicing, 30% noise.
    The voicing IS the Z character.
    The noise just adds the sibilance.

  FIX 5: NASAL HARD GATE
    Last 12ms of M and N:
    hard zero. No envelope ramp.
    Kills the ringing completely.

  FIX 6: PLOSIVE CLOSURE
    During closure (silence):
    run formant bank on zeros
    to pre-charge state toward
    the following vowel's formants.
    No audio output but filter warms up.
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
    nyq = sr/2.0
    return butter(2,
        min(fc/nyq, 0.499),
        btype='low')

def safe_hp(fc, sr=SR):
    nyq = sr/2.0
    return butter(2,
        min(fc/nyq, 0.499),
        btype='high')

def safe_bp(lo, hi, sr=SR):
    nyq = sr/2.0
    l   = max(lo/nyq,  0.001)
    h   = min(hi/nyq,  0.499)
    if l >= h: l = h*0.5
    return butter(2, [l,h], btype='band')


# ============================================================
# RESONATOR — with explicit state in/out
# ============================================================

def resonator_with_state(signal,
                          f_c, bw,
                          y1_in=0.0,
                          y2_in=0.0,
                          gain=1.0,
                          sr=SR):
    """
    IIR resonator.
    Returns (output, y1_out, y2_out).
    Caller manages state across calls.
    """
    n_s = len(signal)
    if n_s == 0:
        return (f32(np.zeros(0)),
                y1_in, y2_in)
    T   = 1.0/sr
    fc  = max(20.0, min(float(sr*0.48),
                         float(f_c)))
    bw_ = max(10.0, float(bw))
    a2  = -np.exp(-2*np.pi*bw_*T)
    a1  =  2*np.exp(-np.pi*bw_*T) * \
            np.cos(2*np.pi*fc*T)
    b0  = 1.0 - a1 - a2

    out = np.zeros(n_s, dtype=DTYPE)
    y1  = float(y1_in)
    y2  = float(y2_in)
    for i in range(n_s):
        y  = (b0*float(signal[i])
              + a1*y1 + a2*y2)
        y2 = y1
        y1 = y
        out[i] = y

    return out*gain, y1, y2


def warm_up_resonator(f_c, bw,
                       warm_ms=8.0,
                       sr=SR):
    """
    FIX 1: Pre-charge a resonator
    by running it on low noise.
    Returns (y1, y2) — the warm state.
    Discard audio output.
    This eliminates initialization transient.
    """
    n_warm = int(warm_ms/1000*sr)
    if n_warm < 2:
        return 0.0, 0.0
    noise  = f32(np.random.normal(
        0, 0.001, n_warm))
    _, y1, y2 = resonator_with_state(
        noise, f_c, bw, sr=sr)
    return y1, y2


def formant_bank_warmed(signal,
                         F_arrs, B_arrs,
                         gains,
                         warm_ms=8.0,
                         block=128,
                         sr=SR):
    """
    Parallel formant bank with
    pre-warmed filter states.
    No initialization transients.
    """
    n_s    = len(signal)
    n_form = len(F_arrs)
    result = np.zeros(n_s, dtype=DTYPE)

    for fi in range(n_form):
        # Warm up using initial formant value
        f_init = float(F_arrs[fi][0]) \
                 if len(F_arrs[fi])>0 \
                 else 500.0
        bw_init = float(B_arrs[fi][0]) \
                  if len(B_arrs[fi])>0 \
                  else 100.0
        y1, y2 = warm_up_resonator(
            f_init, bw_init, warm_ms, sr)

        out_fi = np.zeros(n_s, dtype=DTYPE)

        for start in range(0, n_s, block):
            end  = min(start+block, n_s)
            seg  = signal[start:end]
            fc_  = float(np.mean(
                F_arrs[fi][start:end]))
            bw_  = float(np.mean(
                B_arrs[fi][start:end]))
            seg_out, y1, y2 = \
                resonator_with_state(
                    seg, fc_, bw_,
                    y1_in=y1,
                    y2_in=y2,
                    gain=1.0, sr=sr)
            out_fi[start:end] = seg_out

        result += out_fi * gains[fi]

    return result


# ============================================================
# PHONEME DATA v3
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
    'AO': {
        'dur': 130, 'voiced': True,
        'F': [570, 840, 2410, 3300],
        'B': [ 80,  80,  160,  250],
    },

    # ---- NASALS ----
    # FIX 5: hard gate at release
    'M': {
        'dur': 85, 'voiced': True,
        'F': [250,  700, 2200, 3300],
        'B': [ 60,  120,  250,  350],
        'nasal': True,
        'antiformant': 1000,
        'anti_bw': 300,
        'anti_depth': 0.50,
        'amp_scale': 0.52,
        'hard_gate_ms': 14,
    },
    'N': {
        'dur': 80, 'voiced': True,
        'F': [250,  900, 2200, 3300],
        'B': [ 60,  120,  250,  350],
        'nasal': True,
        'antiformant': 1500,
        'anti_bw': 350,
        'anti_depth': 0.48,
        'amp_scale': 0.50,
        'hard_gate_ms': 12,
    },
    'NG': {
        'dur': 90, 'voiced': True,
        'F': [250,  700, 2200, 3300],
        'B': [ 60,  120,  250,  350],
        'nasal': True,
        'antiformant': 2000,
        'anti_bw': 400,
        'anti_depth': 0.48,
        'amp_scale': 0.52,
        'hard_gate_ms': 14,
    },

    # ---- FRICATIVES ----
    # FIX 4: Z narrower band, more voicing
    'S': {
        'dur': 100, 'voiced': False,
        'noise_only': True,
        'noise_bands': [(4000, 10000, 1.0)],
        'F': [6000, 8000, 10000, 11000],
        'B': [500, 500, 500, 500],
    },
    'Z': {
        'dur': 95, 'voiced': True,
        # FIX: narrow noise band
        # heavy voicing underneath
        'noise_bands': [(3500, 8000, 0.55)],
        'voice_frac': 0.70,   # 70% voicing
        'noise_frac': 0.30,   # 30% noise
        'F': [250,  900, 2200, 3300],
        'B': [100,  130,  220,  320],
    },
    'SH': {
        'dur': 105, 'voiced': False,
        'noise_only': True,
        'noise_bands': [(1800, 7000, 1.0)],
        'F': [6000, 8000, 10000, 11000],
        'B': [500, 500, 500, 500],
    },
    'ZH': {
        'dur': 95, 'voiced': True,
        'noise_bands': [(1500, 6500, 0.50)],
        'voice_frac': 0.65,
        'noise_frac': 0.35,
        'F': [250,  900, 2200, 3300],
        'B': [100,  130,  220,  320],
    },
    'F': {
        'dur': 90, 'voiced': False,
        'noise_only': True,
        'noise_bands': [(1000, 10000, 0.7),
                         (4000, 12000, 0.4)],
        'F': [6000, 8000, 10000, 11000],
        'B': [500, 500, 500, 500],
    },
    'V': {
        'dur': 85, 'voiced': True,
        'noise_bands': [(800, 7000, 0.50)],
        'voice_frac': 0.65,
        'noise_frac': 0.35,
        'F': [250,  900, 2200, 3300],
        'B': [100,  130,  220,  320],
    },
    'TH': {
        'dur': 90, 'voiced': False,
        'noise_only': True,
        'noise_bands': [(1000, 7000, 0.75)],
        'F': [6000, 8000, 10000, 11000],
        'B': [500, 500, 500, 500],
    },
    'DH': {
        'dur': 80, 'voiced': True,
        'noise_bands': [(800, 5500, 0.42)],
        'voice_frac': 0.68,
        'noise_frac': 0.32,
        'F': [250,  900, 2200, 3300],
        'B': [100,  130,  220,  320],
    },
    # FIX 2: H bypasses formant bank
    # pure broadband noise shaped by
    # following vowel — handled in code
    'H': {
        'dur': 70, 'voiced': False,
        'h_phoneme': True,
        # No F/B needed — overridden
        'F': [500, 1500, 2500, 3500],
        'B': [200,  220,  320,  420],
    },

    # ---- PLOSIVES ----
    # FIX 3: burst 2-3ms only
    # FIX 6: closure pre-warms filter
    'P': {
        'dur': 90, 'voiced': False,
        'plosive': True,
        'closure_ms': 55,
        'burst_ms':    2,     # FIX: 2ms only
        'vot_ms':     62,
        'place': 'bilabial',
        'burst_amp':  0.38,
        'burst_hp':    500,
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
        'burst_amp':  0.25,
        'burst_hp':    300,
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
        'burst_amp':  0.42,
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
        'burst_amp':  0.26,
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
        'burst_amp':  0.40,
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
        'burst_amp':  0.24,
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
    'already': ['AA', 'L',  'R',  'EH',
                'D',  'IY', 'SIL'],
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
    'solid':   ['S',  'AA', 'L',  'IH',
                'D',  'SIL'],
    'landing': ['L',  'AE', 'N',  'D',
                'IH', 'NG', 'SIL'],
    'wrong':   ['R',  'AO', 'NG', 'SIL'],
    'both':    ['B',  'OH', 'TH', 'SIL'],
    'always':  ['AA', 'L',  'W',  'EH',
                'Z',  'SIL'],
}


# ============================================================
# GLOTTAL SOURCE
# ============================================================

def glottal_source(pitch_hz, dur_s,
                    jitter=0.005,
                    shimmer=0.030,
                    sr=SR):
    n_s = int(dur_s * sr)
    if n_s < 2:
        return f32(np.zeros(2))
    t   = np.arange(n_s, dtype=DTYPE)/sr

    vib_onset = min(0.08, dur_s*0.3)
    vib_env   = f32(np.clip(
        (t-vib_onset)/0.06, 0, 1))
    freq_t    = pitch_hz*(
        1 + 0.007*vib_env*np.sin(
            2*np.pi*5.0*t))

    phase = np.zeros(n_s, dtype=DTYPE)
    p     = 0.0
    for i in range(n_s):
        jit  = 1 + np.random.normal(
            0, jitter)
        p   += float(freq_t[i])*jit/sr
        if p >= 1.0: p -= 1.0
        phase[i] = p

    oq     = 0.65
    src    = np.where(
        phase < oq,
        (phase/oq)*(2-phase/oq),
        1-(phase-oq)/(1-oq+1e-9))
    src    = f32(np.diff(
        src, prepend=src[0]))

    shim = f32(np.random.normal(0,1,n_s))
    try:
        b,a  = safe_lp(25, sr)
        shim = f32(lfilter(b,a,shim))
    except:
        pass
    shim = f32(np.clip(1+shimmer*shim,
                        0.4, 1.6))
    src  = src*shim

    asp  = f32(np.random.normal(0,0.025,n_s))
    try:
        b,a = safe_bp(400, 2200, sr)
        asp = f32(lfilter(b,a,asp))
    except:
        asp = f32(np.zeros(n_s))

    return src + asp


def shaped_noise(dur_s, bands, sr=SR):
    """
    Generate noise shaped by multiple
    bandpass filters, summed.
    bands: list of (lo, hi, gain)
    """
    n_s    = int(dur_s*sr)
    if n_s < 2:
        return f32(np.zeros(2))
    noise  = f32(np.random.normal(0,1,n_s))
    result = np.zeros(n_s, dtype=DTYPE)
    for lo,hi,g in bands:
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
# BUILD FORMANT ARRAYS
# ============================================================

def build_f_arrays(F_tgt, B_tgt,
                    F_from, F_to,
                    n_s, diphthong=False):
    """
    3-zone coarticulated formant arrays.
    FIX: onset zone reduced to 20%
    (less coarticulation = cleaner onset).
    """
    F_end = F_tgt  # default

    n_on  = int(0.20*n_s)
    n_off = int(0.20*n_s)
    n_mid = n_s - n_on - n_off

    F_arrs = []
    B_arrs = []

    for fi in range(4):
        arr = np.zeros(n_s, dtype=DTYPE)

        # Onset transition
        if n_on > 0:
            arr[:n_on] = np.linspace(
                F_from[fi], F_tgt[fi],
                n_on, dtype=DTYPE)

        # Mid (steady or diphthong)
        if n_mid > 0:
            if diphthong:
                F_diph = F_tgt  # start
                # get F_end from caller
                # — passed as F_to override
                n_move = int(n_mid*0.72)
                n_hold = n_mid - n_move
                if n_move > 0:
                    arr[n_on:n_on+n_move] = \
                        np.linspace(
                            F_tgt[fi],
                            F_to[fi],
                            n_move,
                            dtype=DTYPE)
                if n_hold > 0:
                    arr[n_on+n_move:
                        n_on+n_mid] = \
                        float(F_to[fi])
            else:
                arr[n_on:n_on+n_mid] = \
                    float(F_tgt[fi])

        # Offset transition
        if n_off > 0:
            f_off_start = (
                float(F_to[fi])
                if diphthong
                else float(F_tgt[fi]))
            arr[n_on+n_mid:] = np.linspace(
                f_off_start,
                F_to[fi],
                n_off, dtype=DTYPE)

        F_arrs.append(arr)
        B_arrs.append(f32(np.full(
            n_s, float(B_tgt[fi]))))

    return F_arrs, B_arrs


# ============================================================
# PHONEME SYNTHESIS v3
# ============================================================

def synth_phoneme(phon, pitch_hz,
                   dur_ms=None,
                   prev_phon=None,
                   next_phon=None,
                   sr=SR):

    data = PHONEMES.get(phon)
    if data is None:
        n = int((dur_ms or 50)/1000*sr)
        return f32(np.zeros(max(n,2)))

    d_ms  = dur_ms if dur_ms is not None \
            else data['dur']
    dur_s = d_ms/1000.0
    n_s   = max(4, int(dur_s*sr))

    # ---- SILENCE ----
    if phon == 'SIL':
        return f32(np.zeros(n_s))

    # ---- PLOSIVE ----
    if data.get('plosive', False):
        return synth_plosive(
            phon, data, pitch_hz,
            prev_phon, next_phon, sr)

    # ---- FIX 2: H — pure shaped noise ----
    if data.get('h_phoneme', False):
        return synth_h(
            data, pitch_hz, dur_s,
            next_phon, sr)

    # ---- NOISE-ONLY FRICATIVES ----
    if data.get('noise_only', False):
        return synth_fricative_unvoiced(
            data, dur_s, sr)

    # ---- VOICED FRICATIVES ----
    if 'voice_frac' in data:
        return synth_fricative_voiced(
            data, pitch_hz, dur_s,
            prev_phon, next_phon, sr)

    # ---- VOWELS, NASALS, APPROXIMANTS ----
    return synth_sonorant(
        phon, data, pitch_hz, dur_s,
        prev_phon, next_phon, sr)


# ============================================================
# H SYNTHESIS — FIX 2
# Pure noise, shaped by following vowel
# ============================================================

def synth_h(data, pitch_hz, dur_s,
             next_phon, sr=SR):
    n_s = max(4, int(dur_s*sr))

    # Get following vowel formants
    if next_phon and next_phon in PHONEMES:
        nxt   = PHONEMES[next_phon]
        F_use = nxt['F']
        # Wide bandwidth — breathy
        B_use = [min(bw*3.5, 550)
                 for bw in nxt['B']]
    else:
        F_use = [500, 1500, 2500, 3500]
        B_use = [200,  220,  350,  450]

    # Pure noise source
    noise = f32(np.random.normal(0,1,n_s))

    # Shape noise directly through
    # bandpass filters — NO resonator bank
    # (avoids initialization transient)
    result = np.zeros(n_s, dtype=DTYPE)
    gains  = [0.50, 0.70, 0.40, 0.20]
    for fi in range(4):
        fc  = float(F_use[fi])
        bw  = float(B_use[fi])
        lo  = max(60,  fc - bw*1.5)
        hi  = min(sr*0.48, fc + bw*1.5)
        try:
            b,a = safe_bp(lo, hi, sr)
            result += f32(
                lfilter(b,a,noise)
            ) * gains[fi]
        except:
            pass

    # Envelope: slow rise (breath onset)
    # no ring possible — just noise
    atk_n = int(min(0.025, dur_s*0.3)*sr)
    rel_n = int(min(0.020, dur_s*0.2)*sr)
    env   = f32(np.ones(n_s))
    if atk_n > 0:
        env[:atk_n] = f32(
            np.linspace(0,1,atk_n)**0.5)
    if rel_n > 0:
        env[-rel_n:] = f32(
            np.linspace(1,0,rel_n))

    result = result*env
    mx = np.max(np.abs(result))
    if mx > 0: result /= mx
    return result * 0.72


# ============================================================
# UNVOICED FRICATIVE SYNTHESIS
# ============================================================

def synth_fricative_unvoiced(data,
                               dur_s, sr=SR):
    n_s    = max(4, int(dur_s*sr))
    bands  = data.get('noise_bands', [])
    result = shaped_noise(dur_s, bands, sr)
    result = f32(result[:n_s])

    atk_n = int(min(0.006, dur_s*0.1)*sr)
    rel_n = int(min(0.008, dur_s*0.1)*sr)
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
    return result


# ============================================================
# VOICED FRICATIVE SYNTHESIS
# FIX 4: proper voicing + narrow noise
# ============================================================

def synth_fricative_voiced(data,
                            pitch_hz,
                            dur_s,
                            prev_phon,
                            next_phon,
                            sr=SR):
    n_s = max(4, int(dur_s*sr))

    F_tgt = data['F']
    B_tgt = data['B']
    F_prev = (PHONEMES[prev_phon]['F']
              if prev_phon and
              prev_phon in PHONEMES
              else F_tgt)
    F_next = (PHONEMES[next_phon]['F']
              if next_phon and
              next_phon in PHONEMES
              else F_tgt)

    F_arrs, B_arrs = build_f_arrays(
        F_tgt, B_tgt,
        F_prev, F_next, n_s,
        diphthong=False)

    # Voiced excitation (full amplitude)
    exc    = glottal_source(
        pitch_hz, dur_s,
        jitter=0.005,
        shimmer=0.030, sr=sr)
    exc    = f32(exc[:n_s])

    gains  = [0.55, 0.75, 0.45, 0.25]
    voiced = formant_bank_warmed(
        exc, F_arrs, B_arrs, gains,
        warm_ms=8.0, sr=sr)

    # Noise component — narrow band
    bands  = data.get('noise_bands', [])
    noise  = shaped_noise(dur_s, bands, sr)
    noise  = f32(noise[:n_s])

    vf = data.get('voice_frac', 0.70)
    nf = data.get('noise_frac',  0.30)
    result = voiced*vf + noise*nf

    # Envelope
    atk_n = int(min(0.020, dur_s*0.25)*sr)
    rel_n = int(min(0.015, dur_s*0.20)*sr)
    env   = f32(np.ones(n_s))
    if atk_n > 0:
        env[:atk_n] = f32(
            np.linspace(0,1,atk_n)**0.5)
    if rel_n > 0:
        env[-rel_n:] = f32(
            np.linspace(1,0,rel_n))
    result = result*env
    mx = np.max(np.abs(result))
    if mx > 0: result /= mx
    return result


# ============================================================
# SONORANT SYNTHESIS
# (vowels, nasals, approximants)
# FIX 1: warmed resonators
# FIX 5: nasal hard gate
# ============================================================

def synth_sonorant(phon, data, pitch_hz,
                    dur_s, prev_phon,
                    next_phon, sr=SR):
    n_s = max(4, int(dur_s*sr))

    F_tgt  = data['F']
    B_tgt  = data['B']
    is_diph = data.get('diphthong', False)
    F_diph_end = data.get('F_end', F_tgt)

    F_prev = (PHONEMES[prev_phon]['F']
              if prev_phon and
              prev_phon in PHONEMES
              else F_tgt)
    F_next = (PHONEMES[next_phon]['F']
              if next_phon and
              next_phon in PHONEMES
              else F_diph_end)

    F_arrs, B_arrs = build_f_arrays(
        F_tgt, B_tgt,
        F_prev,
        F_diph_end if is_diph else F_next,
        n_s,
        diphthong=is_diph)

    # FIX: R fast F3 drop in first 30ms
    if data.get('r_fast_f3', False):
        f3_arr   = F_arrs[2].copy()
        n_drop   = min(int(0.030*sr), n_s)
        f3_start = float(
            F_prev[2] if F_prev else 2500)
        f3_arr[:n_drop] = np.linspace(
            f3_start, 1690.0,
            n_drop, dtype=DTYPE)
        f3_arr[n_drop:] = 1690.0
        F_arrs[2] = f3_arr

    # Excitation
    exc    = glottal_source(
        pitch_hz, dur_s,
        jitter=0.005,
        shimmer=0.030, sr=sr)
    exc    = f32(exc[:n_s])

    gains  = [0.55, 0.75, 0.45, 0.25]

    # FIX 1: warmed resonator bank
    result = formant_bank_warmed(
        exc, F_arrs, B_arrs, gains,
        warm_ms=8.0, sr=sr)

    # Nasal processing
    if data.get('nasal', False):
        af    = data.get('antiformant',1000)
        af_bw = data.get('anti_bw', 300)
        depth = data.get('anti_depth', 0.50)
        anti_out, _, _ = resonator_with_state(
            result, af, af_bw, sr=sr)
        result = result - anti_out*depth
        result *= data.get('amp_scale', 0.52)

    # Envelope
    atk_ms = {'M':18,'N':16,'NG':18,
               'L':12,'R':12,'W':18,
               'Y':12}.get(phon, 22)
    rel_ms = {'M':15,'N':14,'NG':15,
               'L':14,'R':14}.get(phon, 24)

    atk_n = min(int(atk_ms/1000*sr),n_s//3)
    rel_n = min(int(rel_ms/1000*sr),n_s//3)
    env   = f32(np.ones(n_s))
    if atk_n > 0:
        env[:atk_n] = f32(
            np.linspace(0,1,atk_n)**0.45)
    if rel_n > 0:
        env[-rel_n:] = f32(
            np.linspace(1,0,rel_n)**0.5)

    result = result*env

    # FIX 5: nasal hard gate
    # Zero out last N ms completely
    if data.get('nasal', False):
        hg_ms = data.get('hard_gate_ms', 12)
        hg_n  = min(int(hg_ms/1000*sr),
                     n_s//4)
        if hg_n > 0:
            result[-hg_n:] = 0.0

    mx = np.max(np.abs(result))
    if mx > 0: result /= mx
    return result


# ============================================================
# PLOSIVE SYNTHESIS v3
# FIX 3: 2ms burst
# FIX 6: closure pre-warms filter
# ============================================================

def synth_plosive(phon, data, pitch_hz,
                   prev_phon, next_phon,
                   sr=SR):

    closure_ms = data.get('closure_ms', 45)
    burst_ms   = data.get('burst_ms',   2)
    vot_ms     = data.get('vot_ms',    60)
    voiced     = data.get('voiced',  False)
    burst_amp  = data.get('burst_amp', 0.38)
    burst_hp   = data.get('burst_hp', 1500)

    n_clos  = int(closure_ms/1000*sr)
    n_burst = int(burst_ms/1000*sr)
    n_vot   = int(vot_ms/1000*sr)
    n_trans = int(0.042*sr)

    total   = n_clos+n_burst+n_vot+n_trans
    result  = np.zeros(total, dtype=DTYPE)

    # Get following vowel data
    nxt_data = (PHONEMES.get(next_phon)
                if next_phon else None)
    nxt_F = (nxt_data['F']
             if nxt_data
             else [500,1500,2500,3500])
    nxt_B = (nxt_data['B']
             if nxt_data
             else [200, 200, 300, 400])

    # FIX 6: pre-warm resonators
    # during closure silence
    # (no audio, just charges filter)
    # — state used in trans section below
    warm_states = []
    for fi in range(4):
        y1, y2 = warm_up_resonator(
            nxt_F[fi], nxt_B[fi],
            warm_ms=(closure_ms+
                     burst_ms+vot_ms),
            sr=sr)
        warm_states.append((y1, y2))

    # Burst — FIX 3: very short, quieter
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
        bs = n_clos
        result[bs:bs+n_burst] = \
            burst*b_env*burst_amp

    # VOT / aspiration
    # FIX: shaped by following vowel formants
    if n_vot > 0:
        if not voiced:
            asp  = f32(
                np.random.normal(0,1,n_vot))
            asp_r = np.zeros(
                n_vot, dtype=DTYPE)
            asp_g = [0.45,0.65,0.35,0.18]
            # Shape through following vowel
            # (wide BW = breathy)
            for fi in range(4):
                fc = float(nxt_F[fi])
                bw = float(nxt_B[fi])*2.8
                lo = max(60,  fc-bw*1.2)
                hi = min(sr*0.48, fc+bw*1.2)
                try:
                    b,a  = safe_bp(lo,hi,sr)
                    asp_r += f32(
                        lfilter(b,a,asp)
                    )*asp_g[fi]
                except:
                    pass
            asp_env = f32(np.linspace(
                0.55, 0.04, n_vot))
            vs = n_clos+n_burst
            result[vs:vs+n_vot] += \
                asp_r*asp_env*0.50
        else:
            # Voiced: quiet voicing from start
            pv  = glottal_source(
                pitch_hz, n_vot/sr,
                jitter=0.012,
                shimmer=0.08, sr=sr)
            pve = f32(np.linspace(
                0.04, 0.50, n_vot))
            vs  = n_clos+n_burst
            result[vs:vs+n_vot] += \
                pv[:n_vot]*pve

    # Formant transition into vowel
    # Uses pre-warmed filter state
    if n_trans > 0 and nxt_data:
        place = data.get('place','alveolar')
        F2_LOCUS = {
            'bilabial':  720,
            'alveolar': 1800,
            'velar':    3000,
        }
        locus = F2_LOCUS.get(place, 1800)

        F_trans_start = [
            400,           # F1 neutral
            locus,         # F2 locus (key)
            nxt_F[2],      # F3 at target
            nxt_F[3],      # F4 at target
        ]

        v_trans = glottal_source(
            pitch_hz, n_trans/sr,
            jitter=0.005,
            shimmer=0.025, sr=sr)

        trans_r = np.zeros(
            n_trans, dtype=DTYPE)
        tg      = [0.55,0.75,0.45,0.25]

        for fi in range(4):
            f_arr = f32(np.linspace(
                F_trans_start[fi],
                nxt_F[fi], n_trans))
            y1,y2 = warm_states[fi]
            for blk_s in range(
                    0, n_trans, 128):
                blk_e = min(
                    blk_s+128, n_trans)
                seg   = v_trans[blk_s:blk_e]
                fc_   = float(np.mean(
                    f_arr[blk_s:blk_e]))
                bw_   = float(nxt_B[fi])
                out,y1,y2 = \
                    resonator_with_state(
                        seg, fc_, bw_,
                        y1_in=y1,
                        y2_in=y2, sr=sr)
                trans_r[blk_s:blk_e] += \
                    out*tg[fi]

        t_env = f32(np.linspace(
            0.12, 0.92, n_trans))
        ts    = n_clos+n_burst+n_vot
        result[ts:ts+n_trans] += \
            trans_r*t_env

    mx = np.max(np.abs(result))
    if mx > 0: result /= mx
    return f32(result)


# ============================================================
# WORD + PHRASE
# ============================================================

def synth_word(word, pitch_hz=175,
               tempo_scale=1.0,
               sr=SR):
    phonemes = WORDS.get(word.lower())
    if phonemes is None:
        print(f"  '{word}' not in dict")
        return f32(np.zeros(int(0.1*sr)))

    segs = []
    for i, ph in enumerate(phonemes):
        prev_p = phonemes[i-1] if i>0 \
                 else None
        next_p = phonemes[i+1] \
                 if i<len(phonemes)-1 \
                 else None
        d_ms = PHONEMES.get(
            ph,{}).get('dur',80)
        d_ms /= tempo_scale
        seg  = synth_phoneme(
            ph, pitch_hz,
            dur_ms=d_ms,
            prev_phon=prev_p,
            next_phon=next_p, sr=sr)
        segs.append(f32(seg))

    if not segs:
        return f32(np.zeros(int(0.1*sr)))

    fade_n  = int(0.006*sr)
    total_n = sum(len(s) for s in segs)
    result  = f32(np.zeros(total_n))
    pos     = 0
    for si,seg in enumerate(segs):
        n   = len(seg)
        end = min(pos+n, total_n)
        sn  = end-pos
        if si>0 and fade_n>0 and sn>fade_n:
            fi  = f32(np.linspace(
                0,1,min(fade_n,sn)))
            sc  = seg[:sn].copy()
            sc[:len(fi)] *= fi
            result[pos:end] += sc
        else:
            result[pos:end] += seg[:sn]
        pos += n

    mx = np.max(np.abs(result))
    if mx > 0: result /= mx
    return result


def synth_phrase(word_list,
                  pitch_base=175,
                  sr=SR):
    segs = []
    nw   = len(word_list)
    for wi,word in enumerate(word_list):
        prog  = wi/max(nw-1,1)
        pitch = pitch_base*(1-0.08*prog)
        tempo = 1.0+0.06*float(
            np.random.uniform(-1,1))
        seg   = synth_word(
            word, pitch_hz=pitch,
            tempo_scale=tempo, sr=sr)
        segs.append(f32(seg))
        if wi < nw-1:
            segs.append(f32(
                np.zeros(int(0.082*sr))))
    result = f32(np.concatenate(segs))
    n   = len(result)
    env = f32(np.ones(n))
    atk = int(0.018*sr)
    rel = int(0.050*sr)
    if atk>0 and atk<n:
        env[:atk]=f32(np.linspace(0,1,atk))
    if rel>0:
        env[-rel:]=f32(np.linspace(1,0,rel))
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
    print("VOCAL WORDS v3")
    print("="*60)
    print()
    print("  ROOT CAUSE: IIR resonator")
    print("  initialization transient.")
    print("  The (k+ch) artifact.")
    print()
    print("  FIX: warm-up resonators")
    print("  before each phoneme.")
    print("  The filter starts warm —")
    print("  no click, no chirp.")
    print()

    pitch = 175.0

    # ---- PHONEME TEST 6x ----
    print("  Writing phoneme groups (6x)...")

    GROUPS = [
        ("vowels",
         ['AA','AE','AH','EH','ER',
          'IH','IY','OH','UH','UW']),
        ("diphthongs",
         ['AW','AY','OW','OY']),
        ("nasals",
         ['M','N','NG']),
        ("fricatives_unvoiced",
         ['S','SH','F','TH','H']),
        ("fricatives_voiced",
         ['Z','ZH','V','DH']),
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
            seg  = synth_phoneme(
                ph, pitch,
                dur_ms=dil,
                prev_phon='AA',
                next_phon='AA',
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
    targets = ['here','home','water',
                'still','open','always',
                'both','now','voice',
                'matter','landing','state']

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
    print("  Writing words 0.55x tempo...")
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
        ['both'],
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
        dur = len(seg)/SR
        print(f"    '{' '.join(pw)}' "
              f"({dur:.2f}s)")

    print()
    print("="*60)
    print()
    print("  Listen in order:")
    print()
    print("  1. Phoneme groups (6x)")
    print("     Listen for: NO (k+ch) artifact")
    print("     H: breathy, not clicking")
    print("     S: hiss only, no click")
    print("     Z: buzzy not static")
    print("     M,N: quiet, clean cutoff")
    print()
    for g,_ in GROUPS:
        print(f"     afplay output_words/"
              f"phon_{g}_6x.wav")
    print()
    print("  2. Slow words")
    for w in targets[:6]:
        print(f"     afplay output_words/"
              f"{w}_slow.wav")
    print()
    print("  3. Normal words")
    for w in targets[:6]:
        print(f"     afplay output_words/"
              f"{w}.wav")
    print()
    print("  The (k+ch) should be gone.")
    print("  If it is: the root cause")
    print("  is fixed and we iterate")
    print("  from there.")
    print("  If it remains: tell me")
    print("  which phoneme group still")
    print("  has it and I will isolate")
    print("  further.")
    print()
