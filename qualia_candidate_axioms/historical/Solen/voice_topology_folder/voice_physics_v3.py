"""
VOICE PHYSICS v7
February 2026

THE SUPRASEGMENTAL LAYER.

v6 gave us the segmental layer:
  continuous formant trajectory
  correct phoneme geometries
  one tract, never resets

v7 adds what was missing:
  INTONATION — the shape of F0
               across the phrase
  STRESS      — duration and amplitude
               vary with syllable weight
  BANDWIDTH   — the flesh of the voice
               varies with voice quality
  PRESSURE    — open quotient varies
               with stress and position
  SYNTAX      — rest duration from
               syntactic bond strength

The segmental layer said WHAT.
The suprasegmental layer says HOW.
The HOW is more important
than the WHAT.
"""

from tonnetz_engine import (SR, RoomReverb)
import numpy as np
import wave as wave_module
import os
from scipy.signal import butter, lfilter

DTYPE = np.float32
PITCH = 175.0
DIL   = 6.0

def f32(x):
    return np.asarray(x, dtype=DTYPE)

def sil(dur_s, sr=SR):
    return f32(np.zeros(int(dur_s*sr)))

def write_wav(path, sig, sr=SR):
    sig = f32(sig)
    mx  = np.max(np.abs(sig))
    if mx > 0: sig = sig/mx*0.88
    with wave_module.open(path,'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(
            (sig*32767).astype(
                np.int16).tobytes())

def apply_room(sig, rt60=1.5, dr=0.50,
               sr=SR):
    rev = RoomReverb(rt60=rt60, sr=sr,
                     direct_ratio=dr)
    return f32(rev.process(sig))

def safe_bp(lo, hi, sr=SR):
    nyq = sr/2.0
    l   = max(lo/nyq, 0.001)
    h   = min(hi/nyq, 0.499)
    if l >= h: l = h*0.5
    return butter(2, [l,h], btype='band')

def safe_lp(fc, sr=SR):
    return butter(2,
        min(float(fc)/(sr/2), 0.499),
        btype='low')

def safe_hp(fc, sr=SR):
    return butter(2,
        min(float(fc)/(sr/2), 0.499),
        btype='high')

def scalar(x):
    a = np.asarray(x, dtype=DTYPE)
    return float(a.flat[0])


# ============================================================
# SUPRASEGMENTAL DATA
# The HOW layer.
# ============================================================

# English lexical stress.
# Format: word → list of stress values
# per syllable.
# 2 = primary stress
# 1 = secondary stress
# 0 = unstressed
STRESS_DICT = {
    # monosyllables — context determines
    # stress. Default: content=1,
    # function=0
    'the':      [0],
    'a':        [0],
    'an':       [0],
    'of':       [0],
    'to':       [0],
    'and':      [0],
    'in':       [0],
    'is':       [0],
    'was':      [0],
    'it':       [0],
    'i':        [1],
    'am':       [1],
    'here':     [2],
    'home':     [2],
    'now':      [2],
    'still':    [2],
    'both':     [2],
    'not':      [2],
    'yet':      [2],
    'where':    [2],
    'find':     [2],
    'been':     [2],
    'wrong':    [2],
    # bisyllabic
    'voice':    [2],
    'water':    [2, 0],
    'open':     [2, 0],
    'always':   [2, 0],
    'matter':   [2, 0],
    'landing':  [2, 0],
    'solid':    [2, 0],
    'named':    [2, 0],
    'state':    [2],
    # trisyllabic
    'already':  [0, 2, 0],
    'always':   [2, 0],
    'never':    [2, 0],
}

# Syllable → phoneme mapping
# (which phonemes carry the vowel
#  nucleus = which phoneme gets
#  the stress duration scaling)
WORD_SYLLABLES = {
    'the':      [['DH','AH']],
    'voice':    [['V','OY','S']],
    'was':      [['W','AH','Z']],
    'already':  [['AA'],
                  ['L','R','EH'],
                  ['D','IY']],
    'here':     [['H','IH','R']],
    'home':     [['H','OW','M']],
    'water':    [['W','AA','T'],
                  ['ER']],
    'still':    [['S','T','IH','L']],
    'open':     [['OH','P'],
                  ['EH','N']],
    'always':   [['AA','L'],
                  ['W','EH','Z']],
    'both':     [['B','OH','TH']],
    'now':      [['N','AW']],
    'matter':   [['M','AE','T'],
                  ['ER']],
    'not':      [['N','AA','T']],
    'yet':      [['Y','EH','T']],
    'where':    [['W','EH','R']],
    'landing':  [['L','AE','N'],
                  ['D','IH','NG']],
    'find':     [['F','AY','N','D']],
    'state':    [['S','T','EH','T']],
    'wrong':    [['R','AO','NG']],
    'been':     [['B','IH','N']],
    'named':    [['N','EH','M','D']],
    'i':        [['AY']],
    'am':       [['AH','M']],
    'solid':    [['S','AA'],
                  ['L','IH','D']],
}

# Duration multipliers by stress level
DUR_SCALE = {
    2: 1.40,   # primary stress: longer
    1: 1.10,   # secondary: slightly longer
    0: 0.72,   # unstressed: compressed
}

# Amplitude multipliers by stress level
AMP_SCALE = {
    2: 1.20,
    1: 1.05,
    0: 0.78,
}

# Open quotient by stress + position
# Lower oq = more abrupt closure
# = richer harmonics = more pressed
OQ_SCALE = {
    2: 0.58,   # stressed: more pressed
    1: 0.63,
    0: 0.68,   # unstressed: more open
}

# Syntactic bond strength between
# word pairs.
# Lower = tighter bond = shorter rest.
# Scale: 0.0 (no rest) to 1.0 (full rest)
SYNTACTIC_BONDS = {
    # Determiner + noun: very tight
    ('the', 'voice'):   0.20,
    ('the', 'water'):   0.20,
    ('the', 'state'):   0.20,
    ('a',   'voice'):   0.20,
    # Adjective + noun: tight
    ('still', 'water'): 0.35,
    ('both',  'here'):  0.45,
    # Subject + verb: moderate
    ('voice', 'was'):   0.65,
    ('i',     'am'):    0.60,
    # Verb + adverb/complement: moderate
    ('was', 'already'): 0.55,
    ('was', 'here'):    0.55,
    # Adverb + location: moderate
    ('already', 'here'):0.60,
    ('always',  'here'):0.60,
    ('always',  'open'):0.55,
    ('always',  'home'):0.55,
    # Default
    'default':          0.80,
}

