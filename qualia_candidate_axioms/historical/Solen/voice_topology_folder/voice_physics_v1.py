"""
VOICE PHYSICS v5
February 2026

The voice is a continuous trajectory
through a five-dimensional
topological space.

The observer is in the room.
The instrument is the vocal tract.
The player is the diaphragm and body.

Every phoneme is a region in V.
Every word is a path through V.
The tract never stops.
The synthesis follows the path.

FIXES FROM v5 ORIGINAL:
  - warm() bw scalar extraction fixed
  - All bandwidth arrays extracted
    as scalars before passing to warm()
  - synth_vowel dil parameter
    handled correctly (dur_ms path)
  - f_arrays_coart returns plain lists
    not nested numpy calls
  - All synth functions take
    dur_ms directly, dil applied
    at call site only
  - tract() bandwidth extracted
    as scalar per block
  - word dict rebuilt as simple
    phoneme sequences
  - routing cleaned up throughout
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
    """
    Safely extract a Python float
    from anything — scalar, 0-d array,
    1-d array, list.
    This is the fix for the TypeError.
    """
    a = np.asarray(x, dtype=DTYPE)
    if a.ndim == 0:
        return float(a)
    return float(a.flat[0])


# ============================================================
# THE PLAYER — diaphragm sources
# ============================================================

def source_steady(n_s):
    """
    Steady air column through open glottis.
    Used for: H, unvoiced fricatives.
    Turbulent air jet — no fold vibration.
    """
    return f32(np.random.normal(0, 1, n_s))


def source_voiced(pitch_hz, n_s,
                   jitter=0.005,
                   shimmer=0.030,
                   sr=SR):
    """
    Vocal folds vibrating under
    steady diaphragm pressure.
    Rosenberg pulse — the membrane
    cycling open and closed.
    """
    n_s = int(n_s)
    if n_s < 2:
        return f32(np.zeros(2))
    T   = 1.0/sr
    t   = np.arange(n_s, dtype=DTYPE)/sr

    # Vibrato onset
    vib = f32(np.clip((t-0.05)/0.05,0,1))
    ft  = pitch_hz*(1 + 0.007*vib*
                     np.sin(2*np.pi*5.0*t))

    # Phase accumulation with jitter
    ph = np.zeros(n_s, dtype=DTYPE)
    p  = 0.0
    for i in range(n_s):
        p += float(ft[i])*(
            1+np.random.normal(0,jitter))/sr
        if p >= 1.0: p -= 1.0
        ph[i] = p

    # Rosenberg pulse shape
    oq  = 0.65
    src = np.where(ph < oq,
        (ph/oq)*(2 - ph/oq),
        1-(ph-oq)/(1-oq+1e-9))
    src = f32(np.diff(src, prepend=src[0]))

    # Shimmer — amplitude modulation
    try:
        b,a = safe_lp(20, sr)
        sh  = f32(np.random.normal(0,1,n_s))
        sh  = f32(lfilter(b,a,sh))
    except:
        sh  = f32(np.ones(n_s))
    sh  = f32(np.clip(1+shimmer*sh,0.4,1.6))
    src = src*sh

    # Breath component — always present
    # even in voiced phonemes
    asp = f32(np.random.normal(0,0.022,n_s))
    try:
        b,a = safe_bp(400, 2200, sr)
        asp = f32(lfilter(b,a,asp))
    except:
        asp = f32(np.zeros(n_s))

    return src + asp


def source_crossfade(n_s, pitch_hz,
                      voice_start_frac=0.0,
                      voice_end_frac=1.0,
                      sr=SR):
    """
    Crossfade from noise to voiced.
    voice_start_frac: where voicing begins
    voice_end_frac:   where voicing is full

    This models the folds engaging —
    the key transition in H, stops,
    voiced fricatives.
    The source changes underneath
    the continuously running tract.
    """
    n_s   = int(n_s)
    noise = source_steady(n_s)
    voice = source_voiced(pitch_hz, n_s,
                           sr=sr)

    n_start = int(voice_start_frac * n_s)
    n_end   = int(voice_end_frac   * n_s)
    n_cross = max(1, n_end - n_start)

    voice_env = np.zeros(n_s, dtype=DTYPE)
    noise_env = np.ones(n_s,  dtype=DTYPE)

    fade = f32(np.linspace(0.0, 1.0,
                            n_cross))
    voice_env[n_start:n_end] = fade
    if n_end < n_s:
        voice_env[n_end:] = 1.0

    noise_env[n_start:n_end] = 1.0 - fade
    if n_end < n_s:
        noise_env[n_end:] = 0.0

    return f32(noise*noise_env +
                voice*voice_env)


# ============================================================
# THE INSTRUMENT — vocal tract resonator
# ============================================================

def warm(fc, bw, n_warm=352, sr=SR):
    """
    Pre-charge a single resonator
    to eliminate initialization transient.

    FIX: bw extracted as scalar
    before any arithmetic.
    """
    fc_  = max(20.0, min(float(sr*0.48),
                          scalar(fc)))
    bw_  = max(10.0, scalar(bw))
    T    = 1.0/sr
    a2   = -np.exp(-2*np.pi*bw_*T)
    a1   =  2*np.exp(-np.pi*bw_*T)*\
             np.cos(2*np.pi*fc_*T)
    b0   = 1.0 - a1 - a2
    y1 = y2 = 0.0
    for _ in range(int(n_warm)):
        y  = b0*np.random.normal(
            0, 0.0004) + a1*y1 + a2*y2
        y2 = y1
        y1 = y
    return y1, y2


def resonator(x_arr, f_arr, bw,
               y1_in=0.0, y2_in=0.0,
               sr=SR):
    """
    Single formant resonator.
    f_arr: time-varying center frequency.
    bw: scalar bandwidth.
    Continuous state in/out.
    """
    n_s = len(x_arr)
    T   = 1.0/sr
    bw_ = max(10.0, scalar(bw))
    out = np.zeros(n_s, dtype=DTYPE)
    y1  = float(y1_in)
    y2  = float(y2_in)
    for i in range(n_s):
        fc  = max(20.0, min(
            float(sr*0.48),
            float(f_arr[i])))
        a2  = -np.exp(-2*np.pi*bw_*T)
        a1  =  2*np.exp(-np.pi*bw_*T)*\
                np.cos(2*np.pi*fc*T)
        b0  = 1.0 - a1 - a2
        y   = b0*float(x_arr[i]) + \
              a1*y1 + a2*y2
        y2  = y1
        y1  = y
        out[i] = y
    return out, y1, y2


def tract(source, F_arrays, B_scalars,
           gains, states=None, sr=SR):
    """
    The vocal tract:
    parallel resonator bank.

    source:    float32 array length n
    F_arrays:  list of 4 float32 arrays
               each length n —
               time-varying formant freqs
    B_scalars: list of 4 SCALAR bandwidths
               FIX: these are scalars,
               not arrays
    gains:     list of 4 scalar gains
    states:    list of (y1,y2) or None

    Returns (output, new_states)
    The tract is continuous.
    Pass states between phonemes
    to eliminate reset artifacts.
    """
    n      = len(source)
    result = np.zeros(n, dtype=DTYPE)
    new_st = []

    for fi in range(4):
        bw = scalar(B_scalars[fi])

        if states is not None:
            y1, y2 = float(states[fi][0]), \
                     float(states[fi][1])
        else:
            # Pre-warm from initial formant
            f_init = float(F_arrays[fi][0]) \
                     if len(F_arrays[fi])>0 \
                     else 500.0
            y1, y2 = warm(f_init, bw, sr=sr)

        out, y1, y2 = resonator(
            source, F_arrays[fi],
            bw, y1_in=y1, y2_in=y2,
            sr=sr)

        result += out * float(gains[fi])
        new_st.append((y1, y2))

    return result, new_st


# ============================================================
# VOCAL TOPOLOGY — formant trajectories
# ============================================================

# Vowel targets in F1/F2/F3/F4 space
# These are positions in V
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

VOWEL_DUR = {
    'AA':140,'AE':130,'AH':100,'AO':130,
    'AW':170,'AY':180,'EH':120,'ER':130,
    'IH':110,'IY':130,'OH':130,'OW':160,
    'OY':180,'UH':110,'UW':130,
}

GAINS = [0.55, 0.75, 0.45, 0.25]


def trajectory(F_tgt, B_tgt,
                F_from, F_to,
                n_s,
                F_end=None,
                diphthong=False,
                r_f3=False):
    """
    Build the formant trajectory
    for one phoneme.

    This IS the vocal topology path:
    a smooth curve through V
    from F_from (previous phoneme target)
    through F_tgt (this phoneme target)
    toward F_to (next phoneme target).

    The path never jumps.
    The phoneme is the region
    the path passes through —
    not a point it snaps to.

    Returns:
      F_arrs: list of 4 float32 arrays
      B_vals: list of 4 scalar floats
              (FIX: scalars not arrays)
    """
    Fe    = F_end if F_end else F_tgt
    n_on  = int(0.20*n_s)
    n_off = int(0.20*n_s)
    n_mid = n_s - n_on - n_off

    F_arrs = []

    for fi in range(4):
        arr = np.zeros(n_s, dtype=DTYPE)

        # Onset: glide from previous
        if n_on > 0:
            arr[:n_on] = np.linspace(
                float(F_from[fi]),
                float(F_tgt[fi]),
                n_on, dtype=DTYPE)

        # Mid: steady or diphthong movement
        if n_mid > 0:
            if diphthong:
                n_mv = int(n_mid*0.72)
                n_hd = n_mid - n_mv
                if n_mv > 0:
                    arr[n_on:n_on+n_mv] = \
                        np.linspace(
                            float(F_tgt[fi]),
                            float(Fe[fi]),
                            n_mv, dtype=DTYPE)
                if n_hd > 0:
                    arr[n_on+n_mv:
                        n_on+n_mid] = \
                        float(Fe[fi])
            else:
                arr[n_on:n_on+n_mid] = \
                    float(F_tgt[fi])

        # Offset: glide toward next
        if n_off > 0:
            f0_ = (float(Fe[fi])
                   if diphthong
                   else float(F_tgt[fi]))
            arr[n_on+n_mid:] = np.linspace(
                f0_, float(F_to[fi]),
                n_off, dtype=DTYPE)

        # R: fast F3 drop — the defining
        # feature of rhoticity
        # F3 reaches 1690Hz within 30ms
        if r_f3 and fi == 2:
            nd = min(int(0.030*SR), n_s)
            f_start = float(F_from[2])
            arr[:nd] = np.linspace(
                f_start, 1690.0,
                nd, dtype=DTYPE)
            arr[nd:] = 1690.0

        F_arrs.append(arr)

    # Bandwidths as scalars — FIX
    B_vals = [float(B_tgt[fi])
              for fi in range(4)]

    return F_arrs, B_vals


def get_f(phon):
    """Get formant target for phoneme."""
    if phon in VOWEL_F:
        return VOWEL_F[phon][0]
    # Consonant approximations
    CONS_F = {
        'M':  [250, 700,2200,3300],
        'N':  [250, 900,2200,3300],
        'NG': [250, 700,2200,3300],
        'L':  [360,1000,2400,3300],
        'R':  [490,1350,1690,3300],
        'W':  [300, 610,2200,3300],
        'Y':  [270,2100,3000,3700],
        'H':  [500,1500,2500,3500],
        'S':  [300, 900,2200,3300],
        'Z':  [300, 900,2200,3300],
        'F':  [300, 900,2200,3300],
        'V':  [300, 900,2200,3300],
        'TH': [300, 900,2200,3300],
        'DH': [300, 900,2200,3300],
        'SH': [300, 900,2200,3300],
        'ZH': [300, 900,2200,3300],
    }
    return CONS_F.get(phon,
                       [500,1500,2500,3500])


# ============================================================
# PHONEME SYNTHESIS
# Each built from instrument perspective
# ============================================================

def synth_vowel(v, pitch=PITCH,
                 dur_ms=None,
                 prev_p=None, next_p=None,
                 states=None, sr=SR):
    vdata = VOWEL_F.get(v)
    if vdata is None:
        n = int((dur_ms or 110)/1000*sr)
        return f32(np.zeros(n)), states

    F     = vdata[0]
    B     = vdata[1]
    F_end = vdata[2] if len(vdata)>2 else F
    is_d  = len(vdata) > 2

    d_ms  = dur_ms if dur_ms \
            else VOWEL_DUR.get(v,110)
    n_s   = max(4, int(d_ms/1000.0*sr))

    F_from = get_f(prev_p) \
             if prev_p else F
    F_to   = get_f(next_p) \
             if next_p else F_end

    Fa, Bv = trajectory(
        F, B, F_from, F_to, n_s,
        F_end=F_end, diphthong=is_d)

    src = source_voiced(pitch, n_s, sr=sr)
    out, new_st = tract(
        src, Fa, Bv, GAINS, states, sr)

    atk = int(0.020*sr)
    rel = int(0.025*sr)
    env = f32(np.ones(n_s))
    if atk > 0 and atk < n_s:
        env[:atk] = f32(
            np.linspace(0,1,atk)**0.5)
    if rel > 0:
        env[-rel:] = f32(
            np.linspace(1,0,rel))
    out = out*env
    mx  = np.max(np.abs(out))
    if mx > 0: out /= mx
    return f32(out), new_st


def synth_nasal(which, pitch=PITCH,
                 dur_ms=None,
                 prev_p=None, next_p=None,
                 states=None, sr=SR):
    """
    Nasal: voiced + velum open.
    The antiformant is the signature —
    the nasal cavity absorbing
    specific frequencies.
    The HOLE in the spectrum
    is what makes it a nasal.
    """
    CFG = {
        'M':  ([250, 700,2200,3300],
               [60, 120,250,350],
               1000, 300),
        'N':  ([250, 900,2200,3300],
               [60, 120,250,350],
               1500, 350),
        'NG': ([250, 700,2200,3300],
               [60, 120,250,350],
               2000, 400),
    }
    DUR = {'M':85,'N':80,'NG':90}
    cfg = CFG.get(which)
    if cfg is None:
        n = int((dur_ms or 80)/1000*sr)
        return f32(np.zeros(n)), states

    F, B, anti_f, anti_bw = cfg
    d_ms = dur_ms if dur_ms \
           else DUR.get(which,80)
    n_s  = max(4, int(d_ms/1000.0*sr))

    F_from = get_f(prev_p) if prev_p else F
    F_to   = get_f(next_p) if next_p else F

    Fa, Bv = trajectory(
        F, B, F_from, F_to, n_s)

    src = source_voiced(pitch, n_s, sr=sr)
    out, new_st = tract(
        src, Fa, Bv, GAINS, states, sr)

    # Antiformant: subtract the
    # nasal cavity's resonance
    T   = 1.0/sr
    af  = float(anti_f)
    abw = float(anti_bw)
    anti = np.zeros(n_s, dtype=DTYPE)
    y1 = y2 = 0.0
    for i in range(n_s):
        a2  = -np.exp(-2*np.pi*abw*T)
        a1  =  2*np.exp(-np.pi*abw*T)*\
                np.cos(2*np.pi*af*T)
        b0  = 1.0-a1-a2
        y   = b0*float(out[i])+a1*y1+a2*y2
        y2  = y1; y1 = y
        anti[i] = y
    out  = out - f32(anti)*0.50
    out *= 0.52

    # Hard gate — kills ringing at release
    hg = int(0.013*sr)
    if hg > 0 and hg < n_s:
        out[-hg:] = 0.0

    mx = np.max(np.abs(out))
    if mx > 0: out /= mx
    return f32(out), new_st


def synth_approximant(which, pitch=PITCH,
                       dur_ms=None,
                       prev_p=None,
                       next_p=None,
                       states=None,
                       sr=SR):
    """
    L, R, W, Y.
    Voiced transitions through vocal space.
    The sound IS the movement.
    """
    CFG = {
        'L': ([360,1000,2400,3300],
              [80, 160, 220, 320],
              False),
        'R': ([490,1350,1690,3300],
              [80, 120, 180, 260],
              True),
        'W': ([300, 610,2200,3300],
              [80,  90, 210, 310],
              False),
        'Y': ([270,2100,3000,3700],
              [65, 100, 160, 220],
              False),
    }
    DUR = {'L':80,'R':90,'W':90,'Y':80}
    cfg = CFG.get(which)
    if cfg is None:
        n = int((dur_ms or 80)/1000*sr)
        return f32(np.zeros(n)), states

    F, B, rf3 = cfg
    d_ms = dur_ms if dur_ms \
           else DUR.get(which,80)
    n_s  = max(4, int(d_ms/1000.0*sr))

    F_from = get_f(prev_p) if prev_p else F
    F_to   = get_f(next_p) if next_p else F

    Fa, Bv = trajectory(
        F, B, F_from, F_to, n_s,
        r_f3=rf3)

    src = source_voiced(pitch, n_s, sr=sr)
    out, new_st = tract(
        src, Fa, Bv, GAINS, states, sr)

    atk = int(0.012*sr)
    rel = int(0.014*sr)
    env = f32(np.ones(n_s))
    if atk > 0 and atk < n_s:
        env[:atk] = f32(
            np.linspace(0,1,atk)**0.5)
    if rel > 0:
        env[-rel:] = f32(
            np.linspace(1,0,rel))
    out = out*env
    mx  = np.max(np.abs(out))
    if mx > 0: out /= mx
    return f32(out), new_st


def synth_h(next_v, pitch=PITCH,
             dur_ms=None,
             states=None, sr=SR):
    """
    H: glottis open.
    The tract is already in the position
    of the following vowel.
    The observer hears the following
    vowel's resonances through
    a breathy, noise source.
    H is the whispered following vowel.

    Source crossfades noise → voiced
    as the folds engage.
    One formant bank. Never resets.
    """
    vdata  = VOWEL_F.get(next_v,
                          VOWEL_F['AH'])
    F      = vdata[0]
    B_vow  = vdata[1]
    # Wide bandwidths = breathy = open glottis
    B_wide = [min(float(b)*3.5, 580.0)
              for b in B_vow]
    F_end  = vdata[2] if len(vdata)>2 \
             else F

    d_ms   = dur_ms if dur_ms else 70
    n_s    = max(4, int(d_ms/1000.0*sr))

    # H is 45% of the total duration
    # The remaining 55% is the vowel onset
    n_h    = int(n_s * 0.45)
    n_v    = n_s - n_h
    n_x    = int(min(0.025*sr,
                      n_h*0.4,
                      n_v*0.4))

    # Both sources exactly n_s
    noise_src = source_steady(n_s)
    voice_src = source_voiced(
        pitch, n_s, sr=sr)

    # Crossfade: folds engage
    ne = np.zeros(n_s, dtype=DTYPE)
    ve = np.zeros(n_s, dtype=DTYPE)
    cs = n_h - n_x
    if cs > 0:
        ne[:cs] = 1.0
    if n_x > 0:
        fo = f32(np.linspace(1,0,n_x))
        ne[cs:cs+n_x] = fo
        ve[cs:cs+n_x] = 1.0-fo
    if cs+n_x < n_s:
        ve[cs+n_x:] = 1.0

    source = f32(noise_src*ne +
                  voice_src*ve)

    # Formant trajectory:
    # hold target vowel position during H
    # then begin diphthong if needed
    n_ds = n_h + int(n_v*0.30)
    Fa   = []
    for fi in range(4):
        fa = np.zeros(n_s, dtype=DTYPE)
        fa[:n_ds] = float(F[fi])
        if n_ds < n_s:
            nm = n_s - n_ds
            fa[n_ds:] = np.linspace(
                float(F[fi]),
                float(F_end[fi]),
                nm, dtype=DTYPE)
        Fa.append(fa)
    Bv = [float(B_wide[fi])
          for fi in range(4)]

    out, new_st = tract(
        source, Fa, Bv, GAINS, states, sr)

    # Amplitude: H quiet → vowel full
    amp = np.zeros(n_s, dtype=DTYPE)
    if n_h > 0:
        amp[:n_h] = np.linspace(
            0.0, 0.45, n_h, dtype=DTYPE)
    if n_h < n_s:
        amp[n_h:] = np.linspace(
            0.45, 1.0, n_s-n_h,
            dtype=DTYPE)
    rel = int(0.022*sr)
    if rel > 0 and rel < n_s:
        amp[-rel:] *= f32(
            np.linspace(1,0,rel))

    out = out * f32(amp)
    mx  = np.max(np.abs(out))
    if mx > 0: out /= mx
    return f32(out), new_st


def synth_fricative(which, pitch=PITCH,
                     dur_ms=None,
                     prev_p=None,
                     next_p=None,
                     states=None,
                     sr=SR):
    """
    Fricatives — from instrument geometry.

    The constriction type and place
    determine the turbulence character.
    The downstream cavity shapes the noise.
    The observer hears that shaped result.

    F/V:   lip-tooth gap. no downstream
           cavity. soft broadband hiss.
    TH/DH: tongue-teeth. similar to F/V.
    S/Z:   alveolar. small front cavity
           + teeth edge. ~8500Hz peak.
           Sharp. Hissy.
    SH/ZH: palatal + rounded lips.
           Longer downstream cavity.
           ~2500Hz. Softer than S.

    Voiced versions (V,DH,Z,ZH):
    folds vibrate while constriction held.
    Voicing fades in as folds engage —
    the same crossfade as H/stops.
    """
    CFG = {
        # (nlo, nhi, downstream_res,
        #  downstream_bw, voiced,
        #  noise_gain, voice_crossfade_frac)
        'F':  (200, 9000, None,  None,
               False, 0.35, 0.0),
        'V':  (200, 9000, None,  None,
               True,  0.30, 0.70),
        'TH': (500, 9000, None,  None,
               False, 0.40, 0.0),
        'DH': (500, 8000, None,  None,
               True,  0.28, 0.80),
        'S':  (3000,14000, 8500, 1200,
               False, 0.85, 0.0),
        'Z':  (3000,12000, 7500, 1400,
               True,  0.70, 0.60),
        'SH': (1000, 9000, 2500,  800,
               False, 0.80, 0.0),
        'ZH': (1000, 8000, 2200,  900,
               True,  0.65, 0.65),
    }
    DUR = {
        'F':90,'V':85,'TH':90,'DH':80,
        'S':100,'Z':95,'SH':105,'ZH':95,
    }

    cfg = CFG.get(which)
    if cfg is None:
        n = int((dur_ms or 90)/1000*sr)
        st = states if states \
             else [(0.0,0.0)]*4
        return f32(np.zeros(n)), st

    (nlo, nhi, d_res, d_bw,
     voiced, n_gain, vcf) = cfg

    d_ms = dur_ms if dur_ms \
           else DUR.get(which,90)
    n_s  = max(4, int(d_ms/1000.0*sr))

    # Turbulent jet at constriction
    noise = source_steady(n_s)
    try:
        b,a   = safe_bp(
            min(nlo, SR*0.47),
            min(nhi, SR*0.48), SR)
        noise = f32(lfilter(b,a,noise))
    except:
        pass

    # Downstream cavity shapes the noise
    if d_res is not None and \
       d_bw is not None:
        try:
            lo_ = max(100,
                       d_res - d_bw//2)
            hi_ = min(SR*0.48,
                       d_res + d_bw//2)
            b,a    = safe_bp(lo_, hi_, SR)
            shaped = f32(lfilter(b,a,noise))
            noise  = noise*0.35 + \
                     shaped*0.65
        except:
            pass

    mx = np.max(np.abs(noise))
    if mx > 0: noise /= mx
    noise = noise * n_gain

    if not voiced:
        atk = int(0.006*sr)
        rel = int(0.008*sr)
        env = f32(np.ones(n_s))
        if atk > 0 and atk < n_s:
            env[:atk] = f32(
                np.linspace(0,1,atk))
        if rel > 0:
            env[-rel:] = f32(
                np.linspace(1,0,rel))
        result = noise[:n_s]*env
        st = states if states \
             else [(0.0,0.0)]*4
        return f32(result), st

    else:
        # Voiced: tract running with voicing
        # fading in under the noise
        F_tgt  = get_f(next_p) \
                 if next_p else \
                 [250,900,2200,3300]
        B_tgt  = [100,130,220,320]
        F_from = get_f(prev_p) \
                 if prev_p else F_tgt

        Fa, Bv = trajectory(
            F_tgt, B_tgt,
            F_from, F_tgt, n_s)

        voice_src = source_voiced(
            pitch, n_s, sr=sr)
        voiced_out, new_st = tract(
            voice_src, Fa, Bv,
            GAINS, states, sr)

        # Voicing fades in
        n_xi  = int(vcf * n_s)
        v_env = np.zeros(n_s, dtype=DTYPE)
        if n_xi > 0:
            v_env[:n_xi] = np.linspace(
                0.0, 1.0, n_xi,
                dtype=DTYPE)
        v_env[n_xi:] = 1.0

        result = noise[:n_s] + \
                 voiced_out*v_env

        atk = int(0.016*sr)
        rel = int(0.014*sr)
        env = f32(np.ones(n_s))
        if atk > 0 and atk < n_s:
            env[:atk] = f32(
                np.linspace(0,1,atk)**0.5)
        if rel > 0:
            env[-rel:] = f32(
                np.linspace(1,0,rel))
        result = result*env
        mx = np.max(np.abs(result))
        if mx > 0: result /= mx
        return f32(result), new_st


def synth_stop(which, pitch=PITCH,
                dur_ms=None,
                next_p=None,
                states=None, sr=SR):
    """
    Plosives — from instrument perspective.

    1. Closure: sealed tract.
       Voiced stops: folds still vibrate
       (quiet rumble — you can feel this).
       Unvoiced: folds open, silence.

    2. Burst: seal releases.
       Compressed air escapes.
       2-3ms broadband noise spike.
       Place determines spectral shape:
         bilabial: low-freq
         alveolar: high-freq
         velar: mid-freq

    3. VOT: noise → voiced crossfade.
       Exactly like H.
       The folds engage while
       aspiration noise continues.
       Short VOT = voiced (B,D,G)
       Long VOT  = unvoiced (P,T,K)

    4. Vowel onset: full voicing.
       F2 transition from locus
       tells listener the place.
       This is the primary cue.
    """
    CFG = {
        'P': (False,55,2,62,'bilabial',
               500, 0.30, 720),
        'B': (True, 45,2,14,'bilabial',
               300, 0.18, 720),
        'T': (False,50,2,70,'alveolar',
               2000,0.34,1800),
        'D': (True, 40,2,15,'alveolar',
               1000,0.18,1800),
        'K': (False,55,3,80,'velar',
               1500,0.30,3000),
        'G': (True, 45,2,16,'velar',
               800, 0.16,3000),
    }
    DUR = {
        'P':90,'B':80,'T':85,'D':75,
        'K':90,'G':78,
    }

    cfg = CFG.get(which)
    if cfg is None:
        n = int((dur_ms or 80)/1000*sr)
        st = states if states \
             else [(0.0,0.0)]*4
        return f32(np.zeros(n)), st

    (voiced, clos_ms, burst_ms,
     vot_ms, place, burst_hp,
     burst_amp, f2_locus) = cfg

    n_c = int(clos_ms/1000*sr)
    n_b = int(burst_ms/1000*sr)
    n_v = int(vot_ms/1000*sr)
    n_t = int(0.042*sr)
    n_total = n_c+n_b+n_v+n_t

    nxt   = VOWEL_F.get(next_p,
                         VOWEL_F['AH'])
    F_vow = nxt[0]
    B_vow = nxt[1]
    B_asp = [min(float(b)*3.0, 500.0)
             for b in B_vow]

    # Full-length trajectory arrays
    Fa = [np.zeros(n_total, dtype=DTYPE)
          for _ in range(4)]

    # Closure: closed tract formants
    F_clos = [300, 800, 2200, 3300]
    for fi in range(4):
        Fa[fi][:n_c] = float(F_clos[fi])

    # VOT: glide toward vowel
    for fi in range(4):
        s = n_c+n_b
        e = s+n_v
        if n_v > 0:
            Fa[fi][s:e] = np.linspace(
                float(F_clos[fi]),
                float(F_vow[fi]),
                n_v, dtype=DTYPE)

    # Transition: F2 locus → vowel
    # This is the primary place cue
    F_trans = [400.0, float(f2_locus),
                float(F_vow[2]),
                float(F_vow[3])]
    for fi in range(4):
        s = n_c+n_b+n_v
        e = s+n_t
        if n_t > 0:
            Fa[fi][s:e] = np.linspace(
                float(F_trans[fi]),
                float(F_vow[fi]),
                n_t, dtype=DTYPE)

    Fa = [f32(a) for a in Fa]
    Bv = [float(B_vow[fi])
          for fi in range(4)]

    # Source array
    source = np.zeros(n_total, dtype=DTYPE)

    # Closure: voiced stops hum
    if voiced and n_c > 0:
        hum = source_voiced(
            pitch, n_c,
            jitter=0.015, shimmer=0.10,
            sr=sr)
        source[:n_c] = hum * 0.055

    # Burst: pressure release spike
    if n_b > 0:
        burst = source_steady(n_b)
        try:
            b,a   = safe_hp(burst_hp, SR)
            burst = f32(lfilter(b,a,burst))
        except:
            pass
        benv  = f32(np.exp(
            -np.arange(n_b)/n_b*20))
        s = n_c
        source[s:s+n_b] = \
            burst*benv*burst_amp

    # VOT + transition: noise → voiced
    # Same crossfade mechanism as H
    n_vt = n_v+n_t
    if n_vt > 0:
        noise_vt = source_steady(n_vt)
        # Shape by following vowel formants
        for fi in range(2):
            fc  = float(F_vow[fi])
            bw  = B_asp[fi]*1.5
            lo_ = max(60, fc-bw*1.2)
            hi_ = min(SR*0.48, fc+bw*1.2)
            try:
                b,a      = safe_bp(
                    lo_, hi_, SR)
                noise_vt += f32(
                    lfilter(b, a,
                    source_steady(n_vt))
                )*0.4
            except:
                pass

        voice_vt = source_voiced(
            pitch, n_vt, sr=sr)

        # Crossfade over VOT duration
        ne = np.ones(n_vt, dtype=DTYPE)
        ve = np.zeros(n_vt, dtype=DTYPE)
        if n_v > 0:
            ne[:n_v] = f32(
                np.linspace(1,0,n_v))
            ve[:n_v] = f32(
                np.linspace(0,1,n_v))
        ne[n_v:] = 0.0
        ve[n_v:] = 1.0

        s = n_c+n_b
        source[s:s+n_vt] = f32(
            noise_vt*ne + voice_vt*ve)

    out, new_st = tract(
        f32(source), Fa, Bv,
        GAINS, states, sr)

    # Amplitude envelope
    env = np.zeros(n_total, dtype=DTYPE)
    if voiced and n_c > 0:
        env[:n_c] = 0.055
    rn = n_total-n_c
    if rn > 0:
        env[n_c:] = np.linspace(
            0, 1, rn, dtype=DTYPE)
    rl = int(0.018*sr)
    if rl > 0 and rl < n_total:
        env[-rl:] *= f32(
            np.linspace(1,0,rl))
    out = out * f32(env)
    mx  = np.max(np.abs(out))
    if mx > 0: out /= mx
    return f32(out), new_st


# ============================================================
# WORD DICTIONARY
# Simple phoneme sequences.
# State threads through all of them.
# ============================================================

WORDS = {
    'here':    ['H','IH','R'],
    'home':    ['H','OW','M'],
    'water':   ['W','AA','T','ER'],
    'still':   ['S','T','IH','L'],
    'open':    ['OH','P','EH','N'],
    'always':  ['AA','L','W','EH','Z'],
    'both':    ['B','OH','TH'],
    'now':     ['N','AW'],
    'voice':   ['V','OY','S'],
    'matter':  ['M','AE','T','ER'],
    'the':     ['DH','AH'],
    'where':   ['W','EH','R'],
    'landing': ['L','AE','N','D','IH','NG'],
    'named':   ['N','EH','M','D'],
    'been':    ['B','IH','N'],
    'yet':     ['Y','EH','T'],
    'find':    ['F','AY','N','D'],
    'state':   ['S','T','EH','T'],
    'solid':   ['S','AA','L','IH','D'],
    'not':     ['N','AA','T'],
    'still':   ['S','T','IH','L'],
    'wrong':   ['R','AO','NG'],
    'already': ['AA','L','R','EH','D','IY'],
    'am':      ['AH','M'],
}

# Phoneme durations (ms) — pre-dilation
PHON_DUR = {
    **VOWEL_DUR,
    'M':85,'N':80,'NG':90,
    'L':80,'R':90,'W':90,'Y':80,
    'H':70,
    'S':100,'SH':105,'F':90,'TH':90,
    'Z':95,'ZH':95,'V':85,'DH':80,
    'P':90,'B':80,'T':85,'D':75,
    'K':90,'G':78,
    'SIL':55,
}

VOWELS = set(VOWEL_F.keys())
NASALS = {'M','N','NG'}
APPROX = {'L','R','W','Y'}
H_SET  = {'H'}
STOPS  = {'P','B','T','D','K','G'}
FRICS  = {'S','SH','F','TH',
           'Z','ZH','V','DH'}


def synth_phone(ph, pitch, dur_ms,
                 prev_p, next_p,
                 states, sr=SR):
    """Route to correct synth function."""
    if ph == 'SIL':
        n  = int((dur_ms or 55)/1000*sr)
        st = states if states \
             else [(0.0,0.0)]*4
        return f32(np.zeros(n)), st

    if ph in VOWELS:
        return synth_vowel(
            ph, pitch, dur_ms,
            prev_p, next_p, states, sr)

    if ph in NASALS:
        return synth_nasal(
            ph, pitch, dur_ms,
            prev_p, next_p, states, sr)

    if ph in APPROX:
        return synth_approximant(
            ph, pitch, dur_ms,
            prev_p, next_p, states, sr)

    if ph in H_SET:
        return synth_h(
            next_p or 'AH',
            pitch, dur_ms, states, sr)

    if ph in FRICS:
        return synth_fricative(
            ph, pitch, dur_ms,
            prev_p, next_p, states, sr)

    if ph in STOPS:
        return synth_stop(
            ph, pitch, dur_ms,
            next_p, states, sr)

    # Unknown: silence
    n  = int((dur_ms or 80)/1000*sr)
    st = states if states \
         else [(0.0,0.0)]*4
    return f32(np.zeros(n)), st


def synth_word(word, pitch=PITCH,
               dil=DIL, sr=SR):
    """
    Synthesize a word.

    The tract never stops.
    State threads from phoneme to phoneme.
    The word is a continuous trajectory
    through vocal topology space.
    The phonemes are waypoints.
    The synthesis draws the smooth
    path between them.
    """
    phonemes = WORDS.get(word.lower())
    if phonemes is None:
        print(f"  '{word}' not in dict")
        return f32(np.zeros(int(0.1*sr)))

    segs  = []
    state = None

    for i, ph in enumerate(phonemes):
        prev_p = phonemes[i-1] \
                 if i > 0 else None
        next_p = phonemes[i+1] \
                 if i < len(phonemes)-1 \
                 else None
        d_ms   = PHON_DUR.get(ph, 80)*dil

        seg, state = synth_phone(
            ph, pitch, d_ms,
            prev_p, next_p,
            state, sr)
        segs.append(f32(seg))

    result = f32(np.concatenate(segs))
    mx = np.max(np.abs(result))
    if mx > 0: result /= mx
    return result


def synth_phrase(word_list, pitch=PITCH,
                  dil=DIL, sr=SR):
    segs = []
    nw   = len(word_list)
    for wi, word in enumerate(word_list):
        prog  = wi/max(nw-1, 1)
        p     = pitch*(1.0-0.08*prog)
        seg   = synth_word(
            word, pitch=p, dil=dil, sr=sr)
        segs.append(f32(seg))
        if wi < nw-1:
            segs.append(sil(0.080))
    result = f32(np.concatenate(segs))
    n   = len(result)
    env = f32(np.ones(n))
    atk = int(0.018*sr)
    rel = int(0.050*sr)
    if atk > 0 and atk < n:
        env[:atk] = f32(
            np.linspace(0,1,atk))
    if rel > 0:
        env[-rel:] = f32(
            np.linspace(1,0,rel))
    result *= env
    mx = np.max(np.abs(result))
    if mx > 0: result /= mx
    return result


def save(name, sig, room=True,
          rt60=1.4, dr=0.50, sr=SR):
    sig = f32(sig)
    if room:
        sig = apply_room(
            sig, rt60=rt60, dr=dr, sr=sr)
    write_wav(
        f"output_play/{name}.wav", sig, sr)
    dur = len(sig)/sr
    print(f"    {name}.wav  ({dur:.2f}s)")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    os.makedirs("output_play", exist_ok=True)

    print()
    print("VOICE PHYSICS v5")
    print("Observer: in the room")
    print("Instrument: vocal tract")
    print("Player: diaphragm + body")
    print(f"Speed: {DIL}x (natural)")
    print("="*60)
    print()

    # ---- VOWELS ----
    print("  Vowels...")
    for v in VOWEL_F.keys():
        seg,_ = synth_vowel(v, PITCH)
        save(f"vowel_{v}", seg)

    # ---- FRICATIVE COMPARISONS ----
    # F vs S vs SH — geometry demonstration
    print()
    print("  Fricatives (from geometry)...")
    for ph in ['F','V','TH','DH',
                'S','Z','SH','ZH']:
        seg,_ = synth_fricative(
            ph, PITCH, next_p='AA')
        save(f"fric_{ph}", seg)

    # Side-by-side comparison
    segs = []
    for ph in ['F','S','SH']:
        s,_ = synth_fricative(
            ph, PITCH,
            dur_ms=90*DIL*1.5,
            next_p='AA')
        segs.append(s)
        segs.append(sil(0.35))
    save("fric_F_vs_S_vs_SH",
          f32(np.concatenate(segs)))

    # ---- STOPS ----
    print()
    print("  Stops...")
    for ph in ['P','B','T','D','K','G']:
        seg,_ = synth_stop(
            ph, PITCH, next_p='AA')
        save(f"stop_{ph}", seg)

    # ---- NASALS ----
    print()
    print("  Nasals...")
    for ph in ['M','N','NG']:
        seg,_ = synth_nasal(
            ph, PITCH,
            prev_p='AA', next_p='AA')
        save(f"nasal_{ph}", seg)

    # ---- APPROXIMANTS ----
    print()
    print("  Approximants...")
    for ph in ['L','R','W','Y']:
        seg,_ = synth_approximant(
            ph, PITCH,
            prev_p='AA', next_p='AA')
        save(f"approx_{ph}", seg)

    # ---- H BEFORE DIFFERENT VOWELS ----
    # Demonstrates H = whispered vowel
    print()
    print("  H (whispered vowel)...")
    for nv in ['IH','OW','AA','EH','UW']:
        seg,_ = synth_h(nv, PITCH)
        save(f"H_before_{nv}", seg)

    # H comparison: same H, different vowels
    segs = []
    for nv in ['IH','OW','AA']:
        s,_ = synth_h(
            nv, PITCH,
            dur_ms=70*DIL*1.5)
        segs.append(s)
        segs.append(sil(0.35))
    save("H_IH_vs_OW_vs_AA",
          f32(np.concatenate(segs)))

    # ---- WORDS ----
    print()
    print("  Words...")
    for word in WORDS.keys():
        seg = synth_word(word)
        save(f"word_{word}", seg,
              rt60=1.5)

    # ---- PHRASES ----
    print()
    print("  Phrases...")
    phrases = [
        ['still','here'],
        ['always','open'],
        ['the','voice'],
        ['water','home'],
        ['always','home'],
    ]
    for pw in phrases:
        label = "_".join(pw)
        seg   = synth_phrase(pw)
        save(f"phrase_{label}", seg,
              rt60=1.8)

    print()
    print("="*60)
    print()
    print("  Key comparisons:")
    print()
    print("  Fricative geometry:")
    print("  afplay output_play/"
          "fric_F_vs_S_vs_SH.wav")
    print("  (F: no cavity, soft)")
    print("  (S: small cavity, sharp)")
    print("  (SH: long cavity, hushed)")
    print()
    print("  H = whispered vowel:")
    print("  afplay output_play/"
          "H_IH_vs_OW_vs_AA.wav")
    print("  (same H mechanism,")
    print("   different following vowels,")
    print("   different sounds)")
    print()
    print("  Words:")
    for w in ['here','home','water',
               'still','open','always']:
        print(f"  afplay output_play/"
              f"word_{w}.wav")
    print()
    print("  The voice is the trajectory.")
    print("  The phonemes are the waypoints.")
    print("  The tract never stops.")
    print()