# Sentence types → intonation contour
# functions over normalized time [0,1]
# Returns F0 multiplier
def contour_statement(t):
    """
    Falling contour.
    High start, low finish.
    English declarative.
    """
    return 1.08 - 0.22*t

def contour_question(t):
    """
    Rising contour.
    Low-ish start, rises at end.
    """
    return 0.96 + 0.28*(t**1.8)

def contour_exclaim(t):
    """
    Rise to peak then decisive land.
    Energy builds, arrives, lands.
    """
    if t < 0.65:
        return 0.98 + 0.24*(t/0.65)
    else:
        return 1.22 - 0.18*((t-0.65)/0.35)

def contour_flat(t):
    return 1.0

CONTOURS = {
    '.':   contour_statement,
    '?':   contour_question,
    '!':   contour_exclaim,
    '...': lambda t: 0.98 - 0.12*t,
    ',':   lambda t: 1.02 - 0.06*t,
    'default': contour_statement,
}

# Boundary tones at phrase end
# F0 multiplier applied to
# final 20% of phrase
BOUNDARY_TONE = {
    '.':   ('fall',  0.82),
    '?':   ('rise',  1.28),
    '!':   ('level', 1.00),
    '...': ('fall',  0.88),
    ',':   ('rise',  1.06),
    'default': ('fall', 0.88),
}


# ============================================================
# PROSODY PLANNER
# Takes a phrase + punctuation.
# Returns per-phoneme prosody values.
# ============================================================

def plan_prosody(words_phonemes,
                  punctuation='.',
                  pitch_base=PITCH,
                  dil=DIL):
    """
    For each phoneme in the phrase,
    compute:
      - dur_ms (stress-scaled)
      - amp (stress-scaled)
      - f0_mult (intonation contour
                 + local stress peak)
      - oq (open quotient for source)
      - bw_mult (bandwidth multiplier
                 for voice quality)
      - rest_ms (after this word, if any)

    Returns list of phoneme dicts
    in order.
    """
    # Flatten to (word, phoneme, stress)
    flat = []

    for wi, (word, phonemes) in \
            enumerate(words_phonemes):
        syl_map  = WORD_SYLLABLES.get(
            word.lower(), [phonemes])
        stress_p = STRESS_DICT.get(
            word.lower(),
            [1]*len(syl_map))

        # Pad stress list if needed
        while len(stress_p) < len(syl_map):
            stress_p.append(0)

        for si, syl in enumerate(syl_map):
            sv = stress_p[si] \
                 if si < len(stress_p) \
                 else 0
            for ph in syl:
                flat.append({
                    'word':    word,
                    'word_idx':wi,
                    'ph':      ph,
                    'stress':  sv,
                })

    if not flat:
        return []

    n_total   = len(flat)
    contour_fn = CONTOURS.get(
        punctuation,
        CONTOURS['default'])
    bt_type, bt_val = BOUNDARY_TONE.get(
        punctuation,
        BOUNDARY_TONE['default'])

    # Compute total duration for
    # contour timing
    from voice_physics_v2 import (
        PHON_DUR_BASE
    )

    # First pass: assign base durations
    for i, item in enumerate(flat):
        ph  = item['ph']
        sv  = item['stress']
        d   = PHON_DUR_BASE.get(ph, 80)
        d  *= DUR_SCALE.get(sv, 1.0)
        d  *= dil
        item['dur_ms'] = d

    total_dur = sum(
        f['dur_ms'] for f in flat)

    # Second pass: assign F0, amp,
    # oq, bw_mult
    t_pos = 0.0
    for i, item in enumerate(flat):
        ph  = item['ph']
        sv  = item['stress']
        dur = item['dur_ms']
        t   = t_pos / max(total_dur, 1.0)
        t_mid = (t_pos + dur/2) / \
                max(total_dur, 1.0)

        # Global contour
        f0_global = contour_fn(t_mid)

        # Local stress peak
        # stressed syllables get
        # a small F0 boost
        f0_local = 1.0
        if sv == 2:
            f0_local = 1.08
        elif sv == 1:
            f0_local = 1.03

        # Boundary tone: apply to
        # final 20% of phrase
        f0_boundary = 1.0
        if t_mid > 0.80:
            bt_progress = (t_mid-0.80)/0.20
            if bt_type == 'fall':
                f0_boundary = 1.0 - \
                    (1.0-bt_val)*bt_progress
            elif bt_type == 'rise':
                f0_boundary = 1.0 + \
                    (bt_val-1.0)*bt_progress
            else:
                f0_boundary = bt_val

        item['f0_mult'] = (f0_global *
                            f0_local *
                            f0_boundary)
        item['amp']     = AMP_SCALE.get(
            sv, 1.0)
        item['oq']      = OQ_SCALE.get(
            sv, 0.65)

        # Bandwidth multiplier:
        # stressed = narrower (more focused)
        # unstressed = wider (more open)
        # phrase end = wider (breathier)
        bw_stress = {2:0.75, 1:0.90,
                      0:1.10}.get(sv, 1.0)
        bw_pos    = 1.0
        if t_mid > 0.85:
            bw_pos = 1.0 + \
                2.0*(t_mid-0.85)/0.15
        item['bw_mult'] = (bw_stress *
                            bw_pos)

        t_pos += dur

    # Third pass: inter-word rests
    word_indices = []
    for i, item in enumerate(flat):
        wi = item['word_idx']
        if not word_indices or \
           word_indices[-1] != wi:
            word_indices.append(wi)

    # Mark last phoneme of each word
    last_ph_of_word = {}
    for i, item in enumerate(flat):
        last_ph_of_word[
            item['word_idx']] = i

    n_words = len(words_phonemes)
    for wi in range(n_words-1):
        last_idx = last_ph_of_word[wi]
        w_this   = words_phonemes[wi][0]\
                   .lower()
        w_next   = words_phonemes[wi+1][0]\
                   .lower()
        bond_key = (w_this, w_next)
        bond     = SYNTACTIC_BONDS.get(
            bond_key,
            SYNTACTIC_BONDS.get(
                (w_next, w_this),
                SYNTACTIC_BONDS['default']))
        # Rest duration: bond strength
        # × base rest
        base_rest_ms = 85.0
        rest_ms = base_rest_ms * bond * dil
        flat[last_idx]['rest_ms'] = rest_ms

    # Ensure all have rest_ms
    for item in flat:
        if 'rest_ms' not in item:
            item['rest_ms'] = 0.0

    return flat


# ============================================================
# VOICED SOURCE WITH VARIABLE OQ
# Subglottal pressure dynamics.
# Open quotient varies per phoneme.
# ============================================================

def source_voiced_oq(pitch_hz, n_s,
                      oq=0.65,
                      jitter=0.005,
                      shimmer=0.030,
                      sr=SR):
    """
    Rosenberg pulse with variable
    open quotient.

    oq controls fold closure:
      low oq (0.50-0.58): more pressed
        abrupt closure, rich harmonics
        stressed syllables
      mid oq (0.63-0.65): modal
        normal speech
      high oq (0.68-0.75): breathy
        phrase ends, H onset,
        unstressed syllables

    This changes the TIMBRE
    not just the amplitude.
    Stressed syllables are spectrally
    richer, not just louder.
    """
    n_s = int(n_s)
    if n_s < 2: return f32(np.zeros(2))
    T   = 1.0/sr
    t   = np.arange(n_s, dtype=DTYPE)/sr

    vib = f32(np.clip(
        (t-0.05)/0.05, 0, 1))
    ft  = pitch_hz*(
        1+0.007*vib*
        np.sin(2*np.pi*5.0*t))

    ph  = np.zeros(n_s, dtype=DTYPE)
    p   = 0.0
    for i in range(n_s):
        p += float(ft[i])*(
            1+np.random.normal(
                0, jitter))/sr
        if p >= 1.0: p -= 1.0
        ph[i] = p

    # Variable oq Rosenberg pulse
    oq_ = max(0.40, min(0.85, float(oq)))
    src = np.where(ph < oq_,
        (ph/oq_)*(2 - ph/oq_),
        1-(ph-oq_)/(1-oq_+1e-9))
    src = f32(np.diff(
        src, prepend=src[0]))

    try:
        b,a = safe_lp(20, sr)
        sh  = f32(np.random.normal(
            0, 1, n_s))
        sh  = f32(lfilter(b,a,sh))
    except:
        sh  = f32(np.ones(n_s))
    sh  = f32(np.clip(
        1+shimmer*sh, 0.4, 1.6))

    # Breath component scales
    # with oq (breathier = more breath)
    breath_amp = 0.015 + \
                 0.025*(oq_-0.55)/0.30
    asp = f32(np.random.normal(
        0, breath_amp, n_s))
    try:
        b,a = safe_bp(400, 2200, sr)
        asp = f32(lfilter(b,a,asp))
    except:
        asp = f32(np.zeros(n_s))

    return src*sh + asp

def source_steady(n_s, sr=SR):
    return f32(np.random.normal(
        0, 1, int(n_s)))


# ============================================================
# TRACT — with bandwidth trajectory
# ============================================================

def warm(fc, bw, n_warm=352, sr=SR):
    fc_ = max(20.0, min(
        float(sr*0.48), scalar(fc)))
    bw_ = max(10.0, scalar(bw))
    T   = 1.0/sr
    a2  = -np.exp(-2*np.pi*bw_*T)
    a1  =  2*np.exp(-np.pi*bw_*T)*\
            np.cos(2*np.pi*fc_*T)
    b0  = 1.0-a1-a2
    y1 = y2 = 0.0
    for _ in range(int(n_warm)):
        y  = b0*np.random.normal(
            0, 0.0004)+a1*y1+a2*y2
        y2=y1; y1=y
    return y1, y2

def resonator(x_arr, f_arr, b_arr,
               y1_in=0.0, y2_in=0.0,
               sr=SR):
    """
    FIX: b_arr is now a TIME-VARYING
    bandwidth array — not a scalar.
    The bandwidth trajectory IS
    the voice quality trajectory.
    """
    n_s = len(x_arr)
    T   = 1.0/sr
    out = np.zeros(n_s, dtype=DTYPE)
    y1  = float(y1_in)
    y2  = float(y2_in)
    for i in range(n_s):
        fc  = max(20.0, min(
            float(sr*0.48),
            float(f_arr[i])))
        bw  = max(10.0, float(b_arr[i]))
        a2  = -np.exp(-2*np.pi*bw*T)
        a1  =  2*np.exp(-np.pi*bw*T)*\
                np.cos(2*np.pi*fc*T)
        b0  = 1.0-a1-a2
        y   = b0*float(x_arr[i])+\
              a1*y1+a2*y2
        y2=y1; y1=y
        out[i]=y
    return out, y1, y2

def tract(source, F_arrays, B_arrays,
           gains, states=None, sr=SR):
    """
    B_arrays: now list of 4 ARRAYS
    (time-varying bandwidth)
    not scalars.
    This carries the voice quality
    trajectory.
    """
    n      = len(source)
    result = np.zeros(n, dtype=DTYPE)
    new_st = []

    for fi in range(4):
        if states is not None:
            y1 = float(states[fi][0])
            y2 = float(states[fi][1])
        else:
            f0_ = float(F_arrays[fi][0])
            b0_ = float(B_arrays[fi][0])
            y1,y2 = warm(f0_, b0_, sr=sr)

        out,y1,y2 = resonator(
            source,
            F_arrays[fi],
            B_arrays[fi],
            y1_in=y1, y2_in=y2, sr=sr)
        result += out*float(gains[fi])
        new_st.append((y1,y2))

    return result, new_st

GAINS = [0.55, 0.75, 0.45, 0.25]


# ============================================================
# VOCAL TOPOLOGY
# ============================================================

VOWEL_F = {
    'AA': ([730,1090,2440,3400],
           [70, 110, 170, 250]),
    'AE': ([660,1720,2410,3300],
           [65, 105, 165, 250]),
    'AH': ([520,1190,2390,3300],
           [70, 110, 170, 250]),
    'AO': ([570, 840,2410,3300],
           [80,  80, 160, 250]),
    'AW': ([730,1090,2440,3400],
           [70,  90, 160, 250],
           [300, 870,2240,3300]),
    'AY': ([730,1090,2440,3400],
           [70, 100, 160, 250],
           [270,2290,3010,3700]),
    'EH': ([530,1840,2480,3500],
           [60, 100, 140, 250]),
    'ER': ([490,1350,1690,3300],
           [70, 110, 170, 250]),
    'IH': ([390,1990,2550,3600],
           [70, 110, 160, 250]),
    'IY': ([270,2290,3010,3700],
           [60,  90, 150, 200]),
    'OH': ([570, 840,2410,3300],
           [80,  80, 160, 250]),
    'OW': ([450, 800,2400,3300],
           [70,  85, 160, 250],
           [300, 870,2240,3300]),
    'OY': ([570, 840,2410,3300],
           [70,  90, 160, 250],
           [270,2290,3010,3700]),
    'UH': ([440,1020,2240,3300],
           [70, 100, 160, 250]),
    'UW': ([300, 870,2240,3300],
           [70,  80, 160, 250]),
}

PHON_DUR_BASE = {
    'AA':140,'AE':130,'AH':100,'AO':130,
    'AW':170,'AY':180,'EH':120,'ER':130,
    'IH':110,'IY':130,'OH':130,'OW':160,
    'OY':180,'UH':110,'UW':130,
    'M':85,'N':80,'NG':90,
    'L':80,'R':90,'W':90,'Y':80,
    'H':70,'DH':80,'V':85,'Z':95,
    'S':100,'SH':105,'F':90,'TH':90,
    'ZH':95,'P':90,'B':80,'T':85,
    'D':75,'K':90,'G':78,
}

def get_f(phon):
    if phon and phon in VOWEL_F:
        return VOWEL_F[phon][0]
    CONS_F = {
        'M': [250, 700,2200,3300],
        'N': [250, 900,2200,3300],
        'NG':[250, 700,2200,3300],
        'L': [360,1000,2400,3300],
        'R': [490,1350,1690,3300],
        'W': [300, 610,2200,3300],
        'Y': [270,2100,3000,3700],
        'DH':[200,1800,2600,3400],
        'V': [250, 900,2200,3300],
        'Z': [250, 900,2200,3300],
        'S': [300,1800,2600,3500],
        'SH':[300, 900,2200,3300],
        'F': [300, 900,2200,3300],
        'TH':[300, 900,2200,3300],
        'H': [500,1500,2500,3500],
    }
    return CONS_F.get(phon,
        [500,1500,2500,3500])

def get_b(phon):
    if phon and phon in VOWEL_F:
        return VOWEL_F[phon][1]
    CONS_B = {
        'M': [60,120,250,350],
        'N': [60,120,250,350],
        'NG':[60,120,250,350],
        'L': [80,160,220,320],
        'R': [80,120,180,260],
        'W': [80, 90,210,310],
        'Y': [65,100,160,220],
        'DH':[100,150,250,350],
        'V': [100,130,220,320],
        'Z': [100,130,220,320],
        'H': [200,220,320,420],
    }
    return CONS_B.get(phon,
        [200,200,300,400])


# ============================================================
# CONTINUOUS TRAJECTORY BUILDER
# Now includes bandwidth trajectory.
# ============================================================

def build_trajectories(phoneme_specs,
                        sr=SR):
    """
    Build continuous F AND B trajectories.

    phoneme_specs: list of dicts with:
      F_tgt, B_tgt (base values)
      bw_mult (voice quality scalar)
      n_s, coart_frac, diphthong,
      F_end, r_f3

    Returns:
      F_full: 4 arrays (formant freqs)
      B_full: 4 arrays (bandwidths)
              time-varying — the flesh
      seg_ends: sample boundary indices
    """
    if not phoneme_specs:
        return ([np.zeros(1,dtype=DTYPE)]*4,
                [np.zeros(1,dtype=DTYPE)]*4,
                [])

    n_total  = sum(s['n_s']
                   for s in phoneme_specs)
    F_full   = [np.zeros(n_total,dtype=DTYPE)
                for _ in range(4)]
    B_full   = [np.zeros(n_total,dtype=DTYPE)
                for _ in range(4)]
    seg_ends = []

    F_current = list(
        phoneme_specs[0]['F_tgt'])
    B_current = list(
        phoneme_specs[0]['B_tgt'])

    pos = 0
    for si, spec in enumerate(
            phoneme_specs):
        n_s     = spec['n_s']
        F_tgt   = spec['F_tgt']
        B_tgt   = spec['B_tgt']
        bw_mult = spec.get('bw_mult', 1.0)
        F_end   = spec.get('F_end', F_tgt)
        is_d    = spec.get(
            'diphthong', False)
        r_f3    = spec.get('r_f3', False)
        cf      = spec.get(
            'coart_frac', 0.20)

        # Next phoneme targets
        if si < len(phoneme_specs)-1:
            F_next = phoneme_specs[
                si+1]['F_tgt']
            B_next = phoneme_specs[
                si+1]['B_tgt']
            bw_next = phoneme_specs[
                si+1].get('bw_mult', 1.0)
        else:
            F_next  = F_end \
                      if is_d else F_tgt
            B_next  = B_tgt
            bw_next = bw_mult

        n_on  = int(cf*n_s)
        n_off = int(cf*n_s)
        n_mid = n_s-n_on-n_off
        if n_mid < 1:
            n_mid=1
            n_on=(n_s-1)//2
            n_off=n_s-1-n_on

        F_from = list(F_current)
        B_from = list(B_current)

        for fi in range(4):
            # Formant frequency array
            f_arr = np.zeros(n_s,
                              dtype=DTYPE)
            if n_on > 0:
                f_arr[:n_on] = np.linspace(
                    float(F_from[fi]),
                    float(F_tgt[fi]),
                    n_on, dtype=DTYPE)
            if n_mid > 0:
                if is_d:
                    nm=int(n_mid*0.72)
                    nh=n_mid-nm
                    if nm>0:
                        f_arr[n_on:
                              n_on+nm]=\
                            np.linspace(
                                float(F_tgt[fi]),
                                float(F_end[fi]),
                                nm,dtype=DTYPE)
                    if nh>0:
                        f_arr[n_on+nm:
                              n_on+n_mid]=\
                            float(F_end[fi])
                else:
                    f_arr[n_on:
                          n_on+n_mid]=\
                        float(F_tgt[fi])
            if n_off > 0:
                ff = (float(F_end[fi])
                      if is_d
                      else float(F_tgt[fi]))
                f_arr[n_on+n_mid:]=\
                    np.linspace(
                        ff,
                        float(F_next[fi]),
                        n_off, dtype=DTYPE)
            if r_f3 and fi==2:
                nd=min(int(0.030*sr),n_s)
                f_arr[:nd]=np.linspace(
                    float(F_from[2]),
                    1690.0,nd,dtype=DTYPE)
                f_arr[nd:]=1690.0

            F_full[fi][pos:pos+n_s] = f_arr

            # Bandwidth array
            # Base B × bw_mult
            # Interpolates smoothly
            # from current to next
            b_base_start = float(B_from[fi])
            b_base_end   = float(
                B_next[fi])*bw_next
            b_arr = np.linspace(
                b_base_start,
                float(B_tgt[fi])*bw_mult,
                n_s, dtype=DTYPE)
            # Apply voice quality
            # variation smoothly
            b_arr = np.clip(
                b_arr, 10.0, 1200.0)
            B_full[fi][pos:pos+n_s] = b_arr

        # Track actual end position
        for fi in range(4):
            F_current[fi] = float(
                F_full[fi][pos+n_s-1])
            B_current[fi] = float(
                B_full[fi][pos+n_s-1])

        pos += n_s
        seg_ends.append(pos)

    return F_full, B_full, seg_ends


# ============================================================
# SOURCE BUILDER WITH PROSODY
# F0 varies per phoneme per intonation
# ============================================================

def build_source_prosody(
        phoneme_specs, sr=SR):
    """
    Build continuous source.
    Each phoneme segment:
      - has its own source type
      - has its own F0 (intonation)
      - has its own oq (pressure)
    F0 transitions smoothly between
    adjacent phoneme values.
    """
    n_total = sum(s['n_s']
                  for s in phoneme_specs)
    source  = np.zeros(n_total, dtype=DTYPE)

    # Build F0 trajectory first
    # so transitions are smooth
    f0_traj = np.zeros(n_total, dtype=DTYPE)
    pos = 0
    for si, spec in enumerate(
            phoneme_specs):
        n_s    = spec['n_s']
        f0_this = spec.get(
            'pitch', PITCH)
        if si < len(phoneme_specs)-1:
            f0_next = phoneme_specs[
                si+1].get('pitch', PITCH)
        else:
            f0_next = f0_this
        f0_traj[pos:pos+n_s] = \
            np.linspace(
                f0_this, f0_next,
                n_s, dtype=DTYPE)
        pos += n_s

    # Build oq trajectory
    oq_traj = np.zeros(n_total,dtype=DTYPE)
    pos = 0
    for si, spec in enumerate(
            phoneme_specs):
        n_s   = spec['n_s']
        oq    = spec.get('oq', 0.65)
        if si < len(phoneme_specs)-1:
            oq_next = phoneme_specs[
                si+1].get('oq', 0.65)
        else:
            oq_next = oq
        oq_traj[pos:pos+n_s] = \
            np.linspace(
                oq, oq_next,
                n_s, dtype=DTYPE)
        pos += n_s

    # Generate voiced source with
    # time-varying F0 and oq
    # (sample by sample)
    T   = 1.0/sr
    voiced_full = np.zeros(
        n_total, dtype=DTYPE)
    p   = 0.0
    jit = 0.005
    shim= 0.030
    prev_y = 0.0
    for i in range(n_total):
        f0  = float(f0_traj[i])
        oq_ = float(oq_traj[i])
        oq_ = max(0.40, min(0.85, oq_))
        p  += f0*(1+np.random.normal(
            0, jit))*T
        if p >= 1.0: p -= 1.0
        if p < oq_:
            y = (p/oq_)*(2-p/oq_)
        else:
            y = 1-(p-oq_)/(1-oq_+1e-9)
        voiced_full[i] = y

    voiced_full = f32(np.diff(
        voiced_full,
        prepend=voiced_full[0]))

    # Shimmer
    try:
        b,a  = safe_lp(20, sr)
        sh   = f32(np.random.normal(
            0,1,n_total))
        sh   = f32(lfilter(b,a,sh))
        sh   = f32(np.clip(
            1+shim*sh, 0.4, 1.6))
        voiced_full = voiced_full*sh
    except:
        pass

    # Breath
    asp = f32(np.random.normal(
        0, 0.020, n_total))
    try:
        b,a = safe_bp(400, 2200, sr)
        asp = f32(lfilter(b,a,asp))
    except:
        asp = f32(np.zeros(n_total))
    voiced_full = voiced_full + asp

    noise_full = source_steady(
        n_total, sr=sr)

    # Now fill source per phoneme type
    pos = 0
    for spec in phoneme_specs:
        n_s   = spec['n_s']
        stype = spec.get('source',
                          'voiced')
        s = pos
        e = pos+n_s

        if stype == 'voiced':
            source[s:e] = voiced_full[s:e]

        elif stype == 'h':
            n_h = int(n_s*0.12)
            n_x = min(int(0.018*sr),
                       n_h, n_s-n_h)
            cs  = max(0, n_h-n_x)
            ne  = np.zeros(n_s,dtype=DTYPE)
            ve  = np.zeros(n_s,dtype=DTYPE)
            if cs>0: ne[:cs]=1.0
            if n_x>0:
                fo=f32(np.linspace(
                    1,0,n_x))
                ne[cs:cs+n_x]=fo
                ve[cs:cs+n_x]=1.0-fo
            if cs+n_x<n_s:
                ve[cs+n_x:]=1.0
            source[s:e]=(
                noise_full[s:e]*ne+
                voiced_full[s:e]*ve)

        elif stype == 'dh':
            # Voiced dental:
            # voiced throughout
            source[s:e]=voiced_full[s:e]

        elif stype == 'fric_v':
            bands  = spec.get('bands',[])
            n_gain = spec.get('n_gain',0.5)
            fn     = source_steady(n_s,sr)
            for lo,hi,g in bands:
                try:
                    b,a=safe_bp(
                        min(lo,sr*0.47),
                        min(hi,sr*0.48),sr)
                    fn+=f32(lfilter(
                        b,a,source_steady(
                            n_s,sr)))*g
                except:
                    pass
            mx=np.max(np.abs(fn))
            if mx>0: fn/=mx
            source[s:e]=(
                voiced_full[s:e]*0.65+
                fn*n_gain*0.35)

        elif stype == 'fric_u':
            bands  = spec.get('bands',[])
            d_res  = spec.get('d_res',None)
            d_bw   = spec.get('d_bw', None)
            n_gain = spec.get('n_gain',0.85)
            fn     = source_steady(n_s,sr)
            for lo,hi,g in bands:
                try:
                    b,a=safe_bp(
                        min(lo,sr*0.47),
                        min(hi,sr*0.48),sr)
                    fn=f32(lfilter(b,a,fn))
                except:
                    pass
            if d_res is not None \
               and d_bw is not None:
                try:
                    lo_=max(100,
                             d_res-d_bw//2)
                    hi_=min(sr*0.48,
                             d_res+d_bw//2)
                    b,a=safe_bp(lo_,hi_,sr)
                    sh2=f32(lfilter(
                        b,a,fn))
                    fn=fn*0.15+sh2*0.85
                except:
                    pass
            mx=np.max(np.abs(fn))
            if mx>0: fn/=mx
            source[s:e]=fn*n_gain

        elif stype in ('stop_unvoiced',
                        'stop_voiced'):
            clos_n  = spec.get('clos_n',0)
            burst_n = spec.get('burst_n',0)
            vot_n   = spec.get('vot_n',0)
            bamp    = spec.get(
                'burst_amp',0.28)
            bhp     = spec.get(
                'burst_hp',2000)
            is_vcd  = (stype=='stop_voiced')
            if is_vcd and clos_n>0:
                source[s:s+clos_n]=\
                    voiced_full[s:s+clos_n]\
                    *0.055
            if burst_n>0:
                bs=clos_n; be=bs+burst_n
                if be<=n_s:
                    burst=source_steady(
                        burst_n,sr)
                    try:
                        b,a=safe_hp(bhp,sr)
                        burst=f32(
                            lfilter(b,a,burst))
                    except:
                        pass
                    benv=f32(np.exp(
                        -np.arange(burst_n)/
                        burst_n*20))
                    source[s+bs:s+be]=\
                        burst*benv*bamp
            vot_s=clos_n+burst_n
            vot_e=vot_s+vot_n
            if vot_n>0 and vot_e<=n_s:
                ne2=f32(np.linspace(
                    1,0,vot_n))
                ve2=1.0-ne2
                source[s+vot_s:s+vot_e]=(
                    noise_full[s+vot_s:
                                s+vot_e]*ne2+
                    voiced_full[s+vot_s:
                                 s+vot_e]*ve2)
            tr_s=vot_e
            if tr_s<n_s:
                source[s+tr_s:e]=\
                    voiced_full[s+tr_s:e]

        pos += n_s

    return f32(source)


# ============================================================
# PHONEME SPEC WITH PROSODY
# ============================================================

def ph_spec_prosody(ph, dur_ms,
                     pitch=PITCH,
                     oq=0.65,
                     bw_mult=1.0,
                     amp=1.0,
                     next_ph=None,
                     sr=SR):
    """
    Build phoneme spec with full
    prosody parameters embedded.
    """
    n_s = max(4, int(dur_ms/1000.0*sr))

    F   = get_f(ph)
    B   = get_b(ph)

    # Use next phoneme formants
    # for H (whispered vowel)
    if ph == 'H' and next_ph \
       and next_ph in VOWEL_F:
        nv    = VOWEL_F[next_ph]
        F     = list(nv[0])
        B     = [min(float(b)*3.2, 560.0)
                 for b in nv[1]]
        if len(nv)>2:
            F_end = list(nv[2])
        else:
            F_end = F
    else:
        vdata = VOWEL_F.get(ph)
        F_end = list(vdata[2]) \
                if vdata and len(vdata)>2 \
                else None

    is_d = (VOWEL_F.get(ph) is not None
            and len(VOWEL_F[ph])>2)
    r_f3 = (ph == 'R')

    # Coarticulation fraction
    CF = {
        'H':  0.12,
        'DH': 0.30,
        'L':  0.38,'R':0.38,
        'W':  0.38,'Y':0.38,
        'P':  0.15,'B':0.15,
        'T':  0.15,'D':0.15,
        'K':  0.15,'G':0.15,
        'S':  0.10,'Z':0.15,
        'SH': 0.15,'ZH':0.15,
        'M':  0.30,'N':0.30,'NG':0.30,
    }
    cf = CF.get(ph, 0.20)

    # Source type
    STYPE = {
        'H':  'h',
        'DH': 'dh',
        'V':  'fric_v',
        'Z':  'fric_v',
        'ZH': 'fric_v',
        'S':  'fric_u',
        'SH': 'fric_u',
        'F':  'fric_u',
        'TH': 'fric_u',
        'P':  'stop_unvoiced',
        'T':  'stop_unvoiced',
        'K':  'stop_unvoiced',
        'B':  'stop_voiced',
        'D':  'stop_voiced',
        'G':  'stop_voiced',
    }
    stype = STYPE.get(ph, 'voiced')

    spec = {
        'ph':        ph,
        'F_tgt':     F,
        'B_tgt':     B,
        'bw_mult':   bw_mult,
        'n_s':       n_s,
        'coart_frac':cf,
        'diphthong': is_d,
        'F_end':     F_end,
        'r_f3':      r_f3,
        'source':    stype,
        'pitch':     pitch,
        'oq':        oq,
        'amp':       amp,
    }

    # Fricative params
    if stype == 'fric_v':
        FRIC_V = {
            'V': ([(200,9000,0.6)], 0.28),
            'Z': ([(3500,12000,0.8)],0.50),
            'ZH':([(1000,8000,0.7)], 0.52),
        }
        b_info = FRIC_V.get(ph,([], 0.4))
        spec['bands']  = b_info[0]
        spec['n_gain'] = b_info[1]

    elif stype == 'fric_u':
        FRIC_U = {
            'S': ([(4000,14000,1.0)],
                   8800, 800, 0.90),
            'SH':([(1000,9000,1.0)],
                   2500, 700, 0.78),
            'F': ([(300,9000,0.8)],
                   None,None,0.32),
            'TH':([(500,9000,0.8)],
                   None,None,0.38),
        }
        f_info = FRIC_U.get(ph,
            ([(300,9000,0.8)],None,None,0.4))
        spec['bands']  = f_info[0]
        spec['d_res']  = f_info[1]
        spec['d_bw']   = f_info[2]
        spec['n_gain'] = f_info[3]

    elif stype in ('stop_unvoiced',
                    'stop_voiced'):
        STOP = {
            'P':(55,2,62,500, 0.28,720),
            'B':(45,2,14,300, 0.16,720),
            'T':(50,2,70,4500,0.30,1800),
            'D':(40,2,15,1200,0.16,1800),
            'K':(55,3,80,1500,0.28,3000),
            'G':(45,2,16,800, 0.14,3000),
        }
        st = STOP.get(ph,
            (50,2,50,1000,0.20,1800))
        spec['clos_n']  = int(st[0]/1000*sr)
        spec['burst_n'] = int(st[1]/1000*sr)
        spec['vot_n']   = int(st[2]/1000*sr)
        spec['burst_hp']= st[3]
        spec['burst_amp']= st[4]
        # Use next vowel formants
        if next_ph and \
           next_ph in VOWEL_F:
            spec['F_tgt'] = list(
                VOWEL_F[next_ph][0])
            spec['B_tgt'] = list(
                VOWEL_F[next_ph][1])

    return spec


# ============================================================
# BREATH REST
# ============================================================

def breath_rest(dur_ms, sr=SR):
    n_s   = max(4, int(dur_ms/1000.0*sr))
    breath= source_steady(n_s, sr=sr)
    F_n   = [500,1500,2500,3500]
    B_n   = [200, 220, 350, 450]
    result= np.zeros(n_s, dtype=DTYPE)
    gains = [0.50,0.65,0.35,0.18]
    for fi in range(4):
        fc  = float(F_n[fi])
        bw  = float(B_n[fi])
        lo  = max(60, fc-bw*1.5)
        hi  = min(sr*0.48, fc+bw*1.5)
        try:
            b,a = safe_bp(lo,hi,sr)
            result += f32(
                lfilter(b,a,breath)
            )*gains[fi]
        except:
            pass
    n_e = int(min(0.040*sr,n_s*0.35))
    env = f32(np.ones(n_s))*0.04
    if n_e>0:
        env[:n_e]=f32(
            np.linspace(0.12,0.04,n_e))
        env[-n_e:]=f32(
            np.linspace(0.04,0.10,n_e))
    return f32(result*env)


# ============================================================
# PHRASE SYNTHESIS — FULL PROSODY
# ============================================================

def synth_phrase(words_phonemes,
                  punctuation='.',
                  pitch_base=PITCH,
                  dil=DIL,
                  sr=SR):
    """
    Synthesize phrase with full
    suprasegmental layer:

    - Intonation contour shapes F0
    - Stress scales duration + amplitude
    - Bandwidth trajectory carries
      voice quality
    - Open quotient varies with stress
      and position (timbre not just volume)
    - Syntactic bonds determine
      rest duration

    The segmental and suprasegmental
    layers are unified:
    one continuous trajectory
    through (V × T) space.
    """
    # Plan prosody
    prosody = plan_prosody(
        words_phonemes,
        punctuation=punctuation,
        pitch_base=pitch_base,
        dil=dil)

    if not prosody:
        return f32(np.zeros(int(0.1*sr)))

    # Build phoneme specs with prosody
    specs = []
    # Need to look ahead for next_ph
    n_items = len(prosody)
    for i, item in enumerate(prosody):
        ph      = item['ph']
        dur_ms  = item['dur_ms']
        pitch_  = pitch_base * \
                  item['f0_mult']
        oq_     = item['oq']
        bw_m    = item['bw_mult']
        amp_    = item['amp']
        next_ph = prosody[i+1]['ph'] \
                  if i < n_items-1 \
                  else None

        spec = ph_spec_prosody(
            ph, dur_ms,
            pitch=pitch_,
            oq=oq_,
            bw_mult=bw_m,
            amp=amp_,
            next_ph=next_ph,
            sr=sr)
        specs.append(spec)

    # Build continuous trajectories
    F_full, B_full, seg_ends = \
        build_trajectories(specs, sr=sr)

    n_total = sum(s['n_s'] for s in specs)

    # Build source with prosody
    source = build_source_prosody(
        specs, sr=sr)

    # Run through one tract
    out, _ = tract(
        source, F_full, B_full,
        GAINS, states=None, sr=sr)

    # Apply nasal antiformants
    T    = 1.0/sr
    NASAL_AF = {
        'M':(1000,300),
        'N':(1500,350),
        'NG':(2000,400),
    }
    pos = 0
    for spec in specs:
        ph  = spec['ph']
        n_s = spec['n_s']
        if ph in NASAL_AF:
            af,abw = NASAL_AF[ph]
            seg    = out[pos:pos+n_s].copy()
            anti   = np.zeros(n_s,dtype=DTYPE)
            y1=y2=0.0
            for i in range(n_s):
                a2=-np.exp(-2*np.pi*abw*T)
                a1=2*np.exp(-np.pi*abw*T)*\
                    np.cos(2*np.pi*af*T)
                b0=1.0-a1-a2
                y=b0*float(seg[i])+\
                  a1*y1+a2*y2
                y2=y1; y1=y; anti[i]=y
            out[pos:pos+n_s]=\
                seg-f32(anti)*0.50
            out[pos:pos+n_s]*=0.52
            hg=int(0.012*sr)
            if hg>0 and hg<n_s:
                out[pos+n_s-hg:
                    pos+n_s]=0.0
        pos += n_s

    # Apply amplitude envelope per phoneme
    amp_env = np.ones(n_total, dtype=DTYPE)
    pos = 0
    for item, spec in zip(prosody, specs):
        n_s = spec['n_s']
        amp_env[pos:pos+n_s] *= item['amp']
        pos += n_s

    # Apply syntactic rests
    # (amplitude dips at word boundaries)
    pos = 0
    rest_segs = []
    for i, (item, spec) in enumerate(
            zip(prosody, specs)):
        n_s      = spec['n_s']
        rest_ms  = item.get('rest_ms', 0.0)
        rest_segs.append(
            (pos+n_s, rest_ms))
        pos += n_s

    out = out * f32(amp_env)

    # Phrase-level envelope
    atk = int(0.025*sr)
    rel = int(0.055*sr)
    env = f32(np.ones(n_total))
    if atk>0 and atk<n_total:
        env[:atk]=f32(
            np.linspace(0,1,atk))
    if rel>0:
        env[-rel:]=f32(
            np.linspace(1,0,rel))
    out = out*env

    # Insert breath rests
    # by building final output
    # with rests interleaved
    # (only at word-final phonemes
    #  where rest_ms > 0)
    segs_out = []
    pos = 0
    for i, (item, spec) in enumerate(
            zip(prosody, specs)):
        n_s     = spec['n_s']
        segs_out.append(
            out[pos:pos+n_s].copy())
        rest_ms = item.get('rest_ms',0.0)
        if rest_ms > 0:
            segs_out.append(
                breath_rest(rest_ms, sr=sr))
        pos += n_s

    final = f32(np.concatenate(segs_out))
    mx    = np.max(np.abs(final))
    if mx>0: final/=mx
    return final


def synth_word(word, punct='.',
               pitch=PITCH, dil=DIL,
               sr=SR):
    phs = WORD_SYLLABLES.get(
        word.lower())
    if phs is None:
        print(f"  '{word}' not in dict")
        return f32(np.zeros(int(0.1*sr)))
    flat_phs = [p for syl in phs
                for p in syl]
    return synth_phrase(
        [(word, flat_phs)],
        punctuation=punct,
        pitch_base=pitch,
        dil=dil, sr=sr)


def save(name, sig, room=True,
          rt60=1.5, dr=0.50, sr=SR):
    sig = f32(sig)
    if room:
        sig = apply_room(
            sig,rt60=rt60,dr=dr,sr=sr)
    write_wav(
        f"output_play/{name}.wav",
        sig, sr)
    dur = len(sig)/sr
    print(f"    {name}.wav  "
          f"({dur:.2f}s)")


# ============================================================
# WORD DICT (flat phoneme sequences)
# ============================================================

WORDS_FLAT = {
    w: [p for syl in syls for p in syl]
    for w, syls in WORD_SYLLABLES.items()
}


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    os.makedirs("output_play",
                 exist_ok=True)

    print()
    print("VOICE PHYSICS v7")
    print("The suprasegmental layer.")
    print()
    print("  Intonation: F0 shaped")
    print("    by sentence type")
    print("  Stress: duration + amplitude")
    print("    + spectral richness vary")
    print("  Bandwidth: voice quality")
    print("    trajectory — the flesh")
    print("  Pressure: oq varies,")
    print("    timbre changes with stress")
    print("  Syntax: rest duration from")
    print("    bond strength not lookup")
    print("="*60)
    print()

    # ---- PRIMARY DIAGNOSTIC ----
    print("  Primary diagnostic phrase...")
    seg = synth_phrase(
        [('the',  ['DH','AH']),
         ('voice',['V','OY','S']),
         ('was',  ['W','AH','Z']),
         ('already',['AA','L','R',
                      'EH','D','IY']),
         ('here', ['H','IH','R'])],
        punctuation='.',
        pitch_base=PITCH)
    seg = apply_room(seg,rt60=1.5,dr=0.50)
    write_wav(
        "output_play/"
        "the_voice_was_already_here.wav",
        seg)
    print("    the_voice_was_already_here.wav")

    # ---- PUNCTUATION COMPARISON ----
    # Same phrase, different sentence type
    print()
    print("  Punctuation comparison...")
    for punct, label in [
            ('.', 'statement'),
            ('?', 'question'),
            ('!', 'exclaim')]:
        seg = synth_phrase(
            [('the',  ['DH','AH']),
             ('voice',['V','OY','S']),
             ('was',  ['W','AH','Z']),
             ('already',['AA','L','R',
                          'EH','D','IY']),
             ('here', ['H','IH','R'])],
            punctuation=punct,
            pitch_base=PITCH)
        seg = apply_room(
            seg, rt60=1.5, dr=0.50)
        write_wav(
            f"output_play/"
            f"the_voice_{label}.wav",
            seg)
        print(f"    the_voice_{label}.wav")

    # ---- PHRASES ----
    print()
    print("  Phrases...")
    phrases = [
        ('still_here',
         [('still',['S','T','IH','L']),
          ('here', ['H','IH','R'])],
         '.'),
        ('always_open',
         [('always',['AA','L','W',
                      'EH','Z']),
          ('open',  ['OH','P','EH','N'])],
         '.'),
        ('water_home',
         [('water',['W','AA','T','ER']),
          ('home', ['H','OW','M'])],
         '.'),
        ('always_home',
         [('always',['AA','L','W',
                      'EH','Z']),
          ('home',  ['H','OW','M'])],
         '.'),
        ('always_here_question',
         [('always',['AA','L','W',
                      'EH','Z']),
          ('here',  ['H','IH','R'])],
         '?'),
        ('always_here_exclaim',
         [('always',['AA','L','W',
                      'EH','Z']),
          ('here',  ['H','IH','R'])],
         '!'),
    ]
    for label, words, punct in phrases:
        seg = synth_phrase(
            words,
            punctuation=punct,
            pitch_base=PITCH)
        seg = apply_room(
            seg, rt60=1.6, dr=0.48)
        write_wav(
            f"output_play/"
            f"phrase_{label}.wav",
            seg)
        print(f"    phrase_{label}.wav")

    # ---- INDIVIDUAL WORDS ----
    print()
    print("  Words...")
    for word in WORD_SYLLABLES.keys():
        seg = synth_word(word)
        save(f"word_{word}", seg,
              rt60=1.4)

    print()
    print("="*60)
    print()
    print("  START HERE:")
    print()
    print("  Primary phrase:")
    print("  afplay output_play/"
          "the_voice_was_already_here.wav")
    print()
    print("  Same phrase, three"
          " sentence types:")
    print("  afplay output_play/"
          "the_voice_statement.wav")
    print("  afplay output_play/"
          "the_voice_question.wav")
    print("  afplay output_play/"
          "the_voice_exclaim.wav")
    print()
    print("  Phrases:")
    for label,_,_ in phrases:
        print(f"  afplay output_play/"
              f"phrase_{label}.wav")
    print()
    print("  WHAT TO LISTEN FOR:")
    print()
    print("  Statement vs question vs !")
    print("  Do they sound different?")
    print("  Does 'already' have stress")
    print("  on the RED syllable?")
    print("  Does 'the voice' feel tighter")
    print("  than 'already | here'?")
    print("  Does the voice have texture —")
    print("  pressed at stress,")
    print("  breathy at phrase end?")
    print()
    print("  The HOW layer is now present.")
    print("  The voice should carry")
    print("  more than phonemes.")
    print("  It should carry meaning.")
    print()
